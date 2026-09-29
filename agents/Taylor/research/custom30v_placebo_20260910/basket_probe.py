# -*- coding: utf-8 -*-
"""VONG 5 — do TRUC TIEP tren ro (build_pit), khong chay NAV: fincount/ky, trong so tai chinh theo
NGAY, ADV ro. Tai dung vong lap trong so cua build_pit y het Phan 0 vong 4 (co selfcheck vs lvl).
PAPER-ONLY. Chay: $DNA_PYEXE basket_probe.py <leg> [<leg> ...]"""
import os, sys, bisect
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/research/custom30v_placebo_20260910")
sys.path.insert(0, OUT)          # ban copy custom_basket.py cua thu muc nay (bay vong 2)
sys.path.insert(1, WORKDIR)
os.chdir(WORKDIR)
os.environ["BQ_CACHE_THREADS"] = "1"
# GAN CUNG, khong setdefault: wc_env.sh export BQ_LOCAL_CACHE=data/bq_cache (cache SONG, cron ghi
# lai 23:45 ICT moi ngay) => setdefault khong ghi de duoc va probe doc nham cache song. Da can
# thuc te 2026-09-10: chuoi loi suat gross tai lap khong on dinh giua 2 lan chay. Snapshot ghim la
# DUY NHAT hop le o day vi chan NAV day du deu chay tren no.
os.environ["BQ_LOCAL_CACHE"] = "data/bq_cache_asof20260729_postrestate"
os.environ["LAG_ADV_BASIS"] = "price"
os.environ["BASKET_SELECT"] = "yieldcombo"
from simulate_holistic_nav import bq
print("[probe] BQ_LOCAL_CACHE =", os.environ["BQ_LOCAL_CACHE"], flush=True)
import custom_basket as cb
assert os.path.dirname(os.path.abspath(cb.__file__)) == OUT, f"WRONG custom_basket: {cb.__file__}"

START, END = "2014-01-02", "2026-06-19"
CFG = {   # leg -> (pool, placebo_env_or_None, mode)
    "ctrl": ("60",  None,                          "random"),
    "L1b":  ("120", None,                          "random"),
    "P1d":  ("60",  f"0:{OUT}/fincount_L1b.csv",   "top"),
    "P2d":  ("120", f"0:{OUT}/fincount_ctrl.csv",  "top"),
    "P1r1": ("60",  f"101:{OUT}/fincount_L1b.csv", "random"),
    "P1r2": ("60",  f"202:{OUT}/fincount_L1b.csv", "random"),
    "P2r1": ("120", f"101:{OUT}/fincount_ctrl.csv","random"),
    "P2r2": ("120", f"202:{OUT}/fincount_ctrl.csv","random"),
}
FIN = {"BANK", "INSURANCE", "SECURITIES"}
vp = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"],
                 usecols=["ticker", "time", "route"])
vp["q"] = vp["time"].dt.to_period("Q").dt.start_time
_rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker", "q"])["route"].last()
_rh = {tk: (list(g.index.get_level_values(1)), list(g.values)) for tk, g in _rt.groupby(level=0)}
def route_asof(tk, q):     # quy uoc DO (nhu analyze.py vong 4): bisect as-of
    e = _rh.get(tk)
    if not e: return "UNKNOWN"
    i = bisect.bisect_right(e[0], pd.Timestamp(q)) - 1
    return e[1][i] if i >= 0 else e[1][0]

for leg in sys.argv[1:]:
    pool, plac, mode = CFG[leg]
    os.environ["BASKET_CFO_POOL"] = pool
    os.environ["BASKET_PLACEBO_MODE"] = mode
    os.environ["BASKET_FINCOUNT_DUMP"] = f"{OUT}/fincount_probe_{leg}.csv"
    if plac: os.environ["BASKET_PLACEBO_FIN"] = plac
    else:    os.environ.pop("BASKET_PLACEBO_FIN", None)
    print(f"\n===== probe {leg}: pool={pool} placebo={plac} mode={mode} =====", flush=True)
    lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                       gate_rating=3, weight_scheme="namecap")
    memdf["rebal_date"] = pd.to_datetime(memdf["rebal_date"]); bx["time"] = pd.to_datetime(bx["time"])
    memdf.to_csv(f"{OUT}/members_{leg}.csv", index=False)
    # ---- tai lap vong lap trong so hang ngay (copy tu build_pit, KHONG sua) ----
    mcap  = bx.pivot_table(index="time", columns="ticker", values="mcap").sort_index()
    mcapw = bx.pivot_table(index="time", columns="ticker", values="mcapw").reindex(
                index=mcap.index, columns=mcap.columns)
    members = {d: [(r.ticker, r.qmult) for r in g.itertuples()] for d, g in memdf.groupby("rebal_date")}
    reb = sorted(members); prev = None; rows = []; ret_s = {}
    for d in mcap.index:
        if d > pd.Timestamp(END): break
        i = bisect.bisect_right(reb, d) - 1
        aq = reb[i] if i >= 0 else None
        if aq is None or prev is None: prev = d; continue
        mem = members.get(aq, [])
        tks = [t for t, _ in mem if t in mcap.columns]
        w = np.array([qm for t, qm in mem if t in mcap.columns])
        today = mcap.loc[d, tks].values.astype(float); yest = mcap.loc[prev, tks].values.astype(float)
        yestw = mcapw.loc[prev, tks].values.astype(float)
        valid = ~np.isnan(today) & ~np.isnan(yest); r_d = 0.0
        if valid.sum() > 0:
            yv = yest[valid]; yvw = np.where(np.isnan(yestw[valid]), yv, yestw[valid])
            r = today[valid] / yv - 1.0
            base = yvw * w[valid]; W = base / base.sum() if base.sum() > 0 else base
            W = cb._cap_names(W, 0.10); r_d = float(np.nansum(W * r))
            for t, wi in zip([t for t, ok in zip(tks, valid) if ok], W):
                rows.append((d, aq, t, float(wi)))
        ret_s[d] = r_d; prev = d
    ret = pd.Series(ret_s).sort_index()
    ret = ret[(ret.index >= pd.Timestamp(START)) & (ret.index <= pd.Timestamp(END))]
    lv = (1 + ret).cumprod()
    _l = pd.Series(lvl); _l.index = pd.to_datetime(_l.index)
    _l = _l[(_l.index >= ret.index[0]) & (_l.index <= ret.index[-1])]
    chk = float(np.abs((lv / lv.iloc[0]) / (_l / _l.iloc[0]) - 1).max())
    print(f"  [selfcheck trong so] max|sai lech tuong doi| vs lvl build_pit = {chk:.3e} "
          f"{'OK' if chk < 1e-9 else '*** LECH ***'}")
    W = pd.DataFrame(rows, columns=["time", "rebal_date", "ticker", "w"])
    W["q"] = W["time"].dt.to_period("Q").dt.start_time
    k = W[["ticker", "q"]].drop_duplicates(); k["route"] = [route_asof(t, q) for t, q in zip(k.ticker, k.q)]
    W = W.merge(k, on=["ticker", "q"], how="left")
    fw = W.assign(f=W.route.isin(FIN)).groupby("time").apply(lambda g: (g.w * g.f).sum() / g.w.sum())
    bw = W.assign(b=W.route == "BANK").groupby("time").apply(lambda g: (g.w * g.b).sum() / g.w.sum())
    pd.DataFrame({"fin_w": fw, "bank_w": bw}).to_csv(f"{OUT}/dailyw_{leg}.csv")
    ret.to_csv(f"{OUT}/basketret_{leg}.csv", header=["ret"])
    _dd = float((lv / lv.cummax() - 1).min())
    print(f"  [{leg}] RO GROSS: MaxDD {_dd*100:.2f}%  vol {ret.std()*np.sqrt(252)*100:.1f}%  "
          f"Sharpe {ret.mean()/ret.std()*np.sqrt(252):.2f}")
    a = pd.Series(adv).dropna()
    print(f"  [{leg}] ADV median {a.median()/1e9:,.1f}B/day -> park 20% = {a.median()*0.2/1e9:,.1f}B/day"
          f" | fin_w mean {fw.mean()*100:.2f}% (OOS {fw[fw.index>='2020-01-01'].mean()*100:.2f}%)"
          f" | bank_w mean {bw.mean()*100:.2f}%"
          f" | level {float(lv.iloc[-1]):.4f}x  CAGR_ro {(float(lv.iloc[-1])**(365.25/((ret.index[-1]-ret.index[0]).days))-1)*100:.2f}%",
          flush=True)
print("\nPROBE DONE")
