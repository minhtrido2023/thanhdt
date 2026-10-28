# CYCLE_BLOCK — FPT (CTCP FPT) · bước 1 DD mù v2 · job `Taylor_20261026_054003` · 2026-10-26

> Mẫu: `research/dd_template_v2_20261026/TEMPLATE.md` (v2). READ-ONLY. Không phải khuyến nghị.
> Q = **2026Q3** (BCTC CHƯA công bố, dự kiến 28/10/2026) · Q−1 = **2026Q2**. Mọi số tài chính dừng ở 30/06/2026.
> Nhãn nguồn: **[BCTC]** = BCTC hợp nhất quý II/2026 gốc (bản scan 47 trang, ký 21/07/2026, tải từ
> `static2.vietstock.vn/data/HOSE/2026/BCTC/VN/QUY 2/FPT_Baocaotaichinh_Q2_2026_Hopnhat.pdf`, đọc ảnh trang) ·
> **[BQ]** `tav2_bq.ticker_financial` / `tav2_bq.ticker` · **[UL]** ước lượng của tôi (có công thức) ·
> **[WEB]** tóm tắt tìm kiếm. Đơn vị: tỷ đồng, trừ khi ghi khác.
> Giá tham chiếu **57.000 đ (đóng cửa 23/10/2026, BQ `ticker`, `Price`=`Close`)**.

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có   (BCTC Q3/2026 chưa công bố; không tìm, không đọc)
  da_doc_DD_cu_cua_ma_nay          : không (không mở kb/projects, kb/memory, research/dd_*, sector_frames_*,
                                            events_buffer, discretionary_funnel*, bus finding về FPT)
  da_biet_verdict_truoc            : không (không biết verdict fleet nào về FPT)
  quy_Q (mới nhất đã công bố)      : 2026Q2 đã công bố; Q cần dự báo = 2026Q3   ngày công bố Q2: 2026-07-28 (BQ Release_Date; BCTC ký 2026-07-21)
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2
  cycle_block_md5                  : xem LOCK.txt (md5 không nhúng được vào chính file)
  cycle_block_commit               : chưa commit (dispatch READ-ONLY, chỉ yêu cầu md5 + giờ ICT trong LOCK.txt)
  thoi_diem_khoa (ICT)             : xem LOCK.txt
  BLIND                            : NO — xem "Ghi chú mù" bên dưới
```

**Ghi chú mù — vì sao `blind: no`.** Không có số Q3/2026 nào lọt vào. Nhưng một tóm tắt WebSearch (truy vấn
"FPT 2Q2026 edited VN pdf vietstock edocs", không chứa từ cấm) đã tự chèn khuyến nghị CTCK: "NHSV Research Q2.2026
update with a BUY rating", và tiêu đề BSC "X-Stock FPT 90600 +27% business results in line with expectations".
Cả hai là note về **Q2**, không phải Q3, nhưng luật v2 §2 nói lộ khuyến nghị CTCK ⇒ `blind: no`. Ngoài ra,
khi tìm feed tôi có mở header + 3 dòng cuối của `data/tech_fpt_lens.csv` (một artifact R&D cũ, có cột
`cheap/quality/flagged`). Tôi không đọc các giá trị đó và không dùng chúng. Hai tóm tắt [WEB] khác có số Q2 của các công ty liên
kết (FRT LNST 6T/26 ~825 tỷ, +123%; FOX doanh thu 6T ~10.800 tỷ, +15%). Đó là dữ liệu ≤ Q−1, hợp lệ.

**Loại ngành:** **không chu kỳ hàng hoá — dịch vụ CNTT xuất khẩu tăng trưởng (cầu chi tiêu IT doanh nghiệp toàn
cầu + tỷ giá JPY/USD) + giáo dục + phần vốn viễn thông/bán lẻ qua công ty liên kết.** B và C điền rút gọn.
⚠️ **ĐỔI MÔ HÌNH 01/01/2026:** từ 01/01/2026 FPT không hợp nhất CTCP Viễn thông FPT (FTEL/FOX, sở hữu 45,66%) nữa,
chuyển sang phương pháp vốn chủ sở hữu [BCTC giải trình tr.7, TM 17]. Doanh thu báo cáo giảm (Q2: 13.789 so với
16.625, −17,1%). Biên gộp và biên LNST đổi bậc. **Mọi chuỗi biên bị cắt ở 2025Q4.**

---

**A. Biên hiện tại so với lịch sử chính mã** (dữ liệu đến 2026Q2)
- Cửa sổ chuỗi CŨ (có hợp nhất FTEL, sau lần thoái bán lẻ 2018Q1): **2018Q1–2025Q4, 32 quý**. Số chu kỳ đáy→đỉnh
  thấy được = **0–1**: LN tăng gần như đơn điệu, quý Q3 chỉ âm YoY một lần (2020Q3 −3,3%). Phân vị dưới đây chỉ
  là **mô tả**.
  - Biên LNST cổ đông mẹ TTM (NP_P0/Revenue_P0, [BQ]) cuối chuỗi cũ 2025Q4 = **13,35%**, phân vị **100** (cao
    nhất trong 29 điểm TTM, min 11,24% ở 2018Q4).
  - Biên gộp ([BQ] `GPM_P0`) 2025Q4 = **36,9%**, phân vị **4** (2019Q1–2025Q4, n=28; đỉnh 39,8% ở 2021Q2). Biên gộp
    giảm dần từ 2023, trong khi biên ròng tăng (nhờ chi phí bán hàng/quản lý, thu nhập tài chính, LN liên kết).
- Chuỗi MỚI (không hợp nhất FTEL), chỉ có 2 quý [BCTC]: biên gộp **Q1/26 = 34,0%**, **Q2/26 = 31,0%** (4.278,6/13.788,5).
  Biên LNST cổ đông mẹ Q2/26 = **18,6%** (2.567,7/13.788,5), bị đẩy lên vì LN liên kết 756,6 tỷ không có doanh thu
  đi kèm. **Chưa có TTM theo cơ sở mới**, nên không tính được phân vị.
- ⚠️ Lệch BQ: `GPM_P0` 2026Q2 = 0,3468, nhưng BCTC cho 31,0% (Q2) hoặc 32,4% (6T). Không khớp ⇒ không dùng
  `GPM_P0` cho 2026. Ngược lại, `NP_P0` [BQ] khớp LNST cổ đông mẹ trong BCTC (Q1 2.487,4; Q2 2.567,7).

**B. Giá đầu ra và đầu vào chính so với 5–10 năm**
| Biến | Vai trò | Giá trị gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| JPY/VND | ra (doanh thu JPY 6T/26 = 53,91 tỷ JPY, so với 43,98 tỷ JPY 6T/25) và nợ (vay JPY 36,85 tỷ JPY) | — | — | — | CHUỖI THIẾU (`vcb_fx_rate.csv` chỉ có USD, 84 dòng từ 2026-07-03) |
| USD/VND | ra (doanh thu USD 6T/26 = 208,8 triệu USD, so với 200,1 triệu USD) | 25.650 mua CK (26/10) | — | — | `data/vcb_fx_rate.csv` — CHUỖI THIẾU ≥5 năm |
| Chi phí nhân sự CNTT VN (đầu vào chính) | vào | 44.388 nhân viên 30/06/26 (31/12/25: 54.646, gồm cả FTEL) | — | — | [BCTC] TM 1 — CHUỖI THIẾU |
| Chi tiêu IT doanh nghiệp Nhật/Âu | cầu | doanh thu châu Âu +36%, Nhật +25% Q2/26 YoY | — | — | [BCTC] giải trình tr.8 — CHUỖI THIẾU |
- Biến chi phối không có chuỗi ≥5 năm ⇒ mục C chỉ được kết luận "giữa / không xác định".

**C. Pha chu kỳ: KHÔNG XÁC ĐỊNH** (bắt buộc theo luật B: CHUỖI THIẾU)
- Ủng hộ "giữa-lên" của LN: (1) LN trước thuế cùng cơ sở Q2/26 +20,0% YoY, LNST +14,2% [BCTC tr.7]. (2) Doanh thu
  thị trường châu Âu +36%, Nhật +25% Q2/26 [BCTC tr.8].
- Chống: biên gộp chuỗi cũ ở phân vị 4 và đang giảm từ 2023; Q2/26 biên gộp 31,0% < Q1/26 34,0%. Dòng tiền kinh
  doanh 6T/26 **âm 1.144,6 tỷ** (6T/25 dương 1.683,6), do phải thu tăng 2.007 tỷ và chi phí trả trước tăng 958 tỷ
  [BCTC LCTT]. Giá cổ phiếu 57.000 so với đỉnh năm 2026 là 106.100 (−46%) và đỉnh 2025 là 154.300 (chưa điều chỉnh
  cổ tức cổ phiếu 15% ngày 21/07/2025) [BQ `ticker.Price`]. Thị trường đang định giá lại mạnh; nguyên nhân KHÔNG
  được tra trong khối mù, vì cấm đọc tin sau ngày chốt.
- Cơ chế: nếu có cú sốc thì là **định giá/kỳ vọng cầu** (de-rating). Số đến Q2 chưa cho thấy cú sốc chi phí đầu vào.
  Cung: không có số công suất ngành.

**D. Neo chính sách và rủi ro cấu trúc**
| Neo/rủi ro | Loại | Ngày | Chu kỳ hay cấu trúc? | Nguồn |
|---|---|---|---|---|
| Ngừng hợp nhất FTEL, chuyển sang công ty liên kết 45,66% | kế toán / cấu trúc | 01/01/2026 | cấu trúc (so sánh YoY phải dùng số cùng cơ sở) | [BCTC] tr.7, TM 17 |
| Tăng vốn điều lệ lên 17.143,3 tỷ (phát hành nhỏ, ~10,8 triệu cp) | vốn | 16/07/2026 | — | [BCTC] TM 1 |
| Cổ tức tiền 1.000 đ/cp (1.703,5 tỷ) chi trong 6T/26; 2025 chi tiền 3.184,8 tỷ + cổ phiếu 2.221,8 tỷ mệnh giá | cổ tức | 6T/2026; 21/07/2025 | — | [BCTC] TM 24, TM 29 |
| Không có dòng tiền có thời hạn kiểu giấy phép/PPA; doanh thu dựa hợp đồng dự án/khách hàng ngắn hạn | hợp đồng | — | cấu trúc | [BCTC] TM 1 |
| Rủi ro tỷ giá JPY (doanh thu và nợ vay cùng JPY: phòng ngừa tự nhiên một phần; không có hợp đồng phòng ngừa cho số dư JPY/GBP 30/06/26) | thuế-phí / FX | 30/06/2026 | chu kỳ | [BCTC] TM 23 |
- **Cổ đông chi phối:** không có cổ đông >50%. Tôi KHÔNG xác minh cơ cấu cổ đông trong phiên này. Theo hiểu biết
  chung (chưa xác minh trong phiên), cổ đông lớn gồm nhà sáng lập Trương Gia Bình và SCIC, mỗi bên vài %.
  Công ty mẹ không có dự án ngoài ngành hút vốn cổ tức. Capex 6T/26 = 1.336 tỷ (6T/25: 3.295 tỷ, gồm cả FTEL);
  xây dựng dở dang chủ yếu là campus giáo dục [BCTC TM 13]. Xung đột cổ tức/vốn: **không thấy** trong BCTC.
- Dòng tiền lõi **không có thời hạn** ⇒ E dùng PE, không dùng dòng tiền có thời hạn.

**E. PE/PB trên LN chuẩn hoá** (bảng cân đối 30/06/2026 [BCTC]; số cổ phiếu 1.714,33 triệu theo vốn điều lệ 16/07/26)
- Vốn hoá [UL] = 57.000 × 1.714,33 tr = **97.717 tỷ**.
- Net cash [BCTC] = tiền 9.065,5 + đầu tư nắm giữ đến đáo hạn ngắn hạn (ròng dự phòng) 19.906,1 + dài hạn 2,4 − vay
  (ngắn 16.367,8 + dài 2.080,6) = **10.526 tỷ**. ⚠️ BQ `Cash_P0` = 8.843 tỷ: **THIẾU 19.906 tỷ tiền gửi giữ đến đáo hạn**.
- LN cổ đông mẹ:
  - **(i) Lõi TTM** 2025Q3–2026Q2 = 2.434,8 + 2.509,5 + 2.487,4 + 2.567,7 = **9.999,4 tỷ** [BQ `NP_P0`, khớp BCTC Q1–Q2/26].
    Không thấy khoản một lần lớn: lợi nhuận khác Q2 chỉ 24,7 tỷ. Có trộn cơ sở hợp nhất, nhưng LN cổ đông mẹ gần như
    không đổi theo phương pháp vì phần FTEL vẫn vào qua LN liên kết.
  - **(ii) Trung vị LN năm 2019–2025** = 5.295 tỷ (năm 2022). Các năm 2019–2025: 3.135 / 3.538 / 4.333 / 5.295 / 6.470 /
    7.856 / 9.376, cộng từ [BQ] `NP_P0`; năm 2025 = 9.376 khớp BCTC TM 24. Mã tăng trưởng đơn điệu ⇒ trung vị lệch xuống
    **1,89 lần** so với TTM. Chọn (i) làm chuẩn, ghi (ii) để đối chiếu.
- **PE TTM = 9,77x**. **PE ex-cash = (97.717 − 10.526) / (9.999 − 1.228) = 9,94x**. Lãi tiền gửi sau thuế
  [UL] = thu lãi 6T 767,3 × 2 × 0,8 = 1.228 tỷ/năm. PE trên trung vị 2019–25 = 18,5x. PE [BQ] hôm nay 10,75x
  (EPS khác cơ sở). Trung vị PE năm theo [BQ]: 2016–2020 9–12x; 2021–2025 17–26x; 2026 đến nay 12,9x.
- **PB** = 97.717 / VCSH mẹ 39.851,5 = **2,45x**. **P/TB** (trừ lợi thế thương mại 935,4 và TSCĐ vô hình 1.420,9) =
  **2,61x**. Không so với "PB đáy cùng loại" vì không xác định được pha (C). Khoản đầu tư liên kết ghi sổ 9.994,7 tỷ,
  phần lớn là FTEL; giá trị thị trường của phần vốn này chưa đo.

**F. DỰ BÁO CÓ THỂ BÁC BỎ** (về lợi nhuận/biên cho BCTC Q3/2026 sắp ra. Dispatch yêu cầu chân trời Q3 = 1 quý sau
Q−1, ngắn hơn mặc định 2–3 quý của mẫu; ghi lại như một lệch có chủ đích)
```
FORECAST (chính)
  indicator   : LNST của cổ đông Công ty mẹ, QUÝ III/2026 (mã số 61, cột "Quý III năm 2026")
  source      : BCTC hợp nhất quý III/2026 GỐC của CTCP FPT (CBTT HOSE/fpt.com). KHÔNG dùng BQ NP_P0
  baseline    : Q2/2026 = 2.567,65 tỷ; Q3/2025 = 2.434,84 tỷ (báo cáo); TTM = 9.999,4 tỷ
  call        : LỚN HƠN hoặc BẰNG 2.680 tỷ (tương đương ≥ +10,1% YoY so với 2.434,8 và ≥ 1,044× Q2/26)
  horizon     : quý 2026Q3
  due_date    : 2026-11-07 (công bố dự kiến 28/10/2026 + 10 ngày)
  p           : 0,75
  persistence : giữ tăng trưởng 6T/26 (+14,1% YoY cổ đông mẹ: 5.055,0 so với 4.431,8) ⇒ 2.778 tỷ ⇒ HIT.
                Giữ mức Q2 (×1,00) ⇒ 2.568 ⇒ MISS. Lịch sử Q3/Q2 2019–2025: 1,21/1,06/1,13/1,16/1,15/1,11/1,08 (7/7 ≥ 1,057;
                trung vị 1,125 ⇒ 2.889)
  void_if     : FPT đổi tiếp phạm vi hợp nhất (mua/bán công ty con lớn, đổi phương pháp với FTEL/FRT/Synnex) trong Q3;
                ghi nhận khoản bất thường > 300 tỷ được BCTC thuyết minh rõ là một lần; đổi chuẩn mực (VAS→IFRS) cho kỳ này
  rationale   : seasonality Q3 ≥ Q2 (7/7 năm) + tăng trưởng thị trường nước ngoài 6T + LN liên kết tăng 41% 6T.
                Rủi ro MISS: giá cổ phiếu −46% từ đỉnh 2026 có thể phản ánh thông tin cầu/hợp đồng mà khối mù không thấy;
                dòng tiền kinh doanh 6T âm; biên gộp Q2 giảm 3pp so với Q1.

FORECAST (phụ — biên)
  indicator   : biên gộp QUÝ III/2026 = mã 20 / mã 10 (quý III), BCTC hợp nhất gốc
  baseline    : Q2/26 = 31,03%; Q1/26 = 34,01%; 6T/26 = 32,45%
  call        : NHỎ HƠN 33,0%
  horizon     : 2026Q3 · due_date 2026-11-07 · p = 0,60
  persistence : giữ Q2 (31,0%) ⇒ HIT; quay về Q1 (34,0%) ⇒ MISS
  void_if     : như dự báo chính
```
