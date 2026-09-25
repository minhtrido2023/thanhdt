# -*- coding: utf-8 -*-
"""
viec_a_robust.py -- A6: ba truc co the pha vo ket luan cua A1-A5, kiem tra rieng.
  A6.1 TRE THUC THI: config dang chay lay entry = close bar 09:30 va signal cung tu bar do
       => tin hieu va lenh vao TRUNG mot thoi diem. Do lai khi vao tre 1..5 phut.
  A6.2 CHI PHI: slip 0/1/2/3 tick x fee 0.6/2.5/5.0 bps.
  A6.3 BOOTSTRAP: IID + block(5,10,20 phien) CI cho mean/phien va Sharpe -> lam "ky vong"
       cho Viec C (nguong canh bao phai neo vao phan phoi, khong phai 1 diem).
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
import orb_core as C

OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260925)
df = C.load_bars(); days = C.build_days(df)
res = {}

# ---------- A6.1 tre thuc thi ----------
def sim_lag(lag_min):
    """Vao lenh tai close cua bar thu lag_min sau 09:30 (lag=0 = dung nhu dang chay)."""
    recs = []
    for dd in days:
        post = dd["post"]
        if lag_min == 0:
            entry = dd["entry"]; seg = post[post["hm"] <= C.EXIT_HM]
        else:
            if len(post) <= lag_min: continue
            entry = float(post["close"].iloc[lag_min - 1])
            seg = post.iloc[lag_min:]; seg = seg[seg["hm"] <= C.EXIT_HM]
        if len(seg) == 0: continue
        sig = dd["sig"]; exitpx = float(seg["close"].iloc[-1])
        ef = entry + sig*C.SLIP_TICKS*C.TICK; xf = exitpx - sig*C.SLIP_TICKS*C.TICK
        recs.append({"date": dd["date"], "net": sig*(xf/ef-1) - C.FEE, "stopped": False})
    r = pd.DataFrame(recs); r["date_dt"] = pd.to_datetime(r["date"]); return r

print("="*100); print("  A6.1) TRE THUC THI -- tin hieu & entry cua config dang chay trung 1 thoi diem (09:30)")
print("="*100)
lagres = {}
for lag in [0,1,2,3,5]:
    s = C.stats(sim_lag(lag)); lagres[lag] = s
    print(C.fmt(s, f"vao tre {lag} phut" + ("  <== DANG CHAY" if lag==0 else "")))
d1 = lagres[1]["sharpe"] - lagres[0]["sharpe"]
print(f"\n  Tre 1 phut lam Sharpe doi {d1:+.2f} ({lagres[0]['sharpe']:+.2f} -> {lagres[1]['sharpe']:+.2f}),"
      f" mean {lagres[0]['mean_bps']:+.2f} -> {lagres[1]['mean_bps']:+.2f}bps")
res["A6_1_lag"] = lagres

# ---------- A6.2 chi phi ----------
print("\n"+"="*100); print("  A6.2) DO NHAY CHI PHI (slip ticks x fee round-trip)"); print("="*100)
print(f"  {'fee':<10}" + "".join(f"{'slip'+str(s)+'t':>16}" for s in [0,1,2,3]))
costres = {}
for fee in [0.00006, 0.00025, 0.0005]:
    row = f"  {fee*1e4:>4.1f}bps   "
    for slip in [0,1,2,3]:
        s = C.stats(C.sim(days, slip_ticks=slip, fee=fee))
        costres[f"fee{fee*1e4:.1f}_slip{slip}"] = s
        mark = "*" if (abs(fee-C.FEE)<1e-12 and slip==C.SLIP_TICKS) else " "
        row += f"{s['mean_bps']:>+7.2f}/{s['sharpe']:>+5.2f}{mark}".rjust(16)
    print(row)
print("  (moi o = mean bps/phien / Sharpe ann. '*' = config DANG CHAY)")
be = None
for slip in range(0, 12):
    s = C.stats(C.sim(days, slip_ticks=slip, fee=C.FEE))
    if s["mean_bps"] <= 0: be = slip; break
print(f"  Break-even: mean/phien ve <=0 khi slip = {be} tick/chieu (dang gia dinh {C.SLIP_TICKS})"
      f" => bien an toan {be-C.SLIP_TICKS} tick.")
res["A6_2_cost"] = {"grid": costres, "breakeven_slip_ticks": be}

# ---------- A6.3 bootstrap ----------
print("\n"+"="*100); print("  A6.3) BOOTSTRAP CI (10.000 lan) -- nen cho 'ky vong' o Viec C"); print("="*100)
R = C.sim(days)
pre = R[R["date"] < C.LIVE_START]["net"].values     # CHI dung doan pre-live: khong vong tron voi Viec B/C
def boot(x, blk, B=10000):
    n = len(x); ms = np.empty(B); shs = np.empty(B)
    if blk == 1:
        idx = rng.integers(0, n, size=(B, n)); S = x[idx]
    else:
        nb = int(np.ceil(n/blk)); starts = rng.integers(0, n-blk+1, size=(B, nb))
        S = np.concatenate([x[starts[:, j][:, None] + np.arange(blk)] for j in range(nb)], axis=1)[:, :n]
    ms = S.mean(axis=1); sds = S.std(axis=1, ddof=1)
    shs = np.where(sds > 0, ms/sds*np.sqrt(252), 0.0)
    return ms, shs
print(f"  Nen = {len(pre)} phien BACKTEST pre-live (mean that {pre.mean()*1e4:+.2f}bps,"
      f" Sharpe that {pre.mean()/pre.std(ddof=1)*np.sqrt(252):+.2f})")
print(f"  {'block':<9}{'mean p5':>10}{'mean p50':>10}{'mean p95':>10}{'Sh p5':>9}{'Sh p50':>9}{'Sh p95':>9}{'P(mean<=0)':>12}")
bres = {}
for blk in [1,5,10,20]:
    ms, shs = boot(pre, blk)
    q = lambda a,p: float(np.percentile(a,p))
    bres[blk] = {"mean_bps_p5": q(ms,5)*1e4, "mean_bps_p50": q(ms,50)*1e4, "mean_bps_p95": q(ms,95)*1e4,
                 "sharpe_p5": q(shs,5), "sharpe_p50": q(shs,50), "sharpe_p95": q(shs,95),
                 "p_mean_le_0": float((ms<=0).mean())}
    b = bres[blk]
    print(f"  {('IID' if blk==1 else str(blk)):<9}{b['mean_bps_p5']:>+9.2f}{b['mean_bps_p50']:>+10.2f}"
          f"{b['mean_bps_p95']:>+10.2f}{b['sharpe_p5']:>+9.2f}{b['sharpe_p50']:>+9.2f}{b['sharpe_p95']:>+9.2f}"
          f"{b['p_mean_le_0']:>12.4f}")
res["A6_3_bootstrap_prelive"] = bres

# phan phoi cua TONG 25 / 75 phien lien tiep rut tu pre-live -> nguong canh bao Viec C
print(f"\n  Phan phoi CUM (tich luy, khong phi them) cua k phien LIEN TIEP rut tu pre-live:")
print(f"  {'k phien':<10}{'p1':>9}{'p5':>9}{'p25':>9}{'p50':>9}{'p95':>9}")
wres = {}
for k in [25, 50, 75, 100]:
    n = len(pre); st = rng.integers(0, n-k+1, size=20000)
    S = pre[st[:,None] + np.arange(k)]
    cums = np.prod(1+S, axis=1)-1
    wres[k] = {f"p{p}": float(np.percentile(cums,p))*100 for p in (1,5,25,50,95)}
    w = wres[k]
    print(f"  {k:<10}{w['p1']:>+8.2f}%{w['p5']:>+8.2f}%{w['p25']:>+8.2f}%{w['p50']:>+8.2f}%{w['p95']:>+8.2f}%")
res["A6_3_window_cum_prelive_pct"] = wres

with open(os.path.join(OUT,"viec_a_robust_result.json"),"w") as f: json.dump(res,f,indent=1,default=float)
print("\nDone. -> viec_a_robust_result.json")
