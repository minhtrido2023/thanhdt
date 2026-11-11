# -*- coding: utf-8 -*-
"""analyze.py — lưới w (A/G/B/C/B+C), chọn trên IS theo PRELOCK, chấm OOS, CI bootstrap cụm, LOYO, PBO,
walk-forward phụ, ngành. Run: $DNA_PYEXE analyze.py [--fiin-only] -> ../out/summary[_fiinonly].json
"""
import os, sys, json, itertools, argparse
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--fiin-only", action="store_true"); args = ap.parse_args()
TAG = "_fiinonly" if args.fiin_only else ""
p = load(fiin_only=args.fiin_only)
S = {"ctrl_dev_V_l3": p.attrs["ctrl_dev_V_l3"], "n_trials_declared": 306}
r3 = (p.rating <= 3).values
fin_ok = np.isfinite(p.MC0.values)
IS_y = (p.yr <= 2019).values; OOS_y = ~IS_y

# ---- 0. share-basis: cách cũ vs mới (production V_l3)
m0 = r3 & p.eng_ok.values & p.MC0_fiin.notna().values
dlog = np.log(p.MC0_fiin.values[m0] / p.MC0_old.values[m0])
S["share_basis"] = {"n": int(m0.sum()), "frac_absdiff_gt5pct": float((np.abs(dlog) > np.log(1.05)).mean()),
                    "frac_fallback_rows_r3_engok": float((r3 & p.eng_ok.values & (p.mc_src.values == "fb")).mean() /
                                                         (r3 & p.eng_ok.values).mean())}
# K3 cũ (FV đứng yên, TR có cổ tức) trên hệ cũ vs mới, + K3n
k = r3 & p.eng_ok.values & p.full36.values & fin_ok
TR = p.TR36.values[k]; V = p.V_l3.values[k]
for lab, MC in (("old_basis", p.MC0_old.values[k]), ("new_basis", p.MC0.values[k])):
    g0 = np.abs(np.log(MC / V)); S["share_basis"][f"K3a_static_{lab}"] = float(np.median(np.abs(np.log(MC * TR / V))) / np.median(g0))
    S["share_basis"][f"medVP_{lab}"] = float(np.exp(np.median(np.log(V / MC))))

# ---- 1. mẫu chính & độ phủ
base_mask = r3 & fin_ok & (p.V_s > 0).values & (p.V_l3 > 0).values
S["coverage"] = {"r3_rows": int((r3 & fin_ok).sum()), "both": int(base_mask.sum()),
                 "only_Vs": int((r3 & fin_ok & (p.V_s > 0).values & ~(p.V_l3 > 0).values).sum()),
                 "only_Vl": int((r3 & fin_ok & ~(p.V_s > 0).values & (p.V_l3 > 0).values).sum()),
                 "tickers_both": int(p.ticker[base_mask].nunique()), "quarters": int(p.q[base_mask].nunique())}

# ---- 2. chọn 3y vs 5y (w=0, IS, dòng có cả hai)
m35 = base_mask & (p.V_l5 > 0).values & IS_y
c3 = metrics(p, p.V_l3.values, m35, 36); c5 = metrics(p, p.V_l5.values, m35, 36)
use5 = (c5["iqr"] < c3["iqr"]) and (c5["K3n"] <= c3["K3n"])
S["choose_3y5y_IS"] = {"fcfe3y": c3, "fcfe5y": c5, "use_5y": bool(use5)}
VL = p.V_l5.values if use5 else p.V_l3.values
if use5:
    base_mask = base_mask & (p.V_l5 > 0).values
MAIN = base_mask
IS = MAIN & IS_y; OOS = MAIN & OOS_y

# ---- 3. lưới
trials = []
def add(struct, params, V, N):
    for lab, m in (("IS", IS), ("OOS", OOS), ("ALL", MAIN)):
        o = metrics(p, V, m, N); o.update({"struct": struct, "N": N, "split": lab}); o.update(params); trials.append(o)

Vcache = {}
for N in HZ:
    for w in WGRID:
        for kind in ("A", "G"):
            V = blend(p, w, VL, kind); Vcache[(kind, w)] = V; add(kind, {"w": w}, V, N)
    for qn in ("q1", "q2"):
        qv = p[qn].fillna(0.5).values
        for wl, wh in itertools.product((0, .25, .5, .75, 1), repeat=2):
            w_i = wl + (wh - wl) * qv
            V = blend(p, w_i, VL, "A"); Vcache[("B", qn, wl, wh)] = V
            add("B", {"q": qn, "w_lo": wl, "w_hi": wh}, V, N)
T = pd.DataFrame(trials)


def pick(df):
    d = df[(df.split == "IS") & df.medVP.between(0.75, 1.25)].copy()
    return d.sort_values("K3n").iloc[0] if len(d) else None


SEL = {}
for N in HZ:
    sel = {}
    tA = T[(T.struct == "A") & (T.N == N)]
    dA = tA[(tA.split == "IS") & tA.medVP.between(0.75, 1.25)]
    best = dA.K3n.min()
    wA = float(dA[dA.K3n <= best + 0.005].w.min())       # hoà ⇒ w nhỏ hơn
    sel["A"] = wA
    for s in ("G", "B"):
        r_ = pick(T[(T.struct == s) & (T.N == N)])
        sel[s] = None if r_ is None else r_.to_dict()
    SEL[N] = sel
S["selection_IS"] = {N: {"A_w": SEL[N]["A"],
                         "G": SEL[N]["G"] and {k: SEL[N]["G"][k] for k in ("w", "K3n", "medVP")},
                         "B": SEL[N]["B"] and {k: SEL[N]["B"][k] for k in ("q", "w_lo", "w_hi", "K3n", "medVP")}}
                     for N in HZ}
# lưới A đầy đủ (bảng báo cáo)
S["gridA"] = T[T.struct == "A"][["N", "split", "w", "n", "nN", "medVP", "iqr", "K3n", "K3u", "beta", "touch_VltP", "frac_VltP"]].round(4).to_dict("records")
S["gridG"] = T[T.struct == "G"][["N", "split", "w", "medVP", "iqr", "K3n", "beta", "touch_VltP"]].round(4).to_dict("records")


# ---- 4. C và B+C; so sánh OOS có CI (cặp)
def Vsel(N, s):
    if s == "A": return Vcache[("A", SEL[N]["A"])]
    if s == "G": return Vcache[("G", SEL[N]["G"]["w"])]
    b = SEL[N]["B"]; return Vcache[("B", b["q"], b["w_lo"], b["w_hi"])]


D = np.abs(np.log(p.V_s.values / VL))
VCH = {}
S["C"] = {}; S["final"] = {}; S["vs_baseline"] = {}
for N in HZ:
    VA = Vsel(N, "A")
    cres = {}
    for tau_lab, tau in (("log2", np.log(2)), ("log3", np.log(3))):
        flag = D > tau
        for s in ("A", "B"):
            Vb = Vsel(N, s)
            VC = np.where(flag, np.minimum(p.V_s.values, VL), Vb)
            nm = "C" if s == "A" else "B+C"
            cres[f"{nm}_{tau_lab}"] = {sp: metrics(p, VC, m, N) for sp, m in (("IS", IS), ("OOS", OOS))}
            cres[f"{nm}_{tau_lab}"]["flag_rate"] = float(flag[MAIN].mean())
            # cờ: dòng phân kỳ có hội tụ kém hơn?
            cres[f"{nm}_{tau_lab}"]["flagged_vs_not_ALL"] = {"flagged": metrics(p, Vb, MAIN & flag, N),
                                                               "not": metrics(p, Vb, MAIN & ~flag, N)}
    S["C"][N] = cres
    # quyết định cấu trúc theo PRELOCK: G/B/C chỉ thay A nếu IS cải thiện > 0,01 VÀ Δ OOS CI<0
    cand = {"A": VA, "G": Vsel(N, "G") if SEL[N]["G"] is not None else None,
            "B": Vsel(N, "B") if SEL[N]["B"] is not None else None}
    for tl in ("log2", "log3"):
        cand[f"C_{tl}"] = np.where(D > (np.log(2) if tl == "log2" else np.log(3)), np.minimum(p.V_s.values, VL), VA)
    isA = metrics(p, VA, IS, N)["K3n"]
    chosen, why = "A", {}
    order = ["G", "C_log2", "C_log3", "B"]
    best_alt = None
    for s in order:
        if cand[s] is None: continue
        isK = metrics(p, cand[s], IS, N).get("K3n", np.nan)
        lvl = metrics(p, cand[s], IS, N)["medVP"]
        if not (0.75 <= lvl <= 1.25): why[s] = "level"; continue
        if isA - isK > 0.01:
            pt, bt, n_, ng = boot_k3n(p, [cand[s], VA], OOS, N)
            dci = ci(bt[:, 0] - bt[:, 1])
            why[s] = {"IS_gain": isA - isK, "OOS_delta": float(pt[0] - pt[1]), "OOS_delta_ci": dci}
            if dci[1] < 0 and (best_alt is None or isK < best_alt[1]):
                best_alt = (s, isK)
        else:
            why[s] = {"IS_gain": isA - isK}
    if best_alt: chosen = best_alt[0]
    Vc = cand[chosen]; VCH[N] = Vc
    S["final"][N] = {"chosen": chosen, "A_w": SEL[N]["A"], "alt_tests": why}
    # baseline: w=0 production, w=1 LNST, 50/50
    bl = {"prod_w0": Vcache[("A", 0.0)], "lnst_w1": Vcache[("A", 1.0)], "half": Vcache[("A", 0.5)]}
    out = {}
    for sp, m in (("IS", IS), ("OOS", OOS), ("ALL", MAIN)):
        names = ["chosen"] + list(bl)
        pt, bt, n_, ng = boot_k3n(p, [Vc] + list(bl.values()), m, N)
        pq, bq, _, nq = boot_k3n(p, [Vc] + list(bl.values()), m, N, cluster="q")
        o = {"n": n_, "n_tickers": ng, "n_quarters": nq}
        for j, nm in enumerate(names):
            mm = metrics(p, ([Vc] + list(bl.values()))[j], m, N)
            o[nm] = {"K3n": float(pt[j]), "K3n_ci_ticker": ci(bt[:, j]), "K3n_ci_quarter": ci(bq[:, j]),
                     "medVP": mm["medVP"], "iqr": mm["iqr"], "beta": mm.get("beta"), "K3u": mm.get("K3u"),
                     "touch_VltP": mm.get("touch_VltP"), "frac_VltP": mm.get("frac_VltP")}
            if j > 0:
                o[nm]["delta_chosen_minus_this"] = float(pt[0] - pt[j])
                o[nm]["delta_ci_ticker"] = ci(bt[:, 0] - bt[:, j])
                o[nm]["delta_ci_quarter"] = ci(bq[:, 0] - bq[:, j])
        out[sp] = o
    S["vs_baseline"][N] = out
    print(N, "chosen", chosen, "wA", SEL[N]["A"], {k: round(out["OOS"][k]["K3n"], 3) for k in ["chosen"] + list(bl)}, flush=True)

# beta CI cho V chọn tại N (OOS/ALL, cụm mã)
def boot_beta(V, m, N, B=1000):
    ok = m & p[f"full{N}"].values & np.isfinite(V) & (V > 0)
    idx = np.where(ok)[0]; x = np.log(V[idx] / p.MC0.values[idx]); y = np.log(p[f"TR{N}"].values[idx])
    groups = list(pd.Series(np.arange(len(idx))).groupby(p.ticker.values[idx]).indices.values())
    rng = np.random.default_rng(SEED); out = []
    for _ in range(B):
        s = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        out.append(np.polyfit(x[s], y[s], 1)[0])
    return ci(np.array(out))
S["beta_ci"] = {N: {sp: {"chosen": boot_beta(VCH[N], m, N),
                         "prod_w0": boot_beta(Vcache[("A", 0.0)], m, N)} for sp, m in (("OOS", OOS), ("ALL", MAIN))} for N in HZ}

# ---- 5. walk-forward phụ IS<=2021 / OOS>=2022 (N<=36), LOYO
S["wf2"] = {}
IS2 = MAIN & (p.yr <= 2021).values; OOS2 = MAIN & (p.yr >= 2022).values
for N in (12, 24, 36):
    rows = [(w, metrics(p, Vcache[("A", w)], IS2, N)) for w in WGRID]
    el = [(w, o) for w, o in rows if 0.75 <= o["medVP"] <= 1.25 and "K3n" in o]
    b = min(o["K3n"] for _, o in el); w2 = min(w for w, o in el if o["K3n"] <= b + 0.005)
    pt, bt, n_, ng = boot_k3n(p, [Vcache[("A", w2)], Vcache[("A", 0.0)]], OOS2, N)
    S["wf2"][N] = {"w_IS2": float(w2), "OOS2_K3n": float(pt[0]), "OOS2_K3n_ci": ci(bt[:, 0]),
                   "OOS2_prod": float(pt[1]), "delta_ci": ci(bt[:, 0] - bt[:, 1]), "n": n_, "n_tickers": ng,
                   "OOS2_medVP": metrics(p, Vcache[("A", w2)], OOS2, N)["medVP"]}
S["loyo"] = {}
for N in HZ:
    ws = {}
    for y in sorted(p.yr[MAIN].unique()):
        m = MAIN & (p.yr != y).values
        el = []
        for w in WGRID:
            o = metrics(p, Vcache[("A", w)], m, N)
            if "K3n" in o and 0.75 <= o["medVP"] <= 1.25: el.append((w, o["K3n"]))
        b = min(k for _, k in el); ws[int(y)] = float(min(w for w, k in el if k <= b + 0.005))
    S["loyo"][N] = ws

# ---- 6. PBO (CSCV, khối = năm 2016-2023, N=36, trials A+G+B)
keys = [("A", w) for w in WGRID] + [("G", w) for w in WGRID] + \
       [("B", q, a, b) for q in ("q1", "q2") for a, b in itertools.product((0, .25, .5, .75, 1), repeat=2)]
years = list(range(2016, 2024))
ok36 = MAIN & p.full36.values
G0 = {}; GN = {}
for kk in keys:
    V = Vcache[kk]; g0, gN = k3n_vec(p.MC0.values, V, p.TR36.values, p.r.values, 36)
    G0[kk], GN[kk] = g0, gN
yrv = p.yr.values
logits = []
for comb in itertools.combinations(years, 4):
    mi = ok36 & np.isin(yrv, comb); mo = ok36 & np.isin(yrv, [y for y in years if y not in comb])
    isv = np.array([np.median(GN[kk][mi]) / np.median(G0[kk][mi]) for kk in keys])
    oov = np.array([np.median(GN[kk][mo]) / np.median(G0[kk][mo]) for kk in keys])
    b = int(np.argmin(isv))
    rank = (oov > oov[b]).sum() + 0.5 * ((oov == oov[b]).sum() - 1)   # tốt hơn = K3n nhỏ ⇒ đếm số trial tệ hơn
    om = (rank + 0.5) / (len(keys) + 1)
    logits.append(np.log(om / (1 - om)))
S["pbo"] = {"n_trials": len(keys), "n_splits": len(logits), "PBO": float(np.mean(np.array(logits) <= 0)),
            "median_logit": float(np.median(logits))}

# ---- 7. ngành (mô tả): w*_A theo nhóm trên ALL; Δ OOS so với w* chung
S["industry"] = {}
for N in (12, 36):
    wglob = SEL[N]["A"]
    for gname in sorted(p.grp[MAIN].unique()):
        mg = MAIN & (p.grp == gname).values
        if (mg & p[f"full{N}"].values).sum() < 150: continue
        rows = []
        for w in WGRID:
            o = metrics(p, Vcache[("A", w)], mg & IS_y, N)
            if "K3n" in o and 0.75 <= o["medVP"] <= 1.25: rows.append((w, o["K3n"]))
        res = {"n_all": int((mg & p[f"full{N}"].values).sum()), "n_tickers": int(p.ticker[mg].nunique())}
        if rows:
            b = min(k for _, k in rows); wg = float(min(w for w, k in rows if k <= b + 0.005))
            res["w_IS_group"] = wg
            try:
                pt, bt, n_, ng = boot_k3n(p, [Vcache[("A", wg)], Vcache[("A", wglob)]], mg & OOS_y, N)
                res.update({"OOS_K3n_group_w": float(pt[0]), "OOS_K3n_global_w": float(pt[1]),
                            "delta_ci": ci(bt[:, 0] - bt[:, 1]), "n_OOS": n_, "tickers_OOS": ng})
            except Exception as e:
                res["oos_err"] = str(e)
        full_curve = {float(w): metrics(p, Vcache[("A", w)], mg, N).get("K3n") for w in (0.0, 0.5, 1.0)}
        res["ALL_K3n_w0_w05_w1"] = full_curve
        res["ALL_medVP_w0_w1"] = [metrics(p, Vcache[("A", 0.0)], mg, N)["medVP"], metrics(p, Vcache[("A", 1.0)], mg, N)["medVP"]]
        S["industry"].setdefault(N, {})[gname] = res

T.round(5).to_csv(os.path.join(OUT, f"trials{TAG}.csv"), index=False)
S["n_trials_run"] = int(len(T[T.split == "IS"])) + 2 + 16   # A/G/B + chọn 3y5y + C/B+C
json.dump(S, open(os.path.join(OUT, f"summary{TAG}.json"), "w"), indent=1, sort_keys=True, default=float)
np.save(os.path.join(OUT, f"VL_is5y{TAG}.npy"), np.array([use5]))
print(json.dumps({k: S[k] for k in ("share_basis", "coverage", "choose_3y5y_IS", "selection_IS", "pbo", "wf2", "loyo")}, indent=0, default=float)[:6000])
