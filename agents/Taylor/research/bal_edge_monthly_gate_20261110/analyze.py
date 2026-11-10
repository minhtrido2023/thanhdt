"""Analysis — BAL monthly gate vs BLIND (job Taylor_20261110_053025). Writes results.json + tables.
Reads engine ledgers (data/*_exp_bg_<tag>_univpit[_idledep1m].csv) + logs (self-check lines)."""
import os, re, json, glob, hashlib
import numpy as np, pandas as pd
import approx

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
PFX = WC + "/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp_"
PIN = {"off": "537e349b5589408c994f8aceafeb9a39", "1m": "a6ba34d83a4d374a73293d897c0b43d9"}
VARS = ["G1_L0", "G1_L1", "G1_L2", "G2_3m_L0", "G3_x2_L0", "G4_hu2_L0", "G5_hl2_L0", "G6_n3_L0", "G1_L0capx"]
L, B, SEED = 21, 4000, 12345


def path(tag, c):
    return PFX + f"bg_{tag}_{c}_univpit" + ("_idledep1m" if c == "1m" else "") + ".csv"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_daily(p):
    d = pd.read_csv(p, low_memory=False, usecols=["record_type", "ymd", "combined_nav", "nav_bal_ref", "nav_lag_ref",
                                                   "bal_stocks_ref", "lag_stocks_ref", "state"])
    d = d[d.record_type == "DAILY"].copy(); d["ymd"] = pd.to_datetime(d["ymd"])
    return d.sort_values("ymd").set_index("ymd")


def selfcheck(tag, c):
    lg = open(f"{HERE}/logs/bg_{tag}_{c}.log").read()
    ok = len(re.findall(r"cash-flow identity max err = 0 VND; final NAV identity err = 0 VND", lg)) == 2
    blk = re.findall(r"\[BAL_BUY_BLOCK\].*first-fills blocked=(\d+)", lg)
    return ok, (int(blk[-1]) if blk else 0), ("EXIT=0" in lg)


def met(nav):
    nav = pd.Series(nav)
    idx = nav.index
    yrs = (idx[-1] - idx[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr, sharpe=r.mean() / r.std() * np.sqrt(252), maxdd=dd, calmar=cagr / -dd)


def met_r(r, yrs):
    nav = np.cumprod(1 + r)
    cagr = nav[-1] ** (1 / yrs) - 1
    dd = (nav / np.maximum.accumulate(nav) - 1).min()
    return cagr, r.mean() / r.std() * np.sqrt(252), dd, cagr / -dd


def split(nav, a, b):
    s = nav[(nav.index >= a) & (nav.index <= b)]
    return met(s)


def paired_boot(ra, rb, yrs):
    """circular block bootstrap with one common index; returns P(delta>0) and 90% CI for each metric"""
    rng = np.random.default_rng(SEED); n = len(ra); nb = int(np.ceil(n / L))
    out = []
    for _ in range(B):
        st = rng.integers(0, n, nb)
        ix = (st[:, None] + np.arange(L)[None, :]).ravel()[:n] % n
        a = met_r(ra[ix], yrs); b = met_r(rb[ix], yrs)
        out.append([a[i] - b[i] for i in range(4)])
    o = np.array(out); k = ["cagr", "sharpe", "maxdd", "calmar"]
    return {k[i]: dict(p_gt0=float((o[:, i] > 0).mean()), ci90=[float(np.percentile(o[:, i], 5)), float(np.percentile(o[:, i], 95))])
            for i in range(4)}


def loo_year(navg, navb):
    rg = navg.pct_change().fillna(0); rb = navb.pct_change().fillna(0); out = {}
    for y in sorted(set(navg.index.year)):
        m = navg.index.year != y
        yrs = m.sum() / 252 * (12.46 * 252 / len(navg))   # calendar-equivalent years
        a = met_r(rg[m].values, yrs); b = met_r(rb[m].values, yrs)
        out[int(y)] = dict(dcagr=a[0] - b[0], dsharpe=a[1] - b[1], dcalmar=a[3] - b[3])
    return out


def per_year(navg, navb):
    yg = navg.resample("YE").last().pct_change(); yb = navb.resample("YE").last().pct_change()
    yg.iloc[0] = navg.resample("YE").last().iloc[0] / navg.iloc[0] - 1; yb.iloc[0] = navb.resample("YE").last().iloc[0] / navb.iloc[0] - 1
    return {int(k.year): float(yg[k] - yb[k]) for k in yg.index}


def main():
    R = {"controls": {}, "legs": {}}
    blind = {}
    for c in ["off", "1m"]:
        p = path("ctl", c); h = md5(p); sc = selfcheck("ctl", c)
        R["controls"][c] = dict(md5=h, pin=PIN[c], byte_identical=(h == PIN[c]), selfcheck0=sc[0], exit0=sc[2])
        blind[c] = load_daily(p)
        R["controls"][c]["full"] = met(blind[c]["combined_nav"])
    yrs = (blind["off"].index[-1] - blind["off"].index[0]).days / 365.25
    for c in ["off", "1m"]:
        nb = blind[c]["combined_nav"]; rb = nb.pct_change().fillna(0).values
        for v in VARS + ["LAG_G1_L0"] + [f"PLAC{j}" for j in range(8)]:
            p = path(v, c)
            if not os.path.exists(p):
                continue
            g = load_daily(p); ng = g["combined_nav"]
            sc = selfcheck(v, c)
            fg, fb = met(ng), met(nb)
            e = dict(md5=md5(p), selfcheck0=sc[0], exit0=sc[2], blocked_first_fills=sc[1], full=fg,
                     delta={k: fg[k] - fb[k] for k in fg},
                     IS={k: split(ng, "2014-01-01", "2019-12-31")[k] - split(nb, "2014-01-01", "2019-12-31")[k] for k in fg},
                     OOS={k: split(ng, "2020-01-01", "2026-12-31")[k] - split(nb, "2020-01-01", "2026-12-31")[k] for k in fg},
                     bal_book=dict(gate=met(g["nav_bal_ref"]), blind=met(blind[c]["nav_bal_ref"])),
                     lag_book=dict(gate=met(g["nav_lag_ref"]), blind=met(blind[c]["nav_lag_ref"])),
                     bal_expo=dict(gate=float((g.bal_stocks_ref / g.nav_bal_ref).mean()),
                                   blind=float((blind[c].bal_stocks_ref / blind[c].nav_bal_ref).mean())))
            rg = ng.pct_change().fillna(0).values
            e["boot"] = paired_boot(rg, rb, yrs)
            e["loo_year"] = loo_year(ng, nb)
            e["per_year_dret"] = per_year(ng, nb)
            e["excess_daily"] = None
            R["legs"][f"{v}_{c}"] = e
            print(f"{v:12s} {c:3s} dCAGR {e['delta']['cagr']*100:+.2f}pp dSh {e['delta']['sharpe']:+.3f} "
                  f"dDD {e['delta']['maxdd']*100:+.2f}pp dCal {e['delta']['calmar']:+.3f} | IS {e['IS']['cagr']*100:+.2f} OOS {e['OOS']['cagr']*100:+.2f} "
                  f"| P(dCal>0) {e['boot']['calmar']['p_gt0']:.2f} P(dSh>0) {e['boot']['sharpe']['p_gt0']:.2f} | blk {sc[1]} sc0 {sc[0]}")
    json.dump(R, open(f"{HERE}/results.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()


# ---------------- DSR / PBO (family = 9 gate variants + BLIND) ----------------
def dsr_pbo(carry="off", S=16):
    from scipy.stats import norm, skew, kurtosis
    from itertools import combinations
    cols = {"BLIND": load_daily(path("ctl", carry))["combined_nav"]}
    for v in VARS:
        p = path(v, carry)
        if os.path.exists(p):
            cols[v] = load_daily(p)["combined_nav"]
    R = pd.DataFrame(cols).pct_change().dropna()
    ex = R.drop(columns="BLIND").sub(R["BLIND"], axis=0)        # excess daily vs blind
    sr = ex.mean() / ex.std()                                   # per-period SR of excess
    n = len(ex); N = ex.shape[1]; var_sr = sr.var(ddof=1)
    emc = 0.5772156649
    sr0 = np.sqrt(var_sr) * ((1 - emc) * norm.ppf(1 - 1 / N) + emc * norm.ppf(1 - 1 / (N * np.e)))
    best = sr.idxmax(); x = ex[best]
    g3, g4 = skew(x), kurtosis(x, fisher=False)
    dsr = norm.cdf((sr[best] - sr0) * np.sqrt(n - 1) / np.sqrt(1 - g3 * sr[best] + (g4 - 1) / 4 * sr[best] ** 2))
    # CSCV PBO over all configs incl. BLIND (selection on Sharpe)
    blocks = np.array_split(np.arange(len(R)), S); lam = []
    for c in combinations(range(S), S // 2):
        IS = np.concatenate([blocks[i] for i in c]); OS = np.concatenate([blocks[i] for i in range(S) if i not in c])
        si = R.iloc[IS].mean() / R.iloc[IS].std(); so = R.iloc[OS].mean() / R.iloc[OS].std()
        k = si.idxmax(); rank = so.rank().loc[k] / (len(so) + 1)
        lam.append(np.log(rank / (1 - rank)))
    lam = np.array(lam)
    return dict(carry=carry, n_trials=int(N), best=best, best_excess_sr_ann=float(sr[best] * np.sqrt(252)),
                excess_sr_ann={k: float(v * np.sqrt(252)) for k, v in sr.items()}, sr0_ann=float(sr0 * np.sqrt(252)),
                dsr=float(dsr), pbo=float((lam <= 0).mean()), n_splits=len(lam),
                is_best_blind_share=None)


if __name__ == "__main__" and os.environ.get("DSR", "1") == "1":
    R = json.load(open(f"{HERE}/results.json"))
    R["dsr_pbo"] = {c: dsr_pbo(c) for c in ["off", "1m"]}
    print(json.dumps(R["dsr_pbo"], indent=1))
    json.dump(R, open(f"{HERE}/results.json", "w"), indent=1, default=float)
