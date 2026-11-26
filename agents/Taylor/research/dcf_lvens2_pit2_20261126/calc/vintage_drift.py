# -*- coding: utf-8 -*-
"""vintage_drift.py — selfcheck vintage (skeptic mục 3): so lv_ENS2 stepcar dựng as-of 2026-05/06 từ cache data/bq_cache_asof20260728 (out/vintage)
với cùng as-of dựng từ cache hiện tại (out/final). Định lượng drift do vendor restate SAU ngày chụp cache (BVPS/OShares/NP…), không phải do code.
Dùng: python vintage_drift.py OUT_JSON OUT_CSV"""
import sys, json
import numpy as np, pandas as pd

YMS = ["2026-05", "2026-06"]


def main(out_json, out_csv):
    res = {}; rows = []
    for ym in YMS:
        a = pd.read_parquet(f"out/vintage/lvens2_{ym}_mcstepcar.parquet").set_index("ticker")
        b = pd.read_parquet(f"out/final/lvens2_{ym}_mcstepcar.parquet").set_index("ticker")
        com = a.index.intersection(b.index)
        a, b = a.loc[com], b.loc[com]
        ok = a.lv_ENS2.notna() & b.lv_ENS2.notna()
        d = (b.lv_ENS2 - a.lv_ENS2)[ok]
        dE = np.log(b.E.where(b.E > 0) / a.E.where(a.E > 0))
        r = {"n_common": int(len(com)), "n_lv_both": int(ok.sum()),
             "lv_identical": int((d.abs() < 1e-12).sum()), "lv_absdiff_gt_0.01": int((d.abs() > 0.01).sum()), "lv_absdiff_gt_0.05": int((d.abs() > 0.05).sum()),
             "lv_absdiff_mean": float(d.abs().mean()), "lv_absdiff_p95": float(d.abs().quantile(0.95)), "lv_absdiff_max": float(d.abs().max()),
             "E_changed_gt_1pct": int((dE.abs() > 0.01).sum()), "rank_spearman": float(a.lv_ENS2[ok].rank().corr(b.lv_ENS2[ok].rank())),
             "half_flip(lv rank vs median)": int(((a.lv_ENS2[ok].rank(pct=True) >= 0.5) != (b.lv_ENS2[ok].rank(pct=True) >= 0.5)).sum())}
        res[ym] = r
        top = d.abs().sort_values(ascending=False).head(15).index
        for t in top:
            rows.append({"ym": ym, "ticker": t, "route": b.at[t, "route"], "lv_vintage": round(a.at[t, "lv_ENS2"], 4), "lv_now": round(b.at[t, "lv_ENS2"], 4),
                         "dlv": round(d.at[t], 4), "E_vintage": a.at[t, "E"], "E_now": b.at[t, "E"], "N_vintage": a.at[t, "N"], "N_now": b.at[t, "N"],
                         "E_unexpl_v": bool(a.at[t, "E_unexpl"]), "E_unexpl_now": bool(b.at[t, "E_unexpl"])})
    json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(json.dumps(res, ensure_ascii=False, indent=1)); print(pd.DataFrame(rows).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
