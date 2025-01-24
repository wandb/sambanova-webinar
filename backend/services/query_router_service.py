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
        
        # Keywords that suggest educational content - expanded
        self.edu_keywords = [
            "explain", "guide", "learn", "teach", "understand", "what is",
            "how does", "tutorial", "course", "education", "training",
            "concepts", "fundamentals", "basics", "advanced", "intermediate",
            "beginner", "introduction", "deep dive", "overview", "study",
            # Added research/technical keywords
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

    def _detect_query_type(self, query: str) -> str:
        """
        Pre-check query type based on keywords before LLM call
        """
        query_lower = query.lower()
        edu_score = sum(1 for keyword in self.edu_keywords if keyword in query_lower)
        sales_score = sum(1 for keyword in self.sales_keywords if keyword in query_lower)
        
        # Bias towards educational content when scores are equal or no keywords found
        return "educational_content" if edu_score >= sales_score else "sales_leads"

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
        
        Important rules:
        1. If a query is purely about a technical topic or concept without company/business context, treat it as educational_content
        2. Only categorize as sales_leads if there's a clear intention to find companies, products, or business opportunities
        
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
        
        Query: "High Bandwidth Memory and SRAM"
        {
            "type": "educational_content",
            "parameters": {
                "topic": "High Bandwidth Memory and SRAM technologies",
                "audience_level": "intermediate",
                "focus_areas": ["architecture comparison", "performance characteristics", "implementation details"]
            }
        }
        
        Query: "Quantum Computing Architecture"
        {
            "type": "educational_content",
            "parameters": {
                "topic": "Quantum Computing Architecture",
                "audience_level": "intermediate",
                "focus_areas": ["system design", "quantum principles", "hardware implementation"]
            }
        }
        
        Query: "RISC-V processor manufacturers in Asia"
        {
            "type": "sales_leads",
            "parameters": {
                "industry": "semiconductor",
                "company_stage": "",
                "geography": "Asia",
                "funding_stage": "",
                "product": "RISC-V processors"
            }
        }
        
        Query: "Neural Network Accelerators"
        {
            "type": "educational_content",
            "parameters": {
                "topic": "Neural Network Accelerators",
                "audience_level": "intermediate",
                "focus_areas": ["hardware architecture", "optimization techniques", "performance analysis"]
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
