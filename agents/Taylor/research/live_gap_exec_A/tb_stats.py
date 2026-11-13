"""Tie-break noise floor (Luồng A, job Taylor_20261112_162004).
Usage: tb_stats.py <ledger_dir>   — FULL metrics (DAILY combined_nav, năm lịch, Sharpe lịch sqrt(n/yrs)) cho
L0..L4 + TB1..TBn, sd seed cho từng đầu dải, |Δ| mỗi bước ladder so với sd."""
import sys, glob, re, numpy as np, pandas as pd
D = sys.argv[1]
def met(p):
    X = pd.read_csv(p, low_memory=False); X = X[X.record_type == "DAILY"]
    t = pd.to_datetime(X["ymd"].astype(str)); v = X["combined_nav"].astype(float).values
    yrs = (t.iloc[-1] - t.iloc[0]).days / 365.25; cagr = (v[-1] / v[0]) ** (1 / yrs) - 1
    r = np.diff(np.log(v)); sh = r.mean() / r.std(ddof=1) * np.sqrt(len(r) / yrs)
    dd = (v / np.maximum.accumulate(v) - 1).min()
    return dict(CAGR=100 * cagr, Sharpe=sh, MaxDD=100 * dd, Calmar=cagr / -dd)
rows = {}
for p in glob.glob(f"{D}/*_exp_*_univpit*.csv"):
    m = re.search(r"_exp_((?:L\d|TB\d+)_(?:off|1m))_univpit", p)
    if m: rows[m.group(1)] = met(p)
R = pd.DataFrame(rows).T
for band in ("off", "1m"):
    L = R.loc[[f"L{i}_{band}" for i in range(5) if f"L{i}_{band}" in R.index]]
    T = R.loc[sorted([i for i in R.index if i.startswith("TB") and i.endswith("_" + band)], key=lambda s: int(s[2:].split("_")[0]))]
    print(f"\n=== band {band}: ladder\n{L.round(3).to_string()}")
    print(f"--- tie-break n={len(T)}\n{T.round(3).to_string()}")
    sd = T.std(ddof=1); print(f"--- TB mean\n{T.mean().round(3).to_string()}\n--- TB sd\n{sd.round(3).to_string()}")
    print(f"--- TB min/max CAGR {T.CAGR.min():.2f}/{T.CAGR.max():.2f}  MaxDD {T.MaxDD.min():.2f}/{T.MaxDD.max():.2f}")
    dl = L.diff().dropna()
    print("--- |Δ| bước / sd_TB (CAGR, MaxDD, Sharpe)")
    for k, d in dl.iterrows():
        print(f"  {k}: ΔCAGR {d.CAGR:+.2f}pp ({abs(d.CAGR)/sd.CAGR:.1f} sd) ΔMaxDD {d.MaxDD:+.2f}pp ({abs(d.MaxDD)/sd.MaxDD:.1f} sd) ΔSharpe {d.Sharpe:+.3f} ({abs(d.Sharpe)/sd.Sharpe:.1f} sd)")
