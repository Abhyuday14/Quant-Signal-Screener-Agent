"""Stage 0 — resolve company names or loose symbols to Yahoo Finance tickers."""

import re
from functools import lru_cache

import yfinance as yf

_TICKER_RE = re.compile(r"^[A-Z0-9.\-&]{1,15}$")

# Exchange codes to prefer when a name is ambiguous across markets
# (e.g. "Infosys" also has a US-listed ADR under a different symbol).
_INDIA_EXCHANGES = ("NSI", "BSE")


def _looks_like_ticker(query: str) -> bool:
    return bool(_TICKER_RE.match(query.strip().upper()))


@lru_cache(maxsize=256)
def resolve_ticker(query: str, prefer_india: bool = True) -> str:
    """Resolve a company name or bare symbol to a Yahoo Finance ticker.

    Args:
        query: A ticker (e.g. "TCS.NS") or company name (e.g. "Tata Consultancy").
        prefer_india: When a name matches companies on multiple exchanges,
            prefer the NSE/BSE listing over others (e.g. US ADRs).

    Returns:
        A Yahoo Finance ticker symbol.

    Raises:
        ValueError: If no matching symbol can be found.
    """
    query = query.strip()
    if not query:
        raise ValueError("Empty ticker/company name")

    try:
        candidates = [
            c
            for c in yf.Search(query, max_results=8).quotes
            if c.get("symbol") and c.get("quoteType") == "EQUITY"
        ]
    except Exception:
        # Search endpoint unavailable — fall back to the literal input if it
        # already looks like a ticker, otherwise give up.
        if _looks_like_ticker(query):
            return query.upper()
        raise ValueError(f"Could not resolve '{query}' to a ticker symbol (search unavailable)")

    if _looks_like_ticker(query):
        exact = next((c for c in candidates if c["symbol"].upper() == query.upper()), None)
        if exact:
            return exact["symbol"]
        if not candidates:
            return query.upper()

    if not candidates:
        raise ValueError(f"Could not resolve '{query}' to a ticker symbol")

    if prefer_india:
        for exch in _INDIA_EXCHANGES:
            match = next((c for c in candidates if c.get("exchange") == exch), None)
            if match:
                return match["symbol"]

    return candidates[0]["symbol"]
