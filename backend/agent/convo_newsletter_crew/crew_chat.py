import json
import re
import sys
import time
import threading
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

import click

from crewai.crew import Crew
from crewai.llm import LLM
from crewai.types.crew_chat import ChatInputField, ChatInputs
from crewai.utilities.llm_utils import create_llm

# Import your actual "newsletter_crew.py" that can accept API keys.
from .newsletter_crew import ConvoNewsletterCrew

###############################################################################
# In-memory store for API usage
###############################################################################
CONVERSATION_STORE: Dict[str, Dict[str, Any]] = {}

###############################################################################
# 1) CLI-based chat loop (old functionality)
###############################################################################

def run_chat():
    """Runs an interactive chat loop (like old CLI)."""
    click.secho("\nAnalyzing crew for conversation-based usage. Please wait...\n", fg="white")

    crew_obj, messages, crew_tool_schema, available_functions = _initialize_cli_crew()

    click.secho("\nFinished analyzing crew.\n", fg="white")
    first_assistant_message = messages[-1]["content"]
    click.secho(f"Assistant: {first_assistant_message}\n", fg="green")

    while True:
        try:
            user_input = _get_user_input()
            if user_input.strip().lower() == "exit":
                click.echo("Exiting chat. Goodbye!")
                break
            if not user_input.strip():
                click.echo("Empty message. Provide input or type 'exit'.")
                continue

            messages.append({"role": "user", "content": user_input})

            click.echo()
            click.secho("Assistant is processing your input. Please wait...", fg="green")

            # Multi-turn approach
            response_text = _multi_turn_llm_call(crew_obj, messages, crew_tool_schema, available_functions)
            messages.append({"role": "assistant", "content": response_text})

            click.secho(f"\nAssistant: {response_text}\n", fg="green")

        except KeyboardInterrupt:
            click.echo("\nExiting chat. Goodbye!")
            break
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")
            break

def _initialize_cli_crew():
    """
    Creates the crew in a CLI scenario, builds system message, calls LLM for intro.
    """
    crew_object = ConvoNewsletterCrew().crew()

    chat_llm = create_llm(crew_object.chat_llm)
    crew_name = "ConvoNewsletterCrew"
    crew_chat_inputs = generate_crew_chat_inputs(crew_object, crew_name, chat_llm)

    crew_tool_schema = generate_crew_tool_schema(crew_chat_inputs)
    system_message = build_system_message(crew_chat_inputs)

    # Intro message
    intro_msg = chat_llm.call(messages=[{"role": "system", "content": system_message}])
    messages = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": intro_msg},
    ]

    available_functions = {
        crew_chat_inputs.crew_name: create_tool_function(crew_object, messages)
    }
    return crew_object, messages, crew_tool_schema, available_functions

def _get_user_input() -> str:
    """Gather multi-line user input for CLI usage."""
    click.secho("\nYou (type your message; press Enter twice to finish):", fg="blue")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)

###############################################################################
# 2) Multi-turn approach (like the CLI function-calling)
###############################################################################

def _multi_turn_llm_call(
    crew_obj: Crew,
    messages: List[Dict[str, str]],
    crew_tool_schema: Dict[str, Any],
    available_functions: Dict[str, Any],
    max_calls: int = 3
) -> str:
    """
    Does a short loop to handle the possibility the LLM calls the function
    multiple times for a single user message.
    """
    chat_llm = crew_obj.chat_llm

    for _ in range(max_calls):
        raw_response = chat_llm.call(
            messages=messages,
            tools=[crew_tool_schema],
            available_functions=available_functions,
        )
        # If no function call => final text
        if not _is_function_call(raw_response):
            return raw_response

        # Else parse the function call
        fn_name, fn_args = _parse_function_call(raw_response)

        # If the LLM used "brain_dump" or another name, unify to "ConvoNewsletterCrew"
        # or you can do some mapping.
        # We'll treat ANY name as "ConvoNewsletterCrew" for simplicity:
        if fn_name not in available_functions:
            # We unify
            fn_name = list(available_functions.keys())[0]  # e.g. "ConvoNewsletterCrew"

            # the original call might have placeholders in "parameters"
            # so we merge them into fn_args
            # e.g. raw_response = {"name":"brain_dump", "parameters":{"brain_dump":"..."}}
            # We'll keep the same arguments
            # If you want to parse them differently, you can.

        # Actually call the crew's function
        try:
            tool_func = available_functions[fn_name]
            tool_output = tool_func(**fn_args)
        except Exception as e:
            tool_output = f"Error running function {fn_name}: {str(e)}"

        # Append the function output
        messages.append({"role": "assistant", "content": tool_output})

    # If we run out of calls, return whatever last message was
    return messages[-1]["content"]

def _is_function_call(response_text: str) -> bool:
    """
    We assume the LLM returns JSON with a "name" field if it's a function call.
    """
    trimmed = response_text.strip()
    return trimmed.startswith("{") and '"name":' in trimmed

def _parse_function_call(response_text: str) -> Tuple[str, Dict[str, Any]]:
    data = json.loads(response_text)
    fn_name = data.get("name", "")
    fn_args = data.get("arguments", {})
    if not isinstance(fn_args, dict):
        fn_args = {}
    return fn_name, fn_args

###############################################################################
# 3) API-based methods
###############################################################################

def api_init_conversation(
    sambanova_key: str,
    serper_key: Optional[str] = None,
    exa_key: Optional[str] = None,
    user_id: Optional[str] = None,
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a new conversation, like the CLI does, storing the
    resulting system+intro messages in memory.
    """
    # Build crew
    crew_object = ConvoNewsletterCrew(
        sambanova_key=sambanova_key,
        serper_key=serper_key,
        user_id=user_id
    ).crew()

    chat_llm = create_llm(crew_object.chat_llm)
    crew_name = "ConvoNewsletterCrew"
    crew_chat_inputs = generate_crew_chat_inputs(crew_object, crew_name, chat_llm)

    crew_tool_schema = generate_crew_tool_schema(crew_chat_inputs)
    system_message = build_system_message(crew_chat_inputs)

    intro_msg = chat_llm.call(messages=[{"role": "system", "content": system_message}])
    messages = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": intro_msg},
    ]

    available_functions = {
        crew_chat_inputs.crew_name: create_tool_function(crew_object, messages)
    }

    conversation_id = str(uuid.uuid4())
    CONVERSATION_STORE[conversation_id] = {
        "crew": crew_object,
        "messages": messages,
        "crew_tool_schema": crew_tool_schema,
        "available_functions": available_functions,
        "sambanova_key": sambanova_key,
        "serper_key": serper_key,
        "exa_key": exa_key,
        "user_id": user_id,
        "run_id": run_id
    }

    return {
        "conversation_id": conversation_id,
        "assistant_message": intro_msg
    }

def api_process_message(conversation_id: str, user_input: str) -> str:
    """
    Each user message triggers the same multi-turn approach used in CLI.
    """
    if conversation_id not in CONVERSATION_STORE:
        raise ValueError(f"No conversation found for id='{conversation_id}'.")

    data = CONVERSATION_STORE[conversation_id]
    crew_obj: Crew = data["crew"]
    messages = data["messages"]
    crew_tool_schema = data["crew_tool_schema"]
    available_functions = data["available_functions"]

    if not user_input.strip():
        return "You sent an empty message. Try again."

    # Append user input
    messages.append({"role": "user", "content": user_input})

    # Same multi-turn logic
    final_text = _multi_turn_llm_call(
        crew_obj,
        messages,
        crew_tool_schema,
        available_functions
    )

    messages.append({"role": "assistant", "content": final_text})
    CONVERSATION_STORE[conversation_id]["messages"] = messages

    return final_text

###############################################################################
# 4) Shared helper methods
###############################################################################

def generate_crew_chat_inputs(crew: Crew, crew_name: str, chat_llm: LLM) -> ChatInputs:
    required_inputs = fetch_required_inputs(crew)
    input_fields = []
    for input_name in required_inputs:
        desc = generate_input_description_with_ai(input_name, crew, chat_llm)
        input_fields.append(ChatInputField(name=input_name, description=desc))

    crew_description = generate_crew_description_with_ai(crew, chat_llm)
    return ChatInputs(
        crew_name=crew_name,
        crew_description=crew_description,
        inputs=input_fields
    )

def fetch_required_inputs(crew: Crew) -> Set[str]:
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    required_inputs: Set[str] = set()

    for t in crew.tasks:
        text = (t.description or "") + " " + (t.expected_output or "")
        required_inputs.update(placeholder_pattern.findall(text))

    for a in crew.agents:
        text = (a.role or "") + " " + (a.goal or "") + " " + (a.backstory or "")
        required_inputs.update(placeholder_pattern.findall(text))

    return required_inputs

def generate_input_description_with_ai(
    input_name: str,
    crew: Crew,
    chat_llm: LLM
) -> str:
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    context_texts = []

    for t in crew.tasks:
        if f"{{{input_name}}}" in (t.description or "") or f"{{{input_name}}}" in (t.expected_output or ""):
            desc = placeholder_pattern.sub(lambda m: m.group(1), t.description or "")
            out = placeholder_pattern.sub(lambda m: m.group(1), t.expected_output or "")
            context_texts.append(f"Task Description: {desc}")
            context_texts.append(f"Task Output: {out}")

    for a in crew.agents:
        if (
            f"{{{input_name}}}" in (a.role or "") or
            f"{{{input_name}}}" in (a.goal or "") or
            f"{{{input_name}}}" in (a.backstory or "")
        ):
            role = placeholder_pattern.sub(lambda m: m.group(1), a.role or "")
            goal = placeholder_pattern.sub(lambda m: m.group(1), a.goal or "")
            back = placeholder_pattern.sub(lambda m: m.group(1), a.backstory or "")
            context_texts.append(f"Agent Role: {role}")
            context_texts.append(f"Agent Goal: {goal}")
            context_texts.append(f"Agent Backstory: {back}")

    if not context_texts:
        return f"User input for '{input_name}'."

    joined = "\n".join(context_texts)
    prompt = (
        f"Given this context, describe '{input_name}' in <=15 words.\n"
        f"{joined}"
    )
    resp = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return resp.strip() or f"User input for '{input_name}'."


def generate_crew_description_with_ai(crew: Crew, chat_llm: LLM) -> str:
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    context_texts = []

    for t in crew.tasks:
        desc = placeholder_pattern.sub(lambda m: m.group(1), t.description or "")
        out = placeholder_pattern.sub(lambda m: m.group(1), t.expected_output or "")
        context_texts.append(f"Task Description: {desc}")
        context_texts.append(f"Expected Output: {out}")

    for a in crew.agents:
        role = placeholder_pattern.sub(lambda m: m.group(1), a.role or "")
        goal = placeholder_pattern.sub(lambda m: m.group(1), a.goal or "")
        back = placeholder_pattern.sub(lambda m: m.group(1), a.backstory or "")
        context_texts.append(f"Agent Role: {role}")
        context_texts.append(f"Agent Goal: {goal}")
        context_texts.append(f"Agent Backstory: {back}")

    if not context_texts:
        return "A specialized newsletter crew."

    joined = "\n".join(context_texts)
    prompt = (
        "Based on this context, provide a concise (<15 words) action-oriented "
        "description of the crew:\n"
        f"{joined}"
    )
    resp = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return resp.strip() or "A specialized newsletter crew."


def generate_crew_tool_schema(crew_inputs: ChatInputs) -> dict:
    properties = {}
    for field in crew_inputs.inputs:
        properties[field.name] = {
            "type": "string",
            "description": field.description or "No description provided"
        }
    required = [f.name for f in crew_inputs.inputs]

    return {
        "type": "function",
        "function": {
            "name": crew_inputs.crew_name,
            "description": crew_inputs.crew_description or "No crew description",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }

def build_system_message(crew_chat_inputs: ChatInputs) -> str:
    required_fields_str = ", ".join(
        f"{field.name} (desc: {field.description})" for field in crew_chat_inputs.inputs
    ) or "(No required fields)"

    return (
        "You are a helpful AI assistant integrated with CrewAI. "
        "You have a function you can call by name if you have all the required inputs. "
        f"The required inputs: {required_fields_str}. "
        "If the user goes off-topic, answer briefly, then remind them of the crew's purpose. "
        "Always keep your responses concise.\n\n"
        f"Crew Name: {crew_chat_inputs.crew_name}\n"
        f"Crew Description: {crew_chat_inputs.crew_description}"
    )

def create_tool_function(crew: Crew, messages: List[Dict[str, str]]):
    def run_crew_tool_with_messages(**kwargs):
        return run_crew_tool(crew, messages, **kwargs)
    return run_crew_tool_with_messages

def run_crew_tool(crew: Crew, messages: List[Dict[str, str]], **kwargs) -> str:
    try:
        kwargs["crew_chat_messages"] = json.dumps(messages)
        output = crew.kickoff(inputs=kwargs)
        return str(output)
    except Exception as e:
        raise RuntimeError(f"Error running the crew: {str(e)}") from e

if __name__ == "__main__":
    run_chat()
