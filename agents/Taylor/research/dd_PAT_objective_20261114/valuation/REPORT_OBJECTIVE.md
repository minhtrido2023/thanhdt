# PAT (CTCP Phốt pho Apatit Việt Nam): định giá khách quan, mù giá thị trường, 14/11/2026

> Văn bản do valuer Opus stateless (mù giá) soạn; Mike lưu lại nguyên nội dung (subagent không ghi được tệp báo cáo). Khoá giả định: `assumptions_objective.md` md5 `4a177526f4fd099744aff766a2b1d3e0`, 2026-11-14T16:38:21Z (`lock.txt`, 2 đính chính làm tròn/hiển thị). Mã: `calc/model.py` (md5 df86bb94…). Ký hiệu #n = bảng bằng chứng §0 của tệp giả định.

**Kết luận:** giá trị nội tại TRƯỚC chiết khấu thanh khoản **tâm ≈ 83.800 đ/cp, vùng 76.700–102.600**. Cơ sở 89.700; bất lợi 47.100; thuận lợi 108.600. Trong giá trị có **16.600 đ/cp tiền ròng** (tiền + tiền gửi giữ đến đáo hạn − vay − quỹ KT-PL 76,7 tỷ).

## 1. Phán đoán khả năng sinh lời thực

### 1.1 Biên Q3/2026 sập vì sao
Biên gộp thành phẩm (TP) giảm 23,4% (FY25) → 14,5% (Q3/26), −8,9pp; trong đó chi phí nguyên vật liệu (NVL)/doanh thu tăng +8,6pp. Dịch vụ mua ngoài (trừ vận chuyển) giữ 23–26% doanh thu mọi kỳ; nhóm "khác" (nhân công SX, khấu hao) ~6,2%. Nguồn: #5, `calc/prelock_inputs.py`.

| Nguyên nhân | Đóng góp | Tính chất | Bằng chứng |
|---|---|---|---|
| Giá bán/tấn | ≈0 (Q3/26 ≈ Q3/25, ~+3%) | — | Tỷ lệ dịch vụ mua ngoài (giả định chủ yếu điện, ∝ sản lượng) / doanh thu không đổi; biểu giá điện không đổi giữa 2 kỳ (#15). DN nói "sản lượng giảm" (#17) |
| Than cốc | ≈+2,6pp so H1/26; ≈+3pp so FY25 | Chu kỳ. Giá 2.108 ≈ TB 5 năm 2.090 (trung chu kỳ) | #14; định mức cốc là kiến thức nền #24 |
| Quặng GĐ1 (từ Q4/25) | +2–3pp | Kéo dài/cấu trúc: 3 kỳ khi cốc còn đáy; VAPC nói khó đáp ứng nhu cầu quặng tới 2030 | #5, #17, F3 §1.3 |
| Quặng GĐ2 (Q3/26) | ≈+4pp | Hành chính/pháp lý: KT25 tạm dừng vì điều tra → quặng mua ngoài; VAPC dừng tuyển từ T6/2026 | #10, #11, #12; giấy phép KT25 hết hạn cuối 2026 (#13) |
| Bán cho DLC (85,5% DT Q3) | Không chứng minh là nguyên nhân | Kênh DLC tránh thuế XK + tiết kiệm cước | Mẹ DGC cũng mất −10,6pp biên gộp cùng quý (#10) — phản bằng chứng cho giả thuyết chuyển lợi nhuận chọn lọc |

**Chưa xác định:** giá/tấn riêng kênh DLC vs xuất khẩu; giá NVL DLC bán cho PAT; sản lượng thật. Hai cách hiểu còn mở:
- (A) Giá chuyển giao bán DLC thấp hơn ngang giá xuất khẩu trừ thuế: nếu thấp hơn 5% trên phần DLC ⇒ cơ sở **73.000** (−16.700).
- (B) DLC bán NVL cho PAT cao hơn giá thị trường: nằm sẵn trong độ nhạy NVL/DT ±2,75pp ⇒ **76.700–102.600**.
Tín hiệu phân biệt: tài liệu phê duyệt giao dịch bên liên quan ĐHĐCĐ 12/05 và 14/08/2026; biên PAT có hồi khi giá cốc/quặng hạ hay không.

### 1.2 Lợi nhuận bền vững (build-up)
- Doanh thu cơ sở: DT TP 9T/26 quy năm 1.822 tỷ (sản lượng ≈2025, giá đi ngang), trừ thuế XK 15% trên 35% DT xuất khẩu (tỷ trọng 9T/26) ⇒ **1.787 tỷ**.
- Biên gộp TP: 2027 giữ chế độ chi phí Q3/26 (NVL 56,5%, dịch vụ mua ngoài 24,1%, khác 6,3%) ⇒ **13,0%**; từ 2028 về chế độ quặng GĐ1 + cốc hiện tại (NVL 52,5%) ⇒ **17,1%**.
- SG&A theo kênh bán: 52 tỷ/năm. **EBIT 2027 = 180 tỷ; dài hạn = 253 tỷ** (giá 2028, sau đó +2%/năm danh nghĩa).
- LNST hoạt động (thuế ưu đãi 5%): 2027 = 171, dài hạn = **240**; cộng lãi tiền gửi (~28 sau thuế) ⇒ LNST kế toán 2027 ≈ 199, dài hạn ≈ **268**. Sau trích quỹ KT-PL 6% ⇒ phần cổ đông từ hoạt động ≈ 226.

### 1.3 Ba kiểm chéo (LNST kế toán, tỷ/năm)
| Cách | Số | So với build-up dài hạn (268) |
|---|---|---|
| Kế hoạch HĐQT 2026 (#9, chỉ 1 nguồn báo) | 280 | −4% |
| TTM 4 quý (Q4/25 kiểm toán + 9T/26) | 287 | −7% |
| Bình quân năm 8 quý gần nhất | ~318 | gồm 2025 khi cốc ở đáy chu kỳ |
| Lịch sử 2023/2024/2025 | 285 / 265 / 343 | trong dải |

Vì sao chọn build-up: kế hoạch HĐQT và run-rate chưa tính hai thay đổi đã có văn bản/số: (i) thuế XK 15% từ 01/01/2027 (≈−34 tỷ lợi nhuận gộp/năm); (ii) chế độ chi phí quặng sau KT25 tạm dừng. Run-rate còn chứa cốc ở đáy chu kỳ; build-up thay bằng cốc trung chu kỳ. Build-up KHÔNG đẩy quặng về mức 2025 (GĐ1 đã kéo 3 kỳ) và KHÔNG coi cú sốc KT25 vĩnh viễn (mới 1 quý, nguyên nhân hành chính). Ba cách lệch <10% ở mức dài hạn; phần chênh nằm gọn ở hai khoản đã biết.

## 2. V_ngắn và V_dài
| Nền | đ/cp | Cách tính |
|---|---|---|
| V_ngắn | 90.500 | LNST chuẩn hoá (trung vị TTM 12 quý) 289,9 × 0,94 (trừ quỹ) × (1−g/ROE 0,045)/(r−g) |
| V_dài (FCFE cơ sở) | 89.700 | gồm 415,4 tỷ tiền ròng; terminal 36% |
D = 0,01, không cờ phân kỳ. Lưu ý: V_ngắn dùng lợi nhuận lịch sử (chưa thuế XK 15% và chi phí quặng Q3), V_dài có tiền ròng cộng riêng; hai nền gần nhau do bù trừ, KHÔNG phải bằng chứng độc lập cho nhau.

## 3. Kịch bản
| Kịch bản | XS | EBIT 2027/dài hạn | đ/cp | Định nghĩa + tiêu chí xác suất |
|---|---|---|---|---|
| Bất lợi | 0,25 | 148/92 | 47.100 | Quặng thắt vĩnh viễn mức Q3 (NVL 56,5%); SL 2027 −10%; giá thực hiện −5% từ 2028. Cần đồng thời: chưa có quyết định quặng tồn (Bobby P=0,50) và giá P4 TQ giảm sâu (P(<24.000)=0,25), tương quan một phần |
| Cơ sở | 0,50 | 180/253 | 89.700 | §1.2 |
| Thuận lợi | 0,25 | 217/321 | 108.600 | Từ 2028 quặng về mức 2025 (NVL 49,7%); kênh DLC giữ tỷ trọng Q3 (xuất khẩu 13,5%). Neo Bobby P(VAPC ≥80% công suất trước 31/05/2027)=0,30; tỉnh có chủ trương hỗ trợ giá quặng chưa ban hành |
| **Tâm** | — | — | **83.800** | bình quân có trọng số; vùng = cơ sở ± 1 độ lệch chuẩn NVL/DT (2,75pp): 76.700–102.600 |

## 4. Độ nhạy (đ/cp)
r theo lãi huy động (neo r=13,5% @7,4%); ô = cơ sở / tâm:
| Lãi huy động | β=0,5 | β=1,0 |
|---|---|---|
| −100bp | 92.700/86.500 | 96.000/89.500 |
| −50bp | 91.100/85.100 | 92.700/86.500 |
| +50bp | 88.200/82.500 | 86.900/81.200 |
| +100bp | 86.900/81.200 | 84.300/78.900 |

g: 0% 80.500/75.400 · 1% 84.700/79.300 · 2% 89.700/83.800 · 3% 95.500/89.100.
Lưới r×g (cơ sở): r12,5%: 85.100/96.000/103.100 (g 0/2/3%); r13,5%: 80.500/89.700/95.500; r14,5%: 76.500/84.300/89.200.
LNST bền vững (EBIT dài hạn ×): 0,8→76.600; 0,9→83.100; 1,1→96.200; 1,2→102.700.
Thuế XK (tỷ trọng DT chịu 15%): 13,5%→100.300; 35% (cơ sở)→89.700; 85%→65.400; 100% (DLC chuyển trọn thuế)→58.200; thuế giữ 10%→99.800.
**Đòn bẩy giá rất lớn** (biên gộp ~17%): giá thực hiện −5%→64.000; −10%→38.300.
Khác: SL 2027 −20%→87.500; giá chuyển giao DLC −5%→73.000; lỗ một lần −50 tỷ→87.700; mất 42,6 tỷ tiền gửi cầm cố→88.000.

## 5. Bảng giảm trừ / cộng thêm
| Khoản | Trong cơ sở? | Bằng chứng |
|---|---|---|
| Thuế XK 15% trên phần xuất khẩu | Có (−) | #8, #7 |
| Chi phí quặng GĐ1 kéo dài | Có (−) | #5, #17, #11 |
| Chi phí quặng GĐ2 chỉ năm 2027 | Có (−) | #10–#13 |
| Cốc trung chu kỳ | Có (−) | #14, #24 (kiến thức nền) |
| Quỹ KT-PL 6% LNST + trừ số dư 76,7 tỷ | Có (−) | #2, #3 |
| Thuế TNDN lên 10% (2031), 20% (2033) | Có (−) | #4 |
| Capex duy trì = khấu hao (45 tỷ) | Có (−) | #2, #20 |
| Giá điện −2% | Có (+) | #15 |
| SG&A thấp nhờ kênh DLC | Có (+) | #5, #6 |
| Cú sốc KT25 không vĩnh viễn | Có (+) | #22, F3 §1.4 |
| Tiền ròng 415,4 tỷ | Có (+) | #2 |
| Chiết khấu chuyển giá DLC; phạt/truy thu vụ án; mất tiền gửi cầm cố; hoàn nguyên đất | **GỠ** (độ nhạy/WARNING) | thiếu số hoặc có phản bằng chứng |
| Dự báo giá P4 TQ giảm; giá P4 TQ p90 kéo giá PAT lên | **GỠ** | không chứng minh truyền dẫn giá TQ→PAT |
| Hỗ trợ giá quặng; giải phóng vốn lưu động; mở rộng sản lượng; phần bù moat; lãi tiền gửi như lợi nhuận hoạt động | **GỠ** | chưa có quyết định/số, hoặc đếm hai lần |

## 6. Moat 5F
moat_tier = NONE (PAT nhận giá theo giá TQ/xuất khẩu; không sở hữu mỏ: 88,5% NVL mua từ DLC (#6); công suất ~20.000 t (báo); ROIC cao chủ yếu do nhà máy đã khấu hao 62% + vốn lưu động thấp). Rủi ro số 1: quyền tiếp cận quặng phụ thuộc công ty mẹ + lực thứ 6 (giấy phép KT25 hết hạn, thuế XK tăng, ưu đãi thuế hết 2032). Mô hình không dùng tham số moat (không thưởng, không trừ). Chưa tra `data/moat_tags.csv`.

## 7. WARNING pháp lý (không vào cơ sở)
- Vụ án (#18): 17/03/2026 khởi tố các tội kế toán, thăm dò khai thác tài nguyên, gây ô nhiễm môi trường tại nhóm DGC; bị can gồm nguyên Chủ tịch, thành viên HĐQT, Giám đốc, Kế toán trưởng PAT; 23/07/2026 Chủ tịch PAT đương nhiệm khi đó bị khởi tố tội gây ô nhiễm môi trường. Kiểm toán 2025 + soát xét bán niên 2026 có ý kiến ngoại trừ; đổi PwC→UHY; hạn chế giao dịch 01/06–24/08/2026.
- Tác động ĐÃ BIẾT lên hoạt động: thay toàn bộ lãnh đạo; chậm nộp BCTC; KT25 của mẹ tạm dừng (đã phản ánh vào chi phí quặng 2027). Chưa thấy công bố phong toả tài sản/hợp đồng/sản xuất của chính PAT; BGĐ "chưa đủ cơ sở" ước ảnh hưởng tài chính.
- Rủi ro "di cư" sang PAT: PAT ở KCN Tằng Loỏng (nơi cơ quan điều tra mô tả hành vi đổ thải); tín hiệu: quyết định xử phạt/truy thu/đình chỉ đích danh PAT.
- Tiền gửi cầm cố cho "các công ty thành viên" (40 tỷ + 100.000 USD tại Vietinbank, #19); dư nợ bên được bảo đảm không công bố.

## 8. Điều có thể bị bỏ sót
1. Tiền ròng 16.600 đ/cp (đã trừ quỹ KT-PL).
2. Kênh DLC khiến thuế XK 15% chỉ chạm ~35% DT; mỗi 10pp tỷ trọng XK chuyển sang DLC ≈ +2.000 đ/cp.
3. Cú sốc chi phí Q3 do hai nguyên nhân hành chính/chu kỳ, không do giá bán sập.
4. Theo hướng xấu: thuế XK 15% ngay 01/01/2027; ưu đãi thuế hết (5%→20% vào 2033); đòn bẩy giá (−5% giá ⇒ −29% giá trị).

## 9. Thanh khoản (mô tả riêng, không trừ vào tâm)
Khối lượng trung vị 9.300 cp/phiên (#23); free float tối đa 49%, nhóm cổ đông nhỏ thực tế 32,3%.
| Tham gia | cp/phiên | Số phiên thoát 10k/50k/100k/250k cp | Chiết khấu minh hoạ (r/2 × thời gian) |
|---|---|---|---|
| 5% | 465 | 22/108/215/538 | 0,6%/2,9%/5,8%/14,5% |
| 10% | 930 | 11/54/108/269 | 0,3%/1,5%/2,9%/7,3% |
| 20% | 1.860 | 5/27/54/134 | 0,1%/0,7%/1,5%/3,6% |
Không có cơ sở độc lập ước tác động giá khi bán ⇒ không áp vào định giá. Tiền lệ: từng chỉ giao dịch phiên thứ Sáu 01/06–24/08/2026.

## 10. Điều gì làm đổi ý (hai chiều)
| Mốc | Nâng | Hạ |
|---|---|---|
| BCTC Q4/2026 (~cuối 01/2027) | NVL/DT ≤50%, biên gộp TP ≥18% | NVL/DT ≥55% thêm 1 quý; dịch vụ mua ngoài/DT >26% (dấu hiệu giá/tấn giảm) |
| Văn bản thuế / tờ khai 01/2027 | Thuế XK 15% hoãn/giảm (+10.000) | DLC chuyển trọn thuế (tới 58.000) |
| ĐHĐCĐ 2027 | KH LNST ≥270 + công bố nguyên tắc giá với DLC | KH <200; không công bố nguyên tắc giá |
| BCTC Q1/2027 | Tỷ trọng XK <20% và biên giữ | Tỷ trọng XK >60% dưới thuế 15% |
| Giấy phép KT25 (01/2027); quặng tồn 3,53 tr t (Bobby F7, 31/05/2027) | Gia hạn hoặc có quyết định dùng quặng tồn | Không gia hạn + không quyết định ⇒ kịch bản bất lợi |
| Giá P4 TQ (Bobby F1, 14/05/2027) | — | <24.000 và giá thực hiện PAT đi theo |
| Tố tụng | Kết luận không đích danh PAT | Xử phạt/truy thu/đình chỉ đích danh PAT; ngân hàng xử lý tiền gửi cầm cố |

## 11. Số liệu cần đối chiếu bản gốc
1. Kế hoạch 2026 (LNST 280 tỷ, cổ tức 90%): chỉ có báo PL 24/10/2026, chưa thấy NQ 02/2026/NQ-ĐHCĐ.
2. Thành phần "dịch vụ mua ngoài" (giả định chủ yếu điện; BCTC không nêu) — toàn bộ suy luận "giá/tấn đi ngang" dựa vào đây.
3. Sản lượng P4 bán ra 2024–2026 (tấn) và giá/tấn theo kênh.
4. Nguyên tắc giá mua/bán với DLC (tờ trình GD bên liên quan ĐHĐCĐ 12/05 và 14/08/2026).
5. Định mức than cốc của PAT (đang dùng kiến thức nền 1,4–1,6 t/t) và nguồn mua cốc.
6. Capex 2024–9T/26 (từ facts_extracted, chưa tự đối chiếu ảnh LCTT).
7. Văn bản gốc NĐ 199/2025 Phụ lục I (đang dùng bản chép) và thuế ưu đãi FTA cho P4.
8. Giấy phép KT25 hết hạn cuối 2026 (nguồn báo chí).
9. Dư nợ "các công ty thành viên" được bảo đảm bằng tiền gửi của PAT.
10. Chênh LNST 2025 trước/sau kiểm toán (347,5 → 343,2) và 6,8 tỷ thuế truy thu các năm trước.
