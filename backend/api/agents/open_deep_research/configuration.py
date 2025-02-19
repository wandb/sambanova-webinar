########## configuration.py (NEW FILE) ##########
import os
from enum import Enum
from dataclasses import dataclass, field, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from dataclasses import dataclass

from config.model_registry import model_registry
from .prompts import improved_report_structure


DEFAULT_REPORT_STRUCTURE = """The report structure should focus on breaking-down the user-provided topic:

1. Introduction (research needed)
    - Brief overview of the topic area
2. Main Body Sections:
    - Each section should focus on a sub-topic of the user-provided topic
    - Include any key concepts and definitions
    - Provide real-world examples or case studies where applicable
3. Conclusion
    - Aim for 1 structural element (either a list or table) that distills the main body sections
    - Provide a concise summary of the report"""


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""

    report_structure: str = (
        DEFAULT_REPORT_STRUCTURE  # Defaults to the default report structure
    )
    number_of_queries: int = 2  # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    planner_model: str = model_registry.get_model_info(model_key="llama-3.3-70b")[
        "model"
    ]  # Defaults to OpenAI o3-mini as planner model
    writer_model: str = model_registry.get_model_info(model_key="llama-3.1-70b")[
        "model"
    ]  # Defaults to Anthropic as provider
    search_api: SearchAPI = SearchAPI.TAVILY  # Default to TAVILY

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
