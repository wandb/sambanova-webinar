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

from agent.financial_analysis.financial_analysis_crew import FinancialAnalysisCrew, FinancialAnalysisResult
from services.financial_user_prompt_extractor_service import FinancialPromptExtractor

from ..data_types import (
    AgentRequest,
    AgentStructuredResponse,
    FinancialAnalysis,
)
from ..otlp_tracing import logger

@type_subscription(topic_type="financial_analysis")
class FinancialAnalysisAgent(RoutedAgent):
    def __init__(
        self,  
    ) -> None:
        super().__init__("FinancialAnalysisAgent")
        logger.info(f"Initializing FinancialAnalysisAgent with ID: {self.id}")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(content="You are a helpful AI assistant that helps with financial analysis.")
        ]

    async def execute_financial(self, crew: FinancialAnalysisCrew, sambanova_key: str, parameters: Dict[str,Any]):
        fextractor = FinancialPromptExtractor(sambanova_key)
        query_text = parameters.get("query_text","")
        extracted_ticker, extracted_company = fextractor.extract_info(query_text)

        if not extracted_ticker:
            extracted_ticker = parameters.get("ticker","")
        if not extracted_company:
            extracted_company = parameters.get("company_name","")

        if not extracted_ticker:
            extracted_ticker = "AAPL"
        if not extracted_company:
            extracted_company = "Apple Inc"

        inputs = {"ticker": extracted_ticker, "company_name": extracted_company}

        if "docs" in parameters:
            inputs["docs"] = parameters["docs"]

        # Run the synchronous function in a thread pool
        raw_result = await asyncio.to_thread(crew.execute_financial_analysis, inputs)
        return raw_result
    
    @message_handler
    async def handle_analysis_request(
        self, message: AgentRequest, ctx: MessageContext
    ) -> None:
        logger.info(f"FinancialAnalysisAgent received request: {message}")
        try:
            user_id, conversation_id = ctx.topic_id.source.split(":")

            # Initialize crew
            crew = FinancialAnalysisCrew(
                sambanova_key=message.api_keys.sambanova_key,
                exa_key=message.api_keys.exa_key,
                serper_key=message.api_keys.serper_key,
                user_id=user_id,
                run_id=conversation_id,
                docs_included=False 
            )

            # Execute analysis
            raw_result = await self.execute_financial(crew, message.api_keys.sambanova_key, message.parameters.model_dump())
            logger.info(f"Received raw result: {raw_result}")
            
            financial_analysis_result = FinancialAnalysisResult.model_validate(json.loads(raw_result))
            logger.info("Successfully parsed financial analysis result")

        except Exception as e:
            logger.error(f"Failed to process financial analysis request: {str(e)}", exc_info=True)
            financial_analysis_result = FinancialAnalysisResult()

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=financial_analysis_result,
                message=message.parameters.model_dump_json(),
            )
            logger.info(f"Publishing response to user_proxy: {response}")
            await self.publish_message(
                response,
                DefaultTopicId(type="user_proxy", source=ctx.topic_id.source),
            )
        except Exception as e:
            logger.error(f"Failed to publish response: {str(e)}", exc_info=True)
