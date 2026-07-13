# -*- coding: utf-8 -*-
"""dc_trigger_gap_backtest.py (job Taylor_20260713_100550) — RESEARCH ONLY.

Đo độ vênh TRIGGER giữa (a) spec overlay đã backtest & pin (job _173317 CÂU 0: DC vehicle
chạy trên phần tiền park LIÊN TỤC mọi ngày NEUTRAL) và (b) trigger BINARY của paper sleeve
đang chạy (`dc_book_waterfall_paper.compute_waterfall_targets`: bal_lag_has_deal=True →
sleeve FLAT hoàn toàn; tiền park khi đó về custom30V như baseline).

Deal-day proxy: ngày có TX buy book BAL/LAG trong R3 audit (xấp xỉ n_bal>0 | n_lag_upcoming>0
tại plan-build; n_lag_upcoming thực tế còn fire SỚM HƠN entry ~vài phiên → binary thực còn
FLAT nhiều hơn số này = số dưới đây là ước lượng LẠC QUAN cho binary).

N trials khai báo = 2 (binary-TC, binary-noTC diagnostic). Continuous + baseline = reproduction
(self-check C phải khớp registry CÂU 0 ~27.5x/Calmar 1.77x cùng single-cache 07-07).
Self-checks: (A) overlay identity 0 VND; (C) continuous tái lập số CÂU 0 deepdive/timing daily.
Vehicle machinery copy nguyên từ dc_rebal_timing_backtest.py (không sửa logic).
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

AUDIT = "data/h3_baseline_R3.csv"
IS_END = pd.Timestamp("2019-12-31")
CAP, TC = 0.20, 0.001

aud_df = pd.read_csv(AUDIT, low_memory=False)
d = aud_df[aud_df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"])
for c_ in ["state", "bal_etf_ref", "lag_etf_ref", "combined_nav"]:
    d[c_] = pd.to_numeric(d[c_])
aud = d.set_index("ymd").sort_index()

r_c30v = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
nav = aud["combined_nav"]
r_base = nav.pct_change().dropna()
w_park_prev = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]).shift(1).reindex(r_base.index).fillna(0.0)

dbl = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True).astype(bool)
if "DHG" in dbl.columns:
    dbl["DHG"] = False          # paper config: DHG hard-excluded
sret = pd.read_csv("data/dc_stock_ret.csv", index_col=0, parse_dates=True)
park = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
cal = dbl.index
names = list(dbl.columns)

# deal-days: TX buy BAL/LAG (proxy binary-trigger OFF)
tx = aud_df[aud_df["record_type"] == "TX"].copy()
tx["ymd"] = pd.to_datetime(tx["ymd"])
deal_days = set(tx[(tx["action"] == "buy") & (tx["book"].isin(["BAL", "LAG"]))]["ymd"].dt.normalize())
deal_mask = pd.Series([ts in deal_days for ts in cal], index=cal)
print(f"deal-days on vehicle calendar: {int(deal_mask.sum())}/{len(cal)}")

def vehicle(flat_mask=None, tc=TC):
    """Composite sleeve return, daily membership refresh. flat_mask=True days → sleeve is
    100% custom30V (binary trigger OFF). Turnover-TC block-level charges whipsaw tự nhiên."""
    W = pd.DataFrame(0.0, index=cal, columns=names); pk = pd.Series(0.0, index=cal)
    for dd in cal:
        if flat_mask is not None and bool(flat_mask.loc[dd]):
            pk.loc[dd] = 1.0
            continue
        cur = [t for t in names if dbl.at[dd, t]]
        n = len(cur)
        if n:
            w = min(CAP, 1.0 / n)
            for t in cur: W.at[dd, t] = w
            pk.loc[dd] = max(0.0, 1.0 - w * n)
        else:
            pk.loc[dd] = 1.0
    r = pd.Series(0.0, index=cal); prev_w = W.iloc[0].copy(); prev_p = pk.iloc[0]
    turn = pd.Series(0.0, index=cal)
    for i, dd in enumerate(cal):
        if i == 0: continue
        ra = float((prev_w * sret.loc[dd].reindex(names).fillna(0.0)).sum())
        rp = prev_p * (park.loc[dd] if np.isfinite(park.loc[dd]) else 0.0)
        t = (float((W.loc[dd] - prev_w).abs().sum()) + abs(pk.loc[dd] - prev_p)) / 2.0
        r.loc[dd] = ra + rp - t * tc
        turn.loc[dd] = t
        prev_w = W.loc[dd].copy(); prev_p = pk.loc[dd]
    yrs = (cal[-1] - cal[0]).days / 365.25
    return r, turn.sum() / yrs

def overlay(delta_vehicle):
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev * dv

def metrics(r):
    r = r.dropna(); nv = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nv.iloc[-1] ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (nv / nv.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, (cagr / abs(dd) if dd < 0 else np.nan)

def show(name, r):
    for tag, rr in [("FULL", r), ("IS", r[r.index <= IS_END]), ("OOS", r[r.index > IS_END])]:
        c, sh, dd, ca = metrics(rr)
        print(f"{name:<52}{tag:<5}{c:>7.2f}%{sh:>7.2f}{dd:>8.1f}%{ca:>7.2f}")
    print()

# self-check A
r_id = overlay(r_c30v - r_c30v)
assert float((r_id - r_base).abs().max()) == 0.0, "overlay identity broken"
print("SELF-CHECK A: overlay identity 0 VND OK")

hdr = f"{'config':<52}{'win':<5}{'CAGR':>8}{'Sharpe':>7}{'MaxDD':>9}{'Calmar':>7}"
print("\n" + hdr); print("-" * len(hdr))
show("R3 baseline (custom30V parking)", r_base)

rv_cont, turn_c = vehicle(flat_mask=None)
r_cont = overlay(rv_cont - r_c30v)
show(f"CONTINUOUS spec (overlay da pin) | turn {turn_c:.2f}x", r_cont)
c_full = metrics(r_cont)[0]
assert 27.0 < c_full < 28.2, f"SELF-CHECK C FAIL: continuous FULL {c_full:.2f} ngoai range CAU 0"
print(f"SELF-CHECK C: continuous FULL CAGR {c_full:.2f}% khop range CAU 0 (27.54-27.56) OK\n")

rv_bin, turn_b = vehicle(flat_mask=deal_mask)
r_bin = overlay(rv_bin - r_c30v)
show(f"BINARY trigger (paper wire) +whipsawTC | turn {turn_b:.2f}x", r_bin)

rv_bin0, _ = vehicle(flat_mask=deal_mask, tc=0.0)
rv_cont0, _ = vehicle(flat_mask=None, tc=0.0)
r_bin0 = overlay(rv_bin0 - r_c30v)
r_cont0 = overlay(rv_cont0 - r_c30v)
show("BINARY noTC (diagnostic)", r_bin0)
show("CONTINUOUS noTC (diagnostic)", r_cont0)

def yearly(r): return (1 + r).groupby(r.index.year).prod() - 1
yb, yc, ybn = yearly(r_bin), yearly(r_cont), yearly(r_base)
print("year  base_R3   continuous  binary   delta(cont-bin)pp")
for y in yc.index:
    print(f"{y}  {ybn[y]*100:8.2f}%  {yc[y]*100:8.2f}%  {yb[y]*100:8.2f}%   {(yc[y]-yb[y])*100:+.2f}")
cap_full = (metrics(r_bin)[0] - metrics(r_base)[0]) / max(metrics(r_cont)[0] - metrics(r_base)[0], 1e-9)
print(f"\nedge-capture binary/continuous (FULL CAGR delta ratio): {cap_full*100:.0f}%")
