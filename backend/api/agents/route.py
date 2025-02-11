import asyncio
import json
from collections import deque

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agent.lead_generation_crew import ResearchCrew
from api.websocket_manager import WebSocketConnectionManager
from services.query_router_service import QueryRouterService, QueryType

from api.data_types import (
    EducationalContentRequest,
    EndUserMessage,
    CoPilotPlan,
    FinancialAnalysisRequest,
    HandoffMessage,
    SalesLeadsRequest,
)
from api.otlp_tracing import logger
from api.registry import AgentRegistry
from api.session_state import SessionStateManager

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

    connection_manager: WebSocketConnectionManager = None  # Will be set by LeadGenerationAPI

    def __init__(
        self,
        name: str,
        session_manager: SessionStateManager,
    ) -> None:
        super().__init__("SemanticRouterAgent")
        logger.info(f"Initializing SemanticRouterAgent with ID: {self.id}")
        self._name = name
        self._reasoning_model_client = lambda sambanova_key: OpenAIChatCompletionClient(
            model="DeepSeek-R1-Distill-Llama-70B",
            base_url="https://api.sambanova.ai/v1",
            api_key=sambanova_key,
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )
        self._structure_extraction_model = lambda sambanova_key: OpenAIChatCompletionClient(
            model="Meta-Llama-3.1-70B-Instruct",
            base_url="https://api.sambanova.ai/v1",
            api_key=sambanova_key,
            model_info={
                "json_output": False,
                "function_calling": True,
                "family": "unknown",
                "vision": False,
            },
        )
        self._session_manager = session_manager

    @message_handler
    async def route_message(self, message: EndUserMessage, ctx: MessageContext) -> None:
        """
        Routes user messages to appropriate agents based on conversation context.

        Args:
            message (EndUserMessage): The incoming user message.
            ctx (MessageContext): Context information for the message.
        """
        if message.use_planner:
            conversation_id = ctx.topic_id.source

            # Add the current message to session history
            self._session_manager.add_to_history(conversation_id, message)

            # Analyze conversation history for better context
            history = self._session_manager.get_history(conversation_id)
            travel_plan: CoPilotPlan = await self._get_agents_to_route(message, ctx, history)
        else:
            await self.route_message_with_query_router(message, ctx)


    async def route_message_with_query_router(self, message: EndUserMessage, ctx: MessageContext) -> None:
        """
        Routes user messages to appropriate agents based on conversation context.

        Args:
            message (EndUserMessage): The incoming user message.
            ctx (MessageContext): Context information for the message.
        """

        conversation_id = ctx.topic_id.source

        router = QueryRouterService(message.api_keys.sambanova_key)

        route_result: QueryType = router.route_query(message.content)

        if route_result.type == "financial_analysis":
            logger.info(f"Publishing financial analysis request with parameters: {route_result.parameters}")
            financial_analysis_request = FinancialAnalysisRequest(
                ticker=route_result.parameters.get("ticker", ""),
                company_name=route_result.parameters.get("company_name", ""),
                query_text=message.content,
                api_keys=message.api_keys,
                document_ids=message.document_ids
            )
            await self.publish_message(
                financial_analysis_request,
                DefaultTopicId(type="financial_analysis", source=conversation_id),
            )
            logger.info("Financial analysis request published")
            return
        elif route_result.type == "educational_content":
            logger.info(f"Publishing research request with parameters: {route_result.parameters}")
            research_request = EducationalContentRequest(
                topic=route_result.parameters.get("topic", ""),
                audience_level=route_result.parameters.get("audience_level", "intermediate"),
                focus_areas=route_result.parameters.get("focus_areas", None),
                api_keys=message.api_keys,
                document_ids=message.document_ids
            )
            await self.publish_message(
                research_request,
                DefaultTopicId(type="educational_content", source=conversation_id),
            )
            logger.info("Educational content request published")
            return
        elif route_result.type == "sales_leads":
            sales_leads_request = SalesLeadsRequest(
                industry=route_result.parameters.get("industry", ""),
                company_stage=route_result.parameters.get("company_stage", ""),
                geography=route_result.parameters.get("geography", ""),
                funding_stage=route_result.parameters.get("funding_stage", ""),
                product=route_result.parameters.get("product", ""),
                api_keys=message.api_keys
            )
            await self.publish_message(
                sales_leads_request,
                DefaultTopicId(type="sales_leads", source=conversation_id),
            )
            logger.info("Sales leads request published")
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
        self, message: EndUserMessage, ctx: MessageContext, history: deque
    ) -> CoPilotPlan:
        """
        Determines the appropriate agents to route the message to based on context.

        Args:
            message (EndUserMessage): The incoming user message.
            history (deque): The history of messages in the session.

        Returns:
            CoPilotPlan: A plan indicating which agents should handle the subtasks.
        """
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
            reasoning_model_client = self._reasoning_model_client(message.api_keys.sambanova_key)
            feature_extractor_model = self._structure_extraction_model(message.api_keys.sambanova_key)
            user_id, conversation_id = ctx.topic_id.source.split(":")
            
            # Get the WebSocket connection from the connection manager
            websocket = self.connection_manager.get_connection(
                user_id, 
                conversation_id
            )

            planner_response = await reasoning_model_client.create([SystemMessage(content=system_message)])  
                
            # Send the chunk through WebSocket if connection exists
            if websocket:
                await websocket.send_text(json.dumps({
                    "event": "think",
                    "data": planner_response.content,
                    "user_id": user_id,
                    "conversation_id": conversation_id
                }))
                await asyncio.sleep(0.25)
            system_message = lambda query: f"""
You are a query routing expert that categorizes queries and extracts structured information.
Always return a valid JSON object with 'type' and 'parameters'.

We have three possible types: 'sales_leads', 'educational_content', or 'financial_analysis' or 'default_agent'.

Rules:
1. For 'educational_content':
    - Extract the FULL topic from the query
    - Do NOT truncate or summarize the topic
    - If multiple concepts are present, keep them in 'topic'
2. For 'sales_leads': 
    - Extract specific industry, location, or other business parameters if any
3. For 'financial_analysis': 
    - Provide 'query_text' (the user’s full finance question)
    - Provide 'ticker' if recognized
    - Provide 'company_name' if recognized
4. For 'default_agent':
    - If the query is not about finance, education, or sales leads, return 'default_agent'

Examples:

Query: "What is the capital of France?"
[
    {{
        "type": "default_agent",
        "parameters": {{
        "query": "What is the capital of France?"
        }}
    }}
]

Query: "Dark Matter, Black Holes and Quantum Physics"
[
    {{
        "type": "educational_content",
        "parameters": {{
        "topic": "Dark Matter, Black Holes and Quantum Physics",
        "audience_level": "intermediate",
        "focus_areas": ["key concepts", "theoretical foundations", "current research"]
        }}
    }}
]

Query: "Explain the relationship between quantum entanglement and teleportation"
[
    {{
        "type": "educational_content",
        "parameters": {{
        "topic": "relationship between quantum entanglement and teleportation",
        "audience_level": "intermediate",
        "focus_areas": ["key concepts", "theoretical principles", "practical applications"]
        }}
    }}
]

Query: "Find AI startups in Boston"
[
    {{
        "type": "sales_leads",
        "parameters": {{
        "industry": "AI",
        "company_stage": "startup",
        "geography": "Boston",
        "funding_stage": "",
        "product": ""
        }}
    }}
]

Query: "Explain how memory bandwidth impacts GPU performance"
[
    {{
        "type": "educational_content",
        "parameters": {{
        "topic": "memory bandwidth impacts GPU performance",
        "audience_level": "intermediate",
        "focus_areas": ["key concepts", "practical applications"]
        }}
    }}
]

Query: "Analyze Google"
[
    {{
        "type": "financial_analysis",
        "parameters": {{
        "query_text": "Analyze Google",
        "ticker": "GOOGL",
        "company_name": "Google"
        }}
    }}
]

Query: "Perform a fundamental analysis on Tesla stock"
[
    {{
        "type": "financial_analysis",
        "parameters": {{
        "query_text": "Perform a fundamental analysis on Tesla stock",
        "ticker": "TSLA",
        "company_name": "Tesla"
        }}
    }}
]

Query: "Ai chip companies based in geneva"
[
    {{
        "type": "sales_leads",
        "parameters": {{
        "industry": "AI chip",
        "company_stage": "",
        "geography": "Geneva",
        "funding_stage": "",
        "product": ""
        }}
    }}
]

Query: "Quantum computing and qubits"
[
    {{
        "type": "educational_content",
        "parameters": {{
        "topic": "Quantum computing and qubits",
        "audience_level": "intermediate",
        "focus_areas": ["foundational principles", "recent advances"]
        }}
    }}
]

User query: "{query}"

Return ONLY JSON with 'type' and 'parameters'.
Ensure the final output does not include any code block markers like ```json or ```python.
        """
        
            feature_extractor_response = await feature_extractor_model.create([SystemMessage(content=system_message(planner_response.content))])

            # TODO: better way to execute multiple tasks
            plan = json.loads(feature_extractor_response.content)
            plan = plan if isinstance(plan, list) else [plan]
            for p in plan:
                if p["type"] == "financial_analysis":
                        financial_analysis_request = FinancialAnalysisRequest(
                            ticker=p["parameters"]["ticker"],
                            company_name=p["parameters"]["company_name"],
                            query_text=p["parameters"]["query_text"],
                            api_keys=message.api_keys,
                            document_ids=message.document_ids
                        )
                        await self.publish_message(
                            financial_analysis_request,
                            DefaultTopicId(type="financial_analysis", source=ctx.topic_id.source),
                        )



        except Exception as e:
            logger.error(f"Failed to parse activities response: {str(e)}")
            return
