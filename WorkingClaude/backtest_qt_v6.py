#!/usr/bin/env python3
"""
backtest_qt_v6.py — "Dynamic Conviction + BearDvg/BullDvg Gate"
================================================================
Cải tiến v5 (4 fix tune) + thay 5-state bằng BearDvg/BullDvg signals:

A. v5 tuning (giải quyết "trim quá tay" → mất Q1_2026):
   1. valuation_mult floor 0.7x (thay 0.4x ở PE_z>2)
   2. Cash redeploy: cash > 25% NAV → force add 5% NAV vào cheapest A-tier holding
   3. Trim chỉ khi PE_z > +1.5 AND growth_mult < 1.0 (không chỉ định giá)
   4. Half-rebalance: trade 50% của (target - current) thay full

B. Market gate (thay 5-state):
   - BearDvgVNI1/2: RSI bear divergence (peak weakening)
   - BullDvgVNI1/12: RSI bull divergence (trough strengthening)

   Khi BearDvg fires:
     * macro_negative (VNI 3M < -8% AND VNI < MA200) → SELL ALL
     * normal                                         → TRIM 40% proportional
   Khi BullDvg fires SAU một BearDvg (post-crisis):
     * 60d window: target sizing × 1.5 (greedy when fearful)
     * + có thể thoát blacklist cho A-tier muốn re-enter

Entry/Exit rules giữ v4/v5 (VALUE OR GARP; FA_DEGRADE/OVERVALUED/GROWTH_BROKEN)
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

# ─── 1. Extended FA (pre-2014 + lh) ──────────────────────────────────────
print("[1] Loading FA universe ...", flush=True)
fa_lh = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa_lh = fa_lh[["ticker","quarter","time","Release_Date","tier","score","sub"]]
with open("data/qt_v5_fa_pre2014.pkl","rb") as f: fa_pre = pickle.load(f)
fa = pd.concat([fa_pre, fa_lh], ignore_index=True).drop_duplicates(subset=["ticker","quarter"], keep="last")
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
print(f"  Combined FA: {len(fa):,} rows, {fa['ticker'].nunique()} tickers")

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

# ─── 2. Panel load ───────────────────────────────────────────────────────
print("\n[2] Loading TA panel ...", flush=True)
with open("data/qt_panel_2014_2026.pkl","rb") as f: panel = pickle.load(f)
panel["time"] = pd.to_datetime(panel["time"])
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
panel["hi_52w"]    = panel.groupby("ticker")["Close"].transform(lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"]= (panel["Close"]/panel["hi_52w"] - 1) * 100
panel["pe_z"]      = ((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["pb_z"]      = ((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["vs_MA200"]  = (panel["Close"]/panel["MA200"] - 1) * 100
panel["ret_6m"]    = panel.groupby("ticker")["Close"].pct_change(126) * 100
print(f"  Panel: {len(panel):,} rows")

# ─── 3. Financial cache ──────────────────────────────────────────────────
with open("data/qt_v4_fin.pkl","rb") as f: fin = pickle.load(f)
fin["q_time"] = pd.to_datetime(fin["q_time"])
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["eff_release"] = fin["Release_Date"].fillna(fin["q_time"] + pd.Timedelta(days=60))
fin_map = {tk: g.sort_values("eff_release").reset_index(drop=True) for tk, g in fin.groupby("ticker")}
print(f"  Loaded financial cache: {len(fin):,} rows")

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
    last = av.iloc[-1]
    return quality_at_q.get((tk, last["quarter"]))

def get_fin_at(tk, dt):
    if tk not in fin_map: return None
    g = fin_map[tk]
    av = g[g["eff_release"] <= dt]
    if len(av) == 0: return None
    last = av.iloc[-1]
    prev = av.iloc[-2] if len(av) >= 2 else None
    return {
        "PEG": last["PEG"], "NP_R": last["NP_R"], "Rev_YoY": last["Revenue_YoY_P0"],
        "PE": last["PE"],
        "prev_NP_R": prev["NP_R"] if prev is not None else np.nan,
        "prev_Rev_YoY": prev["Revenue_YoY_P0"] if prev is not None else np.nan,
        "release_dt": last["eff_release"],
    }

# ─── 4. Pull VNINDEX with RSI/MACD columns for BearDvg/BullDvg ───────────
vni_cache = "data/qt_v6_vni.pkl"
if os.path.exists(vni_cache):
    with open(vni_cache,"rb") as f: vni_full = pickle.load(f)
    print(f"  Loaded VNI cache: {len(vni_full):,} rows")
else:
    print("\n[4] Pulling VNINDEX with divergence inputs ...", flush=True)
    vni_full = bq_query("""
    SELECT t.time, t.Close, t.MA200,
      t.D_RSI, t.D_RSI_T1W, t.D_RSI_Max1W, t.D_RSI_Max3M,
      t.D_RSI_Min1W, t.D_RSI_Min3M, t.D_RSI_MinT3,
      t.D_RSI_Max1W_Close, t.D_RSI_Min1W_Close,
      t.D_RSI_Max3M_Close, t.D_RSI_Min3M_Close,
      t.D_RSI_Max1W_MACD, t.D_RSI_Max3M_MACD,
      t.D_MACDdiff, t.D_CMF, t.C_L1M, t.C_L1W,
      t.Volume, t.Volume_1M
    FROM tav2_bq.ticker AS t
    WHERE t.ticker='VNINDEX' AND t.time >= '2010-01-01' AND t.Close > 100
    ORDER BY t.time
    """)
    vni_full["time"] = pd.to_datetime(vni_full["time"])
    with open(vni_cache,"wb") as f: pickle.dump(vni_full, f)
    print(f"  Pulled + cached: {len(vni_full):,} rows")

# Compute BearDvg/BullDvg booleans
v = vni_full.set_index("time")
v["BearDvgVNI1"] = (
    (v["D_RSI_Max1W"]/v["D_RSI"] > 1.044) & (v["D_RSI_Max3M"] > 0.74) &
    (v["D_RSI_Max1W"] < 0.72) & (v["D_RSI_Max1W"] > 0.61) &
    (v["D_RSI_Max1W_Close"]/v["D_RSI_Max3M_Close"] > 1.028) &
    (v["D_RSI_Max3M_MACD"]/v["D_RSI_Max1W_MACD"] > 1.11) &
    (v["D_MACDdiff"] < 0) & (v["Close"]/v["D_RSI_Max3M_Close"] > 0.96) &
    (v["D_RSI_MinT3"] > 0.43) & (v["D_CMF"] < 0.13)
)
v["BearDvgVNI2"] = (
    (v["D_RSI_Max1W"]/v["D_RSI"] > 1.016) & (v["D_RSI_Max3M"] > 0.77) &
    (v["D_RSI_Max1W"] < 0.79) & (v["D_RSI_Max1W"] > 0.6) &
    (v["D_RSI_Max1W_Close"]/v["D_RSI_Max3M_Close"] > 1.008) &
    (v["D_RSI_Max3M_MACD"]/v["D_RSI_Max1W_MACD"] > 1.1) &
    (v["D_MACDdiff"] < 0) & (v["Close"]/v["D_RSI_Max3M_Close"] > 0.97) &
    (v["D_RSI_MinT3"] > 0.5) & (v["D_CMF"] < 0.15)
)
v["BullDvgVNI1"] = (
    (v["D_RSI_Min1W"]/v["D_RSI_Min3M"] > 0.9) & (v["D_RSI_Min1W"] < 0.6) &
    (v["D_RSI_Min3M"] < 0.4) & (v["D_RSI_Min1W_Close"]/v["D_RSI_Min3M_Close"] < 1.15) &
    (v["D_MACDdiff"] > 0) & (v["D_RSI_MinT3"] < 0.5) &
    (v["D_RSI_Max1W"] < 0.48) & (v["D_RSI"]/v["D_RSI_T1W"] > 1.12) &
    (v["D_CMF"] > 0) & (v["C_L1M"] < 1.21) & (v["C_L1W"] < 1.05)
)
v["BullDvgVNI12"] = (
    (v["D_RSI_Min1W"]/v["D_RSI_Min3M"] > 0.92) & (v["D_RSI_Min1W"] < 0.52) &
    (v["D_RSI_Min3M"] < 0.38) & (v["D_RSI_Min1W_Close"]/v["D_RSI_Min3M_Close"] < 1.1) &
    (v["D_MACDdiff"] > 0) & (v["D_RSI_MinT3"] < 0.56) &
    (v["D_RSI_Max1W"] < 0.64) & (v["D_RSI"]/v["D_RSI_T1W"] > 1.1) &
    (v["D_CMF"] > 0) & (v["C_L1M"] < 1.2) & (v["C_L1W"] < 1.025)
)
v["BearDvg_ANY"] = v["BearDvgVNI1"] | v["BearDvgVNI2"]
v["BullDvg_ANY"] = v["BullDvgVNI1"] | v["BullDvgVNI12"]

# Macro negative: VNI 3M < -8% AND below MA200
v["vni_3m_ret"] = v["Close"].pct_change(63) * 100
v["below_ma200"] = v["Close"] < v["MA200"]
v["macro_negative"] = (v["vni_3m_ret"] < -8) & (v["below_ma200"])

print(f"  BearDvg events: {v['BearDvg_ANY'].sum()} | BullDvg events: {v['BullDvg_ANY'].sum()}")
print(f"  Macro-negative days: {v['macro_negative'].sum()} | of which BearDvg co-fires: {(v['BearDvg_ANY'] & v['macro_negative']).sum()}")

# ─── 5. Pivots + reindex ─────────────────────────────────────────────────
print("\n[5] Setting up pivots ...", flush=True)
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx

def make_piv(col):
    p = panel.pivot_table(index="time", columns="ticker", values=col, aggfunc="first").sort_index()
    return p.reindex(master_idx).ffill()

px_open  = make_piv("Open")
ma200    = make_piv("MA200")
pe_z     = make_piv("pe_z")
pb_z     = make_piv("pb_z")
dd_52w   = make_piv("dd_52w_pct")
vs_ma200 = make_piv("vs_MA200")
pe_d     = make_piv("PE")
liq      = make_piv("Volume_3M_P50")
ret6m    = make_piv("ret_6m")

# VNI signals aligned to master_idx
v_aligned = v.reindex(master_idx).ffill()
beardvg_any = v_aligned["BearDvg_ANY"].fillna(False).astype(bool)
bulldvg_any = v_aligned["BullDvg_ANY"].fillna(False).astype(bool)
macro_neg   = v_aligned["macro_negative"].fillna(False).astype(bool)
vni_close   = v_aligned["Close"]
vni_ret6m   = vni_close.pct_change(126) * 100

# ─── 6. Sizing rules (v6 tuned) ──────────────────────────────────────────
def trend_mult(stk6m, vni6m):
    if pd.isna(stk6m) or pd.isna(vni6m): return 1.0
    ex = stk6m - vni6m
    if ex > 20: return 1.5
    if ex > 10: return 1.2
    if ex < -20: return 0.5
    if ex < -10: return 0.7
    return 1.0

def valuation_mult_v6(pez):
    # v6 tune: floor at 0.7x (was 0.4x)
    if pd.isna(pez): return 1.0
    if pez < -1.5: return 1.3
    if pez < 0:    return 1.1
    if pez < 1:    return 1.0
    if pez < 2:    return 0.85
    return 0.7

def growth_mult(npr, rev):
    if pd.isna(npr) or pd.isna(rev): return 1.0
    if npr >= 0.20 and rev >= 0.20: return 1.2
    if npr >= 0.10 or rev >= 0.10:  return 1.0
    if npr >= 0 and rev >= 0:       return 0.9
    if npr < -0.10 and rev < -0.10: return 0.5
    return 0.8

BASE_PCT   = 0.10
MIN_PCT    = 0.03
MAX_PCT    = 0.25
REBAL_THR  = 0.02
REBAL_FRAC = 0.5         # half-rebalance
CASH_REDEPLOY_THR = 0.25  # cash >25% NAV → top up
POST_BEAR_WINDOW  = 60   # days
POST_BEAR_BOOST   = 1.5

# ─── 7. Backtest ─────────────────────────────────────────────────────────
print("\n[7] Running QT v6 backtest ...", flush=True)
MAX_POSITIONS = 8
LIQ_CAP_PCT, MAX_FILL_DAYS = 0.20, 5
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE = 0.01
BL_DAYS_FA, BL_DAYS_OVR = 90, 30
PE_Z_OVR, PB_Z_OVR = 2.5, 1.5
GROWTH_BAD_THR = -0.15
BEAR_TRIM_FRAC = 0.40    # trim 40% when BearDvg fires normal

start_dt, end_dt = pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")
sim_days = [d for d in master_idx if start_dt <= d <= end_dt]

cash = INIT_NAV
positions = {}
blacklist = {}
nav_history, trades, regime_log = [], [], []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

pending_buys, pending_sells = [], []
last_bear_dt = None
post_bear_until = None  # set when BullDvg fires AFTER a BearDvg

print(f"  Sim window: {start_dt.date()} → {end_dt.date()} ({len(sim_days)} days)")

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        boost = "BOOST" if (post_bear_until is not None and dt <= post_bear_until) else "norm"
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={nav/1e9:.2f}B pos={len(positions)} cash={cash/1e9:.1f}B mode={boost}", flush=True)
    cash *= (1 + daily_rate)

    is_bear = bool(beardvg_any.at[dt])
    is_bull = bool(bulldvg_any.at[dt])
    is_macro_neg = bool(macro_neg.at[dt])

    # ── BearDvg trigger ──
    if is_bear:
        last_bear_dt = dt
        post_bear_until = None  # reset (will be set on next BullDvg)
        if is_macro_neg:
            # SELL ALL (full liquidation)
            for tk, pos in list(positions.items()):
                pending_sells.append({"ticker":tk,"shares":pos["shares"],"reason":"BEAR_FULL"})
            regime_log.append({"dt":dt,"event":"BEAR_FULL_LIQ","n_pos":len(positions)})
        else:
            # TRIM 40% pro rata
            for tk, pos in list(positions.items()):
                trim_sh = pos["shares"] * BEAR_TRIM_FRAC
                pending_sells.append({"ticker":tk,"shares":trim_sh,"reason":"BEAR_TRIM"})
            regime_log.append({"dt":dt,"event":"BEAR_TRIM_40","n_pos":len(positions)})

    # ── BullDvg post-crisis trigger ──
    if is_bull and last_bear_dt is not None:
        # only if BullDvg comes AFTER bear
        post_bear_until = dt + pd.Timedelta(days=POST_BEAR_WINDOW)
        regime_log.append({"dt":dt,"event":"BULL_POST_BEAR","until":post_bear_until})
        # also clear blacklist for opportunistic re-entry
        blacklist = {tk: bldt for tk, bldt in blacklist.items() if bldt > dt + pd.Timedelta(days=30)}

    boost_active = (post_bear_until is not None and dt <= post_bear_until)
    sizing_boost = POST_BEAR_BOOST if boost_active else 1.0

    # ── T+1 Sells ──
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
        # update or remove
        if pos["shares"] - sell_sh < 1e-6 or s["reason"] in ("FA_DEGRADE","OVERVALUED","GROWTH_BROKEN","BEAR_FULL"):
            bl = BL_DAYS_OVR if s["reason"]=="OVERVALUED" else BL_DAYS_FA
            if s["reason"] in ("BEAR_TRIM","BEAR_FULL"):
                bl = 15  # short bl after BearDvg → ready to re-buy in post-bear boost
            blacklist[tk] = dt + pd.Timedelta(days=bl)
            if tk in positions: del positions[tk]
        else:
            pos["total_cost"] = pos["total_cost"] * (pos["shares"] - sell_sh) / pos["shares"]
            pos["shares"] -= sell_sh
    pending_sells = nps

    # ── T+1 Buys ──
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
                              "last_release_dt": dt}
            trades.append({"dt":dt,"ticker":tk,"side":"BUY","shares":shares,"px":fpx,
                            "net":-cost,"entry_dt":dt,"entry_px":fpx,"ret_pct":0,"hold_days":0})
        else:
            pos = positions[tk]
            pos["shares"] += shares
            pos["total_cost"] += cost
            trades.append({"dt":dt,"ticker":tk,"side":b.get("subtype","REBAL_ADD"),
                            "shares":shares,"px":fpx,"net":-cost,
                            "entry_dt":pos["entry_dt"],"entry_px":pos["total_cost"]/pos["shares"],
                            "ret_pct":(fpx/(pos["total_cost"]/pos["shares"])-1)*100,
                            "hold_days":(dt-pos["entry_dt"]).days})
    pending_buys = []

    # ── Per-position: check exits + quarterly rebalance ──
    mtm_now = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_now = cash + mtm_now
    vni6m = vni_ret6m.get(dt, np.nan)

    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue

        fa_info = get_fa_at(tk, dt)
        fin_info = get_fin_at(tk, dt)

        # Exits
        exit_reason = None
        if fa_info is not None and fa_info["latest_tier"] in ("C","D","E"):
            exit_reason = "FA_DEGRADE"
        if exit_reason is None:
            pez = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
            pbz = pb_z.at[dt,tk] if tk in pb_z.columns else np.nan
            if pd.notna(pez) and pd.notna(pbz) and pez > PE_Z_OVR and pbz > PB_Z_OVR:
                exit_reason = "OVERVALUED"
        if exit_reason is None and fin_info is not None:
            if (pd.notna(fin_info["NP_R"]) and pd.notna(fin_info["Rev_YoY"])
                and pd.notna(fin_info["prev_NP_R"]) and pd.notna(fin_info["prev_Rev_YoY"])
                and fin_info["NP_R"] < GROWTH_BAD_THR and fin_info["Rev_YoY"] < GROWTH_BAD_THR
                and fin_info["prev_NP_R"] < GROWTH_BAD_THR and fin_info["prev_Rev_YoY"] < GROWTH_BAD_THR):
                exit_reason = "GROWTH_BROKEN"
        if exit_reason:
            pending_sells.append({"ticker":tk,"shares":pos["shares"],"reason":exit_reason})
            continue

        # Quarterly rebalance trigger
        if fin_info is None: continue
        rel_dt = fin_info["release_dt"]
        if rel_dt <= pos["last_release_dt"]: continue
        pos["last_release_dt"] = rel_dt

        stk6m = ret6m.at[dt,tk] if tk in ret6m.columns else np.nan
        pez_now = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
        tm = trend_mult(stk6m, vni6m)
        vm = valuation_mult_v6(pez_now)
        gm = growth_mult(fin_info["NP_R"], fin_info["Rev_YoY"])
        target_pct = BASE_PCT * tm * vm * gm * sizing_boost
        target_pct = max(MIN_PCT, min(MAX_PCT, target_pct))

        cur_value = pos["shares"] * p_today
        cur_pct = cur_value / nav_now
        diff_pct = target_pct - cur_pct

        if abs(diff_pct) < REBAL_THR: continue

        # v6 tune #4: half-rebalance
        diff_pct *= REBAL_FRAC

        # v6 tune #3: trim only if PE_z > +1.5 AND growth_mult < 1.0
        if diff_pct < 0:
            if not (pd.notna(pez_now) and pez_now > 1.5 and gm < 1.0):
                continue  # skip trim if not BOTH overvalued and weak growth

        if diff_pct > 0:
            alloc = diff_pct * nav_now
            if alloc < 1e6: continue
            pending_buys.append({"ticker":tk, "type":"REBAL_ADD",
                                  "alloc_vnd":alloc, "subtype":"REBAL_ADD","signal_dt":dt})
        else:
            sell_pct = abs(diff_pct)
            sell_sh = (sell_pct * nav_now) / p_today
            sell_sh = min(sell_sh, pos["shares"])
            if sell_sh * p_today < 1e6: continue
            pending_sells.append({"ticker":tk,"shares":sell_sh,"reason":"REBAL_TRIM"})

    # ── v6 tune #2: Cash redeploy ──
    cash_pct = cash / nav_now if nav_now > 0 else 0
    if cash_pct > CASH_REDEPLOY_THR and len(positions) > 0:
        # find cheapest A-tier position by PE_z
        candidates_pez = []
        for tk, pos in positions.items():
            fa_info = get_fa_at(tk, dt)
            if fa_info is None or fa_info["latest_tier"] not in ("A","B"): continue
            pez = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
            if pd.isna(pez): continue
            cur_pct = (pos["shares"] * px_close.at[dt, tk]) / nav_now
            if cur_pct >= MAX_PCT: continue
            candidates_pez.append((tk, pez, cur_pct))
        if candidates_pez:
            candidates_pez.sort(key=lambda x: x[1])  # cheapest first
            tk, pez, cur_pct = candidates_pez[0]
            redeploy_alloc = min(0.05 * nav_now, (MAX_PCT - cur_pct) * nav_now)
            if redeploy_alloc >= 1e6:
                pending_buys.append({"ticker":tk,"type":"REBAL_ADD",
                                      "alloc_vnd":redeploy_alloc,"subtype":"CASH_DEPLOY",
                                      "signal_dt":dt})

    # ── Scan for NEW entries ──
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

            pez = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
            pbz = pb_z.at[dt,tk] if tk in pb_z.columns else np.nan
            ddv = dd_52w.at[dt,tk] if tk in dd_52w.columns else np.nan
            vs200 = vs_ma200.at[dt,tk] if tk in vs_ma200.columns else np.nan
            pe_now = pe_d.at[dt,tk] if tk in pe_d.columns else np.nan

            v_under = ((pd.notna(pez) and pez < -1.0)
                       or (pd.notna(pbz) and pbz < -1.0)
                       or (pd.notna(ddv) and ddv < -30))
            v_not_falling = (pd.notna(vs200) and vs200 > 0) or (pd.notna(ddv) and ddv > -20)
            value_pass = v_under and v_not_falling

            fin_info = get_fin_at(tk, dt)
            garp_pass = False
            if fin_info is not None:
                peg = fin_info["PEG"]; npyoy = fin_info["NP_R"]; revyoy = fin_info["Rev_YoY"]
                if (pd.notna(peg) and 0 < peg <= 1.0
                    and pd.notna(npyoy) and npyoy >= 0.20
                    and pd.notna(revyoy) and revyoy >= 0.20
                    and pd.notna(pe_now) and pe_now < 25
                    and pd.notna(vs200) and vs200 > 0):
                    garp_pass = True
            if not (value_pass or garp_pass): continue

            score = -(pez if pd.notna(pez) else 0)*2 + fa_info["score"]/10
            if garp_pass: score += 2
            if boost_active: score += 1   # bonus during post-bear window
            candidates.append((tk, score, "VALUE" if value_pass else "GARP"))

        candidates.sort(key=lambda x: x[1], reverse=True)
        for tk, sc, path in candidates[:open_slots]:
            stk6m = ret6m.at[dt,tk] if tk in ret6m.columns else np.nan
            pez_now = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
            fin_info = get_fin_at(tk, dt)
            npr_v = fin_info["NP_R"] if fin_info is not None else np.nan
            rev_v = fin_info["Rev_YoY"] if fin_info is not None else np.nan
            tm = trend_mult(stk6m, vni6m)
            vm = valuation_mult_v6(pez_now)
            gm = growth_mult(npr_v, rev_v)
            init_pct = BASE_PCT * tm * vm * gm * sizing_boost
            init_pct = max(MIN_PCT, min(MAX_PCT, init_pct))
            alloc = init_pct * nav_now
            pending_buys.append({"ticker":tk,"type":"NEW","alloc_vnd":alloc,
                                  "signal_dt":dt,"path":path})

    # NAV
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt,"nav":nav,"cash":cash,"equity":mtm,"n_pos":len(positions),
                         "boost": boost_active})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
regime_df = pd.DataFrame(regime_log) if regime_log else pd.DataFrame(columns=["dt","event"])
print(f"\n  Sim complete: {len(trades_df)} events, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B")
print(f"  BearDvg episodes triggered: {(regime_df['event'].isin(['BEAR_FULL_LIQ','BEAR_TRIM_40'])).sum()}")
print(f"  Post-bear boost episodes: {(regime_df['event']=='BULL_POST_BEAR').sum()}")

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
    full_exits = trades_df[trades_df["side"].isin(["FA_DEGRADE","OVERVALUED","GROWTH_BROKEN","BEAR_FULL"])]
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
        print(f"\n  Top 15 by cum return (full exits only):")
        for tk, r in per_tk.head(15).iterrows():
            print(f"    {tk:<7} N={int(r['n']):2d}  avg={r['avg_ret']:+6.1f}%  cum={r['total_ret']:+7.1f}%  hold={r['avg_hold']:.0f}d")

nav_df.to_csv("qt_v6_nav.csv")
trades_df.to_csv("qt_v6_trades.csv", index=False)
regime_df.to_csv("qt_v6_regime.csv", index=False)
print("\nSaved: qt_v6_nav.csv, qt_v6_trades.csv, qt_v6_regime.csv")
