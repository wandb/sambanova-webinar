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

        # self.agent_tools = self.retrieve_all_agent_tools()

    def retrieve_all_agent_tools(self) -> List[Dict[str, Any]]:
        tools = []
        agent_tools = {
            "flight_booking": get_flight_booking_tool(),
            "hotel_booking": get_hotel_booking_tool(),
            "car_rental": get_car_rental_tool(),
            "activities_booking": get_travel_activity_tools(),
        }

        for agent, tool_list in agent_tools.items():
            for tool in tool_list:
                tools.append(
                    {
                        "agent": agent,
                        "function": tool.name,
                        "description": tool.description,
                        "arguments": list(tool.schema["parameters"]["properties"]),
                    }
                )
        # logger.info(f"Agent tools: {tools}")

        return tools

    async def get_agent(self, intent: str) -> Optional[dict]:
        logger.info(f"AgentRegistry: Getting agent for intent: {intent}")
        return self.agents.get(intent)

    def get_planner_prompt(self, message: EndUserMessage, history) -> str:
        agent_details = {}
        for agent in self.agents.values():
            agent_details[agent["agent_type"]] = {
                "description": agent["description"],
                "examples": agent.get("examples", ""),
                "functions": [],
            }

        # for tool in self.agent_tools:
        #     agent = tool["agent"]
        #     function = tool["function"]
        #     arguments = tool["arguments"]
        #     agent_details[agent]["functions"].append(
        #         {"function": function, "arguments": arguments}
        #     )

        agent_descriptions = "\n".join(
            f"""
    Agent Type: {agent_type}
    Description: {details['description']}
    Examples: {details['examples']}
    {chr(10).join([f"- Function: {func['function']} (Arguments: {', '.join(func['arguments'])})" for func in details['functions']]) if details['functions'] else ""}
    """
            for agent_type, details in agent_details.items()
        )

        planner_prompt = """
    You are an orchestration agent.
    Your job is to decide which agents to run based on the user's request and the conversation history.
    Below are the available agents:

    {agent_descriptions}

    The current user message: {message}
    Conversation history so far: {history}

    Your response should only include the selected agent and a brief justification for your choice, without any additional text.
    Ensure your final answer contains only the content in the following format:{json_schema}\n\n
    Ensure the final output does not include any code block markers like ```json or ```python.
    """.format(
            agent_descriptions=agent_descriptions.strip(),
            message=message.content,
            history=", ".join(msg.content for msg in history),
            json_schema=generate_type_string(CoPilotPlan),
        )
        # logger.info(f"Planner prompt output: {planner_prompt}")
        return planner_prompt
