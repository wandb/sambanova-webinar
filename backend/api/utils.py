import os
from autogen_core import SingleThreadedAgentRuntime
from autogen_core import AgentId
from autogen_core import DefaultSubscription
from autogen_core.tool_agent import ToolAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from backend.api.agents.financial_analysis import FinancialAnalysisAgent
from backend.api.agents.route import SemanticRouterAgent
from pydantic import BaseModel
from typing import get_origin, get_args, get_type_hints

from backend.api.data_types import APIKeys

from .otlp_tracing import configure_oltp_tracing, logger
from .registry import AgentRegistry
from .session_state import SessionStateManager

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

    # Register Semantic Router Agent
    await SemanticRouterAgent.register(
        agent_runtime,
        "router",
        lambda: SemanticRouterAgent(
            name="SemanticRouterAgent",
            session_manager=session_state_manager,
        ),
    )

    await FinancialAnalysisAgent.register(
        agent_runtime,
        "financial_analysis",
        lambda: FinancialAnalysisAgent(),
    )

    # Start the runtime
    agent_runtime.start()

    logger.info("Agent runtime initialized successfully.")

    return agent_runtime
