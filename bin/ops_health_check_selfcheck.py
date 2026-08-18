#!/usr/bin/env python3
"""Regression selfcheck cho check #5 (backlog câu hỏi) và check #10 (notify_thread.sh nuốt
tin nhắn) của bin/ops_health_check.sh.

TẠI SAO tồn tại: check #5 là kênh backlog `question` DUY NHẤT của fleet. Nó đã hỏng
IM LẶNG 2 lần liên tiếp và mỗi lần chỉ được phát hiện bằng mắt người:
  - answer chéo-agent không bao giờ đóng được question (match per-file, fix 2026-07-10);
  - kb_nightly Phase 1b2 (EVENT_KEEP_DAYS=30) archive event >30d sang
    bus/inbox/archive/*.jsonl.gz mà check chỉ glob hot inbox → cliff 30 ngày im lặng,
    2 câu hỏi CHƯA TỪNG được trả lời biến mất 38d/34d (fix 2026-07-31).
Ràng buộc "check #5 phải đọc CẢ archive theo layout Phase 1b2" trước đây chỉ được canh
bằng VĂN XUÔI trong runbook — đúng loại guard vừa thất bại suốt 38 ngày. File này biến nó
thành test đỏ được (arch-reviewer required_change #3, NEEDS_CHANGES coord-2026-07-31).

CÁCH LÀM: KHÔNG copy thuật toán (bản copy sẽ trôi khỏi bản thật). Trích ĐÚNG khối code
giữa 2 marker CHECK5_BEGIN/CHECK5_END trong bin/ops_health_check.sh rồi exec nó trên một
bus GIẢ trong tmpdir. Marker mất/đổi → test FAIL ngay, không im lặng.

Chạy: python3 bin/ops_health_check_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
Được cắm vào kb_nightly.sh Phase 0 (alert-only, không gate prune).
"""
import datetime as dt
import glob
import gzip
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Env override CHỈ để mutation-test (chứng minh test này đỏ được); prod luôn dùng file thật.
SRC = os.environ.get("OPS_HEALTH_CHECK_SRC") or os.path.join(ROOT, "bin", "ops_health_check.sh")
FAILS = []


def extract_block(tag):
    """Trích khối check thật giữa <TAG>_BEGIN … <TAG>_END trong ops_health_check.sh."""
    with open(SRC, encoding="utf-8") as f:
        src = f.read()
    m = re.search(rf"^# {tag}_BEGIN.*?\n(.*?)^# {tag}_END", src, re.S | re.M)
    if not m:
        raise SystemExit(
            f"FAIL: không tìm thấy marker {tag}_BEGIN/{tag}_END trong bin/ops_health_check.sh "
            "— ai đó đổi/xoá marker, selfcheck này không còn kiểm được code thật. "
            "Khôi phục marker hoặc cập nhật selfcheck."
        )
    return m.group(1)


CHECK5_SRC = extract_block("CHECK5")
CHECK10_SRC = extract_block("CHECK10")
CHECK11_SRC = extract_block("CHECK11")
CHECK12_SRC = extract_block("CHECK12")
ROUTING_SRC = extract_block("ROUTING")


def run_check5(wc_root, now=None):
    """Chạy khối thật trên 1 bus giả; trả về (lines, warn_count).

    `now` chỉ dành cho ca 8d: chèn CHECK5_NOW để ghim một thời điểm lịch cố định; production
    luôn chạy không có biến này nên hành vi không đổi.
    """
    old = os.environ.get("CHECK5_NOW")
    if now is not None:
        os.environ["CHECK5_NOW"] = now
    try:
        lines, warn = [], []

        def W(msg):
            warn.append(msg)
            lines.append(f"⚠️ {msg}")

        def OK(msg):
            lines.append(f"✅ {msg}")

        ns = {
            "glob": __import__("glob"), "gzip": gzip, "json": json, "os": os, "re": re,
            "wc_root": wc_root, "W": W, "OK": OK, "lines": lines,
        }
        exec(compile(CHECK5_SRC, SRC + ":CHECK5", "exec"), ns)
        return lines, warn
    finally:
        if now is not None:
            if old is None:
                os.environ.pop("CHECK5_NOW", None)
            else:
                os.environ["CHECK5_NOW"] = old


def write_events(path, events, gz=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
    if gz:
        with gzip.open(path, "wt", encoding="utf-8") as f:
            f.write(body)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)


def ago(days, hours=0):
    return (dt.datetime.now(dt.timezone.utc)
            - dt.timedelta(days=days, hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def ev(agent, etype, topic, ts, payload=None):
    return {"agent_id": agent, "event_type": etype, "topic": topic, "ts": ts,
            "payload": payload or {}, "event_id": f"{agent}-{etype}-{topic}"}


def mkbus():
    # KHÔNG tạo sẵn thư mục archive: nó chỉ nên tồn tại ở ca nào thật sự cần, nếu không
    # mọi ca đều dính WARN "archive rỗng" và ca 8 trở thành assertion vô nghĩa.
    d = tempfile.mkdtemp(prefix="ops_health_selfcheck_")
    inbox = os.path.join(d, "mike", "bus", "inbox")
    os.makedirs(inbox, exist_ok=True)
    return d, inbox


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def joined(lines):
    return "\n".join(lines)


# ── Ca 1 (ràng buộc ĐÃ GÃY 38 ngày): question >30d nằm trong archive theo ĐÚNG layout
#    kb_nightly Phase 1b2 (bus/inbox/archive/<agent>_<YYYY-MM>.jsonl.gz) VẪN phải hiện.
def case_archived_question_visible():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "archive", "Wendy_2026-06.jsonl.gz"),
                     [ev("Wendy", "question", "confirm-margin-thresholds", ago(38))], gz=True)
        write_events(os.path.join(inbox, "Mike.jsonl"), [ev("Mike", "status", "noise", ago(1))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("archive: question >30d trong archive gz VẪN hiện (cliff 30d đã bịt)",
              "confirm-margin-thresholds" in out and "38d" in out, out)
        check("archive: agent lấy đúng từ tên file có hậu tố tháng",
              "Wendy/confirm-margin-thresholds" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 2: answer ở HOT inbox (agent khác) đóng được question nằm trong ARCHIVE (chéo tầng
#    + chéo agent) → không được báo pending.
def case_cross_layer_resolve():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "archive", "Taylor_2026-06.jsonl.gz"),
                     [ev("Taylor", "question", "cache-stability-blocker", ago(35))], gz=True)
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "answer", "cache-stability-blocker [RESOLVED]", ago(2))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("resolve chéo tầng+chéo agent: answer hot inbox đóng question trong archive",
              "cache-stability-blocker" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 2b: quyết định ở topic khác đóng canonical question qua payload.resolves.
def case_explicit_cross_topic_resolve():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Taylor.jsonl"),
                     [ev("Taylor", "question", "cash-vendor-policy", ago(3))])
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "decision", "ops-backlog-batch", ago(1),
                         {"resolves": ["Taylor/cash-vendor-policy"],
                          "evidence": "commit abc"})])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("resolves explicit: decision topic khác đóng canonical Agent/topic",
              "cash-vendor-policy" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 3: resolver phát SINH TRƯỚC câu hỏi KHÔNG được đóng câu hỏi (điểm mù topic lặp,
#    vd plan-t1-not-ready-<ACCOUNT> — alert tiền thật).
def case_resolver_must_be_after():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Winston.jsonl"), [
            ev("Winston", "answer", "plan-t1-not-ready-SpaceX -question-closed", ago(10)),
            ev("Winston", "question", "plan-t1-not-ready-SpaceX", ago(3)),
        ])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("ts-order: answer CŨ hơn không pre-resolve alert lặp mới",
              "plan-t1-not-ready-SpaceX" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 4: cùng 1 event có ở CẢ hot lẫn archive (kb_nightly bị kill giữa chừng) → đếm 1 lần.
def case_dedupe_hot_and_archive():
    root, inbox = mkbus()
    try:
        e = ev("Taylor", "question", "dgc-zalopay-nav", ago(7))
        write_events(os.path.join(inbox, "Taylor.jsonl"), [e])
        write_events(os.path.join(inbox, "archive", "Taylor_2026-07.jsonl.gz"), [e], gz=True)
        lines, _ = run_check5(root)
        out = joined(lines)
        check("dedupe: event trùng hot+archive chỉ đếm 1 lần",
              out.count("dgc-zalopay-nav") == 1, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5 (required_change #1): zombie CŨ không được chèn escalation MỚI khỏi màn hình.
def case_no_crowd_out():
    root, inbox = mkbus()
    try:
        evs = [ev("Zombie", "question", f"zombie-{i}", ago(100 - i)) for i in range(12)]
        evs.append(ev("Zombie", "question", "dgc-zalopay-46-8-nav", ago(7)))
        write_events(os.path.join(inbox, "Zombie.jsonl"), evs)
        lines, _ = run_check5(root)
        out = joined(lines)
        check("crowd-out: escalation MỚI vẫn hiện khi pool có 13 mục",
              "dgc-zalopay-46-8-nav" in out, out)
        check("crowd-out: mục treo LÂU nhất vẫn hiện",
              "zombie-0" in out, out)
        check("crowd-out: có nói rõ bao nhiêu mục bị giấu",
              "mục giữa" in out, out)
        # Không in trùng, và số bị giấu phải khớp (13 mục − 5 cũ − 3 mới = 5 giữa).
        check("crowd-out: mục cũ nhất không bị in 2 lần (bẫy slice [-0:])",
              out.count("zombie-0") == 1, out)
        check("crowd-out: đếm số mục bị giấu đúng (13−5−3=5)",
              "…và 5 mục giữa…" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 6: pool nhỏ (≤10) thì in ĐỦ, không cắt gì.
def case_small_pool_prints_all():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "A.jsonl"),
                     [ev("A", "question", f"q-{i}", ago(10 + i)) for i in range(6)])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("pool nhỏ: in đủ 6/6 mục",
              all(f"q-{i}" in out for i in range(6)), out)
        check("pool nhỏ: không có WARN archive giả (bus không có thư mục archive)",
              "bus/inbox/archive" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7 (required_change #2): gz hỏng phải WARN, KHÔNG được nuốt im lặng.
def case_corrupt_gz_warns():
    root, inbox = mkbus()
    try:
        bad = os.path.join(inbox, "archive", "Wendy_2026-06.jsonl.gz")
        write_events(bad, [ev("Wendy", "question", "sẽ-mất", ago(40))], gz=True)
        with open(bad, "r+b") as f:      # cắt cụt → gzip đọc lỗi
            f.truncate(os.path.getsize(bad) // 2)
        write_events(os.path.join(inbox, "Mike.jsonl"), [ev("Mike", "status", "noise", ago(1))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("gz hỏng: có WARN nêu rõ file không đọc được (không im lặng)",
              "KHÔNG ĐỌC ĐƯỢC" in out and "Wendy_2026-06.jsonl.gz" in out, out)
        check("gz hỏng: WARN đó KHÔNG mang marker [WARN-ONLY] (là lỗi tooling, phải route Wags)",
              not any("KHÔNG ĐỌC ĐƯỢC" in ln and "[WARN-ONLY]" in ln for ln in lines), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8 (required_change #2): archive dir tồn tại nhưng glob khớp 0 file (đổi layout
#    Phase 1b2) → phải WARN, không lặng lẽ quay về cliff 30d.
def case_empty_archive_warns():
    root, inbox = mkbus()
    try:
        # layout "mới" giả định: .jsonl.zst thay vì .jsonl.gz
        write_events(os.path.join(inbox, "archive", "Wendy_2026-06.jsonl.zst"),
                     [ev("Wendy", "question", "khuất", ago(40))])
        write_events(os.path.join(inbox, "Mike.jsonl"), [ev("Mike", "status", "noise", ago(1))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("archive rỗng: WARN khi thư mục archive không có file *.jsonl.gz nào",
              "bus/inbox/archive" in out and "Phase 1b2" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8b (2026-08-17, sự cố coord-2026-08-17): question VỪA ĐĂNG vài phút KHÔNG được kéo
#    dispatch. Thật: Taylor đăng `hybrid-fill-live-deadline-20260817` 02:01:45Z, checker chạy
#    02:06:15Z thấy "chưa có answer" sau 4m31s → dispatch job Wags (Opus); Mike đăng answer
#    02:06:56Z. Ân hạn 60' cắt đúng lớp này. HAI chiều đều phải pin — chỉ pin chiều "không
#    dispatch" thì đổi ân hạn thành ∞ vẫn PASS mà kênh escalate chết im.
def case_grace_fresh_question_not_routable():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Taylor.jsonl"),
                     [ev("Taylor", "question", "hybrid-fill-live-deadline", ago(0, 0))])
        lines, _ = run_check5(root)
        out = joined(lines)
        routable = [ln for ln in lines
                    if "trong 48h qua CHƯA thấy answer" in ln and "[WARN-ONLY]" not in ln]
        check("ân hạn: question 0 phút tuổi KHÔNG vào dòng routable (không dispatch Wags)",
              not routable, out)
        check("ân hạn: vẫn HIỆN trong báo cáo với marker [WARN-ONLY] (không im lặng)",
              any("VỪA ĐĂNG" in ln and "[WARN-ONLY]" in ln
                  and "hybrid-fill-live-deadline" in ln for ln in lines), out)
        check("ân hạn: KHÔNG in ✅ 'không có câu hỏi nào đang chờ' khi vẫn còn câu hỏi mới",
              "Không có câu hỏi (question) nào đang chờ xử lý" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8c: quá ân hạn thì PHẢI routable trở lại — chiều ngược của ca 8b.
def case_grace_expired_question_is_routable():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Taylor.jsonl"),
                     [ev("Taylor", "question", "qua-an-han", ago(0, 3))])
        lines, _ = run_check5(root)
        out = joined(lines)
        routable = [ln for ln in lines
                    if "trong 48h qua CHƯA thấy answer" in ln and "[WARN-ONLY]" not in ln]
        check("ân hạn: question 3h tuổi VẪN routable (kênh escalate còn sống)",
              len(routable) == 1 and "qua-an-han" in routable[0], out)
        check("ân hạn: question 3h tuổi KHÔNG bị xếp vào dòng 'VỪA ĐĂNG'",
              not any("VỪA ĐĂNG" in ln for ln in lines), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8d (2026-08-17, round-2): ân hạn KHÔNG được mở rộng khe T6→T2. Cron thật là
#    `20 1 * * 1-5` + `45 5 * * 1-5`; khe hở lớn nhất T6 05:45Z→T2 01:20Z = 67h35 > cutoff
#    48h. HAI HƯỚNG đều phải pin:
#      - T5 còn lượt T6 01:20Z trước ts+48h ⇒ ân hạn giữ nguyên;
#      - T6 không còn lượt cron nào trước ts+48h ⇒ question 31' tuổi VẪN routable ngay.
def case_grace_schedule_aware_last_weekday_gap():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "question", "gap-t6-sang-t2",
                         "2026-08-14T05:14:00Z")])
        lines, _ = run_check5(root, now="2026-08-14T05:45:00Z")
        out = joined(lines)
        routable = [ln for ln in lines
                    if "trong 48h qua CHƯA thấy answer" in ln and "[WARN-ONLY]" not in ln]
        fresh = [ln for ln in lines if "VỪA ĐĂNG" in ln]
        check("8d gap T6→T2: question 31' tuổi VẪN routable nếu không còn lượt cron "
              "trước ts+48h",
              len(routable) == 1 and "gap-t6-sang-t2" in routable[0], out)
        check("8d gap T6→T2: KHÔNG rơi vào dòng VỪA ĐĂNG [WARN-ONLY]", not fresh, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "question", "con-an-hand-thu-5",
                         "2026-08-13T05:14:00Z")])
        lines, _ = run_check5(root, now="2026-08-13T05:45:00Z")
        out = joined(lines)
        routable = [ln for ln in lines
                    if "trong 48h qua CHƯA thấy answer" in ln and "[WARN-ONLY]" not in ln]
        fresh = [ln for ln in lines if "VỪA ĐĂNG" in ln]
        check("8d T5 còn lượt cron TRƯỚC ts+48h: ân hạn vẫn giữ nguyên",
              len(fresh) == 1 and "con-an-hand-thu-5" in fresh[0], out)
        check("8d T5 còn lượt cron: question chưa routable ngay",
              not any("con-an-hand-thu-5" in ln for ln in routable), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 9: question <48h nằm ở dòng "pending" (nhánh CÓ dispatch), không phải aged.
def case_fresh_question_is_pending():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "question", "coord-moi", ago(0, 5))])
        lines, _ = run_check5(root)
        pend = [ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln]
        check("phân tầng: question <48h vào dòng pending (routable, dispatch Wags)",
              len(pend) == 1 and "coord-moi" in pend[0], joined(lines))
        check("phân tầng: dòng pending KHÔNG mang [WARN-ONLY]",
              not any("[WARN-ONLY]" in p for p in pend), joined(lines))
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 10 (2026-07-31, audit kiến trúc fleet #14): câu hỏi do CHÍNH pipeline wags_autofix
#    sinh ra ở cuối vòng fix+arch-review, <48h, KHÔNG được re-trigger COORD_WARN — đây chính
#    là input của vòng lặp Wags coord-fix tự nuôi quan sát được thật hôm 07-31 (arch-reviewer
#    NEEDS_CHANGES → question → question đó tự nó lại là "câu hỏi tồn đọng" khiến
#    ops_health_check dispatch LẠI wags_autofix cho ĐÚNG issue vừa NEEDS_CHANGES). Câu hỏi
#    KHÁC (không phải của pipeline) vẫn phải routable như cũ — ca 9 ở trên đã khoá phần đó.
#
#    ⚠️ CHẠY CHO MỌI TIỀN TỐ trong WAGS_SELF_Q_PREFIXES, không chỉ tiền tố đầu tiên: bản
#    2026-07-31 chỉ pin "wags-fix-not-confirmed:" nên khi wags_autofix.sh tách thêm nhánh
#    "wags-arch-review-inconclusive:" (08-11, commit 35625a6f) mà quên cập nhật ops_health_check,
#    selfcheck VẪN xanh trong lúc production đã lặp vòng thật (question 08-11T05:57:50Z →
#    dispatch coord-2026-08-12 → INCONCLUSIVE → question coord-2026-08-12). Selfcheck chỉ pin
#    một mẫu đại diện thì không bắt được lớp lỗi "quên mở rộng danh sách".
WAGS_SELF_Q_PREFIXES = ("wags-fix-not-confirmed:", "wags-arch-review-inconclusive:")


def case_wagsfix_not_confirmed_is_warn_only():
    for prefix in WAGS_SELF_Q_PREFIXES:
        topic = f"{prefix} coord-2026-07-31"
        root, inbox = mkbus()
        try:
            write_events(os.path.join(inbox, "Wags.jsonl"),
                         [ev("Wags", "question", topic, ago(0, 3)),
                          ev("Wags", "question", "coord-that-su-moi", ago(0, 1))])
            lines, _ = run_check5(root)
            out = joined(lines)
            wagsfix_lines = [ln for ln in lines if "vòng wags-fix CHƯA CONFIRMED" in ln]
            pending_lines = [ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln]
            check(f"{prefix} <48h: có dòng riêng, mang [WARN-ONLY]",
                  len(wagsfix_lines) == 1 and "[WARN-ONLY]" in wagsfix_lines[0]
                  and topic in wagsfix_lines[0], out)
            check(f"{prefix} <48h: KHÔNG lẫn vào dòng pending routable",
                  not any(prefix in ln for ln in pending_lines), out)
            check(f"{prefix}: câu hỏi coordination KHÁC vẫn ở dòng pending routable",
                  len(pending_lines) == 1 and "coord-that-su-moi" in pending_lines[0], out)
            check(f"{prefix}: câu hỏi coordination khác đó KHÔNG mang [WARN-ONLY]",
                  not any("[WARN-ONLY]" in ln for ln in pending_lines), out)
        finally:
            shutil.rmtree(root, ignore_errors=True)


# ── Ca 10b (đối chứng ÂM, 2026-08-12): miễn trừ phải khớp TIỀN TỐ, không phải substring.
#    Một câu hỏi thật của người mà tình cờ NHẮC ĐẾN tiền tố ở GIỮA topic vẫn phải routable —
#    nếu không, ai đặt tên topic hơi giống là tự tắt mất đường escalate của mình.
def case_wagsfix_prefix_not_substring():
    for prefix in WAGS_SELF_Q_PREFIXES:
        topic = f"ai-đang-nợ {prefix} coord-2026-07-31 — cần người xem"
        root, inbox = mkbus()
        try:
            write_events(os.path.join(inbox, "Wags.jsonl"),
                         [ev("Wags", "question", topic, ago(0, 3))])
            lines, _ = run_check5(root)
            out = joined(lines)
            pending_lines = [ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln]
            wagsfix_lines = [ln for ln in lines if "vòng wags-fix CHƯA CONFIRMED" in ln]
            check(f"substring-ở-giữa '{prefix}': VẪN routable (không bị miễn trừ nhầm)",
                  len(pending_lines) == 1 and topic in pending_lines[0], out)
            check(f"substring-ở-giữa '{prefix}': KHÔNG rơi vào dòng WARN-ONLY wags-fix",
                  not wagsfix_lines, out)
        finally:
            shutil.rmtree(root, ignore_errors=True)


# ── Ca 11: chỉ có câu hỏi tự-sinh của pipeline (không có câu hỏi routable nào khác) — dòng
#    "Không có câu hỏi nào đang chờ" KHÔNG được in (sẽ nói dối — vẫn có 1 mục đang chờ,
#    chỉ là WARN-ONLY).
def case_wagsfix_only_no_false_ok():
    for prefix in WAGS_SELF_Q_PREFIXES:
        root, inbox = mkbus()
        try:
            write_events(os.path.join(inbox, "Wags.jsonl"),
                         [ev("Wags", "question", f"{prefix} coord-2026-07-31", ago(0, 3))])
            lines, _ = run_check5(root)
            out = joined(lines)
            check(f"chỉ có {prefix}: KHÔNG in 'Không có câu hỏi nào đang chờ' (sẽ nói dối)",
                  "Không có câu hỏi (question) nào đang chờ xử lý" not in out, out)
            check(f"chỉ có {prefix}: vẫn có dòng WARN-ONLY nêu rõ",
                  "vòng wags-fix CHƯA CONFIRMED" in out, out)
        finally:
            shutil.rmtree(root, ignore_errors=True)


# ── Ca 11b (2026-08-12): danh sách miễn trừ trong selfcheck phải KHỚP danh sách thật trong
#    bin/ops_health_check.sh. Đây là chốt chặn cuối cho lớp lỗi đã xảy ra: thêm nhánh question
#    mới vào wags_autofix.sh + ops_health_check.sh nhưng quên selfcheck (hoặc ngược lại) thì
#    ca 10/11 ở trên lặng lẽ kiểm thiếu. So sánh bằng cách đọc chính dòng khai báo.
def case_wagsfix_prefix_list_in_sync():
    with open(SRC, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"^WAGS_SELF_Q_PREFIXES = \(([^)]*)\)", src, re.M)
    check("ops_health_check.sh: tìm thấy khai báo WAGS_SELF_Q_PREFIXES", bool(m),
          "không thấy dòng WAGS_SELF_Q_PREFIXES = (...) — đã đổi tên biến?")
    if not m:
        return
    real = tuple(re.findall(r'"([^"]+)"', m.group(1)))
    check("danh sách tiền tố miễn trừ: selfcheck KHỚP ops_health_check.sh",
          real == WAGS_SELF_Q_PREFIXES,
          f"ops_health_check.sh={real} vs selfcheck={WAGS_SELF_Q_PREFIXES} — thêm tiền tố mới "
          f"phải cập nhật CẢ HAI")


# ── Check #10 (notify_thread.sh nuốt tin nhắn) ────────────────────────────────────────────
# Thêm 2026-08-02 vòng 5 (arch-reviewer MINOR-2): check #10 là logic MỚI, lúc commit chỉ được
# verify bằng 1 lần chạy tay. "Đọc code thấy hợp lý + chạy tay 1 lần" chính là loại guard đã
# thất bại 2 lần với check #5 — nên nó được đưa vào đúng khuôn extract-and-test này.
def run_check10(wc_root):
    lines, warn = [], []

    def W(msg):
        warn.append(msg)
        lines.append(f"⚠️ {msg}")

    def OK(msg):
        lines.append(f"✅ {msg}")

    ns = {"os": os, "re": re, "wc_root": wc_root, "W": W, "OK": OK, "lines": lines}
    exec(compile(CHECK10_SRC, SRC + ":CHECK10", "exec"), ns)
    return lines, warn


def _mklog(content, age_seconds=0):
    """Dựng wc_root giả có mike/logs/notify_thread_errors.log; content=None ⇒ không tạo file."""
    d = tempfile.mkdtemp(prefix="ops_health_check10_")
    if content is not None:
        logdir = os.path.join(d, "mike", "logs")
        os.makedirs(logdir, exist_ok=True)
        path = os.path.join(logdir, "notify_thread_errors.log")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        if age_seconds:
            old = dt.datetime.now().timestamp() - age_seconds
            os.utime(path, (old, old))
    return d


def case_c10_no_file_is_ok():
    root = _mklog(None)
    try:
        lines, warn = run_check10(root)
        check("check10: không có file log ⇒ OK, 0 WARN", not warn, joined(lines))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _nte_ts(hours_ago):
    """Timestamp bản ghi notify_thread, TƯƠNG ĐỐI với now.

    Ngày cứng trong fixture sẽ tự mốc: cửa sổ 24h của check #10 nay áp lên TỪNG bản ghi
    (sửa 2026-08-18), nên một fixture ghi "2026-08-16" sẽ tụt ra ngoài cửa sổ vài ngày sau
    khi viết và ca test lặng lẽ đổi nghĩa (coding_guidelines §23 hệ luận 1).
    """
    return (dt.datetime.now().astimezone() - dt.timedelta(hours=hours_ago)).isoformat(timespec="seconds")


def case_c10_fresh_log_warns():
    root = _mklog(f"{_nte_ts(1)} notify_thread: KHONG phan giai duoc topic foo\n"
                  "  ten hop le: architecture, trading_daily\n")
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: log tươi ⇒ WARN", len(warn) == 1, out)
        # Bản đầu lấy dòng cuối THÔ ⇒ in ra đúng cái đuôi "ten hop le: ..." vô nghĩa.
        check("check10: trích dòng CÓ timestamp, không phải dòng tràn",
              "KHONG phan giai duoc topic foo" in out and "Dòng cuối:   ten hop le" not in out, out)
        # MINOR-3: không có marker ⇒ dòng này kéo ops_autofix 4 lần/ngày cho sự cố đã sửa.
        check("check10: WARN mang marker [WARN-ONLY] (không kéo autofix)",
              "[WARN-ONLY]" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_c10_fresh_log_without_timestamp_line():
    # Log tươi nhưng KHÔNG có dòng nào khớp timestamp ⇒ IndexError; phải WARN, KHÔNG được ném
    # exception (ném là chết CẢ khối python ⇒ mất TOÀN BỘ báo cáo health-check).
    root = _mklog("dong rac khong co timestamp\n")
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: log không có dòng timestamp ⇒ vẫn WARN, không ném exception",
              len(warn) == 1 and "KHÔNG đọc được bản ghi nào có timestamp" in out, out)
        check("check10: không có dòng timestamp ⇒ KHÔNG khẳng định mất tin",
              "TIN NHẮN ĐÃ BỊ NUỐT" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca c10-swap (2026-08-16, arch-review coord-2026-08-12 required_change #3): file
#    notify_thread_errors.log chứa HAI loại bản ghi có hệ quả NGƯỢC nhau. "DA TU SUA VA GUI"
#    nghĩa là caller đảo thứ tự đối số nhưng tin ĐÃ ĐẾN nơi; gộp nó vào tiêu đề "TIN NHẮN ĐÃ
#    BỊ NUỐT" là nói với người rằng một tin đã giao là bị mất. "Sửa cả người ĐỌC, không chỉ
#    người GHI."
SWAP_LINE = (f'{_nte_ts(2)} notify_thread: DOI SO BI DAO (topic o vi tri 1, '
             'message o vi tri 2) — DA TU SUA VA GUI toi topic "architecture". '
             'SUA CALL SITE: dung `notify_thread.sh "<message>" <topic>`. caller=bin/foo.sh\n')
HARD_LINE = f"{_nte_ts(1)} notify_thread: KHONG phan giai duoc topic bar\n"


def case_c10_swap_recovery_is_not_swallowed():
    root = _mklog(SWAP_LINE)
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: CHỈ có bản ghi tự-sửa ⇒ KHÔNG nói 'TIN NHẮN ĐÃ BỊ NUỐT'",
              "TIN NHẮN ĐÃ BỊ NUỐT" not in out, out)
        check("check10: bản ghi tự-sửa vẫn WARN (call site còn sai) và nói rõ tin ĐÃ GỬI",
              len(warn) == 1 and "ĐÃ ĐƯỢC GỬI" in out, out)
        check("check10: bản ghi tự-sửa vẫn mang marker [WARN-ONLY]",
              "[WARN-ONLY]" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_c10_hard_error_wins_over_swap():
    # Lỗi THẬT lẫn với bản ghi tự-sửa: không được để bản ghi tự-sửa che mất lỗi thật.
    root = _mklog(SWAP_LINE + HARD_LINE)
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: có lỗi THẬT lẫn bản ghi tự-sửa ⇒ vẫn báo TIN NHẮN ĐÃ BỊ NUỐT",
              "TIN NHẮN ĐÃ BỊ NUỐT" in out, out)
        check("check10: trích đúng dòng lỗi THẬT, không phải dòng tự-sửa",
              "KHONG phan giai duoc topic bar" in out and "DA TU SUA VA GUI" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_c10_old_log_is_ok():
    root = _mklog("2026-07-01T10:00:00+07:00 notify_thread: loi cu\n", age_seconds=86400 + 3600)
    try:
        lines, warn = run_check10(root)
        check("check10: log cũ hơn 24h ⇒ OK (cảnh báo tự tắt)", not warn, joined(lines))
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca c10-window (2026-08-18, sự cố thật ops-health-SpaceX 02:58 ICT): file append-only
#    KHÔNG xoay vòng ⇒ mtime của FILE chỉ nói "vừa có ai ghi", không nói bản ghi NÀO mới.
#    Bản trước lọc cửa sổ 24h theo mtime rồi đọc TOÀN BỘ lịch sử: một dòng tự-sửa mới làm file
#    tươi, check lôi lỗi thật 6 ngày trước ra báo "TIN NHẮN ĐÃ BỊ NUỐT trong 24h qua" —
#    sai sự kiện, sai mốc thời gian, và che luôn kết luận đúng của bản ghi mới.
def case_c10_old_hard_error_not_reported_as_recent():
    root = _mklog("2026-08-12T18:46:56+07:00 notify_thread: KHONG phan giai duoc topic cu\n"
                  + SWAP_LINE)
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: lỗi THẬT cũ >24h + bản ghi tự-sửa mới ⇒ KHÔNG báo 'TIN NHẮN ĐÃ BỊ NUỐT'",
              "TIN NHẮN ĐÃ BỊ NUỐT" not in out, out)
        check("check10: bản ghi MỚI (tự-sửa) vẫn được báo đúng là tin ĐÃ GỬI",
              len(warn) == 1 and "ĐÃ ĐƯỢC GỬI" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_c10_fresh_file_all_records_old_is_ok():
    # File vừa được chạm (mtime tươi) nhưng MỌI bản ghi đều cũ hơn 24h ⇒ OK thật, KHÔNG được
    # rơi vào nhánh "không đọc được bản ghi nào có timestamp" (nhánh đó dành cho file rác).
    root = _mklog("2026-07-01T10:00:00+07:00 notify_thread: loi cu\n")
    try:
        lines, warn = run_check10(root)
        out = joined(lines)
        check("check10: file tươi nhưng mọi bản ghi đều cũ >24h ⇒ OK, 0 WARN", not warn, out)
        check("check10: ca đó KHÔNG bị nhầm sang nhánh 'không đọc được bản ghi'",
              "KHÔNG đọc được bản ghi nào có timestamp" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Khối DELIVER (giao báo cáo: Discord → Telegram dự phòng) ─────────────────────────────
# Thêm 2026-08-03 vòng 6 (arch-reviewer): check #10 phát hiện sự cố định tuyến, nhưng khâu GIAO
# của chính báo cáo chứa nó lại đi qua CÙNG registry đang hỏng ⇒ registry hỏng kéo dài thì
# không ai nhận được cảnh báo nào. Nhánh dự phòng Telegram vá chỗ đó; 2 ca dưới canh nó.
# Khối này là BASH (không phải python như check #5/#10) nên chạy bằng bash thật trên sandbox
# có stub `notify_thread.sh` / `notify_telegram.sh`, thay vì exec trong python.
def run_deliver(thread_rc, telegram_rc=0):
    """Chạy khối DELIVER thật với stub. Trả về (calls, log_content) — calls là danh sách tên
    script đã được gọi, theo thứ tự."""
    src = extract_block("DELIVER")
    d = tempfile.mkdtemp(prefix="ops_health_deliver_")
    bindir, logdir = os.path.join(d, "bin"), os.path.join(d, "logs")
    os.makedirs(bindir, exist_ok=True)
    os.makedirs(logdir, exist_ok=True)
    calls = os.path.join(d, "calls")
    for name, rc in (("notify_thread.sh", thread_rc), ("notify_telegram.sh", telegram_rc)):
        p = os.path.join(bindir, name)
        with open(p, "w", encoding="utf-8") as f:
            # CHỈ ghi TÊN, không ghi "$*": tin nhắn có nhiều dòng ⇒ ghi cả đối số thì mỗi dòng
            # thân tin thành 1 "lần gọi" giả khi đọc lại.
            f.write(f'#!/usr/bin/env bash\necho "{name}" >> "{calls}"\nexit {rc}\n')
        os.chmod(p, 0o755)
    # append_event.sh bị gọi ngay sau khối ⇒ không nằm trong DELIVER, không cần stub.
    script = ('set -uo pipefail\nROOT=%s\nMSG="bao cao test"\nTRADING_DAILY_THREAD=trading_daily\n'
              'ACCOUNT=SpaceX\nTODAY=2026-08-03\n' % json.dumps(d)) + src
    import subprocess
    subprocess.run(["bash", "-c", script], capture_output=True, timeout=30)
    got = []
    if os.path.exists(calls):
        with open(calls, encoding="utf-8") as f:
            got = [ln.split()[0] for ln in f if ln.strip()]
    logpath = os.path.join(logdir, "notify_thread_errors.log")
    log = open(logpath, encoding="utf-8").read() if os.path.exists(logpath) else ""
    shutil.rmtree(d, ignore_errors=True)
    return got, log


def case_deliver_discord_ok_no_telegram():
    calls, _ = run_deliver(thread_rc=0)
    # Gửi song song = nhân đôi mọi báo cáo 08:20/12:45. Dự phòng phải là DỰ PHÒNG.
    check("deliver: Discord OK ⇒ KHÔNG gửi Telegram (không nhân đôi tin)",
          calls == ["notify_thread.sh"], f"calls={calls}")


def case_deliver_discord_fails_falls_back_to_telegram():
    calls, _ = run_deliver(thread_rc=1)
    check("deliver: Discord lỗi (registry hỏng) ⇒ rơi sang Telegram",
          calls == ["notify_thread.sh", "notify_telegram.sh"], f"calls={calls}")


def case_deliver_both_fail_logs_for_check10():
    calls, log = run_deliver(thread_rc=1, telegram_rc=1)
    check("deliver: cả 2 đường chết ⇒ ghi notify_thread_errors.log (check #10 lượt sau tố cáo)",
          calls == ["notify_thread.sh", "notify_telegram.sh"] and "CA HAI duong bao" in log,
          f"calls={calls} log={log!r}")


# ── Ca 12 (Wags coord-2026-08-03): ack "triaged-needs-human:" tắt auto-dispatch nhưng
#    KHÔNG được đóng/giấu câu hỏi, và chỉ ăn khi ack ĐÚNG topic + đăng SAU câu hỏi.
def case_triaged_needs_human_ack():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "question", "can-nguoi-quyet", ago(0, 5)),
                      ev("Mike", "question", "chua-ai-xem", ago(0, 5)),
                      ev("Mike", "question", "ack-truoc-cau-hoi", ago(0, 2))])
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "status", "triaged-needs-human: can-nguoi-quyet", ago(0, 4)),
                      ev("Wags", "status", "triaged-needs-human: ack-truoc-cau-hoi", ago(0, 3))])
        lines, _ = run_check5(root)
        out = joined(lines)
        human_lines = [ln for ln in lines if "ĐÃ TRIAGE, chờ NGƯỜI quyết" in ln]
        pending_lines = [ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln]
        check("ack đúng: câu hỏi sang dòng riêng mang [WARN-ONLY] (không spawn wags_autofix)",
              len(human_lines) == 1 and "[WARN-ONLY]" in human_lines[0]
              and "can-nguoi-quyet" in human_lines[0], out)
        check("ack đúng: câu hỏi vẫn HIỆN trong báo cáo, không bị đóng/giấu",
              "can-nguoi-quyet" in out, out)
        check("ack đúng: câu hỏi đó KHÔNG còn ở dòng pending routable",
              not any("can-nguoi-quyet" in ln for ln in pending_lines), out)
        check("không có ack: câu hỏi vẫn routable như cũ (fail-closed)",
              len(pending_lines) == 1 and "chua-ai-xem" in pending_lines[0], out)
        check("ack đăng TRƯỚC câu hỏi: KHÔNG được tắt dispatch",
              "ack-truoc-cau-hoi" in pending_lines[0]
              and "ack-truoc-cau-hoi" not in human_lines[0], out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 13: chỉ có câu hỏi đã ack → KHÔNG được in "Không có câu hỏi nào đang chờ".
def case_triaged_only_no_false_ok():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "question", "can-nguoi-quyet", ago(0, 5))])
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "status", "triaged-needs-human: can-nguoi-quyet", ago(0, 4))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("chỉ có câu hỏi đã ack: KHÔNG in 'Không có câu hỏi nào đang chờ' (sẽ nói dối)",
              "Không có câu hỏi (question) nào đang chờ xử lý" not in out, out)
        check("chỉ có câu hỏi đã ack: vẫn có dòng WARN-ONLY nêu rõ",
              "ĐÃ TRIAGE, chờ NGƯỜI quyết" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 14 (Wags coord-2026-08-11): ack kèm `suppress_days` phủ CẢ lần cron phát lại cùng
#    topic; mọi đường lỗi/hết hạn phải rơi về hành vi cũ (vẫn routable = fail-closed).
def case_ack_suppress_days_window():
    root, inbox = mkbus()
    try:
        # 4 câu hỏi CÙNG phát lại 3h trước, mỗi cái 1 kiểu ack đăng TRƯỚC đó.
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "question", "tai-phat-co-window", ago(0, 3)),
                      ev("Mike", "question", "tai-phat-khong-window", ago(0, 3)),
                      ev("Mike", "question", "tai-phat-window-het-han", ago(0, 3)),
                      ev("Mike", "question", "tai-phat-window-rac", ago(0, 3))])
        def ack(topic, ago_ts, payload):
            e = ev("Wags", "status", f"triaged-needs-human: {topic}", ago_ts)
            e["payload"] = payload
            return e
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ack("tai-phat-co-window", ago(2), {"suppress_days": 7}),
                      ack("tai-phat-khong-window", ago(2), {}),
                      ack("tai-phat-window-het-han", ago(5), {"suppress_days": 1}),
                      ack("tai-phat-window-rac", ago(2), {"suppress_days": "bay-ngay"})])
        lines, _ = run_check5(root)
        out = joined(lines)
        human = joined([ln for ln in lines if "ĐÃ TRIAGE, chờ NGƯỜI quyết" in ln])
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("suppress_days=7: câu hỏi cron phát lại SAU ack vẫn được tắt dispatch",
              "tai-phat-co-window" in human and "tai-phat-co-window" not in pending, out)
        check("suppress_days=7: câu hỏi VẪN hiện trong báo cáo (không đóng/giấu)",
              "tai-phat-co-window" in out, out)
        check("không khai suppress_days: giữ nguyên hành vi cũ (vẫn routable)",
              "tai-phat-khong-window" in pending, out)
        check("suppress_days đã hết hạn: quay lại routable, ack không vĩnh viễn",
              "tai-phat-window-het-han" in pending, out)
        check("suppress_days không phải số: fail-closed về cửa sổ 0 (vẫn routable)",
              "tai-phat-window-rac" in pending, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15b (2026-08-14, job Wags_20260814_050746): câu hỏi TỔNG khai `rollup_of`.
#    Ca thật: Mike/retro-escalation-2026-08-13-patternB-and-backlog — 2 câu hỏi con được đóng
#    bằng `decision` trong cùng 1 giây, topic tổng không có event đóng riêng ⇒ đốt 1 job
#    wags_autofix. Pin CẢ 5 nhánh, trong đó 3 nhánh fail-closed và 1 RED control (đóng thiếu
#    1 con thì KHÔNG được đóng tổng — đây mới là nhánh nguy hiểm nếu code nới tay thành any()).
def case_rollup_of_umbrella_question():
    root, inbox = mkbus()
    try:
        q_ts = ago(0, 6)
        def umbrella(topic, subs):
            e = ev("Mike", "question", topic, q_ts)
            if subs is not None:
                e["payload"] = {"rollup_of": subs}
            return e
        write_events(os.path.join(inbox, "Mike.jsonl"), [
            umbrella("tong-du-2-con", ["con-a", "con-b"]),
            umbrella("tong-thieu-1-con", ["con-a", "con-chua-dong"]),
            umbrella("tong-khong-khai", None),
            umbrella("tong-rollup-rong", []),
            umbrella("tong-rollup-sai-kieu", "con-a"),
            # Dạng "Agent/topic" (người copy thẳng chuỗi checker in ra) vẫn phải khớp — NHƯNG
            # phải là ĐÚNG agent sở hữu câu hỏi con. Bản đầu của ca này viết "Winston/con-b"
            # cho câu hỏi `Mike/con-b` và assert nó KHỚP: tức chính là hành vi false-CLOSED
            # chéo agent mà arch-review round 3 bắt được, bị đóng đinh thành assertion. Sửa
            # về đúng agent, và thêm ca dưới để khoá chiều sai lại.
            umbrella("tong-dang-agent-slash", ["Mike/con-b"]),
            umbrella("tong-dang-agent-SAI", ["Winston/con-b"]),
            # Con đã đóng TRƯỚC khi escalation tổng được mở ⇒ không được tính là đã quyết
            # (giữ đúng ràng buộc thời gian của _resolved: escalation mở lại là chuyện mới).
            umbrella("tong-con-dong-truoc-khi-hoi", ["con-dong-som"]),
            ev("Mike", "question", "con-a", ago(1)),
            ev("Mike", "question", "con-b", ago(1)),
            ev("Mike", "question", "con-chua-dong", ago(1)),
            ev("Mike", "question", "con-dong-som", ago(2)),
        ])
        write_events(os.path.join(inbox, "Wags.jsonl"), [
            ev("Wags", "decision", "con-a", ago(0, 1)),
            ev("Wags", "decision", "con-b", ago(0, 1)),
            ev("Wags", "decision", "con-dong-som", ago(1, 12)),
        ])
        lines, _ = run_check5(root)
        out = joined(lines)
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("rollup_of: mọi câu hỏi con đã có decision ⇒ câu hỏi TỔNG tự đóng",
              "tong-du-2-con" not in out, out)
        check("rollup_of RED CONTROL: thiếu 1 con chưa đóng ⇒ TỔNG vẫn pending (all, không any)",
              "tong-thieu-1-con" in pending, out)
        check("rollup_of: dạng 'Agent/topic' ĐÚNG agent vẫn khớp được con",
              "tong-dang-agent-slash" not in out, out)
        check("rollup_of: dạng 'Agent/topic' SAI agent (Winston/con-b cho câu hỏi Mike/con-b) "
              "⇒ KHÔNG khớp — lời khai agent phải được tôn trọng, không phải trang trí",
              "tong-dang-agent-SAI" in pending, out)
        check("rollup_of: con đóng TRƯỚC khi tổng được hỏi ⇒ KHÔNG đóng tổng (giữ ràng buộc ts)",
              "tong-con-dong-truoc-khi-hoi" in pending, out)
        for t in ("tong-khong-khai", "tong-rollup-rong", "tong-rollup-sai-kieu"):
            check(f"rollup_of fail-closed: {t} ⇒ giữ nguyên hành vi cũ (vẫn routable)",
                  t in pending, out)
        check("rollup_of: các câu hỏi CON vẫn tự đóng như cũ (không hồi quy)",
              "con-a" not in pending and "con-b" not in pending, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15c (2026-08-16, job Wags_20260816_090511): HAI lỗ của `rollup_of` khi topic con khớp
#    SUBSTRING. arch-review coord-2026-08-14 (killer_objection) tái lập được cả hai trong
#    sandbox; 8 assertion của ca 15b PASS ở CẢ bản lỏng lẫn bản chặt nên đang mù chiều này.
#    Lỗ 1 — MỘT resolver thoả NHIỀU topic con: `all()` không còn nghĩa là "mọi con đã quyết".
#    Lỗ 2 — topic con viết CẮT CỤT/tiền tố: khớp bừa vào resolver của câu hỏi con KHÁC.
#    Cả hai đều đóng oan escalation của USER, đúng thứ `_acked` đã chọn exact để tránh.
#    RED CONTROL: đổi `_resolved_exact` → `_resolved` trong ops_health_check.sh làm 2
#    assertion dưới đây đỏ (đã chạy thật), tức chúng khoá đúng chiều hồi quy.
def case_rollup_of_substring_holes():
    root, inbox = mkbus()
    try:
        q_ts = ago(0, 6)
        def umbrella(topic, subs):
            e = ev("Mike", "question", topic, q_ts)
            e["payload"] = {"rollup_of": subs}
            return e
        resolves_ev = ev("Wags", "decision", "quyet-gop-2-viec", ago(0, 1))
        resolves_ev["payload"] = {"resolves": ["con-x", "con-y"]}
        write_events(os.path.join(inbox, "Mike.jsonl"), [
            # Lỗ 1: 2 con, nhưng chỉ có ĐÚNG 1 decision với topic dài chứa cả 2 chuỗi con.
            umbrella("tong-mot-resolver-nuot-hai-con", ["patternB", "backlog"]),
            # Lỗ 2: topic con viết cắt cụt; resolver thật chỉ đóng câu hỏi con DÀI hơn.
            umbrella("tong-topic-con-cat-cut", ["retro-pattern-recurring"]),
            ev("Mike", "question", "retro-pattern-recurring-wakeup-miss", ago(1)),
            # Đường ĐÓNG HỢP LỆ bằng 1 event: decision khai TƯỜNG MINH `resolves` từng con.
            # Phải giữ được sau khi siết exact, nếu không cơ chế rollup thành vô dụng.
            umbrella("tong-dong-bang-resolves-tuong-minh", ["con-x", "con-y"]),
        ])
        write_events(os.path.join(inbox, "Wags.jsonl"), [
            ev("Wags", "decision", "retro-patternB-and-backlog-summary", ago(0, 1)),
            ev("Wags", "decision", "retro-pattern-recurring-wakeup-miss", ago(0, 1)),
            resolves_ev,
        ])
        lines, _ = run_check5(root)
        out = joined(lines)
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("rollup_of: MỘT resolver KHÔNG được thoả nhiều topic con (khớp exact, không substring)",
              "tong-mot-resolver-nuot-hai-con" in pending, out)
        check("rollup_of: topic con CẮT CỤT/tiền tố KHÔNG khớp resolver của câu hỏi con khác",
              "tong-topic-con-cat-cut" in pending, out)
        check("rollup_of: `resolves` khai tường minh vẫn đóng được tổng bằng 1 event (không thắt chết cơ chế)",
              "tong-dong-bang-resolves-tuong-minh" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15e (2026-08-16, arch-review d65167a9): HAI kiểu đóng con hợp lệ mà bản exact đầu tiên
#    KHÔNG phân biệt được. Mọi assertion 15b/15c đều dùng resolver TRÙNG KHÍT hoặc `resolves`
#    dạng TRẦN, nên chiều "trần ↔ Agent/topic" hoàn toàn không được phủ.
#    (a) PHẢI ĐÓNG: con đóng bằng decision gộp khai resolves=["Mike/con-B"] (đúng khuôn
#        bin/close_bus_question.py) trong khi rollup_of viết dạng trần ["con-B"]. Trước
#        `_same_ref`, `q_topic in explicit` so nguyên chuỗi ⇒ không khớp ⇒ tổng kẹt VĨNH VIỄN.
#    (b) PHẢI PENDING (pin CÓ CHỦ ĐÍCH, không phải bug): con chỉ đóng bằng quy ước hậu-tố
#        trạng thái ("<topic>-question-closed"). `_resolved` bản chính chấp nhận kiểu này qua
#        nhánh substring, nhưng với rollup thì KHÔNG — vì chính nhánh substring đó là thứ cho
#        MỘT resolver nuốt nhiều topic con (lỗ 1 của ca 15c). Đổi lại, tổng phải tự đăng
#        `answer` giữ nguyên topic tổng — đã ghi vào MIKE.md § Escalation TỔNG.
#        Hướng lỗi ở đây là false-PENDING (tốn 1 job wags_autofix), an toàn hơn hẳn
#        false-CLOSED (nuốt quyết định của user) — đó là lý do chọn pin thay vì nới.
#    RED CONTROL: bỏ `_same_ref` (quay lại `q_topic in explicit`) ⇒ assertion (a) đỏ.
def case_rollup_of_ref_forms():
    root, inbox = mkbus()
    try:
        q_ts = ago(0, 6)
        def umbrella(topic, subs):
            e = ev("Mike", "question", topic, q_ts)
            e["payload"] = {"rollup_of": subs}
            return e
        # (a) rollup_of TRẦN, resolves QUALIFIED — hai dạng phải gặp được nhau.
        gop = ev("Wags", "decision", "quyet-gop-qualified", ago(0, 1))
        gop["payload"] = {"resolves": ["Mike/con-qual-1", "Mike/con-qual-2"]}
        # Chiều ngược lại: rollup_of QUALIFIED, resolves TRẦN.
        gop2 = ev("Wags", "decision", "quyet-gop-tran", ago(0, 1))
        gop2["payload"] = {"resolves": ["con-nguoc-1"]}
        # ĐỐI CHỨNG false-CLOSED: cùng tên con nhưng KHÁC agent ⇒ TUYỆT ĐỐI không được khớp.
        gop3 = ev("Wags", "decision", "quyet-gop-khac-agent", ago(0, 1))
        gop3["payload"] = {"resolves": ["Taylor/con-khac-agent"]}
        write_events(os.path.join(inbox, "Mike.jsonl"), [
            umbrella("tong-tran-vs-qualified", ["con-qual-1", "con-qual-2"]),
            umbrella("tong-qualified-vs-tran", ["Mike/con-nguoc-1"]),
            umbrella("tong-khac-agent-khong-duoc-khop", ["Mike/con-khac-agent"]),
            # (b) con CHỈ đóng bằng hậu-tố trạng thái.
            umbrella("tong-con-dong-kieu-hau-to", ["con-hau-to"]),
            ev("Mike", "question", "con-hau-to", ago(1)),
        ])
        write_events(os.path.join(inbox, "Wags.jsonl"), [
            gop, gop2, gop3,
            ev("Wags", "decision", "con-hau-to-question-closed", ago(0, 1)),
        ])
        lines, _ = run_check5(root)
        out = joined(lines)
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("rollup_of TRẦN + resolves 'Agent/topic' ⇒ tổng PHẢI tự đóng",
              "tong-tran-vs-qualified" not in out, out)
        check("rollup_of 'Agent/topic' + resolves TRẦN ⇒ tổng PHẢI tự đóng (đối xứng 2 chiều)",
              "tong-qualified-vs-tran" not in out, out)
        check("ĐỐI CHỨNG false-CLOSED: 'Mike/con' KHÔNG được khớp 'Taylor/con' (khác agent)",
              "tong-khac-agent-khong-duoc-khop" in pending, out)
        check("PIN có chủ đích: con đóng kiểu hậu-tố trạng thái ⇒ tổng VẪN pending "
              "(rollup không nhận substring; xem MIKE.md § Escalation TỔNG)",
              "tong-con-dong-kieu-hau-to" in pending, out)
        check("ĐỐI CHỨNG: chính câu hỏi CON đó vẫn tự đóng như cũ (không hồi quy _resolved)",
              "con-hau-to" not in pending.replace("tong-con-dong-kieu-hau-to", ""), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15f (2026-08-16, arch-review round 3): tiêu chí "đã ở dạng Agent/topic" của `_same_ref`
#    bản đầu là `"/" in s` — SAI CẢ HAI CHIỀU, reviewer tái lập được cả hai:
#    (a) FALSE-PENDING: topic TỰ NÓ chứa '/' (`selfcheck-red: mike/bin/x.py` — lớp câu hỏi
#        ĐÔNG NHẤT trong backlog thật) bị tưởng là đã qualified ⇒ không bao giờ ghép được với
#        dạng còn lại ⇒ rollup kẹt vĩnh viễn, đốt 1 job wags_autofix/ngày.
#    (b) FALSE-CLOSED chéo agent: sub TRẦN + resolves của agent KHÁC khớp nhau vì chỉ MỘT bên
#        có '/'. Ca 15e cũ chỉ pin biến thể "cả hai bên qualified" nên mù hoàn toàn với ca này.
#    Fix: `_split_ref` chỉ bóc tiền tố khi nó là agent-id CÓ THẬT (known_agents, lấy từ tên
#    file inbox), bên còn lại lấy agent NGỮ CẢNH, rồi so CẢ CẶP (agent, topic).
#    RED CONTROL: quay `_split_ref` về `if "/" in s: return s.split("/",1)` ⇒ (a) và (b) đỏ.
def case_rollup_of_ref_forms_agent_aware():
    root, inbox = mkbus()
    try:
        q_ts = ago(0, 6)
        # Topic THẬT đang pending trên bus (không phải chuỗi bịa): chúng chứa '/' ở giữa.
        # HAI topic khác nhau cho (a) và (a'): dùng CHUNG một chuỗi thì resolver của ca này
        # đóng luôn ca kia, và mutation "quay về tiêu chí `\"/\" in s`" chỉ làm đỏ 1 trong 2
        # (đã đo) — tức một assertion xanh nhờ đường không thuộc phạm vi nó đang đo.
        real = "selfcheck-red: mike/bin/job_cancel_guard_selfcheck.py"
        real_b = "selfcheck-red: mike/bin/plan_cash_commitment_selfcheck.py"

        def umbrella(topic, subs):
            e = ev("Mike", "question", topic, q_ts)
            e["payload"] = {"rollup_of": subs}
            return e

        # LƯU Ý cách dựng: agent của một resolver lấy từ TÊN FILE (`_agent_of`), không phải
        # field agent_id — nên quyết định của Taylor phải nằm trong Taylor.jsonl mới đúng ca.
        # `known_agents` cũng lấy từ tên file inbox: {Mike, Taylor, Wags}.
        write_events(os.path.join(inbox, "Mike.jsonl"), [
            # (a) sub TRẦN, đóng bằng resolves QUALIFIED — trên topic tự chứa '/'.
            umbrella("tong-topic-co-dau-gach", [real]),
            # (b) sub TRẦN của Mike, chỉ có quyết định của TAYLOR ⇒ phải Ở LẠI pending.
            umbrella("tong-cheo-agent-sub-tran", ["con-cheo"]),
            # (c) con ĐÃ đóng thật, nhưng danh sách có phần tử rỗng ⇒ fail-closed cả tổng.
            umbrella("tong-co-phan-tu-rong", ["con-that", ""]),
            # (c') ĐỐI CHỨNG cho (c): y hệt nhưng KHÔNG có phần tử rỗng ⇒ phải đóng. Không
            #      có dòng này thì (c) xanh cả khi `con-that` đơn giản là không khớp được.
            umbrella("tong-khong-co-phan-tu-rong", ["con-that"]),
            ev("Mike", "question", "con-that", ago(1)),
            ev("Mike", "decision", "con-that", ago(0, 1)),
        ])
        write_events(os.path.join(inbox, "Wags.jsonl"), [
            ev("Wags", "decision", "quyet-gop-1", ago(0, 1), {"resolves": [f"Mike/{real}"]}),
            # (a') chiều ngược: sub QUALIFIED, đóng bằng resolver topic TRẦN cùng agent.
            ev("Wags", "question", "tong-cua-wags-sub-tran", q_ts,
               {"rollup_of": [f"Wags/{real_b}"]}),
            ev("Wags", "decision", real_b, ago(0, 1)),
        ])
        write_events(os.path.join(inbox, "Taylor.jsonl"), [
            ev("Taylor", "decision", "quyet-cua-taylor", ago(0, 1),
               {"resolves": ["Taylor/con-cheo"]}),
        ])
        lines, _ = run_check5(root)
        out = joined(lines)
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("(a) topic con TỰ CHỨA '/' + resolves qualified ⇒ tổng PHẢI tự đóng "
              "(trước fix: kẹt pending vĩnh viễn — lớp câu hỏi đông nhất trên bus thật)",
              "tong-topic-co-dau-gach" not in pending, out)
        check("(a') chiều ngược: sub có '/' + resolves TRẦN cùng agent ⇒ cũng PHẢI đóng",
              "tong-cua-wags-sub-tran" not in pending, out)
        check("(b) FALSE-CLOSED chéo agent: sub TRẦN của Mike KHÔNG được đóng bằng "
              "resolves ['Taylor/con-cheo'] — hướng lỗi nguy hiểm nhất",
              "tong-cheo-agent-sub-tran" in pending, out)
        check("phần tử RỖNG trong rollup_of ⇒ fail-closed CẢ tổng, không lọc lặng rồi "
              "all() trên ít con hơn số đã khai",
              "tong-co-phan-tu-rong" in pending, out)
        check("ĐỐI CHỨNG cho ca trên: cùng danh sách nhưng KHÔNG có phần tử rỗng ⇒ đóng "
              "bình thường (chứng minh (c) đỏ vì phần tử rỗng, không phải vì con không khớp)",
              "tong-khong-co-phan-tu-rong" not in pending, out)
        check("DIAGNOSTIC: tổng không đóng được thì in ra CON NÀO chưa khớp (fail-closed "
              "đúng nhưng câm thì người đăng không sửa được)",
              "topic con CHƯA khớp" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15d (2026-08-16): wc_root SAI ⇒ bus/inbox không tồn tại. Trước fix, mọi danh sách rỗng
#    ⇒ check in ✅ "không có câu hỏi" — im lặng hoá TOÀN BỘ kênh backlog. arch-reviewer vấp
#    phải khi audit coord-2026-08-14 (check fail_silent, đề nghị mở ticket riêng).
def case_missing_inbox_dir_is_warn_not_green():
    root = tempfile.mkdtemp(prefix="ops_health_selfcheck_noinbox_")
    try:
        lines, warn = run_check5(root)   # KHÔNG tạo mike/bus/inbox
        out = joined(lines)
        check("inbox_dir không tồn tại ⇒ WARN, KHÔNG in ✅ '0 câu hỏi'",
              "Không có câu hỏi (question) nào đang chờ xử lý" not in out, out)
        check("inbox_dir không tồn tại ⇒ nói rõ KHÔNG kiểm tra được (khác hẳn 'không có')",
              any("KHÔNG tìm thấy thư mục bus/inbox" in w for w in warn), out)
        check("inbox_dir không tồn tại CONTROL: không dòng ✅ nào của check #5",
              "✅" not in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 15: trần ACK_MAX_SUPPRESS_DAYS — ack không được tắt dispatch quá hạn trần.
def case_ack_suppress_days_capped():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Mike.jsonl"),
                     [ev("Mike", "question", "window-vo-han", ago(0, 3))])
        e = ev("Wags", "status", "triaged-needs-human: window-vo-han", ago(20))
        e["payload"] = {"suppress_days": 9999}
        write_events(os.path.join(inbox, "Wags.jsonl"), [e])
        lines, _ = run_check5(root)
        out = joined(lines)
        pending = joined([ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln])
        check("suppress_days khổng lồ bị cắt trần: ack 20 ngày trước KHÔNG còn tắt dispatch",
              "window-vo-han" in pending, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 16 (2026-08-14, job Wags_20260814_050658): lớp vòng-wags-fix MIỄN CẮT trong aged_q.
#    Vì sao cần: lớp này đã bị loại khỏi auto-dispatch (đúng — lặp tự động là vòng tự nuôi),
#    nên dòng aged_q là kênh DUY NHẤT đưa nó tới người; mà nó lão hoá theo ngày ⇒ càng treo
#    lâu càng trôi vào ĐÚNG vùng bị cắt giữa.
#    ⚠️ Ghi cho đúng lịch sử: nhánh cắt-giữa CHƯA TỪNG chạy trong production tính đến hôm nay
#    (grep "mục giữa" logs/ops_health.log = 0; nhiều nhất từng thấy 9 mục ≤ 10) — 4 mục
#    wags-fix treo lâu hôm nay ĐỀU đã được in đủ. Đây là bịt lỗ TRƯỚC khi nó cắn, không phải
#    tái lập sự cố đã xảy ra. Nhưng nó SẮP cắn: fixture dưới là 20 câu hỏi pending THẬT của
#    bus lúc 2026-08-14 (bin/bus_question_audit.py), tuổi +2 ngày = trạng thái NGÀY MAI khi
#    cả 20 đều qua mốc 48h ⇒ aged_q=20 > AGED_SHOW_ALL_UPTO, nhánh cắt chạy lần đầu tiên và
#    12/20 mục rơi vào vùng "…mục giữa…". RED control (chứng minh ca này đỏ được, chạy tay):
#      OPS_HEALTH_CHECK_SRC=<file ops_health_check.sh bản HEAD cũ> python3 <selfcheck này>
_AGED_REAL_BOARD_20260814 = [
    # (agent, topic, tuổi ngày) — bảng pending THẬT + 2 ngày, thứ tự cũ → mới
    ("Taylor", "cron-cho-buoc-gop-park-merge-CAN-USER-QUYET", 5),
    ("Mike", "paper-checkpoint-overdue-fill_timing", 4),
    ("Wags", "wags-arch-review-inconclusive: coord-2026-08-12", 4),          # wags-class
    ("Winston", "plan-dd-check-string-gay-poll-fail-moi-fill", 4),
    ("Winston", "ops-autofix-unresolved: ops-health-ZaloPay", 4),
    ("Taylor", "can-user-quyet-mo-cong-CASH_VENDOR-va-kiem-freshness", 3),
    # 9 câu hỏi selfcheck-red: Wags là TÁC GIẢ nhưng topic KHÔNG thuộc WAGS_SELF_Q_PREFIXES
    # ⇒ phải ở nhóm "còn lại", chịu cắt như thường (miễn trừ theo TIỀN TỐ TOPIC, không theo
    # agent_id). Chính 9 mục này là thứ đẩy backlog vượt 10 trong vòng 1 ngày.
    ("Wags", "selfcheck-red: extreme_regime_selfcheck.py", 3),
    ("Wags", "selfcheck-red: hard_no_chase_ceiling_selfcheck.py", 3),
    ("Wags", "selfcheck-red: lag_live_schedule_selfcheck.py", 3),
    ("Wags", "selfcheck-red: mike/bin/exrights_price_basis_selfcheck.py", 3),
    ("Wags", "selfcheck-red: mike/bin/send_plan_report_park_jit_selfcheck.py", 3),
    ("Wags", "selfcheck-red: mike/bin/universe_pit_quality_selfcheck.py", 3),
    ("Wags", "selfcheck-red: paper_main_window_selfcheck.py", 3),
    ("Wags", "selfcheck-red: plan_cash_commitment_selfcheck.py", 3),
    ("Wags", "selfcheck-red: t2_settlement_selfcheck.py", 3),
    ("Wags", "wags-fix-not-confirmed: coord-2026-08-12", 3),                 # wags-class ← bị nuốt
    ("Wags", "selfcheck-red: mike/bin/job_cancel_guard_selfcheck.py", 3),
    ("Wags", "wags-arch-review-inconclusive: coord-2026-08-13", 3),          # wags-class
    ("Mike", "retro-escalation-2026-08-13-patternB-and-backlog", 2),
    ("Wags", "wags-fix-not-confirmed: coord-2026-08-13", 2),                 # wags-class
]


def _write_board(inbox, board):
    by_agent = {}
    for agent, topic, age in board:
        by_agent.setdefault(agent, []).append(ev(agent, "question", topic, ago(age)))
    for agent, evs in by_agent.items():
        write_events(os.path.join(inbox, f"{agent}.jsonl"), evs)


def case_aged_wagsfix_never_truncated():
    root, inbox = mkbus()
    try:
        _write_board(inbox, _AGED_REAL_BOARD_20260814)
        lines, _ = run_check5(root)
        aged = joined([ln for ln in lines if "TREO LÂU" in ln])
        check("aged: bảng THẬT 20 mục ⇒ vào nhánh CẮT (không phải nhánh in-đủ ≤10)",
              "20 mục" in aged and "VÒNG WAGS-FIX" in aged, aged)
        # Điều kiện làm ca này CÓ NGHĨA: nhóm "còn lại" thật sự bị cắt. Nếu không cắt thì
        # mọi assertion "wags vẫn hiện" dưới đây đều đúng một cách vô nghĩa.
        check("aged: nhóm CÒN LẠI vẫn bị cắt giữa (miễn trừ chỉ áp cho lớp wags)",
              "mục giữa" in aged, aged)
        for _a, topic, _d in _AGED_REAL_BOARD_20260814:
            if topic.startswith(WAGS_SELF_Q_PREFIXES):
                check(f"aged MIỄN CẮT: '{topic}' vẫn hiện dù nằm giữa danh sách",
                      topic in aged, aged)
        check("aged: 5 mục cũ nhất vẫn hiện (không hồi quy)",
              all(t in aged for _a, t, _d in _AGED_REAL_BOARD_20260814[:5]), aged)
        check("aged: mục MỚI nhất vẫn hiện (chống crowd-out — lý do sinh ra cắt-giữa)",
              "retro-escalation-2026-08-13-patternB-and-backlog" in aged, aged)
        check("aged: 16 mục KHÔNG thuộc tiền tố (gồm 10 selfcheck-red do Wags viết) nằm ở "
              "nhóm CÒN LẠI — miễn trừ theo TIỀN TỐ TOPIC, không theo agent_id",
              "16 mục còn lại" in aged, aged)
        check("aged: mỗi mục chỉ in 1 lần (không trùng giữa 2 nhóm)",
              all(aged.count(t) <= 1 for _a, t, _d in _AGED_REAL_BOARD_20260814), aged)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_aged_no_wagsfix_keeps_old_cut():
    # Backlog dài mà KHÔNG có mục wags-class ⇒ hành vi phải y hệt trước (cắt giữa).
    root, inbox = mkbus()
    try:
        evs = [ev("Zombie", "question", f"zombie-{i}", ago(100 - i)) for i in range(12)]
        write_events(os.path.join(inbox, "Zombie.jsonl"), evs)
        lines, _ = run_check5(root)
        aged = joined([ln for ln in lines if "TREO LÂU" in ln])
        check("aged: không có mục wags ⇒ giữ NGUYÊN dòng cắt-giữa cũ (không nhắc VÒNG WAGS-FIX)",
              "VÒNG WAGS-FIX" not in aged and "…và 4 mục giữa…" in aged, aged)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_aged_wagsfix_overflow_is_loud():
    # Miễn trừ không được biến thành đường crowd-out mới: quá trần thì CẮT nhưng NÓI RA.
    root, inbox = mkbus()
    try:
        evs = [ev("Wags", "question", f"wags-fix-not-confirmed: coord-{i:03d}", ago(60 - i))
               for i in range(25)]
        write_events(os.path.join(inbox, "Wags.jsonl"), evs)
        evs2 = [ev("Mike", "question", f"khac-{i}", ago(3)) for i in range(3)]
        write_events(os.path.join(inbox, "Mike.jsonl"), evs2)
        lines, _ = run_check5(root)
        aged = joined([ln for ln in lines if "TREO LÂU" in ln])
        check("aged: 25 mục wags ⇒ cắt ở trần AGED_WAGS_MAX=20", "(20 mục, MIỄN CẮT" in aged, aged)
        check("aged: cắt trần phải NÓI RA số bị cắt (không bao giờ cắt im lặng)",
              "đã cắt 5 mục wags vượt trần 20" in aged, aged)
        check("aged: mục KHÁC vẫn hiện dù nhóm wags dài", "khac-0" in aged, aged)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Check #11 (quét selfcheck production: freshness + ca đỏ) ──────────────────────────────
# Thêm 2026-08-12 (job Wags_20260812_112724). Check #11 KHÔNG chạy lại 92 selfcheck, nó chỉ đọc
# artifact — nên toàn bộ giá trị nằm ở 5 nhánh phân loại. Cả 5 chạy THẬT trên artifact giả ở
# đây, gồm 2 nhánh im-lặng-nguy-hiểm (thiếu artifact / artifact hỏng).
def run_check11(wc_root):
    lines, warn = [], []

    def W(msg):
        warn.append(msg)
        lines.append(f"⚠️ {msg}")

    def OK(msg):
        lines.append(f"✅ {msg}")

    ns = {"os": os, "re": re, "json": json, "dt": dt, "glob": glob, "wc_root": wc_root,
          "W": W, "OK": OK, "lines": lines, "WARN_ONLY": "[WARN-ONLY]"}
    exec(compile(CHECK11_SRC, SRC + ":CHECK11", "exec"), ns)
    return lines, warn


def _mkscan(result=None, baseline=None):
    """wc_root giả: mike/logs/selfcheck_weekly_<d>.json + mike/kb/selfcheck_baseline.json.
    Tham số = None ⇒ KHÔNG tạo file đó (mô phỏng thiếu artifact)."""
    d = tempfile.mkdtemp(prefix="ops_health_check11_")
    if result is not None:
        os.makedirs(os.path.join(d, "mike", "logs"), exist_ok=True)
        with open(os.path.join(d, "mike", "logs", "selfcheck_weekly_20260812.json"),
                  "w", encoding="utf-8") as f:
            f.write(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False))
    if baseline is not None:
        os.makedirs(os.path.join(d, "mike", "kb"), exist_ok=True)
        with open(os.path.join(d, "mike", "kb", "selfcheck_baseline.json"),
                  "w", encoding="utf-8") as f:
            f.write(baseline if isinstance(baseline, str)
                    else json.dumps(baseline, ensure_ascii=False))
    return d


def _res(hours_ago, total=92, passed=92):
    return {"ts": (dt.datetime.now(dt.timezone.utc)
                   - dt.timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total": total, "pass": passed}


def case_c11_fresh_all_green():
    d = _mkscan(_res(3), {"known_red": {}})
    try:
        lines, warn = run_check11(d)
        check("check11: quét tươi + 0 đỏ ⇒ OK, không WARN", not warn and "✅" in joined(lines),
              joined(lines))
        check("check11: OK nêu số file đã quét (không phải câu chữ rỗng)",
              "92" in joined(lines), joined(lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_c11_lists_every_red_no_truncation():
    """Danh sách đỏ KHÔNG được cắt ngắn.

    Bản đầu in `_sc_new[:8]`. Đo thật 2026-08-12: đúng 9 ca đỏ chưa triage, và ca thứ 9 theo thứ
    tự alphabet là `t2_settlement_selfcheck.py` — guard settlement, thứ chạm tiền thật — bị cắt
    khỏi báo cáo hằng ngày. Việc nợ bị cắt khỏi báo cáo là việc không tồn tại: người đọc thấy
    "8 ca" và không có cách nào biết ca thứ 9 là ca nguy hiểm nhất.
    """
    names = ["a%d_selfcheck.py" % i for i in range(1, 9)] + ["t2_settlement_selfcheck.py"]
    d = _mkscan(_res(3, 93, 84), {"known_red": {n: {"auto": True, "since": "2026-08-12"}
                                                for n in names}})
    try:
        lines, warn = run_check11(d)
        out = joined(lines)
        missing = [n for n in names if n not in out]
        check("check11: liệt kê ĐỦ cả 9 ca đỏ, không cắt (ca thứ 9 = guard settlement)",
              not missing, "THIẾU: %s | %s" % (missing, out))
        check("check11: không còn dấu cắt '…' trong danh sách đỏ", "…" not in out, out)
        check("check11: số đếm khớp danh sách in ra (9 ca)", "9 selfcheck" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_c11_red_is_warn_only():
    d = _mkscan(_res(3, 92, 88), {"known_red": {
        "extreme_regime_selfcheck.py": {"auto": True, "since": "2026-08-12"},
        "t2_settlement_selfcheck.py": {"auto": True, "since": "2026-08-12"},
        "immutable_publish_selfcheck.py": {"reason": "IAM", "verified_by": "Mike"}}})
    try:
        lines, warn = run_check11(d)
        out = joined(lines)
        check("check11: có ca đỏ chưa triage ⇒ CÓ cảnh báo cho người thấy", len(warn) == 1, out)
        check("check11: mang [WARN-ONLY] (bộ quét đã escalate rồi — không dispatch lại)",
              "[WARN-ONLY]" in out, out)
        check("check11: liệt kê tên file đỏ để triage ngay trong báo cáo",
              "extreme_regime_selfcheck.py" in out, out)
        check("check11: TÁCH đỏ-chưa-triage (2) khỏi đỏ-đã-chấp-nhận (1) — không gộp để việc nợ "
              "chìm vào cái đã chấp nhận",
              "2 selfcheck" in out and "1 ca đỏ đã chấp nhận" in out, out)
        check("check11 CONTROL: bộ lọc routing THẬT (grep -vF) loại đúng dòng này",
              not [l for l in lines if "⚠️" in l and "[WARN-ONLY]" not in l], out)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    # chỉ còn đỏ ĐÃ CHẤP NHẬN ⇒ không WARN, nhưng vẫn phải NÓI RA số đó
    d = _mkscan(_res(3, 92, 91), {"known_red": {
        "immutable_publish_selfcheck.py": {"reason": "IAM", "verified_by": "Mike"}}})
    try:
        lines, warn = run_check11(d)
        check("check11: chỉ còn đỏ đã chấp nhận ⇒ không WARN nhưng vẫn nêu ra",
              not warn and "1 đỏ đã chấp nhận" in joined(lines), joined(lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_c11_stale_is_routable():
    d = _mkscan(_res(40), {"known_red": {}})
    try:
        lines, warn = run_check11(d)
        out = joined(lines)
        check("check11: quét ôi >36h ⇒ WARN", len(warn) == 1, out)
        check("check11: WARN ôi KHÔNG mang [WARN-ONLY] (cron chết là lỗi SỬA ĐƯỢC, phải route)",
              "[WARN-ONLY]" not in out, out)
        check("check11: nói rõ ÔI + nghi cron chết, không lẫn với 'có ca đỏ'",
              "ÔI" in out and "cron" in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d2 = _mkscan(_res(30), {"known_red": {}})
    try:
        _, warn2 = run_check11(d2)
        check("check11: 30h (lỡ đúng 1 lần chạy) CHƯA kêu ôi", not warn2)
    finally:
        shutil.rmtree(d2, ignore_errors=True)
    # ÔI phải thắng cả khi đang có ca đỏ: số liệu cũ 40h không được trình bày như tình trạng hiện tại
    d3 = _mkscan(_res(40), {"known_red": {"a_selfcheck.py": {"auto": True}}})
    try:
        lines3, warn3 = run_check11(d3)
        check("check11: ÔI + có đỏ ⇒ báo ÔI (routable), KHÔNG rơi vào nhánh [WARN-ONLY]",
              len(warn3) == 1 and "[WARN-ONLY]" not in joined(lines3), joined(lines3))
    finally:
        shutil.rmtree(d3, ignore_errors=True)


def case_c11_missing_and_corrupt_never_silent():
    d = _mkscan(None, {"known_red": {}})
    try:
        lines, warn = run_check11(d)
        check("check11: KHÔNG có file kết quả ⇒ WARN 'chưa từng chạy', không im lặng",
              len(warn) == 1 and "CHƯA TỪNG CHẠY" in joined(lines), joined(lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d = _mkscan(_res(3), None)
    try:
        lines, warn = run_check11(d)
        check("check11: có kết quả nhưng THIẾU baseline ⇒ vẫn WARN (không báo '0 đỏ')",
              len(warn) == 1 and "✅" not in joined(lines), joined(lines))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d = _mkscan("{ day khong phai json", {"known_red": {}})
    try:
        lines, warn = run_check11(d)
        out = joined(lines)
        check("check11: artifact HỎNG ⇒ WARN, không rơi về nhánh '0 đỏ'", len(warn) == 1, out)
        check("check11: câu chữ nói rõ KHÔNG kết luận được (khác hẳn 'không có ca đỏ')",
              "không kết luận được" in out, out)
        check("check11 CONTROL: nhánh hỏng KHÔNG in dòng ✅ nào", "✅" not in out, out)
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --- check #12: ccdb bridge mất wakeup one-shot (thêm 2026-08-17, job Wags_20260817_193233) ---
# Cùng khuôn extract-and-test như check #10/#11, và vì đúng LÝ DO đó: check #12 tồn tại để phát
# hiện một sự cố VÔ HÌNH (wakeup mất thì "không có gì xảy ra"). Nếu chính nó hỏng mà im lặng
# xanh thì nó tệ hơn không có. `subprocess` được tiêm giả để khỏi phụ thuộc journalctl thật.
class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


class _FakeSubprocess:
    """Đứng thay module subprocess: trả sẵn kết quả, hoặc ném lỗi đã hẹn.

    GHI LẠI argv của lời gọi: tiêm giả nghĩa là mọi thứ về CÁCH gọi journalctl (tên unit,
    --user hay system, cửa sổ thời gian) nằm ngoài tầm kiểm — arch-review vòng 2 chạy thử 3
    mutation (đổi tên unit, bỏ --user, đổi -24h thành -4000h) và cả 3 đều XANH. `calls` là
    chỗ ca `case_c12_journalctl_invocation_is_pinned` bịt lại lỗ đó.
    """

    def __init__(self, result=None, raises=None):
        self._result, self._raises = result, raises
        self.calls = []

    def run(self, *a, **_kw):
        self.calls.append(a[0] if a else [])
        if self._raises is not None:
            raise self._raises
        return self._result


def run_check12(fake_sub):
    lines, warn = [], []

    def W(msg):
        warn.append(msg)
        lines.append(f"⚠️ {msg}")

    def OK(msg):
        lines.append(f"✅ {msg}")

    ns = {"subprocess": fake_sub, "W": W, "OK": OK, "lines": lines}
    exec(compile(CHECK12_SRC, SRC + ":CHECK12", "exec"), ns)
    return lines, warn


_C12_DROP = ("Aug 18 02:50:02 sgms python[1]: 2026-08-17 19:50:02 [ERROR] "
             "claude_discord.cogs.scheduler: ONE_SHOT_DROPPED: task 41 (dispatch-wake-abc) was "
             "claimed and deleted but never reached Claude — this wakeup is lost and will NOT retry")


def case_c12_clean_journal_is_ok():
    lines, warn = run_check12(_FakeSubprocess(_FakeCompleted(0, "some boring INFO line\n")))
    check("check12: journal sạch ⇒ OK, 0 WARN", not warn, joined(lines))


def case_c12_dropped_wakeup_warns():
    lines, warn = run_check12(_FakeSubprocess(_FakeCompleted(0, _C12_DROP + "\n")))
    out = joined(lines)
    check("check12: có ONE_SHOT_DROPPED ⇒ WARN", len(warn) == 1, out)
    # Đếm SAI thì người đọc tưởng mất 1 wakeup trong khi mất nhiều.
    lines2, warn2 = run_check12(
        _FakeSubprocess(_FakeCompleted(0, _C12_DROP + "\n" + _C12_DROP + "\n"))
    )
    check("check12: đếm đúng số wakeup bị mất", "MẤT 2 wakeup" in joined(lines2), joined(lines2))
    check("check12: WARN-ONLY (không kích autofix cho việc đã mất, không sửa lại được)",
          "[WARN-ONLY]" in out, out)


_C12_INTERRUPTED = ("Aug 18 03:20:11 sgms python[1]: 2026-08-17 20:20:11 [ERROR] "
                    "claude_discord.cogs.scheduler: ONE_SHOT_INTERRUPTED: task 42 "
                    "(dispatch-wake-xyz) was claimed and deleted but its run did not finish")
_C12_UNREACH = ("Aug 18 03:25:00 sgms python[1]: 2026-08-17 20:25:00 [WARNING] "
                "claude_discord.cogs.scheduler: SchedulerCog: task 43 (dispatch-wake-def) "
                "has no reachable destination (thread=555, channel=555) — leaving it due to retry")


def case_c12_empty_journal_is_not_green():
    """rc=0 + stdout RỖNG là XANH GIẢ, không phải 'sạch' (arch-review vòng 2, lỗ N1).

    Chạy thật: `journalctl --user -u definitely-not-a-unit --since -24h -q` trả rc=0 và 0 byte.
    Daemon sống ghi ~4800 dòng/24h ⇒ rỗng nghĩa là sai tên unit / sai scope / journal không giữ
    log. Trước khi bịt, mọi ca đó in ✅ "không mất wakeup one-shot nào".
    """
    for label, out_s in (("rỗng hoàn toàn", ""), ("chỉ khoảng trắng", "  \n \n")):
        lines, warn = run_check12(_FakeSubprocess(_FakeCompleted(0, out_s)))
        out = joined(lines)
        check(f"check12 [journal {label}]: WARN chứ không im lặng", len(warn) == 1, out)
        check(f"check12 [journal {label}]: KHÔNG in dòng ✅ nào (xanh giả là lỗi tệ nhất ở đây)",
              "✅" not in out, out)


def case_c12_journalctl_invocation_is_pinned():
    """Canh chính LỜI GỌI journalctl, không chỉ cách xử lý output.

    Vì subprocess bị tiêm giả, đổi tên unit / bỏ --user / nới cửa sổ đều không làm ca nào đỏ —
    check vẫn "chạy đúng" trên log giả trong khi ngoài đời soi nhầm chỗ.
    """
    fake = _FakeSubprocess(_FakeCompleted(0, "boring\n"))
    run_check12(fake)
    argv = list(fake.calls[0]) if fake.calls else []
    check("check12: có gọi journalctl đúng 1 lần", len(fake.calls) == 1, repr(fake.calls))
    check("check12: gọi đúng unit ccdb-mike", "ccdb-mike" in argv, repr(argv))
    check("check12: đọc journal --user (daemon chạy dưới systemd --user, không phải system)",
          "--user" in argv, repr(argv))
    check("check12: cửa sổ đúng 24h như tiêu đề cảnh báo nói",
          "--since" in argv and "-24h" in argv, repr(argv))


def case_c12_interrupted_marker_also_counts():
    """Restart GIỮA LƯỢT (lớp sự cố đẻ ra bản fix) ghi INTERRUPTED, không phải DROPPED."""
    lines, warn = run_check12(_FakeSubprocess(_FakeCompleted(0, _C12_INTERRUPTED + "\n")))
    out = joined(lines)
    check("check12: ONE_SHOT_INTERRUPTED cũng tính là mất wakeup", len(warn) == 1, out)
    check("check12: INTERRUPTED không bị bỏ qua thành ✅", "✅" not in out, out)
    lines2, _ = run_check12(
        _FakeSubprocess(_FakeCompleted(0, _C12_DROP + "\n" + _C12_INTERRUPTED + "\n"))
    )
    check("check12: đếm gộp cả 2 marker", "MẤT 2 wakeup" in joined(lines2), joined(lines2))


def case_c12_unreachable_destination_is_reported_separately():
    """Row còn sống nhưng không giao được: agent VẪN chưa được đánh thức ⇒ phải nhìn thấy.

    Báo RIÊNG chứ không gộp vào 'MẤT': ca này còn cứu được (thread un-archive là tự chạy), gộp
    vào sẽ nói với người đọc rằng wakeup đã mất hẳn.
    """
    lines, warn = run_check12(_FakeSubprocess(_FakeCompleted(0, _C12_UNREACH + "\n")))
    out = joined(lines)
    check("check12: 'has no reachable destination' ⇒ WARN", len(warn) == 1, out)
    check("check12: KHÔNG in ✅ khi có wakeup chưa giao được", "✅" not in out, out)
    check("check12: nói rõ row còn retry (khác hẳn ca MẤT hẳn)", "retry" in out, out)
    lines2, warn2 = run_check12(
        _FakeSubprocess(_FakeCompleted(0, _C12_DROP + "\n" + _C12_UNREACH + "\n"))
    )
    check("check12: 2 lớp sự cố báo thành 2 dòng riêng", len(warn2) == 2, joined(lines2))


def case_c12_unreadable_journal_never_reports_green():
    """Không đọc được journal ≠ không có sự cố — đây đúng là chỗ check #11 đã phải bịt một lần."""
    for label, fake in (
        ("rc!=0", _FakeSubprocess(_FakeCompleted(1, "", "Failed to add match: bad"))),
        ("thiếu journalctl", _FakeSubprocess(raises=FileNotFoundError("journalctl"))),
        ("lỗi lạ", _FakeSubprocess(raises=RuntimeError("boom"))),
    ):
        lines, warn = run_check12(fake)
        out = joined(lines)
        check(f"check12 [{label}]: WARN chứ không im lặng", len(warn) == 1, out)
        check(f"check12 [{label}]: KHÔNG in dòng ✅ nào (khác hẳn 'đã kiểm và sạch')",
              "✅" not in out, out)



# ── Khối ROUTING (dispatch domain split) ────────────────────────────────────────────────
# TẠI SAO: nhánh COORD_WARN → Wags được TÁCH RA sau commit gốc a8e5b8a6, nhưng lời gọi
# ops_autofix.sh vẫn giữ nguyên "$MSG" (toàn bộ báo cáo) suốt từ đó ⇒ Winston nhận CẢ triệu
# chứng điều phối vừa route sang Wags. Đo được 2 ngày liên tiếp 08-17 và 08-18: hai job Opus
# chẩn đoán CÙNG một câu hỏi tồn đọng. Bản chất là refactor DỞ DANG, không phải bug logic —
# loại lỗi mà không test nào bắt được vì cả 2 nhánh đều "chạy đúng". Ca này chạy ĐÚNG khối
# bash thật (không copy) với 2 autofix GIẢ ghi lại argv, nên hồi quy = đỏ ngay.
_ROUTE_MSG = "\n".join([
    "✅ Kiểm tra sức khỏe vận hành SpaceX 2026-08-18",
    "⚠️ Có 2 câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: ['Mike/x', 'Wags/y']",
    "⚠️ Circuit breaker đang TRIPPED cho Mafee",
    "⚠️ Job board: 1 job overdue (Taylor_20260818_000000)",
    "❌ run_bot ZaloPay lỗi: TimeoutError khi gọi broker",
    "⚠️ [WARN-ONLY] question TREO LÂU >48h cần user chọn A/B: Mike/foo",
    "⚠️ plan T+1 NOT_APPROVED cho SpaceX",
])


def run_routing(msg, src=None):
    """Exec ĐÚNG khối ROUTING của ops_health_check.sh; trả argv thật của 2 autofix (None = không gọi)."""
    import shlex
    import subprocess as sp
    d = tempfile.mkdtemp(prefix="ops_health_routing_")
    try:
        os.makedirs(os.path.join(d, "bin"))
        for name in ("ops_autofix.sh", "wags_autofix.sh"):
            fp = os.path.join(d, "bin", name)
            with open(fp, "w", encoding="utf-8") as f:
                f.write("#!/usr/bin/env bash\n"
                        "printf '%s\\n=ARG=\\n' \"$@\" > \"$ARGV_DIR/" + name + ".argv\"\n")
            os.chmod(fp, 0o755)
        script = ("set -uo pipefail\n"
                  "ROOT=" + shlex.quote(d) + "\n"
                  "ACCOUNT=SpaceX\n"
                  "TODAY=2026-08-18\n"
                  "MSG=" + shlex.quote(msg) + "\n") + (src if src is not None else ROUTING_SRC)
        env = dict(os.environ, ARGV_DIR=d)
        sp.run(["bash", "-c", script], env=env, capture_output=True, text=True, timeout=30)

        def read(name):
            fp = os.path.join(d, name + ".argv")
            if not os.path.exists(fp):
                return None
            with open(fp, encoding="utf-8") as f:
                parts = f.read().split("\n=ARG=\n")
            return [x for x in parts[:-1]]
        return read("ops_autofix.sh"), read("wags_autofix.sh")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def case_routing_domain_split_is_real():
    ops, wags = run_routing(_ROUTE_MSG)
    check("routing: khối bash thật gọi ĐƯỢC cả 2 autofix (harness sống)",
          ops is not None and wags is not None, "ops=%r wags=%r" % (ops, wags))
    if ops is None or wags is None:
        return
    check("routing: label ops giữ nguyên per-account", ops[0] == "ops-health-SpaceX", ops[0])
    check("routing: label wags fleet-wide theo ngày", wags[0] == "coord-2026-08-18", wags[0])
    ops_d, wags_d = ops[1], wags[1]
    check("routing: Winston VẪN nhận lỗi vận hành của mình (run_bot)",
          "run_bot ZaloPay" in ops_d, ops_d)
    for term in ("câu hỏi (question)", "Circuit breaker", "Job board:"):
        check("routing: Winston KHÔNG nhận triệu chứng ĐIỀU PHỐI %r (đã route sang Wags)" % term,
              term not in ops_d, ops_d)
        check("routing: Wags nhận %r" % term, term in wags_d, wags_d)
    check("routing: Wags KHÔNG nhận lỗi vận hành của Winston", "run_bot" not in wags_d, wags_d)
    for who, det in (("Winston", ops_d), ("Wags", wags_d)):
        check("routing: %s không nhận dòng [WARN-ONLY] (chỉ user quyết được)" % who,
              "[WARN-ONLY]" not in det, det)
        check("routing: %s không nhận dòng NOT_APPROVED (việc của user)" % who,
              "NOT_APPROVED" not in det, det)
    check("routing: chi tiết gửi Winston có nêu account đang chạy", "account=SpaceX" in ops_d, ops_d)


def case_routing_coord_only_does_not_wake_winston():
    ops, wags = run_routing("\n".join([
        "⚠️ Có 1 câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: ['Wags/y']",
        "✅ phần còn lại ổn"]))
    check("routing: chỉ có triệu chứng điều phối ⇒ KHÔNG dispatch Winston", ops is None, repr(ops))
    check("routing: … nhưng vẫn dispatch Wags", wags is not None, repr(wags))


def case_routing_red_control():
    """RED control: 2 đột biến phải làm ĐỎ đúng assertion ở trên, nếu không test này vô nghĩa."""
    mut_msg = ROUTING_SRC.replace('"$OTHER_WARN (checker run: account=${ACCOUNT})"',
                                  '"$MSG"')
    check("routing RED: đột biến 1 áp dụng được (chuỗi lời gọi chưa trôi)",
          mut_msg != ROUTING_SRC, "không tìm thấy lời gọi ops_autofix để đột biến")
    ops, _ = run_routing(_ROUTE_MSG, src=mut_msg)
    check("routing RED#1 (quay lại $MSG): Winston LẠI nhận triệu chứng điều phối ⇒ assertion "
          "chính phân biệt được",
          ops is not None and "câu hỏi (question)" in ops[1], repr(ops))

    mut_filter = ROUTING_SRC.replace('grep -vE "NOT_APPROVED|KHÔNG TÌM THẤY|Circuit breaker|'
                                     'câu hỏi \\(question\\)|Job board:"',
                                     'grep -vE "NOT_APPROVED|KHÔNG TÌM THẤY"')
    check("routing RED: đột biến 2 áp dụng được (bộ lọc OTHER_WARN chưa trôi)",
          mut_filter != ROUTING_SRC, "không tìm thấy bộ lọc OTHER_WARN để đột biến")
    ops2, _ = run_routing(_ROUTE_MSG, src=mut_filter)
    check("routing RED#2 (bỏ lọc coord khỏi OTHER_WARN): Winston LẠI nhận Circuit breaker",
          ops2 is not None and "Circuit breaker" in ops2[1], repr(ops2))



def main():
    print("ops_health_check_selfcheck: check #5 (backlog question) + check #10 (notify_thread) "
          "+ check #11 (selfcheck_red_sweep freshness) + check #12 (ccdb one-shot dropped) "
          "+ khối DELIVER (Discord→Telegram) regression")
    for fn in (case_archived_question_visible, case_cross_layer_resolve,
               case_explicit_cross_topic_resolve,
               case_resolver_must_be_after, case_dedupe_hot_and_archive,
               case_no_crowd_out, case_small_pool_prints_all,
               case_corrupt_gz_warns, case_empty_archive_warns,
               case_grace_fresh_question_not_routable, case_grace_expired_question_is_routable,
               case_grace_schedule_aware_last_weekday_gap,
               case_fresh_question_is_pending,
               case_wagsfix_not_confirmed_is_warn_only, case_wagsfix_prefix_not_substring,
               case_wagsfix_only_no_false_ok, case_wagsfix_prefix_list_in_sync,
               case_triaged_needs_human_ack, case_triaged_only_no_false_ok,
               case_ack_suppress_days_window, case_rollup_of_umbrella_question,
               case_rollup_of_substring_holes, case_rollup_of_ref_forms,
               case_rollup_of_ref_forms_agent_aware,
               case_missing_inbox_dir_is_warn_not_green,
               case_ack_suppress_days_capped,
               case_aged_wagsfix_never_truncated, case_aged_no_wagsfix_keeps_old_cut,
               case_aged_wagsfix_overflow_is_loud,
               case_c10_no_file_is_ok, case_c10_fresh_log_warns,
               case_c10_swap_recovery_is_not_swallowed, case_c10_hard_error_wins_over_swap,
               case_c10_fresh_log_without_timestamp_line, case_c10_old_log_is_ok,
               case_c10_old_hard_error_not_reported_as_recent,
               case_c10_fresh_file_all_records_old_is_ok,
               case_c11_fresh_all_green, case_c11_red_is_warn_only,
               case_c11_lists_every_red_no_truncation,
               case_c11_stale_is_routable, case_c11_missing_and_corrupt_never_silent,
               case_c12_clean_journal_is_ok, case_c12_dropped_wakeup_warns,
               case_c12_empty_journal_is_not_green, case_c12_journalctl_invocation_is_pinned,
               case_c12_interrupted_marker_also_counts,
               case_c12_unreachable_destination_is_reported_separately,
               case_c12_unreadable_journal_never_reports_green,
               case_routing_domain_split_is_real,
               case_routing_coord_only_does_not_wake_winston,
               case_routing_red_control,
               case_deliver_discord_ok_no_telegram,
               case_deliver_discord_fails_falls_back_to_telegram,
               case_deliver_both_fail_logs_for_check10):
        fn()
    if FAILS:
        print(f"\nFAIL: {len(FAILS)} assertion hỏng")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    print("\nOK: toàn bộ assertion PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
