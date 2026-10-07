import subprocess
import sys

# Force-install plotly on runtime startup to bypass strict uv lock layers completely
try:
    import plotly
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import random
import time

# Force-clear visual memory layers out of browser context on startup
st.cache_data.clear()

st.set_page_config(page_title="Institutional Trading Terminal", layout="wide")
st.title("⚡ Live Institutional Algorithmic Trading Terminal Suite")

# --- INITIALIZE STATE REGISTERS ---
if "live_logs" not in st.session_state: st.session_state.live_logs = []
if "live_trading_active" not in st.session_state: st.session_state.live_trading_active = False

# --- SIDEBAR STRATEGY & RISK CONTROLS ---
st.sidebar.header("🕹️ Operational Panel Controls")
symbol = st.sidebar.selectbox("Base Index Underlying", ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"])
lot_multiplier = st.sidebar.number_input("Number of Lots", min_value=1, value=1, step=1)
target_pts = st.sidebar.number_input("Profit Target (Points)", min_value=5, value=15, step=5)
required_pcr = st.sidebar.slider("Minimum Bullish PCR Filter Threshold", 0.5, 2.0, 1.1, 0.1)

def calculate_ema(series, periods):
    return series.ewm(span=periods, adjust=False).mean()

# --- RE-EXECUTION LAYOUT GRID PANELS ---
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🟢 Start Live Algorithmic Scanning Engine"):
        st.session_state.live_trading_active = True
        st.session_state.live_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Core indicator matrix scanning sequence armed.")
with col_btn2:
    if st.button("🔴 Emergency Stop & Order Block"):
        st.session_state.live_trading_active = False
        st.session_state.live_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] EMERGENCY TRACKING SYSTEM SHUT DOWN.")

# --- LIVE SIMULATED DATA PATH GENERATOR ---
mock_prices = [24150.0]
for _ in range(200): mock_prices.append(mock_prices[-1] + random.uniform(-4, 4.2))
df_market = pd.DataFrame(mock_prices, columns=["Close"])
df_market["High"] = df_market["Close"] + 3
df_market["Low"] = df_market["Close"] - 3
df_market["Open"] = df_market["Close"].shift(1).fillna(24150.0)
df_market["Volume"] = [random.randint(500, 5000) for _ in range(len(df_market))]

df_market["EMA_50"] = calculate_ema(df_market["Close"], 50)
df_market["EMA_200"] = calculate_ema(df_market["Close"], 200)

# --- CENTRAL PIVOT RANGE (CPR) CALCULATION ---
prev_high = 24190.0
prev_low = 24120.0
prev_close = 24160.0

pivot = (prev_high + prev_low + prev_close) / 3.0
bc = (prev_high + prev_low) / 2.0
tc = (pivot - bc) + pivot

cpr_high = max(tc, bc)
cpr_low = min(tc, bc)
cpr_width = cpr_high - cpr_low

latest_tick = df_market.iloc[-1]
prev_tick = df_market.iloc[-2]

current_price = float(latest_tick["Close"])
ema50_val = float(latest_tick["EMA_50"])
ema200_val = float(latest_tick["EMA_200"])
current_vol = float(latest_tick["Volume"])
prev_vol = float(prev_tick["Volume"])

mock_call_oi = random.randint(1200000, 1800000)
mock_put_oi = random.randint(1300000, 2100000)
live_pcr_ratio = mock_put_oi / mock_call_oi

# --- 🚦 VISUAL CONFIRMATION CHECKLIST MATRIX ---
st.markdown("### 🚦 Live Strategy Order Confirmation Matrix")
col_c1, col_c2, col_c3, col_c4 = st.columns(4)

with col_c1:
    pcr_confirmed = live_pcr_ratio >= required_pcr
    st.metric("Option Chain PCR Ratio", f"{live_pcr_ratio:.2f}", f"Target: >= {required_pcr}")
    if pcr_confirmed: st.success("🟢 PCR CONFIRMED")
    else: st.error("❌ PCR BLOCKED")

with col_c2:
    vol_spike_ratio = current_vol / prev_vol
    vol_confirmed = vol_spike_ratio >= 1.3
    st.metric("Volume Momentum Ratio", f"{vol_spike_ratio:.2f}x", f"Current Bar: {int(current_vol)}")
    if vol_confirmed: st.success("🟢 VOLUME CONFIRMED")
    else: st.warning("⚠️ VOLUME LOW")

with col_c3:
    ema_confirmed = current_price > ema50_val and current_price > ema200_val
    dist_to_ema50 = current_price - ema50_val
    st.metric("Spot to 50 EMA Line", f"{dist_to_ema50:+.2f} Pts", f"50 EMA: {ema50_val:.1f}")
    if ema_confirmed: st.success("🟢 EMA TREND CONFIRMED")
    else: st.error("❌ EMA BLOCKED")

with col_c4:
    is_outside_cpr = (current_price > cpr_high) or (current_price < cpr_low)
    cpr_trend_type = "Narrow (Breakout Day)" if cpr_width < 25 else "Wide (Sideways Day)"
    st.metric("CPR Channel Width Profile", f"{cpr_width:.1f} Pts", cpr_trend_type)
    if is_outside_cpr: st.success("🟢 CPR CONFIRMED")
    else: st.error("❌ CPR BLOCKED")

# --- AUTOMATED SIMULATED DISPATCH DECISION GATE ---
if st.session_state.live_trading_active:
    st.session_state.live_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Scan Check -> Price: {current_price:.2f} | Inside CPR: {not is_outside_cpr}")
    if pcr_confirmed and vol_confirmed and ema_confirmed and is_outside_cpr:
        st.session_state.live_logs.append(f"🎯 🔥 [ALL INDICATORS ALIGNED] Order Conformed! Firing Simulated Market Order to Trade Book...")
        st.session_state.live_trading_active = False

# --- RENDER CHARTS & CONSOLE LOGGER ---
st.markdown("### 📈 Real-Time Indicator & Central Pivot Range Chart Layout")
fig_live = go.Figure(data=[go.Candlestick(x=df_market.index[-40:], open=df_market['Open'].tail(40), high=df_market['High'].tail(40), low=df_market['Low'].tail(40), close=df_market['Close'].tail(40), name="Price Path")])

fig_live.add_trace(go.Scatter(x=df_market.index[-40:], y=[tc]*40, line=dict(color='cyan', width=1.5, dash='dash'), name="CPR TC"))
fig_live.add_trace(go.Scatter(x=df_market.index[-40:], y=[pivot]*40, line=dict(color='magenta', width=2), name="CPR Pivot"))
fig_live.add_trace(go.Scatter(x=df_market.index[-40:], y=[bc]*40, line=dict(color='cyan', width=1.5, dash='dash'), name="CPR BC"))
fig_live.add_trace(go.Scatter(x=df_market.index[-40:], y=df_market['EMA_50'].tail(40), line=dict(color='orange', width=2), name="50 EMA"))
fig_live.add_trace(go.Scatter(x=df_market.index[-40:], y=df_market['EMA_200'].tail(40), line=dict(color='purple', width=2), name="200 EMA"))

fig_live.update_layout(xaxis_rangeslider_visible=False, height=450)
st.plotly_chart(fig_live, use_container_width=True)

st.markdown("### 📜 Real-Time System Diagnostic Console Logs")
for log_line in reversed(st.session_state.live_logs[-12:]): st.text(log_line)

if st.session_state.live_trading_active:
    time.sleep(2)
    st.rerun()
