from autogen_core import SingleThreadedAgentRuntime
from autogen_core import AgentId
from autogen_core import DefaultSubscription
from autogen_core.tool_agent import ToolAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from .otlp_tracing import configure_oltp_tracing, logger
from .registry import AgentRegistry
from .session_state import SessionStateManager

sn_api_url = "https://api.sambanova.ai/v1"
sn_api_key = "a8b6c87f-d356-4c4c-accc-ff7f8432b74c"

aoai_model_client = OpenAIChatCompletionClient(
    model="Meta-Llama-3.1-70B-Instruct",
    base_url=sn_api_url,
    api_key=sn_api_key,
    model_info={
        'json_output': False,
        'function_calling': True,
        'family': 'unknown',
        'vision': False
    }
)

session_state_manager = SessionStateManager()

tracer = configure_oltp_tracing()

async def initialize_agent_runtime() -> SingleThreadedAgentRuntime:
    """
    Initializes the agent runtime with the required agents and tools.

    Returns:
        SingleThreadedAgentRuntime: The initialized runtime for managing agents.
    """
    global session_state_manager, aoai_model_client
    agent_runtime = SingleThreadedAgentRuntime(tracer_provider=tracer)

    # Add subscriptions
    logger.info("Adding user proxy subscription")
    await agent_runtime.add_subscription(
        DefaultSubscription(topic_type="user_proxy", agent_type="user_proxy")
    )

    # Start the runtime
    agent_runtime.start()

    logger.info("Agent runtime initialized successfully.")

    return agent_runtime
