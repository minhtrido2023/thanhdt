#!/usr/bin/env python
"""B3 — CAPIT x Value-Radar band guard (radar<20 => size x0.5). Job Taylor_20260822_141143. PAPER-ONLY.

Nguon: pin R3 2026-08-03 (EVENT_CAPIT 18 dong + TX play_type CAPITB_E<n>/CAPITL_E<n>),
panel_daily.csv (radar score CANONICAL DISPLAY-ONLY, value_radar.load_series), tav2_bq.ticker Close.
Hieu chinh co so gia bang moc adj_price cua TX (bai hoc B1 — BAT BUOC, xem b1 report).
KHONG dung cot profit_*.
"""
import os, sys
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, W)
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
PIN = os.path.join(W, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")
SPY = 249.2785102175346; PARK_TK = "CUSTOM_VN30EXVIC_PITG"; BAND = 20.0
COLS = ["record_type","key","value","ymd","book","ticker","action","play_type","holding_id",
        "shares","adj_price","buy_amount","sell_amount","fee","cash_after","reason","state",
        "nav_bal_ref","nav_lag_ref","bal_cash_ref","bal_stocks_ref","bal_etf_ref","lag_cash_ref",
        "lag_stocks_ref","lag_etf_ref","w_lag_tgt","rebal_cost","cap_bal","cap_lag",
        "combined_nav","vni_close"]

raw = pd.read_csv(PIN, names=COLS, header=0, low_memory=False)
raw["time"] = pd.to_datetime(raw["ymd"], format="ISO8601")
pan = pd.read_csv(os.path.join(OUT, "panel_daily.csv"), parse_dates=["time"])
DATES = list(pan.time); DIDX = {t: i for i, t in enumerate(DATES)}

# ---------------------------------------------------------------- 1. su kien CAPIT + radar score
ev = raw[raw.record_type == "EVENT_CAPIT"][["time","value","reason","state"]].copy()
ev["size"] = pd.to_numeric(ev.value, errors="coerce")
ev = ev.sort_values("time").reset_index(drop=True)
ev["eidx"] = ev.index
ev = ev.merge(pan[["time","score","zone","regime","r_comb","r_vni"]].drop(columns=["r_comb","r_vni"]),
              on="time", how="left")
print(f"[events] {len(ev)} EVENT_CAPIT | size>0: {int((ev['size']>0).sum())} | radar NaN: {int(ev.score.isna().sum())}")
ev["guard"] = np.where(ev.score < BAND, "radar<20", "radar>=20")

# forward return tu NGAY FIRE (T+1, khong nhin truoc)
for col in ["r_comb","r_vni","r_bal","r_lag"]:
    pan[col] = pd.to_numeric(pan[col], errors="coerce")
def fwd(t, col, h):
    i = DIDX[t]
    seg = pan[col].iloc[i+1:i+1+h]
    if len(seg) < h: return np.nan
    return float((1+seg.fillna(0)).prod() - 1)
for h in (60, 120, 250):
    for col, nm in [("r_comb","COMB"),("r_vni","VNI")]:
        ev[f"{nm}_{h}"] = [fwd(t, col, h) for t in ev.time]
    ev[f"EX_{h}"] = ev[f"COMB_{h}"] - ev[f"VNI_{h}"]
ev.to_csv(os.path.join(OUT, "b3_events.csv"), index=False)

pd.set_option("display.width", 220, "display.max_columns", 30)
print("\n=========== 18 su kien CAPIT + radar score tai ngay fire ===========")
print(f"{'#':>2s} {'ngay':10s} {'size':>5s} {'regime':8s} {'zone':10s} {'radar':>6s} {'guard':9s} "
      f"{'C60':>7s} {'C120':>7s} {'C250':>7s} {'EX60':>7s} {'EX250':>7s}")
def pc(x): return "  n/a " if pd.isna(x) else f"{100*x:+6.1f}"
for r in ev.itertuples():
    print(f"{r.eidx:2d} {str(r.time.date()):10s} {r._2 if False else r.size:5.3f} {str(r.regime):8s} "
          f"{str(r.zone):10s} {r.score:6.1f} {r.guard:9s} "
          f"{pc(getattr(r,'COMB_60'))} {pc(getattr(r,'COMB_120'))} {pc(getattr(r,'COMB_250'))} "
          f"{pc(getattr(r,'EX_60'))} {pc(getattr(r,'EX_250'))}")

# ---------------------------------------------------------------- 2. 2 nhom
print("\n=========== NHOM radar<20 vs radar>=20 (chi su kien size>0) ===========")
fired = ev[ev["size"] > 0].copy()
print(f"  su kien fire that: {len(fired)} (2 su kien size=0 la GATE tu choi dung, khong tinh)")
rows = []
for g, sub in fired.groupby("guard"):
    rec = dict(guard=g, n=len(sub), size_mean=sub["size"].mean(), radar_mean=sub.score.mean(),
               dates=", ".join(str(t.date()) for t in sub.time))
    for h in (60, 120, 250):
        for nm in ("COMB","VNI","EX"):
            v = sub[f"{nm}_{h}"].dropna()
            rec[f"{nm}_{h}_med"] = v.median() if len(v) else np.nan
            rec[f"{nm}_{h}_mean"] = v.mean() if len(v) else np.nan
            rec[f"{nm}_{h}_min"] = v.min() if len(v) else np.nan
            rec[f"{nm}_{h}_max"] = v.max() if len(v) else np.nan
            rec[f"{nm}_{h}_n"] = len(v)
    rows.append(rec)
G = pd.DataFrame(rows); G.to_csv(os.path.join(OUT, "b3_groups.csv"), index=False)
for r in G.itertuples():
    print(f"\n  --- {r.guard}  n={r.n}  size TB={r.size_mean:.3f}  radar TB={r.radar_mean:.1f}")
    print(f"      ngay: {r.dates}")
    for h in (60, 120, 250):
        print(f"      h={h:3d}  COMB median {pc(getattr(r,f'COMB_{h}_med'))} mean {pc(getattr(r,f'COMB_{h}_mean'))} "
              f"[{pc(getattr(r,f'COMB_{h}_min'))};{pc(getattr(r,f'COMB_{h}_max'))}] n={getattr(r,f'COMB_{h}_n'):.0f} | "
              f"EXCESS median {pc(getattr(r,f'EX_{h}_med'))} mean {pc(getattr(r,f'EX_{h}_mean'))}")

# permutation test: hieu median giua 2 nhom co the do ngau nhien khong?
print("\n=========== PERMUTATION TEST (N nho — chi de biet 'co the do ngau nhien khong') ===========")
rng = np.random.default_rng(3)
for h in (60, 120, 250):
    for nm in ("COMB","EX"):
        s = fired[["guard", f"{nm}_{h}"]].dropna()
        if s.guard.nunique() < 2: continue
        a = s[s.guard == "radar<20"][f"{nm}_{h}"].to_numpy()
        b = s[s.guard == "radar>=20"][f"{nm}_{h}"].to_numpy()
        obs = np.median(a) - np.median(b)
        pool = np.concatenate([a, b]); na = len(a)
        perm = np.empty(20000)
        for i in range(20000):
            p = rng.permutation(pool); perm[i] = np.median(p[:na]) - np.median(p[na:])
        pv = float((np.abs(perm) >= abs(obs)).mean())
        print(f"  h={h:3d} {nm:4s}: median(radar<20)-median(radar>=20) = {100*obs:+6.1f}pp  "
              f"n={len(a)}/{len(b)}  p_perm={pv:.3f}")

# ---------------------------------------------------------------- 3. NAV gia dinh: half-size khi radar<20
guard_ev = set(ev[(ev.score < BAND) & (ev["size"] > 0)].eidx)
print(f"\n=========== NAV gia dinh: HALF-SIZE cho {len(guard_ev)} su kien radar<20 (E{sorted(guard_ev)}) ===========")

px = pd.read_csv(os.path.join(OUT, "b3_px.csv"), parse_dates=["time"])
cb = raw[raw.record_type == "CUSTOM_BASKET"][["time","ticker","value"]].copy()
cb["Close"] = pd.to_numeric(cb["value"], errors="coerce")
P = pd.concat([px[["time","ticker","Close"]], cb[["time","ticker","Close"]]]) \
      .pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").reindex(DATES).ffill()
_t0 = raw[(raw.record_type == "TX") & (raw.ticker != PARK_TK)].copy()
_t0["adj_price"] = pd.to_numeric(_t0.adj_price, errors="coerce")
_a = _t0.groupby(["ticker","time"]).adj_price.median().reset_index()
_a = _a[_a.ticker.isin(P.columns)]
F = pd.DataFrame(np.nan, index=P.index, columns=P.columns)
for tk, g in _a.groupby("ticker"):
    F[tk] = (pd.Series(g.adj_price.values, index=g.time.values).reindex(P.index) / P[tk]).astype(float)
F = F.interpolate(limit_direction="both").fillna(1.0).replace([np.inf,-np.inf],1.0).clip(0.2, 5.0)
Pc = P * F
Pc[PARK_TK] = P[PARK_TK]
print(f"[gia] {Pc.shape} | he so hieu chinh median {np.nanmedian(F.values):.4f}")

def ledger(book, nav0, scale=None):
    """scale: dict play_type_prefix -> he so (0.5). Tien tiet kiem NAM YEN 0%."""
    scale = scale or {}
    tx = raw[(raw.record_type == "TX") & (raw.book == book)].copy()
    for c in ["shares","buy_amount","sell_amount","fee"]:
        tx[c] = pd.to_numeric(tx[c], errors="coerce").fillna(0.0)
    tx = tx.sort_values(["time","holding_id"]).reset_index(drop=True)
    tx["di"] = tx.time.map(lambda t: DIDX.get(t, len(DATES)-1))
    rows_ = tx.to_dict("records"); n = len(rows_); k = 0
    cash = nav0; pos = {}; nav = np.zeros(len(DATES)); frac = {}
    for i in range(len(DATES)):
        while k < n and rows_[k]["di"] == i:
            r = rows_[k]; k += 1
            hid = r["holding_id"]; pt = str(r["play_type"])
            f = scale.get(pt, 1.0)
            if r["action"] == "buy":
                frac[hid] = f
                cash -= (r["buy_amount"] + r["fee"]) * f
                if hid in pos: pos[hid][1] += r["shares"] * f
                else: pos[hid] = [r["ticker"], r["shares"] * f]
            else:
                if hid not in pos: continue
                f2 = frac.get(hid, 1.0)
                sh = min(r["shares"]*f2, pos[hid][1])
                g = sh / (r["shares"]*f2) if r["shares"]*f2 > 0 else 0.0
                cash += (r["sell_amount"] - r["fee"]) * f2 * g
                pos[hid][1] -= sh
                if pos[hid][1] <= 1e-9: pos.pop(hid)
        mv = 0.0
        for hid, (tk, sh) in pos.items():
            p = Pc[tk].iloc[i]
            if np.isfinite(p): mv += sh * p
        nav[i] = cash + mv
    return pd.Series(nav, index=DATES)

def M(s, lo=None, hi=None):
    x = s.copy()
    if lo: x = x[x.index >= lo]
    if hi: x = x[x.index <= hi]
    x = x / x.iloc[0]; yrs = (x.index[-1]-x.index[0]).days/365.25
    c = x.iloc[-1]**(1/yrs)-1; r = x.pct_change().dropna()
    dd = float((x/x.cummax()-1).min())
    return dict(CAGR=c, Sharpe=r.mean()/r.std()*np.sqrt(SPY), MaxDD=dd, Calmar=c/abs(dd))

SC = {}
for e in guard_ev:
    SC[f"CAPITB_E{e}"] = 0.5; SC[f"CAPITL_E{e}"] = 0.5
res = []
for book, nav0, refcol in [("BAL", 25e9, "nav_bal_ref"), ("LAG", 25e9, "nav_lag_ref")]:
    ref = pd.to_numeric(pan[refcol], errors="coerce"); ref.index = DATES
    b0 = ledger(book, nav0); b1 = ledger(book, nav0, SC)
    m_ref = M(ref); m0 = M(b0); m1 = M(b1)
    print(f"\n  [selfcheck {book}] tai dung vs pin: CAGR {100*m0['CAGR']:.2f}% vs {100*m_ref['CAGR']:.2f}% "
          f"| DD {100*m0['MaxDD']:.2f}% vs {100*m_ref['MaxDD']:.2f}% | NAV cuoi "
          f"{b0.iloc[-1]:,.0f} vs {ref.iloc[-1]:,.0f}")
    for wn, lo, hi in [("FULL",None,None),("IS 2014-2019","2014-01-01","2019-12-31"),("OOS 2020-2026","2020-01-01",None)]:
        a = M(b0, lo, hi); c = M(b1, lo, hi)
        res.append(dict(book=book, window=wn, variant="full_size", **a))
        res.append(dict(book=book, window=wn, variant="half_radar<20", **c))
        print(f"    {wn:14s} full  CAGR {100*a['CAGR']:6.2f}% DD {100*a['MaxDD']:7.2f}% Calmar {a['Calmar']:.2f}"
              f"  ||  guard CAGR {100*c['CAGR']:6.2f}% DD {100*c['MaxDD']:7.2f}% Calmar {c['Calmar']:.2f}"
              f"  || dCAGR {100*(c['CAGR']-a['CAGR']):+5.2f}pp dDD {100*(c['MaxDD']-a['MaxDD']):+5.2f}pp")
R = pd.DataFrame(res); R.to_csv(os.path.join(OUT, "b3_nav.csv"), index=False)
print("\n[done] b3_events.csv / b3_groups.csv / b3_nav.csv")
