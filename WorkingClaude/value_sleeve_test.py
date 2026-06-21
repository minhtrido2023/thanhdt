"""
Value Sleeve Test (acting on the AMH #1-#5 conclusion)
======================================================
All five AMH lenses converged: the V4/V5 book is a MOMENTUM monoculture in a
momentum-inefficiency regime; the unanimous fix = add a VALUE sleeve (negatively
correlated, profits in momentum's drawdowns, currently healthy). This tests it:
reallocate weight w from the real prod-spec V4/V5 NAV into a transparent,
DT5G-gated long-only VALUE book, and measure Sharpe / Calmar / the 2025-26 bleed.

Incumbent  : REAL prod-spec daily NAV (data/5sys_prodspec_...dt5g.csv) -> V4, V5.
Value sleeve: monthly long-only top-quintile cheapest (PB+PE rank), DT5G-gated to
             the same state weights, TC on turnover. Built from data/edge_panel.csv.
Combine at return level (monthly): blend = (1-w)*book + w*value, w in a grid.

NOTE: the value sleeve is a TRANSPARENT PROXY (equal-weight quintile, no capacity
model), so treat absolute numbers as indicative; the DECISION signal is the
Sharpe/Calmar DELTA and the grind-window cushion.

Run: python value_sleeve_test.py
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
GRIND = ("2025-09", "2026-03")


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


def build_value_sleeve():
    df = pd.read_csv(PANEL, parse_dates=["time"])
    df = df[df[FWD].notna()].copy()
    lo, hi = df[FWD].quantile([0.005, 0.995]); df[FWD] = df[FWD].clip(lo, hi)
    df["ym"] = df["time"].dt.to_period("M")
    st = pd.read_csv(STATEF, parse_dates=["time"]); st["ym"] = st["time"].dt.to_period("M")
    modal = st.groupby("ym")["state"].agg(lambda s: int(s.mode().iloc[0]))

    rets, prev = {}, set()
    for ym, g in df.groupby("ym"):
        s = g[["ticker", "PB", "PE", FWD]].dropna()
        if len(s) < MIN_NAMES:
            continue
        s["vscore"] = s["PB"].rank(pct=True) + s["PE"].rank(pct=True)   # low = cheap
        k = max(5, int(len(s) * QTILE))
        picks = s.nsmallest(k, "vscore")
        raw = picks[FWD].mean()
        names = set(picks["ticker"])
        turn = 1.0 if not prev else 1 - len(names & prev) / len(names)
        prev = names
        w = STATE_W.get(int(modal.get(ym, 3)), 0.7)
        rets[ym] = w * raw - TC * turn * w
    return pd.Series(rets).sort_index()


def book_monthly(nav_col):
    nav = pd.read_csv(NAVF, parse_dates=["time"]).set_index("time")[nav_col]
    m = nav.resample("ME").last()
    r = m.pct_change()
    r.index = r.index.to_period("M")
    return r.dropna()


def sub(ret, lo, hi):
    return ret[(ret.index >= pd.Period(lo)) & (ret.index <= pd.Period(hi))]


def report(name, book, value, vni):
    idx = book.index.intersection(value.index)
    book, value = book.loc[idx], value.loc[idx]
    vni = vni.reindex(idx)
    print(f"\n################  INCUMBENT = {name}  ################")
    print(f"value-sleeve standalone: {fmt(ann(value))}")
    print(f"corr(book, value) = {book.corr(value):+.2f}   "
          f"(months {idx.min()} -> {idx.max()}, n={len(idx)})")
    rows = []
    for w in [0.0, 0.2, 0.3, 0.4, 0.5]:
        blend = (1 - w) * book + w * value
        full = ann(blend)
        oos = ann(sub(blend, "2020-01", "2026-12"))
        grind = sub(blend, *GRIND)
        grind_cum = ((1 + grind).prod() - 1) * 100
        rows.append(dict(w_value=w, **{k: round(v, 2) for k, v in full.items()},
                         Sharpe_OOS=round(oos["Sharpe"], 2),
                         grind_2025_26_pct=round(grind_cum, 1)))
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    # benchmark grind
    g_book = ((1 + sub(book, *GRIND)).prod() - 1) * 100
    g_val = ((1 + sub(value, *GRIND)).prod() - 1) * 100
    g_vni = ((1 + sub(vni, *GRIND)).prod() - 1) * 100
    print(f"  GRIND {GRIND[0]}..{GRIND[1]}: book {g_book:+.1f}% | value {g_val:+.1f}% | VNI {g_vni:+.1f}%")
    return res


def fmt(m):
    return (f"CAGR {m['CAGR']:.1f}% Sharpe {m['Sharpe']:.2f} Sortino {m['Sortino']:.2f} "
            f"MaxDD {m['MaxDD']:.1f}% Calmar {m['Calmar']:.2f}")


def main():
    value = build_value_sleeve()
    vni = book_monthly("VNI")
    print(f"Value sleeve: {len(value)} months {value.index.min()} -> {value.index.max()}")
    allres = {}
    for col, label in [("V4_V121_ENS_TQ34b", "V4 (V121_ENS, recommended)"),
                       ("V5_V4_KellyQ2", "V5 (Kelly)")]:
        book = book_monthly(col)
        allres[label] = report(label, book, value, vni)
    # save
    out = pd.concat({k: v.set_index("w_value") for k, v in allres.items()}, axis=0)
    out.to_csv(WORKDIR + r"\data\value_sleeve_results.csv")
    print("\nSaved: data/value_sleeve_results.csv")
    print("\nDECISION READ: compare w=0 (book alone) vs w=0.2-0.4 on Sharpe/Calmar/grind cushion.")


if __name__ == "__main__":
    main()
