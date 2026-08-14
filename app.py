"""Stage 2 — Streamlit UI for the quant signal screener."""

import streamlit as st

from agent import build_agent
from tools.screener import screen_watchlist

st.set_page_config(page_title="Quant Signal Screener", layout="wide")
st.title("Quant Signal Screener")

with st.sidebar:
    st.header("Watchlist")
    tickers_input = st.text_area(
        "Tickers or company names (comma-separated)",
        value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS",
        help='Company names work too, e.g. "Reliance, TCS, Infosys" — '
        "they resolve to their NSE/BSE listing by default.",
    )
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    interval = st.selectbox("Interval", ["1d", "1h", "1wk"], index=0)
    run_clicked = st.button("Run screener", type="primary")

if "screener_df" not in st.session_state:
    st.session_state.screener_df = None

if run_clicked:
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    with st.spinner("Fetching data and computing signals..."):
        st.session_state.screener_df = screen_watchlist(tickers, period=period, interval=interval)

if st.session_state.screener_df is not None:
    df = st.session_state.screener_df

    def highlight_signal(row):
        color = {"BUY": "#1f7a1f", "SELL": "#a33", "HOLD": "#a68a00", "ERROR": "#666"}.get(row["signal"], "")
        return [f"background-color: {color}; color: white" if col == "signal" else "" for col in row.index]

    st.dataframe(df.style.apply(highlight_signal, axis=1), use_container_width=True)
else:
    st.info("Set a watchlist in the sidebar and click **Run screener** to get started.")

st.divider()
st.header("Ask the agent")
st.caption(
    "Chat with an LLM agent that can pull price history, compute indicators, and screen "
    "tickers on its own. Company names work too, e.g. \"What's the RSI on Tata Motors?\""
)

if "agent" not in st.session_state:
    try:
        st.session_state.agent = build_agent()
        st.session_state.agent_error = None
    except RuntimeError as exc:
        st.session_state.agent = None
        st.session_state.agent_error = str(exc)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.agent_error:
    st.warning(st.session_state.agent_error)
else:
    for message in st.session_state.messages:
        if message.type not in {"human", "ai"} or not message.content:
            continue
        with st.chat_message(message.type):
            st.markdown(message.content)

    if user_input := st.chat_input("e.g. What's the RSI on NVDA right now?"):
        with st.chat_message("human"):
            st.markdown(user_input)

        with st.chat_message("ai"):
            with st.spinner("Thinking..."):
                result = st.session_state.agent.invoke(
                    {"messages": st.session_state.messages + [("human", user_input)]}
                )
            reply = result["messages"][-1].content
            st.markdown(reply)
        st.session_state.messages = result["messages"]