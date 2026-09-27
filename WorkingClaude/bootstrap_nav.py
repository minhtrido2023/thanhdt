"""Bootstrap robustness on a strategy's daily NAV — the workflow STEP 3.5 tool.

WHEN to run (NOT on every research variant — that is the multiple-testing trap):
  only on a config that has ALREADY passed walk-forward IS/OOS AND is one of:
    (a) a config being promoted to production/go-live,
    (b) a leverage/sizing decision,
    (c) Spyros needs a quantified DD tail to calibrate the breaker.

WHAT it answers (complements, does NOT replace, walk-forward):
  walk-forward = "does the edge survive in unseen TIME / is it period-overfit?" (structural)
  bootstrap    = "given this return distribution, how much could LUCK alone swing the
                  outcome, and where is the drawdown tail?" (sampling)

Method: circular BLOCK bootstrap of daily NAV log-returns (block=21d ~1M, preserves
autocorrelation + vol clustering), B paths -> CI on CAGR/Sharpe/MaxDD + tail probs.

OUTPUT is a SIZING/CONFIDENCE input, NOT a pass/fail gate: feed the 5th-pct MaxDD as the
DD anchor + P(DD<-30/-40) to Spyros, who owns the risk-gate decision.

HONEST LIMIT (always quote this): bootstrap captures SAMPLING uncertainty given the
historical return DISTRIBUTION — it does NOT model regime change / structural breaks.
The future is not a resample of the past -> these CIs are a LOWER bound on true uncertainty.

Usage:
  python bootstrap_nav.py <audit_or_nav_csv>            # single config
  python bootstrap_nav.py <config_csv> <baseline_csv>   # compare config vs baseline
A CSV may be either an audit CSV (has a 'combined_nav' column + a time/ymd/date column) or
a plain saved NAV CSV (index col 0 + 'combined_nav'). Both forms are auto-detected.

ANNUALIZATION = CALENDAR time ((t_last-t_first).days/365.25), same as
`simulate_holistic_nav.metrics` which produced every number in data/results_registry.md, per
CLAUDE.md section Backtest. Before 2026-09-27 this file used len(returns)/252 and sqrt(252), which
made its CAGR column systematically ~+0.3pp higher than the registry CAGR standing right next to it
(FAIL-F, audit measurement-integrity 2026-09-27). Sharpe now uses sqrt(N_ret/yrs_calendar).
"""
import sys, numpy as np, pandas as pd

L = 21; B = 4000; SEED = 12345                 # block ~1 month, 4000 paths, fixed seed = deterministic

def load_nav(path):
    """Return a daily-last NAV series (pd.Series indexed by DATE) from an audit CSV or plain nav CSV.

    The index is NOT decoration: annualization must be on CALENDAR time (CLAUDE.md §Backtest,
    `simulate_holistic_nav.metrics` = the source of every registry number), so the first and last
    calendar dates are part of the required input, not optional metadata.
    """
    df = pd.read_csv(path, low_memory=False)
    if "combined_nav" not in df.columns:
        raise SystemExit(f"{path}: no 'combined_nav' column")
    tc = [c for c in df.columns if c.lower() in ("time", "ymd", "date")]
    d = df.dropna(subset=["combined_nav"])
    if tc:                                     # audit CSV -> collapse to one NAV per calendar day
        t = pd.to_datetime(d[tc[0]], errors="coerce")
        d = d[t.notna()]; t = t[t.notna()]
        return d.groupby(t.dt.normalize())["combined_nav"].last().astype(float)
    # plain saved NAV CSV: index col 0 carries the date
    idx = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    ok = idx.notna() & df["combined_nav"].notna()
    if not ok.any():
        # FAIL-CLOSED on purpose: silently falling back to N/252 is exactly the bug this file was
        # patched for (FAIL-F, audit measurement-integrity 2026-09-27) — it made every CAGR here
        # ~+0.3pp higher than the registry CAGR quoted next to it, i.e. not comparable.
        raise SystemExit(f"{path}: no parseable date column (tried time/ymd/date and column 0) - "
                         f"cannot annualize on calendar time; add a date column instead of "
                         f"reverting to a trading-day count")
    return df.loc[ok, "combined_nav"].astype(float).set_axis(idx[ok]).groupby(level=0).last()

def calendar_years(s):
    """(t_last - t_first).days / 365.25 - the registry convention, NOT len(returns)/252.

    Measured on the pinned R3 ledgers 2026-09-27: 3,106 returns over 4,551 calendar days =
    12.460y calendar vs 12.325y by session count, i.e. every CAGR computed the old way was
    ~+0.30pp (post-fix R3) / ~+0.36pp (pre-fix R3) too high.
    """
    idx = pd.DatetimeIndex(s.index)
    yrs = (idx[-1] - idx[0]).days / 365.25
    if yrs <= 0:
        raise SystemExit("NAV series spans 0 calendar days - cannot annualize")
    return yrs

def boot(s):
    r = np.diff(np.log(s.values)); N = len(r)
    yrs = calendar_years(s)
    ann = N / yrs        # observations per CALENDAR year (mirrors simulate_holistic_nav.metrics)
    rng = np.random.default_rng(SEED); nblk = int(np.ceil(N / L))
    def met(p):
        nav = np.exp(np.cumsum(p)); peak = np.maximum.accumulate(nav)
        return nav[-1] ** (1 / yrs) - 1, p.mean() / p.std() * np.sqrt(ann), (nav / peak - 1).min()
    A = met(r); C = np.empty(B); S = np.empty(B); D = np.empty(B)
    for b in range(B):
        st = rng.integers(0, N, nblk)
        p = np.concatenate([np.take(r, np.arange(s0, s0 + L), mode="wrap") for s0 in st])[:N]
        C[b], S[b], D[b] = met(p)
    return N, yrs, A, C, S, D

def pct(x, p): return np.percentile(x, p)

paths = sys.argv[1:]
if not paths:
    raise SystemExit("usage: python bootstrap_nav.py <audit_or_nav_csv> [baseline_csv]")

rows = []
for path in paths:
    s = load_nav(path)
    N, yrs, A, C, S, D = boot(s)
    rows.append((path, N, yrs, A, C, S, D))

if len(rows) == 1:
    path, N, yrs, A, C, S, D = rows[0]
    print(f"=== Bootstrap robustness ({N} days, {yrs:.3f}y CALENDAR, {N/yrs:.1f} obs/yr, "
          f"block={L}d, B={B}, seed={SEED}) ===")
    print(f"src: {path}")
    print(f"{'metric':>8} {'ACTUAL':>8} {'median':>8} {'5th':>8} {'95th':>8}")
    print(f"{'CAGR':>8} {A[0]*100:>7.1f}% {pct(C,50)*100:>7.1f}% {pct(C,5)*100:>7.1f}% {pct(C,95)*100:>7.1f}%")
    print(f"{'Sharpe':>8} {A[1]:>8.2f} {pct(S,50):>8.2f} {pct(S,5):>8.2f} {pct(S,95):>8.2f}")
    print(f"{'MaxDD':>8} {A[2]*100:>7.1f}% {pct(D,50)*100:>7.1f}% {pct(D,5)*100:>7.1f}% {pct(D,95)*100:>7.1f}%")
    print(f"\nTail probabilities (over {B} bootstrap paths):")
    print(f"  P(CAGR < 0)     = {(C<0).mean()*100:.1f}%")
    print(f"  P(CAGR < 10%)   = {(C<0.10).mean()*100:.1f}%")
    print(f"  P(Sharpe < 1.0) = {(S<1.0).mean()*100:.1f}%")
    print(f"  P(MaxDD < -30%) = {(D<-0.30).mean()*100:.1f}%")
    print(f"  P(MaxDD < -40%) = {(D<-0.40).mean()*100:.1f}%")
    print(f"\nSIZING: use 5th-pct MaxDD ({pct(D,5)*100:.1f}%) as the DD anchor, NOT actual ({A[2]*100:.1f}%).")
else:
    print(f"=== Bootstrap compare (block={L}d, B={B}, seed={SEED}) ===")
    for path, N, *_ in rows: print(f"  {path}  ({N} days)")
    print(f"\n{'config':>40} {'CAGR_act':>8} {'CAGR_5th':>8} {'Sh_5th':>7} {'DD_act':>7} {'DD_med':>7} {'DD_5th':>7} {'P(<-30)':>8} {'P(<-40)':>8}")
    for path, N, yrs, A, C, S, D in rows:
        lab = path.split("/")[-1][:40]
        print(f"{lab:>40} {A[0]*100:>7.1f}% {pct(C,5)*100:>7.1f}% {pct(S,5):>7.2f} "
              f"{A[2]*100:>6.1f}% {pct(D,50)*100:>6.1f}% {pct(D,5)*100:>6.1f}% "
              f"{(D<-0.30).mean()*100:>7.1f}% {(D<-0.40).mean()*100:>7.1f}%")
    print("\nREAD: compare DD_5th + P(<-30/-40). Wider tail on the lever/variant = it materially raises drawdown risk.")

print("\nNOTE: sampling-uncertainty only (resamples history); excludes regime-change/structural risk -> real uncertainty is WIDER. Not a pass/fail gate — a sizing input for Spyros.")
