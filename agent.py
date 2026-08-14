"""Stage 1 — LangChain agent that reasons over the screener tools."""

import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from tools.langchain_tools import ALL_TOOLS

load_dotenv()

SYSTEM_PROMPT = """You are a quant signal screener assistant.

You have tools to fetch price history, compute technical indicators
(SMA, EMA, MACD, RSI, Bollinger Bands), and screen a watchlist of
tickers for BUY/SELL/HOLD signals. Use them to answer questions about
specific stocks or watchlists.

You can pass either a ticker symbol or a plain company name to these
tools (e.g. "Reliance", "TCS", "HDFC Bank") — they resolve names to
their Yahoo Finance ticker automatically, preferring the NSE/BSE
listing by default when a company trades in India. When a query is
ambiguous, mention which exchange/ticker you resolved to.

Always ground your analysis in the tool output rather than prior
knowledge of the market, since prices move daily. When you give a
signal, briefly explain the reasoning (trend, momentum, volatility).
This is not financial advice, and you should say so when a user asks
you to make a decision for them."""


def build_agent(model: str | None = None, temperature: float = 0.0) -> CompiledStateGraph:
    """Construct a tool-calling agent over the screener tools.

    Args:
        model: OpenRouter model slug, e.g. "openai/gpt-oss-20b:free".
            Defaults to the OPENROUTER_MODEL env var.
        temperature: Sampling temperature for the LLM.

    Returns:
        A LangGraph agent ready to `.invoke({"messages": [...]})`.

    Raises:
        RuntimeError: If OPENROUTER_API_KEY is not set.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file."
        )
    model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    return create_agent(llm, ALL_TOOLS, system_prompt=SYSTEM_PROMPT)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    agent = build_agent()
    print("Quant Signal Screener Agent — type 'exit' to quit.\n")

    messages: list = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        messages.append(("human", user_input))
        result = agent.invoke({"messages": messages})
        messages = result["messages"]
        print(f"\nAgent: {messages[-1].content}\n")


if __name__ == "__main__":
    main()
