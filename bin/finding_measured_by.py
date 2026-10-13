#!/usr/bin/env python3
"""Cổng `measured_by` cho event `finding` — CHỈ CẢNH BÁO, KHÔNG BAO GIỜ CHẶN.

Được `append_event.sh` gọi SAU KHI event gốc đã nằm trên bus. Đọc đúng dòng event vừa ghi
từ stdin; nếu finding có số mà thiếu `measured_by` thì (1) in 1 dòng ra stderr cho agent
thấy ngay lúc ghi và (2) nối 1 bản ghi vào `bus/_measured_by_warn.jsonl`.

LUẬT CƠ HỌC (RULE_VERSION=1) — không có phán đoán nào khác ngoài 3 mệnh đề dưới:

  ĐƯỢC XÉT  ⇔ event_type == "finding" VÀ payload là JSON object (dict).
              Payload là chuỗi / mảng: KHÔNG xét (không có chỗ đặt trường).

  CÓ SỐ     ⇔ trong CÁC GIÁ TRỊ của payload (đệ quy; KHÔNG xét tên khoá, KHÔNG xét topic)
              có ít nhất một trong:
              (a) một giá trị JSON kiểu số (int/float; true/false KHÔNG tính), hoặc
              (b) một chuỗi mà sau khi bỏ các "mã tham chiếu" vẫn còn token số.
              Xét từng từ (cách nhau bởi khoảng trắng), theo đúng thứ tự:
                1. bỏ hậu tố đơn vị `/<chỉ chữ cái>` (kèm dấu câu `.,;:!?)]` theo sau) ở cuối từ:
                   `23,37%/năm` → `23,37%`, `3,5%/năm,` → `3,5%`
                2. BỎ NGUYÊN TỪ nếu còn `/` kèm chữ cái ASCII (đường dẫn, tên nhánh) hoặc có
                   tên file `x.py`, `x.json`…
                3. xoá ngày `12/10`, `12/10/2026` (ngày ≤31, tháng ≤12) và giờ `08:23`, `08:23:05`
                4. tìm token số trong phần còn lại.
              Token số = dãy chữ số (kèm dấu +/-, phần thập phân `.`/`,`, `%`) KHÔNG dính
              liền chữ cái/`_`, KHÔNG đứng sau `.` `,` `:` `#` `§` `-`, và KHÔNG đứng ngay
              trước chữ cái, `-<chữ số>` hay `.`/`,`+chữ số ⇒ không tính: `r2`, `T5`, `v3.4b`,
              `2.5x`, `1.2e6`, `§23`, `#5`, `10-12`, `06-15..06-30`. Cũng nhờ mệnh đề này mà
              ngày ISO `2026-10-12T01:09:31Z`, job id `Taylor_20261012_124854`, mã commit
              `a1b2c3d4` tự rơi ra — không cần luật riêng.
              HỆ QUẢ CHẤP NHẬN (phần lớn có ca ghim trong append_event_selfcheck.py, bảng
              `exact`; riêng "tham số thiết kế" và "số tài khoản" thì không):
                · ÂM TÍNH GIẢ: số dính đơn vị/chữ (`2.5x`, `1.5tỷ`, `+480/-611dòng`); CẢ
                  khoảng `0.2-0.5`; tỉ số trùng dạng ngày (`9/9`, `25/12`); số nằm trong từ có
                  `/` kèm chữ (`P/E=12.5`, `(pass=27/fail=0)`); dấu trừ Unicode `−` bị rơi.
                · DƯƠNG TÍNH GIẢ: mã THUẦN SỐ (số tài khoản, `HTTP 401`), tham số thiết kế
                  (`45 ngày`), ngày viết `12.10.2026` hay `2026/10/12`.

  ĐÃ KHAI   ⇔ payload có khoá CẤP CAO NHẤT tên ĐÚNG `measured_by` với giá trị không rỗng
              (chuỗi khác rỗng sau strip, hoặc list/dict khác rỗng). `measured_by` đặt lồng
              cạnh con số, hay viết `measuredBy`, KHÔNG được tính.

  CẢNH BÁO  ⇔ ĐƯỢC XÉT ∧ CÓ SỐ ∧ ¬ĐÃ KHAI.

ĐO TRƯỚC KHI BẬT (finding thật của bus 2026-09-29→2026-10-13): số liệu, 24 ca soi tay và
lệnh tái lập nằm ở `agents/Wags/research/measured_by_20261013/` — không chép vào đây để khỏi
lệch. Điều cần biết khi đọc cảnh báo: luật này bắt GẦN NHƯ MỌI finding (finding nào cũng có
số), nên nó là lời nhắc "khai nguồn số", không phải bộ lọc tìm finding đáng ngờ.

GIỚI HẠN — nói thẳng: cổng này chỉ ép KHAI nguồn. Nó KHÔNG chạy lại lệnh, KHÔNG mở file,
KHÔNG chứng minh con số đúng. `"measured_by": "abc"` là đủ để nó im.

VÌ SAO FILE CẠNH BUS CHỨ KHÔNG PHẢI EVENT: mọi reader của bus glob `bus/inbox/*.jsonl`
(consolidate.sh → mục "MỚI NHẤT" của context_pack). Cảnh báo dạng event sẽ (1) ngập context
của cả fleet, (2) tự kích lại chính cổng này nếu là finding, (3) thành việc cho
ops_health_check nếu là question. `bus/_measured_by_warn.jsonl` theo đúng tiền lệ
`bus/_rejected.jsonl`: nằm trên bus, không reader nào nuốt, không thể đệ quy.
KHÔNG có reader tự động nào đọc file này (cố ý — không đẩy việc cho ai); muốn xem thì mở tay.
CHƯA được rotate: fleet_housekeeping.sh chỉ rotate `_rejected.jsonl` (đo 2026-10-13: ~5,8 KB/ngày,
tức ~2 MB/năm) — thêm vào rotate là việc theo sau, phải kèm selfcheck cho script đó.

Exit code LUÔN 0 (kết thúc bằng os._exit(0) sau khi flush có bọc lỗi — stderr hỏng cũng không
đổi được rc). Mọi ngoại lệ bị nuốt: thà mất 1 cảnh báo còn hơn làm phiền đường ghi.
"""
import json
import os
import re
import sys
import time

RULE_VERSION = 1

_FILE_RE = re.compile(r"\.(?:py|sh|json|jsonl|md|csv|txt|log|html|sql|yaml|yml|toml)\b")
_REF_RE = re.compile(
    r"\b(?:0?[1-9]|[12]\d|3[01])/(?:0?[1-9]|1[0-2])(?:/\d{2,4})?\b"  # ngày d/m[/y]
    r"|\b\d{1,2}:\d{2}(?::\d{2})?\b"                             # giờ HH:MM[:SS]
)
_NUM_RE = re.compile(r"(?<![\w.,:#§-])[+-]?\d+(?:[.,]\d+)*%?(?!\w|-\d|[.,]\d)")
_UNIT_SUFFIX_RE = re.compile(r"/[^\W\d_]+[.,;:!?)\]]*$")
_HAS_ALPHA_RE = re.compile(r"[A-Za-z]")
_MAX_SAMPLES = 5


def _values(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _values(v)
    elif isinstance(x, list):
        for v in x:
            yield from _values(v)
    else:
        yield x


def number_tokens(payload, limit=_MAX_SAMPLES):
    """Tối đa `limit` token số tìm được trong các GIÁ TRỊ của payload (rỗng = không có số)."""
    found = []
    for v in _values(payload):
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            found.append(repr(v))
        elif isinstance(v, str):
            for word in v.split():
                word = _UNIT_SUFFIX_RE.sub("", word)
                if ("/" in word and _HAS_ALPHA_RE.search(word)) or _FILE_RE.search(word):
                    continue
                found.extend(_NUM_RE.findall(_REF_RE.sub(" ", word)))
                if len(found) >= limit:
                    break
        if len(found) >= limit:
            break
    return found[:limit]


def has_measured_by(payload):
    mb = payload.get("measured_by")
    if isinstance(mb, str):
        return bool(mb.strip())
    if isinstance(mb, (list, dict)):
        return bool(mb)
    return False


def verdict(event):
    """Trả list token mẫu nếu PHẢI cảnh báo, ngược lại None."""
    if not isinstance(event, dict) or event.get("event_type") != "finding":
        return None
    payload = event.get("payload")
    if not isinstance(payload, dict) or has_measured_by(payload):
        return None
    return number_tokens(payload) or None


def main(argv):
    # Đọc BYTE rồi tự giải mã UTF-8: không phụ thuộc locale của caller (cron hay chạy LC_ALL=C).
    event = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    samples = verdict(event)
    if not samples:
        return
    topic = str(event.get("topic", ""))[:200]
    shown = ", ".join(s[:24] for s in samples)
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "warn": "finding_missing_measured_by", "rule_version": RULE_VERSION,
           "agent_id": str(event.get("agent_id", ""))[:80], "topic": topic,
           "event_id": event.get("event_id"), "trace_id": event.get("trace_id"),
           "sample_numbers": [s[:24] for s in samples]}
    try:
        if len(argv) > 1:
            # ensure_ascii=True: 1 dòng thuần ASCII, không phụ thuộc locale của caller.
            with open(argv[1], "a", encoding="ascii") as f:
                f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    finally:
        sys.stderr.write(
            "append_event.sh: [CẢNH BÁO — KHÔNG chặn, event ĐÃ ghi, ĐỪNG gửi lại] finding '%s' "
            "có số (vd %s) nhưng payload thiếu \"measured_by\" ở CẤP CAO NHẤT. Lần sau khai "
            "\"measured_by\":\"<lệnh đã chạy | file chứa số>\"; số CHƯA đo thì ghi rõ "
            "\"ước lượng\".\n" % (" ".join(topic.split()), shown))


if __name__ == "__main__":
    try:
        main(sys.argv)
    except BaseException:  # noqa: BLE001 — fail-open tuyệt đối, kể cả SystemExit/KeyboardInterrupt
        pass
    try:
        sys.stderr.flush()
    except BaseException:  # noqa: BLE001 — stderr hỏng (/dev/full, pipe đóng) không được đổi rc
        pass
    os._exit(0)
