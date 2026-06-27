"""DRI Q3-2026 NP — VOLUME-BUDGET model (user insight: annual volume is the stable anchor; quarterly swings
= inventory/timing, e.g. Q1-2026 destock spike. Total annual volume hard to change much).

Method:
 1) implied_vol_q = Revenue_q / RSS3_price_q  (volume index; DRI sell-price tracks RSS3, FX/grade absorbed in level)
 2) annual implied_vol per year -> check stability + growth trend (validates the user premise)
 3) seasonal share s_q = implied_vol_q / annual_vol (historical mean per quarter)
 4) 2026 forecast: annual_2026 = annual_2025 * (1+g); remainder = annual_2026 - H1_actual(Q1+Q2);
    Q3_vol = remainder * s_Q3/(s_Q3+s_Q4)  -> if Q1 over-sold, H2 budget shrinks (the inventory mean-reversion)
 5) Q3 NP = Q3_vol * price_Q3 * NPM_recent ; cross-check Q3 Rev = Q3_vol*price_Q3.
Price (RSS3) from data/rubber_monthly.csv; DRI Rev/NP/NPM from BQ. Honest: implied-vol is a proxy (price-grade/FX),
NPM assumed stable; n small.
"""
import duckdb, numpy as np, pandas as pd
c = duckdb.connect()
m = pd.read_csv("data/rubber_monthly.csv"); m["q"] = pd.PeriodIndex(m["month"], freq="M").asfreq("Q")
rss3 = m.groupby("q")["price"].mean()
d = c.execute("""SELECT quarter, NP_P0/1e9 NP, Revenue_P0/1e9 Rev, NPM_P0 NPM
  FROM read_parquet('data/bq_cache/ticker_financial.parquet') WHERE ticker='DRI' AND Revenue_P0 IS NOT NULL ORDER BY time""").df()
d["q"] = d["quarter"].apply(lambda s: pd.Period(year=int(s[:4]), quarter=int(s[-1]), freq="Q"))
d = d.set_index("q"); d["price"] = rss3.reindex(d.index).values
d["impvol"] = d["Rev"]/d["price"]; d["yr"] = d.index.year; d["qn"] = d.index.quarter

# (2) annual implied volume — is it stable? (user premise)
ann = d.groupby("yr")["impvol"].sum()
print("=== annual implied volume (Revenue/price), 'stable anchor' check ===")
print(ann.round(1).to_string()); print(f"  YoY growth recent: 2024->2025 = {ann.get(2025,np.nan)/ann.get(2024,np.nan)-1:+.1%}")
# (3) seasonal shares (use full-year years only, 2018-2025)
full = d[d["yr"].between(2018,2025)]
sh = full.groupby("qn")["impvol"].sum(); sh = sh/sh.sum()
print(f"\nseasonal vol share Q1/Q2/Q3/Q4: {sh.round(3).to_dict()}")
npm_recent = d[d["yr"]>=2024]["NPM"].mean()
print(f"recent NPM (2024+): {npm_recent:.3f}")

# (4) 2026 forecast
q1 = d.loc[pd.Period('2026Q1','Q')]                       # only Q1'26 reported so far
ann_anchor3 = ann.loc[2023:2025].mean()                   # robust anchor (3yr avg, less noisy than 2025 alone)
priceQ3 = 2.73                                             # Q3'26 spot
sh_rest = sh[2]+sh[3]+sh[4]                                # Q2+Q3+Q4 share (Q1 already actual)
print(f"\n2026: Q1 actual impvol={q1['impvol']:.1f} (Rev {q1['Rev']:.0f}@{q1['price']:.2f}); Q2'26 NOT yet reported.")
print(f"annual anchor: 2025={ann[2025]:.0f} | 3yr-avg(23-25)={ann_anchor3:.0f}  (NOTE 2024->25 +52% = proxy is NOISY)")
print(f"\n=== DRI Q3'26 NP — volume-budget (Q3 = (annual_budget - Q1) * Q3share/(Q2+Q3+Q4 share)) ===")
print(f"{'anchor':>14} {'ann26':>7} {'rem(Q2-4)':>9} {'Q3vol':>6} {'Q3Rev':>6} {'Q3NP':>5}")
for lab, base in [("2025x1.05", ann[2025]*1.05), ("3yr-avg x1.05", ann_anchor3*1.05), ("3yr-avg x1.0", ann_anchor3)]:
    rem = base - q1["impvol"]; q3v = rem * sh[3]/sh_rest
    q3rev = q3v*priceQ3; q3np = q3rev*npm_recent
    print(f"{lab:>14} {base:>7.0f} {rem:>9.0f} {q3v:>6.0f} {q3rev:>6.0f} {q3np:>5.0f}")
print(f"\nvs price+seasonal model ~42B | Q3'25 actual 39B. NPM={npm_recent:.2f}.")
print("HONEST: implied-vol (Rev/RSS3) swings +52% 2024->25 = too noisy to be a clean volume anchor (DRI realized")
print("price != RSS3 + FX + grade). Need DRI PHYSICAL tons/qtr (Winston/company) for a real volume model.")
