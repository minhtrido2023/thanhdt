#!/usr/bin/env python3
"""Selfcheck cho bin/wags_verdict_parse.py.

Ca 15 là ca QUAN TRỌNG NHẤT: chạy lại trên CHÍNH file log thật đã gây sự cố
2026-08-11 (không phải input tổng hợp cho khớp) — đúng yêu cầu skill close-the-loop
root-cause-B #3: "verify bằng đúng dữ liệu thật đã fail trước đó".
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wags_verdict_parse import parse_verdict_block, missing_closers  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "bin", "wags_verdict_parse.py")
FIXTURE_0811 = os.path.join(ROOT, "tests", "fixtures",
                            "verdict_20260811_missing_closer.txt")
FIXTURE_0812 = os.path.join(ROOT, "tests", "fixtures",
                            "verdict_20260812_end_marker_in_string.log")

T = "topic-x"
ok = fail = 0


def chk(label, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print("  ✅ %s" % label)
    else:
        fail += 1
        print("  ❌ %s %s" % (label, extra))


print("\n[1] JSON sạch đi thẳng, KHÔNG gắn cờ vá")
o = parse_verdict_block('{"verdict":"CONFIRMED","confidence":"high","summary":"ok"}', T)
chk("verdict=CONFIRMED", o["verdict"] == "CONFIRMED")
chk("không có parse_repaired", "parse_repaired" not in o)
chk("finding_topic tự điền", o["finding_topic"] == T)

print("\n[2] Thiếu 1 dấu } (đúng hình dạng sự cố 08-11) → cứu được")
o = parse_verdict_block(
    '{"verdict":"CONFIRMED","confidence":"high","checks":{"a":"pass","b":"pass"},'
    '"summary":"s","required_changes":[]', T)
chk("verdict cứu được = CONFIRMED", o["verdict"] == "CONFIRMED")
chk("có cờ parse_repaired", o.get("parse_repaired") == "}")
chk("giữ nguyên field lồng nhau", o["checks"]["b"] == "pass")
chk("summary nói rõ đã vá", "đã vá" in o["summary"])

print("\n[3] KHÔNG BAO GIỜ nâng verdict — NEEDS_CHANGES hỏng vẫn là NEEDS_CHANGES")
o = parse_verdict_block(
    '{"verdict":"NEEDS_CHANGES","confidence":"high","checks":{"a":"fail"},"summary":"s"', T)
chk("giữ NEEDS_CHANGES", o["verdict"] == "NEEDS_CHANGES")
chk("có cờ parse_repaired", "parse_repaired" in o)

print("\n[4] Fail-safe: chuỗi ký tự chưa đóng nháy → KHÔNG đoán, giữ INCONCLUSIVE")
o = parse_verdict_block('{"verdict":"CONFIRMED","summary":"bị cắt giữa câu', T)
chk("INCONCLUSIVE", o["verdict"] == "INCONCLUSIVE")
chk("không gắn cờ vá", "parse_repaired" not in o)
# Phủ TRỰC TIẾP guard `if in_str or esc` (arch-review coord-2026-08-12 required_change #3):
# mutation bỏ guard này SỐNG SÓT 37/0 vì `json.loads` mới là thứ chặn ở 2 assertion trên —
# tức ca 4 đang quảng cáo phủ một guard mà nó không hề chạm tới.
chk("missing_closers bỏ cuộc khi nháy kép chưa đóng",
    missing_closers('{"a":"chua dong') is None)
chk("và khi chuỗi kết thúc bằng backslash escape",
    missing_closers('{"a":"x\\') is None)

print("\n[5] Fail-safe: dấu đóng lệch loại / thừa → bỏ cuộc")
chk("lệch loại → None", missing_closers('{"a":[1,2}') is None)
chk("đóng thừa → None", missing_closers('{"a":1}}') is None)
o = parse_verdict_block('{"verdict":"CONFIRMED","a":[1,2}', T)
chk("INCONCLUSIVE", o["verdict"] == "INCONCLUSIVE")

print("\n[6] Fail-safe: verdict lạ sau khi vá → KHÔNG nhận")
o = parse_verdict_block('{"verdict":"LGTM","checks":{"a":1}', T)
chk("INCONCLUSIVE", o["verdict"] == "INCONCLUSIVE")

print("\n[7] Fail-safe: thiếu quá MAX_REPAIR dấu đóng → bỏ cuộc, không đoán")
o = parse_verdict_block('{"verdict":"CONFIRMED","a":{"b":{"c":{"d":{"e":{"f":{"g":1', T)
chk("INCONCLUSIVE (7 dấu > trần 6)", o["verdict"] == "INCONCLUSIVE")

print("\n[8] Nháy kép ESCAPE bên trong chuỗi không làm lệch bộ đếm")
o = parse_verdict_block('{"verdict":"CONFIRMED","summary":"anh ta noi \\"xong\\" roi","c":{"a":1}', T)
chk("cứu được", o["verdict"] == "CONFIRMED")
chk("nội dung escape nguyên vẹn", '"xong"' in o["summary"])

print("\n[9] Dấu ngoặc nằm TRONG chuỗi không bị tính là cấu trúc")
chk("{ trong chuỗi bị bỏ qua", missing_closers('{"a":"} ] {"}') == [])
o = parse_verdict_block('{"verdict":"REFUTED","summary":"loi o dong {x[0]}","c":{"a":1}', T)
chk("cứu được, giữ REFUTED", o["verdict"] == "REFUTED")

print("\n[10] JSON hợp lệ nhưng KHÔNG phải object (list/scalar) → INCONCLUSIVE")
chk("list", parse_verdict_block('[1,2,3]', T)["verdict"] == "INCONCLUSIVE")
chk("scalar", parse_verdict_block('"CONFIRMED"', T)["verdict"] == "INCONCLUSIVE")

print("\n[11] Khối rỗng / rác hoàn toàn → INCONCLUSIVE, không nổ")
chk("rỗng", parse_verdict_block('', T)["verdict"] == "INCONCLUSIVE")
chk("rác", parse_verdict_block('khong phai json', T)["verdict"] == "INCONCLUSIVE")

print("\n[12] Thiếu ] của mảng (không chỉ }) cũng cứu được")
o = parse_verdict_block('{"verdict":"NEEDS_CHANGES","required_changes":["a","b"', T)
chk("cứu được", o["verdict"] == "NEEDS_CHANGES")
chk("vá đúng ']}'", o.get("parse_repaired") == "]}")
chk("mảng nguyên vẹn", o["required_changes"] == ["a", "b"])

print("\n[13] CLI: không có marker VERDICT_JSON → INCONCLUSIVE (hành vi cũ, giữ nguyên)")
import tempfile  # noqa: E402
with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as f:
    f.write("arch-reviewer chạy nhưng chết giữa chừng, không in gì\n")
    tmp = f.name
r = subprocess.run([sys.executable, SCRIPT, tmp, T], capture_output=True, text=True)
o = json.loads(r.stdout)
chk("rc=0", r.returncode == 0, r.stderr[:200])
chk("INCONCLUSIVE", o["verdict"] == "INCONCLUSIVE")
chk("summary nói không in được khối", "không in được" in o["summary"])
os.unlink(tmp)

print("\n[14] CLI: file log KHÔNG TỒN TẠI → INCONCLUSIVE, không ném exception")
r = subprocess.run([sys.executable, SCRIPT, "/khong/co/that.log", T],
                   capture_output=True, text=True)
chk("rc=0", r.returncode == 0, r.stderr[:200])
chk("INCONCLUSIVE", json.loads(r.stdout)["verdict"] == "INCONCLUSIVE")

print("\n[15] ĐỐI CHỨNG THẬT — corpus 2026-08-11T05:57Z (thiếu 1 dấu đóng)")
# Nguồn chuẩn là FIXTURE TRACKED, không phải logs/ (arch-review coord-2026-08-12
# required_change #1+#2): logs/ nằm trong .gitignore:4, nên bản cũ neo vào
# logs/arch_review_20260811_055220.log tụt 37→32 assertion mà VẪN exit 0 trên bất kỳ máy
# nào không phải máy này — "test âm thầm ngừng test", đúng lớp lỗi parser sinh ra để chống.
# Thiếu corpus giờ là ĐỎ, không phải ⚠️ BỎ QUA.
if not os.path.exists(FIXTURE_0811):
    chk("corpus 08-11 phải có trong git", False,
        "thiếu %s — fixture tracked bị xoá, KHÔNG được bỏ qua im lặng" % FIXTURE_0811)
else:
    blk = open(FIXTURE_0811, encoding="utf-8").read().strip()
    # chứng minh ĐÚNG lỗi cũ vẫn tái lập được với parser NGHIÊM NGẶT
    try:
        json.loads(blk)
        strict_failed = False
    except Exception:
        strict_failed = True
    chk("json.loads nghiêm ngặt VẪN fail (tái lập được sự cố)", strict_failed)
    o = parse_verdict_block(blk, "wags-fix: coord-2026-08-11")
    chk("parser MỚI cứu ra CONFIRMED", o["verdict"] == "CONFIRMED", o.get("summary", "")[:160])
    chk("confidence=high giữ nguyên", o.get("confidence") == "high")
    chk("thiếu đúng 1 dấu '}'", o.get("parse_repaired") == "}")
    chk("khối checks nguyên vẹn", isinstance(o.get("checks"), dict) and len(o["checks"]) > 0)

print("\n[16] ĐỐI CHỨNG THẬT — corpus 2026-08-12T01:39Z (END_VERDICT nằm TRONG chuỗi JSON)")
# Sự cố: arch-reviewer trích dẫn chính chuỗi marker trong `checks.fail_silent` và
# `required_changes` ⇒ 3 dấu đóng, regex non-greedy cắt ở cái ĐẦU TIÊN ⇒ khối đứt giữa
# chuỗi ⇒ INCONCLUSIVE ⇒ question treo 4 ngày trong khi verdict còn nguyên trong log.
if not os.path.exists(FIXTURE_0812):
    chk("corpus 08-12 phải có trong git", False, "thiếu %s" % FIXTURE_0812)
else:
    raw = open(FIXTURE_0812, encoding="utf-8").read()
    chk("corpus thật có >1 dấu END_VERDICT", raw.count("<<<END_VERDICT>>>") == 3)
    # RED control tại chỗ: hành vi CŨ (non-greedy, dấu đóng ĐẦU TIÊN) phải hỏng thật
    old = re.search(r"<<<VERDICT_JSON>>>(.*?)<<<END_VERDICT>>>", raw, re.S).group(1).strip()
    try:
        json.loads(old)
        old_failed = False
    except Exception:
        old_failed = True
    chk("cách trích CŨ vẫn tái lập được lỗi (Unterminated string)", old_failed)
    r = subprocess.run([sys.executable, SCRIPT, FIXTURE_0812, "wags-fix: coord-2026-08-12"],
                       capture_output=True, text=True)
    o = json.loads(r.stdout)
    chk("parser MỚI cứu ra NEEDS_CHANGES", o["verdict"] == "NEEDS_CHANGES",
        o.get("summary", "")[:160])
    chk("confidence=high", o.get("confidence") == "high")
    chk("KHÔNG cần vá (trích đúng là đủ)", "parse_repaired" not in o)
    chk("4 required_changes nguyên vẹn", len(o.get("required_changes", [])) == 4)
    chk("ghi rõ đã dùng dấu đóng nào", "đếm từ cuối" in o.get("parse_end_marker", ""))
    chk("cờ nội bộ parse_failed KHÔNG rò ra output", "parse_failed" not in o)

print("\n[17] Không ứng viên nào parse được → giữ INCONCLUSIVE, không đoán bừa")
with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as f:
    f.write('<<<VERDICT_JSON>>>\n{"verdict":"CONFIRMED","x":"a<<<END_VERDICT>>>b\n'
            'khong bao gio dong\n<<<END_VERDICT>>>\n')
    tmp17 = f.name
o = json.loads(subprocess.run([sys.executable, SCRIPT, tmp17, T],
                              capture_output=True, text=True).stdout)
chk("INCONCLUSIVE", o["verdict"] == "INCONCLUSIVE")
chk("không gắn cờ vá", "parse_repaired" not in o)
os.unlink(tmp17)

print("\n" + "=" * 66)
print("KẾT QUẢ: %d PASS / %d FAIL" % (ok, fail))
print("=" * 66)
sys.exit(1 if fail else 0)
