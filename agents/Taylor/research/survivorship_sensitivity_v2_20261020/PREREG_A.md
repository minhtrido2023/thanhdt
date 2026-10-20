# PREREG_A — sửa bug book_counts v2 (job Taylor_20261020_113646, EXPLORATORY)

Viết + md5 + commit CÙNG bản sửa `svs_overlay_v2.py` TRƯỚC khi chạy lại MC. Không sửa pin/registry/pin_ledger.
Kế thừa nguyên PREREG.md (md5 f9092a9e): mô hình phantom, MC 2000, seed 20261020, CRN, lưới λ×L, ngưỡng 0,46pp (+0,50 so v1).

## Bug (quant-skeptic REFUTED, logs/verify_20261020_093922_1325283.log)
`book_counts()` đếm `CUSTOM_VN30EXVIC_PITG` (play_type ETF_PARK) vào n_b, trong khi giá trị rổ nằm ở `*_etf_ref`, không ở tử số
`*_stocks_ref` ⇒ vi phạm PREREG §1 ("Rổ ETF/custom30 không tính"), w_b thấp ~20% ở 2 chân park 0,3.

## Sửa (duy nhất)
1. n_b chỉ đếm TX có play_type ≠ ETF_PARK (≡ ticker không bắt đầu `CUSTOM_`; assert hai phân loại trùng nhau).
2. Assert mỗi ngày DAILY trừ ngày cuối (2026-06-19, TX thanh lý kết thúc audit): n_b>0 ⇔ b_stocks_ref>0 và số rổ mở>0 ⇔ b_etf_ref>0.
   Probe trước khi viết: lệch duy nhất ở ngày cuối (3106/3107 ngày khớp, chân p30_pin0 và p0_pin0).
3. Không đổi gì khác.

## Dự đoán kiểm được (trước khi chạy)
- 2 chân park 0 (537e349b, a6ba34d8) không có rổ ⇒ kết quả MC phải TRÙNG với bản cũ (so `out_mc_results_SUPERSEDED_bookcount_bug.csv`).
- p30_pin0: w_BAL ≈ 2,57%, w_LAG ≈ 3,73%, MIX λ*@0,46 L−50 ≈ 0,20, L−100 ≈ 0,12 (số skeptic tự tính lại). Lệch đáng kể ⇒ báo, không chỉnh.

## Control
4 chân chạy lại đúng lệnh pin (run_leg.sh, như REPORT v2), md5 byte-identical 4707bcbe/bcd0469f/537e349b/a6ba34d8, self-check 0 VND,
TRƯỚC khi đọc kết quả MC. Số cũ (`*_SUPERSEDED_bookcount_bug.*`, REPORT v2 bảng λ*/trọng số park 0,3) = SUPERSEDED.
