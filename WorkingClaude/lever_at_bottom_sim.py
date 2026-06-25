"""
lever_at_bottom_sim.py — dedicated LEVERED BOOK opening only at confirmed capitulation bottoms.

Self-contained, fully-auditable sandbox (Taylor, 2026-06-25; user spec) to study, without guessing:
WHAT to buy (custom30 vs VNINDEX), HOW LONG to hold (close-rule), HOW MUCH to borrow (LEVER_FRAC).

Book mechanics (a SEPARATE book):
  OPEN  : A∧C-confirm bottom — vol_ratio_3M ≥ VOL_THR inside gate(state∈{CRISIS,BEAR} ∧ pb_z≤-0.5) AND a
          refined BullDvg "C-arm" within last C_ARM_K sessions. One open per episode (28-day dedup).
  BORROW: on open, borrow = LEVER_FRAC × NAV[T-1]; buy basket worth NAV[T-1]+borrow ⇒ gross = 1+LEVER_FRAC.
  CLOSE : CLOSE_RULE ∈ {regime, fixed, trail}, after MIN_HOLD, hard-capped MAX_HOLD; optional book-DD STOP.
            regime → exit when state ≥ NEUTRAL(3)        fixed → exit after FIXED_HOLD days
            trail  → exit when book NAV drops TRAIL from the episode peak
  Borrow charged BORROW_RATE/yr (act/365) while open. Idle book cash earns 0%.

Self-check: compounded per-episode book-returns == simulated final NAV (== 0 VND).

Single run (env): UNIVERSE LEVER_FRAC VOL_THR C_ARM_K MIN_HOLD MAX_HOLD STOP CLOSE_RULE FIXED_HOLD TRAIL START
Sweep:  SWEEP=1 python lever_at_bottom_sim.py   → leaderboard over close-rule × frac on both universes.
"""
import os, numpy as np, pandas as pd

WORK = "/home/trido/thanhdt/WorkingClaude"
BORROW_RATE = float(os.environ.get("BORROW_RATE", "0.10"))
START = os.environ.get("START", "2011-01-01")
NAV0 = 1_000_000_000.0
DT = 1.0 / 365.0

# ---------------------------------------------------------------- load data once
_vni = pd.read_csv("/tmp/vni_2011.csv"); _vni["time"] = pd.to_datetime(_vni["time"])
_vni = _vni[_vni["time"] >= START].sort_values("time").reset_index(drop=True)
_st = pd.read_csv("/tmp/state_2011.csv"); _st["time"] = pd.to_datetime(_st["time"])
_vni = _vni.merge(_st, on="time", how="left"); _vni["state"] = _vni["state"].ffill()
_pb = pd.read_csv("/tmp/pbz_2011.csv"); _pbm = {r.ym: r.med_pbz for r in _pb.itertuples()}
_vni["pbz"] = _vni["time"].apply(lambda t: _pbm.get((t.to_period("M") - 1).strftime("%Y-%m"), np.nan))

# deposit-gate (production false-bottom blocker): money-condition m = clip((CEIL-dep)/(CEIL-FLOOR),0,1).
# High deposit/borrow rates (2011: 14%) → m=0 → no lever (bad carry). Falls to m=1 by ~2013 (rates ≤7.5%).
from deposit_rate_vn import DEPOSIT_EVENTS as _DEPEV
_dep = sorted((pd.Timestamp(d), v / 100.0) for d, v in _DEPEV)
def _dep_asof(t):
    t = pd.Timestamp(t); r = _dep[0][1]
    for dd, vv in _dep:
        if dd <= t: r = vv
        else: break
    return r
_DEP_FLOOR, _DEP_CEIL = 0.075, 0.12
_vni["dep_m"] = _vni["time"].apply(
    lambda t: float(np.clip((_DEP_CEIL - _dep_asof(t)) / (_DEP_CEIL - _DEP_FLOOR), 0.0, 1.0)))

def build_signal(vol_thr, c_arm_k, dep_m_min=0.0):
    v = _vni.copy(); r = v["D_RSI"]; c = v["Close"]
    v["vr63"] = v["Volume"] / v["Volume"].rolling(63, min_periods=20).mean().shift(1)
    sigA = v["vr63"] >= vol_thr
    rmin3m = r.rolling(63, min_periods=20).min()
    carm = (r > r.shift(63) + 0.02) & (c <= c.shift(63) * 1.06) & (rmin3m < 0.40) & (r < 0.60)
    carmed = carm.rolling(c_arm_k, min_periods=1).max().fillna(0).astype(bool)
    gate = v["state"].isin([1, 2]) & (v["pbz"] <= -0.5)
    money_ok = v["dep_m"] >= dep_m_min        # deposit-gate: block lever when borrow carry is bad
    return (sigA & carmed & gate & money_ok).values

DATES = _vni["time"].tolist()
STATE_BY = dict(zip(_vni["time"], _vni["state"]))

def _custom30_index():
    comp = pd.read_parquet(f"{WORK}/data/bq_cache/custom30v_8l.parquet")
    for col in ("effective_from", "effective_to"): comp[col] = pd.to_datetime(comp[col])
    px = pd.read_csv("/tmp/c30_prices.csv"); px["time"] = pd.to_datetime(px["time"])
    pan = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()
    ret = pan.pct_change(); bret = pd.Series(0.0, index=pan.index)
    for (ef, et), grp in comp.groupby(["effective_from", "effective_to"]):
        w = grp.set_index("ticker")["weight"]; members = [t for t in w.index if t in ret.columns]
        if not members: continue
        win = ret.loc[(ret.index >= ef) & (ret.index < et), members]
        if win.empty: continue
        wmat = win.notna().mul(w[members].astype(float), axis=1)
        wmat = wmat.div(wmat.sum(axis=1).replace(0, np.nan), axis=0)
        bret.loc[win.index] = (win.fillna(0.0) * wmat).sum(axis=1)
    return (1.0 + bret.fillna(0.0)).cumprod()

_C30 = _custom30_index()
BASKETS = {
    "custom30": _C30.reindex(DATES).ffill(),
    "vnindex": _vni.set_index("time")["Close"].reindex(DATES).ffill(),
}

def run_book(universe="custom30", lever_frac=0.30, vol_thr=1.7, c_arm_k=30,
             min_hold=10, max_hold=252, stop=0.0, close_rule="regime",
             fixed_hold=120, trail=-0.08, dep_m_min=0.0):
    basket = BASKETS[universe]; bret = basket.pct_change().fillna(0.0)
    bret_by = dict(zip(DATES, bret.values)); avail = basket.notna()
    opensig = build_signal(vol_thr, c_arm_k, dep_m_min)
    cash = NAV0; pos = 0.0; borrow = 0.0; opened = False; dh = 0
    entry_nav = entry_basket = 0.0; entry_date = None; ep_peak = NAV0
    navs = []; episodes = []; last_close = None
    for i, d in enumerate(DATES):
        if opened:
            pos += pos * bret_by.get(d, 0.0)
            borrow += borrow * BORROW_RATE * DT
            dh += 1
        nav = cash + pos - borrow
        if opened: ep_peak = max(ep_peak, nav)
        if opened:
            stp = int(STATE_BY.get(d, 1) or 1); dd = nav / ep_peak - 1.0
            close = False; why = ""
            if dh >= min_hold:
                if close_rule == "regime" and stp >= 3: close, why = True, f"regime NEUTRAL+({stp})"
                elif close_rule == "fixed" and dh >= fixed_hold: close, why = True, f"fixed {fixed_hold}d"
                elif close_rule == "trail" and dd <= trail: close, why = True, f"trail {dd:.0%}"
            if not close and dh >= max_hold: close, why = True, f"max {max_hold}d"
            if not close and stop < 0 and dd <= stop: close, why = True, f"stop {dd:.0%}"
            if close:
                episodes.append(dict(open=entry_date.date(), close=d.date(), days=dh,
                                     basket_ret=pos / entry_basket - 1.0,
                                     interest=borrow - entry_nav * lever_frac,
                                     book_ret=nav / entry_nav - 1.0, why=why))
                cash = cash + pos - borrow; pos = 0.0; borrow = 0.0; opened = False; dh = 0
                last_close = d
        if (not opened) and opensig[i] and avail.get(d, False):
            if last_close is None or (d - last_close).days > 28:
                nav_prev = navs[-1] if navs else NAV0
                borrow = lever_frac * nav_prev; entry_nav = cash
                pos = entry_nav + borrow; cash = 0.0
                entry_basket = pos; entry_date = d; opened = True; dh = 0; ep_peak = entry_nav
        navs.append(cash + pos - borrow)
    n = np.asarray(navs, float); t = np.asarray(DATES, "datetime64[ns]")
    yrs = (t[-1] - t[0]) / np.timedelta64(365, "D")
    peak = np.maximum.accumulate(n)
    rets = [e["book_ret"] for e in episodes]
    chk = NAV0
    for e in episodes: chk *= (1 + e["book_ret"])
    return dict(episodes=episodes, final=n[-1], cagr=((n[-1]/n[0])**(1/yrs)-1)*100,
                maxdd=(n/peak-1).min()*100, n=len(episodes),
                n_loss=sum(1 for x in rets if x < 0), worst=min(rets)*100 if rets else 0,
                mean=np.mean(rets)*100 if rets else 0, selfcheck=abs(chk-n[-1]))

if __name__ == "__main__" and os.environ.get("SWEEP"):
    rules = [("regime", {}), ("fixed", {"fixed_hold": 60}), ("fixed", {"fixed_hold": 120}),
             ("fixed", {"fixed_hold": 180}), ("trail", {"trail": -0.08}), ("trail", {"trail": -0.12})]
    for uni in ("vnindex", "custom30"):
        print(f"\n===== SWEEP universe={uni} (frac=0.30) — close-rule study =====")
        print(f"{'close-rule':16s} {'#ep':>4s} {'#loss':>5s} {'mean_ep%':>8s} {'worst_ep%':>9s} "
              f"{'final':>7s} {'bookDD%':>8s} {'0VND':>5s}")
        for cr, kw in rules:
            r = run_book(universe=uni, lever_frac=0.30, close_rule=cr, **kw)
            lbl = cr + ("" if cr == "regime" else f"({list(kw.values())[0]})")
            print(f"{lbl:16s} {r['n']:>4} {r['n_loss']:>5} {r['mean']:>+7.1f}% {r['worst']:>+8.1f}% "
                  f"{r['final']/1e9:>6.2f}B {r['maxdd']:>7.1f}% {'OK' if r['selfcheck']<1 else 'X':>5s}")
    print(f"\n===== FRAC study (custom30, best close-rule per above) =====")
    for cr, kw in [("regime", {}), ("trail", {"trail": -0.08})]:
        print(f"  -- close={cr}{kw if kw else ''} --")
        for fr in (0.0, 0.20, 0.30, 0.50, 0.75):
            r = run_book(universe="custom30", lever_frac=fr, close_rule=cr, **kw)
            print(f"     frac {fr:.2f}: mean_ep {r['mean']:+.1f}%  worst {r['worst']:+.1f}%  "
                  f"final {r['final']/1e9:.2f}B  bookDD {r['maxdd']:.1f}%  0VND={'OK' if r['selfcheck']<1 else 'X'}")
elif __name__ == "__main__":
    P = dict(universe=os.environ.get("UNIVERSE", "custom30").lower(),
             lever_frac=float(os.environ.get("LEVER_FRAC", "0.30")),
             vol_thr=float(os.environ.get("VOL_THR", "1.7")), c_arm_k=int(os.environ.get("C_ARM_K", "30")),
             min_hold=int(os.environ.get("MIN_HOLD", "10")), max_hold=int(os.environ.get("MAX_HOLD", "252")),
             stop=float(os.environ.get("STOP", "0")), close_rule=os.environ.get("CLOSE_RULE", "regime"),
             fixed_hold=int(os.environ.get("FIXED_HOLD", "120")), trail=float(os.environ.get("TRAIL", "-0.08")))
    r = run_book(**P)
    print(f"=== universe={P['universe']} frac={P['lever_frac']} close={P['close_rule']} ===")
    print(f"{'#':>2} {'open':11s} {'close':11s} {'days':>4s} {'basket%':>8s} {'BOOK%':>8s} {'reason':20s}")
    for k, e in enumerate(r["episodes"], 1):
        print(f"{k:>2} {str(e['open']):11s} {str(e['close']):11s} {e['days']:>4} "
              f"{e['basket_ret']*100:>+7.1f}% {e['book_ret']*100:>+7.1f}% {e['why']:20s}")
    print(f"final {r['final']/1e9:.3f}B  CAGR {r['cagr']:.2f}%  bookDD {r['maxdd']:.1f}%  "
          f"loss {r['n_loss']}/{r['n']}  self-check {r['selfcheck']:,.0f} VND")
