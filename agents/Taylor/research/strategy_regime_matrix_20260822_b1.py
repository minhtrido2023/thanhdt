#!/usr/bin/env python
"""B1 — BAL exit theo DT candidate streak. Job Taylor_20260822_141143. PAPER-ONLY.

Nguon (da tra mike/kb/data_registry/):
  - pin R3 2026-08-03 CANONICAL (results_registry "RE-PIN R3 ... LAG_ADV_BASIS=price"): TX ledger
    + DAILY nav_bal_ref. self-check 0 VND o ban goc.
  - tav2_bq.ticker Close (adj) CANONICAL cho 236 ma BAL.
  - CUSTOM_BASKET rows trong chinh file pin = chuoi chi so ro parking custom30V.
  - DT5G committed: cot state cua DAILY rows (= vnindex_5state_dt5g_live, KHONG phai bang tho).
  - BASE v3.4b: tav2_bq.vnindex_5state (dung LAM XAP XI candidate streak — xem caveat).
KHONG dung cot profit_* (forward-looking).
"""
import os, sys, json
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
PIN = os.path.join(W, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")
SPY = 249.2785102175346
PARK_TK = "CUSTOM_VN30EXVIC_PITG"
COLS = ["record_type","key","value","ymd","book","ticker","action","play_type","holding_id",
        "shares","adj_price","buy_amount","sell_amount","fee","cash_after","reason","state",
        "nav_bal_ref","nav_lag_ref","bal_cash_ref","bal_stocks_ref","bal_etf_ref","lag_cash_ref",
        "lag_stocks_ref","lag_etf_ref","w_lag_tgt","rebal_cost","cap_bal","cap_lag",
        "combined_nav","vni_close"]

raw = pd.read_csv(PIN, names=COLS, header=0, low_memory=False)
raw["time"] = pd.to_datetime(raw["ymd"], format="ISO8601")

d = raw[raw.record_type == "DAILY"].copy()
for c in ["state","nav_bal_ref","combined_nav","vni_close"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")
d = d.sort_values("time").reset_index(drop=True)
DATES = list(d.time)
DIDX = {t: i for i, t in enumerate(DATES)}
print(f"[data] {len(DATES)} phien {DATES[0].date()}..{DATES[-1].date()}")

# ---- gia: BQ ticker Close + chuoi ro parking tu chinh file pin
px = pd.read_csv(os.path.join(OUT, "b1_px.csv"), parse_dates=["time"])
cb = raw[raw.record_type == "CUSTOM_BASKET"][["time", "ticker", "value"]].copy()
cb["Close"] = pd.to_numeric(cb["value"], errors="coerce")
px = pd.concat([px[["time","ticker","Close"]], cb[["time","ticker","Close"]]], ignore_index=True)
P = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last")
P = P.reindex(DATES).ffill()

# --- HIEU CHINH CO SO GIA (bat buoc, KHONG phai tuy chon) ---
# BQ Close la gia dieu chinh NGUOC ve co so HOM NAY; engine chay theo point-in-time nen adj_price
# cua no lech theo ma/theo ky (LHG 2016: engine/BQ = 1,148). Dung chinh adj_price cua TX lam MOC,
# noi suy he so f=adj_price/Close theo thoi gian de MTM ve DUNG co so cua engine.
_tx0 = raw[(raw.record_type == "TX") & (raw.ticker != PARK_TK)].copy()
_tx0["adj_price"] = pd.to_numeric(_tx0.adj_price, errors="coerce")
_anch = _tx0.groupby(["ticker", "time"]).adj_price.median().reset_index()
_anch = _anch[_anch.ticker.isin(P.columns)]
F = pd.DataFrame(np.nan, index=P.index, columns=P.columns)
for tk, g in _anch.groupby("ticker"):
    ser = pd.Series(g.adj_price.values, index=g.time.values).reindex(P.index)
    F[tk] = (ser / P[tk]).astype(float)
F = F.interpolate(limit_direction="both").fillna(1.0).replace([np.inf, -np.inf], 1.0)
F = F.clip(0.2, 5.0)
P = P * F
P[PARK_TK] = P[PARK_TK] / F[PARK_TK] if PARK_TK in F.columns else P[PARK_TK]
print(f"[data] price matrix {P.shape} | he so hieu chinh: median {np.nanmedian(F.values):.4f} "
      f"p1 {np.nanpercentile(F.values,1):.3f} p99 {np.nanpercentile(F.values,99):.3f}")

# ---- ledger BAL
tx = raw[(raw.record_type == "TX") & (raw.book == "BAL")].copy()
for c in ["shares","adj_price","buy_amount","sell_amount","fee"]:
    tx[c] = pd.to_numeric(tx[c], errors="coerce").fillna(0.0)
tx = tx.sort_values(["time","holding_id"]).reset_index(drop=True)
tx["di"] = tx.time.map(lambda t: DIDX.get(t, len(DATES) - 1))   # MTM 06-19 > phien cuoi -> gan cuoi
FEE_BUY  = float((tx[(tx.action=="buy")  & (tx.buy_amount  > 0)].fee / tx[(tx.action=="buy")  & (tx.buy_amount>0)].buy_amount).median())
FEE_SELL = float((tx[(tx.action=="sell") & (tx.sell_amount > 0)].fee / tx[(tx.action=="sell") & (tx.sell_amount>0)].sell_amount).median())
print(f"[fee] median empirical BAL: buy {FEE_BUY:.5f}  sell {FEE_SELL:.5f}  (dung cho MOI variant, khong uu ai)")

NAV0 = float(d.nav_bal_ref.iloc[0])

def run_ledger(early_exit=None):
    """early_exit: dict holding_id -> di (phien thuc thi ban som). Tien thu ve NAM YEN 0%/nam."""
    early_exit = early_exit or {}
    cash = NAV0
    pos = {}                      # holding_id -> [ticker, shares]
    nav = np.zeros(len(DATES))
    k = 0
    n_tx = len(tx)
    rows = tx.to_dict("records")
    for i in range(len(DATES)):
        # 1) ban som (uu tien: neu holding co lenh exit som tai phien nay)
        for hid in [h for h, dd in early_exit.items() if dd == i and h in pos]:
            tk, sh = pos.pop(hid)
            p = P[tk].iloc[i]
            if not np.isfinite(p):
                pos[hid] = [tk, sh]; continue
            amt = sh * p
            cash += amt - amt * FEE_SELL
        # 2) TX goc cua phien
        while k < n_tx and rows[k]["di"] == i:
            r = rows[k]; k += 1
            hid = r["holding_id"]
            if r["action"] == "buy":
                if hid in early_exit and early_exit[hid] <= i:
                    continue        # da thoat -> khong nap them
                cash -= r["buy_amount"] + r["fee"]
                if hid in pos: pos[hid][1] += r["shares"]
                else: pos[hid] = [r["ticker"], r["shares"]]
            else:
                if hid not in pos:  # da ban som roi
                    continue
                sh = min(r["shares"], pos[hid][1])
                # scale tien theo ty le co phieu con lai (thuong = 1.0)
                f = sh / r["shares"] if r["shares"] > 0 else 0.0
                cash += r["sell_amount"] * f - r["fee"] * f
                pos[hid][1] -= sh
                if pos[hid][1] <= 1e-9: pos.pop(hid)
        # 3) MTM
        mv = 0.0
        for hid, (tk, sh) in pos.items():
            p = P[tk].iloc[i]
            if np.isfinite(p): mv += sh * p
        nav[i] = cash + mv
    return pd.Series(nav, index=DATES)

base = run_ledger()
ref = d.set_index("time").nav_bal_ref
err = (base - ref).abs()
rel = (err / ref).max()
print(f"[selfcheck] tai dung NAV BAL vs nav_bal_ref: max |sai so| = {err.max():,.0f} VND "
      f"({rel*100:.4f}% NAV) | cuoi ky tai dung {base.iloc[-1]:,.0f} vs pin {ref.iloc[-1]:,.0f}")

# ---- trang thai
state = d.set_index("time").state.astype(int)
b = pd.read_csv(os.path.join(OUT, "b1_base.csv"), parse_dates=["time"]).set_index("time").state
bstate = b.reindex(DATES).ffill()
# Variant A: committed downgrade
downA = (state.diff() < 0)
# Variant B: candidate streak XUONG = so phien lien tiep BASE < COMMITTED (xap xi tho)
below = (bstate < state).astype(int)
streak = np.zeros(len(DATES), int)
for i in range(len(DATES)):
    streak[i] = streak[i-1] + 1 if (i > 0 and below.iloc[i]) else int(below.iloc[i])
streak = pd.Series(streak, index=DATES)
print(f"[state] downgrade committed: {int(downA.sum())} phien | phien BASE<COMMITTED: {int(below.sum())} "
      f"| streak>=10: {int((streak>=10).sum())} phien")

# ---- holdings BAL khong-park, exit theo luat hold45/stop
hold = []
for hid, g in tx.groupby("holding_id"):
    pt = g.play_type.iloc[0]
    if pt == "ETF_PARK":  continue
    bs = g[g.action == "buy"]; ss = g[g.action == "sell"]
    if len(bs) == 0 or len(ss) == 0: continue
    ent = int(bs.di.min()); ex = int(ss.di.max())
    hold.append(dict(hid=hid, ticker=g.ticker.iloc[0], play=pt, ent=ent, ex=ex,
                     reason=ss.reason.iloc[-1], shares=float(bs.shares.sum())))
H = pd.DataFrame(hold)
print(f"[holdings] BAL non-park: {len(H)} | reason: {dict(H.reason.value_counts())}")

def triggers(mask, K=1):
    """tra dict hid->di thuc thi (T+1 sau phien trigger), chi lay trigger DAU TIEN trong hold window."""
    out, ev = {}, []
    m = mask.values
    for r in H.itertuples():
        lo, hi = r.ent + 1, r.ex          # trigger phai nam TRONG hold window
        idx = [i for i in range(lo, min(hi, len(DATES)-1)) if m[i]]
        if not idx: continue
        t0 = idx[0]; ex_i = t0 + 1        # T+1, khong nhin truoc
        if ex_i >= r.ex: continue         # khong som hon exit goc -> bo
        out[r.hid] = ex_i
        p0 = P[r.ticker].iloc[ex_i]; p1 = P[r.ticker].iloc[r.ex]
        if np.isfinite(p0) and np.isfinite(p1) and p0 > 0:
            ev.append(dict(hid=r.hid, ticker=r.ticker, play=r.play, reason=r.reason,
                           trig=DATES[t0], exec_=DATES[ex_i], orig=DATES[r.ex],
                           days_saved=r.ex - ex_i, r_avoided=p1/p0 - 1.0))
    return out, pd.DataFrame(ev)

eeA, evA = triggers(downA)
eeB, evB = triggers(streak >= 10)
print(f"[trigger] A (committed downgrade): {len(eeA)} vi the | B (streak>=10): {len(eeB)} vi the")

navA = run_ledger(eeA)
navB = run_ledger(eeB)

# ---- metric
def metrics(nav, lo=None, hi=None):
    s = nav.copy()
    if lo is not None: s = s[s.index >= lo]
    if hi is not None: s = s[s.index <= hi]
    s = s / s.iloc[0]
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = s.iloc[-1] ** (1/yrs) - 1
    r = s.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(SPY) if r.std() > 0 else np.nan
    dd = (s / s.cummax() - 1).min()
    return dict(CAGR=cagr, Sharpe=sh, MaxDD=dd, Calmar=cagr/abs(dd) if dd < 0 else np.nan)

WIN = [("FULL", None, None),
       ("IS 2014-2019", "2014-01-01", "2019-12-31"),
       ("OOS 2020-2026", "2020-01-01", None)]
rows = []
for wn, lo, hi in WIN:
    for name, nv in [("BAL_goc", base), ("variant_A", navA), ("variant_B", navB)]:
        m = metrics(nv, lo, hi); m.update(window=wn, variant=name); rows.append(m)
T = pd.DataFrame(rows)[["window","variant","CAGR","Sharpe","MaxDD","Calmar"]]
print("\n=== B1 bang chinh ===")
for wn, _, _ in WIN:
    g = T[T.window == wn]
    print(f"\n-- {wn}")
    for r in g.itertuples():
        print(f"   {r.variant:<10} CAGR {r.CAGR*100:7.2f}%  Sharpe {r.Sharpe:5.2f}  "
              f"MaxDD {r.MaxDD*100:7.2f}%  Calmar {r.Calmar:5.2f}")
T.to_csv(os.path.join(OUT, "b1_metrics.csv"), index=False)

# ---- test su kien: r_avoided co AM co y nghia khong (cum theo ngay trigger = episode)
def event_test(ev, tag):
    if len(ev) == 0:
        print(f"[event {tag}] rong"); return {}
    ep = ev.groupby("trig").r_avoided.mean()
    n_ep = len(ep)
    rng = np.random.default_rng(7)
    bs = [rng.choice(ep.values, n_ep, replace=True).mean() for _ in range(10000)]
    p = 2 * min((np.array(bs) >= 0).mean(), (np.array(bs) <= 0).mean())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"[event {tag}] n_vithe={len(ev)} n_episode={n_ep} | mean r_avoided (episode-lvl) "
          f"{ep.mean()*100:+.2f}% CI[{lo*100:+.2f};{hi*100:+.2f}] p={p:.3f} | median {ev.r_avoided.median()*100:+.2f}%")
    # LOO theo nam
    ev2 = ev.copy(); ev2["yr"] = ev2.trig.dt.year
    loo = []
    for y in sorted(ev2.yr.unique()):
        sub = ev2[ev2.yr != y].groupby("trig").r_avoided.mean()
        loo.append((y, sub.mean()))
    print(f"[event {tag}] LOO theo nam (mean episode khi BO nam do): " +
          "  ".join(f"{y}:{v*100:+.1f}%" for y, v in loo))
    return dict(n=len(ev), n_ep=n_ep, mean=ep.mean(), ci=[lo, hi], p=p, loo=loo)

resA = event_test(evA, "A")
resB = event_test(evB, "B")
for nm, e in [("A", evA), ("B", evB)]:
    if len(e): e.to_csv(os.path.join(OUT, f"b1_events_{nm}.csv"), index=False)

# ---- per-year CAGR delta
py = []
for y in range(2014, 2027):
    lo, hi = f"{y}-01-01", f"{y}-12-31"
    try:
        mb = metrics(base, lo, hi); ma = metrics(navA, lo, hi); mbv = metrics(navB, lo, hi)
        py.append(dict(year=y, base=mb["CAGR"], A=ma["CAGR"], B=mbv["CAGR"],
                       dA=ma["CAGR"]-mb["CAGR"], dB=mbv["CAGR"]-mb["CAGR"],
                       dd_base=mb["MaxDD"], dd_A=ma["MaxDD"], dd_B=mbv["MaxDD"]))
    except Exception:
        pass
PY = pd.DataFrame(py); PY.to_csv(os.path.join(OUT, "b1_peryear.csv"), index=False)
print("\n=== per-year (CAGR trong nam, delta so voi goc) ===")
for r in PY.itertuples():
    print(f"  {r.year}  base {r.base*100:7.2f}%  A {r.A*100:7.2f}% ({r.dA*100:+6.2f}pp)  "
          f"B {r.B*100:7.2f}% ({r.dB*100:+6.2f}pp) | DD base {r.dd_base*100:6.1f}% A {r.dd_A*100:6.1f}% B {r.dd_B*100:6.1f}%")

json.dump(dict(fee_buy=FEE_BUY, fee_sell=FEE_SELL, selfcheck_max_abs_err=float(err.max()),
               selfcheck_max_rel=float(rel), nA=len(eeA), nB=len(eeB),
               eventA={k: (v if not isinstance(v, (list, np.ndarray)) else list(map(float, v)))
                       for k, v in resA.items() if k != "loo"},
               eventB={k: (v if not isinstance(v, (list, np.ndarray)) else list(map(float, v)))
                       for k, v in resB.items() if k != "loo"}),
          open(os.path.join(OUT, "b1_summary.json"), "w"), default=float, indent=1)
print("\n[done] b1_metrics.csv / b1_peryear.csv / b1_events_*.csv / b1_summary.json")
