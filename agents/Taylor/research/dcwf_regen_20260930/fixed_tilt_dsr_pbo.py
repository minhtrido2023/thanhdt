# -*- coding: utf-8 -*-
"""fixed_tilt_dsr_pbo.py (job Taylor_20260930_161830) — VIỆC 1.

DSR/PBO cho trục "trộn cố định X% DC-book / (100-X)% custom30V" trên phần đã triển khai
của park=0.30 (KHÁC trục waterfall đã bị bác bỏ — không ưu tiên DC mua đầy trước, luôn giữ
tỉ lệ CỐ ĐỊNH mỗi ngày). Tái dùng logic vehicle()/overlay() từ
dc_waterfall_deepdive_regen.py (job Taylor_20260930_122400) nguyên xi, KHÔNG viết lại.

N TRIALS KHAI TRƯỚC KHI CHẠY: 5 — dc_share in {0.20, 0.30, 0.40, 0.50, 0.70}. Điểm 0.30 là
điểm quan sát phụ từ job trước (+0.31pp FULL CAGR); 0.20/0.40 thêm để kiểm tính đơn điệu quanh
0.30; 0.50/0.70 đã có sẵn từ job trước (CÂU 2), giữ lại để đủ N=5 và xem đơn điệu toàn dải.
N=5 < 8 => PBO (cscv_pbo, Bailey et al 2017) vẫn tính được (không cần >=8 config) nhưng báo
kèm caveat thay vì coi là kết luận mạnh; DSR tính trên (a) excess return của cấu hình tốt nhất
IS so với baseline, N=5 cho hệ số hiệu chỉnh multiple-testing.

SELF-CHECK 0 VND: dc_share=0 (rỗng -> vehicle toàn bộ về custom30V, r_wfall == r_base) đã được
job trước xác nhận bằng SELF-CHECK B (identity overlay). Ở đây thêm self-check D: overlay với
delta=(vehicle(dc_share=1e-9)-r_c30v) ~ 0 khi dc_share cực nhỏ (sanity biên).
"""
import os, sys, math
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from dsr_pbo_annex import dsr, cscv_pbo

AUDIT = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_advprice_exp_dcwf_r3_20260930_univpit.csv"
SLEEVE = "data/converge_portfolio_backtest_nav_dcwf_r3_20260930.csv"
IS_END = pd.Timestamp("2019-12-31")
CAP = 0.20
TC = 0.001
SHARES = [0.20, 0.30, 0.40, 0.50, 0.70]   # N=5, declared before running


def load_audit():
    df = pd.read_csv(AUDIT, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    for c in ["state", "bal_etf_ref", "lag_etf_ref", "bal_cash_ref", "lag_cash_ref", "combined_nav"]:
        d[c] = pd.to_numeric(d[c])
    d = d.set_index("ymd").sort_index()
    met = df[df["record_type"] == "METRIC"].set_index("key")["value"]
    return d, met


def metrics(r):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    sd = r.std()
    sh = r.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else np.nan
    return dict(CAGR=cagr * 100, Sharpe=sh, MaxDD=dd * 100, Calmar=cal)


def wf3(r):
    return [("FULL", r), ("IS 2014-19", r[r.index <= IS_END]), ("OOS 2020+", r[r.index > IS_END])]


def table(rows):
    hdr = f"{'config':<34}{'win':<11}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}"
    print(hdr); print("-" * len(hdr))
    for name, r in rows:
        for tag, rr in wf3(r):
            m = metrics(rr)
            print(f"{name:<34}{tag:<11}{m['CAGR']:>7.2f}%{m['Sharpe']:>8.2f}"
                  f"{m['MaxDD']:>7.1f}%{m['Calmar']:>8.2f}")
        print()


def overlay(r_base, w_park_prev, delta_vehicle):
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev.reindex(r_base.index).fillna(0.0) * dv


def main():
    aud, met = load_audit()
    slv = pd.read_csv(SLEEVE, parse_dates=["date"]).set_index("date")
    r_c30v = slv["baseline_ret"]

    nav = aud["combined_nav"]
    r_base = nav.pct_change().dropna()
    w_park = ((aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"])
    w_park_prev = w_park.shift(1).reindex(r_base.index).fillna(0.0)

    m_full = metrics(r_base)
    print("=== SELF-CHECK A — base metrics vs audit METRIC rows (0 VND) ===")
    print(f"  CAGR   {m_full['CAGR']/100:.6f}  vs file {float(met['cagr']):.6f}")
    print(f"  Sharpe {m_full['Sharpe']:.4f}  vs file {float(met['sharpe_252']):.4f}")
    print(f"  MaxDD  {m_full['MaxDD']/100:.6f} vs file {float(met['max_dd']):.6f}")
    print(f"  Calmar {m_full['Calmar']:.4f}  vs file {float(met['calmar']):.4f}")
    ok_a = (abs(m_full['CAGR']/100 - float(met['cagr'])) < 1e-4 and
            abs(m_full['MaxDD']/100 - float(met['max_dd'])) < 1e-4)
    print(f"  PASS: {ok_a}\n")

    dbl = pd.read_csv("data/dc_dbl_panel.csv", index_col=0, parse_dates=True)
    sret = pd.read_csv("data/dc_stock_ret.csv", index_col=0, parse_dates=True)
    park = pd.read_csv("data/dc_park_ret.csv", index_col=0, parse_dates=True)["park_ret"]
    cal = dbl.index
    dbl = dbl.astype(bool)
    if "DHG" in dbl.columns:
        dbl = dbl.copy(); dbl["DHG"] = False
    names = list(dbl.columns)

    def vehicle(dc_share):
        W = pd.DataFrame(0.0, index=cal, columns=names); pk = pd.Series(0.0, index=cal)
        for d in cal:
            cur = [t for t in names if dbl.at[d, t]]
            n = len(cur)
            if n:
                w = min(CAP, dc_share / n)
                for t in cur: W.at[d, t] = w
                pk.loc[d] = max(0.0, 1.0 - w * n)
            else:
                pk.loc[d] = 1.0
        r = pd.Series(0.0, index=cal); prev_w = W.iloc[0].copy(); prev_p = pk.iloc[0]
        turn = pd.Series(0.0, index=cal)
        for i, d in enumerate(cal):
            if i == 0: continue
            ra = float((prev_w * sret.loc[d].reindex(names).fillna(0.0)).sum())
            rp = prev_p * (park.loc[d] if np.isfinite(park.loc[d]) else 0.0)
            t = (float((W.loc[d] - prev_w).abs().sum()) + abs(pk.loc[d] - prev_p)) / 2.0
            r.loc[d] = ra + rp - t * TC
            turn.loc[d] = t
            prev_w = W.loc[d].copy(); prev_p = pk.loc[d]
        yrs = (cal[-1] - cal[0]).days / 365.25
        return r, turn.sum() / yrs, (turn.sum() * TC / yrs)

    # ---- self-check D: dc_share -> 0 reproduces baseline (boundary sanity)
    rv0, _, _ = vehicle(1e-9)
    r_id = overlay(r_base, w_park_prev, (rv0 - r_c30v))
    print(f"=== SELF-CHECK D — dc_share~0 overlay max|r_new - r_base| = {(r_id - r_base).abs().max():.2e} ===\n")

    print(f"=== VIỆC 1 — fixed-tilt DC/custom30V grid, N={len(SHARES)} trials {SHARES} ===")
    rows = [("baseline (custom30V thuần, production)", r_base)]
    matrix_cols = {"baseline": r_base}
    for share in SHARES:
        rv, tvr, drag = vehicle(share)
        rr = overlay(r_base, w_park_prev, (rv - r_c30v))
        label = f"fixed {int(share*100)}/{int((1-share)*100)} DC/c30V"
        rows.append((f"{label} (turn {tvr:.1f}x, TCdrag {drag*100:.2f}pp/yr sleeve)", rr))
        matrix_cols[f"dc{share:.2f}"] = rr
    table(rows)

    # ---- DSR on the IS-best trial's excess vs baseline, N=len(SHARES)
    full_metrics = {k: metrics(v) for k, v in matrix_cols.items() if k != "baseline"}
    is_metrics = {k: metrics(v[v.index <= IS_END]) for k, v in matrix_cols.items() if k != "baseline"}
    best_is = max(is_metrics, key=lambda k: is_metrics[k]["Sharpe"])
    print(f"IS-best trial (by IS Sharpe): {best_is}  (IS Sharpe {is_metrics[best_is]['Sharpe']:.3f})")
    print(f"  Its FULL metrics: {full_metrics[best_is]}")

    ex = (matrix_cols[best_is] - r_base).dropna()
    N = len(SHARES)
    T = len(ex)
    if ex.std() > 0:
        sr_d = ex.mean() / ex.std()
        g3 = float(((ex - ex.mean()) ** 3).mean() / ex.std() ** 3)
        g4 = float(((ex - ex.mean()) ** 4).mean() / ex.std() ** 4)
        emc = 0.5772156649
        from statistics import NormalDist
        if N <= 1:
            sr0 = 0.0
        else:
            z1 = NormalDist().inv_cdf(1 - 1.0 / N)
            z2 = NormalDist().inv_cdf(1 - 1.0 / (N * math.e))
            sr0 = ((1 - emc) * z1 + emc * z2) * ex.std() / math.sqrt(T - 1) / ex.std()
        p, stat = dsr(sr_d, sr0, g3, g4, T)
        print(f"\nDSR (excess of best-IS trial '{best_is}' over baseline, N={N} trials): {p:.4f}  (stat={stat:.3f})")
    else:
        print("\nDSR: excess series has zero variance, cannot compute.")

    # ---- PBO (CSCV) over the N=5 fixed-tilt configs (full-NAV absolute return level)
    M = pd.DataFrame({k: v for k, v in matrix_cols.items() if k != "baseline"}).dropna()
    print(f"\nPBO input matrix: T={len(M)} days, Ncfg={M.shape[1]} (baseline excluded, "
          f"comparing among the {N} DC-tilt trials only)")
    if M.shape[1] >= 2 and len(M) >= 32:
        pbo, logits, n_combos, ncfg, T2 = cscv_pbo(M.values, S=16)
        print(f"PBO (CSCV, S=16, {n_combos} combos, Ncfg={ncfg}, T={T2}) = {pbo:.3f}")
        print(f"  CAVEAT: N={N} < 8 — PBO trên họ nhỏ kém ổn định hơn họ chuẩn (>=8 trial); "
              f"đọc như tín hiệu định hướng, không phải kết luận mạnh độc lập với DSR.")
    else:
        print("PBO: không đủ dữ liệu/config để chạy CSCV.")


if __name__ == "__main__":
    main()
