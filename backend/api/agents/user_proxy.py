from datetime import datetime
import json
from typing import Dict, List, Any

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
)
from autogen_core.models import AssistantMessage
from fastapi import WebSocket
import redis

from api.session_state import SessionStateManager

from ..data_types import (
    AgentStructuredResponse,
    EndUserMessage,
)
from ..otlp_tracing import logger, format_log_message


# User Proxy Agent
class UserProxyAgent(RoutedAgent):
    """
    Acts as a proxy between the user and the routing agent.
    """

    def __init__(self, session_manager: SessionStateManager, websocket: WebSocket, redis_client: redis.Redis) -> None:
        super().__init__("UserProxyAgent")
        logger.info(format_log_message(None, f"Initializing UserProxyAgent with ID: {self.id} and WebSocket connection"))
        self.session_manager = session_manager
        self.websocket = websocket
        self.redis_client = redis_client

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
        logger.info(format_log_message(
            ctx.topic_id.source,
            f"Received response from {ctx.sender.type} agent"
        ))
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")
            if self.websocket:
                message_data = {
                    "event": "completion",
                    "data": message.model_dump_json(),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store in Redis
                message_key = f"messages:{user_id}:{conversation_id}"
                self.redis_client.rpush(
                    message_key,
                    json.dumps(message_data)
                )
                logger.info(format_log_message(
                    ctx.topic_id.source,
                    "Stored message in Redis"
                ))
                
                # Send through WebSocket
                await self.websocket.send_text(json.dumps(message_data))
                logger.info(format_log_message(
                    ctx.topic_id.source,
                    "Sent response to user via WebSocket"
                ))

                self.session_manager.add_to_history(
                    ctx.topic_id.source,
                    AssistantMessage(
                        content=message.data.model_dump_json(), source=ctx.sender.type
                    ),
                )
                logger.info(format_log_message(
                    ctx.topic_id.source,
                    "Updated conversation history"
                ))
        except Exception as e:
            logger.error(format_log_message(
                ctx.topic_id.source,
                f"Failed to send message: {str(e)}"
            ), exc_info=True)

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

        logger.info(format_log_message(
            ctx.topic_id.source,
            f"Forwarding user message to router: '{message.content[:100]}...'"
        ))

        # Forward the message to the router
        await self.publish_message(
            message,
            DefaultTopicId(type="router", source=ctx.topic_id.source),
        )
        logger.info(format_log_message(
            ctx.topic_id.source,
            "Successfully forwarded message to router"
        ))
