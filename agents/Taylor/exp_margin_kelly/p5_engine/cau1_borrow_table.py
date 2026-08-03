#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CAU 1 (dispatch Taylor_20260803_101341) — "vay bao nhieu, bang SO THAT (khong chi he so f truu tuong)".

Doc thang tu ledger ma engine_lever.py ghi ra khi chay voi CAPIT_LEVER_FORCE=f:
  data/..._exp_D_f<..>_leveraudit.csv    per-event: book NAV, wt truoc/sau, LOAN VND, position VND
  data/..._exp_D_f<..>_borrowledger.csv  per-session: notional, native negative cash, interest charged

Xuat 2 bang:
  (1) so tien vay THAT tai moi su kien, o quy mo so sach LUC DO (NAV backtest tang 50B -> 1.178B)
  (2) so tien do NEU AP DUNG HOM NAY tren SpaceX — NAV doc song tu nav_history_SpaceX.csv (dong cuoi),
      KHONG ghi cung.

QUY DOI DUNG (da sua 2026-08-03): loan_live = (vay / NAV so sach TAI NGAY DO) x NAV song hom nay.
KHONG duoc dung (nav_live / 50e9) lam he so: 50B la NAV LUC BAT DAU, con so sach cuoi ky la 1.178B —
nhan kieu do cho ra "vay 1.664tr VND" cho su kien 2023 tren mot tai khoan chi co 938tr, tuc vo ly.
Ty le vay/NAV luon = (f-1)/f x wt_engine, la boi so con nguoi doc va kiem tra duoc.

CANH BAO PHAI DOC KEM (khong duoc bo khi trich bang 2): ke ca voi quy doi theo ty le, con so live van
la CAN DUOI, vi chinh sach KHONG bat bien theo quy mo: (a) tran %ADV cua ro CAPIT chan o quy mo LON,
nen o 50B mot so slug bi cat bot con o 0,94B thi khong -> ban 0,94B thuc te se vay NHIEU HON ty le;
(b) o 0,94B tai khoan gan nhu khong con tien nhan (SpaceX ~98,5% da dau tu, p1 §5) trong khi backtest
50B luon con -> phan "vay that" o live cao hon.

Chay: $DNA_PYEXE cau1_borrow_table.py
"""
import os, glob, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/trido/thanhdt/WorkingClaude/data"
NAVCSV = "/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_history_SpaceX.csv"


def spacex_nav():
    df = pd.read_csv(NAVCSV)
    last = df.iloc[-1]
    return float(last["nav"]), str(last["date"])


def legs():
    """Chan co ledger vay = moi leg chay voi CAPIT_LEVER_FORCE>1 (D_* @10%/nam cua vong dau,
    E125_* @12,5% = lai suat BASE dang ky trong plan, E140_* @14% = adversarial)."""
    out = {}
    for pat in ("*_exp_D_f*_leveraudit.csv", "*_exp_E1*_f*_leveraudit.csv"):
        for p in sorted(glob.glob(os.path.join(DATA, pat))):
            tag = os.path.basename(p).split("_exp_")[1].split("_leveraudit")[0]
            tag = tag.replace("_univpit", "").replace("_mge110cap", "").replace(
                "_mge120cap", "").replace("_mge130cap", "").replace("_mge150cap", "")
            out[tag] = p
    return out


def leg_f(tag):
    """'E125_f13'/'D_f11'/'D_f13nc' -> 1.3/1.1/1.3 (bo hau to bien the nhu 'nc')."""
    d = tag.split("_f")[-1]
    d = "".join(ch for ch in d if ch.isdigit())
    return float(d[0] + "." + d[1:]) if len(d) >= 2 else float("nan")


def main():
    nav_live, nav_date = spacex_nav()
    L = legs()
    if not L:
        sys.exit("chua co file *_leveraudit.csv — chay run_p5.sh voi CAPIT_LEVER_FORCE truoc")
    print("=" * 118)
    print("CAU 1 — SO TIEN VAY THAT tai moi su kien CAPIT lich su (engine tier, forced-borrow ledger)")
    print(f"  SpaceX NAV song = {nav_live:,.0f} VND  (nav_history_SpaceX.csv, ngay {nav_date})")
    print("  Quy doi = (vay / NAV so sach TAI NGAY DO) x NAV song. CAN DUOI cho live — xem docstring.")
    print("=" * 118)

    summ = []
    for tag in sorted(L):
        f = leg_f(tag)
        t = pd.read_csv(L[tag])
        led = pd.read_csv(L[tag].replace("_leveraudit", "_borrowledger"))
        # SAI LAM PHAI TRANH: KHONG duoc nhan loan_vnd voi (nav_live/50e9). 50B la NAV LUC BAT DAU;
        # so sach backtest tang len 1.178B, nen mot khoan vay nam 2023 quy doi kieu do se ra 1.664tr VND
        # tren mot tai khoan chi co 938tr — vo ly. Quy doi DUNG = ty le vay/NAV TAI THOI DIEM DO, roi
        # nhan voi NAV song hom nay. (Kiem chung: ty le nay luon = (f-1)/f x wt, boi so con nguoi doc duoc.)
        t.to_csv(os.path.join(HERE, f"cau1_borrow_{tag}.csv"), index=False)
        # gop 2 book (B/L) theo NGAY su kien -> "mot dot washout vay bao nhieu"
        g = (t.groupby("date", as_index=False)
               .agg(loan_vnd=("loan_vnd", "sum"), position_vnd=("position_vnd", "sum"),
                    book_nav_vnd=("book_nav_vnd", "sum"), n_book=("tag", "count")))
        g["loan_pct_nav"] = g["loan_vnd"] / g["book_nav_vnd"] * 100.0
        g["loan_live_vnd"] = g["loan_pct_nav"] / 100.0 * nav_live
        print(f"\n--- {tag}  (f = {f:.2f})  " + "-" * 74)
        print(f"{'su kien':<13}{'NAV so sach':>16}{'vi the CAPIT':>16}{'VAY (tai thoi diem)':>21}"
              f"{'vay/NAV':>9}{'VAY neu ap dung HOM NAY':>25}")
        for _, r in g.iterrows():
            print(f"{r['date']:<13}{r['book_nav_vnd']/1e9:>13,.1f}B{r['position_vnd']/1e9:>15,.1f}B"
                  f"{r['loan_vnd']/1e9:>19,.1f}B{r['loan_pct_nav']:>8.1f}%"
                  f"{r['loan_live_vnd']/1e6:>22,.1f}tr")
        pk = g.loc[g["loan_pct_nav"].idxmax()]
        print(f"  vay NANG NHAT (theo %NAV) = {pk['loan_pct_nav']:.1f}% NAV  ({pk['date']})  ->  "
              f"{pk['loan_live_vnd']/1e6:,.1f}tr VND tren tai khoan SpaceX hom nay")
        print(f"  TB moi dot = {g['loan_pct_nav'].mean():.1f}% NAV -> {g['loan_live_vnd'].mean()/1e6:,.1f}tr VND")
        peak = g["loan_vnd"].max()
        # SUA 2026-08-03 (quant-skeptic bat): gop 2 book THEO NGAY truoc khi max()/dem — cong
        # max(BAL)+max(LAG) la du no chua bao gio dong thoi ton tai; dem rieng tung book thi 600
        # ngay co ca 2 book cung no se bi tinh 2 lan.
        _day = led.groupby("ymd")["notional"].sum()
        print(f"  lai vay THUC TRA (engine, ca ky) = {led['charge'].sum()/1e6:,.1f}tr VND ; "
              f"so NGAY co du no (khong trung) = {int((_day>0).sum())} ; "
              f"du no DONG THOI dinh cao = {_day.max()/1e6:,.0f}tr VND")
        print(f"  trong do lai ma engine tu tinh tren TIEN MAT AM (khong can ep) = "
              f"{led['native_neg_cash'].gt(0).sum()} phien "
              f"-> {'engine CO tu vay' if led['native_neg_cash'].gt(0).any() else 'engine KHONG he tu vay (dung nhu p2 do duoc)'}")
        summ.append({"leg": tag, "f": f, "n_event": len(g),
                     "loan_total_50B": g["loan_vnd"].sum(), "loan_peak_50B": peak,
                     "loan_pct_nav_max": g["loan_pct_nav"].max(), "loan_pct_nav_mean": g["loan_pct_nav"].mean(),
                     "loan_live_max_vnd": g["loan_live_vnd"].max(), "loan_live_mean_vnd": g["loan_live_vnd"].mean(),
                     "interest_paid_50B": led["charge"].sum(),
                     "loan_days": int((led.groupby("ymd")["notional"].sum() > 0).sum()),
                     "peak_simul_debt_vnd": float(led.groupby("ymd")["notional"].sum().max()),
                     "native_borrow_days": int((led["native_neg_cash"] > 0).sum())})
    s = pd.DataFrame(summ)
    s.to_csv(os.path.join(HERE, "cau1_summary.csv"), index=False)
    print("\n" + "=" * 118)
    print("TOM TAT")
    print("=" * 118)
    print(s.to_string(index=False))
    print(f"\n  -> file: cau1_summary.csv + cau1_borrow_<leg>.csv (per-event, ca 2 quy mo)")


if __name__ == "__main__":
    main()
