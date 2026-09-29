# Đề xuất kiến trúc wake-up/phản hồi toàn diện — 2026-08-20

Người soạn: Mike (theo yêu cầu user cùng ngày, sau sự cố thread Maintenance ngủ 12 phút).
Trạng thái: **ĐỀ XUẤT** — mục Phase 0 đã tự vá (trong thẩm quyền ops-autofix), Phase 1-3 chờ
user/Wags + arch-reviewer duyệt trước khi wire.

## 1. Chẩn đoán hệ thống — vì sao lỗi cứ phát sinh

### 1a. Kiến trúc hiện tại: 4 cơ chế, TẤT CẢ đều edge-triggered

| Cơ chế | Bản chất | Mất tín hiệu khi nào |
|---|---|---|
| Push wake-on-completion (`wake_thread.sh`) | 1 phát bắn lúc job xong | API lỗi, encoding hỏng, ccdb đang restart |
| ScheduleWakeup ladder | 1 phát bắn theo hẹn giờ | Mike quên đặt (~23% lượt, đo lại 08-17), bị `delete_pending_one_shot_by_thread` xoá, ccdb mất row |
| `resume_pending.py` (cron 10') | level-triggered NHƯNG chỉ cho usage-limit/max-turns | Không phủ khâu "job xong rồi mà không ai post kết quả" |
| CronCreate one-shot trong phiên | 1 phát bắn, session-only | Mike restart là mất |

**Định luật của 3 tháng sự cố**: mọi sự cố wake-up (07-02 bg chết theo session, 07-20 quên
ladder, 08-17 double-answer, 08-15/19/20 push surrogate) đều là MỘT dạng: **cạnh (edge) bị mất
hoặc bắn đúp, và không có tầng nào so "trạng thái mong muốn vs thực tế" để tự sửa**. Ba tháng
qua ta phản ứng bằng cách THÊM edge (ladder → push → claim-reply) — mỗi edge mới lại sinh race
mới (double-answer chính là hệ quả của 2 producer edge). Trong khi đó, các khâu đã ổn định của
fleet (`resume_pending.py`, `jobs.sh reap`, `ops_autofix.sh`) đều ổn vì chúng là
**reconciler level-triggered**: cron quét bất biến bị vi phạm rồi tự sửa, mất bao nhiêu edge
cũng chỉ trễ ≤ 1 chu kỳ cron.

### 1b. Ba lỗ hổng cụ thể còn mở (bằng chứng thật, không suy đoán)

1. **Chuỗi encoding 3 tầng cho payload không cần thiết**: log agent (bytes) → `tail -c 500`
   (cắt byte, sinh UTF-8 gãy) → bash argv → Python surrogateescape → JSON → sqlite. Sự cố
   surrogate là hệ quả tất yếu; đã vá sanitize (commit `886d9158`) nhưng THIẾT KẾ vẫn mong manh
   — wake prompt không cần chở preview nội dung; claim-reply + job record đã chứa mọi thứ.
2. **ccdb `POST /api/tasks`: delete-then-insert không atomic + catch-all 409**: insert fail thì
   lưới cũ đã bị xoá (phá hoại thay vì thay thế); mọi lỗi bị dán nhãn "Task name already
   exists" (3 lần chẩn đoán sai hướng).
3. **Không có giám sát nào cho chính hệ wake**: `wake_thread_errors.log` không checker nào đọc;
   `tasks.db` xoá row one-shot sau khi chạy nên không còn sổ audit (Wags 08-17 đã chỉ ra:
   sqlite_sequence 1739 nhưng max(id) 1732); wakeup_audit.py có bug detector substring (đếm cả
   notify nói VỀ dispatch).

## 2. Kiến trúc đề xuất — nguyên tắc "edge để NHANH, level để ĐÚNG"

Giữ nguyên push + ladder (tốc độ ~30s là giá trị thật, đã đo). Thêm MỘT tầng reconciler làm
nguồn sự thật cuối cùng, và làm cứng 2 điểm gãy đã biết. Mọi lỗi edge từ nay — kể cả lỗi CHƯA
BIẾT — suy biến thành "trễ ≤ 5 phút" thay vì "im lặng vô hạn".

### Phase 0 — hotfix (ĐÃ XONG cùng ngày, commit `886d9158`)
Sanitize UTF-8 tại `wake_thread.sh` (choke-point mọi caller) + sửa comment giám sát sai.
Selfcheck 14/14 PASS. Chặn đứng nguyên class lỗi surrogate mà KHÔNG cần restart ccdb.

### Phase 1 — `bin/wakeup_reconcile.py` (cron */5, ~60 dòng) — TÂM ĐIỂM ĐỀ XUẤT
Bất biến cần cưỡng chế: *"Mọi job terminal `from=Mike` có `discord_thread_id`, chưa
`replied_at`, xong quá N phút ⇒ thread đó PHẢI có ≥1 one-shot wakeup pending hoặc session đang
running."*

Mỗi 5 phút: quét `bus/jobs/*.json` (terminal, from=Mike, chưa replied, ended_at > 3'), đối
chiếu `tasks.db` (read-only) + `/api/sessions` — thiếu wakeup và session idle ⇒ gọi
`wake_thread.sh` lại (prompt template chuẩn §8.4, an toàn tuyệt đối vì claim-reply đã idempotent
— bắn thừa chỉ tốn 1 lượt claim exit-1). Đồng thời: đếm dòng mới trong
`wake_thread_errors.log` ⇒ có dòng mới thì notify Trading Daily (đóng lỗ hổng "log không ai
đọc" bằng đúng 1 consumer).

- Tái dùng nguyên pattern `resume_pending.py` (cùng cadence, cùng phong cách fail-safe).
- KHÔNG đụng dispatch.sh/executor — thuần đọc + gọi script có sẵn. Rollback = xoá 1 dòng cron.
- Đăng ký `kb/cron_registry.md` theo §11 trước khi cài.

### Phase 2 — thu gọn payload wake (đổi 1 biến trong dispatch.sh)
Wake prompt bỏ `$_preview`, chỉ giữ template §8.4 + job_id + status ("kết quả đọc từ
`jobs.sh status` + logfile"). Preview NGƯỜI đọc vẫn nguyên ở `notify_thread.sh` (kênh hiển
thị, đã chứng minh chịu được bytes hỏng). Ít tầng encoding hơn = ít mặt cắt hỏng hơn; nội dung
không mất vì lượt wake nào cũng phải đọc job record thật trước khi post (luật §8.3 sẵn có).

### Phase 3 — vá ccdb bridge (cần restart service → cần user duyệt + né giờ giao dịch)
1. `task_repo`: gộp delete+insert một-shot vào **một transaction** (method mới
   `replace_thread_one_shot`) — insert fail thì delete tự rollback, không bao giờ "phá lưới
   rồi chết".
2. `api_server.create_task`: bắt riêng `IntegrityError` → 409; mọi lỗi khác → 500 kèm tên
   exception (hết misdiagnosis). Sanitize surrogate server-side (phòng producer khác ngoài
   wake_thread.sh).
3. (tuỳ chọn, rẻ) bảng `task_audit` append-only ghi mỗi lần one-shot fire — trả lại khả năng
   audit mà Wags 08-17 kết luận là đã mất.

### Phase 4 — đo lường (không chặn, chỉ nhìn)
- Sửa detector `wakeup_audit.py` theo phát hiện của Wags (anchor lời gọi, hết false-positive).
- `daily_retro.sh` thêm 2 số: push success-rate (SUCCESS vs errors trong wake logs) + số lần
  reconciler phải cứu. Reconciler cứu >0 lần/tuần = còn bug edge ở đâu đó cần tìm.

## 3. Những gì CỐ Ý không đề xuất
- **Không thêm cơ chế wake thứ 5** — vấn đề là thiếu reconciliation, không phải thiếu edge.
- **Không bỏ ladder** ("đã có push") — MIKE.md §8 đã cấm đúng; push vừa chứng minh nó chết được.
- **Không auto-retry trong wake_thread.sh** — user mandate 2026-08-03 (ưu tiên quan sát tự
  nhiên hơn auto-recovery); reconciler 5' đã là retry có kỷ luật rồi.
- **Không đổi claim-reply** — nó đang đúng (kể cả exit-3 fix 08-19); reconciler dựa hẳn vào nó.

## 4. Thứ tự triển khai đề xuất & tiêu chí thành công
| Bước | Ai | Điều kiện | Verify |
|---|---|---|---|
| Phase 0 | Mike (đã xong) | — | selfcheck 14/14 ✔, đã commit |
| Phase 1 | Wags code + arch-reviewer audit | user gật đầu đề xuất này | selfcheck giả lập 3 ca thật (surrogate-kill, quên ladder, ccdb restart) đều được cứu ≤1 chu kỳ |
| Phase 2 | cùng PR Phase 1 | như trên | 1 job thật end-to-end: wake không preview vẫn post đủ kết quả |
| Phase 3 | Mike sửa + test, restart ngoài giờ giao dịch, báo lounge trước | user duyệt riêng (đụng service dùng chung) | test transaction rollback + 409-vs-500; các session sống không mất lượt |
| Phase 4 | Wags | sau Phase 1 | số liệu xuất hiện trong daily retro |
