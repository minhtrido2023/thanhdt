#!/usr/bin/env python3
"""Selfcheck cho `bin/wags_bus_verdict.py` + bất biến hoà giải verdict của wags_autofix.sh.

TẠI SAO tồn tại (2026-08-12, arch-reviewer required_change #2 trên vòng 1 của
'wags-fix: close-the-loop-mechanism-fix', commit 35625a6f): wags_bus_verdict.py là lớp
BẰNG CHỨNG cuối cùng quyết định pipeline báo ✅ HOÀN TẤT hay ⚠️ CẦN NGƯỜI XEM. Vòng 1 chỉ
verify nó bằng harness dùng-một-lần ở /tmp/wagsharness (không commit) — tức là lớp quyết
định "fix có được duyệt không" lại không có regression test nào chạy lại được. Kênh này đã
sai THẬT 2 lần: 2026-07-08 notify in {"status":"sent"} vào stdout ⇒ 2 question giả;
2026-07-22T05:55Z INCONCLUSIVE, 8 ngày sau đóng lại là FALSE_ALARM.

2 phần:
  A. Đọc bus (subprocess CLI thật) — latest-wins, cutoff, payload là chuỗi / hỏng, file thiếu.
  B. Bất biến hoà giải trong wags_autofix.sh — KHÔNG copy thuật toán: TRÍCH đúng khối giữa
     WAGS_VERDICT_RECONCILE_BEGIN/END rồi chạy nó trên bus giả. Khối đó nằm trong một chuỗi
     nháy-đơn của script mẹ, nên phải "bóc" đúng một tầng nháy như shell mẹ vẫn làm —
     dựng lại bằng chính `printf '%s' '<khối>'` thay vì tự đoán, để bản test thấy ĐÚNG văn
     bản mà bash con thấy lúc chạy thật.

Chạy: python3 bin/wags_bus_verdict_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BV = os.path.join(ROOT, "bin", "wags_bus_verdict.py")
# Env override CHỈ để mutation-test (chứng minh test này đỏ được); prod luôn dùng file thật.
AUTOFIX_SRC = os.environ.get("WAGS_AUTOFIX_SRC") or os.path.join(ROOT, "bin", "wags_autofix.sh")
FAILS = []

LABEL = "coord-2026-08-11"
TOPIC = f"ARCH-REVIEW: wags-fix: {LABEL}"
SINCE = "2026-08-11T01:20:07Z"


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        FAILS.append(f"{name} — {detail}")
        print(f"  FAIL  {name} — {detail}")


def ev(topic, ts, payload, etype="verification"):
    return {"agent_id": "arch-reviewer", "event_type": etype, "topic": topic, "ts": ts,
            "payload": payload, "event_id": f"arch-{topic}-{ts}"}


def mkinbox(events, raw_extra=None):
    d = tempfile.mkdtemp(prefix="wags_bus_verdict_selfcheck_")
    path = os.path.join(d, "arch-reviewer.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        if raw_extra:
            f.write(raw_extra)
    return d, path


def run_bv(inbox, topic=TOPIC, since=SINCE):
    p = subprocess.run([sys.executable, BV, inbox, topic, since],
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr


# ══ Phần A — hợp đồng đọc bus ═════════════════════════════════════════════════════════════

# ── Ca 1: LATEST-WINS. arch-reviewer có thể ghi nhiều verification cùng topic trong một
#    vòng (review lại sau khi Wags sửa tiếp). Bản CUỐI mới là kết luận; lấy bản đầu là đóng
#    băng phán quyết cũ lên bản vá mới.
def case_latest_wins():
    d, path = mkinbox([
        ev(TOPIC, "2026-08-11T01:30:00Z", {"verdict": "NEEDS_CHANGES"}),
        ev(TOPIC, "2026-08-11T01:35:27Z", {"verdict": "CONFIRMED"}),
    ])
    try:
        rc, out, _ = run_bv(path)
        check("latest-wins: lấy verification MỚI NHẤT (CONFIRMED), không phải bản đầu",
              rc == 0 and out == "CONFIRMED", f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 1b: latest-wins theo THỨ TỰ DÒNG (bus là append-only) — kể cả khi verdict mới XẤU
#    hơn. Nếu ai đó "tối ưu" thành ưu tiên CONFIRMED thì một NEEDS_CHANGES ghi sau sẽ bị nuốt.
def case_latest_wins_even_when_worse():
    d, path = mkinbox([
        ev(TOPIC, "2026-08-11T01:30:00Z", {"verdict": "CONFIRMED"}),
        ev(TOPIC, "2026-08-11T01:35:27Z", {"verdict": "NEEDS_CHANGES"}),
    ])
    try:
        rc, out, _ = run_bv(path)
        check("latest-wins kể cả khi verdict mới XẤU hơn (không ưu ái CONFIRMED)",
              rc == 0 and out == "NEEDS_CHANGES", f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 2: cutoff since_iso — nhãn label gắn theo NGÀY và lặp lại hằng ngày, nên một
#    CONFIRMED của vòng HÔM QUA cùng label tuyệt đối không được tự chữa vòng hôm nay
#    (chính là lý do script cố ý bắt truyền since_iso tường minh, không nhận "N giờ trước").
def case_since_cutoff_blocks_stale_confirmed():
    d, path = mkinbox([ev(TOPIC, "2026-08-10T06:02:04Z", {"verdict": "CONFIRMED"})])
    try:
        rc, out, _ = run_bv(path)
        check("CONFIRMED cũ hơn since_iso: KHÔNG được tính (exit 1, in rỗng)",
              rc == 1 and out == "", f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 3: topic khớp TIỀN TỐ (arch-reviewer nối mô tả phía sau) nhưng topic KHÁC hẳn thì không.
def case_topic_prefix_scope():
    d, path = mkinbox([
        ev(f"{TOPIC} — vòng 2", "2026-08-11T01:35:27Z", {"verdict": "CONFIRMED"}),
        ev("ARCH-REVIEW: wags-fix: coord-2026-08-99", "2026-08-11T01:36:00Z",
           {"verdict": "REFUTED"}),
    ])
    try:
        rc, out, _ = run_bv(path)
        check("topic khớp tiền tố (có hậu tố mô tả): vẫn nhận",
              rc == 0 and out == "CONFIRMED", f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 4: chỉ `verification` mới là artifact. finding/status của arch-reviewer cùng topic
#    là văn xuôi, không phải phán quyết.
def case_event_type_must_be_verification():
    d, path = mkinbox([ev(TOPIC, "2026-08-11T01:35:27Z", {"verdict": "CONFIRMED"},
                          etype="finding")])
    try:
        rc, out, _ = run_bv(path)
        check("event_type != verification: bỏ qua (exit 1)", rc == 1 and out == "",
              f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 5: payload LÀ CHUỖI JSON (append_event.sh nhận payload dạng chuỗi ở một số caller)
#    — phải parse được, nếu không mọi verdict qua đường đó biến mất im lặng.
def case_payload_as_json_string():
    d, path = mkinbox([ev(TOPIC, "2026-08-11T01:35:27Z",
                          json.dumps({"verdict": "CONFIRMED", "confidence": "high"}))])
    try:
        rc, out, _ = run_bv(path)
        check("payload là CHUỖI JSON: vẫn đọc ra verdict", rc == 0 and out == "CONFIRMED",
              f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 6: payload HỎNG (chuỗi không phải JSON / không phải dict / thiếu key verdict) ⇒
#    không có bằng chứng ⇒ exit 1, KHÔNG crash. Fail-closed: "không đọc được" phải ra cùng
#    tín hiệu với "không có", để nhánh gọi giữ nguyên đường báo động thay vì tự nâng cấp.
def case_broken_payload_is_silent_not_crash():
    for label, payload in (("chuỗi không phải JSON", "khong phai json {{"),
                           ("payload là list", ["verdict", "CONFIRMED"]),
                           ("dict thiếu key verdict", {"confidence": "high"}),
                           ("verdict rỗng", {"verdict": ""})):
        d, path = mkinbox([ev(TOPIC, "2026-08-11T01:35:27Z", payload)])
        try:
            rc, out, err = run_bv(path)
            check(f"payload hỏng ({label}): exit 1, in rỗng, KHÔNG traceback",
                  rc == 1 and out == "" and "Traceback" not in err,
                  f"rc={rc} out={out!r} err={err}")
        finally:
            shutil.rmtree(d, ignore_errors=True)


# ── Ca 7: dòng JSON hỏng CHEN GIỮA không được nuốt mất verdict ở dòng sau (bus bị ghi
#    đồng thời có thể sinh dòng cụt).
def case_corrupt_line_does_not_hide_later_verdict():
    d, path = mkinbox([ev(TOPIC, "2026-08-11T01:30:00Z", {"verdict": "NEEDS_CHANGES"})],
                      raw_extra="{dong cut khong dong ngoac\n"
                                + json.dumps(ev(TOPIC, "2026-08-11T01:35:27Z",
                                                {"verdict": "CONFIRMED"})) + "\n")
    try:
        rc, out, _ = run_bv(path)
        check("dòng hỏng chen giữa: verdict dòng SAU vẫn đọc được",
              rc == 0 and out == "CONFIRMED", f"rc={rc} out={out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 8: file KHÔNG TỒN TẠI ⇒ exit 1 + rỗng (không traceback, không tạo file).
#    Đây là trạng thái thật của một fleet mới/bus vừa archive — phải im lặng đúng cách.
def case_missing_file():
    d = tempfile.mkdtemp(prefix="wags_bus_verdict_selfcheck_")
    try:
        rc, out, err = run_bv(os.path.join(d, "khong-ton-tai.jsonl"))
        check("file bus thiếu: exit 1, in rỗng, không traceback",
              rc == 1 and out == "" and "Traceback" not in err, f"rc={rc} out={out!r} err={err}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 9: sai số lượng tham số ⇒ exit 1 + rỗng (caller dùng `|| true` nên không được in
#    rác ra stdout — rác ở stdout CHÍNH LÀ sự cố 2026-07-08).
def case_bad_argc():
    p = subprocess.run([sys.executable, BV, "chi-mot-tham-so"], capture_output=True, text=True)
    check("thiếu tham số: exit 1 và stdout KHÔNG có rác", p.returncode == 1
          and p.stdout.strip() == "", f"rc={p.returncode} out={p.stdout!r}")


# ══ Phần B — bất biến hoà giải verdict (trích từ wags_autofix.sh, không copy) ═════════════

def extract_reconcile_block(pipelog):
    """Trả về ĐÚNG văn bản mà bash con thấy: trích giữa 2 marker rồi bóc một tầng nháy đơn
    bằng chính shell (printf '%s' '<khối>'), thay vì tự đoán quy tắc thoát nháy."""
    with open(AUTOFIX_SRC, encoding="utf-8") as f:
        src = f.read()
    # Cắt từ SAU hết dòng chứa marker mở: phần chữ còn lại trên chính dòng đó là văn xuôi
    # giải thích, không phải code — gộp vào sẽ thành lệnh shell rác.
    m = re.search(r"# WAGS_VERDICT_RECONCILE_BEGIN[^\n]*\n(.*?)[ \t]*# WAGS_VERDICT_RECONCILE_END",
                  src, re.S)
    if not m:
        return None
    body = m.group(1)
    unquote = subprocess.run(["bash", "-c", f"PIPELOG={pipelog}; printf '%s' '{body}'"],
                             capture_output=True, text=True)
    if unquote.returncode != 0:
        return None
    return unquote.stdout


def run_reconcile(verdict_stdout, bus_events):
    """Chạy khối hoà giải THẬT với $ROOT trỏ vào sandbox; in ra verdict + verdict_disagree."""
    d = tempfile.mkdtemp(prefix="wags_reconcile_selfcheck_")
    try:
        os.makedirs(os.path.join(d, "bin"))
        os.makedirs(os.path.join(d, "bus", "inbox"))
        shutil.copy2(BV, os.path.join(d, "bin", "wags_bus_verdict.py"))
        with open(os.path.join(d, "bus", "inbox", "arch-reviewer.jsonl"), "w",
                  encoding="utf-8") as f:
            for e in bus_events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        pipelog = os.path.join(d, "pipe.log")
        block = extract_reconcile_block(pipelog)
        if block is None:
            return None
        script = (f'set -u\nROOT={d}\nLABEL="{LABEL}"\nDISPATCH_START_ISO="{SINCE}"\n'
                  f'verdict="{verdict_stdout}"\nsummary="tom tat"\n'
                  f'{block}\n'
                  f'printf "VERDICT=%s\\nDISAGREE=%s\\n" "$verdict" "$verdict_disagree"\n')
        p = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        log = open(pipelog, encoding="utf-8").read() if os.path.exists(pipelog) else ""
        return p.returncode, p.stdout, p.stderr, log
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 10: marker phải còn ở đó — mất marker = mất luôn phần test bất biến, đúng kiểu im
#    lặng mà file này sinh ra để chặn.
def case_reconcile_markers_exist():
    d = tempfile.mkdtemp(prefix="wags_marker_")
    try:
        blk = extract_reconcile_block(os.path.join(d, "x.log"))
        check("wags_autofix.sh: còn marker WAGS_VERDICT_RECONCILE_BEGIN/END và bóc nháy được",
              bool(blk) and "wags_bus_verdict.py" in blk,
              "không trích được khối — marker bị xoá/đổi tên?")
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ── Ca 11: BẤT BIẾN CHỈ-NÂNG. stdout hỏng/nhiễu (INCONCLUSIVE) + bus CONFIRMED ⇒ nâng lên
#    CONFIRMED. Đây là ca replay sự cố 2026-07-08 (notify in {"status":"sent"} vào stdout).
def case_invariant_upgrade_from_bus():
    r = run_reconcile("INCONCLUSIVE", [ev(TOPIC, "2026-08-11T01:35:27Z",
                                          {"verdict": "CONFIRMED"})])
    check("chỉ-NÂNG: stdout=INCONCLUSIVE + bus=CONFIRMED ⇒ verdict thành CONFIRMED",
          r and "VERDICT=CONFIRMED" in r[1], r and r[1:3])
    check("nâng verdict có ghi dấu vết vào pipelog (người truy lại được vì sao)",
          r and "theo bus (artifact)" in r[3], r and r[3])


# ── Ca 12: BẤT BIẾN KHÔNG-HẠ. stdout=NEEDS_CHANGES + bus im lặng (không có verification)
#    ⇒ GIỮ NGUYÊN NEEDS_CHANGES. Bus im lặng = không có bằng chứng, không phải bằng chứng
#    ngược — không được tự nâng thành CONFIRMED.
def case_invariant_no_downgrade_or_selfheal_on_silence():
    r = run_reconcile("NEEDS_CHANGES", [])
    check("bus im lặng: verdict GIỮ NGUYÊN NEEDS_CHANGES (không tự chữa)",
          r and "VERDICT=NEEDS_CHANGES" in r[1], r and r[1:3])
    r2 = run_reconcile("CONFIRMED", [])
    check("bus im lặng + stdout=CONFIRMED: KHÔNG bị hạ, cũng KHÔNG báo bất đồng",
          r2 and "VERDICT=CONFIRMED" in r2[1] and "DISAGREE=\n" in r2[1], r2 and r2[1:3])


# ── Ca 13 (LỖ HỔNG ĐÃ VÁ 2026-08-12): stdout=CONFIRMED nhưng bus=NEEDS_CHANGES. Luật
#    "chỉ nâng, không hạ" canh một chiều nên ca này TỪNG đi thẳng vào ✅ HOÀN TẤT trong im
#    lặng. Yêu cầu: KHÔNG tự hạ verdict, nhưng PHẢI phát tín hiệu bất đồng (biến
#    verdict_disagree + dòng pipelog) để nhánh notify đổi ✅ thành 🟠.
def case_asymmetric_disagreement_is_reported():
    for bus_v in ("NEEDS_CHANGES", "REFUTED"):
        r = run_reconcile("CONFIRMED", [ev(TOPIC, "2026-08-11T01:35:27Z", {"verdict": bus_v})])
        check(f"stdout=CONFIRMED + bus={bus_v}: KHÔNG tự hạ verdict (giữ bất biến)",
              r and "VERDICT=CONFIRMED" in r[1], r and r[1:3])
        check(f"stdout=CONFIRMED + bus={bus_v}: CÓ phát tín hiệu bất đồng (không im lặng)",
              r and "BẤT ĐỒNG" in r[1] and bus_v in r[1], r and r[1:3])
        check(f"stdout=CONFIRMED + bus={bus_v}: bất đồng được ghi vào pipelog",
              r and "BAT DONG 2 NGUON" in r[3], r and r[3])


# ── Ca 14: 2 nguồn ĐỒNG Ý CONFIRMED ⇒ tuyệt đối không được báo bất đồng (nếu không, cảnh
#    báo mới này tự biến thành nhiễu hằng ngày — đúng thứ vừa mất 8 ngày để dọn).
def case_agreement_is_quiet():
    r = run_reconcile("CONFIRMED", [ev(TOPIC, "2026-08-11T01:35:27Z", {"verdict": "CONFIRMED"})])
    check("2 nguồn cùng CONFIRMED: KHÔNG báo bất đồng (không tạo nhiễu mới)",
          r and "VERDICT=CONFIRMED" in r[1] and "DISAGREE=\n" in r[1], r and r[1:3])
    r2 = run_reconcile("NEEDS_CHANGES", [ev(TOPIC, "2026-08-11T01:35:27Z",
                                            {"verdict": "NEEDS_CHANGES"})])
    check("2 nguồn cùng NEEDS_CHANGES: giữ nguyên, không báo bất đồng",
          r2 and "VERDICT=NEEDS_CHANGES" in r2[1] and "DISAGREE=\n" in r2[1], r2 and r2[1:3])


def main():
    print("wags_bus_verdict_selfcheck: đọc bus (A) + bất biến hoà giải verdict (B)")
    for fn in (case_latest_wins, case_latest_wins_even_when_worse,
               case_since_cutoff_blocks_stale_confirmed, case_topic_prefix_scope,
               case_event_type_must_be_verification, case_payload_as_json_string,
               case_broken_payload_is_silent_not_crash,
               case_corrupt_line_does_not_hide_later_verdict, case_missing_file,
               case_bad_argc,
               case_reconcile_markers_exist, case_invariant_upgrade_from_bus,
               case_invariant_no_downgrade_or_selfheal_on_silence,
               case_asymmetric_disagreement_is_reported, case_agreement_is_quiet):
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
