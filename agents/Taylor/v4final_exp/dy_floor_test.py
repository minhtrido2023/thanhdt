# -*- coding: utf-8 -*-
"""dy_floor_test.py — is dividend yield a DOWNSIDE FLOOR (not a return predictor)?
Job Taylor_20260714_140127. Research-only.

The user's claim is ASYMMETRIC and must be tested as such:
  "DY cao không cho biết tăng giá đến đâu, nhưng làm ngưỡng chặn khó giảm sâu hơn."
So the test is NOT IC(DY, forward return) — that tests a claim nobody made, and answering the wrong
question is exactly the methodological error this whole day's research chain has been about.

Claim is SUPPORTED only if, high-DY vs low-DY, in the same route and quarter:
  (a) forward DOWNSIDE is materially and significantly shallower, AND
  (b) forward MEAN RETURN is NOT materially better.
(b) matters as much as (a): if high-DY also returns more, DY is just a return predictor wearing a
floor costume — and a return predictor belongs on the ranking axis, not in a floor rule.

CONFOUND, controlled explicitly: DY and 1/PE are both cheapness. An unconditional DY effect could be
the value effect the selector ALREADY ranks on. So every measure is also reported DOUBLE-SORTED
within ey tertile, and separately on the marginal cohort (ranks ~20-45) where a tie-breaker would
actually act — the only cohort where the answer changes any decision.

Primary downside metric = worst point loss for a buyer at the obs date, min(Close)/Close_0 - 1 over
the next h sessions. That is what "a floor under the price" means to someone holding the name.
Adjusted Close throughout -> the dividend itself is already IN the path, so a high-DY name cannot
score a shallower drawdown merely by paying the dividend. DY denominator = unadjusted Price (the
real market price a real yield is quoted against).

Run: $DNA_PYEXE mike/agents/Taylor/v4final_exp/dy_floor_test.py
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402

OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "v4final_exp")
START, END = "2014-01-02", "2026-06-19"
POOL_N = 60           # same tradability pool the selector cuts from
HORIZONS = {"3M": 63, "6M": 126}

# ---------------------------------------------------------------- obs dates (q2m5, as the selector)
cal = bq(f"""SELECT DISTINCT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX'
  AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time""")
cal["time"] = pd.to_datetime(cal["time"])
days = np.array(sorted(cal["time"]), dtype="datetime64[ns]")
obs_dates = []
for Y in range(2014, 2027):
    for mo in (2, 5, 8, 11):
        i = int(np.searchsorted(days, np.datetime64(pd.Timestamp(Y, mo, 5)), side="left"))
        if i < len(days):
            d = pd.Timestamp(days[i])
            if pd.Timestamp(START) <= d <= pd.Timestamp(END):
                obs_dates.append(d)
obs_dates = sorted(set(obs_dates))
print(f"obs dates (q2m5): {len(obs_dates)}  {obs_dates[0].date()} → {obs_dates[-1].date()}")

# ---------------------------------------------------------------- pool = top-60 prior-quarter liquidity
qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*t.Close) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND t.ICB_Code IS NOT NULL
  AND t.time >= DATE_SUB(DATE '{START}', INTERVAL 380 DAY) AND t.time <= DATE '{END}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")

# rating gate <=3, as-of (identical semantics to custom_basket.rating_asof)
rat = bq(f"""SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r
WHERE r.time <= DATE '{END}' ORDER BY r.ticker, r.time""")
rat["time"] = pd.to_datetime(rat["time"])
rat_by_tk = {tk: (list(g["time"]), list(g["rating"])) for tk, g in rat.groupby("ticker")}


def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e:
        return np.nan
    import bisect
    i = bisect.bisect_right(e[0], d) - 1
    return float(e[1][i]) if i >= 0 else np.nan


# ---------------------------------------------------------------- DY (as-of Release_Date) + prices
div = bq(f"""SELECT f.ticker, f.time, f.Release_Date, f.Dividend_Min3Y
FROM tav2_bq.ticker_financial f WHERE f.time <= DATE '{END}' AND f.Dividend_Min3Y IS NOT NULL""")
div["eff"] = pd.to_datetime(div["Release_Date"]).fillna(pd.to_datetime(div["time"]) + pd.Timedelta(days=45))
div = div.sort_values("eff")
div_by_tk = {tk: (list(g["eff"]), list(g["Dividend_Min3Y"])) for tk, g in div.groupby("ticker")}


def div_asof(tk, d):
    e = div_by_tk.get(tk)
    if not e:
        return np.nan
    import bisect
    i = bisect.bisect_right(e[0], d) - 1
    return float(e[1][i]) if i >= 0 else np.nan


px = bq(f"""SELECT t.ticker, t.time, t.Close, t.Price, t.PE FROM tav2_bq.ticker t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
  AND t.time BETWEEN DATE '{START}' AND DATE_ADD(DATE '{END}', INTERVAL 200 DAY)
  AND t.Close IS NOT NULL""")
px["time"] = pd.to_datetime(px["time"])
close = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()
price = px.pivot_table(index="time", columns="ticker", values="Price").sort_index()
pe = px.pivot_table(index="time", columns="ticker", values="PE").sort_index()
print(f"price panel: {close.shape[0]} sessions x {close.shape[1]} tickers")

PANEL = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"),
                    usecols=["ticker", "time", "route"], parse_dates=["time"])
PANEL["qstart"] = PANEL["time"].dt.to_period("Q").dt.start_time
ROUTE_TQ = (PANEL.dropna(subset=["route"]).sort_values("time")
            .groupby(["ticker", "qstart"])["route"].last().to_dict())
ROUTE_LAST = PANEL.dropna(subset=["route"]).sort_values("time").groupby("ticker")["route"].last().to_dict()

# ---------------------------------------------------------------- build the observation panel
rows = []
cl_idx = close.index
for d in obs_dates:
    qd = pd.Timestamp(d).to_period("Q").start_time
    prior = [q for q in liq_piv.index if q < qd]
    if not prior:
        continue
    src_q = max(prior)
    lr = liq_piv.loc[src_q].dropna().sort_values(ascending=False)
    pool = [tk for tk in lr.index if (lambda r: pd.notna(r) and r <= 3)(rating_asof(tk, d))][:POOL_N]
    if d not in cl_idx:
        continue
    i0 = cl_idx.get_loc(d)
    for tk in pool:
        if tk not in close.columns:
            continue
        c0 = close.at[d, tk]
        p0 = price.at[d, tk] if tk in price.columns else np.nan
        dv = div_asof(tk, d)
        pe0 = pe.at[d, tk] if tk in pe.columns else np.nan
        if not (pd.notna(c0) and c0 > 0 and pd.notna(p0) and p0 > 0 and pd.notna(dv)):
            continue
        rec = {"date": d, "src_q": src_q, "ticker": tk,
               "route": ROUTE_TQ.get((tk, src_q), ROUTE_LAST.get(tk, "?")),
               "dy": dv / p0,
               "ey": (1.0 / pe0) if (pd.notna(pe0) and pe0 > 0) else np.nan}
        ok = False
        for hname, h in HORIZONS.items():
            path = close.iloc[i0 + 1: i0 + 1 + h][tk].dropna()
            if len(path) < h * 0.6:      # need most of the window to exist
                rec[f"maxloss_{hname}"] = np.nan
                rec[f"ret_{hname}"] = np.nan
                continue
            rec[f"maxloss_{hname}"] = float(path.min() / c0 - 1.0)
            rec[f"ret_{hname}"] = float(path.iloc[-1] / c0 - 1.0)
            ok = True
        if ok:
            rows.append(rec)

P = pd.DataFrame(rows)
P.to_csv(os.path.join(OUT, "dy_floor_panel.csv"), index=False)
print(f"panel: {len(P)} obs, {P.ticker.nunique()} tickers, {P.date.nunique()} dates, "
      f"DY>0 on {(P.dy > 0).mean():.1%}")


def tertile(s):
    """Within-group tertile label; needs >=6 names to be meaningful."""
    if s.notna().sum() < 6:
        return pd.Series(np.nan, index=s.index)
    try:
        return pd.qcut(s.rank(method="first"), 3, labels=["LOW", "MID", "HIGH"])
    except ValueError:
        return pd.Series(np.nan, index=s.index)


def report(df, label, by):
    """HIGH-vs-LOW DY within `by` groups: downside + return, with the asymmetry verdict."""
    d = df.copy()
    d["dy_t"] = d.groupby(by, observed=True)["dy"].transform(tertile)
    d = d[d.dy_t.isin(["LOW", "HIGH"])]
    out = []
    for h in HORIZONS:
        c = d.dropna(subset=[f"maxloss_{h}"])
        if len(c) < 50:
            continue
        hi = c[c.dy_t == "HIGH"]
        lo = c[c.dy_t == "LOW"]
        ml_t = stats.ttest_ind(hi[f"maxloss_{h}"], lo[f"maxloss_{h}"], equal_var=False)
        rt_t = stats.ttest_ind(hi[f"ret_{h}"], lo[f"ret_{h}"], equal_var=False)
        # per-date paired view: does HIGH have shallower downside on most dates? (t-stat above
        # pools overlapping windows and correlated names -> its t is optimistic; the hit rate is not)
        pq = c.groupby("date").apply(
            lambda g: (g[g.dy_t == "HIGH"][f"maxloss_{h}"].mean()
                       - g[g.dy_t == "LOW"][f"maxloss_{h}"].mean()), include_groups=False).dropna()
        out.append({
            "label": label, "h": h, "n_hi": len(hi), "n_lo": len(lo),
            "maxloss_HIGH": hi[f"maxloss_{h}"].mean() * 100,
            "maxloss_LOW": lo[f"maxloss_{h}"].mean() * 100,
            "d_maxloss_pp": (hi[f"maxloss_{h}"].mean() - lo[f"maxloss_{h}"].mean()) * 100,
            "t_maxloss": ml_t.statistic,
            "hit_dates": float((pq > 0).mean()), "n_dates": len(pq),
            "ret_HIGH": hi[f"ret_{h}"].mean() * 100, "ret_LOW": lo[f"ret_{h}"].mean() * 100,
            "d_ret_pp": (hi[f"ret_{h}"].mean() - lo[f"ret_{h}"].mean()) * 100,
            "t_ret": rt_t.statistic,
        })
    return pd.DataFrame(out)


print("\n" + "=" * 100)
print("HIGH-DY vs LOW-DY tertile — d_maxloss_pp > 0 means HIGH-DY falls LESS (floor claim supported)")
print("=" * 100)

res = []
# (1) unconditional, within route x quarter
res.append(report(P, "route×date", ["date", "route"]))
# (2) value-controlled: within route x quarter x ey tertile — strips the "DY is just cheapness" story
P2 = P.copy()
P2["ey_t"] = P2.groupby(["date", "route"], observed=True)["ey"].transform(tertile)
res.append(report(P2.dropna(subset=["ey_t"]), "route×date×ey-tertile", ["date", "route", "ey_t"]))
# (3) the cohort a tie-breaker would actually touch: ranks 20-45 by ey within the pool
P3 = P.copy()
P3["ey_rank"] = P3.groupby("date")["ey"].rank(ascending=False, method="first")
P3 = P3[(P3.ey_rank >= 20) & (P3.ey_rank <= 45)]
res.append(report(P3, "marginal cohort (ey rank 20-45)", ["date"]))

R = pd.concat(res, ignore_index=True)
R.to_csv(os.path.join(OUT, "dy_floor_results.csv"), index=False)
pd.set_option("display.width", 220, "display.max_columns", 30)
print(R.round(3).to_string(index=False))

print("\n" + "=" * 100)
print("VERDICT LOGIC — claim needs: downside shallower (d_maxloss_pp > 0, significant, hit>~0.55)")
print("                AND return NOT better (|d_ret_pp| small / not significant)")
print("=" * 100)
for _, r in R.iterrows():
    floor_ok = (r.d_maxloss_pp > 0) and (abs(r.t_maxloss) > 2) and (r.hit_dates > 0.55)
    ret_flat = abs(r.t_ret) < 2
    verdict = ("FLOOR (supported)" if floor_ok and ret_flat else
               "RETURN-PREDICTOR (not a floor)" if floor_ok and not ret_flat else
               "NO FLOOR EFFECT")
    print(f"  {r.label:34s} {r.h}: d_maxloss {r.d_maxloss_pp:+6.2f}pp (t={r.t_maxloss:+5.2f}, "
          f"hit {r.hit_dates:.0%}) | d_ret {r.d_ret_pp:+6.2f}pp (t={r.t_ret:+5.2f}) → {verdict}")
print(f"\nartifacts: {OUT}/dy_floor_panel.csv, dy_floor_results.csv")
