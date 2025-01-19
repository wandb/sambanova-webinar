# file: services/company_research_service.py

from typing import Optional
import json
from datetime import datetime
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.envutils import EnvUtils
# Import your new tool
from tools.exa_dev_tool import ExaDevTool


class CompanyIntelligenceService:
    def __init__(self):
        """
        Initialize with the ExaDevTool approach for searching.
        """
        self.env_utils = EnvUtils()
        # If you want to do something with the environment, do it here:
        self.exa_api_key = self.env_utils.get_required_env("EXA_API_KEY")

        # Initialize the Exa-based search tool
        self.search_tool = ExaDevTool()

    def get_company_intelligence(
        self,
        industry: Optional[str] = None,
        company_name: Optional[str] = None,
        product: Optional[str] = None,
        company_stage: Optional[str] = None,
        geography: Optional[str] = None,
        funding_stage: Optional[str] = None
    ) -> str:
        """
        Get detailed company intelligence based on provided criteria using Exa.
        Returns a JSON string with 'companies' plus the 'search_criteria'.
        """
        search_query = self._build_search_query(
            industry, company_name, product, company_stage, geography, funding_stage
        )

        # Use the Exa search tool with the user's combined query
        exa_results = self.search_tool.run(
            search_query=search_query,  # required
            search_type="auto",       # or "auto" or "keyword"
            text=True,
            use_autoprompt=True,
            num_results=20,           # Adjust as needed
            summary=True
        )
 

        if "results" not in exa_results:
            # error or empty
            return json.dumps({
                "companies": [],
                "search_criteria": {
                    "industry": industry or "",
                    "company_name": company_name or "",
                    "product": product or "",
                    "company_stage": company_stage or "",
                    "geography": geography or "",
                    "funding_stage": funding_stage or ""
                },
                "total_companies": 0,
                "generated_at": datetime.now().isoformat()
            }, indent=2)

        # Parse Exa results into your "companies" structure
        companies_array = self._parse_exa_results(exa_results["results"])

        output = {
            "companies": companies_array,
            "search_criteria": {
                "industry": industry or "",
                "company_name": company_name or "",
                "product": product or "",
                "company_stage": company_stage or "",
                "geography": geography or "",
                "funding_stage": funding_stage or ""
            },
            "total_companies": len(companies_array),
            "generated_at": datetime.now().isoformat()
        }

        return json.dumps(output, indent=2)

    def _build_search_query(
        self,
        industry: Optional[str],
        company_name: Optional[str],
        product: Optional[str],
        company_stage: Optional[str],
        geography: Optional[str],
        funding_stage: Optional[str]
    ) -> str:
        """
        Combine all user parameters into a single search string for Exa.
        """
        query_parts = []
        if company_name:
            query_parts.append(company_name)
        if product:
            query_parts.append(product)
        if industry:
            query_parts.append(f"{industry} industry")
        if company_stage:
            query_parts.append(f"{company_stage} stage")
        if geography:
            query_parts.append(f"in {geography}")
        if funding_stage:
            query_parts.append(f"{funding_stage} funding")

        # If user gave no data, fallback:
        if not query_parts:
            return "technology companies"

        return " ".join(query_parts)

    def _parse_exa_results(self, results: list) -> list:
        """
        Convert the Exa search results into a list of
        simple 'company' objects:
        { "name", "website", "description", ... }
        """
        companies = []
        for item in results:
            title = item.get("title", "Unknown Company")
            url = item.get("url", "N/A")
            text = item.get("text", "")
            summary = item.get("summary", "")  # <-- here's the summary from Exa

            c = {
                "name": title,
                "website": url,
                # Use summary as the description
                "description": summary,  
                "headquarters": "Unknown, Unknown",
                "employee_count": "Unknown",
                "funding_status": "Unknown",
                "product_list": "",
                "competitor_list": "",
                "founded_year": "Unknown",
                "revenue_range": "Unknown"
            }
            companies.append(c)

        return companies[:15]  # If you only want the top 15

if __name__ == "__main__":
    # Quick test
    svc = CompanyIntelligenceService()
    example_json = svc.get_company_intelligence(
        industry="hardware",
        product="ai",
        geography="bay area",
        company_stage="startup"
    )
    print(example_json)
