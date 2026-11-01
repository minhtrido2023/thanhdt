# -*- coding: utf-8 -*-
"""(1) Tăng trưởng ngầm định 2 năm giải ngược từ giá (base FCFE engine, r 12,25%, sau đó g_T 4,5%) — live 30/10/2026 + lịch sử.
(2) Selfcheck: tính tay g1s/gQ2s từ ticker_financial thô; PE tự thân từ cache ngày thô; tái lập %RẺ S0 = 53,1% của bài trước."""
import os
import numpy as np
import pandas as pd
import duckdb
from q2_light import h, R, GT

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
P = print
T = pd.Timestamp("2026-10-30")


def implied_g(mult, N=2):
    lo = np.full(len(mult), -0.95)
    hi = np.full(len(mult), 5.0)
    for _ in range(80):
        mid = (lo + hi) / 2
        f = h(mid, N) - mult
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f >= 0, mid, hi)
    out = (lo + hi) / 2
    return np.where((out > -0.94) & (out < 4.99), out, np.nan)


def main():
    v = pd.read_parquet(os.path.join(HERE, "data", "q2_variants.parquet"))
    mult = v.Price.values / (v.base.values / v.OShares.values)
    v["g_impl2"] = implied_g(mult)
    rank_corr = v.groupby("t").apply(lambda g: g.g_impl2.rank().corr(g.mos_S0.rank())).median()
    P(f"Spearman(g ngầm định 2 năm, MoS S0) trung vị theo tháng = {rank_corr:.4f} (−1 ⇒ cùng thông tin, chỉ đổi đơn vị)")
    now = v[v.t == T]
    P(f"Live 30/10/2026: n={now.g_impl2.notna().sum()}; trung vị g ngầm định 2 năm {now.g_impl2.median():.1%}/năm; "
      f"p25 {now.g_impl2.quantile(.25):.1%}; p75 {now.g_impl2.quantile(.75):.1%}; % < 4,5% (g_T) {(now.g_impl2 < GT).mean():.1%}")
    hist = v[v.t >= "2014-01-01"].groupby("t").g_impl2.median()
    P(f"Trung vị cắt ngang theo tháng 2014-2026: min {hist.min():.1%} / trung vị {hist.median():.1%} / max {hist.max():.1%}; "
      f"hôm nay ở phân vị {(hist < hist.loc[T]).mean() * 100:.0f}")
    # so với tăng trưởng NP thực 2 năm sau (tỷ số thường/năm) trong lịch sử
    q = v.sort_values("t").drop_duplicates(["ticker", "qtime"])
    ok = (q.TTM0 > 0) & (q.TTMf2 > 0) & q.g_impl2.notna()
    real = np.sqrt(q.TTMf2[ok] / q.TTM0[ok]) - 1
    P(f"Lịch sử (dòng quý có NP dương 2 đầu): trung vị g ngầm định {q.g_impl2[ok].median():.1%} vs NP thực 2 năm "
      f"{real.median():.1%}/năm; Spearman {q.g_impl2[ok].rank().corr(real.rank()):.3f}")
    cases = now[now.ticker.isin(["FPT", "MWG", "DGC", "VCS", "VNM", "HPG", "PNJ", "REE"])][["ticker", "Price", "PE", "g1s", "g_impl2"]]
    P(cases.round(3).to_string(index=False))
    now[["ticker", "Price", "PE", "PE_own", "g1s", "gQ2s", "g_impl2", "mos_S0"]].to_csv(os.path.join(OUT, "implied_g2_live.csv"), index=False)

    # ---- selfcheck
    P("\n=== SELFCHECK ===")
    bad = 0
    c = duckdb.connect()
    f = c.execute(f"SELECT ticker,time,quarter,NP_P0,NP_P1,NP_P2,NP_P3,NP_P4,NP_P5,NP_P6,NP_P7 FROM "
                  f"read_parquet('{WC}/data/bq_cache/ticker_financial.parquet')").df()
    qp = pd.read_parquet(os.path.join(HERE, "data", "qpanel.parquet"))
    rng = np.random.default_rng(20261102)
    s = qp[qp.g1s.notna() & qp.gQ2s.notna()].sample(200, random_state=1)
    for _, r in s.iterrows():
        raw = f[(f.ticker == r.ticker) & (f.quarter == r.quarter)].sort_values("time").iloc[0]
        t0 = raw[["NP_P0", "NP_P1", "NP_P2", "NP_P3"]].sum()
        t1 = raw[["NP_P4", "NP_P5", "NP_P6", "NP_P7"]].sum()
        g1 = t0 / t1 - 1
        gq = (raw.NP_P0 + raw.NP_P1) / (raw.NP_P4 + raw.NP_P5) - 1
        if not (np.isclose(g1, r.g1s, rtol=1e-9) and np.isclose(gq, r.gQ2s, rtol=1e-9)):
            bad += 1
            P("MISMATCH g", r.ticker, r.quarter, g1, r.g1s)
    P(f"g1s/gQ2s: 200 dòng ngẫu nhiên tính tay từ ticker_financial thô, sai lệch = {bad}")
    m = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    d = c.execute(f"SELECT time,ticker,PE FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')").df()
    d["time"] = pd.to_datetime(d.time)
    old = pd.read_csv(os.path.join(HERE, "data", "pe_2008_2012.csv.gz"), parse_dates=["time"])[["time", "ticker", "PE"]]
    d = pd.concat([old[old.time < d.time.min()], d])
    vn = d[d.ticker == "VNINDEX"].time if (d.ticker == "VNINDEX").any() else None
    bad2 = 0
    s2 = m[m.PE_own.notna() & (m.t >= "2016-01-01")].sample(40, random_state=2)
    for _, r in s2.iterrows():
        x = d[d.ticker == r.ticker].sort_values("time")
        x["mp"] = x.time.dt.to_period("M")
        x = x.groupby("mp").last()
        cur = x.loc[r.t.to_period("M"), "PE"]
        hist_ = x[(x.index < r.t.to_period("M")) & (x.index >= r.t.to_period("M") - 60)].PE
        hist_ = hist_[hist_ > 0]
        own = (np.sum(hist_ < cur) + 0.5 * np.sum(hist_ == cur)) / len(hist_) * 100
        if not np.isclose(own, r.PE_own, atol=1e-9):
            bad2 += 1
            P("MISMATCH PE_own", r.ticker, r.t.date(), own, r.PE_own, len(hist_))
    P(f"PE tự thân: 40 (mã, tháng) ngẫu nhiên tính lại từ cache ngày thô, sai lệch = {bad2}")
    del vn, rng
    pct = (v[v.t == T].mos_S0 > 0).mean()
    P(f"Tái lập bài trước: %RẺ S0 (s0, g_T 4,5%) ngày 30/10/2026 = {pct:.1%} (pin bài trước 53,1%) ⇒ "
      f"{'KHỚP' if abs(pct - 0.531) < 0.0005 else 'LỆCH'}")
    return bad + bad2 + (0 if abs(pct - 0.531) < 0.0005 else 1)


if __name__ == "__main__":
    import sys
    sys.exit(1 if main() else 0)
