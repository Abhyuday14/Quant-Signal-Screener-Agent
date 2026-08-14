"""Stage 0 — technical indicator calculations."""

import pandas as pd


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.where(avg_loss != 0, 100.0)


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add trend/momentum/volatility indicators to an OHLCV DataFrame.

    Args:
        df: DataFrame with at least a "Close" column, as returned by
            tools.data.get_price_history.

    Returns:
        A copy of df with added columns: SMA20, SMA50, EMA12, EMA26,
        MACD, MACD_signal, MACD_hist, RSI14, BB_mid, BB_upper, BB_lower.
    """
    out = df.copy()
    close = out["Close"]

    out["SMA20"] = close.rolling(window=20).mean()
    out["SMA50"] = close.rolling(window=50).mean()

    out["EMA12"] = close.ewm(span=12, adjust=False).mean()
    out["EMA26"] = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = out["EMA12"] - out["EMA26"]
    out["MACD_signal"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_hist"] = out["MACD"] - out["MACD_signal"]

    out["RSI14"] = _rsi(close, window=14)

    bb_mid = close.rolling(window=20).mean()
    bb_std = close.rolling(window=20).std()
    out["BB_mid"] = bb_mid
    out["BB_upper"] = bb_mid + 2 * bb_std
    out["BB_lower"] = bb_mid - 2 * bb_std

    return out