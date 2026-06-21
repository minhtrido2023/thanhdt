#!/usr/bin/env python3
"""
backtest_qt_v5.py — "Dynamic Conviction Compounder"
====================================================
Cải tiến v4:
  (i)   Extended FA universe: UNION fa_ratings_pre2014 + fa_ratings_lh
        → tickers lớn có FA history từ 2007 → vào universe ngay từ 2014-04
  (ii)  Quarterly dynamic sizing: target_weight = 10% × trend × val × growth
        Rebalance khi |cur - tgt| > 2pp → thay daily avg-down
  (iii) Winner runs (1.5x), loser trim (0.5x) — Buffett add-to-strength

Entry (giữ v4): VALUE path (PE_z<-1 OR PB_z<-1 OR DD<-30) + above-MA200 soft
                hoặc GARP path (PEG≤1 AND NP_YoY≥20% AND Rev_YoY≥20% AND PE<25 AND above MA200)
Exit (giữ v4):  FA_DEGRADE / OVERVALUED / GROWTH_BROKEN

Sim: 50B init, T+1 open, slip 0.1/0.15%, tax 0.1%, liq cap 20%×5d, deposit 1%/yr
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

# ─── 1. Extended FA universe (pre-2014 + current) ────────────────────────
print("[1] Loading + extending FA universe ...", flush=True)
fa_lh = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa_lh = fa_lh[["ticker","quarter","time","Release_Date","tier","score","sub"]]
print(f"  fa_ratings_lh: {len(fa_lh):,} rows, {fa_lh['ticker'].nunique()} tickers, quarter range {fa_lh['quarter'].min()} → {fa_lh['quarter'].max()}")

ext_cache = "qt_v5_fa_pre2014.pkl"
if os.path.exists(ext_cache):
    with open(ext_cache,"rb") as f: fa_pre = pickle.load(f)
    print(f"  Loaded pre-2014 cache: {len(fa_pre):,} rows")
else:
    fa_pre = bq_query("""
    SELECT f.ticker, f.quarter, f.time, f.tier, f.total_score AS score
    FROM tav2_bq.fa_ratings_pre2014 AS f
    """)
    fa_pre["time"] = pd.to_datetime(fa_pre["time"])
    fa_pre["Release_Date"] = fa_pre["time"] + pd.Timedelta(days=60)
    fa_pre["sub"] = "PRE2014"
    with open(ext_cache,"wb") as f: pickle.dump(fa_pre, f)
    print(f"  Pulled pre-2014 FA: {len(fa_pre):,} rows, {fa_pre['ticker'].nunique()} tickers")

# Combine (pre-2014 first, then current; dedupe on ticker+quarter keeping current as authoritative)
fa = pd.concat([fa_pre, fa_lh], ignore_index=True)
fa = fa.drop_duplicates(subset=["ticker","quarter"], keep="last")
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)
print(f"  Combined FA: {len(fa):,} rows, {fa['ticker'].nunique()} tickers")
print(f"  Quarter range after union: {fa['quarter'].min()} → {fa['quarter'].max()}")

# Quality lookup at (ticker, quarter)
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
print(f"  Quality entries (≥12Q history): {len(quality_at_q):,}")

# ─── 2. Panel load + features ────────────────────────────────────────────
print("\n[2] Loading TA panel cache ...", flush=True)
with open("qt_panel_2014_2026.pkl","rb") as f: panel = pickle.load(f)
panel["time"] = pd.to_datetime(panel["time"])
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)

panel["hi_52w"]    = panel.groupby("ticker")["Close"].transform(lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"]= (panel["Close"]/panel["hi_52w"] - 1) * 100
panel["pe_z"]      = ((panel["PE"]-panel["PE_MA5Y"])/panel["PE_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["pb_z"]      = ((panel["PB"]-panel["PB_MA5Y"])/panel["PB_SD5Y"].replace(0,np.nan)).clip(-10,10)
panel["vs_MA200"]  = (panel["Close"]/panel["MA200"] - 1) * 100
panel["ret_6m"]    = panel.groupby("ticker")["Close"].pct_change(126) * 100
print(f"  Panel: {len(panel):,} rows")

# ─── 3. Quarterly financial (PEG/NP_R/Revenue_YoY) ───────────────────────
fin_cache = "qt_v4_fin.pkl"
with open(fin_cache,"rb") as f: fin = pickle.load(f)
fin["q_time"] = pd.to_datetime(fin["q_time"])
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
fin["eff_release"] = fin["Release_Date"].fillna(fin["q_time"] + pd.Timedelta(days=60))
fin_map = {tk: g.sort_values("eff_release").reset_index(drop=True) for tk, g in fin.groupby("ticker")}
print(f"  Loaded financial cache: {len(fin):,} rows")

# FA release timeline
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

# ─── 4. Pivots ───────────────────────────────────────────────────────────
print("\n[4] Setting up pivots ...", flush=True)
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
px_open  = panel.pivot_table(index="time", columns="ticker", values="Open",  aggfunc="first").sort_index().ffill()
ma200    = panel.pivot_table(index="time", columns="ticker", values="MA200", aggfunc="first").sort_index().ffill()
pe_z     = panel.pivot_table(index="time", columns="ticker", values="pe_z",  aggfunc="first").sort_index().ffill()
pb_z     = panel.pivot_table(index="time", columns="ticker", values="pb_z",  aggfunc="first").sort_index().ffill()
dd_52w   = panel.pivot_table(index="time", columns="ticker", values="dd_52w_pct", aggfunc="first").sort_index().ffill()
vs_ma200 = panel.pivot_table(index="time", columns="ticker", values="vs_MA200", aggfunc="first").sort_index().ffill()
pe_d     = panel.pivot_table(index="time", columns="ticker", values="PE", aggfunc="first").sort_index().ffill()
liq      = panel.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill()
ret6m    = panel.pivot_table(index="time", columns="ticker", values="ret_6m", aggfunc="first").sort_index().ffill()

trading_days = sorted(panel["time"].unique())

# VNINDEX
vni = bq_query("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2014-01-01' AND t.Close > 100 ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"]
vni_ret6m = vni_px.pct_change(126) * 100

# ─── 5. Conviction scoring + sizing rules ────────────────────────────────
def trend_mult(stock_6m, vni_6m):
    if pd.isna(stock_6m) or pd.isna(vni_6m): return 1.0
    ex = stock_6m - vni_6m
    if ex > 20: return 1.5
    if ex > 10: return 1.2
    if ex < -20: return 0.5
    if ex < -10: return 0.7
    return 1.0

def valuation_mult(pez):
    if pd.isna(pez): return 1.0
    if pez < -1.5: return 1.3
    if pez < 0:    return 1.1
    if pez < 1:    return 1.0
    if pez < 2:    return 0.7
    return 0.4

def growth_mult(npr, rev):
    if pd.isna(npr) or pd.isna(rev): return 1.0
    if npr >= 0.20 and rev >= 0.20: return 1.2
    if npr >= 0.10 or rev >= 0.10:  return 1.0
    if npr >= 0 and rev >= 0:       return 0.9
    if npr < -0.10 and rev < -0.10: return 0.5
    return 0.8

BASE_PCT  = 0.10
MIN_PCT   = 0.03
MAX_PCT   = 0.25
REBAL_THR = 0.02   # 2pp drift trigger

# ─── 6. Backtest ─────────────────────────────────────────────────────────
print("\n[6] Running QT v5 (dynamic conviction) backtest ...", flush=True)
MAX_POSITIONS = 8
LIQ_CAP_PCT   = 0.20
MAX_FILL_DAYS = 5
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE  = 0.01
BL_DAYS_FA    = 90
BL_DAYS_OVR   = 30
PE_Z_OVR, PB_Z_OVR = 2.5, 1.5
GROWTH_BAD_THR = -0.15

start_dt, end_dt = pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")
# Reindex all pivots to master date list (px_close is canonical — always has data)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
px_open  = px_open.reindex(master_idx).ffill()
ma200    = ma200.reindex(master_idx).ffill()
pe_z     = pe_z.reindex(master_idx).ffill()
pb_z     = pb_z.reindex(master_idx).ffill()
dd_52w   = dd_52w.reindex(master_idx).ffill()
vs_ma200 = vs_ma200.reindex(master_idx).ffill()
pe_d     = pe_d.reindex(master_idx).ffill()
liq      = liq.reindex(master_idx).ffill()
ret6m    = ret6m.reindex(master_idx).ffill()
vni_px.index = pd.DatetimeIndex(vni_px.index).as_unit("ns")
vni_px = vni_px.reindex(master_idx).ffill()
vni_ret6m = vni_px.pct_change(126) * 100
sim_days = [d for d in master_idx if start_dt <= d <= end_dt]

cash = INIT_NAV
positions = {}      # tk → {entry_dt, entry_px, shares, total_cost, last_release_dt}
blacklist = {}
nav_history, trades = [], []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

pending_buys, pending_sells = [], []   # buy: {ticker, alloc_vnd, type, signal_dt}; sell: {ticker, shares, reason}

print(f"  Sim window: {start_dt.date()} → {end_dt.date()} ({len(sim_days)} days)")

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={(cash+mtm)/1e9:.2f}B pos={len(positions)} cash={cash/1e9:.1f}B", flush=True)
    cash *= (1 + daily_rate)

    # ── T+1 Sells first ──
    nps = []
    for s in pending_sells:
        tk = s["ticker"]
        if tk not in positions: continue
        if tk not in px_open.columns: continue
        fpx = px_open.at[dt, tk]
        if pd.isna(fpx) or fpx <= 0: nps.append(s); continue
        pos = positions[tk]
        sell_shares = min(s["shares"], pos["shares"])
        gross = sell_shares * fpx * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        avg_entry = pos["total_cost"]/pos["shares"] if pos["shares"]>0 else pos["entry_px"]
        trades.append({"dt":dt,"ticker":tk,"side":s["reason"],"shares":sell_shares,
                       "px":fpx,"net":net,"entry_dt":pos["entry_dt"],"entry_px":avg_entry,
                       "ret_pct":(fpx/avg_entry-1)*100,"hold_days":(dt-pos["entry_dt"]).days})
        pos["shares"] -= sell_shares
        pos["total_cost"] -= (pos["total_cost"]/(pos["shares"]+sell_shares)) * sell_shares if pos["shares"]+sell_shares > 0 else 0
        if pos["shares"] <= 1e-6 or s["reason"] in ("FA_DEGRADE","OVERVALUED","GROWTH_BROKEN"):
            bl = BL_DAYS_OVR if s["reason"]=="OVERVALUED" else BL_DAYS_FA
            blacklist[tk] = dt + pd.Timedelta(days=bl)
            if tk in positions: del positions[tk]
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
        else:  # REBAL_ADD
            pos = positions[tk]
            pos["shares"] += shares
            pos["total_cost"] += cost
            trades.append({"dt":dt,"ticker":tk,"side":"REBAL_ADD","shares":shares,"px":fpx,
                            "net":-cost,"entry_dt":pos["entry_dt"],"entry_px":pos["total_cost"]/pos["shares"],
                            "ret_pct":(fpx/(pos["total_cost"]/pos["shares"])-1)*100,
                            "hold_days":(dt-pos["entry_dt"]).days})
    pending_buys = []

    # ── Check exits + quarterly rebalance for each position ──
    mtm_now = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_now = cash + mtm_now
    vni_6m_t = vni_ret6m.get(dt, np.nan)

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

        # Quarterly rebalance — trigger when a new financial release arrived
        if fin_info is None: continue
        rel_dt = fin_info["release_dt"]
        if rel_dt <= pos["last_release_dt"]:
            continue   # already processed this quarter

        # Mark this release as processed
        pos["last_release_dt"] = rel_dt

        # Compute conviction
        stk6m = ret6m.at[dt,tk] if tk in ret6m.columns else np.nan
        pez_now = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
        tm = trend_mult(stk6m, vni_6m_t)
        vm = valuation_mult(pez_now)
        gm = growth_mult(fin_info["NP_R"], fin_info["Rev_YoY"])
        target_pct = BASE_PCT * tm * vm * gm
        target_pct = max(MIN_PCT, min(MAX_PCT, target_pct))

        # Current weight
        cur_value = pos["shares"] * p_today
        cur_pct = cur_value / nav_now
        diff_pct = target_pct - cur_pct

        if abs(diff_pct) < REBAL_THR:
            continue

        if diff_pct > 0:
            alloc = diff_pct * nav_now
            if alloc < 1e6: continue
            pending_buys.append({"ticker":tk, "type":"REBAL_ADD",
                                  "alloc_vnd":alloc, "signal_dt":dt})
        else:
            sell_pct = abs(diff_pct)
            sell_shares = (sell_pct * nav_now) / p_today
            sell_shares = min(sell_shares, pos["shares"])
            if sell_shares * p_today < 1e6: continue
            pending_sells.append({"ticker":tk,"shares":sell_shares,"reason":"REBAL_TRIM"})

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
            candidates.append((tk, score, "VALUE" if value_pass else "GARP"))

        candidates.sort(key=lambda x: x[1], reverse=True)
        for tk, sc, path in candidates[:open_slots]:
            # Initial conviction sizing
            stk6m = ret6m.at[dt,tk] if tk in ret6m.columns else np.nan
            pez_now = pe_z.at[dt,tk] if tk in pe_z.columns else np.nan
            fin_info = get_fin_at(tk, dt)
            npr_v = fin_info["NP_R"] if fin_info is not None else np.nan
            rev_v = fin_info["Rev_YoY"] if fin_info is not None else np.nan
            tm = trend_mult(stk6m, vni_6m_t)
            vm = valuation_mult(pez_now)
            gm = growth_mult(npr_v, rev_v)
            init_pct = BASE_PCT * tm * vm * gm
            init_pct = max(MIN_PCT, min(MAX_PCT, init_pct))
            alloc = init_pct * nav_now
            pending_buys.append({"ticker":tk,"type":"NEW","alloc_vnd":alloc,
                                  "signal_dt":dt,"path":path})

    # NAV mark-to-market
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt,"nav":nav,"cash":cash,"equity":mtm,"n_pos":len(positions)})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} events, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B")

# ─── 7. Metrics + report ─────────────────────────────────────────────────
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

vni_aligned = vni_px.reindex(nav_df.index).ffill()
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
    m = metrics(nav_df["nav"], ps, pe); vm = metrics(vni_aligned, ps, pe)
    if m is None or vm is None: continue
    a = m["CAGR"] - vm["CAGR"]
    print(f"  {nm:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+10.2f}{m['MaxDD']:>+9.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+9.2f}%{a:>+9.2f}pp")

if len(trades_df) > 0:
    full_exits = trades_df[trades_df["side"].isin(["FA_DEGRADE","OVERVALUED","GROWTH_BROKEN"])]
    print(f"\n  --- Trade summary ---")
    print(f"  Total events: {len(trades_df)}")
    print(f"  Buys: {(trades_df['side']=='BUY').sum()}  | Rebal-add: {(trades_df['side']=='REBAL_ADD').sum()}  | Rebal-trim: {(trades_df['side']=='REBAL_TRIM').sum()}  | Full-exits: {len(full_exits)}")
    if len(full_exits) > 0:
        for rs, g in full_exits.groupby("side"):
            print(f"    {rs:<14}: N={len(g):3d}, avg_ret={g['ret_pct'].mean():+6.1f}%, median_hold={g['hold_days'].median():.0f}d, WR={(g['ret_pct']>0).mean()*100:.1f}%")
        print(f"  Avg hold (full exits): {full_exits['hold_days'].mean():.0f}d | Avg ret: {full_exits['ret_pct'].mean():+.2f}%")
        print(f"  Win rate: {(full_exits['ret_pct']>0).mean()*100:.1f}%")
        if len(full_exits)>0:
            print(f"  Best: {full_exits['ret_pct'].max():+.1f}% ({full_exits.loc[full_exits['ret_pct'].idxmax(),'ticker']})")
            print(f"  Worst: {full_exits['ret_pct'].min():+.1f}% ({full_exits.loc[full_exits['ret_pct'].idxmin(),'ticker']})")

        per_tk = full_exits.groupby("ticker").agg(n=("ticker","size"),avg_ret=("ret_pct","mean"),
                                                    total_ret=("ret_pct","sum"),avg_hold=("hold_days","mean"))
        per_tk = per_tk.sort_values("total_ret", ascending=False)
        print(f"\n  Top 15 by cum return (full exits only):")
        for tk, r in per_tk.head(15).iterrows():
            print(f"    {tk:<7} N={int(r['n']):2d}  avg={r['avg_ret']:+6.1f}%  cum={r['total_ret']:+7.1f}%  hold={r['avg_hold']:.0f}d")

nav_df.to_csv("qt_v5_nav.csv")
trades_df.to_csv("qt_v5_trades.csv", index=False)
print("\nSaved: qt_v5_nav.csv, qt_v5_trades.csv")
