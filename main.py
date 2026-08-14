"""Stage 0 — CLI entry point for the quant signal screener."""

import argparse

from rich.console import Console
from rich.table import Table

from tools.screener import screen_watchlist

DEFAULT_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Screen a watchlist for technical trade signals.")
    parser.add_argument(
        "tickers",
        nargs="*",
        default=DEFAULT_WATCHLIST,
        help=f"Tickers or company names to screen (default: {' '.join(DEFAULT_WATCHLIST)})",
    )
    parser.add_argument("--period", default="6mo", help="Lookback window, e.g. 1mo, 6mo, 1y (default: 6mo)")
    parser.add_argument("--interval", default="1d", help="Bar size, e.g. 1d, 1h, 1wk (default: 1d)")
    return parser.parse_args()


def render(df) -> None:
    console = Console()
    table = Table(title="Quant Signal Screener")

    for col in ["ticker", "close", "signal", "score", "reasons"]:
        table.add_column(col)

    signal_style = {"BUY": "green", "SELL": "red", "HOLD": "yellow", "ERROR": "dim"}
    for _, row in df.iterrows():
        style = signal_style.get(row["signal"], "")
        table.add_row(
            row["ticker"],
            "" if row["close"] is None else f"{row['close']:.2f}",
            f"[{style}]{row['signal']}[/{style}]" if style else row["signal"],
            str(row["score"]),
            row["reasons"],
        )

    console.print(table)


def main() -> None:
    args = parse_args()
    df = screen_watchlist(args.tickers, period=args.period, interval=args.interval)
    render(df)


if __name__ == "__main__":
    main()