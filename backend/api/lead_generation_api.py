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


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Services, Tools, etc.
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew
from backend.agent.samba_research_flow.samba_research_flow import SambaResearchFlow

# Create a global ThreadPoolExecutor if you want concurrency in a single worker
# for CPU-heavy tasks (Pick a reasonable max_workers based on your environment).
executor = ThreadPoolExecutor(max_workers=2)

class QueryRequest(BaseModel):
    prompt: str

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
        @self.app.post("/generate-leads")
        async def generate_leads(request: Request, background_tasks: BackgroundTasks):
            # Extract API keys from headers
            sambanova_key = request.headers.get("x-sambanova-key")
            exa_key = request.headers.get("x-exa-key")

            if not sambanova_key or not exa_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing required API keys"}
                )

            try:
                # Get request body
                body = await request.json()
                prompt = body.get("prompt", "")

                if not prompt:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Missing prompt in request body"}
                    )

                # Initialize services with API keys
                extractor = UserPromptExtractor(sambanova_key)
                extracted_info = extractor.extract_lead_info(prompt)

                # Initialize crew with API keys
                crew = ResearchCrew(sambanova_key=sambanova_key, exa_key=exa_key)

                # Offload CPU-bound or time-consuming "execute_research" call 
                # to a separate thread so it doesn't block the async event loop.
                loop = asyncio.get_running_loop()
                future = executor.submit(crew.execute_research, extracted_info)
                result = await loop.run_in_executor(None, future.result)
                # Alternatively:
                # result = await loop.run_in_executor(executor, crew.execute_research, extracted_info)

                # Parse result and return
                parsed_result = json.loads(result)
                outreach_list = parsed_result.get("outreach_list", [])
                return JSONResponse(content=outreach_list)

            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Invalid JSON response from research crew"}
                )
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

        @self.app.post("/api/edu-content")
        async def generate_educational_content(request: Request, content_request: EduContentRequest):
            # Extract API keys from headers
            sambanova_key = request.headers.get("x-sambanova-key")
            serper_key = request.headers.get("x-serper-key")

            if not sambanova_key or not serper_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing required API keys"}
                )

            try:
                # Initialize EduFlow with the API keys
                edu_flow = SambaResearchFlow(
                    sambanova_key=sambanova_key,
                    serper_key=serper_key
                )

                # Convert additional_context focus areas to string if present
                additional_context = None
                if content_request.additional_context and "focus_areas" in content_request.additional_context:
                    additional_context = ", ".join(content_request.additional_context["focus_areas"])
                
                # Set input variables
                edu_flow.input_variables = {
                    "topic": content_request.topic,
                    "audience_level": content_request.audience_level,
                    "additional_context": additional_context
                }

                # Execute flow
                result = edu_flow.kickoff()

                return JSONResponse(content={
                    "topic": content_request.topic,
                    "audience_level": content_request.audience_level,
                    "sections": result
                })

            except Exception as e:
                print(f"Error in generate_educational_content: {str(e)}")  # Add logging
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )

def create_app():
    api = LeadGenerationAPI()
    return api.app 

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
