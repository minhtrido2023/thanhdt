#!/usr/bin/env python3
"""T2 — backtest of long-horizon TREND-BREAK signals on the WB monthly RSS3 series.

Question asked by the user: does "RSS3 breaks its 100-day trendline / MA200" flag a REAL
cycle reversal, unlike the short-horizon % moves already wired (WATCH/ALERT)?

The daily feed cannot answer it (34 real prints, 47 calendar days — T1). The only series
long enough is data/rubber_monthly.csv (WB Pink Sheet, 244 months, 2006-04..2026-07, no
month missing). Daily windows are mapped at 21 trading days/month:
    MA200 daily ~ MA10 monthly     MA100 daily ~ MA5 monthly
and the linear-regression variant is a 5-month OLS trendline (100 sessions).

NO LOOK-AHEAD:
  * MA/trendline at month t use months <= t only (rolling, closed on the right).
  * A WB monthly point is a MONTHLY AVERAGE, not a month-end close, so the value at t is
    not fully tradable at t. Every forward return is therefore measured from t+1, and the
    "confirmed" variants only act at t+1/t+2. Publication lag of the Pink Sheet (~first
    week of the following month) is covered by the same t+1 shift.
"""
import numpy as np, pandas as pd
from itertools import groupby

W = "/home/trido/thanhdt/WorkingClaude"
m = pd.read_csv(f"{W}/data/rubber_monthly.csv")
m["dt"] = pd.to_datetime(m["month"].astype(str) + "-15")
m = m[m["price"].notna()].sort_values("dt").reset_index(drop=True)
p = pd.Series(m["price"].astype(float).values, index=m["dt"])
N_OBS = len(p)


# ------------------------------------------------------------------ signals -----
def ma_break(price, win):
    """Down-break of MA<win>: close crosses from >= MA to < MA. Causal."""
    ma = price.rolling(win).mean()
    below = price < ma
    # first month of a below-run, and MA must exist
    sig = below & ~below.shift(1, fill_value=False) & ma.notna()
    return sig, ma, below


def reg_break(price, win):
    """Down-break of a rolling OLS trendline fitted on the last <win> months.
    Trendline value at t = fitted value at the LAST point of the window (causal)."""
    x = np.arange(win, dtype=float)
    fit = pd.Series(np.nan, index=price.index)
    v = price.values
    for i in range(win - 1, len(v)):
        y = v[i - win + 1:i + 1]
        b, a = np.polyfit(x, y, 1)          # y = a + b*x
        fit.iloc[i] = a + b * (win - 1)
    below = price < fit
    sig = below & ~below.shift(1, fill_value=False) & fit.notna()
    return sig, fit, below


def confirm(sig, below, k):
    """Require k consecutive months below the line. The event date moves to the k-th
    month (that is when we would actually know it), so no look-ahead is smuggled in."""
    if k <= 1:
        return sig
    run = below & below.shift(1, fill_value=False)
    for j in range(2, k):
        run &= below.shift(j, fill_value=False)
    # k-th consecutive month below, and the run started with a genuine cross
    return run & ~run.shift(1, fill_value=False)


# ------------------------------------------------------------------ evaluation --
def fwd(price, i, h):
    """Return from t+1 to t+1+h (act one month after the signal is known)."""
    if i + 1 + h >= len(price):
        return None
    return float(price.iloc[i + 1 + h] / price.iloc[i + 1] - 1) * 100


HORIZONS = (3, 6, 12)


def base_rates(price):
    out = {}
    for h in HORIZONS:
        r = [fwd(price, i, h) for i in range(len(price))]
        r = [x for x in r if x is not None]
        out[h] = (np.mean(r), np.median(r), np.mean([x < 0 for x in r]) * 100, len(r))
    return out


def evaluate(name, sig, price, below):
    idx = [i for i, s in enumerate(sig.values) if s]
    rows = []
    for i in idx:
        rec = {"date": price.index[i].strftime("%Y-%m"), "px": float(price.iloc[i])}
        for h in HORIZONS:
            rec[f"f{h}"] = fwd(price, i, h)
        # whipsaw: back above the line within 2 months?
        nxt = below.iloc[i + 1:i + 3]
        rec["whip2"] = bool(len(nxt) and (~nxt).any())
        rows.append(rec)
    df = pd.DataFrame(rows)
    return name, df


def summarize(name, df, base):
    n = len(df)
    print(f"\n--- {name}  (N = {n} events) ---")
    if n == 0:
        print("  no events")
        return
    print(f"  whipsaw (back above line within 2m): {df['whip2'].sum()}/{n} "
          f"= {df['whip2'].mean()*100:.0f}%")
    for h in HORIZONS:
        v = df[f"f{h}"].dropna()
        if not len(v):
            continue
        bm, bmed, bneg, bn = base[h]
        # LOO: drop each event, worst-case mean (small-N discipline)
        loo = [np.mean(np.delete(v.values, k)) for k in range(len(v))] if len(v) > 1 else [v.mean()]
        # bootstrap CI on the mean
        rng = np.random.default_rng(7)
        bs = [np.mean(rng.choice(v.values, len(v), replace=True)) for _ in range(5000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"  fwd {h:2d}m: mean {v.mean():+6.2f}%  (base {bm:+6.2f}%, edge {v.mean()-bm:+6.2f}pp)"
              f"  CI95 [{lo:+.1f},{hi:+.1f}]  n={len(v)}"
              f"  | P(down) {np.mean(v<0)*100:4.0f}% vs base {bneg:4.0f}%"
              f"  | LOO mean range [{min(loo):+.1f},{max(loo):+.1f}]")


print("=" * 78)
print(f"WB monthly RSS3 — N_obs = {N_OBS} months, {p.index[0]:%Y-%m} .. {p.index[-1]:%Y-%m}")
base = base_rates(p)
print("Unconditional base rates (every month, act t+1):")
for h in HORIZONS:
    bm, bmed, bneg, bn = base[h]
    print(f"  fwd {h:2d}m: mean {bm:+6.2f}%  median {bmed:+6.2f}%  P(down) {bneg:4.0f}%  n={bn}")
print("=" * 78)

variants = []
for win, lbl in ((10, "MA10 monthly  (~MA200 daily)"), (5, "MA5 monthly   (~MA100 daily)")):
    sig, ma, below = ma_break(p, win)
    for k in (1, 2):
        variants.append((f"{lbl}, confirm {k}m", confirm(sig, below, k), below))
sig, fit, below = reg_break(p, 5)
for k in (1, 2):
    variants.append((f"OLS trendline 5m (~100d), confirm {k}m", confirm(sig, below, k), below))

results = {}
for name, s, b in variants:
    nm, df = evaluate(name, s, p, b)
    results[nm] = df
    summarize(nm, df, base)

# ------------------------------------------------------------------ cycle test --
print("\n" + "=" * 78)
print("CYCLE TEST — did a confirmed MA10 break flag the real peak-to-trough declines?")
print("=" * 78)
# real cycles: local peak -> subsequent trough with >= 30% decline
px = p.values
peaks = []
i = 0
while i < len(px):
    # running max, then find the trough after it
    j = int(np.argmax(px[i:])) + i
    k = int(np.argmin(px[j:])) + j
    dd = px[k] / px[j] - 1
    if dd <= -0.30 and k > j:
        peaks.append((j, k, dd))
        i = k + 1
    else:
        break
sig10, ma10, below10 = ma_break(p, 10)
sig10c = confirm(sig10, below10, 2)
ev = [i for i, s in enumerate(sig10c.values) if s]
for j, k, dd in peaks:
    after = [e for e in ev if e >= j]
    if after:
        e = after[0]
        rem = px[k] / px[e + 1] - 1 if e + 1 < len(px) else float("nan")
        print(f"  peak {p.index[j]:%Y-%m} {px[j]:.2f} -> trough {p.index[k]:%Y-%m} {px[k]:.2f} "
              f"({dd*100:+.0f}%) | first confirmed break {p.index[e]:%Y-%m} "
              f"= {e-j} months after peak, {(px[e]/px[j]-1)*100:+.0f}% of the fall already gone, "
              f"remaining from t+1 {rem*100:+.0f}%")
    else:
        print(f"  peak {p.index[j]:%Y-%m} -> trough {p.index[k]:%Y-%m} ({dd*100:+.0f}%) | NO break found")

# how many confirmed breaks are NOT inside a >=30% cycle decline (false alarms)
in_cycle = set()
for j, k, dd in peaks:
    in_cycle.update(range(j, k + 1))
fa = [e for e in ev if e not in in_cycle]
print(f"\n  confirmed MA10 breaks total: {len(ev)} | inside a >=30% decline: {len(ev)-len(fa)} "
      f"| outside (false alarm): {len(fa)} -> {[p.index[e].strftime('%Y-%m') for e in fa]}")

# ------------------------------------------------------------------ frequency ---
print("\n" + "=" * 78)
print("FIRING FREQUENCY (how noisy would the new tier be?)")
for name, df in results.items():
    if len(df):
        yrs = (p.index[-1] - p.index[0]).days / 365.25
        print(f"  {name:42s}: {len(df):3d} events / {yrs:.1f}y = 1 per {yrs*12/len(df):.1f} months")
