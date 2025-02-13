import os
from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from autogen_core import DefaultSubscription

from api.agents.financial_analysis import FinancialAnalysisAgent
from api.agents.educational_content import EducationalContentAgent
from api.agents.route import SemanticRouterAgent

from api.agents.sales_leads import SalesLeadsAgent
from autogen_agentchat.agents import AssistantAgent

from api.otlp_tracing import configure_oltp_tracing, logger
from api.session_state import SessionStateManager
from api.agents.user_proxy import UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from api.agents.assistant import AssistantAgentWrapper

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

    await EducationalContentAgent.register(
        agent_runtime,
        "educational_content",
        lambda: EducationalContentAgent(),
    )

    await SalesLeadsAgent.register(
        agent_runtime,
        "sales_leads",
        lambda: SalesLeadsAgent(),
    )

    await AssistantAgentWrapper.register(
        agent_runtime, "assistant", lambda: AssistantAgentWrapper("assistant")
    )

    # Register the UserProxyAgent instance with the AgentRuntime
    await UserProxyAgent.register(
        agent_runtime,
        "user_proxy",
        lambda: UserProxyAgent(session_manager=session_state_manager),
    )

    # Start the runtime
    agent_runtime.start()

    logger.info("Agent runtime initialized successfully.")

    return agent_runtime
