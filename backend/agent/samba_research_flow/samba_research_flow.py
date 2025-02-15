#!/usr/bin/env python
"""
Main module for the Educational Content Generation Flow.

This module implements a workflow for generating educational content using
multiple specialized AI crews. It handles the coordination between research
and content creation phases.
"""

import os
import asyncio
from typing import List, Dict, Any, Tuple

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv

load_dotenv()
from langtrace_python_sdk import langtrace
langtrace.init(api_key=os.getenv("LANGTRACE_API_KEY"))

from .crews.edu_content_writer.edu_content_writer_crew import EduContentWriterCrew
from .crews.edu_research.edu_research_crew import EducationalPlan, EduResearchCrew
from .crews.edu_doc_summariser.edu_doc_summariser_crew import EduDocSummariserCrew
import json


class SambaResearchFlow(Flow):
    """
    Reseach and Educational content generation workflow manager.

    This class orchestrates the process of researching topics and generating
    educational content through multiple specialized AI crews.

    Attributes:
        input_variables (dict): Configuration for the educational content generation
        research_crew (Crew): Crew responsible for research phase
        content_crew (Crew): Crew responsible for content creation phase
    """

    input_variables = Dict[str, Any]

    def __init__(
        self,
        sambanova_key: str = None,
        serper_key: str = None,
        user_id: str = None,
        run_id: str = None,
        docs_included: bool = False,
        verbose: bool = True
    ) -> None:
        """Initialize the educational flow with research and content creation crews."""
        super().__init__()
        self.summariser = EduDocSummariserCrew(
            sambanova_key=sambanova_key,
            user_id=user_id,
            run_id=run_id,
            verbose=verbose
        ).crew()
        self.research_crew = EduResearchCrew(
            sambanova_key=sambanova_key,
            serper_key=serper_key,
            user_id=user_id,
            run_id=run_id,
            verbose=verbose
        ).crew()
        self.content_crew = EduContentWriterCrew(
            sambanova_key=sambanova_key,
            user_id=user_id,
            run_id=run_id,
            verbose=verbose
        ).crew()
        self.docs_included = docs_included

    async def run_research_and_summarize(self) -> Tuple[EducationalPlan, Any]:
        """
        Run research and document summarization in parallel.

        Returns:
            Tuple[EducationalPlan, Any]: Research plan and document summaries
        """
        # Create tasks for parallel execution
        research_task = asyncio.create_task(
            asyncio.to_thread(
                lambda: self.research_crew.kickoff(self.input_variables).pydantic
            )
        )
        
        summary_task = None
        if self.docs_included:
            summary_task = asyncio.create_task(
                asyncio.to_thread(
                    lambda: self.summariser.kickoff(self.input_variables).raw
                )
            )
        
        # Wait for research task and optionally summary task
        research_result = await research_task
        summary_result = None
        if summary_task:
            summary_result = await summary_task
            
        return research_result, summary_result

    @start()
    async def generate_reseached_content(self) -> Tuple[EducationalPlan, Any]:
        """
        Begin the content generation process with parallel research and summarization.

        Returns:
            Tuple[EducationalPlan, Any]: Research plan and document summaries
        """
        return await self.run_research_and_summarize()

    @listen(generate_reseached_content)
    def generate_educational_content(self, results: Tuple[EducationalPlan, Any]) -> List[Dict]:
        """
        Generate educational content based on the research plan and summaries.

        Args:
            results (Tuple[EducationalPlan, Any]): The research plan and document summaries

        Returns:
            List[Dict]: List of sections with their plan and generated content.
        """
        plan, summaries = results
        sections_with_content = []

        for section in plan.sections:
            # Create section dict with all original fields
            section_dict = section.model_dump()

            # Generate content for this section
            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section.model_dump_json()

            if summaries:
                writer_inputs['docs'] = summaries
            else:
                writer_inputs['docs'] = "None"

            # Add generated content to the section dict
            section_dict['generated_content'] = self.content_crew.kickoff(writer_inputs).raw

            sections_with_content.append(section_dict)

        return sections_with_content


def kickoff() -> None:
    """Initialize and start the educational content generation process."""
    edu_flow = SambaResearchFlow()
    edu_flow.kickoff()


def plot() -> None:
    """Generate and display a visualization of the flow structure."""
    edu_flow = SambaResearchFlow()
    edu_flow.plot()


def test_flow() -> List[Dict]:
    """
    Helper function to test the educational flow with predefined inputs.
    Returns the generated content sections.
    """
    edu_flow = SambaResearchFlow(
        sambanova_key="fake",
        serper_key="fake"
    )
    
    # Convert focus_areas list to comma-separated string
    focus_areas = ", ".join([
        "technical comparison",
        "performance characteristics",
        "use cases"
    ])
    
    edu_flow.input_variables = {
        "topic": "SRAM and High Bandwidth Memory",
        "audience_level": "intermediate",
        "additional_context": focus_areas  # Now a string instead of a dict
    }
    
    return edu_flow.kickoff()


if __name__ == '__main__':
    result = test_flow()
    print(result)
