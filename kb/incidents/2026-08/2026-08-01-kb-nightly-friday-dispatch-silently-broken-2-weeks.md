---
kind: incident
date: 2026-08-01
topic: kb-nightly-friday-dispatch-silently-broken-2-weeks
title: >-
  2026-08-01: kb_nightly.sh Friday/Saturday editorial dispatch silently FAILED every week
  since 2026-07-17 — 2 unescaped-quote bugs (same class as daily_retro.sh, bigger blast radius)
status: fixed
category: dispatch-orchestration
origin: >-
  2 lần sửa file thêm text tự do vào chuỗi bash double-quoted nhiều dòng mà không escape
  ký tự đặc biệt (`"` khi thêm item 5b, 2026-07-17; backtick `` ` `` khi thêm item 7,
  cũng 2026-07-17) — không có bước chạy thử đoạn code sau khi sửa
recorder: >-
  Mike, phát hiện trong lúc rà soát để làm theo yêu cầu user (thêm opus%-alert vào cùng khối
  prompt) — tự kiểm quoting của đoạn mình sắp sửa nên phát hiện luôn 2 lỗi cũ đã có sẵn
---

# 2026-08-01: kb_nightly.sh Friday/Saturday editorial dispatch broken 2 tuần liền

**Bối cảnh phát hiện:** trong lúc thêm opus-drift check (item 5c, theo yêu cầu user) vào khối
prompt Friday-dispatch của `kb_nightly.sh`, tự kiểm lại quoting của đoạn mình vừa viết (đúng bài
học vừa rút ra từ [[2026-08-01-daily-retro-quoting-bug-silent-2day-outage]]) — và phát hiện
**2 lỗi quoting CÓ SẴN từ trước**, không liên quan gì đến phần tôi thêm.

**Lưu ý quan trọng về lịch:** `DOW=$(date -u +%u)` dùng giờ UTC; block "Friday" (`DOW -eq 5`)
thực ra fire vào lần chạy cron **02:00 ICT Sáng THỨ BẢY** (= 19:00 UTC thứ Sáu), KHÔNG PHẢI sáng
thứ Sáu như tên biến/comment trong code gợi ý. Xác nhận bằng log thật: dòng "Editorial dispatch
launched" gần nhất có timestamp `2026-07-31T19:00:08Z` = đúng 02:00 ICT 2026-08-01 (hôm nay, thứ
Bảy).

**Root cause — 2 lỗi độc lập, cùng file, cùng ngày phát sinh (2026-07-17):**

1. **Item 5b (model-tier drift check, thêm khi vá sự cố fable-drift 07-17)**: text
   `hay thật sự "cực kỳ phức tạp" theo đúng` có cặp `"..."` KHÔNG escape nằm trong chuỗi
   double-quoted bao ngoài (chuỗi prompt gửi cho `dispatch.sh`). Bash đóng chuỗi ở dấu `"` đầu
   tiên, biến `cực kỳ phức tạp` (4 từ, unquoted) thành các ARGUMENT RIÊNG của lệnh
   `dispatch.sh`, rồi mở lại 1 chuỗi mới ở dấu `"` thứ hai (may mắn khớp đúng dấu đóng thật ở
   cuối). **Hệ quả**: `dispatch.sh` nhận `Mike "<đoạn đầu>" cực kỳ phức tạp "<đoạn sau>" --timeout 900`
   thay vì 1 argument prompt duy nhất — rơi vào nhánh `case "$1" in ... *) echo "ERROR: unknown
   argument '$1'"; exit 1 ;; esac` của `dispatch.sh` → **dispatch.sh EXIT 1 NGAY LẬP TỨC**, KHÔNG
   có review nào chạy.
2. **Item 7 (`kb/current_ops.md` bloat check, cũng thêm 07-17)**: dùng backtick THẬT
   `` `kb/current_ops.md` `` (định dạng markdown code) thay vì backtick escape `` \`...\` `` —
   backtick RAW bên trong chuỗi bash double-quoted = COMMAND SUBSTITUTION. Bash cố gắng
   **THỰC THI file `kb/current_ops.md` như 1 lệnh** → `Permission denied` (file tồn tại nhưng
   không có quyền exec, đúng errno EACCES).

**Bằng chứng thật từ production** (`logs/kb_nightly.log`, xuất hiện ĐỀU ĐẶN mỗi lần chạy Friday
kể từ 07-17, ví dụ 3 lần gần nhất):
```
line 747:  kb/current_ops.md: Permission denied
line 1212: kb/current_ops.md: Permission denied
line 2377: kb/current_ops.md: Permission denied
...
[2026-07-31T19:00:08Z] Editorial dispatch launched (background).
[2026-07-31T19:00:08Z] === kb_nightly DONE ===
ERROR: unknown argument 'kỳ'
```
→ **`dispatch.sh` fail ngay (rc=1)** — dòng log "Editorial dispatch launched (background)" chỉ
xác nhận lệnh ĐÃ ĐƯỢC GỌI (backgrounded), KHÔNG xác nhận nó chạy đúng. Không ai đọc lỗi này vì
job chạy nền, output đi vào cùng `kb_nightly.log`, không có post-condition check nào (đúng bug
class #3 trong `agents/Wags/audit_dispatch_content_gates_20260730.md`).

**Tác động — nghiêm trọng hơn bug daily_retro cùng ngày:** TOÀN BỘ 11 mục của review Friday/Saturday
(KNOWLEDGE.md editorial, `data_registry_audit.sh`, fable-drift check, role-scoped context drift,
`current_ops.md` bloat trim, token-saver skill audit, và **quan trọng nhất: item 11 — báo cáo
accountability bus-question hàng tuần mà user mandate ngày 2026-07-31**) **CHƯA TỪNG chạy thành
công dù chỉ 1 lần kể từ 2026-07-17** — bao gồm cả lần chạy sáng nay (2026-08-01, hôm user hỏi về
hiệu quả các cải thiện). Việc dọn backlog bus-question xuống còn 1 câu (ghi trong working memory
07-31) là do **Mike tự làm tay trong phiên sống**, không phải do cơ chế tự động này.

**Fix**: escape đúng 2 chỗ —
`\"cực kỳ phức tạp\"` (item 5b) và `` \`kb/current_ops.md\` `` (item 7).

**Verify (không chỉ đọc lại thấy hợp lý — chạy thật):**
1. `bash -n bin/kb_nightly.sh` — pass.
2. Scanner tự viết (duyệt buffer chuỗi double-quoted, tôn trọng `\`-escape) xác nhận: quote đóng
   ĐẦU TIÊN của chuỗi prompt giờ rơi đúng vị trí thật ở cuối (trước ` \` + `--timeout 900`), 0
   backtick/`$(` chưa escape còn sót.
3. Mô phỏng thật: trích đúng khối `if [ "$DOW" -eq 5 ]; then ... fi`, thay lệnh gọi
   `dispatch.sh` thật bằng 1 script Python chỉ đếm/in số lượng + nội dung argument nhận được,
   chạy với `DOW=5` ép buộc. Trước fix: `ERROR: unknown argument 'kỳ'` tái hiện CHÍNH XÁC lỗi
   production. Sau fix: nhận đúng **4 argument** (`Mike`, 1 chuỗi prompt dài 9295 ký tự, `--timeout`,
   `900`), `STDERR` rỗng hoàn toàn.

**Bài học — pattern đã lặp lại LẦN THỨ 3 trong 1 ngày (daily_retro item, kb_nightly item 5b, kb_nightly
item 7), cả 3 cùng 1 gốc: chèn text có `"`/`` ` `` vào chuỗi bash double-quoted dài mà không escape,
không chạy thử.** Đề xuất prevention cụ thể (đã nêu ở entry daily_retro, nhắc lại vì mức độ nghiêm
trọng hơn ở đây): mọi lần sửa `draft_prompt=`/chuỗi truyền cho `dispatch.sh` trong file cron-driven
(`daily_retro.sh`, `kb_nightly.sh`, `ops_autofix.sh`, `wags_autofix.sh`, `send_plan_report.sh`) —
chạy thử đoạn gán biến/scan quote CÔ LẬP trước khi commit, không chỉ đọc lại bằng mắt. Cân nhắc
thêm: 1 self-check nhỏ (`bin/dispatch_prompt_selfcheck.sh` hoặc tương tự) quét các file trên tìm
`"`/`` ` `` chưa escape bên trong chuỗi truyền cho `dispatch.sh`, chạy trong CI/pre-commit hoặc
Friday review — CHƯA làm, đề xuất cho user/Wags cân nhắc.

**Liên quan**: [[2026-08-01-daily-retro-quoting-bug-silent-2day-outage]] (cùng ngày phát hiện,
cùng lớp lỗi, script khác).
