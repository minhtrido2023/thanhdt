# PREREG v2 — Stress test survivorship R3, trọng số phantom THEO BOOK (job Taylor_20261020_091621)

EXPLORATORY. Không ghi `data/results_registry.md`, không `pin_ledger add`, không kết luận lại số pin.
Viết + md5 + commit TRƯỚC khi chạy overlay. Thư mục cũ `../survivorship_sensitivity_20261020/` giữ nguyên.
Kế thừa PREREG v1 (mô hình phantom, MC 2000 lần, seed 20261020, CRN, tái tạo METRIC <1e-9) trừ các thay đổi dưới.

## Thay đổi so với v1 (theo quant-skeptic)
1. **Trọng số phantom theo book** thay cho trung bình mỗi mã gồm 30 mã rổ.
   Đo từ ledger pin: với mỗi book b ∈ {BAL, LAG}, ngày d có n_b(d) ≥ 1 vị thế cổ phiếu mở (dựng từ TX theo cột `book`,
   net shares > 0): `w_b(d) = b_stocks_ref(d) / combined_nav(d) / n_b(d)`. **w_b = median của w_b(d) trên các ngày n_b ≥ 1**,
   đo riêng từng chân (4 chân) và dùng giá trị của chính chân đó, hằng số theo thời gian. Rổ ETF/custom30 không tính (không phải
   vị thế chọn lọc; phantom rổ ngoài phạm vi).
2. **Ba cấu hình trọng số**: BAL-only (w_BAL), LAG-only (w_LAG), **tổng hợp** = mỗi sự kiện phantom gán ngẫu nhiên cho
   book b với xác suất `s_b = mean_d n_b(d) / Σ_b mean_d n_b(d)` (trung bình số vị thế mở, chỉ ngày có ≥1), rồi dùng w_b.
3. **Một ngưỡng duy nhất 0,46pp** (sàn nhiễu W2b) cho nhãn và điểm giải λ*. Báo thêm λ* tại 0,50pp để so với v1.
   Nội suy tuyến tính trên lưới, điểm (λ=0, Δ=0) thêm vào.
4. Lưới λ ∈ {0,05; 0,1; 0,25; 0,5; 1; 2; 3}/năm × L ∈ {−30, −50, −80, −100}%; dạng "tuyến tính" (giá 1 → 1−L trong 365 ngày
   rồi đóng băng). Không chạy lại các kịch bản p_zone/p_hold của v1 (không đổi theo trọng số book là mục tiêu).
5. Nhãn: λ* nằm dưới/trên mức nắm thật ước tính được ghi như v1 (λ_eff ≈ 0,010 post-hoc, KHÔNG đăng ký trước, thiên lệch chọn mẫu);
   không dùng để tuyên bố "survivorship nhỏ".

## Control
4 chân chạy lại đúng lệnh pin (md5 4707bcbe/bcd0469f/537e349b/a6ba34d8), cache `data/bq_cache_asof20260729_postrestate`,
`$DNA_PYEXE`, `BQ_CACHE_THREADS=1`; chạy lại và so md5 + self-check 0 VND TRƯỚC khi đọc kết quả MC.
Nguồn dữ liệu: v1 đã tra data_registry; giá = cache pin (tương đương `tav2_pin.ticker_pin_202610`), không đọc `tav2_bq.ticker` live.
