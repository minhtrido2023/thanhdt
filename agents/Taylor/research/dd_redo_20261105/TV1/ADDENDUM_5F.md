> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành, đồng bộ `REPORT_r3.md` (vòng 3, giá 06/11): tâm 16.740; P10 8.823; P90 25.179, nhãn TRONG vùng** (15.379 là số r2 đã thay thế; mọi con số 15.379/4.693 ở dưới là số r2 dùng làm đối chiếu lịch sử); mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.

# TV1 — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07/11/2026 · r3 (sau đính chính GPM/EBITM = TTM) · job `Taylor_20261107_124450` · bản trước: `ADDENDUM_5F_r2.md`, `ADDENDUM_5F_r1.md`

> Bổ sung cho `REPORT_r2.md` (05/11). Không làm lại DD; mọi phần khác của REPORT_r2 giữ nguyên.
> Số: `calc/moat_5f_tv1_r3.py` → `calc/moat_5f_tv1_r3_out.{txt,json}` (chạy 2 lần, md5 trùng); độ nhạy m_T ở `calc/moat_5f_tv1_mT_sens.txt` (độc lập neo peer, không đổi). Bản r1/r2 giữ ở `calc/moat_5f_tv1_r1_*`, `_r2_*`.
> **Đính chính r3 (Mike 07/11 19:50):** GPM_P0/NPM_P0/EBITM_P0/EBITDA_P0 trong BQ là **TTM** (4 quý trượt), không phải quý; dòng Q4 = số cả năm, dùng thẳng. r2 gọi EBITM_P0 là "một quý" và lấy "TB-4-quý" là SAI ⇒ hoàn lại; neo peer tính lại từ **dòng Q4** của từng năm.
> 5F dựa trên kiến thức LLM, non-point-in-time ⇒ chỉ dùng cho DD sống, không đưa vào backtest. Vụ án chỉ để ở WARNING (luật 27/09).

## 1. Vị thế & lợi thế cạnh tranh (5F) — TÁI DÙNG
**Nguồn tái dùng:** `data/moat_tags.csv` dòng TV1 = **NARROW · REGULATORY/AFFILIATION**, asof **2026-06-05**, src `5f_validated_compet`. Tính đến nay mới 5 tháng (<12 tháng) ⇒ theo luật 06/11 KHÔNG dựng lại. Phần dưới chỉ kiểm nhanh bằng dữ liệu đang có trong thư mục này và BQ.

**Loại hình DN:** lai giữa hai mảng.
- (a) Tư vấn thiết kế lưới/nguồn điện: ít tài sản, theo dự án, khách hàng bị khoá trong hệ EVN.
- (b) Tài sản hợp đồng có thời hạn: thuỷ điện Sông Bung 5 (57 MW), thuê đất đến 08/2059, giá PPA do EVN đàm phán.
- Hào chỉ có ý nghĩa ở mảng (a). Mảng (b) không có hào: người mua độc quyền (EVN) và giá sắp hạ bậc từ 2027, đã nằm sẵn trong lưới PPA.

| Lực | Kiểm nhanh (số + nguồn) |
|---|---|
| Cạnh tranh nội ngành | Các PECC khác có biên thấp: EBITM_P0 **TTM** (dòng Q4 = cả năm) của TV2/TV3/TV4, 2016–2025 (30 năm-mã): **trung vị 6,71%, trung bình 7,35%** [BQ `ticker_financial`, `quarter LIKE '%Q4'`]; trung bình nhạy outlier (TV2 2017 = 26,7%), trung vị bền hơn. (r2: 6,0%/6,77% là TB-4-quý chồng lấn, bỏ.) Peer = 3 công ty PECC nội địa (đúng nhóm đối thủ); EBITM peer gồm overhead/EPC (nhất là TV2), còn m của TV1 đã bỏ ~8 tỷ overhead thuỷ điện ⇒ so sánh chỉ gần đúng, chưa đo độ nhạy theo cách chọn peer (chỉ có 3 mã, không loại mã nào). Biên tư vấn tự tách của TV1: **+2…+4% (2022), +4…+7% (2023), +4…+6% (2024), +8…+10% (2025), 11…17% (9T/26)** [đã sửa theo `REPORT_r3.md` §1 đính chính 5b: số cũ −19…−17% (2022) và −2…0% (2023) của `tv1_v2_core_out.txt` §B sai vì nhân DT quý với EBITM_P0 TTM; cách đúng = TTM Q4 × DT năm] ⇒ biên tăng dần 2022→9T/26, ý "âm 2022–23" bị bác; vẫn chưa đủ chu kỳ để kết luận bền. |
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
| (i) Siêu ngạch nhiều chu kỳ | ✗ **không đạt (mảng tư vấn trượt)**, nhưng có chiều ngược cần nêu. Hợp nhất [BQ, dòng Q4 mỗi năm]: ROIC5Y **16,0% (2024Q4) → 20,7% (2025Q4) > Ke 13,5%** (do thuỷ điện 949 đ/kWh sắp hạ giá — tài sản hợp đồng có thời hạn, không phải hào); ROIC_Min5Y = **6,7% (2021Q4–23Q4) → 8,1% (2024Q4) → 11,5% (2025Q4) < Ke**; ROE_Min5Y (ROE riêng, không thay ROIC) = **0,28% (2019Q4–23Q4) → 0,36% (2024Q4) → 10,37% (2025Q4) < Ke**. Phía đối: peer cùng ngành cũng dưới Ke (2025Q4: ROIC5Y TV2 7,8%/TV3 6,8%/TV4 7,4%; ROIC_Min5Y 3,8/2,2/4,1%) ⇒ ROIC5Y 20,7% của TV1 là do thuỷ điện, không phải hào tư vấn. Biên tư vấn tách riêng mới ở mức +2…+7% trong 2022–23 (không âm; đã sửa theo `REPORT_r3.md` §1 đính chính 5b) và chỉ lên 8–17% từ 2025 ⇒ chưa đủ nhiều chu kỳ ⇒ trượt (lý do không còn là "âm").
> *Bất thường chuỗi, cần kiểm chứng:* EBITM_P0 (TTM) của TV1 đi 0,110 (2022Q3) → **0,302 (2022Q4)** → 0,143 (2023Q1); GPM_P0 0,215 → 0,406 → 0,263. TTM không nên nhảy rồi tụt như vậy; chưa giải thích được (không khẳng định là biên quý). Không dùng cho neo peer; kết luận tier không dựa vào điểm này. |
| (ii) Cơ chế gọi tên được | ✓ một phần: incumbency 500 kV + quan hệ EVN. |
| (iii) Không có đồng hồ cắt hào | ✗. Vụ án/cấm thầu nhắm đúng cơ chế ở (ii). |

## 2. Moat trong mô hình — KHÔNG thưởng; mô hình r2 giữ biên kịch bản vĩnh viễn
- Thuỷ điện (PPA có thời hạn), tiền ròng, lưới 5 trục và các xác suất đều **không bị moat chạm tới**.
- **Phát hiện:** terminal DCF tư vấn trong r2 (`tv1_v2_core.consult`) giữ biên kịch bản 5/8/11/14% **mãi mãi** (g 5%, tái đầu tư VLĐ 49%·ΔDT) ⇒ RONIC ngầm = m·0,8·0,8/0,49 = **6,5% / 10,4% / 14,4% / 18,3%**; biên kỳ vọng 9,2% > biên peer 6%, terminal chiếm 56–81% giá trị tư vấn. Trái luật 3c cho NARROW (biên về trung bình chu kỳ NGÀNH + RONIC=Ke).
- **Tách nguồn thay đổi (r3, đo):** (1) chỉ đặt **RONIC=Ke, giữ biên từng kịch bản** (RONIC_ONLY): tâm **15.379 → 15.757 (+2,5%)** — tức bản thân RONIC=Ke không làm giảm tâm; (2) thêm **mỏ neo biên về 6,71% (trung vị TTM peer, fade 2031–32)**: 15.757 → **13.804**. ⇒ **toàn bộ mức giảm đến từ mỏ neo biên**, không từ RONIC. (Mô tả "thưởng WIDE ngầm qua RONIC" ở r1 là sai nguồn.)
- **Tham số NARROW đề xuất** (cơ sở: NARROW REGULATORY/AFFILIATION không qua (i)/(iii); luật 3c ghi "trung bình"):
  - biên kịch bản giữ 2027–30 (đường ống QHĐ8, biên 2025–9T/26 đã đo);
  - fade tuyến tính 2031–32 về biên peer — **trung vị 6,71% hoặc trung bình 7,35%** (TTM dòng Q4) (cả hai báo ở §3; số liệu peer, không phải vụ án);
  - terminal RONIC = Ke (TV = NOPAT_{T+1}/Ke), không bội số premium.

## 3. Độ nhạy — bảng 4 ô NARROW (r 13,5%, giá 19.600; CK = chiết khấu thanh khoản)
Nhãn so giá 19.600 với P10/P90 sau CK.

| Fade về | CK 5 tỷ (4,02%) | CK 1 tỷ (1,98%) | CK sleeve (0,66%) |
|---|---|---|---|
| **Trung vị 6,71%** | tâm 13.804 · P90 **19.599** · **TRÊN (lệch 1 đ so giá — ranh giới)** | tâm 14.097 · P90 20.015 · TRONG | tâm 14.287 · P90 20.284 · TRONG |
| **Trung bình 7,35%** | tâm 14.218 · P90 20.083 · TRONG | tâm 14.520 · P90 20.509 · TRONG | tâm 14.715 · P90 20.785 · TRONG |
| (đối chiếu) r2 hiện hành | tâm 15.379 · P90 24.544 · TRONG | 15.705 · 25.065 · TRONG | 15.916 · 25.402 · TRONG |

- **Nhãn: RANH GIỚI.** Trong 6 ô chỉ 1 ô TRÊN (trung vị × CK 5 tỷ) và nó hụt ngưỡng đúng 1 đ (P90 19.599 vs giá 19.600); 5 ô TRONG; giá–P90 −0,0%…+5,7% (P90 19.599…20.785). Điểm lật m_T ≈ 6,66% (*ước lượng*, nội suy P90 giữa 6% và 8%) — trùng trung vị peer 6,71%. Đổi cỡ CK hay trung vị→trung bình đều lật nhãn. **Không khẳng định "TRONG → TRÊN vùng".**
- **Phát hiện bền (không phụ thuộc nhãn): tâm giảm 7,5–10%** so r2 (CK 5 tỷ: trung vị 15.379 → 13.804 = −10,2%, trung bình → 14.218 = −7,5%; CK sleeve: 15.916 → 14.287 = −10,2% / 14.715 = −7,5%), P10 *tăng* (4.693 → 6.2–6.6 nghìn), P90 giảm (24.544 → 19.6–20.1 nghìn). Giá vẫn cao hơn tâm ở mọi ô (83–90% khối xác suất dưới giá) ⇒ "không có biên an toàn" không đổi.
- P10 NARROW/NONE cao hơn WIDE: khi RONIC = Ke, kịch bản biên 5% không còn bị phạt vì tăng trưởng huỷ giá trị (biên 5% → 6,71%: kịch bản C_bien5 836 → 3.803). Hiệu ứng hai chiều, đối xứng.
- Độ nhạy m_T (NARROW, CK 5 tỷ; `moat_5f_tv1_mT_sens.txt`):

| m_T | 4% | 6% | 8% | 9,2% | 11% |
|---|---|---|---|---|---|
| Tâm | 12.072 | 13.347 | 14.641 | 15.427 | 16.619 |
| P90 | 17.545 | 19.063 | 20.696 | 21.600 | 22.918 |
| Nhãn | TRÊN | TRÊN | TRONG | TRONG | TRONG |

- Chế độ khác (CK 5 tỷ): NONE (fade 2028–29 về 6,71%) tâm 12.921 · P90 18.261 · TRÊN (cả 3 CK đều TRÊN); NONE-riêng TV1 (về biên TB 2022–9T/26 = 1,3%) tâm 7.832 · P90 12.859 · TRÊN.
- Có cấm thầu 3 năm (Δ −8.194 đ/cp cùng như nhau mọi chế độ): tâm WIDE 12.981 · NARROW-trung vị 11.426 · NARROW-trung bình 11.835.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi (tâm), Mike quyết.** Chỉ sửa terminal DCF tư vấn: **tâm 15.379 → 13.804 (trung vị 6,71%) / 14.218 (trung bình 7,35%)**, tức −10,2% / −7,5% (CK 5 tỷ); toàn bộ do mỏ neo biên, RONIC=Ke riêng lẻ +2,5%. (So r2: −13,2%/−10,0% — nhẹ hơn vì neo TTM cao hơn.)
- Nhãn mới: **ranh giới** (xem §3: 1/6 ô TRÊN, hụt 1 đ), KHÔNG ghi "TRÊN vùng". **Moat_tier/durable không đổi** (NARROW, không bền).
- **Hệ quả nếu Mike duyệt NARROW:** ngưỡng "TRÊN vùng" tại `REPORT_r2.md:104` phải đổi sang P90 của NARROW (19.599 trung vị / 20.083 trung bình, CK 5 tỷ) thay vì P90 r2 (24.544) — *đề xuất, chưa sửa REPORT*.
- Mốc kiểm chứng: biên tư vấn FY2026 kiểm toán và FY2027 (nếu ≥ 11% hai năm liền, không có trích lập vụ án ⇒ có cơ sở nâng m_T).
- Không ghi `dd_price_zones`, không sửa REPORT_r2/SUMMARY.json.

## 5. Đề xuất `data/moat_tags.csv`
Không cần dòng mới: tag 05/06 vẫn còn hạn (<12 tháng) và kiểm nhanh không đổi tier. Đến kỳ audit 06/2027, đề nghị bổ sung số đo vào cột risk1: "ROIC_Min5Y/ROE_Min5Y <Ke tới 2025Q3 (ROE_Min5Y 10,4% từ 2025Q4 vẫn <Ke); biên tư vấn +2…+4%→11…17% (2022–9T26; số cũ −19% đã sửa) vs peer 6,7–7,35% (TTM Q4)".

*Nguồn BQ:* `SELECT t.ticker, t.quarter, t.EBITM_P0, t.GPM_P0, t.ROIC_Min5Y, t.ROIC5Y, t.ROE_Min5Y FROM tav2_bq.ticker_financial AS t WHERE t.ticker IN ('TV1','TV2','TV3','TV4') AND t.quarter>='2016' AND t.quarter LIKE '%Q4'` (chạy 07/11/2026). EBITM_P0/GPM_P0 là TTM, dòng Q4 = cả năm, dùng thẳng (không TB4Q); peer 2016–2025 = 30 năm-mã (2026 chưa có Q4); EBITM_P0 hợp nhất của TV1 gồm thuỷ điện nên không dùng để so trực tiếp; biên tư vấn tách riêng lấy từ core §B.
