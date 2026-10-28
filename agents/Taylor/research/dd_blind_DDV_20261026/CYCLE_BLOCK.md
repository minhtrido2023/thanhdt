# CYCLE_BLOCK — DDV (CTCP DAP-VINACHEM) · bước 1 · job `Taylor_20261026_045654` · 2026-10-26

```
BLIND_ATTESTATION
  da_viet_truoc_khi_doc_BCTC_quy_Q : có (chưa mở BCTC Q3/2026 hay tin KQKD Q3 trước khi khoá file này)
  da_doc_DD_cu_cua_ma_nay          : không (chưa mở research/dd_DDV_20261026/) — NHƯNG xem dòng lộ thông tin dưới
  da_biet_verdict_truoc            : CÓ
  quy_Q (mới nhất đã công bố)      : 2026Q3       ngày công bố: 2026-10-20..22 (theo dispatch)
  du_lieu_tai_chinh_dung_den_quy   : 2026Q2 (BQ ticker_financial, quarter <= "2026Q2")
  cycle_block_md5                  : xem LOCK.txt
  cycle_block_commit               : KHÔNG commit (dispatch chỉ định md5 + mtime thay commit)
  blind                            : NO
  Lộ thông tin (vô tình, trước khi viết):
   1. dd_template_20261026/README.md §4 (file được PHÉP mở) ghi verdict cũ DDV = "NON (watchlist)", biên ở đáy,
      DAP đỉnh, sốc chi phí, PB 1,17 vs đáy cũ 0,68–0,76.
   2. dd_template_20261026/TEMPLATE.md mục A/E ghi "DDV Q3/26: BQ 0,10 vs BCTC 3,7%" (biên gộp quý Q3) và
      "DDV: thiếu 1.207,8 tỷ" tiền gửi trong Cash_P0.
   3. Cột PE của BQ `ticker` nhảy 4,30 → 6,57 ngày 2026-10-22 (EPS TTM giảm sau khi cập nhật Q3) — thấy khi lấy giá.
   4. Working-memory đầu phiên ghi phiên trước của tôi đã lấy số Q3 cho DDV (không có giá trị số).
   5. Tôi (Taylor) là tác giả báo cáo DDV cũ sáng 26/10 (theo working-memory) ⇒ thiên lệch hồi tưởng không loại được.
  ⇒ Entry này KHÔNG tính vào cổng đánh giá (README §3). Mọi số dưới đây vẫn chỉ dùng dữ liệu ≤ 2026Q2 + feed.
```

**Loại ngành:** chu kỳ hàng hoá (phân bón DAP; đầu ra DAP/MAP, đầu vào quặng apatit, lưu huỳnh → axit sulfuric, NH3).

**A. Biên so với lịch sử chính mã** (BQ `ticker_financial`, tự tính TTM = Σ4 quý NP / Σ4 quý Revenue)
- Cửa sổ TTM: 2015Q4–2026Q2, 43 điểm; chu kỳ thấy được k ≈ 3 (đáy 2016–17, 2019–20, 2023; đỉnh 2018, 2022, 2025).
- Biên LNST TTM 2026Q2 = **9,02%**, phân vị **81** (tự tính, khớp `NPM_P0`=0,0905 ⇒ `NPM_P0` là TTM).
- `GPM_P0` 2026Q2 = 0,1378, phân vị **65** (n=46). `GPM_P0` trông là TTM (đi cùng `NPM_P0`), CHƯA đối chiếu với
  BCTC kiểm toán (không mở BCTC trong bước này) ⇒ dùng biên LNST làm chỉ số chính.
- **Quỹ đạo quý quan trọng hơn mức TTM:** biên LNST quý 2025Q3 15,8% → Q4 9,3% → 2026Q1 6,7% → Q2 **5,8%**
  (phân vị quý 63). TTM ở mức cao vì còn mang quý đỉnh 2025Q3; quý gần nhất đã rơi về quanh trung vị.
- k=3 ⇒ phân vị là mô tả.

**B. Giá đầu ra/đầu vào**
| Biến | Vai trò | Gần nhất | Trung vị 5 năm | Phân vị 10 năm | Nguồn |
|---|---|---|---|---|---|
| DAP (USD/t) | đầu ra | 783,8 (2026-06); 800,6 (2026-09) | 627 / 633 | **96 / 98** | [FEED] `data/dap_monthly.csv` (WB CMO) |
| Urea (USD/t) | proxy giá N/NH3 (đầu vào gián tiếp) | 453,1 (06) ; 407,5 (09) | 413 / 404 | 82 / 73 | [FEED] `data/urea_monthly.csv` |
| Brent | proxy năng lượng/vận tải | 85,4 (06) ; 116,8 (09) | 81 / 83 | 85 / 98 | [FEED] `data/brent_monthly.csv` |
| Lưu huỳnh | đầu vào chính (axit) | ~620 (Q1/26), ~500 (05/26) vs 256–315 năm 2025 | — | — | **CHUỖI THIẾU** — `data/sulfur_anchors.csv` chỉ 5 mốc 2025-04..2026-05, nguồn báo chí, basis lẫn lộn |
| NH3, quặng apatit | đầu vào chính | — | — | — | **CHUỖI THIẾU** |
- Spread DAP − (S + NH3 + apatit) — biến chi phối thật — **không đo được**.

**C. Pha chu kỳ: KHÔNG XÁC ĐỊNH (theo luật mẫu) — nghiêng GIỮA-XUỐNG từ đỉnh, cơ chế CHI PHÍ**
- Luật cơ học 80/20: A (81) và DAP (96) đều ≥ 80 ⇒ mặc định ĐỈNH. Nhưng biến chi phối là SPREAD, mà S/NH3 là
  CHUỖI THIẾU ⇒ theo mẫu chỉ được "giữa/không xác định".
- Ủng hộ "giữa-xuống từ đỉnh": (1) biên LNST quý giảm 4 quý liền 15,8 → 5,8% trong khi DAP vẫn tăng 627 → 784 ⇒
  ép biên đến từ đầu vào, không từ giá bán; (2) mốc lưu huỳnh ~2x so 2025 [sulfur_anchors]; hàng tồn kho 2026Q2
  906 tỷ vs 356 tỷ 2025Q2 [BQ `Inventory_P0`] và CF_OA âm 3 quý liền (−20, −72, −105 tỷ) ⇒ đang tích hàng/nguyên liệu giá cao.
- Chống: DAP chưa giảm (phân vị 98 tháng 09/2026) và urea hạ (453 → 408) ⇒ nếu S hạ nhiệt, spread có thể nở lại
  nhanh; TTM vẫn ở phân vị 81 — chưa phải đáy theo bất kỳ thước đo nào.
- Khác các đáy cũ: 2016, 2019–20, 2023 xảy ra khi giá DAP thấp/giảm (cầu/giá bán); lần này giá bán ở đỉnh ⇒ đây
  KHÔNG phải đáy cùng loại, PB đáy cũ (0,46–0,70) không phải mốc so.
- Cung: không có số công suất ngành mới trong 12–24 tháng (chưa đo).

**D. Neo chính sách/cấu trúc** (chưa tra URL trong bước này — nhãn [chưa verify], ghi để kiểm ở bước 2)
| Neo | Loại | Ngày | Chu kỳ/cấu trúc | Nguồn |
|---|---|---|---|---|
| Phân bón chịu VAT 5% (được khấu trừ VAT đầu vào) | thuế | 2025-07-01 | cấu trúc (+) | Luật GTGT 48/2024/QH15 [chưa verify] |
| Hạn chế xuất khẩu phốt phát của Trung Quốc | chính sách nước ngoài | từ 2021, theo đợt | chu kỳ (đỡ giá DAP) | [chưa verify ngày cụ thể] |
| Nguồn quặng apatit phụ thuộc Apatit VN (cùng VINACHEM) | hợp đồng nội bộ tập đoàn | không rõ hạn | cấu trúc | [chưa verify] |
- Dòng tiền lõi không có thời hạn pháp lý rõ (không phải giấy phép mỏ/PPA) ⇒ E dùng PE vĩnh viễn chuẩn hoá.

**E. Định giá chuẩn hoá** (giá 17.700 đ đóng cửa 2026-10-23 [BQ `ticker`]; 146,11 tr cp ⇒ vốn hoá **2.586 tỷ**)
- LN chuẩn hoá (a) = trung vị LNST năm 2017–2025 = **168,3 tỷ** [BQ, tự tính]; (b) biên LNST trung vị năm 2016–25
  3,56% × doanh thu TTM 6.519 tỷ = **232 tỷ**. Chọn (a) làm chính (không giả định doanh thu 2025–26 bền ở giá DAP đỉnh).
- Nợ vay 2026Q2 = 403,1 + 3,6 = 406,7 tỷ; `Cash_P0` 170,7 tỷ ⇒ net cash BQ **−236 tỷ**. ⚠️ `Cash_P0` có thể thiếu tiền
  gửi có kỳ hạn — CHƯA ĐO ở Q2 (không mở BCTC Q2 trong bước 1).
- PE chuẩn hoá (BQ net cash): (2.586 + 236)/168,3 = **16,8x**; theo (b) **12,2x**. PE trailing Q2 = 2.586/587,9 = 4,4x
  (gây hiểu lầm: TTM mang quý đỉnh).
- PB = 17.700/14.931 (BVPS Q2) = **1,19x**. PB đáy cũ (cơ chế cầu): 0,46 (2016), 0,63 (2019–20), 0,70 (2023) [BQ];
  không cùng loại cú sốc ⇒ chỉ tham khảo. PB min năm 2025 = 1,15.
- Kết luận E: trên LN chuẩn hoá DDV KHÔNG rẻ (PE 12–17x); "rẻ" chỉ khi coi LN 2025 là bền.

**F. DỰ BÁO CÓ THỂ BÁC BỎ**
```
FORECAST
  indicator   : biên LNST TTM DDV = Σ NP_P0 4 quý / Σ Revenue_P0 4 quý
  source      : tav2_bq.ticker_financial (ticker='DDV'), đối chiếu BCTC hợp nhất/riêng quý của DDV
  baseline    : 9,02% (TTM 2026Q2)
  call        : TTM tại 2027Q1 (2026Q2..2027Q1) < 7,0%
  horizon     : quý 2027Q1
  due_date    : 2027-05-01 (BCTC Q1 dự kiến ~2027-04-20 + 10 ngày)
  p           : 0,65
  persistence : TTM giữ ≥ 9,0% ⇒ call MISS
  void_if     : sáp nhập/tách, đổi chuẩn mực (VAS→IFRS) làm đổi doanh thu, đình chỉ giao dịch, điều chỉnh hồi tố > 10% LN
```
