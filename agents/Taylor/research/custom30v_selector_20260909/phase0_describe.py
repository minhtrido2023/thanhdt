# -*- coding: utf-8 -*-
"""Phase 0 — mo ta dinh luong ro custom30V (PAPER-ONLY, khong sua production).
Tai lap CHINH XAC selector production (papertrade_daily.sh [6b]):
  BASKET_SELECT=yieldcombo, top_n=30, quality=none, rebal=q2m5, gate_rating=3,
  weight_scheme=namecap, name_cap=0.10  -> custom_basket.build_pit
Roi tai dung vong lap trong so hang ngay cua build_pit de lay W_i(d) chinh xac,
tu do phan ra dong gop theo ten / nganh / nam / state DT5G + phan phoi vi the.
"""
import os, sys, bisect, json
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/research/custom30v_selector_20260909")
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
os.environ.setdefault("BQ_CACHE_THREADS", "1")
os.environ["BASKET_SELECT"] = "yieldcombo"          # production selector
from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-02", "2026-06-19"             # AUDIT_END pin cua ho R3
print(f"[build_pit] yieldcombo namecap0.10 top30 gate3 q2m5 {START}->{END}")
lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                   gate_rating=3, weight_scheme="namecap")
memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"])
bx["time"] = pd.to_datetime(bx["time"])
memdf.to_csv(f"{OUT}/members.csv", index=False)

# ---- tai lap vong lap trong so hang ngay (copy tu build_pit, khong sua) -------------
mcap  = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
mcapw = bx.pivot_table(index="time", columns="ticker", values="mcapw").reindex(
            index=mcap.index, columns=mcap.columns)
members = {d: [(r.ticker, r.qmult) for r in g.itertuples()]
           for d, g in memdf.groupby("rebal_date")}
reb = sorted(members.keys())
idx_dates = [d for d in mcap.index if d >= pd.Timestamp(START) and d <= pd.Timestamp(END)]
def active_q(d):
    i = bisect.bisect_right(reb, d) - 1
    return reb[i] if i >= 0 else None

rows = []            # dong gop tung ten tung ngay
ret_s = {}
prev = None
for d in mcap.index:
    if d > pd.Timestamp(END): break
    aq = active_q(d)
    if aq is None or prev is None:
        prev = d; continue
    mem = members.get(aq, [])
    tks = [t for t, _ in mem if t in mcap.columns]
    w   = np.array([qm for t, qm in mem if t in mcap.columns])
    today = mcap.loc[d, tks].values.astype(float)
    yest  = mcap.loc[prev, tks].values.astype(float)
    yestw = mcapw.loc[prev, tks].values.astype(float)
    valid = ~np.isnan(today) & ~np.isnan(yest)
    r_d = 0.0
    if valid.sum() > 0:
        yv = yest[valid]; yvw = np.where(np.isnan(yestw[valid]), yv, yestw[valid])
        r = today[valid] / yv - 1.0
        base = yvw * w[valid]
        W = base / base.sum() if base.sum() > 0 else base
        W = cb._cap_names(W, 0.10)
        r_d = float(np.nansum(W * r))
        vt = [t for t, ok in zip(tks, valid) if ok]
        for t, wi, ri in zip(vt, W, r):
            rows.append((d, aq, t, float(wi), float(ri)))
    ret_s[d] = r_d
    prev = d

ret = pd.Series(ret_s).sort_index()
ret = ret[(ret.index >= pd.Timestamp(START)) & (ret.index <= pd.Timestamp(END))]
lv = (1.0 + ret).cumprod()
# doi chung voi lvl cua build_pit (phai trung)
_l = pd.Series(lvl); _l.index = pd.to_datetime(_l.index)
_l = _l[(_l.index >= ret.index[0]) & (_l.index <= ret.index[-1])]
_chk = (lv / lv.iloc[0]) / (_l / _l.iloc[0]) - 1.0
print(f"[selfcheck] tai lap chuoi loi suat: max|sai lech tuong doi| = {np.abs(_chk).max():.3e}")

D = pd.DataFrame(rows, columns=["time", "rebal_date", "ticker", "w", "r"])
D["lvl_prev"] = D["time"].map((lv.shift(1).fillna(1.0)).to_dict())
D["contrib"] = D["lvl_prev"] * D["w"] * D["r"]        # dong gop theo diem chi so (cong don = lv_end - 1)
D.to_parquet(f"{OUT}/daily_contrib.parquet")
print(f"[check] sum contrib {D.contrib.sum():.6f} vs lv_end-1 {lv.iloc[-1]-1:.6f}")
ret.to_csv(f"{OUT}/basket_daily_return.csv", header=["ret"])
print("PHASE0 core done:", len(ret), "phien,", len(reb), "rebal, level", round(float(lv.iloc[-1]), 4))
