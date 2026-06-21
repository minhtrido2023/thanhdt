#!/usr/bin/env python3
"""
backtest_qt_v2.py
==================
QT v2 — Regime-Turn Aware Quality+Tactical framework.

Improvements over v1:
  - 4 entry modes by regime: RECOVERY / BULL_STRICT / NEUTRAL / PAUSE
  - Universe relaxed (≥50% A+B, ≥8Q, liq ≥3B)
  - Aggressive post-turn entries (no MA200 requirement)
  - Strict bull mode entries (avoid peak buying)
  - Hard stop -15% (no activation requirement)
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
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Quality universe (relaxed) ───────────────────────────────────────
print("[1] Building relaxed quality universe ...", flush=True)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)

quality_at_q = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("quarter").reset_index(drop=True)
    for i, row in g.iterrows():
        if i < 8: continue  # ≥8Q (was 12)
        history = g.iloc[:i+1]
        pct_ab = (history["tier"].isin(["A","B"])).sum() / len(history) * 100
        quality_at_q[(tk, row["quarter"])] = {
            "pct_AB": pct_ab,
            "latest_tier": row["tier"],
            "score": row["score"],
            "sub": row["sub"],
            "n_q": len(history),
        }
print(f"  Quality lookup: {len(quality_at_q):,} entries (relaxed: ≥8Q, ≥50% A+B)")

# ─── 2. Load cached TA panel ─────────────────────────────────────────────
print("\n[2] Loading TA panel from cache ...", flush=True)
panel_path = "data/qt_panel_2014_2026.pkl"
with open(panel_path, "rb") as f:
    panel = pickle.load(f)
print(f"  Loaded {len(panel):,} rows")

panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
print("  Computing derived features ...", flush=True)
panel["hi_52w"] = panel.groupby("ticker")["Close"].transform(
    lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"] = (panel["Close"] / panel["hi_52w"] - 1) * 100
panel["pe_z"] = ((panel["PE"] - panel["PE_MA5Y"]) / panel["PE_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["pb_z"] = ((panel["PB"] - panel["PB_MA5Y"]) / panel["PB_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["vs_MA50_pct"] = (panel["Close"] / panel["MA50"] - 1) * 100
panel["vs_MA200_pct"] = (panel["Close"] / panel["MA200"] - 1) * 100
panel["vol_ratio"] = panel["Volume"] / panel["Volume_3M_P50"]
panel["rsi"] = panel["D_RSI"] * 100

# ─── 3. Load 5-state regime + compute turn windows ──────────────────────
print("\n[3] Loading 5-state regime + detecting turn windows ...", flush=True)
state = pd.read_csv("data/vnindex_5state.csv", parse_dates=["time"]).sort_values("time").reset_index(drop=True)
state["state_prev"] = state["state"].shift(1)
# Turn UP: state transitions from {1,2} to >=3
state["turn_up"] = ((state["state_prev"].isin([1,2])) & (state["state"] >= 3)).astype(int)
# Mark "post_turn_window": 60 days after each turn UP
state["days_since_turn"] = np.inf
last_turn_idx = -1
for i in range(len(state)):
    if state.iloc[i]["turn_up"] == 1:
        last_turn_idx = i
    if last_turn_idx >= 0:
        state.at[i, "days_since_turn"] = i - last_turn_idx

# State lookup
state_map = state.set_index("time")[["state","state_prev","turn_up","days_since_turn"]]
state_map_full = state_map.reindex(pd.date_range(state["time"].min(), state["time"].max(), freq="D")).ffill()
print(f"  Turn UP events: {state['turn_up'].sum()}")

# Entry mode classification
def entry_mode(dt):
    if dt not in state_map_full.index: return "UNKNOWN"
    r = state_map_full.loc[dt]
    s = r["state"]
    dst = r["days_since_turn"]
    if s in [1, 2]:
        return "PAUSE"  # Bear/Crisis — no entries
    elif dst <= 60:
        return "RECOVERY"  # Post-turn aggressive
    elif s in [4, 5]:
        return "BULL_STRICT"  # Steady bull, top-decile only
    elif s == 3:
        return "NEUTRAL"  # Standard entries
    return "UNKNOWN"

# Build mode lookup
state_map_full["mode"] = state_map_full.index.to_series().apply(entry_mode)
mode_counts = state_map_full["mode"].value_counts().to_dict()
print(f"  Mode distribution: {mode_counts}")

# ─── 4. Setup pivots for simulator ───────────────────────────────────────
print("\n[4] Setting up pivots ...", flush=True)
trading_days = sorted(panel["time"].unique())
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
px_open  = panel.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().ffill()
ma200    = panel.pivot_table(index="time", columns="ticker", values="MA200", aggfunc="first").sort_index().ffill()
rsi      = panel.pivot_table(index="time", columns="ticker", values="rsi", aggfunc="first").sort_index().ffill()
pe_z_p   = panel.pivot_table(index="time", columns="ticker", values="pe_z", aggfunc="first").sort_index().ffill()
pb_z_p   = panel.pivot_table(index="time", columns="ticker", values="pb_z", aggfunc="first").sort_index().ffill()
dd_52w_p = panel.pivot_table(index="time", columns="ticker", values="dd_52w_pct", aggfunc="first").sort_index().ffill()
vs_ma50  = panel.pivot_table(index="time", columns="ticker", values="vs_MA50_pct", aggfunc="first").sort_index().ffill()
vs_ma200 = panel.pivot_table(index="time", columns="ticker", values="vs_MA200_pct", aggfunc="first").sort_index().ffill()
vol_rat  = panel.pivot_table(index="time", columns="ticker", values="vol_ratio", aggfunc="first").sort_index().ffill()
macd_p   = panel.pivot_table(index="time", columns="ticker", values="D_MACDdiff", aggfunc="first").sort_index().ffill()
liq_p    = panel.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill()

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
    last = avail.iloc[-1]
    return quality_at_q.get((ticker, last["quarter"]))

# ─── 5. Simulator ────────────────────────────────────────────────────────
print("\n[5] Running 12y QT v2 backtest ...", flush=True)

MAX_POSITIONS = 10
LIQ_CAP_PCT = 0.20
MAX_FILL_DAYS = 5
SLIP_IN = 0.001
SLIP_OUT = 0.0015
TAX_SALE = 0.001
DEPOSIT_RATE = 0.01
HARD_STOP = -0.15  # cứng hơn v1
TRAIL_PCT = 0.25
TRAIL_ACTIVATION = 0.30  # higher gain required to activate trail
BELOW_MA200_DAYS = 5
BLACKLIST_DAYS = 60
MAX_BUYS_PER_DAY_RECOVERY = 3
MAX_BUYS_PER_DAY_OTHER = 1

start_dt = pd.Timestamp("2014-04-01")
end_dt = pd.Timestamp("2026-05-13")
sim_days = [d for d in trading_days if start_dt <= d <= end_dt]
daily_cash_rate = (1 + DEPOSIT_RATE) ** (1/365.25) - 1

cash = INIT_NAV
positions = {}
blacklist = {}
nav_history = []
trades = []
pending_buys = []
pending_sells = []

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm_temp = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
                       if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_temp = cash + mtm_temp
        mode = state_map_full.loc[dt]["mode"] if dt in state_map_full.index else "?"
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={nav_temp/1e9:.2f}B pos={len(positions)} mode={mode}", flush=True)
    cash *= (1 + daily_cash_rate)

    # T+1: Execute pending sells
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
                       "entry_mode":pos.get("entry_mode","?")})
        blacklist[tk] = dt + pd.Timedelta(days=BLACKLIST_DAYS)
        del positions[tk]
    pending_sells = new_sells

    # T+1: Execute pending buys
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
        mtm = sum(p["shares"] * px_close.at[dt, t_] for t_, p in positions.items()
                  if t_ in px_close.columns and pd.notna(px_close.at[dt, t_]))
        nav_now = cash + mtm
        target = (nav_now / MAX_POSITIONS) * 0.98
        alloc = min(target, max_pos_vnd)
        if alloc < 1e6: continue
        eff_px = fill_px * (1 + SLIP_IN)
        shares = alloc / eff_px
        cost = shares * eff_px
        if cost > cash: continue
        cash -= cost
        positions[tk] = {"entry_dt":dt, "entry_px":fill_px, "shares":shares,
                          "peak_px":fill_px, "below_ma200_count":0, "entry_mode":b.get("mode","?")}
        trades.append({"dt":dt, "ticker":tk, "side":"BUY", "shares":shares,
                        "px":fill_px, "net":-cost, "entry_dt":dt, "entry_px":fill_px,
                        "ret_pct":0, "hold_days":0, "entry_mode":b.get("mode","?")})
    pending_buys = []

    # Check exits — daily signal at close, execute T+1 open
    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue
        if p_today > pos["peak_px"]: pos["peak_px"] = p_today
        gain = p_today/pos["entry_px"] - 1
        exit_reason = None

        # HARD STOP -15% (always active)
        if gain <= HARD_STOP:
            exit_reason = "HARD_STOP_15"

        # TRAIL (activate after +30% gain)
        if exit_reason is None and pos["peak_px"]/pos["entry_px"] - 1 >= TRAIL_ACTIVATION:
            if p_today < pos["peak_px"] * (1 - TRAIL_PCT):
                exit_reason = "TRAIL_STOP"

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

    # Determine entry mode for today
    if dt not in state_map_full.index: continue
    mode = state_map_full.loc[dt]["mode"]

    if mode == "PAUSE":  # Bear/Crisis — no entries
        # MTM and continue
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        nav_history.append({"date":dt, "nav":nav, "cash":cash, "equity":mtm, "n_pos":len(positions), "mode":mode})
        continue

    # Scan for BUY signals
    if len(positions) < MAX_POSITIONS:
        max_buys = MAX_BUYS_PER_DAY_RECOVERY if mode == "RECOVERY" else MAX_BUYS_PER_DAY_OTHER
        buys_today = 0
        for tk in px_close.columns:
            if buys_today >= max_buys: break
            if tk in positions: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            if any(b["ticker"] == tk for b in pending_buys): continue

            fa_info = get_fa_at(tk, dt)
            if fa_info is None: continue
            if fa_info["pct_AB"] < 50: continue  # relaxed from 70
            if fa_info["latest_tier"] not in ("A","B"): continue

            adv_vnd = liq_p.at[dt, tk] if tk in liq_p.columns else 0
            p = px_close.at[dt, tk]
            if pd.isna(p) or pd.isna(adv_vnd) or adv_vnd * p < 3e9: continue  # relaxed

            pez = pe_z_p.at[dt, tk] if tk in pe_z_p.columns else np.nan
            pbz = pb_z_p.at[dt, tk] if tk in pb_z_p.columns else np.nan
            ddv = dd_52w_p.at[dt, tk] if tk in dd_52w_p.columns else np.nan
            rsi_now = rsi.at[dt, tk] if tk in rsi.columns else np.nan
            vs50 = vs_ma50.at[dt, tk] if tk in vs_ma50.columns else np.nan
            vs200 = vs_ma200.at[dt, tk] if tk in vs_ma200.columns else np.nan
            volr = vol_rat.at[dt, tk] if tk in vol_rat.columns else np.nan
            macd = macd_p.at[dt, tk] if tk in macd_p.columns else np.nan

            qualified = False
            if mode == "RECOVERY":
                # Aggressive: undervalued + RSI>35, NO above-MA200 requirement
                v_under = (pez < 0) or (pbz < 0) or (ddv < -20)
                if v_under and pd.notna(rsi_now) and rsi_now > 35:
                    qualified = True
            elif mode == "BULL_STRICT":
                # Strict: above MA50 AND MA200, RSI 50-70, vol>1.5x, PE_z<0
                if (pd.notna(vs50) and vs50 > 0 and pd.notna(vs200) and vs200 > 0
                    and pd.notna(rsi_now) and 50 <= rsi_now <= 70
                    and pd.notna(volr) and volr > 1.5
                    and pd.notna(pez) and pez < 0
                    and pd.notna(macd) and macd > 0):
                    qualified = True
            elif mode == "NEUTRAL":
                # Moderate: PE_z<-0.5, above MA200, RSI>45
                if (pd.notna(pez) and pez < -0.5
                    and pd.notna(vs200) and vs200 > 0
                    and pd.notna(rsi_now) and rsi_now > 45):
                    qualified = True

            if qualified:
                pending_buys.append({"ticker":tk, "signal_dt":dt, "mode":mode})
                buys_today += 1

    # MTM
    mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt, "nav":nav, "cash":cash, "equity":mtm, "n_pos":len(positions), "mode":mode})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} trades, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B", flush=True)

# ─── 6. Metrics ──────────────────────────────────────────────────────────
def compute_metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    years = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1]/s.iloc[0]) ** (1/years) - 1
    rets = s.pct_change().dropna()
    sharpe = rets.mean()/rets.std()*np.sqrt(len(rets)/years) if rets.std() > 0 else 0
    dd = (s - s.cummax()) / s.cummax()
    mdd = dd.min()
    return {"CAGR":cagr*100, "Sharpe":sharpe, "MaxDD":mdd*100, "Calmar":cagr/abs(mdd) if mdd<0 else 0}

vni = bq_query("SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2014-01-01' AND t.Close > 100 ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"].reindex(nav_df.index).ffill()

print("\n" + "="*100)
print("  QT v2 — REGIME-TURN AWARE — 12y BACKTEST RESULTS")
print("="*100)
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2018",     pd.Timestamp("2018-01-01"), pd.Timestamp("2018-12-31")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]
print(f"\n  {'Period':<14}{'CAGR':>10}{'Sharpe':>11}{'MaxDD':>9}{'Calmar':>10}{'VNI CAGR':>11}{'alpha':>10}")
for pname, ps, pe in periods:
    m = compute_metrics(nav_df["nav"], ps, pe)
    vm = compute_metrics(vni_px, ps, pe)
    if m is None or vm is None: continue
    alpha = m["CAGR"] - vm["CAGR"]
    print(f"  {pname:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+11.2f}{m['MaxDD']:>+8.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+10.2f}%{alpha:>+9.2f}pp")

# Exit breakdown
if len(trades_df) > 0:
    exits = trades_df[trades_df["side"] != "BUY"]
    print(f"\n  --- Exit breakdown ---")
    if len(exits) > 0:
        for reason, g in exits.groupby("side"):
            print(f"    {reason:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, WR={(g['ret_pct']>0).mean()*100:.1f}%, median_hold={g['hold_days'].median():.0f}d")
    # By entry mode
    print(f"\n  --- Trade performance by entry mode ---")
    for mode, g in exits.groupby("entry_mode"):
        print(f"    {mode:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, WR={(g['ret_pct']>0).mean()*100:.1f}%")

nav_df.to_csv("data/qt_v2_nav.csv")
trades_df.to_csv("data/qt_v2_trades.csv", index=False)
print("\nSaved: qt_v2_nav.csv, qt_v2_trades.csv")
