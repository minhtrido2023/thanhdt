# PREREG — Định giá lại DRI lần 2, sửa lỗi skeptic (job `Taylor_20261027_093047`, 27/10/2026)

> Khai TRƯỚC khi chạy bất kỳ FV mới nào; commit file này trước `model.py`. Chỉ nghiên cứu: không lệnh, không pin, không
> sửa file cũ (đọc `../dri_val_supply_adj_20261027/` và `../dd_DRI_20261027/`, không ghi vào đó).
> **Đã xem trước khi khai (khai cho minh bạch, không phải FV):** (1) `out.txt` bản trước (FV 14.301 và mọi ô của nó);
> (2) BCTN 2025 và BCTN 2024 của DRI (tải từ vietstock, trích nguyên văn ở `src/`): bảng KH/TH, giá vốn/t, tấn bán,
> giá USD/t, KQKD hợp nhất 2023–2025, "phí chuyển lợi nhuận về nước 10%"; (3) GPM_P0 theo quý 2020–2026 [BQ, snapshot
> `../dri_val_supply_adj_20261027/data/`]; (4) Wendy (legal-vn) trả lời thuế Lào. CHƯA chạy FV của lưới nào dưới đây.
> Nhãn: [BCTC3] BCTC HN Q3/26 · [BCTN25]/[BCTN24] báo cáo thường niên · [BQ] · [FEED] `data/*.csv` · [WENDY] · [UL] ước
> lượng/giả định chưa có nguồn · [NỀN] hiểu biết nền chưa kiểm.

## 0. Selfcheck (dừng nếu lệch > 1 đ)
(a) Hàm cũ `model_q3` §5 ⇒ Base **10.878**, kỳ vọng **11.031**. (b) Model bản trước, đúng tham số của nó (ghép mid↔kịch
bản, C 34, k 0, V 14.000 phẳng, không rò rỉ) ⇒ **14.301**. Hai số phải tái lập TRONG `model.py` mới (chép logic, không
import). Rồi cầu nối từng bước 14.301 → tâm mới. Chạy dưới `env -u TZ` và `TZ=America/New_York`, output giống từng byte.

## 1. Sửa (a): BỎ PHÉP GHÉP — mid là MỘT phân phối chung cho cả hai đường giá
- Đường giá (giữ định nghĩa bản trước): RSS3 xuất phát 2,753 (TB Q3/26 [FEED]).
  PEAK: 2027 = mid + ½(2,753−mid), 2028+ = mid. MID-tiếp diễn: 2027 = 2,753, 2028 = mid + ½(2,753−mid), 2029+ = mid.
- Trọng số đường giá {80/20, 60/40, 40/60} chỉ quyết định 2027–2028. Mọi ô dùng CÙNG mid cho hai đường.
- **Mid thử {1,865; 1,97; 2,075; 2,18}** — báo FV RIÊNG từng mid, KHÔNG gộp/không gán xác suất cho mid:
  | mid | Cơ sở |
  |---|---|
  | 1,865 | trung vị RSS3 **danh nghĩa** 10 năm (10/2016–09/2026) [FEED] |
  | 1,97 | điểm giữa 1,865–2,075 (không có cơ sở độc lập; là bước lưới) |
  | 2,075 | trung vị **danh nghĩa** 5 năm (10/2021–09/2026) [FEED] |
  | 2,18 | TB 2025 [FEED]; ≈ trung vị 10 năm **thực** quy về USD 2025 (CPI Mỹ [NỀN/UL] — model sẽ in số này) |
  Model giữ chi phí VND và tỷ giá ở mức 2025 cố định đến 2054 ⇒ dòng tiền về bản chất là **"tiền 2025"**; so mid với
  trung vị THỰC là nhất quán hơn danh nghĩa, nhưng r 10–13% là danh nghĩa ⇒ có độ lệch thực/danh nghĩa, sẽ ghi rõ, không sửa lưới.

## 2. Sửa (b): giá vốn/t và hàm LNST
**Định nghĩa C trong model = giá vốn hàng bán (GVHB) hợp nhất / tấn cao su bán** (BH+QLDN trừ riêng qua SGA). Số đo
cùng định nghĩa: 2024 281,49/10.108 = 27,85 · 2025 422,04/14.008 = 30,13 · 9T/26 377,40/11.989 = 31,48 [BCTN24/25,
BCTC3; tử số gồm cả GVHB điều/sầu riêng ⇒ hơi cao]. "33,11" của BCTN25 (và 31,98 của BCTN24) là "giá thành hàng
bán" có cộng chi phí bán hàng (chênh với GVHB/t đều ≈ 41,7 tỷ cả 2024 lẫn 2025 ⇒ cùng định nghĩa khác) — dùng 33,11
cùng với SGA riêng là đếm hai lần. Model sẽ in phép đối chiếu này.
- **Hàm chi phí:** C(P, V) = [C_ref + k·(P − 47,24)] × [(1−f) + f·V0/V], V0 = 14.000.
  - C_ref = GVHB/t tại giá 47,24 (giá 2025) và V0. **Lưới C_ref {31; 32; 33}**, đối chứng 34 (bi quan, bản trước) và
    "C_cal" (hiệu chỉnh để LNST 2025 mô hình = 157,4 [BQ]; báo, không làm tâm).
  - **k = hệ số truyền giá vào chi phí {0; 0,3; 0,6}.** k=0 ⇔ hàm cũ (dốc 248 tỷ/($/kg)). 0,3 ≈ chênh (C,P) 2025→9T/26.
    0,6 ≈ biên gộp không đổi (C/P 0,61–0,64 đo 2024/25/9T26; GPM 36–43% 2021–25 [BQ] dù RSS3 1,58–2,27).
  - **f = tỷ trọng cố định của GVHB {0,3; 0,5; 0,7}, tâm 0,5 [UL]** — KHÔNG đo được: 2024→2025 V +39% nhưng C/t tăng
    (nhiễu giá/lương/LAK). Chỉ có tác dụng khi V giảm (mục 3).
- **Chọn k (khai trước, không đổi sau khi thấy FV):** backcast LNST 2021–2024 (2025 là năm hiệu chỉnh mức) với:
  RSS3 TB năm [FEED]; P_y = 47,24 × RSS3_y/2,183 × FX_y/FX_2025 [FEED macro_usdvnd]; V_y = 14.000 cho 2021–2022 [UL],
  14.447 cho 2023 (suy từ "giảm 30,03%" [BCTN24]), 10.108 (2024) và 14.008 (2025) [BCTN]; SGA/FIN/khác/thuế = giá trị
  model (Q3/26×4, ×0,9); mức C_ref = C_cal riêng từng k (để 2025 khớp đúng). **Tiêu chí: RMSE 2021–2024 nhỏ nhất.**
  Báo sai số từng năm 2021–2025 cho mọi k. Bảng FV báo cho **k được chọn** VÀ **k=0 (hàm cũ)**.
  Chẩn đoán phụ (không dùng để chọn): backcast cùng hàm nhưng dùng giá USD thực DRI 2024 (1.788) / 2025 (1.857) [BCTN].

## 3. Sửa (c): sản lượng theo tuổi vườn
- Không tìm thấy bảng năm trồng/diện tích theo tuổi trong BCTN 2025, BCTN 2024, BCTC Q3 hay `dd_*`. Có: 8.592,3 ha cao
  su; "2015: 80% diện tích đã đưa vào khai thác"; thoả thuận dự án 19/11/2004; "diện tích cao su đang dần bước vào chu
  kỳ thanh lý"; tái canh 37,77 ha năm 2026; thu mua tiểu điền ~2.000 t/2026 "bù đắp sản lượng thiếu hụt khi vườn cây
  đi vào lộ trình thanh lý"; cam kết khoanh nuôi phần đất rừng bảo tồn khi hết chu kỳ 1 [BCTN25]. ⇒ trồng chủ yếu
  ~2005–2010 [UL].
- **Đường sản lượng = GIẢ ĐỊNH CHƯA CÓ NGUỒN:** V = 14.000 t tới năm bắt đầu suy giảm, sau đó giảm d %/năm.
  Lưới **d ∈ {0; 2%; 3%} bắt đầu 2035**, tâm 2%. Stress ngoài lưới (báo riêng): 3%/năm từ 2030.
  Năm 2026 KH khai thác 13.800 t [BCTN25] ⇒ 14.000 là tâm hợp lý (2024 11.116, 2025 15.153 [BCTN]).
- Chi phí/t tăng khi V giảm theo f (mục 2). SGA giữ cố định (thận trọng).
- **Tái canh / sầu riêng / gỗ thanh lý / thu mua tiểu điền: LOẠI khỏi FV** (không có số dòng tiền; khác 10 tỷ/năm
  trong model cũ được giữ nguyên như bản trước). Tái canh sau 2035 khó cho mủ trước 2054 ⇒ không cộng giá trị.

## 4. Sửa (c tiếp): rò rỉ khi chuyển LN từ Lào
- **Phí/thuế chuyển LN w ∈ {0; 10%}, tâm 10%** áp lên FCF hoạt động (LN lõi × 0,9). Nguồn 10%: BCTN24 "Lào đang áp dụng
  phí chuyển lợi nhuận về nước 10%/tổng lợi nhuận chuyển về"; Wendy: Luật thuế thu nhập Lào 67/NA ⇒ cổ tức 10%, DTA
  VN–Lào 1996 Điều 10 trần 10% [WENDY, trung bình–cao]. **Chưa xác minh** khoản này đã nằm trong thuế hiệu dụng hợp
  nhất (Q3/26 18,3%) hay chưa — w=0 là ca "đã nằm trong", w=10% là ca "chưa". Không áp lên tiền ròng hiện có.
- **Haircut tiền ở Lào h ∈ {0; 15%; 30%}, tâm 15%** áp lên tiền gửi tại NH Lào 30/09: có kỳ hạn 154,66 + không kỳ hạn
  42,07 = **196,7 tỷ** [BCTC3] (nguyên tệ chỉ công bố 60,48 tỷ USD ⇒ áp lên toàn bộ là cận trên). Stress ngoài lưới:
  h áp thêm lên FCF hoạt động.

## 5. Giữ nguyên từ bản trước (đã selfcheck)
SH 73,2 tr; giá 14.700 [BQ 26/10]; net cash 162,8 tỷ sau cổ tức phải trả [BCTC3]; Dakruco 40×50%; SGA/FIN/thuế Q3×4;
Q4/26 Base 49,7 (Bear/Bull độ nhạy); FCF 90% LN lõi [UL]; L0 = niên kim 2027–2054 (L1 độ nhạy); r {10; 12; 13%}, tâm
12%. **Tồn kho vượt X {0; 1.717; 3.370} t, tâm 1.717**, cách tính như cũ; sửa nhãn: tồn kho 30/09/26 183,9 tỷ là
**[BCTC3]** (snapshot BQ chỉ tới Q2/26), 30/09/25 124,2 [BQ].

## 6. Báo cáo (không ép về một con số)
1. **FV theo từng mid** (4 cột) × trọng số đường giá (3 hàng), ở tâm: r 12, L0, C_ref 32, k chọn, f 0,5, d 2%/2035,
   w 10%, h 15%, X 1.717, Q4 Base. Cùng bảng với k=0.
2. Khoảng FV mỗi mid trên toàn lưới khai trước (r × C_ref{31,32,33} × k{chọn, 0} × f × d × w × h × trọng số; X, Q4 ở tâm),
   báo P10–P90 và min–max (phân vị lưới KHÔNG phải xác suất). Đối chứng C_ref 34 và C_cal báo riêng.
3. 14.700 so FV (%) từng mid. **Độ nhạy một-trục** quanh tâm (mid để riêng, báo ở mid 1,97 và 2,075).
4. **Biên an toàn vùng mua**: FV/ngưỡng − 1 cho ngưỡng 13.000, 11.500 và PB ≤ 1 = BVPS **9.971** (VCSH mẹ 729,86 tỷ
   30/09 sau ghi nhận cổ tức phải trả / 73,2 tr cp [BCTC3]) — mọi PB trong báo cáo dùng BVPS này. Kèm PB trung vị theo
   pha (bản trước) để nói ngưỡng nào thường chỉ xuất hiện ở pha TROUGH.
5. Phân loại rõ ĐO ĐƯỢC vs PHÁN ĐOÁN (mid, trọng số, d, f, w-đã-gồm-chưa, h, r).
Không dùng giá/dữ liệu sau 27/10. Không neo 11.031/14.301/"12–14k" của skeptic.
