# TV1 — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07/11/2026 · r2 (sau skeptic cụm 1) · job `Taylor_20261107_122443` · bản r1: `ADDENDUM_5F_r1.md`

> Bổ sung cho `REPORT_r2.md` (05/11). Không làm lại DD; mọi phần khác của REPORT_r2 giữ nguyên.
> Số: `calc/moat_5f_tv1_r2.py` → `calc/moat_5f_tv1_r2_out.{txt,json}` (chạy 2 lần, md5 trùng); độ nhạy m_T ở `calc/moat_5f_tv1_mT_sens.txt` (từ r1, không đổi; neo trung vị 6%). Bản r1 giữ ở `calc/moat_5f_tv1_r1_*`.
> 5F dựa trên kiến thức LLM, non-point-in-time ⇒ chỉ dùng cho DD sống, không đưa vào backtest. Vụ án chỉ để ở WARNING (luật 27/09).

## 1. Vị thế & lợi thế cạnh tranh (5F) — TÁI DÙNG
**Nguồn tái dùng:** `data/moat_tags.csv` dòng TV1 = **NARROW · REGULATORY/AFFILIATION**, asof **2026-06-05**, src `5f_validated_compet`. Tính đến nay mới 5 tháng (<12 tháng) ⇒ theo luật 06/11 KHÔNG dựng lại. Phần dưới chỉ kiểm nhanh bằng dữ liệu đang có trong thư mục này và BQ.

**Loại hình DN:** lai giữa hai mảng.
- (a) Tư vấn thiết kế lưới/nguồn điện: ít tài sản, theo dự án, khách hàng bị khoá trong hệ EVN.
- (b) Tài sản hợp đồng có thời hạn: thuỷ điện Sông Bung 5 (57 MW), thuê đất đến 08/2059, giá PPA do EVN đàm phán.
- Hào chỉ có ý nghĩa ở mảng (a). Mảng (b) không có hào: người mua độc quyền (EVN) và giá sắp hạ bậc từ 2027, đã nằm sẵn trong lưới PPA.

| Lực | Kiểm nhanh (số + nguồn) |
|---|---|
| Cạnh tranh nội ngành | Các PECC khác có biên thấp: TB-4-quý của EBITM_P0 (giá trị MỘT QUÝ, không phải TTM) theo năm của TV2/TV3/TV4 2016–2026 (33 năm-mã): **trung vị 5,96% (≈6,0%), trung bình 6,77%** [BQ `ticker_financial`]. Peer = 3 công ty PECC nội địa (đúng nhóm đối thủ); EBITM peer gồm overhead/EPC (nhất là TV2), còn m của TV1 đã bỏ ~8 tỷ overhead thuỷ điện ⇒ so sánh chỉ gần đúng, chưa đo độ nhạy theo cách chọn peer (chỉ có 3 mã, không loại mã nào). Biên tư vấn tự tách của TV1: **−19…−17% (2022), −2…0% (2023), +4…+6% (2024), +8…+10% (2025), 11…17% (9T/26)** [`calc/tv1_v2_core_out.txt` §B] ⇒ biên đi theo chu kỳ, không bền. |
| Quyền lực người mua | EVN vừa là cổ đông mẹ (**54,34%**) vừa là khách chính; theo tag, khoảng **~76% doanh thu** đến từ hệ EVN (*cần kiểm chứng trên BCTC Q3/26*). Đã phải dự phòng phải thu 86–113 tỷ [core §B]. Quyền lực người mua rất cao. |
| Quyền lực nhà cung cấp (nhân lực kỹ sư) | Quỹ KTPL lấy **20%** LNST (30,1/150,2 năm 2025) [H1 tr.30]; vốn lưu động chiếm 45–53% ΔDT [core N2]. Một phần lợi nhuận siêu ngạch chảy sang người lao động và bị giam trong vốn lưu động. |
| Đối thủ mới | Rào cản là hồ sơ năng lực 500 kV và quan hệ với EVN; gọi tên được cơ chế. Thị phần thiết kế 500 kV: *cần kiểm chứng*. |
| Sản phẩm thay thế | Thấp (dự án lưới bắt buộc phải có thiết kế). Tư vấn nước ngoài/EPC trọn gói ở dự án HVDC: *cần kiểm chứng*. |
| **Lực thứ 6 (Nhà nước)** | Chiều thuận: QHĐ8 (KH 830k tỷ) [core C_giua]. Chiều ngược, và đây là **đồng hồ cắt hào**: vụ EVNNPT/PC1 (Chủ tịch bị khởi tố 05/2026, gắn với các hợp đồng EVN tăng vọt) đánh thẳng vào chính cơ chế hào là quan hệ EVN. Kịch bản cấm thầu 3 năm, xác suất 0,35, ≈ −8.194 đ/cp [REPORT_r2 §6] — đây là **giảm trừ pháp lý riêng, giữ nguyên như nhau ở mọi chế độ moat** (WIDE/NARROW đều có; không đếm hai lần). Vụ án chỉ ở mức **WARNING**: KHÔNG dùng để ép biên terminal; fade neo vào điều kiện (i) + số liệu peer. |

**Kiểm "có gì đổi hào kể từ 05/06":** không có dữ kiện nâng hạng.
- Các dữ kiện mới đều làm điều kiện (iii) nặng thêm, không làm nhẹ đi:
  - Big4 từ chối kiểm toán (07/2026); An Việt ký 18/08;
  - biên 9T/26 cao, nhưng trùng giai đoạn có hợp đồng EVN đang bị điều tra;
  - hạ bậc PPA thuộc mảng (b).
- ⇒ **Giữ NARROW · REGULATORY/AFFILIATION. Rủi ro số 1: quản trị/vụ án làm mất quan hệ EVN (cấm thầu).**

**Ba điều kiện moat BỀN ⇒ KHÔNG BỀN**

| Điều kiện | Kết quả |
|---|---|
| (i) Siêu ngạch nhiều chu kỳ | ✗ **không đạt (mảng tư vấn trượt)**, nhưng có chiều ngược cần nêu. Hợp nhất [BQ, TB các quý trong năm]: ROIC5Y **16,1% (2024Q4) → 20,7% (2025Q4–26Q3) > Ke 13,5%** (do thuỷ điện 949 đ/kWh sắp hạ giá — tài sản hợp đồng có thời hạn, không phải hào); ROIC_Min5Y = **6,7% (2022–24) → 8,1% (2024Q4) → 11,5% (2025Q4–26) < Ke**; ROE_Min5Y = **0,28% (2022–24Q3) → 0,36% (2024Q4–25Q3) → 10,37% (từ 2025Q4) < Ke**. Biên tư vấn tách riêng âm trong 2022–23 [core §B] ⇒ trượt. |
| (ii) Cơ chế gọi tên được | ✓ một phần: incumbency 500 kV + quan hệ EVN. |
| (iii) Không có đồng hồ cắt hào | ✗. Vụ án/cấm thầu nhắm đúng cơ chế ở (ii). |

## 2. Moat trong mô hình — KHÔNG thưởng; mô hình r2 giữ biên kịch bản vĩnh viễn
- Thuỷ điện (PPA có thời hạn), tiền ròng, lưới 5 trục và các xác suất đều **không bị moat chạm tới**.
- **Phát hiện:** terminal DCF tư vấn trong r2 (`tv1_v2_core.consult`) giữ biên kịch bản 5/8/11/14% **mãi mãi** (g 5%, tái đầu tư VLĐ 49%·ΔDT) ⇒ RONIC ngầm = m·0,8·0,8/0,49 = **6,5% / 10,4% / 14,4% / 18,3%**; biên kỳ vọng 9,2% > biên peer 6%, terminal chiếm 56–81% giá trị tư vấn. Trái luật 3c cho NARROW (biên về trung bình chu kỳ NGÀNH + RONIC=Ke).
- **Tách nguồn thay đổi (r2, đo):** (1) chỉ đặt **RONIC=Ke, giữ biên từng kịch bản** (RONIC_ONLY): tâm **15.379 → 15.757 (+2,5%)** — tức bản thân RONIC=Ke không làm giảm tâm; (2) thêm **mỏ neo biên về 6% (fade 2031–32)**: 15.757 → **13.347**. ⇒ **toàn bộ mức giảm đến từ mỏ neo biên**, không từ RONIC. (Mô tả "thưởng WIDE ngầm qua RONIC" ở r1 là sai nguồn.)
- **Tham số NARROW đề xuất** (cơ sở: NARROW REGULATORY/AFFILIATION không qua (i)/(iii); luật 3c ghi "trung bình"):
  - biên kịch bản giữ 2027–30 (đường ống QHĐ8, biên 2025–9T/26 đã đo);
  - fade tuyến tính 2031–32 về biên peer — **trung vị 6,0% hoặc trung bình 6,77%** (cả hai báo ở §3; số liệu peer, không phải vụ án);
  - terminal RONIC = Ke (TV = NOPAT_{T+1}/Ke), không bội số premium.

## 3. Độ nhạy — bảng 4 ô NARROW (r 13,5%, giá 19.600; CK = chiết khấu thanh khoản)
Nhãn so giá 19.600 với P10/P90 sau CK.

| Fade về | CK 5 tỷ (4,02%) | CK 1 tỷ (1,98%) | CK sleeve (0,66%) |
|---|---|---|---|
| **Trung vị 6,0%** | tâm 13.347 · P90 **19.063** · **TRÊN** | tâm 13.630 · P90 19.468 · **TRÊN** | tâm 13.813 · P90 **19.729** · **TRONG** |
| **Trung bình 6,77%** | tâm 13.843 · P90 **19.644** · **TRONG** | tâm 14.137 · P90 20.061 · TRONG | tâm 14.327 · P90 20.331 · TRONG |
| (đối chiếu) r2 hiện hành | tâm 15.379 · P90 24.544 · TRONG | 15.705 · 25.065 · TRONG | 15.916 · 25.402 · TRONG |

- **Nhãn: RANH GIỚI / KHÔNG XÁC ĐỊNH.** trong 6 ô chỉ 2 ô TRÊN (trung vị × CK 5 tỷ/1 tỷ), 4 ô TRONG; khoảng cách giá–P90 chỉ −2,7%…+3,7% (P90 19.063…20.331); điểm lật nằm ở m_T ≈ 6,7% (*ước lượng*, nội suy bảng dưới) — trùng đúng trung bình peer. Cỡ CK 1 tỷ → 5 tỷ và trung vị → trung bình đều đủ lật nhãn. **Không khẳng định "TRONG → TRÊN vùng".**
- **Phát hiện bền (không phụ thuộc nhãn): tâm giảm 10–13%** so r2 ở mọi CK (trung vị −13,2%, trung bình −10,0% tại CK 5 tỷ; sleeve: −13,2% / −10,0%), P10 *tăng* (4.693 → 5.8–6.3 nghìn), P90 giảm mạnh (24.544 → 19.1–19.7 nghìn). Giá vẫn cao hơn tâm ở mọi ô (89–92% khối xác suất dưới giá) ⇒ "không có biên an toàn" không đổi.
- P10 NARROW/NONE cao hơn WIDE: khi RONIC = Ke, kịch bản biên 5% không còn bị phạt vì tăng trưởng huỷ giá trị (biên 5% → 6%: 836 → 3.365). Hiệu ứng hai chiều, đối xứng.
- Độ nhạy m_T (NARROW, CK 5 tỷ; `moat_5f_tv1_mT_sens.txt`):

| m_T | 4% | 6% | 8% | 9,2% | 11% |
|---|---|---|---|---|---|
| Tâm | 12.072 | 13.347 | 14.641 | 15.427 | 16.619 |
| P90 | 17.545 | 19.063 | 20.696 | 21.600 | 22.918 |
| Nhãn | TRÊN | TRÊN | TRONG | TRONG | TRONG |

- Chế độ khác (CK 5 tỷ): NONE (fade 2028–29 về 6%) tâm 12.249 · P90 17.537 · TRÊN (cả 3 CK đều TRÊN); NONE-riêng TV1 (về biên TB 2022–9T/26 = 1,3%) tâm 7.832 · P90 12.859 · TRÊN.
- Có cấm thầu 3 năm (Δ −8.194 đ/cp cùng như nhau mọi chế độ): tâm WIDE 12.981 · NARROW-trung vị 10.974 · NARROW-trung bình 11.464.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi (tâm), Mike quyết.** Chỉ sửa terminal DCF tư vấn: **tâm 15.379 → 13.347 (trung vị) / 13.843 (trung bình)**, tức −13,2% / −10,0%; toàn bộ do mỏ neo biên 6%, RONIC=Ke riêng lẻ +2,5%.
- Nhãn mới: **ranh giới/không xác định** (xem §3), KHÔNG ghi "TRÊN vùng".
- **Hệ quả nếu Mike duyệt NARROW:** ngưỡng "TRÊN vùng" tại `REPORT_r2.md:104` phải đổi sang P90 của NARROW (19.063 trung vị / 19.644 trung bình, CK 5 tỷ) thay vì P90 r2 (24.544) — *đề xuất, chưa sửa REPORT*.
- Mốc kiểm chứng: biên tư vấn FY2026 kiểm toán và FY2027 (nếu ≥ 11% hai năm liền, không có trích lập vụ án ⇒ có cơ sở nâng m_T).
- Không ghi `dd_price_zones`, không sửa REPORT_r2/SUMMARY.json.

## 5. Đề xuất `data/moat_tags.csv`
Không cần dòng mới: tag 05/06 vẫn còn hạn (<12 tháng) và kiểm nhanh không đổi tier. Đến kỳ audit 06/2027, đề nghị bổ sung số đo vào cột risk1: "ROIC_Min5Y/ROE_Min5Y <Ke tới 2025Q3 (ROE_Min5Y 10,4% từ 2025Q4 vẫn <Ke); biên tư vấn −19%→11% (2022–9T26) vs peer 6,0–6,8%".

*Nguồn BQ:* `SELECT ticker, SUBSTR(quarter,1,4), AVG(EBITM_P0), AVG(GPM_P0), AVG(ROIC_Min5Y), AVG(ROE_Min5Y) FROM tav2_bq.ticker_financial WHERE ticker IN ('TV1','TV2','TV3','TV4') AND quarter>='2016' GROUP BY 1,2` (chạy 07/11/2026). EBITM_P0/ROIC/ROE là GIÁ TRỊ MỘT QUÝ (lấy TB các quý trong năm, không phải TTM); EBITM_P0 hợp nhất của TV1 gồm thuỷ điện nên không dùng để so trực tiếp; biên tư vấn tách riêng lấy từ core §B.
