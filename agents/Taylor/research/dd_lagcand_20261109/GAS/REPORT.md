# DD — GAS (Tổng Công ty Khí Việt Nam – PV GAS) · 09/11/2026 · job `Taylor_20261109_073604` (r1) / `Taylor_20261109_083126` (r2) · **vòng r2 (CUỐI, đã áp errata skeptic — xem Phụ lục E)** · bản r1 giữ ở `REPORT_r1.md`

Ứng viên LAG (LAG_LO, ADV3T 87 tỷ) cho plan 09/11. Chỉ nghiên cứu, không lệnh/wire. Định giá mù giá thị trường; giá 74.100đ (BQ 06/11) chỉ dùng để dán nhãn.
Nguồn chính: BCTC HN Q3/2026 (CBTT 30/10/2026) + BCTC HN soát xét 6T/2026 (Deloitte), tải từ pvgas.com.vn vào `src/` (scan, đọc ảnh) → số liệu chép tại `calc/notes_bctc.md`. Chuỗi lợi nhuận lịch sử: BQ `ticker_financial` (Q3/26 4.576,5 tỷ khớp BCTC).

## 1. Kết luận
- **Giá trị nội tại SAU chiết khấu thanh khoản (cỡ 5 tỷ): tâm 50.146đ · P10 43.327 · P50 49.817 · P90 57.840** (r1: 46.488 / 39.010 / 55.150). Trước CK: tâm 50.476 (P10 43.613 / P90 58.221). Cỡ sleeve 40tr: tâm 50.447 (P10 43.587 / P90 58.187).
- **Nhãn: TRÊN vùng (đắt) — nhãn TƯƠNG ĐỐI THEO KHUNG, không phải bằng chứng thị trường đang hưng phấn** (xem Phụ lục E4). Giá 74.100 cao hơn tâm 47,8% và cao hơn P90 28,1%; 100% trọng số lưới nằm dưới giá. Ngay cả khi r = 8% (ngoài luật), tâm chỉ đạt 68.405 (vẫn dưới giá). Ở r = 13,5%, giá ngụ ý tăng trưởng danh nghĩa vĩnh viễn của LN ≈ **+5,3%/năm** (thay vì suy giảm; đã gồm XDCB); hoặc r ngụ ý = 7,05% (xem E3).
- **LAG chọn vì:** LN quý III tăng mạnh (+79,5% YoY). Phần tăng này **là thật, không đến từ khoản một lần, nhưng không bền**: nó chạy theo giá dầu Brent (Q3 bình quân 90,7 so với 68,0 USD, +33%). Sector read đọc mù (Bobby) dự báo giá dầu đã qua đỉnh cấp tính (F3: trung vị 88 vào 03/2027) và nhãn tầm 2027-30 là STRUCTURAL/ADMIN.
- **Rủi ro lớn nhất (WARNING, không đưa vào tâm):** GAS **không còn đủ điều kiện công ty đại chúng**. PVN nắm 95,76%, cổ đông nhỏ chỉ 4,24% (ngưỡng 10%); CBTT 31/12/2025, thời hạn khắc phục 1 năm. Thêm: thay cả Chủ tịch và TGĐ hồi 07/2026.
- **Khuyến nghị cho plan:** theo DD, giá nằm ngoài vùng giá trị. Nếu LAG vẫn mua theo cơ học thì chỉ nên ở khẩu phần tối thiểu, và xem đây là vị thế ăn theo đà lợi nhuận (momentum của LN), không phải vị thế giá trị.

## 2. Vì sao LAG chọn — surprise bao nhiêu, bền hay một lần (câu hỏi 1)
| LNST CĐ mẹ (tỷ) | Q3/26 | Q3/25 | Δ | 9T/26 | 9T/25 | Δ |
|---|---|---|---|---|---|---|
| | 4.576,5 | 2.549,1 | **+79,5%** | 13.381,2 | 10.053,3 | +33,1% |
Q2/26 đạt 5.860,1 ⇒ Q3 giảm 21,9% QoQ. LN TTM 14.742 tỷ (EPS 6.110đ ⇒ P/E 12,1, khớp cờ hệ).

**Tách nguồn tăng (TM25/27, 9T/26 so với 9T/25):**
- Khí khô + LNG: LN gộp 12.473 so với 8.052 (+4.421 tỷ, **+55% tuyệt đối**). Doanh thu +87% (một phần là LNG cho NT3&4 từ 01/2026 theo cơ chế chuyển ngang) nên biên gộp % giảm từ 21,9% xuống 18,1% — **đó là pha loãng cơ học của doanh thu chuyển ngang, KHÔNG phải bằng chứng suy giảm lợi nhuận** (đính chính r2, E2). Bobby vẫn đọc "pool lợi nhuận dịch sang LNG biên mỏng" như một rủi ro cấu trúc, nhưng số liệu 9T này không chứng minh nó.
- LPG: 3.585 so với 2.816 (+769 tỷ; biên 7,8% so với 5,6%). Một phần có thể là lãi tồn kho khi giá CP tăng (+60% YoY), chưa tách được.
- Vận chuyển khí: 1.450 so với 1.409, ổn định. Khấu hao giảm từ 2.194 xuống 1.691 (tài sản đã khấu hao 78% nguyên giá).
- **Khoản một lần:** hoàn nhập dự phòng trong CP QLDN là −492 tỷ (9T/26) so với −1.631 tỷ (9T/25). Như vậy kỳ gốc còn được "đỡ" nhiều hơn, tức tăng trưởng lõi 9T còn cao hơn mức báo cáo. Q3/26 có CP QLDN +354 tỷ (dương), nên quý này không bị thổi phồng bởi hoàn nhập.
- **Nền so sánh:** FY25 điều chỉnh đạt 10.110 tỷ ở Brent 68. Hồi quy LN năm theo Brent năm (2016-2025, R² 0,68) cho độ dốc **≈120 tỷ LN/năm cho mỗi 1 USD Brent**. LN TTM cao hơn đường hồi quy 2.291 tỷ/năm (phần dư: LNG, STT 2B, khấu hao giảm, cầu điện +9,8%). Mô hình cho phần dư này một trục 0/50/100%.
- ⇒ **Surprise là surprise theo chu kỳ dầu.** Nếu Brent về 72 thì LN hoạt động mô hình (chưa gồm lãi tiền gửi) còn ~10.820 tỷ/năm (đã gồm 50% phần dư), so với ~13.550 tỷ TTM.

## 3. Giá trị nội tại (câu hỏi 2) — `calc/model.py`, khoá `calc/LOCK_prerun.txt`
**Cấu trúc:** Giá trị = tiền ròng theo sổ + **XDCB theo giá sổ (r2/E1)** + LN hoạt động Q4/26 (**tỷ trọng Q4 0,231 năm, r2**) + NOPAT 2027–2028 chiết khấu + giá trị cuối kỳ NOPAT₂₀₂₉/(r + suy giảm). Áp RONIC = Ke (moat không thưởng); conv = 1 (capex duy trì ≈ khấu hao). **Capex tăng trưởng XDCB 5.916,4 tỷ (đường ống Lô B–Ô Môn, LNG Sơn Mỹ…; LN của chúng KHÔNG nằm trong NOPAT lịch sử) được cộng 100% giá sổ — NPV 0 (luật 03/11, tiền lệ FPT CIP_EDU / DGC NS_CIP); không cộng thêm giá trị tăng trưởng.** (r1 đã nói "không cộng không trừ" — sai: bỏ mất giá sổ của tài sản chưa sinh LN.)
**r = 13,5%** (neo CCTG 12T 7,40% ngày 02/11, `deposit_rate_vn` 09/11). Độ nhạy theo lãi huy động: −100bp ⇒ 52.365 · −50bp ⇒ 51.216 · +50bp ⇒ 49.146 · +100bp ⇒ 48.211.

**Tiền ròng 30/09/2026 (tỷ):** tiền 15.540,6 + HTM 35.276,9 − vay 4.261,6 − cổ tức phải trả 5.491,7 − CĐKKS 1.409,5 = 39.654,7 tỷ = 16.434 đ/cp. **Bổ sung r2:** + XDCB 5.916,4 (E1) + tiền khí trả trước bao tiêu 1.775,5 (E6a, tài sản thu hồi, 100% giá sổ, chưa trừ thuế [UL]) − Quỹ khen thưởng phúc lợi 875,6 (E6b, như nợ) ⇒ **46.470,9 tỷ = 19.259 đ/cp** (trong đó XDCB 2.452 đ/cp).
- Giá 06/11 đã ex-quyền cổ tức: GDKHQ 22/09, hệ số Close/Price 0,9718→1,0 (BQ Close điều chỉnh 21/09 = 86.100 vs Price 88.600 ⇒ ngụ ý **2.500 đ/cp**; Báo cáo biến động VCSH ghi chia cổ tức 6.032,4 tỷ = 2.500 × 2,413 tỷ cp). Khoản phải trả trên BCĐKT (mã 313) là 5.491,7 tỷ, **lệch 540,7 tỷ so với 6.032,4 — CHƯA GIẢI THÍCH** (điểm mở; tâm không đổi, dùng số bảng cân đối). Vì vậy trừ khoản phải trả là đúng. (r1 ghi "2,82% × ~80k ≈ 2.276" — sai, đã sửa.)
- Dự phòng phải trả DH 3.300 tỷ (giả định ARO) đặt trục 0/50/100%.

| Kịch bản (w) | Brent Q4/26 · 2027 · 2028 · dài hạn | Suy giảm/năm | Giá trị (đ/cp, trục giữa) |
|---|---|---|---|
| XẤU (0,275) | 95 · 72 · 62 · 62 | 2,8% | 44.338 |
| CƠ SỞ (0,45) | 100 · 85 · 75 · 72 | 1,4% | 50.168 |
| TỐT (0,275) | 105 · 100 · 85 · 82 | 0% | 57.120 |
Cơ sở chọn Brent: dài hạn neo bình quân 2023-25 là 76,5 (BQ). Đường 2027 theo K1/K2/K3 của Bobby. Trọng số đối xứng (tiền lệ FPT r3 D1) [UL].
**Lưới 243 kết cục** (kịch bản × hệ số Brent ±25% × ARO 0/50/100% × Brent dài hạn ±5 × phần dư 0/50/100%): P10 43.327 · P25 46.019 · P50 49.817 · P75 53.890 · P90 57.840 · min 38.781 · max 64.275.
**Vùng giá (sau CK, cỡ 5 tỷ):** rẻ < 43.300 · hợp lý 43.300–57.800 · đắt > 57.800.
**Đối chiếu P/E lịch sử (E4):** P/E TTM hiện tại 12,1x (EPS TTM 6.110đ; BQ quý 2026Q3 = 12,6x). Lịch sử GAS 2016Q1–2026Q3 (43 quý, BQ `ticker_financial.PE`): min 11,7x · max 26,5x · trung vị 15,6x ⇒ hiện sát đáy 10 năm. **Tâm r2 ≈ 8,2x EPS TTM** (P10 7,1x · P90 9,5x), tức khung chiết khấu danh nghĩa 13,5% + RONIC = Ke + suy giảm cho giá trị thấp hơn nhiều so với mức thị trường từng trả. Mô hình KHÔNG ép LN: LN hoạt động ở Brent 72 = 10.820 + lãi tiền gửi sau thuế ~1.190 ≈ 12.000 tỷ/năm, còn hào phóng hơn LN thực 2023-25 (11.606 / 10.398 / 10.110) — chênh lệch với giá đến từ quy ước khung, không phải LN quá thấp. (r1 viết "giá ngụ ý Brent dài hạn > 190 USD — phi thực tế": bỏ, vì gây hiểu sai.)

## 4. Vị thế & lợi thế cạnh tranh (5F tầng b) — làm lần đầu (data/moat_tags.csv chưa có GAS)
- **Loại hình DN:** hạ tầng trung nguồn độc quyền tự nhiên (đường ống Bạch Hổ/NCS/PM3-CAA, nhà máy xử lý khí [NỀN, sector read §3]) + thương mại LPG (phân mảnh) + LNG (chuyển ngang).
- **Bằng chứng định lượng nhiều chu kỳ (BQ):** ROIC 10Y bình quân 20,4%, **ROIC_Min10Y 13,8%**, ROIC_Min5Y 16,9%, ROE_Min10Y 16,0% so với Ke 13,5%. Lợi nhuận siêu ngạch tồn tại qua cả năm Brent 43 (2020: LN 7.812 tỷ). Đạt điều kiện (i). Cơ chế rào cản gọi tên được (độc quyền hạ tầng + quy hoạch): đạt (ii).
- **Đồng hồ cắt hào (lực thứ 6): CÓ.** Mỏ cũ suy giảm (sector read: 10-11 xuống ~8-9 tỷ m³; phần dư hồi quy NP–Brent 2016-2025 có xu hướng ÂM ≈ −119 tỷ/năm, ≈ −1,1%/năm; NP ~ Brent + thời gian ≈ −181 tỷ/năm, ≈ −1,7%/năm), Lô B lùi sang Q3/2027, LNG pass-through biên mỏng (**% biên gộp giảm là pha loãng cơ học, không dùng làm bằng chứng — E2**), cước ống vẫn tạm tính chờ BCT duyệt. ⇒ **Không đạt (iii).**
- LPG: không có hào (biên gộp 5,6-7,8%, bán lẻ phân mảnh). Tập trung khách hàng (EVN/nhà máy điện, đạm): cần kiểm chứng (BCTC quý không tách).
- **Kết luận: moat_tier NARROW · moat_type REGULATORY/INFRA · rủi ro số 1: dịch chuyển cơ cấu sang LNG chuyển ngang + mỏ cũ cạn ⇒ biên/đơn vị co lại.** Moat không bền ⇒ **KHÔNG thêm tham số moat** (RONIC = Ke, có suy giảm 0-4%/năm). Không trừ thêm.
- **Độ nhạy moat:** giả sử không suy giảm ở mọi kịch bản ("không suy giảm"; WIDE còn đòi RONIC > Ke nên không phải WIDE) ⇒ +2.733 đ/cp (tâm ~52.900). Suy giảm +3pp ⇒ −5.039 đ/cp. Cả hai đều không đổi nhãn.
- **Đề xuất dòng moat_tags.csv (human-curated, KHÔNG tự sửa):** `GAS,NARROW,REGULATORY/INFRA,?,"Midstream pipeline/GPP natural monopoly but countdown: field depletion, LNG pass-through thin margin (dry-gas GPM 21.9%->18.1% 9T), provisional pipeline tariff; LPG no moat; free-float 4.24% public-company status at risk",2026-11-09,dd_lagcand_20261109,N`

## 5. Điểm yếu / rủi ro & điều làm nhận định đổi theo CẢ HAI chiều (câu hỏi 3)
**Lên (nâng giá trị/nhãn):**
- LN quý 2027 duy trì ≥ 3.500 tỷ/quý trong khi Brent ≤ 80. Điều này cho thấy phần dư bền >100%, mỗi +1.000 tỷ LN bền/năm ≈ +2.800 đ/cp (1.000/(13,5%+1,4%)/2,413 tỷ cp).
- BCT duyệt cước ống chính thức ≥ mức tạm tính; Qc ≥ 70% (E1 Bobby P = 0,40); Lô B first gas đúng Q3/2027.
- Lãi huy động 12T giảm: mỗi −100bp ≈ +2.219 đ/cp. Ngay cả −300bp vẫn chưa chạm giá (r ngụ ý 7,05%).
- Phương án khắc phục free float qua phát hành có giá cao hơn giá trị nội tại (lợi cho cổ đông hiện hữu) hoặc luật miễn trừ.

**Xuống:**
- Brent < 75 hai quý liên tiếp (F2/F3 Bobby P ≈ 0,35/0,33 dưới 85/80) và Q4/26 LN < 2.500 tỷ (Q4 vốn yếu theo mùa: Q4/24 2.044, Q4/25 1.361).
- Truy thu cước ống hồi tố (−1.500 tỷ ⇒ −618 đ/cp); lỗ tồn kho LPG nếu CP giảm 15% (≈ −82 đ/cp).
- **Hủy tư cách công ty đại chúng / hủy niêm yết** (hạn khắc phục 31/12/2026). Hoặc PVN thoái ≥ 5,76% (~139 triệu cp ≈ 10.300 tỷ ở giá hiện tại ≈ 90 phiên ADV): áp lực cung lớn.
- **HARD ABANDON** (với vị thế đã mua): có quyết định hủy niêm yết, hoặc LN 4 quý < 9.500 tỷ khi Brent ≥ 80.

## 6. Cờ tự động của hệ — thật hay nhiễu (câu hỏi 4)
| Cờ | Đánh giá |
|---|---|
| W CEIL2 2026-08-10 | **Thật nhưng theo chiều TĂNG**: trần 07/08 (+6,9%) và 10/08 (+6,97%), ngay sau KQ Q2 (CBTT 30/07). `data/anomaly_flags.json`: ret 6,97, idio 6,48, vol_x 2,1. TTL 30 ngày đã hết 09/09. Không phải tín hiệu rủi ro; cờ CEIL2 gom chung với FLOOR là tính chất có sẵn của gate (finding 07/08). |
| DCF auto RICH (~67.081 vs 74.100) | **Cùng chiều, đúng.** Mô hình độc lập ra tâm thấp hơn (50.146). Lý do: auto DCF không trừ cổ tức phải trả/CĐKKS, và ngoại suy LN TTM ở Brent 82 (ước lượng, chưa đọc code auto DCF). |
| P/E 12,1 | Đúng số (TTM). Nhưng gồm 16.434 đ/cp tiền ròng; nhưng LN TTM ở Brent 82, cao hơn trung bình chu kỳ; so P/E lịch sử 11,7–26,5x (trung vị 15,6x), 12,1x là sát đáy (xem E4). |
| Trọng tâm brief | Công thức giá bán khí: chưa kiểm được từ nguồn gốc (BCTC không công bố); chỉ có hệ số thực nghiệm 120 tỷ/USD. Cước tạm tính: có (sector read), BCTC không tách dự phòng. Take-or-pay: tiền khí trả trước theo bao tiêu 1.775,5 tỷ (từ 2.122,6, đang thu hồi). LPG tồn kho: HTK tổng 2.763,6 tỷ (từ 4.587,5). Thu một lần: hoàn nhập DP −492 tỷ 9T. |

## 7. Thanh khoản / sizing (câu hỏi 5)
- ADV trung vị 250 phiên 113,2 tỷ (60 phiên 97,9 tỷ); σ ngày 3,11%. CK = σ·√(Q/ADV): **5 tỷ ⇒ 0,65%** (tham gia 4,4% ADV); 40tr ⇒ 0,06%; 10tr ⇒ 0,03%.
- Thoát 5 tỷ ở mức tham gia 10% ≈ 0,44 phiên. Thanh khoản không phải ràng buộc ở mọi khẩu phần sleeve hiện tại.
- Free float thực ~4,24% (≈ 102 triệu cp ≈ 7.600 tỷ): thanh khoản phụ thuộc trạng thái niêm yết (mục 5).
- Khẩu phần đề xuất: nếu plan vẫn mua theo cơ học LAG thì giữ ở mức tối thiểu của sleeve (tiền lệ ≤ 0,5% NAV). DD không ủng hộ nâng tỷ trọng.

## 8. WARNING pháp lý / quản trị (chỉ WARNING, không vào tâm)
- Không còn đủ điều kiện công ty đại chúng (CBTT 31/12/2025; báo cáo quản trị 6T/2026: PVN vẫn 95,76%). Chuyên gia (Yuanta, qua báo) đánh giá rủi ro hủy niêm yết thấp; GAS chờ cơ chế miễn trừ / tăng vốn (chưa có chi tiết).
- Nhân sự: Chủ tịch Nguyễn Thanh Bình bị miễn nhiệm 23/07/2026, TGĐ Phạm Văn Phong bị miễn nhiệm 21/07/2026 (BCTC 6T, trang BTGĐ). Báo chí ghi là PVN điều động. ĐHĐCĐ bất thường 14/09/2026 miễn nhiệm 3 thành viên HĐQT.
- Soát xét 6T/2026 (Deloitte VN, 12/08/2026): chấp nhận toàn phần, không có đoạn nhấn mạnh.

## 9. Giả định [UL] / mở (đầy đủ: `calc/assumptions_r2.json`, md5 `c02f04b50d650838b862f59824187de2` (r2; `calc/assumptions_r2.json`))
- Trọng số 0,275/0,45/0,275 · suy giảm 2,8/1,4/0% (r2) · Brent dài hạn 62/72/82 ±5 · hệ số Brent ±25% · phần dư 0/50/100% · ARO 0/50/100% — đều [UL] đối xứng.
- Hồi quy quý (2023Q3–2026Q3) **bị loại** vì ngoại suy vô lý (độ dốc 108,7 tỷ/quý/USD ⇒ LN ~3.000 tỷ/năm ở Brent 62, trái với 2025). Ghi lại minh bạch trong `calc/LOCK_prerun.txt`.
- Mở: thuyết minh dự phòng DH 3.300 tỷ (**CHƯA KIỂM** — các thuyết minh 16-23 của BCTC HN Q3 đã đọc không có mục dự phòng mã 343; độ nhạy trừ 100% theo sổ = −679 đ/cp); lý do miễn nhiệm Chủ tịch/TGĐ 07/2026 và kế hoạch free-float trước 31/12/2026 (**CHƯA KIỂM**, chờ legal-vn); chênh 540,7 tỷ cổ tức;  sản lượng theo mỏ/khách hàng; công thức giá khí (tỷ lệ % MFO, sàn/trần); phần Q3 của khoản hoàn nhập 492 tỷ; chi tiết phương án tăng vốn.

## 10. File
`src/` (BCTC gốc + PNG trang đã đọc) · `calc/notes_bctc.md` · r1: `calc/assumptions.json` · `calc/model.py` → `calc/model_out.txt` (md5 `cf8ff1ce…`) · `SUMMARY_r1.json` · `REPORT_r1.md`. **r2:** `calc/assumptions_r2.json` · `calc/model_r2.py` → `calc/model_out_r2.txt` (2 lần chạy cùng md5 `d59c081c…`, `calc/LOCK_prerun_r2.txt`, `calc/LOCK_post_md5_r2.txt`) · `calc/make_summary_r2.py` → `SUMMARY.json`.

Nguồn web (WARNING): [Znews — PV GAS không còn đủ điều kiện công ty đại chúng](https://znews.vn/pv-gas-khong-con-du-dieu-kien-la-cong-ty-dai-chung-post1617113.html) · [VnBusiness — 4,24%](https://vnbusiness.vn/pv-gas-hon-24740-co-dong-chi-nam-giu-424-tong-so-co-phieu.html) · [VnEconomy — rủi ro hủy niêm yết DN vốn Nhà nước](https://vneconomy.vn/khong-lo-ngai-rui-ro-huy-niem-yet-o-nhom-doanh-nghiep-co-von-lon-nha-nuoc.htm) · [Người Quan Sát — ĐHĐCĐ bất thường miễn nhiệm](https://nguoiquansat.vn/pv-gas-thong-qua-mien-nhiem-chu-tich-va-tong-giam-doc-tai-dhdcd-bat-thuong-316132.html) · [Nhà Đầu Tư — PVN điều động lãnh đạo](https://nhadautu.vn/petrovietnam-dieu-dong-lanh-dao-pvgas-co-phieu-gas-ve-day-6-thang-d106480.html)


## Phụ lục E — ĐÍNH CHÍNH r2 (áp ERRATA_r1_skeptic.md; không mở rộng phạm vi)
Skeptic r1 kết luận REFUTED số liệu/văn bản; nhãn TRÊN vùng vẫn giữ. Dưới đây là từng mục, trước → sau (đ/cp, sau CK 5 tỷ; số trong `calc/model_out_r2.txt`).

**Bảng tích luỹ (thứ tự errata):**
| Bước | Tâm | P10 | P90 |
|---|---|---|---|
| r1 (gốc) | 46.488 | 39.010 | 55.150 |
| + E1 XDCB 5.916,4 tỷ theo giá sổ (NPV 0) | 48.924 | 41.446 | 57.585 |
| + E2 suy giảm 2,8/1,4/0% (thay 4/2/0) | 49.886 | 43.064 | 57.585 |
| + E6a Q4 = 0,231 năm (thay 0,25) | 49.775 | 42.957 | 57.470 |
| + E6b bao tiêu +1.775,5 tỷ | 50.506 | 43.688 | 58.201 |
| + E6c Quỹ KT-PL −875,6 tỷ = **r2 cuối** | **50.146** | **43.327** | **57.840** |

**Tác động riêng từng mục (so với r1, một mình):** E1 +2.436 · E2 +962 · Q4 −111 · bao tiêu +731 · quỹ KT-PL −360 (tâm; khớp ước lượng skeptic +2.436/+962/−114/+731/−360).

- **E1 — ÁP (vi phạm luật dự án mới đã sửa).** XDCB 5.916,4 tỷ cộng 100% giá sổ (TM13: đường ống Lô B–Ô Môn 5.192,1 gồm first gas Q3/2027, Sơn Mỹ LNG 228,9, STT 41,9, ERP 199,1, khác 254,5). Không cộng giá trị tăng trưởng (NPV 0). Dòng "không cộng không trừ" ở r1 là sai.
- **E2 — ÁP.** Bỏ căn cứ "biên gộp 21,9% → 18,1%" (pha loãng cơ học; LN gộp tuyệt đối +55%). Căn cứ mới là dữ liệu: phần dư hồi quy NP–Brent 2016-2025 xu hướng −119 tỷ/năm (−1,1%/năm so với NP trung bình 10.402 tỷ); NP ~ Brent + thời gian −181 tỷ/năm (−1,7%/năm) (đo trong `model_out_r2.txt`, khoá `E2_trend`). Suy giảm bình quân trọng số = 1,4% (XAU 2,8 / CƠ SỞ 1,4 / TỐT 0). Lưu ý: chỉ 10 điểm năm, Brent 2016 chỉ 49 ngày dữ liệu (ghi chú độ tin cậy thấp). Đổi tên độ nhạy "moat WIDE = không suy giảm" thành "không suy giảm".
- **E3 — ÁP (văn bản).** Bỏ "r ngụ ý 6,2% ~ phi rủi ro ~6,75%" (6,75% không nguồn; snapshot TPCP 10Y 4,58% UNVERIFIED, chỉ dùng Δ; 6,2% tính khi cài sẵn suy giảm 2%). Diễn đạt đúng: ở r = 13,5%, giá ngụ ý tăng trưởng danh nghĩa vĩnh viễn ≈ +5,3%/năm (đã gồm E1; đo bằng cách đặt suy giảm âm đồng đều ở cả 3 kịch bản cho tâm bằng giá). r ngụ ý theo khung r2 = 7,05% (r1: 6,24%).
- **E4 — ÁP (văn bản).** Bỏ "giá ngụ ý Brent dài hạn > 190 USD — phi thực tế" (Taylor không ép LN; LN hoạt động ở Brent 72 ≈ 12.000 tỷ gồm lãi, hào phóng hơn 2023-25). Thêm kiểm P/E lịch sử (mục 3). Nhãn TRÊN vùng là TƯƠNG ĐỐI THEO KHUNG (r danh nghĩa 13,5%, RONIC = Ke, suy giảm), không phải bằng chứng thị trường hưng phấn; P/E hiện 12,1x sát đáy 10 năm (11,7x).
- **E5 — ÁP (văn bản), điểm mở còn lại.** Cổ tức 2.500 đ/cp (BQ Close/Price và Báo cáo biến động VCSH 6.032,4 tỷ = 2.500 × 2,413 tỷ cp đều khớp); khoản phải trả 5.491,7 lệch 540,7 tỷ — chưa giải thích (cổ tức tạm ứng đã trả? chưa kiểm). Tâm không đổi (dùng số bảng cân đối).
- **E6 — ÁP một phần.** (a) bao tiêu +1.775,5 tỷ tài sản thu hồi — ÁP (100% giá sổ, [UL] chưa trừ thuế; +731); (b) Quỹ KT-PL 875,6 coi như nợ — ÁP (−360); (c) Q4 = 0,231 năm — ÁP (đo tỷ trọng trung vị Q4 2014-2025 = 0,2305; −111); (d) **dự phòng 343 (3.300 tỷ): CHƯA KIỂM** — thuyết minh dự phòng phải trả dài hạn không có trong các thuyết minh 16-23 đã đọc (BCĐKT chỉ có số 3.300,0); giữ trục 0/50/100% [UL], độ nhạy trừ 100% theo sổ = −679 đ/cp ghi cạnh, KHÔNG vào tâm; (e) Brent 2016 chỉ 49 ngày dữ liệu — ghi chú E2; (f) phần dư RES có thể chứa lãi tồn kho LPG Q2–Q3/26 ⇒ thiên lệch LÊN (không sửa, đã có trục 0/50/100%).

**Nhãn:** TRÊN vùng (giữ nguyên) — giá 74.100 > P90 57.840 (+28,1%); tâm 50.146 (giá cao hơn 47,8%). **Vùng rule 4** (sau CK 5 tỷ): rẻ < 43.300 · hợp lý 43.300–57.800 · đắt > 57.800. Tổng hợp skeptic dự báo tâm ~49.800–50.100, P90 ~58.500 — kết quả đo 50.146 / 57.840 nằm sát (không dùng số skeptic làm đầu vào). Không đổi hướng khuyến nghị: giá nằm ngoài vùng giá trị; WARNING pháp lý (free float 4,24%, thay lãnh đạo) vẫn chỉ là WARNING, không vào tâm.
**Việc mở / chưa kiểm:** TM dự phòng 343; lý do miễn nhiệm Chủ tịch/TGĐ 07/2026 và kế hoạch free-float trước 31/12/2026 (legal-vn); chênh 540,7 tỷ cổ tức; công thức giá khí; phần Q3 của hoàn nhập 492 tỷ.
