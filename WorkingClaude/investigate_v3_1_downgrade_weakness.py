# -*- coding: utf-8 -*-
"""
investigate_v3_1_downgrade_weakness.py
======================================
Path (c): deep-dive into the 138 downgrade transitions of v3.1 to
find out why T+20 win rate is essentially equal to base rate (44.2% vs 44.9%).

Mean edge IS negative (-0.77pp T+20, -1.45pp T+60) so downgrades DO
shift the distribution down, but they fail to flip the SIGN of the
window often enough — VN has +0.27%/week drift that drowns out signal.

Hypotheses to test:
  (H1) Downgrades on weak signals (r_dual marginal) underperform
  (H2) Downgrades when concentration is high (VIC-led illusion) are
       fake-downs (market keeps drifting up)
  (H3) Downgrades with US-override active are too reactive
  (H4) Step-size matters (1-step vs 2-step vs 3+ step)
  (H5) Era matters (pre-2014 vs 2014-19 vs 2020-26)
  (H6) Specific pair matters (BULL→NEUTRAL probably weak;
       NEUTRAL→BEAR or BEAR→CRISIS probably stronger)
  (H7) Reverted_30d marker — transitions that don't even stick

For each candidate rule we report:
  • how many transitions KEPT (i.e. still allowed to downgrade)
  • forward edge on the KEPT subset at T+5/T+20/T+60
  • forward edge on the BLOCKED subset (should be LESS negative
    or even positive — we don't want to filter out the real bears)
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}

# ── Load ───────────────────────────────────────────────────────────────
st = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
st["time"] = pd.to_datetime(st["time"]); st = st.sort_values("time").reset_index(drop=True)
dr = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])
df = st.merge(dr[["time","Close","r_score_raw","r_score_ew","alpha","concentration_smooth"]],
              on="time", how="left").merge(
    diag[["time","spx_dd_1y","vix","us_cap","override_fired"]], on="time", how="left").reset_index(drop=True)
df["r_dual"] = df["alpha"]*df["r_score_raw"] + (1-df["alpha"])*df["r_score_ew"]
n = len(df); close=df["Close"].values; state=df["state"].values.astype(int)

# Simple RSI(14)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0)
    down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100
        out[i] = 100 - 100/(1+rs)
    return out
df["rsi14"] = rsi14(close)
ma200 = pd.Series(close).rolling(200).mean().values
df["ma200_dev"] = close/ma200 - 1

# Base rates
print(f"Loaded {n} rows | {df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}\n")
print("=== Unconditional VN-Index base rate ===")
base = {}
for h in [5,20,60]:
    r = np.array([close[i+h]/close[i]-1 for i in range(n-h)])
    base[h] = dict(n=len(r), mean=r.mean()*100, pos=(r>0).mean()*100, neg=(r<0).mean()*100)
    print(f"  T+{h:>2}: mean {r.mean()*100:+.2f}% | %neg {(r<0).mean()*100:.1f}%")

# ── Collect downgrade transitions ─────────────────────────────────────
trans = []
prev = state[0]
for i in range(1, n):
    if state[i] != prev:
        f_n, t_n = STATE_NAMES[prev], STATE_NAMES[state[i]]
        step = ORDER[t_n] - ORDER[f_n]
        if step < 0:  # downgrade only
            rec = dict(
                i=i, date=df["time"].iloc[i], from_=f_n, to=t_n,
                step=step, abs_step=abs(step), pair=f"{f_n}→{t_n}",
                close=float(close[i]),
                r_raw=float(df["r_score_raw"].iloc[i])  if not pd.isna(df["r_score_raw"].iloc[i]) else None,
                r_ew =float(df["r_score_ew"].iloc[i])   if not pd.isna(df["r_score_ew"].iloc[i]) else None,
                alpha=float(df["alpha"].iloc[i])        if not pd.isna(df["alpha"].iloc[i]) else None,
                conc =float(df["concentration_smooth"].iloc[i]) if not pd.isna(df["concentration_smooth"].iloc[i]) else None,
                r_dual=float(df["r_dual"].iloc[i])      if not pd.isna(df["r_dual"].iloc[i]) else None,
                rsi  =float(df["rsi14"].iloc[i])        if not pd.isna(df["rsi14"].iloc[i]) else None,
                ma200_dev=float(df["ma200_dev"].iloc[i]) if not pd.isna(df["ma200_dev"].iloc[i]) else None,
                vix  =float(df["vix"].iloc[i])          if not pd.isna(df["vix"].iloc[i]) else None,
                spx_dd=float(df["spx_dd_1y"].iloc[i])   if not pd.isna(df["spx_dd_1y"].iloc[i]) else None,
                us_cap=int(df["us_cap"].iloc[i])        if not pd.isna(df["us_cap"].iloc[i]) else None,
                fired_window=bool(df["override_fired"].iloc[max(0,i-2):i+1].any()),
                year=df["time"].iloc[i].year,
            )
            for h in [5,20,60]:
                rec[f"r{h}"] = close[i+h]/close[i]-1 if i+h<n else None
            # state reverts UP within 30d? (downgrade was over-reaction)
            rec["reverted_30d"] = False
            for j in range(i+1, min(n, i+31)):
                if state[j] > state[i]:
                    rec["reverted_30d"] = True
                    rec["revert_at"] = j-i
                    break
            prev = state[i]
            trans.append(rec)
        else:
            prev = state[i]

trans = [t for t in trans if t["r60"] is not None]
N = len(trans)
print(f"\n{N} downgrade transitions with full T+60 lookahead\n")

# ── Helper ─────────────────────────────────────────────────────────────
def stats(rows, h):
    if not rows: return None
    rs = np.array([r[f"r{h}"] for r in rows])
    return dict(
        n=len(rs), mean=rs.mean()*100,
        win=(rs<0).mean()*100,  # for downgrade: win = market went DOWN
    )

def edge_summary(rows, label, base):
    if not rows: print(f"{label}: n=0"); return
    out = []
    for h in [5,20,60]:
        s = stats(rows, h)
        if s is None: out.append("—"); continue
        base_neg = base[h]['neg']; base_mean = base[h]['mean']
        edge_w = s['win'] - base_neg
        edge_m = base_mean - s['mean']   # mean edge: lower mean = good for downgrade
        out.append(f"T+{h}: n={s['n']} win={s['win']:.0f}% (edge {edge_w:+.1f}pp), mean={s['mean']:+.2f}% (edge {edge_m:+.2f}pp lower)")
    print(f"{label:<30}\n  " + "\n  ".join(out))

# ── (1) PER-PAIR breakdown ────────────────────────────────────────────
print("="*100); print("(1) PER-PAIR DOWNGRADE — which from→to pairs work?"); print("="*100)
pairs = {}
for t in trans:
    pairs.setdefault(t["pair"], []).append(t)

print(f"\n{'Pair':<22}{'n':>5}  T+5 win%/mean    T+20 win%/mean   T+60 win%/mean  rev30d")
print("-"*100)
for pair in sorted(pairs.keys(), key=lambda p:(ORDER[p.split('→')[0]], -ORDER[p.split('→')[1]])):
    rows = pairs[pair]
    cells = []
    for h in [5,20,60]:
        s = stats(rows, h)
        bn = base[h]['neg']
        # color hint via sign
        ew = s['win'] - bn
        cells.append(f"{s['win']:>3.0f}%/{s['mean']:>+5.2f}% ({ew:>+5.1f}pp)")
    rev = sum(1 for r in rows if r["reverted_30d"])
    print(f"{pair:<22}{len(rows):>5}  {cells[0]}  {cells[1]}  {cells[2]}  {rev}/{len(rows)}")

# ── (2) PER-STEP × pair ────────────────────────────────────────────────
print("\n" + "="*100); print("(2) STEP SIZE — bigger jump should be stronger signal"); print("="*100)
for step_grp, label in [(1,"1-step"), (2,"2-step"), (3,"3+ step")]:
    if step_grp == 3:
        rows = [t for t in trans if t["abs_step"]>=3]
    else:
        rows = [t for t in trans if t["abs_step"]==step_grp]
    print(f"\n▼ {label} (n={len(rows)})")
    if not rows: continue
    for h in [5,20,60]:
        s = stats(rows, h); bn = base[h]['neg']; bm = base[h]['mean']
        print(f"  T+{h:>2}: win={s['win']:>4.1f}% (edge {s['win']-bn:+.1f}pp) | mean={s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")
    rev = sum(1 for r in rows if r["reverted_30d"])
    print(f"  Reverted_30d: {rev}/{len(rows)} = {rev/len(rows)*100:.0f}%")

# ── (3) BY ERA ─────────────────────────────────────────────────────────
print("\n" + "="*100); print("(3) BY ERA — has v3.1 quality improved over time?"); print("="*100)
eras = [("2000-2013", 2000, 2013), ("2014-2019", 2014, 2019),
        ("2020-2026", 2020, 2026)]
print(f"\n{'Era':<14}{'n':>5}{'T+20 win':>11}{'T+20 mean':>12}{'T+60 win':>11}{'T+60 mean':>12}{'rev30d %':>10}")
print("-"*80)
for label, y0, y1 in eras:
    rows = [t for t in trans if y0 <= t["year"] <= y1]
    if not rows: print(f"{label:<14}{0:>5}"); continue
    s5  = stats(rows, 5)
    s20 = stats(rows, 20)
    s60 = stats(rows, 60)
    rev = sum(1 for r in rows if r["reverted_30d"])
    print(f"{label:<14}{len(rows):>5}{s20['win']:>10.1f}%{s20['mean']:>+11.2f}%"
          f"{s60['win']:>10.1f}%{s60['mean']:>+11.2f}%{rev/len(rows)*100:>9.0f}%")

# ── (4) BY r_dual at trigger (was signal strong?) ─────────────────────
print("\n" + "="*100); print("(4) r_dual STRENGTH — weak score → bad downgrade?"); print("="*100)
print("(For a downgrade to NEUTRAL/BEAR/CRISIS, r_dual SHOULD be low. If high → fake downgrade)")
buckets = [
    ("r_dual < 0.10  (strong CRISIS)",  lambda t: t["r_dual"] is not None and t["r_dual"] <  0.10),
    ("0.10 ≤ r_dual < 0.20  (BEAR zone)", lambda t: t["r_dual"] is not None and 0.10 <= t["r_dual"] < 0.20),
    ("0.20 ≤ r_dual < 0.40  (weak NEUTRAL)", lambda t: t["r_dual"] is not None and 0.20 <= t["r_dual"] < 0.40),
    ("0.40 ≤ r_dual < 0.55  (mid NEUTRAL)",  lambda t: t["r_dual"] is not None and 0.40 <= t["r_dual"] < 0.55),
    ("r_dual ≥ 0.55  (high — suspect fake downgrade)", lambda t: t["r_dual"] is not None and t["r_dual"] >= 0.55),
]
print(f"\n{'Bucket':<48}{'n':>5}{'T+20 win':>10}{'T+20 mean':>11}{'T+60 win':>10}{'T+60 mean':>11}")
print("-"*100)
for label, pred in buckets:
    rows = [t for t in trans if pred(t)]
    if not rows: print(f"{label:<48}{0:>5}"); continue
    s20 = stats(rows, 20); s60 = stats(rows, 60)
    print(f"{label:<48}{len(rows):>5}{s20['win']:>9.1f}%{s20['mean']:>+10.2f}%{s60['win']:>9.1f}%{s60['mean']:>+10.2f}%")

# ── (5) BY CONCENTRATION at trigger ────────────────────────────────────
print("\n" + "="*100); print("(5) CONCENTRATION — VIC-led illusion theory"); print("="*100)
print("(If concentration high, EW breadth is weak; downgrade may correctly catch fake rally collapse)")
buckets = [
    ("conc < 0.40 (broad)",  lambda t: t["conc"] is not None and t["conc"] <  0.40),
    ("0.40-0.55",            lambda t: t["conc"] is not None and 0.40 <= t["conc"] < 0.55),
    ("0.55-0.70 (concentrated)", lambda t: t["conc"] is not None and 0.55 <= t["conc"] < 0.70),
    ("≥ 0.70 (VIC-led)",     lambda t: t["conc"] is not None and t["conc"] >= 0.70),
    ("(N/A — pre-conc data)", lambda t: t["conc"] is None),
]
print(f"\n{'Bucket':<28}{'n':>5}{'T+20 win':>10}{'T+20 mean':>11}{'T+60 win':>10}{'T+60 mean':>11}")
print("-"*80)
for label, pred in buckets:
    rows = [t for t in trans if pred(t)]
    if not rows: print(f"{label:<28}{0:>5}"); continue
    s20 = stats(rows, 20); s60 = stats(rows, 60)
    print(f"{label:<28}{len(rows):>5}{s20['win']:>9.1f}%{s20['mean']:>+10.2f}%{s60['win']:>9.1f}%{s60['mean']:>+10.2f}%")

# ── (6) US OVERRIDE active vs not ──────────────────────────────────────
print("\n" + "="*100); print("(6) US OVERRIDE — does override-driven downgrade work?"); print("="*100)
fired = [t for t in trans if t["fired_window"]]
not_fired = [t for t in trans if not t["fired_window"]]
print(f"\nFired window (n={len(fired)}):")
for h in [5,20,60]:
    s = stats(fired, h); bn = base[h]['neg']; bm = base[h]['mean']
    print(f"  T+{h:>2}: win {s['win']:.0f}% (edge {s['win']-bn:+.1f}pp), mean {s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")
print(f"\nNot fired (n={len(not_fired)}):")
for h in [5,20,60]:
    s = stats(not_fired, h); bn = base[h]['neg']; bm = base[h]['mean']
    print(f"  T+{h:>2}: win {s['win']:.0f}% (edge {s['win']-bn:+.1f}pp), mean {s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")

# ── (7) REVERTED_30D split ─────────────────────────────────────────────
print("\n" + "="*100); print("(7) REVERTED 30d — downgrades that didn't even stick"); print("="*100)
rev    = [t for t in trans if t["reverted_30d"]]
stable = [t for t in trans if not t["reverted_30d"]]
print(f"\nReverted within 30d (n={len(rev)} = {len(rev)/N*100:.0f}%):")
for h in [5,20,60]:
    s = stats(rev, h); bn = base[h]['neg']; bm = base[h]['mean']
    print(f"  T+{h:>2}: win {s['win']:.0f}% (edge {s['win']-bn:+.1f}pp), mean {s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")
print(f"\nStable for 30d+ (n={len(stable)}):")
for h in [5,20,60]:
    s = stats(stable, h); bn = base[h]['neg']; bm = base[h]['mean']
    print(f"  T+{h:>2}: win {s['win']:.0f}% (edge {s['win']-bn:+.1f}pp), mean {s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")

# ── (8) BULL→NEUTRAL deep-dive (largest pair, likely main problem) ────
print("\n" + "="*100); print("(8) BULL→NEUTRAL DEEP-DIVE  (likely the main noise source)"); print("="*100)
bn_rows = [t for t in trans if t["pair"]=="BULL→NEUTRAL"]
print(f"\nTotal: n={len(bn_rows)}")
for h in [5,20,60]:
    s = stats(bn_rows, h); bn=base[h]['neg']; bm=base[h]['mean']
    print(f"  T+{h:>2}: win {s['win']:.0f}% (edge {s['win']-bn:+.1f}pp), mean {s['mean']:+.2f}% (edge {bm-s['mean']:+.2f}pp lower)")

# split by r_dual
print(f"\nBy r_dual at trigger:")
for cut_low, cut_hi, label in [(0,0.40,"r<0.40 strong sell"), (0.40,0.55,"0.40-0.55"),
                                (0.55,1.0,"r≥0.55 weak signal")]:
    sub = [t for t in bn_rows if t["r_dual"] is not None and cut_low <= t["r_dual"] < cut_hi]
    if not sub: continue
    s20 = stats(sub, 20); s60 = stats(sub, 60)
    print(f"  {label:<22} n={len(sub):>3}  T+20 win {s20['win']:>4.0f}% mean {s20['mean']:+5.2f}%   "
          f"T+60 win {s60['win']:>4.0f}% mean {s60['mean']:+5.2f}%")

# ── (9) Candidate filter rules ─────────────────────────────────────────
print("\n" + "="*100); print("(9) CANDIDATE FILTER RULES — block these downgrade triggers?"); print("="*100)
print("KEPT = still downgrade; BLOCKED = skip downgrade (stay in higher state)")
print("Goal: BLOCKED rows should have positive mean (we don't want to miss real downgrades)\n")

def filter_test(label, keep_fn):
    kept   = [t for t in trans if keep_fn(t)]
    block  = [t for t in trans if not keep_fn(t)]
    print(f"\n{label}")
    for h in [20,60]:
        sk = stats(kept, h);  sb = stats(block, h)
        bn = base[h]['neg']; bm = base[h]['mean']
        print(f"  T+{h:>2} KEPT  n={len(kept):>3} win={sk['win']:>4.1f}% (edge {sk['win']-bn:+.1f}pp) "
              f"mean={sk['mean']:+5.2f}% (edge {bm-sk['mean']:+.2f}pp lower)")
        print(f"        BLOCK n={len(block):>3} win={sb['win']:>4.1f}% (edge {sb['win']-bn:+.1f}pp) "
              f"mean={sb['mean']:+5.2f}% (edge {bm-sb['mean']:+.2f}pp lower)  ← want POSITIVE edge")

# F1: block downgrades where r_dual is HIGH (weak signal)
for thr in [0.55, 0.60, 0.65]:
    filter_test(f"F1: r_dual < {thr}  (only downgrade on convincing weakness)",
                lambda t, _t=thr: (t["r_dual"] is not None) and (t["r_dual"] < _t))

# F2: only downgrade if concentration high AND signal weak
filter_test("F2: r_dual<0.55 OR concentration<0.50 (broad weakness)",
            lambda t: ((t["r_dual"] is not None and t["r_dual"]<0.55)
                       or (t["conc"] is not None and t["conc"]<0.50)
                       or (t["conc"] is None)))

# F3: require RSI < 60 (not on temporary pullback)
filter_test("F3: RSI < 60 at trigger (not just pullback dip)",
            lambda t: (t["rsi"] is None) or (t["rsi"] < 60))

# F4: skip BULL→NEUTRAL specifically (largest noise pair, if confirmed)
filter_test("F4: skip BULL→NEUTRAL only",
            lambda t: t["pair"] != "BULL→NEUTRAL")

# F5: skip BULL→NEUTRAL when r_dual still mid-range
filter_test("F5: skip BULL→NEUTRAL with r_dual ≥ 0.40",
            lambda t: not (t["pair"]=="BULL→NEUTRAL" and t["r_dual"] is not None and t["r_dual"]>=0.40))

# F6: skip 1-step + RSI>55 (small downgrade on minor pullback)
filter_test("F6: skip 1-step downgrades when RSI ≥ 55",
            lambda t: not (t["abs_step"]==1 and t["rsi"] is not None and t["rsi"]>=55))

# F7: post-2014 only (skip pre-2014 era)
filter_test("F7: post-2014 only",
            lambda t: t["year"] >= 2014)

print("\n--- DONE ---")
