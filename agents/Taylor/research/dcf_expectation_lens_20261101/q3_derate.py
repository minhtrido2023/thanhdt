# -*- coding: utf-8 -*-
"""Q3 — de-rating sau chuỗi tăng trưởng nhanh: sự kiện, phản ứng giá vs đối chứng, dấu hiệu sớm, case. PREREG §2 Q3."""
import os
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WC = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(HERE, "..", "dcf_vn_calibration_20261101")
OUT = os.path.join(HERE, "out")
P = print
pd.set_option("display.width", 250)
HZ = (63, 126, 252)


def main():
    q = pd.read_parquet(os.path.join(HERE, "data", "qpanel.parquet"))
    m = pd.read_parquet(os.path.join(HERE, "data", "mpanel.parquet"))
    q = q.sort_values(["ticker", "qo"])
    q["g1s_n1"] = q.groupby("ticker").g1s.shift(-1)
    q["qo_n1"] = q.groupby("ticker").qo.shift(-1)
    q.loc[q.qo_n1 != q.qo + 1, "g1s_n1"] = np.nan
    strong = [(q.g1s >= 0.2)] + [(q[f"g1s_l{k}"] >= 0.2) for k in (1, 2, 3)]
    q["in_streak"] = np.logical_and.reduce(strong)               # dòng này + 3 dòng trước đều ≥ 20%
    prev_streak = np.logical_and.reduce([(q[f"g1s_l{k}"] >= 0.2) for k in (1, 2, 3, 4)])
    q["E1"] = prev_streak & (q.g1s < 0.10)
    q["E2"] = prev_streak & ((q.g1s - q.g1s_l1) <= -0.20)
    # universe: mã có trong mpanel (universe_pit phi tài chính) ở tháng của dòng
    m["tp"] = m.t.dt.to_period("M")
    uni = set(zip(m.ticker, m.tp))
    m["sizeq"] = m.groupby("tp").tv3.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False))
    meta = m[["ticker", "tp", "ICB_Code", "tv3", "sizeq", "PE", "PE_own", "fwd6", "fwd12"]].drop_duplicates(["ticker", "tp"])
    q["tp"] = q.time.dt.to_period("M")
    q = q[q.time >= "2014-01-01"]
    q["in_uni"] = [(a, b) in uni for a, b in zip(q.ticker, q.tp)]
    q = q[q.in_uni].merge(meta, on=["ticker", "tp"], how="left")
    q["icb1"] = q.ICB_Code.astype(str).str[0]
    P(f"dòng quý trong universe 2014+: {len(q)}; dòng in_streak: {int(q.in_streak.sum())}; E1: {int(q.E1.sum())} "
      f"({q[q.E1].ticker.nunique()} mã); E2: {int(q.E2.sum())} ({q[q.E2].ticker.nunique()} mã)")

    # giá ngày
    px = pd.read_parquet(os.path.join(PRIOR, "data", "px_daily.parquet"), columns=["time", "ticker", "Close"])
    piv = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()
    piv = piv[piv.index >= "2013-01-01"]
    dates = piv.index.values
    arr = piv.values
    col = {c: i for i, c in enumerate(piv.columns)}

    def rets(i0, j, k0, k1):
        a, b = i0 + k0, i0 + k1
        if a < 0 or b >= len(dates):
            return np.nan
        x0, x1 = arr[a, j], arr[b, j]
        return x1 / x0 - 1 if (np.isfinite(x0) and np.isfinite(x1) and x0 > 0) else np.nan

    def pool_ret(i0, js, k0, k1):
        a, b = i0 + k0, i0 + k1
        if a < 0 or b >= len(dates):
            return np.nan
        x0, x1 = arr[a, js], arr[b, js]
        r = x1 / x0 - 1
        r = r[np.isfinite(r)]
        return np.median(r) if len(r) >= 5 else np.nan

    ev_any = q[q.E1 | q.E2][["ticker", "time"]]
    evt = ev_any.groupby("ticker").time.apply(lambda s: s.values).to_dict()
    m["icb1"] = m.ICB_Code.astype(str).str[0]
    mg = {k: g for k, g in m.groupby("tp")}
    res = {}
    for E in ("E1", "E2"):
        ev = q[q[E]].copy()
        rows = []
        for _, e in ev.iterrows():
            if e.ticker not in col:
                continue
            i0 = np.searchsorted(dates, np.datetime64(e.time), side="right")  # phiên SAU ngày dữ liệu (bảo thủ)
            if i0 >= len(dates):
                continue
            pool = mg.get(e.tp)
            if pool is None:
                continue

            def clean(tks):
                out = []
                for t in tks:
                    if t == e.ticker or t not in col:
                        continue
                    tt = evt.get(t)
                    if tt is not None and np.any(np.abs((tt - np.datetime64(e.time)).astype("timedelta64[D]").astype(int)) <= 183):
                        continue
                    out.append(col[t])
                return out
            js = clean(pool[(pool.icb1 == e.icb1) & (pool.sizeq == e.sizeq)].ticker.unique())
            if len(js) < 5:  # nới: cùng tháng + cùng tercile quy mô
                js = clean(pool[pool.sizeq == e.sizeq].ticker.unique())
            rec = {"ticker": e.ticker, "quarter": f"{e.qo // 4}Q{e.qo % 4 + 1}", "time": e.time, "g1s": e.g1s,
                   "g1s_l1": e.g1s_l1, "n_ctrl": len(js), "PE0": e.PE, "PE_own0": e.PE_own}
            for k0, k1, nm in ((-63, 0, "pre63"), (0, 63, "r63"), (0, 126, "r126"), (0, 252, "r252")):
                r = rets(i0, col[e.ticker], k0, k1)
                c = pool_ret(i0, np.array(js), k0, k1) if js else np.nan
                rec[nm] = r
                rec[f"x_{nm}"] = r - c
            rows.append(rec)
        d = pd.DataFrame(rows)
        # PE 6/12 tháng sau (cuối tháng)
        pe = m.set_index(["ticker", "tp"]).PE
        for k in (6, 12):
            d[f"PE{k}"] = [pe.get((a, (pd.Period(b, "M") + k)), np.nan) for a, b in zip(d.ticker, d.time)]
            ok = (d.PE0 > 0) & (d[f"PE{k}"] > 0)
            d[f"dlogPE{k}"] = np.where(ok, np.log(d[f"PE{k}"] / d.PE0), np.nan)
        d.to_csv(os.path.join(OUT, f"q3_events_{E}.csv"), index=False)
        res[E] = d
        P(f"\n=== {E}: n={len(d)} sự kiện / {d.ticker.nunique()} mã / {d.time.dt.year.nunique()} năm ===")
        rng = np.random.default_rng(3)
        lines = []
        for c in ("pre63", "r63", "r126", "r252", "x_pre63", "x_r63", "x_r126", "x_r252", "dlogPE6", "dlogPE12"):
            x = d[[c, "time"]].dropna()
            yrs = sorted(x.time.dt.year.unique())
            bs = [np.mean(np.concatenate([x[x.time.dt.year == y][c].values for y in rng.choice(yrs, len(yrs))]))
                  for _ in range(2000)]
            lines.append({"metric": c, "n": len(x), "mean": x[c].mean(), "median": x[c].median(),
                          "ci_lo": np.percentile(bs, 2.5), "ci_hi": np.percentile(bs, 97.5),
                          "frac_neg": (x[c] < 0).mean(),
                          "mean_IS": x[x.time.dt.year <= 2019][c].mean(), "mean_OOS": x[x.time.dt.year >= 2020][c].mean()})
        t = pd.DataFrame(lines)
        P(t.round(3).to_string(index=False))
        t.to_csv(os.path.join(OUT, f"q3_summary_{E}.csv"), index=False)

    # dấu hiệu sớm: dòng in_streak, nhãn = dòng KẾ là E1 (g1s_n1 < 10%)
    s = q[q.in_streak & q.g1s_n1.notna()].copy()
    s["y"] = (s.g1s_n1 < 0.10).astype(int)
    s["sig_acc"] = s.acc < 0
    s["sig_accS"] = s.accS < 0
    s["sig_npm"] = s.NPM_P0 < s[[f"npm_l{k}" for k in (1, 2, 3, 4)]].max(axis=1)
    s["sig_roe"] = s.ROE_Trailing < s[[f"roe_l{k}" for k in (1, 2, 3, 4)]].max(axis=1)
    s["sig_pe80"] = s.PE_own > 80
    s["sig_g1dec"] = s.g1s < s.g1s_l1
    P(f"\n=== Dấu hiệu sớm: {len(s)} dòng in_streak có dòng kế; tỷ lệ cơ sở E1 kế tiếp = {s.y.mean():.3f} ===")
    rows = []
    for c in ("sig_acc", "sig_accS", "sig_npm", "sig_roe", "sig_pe80", "sig_g1dec"):
        x = s[[c, "y", "fwd6", "fwd12", "time"]].copy()
        if c == "sig_pe80":
            x = x[s.PE_own.notna()]
        tpr = x[x.y == 1][c].mean()
        fpr = x[x.y == 0][c].mean()
        a = x.groupby(c)
        rows.append({"signal": c, "n": len(x), "share_on": x[c].mean(), "P(E1|on)": x[x[c]].y.mean(),
                     "P(E1|off)": x[~x[c]].y.mean(), "AUC": 0.5 * (tpr + 1 - fpr),
                     "fwd6_on": a.fwd6.mean().get(True), "fwd6_off": a.fwd6.mean().get(False),
                     "fwd12_on": a.fwd12.mean().get(True), "fwd12_off": a.fwd12.mean().get(False),
                     "AUC_IS": None, "AUC_OOS": None})
        for per, mm in (("IS", x.time.dt.year <= 2019), ("OOS", x.time.dt.year >= 2020)):
            xx = x[mm]
            rows[-1][f"AUC_{per}"] = 0.5 * (xx[xx.y == 1][c].mean() + 1 - xx[xx.y == 0][c].mean())
    sg = pd.DataFrame(rows)
    P(sg.round(3).to_string(index=False))
    sg.to_csv(os.path.join(OUT, "q3_early_signals.csv"), index=False)
    # lợi suất 6/12T của nhóm in_streak vs ngoài (mô tả)
    P("\nfwd12 TB: in_streak", round(q[q.in_streak].fwd12.mean(), 4), "| khác", round(q[~q.in_streak].fwd12.mean(), 4))

    # case
    cases = ["DGC", "VCS", "MWG", "FPT", "VNM"]
    c = duckdb.connect()
    tl = ",".join(f"'{x}'" for x in cases)
    d = c.execute(f"SELECT time,ticker,Close,Price,PE FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') "
                  f"WHERE ticker IN ({tl}) ORDER BY time").df()
    d["time"] = pd.to_datetime(d.time)
    qq = pd.read_parquet(os.path.join(HERE, "data", "qpanel.parquet"))
    qq = qq[qq.ticker.isin(cases) & (qq.time >= "2013-06-01")]
    fig, ax = plt.subplots(3, len(cases), figsize=(4.2 * len(cases), 9), sharex=True)
    rows = []
    for j, tk in enumerate(cases):
        dd = d[d.ticker == tk].set_index("time")
        g = qq[qq.ticker == tk].sort_values("time")
        ax[0, j].semilogy(dd.index, dd.Close, lw=0.8)
        ax[0, j].set_title(f"{tk} — giá điều chỉnh (log)")
        ax[1, j].plot(dd.index, dd.PE.where((dd.PE > 0) & (dd.PE < 80)), lw=0.8, color="tab:orange")
        ax[1, j].set_title("P/E (Price thô / EPS TTM)")
        ax[2, j].bar(g.time, g.g1s.clip(-1, 2) * 100, width=60, color=np.where(g.g1s >= 0.2, "tab:green", "tab:gray"))
        ev = q[(q.ticker == tk) & q.E1]
        for t in ev.time:
            for a in ax[:, j]:
                a.axvline(t, color="red", lw=0.8, ls="--")
        ax[2, j].set_title("Tăng trưởng LNST TTM YoY % (xanh ≥20%); đỏ = E1")
        ax[2, j].axhline(0, color="k", lw=0.5)
        for _, r in g.iterrows():
            px_at = dd.Close[dd.index <= r.time + pd.Timedelta(days=1)]
            pe_at = dd.PE[dd.index <= r.time + pd.Timedelta(days=1)]
            rows.append({"ticker": tk, "quarter": r.quarter, "time": r.time.date(), "TTM_NP_bn": r.TTM0 / 1e9,
                         "g1_TTM_YoY": r.g1s, "gQ2_YoY": r.gQ2s, "PE": pe_at.iloc[-1] if len(pe_at) else np.nan,
                         "Close_adj": px_at.iloc[-1] if len(px_at) else np.nan,
                         "E1": bool(((q.ticker == tk) & (q.qo == r.qo) & q.E1).any())})
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q3_cases.png"), dpi=90)
    ct = pd.DataFrame(rows)
    ct.to_csv(os.path.join(OUT, "q3_cases_quarterly.csv"), index=False)
    P("\n=== Case: sự kiện E1/E2 của 5 mã ===")
    for E in ("E1", "E2"):
        x = res[E]
        P(E)
        P(x[x.ticker.isin(cases)][["ticker", "quarter", "time", "g1s_l1", "g1s", "PE0", "PE_own0", "pre63", "r126", "r252",
                                    "x_r126", "x_r252", "dlogPE12"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
