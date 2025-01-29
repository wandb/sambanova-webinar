import yfinance as yf
from typing import Dict, Any, List
from crewai.tools import tool

@tool('Fundamental Analysis Tool')
def fundamental_analysis_tool(ticker: str) -> Dict[str, Any]:
    """
    Expanded fundamental analysis with additional metrics: EPS, P/S, short ratio, margins, etc.
    Also retrieve 'quarterly_fundamentals' as a list of dicts for front-end CSV plotting.
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
        "52_week_high": str(info.get("fiftyTwoWeekHigh","")),
        "52_week_low": str(info.get("fiftyTwoWeekLow","")),
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

    # We'll store some derived ratios
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
                if cl != 0: current_ratio = float(ca)/float(cl)
            if "Total Liabilities" in bs.index and "Total Stockholder Equity" in bs.index:
                tl = bs.loc["Total Liabilities"].iloc[0]
                te = bs.loc["Total Stockholder Equity"].iloc[0]
                if te != 0: debt_to_equity = float(tl)/float(te)
        if fin is not None and not fin.empty:
            if "Net Income" in fin.index and "Total Revenue" in fin.index:
                ni = fin.loc["Net Income"]
                tr = fin.loc["Total Revenue"]
                if len(ni)>=2:
                    prev = ni.iloc[1]
                    curr = ni.iloc[0]
                    if abs(prev)>0: net_income_growth = (curr-prev)/abs(prev)
                if len(tr)>=2:
                    prev = tr.iloc[1]
                    curr = tr.iloc[0]
                    if abs(prev)>0: revenue_growth = (curr-prev)/abs(prev)
            if "Net Income" in fin.index and "Total Stockholder Equity" in bs.index:
                neti_latest = fin.loc["Net Income"].iloc[0]
                eq_latest = bs.loc["Total Stockholder Equity"].iloc[0]
                if eq_latest!=0: roe = float(neti_latest)/float(eq_latest)
            if "Net Income" in fin.index and "Total Assets" in bs.index:
                neti_latest = fin.loc["Net Income"].iloc[0]
                assets_latest = bs.loc["Total Assets"].iloc[0]
                if assets_latest!=0: roa = float(neti_latest)/float(assets_latest)
        if cf is not None and not cf.empty:
            if "Operating Cash Flow" in cf.index and "Capital Expenditures" in cf.index:
                ocf = cf.loc["Operating Cash Flow"].iloc[0]
                capex = cf.loc["Capital Expenditures"].iloc[0]
                free_cash_flow = float(ocf)-float(capex)
    except:
        pass

    result["current_ratio"] = str(current_ratio if current_ratio else "")
    result["debt_to_equity"] = str(debt_to_equity if debt_to_equity else "")
    result["return_on_equity"] = str(roe if roe else "")
    result["return_on_assets"] = str(roa if roa else "")
    result["revenue_growth"] = str(revenue_growth if revenue_growth else "")
    result["net_income_growth"] = str(net_income_growth if net_income_growth else "")
    result["free_cash_flow"] = str(free_cash_flow if free_cash_flow else "")

    # Now let's also gather 'quarterly_fundamentals' from yfinance if possible
    # e.g. data.quarterly_financials or data.quarterly_earnings
    # We'll try data.quarterly_financials 
    # It's a DataFrame with row=financial line item, columns=dates
    quarterly_csv = []
    try:
        qfin = data.quarterly_financials
        # Each column is a quarter date, each row is e.g. "Net Income", "Total Revenue"
        # We'll pivot into a CSV-like array of {date, total_revenue, net_income, ...}
        if qfin is not None and not qfin.empty:
            # Let's just parse out "Total Revenue" and "Net Income" for demonstration
            # Dates are columns, row index are line items
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

    return result
