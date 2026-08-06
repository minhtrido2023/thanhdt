#!/usr/bin/env python3
"""T3 — (a) proper zigzag cycle detection (T2's greedy argmax found only 1 cycle),
(b) the metric that actually matters for a WARNING tier: P(big further decline | break),
(c) drawdown-avoidance, (d) does the rubber-price break say anything about the rubber
STOCKS (GVR/PHR/DPR/DRI/TRC/HRC) — the thing the alert exists to protect."""
import numpy as np, pandas as pd, subprocess, io, os

W = "/home/trido/thanhdt/WorkingClaude"
m = pd.read_csv(f"{W}/data/rubber_monthly.csv")
m["dt"] = pd.to_datetime(m["month"].astype(str) + "-15")
m = m[m["price"].notna()].sort_values("dt").reset_index(drop=True)
p = pd.Series(m["price"].astype(float).values, index=m["dt"])
px = p.values


def ma_break(price, win):
    ma = price.rolling(win).mean()
    below = price < ma
    sig = below & ~below.shift(1, fill_value=False) & ma.notna()
    return sig, ma, below


def confirm(sig, below, k):
    if k <= 1:
        return sig
    run = below.copy()
    for j in range(1, k):
        run &= below.shift(j, fill_value=False)
    return run & ~run.shift(1, fill_value=False)


# ------------------------------------------------------- (a) zigzag cycles ------
def zigzag(v, thr=0.25):
    """Alternating peaks/troughs; a new extreme is confirmed once price retraces >= thr."""
    piv, mode, last_i = [], None, 0
    for i in range(1, len(v)):
        if mode in (None, "up"):
            if v[i] > v[last_i]:
                last_i = i
            elif v[i] / v[last_i] - 1 <= -thr:
                piv.append(("P", last_i)); mode, last_i = "down", i
                continue
        if mode in (None, "down"):
            if v[i] < v[last_i]:
                last_i = i
            elif v[i] / v[last_i] - 1 >= thr:
                piv.append(("T", last_i)); mode, last_i = "up", i
    return piv


piv = zigzag(px, 0.25)
cycles = []
for (k1, i1), (k2, i2) in zip(piv, piv[1:]):
    if k1 == "P" and k2 == "T":
        cycles.append((i1, i2, px[i2] / px[i1] - 1))

sig10, ma10, below10 = ma_break(p, 10)
ev1 = [i for i, s in enumerate(sig10.values) if s]
ev2 = [i for i, s in enumerate(confirm(sig10, below10, 2).values) if s]

print("=" * 84)
print("(a) REAL DOWN-CYCLES (zigzag 25%) vs first MA10 down-break")
print("=" * 84)
hit1 = hit2 = 0
for j, k, dd in cycles:
    a = [e for e in ev1 if j <= e <= k]
    b = [e for e in ev2 if j <= e <= k]
    s1 = f"{p.index[a[0]]:%Y-%m} (+{a[0]-j}m, {(px[a[0]]/px[j]-1)*100:+.0f}% gone, còn {(px[k]/px[a[0]+1]-1)*100:+.0f}%)" if a else "KHÔNG BÁO"
    s2 = f"{p.index[b[0]]:%Y-%m} (+{b[0]-j}m)" if b else "KHÔNG BÁO"
    hit1 += bool(a); hit2 += bool(b)
    print(f"  đỉnh {p.index[j]:%Y-%m} {px[j]:5.2f} -> đáy {p.index[k]:%Y-%m} {px[k]:5.2f} ({dd*100:+4.0f}%)")
    print(f"       break confirm-1m: {s1}")
    print(f"       break confirm-2m: {s2}")
print(f"\n  Bắt được: confirm-1m {hit1}/{len(cycles)} chu kỳ | confirm-2m {hit2}/{len(cycles)}")
in_cyc = set()
for j, k, _ in cycles:
    in_cyc.update(range(j, k + 1))
for lbl, ev in (("confirm-1m", ev1), ("confirm-2m", ev2)):
    fa = [e for e in ev if e not in in_cyc]
    print(f"  {lbl}: {len(ev)} lần báo, {len(ev)-len(fa)} trong chu kỳ giảm thật, "
          f"{len(fa)} ngoài => precision {100*(len(ev)-len(fa))/len(ev):.0f}%")
    print(f"        ngoài chu kỳ: {[p.index[e].strftime('%Y-%m') for e in fa]}")

# ------------------------------------------- (b) P(big further decline | break) --
print("\n" + "=" * 84)
print("(b) METRIC ĐÚNG CHO 1 TẦNG CẢNH BÁO: P(giá giảm tiếp >= X% trong 6 tháng)")
print("=" * 84)
def p_drop(idx_list, thr, h=6):
    hits = tot = 0
    for i in idx_list:
        if i + 1 + h >= len(px):
            continue
        fwd_min = px[i + 1:i + 2 + h].min()
        tot += 1
        hits += (fwd_min / px[i + 1] - 1) <= -thr
    return hits, tot


for thr in (0.10, 0.15, 0.20):
    hb, tb = p_drop(range(len(px)), thr)
    print(f"  giảm tiếp >= {thr*100:.0f}% trong 6m:  base {hb}/{tb} = {100*hb/tb:4.0f}%", end="")
    for lbl, ev in (("MA10 c1", ev1), ("MA10 c2", ev2)):
        h, t = p_drop(ev, thr)
        print(f"  | {lbl} {h}/{t} = {100*h/t if t else 0:4.0f}%", end="")
    print()

# ------------------------------------------------------ (c) drawdown avoided ----
print("\n" + "=" * 84)
print("(c) TRÁNH SỤT GIẢM: giữ giá cao su vs thoát khi phá MA10, vào lại khi cắt lên")
print("=" * 84)
for win in (10, 5):
    ma = p.rolling(win).mean()
    pos = (p >= ma).shift(1).fillna(False)          # act next month, causal
    r = p.pct_change().fillna(0)
    nav_bh = (1 + r).cumprod()
    nav_sy = (1 + r * pos).cumprod()
    def mdd(s): return float((s / s.cummax() - 1).min()) * 100
    print(f"  MA{win}: buy&hold cuối {nav_bh.iloc[-1]:.2f}x MaxDD {mdd(nav_bh):+.0f}% | "
          f"thoát-khi-phá cuối {nav_sy.iloc[-1]:.2f}x MaxDD {mdd(nav_sy):+.0f}% | "
          f"thời gian ở ngoài {100*(1-pos.mean()):.0f}%")

# ------------------------------------------------------ (d) rubber stocks -------
print("\n" + "=" * 84)
print("(d) TÍN HIỆU NÀY CÓ NÓI GÌ VỀ CỔ PHIẾU CAO SU KHÔNG? (GVR/PHR/DPR/DRI/TRC/HRC)")
print("=" * 84)
SQL = ("SELECT t.ticker, t.time, t.Close FROM tav2_bq.ticker AS t "
       "WHERE t.ticker IN ('GVR','PHR','DPR','DRI','TRC','HRC') AND t.time >= '2006-01-01' "
       "ORDER BY t.time")
cache = f"{W}/mike/agents/Taylor/exp_rubber_trend/rubber_stocks.csv"
if not os.path.exists(cache):
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=csv",
                          "--max_rows=1000000", "--project_id=lithe-record-440915-m9", SQL],
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        print("  [bq failed]", out.stderr[-500:]); raise SystemExit(0)
    open(cache, "w").write(out.stdout)
s = pd.read_csv(cache)
s["time"] = pd.to_datetime(s["time"])
s = s[s["Close"].notna()]
# equal-weight monthly basket return
s["ym"] = s["time"].dt.to_period("M")
mo = s.groupby(["ticker", "ym"])["Close"].last().unstack(0)
ret = mo.pct_change()
bask = ret.mean(axis=1, skipna=True)          # equal-weight, names present that month
bask.index = bask.index.to_timestamp() + pd.Timedelta(days=14)
print(f"  rổ cổ phiếu: {mo.shape[1]} mã, {bask.dropna().index[0]:%Y-%m} .. {bask.dropna().index[-1]:%Y-%m}, "
      f"{bask.notna().sum()} tháng có dữ liệu")

def stock_fwd(i, h):
    d = p.index[i]
    fut = bask[(bask.index > d)][:h]
    return float((1 + fut).prod() - 1) * 100 if len(fut) == h else None


for h in (3, 6, 12):
    allr = [stock_fwd(i, h) for i in range(len(px))]
    allr = [x for x in allr if x is not None]
    base = np.mean(allr)
    print(f"\n  fwd {h:2d}m rổ cổ phiếu — base {base:+6.2f}% (n={len(allr)})")
    for lbl, ev in (("MA10 confirm-1m", ev1), ("MA10 confirm-2m", ev2)):
        v = [stock_fwd(i, h) for i in ev]
        v = [x for x in v if x is not None]
        if not v:
            continue
        rng = np.random.default_rng(11)
        bs = [np.mean(rng.choice(v, len(v), replace=True)) for _ in range(5000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        loo = [np.mean(np.delete(np.array(v), k)) for k in range(len(v))]
        print(f"    {lbl}: mean {np.mean(v):+6.2f}% (edge {np.mean(v)-base:+6.2f}pp) "
              f"CI95 [{lo:+.1f},{hi:+.1f}] n={len(v)} P(down) {100*np.mean(np.array(v)<0):.0f}% "
              f"LOO [{min(loo):+.1f},{max(loo):+.1f}]")
