# file: tools/exa_dev_tool.py

import os
import json
import requests
from typing import Any, Type, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ExaDevToolSchema(BaseModel):
    """Schema for using the ExaDevTool with raw requests."""
    search_query: str = Field(
        ...,
        description="Search query for Exa semantic search."
    )
    search_type: str = Field(
        default="auto",
        description="Search type: 'auto', 'neural', 'keyword', etc."
    )
    category: str = Field(
        default="company",
        description="Search category, e.g. 'company', 'news', etc."
    )
    num_results: int = Field(
        default=20,
        description="Number of search results to retrieve."
    )
    text: bool = Field(
        default=True,
        description="Whether to retrieve the 'text' field from Exa search."
    )
    summary: bool = Field(
        default=True,
        description="Whether to retrieve the 'summary' field from Exa."
    )
    livecrawl: str = Field(
        default="always",
        description="Set to 'always' if you want the most up-to-date content."
    )


class ExaDevTool(BaseTool):
    """
    A tool that leverages Exa's search endpoint via raw HTTP POST.
    Includes the summary field in the results.
    """
    name: str = "Exa Search Tool"
    description: str = (
        "Use Exa to perform semantic search via raw HTTP POST. "
        "Returns structured JSON with title, url, text, summary, etc."
    )
    args_schema: Type[BaseModel] = ExaDevToolSchema

    def _run(self, **kwargs: Any) -> Any:
        """
        Perform a POST to https://api.exa.ai/search using the provided parameters,
        parse the JSON, and return it.
        """
        # 1. Collect arguments
        search_query = kwargs.get("search_query")
        search_type = kwargs.get("search_type", "auto")
        category = kwargs.get("category", "company")
        num_results = kwargs.get("num_results", 20)
        text = kwargs.get("text", True)
        summary = kwargs.get("summary", True)
        livecrawl = kwargs.get("livecrawl", "always")
        
        # 2. Build JSON payload
        payload = {
            "query": search_query,
            "type": search_type,
            "category": category,
            "numResults": num_results,
            "contents": {
                "text": text,
                "highlights": {},
                "summary": summary,
                "livecrawl": livecrawl
            }
        }

        # 3. Get API key from environment
        exa_api_key = os.environ.get("EXA_API_KEY", "")
        if not exa_api_key:
            raise ValueError("EXA_API_KEY not found in environment variables.")

        # 4. Build headers
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": exa_api_key
        }

        # 5. Make the POST request
        url = "https://api.exa.ai/search"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": f"Exa search request failed: {e}"}

        # 6. Parse JSON response
        try:
            json_response = response.json()
            return json_response
        except json.JSONDecodeError:
            return {"error": "Could not decode JSON from Exa response."}
