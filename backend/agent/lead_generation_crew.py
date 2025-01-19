import sys
import os
import json

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from crewai import Agent, Task, Crew, LLM, Process
from tools.company_intelligence_tool import CompanyIntelligenceTool
from tools.market_research_tool import MarketResearchTool
from typing import List
from pydantic import BaseModel

class Outreach(BaseModel):
    company_name: str
    website: str
    headquarters: str
    funding_status: str
    email_subject: str
    email_body: str

class OutreachList(BaseModel):
    outreach_list: List[Outreach]

class ResearchCrew:
    def __init__(self):
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-70B-Instruct",
            temperature=0.8,
            max_tokens=4096
        )
        
        self._initialize_agents()
        self._initialize_tasks()

    def _initialize_agents(self) -> None:
        """Initialize all agents."""


        # Agent for company research
        self.company_research_agent = Agent(
            role="Company Research Specialist",
            goal="Conduct comprehensive research on target companies",
            backstory="You are an expert business analyst ...",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[CompanyIntelligenceTool()]
        )

        # Agent for market research
        self.market_trends_agent = Agent(
            role="Market Trends Analyst",
            goal="Analyze current market trends and opportunities",
            backstory="You are an experienced market research analyst ...",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[MarketResearchTool()]
        )

        # Agent for outreach
        self.outreach_agent = Agent(
            role="Outreach Specialist",
            goal="Create compelling, personalized outreach emails",
            backstory="You craft personalized outreach messages ...",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def _initialize_tasks(self) -> None:
        """Set up the tasks in the correct order."""


        # 2) Company Research
        self.company_research_task = Task(
            description=(
                "Use the JSON from prompt_extraction_task. Perform a search with:\n"
                "industry: {industry}, company_stage: {company_stage}, geography: {geography}, "
                "funding_stage: {funding_stage}, product: {product}.\n"
                "Then analyze the returned companies ..."
            ),
            expected_output=(
                "For each company found:\n"
                "- Company Name\n"
                "- Website\n"
                "- Headquarters\n"
                "- Funding Status\n"
                "- etc."
            ),
            agent=self.company_research_agent,
        )

        # 3) Market Research
        self.market_trends_task = Task(
            description=(
                "Use Market Research Intelligence with:\n"
                "industry: {industry}\n"
                "product: {product}\n"
                "Then map findings to each company from the previous step."
            ),
            expected_output=(
                "[\n"
                "  {\n"
                "    'company_name': '...',\n"
                "    'relevant_trends': '...',\n"
                "    'opportunities': '...',\n"
                "    'challenges': '...'\n"
                "  },\n"
                "  ...\n"
                "]"
            ),
            agent=self.market_trends_agent,
            context=[self.company_research_task]
        )

        # 4) Outreach
        self.outreach_task = Task(
            description=(
                "Create a JSON array of personalized emails for the researched companies. "
                "1. Each entry: company_name, website, headquarters, funding_status, email_subject, email_body. "
                "2. Email body must start with 'Dear [Company]' and be 50-125 words ... "
                "Return ONLY a JSON array."
            ),
            expected_output=(
                "[\n"
                "  {\n"
                "    'company_name': '...',\n"
                "    'website': '...',\n"
                "    'headquarters': '...',\n"
                "    'funding_status': '...',\n"
                "    'email_subject': '...',\n"
                "    'email_body': '...'\n"
                "  }\n"
                "]"
            ),
            agent=self.outreach_agent,
            context=[self.company_research_task, self.market_trends_task],
            output_pydantic=OutreachList
        )

    def execute_research(self, inputs: dict) -> str:
        """
        Runs the entire 4-step pipeline. 
        Inputs must contain a key 'prompt'.
        Returns a string (raw) representing the final results (JSON or text).
        """
        crew = Crew(
            agents=[
                self.company_research_agent,
                self.market_trends_agent,
                self.outreach_agent
            ],
            tasks=[
                self.company_research_task,
                self.market_trends_task,
                self.outreach_task
            ],
            process=Process.sequential,
            verbose=True,
            memory=False
        )

        results = crew.kickoff(inputs=inputs)
        return results.pydantic.model_dump_json()

def main():
    crew = ResearchCrew()
    prompt = "Generate leads for quantum computing startups in California interested in AI-driven cryptography"

    final_output = crew.execute_research({"prompt": prompt})
    print("Crew Output:")
    print(final_output)

if __name__ == "__main__":
    main()
