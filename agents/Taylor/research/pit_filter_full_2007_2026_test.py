import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import pandas as pd
import cpi_vn
import deposit_rate_vn

VNI = "/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv"
DEPOSIT_CSV_2007_2010 = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/vn_cpi_sbv_2007_2010_winston.csv"

CPI_THRESH = 6.0
DEP_THRESH = 9.0

def merge_cpi_pit(df, time_col="time", end="2026-06-01"):
    """PIT-correct as-of merge of monthly CPI onto a daily frame.

    [FIX 2026-08-25, quant-skeptic look-ahead finding on backtest-2008-v24-full]
    cpi_vn.merge_cpi() tags month M's CPI at timestamp M-01 (month-start) and merge_asof
    backward from there — but VN GSO does not publish month M's CPI until ~month-end M, so a
    trading day early in month M (e.g. 2011-05-05) would incorrectly see May's own CPI instead
    of April's. Shift the monthly series forward by 1 month before merge_asof so a trading day
    only ever sees the PRIOR month's published CPI.
    """
    cpi = cpi_vn.cpi_monthly_df(end=end).copy()
    cpi["time"] = cpi["time"] + pd.DateOffset(months=1)
    d = df.sort_values(time_col).copy()
    d[time_col] = pd.to_datetime(d[time_col])
    return pd.merge_asof(d, cpi, left_on=time_col, right_on="time",
                          direction="backward", suffixes=("", "_cpi"))

def deposit_backfill_2007_2010():
    d = pd.read_csv(DEPOSIT_CSV_2007_2010)
    d["time"] = pd.to_datetime(dict(year=d.year, month=d.month, day=1))
    return d.set_index("time")["deposit_rate_approx_pct"]

def deposit_lookup(dates):
    """as-of backward merge: Tier backfill (2007-2010, from Winston CSV, TEST-ONLY, NOT wired
    into deposit_rate_vn.py per dispatch scope) union with deposit_rate_vn.py (2011+)."""
    bf = deposit_backfill_2007_2010()
    q = pd.DataFrame({"time": pd.to_datetime(dates)}).sort_values("time")
    bf_df = bf.reset_index()
    bf_df.columns = ["time", "deposit_rate_bf"]
    m = pd.merge_asof(q, bf_df, on="time", direction="backward")
    prod = deposit_rate_vn.merge_deposit(q.copy())[["time", "deposit_rate"]]
    m = m.merge(prod, on="time", how="left")
    # production (2011+) wins where available; backfill (2007-2010, test-only) fills the rest
    m["deposit_final"] = m["deposit_rate"].fillna(m["deposit_rate_bf"])
    return m.set_index("time")["deposit_final"]

def main():
    df = pd.read_csv(VNI, usecols=["time", "Close"])
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["roll_max"] = df["Close"].rolling(252, min_periods=1).max()
    df["dd52"] = df["Close"] / df["roll_max"] - 1.0
    fired = df[df["dd52"] <= -0.20].reset_index(drop=True)

    # cluster consecutive fired rows using ORIGINAL df row-index gap <=30 sessions
    fired = fired.merge(df[["time"]].reset_index().rename(columns={"index": "ridx"}), on="time")
    clusters = []
    cur = [fired.iloc[0]]
    for i in range(1, len(fired)):
        if fired.iloc[i]["ridx"] - fired.iloc[i - 1]["ridx"] <= 30:
            cur.append(fired.iloc[i])
        else:
            clusters.append(pd.DataFrame(cur))
            cur = [fired.iloc[i]]
    clusters.append(pd.DataFrame(cur))

    rows = []
    for c in clusters:
        start = c["time"].min()
        end = c["time"].max()
        min_dd = c["dd52"].min()
        n = len(c)
        rows.append({"start": start, "end": end, "n_sessions": n, "min_dd52_pct": round(min_dd * 100, 1)})
    summary = pd.DataFrame(rows)

    starts = summary["start"]
    cpi_at_start = merge_cpi_pit(pd.DataFrame({"time": starts}), end="2026-06-01")["cpi_yoy"].values
    dep_at_start = deposit_lookup(starts).values
    summary["cpi_yoy_at_start"] = cpi_at_start
    summary["deposit_at_start"] = dep_at_start

    def bobby_label(start):
        y = start.year
        if pd.Timestamp("2007-01-01") <= start <= pd.Timestamp("2012-12-31"):
            return "Loai1_MEGA_2007_2012"
        if pd.Timestamp("2018-01-01") <= start <= pd.Timestamp("2019-12-31"):
            return "Loai2_2018_ambiguous"
        if pd.Timestamp("2020-01-01") <= start <= pd.Timestamp("2020-12-31"):
            return "Loai2_2020_COVID"
        if pd.Timestamp("2022-01-01") <= start <= pd.Timestamp("2023-12-31"):
            return "Loai2_2022_SCB"
        return "chua_phan_loai_(truoc_WTO_hoac_khac)"

    summary["bobby_label"] = summary["start"].apply(bobby_label)

    def filter_verdict(cpi, dep, cpi_th, dep_th):
        if pd.isna(cpi) or pd.isna(dep):
            return "FAIL_CLOSED_NaN_(coi_nhu_Loai1_block)"
        if cpi >= cpi_th or dep >= dep_th:
            return "BLOCKED"
        return "PASS"

    summary["verdict_th6.0_9.0"] = summary.apply(
        lambda r: filter_verdict(r["cpi_yoy_at_start"], r["deposit_at_start"], 6.0, 9.0), axis=1)
    summary["verdict_th5.5_9.0"] = summary.apply(
        lambda r: filter_verdict(r["cpi_yoy_at_start"], r["deposit_at_start"], 5.5, 9.0), axis=1)

    pd.set_option("display.max_rows", 200)
    pd.set_option("display.width", 200)
    print(summary.to_string(index=False))

    # ---- 2009 base-effect window: monthly-resolution check (not just cluster-start dates) ----
    print("\n--- 2009-05..2009-11 monthly CPI/deposit + verdict (base-effect window) ---")
    months = pd.date_range("2009-04-01", "2009-12-01", freq="MS")
    cpi_m = merge_cpi_pit(pd.DataFrame({"time": months}), end="2026-06-01")["cpi_yoy"].values
    dep_m = deposit_lookup(months).values
    for m, c, d in zip(months, cpi_m, dep_m):
        v = filter_verdict(c, d, 6.0, 9.0)
        print(f"  {m.date()}  CPI={c:5.2f}%  deposit={d:5.2f}%  -> {v}")

    print("\nSummary CSV written.")
    summary.to_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/pit_filter_full_2007_2026_clusters.csv", index=False)

if __name__ == "__main__":
    main()
