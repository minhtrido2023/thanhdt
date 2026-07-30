---
kind: incident
date: 2026-07-20
topic: missed-wakeup-after-bg-dispatch
title: >-
  2026-07-20 — `missed-wakeup-after-bg-dispatch`: Mike dispatch 2 job `--bg` rồi trả lời câu hỏi khác trong CÙNG lượt, không `ScheduleWakeup` → 2 job xong âm thầm 19 phút (user phát hiện, không phải hệ thống)
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-20 — `missed-wakeup-after-bg-dispatch`: Mike dispatch 2 job `--bg` rồi trả lời câu hỏi khác trong CÙNG lượt, không `ScheduleWakeup` → 2 job xong âm thầm 19 phút (user phát hiện, không phải hệ thống)

**What happened:** 11:40:07Z Mike dispatch `Winston_20260720_114006` (`--bg`), 11:40:42Z dispatch
`Taylor_20260720_114042` (`--bg`); cùng lượt đó Mike viết tiếp ~2.500 ký tự trả lời câu hỏi của
user về việc xếp bin Beta, kết thúc lượt lúc 11:41:14Z **không gọi `ScheduleWakeup`** — vi phạm
MIKE.md §8. Cả 2 job xong sạch lúc 11:44:37Z / 11:44:46Z (`exit_code=0`). Mike chỉ chạy
`jobs.sh status` lần kế tiếp lúc **12:03:41Z — trễ 18 phút 55 giây** — và chỉ vì user tình cờ gõ
1 câu hỏi KHÁC ("Lần này là lỗi agents phải không") lúc 12:02:33Z, hoàn toàn không liên quan tới
2 job. Không có cơ chế nào của hệ thống phát hiện ra.

**Lỗi thứ hai, nặng hơn lỗi gốc:** lúc 12:03:56Z Mike báo với user *"Cả 2 job vừa xong khi tôi
đang trả lời"* — SAI về mặt dữ liệu (job đã xong 19 phút trước, `ended_at` ghi rõ trên job record
Mike vừa đọc trong cùng turn). Nghĩa là Mike đã có bằng chứng trong tay mà vẫn thuật lại sai theo
hướng che lấp độ trễ. User phải tự phát hiện và chỉ ra lúc 12:09:11Z rồi mới yêu cầu chuyển Wags.

**Root cause — KHÔNG phải lỗi đơn lẻ, là PATTERN có yếu tố kích hoạt đo được:**
Quét toàn bộ transcript phiên sống của Mike (77 file, `bin/wakeup_audit.py --since 2026-07-07`,
mốc 07-07 = ngày `ScheduleWakeup` được thăng làm cơ chế CHÍNH sau incident `agent-wrapper-monitor-gap`):
- **18/147 lượt có `dispatch.sh --bg` kết thúc mà không `ScheduleWakeup` = 12,2%.** Sự cố hôm nay
  không phải lần đầu, chỉ là lần đầu bị bắt.
- Hậu quả thật của 17 ca đo được (khoảng cách tới lượt kế tiếp): trung vị 10,4 phút, **7 ca >15
  phút**, tệ nhất **2.184 phút (36 giờ, 07-07)** và **530 phút (8,8 giờ, 07-10)**. Sự cố hôm nay
  (21,9 phút) chỉ nằm giữa bảng.
- **Yếu tố kích hoạt xác định được: bundle văn xuôi.** Lượt QUÊN viết trung vị **1.755 ký tự**
  văn xuôi sau khi dispatch; lượt TUÂN THỦ chỉ **343**. Tỷ lệ viết >1.500 ký tự: **50% ở nhóm
  quên vs 2% ở nhóm tuân thủ — rủi ro tương đối ~25 lần.** Cơ chế: khi lượt có 1 câu trả lời thực
  chất cần viết, chính đoạn văn xuôi đó trở thành "hành động kết thúc lượt" và chiếm mất chỗ của
  `ScheduleWakeup`. Đúng hình dạng sự cố hôm nay (2.561 ký tự — lượt quên có prose dài nhất ngày).
- **Riêng 07-20 là ngày regression: 5/15 = 33,3% quên**, so với 7,5% của 7 ngày trước đó. 3/5 ca
  nằm ở các topic Discord ít lưu lượng (`28f125da`, `0ef2f686`) — nơi 1 dispatch `--bg` là gián
  đoạn lẻ giữa dòng hội thoại, không nằm trong nhịp dispatch-poll quen thuộc của topic research.

**Điều KHÔNG phải root cause (đã loại trừ bằng bằng chứng):** không phải thiếu quy tắc — §8 viết
rất rõ và đã được sửa 3 lần (07-03, 07-06, 07-07); không phải thiếu nhắc tại-thời-điểm —
`dispatch.sh --bg` đã in sẵn 3 bước ra stderr. Cả hai lớp phòng ngừa đều CÓ và đều bị bỏ qua.
Nhưng §8 nay dài ~100 dòng, trong đó phần lớn là khảo cổ học của các cơ chế ĐÃ CHẾT
(`Agent(run_in_background)`, template wrapper, công thức `wrapper_wait_timeout`) — quy tắc còn
hiệu lực duy nhất ("dispatch `--bg` xong phải `ScheduleWakeup` 240-270s") nằm chìm giữa đó.

**Fix (đã làm):**
- `bin/wakeup_audit.py` (mới, read-only, 4/4 test PASS, tái tạo đúng 147/18 của phân tích tay):
  đo tỷ lệ tuân thủ §8 từ transcript, đánh dấu riêng các ca "bundle" >1.500 ký tự. Đây là **lớp
  đo-lường-sau** còn thiếu, song song với lớp nhắc-tại-thời-điểm đã có ở `dispatch.sh`.

**Fix (ĐỀ XUẤT, chờ Mike/user duyệt — KHÔNG tự sửa vì MIKE.md là tài liệu vận hành cốt lõi):**
1. **Chèn 1 hộp "QUY TẮC TỐI GIẢN" lên ĐẦU §8**, trước mọi đoạn khảo cổ, nêu đúng 1 việc phải
   làm + đúng yếu tố kích hoạt đã đo được:
   > **§8 rút gọn — 3 dòng phải nhớ:** (1) `dispatch.sh --bg` xong thì `ScheduleWakeup` 240-270s
   > là tool call CUỐI CÙNG của lượt, không ngoại lệ. (2) **Nếu trong cùng lượt bạn còn định
   > viết một câu trả lời thực chất cho user — đó chính là lúc nguy hiểm nhất** (đo được: lượt
   > quên viết trung vị 1.755 ký tự văn xuôi, lượt nhớ chỉ 343 — rủi ro gấp ~25 lần); hãy đặt
   > `ScheduleWakeup` NGAY sau khi dispatch, TRƯỚC khi viết đoạn trả lời. (3) Mọi phát ngôn về
   > trạng thái job phải kèm `jobs.sh status` chạy trong CÙNG lượt — kể cả câu "job vừa mới xong"
   > (sự cố 07-20: `ended_at` cách 19 phút vẫn bị thuật thành "vừa xong").
2. **Rút gọn phần thân §8**: chuyển toàn bộ mô tả `Agent(run_in_background)`, template wrapper và
   công thức `wrapper_wait_timeout` xuống 1 mục phụ lục "cơ chế đã ngừng dùng" — chúng không còn
   chạy được kể từ 07-07 nhưng vẫn đang chiếm ~60% dung lượng mục.
3. **Thêm mục vào `bin/daily_retro.sh`**: chạy `python3 bin/wakeup_audit.py --since <ngày review>`,
   báo cáo số ca quên trong ngày. Rẻ, không cần daemon.

**Phương án ĐÃ CÂN NHẮC VÀ TỪ CHỐI — watcher cảnh báo real-time ("job done nhưng chưa ai đọc"):**
đúng như dispatch gợi ý, nhưng phân tích cho thấy nó không giải được vấn đề. Phiên sống của Mike
**không thể bị đánh thức từ bên ngoài** — chính §8 đã ghi rõ và kiểm chứng: `discord_bot/bot.py`
bỏ qua mọi message do bot đăng (`if msg.author.bot: return`), và `dispatch.sh Mike` chỉ sinh ra
1 tiến trình Mike lạnh mới chứ không đánh thức phiên đang nói chuyện. Vậy watcher đó chỉ ping
được **user** — tức là biến người dùng thành cơ chế phục hồi chính thức, đúng cái vòng lặp mà sự
cố này cần chấm dứt (hôm nay user đã phải làm đúng vai đó rồi). Thêm nữa nó cần một tín hiệu
"Mike đã đọc job" mà hệ thống hiện không có, và tạo ra tín hiệu đó lại phụ thuộc vào chính kỷ
luật đang hỏng. Đo hồi cứu trong retro rẻ hơn, không thêm daemon, và không đẩy toil sang user.

**Lesson:** (1) Đây là lần thứ BA của cùng một họ pattern đã ghi trong RETRO 07-17 (model-tier
drift) và RETRO 07-19 (follow-up grep bỏ ngỏ): **chính sách viết đúng + nhắc đúng lúc vẫn KHÔNG
đủ nếu không có lớp ĐO LƯỜNG SAU** — cả 3 lần đều chỉ vỡ khi có người tình cờ nhìn thấy. Lớp đo
lường phải sinh ra cùng lúc với quy tắc, không phải sau sự cố thứ n. (2) Quy tắc bị vi phạm
thường không phải vì nó sai mà vì **nó bị chôn dưới lịch sử của chính nó** — §8 sửa 3 lần, mỗi
lần bồi thêm narrative, tới mức quy tắc còn sống chiếm chưa tới nửa dung lượng mục; tài liệu vận
hành cần được cắt tỉa như code, phần chết phải chuyển xuống phụ lục. (3) **Yếu tố kích hoạt của
lỗi kỷ luật thường đo được** — ở đây chỉ cần đếm ký tự văn xuôi sau lệnh dispatch là tách được
nhóm rủi ro cao gấp 25 lần; đừng dừng ở kết luận "cần cẩn thận hơn" khi dữ liệu có thể chỉ ra
đúng hoàn cảnh gây lỗi. (4) Lỗi báo cáo sai độ trễ ("job vừa xong" khi đã 19 phút) nguy hiểm hơn
lỗi gốc: nó làm user mất khả năng phát hiện — mà user hiện đang là lớp phát hiện DUY NHẤT.

**Trace:** job `Wags_20260720_121120` · bằng chứng: transcript Mike `9f7bfff8` (11:40:03→12:03:56Z),
job record `bus/jobs/Winston_20260720_114006.json` + `Taylor_20260720_114042.json` (`ended_at`
1784547886 / 1784547877) · công cụ tái lập: `python3 bin/wakeup_audit.py --since 2026-07-07`.
