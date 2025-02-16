########## NEW CODE ##########
import os
from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from autogen_core import DefaultSubscription
from fastapi import WebSocket
import redis

from api.agents.financial_analysis import FinancialAnalysisAgent
from api.agents.educational_content import EducationalContentAgent
from api.agents.route import SemanticRouterAgent

from api.agents.sales_leads import SalesLeadsAgent
from autogen_agentchat.agents import AssistantAgent

from api.otlp_tracing import configure_oltp_tracing
from utils.logging import logger
from api.session_state import SessionStateManager
from api.agents.user_proxy import UserProxyAgent

from api.agents.assistant import AssistantAgentWrapper
from api.data_types import APIKeys

# NEW IMPORT: our new DeepResearchAgent
from api.agents.deep_research_agent import DeepResearchAgent

session_state_manager = SessionStateManager()

tracer = configure_oltp_tracing()

async def initialize_agent_runtime(
    websocket: WebSocket, redis_client: redis.Redis, api_keys: APIKeys
) -> SingleThreadedAgentRuntime:
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
            websocket=websocket,
            redis_client=redis_client,
            api_keys=api_keys,
        ),
    )

    await FinancialAnalysisAgent.register(
        agent_runtime,
        "financial_analysis",
        lambda: FinancialAnalysisAgent(api_keys=api_keys),
    )

    # Keep old educational content agent for “basic” usage
    await EducationalContentAgent.register(
        agent_runtime,
        "educational_content",
        lambda: EducationalContentAgent(api_keys=api_keys),
    )

    await SalesLeadsAgent.register(
        agent_runtime,
        "sales_leads",
        lambda: SalesLeadsAgent(api_keys=api_keys),
    )

    await AssistantAgentWrapper.register(
        agent_runtime, "assistant", lambda: AssistantAgentWrapper(api_keys=api_keys)
    )

    # Register the new deep research agent:
    await DeepResearchAgent.register(
        agent_runtime,
        "deep_research",
        lambda: DeepResearchAgent(api_keys=api_keys, session_manager=session_state_manager),
    )

    # Register the UserProxyAgent instance with the AgentRuntime
    await UserProxyAgent.register(
        agent_runtime,
        "user_proxy",
        lambda: UserProxyAgent(
            session_manager=session_state_manager,
            websocket=websocket,
            redis_client=redis_client,
        ),
    )

    # Start the runtime
    agent_runtime.start()

    logger.info("Agent runtime initialized successfully.")

    return agent_runtime
