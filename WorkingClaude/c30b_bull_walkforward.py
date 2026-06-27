# -*- coding: utf-8 -*-
"""c30b_bull_walkforward.py — BULL-PERIODS-ONLY walk-forward of the bull parking vehicle.

Question (Mike dispatch Taylor_20260627_103040): at go-live scale (1B-5B VND), does custom30B
out-park custom30V (and cash) inside DT5G BULL/EX-BULL periods? Should the bull-park enable
threshold drop below 150B?

Method (clean, isolated — NOT the full V2.4 blend):
  - Build both candidate baskets PIT (build_pit, top30, gate<=3, q2m5 rebal, namecap 0.10):
        custom30V = BASKET_SELECT=yieldcombo  (value-yield: rank(1/PE)+rank(1/PCF))
        custom30B = BASKET_SELECT=pemom, MOM_W=1.0, LIQ_FLOOR_B=5  (R6 prod-candidate spec)
  - DT5G state from vnindex_5state_dt5g_live; bull mask = state in {4,5}.
  - Take each basket's DAILY return ONLY on bull days; cash = 0% on bull days (deposit=0).
  - Compound the bull-only return path -> CAGR (annualised over BULL-time), Sharpe, MaxDD.
  - Walk-forward: IS = bull days 2014-2019, OOS = bull days 2020-2026. PASS = IS>0 AND OOS>0
    AND OOS edge (B-V) does not flip negative.
  - Capacity: basket 60-session ADV vs deployed position @1B / @5B under the 20%-ADV rule.
  - TC: per-rebalance turnover x 0.1% (annualised over bull-time).

Audit: writes data/c30b_bull_walkforward.csv (per-day V/B/cash bull returns) and recomputes
the headline cumulative return from that CSV (self-check).
"""
import os, numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
os.environ.setdefault("BQ_CACHE_THREADS", "1")  # determinism (registry item 6)
from simulate_holistic_nav import bq
import custom_basket

END = os.environ.get("AUDIT_END", "2026-06-19"); START = "2014-01-01"
TRADING_DAYS = 252
TC_RATE = 0.001  # 0.1% per traded notional

# ---- DT5G state ----
st = bq(f"SELECT time,state FROM tav2_bq.vnindex_5state_dt5g_live WHERE time>='{START}' AND time<='{END}'")
st["time"] = pd.to_datetime(st["time"]); state = st.set_index("time")["state"]
state = state[~state.index.duplicated(keep="last")].sort_index()

# ---- baskets (PIT) ----
def basket(env):
    for k, v in env.items(): os.environ[k] = str(v)
    lvl, adv, members, _ = custom_basket.build_pit(
        bq, START, END, top_n=30, gate_rating=3, rebal="q2m5", weight_scheme="namecap", name_cap=0.10)
    for k in env: os.environ.pop(k, None)
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index); s = s.sort_index()
    a = pd.Series(adv); a.index = pd.to_datetime(a.index); a = a.sort_index()
    return s, a, members

print("building custom30V (yieldcombo) ...")
lvl_v, adv_v, mem_v = basket({"BASKET_SELECT": "yieldcombo"})
print("building custom30B (pemom MOM_W=1.0 floor=5B) ...")
lvl_b, adv_b, mem_b = basket({"BASKET_SELECT": "pemom", "BASKET_MOM_W": 1.0, "BASKET_LIQ_FLOOR_B": 5})

# ---- common bull-day return panel ----
idx = lvl_v.index.intersection(lvl_b.index)
idx = idx[(idx >= pd.Timestamp(START)) & (idx <= pd.Timestamp(END))]
rv = lvl_v.reindex(idx).pct_change()
rb = lvl_b.reindex(idx).pct_change()
bull = state.reindex(idx).isin([4, 5])
# keep only days where BOTH baskets have a valid return AND it's a bull day
panel = pd.DataFrame({"ret_v": rv, "ret_b": rb, "bull": bull}).dropna(subset=["ret_v", "ret_b"])
panel = panel[panel["bull"]].copy()
panel["ret_cash"] = 0.0
panel.to_csv("data/c30b_bull_walkforward.csv", index_label="ymd")
print(f"\nbull/exbull trading days in window: {len(panel)}")

def met(r):
    r = np.asarray(r, dtype=float)
    if len(r) < 2: return dict(n=len(r), cum=np.nan, cagr=np.nan, sh=np.nan, dd=np.nan)
    nav = np.cumprod(1 + r)
    cum = nav[-1] - 1
    cagr = nav[-1] ** (TRADING_DAYS / len(r)) - 1          # annualised over BULL-time
    sh = r.mean() / r.std(ddof=1) * np.sqrt(TRADING_DAYS) if r.std(ddof=1) > 0 else np.nan
    dd = (nav / np.maximum.accumulate(nav) - 1).min()
    return dict(n=len(r), cum=cum * 100, cagr=cagr * 100, sh=sh, dd=dd * 100)

def window(df, lo, hi): return df[(df.index >= lo) & (df.index <= hi)]

def report(tag, df):
    print(f"\n=== {tag} (n={len(df)} bull days) ===")
    print(f"  {'vehicle':10s} {'cum%':>8s} {'CAGR(bull-time)%':>17s} {'Sharpe':>7s} {'MaxDD%':>8s}")
    for col, name in [("ret_cash", "cash"), ("ret_v", "custom30V"), ("ret_b", "custom30B")]:
        m = met(df[col].values)
        print(f"  {name:10s} {m['cum']:8.2f} {m['cagr']:17.2f} {m['sh']:7.2f} {m['dd']:8.1f}")
    mv = met(df["ret_v"].values); mb = met(df["ret_b"].values)
    print(f"  -> custom30B - custom30V: CAGR {mb['cagr']-mv['cagr']:+.2f}pp | Sharpe {mb['sh']-mv['sh']:+.2f}")
    return mv, mb

FULL = panel
IS = window(panel, "2014-01-01", "2019-12-31")
OOS = window(panel, "2020-01-01", "2026-12-31")
mv_f, mb_f = report("FULL 2014-2026", FULL)
mv_i, mb_i = report("IS 2014-2019", IS)
mv_o, mb_o = report("OOS 2020-2026", OOS)

# ---- self-check: recompute FULL custom30B cum from CSV ----
chk = pd.read_csv("data/c30b_bull_walkforward.csv")
cum_csv = (1 + chk["ret_b"]).prod() - 1
print(f"\n[self-check] custom30B FULL cum from CSV = {cum_csv*100:.4f}%  vs in-mem {mb_f['cum']:.4f}%  "
      f"diff {abs(cum_csv*100 - mb_f['cum']):.2e}pp")

# ---- TC estimate (turnover per rebalance) ----
def turnover(members):
    reb = sorted(members["rebal_date"].unique())
    prev = None; tos = []
    for d in reb:
        cur = set(members[members["rebal_date"] == d]["ticker"])
        if prev is not None:
            churn = len(cur ^ prev) / 2.0      # names in/out
            tos.append(churn / max(len(cur), 1))
        prev = cur
    return float(np.mean(tos)) if tos else np.nan
to_v, to_b = turnover(mem_v), turnover(mem_b)
# rebalances per bull-year: count rebal dates landing in bull, annualise over bull-time
def reb_per_bullyear(members):
    reb = pd.to_datetime(sorted(members["rebal_date"].unique()))
    rb_bull = sum(state.reindex([d], method="ffill").isin([4, 5]).iloc[0] for d in reb if d in state.index or True)
    bull_years = len(FULL) / TRADING_DAYS
    return rb_bull / bull_years if bull_years > 0 else np.nan
rpy = 4.0  # quarterly
print(f"\n[TC] avg per-rebalance turnover  custom30V={to_v:.1%}  custom30B={to_b:.1%}")
print(f"     annual TC drag ~ turnover x {rpy:.0f} rebal/yr x 2 sides x {TC_RATE:.1%}:"
      f"  V={to_v*rpy*2*TC_RATE*100:.2f}%/yr  B={to_b*rpy*2*TC_RATE*100:.2f}%/yr")

# ---- capacity: ADV vs deployed position @1B / @5B ----
# Deployed bull position = park_frac(0.7) x idle-in-bull(~0.30 of NAV typical) ~= 0.21 of NAV into basket.
DEPLOY_FRAC = 0.21
adv_recent_v = adv_v.reindex(panel.index).dropna()
adv_recent_b = adv_b.reindex(panel.index).dropna()
adv_v_now = float(adv_recent_v.iloc[-1]); adv_b_now = float(adv_recent_b.iloc[-1])
print(f"\n[capacity] basket 60-sess ADV (latest bull day) custom30V={adv_v_now/1e9:.1f}B  custom30B={adv_b_now/1e9:.1f}B")
for nav_b in (1, 5):
    nav = nav_b * 1e9
    pos = DEPLOY_FRAC * nav                     # total VND deployed into the basket
    max_name = pos * 0.10                        # namecap 0.10
    # 20%-ADV rule on the basket aggregate (single-day creation) and on the smallest-name proxy
    # smallest member ADV ~ basket aggregate ADV / 30 (rough; conservative since cap-weighted)
    name_adv_b = adv_b_now / 30
    name_adv_v = adv_v_now / 30
    print(f"  @ {nav_b}B NAV: deploy {pos/1e6:.0f}M total, max single name {max_name/1e6:.1f}M")
    print(f"     custom30B per-name ADV~{name_adv_b/1e9:.2f}B -> 20%-ADV cap {0.2*name_adv_b/1e6:.0f}M  "
          f"{'OK' if max_name <= 0.2*name_adv_b else 'TIGHT'}")
    print(f"     custom30V per-name ADV~{name_adv_v/1e9:.2f}B -> 20%-ADV cap {0.2*name_adv_v/1e6:.0f}M  "
          f"{'OK' if max_name <= 0.2*name_adv_v else 'TIGHT'}")

print("\nDONE")
