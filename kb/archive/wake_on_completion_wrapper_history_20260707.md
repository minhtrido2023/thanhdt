# Lịch sử cơ chế `Agent(run_in_background)` wrapper cho fast wake-on-completion

> Chuyển từ MIKE.md §8 sang đây 2026-07-20 (rút gọn §8 theo đề xuất Wags, job
> `Wags_20260720_121120`, sau sự cố `missed-wakeup-after-bg-dispatch`) — nội dung này MOOT từ
> 2026-07-07 (harness bỏ tham số `run_in_background` khỏi Agent tool), chỉ giữ làm sử liệu. Cơ
> chế ĐANG SỐNG hiện tại (ScheduleWakeup poll ngắn) vẫn ở MIKE.md §8, không đọc file này để biết
> quy tắc hiện hành.

## Bối cảnh gốc (thêm 2026-07-03, theo yêu cầu user — nghiên cứu bằng 3 Explore agent + 1 Plan
agent, đọc thẳng code, không suy đoán)

Vấn đề: Mike dispatch `--bg` rồi `ScheduleWakeup` 1 khoảng cố định (vd 1200s) để quay lại — nhưng
Taylor xong sớm hơn nhiều, Discord đã báo GẦN NHƯ TỨC THÌ (`_bg_wrapper` gọi `notify_thread.sh`
ngay khi `claude -p` exit thành công, 0s delay), mà phiên sống của Mike vẫn ngủ tới đúng chu kỳ
mới xử lý. Đã xác nhận 2 hướng KHÔNG dùng được: (a) Discord không đánh thức được phiên sống —
`discord_bot/bot.py`'s `on_message` chủ động bỏ qua mọi message do bot/script đăng
(`if msg.author.bot: return`); phiên remote-control của Mike hoàn toàn thụ động, chỉ xử lý turn
mới khi người thật gõ hoặc `ScheduleWakeup` tự bắn. (b) Auto-callback có sẵn trong `dispatch.sh`
(khi job xong, tự dispatch lại `from` với prompt `[AUTO-CALLBACK...]`, không bao giờ tự lặp — fix
cho vòng lặp Taylor↔Winston 2026-06-27) không dùng được cho Mike: dù gỡ guard chặn target=Mike,
`dispatch.sh Mike "..."` spawn 1 tiến trình Mike lạnh hoàn toàn mới, không phải đánh thức phiên
đang nói chuyện với user.

**Phát hiện mấu chốt**: nút thắt không phải "phát hiện chậm" (Discord đã 0s) mà là "tín hiệu đã
có, không có kênh đưa vào lại turn sống". `bin/jobs.sh wait <job_id> [--timeout SEC]` đã có sẵn
(poll mỗi 15s vào job board bền vững `bus/jobs/*.json`). **Giải pháp lúc đó**: dùng
`Agent(run_in_background: true)` bọc `jobs.sh wait` làm kênh dẫn tín hiệu vào lại turn sống — tận
dụng cơ chế `<task-notification>` gốc của harness.

## SỬA 2026-07-07 (incident `agent-wrapper-monitor-gap`, chẩn đoán Wags job
`Wags_20260707_142752`): template dưới KHÔNG còn chạy được nguyên văn

Harness sau lần restart Mike sang Fable 5 (2026-07-06) đã BỎ tham số `run_in_background` khỏi
Agent tool — schema hiện tại chỉ có `description/prompt/subagent_type/model/isolation` (xác nhận
trực tiếp từ tool schema phiên Wags 2026-07-07).

**`isolation: "worktree"` KHÔNG phải background** — nó chỉ tạo git worktree cách ly; agent vẫn
chạy ĐỒNG BỘ và tin nhắn cuối của nó là kênh trả kết quả DUY NHẤT. Một wrapper trả lời "đã bắt
đầu theo dõi, sẽ báo lại" là bất khả thi cơ học — nó không bao giờ báo lại được. Sự cố thật
2026-07-07 chiều: Mike bọc job `Taylor_20260707_132048` bằng `Agent(isolation:worktree)`, wrapper
trả lời sớm rồi thoát; job thật xong sạch ~13:32 (status:done, exit_code:0) mà Mike không hề
biết, user phải tự hỏi "job die rồi hay bạn không bao giờ biết" mới đi kiểm tra tay.

Wrapper Agent nền CHỈ dùng lại nếu schema tool phiên hiện tại THẬT SỰ có tham số nền (kiểm tra
schema trước khi gọi, không đoán); khi đó dùng template cũ:

```
Agent(prompt="Run: bin/jobs.sh wait <job_id> --timeout <wrapper_timeout>; nếu status != done,
chạy bin/trace.sh <job_id>; CHỈ báo lại field status + result literal, KHÔNG tự ý
retry/quyết định/đánh giá thành-bại", run_in_background: true, model: "haiku")
```

Scope wrapper (khi dùng được) cố tình hẹp: wrapper KHÔNG được gọi `dispatch.sh`, KHÔNG tự retry,
KHÔNG editorialize — quyền quyết định bước tiếp theo luôn ở Mike khi tỉnh dậy, không phải ở
wrapper.

**Công thức timeout cho wrapper** (bám retry thật của dispatch.sh, KHÔNG dùng `--timeout` gốc
trực tiếp vì job có thể đang ở lần thử thứ 2):
```
wrapper_wait_timeout = TIMEOUT × (RETRIES + 1) + 60
```
`dispatch.sh` in sẵn số này ra stderr ngay sau dòng "Theo dõi:".

## Incident 2026-07-06 (dẫn tới quy tắc "luôn dùng, không ngoại lệ fire-and-forget")

Chuỗi Taylor sector-sweep #17-20 (hog/feed leadlag, construction, SOE, holdco) chạy suốt
2026-07-05→06, mỗi job Mike→Taylor xong trong 5-15' thật nhưng dùng ScheduleWakeup dài theo quy
tắc "fire-and-forget research" CŨ — user quan sát thấy lãng phí thời gian chờ rõ rệt cộng dồn qua
nhiều bước. Không phải bug code — quy tắc VIẾT SAI (che khuất bởi lo ngại "đừng phiền vì job dài
không ai chờ", trong khi thực tế TỔNG thời gian trôi qua vẫn tính).

## Giới hạn chưa xác minh (MOOT từ 2026-07-07, giữ làm sử liệu)

Độ bền của `Agent(run_in_background)` task-notification qua CHÍNH việc Mike restart chưa từng
được kiểm chứng thực tế trước khi tham số này bị gỡ khỏi schema — không tài liệu nào trong
codebase khẳng định hay phủ định trước khi câu hỏi trở thành vô nghĩa (harness đã bỏ tham số).

**Verified 2026-07-03 (happy-path, KHÔNG restart, trước khi MOOT)**: dispatch thật Winston `--bg`
(job chạy 14s) + wrapper Agent(haiku, nền) theo đúng template trên → task-notification đánh thức
turn Mike NGAY khi job xong (~vài giây), thay vì chờ hết fallback 600s. Cơ chế chính hoạt động
đúng tại thời điểm đó. Restart-durability chưa từng được quan sát trước khi MOOT.
