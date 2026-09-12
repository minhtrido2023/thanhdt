#!/usr/bin/env python3
"""Selfcheck cho bin/wait_for_artifact.sh — cơ chế đồng bộ producer→consumer theo ARTIFACT
(sự cố 2026-09-12: hit_details_daily.sh 19:05 chạy TRƯỚC producer ghi file 19:06-19:07).

Ba câu hỏi test phải trả lời được, vì đó là ba cách cơ chế này có thể vô dụng:
  A. producer TRỄ  -> consumer vẫn đúng (chờ rồi chạy), không bỏ cuộc sớm.
  B. producer KHÔNG TỚI -> fail LOUD sau trần, nói rõ đã chờ bao lâu + file mong đợi (§29).
  C. file CŨ (mtime hôm qua) -> KHÔNG được tính là tươi; nếu không, vòng chờ chỉ là trang trí
     đúng ở CHÍNH ca đã gây ra sự cố.

Usage: bin/wait_for_artifact_selfcheck.py   (exit 0 = all pass)
"""
import os
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAIT = os.path.join(ROOT, "bin", "wait_for_artifact.sh")
CONSUMER = os.path.join(ROOT, "bin", "hit_details_daily.sh")

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else "  <- " + str(detail)))


def run(path, hint="producer-X", max_s=2, poll=1):
    e = dict(os.environ)
    e.update({"WAIT_ARTIFACT_MAX": str(max_s), "WAIT_ARTIFACT_POLL": str(poll)})
    t0 = time.time()
    r = subprocess.run(["bash", WAIT, path, hint], capture_output=True, text=True, env=e)
    return r, time.time() - t0


def main():
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "golive_v23_recommendations_2026-09-12.csv")

        # ---------- A. producer trễ: consumer chờ rồi vẫn đúng ----------
        def late_producer():
            time.sleep(1.5)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("ticker,ta\n")

        th = threading.Thread(target=late_producer)
        th.start()
        r, dt = run(f, max_s=10, poll=1)
        th.join()
        check("1 producer trễ 1,5s -> consumer CHỜ rồi tiếp tục (exit 0)",
              r.returncode == 0, "rc=%d err=%r" % (r.returncode, r.stderr))
        check("1b đã thật sự chờ (>=1s), không pass ngay nhờ may mắn",
              dt >= 1.0, "dt=%.2fs" % dt)
        check("1c có báo đã chờ bao lâu (để người đọc log thấy producer đang chậm)",
              "đã chờ" in r.stderr, r.stderr)

        # ---------- B. producer không tới: fail LOUD sau trần ----------
        missing = os.path.join(tmp, "khong_bao_gio_toi.csv")
        r, dt = run(missing, hint="producer-KHONG-TON-TAI", max_s=2, poll=1)
        check("2 producer không tới -> exit 1 (không âm thầm chạy tiếp)",
              r.returncode == 1, "rc=%d" % r.returncode)
        check("2b dừng ĐÚNG ở trần, không treo vô hạn", 2.0 <= dt < 8.0, "dt=%.2fs" % dt)
        check("2c thông báo nêu đã chờ bao lâu VÀ trần bao nhiêu",
              "đã chờ 2s" in r.stderr and "trần 2s" in r.stderr, r.stderr)
        check("2d thông báo nêu ĐÚNG file mong đợi (không chỉ 'thiếu dữ liệu')",
              missing in r.stderr, r.stderr)
        check("2e thông báo nêu AI là producer (người trực biết gọi ai)",
              "producer-KHONG-TON-TAI" in r.stderr, r.stderr)
        check("2f giữ lại lý do gốc của csv_fresh_today (§29: không nuốt chẩn đoán)",
              "KHÔNG TÌM THẤY" in r.stderr, r.stderr)
        check("2g im lặng trên stdout (fail đi đường stderr, không lẫn vào output)",
              r.stdout.strip() == "", r.stdout)

        # ---------- C. file CŨ không được tính là tươi ----------
        stale = os.path.join(tmp, "golive_v23_recommendations_2026-09-11.csv")
        with open(stale, "w", encoding="utf-8") as fh:
            fh.write("ticker,ta\n")
        old = time.time() - 30 * 3600      # >24h: chắc chắn rơi vào ngày lịch trước, mọi TZ
        os.utime(stale, (old, old))
        r, dt = run(stale, max_s=2, poll=1)
        check("3 file tồn tại nhưng mtime HÔM QUA -> vẫn fail (đây chính là ca gây sự cố)",
              r.returncode == 1, "rc=%d err=%r" % (r.returncode, r.stderr))
        check("3b nói rõ file cũ tới mức nào, không chỉ 'thiếu file'",
              "ghi lần cuối" in r.stderr, r.stderr)

        # file cũ, nhưng producer ghi đè GIỮA CHỪNG -> phải nhận ra và đi tiếp
        def toucher():
            time.sleep(1.2)
            os.utime(stale, None)

        th = threading.Thread(target=toucher)
        th.start()
        r, dt = run(stale, max_s=10, poll=1)
        th.join()
        check("3c producer ghi đè file cũ giữa chừng -> nhận ra ngay ở vòng poll kế tiếp",
              r.returncode == 0, "rc=%d err=%r" % (r.returncode, r.stderr))

    # ---------- D. wiring: consumer thật sự dùng cơ chế này ----------
    with open(CONSUMER, encoding="utf-8") as fh:
        src = fh.read()
    i_wait = src.find("wait_for_artifact.sh")
    i_py = src.find("python3 hit_details.py")
    check("4 hit_details_daily.sh gọi wait_for_artifact.sh", i_wait > 0, "không thấy")
    check("4b vòng chờ nằm TRƯỚC lúc chạy hit_details.py (chờ sau thì vô nghĩa)",
          0 < i_wait < i_py, "wait@%d py@%d" % (i_wait, i_py))
    check("4c chờ đúng recs CSV của NGÀY đang xử lý ($DATE), không phải file mới nhất",
          'golive_v23_recommendations_${DATE}.csv' in src, "không thấy pattern $DATE")
    check("4d wait fail -> consumer exit 1, KHÔNG chạy trên dữ liệu cũ",
          "BỎ QUA, không chạy trên dữ liệu cũ" in src, "không thấy nhánh fail")

    # ---------- E. crontab: consumer đặt SAU producer (thắt lưng, ngoài dây đeo) ----------
    cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    lines = [x for x in cron.splitlines() if "hit_details_daily.sh" in x and not x.startswith("#")]
    check("5 crontab có đúng 1 dòng hit_details_daily.sh", len(lines) == 1, str(lines))
    if lines:
        mi, hr = lines[0].split()[0], lines[0].split()[1]
        check("5b giờ chạy 19:12 ICT = 12:12 UTC (sau producer 19:00, artifact ~19:07)",
              (mi, hr) == ("12", "12"), "%s %s" % (mi, hr))

    print("\n%d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("FAILED: " + "; ".join(FAIL))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
