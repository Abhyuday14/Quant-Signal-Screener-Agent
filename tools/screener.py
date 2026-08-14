"""Stage 0 — rule-based multi-ticker screener."""

import pandas as pd

from tools.data import get_price_history
from tools.indicators import compute_indicators


def _score_row(row: pd.Series) -> tuple[int, list[str]]:
    """Score the latest bar across trend/momentum/volatility signals.

    Returns a tuple of (score, reasons). Score ranges roughly -4..+4;
    positive is bullish, negative is bearish.
    """
    score = 0
    reasons: list[str] = []

    if pd.notna(row["SMA20"]) and pd.notna(row["SMA50"]):
        if row["SMA20"] > row["SMA50"]:
            score += 1
            reasons.append("SMA20>SMA50 (uptrend)")
        else:
            score -= 1
            reasons.append("SMA20<SMA50 (downtrend)")

    if pd.notna(row["RSI14"]):
        if row["RSI14"] < 30:
            score += 1
            reasons.append(f"RSI {row['RSI14']:.0f} oversold")
        elif row["RSI14"] > 70:
            score -= 1
            reasons.append(f"RSI {row['RSI14']:.0f} overbought")

    if pd.notna(row["MACD"]) and pd.notna(row["MACD_signal"]):
        if row["MACD"] > row["MACD_signal"]:
            score += 1
            reasons.append("MACD>signal (bullish)")
        else:
            score -= 1
            reasons.append("MACD<signal (bearish)")

    if pd.notna(row["BB_lower"]) and pd.notna(row["BB_upper"]):
        if row["Close"] <= row["BB_lower"]:
            score += 1
            reasons.append("price at/below lower band")
        elif row["Close"] >= row["BB_upper"]:
            score -= 1
            reasons.append("price at/above upper band")

    return score, reasons


def _verdict(score: int) -> str:
    if score >= 2:
        return "BUY"
    if score <= -2:
        return "SELL"
    return "HOLD"


def screen_watchlist(
    tickers: list[str], period: str = "6mo", interval: str = "1d"
) -> pd.DataFrame:
    """Run the indicator-based screener across a list of tickers.

    Args:
        tickers: Symbols to screen, e.g. ["AAPL", "MSFT"].
        period: yfinance lookback window passed to get_price_history.
        interval: Bar size passed to get_price_history.

    Returns:
        DataFrame with one row per ticker: ticker, close, signal, score,
        reasons. Tickers that fail to fetch are included with an "ERROR"
        signal and the failure reason instead.
    """
    rows = []
    for ticker in tickers:
        try:
            df = get_price_history(ticker, period=period, interval=interval)
            df = compute_indicators(df)
            latest = df.iloc[-1]
            score, reasons = _score_row(latest)
            rows.append(
                {
                    "ticker": ticker.upper(),
                    "close": round(float(latest["Close"]), 2),
                    "signal": _verdict(score),
                    "score": score,
                    "reasons": "; ".join(reasons) if reasons else "no signal",
                }
            )
        except Exception as exc:  # noqa: BLE001 - surface per-ticker failures, don't abort the batch
            rows.append(
                {
                    "ticker": ticker.upper(),
                    "close": None,
                    "signal": "ERROR",
                    "score": 0,
                    "reasons": str(exc),
                }
            )

    result = pd.DataFrame(rows)
    return result.sort_values("score", ascending=False).reset_index(drop=True)