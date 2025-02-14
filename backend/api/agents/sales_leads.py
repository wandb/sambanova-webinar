import asyncio
from typing import Any, Dict
from autogen_core import DefaultTopicId, RoutedAgent, message_handler, type_subscription
from autogen_core import MessageContext
from api.data_types import AgentRequest, AgentStructuredResponse, SalesLeads, APIKeys
from agent.lead_generation_crew import OutreachList, ResearchCrew
from services.user_prompt_extractor_service import UserPromptExtractor

from ..otlp_tracing import logger


@type_subscription(topic_type="sales_leads")
class SalesLeadsAgent(RoutedAgent):
    def __init__(self, api_keys: APIKeys):
        super().__init__("SalesLeadsAgent")
        logger.info(f"Initializing SalesLeadsAgent with ID: {self.id}")
        self.api_keys = api_keys

    @message_handler
    async def handle_sales_leads_request(
        self, message: AgentRequest, ctx: MessageContext
    ) -> None:
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")   
            crew = ResearchCrew(
                sambanova_key=self.api_keys.sambanova_key,
                exa_key=self.api_keys.exa_key,
                user_id=user_id,
                run_id=conversation_id
            )
            parameters_dict = {k: v if v is not None else "" for k, v in message.parameters.model_dump().items()}

            raw_result = await asyncio.to_thread(crew.execute_research, parameters_dict)
            outreach_list = OutreachList.model_validate_json(raw_result)

        except Exception as e:
            logger.error(f"Failed to process sales leads request: {str(e)}", exc_info=True)
            outreach_list = OutreachList()

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=outreach_list,
                message=message.parameters.model_dump_json(),
            )
            logger.info(f"Publishing response to user_proxy: {response}")
            await self.publish_message(
                response,
                DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
            )
        except Exception as e:
            logger.error(f"Failed to publish response: {str(e)}", exc_info=True)


