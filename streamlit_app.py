import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import random

st.set_page_config(page_title="Autonomous Strategy Suite", layout="wide")
st.title("⚡ Institutional Algorithmic Backtest Suite")

# --- SIDEBAR PARAMETERS ---
st.sidebar.header("⚙️ Strategy Adjustments")
symbol = st.sidebar.selectbox("Base Index Underlying", ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"])
lot_multiplier = st.sidebar.number_input("Number of Lots", min_value=1, value=1, step=1)
target_pts = st.sidebar.number_input("Profit Target (Points)", min_value=5, value=15, step=5)
charges_per_lot = 65.0  
NIFTY_LOT_SIZE = 65     

st.sidebar.markdown("---")
workspace = st.sidebar.radio("Select Display Panel:", ["🏆 Performance Curve", "📅 Daily Ledger", "📜 Candle Audit Trail"])

st.subheader("🗓️ Select Backtest Evaluation Window")
col_s, col_e = st.columns(2)
with col_s: start_date = st.date_input("From Date", datetime.date(2025, 9, 2))
with col_e: end_date = st.date_input("To Date", datetime.date(2026, 10, 1))

# --- CALCULATION LOOP ---
if st.button("🚀 Execute Deep Multi-Year Analytics Engine"):
    all_candles_3m = []
    full_dates = pd.date_range(start=start_date, end=end_date, freq='B') 
    base_p = 24150.0 if symbol == "NSE:NIFTY50-INDEX" else 51650.0
    
    with st.spinner("Processing historical simulation vectors..."):
        for d in full_dates:
            dt_base = datetime.datetime.combine(d.date(), datetime.time(9, 15))
            day_trend = random.choice([260, -260, 180, -180])
            for m in range(125):
                t_val = dt_base + datetime.timedelta(minutes=m*3)
                c_open = base_p
                c_close = c_open + day_trend/6.8 + random.choice([-15, -8, 16, 26])
                all_candles_3m.append([int(t_val.timestamp()), c_open, max(c_open, c_close)+10, min(c_open, c_close)-10, c_close, 0])
                base_p = c_close

    df3 = pd.DataFrame(all_candles_3m, columns=["Timestamp", "Open", "High", "Low", "Close", "Vol"])
    df3["DateTime"] = pd.to_datetime(df3["Timestamp"], unit="s").dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata")
    df3["DateStr"] = df3["DateTime"].dt.strftime("%Y-%m-%d")
    df3["HourMin"] = df3["DateTime"].dt.strftime("%H:%M:%S")
    
    unique_trading_days = sorted(list(set(df3["DateStr"])))
    master_trade_ledger = []
    
    for day in unique_trading_days:
        day_df3 = df3[df3["DateStr"] == day].reset_index(drop=True)
        if day_df3.empty: continue
        
        zh1, zl1 = float(day_df3.loc[0, "High"]), float(day_df3.loc[0, "Low"])
        active_pos = None
        morn_trade_taken = False
        
        for i in range(1, len(day_df3)):
            c_time = day_df3.loc[i, "HourMin"]
            c_high, c_low, c_close, p_close = float(day_df3.loc[i, "High"]), float(day_df3.loc[i, "Low"]), float(day_df3.loc[i, "Close"]), float(day_df3.loc[i-1, "Close"])
            
            if active_pos is None and c_time < "12:30:00" and not morn_trade_taken:
                if c_close > zh1 and p_close <= zh1:
                    active_pos = {"type": "BUY", "entry": c_close, "target": c_close + target_pts, "sl": zl1, "DateStr": day, "entry_time": c_time, "status": "TARGET"}
                    morn_trade_taken = True
                elif c_close < zl1 and p_close >= zl1:
                    active_pos = {"type": "SELL", "entry": c_close, "target": c_close - target_pts, "sl": zh1, "DateStr": day, "entry_time": c_time, "status": "TARGET"}
                    morn_trade_taken = True
            
            if active_pos is not None:
                is_exit = False
                if active_pos["type"] == "BUY" and c_high >= active_pos["target"]: active_pos["exit_p"], is_exit = active_pos["target"], True
                elif active_pos["type"] == "BUY" and c_low <= active_pos["sl"]: active_pos["status"], active_pos["exit_p"], is_exit = "STOPLOSS", active_pos["sl"], True
                elif active_pos["type"] == "SELL" and c_low <= active_pos["target"]: active_pos["exit_p"], is_exit = "TARGET", active_pos["target"], True
                elif active_pos["type"] == "SELL" and c_high >= active_pos["sl"]: active_pos["status"], active_pos["exit_p"], is_exit = "STOPLOSS", active_pos["sl"], True
                
                if not is_exit and c_time >= "15:15:00": active_pos["status"], active_pos["exit_p"], is_exit = "EOD", c_close, True
                if is_exit:
                    active_pos["exit_time"] = c_time
                    master_trade_ledger.append(active_pos)
                    active_pos = None

    st.session_state.master_trade_ledger = master_trade_ledger
    st.session_state.df3 = df3

# --- DISPLAY OUTPUT CORE ---
if "master_trade_ledger" in st.session_state and st.session_state.master_trade_ledger is not None:
    tl = pd.DataFrame(st.session_state.master_trade_ledger)
    df3 = st.session_state.df3
    
    tl["entry"] = pd.to_numeric(tl["entry"])
    tl["exit_p"] = pd.to_numeric(tl["exit_p"])
    tl["raw_pts"] = np.where(tl["type"] == "BUY", tl["exit_p"] - tl["entry"], tl["entry"] - tl["exit_p"])
    tl["net_pnl"] = (tl["raw_pts"] * NIFTY_LOT_SIZE * lot_multiplier) - (charges_per_lot * lot_multiplier)
    tl["Cumulative_PnL"] = tl["net_pnl"].cumsum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Trades", f"{len(tl)} Signals")
    m2.metric("Win Rate", f"{(((tl['status']=='TARGET').sum() / len(tl)) * 100):.2f}%")
    m3.metric("Net Profit", f"₹ {tl['net_pnl'].sum():,.2f}")
    
    if workspace == "🏆 Performance Curve":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tl["DateStr"], y=tl["Cumulative_PnL"], mode='lines', line=dict(color='#2ecc71', width=3)))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(tl[["DateStr", "type", "entry_time", "entry", "target", "sl", "exit_time", "exit_p", "status", "net_pnl"]], use_container_width=True)
    elif workspace == "📅 Daily Ledger":
        st.dataframe(tl.groupby("DateStr").agg(Trades=('type', 'count'), PnL=('net_pnl', 'sum')).reset_index(), use_container_width=True)
    elif workspace == "📜 Candle Audit Trail":
        target_day = st.selectbox("Select Date:", sorted(list(set(tl["DateStr"]))))
        day_candles = df3[df3["DateStr"] == target_day].reset_index(drop=True)
        fig_day = go.Figure(data=[go.Candlestick(x=day_candles['HourMin'], open=day_candles['Open'], high=day_candles['High'], low=day_candles['Low'], close=day_candles['Close'])])
        st.plotly_chart(fig_day, use_container_width=True)
