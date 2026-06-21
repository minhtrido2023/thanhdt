# -*- coding: utf-8 -*-
"""
diagnose_bull_regime.py
=======================
Define "true bull regime" and test whether conservative filters lose
predictive power inside it (user's hypothesis 2026-05-21).

Definitions tested (BTC = Bull Trend Confirmed):
  BTC_A30  : state ∈ {BULL,EX-BULL} continuously ≥ 30 sessions
  BTC_A60  : ditto ≥ 60 sessions
  BTC_A90  : ditto ≥ 90 sessions
  BTC_A120 : ditto ≥ 120 sessions
  BTC_B    : state ≥ BULL ≥ 30d AND VNI/MA200 > 1.10 ≥ 30d
  BTC_C    : state ≥ BULL ≥ 30d AND VNI/VNI[-60d] > 1.15 (6m return > 15%)
  BTC_D    : (BTC_A60 OR BTC_B) — union, broader confirmation

For each filter activation in v3.1/v3.3b history, classify as:
  • IN-REGIME  (BTC=True at trigger)
  • OUT-REGIME (BTC=False at trigger)

Then compare T+20/T+60 forward outcomes between IN vs OUT.
If IN-regime activations have systematically worse outcomes (filter hurts
during true bull), → confirms hypothesis → v3.4 should disable filter when
BTC is on.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ── Load all needed series ─────────────────────────────────────────────
v31 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_full_history.csv"))
v31["time"] = pd.to_datetime(v31["time"]); v31 = v31.sort_values("time").reset_index(drop=True)
dr  = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_dual_v3_full.csv"))
dr["time"] = pd.to_datetime(dr["time"])
diag = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_1_diag.csv"))
diag["time"] = pd.to_datetime(diag["time"])

df = v31.merge(dr[["time","Close","concentration_smooth","alpha","r_score_raw","r_score_ew"]],
               on="time", how="left").merge(
    diag[["time","spx_dd_1y","vix","us_cap","override_fired"]], on="time", how="left").reset_index(drop=True)
df["r_dual"] = df["alpha"]*df["r_score_raw"] + (1-df["alpha"])*df["r_score_ew"]

n = len(df); close = df["Close"].values
state = df["state"].values.astype(int)

# Compute MA200, MA50, 60d return
df["ma200"] = pd.Series(close).rolling(200).mean()
df["ma50"]  = pd.Series(close).rolling(50).mean()
df["ma200_dev"] = close / df["ma200"] - 1
df["ret_60d"]   = pd.Series(close).pct_change(60)

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

# ── Compute BTC indicators ────────────────────────────────────────────
# Count consecutive days in {BULL, EX-BULL}
is_bull = (state >= 4).astype(int)
consec_bull = np.zeros(n, dtype=int)
for t in range(n):
    if is_bull[t] == 0: consec_bull[t] = 0
    else: consec_bull[t] = (consec_bull[t-1] + 1) if t > 0 else 1

# Count consecutive days MA200_dev > 0.10
m200_above = ((df["ma200_dev"] > 0.10).fillna(False)).astype(int).values
consec_m200 = np.zeros(n, dtype=int)
for t in range(n):
    if m200_above[t] == 0: consec_m200[t] = 0
    else: consec_m200[t] = (consec_m200[t-1] + 1) if t > 0 else 1

df["consec_bull"] = consec_bull
df["consec_m200"] = consec_m200

# BTC definitions
df["BTC_A30"]  = (consec_bull >= 30)
df["BTC_A60"]  = (consec_bull >= 60)
df["BTC_A90"]  = (consec_bull >= 90)
df["BTC_A120"] = (consec_bull >= 120)
df["BTC_B"]    = (consec_bull >= 30) & (consec_m200 >= 30)
ret_60_ok = (df["ret_60d"] > 0.15).fillna(False)
df["BTC_C"]    = (consec_bull >= 30) & ret_60_ok
df["BTC_D"]    = df["BTC_A60"] | df["BTC_B"]

BTC_NAMES = ["BTC_A30","BTC_A60","BTC_A90","BTC_A120","BTC_B","BTC_C","BTC_D"]

# ── Distribution ──────────────────────────────────────────────────────
print("="*100); print("BULL REGIME COVERAGE (% of sessions where BTC=True)"); print("="*100)
print(f"{'Definition':<12}{'All era':>10}{'2014-26':>10}{'2014-19':>10}{'2020-26':>10}")
mask_post14 = df["time"] >= "2014-01-01"
mask_1419   = (df["time"] >= "2014-01-01") & (df["time"] <= "2019-12-31")
mask_2026   = df["time"] >= "2020-01-01"
for nm in BTC_NAMES:
    pct = lambda mask: df.loc[mask, nm].mean()*100
    print(f"{nm:<12}{pct(df['time']>=df['time'].iloc[0]):>9.1f}%{pct(mask_post14):>9.1f}%"
          f"{pct(mask_1419):>9.1f}%{pct(mask_2026):>9.1f}%")

# ── List bull regime windows for BTC_A60 (most interpretable) ─────────
print(f"\n=== Bull regime windows (BTC_A60) post-2014 ===")
btc = df["BTC_A60"].values
in_regime = False; start_i = None; windows = []
for t in range(n):
    if df["time"].iloc[t] < pd.Timestamp("2014-01-01"): continue
    if btc[t] and not in_regime:
        in_regime = True; start_i = t
    elif not btc[t] and in_regime:
        in_regime = False
        windows.append((df["time"].iloc[start_i], df["time"].iloc[t-1], t-1-start_i+1))
if in_regime:
    windows.append((df["time"].iloc[start_i], df["time"].iloc[n-1], n-start_i))

print(f"{'Start':<12}{'End':<12}{'Duration':>10}")
for s, e, d in windows:
    print(f"{s.date().isoformat():<12}{e.date().isoformat():<12}{d:>9}d")

# ── Now: test whether US override fires hurt during bull regime ───────
print(f"\n" + "="*100)
print("(1) US OVERRIDE fires — IN vs OUT bull regime (BTC_A60)")
print("="*100)
print("(Hypothesis: fires during bull regime are noise — VN ignores US news in bull)")

# Find US override fire days
fire_days = df[df["override_fired"]==True].copy()
fire_days = fire_days[fire_days["time"] >= "2014-01-01"]  # only V11 era
print(f"Total US override fires post-2014: {len(fire_days)}")

# For each fire day, compute T+5/T+20/T+60 fwd VNI return
def fwd_ret(i, h):
    if i+h >= n: return None
    return close[i+h]/close[i] - 1

fire_days["i"] = fire_days.index
fire_days["r5"]  = fire_days["i"].apply(lambda i: fwd_ret(i, 5))
fire_days["r20"] = fire_days["i"].apply(lambda i: fwd_ret(i, 20))
fire_days["r60"] = fire_days["i"].apply(lambda i: fwd_ret(i, 60))

def stats(rs):
    r = np.array(rs); r = r[~pd.isna(r)]
    if len(r)==0: return None
    return dict(n=len(r), mean=r.mean()*100, median=np.median(r)*100,
                pos=(r>0).mean()*100)

for btc_def in ["BTC_A30","BTC_A60","BTC_A90","BTC_D"]:
    in_r  = fire_days[fire_days[btc_def]==True]
    out_r = fire_days[fire_days[btc_def]==False]
    print(f"\n  --- {btc_def} ---")
    for h, col in [(5,"r5"),(20,"r20"),(60,"r60")]:
        s_in = stats(in_r[col]); s_out = stats(out_r[col])
        if s_in and s_out:
            print(f"    T+{h:>2}  IN-bull n={s_in['n']:>3} mean={s_in['mean']:+5.2f}% %pos={s_in['pos']:>4.0f}%   "
                  f"OUT n={s_out['n']:>3} mean={s_out['mean']:+5.2f}% %pos={s_out['pos']:>4.0f}%")

# ── (2) Conc filter blocks: where would v3.3b block downgrades AND BTC is on?
print(f"\n" + "="*100)
print("(2) CONC FILTER blocks (>0.55) — when does the filter activate during bull regime?")
print("="*100)
print("(Filter blocks v3.3b RSI gate when conc>0.55 → lets downgrade through. Is this right?)")

# Need to find days where v3.1 fired 1-step downgrade AND RSI≥55 AND conc>0.55
# These are the 5 gate fires that v3.3b BLOCKED (filtered out) vs v3.3 (no conc filter)
v31_state = df["state"].values
rsi = df["rsi14"].values; conc = df["concentration_smooth"].values

fired_conc_blocks = []
for t in range(1, n):
    if df["time"].iloc[t] < pd.Timestamp("2014-01-01"): continue
    cur = v31_state[t]; prev = v31_state[t-1]
    is_1step_dn = (prev - cur == 1)
    rsi_ok = (rsi[t] is not None) and (not np.isnan(rsi[t])) and (rsi[t] >= 55)
    conc_high = (conc[t] is not None) and (not np.isnan(conc[t])) and (conc[t] > 0.55)
    if is_1step_dn and rsi_ok and conc_high:
        fired_conc_blocks.append({
            "i": t, "date": df["time"].iloc[t],
            "from": STATE_NAMES[prev], "to": STATE_NAMES[cur],
            "rsi": rsi[t], "conc": conc[t],
            "r20": fwd_ret(t,20), "r60": fwd_ret(t,60),
            "BTC_A30": df["BTC_A30"].iloc[t], "BTC_A60": df["BTC_A60"].iloc[t],
            "BTC_A90": df["BTC_A90"].iloc[t], "BTC_D": df["BTC_D"].iloc[t],
        })

print(f"\nConc filter blocks (post-2014): {len(fired_conc_blocks)}")
for f in fired_conc_blocks:
    btc_str = " ".join([k for k in ["BTC_A30","BTC_A60","BTC_A90"] if f[k]])
    if not btc_str: btc_str = "—"
    r20 = f"{f['r20']*100:+.1f}%" if f['r20'] is not None else "?"
    r60 = f"{f['r60']*100:+.1f}%" if f['r60'] is not None else "?"
    # gate was BLOCKED → v3.1 downgrade was let through → outcome = did v3.1 do right thing?
    # For v3.1 downgrade: T+20 negative = downgrade was right = filter was right to let through
    verdict_v31 = "✓ DOWNGRADE OK (market fell)" if f['r20'] is not None and f['r20']<0 else "✗ DOWNGRADE WRONG (market rose)"
    print(f"  {f['date'].date()} {f['from']}→{f['to']}  RSI={f['rsi']:.0f} conc={f['conc']:.2f}  "
          f"T+20={r20} T+60={r60}  bull?[{btc_str}]  {verdict_v31}")

# ── (3) RSI gate fires post-2014: do they help or hurt depending on BTC?
print(f"\n" + "="*100)
print("(3) RSI GATE fires (v3.3) — held vs let-through, IN vs OUT bull regime")
print("="*100)

# RSI gate fires WITHOUT conc filter (= v3.3 base fires)
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
            gate_fires.append({
                "i": t, "date": df["time"].iloc[t],
                "rsi": cr, "conc": conc[t] if not pd.isna(conc[t]) else None,
                "r5": fwd_ret(t,5), "r20": fwd_ret(t,20), "r60": fwd_ret(t,60),
                "BTC_A30": df["BTC_A30"].iloc[t], "BTC_A60": df["BTC_A60"].iloc[t],
                "BTC_A90": df["BTC_A90"].iloc[t], "BTC_D": df["BTC_D"].iloc[t],
                "BTC_A120": df["BTC_A120"].iloc[t],
            })

print(f"\nGate fires post-2014: {len(gate_fires)}")
# For RSI gate fire: HELP if T+20 r > 0 (gate correctly held us in bull)
for btc_def in ["BTC_A30","BTC_A60","BTC_A90","BTC_A120","BTC_D"]:
    in_r  = [g for g in gate_fires if g[btc_def] and g["r20"] is not None]
    out_r = [g for g in gate_fires if not g[btc_def] and g["r20"] is not None]
    print(f"\n  --- {btc_def} ---")
    for label, rows in [("IN-bull", in_r), ("OUT-bull", out_r)]:
        if not rows: continue
        for h in [5,20,60]:
            rs = [r[f"r{h}"] for r in rows if r[f"r{h}"] is not None]
            if not rs: continue
            rs = np.array(rs)
            print(f"    {label:<10} T+{h:>2}: n={len(rs):>2} mean={rs.mean()*100:+5.2f}% "
                  f"%pos={(rs>0).mean()*100:>4.0f}%  → HELP rate={(rs>0).mean()*100:.0f}%")

print(f"\n--- Detail of gate fires by BTC_A60 ---")
print(f"{'Date':<12}{'RSI':>5}{'Conc':>7}{'T+20':>9}{'T+60':>9}{'BTC_A60':>10}{'HELP?':>9}")
for g in gate_fires:
    r20s = f"{g['r20']*100:+.1f}%" if g['r20'] is not None else "?"
    r60s = f"{g['r60']*100:+.1f}%" if g['r60'] is not None else "?"
    conc_s = f"{g['conc']:.2f}" if g['conc'] is not None else "N/A"
    help_str = "✓" if g['r20'] is not None and g['r20']>0 else "✗"
    print(f"{g['date'].date().isoformat():<12}{g['rsi']:>4.0f}{conc_s:>7}"
          f"{r20s:>8}{r60s:>9}{'YES' if g['BTC_A60'] else 'NO':>10}{help_str:>9}")
