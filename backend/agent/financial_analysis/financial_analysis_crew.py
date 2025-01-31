import os
import sys
import uuid
import json
from typing import Dict, Any, List, Optional
import numpy as np
import yfinance as yf

# Ensure our parent directories are in sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
parent_of_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
if parent_of_parent_dir not in sys.path:
    sys.path.insert(0, parent_of_parent_dir)

from dotenv import load_dotenv

# crewai imports
from crewai import Agent, Task, Crew, LLM, Process
from utils.agent_thought import RedisConversationLogger
from crewai.tools import tool
from crewai_tools import SerperDevTool

###################### RISK ASSESSMENT TOOL (unchanged, used for 1-year period) ######################
@tool('Risk Assessment Tool')
def risk_assessment_tool(ticker: str, benchmark: str = "^GSPC", period: str = "1y") -> Dict[str, Any]:
    """
    Compute Beta, Sharpe, VaR, Max Drawdown, Volatility, plus daily_returns CSV for advanced plotting.
    We do monthly averages to reduce tokens. Period defaults to '1y'.
    """
    stock = yf.Ticker(ticker)
    bench = yf.Ticker(benchmark)

    stock_close = stock.history(period=period)['Close']
    bench_close = bench.history(period=period)['Close']

    if stock_close.empty or bench_close.empty:
        return {"error": "Insufficient data for risk metrics."}

    stock_returns = stock_close.pct_change().dropna()
    bench_returns = bench_close.pct_change().dropna()

    common_idx = stock_returns.index.intersection(bench_returns.index)
    stock_returns = stock_returns.loc[common_idx]
    bench_returns = bench_returns.loc[common_idx]

    cov = np.cov(stock_returns, bench_returns)[0][1]
    var_bench = np.var(bench_returns)
    beta = float(cov/var_bench) if var_bench != 0 else 0.0

    # Sharpe ratio
    risk_free_annual = 0.02
    risk_free_daily = risk_free_annual / 252
    excess = stock_returns - risk_free_daily
    if excess.std() == 0:
        sharpe = 0.0
    else:
        sharpe = float(np.sqrt(252) * excess.mean() / excess.std())

    # VaR @ 95
    var_95 = float(np.percentile(stock_returns, 5))
    # Max Drawdown
    cumul = (1 + stock_returns).cumprod()
    peak = cumul.cummax()
    dd = (cumul - peak)/peak
    max_dd = float(dd.min())
    # annual vol
    vol = float(stock_returns.std() * np.sqrt(252))

    # monthly average returns
    monthly_group = stock_returns.groupby([stock_returns.index.year, stock_returns.index.month]).mean()
    returns_csv = []
    for (year, month), ret in monthly_group.items():
        date_str = f"{year}-{month:02d}"
        returns_csv.append({
            "date": date_str,
            "daily_return": float(ret)
        })

    return {
        "beta": beta,
        "sharpe_ratio": sharpe,
        "value_at_risk_95": var_95,
        "max_drawdown": max_dd,
        "volatility": vol,
        "daily_returns": returns_csv
    }

###################### FUNDAMENTAL ANALYSIS TOOL (unchanged from the last version) ######################
@tool('Fundamental Analysis Tool')
def fundamental_analysis_tool(ticker: str) -> Dict[str, Any]:
    """
    Expanded fundamental analysis with additional metrics from yfinance.
    We also retrieve 'quarterly_fundamentals' plus new advanced data:
    - dividend history
    - advanced_fundamentals (like shares outstanding, float shares, etc.)
    """
    data = yf.Ticker(ticker)
    info = data.info

    # Basic fields
    result = {
        "ticker": ticker,
        "company_name": info.get("longName",""),
        "sector": info.get("sector",""),
        "industry": info.get("industry",""),
        "market_cap": str(info.get("marketCap","")),
        "pe_ratio": str(info.get("trailingPE","")),
        "forward_pe": str(info.get("forwardPE","")),
        "peg_ratio": str(info.get("pegRatio","")),
        "ps_ratio": str(info.get("priceToSalesTrailing12Months","")),
        "price_to_book": str(info.get("priceToBook","")),
        "dividend_yield": str(info.get("dividendYield","")),
        "beta": str(info.get("beta","")),
        "year_high": str(info.get("fiftyTwoWeekHigh","")),
        "year_low": str(info.get("fiftyTwoWeekLow","")),
        "analyst_recommendation": info.get("recommendationKey",""),
        "target_price": str(info.get("targetMeanPrice","")),
        "earnings_per_share": str(info.get("trailingEps","")),
        "profit_margins": str(info.get("profitMargins","")),
        "operating_margins": str(info.get("operatingMargins","")),
        "ebitda_margins": str(info.get("ebitdaMargins","")),
        "short_ratio": str(info.get("shortRatio","")),
    }

    # Attempt advanced statement analysis
    fin = data.financials
    bs = data.balance_sheet
    cf = data.cashflow

    current_ratio = None
    debt_to_equity = None
    roe = None
    roa = None
    revenue_growth = None
    net_income_growth = None
    free_cash_flow = None

    try:
        if bs is not None and not bs.empty:
            if "Total Current Assets" in bs.index and "Total Current Liabilities" in bs.index:
                ca = bs.loc["Total Current Assets"].iloc[0]
                cl = bs.loc["Total Current Liabilities"].iloc[0]
                if cl != 0:
                    current_ratio = float(ca)/float(cl)
            if "Total Liabilities" in bs.index and "Total Stockholder Equity" in bs.index:
                tl = bs.loc["Total Liabilities"].iloc[0]
                te = bs.loc["Total Stockholder Equity"].iloc[0]
                if te != 0:
                    debt_to_equity = float(tl)/float(te)
        if fin is not None and not fin.empty:
            if "Net Income" in fin.index and "Total Revenue" in fin.index:
                ni = fin.loc["Net Income"]
                tr = fin.loc["Total Revenue"]
                if len(ni) >= 2:
                    prev = ni.iloc[1]
                    curr = ni.iloc[0]
                    if abs(prev) > 0:
                        net_income_growth = (curr - prev)/abs(prev)
                if len(tr) >= 2:
                    prev = tr.iloc[1]
                    curr = tr.iloc[0]
                    if abs(prev) > 0:
                        revenue_growth = (curr - prev)/abs(prev)
            if "Net Income" in fin.index and "Total Stockholder Equity" in bs.index:
                neti_latest = fin.loc["Net Income"].iloc[0]
                eq_latest = bs.loc["Total Stockholder Equity"].iloc[0]
                if eq_latest != 0:
                    roe = float(neti_latest)/float(eq_latest)
            if "Net Income" in fin.index and "Total Assets" in bs.index:
                neti_latest = fin.loc["Net Income"].iloc[0]
                assets_latest = bs.loc["Total Assets"].iloc[0]
                if assets_latest != 0:
                    roa = float(neti_latest)/float(assets_latest)
        if cf is not None and not cf.empty:
            if "Operating Cash Flow" in cf.index and "Capital Expenditures" in cf.index:
                ocf = cf.loc["Operating Cash Flow"].iloc[0]
                capex = cf.loc["Capital Expenditures"].iloc[0]
                free_cash_flow = float(ocf) - float(capex)
    except:
        pass

    result["current_ratio"] = str(current_ratio if current_ratio else "")
    result["debt_to_equity"] = str(debt_to_equity if debt_to_equity else "")
    result["return_on_equity"] = str(roe if roe else "")
    result["return_on_assets"] = str(roa if roa else "")
    result["revenue_growth"] = str(revenue_growth if revenue_growth else "")
    result["net_income_growth"] = str(net_income_growth if net_income_growth else "")
    result["free_cash_flow"] = str(free_cash_flow if free_cash_flow else "")

    # Attempt to retrieve quarterly_fundamentals
    quarterly_csv = []
    try:
        qfin = data.quarterly_financials
        if qfin is not None and not qfin.empty:
            for date_col in qfin.columns:
                col_str = str(date_col.date()) if hasattr(date_col, "date") else str(date_col)
                total_rev = None
                net_inc = None
                if "Total Revenue" in qfin.index:
                    total_rev = float(qfin.loc["Total Revenue", date_col])
                if "Net Income" in qfin.index:
                    net_inc = float(qfin.loc["Net Income", date_col])
                quarterly_csv.append({
                    "date": col_str,
                    "total_revenue": total_rev,
                    "net_income": net_inc
                })
    except:
        pass
    result["quarterly_fundamentals"] = quarterly_csv

    # Additional advanced data from yfinance: e.g. share count, float shares, etc.
    adv_data = {}
    adv_data["shares_outstanding"] = str(info.get("sharesOutstanding",""))
    adv_data["float_shares"] = str(info.get("floatShares",""))
    adv_data["enterprise_value"] = str(info.get("enterpriseValue",""))
    adv_data["book_value"] = str(info.get("bookValue",""))

    # Attempt to gather dividends
    div_hist = []
    try:
        dividends = data.dividends
        for dt, val in dividends.iteritems():
            div_hist.append({"date": str(dt.date()), "dividend": float(val)})
    except:
        pass

    return {
        "ticker": ticker,
        **result,
        "advanced_fundamentals": adv_data,
        "dividend_history": div_hist
    }

###################### COMPETITOR TOOL WITH PROMPT ENGINEERING ######################
@tool('EnhancedCompetitorTool')
def enhanced_competitor_tool(company_name: str, ticker: str) -> Dict[str, Any]:
    """
    Attempts to find relevant competitor tickers using yfinance's peers or 'info' data.
    If that fails, it uses a small LLM-based approach to guess the top 3.
    Return a list of competitor tickers and an empty competitor_details[] (the competitor_analysis tool will fill them).
    """
    # For demonstration, we do an approximate approach:
    fallback_competitors = []
    y = yf.Ticker(ticker)
    inf = y.info
    sector = inf.get("sector","")

    if sector and "Tech" in sector:
        fallback_competitors = ["AMD","INTC","MSFT"]
    elif sector and "Energy" in sector:
        fallback_competitors = ["XOM","CVX","BP"]
    else:
        fallback_competitors = ["GOOGL","AMZN","META"]  # fallback guess

    return {
      "competitor_tickers": fallback_competitors[:3],
      "competitor_details": []
    }

###################### COMPETITOR ANALYSIS TOOL ######################
@tool('Competitor Analysis Tool')
def competitor_analysis_tool(tickers: List[str]) -> Dict[str, Any]:
    """
    For each ticker in 'tickers', fetch basic fundamentals from yfinance to produce:
    {ticker, name, market_cap, pe_ratio, ps_ratio, ebitda_margins, profit_margins, revenue_growth, earnings_growth, short_ratio, industry, sector}
    Return competitor_details[] plus competitor_tickers[] = tickers
    """
    details = []
    for t in tickers:
        data = yf.Ticker(t)
        info = data.info
        details.append({
            "ticker": t,
            "name": info.get("longName",""),
            "market_cap": str(info.get("marketCap","")),
            "pe_ratio": str(info.get("trailingPE","")),
            "ps_ratio": str(info.get("priceToSalesTrailing12Months","")),
            "ebitda_margins": str(info.get("ebitdaMargins","")),
            "profit_margins": str(info.get("profitMargins","")),
            "revenue_growth": str(info.get("revenueGrowth","")),
            "earnings_growth": str(info.get("earningsGrowth","")),
            "short_ratio": str(info.get("shortRatio","")),
            "industry": info.get("industry",""),
            "sector": info.get("sector","")
        })
    return {
      "competitor_tickers": tickers,
      "competitor_details": details
    }

###################### TECHNICAL ANALYSIS TOOL (6mo weekly now) #####
@tool('Technical Analysis Tool')
def yf_tech_analysis(ticker: str, period: str = "6mo") -> Dict[str, Any]:
    """
    Perform technical analysis on ticker. Now retrieving 6-month weekly intervals
    to save on tokens.
    Returns standard fields plus 'stock_price_data': an array of {date, open, high, low, close, volume}.
    """
    data = yf.Ticker(ticker)
    hist = data.history(period=period, interval='1wk')
    stock_price_data = []
    for dt, row in hist.iterrows():
        date_str = dt.strftime("%Y-%m-%d")
        stock_price_data.append({
            "date": date_str,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"])
        })
    return {
        "moving_averages": {"ma50": None,"ma200": None},
        "rsi": None,
        "macd": {"macd_line": None,"signal_line": None},
        "bollinger_bands": {"upper": None,"middle": None,"lower": None},
        "volatility": None,
        "momentum": None,
        "support_levels": [],
        "resistance_levels": [],
        "detected_patterns": [],
        "chart_data": [],
        "stock_price_data": stock_price_data
    }

############# NEWS Pydantic + Tool + Agent to gather & analyze recent news #############
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    title: str
    content: str
    link: str
    published_time: str
    named_entities: List[str] = []

class YahooNewsData(BaseModel):
    news_items: List[NewsItem]



########################## Additional Pydantic Models for the aggregator ###############
class QuarterlyFundamentals(BaseModel):
    date: str
    total_revenue: Optional[str] = None
    net_income: Optional[str] = None

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
    advanced_fundamentals: Dict[str, str] = {}
    dividend_history: List[Dict[str,Any]] = []

class TechnicalChartData(BaseModel):
    date: str = ""
    open: str = ""
    high: str = ""
    low: str = ""
    close: str = ""
    volume: str = ""

class TechnicalData(BaseModel):
    moving_averages: Dict[str, Optional[str]] = {}
    rsi: Optional[str] = None
    macd: Dict[str, Optional[str]] = {}
    bollinger_bands: Dict[str, Optional[str]] = {}
    volatility: Optional[str] = None
    momentum: Optional[str] = None
    support_levels: List[str] = []
    resistance_levels: List[str] = []
    detected_patterns: List[str] = []
    chart_data: List[TechnicalChartData] = []
    stock_price_data: List[TechnicalChartData] = []

class RiskDailyReturns(BaseModel):
    date: str
    daily_return: str

class RiskData(BaseModel):
    beta: float
    sharpe_ratio: str
    value_at_risk_95: str
    max_drawdown: str
    volatility: str
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

class WeeklyPriceData(BaseModel):
    date: str = ""
    open: str = ""
    high: str = ""
    low: str = ""
    close: str = ""
    volume: str = ""

class YahooNewsData(BaseModel):
    news_items: List[NewsItem]

class FinancialAnalysisResult(BaseModel):
    ticker: str
    company_name: str
    competitor: CompetitorBlock
    fundamental: FundamentalData
    risk: RiskData
    stock_price_data: List[WeeklyPriceData] = []
    comprehensive_summary: str = ""

########################### THE CREW CLASS (with News Agent & Task) ###########################
load_dotenv()

class FinancialAnalysisCrew:
    """
    Multi-agent pipeline:
      1) Enhanced competitor step
      2) competitor_analysis -> competitor_details
      3) fundamental
      4) technical (6-month weekly stock data)
      5) risk
      6) news => gather top stories & produce ~10 items if possible
      7) aggregator => merges everything into final JSON, referencing the news, advanced_fundamentals, etc.
    """

    def __init__(self, sambanova_key: str, exa_key: str, serper_key: str, user_id: str = "", run_id: str = ""):
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-8B-Instruct",
            temperature=0.0,
            max_tokens=4096,
            api_key=sambanova_key
        )
        self.aggregator_llm = LLM(
            model="sambanova/Meta-Llama-3.1-70B-Instruct",
            temperature=0.0,
            max_tokens=8192,
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
        # Enhanced competitor agent
        self.enhanced_competitor_agent = Agent(
            role="Enhanced Competitor Finder",
            goal=(
                "Identify 3 MOST  relevant competitor tickers for the target company {ticker}. Be sure to match the industry and sector of the target company, this is crucial they should be in the same industry are going for the same market share."
            ),
            backstory="You are an experienced financial analyst and you know the industry and sector of the target company. You are also an expert in the field of finance and you know the market share of the target company and the competitors. You are also an expert in the field of finance and you know the market share of the target company and the competitors.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            #output_pydantic=CompetitorBlock
        )

        # Competitor analysis
        self.competitor_analysis_agent = Agent(
            role="Competitor Analysis Agent",
            goal="Perform detailed analysis of competitor fundamentals from yfinance. Output competitor_info objects.",
            backstory="Retained from old pipeline, obtains competitor metrics.",
            llm=self.llm,
            tools=[competitor_analysis_tool],
            allow_delegation=False,
            verbose=True,
        )

        # Fundamental
        self.fundamental_agent = Agent(
            role="Fundamental Analysis Agent",
            goal="Analyze fundamental data plus advanced statements, dividend history, etc. from yfinance for the target ticker.",
            backstory="Extended with advanced_fundamentals & dividend_history. Output FundamentalData.",
            llm=self.llm,
            tools=[fundamental_analysis_tool],
            allow_delegation=False,
            verbose=True,
        )

        # Technical
        self.technical_agent = Agent(
            role="Technical Analysis Agent",
            goal="Fetch 3-month weekly stock price plus standard technical fields. Output a TechnicalData object with stock_price_data[].",
            backstory="Using 3-month weekly intervals to reduce token usage. We keep old disclaimers.",
            llm=self.llm,
            tools=[yf_tech_analysis],
            allow_delegation=False,
            verbose=True,
            #output_pydantic=TechnicalData
        )

        # Risk
        self.risk_agent = Agent(
            role="Risk Assessment Agent",
            goal="Compute advanced risk metrics from yfinance returns. Return monthly average returns in daily_returns array.",
            backstory="Same as old approach, 1-year period. Output RiskData.",
            llm=self.llm,
            tools=[risk_assessment_tool],
            allow_delegation=False,
            verbose=True,
        )

        # News agent
        # We'll use 'Yahoo Finance News Tool' or 'SerperDevTool'. 
        os.environ["SERPER_API_KEY"] = self.serper_key
        self.news_agent = Agent(
            role="Financial News Agent",
            goal=(
                "Gather and analyze recent news and market sentiment data for {company_name}. You focus on the latest news and market sentiment data for {company_name}. Especially on stories that may affect the stock price or metrics. Summarize competitor angles, product announcements, etc."
            ),
            backstory=(
                "You are a seasoned news reporter for companies you are familiar with all companiesover the world. You are an expert in the field of cause and effect and you can analyze the news and market sentiment data for {company_name} and summarize the competitor angles, product announcements, etc."
            ),
            llm=self.aggregator_llm,
            tools=[SerperDevTool()], 
            allow_delegation=False,
            verbose=True
        )

        # aggregator
        self.aggregator_agent = Agent(
            role="Aggregator Agent",
            goal=(
                "Combine competitor, fundamental, technical, risk, and news data into a single final JSON. We keep old aggregator instructions plus new references to advanced_fundamentals, dividend_history, 6-month stock_price_data, and the 'news' array. Summaries must be at least 700 words referencing major news items or competitor events. The final JSON must match:  ticker, company_name, competitor, fundamental, risk, stock_price_data, news, comprehensive_summary "
            ),
            backstory="We keep old disclaimers: thorough 700+ words referencing all new data, competitor moves, news items. Must not remove any field from the final schema.",
            llm=self.aggregator_llm,
            allow_delegation=False,
            verbose=True,

        )

        # attach redis logs
        self.enhanced_competitor_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Enhanced Competitor Finder Agent")
        self.competitor_analysis_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Competitor Analysis Agent")
        self.fundamental_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Fundamental Agent")
        self.technical_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Technical Agent")
        self.risk_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Risk Agent")
        self.news_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "News Agent")
        self.aggregator_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Aggregator Agent")

    def _init_tasks(self):
        # 1) competitor finding
        self.enhanced_competitor_task = Task(
            description="Find competitor tickers for {ticker} using the EnhancedCompetitorTool. Return competitor_tickers plus competitor_details=[].",
            agent=self.enhanced_competitor_agent,
            expected_output="competitor_tickers[] plus competitor_details=[]"
        )
        # 2) competitor analysis
        self.competitor_analysis_task = Task(
            description="Use competitor_analysis_tool on those competitor tickers to produce competitor_details.",
            agent=self.competitor_analysis_agent,
            context=[self.enhanced_competitor_task],
            expected_output="competitor_tickers plus competitor_details array with ticker,name,market_cap,..."
        )
        # 3) fundamental
        self.fundamental_task = Task(
            description="Retrieve fundamentals from fundamental_analysis_tool for {ticker}, including advanced_fundamentals & dividend_history.",
            agent=self.fundamental_agent,
            expected_output="FundamentalData"
        )
        # 4) technical
        self.technical_task = Task(
            description="Get 6-month weekly data from yf_tech_analysis for {ticker}. Invoke the tool with the ticker, the period ie '3mo'.",
            agent=self.technical_agent,
            expected_output="TechnicalData ie moving_averages, rsi, macd, bollinger_bands, volatility, momentum, support_levels, resistance_levels, detected_patterns, chart_data, stock_price_data",
            async_execution=True
        )
        # 5) risk
        self.risk_task = Task(
            description="Compute risk metrics for {ticker} over 1-year from risk_assessment_tool. Invoke the tool with the ticker, the period ie '1y' and the benchmark: str = '^GSPC' ",
            agent=self.risk_agent, 
            expected_output="RiskData ie beta, sharpe_ratio, value_at_risk_95, max_drawdown, volatility, daily_returns",
            async_execution=True
        )
        # 6) news
        self.news_task = Task(
            description=(
                "Gather and analyze recent news for {company_name} from the last ~3 months, referencing competitor news as well. ReturnTitle, content, link, published_time, named_entities."
            ),
            agent=self.news_agent,
            expected_output="All of the recent news items about {company_name} focusing on competitor news, product announcements, etc.",
            async_execution=True,
            max_iterations=1
        )
        # 7) aggregator
        self.aggregator_task = Task(
            description=(
                "Aggregate competitor, fundamental, technical, risk, and comprehensive_summary data into final JSON. The Comprehensive_summary must be >=700 words summarizing all financial data and metrics and espcially latest stories and data from the previous steps. You do NOT need to include the news in the final JSON. The news is only for the news_agent and is replaced by the comprehensive_summary."
            ),
            agent=self.aggregator_agent,
            context=[self.competitor_analysis_task, self.fundamental_task, self.technical_task, self.risk_task, self.news_task],
            expected_output="A legal json containing ticker, company_name, competitor, fundamental, risk, stock_price_data, comprehensive_summary and nothing else no comments or other text or backticks or anything else",
            output_pydantic=FinancialAnalysisResult
        )

    def execute_financial_analysis(self, inputs: Dict[str,Any]) -> str:
        """
        The full pipeline in sequence:
          1) competitor tasks
          2) fundamentals + technical + risk + news
          3) aggregator => merges everything
        Returns a JSON string matching 'FinancialAnalysisResult'.
        """
        crew = Crew(
            agents=[
                self.enhanced_competitor_agent,
                self.competitor_analysis_agent,
                self.fundamental_agent,
                self.technical_agent,
                self.risk_agent,
                self.news_agent,
                self.aggregator_agent
            ],
            tasks=[
                self.enhanced_competitor_task,
                self.competitor_analysis_task,
                self.fundamental_task,
                self.technical_task,
                self.risk_task,
                self.news_task,
                self.aggregator_task
            ],
            process=Process.sequential,
            verbose=True
        )
        final = crew.kickoff(inputs=inputs)
        final = final.pydantic.model_dump_json()
        return final

########## EXAMPLE MAIN ##############
def main():
    load_dotenv()
    example_samba_key = "YOUR_SAMBANOVA_KEY"
    exa_key = "YOUR_EXA_KEY"
    serper_key = "YOUR_SERPER_KEY"
    user_id = "demo_user"
    run_id = str(uuid.uuid4())

    inputs = {
        "ticker": "NVDA",
        "company_name": "NVIDIA Corporation"
    }

    fac = FinancialAnalysisCrew(
        sambanova_key=example_samba_key,
        exa_key=exa_key,
        serper_key=serper_key,
        user_id=user_id,
        run_id=run_id
    )
    result_json = fac.execute_financial_analysis(inputs)
    print("FINAL FINANCIAL ANALYSIS JSON:\n")
    print(result_json)

if __name__=="__main__":
    main()
