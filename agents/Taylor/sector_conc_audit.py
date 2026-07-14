# -*- coding: utf-8 -*-
"""sector_conc_audit.py — Task 1+3 of job Taylor_20260714_095953 (sector-cap research).

READ-ONLY audit. Reconstructs the custom30V (yieldcombo) basket at every q2m5 rebalance
2014->now with PRODUCTION weighting (namecap 10%, no sector cap) and measures the realised
sector_code=8 (Financials+RealEstate+Brokers) weight per rebal date.

Weights are computed exactly as the production publisher does (custom30_history.py):
  base_i = mcap_i(as-of rebal date) / sum(mcap)  ->  _cap_names(base, 0.10)
so the numbers here are directly comparable to data/custom30v_8l_publish.csv.

Also prints (Task 3) the CURRENT rebal (2026-05-05) basket under:
  - baseline  : namecap only            (= production today)
  - variant A : sector-8 capped at 0.50 (existing weight_scheme='sectorcap')
  - variant B : sector-8 capped at the PIT market-cap weight of sector 8 in ticker_prune
  - variant B15: same, x1.5 (value-tilt allowance)

Sector map is POINT-IN-TIME (ICB as-of the rebal date), not latest-row.
Output: sector_conc_history.csv + stdout tables.
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sector_conc_history.csv")
START, END = "2014-01-02", "2026-06-19"
NAME_CAP, SEC_CODE = 0.10, 8

os.environ["BASKET_SELECT"] = "yieldcombo"   # custom30V = the V2.4 production parking basket

print(f"building custom30V PIT basket {START} -> {END} (production params: q2m5, gate<=3, namecap) ...")
lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                   gate_rating=3, weight_scheme="namecap")
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
bx["time"] = pd.to_datetime(bx["time"])
rebals = sorted(memdf["rebal_date"].unique())
union = sorted(memdf["ticker"].unique())

# ---- PIT sector map: ICB as-of each rebal date (not latest row -> no look-ahead) ----
inlist = ",".join(f"'{x}'" for x in union)
icb = bq(f"""SELECT t.ticker, t.time, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec
FROM tav2_bq.ticker AS t WHERE t.ticker IN ({inlist}) AND t.ICB_Code IS NOT NULL
  AND t.time <= DATE '{END}'""")
icb["time"] = pd.to_datetime(icb["time"])
icb = icb.sort_values(["ticker", "time"])
_icb_by_tk = {tk: (list(g["time"]), list(g["sec"])) for tk, g in icb.groupby("ticker")}
import bisect
def sec_asof(tk, d):
    e = _icb_by_tk.get(tk)
    if not e: return -1
    i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
    return int(e[1][i]) if i >= 0 else -1

# ---- PIT market-cap weight of sector 8 across the whole ticker_prune universe (variant B cap) ----
# mcap = Close(adj) x OShares, same definition custom_basket uses for the basket itself, so the
# basket weight and the market weight are measured on ONE consistent scale. OShares from
# ticker_financial as-of/ffilled (identical join to custom_basket.build_pit).
_reb_in = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in rebals)
mkt = bq(f"""WITH fin AS (
  SELECT f.ticker, f.time AS ftime, f.OShares,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS nft
  FROM tav2_bq.ticker_financial AS f WHERE f.OShares IS NOT NULL)
SELECT t.time, t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
       t.Close * fin.OShares AS mcap
FROM tav2_bq.ticker AS t
JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ftime AND (fin.nft IS NULL OR t.time<fin.nft)
WHERE t.time IN ({_reb_in}) AND t.ICB_Code IS NOT NULL AND t.Close IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""")
mkt["time"] = pd.to_datetime(mkt["time"])
mw = (mkt.groupby(["time", mkt["sec"] == SEC_CODE])["mcap"].sum().unstack(fill_value=0.0))
mkt_w8 = (mw[True] / (mw[True] + mw[False])).rename("mkt_w8")
n_names = mkt.groupby("time")["ticker"].nunique().rename("n_universe")

# ---- per-rebal basket weights (production recipe) ----
rows = []
picture = {}
for rd in rebals:
    rd = pd.Timestamp(rd)
    mem = memdf[memdf["rebal_date"] == rd].sort_values("liq_rank")
    tks = list(mem["ticker"])
    sub = bx[(bx["ticker"].isin(tks)) & (bx["time"] <= rd)]
    mc = sub.sort_values("time").groupby("ticker")["mcap"].last().reindex(tks).fillna(0.0)
    base = (mc / mc.sum()).values if mc.sum() > 0 else np.ones(len(tks)) / len(tks)
    sv = np.array([sec_asof(t, rd) for t in tks])
    w_base = cb._cap_names(base, NAME_CAP)                       # production
    mkw = float(mkt_w8.get(rd, np.nan))
    variants = {"baseline": w_base}
    for tag, scap in (("A_fix50", 0.50), ("B_mktcap", mkw), ("B15_mktx15", min(1.0, mkw * 1.5))):
        if not np.isfinite(scap): variants[tag] = np.full(len(tks), np.nan); continue
        w = cb._cap_sector(w_base, sv, SEC_CODE, scap)
        variants[tag] = cb._cap_names(w, NAME_CAP)
    picture[rd] = (tks, sv, variants, list(mem["rating"]), list(mem["liq_rank"]))
    r = {"rebal_date": rd.date(), "n_members": len(tks),
         "n_sec8": int((sv == SEC_CODE).sum()),
         "w8_production": float(w_base[sv == SEC_CODE].sum()),
         "mkt_w8_prune": mkw, "n_universe": int(n_names.get(rd, 0))}
    for tag in ("A_fix50", "B_mktcap", "B15_mktx15"):
        r[f"w8_{tag}"] = float(np.nansum(variants[tag][sv == SEC_CODE]))
    rows.append(r)
hist = pd.DataFrame(rows)
hist.to_csv(OUT, index=False)

print("\n=== TASK 1: sector-8 (Financials+RealEstate+Brokers) weight per q2m5 rebalance ===")
print("  w8_production = realised weight in the LIVE basket (namecap, no sector cap)")
print("  mkt_w8_prune  = PIT market-cap weight of sector 8 across ticker_prune (variant B cap)")
print(hist[["rebal_date", "n_members", "n_sec8", "w8_production", "mkt_w8_prune", "n_universe"]]
      .to_string(index=False, float_format=lambda v: f"{v:.3f}"))
print("\n-- by year (mean) --")
hist["yr"] = pd.to_datetime(hist["rebal_date"]).dt.year
print(hist.groupby("yr")[["w8_production", "mkt_w8_prune"]].mean()
      .to_string(float_format=lambda v: f"{v:.3f}"))
print(f"\nw8_production: mean {hist.w8_production.mean():.3f} | median {hist.w8_production.median():.3f} "
      f"| min {hist.w8_production.min():.3f} | max {hist.w8_production.max():.3f}")
print(f"mkt_w8_prune : mean {hist.mkt_w8_prune.mean():.3f} | median {hist.mkt_w8_prune.median():.3f} "
      f"| min {hist.mkt_w8_prune.min():.3f} | max {hist.mkt_w8_prune.max():.3f}")
print(f"rebals where production w8 > 0.50: {(hist.w8_production > 0.50).sum()}/{len(hist)}")
print(f"rebals where production w8 > mkt : {(hist.w8_production > hist.mkt_w8_prune).sum()}/{len(hist)}")

# ---- TASK 3: the CURRENT basket under each variant ----
cur = max(rebals)
tks, sv, variants, rats, lrk = picture[cur]
print(f"\n=== TASK 3: basket at CURRENT rebal {pd.Timestamp(cur).date()} under each variant ===")
tab = pd.DataFrame({"ticker": tks, "sec": sv, "rating": rats, "liq_rank": lrk,
                    **{k: v for k, v in variants.items()}})
tab = tab.sort_values("baseline", ascending=False)
print(tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
print("\n-- sector-8 totals at current rebal --")
for k in variants:
    print(f"  {k:12s}: w8 = {np.nansum(variants[k][sv == SEC_CODE]):.3f}")
print(f"  mkt_w8_prune @ {pd.Timestamp(cur).date()} = {float(mkt_w8.get(cur, np.nan)):.3f}")
print(f"\n-> {OUT}")
