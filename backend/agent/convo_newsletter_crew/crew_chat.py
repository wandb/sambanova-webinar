import json
import re
import sys
import time
import threading
import uuid
from typing import Any, Dict, List, Optional, Set

# We'll keep CLI references to preserve original "old functionality"
import click

from crewai.crew import Crew
from crewai.llm import LLM
from crewai.types.crew_chat import ChatInputField, ChatInputs
from crewai.utilities.llm_utils import create_llm

# Import your actual "newsletter_crew.py"
# We'll rely on a constructor that can accept the various API keys.
from .newsletter_crew import ConvoNewsletterCrew

###############################################################################
# In-memory conversation store for the new API usage.
###############################################################################
CONVERSATION_STORE: Dict[str, Dict[str, Any]] = {}
# Each entry is keyed by conversation_id with structure like:
# {
#   "crew": <Crew instance>,
#   "messages": <list of dicts>,
#   "crew_tool_schema": <dict>,
#   "available_functions": <dict>,
#   ...
# }

###############################################################################
# 1) CLI-based chat loop (OLD FUNCTIONALITY) - minimal changes to keep it working
###############################################################################

def run_chat():
    """
    Runs an interactive chat loop (like the old CLI).
    We do not rely on pyproject.toml or version checks.
    """
    click.secho(
        "\nAnalyzing crew for conversation-based usage. Please wait...\n",
        fg="white"
    )

    # Instantiate the default ConvoNewsletterCrew without explicit keys
    # (assumes they're in environment or a default is used)
    crew, messages, crew_tool_schema, available_functions = _initialize_cli_crew()

    click.secho("\nFinished analyzing crew.\n", fg="white")
    first_assistant_message = messages[-1]["content"]
    click.secho(f"Assistant: {first_assistant_message}\n", fg="green")

    # Now enter a loop for user input
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

            chat_llm: LLM = crew.chat_llm
            final_response = chat_llm.call(
                messages=messages,
                tools=[crew_tool_schema],
                available_functions=available_functions,
            )
            messages.append({"role": "assistant", "content": final_response})
            click.secho(f"\nAssistant: {final_response}\n", fg="green")

        except KeyboardInterrupt:
            click.echo("\nExiting chat. Goodbye!")
            break
        except Exception as exc:
            click.secho(f"Error: {exc}", fg="red")
            break

def _initialize_cli_crew():
    """
    Creates the crew in a CLI scenario, generates system message,
    calls LLM for an intro, and returns (crew, messages, schema, available_functions).
    """
    # 1) Build a crew
    crew_object = ConvoNewsletterCrew().crew()

    # 2) Analyze tasks/agents
    chat_llm = create_llm(crew_object.chat_llm)
    crew_name = "ConvoNewsletterCrew"
    crew_chat_inputs = generate_crew_chat_inputs(crew_object, crew_name, chat_llm)
    crew_tool_schema = generate_crew_tool_schema(crew_chat_inputs)
    system_message = build_system_message(crew_chat_inputs)

    # 3) Intro message
    introductory_message = chat_llm.call(messages=[{"role": "system", "content": system_message}])
    messages = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    available_functions = {
        crew_chat_inputs.crew_name: create_tool_function(crew_object, messages)
    }

    return crew_object, messages, crew_tool_schema, available_functions


def _get_user_input() -> str:
    """
    Collect multi-line user input with blank line as delimiter (CLI style).
    """
    click.secho("\nYou (type your message; press Enter twice to finish):", fg="blue")
    lines = []
    while True:
        line = input()
        if not line:
            # blank line => done
            break
        lines.append(line)
    return "\n".join(lines)

###############################################################################
# 2) NEW: API-based methods (init & message) that do NOT re-init the Crew each time
###############################################################################

def api_init_conversation(
    sambanova_key: str,
    serper_key: Optional[str] = None,
    exa_key: Optional[str] = None,
    user_id: Optional[str] = None,
    run_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initializes a brand-new conversation by creating a ConvoNewsletterCrew
    with the provided keys and user/run info, analyzing tasks/agents to build
    a system message & function schema, then returns the initial assistant reply.
    """
    # 1) Create the crew with the user-supplied keys & IDs
    #    (Inside ConvoNewsletterCrew.__init__, you might store them or pass them to LLMs)
    crew_object = ConvoNewsletterCrew(
        sambanova_key=sambanova_key,
        serper_key=serper_key,
        user_id=user_id,
    ).crew()

    # 2) Same analysis as CLI does
    chat_llm = create_llm(crew_object.chat_llm)
    crew_name = "ConvoNewsletterCrew"
    crew_chat_inputs = generate_crew_chat_inputs(crew_object, crew_name, chat_llm)
    crew_tool_schema = generate_crew_tool_schema(crew_chat_inputs)
    system_message = build_system_message(crew_chat_inputs)

    # 3) Get the initial assistant message
    introductory_message = chat_llm.call(
        messages=[{"role": "system", "content": system_message}]
    )

    # 4) Start conversation
    messages = [
        {"role": "system", "content": system_message},
        {"role": "assistant", "content": introductory_message},
    ]

    available_functions = {
        crew_chat_inputs.crew_name: create_tool_function(crew_object, messages)
    }

    # 5) Unique conversation id
    conversation_id = str(uuid.uuid4())

    # 6) Store in memory
    CONVERSATION_STORE[conversation_id] = {
        "crew": crew_object,
        "messages": messages,
        "crew_tool_schema": crew_tool_schema,
        "available_functions": available_functions,
        "user_id": user_id,
        "run_id": run_id,
        "sambanova_key": sambanova_key,
        "serper_key": serper_key,
        "exa_key": exa_key
    }

    return {
        "conversation_id": conversation_id,
        "assistant_message": introductory_message
    }


def api_process_message(
    conversation_id: str,
    user_input: str
) -> str:
    """
    Accepts a new user message for an existing conversation,
    calls the LLM with the same messages & tool schema, and returns the new assistant reply.
    We do NOT re-instantiate the crew, so no repeated overhead.
    """
    if conversation_id not in CONVERSATION_STORE:
        raise ValueError(f"No conversation found for id='{conversation_id}'.")

    data = CONVERSATION_STORE[conversation_id]
    crew: Crew = data["crew"]
    messages = data["messages"]
    crew_tool_schema = data["crew_tool_schema"]
    available_functions = data["available_functions"]

    if not user_input.strip():
        # If the user sends an empty message
        return "You sent an empty message. Try again."

    # Add user message
    messages.append({"role": "user", "content": user_input})

    # Summon the chat LLM
    chat_llm: LLM = crew.chat_llm
    assistant_reply = chat_llm.call(
        messages=messages,
        tools=[crew_tool_schema],
        available_functions=available_functions,
    )

    # Append assistant's message
    messages.append({"role": "assistant", "content": assistant_reply})

    # Store updated messages
    CONVERSATION_STORE[conversation_id]["messages"] = messages

    return assistant_reply

###############################################################################
# 3) Common helper methods from the original approach (used by both CLI & API)
###############################################################################

def generate_crew_chat_inputs(crew: Crew, crew_name: str, chat_llm: LLM) -> ChatInputs:
    """
    Gathers placeholders (like {topic}, {audience}) from tasks & agents,
    then uses the LLM to produce short descriptions for each placeholder
    and also a short description for the entire crew.
    """
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

    # tasks
    for t in crew.tasks:
        text = (t.description or "") + " " + (t.expected_output or "")
        required_inputs.update(placeholder_pattern.findall(text))

    # agents
    for a in crew.agents:
        text = (a.role or "") + " " + (a.goal or "") + " " + (a.backstory or "")
        required_inputs.update(placeholder_pattern.findall(text))

    return required_inputs


def generate_input_description_with_ai(
    input_name: str, crew: Crew, chat_llm: LLM
) -> str:
    """
    Looks up any references to {input_name} in tasks/agents,
    then calls the LLM to produce a short human-friendly description for it.
    """
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    context_texts = []

    # tasks
    for t in crew.tasks:
        if f"{{{input_name}}}" in (t.description or "") or f"{{{input_name}}}" in (t.expected_output or ""):
            desc = placeholder_pattern.sub(lambda m: m.group(1), t.description or "")
            out = placeholder_pattern.sub(lambda m: m.group(1), t.expected_output or "")
            context_texts.append(f"Task Description: {desc}")
            context_texts.append(f"Task Output: {out}")

    # agents
    for a in crew.agents:
        references = (
            f"{{{input_name}}}" in (a.role or "") or
            f"{{{input_name}}}" in (a.goal or "") or
            f"{{{input_name}}}" in (a.backstory or "")
        )
        if references:
            role = placeholder_pattern.sub(lambda m: m.group(1), a.role or "")
            goal = placeholder_pattern.sub(lambda m: m.group(1), a.goal or "")
            back = placeholder_pattern.sub(lambda m: m.group(1), a.backstory or "")
            context_texts.append(f"Agent Role: {role}")
            context_texts.append(f"Agent Goal: {goal}")
            context_texts.append(f"Agent Backstory: {back}")

    if not context_texts:
        # If it doesn't appear anywhere, just do a default
        return f"User input for '{input_name}'."

    joined = "\n".join(context_texts)
    prompt = (
        f"Given this crew context, describe '{input_name}' in <=15 words. "
        "No placeholders or extra text:\n"
        f"{joined}"
    )
    response = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip() or f"User input for '{input_name}'."


def generate_crew_description_with_ai(crew: Crew, chat_llm: LLM) -> str:
    """
    Summarizes the entire crew in 15 words or fewer, scanning tasks/agents for context.
    """
    placeholder_pattern = re.compile(r"\{(.+?)\}")
    context_texts = []

    for t in crew.tasks:
        desc = placeholder_pattern.sub(lambda m: m.group(1), t.description or "")
        out = placeholder_pattern.sub(lambda m: m.group(1), t.expected_output or "")
        context_texts.append(f"Task Description: {desc}")
        context_texts.append(f"Task Output: {out}")

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
        "Based on the context below, provide a concise (<15 words) action-oriented "
        "description of the crew:\n"
        f"{joined}"
    )
    response = chat_llm.call(messages=[{"role": "user", "content": prompt}])
    return response.strip() or "A specialized newsletter crew."


def generate_crew_tool_schema(crew_inputs: ChatInputs) -> dict:
    """
    Builds a function schema (for function calling) referencing the placeholders
    found in the crew's tasks/agents.
    """
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
    """
    Creates the "system" role message describing the crew, placeholders, usage.
    """
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
    """
    Returns a function that runs crew.kickoff with the placeholders
    the LLM has provided. The LLM can "invoke" this function.
    """
    def run_crew_tool_with_messages(**kwargs):
        return run_crew_tool(crew, messages, **kwargs)
    return run_crew_tool_with_messages


def run_crew_tool(crew: Crew, messages: List[Dict[str, str]], **kwargs) -> str:
    """
    Actually calls 'crew.kickoff(inputs=kwargs)', returning the result as a string.
    Embeds the entire conversation in 'crew_chat_messages' for reference if needed.
    """
    try:
        kwargs["crew_chat_messages"] = json.dumps(messages)
        result = crew.kickoff(inputs=kwargs)
        return str(result)
    except Exception as ex:
        raise RuntimeError(f"Error running the crew: {ex}") from ex


###############################################################################
# If you want to allow "python crew_chat.py" to start a CLI chat, do so:
###############################################################################
if __name__ == "__main__":
    run_chat()
