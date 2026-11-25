# PRELOCK — chọn biến thể mc cho lvens2 pit2 (job Taylor_20261125_160331)
Commit TRƯỚC khi đo bất kỳ sai số mc nào và trước khi nhìn bất kỳ kết quả forward nào (không có kết quả forward nào trong job này — sổ paper chưa có tháng forward).

## Ứng viên (N trials = 4, khai đủ)
1. `strict` — code V3.1: mc = Price(D) × N_row (N của kỳ BCTC mới nhất ≤ D).
2. `step` — mc = Price(D) × N_row × [Close/Price tại D] / [Close/Price tại ngày BCTC] (hệ số điều chỉnh giá; lẫn cả cổ tức tiền).
3. `stepca` — mc = Price(D) × N_row × Π(1 + exercise_ratio) trên sự kiện `tav2_bq.corporate_action` (extract đóng băng, md5 trong REPORT):
   event_code=ISS, event_status≠not_executed, issue_method ∈ {Trả Cổ tức bằng Cổ phiếu, Cổ phiếu thưởng}, exercise_ratio>0,
   public_date ≤ D, ngày BCTC < exright_date ≤ D. KHÔNG BAO GIỜ dùng DIV (cổ tức tiền). Quyền mua KHÔNG tính (CP chỉ ra sau khi nộp tiền, tỉ lệ thực hiện không biết ở D).
4. `stepcar` — như 3 + quyền mua ("Quyền mua CP cho Cổ đông hiện hữu") tính đủ exercise_ratio (cận trên). Chỉ để đo, không phải ứng viên mặc định.

## Thước đo (định trước)
Sự thật = số CP PIT theo ngày `mike/data/fiinprox_oshares_pit_20260926.csv` (neo ex-right, đúng cơ sở giá đã điều chỉnh; registry: UNVERIFIED-PIT, khớp tỷ lệ 98,5%) tại D.
Mẫu = mọi (mã, tháng) in_universe (universe_pit) có sự thật, as-of 2014-01 … 2026-08 (fiinprox dừng 2026-09-25), mã nguồn BQ.
Thước chính: trung bình |log(N_mc / N_true)| trên mẫu. Phụ: tỉ lệ ô |err|>5%; lặp lại riêng nhóm có sự kiện (N_row ≠ N_true).
Thước phụ 2: N của kỳ BCTC kế tiếp (OShares restate ⇒ chỉ tham khảo).

## Luật chọn (khoá)
Chọn biến thể có thước chính nhỏ nhất trong {strict, step, stepca}. `stepcar` chỉ được chọn nếu tốt hơn stepca ≥ 10% tương đối VÀ tỉ lệ ô |err|>5% không tăng.
Nếu chênh giữa hạng 1 và 2 < 2% tương đối ⇒ chọn biến thể ĐƠN GIẢN hơn theo thứ tự strict < stepca < step (step lẫn cổ tức tiền nên xếp sau).
Không chọn theo "gần vp2" (vp2 không PIT).

## Sửa E ngân hàng (không phải trial — sửa lỗi dữ liệu; luật SỬA SAU khi thấy lan truyền ở bản đầu, xem REPORT §2)
Dòng có E = BVPS×OShares (không có nợ ngắn/dài hạn ⇒ ngân hàng…): nếu log(E_bo / E_trước) < −0,07 với kỳ trước ≤ 200 ngày ⇒ BVPS đã bị ghi theo cơ sở CP sau sự kiện
⇒ E = E_trước + NP_P0 (lãi quý, đại lượng tổng, không phụ thuộc số CP). Chỉ dùng dòng ≤ D. N (pick_n) vẫn tính từ E gốc để không kéo số CP tương lai vào.
