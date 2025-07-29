import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# ---------------------------------------
# Functions
# ---------------------------------------

def get_stock_data(ticker, period="1d", interval="1m"):
    """Fetch real-time stock data using yfinance"""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)

def add_indicators(df):
    """Add SMA and EMA indicators"""
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    return df

def plot_candlestick(df, ticker):
    """Plot candlestick chart with indicators"""
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Price"
    ))

    # SMA & EMA
    if 'SMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1.5), name='SMA 20'))
    if 'EMA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1.5), name='EMA 20'))

    fig.update_layout(
        title=f"{ticker} - Real-Time Candlestick Chart",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=600
    )
    return fig

# ---------------------------------------
# Streamlit App
# ---------------------------------------

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL").upper()
refresh_rate = st.sidebar.slider("Refresh Rate (seconds):", 5, 60, 15)

# Countdown placeholder
countdown_placeholder = st.empty()

# Load data
try:
    df = get_stock_data(ticker)
    if df.empty:
        st.warning("No data available. Try a different ticker or interval.")
    else:
        df = add_indicators(df)

        # Metrics
        latest_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change = latest_close - prev_close
        pct_change = (change / prev_close) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Price", f"${latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
        col2.metric("Day High", f"${df['High'].iloc[-1]:.2f}")
        col3.metric("Day Low", f"${df['Low'].iloc[-1]:.2f}")

        # Candlestick chart
        st.plotly_chart(plot_candlestick(df, ticker), use_container_width=True)

        # Show last 5 data rows
        st.subheader("📊 Latest Data")
        st.dataframe(df.tail())

        # Countdown and refresh
        for i in range(refresh_rate, 0, -1):
            countdown_placeholder.markdown(f"⏳ **Refreshing in {i} seconds...**")
            time.sleep(1)

        st.experimental_rerun()

except Exception as e:
    st.error(f"Error: {e}")
