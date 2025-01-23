"""
Educational research crew module for content generation.

This module implements a specialized crew for conducting research and planning
educational content.
"""

import os
import sys
from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel

current_dir = os.getcwd()
repo_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(repo_dir)



class Section(BaseModel):
    """
    Represents a section in the educational content plan.

    Attributes:
        title: The section title
        high_level_goal: The main objective of the section
        why_important: Explanation of the section's importance
        sources: List of reference sources
        content_outline: Structured outline of the section content
    """

    title: str
    high_level_goal: str
    why_important: str
    sources: List[str]
    content_outline: List[str]


class EducationalPlan(BaseModel):
    """
    Represents the complete educational content plan.

    Attributes:
        sections: List of content sections
    """

    sections: List[Section]


@CrewBase
class EduResearchCrew:
    """
    Educational research crew implementation.

    This crew is responsible for conducting research and planning educational
    content structure.
    """

    agents_config: Dict[str, Any]  # Type hint for the config attribute
    tasks_config: Dict[str, Any]  # Type hint for the tasks config
    agents: List[Any]  # Type hint for the agents list
    tasks: List[Any]  # Type hint for the tasks list
    llm: LLM
    sambanova_key: str
    serper_key: str

    def __init__(self, sambanova_key: str = None, serper_key: str = None) -> None:
        """Initialize the research crew with API keys."""
        super().__init__()
        self.agents_config = {}
        self.tasks_config = {}
        self.agents = []
        self.tasks = []
        self.sambanova_key = sambanova_key
        self.serper_key = serper_key
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-70B-Instruct",
            temperature=0.01,
            max_tokens=4096,
            api_key=self.sambanova_key
        )

    @agent
    def researcher(self) -> Agent:
        """
        Create the researcher agent.

        Returns:
            Agent: A configured research agent with search capabilities
        """
        # Temporarily set serper key in environment for this tool instance
        os.environ["SERPER_API_KEY"] = self.serper_key
        tool = SerperDevTool()
           
        return Agent(config=self.agents_config['researcher'], llm=self.llm, verbose=True, tools=[tool])

    @agent
    def planner(self) -> Agent:
        """
        Create the planner agent.

        Returns:
            Agent: A configured planning agent
        """
        return Agent(config=self.agents_config['planner'], llm=self.llm, verbose=True)

    @task
    def research_task(self) -> Task:
        """
        Define the research task.

        Returns:
            Task: A configured research task
        """
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def planning_task(self) -> Task:
        """
        Define the planning task.

        Returns:
            Task: A configured planning task with EducationalPlan output
        """
        return Task(config=self.tasks_config['planning_task'], output_pydantic=EducationalPlan)

    @crew
    def crew(self) -> Crew:
        """
        Create and configure the research crew.

        Returns:
            Crew: A configured crew with research and planning capabilities
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
