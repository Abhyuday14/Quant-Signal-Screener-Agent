"""Stage 1 — LangChain @tool wrappers around the Stage 0 functions."""

import pandas as pd
from langchain_core.tools import tool

from tools.data import get_price_history
from tools.indicators import compute_indicators
from tools.resolver import resolve_ticker
from tools.screener import screen_watchlist


def _df_to_markdown(df: pd.DataFrame, max_rows: int = 15) -> str:
    return df.tail(max_rows).round(4).to_markdown()


@tool
def price_history_tool(ticker: str, period: str = "6mo", interval: str = "1d") -> str:
    """Get recent OHLCV price history for a single stock.

    Args:
        ticker: Symbol or company name, e.g. "AAPL" or "Apple". Bare names
            resolve to their NSE/BSE listing by default when the company
            trades in India (e.g. "TCS", "Reliance", "HDFC Bank").
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    resolved = resolve_ticker(ticker)
    df = get_price_history(resolved, period=period, interval=interval)
    return f"Resolved '{ticker}' -> {resolved}\n\n" + _df_to_markdown(df)


@tool
def indicators_tool(ticker: str, period: str = "6mo", interval: str = "1d") -> str:
    """Compute technical indicators (SMA, EMA, MACD, RSI, Bollinger Bands) for a stock.

    Args:
        ticker: Symbol or company name, e.g. "AAPL" or "Apple". Bare names
            resolve to their NSE/BSE listing by default when the company
            trades in India (e.g. "TCS", "Reliance", "HDFC Bank").
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    resolved = resolve_ticker(ticker)
    df = get_price_history(resolved, period=period, interval=interval)
    df = compute_indicators(df)
    return f"Resolved '{ticker}' -> {resolved}\n\n" + _df_to_markdown(df)


@tool
def screener_tool(tickers: list[str], period: str = "6mo", interval: str = "1d") -> str:
    """Screen a list of stocks and return a BUY/SELL/HOLD signal for each.

    Args:
        tickers: Symbols or company names, e.g. ["RELIANCE", "TCS", "Infosys"]
            or ["AAPL", "MSFT"]. Bare names resolve to their NSE/BSE listing
            by default when the company trades in India.
        period: Lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".
    """
    df = screen_watchlist(tickers, period=period, interval=interval)
    return df.to_markdown(index=False)


ALL_TOOLS = [price_history_tool, indicators_tool, screener_tool]