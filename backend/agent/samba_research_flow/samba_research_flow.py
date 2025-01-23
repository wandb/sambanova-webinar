#!/usr/bin/env python
"""
Main module for the Educational Content Generation Flow.

This module implements a workflow for generating educational content using
multiple specialized AI crews. It handles the coordination between research
and content creation phases.
"""

import os
from typing import List, Dict, Any

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv

from .crews.edu_content_writer.edu_content_writer_crew import EduContentWriterCrew
from .crews.edu_research.edu_research_crew import EducationalPlan, EduResearchCrew
import json

load_dotenv()


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

    def __init__(self, sambanova_key: str = None, serper_key: str = None) -> None:
        """Initialize the educational flow with research and content creation crews."""
        super().__init__()
        self.research_crew = EduResearchCrew(
            sambanova_key=sambanova_key,
            serper_key=serper_key
        ).crew()
        self.content_crew = EduContentWriterCrew(
            sambanova_key=sambanova_key
        ).crew()

    @start()
    def generate_reseached_content(self) -> EducationalPlan:
        """
        Begin the content generation process with research.

        Returns:
            EducationalPlan: A structured plan for educational content based on research.
        """
        return self.research_crew.kickoff(self.input_variables).pydantic

    @listen(generate_reseached_content)
    def generate_educational_content(self, plan: EducationalPlan) -> List[Dict]:
        """
        Generate educational content based on the research plan.

        Args:
            plan (EducationalPlan): The structured content plan from research phase.

        Returns:
            List[Dict]: List of sections with their plan and generated content.
        """
        sections_with_content = []

        for section in plan.sections:
            # Create section dict with all original fields
            section_dict = section.model_dump()
            
            # Generate content for this section
            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section.model_dump_json()
            
            # Add generated content to the section dict
            section_dict['generated_content'] = self.content_crew.kickoff(writer_inputs).raw
            
            sections_with_content.append(section_dict)

            #dump the complete sections_with_content to a json file
            with open('sections_with_content.json', 'w') as f:
                json.dump(sections_with_content, f)

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
