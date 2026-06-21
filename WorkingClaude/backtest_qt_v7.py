#!/usr/bin/env python3
"""
backtest_qt_v7.py — "Margin of Safety Compounder"
==================================================
Refactor lớn từ v4/v5/v6: bỏ PE_z, PB_z, trend_mult — dùng 1 metric duy nhất MoS.

Triết lý: "Mua khi giá thấp hơn giá trị thật. Càng rẻ càng mua nhiều."

MoS (Margin of Safety):
  expected_growth = mean(NP_R, (NP_P0/NP_P7)^(4/7)-1, Revenue_YoY_P0)
                  ∈ [5%, 35%]
  fair_PE = max(expected_growth*100 + 10, 12)    # Lynch rule of thumb
  MoS = (fair_PE - PE_current) / fair_PE * 100

Position sizing (càng rẻ càng mua):
  MoS ≥ +50%       → 25% NAV (cực rẻ)
  MoS +30 to +50%  → 18% NAV
  MoS +15 to +30%  → 12% NAV
  MoS 0 to +15%    → 8% NAV
  MoS -15 to 0     → 6% NAV (hold)
  MoS -30 to -15%  → 3% NAV (trim)
  MoS < -30%       → 0% (SELL ALL)

Entry: MoS ≥ +15% + quality universe + above MA200
Exit:  MoS < -20% OR FA_DEGRADE OR GROWTH_BROKEN
Rebal: quarterly per release, FULL diff (not half)

Mild market gate:
  BearDvg fires → trim 20% pro-rata (lock chip, not full liquidation)
  Post-BullDvg 60d → sizing × 1.3 (greedy when fearful)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys, pickle
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

# ─── 1. Extended FA ──────────────────────────────────────────────────────
print("[1] Loading FA universe ...", flush=True)
fa_lh = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa_lh = fa_lh[["ticker","quarter","time","Release_Date","tier","score","sub"]]
with open("qt_v5_fa_pre2014.pkl","rb") as f: fa_pre = pickle.load(f)
fa = pd.concat([fa_pre, fa_lh], ignore_index=True).drop_duplicates(subset=["ticker","quarter"], keep="last")
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)

quality_at_q = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("quarter").reset_index(drop=True)
    for i, row in g.iterrows():
        if i < 12: continue
        history = g.iloc[:i+1]
        pct_ab = (history["tier"].isin(["A","B"])).sum() / len(history) * 100
        quality_at_q[(tk, row["quarter"])] = {
            "pct_AB": pct_ab,
            "latest_tier": row["tier"],
            "score": row["score"],
            "sub": row["sub"] if pd.notna(row["sub"]) else "",
        }
print(f"  Quality entries: {len(quality_at_q):,}")

# ─── 2. Panel ────────────────────────────────────────────────────────────
print("\n[2] Loading TA panel ...", flush=True)
with open("qt_panel_2014_2026.pkl","rb") as f: panel = pickle.load(f)
panel["time"] = pd.to_datetime(panel["time"])
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
panel["hi_52w"]     = panel.groupby("ticker")["Close"].transform(lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"] = (panel["Close"]/panel["hi_52w"] - 1) * 100
panel["vs_MA200"]   = (panel["Close"]/panel["MA200"] - 1) * 100
print(f"  Panel: {len(panel):,} rows")

# ─── 3. Financial (with NP_P7 for 2Y CAGR) ───────────────────────────────
fin_cache = "qt_v7_fin.pkl"
if os.path.exists(fin_cache):
    with open(fin_cache,"rb") as f: fin = pickle.load(f)
    print(f"  Loaded financial cache: {len(fin):,} rows")
else:
    print("\n[3] Pulling financial fields (incl NP_P0/NP_P7) ...", flush=True)
    fin = bq_query("""
    SELECT f.ticker, f.quarter, f.time AS q_time, f.Release_Date,
           f.NP_R, f.NP_P0, f.NP_P7, f.Revenue_YoY_P0, f.PE
    FROM tav2_bq.ticker_financial AS f
    WHERE f.time >= '2010-01-01'
    """)
    fin["q_time"] = pd.to_datetime(fin["q_time"])
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    fin["eff_release"] = fin["Release_Date"].fillna(fin["q_time"] + pd.Timedelta(days=60))
    with open(fin_cache,"wb") as f: pickle.dump(fin, f)
    print(f"  Pulled + cached: {len(fin):,} rows")

fin_map = {tk: g.sort_values("eff_release").reset_index(drop=True) for tk, g in fin.groupby("ticker")}

fa_release_map = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("time").reset_index(drop=True)
    g["eff_release"] = g["Release_Date"].fillna(g["time"] + pd.Timedelta(days=60))
    fa_release_map[tk] = g[["eff_release","quarter","tier","score","sub"]].copy()

def get_fa_at(tk, dt):
    if tk not in fa_release_map: return None
    g = fa_release_map[tk]
    av = g[g["eff_release"] <= dt]
    if len(av) == 0: return None
    return quality_at_q.get((tk, av.iloc[-1]["quarter"]))

def compute_mos(fin_row, current_PE):
    """Lynch fair PE: max(growth_pct + 10, 12). MoS = (fair - actual) / fair × 100."""
    if pd.isna(current_PE) or current_PE <= 0 or current_PE > 200: return None

    growths = []
    npr = fin_row["NP_R"]
    if pd.notna(npr): growths.append(npr * 100)

    np0 = fin_row["NP_P0"]; np7 = fin_row["NP_P7"]
    if pd.notna(np0) and pd.notna(np7) and np7 > 0 and np0 > 0:
        # 1.75-year annualized growth
        g2y = (np0/np7) ** (4/7) - 1
        growths.append(g2y * 100)

    rev_yoy = fin_row["Revenue_YoY_P0"]
    if pd.notna(rev_yoy): growths.append(rev_yoy * 100)

    if len(growths) == 0: return None
    expected_growth = np.mean(growths)
    expected_growth = max(5, min(35, expected_growth))

    fair_PE = max(expected_growth + 10, 12)
    mos = (fair_PE - current_PE) / fair_PE * 100
    return {"growth": expected_growth, "fair_PE": fair_PE, "PE": current_PE, "MoS": mos}

def get_mos_at(tk, dt, current_PE):
    if tk not in fin_map: return None
    g = fin_map[tk]
    av = g[g["eff_release"] <= dt]
    if len(av) == 0: return None
    last = av.iloc[-1]
    prev = av.iloc[-2] if len(av) >= 2 else None
    m = compute_mos(last, current_PE)
    if m is None: return None
    m["release_dt"] = last["eff_release"]
    m["prev_NP_R"] = prev["NP_R"] if prev is not None else np.nan
    m["prev_Rev_YoY"] = prev["Revenue_YoY_P0"] if prev is not None else np.nan
    m["NP_R"] = last["NP_R"]
    m["Rev_YoY"] = last["Revenue_YoY_P0"]
    return m

# ─── 4. Pivots ───────────────────────────────────────────────────────────
print("\n[4] Setting up pivots ...", flush=True)
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx

def make_piv(col):
    p = panel.pivot_table(index="time", columns="ticker", values=col, aggfunc="first").sort_index()
    return p.reindex(master_idx).ffill()

px_open  = make_piv("Open")
ma200    = make_piv("MA200")
dd_52w   = make_piv("dd_52w_pct")
vs_ma200 = make_piv("vs_MA200")
pe_d     = make_piv("PE")
liq      = make_piv("Volume_3M_P50")

# ─── 5. VNINDEX + BearDvg/BullDvg signals ────────────────────────────────
vni_cache = "qt_v6_vni.pkl"
with open(vni_cache,"rb") as f: vni_full = pickle.load(f)
vni_full["time"] = pd.to_datetime(vni_full["time"])
v = vni_full.set_index("time")
v["BearDvg_ANY"] = (
    ((v["D_RSI_Max1W"]/v["D_RSI"] > 1.044) & (v["D_RSI_Max3M"] > 0.74) & (v["D_RSI_Max1W"] < 0.72) & (v["D_RSI_Max1W"] > 0.61) & (v["D_RSI_Max1W_Close"]/v["D_RSI_Max3M_Close"] > 1.028) & (v["D_RSI_Max3M_MACD"]/v["D_RSI_Max1W_MACD"] > 1.11) & (v["D_MACDdiff"] < 0) & (v["Close"]/v["D_RSI_Max3M_Close"] > 0.96) & (v["D_RSI_MinT3"] > 0.43) & (v["D_CMF"] < 0.13))
    |
    ((v["D_RSI_Max1W"]/v["D_RSI"] > 1.016) & (v["D_RSI_Max3M"] > 0.77) & (v["D_RSI_Max1W"] < 0.79) & (v["D_RSI_Max1W"] > 0.6) & (v["D_RSI_Max1W_Close"]/v["D_RSI_Max3M_Close"] > 1.008) & (v["D_RSI_Max3M_MACD"]/v["D_RSI_Max1W_MACD"] > 1.1) & (v["D_MACDdiff"] < 0) & (v["Close"]/v["D_RSI_Max3M_Close"] > 0.97) & (v["D_RSI_MinT3"] > 0.5) & (v["D_CMF"] < 0.15))
)
v["BullDvg_ANY"] = (
    ((v["D_RSI_Min1W"]/v["D_RSI_Min3M"] > 0.9) & (v["D_RSI_Min1W"] < 0.6) & (v["D_RSI_Min3M"] < 0.4) & (v["D_RSI_Min1W_Close"]/v["D_RSI_Min3M_Close"] < 1.15) & (v["D_MACDdiff"] > 0) & (v["D_RSI_MinT3"] < 0.5) & (v["D_RSI_Max1W"] < 0.48) & (v["D_RSI"]/v["D_RSI_T1W"] > 1.12) & (v["D_CMF"] > 0) & (v["C_L1M"] < 1.21) & (v["C_L1W"] < 1.05))
    |
    ((v["D_RSI_Min1W"]/v["D_RSI_Min3M"] > 0.92) & (v["D_RSI_Min1W"] < 0.52) & (v["D_RSI_Min3M"] < 0.38) & (v["D_RSI_Min1W_Close"]/v["D_RSI_Min3M_Close"] < 1.1) & (v["D_MACDdiff"] > 0) & (v["D_RSI_MinT3"] < 0.56) & (v["D_RSI_Max1W"] < 0.64) & (v["D_RSI"]/v["D_RSI_T1W"] > 1.1) & (v["D_CMF"] > 0) & (v["C_L1M"] < 1.2) & (v["C_L1W"] < 1.025))
)
v_aligned = v.reindex(master_idx).ffill()
beardvg = v_aligned["BearDvg_ANY"].fillna(False).astype(bool)
bulldvg = v_aligned["BullDvg_ANY"].fillna(False).astype(bool)
vni_close = v_aligned["Close"]
print(f"  BearDvg events: {beardvg.sum()} | BullDvg events: {bulldvg.sum()}")

# ─── 6. Sizing table (MoS-driven) ────────────────────────────────────────
def mos_to_target_pct(mos):
    if mos is None: return 0
    if mos >= 50:  return 0.25
    if mos >= 30:  return 0.18
    if mos >= 15:  return 0.12
    if mos >= 0:   return 0.08
    if mos > -15:  return 0.06
    if mos > -30:  return 0.03
    return 0.0

# ─── 7. Backtest ─────────────────────────────────────────────────────────
print("\n[7] Running QT v7 (MoS) backtest ...", flush=True)
MAX_POSITIONS = 8
LIQ_CAP_PCT, MAX_FILL_DAYS = 0.20, 5
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE = 0.01
BL_DAYS_FA = 90
GROWTH_BAD_THR = -0.15
BEAR_TRIM_FRAC = 0.20
POST_BEAR_WINDOW = 60
POST_BEAR_BOOST  = 1.3

start_dt, end_dt = pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")
sim_days = [d for d in master_idx if start_dt <= d <= end_dt]

cash = INIT_NAV
positions = {}  # tk → {entry_dt, entry_px, shares, total_cost, last_release_dt, last_mos}
blacklist = {}
nav_history, trades, regime_log = [], [], []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

pending_buys, pending_sells = [], []
last_bear_dt = None
post_bear_until = None

print(f"  Sim window: {start_dt.date()} → {end_dt.date()} ({len(sim_days)} days)")

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={nav/1e9:.2f}B pos={len(positions)} cash={cash/1e9:.1f}B", flush=True)
    cash *= (1 + daily_rate)

    is_bear = bool(beardvg.at[dt])
    is_bull = bool(bulldvg.at[dt])

    # BearDvg → mild trim 20%
    if is_bear:
        last_bear_dt = dt
        post_bear_until = None
        for tk, pos in list(positions.items()):
            trim_sh = pos["shares"] * BEAR_TRIM_FRAC
            pending_sells.append({"ticker":tk,"shares":trim_sh,"reason":"BEAR_TRIM"})
        regime_log.append({"dt":dt,"event":"BEAR_TRIM_20","n_pos":len(positions)})

    if is_bull and last_bear_dt is not None:
        post_bear_until = dt + pd.Timedelta(days=POST_BEAR_WINDOW)
        regime_log.append({"dt":dt,"event":"BULL_POST_BEAR","until":post_bear_until})
        blacklist = {tk: bldt for tk, bldt in blacklist.items() if bldt > dt + pd.Timedelta(days=30)}

    boost_active = (post_bear_until is not None and dt <= post_bear_until)
    sizing_boost = POST_BEAR_BOOST if boost_active else 1.0

    # T+1 Sells
    nps = []
    for s in pending_sells:
        tk = s["ticker"]
        if tk not in positions: continue
        if tk not in px_open.columns: continue
        fpx = px_open.at[dt, tk]
        if pd.isna(fpx) or fpx <= 0: nps.append(s); continue
        pos = positions[tk]
        sell_sh = min(s["shares"], pos["shares"])
        if sell_sh < 1e-6: continue
        gross = sell_sh * fpx * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        avg_entry = pos["total_cost"]/pos["shares"] if pos["shares"]>0 else pos["entry_px"]
        trades.append({"dt":dt,"ticker":tk,"side":s["reason"],"shares":sell_sh,
                       "px":fpx,"net":net,"entry_dt":pos["entry_dt"],"entry_px":avg_entry,
                       "ret_pct":(fpx/avg_entry-1)*100,"hold_days":(dt-pos["entry_dt"]).days})
        if pos["shares"] - sell_sh < 1e-6 or s["reason"] in ("FA_DEGRADE","MOS_OVERPRICED","GROWTH_BROKEN"):
            bl = 15 if s["reason"]=="BEAR_TRIM" else BL_DAYS_FA
            blacklist[tk] = dt + pd.Timedelta(days=bl)
            if tk in positions: del positions[tk]
        else:
            pos["total_cost"] = pos["total_cost"] * (pos["shares"] - sell_sh) / pos["shares"]
            pos["shares"] -= sell_sh
    pending_sells = nps

    # T+1 Buys
    for b in pending_buys:
        tk = b["ticker"]; btype = b["type"]; alloc = b["alloc_vnd"]
        if tk not in px_open.columns: continue
        fpx = px_open.at[dt, tk]
        if pd.isna(fpx) or fpx <= 0: continue
        if alloc < 1e6 or alloc > cash: continue
        if btype == "NEW":
            if tk in positions: continue
            if len(positions) >= MAX_POSITIONS: continue
            if tk in blacklist and blacklist[tk] > dt: continue

        adv = liq.at[dt, tk] if tk in liq.columns else 0
        if pd.isna(adv) or adv <= 0: adv = 1e6
        cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
        alloc = min(alloc, cap)
        if alloc < 1e6: continue

        eff_px = fpx * (1 + SLIP_IN)
        shares = alloc / eff_px
        cost = shares * eff_px
        if cost > cash: continue
        cash -= cost

        if btype == "NEW":
            positions[tk] = {"entry_dt":dt, "entry_px":fpx, "shares":shares, "total_cost":cost,
                              "last_release_dt": dt, "last_mos": b.get("mos", None)}
            trades.append({"dt":dt,"ticker":tk,"side":"BUY","shares":shares,"px":fpx,
                            "net":-cost,"entry_dt":dt,"entry_px":fpx,"ret_pct":0,
                            "hold_days":0,"mos":b.get("mos", None)})
        else:
            pos = positions[tk]
            pos["shares"] += shares
            pos["total_cost"] += cost
            trades.append({"dt":dt,"ticker":tk,"side":"REBAL_ADD","shares":shares,"px":fpx,
                            "net":-cost,"entry_dt":pos["entry_dt"],
                            "entry_px":pos["total_cost"]/pos["shares"],
                            "ret_pct":(fpx/(pos["total_cost"]/pos["shares"])-1)*100,
                            "hold_days":(dt-pos["entry_dt"]).days,"mos":b.get("mos", None)})
    pending_buys = []

    # Per-position: check exits + rebal
    mtm_now = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_now = cash + mtm_now

    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue

        fa_info = get_fa_at(tk, dt)

        exit_reason = None
        if fa_info is not None and fa_info["latest_tier"] in ("C","D","E"):
            exit_reason = "FA_DEGRADE"

        # Compute MoS at current PE
        cur_pe = pe_d.at[dt, tk] if tk in pe_d.columns else np.nan
        mos_info = get_mos_at(tk, dt, cur_pe)

        if exit_reason is None and mos_info is not None:
            # Growth broken: 2 quý liên tiếp âm sâu
            if (pd.notna(mos_info["NP_R"]) and pd.notna(mos_info["Rev_YoY"])
                and pd.notna(mos_info["prev_NP_R"]) and pd.notna(mos_info["prev_Rev_YoY"])
                and mos_info["NP_R"] < GROWTH_BAD_THR and mos_info["Rev_YoY"] < GROWTH_BAD_THR
                and mos_info["prev_NP_R"] < GROWTH_BAD_THR and mos_info["prev_Rev_YoY"] < GROWTH_BAD_THR):
                exit_reason = "GROWTH_BROKEN"
            # MoS overpriced
            elif mos_info["MoS"] < -30:
                exit_reason = "MOS_OVERPRICED"

        if exit_reason:
            pending_sells.append({"ticker":tk,"shares":pos["shares"],"reason":exit_reason})
            continue

        # Quarterly rebalance trigger
        if mos_info is None: continue
        rel_dt = mos_info["release_dt"]
        if rel_dt <= pos["last_release_dt"]: continue
        pos["last_release_dt"] = rel_dt
        pos["last_mos"] = mos_info["MoS"]

        target_pct = mos_to_target_pct(mos_info["MoS"]) * sizing_boost
        target_pct = min(target_pct, 0.25)  # cap

        cur_value = pos["shares"] * p_today
        cur_pct = cur_value / nav_now
        diff_pct = target_pct - cur_pct

        if abs(diff_pct) < 0.02: continue

        if diff_pct > 0:
            alloc = diff_pct * nav_now
            if alloc < 1e6: continue
            pending_buys.append({"ticker":tk,"type":"REBAL_ADD","alloc_vnd":alloc,
                                  "signal_dt":dt,"mos":mos_info["MoS"]})
        else:
            sell_pct = abs(diff_pct)
            sell_sh = (sell_pct * nav_now) / p_today
            sell_sh = min(sell_sh, pos["shares"])
            if sell_sh * p_today < 1e6: continue
            pending_sells.append({"ticker":tk,"shares":sell_sh,"reason":"REBAL_TRIM"})

    # Scan for NEW entries
    open_slots = MAX_POSITIONS - len(positions) - sum(1 for b in pending_buys if b["type"]=="NEW")
    if open_slots > 0:
        candidates = []
        for tk in px_close.columns:
            if tk in positions: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            if any(b["ticker"]==tk for b in pending_buys): continue

            fa_info = get_fa_at(tk, dt)
            if fa_info is None: continue
            if fa_info["pct_AB"] < 70: continue
            if fa_info["latest_tier"] not in ("A","B"): continue

            adv_vnd = liq.at[dt, tk] if tk in liq.columns else 0
            p = px_close.at[dt, tk]
            if pd.isna(p) or pd.isna(adv_vnd) or adv_vnd*p < 5e9: continue

            vs200 = vs_ma200.at[dt,tk] if tk in vs_ma200.columns else np.nan
            ddv = dd_52w.at[dt,tk] if tk in dd_52w.columns else np.nan
            # Don't catch deep falling knife
            if not ((pd.notna(vs200) and vs200 > 0) or (pd.notna(ddv) and ddv > -15)):
                continue

            cur_pe = pe_d.at[dt, tk] if tk in pe_d.columns else np.nan
            mos_info = get_mos_at(tk, dt, cur_pe)
            if mos_info is None: continue
            if mos_info["MoS"] < 15: continue  # need ≥15% margin

            score = mos_info["MoS"]  # rank by cheapness
            if boost_active: score += 20
            candidates.append((tk, score, mos_info["MoS"]))

        candidates.sort(key=lambda x: x[1], reverse=True)
        for tk, sc, mos in candidates[:open_slots]:
            init_pct = mos_to_target_pct(mos) * sizing_boost
            init_pct = min(init_pct, 0.25)
            alloc = init_pct * nav_now
            pending_buys.append({"ticker":tk,"type":"NEW","alloc_vnd":alloc,
                                  "signal_dt":dt,"mos":mos})

    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt,"nav":nav,"cash":cash,"equity":mtm,"n_pos":len(positions)})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
regime_df = pd.DataFrame(regime_log) if regime_log else pd.DataFrame(columns=["dt","event"])
print(f"\n  Sim complete: {len(trades_df)} events, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B")
print(f"  BearDvg trim events: {(regime_df['event']=='BEAR_TRIM_20').sum() if len(regime_df) else 0}")
print(f"  Post-bear boost episodes: {(regime_df['event']=='BULL_POST_BEAR').sum() if len(regime_df) else 0}")

# ─── 8. Metrics ──────────────────────────────────────────────────────────
def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)]
    if len(s) < 30: return None
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
    rets = s.pct_change().dropna()
    spy = len(rets)/yrs
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (s - s.cummax())/s.cummax()
    mdd = dd.min()
    calmar = cagr/abs(mdd) if mdd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"MaxDD":mdd*100,"Calmar":calmar}

vni_aligned_idx = vni_close.reindex(nav_df.index).ffill()
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]
print("\n" + "="*100)
print(f"  {'Period':<14}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'VNI':>10}{'alpha':>10}")
for nm, ps, pe in periods:
    m = metrics(nav_df["nav"], ps, pe); vm = metrics(vni_aligned_idx, ps, pe)
    if m is None or vm is None: continue
    a = m["CAGR"] - vm["CAGR"]
    print(f"  {nm:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+10.2f}{m['MaxDD']:>+9.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+9.2f}%{a:>+9.2f}pp")

if len(trades_df) > 0:
    full_exits = trades_df[trades_df["side"].isin(["FA_DEGRADE","MOS_OVERPRICED","GROWTH_BROKEN"])]
    print(f"\n  --- Trade summary ---")
    print(f"  Total events: {len(trades_df)}")
    sides = trades_df["side"].value_counts().to_dict()
    for k, v in sides.items():
        print(f"    {k:<14}: {v}")
    if len(full_exits) > 0:
        for rs, g in full_exits.groupby("side"):
            print(f"    {rs:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, hold={g['hold_days'].median():.0f}d, WR={(g['ret_pct']>0).mean()*100:.1f}%")
        per_tk = full_exits.groupby("ticker").agg(n=("ticker","size"),avg_ret=("ret_pct","mean"),
                                                    total_ret=("ret_pct","sum"),avg_hold=("hold_days","mean"))
        per_tk = per_tk.sort_values("total_ret", ascending=False)
        print(f"\n  Top 15 by cum return (full exits):")
        for tk, r in per_tk.head(15).iterrows():
            print(f"    {tk:<7} N={int(r['n']):2d}  avg={r['avg_ret']:+6.1f}%  cum={r['total_ret']:+7.1f}%  hold={r['avg_hold']:.0f}d")

nav_df.to_csv("qt_v7_nav.csv")
trades_df.to_csv("qt_v7_trades.csv", index=False)
regime_df.to_csv("qt_v7_regime.csv", index=False)
print("\nSaved: qt_v7_nav.csv, qt_v7_trades.csv, qt_v7_regime.csv")
