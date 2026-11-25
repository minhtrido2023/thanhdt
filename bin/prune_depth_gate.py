#!/usr/bin/env python3
"""Cổng ĐỘ SÂU ticker_prune — NGUỒN DUY NHẤT cho bq_freshness_check.sh và daily_refresh_v34b_linux.sh.

Luật (user duyệt "B" 25/11/2026, sự cố "không ra plan 25/11"):
    FAIL khi n < max(FLOOR, ceil(RATIO × trung vị n của WINDOW phiên liền trước ĐÃ có dữ liệu)).
Ngưỡng cứng 200 cũ chặn oan phiên thật 23/11 (197 mã) vì universe thu hẹp DẦN (trung vị/tháng
2026: T7 219 → T8 215 → T9 212 → T10 205 → T11 202). Ngưỡng tương đối bám theo trôi chậm nhưng
vẫn chặn rớt ĐỘT NGỘT (ghi thiếu/moi ruột, vd sự cố 07-2026 còn 7-10 mã/ngày).

Số đo (BQ ticker_prune 2012-01-03→2026-11-23, 3.695 phiên có đủ 20 phiên trước):
  * tỉ lệ n / trung vị-20 thấp nhất từ 2016: 0,919 (2022-11-15: 251/273) ⇒ RATIO 0,90 không chặn
    oan phiên nào 2016→nay; 16 phiên <0,90 đều ≤2015 (đứt gãy universe 09-10/2015: 156→107).
  * n nhỏ nhất mỗi năm 2017-2026: 170 168 171 171 267 251 239 252 253 197 ⇒ FLOOR 150 ≈ 0,9×168
    (đáy 2017+), thấp hơn 197 hiện tại; universe co dưới 150 = cần người xem lại, không tự qua.
  * ca 23/11 (đo BQ 25/11): 197 vs trung vị 20 phiên trước 203 ⇒ ngưỡng 183 ⇒ QUA.  202→150 ⇒ CHẶN.

Trung vị NEO vào phiên ĐÃ QUA CỔNG (arch-review vòng 2 #6, 25/11): trước đây trung vị lấy 20 phiên trước BẤT KỂ
phiên đó có FAIL không ⇒ một chuỗi ghi thiếu kéo dài tự đầu độc trung vị (202 rồi chuỗi 170: phiên thứ 11 ngưỡng
còn 153 ⇒ cổng tự cho qua). Giờ duyệt lịch sử theo thời gian: WINDOW phiên đầu (≥ sàn) làm hạt giống, mỗi phiên
sau chỉ được NHẬN vào lịch sử nếu chính nó QUA ngưỡng tính trên lịch sử đã nhận trước nó. Hệ quả cố ý: universe co
THẬT >10% một lần sẽ bị chặn tới khi NGƯỜI xác nhận (không tự hợp thức hoá) — LOOKBACK 150 ngày (~100 phiên) để
hạt giống còn sạch kể cả chuỗi ghi thiếu dài ~2-3 tháng.

Fail-closed: không đủ WINDOW phiên trước / BQ lỗi / output lạ ⇒ rc=2 (KHÔNG ĐO ĐƯỢC) — caller chặn.

CLI:
  prune_depth_gate.py --latest            # ngày = MAX(time) của bảng (bq_freshness_check.sh)
  prune_depth_gate.py --date YYYY-MM-DD   # ngày cụ thể (daily_refresh step [0]; chưa ingest ⇒ n=0)
  prune_depth_gate.py --counts-json '{"date":"…","n":197,"prior":[…]}'   # selfcheck, không gọi BQ
In đúng 1 dòng `PRUNE_DEPTH <PASS|FAIL|UNMEASURABLE> …`. rc: 0 PASS · 1 FAIL · 2 UNMEASURABLE.
"""
import argparse
import csv
import io
import json
import math
import os
import re
import statistics
import subprocess
import sys

FLOOR = 150
RATIO = 0.90
WINDOW = 20
LOOKBACK_DAYS = 150  # ~100 phiên: hạt giống 20 + đủ dài để chuỗi ghi thiếu không chiếm hạt giống — partition-pruned, rẻ
PROJECT = os.environ.get("BQ_PROJECT", "lithe-record-440915-m9")
TABLE = f"`{PROJECT}.tav2_bq.ticker_prune`"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def threshold(hist, floor=FLOOR, ratio=RATIO, window=WINDOW):
    med = statistics.median(hist[-window:])
    return med, max(floor, math.ceil(ratio * med))


def accepted_history(prior, floor=FLOOR, ratio=RATIO, window=WINDOW):
    """prior (cũ→mới) → (đã nhận, số phiên bị loại). Hạt giống = WINDOW phiên đầu có n ≥ sàn; sau đó chỉ nhận
    phiên QUA ngưỡng tính trên lịch sử ĐÃ NHẬN trước nó (phiên FAIL không đầu độc trung vị)."""
    acc, dropped = [], 0
    for x in (int(v) for v in prior):
        if len(acc) < window:
            if x >= floor:
                acc.append(x)
            else:
                dropped += 1
        elif x >= threshold(acc, floor, ratio, window)[1]:
            acc.append(x)
        else:
            dropped += 1
    return acc, dropped


def decide(n, prior, floor=FLOOR, ratio=RATIO, window=WINDOW):
    """→ (verdict, info). prior = list số mã của các phiên TRƯỚC ngày xét (cũ→mới)."""
    acc, dropped = accepted_history(prior, floor, ratio, window)
    if len(acc) < window:
        return "UNMEASURABLE", {"n": n, "reason": f"chỉ có {len(acc)}/{window} phiên trước hợp lệ (≥ sàn {floor}) — "
                                                  "không tính được trung vị"}
    med, thr = threshold(acc, floor, ratio, window)
    info = {"n": n, "median": med, "threshold": thr, "floor": floor, "ratio": ratio, "window": window,
            "dropped": dropped}
    return ("PASS" if n >= thr else "FAIL"), info


def fmt(verdict, date, info):
    if verdict == "UNMEASURABLE":
        return f"PRUNE_DEPTH UNMEASURABLE date={date} n={info.get('n')} reason={info['reason']}"
    med = info["median"]
    med_s = str(int(med)) if float(med).is_integer() else f"{med:.1f}"
    drop = f" loại_khỏi_trung_vị={info['dropped']} phiên FAIL trước đó" if info.get("dropped") else ""
    return (f"PRUNE_DEPTH {verdict} date={date} n={info['n']} threshold={info['threshold']} "
            f"median{info['window']}={med_s} (=max(sàn {info['floor']}, ⌈{info['ratio']:.2f}×trung vị phiên đã qua cổng⌉))"
            + drop)


def query_counts(date_arg):
    """→ (date, n, prior). date_arg=None ⇒ MAX(time)."""
    target = f"DATE('{date_arg}')" if date_arg else f"(SELECT MAX(x.time) FROM {TABLE} AS x)"
    sql = (f"WITH tg AS (SELECT {target} AS d) "
           f"SELECT t.time AS dt, COUNT(DISTINCT t.ticker) AS n FROM {TABLE} AS t, tg "
           f"WHERE t.time BETWEEN DATE_SUB(tg.d, INTERVAL {LOOKBACK_DAYS} DAY) AND tg.d "
           f"GROUP BY dt ORDER BY dt")
    r = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=csv", "--quiet", "--max_rows=1000", sql],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"bq rc={r.returncode}: {' '.join((r.stderr or r.stdout).split())[:200]}")
    rows = list(csv.DictReader(io.StringIO(r.stdout)))
    try:
        pairs = [(row["dt"], int(row["n"])) for row in rows]
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"bq trả output lạ ({type(exc).__name__}): {' '.join(r.stdout.split())[:200]}")
    if not pairs:
        raise RuntimeError("bq không trả phiên nào trong cửa sổ — bảng rỗng/ngày sai")
    date = date_arg or pairs[-1][0]
    n = next((c for d, c in pairs if d == date), 0)
    prior = [c for d, c in pairs if d < date]
    return date, n, prior


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--latest", action="store_true")
    g.add_argument("--date")
    g.add_argument("--counts-json")
    a = ap.parse_args(argv)
    try:
        if a.counts_json:
            j = json.loads(a.counts_json)
            date, n, prior = j["date"], int(j["n"]), list(j["prior"])
        else:
            if a.date and not DATE_RE.match(a.date):
                raise RuntimeError(f"--date sai định dạng: {a.date!r}")
            date, n, prior = query_counts(a.date)
    except Exception as exc:  # noqa: BLE001 — mọi lỗi đo ⇒ fail-closed, nói rõ nguyên nhân
        print(f"PRUNE_DEPTH UNMEASURABLE date={a.date or 'latest'} reason={type(exc).__name__}: {exc}")
        return 2
    verdict, info = decide(n, prior)
    print(fmt(verdict, date, info))
    return {"PASS": 0, "FAIL": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
