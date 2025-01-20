# lead_generation_api.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import uvicorn
import sys
import os
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Services, Tools, etc.
from services.user_prompt_extractor_service import UserPromptExtractor
from agent.lead_generation_crew import ResearchCrew

class QueryRequest(BaseModel):
    prompt: str

class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI()
        self.setup_cors()
        self.setup_routes()

    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://localhost:5174"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*", "x-sambanova-key", "x-exa-key"],
        )

    def setup_routes(self):
        @self.app.post("/generate-leads")
        async def generate_leads(request: Request):
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
                result = crew.execute_research(extracted_info)

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

def create_app():
    api = LeadGenerationAPI()
    return api.app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
