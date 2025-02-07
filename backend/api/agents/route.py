import json
from collections import deque

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from backend.services.query_router_service import QueryRouterService, QueryType

from ..data_types import (
    AgentEnum,
    EndUserMessage,
    CoPilotPlan,
    AgentStructuredResponse,
    FinancialAnalysisRequest,
    Greeter,
    HandoffMessage,
)
from ..otlp_tracing import logger
from ..registry import AgentRegistry
from ..session_state import SessionStateManager

agent_registry = AgentRegistry()


@type_subscription(topic_type="router")
class SemanticRouterAgent(RoutedAgent):
    """
    The SemanticRouterAgent routes incoming messages to appropriate agents based on the intent.

    Attributes:
        name (str): Name of the agent.
        model_client (OpenAIChatCompletionClient): The model client for agent routing.
        agent_registry (AgentRegistry): The registry containing agent information.
        session_manager (SessionStateManager): Manages the session state for each user.
    """

    def __init__(
        self,
        name: str,
        model_client: OpenAIChatCompletionClient,
        session_manager: SessionStateManager,
        sambanova_key: str,
    ) -> None:
        super().__init__("SemanticRouterAgent")
        logger.info(f"Initializing SemanticRouterAgent with ID: {self.id}")
        self._name = name
        self._model_client = model_client
        self._session_manager = session_manager
        self._sambanova_key = sambanova_key

    @message_handler
    async def route_message(self, message: EndUserMessage, ctx: MessageContext) -> None:
        """
        Routes user messages to appropriate agents based on conversation context.

        Args:
            message (EndUserMessage): The incoming user message.
            ctx (MessageContext): Context information for the message.
        """
        session_id = ctx.topic_id.source

        # Add the current message to session history
        self._session_manager.add_to_history(session_id, message)

        # Analyze conversation history for better context
        history = self._session_manager.get_history(session_id)
        logger.info("Analyzing conversation history for context")

        router = QueryRouterService(self._sambanova_key)

        route_result: QueryType = router.route_query(message.content)

        if route_result.type == "financial_analysis":
            logger.info(f"Publishing financial analysis request with parameters: {route_result.parameters}")
            await self.publish_message(
                FinancialAnalysisRequest(**route_result.parameters),
                DefaultTopicId(type="financial_analysis", source=session_id),
            )
            logger.info("Financial analysis request published")
            return


    @message_handler
    async def handle_handoff(
        self, message: HandoffMessage, ctx: MessageContext
    ) -> None:
        """
        Handles handoff messages from other agents.

        Args:
            message (HandoffMessage): The handoff message from another agent.
            ctx (MessageContext): Context information for the message.
        """
        session_id = ctx.topic_id.source
        logger.info(f"Received handoff message from {message.source}")

        # Clear session if conversation is complete, otherwise continue routing
        if message.original_task and "complete" in message.content.lower():
            self._session_manager.clear_session(session_id)
        else:
            await self.route_message(
                EndUserMessage(content=message.content, source=message.source), ctx
            )

    async def _get_agents_to_route(
        self, message: EndUserMessage, history: deque
    ) -> CoPilotPlan:
        """
        Determines the appropriate agents to route the message to based on context.

        Args:
            message (EndUserMessage): The incoming user message.
            history (deque): The history of messages in the session.

        Returns:
            CoPilotPlan: A plan indicating which agents should handle the subtasks.
        """
        # System prompt to determine the appropriate agents to handle the message
        logger.info(f"Analyzing message: {message.content}")
        try:
            logger.info(
                f"Getting planner prompt for message: {message.content} and history: {[msg.content for msg in history]}"
            )
            system_message = agent_registry.get_planner_prompt(
                message=message, history=history
            )
        except Exception as e:
            logger.error(e)

        try:
            response = await self._model_client.create(
                [SystemMessage(content=system_message)],
            )

            
            copilot_plan: CoPilotPlan = CoPilotPlan.model_validate(
                json.loads(response.content)
            )
            if copilot_plan.is_greeting:
                logger.info("User greeting detected")
                copilot_plan.subtasks = [
                    {
                        "task_details": f"Greeting - {message.content}",
                        "assigned_agent": "default_agent",
                    }
                ]

            logger.info(f"Received copilot plan: {copilot_plan}")
            return copilot_plan
        except Exception as e:
            logger.error(f"Failed to parse activities response: {str(e)}")
            return CoPilotPlan(subtasks=[])
