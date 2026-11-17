# PREREG — B: "Cổ tức ổn định vượt lãi tiền gửi thì không bị giảm giá sâu" (viết 2026-11-17, TRƯỚC khi xem kết quả)

Phạm vi: kiểm khẳng định thực nghiệm của nhà đầu tư trên dữ liệu VN, rồi suy ra hàm ý cho spread
r − lãi huy động (mô hình đang dùng 6,1pp). PAT bị LOẠI khỏi mọi truy vấn (tránh vòng tròn, mù giá).
Lúc viết file này: CHƯA kéo giá, CHƯA tính lợi suất, CHƯA nhìn danh sách mã nào.

## Nguồn dữ liệu (đã tra data_registry)
- Universe: `tav2_mike.universe_pit` (ruleset_version=1), `in_universe=TRUE` tại ngày D. KHÔNG `ticker_prune`.
- Cổ tức tiền: `tav2_bq.corporate_action` `event_code='DIV'`, `event_status='executed'`, `value_per_share`
  (VND/cp GỘP), neo theo `exright_date` (ngày GDKHQ ≤ D ⇒ chắc chắn đã công khai tại D; bảo thủ: bỏ qua
  cổ tức đã công bố nhưng chưa tới GDKHQ). Dedup trùng tuyệt đối (ticker, exright_date, event_title_vi,
  value); khác title cùng ngày (Đợt 1 + Đợt 2) ⇒ CỘNG. KHÔNG suy cổ tức từ Close−Price hay Close/Price.
- Quy đổi DPS về cơ sở số CP tại D: chia cho Π(1+exercise_ratio) của ISS `Trả Cổ tức bằng Cổ phiếu` +
  `Cổ phiếu thưởng` (status ≠ not_executed) có exright_date trong (exdate_cổ tức, D]. Quyền mua/riêng lẻ/
  ESOP KHÔNG quy đổi (có trả tiền).
- Giá: `tav2_bq.ticker` — `Price` (thô, PIT) để tính yield tại D; `Close` (đã điều chỉnh cổ tức+tách,
  chỉ dùng TỈ SỐ giữa 2 ngày) để tính lợi suất tổng 12T và drawdown (đã bao cổ tức ⇒ BẢO THỦ theo hướng
  ủng hộ nhà đầu tư: ít phản ví dụ hơn so với đo giá thô).
- Lãi huy động 12T (benchmark chính): `deposit_rate_vn.deposit_events_df()` (Big-4 12M, step, ffill) —
  cùng khái niệm với neo 7,4% của mô hình. Caveat registry (b): 26 mốc neo hồi tố 1 lần ⇒ không PIT thật;
  chấp nhận vì là benchmark, không phải tín hiệu. Chuỗi bắt đầu 2011-01-01 ⇒ D sớm nhất = cuối 2011.
- Benchmark phụ (biến thể V3): SBV "Lãi suất huy động bình quân trên 12 tháng (cao nhất)" FiinPro
  (`idle_cash_proxy_20260927/fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv`), mốc tháng T chỉ dùng từ T+1.
- Ngành: `ticker.ICB_Code` tại D.

## Ngày quyết định
- CHÍNH: phiên giao dịch cuối cùng của mỗi năm 2011…2024 (cửa sổ 12T đủ) ⇒ 14 mặt cắt năm.
  2025 (cửa sổ chỉ ~10,5 tháng tới 2026-11) báo RIÊNG, không vào thống kê chính.
- Biến thể V5: cuối mỗi quý 2011Q4…2025Q3 (cửa sổ chồng lấn ⇒ CHỈ dùng làm độ nhạy; đếm phản ví dụ theo
  mã-năm duy nhất).

## Cohort P0 (chính)
- Cửa sổ W_k = (D−(k+1)·365, D−k·365], k=0..N−1; DPS_k = tổng DPS đã quy đổi trong W_k.
- Ổn định(N, X): DPS_k > 0 ∀k<N VÀ DPS_k ≥ (1−X)·DPS_{k+1} ∀k=0..N−2. P0: N=5, X=0,25.
- Yield y = DPS_0 / Price_D; điều kiện y > dep_D.
- Nhóm so sánh: "payer khác" = universe tại D có DPS_0>0 nhưng không thuộc cohort; "toàn universe".

## Biến thể (tất cả đều báo, KHÔNG chọn cái đẹp nhất) — N_trials = 8 (gồm P0)
V1 N=3,X=0,25 · V2 N=5,X=0,10 · V3 P0 nhưng benchmark SBV-cao-nhất · V4 P0 + payout DPS_0 ≤ EPS_D (EPS>0;
EPS từ `ticker.EPS` tại D, PIT chưa kiểm — ghi caveat) · V5 P0 quý · V6 P0 + y > dep+2pp ("vượt xa") ·
V7 N=3,X=0,10.

## Kết quả đo
- TR12 = Close(last ≤ D+365)/Close_D − 1 (lợi suất tổng, bao cổ tức).
- MDD12 = min Close trên (D, D+365] / Close_D − 1 (sụt tính từ giá mua tại D).
- Ngừng giao dịch: phiên cuối < D+335 ⇒ cờ DELIST; dùng giá cuối có (thật sự có thể tệ hơn) — báo số đếm.
- Phản ví dụ: MDD12 ≤ −30/−40/−50%; đồng thời báo TR12 ≤ −30/−40/−50%.
- Hành vi cổ tức sau D: DPS_fwd (D, D+365] quy về cơ sở D / DPS_0: giữ (≥0,9) / cắt (0,0.9) / bỏ (=0).
  Với phản ví dụ: kiểm "cắt trước hay sau đáy": so ngày đáy MDD với ex-date đầu tiên trong cửa sổ sau D và
  lượng DPS của nó (public_date bị ghi đè ⇒ KHÔNG có ngày công bố thật ⇒ chỉ ex-date, ghi giới hạn).
- r* ngầm: (i) r*_0 = y (g=0, sàn); (ii) r*_g = y(1+g)+g, g = CAGR(DPS_{N−1}→DPS_0) kẹp [0; 8%].
  Spread ngầm = r* − dep_D. (iii) Thực hiện: excess = TR12 − dep_D.
- Kiểm định: bootstrap KHỐI-NĂM (lấy lại năm có hoàn lại, mang theo mọi dòng của năm đó), B=5000,
  seed 20261117, CI 95% phân vị. N độc lập khai = số NĂM (14) cho câu hỏi tần suất/lợi suất; số mã-năm
  báo kèm nhưng không coi là độc lập.

## Walk-forward
IS = D ≤ 2019-12-31 (cửa sổ 2019 chồng sang 2020, ghi nhận), OOS = D ≥ 2020. Hiệu chỉnh spread s_IS =
trung bình excess thực hiện của cohort trên IS (và trung vị spread ngầm r*_g trên IS); OOS báo excess
thực hiện + CI, so với s_IS và với 6,1pp. Per-year leave-one-out trên trung bình excess. Không chọn cấu
hình để wire ⇒ DSR/PBO không bắt buộc (skill bước 13); vẫn khai N_trials=8 và báo cả 8.

## Luật phán quyết (khai trước)
Khẳng định K1 "chưa có công ty nào cổ tức ổn định vượt lãi gửi mà bị giảm sâu":
- SAI nếu cohort P0 có phản ví dụ MDD12 ≤ −30% ở ≥3 năm khác nhau (không tính DELIST) VÀ tần suất của cohort
  KHÔNG thấp hơn có ý nghĩa so với "payer khác" (CI chênh lệch chứa 0).
- MỘT PHẦN nếu có phản ví dụ ở ≥3 năm NHƯNG tần suất cohort thấp hơn có ý nghĩa so với payer khác.
- ĐÚNG nếu phản ví dụ MDD12 ≤ −30% xuất hiện ở ≤2 năm (đều là năm khủng hoảng toàn thị trường).
Khẳng định K2 "định giá (r=dep+6,1pp) không bao giờ bắt kịp thị giá" ⇒ hàm ý spread ngầm của nhóm này < 6,1pp:
- ỦNG HỘ nếu cận trên CI 95% của excess thực hiện cohort (IS và OOS) < 6,1pp VÀ trung vị spread ngầm r*_g < 6,1pp.
- KHÔNG PHÂN BIỆT ĐƯỢC nếu CI chứa 6,1pp.
- BÁC nếu cận dưới CI > 6,1pp.
Đề xuất hiệu chỉnh spread chỉ khi ỦNG HỘ ở CẢ IS lẫn OOS.

## Self-check độc lập
(1) Tính lại TTM DPS của 2 mã thanh khoản (không phải PAT) bằng đường khác: so DPS_0 từ corporate_action với
cột `ticker.Dividend_1Y` tại D (nguồn ETL độc lập) — báo tỉ lệ khớp ±10% trên toàn cohort. (2) Tính lại TR12
bằng đường Price thô + cộng cổ tức tiền + quy đổi CP thưởng cho vài dòng, so với Close-ratio.

## SỬA ĐỔI 1 (2026-11-17, sau fetch, TRƯỚC khi tính bất kỳ kết quả nào)
`tav2_bq.ticker` KHÔNG có cột `EPS`/`Dividend_1Y` (lỗi khai báo của tôi). Thay:
- V4 payout: EPS_ttm = Price_D / PE_D (PE trên cơ sở Price thô — skill bước 9) ⇒ payout = y·PE ≤ 1, PE>0.
- Self-check (1): so y tự tính với cột ETL `ticker.DY` (%) tại D thay cho `Dividend_1Y`.
Không đổi gì khác.
