
import streamlit as st
import pandas as pd
import time
from data_engine import get_recent_earnings_tickers, get_ticker_data
from filters import check_ep_setup, check_momentum_setup, check_swing_breakout

# Page Config
st.set_page_config(
    page_title="Qulla-Catalyst Scanner Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title & Branding
st.title("🚀 Qulla-Catalyst Scanner Pro")
st.markdown("### Algorithmic Detection of High Momentum Setups")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Scanner Settings")
    
    st.subheader("Data Source")
    earnings_lookback = st.slider("Earnings Lookback (Days)", 0, 5, 2)
    
    st.subheader("Strictness")
    min_volume_ratio = st.number_input("Min Volume Ratio (vs 20d Avg)", 1.5, 5.0, 2.0, 0.1)
    min_gap_pct = st.number_input("Min Gap %", 2.0, 20.0, 8.0, 0.5)
    
    run_btn = st.button("RUN SCANNER", type="primary")

    st.info("ℹ️ Scans Yahoo Finance Earnings Calendar + yFinance Market Data.")

# Main Logic
if run_btn:
    # 1. Get Tickers (Earnings)
    st.status("Fetching Earnings Calendar...", expanded=True)
    with st.spinner("Scraping Yahoo Finance..."):
        # tickers = ["NVDA", "TSLA", "PLTR", "AMD"] # Debug
        tickers = get_recent_earnings_tickers(days_back=earnings_lookback)
        
    st.success(f"Found {len(tickers)} potential catalyst tickers.")
    
    # 2. Process Tickers
    ep_results = []
    momentum_results = []
    swing_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"Analyzing {ticker}...")
        
        # Rate Limit
        time.sleep(1) 
        
        df = get_ticker_data(ticker)
        if df is None: 
            continue
            
        # Check EP
        is_ep, gap, vol_r = check_ep_setup(df)
        # Apply strictness overwrite if needed, or update filter logic to take params
        # For now using hardcoded logic in filters.py but let's check strictness here:
        if gap >= min_gap_pct and vol_r >= min_volume_ratio:
            ep_results.append({
                "ticker": ticker,
                "gap": gap,
                "vol_ratio": vol_r,
                "close": df.iloc[-1]['Close']
            })
            
        # Check Momentum
        if check_momentum_setup(df):
            momentum_results.append({
                "ticker": ticker,
                "adr": df.iloc[-1]['ADR_20'],
                "close": df.iloc[-1]['Close']
            })
            
        # Check Swing
        is_swing, tightness = check_swing_breakout(df)
        if is_swing:
            swing_results.append({
                "ticker": ticker,
                "tightness": tightness,
                "close": df.iloc[-1]['Close']
            })
            
        progress_bar.progress((i + 1) / len(tickers))
        
    status_text.text("Scan Complete!")
    
    # 3. Display Results (3 Columns)
    col1, col2, col3 = st.columns(3)
    
    # helper for link
    def tv_link(ticker):
        return f"https://www.tradingview.com/chart/?symbol={ticker}"
    
    with col1:
        st.header("🔥 EP ALERT")
        st.caption("Gap > 8% | Vol > 200%")
        if not ep_results:
            st.info("No EP setups found today.")
        for item in ep_results:
            with st.container(border=True):
                st.markdown(f"### **{item['ticker']}**")
                st.metric("Gap UP", f"+{item['gap']:.2f}%", f"Vol: {item['vol_ratio']:.1f}x")
                st.markdown(f"[Chart on TradingView]({tv_link(item['ticker'])})")
                
    with col2:
        st.header("🌊 MOMENTUM")
        st.caption("ADR > 4% | Trending")
        if not momentum_results:
            st.info("No Momentum setups found.")
        for item in momentum_results:
            with st.container(border=True):
                st.markdown(f"**{item['ticker']}** (${item['close']:.2f})")
                st.markdown(f"ADR: **{item['adr']:.2f}%**")
                st.markdown(f"[View Chart]({tv_link(item['ticker'])})")

    with col3:
        st.header("🚩 SWING WATCH")
        st.caption("Consolidating (> SMA50)")
        if not swing_results:
            st.info("No Swing setups found.")
        for item in swing_results:
            with st.container(border=True):
                st.markdown(f"**{item['ticker']}**")
                st.markdown(f"Tightness: **{item['tightness']:.1f}%**")
                st.markdown(f"[View Chart]({tv_link(item['ticker'])})")

else:
    st.info("👈 Adjust settings and click RUN SCANNER to start.")
