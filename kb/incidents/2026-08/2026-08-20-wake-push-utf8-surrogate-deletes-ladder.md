# 2026-08-20 — Push wake-on-completion chết im lặng vì UTF-8 surrogate, còn XOÁ mất ladder đang chờ

**Phát hiện**: user (John Dinh) tự thấy job `Taylor_20260820_015520` báo done ~12 phút mà thread
Maintenance (1539659365324169287) không phản hồi. Không cơ chế giám sát nào của fleet phát hiện.

## Timeline (ICT, 2026-08-20)
- 10:41:56 — phiên Mike ở thread Maintenance kết thúc lượt poll, đặt ScheduleWakeup ladder
  (one-shot `wakeup-thread-1539659365324169287` pending trong tasks.db).
- 10:44:50 — job Taylor xong (`status=done`, kết quả đầy đủ trên bus + logfile).
- 10:44:53 — `_bg_wrapper` gọi `notify_thread.sh` (✅ tin nhắn hiển thị — HTTP 200, tới nơi).
- 10:44:54 — `_bg_wrapper` gọi `wake_thread.sh` → ccdb `POST /api/tasks`:
  1. Server **XOÁ trước** one-shot đang pending của thread (log: "Cancelled 1 pending
     one-shot wakeup(s)") — đúng thiết kế "tối đa 1 one-shot/thread".
  2. INSERT task mới **CHẾT**: `'utf-8' codec can't encode character '\udc91' in position
     408: surrogates not allowed`.
  3. Handler `except Exception` dán nhãn NHẦM thành `409 Task name already exists`.
- 10:44:54 — `wake_thread.sh` ghi "HTTP 409" vào `logs/wake_thread_errors.log`, exit 1, bị
  `|| true` trong dispatch.sh nuốt. **Không ai đọc file log này** (comment header nói
  ops_health_check.sh đọc — SAI, đã kiểm chứng grep toàn bin/).
- 10:44 → 10:56 — thread không còn BẤT KỲ wakeup nào pending (push chết + ladder đã bị xoá
  ở bước 1). Ngủ vô hạn.
- 10:56 — user hỏi Mike ở thread khác; Mike tra job board + tasks API, wake tay thành công
  (task 1836), thread sống lại trong ~30s và post kết quả thật.

## Root cause chain (5 lớp cộng hưởng)
1. **`tail -c 500` cắt theo BYTE** (dispatch.sh `_preview`) — chém đôi ký tự UTF-8 nhiều byte
   (tiếng Việt/emoji ✓). Bash truyền byte hỏng vào argv.
2. Python `sys.argv` decode bằng **surrogateescape** → lone surrogate `\udc91`. `json.dumps`
   escape được (ASCII-safe) nên request HTTP đi qua trót lọt — lỗi chỉ nổ ở tầng sqlite ccdb.
3. **ccdb delete-then-insert KHÔNG atomic** (`delete_pending_one_shot_by_thread` rồi mới
   `create`, 2 transaction rời) — insert fail thì cái delete KHÔNG rollback ⇒ hành vi thực tế
   là "phá lưới an toàn cũ rồi chết", tệ hơn cả không làm gì.
4. **Misclassified error**: `except Exception` → "Task name already exists" cho MỌI lỗi insert
   ⇒ 3 sự cố cùng gốc bị chẩn đoán sai hướng (đi tìm race trùng tên task).
5. **Fail-soft không có tầng đọc lỗi**: `wake_thread_errors.log` không có checker nào giám sát
   ⇒ silent-failure đúng nghĩa (vi phạm tinh thần §14 coding_guidelines).

## Tái diễn — cùng chữ ký, 3 lần trong 5 ngày (journalctl ccdb-mike)
- 2026-08-15 11:20:58 — `positions 66-67` (job Taylor_20260815_034407, plan channel)
- 2026-08-19 19:16:20 — `\udca5` (job DollarBill_20260819_120605, plan channel)
- 2026-08-20 10:44:54 — `\udc91` (job Taylor_20260820_015520, Maintenance — ca duy nhất
  user-visible vì đúng lúc không có ladder dự phòng nào khác sống)

## Fix
- **ĐÃ VÁ (commit `886d9158`, cùng ngày)**: sanitize `prompt`/`name_suffix` bằng
  `encode("utf-8","replace")` trong `wake_thread.sh` — choke-point cho mọi caller, không cần
  restart ccdb. Selfcheck `wake_thread_selfcheck.py` 14/14 PASS. Sửa luôn comment header sai.
- **ĐỀ XUẤT (chưa wire — chờ duyệt)**: 4 fix kiến trúc còn lại, xem
  `agents/Mike/research/wakeup_architecture_redesign_20260820.md` — quan trọng nhất là
  **reconciler level-triggered** đóng CẢ class "mất tín hiệu edge" thay vì vá từng edge.

## Bài học
1. **Mọi tín hiệu wake hiện tại đều edge-triggered** — mất cạnh (push chết, ladder bị xoá,
   quên đặt) = im lặng vô hạn. Fleet đã có sẵn pattern level-triggered đúng
   (`resume_pending.py`, `jobs.sh reap`) nhưng chưa áp cho khâu GIAO KẾT QUẢ.
2. **Cắt chuỗi hiển thị phải cắt theo KÝ TỰ, không theo BYTE** khi chuỗi đi tiếp vào tầng khác
   (API/DB). `tail -c` trên text UTF-8 là mẫu lỗi lint-được (ứng viên gate cơ học §15-style).
3. **Delete-then-insert giữ bất biến phải nằm trong MỘT transaction** — không thì lỗi insert
   biến "thay thế" thành "phá hủy".
4. **Catch-all except + message cố định = chẩn đoán sai có hệ thống** — 409 phải dành riêng
   IntegrityError; lỗi khác trả 500 kèm class name (khớp §28: so GIÁ TRỊ chuẩn hoá, đừng suy
   từ nhãn).
5. Comment "X giám sát Y" phải kiểm chứng như code — câu sai trong header đã che lỗ hổng
   giám sát 5 ngày.
