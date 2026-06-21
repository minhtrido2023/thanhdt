# -*- coding: utf-8 -*-
"""
investigate_v3_1_2step_upgrades.py
==================================
Deep-dive into every 2-step upgrade transition in Tam Quan v3.1.

Goal: figure out whether the 15-trade negative-edge signal is
  (a) statistical noise (n too small)
  (b) a real failure mode triggered by some observable condition
      (concentration / RSI / VIX / r_dual barely over threshold / etc.)

For every 2-step upgrade we collect:
  • r_raw, r_ew, alpha, conc, r_dual at trigger
  • VIX, SPX_DD_1Y, us_cap at trigger
  • T+5/T+20/T+60 fwd return
  • What happened to state in next 30 sessions (immediate reversal?)

Then we test a few candidate filter rules and report:
  • how many trades they would have blocked
  • the win/mean edge of trades they would have KEPT
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ORDER = {"CRISIS":1,"BEAR":2,"NEUTRAL":3,"BULL":4,"EX-BULL":5}

# ── Load ────────────────────────────────────────────────────────────────
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
print(f"Loaded {n} rows")

# Compute simple RSI(14) on close just for context
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

# Compute close vs MA200
ma200 = pd.Series(close).rolling(200).mean().values
df["ma200_dev"] = close/ma200 - 1
df["ma50_dev"]  = close/pd.Series(close).rolling(50).mean().values - 1

# ── Collect transitions ─────────────────────────────────────────────────
trans = []
prev = state[0]
for i in range(1, n):
    if state[i] != prev:
        f_n, t_n = STATE_NAMES[prev], STATE_NAMES[state[i]]
        step = ORDER[t_n] - ORDER[f_n]
        rec = dict(
            i=i, date=df["time"].iloc[i], from_=f_n, to=t_n, step=step, abs_step=abs(step),
            dir="up" if step>0 else "down",
            close=float(close[i]),
            r_raw=float(df["r_score_raw"].iloc[i])  if not pd.isna(df["r_score_raw"].iloc[i]) else None,
            r_ew =float(df["r_score_ew"].iloc[i])   if not pd.isna(df["r_score_ew"].iloc[i]) else None,
            alpha=float(df["alpha"].iloc[i])        if not pd.isna(df["alpha"].iloc[i]) else None,
            conc =float(df["concentration_smooth"].iloc[i]) if not pd.isna(df["concentration_smooth"].iloc[i]) else None,
            r_dual=float(df["r_dual"].iloc[i])      if not pd.isna(df["r_dual"].iloc[i]) else None,
            rsi  =float(df["rsi14"].iloc[i])        if not pd.isna(df["rsi14"].iloc[i]) else None,
            ma200_dev=float(df["ma200_dev"].iloc[i]) if not pd.isna(df["ma200_dev"].iloc[i]) else None,
            ma50_dev =float(df["ma50_dev"].iloc[i])  if not pd.isna(df["ma50_dev"].iloc[i]) else None,
            vix  =float(df["vix"].iloc[i])          if not pd.isna(df["vix"].iloc[i]) else None,
            spx_dd=float(df["spx_dd_1y"].iloc[i])   if not pd.isna(df["spx_dd_1y"].iloc[i]) else None,
            us_cap=int(df["us_cap"].iloc[i])        if not pd.isna(df["us_cap"].iloc[i]) else None,
            fired_window=bool(df["override_fired"].iloc[max(0,i-2):i+1].any()),
        )
        # forward returns + reversal flag
        for h in [5,20,60]:
            rec[f"r{h}"] = close[i+h]/close[i]-1 if i+h<n else None
        # did state revert (go DOWN at any point) within 30 sessions?
        rec["reverted_30d"] = False
        rec["max_state_30d"] = state[i]
        for j in range(i+1, min(n, i+31)):
            rec["max_state_30d"] = max(rec["max_state_30d"], state[j])
            if state[j] < state[i]:
                rec["reverted_30d"] = True
                rec["revert_at"] = j-i
                break
        else:
            rec["revert_at"] = None
        prev = state[i]
        trans.append(rec)

# Only complete
trans = [t for t in trans if t["r60"] is not None]

# ── Filter to 2-step upgrades ──────────────────────────────────────────
ups2 = [t for t in trans if t["dir"]=="up" and t["abs_step"]==2]
print(f"\n=== {len(ups2)} 2-step upgrades ===\n")

# Print each row
print(f"{'#':<3}{'Date':<13}{'From→To':<22}{'Close':>9}{'r_raw':>8}{'r_ew':>8}{'α':>6}"
      f"{'conc':>7}{'r_dual':>8}{'RSI':>6}{'MA50%':>8}{'MA200%':>9}"
      f"{'VIX':>6}{'r5%':>8}{'r20%':>8}{'r60%':>8}{'Revert30d':>11}")
print("-"*180)

for idx, t in enumerate(ups2, 1):
    revert = "—"
    if t["reverted_30d"]:
        revert = f"YES@{t['revert_at']}d"
    print(f"{idx:<3}{t['date'].strftime('%Y-%m-%d'):<13}"
          f"{t['from_']+'→'+t['to']:<22}"
          f"{t['close']:>9.1f}"
          f"{t['r_raw']*100:>7.0f}%" if t['r_raw'] else f"{'N/A':>8}",
          end="")
    print(f"{t['r_ew']*100:>7.0f}%" if t['r_ew'] else f"{'N/A':>8}",
          f"{t['alpha']:>5.2f}" if t['alpha'] else f"{'N/A':>6}",
          f"{t['conc']:>6.2f}" if t['conc'] else f"{'N/A':>7}",
          f"{t['r_dual']*100:>7.0f}%" if t['r_dual'] else f"{'N/A':>8}",
          f"{t['rsi']:>5.0f}" if t['rsi'] else f"{'N/A':>6}",
          f"{t['ma50_dev']*100:>+7.1f}%" if t['ma50_dev'] is not None else f"{'N/A':>8}",
          f"{t['ma200_dev']*100:>+8.1f}%" if t['ma200_dev'] is not None else f"{'N/A':>9}",
          f"{t['vix']:>5.0f}" if t['vix'] else f"{'N/A':>6}",
          f"{t['r5']*100:>+7.1f}%",
          f"{t['r20']*100:>+7.1f}%",
          f"{t['r60']*100:>+7.1f}%",
          f"{revert:>11}", sep="")

# ── Quick group split: by transition pair ─────────────────────────────
print("\n--- By transition pair ---")
pair_groups = {}
for t in ups2:
    pair_groups.setdefault((t["from_"], t["to"]), []).append(t)
for (f_n,t_n), rows in pair_groups.items():
    rs5  = np.array([r["r5"]  for r in rows])
    rs20 = np.array([r["r20"] for r in rows])
    rs60 = np.array([r["r60"] for r in rows])
    rev  = sum(1 for r in rows if r["reverted_30d"])
    print(f"{f_n}→{t_n}: n={len(rows)}  T+5 mean={rs5.mean()*100:+.2f}% win={(rs5>0).mean()*100:.0f}%  "
          f"T+20 mean={rs20.mean()*100:+.2f}% win={(rs20>0).mean()*100:.0f}%  "
          f"T+60 mean={rs60.mean()*100:+.2f}% win={(rs60>0).mean()*100:.0f}%  "
          f"reverted_30d={rev}/{len(rows)}")

# ── Filter rule experiments ───────────────────────────────────────────
print("\n=== Candidate filter rules ===")
print("(KEEP = transition allowed; BLOCK = forbidden. We want KEPT subset to have positive edge.)\n")

def eval_filter(rule_name, keep_fn, all_rows):
    kept   = [t for t in all_rows if keep_fn(t)]
    block  = [t for t in all_rows if not keep_fn(t)]
    if not kept and not block: return
    def stats(rows, h):
        if not rows: return "n=0"
        rs = np.array([r[f"r{h}"] for r in rows])
        return f"n={len(rs)}, mean={rs.mean()*100:+.2f}%, win={(rs>0).mean()*100:.0f}%"
    print(f"\n{rule_name}")
    for h in [5,20,60]:
        print(f"  T+{h:>2}  KEPT  {stats(kept, h):<40}  BLOCKED  {stats(block, h)}")
    if kept:
        revs = sum(1 for r in kept if r["reverted_30d"])
        print(f"   reverted_30d in KEPT: {revs}/{len(kept)}")

# Rule 1: only allow if r_dual >= some threshold (filter "barely over")
for thr in [0.60, 0.70, 0.75, 0.80]:
    eval_filter(f"R1: r_dual >= {thr:.2f}",
                lambda t, _thr=thr: (t["r_dual"] or 0) >= _thr, ups2)

# Rule 2: only allow if concentration low (broad-based rally)
for thr in [0.50, 0.55, 0.60, 0.65]:
    eval_filter(f"R2: concentration <= {thr:.2f}  (broad rally only)",
                lambda t, _thr=thr: (t["conc"] is None) or (t["conc"] <= _thr), ups2)

# Rule 3: RSI cap (not already overbought)
for thr in [60, 65, 70]:
    eval_filter(f"R3: RSI <= {thr}  (not over-extended)",
                lambda t, _thr=thr: (t["rsi"] is None) or (t["rsi"] <= _thr), ups2)

# Rule 4: MA200_dev cap (price not too far above trend)
for thr in [0.10, 0.15, 0.20]:
    eval_filter(f"R4: close/MA200 - 1 <= {thr*100:.0f}%  (not stretched)",
                lambda t, _thr=thr: (t["ma200_dev"] is None) or (t["ma200_dev"] <= _thr), ups2)

# Rule 5: block if US override active or US still risky
eval_filter("R5: us_cap == 5 (US calm only)",
            lambda t: t["us_cap"] is None or t["us_cap"] >= 5, ups2)

# Rule 6: combined — broad rally + not stretched RSI
eval_filter("R6: conc <= 0.60 AND RSI <= 65",
            lambda t: ((t["conc"] is None or t["conc"] <= 0.60)
                       and (t["rsi"] is None or t["rsi"] <= 65)), ups2)

# Rule 7: WAYPOINT — block direct 2-step entirely (force 1-step + wait)
eval_filter("R7: BLOCK ALL 2-step (force step-by-step)",
            lambda t: False, ups2)

# Rule 8: only block specific pair NEUTRAL→EX-BULL (might be worst)
eval_filter("R8: block NEUTRAL→EX-BULL only (keep BEAR→BULL & CRISIS→NEUTRAL)",
            lambda t: not (t["from_"]=="NEUTRAL" and t["to"]=="EX-BULL"), ups2)

# Rule 9: only block BEAR→BULL (might be premature)
eval_filter("R9: block BEAR→BULL only",
            lambda t: not (t["from_"]=="BEAR" and t["to"]=="BULL"), ups2)

print("\n--- DONE ---")
