#!/usr/bin/env python3
"""Tach Delta cua chan `_21s` thanh SO HOC vs DUONG DI — job Taylor_20260928_010454.

Cung cong thuc truy hoi voi `c30v_w2_q2_20260927/w2b_overlay.py` (quant-skeptic CONFIRMED
2026-09-27 16:44Z), chi thay "tien nhan roi" bang "tien DU TUOI":

    nav_ov(d) = nav_ov(d-1) * (1 + r_ctrl(d)) + matured_ctrl(d-1) * rate(d)/252 * scale(d-1)
    scale     = nav_ov(d-1) / nav_ctrl(d-1)      (overlay gop lai tren von CUA NO)

`matured_ctrl` = tien nhan roi CUA CHAN CONTROL nhan voi TY LE du-tuoi/nhan-roi tung phien tung
so sach LAY TU CHAN 21s. Ty le do suy ra tu dong nhat thuc tien lai cua chinh ledger 21s
(`interest(d) = cash(d)-cash(d-1) - sum(TX net)`, dung cai ma self-check cua engine dung), nen no
la so DO LAI tu artifact chu khong phai tai dung mo hinh.

XAP XI PHAI KHAI: ty le du-tuoi duoc "mang" tu duong di 21s sang duong di control. Hai duong di
khac nhau (chinh la phan DUONG DI ta dang muon do), nen overlay nay do dung phan SO HOC *neu* co
cau tuoi tien giong chan 21s. Do la gia dinh yeu nhat co the, va no la ly do con so cua RECORD van
la chan engine (25,24%), khong phai overlay.

    overlay_21s.py <ctrl.csv> <21s.csv> [<21s_2.csv> ...]
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude")
import idle_rate_proxy as irp   # noqa: E402

BOOKS = (("BAL", "bal_cash_ref"), ("LAG", "lag_cash_ref"))


def load(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["t"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["t", "combined_nav"]).sort_values("t")
    g = d.groupby(d["t"].dt.normalize()).last()
    tx = df[(df["record_type"] == "TX") & (~df["reason"].astype(str).str.startswith("MTM"))].copy()
    tx["t"] = pd.to_datetime(tx["ymd"], errors="coerce").dt.normalize()
    tx["net"] = np.where(tx["action"] == "sell", tx["sell_amount"] - tx["fee"],
                         -(tx["buy_amount"] + tx["fee"]))
    return g, tx


def interest_by_book(g, tx, book, col):
    """interest(d) = dcash(d) - net TX(d) — chinh dong nhat thuc self-check cua engine dung."""
    cash = pd.to_numeric(g[col], errors="coerce").astype(float)
    f = tx[tx["book"] == book].groupby("t")["net"].sum().reindex(g.index).fillna(0.0)
    return cash.diff() - f, cash


def matured_from_lumps(inter, rate, term):
    """Che do pay_mode=maturity: suy lai GOC DAO HAN tung phien tu chuoi lai dang CUC.

    KHONG phai xap xi. Trong che do maturity moi lo accrue MOI phien no con song va tra o dung phien
    thu `term` cua ky han, nen ky han cua mot cuc tra o phien d LA DUNG `term` phien lien truoc d
    ([d-term, d-1]). Vi vay:
        P_d = cuc(d) / SUM_{k=d-term}^{d-1} rate(k)/252      (goc cua cuc do)
    va goc dao han hieu dung cua phien k = tong P_d cua moi cuc co k trong ky han. Chuoi tra ve VI
    THE so sanh duoc 1-1 voi `eligible` cua che do daily => cung mot cong thuc overlay dung cho ca hai.
    """
    per = rate / 252.0
    inter = np.nan_to_num(np.asarray(inter, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    out = np.zeros(len(inter))
    for d in np.flatnonzero(np.abs(inter) > 1.0):
        lo = max(d - term, 0)
        denom = per[lo:d].sum()
        if denom <= 0:
            continue
        out[lo:d] += inter[d] / denom
    return out


def cagr(nav, idx):
    yrs = (idx[-1] - idx[0]).days / 365.25
    return (nav[-1] / nav[0]) ** (1 / yrs) - 1


def main(ctrl_path, leg_paths, pay_mode="daily", term=21):
    gc, txc = load(ctrl_path)
    rate = np.array([irp.r_idle(t, tier="dep1m") / 100.0 for t in gc.index])
    nav_c = pd.to_numeric(gc["combined_nav"], errors="coerce").astype(float).values
    r_c = np.concatenate([[0.0], nav_c[1:] / nav_c[:-1] - 1.0])
    cash_c = {bk: pd.to_numeric(gc[col], errors="coerce").astype(float).values for bk, col in BOOKS}
    print(f"CTRL {ctrl_path.rsplit('/', 1)[-1][-42:]}  CAGR {cagr(nav_c, gc.index)*100:.3f}%")
    for lp in leg_paths:
        gl, txl = load(lp)
        assert (gl.index == gc.index).all(), "hai ledger khac chuoi ngay"
        frac = np.zeros(len(gc))          # ty le du-tuoi / nhan-roi, gop 2 so sach
        mat_tot = np.zeros(len(gc)); cash_tot = np.zeros(len(gc))
        for bk, col in BOOKS:
            inter, cash_l = interest_by_book(gl, txl, bk, col)
            if pay_mode == "maturity":
                mat = matured_from_lumps(inter.values, rate, term)
            else:
                mat = (inter.values / (rate / 252.0))      # tien du tuoi suy tu dong nhat thuc
            mat = np.nan_to_num(mat, nan=0.0, posinf=0.0, neginf=0.0)
            r = np.divide(mat, cash_l.values, out=np.zeros_like(mat),
                          where=np.abs(cash_l.values) > 1.0)
            r = np.clip(r, 0.0, 1.0)
            mat_tot += r * cash_c[bk]
            cash_tot += cash_c[bk]
        frac = np.divide(mat_tot, cash_tot, out=np.zeros_like(mat_tot), where=cash_tot > 1.0)
        nav_ov = np.empty(len(gc)); nav_ov[0] = nav_c[0]
        for i in range(1, len(gc)):
            scale = nav_ov[i - 1] / nav_c[i - 1]
            nav_ov[i] = nav_ov[i - 1] * (1 + r_c[i]) + mat_tot[i - 1] * rate[i] / 252.0 * scale
        nav_l = pd.to_numeric(gl["combined_nav"], errors="coerce").astype(float).values
        c_ov, c_l, c_c = cagr(nav_ov, gc.index), cagr(nav_l, gl.index), cagr(nav_c, gc.index)
        d_tot, d_ar = (c_l - c_c) * 100, (c_ov - c_c) * 100
        print(f"\n== {lp.rsplit('/', 1)[-1][-46:]}")
        print(f"   CAGR engine {c_l*100:7.3f}%   overlay {c_ov*100:7.3f}%   ctrl {c_c*100:7.3f}%")
        print(f"   Delta TONG {d_tot:+.3f}pp = SO HOC {d_ar:+.3f}pp + DUONG DI {d_tot-d_ar:+.3f}pp"
              f"   ({d_ar/d_tot*100:.1f}% so hoc)")
        print(f"   tien du tuoi / NAV ket hop mean = {np.nanmean(mat_tot/nav_c)*100:.2f}%   "
              f"| tien nhan roi / NAV mean = {np.nanmean(cash_tot/nav_c)*100:.2f}%   "
              f"| du tuoi / nhan roi mean = {np.nanmean(frac)*100:.1f}%")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    _pm = "maturity" if "--maturity" in sys.argv else "daily"
    main(args[0], args[1:], pay_mode=_pm)
