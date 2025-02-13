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
)
from ..otlp_tracing import logger

@type_subscription(topic_type="educational_content")
class EducationalContentAgent(RoutedAgent):
    def __init__(self):
        super().__init__("EducationalContentAgent")

    @message_handler
    async def handle_educational_content_request(self, message: AgentRequest, ctx: MessageContext) -> None:
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")
            edu_flow = SambaResearchFlow(
                    sambanova_key=message.api_keys.sambanova_key,
                    serper_key=message.api_keys.serper_key,
                    user_id=user_id,
                    run_id=conversation_id,
                    docs_included=False
                )
            edu_inputs = {
                "topic": message.parameters.topic,
                "audience_level": message.parameters.audience_level if message.parameters.audience_level else "",
                "additional_context": message.parameters.focus_areas if message.parameters.focus_areas else ""
            }
            edu_flow.input_variables = edu_inputs
            result = await asyncio.to_thread(edu_flow.kickoff, edu_inputs)

            logger.info(f"Educational content flow result: {result}")

            sections_with_content = EducationalPlanResult.model_validate({"sections": result})
        except Exception as e:
            logger.error(f"Failed to process educational content request: {str(e)}", exc_info=True)
            sections_with_content = EducationalPlanResult()

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=sections_with_content,
                message=message.parameters.model_dump_json(),
            )
            logger.info(f"Publishing response to user_proxy: {response}")
            await self.publish_message(
                response,
                DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
            )
        except Exception as e:
            logger.error(f"Failed to publish response: {str(e)}", exc_info=True)
