"""Stage 0 — market data access."""

import pandas as pd
import yfinance as yf


def get_price_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV price history for a single ticker.

    Args:
        ticker: Symbol, e.g. "AAPL".
        period: yfinance lookback window, e.g. "1mo", "6mo", "1y", "5y".
        interval: Bar size, e.g. "1d", "1h", "1wk".I wnat 

    Returns:
        DataFrame indexed by date with columns: Open, High, Low, Close, Volume.

    Raises:
        ValueError: If no data is returned for the ticker.
    """
    df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No price data returned for '{ticker}' (period={period}, interval={interval})")

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index.name = "Date"
    # Drop trailing bars for sessions still in progress (yfinance sometimes
    # returns a row with volume but no OHLC for the current, unsettled bar).
    df = df.dropna(subset=["Close"])
    if df.empty:
        raise ValueError(f"No settled price data for '{ticker}' (period={period}, interval={interval})")
    return df