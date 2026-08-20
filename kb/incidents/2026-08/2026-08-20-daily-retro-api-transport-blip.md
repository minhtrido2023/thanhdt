# 2026-08-20 — daily_retro mất retro 2026-08-19: lỗi TRUYỀN TẢI API bị gán nhãn "Mike trả lạc đề"

**What happened.** Cron `daily_retro.sh` 00:30 ICT abort, không sinh
`kb/incidents/retro/retro-2026-08-19.md`. Checker ops-health 08:20 flag đúng triệu chứng
nhưng gợi ý sai hướng ("nghi quoting bug lớp 08-01").

**Root cause (bằng chứng thật, không suy đoán).** Cả 2 lần thử draft chết sau 16s/18s với
`API Error: Unable to connect to API: Self-signed certificate detected` (proxy/ISP chèn cert)
— `logs/daily_retro_draft_20260819_173001_a1.log` + `..._173017_a2.log`. Script KHÔNG có bug
quoting; nó có **hai lỗi thiết kế**:

1. **Retry tức thì vô dụng.** Lần thử 2 gọi lại sau **18 giây** ⇒ rơi đúng cùng blip mạng.
2. **Chỉ có 2 lớp phân loại** (usage-limit / phần còn lại), và "phần còn lại" bị gán CỨNG
   nhãn *"nghi Mike trả nhầm task cũ"* trong log + Telegram + bus question ⇒ job ops-autofix
   sáng hôm sau (`Winston_20260820_012008`) bị dẫn sang giả thuyết quoting-bug sai hoàn toàn.
   Lỗi mạng là **lớp thứ BA**, không phải "phần còn lại".

**Fix** (commit `199a03a3`): thêm `API_TRANSPORT_ERROR_RE` (lớp 3) ⇒ `sleep 180s` trước lần
thử cuối, và `_fail_cause` bơm vào CẢ log/notify/payload bus question.
**CỐ Ý không gộp vào `bin/usage_limit_phrases.sh`** — file đó là hợp đồng dùng chung với
`dispatch.sh` (khớp ⇒ auto-resume); lỗi mạng KHÔNG được phép kích auto-resume.

**Verify.** `bash -n` OK, `shellcheck -S error` sạch. Chạy bộ phân loại lên **log thật**:
2 log hỏng 00:30 → `transport=YES, usage_limit=NO` (đi đúng nhánh backoff + nhãn đúng);
log thành công 08:35 → cả hai `NO` (không false-positive). Retro 08-19 đã được chạy bù thủ
công 08:35 và commit `29764096` — nội dung không mất.

**Lesson.** Một checker/pipeline có N-1 lớp phân loại sẽ dồn mọi nguyên nhân chưa biết vào
lớp cuối cùng và **gọi tên nó bằng nhãn của lớp đó** — nhãn sai đó là thứ người/agent đọc
sáng hôm sau. Cùng họ với §28: đừng suy nguyên nhân từ nhánh else, phải khớp bằng chứng thật.
