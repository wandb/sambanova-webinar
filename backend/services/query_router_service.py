from typing import Dict, Any
import json
import requests
from pydantic import BaseModel

class QueryType(BaseModel):
    # Possible types: "sales_leads", "educational_content", or "financial_analysis"
    type: str
    parameters: Dict[str, Any]

class QueryRouterService:
    def __init__(self, sambanova_key: str):
        self.sambanova_key = sambanova_key
        self.api_url = "https://api.sambanova.ai/v1/chat/completions"
        
        # Expanded / refined keywords for educational content (including some "report", "compare", etc.)
        self.edu_keywords = [
            "explain", "guide", "learn", "teach", "understand", "what is",
            "how does", "tutorial", "course", "education", "training",
            "concepts", "fundamentals", "basics", "advanced", "intermediate",
            "beginner", "introduction", "deep dive", "overview", "study",
            "technology", "architecture", "design", "implementation",
            "comparison", "compare", "comparing", "performance", "methodology",
            "framework", "system", "protocol", "algorithm", "mechanism",
            "theory", "principle", "structure", "process",
            # Newly added cues for research/educational style requests:
            "report", "tell me about", "describe", "differences", "similarities"
        ]
        
        # Sales leads keywords
        self.sales_keywords = [
            "find", "search", "companies", "startups", "leads", "vendors",
            "identify", "discover", "list", "funding", "funded", "investors",
            "market research", "competitors", "industry", "geography",
            "series", "seed", "venture", "investment", "firm", "corporation",
            "business", "enterprise", "provider", "supplier", "manufacturer"
        ]

        # Financial keywords - removing generic “analysis” to avoid over-triggering
        self.financial_keywords = [
            "stock",
            "fundamental analysis", 
            "technical analysis", 
            "price target", 
            "investment strategy", 
            "ticker",
            "financial analysis",
            "ratios", 
            "eps", 
            "balance sheet", 
            "income statement",
            "market cap",
            "valuation"
        ]

        # Additional phrases for override
        self.override_phrases = [
            "fundamental analysis",
            "technical analysis",
            "fundamental & technical analysis"
        ]

        # A small set of known big company names to help push "analysis" queries to financial
        self.known_big_companies = [
            "google", "amazon", "apple", "tesla", "microsoft", "netflix",
            "meta", "alphabet", "nvidia", "amd", "intel"
        ]
        # Tickers for some known big companies
        self.known_tickers = [
            "goog", "googl", "amzn", "aapl", "tsla", "msft",
            "nflx", "meta", "nvda", "amd", "intc"
        ]

    def _detect_query_type(self, query: str) -> str:
        """
        Score-based approach for edu, sales, finance, with special handling for 
        'analysis' or 'analyze' + big-company/ticker or explicit finance terms.
        """
        query_lower = query.lower()

        # 1) If user explicitly says "fundamental analysis" or "technical analysis" => finance
        if "fundamental analysis" in query_lower or "technical analysis" in query_lower:
            return "financial_analysis"

        # 2) Tally normal keywords (but remove "analysis" from direct financial scoring)
        edu_score = sum(1 for keyword in self.edu_keywords if keyword in query_lower)
        sales_score = sum(1 for keyword in self.sales_keywords if keyword in query_lower)
        fin_score = sum(1 for keyword in self.financial_keywords if keyword in query_lower)

        # 3) Special logic for the words 'analysis' or 'analyze' 
        #    => check if they appear alongside strong finance signals
        if ("analysis" in query_lower or "analyze" in query_lower):
            # If user also mentions known big cos, tickers, or finance words like 'stock'
            # or explicit finance terms, treat as finance:
            if any(big_co in query_lower for big_co in self.known_big_companies + self.known_tickers):
                fin_score += 5  # strongly finance
            elif any(x in query_lower for x in ["stock", "price target", "investment strategy"]):
                fin_score += 5  # strongly finance
            # If none of these appear, do NOT boost finance

        # 4) Decide based on highest score
        if fin_score > edu_score and fin_score > sales_score:
            return "financial_analysis"
        if edu_score >= sales_score:
            return "educational_content"
        return "sales_leads"

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """
        Make an API call to SambaNova's LLM, returning raw string content.
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
        """Return a default structured JSON string based on the detected type."""
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
        # else, fallback => sales
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
        """Normalize educational content parameters with safe defaults."""
        focus_areas = params.get("focus_areas", [])
        if isinstance(focus_areas, str):
            focus_areas = [area.strip() for area in focus_areas.split(",")]
        elif not focus_areas:
            focus_areas = ["key concepts", "practical applications"]

        valid_levels = ["beginner", "intermediate", "advanced"]
        audience_level = params.get("audience_level", "intermediate").lower()
        if audience_level not in valid_levels:
            audience_level = "intermediate"

        return {
            "topic": params.get("topic", ""),
            "audience_level": audience_level,
            "focus_areas": focus_areas
        }

    def _normalize_sales_params(self, params: Dict) -> Dict:
        """Normalize sales leads parameters with safe defaults."""
        return {
            "industry": params.get("industry", ""),
            "company_stage": params.get("company_stage", ""),
            "geography": params.get("geography", ""),
            "funding_stage": params.get("funding_stage", ""),
            "product": params.get("product", "")
        }

    def _normalize_financial_params(self, params: Dict) -> Dict:
        """Normalize financial analysis parameters with safe defaults."""
        return {
            "query_text": params.get("query_text",""),
            "ticker": params.get("ticker",""),
            "company_name": params.get("company_name","")
        }

    def _final_override(self, user_query: str, chosen_type: str) -> str:
        """
        If user query explicitly mentions certain override phrases 
        (like 'fundamental analysis' or 'technical analysis'),
        we force 'financial_analysis'.
        """
        qlower = user_query.lower()

        for phrase in self.override_phrases:
            if phrase in qlower:
                return "financial_analysis"

        return chosen_type

    def route_query(self, query: str) -> QueryType:
        """
        Main routing method:
          1) Detect type using _detect_query_type
          2) Call LLM with few-shot system prompt
          3) Parse or fall back to a default if LLM fails
          4) Normalize parameters
          5) Final override check
        """
        detected_type = self._detect_query_type(query)
        
        system_message = f"""
        You are a query routing expert that categorizes queries and extracts structured information.
        Always return a valid JSON object with 'type' and 'parameters'.

        We have three possible types: 'sales_leads', 'educational_content', or 'financial_analysis'.

        Rules:
        1. For 'educational_content':
           - Extract the FULL topic from the query
           - Do NOT truncate or summarize the topic
           - If multiple concepts are present, keep them in 'topic'
        2. For 'sales_leads': 
           - Extract specific industry, location, or other business parameters if any
        3. For 'financial_analysis': 
           - Provide 'query_text' (the user’s full finance question)
           - Provide 'ticker' if recognized
           - Provide 'company_name' if recognized

        Examples:

        Query: "Dark Matter, Black Holes and Quantum Physics"
        {{
          "type": "educational_content",
          "parameters": {{
            "topic": "Dark Matter, Black Holes and Quantum Physics",
            "audience_level": "intermediate",
            "focus_areas": ["key concepts", "theoretical foundations", "current research"]
          }}
        }}

        Query: "Explain the relationship between quantum entanglement and teleportation"
        {{
          "type": "educational_content",
          "parameters": {{
            "topic": "relationship between quantum entanglement and teleportation",
            "audience_level": "intermediate",
            "focus_areas": ["key concepts", "theoretical principles", "practical applications"]
          }}
        }}

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

        Query: "Explain how memory bandwidth impacts GPU performance"
        {{
          "type": "educational_content",
          "parameters": {{
            "topic": "memory bandwidth impacts GPU performance",
            "audience_level": "intermediate",
            "focus_areas": ["key concepts", "practical applications"]
          }}
        }}

        Query: "Analyze Google"
        {{
          "type": "financial_analysis",
          "parameters": {{
            "query_text": "Analyze Google",
            "ticker": "GOOGL",
            "company_name": "Google"
          }}
        }}

        Query: "Perform a fundamental analysis on Tesla stock"
        {{
          "type": "financial_analysis",
          "parameters": {{
            "query_text": "Perform a fundamental analysis on Tesla stock",
            "ticker": "TSLA",
            "company_name": "Tesla"
          }}
        }}

        Query: "Ai chip companies based in geneva"
        {{
          "type": "sales_leads",
          "parameters": {{
            "industry": "AI chip",
            "company_stage": "",
            "geography": "Geneva",
            "funding_stage": "",
            "product": ""
          }}
        }}

        Query: "Quantum computing and qubits"
        {{
          "type": "educational_content",
          "parameters": {{
            "topic": "Quantum computing and qubits",
            "audience_level": "intermediate",
            "focus_areas": ["foundational principles", "recent advances"]
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

            # Param normalization
            if parsed_result["type"] == "educational_content":
                parsed_result["parameters"] = self._normalize_educational_params(
                    parsed_result.get("parameters", {})
                )
            elif parsed_result["type"] == "financial_analysis":
                parsed_result["parameters"] = self._normalize_financial_params(
                    parsed_result.get("parameters", {})
                )
            else:
                parsed_result["parameters"] = self._normalize_sales_params(
                    parsed_result.get("parameters", {})
                )

            # Final override check
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
