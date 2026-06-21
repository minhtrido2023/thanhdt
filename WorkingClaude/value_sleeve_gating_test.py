"""
Value Sleeve — GATED vs UNGATED (AMH action, follow-up #2)
=========================================================
#3 showed value's cross-sectional edge (cheap beats expensive) is STRONG in
CRISIS. But that is a SELECTION fact (tilt to cheap IF invested), orthogonal to
the TIMING decision (whether to be invested = the DT5G gate, #5). Question: when
we run a value sleeve, should it follow the DT5G gate to cash in CRISIS (GATED),
or stay invested to capture value's relative outperformance (UNGATED)?
Let the data decide. Variants of the long-only top-quintile-cheap value book:
  GATED     = w_state * raw   (cash in CRISIS, like the momentum book)
  UNGATED   = 1.00   * raw    (always fully invested)
  FLOOR50   = max(w_state,0.5)* raw  (half-invested floor through stress)
Compare standalone + CRISIS/BEAR-conditional + blended onto real V4/V5.

Run: python value_sleeve_gating_test.py
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
NAVF = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g.csv"
PANEL = WORKDIR + r"\data\edge_panel.csv"
STATEF = WORKDIR + r"\data\dt5g_vnindex.csv"
FWD = "fwd_1m"
QTILE = 0.20
MIN_NAMES = 25
TC = 0.001
STATE_W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}


def ann(ret):
    ret = ret.dropna()
    mu = ret.mean() * 12
    sd = ret.std(ddof=1) * np.sqrt(12)
    sharpe = mu / sd if sd > 0 else 0
    dn = ret[ret < 0].std(ddof=1) * np.sqrt(12)
    sortino = mu / dn if dn > 0 else 0
    nav = (1 + ret).cumprod()
    dd = (nav / nav.cummax() - 1).min()
    calmar = mu / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=mu*100, Sharpe=sharpe, Sortino=sortino, MaxDD=dd*100, Calmar=calmar)


def fmt(m):
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}  "
            f"MaxDD {m['MaxDD']:6.1f}%  Calmar {m['Calmar']:.2f}")


def build():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995]); df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    modal = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))

    raw, wst, state, prev = {}, {}, {}, set()
    for ym, g in df.groupby("ym"):
        s = g[["ticker", "PB", "PE", FWD]].dropna()
        if len(s) < MIN_NAMES:
            continue
        s["vscore"] = s["PB"].rank(pct=True) + s["PE"].rank(pct=True)
        k = max(5, int(len(s) * QTILE))
        picks = s.nsmallest(k, "vscore")
        names = set(picks["ticker"])
        turn = 1.0 if not prev else 1 - len(names & prev) / len(names)
        prev = names
        stt = int(modal.get(ym, 3))
        raw[ym] = picks[FWD].mean() - TC * turn   # raw value return net of TC (pre-gate)
        wst[ym] = STATE_W.get(stt, 0.7)
        state[ym] = stt
    raw = pd.Series(raw).sort_index(); wst = pd.Series(wst).reindex(raw.index)
    state = pd.Series(state).reindex(raw.index)
    variants = {
        "GATED":   wst * raw,
        "UNGATED": 1.00 * raw,
        "FLOOR50": np.maximum(wst, 0.5) * raw,
    }
    return pd.DataFrame(variants), raw, state


def book_monthly(col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[col]
    r = nav.resample("ME").last().pct_change()
    r.index = r.index.to_period("M")
    return r.dropna()


def main():
    V, raw, state = build()
    print(f"Value sleeve variants: {len(V)} months {V.index.min()} -> {V.index.max()}")
    print(f"Months by state: " + ", ".join(f"{k}:{(state==k).sum()}" for k in sorted(state.unique())))

    print("\n=== STANDALONE (full history) ===")
    for c in V.columns:
        print(f"  {c:8s} {fmt(ann(V[c]))}")

    print("\n=== CRISIS+BEAR conditional (states 1-2) — what gating saves/costs ===")
    cb = state.isin([1, 2])
    print(f"  months in CRISIS+BEAR: {cb.sum()}")
    for c in V.columns:
        seg = V[c][cb]
        print(f"  {c:8s} mean {seg.mean()*100:+.2f}%/mo  cum {((1+seg).prod()-1)*100:+.1f}%  "
              f"worst {seg.min()*100:+.1f}%")
    print(f"  (raw ungated value in crisis+bear: cum {((1+raw[cb]).prod()-1)*100:+.1f}% "
          f"-> staying invested eats the crash; gating to cash = 0)")

    print("\n=== BLEND onto real books at w=0.30 (gated vs ungated vs floor sleeve) ===")
    for col, lbl in [("V4_V121_ENS_TQ34b", "V4"), ("V5_V4_KellyQ2", "V5")]:
        book = book_monthly(col)
        idx = book.index.intersection(V.index)
        print(f"\n  -- {lbl} (book alone): {fmt(ann(book.loc[idx]))}")
        for c in V.columns:
            blend = 0.7 * book.loc[idx] + 0.3 * V[c].loc[idx]
            print(f"     +30% {c:8s}: {fmt(ann(blend))}")

    V.to_csv(WORKDIR + r"\data\value_sleeve_gating.csv")
    print("\nSaved: data/value_sleeve_gating.csv")


if __name__ == "__main__":
    main()
