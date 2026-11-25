# -*- coding: utf-8 -*-
"""p5_interaction.py — POST-HOC (sau skeptic, job Taylor_20261125_114526). KHÔNG đổi số pilot đã khoá.
Phép thử TƯƠNG TÁC (diff-in-diff) của bốn ô: DiD = (rẻ,cao − rẻ,thấp) − (đắt,cao − đắt,thấp), trên y đã khử trung bình tháng.
Hai trục 'thừa nhận': (F) = thành phần hành vi `beh` của mô hình F (pilot_pred_h*.parquet); (hi52) = hạng hi52 trong tháng (không ước lượng).
CI: t(n-1) trên trung bình THEO NĂM as-of (n = số năm, 5-6 cụm) — KHÔNG phải bootstrap dòng. Bản 'một tháng mỗi năm' (không chồng lấn nhãn 12T): với
mỗi tháng lịch m=1..12, chuỗi DiD của m qua các năm; báo CI rộng nhất. Out: ../out/interaction.json, interaction.md
Env: LABEL (h50|h0|h100), TAG."""
import os, json
import numpy as np, pandas as pd
from scipy import stats
WC = "/home/trido/thanhdt/WorkingClaude"; HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
LABEL = os.environ.get("LABEL", "h50"); TAG = os.environ.get("TAG", "")
ft = pd.read_parquet(os.path.join(OUT, "feat.parquet"), columns=["ticker", "ym", "hi52"])
res = {"label": LABEL}; md = []

def tci(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float); n = len(v)
    if n < 3: return None
    se = v.std(ddof=1) / np.sqrt(n); t = stats.t.ppf(0.975, n - 1)
    return {"mean": float(v.mean()), "lo": float(v.mean() - t * se), "hi": float(v.mean() + t * se), "n_y": n, "t": float(v.mean() / se) if se > 0 else None}

def cells(g, ax):                                                     # g: một tháng as-of; ax: cột thừa nhận
    hi = g[ax] >= g[ax].median(); ch = g.r_lv_ENS2 >= 0; out = {}
    for nm, m in (("re_cao", ch & hi), ("re_thap", ch & ~hi), ("dat_cao", ~ch & hi), ("dat_thap", ~ch & ~hi)):
        out[nm] = g.ydm[m].mean() if m.sum() >= 5 else np.nan
    out["did"] = (out["re_cao"] - out["re_thap"]) - (out["dat_cao"] - out["dat_thap"])
    out["main_re"] = out["re_cao"] - out["re_thap"]; out["main_dat"] = out["dat_cao"] - out["dat_thap"]
    out["n_dat_cao"] = int(((~ch) & hi).sum()); return out

for h in (12, 24):
    P = pd.read_parquet(os.path.join(OUT, f"pilot_pred_h{h}{TAG}.parquet")).merge(ft, on=["ticker", "ym"], how="left")
    P["r_hi52"] = P.groupby("mi").hi52.rank(pct=True)                 # hạng trong mẫu có nhãn của tháng (xấp xỉ pilot: hạng trên mẫu lõi; ghi nhận)
    for era in ("IS", "OOS"):
        E = P[P.era == era]; per = {}
        for axn, col in (("F_behaviour", "beh"), ("hi52", "r_hi52")):
            rows = []
            for mi, g in E.dropna(subset=[col]).groupby("mi"):
                c = cells(g, col); c.update(mi=mi, year=mi // 12, mon=mi % 12 + 1); rows.append(c)
            T = pd.DataFrame(rows); r = {}
            ym_ = T.groupby("year")[["did", "main_re", "main_dat", "re_cao", "re_thap", "dat_cao", "dat_thap"]].mean()
            r["per_year"] = {int(y): {k: round(float(v), 4) for k, v in row.items()} for y, row in ym_.iterrows()}
            r["all_months_year_t"] = {k: tci(ym_[k].values) for k in ("did", "main_re", "main_dat", "re_cao", "re_thap", "dat_cao", "dat_thap")}
            one = {}
            for m in range(1, 13):
                s = T[T.mon == m].groupby("year").did.mean(); one[m] = tci(s.values)
            ok = {m: v for m, v in one.items() if v}
            r["one_month_per_year"] = {m: (None if not v else {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()}) for m, v in one.items()}
            if ok:
                wid = max(ok, key=lambda m: ok[m]["hi"] - ok[m]["lo"]); r["widest_month"] = {"month": wid, **ok[wid]}
                r["share_months_ci_excl0"] = float(np.mean([(v["lo"] > 0) or (v["hi"] < 0) for v in ok.values()]))
                r["share_months_pos"] = float(np.mean([v["mean"] > 0 for v in ok.values()]))
            r["n_dat_cao_mean_per_month"] = float(T.n_dat_cao.mean()); r["n_years"] = int(T.year.nunique()); r["n_months"] = int(len(T))
            per[axn] = r
            a = r["all_months_year_t"]["did"]; w = r.get("widest_month")
            md.append(f"| h={h} | {era} | {axn} | DiD {a['mean']:+.4f} [{a['lo']:+.4f}; {a['hi']:+.4f}] t={a['t']:+.2f} n_y={a['n_y']} | "
                      + (f"tháng {w['month']}: {w['mean']:+.4f} [{w['lo']:+.4f}; {w['hi']:+.4f}] | {r['share_months_ci_excl0']:.2f} / {r['share_months_pos']:.2f} |" if w else "— | — |"))
        res[f"h{h}_{era}"] = per
json.dump(res, open(os.path.join(OUT, f"interaction{TAG}.json"), "w"), indent=1, ensure_ascii=False)
open(os.path.join(OUT, f"interaction{TAG}.md"), "w").write(
    "POST-HOC (sau skeptic). DiD = (rẻ,cao−rẻ,thấp) − (đắt,cao−đắt,thấp); CI t(n−1) trên trung bình theo năm.\n\n"
    "| h | era | trục | DiD mọi tháng [CI t theo năm] | bản 1 tháng/năm: tháng CI RỘNG NHẤT | tỉ lệ 12 tháng lịch có CI không chứa 0 / có dấu dương |\n|---|---|---|---|---|---|\n" + "\n".join(md) + "\n")
print(open(os.path.join(OUT, f"interaction{TAG}.md")).read())
for k in res:
    if k == "label": continue
    for axn, r in res[k].items():
        a = r["all_months_year_t"]
        print(k, axn, "main_re", {x: round(a["main_re"][x], 4) for x in ("mean", "lo", "hi")}, "main_dat", {x: round(a["main_dat"][x], 4) for x in ("mean", "lo", "hi")},
              "cells", {c: round(a[c]["mean"], 4) for c in ("re_cao", "re_thap", "dat_cao", "dat_thap")}, "n_dat_cao/mo", round(r["n_dat_cao_mean_per_month"], 1))
