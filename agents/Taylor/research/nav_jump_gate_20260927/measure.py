#!/usr/bin/env python3
"""Đo phân bố |Δnav| NGÀY thật của 2 account → chọn ngưỡng cho cổng NAV-jump trong
`mike/bin/daily_nav_snapshot.py::nav_jump_verdict()` (job Taylor_20260927_103434).

Vì sao cần script này: bình luận ngưỡng trong `daily_nav_snapshot.py` TRÍCH các con số dưới đây.
Không có script tái lập thì con số trong bình luận không khác gì số bốc (§8 / §29).

Chạy:  $DNA_PYEXE agents/Taylor/research/nav_jump_gate_20260927/measure.py
"""
import csv
import datetime
import os
import statistics
import sys

WC_ROOT = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
ACCOUNTS = ("SpaceX", "ZaloPay")


def load_pairs(account):
    """-> list (d_prev, d, nav_prev, nav, pct) trên các cặp phiên LIỀN KỀ của chính file.

    Cặp liền kề của FILE, không phải "cách nhau ≤N ngày lịch" — cùng bài học với cổng
    price-freeze (Việc 1 của job này): lọc theo ngày lịch âm thầm bỏ mất các cặp qua nghỉ dài.
    """
    path = os.path.join(EXEC_DIR, f"nav_history_{account}.csv")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("date") or not r.get("nav"):
                continue
            try:
                rows.append((datetime.date.fromisoformat(r["date"]), float(r["nav"])))
            except ValueError:
                continue
    rows.sort()
    out = []
    for (dp, np_), (d, n) in zip(rows, rows[1:]):
        if np_ == 0:
            continue
        out.append((dp, d, np_, n, (n / np_ - 1) * 100))
    return rows, out


def main():
    all_pairs = []
    for acc in ACCOUNTS:
        rows, pairs = load_pairs(acc)
        absp = [abs(p[4]) for p in pairs]
        print(f"{acc}: {len(rows)} dòng nav_history ({rows[0][0]} → {rows[-1][0]}), "
              f"{len(pairs)} cặp phiên liền kề")
        if absp:
            worst = max(pairs, key=lambda p: abs(p[4]))
            print(f"  |Δ| max {max(absp):.3f}%  (ngày {worst[1]}, "
                  f"{worst[2]:,.0f} → {worst[3]:,.0f} VND)")
        all_pairs += pairs

    absp = sorted(abs(p[4]) for p in all_pairs)
    n = len(absp)
    print(f"\nGỘP 2 TK: N={n} cặp phiên liên tiếp")
    print(f"  max    = {absp[-1]:.3f}%")
    print(f"  p95    = {statistics.quantiles(absp, n=20)[18]:.3f}%")
    print(f"  median = {statistics.median(absp):.3f}%")
    print(f"  mean   = {statistics.mean(absp):.3f}%   sd = {statistics.stdev(absp):.3f}%")
    print("\n  số cặp vượt từng ngưỡng ứng viên:")
    for thr in (3, 4, 5, 7, 10, 15, 20):
        over = [p for p in all_pairs if abs(p[4]) > thr]
        detail = ("  ← " + ", ".join(f"{p[1]} {p[4]:+.2f}%" for p in over[:4])) if over else ""
        print(f"    >{thr:2d}%  {len(over):3d}/{n}{detail}")

    print("""
KẾT LUẬN (vì sao GIỮ 15%, không hạ về 5% cho khớp cổng công bố):
  - Dữ liệu chưa có phiên nào vượt 5% ⇒ nó KHÔNG phân biệt được 5% với 15%: cả hai đều
    0 false-positive trên lịch sử hiện có. Chọn bằng CHI PHÍ SAI, không bằng số phiên.
  - Cổng này chặn GHI nav_history — chặn oan = mất vĩnh viễn 1 dòng NAV mà §31/WTD/MTD/
    park-trim/active_nav dùng chung. Biên độ HOSE ±7%/phiên ⇒ danh mục tập trung đi ~7%
    thật trong một phiên sàn là khả dĩ; 5% sẽ chặn oan đúng ca đó.
  - Cổng công bố (`NAV_JUMP_BLOCK_PCT`=5%, account_cash_flows.py) chặn oan chỉ làm CHẬM
    báo cáo ⇒ được phép nhạy hơn. Hai câu hỏi khác nhau, hai ngưỡng khác nhau (§28: đừng
    gộp hai câu hỏi về một giá trị).
  - Hệ quả có chủ đích: bước nhảy 5–15% không khai dòng tiền VẪN được ghi ở đây, chỉ bị
    bắt ở cổng công bố.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
