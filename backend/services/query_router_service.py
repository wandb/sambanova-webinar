from typing import Dict, Any, List
import json
import requests
from pydantic import BaseModel

class QueryType(BaseModel):
    # Now can be: "sales_leads", "educational_content", or "financial_analysis"
    type: str
    parameters: Dict[str, Any]

class QueryRouterService:
    def __init__(self, sambanova_key: str):
        self.sambanova_key = sambanova_key
        self.api_url = "https://api.sambanova.ai/v1/chat/completions"
        
        # Keywords that suggest educational content - expanded
        self.edu_keywords = [
            "explain", "guide", "learn", "teach", "understand", "what is",
            "how does", "tutorial", "course", "education", "training",
            "concepts", "fundamentals", "basics", "advanced", "intermediate",
            "beginner", "introduction", "deep dive", "overview", "study",
            # Additional research/technical
            "technology", "architecture", "design", "implementation",
            "analysis", "comparison", "performance", "methodology",
            "framework", "system", "protocol", "algorithm", "mechanism",
            "theory", "principle", "structure", "process"
        ]
        
        # Keywords that suggest sales leads - made more specific
        self.sales_keywords = [
            "find", "search", "companies", "startups", "leads", "vendors",
            "identify", "discover", "list", "funding", "funded", "investors",
            "market research", "competitors", "industry", "geography",
            "series", "seed", "venture", "investment", "firm", "corporation",
            "business", "enterprise", "provider", "supplier", "manufacturer"
        ]

        # Financial-specific keywords/phrases
        self.financial_keywords = [
            "stock", 
            "technical analysis", 
            "fundamental analysis", 
            "price target", 
            "investment strategy", 
            "ticker",
            "financial analysis",
            "ratios", 
            "eps", 
            "balance sheet", 
            "income statement",
            "analysis of a stock",
            "analyzing a stock",
            # you can add more synonyms
        ]

        # Additional phrases for override
        self.override_phrases = [
            "fundamental and technical analysis",
            "fundamental & technical analysis"
        ]

    def _detect_query_type(self, query: str) -> str:
        """
        Pre-check query type based on keywords before LLM call,
        including financial keywords for 'financial_analysis'.
        """
        query_lower = query.lower()
        edu_score = sum(1 for keyword in self.edu_keywords if keyword in query_lower)
        sales_score = sum(1 for keyword in self.sales_keywords if keyword in query_lower)
        fin_score = sum(1 for keyword in self.financial_keywords if keyword in query_lower)
        
        # If financial keywords predominate, route to financial_analysis
        if fin_score > edu_score and fin_score > sales_score:
            return "financial_analysis"

        # Otherwise keep your original approach
        return "educational_content" if edu_score >= sales_score else "sales_leads"

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """
        Make an API call to SambaNova's LLM (same logic you had).
        """
        headers = {
            "Authorization": f"Bearer {self.sambanova_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "Meta-Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.01,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            json_response = response.json()
            
            if "choices" not in json_response or len(json_response["choices"]) == 0:
                return self._get_default_response(self._detect_query_type(user_message))

            content = json_response["choices"][0]["message"]["content"].strip()
            return content.replace("```json", "").replace("```", "").strip()
            
        except Exception as e:
            print(f"Error calling LLM: {str(e)}")
            return self._get_default_response(self._detect_query_type(user_message))

    def _get_default_response(self, detected_type: str) -> str:
        """Return a default structured response based on detected type, also handling financial_analysis."""
        if detected_type == "educational_content":
            return json.dumps({
                "type": "educational_content",
                "parameters": {
                    "topic": "",
                    "audience_level": "intermediate",
                    "focus_areas": ["key concepts", "practical applications"]
                }
            })
        elif detected_type == "financial_analysis":
            return json.dumps({
                "type": "financial_analysis",
                "parameters": {
                    "query_text": "",
                    "ticker": "",
                    "company_name": ""
                }
            })
        # else fallback is sales_leads
        return json.dumps({
            "type": "sales_leads",
            "parameters": {
                "industry": "",
                "company_stage": "",
                "geography": "",
                "funding_stage": "",
                "product": ""
            }
        })

    def _normalize_educational_params(self, params: Dict) -> Dict:
        """Normalize educational content parameters with defaults."""
        focus_areas = params.get("focus_areas", [])
        if isinstance(focus_areas, str):
            focus_areas = [area.strip() for area in focus_areas.split(",")]
        elif not focus_areas:
            focus_areas = ["key concepts", "practical applications"]

        valid_levels = ["beginner", "intermediate", "advanced"]
        audience_level = params.get("audience_level","intermediate").lower()
        if audience_level not in valid_levels:
            audience_level = "intermediate"

        return {
            "topic": params.get("topic",""),
            "audience_level": audience_level,
            "focus_areas": focus_areas
        }

    def _normalize_sales_params(self, params: Dict) -> Dict:
        """Normalize sales leads parameters with defaults."""
        return {
            "industry": params.get("industry", ""),
            "company_stage": params.get("company_stage", ""),
            "geography": params.get("geography", ""),
            "funding_stage": params.get("funding_stage", ""),
            "product": params.get("product", "")
        }

    def _normalize_financial_params(self, params: Dict) -> Dict:
        """Normalize financial analysis parameters with defaults."""
        return {
            "query_text": params.get("query_text",""),
            "ticker": params.get("ticker",""),
            "company_name": params.get("company_name","")
        }

    def _final_override(self, user_query: str, chosen_type: str) -> str:
        """
        If user query explicitly mentions 'technical analysis' or 'fundamental analysis',
        or certain override phrases, we force 'financial_analysis'.
        This ensures queries like 'Could you do fundamental and technical analysis on Tesla?'
        won't route to educational_content.
        """
        qlower = user_query.lower()

        # If user typed both "fundamental" and "analysis", or "technical" and "analysis",
        # or special override phrases, force financial.
        if "fundamental analysis" in qlower or "technical analysis" in qlower:
            return "financial_analysis"

        # Check for combined phrase like "fundamental and technical analysis" etc.
        for phrase in self.override_phrases:
            if phrase in qlower:
                return "financial_analysis"

        return chosen_type

    def route_query(self, query: str) -> QueryType:
        """
        Our main routing method with LLM. 
        We do:
          1) initial detection with _detect_query_type
          2) call LLM with a few-shot system prompt
          3) parse/normalize
          4) final override if we see certain phrases in user query
        """
        detected_type = self._detect_query_type(query)
        
        system_message = f"""
        You are a query routing expert that categorizes queries and extracts structured information.
        You must ALWAYS return a valid JSON object with 'type' and 'parameters'.

        We have three possible types: 'sales_leads', 'educational_content', or 'financial_analysis'.

        Important rules:
        1. If a query is purely about a technical topic or concept without business context, treat as 'educational_content'.
        2. Only categorize as 'sales_leads' if there's a clear intention to find companies, products, or business leads.
        3. If user is talking about stock analysis, risk metrics, price targets, or fundamental/technical financial details, route to 'financial_analysis'.

        Examples:

        Query: "Find AI startups in Boston"
        {{
          "type": "sales_leads",
          "parameters": {{
            "industry": "AI",
            "company_stage": "startup",
            "geography": "Boston",
            "funding_stage": "",
            "product": ""
          }}
        }}

        Query: "High Bandwidth Memory and SRAM"
        {{
          "type": "educational_content",
          "parameters": {{
            "topic": "High Bandwidth Memory and SRAM technologies",
            "audience_level": "intermediate",
            "focus_areas": ["architecture comparison", "performance characteristics", "implementation details"]
          }}
        }}

        Query: "Perform a fundamental analysis on Apple"
        {{
          "type": "financial_analysis",
          "parameters": {{
            "query_text": "Perform a fundamental analysis on Apple",
            "ticker": "",
            "company_name": ""
          }}
        }}

        User query: "{query}"
        Initial type detection suggests: {detected_type}

        Return ONLY JSON with 'type' and 'parameters'.
        """

        user_message = "Please classify and extract parameters."

        try:
            llm_result_str = self._call_llm(system_message, user_message)
            parsed_result = json.loads(llm_result_str)

            # If LLM didn't provide "type", fallback
            if "type" not in parsed_result:
                parsed_result["type"] = detected_type

            # Now do final param normalization
            if parsed_result["type"] == "educational_content":
                parsed_result["parameters"] = self._normalize_educational_params(
                    parsed_result.get("parameters", {})
                )
            elif parsed_result["type"] == "financial_analysis":
                parsed_result["parameters"] = self._normalize_financial_params(
                    parsed_result.get("parameters", {})
                )
            else:
                # default to sales_leads
                parsed_result["parameters"] = self._normalize_sales_params(
                    parsed_result.get("parameters", {})
                )

            # final override check
            final_type = self._final_override(query, parsed_result["type"])
            parsed_result["type"] = final_type

            return QueryType(**parsed_result)
            
        except json.JSONDecodeError as e:
            print(f"[route_query] JSON decode error: {str(e)}")
            # fallback if LLM fails
            fallback_json = self._get_default_response(detected_type)
            fallback_dict = json.loads(fallback_json)
            # also final override
            fallback_dict["type"] = self._final_override(query, fallback_dict["type"])
            return QueryType(**fallback_dict)
