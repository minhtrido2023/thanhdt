#!/usr/bin/env python3
"""
backtest_qt_v3.py
==================
QT v3 — Bull-Age Aware Risk Management.

Key additions over v2:
  1. bull_age tracking: longer bull → higher fragility → tighter risk controls
  2. FORCE EXIT when regime turns DOWN (state 4-5 → ≤3): liquidate over 5 days
  3. DYNAMIC trail stop based on bull_age + EX-BULL
  4. PROFIT TAKING ladder in late bull
"""
import warnings; warnings.filterwarnings("ignore")
import os, pickle, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Quality universe (same as v2) ────────────────────────────────────
print("[1] Building quality universe (relaxed) ...", flush=True)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
quality_at_q = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("quarter").reset_index(drop=True)
    for i, row in g.iterrows():
        if i < 8: continue
        history = g.iloc[:i+1]
        pct_ab = (history["tier"].isin(["A","B"])).sum() / len(history) * 100
        quality_at_q[(tk, row["quarter"])] = {
            "pct_AB": pct_ab,
            "latest_tier": row["tier"],
            "sub": row["sub"],
        }
print(f"  Quality lookup: {len(quality_at_q):,} entries")

# ─── 2. Load panel + compute features ────────────────────────────────────
print("\n[2] Loading panel + computing features ...", flush=True)
with open("data/qt_panel_2014_2026.pkl", "rb") as f:
    panel = pickle.load(f)
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
panel["hi_52w"] = panel.groupby("ticker")["Close"].transform(
    lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"] = (panel["Close"] / panel["hi_52w"] - 1) * 100
panel["pe_z"] = ((panel["PE"] - panel["PE_MA5Y"]) / panel["PE_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["pb_z"] = ((panel["PB"] - panel["PB_MA5Y"]) / panel["PB_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["vs_MA50_pct"] = (panel["Close"] / panel["MA50"] - 1) * 100
panel["vs_MA200_pct"] = (panel["Close"] / panel["MA200"] - 1) * 100
panel["vol_ratio"] = panel["Volume"] / panel["Volume_3M_P50"]
panel["rsi"] = panel["D_RSI"] * 100
print(f"  Loaded {len(panel):,} rows")

# ─── 3. 5-state + bull_age tracking ──────────────────────────────────────
print("\n[3] Loading 5-state + computing bull_age ...", flush=True)
state = pd.read_csv("data/vnindex_5state.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state["state_prev"] = state["state"].shift(1)

# Bull_age: consecutive days in state >= 4
state["bull_age"] = 0
bull_counter = 0
for i in range(len(state)):
    if state.iloc[i]["state"] >= 4:
        bull_counter += 1
    else:
        bull_counter = 0
    state.at[i, "bull_age"] = bull_counter

# Turn UP: state {1,2} → ≥3
state["turn_up"] = ((state["state_prev"].isin([1,2])) & (state["state"] >= 3)).astype(int)
# Turn DOWN: state {4,5} → ≤3 (the critical force-exit trigger)
state["turn_down"] = ((state["state_prev"].isin([4,5])) & (state["state"] <= 3)).astype(int)

state["days_since_turn_up"] = np.inf
last_turn_idx = -1
for i in range(len(state)):
    if state.iloc[i]["turn_up"] == 1:
        last_turn_idx = i
    if last_turn_idx >= 0:
        state.at[i, "days_since_turn_up"] = i - last_turn_idx

# Mode + bull_age category
def classify_mode(row):
    s = row["state"]
    dst = row["days_since_turn_up"]
    bage = row["bull_age"]
    if s in [1, 2]: return "PAUSE", "BEAR"
    if dst <= 60: return "RECOVERY", "RECOVERY"
    if s == 3: return "NEUTRAL", "NEUTRAL"
    # State 4 or 5
    if bage < 60: return "BULL_EARLY", "EARLY"
    if bage < 180: return "BULL_MID", "MID"
    if bage < 365: return "BULL_LATE", "LATE"
    return "BULL_EXTREME", "EXTREME"

state[["mode","bull_phase"]] = state.apply(lambda r: pd.Series(classify_mode(r)), axis=1)
state_map = state.set_index("time")[["state","state_prev","mode","bull_phase","bull_age","turn_down"]]
state_map_full = state_map.reindex(pd.date_range(state["time"].min(), state["time"].max(), freq="D")).ffill()

mode_dist = state["mode"].value_counts().to_dict()
print(f"  Mode distribution: {mode_dist}")
print(f"  Turn UP: {state['turn_up'].sum()}, Turn DOWN: {state['turn_down'].sum()}")
print(f"  Max bull_age in history: {state['bull_age'].max()} days")
print(f"  Phase distribution: {state['bull_phase'].value_counts().to_dict()}")

# ─── 4. Pivot setup ──────────────────────────────────────────────────────
print("\n[4] Setting up pivots ...", flush=True)
trading_days = sorted(panel["time"].unique())
def piv(col): return panel.pivot_table(index="time", columns="ticker", values=col, aggfunc="first").sort_index().ffill()
px_close = piv("Close")
px_open = piv("Open")
ma200 = piv("MA200")
rsi = piv("rsi")
pe_z_p = piv("pe_z")
pb_z_p = piv("pb_z")
dd_52w_p = piv("dd_52w_pct")
vs_ma50 = piv("vs_MA50_pct")
vs_ma200 = piv("vs_MA200_pct")
vol_rat = piv("vol_ratio")
macd_p = piv("D_MACDdiff")
liq_p = piv("Volume_3M_P50")

# FA release lookup
fa_release_map = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("time")
    fa_release_map[tk] = g[["time","Release_Date","quarter","tier","score"]].copy()
    fa_release_map[tk]["eff_release"] = fa_release_map[tk]["Release_Date"].fillna(
        fa_release_map[tk]["time"] + pd.Timedelta(days=60))

def get_fa_at(ticker, date):
    if ticker not in fa_release_map: return None
    g = fa_release_map[ticker]
    avail = g[g["eff_release"] <= date]
    if len(avail) == 0: return None
    return quality_at_q.get((ticker, avail.iloc[-1]["quarter"]))

# ─── 5. v3 Simulator ────────────────────────────────────────────────────
print("\n[5] Running QT v3 backtest ...", flush=True)

MAX_POSITIONS = 10
LIQ_CAP_PCT = 0.20
MAX_FILL_DAYS = 5
SLIP_IN = 0.001
SLIP_OUT = 0.0015
TAX_SALE = 0.001
DEPOSIT_RATE = 0.01
HARD_STOP = -0.15
BELOW_MA200_DAYS = 5
BLACKLIST_DAYS = 60
FORCE_EXIT_DAYS = 5  # turn-down → liquidate over 5 days

# Position sizing scale based on bull phase
SIZE_SCALE = {
    "RECOVERY":     1.0,
    "NEUTRAL":      0.9,
    "EARLY":        1.0,
    "MID":          0.8,
    "LATE":         0.6,
    "EXTREME":      0.3,
    "BEAR":         0.0,  # no entries
}

# Trail stop scale based on bull phase
TRAIL_CONFIG = {
    "RECOVERY":  {"pct": 0.25, "activation": 0.30},
    "NEUTRAL":   {"pct": 0.22, "activation": 0.25},
    "EARLY":     {"pct": 0.25, "activation": 0.30},
    "MID":       {"pct": 0.20, "activation": 0.25},
    "LATE":      {"pct": 0.15, "activation": 0.20},
    "EXTREME":   {"pct": 0.10, "activation": 0.15},
    "BEAR":      {"pct": 0.10, "activation": 0.10},
}

start_dt = pd.Timestamp("2014-04-01")
end_dt = pd.Timestamp("2026-05-13")
sim_days = [d for d in trading_days if start_dt <= d <= end_dt]
daily_cash_rate = (1 + DEPOSIT_RATE) ** (1/365.25) - 1

cash = INIT_NAV
positions = {}  # ticker -> dict
blacklist = {}
nav_history = []
trades = []
pending_buys = []
pending_sells = []
force_exit_queue = []  # list of (ticker, days_remaining_to_exit)

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        mode_now = state_map_full.loc[dt]["mode"] if dt in state_map_full.index else "?"
        phase_now = state_map_full.loc[dt]["bull_phase"] if dt in state_map_full.index else "?"
        bage = int(state_map_full.loc[dt]["bull_age"]) if dt in state_map_full.index else 0
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={nav/1e9:.2f}B pos={len(positions)} mode={mode_now} phase={phase_now} bull_age={bage}d", flush=True)
    cash *= (1 + daily_cash_rate)

    # Get today's regime
    if dt in state_map_full.index:
        r = state_map_full.loc[dt]
        mode_today = r["mode"]
        phase_today = r["bull_phase"]
        turn_down_today = r["turn_down"] == 1
    else:
        mode_today = "PAUSE"; phase_today = "BEAR"; turn_down_today = False

    # Handle FORCE EXIT on turn DOWN
    if turn_down_today and len(positions) > 0:
        for tk in positions:
            if not any(fe["ticker"] == tk for fe in force_exit_queue):
                force_exit_queue.append({"ticker":tk, "days_left":FORCE_EXIT_DAYS, "reason":"REGIME_TURN_DOWN"})

    # T+1: Pending sells (force-exit queue, regular exits)
    new_sells = []
    for s in pending_sells:
        tk = s["ticker"]
        if tk not in positions: continue
        if tk not in px_open.columns: continue
        fill_px = px_open.at[dt, tk]
        if pd.isna(fill_px) or fill_px <= 0: new_sells.append(s); continue
        pos = positions[tk]
        gross = pos["shares"] * fill_px * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        trades.append({"dt":dt, "ticker":tk, "side":s["reason"], "shares":pos["shares"],
                       "px":fill_px, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                       "ret_pct":(fill_px/pos["entry_px"]-1)*100, "hold_days":(dt-pos["entry_dt"]).days,
                       "entry_phase":pos.get("entry_phase","?")})
        blacklist[tk] = dt + pd.Timedelta(days=BLACKLIST_DAYS)
        del positions[tk]
    pending_sells = new_sells

    # Process force-exit queue (sell 1/N per day until done)
    new_force_queue = []
    for fe in force_exit_queue:
        tk = fe["ticker"]
        if tk not in positions: continue  # already sold
        if fe["days_left"] <= 0: continue  # expired
        # Sell partial (1/days_left fraction)
        fraction = 1.0 / max(fe["days_left"], 1)
        if tk not in px_open.columns:
            new_force_queue.append({"ticker":tk, "days_left":fe["days_left"]-1, "reason":fe["reason"]})
            continue
        fill_px = px_open.at[dt, tk]
        if pd.isna(fill_px) or fill_px <= 0:
            new_force_queue.append({"ticker":tk, "days_left":fe["days_left"]-1, "reason":fe["reason"]})
            continue
        pos = positions[tk]
        shares_to_sell = pos["shares"] * fraction
        gross = shares_to_sell * fill_px * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        trades.append({"dt":dt, "ticker":tk, "side":fe["reason"], "shares":shares_to_sell,
                       "px":fill_px, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                       "ret_pct":(fill_px/pos["entry_px"]-1)*100, "hold_days":(dt-pos["entry_dt"]).days,
                       "entry_phase":pos.get("entry_phase","?")})
        pos["shares"] -= shares_to_sell
        if pos["shares"] < 0.01 or fe["days_left"] == 1:
            del positions[tk]
            blacklist[tk] = dt + pd.Timedelta(days=BLACKLIST_DAYS)
        else:
            new_force_queue.append({"ticker":tk, "days_left":fe["days_left"]-1, "reason":fe["reason"]})
    force_exit_queue = new_force_queue

    # T+1: Pending buys
    new_buys = []
    for b in pending_buys:
        tk = b["ticker"]
        if tk in positions: continue
        if len(positions) >= MAX_POSITIONS: continue
        if tk in blacklist and blacklist[tk] > dt: continue
        if tk not in px_open.columns: continue
        fill_px = px_open.at[dt, tk]
        if pd.isna(fill_px) or fill_px <= 0: new_buys.append(b); continue
        adv = liq_p.at[dt, tk] if tk in liq_p.columns else 0
        if pd.isna(adv) or adv <= 0: adv = 1e6
        max_pos_vnd = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fill_px
        mtm_now = sum(p["shares"] * px_close.at[dt, t_] for t_, p in positions.items()
                      if t_ in px_close.columns and pd.notna(px_close.at[dt, t_]))
        nav_now = cash + mtm_now
        size_scale = SIZE_SCALE.get(b.get("phase","NEUTRAL"), 0.8)
        target = (nav_now / MAX_POSITIONS) * size_scale * 0.98
        alloc = min(target, max_pos_vnd)
        if alloc < 1e6: continue
        eff_px = fill_px * (1 + SLIP_IN)
        shares = alloc / eff_px
        cost = shares * eff_px
        if cost > cash: continue
        cash -= cost
        positions[tk] = {"entry_dt":dt, "entry_px":fill_px, "shares":shares,
                          "peak_px":fill_px, "below_ma200_count":0,
                          "entry_mode":b.get("mode","?"), "entry_phase":b.get("phase","?"),
                          "profit_taken_50":False, "profit_taken_30":False}
        trades.append({"dt":dt, "ticker":tk, "side":"BUY", "shares":shares,
                        "px":fill_px, "net":-cost, "entry_dt":dt, "entry_px":fill_px,
                        "ret_pct":0, "hold_days":0, "entry_phase":b.get("phase","?")})
    pending_buys = []

    # Check exits + profit-taking
    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue
        if p_today > pos["peak_px"]: pos["peak_px"] = p_today
        gain = p_today/pos["entry_px"] - 1

        exit_reason = None

        # HARD STOP -15%
        if gain <= HARD_STOP:
            exit_reason = "HARD_STOP_15"

        # DYNAMIC TRAIL based on current phase
        if exit_reason is None:
            tcfg = TRAIL_CONFIG.get(phase_today, TRAIL_CONFIG["NEUTRAL"])
            if pos["peak_px"]/pos["entry_px"] - 1 >= tcfg["activation"]:
                if p_today < pos["peak_px"] * (1 - tcfg["pct"]):
                    exit_reason = f"TRAIL_{phase_today}"

        # Profit taking ladder in late bull (partial sell)
        if exit_reason is None:
            if phase_today == "LATE" and gain >= 0.50 and not pos["profit_taken_50"]:
                # Exit 30% of position
                fraction = 0.30
                shares_to_sell = pos["shares"] * fraction
                if tk in px_open.columns:
                    pos_open = px_open.at[dt, tk]
                    if pd.notna(pos_open):
                        net = shares_to_sell * pos_open * (1 - SLIP_OUT) * (1 - TAX_SALE)
                        cash += net
                        trades.append({"dt":dt, "ticker":tk, "side":"PROFIT_TAKE_LATE", "shares":shares_to_sell,
                                       "px":pos_open, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                                       "ret_pct":(pos_open/pos["entry_px"]-1)*100, "hold_days":(dt-pos["entry_dt"]).days,
                                       "entry_phase":pos.get("entry_phase","?")})
                        pos["shares"] -= shares_to_sell
                        pos["profit_taken_50"] = True
            elif phase_today == "EXTREME" and gain >= 0.30 and not pos["profit_taken_30"]:
                fraction = 0.50
                shares_to_sell = pos["shares"] * fraction
                if tk in px_open.columns:
                    pos_open = px_open.at[dt, tk]
                    if pd.notna(pos_open):
                        net = shares_to_sell * pos_open * (1 - SLIP_OUT) * (1 - TAX_SALE)
                        cash += net
                        trades.append({"dt":dt, "ticker":tk, "side":"PROFIT_TAKE_EXTREME", "shares":shares_to_sell,
                                       "px":pos_open, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                                       "ret_pct":(pos_open/pos["entry_px"]-1)*100, "hold_days":(dt-pos["entry_dt"]).days,
                                       "entry_phase":pos.get("entry_phase","?")})
                        pos["shares"] -= shares_to_sell
                        pos["profit_taken_30"] = True

        # MA200 break
        if exit_reason is None and tk in ma200.columns:
            m200 = ma200.at[dt, tk]
            if pd.notna(m200):
                if p_today < m200:
                    pos["below_ma200_count"] += 1
                    if pos["below_ma200_count"] >= BELOW_MA200_DAYS:
                        exit_reason = "TREND_BREAK"
                else:
                    pos["below_ma200_count"] = 0

        # FA drop
        if exit_reason is None:
            fa_info = get_fa_at(tk, dt)
            if fa_info is not None and fa_info["latest_tier"] in ("C","D","E"):
                exit_reason = "FA_DROP"

        if exit_reason:
            pending_sells.append({"ticker":tk, "reason":exit_reason})

    # Scan for BUY signals (only if not BEAR/PAUSE)
    if mode_today not in ("PAUSE",) and len(positions) < MAX_POSITIONS and len(force_exit_queue) == 0:
        max_buys = 3 if mode_today == "RECOVERY" else 1
        buys_today = 0
        for tk in px_close.columns:
            if buys_today >= max_buys: break
            if tk in positions: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            if any(b["ticker"] == tk for b in pending_buys): continue

            fa_info = get_fa_at(tk, dt)
            if fa_info is None or fa_info["pct_AB"] < 50: continue
            if fa_info["latest_tier"] not in ("A","B"): continue

            adv_vnd = liq_p.at[dt, tk] if tk in liq_p.columns else 0
            p = px_close.at[dt, tk]
            if pd.isna(p) or pd.isna(adv_vnd) or adv_vnd * p < 3e9: continue

            pez = pe_z_p.at[dt, tk] if tk in pe_z_p.columns else np.nan
            pbz = pb_z_p.at[dt, tk] if tk in pb_z_p.columns else np.nan
            ddv = dd_52w_p.at[dt, tk] if tk in dd_52w_p.columns else np.nan
            rsi_now = rsi.at[dt, tk] if tk in rsi.columns else np.nan
            vs50 = vs_ma50.at[dt, tk] if tk in vs_ma50.columns else np.nan
            vs200 = vs_ma200.at[dt, tk] if tk in vs_ma200.columns else np.nan
            volr = vol_rat.at[dt, tk] if tk in vol_rat.columns else np.nan
            macd = macd_p.at[dt, tk] if tk in macd_p.columns else np.nan

            qualified = False
            if mode_today == "RECOVERY":
                v_under = (pez < 0) or (pbz < 0) or (ddv < -20)
                if v_under and pd.notna(rsi_now) and rsi_now > 35:
                    qualified = True
            elif mode_today in ("BULL_EARLY","BULL_MID","BULL_LATE","BULL_EXTREME"):
                # Stricter for late bull
                if phase_today in ("LATE","EXTREME"):
                    # Very strict
                    if (pd.notna(pez) and pez < -0.5 and pd.notna(vs50) and vs50 > 0
                        and pd.notna(rsi_now) and 45 <= rsi_now <= 65
                        and pd.notna(volr) and volr > 2.0):
                        qualified = True
                else:
                    # Normal bull
                    if (pd.notna(vs50) and vs50 > 0 and pd.notna(vs200) and vs200 > 0
                        and pd.notna(rsi_now) and 50 <= rsi_now <= 70
                        and pd.notna(volr) and volr > 1.5
                        and pd.notna(pez) and pez < 0
                        and pd.notna(macd) and macd > 0):
                        qualified = True
            elif mode_today == "NEUTRAL":
                if (pd.notna(pez) and pez < -0.5 and pd.notna(vs200) and vs200 > 0
                    and pd.notna(rsi_now) and rsi_now > 45):
                    qualified = True

            if qualified:
                pending_buys.append({"ticker":tk, "mode":mode_today, "phase":phase_today})
                buys_today += 1

    # MTM
    mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt, "nav":nav, "cash":cash, "equity":mtm, "n_pos":len(positions),
                         "mode":mode_today, "phase":phase_today})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} trades, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B", flush=True)

# Metrics
def cm(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
    rets = s.pct_change().dropna()
    sharpe = rets.mean()/rets.std()*np.sqrt(len(rets)/yrs) if rets.std() > 0 else 0
    dd = (s - s.cummax())/s.cummax()
    mdd = dd.min()
    return {"CAGR":cagr*100, "Sharpe":sharpe, "MaxDD":mdd*100, "Calmar":cagr/abs(mdd) if mdd<0 else 0}

vni = bq_query("SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2014-01-01' AND t.Close > 100 ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"].reindex(nav_df.index).ffill()

print("\n" + "="*100)
print("  QT v3 — BULL-AGE AWARE — 12y BACKTEST RESULTS")
print("="*100)
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2018",     pd.Timestamp("2018-01-01"), pd.Timestamp("2018-12-31")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]
print(f"\n  {'Period':<14}{'CAGR':>10}{'Sharpe':>11}{'MaxDD':>9}{'Calmar':>10}{'VNI':>10}{'alpha':>10}")
for pname, ps, pe in periods:
    m = cm(nav_df["nav"], ps, pe)
    vm = cm(vni_px, ps, pe)
    if m is None or vm is None: continue
    alpha = m["CAGR"] - vm["CAGR"]
    print(f"  {pname:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+11.2f}{m['MaxDD']:>+8.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+9.2f}%{alpha:>+9.2f}pp")

if len(trades_df) > 0:
    print(f"\n  --- Exit breakdown ---")
    exits = trades_df[trades_df["side"] != "BUY"]
    for reason, g in exits.groupby("side"):
        print(f"    {reason:<25}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, WR={(g['ret_pct']>0).mean()*100:.1f}%")
    print(f"\n  --- By entry phase ---")
    for phase, g in exits.groupby("entry_phase"):
        print(f"    {phase:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, WR={(g['ret_pct']>0).mean()*100:.1f}%")

nav_df.to_csv("data/qt_v3_nav.csv")
trades_df.to_csv("data/qt_v3_trades.csv", index=False)
print("\nSaved: qt_v3_nav.csv, qt_v3_trades.csv")
