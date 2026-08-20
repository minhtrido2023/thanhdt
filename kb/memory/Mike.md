# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
1. **Batch-aware wake P2 (RCA 08-20 lỗi #1)** — Wags_20260820_161721 ĐANG CHẠY
   Fix 5 điểm arch-reviewer vòng 6: killer=check_report_cadence.sh+paper_checkpoint_escalation.sh
   chưa --batch-id; doc 19:30→21:00; caveat wrapper-không-khởi-động; retro đếm batch_wake fail;
   guard --batch-size. Timeout 3600s, opus/high. Core đã xong (64/64 PASS commit a9f5f4f2).
2. **plan-dd-check-string fix** (commit 9a9dbb1) — cần ngày có LAG/BAL entry để verify.
3. **Order-book Pha 0 telemetry** (commit d6346efd) — N=39 obs/3 phiên, tích lũy bình thường.

## Việc còn treo từ retro 08-19
- 3 selfcheck đỏ (nav_cum_dividend, corp_action_daily, lag_forensic_filter) — cần chủ sở hữu xác nhận
- bot_prepare_plan.py bug2 (plan phantom) — cần Taylor điều tra hoặc xác nhận dead/unused
- Pattern 2 (sửa chung working copy, tái diễn 08-07→08-20) — draft đề xuất, chưa post bus question

## Bối cảnh còn hiệu lực
- GDKHQ D1-D3 LIVE từ 08-17. yield_floor Option C WIRED, review 2027-02-10.
- TV1 Rule A LIVE từ 08-15. CASH_VENDOR gate: ĐÓNG.
- OKF split mandate: file vượt 40KB → tự split theo pattern MIKE_ext.md/coding_guidelines_ext.md.
- P2 expvol_pacing: shadow log-only trên LIVE từ 08-17, review 2026-09-15.
- BAL signal shadow-track (case VPI): bắt đầu theo dõi, review 2026-09-16.
- signal_holds.json: book=BAL buy until 2026-09-16 + ticker=VPI until 2026-09-16 (LIVE).
- Wakeup redesign HOÀN TẤT 4 Phase (08-20, 7 commit, 109 assertion PASS).
- P3 ccdb session-dedupe RCA 08-20: chờ restart ngoài giờ giao dịch.
- F2.3 bảng §25 coding_guidelines: chưa làm.
- F3.3 checker ngược khi hold hết hạn: chưa làm.
- Verify production batch wake: lần chạy đầu tiên bq_freshness_check 19:00 ICT ngày mai (08-21).

