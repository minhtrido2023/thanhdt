#!/usr/bin/env python3
"""
pt_v4_capit_faithful.py — TRANSACTION-FAITHFUL committed capitulation sleeve on a
V4-philosophy single-wallet book, 50B. Default window 2022->now (7 events);
`--full` = 2014->now (12 events, the deployable headline).

RESULT (2026-06-10, --full): BASE 12.85%/Sh0.95 -> +CAPIT 15.51%/Sh1.09, DELTA
+2.66pp, MaxDD unchanged. Recombined same-window playbook-sized = +5.4pp -> real
fills cut the edge ~in half, and the cut is CAPACITY: fill% of committed size
collapses as NAV grows (2014@50B 100% -> 2018@119B 38% -> 2023-10@250B 4%) because
the golden basket is only 3-4 liquid names. Cross-check: 2022->now window faithful
-1.21pp vs recombined -1.10/-1.32pp = the substitution math itself translates.
===============================================================================
WHY: the +6.58pp committed-sleeve result was measured on the leg-recombined V5 NAV
(idealized, hides risk). This script answers "can the number be reproduced with
real transactions?" — ONE wallet, real fills (T+1 Open, slippage, 0.3% TC round-trip,
20%-of-ADV liquidity caps at 50B), real cash ledger, no margin.

BOOK (both arms) = V4 BAL philosophy at full 50B (closest faithful single-wallet
proxy of V4 — the switched VN30/LAG leg is the recombination artifact we're NOT
reproducing, stated limitation):
  - signal  : real BA-v11 stack (ba_v11_unified_12y_sig.pkl) + SV_TIGHT + overheat-AVOID
  - tiers   : TIER_BAL, tier_weights 10%/name, max 12 positions, sector-8 cap 4
  - exits   : hold 45d / stop -20% / min_hold 2 (prod spec)
  - parking : DT5G NEUTRAL -> 70% idle cash in E1VFVN30 (ETF_BASE {3:0.7}); JIT sell
  - costs   : slippage 0.1% + tiered exit slip, TC 0.15+0.15+0.1, borrow 10%, deposit 0
  - state   : DT5G (daily_comovement_dt5g.csv), play_type internal gating = pkl's own
ARM 2 adds the COMMITTED CAPITULATION SLEEVE exactly per crisis_playbook.md:
  - events  : oversold breadth >=40% washouts (7 events 2022+)
  - sizing  : size = base(1.0 CRISIS / 0.5 else) x grind(0.5 if repeat<=90td)
              committed VND = size x BASE-arm raw cash at signal date (f=cash decision);
              per-name NAV-weight = that / K names. Engine cash cap = hard floor (no margin).
  - basket  : playbook-exact eligibility (ROE_Min5Y>=12% & ROIC5Y>=10% & FSCORE>=6,
              liq>=2B) golden pb_z<-1 -> fallback pb_z<0 -> all; max 15 names
              (pre-fetched: data/capit_event_elig.csv)
  - hold    : 60 trading days COMMITTED — no stop-loss, slot-exempt, engine never
              force-sells it (no state_exit_map in V4 spec) = "respect the sleeve"
Outputs: data/pt_v4_capit_faithful_{nav_base,nav_capit,transactions}.csv + console.
Run: python pt_v4_capit_faithful.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
INIT = 50_000_000_000          # all simulations start at 50B (user spec)
FULL = "--full" in sys.argv    # --full: 2014 -> now (12 events); default: 2022 -> now (7 events)
START_MEASURE = "2014-01-02" if FULL else "2022-01-01"
PANEL_FILE = "v4f_panel_2014.csv" if FULL else "v4f_panel.csv"
ELIG_FILE  = "capit_event_elig_full.csv" if FULL else "capit_event_elig.csv"
# CAPIT universe (env CAPIT_UNIV, 2026-06-16): "golden" = OLD deep pb_z<=-1 + strict-quality (illiquid,
# capacity-trapped). "custom30" = user reframe — capitulation-buy from the liquid custom30 basket, picks =
# all members 'cheap enough' (pb_z<0). Validated: 15x more deployable, +return, lower downside.
CAPIT_UNIV = os.environ.get("CAPIT_UNIV", "golden").lower()
if CAPIT_UNIV == "custom30": ELIG_FILE = "capit_event_elig_custom30.csv"
CAPIT_PBZ = float(os.environ.get("CAPIT_PBZ", "0"))          # custom30 cheapness cut (0=pb_z<0; -0.5 deeper)
CAPIT_DEPLOY_CAP = float(os.environ.get("CAPIT_DEPLOY_CAP", "1.0"))   # cap total per-event deploy weight
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}
MAX_POS = 12
# playbook sizing per event: (date, state, grind) -> size = base x grind
EVENTS_2014 = [("2014-05-08",1,False),("2015-08-24",3,False),("2016-01-18",3,True),
               ("2018-05-28",1,False),("2020-03-12",2,False)]
EVENTS = [("2022-04-20",1,False),("2022-06-20",2,True),("2022-09-29",2,True),
          ("2023-10-31",1,False),("2024-04-19",4,False),("2025-04-03",4,False),
          ("2026-03-09",3,False)]
if FULL: EVENTS = EVENTS_2014 + EVENTS
def size_of(state, grind):
    base = 1.0 if state == 1 else 0.5
    return base * (0.5 if grind else 1.0)

# ── data ────────────────────────────────────────────────────────────────────
print("[1] Loading data...")
panel = pd.read_csv(os.path.join(W,"data",PANEL_FILE), parse_dates=["time"])  # hole-free: no per-day liq/PE row filter (gating belongs at signal level)
sig_b = pickle.load(open(os.path.join(W,"data/ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
sig_b = sig_b[sig_b["time"] >= panel["time"].min()].copy()

dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
# ffill DT5G state over panel dates beyond comovement file end
vni_dates = sorted(panel["time"].unique())
last_st = None
for d in vni_dates:
    if d in state_by_date: last_st = state_by_date[d]
    elif last_st is not None: state_by_date[d] = last_st

vnx = pd.read_csv(os.path.join(W,"data/VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
vnx = vnx[vnx["time"] >= panel["time"].min()]
etf = pd.read_csv(os.path.join(W,"data","e1vfvn30_daily.csv"), parse_dates=["time"])
vn30_und = pd.Series(etf["Close"].values, index=etf["time"])

# ── signal: SV_TIGHT + overheat (same layering as prodspec dt5g) ────────────
print("[2] Building signal (SV_TIGHT + overheat-AVOID on DT5G)...")
def sv_tight_keep(row):
    s, days = row["state5"], row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mb = sig_b["play_type"].isin(BUY_TIERS)
sig_b = sig_b[(~mb) | sig_b.apply(sv_tight_keep, axis=1)].copy()

v = vnx.merge(pd.DataFrame({"time": list(state_by_date.keys()), "st": list(state_by_date.values())}), on="time", how="left")
v["st"] = v["st"].ffill()
oh_dates = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["st"]==5) | (v["D_RSI"] > 0.75))]["time"])
sig_b.loc[sig_b["time"].isin(oh_dates) & sig_b["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

sec_map = sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}

sig_mom = sig_b[["time","ticker","play_type","ta","Close"]].copy()

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
COMMON = dict(max_positions=MAX_POS, hold_days=45, stop_loss=-0.20, min_hold=2,
              slippage=0.001, init_nav=INIT,
              sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
              cash_etf_states={3:0.7}, vn30_underlying=vn30_und,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=opens, t1_open_exec=True, **LIQ)

def run(sig, tiers, label, tw, extra=None):
    ev = []
    nav, _ = simulate(sig, prices, vni_dates, allowed_tiers=tiers,
                      tier_weights=tw, event_log=ev, name=label, **COMMON, **(extra or {}))
    nav["time"] = pd.to_datetime(nav["time"])
    return nav, pd.DataFrame(ev)

def metrics(nav_df):
    nd = nav_df[nav_df["time"] >= START_MEASURE]
    s = nd.set_index("time")["nav"]
    r = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    dd = (s/s.cummax()-1).min(); sh = r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, cagr/abs(dd) if dd < 0 else 0, s.iloc[-1]/1e9

# ── PASS 1: BASE arm ────────────────────────────────────────────────────────
print("[3] PASS 1 — BASE arm (V4-philosophy, 50B one wallet)...")
nav_base, ev_base = run(sig_mom, TIER_BAL, "V4F_BASE", TIER_WEIGHTS)
cb, db, sb, calb, wb = metrics(nav_base)
print(f"    BASE : CAGR {cb:6.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}  Calmar {calb:.2f}  NAV {wb:.1f}B")

# ── PASS 2: CAPIT arm (sleeve sized from BASE real cash at signal date) ─────
print("[4] PASS 2 — committed CAPIT sleeve (playbook sizing, real-cash f)...")
basecash = nav_base.set_index("time")["cash_pct"] / 100.0   # raw cash only (f=cash)
elig = pd.read_csv(os.path.join(W,"data",ELIG_FILE), parse_dates=["event"])

cap_rows, cap_tw, cap_tiers, cap_info = [], {}, [], []
for i, (ds, st, grind) in enumerate(EVENTS):
    d = pd.Timestamp(ds)
    e = elig[elig["event"] == d].copy()
    if len(e) == 0:                       # no eligible names this event (e.g. custom30 pre-2014-08)
        cap_info.append((ds, st, grind, float("nan"), 0.0, 0)); continue
    # tradable-first: only names the sim can actually fill at the signal date
    e = e[[t in prices and d in prices[t] for t in e["ticker"]]]
    if CAPIT_UNIV == "custom30":
        # liquid custom30 universe -> 'cheap enough' (pb_z < CAPIT_PBZ). RESCUE knobs (2026-06-16): the
        # naive pb_z<0 + uncapped sizing OVER-deployed (164B into a -9.9% event) -> worse risk-adj than
        # golden. CAPIT_PBZ (default 0; -0.5 = higher conviction) and CAPIT_DEPLOY_CAP (cap total weight)
        # test whether liquidity breadth can be kept WITHOUT over-deploying into low-conviction names.
        pick = e[e["pbz"] < CAPIT_PBZ]
        pick = pick.nsmallest(20, "pbz") if len(pick) > 20 else pick
    else:
        g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
        pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
        pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    names = list(pick["ticker"])
    if len(names) < 3:
        cap_info.append((ds, st, grind, float("nan"), 0.0, len(names))); continue
    pos = basecash.index.searchsorted(d)
    cfree = float(basecash.iloc[max(0,pos-2):pos+1].mean())
    w_total = size_of(st, grind) * max(cfree, 0.0)
    w_total = min(w_total, CAPIT_DEPLOY_CAP)        # sizing cap (RESCUE): bound per-event deployment
    if w_total <= 0.005:
        cap_info.append((ds, st, grind, cfree, 0.0, len(names))); continue
    pt = f"CAPIT_E{i}"
    shn.TIER_PRIORITY[pt] = 95
    cap_tw[pt] = w_total / len(names)
    cap_tiers.append(pt)
    cap_info.append((ds, st, grind, cfree, w_total, len(names)))
    for t in names:
        cap_rows.append({"time": d, "ticker": t, "play_type": pt, "ta": 500.0,
                         "Close": prices[t][d]})

print(f"    {'event':<12}{'state':>6}{'grind':>7}{'free-cash':>11}{'committed':>11}{'K':>4}")
for ds, st, gr, cf, wt, k in cap_info:
    print(f"    {ds:<12}{st:>6}{str(gr):>7}{cf:>10.1%}{wt:>10.1%}{k:>4}")

sig_cap = pd.concat([sig_mom, pd.DataFrame(cap_rows)], ignore_index=True)
extra = dict(hold_days_by_tier={t: 60 for t in cap_tiers},
             stop_exempt_tiers=set(cap_tiers),
             slot_exempt_tiers=set(cap_tiers),
             tier_position_limit={t: 15 for t in cap_tiers})
nav_cap, ev_cap = run(sig_cap, TIER_BAL + cap_tiers, "V4F_CAPIT",
                      {**TIER_WEIGHTS, **cap_tw}, extra)
cc, dc, sc, calc, wc = metrics(nav_cap)

# ── report ──────────────────────────────────────────────────────────────────
print("\n" + "="*88)
print(f"FAITHFUL single-wallet result (50B, {START_MEASURE} -> {nav_cap['time'].max().date()}, real fills)")
print("="*88)
print(f"  BASE  (V4-philosophy)      : CAGR {cb:6.2f}%  MaxDD {db:6.1f}%  Sharpe {sb:.2f}  Calmar {calb:.2f}  NAV {wb:.1f}B")
print(f"  +CAPIT committed (playbook): CAGR {cc:6.2f}%  MaxDD {dc:6.1f}%  Sharpe {sc:.2f}  Calmar {calc:.2f}  NAV {wc:.1f}B")
print(f"  DELTA                      : {cc-cb:+.2f}pp CAGR, {dc-db:+.1f}pp MaxDD, {sc-sb:+.2f} Sharpe")

if len(ev_cap):
    tx = ev_cap[ev_cap["play_type"].astype(str).str.startswith("CAPIT")].copy()
    if len(tx):
        print(f"\n  CAPIT sleeve P&L per event (real fills):")
        tx["ymd"] = pd.to_datetime(tx["ymd"])
        for pt in sorted(tx["play_type"].unique()):
            sub = tx[tx["play_type"] == pt]
            buys  = sub[sub["action"]=="buy"]["buy_amount"].sum()
            sells = sub[sub["action"]=="sell"]["sell_amount"].sum()
            fees  = sub["fee"].sum()
            nb = sub[sub["action"]=="buy"]["ticker"].nunique()
            if buys > 0:
                print(f"    {pt:<10} deployed {buys/1e9:6.2f}B over {nb:>2} names -> "
                      f"returned {sells/1e9:6.2f}B  net {(sells-buys-0*fees)/1e9:+6.2f}B ({(sells/buys-1)*100:+5.1f}%)")
# reference: leg-recombined prodspec V4/V5 + VNI over the SAME window (idealization gap)
try:
    rc = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"), parse_dates=["time"]).set_index("time")
    rc = rc[rc.index >= START_MEASURE]
    def m2(s):
        s = s/s.iloc[0]; r = s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
        return (s.iloc[-1]**(1/yrs)-1)*100, (s/s.cummax()-1).min()*100, r.mean()/r.std()*np.sqrt(252)
    for col, lbl in [("V4_V121_ENS_TQ34b","V4 recombined"),("V5_V4_KellyQ2","V5 recombined"),("VNI","VNINDEX B&H")]:
        cg, dd_, sh_ = m2(rc[col])
        print(f"  REF same-window {lbl:<14}: CAGR {cg:6.2f}%  MaxDD {dd_:6.1f}%  Sharpe {sh_:.2f}")
except Exception as ex:
    print("  (ref skipped:", ex, ")")
nav_base.to_csv(os.path.join(W,"data","pt_v4_capit_faithful_nav_base.csv"), index=False)
nav_cap.to_csv(os.path.join(W,"data","pt_v4_capit_faithful_nav_capit.csv"), index=False)
if len(ev_cap): ev_cap.to_csv(os.path.join(W,"data","pt_v4_capit_faithful_transactions.csv"), index=False)
print("  Saved: data/pt_v4_capit_faithful_{nav_base,nav_capit,transactions}.csv")
