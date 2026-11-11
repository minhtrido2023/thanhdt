# -*- coding: utf-8 -*-
"""analyze.py — Q1 (thật/artifact) · Q2 (cơ chế) · Q3 (8 biến thể khoá trước) cho V_dài FCFE3y.
Theo PRELOCK.md (md5 trong ../out/prelock_md5.txt). Giá chỉ là nhãn/thước đo (MC0, TR_N).
Run: $DNA_PYEXE -W ignore analyze.py  -> ../out/summary.json, q1_*.csv, q2_*.csv, q3_*.csv
"""
import os, sys, json, itertools
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
R = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(R, "dd_blend_20261111", "calc")); sys.path.insert(0, HERE)
import common as C
import lib as L
B = int(os.environ.get("IC_B", 1000)); SEED = 20261111; HZ = (12, 24, 36, 60)
HEAVY = {"BDS", "XD_VLXD", "tienIch", "taiNguyen_chuKy"}

p = C.load()
E = pd.read_parquet(os.path.join(OUT, "ext.parquet")).reindex(range(len(p)))
QC = pd.factorize(p.q.values, sort=True)[0]
QLAB = np.array(sorted(pd.unique(p.q.values)))
ctx = L.Ctx(QC, QLAB, p.ticker.values, SEED, B)
QY = ctx.Q_YR
MC0 = p.MC0.values; VL = p.V_l3.values; VS = p.V_s.values
M0 = (p.rating <= 3).values & np.isfinite(MC0) & (VL > 0) & (VS > 0)
S = {"prelock": open(os.path.join(OUT, "prelock_md5.txt")).read().split("\n")[0], "B": B, "seed": SEED,
     "n_M0": int(M0.sum()), "n_trials_selection": 8}

# ---------------- thành phần
CFO3 = p.cfoa3.values / 3; CPX3 = -p.cfinv3.values / 3; FCFE3 = CFO3 - CPX3
rev = E[["Revenue_P0", "Revenue_P1", "Revenue_P2", "Revenue_P3"]].sum(axis=1, min_count=4).values
DA = E.EBITDA_P0.values - E.EBITM_P0.values * rev
DA = np.where(DA > 0, DA, np.nan)
FA = np.where(E.FAssetTurn_P0.values > 0, rev / E.FAssetTurn_P0.values, np.nan)
TA = np.where(E.totalAsset_P0.values > 0, E.totalAsset_P0.values, np.nan)
NPt = E[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum(axis=1, min_count=4).values
CFOt = E[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=4).values
nwc = E.Inventory_P0.values + E.AR_P0.values - E.StLiab_P0.values
nwc4 = E.inv_l4.values + E.ar_l4.values - E.stl_l4.values
AN = [json.loads(s) for s in p.annual_np]
NI3 = np.array([np.mean(a[:3]) if len(a) >= 3 else np.nan for a in AN])
grp = p.grp.values; heavy = np.isin(grp, list(HEAVY))
g_exp, g_T, r = p.g_exp.values, p.g_T.values, p.r.values
k_g = C.dcf(np.ones(len(p)), g_exp, g_T, r)            # V = base × k(g)
assert np.nanmax(np.abs(FCFE3[M0] * k_g[M0] / VL[M0] - 1)) < 1e-9, "decomposition V_l = FCFE3·k(g)"
S["r_unique"] = sorted(set(np.round(r[M0], 6))); S["gT_unique"] = sorted(set(np.round(g_T[M0], 6)))

lg = lambda v: np.where(v > 0, np.log(v / MC0), np.nan)
def demean(x):
    s = pd.Series(x); key = pd.Series(QC).astype(str) + "|" + pd.Series(grp)
    n = s.groupby(key).transform("count")
    return np.where(n >= 3, (s - s.groupby(key).transform("mean")).values, 0.0) + 0 * x

XS = lg(VS); XL = lg(VL)
COMP0 = {"xs": XS, "xl": XL, "fy": lg(FCFE3), "cfoy": lg(CFO3), "cpxy": CPX3 / MC0, "cpx_cfo": CPX3 / CFO3,
         "gk": np.log(k_g), "xl_ind": demean(XL), "fy_ind": demean(lg(FCFE3))}
COMP1 = {"xs": XS, "xl": XL, "cpx_rev": CPX3 / rev, "cpx_ta": CPX3 / TA, "accr": (NPt - CFOt) / TA,
         "ep": NPt / MC0}
COMP2 = {"xs": XS, "xl": XL, "dnwc": (nwc - nwc4) / TA}

Q_IS = QY <= 2019; Q_OOS = QY >= 2020; ALL = np.ones(len(QLAB), bool)
SPL = {"IS": Q_IS, "OOS": Q_OOS, "IS16_18": QY <= 2018, "OOS19": QY >= 2019, "IS16_21": QY <= 2021,
       "OOS22": QY >= 2022, "OOS_ex2022": Q_OOS & (QY != 2022), "OOS_ex2020_21": QY >= 2022, "ALL": ALL}
yN = {N: np.where(p[f"full{N}"].values, np.log(p[f"TR{N}"].values), np.nan) for N in HZ}
ref = json.load(open(os.path.join(R, "dd_fwd_prelock_20261111", "out", "ic_summary.json")))["main_v0"]

def table(res, names, splits):
    return {sp: {k: L.agg(ctx, res, k, splits[sp]) for k in names} for sp in splits}

# ================= Q1
q1 = {}; main = {}
for N in HZ:
    res = L.run(ctx, M0, yN[N], COMP0, "xs", seed=SEED + N)
    main[N] = res
    for sp in ("IS", "OOS"):
        d = abs(L.agg(ctx, res, "PIC:xl", SPL[sp], False)["pt"] - ref[str(N)][sp]["PIC_l"]["pt"])
        assert d < 1e-9, f"baseline != dd_fwd_prelock PIC_l {N} {sp} {d}"
    t = {"splits": table(res, ["IC:xl", "PIC:xl"], SPL)}
    t["d_IS_OOS"] = L.agg_split_diff(ctx, res, "PIC:xl", Q_IS, Q_OOS)
    t["d_IS16_18_OOS19"] = L.agg_split_diff(ctx, res, "PIC:xl", SPL["IS16_18"], SPL["OOS19"])
    t["d_IS16_21_OOS22"] = L.agg_split_diff(ctx, res, "PIC:xl", SPL["IS16_21"], SPL["OOS22"])
    t["d_IS_OOSex2022"] = L.agg_split_diff(ctx, res, "PIC:xl", Q_IS, SPL["OOS_ex2022"])
    t["d_IS_OOSex2020_21"] = L.agg_split_diff(ctx, res, "PIC:xl", Q_IS, SPL["OOS_ex2020_21"])
    # cửa sổ trượt 4 năm
    t["rolling4y"] = {}
    for y0 in range(2016, 2023):
        qs = (QY >= y0) & (QY <= y0 + 3)
        if (qs & res["qok"]).sum() >= 8:
            t["rolling4y"][f"{y0}-{y0+3}"] = L.agg(ctx, res, "PIC:xl", qs, False)
    # xu hướng vs bước nhảy 2020 (trên PIC theo quý)
    q = res["qok"]; v = res["point"]["PIC:xl"][q]
    tt = np.array([int(s[:4]) + (int(s[-1]) - 1) / 4 for s in QLAB])[q]; yy = QY[q]
    def fit(tt_, yy_, v_):
        Xt = np.c_[np.ones(len(v_)), tt_ - 2020]; Xs = np.c_[np.ones(len(v_)), (yy_ >= 2020).astype(float)]
        bt = np.linalg.lstsq(Xt, v_, rcond=None)[0]; bs = np.linalg.lstsq(Xs, v_, rcond=None)[0]
        return bt[1], bs[1], float(((v_ - Xt @ bt) ** 2).sum()), float(((v_ - Xs @ bs) ** 2).sum())
    sl, st, sse_t, sse_s = fit(tt, yy, v)
    isq = yy <= 2019
    sl_is = np.polyfit(tt[isq], v[isq], 1)[0] if isq.sum() > 3 else np.nan
    rng = np.random.default_rng(SEED + 31); yrs = np.unique(yy); bs_sl, bs_st = [], []
    for _ in range(B):
        pick = np.concatenate([np.where(yy == yrs[j])[0] for j in rng.integers(0, len(yrs), len(yrs))])
        if len(np.unique(yy[pick] >= 2020)) < 2:
            continue
        a, b_, _, _ = fit(tt[pick], yy[pick], v[pick]); bs_sl.append(a); bs_st.append(b_)
    t["trend_vs_step"] = {"slope_per_yr": float(sl), "slope_ci_yr": L.pct(bs_sl), "step2020": float(st),
                          "step_ci_yr": L.pct(bs_st), "sse_trend": sse_t, "sse_step": sse_s,
                          "slope_within_IS": float(sl_is), "nq": int(q.sum())}
    # chỉ số mã/quý theo năm
    t["rows_per_q_by_yr"] = {int(y_): float(res["cnt"][q & (QY == y_)].mean()) if (q & (QY == y_)).any() else None
                             for y_ in range(2016, 2026)}
    q1[N] = t
    print("Q1 main", N, flush=True)

# (b) phán quyết
def ex0(ci, pos=True):
    return ci[0] is not None and (ci[0] > 0 if pos else ci[1] < 0)
dd = {N: q1[N]["d_IS_OOS"] for N in HZ}
tk_ok = sum(dd[N]["pt"] > 0 and ex0(dd[N]["ci_tk"]) for N in HZ)
yr_ok = sum(dd[N]["pt"] > 0 and ex0(dd[N]["ci_yr"]) for N in HZ)
both0 = sum((not ex0(dd[N]["ci_tk"])) and (not ex0(dd[N]["ci_yr"])) for N in HZ)
S["Q1_verdict"] = {"n_tk_excl0": tk_ok, "n_yr_excl0": yr_ok, "n_both_contain0": both0,
                   "verdict": "THAT" if (tk_ok >= 3 and yr_ok >= 2) else ("ARTIFACT" if both0 >= 3 else "CHUA_KET_LUAN")}

# (d) tập mã đồng nhất
q1d = {}
for N in HZ:
    m = M0 & p[f"full{N}"].values
    df = pd.DataFrame({"tk": p.ticker.values[m], "is": QY[QC[m]] <= 2019, "q": QC[m]})
    nis = df[df["is"]].groupby("tk").q.nunique(); noo = df[~df["is"]].groupby("tk").q.nunique()
    for lab, k in (("both>=1", 1), ("both>=8", 8)):
        keep = set(nis[nis >= k].index) & set(noo[noo >= k].index)
        if len(keep) < 30:
            q1d[f"{N}|{lab}"] = {"n_tk": len(keep), "skipped": "<30 mã"}; continue
        mk = M0 & np.isin(p.ticker.values, list(keep))
        res = L.run(ctx, mk, yN[N], {"xs": XS, "xl": XL}, "xs", seed=SEED + N)
        q1d[f"{N}|{lab}"] = {"n_tk": len(keep), **{sp: L.agg(ctx, res, "PIC:xl", SPL[sp], False) for sp in ("IS", "OOS")},
                             "d_IS_OOS": L.agg_split_diff(ctx, res, "PIC:xl", Q_IS, Q_OOS)}
    print("Q1d", N, flush=True)
S["Q1"] = {str(N): q1[N] for N in HZ}; S["Q1d_homog"] = q1d

# ================= Q2
q2 = {}
for N in HZ:
    res0 = main[N]
    t = {"M0": table(res0, [f"IC:{k}" for k in COMP0] + [f"PIC:{k}" for k in COMP0 if k != "xs"],
                     {"IS": Q_IS, "OOS": Q_OOS})}
    res1 = L.run(ctx, M0, yN[N], COMP1, "xs", seed=SEED + N)
    t["M1"] = table(res1, [f"IC:{k}" for k in COMP1] + [f"PIC:{k}" for k in COMP1 if k != "xs"], {"IS": Q_IS, "OOS": Q_OOS})
    t["M1_n"] = res1["n"]
    res2 = L.run(ctx, M0, yN[N], COMP2, "xs", seed=SEED + N)
    t["M2"] = table(res2, ["IC:dnwc", "PIC:dnwc", "PIC:xl"], {"IS": Q_IS, "OOS": Q_OOS}); t["M2_n"] = res2["n"]
    res3 = L.run(ctx, M0, yN[N], {"fy": COMP0["fy"], "gk": COMP0["gk"]}, "fy", seed=SEED + N)
    t["gk_given_fy"] = table(res3, ["PIC:gk"], {"IS": Q_IS, "OOS": Q_OOS})
    for lab, ages in (("fresh_0_3m", (0, 3)), ("stale_6_9m", (6, 9))):
        mk = M0 & np.isin(E.m_since_fy.values, ages)
        rs = L.run(ctx, mk, yN[N], {"xs": XS, "xl": XL}, "xs", seed=SEED + N)
        t[lab] = table(rs, ["PIC:xl"], {"IS": Q_IS, "OOS": Q_OOS})
    q2[N] = t
    print("Q2", N, flush=True)
S["Q2"] = {str(N): q2[N] for N in HZ}

# mô tả ngành / g / phân phối thành phần theo năm (không nhãn)
yr = p.yr.values
desc = []
for y_ in range(2016, 2026):
    m = M0 & (yr == y_)
    if not m.any():
        continue
    desc.append({"year": y_, "n": int(m.sum()), "frac_heavy": float(heavy[m].mean()),
                 "med_VL_P": float(np.exp(np.median(XL[m]))), "med_fcfe_y": float(np.median(FCFE3[m] / MC0[m])),
                 "med_cpx_cfo": float(np.median(CPX3[m] / CFO3[m])), "med_gexp": float(np.median(g_exp[m])),
                 "frac_gexp_cap": float(np.mean(g_exp[m] >= g_T[m] + 0.5 * (0.20 - g_T[m]) - 1e-9)),
                 "frac_gexp_floor": float(np.mean(g_exp[m] <= g_T[m] + 0.5 * (-0.02 - g_T[m]) + 1e-9)),
                 "share_mc_heavy": float(MC0[m & heavy].sum() / MC0[m].sum()),
                 "eng_cover": float((M0 & (yr == y_)).sum() / max(1, ((p.rating <= 3).values & (yr == y_) & np.isfinite(MC0) & (VS > 0)).sum()))})
S["Q2_desc_by_year"] = desc
# IC V_dài theo nhóm ngành (điểm; quý có ≥8 dòng trong nhóm)
gi = []
from scipy.stats import spearmanr
for N in (24, 36):
    m = M0 & p[f"full{N}"].values
    df = pd.DataFrame({"q": QC[m], "g": grp[m], "x": XL[m], "y": yN[N][m], "yr": yr[m]})
    for (g_, sp), d in df.assign(sp=np.where(df.yr <= 2019, "IS", "OOS")).groupby(["g", "sp"]):
        ics = [spearmanr(dq.x, dq.y)[0] for _, dq in d.groupby("q") if len(dq) >= 8]
        gi.append({"N": N, "grp": g_, "split": sp, "nq": len(ics), "rows": len(d),
                   "IC_mean": float(np.mean(ics)) if ics else None})
S["Q2_ic_by_group"] = gi

# ================= Q3 — 8 biến thể
gate = (p.cfoa3.values > 0)
BASES = {
    "C1_fcfe5": (p.cfoa5.values + p.cfinv5.values) / 5,
    "C2_cfo3_minus_DA": CFO3 - DA,
    "C3_cfo3_minus_DA_gFA": CFO3 - DA - g_exp * FA,
    "C4_cfo3_minus_min_capex_DA": CFO3 - np.minimum(CPX3, DA),
    "C5_NI3_plus_DA_minus_capex": NI3 + DA - CPX3,
    "C6_cfo5_minus_DA": p.cfoa5.values / 5 - DA,
    "C7_heavy_C2_else_base": np.where(heavy, CFO3 - DA, FCFE3),
    "C8_fcfe_12q_rolling": (E.cfo12q.values + E.cfi12q.values) / 3,
}
q3 = {}; per_year = {}
for nm, bse in BASES.items():
    V = np.where(gate & (bse > 0), C.dcf(bse, g_exp, g_T, r), np.nan)
    xc = lg(V); mk = M0 & np.isfinite(xc)
    o = {"cover_M0": float(mk.sum() / M0.sum())}
    for N in HZ:
        res = L.run(ctx, mk, yN[N], {"xs": XS, "xl": XL, "xc": xc}, "xs", seed=SEED + N)
        o[N] = {"n": res["n"]}
        for sp in ("IS", "OOS", "OOS_ex2020_21", "OOS_ex2022"):
            o[N][sp] = {"PIC_c": L.agg(ctx, res, "PIC:xc", SPL[sp], False), "PIC_base": L.agg(ctx, res, "PIC:xl", SPL[sp], False),
                        "d": L.agg_diff(ctx, res, "PIC:xc", "PIC:xl", SPL[sp])}
        q_ = res["qok"]
        for y_ in range(2016, 2024):
            sel = q_ & (QY == y_)
            per_year[(nm, N, y_)] = float(np.nanmean(res["point"]["PIC:xc"][sel])) if sel.any() else np.nan
            per_year[("baseline", N, y_)] = float(np.nanmean(main[N]["point"]["PIC:xl"][main[N]["qok"] & (QY == y_)]))
    # tiêu chí
    i_ = [o[N]["OOS"]["d"]["pt"] > 0 and ex0(o[N]["OOS"]["d"]["ci_tk"]) for N in HZ]
    ii_ = [o[N]["IS"]["PIC_c"]["pt"] >= o[N]["IS"]["PIC_base"]["pt"] - 0.03 for N in HZ]
    iii = {}
    for sp in ("OOS_ex2020_21", "OOS_ex2022"):
        ev = [N for N in HZ if o[N][sp]["d"].get("nq", 0) >= 6]
        iii[sp] = {"evaluable": ev, "pos": {str(N): o[N][sp]["d"]["pt"] > 0 for N in ev}}
    iii_ok = all(len(v["evaluable"]) >= 2 and all(v["pos"].values()) for v in iii.values())
    o["crit"] = {"i": i_, "i_ok": sum(i_) >= 3, "ii": ii_, "ii_ok": all(ii_), "iii": iii, "iii_ok": iii_ok}
    o["IS_meanPIC"] = float(np.mean([o[N]["IS"]["PIC_c"]["pt"] for N in HZ]))
    q3[nm] = o
    print("Q3", nm, o["crit"]["i_ok"], o["crit"]["ii_ok"], iii_ok, flush=True)

def pbo(M):
    yrs = np.arange(M.shape[0]); lo = []
    for isb in itertools.combinations(yrs, len(yrs) // 2):
        oo = np.setdiff1d(yrs, isb)
        j = int(np.nanargmax(np.nanmean(M[list(isb)], 0)))
        rk = pd.Series(np.nanmean(M[oo], 0)).rank().values[j] / (M.shape[1] + 1)
        lo.append(np.log(rk / (1 - rk)))
    return float(np.mean(np.array(lo) <= 0))
CFG = ["baseline"] + list(BASES)
S["Q3_PBO"] = {str(N): pbo(np.array([[per_year[(c, N, y_)] for c in CFG] for y_ in range(2016, 2024)])) for N in (24, 36)}
pbo_ok = all(v < 0.5 for v in S["Q3_PBO"].values())
for nm in BASES:
    c = q3[nm]["crit"]; c["iv_ok"] = pbo_ok
    c["PASS"] = bool(c["i_ok"] and c["ii_ok"] and c["iii_ok"] and pbo_ok)
passers = [nm for nm in BASES if q3[nm]["crit"]["PASS"]]
S["Q3"] = {nm: {str(k): v for k, v in o.items()} for nm, o in q3.items()}
S["Q3_passers"] = passers
S["Q3_recommend"] = max(passers, key=lambda n: q3[n]["IS_meanPIC"]) if passers else None
S["Q3_per_year"] = {f"{a}|{b}|{c}": v for (a, b, c), v in per_year.items()}

json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=float, sort_keys=True)
print(json.dumps({"Q1_verdict": S["Q1_verdict"], "PBO": S["Q3_PBO"], "passers": passers}, indent=1))
