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

from agent.samba_research_flow.crews.edu_research.edu_research_crew import EducationalPlan
from agent.samba_research_flow.samba_research_flow import SambaResearchFlow

from ..data_types import (
    AgentRequest,
    AgentStructuredResponse,
    EducationalPlanResult,
    APIKeys,
)
from ..otlp_tracing import logger, format_log_message

@type_subscription(topic_type="educational_content")
class EducationalContentAgent(RoutedAgent):
    def __init__(self, api_keys: APIKeys):
        super().__init__("EducationalContentAgent")
        logger.info(format_log_message(None, f"Initializing EducationalContentAgent with ID: {self.id}"))
        self.api_keys = api_keys

    @message_handler
    async def handle_educational_content_request(self, message: AgentRequest, ctx: MessageContext) -> None:
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")
            logger.info(format_log_message(
                ctx.topic_id.source,
                f"Processing educational content request for topic: '{message.parameters.topic}'"
            ))
            
            edu_flow = SambaResearchFlow(
                    sambanova_key=self.api_keys.sambanova_key,
                    serper_key=self.api_keys.serper_key,
                    user_id=user_id,
                    run_id=conversation_id,
                    docs_included=False,
                    verbose=False
                )
            edu_inputs = {
                "topic": message.parameters.topic,
                "audience_level": message.parameters.audience_level if message.parameters.audience_level else "",
                "additional_context": message.parameters.focus_areas if message.parameters.focus_areas else ""
            }
            logger.info(format_log_message(
                ctx.topic_id.source,
                f"Starting educational content flow with inputs: {edu_inputs}"
            ))
            edu_flow.input_variables = edu_inputs
            result = await asyncio.to_thread(edu_flow.kickoff, edu_inputs)

            logger.info(format_log_message(
                ctx.topic_id.source,
                "Successfully generated educational content"
            ))
            sections_with_content = EducationalPlanResult.model_validate({"sections": result})
            
        except Exception as e:
            logger.error(format_log_message(
                ctx.topic_id.source,
                f"Failed to process educational content request: {str(e)}"
            ), exc_info=True)
            sections_with_content = EducationalPlanResult()

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=sections_with_content,
                message=message.parameters.model_dump_json(),
            )
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Publishing educational content to user_proxy"
            ))
            await self.publish_message(
                response,
                DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
            )
        except Exception as e:
            logger.error(format_log_message(
                ctx.topic_id.source,
                f"Failed to publish response: {str(e)}"
            ), exc_info=True)
