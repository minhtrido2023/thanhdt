"""
LBC (Liquidity Burst post Catalyst) pattern scan — dispatch Taylor_20260826_120750.
Reads local CSVs pulled from BQ (tav2_bq.ticker, tav2_bq.corporate_action,
tav2_bq.ticker_financial, tav2_mike.universe_pit) and detects:
  accumulation (ADV_3M < 2B VND, >=6 consecutive months, universe-filtered at catalyst)
  -> catalyst (corp-action bonus/stock-dividend ratio>=0.5, OR earnings-surge quarter)
  -> burst (ADV_3M >= 3x catalyst-month ADV AND > 2B, within 3 months of catalyst)
Outputs: lbc_events.csv (one row per detected event) + printed summary.
"""
import pandas as pd
import numpy as np

BASE = "mike/agents/Taylor/research/liquidity_burst_pattern_20260826/"

adv = pd.read_csv(BASE + "universe_adv_monthly.csv", parse_dates=["month_end", "last_trading_day"])
uni = pd.read_csv(BASE + "universe_pit_monthly.csv", parse_dates=["month_end"])
corp = pd.read_csv(BASE + "catalyst_corp_action.csv", parse_dates=["exright_date", "public_date"])
fin = pd.read_csv(BASE + "quarterly_financials.csv", parse_dates=["time", "Release_Date"])

adv = adv.dropna(subset=["adv_3m_vnd"]).sort_values(["ticker", "month_end"]).reset_index(drop=True)
uni_map = uni.set_index(["ticker", "month_end"])["in_universe"].to_dict()

THRESH = 2e9
MIN_ACCUM_MONTHS = 6
BURST_MULT = 3.0

# ---- 1. accumulation runs per ticker ----
runs = []
for tkr, g in adv.groupby("ticker"):
    g = g.sort_values("month_end").reset_index(drop=True)
    below = g["adv_3m_vnd"] < THRESH
    run_id = (below != below.shift()).cumsum()
    for rid, seg in g.groupby(run_id):
        if not below.loc[seg.index[0]]:
            continue
        if len(seg) >= MIN_ACCUM_MONTHS:
            runs.append({
                "ticker": tkr,
                "accum_start": seg["month_end"].iloc[0],
                "accum_end": seg["month_end"].iloc[-1],
                "accum_months": len(seg),
                "accum_min_adv": seg["adv_3m_vnd"].min(),
            })
runs = pd.DataFrame(runs)
print(f"Accumulation runs (>=6mo, ADV<2B): {len(runs)} across {runs['ticker'].nunique() if len(runs) else 0} tickers")

# ---- 2. catalyst candidates ----
# 2a. corp-action bonus/stock-dividend
corp["cat_month"] = corp["exright_date"].dt.to_period("M").dt.to_timestamp()
corp_cat = corp[["ticker", "cat_month", "exright_date", "issue_method_name_vi", "exercise_ratio"]].copy()
corp_cat["cat_type"] = "corp_action"

# 2b. earnings-surge: NP_P0 > 1.5x max(NP_P1..P4), NP_P0>0, revenue YoY > 15%
fin_sorted = fin.sort_values(["ticker", "time"])
prior_max = fin_sorted.groupby("ticker")[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].apply(
    lambda d: d.max(axis=1)
).reset_index(level=0, drop=True)
fin_sorted["prior_max_np"] = prior_max
surge_mask = (
    (fin_sorted["NP_P0"] > 0)
    & (fin_sorted["prior_max_np"] > 0)
    & (fin_sorted["NP_P0"] > 1.5 * fin_sorted["prior_max_np"])
    & (fin_sorted["Revenue_YoY_P0"] > 0.15)
)
earn_cat = fin_sorted.loc[surge_mask, ["ticker", "Release_Date"]].copy()
earn_cat["cat_month"] = earn_cat["Release_Date"].dt.to_period("M").dt.to_timestamp()
earn_cat = earn_cat.rename(columns={"Release_Date": "exright_date"})
earn_cat["issue_method_name_vi"] = "earnings_surge"
earn_cat["exercise_ratio"] = np.nan
earn_cat["cat_type"] = "earnings"

catalysts = pd.concat([corp_cat, earn_cat[["ticker", "cat_month", "exright_date", "issue_method_name_vi", "exercise_ratio", "cat_type"]]], ignore_index=True)
print(f"Catalyst candidates: {len(catalysts)} ({(catalysts.cat_type=='corp_action').sum()} corp_action, {(catalysts.cat_type=='earnings').sum()} earnings)")

# ---- 3. match catalyst to accumulation run: catalyst falls in [accum_start, accum_end + 3mo] ----
adv_idx = adv.set_index(["ticker", "month_end"])["adv_3m_vnd"]
events = []
for _, r in runs.iterrows():
    tkr = r["ticker"]
    window_end = r["accum_end"] + pd.DateOffset(months=3)
    cands = catalysts[(catalysts["ticker"] == tkr) & (catalysts["cat_month"] >= r["accum_start"]) & (catalysts["cat_month"] <= window_end)]
    for _, c in cands.iterrows():
        cat_month = c["cat_month"]
        if (tkr, cat_month) not in adv_idx.index:
            continue
        adv_at_cat = adv_idx.loc[(tkr, cat_month)]
        burst_month = cat_month + pd.DateOffset(months=3)
        # find nearest available month <= burst_month+1 within ticker's series (handle listing gaps)
        tser = adv[(adv.ticker == tkr) & (adv.month_end >= cat_month) & (adv.month_end <= burst_month + pd.DateOffset(months=1))]
        if tser.empty:
            continue
        max_adv_post = tser["adv_3m_vnd"].max()
        burst_ok = (max_adv_post >= BURST_MULT * max(adv_at_cat, 1)) and (max_adv_post > THRESH)
        if not burst_ok:
            continue
        in_uni_cat = uni_map.get((tkr, cat_month), False)
        in_uni_burst = uni_map.get((tkr, tser.loc[tser["adv_3m_vnd"].idxmax(), "month_end"]), False)
        events.append({
            "ticker": tkr, "accum_start": r["accum_start"], "accum_end": r["accum_end"],
            "accum_months": r["accum_months"], "accum_min_adv": r["accum_min_adv"],
            "cat_type": c["cat_type"], "cat_detail": c["issue_method_name_vi"], "cat_ratio": c["exercise_ratio"],
            "cat_date": c["exright_date"], "cat_month": cat_month, "adv_at_cat": adv_at_cat,
            "burst_max_adv": max_adv_post, "burst_month": tser.loc[tser["adv_3m_vnd"].idxmax(), "month_end"],
            "burst_multiple": max_adv_post / max(adv_at_cat, 1),
            "in_universe_at_catalyst": in_uni_cat, "in_universe_at_burst": in_uni_burst,
        })

ev = pd.DataFrame(events)
print(f"\nRaw LBC events (accum->catalyst->burst, before universe filter): {len(ev)}")
if len(ev):
    ev_uni = ev[ev["in_universe_at_catalyst"] | ev["in_universe_at_burst"]].copy()
    print(f"LBC events with in_universe=True at catalyst OR burst: {len(ev_uni)} across {ev_uni['ticker'].nunique()} tickers")
    ev_uni = ev_uni.sort_values(["ticker", "cat_month"])
    ev_uni.to_csv(BASE + "lbc_events.csv", index=False)
    print("\n--- by cat_type ---")
    print(ev_uni["cat_type"].value_counts())
    print("\n--- by year ---")
    print(ev_uni["cat_month"].dt.year.value_counts().sort_index())
else:
    print("No events found.")
