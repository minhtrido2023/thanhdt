---
kind: retro
date: 2026-07-09
topic: retro-2026-07-09
title: >-
  RETRO — 2026-07-09 (cron 22:00, chạy lần đầu qua `bin/daily_retro.sh`): 9 sự cố tổng trong ngày, 1 sự cố mới phát hiện sau bản RETRO thủ công lúc chiều, 2 pattern xuyên suốt — 1 pattern coi như ĐÃ ĐÓNG (chờ quan sát), 1 pattern ESCALATE
status: open-items
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# RETRO — 2026-07-09 (cron 22:00, chạy lần đầu qua `bin/daily_retro.sh`): 9 sự cố tổng trong ngày, 1 sự cố mới phát hiện sau bản RETRO thủ công lúc chiều, 2 pattern xuyên suốt — 1 pattern coi như ĐÃ ĐÓNG (chờ quan sát), 1 pattern ESCALATE

Đây là lần chạy ĐẦU TIÊN của cơ chế cron tự động (`bin/daily_retro.sh`, 22:00 ICT). Một
bản RETRO khác cho CÙNG NGÀY 2026-07-09 đã được viết thủ công lúc ~20:46 ICT (xem entry
"RETRO — 2026-07-09: 7 sự cố..." phía trên — tiêu đề ghi "7" nhưng bảng liệt kê 8 dòng,
đây là lỗi đánh số nhỏ trong entry đó, không sửa lại vì nguyên tắc không viết đè entry
cũ). Entry này KHÔNG lặp lại nội dung 8 sự cố đã phân tích ở đó — chỉ bổ sung phần MỚI
phát sinh giữa 13:46 UTC (lúc viết bản thủ công) và 15:02 UTC (giờ chạy cron), rồi tổng
kết lại bức tranh cả ngày.

**Sự cố thứ 9 (MỚI, chưa từng có entry riêng cho tới bây giờ):** dispatch hard-timeout
giết agent Wags đã xong việc — xem entry ngay phía trên. Phát sinh SAU khi bản RETRO thủ
công đã viết (bản đó chỉ thấy Wags job "ĐANG SỬA", chưa biết job đó sẽ bị giết oan ngay
sau khi hoàn tất). Đã fix cùng tối bằng heartbeat-aware deadline (commit `d3a7282` +
`b8f78bd`/`5446bf2`), verify e2e 4/4.

**Cập nhật trạng thái Pattern A (job nền chết vì lifecycle bị ràng buộc sai) — từ "ĐANG
SỬA" → coi như ĐÃ ĐÓNG, cần quan sát thêm:** bản thủ công lúc chiều liệt kê Pattern A là
"tái diễn lần 3, prevention cũ chưa đủ", với item 1 còn "chưa xong". Tính tới giờ chạy
cron này, Pattern A đã nhận **2 lớp fix riêng biệt trong cùng 1 buổi tối**: (1)
`systemd-run --scope` tách cgroup (Wags, arch-reviewer CONFIRMED high, 14:09:55Z — job
sống sót qua fake-bridge-stop test thật), (2) heartbeat-aware deadline (sự cố thứ 9 ở
trên, verify e2e 4/4). Hai lớp này che 2 nguyên nhân chết khác nhau (cgroup-kill vs
hard-timeout-kill) nhưng CÙNG một triệu chứng gốc: "job nền còn sống nhưng bị hệ thống
giám sát/hạ tầng giết nhầm". Đây LẦN ĐẦU TIÊN Pattern A có bằng chứng verify độc lập
(arch-reviewer + e2e test) thay vì chỉ "đã sửa, tin lời code". **Chưa tuyên bố đóng
hẳn** — cần quan sát ~1 tuần không có job nào chết oan nữa (theo đúng tinh thần "trust
the artifact" — code verify tốt không đồng nghĩa production sẽ không lộ ca lạ khác) rồi
mới coi Pattern A là closed thật sự trong RETRO tương lai.

**Pattern B (đọc nhầm nguồn dữ liệu trễ/sai — stale/wrong data source) — ESCALATE, vì
đây là RETRO thứ 2 LIÊN TIẾP flag pattern này mà KHÔNG có gì thay đổi ở tầng prevention
giữa 2 lần:** bản thủ công lúc chiều đã liệt kê Pattern B "tái diễn lần 4+, prevention
cũ (coding_guidelines.md §6) chưa đủ mạnh" và đề xuất 2 hướng ((a) checklist bắt buộc
chèn vào dispatch prompt report/plan-generation, (b) static lint grep pattern nguy hiểm)
nhưng CHỦ ĐỘNG chưa làm, chờ bàn phạm vi. Từ 13:46 UTC tới giờ, KHÔNG có commit/thay đổi
nào bổ sung cơ chế (a) hoặc (b) — 2 fix trong khung giờ đó (`bf59061` evidence-counter,
`b57ffce` paper_main_early_check.sh) đều là vá 1 điểm cụ thể (giống cách đã vá riêng lẻ
cho DollarBill 07-09 sáng), không phải cơ chế chung. Theo đúng quy tắc bước 10 của
`bin/daily_retro.sh` (2 lần RETRO liên tiếp cùng 1 pattern chưa đổi prevention →
escalate): đã ghi bus event `question` (`retro-pattern-recurring-dataprovenance`) yêu
cầu Mike/user quyết định giữa (a)/(b) hoặc phương án khác, thay vì viết thêm 1 dòng
"cần cơ chế mạnh hơn" nữa mà không hành động — đúng tinh thần "prevention hiện tại
không hiệu quả, cần thay đổi cách tiếp cận" mà quy tắc yêu cầu.

**Việc còn treo sang ngày mai (không phải sự cố, chỉ ghi để không quên):** crontab
`paper-main` (TZ fix + tách phiên sáng) đã soạn xong, chờ user cài tay (`Taylor` question
`cron-paper-main-can-cai`, 11:06:27Z) — chưa cài nghĩa là fix TZ chưa có hiệu lực thật
cho tới khi user chạy lệnh cài.

**Đã dọn working memory cuối ngày (2 lần trong ngày — bản thủ công lúc chiều đã dọn 1
lần; lần này cập nhật lại cho khớp thông tin mới: Wags job đã xong+verify, sự cố thứ 9
đã đóng, Pattern B đã escalate) + chạy `bin/consolidate.sh`.**
