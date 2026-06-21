# -*- coding: utf-8 -*-
"""
Test: dung DINH VIX (causal-confirmed) de du bao day VNINDEX / re-risk som khoi CRISIS (DT5G)
3 lop:
  1) Event study: VIX-peak-confirmed lead/lag vs day VNINDEX
  2) Coverage: bao nhieu cu sap VN co VIX spike di kem (decoupling risk)
  3) Counterfactual NAV: DT5G + VIX-floor (CRISIS -> BEAR/NEUTRAL khi VIX peak confirmed)
"""
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ---------- load ----------
us = pd.read_csv(f"{WORKDIR}\\us_market_history.csv", parse_dates=["time"])
us = us[["time", "vix", "spx_dd_1y"]].dropna(subset=["vix"]).set_index("time").sort_index()

vni = pd.read_csv(f"{WORKDIR}\\VNINDEX.csv", usecols=["time", "Close"], parse_dates=["time"])
vni = vni.set_index("time").sort_index()["Close"].dropna()

st = pd.read_csv(f"{WORKDIR}\\vnindex_5state_dt5g_live.csv", parse_dates=["time"]).set_index("time").sort_index()

# align VIX to VN calendar at T-1 (same convention as macro_state_live: US close known next VN morning)
vn_idx = vni.index
vix_on_vn = us["vix"].reindex(vn_idx.union(us.index)).ffill().shift(1).reindex(vn_idx)

# ---------- 1) causal VIX-peak-confirmed signal ----------
# fire on the FIRST day where: rolling-max VIX (past 60 VN sessions) >= TH
# AND current VIX <= (1-COOL) * that peak  (peak da nguoi 25%)
def vix_peak_signal(vix, th=30.0, cool=0.25, win=60):
    rmax = vix.rolling(win, min_periods=5).max()
    cond = (rmax >= th) & (vix <= (1 - cool) * rmax)
    # first-day-of-episode: cond True and was False yesterday
    fire = cond & ~cond.shift(1, fill_value=False)
    return cond, fire, rmax

# ---------- VN bottoms: major drawdown episodes ----------
def vn_bottoms(close, dd_th=-0.15):
    roll_max = close.cummax()
    dd = close / roll_max - 1
    in_dd = dd < dd_th
    bottoms = []
    i = 0
    dates = close.index
    arr = in_dd.values
    n = len(arr)
    while i < n:
        if arr[i]:
            j = i
            while j < n and dd.iloc[j] < -0.05:  # episode ends when recovered to -5%
                j += 1
            seg = close.iloc[i:j]
            if len(seg) > 0:
                bot = seg.idxmin()
                bottoms.append((bot, dd.loc[bot]))
            i = j
        else:
            i += 1
    return bottoms, dd

print("=" * 100)
print("LOP 1+2: VIX-peak-confirmed vs day VNINDEX (full history 2000->now)")
print("=" * 100)

for TH, COOL in [(30, 0.25), (35, 0.25), (28, 0.20)]:
    cond, fire, rmax = vix_peak_signal(vix_on_vn, th=TH, cool=COOL)
    fires = vix_on_vn.index[fire.values]
    print(f"\n--- TH=VIX>={TH}, cool={int(COOL*100)}% tu dinh | so lan fire: {len(fires)} ---")
    bots, dd = vn_bottoms(vni, dd_th=-0.15)
    # for each VN bottom: nearest fire within [-120, +120] sessions
    pos = {d: k for k, d in enumerate(vn_idx)}
    for bot, bdd in bots:
        bi = pos[bot]
        best = None
        for f in fires:
            fi = pos[f]
            lag = fi - bi  # >0: fire AFTER bottom
            if abs(lag) <= 150 and (best is None or abs(lag) < abs(best[1])):
                best = (f, lag)
        if best:
            print(f"  day VN {bot.date()} (dd {bdd:+.0%})  <- fire {best[0].date()}  lag {best[1]:+4d} phien "
                  f"({'fire TRUOC day' if best[1]<0 else 'fire SAU day'})")
        else:
            print(f"  day VN {bot.date()} (dd {bdd:+.0%})  <- KHONG co VIX-peak signal trong +/-150 phien (noi dia thuan)")

# forward returns after each fire
TH, COOL = 30, 0.25
cond, fire, rmax = vix_peak_signal(vix_on_vn, th=TH, cool=COOL)
fires = vix_on_vn.index[fire.values]
rows = []
for f in fires:
    fi = vn_idx.get_loc(f)
    r = {}
    for h in (20, 60, 120):
        if fi + h < len(vni):
            r[f"fwd{h}"] = vni.iloc[fi + h] / vni.iloc[fi] - 1
    # max further drawdown within next 60 sessions (rui ro "bat dao roi")
    seg = vni.iloc[fi:fi + 61]
    r["maxdd_60"] = seg.min() / vni.iloc[fi] - 1
    r["date"] = f.date()
    rows.append(r)
ev = pd.DataFrame(rows).set_index("date")
print(f"\n--- Event study sau fire (TH=30/cool25, n={len(ev)}) ---")
print(ev.round(3).to_string())
print("\nTrung vi:", {c: round(ev[c].median(), 3) for c in ev.columns})
print("Win rate fwd60:", round((ev["fwd60"] > 0).mean(), 2) if "fwd60" in ev else None)

# ---------- 3) counterfactual NAV: DT5G + VIX floor ----------
print("\n" + "=" * 100)
print("LOP 3: NAV sim 2014->now  |  DT5G goc vs DT5G+VIX-floor (CRISIS->floor khi VIX-peak-confirmed)")
print("=" * 100)

W = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
TC, BORROW = 0.001, 0.10

sim_idx = st.index.intersection(vni.index)
state = st.loc[sim_idx, "state"].astype(int)
close = vni.loc[sim_idx]
ret = close.pct_change().fillna(0)
vixc = vix_on_vn.reindex(sim_idx).ffill()
cond_all, _, _ = vix_peak_signal(vix_on_vn, th=30, cool=0.25)
vix_ok = cond_all.reindex(sim_idx).fillna(False)

def run_nav(states, label):
    w_tgt = states.map(W)
    w = w_tgt.shift(1).fillna(0)  # T+1 execution
    dw = w.diff().abs().fillna(0)
    spy = 250
    r = w * ret - dw * TC - np.maximum(0, w - 1) * BORROW / spy
    nav = (1 + r).cumprod()
    yrs = (sim_idx[-1] - sim_idx[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    dd = (nav / nav.cummax() - 1).min()
    sharpe = r.mean() / (r.std() + 1e-12) * np.sqrt(spy)
    print(f"  {label:34s} CAGR {cagr*100:6.2f}%  MaxDD {dd*100:6.1f}%  Sharpe {sharpe:5.2f}  "
          f"ngay CRISIS {(states==1).sum():4d}  ngay BEAR {(states==2).sum():4d}")
    return states

base = run_nav(state, "DT5G goc")

# variant A: CRISIS + VIX-peak-confirmed -> nang len BEAR (20%)
vA = state.copy()
mask = (state == 1) & vix_ok
vA[mask] = 2
run_nav(vA, "VIX-floor -> BEAR (20%)")

# variant B: -> NEUTRAL (70%)
vB = state.copy()
vB[mask] = 3
run_nav(vB, "VIX-floor -> NEUTRAL (70%)")

# variant C: floor BEAR, them guard gia (Close > min 20 phien -> day da xac nhan nhe)
price_guard = close > close.rolling(20).min().shift(1) * 1.03
vC = state.copy()
vC[(state == 1) & vix_ok & price_guard] = 2
run_nav(vC, "VIX-floor BEAR + guard gia +3%")

# how many CRISIS days does the floor actually touch, and in which episodes
print("\nNgay CRISIS bi VIX-floor cham (variant A):", int(mask.sum()))
if mask.sum():
    grp = (mask != mask.shift()).cumsum()[mask]
    for g, seg in mask[mask].groupby(grp):
        print(f"   {seg.index[0].date()} -> {seg.index[-1].date()}  ({len(seg)} phien)")

# per-episode detail: DT5G CRISIS episodes & where VIX peak fell
print("\n--- Cac episode CRISIS cua DT5G & vi tri dinh VIX ---")
cri = state == 1
grp = (cri != cri.shift()).cumsum()[cri]
for g, seg in state[cri].groupby(grp):
    s0, s1 = seg.index[0], seg.index[-1]
    vseg = vixc.loc[s0:s1]
    vmax_d = vseg.idxmax() if len(vseg.dropna()) else None
    bot_d = close.loc[s0:s1].idxmin()
    print(f"  CRISIS {s0.date()} -> {s1.date()} ({len(seg)} phien) | VIX max trong ep: "
          f"{vseg.max():.1f} @ {vmax_d.date() if vmax_d is not None else 'n/a'} | day gia: {bot_d.date()}")
