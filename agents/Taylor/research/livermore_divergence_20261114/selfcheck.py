"""Self-check theo PREREG §9 — tính lại ĐỘC LẬP bằng vòng lặp Python thuần (không dùng hàm engine)."""
import glob, json, math, os, random
import numpy as np, pandas as pd
ROOT = "/home/trido/thanhdt/WorkingClaude"; OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(20261114)
E = pd.read_parquet(f"{OUT}/events.parquet"); CT = pd.read_parquet(f"{OUT}/control.parquet"); R = pd.read_csv(f"{OUT}/results.csv")
U1 = pd.read_parquet(f"{OUT}/u1_daily.parquet")
for d in (E, CT, U1): d["time"] = pd.to_datetime(d["time"])
res = {}

# 1. control leg: pin ta-model n_elig L20 = 300437 (≤ 2026-11-05)
mine = CT[CT.time <= "2026-11-05"][["time", "ticker"]]
ta = pd.read_parquet(f"{OUT}/../ta_model_5pct_20261106/deals.parquet", columns=["time", "ticker"]); ta["time"] = pd.to_datetime(ta.time)
a = set(map(tuple, mine.astype(str).values)); b = set(map(tuple, ta.astype(str).values))
res["ctrl_leg"] = dict(mine=len(a), ta_pinned=len(b), only_mine=sorted(a - b)[:5], only_ta=sorted(b - a)[:5])


def rsi_loop(c, n):
    out = [math.nan] * len(c); au = ad = None; cnt = 0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if math.isnan(d): continue
        u, v = max(d, 0.0), max(-d, 0.0)
        if au is None: au, ad = u, v
        else: au = (1 - 1 / n) * au + u / n; ad = (1 - 1 / n) * ad + v / n
        cnt += 1
        if cnt >= n and ad != 0: out[i] = 100 - 100 / (1 + au / ad)
    return out


def detect_loop(c, r, ok):
    L = len(c); hi, lo = [], []
    for i in range(5, L - 5):
        w = c[i - 5:i + 6]
        if any(math.isnan(x) for x in w): continue
        if w.index(max(w)) == 5: hi.append(i)
        if w.index(min(w)) == 5: lo.append(i)
    ev = []
    for P, kind in ((hi, "hi"), (lo, "lo")):
        for j, p2 in enumerate(P):
            t = p2 + 5; p1 = None
            for q in range(j - 1, -1, -1):
                g = p2 - P[q]
                if g < 10: continue
                if g <= 60: p1 = P[q]
                break
            if p1 is None or math.isnan(r[p1]) or math.isnan(r[p2]): continue
            c1, c2, r1, r2 = c[p1], c[p2], r[p1], r[p2]
            if kind == "hi":
                if c2 > c1 * 1.01 and r2 <= r1 - 3 and r1 >= 60: ev.append(("RBEAR", t, p1, p2))
                if c2 < c1 and r2 > r1 + 3: ev.append(("HBEAR", t, p1, p2))
            else:
                if c2 < c1 * 0.99 and r2 >= r1 + 3 and r1 <= 40: ev.append(("RBULL", t, p1, p2))
                if c2 > c1 and r2 < r1 - 3: ev.append(("HBULL", t, p1, p2))
    ev.sort(key=lambda e: e[1]); keep, last = [], {}
    for e in ev:
        if not ok[e[1]]: continue
        if e[1] - last.get(e[0], -10**9) >= 20: keep.append(e); last[e[0]] = e[1]
    return keep

# 2. tái phát hiện toàn bộ sự kiện cho 40 mã U2 ngẫu nhiên + VNINDEX
cols = ["time", "ticker", "Close", "Price", "Volume", "Inflation_7"]
raw = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
raw["time"] = pd.to_datetime(raw.time); raw = raw.sort_values(["ticker", "time"]).drop_duplicates(["ticker", "time"])
eligset = set(zip(CT.ticker, CT.time))
tks = random.sample(sorted(E[E.U == "U2"].ticker.unique()), 40)
mism, n_cmp, fwd_err, look_ahead_bad = 0, 0, 0.0, 0
for tk in tks + ["VNINDEX"]:
    if tk == "VNINDEX":
        g = U1[["time", "close"]].rename(columns={"close": "Close"}); ok = list(g.time >= "2014-01-01")
    else:
        g = raw[raw.ticker == tk]; ok = [(tk, t) in eligset for t in g.time]
    c = [float(x) for x in g.Close]; tt = list(g.time)
    for n in (14, 9):
        r = rsi_loop(c, n); mineL = detect_loop(c, r, ok)
        eng = E[(E.ticker == tk) & (E.rsi == n)].sort_values("t")
        A = [(e[0], e[1]) for e in mineL]; B = list(zip(eng.type, eng.t))
        n_cmp += len(A); mism += len(set(A) ^ set(B))
        for (tp, t, p1, p2) in mineL:
            row = eng[(eng.type == tp) & (eng.t == t)]
            if len(row) != 1: continue
            row = row.iloc[0]
            if not (row.p2 + 5 <= row.t and row.p1 < row.p2): look_ahead_bad += 1
            for H in (10, 20, 40):
                if t + 1 + H < len(c):
                    f = c[t + 1 + H] / c[t + 1] - 1
                    if not np.isnan(row[f"fwd{H}"]): fwd_err = max(fwd_err, abs(f - row[f"fwd{H}"]))
res["redetect"] = dict(tickers=len(tks) + 1, events_loop=n_cmp, symdiff=mism, max_fwd_err=fwd_err, lookahead_bad=look_ahead_bad)

# 3. tính lại exR_OOS + BSS_OOS hai trial bằng vòng lặp
def recompute(U, tp, H, n):
    s = E[(E.U == U) & (E.type == tp) & (E.rsi == n)]
    s = s[s[f"fwd{H}"].notna() & ~s[f"brk{H}"]].sort_values("time")
    if U == "U2":
        c = CT[CT[f"fwd{H}"].notna() & ~CT[f"brk{H}"]]
        ctrl = {}
        for t, f in zip(c.time, c[f"fwd{H}"]): ctrl.setdefault(t, []).append(f)
        ctrl = {k: sum(v) / len(v) for k, v in ctrl.items()}
        base = list(zip(c[f"end{H}"], c[f"fwd{H}"]))
    else:
        u = U1[(U1.time >= "2007-01-01") & U1[f"fwd{H}"].notna()]
        base = list(zip(u[f"end{H}"], u[f"fwd{H}"]))
    base.sort(key=lambda x: x[0])
    def clim(t):
        ms = pd.Timestamp(t.year, t.month, 1); ups = [1.0 if f > 0 else 0.0 for e, f in base if e < ms]; fs = [f for e, f in base if e < ms]
        return (sum(ups) / len(ups), sum(fs) / len(fs)) if ups else (0.5, 0.0)
    cache = {}; per = {}
    evs = list(zip(s.time, s[f"end{H}"], s[f"fwd{H}"], s["sign"]))
    for (t, e, f, sg) in evs:
        if t < pd.Timestamp("2020-01-01"): continue
        key = (t.year, t.month)
        if key not in cache: cache[key] = clim(t)
        cm, rb = cache[key]
        prior = [(1.0 if ff > 0 else 0.0) for (tt2, ee, ff, _) in evs if ee < t]
        p = (sum(prior) + 2 * cm) / (len(prior) + 2); up = 1.0 if f > 0 else 0.0
        x = sg * (f - (ctrl[t] if U == "U2" else rb))
        per.setdefault(t, []).append(((p - up) ** 2, (cm - up) ** 2, x))
    bf = sum(sum(a for a, _, _ in v) / len(v) for v in per.values()); bc = sum(sum(b for _, b, _ in v) / len(v) for v in per.values())
    xs = [sum(x for _, _, x in v) / len(v) for v in per.values()]
    return 1 - bf / bc, sum(xs) / len(xs)
chk = []
for (U, tp, H, n) in [("U2", "RBEAR", 20, 14), ("U1", "HBULL", 20, 9), ("U2", "RBULL", 40, 9)]:
    b_, x_ = recompute(U, tp, H, n); row = R[R.trial == f"{U}_{tp}_H{H}_RSI{n}"].iloc[0]
    chk.append(dict(trial=row.trial, BSS_loop=b_, BSS_eng=row.BSS_OOS, exR_loop=x_, exR_eng=row.exR_OOS,
                    dBSS=abs(b_ - row.BSS_OOS), dexR=abs(x_ - row.exR_OOS)))
res["recompute_headline"] = chk

# 4. RSI14 VNINDEX vs BQ D_RSI*100 (tham khảo)
v = raw[raw.ticker == "VNINDEX"][["time"]].copy()
d = pd.concat([pd.read_parquet(f, columns=["time", "ticker", "D_RSI"]) for f in sorted(glob.glob(f"{ROOT}/data/bq_cache/ticker/20*.parquet"))])
d = d[d.ticker == "VNINDEX"]; d["time"] = pd.to_datetime(d.time)
m = U1.merge(d, on="time"); m = m[m.time >= "2014-01-01"]
res["rsi14_vs_D_RSI"] = dict(n=len(m), frac_within_1pt=float((abs(m.rsi14 - 100 * m.D_RSI) < 1).mean()),
                            median_abs_diff=float((m.rsi14 - 100 * m.D_RSI).abs().median()))
ok = (res["redetect"]["symdiff"] == 0 and res["redetect"]["max_fwd_err"] < 1e-9 and res["redetect"]["lookahead_bad"] == 0
      and all(c["dBSS"] < 1e-9 and c["dexR"] < 1e-9 for c in chk))
res["SELFCHECK"] = "PASS" if ok else "FAIL"
json.dump(res, open(f"{OUT}/selfcheck.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
