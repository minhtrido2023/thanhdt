# CYCLE_BLOCK — TV1 (CTCP Tư vấn Xây dựng Điện 1, EVNPECC1) · DD mù bước 1 · job `Taylor_20261026_054005`

> Mẫu: `research/dd_template_v2_20261026/TEMPLATE.md` (v2). READ-ONLY, không phải khuyến nghị.
> Q = **2026Q3** (CHƯA công bố, dự kiến 30/10/2026) · Q−1 = **2026Q2**. Dữ liệu tài chính dùng đến 30/06/2026.
> Giá tham chiếu **18.400 đ** (đóng cửa 23/10/2026, BQ `ticker`, đã qua ngày GDKHQ cổ tức 2025 khoảng 07/10/2026).
> Nhãn: [BQ] · [BCTC] bản gốc trên pecc1.com.vn (PDF lưu ở `src/pdf/`) · [FEED] · [WEB] · [UL] ước lượng của tôi.

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có  (BCTC Q3/2026 chưa tồn tại; trang BCTC của pecc1.com.vn 26/10 12:44 ICT chưa có mục Q3/2026)
  da_doc_DD_cu_cua_ma_nay          : không
  da_biet_verdict_truoc            : không biết verdict. CÓ biết một phần bối cảnh: context tự nạp của phiên (MEMORY.md index,
                                     mô tả agent fundamental-skeptic, coding_guidelines §27) nhắc TV1 là mã "discretionary,
                                     kiểu DGC/TV1" và có ca đối soát fill TV1 ngày 2026-08-11 ⇒ biết user từng giao dịch mã này.
                                     Không chứa số Q3, không chứa verdict/khuyến nghị.
  quy_Q (mới nhất đã công bố)      : 2026Q2 (BCTC HN Q2 + BCTC bán niên soát xét, phê duyệt 28/08/2026)
                                     Q dự báo = 2026Q3, công bố dự kiến 2026-10-30
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  web_search                       : 1 truy vấn, không chứa mã/“quý 3”/“Q3”/“khuyến nghị”/“giá mục tiêu”/“kết quả kinh doanh”
                                     ("EVNPECC1 nhà máy thủy điện thuộc sở hữu ..."): tóm tắt chỉ nêu Sông Bung 5, không lộ số Q3/khuyến nghị.
                                     Fetch trực tiếp: trang chủ + trang BCTC pecc1.com.vn (tiêu đề tin: sáp nhập MTV3, chi trả cổ tức 2025,
                                     chọn kiểm toán 2026, tỷ lệ sở hữu nước ngoài) — không có số Q3.
  cycle_block_md5                  : xem LOCK.txt (không thể tự chứa md5 của chính file)
  cycle_block_commit               : không commit (dispatch chỉ yêu cầu md5 + LOCK.txt; thư mục research/dd_* đang untracked)
  thoi_diem_khoa (ICT)             : xem LOCK.txt
  blind                            : yes (kèm caveat "biết user từng giao dịch TV1" ở trên)
```

**Loại ngành:** HỖN HỢP — (1) **thủy điện** (Sông Bung 5, miền Trung, bán cho Công ty Mua bán điện/EPTC) = chu kỳ **thủy văn**,
không phải chu kỳ giá; (2) **tư vấn/khảo sát/thiết kế điện** = chu kỳ cầu đầu tư (capex nguồn/lưới EVN, QHĐ8), khách hàng phần
lớn là đơn vị EVN. Năm 2025: thủy điện 261,6 tỷ DT / 165,1 tỷ LN gộp (**67% LN gộp**), tư vấn 447,0 / 80,8 tỷ [BCTC FY2025 kiểm toán, TM VII.3a].

## A. Biên hiện tại so với lịch sử chính mã (dữ liệu đến 2026Q2)
- Cửa sổ: TTM 2011Q1–2026Q2, **62 quý**; số chu kỳ thủy văn thấy được ≈ 2–3 (k ≤ 3 ⇒ phân vị chỉ là **mô tả**).
- **Kiểm `GPM_P0`:** `GPM_P0` là biên gộp **TTM**, không phải quý. Đối chiếu: GP TTM đến Q2/26 = GP FY25 (0,3470 × 708,62) − GP H1/25
  (94,78 [BCTC]) + GP H1/26 (97,11 [BCTC]) = 248,2 tỷ / DT TTM 746,1 tỷ = 33,27% = `GPM_P0` 2026Q2 (0,33268) ⇒ **khớp**. `NPM_P0` cũng là TTM.
- **Biên gộp TTM = 33,27%**, phân vị **56,5** (toàn cửa sổ; min 18,0%, trung vị 31,0%, max 47,2%) · **phân vị 9,1** nếu chỉ tính 11 quý
  TTM từ 2023Q4 (min 32,9%, max 39,9%, đỉnh 2025Q1).
- **Biên LNST TTM = 19,88%**, phân vị **95,2** toàn cửa sổ (trung vị 6,5%) · phân vị 72,7 trong cửa sổ từ 2023Q4 (max 21,2% tại 2025Q4).
- **Điểm gãy mô hình (cắt chuỗi ở 2023):** 2017–2022 LNST năm 0,8–11,9 tỷ (chi phí lãi vay dự án thủy điện 19–24 tỷ/năm, tranh chấp
  khoản huy động cá nhân 2013–2017, dự phòng); vay ngân hàng dài hạn giảm từ 667 tỷ (2015Q2) về 0,41 tỷ (30/06/2026) [BQ `LtDebt_P0`, BCTC TM21].
  Từ 2023 biên LNST nhảy lên 14–21% chủ yếu do **hết gánh lãi vay**, không phải do biên gộp cao lên ⇒ phân vị biên LNST toàn cửa sổ
  (95) phóng đại "đỉnh"; phân vị biên gộp mới là thước chu kỳ.
- Phân rã H1/2026 vs H1/2025 [BCTC bán niên soát xét, TM32]: thủy điện DT 81,20 vs 96,72 tỷ (**−16,1%**), biên gộp 52,9% vs 58,5% ·
  tư vấn DT 197,59 vs 144,55 tỷ (**+36,7%**), biên gộp 27,4% vs 26,4%. Biên gộp HN H1/26 34,83% vs 39,28%.
- Q3/2025 (gốc so sánh của F): DT 149,31 tỷ, LN gộp 51,37 tỷ ⇒ **biên gộp 34,40%** (= 9T/25 [390,59 − 244,43] − H1/25 94,78; BCTC Q3/2025
  TM VII.1, VII.3), LNST 26,76 tỷ [BQ = BCTC]. Thủy điện Q3/25 ≈ 41,6 tỷ [UL: DT bán EPTC 9T/25 138,30 − thủy điện H1/25 96,72; giả định
  toàn bộ DT EPTC là thủy điện — đúng cho FY2025: 261,600 = 261,600].

## B. Giá/biến đầu ra–đầu vào chính so với 5–10 năm
| Biến | Vai trò | Giá trị gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| ONI (ENSO) — proxy thủy văn, El Niño ⇒ thiếu mưa miền Trung | đầu vào sản lượng thủy điện (ngược chiều) | **+2,16** (JAS 2026) | −0,28 | **97,7** (128 mùa từ 2016; max +2,50 2015/16) | [FEED] `data/oni_index.csv` |
| DT thủy điện năm (Sông Bung 5) | đầu ra | TTM 246,1 tỷ (H2/25 164,9 + H1/26 81,2) | 2024: 215,9 · 2025: 261,6 | `CHUỖI THIẾU` (segment chỉ đọc được 2024–H1/26) | [BCTC] |
| Giá bán điện cho EPTC / PPA | đầu ra | — | — | `CHUỖI THIẾU` | — |
| Capex nguồn/lưới EVN (cầu tư vấn) | cầu | proxy: người mua trả trước 130,8 tỷ (30/6/26) vs 104,4 (1/1/26); DT tư vấn H1 +36,7% | — | `CHUỖI THIẾU` | [BCTC] |
| Chi phí nhân công (đầu vào chính mảng tư vấn) | đầu vào | H1/26 92,35 tỷ vs 62,42 (+48%) | — | `CHUỖI THIẾU` | [BCTC TM29] |
- Biến đã đối chiếu số kỳ trước: El Niño mạnh tương tự gần nhất là 2015/16 (ONI ≥ 2,0 từ ASO/2015 đến JFM/2016). Không đo sản lượng
  Sông Bung 5 năm 2015–16 ⇒ tác động lên TV1 là **[UL] chưa đo**.
- Hàm chi phí thủy điện [UL, khớp 2 kỳ]: giá vốn ≈ 15,2 tỷ/quý cố định (khấu hao ~19 tỷ/nửa năm) + ~10% DT (thuế tài nguyên, DVMTR):
  H1/26 38,25 = 2×15,1 + 0,1×81,2; H1/25 40,17 = 2×15,25 + 0,1×96,7 ⇒ biên gộp thủy điện **rất nhạy với sản lượng** (đòn bẩy hoạt động).

## C. Pha chu kỳ: **GIỮA-XUỐNG** (cho biên gộp HN; mức tin thấp)
- Mặc định cơ học không kích hoạt: phân vị A (biên gộp) 56,5 toàn cửa sổ / 9,1 từ 2023; B (ONI, chiều ngược) 97,7 ⇒ không cùng ≥80 hay ≤20.
  Biến chi phối thứ hai (giá điện, capex EVN) `CHUỖI THIẾU` ⇒ theo mẫu không được kết luận ĐÁY/ĐỈNH.
- **Ủng hộ (1):** mảng thủy điện (67% LN gộp 2025) vừa qua năm nước rất tốt (2025: DT 261,6 vs 215,9 tỷ 2024; Q4/25 thủy điện ≈ 123,3 tỷ [UL])
  và đã quay đầu: H1/26 −16,1% DT, biên 52,9% vs 58,5%.
- **Ủng hộ (2):** ONI +2,16, phân vị 97,7/10 năm, El Niño mạnh đang phát triển ⇒ mùa mưa miền Trung (T9–T12) 2026 rủi ro thiếu nước;
  tác động chính rơi vào Q4/26–H1/27, Q3 chịu một phần (T9).
- **Ủng hộ (3):** cơ cấu dịch chuyển sang tư vấn (biên gộp 27% H1, 14,1% ở H2/25 [UL: FY25 − H1/25]) ⇒ biên gộp HN bị kéo xuống dù tư vấn tăng.
- **Chống:** cầu tư vấn đang ở pha lên (QHĐ8; DT tư vấn +36,7%, trả trước +25%); biên gộp tư vấn H1/26 cao hơn H1/25; bảng cân đối hết
  vay ngân hàng ⇒ biên LNST có sàn cấu trúc cao hơn mọi kỳ trước 2023, nên "giữa-xuống" của biên gộp không đồng nghĩa với LN về mức 2017–22.
- **Cơ chế cú sốc giá cổ phiếu:** KHÔNG phải cầu hay chi phí. Giá đi từ trung bình 32.938 đ (T3/2026) về 18.888 đ (T10/2026) [BQ, trung bình
  tháng], trùng **khởi tố + tạm giam Chủ tịch HĐQT và phó phòng TCKT ngày 07/05/2026** (vụ đấu thầu EVNNPT/PC1) ⇒ cú sốc **pháp lý/quản trị**.
  So PB với đáy 2019–21 (gánh lãi vay + tranh chấp vốn huy động cá nhân, cũng là loại quản trị/cấu trúc vốn) chỉ so được một phần.
- **Cung:** đối thủ tư vấn là PECC2/3/4 (cùng tập đoàn EVN) — không có số công suất/backlog ngành.

## D. Neo chính sách và rủi ro cấu trúc
| Neo/rủi ro | Loại | Ngày | Chu kỳ hay cấu trúc? | Nguồn |
|---|---|---|---|---|
| Khởi tố, tạm giam Chủ tịch HĐQT + phó phòng TCKT (vụ EVNNPT/PC1: đấu thầu, kế toán, tham ô, hối lộ); BGĐ không trích dự phòng | pháp lý | 07/05/2026 (CBTT 22/05/2026); chưa kết luận | **cấu trúc** — rủi ro mất tư cách dự thầu dự án EVN / truy thu chưa định lượng | [BCTC] TM33 bán niên |
| Bà Nguyễn Thị Ngãi: phúc thẩm 26/08/2026 giữ sơ thẩm, 08 giấy nhận nợ vô hiệu, TV1 phải trả 17,69 tỷ (sổ ghi vay 14,54 tỷ) | pháp lý | 26/08/2026 (hiệu lực) | một lần: chênh ~3,15 tỷ [UL] có thể ghi nhận Q3/26 | [BCTC] TM21 |
| Ông Lê Phi Long: khoản vay 64,4 tỷ đang tranh chấp, hòa giải 20/12/2023, chưa có thông báo của tòa | pháp lý | treo từ 20/12/2023 | một lần, chưa định lượng | [BCTC] TM21 |
| Thuê đất NM thủy điện (xã Bến Hiên, Thạnh Mỹ — Đà Nẵng) | hợp đồng đất | đến **08/2059** | cấu trúc — dòng tiền thủy điện có thời hạn dài (~33 năm) | [BCTC FY25] TM19b |
| PPA với EPTC, giấy phép khai thác nước Sông Bung 5 | hợp đồng/giấy phép | **chưa thấy ngày** trong BCTC đã đọc | cấu trúc | — |
| **Cổ đông chi phối: EVN 54,34%**; Lê Minh Hà 9,84% (giảm từ 10,35% trong H1/26; đồng thời là bên cho vay 12,6 tỷ) | sở hữu | 30/06/2026 | cấu trúc | [BCTC] TM22 |
| Nhu cầu vốn của cổ đông chi phối: EVN cần vốn lớn cho QHĐ8 ⇒ có động cơ nhận **cổ tức tiền** (2025: phải trả cổ tức 43,18 tỷ tại 30/06/26, ≈1.500–1.600 đ/cp [UL]). Xung đột lợi ích: phần lớn DT tư vấn đến từ đơn vị EVN (bên liên quan) ⇒ giá dịch vụ do bên chi phối quyết; khách hàng EVNNPT chính là nơi xảy ra vụ án | sở hữu/bên liên quan | — | cấu trúc | [BCTC] TM31 |
| Sáp nhập công ty con MTV3 vào công ty mẹ (CBTT trên web công ty, chưa đọc ngày) | tái cấu trúc | 2026 | không đổi số hợp nhất | [WEB] pecc1.com.vn |
| Trình bày lại số so sánh 01/01/2026 theo TT 43/2026/TT-BTC (20/04/2026) | kế toán | 2026 | rủi ro so sánh kỳ | [BCTC] TM35 |
- Dòng tiền lõi có thời hạn? Thủy điện: thuê đất đến 2059 (dài) ⇒ PE không vô hạn nhưng gần như vậy với chiết khấu; tư vấn: không thời hạn
  nhưng phụ thuộc tư cách nhà thầu EVN ⇒ rủi ro "mất vị trí" (loại LOẠI §2.5) phụ thuộc kết luận điều tra — **chưa xác định**.

## E. PE/PB trên LN chuẩn hoá (bảng cân đối 30/06/2026, BCTC HN bán niên soát xét)
- Vốn hoá: 26.691.319 cp × 18.400 = **491,1 tỷ**.
- Net cash [BCTC]: tiền 61,78 + đầu tư giữ đến đáo hạn 81,60 − vay 134,00 (trong đó cá nhân 122,22, quỹ lương 7,76, ngân hàng 4,02) = **+9,38 tỷ**;
  trừ cổ tức phải trả 43,18 tỷ (giá đã ex-quyền) ⇒ **−33,79 tỷ**. EV ≈ **524,9 tỷ**.
  ⚠️ BQ `Cash_P0` = 61,78 tỷ **thiếu 81,60 tỷ** tiền gửi giữ đến đáo hạn (lặp lại bẫy README v2 §3).
- LN chuẩn hoá — ghi cả hai cách theo mẫu v2:
  - (a) Trung vị LNST năm **2023–2025** (cửa sổ sau điểm gãy, A): 75,6 / 92,0 / 150,2 ⇒ **92,0 tỷ**. (Trung vị 2010–2025 = 32,8 tỷ, không dùng:
    gồm thời kỳ gánh lãi vay dự án và dự phòng tranh chấp.)
  - (b) LNST lõi TTM: TTM thô 148,4 tỷ [BQ = BCTC]; trừ phần thủy văn vượt trội 2025 [UL: (DT thủy điện TTM 246,1 − 2024 215,9) × 0,9 × 0,8
    ≈ 21,7 tỷ] ⇒ **≈ 126,7 tỷ [UL]**. Khoản một lần đã biết trong TTM: điều chỉnh soát xét −5,80 tỷ LNST H1/26 (tăng chi phí QLDN) — để nguyên.
  - Chênh (b)/(a) = 1,38 lần — do điểm gãy lãi vay + mảng tư vấn tăng trưởng.
- Lãi tiền gửi sau thuế ≈ 3,5 tỷ/năm [UL: ~143 tỷ tiền + tiền gửi × ~3% × 0,8].
- **PE_chuẩn hoá ex-cash:** 524,9 / (92,0 − 3,5) = **5,9x** (a) · 524,9 / (126,7 − 3,5) = **4,3x** (b) · tham chiếu TTM thô 3,6x.
- **PB hữu hình:** VCSH 507,85 − vô hình 1,05 = 506,80 tỷ ⇒ **0,97x**. BQ PB lịch sử (65 quý): min 0,50 (2011Q3), p25 0,90, trung vị 1,09;
  vùng đáy quản trị/lãi vay 2019–21 ~0,69–0,93 [BQ `PB`]. Không có đáy cùng loại "khởi tố lãnh đạo" trong lịch sử mã để so.

## F. DỰ BÁO CÓ THỂ BÁC BỎ
```
FORECAST  (chính — tính vào sổ)
  indicator   : Biên gộp hợp nhất QUÝ 3/2026 của TV1 = LN gộp (mã 20) / DT thuần (mã 10), cột "Quý này" (Q3 riêng, KHÔNG lũy kế)
  source      : BCTC hợp nhất quý 3/2026 gốc trên pecc1.com.vn / CBTT HNX (nếu chỉ có lũy kế 9T: Q3 = 9T/26 − H1/26 bán niên soát xét
                [DT 278,79; LN gộp 97,11 tỷ])
  baseline    : Q3/2025 = 34,40% (cùng kỳ); TTM đến Q2/26 = 33,27%; H1/26 = 34,83%
  call        : NHỎ HƠN 33,0%
  horizon     : 2026Q3
  due_date    : 2026-11-09  (BCTC Q3 dự kiến 30/10/2026 + 10 ngày)
  p           : 0.65
  persistence : giữ cùng kỳ 34,4% (hoặc TTM 33,3%) ⇒ ≥ 33,0% ⇒ persistence nói KHÔNG
  void_if     : BCTC Q3/2026 không công bố trước 2026-11-30; đổi phạm vi hợp nhất/đổi cách phân loại giá vốn khiến mã 20 không so được;
                đình chỉ giao dịch hay kiểm toán từ chối do vụ án
```
- Lập luận [UL]: thủy điện Q3/26 ≈ 35 tỷ (−15% so 41,6 tỷ, theo đà H1 −16% + El Niño) ⇒ LN gộp ≈ 35×0,9 − 15,2 ≈ 16,3 tỷ; tư vấn ≈ 130 tỷ
  (+20%) × 26% ≈ 33,8 tỷ ⇒ biên gộp HN ≈ **30%**. Kể cả thủy điện giữ nguyên 41,6 tỷ, tư vấn +20% ⇒ ≈ 32,6% (vẫn < 33,0%). Kịch bản làm sai:
  thủy điện ≥ 45 tỷ (mưa T9 tốt) **và** tư vấn ít tăng / biên tư vấn > 30%.

Phụ (KHÔNG tính vào cổng, chỉ để đối chiếu ở mục H):
```
FORECAST F2
  indicator   : LNST hợp nhất quý 3/2026 (mã 60, "Quý này")
  source      : BCTC HN Q3/2026 gốc
  baseline    : Q3/2025 = 26,76 tỷ
  call        : NHỎ HƠN 32,1 tỷ (tức không tăng ≥ 20% YoY)
  p           : 0.75
  persistence : 26,76 < 32,1 ⇒ persistence cũng nói CÓ (F2 ít phân biệt, chỉ là kiểm tra mô hình LN ≈ 26–31 tỷ [UL],
                gồm khả năng ghi nhận ~3,15 tỷ chênh lệch vụ bà Ngãi)
FORECAST F3
  indicator   : DT bán cho Công ty Mua bán điện lũy kế 9T/2026 (TM bên liên quan BCTC HN Q3/2026) − 81,20 tỷ (thủy điện H1/26)
  call        : NHỎ HƠN 41,6 tỷ (thủy điện Q3/26 thấp hơn cùng kỳ)
  p           : 0.70
  void_if     : BCTC Q3/2026 không thuyết minh DT theo bên liên quan
```
