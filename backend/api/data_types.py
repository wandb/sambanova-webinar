from pydantic import BaseModel, model_validator
from enum import Enum
from typing import List, Optional, Union
from datetime import date
from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisResult
from agent.samba_research_flow.crews.edu_research.edu_research_crew import EducationalPlan
from agent.lead_generation_crew import OutreachList


# Enum to Define Agent Types
class AgentEnum(str, Enum):
    FinancialAnalysis = "financial_analysis"
    EducationalContent = "educational_content"
    SalesLeads = "sales_leads"
    DefaultAgent = "default_agent"

class Greeter(BaseModel):
    greeting: str

# Generic Response Wrapper
class AgentStructuredResponse(BaseModel):
    agent_type: AgentEnum
    data: Union[
        FinancialAnalysisResult,
        EducationalPlan,
        OutreachList,
        Greeter,
    ]
    message: Optional[str] = None  # Additional message or notes from the agent

# Base class for messages exchanged between agents and users
class BaseAgentMessage(BaseModel):
    source: str
    timestamp: Optional[date] = None

class TestMessage(BaseAgentMessage):
    content: str

# SubTask Model
class CoPilotSubTask(BaseModel):
    task_details: str
    assigned_agent: AgentEnum

    class Config:
        use_enum_values = True  # To serialize enums as their values

class FinancialAnalysisTask(BaseModel):
    ticker: str = ""
    company_name: str = ""
    query_text: str = ""

class SalesLeadsTask(BaseModel):
    industry: str = ""
    company_stage: str = ""
    geography: str = ""
    funding_stage: str = ""
    product: str = ""

class CoPilotPlan(BaseModel):
    main_task: str
    subtasks: List[Union[FinancialAnalysisTask, SalesLeadsTask]]
    is_greeting: bool

class HandoffMessage(BaseAgentMessage):
    content: str


class APIKeys(BaseModel):
    sambanova_key: str
    serper_key: str 
    exa_key: str

class FinancialAnalysis(BaseModel):
    ticker: Optional[str] = None
    company_name: str
    query_text: str

class SalesLeads(BaseModel):
    industry: str
    company_stage: Optional[str] = None
    geography: Optional[str] = None
    funding_stage: Optional[str] = None
    product: Optional[str] = None

class EducationalContent(BaseModel):
    topic: str
    audience_level: Optional[str] = None
    focus_areas: Optional[str] = None

    # Convert list to string for backwards compatibility
    @model_validator(mode='before')
    def convert_focus_areas_list(cls, data):
        if isinstance(data, dict) and 'focus_areas' in data:
            if isinstance(data['focus_areas'], list):
                data['focus_areas'] = ', '.join(str(area) for area in data['focus_areas'])
        return data

class EndUserMessage(BaseAgentMessage):
    content: str
    api_keys: APIKeys
    use_planner: bool = False
    document_ids: Optional[List[str]] = None


class AgentRequest(BaseModel):
    agent_type: AgentEnum
    parameters: Union[FinancialAnalysis, SalesLeads, EducationalContent]
    query: str
    api_keys: APIKeys
    document_ids: Optional[List[str]] = None

    @model_validator(mode='after')
    def validate_parameters_type(self) -> 'AgentRequest':
        expected_type = {
            AgentEnum.FinancialAnalysis: FinancialAnalysis,
            AgentEnum.SalesLeads: SalesLeads,
            AgentEnum.EducationalContent: EducationalContent,
        }[self.agent_type]
        
        # If parameters is already the correct type, return as is
        if isinstance(self.parameters, expected_type):
            return self
            
        # If it's a dict, try to convert it to the expected type
        if isinstance(self.parameters, dict):
            self.parameters = expected_type.model_validate(self.parameters)
        else:
            raise ValueError(f"Parameters must be of type {expected_type.__name__} for agent_type {self.agent_type}")
        
        return self
