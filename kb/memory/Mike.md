# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- Retro 2026-09-19 XONG (3 sự cố, Pattern B arch-review round2 auto-escalate ĐÃ ĐÓNG bằng gate cơ
  học, Pattern A "sửa 1 khái niệm tiền/dữ liệu quên enumerate consumer" lặp lần 2, theo dõi).

## Việc đang mở / cần theo dõi
1. **universe-pit-migration G7/G8/G9** — ~8.6 tuần treo, chờ user chọn A (dispatch Taylor làm
   dứt điểm) hay B (đóng hẳn). Liên quan: `executor.py::_load_gap_ref_data()` vẫn đọc
   `ticker_prune` cho `chase_cap_vol_scale_enabled` (vi phạm gate G8.1, materiality thấp, bus
   question `Taylor/executor-chase-cap-still-reads-ticker-prune-20260919` PENDING 0d).
2. **`Wags/selfcheck-red: anomaly_gate_prod_parity_selfcheck.py`** PENDING 0d (correctness PASS,
   chỉ fail coverage-gate — không phải regression, theo dõi).
3. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25) — `excluded_dividend_pending()` kẹp theo TỔNG account, có thể loại nhầm mã khác
   nếu quên dọn. Dùng chung bởi `compute_active_nav.py` VÀ `compute_park_trim.py` (đã hợp nhất
   09-19, tránh lệch sibling-consumer lần nữa).
4. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức, bảng BQ thật chưa tạo.
5. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — 2 bug vá chưa có selfcheck/commit xác nhận.
6. Code-quality Tầng 3 auto-dispatch wire vào code_quality_weekly.sh — theo dõi lần chạy tự động
   đầu tiên Chủ Nhật 2026-09-20 03:00 UTC.

## Còn mở không khẩn
- job_cancel_guard nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- append_event.sh JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).
- Pattern A (§25/§9b "sửa 1 field tiền/nguồn dữ liệu, quên grep hết consumer") lặp lần 2
  (08-19, 09-19) — chưa 2 retro liên tiếp, chưa escalate; lần 3 thì escalate ngay.

- [2026-09-20T02:35:04Z] 2026-09-20: xay xong vong feedback spend-report-weekly -> Taylor tu review+cai thien routing policy (kb/mike_model_routing.md), commit 330a02d7. An toan: quan sat 1 tuan chi .proposed, lap lai tuan 2 moi ap live + arch-review bat buoc. Theo doi lan chay dau CN 2026-09-27.
