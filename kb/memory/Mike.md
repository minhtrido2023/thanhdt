# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Retro 2026-09-09 — XONG (job Mike_20260909_173507)
File `kb/incidents/retro/retro-2026-09-09.md` (commit fcf63e01), Wags CONFIRMED. 3 sự cố, 2 pattern.
Pattern A ĐÃ ESCALATE: `Mike/retro-pattern-recurring-nav-price-xcheck-gate-2-days` — gate NAV
PRICE_XCHECK chặn cả 2 account 2 ngày liên tiếp, 3 nguyên nhân độc lập khác nhau (VHM 08-17,
timing-lag 09-08, corp-action giá×lượng 09-09). Prevention đề xuất (chưa làm, cần duyệt vì chạm
NAV): so giá×khối lượng thay vì giá trần đơn lẻ, giảm nhạy khi có corp-action AUTO_CONFIRMED.

## Bus question đang mở, CHƯA fix (theo dõi tiếp)
1. `Mafee/nav-price-xcheck-stuck-{SpaceX,ZaloPay}-2026-09-09` — NAV 2 account thiếu bản ghi 09-09,
   status DIAGNOSED_NOT_FIXED. Escalate ở trên đã mở, không mở question thứ 2.
2. `Mike/bq-cache-manifest-not-updated-by-selfheal-2026-09-09` — self-heal `_drifted_years()`
   (commit 3ff20579) refresh bảng nhưng quên rewrite manifest.json → preflight fail giả, mọi
   dispatch BQ đang fallback network. Chưa sửa.
3. `Wags/wags-fix-not-confirmed: coord-2026-09-07` — doc drift cron vn_realestate_monthly_check.sh.
   Cửa sổ theo dõi: trước cron chạy lại ~10-06.
4. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C.

## Retro 2026-09-08 — XONG, backup silent-failure (lần 4, đã fix hoàn chỉnh) + BQ cache
ticker_prune lệch (sự cố gốc dẫn tới commit 3ff20579 ở trên) — xem file retro nếu cần chi tiết.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## CCS/8L accruals R&D — ĐÓNG HẲN 2026-09-06
Phase 0→0b→R3→Phase2-NARROW, tất cả NO-GO (lần thứ 3). Mở lại chỉ khi có dữ liệu ngoài mẫu 2014-2026.

## BAL/custom30V R&D — ĐÓNG HẲN 2026-09-09, 5 vòng đều NO-GO
BAL vòng 1-3 (attribution, adaptive-exit, gate NEUTRAL) + custom30V vòng 4-5 (selector, placebo
overweight-bank) — tất cả NO-GO, không wire gì. Input đầy đủ cho review VPI/BAL 09-16.
User chốt (decided_by=user): overweight bank trong custom30V (49,1%/67,5%/93,3%) là TÁC DỤNG PHỤ
của pool định nghĩa bằng thanh khoản, không phải chủ ý — giảm tỷ trọng bank là mục tiêu hợp lệ.
Placebo vòng 5 (P1/P2 tách nguồn +2,62pp) đang chạy, output tại
agents/Taylor/research/custom30v_placebo_20260910/.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

