# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Retro 2026-09-25 XONG (commit f67e4db0): 3 sự cố, Wags CONFIRMED. Escalation MỚI mở:
  `retro-pattern-recurring-ack-topic-counter-structural-3retros` — bug ack-topic-counter
  (`daily_retro.sh:195` vs `ops_health_check.sh` `_acked()`) đã bị arch-reviewer chỉ đúng vị
  trí+cách sửa 2 lần (09-23, 09-25), 3 retro liên tiếp không ai vá. Đề xuất: dispatch Wags 1
  task HẸP RIÊNG (không lồng vào wags-fix tổng hợp khác) để đóng dứt điểm.
- Escalation KẾ THỪA (ngày thứ 3): `retro-pattern-recurring-fpt-vendor-backfill-2days` — BQ
  `ticker.Close` FPT backfill hệ số corp-action vẫn thiếu (chặn `report_return_gate` 2 consumer
  khác nhau 09-23/09-24, Wags xác nhận vẫn tồn tại 09-25). Chờ user chọn A/B/C.

## Việc đang mở / cần theo dõi
1. **FiinPro harvest**: 25/74 lô, rate-limit DAILY, tự resume 00:20 ICT mỗi ngày. Theo dõi thụ động.
2. **excluded_dividend_receivable[DGC]** (ZaloPay) — dọn config khi tiền DGC về thật, dự kiến
   ~2026-09-25 (đã qua hạn dự kiến, kiểm lại khi có cập nhật).
3. `append_event.sh` JSON guard: đã vá xong (`json_payload_diag.py`), không cần theo dõi thêm.

## ĐÃ XÁC NHẬN KHÔNG CÒN TREO
- Chuỗi audit corp-action 4 call-site + vendor-mismatch + ex-date price-frame — ĐÓNG HOÀN TOÀN
  2026-09-24, tất cả LIVE trên master.
- test_trading_bot.py:353, universe-pit-migration G7/G8/G9, NAV corp-action gate v2 rc=5,
  discretionary_margin_arms.json, dnse-balances-stock-block-zero, Treasury buyback branch,
  compute_active_nav_selfcheck.py canonical-path — tất cả đã đóng (xem retro 09-22→09-24 cho chi
  tiết nếu cần tra lại).

- [2026-09-25T17:44:35Z] Opening-window A/B thụ động (order_book_execution_shadow ext): triển khai job Taylor_20260925_174424 (deadline trước phiên 28/09); bắt đầu thu thập 28/09; checkpoint sơ bộ 21/10 (trùng mốc nghiệm thu shadow program mẹ, KHÔNG kết luận); mốc quyết định cứng 25/01/2027 (~80 phiên cho N=24 mới). Chi tiết: kb/projects/rnd-pipeline-tracker.md.
- [2026-09-25T17:56:02Z] Opening-window l2-poll DEPLOYED (commit 4d863548, job Taylor_20260925_174424) — cron 09:13 ICT T2-T6 tự chạy từ 28/09, không cần theo dõi thêm cho tới checkpoint 21/10.
- [2026-09-25T21:00:12Z] 2026-09-26 weekly-ops-audit: 4 commit fix (f63efc47 append_event guard JSON, 0344ec93 manifest T1, 3d8eed54 baseline --root-only, 0b57ca4c is_live vnstock). CON MO: loan_package selfcheck cho Taylor (broker_filled_qty 3-tuple); question moi selfcheck-baseline-checker-no-tier; FPT vendor backfill sang ngay 3 CHAN newdeals report 3 ngay lien; context_pack.md 47.6KB DA VUOT nguong 45KB, current_ops.md 25.3KB con 2.7KB.
- [2026-09-26T04:28:34Z] Dispatch Taylor_20260926_042824 (--bg, opus/high, timeout 3600s): đối soát gap V2.3-book panel (pt_v22_dt5g.py) vs NAV thật SpaceX/ZaloPay — user 'Duyệt' 26/09 11:27. Việc: (A) xác minh charter engine_room_oos.md sai claim strategies.py đọc pt_v22_dt5g_open_positions.csv, (B) đối soát tuần-qua-tuần panel vs NAV thuần-trading 2 account, (C) tìm nguyên nhân phân kỳ (DGC exclusion ZaloPay? scale/ADV? fill timing?), (D) kết luận % đóng góp. Poll bằng jobs.sh status; claim-reply trước khi post kết quả.
- [2026-09-26T04:44:46Z] Job Taylor_20260926_042824 XONG, đã post kết quả Discord: panel-vs-live gap ĐẢO NGƯỢC so đoán ban đầu của Mike — live THẮNG panel (SpaceX +5.99pp, ZaloPay +3.90pp), nguyên nhân thật = capacity/ADV×scale (panel 50B buộc chọn CTCK+PNJ lao dốc, live 1B giữ được SCL/DRI) + DGC legacy ZaloPay, KHÔNG PHẢI park 70/80% hay egg-asset (phương pháp trừ-egg của Mike bị Taylor chỉ ra là SAI — egg là transfer nội bộ NAV). Charter engine_room_oos.md đã sửa (registry + regen), commit trong KB v3283. 2 việc phụ còn mở, không khẩn: audit_lib.py nhãn park sai E1VFVN30 vs CUSTOM_VN30G; 8-9 mã live ngoài rổ recommend chưa truy nguồn.
- [2026-09-26T16:31:25Z] 26/09 23:4x — FiinPro harvest XONG 74/74 (OShares 655 mã + FX 15 năm). Đề xuất khai thác đã viết: kb/projects/fiinprox-data-usage-proposal-20260926.md (7 hướng H1-H7, ưu tiên H1 bank 8L → H2 CPI → H4 2018 foreign matched → H5 retail ecology). VIỆC TRƯỚC 28/09: hợp nhất OShares/FX thành CSV + registry §9 + nghiệm thu PIT OShares vs corporate_action (bước 0). Chờ user duyệt hướng nào để dispatch Taylor.
- [2026-09-26T16:41:58Z] 26/09 23:4x — FiinPro BƯỚC 0 XONG (commit 82d7720d): data/fiinprox_oshares_pit_20260926.csv (647 mã, 6.404 sự kiện, UNVERIFIED-PIT) + data/fiinprox_usd_fx_monthly_20260926.csv (177 tháng, VCB DERIVED) + 2 registry. User duyệt LÀM CẢ 7 HƯỚNG, thứ tự Mike quyết. Đã dispatch song song (opus/high, timeout 3h): JOB A Taylor_20260926_164113 = H3 PIT→H1 bank 8L→H2 CPI; JOB B Taylor_20260926_164143 = H4 foreign matched 2018→H5 retail ecology. CÒN LẠI sau khi A/B xong: H6 = Agent(macro-strategist/Bobby) nạp credit/M2/fx_free_premium vào registry lead-indicator (dùng CSV bước 0), H7 GDP gộp vào H6 (thấp). Wakeup poll: claim-reply từng job trước khi post.
