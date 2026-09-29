"""
Buoc 1 -- cluster relative-strength (RS) momentum test, PVN-family + Viettel-family.
Thiet ke khoa cung o PREREG_step1.md TRUOC khi script nay chay lan dau. Khong doi tham so sau khi
da thay so (neu can sua, ghi AMENDMENT trong PREREG_step1.md, khong am tham doi).

Tin hieu:  Cluster_RS_200(t) = mean_i[ln Close_i(t) - ln Close_i(t-200)] - [ln VNINDEX(t) - ln VNINDEX(t-200)]
Muc tieu:  Cluster_fwd_3M(t) = mean_i[ln Close_i(t+60) - ln Close_i(t)]
Mau:       luoi hang thang (phien dau moi thang), giong quy uoc series_by_month cua fitness2.py.
Gia thuyet A (continuation) -- xem PREREG_step1.md muc 2 ve ly do chon, khong test gia thuyet B.
"""
import numpy as np
import pandas as pd

DIR = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/kaffa_correlation_cluster_20260910"
LOOKBACK = 200
FWD = 60
NW_LAG = 12   # justification in PREREG_step1.md / report: combined overlap of 200d predictor (~9.5mo)
              # + 60d target (~3mo) sampled monthly ~ 12-13mo, vs fitness2.py's lag=2 (fwd-only overlap)
IS_END = "2019-12-31"
MIN_M_REPORT = 10     # below this: not reported (matches fitness2.py MIN_M_REPORT convention)
MIN_M_CONCLUDE = 18

CLUSTERS = {
    "PVN-family": ["BSR", "GAS", "OIL", "PLX", "PVB", "PVC", "PVD", "PVS", "PVT"],
    "Viettel-family": ["CTR", "VGI", "VTP"],
}


def nw_tstat(x, lag=NW_LAG):
    """Newey-West HAC t-stat for mean(x)==0. Copied verbatim from
    amh_changepoint_fitness_20260910/fitness2.py::nw_tstat (same convention, reused not rewritten)."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 4:
        return np.nan
    e = x - x.mean()
    g0 = (e @ e) / n
    s = g0
    for L in range(1, min(lag, n - 1) + 1):
        gl = (e[L:] @ e[:-L]) / n
        s += 2.0 * (1.0 - L / (lag + 1.0)) * gl
    if s <= 0:
        return np.nan
    return x.mean() / np.sqrt(s / n)


def load():
    panel = pd.read_csv(f"{DIR}/panel.csv", parse_dates=["time"])
    close = panel.pivot(index="time", columns="ticker", values="Close").sort_index()
    vni = pd.read_csv(f"{DIR}/vnindex.csv", parse_dates=["time"]).set_index("time")["VNINDEX"].sort_index()
    # calendar = VNINDEX index (present every session, superset of any single stock's calendar)
    cal = vni.index
    close = close.reindex(cal)
    logc = np.log(close)
    logv = np.log(vni)
    return cal, logc, logv


def build_series(cal, logc, logv, members):
    n = len(cal)
    rs = pd.Series(np.nan, index=cal)
    fwd = pd.Series(np.nan, index=cal)
    sub = logc[members]
    for i in range(LOOKBACK, n - FWD):
        t = cal[i]
        # RS_200: require ALL members non-null at t and t-LOOKBACK
        c_t = sub.iloc[i]
        c_tm = sub.iloc[i - LOOKBACK]
        if c_t.isna().any() or c_tm.isna().any():
            continue
        member_ret = (c_t - c_tm).mean()
        idx_ret = logv.iloc[i] - logv.iloc[i - LOOKBACK]
        rs.iloc[i] = member_ret - idx_ret
        # fwd_3M: require ALL members non-null at t and t+FWD
        c_f = sub.iloc[i + FWD]
        if c_f.isna().any():
            continue
        fwd.iloc[i] = (c_f - c_t).mean()
    return rs, fwd


def monthly_grid(cal, rs, fwd):
    df = pd.DataFrame({"time": cal, "rs": rs.values, "fwd": fwd.values})
    df["ym"] = df["time"].dt.to_period("M")
    form = df.groupby("ym")["time"].min()
    m = df[df["time"].isin(form.values)].set_index("time")[["rs", "fwd"]]
    return m.dropna()


def corr_stats(m):
    n = len(m)
    if n == 0:
        return dict(n_months=n, corr=np.nan, t_nw=np.nan)
    x = (m["rs"] - m["rs"].mean()) / m["rs"].std(ddof=0)
    y = (m["fwd"] - m["fwd"].mean()) / m["fwd"].std(ddof=0)
    g = (x * y).values
    r = float(np.mean(g))  # == Pearson corr since x,y z-scored (population std)
    t = nw_tstat(g)
    return dict(n_months=n, corr=r, t_nw=t)


def leave_one_year_out(m):
    """Per-year sign, restricted to OOS (post IS_END). Returns list of (year, n, corr, sign)."""
    oos = m[m.index > IS_END]
    rows = []
    for yr, g in oos.groupby(oos.index.year):
        if len(g) < 4:
            rows.append((yr, len(g), np.nan, None))
            continue
        x = (g["rs"] - g["rs"].mean())
        y = (g["fwd"] - g["fwd"].mean())
        denom = (x.std(ddof=0) * y.std(ddof=0))
        r = float((x * y).mean() / denom) if denom > 0 else np.nan
        rows.append((yr, len(g), r, np.sign(r) if pd.notna(r) else None))
    return rows


def main():
    cal, logc, logv = load()
    print(f"Calendar: {cal.min().date()} -> {cal.max().date()}, {len(cal)} sessions")
    all_rows = []
    decision_inputs = {}
    for name, members in CLUSTERS.items():
        print("\n" + "=" * 90)
        print(f"CLUSTER: {name}  ({', '.join(members)})")
        rs, fwd = build_series(cal, logc, logv, members)
        m = monthly_grid(cal, rs, fwd)
        first_valid = m.index.min() if len(m) else None
        print(f"  Monthly obs with valid RS_200 & fwd_3M: n={len(m)}, first={first_valid}")

        full = corr_stats(m)
        is_ = corr_stats(m[m.index <= IS_END])
        oos = corr_stats(m[m.index > IS_END])
        for split, r in (("FULL", full), ("IS_pre2020", is_), ("OOS_2020p", oos)):
            grade = ("CONCLUDE" if r["n_months"] >= MIN_M_CONCLUDE else
                     ("THIN" if r["n_months"] >= MIN_M_REPORT else "TOO-THIN(n<10)"))
            star = "*" if pd.notna(r["t_nw"]) and abs(r["t_nw"]) >= 2 else " "
            print(f"  {split:12s} n={r['n_months']:3d}  corr={r['corr']:+.3f}{star}  "
                  f"t_nw={r['t_nw']:+.2f}  [{grade}]" if pd.notna(r["corr"]) else
                  f"  {split:12s} n={r['n_months']:3d}  corr=NaN  [{grade}]")
            all_rows.append(dict(cluster=name, split=split, **r, grade=grade))

        yoy = leave_one_year_out(m)
        print("  Leave-one-year-out (OOS only):")
        oos_sign_full = np.sign(oos["corr"]) if pd.notna(oos["corr"]) else None
        n_years_same_sign = 0
        n_years_scored = 0
        for yr, n, r, sign in yoy:
            tag = f"corr={r:+.3f}" if pd.notna(r) else "n<4 (skip)"
            same = ""
            if sign is not None and oos_sign_full is not None:
                n_years_scored += 1
                if sign == oos_sign_full:
                    n_years_same_sign += 1
                    same = " (same sign as OOS-full)"
            print(f"    {yr}: n={n:2d}  {tag}{same}")
        decision_inputs[name] = dict(
            oos_corr=oos["corr"], oos_n=oos["n_months"], oos_grade=(
                "CONCLUDE" if oos["n_months"] >= MIN_M_CONCLUDE else
                ("THIN" if oos["n_months"] >= MIN_M_REPORT else "TOO-THIN")),
            years_same_sign=n_years_same_sign, years_scored=n_years_scored,
            is_n=is_["n_months"], is_corr=is_["corr"],
        )

    pd.DataFrame(all_rows).round(4).to_csv(f"{DIR}/step1_corr_stats.csv", index=False)

    print("\n" + "=" * 90)
    print("QUYET DINH (theo quy tac khoa o PREREG_step1.md muc 6)")
    print("=" * 90)
    go_flags = []
    for name, d in decision_inputs.items():
        maj = d["years_scored"] > 0 and d["years_same_sign"] >= (d["years_scored"] / 2.0)
        positive_oos = pd.notna(d["oos_corr"]) and d["oos_corr"] > 0
        cluster_go = positive_oos and maj
        go_flags.append(cluster_go)
        print(f"  {name}: OOS corr={d['oos_corr']:+.3f} (n={d['oos_n']}, {d['oos_grade']}), "
              f"sign-consistency {d['years_same_sign']}/{d['years_scored']} nam -> "
              f"{'DAT' if cluster_go else 'KHONG DAT'}")
        print(f"    (tham khao, KHONG dung de quyet dinh) IS pre-2020: corr={d['is_corr']:+.3f} n={d['is_n']}")

    if all(go_flags):
        verdict = "GO — de xuat buoc 2 (ca 2 cum cung dat)"
    elif any(go_flags):
        verdict = "MIXED — KHONG du de GO, KHONG buoc 2 (chi 1/2 cum dat, N=2 qua nho de tin 1 cum)"
    else:
        verdict = "NO-GO — dung ngay, khong buoc 2 (khop tien le Rule 3 + AMH momentum-death)"
    print(f"\nVERDICT: {verdict}")


if __name__ == "__main__":
    main()
