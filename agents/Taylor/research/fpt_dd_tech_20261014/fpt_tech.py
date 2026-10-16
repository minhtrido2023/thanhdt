# -*- coding: utf-8 -*-
"""FPT technical snapshot + honest event study (job Taylor_20261014_040353).
Input: bq_px_hist.csv (BQ tav2_bq.ticker, history to 2026-10-13, Close = adjusted)
       + today's live bar from DNSE (dnse_live_raw.json, board G1, intraday PARTIAL).
Forward returns are computed from Close, NOT from profit_* columns.
Run: $DNA_PYEXE fpt_tech.py > out_fpt_tech.txt
"""
import json, os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
px = pd.read_csv(os.path.join(HERE, "bq_px_hist.csv"), parse_dates=["time"])
live = json.load(open(os.path.join(HERE, "dnse_live_raw.json")))
g1 = [t for t in live["FPT_lt"]["trades"] if t["boardId"] == "G1"][0]
LIVE = dict(time=pd.Timestamp(g1["time"][:10]), Open=g1["openPrice"] * 1000, High=g1["highestPrice"] * 1000,
            Low=g1["lowestPrice"] * 1000, Close=g1["matchPrice"] * 1000,
            Volume=g1["totalVolumeTraded"] * 10, ts=g1["time"])  # DNSE vol unit = 10 shares (212.1bn / 56.5k ≈ 3.75M)


def rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def indicators(df):
    df = df.copy()
    c = df.Close
    for n in (20, 50, 100, 200):
        df[f"MA{n}"] = c.rolling(n).mean()
    df["RSI14"] = rsi(c)
    e12, e26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    df["MACD"] = e12 - e26
    df["MACDsig"] = df.MACD.ewm(span=9, adjust=False).mean()
    tr = pd.concat([df.High - df.Low, (df.High - c.shift()).abs(), (df.Low - c.shift()).abs()], axis=1).max(axis=1)
    df["ATR14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["HI252"] = c.rolling(252).max()
    df["LO252"] = c.rolling(252).min()
    df["ATH"] = c.cummax()
    df["dMA200"] = c / df.MA200 - 1
    df["dMA50"] = c / df.MA50 - 1
    df["ret63"] = c / c.shift(63) - 1
    for h in (21, 42, 63):
        df[f"fwd{h}"] = c.shift(-h) / c - 1
    return df


fpt = px[px.ticker == "FPT"].set_index("time").sort_index()
vni = fpt["VNINDEX"]
hist = fpt[["Open", "High", "Low", "Close", "Volume", "PE", "PB"]].copy()
today = pd.DataFrame([LIVE]).set_index("time")[["Open", "High", "Low", "Close", "Volume"]]
full = pd.concat([hist, today])
I = indicators(full)
t, y = I.iloc[-1], I.iloc[-2]

print(f"=== FPT snapshot — live DNSE G1 {LIVE['ts']} (PARTIAL session) ; history BQ to {hist.index[-1].date()} ===")
print(f"price live {t.Close:,.0f} | O {t.Open:,.0f} H {t.High:,.0f} L {t.Low:,.0f} | prev close {y.Close:,.0f} ({t.Close/y.Close-1:+.2%})")
for n in (20, 50, 100, 200):
    ma = I[f"MA{n}"]
    print(f"MA{n:<3} {t[f'MA{n}']:>9,.0f}  price vs MA {t.Close/t[f'MA{n}']-1:+.1%}  MA slope 20d {ma.iloc[-1]/ma.iloc[-21]-1:+.1%}")
print(f"52w high {t.HI252:,.0f} ({t.Close/t.HI252-1:+.1%}) on {I.Close.iloc[-252:].idxmax().date()} | 52w low {t.LO252:,.0f} ({t.Close/t.LO252-1:+.1%}) on {I.Close.iloc[-252:].idxmin().date()}")
print(f"ATH (adj) {t.ATH:,.0f} on {I.Close.idxmax().date()} -> drawdown {t.Close/t.ATH-1:+.1%}")
print(f"RSI14 {t.RSI14:.1f} (prev {y.RSI14:.1f}) | MACD {t.MACD:,.0f} sig {t.MACDsig:,.0f} hist {t.MACD-t.MACDsig:+,.0f} (prev hist {y.MACD-y.MACDsig:+,.0f})")
print(f"ATR14 {t.ATR14:,.0f} = {t.ATR14/t.Close:.2%} of price")
v = hist.Volume
print(f"Volume yesterday {v.iloc[-1]/1e6:.2f}M vs MA20 {v.iloc[-20:].mean()/1e6:.2f}M vs MA50 {v.iloc[-50:].mean()/1e6:.2f}M ; today partial {LIVE['Volume']/1e6:.2f}M at {LIVE['ts'][11:16]}")
tv = (hist.Close * hist.Volume).iloc[-20:].mean()
print(f"ADV20 value ≈ {tv/1e9:,.0f} bn VND (Close×Volume, adj≈unadj recently)")

# last 15 sessions
print("\nlast 15 sessions (Close, Vol M, RSI):")
for d, r in I.iloc[-15:].iterrows():
    print(f"  {d.date()} {r.Close:>8,.0f} {r.Volume/1e6:6.2f} {r.RSI14:5.1f}")

# swing pivots (support/resistance) over last 250 sessions, 10-bar fractals
c = I.Close.iloc[-260:]
piv_lo = [(d, x) for i, (d, x) in enumerate(c.items()) if 10 <= i < len(c) - 3 and x == c.iloc[i - 10:i + 11].min()]
piv_hi = [(d, x) for i, (d, x) in enumerate(c.items()) if 10 <= i < len(c) - 3 and x == c.iloc[i - 10:i + 11].max()]
print("\nswing lows  (10-bar):", [(str(d.date()), round(x)) for d, x in piv_lo[-8:]])
print("swing highs (10-bar):", [(str(d.date()), round(x)) for d, x in piv_hi[-8:]])
# longer history lows near current price
lo_hist = I.Close[(I.Close > t.Close * 0.85) & (I.Close < t.Close * 1.0)]
print(f"sessions closed within -15%..0% of today's price since 2010: {len(lo_hist)}, last span {lo_hist.index.min().date() if len(lo_hist) else None} .. {lo_hist.index.max().date() if len(lo_hist) else None}")
yr = I.Close.resample("YE").agg(["min", "max", "last"])
print("yearly min/max/last (adj):\n", yr.tail(5).round(0).to_string())

# relative strength vs VNINDEX (BQ to 10-13)
for h in (21, 63, 126, 252):
    rf, rv = hist.Close.iloc[-1] / hist.Close.iloc[-1 - h] - 1, vni.iloc[-1] / vni.iloc[-1 - h] - 1
    print(f"RS {h:>3}d: FPT {rf:+.1%} VNINDEX {rv:+.1%} diff {rf-rv:+.1%}")
vma = vni.rolling(200).mean()
print(f"VNINDEX {vni.iloc[-1]:.2f} vs MA50 {vni.iloc[-1]/vni.rolling(50).mean().iloc[-1]-1:+.1%} vs MA200 {vni.iloc[-1]/vma.iloc[-1]-1:+.1%}  (BQ close {vni.index[-1].date()})")

# valuation percentile (BQ daily PE/PB of FPT; PE is trailing, as published in ticker)
for yrs in (5, 10):
    w = hist.loc[hist.index >= hist.index[-1] - pd.DateOffset(years=yrs)]
    pe_now = hist.PE.iloc[-1] * t.Close / hist.Close.iloc[-1]
    pb_now = hist.PB.iloc[-1] * t.Close / hist.Close.iloc[-1]
    print(f"PE {yrs}y: now {pe_now:.2f} pctile {(w.PE.dropna() < pe_now).mean():.0%} (median {w.PE.median():.1f}, min {w.PE.min():.1f}) | "
          f"PB now {pb_now:.2f} pctile {(w.PB.dropna() < pb_now).mean():.0%} (median {w.PB.median():.2f})")
for p in ("CMG", "ELC"):
    q = px[px.ticker == p].iloc[-1]
    print(f"peer {p} {q.time.date()}: PE {q.PE:.1f} PB {q.PB:.2f}")

# ---------------- event study (history only, exclude live row) ----------------
H = I.iloc[:-1].copy()
cur = dict(RSI14=t.RSI14, dMA200=t.dMA200, dMA50=t.dMA50, ret63=t.ret63)
print(f"\ncurrent state: RSI14 {cur['RSI14']:.1f}, vs MA200 {cur['dMA200']:+.1%}, vs MA50 {cur['dMA50']:+.1%}, 63d ret {cur['ret63']:+.1%}")


def episodes(mask, gap=63):
    """collapse signal days into independent episodes: first day, then skip `gap` sessions."""
    idx, out, last = np.where(mask.values)[0], [], -10 ** 9
    for i in idx:
        if i - last >= gap:
            out.append(i)
            last = i
    return H.index[out]


def study(name, mask):
    ep = episodes(mask)
    rows = H.loc[ep, ["Close", "RSI14", "dMA200", "fwd21", "fwd42", "fwd63"]]
    v63 = rows.fwd63.dropna()
    print(f"\n[{name}] signal days {int(mask.sum())} -> independent episodes (gap 63) N={len(ep)}, with 63d fwd: {len(v63)}")
    if len(rows):
        print(rows.assign(Close=rows.Close.round(0)).round(3).to_string())
        for h in (21, 42, 63):
            s = rows[f"fwd{h}"].dropna()
            if len(s):
                print(f"  fwd{h}: median {s.median():+.1%} mean {s.mean():+.1%} hit>0 {(s>0).mean():.0%} min {s.min():+.1%} max {s.max():+.1%} (N={len(s)})")
    return rows


H10 = H[H.index >= "2010-01-01"]
base = {h: H10[f"fwd{h}"].dropna() for h in (21, 63)}
print(f"\nBASELINE FPT 2010+ all days: fwd21 median {base[21].median():+.1%} hit {(base[21]>0).mean():.0%} | fwd63 median {base[63].median():+.1%} hit {(base[63]>0).mean():.0%}")
m1 = (H.RSI14.between(cur["RSI14"] - 7, cur["RSI14"] + 7)) & (H.dMA200.between(cur["dMA200"] - 0.06, cur["dMA200"] + 0.06))
r1 = study("A: RSI±7 & dist-MA200 ±6pp", m1)
m2 = (H.dMA200 < -0.12) & (H.RSI14 < 40)
r2 = study("B: below MA200 >12% & RSI<40 (broader)", m2)
m3 = (H.Close / H.ATH - 1 < -0.25) & (H.RSI14 < 40)
r3 = study("C: drawdown from ATH >25% & RSI<40", m3)
pd.concat({"A": r1, "B": r2, "C": r3}).to_csv(os.path.join(HERE, "event_study_episodes.csv"))
I.tail(300).to_csv(os.path.join(HERE, "fpt_indicators_tail300.csv"))
