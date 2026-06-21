# -*- coding: utf-8 -*-
"""
diagnose_bull_regime_v2.py
==========================
v2 BTC definitions — price/return based instead of state-based.

The state-based BTC_A* from v1 failed because v3.1 state oscillates too
much (even 2021 super-bull never stayed BULL+ for 60 consecutive days).

NEW definitions reflect what user means by "true bull trend" — *price* and
*return* persistence, not state oscillation:

  BTC_P30  : VNI/MA200 > 1.05 for ≥ 30 consecutive days
  BTC_P60  : ditto ≥ 60 days
  BTC_P90  : ditto ≥ 90 days
  BTC_R6M  : VNI 6-month return > 15% AND VNI > MA200
  BTC_R3M  : VNI 3-month return > 8% AND VNI > MA200
  BTC_S60  : state ≥ NEUTRAL for ≥ 60 days AND state hit BULL+ at least once
  BTC_RP   : combined — (P60 AND R6M) — strictest, "clearly bull"
  BTC_RP_loose : (P30 OR R3M)  — broader confirmation
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

v31 = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dr  = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
diag = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])
df = v31.merge(dr[["time","Close","concentration_smooth","alpha","r_score_raw","r_score_ew"]],
               on="time", how="left").merge(
    diag[["time","spx_dd_1y","vix","us_cap","override_fired"]], on="time", how="left").reset_index(drop=True)
n = len(df); close = df["Close"].values; state = df["state"].values.astype(int)

# Compute MA200 + returns
df["ma200"]     = pd.Series(close).rolling(200).mean()
df["ma200_dev"] = close / df["ma200"] - 1
df["ret_60d"]   = pd.Series(close).pct_change(60)
df["ret_120d"]  = pd.Series(close).pct_change(120)

# RSI(14)
def rsi14(c):
    delta = np.diff(c, prepend=c[0])
    up   = np.where(delta>0, delta, 0.0); down = np.where(delta<0, -delta, 0.0)
    out = np.full(len(c), np.nan)
    for i in range(14, len(c)):
        gain = up[i-13:i+1].mean(); loss = down[i-13:i+1].mean()
        rs = gain/loss if loss>0 else 100; out[i] = 100 - 100/(1+rs)
    return out
df["rsi14"] = rsi14(close)

# Consecutive day counters
def consec(mask_arr):
    out = np.zeros(len(mask_arr), dtype=int)
    for t in range(len(mask_arr)):
        if mask_arr[t]: out[t] = (out[t-1] + 1) if t > 0 else 1
        else: out[t] = 0
    return out

# Price above MA200 by 5% (sustained)
p_above_5 = (df["ma200_dev"] > 0.05).fillna(False).astype(int).values
df["consec_p5"] = consec(p_above_5)

# State ≥ NEUTRAL
s_neutral = (state >= 3).astype(int)
df["consec_neutral"] = consec(s_neutral)

# State has hit BULL+ in last N days (rolling max)
df["max_state_60d"] = pd.Series(state).rolling(60, min_periods=1).max()

# Definitions
df["BTC_P30"]  = df["consec_p5"] >= 30
df["BTC_P60"]  = df["consec_p5"] >= 60
df["BTC_P90"]  = df["consec_p5"] >= 90
df["BTC_R6M"]  = ((df["ret_120d"] > 0.15) & (df["ma200_dev"] > 0)).fillna(False)
df["BTC_R3M"]  = ((df["ret_60d"]  > 0.08) & (df["ma200_dev"] > 0)).fillna(False)
df["BTC_S60"]  = (df["consec_neutral"] >= 60) & (df["max_state_60d"] >= 4)
df["BTC_RP"]   = df["BTC_P60"] & df["BTC_R6M"]
df["BTC_RP_loose"] = df["BTC_P30"] | df["BTC_R3M"]

BTC_NAMES = ["BTC_P30","BTC_P60","BTC_P90","BTC_R6M","BTC_R3M","BTC_S60","BTC_RP","BTC_RP_loose"]

# ── Coverage stats ───────────────────────────────────────────────────
print("="*100); print("BULL REGIME COVERAGE (v2 — price/return based)"); print("="*100)
print(f"{'Definition':<14}{'All era':>10}{'2014-26':>10}{'2014-19':>10}{'2020-26':>10}{'2021-22':>10}")
mask_post14 = df["time"] >= "2014-01-01"
mask_1419   = (df["time"] >= "2014-01-01") & (df["time"] <= "2019-12-31")
mask_2026   = df["time"] >= "2020-01-01"
mask_2122   = (df["time"] >= "2021-01-01") & (df["time"] <= "2022-12-31")
for nm in BTC_NAMES:
    pct = lambda mask: df.loc[mask, nm].mean()*100
    print(f"{nm:<14}{pct(df['time']>=df['time'].iloc[0]):>9.1f}%{pct(mask_post14):>9.1f}%"
          f"{pct(mask_1419):>9.1f}%{pct(mask_2026):>9.1f}%{pct(mask_2122):>9.1f}%")

# ── List 5 longest bull regime windows for BTC_P30 + BTC_S60 ─────────
print(f"\n=== Longest bull regime windows (post-2014, BTC_P30) ===")
def find_windows(mask_col, start_ts):
    in_r = False; start_i = None; ws = []
    for t in range(n):
        if df["time"].iloc[t] < start_ts: continue
        v = df[mask_col].iloc[t]
        if v and not in_r: in_r = True; start_i = t
        elif (not v) and in_r:
            in_r = False
            ws.append((df["time"].iloc[start_i], df["time"].iloc[t-1], t-start_i))
    if in_r: ws.append((df["time"].iloc[start_i], df["time"].iloc[n-1], n-start_i))
    return ws

for col in ["BTC_P30", "BTC_S60", "BTC_RP", "BTC_RP_loose"]:
    ws = find_windows(col, pd.Timestamp("2014-01-01"))
    ws = sorted(ws, key=lambda x: x[2], reverse=True)[:8]
    print(f"\n  {col}  (top 8 longest):")
    for s, e, d in ws:
        print(f"    {s.date().isoformat()} → {e.date().isoformat()}  ({d}d)")

# ── (1) US override fires IN vs OUT bull regime ──────────────────────
print(f"\n" + "="*100); print("(1) US OVERRIDE fires — IN vs OUT bull regime"); print("="*100)
fire_days = df[df["override_fired"]==True].copy()
fire_days = fire_days[fire_days["time"] >= "2014-01-01"]
fire_days["i"] = fire_days.index
def fwd_ret(i, h):
    if i+h >= n: return None
    return close[i+h]/close[i] - 1
fire_days["r5"]  = fire_days["i"].apply(lambda i: fwd_ret(i, 5))
fire_days["r20"] = fire_days["i"].apply(lambda i: fwd_ret(i, 20))
fire_days["r60"] = fire_days["i"].apply(lambda i: fwd_ret(i, 60))

print(f"Total US override fires post-2014: {len(fire_days)}")
print(f"\n{'Definition':<14}{'IN n':>6}{'IN T+20':>10}{'IN T+60':>10}{'  '}{'OUT n':>6}{'OUT T+20':>11}{'OUT T+60':>11}")
print("-"*92)
for btc_def in ["BTC_P30","BTC_P60","BTC_R6M","BTC_RP","BTC_RP_loose"]:
    in_r  = fire_days[fire_days[btc_def]==True]
    out_r = fire_days[fire_days[btc_def]==False]
    if len(in_r) == 0:
        print(f"{btc_def:<14}{'0':>6}{'—':>10}{'—':>10}  {len(out_r):>6}"); continue
    def s(rs):
        a = np.array([x for x in rs if x is not None])
        if len(a)==0: return None
        return f"{a.mean()*100:+5.2f}% ({(a>0).mean()*100:.0f}%pos)"
    in_t20 = s(in_r["r20"]); in_t60 = s(in_r["r60"])
    out_t20 = s(out_r["r20"]); out_t60 = s(out_r["r60"])
    print(f"{btc_def:<14}{len(in_r):>6}{in_t20:>10}{in_t60:>10}  "
          f"{len(out_r):>6}{out_t20:>11}{out_t60:>11}")

# US override "hurt during bull" test: in bull regime, market should keep rising despite US scary
# If IN-bull fires have positive r20/r60 mean → market ignored US news (filter hurts portfolio)
print("\n  Interpretation: IN-bull fires with POSITIVE mean = US-override was wrong to downgrade")
print("                  (market kept rising; override caused unnecessary derisking)")

# ── (2) RSI gate fires IN vs OUT bull regime ─────────────────────────
print(f"\n" + "="*100); print("(2) RSI GATE fires — HELP rate IN vs OUT bull regime"); print("="*100)
v31_state = df["state"].values
rsi = df["rsi14"].values; conc = df["concentration_smooth"].values
gate_fires = []
blocked = False; blocked_at = None
for t in range(1, n):
    if df["time"].iloc[t] < pd.Timestamp("2014-01-01"): continue
    cur = v31_state[t]; prev = v31_state[t-1]; cr = rsi[t]
    if blocked:
        if (cr is None) or np.isnan(cr) or (cr < 55): blocked=False
        elif cur >= blocked_at: blocked=False
        elif (blocked_at - cur) >= 2: blocked=False
    else:
        if (prev - cur == 1) and (cr is not None) and (not np.isnan(cr)) and (cr >= 55):
            blocked = True; blocked_at = prev
            row = {"i": t, "date": df["time"].iloc[t], "rsi": cr,
                   "conc": conc[t] if not pd.isna(conc[t]) else None,
                   "r5": fwd_ret(t,5), "r20": fwd_ret(t,20), "r60": fwd_ret(t,60)}
            for nm in BTC_NAMES: row[nm] = bool(df[nm].iloc[t])
            gate_fires.append(row)
print(f"Gate fires post-2014: {len(gate_fires)}")
for btc_def in ["BTC_P30","BTC_P60","BTC_R6M","BTC_RP_loose","BTC_S60"]:
    in_r  = [g for g in gate_fires if g[btc_def] and g["r20"] is not None]
    out_r = [g for g in gate_fires if not g[btc_def] and g["r20"] is not None]
    def hr(rs, k="r20"):
        a = [r[k] for r in rs if r[k] is not None]
        if not a: return "n=0"
        return f"n={len(a)} mean {np.mean(a)*100:+5.2f}% HELP={(np.array(a)>0).mean()*100:.0f}%"
    print(f"  {btc_def:<14}  IN: {hr(in_r,'r20')}   OUT: {hr(out_r,'r20')}")

# Detailed list of gate fires with all BTCs flagged
print(f"\n--- All 19 gate fires with all BTC flags ---")
hdr = f"{'Date':<12}{'RSI':>5}{'Conc':>7}{'T+20':>9}"
for nm in ["BTC_P30","BTC_P60","BTC_R6M","BTC_S60","BTC_RP_loose"]: hdr += f"{nm:>13}"
print(hdr)
for g in gate_fires:
    r20s = f"{g['r20']*100:+.1f}%" if g['r20'] is not None else "?"
    conc_s = f"{g['conc']:.2f}" if g['conc'] is not None else "N/A"
    line = f"{g['date'].date().isoformat():<12}{g['rsi']:>4.0f}{conc_s:>7}{r20s:>8}"
    for nm in ["BTC_P30","BTC_P60","BTC_R6M","BTC_S60","BTC_RP_loose"]:
        line += f"{('YES' if g[nm] else '—'):>13}"
    print(line)
