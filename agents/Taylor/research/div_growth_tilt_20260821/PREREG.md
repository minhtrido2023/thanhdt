# PREREG — B_signal_v2: div-growth CAGR làm TILT LIÊN TỤC (industry-relative) thay vì cổng 3 bậc

Job `Taylor_20260821_113800`. **Commit file này TRƯỚC khi chạy `analyze.py`.**
Tiền đề: study `div-growth-signal-20260821` (NO-GO) — `IC(CAGR_3Y, BHAR_60) = +0.024`
(t_NW 1.84, IS 0.037 → OOS 0.012), nhưng hiệu nhóm `GROWING − DECLINING = −0.23pp` (NGƯỢC hướng).
Đọc: nhãn 3 bậc ngưỡng cứng ±5% là cách MẤT thông tin nhất; tín hiệu (nếu có) nằm ở chiều liên tục.

## 0. Cái được kiểm định lần này KHÁC gì lần trước
| | Study cũ (_111228) | Study này |
|---|---|---|
| Biến X | `cagr` thô, xếp hạng TOÀN THỊ TRƯỜNG | `z_cagr_ind` = z-score của `cagr` TRONG CÙNG ngành-tháng |
| Dạng dùng | cắt 3 bậc ±5% (H2) | tilt liên tục, không cắt bậc |
| Biến control | không | `prox` (yield-floor proximity, H2 mới) |

## 1. Dữ liệu — TÁI DÙNG, không dựng lại
- Panel: `../div_growth_signal_20260821/panel_enriched.csv` (đã pin, sinh từ `q_panel.sql`
  cùng job cha). universe_pit, cuối mỗi tháng lịch, 2014-01→, PIT dedup DIV theo
  `(ticker, ex, dividend_year, dividend_stage_vi)` lấy `public_date` mới nhất.
- `cagr = (div0/div3)^(1/3) − 1`, chỉ tính khi STABLE-3 (`n0≥1 ∧ n1≥1 ∧ n2≥1`) **và** `div3 > 0`
  (cột `has_cagr`). **Giữ NGUYÊN công thức, không sửa** (dispatch yêu cầu tái dùng).
- Ngành: `icb_code` trong panel là ICB **4 chữ số**. **ICB L2 := `icb_code // 100`**
  (19 nhóm trên panel; mã 3 chữ số như 533/573 hiểu là 0533/0573 ⇒ L2 = 5). Đây là quy ước
  ICB chuẩn (Industry L1 = 1 chữ số, Supersector L2 = 2 chữ số).
- `prox` (H2): **đúng công thức production** `trading_bot/due_diligence._yield_floor()` /
  `custom30_yield_labels._label_one()` — `prox = price / (div0 / (dep/100))`, với
  `price = price_t` (cột `Price` raw của panel; panel đã lọc `Price>0` nên COALESCE không đổi gì),
  `dep = deposit_rate_vn.current_deposit_rate(<ngày cuối tháng>)`.
  Ngữ nghĩa: `prox = lãi_suất_tiền_gửi / lợi_suất_cổ_tức`. `prox < 0.97` = BELOW_FLOOR (DY vượt
  lãi gửi), `> 1.03` = ABOVE_FLOOR. **Ngân hàng ICB 8355 LOẠI khỏi mọi phân tích có `prox`**
  (đúng như production loại khỏi diễn giải nhãn).

## 2. Định nghĩa `z_cagr_ind` (biến X chính)
Trong mỗi ô (tháng `t` × ICB L2):
- Lấy các dòng `has_cagr`. Nếu số dòng `< 5` ⇒ **bỏ toàn bộ ô** (không tính z).
- Nếu `sd(cagr)` trong ô `== 0` hoặc không hữu hạn ⇒ bỏ ô.
- `z_cagr_ind = (cagr − mean_ô(cagr)) / sd_ô(cagr)`, `sd` dùng `ddof=1`.
- Không winsorize (khai báo trước; robustness winsorize ±3σ chỉ là phụ, không đổi verdict).

## 3. Giả thuyết

**H1 (PRIMARY, 1 test duy nhất):** `IC(z_cagr_ind, bhar60_close) > 0.04` **và** Newey-West
`t ≥ 2.0`, trên scope FULL.
- IC = Spearman theo TỪNG cross-section tháng (gộp mọi ngành trong tháng đó), rồi lấy trung bình
  chuỗi IC theo tháng. Bỏ tháng có `< 10` quan sát hợp lệ hoặc `< 3` giá trị X phân biệt
  (MIN_XS = 10, y hệt study cha).
- NW lag = 3 (y hệt study cha).
- Y chính = `bhar60_close` (Close-vs-VNINDEX, 60 phiên). `bhar20_close` / `bhar60_price` là phụ.

**H1b (benchmark bắt buộc, không phải giả thuyết mới):** cùng công thức IC nhưng dùng `cagr` THÔ
trên **ĐÚNG mẫu con đã lọc ≥5-payer** ở H1. Mục đích: tách "z-score theo ngành có ích" khỏi
"lọc mẫu làm đẹp số". Nếu `IC(cagr thô | mẫu con) ≈ IC(z_cagr_ind)` thì industry-z KHÔNG thêm gì.

**H1c (phụ, khai báo trước để khỏi bị coi là fishing):** biến thể "khử ngành CẢ HAI VẾ" —
`IC(z_cagr_ind, bhar60 đã demean theo ngành-tháng)`. Đây là dạng nhất quán về mặt lý thuyết
(so sánh trong ngành với trong ngành). **KHÔNG dùng để quyết GO/NO-GO**; chỉ để diễn giải.

**H2 (secondary):** IC gia tăng của `z_cagr_ind` SAU KHI control `prox` **> 0**.
- (a) **Partial Spearman**: trong mỗi tháng, xếp hạng `z_cagr_ind`, `bhar60_close`, `prox`;
  partial correlation của 2 cái đầu cho `prox`. Gộp trung bình chuỗi tháng + NW t.
- (b) **Double sort**: trong mỗi tháng chia `prox` làm 3 phần (tercile) × `z_cagr_ind` trên/dưới
  trung vị; báo mean/median BHAR60 từng ô + hiệu (hi-z − lo-z) trong từng tercile prox.
- Mẫu H2 = mẫu H1 ∩ (`prox` hữu hạn) ∩ (`icb_code ≠ 8355`).

**H3 (sparsity check):** `pct_cells = #(ngành-tháng có ≥5 payer) / #(ngành-tháng có ≥1 payer)`
và `pct_rows = #dòng has_cagr giữ lại / #dòng has_cagr`. **SPARSE nếu `pct_rows < 30%`.**
(Dispatch viết "industry-months có ≥5 payers / tổng universe-months"; ở đây báo CẢ HAI mẫu số —
`pct_rows` là mẫu số dùng để quyết SPARSE vì nó mới đo được lượng thông tin thực sự mất đi.)

## 4. Luật quyết định (khoá trước, không thương lượng sau)
- **GO** = H1 thoả (IC>0.04 ∧ t_NW≥2.0) trên FULL **VÀ** IC(IS) và IC(OOS) **cùng dấu dương**
  **VÀ** H3 không SPARSE.
- **NO-GO** = `IC ≤ 0.04` **HOẶC** IS/OOS trái dấu.
- **WEAK** = H1 chỉ thoả ở 1 trong 2 giai đoạn (IS hoặc OOS) mà giai đoạn kia dương-nhưng-dưới-ngưỡng.
- **SPARSE** = H3 `pct_rows < 30%` ⇒ báo SPARSE kèm verdict H1 (không tự động GO dù H1 đẹp).
- Fallback KHAI BÁO TRƯỚC: nếu ICB L2 cho SPARSE, chạy LẠI y hệt trên **ICB L1** (`//1000`) và
  báo như **kết quả phụ có nhãn rõ**, KHÔNG được dùng để lật NO-GO thành GO.
- IS ≤ 2019-12-31 · OOS ≥ 2020-01-01.

## 5. Cái KHÔNG làm
- Không wire vào production dù verdict gì (dispatch chỉ định).
- Không gọi quant-skeptic (dispatch chỉ định).
- Không thử thêm ngưỡng payer (5 là con số dispatch khoá), không thử thêm horizon ngoài
  20/60 phiên, không tune `MIN_XS`.
