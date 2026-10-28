# PREREG — Định giá lại DRI lần 3, sửa lỗi skeptic r2 (job `Taylor_20261027_100801`, 27/10/2026)

> Khai TRƯỚC khi chạy FV của bất kỳ ô nào dưới đây; commit file này trước `model.py`. Chỉ nghiên cứu: không lệnh, không
> pin, không sửa file cũ (đọc `../dri_val_supply_adj_r2_20261027/`, `../dd_DRI_20261027/`, không ghi vào đó).
> **Đã xem trước khi khai:** toàn bộ `out.txt`/`REPORT.md` r2; phản biện skeptic r2 (qua dispatch: FV skeptic trên đường
> đáy 9.334/10.424/11.514/12.604, "khoảng tin hơn" 13,0/14,3/15,5k). Hai khoảng đó KHÔNG phải đích; chỉ đối chiếu SAU.
> Nhãn: [BCTC3] BCTC HN Q3/26 (trích `../dd_DRI_20261027/extract_q3_bctc.md`) · [SX] soát xét H1/26 · [BCTN24/25] ·
> [BQ] · [FEED] `data/*.csv` · [WENDY] · [UL] giả định chưa có nguồn · [NỀN] hiểu biết nền chưa kiểm.

## 0. Selfcheck (dừng nếu lệch > 1 đ), TRƯỚC khi đổi tham số
Trong `model.py` mới (chép logic, không import): (a) model_q3 ⇒ **10.878 / 11.031**; (b) r1 ⇒ **14.301**; (c) r2 tâm mid
1,97 60/40 ⇒ **12.481** (và in đủ hàng 60/40 r2: 11.061 / 12.481 / 13.901 / 15.321). Chạy dưới `env -u TZ` và
`TZ=America/New_York`, output giống từng byte. Sau đó cầu nối cộng dồn r2 → r3 từng sửa một.

## 1. Kiểm lại từng lỗi skeptic (kết quả kiểm ghi ở đây trước khi chạy FV)
| # | Lỗi | Kiểm (nguồn) | Sửa |
|---|---|---|---|
| 1 | C_ref 32 cao hơn số đo | C_cal 2025 = 30,45 [r2 out mục 2]; 9T/26 quy về P 47,24 theo k 0,3 = 30,09 [r2 out mục 8]; FY26E (377,4+145,9)/16.157 = 32,39 @53,71 ⇒ 32,39−0,3×(53,71−47,24) = 30,45 [tính]. **Đúng.** | C_ref tâm = **C_cal tính lại với thuế 9T** (§2) |
| 2 | Bỏ sót KTPL + quỹ dự phòng Lào | 9T/26 trích KTPL **16,68 tỷ** từ LNCPP = 10,6% LNST 2025 157,4; 9T/25 trích **11,55** = 10,6% LNST 2024 108,8 [BCTC3 hn_29; BQ]. Quỹ KTPL 9T **chi thật 10,94 tỷ** (bảng 5.17) ⇒ tiền thật rời công ty cho người lao động/BQL, KHÔNG qua P&L (trích từ LNST, không phải chi phí lương — lương đã nằm trong GVHB/QLDN). Quỹ dự phòng tài chính ở Lào 12,30 tỷ (quỹ khác 419) = 7,8% LNST 2025: không rời tập đoàn nhưng bị giữ trong VCSH con Lào. **Đúng.** Lưu ý mâu thuẫn chưa giải: hn_32 nói "số trích quỹ cả năm 2025 là 3,90 tỷ" (dùng tính lại EPS) ≠ 16,68 — có thể 3,90 là phần mẹ; dùng 16,68 vì là dòng VCSH hợp nhất có dòng chi tiền khớp. | KTPL κ = **10,6%** LNST, trừ khỏi dòng tiền cổ đông (Q4, ops, tồn kho). Quỹ Lào: trục τ riêng (§3) |
| 3 | w Lào | Khấu trừ tại nguồn **11,07 tỷ** ghi thẳng giảm LNCPP (bảng biến động VCSH), không nằm trong chi phí thuế TNDN [BCTC3 hn_29]; 9T/25: 9,03. **Đúng** ⇒ không có trường hợp "đã nằm trong thuế". Ghi chú: 11,07/157,4 = 7,0%, 9,03/108,8 = 8,3% LNST năm trước (vì không phải toàn bộ LN đến từ Lào/được chuyển). | **w = 10% cố định** trên FCF (như r2, thận trọng hơn tỷ lệ đo ~7–8%); bỏ w = 0 |
| 8 | Thuế Q3 18,3% thấp | 9T/26: (39,496+1,277)/208,213 = **19,58%** [BCTC3 KQKD 9T]. **Đúng.** | thuế = **19,58%** cho mọi năm (kể cả C_cal, backcast; Q4 giữ thuế Q3 như r2 vì là ước quý) |
| 6 | Quỹ TDND | Tiền gửi có kỳ hạn **70 tỷ** (01/01: 50) nằm trong "ĐT nắm giữ đến đáo hạn NH" 271,8 ⇒ đang tính 100% trong NETC; góp vốn 3 tỷ là ĐT dài hạn, KHÔNG nằm trong NETC (không ảnh hưởng FV) [BCTC3 hn_18/19; SX sx_26]. **Đúng phần 70 tỷ** (= 956 đ/cp). | trục riêng haircut {0; 50; 100%} × 70 tỷ |
| 4,5,7 | chọn tâm hậu nghiệm; PB≤1 trên đường đáy; sản lượng 2035 | thừa nhận | §4, §5, §3 |

## 2. Khung thực/danh nghĩa — xử lý MỘT lần
- **Tâm: khung THỰC.** Giá (RSS3 mid), C, SGA, FX giữ ở "tiền 2025" (như model vốn đã làm) ⇒ chiết khấu bằng **r thực =
  (1+r_dn)/(1+π) − 1**, π = **3%/năm [NỀN]** (CPI VN gần đây ~3–4%; giả định PPP: VND mất giá bù chênh lạm phát VN–Mỹ,
  LAK cũng vậy [UL]). r_dn {10; 12; 13%} ⇒ r thực {6,80; 8,74; 9,71%}. Tâm r_dn 12%.
- **"Chi phí trôi theo lạm phát" chỉ được dùng ĐÚNG MỘT chỗ:** trục **g = trôi chi phí THỰC** (C tăng nhanh hơn giá đầu ra)
  **{0; 1%/năm}** từ 2027, tâm **0** (không có số đo tách được trôi thực khỏi truyền giá k). KHÔNG dùng để chọn C_ref, mid hay r.
- Đối chứng (không phải tâm): khung r2 "trộn" (dòng tiền tiền-2025, r danh nghĩa) — chỉ để cầu nối.
- Hàm ý cho mid: trong khung thực, mid đọc là RSS3 **USD 2025**. Mốc tham chiếu: trung vị 10 năm thực 2,185, 5 năm thực 2,179
  (CPI Mỹ [NỀN/UL], r2 out mục 1); trung vị danh nghĩa 1,865 / 2,075. Báo cả bốn mid ngang hàng (§4).

## 3. Lưới (khai trước) và tâm
| Trục | Lưới | Tâm | Nguồn |
|---|---|---|---|
| C_ref (GVHB/t tại P 47,24, V 14.000) | {30,0; **C_cal**; 31,5; 32,0} | C_cal (≈30,4 sau thuế 19,58%; model in số) | C_cal & 30,0 (≈30,09 đo 9T/26) có nguồn; 31,5/32 = KHÔNG có nguồn (stress) |
| k truyền giá | {k chọn; 0} | k chọn = RMSE backcast 2021–24 nhỏ nhất trong {0; 0,3; 0,6}, chạy lại với thuế 19,58% (luật r2) | backcast [BQ] |
| f tỷ trọng cố định GVHB | {0,3; 0,5; 0,7} | 0,5 | [UL] |
| Sản lượng: năm bắt đầu giảm d0 × tốc độ d | d0 {2028; 2030; 2035} × d {2%; 3%}/năm | **2030, 2%** (BCTN25: vườn "đang dần bước vào chu kỳ thanh lý", thu mua tiểu điền "bù đắp sản lượng thiếu hụt" ⇒ sớm hơn 2035 của r2) | [UL] |
| r danh nghĩa → thực | {10; 12; 13%} | 12% | [UL] |
| g trôi chi phí thực | {0; 1%} | 0 | [UL] |
| τ quỹ dự phòng Lào 7,8% LNST | {tự do (giá trị đủ); giữ tới 2054 (không lãi); mất} | giữ tới 2054 | 7,8% [BCTC3]; xử lý [UL] |
| h haircut tiền ở Lào 196,7 tỷ | {0; 15; 30%} | 15% | [UL] |
| TDND 70 tỷ haircut | {0; 50; 100%} | 0 (BCTC Q3 không ghi tổn thất tiền gửi); báo ĐỦ ba mức ở bảng chính | [BCTC3] |
| Trọng số đường PEAK/MID (2027–28) | {80/20; 60/40; 40/60} | 60/40 | Bobby |
| Cố định | κ KTPL 10,6%; w 10%; thuế 19,58%; X 1.717 t; Q4 Base; L0 (không giá trị cuối sau 2054); SH 73,2 tr; NETC 162,8 tỷ; Dakruco 20 | | như r2 + §1 |
- Lưới đầy đủ mỗi mid = C_ref 4 × k 2 × f 3 × (d0,d) 6 × r 3 × g 2 × τ 3 × h 3 × TDND 3 × trọng số 3 = 69.984 ô. Phân vị lưới
  KHÔNG phải xác suất.
- Thứ tự trừ: FCF cổ đông = 0,9 × LN lõi × (1 − w − κ − τ_trap) (cộng tuyến tính, các tỷ lệ đều so với LNST năm).
  τ: "tự do" ⇒ phần 7,8% không trừ; "2054" ⇒ cộng lại tổng danh nghĩa (tiền 2025) vào 2054, chiết khấu; "mất" ⇒ bỏ.
  Rủi ro chồng: 10% tái đầu tư (FCF 90%) có thể đã gồm một phần quỹ Lào — ghi caveat, không sửa.

## 4. Mid và luật đọc kết quả
- **Mid {1,865; 1,97; 2,075; 2,18} báo NGANG HÀNG; KHÔNG có cột tâm, KHÔNG gán xác suất.** Không có luật chọn mid.
- Trả lời "14.700 / 14.400 cao/thấp hơn FV bao nhiêu" cho từng cột.

## 5. Vùng mua trên ĐƯỜNG GIÁ ĐÁY
- Đường TROUGH: RSS3 2027 = 2028 = T, 2029+ = mid; T ∈ **{1,60; 1,70}** (TB 2023 1,576 [FEED]). Tồn kho X bán ở giá 2027 = T.
  Q4/26 giữ Base (quý đang chạy, giá đã biết một phần).
- Biên an toàn = FV_TROUGH/ngưỡng − 1, ngưỡng **{9.000; 10.000; 11.500; 13.000}**, ở cả bốn mid, tâm các trục khác; kèm cùng
  phép tính ở TDND 100% và ở P10 lưới (lưới §3 trừ trọng số đường, thay bằng TROUGH).
- **Luật khai trước:** một ngưỡng "có biên ≥15% kể cả khi đáy 2 năm" ở một mid ⇔ FV_TROUGH tâm ≥ 1,15 × ngưỡng với **T = 1,60**.
  Báo bảng 4 mid × 4 ngưỡng; KHÔNG gộp mid.
- **§2.5 #3/#4 (calculated_fear_state_backstop.md):** #3 so GPM DRI với DPR/PHR/TRC 2021–25 [BQ snapshot] (chỉ là proxy chi phí;
  peers có thu nhập đất). #4 tính "sổ sách cứng" = tiền + ĐT đáo hạn NH/DH + tồn kho + phải thu − tổng nợ phải trả [BCTC3],
  đ/cp, có và không có TDND 70 tỷ; phần còn lại của VCSH (TSCĐ vườn cây 333,7 + XDCB 72,7 tỷ trên đất tô nhượng Lào) KHÔNG có
  bằng chứng giá trị thanh lý (đất không sở hữu; gỗ thanh lý "chưa hình thành thị trường" [dd_DRI REPORT dòng 46]; LAK làm
  VCSH −38,16 tỷ 9T [BCTC3 hn_29]) ⇒ nếu không chứng minh được thì ghi thẳng "#4 KHÔNG đạt trên PB".

## 6. Báo cáo
1. FV 4 cột mid × hàng: tâm; TDND 50/100%; trọng số 80/20 và 40/60; g 1%; khung trộn r2 (đối chứng).
2. Khoảng lưới mỗi mid: min/P10/trung vị/P90/max, tỷ lệ ô ≥ 14.700 và ≥ 14.400.
3. Độ nhạy một trục quanh tâm, ở **cả bốn** mid; trục nhạy nhất.
4. Cầu nối r2 → r3 cộng dồn (thuế; C_ref; KTPL; quỹ Lào; khung thực; sản lượng; TDND).
5. Vùng mua §5. 6. Gỗ thanh lý, sầu riêng, tái canh, thu mua tiểu điền: **chưa tính** (không có số có nguồn) — liệt kê.
7. Đo vs đoán. 8. Đối chiếu SAU cùng với số skeptic (đường đáy và 13,0/14,3/15,5k) — không chỉnh tham số theo đó.
Không dùng giá/dữ liệu sau 27/10 (giá đóng 27/10 = 14.400, 26/10 = 14.700 [theo dispatch]).
