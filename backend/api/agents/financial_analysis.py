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
from autogen_core.models import LLMMessage, SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agent.financial_analysis.financial_analysis_crew import (
    FinancialAnalysisCrew,
    FinancialAnalysisResult,
)
from services.financial_user_prompt_extractor_service import FinancialPromptExtractor

from ..data_types import (
    AgentRequest,
    AgentStructuredResponse,
    FinancialAnalysis,
    APIKeys,
)
from ..otlp_tracing import logger, format_log_message


@type_subscription(topic_type="financial_analysis")
class FinancialAnalysisAgent(RoutedAgent):
    def __init__(
        self,
        api_keys: APIKeys,
    ) -> None:
        super().__init__("FinancialAnalysisAgent")
        logger.info(format_log_message(None, f"Initializing FinancialAnalysisAgent with ID: {self.id}"))
        self.api_keys = api_keys

    async def execute_financial(
        self, crew: FinancialAnalysisCrew, parameters: Dict[str, Any]
    ):
        logger.info(format_log_message(None, f"Extracting financial information from query: '{parameters.get('query_text', '')[:100]}...'"))
        fextractor = FinancialPromptExtractor(self.api_keys.sambanova_key)
        query_text = parameters.get("query_text", "")
        extracted_ticker, extracted_company = fextractor.extract_info(query_text)

        if not extracted_ticker:
            extracted_ticker = parameters.get("ticker", "")
        if not extracted_company:
            extracted_company = parameters.get("company_name", "")

        if not extracted_ticker:
            extracted_ticker = "AAPL"
        if not extracted_company:
            extracted_company = "Apple Inc"

        logger.info(format_log_message(None, f"Analyzing company: {extracted_company} (ticker: {extracted_ticker})"))
        inputs = {"ticker": extracted_ticker, "company_name": extracted_company}

        if "docs" in parameters:
            inputs["docs"] = parameters["docs"]
            logger.info(format_log_message(None, "Including additional document analysis in financial analysis"))

        # Run the synchronous function in a thread pool
        raw_result = await asyncio.to_thread(crew.execute_financial_analysis, inputs)
        return raw_result

    @message_handler
    async def handle_analysis_request(
        self, message: AgentRequest, ctx: MessageContext
    ) -> None:
        logger.info(format_log_message(
            ctx.topic_id.source,
            "Processing financial analysis request"
        ))
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")

            # Initialize crew
            crew = FinancialAnalysisCrew(
                sambanova_key=self.api_keys.sambanova_key,
                exa_key=self.api_keys.exa_key,
                serper_key=self.api_keys.serper_key,
                user_id=user_id,
                run_id=conversation_id,
                docs_included=False,
                verbose=False
            )

            # Execute analysis
            raw_result = await self.execute_financial(
                crew, message.parameters.model_dump()
            )
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Successfully generated financial analysis"
            ))

            financial_analysis_result = FinancialAnalysisResult.model_validate(
                json.loads(raw_result)
            )
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Successfully parsed financial analysis result"
            ))

        except Exception as e:
            logger.error(format_log_message(
                ctx.topic_id.source,
                f"Failed to process financial analysis request: {str(e)}"
            ), exc_info=True)
            financial_analysis_result = FinancialAnalysisResult()

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=financial_analysis_result,
                message=message.parameters.model_dump_json(),
            )
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Publishing financial analysis to user_proxy"
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
