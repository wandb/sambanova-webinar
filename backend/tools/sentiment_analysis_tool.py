from textblob import TextBlob
from crewai.tools import tool
from typing import Dict

@tool
def sentiment_analysis_tool(text: str) -> Dict[str, float]:
    """
    Basic sentiment: Return {'polarity': float in [-1..1]} for the text provided.
    """
    blob = TextBlob(text)
    return {"polarity": blob.sentiment.polarity}
