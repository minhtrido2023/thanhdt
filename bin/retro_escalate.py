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
# Đuôi ĐẾM: số ở CUỐI, đơn vị tuỳ chọn, dấu phân cách tuỳ chọn ở cả 2 phía của số. Phủ
# CẢ dạng dính (`-2days`) LẪN dạng có gạch (`-2-days`) — cả hai đều CÓ THẬT trên bus
# (`retro-pattern-recurring-2-days` 08-09, `…-nav-price-xcheck-gate-2-days` 09-09).
_COUNTER_TAIL = re.compile(r"[-_ ]?\d+[-_ ]?(?:days?|retros?|lan|times?|x)?$", re.IGNORECASE)


def has_counter_tail(s):
    return bool(_COUNTER_TAIL.search(str(s or "")))


def stable_topic(pattern):
    """slug → topic ỔN ĐỊNH. TỪ CHỐI (không tự cắt) nếu slug còn mang bộ đếm.

    ⚠️ Bản vòng 1 CẮT đuôi đếm. arch-review vòng 1 bác đúng: cắt là VIẾT LẠI, mà viết
    lại thì 2 slug mô tả KHÁC NHAU có thể gộp thành MỘT topic — `plan-t1-not-ready-
    0001743767` và `…-0001743768` (2 account tiền thật) cùng ra `…-plan-t1-not-ready`
    ⇒ ack của pattern này nuốt IM LẶNG escalation của pattern kia. Đổi một bug ỒN
    (escalate thừa) lấy một bug IM là đi ngược đúng lý do chọn hướng này.
    Nên: từ chối, fail-loud, bắt người gọi đặt tên không có đuôi số. Việc nhận diện các
    câu hỏi LEGACY còn mang bộ đếm nằm ở `_same_pattern()` — khớp MỘT CHIỀU từ topic đã
    biết ra biến thể có đếm, không bao giờ suy ngược từ 2 chuỗi lạ về cùng một gốc.
    """
    s = str(pattern or "").strip().strip("-_ ")
    if s.startswith(TOPIC_PREFIX):
        s = s[len(TOPIC_PREFIX):]
    if not s:
        raise SystemExit("FAIL: --pattern rỗng — cần một slug mô tả pattern.")
    if has_counter_tail(s):
        raise SystemExit(
            f"FAIL: --pattern {str(pattern)!r} kết thúc bằng một CON SỐ. Topic escalate "
            "phải ỔN ĐỊNH qua các ngày: số lần tái diễn đi vào --days (payload), không "
            "vào topic — đó chính là bug ack-topic-counter. Nếu con số là một phần của "
            "danh tính (số tài khoản, id thread) thì viết lại cho nó không đứng cuối, "
            "vd 'plan-t1-not-ready-acct0001743768'.")
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
    """Trả (questions, acks, resolvers) cho toàn bộ inbox + archive.

    questions/resolvers: [(agent, topic, ts)] · acks: [(topic_đã_bỏ_prefix, a_ts, a_until, sd)]

    Thiếu thư mục inbox ⇒ FAIL LOUD. Trả rỗng ở đây có nghĩa "chưa ai escalate bao giờ"
    ⇒ POST — nghe thì fail-open vô hại, nhưng nó biến một lỗi đường dẫn (vd chạy từ
    worktree, `--bus-root` trỏ nhầm) thành "kết luận về nội dung bus", đúng lớp lỗi mà
    chính `ops_health_check.sh` đã phải vá (nhánh không thấy `bus/inbox` là WARN, không
    phải "không có câu hỏi").
    """
    inbox = os.path.join(bus_root, "mike", "bus", "inbox")
    if not os.path.isdir(inbox):
        raise SystemExit(
            f"FAIL: KHÔNG tìm thấy thư mục bus {inbox} — không thể kết luận pattern này "
            "đã được escalate/ack hay chưa. Kiểm --bus-root (mặc định là thư mục CHA của "
            "mike/; chạy từ worktree sẽ ra sai) thay vì coi bus là rỗng.")
    files = sorted(glob.glob(os.path.join(inbox, "*.jsonl"))
                   + glob.glob(os.path.join(inbox, "archive", "*.jsonl.gz")))
    questions, acks, resolvers = [], [], []
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
            elif etype in ("answer", "decision") and topic:
                resolvers.append((agent_p, topic, ts))
    return questions, acks, resolvers


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

    Khớp MỘT CHIỀU: từ `topic` ĐÃ BIẾT sinh ra tập biến thể có bộ đếm và so khớp. Không
    bao giờ chuẩn hoá 2 chuỗi lạ rồi so — đó là đường dẫn tới false-collapse (xem
    `stable_topic`). Nhận các câu hỏi LEGACY đang mở thật trên bus, cả dạng dính
    (`…-2days`) lẫn dạng có gạch (`…-2-days`).
    """
    q_topic = str(q_topic or "")
    if q_topic == topic:
        return True
    return bool(re.fullmatch(
        re.escape(topic) + r"[-_ ]?\d+[-_ ]?(?:days?|retros?|lan|times?|x)?",
        q_topic, re.IGNORECASE))


def decide(topic, bus_root, now=None):
    """(decision, reason) — 'SKIP' chỉ khi câu hỏi CÙNG pattern đang được ack phủ.

    `is_acked` được gọi với topic NGUYÊN VĂN của câu hỏi (không phải bản ổn định): đó
    đúng là chuỗi mà `_acked()` của ops_health_check.sh nhìn thấy, nên 2 bên không thể
    lệch nhau về phán quyết cho cùng một câu hỏi.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    questions, acks, resolvers = load_bus(bus_root)
    same = [(ag, tp, ts) for ag, tp, ts in questions if _same_pattern(tp, topic)]
    if not same:
        return "POST", "chưa có câu hỏi nào ở topic ổn định này"
    # Câu hỏi ĐÃ ĐÓNG (có answer/decision đúng topic, sau nó) không còn là căn cứ để
    # SKIP: ops_health_check cũng đã bỏ nó khỏi backlog, nên dựa vào nó để im lặng là
    # nuốt một lần tái diễn THẬT. Khớp exact-topic (hẹp hơn `_resolved` bên kia, vốn
    # còn nhận hậu tố) — sai sót nghiêng về phía POST, tức phía ỒN, đúng hướng an toàn.
    same = [(ag, tp, ts) for ag, tp, ts in same
            if not any(rt == tp and rts >= ts for _ra, rt, rts in resolvers)]
    if not same:
        return "POST", ("mọi câu hỏi cũ của pattern này ĐÃ có answer/decision — lần tái "
                        "diễn này là lần MỚI, phải escalate")
    ag, tp, ts = max(same, key=lambda r: r[2])
    if is_acked(ag, tp, ts, acks, now=now):
        # ĐƯỜNG THOÁT cho ack sd<=0: `_acked` coi nó là VĨNH VIỄN cho đúng instance đó,
        # điều đúng với việc "không auto-dispatch lại câu hỏi CŨ". Nhưng dùng nguyên
        # tính vĩnh viễn đó để chặn escalate của LẦN TÁI DIỄN MỚI thì một ack duy nhất
        # khoá cả pattern mãi mãi. Trần = ACK_MAX_SUPPRESS_DAYS (cùng con số mà chính
        # ops_health_check dùng để không ack nào tắt dispatch vĩnh viễn).
        if (now - ts).days > ACK_MAX_SUPPRESS_DAYS:
            return "POST", (f"câu hỏi {ag}/{tp} có ack nhưng đã {(now - ts).days} ngày tuổi "
                            f"(> trần {ACK_MAX_SUPPRESS_DAYS}d) — ack không được khoá "
                            f"pattern vĩnh viễn, escalate lại")
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
