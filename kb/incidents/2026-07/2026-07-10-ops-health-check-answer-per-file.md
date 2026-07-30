---
kind: incident
date: 2026-07-10
topic: ops-health-check-answer-per-file
title: >-
  2026-07-10 (sáng sớm) — `ops_health_check.sh` không bao giờ clear được câu hỏi trả lời bởi agent KHÁC người hỏi — checker match answer PER-FILE, bus ghi theo tác giả
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-10 (sáng sớm) — `ops_health_check.sh` không bao giờ clear được câu hỏi trả lời bởi agent KHÁC người hỏi — checker match answer PER-FILE, bus ghi theo tác giả

**Phát hiện (Wags, job `Wags_20260710_012007`, dispatch bởi wags_autofix coord run):**
2 câu hỏi tồn treo dai dẳng dù đã có người trả lời thật. Điều tra: `cron-paper-main-can-cai`
(Taylor hỏi) đã được Mike trả lời từ **2026-07-09T11:37Z** (commit `04db10d`, verify bằng
`crontab -l` thật khớp TZ-fix) — nhưng checker vẫn báo "pending" suốt gần 1 ngày sau.

**Root cause:** `append_event.sh` ghi MỌI event vào file của TÁC GIẢ
(`bus/inbox/<agent_id>.jsonl`) — câu hỏi của Taylor nằm ở `bus/inbox/Taylor.jsonl`, câu
trả lời của Mike nằm ở `bus/inbox/Mike.jsonl`. `ops_health_check.sh` section 5 (cũ) build
tập hợp "answers" **PER-FILE rồi match question trong CÙNG FILE** — answer chéo-agent
(ai đó KHÁC người hỏi trả lời) không bao giờ nằm cùng file với câu hỏi → không bao giờ
clear được, `wags_autofix` dispatch lặp vô ích 2 lần/ngày × cooldown 1h cho câu hỏi ĐÃ trả
lời, cho tới khi câu hỏi tự rơi khỏi cửa sổ 48h. Lịch sử chỉ những lần answer-cùng-tác-giả
(vd 07-08: Wags tự trả lời câu hỏi do chính `wags_autofix` tạo) mới từng clear được — che
giấu bug này suốt nhiều ngày vì phần lớn câu hỏi/trả lời trước đó tình cờ cùng 1 file.

**Fix (commit `d1c71fb`, +24/-17, 1 file):** section 5 đổi thành 2-pass — pass 1 gom
TOÀN CỤC mọi answer từ MỌI file inbox, pass 2 mới match question. Verify: (1) `bash -n`
OK; (2) synthetic 4-case (cross-agent clear / same-file clear / >48h expire / vẫn mở giữ
nguyên / bad-JSON tolerated) PASS; (3) chạy trên inbox THẬT: pending 2→1 (câu còn lại là
chờ-user thật, không phải bug). **arch-reviewer CONFIRMED** (2026-07-10T01:34:57Z, high
confidence) — 2 khuyến nghị không-chặn: (a) match answer nên ràng buộc `ts >= ts(question)`
để tránh 1 answer cũ đè vĩnh viễn lên 1 câu hỏi TÁI SỬ DỤNG cùng topic; (b) verify claim
"bonus finding Pattern B" bằng văn bản retro thật trước khi dùng làm căn cứ — **đã verify
lại trong RETRO này (xem bên dưới): claim ĐÚNG**, retro thủ công 07-09 chiều thật sự báo
crontab paper-main "chưa cài" trong khi thực tế TZ đã cài 3.5h trước đó.

**Bài học:** một checker coordination tự nó dựa trên giả định sai về CẤU TRÚC dữ liệu nó
đọc (per-file ≈ per-topic) sẽ tạo ra false-positive dai dẳng trông giống hệt "vấn đề thật
chưa xử lý" — đúng loại lỗi mà chính cơ chế retro/checker này được dựng ra để bắt, chỉ
khác đối tượng (ở đây là chính tooling điều phối, không phải dữ liệu trading).
