"""Stage 1 — LangChain @tool wrappers around the Stage 0 functions."""

import pandas as pd
from langchain_core.tools import tool

from tools.data import get_price_history
from tools.indicators import compute_indicators
from tools.screener import screen_watchlist


def _df_to_markdown(df: pd.DataFrame, max_rows: int = 15) -> str:
    return df.tail(max_rows).round(4).to_markdown()


@tool
def price_history_tool(ticker: str, period: str = "6mo", interval: str = "1d") -> str:
    """Get recent OHLCV price history for a single stock ticker.

    Args:
        ticker: Symbol, e.g. "AAPL".
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    df = get_price_history(ticker, period=period, interval=interval)
    return _df_to_markdown(df)


@tool
def indicators_tool(ticker: str, period: str = "6mo", interval: str = "1d") -> str:
    """Compute technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands) for a ticker.

    Args:
        ticker: Symbol, e.g. "AAPL".
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    df = get_price_history(ticker, period=period, interval=interval)
    df = compute_indicators(df)
    return _df_to_markdown(df)


@tool
def screener_tool(tickers: list[str], period: str = "6mo", interval: str = "1d") -> str:
    """Screen a list of stock tickers and return a BUY/SELL/HOLD signal for each.

    Args:
        tickers: Symbols to screen, e.g. ["AAPL", "MSFT"].
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    df = screen_watchlist(tickers, period=period, interval=interval)
    return df.to_markdown(index=False)


ALL_TOOLS = [price_history_tool, indicators_tool, screener_tool]