# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại (dọn cuối ngày 2026-10-09, sau retro)
- **Retro 2026-10-09 ghi xong**: kb/incidents/retro/retro-2026-10-09.md (commit 1a9e79bb).
  2 sự cố: (1) SBV weekly fetch_failed — root cause thật tìm ra + vá hôm nay
  (`sbv_policy_verify.py`, merge 18e2f9de + ca62e154), nhưng retro-10-08 đã BỎ SÓT lượt tái diễn
  08/10 dù retro-10-07 đã dặn escalate — gap quy trình retro tự thân. (2) ZaloPay DNSE 401 lúc
  21:00 kiểm drift — đính chính retro-10-07: cơ chế "second-chance" KHÔNG thực retry drift-check
  khi plan không đổi, lần thành công 07/10 là trùng hợp (md5 đổi do plan đổi), chưa vá (rủi ro
  thấp, chỉ-cờ không chặn lệnh). Pattern G MỚI: đánh giá cơ chế tự phục hồi "đúng thiết kế" từ 1
  lần quan sát thành công, không truy điều kiện thật — Prevention: retro mai phải đọc lại "Hành
  động đề xuất" của entry hôm trước (bước 0 mới). Wags verify GAPS FOUND (1 nhỏ, đã sửa).
- **5 nhánh R&D hậu re-pin park0 — TẤT CẢ ĐÃ ĐÓNG**: re-pin R3 park=0 (pin kho), BAL MAX_POS>12
  NO-GO, DC-book event-anchored (merged), rerun nhóm B engine-fixed (xong, trình user đã xử lý),
  cổ tức tiền first_disclosure_datetime=C không PIT (đóng). Còn mở theo trigger: DC-book
  event-anchored, L1b@≤0,3 khi park lãi hạ, announcement study ≥2027-08.
- Instructions-dedup: MERGED master (6e8b7d57 + 34cc5df8). Auto-load Mike −8,6KB. NOT_FOUND=0.
- Cutloss intraday shadow: v1 REFUTED, v2 INCONCLUSIVE (margin 1pp chưa rõ) — user chốt bỏ mốc
  "5 phiên", thay bằng ≥30 ngày-ca live ADV≥10B (1-2 năm), biên 1pp chấp nhận là chi phí dùng
  tiền. Code v2 (3 lỗ hổng vá) merged 9a1eeede, shadow chạy code mới từ 12/10. Không còn gì chờ.
- Corp-action broker-primary SHADOW: tiêu chí bật live đã user duyệt (≥3 sự kiện chỉnh giá thật,
  0 CONFIRMABLE sai, xác minh marketId sau 19:00) — ghi current_ops + research file. Mốc xem lại
  2026-12-15 (đếm sự kiện qua sổ shadow).
- SBV source-B: question đã đóng (user chọn B, merge 4d9a36d8) — theo dõi lượt Thứ Hai 12/10
  08:05 ICT xác nhận finalize nhắc đúng 1 dòng STALE nếu chưa có nguồn B cho chuỗi NHNN.
- Pattern F (PAT expiry alert): action#2 đóng tốt hơn kỳ vọng (github_pat_expiry_check.sh,
  2eb5867a, cảnh báo ≤14 ngày). Action#1 (alert tức thời tại điểm fail push) để ngỏ, không gấp.

## Đang chờ
- `selfcheck-red-sweep-2026-10-09-can-user` (Wags/bus question, lệch thật SCL SpaceX bán tay
  30/09) — còn mở, mới sweep đầu tiên, chưa qua ngưỡng ≥2 sweep để escalate thêm. Không cần
  Mike hành động, chỉ theo dõi sweep Thứ Sáu tiếp (16/10).
- `annualization_basis_selfcheck.py` RED (Taylor, nợ ratchet mới từ R&D) — giao Taylor, theo
  dõi sweep tiếp.
- send_plan_report.sh retry drift-check riêng khi CANNOT_CHECK tồn đọng — đề xuất chưa làm,
  cần user/Winston xác nhận có đáng làm (rủi ro thấp, chỉ-cờ).

## Next
- Áp dụng Prevention #2 Pattern G NGAY từ retro ngày mai (10/10): đọc "Hành động đề xuất" của
  retro-2026-10-09.md trước khi viết bảng sự kiện mới của ngày 10/10.
- Thứ Hai 12/10 08:05 ICT: kiểm cron SBV/CCTG tuần chạy đúng + finalize nhắc STALE nếu cần.
- KHÔNG đặt wakeup thăm dò khi không có job nền đang chờ kết quả (user 10-05).

- [2026-10-09T21:02:37Z] weekly-ops-audit 10/10 xong (272b5001 drift selfcheck WC_ROOT, 6250dbc3 index). Theo dõi: custom30_yield_labels_selfcheck đỏ 10 ngày (Taylor, assertion label_asof E); xác nhận weekly investor report 09:00 hôm nay dùng prompt mới; SBV nguồn B Thứ Hai 12/10.
- [2026-10-10T04:23:05Z] [10-10] Weekly 05-09/10 rev1: bản nháp sửa ở worktree wt-1558282936489611354/reports (nhánh session/1558282936489611354, commit c28cc49d = PORTFOLIO_STEP trong check_report_cadence.sh, CHƯA merge/push; d0c429ab+55613a9f = 2 report, còn 1 sửa làm tròn chưa commit). CHỜ USER: (1) giữ/hoàn bản ghi bán SCL đã nạp vào dnse_raw_2026-09-30.jsonl (backup /tmp/wk1010/dnse_raw_2026-09-30.jsonl.bak_before_scl_backfill) rồi mới đóng question selfcheck-red-sweep-2026-10-09-can-user; (2) duyệt merge c28cc49d; (3) vá dividend_adjusted_return (DRI: Close/Price nhiễu sinh ex-date ma; cổng dùng giá vốn broker + cổ tức 0 khi UNVERIFIED => +37,81% thay vì +34,58%) rồi mới gửi lại 2 báo cáo qua delivery gate; (4) dòng TPB 30cp thưởng SpaceX −18,73% chưa sửa.
- [2026-10-10T14:40:51Z] [10-10 21:45 ICT] Trạng thái: công cụ tỉ suất §21 theo chuẩn tỉ suất tổng đã merge master 3863fecb; báo cáo ngày lấy tỉ suất từ công cụ §21 + cổng đọc dòng báo cáo ngày đã merge 8a1ef4d2; runbook/cron_registry cập nhật b7277191; template bảng danh mục (dòng tổng Cổ phiếu/Tiền/Trứng vàng/Nợ) merge 7dc05d53. Bản nháp sửa của 2 báo cáo tuần 05-09/10 nằm ở wt-1558282936489611354/reports, cổng PASS lệch 0,00, CHƯA gửi lại — đang chờ user quyết có gửi không. User đã chốt: không đính chính 3 báo cáo tuần 14/09→02/10. Chưa kiểm được trên dữ liệu thật: nhánh asof==hôm nay của raw_close_prices (lượt báo cáo ngày có lệnh đầu tiên, dự kiến ~15/10). Nợ đã ghi: cổng chưa đọc cột tổng sleeve; hai lần đọc dnse_raw giữa sinh báo cáo và cổng (F8).
- [2026-10-10T15:08:28Z] [10-10 22:10 ICT] 2 báo cáo tuần 05-09/10 bản sửa ĐÃ GỬI LẠI (user đồng ý 22:03): report_delivery_gate COMPLETE cả SpaceX (sha256 b17e4cc7…) và ZaloPay (829df3f1…), Discord Trading report + email; bản gốc lưu reports/*_weekly_report_2026-10-05_to_2026-10-09.md.bak_sent_20261010. Chuỗi việc báo cáo tuần + công cụ tỉ suất của ngày 10/10 đã đóng, không còn gì chờ user.
- [2026-10-10T16:24:03Z] [10-10 23:40 ICT] Đã trình user phương án 'tài khoản như quỹ mở' (NAV/đơn vị quỹ + sổ dòng tiền tự phát hiện + khoá lịch sử + chính sách đính chính + benchmark có cổ tức + chuỗi riêng ZaloPay trừ DGC). CHƯA sửa code. Chờ user chốt 5 điểm: (1) quy tắc chốt nạp/rút cuối ngày, (2) ZaloPay 2 chuỗi, (3) benchmark total-return, (4) ngưỡng đính chính, (5) không mô phỏng phí quản lý. Duyệt xong ⇒ dispatch Taylor giai đoạn 1 (sổ đơn vị quỹ, phải tái lập đúng −1,33% SpaceX từ đầu khi chưa có dòng tiền).
