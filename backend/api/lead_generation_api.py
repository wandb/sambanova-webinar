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
import agentops


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
        @self.app.post("/route")
        async def determine_route(request: Request, query_request: QueryRequest):
            # Extract API keys from headers
            sambanova_key = request.headers.get("x-sambanova-key")
            
            if not sambanova_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing required SambaNova API key"}
                )

            try:
                # Initialize router
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
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

        @self.app.post("/execute/{query_type}")
        async def execute_query(
            request: Request, 
            query_type: str,
            parameters: Dict[str, Any]
        ):
            sambanova_key = request.headers.get("x-sambanova-key")
            serper_key = request.headers.get("x-serper-key")
            exa_key = request.headers.get("x-exa-key")

            try:
                if query_type == "sales_leads":
                    if not exa_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Missing required Exa API key for sales leads"}
                        )
                    crew = ResearchCrew(sambanova_key=sambanova_key, exa_key=exa_key)
                    raw_result = await self.execute_research(crew, parameters)
                    
                    # Mirror older code: parse and extract outreach_list
                    parsed_result = json.loads(raw_result)
                    outreach_list = parsed_result.get("outreach_list", [])
                    
                    # Return them under a known key
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

                    # IMPORTANT: Check if result is already a Python object or still a JSON string
                    if isinstance(result, str):
                        sections_with_content = json.loads(result)
                    else:
                        sections_with_content = result

                    # Return the content directly - it's already in the correct format
                    return JSONResponse(content=sections_with_content)

                else:
                    return JSONResponse(
                        status_code=400,
                        content={"error": f"Unknown query type: {query_type}"}
                    )

            except Exception as e:
                print(f"Error executing query: {str(e)}")
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
