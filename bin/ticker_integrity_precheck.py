#!/usr/bin/env python3
"""ticker_integrity_precheck.py — đối chiếu tav2_bq.ticker với tav2_bq.ticker_1m (READ-ONLY).

Vì sao có: incident 2026-11-13 (kb/incidents/2026-11/2026-11-13-ticker-raw-lost-U-Y-block-5-sessions.md)
— 1 writer ngoài làm thủng `ticker` (~503 dòng, VNINDEX 09-12/11 + khối W-Y 13/11) trong khi
`ticker_1m` nguyên vẹn; daily_refresh kéo VNINDEX chỉ tới 06/11 ⇒ publish guard ABORT muộn, sau 30+
phút tính toán. Precheck này bắt sớm, ngay sau step [0].

FAIL (exit 1) nếu, trong 5 phiên gần nhất của ticker_1m:
  (a) MAX(time) của VNINDEX trong `ticker` < MAX(time) của `ticker`, hoặc
  (b) số mã thuộc ticker_1m ∩ ticker_prune(cùng phiên) mà VẮNG trong `ticker` > 2, hoặc
      COUNT(*) `ticker` < 90% `ticker_1m` (lưới thảm hoạ). [arch-review 15/11: ngưỡng 97% trên TỔNG
      dòng báo oan 6/19 phiên tự nhiên — đuôi kém thanh khoản rải rác thiếu 34-43 mã, 95,08-96,97% —
      nên đổi sang universe thanh khoản; 0 mã prune thiếu trong 10-20..11-13.]
      Phiên không có dòng nào trong `ticker` ⇒ FAIL. `ticker` trống cả cửa sổ ⇒ FAIL (không phải fail-open).
  (c) [mở rộng so với yêu cầu gốc, vì (a)+(b) để lọt lỗ VNINDEX ở phiên GIỮA: 1 dòng/800 = 0,1% ≪ 3%
      và MAX vẫn đúng] mỗi phiên mà ticker_1m có VNINDEX thì `ticker` cũng phải có VNINDEX.
Exit 0 = PASS. Exit 2 = KHÔNG ĐO ĐƯỢC (bq lỗi / output không parse được) — caller fail-open + cảnh báo.

Hai truy vấn nhỏ (đều dry_run ước phí trước, in ra log): (1) ticker_1m đếm theo phiên, 5 phiên cuối;
(2) ticker từ phiên cũ nhất trong 5 phiên đó, đếm theo phiên + đếm VNINDEX. Không ghi gì.
Không dùng đồng hồ máy (chỉ so sánh ngày lấy từ BQ) ⇒ không phụ thuộc TZ (§16).
Override cho selfcheck: env TI_BQ_BIN (đường dẫn `bq` giả).
"""
import csv
import io
import os
import re
import subprocess
import sys

PROJECT = "lithe-record-440915-m9"
N_SESSIONS = 5
MIN_RATIO = 0.90        # CHỈ là lưới chặn thảm hoạ; baseline tự nhiên 95,08–99,1% (đo 10-20..11-06)
MAX_LIQ_MISSING = 2     # mã thanh khoản (có trong ticker_prune cùng phiên) vắng trong ticker; đo: 0 trong 10-20..11-13
BQ = os.environ.get("TI_BQ_BIN", "bq")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class MeasureError(Exception):
    """Không đo được (không phải 'dữ liệu hỏng') — caller fail-open."""


def evaluate(n1m, raw, vn1m=None, liq_missing=None):
    """n1m: {date: count ticker_1m}. raw: {date: (count ticker, count VNINDEX)}.
    vn1m: {date: số dòng VNINDEX trong ticker_1m} (None ⇒ bỏ luật (c)).
    liq_missing: {date: số mã thanh khoản vắng trong ticker} (None ⇒ bỏ nhánh universe của (b)).
    Trả list lý do FAIL (rỗng = PASS)."""
    fails = []
    if not n1m:
        raise MeasureError("ticker_1m không trả phiên nào")
    raw_max = max(raw) if raw else None
    vn_dates = [d for d, (_, v) in raw.items() if v > 0]
    vn_max = max(vn_dates) if vn_dates else None
    if raw_max is None:
        fails.append("ticker không có dòng nào trong cửa sổ %d phiên của ticker_1m" % N_SESSIONS)
    elif vn_max is None or vn_max < raw_max:
        fails.append("MAX(time) VNINDEX trong ticker = %s < MAX(time) ticker = %s" % (vn_max, raw_max))
    for d in sorted(vn1m or {}):
        if vn1m[d] > 0 and raw.get(d, (0, 0))[1] == 0:
            fails.append("phiên %s: ticker_1m có VNINDEX nhưng ticker không" % d)
    for d in sorted(liq_missing or {}):
        if liq_missing[d] > MAX_LIQ_MISSING:
            fails.append("phiên %s: %d mã thanh khoản (ticker_1m ∩ ticker_prune) vắng trong ticker (> %d)"
                         % (d, liq_missing[d], MAX_LIQ_MISSING))
    for d in sorted(n1m):
        n_raw = raw.get(d, (0, 0))[0]
        if n_raw < MIN_RATIO * n1m[d]:
            fails.append("phiên %s: ticker=%d < %.0f%% ticker_1m=%d (%.1f%%)"
                         % (d, n_raw, MIN_RATIO * 100, n1m[d], 100.0 * n_raw / n1m[d]))
    return fails


def _bq(sql, dry=False):
    cmd = [BQ, "query", "--use_legacy_sql=false", "--project_id=" + PROJECT, "--quiet"]
    if dry:
        cmd.append("--dry_run")
    else:
        cmd += ["--format=csv", "--max_rows=100"]
    cmd.append(sql)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise MeasureError("bq không chạy được: %r" % e)
    if r.returncode != 0:
        raise MeasureError("bq rc=%d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[:300]))
    return r.stdout


def _rows(out, allow_empty=False):
    rows = list(csv.reader(io.StringIO(out)))
    if allow_empty and not out.strip():   # bq --format=csv in RỖNG HOÀN TOÀN (kể cả header) khi 0 dòng
        return []
    if len(rows) < 2:
        raise MeasureError("bq trả không có dòng dữ liệu: %r" % out[:200])
    return rows[1:]


def _query(sql, allow_empty=False):
    est = _bq(sql, dry=True).strip().splitlines()
    print("  dry_run: %s" % (est[-1] if est else "?"))
    return _rows(_bq(sql), allow_empty)


def measure():
    q1 = ("SELECT CAST(t.time AS STRING) AS d, COUNT(*) AS n, COUNTIF(t.ticker = 'VNINDEX') AS v FROM tav2_bq.ticker_1m AS t "
          "GROUP BY t.time ORDER BY t.time DESC LIMIT %d" % N_SESSIONS)
    n1m, vn1m = {}, {}
    for row in _query(q1):
        if len(row) != 3 or not _DATE.match(row[0]) or not row[1].isdigit() or not row[2].isdigit():
            raise MeasureError("dòng ticker_1m không parse được: %r" % row)
        n1m[row[0]] = int(row[1]); vn1m[row[0]] = int(row[2])
    lo = min(n1m)
    q2 = ("SELECT CAST(t.time AS STRING) AS d, COUNT(*) AS n, COUNTIF(t.ticker = 'VNINDEX') AS v "
          "FROM tav2_bq.ticker AS t WHERE t.time >= DATE('%s') GROUP BY t.time" % lo)
    raw = {}
    for row in _query(q2, allow_empty=True):
        if len(row) != 3 or not _DATE.match(row[0]) or not row[1].isdigit() or not row[2].isdigit():
            raise MeasureError("dòng ticker không parse được: %r" % row)
        raw[row[0]] = (int(row[1]), int(row[2]))
    q3 = ("SELECT CAST(m.time AS STRING) AS d, COUNT(*) AS n FROM tav2_bq.ticker_1m AS m "
          "JOIN tav2_bq.ticker_prune AS p ON p.time = m.time AND p.ticker = m.ticker "
          "LEFT JOIN tav2_bq.ticker AS t ON t.time = m.time AND t.ticker = m.ticker "
          "WHERE m.time >= DATE('%s') AND t.ticker IS NULL GROUP BY m.time" % lo)
    liq = {d: 0 for d in n1m}
    for row in _query(q3, allow_empty=True):   # không dòng = không mã nào vắng = tốt
        if len(row) != 2 or not _DATE.match(row[0]) or not row[1].isdigit():
            raise MeasureError("dòng liq_missing không parse được: %r" % row)
        liq[row[0]] = int(row[1])
    return n1m, raw, vn1m, liq


def main():
    print("ticker_integrity_precheck: ticker vs ticker_1m, %d phiên gần nhất, ngưỡng %.0f%%"
          % (N_SESSIONS, MIN_RATIO * 100))
    try:
        n1m, raw, vn1m, liq = measure()
        fails = evaluate(n1m, raw, vn1m, liq)
    except MeasureError as e:
        print("MEASURE_ERROR (fail-open, KHÔNG phải kết luận dữ liệu hỏng): %s" % e)
        return 2
    except Exception as e:  # lỗi của CHÍNH precheck (traceback sẽ ra rc=1 = giả FAIL) ⇒ ép về 2
        print("MEASURE_ERROR bất ngờ (fail-open): %r" % e)
        return 2
    for d in sorted(n1m):
        print("  %s ticker_1m=%d ticker=%d VNINDEX=%d liq_missing=%d" % (d, n1m[d], raw.get(d, (0, 0))[0], raw.get(d, (0, 0))[1], liq[d]))
    if fails:
        print("FAIL:")
        for f in fails:
            print("  - " + f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
