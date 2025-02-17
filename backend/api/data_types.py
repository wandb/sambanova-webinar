########## NEW CODE ##########
from pydantic import BaseModel, model_validator, Field
from enum import Enum
from typing import List, Optional, Union, Dict
from datetime import date
from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisResult
from agent.samba_research_flow.crews.edu_research.edu_research_crew import Section
from agent.lead_generation_crew import OutreachList

# Enum to Define Agent Types
class AgentEnum(str, Enum):
    FinancialAnalysis = "financial_analysis"
    EducationalContent = "educational_content"
    SalesLeads = "sales_leads"
    Assistant = "assistant"
    UserProxy = "user_proxy"
    # NEWLY ADDED AGENT:
    DeepResearch = "deep_research"  # For advanced research (LangGraph)

class Greeter(BaseModel):
    greeting: str

class UserQuestion(BaseModel):
    user_question: str

class AssistantMessage(BaseModel):
    query: str

class AssistantResponse(BaseModel):
    response: str

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

class HandoffMessage(BaseAgentMessage):
    content: str

class APIKeys(BaseModel):
    sambanova_key: str
    serper_key: str
    exa_key: str

class FinancialAnalysis(BaseModel):
    ticker: Optional[str] = Field(default=None, description="The ticker of the company")
    company_name: str = Field(default="", description="The name of the company")
    query_text: str = Field(default="", description="The query text from the user")

class SalesLeads(BaseModel):
    industry: str = Field(default="", description="The industry of the company")
    company_stage: Optional[str] = Field(default=None, description="The stage of the company")
    geography: Optional[str] = Field(default=None, description="The geography for the sales leads")
    funding_stage: Optional[str] = Field(default=None, description="The funding stage for the sales leads")
    product: Optional[str] = Field(default=None, description="The product for the sales leads")

class DeepResearch(BaseModel):
    topic: str = Field(default="", description="The topic of the research")

class EducationalContent(BaseModel):
    topic: str = Field(default="", description="The topic of the research")
    audience_level: Optional[str] = Field(default=None, description="What level of audience is the research for")
    focus_areas: Optional[str] = Field(default=None, description="The focus areas of the research")

    # Convert list to string for backwards compatibility
    @model_validator(mode="before")
    def convert_focus_areas_list(cls, data):
        if isinstance(data, dict) and "focus_areas" in data:
            if isinstance(data["focus_areas"], list):
                data["focus_areas"] = ", ".join(str(area) for area in data["focus_areas"])
        return data

class EndUserMessage(BaseAgentMessage):
    content: str
    use_planner: bool = False
    document_ids: Optional[List[str]] = None

class AgentRequest(BaseModel):
    agent_type: AgentEnum
    parameters: Union[
        FinancialAnalysis, SalesLeads, EducationalContent, AssistantMessage, UserQuestion
    ]
    query: str
    document_ids: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_parameters_type(self) -> "AgentRequest":
        expected_type = {
            AgentEnum.FinancialAnalysis: FinancialAnalysis,
            AgentEnum.SalesLeads: SalesLeads,
            AgentEnum.EducationalContent: EducationalContent,
            AgentEnum.Assistant: AssistantMessage,
            AgentEnum.UserProxy: UserQuestion,
            AgentEnum.DeepResearch: EducationalContent,  # same as before
        }[self.agent_type]

        if isinstance(self.parameters, expected_type):
            return self
        if isinstance(self.parameters, dict):
            self.parameters = expected_type.model_validate(self.parameters)
        else:
            raise ValueError(
                f"Parameters must be of type {expected_type.__name__} for agent_type {self.agent_type}"
            )
        return self

class ExtendedSection(Section):
    generated_content: str

class EducationalPlanResult(BaseModel):
    """
    Represents the complete educational content plan (the older approach).
    """
    sections: List[ExtendedSection] = []

#
# NEW DEEP-RESEARCH STRUCTURES
#
class DeepResearchSection(BaseModel):
    name: str
    description: str
    content: str
    citations: List[Dict[str, str]] = Field(default_factory=list)

class DeepResearchReport(BaseModel):
    """
    A structured object that collects the final multi-section
    deep research report, plus the raw final text if needed.
    """
    sections: List[DeepResearchSection]
    final_report: str  # The entire compiled text in one string

# We now allow AgentStructuredResponse to return DeepResearchReport
class AgentStructuredResponse(BaseModel):
    agent_type: AgentEnum
    data: Union[
        FinancialAnalysisResult,
        EducationalPlanResult,
        OutreachList,
        Greeter,
        AssistantResponse,
        UserQuestion,
        DeepResearchReport,  # ADDED
    ]
    message: Optional[str] = None  # Additional message or notes from the agent
