import os
import sys
from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from utils.agent_thought import RedisConversationLogger

current_dir = os.getcwd()
repo_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(repo_dir)


@CrewBase
class EduDocSummariserCrew:
    """
    Educational document summariser crew implementation.

    This crew is responsible for summarising educational documents.
    """

    agents_config: Dict[str, Any]  # Type hint for the config attribute
    tasks_config: Dict[str, Any]  # Type hint for the tasks config
    agents: List[Any]  # Type hint for the agents list
    tasks: List[Any]  # Type hint for the tasks list
    llm: LLM
    sambanova_key: str
    serper_key: str
    user_id: str
    run_id: str

    def __init__(self, sambanova_key: str = None, user_id: str = None, run_id: str = None) -> None:
        """Initialize the research crew with API keys."""
        super().__init__()
        self.agents_config = {}
        self.tasks_config = {}
        self.agents = []
        self.tasks = []
        self.sambanova_key = sambanova_key
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-70B-Instruct",
            temperature=0.01,
            max_tokens=4096,
            api_key=self.sambanova_key
        )
        self.user_id = user_id
        self.run_id = run_id

    @agent
    def summariser(self) -> Agent:
        """
        Create the summariser agent.

        Returns:
            Agent: A configured planning agent
        """
        summariser_logger = RedisConversationLogger(
            user_id=self.user_id,
            run_id=self.run_id,
            agent_name="Summariser Agent"
        )
        return Agent(
            config=self.agents_config["summariser"],
            llm=self.llm,
            verbose=self.verbose,
            step_callback=summariser_logger,
        )

    @task
    def summarise_task(self) -> Task:
        """
        Define the summarise task.

        Returns:
            Task: A configured research task
        """
        return Task(
            config=self.tasks_config['summarise_task'],
        )

    @crew
    def crew(self, verbose: bool = True) -> Crew:
        """
        Create and configure the summariser crew.

        Returns:
            Crew: A configured crew with summarising capabilities
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=verbose,
        )
