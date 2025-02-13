from fastapi import FastAPI, File, Query, Request, BackgroundTasks, UploadFile
from pydantic import BaseModel
import json
import uvicorn
import sys
import os
import re
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
from starlette.websockets import WebSocketState
from contextlib import asynccontextmanager

from api.agents.user_proxy import UserProxyAgent
from api.websocket_manager import WebSocketConnectionManager

from api.utils import initialize_agent_runtime
from api.otlp_tracing import logger
from autogen_core import MessageContext

import redis
import uuid

from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    default_subscription,
    message_handler,
)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.data_types import APIKeys, EndUserMessage, AgentStructuredResponse, TestMessage


# SSE support
from sse_starlette.sse import EventSourceResponse

from api.agents.route import SemanticRouterAgent
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the new chat logic
from agent.convo_newsletter_crew import crew_chat

# Original Services
from services.query_router_service import QueryRouterService
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew
from agent.samba_research_flow.samba_research_flow import SambaResearchFlow

# For financial analysis
from services.financial_user_prompt_extractor_service import FinancialPromptExtractor
from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisCrew
# For document processing
from services.document_processing_service import DocumentProcessingService

class QueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None

class EduContentRequest(BaseModel):
    topic: str
    audience_level: str = "intermediate"
    additional_context: Optional[Dict[str, List[str]]] = None

class ChatRequest(BaseModel):
    message: str

def estimate_tokens_regex(text: str) -> int:
        return len(re.findall(r"\w+|\S", text))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown lifespan events for the FastAPI application.

    Initializes the agent runtime and registers the UserProxyAgent.
    """
    # Initialize a default agent runtime for the application
    app.state.agent_runtime = await initialize_agent_runtime()

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    app.state.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True
    )
    print(f"[LeadGenerationAPI] Using Redis at {redis_host}:{redis_port}")

    app.state.manager = WebSocketConnectionManager(
        agent_runtime=app.state.agent_runtime,
        redis_client=app.state.redis_client
    )
    UserProxyAgent.connection_manager = app.state.manager
    SemanticRouterAgent.connection_manager = app.state.manager

    yield  # This separates the startup and shutdown logic

    # Cleanup chat-specific agent runtimes
    chat_keys = app.state.redis_client.keys("chat_manager:*")
    for key in chat_keys:
        chat_data = app.state.redis_client.get(key)
        if chat_data:
            chat_info = json.loads(chat_data)
            # TODO: Add cleanup for chat-specific agent runtime
            app.state.redis_client.delete(key)

    # Cleanup default agent runtime
    await app.state.agent_runtime.close()

class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.setup_cors()
        self.setup_routes()
        self.context_length_summariser = 64000
        self.executor = ThreadPoolExecutor(max_workers=2)


    def setup_cors(self):
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        if not allowed_origins or (len(allowed_origins) == 1 and allowed_origins[0] == '*'):
            allowed_origins = ["*"]
        else:
            allowed_origins.extend([
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:8000"
            ])

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=[
                "*",
                "x-sambanova-key",
                "x-exa-key",
                "x-serper-key",
                "x-user-id",
                "x-run-id"
            ],
            expose_headers=["content-type", "content-length"]
        )

    def setup_routes(self):
        # WebSocket endpoint to handle user messages
        @self.app.websocket("/chat")
        async def websocket_endpoint(
            websocket: WebSocket,
            user_id: str = Query(..., description="User ID"),
            conversation_id: str = Query(..., description="Conversation ID")
        ):
            """
            WebSocket endpoint for handling user chat messages.

            Args:
                websocket (WebSocket): The WebSocket connection.
                user_id (str): The ID of the user.
                conversation_id (str): The ID of the conversation.
            """
            await self.app.state.manager.handle_websocket(
                websocket, 
                user_id, 
                conversation_id
            )

        @self.app.post("/route")
        async def determine_route(request: Request, query_request: QueryRequest):
            sambanova_key = request.headers.get("x-sambanova-key")
            if not sambanova_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing required SambaNova API key"}
                )
            try:
                router = QueryRouterService(sambanova_key)
                route_result = router.route_query(query_request.query)
                return JSONResponse(
                    status_code=200,
                    content={
                        "type": route_result.type,
                        "parameters": route_result.parameters
                    }
                )
            except Exception as e:
                print(f"[/route] Error determining route: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.post("/execute/{query_type}")
        async def execute_query(
            request: Request,
            query_type: str,
            parameters: Dict[str, Any]
        ):
            sambanova_key = request.headers.get("x-sambanova-key")
            serper_key = request.headers.get("x-serper-key")
            exa_key = request.headers.get("x-exa-key")

            user_id = request.headers.get("x-user-id", "")
            run_id = request.headers.get("x-run-id", "")

            try:
                # Load document chunks if document_ids are provided
                if "document_ids" in parameters:
                    doc_ids = parameters["document_ids"]
                    chunks_text = []

                    for doc_id in doc_ids:
                        # Verify document exists and belongs to user
                        user_docs_key = f"user_documents:{user_id}"
                        if not self.app.state.redis_client.sismember(user_docs_key, doc_id):
                            continue  # Skip if document doesn't belong to user

                        chunks_key = f"document_chunks:{doc_id}"
                        chunks_data = self.app.state.redis_client.get(chunks_key)

                        if chunks_data:
                            chunks = json.loads(chunks_data)
                            chunks_text.extend([chunk['text'] for chunk in chunks])

                    if chunks_text:
                        combined_text = "\n".join(chunks_text)
                        token_count = estimate_tokens_regex(combined_text)
                        # Check if combined document chunks exceed context length
                        if (
                            token_count > self.context_length_summariser
                        ): 
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "Combined document length exceeds maximum context window size. Please reduce the number or size of documents."
                                },
                            )
                        parameters["docs"] = combined_text

                if query_type == "sales_leads":
                    if not exa_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Exa API key for sales leads"}
                        )
                    crew = ResearchCrew(
                        sambanova_key=sambanova_key,
                        exa_key=exa_key,
                        user_id=user_id,
                        run_id=run_id
                    )
                    raw_result = await self.execute_research(crew, parameters)
                    parsed_result = json.loads(raw_result)
                    outreach_list = parsed_result.get("outreach_list", [])
                    return JSONResponse(content={"results": outreach_list})

                elif query_type == "educational_content":
                    if not serper_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Serper API key for educational content"}
                        )
                    edu_flow = SambaResearchFlow(
                        sambanova_key=sambanova_key,
                        serper_key=serper_key,
                        user_id=user_id,
                        run_id=run_id,
                        docs_included="docs" in parameters
                    )
                    edu_inputs = {
                        "topic": parameters["topic"],
                        "audience_level": parameters.get("audience_level", "intermediate"),
                        "additional_context": ", ".join(parameters.get("focus_areas", []))
                    }
                    if "docs" in parameters:
                        edu_inputs["docs"] = parameters["docs"]
                    edu_flow.input_variables = edu_inputs
                    loop = asyncio.get_running_loop()
                    result = await loop.run_in_executor(None, edu_flow.kickoff)

                    if isinstance(result, str):
                        sections_with_content = json.loads(result)
                    else:
                        sections_with_content = result

                    return JSONResponse(content=sections_with_content)

                elif query_type == "financial_analysis":
                    if not exa_key or not serper_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Exa or Serper API keys for financial analysis"}
                        )
                    crew = FinancialAnalysisCrew(
                        sambanova_key=sambanova_key,
                        exa_key=exa_key,
                        serper_key=serper_key,
                        user_id=user_id,
                        run_id=run_id,
                        docs_included="docs" in parameters
                    )
                    raw_result = await self.execute_financial(crew, parameters)
                    parsed_fin = json.loads(raw_result)
                    return JSONResponse(content=parsed_fin)

                else:
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Unknown query type: {query_type}"}
                    )

            except Exception as e:
                print(f"[/execute/{query_type}] Error executing query: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.get("/stream/logs")
        async def stream_logs(request: Request, user_id: str, run_id: str):
            """
            SSE endpoint that streams agent logs for the given user_id + run_id.
            """
            channel = f"agent_thoughts:{user_id}:{run_id}"
            print(f"[stream_logs] Starting SSE for user_id={user_id}, run_id={run_id}, channel={channel}")

            try:
                local_redis = self.app.state.redis_client

                pubsub = local_redis.pubsub(ignore_subscribe_messages=True)
                pubsub.subscribe(channel)

                async def event_generator():
                    try:
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "connection_established",
                                "message": "Connected to SSE stream"
                            })
                        }
                        while True:
                            if await request.is_disconnected():
                                print("[stream_logs] Client disconnected")
                                break

                            message = pubsub.get_message(timeout=1.0)
                            if message and message["type"] == "message":
                                data_str = message["data"]
                                yield {
                                    "event": "message",
                                    "data": data_str
                                }

                            await asyncio.sleep(0.25)
                            yield {
                                "event": "ping",
                                "data": json.dumps({"type":"ping"})
                            }
                    except Exception as ex:
                        print(f"[stream_logs] Error in SSE generator: {ex}")
                    finally:
                        print("[stream_logs] unsubscribing, closing pubsub")
                        pubsub.unsubscribe()
                        pubsub.close()

                return EventSourceResponse(
                    event_generator(),
                    media_type="text/event-stream",
                    headers={"Cache-Control":"no-cache","Connection":"keep-alive"}
                )
            except Exception as e:
                print(f"[stream_logs] Error setting up SSE: {e}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.post("/chat/init")
        async def init_chat(request: Request):
            """
            Initializes a new chat session and stores the provided API keys.
            Returns a chat ID for subsequent interactions.
            """
            sambanova_key = request.headers.get("x-sambanova-key", "")
            serper_key = request.headers.get("x-serper-key", "")
            exa_key = request.headers.get("x-exa-key", "")
            user_id = request.headers.get("x-user-id", "anonymous")

            try:
                # Generate a unique chat ID
                chat_id = str(uuid.uuid4())

                # Store keys in Redis with user-specific prefix
                key_prefix = f"api_keys:{user_id}"
                self.app.state.redis_client.hset(
                    key_prefix,
                    mapping={
                        "sambanova_key": sambanova_key,
                        "serper_key": serper_key,
                        "exa_key": exa_key
                    }
                )

                #TODO: init autogen agent

                return JSONResponse(
                    status_code=200,
                    content={
                        "chat_id": chat_id,
                        "message": "Chat session initialized successfully"
                    }
                )

            except Exception as e:
                print(f"[/chat/init] Error initializing chat: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to initialize chat: {str(e)}"}
                )

        # ----------------------------------------------------------------
        # NEW ENDPOINT: /newsletter_chat/init
        # ----------------------------------------------------------------
        @self.app.post("/newsletter_chat/init")
        def init_newsletter_chat(request: Request):
            """
            Initializes a conversation with ConvoNewsletterCrew using the provided keys.
            """
            sambanova_key = request.headers.get("x-sambanova-key","")
            serper_key = request.headers.get("x-serper-key","")
            exa_key = request.headers.get("x-exa-key","")
            user_id = request.headers.get("x-user-id","anonymous")
            run_id = request.headers.get("x-run-id","")

            try:
                init_data = crew_chat.api_init_conversation(
                    sambanova_key=sambanova_key,
                    serper_key=serper_key,
                    exa_key=exa_key,
                    user_id=user_id,
                    run_id=run_id
                )
                return JSONResponse(
                    status_code=200,
                    content={
                        "conversation_id": init_data["conversation_id"],
                        "assistant_message": init_data["assistant_message"]
                    }
                )
            except Exception as e:
                print(f"[/newsletter_chat/init] Error: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        # ----------------------------------------------------------------
        # NEW ENDPOINT: /newsletter_chat/message/{conversation_id}
        # ----------------------------------------------------------------
        @self.app.post("/newsletter_chat/message/{conversation_id}")
        def newsletter_chat_message(conversation_id: str, body: ChatRequest, request: Request):
            """
            Sends a user message to an existing conversation, returning assistant's reply.
            """
            user_id = request.headers.get("x-user-id","anonymous")
            user_message = body.message.strip()
            if not user_message:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Empty user message."}
                )
            try:
                response_text = crew_chat.api_process_message(
                    conversation_id,
                    user_message,
                    user_id=user_id
                )
                return JSONResponse(
                    status_code=200,
                    content={"assistant_response": response_text}
                )
            except ValueError as ve:
                print(f"[/newsletter_chat/message] Not found: {str(ve)}")
                return JSONResponse(
                    status_code=404,
                    content={"error": str(ve)}
                )
            except Exception as e:
                print(f"[/newsletter_chat/message] Error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

        # ----------------------------------------------------------------
        # NEW ENDPOINT: /newsletter_chat/history/{conversation_id}
        # ----------------------------------------------------------------
        @self.app.get("/newsletter_chat/history/{conversation_id}")
        def conversation_history(conversation_id: str, request: Request):
            """
            Returns the entire messages list for the specified conversation, 
            so the front end can show the entire conversation from start.
            """
            user_id = request.headers.get("x-user-id","anonymous")
            try:
                data = crew_chat.api_get_full_history(conversation_id, user_id)
                return JSONResponse(
                    status_code=200,
                    content=data
                )
            except ValueError as ve:
                return JSONResponse(
                    status_code=404,
                    content={"error":str(ve)}
                )
            except Exception as e:
                print(f"[/newsletter_chat/history] Error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

        # ~~~~ Existing Helper Methods for Sales Leads, Fin Analysis, etc. ~~~~

        @self.app.post("/upload")
        async def upload_document(
            request: Request,
            file: UploadFile = File(...),
        ):
            """Upload and process a document."""
            try:
                # Get user_id from headers
                user_id = request.headers.get("x-user-id", "")

                if not user_id:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "x-user-id header is required"}
                    )

                # Generate unique document ID
                document_id = str(uuid.uuid4())

                # Read file content
                content = await file.read()

                # Process document
                doc_processor = DocumentProcessingService()
                chunks = doc_processor.process_document(content, file.filename)

                # Store document metadata
                document_metadata = {
                    "id": document_id,
                    "filename": file.filename,
                    "upload_timestamp": time.time(),
                    "num_chunks": len(chunks),
                    "user_id": user_id
                }

                # Store document metadata
                doc_key = f"document:{document_id}"
                self.app.state.redis_client.set(doc_key, json.dumps(document_metadata))

                # Add to user's document list
                user_docs_key = f"user_documents:{user_id}"
                self.app.state.redis_client.sadd(user_docs_key, document_id)

                # Store document chunks
                chunks_key = f"document_chunks:{document_id}"
                chunks_data = [
                    {
                        "text": chunk.page_content,
                        "metadata": {
                            **chunk.metadata,
                            "document_id": document_id
                        }
                    }
                    for chunk in chunks
                ]
                self.app.state.redis_client.set(chunks_key, json.dumps(chunks_data))

                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "Document processed successfully",
                        "document": document_metadata
                    },
                )

            except Exception as e:
                print(f"[/upload] Error processing document: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.get("/documents/{user_id}")
        async def get_user_documents(user_id: str):
            """Retrieve all documents for a user."""
            try:
                # Get all document IDs for the user
                user_docs_key = f"user_documents:{user_id}"
                doc_ids = self.app.state.redis_client.smembers(user_docs_key)

                if not doc_ids:
                    return JSONResponse(
                        status_code=200,
                        content={"documents": []}
                    )

                # Get metadata for each document
                documents = []
                for doc_id in doc_ids:
                    doc_key = f"document:{doc_id}"
                    doc_data = self.app.state.redis_client.get(doc_key)
                    if doc_data:
                        documents.append(json.loads(doc_data))

                return JSONResponse(
                    status_code=200,
                    content={"documents": documents}
                )

            except Exception as e:
                print(f"[/documents] Error retrieving documents: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.get("/documents/{user_id}/{document_id}/chunks")
        async def get_document_chunks_by_id(user_id: str, document_id: str):
            """Retrieve chunks for a specific document."""
            try:
                # Verify document belongs to user
                user_docs_key = f"user_documents:{user_id}"
                if not self.app.state.redis_client.sismember(user_docs_key, document_id):
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Document not found or access denied"}
                    )

                # Get document chunks
                chunks_key = f"document_chunks:{document_id}"
                chunks_data = self.app.state.redis_client.get(chunks_key)

                if not chunks_data:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Document chunks not found"}
                    )

                return JSONResponse(
                    status_code=200,
                    content=json.loads(chunks_data)
                )

            except Exception as e:
                print(f"[/documents/chunks] Error retrieving chunks: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.delete("/documents/{user_id}/{document_id}")
        async def delete_document(user_id: str, document_id: str):
            """Delete a document and its associated data from the database."""
            try:
                # Verify document belongs to user
                user_docs_key = f"user_documents:{user_id}"
                if not self.app.state.redis_client.sismember(user_docs_key, document_id):
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Document not found or access denied"}
                    )

                # Delete document metadata
                doc_key = f"document:{document_id}"
                self.app.state.redis_client.delete(doc_key)

                # Delete document chunks
                chunks_key = f"document_chunks:{document_id}"
                self.app.state.redis_client.delete(chunks_key)

                # Remove from user's document list
                self.app.state.redis_client.srem(user_docs_key, document_id)

                return JSONResponse(
                    status_code=200,
                    content={"message": "Document deleted successfully"}
                )

            except Exception as e:
                print(f"[/documents/delete] Error deleting document: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.post("/set_api_keys/{user_id}")
        async def set_api_keys(user_id: str, keys: APIKeys):
            """
            Store API keys for a user in Redis.
            
            Args:
                user_id (str): The ID of the user
                keys (APIKeys): The API keys to store
            """
            try:
                # Store keys in Redis with user-specific prefix
                key_prefix = f"api_keys:{user_id}"
                self.app.state.redis_client.hset(
                    key_prefix,
                    mapping={
                        "sambanova_key": keys.sambanova_key,
                        "serper_key": keys.serper_key,
                        "exa_key": keys.exa_key
                    }
                )
                
                return JSONResponse(
                    status_code=200,
                    content={"message": "API keys stored successfully"}
                )
                
            except Exception as e:
                print(f"[/set_api_keys] Error storing API keys: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to store API keys: {str(e)}"}
                )

        @self.app.get("/get_api_keys/{user_id}")
        async def get_api_keys(user_id: str):
            """
            Retrieve stored API keys for a user.
            
            Args:
                user_id (str): The ID of the user
            """
            try:
                key_prefix = f"api_keys:{user_id}"
                stored_keys = self.app.state.redis_client.hgetall(key_prefix)
                
                if not stored_keys:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "No API keys found for this user"}
                    )
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "sambanova_key": stored_keys.get("sambanova_key", ""),
                        "serper_key": stored_keys.get("serper_key", ""),
                        "exa_key": stored_keys.get("exa_key", "")
                    }
                )
                
            except Exception as e:
                print(f"[/get_api_keys] Error retrieving API keys: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Failed to retrieve API keys: {str(e)}"}
                )

    async def execute_research(self, crew, parameters: Dict[str, Any]):
        extractor = UserPromptExtractor(crew.sambanova_key)
        combined_text = " ".join([
            parameters.get("industry", ""),
            parameters.get("company_stage", ""),
            parameters.get("geography", ""),
            parameters.get("funding_stage", ""),
            parameters.get("product", ""),
        ]).strip()
        extracted_info = extractor.extract_lead_info(combined_text)

        loop = asyncio.get_running_loop()
        future = self.executor.submit(crew.execute_research, extracted_info)
        result = await loop.run_in_executor(None, future.result)
        return result

    async def execute_financial(self, crew, parameters: Dict[str,Any]):
        fextractor = FinancialPromptExtractor(crew.sambanova_key)
        query_text = parameters.get("query_text","")
        extracted_ticker, extracted_company = fextractor.extract_info(query_text)

        if not extracted_ticker:
            extracted_ticker = parameters.get("ticker","")
        if not extracted_company:
            extracted_company = parameters.get("company_name","")

        if not extracted_ticker:
            extracted_ticker = "AAPL"
        if not extracted_company:
            extracted_company = "Apple Inc"

        inputs = {"ticker": extracted_ticker, "company_name": extracted_company}

        if "docs" in parameters:
            inputs["docs"] = parameters["docs"]

        loop = asyncio.get_running_loop()
        future = self.executor.submit(crew.execute_financial_analysis, inputs)
        raw_result = await loop.run_in_executor(None, future.result)
        return raw_result

def create_app():
    api = LeadGenerationAPI()
    return api.app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
