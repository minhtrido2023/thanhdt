# -*- coding: utf-8 -*-
"""NET entry-quality backtest: static 1.5% chase-cap vs vol-scaled cap.

Patch#3 proposal (Taylor, job Taylor_20260701_102033, user-approved 102950):
    cap_pct = clamp(k * rvol_20d, floor=0.015, ceil=0.04)   # k = 2.0
    cap     = ref * (1 + cap_pct)
Monotone-safe (floor == current static cap → only widens, never tightens),
fail-safe to static 1.5% when rvol_20d missing/<=0. Only touches _limit_price.

WHY a NET test, not fill-rate: a wider cap fills more gap-ups but at a worse
average entry price. The open question (Taylor's own): does catching breakouts
that the static cap MISSES earn enough forward return to pay for the worse
entry on the days both caps fill? fill-rate alone can't answer that.

SUBSTRATE — the real fill CEILING mechanism, simulated on real intraday paths:
  data/intraday_1m/*.csv : 1-minute OHLCV, 16 liquid VN names, 2023-09..2026-06.
  Daily OHLC + intraday min-low are derived from these bars (self-contained;
  no external join → fully recomputable). rvol_20d & forward returns come from
  the SAME daily close series.

FILL MODEL (matches executor.py::_limit_price buy branch):
  L = ref * (1 + cap_pct)                       # the chase ceiling
  bot places at min(ask, cap): crosses when ask<=cap, else rests passively at cap.
    - open <= L            -> crosses, fills ~ open              (pays min(open,L)=open)
    - open >  L , low<=L   -> rests at L, someone sells down to L -> fills at L
    - open >  L , low > L  -> price never returns to cap -> MISS  (the go-live failure)
  fill_price = min(open, L)  when  min_low_of_day <= L   ; else NO FILL.
  Using `open` as the cross price is PESSIMISTIC and identical for both caps,
  so the COMPARISON is fair (the live 11:15 fill-timing rule fills better still).

POPULATION: gap-up sessions only (open > prior close). On flat/down opens both
caps fill at the open identically (open <= L_static <= L_vol) → zero difference,
so they are correctly excluded from the contrast. This is the exact population
where the cap binds; it is NOT the literal BAL SIGNAL_V11 list (disclosed
limitation — momentum buys concentrate on strength/gap-ups, so gap-ups are the
representative + cap-relevant slice).

NET metric — captured forward return per decision:
  filled -> fwd(T+H)/fill_price - 1
  missed -> 0            (breakout not entered; capital idle = the cost of a miss)
Primary H = 20 sessions (~1M, BAL horizon); H in {10,20,40} for robustness.
"""
import os, glob, sys
import numpy as np, pandas as pd

DDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "..", "data", "intraday_1m")
DDIR = os.path.normpath(DDIR)
K = 2.0
FLOOR = 0.015          # == current static max_chase_pct_buy
CEIL = 0.040
STATIC = 0.015
HORIZONS = [10, 20, 40]
H_PRIMARY = 20
GAP_MIN = 0.0          # gap-up = open strictly above prior close
RVOL_MIN_OBS = 10      # need >=10 daily returns to trust rvol; else fail-safe to static


def cap_vol(rvol):
    """clamp(k*rvol, floor, ceil); fail-safe to static floor when rvol missing/<=0."""
    if rvol is None or not np.isfinite(rvol) or rvol <= 0:
        return STATIC
    return min(max(K * rvol, FLOOR), CEIL)


def build_daily(f):
    df = pd.read_csv(f)
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    df = df.sort_values("time")
    g = df.groupby("date")
    daily = pd.DataFrame({
        "open":  g["open"].first(),
        "high":  g["high"].max(),
        "low":   g["low"].min(),      # intraday session low (the fill test)
        "close": g["close"].last(),   # last bar ~ ATC
        "nbar":  g["close"].count(),
    }).reset_index()
    daily = daily[daily["nbar"] >= 50].reset_index(drop=True)   # drop half/broken sessions
    return daily


def run():
    files = sorted(glob.glob(os.path.join(DDIR, "*.csv")))
    if not files:
        sys.exit(f"no intraday csv under {DDIR}")
    rows = []
    for f in files:
        tk = os.path.basename(f)[:-4]
        d = build_daily(f)
        c = d["close"].values
        o = d["open"].values
        lo = d["low"].values
        ret = np.concatenate([[np.nan], c[1:] / c[:-1] - 1.0])   # daily returns
        n = len(d)
        for i in range(21, n - max(HORIZONS)):        # need 20 prior rets + max horizon fwd
            ref = c[i - 1]                            # prior-day close = decision/arrival price
            if ref <= 0:
                continue
            gap = o[i] / ref - 1.0
            if gap <= GAP_MIN:                        # only gap-ups: where the cap can bind
                continue
            past = ret[i - 20:i]
            past = past[np.isfinite(past)]
            rvol = float(np.std(past, ddof=1)) if len(past) >= RVOL_MIN_OBS else None
            cs, cv = STATIC, cap_vol(rvol)
            Ls, Lv = ref * (1 + cs), ref * (1 + cv)
            fill_s = lo[i] <= Ls
            fill_v = lo[i] <= Lv
            px_s = min(o[i], Ls) if fill_s else np.nan
            px_v = min(o[i], Lv) if fill_v else np.nan
            rec = {"tk": tk, "i": i, "date": d["date"].iloc[i], "ref": ref,
                   "open": o[i], "low": lo[i], "gap": gap, "rvol": rvol if rvol else np.nan,
                   "cap_v": cv, "Ls": Ls, "Lv": Lv,
                   "fill_s": fill_s, "fill_v": fill_v, "px_s": px_s, "px_v": px_v}
            for H in HORIZONS:
                fwd = c[i + H]
                rec[f"cap_s_{H}"] = (fwd / px_s - 1) if fill_s else 0.0
                rec[f"cap_v_{H}"] = (fwd / px_v - 1) if fill_v else 0.0
                rec[f"fwd_{H}"] = fwd
            rows.append(rec)
    R = pd.DataFrame(rows)
    return R


def report(R):
    print(f"=== chase-cap NET entry-quality: {R['tk'].nunique()} names, "
          f"{len(R)} gap-up decisions ({R['date'].min()}..{R['date'].max()}) ===\n")

    # cap distribution
    binds = (R["cap_v"] > STATIC + 1e-9).mean() * 100
    at_ceil = (R["cap_v"] >= CEIL - 1e-9).mean() * 100
    print(f"vol-cap widens vs static on {binds:.1f}% of gap-ups; "
          f"hits the 4% ceiling on {at_ceil:.1f}%. "
          f"rvol_20d median={R['rvol'].median():.4f} "
          f"(=> k*rvol median={K*R['rvol'].median():.4f})\n")

    # (a) fill-rate
    fs, fv = R["fill_s"].mean() * 100, R["fill_v"].mean() * 100
    print(f"(a) FILL-RATE on gap-ups:  static {fs:5.1f}%   vol {fv:5.1f}%   "
          f"(+{fv - fs:.1f}pp)\n")

    # (b) entry-price degradation on the BOTH-filled subset (like-for-like)
    both = R[R["fill_s"] & R["fill_v"]]
    deg = (both["px_v"] / both["px_s"] - 1).mean() * 1e4
    worse = (both["px_v"] > both["px_s"] + 1e-9).mean() * 100
    print(f"(b) ENTRY-PRICE on both-filled (n={len(both)}): vol is "
          f"{deg:+.1f} bps vs static on avg; worse on {worse:.1f}% of them "
          f"(better/equal on the rest since floor==static)\n")

    # newly-captured trades: static MISSES, vol FILLS -> are they winners?
    gained = R[(~R["fill_s"]) & R["fill_v"]]
    print(f"    trades static MISSES but vol CATCHES: n={len(gained)} "
          f"({len(gained)/len(R)*100:.1f}% of gap-ups). "
          f"their fwd{H_PRIMARY} from vol entry: "
          f"mean {gained[f'cap_v_{H_PRIMARY}'].mean()*100:+.2f}%  "
          f"median {gained[f'cap_v_{H_PRIMARY}'].median()*100:+.2f}%  "
          f"win {(gained[f'cap_v_{H_PRIMARY}']>0).mean()*100:.0f}%\n")

    # (c) NET captured forward return per decision (0 when missed)
    print("(c) NET captured forward return per gap-up decision "
          "(missed = 0 = breakout not entered):")
    print(f"    {'H':>4} {'static':>9} {'vol':>9} {'NET Δ':>9}  {'t-stat(paired)':>14}")
    for H in HORIZONS:
        s = R[f"cap_s_{H}"]
        v = R[f"cap_v_{H}"]
        diff = v - s
        t = diff.mean() / (diff.std(ddof=1) / np.sqrt(len(diff))) if diff.std() > 0 else float("nan")
        star = "  <== primary" if H == H_PRIMARY else ""
        print(f"    {H:>4} {s.mean()*100:>8.2f}% {v.mean()*100:>8.2f}% "
              f"{diff.mean()*100:>+8.2f}% {t:>14.2f}{star}")
    print("\n    (per-decision return; NET Δ>0 => vol-cap captures more forward return "
          "AFTER paying the worse entry.)")

    # per-year robustness (primary H)
    R = R.copy()
    R["yr"] = pd.to_datetime(R["date"]).dt.year
    print(f"\n(d) per-year NET Δ (H={H_PRIMARY}, pp of captured return):")
    for yr, g in R.groupby("yr"):
        d = (g[f"cap_v_{H_PRIMARY}"] - g[f"cap_s_{H_PRIMARY}"]).mean() * 100
        print(f"    {yr}: n={len(g):5d}  static {g[f'cap_s_{H_PRIMARY}'].mean()*100:+6.2f}%  "
              f"vol {g[f'cap_v_{H_PRIMARY}'].mean()*100:+6.2f}%  Δ {d:+.2f}pp")
    return R


def selfcheck(R):
    """Independent recompute of the headline NET number from the raw per-row fields,
    NOT from the aggregates, and a 0-VND identity: on rows where BOTH caps fill at the
    SAME price (open <= Ls), captured returns must be byte-identical."""
    print("\n--- SELF-CHECK (independent recompute) ---")
    ok = True
    # 1) identity: same entry px => identical captured return
    same = R[R["fill_s"] & R["fill_v"] & (np.abs(R["px_s"] - R["px_v"]) < 1e-12)]
    d = (same[f"cap_v_{H_PRIMARY}"] - same[f"cap_s_{H_PRIMARY}"]).abs().max()
    print(f"  identity (same entry px, n={len(same)}): max |Δcaptured| = {d:.2e}  "
          f"{'PASS' if d < 1e-12 else 'FAIL'}")
    ok &= d < 1e-12
    # 2) monotone: vol cap is NEVER below static (floor==static) => fill_v >= fill_s always
    mono = (R["fill_v"] | ~R["fill_s"]).all()   # fill_s True must imply fill_v True
    print(f"  monotone (static-fill => vol-fill): {'PASS' if mono else 'FAIL'}")
    ok &= mono
    # 3) recompute NET from raw px & fwd, compare to report path
    H = H_PRIMARY
    man_s = np.where(R["fill_s"], R[f"fwd_{H}"] / R["px_s"] - 1, 0.0)
    man_v = np.where(R["fill_v"], R[f"fwd_{H}"] / R["px_v"] - 1, 0.0)
    e1 = np.nanmax(np.abs(man_s - R[f"cap_s_{H}"].values))
    e2 = np.nanmax(np.abs(man_v - R[f"cap_v_{H}"].values))
    print(f"  recompute captured from raw: max err static {e1:.2e} vol {e2:.2e}  "
          f"{'PASS' if max(e1, e2) < 1e-12 else 'FAIL'}")
    ok &= max(e1, e2) < 1e-12
    print(f"  SELF-CHECK: {'ALL PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    R = run()
    R2 = report(R)
    selfcheck(R)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chase_cap_backtest_raw.csv")
    R.to_csv(out, index=False)
    print(f"\nraw -> {out}  ({len(R)} rows)")
