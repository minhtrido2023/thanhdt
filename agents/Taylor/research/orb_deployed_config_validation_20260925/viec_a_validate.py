# -*- coding: utf-8 -*-
"""
viec_a_validate.py -- VIEC A: validate tu dau CHINH config dang deploy trong orb_pt.py.
Chay: python3 viec_a_validate.py   (in ra stdout + ghi viec_a_result.json + trades CSV)

Neo provenance: truoc khi bao BAT KY so nao, script tu doi soat cua so live cua chinh no
voi data/orb_pt_log.csv (75 phien paper THAT). Lech > 1e-9 o bat ky cot => abort.
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from normstat import ncdf as _ncdf, nppf as _nppf
import orb_core as C

OUT = os.path.dirname(os.path.abspath(__file__))
IS_END = "2025-01-01"          # IS = truoc moc nay, OOS = tu moc nay
EULER  = 0.5772156649015329

days = C.build_days(C.load_bars())
R = C.sim(days)                                  # config DANG DEPLOY, y nguyen
R.to_csv(os.path.join(OUT, "deployed_trades_full.csv"), index=False)

# ---------- 0) SELF-CHECK provenance: sim == so paper that ----------
log = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/orb_pt_log.csv")
sim_live = R[R["date"] >= C.LIVE_START]
m = log.merge(sim_live, on="date", suffixes=("_log", "_sim"), how="outer", indicator=True)
bad = (m["_merge"] != "both").sum()
worst = 0.0
for c in ["or_ret", "sig", "entry", "exit", "net"]:
    worst = max(worst, float((m[c + "_log"] - m[c + "_sim"]).abs().max()))
print("=" * 100)
print("  SELF-CHECK provenance: engine nay co dung la config DANG CHAY khong?")
print("=" * 100)
print(f"  so phien log paper = {len(log)} | so phien sim trong cung cua so = {len(sim_live)}"
      f" | ngay khong khop = {bad} | lech lon nhat moi cot = {worst:.2e}")
if bad or worst > 1e-9:
    print("  !!! ABORT: engine KHONG tai dung duoc so paper that. Moi so duoi day vo nghia.")
    sys.exit(2)
print("  => PASS. Engine tai dung 75/75 phien paper that toi 1e-16. Cac so duoi la ve CONFIG DANG CHAY.")

res = {"selfcheck": {"paper_rows": len(log), "sim_rows": int(len(sim_live)),
                     "unmatched_dates": int(bad), "max_abs_diff": worst, "verdict": "PASS"}}

# ---------- 1) TOAN BO lich su + tach pre-live / live ----------
pre  = R[R["date"] <  C.LIVE_START]
live = R[R["date"] >= C.LIVE_START]
print("\n" + "=" * 100)
print("  A1) CONFIG DANG DEPLOY tren toan bo lich su co du lieu (1m VN30F1M, 2 nguon ghep)")
print("=" * 100)
blocks = [("FULL 2023-09-11..2026-09-25", R),
          ("BACKTEST (truoc live)", pre),
          ("LIVE paper (2026-06-09+)", live)]
for lbl, sub in blocks:
    print(C.fmt(C.stats(sub), lbl))
res["A1"] = {lbl: C.stats(sub) for lbl, sub in blocks}

# ---------- 2) WALK-FORWARD IS/OOS ----------
print("\n" + "=" * 100
      )
print(f"  A2) WALK-FORWARD  IS = < {IS_END}  |  OOS = >= {IS_END}")
print("=" * 100)
wf = [(f"IS  (<{IS_END})", R[R["date"] < IS_END]),
      (f"OOS (>={IS_END}, ca live)", R[R["date"] >= IS_END]),
      (f"OOS backtest-only", R[(R["date"] >= IS_END) & (R["date"] < C.LIVE_START)]),
      (f"OOS live-only", live)]
for lbl, sub in wf:
    print(C.fmt(C.stats(sub), lbl))
res["A2"] = {lbl: C.stats(sub) for lbl, sub in wf}

# ---------- 3) PER-YEAR toan bo cac nam ----------
print("\n" + "=" * 100)
print("  A3) PER-YEAR -- TOAN BO cac nam co du lieu")
print("=" * 100)
R["yr"] = R["date_dt"].dt.year
peryear = {}
for yr, gg in R.groupby("yr"):
    s = C.stats(gg); peryear[int(yr)] = s
    note = ""
    if yr == 2023: note = "  (tu 09-11, nam cat)"
    if yr == 2026: note = "  (den 09-25, nam cat; gom 75 phien live)"
    print(C.fmt(s, f"{yr}{note}"))
npos = sum(1 for s in peryear.values() if s["mean_bps"] > 0)
print(f"\n  => {npos}/{len(peryear)} nam duong theo mean/phien. "
      f"Am: {[y for y,s in peryear.items() if s['mean_bps']<=0] or 'khong co'}")
res["A3"] = peryear

# quarter breakdown -- do min do (nam it, N=4 khong noi len duoc gi)
R["q"] = R["date_dt"].dt.to_period("Q").astype(str)
qs = {q: C.stats(gg) for q, gg in R.groupby("q")}
qpos = sum(1 for s in qs.values() if s["mean_bps"] > 0)
print(f"  Chi tiet hon theo QUY: {qpos}/{len(qs)} quy duong "
      f"(am: {[q for q,s in qs.items() if s['mean_bps']<=0]})")
res["A3_quarter"] = qs

# ---------- 5) NEIGHBOURHOOD / robustness (chay truoc A4 vi A4 can V[SR] tu day) ----------
print("\n" + "=" * 100)
print("  A5) DO NHAY QUANH THAM SO LAN CAN -- CHI de xem config hien tai co nam trong vung")
print("      on dinh hay la mot diem may man co lap. KHONG dung de de xuat doi tham so.")
print("=" * 100)
EXITS  = ["13:30", "14:00", "14:15", "14:30", "14:45"]
MINORS = [0.0, 0.0005, 0.001, 0.002]
STOPS  = [None, 0.007, 0.010]
grid = []
for ex in EXITS:
    for mo in MINORS:
        for st in STOPS:
            rr = C.sim(days, exit_hm=ex, stop=st, min_or=mo)
            s = C.stats(rr)
            if s is None: continue
            s_pre  = C.stats(rr[rr["date"] <  C.LIVE_START])
            s_oos  = C.stats(rr[rr["date"] >= IS_END])
            grid.append(dict(exit=ex, min_or=mo, stop=(st or 0.0), **{k: s[k] for k in
                        ("n","wr","mean_bps","sharpe","cum","mdd","t","sr_per_obs")},
                        sharpe_pre=s_pre["sharpe"] if s_pre else None,
                        sharpe_oos=s_oos["sharpe"] if s_oos else None,
                        is_deployed=(ex=="14:30" and mo==0.0 and st is None)))
G = pd.DataFrame(grid)
G.to_csv(os.path.join(OUT, "neighbourhood_grid.csv"), index=False)
print(f"  {'exit':<7}{'minOR':<8}{'stop':<7}{'n':>5}{'mean':>9}{'Sh_full':>9}{'Sh_IS':>8}{'Sh_OOS':>8}{'cum':>9}")
print("  " + "-" * 72)
for _, g in G.iterrows():
    mark = "  <== DANG CHAY" if g["is_deployed"] else ""
    print(f"  {g['exit']:<7}{g['min_or']*100:<7.2f}%{g['stop']*100:<6.1f}%{int(g['n']):>5}"
          f"{g['mean_bps']:>+8.2f}{g['sharpe']:>+9.2f}{g['sharpe_pre']:>+8.2f}{g['sharpe_oos']:>+8.2f}"
          f"{g['cum']*100:>+8.1f}%{mark}")
dep = G[G["is_deployed"]].iloc[0]
print(f"\n  Vi tri config DANG CHAY trong ho {len(G)} to hop lan can:")
for k, lbl in [("sharpe","Sharpe full"), ("sharpe_pre","Sharpe IS/pre-live"), ("sharpe_oos","Sharpe OOS")]:
    pct = float((G[k] < dep[k]).mean()) * 100
    print(f"    {lbl:<20} = {dep[k]:+.2f}  -> phan vi {pct:.0f}% (median ho = {G[k].median():+.2f},"
          f" max = {G[k].max():+.2f})")
npos_grid = int((G["sharpe"] > 0).sum())
print(f"    {npos_grid}/{len(G)} to hop lan can co Sharpe full > 0"
      f" ; {int((G['sharpe_oos']>0).sum())}/{len(G)} co Sharpe OOS > 0")
res["A5"] = {"grid_rows": len(G), "deployed": {k: (None if pd.isna(dep[k]) else float(dep[k]))
             for k in ("sharpe","sharpe_pre","sharpe_oos","mean_bps","cum")},
             "pct_rank_sharpe_full": float((G["sharpe"] < dep["sharpe"]).mean()),
             "pct_rank_sharpe_oos": float((G["sharpe_oos"] < dep["sharpe_oos"]).mean()),
             "n_pos_sharpe_full": npos_grid, "n_pos_sharpe_oos": int((G["sharpe_oos"]>0).sum()),
             "median_sharpe_full": float(G["sharpe"].median()),
             "max_sharpe_full": float(G["sharpe"].max())}

# ---------- 4) PSR / DSR ----------
def psr(sr, n, skew, kurt, sr_star=0.0):
    """Probabilistic Sharpe Ratio (Bailey-Lopez de Prado). sr, sr_star = per-observation."""
    denom = np.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4.0 * sr ** 2))
    return float(_ncdf((sr - sr_star) * np.sqrt(n - 1) / denom))

def e_max_sr(n_trials, var_sr):
    if n_trials <= 1: return 0.0
    return float(np.sqrt(var_sr) * ((1 - EULER) * _nppf(1 - 1.0 / n_trials)
                                    + EULER * _nppf(1 - 1.0 / (n_trials * np.e))))

s_full = C.stats(R)
sr_obs, n_obs = s_full["sr_per_obs"], s_full["n"]
var_grid = float(G["sr_per_obs"].var(ddof=1))
print("\n" + "=" * 100)
print("  A4) PSR / DSR cho CHINH config dang deploy")
print("=" * 100)
print(f"  Sharpe/phien = {sr_obs:.4f} (annualised {s_full['sharpe']:+.2f}), n = {n_obs},"
      f" skew = {s_full['skew']:+.3f}, kurtosis = {s_full['kurt']:.2f}")
print(f"  PSR(SR*=0) = {psr(sr_obs, n_obs, s_full['skew'], s_full['kurt']):.4f}"
      f"   (xac suat Sharpe THAT > 0, da hieu chinh skew/kurtosis/n)")
print(f"  V[SR] do tu {len(G)} to hop lan can = {var_grid:.6f} (sd = {np.sqrt(var_grid):.4f}/phien)")
print(f"\n  {'gia dinh so phep thu N':<46}{'E[max SR]':>11}{'DSR':>9}")
print("  " + "-" * 66)
dsr = {}
for N, lbl in [(1,  "N=1  (chua he chon theo hieu suat)"),
               (12, "N=12 (grid exit x stop cua strategy.py)"),
               (20, "N=20 (ca ho ~20 config da sweep truoc)"),
               (60, f"N={len(G)} (toan bo ho lan can A5)")]:
    NN = len(G) if N == 60 else N
    ss = e_max_sr(NN, var_grid)
    d  = psr(sr_obs, n_obs, s_full["skew"], s_full["kurt"], ss)
    dsr[NN] = {"e_max_sr": ss, "dsr": d}
    print(f"  {lbl:<46}{ss:>11.4f}{d:>9.4f}")
res["A4"] = {"sr_per_obs": sr_obs, "n": n_obs, "skew": s_full["skew"], "kurt": s_full["kurt"],
             "psr_0": psr(sr_obs, n_obs, s_full["skew"], s_full["kurt"]),
             "var_sr_grid": var_grid, "dsr": dsr}

# DSR tren rieng doan pre-live (khong dung du lieu live -> khong vong tron voi Viec B/C)
s_pre = C.stats(pre)
res["A4_prelive"] = {"sr_per_obs": s_pre["sr_per_obs"], "n": s_pre["n"],
                     "psr_0": psr(s_pre["sr_per_obs"], s_pre["n"], s_pre["skew"], s_pre["kurt"]),
                     "dsr_N20": psr(s_pre["sr_per_obs"], s_pre["n"], s_pre["skew"], s_pre["kurt"],
                                    e_max_sr(20, var_grid))}
print(f"\n  Lap lai chi tren doan BACKTEST pre-live (n={s_pre['n']}, khong dung du lieu live):")
print(f"    PSR(0) = {res['A4_prelive']['psr_0']:.4f} | DSR(N=20) = {res['A4_prelive']['dsr_N20']:.4f}")

with open(os.path.join(OUT, "viec_a_result.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)
print("\nDone. -> viec_a_result.json, deployed_trades_full.csv, neighbourhood_grid.csv")
