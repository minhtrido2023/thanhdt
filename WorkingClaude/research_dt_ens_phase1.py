# -*- coding: utf-8 -*-
"""research_dt_ens_phase1.py — DT4 × ensemble integration research, PHASE 1.

Goals:
  (A) Reproduce canonical V121_ENS in this harness (mirror test_v12_ensemble_dt.py
      data + VNINDEX-proxy switched-ETF leg) and confirm it reconciles with the
      documented crude-DT finding (ENS+DT ~ +0.46 Full / -0.61 OOS24).
  (B) E0 — answer the user's custom question: what TIMEFRAME / CADENCE should the
      switched-leg decision run on?  Sweep:
        - M1/M3 lookback horizon: 63d / 126d(canonical) / 252d
        - decision cadence: every 1 / 5 / 21 trading days
        - min-dwell between flips: 0 / 20 / 40 / 60 days
  (C) Cache leg NAV return series to data/dt_ens_legs.pkl for Phase 2.

All comparisons vs canonical V121_ENS TQ34b (daily AND-HOLD, 126d horizon, 0 dwell).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10; ETF_STATES = {3: 0.7}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
SWITCH_COST = 0.005

print("="*104); print("  PHASE 1 — harness validation + E0 switch cadence/horizon sweep"); print("="*104)

# ───────────────────────────────────────────────────────────────────────────
# 1. Common data
# ───────────────────────────────────────────────────────────────────────────
print("\n[1] Loading BA v11 signals + common data...")
with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))  # VNINDEX proxy (harness consistency)

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ───────────────────────────────────────────────────────────────────────────
# 2. LAGGED V12.1 leg (state-independent, runs once)
# ───────────────────────────────────────────────────────────────────────────
print("\n[2] LAGGED V12.1 leg (state-independent)...")
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]; cur_date = row["Release_Date"]; n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
e_hl3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])
ENTRY_OFFSET, HOLD_DAYS, MAX_POS_L, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged(init_nav, s2_sizing=True, park_state_ff=None, park_etf_states=None,
               sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    """LAGGED leg. If park_state_ff + park_etf_states given, park idle cash in VN30 ETF
    per state (DT-Kelly parking on LAGGED idle cash — design E1). Returns nav series.
    park accounting: ETF marked daily at vn30_underlying; friction 0.15%/side on rebalance."""
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
    ETF_FRIC = 0.0015
    etf_shares = 0.0  # parked ETF position (single pooled lot, marked daily)
    sched_dict = {(r["ticker"], r["entry_dt"]): r["surprise"] for _, r in sched_lag.iterrows()}
    for dt in sim_days:
        etf_px = vn30_underlying.get(dt)
        etf_px_ok = etf_px is not None and not pd.isna(etf_px) and etf_px > 0
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
                gross = pos["shares"]*fpx*(1-SLIP_OUT); cash += gross*(1-TAX); del positions[tk]
        # ETF PRE-FILL SELL (release parked cash so deals get priority)
        if park_etf_states is not None and etf_px_ok:
            st = park_state_ff.get(dt); st = int(st) if st is not None else 3
            frac = park_etf_states.get(st, 0.0)
            etf_val = etf_shares * etf_px
            pool = cash + etf_val
            target = pool * frac
            if etf_val - target > pool*0.005:
                sell_vnd = etf_val - target
                cash += sell_vnd - sell_vnd*ETF_FRIC
                etf_shares -= sell_vnd/etf_px
        # ENTRIES — with S2 sizing
        if dt in entries_by_day.groups:
            mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm + (etf_shares*etf_px if etf_px_ok else 0.0)
            for _, en_row in entries_by_day.get_group(dt).iterrows():
                tk = en_row["ticker"]
                if tk in positions or len(positions) >= MAX_POS_L: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
                pos_pct = (0.10 if sched_dict.get((tk, dt), 0) > 0.5 else 0.08) if s2_sizing else 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                # JIT unwind ETF if cash short
                if alloc > cash and park_etf_states is not None and etf_px_ok and etf_shares > 0:
                    need = alloc - cash
                    etf_val = etf_shares*etf_px
                    rel = min(need, etf_val)
                    cash += rel - rel*ETF_FRIC; etf_shares -= rel/etf_px
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        # ETF POST-FILL SWEEP (park leftover idle cash up to target)
        if park_etf_states is not None and etf_px_ok and cash > 0:
            st = park_state_ff.get(dt); st = int(st) if st is not None else 3
            frac = park_etf_states.get(st, 0.0)
            if frac > 0:
                etf_val = etf_shares*etf_px; pool = cash + etf_val
                target = pool*frac; delta = target - etf_val
                if delta > pool*0.005:
                    buy = min(delta, cash)
                    cash -= buy + buy*ETF_FRIC; etf_shares += buy/etf_px
        # EOD NAV
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        etf_val = etf_shares*etf_px if etf_px_ok else 0.0
        nav_history.append({"time":dt,"nav":cash+mtm+etf_val})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

nav_lag_v121 = run_lagged(BOOK_NAV, s2_sizing=True)
print(f"    LAGGED V12.1 (no park): {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# ───────────────────────────────────────────────────────────────────────────
# 3. BAL + VN30 under TQ34b (canonical SVT+overheat+parking)
# ───────────────────────────────────────────────────────────────────────────
def load_state_ff(state_csv):
    sdf = pd.read_csv(state_csv); sdf["time"] = pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"]>=START_B) & (sdf["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(sdf["time"], sdf["state"])); ff = {}; last=None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        ff[d] = last
    return sdf, ff

def run_state_legs(svt_csv, label, park_ff=None, park_etf_states=ETF_STATES):
    """BAL+VN30. SVT/overheat from svt_csv. ETF parking uses park_ff (defaults to svt state)."""
    sdf, sbd_ff = load_state_ff(svt_csv)
    park_ff = park_ff if park_ff is not None else sbd_ff
    v = vni_full.merge(sdf, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    overheat_dates = set(v[v["overheat"]]["time"])
    sig_v = sig_B.copy()
    sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=park_ff,
        cash_etf_states=park_etf_states, vn30_underlying=vn30_underlying, **LIQ, name=f"BAL_{label}")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"]); nav_bal_s = nav_bal.set_index("time")["nav"]
    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:vv for k,vv in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=park_ff,
        cash_etf_states=park_etf_states, vn30_underlying=vn30_underlying, **LIQ30, name=f"VN30_{label}")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"]); nav_vn30_s = nav_vn30.set_index("time")["nav"]
    print(f"    [{label}] BAL={nav_bal_s.iloc[-1]/1e9:.2f}B  VN30={nav_vn30_s.iloc[-1]/1e9:.2f}B")
    return nav_bal_s, nav_vn30_s

print("\n[3] BAL+VN30 under TQ34b (canonical)...")
nav_bal_tq, nav_vn30_tq = run_state_legs("vnindex_5state_tam_quan_v3_4b_full_history.csv", "TQ34b")

# ───────────────────────────────────────────────────────────────────────────
# 4. M1/M3 at multiple horizons (BQ recompute)
# ───────────────────────────────────────────────────────────────────────────
print("\n[4] Computing M1/M3 at horizons 63/126/252d...")
def pull_m1_m3(h):
    m1 = bq(f"""WITH base AS (
      SELECT t.time, SAFE_DIVIDE(t.Close, LAG(t.Close,{h}) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6
      FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{END_B}'
        AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
    vni AS (SELECT t.time, SAFE_DIVIDE(t.Close, LAG(t.Close,{h}) OVER (ORDER BY t.time))-1 AS vr
      FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2013-01-01' AND DATE '{END_B}')
    SELECT b.time, vni.vr - AVG(b.r6) AS M1 FROM base b JOIN vni USING(time)
    GROUP BY b.time, vni.vr ORDER BY b.time""")
    m1["time"] = pd.to_datetime(m1["time"])
    m3 = bq(f"""WITH base AS (
      SELECT t.time, t.ticker,
        SAFE_DIVIDE(t.Close, LAG(t.Close,{h}) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6,
        AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv1y
      FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{END_B}'
        AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
    ranked AS (SELECT time, r6, adv1y, ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv1y DESC) AS rnk
      FROM base WHERE adv1y IS NOT NULL AND r6 IS NOT NULL)
    SELECT time, AVG(IF(rnk<=10, r6, NULL)) - AVG(r6) AS M3r FROM ranked GROUP BY time ORDER BY time""")
    m3["time"] = pd.to_datetime(m3["time"])
    return m1.set_index("time")["M1"], m3.set_index("time")["M3r"]

def make_signal(metric, min_history=252):
    s = metric.dropna().sort_index()
    em = s.expanding(min_periods=min_history).median()
    raw = (s > em).astype(int)
    raw = raw.reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)

horizons = {63: None, 126: None, 252: None}
for h in horizons:
    m1r, m3r = pull_m1_m3(h)
    horizons[h] = (make_signal(m1r), make_signal(m3r))
    print(f"    h={h}: m1 {len(m1r)} pts, m3 {len(m3r)} pts")

# ───────────────────────────────────────────────────────────────────────────
# 5. Ensemble builders + metrics
# ───────────────────────────────────────────────────────────────────────────
def ensemble_signal(m1_bin, m3_bin, cadence=1, min_dwell=0):
    idx = m1_bin.index; out = np.zeros(len(idx), int)
    cur = int(m1_bin.iloc[0]); last_flip = -10**9
    for i in range(len(idx)):
        if (i % cadence == 0):
            a, b = int(m1_bin.iloc[i]), int(m3_bin.iloc[i])
            if a == b and a != cur and (i - last_flip) >= min_dwell:
                cur = a; last_flip = i
        out[i] = cur
    return pd.Series(out, index=idx)

def switched_nav(bal_ret, vn30_ret, lag_ret, signal, switch_cost=SWITCH_COST):
    common = bal_ret.index
    nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
    second = np.full(len(common), BOOK_NAV, dtype=float)
    prev = int(signal.iloc[0]); flips = 0
    for i in range(1, len(common)):
        cur = int(signal.iloc[i])
        if cur != prev: second[i] = second[i-1]*(1-switch_cost); flips += 1
        else: second[i] = second[i-1]
        r = vn30_ret.iloc[i] if cur==1 else lag_ret.iloc[i]
        second[i] = second[i]*(1+r); prev = cur
    total = nav_bal_path.values + second
    return pd.Series(total/TOTAL_NAV, index=common), flips

def metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100}

periods = [("FULL", "2014-01-01","2026-05-15"), ("IS 14-19","2014-01-01","2019-12-31"),
           ("OOS20","2020-01-01","2026-05-15"), ("OOS24","2024-01-01","2026-05-15")]

common = nav_bal_tq.index.intersection(nav_vn30_tq.index).intersection(nav_lag_v121.index)
bal_ret = nav_bal_tq.loc[common].pct_change().fillna(0)
vn30_ret = nav_vn30_tq.loc[common].pct_change().fillna(0)
lag_ret = nav_lag_v121.loc[common].pct_change().fillna(0)

# CANONICAL = h126 daily AND-HOLD, dwell 0
m1c, m3c = horizons[126]
m1c = m1c.reindex(common).ffill().fillna(1).astype(int)
m3c = m3c.reindex(common).ffill().fillna(1).astype(int)
sig_canon = ensemble_signal(m1c, m3c, cadence=1, min_dwell=0)
nav_canon, flips_canon = switched_nav(bal_ret, vn30_ret, lag_ret, sig_canon)

print("\n" + "="*104)
print(f"  CANONICAL V121_ENS (h126, daily, dwell0): flips={flips_canon}")
for pl, st, en in periods:
    m = metrics(nav_canon, pd.Timestamp(st), pd.Timestamp(en))
    print(f"    {pl:<10} CAGR={m['CAGR']:+.2f}%  Sharpe={m['Sharpe']:+.2f}  DD={m['DD']:+.2f}%")
print("="*104)

# ───────────────────────────────────────────────────────────────────────────
# 6. E0 sweep: horizon × cadence × min-dwell
# ───────────────────────────────────────────────────────────────────────────
print("\n[E0] Switch cadence/horizon sweep (Δ vs canonical, Full CAGR + OOS24 + DD + flips)")
print(f"  {'horizon':>7} {'cadence':>7} {'dwell':>5} | {'Full':>8} {'ΔFull':>7} | {'OOS24':>8} {'ΔOOS24':>8} | {'DD':>7} {'flips':>5}")
canon_full = metrics(nav_canon, pd.Timestamp("2014-01-01"), pd.Timestamp("2026-05-15"))["CAGR"]
canon_oos24 = metrics(nav_canon, pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-15"))["CAGR"]
e0_rows = []
for h in [63,126,252]:
    m1h, m3h = horizons[h]
    m1h = m1h.reindex(common).ffill().fillna(1).astype(int)
    m3h = m3h.reindex(common).ffill().fillna(1).astype(int)
    for cad in [1,5,21]:
        for dwell in [0,20,40,60]:
            sig = ensemble_signal(m1h, m3h, cadence=cad, min_dwell=dwell)
            nav, flips = switched_nav(bal_ret, vn30_ret, lag_ret, sig)
            mf = metrics(nav, pd.Timestamp("2014-01-01"), pd.Timestamp("2026-05-15"))
            mo = metrics(nav, pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-15"))
            tag = "  <-canon" if (h==126 and cad==1 and dwell==0) else ""
            print(f"  {h:>7} {cad:>7} {dwell:>5} | {mf['CAGR']:>+7.2f}% {mf['CAGR']-canon_full:>+6.2f} | "
                  f"{mo['CAGR']:>+7.2f}% {mo['CAGR']-canon_oos24:>+7.2f} | {mf['DD']:>+6.2f}% {flips:>5}{tag}")
            e0_rows.append({"horizon":h,"cadence":cad,"dwell":dwell,"full":mf['CAGR'],
                            "oos24":mo['CAGR'],"dd":mf['DD'],"flips":flips})
pd.DataFrame(e0_rows).to_csv("data/dt_ens_e0_sweep.csv", index=False)

# ───────────────────────────────────────────────────────────────────────────
# 7. Cache legs for Phase 2
# ───────────────────────────────────────────────────────────────────────────
cache = {
    "common": common,
    "bal_ret_tq": bal_ret, "vn30_ret_tq": vn30_ret, "lag_ret_v121": lag_ret,
    "nav_bal_tq": nav_bal_tq, "nav_vn30_tq": nav_vn30_tq, "nav_lag_v121": nav_lag_v121,
    "sig_canon": sig_canon, "m1_126": m1c, "m3_126": m3c,
}
with open("data/dt_ens_legs.pkl","wb") as f: pickle.dump(cache, f)
print("\n  Cached legs -> data/dt_ens_legs.pkl")
print("  E0 sweep    -> data/dt_ens_e0_sweep.csv")
print("\nDONE phase 1.")
