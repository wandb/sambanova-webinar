# lead_generation_api.py

from fastapi import FastAPI
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
from services.read_json_test import JSONFileReader
from agent.lead_generation_crew import ResearchCrew

class QueryRequest(BaseModel):
    query: str

class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI()
        self.prompt_extractor = UserPromptExtractor()
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.use_agent_pipeline = True

        @self.app.post("/research")
        def execute_research(request: QueryRequest):
            if self.use_agent_pipeline:
                # 1) Extract structured info from user query
                extracted_json = self.prompt_extractor.extract_lead_info(request.query)
               
                # 2) Initialize research crew
                crew = ResearchCrew()
                
                # 3) Execute the research pipeline with the extracted JSON
                #    The agent returns a JSON string in `results_str`
                results_str = crew.execute_research(dict(extracted_json))
                
                # 4) Parse the JSON string into a Python dict
                parsed_result = json.loads(results_str)
                
                # 5) Extract the 'outreach_list' (which should be a list of outreach objects)
                outreach_list = parsed_result.get("outreach_list", [])
                
                # 6) Return that list at the top level so the frontend gets [ {..}, {..}, ... ]
                return JSONResponse(content=outreach_list)
            else:
                # Fallback behavior
                time.sleep(3)
                structured_json = JSONFileReader().read_json()
                return structured_json

def create_app():
    api = LeadGenerationAPI()
    return api.app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
