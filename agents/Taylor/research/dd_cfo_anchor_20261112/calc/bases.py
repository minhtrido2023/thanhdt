# -*- coding: utf-8 -*-
"""bases.py — dựng 9 ứng viên nền + baseline + chân điều khiển theo PRELOCK.md (dd_cfo_anchor_20261112).
Không đọc nhãn. Giá chỉ vào qua MC0 (thước đo). Trả dict mảng V (VND, giá trị vốn chủ) cùng chỉ số với panel.
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
R = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(R, "dd_blend_20261111", "calc"))
import common as C

CANDS = ["A1", "A2", "B3", "B5", "C1", "C2", "D1", "D2", "E"]


def build():
    p = C.load()
    E1 = pd.read_parquet(os.path.join(R, "dd_fcfe3y_decay_20261111", "out", "ext.parquet")).reindex(range(len(p)))
    E2 = pd.read_parquet(os.path.join(OUT, "ext2.parquet")).reindex(range(len(p)))
    n = len(p)
    an = [json.loads(s) for s in p.annual_np]
    NI3 = np.array([np.sum(a[:3]) if len(a) >= 3 else np.nan for a in an])
    NIn = p.NI_norm.values
    CFO3 = p.cfoa3.values; CPX3 = -p.cfinv3.values; CPX5 = -p.cfinv5.values
    cfo5_ok = np.isfinite(p.cfoa5.values)
    rev0 = E2.rev_y0.values
    DA = E2.EBITDA_P0.values - E2.EBITM_P0.values * rev0
    DA = np.where(DA > 0, DA, np.nan)
    roe = p.roe.values
    roic = np.where(np.isfinite(E2.ROIC3Y.values), E2.ROIC3Y.values, roe)
    g, gT, r = p.g_exp.values, p.g_T.values, p.r.values

    def V(base, rr=None):
        """rr=None ⇒ b=0 (FCFE như engine); ngược lại b = clip(g/rr, 0, 0.8), cần rr>0."""
        base = np.asarray(base, float)
        if rr is None:
            v = C.dcf(base, g, gT, r)
            ok = np.isfinite(base) & (base > 0)
        else:
            with np.errstate(all="ignore"):
                b1 = np.clip(g / rr, 0, 0.8); bT = np.clip(gT / rr, 0, 0.8)
            v = C.dcf(base, g, gT, r, b1, bT)
            ok = np.isfinite(base) & (base > 0) & np.isfinite(rr) & (rr > 0)
        return np.where(ok & np.isfinite(v) & (v > 0), v, np.nan)

    out = {}
    with np.errstate(all="ignore"):
        ratio = np.where(NI3 > 0, CFO3 / NI3, np.nan)
        out["A1"] = V(np.where(NI3 > 0, NIn * np.clip(ratio, 0, 1), np.nan), roe)
        out["A2"] = V(np.minimum(NI3, CFO3) / 3, roe)
        cy = np.column_stack([E2[f"cfo_y{j}"].values for j in range(5)])
        b3 = np.where(np.isfinite(cy[:, :3]).all(1), np.median(cy[:, :3], 1), np.nan)
        b5 = np.where(np.isfinite(cy).all(1), np.median(cy, 1), np.nan)
        out["B3"] = V(b3, roic); out["B5"] = V(b5, roic)
        c1 = NI3 / 3 + DA - np.minimum(CPX3 / 3, DA)
        out["C1"] = V(c1, roe)
        dnwc = (E2.nwc0.values - E2.nwc12.values) / 3
        out["C2"] = V(c1 - dnwc, roe)
        out["D1"] = V(np.where(cfo5_ok, CFO3 / 3 - CPX5 / 5, np.nan))
        rev3 = E2[["rev_y0", "rev_y1", "rev_y2"]].sum(axis=1, min_count=3).values
        ci = np.where(rev3 > 0, CPX3 / rev3, np.nan)
        d = pd.DataFrame({"q": p.q.values, "grp": p.grp.values, "ci": ci})
        mg = d.groupby(["q", "grp"]).ci.transform("median"); ng = d.groupby(["q", "grp"]).ci.transform("count")
        mq = d.groupby("q").ci.transform("median")
        m = np.where(ng >= 5, mg, mq)
        out["D2"] = V(np.where(rev0 > 0, CFO3 / 3 - m * rev0, np.nan))
        Vearn = V(NIn, roe)
        Vcash = V(CFO3 / 3 - np.minimum(CPX3 / 3, DA))
        qa = (NI3 > 0) & (ratio >= 0.8)
        qb = np.isfinite(cy[:, :3]).all(1) & (np.nan_to_num(cy[:, :3], nan=-1) > 0).all(1)
        TA = E2.totalAsset_P0.values
        qc = (TA > 0) & (np.abs(E2.ni_y0.values - E2.cfo_y0.values) / TA <= 0.10)
        w = (qa.astype(float) + qb + qc) / 3
        okE = np.isfinite(Vearn) & np.isfinite(Vcash)
        out["E"] = np.where(okE, w * Vearn + (1 - w) * Vcash, np.nan)
    MC0 = p.MC0.values; VL = p.V_l3.values; VS = p.V_s.values
    M0 = (p.rating <= 3).values & np.isfinite(MC0) & (VL > 0) & (VS > 0)
    isrow = p["asof"].dt.year.values <= 2019
    wbar = float(np.mean(w[M0 & isrow & okE]))
    out["E_const"] = np.where(okE, wbar * Vearn + (1 - wbar) * Vcash, np.nan)
    out["F"] = VL; out["S"] = VS; out["C4"] = Vcash
    out["K"] = np.where(M0, 0.5 * VS + 0.5 * VL, np.nan)
    aux = {"w": w, "wbar": wbar, "Vearn": Vearn, "NI3": NI3, "CFO3": CFO3, "CPX3": CPX3, "DA": DA,
           "ratio": ratio, "qa": qa, "qb": qb, "qc": qc, "rev3": rev3, "ci": ci, "m_ci": m, "roic": roic,
           "b3": b3, "c1": c1, "dnwc": dnwc}
    return p, E1, E2, out, M0, aux
