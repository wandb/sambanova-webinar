import yfinance as yf
import numpy as np
import pandas as pd
import talib
from scipy.signal import find_peaks
from typing import Dict, Any, List
from crewai.tools import tool

@tool
def technical_analysis_tool(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """
    Returns major technical indicators plus a 'chart_data' CSV-like array 
    for the last 120 days.
    """
    df = yf.download(ticker, period=period)
    if df is None or df.empty:
        return {"error": f"No data for {ticker}"}

    close = df['Close']
    df['rsi'] = talib.RSI(close, timeperiod=14)
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(close,12,26,9)
    df['upper_bb'], df['middle_bb'], df['lower_bb'] = talib.BBANDS(close, timeperiod=20)
    df['ma50'] = talib.SMA(close, timeperiod=50)
    df['ma200'] = talib.SMA(close, timeperiod=200)

    # daily returns -> volatility
    daily_returns = close.pct_change().dropna()
    volatility = float(daily_returns.std()*np.sqrt(252))

    momentum = None
    if len(close)>=20:
        momentum = float(close.iloc[-1]-close.iloc[-20])

    # detect support/resistance from last 60 days
    last60 = close[-60:]
    peaks_idx, _ = find_peaks(last60, distance=5)
    troughs_idx, _ = find_peaks(-last60, distance=5)
    peak_vals = [float(last60.iloc[i]) for i in peaks_idx]
    trough_vals = [float(last60.iloc[i]) for i in troughs_idx]

    # possible chart patterns
    detected_patterns = []
    if len(peak_vals)>=2:
        if abs(peak_vals[-1]-peak_vals[-2])/peak_vals[-2]<0.02:
            detected_patterns.append("double_top")
    if len(trough_vals)>=2:
        if abs(trough_vals[-1]-trough_vals[-2])/trough_vals[-2]<0.02:
            detected_patterns.append("double_bottom")

    # chart_data for last 120 days 
    subset = df.tail(120)
    chart_data = []
    for idx, row in subset.iterrows():
        chart_data.append({
            "date": str(idx.date()),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": float(row["Volume"])
        })

    result = {
        "moving_averages": {
            "ma50": float(df['ma50'].iloc[-1]) if not pd.isna(df['ma50'].iloc[-1]) else None,
            "ma200": float(df['ma200'].iloc[-1]) if not pd.isna(df['ma200'].iloc[-1]) else None
        },
        "rsi": float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else None,
        "macd": {
            "macd": float(df['macd'].iloc[-1]) if not pd.isna(df['macd'].iloc[-1]) else None,
            "signal": float(df['macd_signal'].iloc[-1]) if not pd.isna(df['macd_signal'].iloc[-1]) else None,
            "hist": float(df['macd_hist'].iloc[-1]) if not pd.isna(df['macd_hist'].iloc[-1]) else None
        },
        "bollinger_bands": {
            "upper": float(df['upper_bb'].iloc[-1]) if not pd.isna(df['upper_bb'].iloc[-1]) else None,
            "middle": float(df['middle_bb'].iloc[-1]) if not pd.isna(df['middle_bb'].iloc[-1]) else None,
            "lower": float(df['lower_bb'].iloc[-1]) if not pd.isna(df['lower_bb'].iloc[-1]) else None,
        },
        "volatility": volatility,
        "momentum": momentum,
        "support_levels": sorted(trough_vals),
        "resistance_levels": sorted(peak_vals),
        "detected_patterns": detected_patterns,
        "chart_data": chart_data
    }
    return result
