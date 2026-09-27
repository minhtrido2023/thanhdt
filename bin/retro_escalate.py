#!/usr/bin/env python3
"""Escalate một pattern tái diễn của RETRO — CỔNG DUY NHẤT cho bước 6 của `daily_retro.sh`.

LÝ DO TỒN TẠI (bug ack-topic-counter, escalate 3 lần: retro 09-23, 09-25, và question
`retro-pattern-recurring-ack-topic-counter-structural-3retros` 09-25T17:33Z):

  `daily_retro.sh` bước 6 ra lệnh cho phiên retro escalate dưới topic
  `retro-pattern-recurring-<n>-days` — bộ ĐẾM SỐ NGÀY nằm TRONG chuỗi topic. Còn
  `ops_health_check.sh` `_acked()` (khối CHECK5) khớp topic TUYỆT ĐỐI, CỐ Ý (nới lỏng
  thành prefix/substring thì một ack topic ngắn sẽ tắt auto-dispatch của câu hỏi khác
  chưa ai xem — xem comment tại chỗ). Hệ quả cơ học: ack hôm nay cho `…-2days` KHÔNG
  bao giờ phủ được escalation ngày mai `…-3days`; mỗi ngày pattern còn sống là một
  câu hỏi MỚI + một job `wags_autofix` bị đốt cho đúng việc người đã triage.

  arch-reviewer (09-25, NEEDS_CHANGES, required_changes #1) cho 2 hướng và yêu cầu
  CHỌN 1: (a) topic slug ỔN ĐỊNH, số lần tái diễn chuyển vào payload; (b) nới `_acked()`
  khớp theo prefix. Chọn (a): `_acked()` là chốt an toàn của kênh backlog DUY NHẤT của
  fleet, nới nó ra là đổi một bug ồn (escalate thừa) lấy một bug im (tắt nhầm câu hỏi
  chưa ai xem). (a) cũng giữ ops_health_check.sh — logic core — KHÔNG bị đụng tới.

CƠ CHẾ DÙNG CHUNG (điểm mấu chốt — đây là chỗ 2 nơi trước đây lệch nhau):
  Không còn "2 quy ước" nữa. Topic escalate bây giờ do ĐÚNG MỘT hàm sinh ra
  (`stable_topic()`), và quyết định "đã ack chưa" do ĐÚNG MỘT bộ luật quyết định
  (`is_acked()` — bản sao có chủ đích của `_acked()` trong ops_health_check.sh, cùng
  ACK_PREFIX / cùng cách clamp suppress_days / cùng 2 nhánh sd<=0 vs sd>0).
  Chống DRIFT giữa 2 bản: `bin/retro_escalate_selfcheck.py` chạy CHÍNH khối CHECK5 thật
  (qua harness `ops_health_check_selfcheck.run_check5`) trên cùng một bus fixture và
  assert verdict của file này TRÙNG verdict của ops_health_check.sh. Đổi một bên mà
  quên bên kia ⇒ selfcheck ĐỎ. Đó là ràng buộc cơ khí, không phải lời hứa trong docs.

HÀNH VI:
  - Chuẩn hoá slug: mọi đuôi đếm (`-3days`, `-2day`, `-3retros`, `-4`) bị CẮT khỏi topic.
    Phiên retro có cố nhét bộ đếm vào cũng không vào được — đó là mục đích.
  - Đã có câu hỏi ĐÚNG topic đó và nó ĐANG được ack phủ ⇒ SKIP (không mở câu hỏi thứ
    hai cho cùng pattern — luật này trước đây chỉ là 1 dòng văn xuôi trong
    retro-2026-09-24.md:94 mà prompt retro không hề nhắc). Ghi 1 event `status` để số
    ngày tái diễn mới KHÔNG mất.
  - Chưa có, hoặc ack đã hết cửa sổ ⇒ POST câu hỏi (fail-LOUD: thà escalate thừa hơn
    im lặng nuốt một pattern đang tái diễn).

CLI:
  retro_escalate.py --pattern <slug> --days <N> --payload '<json>' [--agent Mike]
                    [--trace-id <id>] [--dry-run] [--bus-root <dir>]
  In ra TOPIC=… / DECISION=POST|SKIP / REASON=… (đọc được bằng mắt lẫn bằng grep).
"""
import argparse
import datetime as dt
import glob
import gzip
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Giữ ĐỒNG BỘ với ops_health_check.sh (ACK_PREFIX dòng ~341, ACK_MAX_SUPPRESS_DAYS ~342).
# retro_escalate_selfcheck.py assert 2 hằng này bằng cách đọc thẳng file kia — đổi 1 bên
# mà quên bên kia là ĐỎ, không phải trôi im lặng.
ACK_PREFIX = "triaged-needs-human:"
ACK_MAX_SUPPRESS_DAYS = 14

TOPIC_PREFIX = "retro-pattern-recurring-"
# Đuôi ĐẾM cần cắt. Chỉ cắt MỘT đuôi ở CUỐI chuỗi; `-3days-holiday` (số ở giữa) giữ nguyên.
_COUNTER_TAIL = re.compile(r"[-_]\d+\s*(?:days?|retros?|lan|times?|x)?$", re.IGNORECASE)
# Slug chỉ gồm bộ đếm (`3days`) — không có phần mô tả nào. Tách riêng khỏi _COUNTER_TAIL
# (cái đó đòi dấu phân cách đứng trước) để không âm thầm sinh topic `…-recurring-3days`,
# tức đúng hình thái bug đang đi diệt.
_COUNTER_ONLY = re.compile(r"^\d+\s*(?:days?|retros?|lan|times?|x)?$", re.IGNORECASE)


def stable_topic(pattern):
    """slug (hoặc cả topic) → topic ỔN ĐỊNH, không chứa bộ đếm."""
    s = str(pattern or "").strip().strip("-")
    if s.startswith(TOPIC_PREFIX):
        s = s[len(TOPIC_PREFIX):]
    # Cắt LẶP: `foo-2days-3` (retro nối thêm lần nữa) vẫn phải về `foo`.
    while True:
        s2 = _COUNTER_TAIL.sub("", s).strip("-_")
        if s2 == s:
            break
        s = s2
    if not s or _COUNTER_ONLY.match(s):
        raise SystemExit("FAIL: --pattern không có phần MÔ TẢ nào sau khi cắt bộ đếm — cần "
                         "một slug có nghĩa (vd 'ack-topic-counter-structural', "
                         f"không phải {str(pattern)!r}).")
    return TOPIC_PREFIX + s


def _iter_events(path):
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def _agent_of(path):
    return os.path.basename(path).split(".")[0].split("_")[0]


def _ts(rec):
    try:
        return dt.datetime.fromisoformat(str(rec.get("ts", "")).replace("Z", "+00:00"))
    except Exception:
        return None


def load_bus(bus_root):
    """Trả (questions, acks) cho toàn bộ inbox + archive.

    questions: [(agent, topic, ts)] · acks: [(topic_đã_bỏ_prefix, a_ts, a_until, sd)]
    """
    inbox = os.path.join(bus_root, "mike", "bus", "inbox")
    files = sorted(glob.glob(os.path.join(inbox, "*.jsonl"))
                   + glob.glob(os.path.join(inbox, "archive", "*.jsonl.gz")))
    questions, acks = [], []
    for p in files:
        agent_p = _agent_of(p)
        for rec in _iter_events(p):
            etype = rec.get("event_type")
            topic = str(rec.get("topic") or "")
            ts = _ts(rec)
            if ts is None:
                continue          # fail-closed y như ops_health_check.sh: ts hỏng ⇒ bỏ qua
            if etype == "status" and topic.startswith(ACK_PREFIX):
                pl = rec.get("payload")
                if isinstance(pl, str):
                    try:
                        pl = json.loads(pl)
                    except Exception:
                        pl = {}
                sd = 0
                if isinstance(pl, dict):
                    try:
                        sd = int(pl.get("suppress_days") or 0)
                    except Exception:
                        sd = 0
                sd = max(0, min(sd, ACK_MAX_SUPPRESS_DAYS))
                acks.append((topic[len(ACK_PREFIX):].strip(), ts,
                             ts + dt.timedelta(days=sd), sd))
            elif etype == "question" and topic:
                questions.append((agent_p, topic, ts))
    return questions, acks


def is_acked(q_agent, q_topic, q_ts, acks, now=None):
    """Bản sao CÓ CHỦ ĐÍCH của `_acked()` trong ops_health_check.sh (khối CHECK5).

    Hai nhánh, giống hệt bản kia:
      sd <= 0 ⇒ phủ VĨNH VIỄN nhưng chỉ cho ĐÚNG instance đã có lúc ack (a_ts >= q_ts).
      sd  > 0 ⇒ phủ theo CỬA SỔ tính từ lúc ack, so với THỜI ĐIỂM CHẠY (a_until >= now).
    Khớp topic TUYỆT ĐỐI, chấp nhận thêm dạng "Agent/topic" — không prefix, không substring.
    """
    if not q_topic:
        return False
    now = now or dt.datetime.now(dt.timezone.utc)
    want = (q_topic, f"{q_agent}/{q_topic}")
    return any(a in want and ((sd <= 0 and a_ts >= q_ts) or (sd > 0 and a_until >= now))
               for a, a_ts, a_until, sd in acks)


def _same_pattern(q_topic, topic):
    """Câu hỏi này có thuộc CÙNG pattern với `topic` (đã ổn định) không?

    Nhận cả các câu hỏi LEGACY còn nhúng bộ đếm (`…-fpt-vendor-backfill-2days`) — đó là
    những cái đang mở THẬT trên bus lúc bản vá này land. Không nhận chúng thì ngày đầu
    tiên sau khi land sẽ mở thêm một câu hỏi trùng nội dung cho mỗi pattern đang treo,
    tức đúng thứ ồn ào mà bản vá này đi diệt.
    """
    q_topic = str(q_topic or "")
    if not q_topic.startswith(TOPIC_PREFIX):
        return False
    try:
        return stable_topic(q_topic) == topic
    except SystemExit:
        return False


def decide(topic, bus_root, now=None):
    """(decision, reason) — 'SKIP' chỉ khi câu hỏi CÙNG pattern đang được ack phủ.

    `is_acked` được gọi với topic NGUYÊN VĂN của câu hỏi (không phải bản ổn định): đó
    đúng là chuỗi mà `_acked()` của ops_health_check.sh nhìn thấy, nên 2 bên không thể
    lệch nhau về phán quyết cho cùng một câu hỏi.
    """
    questions, acks = load_bus(bus_root)
    same = [(ag, tp, ts) for ag, tp, ts in questions if _same_pattern(tp, topic)]
    if not same:
        return "POST", "chưa có câu hỏi nào ở topic ổn định này"
    ag, tp, ts = max(same, key=lambda r: r[2])
    if is_acked(ag, tp, ts, acks, now=now):
        return "SKIP", (f"đã có câu hỏi {ag}/{tp} ({ts:%Y-%m-%dT%H:%M:%SZ}) ĐANG được ack "
                        f"`{ACK_PREFIX}` phủ — không mở câu hỏi thứ hai cho cùng pattern")
    return "POST", (f"đã có câu hỏi {ag}/{tp} ({ts:%Y-%m-%dT%H:%M:%SZ}) nhưng KHÔNG ack nào "
                    f"phủ (chưa triage, hoặc cửa sổ ack đã hết) — escalate lại")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pattern", required=True,
                    help="slug ỔN ĐỊNH mô tả pattern (KHÔNG kèm số ngày — sẽ bị cắt)")
    ap.add_argument("--days", type=int, required=True,
                    help="số RETRO liên tiếp pattern tái diễn — vào PAYLOAD, không vào topic")
    ap.add_argument("--payload", default="{}",
                    help="payload JSON (object). recurring_days sẽ được chèn/ghi đè.")
    ap.add_argument("--agent", default="Mike", help="agent_id đứng tên escalation")
    ap.add_argument("--trace-id", default=os.environ.get("JOB_ID", ""))
    ap.add_argument("--dry-run", action="store_true", help="chỉ in quyết định, không ghi bus")
    ap.add_argument("--bus-root", default=os.environ.get("RETRO_ESCALATE_BUS_ROOT")
                    or os.path.dirname(ROOT),
                    help="thư mục CHA của mike/ (mặc định: WorkingClaude thật)")
    a = ap.parse_args(argv)

    topic = stable_topic(a.pattern)
    try:
        payload = json.loads(a.payload)
        if not isinstance(payload, dict):
            raise ValueError("payload phải là JSON object")
    except Exception as e:
        raise SystemExit(f"FAIL: --payload không phải JSON object hợp lệ: {e}")
    payload["recurring_days"] = a.days
    payload["topic_stable"] = True

    decision, reason = decide(topic, a.bus_root)
    print(f"TOPIC={topic}")
    print(f"DECISION={decision}")
    print(f"REASON={reason}")
    if a.dry_run:
        return 0

    if decision == "POST":
        etype, ev_topic = "question", topic
    else:
        # KHÔNG im lặng: số ngày tái diễn mới vẫn phải nằm trên bus, chỉ là dưới dạng
        # status (không đánh thức kênh backlog) thay vì một câu hỏi trùng lặp.
        etype, ev_topic = "status", f"retro-pattern-recurring-update:{topic}"
        payload["suppressed_reason"] = reason

    cmd = [os.path.join(ROOT, "bin", "append_event.sh"), a.agent, etype, ev_topic,
           json.dumps(payload, ensure_ascii=False)]
    if a.trace_id:
        cmd.append(a.trace_id)
    r = subprocess.run(cmd, capture_output=True, text=True)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        raise SystemExit(f"FAIL: append_event.sh rc={r.returncode} — escalation KHÔNG được ghi")
    print(f"WROTE={etype}:{ev_topic}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
