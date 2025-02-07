from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Union
from datetime import date
from backend.agent.financial_analysis.financial_analysis_crew import FinancialAnalysisResult


# Enum to Define Agent Types
class AgentEnum(str, Enum):
    FinancialAnalysisResult = "financial_analysis"

# Generic Response Wrapper
class AgentStructuredResponse(BaseModel):
    agent_type: AgentEnum
    data: Union[
        FinancialAnalysisResult,
    ]
    message: Optional[str] = None  # Additional message or notes from the agent

# Base class for messages exchanged between agents and users
class BaseAgentMessage(BaseModel):
    source: str
    timestamp: Optional[date] = None

class EndUserMessage(BaseAgentMessage):
    content: str

class TestMessage(BaseAgentMessage):
    content: str
