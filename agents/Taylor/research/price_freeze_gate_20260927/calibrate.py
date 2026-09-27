#!/usr/bin/env python3
"""Tái lập ngưỡng của gate Price-freeze trong mike/bin/bq_freshness_check.sh.

Chạy:  $DNA_PYEXE calibrate.py [daily_flat_series_v2.csv]

Series đầu vào sinh bằng query dưới (chạy 2026-09-27, job Taylor_20260927_103434).
CẶP SO SÁNH = phiên LIỀN KỀ CỦA BẢNG (LAG trên danh sách ngày distinct), KHÔNG phải
"cách <= N ngày lịch": bản đầu dùng ngưỡng ngày lịch <=7 đã âm thầm bỏ qua phiên đầu sau
Tết (gap 10-12 ngày) và chính 2025-02-03 — một trong hai phiên đóng băng thật — rơi vào đó.

  WITH days AS (SELECT DISTINCT time AS d FROM `PROJ.tav2_bq.ticker_prune` WHERE time >= "2010-01-01"),
  dseq AS (SELECT d, LAG(d) OVER (ORDER BY d) AS dprev FROM days),
  b AS (SELECT ticker, time, Price, Close,
               LAG(Price) OVER (PARTITION BY ticker ORDER BY time) AS p_prev,
               LAG(Close) OVER (PARTITION BY ticker ORDER BY time) AS c_prev,
               LAG(time)  OVER (PARTITION BY ticker ORDER BY time) AS t_prev
        FROM `PROJ.tav2_bq.ticker_prune` WHERE time >= "2010-01-01")
  SELECT b.time, COUNT(*) n_tot, COUNTIF(b.Price=b.p_prev) n_flat,
         COUNTIF(b.Price=b.p_prev AND b.Close!=b.c_prev) n_flat_closemoved
  FROM b JOIN dseq ON b.time=dseq.d AND b.t_prev=dseq.dprev
  WHERE b.Price IS NOT NULL AND b.p_prev IS NOT NULL
    AND b.Close IS NOT NULL AND b.c_prev IS NOT NULL
  GROUP BY b.time ORDER BY b.time
"""
import csv
import statistics as st
import sys

MIN_N = 50          # = MIN_FLAT_SAMPLE trong gate
CHOSEN_PCT = 50     # = MAX_PRICE_FLAT_PCT trong gate


def q(sorted_vals, p):
    return sorted_vals[min(len(sorted_vals) - 1, int(round(p * (len(sorted_vals) - 1))))]


def stats(vals, label):
    s = sorted(vals)
    med = st.median(s)
    sd = 1.4826 * st.median([abs(x - med) for x in s])
    print(f"  {label}: N={len(s)} p50={med:.4f} p90={q(s,.90):.4f} p99={q(s,.99):.4f} "
          f"p99.9={q(s,.999):.4f} max={s[-1]:.4f} robustSD={sd:.4f} "
          f"med+6SD={med+6*sd:.4f} med+8SD={med+8*sd:.4f}")
    return s, med, sd


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "daily_flat_series_v2.csv"
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        n = int(r["n_tot"])
        if n < MIN_N:
            continue
        f, cm = int(r["n_flat"]), int(r["n_flat_closemoved"])
        rows.append((r["time"], n, f, cm, f / n, (f - cm) / n))
    print(f"series: {path} — {len(rows)} phiên (n_tot>={MIN_N}), "
          f"{rows[0][0]} -> {rows[-1][0]}")

    for era in ("2010", "2014", "2020"):
        sub = [x for x in rows if x[0] >= era]
        print(f"\n=== {era}+ ({len(sub)} phiên) ===")
        stats([x[4] for x in sub], "metric A  = tỉ lệ mã Price[t]==Price[t-1]      ")
        stats([x[5] for x in sub], "metric AB = tỉ lệ mã CẢ Price VÀ Close phẳng  ")
        for thr in (0.40, 0.45, 0.50, 0.55, 0.60):
            hA = [x for x in sub if x[4] > thr]
            hB = [x for x in sub if x[5] > thr]
            print(f"  thr={thr:.2f} -> A kêu {len(hA)} phiên {[x[0] for x in hA]}"
                  f" | AB kêu {len(hB)} phiên {[x[0] for x in hB]}")

    print(f"\n=== KẾT LUẬN (ngưỡng đang dùng trong gate: {CHOSEN_PCT}%) ===")
    s14 = [x for x in rows if x[0] >= "2014"]
    A = sorted(x[4] for x in s14)
    body = [x for x in A if x <= 0.5]
    anom = [x for x in A if x > 0.5]
    print(f"  2014+: {len(A)} phiên. Phần THÂN cao nhất = {max(body):.4f}; "
          f"phiên bất thường thấp nhất = {min(anom):.4f} "
          f"=> khoảng trống rỗng [{max(body):.4f} ; {min(anom):.4f}], ngưỡng 0,50 nằm GIỮA.")
    print(f"  False positive thực đo ở 0,50 = {len([x for x in A if x>0.5])-len(anom)} "
          f"/{len(A)} phiên (chỉ khớp đúng {len(anom)} phiên bất thường đã biết).")
    print("  4 phiên bất thường: " +
          ", ".join(f"{x[0]} A={x[4]:.3f} AB={x[5]:.3f}" for x in s14 if x[4] > 0.5))


if __name__ == "__main__":
    main()
