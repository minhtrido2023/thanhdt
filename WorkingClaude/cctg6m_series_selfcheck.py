#!/usr/bin/env python3
"""Selfcheck cho append_cctg_rate.py --series 6m (user duyệt 2026-10-07).

Bất biến: (1) --series 6m chỉ ghi data/cctg_rate_vn_6m_events.csv + sidecar riêng, KHÔNG chạm file
12M lẫn sidecar 12M; (2) nhánh 6m giữ đủ guard (idempotent, ngày phải mới hơn mốc 2026-09-30, chặn
lệch >=1,0pp so với số 6M gần nhất, >=2 nguồn khác chủ, nguồn lệch >0,1pp, JOB_ID cấm --force);
(3) gọi 12m SAU một lượt 6m trong cùng process vẫn ghi đúng file 12M (không rò global).
Chạy từ chính thư mục chứa file (tự định vị, chạy được trong worktree)."""
import csv
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import append_cctg_rate as acr  # noqa: E402
import cctg_rate_vn as cctg  # noqa: E402

assert os.path.dirname(os.path.abspath(acr.__file__)) == HERE, "nạp nhầm module ngoài cây này"
TODAY = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
FAILS = []
N = 0


def check(label, cond):
    global N
    N += 1
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


def run(argv, job_id=None):
    old_argv, old_job = sys.argv, os.environ.get("JOB_ID")
    sys.argv = ["append_cctg_rate.py"] + argv
    os.environ.pop("JOB_ID", None)
    if job_id:
        os.environ["JOB_ID"] = job_id
    try:
        return (acr.main() or 0), ""
    except SystemExit as e:
        return 1, str(e.code)
    finally:
        sys.argv = old_argv
        os.environ.pop("JOB_ID", None)
        if old_job is not None:
            os.environ["JOB_ID"] = old_job


def rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def src(pub, url, rate):
    return {"publisher": pub, "url": url, "date": TODAY, "rate": rate}


d = tempfile.mkdtemp(prefix="cctg6m_selfcheck_")
csv12 = os.path.join(d, "cctg_rate_vn_events.csv")
csv6 = os.path.join(d, "cctg_rate_vn_6m_events.csv")
with open(csv12, "w", encoding="utf-8") as f:
    f.write("effective_date,cctg_rate,collected_date,source,note\n2026-10-05,7.4,2026-10-05,manual_verify,seed12\n")
bytes12 = open(csv12, "rb").read()
orig = (acr.CSV_PATH, acr.CSV_PATH_6M, cctg._EVENTS_CSV)
acr.CSV_PATH, acr.CSV_PATH_6M, cctg._EVENTS_CSV = csv12, csv6, csv12
try:
    # C1 mốc ngày: không được ghi <= mốc đông cứng 2026-09-30
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", "2026-09-30", "--source", "manual_verify"])
    check("C1 6m effective == seed date bị chặn", rc == 1 and "not newer" in msg and not rows(csv6))
    # C2 lệch >=1pp so với seed 7,5 bị chặn
    rc, msg = run(["--series", "6m", "--rate", "8.6", "--effective", TODAY, "--source", "manual_verify"])
    check("C2 6m lệch 1,1pp so với seed bị chặn", rc == 1 and "differs" in msg and not rows(csv6))
    # C3 ghi tay hợp lệ -> chỉ file 6M đổi
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "manual_verify"])
    r6 = rows(csv6)
    check("C3 6m manual ghi đúng 1 dòng vào file 6M", rc == 0 and len(r6) == 1 and r6[0]["cctg_rate"] == "7.5")
    check("C3b file 12M không đổi từng byte", open(csv12, "rb").read() == bytes12)
    # C4 idempotent
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "manual_verify"])
    check("C4 6m chạy lại cùng ngày SKIP rc=0, không thêm dòng", rc == 0 and len(rows(csv6)) == 1)
    # C5 JOB_ID cấm --force
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "web_crosscheck_auto",
                   "--note", "x", "--force"], job_id="selfcheck_job")
    check("C5 6m --force bị từ chối khi có JOB_ID", rc == 1 and "--force is refused" in msg)

    # C6-C8 nhánh auto trên file 6M sạch (ngày ghi = hôm nay, nên dọn dòng C3)
    if os.path.exists(csv6):
        os.remove(csv6)
    same_owner = json.dumps([src("CafeF", "https://cafef.vn/a", 7.5), src("Kenh14", "https://kenh14.vn/b", 7.5)])
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "web_crosscheck_auto",
                   "--collected", TODAY, "--note", "x", "--sources", same_owner], job_id="selfcheck_job")
    check("C6 6m 2 nguồn cùng chủ bị chặn", rc == 1 and "distinct owner" in msg and not rows(csv6))
    disagree = json.dumps([src("VietnamNet", "https://vietnamnet.vn/a", 7.5), src("VnExpress", "https://vnexpress.net/b", 7.2)])
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "web_crosscheck_auto",
                   "--collected", TODAY, "--note", "x", "--sources", disagree], job_id="selfcheck_job")
    check("C7 6m 2 nguồn lệch 0,3pp bị chặn", rc == 1 and "disagree" in msg and not rows(csv6))
    good = json.dumps([src("VietnamNet", "https://vietnamnet.vn/cctg6", 7.5), src("VnExpress", "https://vnexpress.net/cctg6", 7.5)])
    rc, msg = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "web_crosscheck_auto",
                   "--collected", TODAY, "--note", "VCB 6M", "--sources", good], job_id="selfcheck_job")
    check("C8 6m auto hợp lệ ghi được", rc == 0 and len(rows(csv6)) == 1)
    check("C8b sidecar 6M được ghi", os.path.exists(os.path.join(d, acr.LAST_AUTO_SOURCES_NAME_6M)))
    check("C8c sidecar 12M KHÔNG bị tạo", not os.path.exists(os.path.join(d, acr.LAST_AUTO_SOURCES_NAME)))
    check("C8d file 12M vẫn không đổi", open(csv12, "rb").read() == bytes12)

    # C9 cùng process: lượt 12m sau lượt 6m phải ghi vào file 12M
    n6 = len(rows(csv6))
    rc, msg = run(["--rate", "7.4", "--effective", TODAY, "--source", "manual_verify"])
    check("C9 12m mặc định sau lượt 6m ghi vào file 12M", rc == 0 and len(rows(csv12)) == 2)
    check("C9b file 6M không bị lượt 12m đụng", len(rows(csv6)) == n6)
finally:
    acr.CSV_PATH, acr.CSV_PATH_6M, cctg._EVENTS_CSV = orig
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{N - len(FAILS)}/{N} PASS")
sys.exit(1 if FAILS else 0)
