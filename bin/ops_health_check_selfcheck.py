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


def run_check5(wc_root):
    """Chạy khối thật trên 1 bus giả; trả về (lines, warn_count)."""
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


def ev(agent, etype, topic, ts):
    return {"agent_id": agent, "event_type": etype, "topic": topic, "ts": ts,
            "payload": {}, "event_id": f"{agent}-{etype}-{topic}"}


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


# ── Ca 10 (2026-07-31, audit kiến trúc fleet #14): câu hỏi wags-fix-not-confirmed:*
#    <48h KHÔNG được re-trigger COORD_WARN — đây chính là input của vòng lặp Wags
#    coord-fix tự nuôi quan sát được thật hôm 07-31 (arch-reviewer NEEDS_CHANGES → question
#    → question đó tự nó lại là "câu hỏi tồn đọng" khiến ops_health_check dispatch LẠI
#    wags_autofix cho ĐÚNG issue vừa NEEDS_CHANGES). Câu hỏi KHÁC (không phải wags-fix) vẫn
#    phải routable như cũ — ca 9 ở trên đã khoá phần đó, ca này chỉ khoá phần MỚI.
def case_wagsfix_not_confirmed_is_warn_only():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "question", "wags-fix-not-confirmed: coord-2026-07-31", ago(0, 3)),
                      ev("Wags", "question", "coord-that-su-moi", ago(0, 1))])
        lines, _ = run_check5(root)
        out = joined(lines)
        wagsfix_lines = [ln for ln in lines if "vòng wags-fix CHƯA CONFIRMED" in ln]
        pending_lines = [ln for ln in lines if "trong 48h qua CHƯA thấy answer" in ln]
        check("wags-fix-not-confirmed <48h: có dòng riêng, mang [WARN-ONLY]",
              len(wagsfix_lines) == 1 and "[WARN-ONLY]" in wagsfix_lines[0]
              and "wags-fix-not-confirmed: coord-2026-07-31" in wagsfix_lines[0], out)
        check("wags-fix-not-confirmed <48h: KHÔNG lẫn vào dòng pending routable",
              not any("wags-fix-not-confirmed" in ln for ln in pending_lines), out)
        check("câu hỏi coordination KHÁC (không phải wags-fix) vẫn ở dòng pending routable",
              len(pending_lines) == 1 and "coord-that-su-moi" in pending_lines[0], out)
        check("câu hỏi coordination khác đó KHÔNG mang [WARN-ONLY]",
              not any("[WARN-ONLY]" in ln for ln in pending_lines), out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 11: chỉ có wags-fix-not-confirmed (không có câu hỏi routable nào khác) — dòng
#    "Không có câu hỏi nào đang chờ" KHÔNG được in (sẽ nói dối — vẫn có 1 mục đang chờ,
#    chỉ là WARN-ONLY).
def case_wagsfix_only_no_false_ok():
    root, inbox = mkbus()
    try:
        write_events(os.path.join(inbox, "Wags.jsonl"),
                     [ev("Wags", "question", "wags-fix-not-confirmed: coord-2026-07-31", ago(0, 3))])
        lines, _ = run_check5(root)
        out = joined(lines)
        check("chỉ có wags-fix: KHÔNG in 'Không có câu hỏi nào đang chờ' (sẽ nói dối)",
              "Không có câu hỏi (question) nào đang chờ xử lý" not in out, out)
        check("chỉ có wags-fix: vẫn có dòng WARN-ONLY nêu rõ",
              "vòng wags-fix CHƯA CONFIRMED" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


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


def case_c10_fresh_log_warns():
    root = _mklog("2026-08-02T23:14:57+07:00 notify_thread: KHONG phan giai duoc topic foo\n"
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
              len(warn) == 1 and "không đọc được nội dung" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_c10_old_log_is_ok():
    root = _mklog("2026-07-01T10:00:00+07:00 notify_thread: loi cu\n", age_seconds=86400 + 3600)
    try:
        lines, warn = run_check10(root)
        check("check10: log cũ hơn 24h ⇒ OK (cảnh báo tự tắt)", not warn, joined(lines))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    print("ops_health_check_selfcheck: check #5 (backlog question) + check #10 (notify_thread) regression")
    for fn in (case_archived_question_visible, case_cross_layer_resolve,
               case_resolver_must_be_after, case_dedupe_hot_and_archive,
               case_no_crowd_out, case_small_pool_prints_all,
               case_corrupt_gz_warns, case_empty_archive_warns,
               case_fresh_question_is_pending,
               case_wagsfix_not_confirmed_is_warn_only, case_wagsfix_only_no_false_ok,
               case_c10_no_file_is_ok, case_c10_fresh_log_warns,
               case_c10_fresh_log_without_timestamp_line, case_c10_old_log_is_ok):
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
