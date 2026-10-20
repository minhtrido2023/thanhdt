# PREREG_FORWARD — Rating 8L G1, tích luỹ OOS đi tới (forward)

Job `Taylor_20261020_055002` · 2026-10-20 (giờ thật = giờ commit file này). Viết TRƯỚC khi chạy tracker lần đầu,
TRƯỚC khi nhìn bất kỳ sự kiện nào có eff_date > 2026-07-31. Chỉ đạo Mike (user duyệt 2026-10-20), theo
`killer_objection` + `recommended_reruns[0]` của quant-skeptic (log `mike/logs/verify_20261020_045855_374538.log`).
PAPER-ONLY. Không đổi gate/luật production, không đề xuất wire. File này KHÔNG được sửa sau commit; sai lệch
(nếu có) khai ở REPORT của lần review, mục riêng.

## 1. Giả thuyết và đại lượng — duy nhất một phép thử quyết định
- H1: E[δ] ≠ 0, với δ = CAR_G1[2,40] − mean(CAR_G0 cùng ô), ô = (quý lịch của eff × nhóm momentum 5 × nhóm SUE 5 ×
  ngân hàng). G1 = rating quý trước ≥ 4 → quý này ≤ 3; G0 = rating không đổi.
- Benchmark **B3** = trung bình EW lợi suất ngày các mã `in_universe` (tav2_mike.universe_pit) có giao dịch cùng phiên,
  LOẠI chính mã sự kiện. AR = r − B3. Vào ở close phiên +1 (phiên 0 = phiên đầu ≥ eff).
- **Cửa sổ quyết định DUY NHẤT: CAR[2,40].** CAR[2,20] chỉ in để mô tả, không vào verdict.
- Code phân tích = `event_study_v2_frozen.py` (bản copy NGUYÊN của `rating_8l_lag_p2v2_20261020/event_study_v2.py`),
  md5 `a857d81bfc95be8b7dac507f6cf9dbad`. Lúc review CHỈ được đổi: `EFF_MIN` = 2026-08-01, `EFF_MAX` = mốc cắt
  review (§4), đường dẫn raw (kéo mới lúc review), và in thêm thống kê §3 cho G1 [2,40]. Không đổi: luật loại ca,
  phân vị (theo quý lịch), ô khớp, B3, bootstrap theo quý (2.000 lần, seed 20261020), cách tính SUE/momentum/ADV.
- Luật loại ca giữ nguyên: (a) RD < cuối quý HOẶC RD ≤ RD quý trước, (b) RD trong 0-7 ngày sau cuối quý (gồm cụm Q1 RD
  đầu tháng 4), (c) RD NULL; mã phải in_universe tại phiên 0; <80% phiên có giao dịch trong [−60,+40] hoặc |r|>40%/phiên
  ⇒ loại (luật của event study, KHÔNG dùng cho chiến lược giao dịch).
- **Tập sự kiện: eff_date > 2026-07-31** (cửa sổ vòng 1/2 dùng eff ≤ 2026-07-31). Không bao giờ gộp với dữ liệu cũ.
- Một khác biệt có chủ ý với vòng 1/2: rating/eff được ghi nhận BẰNG ẢNH CHỤP lần đầu tracker thấy dòng đó
  (`first_seen`, append-only). Lúc review, rating dùng để xếp G0/G1 = giá trị trong ledger forward, KHÔNG phải giá trị
  `fa_ratings_8l` lúc review (bảng có thể restate). Đây là PIT thật, sửa đúng giới hạn "NP vintage hôm nay" của vòng 2.
  Code frozen đọc `fa.parquet` ⇒ lúc review dựng `fa.parquet` từ ledger forward (cột ticker, time=eff, route, rating) +
  dòng quý liền trước (rating `prev` lấy từ ledger). Đây là thay đổi NGUỒN đầu vào duy nhất cho phép.

## 2. Nguồn giá — cổng fail-closed
- Giá: `tav2_bq.ticker` (Close/Price/Volume) CHỈ khi qua cổng độ phủ: tại phiên mới nhất, số mã có giá ≥ 1.200 VÀ
  ≥ 98% số mã in_universe của universe_pit ở phiên đó có giá. Trượt ⇒ dùng pin tháng mới nhất `tav2_pin.ticker_pin_YYYYMM`
  nếu pin đó qua cùng cổng và phủ tới mốc cắt; nếu không ⇒ HOÃN review, không tính CAR.
  (Lý do: 2026-10-20 `tav2_bq.ticker` mất 243 mã; raw của vòng 1/2 kéo lúc 10:48 đã thiếu 113/770 mã universe.)
- Ghi vintage (bảng, snapshotTime hoặc giờ kéo) + md5 mọi raw trong REPORT review.

## 3. Cỡ mẫu tối thiểu N_min và tiêu chí kết luận (khai TRƯỚC)
Đo trên `rating_8l_lag_p2v2_20261020/out_v2_events.csv` (cùng code; LƯU Ý: đo trên raw đã thiếu 113 mã — dùng làm số khoá,
KHÔNG tính lại kể cả khi chân control vintage pin cho σ khác):
- σ_iid(δ, G1, [2,40]) = **0,1787** (N = 938 sự kiện có ô khớp); hệ số thiết kế DEFF = N/N_eff = 938/692 = **1,355**
  (N_eff từ SE cluster theo quý của vòng 2).
- Công thức (hai phía, α = 0,05, power 1−β = 0,80, δ* = +1,0%):
  **N_min = DEFF · ((z_{0,975} + z_{0,80}) · σ / δ*)² = 1,355 · ((1,960 + 0,842) · 0,1787 / 0,010)² ≈ 3.398** sự kiện G1
  có ô khớp (iid: 2.507).
- Tốc độ tích luỹ đo được (vòng 2): 938 G1 khớp / 48 quý ≈ 19,5/quý (2021-2025: 74-123/năm). ⇒ ước lượng thời gian
  đạt N_min ≈ 3.398 / ~90 mỗi năm ≈ **35-40 năm** (ước lượng). Khai thẳng: với δ* = 1,0% phép thử forward KHÔNG đạt
  power 80% trong bất kỳ chân trời thực tế nào. Thiết kế vẫn được khoá để mọi lần nhìn sau này không chọn lại được.
- **Verdict (theo thứ tự, áp ở mỗi lần review):**
  1. **"có (forward xác nhận)"** CHỈ khi N ≥ N_min VÀ p_boot < 0,05 VÀ δ > 0 (cùng dấu vòng 2).
  2. **"không có (futility)"** khi N ≥ 300 VÀ cận trên CI95 bootstrap quý của δ < 0 (dấu ngược hẳn) — dừng chương trình.
  3. **"không phân biệt được (thiếu N)"** mọi trường hợp còn lại, kể cả khi p < 0,05 mà N < N_min (lần nhìn tạm KHÔNG
     được tuyên bố "có": không có alpha-spending; nhìn tạm = mô tả).
- Mỗi review in: N G1/G0, số quý, δ [2,40] + CI95 + p_boot, δ [2,20] (mô tả), tỉ lệ sự kiện có ADV ≥ 5 tỷ.

## 4. Lịch review
- Mốc cắt review: eff ≤ phiên cuối của dữ liệu − 42 phiên (đủ +40 và +1 phiên đệm).
- Review định kỳ NĂM: 2027-10-20, rồi mỗi 12 tháng. Mỗi review ghi 1 finding bus `rating-8l-forward-review-<YYYYMMDD>`.
- Điều kiện dừng: verdict 2 (futility), HOẶC user/Mike chấm dứt, HOẶC `fa_ratings_8l` đổi định nghĩa rating (ghi rõ
  ngày; sự kiện sau mốc đó không còn cùng biến ⇒ dừng, không nối).
- Tracker chỉ GHI sự kiện + CAR mô tả từng sự kiện; KHÔNG tự ra verdict.
