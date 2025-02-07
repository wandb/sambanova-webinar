from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Union
from datetime import date
from backend.agent.financial_analysis.financial_analysis_crew import FinancialAnalysisResult


# Enum to Define Agent Types
class AgentEnum(str, Enum):
    FinancialAnalysis = "financial_analysis"
    DefaultAgent = "default_agent"

class Greeter(BaseModel):
    greeting: str

# Generic Response Wrapper
class AgentStructuredResponse(BaseModel):
    agent_type: AgentEnum
    data: Union[
        FinancialAnalysisResult,
        Greeter,
    ]
    message: Optional[str] = None  # Additional message or notes from the agent

# Base class for messages exchanged between agents and users
class BaseAgentMessage(BaseModel):
    source: str
    timestamp: Optional[date] = None

class EndUserMessage(BaseAgentMessage):
    content: str
    document_ids: Optional[List[str]] = None

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

class FinancialAnalysisRequest(BaseModel):
    ticker: str
    company_name: str
    query_text: str
    document_ids: Optional[List[str]] = None
