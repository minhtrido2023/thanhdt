#!/usr/bin/env python3
"""universe_gap_fill.py — lấp các phiên THIẾU trong `universe_pit`/`universe_pit_quality` trước golive.

Vì sao có: 2026-10-15 chuỗi 19:00 hỏng cả plan T+1 vì `universe_pit` thiếu phiên 14/10 (chuỗi 14/10
bị chặn, sáng 15/10 chỉ publish DT5G). `bq_freshness_check.sh` chỉ build ĐÚNG phiên hôm nay, còn
`golive_recommend_v23.assert_universe_covers` (cổng §4.3, CỐ Ý không rơi về ticker_prune) thấy
thiếu 1/84 phiên → dừng → DollarBill không được dispatch. Cổng đúng; thiếu là việc của bước build.

Cách làm (không đụng cổng, không đụng builder):
  - tìm phiên trong `tav2_bq.ticker` thuộc [today-LOOKBACK_DAYS, today) chưa có trong `universe_pit`;
  - BỎ phiên "stub" (số dòng thô < B8_RAW_DEPTH × trung vị cửa sổ) — builder sẽ REFUSE đúng ca này;
  - quá MAX_GAPS phiên thiếu ⇒ KHÔNG tự lấp (nghi vấn đề lớn hơn, cần người) — exit 2;
  - lấp tăng dần theo ngày bằng chính `build_universe_pit.py --date D` rồi `build_universe_pit_quality.py
    --date D` (cùng cổng B8; point-in-time vì builder chỉ nhìn dữ liệu <= D; append-only).

Exit: 0 = không thiếu / lấp xong hết · 1 = có phiên lấp lỗi · 2 = quá MAX_GAPS (không làm gì).
Caller (`bq_freshness_check.sh`) coi mọi exit ≠ 0 là WARN, KHÔNG chặn: cổng thật vẫn là
`assert_universe_covers` trong golive.

Usage: universe_gap_fill.py --today YYYY-MM-DD [--dry-run]
"""
import argparse
import datetime as dt
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LOOKBACK_DAYS = 30      # cửa sổ lịch tìm phiên thiếu
MAX_GAPS = 5            # quá số này ⇒ không tự lấp
B8_RAW_DEPTH = 0.90     # trùng build_universe_pit.B8_RAW_DEPTH (stub = dưới ngưỡng này so trung vị)


def find_gap_dates(src_counts, pit_days, today, lookback_days=LOOKBACK_DAYS,
                   raw_depth=B8_RAW_DEPTH):
    """Hàm THUẦN (selfcheck được). src_counts: {date: số dòng thô ticker}; pit_days: set date.

    Trả (gaps, stubs): gaps = phiên đủ dày chưa có trong universe_pit, tăng dần; stubs = phiên thiếu
    nhưng quá mỏng (builder sẽ REFUSE), chỉ để báo. Chỉ xét [today-lookback, today) — today do
    bước build chính của caller lo."""
    lo = today - dt.timedelta(days=lookback_days)
    window = {d: n for d, n in src_counts.items() if lo <= d < today}
    if not window:
        return [], []
    med = statistics.median(window.values())
    gaps, stubs = [], []
    for d in sorted(window):
        if d in pit_days:
            continue
        (gaps if med <= 0 or window[d] / med >= raw_depth else stubs).append(d)
    return gaps, stubs


def _load(today):
    import build_universe_pit as bup
    client = bup.get_client()
    lo = today - dt.timedelta(days=LOOKBACK_DAYS)
    src = {r["d"]: r["n"] for r in bup._q(
        client,
        f"SELECT time AS d, COUNT(*) AS n FROM `{bup.SRC_TABLE}` WHERE time >= @lo AND time < @hi "
        f"GROUP BY time",
        [bup.bigquery.ScalarQueryParameter("lo", "DATE", lo),
         bup.bigquery.ScalarQueryParameter("hi", "DATE", today)])}
    target = f"{bup.PROJECT}.{bup.DATASET}.{bup.TABLE}"
    pit = {r["d"] for r in bup._q(
        client, f"SELECT DISTINCT time AS d FROM `{target}` WHERE time >= @lo AND time < @hi",
        [bup.bigquery.ScalarQueryParameter("lo", "DATE", lo),
         bup.bigquery.ScalarQueryParameter("hi", "DATE", today)])}
    return src, pit


def _run(script, day):
    return subprocess.run([sys.executable, os.path.join(HERE, script), "--date", str(day)]).returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", required=True, help="YYYY-MM-DD — phiên hôm nay (KHÔNG lấp ngày này)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.today)

    src, pit = _load(today)
    gaps, stubs = find_gap_dates(src, pit, today)
    for d in stubs:
        print(f"  [gap-fill] bỏ qua {d}: dòng thô {src[d]} quá mỏng (stub) — builder sẽ REFUSE")
    if not gaps:
        print(f"  [gap-fill] không thiếu phiên nào trong {LOOKBACK_DAYS} ngày trước {today}")
        return 0
    print(f"  [gap-fill] thiếu {len(gaps)} phiên: {', '.join(str(d) for d in gaps)}")
    if len(gaps) > MAX_GAPS:
        print(f"  [gap-fill] ✗ thiếu {len(gaps)} > {MAX_GAPS} phiên — KHÔNG tự lấp, cần người xem "
              f"(build_universe_pit.py --date ... từng ngày)", file=sys.stderr)
        return 2
    if args.dry_run:
        print("  [gap-fill] dry-run — không ghi")
        return 0

    bad = []
    for d in gaps:
        print(f"  [gap-fill] build {d}")
        if _run("build_universe_pit.py", d) != 0 or _run("build_universe_pit_quality.py", d) != 0:
            bad.append(d)
            print(f"  [gap-fill] ✗ {d} lỗi — dừng, các phiên sau KHÔNG build (giữ thứ tự)", file=sys.stderr)
            break
    if bad:
        return 1
    print(f"  [gap-fill] ✓ đã lấp {len(gaps)} phiên")
    return 0


if __name__ == "__main__":
    sys.exit(main())
