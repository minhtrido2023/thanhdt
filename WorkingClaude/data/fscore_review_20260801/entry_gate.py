#!/usr/bin/env python
"""CAU A — CAPIT ENTRY-gate variants: does the FSCORE>=6 leg earn its place?

Replicates capit_basket()'s selection EXACTLY (pt_v23_audit_2014.py:1168-1180) but swaps the
quality floor. For each real CAPIT event (the 14 that actually got positions in the pinned R3
control run), builds the basket under each floor variant and measures the equal-weight 60-session
forward return (engine convention: tw2[pt] = wt/len(names) => equal weight inside the basket;
entry Open T+1, hold 60 sessions).

Pure measurement. No production wiring. Snapshot: bq_cache_asof20260729_postrestate.
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.environ["BQ_LOCAL_CACHE"] = os.path.join(WORKDIR, "data", "bq_cache_asof20260729_postrestate")
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from bq_local_cache import get_cache  # noqa: E402

CACHE = get_cache()
assert CACHE is not None, "local cache not available"
OUT = os.path.join(WORKDIR, "data", "fscore_review_20260801")
HOLD = 60


def q(sql):
    return CACHE.query(sql)


# ---------------------------------------------------------------- event dates (from pinned ctrl run)
ev = pd.read_csv(os.path.join(WORKDIR, "data", "capit_qexit_20260801", "event_rollup.csv"))
EVENTS = [pd.Timestamp(d) for d in ev["date"]]
print(f"[events] {len(EVENTS)} CAPIT events with real positions: "
      f"{EVENTS[0].date()} .. {EVENTS[-1].date()}")

# ---------------------------------------------------------------- trading calendar (VNINDEX sessions)
cal = q("SELECT DISTINCT t.time FROM tav2_bq.ticker_prune AS t "
        "WHERE t.ticker='VNM' AND t.time >= DATE '2014-01-01' ORDER BY t.time")
CAL = list(pd.to_datetime(cal["time"]))
print(f"[cal] {len(CAL)} sessions {CAL[0].date()}..{CAL[-1].date()}")

# ---------------------------------------------------------------- 8L rating as-of (for the r8l variant)
rat = q("SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l AS r ORDER BY r.ticker, r.time")
rat["time"] = pd.to_datetime(rat["time"])


def rating_asof(d):
    """Last published 8L rating strictly as-of d (no hindsight)."""
    sub = rat[rat["time"] <= d]
    return sub.sort_values("time").groupby("ticker")["rating"].last()


# ---------------------------------------------------------------- floor variants
# 8L drops/deweights FSCORE for exactly these routes (rate_securities/rate_insurance ignore it
# entirely; rate_bank has its own lens). ICB per rating_8l.py:117-118 + route_of().
def is_fscore_blind_route(icb):
    if pd.isna(icb):
        return False
    icb = float(icb)
    return (icb == 8355) or (8530 <= icb <= 8579) or (8770 <= icb <= 8779)


VARIANTS = {
    # name          : callable(df, rat_asof) -> boolean mask on top of ROE/ROIC base
    "V0_prod":      lambda d, r: d["FSCORE"] >= 6,
    "V1_nofscore":  lambda d, r: pd.Series(True, index=d.index),
    "V2_fs5":       lambda d, r: d["FSCORE"] >= 5,
    "V3_sectoraware": lambda d, r: (d["FSCORE"] >= 6) | d["ICB_Code"].map(is_fscore_blind_route),
    "V4_r8l":       lambda d, r: d["ticker"].map(r).le(3).fillna(False),
    # user's own proposal: a name is only excluded after TWO consecutive weak quarters, so a
    # one-quarter accounting wobble (the NCT/SAB complaint) no longer breaks the floor.
    "V5_2q":        lambda d, r: (d["FSCORE"] >= 6) | (d["FSCORE_P1"] >= 6),
}


def select(e, mask):
    """capit_basket() selection, verbatim: cheap-gate ladder then nsmallest(15) on pb_z."""
    pool = e[mask].copy()
    if pool.empty:
        return [], np.nan
    g = pool[pool["pbz"] < -1]
    c = pool[pool["pbz"] < 0]
    pick = g if len(g) >= 3 else (c if len(c) >= 3 else pool)
    pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
    return list(pick["ticker"]), float(pick["pbz"].median())


# ---------------------------------------------------------------- per-event basket build
rows, comp = [], []
for i, d in enumerate(EVENTS):
    e = q(f"""SELECT p.ticker, p.ICB_Code, p.ROE_Min5Y, p.ROIC5Y, p.FSCORE,
  SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz, COALESCE(p.Price,p.Close)*p.Volume/1e9 liq
FROM tav2_bq.ticker_prune p WHERE p.time = DATE '{d.date()}'""")
    # production base floor + liquidity (both kept in EVERY variant)
    base = (e["ROE_Min5Y"] >= 0.12) & (e["ROIC5Y"] >= 0.10) & (e["liq"] >= 2)
    e = e[base.fillna(False)].reset_index(drop=True)
    # prior-quarter FSCORE, PIT (last quarter RELEASED on or before the event date)
    p1 = q(f"""SELECT t.ticker, t.FSCORE_P1 FROM tav2_bq.ticker_financial t
WHERE t.Release_Date <= DATE '{d.date()}' QUALIFY ROW_NUMBER() OVER
  (PARTITION BY t.ticker ORDER BY t.Release_Date DESC) = 1""")
    e["FSCORE_P1"] = e["ticker"].map(p1.set_index("ticker")["FSCORE_P1"])
    r_asof = rating_asof(d)
    for vn, fn in VARIANTS.items():
        m = fn(e, r_asof).fillna(False)
        names, pbz_med = select(e, m)
        comp.append({"event": i, "date": d.date(), "variant": vn, "n_eligible": int(m.sum()),
                     "n_basket": len(names), "pbz_med": pbz_med, "names": ",".join(sorted(names))})
    print(f"  E{i} {d.date()}: " + " ".join(
        f"{v}={c['n_basket']}/{c['n_eligible']}" for v, c in
        ((r["variant"], r) for r in comp[-len(VARIANTS):])))

comp = pd.DataFrame(comp)
comp.to_csv(os.path.join(OUT, "basket_composition.csv"), index=False)

# ---------------------------------------------------------------- forward returns
allnames = sorted({t for s in comp["names"] for t in s.split(",") if t})
inlist = ",".join(f"'{t}'" for t in allnames)
px = q(f"""SELECT p.ticker, p.time, p.Open, p.Close FROM tav2_bq.ticker_prune p
WHERE p.ticker IN ({inlist}) AND p.time >= DATE '2014-01-01'""")
px["time"] = pd.to_datetime(px["time"])
PX = {t: g.set_index("time").sort_index() for t, g in px.groupby("ticker")}


def fwd(t, d, hold=HOLD):
    """Entry Open at the session AFTER d; exit Open `hold` sessions later. None if unpriceable."""
    g = PX.get(t)
    if g is None:
        return None
    try:
        i0 = CAL.index(d)
    except ValueError:
        return None
    if i0 + 1 >= len(CAL):
        return None
    de = CAL[i0 + 1]
    dx = CAL[min(i0 + 1 + hold, len(CAL) - 1)]
    if de not in g.index or dx not in g.index:
        return None
    p0, p1 = g.loc[de, "Open"], g.loc[dx, "Open"]
    if not (p0 > 0 and p1 > 0):
        return None
    return float(p1 / p0 - 1.0)


for _, r in comp.iterrows():
    names = [t for t in r["names"].split(",") if t]
    rr = [(t, fwd(t, pd.Timestamp(r["date"]))) for t in names]
    ok = [(t, x) for t, x in rr if x is not None]
    rows.append({"event": r["event"], "date": r["date"], "variant": r["variant"],
                 "n_basket": len(names), "n_priced": len(ok),
                 "ew_ret": float(np.mean([x for _, x in ok])) if ok else np.nan})

res = pd.DataFrame(rows)
res.to_csv(os.path.join(OUT, "entry_gate_returns.csv"), index=False)

print("\n" + "=" * 78)
print("PER-VARIANT: equal-weight 60-session basket return, averaged over the 14 CAPIT events")
print("=" * 78)
piv = res.pivot(index="event", columns="variant", values="ew_ret")
npiv = res.pivot(index="event", columns="variant", values="n_basket")
dates = res.drop_duplicates("event").set_index("event")["date"]
print(f"{'ev':>3} {'date':>11} " + " ".join(f"{v:>16}" for v in VARIANTS))
for ev_i in piv.index:
    print(f"{ev_i:>3} {str(dates[ev_i]):>11} " + " ".join(
        f"{piv.loc[ev_i, v]*100:>9.1f}% n={int(npiv.loc[ev_i, v]):>2}" for v in VARIANTS))
print("-" * 78)
print(f"{'':>3} {'MEAN':>11} " + " ".join(
    f"{piv[v].mean()*100:>9.2f}% n={npiv[v].mean():>4.1f}" for v in VARIANTS))
print(f"{'':>3} {'MEDIAN':>11} " + " ".join(f"{piv[v].median()*100:>9.2f}%     " for v in VARIANTS))
print(f"{'':>3} {'vs V0 (pp)':>11} " + " ".join(
    f"{(piv[v]-piv['V0_prod']).mean()*100:>+9.2f}pp    " for v in VARIANTS))

# basket-overlap diagnostics vs production
print("\n" + "=" * 78)
print("BASKET DELTA vs V0_prod (how many names actually change)")
print("=" * 78)
w = comp.pivot(index="event", columns="variant", values="names")
for v in VARIANTS:
    if v == "V0_prod":
        continue
    add = rem = same = 0
    for ev_i in w.index:
        a = set(x for x in w.loc[ev_i, "V0_prod"].split(",") if x)
        b = set(x for x in w.loc[ev_i, v].split(",") if x)
        add += len(b - a)
        rem += len(a - b)
        same += len(a & b)
    print(f"  {v:>16}: kept {same:>3}  added {add:>3}  dropped {rem:>3}  "
          f"(prod total names over all events = {same+rem})")

# leave-one-event-out on the headline comparison
print("\n" + "=" * 78)
print("LEAVE-ONE-EVENT-OUT on mean(variant) - mean(V0_prod), pp")
print("=" * 78)
for v in VARIANTS:
    if v == "V0_prod":
        continue
    dl = (piv[v] - piv["V0_prod"])
    loo = [(dl.drop(k).mean()) * 100 for k in dl.index]
    sgn = "ALL SAME SIGN" if (min(loo) > 0 or max(loo) < 0) else "SIGN FLIPS"
    print(f"  {v:>16}: full {dl.mean()*100:>+6.2f}pp  LOO range [{min(loo):>+6.2f}, {max(loo):>+6.2f}]  {sgn}")
print(f"\n[written] {OUT}/basket_composition.csv, {OUT}/entry_gate_returns.csv")
