"""Survivorship sensitivity overlay — job Taylor_20261020_082308. Theo PREREG.md (md5 98835b50).

Overlay "phantom loss" lên NAV ngày của ledger control R3 (không chạy lại engine), Monte Carlo 2000 lần,
seed 20261020, common random numbers. EXPLORATORY — không ghi registry/pin.

Usage: $DNA_PYEXE svs_overlay.py <out_dir> <label>=<ledger.csv> [<label>=<ledger.csv> ...]
"""
import sys, json, os
import numpy as np, pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
KBP = f"{WC}/mike/kb/projects"
DELIST = f"{KBP}/delisted-tickers-survivorship-20261020.csv"
TEST127 = f"{KBP}/delisted-tickers-survivorship-20261020.d/mandatory_delist_inData_8l_test.csv"
ZONE10 = ["PHH", "ATA", "PIV", "ALV", "IDC", "LMH", "PXS", "PHP", "BII", "DNM"]  # Winston §3
NSIM, SEED, NOISE_PP = 2000, 20261020, 0.46
LS = [0.30, 0.50, 0.80, 1.00]
LAM_GRID = [0.1, 0.25, 0.5, 1.0, 2.0, 3.0]
START, END = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-06-19")


def calc_metrics(s):  # nguyên văn pt_v23_audit_2014.py::calc_metrics (phần cần dùng)
    s = s.dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh252 = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    maxdd = (s / s.cummax() - 1).min()
    return dict(cagr=cagr, sharpe_252=sh252, max_dd=maxdd)


def load_ledger(path):
    df = pd.read_csv(path, low_memory=False)
    met = df[df.record_type == "METRIC"].set_index("key")["value"].astype(float)
    d = df[df.record_type == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d.ymd)
    d = d.set_index("ymd").sort_index()
    for c in ["combined_nav", "bal_stocks_ref", "lag_stocks_ref", "bal_etf_ref", "lag_etf_ref"]:
        d[c] = d[c].astype(float)
    tx = df[df.record_type == "TX"].copy()
    tx["ymd"] = pd.to_datetime(tx.ymd)
    tx["shares"] = tx.shares.astype(float)
    mem = df[df.record_type == "CUSTOM_MEMBERS"].copy()
    mem["ymd"] = pd.to_datetime(mem.ymd)
    return met, d, tx, mem


def open_positions(d, tx):
    """Tickers có net shares > 0 (theo book) cuối mỗi ngày DAILY."""
    tx = tx.sort_values("ymd", kind="stable")
    sgn = np.where(tx.action.str.startswith("buy"), 1.0, np.where(tx.action.str.startswith("sell"), -1.0, 0.0))
    if (sgn == 0).any():
        raise SystemExit(f"action lạ: {tx.action[sgn == 0].unique()}")
    tx = tx.assign(q=sgn * tx.shares)
    pos, out, by_day = {}, {}, {k: g for k, g in tx.groupby("ymd")}
    for day in d.index:
        if day in by_day:
            for (b, t), q in by_day[day].groupby(["book", "ticker"]).q.sum().items():
                pos[(b, t)] = pos.get((b, t), 0.0) + q
        out[day] = {t for (b, t), q in pos.items() if q > 1e-6}
    return out


def basket_members(d, mem):
    """Thành viên rổ có hiệu lực mỗi ngày (rổ mới nhất ≤ ngày), chỉ tính khi ETF>0."""
    snaps = {k: set(g.ticker) for k, g in mem.groupby("ymd")}
    keys = sorted(snaps)
    etf = d.bal_etf_ref + d.lag_etf_ref
    out, j = {}, -1
    for day in d.index:
        while j + 1 < len(keys) and keys[j + 1] <= day:
            j += 1
        out[day] = snaps[keys[j]] if (j >= 0 and etf[day] > 0) else set()
    return out


def name_weight(d, opn, bkt):
    eq = d.bal_stocks_ref + d.lag_stocks_ref + d.bal_etf_ref + d.lag_etf_ref
    n = pd.Series({k: len(opn[k]) + len(bkt[k]) for k in d.index})
    return (eq / d.combined_nav / n.replace(0, np.nan)).fillna(0.0), n


def held_in_window(tick, ann, opn, bkt):
    lo = ann - pd.Timedelta(days=365)
    return any((tick in opn[k] or tick in bkt[k]) for k in opn if lo <= k <= ann)


def delist_rate():
    d = pd.read_csv(DELIST)
    x = d[(~d.in_data) & d.yr.between(2014, 2025)]
    ex = x.exch2.fillna("NA")
    base = x[x.cat.isin(["bat_buoc", "khac_khong_ro", "tu_nguyen"]) & ex.isin(["HOSE", "HNX", "NA"])]
    wide = x[(x.cat.isin(["bat_buoc", "khac_khong_ro", "tu_nguyen"]) & ex.isin(["HOSE", "HNX", "NA"]))
             | ((x.cat == "mat_tu_cach_DC") & ex.isin(["HOSE", "HNX"]))
             | ((x.cat == "bat_buoc") & (ex == "UPCOM"))]
    return len(base) / 12.0, len(wide) / 12.0, len(base), len(wide)


class MC:
    def __init__(self, nav, w):
        self.nav = nav.values; self.idx = nav.index; self.w = w.reindex(nav.index).values
        self.days = (nav.index - nav.index[0]).days.values.astype(float)
        self.T = len(nav); self.years = self.days[-1] / 365.25
        rng = np.random.default_rng(SEED)
        self.u_n = rng.random(NSIM)                       # CRN cho N (inverse Poisson)
        self.u_t = rng.random((NSIM, 400))                # CRN cho ngày t1
        self.base = calc_metrics(nav)

    def _factor(self, i0, i1, L, shape):
        f = np.ones(self.T)
        span = max(self.days[i1] - self.days[i0], 1.0)
        seg = slice(i0, i1 + 1)
        G = self.nav[seg] / self.nav[i0]
        if shape == "linear":
            p = 1 - L * (self.days[seg] - self.days[i0]) / span
        else:  # cliff
            p = np.ones(i1 - i0 + 1); p[-1] = 1 - L
        f[seg] = 1 - self.w[i0] * (1 - p / G)
        f[i1 + 1:] = f[i1]
        return f

    def run(self, lam, L, shape="linear"):
        from scipy.stats import poisson
        Ns = poisson.ppf(self.u_n, lam * self.years).astype(int)
        if Ns.max() > self.u_t.shape[1]:
            raise SystemExit("tăng u_t")
        res = np.empty((NSIM, 3))
        for s in range(NSIM):
            F = np.ones(self.T)
            for k in range(Ns[s]):
                d1 = self.u_t[s, k] * self.days[-1]
                i1 = int(np.searchsorted(self.days, d1))
                i0 = int(np.searchsorted(self.days, max(self.days[i1] - 365.0, 0.0)))
                F *= self._factor(i0, i1, L, shape)
            m = calc_metrics(pd.Series(self.nav * F, index=self.idx))
            res[s] = (m["cagr"] - self.base["cagr"], m["sharpe_252"] - self.base["sharpe_252"],
                      m["max_dd"] - self.base["max_dd"])
        q = lambda a: (np.median(a), np.quantile(a, 0.05), np.quantile(a, 0.95))
        out = dict(lam=lam, L=L, shape=shape, mean_events=float(Ns.mean()))
        for j, nm in enumerate(["dcagr_pp", "dsharpe", "dmaxdd_pp"]):
            sc = 100 if nm.endswith("pp") else 1
            md, lo, hi = q(res[:, j]); out.update({f"{nm}_med": md * sc, f"{nm}_p05": lo * sc, f"{nm}_p95": hi * sc})
        return out


def main():
    out_dir = sys.argv[1]; legs = dict(a.split("=", 1) for a in sys.argv[2:])
    D, Dw, nD, nDw = delist_rate()
    t127 = pd.read_csv(TEST127, parse_dates=["ann"])
    summary = dict(D_per_yr=D, Dplus_per_yr=Dw, n_D_2014_2025=nD, n_Dplus_2014_2025=nDw, legs={})
    rows = []
    for label, path in legs.items():
        met, d, tx, mem = load_ledger(path)
        nav = d.combined_nav
        m = calc_metrics(nav)
        err = {k: abs(m[k] - met[k]) for k in m}
        if max(err.values()) > 1e-9:
            raise SystemExit(f"{label}: không tái tạo METRIC {err}")
        opn = open_positions(d, tx); bkt = basket_members(d, mem)
        w, n = name_weight(d, opn, bkt)
        held127 = [t for t, a in zip(t127.ticker, t127.ann) if START <= a and held_in_window(t, a, opn, bkt)]
        a10 = t127.set_index("ticker").ann
        held10 = [t for t in ZONE10 if held_in_window(t, a10[t], opn, bkt)]
        n127 = int((t127.ann >= START).sum())
        p_hold = len(held10) / len(ZONE10); p_emp = len(held127) / n127
        scen = {
            "trung_vi": (D * 0.10 * p_hold, 0.50),
            "emp_L50": (D * p_emp, 0.50),
            "xau_nhat_hop_ly": (Dw * 0.20 * 1.0, 1.00),
            "zone5_hold1_L50": (D * 0.05, 0.50), "zone10_hold1_L50": (D * 0.10, 0.50),
            "zone20_hold1_L50": (D * 0.20, 0.50),
        }
        mc = MC(nav, w)
        info = dict(ledger=path, metric_recompute_maxerr=max(err.values()), base=m,
                    w_mean=float(w[w > 0].mean()), w_median=float(w[w > 0].median()), n_names_median=float(n.median()),
                    held10=held10, p_hold=p_hold, n127_in_window=n127, held127=held127, p_emp=p_emp,
                    scenarios={k: dict(lam=v[0], L=v[1]) for k, v in scen.items()})
        for nm, (lam, L) in scen.items():
            for shape in ["linear", "cliff"]:
                r = mc.run(lam, L, shape); r.update(leg=label, kind="scenario", name=nm); rows.append(r)
        for lam in LAM_GRID:
            for L in LS:
                r = mc.run(lam, L); r.update(leg=label, kind="grid", name=f"lam{lam}_L{L}"); rows.append(r)
        g = pd.DataFrame([r for r in rows if r["leg"] == label and r["kind"] == "grid"])
        be = {}
        for L in LS:
            gg = g[g.L == L].sort_values("lam")
            x = np.r_[0.0, gg.lam.values]; y = np.r_[0.0, gg.dcagr_pp_med.values]
            be[str(L)] = float(np.interp(-0.5, y[::-1], x[::-1])) if y.min() <= -0.5 else None
        info["breakeven_lam_for_-0.5pp"] = be
        summary["legs"][label] = info
        print(label, json.dumps({k: info[k] for k in ["base", "w_mean", "held10", "p_hold", "p_emp", "breakeven_lam_for_-0.5pp"]}, default=str), flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "out_mc_results.csv"), index=False)
    with open(os.path.join(out_dir, "out_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)


if __name__ == "__main__":
    main()
