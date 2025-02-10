from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Union
from datetime import date
from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisResult
from agent.samba_research_flow.crews.edu_research.edu_research_crew import EducationalPlan


# Enum to Define Agent Types
class AgentEnum(str, Enum):
    FinancialAnalysis = "financial_analysis"
    EducationalContent = "educational_content"
    DefaultAgent = "default_agent"

class Greeter(BaseModel):
    greeting: str

# Generic Response Wrapper
class AgentStructuredResponse(BaseModel):
    agent_type: AgentEnum
    data: Union[
        FinancialAnalysisResult,
        EducationalPlan,
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


class CoPilotPlan(BaseModel):
    main_task: str
    subtasks: List[CoPilotSubTask]
    is_greeting: bool

class HandoffMessage(BaseAgentMessage):
    content: str


class APIKeys(BaseModel):
    sambanova_key: str
    serper_key: str 
    exa_key: str

class FinancialAnalysisRequest(BaseModel):
    ticker: str
    company_name: str
    query_text: str
    document_ids: Optional[List[str]] = None
    api_keys: APIKeys

class EducationalContentRequest(BaseModel):
    topic: str
    audience_level: str
    focus_areas: Optional[List[str]] = None
    api_keys: APIKeys
    document_ids: Optional[List[str]] = None

class EndUserMessage(BaseAgentMessage):
    content: str
    api_keys: APIKeys
    document_ids: Optional[List[str]] = None