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
        self.api_keys = api_keys

        self._reasoning_model_name = "llama-3.1-70b"
        self._reasoning_model = lambda provider: OpenAIChatCompletionClient(
            model=model_registry.get_model_info(provider=provider, model_key=self._reasoning_model_name)["model"],
            base_url=model_registry.get_model_info(provider=provider, model_key=self._reasoning_model_name)["url"],
            api_key=getattr(api_keys, model_registry.get_api_key_env(provider=provider)),
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )

        self._structure_extraction_model_name = "llama-3.1-70b"
        self._structure_extraction_model = lambda provider: OpenAIChatCompletionClient(
            model=model_registry.get_model_info(provider=provider, model_key=self._structure_extraction_model_name)["model"],
            base_url=model_registry.get_model_info(provider=provider, model_key=self._structure_extraction_model_name)["url"],
            api_key=getattr(api_keys, model_registry.get_api_key_env(provider=provider)),
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )

        self._context_summary_model_name = "llama-3.1-70b"
        self._context_summary_model = lambda provider: OpenAIChatCompletionClient(
            model=model_registry.get_model_info(provider=provider, model_key=self._context_summary_model_name)["model"],
            base_url=model_registry.get_model_info(provider=provider, model_key=self._context_summary_model_name)["url"],
            api_key=getattr(api_keys, model_registry.get_api_key_env(provider=provider)),
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
                "provider": message.provider,
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

        user_id, conversation_id = ctx.topic_id.source.split(":")
        history = self._session_manager.get_history(conversation_id)

        last_content = {}
        if len(history) > 0:
            try:
                last_content = json.loads(history[-1].content)
            except json.JSONDecodeError:
                pass
                
        if "deep_research_question" in last_content:
            logger.info(logger.format_message(
                ctx.topic_id.source,
                "Deep research feedback received, routing to deep research"
            ))
            deep_research_request = AgentRequest(
                agent_type=AgentEnum.DeepResearch,
                parameters=DeepResearch(deep_research_topic=""),
                query=message.content,
                provider=message.provider,
            )
            await self.publish_message(
                deep_research_request, DefaultTopicId(type="deep_research", source=ctx.topic_id.source))
            return


        api_key = getattr(self.api_keys, model_registry.get_api_key_env(message.provider))
        router = QueryRouterService(llm_api_key=api_key, provider=message.provider, websocket=self.websocket, redis_client=self.redis_client, user_id=user_id, conversation_id=conversation_id)

        history = self._session_manager.get_history(conversation_id)

        if len(history) > 0:
            model_response = await self._context_summary_model(message.provider).create(
                list(history)
                + [UserMessage(content="Summarize the messages so far in a few sentences.", source="user")]
            )
            context_summary = model_response.content
        else:
            context_summary = ""

        route_result: QueryType = await router.route_query(message.content, context_summary)

        self._session_manager.add_to_history(
                conversation_id,
                UserMessage(content=message.content, source="user")
        )

        try:
            request_obj = self._create_request(
                route_result.type, route_result.parameters, message
            )
            logger.info(logger.format_message(
                ctx.topic_id.source,
                f"Routing to {request_obj.agent_type.value} agent with parameters: {route_result.parameters}"
            ))
            await self._publish_message(request_obj, ctx)
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
        deep_research_plans = []
        for plan in plans:
            if plan["agent_type"] == AgentEnum.UserProxy:
                user_proxy_plans.append(plan)
            elif plan["agent_type"] == AgentEnum.Assistant:
                assistant_plans.append(plan)
            elif plan["agent_type"] == AgentEnum.DeepResearch:
                deep_research_plans.append(plan)

        if len(user_proxy_plans) > 0:
            return [user_proxy_plans[0]]
        elif len(assistant_plans) > 0:
            return [assistant_plans[0]]
        elif len(deep_research_plans) > 0:
            return [deep_research_plans[0]]
        else:
            return [plans[0]]


    async def _publish_message(
        self, request_obj: AgentRequest, ctx: MessageContext
    ) -> None:
        """
        Publishes a message to the appropriate agent.
        """
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

    async def _get_agents_to_route(
        self, message: EndUserMessage, ctx: MessageContext
    ) -> None:
        """
        Determines which agents to route the message to based on the message content.
        """
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")
            message_key = f"messages:{user_id}:{conversation_id}"

            # Get planner response
            planner_final_response, planner_metadata = await self._get_planner_response(message)

            # Validate planner response
            if not planner_final_response:
                logger.error(logger.format_message(
                    ctx.topic_id.source,
                    "No planner response found"
                ))
                raise ValueError("No planner response found")

            # Prepare message data
            final_message_data = {
                "event": "planner",
                "data": json.dumps({
                    "response": planner_final_response, 
                    "metadata": planner_metadata
                }),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
            }

            # Create tasks for Redis operation and WebSocket send
            tasks = [
                asyncio.create_task(asyncio.to_thread(
                    self.redis_client.rpush,
                    message_key,
                    json.dumps(final_message_data)
                )),
                asyncio.create_task(self.websocket.send_text(json.dumps(final_message_data)))
            ]

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

            # Clean and process response
            cleaned_response = re.sub(
                r"<think>.*?</think>",
                "",
                str(planner_final_response),
                flags=re.DOTALL
            ).strip()

            # Get structured output plan
            feature_extractor_response = await self._structure_extraction_model(message.provider).create(
                [
                    SystemMessage(
                        content=agent_registry.get_strucuted_output_plan_prompt(
                            cleaned_response
                        )
                    )
                ]
            )

            # Process and validate plan
            try:
                plan = json.loads(feature_extractor_response.content)
                plan = plan if isinstance(plan, list) else [plan]
                plan = self._reconcile_plans(plan)

                # Route messages to agents based on plan
                for p in plan:
                    try:
                        request_obj = self._create_request(
                            p["agent_type"], p["parameters"], message
                        )
                        logger.info(logger.format_message(
                            ctx.topic_id.source,
                            f"Publishing request to {request_obj.agent_type.value} with parameters: {request_obj.parameters}"
                        ))
                        await self._publish_message(request_obj, ctx)
                    except Exception as e:
                        logger.error(logger.format_message(
                            ctx.topic_id.source,
                            f"Failed to process plan item {p}: {str(e)}"
                        ))
                        continue

            except Exception as e:
                logger.error(logger.format_message(
                    ctx.topic_id.source,
                    f"Failed to process feature extractor response: {str(e)}"
                ))
                raise

        except Exception as e:
            logger.error(logger.format_message(
                ctx.topic_id.source,
                f"Error in _get_agents_to_route: {str(e)}"
            ))
            # Fallback to assistant agent
            logger.info(logger.format_message(
                ctx.topic_id.source,
                "Falling back to assistant agent"
            ))
            request_obj = AgentRequest(
                provider=message.provider,
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
