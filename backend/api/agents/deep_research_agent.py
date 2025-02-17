########## deep_research_agent.py (NEW CODE) ##########
import asyncio
import json
from typing import Any, Union
import uuid

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)

from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

from api.data_types import (
    AgentRequest,
    AgentStructuredResponse,
    APIKeys,
    AgentEnum,
    EducationalContent,
    UserQuestion,
    EndUserMessage,
    DeepResearchReport,
)
from utils.logging import logger
from api.session_state import SessionStateManager

from .open_deep_research.graph import builder

@type_subscription(topic_type="deep_research")
class DeepResearchAgent(RoutedAgent):
    """
    Handles advanced multi-section research with user feedback (interrupt).
    """

    def __init__(self, api_keys: APIKeys):
        super().__init__("DeepResearchAgent")
        self.api_keys = api_keys
        logger.info(
            logger.format_message(
                None, f"Initializing DeepResearchAgent with ID: {self.id}"
            )
        )
        # memory saver per user session
        self.memory_stores = {}
        self._session_threads = {}

    def _get_or_create_memory(self, session_id: str) -> MemorySaver:
        if session_id not in self.memory_stores:
            self.memory_stores[session_id] = MemorySaver()
        return self.memory_stores[session_id]

    def _get_or_create_thread_config(self, session_id: str) -> dict:
        if session_id not in self._session_threads:
            thread_id = str(uuid.uuid4())
            self._session_threads[session_id] = {
                "configurable": {
                    "thread_id": thread_id,
                    # You can also include other config keys here if needed
                    "planner_model": "Meta-Llama-3.3-70B-Instruct",
                    "writer_model": "Meta-Llama-3.1-70B-Instruct",
                    "search_api": "tavily",
                }
            }
        return self._session_threads[session_id]

    @message_handler
    async def handle_deep_research_request(self, message: AgentRequest, ctx: MessageContext) -> None:
        session_id = ctx.topic_id.source
        user_text = message.query.strip()

        # Decide if it's feedback or a brand-new request
        if user_text.lower() == "true":
            graph_input = Command(resume=True)
        elif user_text.lower() == "false":
            graph_input = Command(resume=False)
        elif user_text and (not message.parameters.topic):
            # user typed some text, treat it as feedback
            graph_input = Command(resume=user_text)
        else:
            # brand-new request with the entire user query in topic
            graph_input = {"topic": message.parameters.topic}

        memory = self._get_or_create_memory(session_id)
        graph = builder.compile(checkpointer=memory)
        thread_config = self._get_or_create_thread_config(session_id)

        try:
            async for event in graph.astream(graph_input, thread_config, stream_mode="updates"):
                logger.info(logger.format_message(session_id, f"[DeepResearchFlow Event]: {event}"))
                # if there's an interrupt, we ask user for feedback
                if "__interrupt__" in event:
                    interrupt_data = event["__interrupt__"]
                    if isinstance(interrupt_data, tuple) and interrupt_data:
                        interrupt_msg = interrupt_data[0].value
                        user_question_str = (
                            "The system needs your feedback before continuing:\n\n"
                            f"{interrupt_msg}\n\n"
                            "Type 'true' to approve the plan, or type feedback text to revise it."
                        )
                        response = AgentStructuredResponse(
                            agent_type=AgentEnum.UserProxy,
                            data=UserQuestion(user_question=user_question_str),
                            message=user_question_str
                        )
                        await self.publish_message(
                            response,
                            DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
                        )
                    return

            # If we get here => the flow completed
            final_state = graph.get_state(thread_config, subgraphs=True)
            dr_report = final_state.values.get("deep_research_report", None)
            if dr_report is None:
                logger.warning(logger.format_message(session_id, "No deep_research_report found. Fallback."))
                dr_report = {
                    "sections": [],
                    "final_report": final_state.values.get("final_report", ""),
                }

            structured_report = DeepResearchReport.model_validate(dr_report)
            response = AgentStructuredResponse(
                agent_type=AgentEnum.DeepResearch,
                data=structured_report,
                message="Deep research flow completed."
            )

        except Exception as e:
            logger.error(
                logger.format_message(session_id, f"DeepResearch flow error: {str(e)}"),
                exc_info=True
            )
            # fallback empty
            structured_report = DeepResearchReport(sections=[], final_report="")
            response = AgentStructuredResponse(
                agent_type=AgentEnum.DeepResearch,
                data=structured_report,
                message=f"Deep research flow error: {str(e)}"
            )

        await self.publish_message(
            response,
            DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
        )
