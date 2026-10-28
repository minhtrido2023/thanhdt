"""cluster_boot + holm — bản sao NGUYÊN VĂN từ nav_overlay.py (dùng chung cho lag_events.py, tránh chạy overlay khi import)."""
import numpy as np
SEED, NB = 20261022, 2000

def cluster_boot(vals, clus, mask_a=None, stat="mean", seed=SEED):
    """Bootstrap cụm. stat mean (Δ trung bình của vals) hoặc diff (mean vals|a − mean vals|~a)."""
    us, ci = np.unique(clus, return_inverse=True)
    rng = np.random.default_rng(seed)
    nc = len(us)
    if stat == "mean":
        s = np.bincount(ci, weights=vals, minlength=nc); n = np.bincount(ci, minlength=nc).astype(float)
        est = s.sum() / n.sum()
        bs = []
        for _ in range(NB):
            b = rng.integers(0, nc, nc); bs.append(s[b].sum() / n[b].sum())
    else:
        a = mask_a
        sA = np.bincount(ci, weights=vals * a, minlength=nc); nA = np.bincount(ci, weights=a.astype(float), minlength=nc)
        sB = np.bincount(ci, weights=vals * ~a, minlength=nc); nB = np.bincount(ci, weights=(~a).astype(float), minlength=nc)
        est = sA.sum() / nA.sum() - sB.sum() / nB.sum()
        bs = []
        for _ in range(NB):
            b = rng.integers(0, nc, nc)
            bs.append(sA[b].sum() / max(nA[b].sum(), 1) - sB[b].sum() / max(nB[b].sum(), 1))
    bs = np.array(bs)
    p = min(2 * min((bs >= 0).mean(), (bs <= 0).mean()), 1.0)
    return est, np.percentile(bs, [2.5, 97.5]), p, nc


def holm(ps, alpha=0.05):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); ok = np.zeros(m, bool)
    for i, j in enumerate(o):
        if ps[j] <= alpha / (m - i): ok[j] = True
        else: break
    return ok


