from autogen_core import AgentRuntime, DefaultTopicId
from fastapi import FastAPI, File, Query, Request, BackgroundTasks, UploadFile, WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Optional, Dict, Any, List
import redis
from starlette.websockets import WebSocketState

from api.data_types import APIKeys, EndUserMessage

from .otlp_tracing import logger



class WebSocketConnectionManager:
    """
    Manages WebSocket connections for user sessions.
    """

    def __init__(self, agent_runtime: AgentRuntime, redis_client: redis.Redis):
        # Use user_id:conversation_id as the key
        self.connections: Dict[str, WebSocket] = {}
        self.agent_runtime = agent_runtime
        self.redis_client = redis_client

    def add_connection(self, websocket: WebSocket, user_id: str, conversation_id: str) -> None:
        """
        Adds a new WebSocket connection to the manager.

        Args:
            websocket (WebSocket): The WebSocket connection.
            user_id (str): The ID of the user.
            conversation_id (str): The ID of the conversation.
        """
        key = f"{user_id}:{conversation_id}"
        self.connections[key] = websocket

    def get_connection(self, user_id: str, conversation_id: str) -> Optional[WebSocket]:
        """
        Gets WebSocket connection for a user's conversation.

        Args:
            user_id (str): The ID of the user.
            conversation_id (str): The ID of the conversation.

        Returns:
            Optional[WebSocket]: The WebSocket connection if found, None otherwise.
        """
        key = f"{user_id}:{conversation_id}"
        return self.connections.get(key)

    def remove_connection(self, user_id: str, conversation_id: str) -> None:
        """
        Removes a WebSocket connection from the manager.

        Args:
            user_id (str): The ID of the user.
            conversation_id (str): The ID of the conversation.
        """
        key = f"{user_id}:{conversation_id}"
        if key in self.connections:
            del self.connections[key]

    async def handle_websocket(self, websocket: WebSocket, user_id: str, conversation_id: str):
        """
        Handles incoming WebSocket messages and manages connection lifecycle.

        Args:
            websocket (WebSocket): The WebSocket connection.
            user_id (str): The ID of the user.
            conversation_id (str): The ID of the conversation.
        """
        await websocket.accept()
        self.add_connection(websocket, user_id, conversation_id)

        # Set up Redis pubsub for this connection
        # Combine user_id and conversation_id with a colon delimiter
        source = f"{user_id}:{conversation_id}"
        channel = f"agent_thoughts:{source}"
        pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(channel)

        try:
            # Send connection established message
            await websocket.send_json({
                "event": "connection_established",
                "data": "WebSocket connection established",
                "user_id": user_id,
                "conversation_id": conversation_id
            })

            # Start background task for Redis messages
            background_task = asyncio.create_task(self.handle_redis_messages(websocket, pubsub, user_id, conversation_id))

            # Handle incoming WebSocket messages
            while True:
                user_message_text = await websocket.receive_text()
                try:
                    user_message_input = json.loads(user_message_text)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "event": "error",
                        "data": "Invalid JSON message format",
                        "user_id": user_id,
                        "conversation_id": conversation_id
                    })
                    continue

                # Load the API keys from Redis
                redis_api_keys = self.redis_client.hgetall(f"api_keys:{user_id}")                
                if not redis_api_keys:
                    await websocket.send_json({
                        "event": "error",
                        "data": "No API keys found for this user",
                        "user_id": user_id,
                        "conversation_id": conversation_id
                    })
                    continue
                
                api_keys = APIKeys(
                    sambanova_key=redis_api_keys.get("sambanova_key", ""),
                    serper_key=redis_api_keys.get("serper_key", ""),
                    exa_key=redis_api_keys.get("exa_key", "")
                )
                
                user_message = EndUserMessage(
                    source="User",
                    content=user_message_input["data"], 
                    api_keys=api_keys,
                    use_planner=True,
                )

                logger.info(f"Received message from user: {user_id} in conversation: {conversation_id}")

                # Publish the user's message to the agent using combined source
                await self.agent_runtime.publish_message(
                    user_message,
                    DefaultTopicId(type="user_proxy", source=f"{user_id}:{conversation_id}"),
                )
                await asyncio.sleep(0.1)

        except WebSocketDisconnect:
            logger.info(f"WebSocket connection closed for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Exception in WebSocket connection for conversation {conversation_id}: {str(e)}")
        finally:
            # Clean up
            if 'background_task' in locals():
                background_task.cancel()
            pubsub.unsubscribe()
            pubsub.close()
            self.remove_connection(user_id, conversation_id)
            try:
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
            except WebSocketDisconnect:
                logger.info(f"WebSocket already closed for conversation: {conversation_id}")

    async def handle_redis_messages(self, websocket: WebSocket, pubsub, user_id: str, conversation_id: str):
        """
        Background task to handle Redis pub/sub messages and forward them to WebSocket.
        """
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    data_str = message["data"]
                    await websocket.send_json({
                        "event": "think",
                        "data": data_str,
                        "user_id": user_id,
                        "conversation_id": conversation_id
                    })

                # Send periodic ping to keep connection alive
                await websocket.send_json({
                    "event": "ping",
                    "data": json.dumps({"type": "ping"})
                })
                await asyncio.sleep(0.25)

        except Exception as e:
            logger.error(f"Error in Redis message handler: {str(e)}")
            raise