"""
Bước 2.2 (tiếp) — gate IS-only (thresholds_is_only.json) có gắn cờ 35 sự kiện độc lập
(step2) TRƯỚC thời điểm sự kiện không, và trước bao lâu?

Quan trọng: rule1 (BVPS<=0) TRÙNG với chính định nghĩa event (BVPS turn negative) -- gắn cờ ở
ĐÚNG quý event là tautological (lead=0, không phải "dự báo"). Recall thật (lead>0, cảnh báo SỚM)
chỉ có thể đến từ rule2 (leverage+EBITDA<0, sustained 2Q) hoặc rule3 (dilution) bắn ở các quý
TRƯỚC quý event. Báo cáo riêng 2 loại: (i) lead>0 "cảnh báo sớm thật" và (ii) lead=0 "phản ứng
tức thời khi BVPS đã âm" (vẫn có giá trị vận hành, nhưng không phải dự báo).
"""
import pandas as pd, numpy as np, json

BANNED_16 = {"PC1", "VVS", "KSF", "NKG", "HSG", "HVN", "VJC", "NVL", "GEG", "SBA",
             "DMC", "IMP", "TRA", "TOS", "VTP", "BAF"}

with open("thresholds_is_only.json") as f:
    TH = json.load(f)
DEQ_TH = TH["debt_eq_threshold_PRIMARY_p95"]
DIL_TH = TH["dilution_threshold_PRIMARY_p95"]

df = pd.read_csv("universe_financials_v3_intcov.csv", parse_dates=["time", "Release_Date"])
df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
df["eff_date"] = df["Release_Date"]
df.loc[df["eff_date"].isna(), "eff_date"] = df["time"] + pd.Timedelta(days=45)

df["min_oshares_12q"] = df.groupby("ticker")["OShares"].transform(lambda s: s.rolling(12, min_periods=4).min().shift(1))
df["dilution_pct"] = df["OShares"] / df["min_oshares_12q"] - 1

df["r1_negeq"] = df["BVPS"] <= 0
df["r2_combo"] = (df["Debt_Eq_P0"] > DEQ_TH) & (df["EBITDA_P0"] < 0)
df["r2_sust"] = df["r2_combo"] & df.groupby("ticker")["r2_combo"].shift(1).fillna(False)
df["r3_dilution"] = df["dilution_pct"] > DIL_TH
df["any_flag_incl_r1"] = df["r1_negeq"] | df["r2_sust"] | df["r3_dilution"]
df["early_flag_r2_or_r3"] = df["r2_sust"] | df["r3_dilution"]   # excludes tautological r1

events = pd.read_csv("independent_event_set_bvps_turn_negative.csv", parse_dates=["time", "Release_Date"])

rows = []
for _, ev in events.iterrows():
    tk = ev["ticker"]
    ev_eff = ev["Release_Date"] if pd.notna(ev["Release_Date"]) else ev["time"] + pd.Timedelta(days=45)
    hist = df[(df["ticker"] == tk) & (df["eff_date"] < ev_eff)].sort_values("eff_date")
    early_hits = hist[hist["early_flag_r2_or_r3"]]
    if len(early_hits) > 0:
        first_hit = early_hits.iloc[0]
        lead_days = (ev_eff - first_hit["eff_date"]).days
        rows.append(dict(ticker=tk, event_eff_date=ev_eff, caught="EARLY (r2/r3 before event)",
                          first_flag_eff_date=first_hit["eff_date"], lead_days=lead_days))
    else:
        # did rule1 (BVPS<=0) at least fire AT the event quarter itself (lead=0, same-quarter reaction)?
        same_q = df[(df["ticker"] == tk) & (df["eff_date"] == ev_eff)]
        r1_hit = same_q["r1_negeq"].any() if len(same_q) else False
        rows.append(dict(ticker=tk, event_eff_date=ev_eff,
                          caught="SAME-QUARTER (r1 only, lead=0)" if r1_hit else "MISSED",
                          first_flag_eff_date=ev_eff if r1_hit else pd.NaT,
                          lead_days=0 if r1_hit else np.nan))

res = pd.DataFrame(rows)
res.to_csv("recall_leadtime_results.csv", index=False)
print(res.to_string(index=False))

n = len(res)
n_early = (res["caught"] == "EARLY (r2/r3 before event)").sum()
n_same_q = (res["caught"].str.startswith("SAME-QUARTER")).sum()
n_missed = (res["caught"] == "MISSED").sum()
print(f"\nn events = {n}")
print(f"EARLY (lead>0, r2/r3 fired before BVPS-negative quarter): {n_early} ({n_early/n*100:.1f}%)")
print(f"SAME-QUARTER only (r1 fires exactly when BVPS goes negative, lead=0): {n_same_q} ({n_same_q/n*100:.1f}%)")
print(f"MISSED entirely (no flag ever, even at event quarter): {n_missed} ({n_missed/n*100:.1f}%)")
print(f"recall (EARLY+SAME-QUARTER, i.e. flagged by end of event quarter) = {(n_early+n_same_q)/n*100:.1f}%")
if n_early > 0:
    print(f"median lead_days among EARLY: {res.loc[res['caught']=='EARLY (r2/r3 before event)','lead_days'].median():.0f}")

# ---- false positive rate: of ALL tickers ever flagged (early_flag_r2_or_r3) post-2020, ex-BANNED,
#      what fraction NEVER had a BVPS-turn-negative event (or any subsequent flag escalation) within
#      2 years of the flag? ----
flag_events = df[(df["early_flag_r2_or_r3"]) & (df["eff_date"] >= "2020-01-01") & (~df["ticker"].isin(BANNED_16))].copy()
flag_first = flag_events.sort_values(["ticker", "eff_date"]).groupby("ticker").first().reset_index()
ev_lookup = events.set_index("ticker")["Release_Date"].to_dict()

def had_danger_within_2y(row):
    tk = row["ticker"]
    if tk not in ev_lookup:
        return False
    ev_date = pd.Timestamp(ev_lookup[tk])
    return row["eff_date"] <= ev_date <= row["eff_date"] + pd.Timedelta(days=730)

flag_first["true_positive"] = flag_first.apply(had_danger_within_2y, axis=1)
n_flagged_tickers = len(flag_first)
n_tp = flag_first["true_positive"].sum()
print(f"\n--- False positive rate among ALL tickers flagged by r2/r3 since 2020 (ex-BANNED-16) ---")
print(f"n distinct tickers flagged: {n_flagged_tickers}")
print(f"of which went on to a BVPS-negative event within 2y of first flag: {n_tp} ({n_tp/n_flagged_tickers*100:.1f}%)")
print(f"false positive rate (flagged, no BVPS-negative event within 2y): {(n_flagged_tickers-n_tp)/n_flagged_tickers*100:.1f}%")
flag_first.to_csv("flagged_tickers_fp_check.csv", index=False)
