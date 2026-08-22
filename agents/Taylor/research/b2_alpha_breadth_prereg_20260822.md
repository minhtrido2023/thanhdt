# PREREG — B2-ext: "Alpha sau khử beta của V2.4 có phụ thuộc breadth-tercile không?"

- **Job**: `Taylor_20260822_153901` (dispatch từ Mike) · **Ngày viết prereg**: 2026-08-22
- **Trạng thái khi viết**: đã đọc *script* B2 (`strategy_regime_matrix_20260822_b2.py`) và 3 con số
  alpha do dispatch trích (LOW +16,3 / MID +20,2 / HIGH +28,1pp; beta 0,43/0,59/0,55).
  **CHƯA** chạy bất kỳ tính toán nào của B2-ext, **CHƯA** mở `b2_cells.csv`/`b2_bh_tests.csv`.
- **Phạm vi**: PAPER-ONLY / R&D. Không đề xuất wire trong lần này kể cả khi CONFIRM.

---

## 1. Hypothesis

- **H0**: beta-adjusted alpha hằng ngày của V2.4 (BAL, LAG, COMB) **độc lập** với breadth-tercile
  → `alpha_HIGH − alpha_LOW = 0`.
- **H1 (một đuôi, có hướng — lấy từ observation B2)**: `alpha_HIGH − alpha_LOW > 0`
  (breadth cao → alpha cao hơn).
- Hướng H1 được **cố định trước** khi chạy, dựa trên B2 và cơ chế giả định: breadth cao = thị
  trường rộng khoẻ → momentum và earnings-drift dễ khai thác hơn; breadth thấp = rơi đồng loạt,
  hệ chỉ *bảo tồn vốn* tốt hơn (beta thấp) chứ không sinh alpha.

## 2. Nguồn dữ liệu (đã tra `mike/kb/data_registry/index.md` ở B2)

| Thứ | Nguồn | Ghi chú |
|---|---|---|
| Breadth | `tav2_mike.universe_pit` JOIN `tav2_bq.ticker` — **CANONICAL** (PIT) | tái dùng `b2_breadth.csv`, 2012-01-03→, cột `breadth = %(Close>MA200)` trong universe |
| Return series | `strategy_regime_matrix_20260822/panel_daily.csv` (pin R3, part-1 job `_101400`) | cột `r_bal / r_lag / r_comb / r_vni`, `regime` (DT5G) |

**Không dùng** bất kỳ cột `profit_*` nào (forward-looking).

## 3. Định nghĩa biến — chốt trước

### 3.1 Breadth-tercile (PIT, trễ 1 phiên)
1. `pct252_t` = phân vị của `breadth_t` trong **252 phiên TRƯỚC t** (không gồm t) — rolling, PIT.
2. **Nhãn dùng để phân loại phiên t là `btile_{t-1}`** (tercile của phiên liền trước):
   LOW = pct ∈ [0, ⅓), MID = [⅓, ⅔), HIGH = [⅔, 1].
   Lý do: `breadth_t` tính từ `Close_t` nên cùng phiên với `r_vni_t`; B2 đo
   `corr(breadth_t, r_vni_t) = +0,109`. Trễ 1 phiên loại bỏ đúng kênh nhiễm này.
   **Đây là khác biệt CHỦ ĐÍCH so với B2** (B2 dùng nhãn cùng phiên ở phần chính, chỉ để
   `btile_lag1` ở mục robustness).

### 3.2 Beta (rolling, PIT)
- `beta_t = Cov(r_strat[t-251:t], r_vni[t-251:t]) / Var(r_vni[t-251:t])`, OLS slope.
- Yêu cầu ≥126 quan sát hữu hạn trong cửa sổ, nếu không → NaN.
- **Dùng `beta_{t-1}`** để khử beta cho phiên t (không nhìn trước).

### 3.3 Alpha
- `alpha_t = r_strat_t − beta_{t-1} × r_vni_t` (Jensen alpha daily, không trừ risk-free — VN
  không có RF ngày sạch trong panel; ảnh hưởng triệt tiêu phần lớn khi lấy HIỆU giữa 2 tercile).
- Alpha năm hoá = `mean(alpha_t) × 249,2785` (hằng số SPY dùng thống nhất trong part-1/B2).
- Phiên chỉ vào mẫu khi **cả** `btile_{t-1}` **và** `beta_{t-1}` đều hữu hạn (mất warm-up ~252
  phiên đầu panel ⇒ mẫu hiệu dụng bắt đầu ~2015).

## 4. Kiểm định

**Test chính (9 tests)**: 3 chiến lược (BAL/LAG/COMB) × 3 cặp (HIGH−LOW, HIGH−MID, MID−LOW).

- Thống kê: `Δ = mean(alpha | tile=A) − mean(alpha | tile=B)`, năm hoá.
- **Block bootstrap L=20, 10.000 lần**, resample khối trên **chuỗi thời gian chung**
  `(alpha_t, btile_{t-1})` để giữ nguyên cấu trúc gán nhãn + tự tương quan; mỗi replicate tính
  lại `Δ*`.
- p **một đuôi**: `p = mean( (Δ* − mean(Δ*)) ≥ Δ_obs )` (dịch phân phối bootstrap về H0: Δ=0).
  Replicate thiếu 1 trong 2 nhóm → loại.
- **Đa kiểm định: BH FDR 10% trên đúng 9 test chính.** Test phụ (robustness/gradient/
  conditional-on-regime) báo p thô, **không** dùng để tuyên bố CONFIRM.

**Walk-forward**: IS = 2014-2019, OOS = 2020-2026 (mẫu hiệu dụng: IS ~2015-2019).

**LOO theo năm**: bỏ từng năm có mặt trong mẫu hiệu dụng, tính lại `Δ_HIGH−LOW`; đếm % năm cho
Δ dương.

## 5. Tiêu chí CONFIRM / REFUTE (chốt trước, không sửa sau)

Áp cho **COMB** (chiến lược production tổng hợp) là chính; BAL/LAG là bằng chứng hỗ trợ.

- **CONFIRM** khi ĐỦ CẢ 4: (a) `Δ_HIGH−LOW > 5pp/năm`; (b) `p < 0,05` một đuôi **và** qua BH FDR
  10%; (c) LOO > 75% số năm cho Δ dương; (d) OOS cùng dấu với IS.
- **REFUTE** khi BẤT KỲ: `p > 0,10`; hoặc LOO < 50% dương; hoặc OOS đổi dấu so với IS.
- **INCONCLUSIVE**: phần còn lại.

## 6. Kỳ vọng (ghi trước để đối chiếu)

- Dấu: kỳ vọng Δ_HIGH−LOW **dương** (từ B2).
- Độ lớn: B2 gợi ý ~+11,8pp (28,1 − 16,3) nhưng đó là alpha tính trên **CAGR gộp với beta
  toàn-ô**; đo lại bằng alpha ngày + rolling beta + nhãn trễ 1 phiên, tôi kỳ vọng **nhỏ hơn
  đáng kể**, khoảng **+3 đến +8pp**, và **không chắc** qua p<0,05 vì n_effective theo episode
  thấp (B2 đã cho thấy 0/27 ô qua BH 10% trên excess thô).
- Rủi ro alias: nếu `corr(breadth, DT5G state) > 0,5` thì gradient breadth có thể chỉ là regime
  đội lốt → bắt buộc chạy test conditional-on-state trước khi diễn giải.

## 7. Test phụ (khai báo trước, KHÔNG dùng để CONFIRM)

1. Corr(breadth, DT5G ordinal 0-4) + gradient breadth **trong cùng một DT5G state**.
2. Robustness beta: (a) beta toàn mẫu (một số duy nhất/chiến lược); (b) beta riêng theo tercile
   (đúng cách B2 làm) — kiểm tra kết luận có nhạy với phương pháp beta không.
3. Robustness tercile: phân vị **toàn mẫu** (non-PIT, có look-ahead) vs PIT rolling.
4. Robustness nhãn: `btile_t` (cùng phiên, như B2) vs `btile_{t-1}` (prereg) — đo đúng phần
   đóng góp của same-day contamination.
5. Phân rã: tỷ trọng đầu tư (`inv_bal`, `inv_lag`) theo tercile — alpha cao ở HIGH có phải chỉ
   vì hệ đầu tư nhiều hơn không.

## 8. Sai lệch so với prereg

Mọi thay đổi sau khi chạy phải ghi vào mục "SAI LỆCH SO VỚI PREREG" của báo cáo
`b2_alpha_breadth_20260822.md`, kèm lý do. Nếu không có → ghi rõ "không có".

## 9. Caveat cố định

- Backtest **gross**: chưa trừ phí/slippage/thuế (quy đổi thực tế: CAGR thật ≈ backtest − 1,5%).
  Hiệu ALPHA giữa 2 tercile ít bị ảnh hưởng hơn mức tuyệt đối, nhưng không bằng 0.
- Alpha ở đây là **mô tả**, không phải tín hiệu giao dịch: nhãn tercile biết được đầu phiên t
  nhưng bản thân alpha thì không.
- Kể cả CONFIRM: **không** đề xuất wire. Bước tiếp theo phải là prereg riêng về sizing +
  quant-skeptic (§18 coding_guidelines, mục 5 quy chuẩn backtest).
