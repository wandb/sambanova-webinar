# lead_generation_api.py

from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
import json
import uvicorn
import sys
import os
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
import redis

# SSE support
from sse_starlette.sse import EventSourceResponse

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from services.query_router_service import QueryRouterService
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew
from agent.samba_research_flow.samba_research_flow import SambaResearchFlow


class QueryRequest(BaseModel):
    query: str


class EduContentRequest(BaseModel):
    topic: str
    audience_level: str = "intermediate"
    additional_context: Optional[Dict[str, List[str]]] = None


class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI()
        self.setup_cors()
        self.setup_routes()

        # Redis
        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)

        # Executor for concurrency
        self.executor = ThreadPoolExecutor(max_workers=2)

    def setup_cors(self):
        # Get allowed origins from environment variable or use default
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        if not allowed_origins or (len(allowed_origins) == 1 and allowed_origins[0] == '*'):
            allowed_origins = ["*"]
        else:
            allowed_origins.extend(["http://localhost:5173", "http://localhost:5174"])

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
        )

    def setup_routes(self):
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
                print(f"Error determining route: {str(e)}")
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

            # Retrieve user/run IDs
            user_id = request.headers.get("x-user-id", "")
            run_id = request.headers.get("x-run-id", "")

            try:
                if query_type == "sales_leads":
                    if not exa_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Exa API key for sales leads"}
                        )
                    # Pass user_id and run_id to the crew
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
                        serper_key=serper_key
                    )
                    edu_flow.input_variables = {
                        "topic": parameters["topic"],
                        "audience_level": parameters.get("audience_level", "intermediate"),
                        "additional_context": ", ".join(parameters.get("focus_areas", []))
                    }
                    loop = asyncio.get_running_loop()
                    result = await loop.run_in_executor(None, edu_flow.kickoff)

                    if isinstance(result, str):
                        sections_with_content = json.loads(result)
                    else:
                        sections_with_content = result

                    return JSONResponse(content=sections_with_content)

                else:
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Unknown query type: {query_type}"}
                    )

            except Exception as e:
                print(f"Error executing query: {str(e)}")
                return JSONResponse(status_code=500, content={"error": str(e)})

        @self.app.get("/stream/logs")
        async def stream_logs(request: Request, user_id: str, run_id: str):
            """
            SSE endpoint that streams agent logs for the given user_id + run_id.
            """
            channel = f"agent_thoughts:{user_id}:{run_id}"
            print(f"Subscribing to channel: {channel}")  # Debug log
            
            try:
                pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
                await pubsub.subscribe(channel)
                
                async def event_generator():
                    try:
                        while True:
                            if await request.is_disconnected():
                                print("Client disconnected")
                                break
                                
                            message = await pubsub.get_message(timeout=1.0)
                            if message and message["type"] == "message":
                                print(f"Received message: {message['data']}")  # Debug log
                                yield {
                                    "event": "message",
                                    "data": message["data"]
                                }
                            await asyncio.sleep(0.1)
                    except Exception as e:
                        print(f"Error in event generator: {e}")
                    finally:
                        await pubsub.unsubscribe()
                        await pubsub.close()
                        
                return EventSourceResponse(event_generator())
            except Exception as e:
                print(f"Error setting up SSE stream: {e}")
                return JSONResponse(status_code=500, content={"error": str(e)})

    async def execute_research(self, crew, parameters):
        # We can do optional advanced parsing or just feed userPromptExtractor
        extractor = UserPromptExtractor(crew.sambanova_key)
        # Combine text
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


def create_app():
    api = LeadGenerationAPI()
    return api.app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
