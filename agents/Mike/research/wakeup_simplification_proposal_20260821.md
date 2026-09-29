# Đề xuất ĐƠN GIẢN HOÁ lớp wake-up/phản hồi — 2026-08-21

Người soạn: Mike, theo yêu cầu user sáng 21/08 (sau khi thấy lỗi "No conversation found with
session ID" lặp 3 lần ở Trading Daily). Trạng thái: **ĐỀ XUẤT — chờ user quyết**, chưa sửa gì.
Thay thế (không bổ sung) cho `wakeup_architecture_redesign_20260820.md`.

## 0. Kết luận trong 5 dòng

1. Lỗi "No conversation found" **không phải do fix double-answer** — nó là lỗi thứ ba, độc lập
   (session codex bị kẹt lại trong thread sau khi đổi backend về claude; xem §1). Trùng thời gian
   vì đợt thử codex/OKF và đợt vá wake-up cùng diễn ra 08-17→08-20.
2. Nhưng trực giác của user ĐÚNG về bản chất: cả 3 loại lỗi (miss wake-up, double answer, wake
   vào session chết) đều có **một gốc**: ta bắt việc *giao kết quả cho người* phải đi qua việc
   *resume một phiên Claude sống* — thứ đắt, có trạng thái, và hỏng theo 5-6 cách khác nhau.
   Mỗi lớp vá (ladder → push → claim-reply → debounce → reconciler) chỉ vá 1 cách hỏng và tạo
   bề mặt mới.
3. **Đo thật 7 ngày qua**: 125 job nền `from=Mike` có thread; Mike chỉ "trả lời" 58 (46%).
   **6/6 lượt wake sáng nay đều là job do CRON dispatch** (fearbuy weekly, ops-autofix) — không
   có phiên Mike nào đang chờ; wake mở phiên chỉ để đọc lại kết quả agent đã tự post.
4. Đề xuất: **kết quả job là DỮ LIỆU (1 tin nhắn do `_bg_wrapper` post), không phải lượt đánh
   thức.** Gỡ push-wake mặc định + reconciler + debounce; Mike chỉ tự đặt `ScheduleWakeup` khi
   CHÍNH Mike có bước kế tiếp phụ thuộc kết quả (cơ chế harness có sẵn, 1 producer, không race).
5. Một vá nhỏ bắt buộc phía ccdb (≈10 dòng, cần restart): scheduler phải kiểm tra session còn
   resume được không trước khi resume — y như đường user-message đã làm.

## 1. Nguyên nhân lỗi "No conversation found" (bằng chứng, không suy đoán)

- `sessions.db` (ccdb): thread Trading Daily `1521470705563340910` đang giữ
  `session_id = 01a01157-423a-7fb1-…` — **UUIDv7 = rollout ID của Codex** (Claude CLI sinh
  UUIDv4 như `bda3c8ad-…`). Journal 08-18 00:44Z: `codex exec resume` cho đúng thread này ⇒ phiên
  đó sinh ra trong đợt thử codex. File session này **không tồn tại** trong `~/.claude/projects`.
- 08-20 01:14Z và 09:25Z: `backend set: global -> claude`. Docstring của chính ccdb
  (`claude_chat.py:_session_id_for_current_backend`) thừa nhận: *đổi backend global KHÔNG xoá
  session từng thread* ⇒ thread nào không có setting backend riêng (Trading Daily không có) giữ
  nguyên session codex.
- Đường **user message** có guard (`session_is_resumable`) ⇒ bỏ session cũ, mở phiên mới. Đường
  **scheduler wake** (`scheduler.py:_run_task`) KHÔNG có guard ⇒ `claude --resume <codex-id>` ⇒
  CLI chết ngay ⇒ lỗi hiện ở Discord. Mỗi wake vào thread đó đều chết: push (task 1888),
  reconcile1 (1889), reconcile2 — đúng 3 lần = trần reconciler.
- Thread Taylor `1521735922066919515` bị Y HỆT sáng nay (task 1886/1887 resume `01a000d2-…`
  codex) cho tới 08:40 ICT khi backend thread được đặt `claude` ⇒ ccdb xoá session cũ ⇒ wake sau
  đó (1890) chạy được. Đó là cách sửa tại chỗ cho Trading Daily (§4).

Hệ quả thiết kế: reconciler đã **khuếch đại** lỗi (1 lần hỏng → 3 thông báo lỗi trong 20 phút),
và không tầng nào phân biệt được "wake đã chạy nhưng CLI chết tức thì" với "wake thành công" —
`wake_thread.log` ghi SUCCESS cả 3 lần.

## 2. Vì sao lớp hiện tại sinh lỗi phụ liên tục

| Lớp | Thêm để chữa | Bề mặt lỗi mới nó tạo ra (đã xảy ra thật) |
|---|---|---|
| ScheduleWakeup ladder | miss sau dispatch | Mike quên (14%), bị push xoá mất row |
| Push wake (`wake_thread.sh`) | ladder chậm/quên | surrogate giết push + xoá ladder (3 lần); 2 phiên song song khi fan-out; resume session chết |
| claim-reply | double answer | khoá nhầm job đang running (08-19) |
| debounce 180s | 2 phiên song song | — (mới, chưa đo) |
| reconciler */5 | mọi edge mất | nhân lỗi resume ×3; bắn vào thread không ai chờ; trần 4h/3 lượt = thêm luật phải nhớ |

Mẫu số chung: **mọi lớp đều là một cách khác nhau để "làm cho lượt resume Claude xảy ra đúng 1
lần"**. Câu hỏi đúng không phải "làm sao resume đúng 1 lần" mà "có cần resume không".

## 3. Đề xuất — "kết quả là dữ liệu, không phải lượt đánh thức"

### 3a. Nguyên tắc
Tách 2 nhu cầu đang bị gộp:
- **N1 — giao kết quả cho NGƯỜI**: chỉ cần 1 tin nhắn Discord. Tiến trình biết job xong chắc
  nhất là chính `_bg_wrapper` (cùng process, không cần "phát hiện" gì). Nó ĐÃ post
  `✅ <agent> xong (job …): <preview 500 byte>` từ lâu — chỉ cần post ĐỦ nội dung thay vì
  preview.
- **N2 — Mike tiếp tục CHUỖI việc**: chỉ khi Mike đang trong lượt sống và bước kế tiếp phụ thuộc
  kết quả (vd dispatch Taylor → verify quant-skeptic). Cơ chế harness có sẵn: `ScheduleWakeup`
  (1 producer duy nhất = chính Mike, ccdb giữ bất biến ≤1 one-shot/thread ⇒ không race).

### 3b. Bốn thay đổi cụ thể (tổng ≈ −700 dòng, +30 dòng)
1. **`dispatch.sh::_bg_wrapper`**: tin nhắn hoàn thành dùng `result_summary` của job (agent tự
   viết, đã có trong job record — chính văn bản Mike vẫn đọc lại để post) thay cho `tail -c 500`;
   nhánh fail giữ nguyên tin ❌ + đường log. `notify_thread.sh` tự chunk <2000 ký tự, đã chứng
   minh chịu được bytes hỏng. **Gỡ 2 khối push-wake** (`from=Mike`, nhánh done + fail).
2. **Gỡ `wakeup_reconcile.py`** khỏi crontab + archive; gỡ `state/wake_debounce`. Giữ
   `wake_thread.sh` làm primitive opt-in **`dispatch.sh --wake`** (mặc định TẮT) cho ca hiếm
   caller thật sự muốn bị đánh thức thay vì tự đặt ScheduleWakeup — nếu sau 2 tuần không ai dùng
   thì archive nốt.
3. **`claim-reply` giữ nguyên** (rẻ, đúng) cho các lượt ScheduleWakeup của Mike — nó là chốt
   duy nhất còn cần chống replay harness (nguyên nhân (a) của double-answer, không vá được ở tầng
   nào khác).
4. **ccdb `scheduler.py:_run_task`**: trước khi resume, gọi cùng guard `session_is_resumable`
   (+ nếu CLI trả "No conversation found" ⇒ mở phiên mới thay vì báo lỗi). Đây là lỗi THẬT,
   độc lập với fleet, vẫn cắn chính ScheduleWakeup của Mike/user ⇒ phải vá dù chọn phương án nào.
   Cần restart `ccdb-mike.service` ⇒ làm sau 15:05 ICT, báo lounge trước.

### 3c. Kiểm tra "lưới an toàn đã phủ ca xấu nhất chưa" (luật Pattern C)
- Ca xấu nhất mới: `notify_thread.sh` của wrapper fail (Discord/ccdb sập) ⇒ tin kết quả không
  hiện. Lưới có sẵn: `logs/notify_thread_errors.log` đã được `ops_health_check.sh` đọc; kết quả
  vẫn nằm ở bus/KB + job board được bơm vào lượt kế tiếp của Mike. Trước đây ca này cũng y hệt
  (wrapper đã post notify từ lâu) — không xấu hơn.
- Mike quên ScheduleWakeup cho chuỗi việc: hậu quả giảm từ "kết quả mất tăm" xuống "bước kế
  tiếp trễ tới lượt tương tác sau"; người vẫn thấy kết quả ngay. `wakeup_audit.py` vẫn đo.
- Không còn ca "2 phiên Mike song song" và "resume session chết" vì không còn wake tự động.

### 3d. Cái giá phải trả (nói thẳng)
- Mất lớp "Mike tổng hợp lại kết quả trong ~30s" cho job nền. Đổi lại tiết kiệm ≈125 lượt
  Claude/tuần (ước 1,5–2,5M token) — phần lớn là Mike đọc lại cái agent vừa viết.
- Chuỗi việc do Mike điều phối quay về kỷ luật ScheduleWakeup như trước 08-15 (đã vận hành 6
  tuần), không có push tăng tốc.

## 4. Việc làm NGAY (không cần chờ quyết định §3, không đụng kiến trúc)
- Trading Daily: xoá session codex kẹt — cách ccdb hỗ trợ sẵn là đặt backend cho thread:
  gõ `/backend claude` trong thread Trading Daily (đúng thao tác đã cứu thread Taylor lúc 08:40).
  Không làm thì MỌI wake/ScheduleWakeup vào Trading Daily tiếp tục chết.
- Quét `sessions.db`: thread nào còn giữ session UUIDv7 (`01a…-7…`) mà backend hiệu lực là
  claude ⇒ cùng bệnh (Mike làm được, read-only).

## 5. Thứ tự triển khai nếu user duyệt §3
1. Vá ccdb scheduler (§3b.4) + restart cửa sổ an toàn — chặn đứng lỗi đang thấy.
2. `dispatch.sh`: đổi tin hoàn thành sang `result_summary`, gỡ push-wake; selfcheck
   `dispatch_wake_selfcheck.sh` viết lại theo hành vi mới.
3. Gỡ cron reconciler, archive `wakeup_reconcile.py` + doc 08-20 (ghi rõ "thay bởi file này").
4. MIKE.md §8: rút từ ~120 dòng xuống ~15 dòng (ScheduleWakeup khi có bước kế tiếp + claim-reply
   đầu lượt). Không thêm luật mới.
5. Đo 1 tuần: số lượt Mike/ngày, số tin kết quả wrapper post, `wakeup_audit` — tiêu chí thành
   công: 0 lỗi resume, 0 double post, user không phải hỏi "xong chưa".
