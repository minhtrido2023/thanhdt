"""Diff bang rating CTL (main) vs EXP (guard) theo dedupe giong refresh_bq_table; + as-of hom nay."""
import pandas as pd, sys
O = sys.argv[1] if len(sys.argv) > 1 else "."
def dedup(p):
    d = pd.read_csv(p).sort_values(["ticker", "eff_date", "q_time"], ascending=[True, True, False])
    return d.drop_duplicates(["ticker", "eff_date"]).rename(columns={"eff_date": "time"})[["ticker","time","q_time","route","rating","tier"]]
ctl = dedup(f"{O}/rating_8l_history_CTL_main_pinicb.csv"); exp = dedup(f"{O}/rating_8l_history_EXP_guard_pinicb.csv")
fa = pd.read_csv(f"{O}/raw/fa_current_20261020.csv")
k = ["ticker", "time"]
m = ctl.merge(fa, on=k, how="outer", suffixes=("", "_fa"), indicator=True)
print("CTL vs fa_ratings_8l hien tai:", m["_merge"].value_counts().to_dict(),
      "| rating khac:", int(((m["_merge"]=="both") & (m["rating"]!=m["rating_fa"])).sum()),
      "| tier khac:", int(((m["_merge"]=="both") & (m["tier"]!=m["tier_fa"])).sum()))
d = ctl.merge(exp, on=k, how="outer", suffixes=("_ctl", "_exp"), indicator=True)
only_c = d[d["_merge"]=="left_only"]; only_e = d[d["_merge"]=="right_only"]
both_chg = d[(d["_merge"]=="both") & ((d["rating_ctl"]!=d["rating_exp"]) | (d["tier_ctl"]!=d["tier_exp"]) | (d["q_time_ctl"]!=d["q_time_exp"]))]
print(f"dong dedupe: CTL {len(ctl)} EXP {len(exp)} | chi CTL {len(only_c)} | chi EXP {len(only_e)} | cung (ticker,time) doi noi dung {len(both_chg)}")
cols = ["ticker","time","q_time_ctl","rating_ctl","tier_ctl","q_time_exp","rating_exp","tier_exp","_merge"]
chg = pd.concat([only_c, only_e, both_chg]).sort_values(["ticker","time"])[cols]
chg.to_csv(f"{O}/out_dedup_row_diff_pinicb.csv", index=False); print(chg.to_string(index=False))
# as-of theo ngay: rating co hieu luc tung ngay 2025-10-01..2026-10-20, so CTL vs EXP
days = pd.date_range("2025-10-01", "2026-10-20")
tk = sorted(set(chg["ticker"]))
rows = []
for t in tk:
    for name, tab in (("ctl", ctl), ("exp", exp)):
        s = tab[tab["ticker"]==t].assign(time=lambda x: pd.to_datetime(x["time"])).sort_values("time")
        a = pd.merge_asof(pd.DataFrame({"day": days}), s[["time","rating","tier","q_time"]], left_on="day", right_on="time")
        a["ticker"] = t; a["leg"] = name; rows.append(a)
A = pd.concat(rows).pivot_table(index=["ticker","day"], columns="leg", values=["rating","q_time"], aggfunc="first")
A.columns = [f"{a}_{b}" for a, b in A.columns]; A = A.reset_index()
dif = A[(A["rating_ctl"]!=A["rating_exp"]) | (A["q_time_ctl"]!=A["q_time_exp"])]
seg = (dif.assign(g=(dif["day"].diff()!=pd.Timedelta(days=1)) | (dif["ticker"]!=dif["ticker"].shift())).assign(g=lambda x: x["g"].cumsum())
          .groupby(["ticker","g"]).agg(start=("day","min"), end=("day","max"), days=("day","size"),
                                       rating_ctl=("rating_ctl","first"), rating_exp=("rating_exp","first"),
                                       q_ctl=("q_time_ctl","first"), q_exp=("q_time_exp","first")).reset_index().drop(columns="g"))
seg["gate_flip_le3"] = (seg["rating_ctl"]<=3) != (seg["rating_exp"]<=3)
seg.to_csv(f"{O}/out_asof_diff_segments_pinicb.csv", index=False)
print("\nDoan ngay as-of khac (2025-10-01..2026-10-20):"); print(seg.to_string(index=False))
today = A[A["day"]==pd.Timestamp("2026-10-20")]
print("\nAs-of 2026-10-20 khac:", int(((today["rating_ctl"]!=today["rating_exp"])|(today["q_time_ctl"]!=today["q_time_exp"])).sum()), "ma")
