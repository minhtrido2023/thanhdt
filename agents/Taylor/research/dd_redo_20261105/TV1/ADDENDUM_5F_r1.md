# TV1 — ADDENDUM bước 3c (5F tầng b + moat trong mô hình) · 07/11/2026 · job `Taylor_20261107_120558`

> Bổ sung cho `REPORT_r2.md` (05/11). Không làm lại DD; mọi phần khác của REPORT_r2 giữ nguyên.
> Số: `calc/moat_5f_tv1.py` → `calc/moat_5f_tv1_out.{txt,json}`, độ nhạy biên terminal ở `calc/moat_5f_tv1_mT_sens.txt` (`$DNA_PYEXE -I`).
> 5F dựa trên kiến thức LLM, non-point-in-time ⇒ chỉ dùng cho DD sống, không đưa vào backtest. Vụ án chỉ để ở WARNING (luật 27/09).

## 1. Vị thế & lợi thế cạnh tranh (5F) — TÁI DÙNG
**Nguồn tái dùng:** `data/moat_tags.csv` dòng TV1 = **NARROW · REGULATORY/AFFILIATION**, asof **2026-06-05**, src `5f_validated_compet`. Tính đến nay mới 5 tháng (<12 tháng) ⇒ theo luật 06/11 KHÔNG dựng lại. Phần dưới chỉ kiểm nhanh bằng dữ liệu đang có trong thư mục này và BQ.

**Loại hình DN:** lai giữa hai mảng.
- (a) Tư vấn thiết kế lưới/nguồn điện: ít tài sản, theo dự án, khách hàng bị khoá trong hệ EVN.
- (b) Tài sản hợp đồng có thời hạn: thuỷ điện Sông Bung 5 (57 MW), thuê đất đến 08/2059, giá PPA do EVN đàm phán.
- Hào chỉ có ý nghĩa ở mảng (a). Mảng (b) không có hào: người mua độc quyền (EVN) và giá sắp hạ bậc từ 2027, đã nằm sẵn trong lưới PPA.

| Lực | Kiểm nhanh (số + nguồn) |
|---|---|
| Cạnh tranh nội ngành | Các PECC khác có biên thấp: trung vị EBITM_P0 của TV2/TV3/TV4 giai đoạn 2016–2026 là **6%** (33 năm-mã; TV2 4–17%, TV3 4–8%, TV4 5–10%) [BQ `ticker_financial`]. Biên tư vấn tự tách của TV1: **−19…−17% (2022), −2…0% (2023), +4…+6% (2024), +8…+10% (2025), 11…17% (9T/26)** [`calc/tv1_v2_core_out.txt` §B] ⇒ biên đi theo chu kỳ, không bền. |
| Quyền lực người mua | EVN vừa là cổ đông mẹ (**54,34%**) vừa là khách chính; theo tag, khoảng **~76% doanh thu** đến từ hệ EVN (*cần kiểm chứng trên BCTC Q3/26*). Đã phải dự phòng phải thu 86–113 tỷ [core §B]. Quyền lực người mua rất cao. |
| Quyền lực nhà cung cấp (nhân lực kỹ sư) | Quỹ KTPL lấy **20%** LNST (30,1/150,2 năm 2025) [H1 tr.30]; vốn lưu động chiếm 45–53% ΔDT [core N2]. Một phần lợi nhuận siêu ngạch chảy sang người lao động và bị giam trong vốn lưu động. |
| Đối thủ mới | Rào cản là hồ sơ năng lực 500 kV và quan hệ với EVN; gọi tên được cơ chế. Thị phần thiết kế 500 kV: *cần kiểm chứng*. |
| Sản phẩm thay thế | Thấp (dự án lưới bắt buộc phải có thiết kế). Tư vấn nước ngoài/EPC trọn gói ở dự án HVDC: *cần kiểm chứng*. |
| **Lực thứ 6 (Nhà nước)** | Chiều thuận: QHĐ8 (KH 830k tỷ) [core C_giua]. Chiều ngược, và đây là **đồng hồ cắt hào**: vụ EVNNPT/PC1 (Chủ tịch bị khởi tố 05/2026, gắn với các hợp đồng EVN tăng vọt) đánh thẳng vào chính cơ chế hào là quan hệ EVN. Kịch bản cấm thầu 3 năm, xác suất 0,35, ≈ −8.194 đ/cp [REPORT_r2 §6]. |

**Kiểm "có gì đổi hào kể từ 05/06":** không có dữ kiện nâng hạng.
- Các dữ kiện mới đều làm điều kiện (iii) nặng thêm, không làm nhẹ đi:
  - Big4 từ chối kiểm toán (07/2026); An Việt ký 18/08;
  - biên 9T/26 cao, nhưng trùng giai đoạn có hợp đồng EVN đang bị điều tra;
  - hạ bậc PPA thuộc mảng (b).
- ⇒ **Giữ NARROW · REGULATORY/AFFILIATION. Rủi ro số 1: quản trị/vụ án làm mất quan hệ EVN (cấm thầu).**

**Ba điều kiện moat BỀN ⇒ KHÔNG BỀN**

| Điều kiện | Kết quả |
|---|---|
| (i) Siêu ngạch nhiều chu kỳ | ✗. ROE_Min5Y TV1 = **0,3% (2021–24), 2,9% (2025), 10,4% (2026)**; ROIC_Min5Y = **6,7–11,5% (2022–26)**. Cả hai đều < Ke 13,5% [BQ]. Biên tư vấn âm trong 2022–23. |
| (ii) Cơ chế gọi tên được | ✓ một phần: incumbency 500 kV + quan hệ EVN. |
| (iii) Không có đồng hồ cắt hào | ✗. Vụ án/cấm thầu nhắm đúng cơ chế ở (ii). |

## 2. Moat trong mô hình — KHÔNG thưởng; mô hình r2 đang NGẦM thưởng
- Thuỷ điện (PPA có thời hạn), tiền ròng, lưới 5 trục và các xác suất đều **không bị moat chạm tới**.
- **Phát hiện:** phần terminal DCF tư vấn trong r2 (`tv1_v2_core.consult`) giữ biên kịch bản 5/8/11/14% **mãi mãi**, với g 5% và tái đầu tư VLĐ 49%·ΔDT.
  - RONIC ngầm = m·0,8·0,8/0,49 = **6,5% / 10,4% / 14,4% / 18,3%**.
  - Biên kỳ vọng 9,2% cao hơn biên ngành 6%, trong khi terminal chiếm 56–81% giá trị tư vấn.
  - Như vậy hai kịch bản trên (xác suất 0,50) đang được thưởng hào WIDE mà không qua (i)/(iii). Đây là **mâu thuẫn với NARROW**; không phải đếm hai lần, vì r2 không cộng bội số premium.
- **Tham số NARROW đề xuất** (cơ sở: moat NARROW REGULATORY/AFFILIATION, không qua (i)/(iii)):
  - biên kịch bản giữ 2027–30 (cơ sở: đường ống QHĐ8, biên 2025–9T/26 đã đo);
  - fade tuyến tính 2031–32 về **6%** (cơ sở: trung vị EBITM ngành TV2–4 2016–26, BQ);
  - terminal **RONIC = Ke** (TV = NOPAT_{T+1}/Ke; tăng trưởng không tạo giá trị);
  - không dùng bội số premium.

## 3. Độ nhạy WIDE/NARROW/NONE (sau CK 4,02% @5 tỷ, r 13,5%, giá 19.600)
| Moat (chế độ terminal tư vấn) | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn | Tư vấn kỳ vọng đ/cp | Có cấm thầu: tâm / P10 |
|---|---|---|---|---|---|---|---|---|
| WIDE-ngầm = **r2 hiện hành** (tái lập khớp) | 15.379 | 4.693 | 15.532 | 24.544 | 71,3% | TRONG | 7.382 | 12.981 / 1.431 |
| **NARROW (đề xuất)** | **13.347** | **5.810** | **14.101** | **19.063** | 92,4% | **TRÊN vùng** | 5.207 | 10.974 / 314 |
| NONE (fade 2028–29 về 6%, RONIC=Ke) | 12.249 | 6.022 | 12.674 | 17.537 | 95,1% | TRÊN | 3.965 | 9.945 / 0 |
| NONE-riêng TV1 (về biên TB 2022–9T/26 = 1,3%) | 7.832 | 0 | 7.969 | 12.859 | 95,6% | TRÊN | −1.116 | 5.919 / 0 |

- P10 của NARROW và NONE **cao hơn** WIDE: khi RONIC = Ke, kịch bản biên 5% không còn bị phạt vì tăng trưởng huỷ giá trị (biên 5% → 6%, giá trị 836 → 3.365). Hiệu ứng hai chiều, đối xứng.
- **Độ nhạy biên terminal ở chế độ NARROW** (`moat_5f_tv1_mT_sens.txt`):

| m_T | 4% | 6% | 8% | 9,2% | 11% |
|---|---|---|---|---|---|
| Tâm | 12.072 | 13.347 | 14.641 | 15.427 | 16.619 |
| P90 | 17.545 | 19.063 | 20.696 | 21.600 | 22.918 |
| Nhãn | TRÊN | TRÊN | TRONG | TRONG | TRONG |

- **Nhãn đổi rất mong manh.** Giá 19.600 chỉ cao hơn P90 của NARROW 2,8%; nhãn lật ở m_T khoảng 6,7% (nội suy, *ước lượng*).
- Ở m_T 9,2% (= biên kỳ vọng của lưới), RONIC = Ke cho tâm 15.427 ≈ r2. ⇒ Toàn bộ chênh lệch r2→NARROW đến từ việc **biên terminal về mức ngành**, gần như không đến từ RONIC.

## 4. Thay đổi so với báo cáo hiện hành
**Có đổi, và Mike quyết.** Áp moat NARROW nhất quán chỉ sửa phần terminal của DCF tư vấn:
- **tâm 15.379 → 13.347 (−13,2%)**, P10 4.693 → 5.810, P50 15.532 → 14.101, **P90 24.544 → 19.063**;
- **nhãn TRONG vùng → TRÊN vùng** (giá 19.600 > P90).
- Nhãn mới phụ thuộc mạnh vào m_T 6%: chỉ cần ≥ 8% là nhãn về lại TRONG.
- Cả hai bản đều có giá cao hơn tâm; kết luận "không có biên an toàn" không đổi.
- Mốc kiểm chứng: biên tư vấn FY2026 kiểm toán và FY2027 (nếu ≥ 11% hai năm liền, không có trích lập vụ án ⇒ có cơ sở nâng m_T).
- Không ghi `dd_price_zones`, không sửa REPORT_r2/SUMMARY.json.

## 5. Đề xuất `data/moat_tags.csv`
Không cần dòng mới: tag 05/06 vẫn còn hạn (<12 tháng) và kiểm nhanh không đổi tier. Đến kỳ audit 06/2027, đề nghị bổ sung số đo vào cột risk1: "ROE_Min5Y <Ke mọi năm 2021–26; biên tư vấn −19%→11% (2022–9T26) vs ngành 6%".

*Nguồn BQ:* `SELECT ticker, SUBSTR(quarter,1,4), AVG(EBITM_P0), AVG(GPM_P0), AVG(ROIC_Min5Y), AVG(ROE_Min5Y) FROM tav2_bq.ticker_financial WHERE ticker IN ('TV1','TV2','TV3','TV4') AND quarter>='2016' GROUP BY 1,2` (chạy 07/11/2026). EBITM_P0 là TTM hợp nhất; với TV1 số này gồm cả thuỷ điện nên không dùng để so trực tiếp; biên tư vấn tách riêng lấy từ core §B.
