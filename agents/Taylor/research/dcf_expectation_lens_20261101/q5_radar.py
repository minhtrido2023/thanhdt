# -*- coding: utf-8 -*-
"""Q5 — Value Radar (PE thị trường p3, tổng 14,4 RẺ ngày 30/10/2026) vs DCF S0 (%RẺ ~53%): vì sao lệch. PREREG §2 Q5.
KHÔNG chỉnh tham số cho khớp."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
P = print
pd.set_option("display.width", 250)
T = pd.Timestamp("2026-10-30")


def main():
    m = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    v = pd.read_parquet(os.path.join(HERE, "data", "q2_variants.parquet"))
    now = m[m.t == T]
    P(f"universe phi tài chính 30/10/2026: {len(now)} mã; có PE>0: {(now.PE > 0).sum()}; có PE tự thân: {now.PE_own.notna().sum()}")
    po = now.PE_own.dropna()
    P(f"PE tự thân (60T): trung vị {po.median():.1f}; % <20: {(po < 20).mean():.1%}; % <33: {(po < 33.3).mean():.1%}; "
      f"% >67: {(po > 66.7).mean():.1%}")
    pc = now.PCF_own.dropna()
    P(f"P/CF tự thân: n={len(pc)} trung vị {pc.median():.1f}; % <33: {(pc < 33.3).mean():.1%}")
    vn = v[v.t == T]
    P(f"DCF S0 (FCFE 3Y, g 4,5%, r 12,25%): tính được {len(vn)} mã; %RẺ (FV>P) {(vn.mos_S0 > 0).mean():.1%}; "
      f"trung vị P/FV {np.exp(-vn.mos_S0).median():.3f}")
    # lịch sử: trung vị cắt ngang theo tháng
    hist = pd.DataFrame({
        "med_PE": m[(m.PE > 0) & (m.PE < 200)].groupby("t").PE.median(),
        "med_PE_own": m.groupby("t").PE_own.median(),
        "med_PFV_S0": v.groupby("t").mos_S0.median().pipe(lambda s: np.exp(-s)),
        "pct_cheap_S0": v.groupby("t").mos_S0.apply(lambda s: (s > 0).mean()),
    })
    hist = hist[hist.index >= "2014-01-01"]
    pct = {c: (hist[c] < hist[c].loc[T]).mean() * 100 for c in hist.columns}
    P("\n=== Phân vị của giá trị hôm nay trong lịch sử tháng 2014-01 → 2026-10 (154 tháng) ===")
    for c in hist.columns:
        P(f"  {c:13s} hôm nay {hist[c].loc[T]:.3f}  phân vị lịch sử {pct[c]:.0f}  (min {hist[c].min():.3f} / trung vị "
          f"{hist[c].median():.3f} / max {hist[c].max():.3f})")
    hist.to_csv(os.path.join(OUT, "q5_history_medians.csv"))
    # tách nguyên nhân
    P("\n=== Tách nguyên nhân (mã tính được cả DCF S0 và PE tự thân hôm nay) ===")
    j = vn.merge(now[["ticker"]], on="ticker")
    j = j[j.PE_own.notna()]
    j["cheap_dcf"] = j.mos_S0 > 0
    j["cheap_own"] = j.PE_own < 33.3
    P(pd.crosstab(j.cheap_own, j.cheap_dcf, margins=True).to_string())
    # (a) LN TTM tăng 2 năm vs base FCFE 3Y; giá 2 năm
    v24 = v[v.t == T - pd.offsets.MonthEnd(24)][["ticker", "base", "Price", "PE"]]
    v24 = v[(v.t.dt.to_period("M") == (T.to_period("M") - 24))][["ticker", "base", "Close", "PE"]]
    jj = j.merge(v24.rename(columns={"base": "base24", "Close": "Close24", "PE": "PE24"}), on="ticker", how="inner")
    lp = np.log(jj.Close / jj.Close24)
    le = np.where((jj.TTM0 > 0) & (jj.TTM2 > 0), np.log(jj.TTM0 / jj.TTM2), np.nan)
    lb = np.where((jj.base > 0) & (jj.base24 > 0), np.log(jj.base / jj.base24), np.nan)
    P(f"n cặp 24T: {len(jj)}; trung vị Δlog giá 24T {np.nanmedian(lp):+.3f}; Δlog LN TTM 24T {np.nanmedian(le):+.3f}; "
      f"Δlog base FCFE-3Y 24T {np.nanmedian(lb):+.3f}")
    P(f"  ⇒ trung vị Δlog PE (giá − LN) ≈ {np.nanmedian(lp - le):+.3f}; Δlog P/base ≈ {np.nanmedian(lp - lb):+.3f}")
    P(f"  tỷ lệ FCFE base / LN TTM hôm nay (trung vị, cùng mã): "
      f"{np.nanmedian((j.base / j.TTM0).where(j.TTM0 > 0)):.3f}; 24T trước cùng phép đo ở mẫu lịch sử: "
      f"{np.nanmedian((v[v.t.dt.to_period('M') == T.to_period('M') - 24].base / v[v.t.dt.to_period('M') == T.to_period('M') - 24].TTM0).where(lambda s: s > 0)):.3f}")
    # tỷ lệ base/TTM theo năm (trung vị cắt ngang)
    rr = v[v.TTM0 > 0].assign(r=lambda d: d.base / d.TTM0).groupby(v.t.dt.year).r.median()
    P("  trung vị base FCFE-3Y / LN TTM theo năm: " + ", ".join(f"{y}:{x:.2f}" for y, x in rr.items()))
    # (b) mã còn đọc Q2
    lastq = now.merge(m[["ticker", "t"]].head(0), how="left")
    qtr = pd.read_parquet(os.path.join(HERE, "data", "qpanel.parquet"))
    qtr = qtr[qtr.time <= T].sort_values("time").groupby("ticker").quarter.last()
    share = now.ticker.map(qtr).value_counts(normalize=True)
    P(f"(b) quý BCTC mới nhất khả dụng 30/10 trong universe: " + ", ".join(f"{k} {x:.1%}" for k, x in share.head(4).items()))
    del lastq
    # (c) PE thấp vì E tăng hay giá giảm — đã có ở (a). (d) PE_own theo nhóm có/không 2026Q3
    now2 = now.assign(q=now.ticker.map(qtr))
    P("(d) PE tự thân trung vị theo quý BCTC: " + ", ".join(f"{k}: {g.PE_own.median():.1f} (n={g.PE_own.notna().sum()})"
                                                         for k, g in now2.groupby("q") if len(g) > 10))
    pd.DataFrame({"PE_own": po}).describe().to_csv(os.path.join(OUT, "q5_peown_now.csv"))
    j[["ticker", "PE", "PE_own", "mos_S0", "cheap_dcf", "cheap_own", "g1s", "TTM0", "base"]].to_csv(
        os.path.join(OUT, "q5_now_by_ticker.csv"), index=False)


if __name__ == "__main__":
    main()
