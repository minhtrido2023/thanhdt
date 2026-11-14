# PAT — Giả định cốt lõi định giá KHÁCH QUAN, MÙ GIÁ (khoá trước khi chạy mô hình)
Người lập: người định giá độc lập stateless, 14/11/2026. Không biết và không tra giá cổ phiếu/P/E/P/B/vốn hoá/khuyến nghị.
Đơn vị: tỷ đồng (tỷ) trừ khi ghi khác. Số cổ phần: **25.000.000** (TM17 Q3/2026, ảnh png_q326/p26 — đã tự đối chiếu ảnh).

## 0. Bảng bằng chứng (#n dùng trong toàn bộ tệp)
| # | Nội dung | Nguồn |
|---|---|---|
| #1 | KQKD Q3/2026 & 9T: DT 440,032 / 1.379,304; LN gộp 63,604 / 250,598; CPBH 5,049 / 32,289; QLDN 4,711 / 12,750; LNTT 63,747 / 230,384; LNST 59,320 / 215,713 | png_q326/p07 — **tự đối chiếu ảnh** |
| #2 | BCĐKT 30/09/2026: tiền 1,246; HTM ngắn hạn 558,069; vay NH 67,218; quỹ KT-PL 76,690; VCSH 708,446; NG TSCĐ 573,214, HMLK 356,368 | png_q326/p05–p06 — **tự đối chiếu ảnh** |
| #3 | Quỹ KT-PL: trích 20,713 từ LNST 2025 (= 6,0% × 343,213); 2024 trích 13,488 / 264,941 = 5,1%; sử dụng 9T/26 6,648, năm 2025 20,722 | png_q326/p26 (TM16) — **tự đối chiếu ảnh** |
| #4 | Thuế TNDN: dự án P4 thuế suất 10% 15 năm (2018–2032), miễn 2018–2021, giảm 50% 2022–2030; ETR 9T/26 = 14,672/230,384 = 6,4% | png_q326/p30 (TM27) — **tự đối chiếu ảnh** |
| #5 | DT/GV theo thành phẩm, chi phí theo yếu tố FY25/H1/9T, CPBH chi tiết (vận chuyển, hoa hồng) | F2 §1.1, §1.3, §1.4, §1.5 (F2 đọc lại PDF gốc); tỷ lệ tính ở `calc/prelock_inputs.py` |
| #6 | Bán cho DLC 9T/26 878,140 = 63,7% DT (Q3 riêng 85,5%); 9T/25 10,8%; FY25 8,5%; mua NVL từ DLC 9T/26 627,916 ≈ 88,5% chi phí NVL | F2 §2.2 (Q3 TM30 p32 tự đối chiếu ở F4 §6) |
| #7 | DT nước ngoài 9T/26 487,508 = 35,3% DT; Q3/26 riêng 59,397 = 13,5%; FY25 90,4%; FY24 79,7% | F2 §1.2 |
| #8 | Thuế XK phospho vàng (HS 2804.70.00.10): 10% từ 01/01/2026, **15% từ 01/01/2027** (NĐ 199/2025 Phụ lục I, bản chép); thuế XNK phát sinh 9T/26 51,610 = 10,6% DT XK | F3 §2; F2 §1.5 |
| #9 | Kế hoạch 2026: DT 2.111, LNST 280, cổ tức 90% (chỉ báo PL 24/10/2026, chưa thấy nghị quyết gốc). KH vs TH: 2023 416→285 (69%); 2024 230→265 (115%); 2025 300→343 (114%) | F1 §1.1, §1.2 |
| #10 | DGC Q3/2026: khai trường 25 tạm dừng phục vụ điều tra, dùng quặng nhập/mua ngoài ⇒ giá vốn P4 cao hơn tự khai thác; GPM DGC 31,1% → 20,5% (−10,6pp) | F2 §1.6, F3 §1.6, §3.2 (Báo PL 29/10/2026) |
| #11 | VAPC: 3 nhà máy tuyển dừng từ 6/2026; Mỏ Cóc 1 (436.565 t loại III) chỉ đủ tới hết 11/2026; 3,53 tr t quặng III tồn đang xin hướng dẫn | F3 §1.1–1.2 (Báo Lào Cai 06/10, 20/10/2026) |
| #12 | PAT phản ánh thiếu nguyên liệu; tỉnh giao Sở Tài chính tham mưu "hỗ trợ giá/giảm chi phí quặng apatit" cho PAT (không thời hạn) | F3 §1.3(c) (TH&CL 06/09/2026) |
| #13 | KT25 (DGC) "chỉ có giấy phép đến hết 2026" | F3 §1.3 (VietTimes 18/03/2026 — báo chí) |
| #14 | Than cốc sunsirs (CNY/t): TB 2025 1.491; H1/26 1.541; Q3/26 2.040; T11/26 2.108; TB 20 quý 2021Q4–2026Q3 2.090 | F4 §2–3; sector read §1 |
| #15 | Giá điện bán lẻ bình quân −2% từ 01/11/2026 | F3 §4 |
| #16 | Chuỗi LNST/EBIT theo kỳ 2021Q4–2026Q3 | F4 §2–3 |
| #17 | Giải trình qua báo: Q1/26 giá bán ít biến động, giá vốn SX +14% do NVL; Q2/26 giá bán tăng; Q3/26 sản lượng giảm, NVL tăng | F1 §2 (báo chí, chưa có công văn gốc) |
| #18 | Vụ án: khởi tố 17/03/2026 (kế toán; thăm dò khai thác tài nguyên; môi trường) gồm nguyên Chủ tịch, TV HĐQT, GĐ, KTT của PAT; 23/07/2026 Chủ tịch đương nhiệm bị khởi tố (môi trường); ngoại trừ kiểm toán 2025 & soát xét BN26; BGĐ chưa ước được ảnh hưởng tài chính | F2 §3–4 |
| #19 | Tiền gửi cầm cố 30/09/2026: 70 (bảo lãnh tiền điện) + 199 BIDV + 130 ACB (vay của PAT) + 40 tỷ & 100.000 USD Vietinbank (vay của PAT **và các công ty thành viên**, dư nợ của họ không nêu) | F2 §5.1 |
| #20 | Khấu hao 9T/26 33,658; FY25 44,816. Capex 9T/26 0,115; 2025 8,06; 2024 0,83 | F2 §1.4 (KH); facts_extracted LCTT (capex, CHƯA tự đối chiếu ảnh) |
| #21 | ICL Specialty Products trả trước 12,647 tại 30/09/2026 | F2 §1.2 |
| #22 | Bobby (MÙ): P4 sunsirs 28.466 (13/11) ở p90 chế độ 2023+; F1 P(<28.466 sau 6T)=0,60, P(<24.000)=0,25; F7 P(3 nhà máy tuyển VAPC ≥80% công suất trước 31/05/2027)=0,30, P(quyết định dùng 3,53 tr t)=0,50; nguyên nhân thiếu quặng là hành chính/đất đai | sector_read §1, §3, §6 |
| #23 | Khối lượng giao dịch trung vị 60 phiên ≈ 9.300 cp/phiên (số cổ phiếu) | đề bài (số liệu độc lập cho phép) |
| #24 | Định mức than cốc 1,4–1,6 t/t P4 | sector_read §1 — **[NỀN], chưa kiểm** |

## 1. Nguồn BCTC và cơ sở kỳ
- Nguồn số trọng yếu: BCTC riêng Q3/2026 (chưa soát xét; PAT không có công ty con), BCTC bán niên 2026 soát xét UHY (ngoại trừ), BCTC 2025 kiểm toán UHY (ngoại trừ). FY2025 dùng số **kiểm toán** (LNST 343,213), không dùng số BQ trước kiểm toán (347,5).
- Kỳ định danh được: FY, H1, Q3, Q4 (Q1/Q2 riêng không tách được — F4 §3). Không dùng cột GPM/EBITM BQ như số quý (là TTM).
- Ngày định giá: 14/11/2026. Dòng tiền: Q4/2026 (phần còn lại năm) + 2027 trở đi; tiền mặt ròng lấy tại 30/09/2026.

## 2. PHÁN ĐOÁN KHẢ NĂNG SINH LỜI — build-up
Không có sản lượng (tấn) và đơn giá trong BCTC (F2 §1.6) ⇒ dựng bằng **cấu trúc chi phí theo yếu tố / doanh thu thành phẩm** (đều là số BCTC), điều chỉnh theo tỷ lệ bán/sản xuất (giá vốn TP / chi phí SX ngoài BH-QLDN). Bảng tính (#5, `calc/prelock_inputs.py`):

| Kỳ | GPM TP | NVL/DT | DV mua ngoài trừ vận chuyển/DT | Khác (nhân công SX, KH, khác)/DT |
|---|---|---|---|---|
| H1/25 | 24,9% | 46,3% | 23,1% | 5,8% |
| Q3/25 | 25,3% | 43,6% | 24,9% | 6,2% |
| Q4/25 | 19,0% | 49,9% | 24,0% | 7,1% |
| FY25 | 23,4% | 46,6% | 23,8% | 6,2% |
| H1/26 | 20,2% | 48,6% | 25,6% | 5,6% |
| Q3/26 | 14,5% | 55,2% | 24,1% | 6,2% |

### 2.1 Câu hỏi trung tâm — biên Q3/2026 sập vì sao (bằng chứng)
1. **Không phải do giá bán đơn vị sập.** DV mua ngoài (chủ yếu là điện theo nhận định ngành; thành phần không được BCTC nêu — giả định) giữ 23–26% DT ở mọi kỳ 2025–2026. Điện ∝ sản lượng và biểu giá không đổi giữa Q3/25 và Q3/26 (lần đổi kế tiếp là −2% từ 01/11/2026, #15) ⇒ doanh thu/tấn so với điện/tấn gần như không đổi (24,9% → 24,1%) ⇒ giá thực hiện/tấn Q3/26 ≈ Q3/25 (+~3%). Báo dẫn lời DN Q3: "sản lượng giảm" (#17), khớp DT TP −12,7% với giá xấp xỉ đi ngang. (Chỗ yếu: thành phần DV mua ngoài chưa xác minh; nếu DV gồm cả dịch vụ khác thì suy luận này yếu đi.)
2. **Gần như toàn bộ cú sập là NVL/DT**: GPM TP FY25 23,4% → Q3/26 14,5% (−8,9pp) trong khi NVL/DT +8,6pp, DV và "khác" ±0,3pp. NVL 88,5% mua từ DLC (#6).
3. Tách NVL tăng (FY25 → Q3/26, +8,6pp):
   - **Than cốc (CHU KỲ):** than cốc sunsirs 1.491 (TB 2025) → 2.040 (Q3/26) (#14). Ước tỷ trọng than cốc ≈ 1,5 t/t P4 (#24, NỀN) × giá cốc quy VND không VAT ≈ 7,7% DT ở giá 2025–H1/26 ⇒ đóng góp ≈ **+2,6pp** (Q3/26 so H1/26) và ≈ +3pp so FY25. Mức hiện tại 2.108 ≈ TB 20 quý 2.090 ⇒ **trung chu kỳ, không phải đỉnh**.
   - **Quặng — giai đoạn 1 (từ Q4/2025):** NVL/DT đã lên 49,9% (Q4/25) và 48,6% (H1/26) khi than cốc còn đáy (1.474; 1.541) ⇒ +2–3pp không do cốc. DN nói Q4/25 giá thành +26%, Q1/26 giá vốn SX +14% do NVL (#17). Trùng thời điểm khởi tố bị can 25/12/2025 và thắt cung quặng (#10, #11, #18). Ba kỳ liên tiếp (Q4/25, Q1/26, Q2/26) ⇒ coi là **chế độ quặng thắt có tính cấu trúc/kéo dài** (VAPC: nguồn quặng theo giấy phép khó đáp ứng nhu cầu tới 2030; chất lượng quặng giảm — F3 §1.3).
   - **Quặng — giai đoạn 2 (Q3/2026):** thêm ≈ +4pp sau khi trừ cốc. Trùng đúng sự kiện KT25 của DGC tạm dừng phục vụ điều tra, chuyển sang quặng mua ngoài/nhập (#10), và VAPC dừng tuyển từ 6/2026 (#11), PAT phản ánh thiếu quặng (#12). Tính chất: **HÀNH CHÍNH/PHÁP LÝ** (Bobby #22: nguyên nhân hành chính/đất đai, không phải cạn trữ lượng), có lời giải bằng văn bản, nhưng KT25 còn vướng giấy phép hết hạn cuối 2026 (#13) ⇒ không giải nhanh.
4. **Cơ cấu bán cho DLC (85,5% Q3) không phải nguyên nhân trực tiếp của biên thấp có bằng chứng:** giá/tấn Q3 (DLC-chi phối) ≈ giá/tấn 2025 (xuất khẩu-chi phối, sau thuế 5%) theo điểm 1; và DGC (bên có thể hưởng lợi nếu chuyển giá) cũng mất −10,6pp biên gộp cùng quý (#10) — phản bằng chứng cho giả thuyết "chuyển lợi nhuận có chọn lọc". Bán cho DLC tránh thuế XK 10% và cước/hoa hồng (CPBH Q3 chỉ 5,0 vs 20,6). ⇒ **Không giảm trừ chuyển giá trong cơ sở**; giữ làm WARNING + độ nhạy (mục 6).
5. **Chỗ KHÔNG xác định được:** (a) giá/tấn riêng kênh DLC vs XK; (b) giá NVL DLC bán cho PAT có theo thị trường không; (c) sản lượng thật. Các cách hiểu còn lại: (A) giá chuyển giao DLC thấp hơn ngang giá XK ròng thuế → tín hiệu phân biệt: tài liệu phê duyệt GD bên liên quan ĐHĐCĐ 12/05 & 14/08/2026, hoặc biên PAT không hồi khi cốc/quặng hạ; (B) NVL DLC bán cho PAT giá cao hơn thị trường → tín hiệu: NVL/DT PAT tăng mạnh hơn biên giảm của DGC/DLC. Hậu quả giá trị ở mục 6.

### 2.2 Build-up cơ sở (đã chọn)
- **Doanh thu TP cơ sở = 9T/2026 quy năm 1.366,520 × 4/3 = 1.822** (ba quý thực tế gần nhất; sản lượng ≈ 2025 vì DT TP 9T/26 ≈ 9T/25 +1% với giá ≈ đi ngang; không lấy riêng Q3 vì proxy giá/tấn từng quý quá nhiễu để ưu tiên một quý). Hàng hoá thương mại bỏ qua (biên ~1%).
- **Thuế XK 15% từ 2027 (#8):** áp lên phần XK = **35% DT** (tỷ trọng 9T/26 thực tế #7 — kỳ đã chịu thuế 10%, sau khi kênh DLC hình thành; không dùng Q3 13,5% vì 1 quý, không dùng 2025 90% vì trước khi thuế 10% đổi kênh). Doanh thu ròng thuế XK: 0,85/0,90 − 1 = −5,56% trên phần XK ⇒ **×0,9806** toàn DT ⇒ **DT cơ sở 1.787**. Chi phí/tấn không đổi ⇒ các tỷ lệ chi phí/DT ×1,0198.
- **DV mua ngoài/DT = 24,1%** (Q3/26 24,13% × 0,98 điện −2% #15 × 1,0198) — cụm Q4/25, FY25, Q3/26 = 23,8–24,1%.
- **Khác/DT = 6,3%** (Q3/26 & FY25 6,2% × 1,0198).
- **NVL/DT ngắn hạn (2027) = 56,5%**: Q3/26 55,20% + than cốc Q3 → T11 (2.040 → 2.108, +3,3% × 7,7%) +0,25pp ⇒ 55,45% × 1,0198. Lý do: chế độ quặng giai đoạn 2 chưa có ngày giải (KT25 không có ngày chạy lại #10, giấy phép hết 2026 #13; VAPC đủ quặng tới hết 11/2026 #11).
- **NVL/DT dài hạn (từ 2028) = 52,5%**: chế độ giai đoạn 1 H1/26 48,64% + than cốc H1/26 → hiện tại (1.541 → 2.108, ×1,368 trên tỷ trọng 7,7%) +2,83pp ⇒ 51,47% × 1,0198. Lý do chọn: (i) không giả định quặng về mức 2025 (giai đoạn 1 đã 3 kỳ, có tính cấu trúc); (ii) không giả định cú sốc KT25 vĩnh viễn (một quý, nguyên nhân hành chính có cơ chế giải bằng văn bản #22, DGC đã đa dạng nguồn nhập #F3 §1.4); (iii) than cốc giữ ở hiện tại vì ≈ trung bình 5 năm.
- **GPM TP:** 2027 = 1 − 0,565 − 0,241 − 0,063 = **13,1%**; 2028+ = 1 − 0,525 − 0,241 − 0,063 = **17,1%**.
- **CPBH+QLDN = 52/năm**: vận chuyển 3,85% × DT XK (FY25 66,866/1.738,334) × 35% × 1.787 = 24,1; hoa hồng 6,3 (9T/26 cả năm); khác BH 5; QLDN 17 (9T/26 12,75 quy năm) — cấu trúc theo kênh, khớp SG&A Q3 thấp (9,8) khi XK 13,5%.
- ⇒ **EBIT 2027 = 1.787 × 13,1% − 52 = 182**; **EBIT dài hạn (2028, giá 2028) = 1.787 × 17,1% − 52 = 254**, tăng danh nghĩa g từ 2029.
- Thu nhập tài chính KHÔNG tính vào lợi nhuận hoạt động (tiền ròng được cộng theo mệnh giá — tránh đếm hai lần).
- **LNST bền vững cơ sở (hoạt động, thuế 5%, trước quỹ)** = 254 × 0,95 = **241,3**; sau quỹ KT-PL 6% = 226,8. Quy về LNST "kế toán" có lãi tiền gửi (≈ 28 sau thuế 20% trên ~35 lãi/năm) ≈ **269**.

### 2.3 Ba kiểm chéo và lý do chọn
| Phương pháp | LNST kế toán/năm (gồm thu nhập TC) | Ghi chú |
|---|---|---|
| (i) Kế hoạch HĐQT 2026 (#9) | 280 | Lập trước KQ Q3; chưa có thuế 15% (2027). Bằng thực hiện 9T + Q4 ≈ Q3 |
| (ii) Run-rate: TTM 4 quý (Q4/25 kiểm toán + 9T/26) | 286,6 | 8 quý (Q4/24–Q3/26) quy năm ≈ 318 (gồm năm 2025 cốc đáy) |
| (iii) Lịch sử 2022–2026 | 963 (2022 đỉnh) / 285 / 265 / 343 / ~275–280 (2026E) | 2022 = siêu chu kỳ giá P4 |
| **Build-up cơ sở** | **2027 ≈ 200; dài hạn ≈ 269** | |
Lý do chọn build-up, không lấy trung bình: (i) và (ii) chưa phản ánh hai thay đổi đã biết có văn bản/có số: thuế XK 15% từ 01/01/2027 (#8, ≈ −34 tỷ GP/năm) và chế độ chi phí quặng sau KT25 tạm dừng (Q3/26); nhưng run-rate cũng chứa năm 2025 than cốc ở đáy chu kỳ — build-up thay bằng mức hiện tại ≈ trung bình 5 năm. Dài hạn 269 thấp hơn (ii) ≈6%, sát (i) −4%, nằm trong dải hậu-2022 (265–343). 2027 thấp hơn rõ vì giữ nguyên chế độ chi phí Q3/26 thêm một năm.

## 3. Kịch bản (xác suất khoá trước, tiêu chí gán)
| Kịch bản | Định nghĩa | Xác suất | Tiêu chí |
|---|---|---|---|
| Bất lợi | NVL/DT ở mức 2027 (56,5%) **vĩnh viễn** (quặng thắt cấu trúc + KT25 không trở lại); 2027 sản lượng −10% (thiếu quặng #11–#12; "khác" là chi phí cố định nên tăng theo tỷ lệ); từ 2028 giá thực hiện −5% (P4 TQ giảm theo Bobby F1 #22; chi phí/tấn giữ) | **0,25** | Cần đồng thời quặng không giải (1 − P(quyết định 3,53 tr t)=0,50) và giá P4 TQ giảm sâu (P(<24.000 sau 6T)=0,25) — một phần tương quan (thiếu quặng toàn ngành ít làm giá giảm) ⇒ ≈0,25 |
| Cơ sở | Như mục 2.2 | **0,50** | Phần còn lại; quặng giải từng phần (Bobby P(quyết định 3,53 tr t trước 31/05/2027) = 0,50) |
| Thuận lợi | Từ 2028 NVL/DT về FY25 46,6% + than cốc 2025→hiện tại (+3,1pp) ⇒ 49,7%; kênh DLC giữ tỷ trọng Q3 (XK 13,5% ⇒ hệ số thuế ×0,9925, chi phí ×1,0075, SG&A 38); 2027 như cơ sở nhưng XK 13,5% | **0,25** | Bobby P(VAPC ≥80% công suất trước 31/05/2027)=0,30; tỉnh có chủ trương hỗ trợ giá quặng (#12) nhưng chưa có quyết định ⇒ hạ nhẹ còn 0,25 |
**Tâm = Σ xác suất × giá trị kịch bản. Vùng = [cơ sở với NVL/DT dài hạn +2,75pp; cơ sở với NVL/DT dài hạn −2,75pp]** (2,75pp = độ lệch chuẩn NVL/DT của 4 kỳ định danh trước KT25 tạm dừng: H1/25, Q3/25, Q4/25, H1/26).

## 4. Tham số định giá
- **r (Ke nội địa) = 13,5%**: điểm neo 03/11/2026 lãi huy động hiệu dụng 12T = 7,4% (CCTG 12M; Big-4 12M 6,8%), hiện tại 7,4% ⇒ không điều chỉnh. Độ nhạy: lãi huy động ±50bp/±100bp × β 0,5/1,0.
- **g = 2,0% danh nghĩa** từ 2029 và trong terminal: sản lượng phẳng (công suất ~20.000 t, không thấy kế hoạch mở rộng — F1 §1.2; F2 §1.6); trôi giá/chi phí danh nghĩa theo lạm phát USD (P4 định giá USD/CNY); tỷ giá USD/VND 12T −2,4% (VND mạnh lên) nên không cộng trượt giá VND. Độ nhạy g 0/1/2/3%.
- **Thuế TNDN hoạt động (#4):** 5% 2026–2030; 10% 2031–2032; 20% từ 2033 (hết ưu đãi). Thu nhập tài chính không mô hình (tiền ròng tính mệnh giá).
- **Quỹ KT-PL = 6,0% LNST** (#3, 2025) — trừ khỏi FCFE.
- **Capex = khấu hao = 45/năm** (FY25 44,8 #20): duy trì công suất; capex thực 2024–9T/26 chỉ ~3/năm nhưng HMLK đã 62% nguyên giá (#2) ⇒ không thể kéo dài; giả định trạng thái dừng, không phải bi quan. ΔVLĐ = 0 (không giả định giải phóng VLĐ tăng 9T/26).
- **FCFE = EBIT × (1 − thuế) × (1 − 6%)** (capex = KH, ΔVLĐ = 0).
- **Q4/2026:** EBIT = Q3/26 53,84 ⇒ FCFE = 53,84×0,95×0,94 = 48,1, chiết khấu 0,13 năm (khớp KH LNST 2026: Q4 cần 64,3 có cả lãi tiền gửi).
- **Năm 2027 chiết khấu giữa năm (t = 0,63 năm từ 14/11/2026), các năm sau +1.** Terminal tại cuối 2033 (Gordon, g 2%, thuế 20%).
- **Tiền ròng tại 30/09/2026** = tiền 1,246 + HTM 558,069 − vay 67,218 − quỹ KT-PL 76,690 = **415,4** (#2). Tiền gửi cầm cố cho vay CỦA PAT đã được bù trừ với chính khoản vay; 70 tỷ bảo lãnh tiền điện là tài sản hoạt động, vẫn thuộc PAT.
- **V_ngắn (nền lợi nhuận, quy ước skill)** = LNST chuẩn hoá (trung vị TTM 12 quý gần nhất, BQ = 289,9) × (1 − 6% quỹ) × (1 − g/ROE)/(r − g); ROE = 289,9/VCSH bình quân (≈650) ≈ 44,6%; g/ROE trong [0; 0,8]. Không cộng tiền ròng (LNST đã gồm lãi tiền gửi). **V_dài** = DCF FCFE cơ sở. D = |ln(V_ngắn/V_dài)|.
- **Thanh khoản (mô tả riêng, không vào tâm):** 9.300 cp/phiên (#23); tham gia 5/10/20% ⇒ 465/930/1.860 cp/phiên; số phiên thoát cho 10k/50k/100k/250k cp; chiết khấu minh hoạ chỉ phần thời gian = r × (số phiên/250)/2; không có cơ sở độc lập cho tác động giá ⇒ không áp.
- **Moat:** NONE ở cấp PAT (price-taker theo giá TQ/XK; không sở hữu mỏ — 88,5% NVL từ DLC #6; ROIC cao chủ yếu vì nhà máy đã khấu hao gần 2/3 và VLĐ thấp) ⇒ không tham số moat, không thưởng/không trừ.

## 5. Khoản GIẢM TRỪ trong cơ sở (đều có bằng chứng)
| Khoản | Mức | Bằng chứng |
|---|---|---|
| Thuế XK 15% trên phần XK | DT ×0,9806 | #8, #7 |
| Chi phí quặng tăng giai đoạn 1 (giữ dài hạn) | NVL/DT +2,0pp so FY25 | #5 (Q4/25, H1/26), #17, #11 |
| Chi phí quặng giai đoạn 2 (chỉ 2027) | +4pp năm 2027 | #5 (Q3/26), #10, #11, #12, #13 |
| Than cốc về trung chu kỳ | ≈ +3pp so FY25 | #14, #24 (NỀN) |
| Quỹ KT-PL | 6% LNST; trừ 76,7 số dư khỏi tiền | #2, #3 |
| Thuế TNDN tăng 10% (2031) / 20% (2033) | theo văn bản | #4 |
| Capex duy trì = KH | 45/năm | #2, #20 |
## 5b. Khoản CỘNG trong cơ sở (đều có bằng chứng)
| Khoản | Bằng chứng |
|---|---|
| Điện −2% | #15 |
| CPBH thấp theo kênh DLC (không cước/hoa hồng) | #5 (CPBH Q3 5,0), #6 |
| Chế độ KT25 tạm dừng không vĩnh viễn (hết sau 2027) | #22 (hành chính), F3 §1.4 (nhập khẩu thay thế, nhà máy tuyển mới) |
| Tiền ròng 415,4 | #2 |

## 6. Đã CÂN NHẮC NHƯNG GỠ khỏi cơ sở (thiếu bằng chứng) — chuyển WARNING/độ nhạy
1. Chiết khấu chuyển giá bán P4 cho DLC (không có nguyên tắc giá; DGC biên giảm tương tự #10 là phản bằng chứng) ⇒ độ nhạy: giá DLC thấp hơn 5% trên phần DLC (65% DT).
2. Phạt/truy thu thuế, nghĩa vụ từ vụ án (#18: BGĐ chưa ước được; FY25 có 6,8 tỷ thuế năm trước) ⇒ độ nhạy minh hoạ −50 tỷ một lần; không xác suất.
3. Mất tiền gửi cầm cố cho công ty thành viên (40 tỷ + 100.000 USD ≈ 42,6 tỷ #19; không có dấu hiệu vỡ nợ) ⇒ độ nhạy.
4. Chi phí hoàn nguyên đất thuê chưa trích lập (không có số) ⇒ WARNING.
5. Áp dự báo giá P4 TQ giảm (Bobby) vào cơ sở: giá thực hiện PAT không theo TQ đi lên năm 2026 (điểm 2.1.1) và cao hơn TQ 2023–2025 ⇒ không có cơ chế truyền dẫn đã chứng minh ⇒ chỉ vào kịch bản bất lợi.
6. Cộng giá P4 TQ ở p90 / giá PAT theo TQ đi lên: Q3 không thấy truyền dẫn ⇒ gỡ.
7. Hỗ trợ giá quặng từ tỉnh (#12): chưa có quyết định ⇒ chỉ kịch bản thuận lợi.
8. Giải phóng vốn lưu động (VLĐ 30/09 cao hơn 31/12/2025 ~110 tỷ): không có bằng chứng sẽ đảo ⇒ gỡ.
9. Tăng sản lượng/mở rộng: không có kế hoạch ⇒ gỡ. Dự án mới: không có ⇒ NPV = 0 mặc định.
10. Phần bù moat (ROIC cao nhiều năm) ⇒ gỡ (không có cơ chế riêng của PAT; tránh đếm hai lần với biên build-up).
11. Lãi tiền gửi như lợi nhuận hoạt động ⇒ gỡ (đã tính tiền ròng theo mệnh giá).
12. Mùa vụ Q4/tác động mùa khô TQ lên giá ⇒ gỡ (không có quan hệ ổn định giá PAT ~ giá TQ, F4 §5).

## 7. Độ nhạy sẽ chạy (khoá danh sách)
r ∈ {12,5; 13,0; 13,25; 13,5; 13,75; 14,0; 14,5}% (lãi huy động ±50/±100bp × β 0,5/1,0) · g ∈ {0;1;2;3}% · EBIT dài hạn ±10%/±20% · NVL/DT dài hạn ±2,75pp · tỷ trọng chịu thuế XK 15%: 13,5% / 35% / 85% / 100% (chuyển trọn thuế qua giá DLC) · thuế XK giữ 10% (nếu hoãn) · giá thực hiện −5%/−10% (chi phí/tấn giữ) · sản lượng 2027 −20% · chuyển giá DLC −5% · một lần −50 tỷ · mất tiền gửi cầm cố 42,6 tỷ.
