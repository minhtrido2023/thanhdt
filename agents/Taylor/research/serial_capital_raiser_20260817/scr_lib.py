#!/usr/bin/env python3
"""Estimators for the serial-capital-raiser program. Offline — no BigQuery, no network.

`Index`, `boot`, `holm`, `loo` are lifted from `corp_action_program_20260815/sprint3_analyze.py`
so the two programs' confidence intervals are produced by the same code, not by two similar-looking
reimplementations. `nw_tstat`, `absorb`, `cluster2_ols` are new here and documented below.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260817
NBOOT = 10_000


class Index:
    """As-of level lookup on a sorted date series. Used for the VNINDEX benchmark leg.

    `level()` returns NaN for a date before the first observation instead of raising or borrowing
    a neighbouring level — a missing benchmark date must drop the event, not silently substitute
    another session's price (corp-action ledger E3).
    """

    def __init__(self, dts, closes):
        d = np.asarray(dts, dtype=object)
        c = np.asarray(closes, float)
        order = np.argsort(d, kind="stable")
        self.d, self.c = d[order], c[order]

    def level(self, s):
        keys = np.asarray([x if isinstance(x, str) and x else "" for x in s], dtype=object)
        ix = np.searchsorted(self.d, keys, side="right") - 1
        out = np.full(len(ix), np.nan)
        ok = (ix >= 0) & (keys != "")
        out[ok] = self.c[ix[ok]]
        return out

    def ret(self, a, b):
        x, y = self.level(a), self.level(b)
        with np.errstate(divide="ignore", invalid="ignore"):
            return y / x - 1


def boot(x, blocks, seed: int = SEED, nboot: int = NBOOT) -> dict:
    """Block bootstrap of a mean, resampling whole blocks (anchor year-months).

    Events in the same month share a market shock, so an event-level CI understates the true
    spread. Resampling blocks keeps that correlation. The p-value is the two-sided proportion of
    resampled means on the wrong side of zero.
    """
    x = np.asarray(x, float)
    blocks = np.asarray(blocks, dtype=object)
    m = np.isfinite(x)
    x, blocks = x[m], blocks[m]
    if not len(x):
        return {"n": 0, "mean": None, "lo": None, "hi": None, "p": None}
    u = np.unique(blocks)
    sums = np.array([x[blocks == b].sum() for b in u])
    ns = np.array([(blocks == b).sum() for b in u])
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(u), (nboot, len(u)))
    means = sums[draws].sum(1) / ns[draws].sum(1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    p = 2 * min((means <= 0).mean(), (means >= 0).mean())
    q = np.percentile(x, [10, 25, 50, 75, 90])
    return {"n": int(len(x)), "n_blocks": int(len(u)), "mean": float(x.mean()),
            "lo": float(lo), "hi": float(hi), "p": float(min(1.0, p)),
            "p10": float(q[0]), "p25": float(q[1]), "median": float(q[2]),
            "p75": float(q[3]), "p90": float(q[4]),
            "share_positive": float((x > 0).mean())}


def holm(d: dict) -> dict:
    """Holm step-down adjustment. Returns adjusted p per key."""
    items = sorted(((k, v) for k, v in d.items() if v is not None and np.isfinite(v)),
                   key=lambda z: z[1])
    n = len(items)
    out, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (n - i) * p))
        out[k] = run
    return out


def loo(vals: np.ndarray, years: np.ndarray) -> dict:
    """Leave-one-year-out. A sign flip means one year carries the whole effect."""
    v = np.asarray(vals, float)
    y = np.asarray(years)
    m = np.isfinite(v)
    v, y = v[m], y[m]
    if not len(v):
        return {"rows": [], "sign_flip": None}
    full = v.mean()
    total = v.sum()
    rows = []
    for yy in sorted(set(y.tolist())):
        g = v[y == yy]
        rest = v[y != yy]
        rows.append({"year": int(yy), "n": int(len(g)), "mean": float(g.mean()),
                     "mean_without": float(rest.mean()) if len(rest) else None,
                     "effect_share": float(g.sum() / total) if total else None})
    carrier = max(rows, key=lambda z: abs(z["effect_share"] or 0.0)) if rows else None
    return {"full_mean": float(full), "rows": rows,
            "carrier_year": carrier["year"] if carrier else None,
            "carrier_share": carrier["effect_share"] if carrier else None,
            "sign_flip": bool(any(r["mean_without"] is not None
                                  and np.sign(r["mean_without"]) != np.sign(full) for r in rows))}


def nw_tstat(x, lag: int = 6) -> dict:
    """Newey-West t-stat for the mean of a time series (autocorrelation-robust)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 12:
        return {"n": n, "mean": float(x.mean()) if n else None, "t": None, "se": None}
    e = x - x.mean()
    g0 = (e @ e) / n
    s = g0
    for L in range(1, min(lag, n - 1) + 1):
        gL = (e[L:] @ e[:-L]) / n
        s += 2 * (1 - L / (lag + 1)) * gL
    se = np.sqrt(max(s, 0) / n)
    return {"n": int(n), "mean": float(x.mean()), "se": float(se),
            "t": float(x.mean() / se) if se > 0 else None}


def absorb(df: pd.DataFrame, cols: list[str], group: pd.Series) -> pd.DataFrame:
    """Within-group demeaning = exactly including that group's dummies, but cheap.

    Cells of size 1 demean to zero and therefore contribute no identifying variation. That is the
    correct behaviour (a single observation cannot compare anything), but it makes the EFFECTIVE
    sample smaller than the row count — reported separately as `n_eff_cells`.
    """
    g = df.groupby(group, observed=True)[cols].transform("mean")
    return df[cols] - g


def cluster2_ols(y: np.ndarray, X: np.ndarray, g1: np.ndarray, g2: np.ndarray,
                 n_absorbed: int = 0) -> dict:
    """OLS with two-way clustered (Cameron-Gelbach-Miller) standard errors.

    V = inv * (M(g1) + M(g2) - M(g1 x g2)) * inv.

    Clustering on the firm is not optional here: `serial` is a persistent firm state, so treating
    64k firm-months as independent draws would understate the SE by roughly sqrt(months per firm).
    """
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    inv = np.linalg.pinv(X.T @ X)
    beta = inv @ X.T @ y
    e = y - X @ beta

    def meat(g):
        M = np.zeros((X.shape[1], X.shape[1]))
        gs = np.asarray(g)
        for q in pd.unique(gs):
            sel = gs == q
            s = X[sel].T @ e[sel]
            M += np.outer(s, s)
        return M

    g1 = np.asarray(g1).astype(str)
    g2 = np.asarray(g2).astype(str)
    g12 = np.char.add(np.char.add(g1, "|"), g2)
    V = inv @ (meat(g1) + meat(g2) - meat(g12)) @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    n, k = len(y), X.shape[1] + n_absorbed
    dof = max(n - k, 1)
    return {"n": int(n), "beta": beta.tolist(), "se": se.tolist(),
            "t": [float(b / s) if s > 0 else None for b, s in zip(beta, se)],
            "dof": int(dof),
            "n_clusters_1": int(len(pd.unique(g1))), "n_clusters_2": int(len(pd.unique(g2))),
            "resid_ss": float(e @ e)}
