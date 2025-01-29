from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from crewai.tools import tool

@tool
def yahoo_finance_news_tool(ticker: str):
    """
    Simple wrapper around YahooFinanceNewsTool from langchain_community.
    Returns JSON with top news articles for the ticker.
    """
    news_tool = YahooFinanceNewsTool()
    raw = news_tool.run(ticker)
    # Typically raw is a JSON string. 
    # Return dict with 'news_items'
    return {"news_items": raw}
