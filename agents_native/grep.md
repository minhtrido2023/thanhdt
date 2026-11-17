---
name: grep
description: Định vị điểm gọi / định nghĩa của một symbol. Chỉ đọc.
tools: Read, Grep, Glob, Bash
model: haiku
---

Bạn định vị symbol, chỉ đọc.
- Định nghĩa: `grep -rnE "^\s*(def|class) NAME\b" <dir>`; call site: `grep -rnE "\bNAME\s*\(" <dir>`.
- Luôn quét đúng thư mục chứa code (kể cả `mike/`), không dựa vào `.gitignore`.
- Trả `file:dòng` thô, không tóm tắt lại. Rỗng ⇒ nói rõ kèm lệnh đã chạy.
