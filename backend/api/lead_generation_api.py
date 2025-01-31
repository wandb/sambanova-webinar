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

# Original
from services.query_router_service import QueryRouterService
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew
from agent.samba_research_flow.samba_research_flow import SambaResearchFlow

# For financial analysis
from services.financial_user_prompt_extractor_service import FinancialPromptExtractor
from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisCrew

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

        # For concurrency
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Redis connection for route logs / SSE
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=0,
            decode_responses=True
        )
        print(f"[LeadGenerationAPI] Using Redis at {redis_host}:{redis_port}")

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

            print(f"[/execute/{query_type}] user_id={user_id}, run_id={run_id}")

            try:
                if query_type == "sales_leads":
                    # Sales route
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
                    # Educational content route
                    if not serper_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Serper API key for educational content"}
                        )
                    edu_flow = SambaResearchFlow(
                        sambanova_key=sambanova_key,
                        serper_key=serper_key,
                        user_id=user_id,
                        run_id=run_id
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

                elif query_type == "financial_analysis":
                    # New financial route, align with sales_leads approach
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
                        run_id=run_id
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
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                local_redis = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=0,
                    decode_responses=True
                )

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
                        local_redis.close()

                return EventSourceResponse(
                    event_generator(),
                    media_type="text/event-stream",
                    headers={"Cache-Control":"no-cache","Connection":"keep-alive"}
                )
            except Exception as e:
                print(f"[stream_logs] Error setting up SSE: {e}")
                return JSONResponse(status_code=500, content={"error": str(e)})

    async def execute_research(self, crew, parameters: Dict[str,Any]):
        """
        Helper for 'sales_leads' route.
        Extract lead info from parameters, run crew.execute_research in a thread.
        """
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
        """
        Helper for 'financial_analysis' route.
        Extract ticker/company from parameters, then run crew.execute_financial_analysis in a thread.
        """
        fextractor = FinancialPromptExtractor(crew.sambanova_key)
        query_text = parameters.get("query_text","")
        (extracted_ticker, extracted_company) = fextractor.extract_info(query_text)

        if not extracted_ticker:
            extracted_ticker = parameters.get("ticker","")
        if not extracted_company:
            extracted_company = parameters.get("company_name","")

        if not extracted_ticker:
            extracted_ticker = "AAPL"
        if not extracted_company:
            extracted_company = "Apple Inc"

        inputs = {"ticker": extracted_ticker, "company_name": extracted_company}

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
