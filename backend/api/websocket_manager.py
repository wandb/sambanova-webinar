from datetime import datetime
from autogen_core import DefaultTopicId
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Optional, Dict
import redis
from starlette.websockets import WebSocketState

from api.data_types import APIKeys, EndUserMessage
from api.utils import initialize_agent_runtime

from .otlp_tracing import logger


class WebSocketConnectionManager:
    """
    Manages WebSocket connections for user sessions.
    """

    def __init__(self, redis_client: redis.Redis):
        # Use user_id:conversation_id as the key
        self.connections: Dict[str, WebSocket] = {}
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
        agent_runtime = None
        pubsub = None
        try:
            # Check if conversation exists
            meta_key = f"chat_metadata:{user_id}:{conversation_id}"
            if not self.redis_client.exists(meta_key):
                await websocket.close(code=4004, reason="Conversation not found")
                return

            await websocket.accept()
            self.add_connection(websocket, user_id, conversation_id)

            # Set up Redis pubsub for this connection
            # Combine user_id and conversation_id with a colon delimiter
            source = f"{user_id}:{conversation_id}"
            channel = f"agent_thoughts:{source}"
            pubsub = self.redis_client.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(channel)

            # Load the API keys from Redis
            redis_api_keys = self.redis_client.hgetall(f"api_keys:{user_id}")                
            if not redis_api_keys:
                await websocket.send_json({
                    "event": "error",
                    "data": "No API keys found for this user",
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                })
                await websocket.close(code=4006, reason="No API keys found")
                return

            api_keys = APIKeys(
                SAMBANOVA_API_KEY=redis_api_keys.get("sambanova_key", ""),
                FIREWORKS_API_KEY=redis_api_keys.get("fireworks_key", ""),
                serper_key=redis_api_keys.get("serper_key", ""),
                exa_key=redis_api_keys.get("exa_key", "")
            )

            # Initialize agent runtime with error handling
            try:
                agent_runtime = await initialize_agent_runtime(
                    websocket=websocket,
                    redis_client=self.redis_client,
                    api_keys=api_keys,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )
            except Exception as e:
                logger.error(f"Failed to initialize agent runtime: {str(e)}")
                await websocket.close(code=4005, reason="Failed to initialize agent runtime")
                return

            # Send connection established message
            await websocket.send_json({
                "event": "connection_established",
                "data": "WebSocket connection established",
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
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
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    continue

                # Check if name field exists in metadata - non-blocking
                meta_key = f"chat_metadata:{user_id}:{conversation_id}"
                async def update_metadata():
                    meta_data = await asyncio.to_thread(self.redis_client.get, meta_key)
                    if meta_data:
                        metadata = json.loads(meta_data)
                        if "name" not in metadata:
                            metadata["name"] = user_message_input["data"]
                            await asyncio.to_thread(self.redis_client.set, meta_key, json.dumps(metadata))

                # Create task for metadata update without waiting
                asyncio.create_task(update_metadata())

                user_message = EndUserMessage(
                    source="User",
                    content=user_message_input["data"], 
                    use_planner=True,
                )    

                # Store message in Redis asynchronously without waiting
                message_key = f"messages:{user_id}:{conversation_id}"
                message_data = {
                    "event": "user_message", 
                    "data": user_message_input["data"],
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": user_message_input["timestamp"]
                }
                # Run Redis rpush in a thread pool since it's blocking
                asyncio.create_task(asyncio.to_thread(
                    self.redis_client.rpush,
                    message_key,
                    json.dumps(message_data)
                ))

                logger.info(f"Received message from user: {user_id} in conversation: {conversation_id}")

                # Publish the user's message to the agent using combined source
                await agent_runtime.publish_message(
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
            if pubsub:
                pubsub.unsubscribe()
                pubsub.close()
            if agent_runtime:
                try:
                    await agent_runtime.close()
                except Exception as e:
                    logger.error(f"Error closing agent runtime: {str(e)}")
            self.remove_connection(user_id, conversation_id)

            # Only attempt to close if the connection hasn't been closed from either end
            if (websocket.client_state != WebSocketState.DISCONNECTED and 
                websocket.application_state != WebSocketState.DISCONNECTED):
                try:
                    await websocket.close()
                except Exception as e:
                    # Log any closure errors but don't raise them
                    logger.info(f"Error during WebSocket closure for conversation {conversation_id}: {str(e)}")

    async def handle_redis_messages(self, websocket: WebSocket, pubsub, user_id: str, conversation_id: str):
        """
        Background task to handle Redis pub/sub messages and forward them to WebSocket.
        """
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message["type"] == "message":
                    data_str = message["data"]
                    message_data = {
                        "event": "think",
                        "data": data_str,
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Store think event in Redis
                    message_key = f"messages:{user_id}:{conversation_id}"
                    await asyncio.to_thread(
                        self.redis_client.rpush,
                        message_key,
                        json.dumps(message_data)
                    )

                    await websocket.send_json(message_data)

                # Send periodic ping to keep connection alive (not stored in Redis)
                await websocket.send_json({
                    "event": "ping",
                    "data": json.dumps({"type": "ping"}),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                })
                await asyncio.sleep(0.25)

        except Exception as e:
            logger.error(f"Error in Redis message handler: {str(e)}")
            raise
