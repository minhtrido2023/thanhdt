# PREREG — Định giá lại DRI có điều chỉnh theo cung cao su (job `Taylor_20261027_084046`, 27/10/2026)

> Khai TRƯỚC khi chạy bất kỳ số FV mới nào. Commit file này trước `model_supply_adj.py`. Chỉ nghiên cứu: không lệnh,
> không pin, không sửa `model.py`/`model_q3.py`.
> **Đã xem trước khi khai (khai cho minh bạch):** BQ `ticker_financial` (NP_P0, Inventory_P0, Dividend_1Y theo quý của
> DRI/TRC/DPR/PHR) và chuỗi tháng Price/PE/PB của 4 mã từ `ticker`. ĐÃ tính tổng NP năm (DRI 2021–2025: 76,8 / 59,9 /
> 74,1 / 108,8 / 157,4 tỷ). CHƯA tính trung vị PE/PB theo pha, CHƯA chạy FV của lưới nào dưới đây.
> Nguồn: [BCTC3] BCTC HN Q3/26 · [SX] soát xét H1 · [SXKD] báo cáo SXKD DRI · [BQ] · [FEED] file `data/` · [UL] ước lượng
> · [NỀN] hiểu biết nền chưa kiểm lại · [DISPATCH] số do Mike nêu trong prompt, chưa đo.

## 0. Selfcheck bắt buộc trước khi đổi tham số
Tái lập đúng `REPORT_Q3_UPDATE` §6.2: Base **10.878**, kỳ vọng **11.031** bằng hàm cũ (chép logic `model_q3.py` §5, không
import, không sửa file cũ). Lệch > 1 đ ⇒ dừng. Chạy lại toàn bộ dưới `env -u TZ` và `TZ=America/New_York`; output phải
giống từng byte.

## 1. Khung chung (giữ từ `model_q3.py`, không tối ưu lại)
- SH 73,2 tr cp; giá 14.700 [BQ `Price` 26/10]. Net cash 30/09 sau cổ tức phải trả **162,8 tỷ** [BCTC3]. Dakruco 40 tỷ × 50%.
- LNST năm = (V×(P−C)/1e3 + 10 − SGA×0,9 + FIN)×(1−thuế); V = 14.000 t; SGA = BH+QLDN Q3×4; FIN = TC ròng Q3×4×0,83;
  thuế = hiệu dụng Q3 [BCTC3]. LN lõi = LNST − lãi tiền gửi trên net cash (5%×0,8). FCF = 90% LN lõi [UL].
- Giá bán P (tr đ/t) = 47,24 × RSS3/2,183 (neo giá 2025 [BCTN], RSS3 TB 2025 [FEED `rubber_monthly.csv`]).
- **Thay đổi cấu trúc so với model cũ (khai rõ):** model cũ gộp RSS3, r, giá vốn và "số năm đỉnh" vào 3 kịch bản cố
  định. Model mới tách thành trục độc lập, và thay "số năm đỉnh" bằng **đường giá theo lịch** (mục 2).
- Gốc thời gian: hôm nay ≈ 31/10/2026. Q4/26 chiết khấu t = 0,17 năm; năm lịch 2027 t = 0,67; năm k: t = 0,67 + (k−2027).

## 2. Kịch bản pha (Bobby: CYCLICAL_PEAK 60 / MID-tiếp diễn 40)
RSS3 xuất phát = TB Q3/26 = 2,753 [FEED]. "mid" = RSS3 chuẩn giữa chu kỳ (trục a).
| Kịch bản | 2027 | 2028 | 2029+ |
|---|---|---|---|
| **PEAK** (đỉnh do cung, về giữa chu kỳ) | mid + 0,5×(2,753−mid) | mid | mid |
| **MID-tiếp diễn** (giá cao kéo dài) | 2,753 | mid + 0,5×(2,753−mid) | mid |
- **Ghép mid với kịch bản (bảng CHÍNH):** PEAK ↔ mid ∈ {1,865; 1,97; 2,075} trọng số đều; MID ↔ mid ∈ {2,18; 2,30} trọng
  số đều. Lý do: MID-tiếp diễn của Bobby gắn với nền cung thắt cấu trúc ⇒ đáy/mức giữa chu kỳ cao hơn.
- **Bảng PHỤ (tách hẳn):** ma trận 5 mid × 2 đường giá, để người đọc tự ghép khác.
- **Trọng số:** {80/20, 60/40, 40/60} (PEAK/MID). 60/40 lấy từ Bobby — là **phán đoán chủ quan**, không phải xác suất đo
  được. Báo cả 3; KHÔNG chọn bộ nào sau khi thấy kết quả. Không có bộ "chính thức".

## 3. Các trục (báo riêng từng trục, không gộp vào kịch bản)
| Trục | Giá trị | Mặc định (tâm, chỉ dùng làm điểm xoay cho bảng độ nhạy) |
|---|---|---|
| (a) RSS3 mid | 1,865 · 1,97 · 2,075 · 2,18 · 2,30 | theo ghép mục 2 |
| (b) r | 10% · 12% · 13% | 12% (giữa lưới; model cũ dùng 13% ở Base) |
| (c) đời khai thác | L0 = niên kim 2027–2054 (28 năm) · L1 = L0 + gia hạn/tái canh sau 2054 xác suất 50% (vĩnh viễn, g=0) · L2 = như L1 xác suất 100% (cận trên) | L0 |
| Giá vốn/t (tại giá 47,24) | 32 · 34 · 36 | 34 |
| Quỹ lương | (a) cố định · (b) C_eff = C + 0,30×(P − 47,24) | (a) |
| Q4/26 LNST | Bear 13,7 · Base 49,7 · Bull 90,0 (tính lại bằng công thức `model_q3.py` §4) | Base |
| Tồn kho thành phẩm vượt mức | X = 0 · **1.717 t** · 3.370 t (mục 4) | 1.717 |
- **Kiểm r:** báo phần bù r − lãi tiền gửi. Lãi Big4 12T online **6,8%** [FEED `deposit_rate_vn_events.csv` 26/10]; Mike
  nêu ~7,4% effective [DISPATCH]. Không chỉnh r theo kết quả.
- **Kiểm tỷ giá/lạm phát (chỉ báo cáo, không đổi bảng chính):** (i) USD/VND TB 2016 vs 2026 [FEED `macro_usdvnd.csv`];
  (ii) trung vị RSS3 10 năm tính lại bằng USD thực 2026 (CPI Mỹ năm [NỀN, UL]) ⇒ ứng với ô mid nào trong lưới.
- **Chẩn đoán hiệu chỉnh (chỉ báo cáo):** giá vốn ngầm định để công thức LNST tái lập LNST 2025 [BQ tổng NP_P0 157,4]
  ở RSS3 2025.
- **Độ nhạy (câu "nhạy nhất với gì"):** từ cấu hình tâm, đổi MỘT trục qua toàn bộ giá trị của nó, báo biên độ FV
  (max−min). Trục có biên độ lớn nhất = nhạy nhất. Thêm: biên độ FV do trọng số (80/20 ↔ 40/60).

## 4. LN đỉnh còn lại + tồn kho
- Q4/26: cộng LNST Q4 × 0,9, chiết khấu t = 0,17.
- Tồn kho vượt mức X tấn bán trong H1/2027 (t = 0,4) ở giá P_2027 của đường giá; giá trị = X×(P − thuế×(P − 36,54)),
  36,54 = giá vốn/t Q3 [model_q3]. P < 36,54 ⇒ tự thành lỗ NRV (có lá chắn thuế). Stress: P_2027 −30%.
- Căn cứ X: (i) 1.717 t = chế biến Q3 − bán Q3 [SXKD]; (ii) đối chứng giá trị: Inventory_P0 30/09/26 183,9 vs 30/09/25
  124,2 tỷ [BQ] ⇒ ~59,7 tỷ vượt. X = 3.370 t = "giữ tới 8.000 t" [DISPATCH, chưa xác minh nguồn] − thành phẩm cuối 2025
  ~4.630 t [UL: 153,18 tỷ/33,11]; ca này giảm tấn bán Q4 base đi 1.653 t (để không đếm hai lần).
- Bảng tồn kho báo riêng; không trộn vào câu "nhạy nhất".

## 5. Kiểm chéo độc lập
**(i) PE/PB lịch sử theo pha:** pha của tháng m = phân vị RSS3 tháng m−1 trong cửa sổ 120 tháng trước đó (PIT):
PEAK ≥ 80, MID 40–80, TROUGH < 40. Mỗi mã DRI/TRC/DPR/PHR: trung vị PB và PE (chỉ PE 0–50) theo pha từ `tav2_bq.ticker`
cuối tháng (alias bảng). Giá ngầm định DRI = PB trung vị pha × BVPS 9.970 đ (VCSH mẹ 729,86 tỷ 30/09 [BCTC3]); PE pha ×
LNST chuẩn của từng kịch bản/SH. Cảnh báo khai trước: PHR/DPR có thu nhập đất KCN ⇒ không thuần mủ; TRC gần nhất; DRI
chỉ có dữ liệu từ 2017. Nhóm do tên chỉ định, không lọc universe ⇒ `universe_pit` không áp dụng (không dùng
`ticker_prune`).
**(ii) Lợi suất cổ tức:** cổ tức bền = min(1.000 đ, tỷ lệ chi trả lịch sử × EPS chuẩn từng kịch bản); tỷ lệ chi trả
lịch sử = trung vị (Dividend_1Y / EPS năm) DRI 2018–2025 [BQ]. FV_div = D / r (r lưới) và D × niên kim 28 năm. Khả
năng chuyển tiền: LNST riêng mẹ Q3 0,15 tỷ, Q2 55,70 [BCTC3, GT] — báo, không mô hình hoá xác suất.

## 6. Câu hỏi phải trả lời (mục 5 dispatch)
1. Khoảng FV dưới 3 bộ trọng số × r × đời khai thác. 2. Giá 14.700 cao/thấp hơn FV bao nhiêu % ở từng ô.
3. Nhạy nhất với giả định nào (đo theo mục 3). 4. Vùng mua ≤13.000 / ≤11.500 (Mike 21/10 [DISPATCH], không tìm thấy
trong KB/bus) đúng ở ô nào: "đúng" ⇔ FV ≥ ngưỡng (mua ở ngưỡng có biên an toàn ≥ 0).
Không suy FV từ giá/forward-return sau 27/10.
