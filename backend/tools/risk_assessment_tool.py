import yfinance as yf
import numpy as np
from typing import Dict, Any
from crewai.tools import tool

@tool('Risk Assessment Tool')
def risk_assessment_tool(ticker: str, benchmark: str = "^GSPC", period: str = "5y") -> Dict[str, Any]:
    """
    Compute Beta, Sharpe, VaR, Max Drawdown, Volatility, plus daily_returns CSV for advanced plotting.
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
    beta = float(cov/var_bench) if var_bench!=0 else 0.0

    # Sharpe ratio
    risk_free_annual = 0.02
    risk_free_daily = risk_free_annual/252
    excess = stock_returns - risk_free_daily
    if excess.std()==0:
        sharpe = 0.0
    else:
        sharpe = float(np.sqrt(252)*excess.mean()/excess.std())

    # VaR
    var_95 = float(np.percentile(stock_returns,5))
    # Max Drawdown
    cumul = (1+stock_returns).cumprod()
    peak = cumul.cummax()
    dd = (cumul - peak)/peak
    max_dd = float(dd.min())
    # annual vol
    vol = float(stock_returns.std()*np.sqrt(252))

    # daily returns CSV 
    # for sake of tokens can we group by month? 
    # we can do this by creating a new dataframe with the date as the index and the monthly return as the value
    # then we can group by month and sum the returns

    # Group returns by month and calculate average
    monthly_returns = stock_returns.groupby([stock_returns.index.year, stock_returns.index.month]).mean()
    returns_csv = []
    for (year, month), ret in monthly_returns.items():
        # Create date string in YYYY-MM format
        date_str = f"{year}-{month:02d}"
        returns_csv.append({
            "date": date_str,
            "monthly_avg_return": float(ret)
        })

  
    return {
        "beta": beta,
        "sharpe_ratio": sharpe,
        "value_at_risk_95": var_95,
        "max_drawdown": max_dd,
        "volatility": vol,
        "daily_returns": returns_csv
    }
