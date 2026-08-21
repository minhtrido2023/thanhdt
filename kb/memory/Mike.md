# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Trạng thái 2026-08-21 (cuối ngày) — S2/S3/S4 HOÀN TẤT

### Lỗi giờ lần 3 — đã implement đủ S2+S3+S4
- ccdb commit ce4778e: fix prompt_builder early-return (S2.1) + scheduler injection (S2.2) + thread_context ICT (S3) + now_context_line market-state suffix (S2)
- fleet commit fd3b710f: hook user_prompt_submit.sh (S2.3) + now_line.py + time_claim_audit.py (S4) + now_injection_selfcheck.sh
- S4 detector confirmed catches real 2026-08-21 23:02 ICT incident
- All 109 ccdb tests pass; now_injection_selfcheck PASS on all 3 topics

### ccdb-mike.service restart PENDING
- S2/S3 chưa có hiệu lực cho đến khi restart ccdb-mike.service
- CHỜ user confirm giờ restart an toàn (không có session live nào đang active)

### S1 flip — READY nhưng CHƯA LÀM
- Taylor audit: chỉ 1 file cần sửa trước: mike/agents/Taylor/anomaly_scan.py:294 (1 dòng)
- Sau sửa 1 dòng đó: safe to flip TZ=Asia/Ho_Chi_Minh ở ccdb-mike.service
- Làm sau khi S2/S3 đã verify ổn định (vài ngày)

### Known-red còn lại (KHÔNG do thay đổi này)
- lag_live_schedule_selfcheck.py B6
- phs_flash_api_selfcheck.py: chờ PHS creds
- daily_retro_wake_metrics_selfcheck.sh: _batch_unknown unbound

### Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE. TV1 Rule A LIVE. CASH_VENDOR gate ĐÓNG.
- BAL+VPI signal_holds until 09-16. SpaceX+ZaloPay HOLD_ALL.
- OKF split mandate: file >40KB tự split.

