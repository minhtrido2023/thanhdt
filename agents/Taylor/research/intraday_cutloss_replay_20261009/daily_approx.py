#!/usr/bin/env python3
"""daily_approx.py — LỚP XẤP XỈ NGÀY (2014-02..2026-06, ledger R3 4707bcbe) để có N lớn hơn cửa sổ intraday.

KHÔNG phải replay driver: không có giá trong phiên ⇒ chỉ gọi hàm quyết định của engine
(`trigger_check`, `market_wide_reason`, `floor_price`) trên giá xấp xỉ:
  last  = Low(D) (giá thấp nhất ngày — điểm sâu nhất cổng có thể thấy; quét 15' thật thấy ít hơn)
  VNI   = VNINDEX Close(D) (không biết VNINDEX đúng thời điểm Low ⇒ idio xấp xỉ)
  gộp cả thị trường: đếm mọi mã đang giữ kích hoạt TRONG NGÀY (bản thật đếm theo TỪNG lượt quét ⇒
  xấp xỉ này gộp NHIỀU hơn thật).
Giá thoát xấp xỉ: Close(D) (ca rút gọn HOSE bán xong trong ~25-55' sau T0; ca ≥14:00 hoãn sang 09:15 phiên
sau ⇒ Close(D) là xấp xỉ thô). Chi phí: 0,097% × 2 + impact 0,5σ√(Q/ADV) với NAV 1 tỷ.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import analyze as A  # noqa: E402
import intraday_cutloss_engine as E  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "cache")
EXCH = json.load(open(os.path.join(C, "exchange.json")))


def main():
    h = pd.read_parquet(os.path.join(C, "holdings_ledger.parquet"))
    h["d"] = h.date.dt.date
    rows = []
    vni = A.VNI
    for (d, tk), r in h.set_index(["d", "ticker"]).iterrows():
        p = A.PX.get(tk)
        if p is None or d not in p.index or d not in A.TD:
            continue
        i = A.TD.index(d)
        if i == 0:
            continue
        dp = A.TD[i - 1]
        if dp not in p.index or dp not in vni.index:
            continue
        x, xp = p.loc[d], p.loc[dp]
        if not all(v == v and v for v in (x.Close, xp.Close, x.Price, x.Low)):
            continue
        f = x.Price / x.Close                       # adj → thô của ngày D
        ref = xp.Close * f
        low = x.Low * f
        ex = (EXCH.get(tk) or "HOSE").upper()
        fl = E.floor_price(ref, ex)
        tr = E.trigger_check(max(low, fl), ref, fl, float(vni.loc[d, "Close"]), float(vni.loc[dp, "Close"]))
        trr = E.trigger_check_rel(max(low, fl), ref, fl, float(vni.loc[d, "Close"]), float(vni.loc[dp, "Close"]), ex)
        if not ((tr and tr["hit"]) or (trr and trr["hit"])):
            continue
        sig, adv = A.risk(tk, d)
        qty = r.weight * 1e9 / ref
        imp = 0.5 * sig * np.sqrt(qty / adv) if adv and sig == sig else 0.0
        exit_net = x.Price * (1 - 2 * A.FEE - imp)
        row = {"day": str(d), "ticker": tk, "book": r.book, "exchange": ex, "hit_cur": tr["hit"],
               "hit_rel": trr["hit"], "at_floor": tr["at_floor"], "ret_low": tr["ret"], "idio": tr["idio"],
               "vni_ret": tr["vni_ret"], "close_ret": x.Price / ref - 1, "weight": r.weight}
        for k in A.HOR:
            pk = A.fut(tk, d, k)
            row[f"E{k}"] = exit_net / pk - 1 if pk == pk else np.nan
            row[f"oan{k}"] = bool(pk > x.Price) if pk == pk else np.nan
        rows.append(row)
    df = pd.DataFrame(rows)
    # gộp cả thị trường theo NGÀY (xấp xỉ) — gọi đúng hàm engine trên các ca kích hoạt hiện hành của ngày
    mw = {}
    for d, g in df[df.hit_cur].groupby("day"):
        hits = [{"at_floor": a, "vni_missing": False} for a in g.at_floor]
        mw[d] = E.market_wide_reason(hits)
    df["market_wide_day"] = df.day.map(mw)
    df.to_csv(os.path.join(HERE, "out", "daily_approx_cases.csv"), index=False)
    df["period"] = np.where(df.day < "2020-01-01", "IS_2014_19", "OOS_2020_26")
    res = []
    for name, sub in (("cur_idio_case (mở ca riêng)", df[df.hit_cur & df.market_wide_day.isna()]),
                      ("cur_market_wide (gộp, không hành động)", df[df.hit_cur & df.market_wide_day.notna()]),
                      ("rel_only (ngưỡng tương đối, không hit hiện hành)", df[df.hit_rel & ~df.hit_cur])):
        for per, s2 in [("ALL", sub)] + list(sub.groupby("period")):
            for k in (1, 5, 20):
                x = s2[f"E{k}"].dropna()
                if x.empty:
                    continue
                lo, hi = A.boot_ci(s2, f"E{k}")
                res.append({"nhánh": name, "giai_đoạn": per, "h": k, "n_cases": len(x),
                            "n_days": s2.loc[x.index, "day"].nunique(), "mean%": x.mean() * 100,
                            "median%": x.median() * 100, "ci_lo%": lo * 100, "ci_hi%": hi * 100,
                            "cutloss_thắng%": (x > 0).mean() * 100,
                            "bán_oan%": s2.loc[x.index, f"oan{k}"].mean() * 100})
    r = pd.DataFrame(res)
    r.to_csv(os.path.join(HERE, "out", "daily_approx_summary.csv"), index=False)
    print(r.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
