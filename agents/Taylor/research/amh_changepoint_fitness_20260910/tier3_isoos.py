"""
AMH #4, TIER 3 — the decision-relevant cut for the VPI/BAL review 2026-09-16.

Tier 1/2 showed momentum's whole edge sits in NEUTRAL. The question that actually matters is
whether that NEUTRAL edge SURVIVES out-of-sample, or whether the whole "NEUTRAL is momentum's
habitat" result is an IS(2014-19) artifact. Same harness, same PIT axes as fitness2.py.
"""
import numpy as np, pandas as pd
import fitness2 as F

df, meta = F.load()
IS_END = "2019-12-31"
rows = []
for col, label in F.SIGNALS.items():
    s0 = F.series_by_month(df, col, 0)
    sign = np.sign(s0["ic"].mean()) or 1
    s = F.series_by_month(df, col, sign).join(
        meta.set_index("form_dt")[["state", "terc"]], how="inner")
    for split, sub0 in (("IS_2014_19", s[s.index <= IS_END]), ("OOS_2020p", s[s.index > IS_END])):
        for scope, sub in ([("ALL", sub0), ("NEUTRAL", sub0[sub0.state == 3])] +
                           [(f"NEUTRAL/{F.TERC_LBL[t]}", sub0[(sub0.state == 3) & (sub0.terc == t)])
                            for t in (0, 1, 2)] +
                           [(f"{F.TERC_LBL[t]}", sub0[sub0.terc == t]) for t in (0, 1, 2)]):
            r = F.cell_stats(sub)
            if r:
                rows.append(dict(signal=col, label=label, split=split, scope=scope, **r))
R = pd.DataFrame(rows)
R.round(4).to_csv(F.OUT + "/fitness2_tier3_isoos.csv", index=False)

print("=" * 104)
print("TIER 3 — does the conditional edge SURVIVE OOS?  mean fwd-3M IC (n_months) · * = |t_NW|>=2")
print("          '--' = n<10 (not reported).  '?' = 10<=n<18 (reported, NOT conclusion-grade).")
print("=" * 104)
order = ["ALL", "NEUTRAL", "NEUTRAL/B-LOW", "NEUTRAL/B-MID", "NEUTRAL/B-HIGH",
         "B-LOW", "B-MID", "B-HIGH"]
for split in ("IS_2014_19", "OOS_2020p"):
    print(f"\n--- {split} ---")
    out = {}
    for sc in order:
        out[sc] = {}
        for lbl in R.label.unique():
            q = R[(R.split == split) & (R.scope == sc) & (R.label == lbl)]
            if q.empty or q.n_months.iloc[0] < F.MIN_M_REPORT:
                out[sc][lbl] = "     --     "
            else:
                v, n, t = q.mean_ic.iloc[0], int(q.n_months.iloc[0]), q.t_nw.iloc[0]
                star = "*" if (pd.notna(t) and abs(t) >= 2) else " "
                out[sc][lbl] = f"{v:+.3f}{star}{'' if n >= F.MIN_M_CONCLUDE else '?'} n{n:<3d}"
    print(pd.DataFrame(out)[order].to_string())

print("\n" + "=" * 104)
print("MOMENTUM VERDICT TABLE (mom_200 + D_RSI), IS vs OOS side by side")
print("=" * 104)
mv = R[R.signal.isin(["mom_200", "D_RSI"])].pivot_table(
    index=["signal", "scope"], columns="split",
    values=["mean_ic", "n_months", "t_nw"])
mv = mv.reindex(index=pd.MultiIndex.from_product([["mom_200", "D_RSI"], order],
                                                 names=["signal", "scope"]))
print(mv.round(3).to_string())
