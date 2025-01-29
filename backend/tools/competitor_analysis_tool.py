import yfinance as yf
from typing import Dict, Any, List
from crewai.tools import tool

@tool
def competitor_analysis_tool(tickers: List[str]) -> Dict[str, Any]:
    """
    For each ticker in 'tickers', fetch fundamental info from yfinance. 
    Return an array of competitor details for each.
    """
    output = []
    for t in tickers:
        try:
            t_up = t.upper()
            data = yf.Ticker(t_up)
            info = data.info
            output.append({
                "ticker": t_up,
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
        except:
            pass

    return {"competitors": output}
