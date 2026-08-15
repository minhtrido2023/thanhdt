#!/usr/bin/env python3
"""Selfcheck cho phần AUTO-CLOSE bus question của bin/check_report_cadence.sh.

VÌ SAO CÓ FILE NÀY (arch-review coord-2026-08-10, verdict NEEDS_CHANGES). Bản auto-close đầu
tiên đóng question bằng `os.path.exists(<target_file cố định>)`, trong khi DETECTOR sinh ra
question lại chấp nhận BẤT KỲ `*_weekly_report_*.md` nào theo ngày trong tên. Tên biến thể
(`SpaceX_weekly_report_2026-08-07.md` — có thật trong repo) làm detector im nhưng closer không
đóng được ⇒ question treo vĩnh viễn ⇒ wags_autofix bị đánh thức 2 lần/ngày cho việc đã xong.
Đúng lớp sự cố mà chính bản vá đó định chặn, và ở đúng ca đó thì không còn đường thoát nào.
Ngoài ra: khoá idempotency phi thời gian (hỏi lại cùng topic là chết vĩnh viễn) và đường ghi
bus nuốt lỗi rồi vẫn in "auto-closed".

Selfcheck KHÔNG chép lại logic: nó TRÍCH hai khối thật đang nằm trong check_report_cadence.sh
(python giữa RC_CLOSE_BEGIN/END và bash giữa RC_BASH_CLOSE_BEGIN/END) rồi chạy chúng trên
fixture. Khối bị đổi tên/di chuyển ⇒ trích thất bại ⇒ FAIL to, không im lặng pass.

  python3 bin/check_report_cadence_selfcheck.py

Đối chứng trên cây hỏng: RC_SRC=<đường dẫn bản cũ> python3 bin/check_report_cadence_selfcheck.py
"""
import gzip
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(os.environ.get("RC_SRC") or (ROOT / "bin" / "check_report_cadence.sh"))
AUDIT = ROOT / "bin" / "bus_question_audit.py"

fails, oks = [], []


def check(name, cond, detail=""):
    (oks if cond else fails).append(f"{name}: {detail}")
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))


def extract(begin, end):
    """Trích phần THÂN giữa 2 marker. Marker nằm trong comment có chữ mô tả đi kèm phía sau,
    nên phải cắt tới HẾT DÒNG chứa marker — nếu không, phần đuôi comment lọt vào script và
    bash chết vì syntax error (đã cắn thật khi viết selfcheck này: 2 ca 'PASS' giả vì khối
    không hề chạy)."""
    src = SRC.read_text(encoding="utf-8")
    m = re.search(re.escape(begin) + r"[^\n]*\n(.*?)[^\n]*" + re.escape(end), src, re.S)
    if not m:
        print(f"❌ FATAL: không trích được khối {begin}…{end} trong {SRC} — "
              "khối đã bị đổi/di chuyển, selfcheck vô hiệu.")
        sys.exit(1)
    return m.group(1)


# ── Phần 1: quyết định "kỳ đã được phủ ⇒ đóng được" (khối python thật) ──────────────────
# Khối RC_CLOSE dùng lại biến của detector (most_recent_weekly, monthly_files, actions…), nên
# ta chạy TOÀN BỘ heredoc detector — đó cũng chính là điều cần khoá: hai bên phải cùng scope.
def detector_block():
    src = SRC.read_text(encoding="utf-8")
    m = re.search(r'PLAN="\$\(python3 - "\$WC_ROOT" "\$TODAY" "\$STATE" "\$DELIVERY_STATE" << \'PYEOF\'\n(.*?)\nPYEOF\n',
                  src, re.S)
    if not m:
        print(f"❌ FATAL: không trích được khối detector trong {SRC}.")
        sys.exit(1)
    block = m.group(1)
    if "RC_CLOSE_BEGIN" not in block or "closable" not in block:
        print("❌ FATAL: khối detector không còn chứa phần RC_CLOSE (auto-close) — "
              "closer đã bị tách ra khỏi scope của detector, đúng thứ selfcheck này cấm.")
        sys.exit(1)
    return block


def run_detector(report_files, pending_topics, today="2026-08-14", scheduled_kind=""):
    """Chạy khối detector+closer thật trên một reports_dir giả."""
    with tempfile.TemporaryDirectory() as td:
        reports = Path(td) / "mike" / "reports"
        reports.mkdir(parents=True)
        for fn in report_files:
            (reports / fn).write_text("fixture", encoding="utf-8")
        state = Path(td) / "state.json"
        state.write_text("{}", encoding="utf-8")
        delivery = Path(td) / "delivery.json"
        records = {}
        import hashlib
        for fn in report_files:
            p = reports / fn
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            records[fn] = {"sha256": sha, "artifact_validated_at": "fixture",
                           "discord": {"status": "delivered", "delivered_at": "fixture", "sha256": sha},
                           "email": {"status": "delivered", "delivered_at": "fixture", "sha256": sha}}
        delivery.write_text(json.dumps({"reports": records}), encoding="utf-8")
        py = Path(td) / "block.py"
        py.write_text(detector_block(), encoding="utf-8")
        env = dict(os.environ, RC_PENDING_TOPICS="\n".join(pending_topics),
                   REPORT_SCHEDULED_KIND=scheduled_kind)
        r = subprocess.run([sys.executable, str(py), td, today, str(state), str(delivery)],
                           capture_output=True, text=True, env=env)
        if r.returncode != 0:
            return {"__crash__": r.stderr.strip()[-400:]}
        return json.loads(r.stdout)


Q_WEEK = "report-cadence-overdue-weekly_2026-08-03_2026-08-07"
Q_MONTH = "report-cadence-overdue-monthly_2026-07"

print(f"check_report_cadence_selfcheck — nguồn: {SRC}")

out = run_detector(["SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md"], [Q_WEEK])
check("#1 happy path: đúng tên file chuẩn ⇒ đóng được",
      [c[0] for c in out.get("closable", [])] == ["weekly_2026-08-03_2026-08-07"], str(out))

# ── CA KILLER của arch-review: tên biến thể. Detector im (nó chỉ đọc ngày trong tên), nên
#    closer BẮT BUỘC phải đóng được — nếu không, question này không còn đường thoát nào.
out = run_detector(["SpaceX_weekly_report_2026-08-07.md"], [Q_WEEK])
check("#2 TÊN FILE BIẾN THỂ vẫn đóng được (ca killer coord-2026-08-10)",
      [c[0] for c in out.get("closable", [])] == ["weekly_2026-08-03_2026-08-07"], str(out))

out = run_detector([], [Q_WEEK])
check("#3 KHÔNG có báo cáo nào ⇒ KHÔNG đóng (không tự dọn câu hỏi còn thật)",
      out.get("closable") == [], str(out))

# Báo cáo CŨ hơn kỳ đang hỏi: kỳ 08-03→08-07 vẫn chưa được phủ.
out = run_detector(["SpaceX_ZaloPay_weekly_report_2026-07-27_to_2026-07-31.md"], [Q_WEEK])
check("#4 chỉ có báo cáo kỳ CŨ hơn ⇒ KHÔNG đóng kỳ mới",
      out.get("closable") == [], str(out))

out = run_detector(["SpaceX_ZaloPay_monthly_report_2026-07.md"], [Q_MONTH])
check("#5 monthly: có báo cáo tháng ⇒ đóng được",
      [c[0] for c in out.get("closable", [])] == ["monthly_2026-07"], str(out))

out = run_detector(["SpaceX_ZaloPay_monthly_report_2026-06.md"], [Q_MONTH])
check("#6 monthly: chỉ có tháng KHÁC ⇒ KHÔNG đóng", out.get("closable") == [], str(out))

out = run_detector(["SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md"], [])
check("#7 không có question nào treo ⇒ closable rỗng (không tự bịa ra việc đóng)",
      out.get("closable") == [], str(out))

out = run_detector(["SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md"],
                   ["report-cadence-overdue-quarterly_2026Q2"])
check("#8 period_key schema LẠ ⇒ KHÔNG đóng (fail về phía để người xem)",
      out.get("closable") == [], str(out))

out = run_detector(["SpaceX_ZaloPay_weekly_report_2026-08-03_to_2026-08-07.md"],
                   [Q_WEEK, Q_MONTH, "report-cadence-overdue-weekly_2026-08-10_2026-08-14"])
_keys = sorted(c[0] for c in out.get("closable", []))
check("#9 nhiều question cùng lúc: đóng ĐÚNG cái đã phủ, giữ cái chưa phủ",
      _keys == ["weekly_2026-08-03_2026-08-07"], str(out))

out = run_detector([], [], today="2026-08-15", scheduled_kind="weekly")
check("#9b lượt scheduled-weekly sinh đúng kỳ T2→T6 vừa đóng, không chờ +3 ngày",
      [a.get("period_key") for a in out.get("actions", [])]
      == ["weekly_2026-08-10_2026-08-14"], str(out))

out = run_detector([], [], today="2026-08-01", scheduled_kind="monthly")
check("#9c lượt scheduled-monthly sinh đúng tháng vừa đóng ngay ngày 1",
      [a.get("period_key") for a in out.get("actions", [])]
      == ["monthly_2026-07"], str(out))


# ── Phần 2: danh sách "còn treo" lấy từ matcher CHÍNH THỐNG (bus_question_audit.py) ─────
def pending_topics_from_bus(events, archived=()):
    """Dựng 1 bus giả rồi hỏi bus_question_audit.py xem còn treo những gì."""
    with tempfile.TemporaryDirectory() as td:
        inbox = Path(td) / "bus" / "inbox"
        (inbox / "archive").mkdir(parents=True)
        (inbox / "Mike.jsonl").write_text(
            "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8")
        if archived:
            with gzip.open(inbox / "archive" / "Mike_2026-07.jsonl.gz", "wt", encoding="utf-8") as f:
                for e in archived:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
        r = subprocess.run([sys.executable, str(AUDIT), "--json"], capture_output=True,
                           text=True, env=dict(os.environ, BUS_AUDIT_ROOT=td))
        try:
            return [q["topic"] for q in json.loads(r.stdout).get("pending", [])]
        except Exception:
            return [f"__crash__ {r.stderr.strip()[-200:]}"]


def ev(etype, topic, ts):
    return {"event_id": f"{etype}-{ts}", "agent_id": "Mike", "event_type": etype,
            "topic": topic, "payload": {}, "ts": ts}


got = pending_topics_from_bus([ev("question", Q_WEEK, "2026-08-10T06:00:00Z")])
check("#10 question chưa ai đóng ⇒ còn treo", Q_WEEK in got, str(got))

got = pending_topics_from_bus([ev("question", Q_WEEK, "2026-08-10T06:00:00Z"),
                               ev("answer", Q_WEEK, "2026-08-10T07:00:00Z")])
check("#11 đã có answer SAU câu hỏi ⇒ hết treo (chạy lần 2 không đóng lại — idempotent)",
      Q_WEEK not in got, str(got))

got = pending_topics_from_bus([ev("question", Q_WEEK, "2026-08-10T06:00:00Z"),
                               ev("answer", Q_WEEK, "2026-08-10T07:00:00Z"),
                               ev("question", Q_WEEK, "2026-08-13T06:00:00Z")])
check("#12 HỎI LẠI cùng topic sau answer cũ ⇒ treo TRỞ LẠI (bản cũ chết vĩnh viễn ca này)",
      Q_WEEK in got, str(got))

got = pending_topics_from_bus([], archived=[ev("question", Q_WEEK, "2026-07-20T06:00:00Z")])
check("#13 question nằm trong archive .jsonl.gz vẫn được nhìn thấy", Q_WEEK in got, str(got))


# ── Phần 3: đường ghi bus không được nuốt lỗi (khối bash thật) ──────────────────────────
def run_bash_closer(append_exit, closable):
    with tempfile.TemporaryDirectory() as td:
        fake_bin = Path(td) / "bin"
        fake_bin.mkdir(parents=True)
        (fake_bin / "append_event.sh").write_text(
            f"#!/usr/bin/env bash\necho 'stub append_event' >&2\nexit {append_exit}\n",
            encoding="utf-8")
        (fake_bin / "append_event.sh").chmod(0o755)
        script = Path(td) / "closer.sh"
        script.write_text("#!/usr/bin/env bash\nset -uo pipefail\n"
                          'PLAN="$1"\nROOT="$2"\n' + extract("RC_BASH_CLOSE_BEGIN", "RC_BASH_CLOSE_END"),
                          encoding="utf-8")
        r = subprocess.run(["bash", str(script), json.dumps({"actions": [], "closable": closable}), td],
                           capture_output=True, text=True)
        # Khối không chạy được (syntax error) mà vẫn để "không thấy auto-closed" đọc thành PASS
        # là ĐÚNG kiểu selfcheck tự thoả — bắt lỗi này thành FAIL to.
        if "syntax error" in r.stderr or "command not found" in r.stderr:
            return "__BLOCK_DID_NOT_RUN__", r.stderr
        return r.stdout, r.stderr


CLOSABLE_FIX = [["weekly_2026-08-03_2026-08-07", "most_recent_weekly=2026-08-07"]]

so, se = run_bash_closer(0, CLOSABLE_FIX)
check("#14 ghi bus THÀNH CÔNG ⇒ in 'auto-closed'", "auto-closed" in so, so.strip() or se.strip())

so, se = run_bash_closer(3, CLOSABLE_FIX)
check("#15 ghi bus LỖI ⇒ KHÔNG in 'auto-closed' (bản cũ `|| true` rồi echo vô điều kiện)",
      "auto-closed" not in so and so != "__BLOCK_DID_NOT_RUN__", so.strip())
check("#16 ghi bus LỖI ⇒ có cảnh báo ra stderr, nói rõ question VẪN TREO",
      "KHÔNG ghi được answer" in se and "VẪN TREO" in se, se.strip()[:200])

so, se = run_bash_closer(0, [])
check("#17 không có gì để đóng ⇒ im lặng, không gọi append_event",
      so != "__BLOCK_DID_NOT_RUN__" and "auto-closed" not in so
      and "stub append_event" not in se, (so + se).strip())

print()
if fails:
    print(f"❌ FAIL {len(fails)}/{len(fails) + len(oks)}")
    for f in fails:
        print("   -", f)
    sys.exit(1)
print(f"✅ PASS {len(oks)}/{len(oks)}")
