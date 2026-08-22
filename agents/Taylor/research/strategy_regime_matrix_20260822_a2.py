#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A2 — Ma tran FORWARD-HORIZON (DT5G x Value Radar) + hang PARKING/CAPIT.
Job Taylor_20260822_131318.

Khac ma tran goc (job Taylor_20260822_101400): ma tran goc do return DONG THOI trong o
(dieu kien tren viec DANG o trong o). A2 do return PHIA TRUOC ke tu phien BUOC VAO o
=> tra loi duoc "vao o nay thi 60/120/250 phien sau ra sao", la cau hoi dung cho quyet dinh.

Nguon: panel_daily.csv (job truoc, tu pin R3 CANONICAL, self-check 0 VND da chay o job do)
     + a1_daily.csv (ro parking custom30V PIT, self-check 0 VND chay o A1)
     + EVENT_CAPIT tu CHINH file pin R3 (18 lan fire, cung backtest => nhat quan).
KHONG dung cot profit_* (forward-looking).
"""
import os, sys
import numpy as np, pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
PIN = os.path.join(W, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_repin0803_price_univpit.csv")
HZ = [60, 120, 250]

# ------------------------------------------------------------------ 1. panel
d = pd.read_csv(os.path.join(OUT, "panel_daily.csv"), parse_dates=["time"]).sort_values("time")
d = d.reset_index(drop=True)
assert len(d) == 3107, len(d)
print(f"[data] panel {len(d)} phien {d.time.min().date()} -> {d.time.max().date()}")

# NAV level cho tung chien luoc. nav_*_ref = so cai tham chieu 25B doc lap cua tung so
# (return thuan cua so, khong bi allocator rebalance lam nhay) — dung dung nhu job truoc.
lvl = pd.DataFrame({"time": d.time})
lvl["BAL"] = d.nav_bal_ref.values
lvl["LAG"] = d.nav_lag_ref.values
lvl["COMB"] = d.combined_nav.values
lvl["VNI"] = d.vni_close.values

# PARK: dung ro custom30V PIT tu A1 (self-check 0 VND). Chi co tu 2014-08-05.
a1 = pd.read_csv(os.path.join(OUT, "a1_daily.csv"), parse_dates=["time"])[["time", "r_base"]]
lvl = lvl.merge(a1, on="time", how="left")
r = lvl.r_base.copy()
first = r.first_valid_index()
park = pd.Series(np.nan, index=lvl.index)
park.loc[first:] = 1e9 * (1 + r.loc[first:].fillna(0)).cumprod()
lvl["PARK"] = park
lvl = lvl.drop(columns=["r_base"]).set_index("time")
print(f"[data] PARK co tu {lvl.PARK.first_valid_index().date()} "
      f"({int(lvl.PARK.notna().sum())} phien) — ro custom30V PIT, self-check 0 VND (A1)")

d["cell"] = d.regime + "|" + d.zone
cell = pd.Series(d.cell.values, index=d.time.values)

# ------------------------------------------------------------------ 2. forward return
def fwd(series, i, h):
    """return tu DONG CUA phien i den dong cua phien i+h. Khong nhin truoc: o duoc quan sat
    tai dong cua i, vao lenh tu i (hoac T+1 — chenh 1 phien, khong doi ket luan o 60/120/250)."""
    if i + h >= len(series):
        return np.nan
    a, b = series.iloc[i], series.iloc[i + h]
    if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
        return np.nan
    return b / a - 1.0

STRATS = ["BAL", "LAG", "COMB", "PARK", "VNI"]
entries = cell.ne(cell.shift())          # phien DAU TIEN cua moi lan o o do
entries.iloc[0] = True
ent_idx = np.where(entries.values)[0]
print(f"[entries] tong so lan BUOC VAO mot o = {len(ent_idx)}")

recs = []
for i in ent_idx:
    row = {"i": i, "time": d.time.iloc[i], "cell": d.cell.iloc[i],
           "regime": d.regime.iloc[i], "zone": d.zone.iloc[i]}
    for h in HZ:
        for s in STRATS:
            row[f"{s}_{h}"] = fwd(lvl[s], i, h)
    recs.append(row)
E = pd.DataFrame(recs)
E.to_csv(os.path.join(OUT, "a2_entries.csv"), index=False)

# ------------------------------------------------------------------ 3. ma tran
rows = []
for (rg, zn), g in E.groupby(["regime", "zone"]):
    for h in HZ:
        rec = {"regime": rg, "zone": zn, "horizon": h, "n_entries": len(g)}
        vni = g[f"VNI_{h}"]
        rec["n_full"] = int(vni.notna().sum())
        rec["VNI_med"] = vni.median()
        for s in ["BAL", "LAG", "COMB", "PARK"]:
            v = g[f"{s}_{h}"]
            ok = v.notna() & vni.notna()
            rec[f"{s}_n"] = int(ok.sum())
            rec[f"{s}_med"] = v[ok].median() if ok.any() else np.nan
            rec[f"{s}_p_pos"] = float((v[ok] > 0).mean()) if ok.any() else np.nan
            rec[f"{s}_p_beat"] = float((v[ok] > vni[ok]).mean()) if ok.any() else np.nan
        rows.append(rec)
# hang tong theo regime (moi zone)
for rg, g in E.groupby("regime"):
    for h in HZ:
        rec = {"regime": rg, "zone": "*ALL*", "horizon": h, "n_entries": len(g)}
        vni = g[f"VNI_{h}"]; rec["n_full"] = int(vni.notna().sum()); rec["VNI_med"] = vni.median()
        for s in ["BAL", "LAG", "COMB", "PARK"]:
            v = g[f"{s}_{h}"]; ok = v.notna() & vni.notna()
            rec[f"{s}_n"] = int(ok.sum())
            rec[f"{s}_med"] = v[ok].median() if ok.any() else np.nan
            rec[f"{s}_p_pos"] = float((v[ok] > 0).mean()) if ok.any() else np.nan
            rec[f"{s}_p_beat"] = float((v[ok] > vni[ok]).mean()) if ok.any() else np.nan
        rows.append(rec)
M = pd.DataFrame(rows).sort_values(["regime", "zone", "horizon"])
M.to_csv(os.path.join(OUT, "forward_matrix.csv"), index=False)

pd.set_option("display.width", 260, "display.max_columns", 60, "display.max_rows", 200)
print("\n=== A2 MA TRAN FORWARD (median %, n = so lan buoc vao o co du horizon) ===")
sh = M[["regime", "zone", "horizon", "n_entries", "n_full", "VNI_med",
        "COMB_med", "COMB_p_pos", "COMB_p_beat", "BAL_med", "LAG_med", "PARK_med", "PARK_n"]].copy()
for c in ["VNI_med", "COMB_med", "BAL_med", "LAG_med", "PARK_med"]:
    sh[c] = (sh[c] * 100).round(1)
for c in ["COMB_p_pos", "COMB_p_beat"]:
    sh[c] = (sh[c] * 100).round(0)
print(sh.to_string(index=False))

# ------------------------------------------------------------------ 4. NEUTRAL+RE deep dive
print("\n=== A2 §3 — O HIEN TAI (NEUTRAL + RE): phan phoi forward, khong chi median ===")
QS = [0, 10, 25, 50, 75, 90, 100]
dist = []
for zn in ["RE", "TRUNGTINH", "DAT"]:
    g = E[(E.regime == "NEUTRAL") & (E.zone == zn)]
    for h in HZ:
        for s in ["COMB", "VNI", "PARK"]:
            v = g[f"{s}_{h}"].dropna()
            if len(v) == 0: continue
            row = {"zone": zn, "horizon": h, "strat": s, "n": len(v)}
            for q in QS:
                row[f"p{q}"] = round(float(np.percentile(v, q)) * 100, 1)
            row["mean"] = round(float(v.mean()) * 100, 1)
            row["p_pos"] = round(float((v > 0).mean()) * 100, 0)
            dist.append(row)
D = pd.DataFrame(dist)
D.to_csv(os.path.join(OUT, "a2_neutral_distribution.csv"), index=False)
print(D.to_string(index=False))

print("\n--- histogram COMB fwd-250 theo zone trong NEUTRAL (bin 20pp) ---")
bins = [-1, -0.4, -0.2, -0.1, 0, 0.1, 0.2, 0.4, 0.8, 99]
lab = ["<-40", "-40..-20", "-20..-10", "-10..0", "0..10", "10..20", "20..40", "40..80", ">80"]
for zn in ["RE", "TRUNGTINH", "DAT"]:
    v = E[(E.regime == "NEUTRAL") & (E.zone == zn)]["COMB_250"].dropna()
    if len(v) == 0: continue
    c = pd.cut(v, bins=bins, labels=lab).value_counts().reindex(lab).fillna(0).astype(int)
    print(f"  {zn:10s} n={len(v):3d}  " + " ".join(f"{l}:{c[l]}" for l in lab if c[l]))

# ------------------------------------------------------------------ 5. CAPIT
print("\n=== A2 §2b — CAPIT: 18 lan fire (EVENT_CAPIT tu chinh pin R3) ===")
cols = ["record_type", "key", "value", "ymd", "book", "ticker", "action", "play_type",
        "holding_id", "shares", "adj_price", "buy_amount", "sell_amount", "fee", "cash_after",
        "reason", "state", "nav_bal_ref", "nav_lag_ref", "bal_cash_ref", "bal_stocks_ref",
        "bal_etf_ref", "lag_cash_ref", "lag_stocks_ref", "lag_etf_ref", "w_lag_tgt",
        "rebal_cost", "cap_bal", "cap_lag", "combined_nav", "vni_close"]
raw = pd.read_csv(PIN, names=cols, header=0, low_memory=False)
cap = raw[raw.record_type == "EVENT_CAPIT"].copy()
cap["time"] = pd.to_datetime(cap["ymd"]).dt.normalize()
cap["size"] = pd.to_numeric(cap["value"], errors="coerce")
pos = {t: i for i, t in enumerate(d.time)}
cr = []
for _, rr in cap.iterrows():
    i = pos.get(rr.time)
    if i is None:
        cr.append({"time": rr.time, "note": "khong co trong panel"}); continue
    rec = {"time": rr.time.date(), "size": rr["size"], "regime": d.regime.iloc[i],
           "zone": d.zone.iloc[i], "reason": str(rr.reason)}
    for h in HZ:
        rec[f"COMB_{h}"] = fwd(lvl["COMB"], i, h)
        rec[f"VNI_{h}"] = fwd(lvl["VNI"], i, h)
    cr.append(rec)
C = pd.DataFrame(cr)
C.to_csv(os.path.join(OUT, "a2_capit_events.csv"), index=False)
shc = C.copy()
for c in [f"{s}_{h}" for s in ("COMB", "VNI") for h in HZ]:
    if c in shc: shc[c] = (shc[c] * 100).round(1)
print(shc[["time", "size", "regime", "zone"] + [f"COMB_{h}" for h in HZ]
          + [f"VNI_{h}" for h in HZ]].to_string(index=False))
print("\n  gop theo O (n<5 => CHI LIET KE, KHONG p-value):")
for (rg, zn), g in C.groupby(["regime", "zone"]):
    s = f"    {rg}|{zn} n={len(g)}"
    for h in HZ:
        v, vv = g[f"COMB_{h}"].dropna(), g[f"VNI_{h}"].dropna()
        s += f" | fwd{h}: COMB med {v.median()*100:+.1f}% vs VNI {vv.median()*100:+.1f}%" if len(v) else ""
    print(s)
print(f"\n  size CAPIT theo o: " + str(C.groupby(['regime', 'zone'])['size'].apply(list).to_dict()))

# ------------------------------------------------------------------ 5b. BASELINE VO DIEU KIEN
# BAT BUOC doc truoc bang ma tran: he compound manh 12 nam nen HAU HET cua so 250 phien deu duong.
# p_pos ~100% o gan moi o KHONG phai tin hieu cua o — do la BASE RATE. Chi doc CHENH LECH vs day.
print("\n=== BASELINE VO DIEU KIEN (moi phien la 1 diem xuat phat) — day de tru ===")
bl = []
for h in HZ:
    row = {"horizon": h}
    for s in ["COMB", "BAL", "LAG", "PARK", "VNI"]:
        v = pd.Series([fwd(lvl[s], i, h) for i in range(len(lvl))]).dropna()
        row[f"{s}_med"] = round(float(v.median()) * 100, 1)
        row[f"{s}_ppos"] = round(float((v > 0).mean()) * 100, 0)
    bl.append(row)
B = pd.DataFrame(bl); print(B.to_string(index=False))
B.to_csv(os.path.join(OUT, "a2_baseline.csv"), index=False)

# ------------------------------------------------------------------ 5c. TAP CON KHONG CHONG LAN
# Greedy: quet theo thoi gian, giu 1 entry roi bo moi entry cach no < h phien. N nay moi la N doc lap.
print("\n=== TAP CON KHONG CHONG LAN (N doc lap that) — NEUTRAL x zone ===")
ni = []
for zn in ["RE", "TRUNGTINH", "DAT"]:
    g = E[(E.regime == "NEUTRAL") & (E.zone == zn)].sort_values("i")
    for h in HZ:
        gg = g.dropna(subset=[f"COMB_{h}"])
        keep, last = [], -10 ** 9
        for _, rr in gg.iterrows():
            if rr["i"] - last >= h:
                keep.append(rr); last = rr["i"]
        if not keep: continue
        K = pd.DataFrame(keep)
        ni.append({"zone": zn, "horizon": h, "n_all": len(gg), "n_indep": len(K),
                   "COMB_med_all": round(float(gg[f"COMB_{h}"].median()) * 100, 1),
                   "COMB_med_indep": round(float(K[f"COMB_{h}"].median()) * 100, 1),
                   "VNI_med_indep": round(float(K[f"VNI_{h}"].median()) * 100, 1),
                   "PARK_med_indep": round(float(K[f"PARK_{h}"].dropna().median()) * 100, 1)
                                     if K[f"PARK_{h}"].notna().any() else None})
NI = pd.DataFrame(ni); print(NI.to_string(index=False))
NI.to_csv(os.path.join(OUT, "a2_nonoverlap.csv"), index=False)

# ------------------------------------------------------------------ 6. canh bao chong lan
print("\n=== CANH BAO DOC LAP ===")
for h in HZ:
    for zn in ["RE", "TRUNGTINH", "DAT"]:
        g = E[(E.regime == "NEUTRAL") & (E.zone == zn)]
        t = g.dropna(subset=[f"COMB_{h}"])["i"].values
        if len(t) < 2: continue
        gap = np.diff(np.sort(t))
        ov = int((gap < h).sum())
        print(f"  NEUTRAL|{zn:10s} h={h:3d}: n={len(t):3d}, "
              f"{ov}/{len(gap)} cap ke tiep cach nhau < {h} phien => CHONG LAN "
              f"(median gap {int(np.median(gap))} phien)")
print("\n[done]", OUT)
