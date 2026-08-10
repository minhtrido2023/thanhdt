#!/usr/bin/env python3
"""LAG/PEAD — chi phi co hoi cua viec vao lenh TRE trong cua so entry V2.4.

CAU HOI: cua so entry LAG = phien chuan (T+5 sau Release_Date) + toi da 2 phien ke tiep.
Luat V2.4 (user duyet 2026-08-09): phien 2/3 CHI duoc vao neu gia live <= entry_anchor_price
(= gia THO `Price` cua phien chuan). Ngay THOAT van neo theo lich entry chuan (hold 25 phien
tinh tu phien chuan) => vao tre vua MAT k phien drift dau, vua BI RUT NGAN thoi gian nam.

Do 3 nhanh, tren CUNG tap su kien:
  A_k  "CHASE"  : luon vao o phien e+k, gia thi truong (khong tran)
  B_k  "ANCHOR" : chi vao o phien e+k neu Price[e+k] <= Price[e] (dung luat hien tai)
  (k = 0,1,2 = phien 1,2,3 cua cua so)

Loi nhuan tinh tren Close (da dieu chinh co tuc = total return); cong tac chan (fill gate)
tinh tren Price (gia tho) — DUNG y he sinh anchor live (`mike/bin/lag_entry_anchor.py`).

Exit = e+25 phien (neo lich chuan) cho MOI nhanh => so sanh cong bang.

KHONG dung profit_* (no look-ahead). Su kien = (ticker, Release_Date) doc lap.
"""
import os
import sys
import pickle

import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
os.chdir(WC)

from simulate_holistic_nav import bq  # noqa: E402

START_DATE = "2014-01-02"
HOLD = 25          # phien nam, neo theo lich entry chuan (pt_v23_audit_2014.py lag_signal_rule)
ENTRY_OFF = 5      # Release_Date + 5 phien = phien entry chuan
MAX_LATE = 2       # cua so = phien chuan + 2 phien (LATE_WINDOW_SESSIONS)

# ─────────────────────────────── 1. Tap su kien LAG (sao y engine production)
print("[1] Dung tap su kien LAG (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5, forensic gate ON)...")
with open("data/earnings_surprise_data.pkl", "rb") as f:
    fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1", "NP_P2", "NP_P3", "NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"])
                        / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)

ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker", "quarter", "Release_Date", "surprise_B_MA"]],
                    on=["ticker", "quarter", "Release_Date"], how="left")
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)

LN2, HL = np.log(2), 3.0
ev["prior_n_good"] = 0
ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]
        cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist])
            pa = np.array([p for _, p in hist])
            w = np.exp(-LN2 * ((cur - da).days.values / 365.25) / HL)
            ev.at[ri, "pa_HL3"] = (pa * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))

_forx = {}
try:
    _ff = pd.read_csv("data/forensic_flags.csv")
    _forx = {r["ticker"]: pd.Timestamp(r["date"]) for _, r in _ff.iterrows()
             if str(r["severity"]).strip() == "exclude"}
except Exception:
    pass
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk])
                 for tk, rd in zip(ev["ticker"], ev["Release_Date"])]

_m = (ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & (~ev["_forbid"])
e_hl3 = ev[_m].copy()
print(f"    su kien qua gate: {len(e_hl3)}")

# ─────────────────────────────── 2. Panel gia
tickers = sorted(e_hl3["ticker"].unique().tolist())
print(f"[2] Keo panel gia cho {len(tickers)} ma tu BQ...")
tk_list = ",".join(f'"{t}"' for t in tickers)
px = bq(f"""
SELECT t.ticker, t.time, t.Close, t.Price
FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tk_list})
  AND t.time >= DATE '2013-06-01'
  AND t.Close IS NOT NULL AND t.Price IS NOT NULL AND t.Close > 0 AND t.Price > 0
""")
px["time"] = pd.to_datetime(px["time"])
px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
print(f"    {len(px):,} dong gia")

# lich giao dich chung (union moi ngay co gia) — dung de offset phien
all_dates = np.array(sorted(px["time"].unique()), dtype="datetime64[ns]")


def offset_date(ref, off):
    pos = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(all_dates[tgt]) if 0 <= tgt < len(all_dates) else None


# index nhanh: (ticker, time) -> (Close, Price); va vi tri phien theo tung ma
by_tk = {tk: g.reset_index(drop=True) for tk, g in px.groupby("ticker")}
tk_pos = {}
for tk, g in by_tk.items():
    tk_pos[tk] = {t: i for i, t in enumerate(g["time"].values)}

sw = pd.Timestamp(START_DATE)

# ─────────────────────────────── 3. Do tung su kien
rows = []
for _, r in e_hl3.iterrows():
    tk = r["ticker"]
    g = by_tk.get(tk)
    if g is None:
        continue
    entry = offset_date(r["Release_Date"], ENTRY_OFF)
    if entry is None or entry < sw:
        continue
    posmap = tk_pos[tk]
    # vi tri phien chuan TRONG chuoi gia cua chinh ma do (ma nghi giao dich se lech -> bo)
    i0 = posmap.get(np.datetime64(entry))
    if i0 is None:
        continue
    i_exit = i0 + HOLD
    if i_exit >= len(g):
        continue
    c = g["Close"].values
    p = g["Price"].values
    anchor = p[i0]
    px_exit = c[i_exit]
    rec = {"ticker": tk, "release": r["Release_Date"], "entry": entry,
           "year": entry.year, "surprise": r["surprise_B_MA"], "np_r": r["NP_R"]}
    for k in range(0, MAX_LATE + 1):
        ik = i0 + k
        if ik >= len(g):
            rec[f"ret_chase_{k}"] = np.nan
            rec[f"fill_anchor_{k}"] = np.nan
            rec[f"ret_anchor_{k}"] = np.nan
            rec[f"px_prem_{k}"] = np.nan
            continue
        rec[f"ret_chase_{k}"] = px_exit / c[ik] - 1.0
        # cong chan anchor: gia THO phien e+k <= anchor (gia tho phien chuan)
        filled = bool(p[ik] <= anchor + 1e-9)
        rec[f"fill_anchor_{k}"] = filled
        rec[f"ret_anchor_{k}"] = (px_exit / c[ik] - 1.0) if filled else np.nan
        rec[f"px_prem_{k}"] = p[ik] / anchor - 1.0   # % phai tra them so voi anchor
    rows.append(rec)

df = pd.DataFrame(rows)
print(f"[3] su kien do duoc: {len(df)}  |  ma doc nhat: {df['ticker'].nunique()}  "
      f"|  ngay release doc nhat: {df['release'].nunique()}")
os.makedirs(os.path.join(WC, "mike/agents/Taylor/exp_lag_entrylag_20260810"), exist_ok=True)
out = os.path.join(WC, "mike/agents/Taylor/exp_lag_entrylag_20260810/exp_lag_entry_lag_events.csv")
df.to_csv(out, index=False)
print(f"    -> {out}")

# ─────────────────────────────── 4. Bao cao
N = len(df)
print("\n" + "=" * 78)
print("KET QUA — LAG/PEAD, exit NEO theo lich entry chuan (e+25 phien)")
print("=" * 78)
print(f"N (su kien doc lap) = {N}   ({df['ticker'].nunique()} ma, "
      f"{df['release'].nunique()} ngay cong bo doc nhat, {df['year'].min()}-{df['year'].max()})")
print()
print(f"{'phien':<8}{'nhanh':<10}{'fill%':>8}{'ret|fill':>11}{'median':>10}"
      f"{'ret*fill':>11}{'premium':>10}")
print("-" * 78)
base = None
for k in range(0, MAX_LATE + 1):
    rc = df[f"ret_chase_{k}"].dropna()
    mc = rc.mean()
    if k == 0:
        base = mc
    print(f"{'e+'+str(k):<8}{'CHASE':<10}{100.0:>7.1f}%{mc*100:>10.2f}%"
          f"{rc.median()*100:>9.2f}%{mc*100:>10.2f}%{'':>10}")
    fa = df[f"fill_anchor_{k}"].dropna().astype(bool)
    ra = df[f"ret_anchor_{k}"].dropna()
    fr = fa.mean() if len(fa) else np.nan
    ma = ra.mean() if len(ra) else np.nan
    eff = fr * ma if len(ra) else np.nan
    prem = df[f"px_prem_{k}"].dropna()
    print(f"{'':<8}{'ANCHOR':<10}{fr*100:>7.1f}%{ma*100:>10.2f}%"
          f"{ra.median()*100:>9.2f}%{eff*100:>10.2f}%{prem.mean()*100:>9.2f}%")
print("-" * 78)
print("ret|fill = loi nhuan TRUNG BINH tren cac su kien CO khop")
print("ret*fill = loi nhuan tren VON GIAO cho sleeve (khong khop = tien nam im, 0%)")
print("premium  = gia tho phien do / anchor - 1 (trung binh)")

# so sanh truc tiep tai phien 3 (k=2) — dung ca hom nay
print("\n" + "=" * 78)
print("SO SANH QUYET DINH — tai PHIEN 3 cua cua so (k=2), dung tinh huong 2026-08-10")
print("=" * 78)
k = 2
sub = df.dropna(subset=[f"ret_chase_{k}", f"fill_anchor_{k}"]).copy()
fa = sub[f"fill_anchor_{k}"].astype(bool)
print(f"N = {len(sub)}")
print(f"  CHASE  (luon mua): fill 100.0%  ret {sub[f'ret_chase_{k}'].mean()*100:6.2f}%  "
      f"-> von: {sub[f'ret_chase_{k}'].mean()*100:6.2f}%")
print(f"  ANCHOR (luat nay): fill {fa.mean()*100:5.1f}%  "
      f"ret {sub.loc[fa, f'ret_chase_{k}'].mean()*100:6.2f}%  "
      f"-> von: {fa.mean()*sub.loc[fa, f'ret_chase_{k}'].mean()*100:6.2f}%")
print(f"  (nhom BI CHAN lai: n={int((~fa).sum())}, "
      f"neu mua thi ret {sub.loc[~fa, f'ret_chase_{k}'].mean()*100:6.2f}%)")

# t-test cap: nhom bi chan co te hon nhom duoc phep khong?
from scipy import stats  # noqa: E402
a = sub.loc[fa, f"ret_chase_{k}"].values
b = sub.loc[~fa, f"ret_chase_{k}"].values
if len(a) > 5 and len(b) > 5:
    t, pv = stats.ttest_ind(a, b, equal_var=False)
    print(f"  Welch t-test (duoc-phep vs bi-chan): t={t:.2f}  p={pv:.4f}")

# theo nam (leave-one-out kiem tra edge co bi 1-2 nam ganh khong)
print("\nTHEO NAM (k=2):")
print(f"{'nam':<7}{'N':>5}{'fill%':>8}{'CHASE von':>11}{'ANCHOR von':>12}{'chenh':>9}")
for y, gg in sub.groupby("year"):
    f2 = gg[f"fill_anchor_{k}"].astype(bool)
    ch = gg[f"ret_chase_{k}"].mean()
    an = f2.mean() * gg.loc[f2, f"ret_chase_{k}"].mean() if f2.any() else 0.0
    print(f"{y:<7}{len(gg):>5}{f2.mean()*100:>7.1f}%{ch*100:>10.2f}%{an*100:>11.2f}%"
          f"{(ch-an)*100:>8.2f}%")
