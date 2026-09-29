#!/usr/bin/env python3
"""Doc metric FULL / IS(2014-19) / OOS(2020+) tu mot ledger audit — job Taylor_20260927_170645.

Cong thuc COPY nguyen tu `simulate_holistic_nav.metrics` (nguon sinh moi so trong
data/results_registry.md): annualize theo THOI GIAN LICH ((t_last-t_first).days/365.25),
sessions_per_year = len(rets)/n_yrs (KHONG phai 252 cung). Khong tu nghi cong thuc moi —
so IS/OOS phai so sanh duoc voi so FULL ma engine tu in ra.

  leg_metrics.py <ledger.csv> [<ledger2.csv> ...]
"""
import hashlib, sys
import numpy as np, pandas as pd

def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna()].copy()
    tc = [c for c in d.columns if c.lower() in ("time", "ymd", "date")][0]
    t = pd.to_datetime(d[tc], errors="coerce")
    d, t = d[t.notna()], t[t.notna()]
    return d.groupby(t.dt.normalize())["combined_nav"].last().astype(float)

def met(nav):
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / n_yrs) - 1
    r = nav.pct_change().dropna()
    spy = len(r) / n_yrs
    sharpe = r.mean() / r.std() * np.sqrt(spy)
    dd = ((nav - nav.cummax()) / nav.cummax()).min()
    return {"first": str(nav.index[0].date()), "last": str(nav.index[-1].date()),
            "yrs": round(n_yrs, 3), "n_obs": len(nav),
            "nav0_B": round(nav.iloc[0] / 1e9, 4), "navT_B": round(nav.iloc[-1] / 1e9, 4),
            "CAGR_pct": round(cagr * 100, 2), "Sharpe": round(sharpe, 2),
            "MaxDD_pct": round(dd * 100, 1), "Calmar": round(cagr / abs(dd), 2)}

def md5(p, c=1 << 20):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(c), b""):
            h.update(b)
    return h.hexdigest()

if __name__ == "__main__":
    for p in sys.argv[1:]:
        nav = load_nav(p)
        print(f"\n== {p.rsplit('/', 1)[-1]}\n   md5 {md5(p)}")
        for lbl, s in (("FULL", nav),
                       ("IS 2014-19", nav.loc[:"2019-12-31"]),
                       ("OOS 2020+", nav.loc["2020-01-01":])):
            if len(s) < 3:
                print(f"   {lbl:<11} (khong du quan sat: {len(s)})"); continue
            m = met(s)
            print(f"   {lbl:<11} {m['first']}..{m['last']} {m['yrs']:>6.2f}y n={m['n_obs']:<5} "
                  f"NAV {m['nav0_B']:>8.3f}B -> {m['navT_B']:>8.3f}B  CAGR {m['CAGR_pct']:>6.2f}%  "
                  f"Sharpe {m['Sharpe']:>5.2f}  MaxDD {m['MaxDD_pct']:>6.1f}%  Calmar {m['Calmar']:>5.2f}")
