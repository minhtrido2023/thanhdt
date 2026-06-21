#!/usr/bin/env python3
"""
tune_lagged_pos.py
==================
Parameter sweep + tactical filters cho LAGGED_POS strategy.

Base config:
  HOLD_DAYS=25, ENTRY_OFFSET=5, NPR_MIN=0.15, POST_RET_MIN=5,
  MAX_POSITIONS=8, POS_PCT=0.10, LIQ_MIN_VND=2e9

Sweeps:
  E1: HOLD_DAYS = [15, 20, 25, 30, 40, 60]
  E2: ENTRY_OFFSET = [2, 3, 5, 7, 10]
  E3: NPR_MIN = [0.10, 0.15, 0.20, 0.25, 0.30]
  E4: POST_RET_MIN = [3, 5, 8, 10, 15]
  F1: Require both NP_R AND Revenue_YoY ≥ 15%
  F2: Pre-release dip filter (pre_ret_30d < +5%)
  F3: Skip when VNI 6M return > +25% (overheated bull)
  F4: Sector boost — Securities/REIT_RES get POS_PCT=0.13
  F5: Top-100 universe by avg_post_good
  COMBO: best E + F stacked
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
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

# ─── Load shared data once ────────────────────────────────────────────────
print("[Load] price + OV cache ...")
with open("data/earnings_px.pkl","rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_close = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq     = liq.reindex(master_idx).ffill(limit=5)

events_all = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
prof = pd.read_csv("data/ticker_reaction_profile.csv", index_col=0)

# VNI for filter F3
vni_df = bq_query("SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time>='2009-01-01' AND t.Close>100 ORDER BY t.time")
vni_df["time"] = pd.to_datetime(vni_df["time"])
vni_px = vni_df.set_index("time")["Close"]
vni_px = vni_px.reindex(master_idx).ffill()
vni_6m = vni_px.pct_change(126) * 100  # for F3

# FA for sector (F4)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time"])
fa_uni = fa.sort_values("quarter").drop_duplicates("ticker", keep="last")[["ticker","sub","MktCap"]]
ticker_sub = dict(zip(fa_uni["ticker"], fa_uni["sub"]))

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

def get_offset_close(tk, ref_dt, offset):
    if tk not in px_close.columns: return np.nan
    pos = np.searchsorted(all_dates, np.datetime64(ref_dt), side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + offset
    if tgt < 0 or tgt >= len(all_dates): return np.nan
    return px_close.iloc[tgt][tk]

# ─── Backtest function ───────────────────────────────────────────────────
def backtest(cfg):
    nm = cfg["name"]
    POST_RET_MIN = cfg.get("post_ret_min", 5.0)
    N_GOOD_MIN = cfg.get("n_good_min", 4)
    NPR_MIN = cfg.get("npr_min", 0.15)
    REV_REQ = cfg.get("rev_req", False)
    PRE_DIP_MAX = cfg.get("pre_dip_max", None)  # if set, require pre_30d < this
    ENTRY_OFFSET = cfg.get("entry_offset", 5)
    HOLD_DAYS = cfg.get("hold_days", 25)
    MAX_POS = cfg.get("max_pos", 8)
    POS_PCT = cfg.get("pos_pct", 0.10)
    SECTOR_BOOST = cfg.get("sector_boost", None)  # {"SECURITIES": 0.13}
    VNI_6M_MAX = cfg.get("vni_6m_max", None)
    TOP_N_UNI = cfg.get("top_n_uni", None)
    LIQ_MIN = cfg.get("liq_min", 2e9)
    SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
    DEPOSIT_RATE = 0.01
    LIQ_CAP_PCT = 0.20
    MAX_FILL_DAYS = 5

    # Universe
    mask = (prof["avg_post_good"] >= POST_RET_MIN) & (prof["n_good"] >= N_GOOD_MIN)
    if TOP_N_UNI:
        universe = prof[mask].nlargest(TOP_N_UNI, "avg_post_good").index.tolist()
    else:
        universe = prof[mask].index.tolist()

    ev = events_all[events_all["ticker"].isin(universe)].copy()
    ev = ev[ev["NP_R"] >= NPR_MIN * 100]
    if REV_REQ:
        ev = ev[ev["Rev_YoY"] >= 15]

    # Build schedule
    schedule = []
    for _, row in ev.iterrows():
        tk = row["ticker"]; rdt = row["Release_Date"]
        if tk not in px_open.columns: continue
        if PRE_DIP_MAX is not None:
            p_m30 = get_offset_close(tk, rdt, -30)
            p_m1  = get_offset_close(tk, rdt, -1)
            if pd.isna(p_m30) or pd.isna(p_m1) or p_m30 <= 0: continue
            pre_ret = (p_m1/p_m30 - 1) * 100
            if pre_ret >= PRE_DIP_MAX: continue
        entry_dt = offset_date(rdt, ENTRY_OFFSET)
        exit_dt  = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
        if entry_dt is None or exit_dt is None: continue
        if VNI_6M_MAX is not None:
            v = vni_6m.get(entry_dt, np.nan)
            if pd.notna(v) and v > VNI_6M_MAX: continue
        schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt, "release_dt":rdt})
    sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
    entries_by_day = sched.groupby("entry_dt")
    exits_by_day = sched.groupby("exit_dt")

    # Sim
    start_dt = pd.Timestamp("2010-01-01"); end_dt = pd.Timestamp("2026-05-13")
    sim_days = [d for d in master_idx if start_dt <= d <= end_dt]
    cash = INIT_NAV; positions = {}; nav_history = []; trades = []
    daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

    for dt in sim_days:
        cash *= (1 + daily_rate)
        # EXITS
        if dt in exits_by_day.groups:
            for _, ex_row in exits_by_day.get_group(dt).iterrows():
                tk = ex_row["ticker"]
                if tk not in positions: continue
                pos = positions[tk]
                if pos["exit_dt"] != dt: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                gross = pos["shares"] * fpx * (1 - SLIP_OUT)
                net = gross * (1 - TAX_SALE)
                cash += net
                ret_pct = (fpx / pos["entry_px"] - 1) * 100
                trades.append({"dt":dt,"ticker":tk,"side":"SELL","ret_pct":ret_pct,
                               "hold_days":(dt-pos["entry_dt"]).days,
                               "release_dt":pos["release_dt"]})
                del positions[tk]
        # ENTRIES
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
                      if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions: continue
                if len(positions) >= MAX_POS: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq.at[dt, tk] if tk in liq.columns else 0
                if pd.isna(adv) or adv * fpx < LIQ_MIN: continue
                # Position sizing
                pct = POS_PCT
                if SECTOR_BOOST is not None:
                    sub = ticker_sub.get(tk, "DEFAULT")
                    if sub in SECTOR_BOOST: pct = SECTOR_BOOST[sub]
                target = pct * nav_now
                cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx * (1 + SLIP_IN)
                shares = alloc / eff_px
                cost = shares * eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"],
                                  "shares":shares, "entry_px":fpx,
                                  "release_dt":en_row["release_dt"]}
                trades.append({"dt":dt,"ticker":tk,"side":"BUY","ret_pct":0,
                               "hold_days":0,"release_dt":en_row["release_dt"]})
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav = cash + mtm
        nav_history.append({"date":dt,"nav":nav,"cash":cash,"n_pos":len(positions)})

    nav_df = pd.DataFrame(nav_history).set_index("date")
    trades_df = pd.DataFrame(trades)
    sells = trades_df[trades_df["side"]=="SELL"]

    def metrics_for(start, end):
        s = nav_df["nav"][(nav_df.index>=start) & (nav_df.index<=end)]
        if len(s) < 30: return None
        yrs = (s.index[-1]-s.index[0]).days/365.25
        cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
        rets = s.pct_change().dropna()
        spy = len(rets)/yrs
        sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
        dd = (s - s.cummax())/s.cummax()
        mdd = dd.min()
        cal = cagr/abs(mdd) if mdd<0 else 0
        return cagr*100, sh, mdd*100, cal

    full = metrics_for(pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13"))
    oos  = metrics_for(pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13"))
    y22  = metrics_for(pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))
    q126 = metrics_for(pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30"))
    wr   = (sells["ret_pct"]>0).mean()*100 if len(sells)>0 else 0
    avg  = sells["ret_pct"].mean() if len(sells)>0 else 0
    return {
        "name": nm, "n_trades": len(sells), "WR": wr, "avg_ret": avg,
        "full_CAGR": full[0] if full else 0, "full_Sharpe": full[1] if full else 0,
        "full_DD": full[2] if full else 0, "full_Calmar": full[3] if full else 0,
        "oos_CAGR": oos[0] if oos else 0, "oos_Sharpe": oos[1] if oos else 0,
        "y22_CAGR": y22[0] if y22 else 0,
        "q126_CAGR": q126[0] if q126 else 0,
        "final_nav": nav_df["nav"].iloc[-1]/1e9,
    }

# ─── Run experiments ─────────────────────────────────────────────────────
configs = [
    {"name": "BASE"},
    # E1: hold days
    {"name": "E1_hold15", "hold_days":15},
    {"name": "E1_hold20", "hold_days":20},
    {"name": "E1_hold30", "hold_days":30},
    {"name": "E1_hold40", "hold_days":40},
    {"name": "E1_hold60", "hold_days":60},
    # E2: entry offset
    {"name": "E2_ent2",  "entry_offset":2},
    {"name": "E2_ent3",  "entry_offset":3},
    {"name": "E2_ent7",  "entry_offset":7},
    {"name": "E2_ent10", "entry_offset":10},
    # E3: NPR threshold
    {"name": "E3_npr10", "npr_min":0.10},
    {"name": "E3_npr20", "npr_min":0.20},
    {"name": "E3_npr25", "npr_min":0.25},
    {"name": "E3_npr30", "npr_min":0.30},
    # E4: universe threshold
    {"name": "E4_post3",  "post_ret_min":3},
    {"name": "E4_post8",  "post_ret_min":8},
    {"name": "E4_post10", "post_ret_min":10},
    # F1: Rev_YoY also required
    {"name": "F1_revreq", "rev_req":True},
    # F2: pre-release dip filter
    {"name": "F2_dip0",  "pre_dip_max":0},
    {"name": "F2_dip5",  "pre_dip_max":5},
    # F3: skip overheated bull
    {"name": "F3_vni25", "vni_6m_max":25},
    {"name": "F3_vni15", "vni_6m_max":15},
    # F4: sector boost
    {"name": "F4_secboost", "sector_boost":{"SECURITIES":0.13, "REIT_RES":0.13}},
    # F5: top-N universe
    {"name": "F5_top100", "top_n_uni":100},
    {"name": "F5_top50",  "top_n_uni":50},
    # COMBO: stack best
    {"name": "COMBO_a", "hold_days":30, "npr_min":0.20, "pre_dip_max":5, "vni_6m_max":25},
    {"name": "COMBO_b", "hold_days":40, "npr_min":0.20, "pre_dip_max":0, "rev_req":True},
    {"name": "COMBO_c", "hold_days":30, "post_ret_min":8, "pre_dip_max":5},
]

results = []
print(f"\nRunning {len(configs)} configs ...\n")
for i, cfg in enumerate(configs):
    print(f"[{i+1:>2}/{len(configs)}] {cfg['name']:<16} ...", end="", flush=True)
    try:
        r = backtest(cfg)
        results.append(r)
        print(f" N={r['n_trades']:3d}  WR={r['WR']:.1f}%  avg={r['avg_ret']:+.2f}%  "
              f"full_CAGR={r['full_CAGR']:+.2f}%  Sh={r['full_Sharpe']:.2f}  "
              f"DD={r['full_DD']:.1f}%  Q126={r['q126_CAGR']:+.1f}%", flush=True)
    except Exception as e:
        print(f" ERROR: {e}")
        continue

# ─── Sort + report ───────────────────────────────────────────────────────
df = pd.DataFrame(results)
df.to_csv("data/lagged_pos_tune_results.csv", index=False)

print("\n" + "="*120)
print("  TOP 10 BY FULL CAGR")
print("="*120)
print(df.nlargest(10, "full_CAGR").to_string(index=False, float_format="%.2f"))

print("\n" + "="*120)
print("  TOP 10 BY SHARPE")
print("="*120)
print(df.nlargest(10, "full_Sharpe").to_string(index=False, float_format="%.2f"))

print("\n" + "="*120)
print("  TOP 10 BY CALMAR")
print("="*120)
print(df.nlargest(10, "full_Calmar").to_string(index=False, float_format="%.2f"))

print("\nSaved: lagged_pos_tune_results.csv")
