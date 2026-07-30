---
kind: incident
date: 2026-07-10
topic: dollarbill-plan-doc-dt5g-hom-qua
title: >-
  2026-07-10 — DollarBill lập plan luôn đọc DT5G của HÔM QUA — thứ tự cron bị đảo ngược
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-10 — DollarBill lập plan luôn đọc DT5G của HÔM QUA — thứ tự cron bị đảo ngược

**Hiện tượng:** user nghi ngờ trực tiếp: lúc lập plan T+1 (dispatch DollarBill ~17:30 ICT),
trạng thái thị trường DT5G có thể bị trễ 1 ngày. Verify thật: `golive_state_today.json`
ghi lúc 17:30:16 hôm nay nhưng field `as_of: 2026-07-09` — dữ liệu hôm qua, dù file mới toanh.

**Root cause:** `daily_refresh_v34b_linux.sh` (TÍNH DT5G của hôm nay, ghi vào BQ
`vnindex_5state_dt5g_live`) chạy cron lúc **23:15 ICT**, nhưng `bq_freshness_check.sh` (ĐỌC
DT5G để dispatch DollarBill lập plan) chạy **17:30 ICT** — sớm hơn gần 6 tiếng so với lúc dữ
liệu hôm nay được tính xong. Đây KHÔNG phải thỉnh thoảng trễ — luôn luôn trễ 1 ngày, mọi ngày,
theo đúng cấu trúc lịch chạy. Bị che giấu suốt nhiều tuần vì `bq_freshness_check.sh`'s
`MAX_STATE_LAG=2` (dung sai 2 ngày giao dịch) luôn pass âm thầm với độ trễ 1 ngày (1≤2).

**Vì sao 23:15 mà không phải sớm hơn:** `daily_refresh_v34b_linux.sh` tự ghi trong header
"Schedule: cron ~18:05 ICT (after market close + ticker ingest)" — ý định BAN ĐẦU đã đúng,
nhưng lịch cron THẬT lại là 23:15, lệch ~5 tiếng, không tìm thấy lý do trong lịch sử sự cố.
User hỏi thẳng: "có cần chờ BQ sync đâu?" — verify bằng dữ liệu thật: `ticker`/`ticker_prune`
của HÔM NAY đã đầy đủ (818 dòng / 265 mã, nằm trong khoảng bình thường 737-859/264-268 các
ngày trước) từ TRƯỚC 18:45 ICT — xác nhận giả thuyết user đúng, 23:15 là dư thừa an toàn
không cần thiết, không phải ràng buộc kỹ thuật thật.

**Fix (commit `1a3ea5c` + `5ea7592`):**
1. `daily_refresh_v34b_linux.sh`: thêm bước [0] verify THẬT (không chỉ tin giờ) — kiểm tra
   `ticker_prune` đã có đủ dữ liệu hôm nay (≥200 mã) trước khi tính, retry có giới hạn (tối đa
   6 lần × 15' = 1.5h) thay vì chạy mù trên dữ liệu thiếu. Cron dời 23:15 → **18:30 ICT**.
2. `bq_freshness_check.sh`: dời 17:30 → **19:00 ICT** (sau khi daily_refresh chạy xong, không
   phải trước). Siết `MAX_STATE_LAG` 2→**1** ngày giao dịch — để nếu bug tái diễn (daily_refresh
   trễ/lỗi) thì bị CHẶN thật (block DollarBill) thay vì lại âm thầm pass.
3. `send_plan_report.sh`: dời 19:30 → **21:00 ICT** (giữ khoảng cách 2h với bq_freshness_check
   như cũ, đủ thời gian DollarBill dispatch chạy xong).

**Verify:** cả 2 script `bash -n` PASS; crontab cài xong, diff xác nhận chỉ đổi đúng 3 dòng
giờ, không đụng gì khác (SpaceX/ZaloPay run_bot/heartbeat/preflight nguyên vẹn).

**Bài học:** dung sai (tolerance) rộng trong 1 cảnh báo (ở đây `MAX_STATE_LAG=2`) có thể VÔ
TÌNH che giấu đúng loại lỗi mà nó được thiết kế để bắt, nếu độ trễ THẬT luôn nằm gọn trong
dung sai — cùng họ bài học Pattern B (RETRO 2026-07-09): đọc nhầm/trễ nguồn dữ liệu, chỉ khác
lần này lỗi nằm ở THỨ TỰ 2 cron job thay vì chọn sai bảng dữ liệu.
