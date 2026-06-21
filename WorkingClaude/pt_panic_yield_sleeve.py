# -*- coding: utf-8 -*-
"""pt_panic_yield_sleeve.py — STEP 2 NAV backtest of the "panic + cheap-on-yield" deep-value sleeve.

Idea (user 2026-06-18, validated step-1 IC): pb_z = PANIC GATE (cheap vs own 5y PB history), the two
YIELD axes (1/PE + 1/PCF) = the cheapness DISCRIMINATOR that separates real bargains from value traps.
Optional secondary gate = D_RSI oversold. Quality gate (ROE_Min5Y/ROIC5Y/FSCORE) = the trap guard (it
also excludes HAG-style structural junk). Monthly-rebalanced equal-weight basket, top-N by yield rank
within the gated set. T+1 Open execution, 20% ADV liquidity cap, self-check (cash-flow identity 0 VND).

This is a STANDALONE single-book sleeve measure (not integrated) — to see standalone CAGR/Sharpe/DD,
walk-forward IS/OOS, per-year (esp. the 2025 bull-grind drag), before deciding capital/integration.

Env: NAV_TOTAL_B(20) AUDIT_START(2014-01-02) AUDIT_END(auto) RSI_GATE(1) RSI_THR(0.40) GATE_PBZ(-1.0)
     TOPN(15) HOLD_D(30) STOP(off) REBAL(M=monthly)
"""
import os, sys
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq, simulate
from pt_dates import detect_end_date

NAV        = float(os.environ.get("NAV_TOTAL_B", "20")) * 1e9
START_DATE = os.environ.get("AUDIT_START", "2014-01-02")
END_DATE   = os.environ.get("AUDIT_END") or detect_end_date()
RSI_GATE   = os.environ.get("RSI_GATE", "1") == "1"
RSI_THR    = float(os.environ.get("RSI_THR", "0.40"))
QUAL       = os.environ.get("QUAL", "strict")   # strict | mild | prune (broaden for deal flow)
_QUAL_SQL  = {"strict": "AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6",
              "mild":   "AND p.ROE_Min5Y>=0.08 AND p.FSCORE>=5",
              "prune":  ""}[QUAL]   # prune = ticker_prune membership + liquidity only
GATE_PBZ   = float(os.environ.get("GATE_PBZ", "-1.0"))
TOPN       = int(os.environ.get("TOPN", "15"))
HOLD_D     = int(os.environ.get("HOLD_D", "30"))
STOP       = os.environ.get("STOP", "off")
STOP_LOSS  = -0.95 if STOP in ("off", "none", "0") else float(STOP)

print("=" * 100)
print(f"  PANIC+YIELD sleeve | NAV {NAV/1e9:.0f}B | {START_DATE}->{END_DATE}")
print(f"  gate pb_z<{GATE_PBZ}{' + D_RSI<'+str(RSI_THR) if RSI_GATE else ' (no RSI gate)'} | quality | "
      f"rank 1/PE+1/PCF top{TOPN} | qual={QUAL} | hold~{HOLD_D}d | stop={STOP}")
print("=" * 100)

# ---- trading dates + monthly rebal anchors ----
vd = bq(f"""SELECT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
vd["time"] = pd.to_datetime(vd["time"]); vni_dates = list(vd["time"])
_m = pd.Series(vni_dates).groupby([pd.Series(vni_dates).dt.year, pd.Series(vni_dates).dt.month]).min()
rebals = list(_m.values)
rebals = [pd.Timestamp(r) for r in rebals]
print(f"[1] {len(vni_dates)} sessions, {len(rebals)} monthly rebalances")

# ---- build signals per rebal: gated quality panic set, rank by yield, top-N ----
rsi_clause = f"AND p.D_RSI < {RSI_THR}" if RSI_GATE else ""
sig_rows, sel_names = [], set()
for rd in rebals:
    q = f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) AS pbz,
      SAFE_DIVIDE(1.0,p.PE) AS ey, SAFE_DIVIDE(1.0,p.PCF) AS cfy, p.Close
    FROM tav2_bq.ticker_prune p
    WHERE p.time = DATE '{rd.date()}' AND p.PE>0 AND p.PCF>0 AND p.PB_SD5Y>0
      {_QUAL_SQL}
      AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2
      AND SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) < {GATE_PBZ} {rsi_clause}"""
    e = bq(q)
    if e.empty: continue
    e["yscore"] = e["ey"].rank(pct=True) + e["cfy"].rank(pct=True)   # cheapness discriminator
    pick = e.nlargest(TOPN, "yscore")
    for _, r in pick.iterrows():
        sig_rows.append({"time": rd, "ticker": r["ticker"], "play_type": "PANIC",
                         "ta": 500.0, "Close": float(r["Close"])})
        sel_names.add(r["ticker"])
sig = pd.DataFrame(sig_rows, columns=["time","ticker","play_type","ta","Close"])
print(f"[2] {len(sig)} signals across {len(rebals)} rebals; {len(sel_names)} distinct names; "
      f"avg {len(sig)/max(1,sig['time'].nunique()):.1f}/rebal")
if sig.empty:
    print("  NO SIGNALS — gate too tight."); sys.exit(0)

# ---- price/open/liquidity panels for the selected universe ----
names = sorted(sel_names)
chunks = [names[i:i+250] for i in range(0, len(names), 250)]
parts = []
for ch in chunks:
    inl = ",".join(f"'{t}'" for t in ch)
    parts.append(bq(f"""SELECT t.ticker,t.time,t.Open,t.Close,t.Volume_3M_P50
      FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
      AND t.ticker IN ({inl})"""))
px = pd.concat(parts, ignore_index=True); px["time"] = pd.to_datetime(px["time"])
prices, opens, liq = {}, {}, {}
for tk, g in px.groupby("ticker"):
    gc = g[g["Close"].notna()]; prices[tk] = dict(zip(gc["time"], gc["Close"].astype(float)))
    go = g[g["Open"].notna()];  opens[tk]  = dict(zip(go["time"], go["Open"].astype(float)))
    gl = g[g["Volume_3M_P50"].notna() & g["Close"].notna()]
    for d, a, c in zip(gl["time"], gl["Volume_3M_P50"].astype(float), gl["Close"].astype(float)):
        liq[(tk, d)] = a * c
print(f"[3] price panel: {len(px):,} rows, {len(prices)} tickers")

# ---- simulate (single book, full deployment, T+1 Open) ----
import simulate_holistic_nav as shn
shn.TIER_PRIORITY["PANIC"] = 90
evlog = []
nav_df, trades = simulate(
    sig, prices, vni_dates,
    allowed_tiers={"PANIC"}, max_positions=TOPN,
    tier_weights={"PANIC": 1.0 / TOPN},
    hold_days=HOLD_D, min_hold=3, stop_loss=STOP_LOSS,
    reentry_blacklist_days=0,
    liquidity_lookup=liq, liquidity_volume_pct=0.20, max_fill_days=5, exit_slippage_tiered=True,
    open_prices=opens, t1_open_exec=True,
    init_nav=NAV, deposit_annual=0.0, borrow_annual=0.10,
    event_log=evlog, force_close_eod=True, name="panic_yield")
nav_df["time"] = pd.to_datetime(nav_df["time"])
nav_df = nav_df.set_index("time")
print(f"[4] sim done: final NAV {nav_df['nav'].iloc[-1]/1e9:.2f}B")

# ---- self-check: daily cash-flow identity (cash diff == net trade flows) ----
ev = pd.DataFrame(evlog)
if not ev.empty:
    ev["ymd"] = pd.to_datetime(ev["ymd"])
    ev["net"] = np.where(ev["action"] == "sell", ev["sell_amount"] - ev["fee"],
                         -(ev["buy_amount"] + ev["fee"]))
    # exclude the final-day force-close (EOD): with T+1 exec those exits can't fill, the sim marks
    # open positions to market (legit NAV, == harness MTM_UNREALIZED). Cash-flow identity is checked
    # over the LIVE period (all days except last); end-NAV conservation is asserted separately.
    real = ev[ev["reason"] != "EOD"]
    f = real.groupby("ymd")["net"].sum().reindex(nav_df.index).fillna(0.0)
    cash = nav_df["cash"]; dcash = cash.diff(); dcash.iloc[0] = cash.iloc[0] - NAV
    diff = (dcash - f).iloc[:-1]                                    # drop the force-close last day
    err = float(diff.abs().max())
    # end-NAV conservation: cash gained over live period == net real flows (EOD marks excluded)
    glob = float((cash.iloc[-1] - NAV) - real["net"].sum())
    # nav_final == cash + open marks (identity by construction); report open value carried as MTM
    open_mtm = float(nav_df["nav"].iloc[-1] - cash.iloc[-1])
    print(f"    [diag] live-period max err={err:,.0f}  end cash-conservation err={glob:,.0f}  "
          f"open MTM carried at end={open_mtm/1e9:.2f}B")
else:
    err = glob = 0.0
print(f"[5] SELF-CHECK (live period) cash-flow identity max err = {err:,.0f} VND  "
      f"{'PASS' if err < 1000 and abs(glob) < 1000 else 'FAIL'}")

# ---- metrics (FULL / IS / OOS / per-year) vs VNINDEX ----
vni = bq(f"""SELECT t.time,t.Close FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")["Close"]

def met(s):
    s = s.dropna()
    if len(s) < 5: return None
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else 0
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    dd = (s / s.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=sh, maxdd=dd * 100, calmar=cagr / abs(dd) if dd < 0 else 0)

def show(lbl, navs, vs):
    m = met(navs); v = met(vs)
    if m is None: print(f"  {lbl:16s} (insufficient)"); return
    print(f"  {lbl:16s} sleeve CAGR {m['cagr']:6.2f}%  Sh {m['sharpe']:4.2f}  DD {m['maxdd']:6.1f}%  "
          f"Cal {m['calmar']:4.2f}   |  VNI CAGR {v['cagr']:6.2f}%  DD {v['maxdd']:6.1f}%")

nav = nav_df["nav"]
print("\n[6] WALK-FORWARD")
show("FULL", nav, vni)
isn = nav[nav.index <= "2019-12-31"]; iv = vni[vni.index <= "2019-12-31"]
oos = nav[nav.index >= "2020-01-01"]; ov = vni[vni.index >= "2020-01-01"]
show("IS 2014-19", isn, iv); show("OOS 2020-26", oos, ov)
print("\n[7] PER-YEAR (sleeve CAGR vs VNI)")
for y in range(int(nav.index[0].year), int(nav.index[-1].year) + 1):
    ny = nav[nav.index.year == y]; vy = vni[vni.index.year == y]
    if len(ny) < 5: continue
    sr = (ny.iloc[-1] / ny.iloc[0] - 1) * 100; vr = (vy.iloc[-1] / vy.iloc[0] - 1) * 100
    print(f"  {y}: sleeve {sr:+6.1f}%   VNI {vr:+6.1f}%   {'WIN' if sr > vr else 'lag'}")
print("=" * 100)
