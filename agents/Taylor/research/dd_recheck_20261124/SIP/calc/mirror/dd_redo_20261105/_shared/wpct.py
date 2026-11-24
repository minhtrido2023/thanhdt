"""Phân vị có trọng số CHUẨN cho mọi DD redo (mid-block CDF). Dùng cho P10/P50/P90 ở MỨC KẾT CỤC."""
import numpy as np

def wpct(values, weights, qs=(0.10, 0.50, 0.90)):
    v = np.asarray(values, float); w = np.asarray(weights, float)
    assert len(v) == len(w) and (w >= 0).all() and w.sum() > 0
    o = np.argsort(v, kind="mergesort"); v, w = v[o], w[o] / w.sum()
    cdf = np.cumsum(w) - w / 2.0          # mid-block
    return {q: float(np.interp(q, cdf, v)) for q in qs}

def weight_below(values, weights, x):
    v = np.asarray(values, float); w = np.asarray(weights, float)
    return float(w[v < x].sum() / w.sum())
