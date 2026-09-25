#!/usr/bin/env python3
"""Đọc payload từ stdin; exit 0 nếu là JSON hợp lệ, ngược lại in ra stderr lỗi parser
THẬT + một chẩn đoán ĐO ĐƯỢC (không đoán) rồi exit 1.

Vì sao tách khỏi `append_event.sh` (2026-09-25, job Winston_20260925_012008): dòng gợi ý
cũ nằm inline trong die-message và quy CHỤP mọi lỗi 'Expecting'/'Unterminated' là "cụt thật
(word-split hoặc bị cắt)". Ca Taylor 2026-09-24T06:13:45Z phản chứng: payload đủ 2452 ký tự,
argc=5 (KHÔNG word-split), kết thúc đúng `"}`, lỗi thật chỉ là THIẾU 1 dấu `}` — gợi ý cũ đẩy
người xử lý đi tìm word-split không tồn tại. Đây là lần thứ 2 cùng hình thái trên chính guard
này (lần 1: 2026-08-28, commit 55b3f34c, ca 'Extra data' bị gọi là "cắt cụt") ⇒ thay văn xuôi
phỏng đoán bằng phép ĐẾM trên chính payload (coding_guidelines §29).

Bit cơ khí phân biệt 4 ca: chuỗi còn mở ở cuối (cắt giữa chuỗi) · mở > đóng (thiếu dấu đóng) ·
đóng > mở (thừa dấu đóng) · cân bằng (lỗi cú pháp bên trong).
"""
import json
import sys


def diagnose(src):
    opens = closes = 0
    in_str = False
    esc = False
    for ch in src:
        if esc:
            esc = False
            continue
        if ch == '\\':
            if in_str:
                esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in '{[':
            opens += 1
        elif ch in ']}':
            closes += 1
    if in_str:
        return ("CHUỖI CHƯA ĐÓNG ở cuối payload (mở %d dấu cấu trúc, đóng %d) ⇒ payload bị CẮT "
                "giữa chuỗi — word-split hoặc bị truncate, KHÔNG phải lệch ngoặc." % (opens, closes))
    if opens > closes:
        return ("THIẾU %d dấu đóng }/] — mở %d, đóng %d, ký tự cuối là %r ⇒ JSON viết tay lệch "
                "ngoặc; payload KHÔNG cụt giữa chuỗi." % (opens - closes, opens, closes, src[-1:]))
    if closes > opens:
        return ("THỪA %d dấu đóng }/] — mở %d, đóng %d ⇒ JSON viết tay lệch ngoặc; payload KHÔNG cụt."
                % (closes - opens, opens, closes))
    return ("Dấu cấu trúc CÂN (mở %d = đóng %d) và mọi chuỗi đều đóng ⇒ lỗi ở cú pháp bên trong "
            "(thiếu dấu phẩy/hai chấm, nháy đơn thay vì nháy kép), KHÔNG phải cụt." % (opens, closes))


def main():
    src = sys.stdin.read()
    try:
        json.loads(src)
    except ValueError as exc:
        sys.stderr.write("%s\n  Chẩn đoán ĐO ĐƯỢC: %s" % (exc, diagnose(src)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
