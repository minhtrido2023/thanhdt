# -*- coding: utf-8 -*-
"""lib.py — lõi rank IC / partial rank IC theo quý + bootstrap cụm mã / khối năm (PRELOCK.md).

Cùng công thức với dd_fwd_prelock_20261111/calc/ic_analysis.py (Pearson trên hạng trong từng quý,
PIC = hệ số chuẩn hoá trong hồi quy hạng 2 biến), tổng quát hoá cho nhiều cột x và biến kiểm soát tuỳ chọn.
"""
import numpy as np, pandas as pd

MINQ = 20


class Ctx:
    def __init__(self, qcode, qlab, ticker, seed=20261111, B=1000):
        self.QC = qcode; self.QLAB = qlab; self.nQ = len(qlab)
        self.Q_YR = np.array([int(s[:4]) for s in qlab]); self.TK = ticker
        self.seed = seed; self.B = B


def _qcorr(ctx, idx, cols, y):
    d = pd.DataFrame({"g": ctx.QC[idx], "y": y[idx]})
    for k, v in cols.items():
        d[k] = v[idx]
    R = d.groupby("g").rank(method="average")
    g = d.g.values; nQ = ctx.nQ
    cnt = np.bincount(g, minlength=nQ).astype(float)
    den = np.where(cnt > 0, cnt, np.nan)
    Z = {}
    for k in R.columns:
        r = R[k].values
        mu = np.bincount(g, r, nQ) / den
        dv = r - mu[g]
        sd = np.sqrt(np.bincount(g, dv * dv, nQ) / den)
        Z[k] = dv / sd[g]
    rho = lambda a, b: np.bincount(g, Z[a] * Z[b], nQ) / den
    return cnt, rho


def _stats(rho, names, ctrl):
    o = {}
    for k in names:
        o[f"IC:{k}"] = rho(k, "y")
    if ctrl is not None:
        pc = o[f"IC:{ctrl}"]
        for k in names:
            if k == ctrl:
                continue
            r_kc = rho(k, ctrl)
            with np.errstate(all="ignore"):
                o[f"PIC:{k}"] = (o[f"IC:{k}"] - r_kc * pc) / (1 - r_kc ** 2)
            o[f"rho:{k}|{ctrl}"] = r_kc
    return o


def run(ctx, mask, y_full, cols, ctrl="xs", seed=None, B=None):
    """Điểm + bootstrap cụm mã. mask đã gồm full_N; dòng có x không hữu hạn bị loại."""
    B = ctx.B if B is None else B
    m = mask & np.isfinite(y_full)
    for v in cols.values():
        m &= np.isfinite(v)
    idx = np.where(m)[0]
    cnt, rho = _qcorr(ctx, idx, cols, y_full)
    point = _stats(rho, list(cols), ctrl)
    qok = cnt >= MINQ
    tk = ctx.TK[idx]
    groups = list(pd.Series(np.arange(len(idx))).groupby(tk).indices.values())
    rng = np.random.default_rng(ctx.seed if seed is None else seed)
    boot = {k: np.full((B, ctx.nQ), np.nan) for k in point}
    for b in range(B):
        s = idx[np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])]
        cb, rb = _qcorr(ctx, s, cols, y_full)
        ob = _stats(rb, list(cols), ctrl)
        for k in ob:
            v = ob[k].copy(); v[cb < 5] = np.nan; boot[k][b] = v
    return {"point": point, "boot": boot, "qok": qok, "cnt": cnt, "n": int(len(idx)),
            "n_tk": int(len(groups)), "idx": idx}


def _yrboot(ctx, vals_by_q, q, rng, B):
    """Bootstrap khối năm: rút năm có hoàn lại trong tập quý q, trung bình quý."""
    yrs = np.unique(ctx.Q_YR[q])
    blocks = [np.where(q & (ctx.Q_YR == y))[0] for y in yrs]
    out = np.empty(B)
    for b in range(B):
        pick = np.concatenate([blocks[j] for j in rng.integers(0, len(blocks), len(blocks))])
        out[b] = np.nanmean(vals_by_q[pick])
    return out


def pct(a):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) else [None, None]


def agg(ctx, res, name, qsel, yrblock=True):
    q = qsel & res["qok"]
    if q.sum() == 0:
        return {"nq": 0}
    pt = res["point"][name]
    bt = np.nanmean(res["boot"][name][:, q], axis=1)
    o = {"nq": int(q.sum()), "n": int(res["cnt"][q].sum()), "pt": float(np.nanmean(pt[q])), "ci_tk": pct(bt)}
    if yrblock:
        o["ci_yr"] = pct(_yrboot(ctx, pt, q, np.random.default_rng(ctx.seed + 7), ctx.B))
    return o


def agg_diff(ctx, res, a, b, qsel):
    """Δ = a − b, cùng quý, cùng mẫu bootstrap."""
    q = qsel & res["qok"]
    if q.sum() == 0:
        return {"nq": 0}
    d = res["point"][a] - res["point"][b]
    bt = np.nanmean(res["boot"][a][:, q] - res["boot"][b][:, q], axis=1)
    return {"nq": int(q.sum()), "pt": float(np.nanmean(d[q])), "ci_tk": pct(bt),
            "ci_yr": pct(_yrboot(ctx, d, q, np.random.default_rng(ctx.seed + 11), ctx.B))}


def agg_split_diff(ctx, res, name, qa, qb):
    """Δ = mean(name | qa) − mean(name | qb). Cụm mã: cùng mẫu bootstrap; khối năm: rút độc lập."""
    qa = qa & res["qok"]; qb = qb & res["qok"]
    if qa.sum() == 0 or qb.sum() == 0:
        return {"nq": [int(qa.sum()), int(qb.sum())]}
    pt = res["point"][name]
    bt = np.nanmean(res["boot"][name][:, qa], axis=1) - np.nanmean(res["boot"][name][:, qb], axis=1)
    rng = np.random.default_rng(ctx.seed + 13)
    ya = _yrboot(ctx, pt, qa, rng, ctx.B); yb = _yrboot(ctx, pt, qb, rng, ctx.B)
    return {"nq": [int(qa.sum()), int(qb.sum())], "pt": float(np.nanmean(pt[qa]) - np.nanmean(pt[qb])),
            "ci_tk": pct(bt), "ci_yr": pct(ya - yb)}
