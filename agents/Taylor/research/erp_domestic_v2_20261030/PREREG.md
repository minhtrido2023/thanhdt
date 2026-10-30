# PREREG v2 — ERP nội địa + đo ảnh hưởng lên consumer DCF (job Taylor_20261030_041731)
Viết 30/10/2026 ~11:21 ICT, **TRƯỚC** khi chạy bất kỳ số v2 nào (commit trước `erp_v2.py` / `impact_v2.py`).
Chỉ nghiên cứu: không merge, không sửa main, không đặt lệnh. Patch (nếu có) ở nhánh `session/erp-domestic-dcf-20261030`.

## 0. Nói thẳng: PREREG này KHÔNG mù
- Viết SAU vòng 1 (`../erp_domestic_20261030/`, trung tâm 5,05) và SAU phán quyết quant-skeptic REFUTED
  (`mike/logs/verify_20261030_035917_2624322.log`). Mọi số cấp cửa sổ (ERP hình học/số học, tái định giá, rf TB)
  đã nằm sẵn trong `../erp_domestic_20261030/out_erp_history.csv`; D1 = 3,38, D2 = 6,54 đã biết.
- Vì vậy cái PREREG v2 khoá được KHÔNG phải dữ liệu, mà là **luật tổng hợp**. Luật dưới đây được chọn theo nguyên tắc
  (Blume, trọng số đều giữa hai họ, trung bình mọi cửa sổ thay vì chọn một), KHÔNG theo kết quả.
- **Kết quả tôi đã nhẩm trước khi commit** (để người đọc thấy tôi biết gì): luật chính cho trung tâm ≈ **5,4**
  (Ke β1 ≈ 12,2); biến thể thuần số học ≈ 6,1–6,2; thuần hình học ≈ 5,2; luật trung vị v1 ≈ 5,9. Nghĩa là tôi dự
  đoán trước **trung tâm KHÔNG đạt tiêu chí bền 0,5pp** (do trục hình học/số học) ⇒ sẽ phải báo dạng khoảng.
- Chống thiên lệch "Ke thấp" (hướng user mong): mọi độ nhạy được báo **theo cả hai chiều**, xếp riêng nhóm "đẩy
  lên" và "đẩy xuống"; ảnh hưởng lên consumer đo ở **cả hai đầu** của khoảng trung tâm, không chỉ ở điểm chính.

## 1. Đặc tả ERP v2 (việc 1–2)
Dữ liệu: dùng lại NGUYÊN cache bất biến vòng 1 (`../erp_domestic_20261030/data/`, md5 trong SELFCHECK v1); không kéo lại.
rf_c = 6,75 (giữ). π = 4,25. ERP đo so với Big-4 12M rồi quy về rf_c: x + (rf_TB_cửa_sổ − 6,75).

**(a) Cửa sổ — CỐ ĐỊNH 3 cửa sổ, lấy TRUNG BÌNH, không chọn một:** W = {2011-01-01→asof, 2013-12-31→asof,
2016-07-01→asof}, asof 2026-10-29, chân Big-4 12M. (2008→ bị loại vì không có chân lãi huy động; lý do giữ nguyên v1.)
Cả D3 và D4 dùng CÙNG bộ W (v1 dùng cửa sổ khác nhau cho D3/D4 — bỏ).

**(b) Hình học vs số học — quy tắc Blume (1974), chân trời T = 10 năm:**
B = G·(T−1)/(N−1) + A·(N−T)/(N−1), N = độ dài cửa sổ (năm), G = ERP hình học, A = ERP số học (TB tháng ×12);
nếu N < T thì B = G. Báo CẢ G, A, B cho mọi cửa sổ.
- D3 = mean_W[ B(G − ρ, A − ρ) ] + (rf_TB − 6,75), ρ = tái định giá/năm = ln(PE_cuối/PE_đầu)/N.
- D4 = mean_W[ B(G, A) ] + (rf_TB − 6,75) (không bỏ tái định giá).
- (Phép quy về rf_c làm bên trong mỗi cửa sổ, rồi mới lấy trung bình.)
- D1 = ERP ngầm định M-b (value-driver, g 5,5, ROE5Y **trung vị** rổ) — như v1. D2 = M-a (E/P + π 4,25) — như v1.
  Tập E/P robust {E2, E4, E6, E9, E10} như v1.
- **D1-ew (độ nhạy, theo yêu cầu)**: M-b với ROE5Y **trọng số vốn chủ** (BV = Price×OShares/PB) của từng rổ.

**(c) Luật trung tâm và dải:**
- Trung tâm C = ½·mean(D1, D2) + ½·mean(D3, D4) (họ ngầm định và họ lịch sử nặng ngang nhau; khắc phục lỗi v1 là
  trung vị-4-số thực chất = TB(D3, D4)).
- Dải = [min, max] của {D1, D2, D3, D4}.
- Sàn: C < 4,23 ⇒ đặt 4,23 và báo. Kiểm (không cắt): Ke(β1) = 6,75 + C so với lãi cho vay TB 10,7%.
- Giá trị đề xuất cho code = C làm tròn 0,25pp gần nhất; r = 6,75 + giá trị đó, KHÔNG làm tròn r thêm lần nữa
  (sửa lỗi 11,75 vs 11,8 của v1: mọi bảng dùng đúng r này).

**(d) Tiêu chí "đủ bền":** C bền ⇔ |C_Rk − C| ≤ 0,5pp với MỌI biến thể hợp lý Rk dưới đây (mỗi biến thể đổi MỘT trục):
- R1–R3: bỏ lần lượt từng cửa sổ của W.
- R4: thuần hình học (B = G). R5: thuần số học (B = A). R6: Blume T = 5.
- R7: D1-ew thay D1. R8/R9: g của D1 = 4,25 / 6,75. R10/R11: π của D2 = 4,0 / 4,5.
- R12: luật trung vị {D1..D4} (luật v1).
- Báo thêm (KHÔNG tính vào tiêu chí, vì bỏ hẳn một họ): R13 chỉ họ lịch sử mean(D3, D4); R14 chỉ họ ngầm định mean(D1, D2).
Không bền ⇒ **trung tâm báo dạng KHOẢNG [min, max] của C qua R1–R12**, và mọi phép đo ảnh hưởng (mục 3) chạy ở
C, ở đầu dưới và đầu trên của khoảng đó.

**Sửa sai sót v1 (bắt buộc):** bội số terminal báo theo Gordon đúng code `dcf_valuation.py:_fv_per_share`:
(1+g)/(r−g) (kèm 1/(r−g) để đối chiếu v1); TCB/DGC (và mọi mã khác) lệch OShares ⇒ liệt kê gửi data-ops, không sửa.

## 2. g_T đổi cùng lúc với r
Khung mới (tên `domestic_v2`): r = 6,75 + ERP_code (hằng, không ghép lãi huy động hôm nay);
g_T = min(CPI5y + GDP thực 15y, G_T_DOM), **G_T_DOM = π 4,25 + thực 1,25 = 5,5** (giữ nguyên số user nêu, không tinh chỉnh).
Kiểm g_T 5,5 (báo, không tối ưu):
- (i) ≤ GDP danh nghĩa dài hạn (CPI5y + GDP thực 15y tại asof, đúng hàm code dùng).
- (ii) so với tăng trưởng EPS danh nghĩa trên 1 đơn vị VNINDEX (= VNINDEX/VNINDEX_PE) CAGR 2011→, 2014→, 2016-07→ [BQ, cache v1].
- (iii) RONIC ≥ Ke: % mã phi tài chính universe_pit asof có ROE5Y ≥ r; ghi rõ mô hình FCFE của code KHÔNG trừ tái đầu tư
  theo g_T (RONIC ngầm định = ∞) ⇒ g_T càng cao càng lạc quan; đó là lý do g_T phải ≤ r − (biên an toàn).

## 3. Đo ảnh hưởng (việc 3) — chỉ MÔ PHỎNG, không chạy bot
Gọi CHÍNH `dcf_valuation.fair_value` + `classify_dcf` (không chép công thức), đổi khung bằng monkeypatch
`discount_rate`/`terminal_growth_mode` trong tiến trình nghiên cứu. Tài chính: bản chụp `ticker_financial.parquet`
(md5 ghi SELFCHECK) truyền qua `fin=`. Các khung:
- **L** legacy (code hiện tại: r = consumer_deposit_rate + 6,5; g_T = min(CPI+GDP, lãi huy động)).
- **R-only** (cảnh báo): r mới, g_T giữ cap theo lãi huy động.
- **N-c / N-lo / N-hi**: khung `domestic_v2` ở ERP_code, đầu dưới, đầu trên của khoảng trung tâm (nếu bền thì lo/hi = dải D).
Đo:
1. Snapshot asof 2026-10-29, rổ universe_pit (in_universe) phi tài chính, giá = Price [BQ cache v1]: % CHEAP / RICH /
   NOT_COMPUTED; % robust; số mã lật CHEAP↔RICH; số mã lật qua ngưỡng RICH SÂU MoS < −100% (`lag_dd_pack.DCF_RICH_DEEP_MOS`,
   cờ DD của LAG = đường tiền); FV trung vị thay đổi %.
2. Lịch sử quý 2014Q4→2026Q3 (rổ PIT từng quý): % CHEAP theo khung; IC Spearman cắt ngang MoS vs lợi suất kỳ sau,
   **chính = 4 quý tới (≈12T), phụ = 1 quý**, trung bình theo ngày; tách IS 2014–2019 / OOS 2020+. Lợi suất từ Close điều
   chỉnh [BQ] tại các ngày cuối quý (kéo một lần). `profit_*` KHÔNG dùng. Mã mất khỏi dữ liệu kỳ sau ⇒ loại (ghi số).
   Kỳ vọng khai trước: IC gần như không đổi (r, g_T giống nhau mọi mã cùng ngày); thay đổi chủ yếu ở MỨC (%cheap, cờ).
3. Danh mục/plan live: mã đang nắm + mã trong plan gần nhất (SpaceX, ZaloPay) + rổ custom30V hiện hành: dcf_check theo
   L vs N-c (status, MoS, robust, cờ RICH SÂU). Đọc file, không gọi broker, không chạy bot.
4. Call-site: liệt kê bằng `grep` (không chỉ srcwalk), phân loại: đường tiền (đổi hành vi plan/lệnh) / hiển thị / nghiên cứu.
   `custom30_yield_labels`: kiểm phụ thuộc bằng grep; không phụ thuộc ⇒ ghi "không đổi".
5. DGC tầng A r7 (`model_ke.py` 29/10): tái lập 21.407/32.925/41.779 (EV 29.817) lệch 0 rồi báo ở Ke = 6,75 + 1,11×{lo, C, hi}.

## 4. Patch đề xuất (việc 4)
Nhánh/worktree `session/erp-domestic-dcf-20261030`, KHÔNG merge. Một knob env `DCF_RATE_FRAME` ∈ {`legacy` (MẶC ĐỊNH),
`domestic_v2`}; r và g_T đổi CÙNG LÚC trong một knob (không có cách đổi riêng r). Selfcheck: (a) knob mặc định ⇒
fair_value/MoS/robust toàn rổ asof trùng byte với code main; (b) DGC r7 21.407/32.925/41.779 tái lập; (c) `domestic_v2`
⇒ khớp số mô phỏng mục 3; chạy 2 múi giờ (UTC, Pacific/Kiritimati).

## 5. Kỷ luật
Nhãn [SRC]/[BQ]/[UL]. Point-in-time, universe_pit. Tất định byte-for-byte ở 2 múi giờ ⇒ SELFCHECK.md.
Không p-value cho ERP (N độc lập ≈ 10–16 năm). IC chỉ mô tả độ chênh giữa khung, không phải kiểm định alpha.
