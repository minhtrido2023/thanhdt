# -*- coding: utf-8 -*-
"""
f_sleeve_pt.py
==============
Paper-trade F-SYSTEM STANDALONE sleeve (rieng, von rieng) chay song song V5.
Overlay dinh huong VN30F theo regime DT5G, da lam sach bang Vol-target Van + deadband.

CO CHE (causal):
  state  = DT5G live (BQ tav2_bq.vnindex_5state_dt5g_live)
  base   = M_LIVE[state]:  CRISIS -1.0 | BEAR -0.2 | NEUTRAL +0.7 | BULL +1.0 | EX-BULL +1.3
  rv20   = std(20 log-ret VN30F1M) * sqrt(248)
  desired_scale = clip(median_rv20 / rv20, 0, 1.5)   [median_rv20=17.46% dong bang]
  applied_scale : deadband 0.10 — chi cap nhat khi |desired-applied|>=0.10
  position = base * applied_scale   (decided t, executed t+1; + long / - short)
  sleeve_ret_t = position_{t-1} * vn30f_ret_t - TC*|position_{t-1}-position_{t-2}|
Sleeve NAV tu base=10B (=20% cua 50B von V5 goc). Paper window 2026-06-08 -> 2026-06-30.
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from vnstock import Vnstock

WD = r"/home/trido/thanhdt/WorkingClaude"
STARTDATE   = "2026-06-08"
ENDDATE     = "2026-06-30"
SLEEVE_BASE = 10_000_000_000     # 10B = 20% cua von V5 goc 50B
MEDIAN_RV20 = 0.17459            # dong bang
DEADBAND    = 0.10
TC          = 0.0003
MULT        = 100_000
M_LIVE      = {1:-1.00, 2:-0.20, 3:0.70, 4:1.00, 5:1.30}
SN          = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ---- 1) VN30F1M + rv20 + Van applied_scale (deadband, deterministic) ----
f = Vnstock().stock(symbol="VN30F1M", source="VCI").quote.history(
        start="2017-08-01", end=ENDDATE, interval="1D")
f["time"] = pd.to_datetime(f["time"]); f = f.sort_values("time").reset_index(drop=True)
f["fret"] = f["close"].pct_change()
f["lr"]   = np.log(f["close"]/f["close"].shift(1))
f["rv20"] = f["lr"].rolling(20).std()*np.sqrt(248)
desired = np.clip(MEDIAN_RV20 / f["rv20"].values, 0, 1.5)
applied = np.ones(len(f)); cur = 1.0
for t in range(len(f)):
    d = desired[t]
    if not np.isnan(d) and abs(d-cur) >= DEADBAND: cur = d
    applied[t] = cur
f["applied_scale"] = applied

# ---- 2) DT5G state from BQ (fresh), align to VN30F dates ----
try:
    from recommend_holistic import bq
    st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s "
            "WHERE s.time>='2017-08-01' ORDER BY s.time")
    st["time"] = pd.to_datetime(st["time"])
except Exception as e:
    print(f"  WARN: BQ DT5G that bai ({e}); doc local CSV.");
    st = pd.read_csv(WD+"/vnindex_5state_dt5g_live.csv")[["time","state"]]
    st["time"] = pd.to_datetime(st["time"])
f = f.merge(st, on="time", how="left")
f["state"] = f["state"].ffill().fillna(3).astype(int)   # forward-fill; default NEUTRAL

# ---- 3) position path + sleeve daily return ----
f["position"] = f["state"].map(M_LIVE).astype(float) * f["applied_scale"]
pos = f["position"].values; fret = f["fret"].values
sret = np.zeros(len(f))
for t in range(1, len(f)):
    dpos = abs(pos[t-1]-pos[t-2]) if t>=2 else abs(pos[t-1])
    sret[t] = pos[t-1]*(fret[t] if not np.isnan(fret[t]) else 0.0) - TC*dpos
f["sleeve_ret"] = sret

# ---- 4) latest recommendation (next session) ----
last = f.iloc[-1]
st_now = int(last["state"]); base_now = M_LIVE[st_now]; sc_now = float(last["applied_scale"])
pos_now = base_now*sc_now
contracts = round(pos_now * SLEEVE_BASE / (last["close"]*MULT))
side = "LONG" if pos_now>0 else ("SHORT" if pos_now<0 else "FLAT")

print("="*100)
print(f"  F-SYSTEM STANDALONE sleeve — PAPER-TRADE  ({STARTDATE} -> {ENDDATE})")
print(f"  DT5G + Van + deadband {DEADBAND} | sleeve base={SLEEVE_BASE:,.0f} (20% cua 50B)")
print("="*100)
print(f"\n  >> KHUYEN NGHI HOM NAY ({last['time'].date()}): DT5G={SN[st_now]} | VN30F={last['close']:.1f} | rv20={last['rv20']:.1%}")
print(f"     base={base_now:+.2f} x scale={sc_now:.2f} = position {pos_now:+.2f}")
print(f"     -> phien KE TIEP: {side} {abs(contracts)} HD VN30F (notional {abs(pos_now)*SLEEVE_BASE:,.0f})")

status = {
    "asof": str(last["time"].date()), "state": st_now, "state_name": SN[st_now],
    "vn30f": round(float(last["close"]),1), "rv20": round(float(last["rv20"]),4),
    "base": base_now, "applied_scale": round(sc_now,3), "position": round(pos_now,3),
    "side": side, "reco_contracts": int(abs(contracts)),
    "reco_notional": int(abs(pos_now)*SLEEVE_BASE),
    "sleeve_base": SLEEVE_BASE, "window_start": STARTDATE, "window_end": ENDDATE,
    "window_started": False, "n_days": 0, "sleeve_ret": None, "sleeve_nav": None,
}
def _write_status():
    with open(WD+"/data/f_sleeve_status.json","w",encoding="utf-8") as fp:
        json.dump(status, fp, ensure_ascii=False, indent=2)

# ---- 5) paper-trade window ----
w = f[(f["time"]>=STARTDATE)&(f["time"]<=ENDDATE)].reset_index(drop=True)
if len(w)==0:
    print(f"\n  [Paper chua bat dau] Chua co phien VN30F >= {STARTDATE}.")
    _write_status(); print("Done."); sys.exit()
w["nav"] = SLEEVE_BASE*(1+w["sleeve_ret"]).cumprod()
ret_tot = w["nav"].iloc[-1]/SLEEVE_BASE - 1
print(f"\n  --- Dien bien sleeve tu {STARTDATE} ---")
print(f"  {'Date':<12}{'DT5G':>9}{'VN30F':>8}{'pos':>7}{'sleeve_ret':>11}{'NAV':>16}")
print("  "+"-"*64)
for _,r in w.iterrows():
    print(f"  {str(r['time'].date()):<12}{SN[int(r['state'])]:>9}{r['close']:>8.1f}{r['position']:>+7.2f}"
          f"{r['sleeve_ret']*100:>+10.2f}%{r['nav']:>16,.0f}")
print("  "+"-"*64)
print(f"\n  TONG KET {len(w)} phien: sleeve return {ret_tot*100:+.2f}%  (NAV {w['nav'].iloc[-1]:,.0f})")
status.update({"window_started": True, "n_days": int(len(w)),
               "sleeve_ret": round(float(ret_tot),4), "sleeve_nav": int(w["nav"].iloc[-1])})
_write_status()
w.to_csv(WD+"/data/f_sleeve_pt_log.csv", index=False)
print(f"\n  Log -> data/f_sleeve_pt_log.csv | status -> data/f_sleeve_status.json")
print("Done.")
