from typing import Dict, Any, List
import json
import requests
from pydantic import BaseModel

class QueryType(BaseModel):
    type: str  # "sales_leads" or "educational_content"
    parameters: Dict[str, Any]

class QueryRouterService:
    def __init__(self, sambanova_key: str):
        self.sambanova_key = sambanova_key
        self.api_url = "https://api.sambanova.ai/v1/chat/completions"
        
        # Keywords that suggest educational content
        self.edu_keywords = [
            "explain", "guide", "learn", "teach", "understand", "what is",
            "how does", "tutorial", "course", "education", "training",
            "concepts", "fundamentals", "basics", "advanced", "intermediate",
            "beginner", "introduction", "deep dive", "overview", "study"
        ]
        
        # Keywords that suggest sales leads
        self.sales_keywords = [
            "find", "search", "companies", "startups", "leads", "research",
            "identify", "discover", "list", "funding", "funded", "investors",
            "market research", "competitors", "industry", "geography",
            "series", "seed", "venture", "investment"
        ]

    def _detect_query_type(self, query: str) -> str:
        """
        Pre-check query type based on keywords before LLM call
        """
        query_lower = query.lower()
        edu_score = sum(1 for keyword in self.edu_keywords if keyword in query_lower)
        sales_score = sum(1 for keyword in self.sales_keywords if keyword in query_lower)
        
        return "educational_content" if edu_score > sales_score else "sales_leads"

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """
        Make an API call to SambaNova's LLM.
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
        """Return a default structured response based on detected type"""
        if detected_type == "educational_content":
            return json.dumps({
                "type": "educational_content",
                "parameters": {
                    "topic": "",
                    "audience_level": "intermediate",
                    "focus_areas": ["key concepts", "practical applications"]
                }
            })
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
        """Normalize educational content parameters with defaults"""
        # Handle focus areas
        focus_areas = params.get("focus_areas", [])
        if isinstance(focus_areas, str):
            focus_areas = [area.strip() for area in focus_areas.split(",")]
        elif not focus_areas:
            focus_areas = ["key concepts", "practical applications"]

        # Validate and default audience_level
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
        """Normalize sales leads parameters with defaults"""
        return {
            "industry": params.get("industry", ""),
            "company_stage": params.get("company_stage", ""),
            "geography": params.get("geography", ""),
            "funding_stage": params.get("funding_stage", ""),
            "product": params.get("product", "")
        }
    
    def route_query(self, query: str) -> QueryType:
        """
        Route the query to appropriate endpoint using LLM with few-shot examples.
        """
        detected_type = self._detect_query_type(query)
        
        system_message = """
        You are a query routing expert that categorizes queries and extracts structured information.
        You must ALWAYS return a valid JSON object with 'type' and 'parameters'.
        
        Examples:
        
        Query: "Find AI startups in Boston"
        {
            "type": "sales_leads",
            "parameters": {
                "industry": "AI",
                "company_stage": "startup",
                "geography": "Boston",
                "funding_stage": "",
                "product": ""
            }
        }
        
        Query: "Explain quantum computing for beginners"
        {
            "type": "educational_content",
            "parameters": {
                "topic": "quantum computing",
                "audience_level": "beginner",
                "focus_areas": ["basic principles", "quantum bits", "quantum gates"]
            }
        }
        
        Query: "Create an advanced guide about blockchain"
        {
            "type": "educational_content",
            "parameters": {
                "topic": "blockchain",
                "audience_level": "advanced",
                "focus_areas": ["consensus mechanisms", "cryptography", "distributed systems"]
            }
        }
        
        Query: "Research Series B cybersecurity companies in Israel"
        {
            "type": "sales_leads",
            "parameters": {
                "industry": "cybersecurity",
                "company_stage": "",
                "geography": "Israel",
                "funding_stage": "Series B",
                "product": ""
            }
        }
        """

        user_message = f"""
        Query: "{query}"
        
        Based on the examples above, categorize this query and extract relevant parameters.
        Initial type detection suggests: {detected_type}
        
        Return ONLY a JSON object with the same structure as the examples.
        """

        try:
            result = self._call_llm(system_message, user_message)
            parsed_result = json.loads(result)
            
            # Use keyword detection as fallback
            if "type" not in parsed_result:
                parsed_result["type"] = detected_type
            
            # Normalize parameters based on type
            if parsed_result["type"] == "educational_content":
                parsed_result["parameters"] = self._normalize_educational_params(parsed_result.get("parameters", {}))
            else:
                parsed_result["parameters"] = self._normalize_sales_params(parsed_result.get("parameters", {}))
                
            return QueryType(**parsed_result)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return QueryType(**json.loads(self._get_default_response(detected_type))) 
