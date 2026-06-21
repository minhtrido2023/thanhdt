# -*- coding: utf-8 -*-
"""
vol_spike_hedge_pt.py
=====================
Paper-trade VOL-SPIKE HEDGE phu len sach V5 (V121_Kelly trong papertrade_compare5.csv).
Chay moi phien (sau khi co gia VN30F + NAV V5 cuoi ngay). Idempotent: dung lai toan bo
tu nguon moi lan chay, khong phu thuoc state file de.

CO CHE (causal):
  rv10 = std(10 log-ret VN30F1M gan nhat) * sqrt(248)   [vol thuc hien 10 ngay, quy nam]
  signal_t = 1 neu rv10_t > THRESHOLD (=1.3 x median lich su = 20.77%)  else 0
  Vi the giu hom nay = signal cua HOM QUA (T+1 execution).
  hedge_ret_t = -lambda * signal_{t-1} * vn30f_ret_t     (SHORT, lambda=0.4 ~ beta V5)
  combined_ret_t = v5_ret_t + hedge_ret_t
Paper-trade tu STARTDATE=2026-06-08 den ENDDATE=2026-06-30.
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from vnstock import Vnstock

WD = r"/home/trido/thanhdt/WorkingClaude"
STARTDATE = "2026-06-08"
ENDDATE   = "2026-06-30"
LAMBDA    = 0.40
MEDIAN_RV10 = 0.15979          # dong bang tren lich su den 2026-06-08
THRESHOLD   = 1.3 * MEDIAN_RV10  # = 0.20773
MULT = 100_000                 # VN30F: 100k VND/diem

# ---- 1) VN30F1M + rv10 + returns ----
f = Vnstock().stock(symbol="VN30F1M", source="VCI").quote.history(
        start="2026-01-01", end=ENDDATE, interval="1D")
f["time"] = pd.to_datetime(f["time"]); f = f.sort_values("time").reset_index(drop=True)
f["lr"]  = np.log(f["close"]/f["close"].shift(1))
f["fret"]= f["close"].pct_change()
f["rv10"]= f["lr"].rolling(10).std()*np.sqrt(248)
f["signal"] = (f["rv10"] > THRESHOLD).astype(int)

# ---- 2) V5 paper NAV (V121_Kelly) ----
v = pd.read_csv(WD+"/data/papertrade_compare5.csv")
v["time"] = pd.to_datetime(v["ymd"])
v = v[["time","V23"]].rename(columns={"V23":"V5"}).sort_values("time")
v["v5_ret"] = v["V5"].pct_change()

# ---- always: latest trigger status (kể cả khi cửa sổ paper chưa có NAV) ----
last = f.iloc[-1]
base_latest = float(v["V5"].iloc[-1])
on = "ON (SHORT)" if last["signal"]==1 else "OFF (flat)"
contracts = round(LAMBDA*base_latest/(last["close"]*MULT))
print("="*100)
print(f"  VOL-SPIKE HEDGE cho V5 — PAPER-TRADE  ({STARTDATE} -> {ENDDATE})")
print(f"  lambda={LAMBDA} | nguong rv10 > {THRESHOLD:.2%} (1.3x median {MEDIAN_RV10:.2%}) | V5 NAV moi nhat={base_latest:,.0f}")
print("="*100)
print(f"\n  >> TRANG THAI CO HOM NAY ({last['time'].date()}): VN30F={last['close']:.1f} | rv10={last['rv10']:.2%} -> {on}")
print(f"     Khuyen nghi phien KE TIEP: "
      + (f"SHORT {contracts} HD VN30F (notional {LAMBDA*base_latest:,.0f})" if last["signal"]==1
         else "KHONG hedge (dong short neu dang co)"))

# status dict (telegram report doc file nay)
status = {
    "asof": str(last["time"].date()), "vn30f": round(float(last["close"]),1),
    "rv10": round(float(last["rv10"]),4), "threshold": round(float(THRESHOLD),4),
    "signal_on": bool(last["signal"]==1), "lambda": LAMBDA,
    "reco_contracts": int(contracts) if last["signal"]==1 else 0,
    "reco_notional": int(LAMBDA*base_latest) if last["signal"]==1 else 0,
    "v5_nav": int(base_latest), "window_start": STARTDATE, "window_end": ENDDATE,
    "window_started": False, "n_days": 0, "on_days": 0,
    "v5_only_ret": None, "v5_hedged_ret": None, "hedge_pp": None, "hedge_vnd": None,
}
def _write_status():
    with open(WD+"/data/vol_spike_hedge_status.json","w",encoding="utf-8") as fp:
        json.dump(status, fp, ensure_ascii=False, indent=2)

# ---- 3) merge on trading days, restrict to paper window ----
m = v.merge(f[["time","close","fret","rv10","signal"]].rename(columns={"close":"vn30f"}),
            on="time", how="inner")
m = m[(m["time"]>=STARTDATE)&(m["time"]<=ENDDATE)].reset_index(drop=True)

# signal held today = signal decided yesterday (shift). Day 0 of window: flat.
m["sig_held"] = m["signal"].shift(1).fillna(0).astype(int)
m["hedge_ret"] = -LAMBDA * m["sig_held"] * m["fret"].fillna(0)
m["v5_ret"]    = m["v5_ret"].fillna(0)
m["comb_ret"]  = m["v5_ret"] + m["hedge_ret"]

# ---- 4) build NAV paths from window start (base = V5 NAV at start) ----
if len(m)==0:
    print(f"\n  [Paper-trade chua bat dau] Chua co NAV V5 phien nao >= {STARTDATE} "
          f"(V5 NAV moi nhat: {v['time'].iloc[-1].date()}).")
    print("  Tracker se tu dien khi papertrade_compare5.csv ghi phien dau trong cua so.")
    _write_status()
    print("Done."); sys.exit()
base = float(m["V5"].iloc[0])
m["V5_only"]  = base*(1+m["v5_ret"]).cumprod()
m["V5_hedged"]= base*(1+m["comb_ret"]).cumprod()
m["hedge_pnl_day"] = base*(1+m["v5_ret"]).cumprod()*m["hedge_ret"]   # approx VND dong gop/ngay
m["hedge_cum"] = (m["V5_hedged"]-m["V5_only"])

# ---- 5) report: daily table since window start ----
print(f"\n  --- Dien bien paper-trade tu {STARTDATE} (base V5 NAV={base:,.0f}) ---")
print(f"\n  {'Date':<12}{'VN30F':>8}{'rv10':>7}{'sig':>4}{'held':>5}{'V5_ret':>8}{'hedge':>8}{'comb':>8}{'V5_only':>15}{'V5_hedged':>15}")
print("  "+"-"*96)
for _,r in m.iterrows():
    print(f"  {str(r['time'].date()):<12}{r['vn30f']:>8.1f}{r['rv10']:>7.1%}{r['signal']:>4}{r['sig_held']:>5}"
          f"{r['v5_ret']*100:>+7.2f}%{r['hedge_ret']*100:>+7.2f}%{r['comb_ret']*100:>+7.2f}%"
          f"{r['V5_only']:>15,.0f}{r['V5_hedged']:>15,.0f}")
nd=len(m); on_days=int(m["sig_held"].sum())
r_v5=m["V5_only"].iloc[-1]/base-1; r_hd=m["V5_hedged"].iloc[-1]/base-1
print("  "+"-"*96)
print(f"\n  TONG KET {nd} phien | hedge ON {on_days} phien:")
print(f"    V5 khong hedge : {r_v5*100:+.2f}%  (NAV {m['V5_only'].iloc[-1]:,.0f})")
print(f"    V5 + hedge     : {r_hd*100:+.2f}%  (NAV {m['V5_hedged'].iloc[-1]:,.0f})")
print(f"    Dong gop hedge : {(r_hd-r_v5)*100:+.2f}pp  ({m['hedge_cum'].iloc[-1]:+,.0f} VND)")

m.to_csv(WD+"/data/vol_spike_hedge_pt_log.csv", index=False)
status.update({"window_started": True, "n_days": int(nd), "on_days": int(on_days),
               "v5_only_ret": round(float(r_v5),4), "v5_hedged_ret": round(float(r_hd),4),
               "hedge_pp": round(float((r_hd-r_v5)*100),3), "hedge_vnd": (int(m["hedge_cum"].iloc[-1]) if pd.notna(m["hedge_cum"].iloc[-1]) else 0)})
_write_status()
print(f"\n  Log -> data/vol_spike_hedge_pt_log.csv | status -> data/vol_spike_hedge_status.json")
print("Done.")
