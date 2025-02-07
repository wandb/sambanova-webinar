import json
from typing import List

from autogen_core import MessageContext
from autogen_core import (
    DefaultTopicId,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_core.models import LLMMessage, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from backend.agent.financial_analysis.financial_analysis_crew import FinancialAnalysisCrew, FinancialAnalysisResult

from ..data_types import (
    AgentStructuredResponse,
    DestinationInfo,
    EndUserMessage,
    GroupChatMessage,
    TravelRequest,
)
from ..otlp_tracing import logger


class FinancialAnalysisAgent(RoutedAgent):
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
    ) -> None:
        super().__init__("FinancialAnalysisAgent")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(
                "You are a helpful AI assistant that helps with financial analysis."
            )
        ]
        self._model_client = model_client

    @message_handler
    async def handle_message(
        self, message: EndUserMessage, ctx: MessageContext
    ) -> None:
        logger.info(
            f"FinancialAnalysisAgent received financial analysis request: EndUserMessage {message.content}"
        )
        try:
            # call the financial analysis crew
            crew = FinancialAnalysisCrew(
                sambanova_key=sambanova_key,
                exa_key=exa_key,
                serper_key=serper_key,
                user_id=user_id,
                run_id=run_id,
                docs_included="docs" in parameters
            )
            raw_result = await self.execute_financial(crew, parameters)
            financial_analysis_result = FinancialAnalysisResult.model_validate(
                json.loads(response_content.content)
            )
        except Exception as e:
            logger.error(f"Failed to parse destination response: {str(e)}")
            financial_analysis_result = FinancialAnalysisResult()

        await self.publish_message(
            AgentStructuredResponse(
                agent_type=self.id.type,
                data=financial_analysis_result,
                message=message.content,
            ),
            DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
        )
