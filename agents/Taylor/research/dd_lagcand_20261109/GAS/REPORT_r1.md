# DD — GAS (Tổng Công ty Khí Việt Nam – PV GAS) · 09/11/2026 · job `Taylor_20261109_073604` · vòng r1 (chờ fundamental-skeptic)

Ứng viên LAG (LAG_LO, ADV3T 87 tỷ) cho plan 09/11. Chỉ nghiên cứu, không lệnh/wire. Định giá mù giá thị trường; giá 74.100đ (BQ 06/11) chỉ dùng để dán nhãn.
Nguồn chính: BCTC HN Q3/2026 (CBTT 30/10/2026) + BCTC HN soát xét 6T/2026 (Deloitte), tải từ pvgas.com.vn vào `src/` (scan, đọc ảnh) → số liệu chép tại `calc/notes_bctc.md`. Chuỗi lợi nhuận lịch sử: BQ `ticker_financial` (Q3/26 4.576,5 tỷ khớp BCTC).

## 1. Kết luận
- **Giá trị nội tại SAU chiết khấu thanh khoản (cỡ 5 tỷ): tâm 46.488đ · P10 39.010 · P50 45.983 · P90 55.150.** Trước CK: tâm 46.794 (P10 39.267 / P90 55.513). Cỡ sleeve 40tr: tâm 46.767.
- **Nhãn: TRÊN vùng (đắt).** Giá 74.100 cao hơn tâm 59% và cao hơn P90 34%; 100% trọng số lưới nằm dưới giá. Kết luận vững: ngay cả khi r = 8% (ngoài luật), tâm chỉ đạt 63.446 (vẫn dưới giá). Muốn tâm bằng giá thì r ngụ ý = **6,2%**, tức xấp xỉ lãi suất phi rủi ro (~6,75%), gần như không có phần bù rủi ro cổ phần.
- **LAG chọn vì:** LN quý III tăng mạnh (+79,5% YoY). Phần tăng này **là thật, không đến từ khoản một lần, nhưng không bền**: nó chạy theo giá dầu Brent (Q3 bình quân 90,7 so với 68,0 USD, +33%). Sector read đọc mù (Bobby) dự báo giá dầu đã qua đỉnh cấp tính (F3: trung vị 88 vào 03/2027) và nhãn tầm 2027-30 là STRUCTURAL/ADMIN.
- **Rủi ro lớn nhất (WARNING, không đưa vào tâm):** GAS **không còn đủ điều kiện công ty đại chúng**. PVN nắm 95,76%, cổ đông nhỏ chỉ 4,24% (ngưỡng 10%); CBTT 31/12/2025, thời hạn khắc phục 1 năm. Thêm: thay cả Chủ tịch và TGĐ hồi 07/2026.
- **Khuyến nghị cho plan:** theo DD, giá nằm ngoài vùng giá trị. Nếu LAG vẫn mua theo cơ học thì chỉ nên ở khẩu phần tối thiểu, và xem đây là vị thế ăn theo đà lợi nhuận (momentum của LN), không phải vị thế giá trị.

## 2. Vì sao LAG chọn — surprise bao nhiêu, bền hay một lần (câu hỏi 1)
| LNST CĐ mẹ (tỷ) | Q3/26 | Q3/25 | Δ | 9T/26 | 9T/25 | Δ |
|---|---|---|---|---|---|---|
| | 4.576,5 | 2.549,1 | **+79,5%** | 13.381,2 | 10.053,3 | +33,1% |
Q2/26 đạt 5.860,1 ⇒ Q3 giảm 21,9% QoQ. LN TTM 14.742 tỷ (EPS 6.110đ ⇒ P/E 12,1, khớp cờ hệ).

**Tách nguồn tăng (TM25/27, 9T/26 so với 9T/25):**
- Khí khô + LNG: LN gộp 12.473 so với 8.052 (+4.421 tỷ). Doanh thu +87% (một phần là LNG cho NT3&4 từ 01/2026 theo cơ chế chuyển ngang), nhưng **biên gộp giảm từ 21,9% xuống 18,1%**. Đây là dấu hiệu đúng như Bobby mô tả: "pool lợi nhuận" đang dịch sang LNG biên mỏng.
- LPG: 3.585 so với 2.816 (+769 tỷ; biên 7,8% so với 5,6%). Một phần có thể là lãi tồn kho khi giá CP tăng (+60% YoY), chưa tách được.
- Vận chuyển khí: 1.450 so với 1.409, ổn định. Khấu hao giảm từ 2.194 xuống 1.691 (tài sản đã khấu hao 78% nguyên giá).
- **Khoản một lần:** hoàn nhập dự phòng trong CP QLDN là −492 tỷ (9T/26) so với −1.631 tỷ (9T/25). Như vậy kỳ gốc còn được "đỡ" nhiều hơn, tức tăng trưởng lõi 9T còn cao hơn mức báo cáo. Q3/26 có CP QLDN +354 tỷ (dương), nên quý này không bị thổi phồng bởi hoàn nhập.
- **Nền so sánh:** FY25 điều chỉnh đạt 10.110 tỷ ở Brent 68. Hồi quy LN năm theo Brent năm (2016-2025, R² 0,68) cho độ dốc **≈120 tỷ LN/năm cho mỗi 1 USD Brent**. LN TTM cao hơn đường hồi quy 2.291 tỷ/năm (phần dư: LNG, STT 2B, khấu hao giảm, cầu điện +9,8%). Mô hình cho phần dư này một trục 0/50/100%.
- ⇒ **Surprise là surprise theo chu kỳ dầu.** Nếu Brent về 72 thì LN hoạt động mô hình (chưa gồm lãi tiền gửi) còn ~10.820 tỷ/năm (đã gồm 50% phần dư), so với ~13.550 tỷ TTM.

## 3. Giá trị nội tại (câu hỏi 2) — `calc/model.py`, khoá `calc/LOCK_prerun.txt`
**Cấu trúc:** Giá trị = tiền ròng theo sổ + LN hoạt động Q4/26 + NOPAT 2027–2028 chiết khấu + giá trị cuối kỳ NOPAT₂₀₂₉/(r + suy giảm). Áp RONIC = Ke (moat không thưởng); conv = 1 (capex duy trì ≈ khấu hao, capex mới XDCB 5.916 tỷ tính theo giá sổ, NPV 0).
**r = 13,5%** (neo CCTG 12T 7,40% ngày 02/11, `deposit_rate_vn` 09/11). Độ nhạy theo lãi huy động: −100bp ⇒ 48.573 · −50bp ⇒ 47.494 · +50bp ⇒ 45.547 · +100bp ⇒ 44.664.

**Cầu tiền ròng 30/09/2026 (tỷ):** tiền 15.540,6 + HTM 35.276,9 − vay 4.261,6 − cổ tức phải trả 5.491,7 − CĐKKS 1.409,5 = **39.654,7 tỷ = 16.434 đ/cp**.
- Giá 06/11 đã ex-quyền cổ tức: GDKHQ 22/09, hệ số Close/Price 0,9718→1,0 ≈ 2.276 đ/cp = 5.491,7 tỷ / 2,413 tỷ cp. Vì vậy trừ khoản phải trả là đúng.
- Dự phòng phải trả DH 3.300 tỷ (giả định ARO) đặt trục 0/50/100%.

| Kịch bản (w) | Brent Q4/26 · 2027 · 2028 · dài hạn | Suy giảm/năm | Giá trị (đ/cp, trục giữa) |
|---|---|---|---|
| XẤU (0,275) | 95 · 72 · 62 · 62 | 4% | 39.972 |
| CƠ SỞ (0,45) | 100 · 85 · 75 · 72 | 2% | 46.309 |
| TỐT (0,275) | 105 · 100 · 85 · 82 | 0% | 54.411 |
Cơ sở chọn Brent: dài hạn neo bình quân 2023-25 là 76,5 (BQ). Đường 2027 theo K1/K2/K3 của Bobby. Trọng số đối xứng (tiền lệ FPT r3 D1) [UL].
**Lưới 243 kết cục** (kịch bản × hệ số Brent ±25% × ARO 0/50/100% × Brent dài hạn ±5 × phần dư 0/50/100%): P10 39.010 · P25 42.012 · P50 45.983 · P75 50.479 · P90 55.150 · min 34.792 · max 61.602.
**Vùng giá (sau CK, cỡ 5 tỷ):** rẻ < 39.000 · hợp lý 39.000–55.100 · đắt > 55.100.
**Đối chiếu:** P/E phần hoạt động (bỏ tiền ròng) ở giá hiện tại = (74.100 − 16.434) / 5.616 = **10,3x**, trong khi 1/Ke = 7,4x trên LN chuẩn hoá (vốn thấp hơn TTM). Giá ngụ ý Brent dài hạn > 190 USD (CƠ SỞ) — phi thực tế.

## 4. Vị thế & lợi thế cạnh tranh (5F tầng b) — làm lần đầu (data/moat_tags.csv chưa có GAS)
- **Loại hình DN:** hạ tầng trung nguồn độc quyền tự nhiên (đường ống Bạch Hổ/NCS/PM3-CAA, nhà máy xử lý khí [NỀN, sector read §3]) + thương mại LPG (phân mảnh) + LNG (chuyển ngang).
- **Bằng chứng định lượng nhiều chu kỳ (BQ):** ROIC 10Y bình quân 20,4%, **ROIC_Min10Y 13,8%**, ROIC_Min5Y 16,9%, ROE_Min10Y 16,0% so với Ke 13,5%. Lợi nhuận siêu ngạch tồn tại qua cả năm Brent 43 (2020: LN 7.812 tỷ). Đạt điều kiện (i). Cơ chế rào cản gọi tên được (độc quyền hạ tầng + quy hoạch): đạt (ii).
- **Đồng hồ cắt hào (lực thứ 6): CÓ.** Mỏ cũ suy giảm (sector read: 10-11 xuống ~8-9 tỷ m³), Lô B lùi sang Q3/2027, LNG có biên mỏng (biên gộp khí khô+LNG giảm từ 21,9% xuống 18,1% trong 1 năm), cước ống vẫn tạm tính chờ BCT duyệt. ⇒ **Không đạt (iii).**
- LPG: không có hào (biên gộp 5,6-7,8%, bán lẻ phân mảnh). Tập trung khách hàng (EVN/nhà máy điện, đạm): cần kiểm chứng (BCTC quý không tách).
- **Kết luận: moat_tier NARROW · moat_type REGULATORY/INFRA · rủi ro số 1: dịch chuyển cơ cấu sang LNG chuyển ngang + mỏ cũ cạn ⇒ biên/đơn vị co lại.** Moat không bền ⇒ **KHÔNG thêm tham số moat** (RONIC = Ke, có suy giảm 0-4%/năm). Không trừ thêm.
- **Độ nhạy moat:** giả sử WIDE (không suy giảm ở mọi kịch bản) ⇒ +3.695 đ/cp (tâm ~50.200). NONE (suy giảm +3pp) ⇒ −4.758 đ/cp. Cả hai đều không đổi nhãn.
- **Đề xuất dòng moat_tags.csv (human-curated, KHÔNG tự sửa):** `GAS,NARROW,REGULATORY/INFRA,?,"Midstream pipeline/GPP natural monopoly but countdown: field depletion, LNG pass-through thin margin (dry-gas GPM 21.9%->18.1% 9T), provisional pipeline tariff; LPG no moat; free-float 4.24% public-company status at risk",2026-11-09,dd_lagcand_20261109,N`

## 5. Điểm yếu / rủi ro & điều làm nhận định đổi theo CẢ HAI chiều (câu hỏi 3)
**Lên (nâng giá trị/nhãn):**
- LN quý 2027 duy trì ≥ 3.500 tỷ/quý trong khi Brent ≤ 80. Điều này cho thấy phần dư bền >100%, mỗi +1.000 tỷ LN bền/năm ≈ +2.700 đ/cp (1.000/(13,5%+2%)/2,413 tỷ cp).
- BCT duyệt cước ống chính thức ≥ mức tạm tính; Qc ≥ 70% (E1 Bobby P = 0,40); Lô B first gas đúng Q3/2027.
- Lãi huy động 12T giảm: mỗi −100bp ≈ +2.085 đ/cp. Ngay cả −300bp vẫn chưa chạm giá.
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
| DCF auto RICH (~67.081 vs 74.100) | **Cùng chiều, đúng.** Mô hình độc lập ra tâm thấp hơn (46.488). Lý do: auto DCF không trừ cổ tức phải trả/CĐKKS, và ngoại suy LN TTM ở Brent 82 (ước lượng, chưa đọc code auto DCF). |
| P/E 12,1 | Đúng số (TTM). Nhưng gồm 16.434 đ/cp tiền ròng; P/E phần hoạt động 10,3x trên LN đỉnh chu kỳ dầu. |
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

## 9. Giả định [UL] / mở (đầy đủ: `calc/assumptions.json`, md5 `3d026e48c49a96b639537feb52ec7b98`)
- Trọng số 0,275/0,45/0,275 · suy giảm 4/2/0% · Brent dài hạn 62/72/82 ±5 · hệ số Brent ±25% · phần dư 0/50/100% · ARO 0/50/100% — đều [UL] đối xứng.
- Hồi quy quý (2023Q3–2026Q3) **bị loại** vì ngoại suy vô lý (độ dốc 108,7 tỷ/quý/USD ⇒ LN ~3.000 tỷ/năm ở Brent 62, trái với 2025). Ghi lại minh bạch trong `calc/LOCK_prerun.txt`.
- Mở: thuyết minh dự phòng DH 3.300 tỷ; sản lượng theo mỏ/khách hàng; công thức giá khí (tỷ lệ % MFO, sàn/trần); phần Q3 của khoản hoàn nhập 492 tỷ; chi tiết phương án tăng vốn.

## 10. File
`src/` (BCTC gốc + PNG trang đã đọc) · `calc/notes_bctc.md` · `calc/assumptions.json` · `calc/model.py` → `calc/model_out.txt` (2 lần chạy cùng md5 `cf8ff1ce…`, `calc/LOCK_post_md5.txt`) · `calc/sens_r_wide.py/.txt` · `calc/make_summary.py` → `SUMMARY.json`.

Nguồn web (WARNING): [Znews — PV GAS không còn đủ điều kiện công ty đại chúng](https://znews.vn/pv-gas-khong-con-du-dieu-kien-la-cong-ty-dai-chung-post1617113.html) · [VnBusiness — 4,24%](https://vnbusiness.vn/pv-gas-hon-24740-co-dong-chi-nam-giu-424-tong-so-co-phieu.html) · [VnEconomy — rủi ro hủy niêm yết DN vốn Nhà nước](https://vneconomy.vn/khong-lo-ngai-rui-ro-huy-niem-yet-o-nhom-doanh-nghiep-co-von-lon-nha-nuoc.htm) · [Người Quan Sát — ĐHĐCĐ bất thường miễn nhiệm](https://nguoiquansat.vn/pv-gas-thong-qua-mien-nhiem-chu-tich-va-tong-giam-doc-tai-dhdcd-bat-thuong-316132.html) · [Nhà Đầu Tư — PVN điều động lãnh đạo](https://nhadautu.vn/petrovietnam-dieu-dong-lanh-dao-pvgas-co-phieu-gas-ve-day-6-thang-d106480.html)
