#!/usr/bin/env python3
"""final_tables.py — gộp mọi lượt replay (ledger 4 shard + live) thành bảng cho REPORT.md.

N độc lập: (i) NGÀY có sự kiện (CI bootstrap theo cụm ngày, analyze.boot_ci); (ii) EPISODE = cùng mã,
các kích hoạt cách nhau ≤5 phiên gộp làm 1. Không dùng cột profit_*.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.argv = sys.argv[:1]
import analyze as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(HERE, "out")
TD = A.TD
TDI = {d: i for i, d in enumerate(TD)}


def cat(pat):
    fs = sorted(glob.glob(os.path.join(O, pat)))
    xs = [pd.read_csv(f).assign(run=os.path.basename(f).split("_")[0]) for f in fs if os.path.getsize(f) > 2]
    return pd.concat(xs, ignore_index=True) if xs else pd.DataFrame()


def ttype(r):
    ph = r.ret <= -0.05 + 1e-9 and r.idio <= -0.04 + 1e-9
    return "price(ret≤-5%∧idio≤-4%)" if ph else "floor_only(idio>-4%)"


def episodes(df):
    df = df.sort_values(["ticker", "day"]).copy()
    ep, last, k = [], {}, 0
    for r in df.itertuples():
        i = TDI.get(pd.Timestamp(r.day).date())
        j = last.get(r.ticker)
        if j is None or i is None or i - j[0] > 5:
            k += 1
            j = (i, k)
        last[r.ticker] = (i, j[1])
        ep.append(j[1])
    df["episode"] = ep
    return df


def summ(sc, label, col="E"):
    rows = []
    for k in A.HOR:
        c = f"{col}{k}"
        x = sc[c].dropna()
        if x.empty:
            continue
        lo, hi = A.boot_ci(sc, c)
        rows.append({"nhóm": label, "h": k, "n_ca": len(x), "n_ngày": sc.loc[x.index, "day"].nunique(),
                     "n_episode": sc.loc[x.index, "episode"].nunique(), "mean%": x.mean() * 100,
                     "median%": x.median() * 100, "ci_lo%": lo * 100, "ci_hi%": hi * 100,
                     "cutloss_thắng%": (x > 0).mean() * 100,
                     "bán_oan%": sc.loc[x.index, f"oan{k}"].astype(float).mean() * 100})
    return rows


def main():
    # --- A. sự kiện kích hoạt (NONE = đúng hành vi shadow hiện tại, không có agent)
    tr = cat("*_NONE_d0.5_triggers.csv")
    tr = tr[tr.account.notna()].copy()                       # chỉ mã ĐANG GIỮ
    tr["src"] = np.where(tr.run == "live", "live_dnse1m", "ledger_bar15")
    tr["type"] = tr.apply(ttype, axis=1)
    tr = episodes(tr.drop_duplicates(["t0", "ticker"]))
    # độ trễ: ret tại T0 vs Low/Close ngày
    lows, closes = [], []
    for r in tr.itertuples():
        d = pd.Timestamp(r.day).date()
        p = A.PX.get(r.ticker)
        if p is None or d not in p.index:
            lows.append(np.nan); closes.append(np.nan); continue
        f = p.loc[d, "Price"] / p.loc[d, "Close"]
        lows.append(p.loc[d, "Low"] * f / r.ref - 1)
        closes.append(p.loc[d, "Price"] / r.ref - 1)
    tr["ret_low_day"], tr["ret_close_day"] = lows, closes
    tr.to_csv(os.path.join(O, "events_held_NONE.csv"), index=False)
    mw = cat("*_NONE_d0.5_market_wide.csv")
    mw.to_csv(os.path.join(O, "market_wide_all.csv"), index=False)

    print("=== A. Sự kiện trên mã đang giữ (NONE) ===")
    print(f"ca={len(tr)} ngày={tr.day.nunique()} episode={tr.episode.nunique()} "
          f"(ledger15 {int((tr.src=='ledger_bar15').sum())} / live1m {int((tr.src=='live_dnse1m').sum())})")
    print(tr.groupby("type").agg(n=("ticker", "size"), ngày=("day", "nunique"), ep=("episode", "nunique"),
                                 ret_T0=("ret", "median"), idio_T0=("idio", "median"),
                                 vni_T0=("vni_ret", "median"), low=("ret_low_day", "median"),
                                 close=("ret_close_day", "median"), late=("late", "mean")).round(4).to_string())
    print(tr.groupby("exchange").size().to_string())
    print("giờ T0:", tr.t0.str[11:13].value_counts().sort_index().to_dict())

    # --- D. phiên VNINDEX giảm mạnh
    v = A.VNI
    vr = (v.Close / v.Close.shift(1) - 1)
    win = [d for d in vr.index if pd.Timestamp("2023-09-12").date() <= d]
    big = vr.loc[win][vr.loc[win] <= -0.03]
    q5 = vr.loc[win].quantile(0.02)
    big2 = vr.loc[win][vr.loc[win] <= q5]
    rows = []
    for d, x in sorted(set(big.items()) | set(big2.items())):
        ds = str(d)
        m = mw[mw.day == ds] if len(mw) else mw
        t = tr[tr.day == ds]
        rows.append({"ngày": ds, "VNI%": round(x * 100, 2), "mw_scans": len(m),
                     "mw_lý_do": "; ".join(sorted(set(m.reason))) if len(m) else "",
                     "mw_mã": ",".join(sorted(set(",".join(m.tickers).split(",")))) if len(m) else "",
                     "ca_riêng": ",".join(f"{a.ticker}@{a.t0[11:16]}({'sàn' if a.at_floor else 'giá'})"
                                          for a in t.itertuples())})
    vd = pd.DataFrame(rows)
    vd.to_csv(os.path.join(O, "vni_big_down_days.csv"), index=False)
    print(f"\n=== D. VNINDEX ≤−3% hoặc ≤p2 ({q5*100:.2f}%) từ 2023-09-12: {len(vd)} phiên ===")
    print(vd.to_string(index=False))

    # --- B. thực thi kịch bản agent GÃY / CHƯA RÕ
    out = []
    ex_all = []
    for s in ("BROKEN", "UNCLEAR"):
        ex = cat(f"*_{s}_d0.5_exec.csv")
        ex = ex[ex.sold > 0].copy()
        ex["scenario"] = s
        ex["src"] = np.where(ex.run == "live", "live_dnse1m", "ledger_bar15")
        ex["type"] = ex.apply(lambda r: ttype(r), axis=1)
        ex = episodes(ex)
        ex_all.append(ex)
        out += summ(ex, f"{s}: tất cả")
        out += summ(ex, f"{s}: tất cả [vị thế, B]", col="B") if s == "UNCLEAR" else []
        if s == "BROKEN":
            for k_, g in ex.groupby("type"):
                out += summ(g, f"BROKEN: {k_}")
            for k_, g in ex.groupby("deferred"):
                out += summ(g, f"BROKEN: hoãn sau 14:00={k_}")
            for k_, g in ex.groupby("book"):
                out += summ(g, f"BROKEN: book {k_}")
            for k_, g in ex.groupby("src"):
                out += summ(g, f"BROKEN: nguồn {k_}")
            out += summ(ex, "BROKEN: lý tưởng bán ngay T0", col="Eideal")
    s = pd.DataFrame(out)
    s.to_csv(os.path.join(O, "summary_exec.csv"), index=False)
    ex = pd.concat(ex_all, ignore_index=True)
    ex.to_csv(os.path.join(O, "exec_all.csv"), index=False)
    print("\n=== B. Cutloss vs GIỮ (E = giá bán ròng/giá giữ − 1; >0 = cutloss thắng) ===")
    print(s.round(2).to_string(index=False))
    b = ex[ex.scenario == "BROKEN"]
    print("\nfill:", b.fill.describe().round(3).to_dict())
    print("impact median %:", round(b.impact.median() * 100, 3), "p90 %:", round(b.impact.quantile(.9) * 100, 3))
    print("max_mode:", b.max_mode.value_counts().sort_index().to_dict())
    print("status:", b.status.value_counts().to_dict())
    print("avg/ref−1 median:", round((b.avg / b.ref - 1).median() * 100, 2),
          " t0_last/ref−1 median:", round((b.t0_last / b.ref - 1).median() * 100, 2))


if __name__ == "__main__":
    main()
