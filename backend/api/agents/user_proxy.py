
import asyncio
import json
from typing import Dict, List, Any

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import LLMMessage, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from api.websocket_manager import WebSocketConnectionManager

from ..data_types import (
    AgentStructuredResponse,
    EndUserMessage,
)
from ..otlp_tracing import logger

# User Proxy Agent
class UserProxyAgent(RoutedAgent):
    """
    Acts as a proxy between the user and the routing agent.
    """
    connection_manager: WebSocketConnectionManager = None  # Will be set by LeadGenerationAPI

    def __init__(self) -> None:
        super().__init__("UserProxyAgent")

    @message_handler
    async def handle_agent_response(
        self,
        message: AgentStructuredResponse,
        ctx: MessageContext,
    ) -> None:
        """
        Sends the agent's response back to the user via WebSocket.

        Args:
            message (AgentStructuredResponse): The agent's response message.
            ctx (MessageContext): The message context.
        """
        logger.info(f"UserProxyAgent received agent response: {message}")
        # ctx.topic_id.source is already in format "user_id:conversation_id"
        try:
            websocket = self.connection_manager.connections.get(ctx.topic_id.source)
            user_id, conversation_id = ctx.topic_id.source.split(":")
            if websocket:
                await websocket.send_text(json.dumps({
                    "event": "completion", 
                    "data": message.model_dump_json(),
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }))
        except Exception as e:
            logger.error(f"Failed to send message to session {ctx.topic_id.source}: {str(e)}")

    @message_handler
    async def handle_user_message(
        self, message: EndUserMessage, ctx: MessageContext
    ) -> None:
        """
        Forwards the user's message to the router for further processing.

        Args:
            message (EndUserMessage): The user's message.
            ctx (MessageContext): The message context.
        """

        logger.info(f"UserProxyAgent received user message: {message.content}")
        
        # Forward the message to the router
        await self.publish_message(
            message,
            DefaultTopicId(type="router", source=ctx.topic_id.source),
        )