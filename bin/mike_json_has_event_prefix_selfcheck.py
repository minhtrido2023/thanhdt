#!/usr/bin/env python3
"""Selfcheck cho `bin/mike_json.py has-event-prefix` — hợp đồng khớp TIỀN TỐ.

TẠI SAO tồn tại (2026-08-12, arch-reviewer required_change #2 trên vòng 1 của
'wags-fix: close-the-loop-mechanism-fix', commit 35625a6f): subcommand này được thêm để vá
một bug đã âm thầm chạy 8 ngày (08-04→08-11) — wags_autofix.sh bước 1.5 gọi `has-event`
(khớp TUYỆT ĐỐI) với "finding:wags-fix: <label>" trong khi prompt yêu cầu Wags ghi topic
BẮT ĐẦU BẰNG chuỗi đó và Wags luôn nối mô tả tự do phía sau ⇒ không bao giờ khớp ⇒ mỗi
ngày một cảnh báo 🟡 "Wags KHÔNG ghi finding" giả. Vòng 1 CÓ chạy harness thật ở
/tmp/wagsharness nhưng KHÔNG commit nó — nghĩa là bản vá cho một bug-âm-thầm-8-ngày lại
được canh bằng một test không ai chạy lại được. File này biến harness đó thành regression
test đứng, tự động vào run_selfchecks.sh (registry glob theo tên *selfcheck*.py).

CÁCH LÀM: chạy CLI thật qua subprocess (không import hàm) — pipeline gọi nó bằng dòng lệnh
nên test phải đi đúng đường đó để không bỏ sót lỗi ở lớp argv/exit-code. Bus GIẢ trong
tmpdir, KHÔNG bao giờ chạm bus thật.

Chạy: python3 bin/mike_json_has_event_prefix_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJ = os.path.join(ROOT, "bin", "mike_json.py")
FAILS = []

SINCE = "2026-08-11T01:20:07Z"
LABEL = "coord-2026-08-11"
# Chuỗi THẬT của sự cố: prompt hứa tiền tố, agent nối mô tả tự do phía sau.
REAL_TOPIC = f"wags-fix: {LABEL} — gate state_source báo động giả"
PREFIX_SPEC = f"finding:wags-fix: {LABEL}"


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def mkbus():
    d = tempfile.mkdtemp(prefix="has_event_prefix_selfcheck_")
    os.makedirs(os.path.join(d, "inbox", "archive"), exist_ok=True)
    return d


def ev(agent, etype, topic, ts):
    return {"agent_id": agent, "event_type": etype, "topic": topic, "ts": ts,
            "payload": {}, "event_id": f"{agent}-{etype}-{topic}-{ts}"}


def write_jsonl(path, events, gz=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
    if gz:
        with gzip.open(path, "wt", encoding="utf-8") as f:
            f.write(body)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)


def run(*args):
    p = subprocess.run([sys.executable, MJ, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def hot(root, events):
    write_jsonl(os.path.join(root, "inbox", "Wags.jsonl"), events)


# ── Ca 1: tiền tố THẬT (topic = tiền tố + mô tả tự do) phải KHỚP — đây chính là ca mà
#    has-event tuyệt đối đã trượt suốt 8 ngày. Kèm luôn đối chứng: has-event CŨ vẫn phải
#    trượt trên CÙNG dữ liệu (nếu nó cũng khớp thì ai đó đã nới lỏng semantics tuyệt đối,
#    làm hỏng 3 caller còn lại: weekly_ops_audit.sh, fearbuy_weekly_scan.sh, eod_trading_report.sh).
def case_prefix_matches_suffixed_topic():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:28:49Z")])
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("prefix + mô tả tự do phía sau: exit 0 + in MATCH", rc == 0 and "MATCH" in out,
              f"rc={rc} out={out}")
        check("MATCH in ra topic ĐẦY ĐỦ (người đọc verify được đúng event nào)",
              REAL_TOPIC in out, out)
        rc2, out2, _ = run("has-event", root, "Wags", SINCE, PREFIX_SPEC)
        check("đối chứng: has-event (tuyệt đối) VẪN trượt trên cùng dữ liệu — semantics cũ "
              "không bị nới lỏng", rc2 == 1, f"rc={rc2} out={out2}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 2 (ĐỐI CHỨNG ÂM, quan trọng nhất): khớp phải là TIỀN TỐ, KHÔNG phải substring.
#    Nếu lỏng thành substring thì một event chỉ TÌNH CỜ nhắc tới label ở giữa topic
#    (vd finding tổng kết "3 câu hỏi ... wags-fix: coord-... là báo động giả") sẽ tự nhận
#    là bằng chứng Wags đã làm việc ⇒ pipeline báo xong khi chưa ai làm gì. Đây là chiều
#    hỏng NGUY HIỂM hơn bug gốc: bug gốc chỉ báo động giả, chiều này giấu mất việc chưa làm.
def case_substring_in_middle_does_not_match():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "finding", f"tong ket: {REAL_TOPIC} la bao dong gia",
                      "2026-08-11T01:28:49Z")])
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("substring-ở-GIỮA topic: KHÔNG khớp (exit 1)", rc == 1, f"rc={rc} out={out}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 3: topic TRÙNG KHÍT tiền tố (không có hậu tố) vẫn phải khớp — prefix là quan hệ
#    phản xạ; nếu chỉ khớp khi CÓ hậu tố thì agent nào ghi topic đúng y hợp đồng lại bị coi
#    là chưa ghi.
def case_exact_topic_still_matches():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "finding", f"wags-fix: {LABEL}", "2026-08-11T01:28:49Z")])
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("topic trùng khít tiền tố (không hậu tố): vẫn khớp", rc == 0, f"rc={rc} out={out}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 4: cutoff since_iso. Prefix match RỘNG hơn exact match, nên một event cũ cùng label
#    (nhãn theo NGÀY, lặp lại hằng ngày) false-positive dễ hơn hẳn — cutoff là thứ duy nhất
#    chặn "vòng chạy hôm nay tự chữa bằng bằng chứng của vòng hôm qua".
def case_since_iso_cutoff():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:19:00Z")])   # TRƯỚC since
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("event TRƯỚC since_iso: KHÔNG khớp (chống bằng chứng cũ tự chữa)",
              rc == 1, f"rc={rc} out={out}")
        # đúng đường biên: ts == since_iso được tính là trong cửa sổ (>= chứ không phải >)
        hot(root, [ev("Wags", "finding", REAL_TOPIC, SINCE)])
        rc2, _, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("event ĐÚNG BẰNG since_iso: khớp (biên >=, không phải >)", rc2 == 0, f"rc={rc2}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 5: event_type phải khớp tuyệt đối — chỉ topic mới khớp tiền tố. Một `question` hay
#    `status` cùng topic KHÔNG chứng minh được agent đã ghi `finding`.
def case_event_type_must_match_exactly():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "question", REAL_TOPIC, "2026-08-11T01:28:49Z"),
                   ev("Wags", "status", REAL_TOPIC, "2026-08-11T01:29:00Z")])
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("đúng topic nhưng SAI event_type: KHÔNG khớp", rc == 1, f"rc={rc} out={out}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 6: spec sai định dạng (thiếu dấu ':') phải exit 2 — KHÁC hẳn exit 1 ("không tìm
#    thấy"). Gộp 2 mã này chính là lớp lỗi close-the-loop: "tra cứu hỏng" bị đọc thành
#    "không có bằng chứng" rồi thành "việc chưa làm".
def case_bad_spec_exit_2():
    root = mkbus()
    try:
        hot(root, [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:28:49Z")])
        rc, _, err = run("has-event-prefix", root, "Wags", SINCE, "khong-co-dau-hai-cham")
        check("spec thiếu ':' ⇒ exit 2 (lỗi gọi), KHÔNG phải exit 1 (không tìm thấy)",
              rc == 2, f"rc={rc} err={err}")
        check("spec sai in ra stderr nói rõ định dạng mong đợi",
              "expected event_type:topic_prefix" in err, err)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 7: quét CẢ tầng archive (kb_nightly Phase 1b2 nén event >30d sang
#    inbox/archive/<agent>_<YYYY-MM>.jsonl.gz). Cùng lớp lỗi reader-scope đã cắn 2 lần ở
#    check #5 và ở trace/verify-coverage (mike_json_archive_selfcheck.py).
def case_scans_archive_tier():
    root = mkbus()
    try:
        write_jsonl(os.path.join(root, "inbox", "archive", "Wags_2026-08.jsonl.gz"),
                    [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:28:49Z")], gz=True)
        hot(root, [ev("Wags", "status", "nhieu", "2026-08-11T02:00:00Z")])
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("event chỉ nằm trong archive .jsonl.gz: VẪN khớp", rc == 0, f"rc={rc} out={out}")
        # archive của agent KHÁC có tên bắt đầu giống không được lẫn vào
        root2 = mkbus()
        try:
            write_jsonl(os.path.join(root2, "inbox", "archive", "WagsX_2026-08.jsonl.gz"),
                        [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:28:49Z")], gz=True)
            rc2, _, _ = run("has-event-prefix", root2, "Wags", SINCE, PREFIX_SPEC)
            check("archive của agent KHÁC (WagsX) KHÔNG bị tính là của Wags", rc2 == 1,
                  f"rc={rc2}")
        finally:
            shutil.rmtree(root2, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 8: nhiều spec = quan hệ HOẶC; và file bus hỏng 1 dòng không được làm chết cả lệnh
#    (dòng hỏng ⇒ mất bằng chứng ⇒ báo động giả, đúng thứ file này đang chặn).
def case_multi_spec_and_corrupt_line():
    root = mkbus()
    try:
        path = os.path.join(root, "inbox", "Wags.jsonl")
        write_jsonl(path, [ev("Wags", "finding", REAL_TOPIC, "2026-08-11T01:28:49Z")])
        with open(path, "a", encoding="utf-8") as f:
            f.write("{day khong phai json\n")
        rc, out, _ = run("has-event-prefix", root, "Wags", SINCE,
                         "finding:khong-ton-tai", PREFIX_SPEC)
        check("nhiều spec: khớp 1 trong số đó là đủ (quan hệ HOẶC)", rc == 0, f"rc={rc} out={out}")
        check("dòng JSON hỏng trong bus KHÔNG làm hỏng kết quả", "MATCH" in out, out)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ── Ca 9: agent chưa từng có file inbox (bus rỗng) ⇒ exit 1 sạch sẽ, không traceback.
def case_missing_inbox_file():
    root = mkbus()
    try:
        rc, out, err = run("has-event-prefix", root, "Wags", SINCE, PREFIX_SPEC)
        check("không có file inbox: exit 1 (no match), không traceback",
              rc == 1 and "Traceback" not in err, f"rc={rc} out={out} err={err}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    print("mike_json_has_event_prefix_selfcheck: hợp đồng khớp TIỀN TỐ của has-event-prefix")
    for fn in (case_prefix_matches_suffixed_topic, case_substring_in_middle_does_not_match,
               case_exact_topic_still_matches, case_since_iso_cutoff,
               case_event_type_must_match_exactly, case_bad_spec_exit_2,
               case_scans_archive_tier, case_multi_spec_and_corrupt_line,
               case_missing_inbox_file):
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
