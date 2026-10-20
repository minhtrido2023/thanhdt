"""Survivorship sensitivity v2 — trọng số phantom theo book. Theo PREREG.md (md5 f9092a9e). EXPLORATORY.
Usage: $DNA_PYEXE svs_overlay_v2.py <out_dir> <label>=<ledger.csv> ...
"""
import sys, json, os
import numpy as np, pandas as pd
from scipy.stats import poisson
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/survivorship_sensitivity_20261020")
from svs_overlay import calc_metrics, load_ledger, NSIM, SEED, NOISE_PP, LS

LAM_GRID = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0]


def book_counts(d, tx):
    """n_b(d): số vị thế cổ phiếu mở cuối mỗi ngày DAILY, theo book."""
    tx = tx.sort_values("ymd", kind="stable")
    if not tx.action.str.startswith(("buy", "sell")).all():
        raise SystemExit(f"action lạ: {tx.action.unique()}")
    tx = tx.assign(q=np.where(tx.action.str.startswith("buy"), 1.0, -1.0) * tx.shares)
    pos, by_day = {}, {k: g for k, g in tx.groupby("ymd")}
    out = {"BAL": [], "LAG": []}
    for day in d.index:
        if day in by_day:
            for (b, t), q in by_day[day].groupby(["book", "ticker"]).q.sum().items():
                pos[(b, t)] = pos.get((b, t), 0.0) + q
        for b in out:
            out[b].append(sum(1 for (bb, t), q in pos.items() if bb == b and q > 1e-6))
    return {b: pd.Series(v, index=d.index) for b, v in out.items()}


class MC:
    def __init__(self, nav):
        self.nav = nav.values; self.idx = nav.index
        self.days = (nav.index - nav.index[0]).days.values.astype(float)
        self.T = len(nav); self.years = self.days[-1] / 365.25
        rng = np.random.default_rng(SEED)
        self.u_n = rng.random(NSIM); self.u_t = rng.random((NSIM, 400)); self.u_b = rng.random((NSIM, 400))
        self.base = calc_metrics(nav)

    def _factor(self, i0, i1, L, w):
        f = np.ones(self.T)
        span = max(self.days[i1] - self.days[i0], 1.0)
        seg = slice(i0, i1 + 1)
        G = self.nav[seg] / self.nav[i0]
        p = 1 - L * (self.days[seg] - self.days[i0]) / span
        f[seg] = 1 - w * (1 - p / G)
        f[i1 + 1:] = f[i1]
        return f

    def run(self, lam, L, wfun):
        Ns = poisson.ppf(self.u_n, lam * self.years).astype(int)
        if Ns.max() > self.u_t.shape[1]:
            raise SystemExit("tăng u_t")
        res = np.empty(NSIM)
        for s in range(NSIM):
            F = np.ones(self.T)
            for k in range(Ns[s]):
                d1 = self.u_t[s, k] * self.days[-1]
                i1 = int(np.searchsorted(self.days, d1))
                i0 = int(np.searchsorted(self.days, max(self.days[i1] - 365.0, 0.0)))
                F *= self._factor(i0, i1, L, wfun(self.u_b[s, k]))
            res[s] = calc_metrics(pd.Series(self.nav * F, index=self.idx))["cagr"] - self.base["cagr"]
        return dict(lam=lam, L=L, mean_events=float(Ns.mean()), dcagr_pp_med=float(np.median(res) * 100),
                    dcagr_pp_p05=float(np.quantile(res, .05) * 100), dcagr_pp_p95=float(np.quantile(res, .95) * 100))


def breakeven(g, thr):
    out = {}
    for L in LS:
        gg = g[g.L == L].sort_values("lam")
        x = np.r_[0.0, gg.lam.values]; y = np.r_[0.0, gg.dcagr_pp_med.values]
        out[str(L)] = float(np.interp(-thr, y[::-1], x[::-1])) if y.min() <= -thr else None
    return out


def main():
    out_dir = sys.argv[1]; legs = dict(a.split("=", 1) for a in sys.argv[2:])
    rows, summary = [], {"noise_pp": NOISE_PP, "legs": {}}
    for label, path in legs.items():
        met, d, tx, mem = load_ledger(path)
        nav = d.combined_nav
        m = calc_metrics(nav)
        err = max(abs(m[k] - met[k]) for k in m)
        if err > 1e-9:
            raise SystemExit(f"{label}: không tái tạo METRIC {err}")
        n = book_counts(d, tx)
        ref = {"BAL": d.bal_stocks_ref, "LAG": d.lag_stocks_ref}
        w, nmean = {}, {}
        for b in n:
            ok = n[b] >= 1
            wb = (ref[b] / d.combined_nav / n[b].where(ok))[ok]
            w[b] = float(wb.median()); nmean[b] = float(n[b][ok].mean())
        tot = sum(nmean.values()); share = {b: nmean[b] / tot for b in n}
        cfgs = {"BAL": lambda u: w["BAL"], "LAG": lambda u: w["LAG"],
                "MIX": lambda u: w["BAL"] if u < share["BAL"] else w["LAG"]}
        info = dict(ledger=path, metric_err=err, base=m, w_median=w, n_mean=nmean, share=share,
                    days_active={b: int((n[b] >= 1).sum()) for b in n})
        mc = MC(nav)
        for cfg, fn in cfgs.items():
            for lam in LAM_GRID:
                for L in LS:
                    r = mc.run(lam, L, fn); r.update(leg=label, cfg=cfg); rows.append(r)
            g = pd.DataFrame([r for r in rows if r["leg"] == label and r["cfg"] == cfg])
            info[f"lam_star_{cfg}"] = {"0.46": breakeven(g, 0.46), "0.50": breakeven(g, 0.50)}
        summary["legs"][label] = info
        print(label, json.dumps({k: info[k] for k in ["w_median", "n_mean", "share"]}), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "out_mc_results.csv"), index=False)
    with open(os.path.join(out_dir, "out_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)


if __name__ == "__main__":
    main()
