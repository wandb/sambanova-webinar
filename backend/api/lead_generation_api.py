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
from services.query_router_service import QueryRouterService


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Services, Tools, etc.
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew
from agent.samba_research_flow.samba_research_flow import SambaResearchFlow

# Create a global ThreadPoolExecutor if you want concurrency in a single worker
# for CPU-heavy tasks (Pick a reasonable max_workers based on your environment).
executor = ThreadPoolExecutor(max_workers=2)

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

    def setup_cors(self):
        # Get allowed origins from environment variable or use default
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        
        # If no specific origins are set, default to allowing all
        if not allowed_origins or (len(allowed_origins) == 1 and allowed_origins[0] == '*'):
            allowed_origins = ["*"]
        else:
            # Add localhost for development
            allowed_origins.extend(["http://localhost:5173", "http://localhost:5174"])

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*", "x-sambanova-key", "x-exa-key"],
        )
        

    def setup_routes(self):
        @self.app.post("/query")
        async def route_query(request: Request, query_request: QueryRequest):
            # Extract API keys from headers
            sambanova_key = request.headers.get("x-sambanova-key")
            serper_key = request.headers.get("x-serper-key")
            exa_key = request.headers.get("x-exa-key")

            if not sambanova_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing required SambaNova API key"}
                )

            try:
                # Initialize router
                router = QueryRouterService(sambanova_key)
                route_result = router.route_query(query_request.query)

                if route_result.type == "sales_leads":
                    if not exa_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Exa API key for sales leads"}
                        )
                    # Use existing lead generation logic
                    crew = ResearchCrew(sambanova_key=sambanova_key, exa_key=exa_key)
                    result = await self.execute_research(crew, route_result.parameters)
                    return JSONResponse(content=json.loads(result))

                elif route_result.type == "educational_content":
                    if not serper_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Serper API key for educational content"}
                        )
                    try:
                        # Initialize EduFlow
                        edu_flow = SambaResearchFlow(
                            sambanova_key=sambanova_key,
                            serper_key=serper_key
                        )
                        
                        # Set input variables
                        edu_flow.input_variables = {
                            "topic": route_result.parameters["topic"],
                            "audience_level": route_result.parameters.get("audience_level", "intermediate"),
                            "additional_context": ", ".join(route_result.parameters.get("focus_areas", []))
                        }
                        
                        # Execute flow in a way that works with asyncio
                        loop = asyncio.get_running_loop()
                        result = await loop.run_in_executor(None, edu_flow.kickoff)
                        
                        return JSONResponse(content={
                            "topic": route_result.parameters["topic"],
                            "audience_level": route_result.parameters.get("audience_level", "intermediate"),
                            "sections": result
                        })
                    except Exception as e:
                        print(f"Error in educational content generation: {str(e)}")
                        return JSONResponse(
                            status_code=500,
                            content={"error": f"Educational content generation failed: {str(e)}"}
                        )

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

    async def execute_research(self, crew, parameters):
        # Extract parameters
        industry = parameters.get("industry")
        company_stage = parameters.get("company_stage")
        geography = parameters.get("geography")
        funding_stage = parameters.get("funding_stage")
        product = parameters.get("product")

        # Initialize research crew with parameters
        crew.parameters = parameters

        # Initialize services with API keys
        extractor = UserPromptExtractor(crew.sambanova_key)
        extracted_info = extractor.extract_lead_info(f"{industry} {company_stage} {geography} {funding_stage} {product}")

        # Offload CPU-bound or time-consuming "execute_research" call 
        # to a separate thread so it doesn't block the async event loop.
        loop = asyncio.get_running_loop()
        future = executor.submit(crew.execute_research, extracted_info)
        result = await loop.run_in_executor(None, future.result)
        # Alternatively:
        # result = await loop.run_in_executor(executor, crew.execute_research, extracted_info)

        return result

def create_app():
    api = LeadGenerationAPI()
    return api.app 

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
