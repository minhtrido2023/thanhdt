#!/usr/bin/env python3
"""D2 vòng 2 — phân tích BỔ SUNG theo yêu cầu quant-skeptic (POST-HOC, NGOÀI PREREG, không đổi verdict khoá).
Tái dùng hàm của analysis.py (không sửa). Usage: $DNA_PYEXE analysis_r2.py [--asof YYYY-MM-DD]
Ra: results_r2.json + stdout. Tất định, không dùng đồng hồ."""
import argparse, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analysis as A

HS = tuple(range(1, 10))

def delta(dep, T, h):
    base, _ = A.val_at(dep, T)
    th = T + pd.DateOffset(months=h)
    if base is None or th > dep.index.max():
        return None
    return round(A.val_at(dep, th)[0] - base, 4)

def med(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else round(float(np.median(xs)), 4)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--asof", default="2026-11-05"); a = ap.parse_args()
    ib, pol, pol_ff, s = A.load_te(pd.Timestamp(a.asof))
    dep = A.load_dep1m()
    R = {}
    # (1) quét chân trời h=1..9, episode thr +1,0 (chính) — chỉ episode có baseline thật
    eps = [e for e in A.episodes(s, 1.0) if e["signal"] >= dep.index.min()]
    scan = {}
    for e in eps:
        scan[str(e["signal"].date())] = {f"h{h}": delta(dep, e["signal"], h) for h in HS}
    R["scan_h1_9"] = scan
    R["scan_median"] = {f"h{h}": med([v[f"h{h}"] for v in scan.values()]) for h in HS}
    R["scan_n_eval"] = {f"h{h}": sum(v[f"h{h}"] is not None for v in scan.values()) for h in HS}
    # (2) điều kiện theo MỨC: mọi ngày quan sát có S>=thr, tín hiệu = chính ngày đó (S đã biết, dep tại ngày đó)
    lvl = {}
    last_ok = dep.index.max()
    for thr in (1.0, 2.0):
        days = s[(s >= thr) & (s.index >= dep.index.min())].index
        row = {"n_days": int(len(days))}
        for h in (3, 6):
            d = [delta(dep, t, h) for t in days]
            dd = [x for x in d if x is not None]
            row[f"d{h}"] = {"n_days": len(dd), "median": med(dd), "mean": round(float(np.mean(dd)), 4) if dd else None,
                            "share_pos": round(float(np.mean([x > 0 for x in dd])), 3) if dd else None}
        # cụm độc lập theo tháng dương lịch (ngày liền kề tương quan mạnh)
        byM = {}
        for t in days:
            x = delta(dep, t, 6)
            if x is not None: byM.setdefault(str(t.to_period("M")), []).append(x)
        mm = {k: round(float(np.median(v)), 4) for k, v in sorted(byM.items())}
        row["d6_by_month_median"] = mm
        row["d6_months"] = len(mm)
        row["d6_months_pos"] = sum(v > 0 for v in mm.values())
        row["d6_median_of_month_medians"] = med(list(mm.values()))
        lvl[str(thr)] = row
    R["level_conditional"] = lvl
    # ví dụ cụ thể skeptic nêu: 2023Q1, S>=2 ngày nào
    q1 = s.loc["2023-01-01":"2023-03-31"]
    t = q1.idxmax()
    R["case_2023Q1"] = {"date": str(t.date()), "S": round(float(q1.max()), 3), "d3": delta(dep, t, 3), "d6": delta(dep, t, 6),
                        "n_days_S_ge_2_in_Q1": int((q1 >= 2.0).sum())}
    # (3) đếm độc lập theo regime: gộp episode nếu S>=0 xuyên suốt giữa 2 tín hiệu
    sig = [e["signal"] for e in eps]
    # regime = episode thr 0 theo ĐÚNG luật kết thúc PREREG (20 obs liên tiếp S<0 mới kết thúc) — định nghĩa có sẵn, không tune
    ext, st, below, last = [], None, 0, None
    for t_, v in s.items():
        if st is None:
            if v >= 0: st, below, last = t_, 0, t_
        else:
            if v >= 0: below, last = 0, t_
            else:
                below += 1
                if below >= A.END_RUN: ext.append((st, last)); st = None
    if st is not None: ext.append((st, last))
    reg = []
    for t_ in sig:
        k = next((i for i, (x, y) in enumerate(ext) if x <= t_ <= y), None)
        if reg and reg[-1][0] == k: reg[-1][1].append(t_)
        else: reg.append([k, [t_]])
    R_ext = {str(k): [str(ext[k][0].date()), str(ext[k][1].date())] for k, _ in reg if k is not None}
    reg = [g[1] for g in reg]
    band = s.loc["2024-05-01":"2025-10-31"]
    R["regimes"] = {"rule": "regime = episode thr 0 (kết thúc sau 20 obs liên tiếp S<0, luật PREREG §3); tín hiệu cùng regime gộp thành 1", "regime_extents": R_ext,
                    "groups": [[str(x.date()) for x in g] for g in reg],
                    "between_2025-01_and_2025-08": {"min_S": round(float(s.loc["2025-01-02":"2025-08-15"].min()), 3),
                                                    "days_S_lt_0": int((s.loc["2025-01-02":"2025-08-15"] < 0).sum()),
                                                    "days_S_lt_1": int((s.loc["2025-01-02":"2025-08-15"] < 1).sum())},
                    "band_2024-05_2025-10": {"min_S": round(float(band.min()), 3), "days_S_ge_0": int((band >= 0).sum()), "n_days": int(len(band))}}
    # verdict áp lại với 1 cycle/regime: giá trị đại diện mỗi regime = median Δ6 trong regime
    reg_d6 = []
    for g in reg:
        reg_d6.append(med([delta(dep, t, 6) for t in g]))
    R["regimes"]["d6_per_regime"] = reg_d6
    R["regimes"]["n_regimes_eval"] = sum(x is not None for x in reg_d6)
    R["regimes"]["median_d6"] = med(reg_d6)
    R["regimes"]["prereg_rule_needs_N>=3_met"] = bool(R["regimes"]["n_regimes_eval"] >= 3)
    R["regimes"]["verdict_rule_applied"] = "KHÔNG KẾT LUẬN" if R["regimes"]["n_regimes_eval"] < 3 else "xem PREREG §6"
    out = json.dumps(R, ensure_ascii=False, indent=1, sort_keys=True)
    open(os.path.join(HERE, "results_r2.json"), "w").write(out + "\n"); print(out)

if __name__ == "__main__":
    main()
