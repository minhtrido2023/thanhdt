# -*- coding: utf-8 -*-
"""Chon muc STOP THAM HOA cho ORB VN30F (job Taylor_20261116_162132) theo TAN SUAT CHAM, KHONG theo PnL.

Config GIU NGUYEN orb_pt.py: sig = sign(close<=09:30 / close bar dau - 1); vao = close bar cuoi
<=09:30; thoat = close bar cuoi <=14:30 (doan FiinX: 14:29, vi vendor thu gon bar 14:30);
slip 1 tick/chieu + fee 0.6bps. Chi THEM stop: cham muc entry*(1 -/+ s) trong 09:31..14:30.

Nguon: (1) FiinX 2022-02-17..2023-09-08 per-day (chi co minlow29/maxhigh29 => chi do cham,
khong do gap); (2) vnstock 1m 2023-09-11..2026-09-25 (orb_core.load_bars) + (3) VCI 1m
2026-09-26..2026-11-16 (fetch_tail.py). (2)+(3) do theo TUNG BAR: fill stop = muc stop neu bar
mo cua chua vuot qua, nguoc lai = gia mo bar (gap qua stop).
N trial = so muc stop da thu = len(LEVELS). Lua chon theo tieu chi tan suat cham, khai bao TRUOC
khi in PnL: muc NHO NHAT co ti le cham <= 3% tren tape ghep (cau chi hiem).
"""
import sys, json, numpy as np, pandas as pd
RES = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research"
sys.path.insert(0, RES + "/orb_deployed_config_validation_20260925")
import orb_core
TICK, SLIP, FEE = 0.1, 1, 0.00006
LEVELS = [0.010, 0.015, 0.020, 0.025, 0.030, 0.040]
TARGET_HIT = 0.03

def bar_days():
    a = orb_core.load_bars()
    t = pd.read_csv("vn30f1m_tail_20260920_20261116.csv"); t["time"] = pd.to_datetime(t["time"])
    t = t[t["time"].dt.date > pd.Timestamp("2026-09-25").date()]
    t["date"] = t["time"].dt.date; t["hm"] = t["time"].dt.strftime("%H:%M")
    df = pd.concat([a[["time","open","high","low","close","date","hm"]], t[["time","open","high","low","close","date","hm"]]])
    out = []
    for d, g in df.groupby("date"):
        g = g.sort_values("time")
        op = g[g["hm"] <= "09:30"]; seg = g[(g["hm"] > "09:30") & (g["hm"] <= "14:30")]
        if not (len(op) >= 10 and len(seg) > 0 and g["hm"].iloc[-1] >= "14:25"):
            continue
        c0, e = float(g["close"].iloc[0]), float(op["close"].iloc[-1])
        s = int(np.sign(e / c0 - 1))
        if s == 0: continue
        adv = (seg["low"].values / e - 1) * -1 if s > 0 else (seg["high"].values / e - 1)
        out.append(dict(date=str(d), src="bars", sig=s, entry=e, exit=float(seg["close"].iloc[-1]),
                        mae=float(max(adv.max(), 0)), o=seg["open"].values, lo=seg["low"].values,
                        hi=seg["high"].values, hm=seg["hm"].values))
    return out

def fiinx_days():
    f = pd.read_csv(RES + "/orb_fiinx_vn30f1m_20260925/fiinx_daily_gap.csv")
    f = f[(f["nop"] >= 10) & (f["nseg29"] > 0) & (f["hmL"] >= "14:25")]
    out = []
    for _, r in f.iterrows():
        s = int(np.sign(r["entry"] / r["c_first"] - 1))
        if s == 0: continue
        mae = (1 - r["minlow29"] / r["entry"]) if s > 0 else (r["maxhigh29"] / r["entry"] - 1)
        out.append(dict(date=str(r["date"]), src="fiinx", sig=s, entry=float(r["entry"]),
                        exit=float(r["exit29"]), mae=float(max(mae, 0))))
    return out

def run(days, stop):
    nets, hits, gaps, hit_hm = [], 0, [], []
    for d in days:
        s, e, px = d["sig"], d["entry"], d["exit"]
        if stop is not None and d["mae"] >= stop:
            hits += 1
            lvl = e * (1 - s * stop)
            if d["src"] == "bars":
                for o, lo, hi, hm in zip(d["o"], d["lo"], d["hi"], d["hm"]):
                    touched = lo <= lvl if s > 0 else hi >= lvl
                    if touched:
                        gapped = (o < lvl) if s > 0 else (o > lvl)
                        px = o if gapped else lvl
                        gaps.append(s * (lvl - px) / e * 1e4)  # bps truot qua stop (>=0 la xau)
                        hit_hm.append(hm); break
            else:
                px = lvl
        ef = e + s * SLIP * TICK; xf = px - s * SLIP * TICK
        nets.append(s * (xf / ef - 1) - FEE)
    n = np.array(nets); nav = np.cumprod(1 + n); dd = (nav / np.maximum.accumulate(nav) - 1).min()
    return dict(n=len(n), hit=hits, hit_rate=hits / len(n), mean_bps=n.mean() * 1e4,
                sharpe=n.mean() / n.std() * np.sqrt(252), cum=nav[-1] - 1, maxdd=dd,
                worst_bps=n.min() * 1e4, p01_bps=np.percentile(n, 1) * 1e4,
                gap_n=int(sum(g > 0 for g in gaps)), gap_max_bps=max(gaps) if gaps else 0.0,
                gap_mean_bps=float(np.mean(gaps)) if gaps else 0.0, hit_hm=hit_hm)

B, F = bar_days(), fiinx_days()
ALL = sorted(F + B, key=lambda d: d["date"])
mae = np.array([d["mae"] for d in ALL])
print(f"Tape ghep: {len(ALL)} trade {ALL[0]['date']}..{ALL[-1]['date']} (FiinX {len(F)}, bar {len(B)})")
print("MAE trong phien (% tu gia vao): " + " ".join(f"p{q}={np.percentile(mae,q)*100:.2f}%" for q in (50,75,90,95,97,99)) + f" max={mae.max()*100:.2f}%")
top = sorted(ALL, key=lambda d: -d["mae"])[:8]
print("8 phien MAE lon nhat: " + ", ".join(f"{d['date']} {d['mae']*100:.2f}%" for d in top))
res = {"n_trials": len(LEVELS), "levels": LEVELS, "target_hit": TARGET_HIT, "rows": []}
base = {k: run(seg, None) for k, seg in (("all", ALL), ("fiinx", F), ("bars", B))}
print(f"\n{'stop':>6} {'hit_all':>8} {'hit_22-23':>9} {'hit_23-26':>9} {'gap_n':>5} {'gapmax':>7} | {'mean':>6} {'Sh':>5} {'cum':>7} {'MaxDD':>7} {'worst':>7}")
print(f"{'none':>6} {'-':>8} {'-':>9} {'-':>9} {'-':>5} {'-':>7} | {base['all']['mean_bps']:6.2f} {base['all']['sharpe']:5.2f} {base['all']['cum']*100:6.1f}% {base['all']['maxdd']*100:6.1f}% {base['all']['worst_bps']:7.0f}")
chosen = None
for s in LEVELS:
    a, f, b = run(ALL, s), run(F, s), run(B, s)
    if chosen is None and a["hit_rate"] <= TARGET_HIT: chosen = s
    print(f"{s*100:5.1f}% {a['hit_rate']*100:7.2f}% {f['hit_rate']*100:8.2f}% {b['hit_rate']*100:8.2f}% {b['gap_n']:5d} {b['gap_max_bps']:6.1f}b | {a['mean_bps']:6.2f} {a['sharpe']:5.2f} {a['cum']*100:6.1f}% {a['maxdd']*100:6.1f}% {a['worst_bps']:7.0f}")
    res["rows"].append({"stop": s, "hit_all": a["hit"], "hit_rate_all": round(a["hit_rate"], 4),
        "hit_rate_fiinx": round(f["hit_rate"], 4), "hit_rate_bars": round(b["hit_rate"], 4),
        "gap_n_bars": b["gap_n"], "gap_max_bps": round(b["gap_max_bps"], 1), "gap_mean_bps": round(b["gap_mean_bps"], 2),
        "hit_hm_bars": b["hit_hm"], "mean_bps": round(a["mean_bps"], 2), "sharpe": round(a["sharpe"], 3),
        "cum": round(a["cum"], 4), "maxdd": round(a["maxdd"], 4), "worst_bps": round(a["worst_bps"], 1)})
res.update({"n_trades": len(ALL), "first": ALL[0]["date"], "last": ALL[-1]["date"], "chosen_stop": chosen,
            "mae_pct": {f"p{q}": round(float(np.percentile(mae, q)), 5) for q in (50,75,90,95,97,99)} | {"max": round(float(mae.max()), 5)},
            "baseline_nostop": {k: {kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in r.items() if kk != "hit_hm"} for k, r in base.items()}})
print(f"\nCHON (tieu chi tan suat, khai bao truoc): stop = {chosen*100:.1f}% (muc nho nhat co hit <= {TARGET_HIT*100:.0f}%)")
json.dump(res, open("stop_study_result.json", "w"), indent=1, default=str)
