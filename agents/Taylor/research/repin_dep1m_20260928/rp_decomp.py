#!/usr/bin/env python3
"""TACH Delta cua chan pin dep1m thanh (a) so hoc carry cong vao tien va (b) doi duong giao dich.

Job Taylor_20260927_170645, buoc 6 cua dispatch. Day la chinh bai hoc W2b (quant-skeptic REFUTED
W2 vi doc Delta cua engine-rerun nhu the no la hieu ung cua carry): engine-rerun tron HAI hieu ung,
chi OVERLAY tach duoc cai thu nhat.

Cong thuc overlay COPY nguyen tu `c30v_w2_q2_20260927/w2b_overlay.py` (da qua quant-skeptic
CONFIRMED 2026-09-27 16:44Z) — tai su dung, khong dan xuat lai:
  nav_ov(d) = nav_ov(d-1)*(1+r_eng(d)) + max(idle_cash(d-1),0) * rate(d)/252 * nav_ov(d-1)/nav_eng(d-1)
  idle_cash = bal_cash_ref + lag_cash_ref  (dung dai luong simulate() tra lai cho: chi cash>0)
Bootstrap L=21 B=4000 seed=12345, PAIRED (mot chuoi block cho MOI chan) — module `paired_w2`.
"""
import io, json, os, sys
import numpy as np, pandas as pd

WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude"
W2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927"
HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "logs")
sys.path.insert(0, WT)          # tier dep1m ban moi
sys.path.insert(0, W2)
import idle_rate_proxy as irp
from paired_w2 import metrics, boot, L, B, SEED
from w2b_overlay import load_daily, overlay, hdr

assert (L, B, SEED) == (21, 4000, 12345), (L, B, SEED)
assert "dep1m" in irp.TIERS, "sys.path lay nham ban idle_rate_proxy KHONG co tier dep1m"

def leg_path(tag):
    """Duong dan ledger do CHINH engine in ra (khong dung lai tu env — §8)."""
    txt = io.open(os.path.join(LOGS, f"{tag}.log"), encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: chan khong EXIT=0 — tu choi doc so"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, f"{tag}: {hits}"
    return hits[0]

OFFSETS = {"median": -2.525, "p25": -3.400, "p75": -2.300}
ENGINE = {"median": "rp_pin", "p25": "rp_p25", "p75": "rp_p75"}

if __name__ == "__main__":
    ctrl_p = leg_path("rp_ctrl")
    nav0, idle0 = load_daily(ctrl_p)
    res = {"_ctrl_leg": ctrl_p, "_n_daily": int(len(nav0)),
           "_window": [str(nav0.index[0].date()), str(nav0.index[-1].date())],
           "_idle_frac_mean": round(float((idle0 / nav0).mean()), 4),
           "_bootstrap": {"L": L, "B": B, "seed": SEED, "paired": True}}
    res["ctrl_carry0"] = hdr("ctrl", nav0)

    series = {"ctrl_carry0": nav0}
    for lbl, off in OFFSETS.items():
        irp.DEP1M_OFFSET_PP = off
        ov, nostart, rate = overlay(nav0, idle0, "dep1m")
        h = hdr(lbl, ov)
        h.update({"offset_pp": off, "pre_series_zero_sessions": int(nostart),
                  "rate_mean_pct": round(float(rate.mean()) * 100, 3),
                  "delta_cagr_pp_ARITH": round(h["cagr_pct"] - res["ctrl_carry0"]["cagr_pct"], 3)})
        res[f"overlay_{lbl}"] = h
        series[f"overlay_{lbl}"] = ov

        eng = load_daily(leg_path(ENGINE[lbl]))[0]
        assert eng.index.equals(nav0.index), f"{lbl}: index engine != index ctrl"
        he = hdr(lbl, eng)
        he["offset_pp"] = off
        he["delta_cagr_pp_TOTAL"] = round(he["cagr_pct"] - res["ctrl_carry0"]["cagr_pct"], 3)
        he["delta_cagr_pp_PATH"] = round(he["delta_cagr_pp_TOTAL"] - h["delta_cagr_pp_ARITH"], 3)
        he["ledger"] = leg_path(ENGINE[lbl])
        res[f"engine_{lbl}"] = he
        series[f"engine_{lbl}"] = eng
    irp.DEP1M_OFFSET_PP = OFFSETS["median"]

    names = list(series)
    R = np.column_stack([np.diff(np.log(series[nm].values)) for nm in names])
    N = R.shape[0]; YRS = (nav0.index[-1] - nav0.index[0]).days / 365.25; ANN = N / YRS
    res["_ann_obs_per_yr"] = round(ANN, 2)
    C, S, D, K = boot(R, ANN, N)
    EK = K.mean(axis=0); D5 = np.percentile(D, 5, axis=0); C5 = np.percentile(C, 5, axis=0)
    jc = names.index("ctrl_carry0")
    for i, nm in enumerate(names):
        res[nm]["E_calmar"] = round(float(EK[i]), 4)
        res[nm]["dd5th_pct"] = round(float(D5[i]), 4) * 100
        res[nm]["cagr5th_pct"] = round(float(C5[i]) * 100, 2)
        res[nm]["P_gt_ctrl_calmar"] = round(float((K[:, i] > K[:, jc]).mean()), 4)
    # dai bat dinh cua cau, doc tren CHINH chan engine
    eng_c = [res[f"engine_{k}"]["cagr_pct"] for k in OFFSETS]
    ov_c = [res[f"overlay_{k}"]["cagr_pct"] for k in OFFSETS]
    res["_band"] = {
        "engine_cagr_range_pp": round(max(eng_c) - min(eng_c), 3),
        "overlay_cagr_range_pp": round(max(ov_c) - min(ov_c), 3),
        "engine_monotonic_in_offset": bool(
            res["engine_p25"]["cagr_pct"] < res["engine_median"]["cagr_pct"] < res["engine_p75"]["cagr_pct"]),
        "overlay_monotonic_in_offset": bool(
            res["overlay_p25"]["cagr_pct"] < res["overlay_median"]["cagr_pct"] < res["overlay_p75"]["cagr_pct"]),
        "w2b_noise_floor_parked_leg_pp": 0.46,
        "w2b_mde_one_leg_parked_pp": 0.4}
    out = os.path.join(HERE, "rp_decomp.json")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1)); print("->", out)
