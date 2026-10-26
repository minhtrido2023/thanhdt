# CYCLE_BLOCK — SAS (CTCP Dịch vụ Hàng không Sân bay Tân Sơn Nhất, SASCO) · job `Taylor_20261026_045658` · 2026-10-26

> Bước 1 của mẫu `dd_template_20261026/TEMPLATE.md`. Dữ liệu tài chính đến **2026Q2** (Q−1); Q = 2026Q3 (công bố 20–22/10/2026),
> KHÔNG đọc. Giá cổ phiếu là đầu vào hợp lệ của E (README §2.2): **37.000 đ, đóng cửa 2026-10-23 [BQ `ticker`]** — lưu ý giá này
> nằm SAU ngày công bố Q3, nên đã hấp thụ phản ứng thị trường với Q3 (đóng cửa 2026-10-19, trước công bố: 38.600 đ).
> Nhãn: [BQ] `tav2_bq.ticker_financial` (file `step1/bq_sas_fin_le2026Q2.csv`) · [BC] báo chí trích BCTC/ĐHĐCĐ · [FEED] `data/` · [UL] ước lượng của tôi.

## BLIND_ATTESTATION
```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có
  da_doc_DD_cu_cua_ma_nay          : không (không mở dd_SAS_20261026/)
  da_biet_verdict_truoc            : CÓ — README.md của thư mục template (file được phép mở) §4 ghi verdict cũ SAS = NON
                                     và gợi ý "D chi phối: Long Thành 2027–28; PE 5,4x". Đọc trước khi viết khối này.
  quy_Q (mới nhất đã công bố)      : 2026Q3       ngày công bố: 2026-10-20..22 (theo dispatch)
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  cycle_block_md5                  : xem LOCK.txt
  cycle_block_commit               : KHÔNG commit (dispatch: READ-ONLY) — thay bằng md5 + mtime trong LOCK.txt
  thoi_diem_khoa (ICT)             : xem LOCK.txt
  ⇒ blind: NO (lộ verdict cũ qua README §4). Tin web đã đọc đều đề ngày ≤ 2026-07-24; không thấy tin KQKD Q3/2026.
```

**Loại ngành:** chu kỳ CẦU (lượng khách quốc tế qua TSN, chi tiêu/khách) + **nhượng quyền vị trí có thời hạn** (bán lẻ miễn
thuế, F&B, phòng chờ trong nhà ga do ACV quản lý). Không phải hàng hoá; giá đầu vào hàng hoá chỉ tác động gián tiếp (nhiên liệu
bay → giá vé → lượng khách).

**A. Biên so với lịch sử chính mã** — cửa sổ 2015Q2–2026Q2, 45 quý, TTM từ 2016Q1 (42 điểm); thấy 1 chu kỳ cầu trọn vẹn (đỉnh
2019 → đáy COVID 2021 → hồi 2023–26), k = 1 ⇒ phân vị là **mô tả**.
- Biên LNST TTM = **25,3%** (NP TTM 845,1 tỷ / DT TTM 3.334,6 tỷ) [BQ] — phân vị **95** (42 điểm). Trung vị năm 2016–2025 = 12,9%;
  trước COVID 2017–19 = 12,7% [BQ].
- Biên gộp TTM theo `GPM_P0` = 63,6%, phân vị 98 — **KHÔNG dùng**: `GPM_P0` lệch BCTC. Q4/25: BC 700/976 = 71,7% vs BQ 63,0%;
  Q2/26: BC 505/775 = 65,2% vs BQ 66,5% [BC baophapluat 23/01/2026, 24/07/2026]. Dùng biên LNST.
- ⚠️ **Có dấu hiệu đổi mô hình** (cắt chuỗi chưa làm được vì không có BCTC phân đoạn): mảng miễn thuế chuyển sang **tự doanh** trong
  giai đoạn tìm đối tác mới [BC daibieunhandan 11/06/2026]; tồn kho 31/12/25 còn 69 tỷ (−68,6%) [BC], dựng lại 194 tỷ ở 2026Q2 [BQ];
  Q4/25 doanh thu +23,7% trong khi giá vốn −8,3% [BC]. Biên cao một phần là đổi cấu trúc doanh thu/giá vốn, không chỉ chu kỳ.
- ⚠️ **LN có phần tài chính không lõi**: doanh thu tài chính Q4/25 ~140 tỷ "chủ yếu cổ tức" [BC]; Q2/26 cổ tức được chia 88 tỷ,
  cùng kỳ 2025 không có [BC]. Tổng ~228 tỷ trong TTM là cổ tức/thu tài chính trên khoản đầu tư dài hạn sổ sách ~254 tỷ [BQ
  `LtInvest_P0`] — tính lặp lại chưa rõ. Q4/25 còn lỗ khác ~45 tỷ truy thu tiền thuê đất 2015–2024 [BC] (một lần, ngược chiều).

**B. Biến chi phối so 5–10 năm**
| Biến | Vai trò | Gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| Lượt khách quốc tế qua TSN | đầu ra chính (cầu) | — | — | — | **CHUỖI THIẾU** (không có feed) |
| Chi tiêu/khách, cơ cấu khách | đầu ra | — | — | — | **CHUỖI THIẾU** |
| Brent (proxy nhiên liệu bay → giá vé) | gián tiếp, đầu vào cầu | 85,4 USD (2026-06); 116,8 (2026-09) | 82,65 | 83 (06/26); 97,5 (09/26) | [FEED] `data/brent_monthly.csv` |
| USD/VND (hàng miễn thuế định giá USD) | giá bán / giá vốn | 26.030 (2026-10-26) | — | — | **CHUỖI THIẾU** (`vcb_fx_rate.csv` chỉ từ 2026-07-03, 83 dòng) |

**C. Pha chu kỳ: KHÔNG XÁC ĐỊNH (nghiêng ĐỈNH biên)** — biến chi phối B (khách quốc tế) là CHUỖI THIẾU ⇒ theo luật mẫu không
được kết luận ĐỈNH/ĐÁY dù A ở phân vị 95.
- Ủng hộ "gần đỉnh": (1) biên LNST TTM phân vị 95, gần gấp đôi trung vị 12,9%; (2) ban lãnh đạo tự đặt KH 2026 LNTT 802 tỷ, **−5%**
  so 2025 (844 tỷ), nêu nhiên liệu bay, tỷ giá, khách thắt chi tiêu, chuyển tiếp miễn thuế [BC daibieunhandan 11/06/2026]; Brent
  09/2026 phân vị 97,5 [FEED].
- Chống: H1/2026 LNTT 438 tỷ **+58%** YoY, DT kỷ lục 1.553 tỷ [BC baophapluat 24/07/2026] — động lượng chưa gãy; T3 TSN mở rộng
  diện tích phi hàng không [BC].
- Cơ chế cú sốc sắp tới (nếu có) là **CẤU TRÚC/vị trí** (mục D), không phải cầu sập hay chi phí đầu vào. Không có đáy cùng loại
  trong lịch sử để so PB. Cung: đối thủ cạnh tranh trực tiếp là nhà ga Long Thành mới (mục D).

**D. Neo chính sách / rủi ro cấu trúc**
| Neo/rủi ro | Loại | Ngày | Chu kỳ hay cấu trúc? | Nguồn |
|---|---|---|---|---|
| Long Thành GĐ1 khai thác thương mại | hạ tầng | 2026-12-01 (đã lùi 1 lần) | cấu trúc | [BC baomoi; vietnamtourism.com] |
| Bước 1: khuyến khích hãng chuyển bay QT sang LTH, TSN không cấp đường bay QT mới | phân bổ | 2026-12-01 → 2027-03-27 | cấu trúc | [BC vov.vn post1319489; vneconomy] |
| Bước 2: chuyển toàn bộ bay QT đường dài (>1.000 km) sang LTH; TSN giữ QT <1.000 km code C | phân bổ | lịch hè 2027 (từ 2027-03-28); nguồn khác chia thêm bước đông 2027 | cấu trúc | [BC vneconomy, vov — đề xuất ACV/Cục HK, CHƯA thấy quyết định chính thức] |
| Suất kinh doanh (miễn thuế, F&B, phòng chờ) ở LTH: SASCO "chuẩn bị tham gia đấu thầu", chưa thấy hồ sơ mời thầu/kết quả | hợp đồng/nhượng quyền | chưa có ngày | cấu trúc | [BC daibieunhandan 11/06/2026; dnse senses] |
| Miễn thuế TSN: tự doanh, đang tìm đối tác mới | hợp đồng | từ ~cuối 2025, chưa có ngày kết thúc | cấu trúc | [BC] |
| Truy thu tiền thuê đất 2015–2024 | thuế-phí | ghi nhận Q4/2025 | một lần | [BC] |
- Dòng tiền lõi có thời hạn: **CÓ, trên phần quốc tế đường dài** — lợi thế vị trí độc quyền ở nhà ga quốc tế TSN mất dần từ
  2026-12 → 2027. Tỷ trọng DT/LN của khách QT đường dài: **chưa đo** (không có phân đoạn). ⇒ E không được dùng PE vĩnh viễn trên LN
  hiện tại. Thuộc rủi ro "mất vị trí" trong danh sách LOẠI của §2.5 trừ khi SASCO trúng suất ở LTH.

**E. PE/PB trên LN chuẩn hoá** (vốn hoá = 133,45 tr cp × 37.000 = **4.937,7 tỷ** [BQ OShares, giá 2026-10-23])
- Net cash 30/6/2026 = tiền + tiền gửi **1.241 tỷ**, không vay [BC baophapluat 24/07/2026]. BQ `Cash_P0` = 343,6 tỷ ⇒ **BQ thiếu
  ~897 tỷ tiền gửi có kỳ hạn** (lặp lại bẫy NT2/DDV). Lãi tiền gửi sau thuế ≈ 1.241 × 5% × 0,8 = 50 tỷ [UL, lãi suất 5% ước lượng].
- LN chuẩn hoá — chọn **biên giữa chu kỳ × DT hiện tại**: 12,9% (trung vị năm 2016–25) × 3.334,6 = **430 tỷ** [UL]. Lý do: DT đã
  vượt đỉnh 2019 15%, trung vị LN tuyệt đối (292 tỷ) đánh thấp quy mô hiện tại. Biên trung vị đã chứa phần cổ tức thời trước.
- PE_chuẩn hoá ex-cash = (4.937,7 − 1.241) / (430 − 50) = **9,7x** [UL]. Độ nhạy: trung vị LN tuyệt đối 292 ⇒ 15,3x; TTM thô 845
  ⇒ PE 5,8x (con số gây hiểu lầm — chứa biên phân vị 95 và ~228 tỷ cổ tức/thu tài chính).
- Chưa trừ tác động Long Thành: nếu mất X% LN vĩnh viễn từ 2027, PE chuẩn hoá ×1/(1−X) — X **chưa đo**.
- PB = 4.937,7 / VCSH 1.713 [BC 30/6/2026] = **2,88x** (tài sản vô hình không đáng kể — chưa kiểm). Không có đáy cùng loại
  (cú sốc cấu trúc) để so; đáy COVID 2021 là sốc cầu, PB BQ khi đó ~2,4–2,8 [BQ `PB` cột theo quý] — không so được.

**F. DỰ BÁO CÓ THỂ BÁC BỎ**
```
FORECAST
  indicator   : Biên LNST TTM của SAS = sum(NP_P0, 4 quý) / sum(Revenue_P0, 4 quý)
  source      : tav2_bq.ticker_financial, ticker="SAS", quarter 2026Q2..2027Q1 (đối chiếu BCTC hợp nhất quý 1/2027 nếu BQ lệch)
  baseline    : 25,3% (TTM đến 2026Q2)
  call        : NHỎ HƠN 22,0% tại TTM kết thúc 2027Q1
  horizon     : quý 2027Q1 (2 quý sau Q=2026Q3)
  due_date    : 2027-05-05 (BCTC Q1/2027 dự kiến ~2027-04-22..25 + 10 ngày)
  p           : 0,60
  persistence : biên giữ ≥ 22% (≈ giữ 25,3%)
  void_if     : SASCO M&A/hợp nhất công ty con mới; đổi ghi nhận doanh thu miễn thuế (gross↔net) công bố chính thức; đình chỉ giao dịch
```
Lập luận [UL]: TTM 2027Q1 loại ra Q4/25 (367 tỷ, có ~140 tỷ thu tài chính) và Q1/26 (155 tỷ); để giữ ≥22% thì Q3/26+Q4/26+Q1/27
cần ≥ ~518 tỷ (~173 tỷ/quý, giả định DT TTM không đổi) trong khi bước 1 Long Thành từ 2026-12-01 và KH ban lãnh đạo đi lùi.
Dự báo phụ (không chấm): đến 2027-03-31 chưa có công bố SASCO trúng suất miễn thuế tại Long Thành (p 0,6).
