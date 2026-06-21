#!/usr/bin/env python3
"""Faithful daily-ledger sim for Book C (value, monthly rebalance) + BAL-swap test.

Mechanics (house cost model, same constants as simulate_holistic_nav):
  - Signal at close of FIRST session of month m -> execute at OPEN of session 2 (T+1 Open).
  - Target weights: each pick = alloc_m / n_picks_m of current NAV (alloc = Book C's own
    state gate from the research backtest). Names dropped from the list -> full sell.
    Continuing names -> trade only the DELTA (real monthly-rebalance dedupe).
  - Costs: slippage 0.1%/side + TC 0.1%/side + CGT 0.1% on sells (0.5% effective round trip).
  - Liquidity: per name per day max 20% of ADV notional (liq_adv), order carried up to
    5 sessions, remainder abandoned.
  - Idle cash: 0%/yr (conservative — BAL gets ETF parking in NEUTRAL, Book C gets nothing).
  - NAV marked daily at Close. Init 17.5B (the partner-book size under the w=.65 allocator).
"""
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

W = r"/home/trido/thanhdt/WorkingClaude"
INIT = 17_500_000_000
SLIP = 0.001; TC = 0.001; CGT = 0.001
LIQ_PCT = 0.20; MAX_FILL_DAYS = 5

print("[1] data...")
panel = pd.read_csv(os.path.join(W, "data", "v4f_panel_2014.csv"), parse_dates=["time"])
bc = pd.read_csv(os.path.join(W, "data", "book_c_backtest.csv"))
bc["month"] = pd.to_datetime(bc["time"] + "-01")
need = set()
for t in bc["tickers"].dropna(): need.update(t.split(","))
panel = panel[panel["ticker"].isin(need)]
close = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opn   = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
adv   = {tk: dict(zip(g["time"], g["liq_adv"])) for tk, g in panel.groupby("ticker")}
all_dates = sorted(pd.read_csv(os.path.join(W, "data", "v4f_panel_2014.csv"),
                               usecols=["time"], parse_dates=["time"])["time"].unique())
all_dates = [d for d in all_dates if d >= bc["month"].min()]

# rebalance schedule: month -> (signal_day = 1st session, exec_day = 2nd session)
dser = pd.Series(all_dates)
sched = {}
for m in bc["month"]:
    days = dser[(dser >= m) & (dser < m + pd.offsets.MonthBegin(1))]
    if len(days) >= 2: sched[m] = (days.iloc[0], days.iloc[1])
targets_by_exec = {}
for _, r in bc.iterrows():
    if r["month"] not in sched or pd.isna(r["tickers"]): continue
    _, ex = sched[r["month"]]
    picks = r["tickers"].split(",")
    targets_by_exec[ex] = {tk: r["alloc"] / len(picks) for tk in picks}

print(f"  {len(targets_by_exec)} rebalance days, {len(all_dates)} sessions")

print("[2] simulating...")
cash = float(INIT); pos = {}                      # ticker -> shares
pending = []                                       # {tk, side, shares_left, days}
nav_rows = []
def px(tk, d, kind="close"):
    src = close if kind == "close" else opn
    v = src.get(tk, {}).get(d)
    if (v is None or not np.isfinite(v)) and kind == "open":
        v = close.get(tk, {}).get(d)
    return v
last_px = {}
for d in all_dates:
    # 1) execute pending orders at today's OPEN, liquidity-capped
    still = []
    for o in pending:
        p = px(o["tk"], d, "open")
        if p is None or p <= 0:
            o["days"] += 1
            if o["days"] < MAX_FILL_DAYS: still.append(o)
            continue
        a = adv.get(o["tk"], {}).get(d, 0) or 0
        cap_sh = (a * LIQ_PCT) / p if a > 0 else o["sh"]
        fill = min(o["sh"], cap_sh)
        if fill > 0:
            if o["side"] == "buy":
                cost = fill * p * (1 + SLIP) * (1 + TC)
                if cost > cash: fill = max(0.0, cash / (p * (1 + SLIP) * (1 + TC))); cost = fill * p * (1 + SLIP) * (1 + TC)
                cash -= cost; pos[o["tk"]] = pos.get(o["tk"], 0) + fill
            else:
                fill = min(fill, pos.get(o["tk"], 0))
                cash += fill * p * (1 - SLIP) * (1 - TC - CGT)
                pos[o["tk"]] = pos.get(o["tk"], 0) - fill
                if pos.get(o["tk"], 0) <= 1e-9: pos.pop(o["tk"], None)
        o["sh"] -= fill; o["days"] += 1
        if o["sh"] > 1e-9 and o["days"] < MAX_FILL_DAYS: still.append(o)
    pending = still
    # 2) mark NAV at close
    mv = 0.0
    for tk, sh in pos.items():
        p = px(tk, d, "close")
        if p is not None and p > 0: last_px[tk] = p
        mv += sh * last_px.get(tk, 0.0)
    nav = cash + mv
    nav_rows.append({"time": d, "nav": nav, "cash": cash, "stocks_mv": mv, "n_pos": len(pos)})
    # 3) if today is an exec day, queue delta orders vs targets (sized on today's NAV)
    if d in targets_by_exec:
        tgt = targets_by_exec[d]
        cur_w = {tk: (pos.get(tk, 0) * last_px.get(tk, 0)) / nav for tk in set(pos) | set(tgt)}
        for tk in sorted(set(pos) | set(tgt)):
            tw = tgt.get(tk, 0.0); cw = cur_w.get(tk, 0.0)
            delta_vnd = (tw - cw) * nav
            p = last_px.get(tk) or px(tk, d, "close")
            if p is None or p <= 0: continue
            if abs(delta_vnd) < 0.002 * nav: continue            # ignore <0.2% NAV noise
            side = "buy" if delta_vnd > 0 else "sell"
            pending.append({"tk": tk, "side": side, "sh": abs(delta_vnd) / p, "days": 0})

nav_c = pd.DataFrame(nav_rows).set_index("time")["nav"]
nav_c.to_csv(os.path.join(W, "data", "bookc_faithful_nav.csv"))
def met(s):
    s = s.dropna(); r = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    dd = (s / s.cummax() - 1).min(); sh = r.mean() / r.std() * np.sqrt(252)
    return cagr * 100, dd * 100, sh, cagr / abs(dd)
m = met(nav_c)
print(f"  Book C FAITHFUL standalone: CAGR {m[0]:.2f}%  MaxDD {m[1]:.1f}%  Sharpe {m[2]:.2f}  Calmar {m[3]:.2f}")

print("[3] swap test (band-only allocator ±10pp, w_LAG={1:.5,2:0,3/4/5:.65}, LAG haircut 6%)...")
bal = pd.read_csv(os.path.join(W, "data", "pt_v22_bal_v21_cap.csv"), parse_dates=["time"]).set_index("time")
lag = pd.read_csv(os.path.join(W, "data", "pt_v22_lag_v21_cap.csv"), parse_dates=["time"]).set_index("time")
idx = nav_c.index.intersection(bal.index)
d2 = pd.DataFrame({"rl": lag["nav"].pct_change(), "rb_bal": bal["nav"].pct_change(),
                   "rb_c": nav_c.pct_change(), "st": bal["state"]}).loc[idx].dropna()
d2["st"] = d2["st"].astype(int)
WMAP = {1: .5, 2: .0, 3: .65, 4: .65, 5: .65}; BAND = 0.10; RTC = 0.001; HAIR = 0.06
def alloc(pcol):
    w = WMAP[d2["st"].iloc[0]]; cl = w; cb = 1 - w; out = []; nreb = 0
    for t, row in d2.iterrows():
        cl *= (1 + row["rl"] * (1 - HAIR)); cb *= (1 + row[pcol])
        P = cl + cb; tgt = WMAP.get(int(row["st"]), .5)
        if P > 0 and abs(cl / P - tgt) > BAND:
            P -= RTC * abs(tgt * P - cl); cl = tgt * P; cb = (1 - tgt) * P; nreb += 1
        out.append((t, cl + cb))
    return pd.Series(dict(out)), nreb
print(f"  window: {d2.index.min().date()} -> {d2.index.max().date()}")
print(f"  {'combined (allocator)':<30}{'FULL':>8}{'DD':>8}{'Sh':>6}{'Cal':>6}  {'2022+':>7}{'2025+':>8}  #reb")
for nm, pc in [("partner = BAL (current)", "rb_bal"), ("partner = Book C FAITHFUL", "rb_c")]:
    s, n = alloc(pc)
    mm = met(s); m22 = met(s[s.index >= "2022-01-01"]); m25 = met(s[s.index >= "2025-01-01"])
    print(f"  {nm:<30}{mm[0]:>7.2f}%{mm[1]:>7.1f}%{mm[2]:>6.2f}{mm[3]:>6.2f}  {m22[0]:>6.2f}%{m25[0]:>7.2f}%  {n}")
# standalone reference on same window
for nm, col in [("BAL standalone", "rb_bal"), ("BookC standalone", "rb_c"), ("LAG standalone", "rl")]:
    s = (1 + d2[col]).cumprod(); mm = met(s)
    print(f"  {nm:<30}{mm[0]:>7.2f}%{mm[1]:>7.1f}%{mm[2]:>6.2f}")
