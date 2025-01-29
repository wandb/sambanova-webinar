from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsInput
from crewai.tools import tool

@tool
def yahoo_news_tool(ticker: str):
    """
    Perform a comprehensive technical analysis on the given stock symbol.
    
    Args:
        ticker (str): The stock symbol to analyze.
        period (str): The time period for analysis. Default is "1y" (1 year).
    
    Returns:
        dict: A dictionary with the detailed technical analysis results.
    """
    return YahooFinanceNewsInput(query=ticker)