"""R3 park0 @ pin0%/pin1M: ctrl (cache LAG canonical) vs adj (events/edge dẫn xuất từ pkl adjusted). 1 trục.
Tái dùng NGUYÊN paired_w2.boot (L=21 B=4000 seed=12345, chuỗi block chung) + w2b_overlay.load_daily/hdr,
annualize theo lịch — như park0_ab.py (registry "2026-10-08")."""
import hashlib, io, json, os, sys, numpy as np, pandas as pd
from scipy import stats as st
HERE = os.path.dirname(os.path.abspath(__file__))
W2 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927"
WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-balgate-1110/WorkingClaude"
sys.path.insert(0, WT); sys.path.insert(0, W2)
from paired_w2 import metrics, boot, L, B, SEED
from w2b_overlay import load_daily, hdr
assert (L, B, SEED) == (21, 4000, 12345)
EXPECT = {"r3_ctrl_p0_off": "537e349b5589408c994f8aceafeb9a39", "r3_ctrl_p0_1m": "a6ba34d83a4d374a73293d897c0b43d9"}
LEGS = ["r3_ctrl_p0_off", "r3_ctrl_p0_1m", "r3_adj_p0_off", "r3_adj_p0_1m"]
def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def leg_path(tag):
    txt = io.open(f"{HERE}/logs/{tag}.log", encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 (" in txt and f" {tag} " in txt, tag
    assert txt.count("final NAV identity err = 0 VND") == 2 and txt.count("cash-flow identity max err = 0 VND") == 2, f"{tag}: self-check != 0 VND"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines() if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1; return hits[0]
res = {"bootstrap": {"L": L, "B": B, "seed": SEED, "paired": True}}
nav = {}
for t in LEGS:
    p = leg_path(t); nav[t], _ = load_daily(p)
    res[t] = {"ledger": p.split("/research/", 1)[1], "md5": md5(p), "selfcheck_0VND": True, **hdr(t, nav[t])}
    for nm, (a, b) in {"IS_2014_19": ("2014-01-01", "2019-12-31"), "OOS_2020p": ("2020-01-01", "2030-01-01")}.items():
        s = nav[t][(nav[t].index >= a) & (nav[t].index <= b)]
        if nm == "OOS_2020p":   # nối từ NAV cuối 2019 như các mục registry
            s = nav[t][nav[t].index >= nav[t][nav[t].index <= "2019-12-31"].index[-1]]
        res[t][nm] = hdr(nm, s)
for t, m in EXPECT.items():
    res[t]["control_byte_identical"] = res[t]["md5"] == m; assert res[t]["md5"] == m, f"CONTROL {t} lệch md5"
idx = nav[LEGS[0]].index
for t in LEGS: assert nav[t].index.equals(idx)
R = np.column_stack([np.diff(np.log(nav[n].values)) for n in LEGS]); N = R.shape[0]
YRS = (idx[-1] - idx[0]).days / 365.25; ANN = N / YRS
C, S, D, K = boot(R, ANN, N)
bs = {}
for i, n in enumerate(LEGS):
    bs[n] = {"E_cagr_pct": round(float(C[:, i].mean())*100, 2), "cagr5_pct": round(float(np.percentile(C[:, i], 5))*100, 2),
             "dd5_pct": round(float(np.percentile(D[:, i], 5))*100, 2), "P_dd_lt_30": round(float((D[:, i] < -.30).mean()), 4),
             "E_calmar": round(float(K[:, i].mean()), 4)}
res["bootstrap_paired"] = bs
ab = {}
yr = np.array([d.year for d in idx[1:]])
for conv, a, b in (("pin0%", "r3_adj_p0_off", "r3_ctrl_p0_off"), ("pin1M", "r3_adj_p0_1m", "r3_ctrl_p0_1m")):
    ia, ib = LEGS.index(a), LEGS.index(b); dc = C[:, ia] - C[:, ib]; dd = D[:, ia] - D[:, ib]; dk = K[:, ia] - K[:, ib]
    ex = R[:, ia] - R[:, ib]   # chuỗi lợi suất chênh lệch ngày
    sr = ex.mean() / ex.std(ddof=1); g3 = st.skew(ex); g4 = st.kurtosis(ex, fisher=False)
    psr = float(st.norm.cdf(sr * np.sqrt(N - 1) / np.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr**2)))   # N_trials=1 ⇒ DSR = PSR(SR*=0)
    per_year = {int(y): round(float((np.exp(R[yr == y, ia].sum()) - np.exp(R[yr == y, ib].sum())) * 100), 2) for y in np.unique(yr)}
    ab[conv] = {"dCAGR_pp_point": round(res[a]["cagr_pct"] - res[b]["cagr_pct"], 3),
                "dMaxDD_pp_point": round(res[a]["maxdd_pct"] - res[b]["maxdd_pct"], 2),
                "dCalmar_point": round(res[a]["calmar"] - res[b]["calmar"], 4),
                "P_dCAGR_gt0": round(float((dc > 0).mean()), 4), "dCAGR_pp_p5_p95": [round(float(np.percentile(dc, q))*100, 3) for q in (5, 95)],
                "P_maxdd_better": round(float((dd > 0).mean()), 4), "P_calmar_gt": round(float((dk > 0).mean()), 4),
                "N_trials": 1, "DSR_N1_daily_excess": round(psr, 4), "PBO": "không áp dụng (họ 1 cấu hình < 8)",
                "dIS_pp": round(res[a]["IS_2014_19"]["cagr_pct"] - res[b]["IS_2014_19"]["cagr_pct"], 3),
                "dOOS_pp": round(res[a]["OOS_2020p"]["cagr_pct"] - res[b]["OOS_2020p"]["cagr_pct"], 3),
                "per_year_ret_diff_pp": per_year, "years_negative": [y for y, v in per_year.items() if v < 0]}
res["ab_paired_adj_vs_ctrl"] = ab
json.dump(res, open(f"{HERE}/r3_results.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
