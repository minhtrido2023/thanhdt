# PAT — DD rev6 đầy đủ (sổ: dd_date 2026-11-17, rev 4) — 25/11/2026, job Taylor_20261125_063651

Làm lại theo phương án (a) user duyệt 25/11 13:3x ICT (w3 dừng Bước 0 vì D4). Nền: `dd_PAT_rebuttal_20261117/C/r5/` (VALUATION_r5 md5 `64aa2b2d…`, model_r5.py md5 `f6cd2e0e…`, không bị TRIM). Khoá rev6: `assumptions_rev6.md` md5 **`5207e413eb10404ccdf3aa47c7af9916`** (`lock_rev6.txt`) — viết TRƯỚC khi chạy. Calc: `calc/model_r6.py` (bọc model_r5, assert md5 cả hai; CONTROL r5 66.470,1 tái lập), chạy 2 lần `calc/run1.txt` = `run2.txt` md5 `f40663ca…`; output `calc/model_r6_out.json`. MÙ GIÁ trong pha dựng; giá 70.200 (17/11) kế thừa sổ, chỉ dùng cho nhãn.

## 0. Kết luận
**TÂM rev6 (r 13,5%, g 2%, sau CK thanh khoản 10%): 55.527 đ/cp** (trước CK 61.697). Vùng P25–P75 sau CK **40.485 – 67.228**; P10–P90 30.982 – 85.356; trung vị 57.116.
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 59.778 đ/cp sau CK (66.420 trước CK) (+7,66% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): PAT: so với lịch sử 10 năm của chính mã — **KHÔNG CHẮC (proxy lệch DD, k=0.35–0.88)** — phân vị [fade 8, hold 9], 53 tháng, N hiệu dụng ≈ 9.3 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị) ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.57); ROE5Y bị kẹp 45%
Tâm kỳ vọng điều chỉnh: 57.872 đ/cp sau CK (dải 56.700–59.045; +4,22% so với tâm base 55.527); căn cứ 2 hạng mục bậc B (cả hai chiều lên; mọi hạng mục chiều xuống là C — thuê đất 2034 −28,7% chỉ độ nhạy, xem `ADJ_CENTER.md`)

- **So sổ rev3 (59.823 sau CK): −7,18%** (−4.296 đ/cp). Bắc cầu: D4 −1,44% (66.470 → 65.510) rồi ô (A tắt, B bật) về D −5,82% (65.510 → 61.697).
- **Nhãn** (giá 70.200, 17/11, kế thừa): giá cao hơn tâm sau CK 26,4% và **trên P75 (67.228)** — cao hơn vùng hợp lý, trong P90. Cổng 0,85 × tâm sau CK = **47.198** không đạt ⇒ **không có biên an toàn, không mua** (kết luận r5 giữ, nay đã kiểm lại sau khi làm đầy đủ — mọi biến thể chiều lên trong §3/§7 vẫn < 70.200).
- Lớp nhãn đổi: r5 "TRONG P25–P75" → rev6 "TRÊN P75" ⇒ cần phản biện đầy đủ (B2), không cơ học.

## 1. Thay đổi so với r5 (khoá ở assumptions_rev6.md)
| # | Luật/hạng mục | r5 | rev6 | Tâm trước CK |
|---|---|---|---|---|
| 1 | D4 terminal RONIC = Ke | TV Gordon không tái đầu tư (RONIC ngầm ∞) | TV = NOPAT₂₀₄₆/r | 66.470 → 65.510 (−1,44%) |
| 2 | Ô (A tắt, B bật) | O2 ("H1/26 sạch", +4.800) | theo D (= r4) — killer skeptic r1, A1:133,143 | 65.510 → **61.697** (−5,82%) |
| 3 | Hạn thuê đất, cầm cố, capex môi trường | vắng / độ nhạy nhẹ | truy nguồn, phân loại (§4); không vào base | 0 |
Tỉ trọng TV (đường cơ sở): 8,4% giá trị ⇒ D4 tác động nhỏ vì chuỗi tường minh tới 2045. Từng cây q_B (D4, ô D): q=0 63.846 · q=0,25 61.412 · q=0,40 59.832. Tổng xác suất lá 1,0000000000 (9.072 lá).

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r (neo 03/11 lãi huy động 12T 7,40%, Δ đến 25/11 = 0, β=1)
| r | Trước CK | Sau CK | Δ % |
|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 66.420 | 59.778 | +7,66% |
| 12,5% (−100bp) | 65.567 | 59.010 | +6,27% |
| 13,0% (−50bp) | 63.554 | 57.198 | +3,01% |
| 13,4% (đầu trên dải Ke) | 62.057 | 55.851 | +0,58% |
| **13,5% BASE** | **61.697** | **55.527** | 0 |
| 14,0% (+50bp) | 59.979 | 53.981 | −2,78% |
| 14,5% (+100bp) | 58.386 | 52.547 | −5,37% |
β 0,5: ±50bp lãi huy động ⇒ ±25bp r ⇒ khoảng ±1,4–1,5% (nội suy từ bảng, ước lượng). Mọi mức r trong bảng: giá 70.200 > tâm sau CK.

## 3. Soát luật B5
- **D3 capex tuân thủ:** không có số (kế hoạch đầu tư 2026 KHÔNG TÌM ĐƯỢC, F1) ⇒ V4: không vào base, chỉ độ nhạy. Base đặt capex = khấu hao 45 tỷ/năm (capex thực 9T/26 chỉ 0,115 — `dd_PAT_20261114/facts_extracted.md:27`; HMLK 62% nguyên giá ⇒ KH 45 là mức thay thế tài sản, KHÔNG phải đệm dành cho capex môi trường — đính chính sau skeptic r1, Phụ lục E). Ngưỡng hoà vốn: một khoản capex môi trường một lần X tỷ trừ X/25 nghìn đ/cp trước CK (vd 50 tỷ ⇒ −2.000, −3,2%; ước lượng cơ học).
- **D4:** áp (§1). **D5:** BCTC KT 2025 có (UHY 749/2026, ngoại trừ tồn kho) ⇒ `audited_fy_missing=false`.
- **V3:** đo lại SAU khoá (BQ `ticker`, Price×Volume, 64 phiên 21/08–23/11/2026): GTGD bình quân **0,993 tỷ**, trung vị **0,588 tỷ** (r5 theo dispatch: 1,01/0,60) ⇒ cùng bậc, giữ CK 10%; nhãn theo sau CK. Ở 10–20% tham gia: 0,06–0,12 tỷ/phiên.
- **V5 moat:** NARROW (CAPTIVE_SUPPLY/PERMIT, dd_PAT_20261114 5F <12 tháng; bản objective NONE). Đồng hồ cắt hào: thuế XK 15% (2027), CIT ưu đãi hết 2030/2032, thuê đất ~2034, quặng ADMIN_GATED. Không thưởng/không trừ ở pha dự báo; D4 ở cuối kỳ. Kiểm nhanh 25/11: không có BCTC/CBTT mới sau Q3/26 được đọc.
- **V6 (chỉ hiển thị):** V_ngắn = LNST chuẩn hoá (trung vị TTM 12 quý 2023Q4–2026Q3 = 289,9 tỷ, BQ `ticker_financial` NP_P0..P3) × (1 − g/ROE; ROE TTM ≈ 291/708 = 41%, g/ROE 0,05) × 1,02/(0,135 − 0,02) / 25 tr cp ≈ **97.800** đ/cp; V_dài = DCF rev6 trước CK **61.697**; D = |ln(97.800/61.697)| = **0,46 < ln2** ⇒ không cờ. Nguồn chênh: V_ngắn bỏ qua thuế XK 10→15% (2027), CIT 5→10→20% (2030/2032), rủi ro sản lượng quặng và nút giá chuyển giao DLC mà DCF có. C4/D2: chưa tính (chỉ theo dõi). Không trộn vào tâm.
- **V8 sizing:** không đề xuất vị thế (không biên an toàn). Nếu sau này có: chuẩn 2–4% NAV bị chặn bởi thanh khoản (0,06–0,12 tỷ/phiên) ⇒ thực tế ≤0,5% NAV.
- **E15/E16:** §0.

## 4. Hạng mục skeptic r1 — truy nguồn
1. **Ô H1/26 (killer):** đã áp vào base (§1). Chiều ngược: Q2/26 (sau 17/03, VAPC còn chạy tới đầu 06) LNST% 21,2% vs Q1/26 11,0%, Q3/26 13,5% (`dd_PAT_objective_20261114/factpack/F4_history_quarterly_bq.md:73-75`) — 1 quan sát ủng hộ mức O2 nhưng có thể lẫn kho quặng DLC ⇒ hạng mục E17 chiều lên (bậc B), không vào base.
2. **Hạn thuê đất KCN:** BCTC chỉ cho: GPMB đất thuê chờ phân bổ 13,158 tỷ tại 30/09/2026, phân bổ 16 năm (Q3 TM9); chi phí hoàn nguyên đất thuê là nợ tiềm tàng không trích lập (Q3 TM31); cam kết thuê >5 năm 1,67 tỷ (TM33.3) (`F2_costs_relatedparty_legal.md:81`; `dd_PAT_20261114/assumptions_PAT.md:27`). Phân bổ ~1,63 tỷ/năm ⇒ còn ~8,1 năm ⇒ **hết phân bổ ~cuối 2034** (bản "~2042" trong `C/r5/skeptic/r1_raw.md:13` tính 16 năm từ hiện tại — sai gốc thời gian; skeptic r1 `C/skeptic/r1_raw.md:16` nêu cả 2034 lẫn 2042, chưa chọn). Kỳ phân bổ GPMB ≠ chắc chắn hạn HĐ thuê; điều khoản gia hạn KHÔNG có trong nguồn đã đọc; tra web 25/11 không tìm được HĐ thuê của PAT. ⇒ base giữ hoạt động liên tục (gia hạn = thông lệ, ước lượng); độ nhạy (D4, ô D, thả khoá 70 tỷ khi hết thuê): hết 2034 không gia hạn, không TV **43.998 trước / 39.598 sau CK (−28,7%)**; + hoàn nguyên 50 tỷ (ước lượng, blind_val) 43.237 (−29,9%); hết 2042: 54.630 (−11,5%) / 54.354. **Đây là rủi ro chiều xuống lớn nhất chưa định lượng được xác suất.**
3. **Cầm cố (đọc lại nguyên văn TM4 Q3, `F2:177-182`):** 70 tỷ BIDV bảo lãnh tiền điện (đã trừ LOCKED70 trong base); 199 tỷ BIDV và 130 tỷ ACB bảo đảm cho vay **của chính Công ty** (dư nợ PAT 30/09 = 67,2 tỷ BIDV, ACB 0) ⇒ không làm mất giá trị (tiền vẫn của PAT; nợ đã trừ trong tiền ròng) — ước "−5.200 (−7,8%)" cho ACB của skeptic r1 không có cơ sở trong văn bản. Bảo đảm chéo thật: 40 tỷ + 100.000 USD Vietinbank cho "Công ty và các công ty thành viên" ⇒ mất toàn bộ: **59.993 trước CK (−2,76%)**; xác suất không có dữ liệu (dư nợ bên được bảo đảm KHÔNG NÊU). Bán niên còn 249 tỷ BIDV cho "các đơn vị trong cùng Tập đoàn" — Q3 đổi chữ thành vay "của Công ty" (199 tỷ) ⇒ theo dõi BCTC Q4.
4. **Capex môi trường:** §3 D3.
5. **Chiều lên — tồn kho dư 44,44 tỷ:** giải phóng ⇒ 63.095 (+2,27%). **ΔVLĐ phần còn lại**, **70 tỷ theo mệnh giá** (63.501, +2,92%): độ nhạy.

## 5. Độ nhạy khác (kế thừa r5, chưa chạy lại trên rev6 trừ khi ghi)
r5 §2 (giá ×0,95/1,05 ±~37%; nút T; cốc 2.100; q_B) — cùng hướng, độ lớn tương đối giữ; xem `dd_PAT_rebuttal_20261117/C/r5/VALUATION_r5.md` §2. Chạy lại trên rev6: §2, §4.

## 6. WARNING (không bake vào base; giữ r5)
Vụ án hình sự nhóm DGC/PAT (khởi tố 03/2026, mở rộng 07/2026; Chủ tịch PAT bị khởi tố tội gây ô nhiễm môi trường 22/07/2026); tội danh điều 235 tại KCN Tằng Loỏng ⇒ "scandal di cư" sang chi phí môi trường/thuê đất của PAT (§4.2, §3 D3). Kiểm toán ngoại trừ tồn kho 31/12/2025. Bảo đảm chéo trong nhóm (§4.3). Giá chuyển giao DLC (nút T). Pháp lý chỉ WARNING.

## 7. Tâm kỳ vọng điều chỉnh (E17)
57.872 sau CK (64.302 trước CK), dải 56.700–59.045, +4,22% — `ADJ_CENTER.md` + `adj.json` (bảng hạng mục, độ nhạy C/LUẬT, bảng điều kiện đổi số).

## Phụ lục E — đính chính sau skeptic r1 (`skeptic/r1.json`, INCONCLUSIVE/medium, report_md5 f02c83e9…)
| Điểm skeptic | Xử lý | Tâm |
|---|---|---|
| Tăng trưởng 2%/năm 2028–2045 không tái đầu tư (g=0 ⇒ 56.470, −8,47%; g=1% ⇒ 58.943, −4,46% — `calc/post_skeptic_sens.py`, `calc/sens_run1.txt`) | Ghi nhận là THAM SỐ LUẬT: D4 chỉ áp cuối kỳ; V5 (user 08/11) cấm ép ROE/RONIC về Ke ở pha dự báo cho NARROW ⇒ không đổi base, báo [LUẬT] ở ADJ_CENTER. Rút lại câu "KH 45 là đệm cho capex môi trường" (không dùng đệm hai lần). | 0 |
| Ô D "đặt p(O2)=0, không nhất quán E17" | Làm rõ: ô theo D = 50/50 giữa O2 và mức chưa giải quyết (r4), không phải p(O2)=0; E17 #1 dịch thêm theo 1 quan sát Q2/26 (p 0,5) — không đếm hai lần. | 0 |
| Trách nhiệm pháp nhân Đ.235/Đ.76, đình chỉ lò | Pháp lý chỉ WARNING (SKILL; rủi ro vụ án chưa vào KQKD không vào base); độ nhạy đình chỉ 6 tháng 60.020 trước CK (−2,72%, ước lượng cơ học). Việc mở: legal-vn xác minh tình trạng pháp nhân. | 0 |
| Hạn thuê đất / capex môi trường | Không có dữ kiện mới (tra web 25/11 rỗng) ⇒ giữ C + bảng điều kiện đổi số. | 0 |
Tâm dịch 0% và không đổi lớp nhãn so với bản skeptic đã đọc ⇒ **xác nhận cơ học** (§E10); hạng mục "thiếu" chưa đóng ⇒ `skeptic_final = REFUTED_OPEN`.

## 8. Phạm vi đề nghị cho phản biện (§E4)
(1) Base ô D có đúng hướng / có quá bi quan không (Q2/26 LNST% 21,2%); (2) hạn thuê đất: suy luận "hết phân bổ GPMB ~2034" và việc giữ hoạt động liên tục trong base; (3) đọc lại cầm cố (130 ACB / 199 BIDV là vay của chính PAT); (4) D3 — đệm capex = KH 45 có đủ thay capex môi trường; (5) thiếu hạng mục; (6) kiểm bảng §2 và bắc cầu §1.
