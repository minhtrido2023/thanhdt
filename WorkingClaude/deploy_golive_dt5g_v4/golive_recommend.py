# -*- coding: utf-8 -*-
"""
golive_recommend.py  —  LAYER 2: V4 + DT5G daily order/position recommender.

Consumes the gated DT5G state (published by publish_gated_state.py to BQ
tav2_bq.vnindex_5state_dt5g_live) and the live SIGNAL_V11, then emits TODAY's
actionable recommendations for the V4 system (V121_ENS + BASE parking {3:0.7}):

  • Market regime (gated state5 today) + ETF parking target (BASE)
  • Ensemble mode today  -> which 2nd-leg book is active (VN30 vs LAGGED)
  • BAL book   (always-on 50%): ranked BA-core picks, max 12 pos, 10%/pos, Fin/RE cap 4
  • 2nd leg 50%: VN30 book picks (if VN30-mode) OR LAGGED earnings-drift entries due today
  • Fail-safe: state source = whatever publish_gated_state chose (DT5G or DT4) — read from json

Output: deploy_golive_dt5g_v4/out/golive_recommendations_<DATE>.{md,csv}

This is a point-in-time ("today") snapshot of the SAME signal+filter+ensemble logic
validated in run_5systems_dt4.py — NOT a NAV backtest. It tells the desk what to hold/
buy/sell today; position sizing is 10% NAV/slot (BASE), ETF parks idle cash in NEUTRAL.
"""
import os, sys, io, re, json, pickle
from datetime import datetime, timedelta
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

OUTDIR = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out"); os.makedirs(OUTDIR, exist_ok=True)
DT_TABLE = "vnindex_5state_dt5g_live"     # gated DT5G series published by Layer 1
END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")  # recent window for "today"
MAX_POS = 12; POS_PCT = 0.10
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
             "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
PRIORITY = {t: i for i, t in enumerate(TIER_BAL)}     # lower = higher priority
ETF_BASE = {3: 0.7}                                   # V4 BASE parking: 70% idle cash to ETF in NEUTRAL
SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

print("=" * 90); print(f"  V4 + DT5G — DAILY RECOMMENDATIONS  ({END})"); print("=" * 90)

# ── provenance: which state source did the gate pick? ──
prov = {}
try:
    prov = json.load(open(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json"), encoding="utf-8"))
    print(f"  state source: {prov.get('source')} | as_of {prov.get('as_of')} | state {prov.get('state')} ({SNAME.get(prov.get('state'),'?')})")
except Exception as e:
    print(f"  WARNING: golive_state_today.json missing ({e}); run publish_gated_state.py first")

# ── 1. signals with state5 from the gated DT5G series ──
SIG = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", "tav2_bq." + DT_TABLE + " AS s")
sig = bq(SIG.format(start=START, end=END)); sig["time"] = pd.to_datetime(sig["time"])
LATEST = sig["time"].max()
state_today = int(sig.loc[sig["time"] == LATEST, "state5"].dropna().iloc[0]) if (sig["time"] == LATEST).any() else int(prov.get("state", 3))
print(f"  latest signal date: {LATEST.date()} | {len(sig):,} signal rows in window")

# ── 2. D1 RE_BACKLOG (gated state) + SV_TIGHT + overheat (same logic as run_5systems_dt4) ──
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f),
tkd AS (
  -- ICB-8633 panel: canonical ticker + ticker_1m fallback for the freshest session not yet
  -- in `ticker` (ticker ingests ~22:30 VN; ticker_1m is intraday-fresh). Additive/safe: adds
  -- rows only for dates ticker lacks → a no-op when ticker is already current (e.g. 15:30 run).
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  UNION ALL
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker_1m AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND NOT EXISTS (SELECT 1 FROM tav2_bq.ticker AS x WHERE x.ticker=t.ticker AND x.time=t.time AND x.ICB_Code IS NOT NULL))
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tkd AS t LEFT JOIN tav2_bq.{DT_TABLE} AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)""")
d1["time"] = pd.to_datetime(d1["time"])
d1m = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C", "D"]) & d1["state5"].isin([3,4,5]) & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
sig = sig.merge(d1.loc[d1m, ["ticker", "time"]].assign(_ok=True), on=["ticker", "time"], how="left")
om = sig["_ok"].fillna(False) & (sig["ta"] >= 120); sig.loc[om, "play_type"] = "RE_BACKLOG_BUY"; sig = sig.drop(columns=["_ok"])

def svk(r):
    s = r.get("state5"); d = r.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True
    if s == 1: return pd.notna(d) and d <= 30
    if s in (2, 3): return pd.notna(d) and d <= 60
    return True
mb = sig["play_type"].isin(BUY_TIERS); sig = sig[(~mb) | sig.apply(svk, axis=1)].copy()
# overheat on latest date (VNINDEX is NOT in ticker_1m → can't de-lag; the 1-day lag on this
# slow regime gate (ratio>1.30 AND state==5/RSI>0.75) is immaterial)
vni = bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}'")
vni["time"] = pd.to_datetime(vni["time"])
st = bq(f"SELECT s.time,s.state FROM tav2_bq.{DT_TABLE} AS s WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}'"); st["time"] = pd.to_datetime(st["time"])
v = vni.merge(st, on="time", how="left"); v["state"] = v["state"].ffill()
oh = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["state"] == 5) | (v["D_RSI"] > 0.75))]["time"])
sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

# ── 3. today's eligible BA-core signals ──
today = sig[(sig["time"] == LATEST) & sig["play_type"].isin(TIER_BAL)].copy()
sec_map = bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
today["sec"] = today["ticker"].map(sec_map)
today["prio"] = today["play_type"].map(PRIORITY)
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])

def select_book(cand, universe=None):
    c = cand if universe is None else cand[cand["ticker"].isin(universe)]
    c = c.sort_values(["prio", "ta"], ascending=[True, False])
    picked, fin_re = [], 0
    for _, r in c.iterrows():
        if len(picked) >= MAX_POS: break
        is_finre = (r["sec"] == 8)
        exempt = (r["play_type"] == "RE_BACKLOG_BUY")
        if is_finre and not exempt and fin_re >= 4: continue
        picked.append(r)
        if is_finre and not exempt: fin_re += 1
    return pd.DataFrame(picked)

bal = select_book(today)
vn30 = select_book(today, universe=top30)

# ── 4. ensemble mode today (M1 cached + M3r live, AND-hold) → which 2nd leg ──
mode_today, mode_label = 1, "VN30 (V11-mode)"
try:
    cached = pd.read_csv(os.path.join(WORKDIR, "compare_v11_v12_concentration_switch.csv"), index_col=0, parse_dates=True)
    sig_m1 = cached["sig_m1"].dropna().astype(int)
    m3 = bq(f"""WITH base AS (SELECT t.time,t.ticker,
      SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6,
      AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS a1
      FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{END}'
      AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
    ranked AS (SELECT time,r6,a1,ROW_NUMBER() OVER (PARTITION BY time ORDER BY a1 DESC) AS rnk FROM base WHERE a1 IS NOT NULL AND r6 IS NOT NULL)
    SELECT time, AVG(IF(rnk<=10,r6,NULL))-AVG(r6) AS M3r FROM ranked GROUP BY time ORDER BY time""")
    m3["time"] = pd.to_datetime(m3["time"]); m3r = m3.set_index("time")["M3r"]
    em = m3r.dropna().sort_index().expanding(min_periods=252).median()
    sig_m3r = (m3r.dropna().sort_index() > em).astype(int).reindex(m3r.index).ffill().fillna(1).astype(int).shift(1).fillna(1).astype(int)
    idx = sig_m3r.index
    m1 = sig_m1.reindex(idx).ffill().fillna(1).astype(int)
    cur = int(m1.iloc[0])
    for a, b in zip(m1.values, sig_m3r.values):
        if a == b: cur = int(a)
    mode_today = cur
    mode_label = "VN30 (V11-mode)" if cur == 1 else "LAGGED earnings-drift (V12-mode)"
except Exception as e:
    print(f"  WARNING: ensemble mode fallback to VN30 ({e})")

# ── 5. LAGGED entries due today (only relevant if LAGGED-mode) ──
lagged_due = []
try:
    with open(os.path.join(WORKDIR, "earnings_events_classified.csv")) as _f: pass
    ev = pd.read_csv(os.path.join(WORKDIR, "earnings_events_classified.csv"), parse_dates=["Release_Date"])
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    LN2 = np.log(2); HL = 3.0; ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
    for tk, g in ev.groupby("ticker"):
        hist = []
        for ri in g.index.tolist():
            row = ev.loc[ri]; cd = row["Release_Date"]; ng = len(hist); ev.at[ri, "prior_n_good"] = ng
            if ng >= 1:
                da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
                ay = (cd - da).days.values / 365.25; w = np.exp(-LN2 * ay / HL)
                ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]): hist.append((cd, row["post_ret"]))
    cand = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
    # entry = Release_Date + 5 trading days; due within the last 1 trading day up to today
    cand["entry_approx"] = cand["Release_Date"] + pd.Timedelta(days=7)   # ~5 trading days
    due = cand[(cand["entry_approx"] >= LATEST - pd.Timedelta(days=3)) & (cand["entry_approx"] <= LATEST + pd.Timedelta(days=1))]
    lagged_due = sorted(due["ticker"].unique().tolist())
except Exception as e:
    print(f"  WARNING: LAGGED schedule unavailable ({e})")

# ── 6. ETF parking (BASE) ──
etf_frac = ETF_BASE.get(state_today, 0.0)

# ── 7. emit recommendations ──
def book_rows(df, book):
    rows = []
    for _, r in df.iterrows():
        rows.append({"book": book, "ticker": r["ticker"], "play_type": r["play_type"],
                     "ta": round(float(r["ta"]), 0), "close": round(float(r["Close"]), 1),
                     "sector": int(r["sec"]) if pd.notna(r["sec"]) else None, "weight_pct": POS_PCT*100})
    return rows

active_second = "VN30" if mode_today == 1 else "LAGGED"
recs = book_rows(bal, "BAL(50%)")
if mode_today == 1:
    recs += book_rows(vn30, "VN30(50%)")
else:
    # LAGGED-mode: emit the earnings-drift entries due today into the CSV too (consumed by daily report)
    for tk in lagged_due:
        recs.append({"book": "LAGGED(50%)", "ticker": tk, "play_type": "LAGGED_DRIFT",
                     "ta": None, "close": None, "sector": sec_map.get(tk), "weight_pct": POS_PCT*100})
rec_df = pd.DataFrame(recs)
csv_path = os.path.join(OUTDIR, f"golive_recommendations_{END}.csv")
rec_df.to_csv(csv_path, index=False)

L = []
L.append(f"# V4 + DT5G — Daily Recommendations — {END}\n")
L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}. System: V121_ENS + BASE parking, gated DT5G state (fail-safe DT4). Sizing 10% NAV/slot, max {MAX_POS}, hold 45d, stop -20%.*\n")
L.append("## Regime & parking\n")
L.append(f"- **Market state (gated):** {state_today} = **{SNAME.get(state_today,'?')}**  (source: {prov.get('source','?')}; DT4 base={prov.get('base_state_dt4','?')}, DT5G={prov.get('macro_state_dt5g','?')})")
L.append(f"- **ETF parking target (BASE):** park **{etf_frac*100:.0f}%** of idle cash in E1VFVN30" + (" (NEUTRAL)" if state_today == 3 else ""))
if state_today in (1, 2):
    L.append(f"- ⚠️ **{SNAME[state_today]}** — BA-core entries blocked (AVOID_bear); de-risk / hold cash.")
L.append(f"- **Ensemble mode today:** {mode_label} → 2nd-leg book = **{active_second}**\n")
L.append(f"## BAL book (always-on 50%) — {len(bal)} picks\n")
if len(bal):
    L.append("| ticker | tier | ta | close | sector | weight |")
    L.append("|---|---|---:|---:|---:|---:|")
    for _, r in bal.iterrows():
        L.append(f"| {r['ticker']} | {r['play_type']} | {float(r['ta']):.0f} | {float(r['Close']):.1f} | {int(r['sec']) if pd.notna(r['sec']) else '-'} | {POS_PCT*100:.0f}% |")
else:
    L.append("_No new BA-core entries today_ — in this regime there are no qualifying signals in V4's "
             "BAL tiers (MEGA/MOMENTUM*/DEEP_VALUE_RECOVERY/RE_BACKLOG). **Action: hold existing positions "
             "(45d) and park idle cash per the parking target above.** This is normal conservative behavior "
             "in NEUTRAL, not an error.")
# informational: buy-ish signals that exist today but are OUTSIDE V4's BAL tiers
_latest = sig[sig["time"] == LATEST]
_info = _latest[_latest["play_type"].isin(["COMPOUNDER_BUY", "S_PRO", "MOMENTUM_QUALITY", "MOMENTUM_S_N"])]
if len(_info):
    L.append(f"\n_Informational (signals today OUTSIDE V4 BAL tiers, not traded by V4):_ " +
             ", ".join(f"{r['ticker']}({r['play_type']})" for _, r in _info.head(12).iterrows()))
L.append("")
if mode_today == 1:
    L.append(f"## 2nd leg = VN30 book (50%) — {len(vn30)} picks\n")
    if len(vn30):
        L.append("| ticker | tier | ta | close | sector | weight |")
        L.append("|---|---|---:|---:|---:|---:|")
        for _, r in vn30.iterrows():
            L.append(f"| {r['ticker']} | {r['play_type']} | {float(r['ta']):.0f} | {float(r['Close']):.1f} | {int(r['sec']) if pd.notna(r['sec']) else '-'} | {POS_PCT*100:.0f}% |")
    else:
        L.append("_(no eligible VN30 signals today)_")
else:
    L.append("## 2nd leg = LAGGED earnings-drift (50%)\n")
    L.append("Ensemble is in V12/LAGGED mode → 2nd-leg capital follows the earnings-drift book "
             "(buy T+5 after strong earnings, hold ~25 trading days). Entries due ~now:\n")
    L.append("- " + (", ".join(lagged_due) if lagged_due else "_(no LAGGED entries due in the last few sessions)_"))
L.append(f"\n## Notes\n- Position sizing: {POS_PCT*100:.0f}% NAV per slot, BASE parking keeps ~30% cash buffer in NEUTRAL.")
L.append(f"- Fin/RE (sector 8) capped at 4 positions per book (RE_BACKLOG_BUY exempt).")
L.append(f"- This is the V4 (BASE) config. State is the fail-safe gated series; if macro feeds were unhealthy the source would read 'DT4_only'.")
L.append(f"- CSV: `out/golive_recommendations_{END}.csv`")
md_path = os.path.join(OUTDIR, f"golive_recommendations_{END}.md")
open(md_path, "w", encoding="utf-8").write("\n".join(L))

print(f"\n  state={state_today}({SNAME.get(state_today,'?')})  parking={etf_frac*100:.0f}%  ensemble={mode_label}")
print(f"  BAL picks: {len(bal)} | 2nd leg: {active_second} ({len(vn30) if mode_today==1 else len(lagged_due)} items)")
print(f"  -> {md_path}")
print(f"  -> {csv_path}")
print("DONE.")
