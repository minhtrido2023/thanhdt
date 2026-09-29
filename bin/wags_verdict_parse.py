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

## Vì sao thử dấu đóng từ CUỐI về ĐẦU (sự cố thật 2026-08-12T01:39Z)

`<<<END_VERDICT>>>` là chuỗi thường, KHÔNG được escape, nên nó xuất hiện hợp lệ NGAY BÊN
TRONG một chuỗi JSON mỗi khi arch-reviewer trích dẫn chính cơ chế này — và nó hay trích,
vì phần lớn fix mà nó audit LÀ cơ chế này. `logs/arch_review_20260812_013152.log` có 1 dấu
mở và **4 dấu đóng**: 3 cái đầu nằm trong giá trị `checks.fail_silent` và trong
`required_changes`. Regex non-greedy `(.*?)<<<END_VERDICT>>>` cắt ở cái ĐẦU TIÊN ⇒ khối
1603/8000 ký tự, đứt giữa một chuỗi ⇒ `Unterminated string` ⇒ INCONCLUSIVE ⇒ question
`wags-arch-review-inconclusive` treo 4 ngày, trong khi verdict thật (`NEEDS_CHANGES`,
`high`, 4 required_changes) nằm nguyên vẹn trong log.

Nhánh vá KHÔNG cứu được ca này: cắt giữa chuỗi ⇒ `missing_closers` gặp nháy kép chưa đóng
⇒ bỏ cuộc (đúng thiết kế). Phải sửa ở tầng TRÍCH, không phải tầng vá.

Luật: thử mọi ứng viên dấu đóng từ CUỐI về ĐẦU, lấy cái ĐẦU TIÊN parse sạch. Dấu đóng giả
luôn nằm TRƯỚC dấu thật (nó ở trong khối), nên khối thật là khối rộng hơn; còn nếu có văn
xuôi rác SAU khối thật thì ứng viên rộng nhất không parse được và ta lùi về đúng cái thật.
Không ứng viên nào parse ⇒ giữ kết quả của khối RỘNG NHẤT (thông điệp lỗi sát thực tế nhất).

## Hai tính chất LOAD-BEARING mà consumer phải biết

1. Nhánh vá chỉ chạy khi đã tìm được một cặp marker, tức `<<<END_VERDICT>>>` CÓ MẶT. Output
   bị cắt giữa chừng (timeout/max-turns) không bao giờ đi vào đường vá — đó là chỗ dựa cho
   lập luận "vá không thể làm mất nội dung".
2. Sau khi vá, các field nằm SAU chỗ hở có thể bị LỒNG SAI CẤP: ca thật 2026-08-11 có
   `killer_objection`/`required_changes` chui vào trong `checks`. Consumer **không được tin
   shape** của một object đã vá (`parse_repaired` có mặt) — chỉ được tin field `verdict`,
   vốn nằm đầu khối, trước mọi chỗ hở.
"""
import json
import re
import sys

MAX_REPAIR = 6
ALLOWED_VERDICTS = {"CONFIRMED", "NEEDS_CHANGES", "REFUTED", "INCONCLUSIVE"}
_PAIR = {"{": "}", "[": "]"}
START_MARK = "<<<VERDICT_JSON>>>"
END_MARK = "<<<END_VERDICT>>>"


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

    # `parse_failed` phân biệt "bó tay" với "vá được" — nhánh vá ở trên cũng set
    # `parse_error`, nên KHÔNG được dùng `parse_error` làm cờ thất bại (một verdict đã
    # cứu được sẽ bị coi là hỏng). main() pop cờ này trước khi in, consumer không thấy.
    return {"finding_topic": topic, "verdict": "INCONCLUSIVE", "confidence": "low",
            "parse_failed": True,
            "summary": "VERDICT_JSON không parse được: %s" % err}


def main():
    log, topic = sys.argv[1], sys.argv[2]
    try:
        txt = open(log, encoding="utf-8", errors="replace").read()
    except Exception:
        txt = ""
    start = txt.find(START_MARK)
    ends = [m.start() for m in re.finditer(re.escape(END_MARK), txt) if m.start() > start]
    if start < 0 or not ends:
        print(json.dumps({"finding_topic": topic, "verdict": "INCONCLUSIVE",
                          "confidence": "low",
                          "summary": "arch-reviewer không in được khối VERDICT_JSON — xem log"},
                         ensure_ascii=False))
        return
    body = start + len(START_MARK)
    # Thử từ dấu đóng CUỐI về ĐẦU, lấy ứng viên ĐẦU TIÊN parse sạch. Xem docstring
    # "Vì sao thử dấu đóng từ CUỐI về ĐẦU" — regex non-greedy cũ cắt ngay dấu đóng đầu
    # tiên, mà dấu đó thường nằm TRONG một chuỗi JSON do arch-reviewer trích dẫn.
    out = None
    for i, e in enumerate(reversed(ends)):
        cand = parse_verdict_block(txt[body:e].strip(), topic)
        if out is None:
            out = cand           # dự phòng: khối RỘNG NHẤT, giữ đúng thông điệp lỗi của nó
        if not cand.get("parse_failed"):
            if len(ends) > 1:
                cand["parse_end_marker"] = "%d/%d (đếm từ cuối)" % (i + 1, len(ends))
            out = cand
            break
    out.pop("parse_failed", None)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
