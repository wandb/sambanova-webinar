from datetime import datetime
from autogen_core import DefaultTopicId
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Optional, Dict
import redis
from starlette.websockets import WebSocketState
import time

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
        background_task = None
        
        # Pre-compute keys that will be used throughout the session
        meta_key = f"chat_metadata:{user_id}:{conversation_id}"
        message_key = f"messages:{user_id}:{conversation_id}"
        api_keys_key = f"api_keys:{user_id}"
        source = f"{user_id}:{conversation_id}"
        channel = f"agent_thoughts:{source}"

        try:
            # Initial setup tasks that can run concurrently
            setup_tasks = [
                asyncio.to_thread(self.redis_client.exists, meta_key),
                asyncio.to_thread(self.redis_client.hgetall, api_keys_key),
                asyncio.to_thread(lambda: self.redis_client.pubsub(ignore_subscribe_messages=True))
            ]
            
            # Wait for all setup tasks to complete
            exists, redis_api_keys, pubsub = await asyncio.gather(*setup_tasks)

            if not exists:
                await websocket.close(code=4004, reason="Conversation not found")
                return

            if not redis_api_keys:
                await websocket.close(code=4006, reason="No API keys found")
                return

            # Accept connection and subscribe to channel
            await websocket.accept()
            self.add_connection(websocket, user_id, conversation_id)
            
            # Subscribe to channel (must be done after pubsub creation)
            await asyncio.to_thread(pubsub.subscribe, channel)

            # Initialize API keys object
            api_keys = APIKeys(
                sambanova_key=redis_api_keys.get("sambanova_key", ""),
                fireworks_key=redis_api_keys.get("fireworks_key", ""),
                serper_key=redis_api_keys.get("serper_key", ""),
                exa_key=redis_api_keys.get("exa_key", "")
            )

            # Initialize agent runtime
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

            # Start background task for Redis messages
            background_task = asyncio.create_task(
                self.handle_redis_messages(websocket, pubsub, user_id, conversation_id)
            )

            # Send connection established message (non-blocking)
            asyncio.create_task(websocket.send_json({
                "event": "connection_established",
                "data": "WebSocket connection established",
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }))

            # Handle incoming WebSocket messages
            while True:
                user_message_text = await websocket.receive_text()
                
                try:
                    user_message_input = json.loads(user_message_text)
                except json.JSONDecodeError:
                    asyncio.create_task(websocket.send_json({
                        "event": "error",
                        "data": "Invalid JSON message format",
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }))
                    continue

                # Create message data once
                message_data = {
                    "event": "user_message", 
                    "data": user_message_input["data"],
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": user_message_input["timestamp"]
                }

                # Launch Redis operations as background tasks
                asyncio.create_task(self._update_metadata(meta_key, user_message_input["data"]))
                asyncio.create_task(asyncio.to_thread(
                    self.redis_client.rpush,
                    message_key,
                    json.dumps(message_data)
                ))

                # Log message receipt (non-blocking)
                logger.info(f"Received message from user: {user_id} in conversation: {conversation_id}")

                # Create and publish user message
                user_message = EndUserMessage(
                    source="User",
                    content=user_message_input["data"], 
                    use_planner=False,
                    provider=user_message_input["provider"],
                    docs=user_message_input["docs"] if "docs" in user_message_input else None
                )    

                # This must be awaited as it affects the conversation flow
                await agent_runtime.publish_message(
                    user_message,
                    DefaultTopicId(type="user_proxy", source=source),
                )

        except WebSocketDisconnect:
            logger.info(f"WebSocket connection closed for conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Exception in WebSocket connection for conversation {conversation_id}: {str(e)}")
        finally:
            # Create cleanup tasks
            cleanup_tasks = []
            
            if background_task is not None:
                background_task.cancel()
                cleanup_tasks.append(background_task)
            
            if pubsub is not None:
                cleanup_tasks.extend([
                    asyncio.create_task(asyncio.to_thread(pubsub.unsubscribe)),
                    asyncio.create_task(asyncio.to_thread(pubsub.close))
                ])
            
            if agent_runtime is not None:
                cleanup_tasks.append(asyncio.create_task(agent_runtime.close()))
            
            # Run all cleanup tasks concurrently and wait for completion
            if cleanup_tasks:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            
            self.remove_connection(user_id, conversation_id)

            if (websocket.client_state != WebSocketState.DISCONNECTED and 
                websocket.application_state != WebSocketState.DISCONNECTED):
                await websocket.close()

    async def _update_metadata(self, meta_key: str, message_data: str):
        """Helper method to update metadata asynchronously"""
        try:
            meta_data = await asyncio.to_thread(self.redis_client.get, meta_key)
            if meta_data:
                metadata = json.loads(meta_data)
                if "name" not in metadata:
                    metadata["name"] = message_data
                    await asyncio.to_thread(
                        self.redis_client.set,
                        meta_key,
                        json.dumps(metadata)
                    )
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")

    async def handle_redis_messages(self, websocket: WebSocket, pubsub, user_id: str, conversation_id: str):
        """
        Background task to handle Redis pub/sub messages and forward them to WebSocket.
        """
        message_key = f"messages:{user_id}:{conversation_id}"
        last_ping_time = 0
        PING_INTERVAL = 15.0  # Increased ping interval to 15 seconds
        BATCH_SIZE = 25  # Increased batch size to process more messages at once
        
        try:
            while True:
                # Process multiple messages in one iteration if available
                messages = []
                for _ in range(BATCH_SIZE):  # Process up to BATCH_SIZE messages at once
                    message = pubsub.get_message(timeout=0.05)  # Reduced timeout
                    if message and message["type"] == "message":
                        messages.append(message)
                    if not message:
                        break

                # Batch process messages
                if messages:
                    message_tasks = []
                    for message in messages:
                        data_str = message["data"]
                        message_data = {
                            "event": "think",
                            "data": data_str,
                            "user_id": user_id,
                            "conversation_id": conversation_id,
                            "timestamp": datetime.now().isoformat()
                        }

                        # Create tasks for Redis operation and WebSocket send
                        message_tasks.extend([
                            asyncio.create_task(asyncio.to_thread(
                                self.redis_client.rpush,
                                message_key,
                                json.dumps(message_data)
                            )),
                            asyncio.create_task(websocket.send_json(message_data))
                        ])

                    # Wait for all message tasks to complete
                    if message_tasks:
                        await asyncio.gather(*message_tasks)

                # Handle ping with rate limiting
                current_time = time.time()
                if current_time - last_ping_time >= PING_INTERVAL:
                    await websocket.send_json({
                        "event": "ping",
                        "data": json.dumps({"type": "ping"}),
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    })
                    last_ping_time = current_time

                # Slightly longer sleep when no messages to reduce CPU usage
                await asyncio.sleep(0.2)

        except Exception as e:
            logger.error(f"Error in Redis message handler: {str(e)}")
            raise
