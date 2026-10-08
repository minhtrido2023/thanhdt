#!/usr/bin/env python3
"""Re-pin R3 o knob LIVE park=0 + A/B park 0 vs 0.3 duoi CUNG quy uoc idle=dep1m.
Job Taylor_20261008_155435.

Tai su dung NGUYEN (khong dan xuat lai):
  - overlay carry `w2b_overlay.overlay` (quant-skeptic CONFIRMED 2026-09-27 16:44Z) -> tach SO HOC
  - `paired_w2.boot` (L=21 B=4000 seed=12345, MOT chuoi block index chung cho MOI chan) -> paired
  - annualize theo THOI GIAN LICH (len(r)/yrs) — giong bootstrap_nav.py / paired_v2.py.

Tach A/B (duoi dep1m) thanh 3 phan cong lai DUNG bang Delta tong:
  D_total = CAGR(p0_1m) - CAGR(p30_1m)
          = D_off                       (park 0 vs 0.3 khi tien nhan roi 0%: phuong tien + duong di)
          + D_arith_carry               ([ov(p0_off)-p0_off] - [ov(p30_off)-p30_off]: carry them tren
                                         phan tien KHONG park, giu nguyen duong giao dich)
          + D_path_resid                (phan con lai: engine phan ung voi carry khac nhau giua 2 park)
"""
import hashlib, io, json, os, sys
import numpy as np, pandas as pd

WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude"
W2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927"
HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "logs")
sys.path.insert(0, WT); sys.path.insert(0, W2)
import idle_rate_proxy as irp
from paired_w2 import metrics, boot, L, B, SEED
from w2b_overlay import load_daily, overlay, hdr

assert (L, B, SEED) == (21, 4000, 12345), (L, B, SEED)
assert "dep1m" in irp.TIERS, "sys.path lay nham idle_rate_proxy KHONG co tier dep1m"
assert irp.DEP1M_OFFSET_PP == -2.525, irp.DEP1M_OFFSET_PP

EXPECT = {"c_p30_off": "4707bcbeb7e801d49a4a851ffd91d5e7", "c_p30_1m": "bcd0469f42c2f76937a6ebb10aae9b40"}
LEGS = ["c_p30_off", "c_p30_1m", "p0_off", "p0_1m"]

def leg_path(tag):
    txt = io.open(os.path.join(LOGS, f"{tag}.log"), encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: chan khong EXIT=0 — tu choi doc so"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, f"{tag}: {hits}"
    return hits[0]

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()

if __name__ == "__main__":
    res = {"job": "Taylor_20261008_155435", "bootstrap": {"L": L, "B": B, "seed": SEED, "paired": True}}
    nav, idle, paths = {}, {}, {}
    for t in LEGS:
        p = leg_path(t); paths[t] = p
        nav[t], idle[t] = load_daily(p)
        res[t] = {"ledger": os.path.basename(p), "md5": md5(p)}
        res[t].update(hdr(t, nav[t]))
        res[t]["idle_frac_mean"] = round(float((idle[t] / nav[t]).mean()), 4)
    for t, m in EXPECT.items():
        res[t]["control_byte_identical"] = (res[t]["md5"] == m)
        assert res[t]["md5"] == m, f"CONTROL {t} md5 {res[t]['md5']} != {m} — DUNG"
    idx = nav["c_p30_off"].index
    for t in LEGS:
        assert nav[t].index.equals(idx), f"{t}: index != c_p30_off — paired khong hop le"

    # --- overlay so hoc: carry dep1m cong len CHINH duong NAV carry-0% cua tung park ---
    ov = {}
    for park, off_leg, on_leg in (("p30", "c_p30_off", "c_p30_1m"), ("p0", "p0_off", "p0_1m")):
        o, nostart, rate = overlay(nav[off_leg], idle[off_leg], "dep1m")
        ov[park] = o
        h = hdr(f"ov_{park}", o)
        tot = res[on_leg]["cagr_pct"] - res[off_leg]["cagr_pct"]
        ar = h["cagr_pct"] - res[off_leg]["cagr_pct"]
        res[f"decomp_{park}"] = {"overlay": h, "pre_series_zero_sessions": int(nostart),
                                 "rate_mean_pct": round(float(rate.mean()) * 100, 3),
                                 "d_total_pp": round(tot, 3), "d_arith_pp": round(ar, 3),
                                 "d_path_pp": round(tot - ar, 3),
                                 "arith_share": round(ar / tot, 4) if tot else None}

    # --- A/B park 0 vs 0.3 ---
    d_tot = res["p0_1m"]["cagr_pct"] - res["c_p30_1m"]["cagr_pct"]
    d_off = res["p0_off"]["cagr_pct"] - res["c_p30_off"]["cagr_pct"]
    d_ar = res["decomp_p0"]["d_arith_pp"] - res["decomp_p30"]["d_arith_pp"]
    res["ab_decomp_cagr_pp"] = {"d_total_dep1m": round(d_tot, 3), "d_off_vehicle_and_path": round(d_off, 3),
                                "d_arith_extra_carry": round(d_ar, 3),
                                "d_path_resid": round(d_tot - d_off - d_ar, 3)}

    # --- PAIRED bootstrap: 4 engine legs + 2 overlay ---
    names = LEGS + ["ov_p30", "ov_p0"]
    series = dict(nav); series["ov_p30"] = ov["p30"]; series["ov_p0"] = ov["p0"]
    R = np.column_stack([np.diff(np.log(series[n].values)) for n in names])
    N = R.shape[0]; YRS = (idx[-1] - idx[0]).days / 365.25; ANN = N / YRS
    C, S, D, K = boot(R, ANN, N)
    res["_ann_obs_per_yr"] = round(ANN, 2); res["_n_ret"] = int(N)
    bs = {}
    for i, n in enumerate(names):
        bs[n] = {"E_cagr_pct": round(float(C[:, i].mean()) * 100, 2),
                 "cagr5_pct": round(float(np.percentile(C[:, i], 5)) * 100, 2),
                 "E_maxdd_pct": round(float(D[:, i].mean()) * 100, 2),
                 "dd5_pct": round(float(np.percentile(D[:, i], 5)) * 100, 2),
                 "dd_median_pct": round(float(np.median(D[:, i])) * 100, 2),
                 "P_dd_lt_30": round(float((D[:, i] < -0.30).mean()), 4),
                 "E_calmar": round(float(K[:, i].mean()), 4),
                 "calmar5": round(float(np.percentile(K[:, i], 5)), 4),
                 "E_sharpe": round(float(S[:, i].mean()), 3)}
    res["bootstrap_paired"] = bs
    j = {n: names.index(n) for n in names}
    ab = {}
    for conv, a, b in (("dep1m", "p0_1m", "c_p30_1m"), ("off", "p0_off", "c_p30_off"),
                       ("arith_overlay_dep1m", "ov_p0", "ov_p30")):
        ia, ib = j[a], j[b]
        dc, dd, dk = C[:, ia] - C[:, ib], D[:, ia] - D[:, ib], K[:, ia] - K[:, ib]
        ab[conv] = {"P_cagr0_gt_cagr30": round(float((dc > 0).mean()), 4),
                    "P_maxdd0_better": round(float((dd > 0).mean()), 4),
                    "P_calmar0_gt_calmar30": round(float((dk > 0).mean()), 4),
                    "dCAGR_pp_mean": round(float(dc.mean()) * 100, 3),
                    "dCAGR_pp_p5_p95": [round(float(np.percentile(dc, 5)) * 100, 3), round(float(np.percentile(dc, 95)) * 100, 3)],
                    "dMaxDD_pp_mean": round(float(dd.mean()) * 100, 3),
                    "dMaxDD_pp_p5_p95": [round(float(np.percentile(dd, 5)) * 100, 3), round(float(np.percentile(dd, 95)) * 100, 3)],
                    "dCalmar_mean": round(float(dk.mean()), 4),
                    "dCalmar_p5_p95": [round(float(np.percentile(dk, 5)), 4), round(float(np.percentile(dk, 95)), 4)]}
    res["ab_paired"] = ab

    # --- leave-years-out Calmar (nhu paired_v2 muc 2) ---
    yr = np.array([d.year for d in idx[1:]])
    loo = {}
    for name, drop in {"FULL": [], "drop 2018": [2018], "drop 2019+2020": [2019, 2020],
                       "drop 2021": [2021], "drop 2022": [2022], "drop 2025": [2025]}.items():
        keep = ~np.isin(yr, drop)
        c, s, d, k = metrics(R[keep], ANN)
        loo[name] = {n: {"cagr": round(float(c[i]) * 100, 2), "maxdd": round(float(d[i]) * 100, 2),
                         "calmar": round(float(k[i]), 3)} for i, n in enumerate(names[:4])}
    res["leave_years_out"] = loo

    out = os.path.join(HERE, "park0_ab.json")
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False)); print("->", out)
