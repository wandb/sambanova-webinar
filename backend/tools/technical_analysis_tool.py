import yfinance as yf
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt  # For potential plotting if desired
from datetime import datetime, timedelta
from crewai.tools import tool

@tool('yf_tech_analysis')
def yf_tech_analysis(ticker: str, period: str = "1y"):
    """
    Perform a comprehensive technical analysis on the given stock symbol.

    Includes:
      - Moving Averages, MACD, RSI, Bollinger Bands, Stochastic, ATR, OBV
      - Fibonacci Retracements, Support/Resistance, Potential Breakouts
      - Trend Identification, Volume Analysis
      - Additional: Sharpe/Sortino, Beta vs SPY, Golden Cross detection,
                    Pivot Points, Rolling correlation with SPY.
    
    Args:
        ticker (str): The stock symbol to analyze.
        period (str): The time period for analysis. Default is "1y" (1 year).
    
    Returns:
        dict:
            A dictionary with:
            - "DataFrame": A Pandas DataFrame containing all the calculated columns.
            - Other keys summarizing various indicators, statistics, and interpretations.
    """

    # -----------------------
    # 1) Download Data
    # -----------------------
    data = yf.download(ticker, period=period)

    # Flatten multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [
            "_".join(str(level) for level in col if level)
            for col in data.columns.to_flat_index()
        ]

    # Rename columns to standard
    rename_map = {}
    for col in data.columns:
        if 'Open' in col and 'Adj' not in col:
            rename_map[col] = 'Open'
        elif 'High' in col and 'Adj' not in col:
            rename_map[col] = 'High'
        elif 'Low' in col and 'Adj' not in col:
            rename_map[col] = 'Low'
        elif 'Close' in col and 'Adj' not in col:
            rename_map[col] = 'Close'
        elif 'Volume' in col:
            rename_map[col] = 'Volume'
        elif 'Adj Close' in col:
            rename_map[col] = 'Adj_Close'
        else:
            rename_map[col] = col

    data.rename(columns=rename_map, inplace=True)

    # Ensure required columns exist (fill with NaN if missing)
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for rc in required_cols:
        if rc not in data.columns:
            data[rc] = np.nan

    # Keep only main columns
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

    # -----------------------
    # 2) Moving Averages
    # -----------------------
    for ma in [20, 50, 100, 200]:
        data[f'{ma}_MA'] = data['Close'].rolling(window=ma).mean()

    # -----------------------
    # 3) Exponential MAs
    # -----------------------
    for ema in [12, 26, 50, 200]:
        data[f'{ema}_EMA'] = data['Close'].ewm(span=ema, adjust=False).mean()

    # -----------------------
    # 4) MACD
    # -----------------------
    data['MACD'] = data['12_EMA'] - data['26_EMA']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']

    # -----------------------
    # 5) RSI
    # -----------------------
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    data['RSI'] = 100.0 - (100.0 / (1.0 + rs))

    # -----------------------
    # 6) Bollinger Bands
    # -----------------------
    data['20_MA'] = data['Close'].rolling(window=20).mean()
    data['20_SD'] = data['Close'].rolling(window=20).std()
    data['Upper_BB'] = data['20_MA'] + 2 * data['20_SD']
    data['Lower_BB'] = data['20_MA'] - 2 * data['20_SD']

    # -----------------------
    # 7) Stochastic Oscillator
    # -----------------------
    low_14 = data['Low'].rolling(window=14).min()
    high_14 = data['High'].rolling(window=14).max()
    data['%K'] = (data['Close'] - low_14) / (high_14 - low_14 + 1e-9) * 100
    data['%D'] = data['%K'].rolling(window=3).mean()

    # -----------------------
    # 8) Average True Range
    # -----------------------
    data['Prev_Close'] = data['Close'].shift()
    data['TR'] = np.maximum(
        data['High'] - data['Low'],
        np.maximum(abs(data['High'] - data['Prev_Close']),
                   abs(data['Low'] - data['Prev_Close']))
    )
    data['ATR'] = data['TR'].rolling(window=14).mean()

    # -----------------------
    # 9) On-Balance Volume
    # -----------------------
    data['OBV'] = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()

    # -----------------------
    # 10) Fibonacci Retracements
    # -----------------------
    max_price = data['High'].max()
    min_price = data['Low'].min()
    diff = max_price - min_price

    fibonacci_levels = {
        '0%': max_price,
        '23.6%': max_price - 0.236 * diff,
        '38.2%': max_price - 0.382 * diff,
        '50%': max_price - 0.5 * diff,
        '61.8%': max_price - 0.618 * diff,
        '100%': min_price
    }

    # -----------------------
    # 11) Support & Resistance
    # -----------------------
    data['Support'] = data['Low'].rolling(window=20).min()
    data['Resistance'] = data['High'].rolling(window=20).max()
    data[['Support','Resistance']] = data[['Support','Resistance']].fillna(method='bfill')

    data['Potential_Breakout'] = np.where(
        data['Close'] > data['Resistance'].shift(1),
        'Bullish Breakout',
        np.where(
            data['Close'] < data['Support'].shift(1),
            'Bearish Breakdown',
            'No Breakout'
        )
    )

    # -----------------------
    # 12) Trend Identification
    # -----------------------
    data['Trend'] = np.where(
        (data['Close'] > data['200_MA']) & (data['50_MA'] > data['200_MA']),
        'Bullish',
        np.where(
            (data['Close'] < data['200_MA']) & (data['50_MA'] < data['200_MA']),
            'Bearish',
            'Neutral'
        )
    )

    # -----------------------
    # 13) Volume Analysis
    # -----------------------
    data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
    data['Volume_Trend'] = np.where(
        data['Volume'] > data['Volume_MA'],
        'Above Average',
        'Below Average'
    )

    # -----------------------
    # 14) Additional Analysis (Returns, Sharpe, Sortino, Beta)
    # -----------------------
    data['Returns'] = data['Close'].pct_change()
    data['Daily_Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))

    daily_return_mean = data['Returns'].mean()
    daily_return_std = data['Returns'].std()

    sharpe_ratio = None
    sortino_ratio = None
    if daily_return_std and daily_return_std != 0:
        sharpe_ratio = (daily_return_mean / daily_return_std) * np.sqrt(252)

    negative_returns = data['Returns'].where(data['Returns'] < 0, 0)
    downside_std = negative_returns.std()
    if downside_std and downside_std != 0:
        sortino_ratio = (daily_return_mean / downside_std) * np.sqrt(252)

    # Download SPY for Beta + rolling correlation
    spy_data = yf.download("SPY", period=period)
    if isinstance(spy_data.columns, pd.MultiIndex):
        spy_data.columns = [
            "_".join(str(level) for level in col if level)
            for col in spy_data.columns.to_flat_index()
        ]
        rename_spy = {}
        for col in spy_data.columns:
            if 'Close' in col and 'Adj' not in col:
                rename_spy[col] = 'Close'
            elif 'Open' in col:
                rename_spy[col] = 'Open'
            elif 'High' in col:
                rename_spy[col] = 'High'
            elif 'Low' in col:
                rename_spy[col] = 'Low'
            elif 'Volume' in col:
                rename_spy[col] = 'Volume'
            else:
                rename_spy[col] = col
        spy_data.rename(columns=rename_spy, inplace=True)

    if 'Close' not in spy_data.columns:
        spy_data['Close'] = np.nan

    spy_data['Returns'] = spy_data['Close'].pct_change()

    # Merge with main data for correlation
    merged = pd.DataFrame({
        'Asset': data['Returns'],
        'SPY': spy_data['Returns']
    }).dropna()

    beta = None
    if len(merged) > 1:
        covariance = np.cov(merged['Asset'], merged['SPY'])[0, 1]
        variance = np.var(merged['SPY'])
        if variance != 0:
            beta = covariance / variance

    # Rolling correlation (30-day) with SPY
    # Re-merge carefully on date index to keep alignment
    data_merged = pd.concat([data['Returns'], spy_data['Returns']], axis=1, join='inner')
    data_merged.columns = ['Asset', 'SPY']
    data['Corr_with_SPY_30d'] = data_merged['Asset'].rolling(window=30).corr(data_merged['SPY'])

    # -----------------------
    # 15) Golden Cross Detection
    # -----------------------
    # We'll create a column that indicates True/False when 50_MA crosses above 200_MA
    data['Golden_Cross'] = (
        (data['50_MA'] > data['200_MA']) & 
        (data['50_MA'].shift(1) <= data['200_MA'].shift(1))
    )

    # Also detect a 'Death Cross'
    data['Death_Cross'] = (
        (data['50_MA'] < data['200_MA']) &
        (data['50_MA'].shift(1) >= data['200_MA'].shift(1))
    )

    # -----------------------
    # 16) Pivot Points
    # -----------------------
    # Using classic floor trader pivots, for daily candles
    # P = (previous high + previous low + previous close) / 3
    # R1 = 2P - previous low ; S1 = 2P - previous high
    # R2 = P + (previous high - previous low) ; S2 = P - (previous high - previous low)
    data['P'] = ((data['High'].shift(1) + data['Low'].shift(1) + data['Close'].shift(1)) / 3)
    data['R1'] = (2 * data['P']) - data['Low'].shift(1)
    data['S1'] = (2 * data['P']) - data['High'].shift(1)
    data['R2'] = data['P'] + (data['High'].shift(1) - data['Low'].shift(1))
    data['S2'] = data['P'] - (data['High'].shift(1) - data['Low'].shift(1))

    # -----------------------
    # 17) Final Results
    # -----------------------
    latest = data.iloc[-1]
    analysis_results = {
        'Current_Price': latest['Close'],
        'Moving_Averages': {
            f'{ma}_MA': latest.get(f'{ma}_MA', np.nan) for ma in [20, 50, 100, 200]
        },
        'Exponential_MAs': {
            f'{ema}_EMA': latest.get(f'{ema}_EMA', np.nan) for ema in [12, 26, 50, 200]
        },
        'MACD': {
            'MACD': latest.get('MACD', np.nan),
            'Signal_Line': latest.get('Signal_Line', np.nan),
            'Histogram': latest.get('MACD_Histogram', np.nan)
        },
        'RSI': latest.get('RSI', np.nan),
        'Bollinger_Bands': {
            'Upper': latest.get('Upper_BB', np.nan),
            'Middle': latest.get('20_MA', np.nan),
            'Lower': latest.get('Lower_BB', np.nan)
        },
        'Stochastic': {
            '%K': latest.get('%K', np.nan),
            '%D': latest.get('%D', np.nan)
        },
        'ATR': latest.get('ATR', np.nan),
        'OBV': latest.get('OBV', np.nan),
        'Fibonacci_Levels': fibonacci_levels,
        'Support_Resistance': {
            'Support': latest.get('Support', np.nan),
            'Resistance': latest.get('Resistance', np.nan)
        },
        'Potential_Breakout': latest.get('Potential_Breakout', 'N/A'),
        'Trend': latest.get('Trend', 'N/A'),
        'Volume': {
            'Current': latest.get('Volume', np.nan),
            'MA': latest.get('Volume_MA', np.nan),
            'Trend': latest.get('Volume_Trend', 'N/A')
        },
        'Returns': {
            'Daily': latest.get('Returns', np.nan),
            'Daily_Log_Return': latest.get('Daily_Log_Returns', np.nan)
        }
    }

    # -----------------------
    # 18) Basic Statistics
    # -----------------------
    annual_volatility = data['Close'].pct_change().std() * np.sqrt(252)
    analysis_results['Statistics'] = {
        'Yearly_High': data['High'].max(),
        'Yearly_Low': data['Low'].min(),
        'Average_Volume': data['Volume'].mean(),
        'Annualized_Volatility': annual_volatility,
        'Sharpe_Ratio': sharpe_ratio,
        'Sortino_Ratio': sortino_ratio,
        'Beta_vs_SPY': beta
    }

    # Additional signals
    analysis_results['Golden_Cross'] = bool(latest.get('Golden_Cross', False))
    analysis_results['Death_Cross'] = bool(latest.get('Death_Cross', False))
    analysis_results['Corr_with_SPY_30d'] = latest.get('Corr_with_SPY_30d', np.nan)
    analysis_results['Pivot_Points'] = {
        'P': latest.get('P', np.nan),
        'R1': latest.get('R1', np.nan),
        'S1': latest.get('S1', np.nan),
        'R2': latest.get('R2', np.nan),
        'S2': latest.get('S2', np.nan)
    }

    # -----------------------
    # 19) Simple Interpretation
    # -----------------------
    rsi_val = latest.get('RSI', np.nan)
    macd_val = latest.get('MACD', np.nan)
    signal_line_val = latest.get('Signal_Line', np.nan)
    k_val = latest.get('%K', np.nan)
    boll_upper = latest.get('Upper_BB', np.nan)
    boll_lower = latest.get('Lower_BB', np.nan)
    current_close = latest.get('Close', np.nan)
    volume_current = latest.get('Volume', np.nan)
    volume_ma = latest.get('Volume_MA', np.nan)
    ma200 = latest.get('200_MA', np.nan)

    analysis_results['Interpretation'] = {
        'Trend': 'Bullish' if (ma200 is not np.nan and current_close > ma200) else 'Bearish',
        'RSI': (
            'Overbought' if rsi_val > 70 else
            'Oversold' if rsi_val < 30 else
            'Neutral'
        ),
        'MACD': 'Bullish' if macd_val > signal_line_val else 'Bearish',
        'Stochastic': (
            'Overbought' if k_val > 80 else
            'Oversold' if k_val < 20 else
            'Neutral'
        ),
        'Bollinger_Bands': (
            'Overbought' if current_close > boll_upper else
            'Oversold' if current_close < boll_lower else
            'Neutral'
        ),
        'Volume': (
            'High' if (volume_ma is not np.nan and volume_current > volume_ma)
            else 'Low'
        )
    }

    #Let's retun the data as a json object
    #analysis_results['DataFrame'] = data.to_json()

    return analysis_results


# ----------------------------------------------------------------------
#  Potential Plotting Function (commented out, for reference only)
# ----------------------------------------------------------------------
# def plot_technical_analysis(data: pd.DataFrame, ticker: str = ""):
#     """
#     Example of a multi-panel Matplotlib figure displaying key indicators.
#     """
#     import matplotlib.pyplot as plt
#     if data.empty:
#         print("No data to plot.")
#         return

#     plt.style.use('seaborn')
#     fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
#     fig.suptitle(f"{ticker} Technical Analysis", fontsize=16, y=0.95)

#     # 1) Price + Bollinger Bands + MAs
#     ax1 = axes[0]
#     ax1.plot(data.index, data['Close'], label='Close', color='blue', linewidth=1)
#     if 'Upper_BB' in data.columns and 'Lower_BB' in data.columns:
#         ax1.plot(data.index, data['Upper_BB'], label='Upper BB', color='orange', linewidth=1)
#         ax1.plot(data.index, data['Lower_BB'], label='Lower BB', color='orange', linewidth=1)
#         ax1.fill_between(data.index, data['Lower_BB'], data['Upper_BB'], color='orange', alpha=0.1)

#     # Plot MAs if they exist
#     for ma_days, ma_color in zip([20, 50, 100, 200], ['purple', 'green', 'red', 'black']):
#         ma_col = f'{ma_days}_MA'
#         if ma_col in data.columns:
#             ax1.plot(data.index, data[ma_col], label=f"{ma_days} MA", color=ma_color, linewidth=1)

#     ax1.set_ylabel('Price')
#     ax1.set_title("Price & Bollinger Bands")
#     ax1.legend(loc='upper left')

#     # 2) Volume
#     ax2 = axes[1]
#     ax2.bar(data.index, data['Volume'], label='Volume', color='gray', width=1)
#     if 'Volume_MA' in data.columns:
#         ax2.plot(data.index, data['Volume_MA'], label='Volume MA', color='blue', linewidth=1)
#     ax2.set_ylabel('Volume')
#     ax2.set_title("Volume")
#     ax2.legend(loc='upper left')

#     # 3) MACD
#     ax3 = axes[2]
#     if {'MACD', 'Signal_Line', 'MACD_Histogram'}.issubset(data.columns):
#         ax3.plot(data.index, data['MACD'], label='MACD', color='blue')
#         ax3.plot(data.index, data['Signal_Line'], label='Signal Line', color='red')
#         ax3.bar(data.index, data['MACD_Histogram'], label='MACD Hist', color='green', alpha=0.3)
#         ax3.set_title('MACD')
#         ax3.legend(loc='upper left')

#     # 4) RSI
#     ax4 = axes[3]
#     if 'RSI' in data.columns:
#         ax4.plot(data.index, data['RSI'], label='RSI', color='blue')
#         ax4.axhline(70, color='red', linestyle='--', linewidth=1)
#         ax4.axhline(30, color='green', linestyle='--', linewidth=1)
#         ax4.set_title('RSI')
#         ax4.set_ylabel('RSI Value')
#         ax4.legend(loc='upper left')

#     plt.tight_layout()
#     plt.show()


# ----------------------------------------------
#  If running this script directly:
# ----------------------------------------------
if __name__ == "__main__":
    results = yf_tech_analysis("AAPL", "1y")

    # Print a summary of the analysis
    print("\nTechnical Analysis Results for AAPL over 1y:\n")
    for key, value in results.items():
        if key == 'DataFrame':
            print(f"{key}: <DataFrame with shape {value.shape}>")
        else:
            print(f"{key}: {value}")

    # If you want to test plotting, you can uncomment the function call:
    # df = results['DataFrame']
    # plot_technical_analysis(df, ticker="AAPL")
