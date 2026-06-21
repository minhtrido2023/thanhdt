# -*- coding: utf-8 -*-
"""
sweep_window.py
===============
Sweep MODE_WIN (smoothing window) từ 3 → 40 ngày để tìm tham số tối ưu.
Metrics: Sharpe, CAGR, MaxDD, Calmar, số transitions, min-dur, avg-dur, trades/yr.
Output: bảng console + sweep_window_results.html
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os, copy
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ══════════════════════════════════════════════════════════════════════
# THAM SỐ GỐC (giữ nguyên, chỉ sweep MODE_WIN)
# ══════════════════════════════════════════════════════════════════════
W_BASE      = {"P3M": 0.30, "P1M": 0.10, "MA200": 0.15,
               "RSI": 0.15, "MACD": 0.10, "CMF": 0.08, "Breadth": 0.12}
MIN_LB      = 252
MIN_FACTORS = 3
RAMP_DAYS   = 3
SNAP_THR    = 0.03
TC          = 0.001
DEPOSIT_R   = 0.06 / 252
BORROW_R    = 0.10 / 252
TARGET_W    = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

# ── LOAD DATA ─────────────────────────────────────────────────────────
print("Loading VNINDEX.csv ...")
vni = pd.read_csv(os.path.join(WORKDIR, "VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)

cal_days_total  = (vni["time"].iloc[-1] - vni["time"].iloc[0]).days
sessions_per_year = len(vni) / (cal_days_total / 365.25) if cal_days_total > 0 else 252
print(f"  {len(vni)} sessions | {cal_days_total/365.25:.1f} yr | {sessions_per_year:.1f} sess/yr")

for col in ["Open", "High", "Low", "Close", "Volume", "VNINDEX_PE"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

# Breadth (optional)
breadth_path = os.path.join(WORKDIR, "breadth_data.csv")
if os.path.exists(breadth_path):
    breadth = pd.read_csv(breadth_path)
    breadth["time"] = pd.to_datetime(breadth["time"])
    breadth["breadth"] = pd.to_numeric(breadth["breadth"], errors="coerce")
    vni = vni.merge(breadth, on="time", how="left")
else:
    vni["breadth"] = np.nan

close = vni["Close"].values.copy()
high  = vni["High"].values.copy()
low   = vni["Low"].values.copy()
vol   = vni["Volume"].values.copy()
n     = len(close)

# ══════════════════════════════════════════════════════════════════════
# COMPUTE INDICATORS (một lần)
# ══════════════════════════════════════════════════════════════════════
print("Computing indicators ...")

# P3M: Change_3M từ CSV (calendar-correct)
p3m = np.full(n, np.nan)
if "Change_3M" in vni.columns:
    p3m_csv = pd.to_numeric(vni["Change_3M"], errors="coerce").values
    for i in range(n):
        if not np.isnan(p3m_csv[i]):
            p3m[i] = p3m_csv[i]
        elif i >= 60 and close[i-60] > 0:
            p3m[i] = close[i] / close[i-60] - 1
else:
    for i in range(60, n):
        if close[i-60] > 0:
            p3m[i] = close[i] / close[i-60] - 1

# P1M
p1m = np.full(n, np.nan)
if "Change_1M" in vni.columns:
    p1m_csv = pd.to_numeric(vni["Change_1M"], errors="coerce").values
    for i in range(n):
        if not np.isnan(p1m_csv[i]):
            p1m[i] = p1m_csv[i]
        elif i >= 20 and close[i-20] > 0:
            p1m[i] = close[i] / close[i-20] - 1
else:
    for i in range(20, n):
        if close[i-20] > 0:
            p1m[i] = close[i] / close[i-20] - 1

# MA200 dev
ma200 = pd.Series(close).rolling(200, min_periods=200).mean().values
ma200_dev = np.where((ma200 > 0) & ~np.isnan(ma200), close / ma200 - 1, np.nan)

# RSI
rsi = np.full(n, np.nan)
avg_u = avg_d = np.nan
period = 14
for i in range(1, n):
    diff = close[i] - close[i-1]
    u = max(diff, 0.0); d = max(-diff, 0.0)
    if np.isnan(avg_u):
        if i >= period:
            gains  = [max(close[j]-close[j-1],0) for j in range(1, period+1)]
            losses = [max(close[j-1]-close[j],0) for j in range(1, period+1)]
            avg_u  = np.mean(gains); avg_d = np.mean(losses)
            if (avg_u + avg_d) > 0:
                rsi[i] = avg_u / (avg_u + avg_d)
    else:
        avg_u = (avg_u*(period-1)+u)/period
        avg_d = (avg_d*(period-1)+d)/period
        if (avg_u + avg_d) > 0:
            rsi[i] = avg_u / (avg_u + avg_d)

# MACD
ema12 = np.full(n, np.nan); ema26 = np.full(n, np.nan)
signal = np.full(n, np.nan); macd_hist = np.full(n, np.nan)
k12=2/13; k26=2/27; k9=2/10
for i in range(n):
    ema12[i] = close[i] if (i==0 or np.isnan(ema12[i-1])) else ema12[i-1]*(1-k12)+close[i]*k12
    ema26[i] = close[i] if (i==0 or np.isnan(ema26[i-1])) else ema26[i-1]*(1-k26)+close[i]*k26
    ml = ema12[i]-ema26[i]
    signal[i] = ml if (i==0 or np.isnan(signal[i-1])) else signal[i-1]*(1-k9)+ml*k9
    if i >= 33: macd_hist[i] = ml - signal[i]

# CMF
hl_range = high - low
mfm = np.where(hl_range > 0, ((close-low)-(high-close))/hl_range, 0.0)
mfv = mfm * vol
cmf = np.full(n, np.nan)
for i in range(14, n):
    v_sum = np.sum(vol[i-14:i])
    if v_sum > 0: cmf[i] = np.sum(mfv[i-14:i]) / v_sum

vni["f_P3M"]    = p3m
vni["f_P1M"]    = p1m
vni["f_MA200"]  = ma200_dev
vni["f_RSI"]    = rsi
vni["f_MACD"]   = macd_hist
vni["f_CMF"]    = cmf
vni["f_Breadth"]= vni["breadth"].values

# ── EXPANDING RANK ────────────────────────────────────────────────────
def expanding_pct_rank(arr, min_lb=252):
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb or np.isnan(arr[t]): continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

print("Computing ranks (slow) ...")
FACTOR_KEYS = ["P3M","P1M","MA200","RSI","MACD","CMF","Breadth"]
ranks = {}
for k in FACTOR_KEYS:
    print(f"  {k} ...", end=" ", flush=True)
    ranks[k] = expanding_pct_rank(vni[f"f_{k}"].values, MIN_LB)
    print("ok")

# ── COMPOSITE SCORE ───────────────────────────────────────────────────
score = np.full(n, np.nan)
for t in range(n):
    avail = {k: ranks[k][t] for k in FACTOR_KEYS if not np.isnan(ranks[k][t])}
    if len(avail) < MIN_FACTORS: continue
    w_sum = sum(W_BASE[k] for k in avail)
    score[t] = sum(avail[k]*W_BASE[k] for k in avail) / w_sum

r_score = expanding_pct_rank(score, MIN_LB)

# ── CLASSIFY RAW STATE ────────────────────────────────────────────────
def classify_raw(rs):
    if np.isnan(rs): return 3
    if rs < 0.10: return 1
    elif rs < 0.20: return 2
    elif rs < 0.70: return 3
    elif rs < 0.90: return 4
    else: return 5

state_raw = np.array([classify_raw(r) for r in r_score])

# ── RISK OVERRIDES ────────────────────────────────────────────────────
pe_arr = vni["VNINDEX_PE"].values.copy()
pe_p90 = np.full(n, np.nan)
for t in range(n):
    hist = pe_arr[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: pe_p90[t] = np.nanpercentile(valid, 90)

running_max = np.maximum.accumulate(np.where(np.isnan(close), 0, close))
dd = np.where(running_max > 0, close/running_max-1, 0.0)

daily_ret = np.full(n, np.nan)
for i in range(1, n):
    if close[i-1] > 0: daily_ret[i] = close[i]/close[i-1]-1
vol20 = np.full(n, np.nan)
for i in range(20, n):
    w2 = daily_ret[i-20:i]; vv = w2[~np.isnan(w2)]
    if len(vv) >= 15: vol20[i] = np.std(vv)*np.sqrt(sessions_per_year)
avg_vol_exp = np.full(n, np.nan)
for t in range(n):
    hist = vol20[:t+1]; valid = hist[~np.isnan(hist)]
    if len(valid) >= 60: avg_vol_exp[t] = np.mean(valid)

state_after_override = state_raw.copy()
for i in range(n):
    s = state_after_override[i]
    if (not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i])
            and pe_arr[i] > pe_p90[i] and s == 5): s = 4
    if dd[i] < -0.25 and s >= 4: s = 3
    if (not np.isnan(avg_vol_exp[i]) and not np.isnan(vol20[i])
            and vol20[i] > 1.5*avg_vol_exp[i] and s == 5): s = 4
    state_after_override[i] = s

print("Base computation done.")

# ══════════════════════════════════════════════════════════════════════
# SWEEP FUNCTION
# ══════════════════════════════════════════════════════════════════════
dates = vni["time"].reset_index(drop=True)

def rolling_mode(states, window):
    out = states.copy()
    for t in range(window-1, len(states)):
        wv = states[t-window+1:t+1]
        vals, counts = np.unique(wv, return_counts=True)
        mc = counts.max()
        candidates = vals[counts == mc]
        for v in reversed(wv):
            if v in candidates:
                out[t] = v; break
    return out

def calc_metrics(pv_arr, dates_s):
    valid = [(t, pv_arr[t]) for t in range(len(pv_arr)) if pv_arr[t] > 0]
    if len(valid) < 2: return {}
    idx0, v0 = valid[0]; idx1, v1 = valid[-1]
    cal_years = (dates_s.iloc[idx1]-dates_s.iloc[idx0]).days/365.25
    cagr = (v1/v0)**(1/cal_years)-1 if cal_years > 0 else 0
    rets = np.array([pv_arr[i]/pv_arr[i-1]-1 for i in range(1,len(pv_arr)) if pv_arr[i-1]>0])
    n_sub = idx1-idx0
    spy = n_sub/cal_years if cal_years > 0 else sessions_per_year
    sharpe = (np.mean(rets)*spy)/(np.std(rets)*np.sqrt(spy)) if np.std(rets)>0 else 0
    rm = np.maximum.accumulate(pv_arr)
    dd_arr = np.where(rm>0, pv_arr/rm-1, 0)
    mdd = dd_arr.min()
    calmar = cagr/abs(mdd) if mdd!=0 else 0
    return {"cagr":cagr,"sharpe":sharpe,"max_dd":mdd,"calmar":calmar}

def transition_stats(state_arr, dates_s):
    """Thống kê các lần chuyển trạng thái."""
    durations = []
    n_total = 0
    n_short1 = 0   # < 2 ngày
    n_short5 = 0   # < 5 ngày
    n_short10 = 0  # < 10 ngày
    prev_s = state_arr[0]; prev_date = dates_s.iloc[0]
    for i in range(1, len(state_arr)):
        if state_arr[i] != prev_s:
            dur = (dates_s.iloc[i] - prev_date).days
            durations.append(dur)
            n_total += 1
            if dur <= 1:  n_short1 += 1
            if dur <= 5:  n_short5 += 1
            if dur <= 10: n_short10 += 1
            prev_s = state_arr[i]; prev_date = dates_s.iloc[i]
    avg_dur = np.mean(durations) if durations else 0
    min_dur = min(durations) if durations else 0
    return {"n_trans": n_total, "n_short1": n_short1, "n_short5": n_short5,
            "n_short10": n_short10, "avg_dur": avg_dur, "min_dur": min_dur}

def run_backtest(state_smooth):
    pv = np.zeros(n); pv[0] = 1_000_000_000.0
    w  = TARGET_W[3]; w_arr = np.zeros(n); w_arr[0] = w
    for t in range(1, n):
        target = TARGET_W[state_smooth[t-1]]
        diff   = target - w
        w_new  = target if abs(diff) < SNAP_THR else w + diff/RAMP_DAYS
        w_new  = float(np.clip(w_new, 0.0, 1.30))
        r      = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        cash_r = max(0.0, 1.0-w_new)*DEPOSIT_R
        marg_c = max(0.0, w_new-1.0)*BORROW_R
        trd_c  = abs(w_new-w)*TC
        pv[t]  = pv[t-1]*(1.0+w_new*r+cash_r-marg_c-trd_c)
        w = w_new; w_arr[t] = w
    return pv

# ── WINDOWS TO SWEEP ─────────────────────────────────────────────────
windows = [3, 5, 7, 10, 12, 15, 18, 20, 25, 30, 40]

# ── B&H baseline ─────────────────────────────────────────────────────
pv_bh = np.zeros(n); pv_bh[0] = 1_000_000_000.0
for t in range(1, n):
    pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1]) if close[t-1]>0 else pv_bh[t-1]
m_bh = calc_metrics(pv_bh, dates)

# Since 2016 B&H
idx_2016 = vni[vni["time"] >= "2016-01-01"].index[0]
m_bh_16  = calc_metrics(pv_bh[idx_2016:], dates.iloc[idx_2016:].reset_index(drop=True))

print(f"\nB&H baseline: CAGR={m_bh['cagr']:.1%} | Sharpe={m_bh['sharpe']:.2f} | MaxDD={m_bh['max_dd']:.1%}")
print(f"B&H 2016+  : CAGR={m_bh_16['cagr']:.1%} | Sharpe={m_bh_16['sharpe']:.2f} | MaxDD={m_bh_16['max_dd']:.1%}")

# ══════════════════════════════════════════════════════════════════════
# RUN SWEEP
# ══════════════════════════════════════════════════════════════════════
print(f"\n{'─'*130}")
print(f"{'Win':>4} │ {'CAGR':>6} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} │"
      f" {'CAGR16':>6} {'Shrp16':>7} │"
      f" {'Trans':>6} {'1d':>4} {'≤5d':>5} {'≤10d':>6} {'AvgDur':>7} {'MinDur':>7}")
print(f"{'─'*130}")

results = []
for win in windows:
    st_smooth = rolling_mode(state_after_override, win)
    pv        = run_backtest(st_smooth)
    m         = calc_metrics(pv, dates)
    m16       = calc_metrics(pv[idx_2016:], dates.iloc[idx_2016:].reset_index(drop=True))
    ts        = transition_stats(st_smooth, dates)

    row = {"win": win, **m,
           "cagr16": m16.get("cagr",np.nan), "sharpe16": m16.get("sharpe",np.nan),
           "mdd16": m16.get("max_dd",np.nan), "calmar16": m16.get("calmar",np.nan),
           **ts}
    results.append(row)

    marker = " ◄" if win == 5 else ""  # current default
    print(f"{win:>4} │ {m['cagr']:>6.1%} {m['sharpe']:>7.2f} {m['max_dd']:>7.1%} {m['calmar']:>7.2f} │"
          f" {m16.get('cagr',0):>6.1%} {m16.get('sharpe',0):>7.2f} │"
          f" {ts['n_trans']:>6} {ts['n_short1']:>4} {ts['n_short5']:>5} {ts['n_short10']:>6}"
          f" {ts['avg_dur']:>7.0f}d {ts['min_dur']:>7.0f}d{marker}")

print(f"{'─'*130}")

# ── Best by Sharpe ────────────────────────────────────────────────────
best = max(results, key=lambda r: r["sharpe"])
best16 = max(results, key=lambda r: r["sharpe16"] if not np.isnan(r["sharpe16"]) else -99)
print(f"\n★ Best Sharpe (full)  : window={best['win']}  Sharpe={best['sharpe']:.2f}  CAGR={best['cagr']:.1%}  Trans={best['n_trans']}")
print(f"★ Best Sharpe (2016+) : window={best16['win']} Sharpe={best16['sharpe16']:.2f} CAGR={best16['cagr16']:.1%} Trans={best16['n_trans']}")

# ══════════════════════════════════════════════════════════════════════
# HTML REPORT
# ══════════════════════════════════════════════════════════════════════
def pct(v, d=1):
    return "N/A" if np.isnan(v) else f"{v:.{d}%}"
def num(v, d=2):
    return "N/A" if np.isnan(v) else f"{v:.{d}f}"

tr_rows = ""
for r in results:
    is_cur  = r["win"] == 5
    is_best = r["win"] == best["win"]
    bg = "#1a2744" if is_best else ("#1e293b" if is_cur else "transparent")
    marker = " ★" if is_best else (" ◄ hiện tại" if is_cur else "")
    # Sharpe color
    sh = r["sharpe"]
    sh_col = "#4ade80" if sh >= 0.8 else "#fbbf24" if sh >= 0.5 else "#f87171"
    sh16 = r.get("sharpe16", np.nan)
    sh16_col = "#4ade80" if sh16 >= 0.8 else "#fbbf24" if sh16 >= 0.5 else "#f87171"
    # short-dur color
    s1_col  = "#f87171" if r["n_short1"] > 5  else "#fbbf24" if r["n_short1"] > 0  else "#4ade80"
    s5_col  = "#f87171" if r["n_short5"] > 20 else "#fbbf24" if r["n_short5"] > 5  else "#4ade80"
    s10_col = "#f87171" if r["n_short10"]> 40 else "#fbbf24" if r["n_short10"]> 15 else "#4ade80"

    tr_rows += f"""<tr style="background:{bg};border-bottom:1px solid #1e293b">
      <td style="padding:7px 10px;font-weight:{'800' if is_best else '600'};color:#f8fafc">{r['win']}d{marker}</td>
      <td style="padding:7px 10px;text-align:right;color:#60a5fa">{pct(r['cagr'])}</td>
      <td style="padding:7px 10px;text-align:right;color:{sh_col};font-weight:700">{num(sh)}</td>
      <td style="padding:7px 10px;text-align:right;color:#f87171">{pct(r['max_dd'])}</td>
      <td style="padding:7px 10px;text-align:right;color:#a78bfa">{num(r['calmar'])}</td>
      <td style="padding:7px 10px;text-align:right;color:#60a5fa;border-left:1px solid #334155">{pct(r['cagr16'])}</td>
      <td style="padding:7px 10px;text-align:right;color:{sh16_col};font-weight:700">{num(sh16)}</td>
      <td style="padding:7px 10px;text-align:right;color:#f87171">{pct(r.get('mdd16',np.nan))}</td>
      <td style="padding:7px 10px;text-align:right;color:#94a3b8;border-left:1px solid #334155">{r['n_trans']}</td>
      <td style="padding:7px 10px;text-align:right;color:{s1_col}">{r['n_short1']}</td>
      <td style="padding:7px 10px;text-align:right;color:{s5_col}">{r['n_short5']}</td>
      <td style="padding:7px 10px;text-align:right;color:{s10_col}">{r['n_short10']}</td>
      <td style="padding:7px 10px;text-align:right;color:#94a3b8">{r['avg_dur']:.0f}d</td>
      <td style="padding:7px 10px;text-align:right;color:#94a3b8">{r['min_dur']:.0f}d</td>
    </tr>"""

# B&H row
tr_rows += f"""<tr style="background:#0c1830;border-top:2px solid #334155">
  <td style="padding:7px 10px;color:#64748b;font-style:italic">B&amp;H</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{pct(m_bh['cagr'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{num(m_bh['sharpe'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{pct(m_bh['max_dd'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{num(m_bh['calmar'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b;border-left:1px solid #334155">{pct(m_bh_16['cagr'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{num(m_bh_16['sharpe'])}</td>
  <td style="padding:7px 10px;text-align:right;color:#64748b">{pct(m_bh_16['max_dd'])}</td>
  <td colspan="6" style="padding:7px 10px;color:#64748b;font-size:11px;border-left:1px solid #334155">— buy &amp; hold, không chuyển trạng thái</td>
</tr>"""

# Chart data
chart_wins   = [r["win"]      for r in results]
chart_sharpe = [round(r["sharpe"],3)   for r in results]
chart_sh16   = [round(r.get("sharpe16",0),3) for r in results]
chart_cagr   = [round(r["cagr"]*100,2)   for r in results]
chart_trans  = [r["n_trans"]  for r in results]
chart_s5     = [r["n_short5"] for r in results]

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Sweep MODE_WIN — Tối ưu Smoothing Window</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0f1e;color:#e2e8f0;font-family:'Segoe UI',sans-serif;padding:24px}}
h1{{font-size:22px;color:#f8fafc;margin-bottom:6px}}
.sub{{color:#64748b;font-size:13px;margin-bottom:20px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}}
.card{{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:16px}}
canvas{{width:100%!important}}
.tbl-wrap{{overflow-x:auto;border-radius:10px;border:1px solid #1e293b;margin-bottom:24px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead th{{background:#0f172a;color:#475569;font-size:11px;font-weight:700;text-transform:uppercase;
          letter-spacing:.5px;padding:9px 10px;position:sticky;top:0;z-index:5;
          border-bottom:2px solid #1e293b;white-space:nowrap;text-align:right}}
thead th:first-child{{text-align:left}}
tr:hover td{{background:rgba(96,165,250,0.06)!important}}
.note{{background:#1e293b;border:1px solid #334155;border-radius:8px;padding:14px 18px;
       font-size:13px;line-height:1.7;color:#94a3b8;margin-bottom:20px}}
.note strong{{color:#e2e8f0}}
.highlight{{color:#fbbf24;font-weight:700}}
</style>
</head>
<body>
<h1>🔬 Sweep MODE_WIN: Tối ưu Smoothing Window cho 5-State System</h1>
<p class="sub">Sweep window từ 3 → 40 ngày &nbsp;·&nbsp; Giữ nguyên tất cả tham số khác (RAMP=3, SNAP=3%, TC=0.1%)</p>

<div class="note">
  <strong>Giải thích cột:</strong><br>
  <strong>1d</strong> = số lần trạng thái tồn tại ≤ 1 ngày (flip ngay hôm sau) &nbsp;·&nbsp;
  <strong>≤5d / ≤10d</strong> = số lần trạng thái ngắn &nbsp;·&nbsp;
  <strong>AvgDur</strong> = thời gian giữ trạng thái trung bình &nbsp;·&nbsp;
  <strong>MinDur</strong> = trạng thái ngắn nhất &nbsp;·&nbsp;
  <span class="highlight">★ = window cho Sharpe cao nhất</span> &nbsp;·&nbsp;
  ◄ = window hiện tại (5d)
</div>

<div class="tbl-wrap">
<table>
<thead>
<tr>
  <th style="text-align:left">Window</th>
  <th colspan="4" style="text-align:center;border-left:1px solid #334155">── Full Period ──</th>
  <th colspan="3" style="text-align:center;border-left:1px solid #334155">── Từ 2016 ──</th>
  <th colspan="6" style="text-align:center;border-left:1px solid #334155">── Transition Quality ──</th>
</tr>
<tr>
  <th style="text-align:left">Window</th>
  <th style="border-left:1px solid #334155">CAGR</th><th>Sharpe</th><th>MaxDD</th><th>Calmar</th>
  <th style="border-left:1px solid #334155">CAGR</th><th>Sharpe</th><th>MaxDD</th>
  <th style="border-left:1px solid #334155">Trans</th><th>1d</th><th>≤5d</th><th>≤10d</th><th>AvgDur</th><th>MinDur</th>
</tr>
</thead>
<tbody>
{tr_rows}
</tbody>
</table>
</div>

<div class="grid">
  <div class="card">
    <h3 style="font-size:14px;color:#94a3b8;margin-bottom:12px">Sharpe vs Window size</h3>
    <canvas id="chartSharpe" height="200"></canvas>
  </div>
  <div class="card">
    <h3 style="font-size:14px;color:#94a3b8;margin-bottom:12px">Số transitions & trạng thái ≤5d</h3>
    <canvas id="chartTrans" height="200"></canvas>
  </div>
  <div class="card">
    <h3 style="font-size:14px;color:#94a3b8;margin-bottom:12px">CAGR vs Window size</h3>
    <canvas id="chartCagr" height="200"></canvas>
  </div>
</div>

<script>
const wins   = {chart_wins};
const sharpe = {chart_sharpe};
const sh16   = {chart_sh16};
const cagr   = {chart_cagr};
const trans  = {chart_trans};
const s5     = {chart_s5};

const defaults = {{responsive:true,maintainAspectRatio:false,animation:false,
  plugins:{{legend:{{labels:{{boxWidth:12,color:'#94a3b8'}}}}}},
  scales:{{x:{{ticks:{{color:'#64748b'}},grid:{{color:'#1e293b'}}}},
           y:{{ticks:{{color:'#64748b'}},grid:{{color:'#1e293b'}}}}}}}};

new Chart(document.getElementById('chartSharpe'),{{
  type:'line',
  data:{{labels:wins.map(w=>w+'d'),datasets:[
    {{label:'Sharpe (full)',data:sharpe,borderColor:'#4ade80',borderWidth:2,pointRadius:5,pointBackgroundColor:'#4ade80',fill:false}},
    {{label:'Sharpe (2016+)',data:sh16,borderColor:'#60a5fa',borderWidth:2,pointRadius:5,pointBackgroundColor:'#60a5fa',borderDash:[4,3],fill:false}}
  ]}},
  options:{{...defaults,scales:{{x:{{...defaults.scales.x}},y:{{...defaults.scales.y,
    title:{{display:true,text:'Sharpe Ratio',color:'#64748b'}}}}}}}}
}});

new Chart(document.getElementById('chartTrans'),{{
  type:'bar',
  data:{{labels:wins.map(w=>w+'d'),datasets:[
    {{label:'Tổng transitions',data:trans,backgroundColor:'rgba(96,165,250,0.6)',yAxisID:'y'}},
    {{label:'Trạng thái ≤5d',data:s5,backgroundColor:'rgba(248,113,113,0.7)',yAxisID:'y2'}}
  ]}},
  options:{{...defaults,scales:{{
    x:{{...defaults.scales.x}},
    y:{{...defaults.scales.y,position:'left',title:{{display:true,text:'Tổng trans',color:'#64748b'}}}},
    y2:{{position:'right',grid:{{drawOnChartArea:false}},ticks:{{color:'#f87171'}},
         title:{{display:true,text:'≤5d',color:'#f87171'}}}}
  }}}}
}});

new Chart(document.getElementById('chartCagr'),{{
  type:'line',
  data:{{labels:wins.map(w=>w+'d'),datasets:[
    {{label:'CAGR% (full)',data:cagr,borderColor:'#fbbf24',borderWidth:2,pointRadius:5,fill:false}}
  ]}},
  options:{{...defaults,scales:{{x:{{...defaults.scales.x}},y:{{...defaults.scales.y,
    title:{{display:true,text:'CAGR (%)',color:'#64748b'}}}}}}}}
}});
</script>
</body>
</html>"""

out_path = os.path.join(WORKDIR, "sweep_window_results.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nSaved: {out_path}")
print("Done.")
