"""Phan ra CO CHE: tai sao chan LY TUONG (go tran fill) lai TE HON chan THAT?

Gia thuyet: tran fill 20%ADV/phien + min_fill_pct=0.30 hoat dong nhu MOT BO LOC THANH KHOAN
ngau nhien-nhung-co-loi — no loai bo (ABANDONED_REFUND) dung nhom ma microcap thanh khoan mong,
va nhom do LO (bang chung doc lap 2026-07-21: nhom nay -1,11%/vong trong khi phan con lai
+4,82%/vong). Go tran => nhom lo duoc mua TRON SIZE => keo CAGR xuong.

Kiem chung (khong suy doan): voi tung cap (real, ideal) cung NAV, chia ma theo:
  ONLY_IDEAL = ma chi giao dich duoc o chan ly tuong (chan that khong bao gio mo xong vi the)
  BOTH       = ma ca 2 chan deu co vi the hoan tat
roi do loi suat vong (round-trip) TRONG CHINH CHAN LY TUONG cua 2 nhom.
Neu ONLY_IDEAL lo / kem hon han BOTH => co che duoc xac nhan bang so, khong phai bang lap luan.

Job Taylor_20260804_102015.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

DATA = "/home/trido/thanhdt/WorkingClaude/data"


def load(tag):
    g = glob.glob(os.path.join(DATA, f"*_exp_{tag}_univpit*.csv"))
    if not g:
        return None
    d = pd.read_csv(g[0], low_memory=False)
    d = d[d["reason"].notna()].copy()
    d["pt"] = d["play_type"].astype(str)
    return d[d["pt"] != "ETF_PARK"]


def roundtrips(d):
    """Loi suat vong theo holding_id: (tien ban - tien mua)/tien mua, chi vong DA DONG."""
    b = d[d["action"] == "buy"].groupby("holding_id").agg(
        buy=("buy_amount", "sum"), fee_b=("fee", "sum"),
        ticker=("ticker", "first"), pt=("pt", "first"), book=("book", "first"))
    s = d[d["action"] == "sell"].groupby("holding_id").agg(
        sell=("sell_amount", "sum"), fee_s=("fee", "sum"),
        aband=("reason", lambda x: (x == "ABANDONED_REFUND").any()))
    j = b.join(s, how="inner")
    j = j[j["buy"] > 0]
    j["ret"] = (j["sell"] - j["fee_s"] - j["buy"] - j["fee_b"]) / j["buy"] * 100
    j["pnl"] = j["sell"] - j["fee_s"] - j["buy"] - j["fee_b"]
    return j


def report(nav):
    dr, di = load(f"cap{nav}b_real"), load(f"cap{nav}b_ideal")
    if dr is None or di is None:
        print(f"NAV={nav}B: thieu CSV, bo qua"); return
    rr, ri = roundtrips(dr), roundtrips(di)
    # ma "hoan tat duoc" = co it nhat 1 vong KHONG bi bo do
    ok_real = set(rr[~rr["aband"].fillna(False)]["ticker"])
    ok_ideal = set(ri[~ri["aband"].fillna(False)]["ticker"])
    only_ideal = ok_ideal - ok_real
    both = ok_ideal & ok_real

    print("\n" + "=" * 108)
    print(f"NAV = {nav}B — phan ra co che (do TRONG chan LY TUONG, nen khong lan hieu ung gia)")
    print("=" * 108)
    print(f"  ma hoan tat duoc: chan THAT {len(ok_real)}  |  chan LY TUONG {len(ok_ideal)}  "
          f"|  CHI o ly tuong {len(only_ideal)}  |  chung {len(both)}")
    g = ri[~ri["aband"].fillna(False)].copy()
    g["grp"] = np.where(g["ticker"].isin(only_ideal), "ONLY_IDEAL", "BOTH")
    agg = g.groupby("grp").agg(n_vong=("ret", "size"), von_B=("buy", lambda x: x.sum() / 1e9),
                               ret_TB=("ret", "mean"), ret_trungvi=("ret", "median"),
                               pnl_B=("pnl", lambda x: x.sum() / 1e9))
    print()
    print(agg.round(2).to_string())
    if "ONLY_IDEAL" in agg.index and "BOTH" in agg.index:
        a, b_ = agg.loc["ONLY_IDEAL"], agg.loc["BOTH"]
        print(f"\n  => nhom CHI-O-LY-TUONG: {a['ret_TB']:+.2f}%/vong tren {a['von_B']:.0f}B von "
              f"({a['von_B']/(a['von_B']+b_['von_B'])*100:.1f}% tong von quay vong), "
              f"P&L {a['pnl_B']:+.1f}B")
        print(f"     nhom CHUNG          : {b_['ret_TB']:+.2f}%/vong tren {b_['von_B']:.0f}B von, "
              f"P&L {b_['pnl_B']:+.1f}B")
        print(f"     CHENH LECH loi suat/vong = {a['ret_TB'] - b_['ret_TB']:+.2f}pp")

    # ADV cua 2 nhom (thanh khoan) — kiem tra "chi o ly tuong" co dung la nhom mong thanh khoan
    print(f"\n  Kiem tra thanh khoan: so vong theo so (chan ly tuong)")
    print(g.groupby(["grp", "book"]).size().to_string())


if __name__ == "__main__":
    for n in ([int(x) for x in sys.argv[1:]] or [1, 5, 10, 20, 30, 50, 75, 100]):
        report(n)
