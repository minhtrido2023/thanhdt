# -*- coding: utf-8 -*-
"""ic_analysis.py — rank IC / partial rank IC của V_ngắn vs V_dài theo PRELOCK.md (job Taylor_20261111_043843).

Tái dùng panel dd_blend_20261111 (không dựng lại). Giá chỉ là nhãn (MC0 thước đo, TR_N nhãn).
Bootstrap cụm theo MÃ: rút mã, tính lại IC theo từng quý ⇒ mọi split/năm/DT5G suy ra từ cùng mẫu bootstrap.
Run: $DNA_PYEXE ic_analysis.py -> ../out/ic_summary.json, ic_by_year.csv, ic_variants.csv
"""
import os, sys, json, itertools
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
BLEND = os.path.join(HERE, "..", "..", "dd_blend_20261111", "calc")
sys.path.insert(0, BLEND)
import common as C          # load(), dcf(), blend()
WC = "/home/trido/thanhdt/WorkingClaude"
SEED = 20261111; B = int(os.environ.get("IC_B", 1000)); HZ = (12, 24, 36, 60); MINQ = 20
WGRID = np.round(np.arange(0, 1.01, 0.1), 2)
STATE = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}

p = C.load()
r3 = (p.rating <= 3).values
fin_ok = np.isfinite(p.MC0.values)
VL = p.V_l3.values
YR = p.yr.values
QC = pd.factorize(p.q.values, sort=True)[0]        # mã quý số
QLAB = np.array(sorted(pd.unique(p.q.values)))
Q_YR = np.array([int(s[:4]) for s in QLAB])
Q_ST = pd.Series(p.dt5g.values).groupby(QC).first().reindex(range(len(QLAB))).values

# ---------- vốn chủ cho ROE tự tính (ghép (mã, fin_time) lùi)
import duckdb
fe = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS TIMESTAMP) AS time, BVPS, OShares
    FROM read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')""").df()
fe["time"] = pd.to_datetime(fe.time); fe["eq"] = fe.BVPS * fe.OShares
fe = fe[["ticker", "time", "eq"]].dropna().sort_values("time")
key = p[["ticker", "fin_time"]].reset_index().rename(columns={"index": "i"})
key["fin_time"] = pd.to_datetime(key.fin_time)
key = key.sort_values("fin_time")
mm = pd.merge_asof(key, fe, left_on="fin_time", right_on="time", by="ticker", direction="backward")
EQ = mm.set_index("i")["eq"].reindex(range(len(p))).values
assert (mm.time.dropna() <= mm.fin_time[mm.time.notna()]).all(), "PIT eq"

AN = [json.loads(s) for s in p.annual_np]
NI = {"med3": np.array([np.median(a[:3]) if len(a) else np.nan for a in AN]),
      "ttm0": np.array([a[0] if len(a) else np.nan for a in AN]),
      "mean5": np.array([np.mean(a[:5]) if len(a) >= 3 else np.nan for a in AN])}
ROE_V = p.roe.values


def vs_variant(ni_k, roe_k, cmax):
    ni = NI[ni_k]
    roe = ROE_V if roe_k == "v" else np.where(EQ > 0, ni / EQ, np.nan)
    ok = (ni > 0) & (roe > 0)
    with np.errstate(all="ignore"):
        b1 = np.clip(p.g_exp.values / roe, 0, cmax); bT = np.clip(p.g_T.values / roe, 0, cmax)
        V = np.where(ok, C.dcf(ni, p.g_exp.values, p.g_T.values, p.r.values, b1, bT), np.nan)
    V[~(V > 0)] = np.nan
    return V


VARS = list(itertools.product(("med3", "ttm0", "mean5"), ("v", "s"), (1.0, 0.8)))
VNAME = [f"{a}|roe_{b}|clip{c:g}" for a, b, c in VARS]
V0 = VNAME.index("med3|roe_v|clip1")
VS = {n: vs_variant(*v) for n, v in zip(VNAME, VARS)}
dv0 = np.nanmax(np.abs(VS[VNAME[V0]] / p.V_s.values - 1))
assert dv0 < 1e-12 and (np.isnan(VS[VNAME[V0]]) == np.isnan(p.V_s.values)).all(), f"v0 != V_s dd-blend {dv0}"
# kiểm đơn vị ROE tự tính
ratio = np.where((EQ > 0) & (ROE_V > 0) & (NI["med3"] > 0), (NI["med3"] / EQ) / ROE_V, np.nan)
roe_unit = float(np.nanmedian(ratio[r3]))
assert 0.5 <= roe_unit <= 2, f"đơn vị ROE tự tính lệch {roe_unit}"

S = {"prelock_md5": open(os.path.join(OUT, "prelock_md5.txt")).read().split()[0],
     "ctrl_dev_V_l3": p.attrs["ctrl_dev_V_l3"], "v0_vs_ddblend_maxdev": float(dv0),
     "roe_self_over_vendor_median": roe_unit, "B": B, "seed": SEED, "min_rows_per_quarter": MINQ,
     "n_trials_selection": 12 + 11}


# ---------- lõi: tương quan hạng theo quý từ chỉ số dòng
def quarter_corr(idx, cols, y):
    """idx: chỉ số dòng (có thể lặp). cols: dict tên->mảng x đầy đủ. Trả (n_q, rho[name] mảng theo quý, rho_pair)."""
    d = pd.DataFrame({"g": QC[idx], "y": y[idx]})
    for k, v in cols.items():
        d[k] = v[idx]
    R = d.groupby("g").rank(method="average")
    g = d.g.values
    cnt = np.bincount(g, minlength=len(QLAB)).astype(float)
    Z = {}
    for k in R.columns:
        r = R[k].values
        mu = np.bincount(g, r, len(QLAB)) / np.where(cnt > 0, cnt, np.nan)
        dev = r - mu[g]
        sd = np.sqrt(np.bincount(g, dev * dev, len(QLAB)) / np.where(cnt > 0, cnt, np.nan))
        Z[k] = dev / sd[g]
    def rho(a, b):
        return np.bincount(g, Z[a] * Z[b], len(QLAB)) / np.where(cnt > 0, cnt, np.nan)
    return cnt, Z, rho


def stats_from(cnt, rho, xs_names, pair=None):
    """IC_q cho mỗi x; nếu pair=(s,l): β_s, β_l chuẩn hoá + partial corr theo quý."""
    o = {k: rho(k, "y") for k in xs_names}
    if pair:
        s, l = pair
        ps, pl, psl = o[s] if s in o else rho(s, "y"), o[l] if l in o else rho(l, "y"), rho(s, l)
        den = 1 - psl ** 2
        o["PIC_s"] = (ps - psl * pl) / den
        o["PIC_l"] = (pl - psl * ps) / den
        o["PC_s"] = (ps - psl * pl) / np.sqrt(den * (1 - pl ** 2))
        o["rho_sl"] = psl
    return o


def run(mask, N, xcols, pair=None, seed=SEED, quarter_set=None):
    """Điểm + bootstrap cụm mã. Trả dict: point[name]=IC_q (theo quý), boot[name]=(B, n_q), qok."""
    m = mask & p[f"full{N}"].values
    idx = np.where(m)[0]
    y = np.log(p[f"TR{N}"].values)
    cnt, Z, rho = quarter_corr(idx, xcols, y)
    point = stats_from(cnt, rho, list(xcols), pair)
    qok = cnt >= MINQ if quarter_set is None else quarter_set
    tick = p.ticker.values[idx]
    groups = list(pd.Series(np.arange(len(idx))).groupby(tick).indices.values())
    rng = np.random.default_rng(seed)
    boot = {k: np.empty((B, len(QLAB))) for k in point}
    for b in range(B):
        s = idx[np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])]
        cb, _, rb = quarter_corr(s, xcols, y)
        ob = stats_from(cb, rb, list(xcols), pair)
        for k in ob:
            v = ob[k].copy(); v[cb < 5] = np.nan; boot[k][b] = v
    return {"point": point, "boot": boot, "qok": qok, "n": int(len(idx)), "n_tk": int(len(groups)),
            "cnt": cnt}


def agg(res, name, qsel):
    """Trung bình theo quý trong qsel (∧ qok): điểm, CI cụm mã, CI cụm quý."""
    q = qsel & res["qok"]
    if q.sum() == 0:
        return {"nq": 0}
    pt = res["point"][name][q]
    bt = np.nanmean(res["boot"][name][:, q], axis=1)
    rng = np.random.default_rng(SEED + 7)
    bq = np.array([np.mean(pt[rng.integers(0, len(pt), len(pt))]) for _ in range(B)])
    return {"nq": int(q.sum()), "n": int(res["cnt"][q].sum()), "pt": float(np.mean(pt)),
            "ci_tk": [float(np.nanpercentile(bt, 2.5)), float(np.nanpercentile(bt, 97.5))],
            "ci_q": [float(np.percentile(bq, 2.5)), float(np.percentile(bq, 97.5))]}


def agg_diff(res, a, b, qsel):
    q = qsel & res["qok"]
    pt = float(np.mean(res["point"][a][q] - res["point"][b][q]))
    bt = np.nanmean(res["boot"][a][:, q] - res["boot"][b][:, q], axis=1)
    return {"pt": pt, "ci_tk": [float(np.nanpercentile(bt, 2.5)), float(np.nanpercentile(bt, 97.5))]}


Q_IS = Q_YR <= 2019; Q_OOS = Q_YR >= 2020; Q_OOS22 = Q_YR >= 2022; Q_ALL = np.ones(len(QLAB), bool)
Q_EX2021 = ~((Q_YR == 2020) | (Q_YR == 2021))
SPLITS = {"IS": Q_IS, "OOS": Q_OOS, "OOS_ex2020_21": Q_OOS22, "ALL": Q_ALL, "ALL_ex2020_21": Q_EX2021}
base = r3 & fin_ok & (VL > 0)
XL = np.log(VL / p.MC0.values)

# ================= 1. Biến thể chính v0: IC, partial, blend grid, chân co-về-giá
mask0 = base & (VS[VNAME[V0]] > 0)
XS0 = np.log(VS[VNAME[V0]] / p.MC0.values)
# IQR trên IS (mọi dòng mask0 IS) để khớp c(w)
mIS = mask0 & (YR <= 2019)
iqr = lambda v: float(np.subtract(*np.percentile(v[np.isfinite(v)], [75, 25])))
iqr_l = iqr(XL[mIS])
xcols = {"xs": XS0, "xl": XL}
c_of_w = {}
for w in WGRID:
    xh = np.log(C.blend(p, w, VL) / p.MC0.values)
    xcols[f"hh{w:.1f}"] = xh
    c_of_w[f"{w:.1f}"] = iqr(xh[mIS]) / iqr_l
for c in [0.25, 0.5, 0.65, 0.75] + [c_of_w["0.5"], c_of_w["0.8"]]:
    xcols[f"shr{c:.3f}"] = c * XL          # log(V_l^c/MC0) = c·log(V_l/MC0)
S["c_of_w_IS"] = c_of_w
main = {}
for N in HZ:
    res = run(mask0, N, xcols, pair=("xs", "xl"), seed=SEED + N)
    # CHỐT CHẶN: IC co-về-giá == IC V_l (điểm + mọi bootstrap)
    for k in xcols:
        if k.startswith("shr"):
            d1 = np.nanmax(np.abs(res["point"][k] - res["point"]["xl"]))
            d2 = np.nanmax(np.abs(res["boot"][k] - res["boot"]["xl"]))
            assert d1 < 1e-12 and d2 < 1e-12, f"shrink IC != V_l IC ({k},{N}): {d1},{d2}"
    main[N] = res
S["shrink_guard"] = "PASS: IC(V_l^c) == IC(V_l) (|Δ|<1e-12, điểm + 1000 bootstrap, 6 giá trị c, 4 N)"

tab = {}
for N in HZ:
    r_ = main[N]; t = {}
    for sp, qs in SPLITS.items():
        t[sp] = {k: agg(r_, k, qs) for k in ("xs", "xl", "PIC_s", "PIC_l", "PC_s", "rho_sl")}
        t[sp]["hh"] = {f"{w:.1f}": agg(r_, f"hh{w:.1f}", qs) for w in WGRID}
        t[sp]["d_hh_minus_l"] = {f"{w:.1f}": agg_diff(r_, f"hh{w:.1f}", "xl", qs) for w in WGRID}
        t[sp]["d_hh_minus_s"] = {f"{w:.1f}": agg_diff(r_, f"hh{w:.1f}", "xs", qs) for w in WGRID}
        t[sp]["d_s_minus_l"] = agg_diff(r_, "xs", "xl", qs)
    t["n_rows"] = r_["n"]; t["n_tk"] = r_["n_tk"]
    tab[N] = t
S["main_v0"] = {str(N): tab[N] for N in HZ}

# ---------- tiêu chí D trên v0
def crit(tN):
    i_ok = [tN[N]["OOS"]["PIC_s"].get("ci_tk", [0, 0])[0] > 0 and tN[N]["OOS"]["PIC_s"]["pt"] > 0 for N in HZ]
    ii_ok = [tN[N]["IS"]["PIC_s"].get("pt", -1) > 0 for N in HZ]
    ev = [N for N in HZ if tN[N]["OOS_ex2020_21"]["PIC_s"].get("nq", 0) >= 6]
    iii_pos = {N: tN[N]["OOS_ex2020_21"]["PIC_s"]["pt"] > 0 for N in ev}
    i = sum(i_ok) >= 3; ii = sum(ii_ok) >= 3; iii = len(ev) >= 2 and all(iii_pos.values())
    return {"i_per_N": dict(zip(map(str, HZ), i_ok)), "i": i, "ii_per_N": dict(zip(map(str, HZ), ii_ok)), "ii": ii,
            "iii_evaluable_N": ev, "iii_pos": {str(k): v for k, v in iii_pos.items()}, "iii": iii,
            "PASS": bool(i and ii and iii)}
S["criterion_D_v0"] = crit(tab)

# ---------- w* trên IS (mô tả nếu D không đạt)
isic = {f"{w:.1f}": np.mean([tab[N]["IS"]["hh"][f"{w:.1f}"]["pt"] for N in HZ]) for w in WGRID}
best = max(isic.values())
wstar = min(float(w) for w, v in isic.items() if v >= best - 0.002)
S["blend_wstar_IS"] = {"w_star": wstar, "IS_meanIC_by_w": isic,
                       "OOS_d_vs_l": {str(N): tab[N]["OOS"]["d_hh_minus_l"][f"{wstar:.1f}"] for N in HZ},
                       "OOS_d_vs_s": {str(N): tab[N]["OOS"]["d_hh_minus_s"][f"{wstar:.1f}"] for N in HZ}}
wins = [tab[N]["OOS"]["d_hh_minus_l"][f"{wstar:.1f}"]["ci_tk"][0] > 0 and
        tab[N]["OOS"]["d_hh_minus_s"][f"{wstar:.1f}"]["ci_tk"][0] > 0 for N in HZ]
S["blend_wstar_IS"]["beats_both_CI_per_N"] = dict(zip(map(str, HZ), wins))
S["blend_wstar_IS"]["proposal_valid"] = bool(S["criterion_D_v0"]["PASS"] and sum(wins) >= 3)

# ---------- theo năm + DT5G (từ cùng bootstrap)
yr_rows = []
for N in HZ:
    r_ = main[N]
    for y_ in range(2016, 2026):
        qs = Q_YR == y_
        if (qs & r_["qok"]).sum() < 2:
            continue
        row = {"N": N, "year": y_}
        for k in ("xs", "xl", "PIC_s", "PIC_l"):
            a = agg(r_, k, qs); row[f"{k}_pt"] = a["pt"]; row[f"{k}_lo"] = a["ci_tk"][0]; row[f"{k}_hi"] = a["ci_tk"][1]
        row["nq"] = a["nq"]; row["n"] = a["n"]
        yr_rows.append(row)
    for st, nm in STATE.items():
        qs = Q_ST == st
        if (qs & r_["qok"]).sum() < 2:
            continue
        row = {"N": N, "year": f"DT5G_{nm}"}
        for k in ("xs", "xl", "PIC_s", "PIC_l"):
            a = agg(r_, k, qs); row[f"{k}_pt"] = a["pt"]; row[f"{k}_lo"] = a["ci_tk"][0]; row[f"{k}_hi"] = a["ci_tk"][1]
        row["nq"] = a["nq"]; row["n"] = a["n"]
        yr_rows.append(row)
YRT = pd.DataFrame(yr_rows)
YRT.round(4).to_csv(os.path.join(OUT, "ic_by_year.csv"), index=False)

# ---------- mô tả: AEdm/β của chân co vs blend (cho thấy chúng thưởng việc co)
def aedm_beta(x, m, N):
    k = m & p[f"full{N}"].values & np.isfinite(x)
    y = np.log(p[f"TR{N}"].values[k]); xx = x[k]
    cm = pd.Series(y).groupby(QC[k]).transform("median").values
    return {"AEdm": float(np.median(np.abs(y - cm - xx))), "beta": float(np.polyfit(xx, y, 1)[0]) if np.ptp(xx) > 0 else None}
desc = {}
for N in HZ:
    for sp, ym in (("IS", YR <= 2019), ("OOS", YR >= 2020)):
        m = mask0 & ym
        desc[f"{N}_{sp}"] = {"V_l": aedm_beta(XL, m, N), "V_s": aedm_beta(XS0, m, N),
                             "hh0.5": aedm_beta(xcols["hh0.5"], m, N),
                             f"shr_c(w0.5)={c_of_w['0.5']:.3f}": aedm_beta(c_of_w["0.5"] * XL, m, N),
                             "naive_V=MC0": aedm_beta(np.zeros(len(p)), m, N)}
S["desc_AEdm_beta"] = desc

# ================= 2. 12 biến thể V_ngắn (E): own-support
var_rows = []; var_tab = {}; per_year = {}
for vi, nm in enumerate(VNAME):
    xs = np.log(VS[nm] / p.MC0.values)
    mk = base & (VS[nm] > 0)
    vt = {}
    for N in HZ:
        r_ = main[N] if vi == V0 else run(mk, N, {"xs": xs, "xl": XL}, pair=("xs", "xl"), seed=SEED + N)
        vt[N] = {sp: {k: agg(r_, k, qs) for k in ("xs", "PIC_s")} for sp, qs in SPLITS.items()}
        for y_ in range(2016, 2024):
            per_year[(nm, N, y_)] = float(np.nanmean(r_["point"]["PIC_s"][(Q_YR == y_) & r_["qok"]])) \
                if ((Q_YR == y_) & r_["qok"]).any() else np.nan
        for sp in ("IS", "OOS", "OOS_ex2020_21"):
            a = vt[N][sp]["PIC_s"]; b_ = vt[N][sp]["xs"]
            var_rows.append({"variant": nm, "N": N, "split": sp, "n": a.get("n"), "nq": a.get("nq"),
                             "IC_s": b_.get("pt"), "IC_s_lo": b_.get("ci_tk", [None])[0],
                             "PIC_s": a.get("pt"), "PIC_s_lo": a.get("ci_tk", [None, None])[0],
                             "PIC_s_hi": a.get("ci_tk", [None, None])[1]})
    var_tab[nm] = vt
    print("variant", nm, "done", flush=True)
VT = pd.DataFrame(var_rows); VT.round(4).to_csv(os.path.join(OUT, "ic_variants.csv"), index=False)
S["variants_criterion_D"] = {nm: crit(var_tab[nm]) for nm in VNAME}
is_score = {nm: float(np.mean([var_tab[nm][N]["IS"]["PIC_s"]["pt"] for N in HZ])) for nm in VNAME}
vstar = max(is_score, key=is_score.get)
S["variant_select"] = {"IS_meanPIC_s": is_score, "v_star": vstar, "v0": VNAME[V0]}

# ---------- PBO (CSCV, 8 khối năm 2016–2023, 12 biến thể)
def pbo(M):
    yrs = np.arange(M.shape[0]); logits = []
    for isb in itertools.combinations(yrs, len(yrs) // 2):
        oo = np.setdiff1d(yrs, isb)
        ism = np.nanmean(M[list(isb)], axis=0); oom = np.nanmean(M[oo], axis=0)
        j = int(np.nanargmax(ism))
        rk = (pd.Series(oom).rank().values[j]) / (M.shape[1] + 1)
        logits.append(np.log(rk / (1 - rk)))
    return float(np.mean(np.array(logits) <= 0)), len(logits)
S["PBO_variants"] = {}
for N in (12, 36):
    M = np.array([[per_year[(nm, N, y_)] for nm in VNAME] for y_ in range(2016, 2024)])
    S["PBO_variants"][str(N)] = dict(zip(("pbo", "n_splits"), pbo(M)))

# ---------- kiểm bền: giao mọi biến thể (cùng dòng)
mk_all = base.copy()
for nm in VNAME:
    mk_all &= VS[nm] > 0
cx = {f"v{i}": np.log(VS[nm] / p.MC0.values) for i, nm in enumerate(VNAME)}
cx["xl"] = XL
common = {}
for N in HZ:
    m = mk_all & p[f"full{N}"].values; idx = np.where(m)[0]
    y = np.log(p[f"TR{N}"].values)
    cnt, Z, rho = quarter_corr(idx, cx, y)
    qok = cnt >= MINQ
    for i, nm in enumerate(VNAME):
        o = stats_from(cnt, rho, [f"v{i}", "xl"], pair=(f"v{i}", "xl"))
        common[f"{nm}|{N}"] = {sp: float(np.nanmean(o["PIC_s"][qs & qok])) if (qs & qok).any() else None
                               for sp, qs in (("IS", Q_IS), ("OOS", Q_OOS), ("OOS_ex2020_21", Q_OOS22))}
    common[f"n|{N}"] = int(len(idx))
S["common_support_PIC_s_point"] = common

json.dump(S, open(os.path.join(OUT, "ic_summary.json"), "w"), indent=1, default=float, sort_keys=True)
print(json.dumps({"criterion_D_v0": S["criterion_D_v0"], "v_star": vstar, "PBO": S["PBO_variants"],
                  "w_star": wstar}, indent=1, default=str))
