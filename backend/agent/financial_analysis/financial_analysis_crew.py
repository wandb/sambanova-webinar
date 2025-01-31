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

###################### RISK ASSESSMENT TOOL ######################
@tool('Risk Assessment Tool')
def risk_assessment_tool(ticker: str, benchmark: str = "^GSPC", period: str = "1y") -> Dict[str, Any]:
    """
    Compute Beta, Sharpe, VaR, Max Drawdown, Volatility, plus monthly-averaged daily_returns for plotting.
    """
    stock = yf.Ticker(ticker)
    bench = yf.Ticker(benchmark)

    stock_close = stock.history(period=period)['Close']
    bench_close = bench.history(period=period)['Close']

    if stock_close.empty or bench_close.empty:
        return {"error": "Insufficient data for risk metrics."}

    stock_returns = stock_close.pct_change().dropna()
    bench_returns = bench_close.pct_change().dropna()

    # Align indexes
    common_idx = stock_returns.index.intersection(bench_returns.index)
    stock_returns = stock_returns.loc[common_idx]
    bench_returns = bench_returns.loc[common_idx]

    # Beta
    cov = np.cov(stock_returns, bench_returns)[0][1]
    var_bench = np.var(bench_returns)
    beta = float(cov / var_bench) if var_bench != 0 else 0.0

    # Sharpe
    risk_free_annual = 0.02
    risk_free_daily = risk_free_annual / 252
    excess = stock_returns - risk_free_daily
    if excess.std() == 0:
        sharpe = 0.0
    else:
        sharpe = float(np.sqrt(252) * excess.mean() / excess.std())

    # VaR
    var_95 = float(np.percentile(stock_returns, 5))

    # Max Drawdown
    cumul = (1 + stock_returns).cumprod()
    peak = cumul.cummax()
    dd = (cumul - peak) / peak
    max_dd = float(dd.min())

    # annual vol
    vol = float(stock_returns.std() * np.sqrt(252))

    # monthly average
    monthly_group = stock_returns.groupby([stock_returns.index.year, stock_returns.index.month]).mean()
    returns_csv = []
    for (year, month), ret in monthly_group.items():
        date_str = f"{year}-{month:02d}"
        returns_csv.append({
            "date": date_str,
            "daily_return": str(ret)
        })

    return {
        "beta": beta,
        "sharpe_ratio": f"{sharpe:.4f}",
        "value_at_risk_95": f"{var_95:.4f}",
        "max_drawdown": f"{max_dd:.4f}",
        "volatility": f"{vol:.4f}",
        "daily_returns": returns_csv
    }

###################### FUNDAMENTAL ANALYSIS TOOL ######################
@tool('Fundamental Analysis Tool')
def fundamental_analysis_tool(ticker: str) -> Dict[str, Any]:
    """
    Retrieve fundamentals from yfinance: 
    - standard fields
    - advanced_fundamentals
    - dividend_history
    - quarterly_fundamentals
    """
    data = yf.Ticker(ticker)
    info = data.info

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

    quarterly_csv = []
    try:
        qfin = data.quarterly_financials
        if qfin is not None and not qfin.empty:
            for date_col in qfin.columns:
                col_str = str(date_col.date()) if hasattr(date_col, "date") else str(date_col)
                total_rev = None
                net_inc = None
                if "Total Revenue" in qfin.index:
                    total_rev = qfin.loc["Total Revenue", date_col]
                if "Net Income" in qfin.index:
                    net_inc = qfin.loc["Net Income", date_col]
                quarterly_csv.append({
                    "date": col_str,
                    "total_revenue": str(total_rev) if total_rev else None,
                    "net_income": str(net_inc) if net_inc else None
                })
    except:
        pass

    result["quarterly_fundamentals"] = quarterly_csv

    adv_data = {}
    adv_data["shares_outstanding"] = str(info.get("sharesOutstanding",""))
    adv_data["float_shares"] = str(info.get("floatShares",""))
    adv_data["enterprise_value"] = str(info.get("enterpriseValue",""))
    adv_data["book_value"] = str(info.get("bookValue",""))

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
    Attempt to find 3 best competitor tickers from yfinance, fallback LLM guess if not found.
    Return: competitor_tickers[], competitor_details[] = []
    """
    fallback_competitors = []
    y = yf.Ticker(ticker)
    inf = y.info
    sector = inf.get("sector","")

    if sector and "Tech" in sector:
        fallback_competitors = ["AMD","INTC","MSFT"]
    elif sector and "Energy" in sector:
        fallback_competitors = ["XOM","CVX","BP"]
    else:
        fallback_competitors = ["GOOGL","AMZN","META"]

    return {
      "competitor_tickers": fallback_competitors[:3],
      "competitor_details": []
    }

###################### COMPETITOR ANALYSIS TOOL ######################
@tool('Competitor Analysis Tool')
def competitor_analysis_tool(tickers: List[str]) -> Dict[str, Any]:
    """
    For each competitor ticker in 'tickers', fetch fundamental info from yfinance.
    Return competitor_tickers plus competitor_details[] with fields:
    {ticker, name, market_cap, pe_ratio, ps_ratio, ebitda_margins, profit_margins, revenue_growth, earnings_growth, short_ratio, industry, sector}.
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

###################### TECHNICAL ANALYSIS TOOL (3mo weekly) #####
@tool('Technical Analysis Tool')
def yf_tech_analysis(ticker: str, period: str = "3mo") -> Dict[str, Any]:
    """
    Get 3-month weekly intervals from yfinance for the ticker, returning standard fields plus stock_price_data.
    """
    data = yf.Ticker(ticker)
    hist = data.history(period=period, interval='1wk')
    stock_price_data = []
    for dt, row in hist.iterrows():
        date_str = dt.strftime("%Y-%m-%d")
        stock_price_data.append({
            "date": date_str,
            "open": str(row["Open"]),
            "high": str(row["High"]),
            "low": str(row["Low"]),
            "close": str(row["Close"]),
            "volume": str(row["Volume"])
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

###################### NEWS MODELS & (SERPER) WRAPPER ######################
from pydantic import BaseModel

class NewsItem(BaseModel):
    title: str
    content: str
    link: str
    published_time: str
    named_entities: List[str] = []

class YahooNewsData(BaseModel):
    news_items: List[NewsItem]

########################## Additional Pydantic Models for aggregator ###############
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
    year_high: str = ""
    year_low: str = ""
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
    date: str
    open: str
    high: str
    low: str
    close: str
    volume: str

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
    date: str
    open: str
    high: str
    low: str
    close: str
    volume: str

class FinancialAnalysisResult(BaseModel):
    ticker: str
    company_name: str
    competitor: CompetitorBlock
    fundamental: FundamentalData
    risk: RiskData
    stock_price_data: List[WeeklyPriceData] = []
    comprehensive_summary: str = ""

########################### The Main Crew Class ###########################
load_dotenv()

class FinancialAnalysisCrew:
    """
    Multi-agent pipeline for advanced financial analysis:
      1) Enhanced competitor (LLM fallback if needed)
      2) Competitor analysis
      3) Fundamentals
      4) Technical (3mo weekly)
      5) Risk (1y)
      6) News
      7) Aggregator => merges all into final JSON, at least 700 words in summary.
    Using partial concurrency to speed up tasks that do not depend on each other.
    """

    def __init__(self, sambanova_key: str, exa_key: str, serper_key: str, user_id: str = "", run_id: str = ""):
        self.llm = LLM(
            model="sambanova/Meta-Llama-3.1-8B-Instruct",
            temperature=0.0,
            max_tokens=4096,
            api_key=sambanova_key
        )
        self.aggregator_llm = LLM(
            model="sambanova/Meta-Llama-3.1-8B-Instruct",
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
        # 1) competitor finder
        self.enhanced_competitor_agent = Agent(
            role="Enhanced Competitor Finder",
            goal="Identify 3 closest competitor tickers for the same industry and sector as {ticker}.",
            backstory="Expert in analyzing sector, fallback to LLM guess if yfinance fails. No extraneous calls needed.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

        # 2) competitor analysis
        self.competitor_analysis_agent = Agent(
            role="Competitor Analysis Agent",
            goal="Given competitor_tickers, produce competitor_details from yfinance fundamentals.",
            backstory="Focus on market_cap, margins, growth, short_ratio, etc. Must be quick and direct.",
            llm=self.llm,
            tools=[competitor_analysis_tool],
            allow_delegation=False,
            verbose=True,
        )

        # 3) fundamental
        self.fundamental_agent = Agent(
            role="Fundamental Analysis Agent",
            goal="Retrieve fundamental data from yfinance including advanced_fundamentals, dividend_history. for {ticker}",
            backstory="Focus on a single pass to avoid overhead. Return structured data quickly.",
            llm=self.llm,
            tools=[fundamental_analysis_tool],
            allow_delegation=False,
            verbose=True,
        )

        # 4) technical
        self.technical_agent = Agent(
            role="Technical Analysis Agent",
            goal="Gather 3-month weekly price data plus standard technical fields from yfinance. for {ticker}",
            backstory="No repeated calls. Provide stock_price_data for front-end charting.",
            llm=self.llm,
            tools=[yf_tech_analysis],
            allow_delegation=False,
            verbose=True,
        )

        # 5) risk
        self.risk_agent = Agent(
            role="Risk Assessment Agent",
            goal="Compute Beta, Sharpe, VaR, Max Drawdown, Volatility over 1 year for {ticker}.",
            backstory="Return monthly-averaged daily returns quickly. No extraneous calls.",
            llm=self.llm,
            tools=[risk_assessment_tool],
            allow_delegation=False,
            verbose=True,
        )

        # 6) news
        os.environ["SERPER_API_KEY"] = self.serper_key
        self.news_agent = Agent(
            role="Financial News Agent",
            goal="Gather recent news for {ticker}, focusing on recent events that could affect stock price. Must be quick.",
            backstory="Search for top ~10 items, do minimal overhead. Summaries used by aggregator. No re-calls.",
            llm=self.aggregator_llm,
            tools=[SerperDevTool()],
            allow_delegation=False,
            verbose=True,
            max_iter=2
        )

        # 7) aggregator
        self.aggregator_agent = Agent(
            role="Aggregator Agent",
            goal=(
                "Combine competitor, fundamental, technical, risk, and news into final JSON. Summaries must be at least 700 words referencing all tasks."
            ),
            backstory="One-pass aggregator. Minimizes tokens by being succinct. Output must match FinancialAnalysisResult pydantic exactly.",
            llm=self.aggregator_llm,
            allow_delegation=False,
            verbose=True,
        )

        # Redis logs
        self.enhanced_competitor_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Enhanced Competitor Finder Agent")
        self.competitor_analysis_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Competitor Analysis Agent")
        self.fundamental_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Fundamental Agent")
        self.technical_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Technical Agent")
        self.risk_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Risk Agent")
        self.news_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "News Agent")
        self.aggregator_agent.step_callback = RedisConversationLogger(self.user_id, self.run_id, "Aggregator Agent")

    def _init_tasks(self):
        # 1) competitor tasks => sequential
        self.enhanced_competitor_task = Task(
            description="Find competitor tickers for {ticker} with EnhancedCompetitorTool. Return competitor_tickers plus competitor_details=[].",
            agent=self.enhanced_competitor_agent,
            expected_output="competitor_tickers[] + competitor_details[] (empty).",
            max_iterations=1
        )
        self.competitor_analysis_task = Task(
            description="Analyze competitor fundamentals for those tickers with competitor_analysis_tool. Return competitor_details array.",
            agent=self.competitor_analysis_agent,
            context=[self.enhanced_competitor_task],
            expected_output="competitor_tickers plus competitor_details array with fundamentals.",
            max_iterations=1
        )

        # 2) fundamentals + technical + risk + news => parallel
        self.fundamental_task = Task(
            description="Get fundamental data from fundamental_analysis_tool for {ticker}. Return FundamentalData quickly.",
            agent=self.fundamental_agent,
            expected_output="FundamentalData object including advanced_fundamentals, etc.",
            async_execution=True,
            max_iterations=1
        )
        self.technical_task = Task(
            description="Use yf_tech_analysis with period='3mo' to get stock_price_data. Return TechnicalData.",
            agent=self.technical_agent,
            expected_output="TechnicalData with stock_price_data.",
            async_execution=True,
            max_iterations=1
        )
        self.risk_task = Task(
            description="Compute risk metrics from risk_assessment_tool for {ticker}, period='1y'. Return RiskData.",
            agent=self.risk_agent,
            expected_output="Beta, Sharpe, VaR, Max Drawdown, Volatility, daily_returns array",
            async_execution=True,
            max_iterations=1
        )
        self.news_task = Task(
            description="Get ~10 recent news items for {ticker} via SerperDevTool. Return them quickly.",
            agent=self.news_agent,
            expected_output="List of news items with title, content, link, published_time, named_entities.",
            async_execution=True,
            max_iterations=1
        )

        # 3) aggregator => sequential
        self.aggregator_task = Task(
            description=(
                "Aggregate all previous steps => final JSON with fields: ticker, company_name, competitor, fundamental, risk, stock_price_data, comprehensive_summary. Comprehensive Summary should be ~700 words referencing everything. Must match FinancialAnalysisResult exactly. You MUST focus on recent news and events that may affect the stock price or metrics of {ticker} not just financial data. Name entities that are mentioned in the news."
            ),
            agent=self.aggregator_agent,
            context=[
                self.competitor_analysis_task, 
                self.fundamental_task, 
                self.technical_task, 
                self.risk_task, 
                self.news_task
            ],
            expected_output="Valid JSON with ticker, company_name, competitor, fundamental, risk, stock_price_data, comprehensive_summary",
            max_iterations=1,
            output_pydantic=FinancialAnalysisResult
        )

    def execute_financial_analysis(self, inputs: Dict[str,Any]) -> str:
        """
        1) Competitor tasks => sequential
        2) Fundamentals + Technical + Risk + News => parallel
        3) Aggregator => merges
        Return final JSON as string (pydantic).
        """
        # Parallel after competitor tasks => speeds up
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
                # concurrency on these four
                self.fundamental_task,
                self.technical_task,
                self.risk_task,
                self.news_task,
                # aggregator last
                self.aggregator_task
            ],
            process=Process.sequential,  # now we use parallel for tasks, aggregator last
            verbose=True
        )
        final = crew.kickoff(inputs=inputs)
        return final.pydantic.model_dump_json()

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
