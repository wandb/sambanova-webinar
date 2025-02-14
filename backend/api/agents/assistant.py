from datetime import datetime
import functools
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent

from autogen_core import (
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    message_handler,
    type_subscription,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
import requests

from api.data_types import APIKeys, AgentRequest, AgentStructuredResponse, AssistantResponse

from ..otlp_tracing import logger, format_log_message


async def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def serper_search(api_key: str, query: str, num_results: int = 5):
    """Performs a Google search using Serper API and returns the top results."""
    if not api_key:
        raise ValueError("SERPER_API_KEY environment variable is missing.")

    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()

    # Extract relevant search results
    results = []
    for item in data.get("organic", []):
        results.append(
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            }
        )
    return results


@type_subscription(topic_type="assistant")
class AssistantAgentWrapper(RoutedAgent):
    def __init__(self, api_keys: APIKeys) -> None:
        super().__init__("assistant")
        logger.info(format_log_message(None, f"Initializing AssistantAgent with ID: {self.id} and tools: [get_current_time, serper_search]"))
        self.api_keys = api_keys
        self._assistant = AssistantAgent(
            name="assistant",
            model_client=OpenAIChatCompletionClient(
                model="Meta-Llama-3.1-70B-Instruct",
                base_url="https://api.sambanova.ai/v1",
                api_key=self.api_keys.sambanova_key,
                model_info={
                    "json_output": False,
                    "function_calling": True,
                    "family": "unknown",
                    "vision": False,
                },
            ),
            tools=[get_current_time, functools.partial(serper_search, self.api_keys.serper_key)],
            system_message="You are a helpful AI assistant.",
            reflect_on_tool_use=True,
        )

    @message_handler
    async def handle_text_message(
        self, message: AgentRequest, ctx: MessageContext
    ) -> None:
        try:
            logger.info(format_log_message(
                ctx.topic_id.source,
                f"Processing request: '{message.parameters.query[:100]}...'"
            ))
            agent_message = TextMessage(content=message.parameters.query, source="user")
            response = await self._assistant.on_messages([agent_message], ctx.cancellation_token)
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Generated response successfully"
            ))
        except Exception as e:
            logger.error(format_log_message(
                ctx.topic_id.source,
                f"Failed to process request: {str(e)}"
            ), exc_info=True)
            response = AssistantResponse(response="Unable to assist with this request.")

        try:
            # Send response back
            response = AgentStructuredResponse(
                agent_type=self.id.type,
                data=AssistantResponse(response=response.chat_message.content),
                message=message.parameters.model_dump_json(),
            )
            logger.info(format_log_message(
                ctx.topic_id.source,
                "Publishing response to user_proxy"
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
