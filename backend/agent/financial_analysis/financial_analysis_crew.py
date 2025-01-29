import sys
import os
import json
import uuid
from typing import Dict, Any, List, Optional

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# add parent of parent to sys.path
parent_of_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
if parent_of_parent_dir not in sys.path:
    sys.path.insert(0, parent_of_parent_dir)

from crewai import Agent, Task, Crew, LLM, Process
from utils.agent_thought import RedisConversationLogger
from dotenv import load_dotenv

# Tools
from tools.competitor_llm_tool import CompetitorLLMTool
from tools.competitor_analysis_tool import competitor_analysis_tool
from tools.fundamental_analysis_tool import fundamental_analysis_tool
from tools.technical_analysis_tool import technical_analysis_tool
from tools.risk_assessment_tool import risk_assessment_tool
from tools.yahoo_finance_news_tool_wrapper import yahoo_finance_news_tool
from tools.reddit_discussion_tool import reddit_discussion_tool

load_dotenv()

########## Pydantic Models ##########
from pydantic import BaseModel, Field

class QuarterlyFundamentals(BaseModel):
    date: str
    total_revenue: Optional[float] = None
    net_income: Optional[float] = None

class FundamentalData(BaseModel):
    company_name: str = ""
    sector: str = ""
    industry: str = ""
    market_cap: str = ""
    pe_ratio: str = ""
    forward_pe: str = ""
    peg_ratio: str = ""
    ps_ratio: str = ""
    price_to_book: str = ""
    dividend_yield: str = ""
    beta: str = ""
    year_high: str = Field("", alias="52_week_high")
    year_low: str = Field("", alias="52_week_low")
    analyst_recommendation: str = ""
    target_price: str = ""
    earnings_per_share: str = ""
    profit_margins: str = ""
    operating_margins: str = ""
    ebitda_margins: str = ""
    short_ratio: str = ""
    current_ratio: str = ""
    debt_to_equity: str = ""
    return_on_equity: str = ""
    return_on_assets: str = ""
    revenue_growth: str = ""
    net_income_growth: str = ""
    free_cash_flow: str = ""
    quarterly_fundamentals: List[QuarterlyFundamentals] = []

class TechnicalChartData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class TechnicalData(BaseModel):
    moving_averages: Dict[str, Optional[float]] = {}
    rsi: Optional[float] = None
    macd: Dict[str, Optional[float]] = {}
    bollinger_bands: Dict[str, Optional[float]] = {}
    volatility: Optional[float] = None
    momentum: Optional[float] = None
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    detected_patterns: List[str] = []
    chart_data: List[TechnicalChartData] = []

class RiskDailyReturns(BaseModel):
    date: str
    daily_return: float

class RiskData(BaseModel):
    beta: float
    sharpe_ratio: float
    value_at_risk_95: float
    max_drawdown: float
    volatility: float
    daily_returns: List[RiskDailyReturns] = []

class CompetitorInfo(BaseModel):
    ticker: str
    name: str
    market_cap: str
    pe_ratio: str
    ps_ratio: str
    ebitda_margins: str
    profit_margins: str
    revenue_growth: str
    earnings_growth: str
    short_ratio: str
    industry: str
    sector: str

class CompetitorBlock(BaseModel):
    competitor_tickers: List[str] = []
    competitor_details: List[CompetitorInfo] = []

class NewsItem(BaseModel):
    title: str
    content: str
    link: str
    published_time: str

class YahooNewsData(BaseModel):
    news_items: List[NewsItem]  # because the tool might return a list of dict. We can refine as needed.

class RedditPost(BaseModel):
    title: str
    created_utc: float
    subreddit: str

class RedditData(BaseModel):
    posts: List[RedditPost] = []

class FinancialAnalysisResult(BaseModel):
    ticker: str
    company_name: str
    competitor: CompetitorBlock
    fundamental: FundamentalData
    technical: TechnicalData
    risk: RiskData
    news: YahooNewsData
    reddit: RedditData
    summary: str = ""

#####################################
class FinancialAnalysisCrew:
    """
    Multi-agent pipeline:
      1) competitor_llm (company_name -> competitor tickers)
      2) competitor_analysis (tickers -> competitor fundamentals)
      3) fundamental
      4) technical
      5) risk
      6) news + reddit
      7) aggregator
    """

    def __init__(self, sambanova_key: str, exa_key: str, serper_key: str, user_id: str = "", run_id: str = ""):
        # Example LLM usage
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-8B-Instruct",
            temperature=0.0,
            max_tokens=4096,
            api_key=sambanova_key
        )
        self.sambanova_key = sambanova_key
        self.exa_key = exa_key
        self.serper_key = serper_key
        self.user_id = user_id
        self.run_id = run_id

        self._init_agents()
        self._init_tasks()

    def _init_agents(self):
        # 1) competitor LLM

        comp_llm_tool = CompetitorLLMTool(sambanova_api_key=self.sambanova_key)
        self.competitor_llm_agent = Agent(
            role="Competitor Ticker Finder",
            goal="Given company_name {company_name}, call competitor_llm_tool to get competitor tickers.",
            backstory="You are a financial analyst who is tasked with finding the competitors of a given company. You will be given a company name and you will need to find the competitors of that company. You will use the competitor_llm_tool to get the competitors of the company.",
            llm=self.llm,
            tools=[comp_llm_tool],
            allow_delegation=False,
            verbose=True
        )
        # 2) competitor analysis
        self.competitor_analysis_agent = Agent(
            role="Competitor Analysis Agent",
            goal="Given competitor tickers, retrieve competitor fundamentals. Use competitor_analysis_tool.",
            backstory="You are a financial analyst who is tasked with finding the competitors of a given company. You will be given a company name and you will need to find the competitors of that company. You will use the competitor_analysis_tool to get the fundamentals of the competitors of the company.",
            llm=self.llm,
            tools=[competitor_analysis_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=CompetitorBlock
        )
        # 3) fundamental agent
        self.fundamental_agent = Agent(
            role="Fundamental Analysis Agent",
            goal="Gather advanced fundamentals, returns CSV from fundamental_analysis_tool.",
            backstory="You are a financial analyst who is tasked with gathering advanced fundamentals and returns CSV for a given company. You will be given a company name and you will need to gather the advanced fundamentals and returns CSV for that company. You will use the fundamental_analysis_tool to get the advanced fundamentals and returns CSV for the company.",
            llm=self.llm,
            tools=[fundamental_analysis_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=FundamentalData
        )
        # 4) technical agent
        self.technical_agent = Agent(
            role="Technical Analysis Agent",
            goal="Compute technical indicators, chart_data.",
            backstory="You are a financial analyst who is tasked with computing technical indicators and chart data for a given company. You will be given a company name and you will need to compute the technical indicators and chart data for that company. You will use the technical_analysis_tool to get the technical indicators and chart data for the company.",
            llm=self.llm,
            tools=[technical_analysis_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=TechnicalData
        )
        # 5) risk agent
        self.risk_agent = Agent(
            role="Risk Assessment Agent",
            goal="Compute Beta, Sharpe, VaR, maxDD, daily_returns CSV, etc.",
            backstory="You are a financial analyst who is tasked with computing risk metrics for a given company. You will be given a company name and you will need to compute the risk metrics for that company. You will use the risk_assessment_tool to get the risk metrics for the company.",
            llm=self.llm,
            tools=[risk_assessment_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=RiskData
        )
        # 6) news agent
        self.news_agent = Agent(
            role="Financial News Agent",
            goal="Fetch Yahoo Finance news for a the following ticker:  {ticker}. Use yahoo_finance_news_tool.",
            backstory="You are a financial analyst who is tasked with fetching financial news for a given ticker. You will be given a ticker and you will need to fetch the financial news for that ticker. You will use the yahoo_finance_news_tool to get the financial news for the ticker.",

            llm=self.llm,
            tools=[yahoo_finance_news_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=YahooNewsData
        )
        # aggregator
        self.aggregator_agent = Agent(
            role="Aggregator Agent",
            goal="Combine competitor/fundamental/technical/risk/news/reddit into final JSON of type FinancialAnalysisResult.",
            backstory="You are a financial analyst who is tasked with combining the results from the competitor/fundamental/technical/risk/news/reddit agents into a single JSON of type FinancialAnalysisResult. You will be given the results from the competitor/fundamental/technical/risk/news/reddit agents and you will need to combine them into a single JSON of type FinancialAnalysisResult.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            output_pydantic=FinancialAnalysisResult
        )

        # attach Redis logs
        self.competitor_llm_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "CompLLM")
        self.competitor_analysis_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "CompAnalysis")
        self.fundamental_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "FundAgent")
        self.technical_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "TechAgent")
        self.risk_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "RiskAgent")
        self.news_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "NewsAgent")
        self.aggregator_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Aggregator")

    def _init_tasks(self):
        # 1) competitor_llm_task
        self.competitor_llm_task = Task(
            description="Call competitor_llm_tool(company_name, sambanova_key) => competitor tickers",
            agent=self.competitor_llm_agent,
            expected_output=(
                "[\n"
                "  {\n"
                "    'ticker': 'MSFT',\n"
                "    'company_name': 'Microsoft',\n"
                "    'market_cap': '2.8T',\n"
                "    'industry': 'Technology',\n"
                "    'description': 'Global technology company...',\n"
                "    'products': ['Windows', 'Office 365', 'Azure', 'Xbox'],\n"
                "    'competitors': ['AAPL', 'GOOGL', 'AMZN'],\n"
                "    'revenue': '168.1B',\n"
                "    'revenue_growth': '0.18'\n"
                "  }\n"
                "]"
            ),
            
        )
        # 2) competitor_analysis_task
        self.competitor_analysis_task = Task(
            description="Given the competitor tickers from competitor_llm_task, call competitor_analysis_tool(tickers).",
            agent=self.competitor_analysis_agent,
            context=[self.competitor_llm_task],
            expected_output=(
                "[\n"
                "  '{\n"
                "    'competitor_tickers': ['AAPL', 'GOOGL', 'AMZN'],\n"
                "    'competitor_details': [{'ticker': 'AAPL', 'name': 'Apple', 'market_cap': '2.8T', 'industry': 'Technology', 'description': 'Global technology company...', 'products': ['iPhone', 'iPad', 'Mac', 'Apple Watch', 'Apple TV'], 'revenue': '168.1B', 'revenue_growth': '0.18'}]\n"
                "  }\n"
                "]"
            )
        )
        # 3) fundamental_task
        self.fundamental_task = Task(
            description="Call fundamental_analysis_tool(ticker).",
            agent=self.fundamental_agent,
            expected_output=(
                "{\n"
                "  'company_name': 'Apple',\n"
                "  'sector': 'Technology',\n"
                "  'industry': 'Consumer Electronics',\n"
                "  'market_cap': '2.8T',\n"
                "  'pe_ratio': '25.0',\n"
                "  'forward_pe': '20.0',\n"
                "  ...\n"
                "}"
            )
        )
        # 4) technical_task
        self.technical_task = Task(
            description="Call technical_analysis_tool(ticker).",
            agent=self.technical_agent,
            expected_output=(
                "{\n"
                "  'moving_averages': {'50': 150.0, '200': 140.0},\n"
                "  'rsi': 70.0,\n"
                "  'macd': {'12': 1.0, '26': 0.5},\n"
                "  ...\n"
                "}"
            )
        )
        # 5) risk_task
        self.risk_task = Task(
            description="Call risk_assessment_tool(ticker).",
            agent=self.risk_agent,
            expected_output=(
                "{\n"
                "  'beta': 1.2,\n"
                "  'sharpe_ratio': 0.5,\n"
                "  'value_at_risk_95': 1.5,\n"
                "  'max_drawdown': 20.0,\n"
                "  ...\n"
                "}"
            )
        )
        # 6) news_task
        self.news_task = Task(
            description="Call yahoo_finance_news_tool with {ticker} as inputs.",
            agent=self.news_agent,
            expected_output=(
                "News items: [{'title': 'Apple Q4 2024 Earnings', 'link': 'https://finance.yahoo.com/news/apple-q4-2024-earnings-100000000.html', 'published_time': '2024-01-25 10:00:00'}]"
                
            )
        )
        # 7) aggregator_task
        self.aggregator_task = Task(
            description=(
                "Combine partial results from competitor_analysis_task, fundamental_task, "
                "technical_task, risk_task, news_task into a single JSON matching FinancialAnalysisResult. "
                "Ticker = original ticker. Company_name = original. competitor -> competitor_tickers[], competitor_details[]. "
                "Then fundamental, technical, risk, news, reddit. Provide a 'summary' bullet point."
            ),
            agent=self.aggregator_agent,
            context=[self.competitor_analysis_task, self.fundamental_task, self.technical_task, self.risk_task, self.news_task],
            expected_output=(
                #insert expected output here of FinancialAnalysisResult in use all fields by name
                "{\n"
                "  'ticker': 'AAPL',\n"
                "  'company_name': 'Apple',\n"
                "  'competitor': 'competitor_tickers': ['AAPL', 'GOOGL', 'AMZN'],\n"
                "    'competitor_details': [{'ticker': 'AAPL', 'name': 'Apple', 'market_cap': '2.8T', 'industry': 'Technology', 'description': 'Global technology company...', 'products': ['iPhone', 'iPad', 'Mac', 'Apple Watch', 'Apple TV'], 'revenue': '168.1B', 'revenue_growth': '0.18'}]\n"
                "  },\n"
                "  'fundamental': {'company_name': 'Apple',\n"
                "    'sector': 'Technology',\n"
                "    'industry': 'Consumer Electronics',\n"
                "    'market_cap': '2.8T',\n"
                "    'pe_ratio': '25.0',\n"
                "    ...\n"
                "  },\n"
                "  'technical': {'moving_averages': {'50': 150.0, '200': 140.0},\n"
                "    'rsi': 70.0,\n"
                "    'macd': {'12': 1.0, '26': 0.5},\n"
                "    ...\n"
                "  },\n"
                "  'risk': {'beta': 1.2,\n"
                "    'sharpe_ratio': 0.5,\n"
                "    'value_at_risk_95': 1.5,\n"
                "    'max_drawdown': 20.0,\n"
                "    ...\n"
                "  },\n"
                "  'news': {'news_items': [{'title': 'Apple Q4 2024 Earnings', 'link': 'https://finance.yahoo.com/news/apple-q4-2024-earnings-100000000.html', 'published_time': '2024-01-25 10:00:00'}]\n"
                "    'reddit_posts': [{'title': 'Apple Q4 2024 Earnings', 'created_utc': 1716768000, 'subreddit': 'apple'}]\n"
                "  },\n"
                "  'summary': '...'\n"
                "}"
            )
        )

    def execute_financial_analysis(self, inputs: Dict[str, Any]) -> str:
        """
        Full pipeline:
          competitor tasks -> parallel fundamental/technical/risk/news -> aggregator
        Expects inputs: {"ticker":"AAPL","company_name":"Apple"}
        """
        # We'll do competitor tasks in sequence, then fundamental/technical/risk/news in parallel, aggregator last
        # That means the crew tasks order: competitor_llm_task, competitor_analysis_task, 
        # then (fundamental_task, technical_task, risk_task, news_task) parallel,
        # aggregator_task last in sequence.

        crew = Crew(
            agents=[
                self.competitor_llm_agent,
                self.competitor_analysis_agent,
                self.fundamental_agent,
                self.technical_agent,
                self.risk_agent,
                self.news_agent,
                self.aggregator_agent
            ],
            tasks=[
                self.competitor_llm_task,
                self.competitor_analysis_task,
                # parallel stage
                self.fundamental_task,
                self.technical_task,
                  self.risk_task, 
                  self.news_task,
                # aggregator last
                self.aggregator_task
            ],
            process=Process.sequential,
            verbose=True
        )
        final = crew.kickoff(inputs=inputs)
        return final.pydantic.model_dump_json()

def main():
    example_samba_key = "4957c8f9-2468-4cbd-9899-7ba15bd046b4"
    exa_key = "f2f5b5bf-84da-472f-8711-088dfbe9e04c"
    serper_key = "fa053a785d306bc110c0dd657d220b1825338f67"
    user_id = "demo_user"
    run_id = str(uuid.uuid4())

    # Example usage:
    # Suppose user prompt gave us ticker/company
    inputs = {
        "ticker": "NVDA",
        "company_name": "NVIDIA"
    }

    fac = FinancialAnalysisCrew(
        sambanova_key=example_samba_key,
        exa_key=exa_key,
        serper_key=serper_key,
        user_id=user_id,
        run_id=run_id
    )
    result_json = fac.execute_financial_analysis(inputs)
    print("FINAL FINANCIAL ANALYSIS JSON:")
    print(result_json)


if __name__=="__main__":
    main()
