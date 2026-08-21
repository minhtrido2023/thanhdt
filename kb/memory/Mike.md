# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-08-22 00:41 ICT (đầu ngày, sau retro 08-21)

### Lỗi giờ lần 3 — ĐÃ ĐÓNG (S1-S4 hoàn tất)
- ccdb commit ce4778e + fleet commit fd3b710f: [now:] injected by-construction mọi đường prompt.
- `time_claim_audit.py --since 2026-08-21` → 0 mismatch. now_injection_selfcheck PASS cả 3 topic.
- S1 flip (TZ=ICT ở ccdb-mike.service) vẫn CHƯA LÀM — chờ vài ngày verify ổn định trước khi flip.
  Taylor audit: chỉ 1 dòng cần sửa trước (mike/agents/Taylor/anomaly_scan.py:294).
- ccdb-mike.service restart: đã CẦN cho S2/S3 có hiệu lực — kiểm tra đã restart chưa trước khi
  báo cáo trạng thái S2/S3 là "live".

### Wake-up architecture — ĐÓNG bằng loại bỏ (commit 541b50f3, 10:12 ICT 08-21)
- Gỡ toàn bộ push-wake-on-completion + reconciler cron + debounce. Mô hình mới: agent tự báo kết
  quả lên bus/thread; Mike chỉ ScheduleWakeup khi CHÍNH Mike còn bước phụ thuộc (MIKE.md §8).
- Claim-reply nguyên tử vẫn giữ nguyên, vẫn bắt buộc dòng đầu mọi wakeup turn.

### Việc còn HỞ từ retro 2026-08-21 (kb/incidents/retro/retro-2026-08-21.md)
- **`Wags/wags-fix-not-confirmed: coord-2026-08-21` CHƯA ĐÓNG** — `wake_debounce_selfcheck.sh`
  ghi rác (fixture thread_id giả) thẳng vào `logs/wake_thread_errors.log` production, làm
  `daily_retro.sh` đếm sai (50/50 dòng push_err ngày 08-21 = 100% fixture). Cần: sink cách ly
  (`WAKE_THREAD_ERR_SINK`) hoặc lọc thread_id fixture trong daily_retro.sh. Hạ ưu tiên NẾU xác
  nhận không còn script nào đọc log này sau khi kiến trúc wake-up mới ổn định vài ngày.
- Chưa có entry `kb/incidents/2026-08/` riêng cho sự cố #3 (log fixture pollution) và #5
  (CAPIT/custom30V qty floor sizing bug, đã fix, chỉ có bus finding).
- Theo dõi "gộp nguồn quên tách xuất xứ" (tiền §25, vị thế broker, nay CAPIT/parking qty) — lần
  thứ 4 ở field khác thì formalize thành mục coding_guidelines mới.

### Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE. TV1 Rule A LIVE. CASH_VENDOR gate ĐÓNG.
- BAL+VPI signal_holds until 09-16. SpaceX+ZaloPay HOLD_ALL.
- OKF split mandate: file >40KB tự split.

