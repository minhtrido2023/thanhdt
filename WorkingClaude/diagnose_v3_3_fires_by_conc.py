# -*- coding: utf-8 -*-
"""
diagnose_v3_3_fires_by_conc.py
==============================
For each of the 31 RSI-gate fires in v3.3, look up:
  • concentration (smoothed) at fire
  • r_dual at fire
  • T+20 and T+60 forward VNI return
  • whether the fire "helped" (gate kept us in higher state correctly)
    or "hurt" (gate held when downgrade was right)

A fire HELPED if forward VNI return is positive within the held window
(higher state would have captured upside). A fire HURT if forward is
negative (downgrade was right, gate cost us).

Goal: confirm whether high-concentration fires are systematically bad.
If yes, propose conc threshold that filters them out.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# Reproduce the 31 fire dates by running the v3.3 logic
v31 = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dual = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dual["time"] = pd.to_datetime(dual["time"])
dual["r_dual"] = dual["alpha"]*dual["r_score_raw"] + (1-dual["alpha"])*dual["r_score_ew"]

df = v31.merge(dual[["time","Close","concentration_smooth","r_dual","alpha"]],
               on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values; v31_state = df["state"].values.astype(int)

# RSI(14)
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
rsi = rsi14(close)
RSI_THR = 55

# Replay v3.3 + collect fires + measure how long gate was active
fires = []
blocked = False
blocked_at = None
block_start_i = None
for t in range(1, n):
    cur_v31 = v31_state[t]; prev_v31 = v31_state[t-1]; cur_rsi = rsi[t]
    if blocked:
        # exit?
        if (cur_rsi is None) or np.isnan(cur_rsi) or (cur_rsi < RSI_THR):
            # gate released
            blocked = False
            # log return over hold
            held_days = t - block_start_i
            ret_during = close[t]/close[block_start_i] - 1
            fires[-1]["held_days"] = held_days
            fires[-1]["ret_during_hold"] = ret_during
        elif cur_v31 >= blocked_at:
            blocked = False
            held_days = t - block_start_i
            ret_during = close[t]/close[block_start_i] - 1
            fires[-1]["held_days"] = held_days
            fires[-1]["ret_during_hold"] = ret_during
        elif (blocked_at - cur_v31) >= 2:
            blocked = False
            held_days = t - block_start_i
            ret_during = close[t]/close[block_start_i] - 1
            fires[-1]["held_days"] = held_days
            fires[-1]["ret_during_hold"] = ret_during
    else:
        if (prev_v31 - cur_v31 == 1) and (cur_rsi is not None) and (not np.isnan(cur_rsi)) and (cur_rsi >= RSI_THR):
            blocked = True
            blocked_at = prev_v31
            block_start_i = t
            r = df.iloc[t]
            fires.append(dict(
                date=df["time"].iloc[t], i=t,
                from_=STATE_NAMES[prev_v31], to=STATE_NAMES[cur_v31],
                rsi=cur_rsi,
                conc=float(r["concentration_smooth"]) if not pd.isna(r["concentration_smooth"]) else None,
                r_dual=float(r["r_dual"]) if not pd.isna(r["r_dual"]) else None,
                alpha=float(r["alpha"]) if not pd.isna(r["alpha"]) else None,
                close=float(close[t]),
                r5  = close[t+5]/close[t]-1  if t+5<n  else None,
                r20 = close[t+20]/close[t]-1 if t+20<n else None,
                r60 = close[t+60]/close[t]-1 if t+60<n else None,
                held_days=None, ret_during_hold=None,
            ))

# any still active at end
if blocked and fires:
    fires[-1]["held_days"] = n - block_start_i
    fires[-1]["ret_during_hold"] = close[n-1]/close[block_start_i] - 1

print(f"Total fires: {len(fires)}\n")

# Print each
print(f"{'#':<3}{'Date':<12}{'From→To':<22}{'RSI':>5}{'Conc':>7}{'r_dual':>8}"
      f"{'Held(d)':>9}{'Ret hold%':>11}{'r5%':>8}{'r20%':>8}{'r60%':>8}{'Verdict':>10}")
print("-"*125)
for idx, f in enumerate(fires, 1):
    conc_str = f"{f['conc']:.2f}" if f['conc'] is not None else "N/A"
    rd_str   = f"{f['r_dual']:.2f}" if f['r_dual'] is not None else "N/A"
    hold_str = f"{f['held_days']}" if f['held_days'] is not None else "?"
    ret_hold = f"{f['ret_during_hold']*100:+.1f}%" if f['ret_during_hold'] is not None else "?"
    r20_str  = f"{f['r20']*100:+.1f}%" if f['r20'] is not None else "?"
    r60_str  = f"{f['r60']*100:+.1f}%" if f['r60'] is not None else "?"
    r5_str   = f"{f['r5']*100:+.1f}%" if f['r5'] is not None else "?"
    # Verdict: gate HELPS if r20 > 0 (held higher state correctly)
    if f['r20'] is not None:
        verdict = "✓ HELP" if f['r20'] > 0 else "✗ HURT"
    else:
        verdict = "?"
    print(f"{idx:<3}{f['date'].date().isoformat():<12}{f['from_']+'→'+f['to']:<22}"
          f"{f['rsi']:>4.0f} {conc_str:>6} {rd_str:>7} "
          f"{hold_str:>8} {ret_hold:>10} {r5_str:>7} {r20_str:>7} {r60_str:>7}  {verdict:>10}")

# Sort by concentration to see pattern
print(f"\n=== Sorted by concentration (low → high) ===")
print(f"{'Date':<12}{'Conc':>7}{'r20%':>9}{'r60%':>9}{'Verdict':>10}")
print("-"*55)
sorted_fires = sorted([f for f in fires if f['conc'] is not None], key=lambda x: x['conc'])
for f in sorted_fires:
    r20s = f"{f['r20']*100:+.1f}%" if f['r20'] is not None else "?"
    r60s = f"{f['r60']*100:+.1f}%" if f['r60'] is not None else "?"
    v = "✓ HELP" if f['r20'] is not None and f['r20']>0 else "✗ HURT"
    print(f"{f['date'].date().isoformat():<12}{f['conc']:>6.2f} {r20s:>8} {r60s:>8}  {v:>9}")

# Group by conc bucket
print(f"\n=== Fire outcome by concentration bucket ===")
buckets = [(0, 0.45, "conc < 0.45 (very broad)"),
           (0.45, 0.55, "0.45-0.55 (broad)"),
           (0.55, 0.65, "0.55-0.65 (mid)"),
           (0.65, 1.0,  "≥ 0.65 (concentrated/narrow)")]
print(f"{'Bucket':<32}{'n':>4}{'T+20 mean':>11}{'%pos T+20':>11}{'T+60 mean':>11}{'%pos T+60':>11}")
print("-"*82)
for lo, hi, label in buckets:
    rows = [f for f in fires if f['conc'] is not None and lo <= f['conc'] < hi
            and f['r20'] is not None]
    if not rows: print(f"{label:<32}{0:>4}"); continue
    r20 = np.array([r['r20'] for r in rows])
    r60 = np.array([r['r60'] for r in rows if r['r60'] is not None])
    print(f"{label:<32}{len(rows):>4}{r20.mean()*100:>+10.2f}%{(r20>0).mean()*100:>10.0f}%"
          f"{r60.mean()*100 if len(r60) else 0:>+10.2f}%{(r60>0).mean()*100 if len(r60) else 0:>10.0f}%")

# Also: what conc threshold would block which fires?
print(f"\n=== Filter test: only fire gate when conc ≤ threshold ===")
print(f"(KEPT fires = still apply gate;  FILTERED = let downgrade through)")
print(f"{'Threshold':<14}{'KEPT n':>8}{'KEPT T+20 mean':>17}{'KEPT %pos':>11}{'FILT n':>8}{'FILT T+20 mean':>17}{'FILT %pos':>11}")
print("-"*100)
for thr in [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
    kept = [f for f in fires if f['conc'] is not None and f['conc'] <= thr and f['r20'] is not None]
    filt = [f for f in fires if f['conc'] is not None and f['conc'] >  thr and f['r20'] is not None]
    def stat(rs):
        if not rs: return "n=0"
        x = np.array([r['r20'] for r in rs])
        return x.mean()*100, (x>0).mean()*100
    k_mean = stat(kept); f_mean = stat(filt)
    print(f"conc ≤ {thr:<7}{len(kept):>8}"
          f"{f'{k_mean[0]:+.2f}%' if isinstance(k_mean,tuple) else 'n=0':>17}"
          f"{f'{k_mean[1]:.0f}%' if isinstance(k_mean,tuple) else '':>11}"
          f"{len(filt):>8}"
          f"{f'{f_mean[0]:+.2f}%' if isinstance(f_mean,tuple) else 'n=0':>17}"
          f"{f'{f_mean[1]:.0f}%' if isinstance(f_mean,tuple) else '':>11}")

print("\nINTERPRETATION:")
print("  - 'KEPT' = fires that pass concentration check → gate still blocks downgrade")
print("    We want KEPT to have HIGH T+20 mean (gate correctly held us in bull)")
print("  - 'FILT' = fires blocked by conc check → let v3.1 downgrade through")
print("    We want FILT to have LOW or NEGATIVE T+20 mean (downgrades were right)")
