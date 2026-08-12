#!/usr/bin/env python3
"""Đọc khối VERDICT_JSON trong log arch-reviewer → in 1 dòng JSON verdict chuẩn.

Tách khỏi heredoc trong `wags_autofix.sh` (2026-08-12) vì logic đã đủ phức tạp để CẦN
selfcheck: xem `wags_verdict_parse_selfcheck.py`.

## Vì sao có nhánh VÁ DẤU ĐÓNG

Sự cố thật 2026-08-11T05:57Z: arch-reviewer audit fix `suppress_days` và kết luận
`"verdict": "CONFIRMED", "confidence": "high"` — nhưng khối JSON nó in ra THIẾU ĐÚNG MỘT
dấu `}` (object `"checks"` mở ở char 660 không bao giờ đóng; dấu `}` cuối cùng bị dùng để
đóng `checks`, để hở object ngoài cùng). `json.loads` ném "Expecting ',' delimiter: line 1
column 4101" ⇒ verdict rơi về INCONCLUSIVE ⇒ pipeline post question
`wags-arch-review-inconclusive` ⇒ người phải đọc lại log tay mới biết fix ĐÃ được duyệt.

Đây đúng dạng lỗi skill `close-the-loop` root-cause-B: **hỏng đường ĐỌC kết quả bị trình bày
y như kết quả xấu**. Verdict nằm ngay đầu khối, TRƯỚC vùng hỏng — cứu được mà lại vứt đi.

## Vì sao vá theo kiểu này thì an toàn

Phép vá CHỈ ĐƯỢC PHÉP **thêm dấu đóng vào cuối** (`}`/`]`) theo đúng thứ tự stack cấu trúc.
Không sửa, không xoá, không chèn vào giữa một ký tự nào ⇒ **không thể** biến một
`NEEDS_CHANGES` có sẵn thành `CONFIRMED`: field `verdict` được đọc nguyên văn như tác giả
đã ghi. Ngoài ra còn 3 chốt chặn:
  - trần `MAX_REPAIR` dấu đóng — hỏng nặng (output bị cắt giữa chừng) thì bỏ cuộc, không đoán;
  - verdict sau khi vá phải nằm trong `ALLOWED_VERDICTS`, lạ → giữ INCONCLUSIVE;
  - kết quả vá được gắn cờ `parse_repaired`/`parse_error` để người đọc bus phân biệt được
    "CONFIRMED sạch" với "CONFIRMED cứu từ JSON hỏng" — không giấu việc đã phải vá.
"""
import json
import re
import sys

MAX_REPAIR = 6
ALLOWED_VERDICTS = {"CONFIRMED", "NEEDS_CHANGES", "REFUTED", "INCONCLUSIVE"}
_PAIR = {"{": "}", "[": "]"}


def missing_closers(s):
    """Dãy dấu đóng còn thiếu ở CUỐI chuỗi, theo đúng thứ tự stack.

    Trả None nếu chuỗi không thể cứu bằng cách chỉ-thêm-dấu-đóng: đang dở một chuỗi ký tự
    (nháy kép chưa đóng ⇒ có thể mất nội dung thật, không được đoán), hoặc có dấu đóng thừa
    / lệch loại (cấu trúc sai từ giữa, thêm ở cuối không sửa được).
    """
    stack = []
    in_str = esc = False
    for ch in s:
        if esc:
            esc = False
            continue
        if in_str:
            if ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in _PAIR:
            stack.append(ch)
        elif ch in ("}", "]"):
            if not stack or _PAIR[stack.pop()] != ch:
                return None
    if in_str or esc:
        return None
    return [_PAIR[c] for c in reversed(stack)]


def parse_verdict_block(raw, topic):
    """raw = nội dung giữa 2 marker (đã strip). Trả dict verdict đã chuẩn hoá."""
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            obj.setdefault("finding_topic", topic)
            return obj
        err = "khối VERDICT_JSON không phải object JSON"
    except Exception as e:
        err = str(e)

    closers = missing_closers(raw)
    if closers is not None and 0 < len(closers) <= MAX_REPAIR:
        try:
            obj = json.loads(raw + "".join(closers))
        except Exception:
            obj = None
        if isinstance(obj, dict) and obj.get("verdict") in ALLOWED_VERDICTS:
            obj.setdefault("finding_topic", topic)
            obj["parse_repaired"] = "".join(closers)
            obj["parse_error"] = err
            obj["summary"] = ("%s [JSON arch-reviewer THIẾU %d dấu đóng, đã vá bằng cách chỉ "
                              "thêm '%s' vào cuối — verdict đọc nguyên văn, không suy diễn; "
                              "lỗi gốc: %s]" % (obj.get("summary", ""), len(closers),
                                                "".join(closers), err))
            return obj

    return {"finding_topic": topic, "verdict": "INCONCLUSIVE", "confidence": "low",
            "summary": "VERDICT_JSON không parse được: %s" % err}


def main():
    log, topic = sys.argv[1], sys.argv[2]
    try:
        txt = open(log, encoding="utf-8", errors="replace").read()
    except Exception:
        txt = ""
    m = re.search(r"<<<VERDICT_JSON>>>(.*?)<<<END_VERDICT>>>", txt, re.S)
    if not m:
        print(json.dumps({"finding_topic": topic, "verdict": "INCONCLUSIVE",
                          "confidence": "low",
                          "summary": "arch-reviewer không in được khối VERDICT_JSON — xem log"},
                         ensure_ascii=False))
        return
    print(json.dumps(parse_verdict_block(m.group(1).strip(), topic), ensure_ascii=False))


if __name__ == "__main__":
    main()
