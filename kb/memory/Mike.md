# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- VPI/BAL signal HOLD đến review 2026-09-16 — HOLD_ALL theo VPI.

## 🚨 KHẨN — kiểm tra NGAY đầu phiên 09-15
1. **Trade plan T+1 (15/09) cho SpaceX + ZaloPay** — CHƯA CÓ lúc 00:50 ICT, root cause = ingest BQ
   ngoài (`tav2_bq.ticker`/`ticker_prune` phiên 14/09 thiếu nghiêm trọng). Đã dispatch `data-ops`
   nền (agentId abd189aef81b793b2) poll BQ mỗi 20-30', tự chạy lại `daily_refresh_v34b_linux.sh`
   khi đủ ngưỡng, tự dispatch DollarBill lập plan. Nếu tới 07:30 ICT chưa unblock → data-ops tự mở
   bus question đề xuất HOLD (không tự quyết). **Việc đầu tiên đầu phiên**: đọc kết quả agent này
   (hoặc bus event `ticker-prune-ingest-gap-0914-followup`), xác nhận plan đã có/HOLD đã quyết
   trước 09:05 ICT.
2. **Bus-question TV1 (`zalopay-tv1-200cp-sized-by-dgc-dividend-receivable-0914`)** — Wags đóng sai
   `decided_by:user` (arch-review NEEDS_CHANGES 2 vòng 09-14, CÒN HỞ qua đêm). Kiểm tra
   `mike_json.py has-event` xem đã đính chính chưa; nếu chưa, tự đóng đúng cách (không giao lại
   Wags vòng 3 không gate). "Phương án C" (active_nav cộng nhầm dividend excluded_tickers) cũng
   chưa ai quyết — vẫn sống tới 2026-09-25.

## Retro 09-14 đã đóng (`d52d562f`) — 5 sự cố, 2 pattern:
- Pattern 1 (tái diễn, không cần sửa): discretionary auto-inject approval đến sau giờ bot 09:05.
- Pattern 2 (MỚI, theo dõi — escalate nếu lặp lại): Wags tự suy diễn quyết định user khi đóng bus-
  question, bị arch-review NEEDS_CHANGES 2 vòng cùng ngày. Nếu tái diễn ở retro 09-15 →
  escalate `retro-pattern-recurring-wags-decision-overreach-2-days`.
- aria-K (ATC post-close) đã LAND chính thức chiều 09-14 nhưng lộ ra Taylor test patch trên
  working tree thật (không worktree riêng) khiến cron auto-backup cuốn code chưa duyệt vào SXX
  từ 00:03 ICT — may mắn không thiệt hại, nhắc Taylor tránh lặp lại (chưa có rào cản cơ học).

## Còn mở không khẩn: job_cancel_guard nhánh systemd luôn đỏ dưới cron; append_event.sh JSON
cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (không escalate, theo dõi qua retro).

- [2026-09-14T17:42:57Z] 00:57 ICT: killed detached bg monitor (security-flagged, violated no-unsupervised-process rule); ticker_prune 09-14 still 2/200 tickers; now polling via own ScheduleWakeup every ~25min instead — next check should re-run: source wc_env.sh; bq query ... ticker_prune WHERE time=2026-09-14; if >=200 run daily_refresh_v34b_linux.sh then dispatch DollarBill SpaceX+ZaloPay plan T+1; if past 07:30 ICT and still short, post bus question data-ops/bot-run-0915-no-plan-hold-recommended
- [2026-09-14T17:55:58Z] 15/09 01:0x: canary feed corp_action arch APPROVED (branch feat/corp-action-feed-canary @ 2465a35c, worktree mike/agents/wt-corp-feed-canary). Landing: merge mike master + selfcheck --all 33/33 + promote cron_registry.md.proposed (§13, sửa luôn snapshot chạy 06:50 ICT không phải 23:50) + cài cron '5 0 * * 1-5' 07:05 ICT — chờ user duyệt dòng cron; làm SAU land OShares 08:04. KHẨN: snapshot_corp_action_daily FAIL 09-14 (vendor thêm source_news_id + first_disclosure_datetime), run 06:50 ICT sẽ fail lại, mất vintage cả 2 bảng. arch khuyến nghị A′ (ALTER ADD 2 cột + schema_problems không xét thứ tự + HASH_EXCLUDE 2 cột + cô lập bảng + notify lỗi); B mất vĩnh viễn first_disclosure_datetime; CẤM backfill --date 2026-09-14. Dispatch Taylor chuẩn bị A′ (không DDL, không merge). CHỜ USER DUYỆT áp dụng trước 06:50.
- [2026-09-14T18:03:54Z] 15/09 01:03 ICT USER DUYỆT (decided_by user): (1) vá snapshot_corp_action_daily theo A′ (ALTER ADD 2 cột source_news_id/first_disclosure_datetime + schema_problems bỏ xét thứ tự + HASH_EXCLUDE + cô lập bảng + notify lỗi), ÁP TRƯỚC 06:50 ICT sau khi Mike review + arch APPROVED bản chuẩn bị của Taylor_20260914_175556; (2) cài cron canary '5 0 * * 1-5' (07:05 ICT) — merge feat/corp-action-feed-canary + promote cron_registry.md.proposed rồi cài, làm SAU land OShares 08:04 (hoặc trước 07:05 16/09 nếu sáng nay trễ). Trả lời bus question corp-action-snapshot-schema-drift-20260914 với decided_by:user khi áp xong.
- [2026-09-14T18:10:07Z] 15/09 01:3x: SNAPSHOT A′ ĐÃ ÁP XONG (user duyệt 01:03). merge mike dd77553f; ALTER ADD 2 cột (37→39); dry-run rc=0; selfcheck 68/68; chạy thật rc=0 vintage 2026-09-15: corp_action 36.352 (first_disclosure_datetime 15.823 non-null), insider 52.922; hash diff vs 09-13 = 46 + 16 id mới. Cron 06:50 sẽ SKIP. Bus question đã đóng decided_by user. Việc non-blocking còn lại: ghi chú corporate_action_snapshots.md (2 cột thêm 09-15 NULL ở vintage cũ, hash exclude 3 cột, 09-14 mất) + sửa cron_registry snapshot giờ thật 06:50 ICT — gộp khi promote cron_registry.md.proposed của canary. Còn chờ: land OShares 08:04 (cron 141ea337) → rồi merge canary + cài cron 07:05 (user đã duyệt).
- [2026-09-14T18:10:51Z] 15/09 01:4x: CronCreate 141ea337 ĐÃ XOÁ, thay bằng 3a6145a4 (08:04 ICT 15/09, SESSION-ONLY): Phần 1 land OShares (bản vá + đóng băng) + docstring gate_selfcheck + promote registry oshares; Phần 2 merge canary 2465a35c + selfcheck --all + promote cron_registry.md.proposed (sửa giờ snapshot 06:50) + backup crontab + cài dòng '5 0 * * 1-5 ... corp_action_feed_canary.py' + ghi chú corporate_action_snapshots.md; Phần 3 remember kiểm 16/09. Phiên restart = mất cron → làm tay theo đúng các bước này.
- [2026-09-15T01:15:57Z] 15/09 08:2x: PHIÊN RESTART → CronCreate 3a6145a4 (land 08:04) ĐÃ MẤT, chưa merge gì. Trạng thái: corp_action_daily 15/09 OK usable 07:30; snapshot A′ đã áp đêm qua; OShares 2 branch (bc86963e, ce123789) + canary 2465a35c CHƯA merge, cron canary CHƯA cài. Plan 15/09 đang được session khác catch-up (DollarBill_20260915_011449, topic plan) — rating_8l import oshares ⇒ HOÃN land OShares tới khi job plan xong, rồi làm tay theo các bước của 3a6145a4.
