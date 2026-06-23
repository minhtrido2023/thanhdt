# -*- coding: utf-8 -*-
"""
golive_recommend_v23.py  —  LAYER 2: V2.3 + DT5G daily order/position recommender.

V2.3 = V2.2 (BAL | LAG static, always-on, NO ensemble switch) + parking {3:0.7}
on BOTH books + state-conditional LAG/BAL allocator + CAPIT v2 sleeves.
This is the PRODUCTION recommender (replaces the V4 golive_recommend.py picks
in the 18:00 report as of 2026-06-12; V4 stays as a paper-trade benchmark).

Consumes the gated DT5G state (publish_gated_state.py -> BQ
tav2_bq.vnindex_5state_dt5g_live) and emits TODAY's actionable recommendations:

  • Market regime (gated state5) + ETF parking target {NEUTRAL: 70%} (both books)
  • Allocator: w_LAG target by state {CRISIS .50 / BEAR 0 / NEU·BULL·EXBULL .65},
    BAND-only rebalance trigger ±10pp vs current w_LAG (read from pt_v22 logs)
  • BAL book: ranked BA-core picks (SIGNAL_V11 + D1 + SV_TIGHT + overheat
    + AVOID_exbull + regime_size weak-half), max 12, 10%/pos of BAL book
  • LAG book (always-on): PEAD entries due next sessions (NP_R>=15 &
    prior_n_good>=4 & pa_HL3>=5), T+5 entry, hold 25td, LAG_HI 10% / LAG_LO 8%
  • CAPIT v2 monitor: oversold breadth vs 30% gate; if fired -> state-routed
    size + grind x0.5 + BEAR guard (dd52w / VN rv10-cooling) + quality-golden basket

Output:
  deploy_golive_dt5g_v4/out/golive_v23_recommendations_<DATE>.{md,csv}
  data/golive_v23_status.json            (read by the 18:00 telegram report)

Point-in-time snapshot of the SAME logic as pt_v22_dt5g.py — NOT a NAV backtest.
"""
import os, sys, io, json, pickle
from datetime import datetime, timedelta
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

OUTDIR = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out"); os.makedirs(OUTDIR, exist_ok=True)
DT_TABLE = "vnindex_5state_dt5g_live"
END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")    # recent window for "today"
START_BR = (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d") # breadth window (grind lookback 90 sessions)
START_VNI = (datetime.now() - timedelta(days=420)).strftime("%Y-%m-%d")# dd52w/rv10 window

MAX_POS = 12; POS_PCT = 0.10; WEAK_PCT = 0.05
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
             "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
EXB_MOM = {"MEGA","MOMENTUM","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","S_PRO"}
PRIORITY = {t: i for i, t in enumerate(TIER_BAL)}
ETF_PARK = {3: 0.7}                                  # both books in V2.3
STATE_LAG_WEIGHT = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}
ALLOC_BAND = 0.10
LAG_TW = {"LAG_HI": 0.10, "LAG_LO": 0.08}
WASHOUT_GATE = 0.30; CAPIT_HOLD = 60
SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

def capit_base(state, dd52w, vn_cooling):
    if state == 1: return 1.0
    if state == 3: return 0.75
    if state in (4, 5): return 0.5
    if state == 2: return 0.5 if (dd52w > -25 or vn_cooling) else 0.0
    return 0.5

print("=" * 90); print(f"  V2.3 + DT5G — DAILY RECOMMENDATIONS  ({END})"); print("=" * 90)

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

# ── 2. D1 RE_BACKLOG (gated state) + SV_TIGHT + overheat (same layering as pt_v22_dt5g) ──
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f),
tkd AS (
  -- ICB-8633 panel: canonical ticker + ticker_1m fallback for the freshest session not yet in `ticker`
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
# overheat on latest dates (1-day lag on this slow gate is immaterial — see golive_recommend.py note)
vni = bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
st = bq(f"SELECT s.time,s.state FROM tav2_bq.{DT_TABLE} AS s WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}'"); st["time"] = pd.to_datetime(st["time"])
v = vni.merge(st, on="time", how="left"); v["state"] = v["state"].ffill()
oh = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["state"] == 5) | (v["D_RSI"] > 0.75))]["time"])
sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

# ── 2b. AVOID_exbull: suppress BAL momentum tiers in EX-BULL (live 2026-06-11, IC inverts in state 5) ──
mexb = (sig["state5"] == 5) & sig["play_type"].isin(EXB_MOM)
sig.loc[mexb, "play_type"] = "AVOID_exbull"
if int(mexb.sum()): print(f"  [EXBULL] suppressed {int(mexb.sum())} momentum signal rows in EX-BULL")

# ── 2c. regime_size weak flag: ABSOLUTE 8L rating >= 4 → half size ONLY in BEAR/CRISIS ──
r8 = bq(f"""SELECT f.ticker, f.rating FROM tav2_bq.fa_ratings_8l AS f
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
rating8l = dict(zip(r8["ticker"], r8["rating"]))

# ── 3. today's eligible BAL signals ──
today = sig[(sig["time"] == LATEST) & sig["play_type"].isin(TIER_BAL)].copy()
sec_map = bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
today["sec"] = today["ticker"].map(sec_map)
today["prio"] = today["play_type"].map(PRIORITY)
today["rating8l"] = today["ticker"].map(rating8l)
today["weak"] = today["rating8l"].fillna(0).astype(float) >= 4
half_in_state = state_today in (1, 2)
today["weight"] = np.where(today["weak"] & half_in_state, WEAK_PCT, POS_PCT)

def select_book(cand):
    c = cand.sort_values(["prio", "ta"], ascending=[True, False])
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

# ── 4. LAG book (always-on): PEAD entries due ──
trade_dates = sorted(vni["time"].unique())
def td_offset(ref, off):
    """ref + off trading days; returns (date|None, sessions_beyond_LATEST if extrapolated)."""
    pos = int(np.searchsorted(np.array(trade_dates, dtype="datetime64[ns]"), np.datetime64(ref), side="right")) - 1
    if pos < 0: return None, None
    tgt = pos + off
    if tgt < len(trade_dates): return pd.Timestamp(trade_dates[tgt]), 0
    return None, tgt - (len(trade_dates) - 1)     # entry falls N sessions AFTER the latest session

lag_up, lag_recent = [], []
try:
    ev = pd.read_csv(os.path.join(WORKDIR, "data/earnings_events_classified.csv"), parse_dates=["Release_Date"])
    with open(os.path.join(WORKDIR, "data/earnings_surprise_data.pkl"), "rb") as f: fin = pickle.load(f)
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
    fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
    fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
    ev = ev.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                  on=["ticker","quarter","Release_Date"], how="left")
    ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
    ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
    LN2 = np.log(2); HL = 3.0; ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
    for tk, g in ev.groupby("ticker"):
        hist = []
        for ri in g.index.tolist():
            row = ev.loc[ri]; cd = row["Release_Date"]; ev.at[ri, "prior_n_good"] = len(hist)
            if hist:
                da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
                w = np.exp(-LN2 * ((cd - da).days.values / 365.25) / HL)
                ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
            if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]): hist.append((cd, row["post_ret"]))
    cand = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
    cand = cand[cand["Release_Date"] >= pd.Timestamp(START)]
    for _, row in cand.iterrows():
        entry, ahead = td_offset(row["Release_Date"], 5)
        tier = "LAG_HI" if row["surprise_B_MA"] > 0.5 else "LAG_LO"
        item = {"ticker": row["ticker"], "tier": tier, "release": row["Release_Date"].date(),
                "np_r": float(row["NP_R"]), "pa_hl3": float(row["pa_HL3"])}
        if entry is None and ahead is not None and 1 <= ahead <= 5:
            item["entry"] = f"T+{ahead} phiên tới"; lag_up.append(item)
        elif entry is not None and entry > LATEST:
            item["entry"] = str(entry.date()); lag_up.append(item)
        elif entry is not None and entry >= LATEST - pd.Timedelta(days=5) and entry <= LATEST:
            item["entry"] = str(entry.date()); lag_recent.append(item)
except Exception as e:
    print(f"  WARNING: LAG schedule unavailable ({e})")
print(f"  LAG entries: {len(lag_up)} upcoming, {len(lag_recent)} entered in last sessions")

# ── 5. Allocator: w_LAG target vs current (band ±10pp) ──
w_tgt = STATE_LAG_WEIGHT.get(state_today, 0.5)
w_cur, alloc_note = None, "pt_v22 logs unavailable"
try:
    pl = pd.read_csv(os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv"), parse_dates=["ymd"]).sort_values("ymd")
    last = pl.iloc[-1]
    lag_mv = float(last["SECOND_cash"]) + float(last["SECOND_stocks"]) + float(last["SECOND_etf"])
    w_cur = lag_mv / float(last["nav"]) if float(last["nav"]) > 0 else None
    alloc_note = f"as of {last['ymd'].date()}"
except Exception as e:
    print(f"  WARNING: cannot read pt_v22 logs ({e})")
band_breach = (w_cur is not None) and (abs(w_cur - w_tgt) > ALLOC_BAND)

# ── 6. CAPIT v2 monitor (gate 30% + state routing + grind + BEAR guard) ──
br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START_BR}' AND DATE '{END}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
breadth_today = float(br["oversold"].iloc[-1]) if len(br) else np.nan
capit_fired = bool(pd.notna(breadth_today) and breadth_today >= WASHOUT_GATE)
vnh = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_VNI}' AND DATE '{END}' ORDER BY t.time""")
vnh["time"] = pd.to_datetime(vnh["time"]); vnh = vnh.set_index("time")
vnh["dd52"] = (vnh["Close"] / vnh["Close"].rolling(252, min_periods=60).max() - 1) * 100
_r = vnh["Close"].pct_change()
vnh["rv10"] = _r.rolling(10).std() * np.sqrt(252) * 100
vnh["vn_cooling"] = vnh["rv10"] <= vnh["rv10"].rolling(30).max() * 0.85
dd52_now = float(vnh["dd52"].iloc[-1]) if len(vnh) else -99.0
vn_cool_now = bool(vnh["vn_cooling"].iloc[-1]) if len(vnh) and pd.notna(vnh["vn_cooling"].iloc[-1]) else False

capit_size, capit_grind, basket = 0.0, False, []
if capit_fired:
    wdays = br[br["oversold"] >= WASHOUT_GATE]["time"].tolist()
    bdates = br["time"].tolist(); i0 = len(bdates) - 1
    wset = set(wdays)
    for back in range(20, 91):
        j = i0 - back
        if j >= 0 and bdates[j] in wset: capit_grind = True; break
    base = capit_base(state_today, dd52_now, vn_cool_now)
    capit_size = base * (0.5 if capit_grind else 1.0)
    if capit_size > 0.005:
        bd = br["time"].iloc[-1]
        e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{bd.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
        if not e.empty:
            g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
            pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
            pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
            basket = sorted(pick["ticker"].tolist())

# ── 7. emit recommendations (CSV + MD + status JSON) ──
etf_frac = ETF_PARK.get(state_today, 0.0)

# fetch parking basket early — used for both CSV rows and MD text
_park_basket = None
_park_rebal_date = None
if etf_frac > 0:
    try:
        import custom30
        _park_basket = custom30.current(bq)
        if len(_park_basket):
            _park_rebal_date = str(_park_basket["rebal_date"].iloc[0])
    except Exception as _e:
        print(f"  WARNING: custom30 lookup failed: {_e}")

recs = []
for _, r in bal.iterrows():
    recs.append({"book": "BAL", "ticker": r["ticker"], "play_type": r["play_type"],
                 "ta": round(float(r["ta"]), 0), "close": round(float(r["Close"]), 1),
                 "sector": int(r["sec"]) if pd.notna(r["sec"]) else None,
                 "weight_pct": r["weight"]*100, "status": "HALF_SIZE" if (r["weak"] and half_in_state) else "FULL"})
for it in lag_up:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "status": f"UPCOMING {it['entry']}"})
for it in lag_recent:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "status": f"ENTERED {it['entry']}"})
for tk in basket:
    recs.append({"book": "CAPIT", "ticker": tk, "play_type": "CAPIT_GOLDEN",
                 "ta": None, "close": None, "sector": sec_map.get(tk),
                 "weight_pct": round(capit_size / max(len(basket), 1) * 100, 2), "status": "WASHOUT"})
# parking basket — advisory rows (book=PARK, weight_pct = within-basket cap-weight %)
if _park_basket is not None:
    for pr in _park_basket.itertuples():
        recs.append({"book": "PARK", "ticker": pr.ticker, "play_type": "CUSTOM30_8L",
                     "ta": float(pr.rating_8l) if pd.notna(pr.rating_8l) else None,
                     "close": None, "sector": None,
                     "weight_pct": round(float(pr.weight) * 100, 4),
                     "status": "PARK_ADVISORY"})
rec_df = pd.DataFrame(recs, columns=["book","ticker","play_type","ta","close","sector","weight_pct","status"])
csv_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.csv")
rec_df.to_csv(csv_path, index=False)

status = {
    "date": END, "signal_date": str(LATEST.date()), "state": state_today,
    "state_name": SNAME.get(state_today, "?"), "source": prov.get("source"),
    "w_lag_target": w_tgt, "w_lag_current": (round(w_cur, 4) if w_cur is not None else None),
    "alloc_band": ALLOC_BAND, "band_breach": bool(band_breach), "alloc_note": alloc_note,
    "etf_park_frac": etf_frac,
    "breadth_oversold": (round(breadth_today, 4) if pd.notna(breadth_today) else None),
    "washout_gate": WASHOUT_GATE, "capit_fired": capit_fired,
    "capit_size": round(capit_size, 2), "capit_grind": capit_grind,
    "dd52w": round(dd52_now, 1), "vn_cooling": vn_cool_now,
    "n_bal": int(len(bal)), "n_lag_upcoming": len(lag_up), "n_lag_recent": len(lag_recent),
    "n_capit_basket": len(basket),
    "n_park": len(_park_basket) if _park_basket is not None else 0,
    "park_rebal_date": _park_rebal_date,
}
with open(os.path.join(WORKDIR, "data", "golive_v23_status.json"), "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

L = []
L.append(f"# V2.3 + DT5G — Daily Recommendations — {END}\n")
L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*\n")
L.append("## Regime, allocator & parking\n")
L.append(f"- **Market state (gated):** {state_today} = **{SNAME.get(state_today,'?')}**  (source: {prov.get('source','?')})")
L.append(f"- **Allocator w_LAG:** target **{w_tgt*100:.0f}%**" +
         (f" | current {w_cur*100:.0f}% ({alloc_note})" if w_cur is not None else " | current n/a") +
         (f" → **REBALANCE (band ±{ALLOC_BAND*100:.0f}pp breached)**" if band_breach else f" → trong band ±{ALLOC_BAND*100:.0f}pp, không rebalance"))
if state_today == 2:
    L.append(f"- ⚠️ **BEAR** — LAG book defunded (w_LAG=0: PEAD lỗ trong bear); BAL chỉ Fresh-Q ≤60d, mã rating≥4 half-size.")
if state_today == 1:
    L.append(f"- ⚠️ **CRISIS** — BAL chỉ Fresh-Q ≤30d, mã rating≥4 half-size; theo dõi CAPIT washout (cơ hội capitulation-buy).")
if etf_frac > 0:
    if _park_basket is not None:
        _top = " · ".join(f"{r.ticker} {r.weight*100:.0f}%" for r in _park_basket.head(8).itertuples())
        L.append(f"- **Parking (cả 2 book):** park **{etf_frac*100:.0f}%** cash nhàn rỗi vào "
                 f"**rổ 8L custom30** (`tav2_bq.custom30_8l`, cap-weight namecap≤10%, {len(_park_basket)} mã)"
                 + (" (NEUTRAL)" if state_today == 3 else "") + f"\n    - top: {_top} …")
    else:
        L.append(f"- **Parking (cả 2 book):** park **{etf_frac*100:.0f}%** cash nhàn rỗi vào rổ 8L custom30 "
                 f"(`tav2_bq.custom30_8l`) — lookup lỗi (xem log)")
else:
    L.append(f"- **Parking:** {etf_frac*100:.0f}% (state {state_today} → KHÔNG park, giữ cash phòng thủ)")
L.append(f"\n## BAL book ({(1-w_tgt)*100:.0f}% NAV target) — {len(bal)} picks\n")
if len(bal):
    L.append("| ticker | tier | 8L | ta | close | sector | weight (of book) |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for _, r in bal.iterrows():
        rt = rating8l.get(r["ticker"]); rt = int(rt) if pd.notna(rt) and rt is not None else "-"
        L.append(f"| {r['ticker']} | {r['play_type']} | {rt} | {float(r['ta']):.0f} | {float(r['Close']):.1f} | {int(r['sec']) if pd.notna(r['sec']) else '-'} | {r['weight']*100:.0f}% |")
else:
    L.append("_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL "
             "(MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có "
             "(45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.")
_latest = sig[sig["time"] == LATEST]
_exb = _latest[_latest["play_type"] == "AVOID_exbull"]
if len(_exb):
    L.append(f"\n_AVOID_exbull (momentum bị chặn trong EX-BULL):_ " + ", ".join(_exb["ticker"].head(12)))
_info = _latest[_latest["play_type"].isin(["COMPOUNDER_BUY", "S_PRO", "MOMENTUM_QUALITY", "MOMENTUM_S_N"])]
if len(_info):
    L.append(f"\n_Informational (ngoài tier BAL, V2.3 không trade):_ " +
             ", ".join(f"{r['ticker']}({r['play_type']})" for _, r in _info.head(12).iterrows()))
L.append(f"\n## LAG book ({w_tgt*100:.0f}% NAV target, always-on PEAD)\n")
L.append("Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. "
         "LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.\n")
if lag_up:
    L.append("**Vào lệnh phiên tới:**")
    for it in lag_up:
        L.append(f"- **{it['ticker']}** ({it['tier']}) — entry {it['entry']} (release {it['release']}, NP_R {it['np_r']:.0f}%, pa_HL3 {it['pa_hl3']:.1f})")
else:
    L.append("_(không có entry PEAD đến hạn phiên tới)_")
if lag_recent:
    L.append("\n_Đã vào trong các phiên gần nhất:_ " + ", ".join(f"{it['ticker']}({it['entry']})" for it in lag_recent))
if state_today == 2:
    L.append("\n⚠️ BEAR: allocator w_LAG=0 — KHÔNG cấp vốn entry LAG mới cho tới khi thoát BEAR.")
L.append(f"\n## CAPIT v2 monitor\n")
L.append(f"- Oversold breadth (D_RSI<0.3, ticker_prune): **{breadth_today*100:.1f}%** vs gate {WASHOUT_GATE*100:.0f}%")
if capit_fired:
    L.append(f"- 🚨 **WASHOUT GATE FIRED** — state routing size = **{capit_size:.2f}** (grind={capit_grind}, dd52w={dd52_now:.1f}%, vn_cooling={vn_cool_now})")
    L.append(f"- Committed VND = size × free cash mỗi book, hold {CAPIT_HOLD}td, stop-exempt, slot-exempt.")
    if basket:
        L.append(f"- Basket quality-golden ({len(basket)} mã): " + ", ".join(basket))
    else:
        L.append("- Basket: <3 mã quality đạt chuẩn — sleeve không kích hoạt.")
else:
    L.append("- Gate chưa kích hoạt — sleeve dormant.")
L.append(f"\n## Notes\n- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = {(1-w_tgt)*100:.0f}% NAV, LAG book = {w_tgt*100:.0f}% NAV theo allocator).")
L.append(f"- BAL: max {MAX_POS} pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.")
L.append(f"- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).")
L.append(f"- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.")
L.append(f"- CSV: `out/golive_v23_recommendations_{END}.csv` | status: `data/golive_v23_status.json`")
md_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.md")
open(md_path, "w", encoding="utf-8").write("\n".join(L))

print(f"\n  state={state_today}({SNAME.get(state_today,'?')})  w_LAG tgt={w_tgt*100:.0f}%" +
      (f" cur={w_cur*100:.0f}%" if w_cur is not None else "") +
      f"  parking={etf_frac*100:.0f}%  breadth={breadth_today*100:.1f}%")
print(f"  BAL picks: {len(bal)} | LAG upcoming: {len(lag_up)} | CAPIT fired: {capit_fired}")
print(f"  -> {md_path}")
print(f"  -> {csv_path}")
print("DONE.")
