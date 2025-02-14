"""
Module for handling educational content generation through a crew of specialized agents.

This module implements a CrewAI-based content generation system with multiple agents
working together to create, edit, and review educational content.
"""

import os
from typing import Any, Dict, List

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from utils.agent_thought import RedisConversationLogger



@CrewBase
class EduContentWriterCrew:
    """
    A crew of AI agents specialized in creating educational content.

    This crew consists of three main agents:
    - Content Writer: Creates initial educational content
    - Editor: Refines and improves the content
    - Quality Reviewer: Ensures content meets educational standards

    Attributes:
        input_variables (dict): Configuration variables for educational content generation
    """

    input_variables = Dict[str, Any] # Type hint for the input variables
    agents_config: Dict[str, Any]  # Type hint for the config attribute
    tasks_config: Dict[str, Any]  # Type hint for the tasks config
    agents: List[Any]  # Type hint for the agents list
    tasks: List[Any]  # Type hint for the tasks list
    llm: LLM
    sambanova_key: str
    user_id: str
    run_id: str

    def __init__(self, sambanova_key: str = None, user_id: str = None, run_id: str = None) -> None:
        """Initialize the content writer crew with API key."""
        super().__init__()
        self.agents_config = {}
        self.tasks_config = {}
        self.agents = []
        self.tasks = []
        self.input_variables = {}
        self.sambanova_key = sambanova_key
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-70B-Instruct",
            temperature=0.01,
            max_tokens=4096,
            api_key=self.sambanova_key
        )
        self.user_id = user_id
        self.run_id = run_id
        self.__post_init__()

    def __post_init__(self) -> None:
        """Initialize the crew by ensuring required directories exist."""
        self.ensure_output_folder_exists()

    def ensure_output_folder_exists(self) -> None:
        """
        Create the output directory if it doesn't exist.

        This method ensures that the 'output' directory is available for storing
        generated content files.
        """
        output_folder = 'output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    @agent
    def content_writer(self) -> Agent:
        """
        Create the content writer agent.

        Returns:
            Agent: An AI agent specialized in creating educational content.
        """
        content_writer_logger = RedisConversationLogger(
            user_id=self.user_id,
            run_id=self.run_id,
            agent_name="Content Writer Agent"
        )
        return Agent(config=self.agents_config['content_writer'], llm=self.llm, verbose=True,step_callback=content_writer_logger)

    @agent
    def editor(self) -> Agent:
        """
        Create the editor agent.

        Returns:
            Agent: An AI agent specialized in editing and refining content.
        """
        editor_logger = RedisConversationLogger(
            user_id=self.user_id,
            run_id=self.run_id,
            agent_name="Editor Agent"
        )
        return Agent(config=self.agents_config['editor'], llm=self.llm, verbose=True,step_callback=editor_logger)

    @agent
    def quality_reviewer(self) -> Agent:
        """
        Create the quality reviewer agent.

        Returns:
            Agent: An AI agent specialized in reviewing and ensuring content quality.
        """
        quality_reviewer_logger = RedisConversationLogger(
            user_id=self.user_id,
            run_id=self.run_id,
            agent_name="Quality Reviewer Agent"
        )
        return Agent(config=self.agents_config['quality_reviewer'], llm=self.llm, verbose=True,step_callback=quality_reviewer_logger)

    @task
    def writing_task(self) -> Task:
        """
        Define the initial content writing task.

        Returns:
            Task: A task configuration for content creation.
        """
        return Task(
            config=self.tasks_config['writing_task'],
        )

    @task
    def editing_task(self) -> Task:
        """
        Define the content editing task.

        This task includes file path configuration based on the topic and audience level.

        Returns:
            Task: A task configuration for content editing.
        """
        topic = self.input_variables.get('topic')
        audience_level = self.input_variables.get('audience_level')
        file_name = f'{topic}_{audience_level}.md'.replace(' ', '_')
        output_file_path = os.path.join('output', file_name)

        return Task(config=self.tasks_config['editing_task'], output_file=output_file_path)

    @task
    def quality_review_task(self) -> Task:
        """
        Define the quality review task.

        Returns:
            Task: A task configuration for quality review.
        """
        return Task(
            config=self.tasks_config['quality_review_task'],
        )

    @crew
    def crew(self, verbose: bool = True) -> Crew:
        """
        Create and configure the content creation crew.

        Returns:
            Crew: A configured crew with all necessary agents and tasks.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=verbose,
        )
