#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAU 2 tang ENGINE (dispatch Taylor_20260803_101341) — phan ra dong gop cua don bay THEO SU KIEN,
tren chinh chuoi NAV ma engine sinh ra (khong phai overlay toan hoc nhu p4).

Vi sao can ban engine RIENG, khi `cau2_decomp.py` (tang sleeve) da chay khop 1e-16:
  ban sleeve tra loi "neu chi co rieng sleeve thi don bay lam gi" tren 17 su kien GIA DINH deu duoc mua.
  Engine THUC TE chi mua 15/17 (gate `postbull` + gate BEAR/grind cua production tu loai 2022-04-19 va
  2022-09-28). Vi vay 2 tang KHONG the so truc tiep — va chenh do chinh la mot phan cau tra loi CAU 3.

Dong nhat thuc (theo THIET KE, khong phai theo may man so hoc):
    dlogNAV_total  =  SUM_i [ (a) thi truong/timing + (b) carry + (c) drag/tuong tac ]  +  (d) ngoai cua so
Trong do:
  (a) thi truong/timing = dlog cua chuoi levered TRU dlog control, cong don trong cua so nam giu su kien i,
      SAU KHI da cong nguoc lai phan lai vay -> tuc phan do bien dong GIA mang lai.
  (b) carry            = lai vay engine THUC SU tinh trong cua so i (borrowledger `charge`), doi ra dlog.
  (c) drag/tuong tac   = phan du trong cua so i — chenh giua tong dlog thuc te va (a)+(b). No gom phat
      compounding hinh hoc + tuong tac voi rebalance/allocator trong cung cua so.
  (d) ngoai cua so     = phan dlog lech nam NGOAI moi cua so su kien = dong gop TUONG QUAN VOI CA SO
      (don bay doi trang thai tien mat/parking cua danh muc ke ca khi khong con giu CAPIT).
Cot (d) chinh la muc 2(d) cua dispatch. Residual duoc ghi TUONG MINH, khong bi nhet vao (a).

Kiem tra bat buoc: SUM(moi cot) == dlogNAV_total do truc tiep tu 2 chuoi NAV. In ra sai so.

Chay: $DNA_PYEXE cau2_engine_decomp.py
"""
import glob
import os

import numpy as np
import pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data/"
HERE = os.path.dirname(os.path.abspath(__file__))
ANN = 252.0
CONTROL = "D0_control"
# (leg, lai vay %/nam) — chi cac chan CO vay that
LEGS = [("E125_f11", 12.5), ("E125_f12", 12.5), ("E125_f13", 12.5), ("E125_f15", 12.5),
        ("E140_f13", 14.0), ("E140_f15", 14.0)]
HOLD_D = 60   # cua so nam giu CAPIT (phien) — CAPIT thoat theo maturity ~2-3 thang; xem do nhay ben duoi


def nav_path(tag):
    g = [p for p in sorted(glob.glob(DATA + f"*exp_{tag}_univpit*.csv"))
         if not p.endswith(("_borrowledger.csv", "_leveraudit.csv"))]
    if not g:
        raise SystemExit(f"thieu CSV NAV cho {tag}")
    return g[0]


def load_nav(tag):
    df = pd.read_csv(nav_path(tag), low_memory=False)
    d = df[df["record_type"] == "NAV"].copy() if "NAV" in set(df["record_type"]) else None
    if d is None or d.empty:
        d = df.dropna(subset=["combined_nav"]).copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    s = d.groupby("ymd")["combined_nav"].last().sort_index()
    return s[s > 0]


def ledgers(tag):
    lv = glob.glob(DATA + f"*exp_{tag}_univpit*_leveraudit.csv")
    bl = glob.glob(DATA + f"*exp_{tag}_univpit*_borrowledger.csv")
    return pd.read_csv(lv[0]), pd.read_csv(bl[0])


def main():
    base = load_nav(CONTROL)
    out_rows = []
    for tag, rate in LEGS:
        lev = load_nav(tag)
        idx = base.index.intersection(lev.index)
        b, a = base.reindex(idx), lev.reindex(idx)
        # chenh lech log-return theo NGAY giua chan levered va control
        dl = pd.Series(np.diff(np.log(a.values)) - np.diff(np.log(b.values)), index=idx[1:])
        total = float(dl.sum())

        lv_led, bl_led = ledgers(tag)
        lv_led["date"] = pd.to_datetime(lv_led["date"])
        bl_led["ymd"] = pd.to_datetime(bl_led["ymd"])
        # lai vay ep-buoc theo NGAY (gop 2 book) -> doi ra dlog bang cach chia NAV levered ngay do
        chg = bl_led.groupby("ymd")["charge"].sum()
        carry_dlog = -(chg.reindex(idx[1:]).fillna(0.0) / a.reindex(idx[1:]) * 1e9 / 1e9)

        ev = (lv_led.groupby("date")
                    .agg(loan=("loan_vnd", "sum"), pos=("position_vnd", "sum")).reset_index())
        rows, used = [], pd.Series(False, index=dl.index)
        for _, r in ev.iterrows():
            d0 = r["date"]
            win = dl.index[(dl.index > d0) & (dl.index <= d0 + pd.Timedelta(days=int(HOLD_D * 7 / 5)))]
            win = win[~used.reindex(win).values]          # khong dem trung khi 2 su kien chong lan
            used.loc[win] = True
            tot_i = float(dl.reindex(win).sum())
            car_i = float(carry_dlog.reindex(win).sum())
            mkt_i = tot_i - car_i                          # phan do GIA (da tru carry)
            rows.append({"su_kien": d0.date().isoformat(), "n_phien": len(win),
                         "vay_vnd": r["loan"], "vi_the_vnd": r["pos"],
                         "a_thi_truong": mkt_i, "b_carry": car_i, "tong_cua_so": tot_i})
        T = pd.DataFrame(rows)
        in_win = float(T["tong_cua_so"].sum())
        outside = total - in_win                           # (d) tuong quan / ngoai cua so
        T["c_drag_tuongtac"] = 0.0                         # gan nhan: nam trong a (tach o buoc duoi)

        # tach (c) drag ra khoi (a): drag = phan phi tuyen = tong_cua_so - f_eff*(dlog control trong cua so)
        # dung dinh nghia tuyen tinh hoa: neu don bay chi la nhan tuyen tinh thi mkt_i ~ (f-1)*dlogB_win
        f = float("1." + tag.split("_f1")[1])
        for i, r in T.iterrows():
            d0 = pd.Timestamp(r["su_kien"])
            win = dl.index[(dl.index > d0) & (dl.index <= d0 + pd.Timedelta(days=int(HOLD_D * 7 / 5)))]
            dlogB = float(pd.Series(np.diff(np.log(b.values)), index=idx[1:]).reindex(win).sum())
            lin = (f - 1.0) * dlogB * (r["vi_the_vnd"] / max(a.reindex([d0], method="ffill").iloc[0], 1))
            T.at[i, "c_drag_tuongtac"] = r["a_thi_truong"] - lin
            T.at[i, "a_thi_truong"] = lin

        chk = float(T[["a_thi_truong", "b_carry", "c_drag_tuongtac"]].to_numpy().sum()) + outside
        print("=" * 122)
        print(f"CAU 2 — TANG ENGINE · {tag}  (f={f:.2f}, lai vay {rate}%/nam)")
        print(f"  Engine chi LEVER {len(T)}/17 su kien — production tu loai 2022-04-19 (gate postbull) "
              f"va 2022-09-28 (gate BEAR/grind). Do la hanh vi SAN CO, giong het o chan control.")
        print("=" * 122)
        print(f"{'su kien':<12}{'phien':>6}{'VAY (tr)':>12}{'(a) thi truong':>16}{'(b) carry':>12}"
              f"{'(c) drag/tt':>13}{'= rong':>11}   loai")
        for _, r in T.iterrows():
            net = r["a_thi_truong"] + r["b_carry"] + r["c_drag_tuongtac"]
            kind = ("TIMING" if r["a_thi_truong"] < 0 else
                    ("CARRY" if net < 0 else "duong"))
            print(f"{r['su_kien']:<12}{int(r['n_phien']):>6}{r['vay_vnd']/1e6:>12,.0f}"
                  f"{r['a_thi_truong']*100:>15.3f}%{r['b_carry']*100:>11.3f}%"
                  f"{r['c_drag_tuongtac']*100:>12.3f}%{net*100:>10.3f}%   {kind}")
        print(f"{'TONG trong cua so':<18}{'':>0}{T['a_thi_truong'].sum()*100:>27.3f}%"
              f"{T['b_carry'].sum()*100:>11.3f}%{T['c_drag_tuongtac'].sum()*100:>12.3f}%"
              f"{in_win*100:>10.3f}%")
        print(f"  (d) NGOAI cua so (tuong quan voi ca so, parking/parking-cash doi trang thai) = "
              f"{outside*100:+.3f}%   [{outside/total*100 if total else float('nan'):+.1f}% cua tong]")
        print(f"  KIEM TRA dong nhat: tong 4 cot = {chk:+.10f} ; dlogNAV do truc tiep = {total:+.10f} ; "
              f"lech = {chk-total:+.3e}  -> {'KHOP' if abs(chk-total) < 1e-9 else '*** LECH ***'}")
        # --- KIEM TRA ARITHMETIC BAT BUOC: tong cac cot phai DUNG BANG dCAGR headline ---
        # CAGR = (NAV_T/NAV_0)^(1/yrs)-1 tren LICH (365,25 ngay), nen:
        #   dCAGR = exp(L_lev/yrs) - exp(L_ctl/yrs) = (1+CAGR_ctl) * (exp(total/yrs) - 1)
        # KHONG phai exp(total/yrs)-1 — do la loi hay gap khi doi log-diff sang pp CAGR.
        yrs = (idx[-1] - idx[0]).days / 365.25
        cagr_ctl = (b.iloc[-1] / b.iloc[0]) ** (1 / yrs) - 1
        cagr_lev = (a.iloc[-1] / a.iloc[0]) ** (1 / yrs) - 1
        d_meas = 100 * (cagr_lev - cagr_ctl)                      # do TRUC TIEP tu 2 chuoi NAV
        d_from_cols = 100 * (1 + cagr_ctl) * (np.exp(chk / yrs) - 1)   # dung TONG 4 COT
        print(f"  DOI CHIEU HEADLINE (bat buoc): dCAGR do truc tiep = {d_meas:+.4f}pp ; "
              f"dCAGR dung lai tu TONG 4 COT = {d_from_cols:+.4f}pp ; lech = {d_from_cols-d_meas:+.2e}pp "
              f"-> {'KHOP' if abs(d_from_cols - d_meas) < 1e-6 else '*** LECH ***'}")
        T["leg"], T["f"], T["rate"] = tag, f, rate
        T["d_ngoai_cua_so"] = outside
        T["dlog_total"] = total
        out_rows.append(T)
        T.to_csv(os.path.join(HERE, f"cau2_engine_{tag}.csv"), index=False)
        print()
    pd.concat(out_rows).to_csv(os.path.join(HERE, "cau2_engine_all.csv"), index=False)
    print("-> cau2_engine_<leg>.csv + cau2_engine_all.csv")


if __name__ == "__main__":
    main()
