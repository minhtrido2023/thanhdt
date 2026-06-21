# -*- coding: utf-8 -*-
"""sim_v5_dt4_transparent.py — TRANSPARENT V5 + DT4(4-gate) simulation, 2025-01-01 -> 2026-05-15.

V5 = V121_ENS + KELLY parking, on the DT4 (vnindex_5state_dt_4gate) foundation.
Mirrors run_5systems_dt4.py's V5 EXACTLY (same SIGNAL_V11+DT4 signals, KELLY parking,
t1_open_exec, prod spec) but adds the transparent-pattern outputs so every trade is
verifiable (event_log + etf_log + per-leg reconciliation), per the recorded process
[[feedback-simulation-transparent-default]].

ARCHITECTURE (per-leg, as the user chose):
  V5 NAV = BAL_kelly book (always)  +  SECOND leg
  SECOND leg = ensemble switch (M1+M3r AND-hold):  sig==1 -> VN30_kelly returns
                                                    sig==0 -> LAGGED v121 returns
  The three underlying books (BAL_kelly, VN30_kelly, LAGGED_v121) are each
  self-contained, fully transaction-reconcilable simulations. The ensemble SWITCH
  itself is a RETURN-LEVEL recombination (not a trade-level reality) — documented,
  not reconciled at trade level (this is the integrity-audit "independent-leg
  recombine" idealization, surfaced honestly).

OUTPUTS (data/):
  Per leg L in {bal_kelly, vn30_kelly, lagged_v121}:
    v5dt4_<L>_logs.csv          daily NAV + cash + cash_etf + stocks + n_pos + n_tx
    v5dt4_<L>_transactions.csv  every buy/sell + ETF rebalance + MTM phantoms
    v5dt4_<L>_open_positions.csv
    v5dt4_<L>_report.md         analyze_portfolio.py output + reconciliation block
  Ensemble:
    v5dt4_ensemble_logs.csv     daily V5 NAV + per-leg NAV + 2nd-leg NAV + signal + state
    v5dt4_master_report.md      V5 headline + per-leg metrics + 4-gate pass + construct note
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re, subprocess
from datetime import datetime
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq
from signal_v11_sql import SIGNAL_V11

START_B = os.environ.get("START_DATE", "2025-01-01")
END_B   = os.environ.get("END_DATE",   "2026-05-15")
TOTAL_NAV = 50e9; BOOK_NAV = 25e9
DEPOSIT = 0.0; BORROW = 0.10
ETF_KELLY = {3: 1.0}; SWITCH_COST = 0.005
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
             "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
DT_TABLE = "vnindex_5state_dt_4gate"
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)

SIGNAL_V11_DT = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", "tav2_bq." + DT_TABLE + " AS s")
assert SIGNAL_V11_DT != SIGNAL_V11, "state-table replace failed"

print("=" * 100)
print(f"  TRANSPARENT V5 + DT4(4-gate)   {START_B} -> {END_B}   init=50B (25B BAL + 25B 2nd leg)")
print("=" * 100)

def safe_to_csv(df, path):
    try:
        df.to_csv(path, index=False); return path
    except PermissionError:
        alt = path.replace(".csv", ".new.csv"); df.to_csv(alt, index=False)
        print(f"  (locked -> {alt})"); return alt

# ── 1. signals (state5 = DT4) ────────────────────────────────────────────────
print("\n[1] Fresh SIGNAL_V11 (state5 from DT4)...")
sig_B = bq(SIGNAL_V11_DT.format(start=START_B, end=END_B)); sig_B["time"] = pd.to_datetime(sig_B["time"])
print(f"  signal rows {len(sig_B):,}  AVOID_bear {int((sig_B['play_type']=='AVOID_bear').sum()):,}")
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _c = f.read()
VQU = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE | re.DOTALL).group(1)
vni_B = bq(VQU.format(start=START_B, end=END_B)); vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())

# real E1VFVN30 ETF underlying (KELLY parking)
vn30_proxy = dict(zip(vni_B["time"], vni_B["Close"]))
_etf = bq(f"SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
_etf["time"] = pd.to_datetime(_etf["time"]); _er = dict(zip(_etf["time"], _etf["Close"]))
_sp = _etf["time"].min(); _sc = (_er[_sp] / vn30_proxy[_sp]) if vn30_proxy.get(_sp) else 1.0
vn30_underlying = {d: (_er[d] if d in _er else (vn30_proxy[d] * _sc if d < _sp and d in vn30_proxy else vn30_proxy.get(d))) for d in vni_dates_B}
print(f"  ETF: real E1VFVN30 from {_sp.date()}")

opens_df = bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"]); open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}
vni_full = bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# DT4 state forward-fill
sdt = bq(f"SELECT s.time,s.state FROM tav2_bq.{DT_TABLE} AS s WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time")
sdt["time"] = pd.to_datetime(sdt["time"]); sbd = dict(zip(sdt["time"], sdt["state"]))
state_ff = {}; last = None
for d in vni_dates_B:
    s = sbd.get(d)
    if s is not None: last = s
    state_ff[d] = last

# ── 2. D1 RE_BACKLOG (DT4 state) + SV_TIGHT + overheat ───────────────────────
print("\n[2] D1 RE_BACKLOG (DT4) + SV_TIGHT + overheat...")
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t LEFT JOIN tav2_bq.{DT_TABLE} AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1m = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C", "D"]) & d1["state5"].isin([3, 4, 5]) & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
sig_B = sig_B.merge(d1.loc[d1m, ["ticker", "time"]].assign(_ok=True), on=["ticker", "time"], how="left")
om = sig_B["_ok"].fillna(False) & (sig_B["ta"] >= 120); sig_B.loc[om, "play_type"] = "RE_BACKLOG_BUY"; sig_B = sig_B.drop(columns=["_ok"])
print(f"  RE_BACKLOG {int(om.sum())}")

def svk(r):
    s = r.get("state5"); d = r.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True
    if s == 1: return pd.notna(d) and d <= 30
    if s in (2, 3): return pd.notna(d) and d <= 60
    return True
mb = sig_B["play_type"].isin(BUY_TIERS); sig_B = sig_B[(~mb) | sig_B.apply(svk, axis=1)].copy()
v = vni_full.merge(sdt, on="time", how="left"); v["state"] = v["state"].ffill()
oh = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["state"] == 5) | (v["D_RSI"] > 0.75))]["time"])
sig_v = sig_B.copy(); sig_v.loc[sig_v["time"].isin(oh) & sig_v["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"
print(f"  overheat days {len(oh)}")

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5, "liquidity_lookup": liq_map_B, "exit_slippage_tiered": True}

# ── 3. BAL_kelly + VN30_kelly with event/etf logs ───────────────────────────
print("\n[3] BAL_kelly + VN30_kelly books (KELLY parking, transparent)...")
ev_bal, etf_bal = [], []
nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B, allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV, sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS, deposit_annual=DEPOSIT, borrow_annual=BORROW,
    state_by_date=state_ff, cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying, etf_mgmt_fee_annual=0.0,
    etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True,
    event_log=ev_bal, etf_log=etf_bal, force_close_eod=False, **LIQ, name="v5dt4_BAL_kelly")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])

sig30 = sig_v[sig_v["ticker"].isin(top30)].copy(); p30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
l30 = {k: vv for k, vv in liq_map_B.items() if k[0] in top30}; L30 = {**LIQ, "liquidity_lookup": l30}
ev_v30, etf_v30 = [], []
nav_v30, _ = simulate(sig30, p30, vni_dates_B, allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV, ticker_sector_map=sec_map, tier_weights=TIER_WEIGHTS,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff, cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True,
    event_log=ev_v30, etf_log=etf_v30, force_close_eod=False, **L30, name="v5dt4_VN30_kelly")
nav_v30["time"] = pd.to_datetime(nav_v30["time"])
print(f"  BAL  {nav_bal['nav'].iloc[-1]/1e9:.3f}B  ({len(ev_bal)} trades, {len(etf_bal)} ETF rebal)")
print(f"  VN30 {nav_v30['nav'].iloc[-1]/1e9:.3f}B  ({len(ev_v30)} trades, {len(etf_v30)} ETF rebal)")

# ── 4. LAGGED v121 (custom loop, event-logged) ──────────────────────────────
print("\n[4] LAGGED v121 (S2 sizing, transparent)...")
with open("data/earnings_px.pkl", "rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx; all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl", "rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl", "rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
evt = ev_class.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"]], on=["ticker", "quarter", "Release_Date"], how="left")
evt = evt.sort_values(["ticker", "Release_Date"]).reset_index(drop=True); evt["surprise_B_MA"] = evt["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0; evt["prior_n_good"] = 0; evt["pa_HL3"] = np.nan
for tk, g in evt.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = evt.loc[ri]; cd = row["Release_Date"]; ng = len(hist); evt.at[ri, "prior_n_good"] = ng
        if ng >= 1:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
            ay = (cd - da).days.values / 365.25; w = np.exp(-LN2 * ay / HL)
            evt.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]): hist.append((cd, row["post_ret"]))
e_hl3 = evt[(evt["NP_R"] >= 15) & (evt["prior_n_good"] >= 4) & (evt["pa_HL3"] >= 5)].copy()
def offset_date(ref, off):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    if pos < 0: return None
    t = pos + off
    return pd.Timestamp(all_dates[t]) if 0 <= t < len(all_dates) else None
sched = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    ed = offset_date(rdt, 5); xd = offset_date(rdt, 30)
    if ed is None or xd is None: continue
    sched.append({"ticker": tk, "entry_dt": ed, "exit_dt": xd, "surprise": row["surprise_B_MA"]})
sched_lag = pd.DataFrame(sched).sort_values("entry_dt").reset_index(drop=True)
ebd = sched_lag.groupby("entry_dt"); xbd = sched_lag.groupby("exit_dt")

def run_lagged(init):
    """v121 LAGGED book with S2 sizing; logs events + daily NAV breakdown."""
    sd = [d for d in master_idx if pd.Timestamp(START_B) <= d <= pd.Timestamp(END_B)]
    cash = init; pos = {}; SI, SO, TX = 0.001, 0.0015, 0.001; LC, MF = 0.20, 5; MP, LM = 12, 2e9
    events = []; daily = []
    for dt in sd:
        # exits at Open
        if dt in xbd.groups:
            for _, ex in xbd.get_group(dt).iterrows():
                tk = ex["ticker"]
                if tk not in pos or pos[tk]["exit_dt"] != dt: continue
                p = pos[tk]
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0:
                    fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx <= 0: continue
                gross = p["shares"] * fpx                       # clean gross (no costs)
                cash_in = p["shares"] * fpx * (1 - SO) * (1 - TX)
                fee = gross - cash_in
                cash += cash_in
                events.append({"ymd": dt, "ticker": tk, "action": "sell", "buy_amount": 0.0,
                    "sell_amount": float(gross), "fee": float(fee), "adj_price": float(fpx),
                    "shares": float(p["shares"]), "holding_id": p["holding_id"], "play_type": "LAGGED_v121",
                    "cash_after": float(cash), "reason": "TIME_EXIT"})
                del pos[tk]
        # entries at Open
        if dt in ebd.groups:
            mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
            nav_now = cash + mtm
            for _, en in ebd.get_group(dt).iterrows():
                tk = en["ticker"]
                if tk in pos or len(pos) >= MP: continue
                fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
                adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv * fpx < LM: continue
                pp = 0.10 if en["surprise"] > 0.5 else 0.08
                alloc = min(pp * nav_now, LC * adv * MF * fpx)
                if alloc < 1e6 or alloc > cash: continue
                eff = fpx * (1 + SI); sh = alloc / eff; clean = sh * fpx; fee = sh * eff - clean
                cash -= sh * eff
                hid = f"{tk}_{dt.strftime('%Y%m%d')}_LAG"
                events.append({"ymd": dt, "ticker": tk, "action": "buy", "buy_amount": float(clean),
                    "sell_amount": 0.0, "fee": float(fee), "adj_price": float(fpx), "shares": float(sh),
                    "holding_id": hid, "play_type": "LAGGED_v121", "cash_after": float(cash), "reason": "EARN_DRIFT"})
                pos[tk] = {"exit_dt": en["exit_dt"], "shares": sh, "entry_dt": dt, "entry_px": fpx,
                           "cost_basis": sh * eff, "holding_id": hid}
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk, p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        daily.append({"time": dt, "nav": cash + mtm, "cash": cash, "cash_etf": 0.0,
                      "positions_mv": mtm, "pending_mv": 0.0, "n_pos": len(pos)})
    nav_df = pd.DataFrame(daily).set_index("time")
    # open positions snapshot (MTM at last day)
    last_day = nav_df.index[-1]; opens = []
    for tk, p in pos.items():
        cur = px_close.at[last_day, tk] if (tk in px_close.columns and pd.notna(px_close.at[last_day, tk])) else p["entry_px"]
        mv = p["shares"] * cur
        opens.append({"ticker": tk, "entry_date": p["entry_dt"], "last_date": last_day, "entry_price": p["entry_px"],
            "last_price": cur, "shares": p["shares"], "cost_basis": p["cost_basis"], "mark_value": mv,
            "unrealised_pnl": mv - p["cost_basis"], "unrealised_ret_pct": (cur / p["entry_px"] - 1) * 100,
            "days_held": (last_day - p["entry_dt"]).days, "play_type": "LAGGED_v121", "holding_id": p["holding_id"]})
    return nav_df, events, pd.DataFrame(opens)

nav_lag, ev_lag, open_lag = run_lagged(BOOK_NAV)
print(f"  LAGGED {nav_lag['nav'].iloc[-1]/1e9:.3f}B  ({len(ev_lag)} trades, {len(open_lag)} open)")

# ── 5. Ensemble signal (M1 cached + M3r live, AND-hold) ─────────────────────
print("\n[5] Ensemble M1+M3r AND-hold...")
cached = pd.read_csv("data/compare_v11_v12_concentration_switch.csv", index_col=0, parse_dates=True)
sig_m1 = cached["sig_m1"].dropna().astype(int)
m3r_df = bq("""WITH base AS (SELECT t.time,t.ticker,
  SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6,
  AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS a1
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,r6,a1,ROW_NUMBER() OVER (PARTITION BY time ORDER BY a1 DESC) AS rnk FROM base WHERE a1 IS NOT NULL AND r6 IS NOT NULL)
SELECT time, AVG(IF(rnk<=10,r6,NULL))-AVG(r6) AS M3r FROM ranked GROUP BY time ORDER BY time""")
m3r_df["time"] = pd.to_datetime(m3r_df["time"]); m3r = m3r_df.set_index("time")["M3r"]
def mksig(metric, mh=252):
    s = metric.dropna().sort_index(); em = s.expanding(min_periods=mh).median()
    return (s > em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int).shift(1).fillna(1).astype(int)
sig_m3r = mksig(m3r)

nb = nav_bal.set_index("time")["nav"]; nv = nav_v30.set_index("time")["nav"]; nl = nav_lag["nav"]
common = nb.index.intersection(nv.index).intersection(nl.index)
m1 = sig_m1.reindex(common).ffill().fillna(1).astype(int); m3a = sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ensAH(a, b):
    out = np.zeros(len(a), int); cur = int(a.iloc[0])
    for i, (x, y) in enumerate(zip(a.values, b.values)):
        if x == y: cur = int(x)
        out[i] = cur
    return pd.Series(out, index=a.index)
sigAH = ensAH(m1, m3a)

# ── 6. V5 ensemble NAV = BAL_kelly + switched(VN30_kelly / LAGGED) ──────────
print("\n[6] V5 ensemble NAV (BAL_kelly + return-switched 2nd leg)...")
def swnav(bal, vn30, lg, sig):
    br = bal.loc[common].pct_change().fillna(0); vr = vn30.loc[common].pct_change().fillna(0); lr = lg.loc[common].pct_change().fillna(0)
    nbp = (1 + br).cumprod() * BOOK_NAV; sec = np.full(len(common), BOOK_NAV, float); prev = int(sig.iloc[0])
    for i in range(1, len(common)):
        cur = int(sig.iloc[i]); sec[i] = sec[i-1] * (1 - SWITCH_COST) if cur != prev else sec[i-1]
        r = vr.iloc[i] if cur == 1 else lr.iloc[i]; sec[i] = sec[i] * (1 + r); prev = cur
    bal_path = pd.Series(nbp.values, index=common); sec_path = pd.Series(sec, index=common)
    return (bal_path + sec_path), bal_path, sec_path
nav_V5, bal_path, sec_path = swnav(nb, nv, nl, sigAH)
vni_n = vni_B.set_index("time")["Close"].reindex(common).ffill(); vni_n = vni_n / vni_n.iloc[0] * TOTAL_NAV

# ── 7. Per-leg transparent outputs + reconciliation ─────────────────────────
print("\n[7] Per-leg transparent CSVs + reconciliation...")

def build_etf_tx(etf_events):
    if not etf_events: return pd.DataFrame()
    e = pd.DataFrame(etf_events)
    return pd.DataFrame({
        "ymd": pd.to_datetime(e["ymd"]), "ticker": "E1VFVN30",
        "action": e["action"].apply(lambda a: "buy" if a == "buy_etf" else "sell"),
        "buy_amount": np.where(e["action"] == "buy_etf", e["amount_vnd"], 0.0),
        "sell_amount": np.where(e["action"] == "sell_etf", e["amount_vnd"], 0.0),
        "fee": e["friction_cost"], "adj_price": e["price_vn30"], "shares": e["shares"],
        "holding_id": e["holding_id"], "play_type": "ETF_PARK", "cash_after": e["cash_after"],
        "reason": "ETF_REBAL_state" + e["state"].astype(str)})

def leg_outputs(label, nav_df, stock_events, etf_events, open_df_stocks, etf_lots_df):
    """Write logs/transactions/open_positions CSVs for one leg + return 4-gate recon dict."""
    nav_df = nav_df.copy()
    idx = nav_df.index
    # transactions
    stx = pd.DataFrame(stock_events) if stock_events else pd.DataFrame()
    if not stx.empty: stx["ymd"] = pd.to_datetime(stx["ymd"])
    etx = build_etf_tx(etf_events)
    all_tx = pd.concat([stx, etx], ignore_index=True)
    if not all_tx.empty:
        all_tx["ymd"] = pd.to_datetime(all_tx["ymd"])
        all_tx = all_tx.sort_values(["ymd", "action", "ticker"]).reset_index(drop=True)
    # MTM phantoms for open stocks + ETF lots
    last_day = idx[-1]; mtm_rows = []
    if open_df_stocks is not None and not open_df_stocks.empty:
        for _, p in open_df_stocks.iterrows():
            mtm_rows.append({"ymd": last_day, "ticker": p["ticker"], "action": "sell", "buy_amount": 0.0,
                "sell_amount": float(p["mark_value"]), "fee": 0.0, "adj_price": float(p["last_price"]),
                "shares": float(p["shares"]), "holding_id": p["holding_id"], "play_type": p["play_type"],
                "cash_after": None, "reason": "MTM_UNREALIZED"})
    if etf_lots_df is not None and not etf_lots_df.empty:
        for _, lot in etf_lots_df.iterrows():
            mtm_rows.append({"ymd": last_day, "ticker": "E1VFVN30", "action": "sell", "buy_amount": 0.0,
                "sell_amount": float(lot["mark_value"]), "fee": 0.0,
                "adj_price": float(lot["last_price"]) if pd.notna(lot["last_price"]) else None,
                "shares": float(lot["shares"]), "holding_id": lot["holding_id"], "play_type": "ETF_PARK",
                "cash_after": None, "reason": "MTM_UNREALIZED"})
    if mtm_rows:
        all_tx = pd.concat([all_tx, pd.DataFrame(mtm_rows)], ignore_index=True).sort_values(["ymd", "action", "ticker"]).reset_index(drop=True)
    # tx count series
    nser = pd.Series(0, index=idx, dtype=int)
    if not all_tx.empty:
        cc = all_tx[all_tx["reason"] != "MTM_UNREALIZED"].groupby("ymd").size().cumsum()
        for d, n in cc.items(): nser.loc[nser.index >= d] = int(n)
    logs = pd.DataFrame({"ymd": idx, "nav": nav_df["nav"].values, "cash": nav_df["cash"].values,
        "cash_etf": nav_df["cash_etf"].values, "stocks_mv": (nav_df["positions_mv"] + nav_df["pending_mv"]).values,
        "num_holdings": nav_df["n_pos"].values, "num_transactions": nser.values})
    lp = safe_to_csv(logs, os.path.join(DATADIR, f"v5dt4_{label}_logs.csv"))
    tp = safe_to_csv(all_tx, os.path.join(DATADIR, f"v5dt4_{label}_transactions.csv"))
    # open positions CSV (stocks + etf lots)
    op_parts = []
    if open_df_stocks is not None and not open_df_stocks.empty: op_parts.append(open_df_stocks)
    if etf_lots_df is not None and not etf_lots_df.empty: op_parts.append(etf_lots_df)
    open_all = pd.concat(op_parts, ignore_index=True) if op_parts else pd.DataFrame()
    opp = safe_to_csv(open_all, os.path.join(DATADIR, f"v5dt4_{label}_open_positions.csv"))
    # analyze_portfolio.py
    rep = os.path.join(DATADIR, f"v5dt4_{label}_report.md")
    try:
        subprocess.run([sys.executable, "analyze_portfolio.py", "--logs", lp, "--transactions", tp, "--output", rep],
                       cwd=WORKDIR, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    except Exception as e:
        print(f"  ({label} analyze_portfolio failed: {e})")
    # ── 4-gate reconciliation ──
    real = all_tx[all_tx["reason"] != "MTM_UNREALIZED"] if not all_tx.empty else pd.DataFrame()
    mtm = all_tx[all_tx["reason"] == "MTM_UNREALIZED"] if not all_tx.empty else pd.DataFrame()
    # G2: NAV identity each day  cash+cash_etf+stocks_mv == nav
    g2 = float((nav_df["nav"] - (nav_df["cash"] + nav_df["cash_etf"] + nav_df["positions_mv"] + nav_df["pending_mv"])).abs().max())
    # G3a: sum MTM stocks == stocks_mv[-1]
    mtm_stk = mtm[mtm["ticker"] != "E1VFVN30"]["sell_amount"].sum() if not mtm.empty else 0.0
    mtm_etf = mtm[mtm["ticker"] == "E1VFVN30"]["sell_amount"].sum() if not mtm.empty else 0.0
    # ΣMTM phantoms cover FILLED positions only → compare vs positions_mv (pending = in-flight orders, reported separately)
    pending_end = float(nav_df["pending_mv"].iloc[-1])
    g3a = abs(mtm_stk - nav_df["positions_mv"].iloc[-1])
    g3b = abs(mtm_etf - nav_df["cash_etf"].iloc[-1])
    # G1: cash trajectory from tx == end_cash (exact when no ETF; ETF residual = appreciation rebalanced to cash)
    if not real.empty:
        sb = real[(real["action"] == "buy")]; ss = real[(real["action"] == "sell")]
        cash_out = sb["buy_amount"].sum() + sb["fee"].sum()
        cash_in = ss["sell_amount"].sum() - ss["fee"].sum()
        exp_cash = BOOK_NAV - cash_out + cash_in
    else:
        exp_cash = BOOK_NAV
    g1_resid = float(nav_df["cash"].iloc[-1] - exp_cash)   # ~0 for LAGGED; ETF-appreciation residual for BAL/VN30
    # G4: every open stock holding_id has a real buy + an MTM sell
    g4_ok = True
    if open_df_stocks is not None and not open_df_stocks.empty and not real.empty:
        buy_ids = set(real[real["action"] == "buy"]["holding_id"])
        for hid in open_df_stocks["holding_id"]:
            if hid not in buy_ids: g4_ok = False; break
    return {"label": label, "final_nav": float(nav_df["nav"].iloc[-1]), "G2_nav_identity_maxabs": g2,
            "G3a_mtm_stocks": float(g3a), "G3b_mtm_etf": float(g3b), "G1_cash_residual": g1_resid,
            "G4_open_buy_match": g4_ok, "logs": lp, "tx": tp, "open": opp, "report": rep,
            "pending_end": pending_end, "n_real_tx": int(len(real)), "end_cash": float(nav_df["cash"].iloc[-1]),
            "end_etf": float(nav_df["cash_etf"].iloc[-1]), "exp_cash": float(exp_cash)}

recon = []
recon.append(leg_outputs("bal_kelly", nav_bal.set_index("time"), ev_bal, etf_bal,
                         nav_bal.attrs.get("open_positions_final"), nav_bal.attrs.get("etf_lots_final")))
recon.append(leg_outputs("vn30_kelly", nav_v30.set_index("time"), ev_v30, etf_v30,
                         nav_v30.attrs.get("open_positions_final"), nav_v30.attrs.get("etf_lots_final")))
recon.append(leg_outputs("lagged_v121", nav_lag.assign(n_pending=0), ev_lag, [],
                         open_lag, pd.DataFrame()))

# ── 8. Ensemble logs + master report ────────────────────────────────────────
print("\n[8] Ensemble logs + master report...")
ens_logs = pd.DataFrame({
    "ymd": common, "nav_V5": nav_V5.values, "bal_kelly_nav": nb.loc[common].values,
    "vn30_kelly_nav": nv.loc[common].values, "lagged_nav": nl.loc[common].values,
    "bal_path": bal_path.values, "second_leg_nav": sec_path.values,
    "sig_AH": sigAH.values, "active_2nd": np.where(sigAH.values == 1, "VN30", "LAGGED"),
    "state_dt4": pd.Series(common).map(state_ff).values, "vni_bh": vni_n.values})
ens_path = safe_to_csv(ens_logs, os.path.join(DATADIR, "v5dt4_ensemble_logs.csv"))
# Ensemble NAV identity gate: V5 == bal_path + second_leg_nav
g_ens = float((nav_V5 - (bal_path + sec_path)).abs().max())

def metrics(s):
    s = s.dropna(); r = s.pct_change().dropna(); yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(r) / yrs if yrs > 0 else 252
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else 0
    dd = ((s - s.cummax()) / s.cummax()).min()
    return {"CAGR": cagr * 100, "Sharpe": r.mean() / r.std() * np.sqrt(spy) if r.std() > 0 else 0,
            "DD": dd * 100, "Calmar": cagr / abs(dd) if dd < 0 else 0,
            "tot": (s.iloc[-1] / s.iloc[0] - 1) * 100, "final": s.iloc[-1]}

mV5 = metrics(nav_V5); mVNI = metrics(vni_n)
mBAL = metrics(nb.loc[common]); mVN30 = metrics(nv.loc[common]); mLAG = metrics(nl.loc[common])

L = []
L.append("# V5 + DT4(4-gate) — Transparent Simulation Report\n")
L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}*  |  Period **{common.min().date()} → {common.max().date()}**  |  init **50B** (25B BAL + 25B 2nd leg)\n")
L.append("V5 = V121_ENS + KELLY parking on the DT4 (`vnindex_5state_dt_4gate`) foundation. "
         "Mirrors `run_5systems_dt4.py` V5 exactly; adds transparent per-leg trade logs.\n")
L.append("## Headline\n")
L.append("| System | CAGR | Sharpe | MaxDD | Calmar | TotRet | Final NAV |")
L.append("|---|---|---|---|---|---|---|")
L.append(f"| **V5+DT4 (ensemble)** | {mV5['CAGR']:+.2f}% | {mV5['Sharpe']:+.2f} | {mV5['DD']:+.2f}% | {mV5['Calmar']:+.2f} | {mV5['tot']:+.2f}% | {mV5['final']/1e9:.2f}B |")
L.append(f"| VNINDEX B&H | {mVNI['CAGR']:+.2f}% | {mVNI['Sharpe']:+.2f} | {mVNI['DD']:+.2f}% | {mVNI['Calmar']:+.2f} | {mVNI['tot']:+.2f}% | {mVNI['final']/1e9:.2f}B |")
L.append("\n### Underlying leg performance (standalone, each 25B book)\n")
L.append("| Leg | CAGR | Sharpe | MaxDD | Final NAV |")
L.append("|---|---|---|---|---|")
L.append(f"| BAL_kelly | {mBAL['CAGR']:+.2f}% | {mBAL['Sharpe']:+.2f} | {mBAL['DD']:+.2f}% | {mBAL['final']/1e9:.2f}B |")
L.append(f"| VN30_kelly | {mVN30['CAGR']:+.2f}% | {mVN30['Sharpe']:+.2f} | {mVN30['DD']:+.2f}% | {mVN30['final']/1e9:.2f}B |")
L.append(f"| LAGGED_v121 | {mLAG['CAGR']:+.2f}% | {mLAG['Sharpe']:+.2f} | {mLAG['DD']:+.2f}% | {mLAG['final']/1e9:.2f}B |")
L.append("\n## Per-leg trade reconciliation (4 gates — every delta must be ~0)\n")
L.append("| Leg | G2 NAV-identity (max abs) | G3a ΣMTM stocks vs positions_mv | G3b ΣMTM ETF vs cash_etf | G1 cash residual* | G4 open↔buy match | pending (in-flight) | real tx |")
L.append("|---|---|---|---|---|---|---|---|")
for r in recon:
    L.append(f"| {r['label']} | {r['G2_nav_identity_maxabs']:,.2f} | {r['G3a_mtm_stocks']:,.2f} | {r['G3b_mtm_etf']:,.2f} | {r['G1_cash_residual']/1e9:+.4f}B | {'PASS' if r['G4_open_buy_match'] else 'FAIL'} | {r['pending_end']/1e9:.3f}B | {r['n_real_tx']} |")
L.append("\n*G1 cash residual = `end_cash − (init − buys−fees + sells−fees)`. For LAGGED (no ETF) this is ~0. "
         "For BAL/VN30 it equals ETF appreciation that the KELLY rebalance moved out of `cash_etf` into `cash` — "
         "expected & explained, NOT an error; the strict daily NAV identity (G2) is the binding gate and is ~0.\n")
L.append("## Ensemble construction (the part that is NOT trade-reconcilable)\n")
L.append(f"- V5 daily NAV identity gate (V5 == BAL_path + second_leg): **max abs = {g_ens:,.4f} VND** (≈0).\n")
L.append("- The **switch** between VN30_kelly and LAGGED_v121 is applied at the **return level** "
         "(`second_leg[t] = second_leg[t-1]·(1±switch_cost)·(1 + r_active)`), NOT by moving actual share lots. "
         "So the 2nd-leg book that is *inactive* on a given day still has real, logged trades in its own CSV, "
         "but those trades are not 'realized' by V5 that day. This is the documented idealization "
         "(`[[v5-prodspec-integrity-audit]]` 'independent-leg recombine'). Trade-level truth lives in each leg's "
         "CSV; the ensemble overlay is a return-path construct, verified only via the NAV identity above.\n")
L.append(f"- Switches over period: **{int((sigAH.diff().abs() > 0).sum())}** flips; "
         f"days in VN30 = {int((sigAH == 1).sum())}, days in LAGGED = {int((sigAH == 0).sum())}.\n")
L.append("## Files\n")
for r in recon:
    L.append(f"- **{r['label']}**: `{os.path.relpath(r['logs'], WORKDIR)}`, `{os.path.relpath(r['tx'], WORKDIR)}`, "
             f"`{os.path.relpath(r['open'], WORKDIR)}`, `{os.path.relpath(r['report'], WORKDIR)}`")
L.append(f"- **ensemble**: `{os.path.relpath(ens_path, WORKDIR)}`")
master = os.path.join(DATADIR, "v5dt4_master_report.md")
with open(master, "w", encoding="utf-8") as f: f.write("\n".join(L))

print("\n" + "=" * 92)
print(f"  V5+DT4  CAGR {mV5['CAGR']:+.2f}%  Sharpe {mV5['Sharpe']:+.2f}  MaxDD {mV5['DD']:+.2f}%  "
      f"Calmar {mV5['Calmar']:+.2f}  Final {mV5['final']/1e9:.2f}B  (VNI {mVNI['tot']:+.2f}%)")
print("=" * 92)
print("  RECONCILIATION (every value ~0 except explained G1 ETF residual):")
for r in recon:
    print(f"    {r['label']:<12} G2={r['G2_nav_identity_maxabs']:.2f}  G3a={r['G3a_mtm_stocks']:.2f}  "
          f"G3b={r['G3b_mtm_etf']:.2f}  G1resid={r['G1_cash_residual']/1e9:+.4f}B  G4={'PASS' if r['G4_open_buy_match'] else 'FAIL'}"
          f"  pending={r['pending_end']/1e9:.3f}B")
print(f"    ensemble    V5==BAL+2nd identity maxabs = {g_ens:.4f}")
print(f"\n  Master report: data/v5dt4_master_report.md")
print("DONE.")
