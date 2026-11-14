# DD — PAT (CTCP Phốt pho Apatit Việt Nam, UPCoM) · 2026-11-14 · rev2 · job `Taylor_20261114_122249` (rev1: `Taylor_20261114_120425`, lưu `rev1/`)

> **REV2 — áp đính chính fundamental-skeptic** (REFUTED ở mức mô hình/văn bản; số BCTC trích tay KHỚP ảnh gốc, giữ nguyên). Đổi: (1) FCFE trừ trích quỹ KTPL 5,5% LNST; (2) EBT cơ sở 245 → **202,6** (run-rate Q3 trừ bước thuế XK); (3) thêm TM4 cầm cố Vietinbank cho nợ nhóm; (4) mốc M1 hai nhánh kích hoạt được; (5)–(10) quy đổi, facts, §9b, đối chiếu 31/07, cổ tức, "mù giá". **Tâm rev1 75.100 → rev2 66.600.** Cơ sở rev2 chọn theo dữ liệu quý 2026, **TRƯỚC khi so với giá 72.700**; không sửa ngược theo giá.

> **ĐÍNH CHÍNH GIÁ THAM CHIẾU (Mike, 14/11 sau khi Taylor phát hiện):** Giá đóng cửa 13/11/2026 = 71.000 (BQ tav2_bq.ticker); 72.700 là đóng cửa 06/11. Brief ban đầu ghi nhầm 72.700 (truy vấn ANY_VALUE lấy sai ngày). Đối chiếu đúng: giá 71.000 cao hơn tâm 66.600 là 6,6%, cách cận trên 76.600 là 7,3%; vẫn TRONG vùng hợp lý. Mô hình/giả định KHÔNG đổi (định giá không dùng giá).

> Đây là NGHIÊN CỨU read-only, không phải khuyến nghị mua. User quyết. Không đặt lệnh, không wire, không ghi `dd_price_zones.json` (Mike làm sau skeptic).
> **Nguồn số:**
> - **[Q3]**: BCTC RIÊNG Q3/2026, duyệt 20/10/2026, bản scan có chữ ký số. PAT không có công ty con nên không có hợp nhất.
> - **[BN26]**: BCTC bán niên 2026, UHY soát xét, kết luận ngoại trừ.
> - **[KT25]**: BCTC 2025, UHY kiểm toán, ý kiến ngoại trừ.
> - Ba file trên tải từ CDN cafef, lưu ở `src/`. Số đọc tay ghi trong `facts_extracted.md`.
> - **[BQ]**: `tav2_bq.ticker_financial` (NP/DT quý), `ticker` (ADV), `commodity_prices` (sunsirs).
> - **[EY]**: EY Customs Update 07/2025, bản tóm tắt NĐ 199/2025, lưu tại `src/EY_customs_update_jul2025_ND199.pdf`.
> - **[Bobby]**: `kb/data_registry/market-state/sector_read_phot_pho_20261114.md`, đọc mù.
> - Báo chí ghi rõ ngay cạnh số. Giả định khoá ở `assumptions_PAT.md`, khoá TRƯỚC khi tính giá trị. Mô hình: `calc/model_PAT.py` → `calc/valuation_PAT.csv`.
> - Đơn vị tỷ đồng, trừ khi ghi khác. Số không đo được gắn **(ước lượng)**.
> ⚠️ **Định giá MÙ MỘT PHẦN.** Brief có giá 13/11 (72.700). Cột PE (6,2) hiện ra lúc truy vấn BQ lịch sử NP. Giả định được khoá MỘT lần (`assumptions_PAT.md`) trước khi chạy mô hình rev1; rev2 chỉ sửa theo đính chính của skeptic dựa trên dữ liệu quý 2026. Skeptic đã kiểm và không thấy dấu hiệu hiệu chỉnh theo giá; hai lỗi của rev1 (thiếu quỹ KTPL, EBT 245) đều đẩy giá trị LÊN, tức không theo hướng gần giá thị trường.

## 0. Kết luận

**PAT là cỗ máy tiền mặt đơn sản phẩm (P4 thô, công suất 20 kt/năm), phụ thuộc gần như hoàn toàn vào công ty mẹ ở CẢ hai đầu.**
- **Đầu vào:** năm 2025 mua 749,9 tỷ nguyên vật liệu từ DLC [KT25].
- **Đầu ra:** 9T/2026 bán 878,1 tỷ cho DLC, bằng **63,7% doanh thu**. Riêng Q3 là **85,5%** [Q3, BN26].
- **Giá trị nội tại có trọng số: 74.000 đ/cp** trước chiết khấu thanh khoản. Sau chiết khấu thanh khoản 10%: **66.600 đ/cp**, đây là **tâm** (rev1: 75.100).
- **Vùng:** "rẻ" ≤ **56.600** (0,85 × tâm). Hợp lý 56.600–76.600. "Đắt" ≥ 76.600 (1,15 × tâm).
- **Đối chiếu SAU KHI có giá trị:** giá 71.000 (13/11) **cao hơn tâm 6,6%**, nằm trong vùng hợp lý, sát cận trên (cách "đắt" 7,3%). **Không có biên an toàn; không đủ điều kiện luật 02/11 #4 (cần giá < 0,85 × tâm = 56.600).**

| Câu hỏi | Trả lời ngắn | Bằng chứng |
|---|---|---|
| Vì sao LNST Q3 giảm 46% YoY, 46% QoQ? | Biên gộp sập từ 25,7% (Q3/25) và 25,0% (Q2/26) xuống **14,5%**, dù giá P4 TQ cao hơn cùng kỳ 22%. Giải thích hợp lý nhất (CHƯA có số sản lượng): **sản lượng thấp do thiếu quặng**, chi phí cố định dàn trên ít tấn hơn, cộng với than cốc +52% YoY. Rủi ro song song: **giá chuyển nhượng với DLC**. Không có khoản một lần | §2 |
| Q1 CFO âm 408 tỷ vì sao? | PAT trả nợ thương mại cho mẹ: phải trả DLC giảm từ 313,3 xuống 16,5 tỷ trong 9T. Đây không phải lỗ vốn lưu động mà là **DLC thu lại khoản tín dụng thương mại** đã cấp cuối 2025 | §3 |
| Net cash thật | **415,4 tỷ (16.600 đ/cp)** = tiền + HTM − vay − quỹ KTPL. 439 tỷ HTM đang cầm cố | §3 |
| Cổ tức | Trả tiền mặt rất cao: 425 tỷ chi năm 2024, 322,5 tỷ chi 9T26. Kế hoạch 2026 là 90%, tức 9.000 đ/cp (ước lượng theo KH ĐHCĐ, báo PL 24/10). Duy trì được ở mức LN ~280 vì capex gần 0. Kế hoạch 90% **chỉ có báo PL 24/10, chưa xác nhận nghị quyết** (§4) | §4 |
| Ý kiến kiểm toán | NGOẠI TRỪ cả BCTC 2025 và bán niên 2026: không chứng kiến kiểm kê HTK 67,7 tỷ, và vụ khởi tố về **vi phạm kế toán**. Đổi kiểm toán PwC sang UHY, BCKT phát hành trễ tới 20/06/2026 | §7 |
| Moat | **NARROW** (CAPTIVE_SUPPLY/PERMIT), có đồng hồ cắt hào ⇒ không thưởng, không trừ | §6 |

## 1. Kiểm lại số Mike đưa

Kết quả: **khớp**, chỉ lệch Q4/25.

| Chỉ tiêu | Mike / BQ | BCTC gốc | Kết luận |
|---|---|---|---|
| Q3/26 DT / LNST | 440,0 / 59,3 | 440,03 / 59,32 [Q3] | ✅ |
| Q2/26 DT / LNST | 517,4 / 109,8 | 9T − Q3 − Q1 ⇒ LNST 109,84 | ✅ |
| Q1/26 DT / LNST | 421,9 / 46,6 | 421,92 / 46,56 (báo PL 28/04, trích BCTC Q1) | ✅ |
| Q4/25 LNST | 75,2 (BQ) | **70,89** = năm KT 343,21 − 9T 272,33 [KT25, Q3] | ⚠️ Lệch 4,3 tỷ (BQ dùng số Q4 trước kiểm toán). Mô hình dùng 70,89 |
| 9T LNST | ~216 | 215,71 | ✅ 77% KH 280 tỷ |
| Q3/25 LNST | 110 | 109,97 | ✅ |
| Q1 CFO | âm >400 | −408,27 (báo PL, BCTC Q1). 9T CFO **+128,22** [Q3] | ✅ |

Lỗi nhỏ trong BCTC: tiền trên BCĐKT **1,246** tỷ, nhưng thuyết minh 3 ghi **1,286** tỷ, lệch 0,04 tỷ. Không trọng yếu, nhưng đáng ghi lại.

## 2. Chất lượng lợi nhuận — tách Q3 với Q2 và cùng kỳ

| | Q3/25 | Q1/26 | Q2/26 | Q3/26 | 9T25 | 9T26 |
|---|---|---|---|---|---|---|
| DT | 506,7 | 421,9 | 517,4 | 440,0 | 1.420,8 | 1.379,3 |
| LN gộp | 130,5 | 57,6 | 129,4 (suy) | 63,6 | 347,1 | 250,6 |
| GPM | 25,7% | 13,6% | 25,0% | **14,5%** | 24,4% | 18,2% |
| CPBH+QLDN | 24,7 | 17,5 | — | 9,8 | 76,0 | 45,0 |
| TC ròng | +10,5 | — | — | +9,9 | +25,2 | +24,8 |
| LNST | 110,0 | 46,6 | 109,8 | 59,3 | 272,3 | 215,7 |
| P4 TQ TB quý (CNY/t, sunsirs) [BQ] | 22.592 | 24.514 | 31.105 | 27.606 | | |
| Than cốc TQ (CNY/t) [BQ] | 1.341 | 1.412 | 1.661 | 2.040 | | |

**Nguồn:** Q1 lấy từ báo PL 28/04/2026, trích BCTC Q1 (`src/PAT_Q1_2026.pdf` chưa render). Q2 suy ra = 9T − Q1 − Q3.

**Đọc bảng:**
1. **Biên KHÔNG đi theo giá P4 TQ.** Q3/26 P4 +22% YoY nhưng GPM giảm một nửa. Q1/26 P4 +4% nhưng GPM 13,6%, và ban lãnh đạo giải trình Q1 là "giá bán ổn định, giá vốn +14% do NVL tăng" (báo PL 28/04). DT Q3 −13% trong khi giá TQ +22% ⇒ **sản lượng tiêu thụ Q3 có thể giảm ~25–30%** (ước lượng, suy ngược, CHƯA có tấn).
2. **Bằng chứng cấu phần chi phí** [Q3 TM28, 9T]: NVL **709,3** (9T25 595,6, +19%), trong khi DT −3%. DV mua ngoài (chủ yếu điện, ước lượng) 373,2 (+3%). Nhân công 65,2. KH 33,7. Chi phí NVL trên mỗi đồng doanh thu tăng từ 0,42 lên **0,51**, tức quặng/than cốc đắt hơn hoặc giá bán thấp hơn.
3. **Giải thích hợp lý nhất (giả thuyết, cần sản lượng tấn để chốt):**
   - (a) Thiếu quặng toàn ngành từ T6/2026 [Bobby §3] ⇒ lò chạy non tải ⇒ định phí dàn trên ít tấn.
   - (b) Than cốc +52% YoY trong Q3 [BQ].
   - (c) **Giá chuyển nhượng**: 85,5% DT Q3 bán cho DLC, đồng thời mua 248 tỷ NVL từ DLC trong Q3. Biên của PAT do bên chi phối quyết định ở cả hai đầu (§7).
4. **CP bán hàng giảm 54%** (vận chuyển 49,6 → 22,8 trong 9T). Khớp với việc chuyển từ XK (9T25: 1.183 tỷ) sang bán nội địa cho DLC (9T26 XK chỉ còn 487,5 tỷ).
   - Thuế XK đã nộp 9T26 là **51,6 tỷ**, bằng 10,6% DT XK, khớp thuế suất 10% năm 2026.
   - Bán cho DLC thì PAT tránh được thuế XK. Nhưng việc phần lợi ích này có đến được cổ đông PAT hay không phụ thuộc vào giá DLC trả.
5. **Thu nhập tài chính:** lãi tiền gửi 25,1 tỷ (9T) trên số dư ~550–820 tỷ ⇒ ~4–5%/năm. Đây là phần bền khi còn giữ tiền. Lãi tỷ giá giảm 20,2 → 7,2 do bớt XK. **Không có khoản một lần**: LN khác ≈ 0.
6. **Thuế TNDN thấp có thời hạn:** ưu đãi 10% trong 15 năm (2018–2032), giảm 50% giai đoạn 2022–2030 ⇒ ETR 9T26 **6,4%**. Từ 2031 lên 10%, từ 2033 lên 20% [Q3 TM27]. Đây là một phần lý do LN đang cao, và phần này sẽ mất dần.

## 3. Bảng cân đối & dòng tiền thật (30/09/2026) [Q3]

- **Tiền + HTM** = 1,25 + 558,07 = 559,3. **Vay NH** 67,2 (lãi 4–4,5%, USD/VND).
  - Vay được bảo lãnh bởi DGC và DLC, mỗi bên tối đa 400 tỷ, kèm HĐ tiền gửi 1,51 tr USD **của DLC** ⇒ PAT phụ thuộc mẹ cả về tín dụng.
  - Quỹ KTPL 76,7 (nghĩa vụ tiền mặt với người lao động).
  - ⇒ **Net cash thật 415,4 tỷ = 16.616 đ/cp**.
  - HTM cầm cố: 70 tỷ bảo lãnh thanh toán tiền điện, 199 + 130 tỷ đảm bảo vay, 40 tỷ + 100k USD ở Vietinbank.
  - **[rev2] TM4 Q3 (png_q326/p20, đoạn cuối):** tiền gửi 40 tỷ (6 tháng) + 100.000 USD (5 tháng) tại Vietinbank CN Hà Nội thế chấp cho khoản vay "của Công ty **và các công ty thành viên**" ⇒ **~42,6 tỷ ≈ 1.700 đ/cp** (100k USD ≈ 2,6 tỷ, ước lượng) của PAT bảo đảm cho nợ nhóm DGC, đúng lúc DGC bị điều tra. BCTC không nêu dư nợ các công ty thành viên tại Vietinbank ⇒ **cần kiểm**. Base KHÔNG trừ (thiếu cơ sở); độ nhạy: net cash −42,6 tỷ ⇒ tâm **65.100** (−1.500).
- **CFO 9T26 +128,2** = LN trước thay đổi VLĐ 243,4, cộng thu phải thu +249,4 (khách XK ICL/KS International trả hết), trừ tăng tồn kho 52,5, **trừ trả nhà cung cấp −292,7**.
  - Phải trả DLC giảm 313,3 → 16,5. **Q1 âm 408 tỷ là do PAT trả mẹ khoản nợ thương mại** tích luỹ trong 2025. Phải trả DLC đầu năm 2025 là 161,6.
  - Khả năng cao (suy luận): DLC cần tiền trong lúc vụ án/hạn chế giao dịch, nên rút lại tín dụng nhà cung cấp.
  - Không có dấu hiệu ứng trước cho bên liên quan: phải thu DLC = 0, trả trước người bán 2,45.
- **CFO 3 năm:** 2024 **464,0**, 2025 **370,8**, TTM **284,6**, trung bình 373,1. Capex 0,8 / 8,1 / 0,4 tỷ — **dưới mức khấu hao 45 tỷ/năm**.
  - TSCĐ nguyên giá 573, đã khấu hao 62%, còn lại 216,8. Lò đã chạy từ 2018, sớm muộn cần chi đại tu.
  - Mô hình đặt capex = khấu hao (bảo thủ hơn lịch sử).
- **Vốn lưu động hiện mỏng** (~53 tỷ). Nếu DLC lại cấp tín dụng 300 tỷ như cuối 2025, tiền sẽ phồng lên tạm thời. **Không** tính phần này vào giá trị.

## 4. Cổ tức — "vua cổ tức" có bền không

- **Lịch sử:** 2022 >300%, 2023 100%, 2024 95%, tạm ứng 2025 100% (viettimes). Ghi nhận phân phối 2025 là 312,5 tỷ cộng 72,5 tỷ năm 2026 [Q3 TM18].
- **Tiền mặt thực chi:** 2024 **425** tỷ, 2025 62,5 tỷ, 9T26 **322,5** tỷ [LCTT].
- **Kế hoạch 2026:** 90% (9.000 đ/cp, khoảng 225 tỷ) — **chỉ báo PL 24/10/2026, chưa xác nhận nghị quyết.** Q3 TM chỉ ghi NQ 18/2026/NQ-PAT 04/09/2026 chi 72,5 tỷ (phần còn lại cổ tức 2025); tìm web 14/11 không thấy nghị quyết ĐHCĐ 14/08/2026 hay CBTT HNX nêu 90% cho 2026. Chỉ dùng hiển thị lợi suất, **không vào mô hình**.
- **Bền vững:** FCFE thường xuyên ≈ LNST × 94,5% (capex ~0, vốn lưu động mỏng; trừ trích quỹ KTPL) ⇒ trả 80–100% LN là khả thi.
  - Trần thực tế là **LN ~250–300 tỷ/năm** ⇒ 10.000–12.000 đ/cp/năm nếu chi 100% (ước lượng).
  - Rủi ro: thuế TNDN tăng (2031, 2033), thuế XK 15% (2027), đại tu lò.
  - Dòng cổ tức chảy 51% về DLC và 16,7% về gia đình ông Đào Hữu Huyền ⇒ cổ đông chi phối có động cơ giữ tỷ lệ chi cao. Đây là điểm cộng cho cổ đông nhỏ, đối trọng với rủi ro giá chuyển nhượng.

## 5. Ngành — 10 mục "DD cần kiểm gì" của Bobby, trả lời bằng số

Bobby phân loại ADMIN_GATED 0,45 / CYCLICAL 0,40 / STRUCTURAL 0,15.

| # | Câu hỏi | PAT (số BCTC) | Trạng thái |
|---|---|---|---|
| 1 | Quặng tự khai thác vs mua ngoài; giấy phép mỏ | **0% tự khai thác.** PAT không có tài sản quyền khai thác mỏ (TSCĐ vô hình = 0; TSCĐ chỉ gồm nhà xưởng/máy/xe) [Q3 TM8]. NVL mua từ DLC: 749,9 tỷ (2025), 627,9 tỷ (9T26). Mỏ (Khai trường 25) thuộc DGC Chi nhánh Lào Cai (viettimes). Hạn giấy phép mỏ: **cần kiểm** (không thuộc PAT) | ❌ phụ thuộc mẹ 100% |
| 2 | Hệ số sử dụng lò theo quý 2026 | BCTC không công bố tấn. Suy ngược **(ước lượng)**: DT TP 9T ≈ 1.312 tỷ P4 ÷ ~3.700–4.000 USD/t ≈ 12,5–13,5 kt so với công suất 9T 15 kt ⇒ **~83–90%**. Q3 ≈ 4,0 kt/5 kt ≈ **~80%** | cần số thật (BCTN/ĐHCĐ) |
| 3 | kWh/t, cấp điện áp, giá điện | Không công bố. HTM 70 tỷ cầm cố bảo lãnh tiền điện cho EVN. DV mua ngoài ~500 tỷ/năm (ước lượng gần hết là điện). Ở 13–15 MWh/t [Bobby NỀN] và ~1.900 đ/kWh ⇒ ~25–28 tr đ/t | cần kiểm |
| 4 | P4 xuất thô vs hạ nguồn; thuế XK | **~100% là P4 thô.** TP chủ yếu P4 = 96,5% DT 2025 [KT25 TM29.1]; không có hạ nguồn. XK 2025 = 90% DT; 9T26 = 35%; Q3 ≈ 14% (DT − bán DLC). **Thuế XK P4 (HS 2804.70.00.10), XÁC NHẬN theo [EY] tóm tắt NĐ 199/2025/NĐ-CP (08/07/2025): 3%→5% (08/07–31/12/2025), 10% từ 01/01/2026, 15% từ 01/01/2027.** Thuế đã nộp 9T26 51,6 tỷ = 10,6% DT XK (khớp 10%). Chưa đọc Phụ lục I trên Công báo, chỉ có bản EY | ✅ xác nhận (nguồn thứ cấp chuyên nghiệp) |
| 5 | Cơ cấu giá bán, độ trễ so với TQ | Khách XK 2025: ICL Specialty 102,4, KS International 122,9, Italmatch 21,0 (phải thu 31/12/25). Q3/26 ICL trả trước 12,6 ⇒ có hợp đồng kỳ hạn. Biên 2026 không theo sunsirs (§2) ⇒ độ trễ/giá nội bộ **chưa đo được** | cần HĐ |
| 6 | Than cốc | Sunsirs Q3/26 2.040 so với 1.341 (+52% YoY), Q4-to-date 2.156 [BQ]. NVL 9T +19% | 🔴 áp lực |
| 7 | Hạ nguồn / LFP | Không có. Toàn bộ giá trị hạ nguồn (axit nhiệt, muối) nằm ở DLC/DGC | ❌ |
| 8 | Môi trường/pháp lý | Khởi tố gồm tội **gây ô nhiễm môi trường** + vi phạm thăm dò khai thác tài nguyên [BN26 TM33.4]. Không trích lập hoàn nguyên đất thuê (nợ tiềm tàng) [Q3 TM31] | ⚠️ WARNING §7 |
| 9 | Nhạy cảm | Xem §8.4 | ✅ |
| 10 | FX | DT XK USD giảm mạnh ⇒ độ nhạy FX giảm. Vay USD 30,8 tỷ (ngắn hạn). Lãi tỷ giá 7,2 / lỗ 3,1 trong 9T | thấp |

## 6. Vị thế & lợi thế cạnh tranh (5F tầng b)

Tra cứu: `data/moat_tags.csv` có DGC (NARROW, COST/LOCATION, asof 2026-06-05) nhưng **chưa có PAT** ⇒ làm đầy đủ.

**Loại hình doanh nghiệp:** nhà sản xuất hàng hoá cơ bản, đơn sản phẩm, quy mô nhỏ: 20 kt/năm, ~16% công suất P4 VN (~125 kt; viettimes). Là mắt xích **gia công** trong chuỗi DGC.

| Lực | Đánh giá | Bằng chứng |
|---|---|---|
| Nhà cung cấp | **Rất mạnh** | 100% quặng/NVL chính từ DLC (mẹ 51%). Không có mỏ |
| Khách hàng | **Mạnh** | 2026: DLC chiếm 63,7–85,5% DT. Khách XK là các tập đoàn lớn (ICL, Italmatch) |
| Sản phẩm thay thế | Trung bình | Axit ướt làm sạch cạnh tranh với tuyến nhiệt [Bobby §2] |
| Gia nhập mới | Thấp | Giấy phép lò, ĐTM, điện 110kV+, quặng Lào Cai hành chính hoá [Bobby §4] |
| Cạnh tranh nội ngành | Price-taker theo TQ | Giá do TQ đặt |
| **Lực 6 (chính sách)** | **Bất lợi, có đồng hồ** | Thuế XK 10→15% (2027); ưu đãi CIT hết 2030/2032; thuê đất ~2034–35 (GPMB phân bổ 16 năm còn ~8,1 năm, TM9; cam kết thuê >5 năm còn 1,67 tỷ, TM33.3); quặng ADMIN_GATED |

**Kiểm 3 điều kiện moat bền:**
- **(i) Lợi nhuận siêu ngạch nhiều chu kỳ:** ROIC_Min5Y **31,8%**, ROE_Min5Y **43,9%** [BQ] > Ke 13,5% ⇒ đạt **về hình thức**. Nhưng ROIC cao một phần do mẫu số bị ép: nhà máy đã khấu hao 62%, trả cổ tức ~100% LN. Không phải bằng chứng hào.
- **(ii) Cơ chế gọi tên được:** quyền tiếp cận quặng qua mẹ + giấy phép. Nhưng **cơ chế thuộc về DLC, không thuộc PAT**.
- **(iii) Đồng hồ cắt hào:** CÓ, gồm thuê đất, ưu đãi thuế, thuế XK, quặng.

⇒ **moat_tier NARROW, moat_type CAPTIVE_SUPPLY/PERMIT, rủi ro số 1: giá chuyển nhượng/phụ thuộc DLC.** Không thêm tham số moat; mô hình giữ EBT phẳng danh nghĩa, không mean-revert.
- **Độ nhạy moat:** nếu NONE (biên co dần −30% tới 2033) thì giá trị có trọng số 67.500 trước thanh khoản, 60.800 sau (−8,7% so với tâm rev2). WIDE không có cơ sở.
- **Dòng đề xuất cho `data/moat_tags.csv`** (KHÔNG tự sửa file): `PAT,NARROW,CAPTIVE_SUPPLY/PERMIT,M,Single-product P4 converter (20kt); ore 100% from parent DLC, 64-86% of 2026 revenue sold to DLC; ROIC_Min5Y 31.8% inflated by depreciated asset base + ~100% payout; clocks: land lease ~2034-35, CIT incentive ends 2030/2032, P4 export tax 15% from 2027,2026-11-14,dd_PAT_20261114,N`

## 7. Pháp lý / quản trị / bên liên quan — CHỈ WARNING (luật 27/09; không hạ kết luận vì pháp lý)

**⚠️ WARNING 1 — Vụ án.** Nguồn: [BN26 TM33.4], [KT25 TM30.4], viettimes, nguoiquansat.
- 17/03/2026: khởi tố vụ án gây ô nhiễm môi trường; vi phạm nghiên cứu, thăm dò, khai thác tài nguyên; vi phạm kế toán tại Tập đoàn DGC và các đơn vị liên quan.
- Bị can tại PAT gồm nguyên Chủ tịch HĐQT, TV HĐQT, GĐ Đặng Tiến Đức, KTT Phạm Thị Bích Phương. Tội danh với GĐ/KTT PAT: "vi phạm quy định về kế toán gây hậu quả nghiêm trọng".
- 23/07/2026: Chủ tịch đương nhiệm lúc đó (Lưu Bách Đạt) bị khởi tố về gây ô nhiễm môi trường.
- Thay toàn bộ HĐQT/BGĐ: ĐHCĐ bất thường 13/05; CT mới Đỗ Thành Công từ 28/07.
- Tài liệu kế toán bị niêm phong ⇒ BCKT 2025 nộp trễ ⇒ hạn chế GD từ 01/06, sau đó gỡ; HNX gỡ cảnh báo 24/08.
- **Ảnh hưởng đã biết lên số liệu:** chưa có điều chỉnh nào. UHY ngoại trừ vì không đánh giá được nghĩa vụ phải trả hay dự phòng tiềm tàng.

**⚠️ WARNING 2 — "Scandal di cư" sang giá chuyển nhượng.** Đây là rủi ro lớn nhất cho cổ đông thiểu số:
- **Đầu ra:** bán cho DLC 313,0 (2024), 163,7 (2025), **878,1 (9T26)**, trong đó **376,3 riêng Q3** (85,5% DT quý).
- **Đầu vào:** mua từ DLC 533,6 (2024), 749,9 (2025), 627,9 (9T26).
- **Tín dụng:** phải trả DLC lên tới 313 tỷ (31/12/25) rồi bị rút về 16,5. Vay ngân hàng do DGC/DLC bảo lãnh. **[rev2] Chiều ngược lại:** PAT thế chấp ~42,6 tỷ tiền gửi tại Vietinbank cho khoản vay của "Công ty và các công ty thành viên" (TM4 Q3), dư nợ nhóm **cần kiểm** (§3).
- **Vì sao đáng lo:** biên gộp giảm mạnh ĐÚNG lúc tỷ trọng bán cho mẹ tăng vọt và giá P4 thế giới tăng.
  - Giả thuyết lành tính: thiếu quặng/than cốc, cộng thêm né thuế XK 10%.
  - Giả thuyết bất lợi: mẹ mua P4 dưới giá thị trường để hưởng biên ở hạ nguồn hoặc XK của DLC.
  - **Hai giả thuyết này KHÔNG phân biệt được nếu thiếu đơn giá bán cho DLC (đ/t) so với giá XK cùng kỳ.** Đây là số cần kiểm số 1.
- **Kế toán:** đổi kiểm toán PwC (2024, chấp nhận toàn phần) sang UHY (2025–26, ngoại trừ). Tội danh "vi phạm kế toán" ⇒ rủi ro điều chỉnh hồi tố. HTK 67,7 tỷ đầu kỳ chưa được chứng kiến kiểm kê.

**WARNING 3 — Tập trung cổ đông.** DLC 51,00%, Đào Hữu Duy Anh 9,03%, Đào Hữu Huyền 7,69% (đều liên quan vụ án; đã rời HĐQT PAT) ⇒ nhóm chi phối 67,7%, free float ≤ 32,3%. Công ty TNHH Văn Minh: "chung sự kiểm soát của Chủ tịch Công ty" [KT25], giao dịch nhỏ.

**Ghi chú cổng (chỉ nêu, không đổi):** DGC đang EXCLUDED ở ZaloPay (hạn chế HOSE + vụ án). Danh sách BANNED không có PAT. Cổng excluded/banned không tự áp cho PAT. Giá trị cơ sở KHÔNG trừ khoản nào vì pháp lý.

## 8. Định giá — mù giá thị trường (một phần, xem đầu file)

### 8.1 Khung
- **Cách tính (rev2):** FCFE = LNST × (1 − 5,5%) (capex = KH, ΔVLĐ = 0; 5,5% = trích quỹ KTPL hằng năm 5,1–6,0% LNST, TM16: 20,71/343,21 và 13,49/264,94), cộng net cash thật 415,4 tỷ (đã trừ SỐ DƯ quỹ 76,69; dòng trích tương lai trừ trong FCFE ⇒ không trừ hai lần). Ngày định giá 30/09/2026.
- **r = 13,5%** @ lãi huy động 12T hiệu dụng **7,40%** (`effective_deposit_rate('2026-11-14')` = CCTG 12M 02/11) = điểm neo 03/11 ⇒ không điều chỉnh.
- **g dài hạn = 2%** (ước lượng; công suất cố định).
- **Thuế TNDN theo lộ trình ưu đãi:** 5% đến 2030, 10% 2031–32, 20% từ 2033 (terminal tính ở 20%).
- **Không có dự án mới** (XDCB dở 4,3 tỷ) ⇒ luật NPV=0 không phát sinh khoản nào.

### 8.2 Kịch bản (EBT hoạt động, không gồm thu nhập tài chính; `calc/valuation_PAT.csv`)

**EBT cơ sở rev2 = 202,6** (không phải 245). Cách tính, từng bước, không trừ hai lần:
1. Run-rate Q3/26 hoạt động = 4 × (LNTT 63,75 − TC ròng 9,90) = **215,4**. Con số này ĐÃ chịu thuế XK 10%.
2. Bước thuế XK 10%→15% (từ 01/01/2027) chỉ trên XK thực của Q3: XK Q3 = DT 440,03 − bán DLC 376,29 = 63,7 (14,5% DT; cận trên vì gồm bán nội địa không-DLC) ⇒ 255,0/năm × 5pp = **−12,7**.
3. 215,4 − 12,7 = **202,6**.
- Đối chiếu run-rate quý 2026 (skeptic): Q1 (P4 24,5k CNY) ~160/năm; Q3 (P4 27,6k) ~215/năm. 245 rev1 là 9T quy năm, bị Q2 ngoại lai (GPM 25%) kéo. Câu "khớp P4 25–26,5k" của rev1 **bỏ**: Q1 ở P4 24,5k cho ~160 và Q3 ở 27,6k cho ~215, biên không đi theo P4 (§2) nên không có ánh xạ P4→EBT.
- **Độ nhạy nếu dùng 245 cũ:** (FCFE đã trừ quỹ) tâm **71.800**; chỉ riêng sửa EBT 245→202,6 làm tâm −5.200. Quỹ KTPL một mình: 75.100 → 71.800 (−3.300).

| Kịch bản | Trọng số | Giả định | Giá trị (tỷ) | đ/cp |
|---|---|---|---|---|
| Xấu | 0,30 | EBT 150 (2027–28) rồi 200. ½ đời dự án hữu hạn tới 2034 (đ/cp 47.000), ½ liên tục (66.200) | 1.415,2 | **56.600** |
| Cơ sở | 0,50 | EBT 202,6 (run-rate Q3 − bước thuế XK) | 1.789,3 | **71.600** |
| Tốt | 0,20 | EBT 330 (≈ mức 2025): **quặng thông lại, mốc M5**, P4 giữ ~p75 | 2.653,0 | **106.100** |
| **Có trọng số** | | | 1.849,8 | **74.000** |
| **Sau CK thanh khoản 10% ⇒ TÂM** | | | 1.664,8 | **66.600** |

Trọng số 0,3/0,5/0,2 giữ nguyên (không có cơ sở dữ liệu độc lập để đổi).

**Chiết khấu thanh khoản** [BQ `ticker`]: ADV trung vị 6T **0,446 tỷ**, 3T 0,602 tỷ; 17/129 phiên không khớp; free float ≤32%.
- Vị thế 0,5 tỷ ở mức tham gia 15% ⇒ ~7 phiên để thoát. Vị thế 2 tỷ ⇒ ~30 phiên.
- Mức 10% là **(ước lượng)**, không có Amihud hay dữ liệu thực thi. Độ nhạy: 5% → 70.300; 20% → 59.200.
- Áp cho vị thế ≤ ~0,5 tỷ. Vị thế lớn hơn nên dùng mức 20%.

### 8.3 Hai nền giá trị + C4/D2 (chỉ HIỂN THỊ, không đổi tâm)

| Nền | Cách tính | đ/cp |
|---|---|---|
| V_ngắn | LNST chuẩn hoá = trung vị TTM 12 quý **287,7** × (1 − 5,5%) × (1 − g/ROE [2%/40,6%]) × (1+g)/(r−g) | **91.700** |
| V_dài | DCF FCFE cơ sở + net cash | **71.600** |
| D = \|ln(V_ngắn/V_dài)\| | 0,25 < ln2 | không cờ |
| V theo C4 (chưa qua tiêu chí khoá trước 2/4 chân trời, chỉ theo dõi; không đổi so rev1) | CFO3 373,1 − min(capex 3,1; KH 45) | 124.800 |
| V theo D2 (chưa qua tiêu chí khoá trước 0/9, chỉ theo dõi; không đổi) | CFO3 − 5% × DT 1.842 (capex/DT ngành 5% là **ước lượng, chưa đo**) | 94.800 |

**Đọc bảng:**
- V_ngắn > V_dài vì V_ngắn dùng LNST trung vị 3 năm (gồm Q2 ngoại lai, năm 2025 EBT cao), có thu nhập tài chính và không bước thuế XK. Khoảng cách mở rộng so rev1 (0,11 → 0,25) do EBT cơ sở thấp hơn.
- C4 phồng lên do CFO 2024–25 có giải phóng vốn lưu động (phải trả DLC tăng) và capex gần 0 (đầu tư thiếu). Không dùng làm neo.

### 8.4 Độ nhạy

**Theo lãi huy động** (giá trị có trọng số, trước thanh khoản):

| Thay đổi lãi huy động | β = 1 | β = 0,5 |
|---|---|---|
| −100bp | 78.900 (+6,6%) | 76.300 |
| −50bp | 76.300 (+3,2%) | 75.100 |
| +50bp | 71.800 (−2,9%) | 72.900 |
| +100bp | 69.800 (−5,6%) | 71.800 |

Độ nhạy thấp vì một phần lớn giá trị nằm trong dòng tiền 2027–2032 và net cash.

**EBT hằng năm (ước lượng):**

| Biến | Tác động EBT |
|---|---|
| ±10% giá P4 | **±~176 tỷ** (nếu đi thẳng vào EBT, ≈ ±87% EBT cơ sở 202,6). Đây là biến lớn nhất, nhưng biên 2026 không theo giá P4 (§2), nên là cận trên |
| ±5% giá điện | ±~25 tỷ |
| Thuế XK 10→15% | **−12,7 tỷ (cơ cấu XK Q3, đã vào cơ sở)**; −32 (cơ cấu XK 9T26); −87 (cơ cấu XK 2025) |
| −20% sản lượng | −~89 tỷ |

Quy đổi (số mô hình rev2, sau trừ quỹ KTPL): **1 tỷ EBT/năm vĩnh viễn = 263 đ/cp** giá trị kịch bản cơ sở (rev1 ghi 287). Lên TÂM: ≈ **+118 đ/cp** nếu chỉ dịch kịch bản cơ sở (× 0,5 × 0,9), ≈ **+236 đ/cp** nếu dịch cả ba kịch bản (× 0,9).
**Độ nhạy khác:** moat NONE (biên co dần −30% tới 2033): 67.500 trước thanh khoản, **60.800** sau (−8,7% so tâm). Net cash −42,6 tỷ (cầm cố Vietinbank): tâm 65.100.

## 9. Vùng giá, mốc khoá trước, điều kiện đổi theo CẢ HAI chiều

**Vùng (rev2):**
- Tâm **66.600**.
- "Rẻ" ≤ **56.600**.
- Hợp lý 56.600–76.600.
- "Đắt" ≥ **76.600**.

**Đối chiếu (sau khi có giá trị):** 71.000 cao hơn tâm 6,6%, trong vùng hợp lý, sát cận trên. Lợi suất cổ tức kế hoạch 9.000/71.000 ≈ 12,7% (**chỉ báo PL 24/10, chưa xác nhận nghị quyết**; hiển thị, không vào mô hình).

**Mốc khoá trước** (tâm tính lại từ `calc/model_PAT.py`, sau CK thanh khoản 10%):

| Mốc | Ngày | Quan sát | Hệ quả |
|---|---|---|---|
| M1 | BCTC Q4/2026 (~20–25/01/2027) | GPM Q4; DT Q4; tỷ trọng bán DLC | **XẤU:** GPM Q4 ≤ 15% (giữ mức Q1 13,6% / Q3 14,5%) ⇒ trọng số 0,50/0,35/0,15 ⇒ tâm **62.300**. **TRUNG GIAN:** 15% < GPM Q4 < 22%, hoặc GPM ≥ 22% nhưng DT < 500 ⇒ giữ 0,30/0,50/0,20 ⇒ tâm **66.600**. **TỐT:** GPM ≥ 22% **và** DT ≥ 500 ⇒ 0,20/0,45/0,35 ⇒ tâm **72.600** |
| M2 | 01/01/2027 (F6 Bobby) | Thuế XK P4 15% có hiệu lực hay bị hoãn | Hoãn ⇒ +12,7 tỷ EBT (bước thuế đã trừ ở cơ sở) ≈ **+3.500 đ/cp** kịch bản cơ sở, ≈ **+1.600** tâm. Đúng lịch thì đã có trong cơ sở |
| M3 | ĐHCĐ 2027 (~Q2/2027) | Tài liệu: sản lượng tấn, đơn giá bán DLC vs XK, cổ tức 2026 thực chi | Đơn giá bán DLC < giá XK ròng thuế quá ~5% ⇒ xác nhận rủi ro giá chuyển nhượng ⇒ chuyển cơ sở xuống EBT ~160 (run-rate Q1) ⇒ tâm **61.400** (−5.200). Ngang giá ⇒ gỡ WARNING 2. Mỗi 10 tỷ EBT cơ sở ≈ 1.180 đ/cp tâm |
| M4 | BCKT 2026 (~03/2027) | Ý kiến kiểm toán | Gỡ ngoại trừ ⇒ chuyển chiết khấu thanh khoản về 5% (+3.700, tâm 70.300). Điều chỉnh hồi tố/truy thu ⇒ trừ đúng số tiền |
| M5 | 31/05/2027 (F7 Bobby) | Quặng Lào Cai: quyết định dùng 3,53 tr t quặng loại III / nhà máy tuyển chạy ≥80% | Có ⇒ nghiêng kịch bản tốt (EBT 330). Không ⇒ nghiêng xấu |
| M6 | 2027-05-14 / 2027-11-12 (F1/F2) | P4 sunsirs | < 24.000 ⇒ cơ sở EBT ~150–160 (tâm ~60.200–61.400). > 32.000 ⇒ cơ sở EBT 330 (tâm ~82.100). Giữa hai mức: giữ cơ sở |

## 9b. Điều kiện HARD ABANDON + sizing

**HARD ABANDON** (bỏ hẳn giả định đi tiếp; không chờ mốc), khi xảy ra bất kỳ điều kiện nào:
1. PAT bị khởi tố **pháp nhân**.
2. Lò P4 bị đình chỉ hoạt động hoặc bị rút giấy phép môi trường (Chủ tịch đương nhiệm bị khởi tố ô nhiễm 23/07).
3. Tài sản thế chấp ở §3 (HTM cầm cố ~439 tỷ, gồm 40 tỷ + 100k USD Vietinbank) bị phong toả.
4. DLC ngừng cung quặng (nguồn 100% từ DLC).
5. Cổ tức đã công bố bị huỷ.
6. Kiểm toán chuyển từ ngoại trừ sang **từ chối đưa ý kiến**.

**Sizing (nếu có vị thế):** discretionary tiền lệ **≤ 0,5–1,0% NAV**; và trần theo thanh khoản: ADV trung vị 6T **0,446 tỷ**, tham gia 15% ≈ 0,067 tỷ/phiên (vị thế 0,5 tỷ ≈ 7 phiên thoát; 2 tỷ ≈ 30 phiên). Lấy mức nhỏ hơn của hai trần.

## 9c. Cái gì đã đổi so với 31/07

Báo cáo quét tuần 31/07 (`calculated_fear_state_backstop.md`, dòng ~1090) xếp PAT là **NON**: "KHÔNG phải case fear-buy: (a) thị trường không định giá nỗi sợ; (b) tội danh môi trường/khai thác tài nguyên chạm lõi; (c) PB 2,13 không có sàn tài sản".

**Đã đổi:**
- Luật user 27/09: phân tích bình thường, pháp lý chỉ là WARNING (không bake vào base).
- Phát hiện mới: **PAT không sở hữu mỏ** (TSCĐ vô hình = 0; quặng từ DLC, §5 #1), nên "rủi ro giấy phép mỏ chạm lõi" của 31/07 nằm ở DLC, không phải PAT; rủi ro chuyển thành **phụ thuộc DLC + giá chuyển nhượng**.
- BCTC Q3, bán niên, kiểm toán 2025 mới (biên gộp sập, bên liên quan 63,7–85,5% DT, cầm cố Vietinbank).

**Không đổi / nói rõ:** PAT **KHÔNG qua §2/§2.5 fear-buy sleeve**: người chống lưng là DGC tư nhân đang bị điều tra, P/B ~2,5 không có sàn tài sản. **Đường vào duy nhất nếu có là luật user 02/11 #4** (DD + giá < 0,85 × tâm = **56.600**, user duyệt từng lần), **không phải sleeve fear-buy.** Hiện giá 71.000 chưa thoả.

## 10. Số cần kiểm (ưu tiên)

1. **Đơn giá bán P4 cho DLC (đ/t) so với giá XK cùng kỳ**, và đơn giá quặng/NVL mua từ DLC. Nguồn: tờ trình ĐHCĐ, HĐ khung với bên liên quan, nghị quyết HĐQT phê duyệt giao dịch bên liên quan.
2. **Sản lượng P4 theo quý** 2025–2026 và hệ số sử dụng lò. Hiện chỉ có ước lượng 80–90%.
3. kWh/t, cấp điện áp, hoá đơn điện.
4. Hạn hợp đồng thuê đất KCN Tằng Loỏng và điều khoản gia hạn. Suy ra hiện tại là ~2034–35 từ phân bổ GPMB.
5. Phụ lục I NĐ 199/2025 bản Công báo (hiện chỉ có bản tóm tắt của EY).
6. Nội dung kết luận điều tra / cáo trạng liên quan PAT: số tiền thiệt hại, nghĩa vụ khắc phục môi trường.
7. Lệch tiền 1,246 (BCĐKT) với 1,286 (TM3) trong BCTC Q3.
8. Capex/DT trung vị ngành hoá chất (cho dòng D2). Hiện là ước lượng 5%.
9. Kế hoạch đại tu lò (capex thực sắp tới, so với capex ~0 hiện tại).

## 11. Nguồn

**Tệp trong `src/`:**
- `PAT_Q3_2026.pdf`: BCTC Q3/2026.
- `PAT_BN_2026_soatxet.pdf`: UHY 907/2026/UHY-BCSX, 14/08/2026.
- `PAT_KT_2025.pdf`: UHY 749/2026/UHY-BCKT, 20/06/2026.
- `PAT_Q2_2026.pdf`, `PAT_Q1_2026.pdf`, `PAT_Q3_2025.pdf`: đã tải, chưa render, không dùng số trực tiếp.
- `EY_customs_update_jul2025_ND199.pdf`.
- Danh sách file BCTC lấy qua API cafef `FileBCTC.ashx?Symbol=PAT`. Website IR của PAT không phân giải được.

**BQ:** `ticker_financial` PAT 2022Q1–2026Q3; `ticker` ADV tới 2026-11-13; `commodity_prices` sunsirs `yellow_phosphorus`/`coke`. Lãi suất: `deposit_rate_vn.effective_deposit_rate('2026-11-14')` = 7,40%.

**Báo chí:**
- [Báo PL 24/10/2026 — 9T 216 tỷ, KH 2.111/280, cổ tức 90%](https://doanhnhan.baophapluat.vn/apatit-viet-nam-pat-lai-gan-216-ty-dong-sau-9-thang-hoan-thanh-77-ke-hoach-nam.html)
- [Báo PL 28/04/2026 — Q1, CFO −408,27, giải trình giá vốn +14%](https://doanhnhan.baophapluat.vn/apatit-viet-nam-pat-loi-nhuan-quy-i-boc-hoi-45-dong-tien-kinh-doanh-tham-hut-sau-bien-co-thuong-tang.html)
- [Viettimes — bị can theo đơn vị, công suất 20 kt, lịch sử cổ tức](https://viettimes.vn/vu-hoa-chat-duc-giang-doanh-nghiep-co-giam-doc-bi-bat-la-ga-de-trung-vang-cho-tap-doan-post195686.html)
- [Báo PL — xin chậm nộp BCKT do tài liệu bị niêm phong](https://doanhnhan.baophapluat.vn/phot-pho-apatit-viet-nam-pat-xin-cham-nop-bao-cao-kiem-toan-nam-2025-do-tai-lieu-ke-toan-dang-bi-niem-phong.html)
- [Nguoiquansat — Lưu Bách Đạt bị khởi tố](https://nguoiquansat.vn/ong-luu-bach-dat-bi-khoi-to-them-mot-doanh-nghiep-cong-bo-thong-tin-bat-thuong-306013.html)
- [EY Customs & Global Trade Update 07/2025](https://www.ey.com/content/dam/ey-unified-site/ey-com/vi-vn/technical/tax/documents/customs-global-trade-update-july-2025-vn.pdf)

## Phụ lục E — Phản biện fundamental-skeptic

(Mike điền)

**Vòng 1 (rev1) — verdict REFUTED mức mô hình/văn bản**, độ tin cậy trung bình–cao (fundamental-skeptic, 14/11/2026). Số BCTC trích tay khớp ảnh trang gốc (kể cả Q1/26 tự render), net cash 415,4 tỷ không đếm trùng. Đính chính đã áp ở rev2:
1. FCFE bỏ trích quỹ KTPL (5,1–6,0% LNST/năm, TM16) ⇒ tâm −3.300.
2. EBT cơ sở 245 (9T quy năm, bị Q2 ngoại lai kéo) mâu thuẫn run-rate Q1 (~160) và Q3 (~215) ⇒ đặt 202,6 (run-rate Q3 − bước thuế XK 15% theo cơ cấu XK Q3).
3. Bỏ sót TM4: 40 tỷ + 100k USD tiền gửi Vietinbank thế chấp cho vay của "Công ty và các công ty thành viên" (nhóm DGC) ⇒ thêm vào §3/WARNING 2, độ nhạy net cash.
4. M1 nhánh xấu không thể kích hoạt (Q3 GPM đã 14,5%) ⇒ sửa thành GPM Q4 ≤ 15%.
5. Quy đổi 1 tỷ EBT = 287→263 đ/cp (sau KTPL). 6. facts: 0,146 tỷ là lãi dự thu BIDV, MB = 0 tại 30/09. 7. Thêm §9b HARD ABANDON + sizing. 8. Thêm §9c đối chiếu NON 31/07 và nói rõ PAT không qua §2/§2.5. 9. Cổ tức 90% chỉ có báo PL, chưa có nghị quyết. 10. Ghi trung thực mù giá một phần.
**Kết quả rev2:** tâm 75.100 → **66.600**; giá 71.000 cao hơn tâm 6,6% (rev1 nói thấp hơn 3,2% — đảo dấu). **Chưa chạy vòng skeptic thứ hai** cho rev2: mọi thay đổi là áp đúng đính chính skeptic nêu; riêng lựa chọn EBT 202,6 (thay vì ~215 skeptic gợi ý) là phán đoán của Taylor có nêu công thức, và độ nhạy 245 cũ ghi ở §8.2. Còn mở: đơn giá bán P4 cho DLC (rủi ro giá chuyển nhượng), sản lượng tấn theo quý, kết luận điều tra.
