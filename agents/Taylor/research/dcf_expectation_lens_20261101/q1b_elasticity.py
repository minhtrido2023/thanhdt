# -*- coding: utf-8 -*-
"""Q1b — HẬU NGHIỆM (ngoài PREREG, +6 trial): log(PE) cắt ngang lên tăng trưởng bị nhiễu CƠ HỌC (E ở mẫu số ⇒ E vừa tăng
thì PE tự giảm nếu giá chưa theo). Đo trực tiếp ĐỘ CO GIÃN giá theo lợi nhuận:
  log(P_t/P_{t-12}) = a + β1·log(TTM0/TTM1) + β2·log(TTM1/TTM2) + ε   (cắt ngang mỗi tháng, chỉ TTM dương)
β1 = 1 ⇒ bội số giữ nguyên; β1 > 1 ⇒ thị trường NGOẠI SUY (nới bội số khi lợi nhuận tăng); β1 < 1 ⇒ làm mượt / đã tính
mean-revert. β2 > 0 ⇒ tăng trưởng năm TRƯỚC NỮA còn đẩy giá năm nay (ngoại suy chuỗi); β2 < 0 ⇒ đảo chiều.
Thêm: PE tự thân (percentile lịch sử chính mã) lên streak tăng trưởng + g1 + gQ2; và cùng phép đo trên lợi nhuận TƯƠNG LAI
(β_f: giá 12T tới vs log(TTMf1/TTM0)) để biết giá có 'nhìn trước' không."""
import os
import numpy as np
import pandas as pd
from q1_extrap import nw_t, rk

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
P = print


def wins(s, q=0.01):
    lo, hi = s.quantile(q), s.quantile(1 - q)
    return s.clip(lo, hi)


def main():
    p = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    p = p[p.t >= "2014-01-01"].copy()
    piv = p.pivot_table(index="t", columns="ticker", values="Close")
    # Close đầy đủ (không chỉ universe) để có giá t-12, t-24
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "dcf_vn_calibration_20261101"))
    from common import month_close
    mc, me = month_close()
    piv = mc.pivot(index="t", columns="ticker", values="Close").reindex(me)
    piv.index.name = "t"
    piv.columns.name = "ticker"
    for k in (12, 24):
        s = np.log(piv / piv.shift(k)).stack().rename(f"r_b{k}").reset_index()
        p = p.merge(s, on=["t", "ticker"], how="left")
    s = np.log(piv.shift(-12) / piv).stack().rename("r_f12").reset_index()
    p = p.merge(s, on=["t", "ticker"], how="left")
    pos = (p.TTM0 > 0) & (p.TTM1 > 0)
    p["dE1"] = np.where(pos, np.log(p.TTM0 / p.TTM1), np.nan)
    p["dE2"] = np.where((p.TTM1 > 0) & (p.TTM2 > 0), np.log(p.TTM1 / p.TTM2), np.nan)
    p["dEf"] = np.where((p.TTMf1 > 0) & (p.TTM0 > 0), np.log(p.TTMf1 / p.TTM0), np.nan)
    rows = []
    specs = [("r_b12", ["dE1"]), ("r_b12", ["dE1", "dE2"]), ("r_b24", ["dE1", "dE2"]), ("r_f12", ["dEf"]),
             ("r_f12", ["dE1", "dEf"])]
    for y, xs in specs:
        bt = []
        for t, g in p.groupby("t"):
            g = g[[y] + xs].dropna()
            if len(g) < 40:
                continue
            X = np.column_stack([np.ones(len(g))] + [wins(g[x]).values for x in xs])
            b, *_ = np.linalg.lstsq(X, wins(g[y]).values, rcond=None)
            bt.append([t, len(g)] + list(b[1:]))
        d = pd.DataFrame(bt, columns=["t", "n"] + xs)
        for per, m in (("IS", d.t.dt.year <= 2019), ("OOS", d.t.dt.year >= 2020)):
            rec = {"y": y, "xs": "+".join(xs), "per": per, "months": int(m.sum()), "n_med": d[m].n.median()}
            for x in xs:
                rec[f"b_{x}"] = d[m][x].mean()
                rec[f"t_{x}"] = nw_t(d[m][x])
            rows.append(rec)
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(OUT, "q1b_elasticity.csv"), index=False)
    P("=== Độ co giãn giá theo lợi nhuận (OLS cắt ngang, winsor 1%, TB theo tháng, t NW lag 12) ===")
    P(r.round(3).to_string(index=False))
    # streak: số dòng quý liên tiếp g1s >= 20% tính tới dòng hiện tại (dùng g1s_l1..l4 ⇒ 0..5)
    st = (p.g1s >= 0.2).astype(float)
    run = st.copy()
    alive = st.copy()
    for k in (1, 2, 3, 4):
        alive = alive * (p[f"g1s_l{k}"] >= 0.2).astype(float)
        run = run + alive
    p["streak"] = run.where(p.g1s.notna())
    rows = []
    for y in ("PE_own", "logPE"):
        if y == "logPE":
            p["logPE"] = np.log(p.PE.where((p.PE > 0) & (p.PE < 200)))
        xs = ["streak", "g1", "gQ2"]
        bt = []
        for t, g in p.groupby("t"):
            g = g[[y] + xs].dropna()
            if len(g) < 40:
                continue
            X = np.column_stack([np.ones(len(g)), g.streak.values] + [rk(g[x]).values for x in xs[1:]])
            b, *_ = np.linalg.lstsq(X, g[y].values, rcond=None)
            bt.append([t] + list(b[1:]))
        d = pd.DataFrame(bt, columns=["t"] + xs)
        for per, m in (("IS", d.t.dt.year <= 2019), ("OOS", d.t.dt.year >= 2020)):
            rows.append({"y": y, "per": per, **{f"b_{x}": d[m][x].mean() for x in xs},
                         **{f"t_{x}": nw_t(d[m][x]) for x in xs}})
    s = pd.DataFrame(rows)
    s.to_csv(os.path.join(OUT, "q1b_streak.csv"), index=False)
    P("\n=== PE (tự thân percentile / log PE) lên streak (0-5 quý liên tiếp g1≥20%, đơn vị = mỗi quý) + hạng g1, gQ2 ===")
    P(s.round(3).to_string(index=False))
    # mô tả: PE tự thân trung vị theo streak
    tab = p[p.PE_own.notna() & p.streak.notna()].groupby([p.t.dt.year >= 2020, "streak"]).agg(
        n=("PE_own", "size"), pe_own_med=("PE_own", "median"), r_b12_med=("r_b12", "median"),
        r_f12_med=("r_f12", "median"), f1_med=("f1", "median"))
    P("\n=== theo streak (index: OOS?, streak) ===")
    P(tab.round(3).to_string())
    tab.to_csv(os.path.join(OUT, "q1b_streak_table.csv"))


if __name__ == "__main__":
    main()
