import asyncio
from datetime import datetime
import json
from collections import deque
import re
import os
import time

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage, CreateResult
from autogen_ext.models.openai import OpenAIChatCompletionClient
from fastapi import WebSocket
import redis

from config.model_registry import model_registry
from services.query_router_service import QueryRouterService, QueryType

from api.data_types import (
    APIKeys,
    AgentRequest,
    AgentStructuredResponse,
    AssistantMessage,
    DeepResearch,
    EndUserMessage,
    HandoffMessage,
    AgentEnum,
)
from api.registry import AgentRegistry
from api.session_state import SessionStateManager
from utils.logging import logger

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
        connection_manager (WebSocketConnectionManager): Manages WebSocket connections.
    """

    def __init__(
        self,
        name: str,
        session_manager: SessionStateManager,
        websocket: WebSocket,
        redis_client: redis.Redis,
        api_keys: APIKeys,
    ) -> None:
        super().__init__("SemanticRouterAgent")
        logger.info(logger.format_message(None, f"Initializing SemanticRouterAgent '{name}' with ID: {self.id}"))
        self._name = name

        reasoning_model_metadata = model_registry.get_model_info(model_key="llama-3.1-70b")
        self._reasoning_model_client = OpenAIChatCompletionClient(
            model=reasoning_model_metadata["model"],
            base_url=reasoning_model_metadata["url"],
            api_key=getattr(api_keys, model_registry.get_api_key_env()),
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )

        structure_extraction_model_metadata = model_registry.get_model_info(model_key="llama-3.1-70b")
        self._structure_extraction_model = OpenAIChatCompletionClient(
            model=structure_extraction_model_metadata["model"],
            base_url=structure_extraction_model_metadata["url"],
            api_key=getattr(api_keys, model_registry.get_api_key_env()),
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )
        self._session_manager = session_manager
        self.websocket = websocket
        self.redis_client = redis_client

    @message_handler
    async def route_message(self, message: EndUserMessage, ctx: MessageContext) -> None:
        """
        Routes user messages to appropriate agents based on conversation context.

        Args:
            message (EndUserMessage): The incoming user message.
            ctx (MessageContext): Context information for the message.
        """
        logger.info(logger.format_message(
            ctx.topic_id.source,
            f"Routing message: '{message.content[:100]}...' (use_planner={message.use_planner})"
        ))
        if message.use_planner:
            await self._get_agents_to_route(message, ctx)
        else:
            await self.route_message_with_query_router(message, ctx)

    def _create_request(
        self, request_type: str, parameters: dict, message: EndUserMessage
    ) -> AgentRequest:
        """
        Creates the appropriate request object based on the request type.

        Args:
            request_type (str): The type of request to create
            parameters (dict): The parameters for the request
            message (EndUserMessage): The original message containing API keys and document IDs

        Returns:
            AgentRequest: The request object for the agent
        """

        agent_type = AgentEnum(request_type)
        # Create AgentRequest using model_validate
        request = AgentRequest.model_validate(
            {
                "agent_type": agent_type,
                "parameters": parameters,
                "document_ids": message.document_ids,
                "query": message.content,
            }
        )

        return request

    async def route_message_with_query_router(
        self, message: EndUserMessage, ctx: MessageContext
    ) -> None:
        """
        Routes user messages to appropriate agents based on conversation context.

        Args:
            message (EndUserMessage): The incoming user message.
            ctx (MessageContext): Context information for the message.
        """
        logger.info(logger.format_message(
            ctx.topic_id.source,
            f"Using query router for message: '{message.content[:100]}...'"
        ))
        router = QueryRouterService(message.api_keys.sambanova_key)
        route_result: QueryType = router.route_query(message.content)

        try:
            request_obj = self._create_request(
                route_result.type, route_result.parameters, message
            )
            logger.info(logger.format_message(
                ctx.topic_id.source,
                f"Routing to {request_obj.agent_type.value} agent with parameters: {route_result.parameters}"
            ))
            await self.publish_message(
                request_obj,
                DefaultTopicId(
                    type=request_obj.agent_type.value,
                    source=ctx.topic_id.source,
                ),
            )
            logger.info(logger.format_message(
                ctx.topic_id.source,
                f"Successfully published request to {request_obj.agent_type.value}"
            ))

        except ValueError as e:
            logger.error(logger.format_message(
                ctx.topic_id.source,
                f"Error processing request: {str(e)}"
            ), exc_info=True)
            return

    def _reconcile_plans(self, plans: list) -> list:
        """
        Reconciles multiple plans into a single plan.
        """
        user_proxy_plans = []
        assistant_plans = []
        for plan in plans:
            if plan["agent_type"] == AgentEnum.UserProxy:
                user_proxy_plans.append(plan)
            elif plan["agent_type"] == AgentEnum.Assistant:
                assistant_plans.append(plan)

        if len(user_proxy_plans) > 0:
            return [user_proxy_plans[0]]
        elif len(assistant_plans) > 0:
            return [assistant_plans[0]]
        else:
            return plans

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
        logger.info(logger.format_message(
            session_id,
            f"Received handoff from {message.source} agent"
        ))

        # Clear session if conversation is complete, otherwise continue routing
        if message.original_task and "complete" in message.content.lower():
            logger.info(logger.format_message(
                session_id,
                "Task complete, clearing session"
            ))
            self._session_manager.clear_session(session_id)
        else:
            logger.info(logger.format_message(
                session_id,
                f"Continuing conversation with new message from {message.source}"
            ))
            await self.route_message(
                EndUserMessage(content=message.content, source=message.source), ctx
            )

    async def _get_agents_to_route(
        self, message: EndUserMessage, ctx: MessageContext
    ) -> None:
        """
        Determines the appropriate agents to route the message to based on context.

        Args:
            message (EndUserMessage): The incoming user message.
        """

        # TODO: remove this when fixed route
        if message.content == "true":
            deep_research_request = AgentRequest(
                agent_type=AgentEnum.DeepResearch,
                parameters=DeepResearch(deep_research_topic=""),
                query=message.content,
            )
            await self.publish_message(
                deep_research_request, DefaultTopicId(type="deep_research", source=ctx.topic_id.source))
            return

        logger.info(logger.format_message(
            ctx.topic_id.source,
            f"Determining agents to route message: '{message.content[:100]}...'"
        ))
        system_message = agent_registry.get_planner_prompt()

        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")

            start_time = time.time()

            history = self._session_manager.get_history(conversation_id)
            planner_response = self._reasoning_model_client.create_stream(
                [SystemMessage(content=system_message, source="system")]
                + list(history)
                + [UserMessage(content=message.content, source="user")],
            )

            self._session_manager.add_to_history(
                conversation_id,
                UserMessage(content=message.content, source="user")
            )

            # Send the chunks through WebSocket if connection exists
            if self.websocket is None:
                logger.error(logger.format_message(
                    ctx.topic_id.source,
                    "No WebSocket connection found"
                ))
                raise ValueError("No WebSocket connection found")


            planner_metadata = {
                "llm_name": self._reasoning_model_client._resolved_model,
                "llm_provider": model_registry.get_current_provider(),
                "task": "planning",
            }   
            planner_event = {
                "event": "planner",
                "data": json.dumps({"metadata": planner_metadata}),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
            }

            await self.websocket.send_text(json.dumps(planner_event))

            planner_final_response = None
            async for chunk in planner_response:
                if isinstance(chunk, str):
                    message_data = {
                        "event": "planner_chunk",
                        "data": json.dumps({"chunk": chunk}),
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                    await self.websocket.send_text(json.dumps(message_data))
                elif isinstance(chunk, CreateResult):
                    planner_final_response = chunk.content
            
            end_time = time.time()
            processing_time = end_time - start_time
            planner_metadata["duration"] = processing_time

            if planner_final_response:
                # Store complete response in Redis
                message_key = f"messages:{user_id}:{conversation_id}"
                final_message_data = {
                    "event": "planner",
                    "data": json.dumps({"response": planner_final_response, "metadata": planner_metadata}),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat(),
                }
                self.redis_client.rpush(message_key, json.dumps(final_message_data))
                await self.websocket.send_text(json.dumps(final_message_data))

                cleaned_response = re.sub(
                    r"<think>.*?</think>",
                    "",
                    (
                        planner_final_response
                        if isinstance(planner_final_response, str)
                        else str(planner_final_response)
                    ),
                    flags=re.DOTALL,
                ).strip()
                feature_extractor_response = await self._structure_extraction_model.create(
                    [
                        SystemMessage(
                            content=agent_registry.get_strucuted_output_plan_prompt(
                                cleaned_response
                            )
                        )
                    ]
                )

                # TODO: add agents working on a set of tasks
                plan = json.loads(feature_extractor_response.content)
                plan = plan if isinstance(plan, list) else [plan]

                # reconcile multiple plans
                plan = self._reconcile_plans(plan)

                for p in plan:
                    try:
                        request_obj = self._create_request(
                            p["agent_type"], p["parameters"], message
                        )
                    except Exception as e:
                        logger.error(
                            logger.format_message(
                                ctx.topic_id.source,
                                f"SemanticRouterAgent failed to parse plan item {p}: {str(e)}"
                            )
                        )
                        continue

                    logger.info(logger.format_message(
                        ctx.topic_id.source,
                        f"Publishing request to {request_obj.agent_type.value} with parameters: {request_obj.parameters}"
                    ))

                    if request_obj.agent_type == AgentEnum.UserProxy:
                        response = AgentStructuredResponse(
                            agent_type=request_obj.agent_type,
                            data=request_obj.parameters,
                            message=request_obj.parameters.model_dump_json(),
                        )
                        await self.publish_message(
                            response,
                            DefaultTopicId(
                                type=request_obj.agent_type.value,
                                source=ctx.topic_id.source,
                            ),
                        )
                    else:
                        await self.publish_message(
                            request_obj,
                            DefaultTopicId(
                                type=request_obj.agent_type.value,
                                source=ctx.topic_id.source,
                            ),
                        )
            else:
                logger.error(logger.format_message(
                    ctx.topic_id.source,
                    "No planner response found"
                ))
                raise ValueError("No planner response found")

        except Exception as e:
            logger.error(
                logger.format_message(
                    ctx.topic_id.source,
                    f"SemanticRouterAgent failed to parse activities response: {str(e)}"
                )
            )
            logger.info(logger.format_message(ctx.topic_id.source, "SemanticRouterAgent defaulting to assistant agent"))
            request_obj = AgentRequest(
                agent_type=AgentEnum.Assistant,
                parameters=AssistantMessage(query=message.content),
                query=message.content,
            )
            await self.publish_message(
                request_obj,
                DefaultTopicId(
                    type=request_obj.agent_type.value,
                    source=ctx.topic_id.source,
                ),
            )
            return
