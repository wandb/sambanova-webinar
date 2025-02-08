from typing import Optional, List, Dict, Any
from enum import Enum
from .data_types import CoPilotPlan, EndUserMessage
from .otlp_tracing import logger
from pydantic import BaseModel
from typing import get_origin, get_args, get_type_hints

def generate_type_string(model: BaseModel) -> str:
    """Generates a string representation of the type structure of a Pydantic model, recursively."""

    def type_to_string(type_hint):
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is list:
            return f"List[{type_to_string(args[0])}]" if args else "List"
        elif origin:  # Generic type like List, Dict, etc.
            return str(origin).replace("typing.", "")
        elif isinstance(type_hint, type) and issubclass(type_hint, Enum):  # Handle Enum types
            enum_values = [f'"{v.value}"' for v in type_hint]
            return f"Enum({', '.join(enum_values)})"
        elif issubclass(type_hint, BaseModel):  # Check for nested Pydantic models
            return generate_type_string(type_hint)  # Recursive call
        elif hasattr(type_hint, '__name__'):  # Regular class
            return type_hint.__name__
        else:  # Basic type (str, int, etc.)
            return type_hint.__name__

    fields = get_type_hints(model) # Use get_type_hints to resolve forward refs
    fields_string = ", ".join(f'"{field}": {type_to_string(field_type)}' for field, field_type in fields.items())
    return "{ " + fields_string + " }"

class AgentRegistry:
    def __init__(self):
        self.agents = {
            "default_agent": {
                "agent_type": "default_agent",
                "description": "Handles user greetings, salutations, and general travel-related queries that do not fit into other specific categories. Route messages here if they are greetings (e.g., 'hi', 'hello', 'good morning') or general travel queries that do not specify a destination or service.",
                "examples": "'Hello', 'Hi there!', 'Good morning', 'I want to plan a trip.'",
            },
            "financial_analysis": {
                "agent_type": "financial_analysis",
                "description": "Handles financial analysis queries, including stock prices, financial statements, and market trends.",
                "examples": "'Tell me about the stock price of Apple', 'What's the financial statement of Tesla?', 'Market trends in the tech sector?'",
            },
        }
