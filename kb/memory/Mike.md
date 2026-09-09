# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến 2026-09-16 — HOLD_ALL theo VPI.

## Margin đơn mã discretionary — LIVE, PB-adaptive WIRED (đóng hoàn toàn)
- Per-name 5% / sleeve 10% NAV, f≤1.3, %ADV≤10%, exit -20%. Commit 022c48e7.
- Phễu candidate WIRE (cutoff=70%, trần=1.2), commit 714b5889. TV1/DGC lọt nhưng marginable=NO qua DNSE hiện tại.

## CCS/8L accruals R&D — ĐÓNG HẲN 2026-09-06
Phase 0→0b→R3→Phase2-NARROW, tất cả NO-GO (lần thứ 3). Mở lại chỉ khi có dữ liệu ngoài mẫu 2014-2026.

## Retro 2026-09-08 — XONG (job Mike_20260908_173646)
File `kb/incidents/retro/retro-2026-09-08.md` (commit 1010d22c), Wags CONFIRMED. 4 sự cố, 2
pattern. Mở 2 bus question mới (chưa từng escalate trước đó):
1. `Mike/retro-2026-09-08-backup-silent-failure-recurring-3rd` — GitHub backup fail lần 3/5 tuần
   (08-01, 08-12, 09-08), luôn cùng gốc: tín hiệu fail chìm trong digest chung, chưa có alert
   riêng. Cần chọn: alert dòng đầu riêng / check tuổi backup độc lập / cả 2.
2. `Mike/retro-2026-09-08-bq-cache-ticker-prune-disabled` — BQ cache TẮT cho MỌI dispatch từ
   09-08 (ticker_prune lệch 909 dòng vs nguồn), chưa điều tra nguyên nhân, chưa có commit fix.
   Blast radius rộng — mọi dispatch dùng BQ đang fallback network (chậm/đắt hơn).
NAV PRICE_XCHECK gate 09-08 (broker marketPrice trễ đồng bộ) đã fix TRONG NGÀY (exit code 4 riêng
+ cron nav_sync_retry.sh 19:15-21:15, commit 8711a922/b375d0f1) — KHÔNG cần theo dõi thêm.

## Retro 2026-09-07 — XONG
File `kb/incidents/retro/retro-2026-09-07.md` (commit 47168ff6), Wags CONFIRMED.

## Bus question đang mở (4)
1. `Mike/retro-2026-09-08-backup-silent-failure-recurring-3rd` (mới) — xem trên.
2. `Mike/retro-2026-09-08-bq-cache-ticker-prune-disabled` (mới) — xem trên.
3. `Wags/wags-fix-not-confirmed: coord-2026-09-07` (09-07) — 3 nơi doc drift cron
   vn_realestate_monthly_check.sh CHƯA SỬA (comment/2 file ghi sai giờ ICT thay vì UTC). Cửa sổ
   theo dõi: trước cron chạy lại tháng sau (~10-06).
4. `macro-strategist/vn-realestate-monthly-check-2026-09` — chờ user chọn A/B/C, đã ack
   triaged-needs-human bởi Wags 01:21:19Z.

## Sát ngưỡng OKF
kb/coding_guidelines.md 37,9KB/40KB, còn ~2,0KB đệm. §-mới tiếp theo gần như chắc chắn chạm
ngưỡng → tách sang _ext.md khi đó.

- [2026-09-08T17:48:50Z] P2-③ BQ cache drift XONG 09-09: root cause = chunked delta khong bao gio tai lai nam cu (sync_bq_cache.py:464), upstream ghi de partition cu => drift 909 dong ticker_prune => co AND toan cuc tat CA cache cho moi dispatch. Fix _drifted_years() commit 3ff20579, verified OK 14/14 bang + preflight PASS. Con lai P2: (2) MBB journal 1565 vs 1675 chua dieu tra; (4)(5) nhieu log CLOUD_SDK + vnstock chua dap.
- [2026-09-09T02:02:48Z] P2 XONG HET (09-09 sang): (1) backup gitlink ed19d852; (3) BQ cache drift 3ff20579; (2) known_position_discrepancies.json + verify_account_snapshot ack co han (mike 6de5fc2f, WC b65c7228) - MBB rights 10:1 28/08, +110 SpaceX/+20 ZaloPay, het han 30/11, khoa theo qty_delta KHONG phai cap tuyet doi; (5) vnstock chatter 2a815338. (4) CLOUD_SDK warning CHUA lam - can 'gcloud auth application-default set-quota-project', dung auth config nen khong lam trong gio giao dich. PHAT HIEN MOI can user quyet: .gitignore:12 blanket *.json => data/trading_rules.json + data/corp_actions.json KHONG duoc backup. Tiep theo: P3.
