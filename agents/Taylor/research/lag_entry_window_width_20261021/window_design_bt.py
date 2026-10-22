#!/usr/bin/env python3
"""C — thiết kế độ rộng cửa sổ entry LAG dưới Luật A (event study, KHÔNG phải NAV). Theo PREREG.md.

Tập sự kiện sao y exp_lag_entrylag_20260810/measure_entry_lag.py (luật engine). OHLC thô suy ra
= OHLC_adj × Price/Close cùng ngày. ref_k = Price thô phiên trước (XẤP XỈ giá tham chiếu).
Chạy: /home/trido/thanhdt/wc_venv/bin/python window_design_bt.py
"""
import os, sys, pickle
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC); os.chdir(WC)
from simulate_holistic_nav import bq  # noqa: E402

START_DATE, HOLD, ENTRY_OFF, KMAX = "2014-01-02", 25, 5, 4
TAU, LOCK = 0.03, 0.065
SEED, NB = 20261021, 2000

# ---------------- 1. sự kiện (sao y measure_entry_lag.py)
fin = pickle.load(open("data/earnings_surprise_data.pkl", "rb"))
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker", "Release_Date"]).reset_index(drop=True)
LN2, HL = np.log(2), 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri, "prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d, _ in hist]); pa = np.array([p for _, p in hist])
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
ev["_forbid"] = [(tk in _forx) and (rd >= _forx[tk]) for tk, rd in zip(ev["ticker"], ev["Release_Date"])]
e = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5) & (~ev["_forbid"])].copy()
print(f"[1] sự kiện qua gate: {len(e)}")

# ---------------- 2. panel giá OHLC
tks = ",".join(f"'{t}'" for t in sorted(e["ticker"].unique()))
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.High, t.Low, t.Close, t.Price
FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tks}) AND t.time >= DATE '2013-06-01'
AND t.Close > 0 AND t.Price > 0""")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values(["ticker", "time"]).reset_index(drop=True)
all_dates = np.array(sorted(px["time"].unique()), dtype="datetime64[ns]")
by = {tk: g.reset_index(drop=True) for tk, g in px.groupby("ticker")}
pos = {tk: {t: i for i, t in enumerate(g["time"].values)} for tk, g in by.items()}
print(f"[2] {len(px):,} dòng giá")


def off(ref, k):
    p = np.searchsorted(all_dates, np.datetime64(ref), side="right") - 1 + k
    return pd.Timestamp(all_dates[p]) if 0 <= p < len(all_dates) else None


# ---------------- 3. đo từng sự kiện: mỗi phiên k=0..4 → fill_A, px khớp, lock
rec = []
for _, r in e.iterrows():
    tk = r["ticker"]; g = by.get(tk)
    ent = off(r["Release_Date"], ENTRY_OFF)
    if g is None or ent is None or ent < pd.Timestamp(START_DATE):
        continue
    i0 = pos[tk].get(np.datetime64(ent))
    if i0 is None or i0 < 1 or i0 + KMAX + HOLD >= len(g):
        continue
    C, P = g["Close"].values, g["Price"].values
    f = P / C                                          # adj → thô
    O = g["Open"].values * f; H = g["High"].values * f; L = g["Low"].values * f
    d = {"ticker": tk, "release": r["Release_Date"], "entry": ent, "year": ent.year}
    for k in range(KMAX + 1):
        i = i0 + k; ref = P[i - 1]
        lock = bool(abs(H[i] - L[i]) < 1e-6 * P[i] and P[i] / ref - 1 >= LOCK)
        ceil = ref * (1 + TAU)
        fillA = (not lock) and (L[i] <= ceil + 1e-9)
        pA = min(P[i], ceil)                           # giá khớp thô dưới Luật A
        # quy về adj để tính lợi nhuận tổng (Close đã điều chỉnh cổ tức)
        d[f"lock{k}"] = lock
        d[f"fA{k}"] = fillA
        d[f"buyA{k}"] = pA / f[i]                      # adj
        d[f"buyN{k}"] = C[i]                           # NONE: khớp ở Close
        d[f"buyO{k}"] = g["Open"].values[i]            # NONE độ nhạy: Open (engine)
        d[f"exA{k}"] = C[i0 + HOLD]                    # thoát neo lịch chuẩn
        d[f"exS{k}"] = C[i + HOLD]                     # thoát dời theo entry thật
        d[f"prem{k}"] = P[i] / ref - 1
        d[f"Or{k}"], d[f"Lr{k}"], d[f"ref{k}"], d[f"f{k}"] = O[i], L[i], ref, f[i]
    d["anchor"] = P[i0]
    rec.append(d)
df = pd.DataFrame(rec)
df.to_csv(f"{OUT}/exp_window_events.csv", index=False)
N, NC = len(df), df["release"].nunique()
print(f"[3] N sự kiện={N} | mã={df['ticker'].nunique()} | cụm ngày công bố={NC}")


def event_ret(W, ceil, exitm, d1_uncapped=False, buy="N"):
    """lợi nhuận trên vốn giao/sự kiện: phiên đầu tiên k<W khớp được; không khớp ⇒ 0."""
    out = np.zeros(N); filled = np.zeros(N, bool); kk = np.full(N, -1)
    for k in range(W):
        lock = df[f"lock{k}"].values
        if ceil == "A" and not (d1_uncapped and k == 0):
            can = df[f"fA{k}"].values; b = df[f"buyA{k}"].values
        else:
            can = ~lock; b = df[f"buy{buy}{k}"].values
        x = df[f"exA{k}" if exitm == "ANCH" else f"exS{k}"].values
        new = can & ~filled
        out[new] = x[new] / b[new] - 1; kk[new] = k; filled |= new
    return out, filled, kk



def event_ret_open(W, ceil, exitm, d1_uncapped=False):
    """HIỆU CHỈNH sau khi chạy (khai trong REPORT): cơ sở khớp CHUNG = Open thô cho mọi biến thể.
    Trần c: Open<=c ⇒ khớp Open; Open>c>=Low ⇒ khớp c; Low>c ⇒ không khớp. Khoá trần ⇒ không khớp.
    ceil: NONE | A (ref×1,03 mọi phiên) | LEGACY (phiên 1 không trần, phiên 2+ trần = anchor)."""
    out = np.zeros(N); filled = np.zeros(N, bool); kk = np.full(N, -1)
    for k in range(W):
        O_, L_, f_ = df[f"Or{k}"].values, df[f"Lr{k}"].values, df[f"f{k}"].values
        lock = df[f"lock{k}"].values
        if ceil == "NONE" or (k == 0 and (d1_uncapped or ceil == "LEGACY")):
            c = np.full(N, np.inf)
        elif ceil == "A":
            c = df[f"ref{k}"].values * (1 + TAU)
        else:
            c = df["anchor"].values
        can = ~lock & (L_ <= c + 1e-9)
        b_raw = np.where(O_ <= c, O_, c)
        b = b_raw / f_
        x = df[f"exA{k}" if exitm == "ANCH" else f"exS{k}"].values
        new = can & ~filled
        out[new] = x[new] / b[new] - 1; kk[new] = k; filled |= new
    return out, filled, kk


cl = df["release"].values
uc, cidx = np.unique(cl, return_inverse=True)
rng = np.random.default_rng(SEED)
BOOT = [rng.integers(0, len(uc), len(uc)) for _ in range(NB)]
cnt_c = np.bincount(cidx, minlength=len(uc))


def cboot(v):
    s = np.bincount(cidx, weights=v, minlength=len(uc))
    m = np.array([s[b].sum() / cnt_c[b].sum() for b in BOOT])
    return np.percentile(m, [2.5, 97.5])


cfgs = []
for ceil in ("NONE", "A"):
    for exitm in ("ANCH", "SHIFT"):
        for W in (1, 3, 4, 5):
            cfgs.append((f"W{W}·{ceil}·{exitm}", W, ceil, exitm, False))
for W in (1, 3, 4, 5):
    cfgs.append((f"W{W}·A(d1 không trần)·ANCH", W, "A", "ANCH", True))
assert len(cfgs) == 20

res = {c[0]: event_ret(c[1], c[2], c[3], c[4]) for c in cfgs}
base = res["W3·A·ANCH"][0]
yrs = df["year"].values
IS = yrs <= 2019
print("\n" + "=" * 118)
print(f"{'cấu hình':<28}{'fill%':>7}{'ret|fill':>10}{'trên vốn':>10}{'CI95 cụm':>18}"
      f"{'Δ vs W3·A·ANCH':>16}{'CI95 Δ':>18}{'ΔIS':>7}{'ΔOOS':>7}{'LOYO Δ min..max':>18}")
rows = []
for name, *_ in cfgs:
    v, fl, kk = res[name]
    m = v.mean(); lo, hi = cboot(v)
    dlt = v - base; dm = dlt.mean(); dlo, dhi = cboot(dlt)
    loyo = [dlt[yrs != y].mean() for y in np.unique(yrs)]
    rf = v[fl].mean() if fl.any() else np.nan
    print(f"{name:<28}{fl.mean()*100:6.1f}%{rf*100:9.2f}%{m*100:9.2f}%  [{lo*100:5.2f},{hi*100:5.2f}]"
          f"{dm*100:+14.2f}pp  [{dlo*100:+5.2f},{dhi*100:+5.2f}]{dlt[IS].mean()*100:+7.2f}{dlt[~IS].mean()*100:+7.2f}"
          f"   {min(loyo)*100:+5.2f}..{max(loyo)*100:+5.2f}")
    rows.append({"cfg": name, "fill_pct": fl.mean(), "ret_given_fill": rf, "ret_on_capital": m, "ci_lo": lo,
                 "ci_hi": hi, "delta_vs_W3A": dm, "d_ci_lo": dlo, "d_ci_hi": dhi, "d_IS": dlt[IS].mean(),
                 "d_OOS": dlt[~IS].mean(), "loyo_min": min(loyo), "loyo_max": max(loyo),
                 "k_dist": np.bincount(kk[kk >= 0], minlength=5).tolist()})
pd.DataFrame(rows).to_csv(f"{OUT}/exp_window_grid.csv", index=False)

# --- độ nhạy engine: NONE·W5·SHIFT khớp ở Open (giống engine) vs Close
v, fl, _ = event_ret(5, "NONE", "SHIFT", buy="O")
print(f"\n[độ nhạy] W5·NONE·SHIFT khớp ở OPEN (≈engine pin): trên vốn {v.mean()*100:.2f}%  CI{np.round(cboot(v)*100,2).tolist()}"
      f"  Δ vs W3·A·ANCH {(v-base).mean()*100:+.2f}pp CI{np.round(cboot(v-base)*100,2).tolist()}")

# --- mô tả cửa sổ: tỷ lệ khoá trần + tỷ lệ bị Luật A chặn mỗi phiên
print("\n[mô tả] theo phiên k (phiên k+1 của cửa sổ):")
for k in range(KMAX + 1):
    print(f"  k={k}: khoá trần biên độ {df[f'lock{k}'].mean()*100:5.2f}% | Luật A KHÔNG khớp {100-df[f'fA{k}'].mean()*100:5.2f}% "
          f"| premium thô vs ref TB {df[f'prem{k}'].mean()*100:+.2f}%")
# --- phần cận biên: sự kiện CHỈ khớp được nhờ phiên 4-5
v3, f3, _ = res["W3·A·ANCH"]; v5, f5, k5 = res["W5·A·ANCH"]
extra = f5 & ~f3
print(f"\n[cận biên W5 vs W3, A·ANCH] sự kiện thêm được khớp: {extra.sum()} ({extra.mean()*100:.2f}% N); "
      f"ret TB của chúng {v5[extra].mean()*100:.2f}% (neo lịch ⇒ chỉ còn {HOLD-3}-{HOLD-4} phiên nắm)")
v1, f1, _ = res["W1·A·ANCH"]
ex13 = f3 & ~f1
print(f"[cận biên W3 vs W1, A·ANCH] sự kiện thêm được khớp: {ex13.sum()} ({ex13.mean()*100:.2f}% N); ret TB {v3[ex13].mean()*100:.2f}%")


print("\n" + "=" * 118)
print("BẢNG CHÍNH (HIỆU CHỈNH) — cơ sở khớp chung = OPEN thô; baseline = W3·A·ANCH (live hiện hành)")
cf2 = []
for ceil in ("NONE", "A", "LEGACY"):
    for exitm in ("ANCH", "SHIFT"):
        for W in (1, 3, 4, 5):
            cf2.append((f"W{W}·{ceil}·{exitm}", W, ceil, exitm, False))
for W in (1, 3, 4, 5):
    cf2.append((f"W{W}·A(d1 không trần)·ANCH", W, "A", "ANCH", True))
r2 = {c[0]: event_ret_open(c[1], c[2], c[3], c[4]) for c in cf2}
base2 = r2["W3·A·ANCH"][0]
print(f"{'cấu hình':<28}{'fill%':>7}{'ret|fill':>10}{'trên vốn':>10}{'CI95 cụm':>18}"
      f"{'Δ vs W3·A·ANCH':>16}{'CI95 Δ':>18}{'ΔIS':>7}{'ΔOOS':>7}{'LOYO Δ min..max':>18}")
rows2 = []
for name, *_ in cf2:
    v, fl, kk = r2[name]
    m = v.mean(); lo, hi = cboot(v); dlt = v - base2; dm = dlt.mean(); dlo, dhi = cboot(dlt)
    loyo = [dlt[yrs != y].mean() for y in np.unique(yrs)]
    rf = v[fl].mean() if fl.any() else np.nan
    print(f"{name:<28}{fl.mean()*100:6.1f}%{rf*100:9.2f}%{m*100:9.2f}%  [{lo*100:5.2f},{hi*100:5.2f}]"
          f"{dm*100:+14.2f}pp  [{dlo*100:+5.2f},{dhi*100:+5.2f}]{dlt[IS].mean()*100:+7.2f}{dlt[~IS].mean()*100:+7.2f}"
          f"   {min(loyo)*100:+5.2f}..{max(loyo)*100:+5.2f}")
    rows2.append({"cfg": name, "fill_pct": fl.mean(), "ret_given_fill": rf, "ret_on_capital": m, "ci_lo": lo,
                  "ci_hi": hi, "delta_vs_W3A": dm, "d_ci_lo": dlo, "d_ci_hi": dhi, "d_IS": dlt[IS].mean(),
                  "d_OOS": dlt[~IS].mean(), "loyo_min": min(loyo), "loyo_max": max(loyo),
                  "k_dist": np.bincount(kk[kk >= 0], minlength=5).tolist()})
pd.DataFrame(rows2).to_csv(f"{OUT}/exp_window_grid_openbasis.csv", index=False)
for nm in ("W1·A·ANCH", "W3·A·ANCH", "W5·A·ANCH", "W3·LEGACY·ANCH", "W5·NONE·SHIFT"):
    print(f"  phân bố phiên khớp {nm}: {[x for x in pd.DataFrame(rows2).set_index('cfg').loc[nm,'k_dist']]}")
# gói live tiền-Luật-A (LEGACY) so Luật A
d = r2["W3·A·ANCH"][0] - r2["W3·LEGACY·ANCH"][0]
print(f"  Luật A vs LEGACY(≤anchor phiên 2/3), W3·ANCH: {d.mean()*100:+.3f}pp CI{np.round(cboot(d)*100,3).tolist()}")
d = r2["W5·NONE·SHIFT"][0] - r2["W3·A·ANCH"][0]
print(f"  ENGINE-PIN proxy (W5·NONE·SHIFT, Open) − LIVE (W3·A·ANCH): {d.mean()*100:+.3f}pp CI{np.round(cboot(d)*100,3).tolist()}")
for W in (1, 4, 5):
    d = r2[f"W{W}·A·ANCH"][0] - base2
    print(f"  W{W} − W3 (A·ANCH): {d.mean()*100:+.3f}pp CI{np.round(cboot(d)*100,3).tolist()} ; "
          f"số sự kiện khác nhau {(r2[f'W{W}·A·ANCH'][1] != r2['W3·A·ANCH'][1]).sum()}")
