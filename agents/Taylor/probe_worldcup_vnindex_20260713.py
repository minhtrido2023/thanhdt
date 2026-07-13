# -*- coding: utf-8 -*-
"""
probe_worldcup_vnindex_20260713.py — DESCRIPTIVE ONLY (job Taylor_20260713_122053, Phần A).
Đo return/vol/%ngày-âm của VNINDEX trong từng cửa sổ World Cup vs đối chứng cùng khung lịch
ở các năm không có World Cup. N=4 kỳ hoàn chỉnh — KHÔNG phải backtest, không walk-forward/LOO/DSR.

Ngày World Cup (lịch FIFA chính thức, tra cứu — không xấp xỉ):
  2010 Nam Phi   : 2010-06-11 → 2010-07-11
  2014 Brazil    : 2014-06-12 → 2014-07-13
  2018 Nga       : 2018-06-14 → 2018-07-15
  2022 Qatar     : 2022-11-20 → 2022-12-18  (kỳ MÙA ĐÔNG duy nhất — đối chứng phải cùng khung Nov-Dec)
  2026 Bắc Mỹ    : 2026-06-11 → 2026-07-19  (đang diễn ra, dữ liệu tới hôm nay — chỉ báo partial)
"""
import pandas as pd, numpy as np

ROOT = "/home/trido/thanhdt/WorkingClaude"

# --- build VNINDEX daily close 2005..now: CSV (2000→2026-05-26) + cache parquet 2026 ---
px = pd.read_csv(f"{ROOT}/data/VNINDEX.csv", usecols=["time", "Close"])
px["time"] = pd.to_datetime(px["time"])
try:
    import duckdb
    con = duckdb.connect()
    ext = con.execute(
        f"select time, Close from '{ROOT}/data/bq_cache/ticker/2026.parquet' "
        "where ticker='VNINDEX' order by time"
    ).df()
    ext["time"] = pd.to_datetime(ext["time"])
    px = pd.concat([px[px.time < ext.time.min()], ext], ignore_index=True)
except Exception as e:
    print("WARN: cache 2026 read failed:", e)
px = px.sort_values("time").drop_duplicates("time").reset_index(drop=True)
px["ret"] = px.Close.pct_change()
print(f"VNINDEX series: {px.time.min().date()} → {px.time.max().date()}, {len(px)} phiên\n")

WC = {
    2010: ("2010-06-11", "2010-07-11"),
    2014: ("2014-06-12", "2014-07-13"),
    2018: ("2018-06-14", "2018-07-15"),
    2022: ("2022-11-20", "2022-12-18"),
    2026: ("2026-06-11", "2026-07-19"),
}
WC_YEARS = set(WC)


def window_stats(d):
    if len(d) < 5:
        return None
    cum = d.Close.iloc[-1] / d.Close.iloc[0] - 1
    return dict(n=len(d), cum_ret=cum * 100, mean_daily_bps=d.ret.mean() * 1e4,
                vol_ann=d.ret.std() * np.sqrt(250) * 100, pct_neg=(d.ret < 0).mean() * 100)


def slice_window(y, start_md, end_md):
    s, e = pd.Timestamp(f"{y}-{start_md}"), pd.Timestamp(f"{y}-{end_md}")
    return px[(px.time >= s) & (px.time <= e)]


rows = []
for y, (s, e) in WC.items():
    d = px[(px.time >= s) & (px.time <= e)]
    st = window_stats(d)
    if st:
        rows.append(dict(kind="WC", year=y, window=f"{s}→{e}", **st))

# Đối chứng: cùng khung lịch (month-day) ở các năm KHÔNG có World Cup, 2008..2025
for y in range(2008, 2026):
    if y in WC_YEARS:
        continue
    d = slice_window(y, "06-12", "07-13")      # khung hè (khớp 3 kỳ hè)
    st = window_stats(d)
    if st:
        rows.append(dict(kind="CTRL_summer", year=y, window=f"{y} 06-12→07-13", **st))
    d = slice_window(y, "11-20", "12-18")      # khung đông (khớp Qatar 2022)
    st = window_stats(d)
    if st:
        rows.append(dict(kind="CTRL_winter", year=y, window=f"{y} 11-20→12-18", **st))

df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.round(2).to_string(index=False))

full = px[(px.time >= "2008-01-01")]
print(f"\nToàn mẫu 2008+ : mean daily {full.ret.mean()*1e4:.1f}bps | vol_ann "
      f"{full.ret.std()*np.sqrt(250)*100:.1f}% | %ngày âm {(full.ret<0).mean()*100:.1f}%")

for grp, name in [("CTRL_summer", "Đối chứng HÈ (06-12→07-13, năm không WC)"),
                  ("CTRL_winter", "Đối chứng ĐÔNG (11-20→12-18, năm không WC)")]:
    g = df[df.kind == grp]
    print(f"{name}: mean cum_ret {g.cum_ret.mean():+.2f}% (median {g.cum_ret.median():+.2f}%), "
          f"mean %âm {g.pct_neg.mean():.1f}%, n={len(g)} năm")

wc4 = df[(df.kind == "WC") & (df.year != 2026)]
print(f"WC 4 kỳ hoàn chỉnh (2010/14/18/22): mean cum_ret {wc4.cum_ret.mean():+.2f}% "
      f"(median {wc4.cum_ret.median():+.2f}%), mean %âm {wc4.pct_neg.mean():.1f}%")
