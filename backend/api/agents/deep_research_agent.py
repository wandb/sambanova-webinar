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
from langchain_core.runnables import RunnableConfig

from api.data_types import (
    AgentRequest,
    AgentStructuredResponse,
    EducationalPlanResult,
    APIKeys,
    AgentEnum,
    EducationalContent,
    UserQuestion,
    EndUserMessage
)
from utils.logging import logger
from api.session_state import SessionStateManager

# The main LangGraph builder we have:
from .open_deep_research.graph import builder
from .open_deep_research.configuration import Configuration

@type_subscription(topic_type="deep_research")
class DeepResearchAgent(RoutedAgent):
    """
    Handles advanced research with multi-step planning + user feedback (interrupt).
    If user provides "true" => Command(resume=True).
    If user provides text => Command(resume="that text").
    """

    def __init__(self, api_keys: APIKeys, session_manager: SessionStateManager):
        super().__init__("DeepResearchAgent")
        self.api_keys = api_keys
        self.session_manager = session_manager
        logger.info(
            logger.format_message(
                None, f"Initializing DeepResearchAgent with ID: {self.id}"
            )
        )
        # One MemorySaver per user session. 
        self.memory_stores = {}

        # We'll keep a simple dictionary of config states by session
        self._session_threads = {}

    def _get_or_create_memory(self, session_id: str) -> MemorySaver:
        if session_id not in self.memory_stores:
            self.memory_stores[session_id] = MemorySaver()
        return self.memory_stores[session_id]

    def _get_or_create_thread_config(self, session_id: str) -> dict:
        """
        Each session gets a unique 'thread_id' we pass to the graph so it can checkpoint state.
        """
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
        """
        Called whenever the router decides to route to 'deep_research'.
        We'll examine the parameters to see if it's a brand new request 
        or user feedback (interrupt resume).
        """
        session_id = ctx.topic_id.source

        # 1) Are we dealing with brand new request (i.e. user wants a new topic)
        #    or a "resume" scenario where the user typed 'true' or some feedback?
        # We'll check if the user actually typed "true" or something else in 
        # the original message's text. 
        # Because your code uses 'parameters.topic' for new queries,
        # and if it's an interrupt feedback, we see that typically as: 
        #   "parameters": <some string or user question>
        # So let's see how your route code calls us.
        # We'll do something simpler: we also get the original user text from message.query
        user_text = message.query.strip()

        # We'll see if that user text is "true" or if it's something else
        is_feedback = False
        if user_text.lower() == "true":
            is_feedback = True
            graph_input = Command(resume=True)
        elif user_text.lower() == "false":
            # You could do something else here (maybe cancel?), but let's skip
            is_feedback = True
            graph_input = Command(resume=False)
        # If the user text is anything else (non-empty), we treat it as feedback
        elif user_text and (not message.parameters.topic):
            is_feedback = True
            graph_input = Command(resume=user_text)
        else:
            # brand-new request
            # meaning the entire user query is in parameters.topic
            # or at least that is the design from QueryRouterService
            is_feedback = False
            the_topic = message.parameters.topic
            graph_input = {"topic": the_topic}

        # 2) Get the memory saver for this user
        memory = self._get_or_create_memory(session_id)
        # 3) Compile the builder with that memory store
        graph = builder.compile(checkpointer=memory)

        # 4) Get the existing or new config for this session
        thread_config = self._get_or_create_thread_config(session_id)

        # 5) Now run the graph in streaming mode
        #    Because of the 'interrupt' node, if the graph wants feedback,
        #    it’ll yield an event with "__interrupt__" key. We catch that & ask user for input.

        try:
            async for event in graph.astream(graph_input, thread_config, stream_mode="updates"):
                logger.info(logger.format_message(session_id, f"[DeepResearchFlow Event]: {event}"))
                # If the graph triggers an interrupt => ask the user 
                if "__interrupt__" in event:
                    interrupt_data = event["__interrupt__"]
                    if isinstance(interrupt_data, tuple) and interrupt_data:
                        interrupt_msg = interrupt_data[0].value
                        # We pass that as a question to user
                        # “Please provide feedback or pass 'true' to continue”
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
                        # Publish to the user
                        await self.publish_message(
                            response,
                            DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
                        )
                    return  # We stop here, waiting for user feedback

            # If we exhaust the loop => the graph is done
            final_state = graph.get_state(thread_config, subgraphs=True)
            final_report = final_state.values.get("final_report", "")

            # Build our structured output
            sections_out = EducationalPlanResult.model_validate({
                "sections": [
                    {
                        "name": "DeepResearch Final",
                        "description": "Full advanced research result",
                        "research": False,
                        "content": "",
                        "generated_content": final_report
                    }
                ]
            })
            response = AgentStructuredResponse(
                agent_type=AgentEnum.DeepResearch,
                data=sections_out,
                message=f"Deep research flow completed with topic: {final_report[:80]}..."
            )

        except Exception as e:
            logger.error(logger.format_message(session_id, f"DeepResearch flow error: {str(e)}"), exc_info=True)
            sections_out = EducationalPlanResult(sections=[])
            response = AgentStructuredResponse(
                agent_type=AgentEnum.DeepResearch,
                data=sections_out,
                message=f"Deep research flow error: {str(e)}"
            )

        # 6) Return or publish final. If not interrupted or error, we got here
        await self.publish_message(
            response,
            DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
        )
