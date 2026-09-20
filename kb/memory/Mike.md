# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

# Working memory — Mike
> Cập nhật mỗi khi đổi mạch việc. Bơm vào đầu phiên của Mike.

## Ưu tiên hiện tại
- Go-live V2.4 lever LIVE từ 08-24: capit_margin_lever.enabled=TRUE. Ngày có CAPIT margin phải chạy
  approve_margin_day.py TRƯỚC bot.
- Retro 2026-09-20 XONG (3 sự cố, Pattern B arch-review round1→round2 tiếp tục hoạt động tốt —
  2 ca độc lập trong ngày tự đóng không cần gate; Pattern A lặp lần 3/2 ngày liên tiếp, theo dõi
  tới 2026-09-22, KHÔNG escalate cứng).

## Việc đang mở / cần theo dõi
1. **`test_trading_bot.py:353` — cùng lớp bug với config.py hard-boundary fix (đọc field thô
   `p["broker"]`/`p["mode"]` thay vì `make_broker()`)**, arch-reviewer ghi rõ "cần dispatch riêng"
   09-20 nhưng CHƯA có ai dispatch fix. **Nếu chưa sửa trước 2026-09-22 → escalate ngay** ở retro
   ngày đó (`retro-pattern-recurring-test-scope-followup-Nd`).
2. **universe-pit-migration G7/G8/G9** — ~9 tuần treo, chờ user chọn A (dispatch Taylor làm dứt
   điểm) hay B (đóng hẳn). G8.1 (`executor.py::_load_gap_ref_data()` đọc `ticker_prune`) ĐÃ ĐÓNG
   09-20 (migrate sang `tav2_bq.ticker` superset + guard recency/contiguity, commit `fd3f5597`).
3. **`Wags/selfcheck-red: anomaly_gate_prod_parity_selfcheck.py`** PENDING (correctness PASS, chỉ
   fail coverage-gate — không phải regression, theo dõi).
4. **excluded_dividend_receivable[DGC]** (ZaloPay) cần dọn config sau khi tiền DGC về thật
   (~2026-09-25) — dùng chung bởi `compute_active_nav.py` VÀ `compute_park_trim.py` (đã hợp nhất
   09-19).
5. Treasury buyback/corp_action mở rộng (Taylor branch feat/treasury-share-events-table) — chờ
   user duyệt chính thức, bảng BQ thật chưa tạo.
6. FiinPro/OShares harvest dừng 09-15 ở 4/59 lô — 2 bug vá chưa có selfcheck/commit xác nhận.
7. Spend-report feedback loop (routing policy tự cải thiện) — chỉ `.proposed` từ 09-20, giám sát
   2 tuần trước khi live, lần chạy tự động đầu Chủ Nhật 2026-09-27.

## Còn mở không khẩn
- job_cancel_guard nhánh systemd luôn đỏ dưới cron (theo dõi, không escalate).
- append_event.sh JSON cách ly viết tay vẫn thỉnh thoảng tái diễn dạng nhỏ (theo dõi qua retro).

