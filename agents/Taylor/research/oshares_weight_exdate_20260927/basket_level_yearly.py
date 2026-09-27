#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""basket_level_yearly.py — lợi nhuận theo NĂM của CHÍNH CHUỖI RỔ (parking vehicle), 2 chế độ.

Vòng review 2 (job Taylor_20260927_052432). Dùng để phân biệt hai thứ mà AB_R3.md vòng 1 trộn lẫn:
cỡ lệch của RỔ (cái bản sửa thực sự làm) vs con số NAV theo năm (đi qua allocator ⇒ path-dependent).
Gọi ĐÚNG hàm engine gọi (`pt_v23_audit_2014.py:914`, ETF_LIQ=custompitg ⇒ quality="none",
rebal="q2m5", gate_rating=3) trên cache ĐÃ GHIM, chỉ đổi `BASKET_OSHARES_STEP`.

Chạy qua run_with_wt_basket.py để `custom_basket` là bản CỦA WORKTREE (nếu không thì no-op im lặng).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq            # noqa: E402
import custom_basket as cb                      # noqa: E402

START, END = "2014-01-02", "2026-06-19"


def build_level(mode):
    os.environ["BASKET_OSHARES_STEP"] = mode
    cb._CA_CACHE.clear()
    cb.UNIVERSE_SOURCE = "pit"
    lvl, _adv, _mem, _bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                        gate_rating=3, weight_scheme="namecap",
                                        top_n=30, name_cap=0.10)
    s = pd.Series(lvl)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def yearly(s):
    eoy = s.groupby(s.index.year).last()
    prev = pd.Series([s.iloc[0]] + list(eoy.values[:-1]), index=eoy.index)
    return (eoy / prev - 1.0) * 100


def main():
    a, b = build_level("quarter"), build_level("exdate")
    ya, yb = yearly(a), yearly(b)
    print(f"\n{'năm':<6}{'rổ quarter':>12}{'rổ exdate':>12}{'Δ (pp)':>10}")
    for y in ya.index:
        print(f"{y:<6}{ya[y]:>+12.2f}{yb[y]:>+12.2f}{yb[y] - ya[y]:>+10.2f}")
    d = (yb - ya).abs()
    print(f"\nmax |Δ| theo năm = {d.max():.2f}pp (năm {d.idxmax()}); Δ 2021 = {yb[2021] - ya[2021]:+.2f}pp")
    tot_a = (a.iloc[-1] / a.iloc[0]) ** (365.25 / (a.index[-1] - a.index[0]).days) - 1
    tot_b = (b.iloc[-1] / b.iloc[0]) ** (365.25 / (b.index[-1] - b.index[0]).days) - 1
    print(f"CAGR chuỗi rổ: quarter {tot_a * 100:.2f}%  exdate {tot_b * 100:.2f}%  "
          f"Δ {(tot_b - tot_a) * 100:+.2f}pp  (lịch, không phải /252)")


if __name__ == "__main__":
    main()
