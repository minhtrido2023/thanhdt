#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAU 2 (dispatch Taylor_20260803_101341) — PHAN RA per-event: vi sao co su kien LO khi co don bay?

quant-skeptic (verify_20260803_094213.log) doi hoi tuong minh: "luu lai SCRIPT tinh hiep phuong sai /
decomposition ... phai co file chay duoc trong artifact, khong chi so trong bao cao". Day la file do.

DINH DANH TOAN HOC (dong nhat thuc, khong phai xap xi) -----------------------------------------------
Loi nhuan tren VON TU CO cua sleeve o don bay gop f (f = tai san / von tu co):

    R_i(f) = f*(r_i - phi) - (f-1)*c*d_i/365

Cai COMPOUND qua chuoi su kien la log(1+R_i), khong phai R_i. Nen phan ra o KHONG GIAN LOG:

    log(1+R_i(f)) - log(1+R_i(1))
        = (f-1)*r_i                      <- (a) THI TRUONG: dong von vay lai/lo bao nhieu
          - (f-1)*phi                    <- (b) PHI giao dich tren phan vay
          - (f-1)*c*d_i/365              <- (c) CHI PHI VAY (carry)
          - [drag_i(f) - drag_i(1)]      <- (d) PHAT COMPOUNDING (volatility drag)
    voi drag_i(x) = R_i(x) - log(1+R_i(x))  >= 0   (phat phi tuyen, ~ R^2/2)

Tong 4 cot = dung bang N*(g(f) - g(1)). Do la KIEM TRA ARITHMETIC BAT BUOC ma dispatch yeu cau
"khong duoc de ho" — script assert no toi 1e-12, va se BAO LOI neu lech.

Phan loai su kien LO (cau hoi (a)/(b)/(c) cua dispatch) duoc gan MAY MOC, khong bang mo ta:
  TIMING   : r_i < 0                     -> chinh su kien da lo KHI KHONG vay; don bay chi KHUYECH DAI
  CARRY    : r_i >= 0 nhung (f-1)*r_i < (f-1)*(phi + c*d_i/365)  -> lai tho duong, am sau chi phi vay
  DRAG     : con lai, dong gop rong am chi vi phat compounding

(d) tuong quan voi ca so va (e) hien vat engine KHONG do duoc o tang su kien co lap — chung do o
tang engine (cau3_mechanism.py) va duoc bao cao rieng, dung nhu dispatch phan biet.

Chay:  $DNA_PYEXE cau2_decomp.py [f ...]      (mac dinh 1.1 1.2 1.3 1.5)
Nguon: ../p4_fullcycle/events_outcome_pit.csv (chan universe_pit — KHONG dung chan prune)
Xuat:  cau2_decomp_f<f>.csv + cau2_decomp.log (in ra stdout)
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "..", "p4_fullcycle", "events_outcome_pit.csv")

PHI = 0.0015           # 0,075%/chieu x 2 (p1 §2)
C   = 0.125            # lai vay 12,5%/nam (hop dong DNSE RocketX; CHUA doi chieu ban giay - p1 §7)
C_ADV = 0.14           # chan adversarial dang ky truoc (plan §5)


def load_events():
    df = pd.read_csv(SRC)
    df["event"] = pd.to_datetime(df["event"])
    df = df[df["r"].notna() & (df["event"] >= "2014-01-01")].reset_index(drop=True)
    assert len(df) == 17, f"ky vong N=17 su kien 2014+ co ket cuc day du, nhan {len(df)}"
    return df


def R(f, r, d, c):
    return f * (r - PHI) - (f - 1.0) * c * d / 365.0


def decomp(df, f, c=C):
    r = df["r"].to_numpy(float)
    d = df["cal_days"].to_numpy(float)
    R1, Rf = R(1.0, r, d, c), R(f, r, d, c)
    drag1 = R1 - np.log1p(R1)
    dragf = Rf - np.log1p(Rf)
    out = pd.DataFrame({
        "event":      df["event"].dt.date.astype(str),
        "r_tho":      r,
        "cal_days":   d,
        "R_f1":       R1,
        "R_f":        Rf,
        "a_thi_truong":   (f - 1.0) * r,
        "b_phi":         -(f - 1.0) * PHI,
        "c_chi_phi_vay": -(f - 1.0) * c * d / 365.0,
        "d_vol_drag":    -(dragf - drag1),
        "dlog_thuc":  np.log1p(Rf) - np.log1p(R1),
    })
    out["tong_4_cot"] = out[["a_thi_truong", "b_phi", "c_chi_phi_vay", "d_vol_drag"]].sum(axis=1)
    out["sai_so"] = out["tong_4_cot"] - out["dlog_thuc"]
    # KIEM TRA ARITHMETIC BAT BUOC (dispatch: "tong theo cot phai KHOP ... khong duoc de ho")
    assert np.abs(out["sai_so"]).max() < 1e-12, f"phan ra KHONG khop: max|sai so|={np.abs(out['sai_so']).max():.3e}"

    def _loai(row):
        if row["dlog_thuc"] >= 0:
            return "duong"
        if row["r_tho"] < 0:
            return "TIMING"
        if row["a_thi_truong"] < -(row["b_phi"] + row["c_chi_phi_vay"]):
            return "CARRY"
        return "DRAG"
    out["loai"] = out.apply(_loai, axis=1)
    return out


def gg(df, f, c=C):
    r, d = df["r"].to_numpy(float), df["cal_days"].to_numpy(float)
    return float(np.mean(np.log1p(R(f, r, d, c))))


def cagr_equiv(df, f, c=C):
    """CAGR-tuong-duong tren TRUC THOI GIAN THAT cua chuoi su kien (2014-05-08 -> 2026-03-09 + hold).

    Tra ve (naive, thuc) — dung cho CAU 2(c): 'tai sao xac suat thang cao ma ket qua khong cao tuong
    xung nhu ky vong ngay tho'. naive = ap TRUNG BINH SO HOC cho moi su kien roi luy thua N lan
    (phep tinh 'ngay tho' ma truc giac hay lam); thuc = luy tich dung chuoi R_i that.
    """
    r, d = df["r"].to_numpy(float), df["cal_days"].to_numpy(float)
    Rf = R(f, r, d, c)
    yrs = (df["event"].iloc[-1] - df["event"].iloc[0]).days / 365.25 + d[-1] / 365.0
    naive = (1.0 + Rf.mean()) ** (len(Rf) / yrs) - 1.0
    thuc  = float(np.prod(1.0 + Rf)) ** (1.0 / yrs) - 1.0
    return naive, thuc, yrs


def main():
    fs = [float(x) for x in sys.argv[1:]] or [1.1, 1.2, 1.3, 1.5]
    df = load_events()
    print("=" * 108)
    print("CAU 2 — PHAN RA per-event dong gop cua DON BAY (khong gian log, dong nhat thuc)")
    print(f"  Nguon: {os.path.relpath(SRC, HERE)} | N={len(df)} su kien 2014+ (chan universe_pit)")
    _x = df["r"] - PHI - C * df["cal_days"] / 365.0        # = dai luong `x` cua p1 (RONG sau lai vay)
    print(f"  r_tho (loi nhuan THO cua ro):  TB = {df['r'].mean()*100:+.4f}%   %duong = {(df['r']>0).mean()*100:.1f}%")
    print(f"  x     (RONG sau lai vay+phi):  TB = {_x.mean()*100:+.4f}%   %duong = {(_x>0).mean()*100:.1f}%"
          f"   <- day la +9,75% / 64,7% ma dispatch trich")
    print(f"  phi = {PHI*100:.2f}%   lai vay c = {C*100:.1f}%/nam")
    print("=" * 108)

    for f in fs:
        for c, lab in ((C, "BASE 12,5%"), (C_ADV, "ADV 14%")):
            t = decomp(df, f, c)
            if lab == "BASE 12,5%":
                t.to_csv(os.path.join(HERE, f"cau2_decomp_f{f:.2f}.csv"), index=False)
            print(f"\n--- f = {f:.2f}   (lai vay {lab}) " + "-" * 62)
            print(f"{'su kien':<12}{'r_tho':>9}{'ngay':>6}{'(a) t.truong':>13}{'(b) phi':>10}"
                  f"{'(c) vay':>10}{'(d) drag':>10}{'  =  rong':>11}   loai")
            for _, x in t.iterrows():
                print(f"{x['event']:<12}{x['r_tho']*100:>8.2f}%{x['cal_days']:>6.0f}"
                      f"{x['a_thi_truong']*100:>12.2f}%{x['b_phi']*100:>9.3f}%"
                      f"{x['c_chi_phi_vay']*100:>9.2f}%{x['d_vol_drag']*100:>9.2f}%"
                      f"{x['dlog_thuc']*100:>10.2f}%   {x['loai']}")
            s = t[["a_thi_truong", "b_phi", "c_chi_phi_vay", "d_vol_drag", "dlog_thuc"]].sum()
            print(f"{'TONG':<12}{'':>9}{'':>6}{s['a_thi_truong']*100:>12.2f}%{s['b_phi']*100:>9.3f}%"
                  f"{s['c_chi_phi_vay']*100:>9.2f}%{s['d_vol_drag']*100:>9.2f}%{s['dlog_thuc']*100:>10.2f}%")
            g1, gf = gg(df, 1.0, c), gg(df, f, c)
            chk = s["dlog_thuc"] - len(df) * (gf - g1)
            print(f"  KIEM TRA: tong cot rong = {s['dlog_thuc']:+.10f} ; N*(g(f)-g(1)) = "
                  f"{len(df)*(gf-g1):+.10f} ; lech = {chk:+.3e}  -> {'KHOP' if abs(chk) < 1e-12 else 'SAI'}")
            assert abs(chk) < 1e-12
            am = t[t["dlog_thuc"] < 0]
            print(f"  su kien dong gop AM: {len(am)}/{len(t)}  "
                  f"[TIMING {sum(am['loai']=='TIMING')} | CARRY {sum(am['loai']=='CARRY')} | DRAG {sum(am['loai']=='DRAG')}]")
            if len(am):
                print("    " + ", ".join(f"{x['event']}({x['loai']},{x['dlog_thuc']*100:+.2f}%)"
                                         for _, x in am.iterrows()))

    print("\n" + "=" * 108)
    print("CAU 2(c) — PHAT COMPOUNDING do RIENG: 'xac suat thang cao' vs 'ket qua thuc'")
    print("=" * 108)
    print(f"{'f':>6}{'CAGR naive (TB so hoc)':>26}{'CAGR THUC (luy tich)':>24}{'phat drag':>12}"
          f"{'g(f) log':>11}")
    for f in [1.0] + fs:
        n_, t_, yrs = cagr_equiv(df, f)
        print(f"{f:>6.2f}{n_*100:>25.2f}%{t_*100:>23.2f}%{(n_-t_)*100:>11.2f}pp{gg(df,f):>11.5f}")
    print(f"  (truc thoi gian = {yrs:.2f} nam, {len(df)} su kien; naive = ap TRUNG BINH SO HOC cho moi"
          f" su kien roi luy thua)")
    print("\n  Doc: cot 'phat drag' chinh la khoang cach giua ky vong 'ngay tho' (nhan trung binh len)"
          "\n  va ket qua compounding THUC. No tang PHI TUYEN theo f (~f^2*Var/2) — day la ly do"
          "\n  'xac suat thang 64,7% + TB +9,75%' KHONG tu dong dich thanh loi nhuan cao tuong ung.")


if __name__ == "__main__":
    main()
