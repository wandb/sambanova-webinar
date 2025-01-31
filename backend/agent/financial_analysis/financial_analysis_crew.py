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
from tools.technical_analysis_tool import yf_tech_analysis
from tools.risk_assessment_tool import risk_assessment_tool
from tools.yahoo_finance_news_tool_wrapper import yahoo_news_tool
from tools.reddit_discussion_tool import reddit_discussion_tool
from crewai_tools import SerperDevTool

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
    named_entities: List[str] = []

class YahooNewsData(BaseModel):
    news_items: List[NewsItem]

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
    risk: RiskData
    comprehensive_summary: str = ""

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
        self.aggregator_llm = LLM(
            model="sambanova/Qwen2.5-72B-Instruct",
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
            goal="Identify and analyze 3 primary competitors for the target company using market intelligence and financial metrics",
            backstory="Expert in competitive analysis and market research, specializing in identifying key market players and their relative positioning within their industry sectors.",
            llm=self.llm,
            tools=[comp_llm_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=CompetitorBlock
        )

        # 2) competitor analysis
        self.competitor_analysis_agent = Agent(
            role="Competitor Analysis Agent",
            goal="Perform detailed comparative analysis of identified competitors' key financial and operational metrics",
            backstory="Financial analyst specializing in comparative company analysis, with expertise in evaluating competitive advantages and market positioning through quantitative metrics.",
            llm=self.llm,
            tools=[competitor_analysis_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=CompetitorInfo
        )

        # 3) fundamental agent
        self.fundamental_agent = Agent(
            role="Fundamental Analysis Agent",
            goal="Analyze company fundamentals through key financial ratios, growth metrics, and operational efficiency indicators of stock {ticker}",
            backstory="Senior financial analyst with expertise in fundamental analysis, specializing in evaluating company financial health and growth prospects through comprehensive metric analysis.",
            llm=self.llm,
            tools=[fundamental_analysis_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=FundamentalData
        )

        # 4) technical agent
        self.technical_agent = Agent(
            role="Technical Analysis Agent",
            goal="Evaluate price patterns, momentum indicators, and market trends through technical analysis",
            backstory="Technical analysis specialist with deep expertise in chart patterns, technical indicators, and trend analysis for market timing and price movement prediction.",
            llm=self.llm,
            tools=[yf_tech_analysis],
            allow_delegation=False,
            verbose=True,
        )

        # 5) risk agent
        self.risk_agent = Agent(
            role="Risk Assessment Agent",
            goal="Evaluate investment risks through quantitative risk metrics and market exposure analysis",
            backstory="Risk management specialist focusing on quantitative risk assessment, market volatility analysis, and portfolio risk metrics calculation.",
            llm=self.llm,
            tools=[risk_assessment_tool],
            allow_delegation=False,
            verbose=True,
            output_pydantic=RiskData
        )

        # 6) news agent
        # Temporarily set serper key in environment for this tool instance
        os.environ["SERPER_API_KEY"] = self.serper_key
        tool = SerperDevTool()

        self.news_agent = Agent(
            role="Financial News Agent",
            goal="Gather and analyze recent news, market sentiment, and media coverage affecting the ticker {ticker}",
            backstory="Market intelligence  specialist with 15 years experience focusing on news analysis, sentiment evaluation, and media impact assessment on company performance. You MUST reference the news exhaustively in the summary and name any events including named entities ie companies, people, etc that may affect the stock price and other metrics",
            llm=self.llm,
            tools=[SerperDevTool()],
            allow_delegation=False,
            verbose=True,
            #output_pydantic=YahooNewsData
        )

        # aggregator
        self.aggregator_agent = Agent(
            role="Aggregator Agent",
            goal="Synthesize all analysis components into a comprehensive financial assessment",
            backstory="Senior financial advisor with 15 years of experience specializing in comprehensive market analysis, competitor analysis, fundamental analysis, technical analysis, risk analysis, and news analysis, combining multiple analytical perspectives into actionable investment insights. You MUST reference the news exhaustively in the summary and name any events including named entities ie companies, people, etc that may affect the stock price and other metrics",
            llm=self.aggregator_llm,
            allow_delegation=False,
            verbose=True,
            output_pydantic=FinancialAnalysisResult
        )

        # attach Redis logs
        self.competitor_llm_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "CompLLM")
        self.competitor_analysis_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "CompAnalysis")
        self.fundamental_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "FundAgent")
        #self.technical_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "TechAgent")
        self.risk_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "RiskAgent")
        self.news_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "NewsAgent")
        self.aggregator_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Aggregator")

    def _init_tasks(self):
        # 1) competitor_llm_task
        self.competitor_llm_task = Task(
            description="Identify and analyze 3 key competitors for the follwing company using market intelligence: Company Ticker: {ticker}",
            agent=self.competitor_llm_agent,
            expected_output="List of 3 tickers of competitors closest to the target company in the same industry, if they aren't close enough try to find a competitor that is close enough",
        )

        # 2) competitor_analysis_task
        self.competitor_analysis_task = Task(
            description="Perform detailed comparative analysis of identified competitors using financial and operational metrics pass in the tickers from the competitor_llm_task as a list of strings",
            
            agent=self.competitor_analysis_agent,
            context=[self.competitor_llm_task],
            expected_output="Expected fields: competitor_tickers[], competitor_details[]{ticker, name, market_cap, industry, sector, pe_ratio, ps_ratio, ebitda_margins, profit_margins, revenue_growth, earnings_growth}"
        )

        # 3) fundamental_task
        self.fundamental_task = Task(
            description="Analyze company fundamentals through comprehensive financial metrics and ratios for the following company: Company Ticker: {ticker}. Pass in this ticker to the fundamental_analysis_tool as a string",
            agent=self.fundamental_agent,
            expected_output="Expected fields: company_name, sector, industry, market_cap, pe_ratio, forward_pe, peg_ratio, ps_ratio, price_to_book, dividend_yield, beta, quarterly_fundamentals",
            async_execution=True
        )

        # 4) technical_task
        self.technical_task = Task(
            description=(
            "Perform technical analysis on {ticker}. Include:\n"
            "1. 50-day and 200-day moving averages (1 year).\n"
            "2. Key support and resistance levels (3 each).\n"
            "3. RSI and MACD indicators.\n"
            "4. Volume analysis (3 months).\n"
            "5. Significant chart patterns (6 months).\n"
            "6. Fibonacci retracement levels.\n"
            "7. Comparison with sector's average.\n"
            "Use the yf_tech_analysis tool for data. Pass in the ticker as a string to the tool as well as the period as a string ie '1y'"
        ),
            agent=self.technical_agent,
            expected_output="Expected fields: moving_averages, rsi, macd, bollinger_bands, volatility, momentum, support_levels, resistance_levels, detected_patterns, chart_data",
            output_pydantic=TechnicalData
        )

        # 5) risk_task
        self.risk_task = Task(
            description="Calculate and analyze key risk metrics and market exposure indicators for the following company: Company Ticker: {ticker}. Pass in this ticker to the risk_assessment_tool as a string and period as a string ie '1y' and benchmark as a string ie '^GSPC' for the S&P 500",
            agent=self.risk_agent,
            expected_output="Expected fields: beta, sharpe_ratio, value_at_risk_95, max_drawdown, volatility, daily_returns",
            async_execution=True
        )

        # 6) news_task
        self.news_task = Task(
            description="Gather and analyze recent news and market sentiment data for the following company: Company Name: {company_name}. Pass in this company name to the tool as a string and search for the LATEST company news, this is key, analyze all the snippets, retrieve original urls from the link key and turn them all into a single list of news items ad detailed as possible, pay special attention to recent events that may affect the stock price and other metrics and name any events including named entities ie companies, people, etc that may affect the stock price and other metrics. This is very important, you must use the most recent news at top stories affecting {ticker} stock price and other metrics. Favour stories that are directly related to the company and its products, services, or market position, ESPECIALLY cometitor news  make sure you have diverse stories not just investment news",
            agent=self.news_agent,
            expected_output="ALL news items with the title, content, link, and published_time, comeptitor news is key, you must have at least 10 news items", 
            #output_pydantic=YahooNewsData,
            async_execution=True
        )

        # 7) aggregator_task
        self.aggregator_task = Task(
            description=(
                "Synthesize analyses from all components into a comprehensive financial assessment for the following company: Company Ticker: {ticker}. "
                "Combine data from competitor analysis, fundamental metrics, technical indicators, "
                "risk metrics, and market sentiment into a structured report as well a comprehensive summary including the latest news affecting the company, be sure to cross reference the news and events with the stock price and other metrics. You MUST reference the news exhaustively in the summary and name any events including named entities that may affect the stock price and other metricss"
            ),
            agent=self.aggregator_agent,
            context=[self.competitor_analysis_task, self.fundamental_task, self.risk_task, self.news_task],
            expected_output="Expected json fields with nested objects: ticker, company_name, competitor, fundamental, risk, comprehensive_summary (at least 700 words) This summary should be a comprehensive summary of the entire analysis using the news and events from the previous tasks to reference events that may affect the stock price and other metrics, you MUST reference the news exhaustively in the summary",
            output_pydantic=FinancialAnalysisResult
        )
       

    def execute_financial_analysis(self, inputs: Dict[str, Any]) -> str:
        """
        Full pipeline:
          competitor tasks -> parallel fundamental/technical/risk/news -> aggregator
        Expects inputs: {"ticker":"AAPL","company_name":"Apple"}
        """
        crew = Crew(
            agents=[
                self.competitor_llm_agent,
                self.competitor_analysis_agent,
                self.fundamental_agent,
                #self.technical_agent,
                self.risk_agent,
                self.news_agent,
                self.aggregator_agent
            ],
            tasks=[
                self.competitor_llm_task,
                self.competitor_analysis_task,
                # parallel stage
                self.fundamental_task,
                #self.technical_task,
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