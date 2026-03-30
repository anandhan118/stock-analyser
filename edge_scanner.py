"""
╔══════════════════════════════════════════════════════════════╗
║           EDGE SCANNER — NSE Swing Trading System           ║
║        Streamlit App | yfinance | Nifty 200 Analysis        ║
╚══════════════════════════════════════════════════════════════╝
HOW TO RUN:
    streamlit run edge_scanner.py
REQUIRES:
    pip install streamlit yfinance pandas plotly openpyxl
"""

import io
import json
import os
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Edge Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>

/* ===== GLOBAL ===== */
.main, .stApp {
    background-color: #f4f8ff;
    color: #000000;
}

/* ===== SIDEBAR ===== */
div[data-testid="stSidebar"] {
    background-color: #eaf2ff;
    border-right: 1px solid #c7d7f2;
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    color: #1e3a8a !important;
}

/* ===== TEXT ===== */
body, p, span, label {
    color: #000000 !important;
}

/* ===== INPUT BOXES (FIXES YOUR DARK ISSUE) ===== */
input, textarea, .stNumberInput input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #c7d7f2 !important;
}

/* SELECTBOX */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* ===== BUTTON ===== */
.stButton button {
    background: #2563eb;
    color: white;
    border-radius: 6px;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background: #1d4ed8;
}

/* ===== METRIC CARDS ===== */
.metric-card {
    background: #ffffff;
    border: 1px solid #dbe7ff;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.metric-num {
    font-size: 28px;
    font-weight: 700;
    color: #2563eb;
}

.metric-lbl {
    font-size: 11px;
    color: #334155;
}

/* ===== DATAFRAME FIX ===== */
div[data-testid="stDataFrame"] {
    background: white !important;
    color: black !important;
}

/* ===== TABLE TEXT ===== */
thead, tbody, tr, td, th {
    color: black !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab"] {
    color: #334155;
}

.stTabs [aria-selected="true"] {
    background: #dbeafe !important;
    color: #1d4ed8 !important;
    border-bottom: 2px solid #2563eb;
}

/* ===== INFO BOX ===== */
.info-box {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    padding: 10px;
    border-radius: 6px;
    color: black;
}

/* ===== WARNING BOX ===== */
.warn-box {
    background: #fff7ed;
    border-left: 4px solid #f97316;
    padding: 10px;
    border-radius: 6px;
    color: black;
}

# ── Nifty 200 Symbols ─────────────────────────────────────────
</style>
""", unsafe_allow_html=True)

NIFTY200 = [
    "360ONE","ABB","ACC","APLAPOLLO","AUBANK","ADANIENSOL","ADANIENT","ADANIGREEN",
    "ADANIPORTS","ADANIPOWER","ATGL","ABCAPITAL","ALKEM","AMBUJACEM","APOLLOHOSP",
    "APOLLOTYRE","ASHOKLEY","ASIANPAINT","ASTRAL","ATUL","AUROPHARMA","AXISBANK",
    "BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BANDHANBNK","BANKBARODA",
    "BANKINDIA","BATAINDIA","BEL","BERGEPAINT","BHARATFORG","BHARTIARTL","BHEL",
    "BIOCON","BOSCHLTD","BPCL","BRITANNIA","CANBK","CANFINHOME","CDSL","CESC",
    "CGPOWER","CHAMBLFERT","CHOLAFIN","CIPLA","COALINDIA","COFORGE","COLPAL",
    "CONCOR","COROMANDEL","CROMPTON","CUB","CUMMINSIND","DABUR","DALBHARAT",
    "DEEPAKNTR","DELHIVERY","DIVISLAB","DIXON","DLF","DMART","DRREDDY","EICHERMOT",
    "ELGIEQUIP","EMAMILTD","ENGINERSIN","ESCORTS","EXIDEIND","FEDERALBNK",
    "FORTIS","GAIL","GLAND","GLAXO","GLENMARK","GMRINFRA","GNFC","GODREJCP",
    "GODREJPROP","GRANULES","GRASIM","GSPL","GUJGASLTD","HAL","HAVELLS","HCLTECH",
    "HDFCAMC","HDFCBANK","HDFCLIFE","HEROMOTOCO","HFCL","HINDCOPPER","HINDPETRO",
    "HINDUNILVR","HINDZINC","HONASA","HUDCO","ICICIBANK","ICICIGI","ICICIPRULI",
    "IDFCFIRSTB","IEX","IGL","INDHOTEL","INDIAMART","INDIANB","INDIGO","INDUSINDBK",
    "INDUSTOWER","INFY","IOC","IPCALAB","IRB","IRCTC","IRFC","ITC","JINDALSTEL",
    "JIOFIN","JSL","JSWENERGY","JSWSTEEL","JUBLFOOD","KALYANKJIL","KEI","KOTAKBANK",
    "KPITTECH","KRISHNADEF","LALPATHLAB","LAURUSLABS","LICHSGFIN","LICI","LTIM",
    "LTTS","LT","LUPIN","M&M","M&MFIN","MANAPPURAM","MARICO","MARUTI","MAXHEALTH",
    "MCX","MFSL","MGL","MOTHERSON","MPHASIS","MRF","MUTHOOTFIN","NAUKRI","NAVINFLUOR",
    "NMDC","NTPC","OBEROIRLTY","OFSS","OIL","ONGC","PAGEIND","PATANJALI","PAYTM",
    "PEL","PERSISTENT","PETRONET","PFC","PIDILITIND","PIIND","PNB","POLICYBZR",
    "POLYCAB","POONAWALLA","POWERGRID","PRESTIGE","PVRINOX","RAJESHEXPO","RAYMOND",
    "RECLTD","RELIANCE","RVNL","SAIL","SBICARD","SBILIFE","SBIN","SHREECEM",
    "SHRIRAMFIN","SIEMENS","SJVN","SKFINDIA","SONACOMS","SRF","STARHEALTH",
    "SUBURBANGAS","SUNPHARMA","SUNTV","SUPREMEIND","SYNGENE","TATACHEM",
    "TATACOMM","TATACONSUM","TATAELXSI","TATAMOTORS","TATAPOWER","TATASTEEL",
    "TCS","TECHM","TIINDIA","TITAN","TORNTPHARM","TORNTPOWER","TRENT","TVSMOTOR",
    "UBL","ULTRACEMCO","UNIONBANK","UNITDSPR","UPL","VEDL","VOLTAS","WIPRO",
    "YESBANK","ZOMATO","ZYDUSLIFE"
]

WATCHLIST_FILE = "watchlist.json"
JOURNAL_FILE   = "journal.json"

# ── Resolve paths relative to this script's own folder ────────
# This ensures watchlist.json and journal.json are always saved
# next to edge_scanner.py, regardless of where the app is run from.
_BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
WATCHLIST_FILE = os.path.join(_BASE_DIR, "watchlist.json")
JOURNAL_FILE   = os.path.join(_BASE_DIR, "journal.json")

# ── Persistence Helpers ───────────────────────────────────────
def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

# ── Indicator Calculations ────────────────────────────────────
def calc_sma(series, period):
    return series.rolling(window=period, min_periods=1).mean()

def calc_wma(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(window=period, min_periods=1).apply(
        lambda x: np.dot(x[-len(weights[:len(x)]):], weights[:len(x)]) / weights[:len(x)].sum(),
        raw=True
    )

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period, min_periods=1).mean()
    loss  = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
    rs    = gain / loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)

def calc_atr(high, low, close, period=14):
    hl  = high - low
    hpc = (high - close.shift()).abs()
    lpc = (low  - close.shift()).abs()
    tr  = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=1).mean()

def calc_adx(high, low, close, period=14):
    up   = high.diff()
    down = -low.diff()
    pdm  = up.where((up > down) & (up > 0), 0.0)
    ndm  = down.where((down > up) & (down > 0), 0.0)
    atr  = calc_atr(high, low, close, period)
    atr_safe = atr.replace(0, np.nan)
    pdi  = 100 * pdm.rolling(period, min_periods=1).mean() / atr_safe
    ndi  = 100 * ndm.rolling(period, min_periods=1).mean() / atr_safe
    denom = (pdi + ndi).replace(0, np.nan)
    dx   = 100 * (pdi - ndi).abs() / denom
    return dx.rolling(period, min_periods=1).mean().fillna(0)

# ── Fibonacci Retracement ─────────────────────────────────────
def calc_fibonacci(df, lookback=60):
    """
    Auto-detect swing high and swing low over `lookback` bars,
    then return all Fibonacci retracement levels.
    Returns a dict with keys: swing_low, swing_high, levels (dict of label:price),
    fib_zone (label of nearest level to current close), near_fib (bool).
    """
    close = df["Close"].astype(float)
    high  = df["High"].astype(float)
    low   = df["Low"].astype(float)

    window = min(lookback, len(df))

    swing_high = float(high.tail(window).max())
    swing_low  = float(low.tail(window).min())
    price_range = swing_high - swing_low

    if price_range == 0:
        return None

    ratios = {"0.0%": 0.0, "23.6%": 0.236, "38.2%": 0.382,
              "50.0%": 0.500, "61.8%": 0.618, "78.6%": 0.786, "100.0%": 1.0}

    levels = {label: round(swing_high - ratio * price_range, 2)
              for label, ratio in ratios.items()}

    # Find which Fib level the current price is nearest to
    last = float(close.iloc[-1])
    nearest_label = min(levels, key=lambda lbl: abs(levels[lbl] - last))
    nearest_dist  = abs(levels[nearest_label] - last) / last * 100  # % distance

    # "Near Fib" = within 1.5% of any key level (38.2, 50, 61.8, 78.6)
    key_levels = {k: v for k, v in levels.items() if k in ("38.2%", "50.0%", "61.8%", "78.6%")}
    near_fib   = any(abs(v - last) / last * 100 < 1.5 for v in key_levels.values())
    fib_zone   = nearest_label if near_fib else "-"

    return {
        "swing_low":  round(swing_low,  2),
        "swing_high": round(swing_high, 2),
        "levels":     levels,
        "fib_zone":   fib_zone,
        "near_fib":   near_fib,
        "nearest_dist": round(nearest_dist, 2),
    }


# ── Pivot Points ───────────────────────────────────────────────
def calc_pivots(df, method="Classic"):
    """
    Calculate pivot points using yesterday's (last complete bar) OHLC.
    Supports: Classic, Woodie, Camarilla.
    Returns a dict with PP, R1, R2, R3, S1, S2, S3.
    """
    if len(df) < 2:
        return None

    prev = df.iloc[-2]
    H = float(prev["High"])
    L = float(prev["Low"])
    C = float(prev["Close"])

    if method == "Classic":
        PP = (H + L + C) / 3
        R1 = 2 * PP - L
        S1 = 2 * PP - H
        R2 = PP + (H - L)
        S2 = PP - (H - L)
        R3 = H + 2 * (PP - L)
        S3 = L - 2 * (H - PP)

    elif method == "Woodie":
        PP = (H + L + 2 * C) / 4        # Woodie weights close double
        R1 = 2 * PP - L
        S1 = 2 * PP - H
        R2 = PP + H - L
        S2 = PP - H + L
        R3 = H + 2 * (PP - L)
        S3 = L - 2 * (H - PP)

    elif method == "Camarilla":
        PP = (H + L + C) / 3
        diff = H - L
        R1 = C + diff * 1.1 / 12
        R2 = C + diff * 1.1 / 6
        R3 = C + diff * 1.1 / 4        # Key breakout level
        S1 = C - diff * 1.1 / 12
        S2 = C - diff * 1.1 / 6
        S3 = C - diff * 1.1 / 4        # Key breakdown level
    else:
        return None

    levels = {"PP": PP, "R1": R1, "R2": R2, "R3": R3, "S1": S1, "S2": S2, "S3": S3}
    return {k: round(v, 2) for k, v in levels.items()}


# ── Data Fetcher ──────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(symbol, months=14):
    ticker = f"{symbol}.NS"
    end    = datetime.today()
    start  = end - timedelta(days=months * 31)
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df is None or df.empty or len(df) < 30:
            return None
        # Flatten MultiIndex columns from newer yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        df = df[["Open","High","Low","Close","Volume"]].copy()
        df.dropna(subset=["Open","High","Low","Close"], inplace=True)
        df["Volume"] = df["Volume"].fillna(0)
        return df
    except Exception:
        return None

# ── Stock Analyzer ────────────────────────────────────────────
def analyze(symbol, df):
    close  = df["Close"].astype(float)
    high   = df["High"].astype(float)
    low    = df["Low"].astype(float)
    volume = df["Volume"].astype(float)
    n      = len(df)

    sma20  = float(calc_sma(close, 20).iloc[-1])
    sma50  = float(calc_sma(close, 50).iloc[-1])
    sma200 = float(calc_sma(close, 200).iloc[-1])
    wma10  = float(calc_wma(close, 10).iloc[-1])
    wma30  = float(calc_wma(close, 30).iloc[-1])
    rsi_v  = float(calc_rsi(close).iloc[-1])
    atr_v  = float(calc_atr(high, low, close).iloc[-1])
    adx_v  = float(calc_adx(high, low, close).iloc[-1])

    last       = float(close.iloc[-1])
    prev       = float(close.iloc[-2]) if n > 1 else last
    change_pct = round((last - prev) / prev * 100, 2) if prev != 0 else 0

    # Volume ratio — safe calculation
    vol_series = volume.replace(0, np.nan)
    if n > 21:
        vol_avg20 = float(vol_series.iloc[-21:-1].mean())
    else:
        vol_avg20 = float(vol_series.mean())
    last_vol  = float(volume.iloc[-1])
    vol_ratio = round(last_vol / vol_avg20, 2) if vol_avg20 > 0 and last_vol > 0 else 0.0

    above20  = last > sma20
    above50  = last > sma50
    above200 = last > sma200
    aligned  = sma20 > sma50 > sma200
    wma_bull = wma10 > wma30

    # Trend
    if above20 and above50 and above200 and aligned: trend = "STRONG UP"
    elif above50 and above200:                        trend = "UPTREND"
    elif not above200:                                trend = "DOWNTREND"
    else:                                             trend = "SIDEWAYS"

    # Setup detection
    bars   = df.tail(5)
    red3   = sum(1 for i in range(3) if float(bars["Close"].iloc[i]) < float(bars["Open"].iloc[i]))
    last_gr = float(bars["Close"].iloc[-1]) > float(bars["Open"].iloc[-1])
    near20  = abs(last - sma20) / sma20 < 0.03 if sma20 != 0 else False

    h15 = high.tail(15); l15 = low.tail(15); v15 = volume.tail(15)
    l15_min = float(l15.min())
    rng     = (float(h15.max()) - l15_min) / l15_min if l15_min > 0 else 1
    vol_dry = float(v15.iloc[-1]) < float(v15.mean()) if float(v15.mean()) > 0 else False
    coiling = rng < 0.06 and vol_dry

    # WMA cross in last 3 bars
    wma_cross = False
    for i in range(max(31, n - 4), n - 1):
        try:
            w10p = float(calc_wma(close.iloc[:i],   10).iloc[-1])
            w30p = float(calc_wma(close.iloc[:i],   30).iloc[-1])
            w10c = float(calc_wma(close.iloc[:i+1], 10).iloc[-1])
            w30c = float(calc_wma(close.iloc[:i+1], 30).iloc[-1])
            if w10p <= w30p and w10c > w30c:
                wma_cross = True; break
        except Exception:
            continue

    setup = "-"
    if red3 >= 2 and last_gr and near20 and above50:   setup = "3-Bar Pullback"
    elif coiling and vol_ratio > 1.5:                   setup = "Range Breakout"
    elif wma_cross and 45 <= rsi_v <= 65:               setup = "WMA Cross"
    elif coiling:                                        setup = "Coiling"

    # Score (max 10)
    score = 0
    if above20 and aligned:    score += 3
    elif above50 and above200: score += 2
    elif above200:             score += 1

    if adx_v > 30:   score += 2
    elif adx_v > 20: score += 1

    if vol_ratio > 2:        score += 2
    elif vol_ratio > 1.5:    score += 1

    if 45 <= rsi_v <= 60:       score += 2
    elif 60 < rsi_v <= 70:      score += 1
    elif 30 < rsi_v < 45:       score += 1

    if setup != "-": score += 1

    # ── Fibonacci Zone check ──────────────────────────────────
    fib_result = calc_fibonacci(df)
    fib_zone   = fib_result["fib_zone"] if fib_result else "-"
    near_fib   = fib_result["near_fib"] if fib_result else False
    # Bonus +1 if price is on a key Fib support in an uptrend
    if near_fib and trend in ("STRONG UP", "UPTREND"):
        score += 1

    # ── Pivot Point proximity check ────────────────────────────
    pivots     = calc_pivots(df, "Classic")
    near_pivot = "-"
    if pivots:
        pivot_labels = {"PP": pivots["PP"], "S1": pivots["S1"],
                        "S2": pivots["S2"], "R1": pivots["R1"]}
        closest_piv  = min(pivot_labels, key=lambda k: abs(pivot_labels[k] - last))
        piv_dist_pct = abs(pivot_labels[closest_piv] - last) / last * 100
        if piv_dist_pct < 1.0:
            near_pivot = closest_piv

    # Signal
    if score >= 7 and trend != "DOWNTREND" and rsi_v < 72: signal = "BUY"
    elif score >= 5:                                         signal = "WATCH"
    else:                                                    signal = "AVOID"

    return {
        "symbol": symbol, "close": round(last, 2), "change_pct": change_pct,
        "sma20": round(sma20, 2), "sma50": round(sma50, 2), "sma200": round(sma200, 2),
        "wma10": round(wma10, 2), "wma30": round(wma30, 2),
        "rsi": round(rsi_v, 1), "atr": round(atr_v, 2), "adx": round(adx_v, 1),
        "vol_ratio": vol_ratio, "trend": trend, "setup": setup,
        "score": min(score, 11), "signal": signal,
        "above20": above20, "above50": above50, "above200": above200, "aligned": aligned,
        "fib_zone": fib_zone, "near_pivot": near_pivot,
    }

# ── Chart Builder ─────────────────────────────────────────────
def build_chart(symbol, df, result, show_fib=True, show_pivots=True, show_pivot_method="Classic"):
    close  = df["Close"].astype(float)
    high   = df["High"].astype(float)
    low    = df["Low"].astype(float)
    volume = df["Volume"].astype(float)
    dates  = df.index

    sma20_s  = calc_sma(close, 20)
    sma50_s  = calc_sma(close, 50)
    sma200_s = calc_sma(close, 200)
    rsi_s    = calc_rsi(close)
    adx_s    = calc_adx(high, low, close)

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.03,
        subplot_titles=[f"{symbol} — Price & MAs", "RSI (14)", "ADX (14)"]
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=dates, open=df["Open"], high=high, low=low, close=close,
        name="Price",
        increasing_line_color="#00c853", decreasing_line_color="#d32f2f",
        increasing_fillcolor="#00c853", decreasing_fillcolor="#d32f2f",
    ), row=1, col=1)

    # Moving averages
    for ma, color, name in [
        (sma20_s,  "#f9a825", "SMA 20"),
        (sma50_s,  "#4da6ff", "SMA 50"),
        (sma200_s, "#c084fc", "SMA 200"),
    ]:
        fig.add_trace(go.Scatter(x=dates, y=ma, name=name,
            line=dict(color=color, width=1.5)), row=1, col=1)

    # Volume bars — safe rgba colors
    vol_colors = [
        "rgba(0,200,83,0.25)" if float(c) >= float(o) else "rgba(211,47,47,0.25)"
        for c, o in zip(close.values, df["Open"].astype(float).values)
    ]
    fig.add_trace(go.Bar(
        x=dates, y=volume, name="Volume",
        marker=dict(color=vol_colors), yaxis="y2", showlegend=False
    ), row=1, col=1)

    # RSI panel
    fig.add_trace(go.Scatter(x=dates, y=rsi_s, name="RSI",
        line=dict(color="#f9a825", width=1.5)), row=2, col=1)
    for y_val, col in [(70, "rgba(211,47,47,0.4)"), (30, "rgba(0,200,83,0.4)"), (60, "rgba(255,255,255,0.15)")]:
        fig.add_shape(type="line", x0=dates[0], x1=dates[-1], y0=y_val, y1=y_val,
                      line=dict(color=col, width=1, dash="dot"), row=2, col=1)
    fig.add_shape(type="rect", x0=dates[0], x1=dates[-1], y0=45, y1=60,
                  fillcolor="rgba(0,200,83,0.07)", line_width=0, row=2, col=1)

    # ADX panel
    fig.add_trace(go.Scatter(x=dates, y=adx_s, name="ADX",
        line=dict(color="#4da6ff", width=1.5)), row=3, col=1)
    for y_val, col in [(30, "rgba(0,200,83,0.4)"), (20, "rgba(249,168,37,0.4)")]:
        fig.add_shape(type="line", x0=dates[0], x1=dates[-1], y0=y_val, y1=y_val,
                      line=dict(color=col, width=1, dash="dot"), row=3, col=1)

    # ── Fibonacci overlay ──────────────────────────────────────
    fib_result = calc_fibonacci(df)
    if fib_result and show_fib:
        fib_colors = {
            "0.0%":   "#1D9E75", "23.6%":  "#639922", "38.2%":  "#EF9F27",
            "50.0%":  "#D85A30", "61.8%":  "#E24B4A", "78.6%":  "#7F77DD", "100.0%": "#888780"
        }
        for label, price in fib_result["levels"].items():
            lw = 1.8 if label == "61.8%" else 0.9
            fig.add_shape(type="line", x0=dates[0], x1=dates[-1], y0=price, y1=price,
                          line=dict(color=fib_colors[label], width=lw, dash="dash"), row=1, col=1)
            fig.add_annotation(
                x=dates[-1], y=price, xref="x", yref="y",
                text=f" {label} ₹{price:.0f}", showarrow=False,
                font=dict(color=fib_colors[label], size=9),
                xanchor="left", bgcolor="rgba(8,13,20,0.6)"
            )

    # ── Pivot Point overlay ────────────────────────────────────
    pivots = calc_pivots(df, show_pivot_method)
    if pivots and show_pivots:
        piv_colors = {
            "PP": "#ffffff", "R1": "#E24B4A", "R2": "#A32D2D", "R3": "#7B1818",
            "S1": "#1D9E75", "S2": "#0F6E56", "S3": "#085041"
        }
        for label, price in pivots.items():
            lw = 1.5 if label == "PP" else 1.0
            fig.add_shape(type="line", x0=dates[0], x1=dates[-1], y0=price, y1=price,
                          line=dict(color=piv_colors[label], width=lw, dash="dot"), row=1, col=1)
            fig.add_annotation(
                x=dates[0], y=price, xref="x", yref="y",
                text=f"{label} ₹{price:.0f} ", showarrow=False,
                font=dict(color=piv_colors[label], size=9),
                xanchor="right", bgcolor="rgba(8,13,20,0.6)"
            )

    # Signal annotation on price chart
    sig_color = {"BUY": "#00c853", "WATCH": "#f9a825", "AVOID": "#d32f2f"}[result["signal"]]
    fib_tag   = f" | Fib {result.get('fib_zone','-')}" if result.get("fib_zone","-") != "-" else ""
    piv_tag   = f" | Near {result.get('near_pivot','-')}" if result.get("near_pivot","-") != "-" else ""
    fig.add_annotation(
        x=dates[-1], y=float(close.iloc[-1]),
        xref="x", yref="y",
        text=f"  {result['signal']} | Score {result['score']}/11 | RSI {result['rsi']}{fib_tag}{piv_tag}",
        showarrow=True, arrowhead=2, arrowcolor=sig_color,
        font=dict(color=sig_color, size=12),
        bgcolor="#0d1824", bordercolor=sig_color, borderwidth=1,
    )

    fig.update_layout(
        height=700,
        paper_bgcolor="#080d14", plot_bgcolor="#080d14",
        font=dict(color="#c8d8e8", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="#0d1824", bordercolor="#1a2d45", borderwidth=1),
        margin=dict(l=50, r=20, t=40, b=20),
        yaxis2=dict(overlaying="y", side="right", showticklabels=False,
                    range=[0, float(volume.max()) * 5], showgrid=False),
    )
    for i in [1, 2, 3]:
        fig.update_xaxes(gridcolor="#0f1c28", zerolinecolor="#1a2d45", row=i, col=1)
        fig.update_yaxes(gridcolor="#0f1c28", zerolinecolor="#1a2d45", row=i, col=1)
    fig.update_xaxes(showspikes=True, spikecolor="#445566", spikethickness=1)

    return fig

# ── Styling helpers ───────────────────────────────────────────
def color_signal(val):
    if val == "BUY":   return "background-color:rgba(0,200,83,0.13);color:#00c853;font-weight:700"
    if val == "WATCH": return "background-color:rgba(249,168,37,0.13);color:#f9a825;font-weight:700"
    if val == "AVOID": return "background-color:rgba(211,47,47,0.13);color:#d32f2f;font-weight:700"
    return ""

def color_chg(val):
    try:
        return f"color:{'#00c853' if float(val) > 0 else '#d32f2f'}"
    except (TypeError, ValueError):
        return ""

def color_score(val):
    try:
        v = int(val)
        if v >= 8:   return "color:#00c853;font-weight:700"
        elif v >= 6: return "color:#f9a825;font-weight:700"
        else:        return "color:#d32f2f;font-weight:700"
    except (TypeError, ValueError):
        return ""

def color_pnl(val):
    try:
        return f"color:{'#00c853' if float(val) > 0 else '#d32f2f' if float(val) < 0 else '#c8d8e8'}"
    except (TypeError, ValueError):
        return ""

# ══════════════════════════════════════════════════════════════
#                         MAIN APP
# ══════════════════════════════════════════════════════════════
def main():
    if "scan_results" not in st.session_state: st.session_state.scan_results = []
    if "watchlist"    not in st.session_state: st.session_state.watchlist    = load_json(WATCHLIST_FILE, [])
    if "journal"      not in st.session_state: st.session_state.journal      = load_json(JOURNAL_FILE, [])

    # ── Sidebar ───────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;'>
            <div style='width:8px;height:8px;border-radius:50%;background:#00c853;'></div>
            <span style='font-size:16px;font-weight:800;color:#e8f4ff;letter-spacing:2px;'>EDGE SCANNER</span>
        </div>
        <div style='font-size:9px;color:#445566;letter-spacing:2px;margin-bottom:20px;'>NSE SWING TRADING SYSTEM</div>
        """, unsafe_allow_html=True)

        st.markdown("### ⚙️ Settings")
        capital  = st.number_input("Total Capital (₹)", min_value=10000, max_value=10000000,
                                    value=500000, step=10000, format="%d")
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 2.0, 0.5)
        risk_amt = capital * risk_pct / 100
        st.markdown(f"<div class='info-box'>Max loss per trade: <b>₹{risk_amt:,.0f}</b></div>",
                    unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🔍 Quick Lookup")
        quick_sym = st.selectbox("Select Stock", [""] + sorted(NIFTY200))
        st.markdown("---")
        st.markdown(f"### 📋 Watchlist ({len(st.session_state.watchlist)})")
        for w in st.session_state.watchlist:
            st.markdown(f"• `{w}`")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 TREND SCANNER", "📊 CHART ANALYSIS",
        "📋 WATCHLIST", "🧮 POSITION SIZER", "📓 TRADE JOURNAL", "📐 PRICE ACTION"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — TREND SCANNER
    # ══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("## 🔍 Trend Scanner")
        st.markdown("Scans Nifty 200 stocks using SMA, WMA, RSI, ADX, Volume and pattern detection.")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            scan_mode = st.radio("Scan Mode", ["Full Nifty 200", "Watchlist Only", "Custom List"], horizontal=True)
        with col2:
            min_score = st.selectbox("Min Score", [5, 6, 7, 8, 9], index=2)
        with col3:
            signal_filter = st.selectbox("Signal", ["ALL", "BUY", "WATCH", "AVOID"])

        if scan_mode == "Custom List":
            custom_input    = st.text_area("Enter symbols (one per line or comma separated)", "RELIANCE\nHDFCBANK\nINFY\nTCS")
            symbols_to_scan = [s.strip().upper() for s in custom_input.replace(",", "\n").split("\n") if s.strip()]
        elif scan_mode == "Watchlist Only":
            symbols_to_scan = st.session_state.watchlist
        else:
            symbols_to_scan = NIFTY200

        if st.button("▶ RUN SCANNER", use_container_width=True) and symbols_to_scan:
            results  = []
            failed_symbols = []
            progress = st.progress(0, text="Starting scan...")
            status   = st.empty()
            for i, sym in enumerate(symbols_to_scan):
                status.markdown(f"⏳ Fetching `{sym}`... ({i+1}/{len(symbols_to_scan)})")
                df = fetch_data(sym)
                if df is not None and len(df) > 30:
                    try:
                        results.append(analyze(sym, df))
                    except Exception:
                        failed_symbols.append(sym)
                progress.progress((i + 1) / len(symbols_to_scan), text=f"Scanning... {i+1}/{len(symbols_to_scan)}")
            progress.empty(); status.empty()
            st.session_state.scan_results = sorted(
                results, key=lambda x: (["BUY","WATCH","AVOID"].index(x["signal"]), -x["score"])
            )
            st.success(f"✅ Scan complete — {len(results)} stocks analyzed")

            if failed_symbols:
                st.warning("Skipped symbols with analysis errors: " + ", ".join(failed_symbols))

        results = st.session_state.scan_results
        if results:
            filtered = [r for r in results if r["score"] >= min_score]
            if signal_filter != "ALL":
                filtered = [r for r in filtered if r["signal"] == signal_filter]

            c1, c2, c3, c4 = st.columns(4)
            for col, num, lbl, color in [
                (c1, sum(1 for r in filtered if r["signal"]=="BUY"),   "BUY SIGNALS",  "#00c853"),
                (c2, sum(1 for r in filtered if r["signal"]=="WATCH"), "WATCH",         "#f9a825"),
                (c3, sum(1 for r in filtered if r["adx"] > 30),        "STRONG TREND",  "#4da6ff"),
                (c4, sum(1 for r in filtered if r["score"] >= 8),      "SCORE 8+",      "#c084fc"),
            ]:
                col.markdown(f"""<div class='metric-card'>
                    <div class='metric-num' style='color:{color};'>{num}</div>
                    <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

            st.markdown("---")

            df_display = pd.DataFrame([{
                "Symbol":     r["symbol"], "Close": f"₹{r['close']:,.2f}",
                "Chg%":       r["change_pct"], "RSI": r["rsi"], "ADX": r["adx"],
                "Vol Ratio":  r["vol_ratio"], "Trend": r["trend"], "Setup": r["setup"],
                "Fib Zone":   r.get("fib_zone", "-"), "Near Pivot": r.get("near_pivot", "-"),
                "Score":      r["score"], "Signal": r["signal"],
                ">SMA200":    "✓" if r["above200"] else "✗",
                "Aligned":    "✓" if r["aligned"] else "✗",
            } for r in filtered], columns=[
                "Symbol", "Close", "Chg%", "RSI", "ADX", "Vol Ratio",
                "Trend", "Setup", "Fib Zone", "Near Pivot", "Score",
                "Signal", ">SMA200", "Aligned"
            ])

            styled = df_display.style\
                .map(color_signal, subset=["Signal"])\
                .map(color_chg,    subset=["Chg%"])\
                .map(color_score,  subset=["Score"])
            st.dataframe(styled, use_container_width=True, height=500)

            st.markdown("#### ➕ Add to Watchlist")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                add_sym = st.selectbox("Select stock to add", [""] + [r["symbol"] for r in filtered])
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Add to Watchlist") and add_sym:
                    if add_sym not in st.session_state.watchlist:
                        st.session_state.watchlist.append(add_sym)
                        save_json(WATCHLIST_FILE, st.session_state.watchlist)
                        st.success(f"✅ {add_sym} added")
                    else:
                        st.info(f"{add_sym} already in watchlist")

    # ══════════════════════════════════════════════════════════
    # TAB 2 — CHART ANALYSIS
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("## 📊 Chart Analysis")
        col1, col2 = st.columns([3, 1])
        with col1:
            chart_sym = st.selectbox("Select Symbol", [""] + sorted(NIFTY200),
                                      index=NIFTY200.index(quick_sym) + 1 if quick_sym in NIFTY200 else 0)
        with col2:
            months     = st.selectbox("History (months)", [3, 6, 9, 12, 14], index=4)
            show_fib   = st.checkbox("Show Fib Levels", value=True)
            show_pivs  = st.checkbox("Show Pivot Points", value=True)
            piv_method = st.selectbox("Pivot Method", ["Classic", "Woodie", "Camarilla"])
            st.markdown("<br>", unsafe_allow_html=True)
            load_chart = st.button("📊 Load Chart", use_container_width=True)

        if chart_sym and load_chart:
            with st.spinner(f"Loading {chart_sym}..."):
                df = fetch_data(chart_sym, months)
            if df is None or len(df) < 30:
                st.error(f"❌ Could not fetch data for {chart_sym}.")
            else:
                result    = analyze(chart_sym, df)
                sig       = result["signal"]
                sig_color = {"BUY": "#00c853", "WATCH": "#f9a825", "AVOID": "#d32f2f"}[sig]

                m1, m2, m3, m4, m5, m6 = st.columns(6)
                for col, lbl, val, color in [
                    (m1, "CLOSE",  f"₹{result['close']:,.2f}",       "#e8f4ff"),
                    (m2, "CHANGE", f"{result['change_pct']:+.2f}%",   "#00c853" if result["change_pct"] > 0 else "#d32f2f"),
                    (m3, "RSI",    result["rsi"],                      "#f9a825"),
                    (m4, "ADX",    result["adx"],                      "#4da6ff"),
                    (m5, "SCORE",  f"{result['score']}/11",            "#c084fc"),
                    (m6, "SIGNAL", sig,                                sig_color),
                ]:
                    col.markdown(f"""<div class='metric-card'>
                        <div class='metric-num' style='color:{color};font-size:22px;'>{val}</div>
                        <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

                st.markdown("")
                st.plotly_chart(build_chart(chart_sym, df, result, show_fib=show_fib,
                    show_pivots=show_pivs, show_pivot_method=piv_method), use_container_width=True)

                st.markdown("#### Moving Average Structure")
                vals = [result["sma20"], result["sma50"], result["sma200"], result["wma10"], result["wma30"]]
                st.dataframe(pd.DataFrame({
                    "Indicator": ["SMA 20","SMA 50","SMA 200","WMA 10","WMA 30"],
                    "Value":     vals,
                    "vs Price":  [f"{(result['close']-v)/v*100:+.2f}%" for v in vals],
                    "Position":  ["Above ✓" if result["close"] > v else "Below ✗" for v in vals],
                }), use_container_width=True)

                if st.button(f"➕ Add {chart_sym} to Watchlist"):
                    if chart_sym not in st.session_state.watchlist:
                        st.session_state.watchlist.append(chart_sym)
                        save_json(WATCHLIST_FILE, st.session_state.watchlist)
                        st.success(f"✅ {chart_sym} added to watchlist")

    # ══════════════════════════════════════════════════════════
    # TAB 3 — WATCHLIST
    # ══════════════════════════════════════════════════════════
    with tab3:
        st.markdown("## 📋 Watchlist")
        col1, col2 = st.columns([3, 1])
        with col1:
            add_input = st.selectbox("Add stock to watchlist", [""] + sorted(NIFTY200), key="wl_add")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", use_container_width=True) and add_input:
                if add_input not in st.session_state.watchlist:
                    st.session_state.watchlist.append(add_input)
                    save_json(WATCHLIST_FILE, st.session_state.watchlist)

        refresh_wl = st.button("🔄 Refresh Watchlist Data", use_container_width=True)

        if st.session_state.watchlist:
            if refresh_wl:
                wl_results = []
                failed_watchlist = []
                prog = st.progress(0)
                for i, sym in enumerate(st.session_state.watchlist):
                    df = fetch_data(sym)
                    if df is not None:
                        try:
                            wl_results.append(analyze(sym, df))
                        except Exception:
                            failed_watchlist.append(sym)
                    prog.progress((i+1)/len(st.session_state.watchlist))
                prog.empty()
                st.session_state.wl_results = wl_results
                if failed_watchlist:
                    st.warning("Watchlist refresh skipped: " + ", ".join(failed_watchlist))

            wl_results = st.session_state.get("wl_results", [])
            if wl_results:
                for r in wl_results:
                    atr_stop  = r["atr"] * 1.5
                    qty       = int(risk_amt / atr_stop) if atr_stop > 0 else 0
                    invest    = qty * r["close"]
                    icon      = "🟢" if r["signal"]=="BUY" else "🟡" if r["signal"]=="WATCH" else "🔴"
                    with st.expander(f"{icon} {r['symbol']} — {r['signal']} | Score {r['score']}/10 | ₹{r['close']:,.2f}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("RSI",       r["rsi"])
                        c2.metric("ADX",       r["adx"])
                        c3.metric("Vol Ratio", r["vol_ratio"])
                        c4.metric("ATR",       f"₹{r['atr']:.2f}")
                        st.markdown(f"""<div class='info-box'>
                            📐 <b>Position Size (1.5x ATR stop):</b> {qty} shares &nbsp;|&nbsp;
                            💰 <b>Investment:</b> ₹{invest:,.0f} &nbsp;|&nbsp;
                            🛑 <b>Stop Loss:</b> ₹{r['close'] - atr_stop:,.2f}
                        </div>""", unsafe_allow_html=True)
                        st.markdown(f"**Trend:** {r['trend']} | **Setup:** {r['setup']} | **Aligned:** {'Yes ✓' if r['aligned'] else 'No ✗'}")
                        if st.button(f"🗑 Remove {r['symbol']}", key=f"rm_{r['symbol']}"):
                            st.session_state.watchlist.remove(r["symbol"])
                            save_json(WATCHLIST_FILE, st.session_state.watchlist)
                            st.rerun()
            else:
                for sym in st.session_state.watchlist:
                    col_s, col_r = st.columns([5, 1])
                    col_s.markdown(f"• `{sym}`")
                    if col_r.button("Remove", key=f"rm2_{sym}"):
                        st.session_state.watchlist.remove(sym)
                        save_json(WATCHLIST_FILE, st.session_state.watchlist)
                        st.rerun()
                st.markdown("<div class='warn-box'>Click <b>🔄 Refresh Watchlist Data</b> to load live prices.</div>",
                            unsafe_allow_html=True)
        else:
            st.info("Your watchlist is empty. Add stocks from the Scanner or Chart tab.")

    # ══════════════════════════════════════════════════════════
    # TAB 4 — POSITION SIZER
    # ══════════════════════════════════════════════════════════
    with tab4:
        st.markdown("## 🧮 Position Sizer")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Trade Inputs")
            ps_symbol  = st.text_input("Symbol", "RELIANCE").upper()
            ps_entry   = st.number_input("Entry Price (₹)",    min_value=1.0,  value=2800.0, step=1.0)
            ps_stop    = st.number_input("Stop Loss Price (₹)", min_value=1.0,  value=2750.0, step=1.0)
            ps_target  = st.number_input("Target Price (₹)",   min_value=1.0,  value=2950.0, step=1.0)
            ps_capital = st.number_input("Capital (₹)",        min_value=1000, value=capital, step=1000)
            ps_risk    = st.slider("Risk %", 0.5, 5.0, risk_pct, 0.5, key="ps_risk")

        with col2:
            st.markdown("### Results")
            risk_per_trade = ps_capital * ps_risk / 100
            risk_per_share = ps_entry - ps_stop
            reward         = ps_target - ps_entry
            rr_ratio       = reward / risk_per_share if risk_per_share > 0 else 0

            if risk_per_share <= 0:
                st.error("❌ Stop loss must be below entry price")
            else:
                qty         = int(risk_per_trade / risk_per_share)
                total_inv   = qty * ps_entry
                max_loss    = qty * risk_per_share
                max_profit  = qty * reward
                capital_pct = total_inv / ps_capital * 100

                st.markdown(f"""<div class='metric-card' style='margin-bottom:10px;'>
                    <div class='metric-num' style='color:#00c853;'>{qty}</div>
                    <div class='metric-lbl'>SHARES TO BUY</div></div>""", unsafe_allow_html=True)

                st.dataframe(pd.DataFrame({
                    "Metric": ["Total Investment","Capital Used %","Risk per Share","Max Loss","Max Profit","Risk:Reward"],
                    "Value":  [f"₹{total_inv:,.0f}", f"{capital_pct:.1f}%", f"₹{risk_per_share:.2f}",
                               f"₹{max_loss:,.0f}", f"₹{max_profit:,.0f}", f"{rr_ratio:.2f}:1"]
                }), use_container_width=True, hide_index=True)

                if rr_ratio < 2:
                    st.markdown("<div class='warn-box'>⚠️ R:R below 2:1 — consider adjusting target or stop.</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='info-box'>✅ Good R:R of {rr_ratio:.1f}:1 — trade meets minimum threshold.</div>",
                                unsafe_allow_html=True)

                st.markdown("#### ATR-Based Stop Levels")
                df_ps = fetch_data(ps_symbol)
                if df_ps is not None:
                    atr_val  = float(calc_atr(df_ps["High"].astype(float), df_ps["Low"].astype(float), df_ps["Close"].astype(float)).iloc[-1])
                    atr_rows = []
                    for mult in [1.0, 1.5, 2.0]:
                        stop_atr = ps_entry - atr_val * mult
                        qty_atr  = int(risk_per_trade / (atr_val * mult)) if atr_val > 0 else 0
                        atr_rows.append({
                            "ATR Mult": f"{mult}x", "Stop Level": f"₹{stop_atr:.2f}",
                            "Stop Distance": f"₹{atr_val*mult:.2f}", "Qty": qty_atr,
                            "Investment": f"₹{qty_atr * ps_entry:,.0f}",
                        })
                    st.dataframe(pd.DataFrame(atr_rows), use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════
    # TAB 5 — TRADE JOURNAL
    # ══════════════════════════════════════════════════════════
    with tab5:
        st.markdown("## 📓 Trade Journal")

        with st.expander("➕ Log New Trade", expanded=False):
            jc1, jc2, jc3 = st.columns(3)
            j_sym    = jc1.text_input("Symbol",   key="j_sym").upper()
            j_date   = jc1.date_input("Entry Date", key="j_date")
            j_entry  = jc2.number_input("Entry Price",  min_value=0.01, key="j_entry")
            j_stop   = jc2.number_input("Stop Loss",    min_value=0.01, key="j_stop")
            j_target = jc2.number_input("Target",       min_value=0.01, key="j_target")
            j_qty    = jc3.number_input("Qty", min_value=1, step=1, key="j_qty")
            j_setup  = jc3.selectbox("Setup",  ["3-Bar Pullback","Range Breakout","WMA Cross","Coiling",
                                                  "Fib Bounce","Fib Extension","Pivot Range","Pivot Breakout","Other"], key="j_setup")
            j_status = jc3.selectbox("Status", ["OPEN","CLOSED WIN","CLOSED LOSS"], key="j_status")
            j_exit   = jc3.number_input("Exit Price (0 if open)", min_value=0.0, key="j_exit")
            j_notes  = st.text_area("Notes", key="j_notes")

            if st.button("💾 Save Trade"):
                pnl = (j_exit - j_entry) * j_qty if j_exit > 0 else 0
                rr  = (j_target - j_entry) / (j_entry - j_stop) if j_entry > j_stop else 0
                st.session_state.journal.append({
                    "symbol": j_sym, "date": str(j_date), "entry": j_entry,
                    "stop": j_stop, "target": j_target, "exit": j_exit,
                    "qty": j_qty, "setup": j_setup, "status": j_status,
                    "pnl": round(pnl, 2), "rr": round(rr, 2), "notes": j_notes
                })
                save_json(JOURNAL_FILE, st.session_state.journal)
                st.success("✅ Trade saved!")

        if st.session_state.journal:
            jdf          = pd.DataFrame(st.session_state.journal)
            closed       = jdf[jdf["status"] != "OPEN"]
            wins         = len(jdf[jdf["status"] == "CLOSED WIN"])
            total_closed = len(closed)
            win_rate     = wins / total_closed * 100 if total_closed > 0 else 0
            net_pnl      = float(jdf["pnl"].sum())
            avg_rr       = float(jdf["rr"].mean())

            jm1, jm2, jm3, jm4 = st.columns(4)
            for col, lbl, val, color in [
                (jm1, "NET P&L",     f"₹{net_pnl:,.0f}",     "#00c853" if net_pnl > 0 else "#d32f2f"),
                (jm2, "WIN RATE",    f"{win_rate:.0f}%",       "#4da6ff"),
                (jm3, "AVG R:R",     f"{avg_rr:.1f}:1",        "#c084fc"),
                (jm4, "OPEN TRADES", len(jdf[jdf["status"]=="OPEN"]), "#f9a825"),
            ]:
                col.markdown(f"""<div class='metric-card'>
                    <div class='metric-num' style='color:{color};font-size:22px;'>{val}</div>
                    <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

            st.markdown("---")
            display_cols = ["date","symbol","entry","exit","qty","pnl","rr","status","setup"]
            available    = [c for c in display_cols if c in jdf.columns]
            if "pnl" in jdf.columns:
                st.dataframe(jdf[available].style.map(color_pnl, subset=["pnl"]), use_container_width=True)
            else:
                st.dataframe(jdf[available], use_container_width=True)

            # P&L Chart
            if len(closed) > 1:
                cs = closed.sort_values("date").copy()
                cs["cumulative_pnl"] = cs["pnl"].cumsum()
                fig_pnl = go.Figure()
                fig_pnl.add_trace(go.Scatter(
                    x=cs["date"], y=cs["cumulative_pnl"], fill="tozeroy",
                    line=dict(color="#00c853", width=2), fillcolor="rgba(0,200,83,0.13)",
                    name="Cumulative P&L"
                ))
                fig_pnl.update_layout(
                    title="Cumulative P&L", paper_bgcolor="#080d14", plot_bgcolor="#080d14",
                    font=dict(color="#c8d8e8"), height=300, margin=dict(l=40, r=20, t=40, b=20),
                )
                fig_pnl.update_xaxes(gridcolor="#0f1c28")
                fig_pnl.update_yaxes(gridcolor="#0f1c28")
                st.plotly_chart(fig_pnl, use_container_width=True)

            # Export
            st.markdown("#### 📤 Export")
            ex1, ex2 = st.columns(2)
            with ex1:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    jdf.to_excel(writer, sheet_name="All Trades", index=False)
                    pd.DataFrame({
                        "Metric": ["Total Trades","Open Trades","Closed Trades","Wins","Losses","Win Rate %","Net P&L","Avg R:R"],
                        "Value":  [len(jdf), len(jdf[jdf["status"]=="OPEN"]), total_closed,
                                   wins, total_closed-wins, round(win_rate,1), round(net_pnl,2), round(avg_rr,2)]
                    }).to_excel(writer, sheet_name="Summary", index=False)
                    open_t = jdf[jdf["status"]=="OPEN"]
                    if not open_t.empty:
                        open_t.to_excel(writer, sheet_name="Open Trades", index=False)
                output.seek(0)
                st.download_button("📥 Download as Excel", data=output,
                    file_name=f"TradeJournal_{datetime.today().strftime('%d-%b-%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with ex2:
                st.download_button("📥 Download as CSV", data=jdf.to_csv(index=False).encode("utf-8"),
                    file_name=f"TradeJournal_{datetime.today().strftime('%d-%b-%Y')}.csv",
                    mime="text/csv", use_container_width=True)

            st.markdown("---")
            if st.button("🗑 Clear All Journal Entries"):
                st.session_state.journal = []
                save_json(JOURNAL_FILE, [])
                st.rerun()
        else:
            st.info("No trades logged yet. Use the form above to add your first trade.")

    # ══════════════════════════════════════════════════════════
    # TAB 6 — PRICE ACTION (Fibonacci + Pivot Points)
    # ══════════════════════════════════════════════════════════
    with tab6:
        st.markdown("## 📐 Price Action Analysis")
        st.markdown("Fibonacci retracement levels and pivot points for any NSE stock.")

        pa_col1, pa_col2, pa_col3 = st.columns([2, 1, 1])
        with pa_col1:
            pa_sym = st.selectbox("Select Symbol", [""] + sorted(NIFTY200), key="pa_sym")
        with pa_col2:
            pa_months  = st.selectbox("History", [3, 6, 9, 12], index=2, key="pa_months")
            fib_window = st.slider("Fib Lookback (bars)", 20, 120, 60, 10)
        with pa_col3:
            pa_piv_method = st.selectbox("Pivot Method", ["Classic", "Woodie", "Camarilla"], key="pa_piv")
            st.markdown("<br>", unsafe_allow_html=True)
            load_pa = st.button("📐 Analyse", use_container_width=True)

        if pa_sym and load_pa:
            with st.spinner(f"Loading {pa_sym}..."):
                df_pa = fetch_data(pa_sym, pa_months)

            if df_pa is None or len(df_pa) < 30:
                st.error(f"❌ Could not fetch data for {pa_sym}.")
            else:
                fib       = calc_fibonacci(df_pa, lookback=fib_window)
                pivs      = calc_pivots(df_pa, pa_piv_method)
                last_price = float(df_pa["Close"].astype(float).iloc[-1])

                # ── Section 1: Fibonacci ──────────────────────────────
                st.markdown("---")
                st.markdown("### 🌀 Fibonacci Retracement")

                f1, f2, f3 = st.columns(3)
                f1.markdown(f"""<div class='metric-card'>
                    <div class='metric-num' style='color:#1D9E75;font-size:20px;'>₹{fib['swing_low']:,.2f}</div>
                    <div class='metric-lbl'>SWING LOW (base)</div></div>""", unsafe_allow_html=True)
                f2.markdown(f"""<div class='metric-card'>
                    <div class='metric-num' style='color:#E24B4A;font-size:20px;'>₹{fib['swing_high']:,.2f}</div>
                    <div class='metric-lbl'>SWING HIGH (top)</div></div>""", unsafe_allow_html=True)
                zone_color = "#00c853" if fib["near_fib"] else "#445566"
                zone_text  = fib["fib_zone"] if fib["near_fib"] else "Not at Fib"
                f3.markdown(f"""<div class='metric-card'>
                    <div class='metric-num' style='color:{zone_color};font-size:20px;'>{zone_text}</div>
                    <div class='metric-lbl'>CURRENT FIB ZONE</div></div>""", unsafe_allow_html=True)

                # Fib levels table
                fib_rows = []
                for label, price in fib["levels"].items():
                    dist_pct = (last_price - price) / price * 100
                    is_near  = abs(dist_pct) < 1.5
                    fib_rows.append({
                        "Level":        label,
                        "Price (₹)":    f"₹{price:,.2f}",
                        "Distance":     f"{dist_pct:+.2f}%",
                        "Status":       "◉ PRICE HERE" if is_near else ("Above ↑" if last_price > price else "Below ↓"),
                        "Significance": "★★★ Golden Ratio" if label == "61.8%"
                                        else "★★ Strong"   if label in ("38.2%","50.0%","78.6%")
                                        else "★ Moderate",
                    })
                st.dataframe(pd.DataFrame(fib_rows), use_container_width=True, hide_index=True)

                if fib["near_fib"]:
                    st.markdown(f"""<div class='info-box'>
                        🎯 Price is within 1.5% of the <b>{fib['fib_zone']}</b> Fibonacci level
                        (₹{fib['levels'][fib['fib_zone']]:,.2f}).
                        Watch for a reversal candle or volume spike to confirm entry.
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class='warn-box'>
                        ℹ️ Price is not currently at a key Fib level. Wait for price to approach
                        38.2%, 50%, 61.8%, or 78.6% before acting.
                    </div>""", unsafe_allow_html=True)

                # ── Section 2: Pivot Points ───────────────────────────
                st.markdown("---")
                st.markdown(f"### 🔵 Pivot Points — {pa_piv_method}")

                method_notes = {
                    "Classic":   "PP = (H+L+C)/3. Most widely used. Good for daily & weekly timeframes.",
                    "Woodie":    "PP = (H+L+2C)/4. Weights close more heavily. Preferred by day traders.",
                    "Camarilla": "Uses close + H-L range × fixed multipliers. Excellent for intraday breakouts.",
                }
                st.markdown(f"<div class='info-box'>📖 {method_notes[pa_piv_method]}</div>",
                            unsafe_allow_html=True)

                p1, p2, p3 = st.columns(3)
                for col, keys, header, color in [
                    (p1, ["R3","R2","R1"], "Resistance Levels", "#E24B4A"),
                    (p2, ["PP"],           "Pivot Point",        "#e8f4ff"),
                    (p3, ["S1","S2","S3"], "Support Levels",     "#1D9E75"),
                ]:
                    col.markdown(
                        f"<div style='color:{color};font-size:11px;letter-spacing:2px;"
                        f"margin-bottom:6px;'>{header}</div>", unsafe_allow_html=True)
                    for k in keys:
                        dist = (last_price - pivs[k]) / pivs[k] * 100
                        near = abs(dist) < 1.0
                        badge = " ◉" if near else ""
                        col.markdown(f"""<div class='metric-card' style='margin-bottom:6px;padding:10px;'>
                            <div style='color:{color};font-size:16px;font-weight:700;'>
                                {k}: ₹{pivs[k]:,.2f}{badge}</div>
                            <div style='font-size:11px;color:#445566;'>{dist:+.2f}% from price</div>
                        </div>""", unsafe_allow_html=True)

                # Near-pivot alert
                nearest_piv      = min(pivs, key=lambda k: abs(pivs[k] - last_price))
                nearest_piv_dist = abs(pivs[nearest_piv] - last_price) / last_price * 100
                if nearest_piv_dist < 1.0:
                    piv_col = ("#E24B4A" if nearest_piv.startswith("R")
                               else "#1D9E75" if nearest_piv.startswith("S")
                               else "#e8f4ff")
                    piv_msg = ("Resistance zone — watch for reversal or breakout." if nearest_piv.startswith("R")
                               else "Support zone — potential bounce area."         if nearest_piv.startswith("S")
                               else "At Pivot Point — direction of break sets the bias.")
                    st.markdown(f"""<div class='info-box' style='border-left-color:{piv_col};'>
                        🎯 Price is within 1% of <b>{nearest_piv}</b>
                        (₹{pivs[nearest_piv]:,.2f}). {piv_msg}
                    </div>""", unsafe_allow_html=True)

                # ── Section 3: Combined Chart ─────────────────────────
                st.markdown("---")
                st.markdown("### 📊 Combined Chart — Fib + Pivots")
                result_pa = analyze(pa_sym, df_pa)
                st.plotly_chart(
                    build_chart(pa_sym, df_pa, result_pa,
                                show_fib=True, show_pivots=True,
                                show_pivot_method=pa_piv_method),
                    use_container_width=True
                )

                # ── Section 4: Suggested Trade Setup ─────────────────
                st.markdown("---")
                st.markdown("### 🎯 Suggested Trade Setup")

                key_fib_labels = ("38.2%", "50.0%", "61.8%", "78.6%")
                if fib["near_fib"] and fib["fib_zone"] in key_fib_labels:
                    fib_price   = fib["levels"][fib["fib_zone"]]
                    atr_val     = float(calc_atr(
                        df_pa["High"].astype(float),
                        df_pa["Low"].astype(float),
                        df_pa["Close"].astype(float)
                    ).iloc[-1])
                    entry_sugg  = round(last_price, 2)
                    stop_sugg   = round(fib_price - atr_val * 1.5, 2)
                    # Target = previous Fib level (next higher up)
                    all_labels  = list(fib["levels"].keys())
                    cur_idx     = all_labels.index(fib["fib_zone"])
                    target_lbl  = all_labels[cur_idx - 1] if cur_idx > 0 else all_labels[0]
                    target_sugg = round(fib["levels"][target_lbl], 2)
                    rr          = ((target_sugg - entry_sugg) / (entry_sugg - stop_sugg)
                                   if entry_sugg > stop_sugg else 0)

                    ts1, ts2, ts3, ts4 = st.columns(4)
                    for col, lbl, val, color in [
                        (ts1, "ENTRY",  f"₹{entry_sugg:,.2f}",  "#4da6ff"),
                        (ts2, "STOP",   f"₹{stop_sugg:,.2f}",   "#E24B4A"),
                        (ts3, "TARGET", f"₹{target_sugg:,.2f}", "#00c853"),
                        (ts4, "R:R",    f"{rr:.1f}:1",           "#c084fc"),
                    ]:
                        col.markdown(f"""<div class='metric-card'>
                            <div class='metric-num' style='color:{color};font-size:20px;'>{val}</div>
                            <div class='metric-lbl'>{lbl}</div></div>""", unsafe_allow_html=True)

                    box_class = "info-box" if rr >= 2 else "warn-box"
                    rr_msg    = ("✅ Good R:R — meets 2:1 minimum threshold." if rr >= 2
                                 else "⚠️ R:R below 2:1. Consider waiting for a deeper pullback.")
                    st.markdown(f"""<div class='{box_class}'>
                        <b>Fib Bounce Setup</b> at {fib['fib_zone']} level.
                        Stop: 1.5× ATR below Fib zone.
                        Target: {target_lbl} Fib level (₹{target_sugg:,.2f}). {rr_msg}
                    </div>""", unsafe_allow_html=True)

                    # One-click add to journal
                    st.markdown("#### ➕ Log this Setup")
                    lc1, lc2, lc3 = st.columns(3)
                    log_qty = lc1.number_input("Qty", min_value=1, value=10, step=1, key="pa_qty")
                    log_status = lc2.selectbox("Status", ["OPEN","CLOSED WIN","CLOSED LOSS"], key="pa_status")
                    log_exit   = lc3.number_input("Exit Price (0=open)", min_value=0.0,
                                                   value=0.0, step=0.5, key="pa_exit")
                    if st.button("💾 Add to Trade Journal", use_container_width=True):
                        pnl = (log_exit - entry_sugg) * log_qty if log_exit > 0 else 0
                        st.session_state.journal.append({
                            "symbol": pa_sym, "date": str(datetime.today().date()),
                            "entry":  entry_sugg, "stop": stop_sugg,
                            "target": target_sugg, "exit": log_exit,
                            "qty":    log_qty, "setup": f"Fib Bounce {fib['fib_zone']}",
                            "status": log_status, "pnl": round(pnl, 2),
                            "rr":     round(rr, 2), "notes": f"{pa_piv_method} pivot near {nearest_piv}"
                        })
                        save_json(JOURNAL_FILE, st.session_state.journal)
                        st.success("✅ Trade logged to journal!")
                else:
                    st.markdown("""<div class='warn-box'>
                        ⏳ No Fib Bounce setup at current price.
                        Wait for price to reach 38.2%, 50%, 61.8%, or 78.6% before entering.
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style='text-align:center;font-size:10px;color:#334455;letter-spacing:1px;'>
        EDGE SCANNER · NSE SWING TRADING SYSTEM · DATA VIA YAHOO FINANCE · NOT INVESTMENT ADVICE
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
