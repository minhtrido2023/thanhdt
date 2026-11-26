# -*- coding: utf-8 -*-
"""mc_err.py — đo sai số số CP ngầm trong mc (N_mc = mc/Price) của 4 biến thể so với số CP PIT thật tại D (PRELOCK.md).
Vào: panel dump (lvens2_pit2.py --mode v31 --dump-panel): mỗi (mã, tháng) = dòng BCTC mới nhất known ≤ time ⇒ N_row đúng như mode pit (N_next không biết ở D).
Sự thật: mike/data/fiinprox_oshares_pit_20260926.csv (số CP theo ngày, neo ex-right). Phụ: N kỳ BCTC kế (restate, tham khảo).
Dùng: python mc_err.py out/panel_v31_dump.parquet out/mc_err.json"""
import sys, json, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lvens2_pit2 import load_ca, ca_factor, NS  # noqa: E402

TRUTH = "/home/trido/thanhdt/WorkingClaude/mike/data/fiinprox_oshares_pit_20260926.csv"


def main(dump, out):
    p = pd.read_parquet(dump)
    p = p[(p.src == "BQ") & p.in_universe & (p.ym >= "2014-01") & (p.ym <= "2026-08") & (p.N > 0) & (p.Price > 0)].copy().reset_index(drop=True)
    p["time"] = p.time.astype(NS); p["known"] = p.known.astype(NS)
    tr = pd.read_csv(TRUTH, parse_dates=["date"]); tr["date"] = tr.date.astype(NS)
    tr = tr[tr.shares > 0].sort_values("date")
    p = pd.merge_asof(p.sort_values("time"), tr[["ticker", "date", "shares"]], left_on="time", right_on="date", by="ticker", direction="backward")
    p = p[p.shares.notna()].reset_index(drop=True)
    ca = load_ca()
    lr = np.log(p.Close / p.Price) - np.log(p.close_rel / p.price_rel)
    V = {"strict": p.N.values,
         "step": np.where(lr.abs() > 0.003, p.N * np.exp(lr), p.N),
         "stepca": p.N.values * ca_factor(p, ca, False)[0],
         "stepcar": p.N.values * ca_factor(p, ca, True)[0]}
    lt = np.log(p.shares.values)
    ev = np.abs(np.log(p.N.values) - lt) > 0.01          # nhóm có sự kiện (N_row lệch sự thật >1%)
    res = {"n_cells": int(len(p)), "n_tickers": int(p.ticker.nunique()), "months": [p.ym.min(), p.ym.max()], "n_event_cells": int(ev.sum()), "variants": {}}
    for k, v in V.items():
        e = np.abs(np.log(v) - lt)
        nn = p.N_next.values; okn = np.isfinite(nn) & (nn > 0)
        e2 = np.abs(np.log(v[okn]) - np.log(nn[okn]))
        res["variants"][k] = {"mean_abs_log_err": float(e.mean()), "median": float(np.median(e)), "p95": float(np.quantile(e, .95)),
                              "share_gt5pct": float((e > 0.05).mean()), "event_mean_abs": float(e[ev].mean()), "event_share_gt5pct": float((e[ev] > 0.05).mean()),
                              "nonevent_mean_abs": float(e[~ev].mean()),
                              "vs_next_bctc_mean_abs": float(e2.mean()), "vs_next_bctc_share_gt5pct": float((e2 > 0.05).mean()), "n_next": int(okn.sum())}
        p["err_" + k] = np.log(v) - lt
    # theo năm (để thấy ổn định)
    p["yr"] = p.ym.str[:4]
    res["by_year_mean_abs"] = {k: p.groupby("yr")["err_" + k].apply(lambda s: float(s.abs().mean())).to_dict() for k in V}
    # luật chọn PRELOCK
    core = {k: res["variants"][k]["mean_abs_log_err"] for k in ("strict", "step", "stepca")}
    rank = sorted(core, key=core.get); best, second = rank[0], rank[1]
    simple = {"strict": 0, "stepca": 1, "step": 2}
    if (core[second] - core[best]) / core[best] < 0.02:
        best = min(best, second, key=simple.get)
    r = res["variants"]
    if (r["stepca"]["mean_abs_log_err"] - r["stepcar"]["mean_abs_log_err"]) / r["stepca"]["mean_abs_log_err"] >= 0.10 and r["stepcar"]["share_gt5pct"] <= r["stepca"]["share_gt5pct"] and best == "stepca":
        best = "stepcar"
    res["chosen_by_prelock"] = best
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    for k, v in r.items():
        print(f"{k:8s} mean|e|={v['mean_abs_log_err']:.5f} >5%={v['share_gt5pct']:.4f} event_mean={v['event_mean_abs']:.4f} event>5%={v['event_share_gt5pct']:.3f} "
              f"vsNext={v['vs_next_bctc_mean_abs']:.4f}")
    print("n_cells", res["n_cells"], "event_cells", res["n_event_cells"], "CHỌN:", best)
    # mã lệch lớn nhất dưới biến thể chọn (để giải thích)
    p["abs_best"] = p["err_" + best].abs()
    p.nlargest(15, "abs_best")[["ticker", "ym", "known", "N", "shares", "err_strict", "err_step", "err_stepca", "err_stepcar"]].to_csv(out.replace(".json", "_worst.csv"), index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
