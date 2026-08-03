#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAU 3 (dispatch Taylor_20260803_101341) — "neu chon dung, xac suat ro rang thi ket qua khong the thap":
kiem dinh menh de do bang SO, va neu tang engine VAN thap thi chi ra CO CHE lam mat loi the.

Gia thuyet co che (kiem dinh duoc, khong phai loi ke):
  H1. Edge do o tang SU KIEN CO LAP gia dinh moi su kien deu duoc mua o co so day du. Engine thi
      size CAPIT = size_gate x TY LE TIEN MAT CON LAI. Neu cac su kien co r_i CAO lai roi vao luc
      danh muc GAN HET tien (vi vua giai ngan dot truoc), thi don bay nhan len mot vi the NHO
      -> edge "co that" o tang su kien KHONG chuyen hoa duoc qua may.
  Kiem dinh: tuong quan giua r_i (loi nhuan tho su kien) va wt_base (ty trong engine THUC SU dat).
      H1 dung  <=> tuong quan <= 0 (hoac gan 0) => tien khong co mat luc co hoi tot nhat.
      H1 sai   <=> tuong quan > 0 ro ret => may mua NHIEU dung luc co hoi tot => edge chuyen hoa tot.

  H2. Ngay ca khi H1 dung, phan dong gop con lai bi pha them bao nhieu boi carry + drag?
      Dung lai bang phan ra da co (cau2_engine_decomp.py).

Nguon: log engine (dong `[capit-size ...]` va `[capit-lever-force ...]`) + events_outcome_pit.csv (r_i).
Chay: $DNA_PYEXE cau3_mechanism.py
"""
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "E125_f13.log")
EVOUT = os.path.join(HERE, "..", "p4_fullcycle", "events_outcome_pit.csv")

RE_SIZE = re.compile(
    r"\[capit-size (?P<book>[BL]) E(?P<ev>\d+) (?P<date>\d{4}-\d{2}-\d{2})\] "
    r"size=(?P<size>[\d.]+) cash=(?P<cash>[\d.]+) idle=(?P<idle>[\d.]+) -> wt=(?P<wt>[\d.]+)")


def parse_sizes(path):
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = RE_SIZE.search(ln)
            if m:
                d = m.groupdict()
                rows.append({"book": d["book"], "event": int(d["ev"]), "date": d["date"],
                             "size_gate": float(d["size"]), "cash_frac": float(d["cash"]),
                             "idle": float(d["idle"]), "wt_base": float(d["wt"])})
    return pd.DataFrame(rows)


def main():
    S = parse_sizes(LOG)
    if S.empty:
        raise SystemExit("khong doc duoc dong [capit-size ...] tu log")
    # book BAL la noi CAPIT chay chinh; gop 2 book bang trung binh trong so wt
    B = S[S["book"] == "B"].copy()
    E = pd.read_csv(EVOUT)
    ecol = "r"
    dcol = "event"
    E[dcol] = pd.to_datetime(E[dcol]).dt.strftime("%Y-%m-%d")
    M = B.merge(E[[dcol, ecol]], left_on="date", right_on=dcol, how="left")

    print("=" * 118)
    print("CAU 3 — CO CHE: edge o tang SU KIEN co chuyen hoa duoc qua MAY khong?")
    print("=" * 118)
    print(f"{'su kien':<13}{'size gate':>11}{'tien mat con':>14}{'wt engine DAT':>15}"
          f"{'r_i tho':>11}   ghi chu")
    for _, r in M.iterrows():
        note = ""
        if r["cash_frac"] < 0.05:
            note = "<- gan HET tien: don bay nhan len ~0"
        elif r["cash_frac"] < 0.30:
            note = "<- tien mong"
        rv = r[ecol]
        print(f"{r['date']:<13}{r['size_gate']:>11.3f}{r['cash_frac']:>14.4f}{r['wt_base']:>15.4f}"
              f"{(rv*100 if pd.notna(rv) else float('nan')):>10.2f}%   {note}")

    ok = M.dropna(subset=[ecol])
    c_wt = np.corrcoef(ok[ecol], ok["wt_base"])[0, 1]
    c_cash = np.corrcoef(ok[ecol], ok["cash_frac"])[0, 1]
    # tuong quan hang (Spearman) — ben hon voi n=15 va duoi dai
    rs_wt = pd.Series(ok[ecol]).rank().corr(pd.Series(ok["wt_base"]).rank())
    print("\n" + "-" * 118)
    print(f"  n = {len(ok)} su kien co ca r_i lan wt engine")
    print(f"  corr(r_i , wt engine DAT)      Pearson {c_wt:+.3f}   Spearman {rs_wt:+.3f}")
    print(f"  corr(r_i , tien mat con lai)   Pearson {c_cash:+.3f}")
    print(f"  TB wt khi r_i > trung vi = {ok[ok[ecol] > ok[ecol].median()]['wt_base'].mean():.4f}")
    print(f"  TB wt khi r_i < trung vi = {ok[ok[ecol] <= ok[ecol].median()]['wt_base'].mean():.4f}")
    verdict = ("H1 DUNG — tien khong co mat dung luc co hoi tot nhat; don bay nhan len vi the nho"
               if c_wt <= 0.15 else
               "H1 SAI — may VAN mua nhieu dung luc co hoi tot; edge chuyen hoa duoc")
    print(f"  -> {verdict}")

    # Kelly / growth-rate: menh de "xac suat ro rang thi khong the thap" kiem tra bang chinh g(f)
    print("\n" + "=" * 118)
    print("Menh de 'xac suat 64,7% + TB +9,75% thi khong the thap' — kiem bang g(f) tren CHINH 15 su")
    print("kien ma ENGINE thuc su mua (khong phai 17 su kien gia dinh)")
    print("=" * 118)
    r = ok[ecol].to_numpy(dtype=float)
    print(f"  15 su kien engine MUA : %duong {100*(r>0).mean():.1f}%  TB {100*r.mean():+.2f}%  "
          f"trung vi {100*np.median(r):+.2f}%  do lech chuan {100*r.std(ddof=1):.2f}%")
    for f in (1.0, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0):
        g = np.mean(np.log1p(f * r))
        print(f"    f={f:.1f}   g(f)=E[log(1+f*r)] = {g:+.5f}"
              + ("   <- co so" if f == 1.0 else f"   ({(np.exp(g)/np.exp(np.mean(np.log1p(r)))-1)*100:+.2f}% so voi f=1)"))
    fs = np.linspace(0.1, 6.0, 600)
    gs = [np.mean(np.log1p(x * r)) for x in fs]
    fstar = fs[int(np.argmax(gs))]
    print(f"  -> f* (toi da hoa g) tren rieng sleeve = {fstar:.2f}  "
          f"=> o TANG SU KIEN, menh de cua user DUNG: don bay CO nen tang.")
    print("     Nhung f* nay la cua RIENG sleeve. Xem bang tren: vi the engine dat trung binh chi "
          f"{ok['wt_base'].mean():.3f} NAV-book,")
    print("     nen phan NAV toan cuc chiu don bay nho hon nhieu lan -> dCAGR toan-so nho di tuong ung.")

    # ---- DOI CHIEU DINH LUONG: dilution co giai thich DUOC khoang cach sleeve -> toan-so khong? ----
    # Neu co che dung la PHA LOANG (chu khong phai "edge bien mat"), thi:
    #   dCAGR_toan_so  ~=  dCAGR_sleeve  x  (ty trong vi the TB)  x  (ty trong book BAL trong NAV tong)
    # Day la kiem dinh CO THE SAI — neu lech nhieu thi co che khac dang hoat dong, phai noi ro.
    YRS, NEV, W_BAL = 12.466, len(ok), 0.5      # 2014-01-02..2026-06-19 ; BAL = 25B/50B cua pin
    for f, d_meas in ((1.1, 0.0395), (1.2, 0.1701), (1.3, 0.6634), (1.5, 0.9199)):
        g1 = np.mean(np.log1p(r))
        gf = np.mean(np.log1p(f * r))
        cagr_sleeve = 100 * (np.exp((gf - g1) * NEV / YRS) - 1)      # sleeve, quy ra %/nam
        pred = cagr_sleeve * ok["wt_base"].mean() * W_BAL
        print(f"    f={f:.1f}  dCAGR sleeve {cagr_sleeve:+6.2f}%/nam  x wt_TB {ok['wt_base'].mean():.3f} "
              f"x book {W_BAL:.2f}  = du bao {pred:+.3f}pp   |  DO THUC TE {d_meas:+.3f}pp   "
              f"(ty le thuc/du bao {d_meas/pred if pred else float('nan'):.2f}x)")
    print("     -> neu ty le ~1x: khoang cach sleeve->toan-so la PHA LOANG THUAN TUY (khong mat edge).")
    M.to_csv(os.path.join(HERE, "cau3_mechanism.csv"), index=False)
    print("\n-> cau3_mechanism.csv")


if __name__ == "__main__":
    main()
