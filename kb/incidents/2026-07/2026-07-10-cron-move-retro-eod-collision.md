---
kind: incident
date: 2026-07-10
topic: cron-move-retro-eod-collision
title: >-
  2026-07-10 (đêm) — retro dời giờ theo lịch EOD mới + dọn 1 va chạm lịch phụ
status: logged
source: >-
  kb/INCIDENTS.md (migrate OKF 2026-07-30, job Winston_20260730_144031)
---

# 2026-07-10 (đêm) — retro dời giờ theo lịch EOD mới + dọn 1 va chạm lịch phụ

User yêu cầu rà lại toàn bộ chu trình vận hành sau khi đổi giờ DT5G cùng ngày (entry trên).
Phát hiện khi rà toàn bộ crontab buổi tối:
1. `rubber_weekly.sh` (feed cao su, không liên quan) vô tình trùng 18:30 ICT với
   `daily_refresh_v34b_linux.sh` mới dời tới — không lỗi thật (2 tiến trình độc lập, không
   chung tài nguyên) nhưng dọn cho sạch: dời `rubber_weekly.sh` → 18:35 ICT.
2. `daily_retro.sh` (22:00 ICT) chạy TRƯỚC `sync_bq_cache_daily.sh` (23:45) và
   `fleet_backup.sh` (00:00) — sự cố ở 2 job đó sẽ bị trễ 1 ngày mới được retro ghi nhận,
   đúng loại lỗi vừa sửa cho DollarBill/DT5G. Dời `daily_retro.sh` → **00:30 ICT** (sau
   fleet_backup, trước kb_nightly 02:00) — review trọn vẹn cả ngày, không sót job cuối.
3. Bug đi kèm tìm thấy khi dời: script tính `TODAY` bằng `date` tại thời điểm chạy — nếu
   chạy sau nửa đêm (00:30 ICT) sẽ tính nhầm sang ngày MỚI thay vì ngày vừa kết thúc. Đã
   sửa dùng `date -d yesterday` (đúng ngày cần review).

**Verify:** `bash -n` PASS, `date -d yesterday` xác nhận đúng ngày; crontab diff trước/sau
chỉ đổi đúng 2 dòng đã nêu.
