# -*- coding: utf-8 -*-
"""measure_ideas.py — CHỈ ĐO 2 ý của quant-skeptic vòng 2 (đổi số ⇒ KHÔNG áp vào biến thể chính).
 absorb  : bỏ hệ số stepcar/stepca khi OShares của kỳ BCTC đã hấp thụ sự kiện (|log(N_row/N_kỳ_trước) − log f| ≤ tol, tol = min(0,02, log f / 2); luật đặt trước khi đo).
           Đo sai số N_mc so với số CP PIT (cùng mẫu mc_err.py).
 rollfwd : dòng E_unexpl ⇒ E = E_kỳ_trước + NP_P0 (một bước, không lan sang dòng sau). Dựng 2026-05..10 stepcar vào out/measure_rollfwd, so lv và ô với out/r3_final.
           Cần env LVENS2_* như lvens2_pit2. Chạy một mình (~2GB)."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(os.path.join(HERE, ".."))
import lvens2_pit2 as L  # noqa: E402
import mc_err, cmp_cells  # noqa: E402,E401
YMS = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]


def absorb():
    p = pd.read_parquet("out/panel_v31_dump.parquet")
    p = p[(p.src == "BQ") & (p.N > 0)].copy()
    k = p[["ticker", "known", "N"]].drop_duplicates(["ticker", "known"]).sort_values(["ticker", "known"]); k["N_prev"] = k.groupby("ticker").N.shift(1)
    p = p.merge(k[["ticker", "known", "N_prev"]], on=["ticker", "known"], how="left")
    p = p[p.in_universe & (p.ym >= "2014-01") & (p.ym <= "2026-08") & (p.Price > 0)].reset_index(drop=True)
    p["time"] = p.time.astype(L.NS); p["known"] = p.known.astype(L.NS)
    tr = pd.read_csv(mc_err.TRUTH, parse_dates=["date"]); tr["date"] = tr.date.astype(L.NS); tr = tr[tr.shares > 0].sort_values("date")
    p = pd.merge_asof(p.sort_values("time"), tr[["ticker", "date", "shares"]], left_on="time", right_on="date", by="ticker", direction="backward")
    p = p[p.shares.notna()].reset_index(drop=True)
    ca = L.load_ca(); lt = np.log(p.shares.values); ln = np.log(p.N.values)
    print("n_cells", len(p), "N_prev thiếu", int(p.N_prev.isna().sum()))
    for name, rr in (("stepca", False), ("stepcar", True)):
        f = np.asarray(L.ca_factor(p, ca, rr)[0], float); lf = np.log(f)
        ab = (f > 1) & (np.abs(np.log(p.N.values / p.N_prev.values) - lf) <= np.minimum(0.02, lf / 2))
        for lab, ff in ((name, f), (name + "+absorb", np.where(ab, 1.0, f))):
            e = np.abs(ln + np.log(ff) - lt)
            print(f"{lab:16s} mean|e|={e.mean():.5f} >5%={(e > .05).mean():.4f} | ô có f>1 (n={(f > 1).sum()}): mean={e[f > 1].mean():.4f}")
        e0 = np.abs(ln + lf - lt)[ab]; e1 = np.abs(ln - lt)[ab]
        print(f"  {name}: ô bị coi là đã hấp thụ n={ab.sum()} mã={p.ticker[ab].nunique()} | trong đó bỏ hệ số tốt hơn {(e1 < e0 - .01).sum()}, xấu hơn {(e1 > e0 + .01).sum()}")
        p["ab_" + name] = ab
    by = p[p.ab_stepcar].groupby(p.ym.str[:4]).size(); print("ô hấp thụ (stepcar) theo năm:", by.to_dict())


def rollfwd():
    import duckdb
    orig = L.e_guard

    def rf(F, ca, Dcut=None, tol=0.06):
        E, fix, unex = orig(F, ca, Dcut=Dcut, tol=tol)
        out = E.copy(); tk = F.ticker.values; npv = F.NP_P0.values.astype(float)
        for i in np.flatnonzero(unex):
            if i > 0 and tk[i] == tk[i - 1] and np.isfinite(E[i - 1]) and np.isfinite(npv[i]) and E[i - 1] + npv[i] > 0:
                out[i] = E[i - 1] + npv[i]
        return out, fix, unex

    L.e_guard = rf
    for ym in YMS:
        L.run([ym], "pit", "out/measure_rollfwd", L.FROZEN, mc_pit="stepcar", tag="_rollfwd")
    L.e_guard = orig
    px = duckdb.connect().execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{L.CACHE}/ticker/*.parquet')
        WHERE Close > 0 AND CAST(time AS DATE) >= DATE '2025-03-01' AND CAST(time AS DATE) <= DATE '2026-10-31'""").df()
    px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"]).reset_index(drop=True); g = px.groupby("ticker")
    px["hi52"] = np.log(px.Close) - np.log(g.Close.rolling(252, min_periods=120).max().reset_index(level=0, drop=True).sort_index().values)
    rows = []
    for ym in YMS:
        D = px[px.time.dt.strftime("%Y-%m") == ym].time.max()
        u = pd.read_parquet(f"{L.WC}/data/bq_cache/universe_pit/{D.year}.parquet", columns=["time", "ticker", "in_universe"]); u["time"] = pd.to_datetime(u.time)
        ud = u[u.time == D]; f = px[px.time == D][["ticker", "hi52"]]
        a = pd.read_parquet(f"out/r3_final/lvens2_{ym}_mcstepcar.parquet"); b = pd.read_parquet(f"out/measure_rollfwd/lvens2_{ym}_mcstepcar_rollfwd.parquet")
        A, B = cmp_cells.cells(a, ud, f), cmp_cells.cells(b, ud, f)
        com = A.index.intersection(B.index); d = (B.lv_ENS2[com] - A.lv_ENS2[com]).abs()
        un = sorted(a[a.in_universe & a.E_unexpl].ticker); ch = sorted(t for t in com if A.cell[t] != B.cell[t])
        x = a.set_index("ticker"); y = b.set_index("ticker")
        det = ", ".join(f"{t}:E×{y.E[t] / x.E[t]:.2f},Δlv{y.lv_ENS2[t] - x.lv_ENS2[t]:+.3f}" for t in un if t in y.index)
        rows.append((ym, len(com), int((d > 0.01).sum()), int((d > 0.05).sum()), float(d.max()), len(ch), ",".join(ch), det))
    for r in rows:
        print("{} n={} |Δlv|>0,01={} >0,05={} max={:.3f} đổi ô={} [{}]\n    E_unexpl: {}".format(*r))


if __name__ == "__main__":
    {"absorb": absorb, "rollfwd": rollfwd}[sys.argv[1]]()
