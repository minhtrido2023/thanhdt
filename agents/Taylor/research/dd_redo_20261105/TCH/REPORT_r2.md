# DD REDO VÒNG 2 — TCH (Hoàng Huy, HOSE) · job `Taylor_20261105_020021` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Áp `../STANDARD_r2.md`. Số: `calc/model_r2.py` → `calc/model_r2_out.txt/json`, `SUMMARY.json` (r1: `SUMMARY_r1.json`), `calc/LOCK_r2_md5.txt`; chạy 2 lần trùng byte.
> Số BCTC giữ vòng 1 (BCTC hợp nhất/riêng 01/04–30/09/2026, **chưa soát xét**, đọc ở `../../dd_TCH_20261031/calc/notes_read.md`). Đã rà `SKEPTIC_20261031.md` (14 điểm B1–B14) + `GAPS.md`. Giá **12.750 đ** (04/11/2026). Đơn vị tỷ đồng.

## 0. Kết luận (mức KẾT CỤC, sau CK thanh khoản 5 tỷ)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng lưới (trước / sau CK) | 13.857 / **13.768** |
| **P50** kết cục (sau CK) | 13.726 |
| Giá trị tại tham số trung tâm (biên 33,5%, thặng dư 40%, holding 15%; sau CK) | 13.775 |
| **P10 / P90** kết cục (sau CK) | **12.559 / 14.983** |
| n kết cục · % trọng số dưới giá · thấp nhất | 108 · **19,1%** · 11.942 |
| Giá 12.750 so tâm | **−7,4% ⇒ TRONG vùng (nửa dưới, sát P10 +1,5%)** — nhãn không đổi |

Tâm vòng 1 13.401 ⇒ vòng 2 **+2,7%**: chiết khấu holding vòng 1 đặt 20% trong BASE, nhưng dữ liệu chỉ xác nhận CẤU TRÚC (2 tầng niêm yết, CRV free float ~3%, khớp 24/62 phiên), còn ĐỘ LỚN là nhận định ⇒ điều 3: chuyển thành trục xác suất {0; 10; 20; 30}% đều 1/4 [UL] (kỳ vọng 15%). So vùng cũ 31/10 (12.650): +8,8%.
**Độ bền nhãn**: nhãn nhạy với 3 giả định tự đặt — bỏ holding (0%) hoặc thặng dư đất cũ theo biên lịch sử ⇒ DƯỚI vùng; CK quản trị 15% ⇒ TRÊN vùng. Giá đứng gần P10 nên nhãn "TRONG" mong manh ở cả hai phía.
Ba con số: tâm 13.768 ≈ P50 13.726 ≈ tham số trung tâm 13.775; phân phối gần đối xứng, không nhánh trọng số nhỏ nào quyết định P10/P90.
⚠️ **Cross-check ROE lệch rất xa NAV** (§3): giá trị theo P/B-ROE chỉ 3.400–4.600 đ. NAV dự án dựa trên tái tạo thặng dư quỹ đất; ROE chuẩn hoá ~6% < r 13,5% nói rằng nếu lịch sử lợi nhuận lặp lại thì VCSH không tạo giá trị. Đây là rủi ro mô hình lớn nhất — skeptic B4 cũng đã nêu "NAV ≈ sổ sách, không độc lập với giá".

## 1. Lưới (điều 1–2)
4 trục, 108 ô, mỗi ô 1 kết cục tất định; phân vị `_shared/wpct.py`.
- **Có**: biên ròng backlog {30; 33,5; 36}% [UL; skeptic B12 ~33–34%] · thặng dư HTK đất cũ sau thuế {25; 40; 55}% [UL] · CK holding phần qua công ty con {0; 10; 20; 30}% (đều) [UL] · r {12,5; 13,5; 14,5}%.
- **Loại + song song (sau CK)**:

| Trục | Lý do loại | Bản song song: tâm · P10/P90 · nhãn |
|---|---|---|
| CK quản trị | luật pháp lý/quản trị = WARNING | 5%: 13.080 · 11.931/14.234 · TRONG; 10%: 12.391 · TRONG; 15%: 11.703 · 10.675/12.736 · **TRÊN** |
| Thặng dư quỹ đất mới | luật 03/11 NPV 0 | −10%: 13.622 · TRONG; +10%: 13.914 · TRONG |
| Tiền gửi NH Sài Gòn Tài Lộc 678,3 | skeptic B9 INCONCLUSIVE, không có dữ liệu hạn chế rút | stress mất 100%: 13.096 · TRONG (cận dưới cực đoan, không phải kịch bản) |
| Thặng dư đất cũ theo biên lịch sử {40;55;70}% | giữ tâm 40% làm đệm chi phí hoàn thành chưa quan sát (B3) | 14.349 · 13.083/15.644 · **DƯỚI** |
| (đối chiếu) holding vòng 1 {10;20;30} | — | 13.380 · 12.559/14.205 · TRONG |
| (đối chiếu) holding 0% | — | 14.931 · 14.274/15.597 · **DƯỚI** |

## 2. Khoản lệch sổ sách trong BASE (điều 3)
| Khoản | Hiệu ứng | Cơ sở | Nguồn |
|---|---|---|---|
| CK holding (chỉ phần qua con) | trục 0–30%, kỳ vọng 15% (−1.171 đ/cp trước CK so 0%) | cấu trúc quan sát được; độ lớn [UL] | GAPS §1, SKEPTIC B4/B7 |
| Thặng dư đất cũ tâm 40% < ~70% lịch sử | trục | đệm chi phí hoàn thành HH1–HH4 chưa công bố [UL] | SKEPTIC B3 |
| Quỹ đất mới 3.006,3 theo giá sổ | 0 | TM17 mua đất 6T FY26 | notes_read TM17 |
Tham số tự đặt [UL]: VAT bình quân 1,08; PV backlog 1–2 năm, thặng dư 4 năm; trọng số mọi trục; β=1.

## 3. Cross-check P/B-ROE (điều 10; g 3%, LN chuẩn hoá 727 = EPS 725 [UL, v2])
- Có lãi tiền gửi: ROE 6,0% ⇒ **3.442 đ**.
- Không lãi tiền gửi (lãi TG/cho vay 6T 173,5 ⇒ ~278/năm sau thuế, hợp nhất — cận trên phần mẹ): ROE vận hành 4,9% trên VCSH trừ tiền mẹ ~2.960, cộng lại tiền ⇒ **4.600 đ**.
Cả hai ≪ giá và ≪ NAV: thị trường (P/B 1,05x) đang trả cho thặng dư quỹ đất tái hiện, không cho ROE lịch sử.

## 4. Thanh khoản (điều 6)
| Cỡ | ADV250 87,1 tỷ (σ 2,69%) | ADV60 53,2 tỷ (σ 2,39%) |
|---|---|---|
| 10 / 20 / 40 tr (sleeve) | ≤0,06% | ≤0,07% |
| **5 tỷ (tham chiếu nhãn)** | **0,64%** (Q/ADV 5,7%, trong vùng hiệu chỉnh) | 0,73% (9,4%, trong vùng) |
Thanh khoản không phải ràng buộc. ADV60 thấp hơn ADV250 ~39%.

## 5. Độ nhạy r: β=1 ±100bp ⇒ ∓0,5%; β=0,5 ⇒ ∓0,2% (PV ngắn).

## 6. ⚠️ WARNING pháp lý/quản trị — TRUNG BÌNH (mang đủ cờ skeptic/GAPS)
1. **QĐ 1020/QĐ-XPHC 03/04/2026** (Thuế TP Hải Phòng): khai sai TNDN — phạt 2,735 + truy thu 13,676 + chậm nộp 3,798 = 20,21 tỷ; đã nộp, CBTT 07/04/2026.
2. **QĐ 1357/QĐ-XPHC 12/2024** (UBCKNN, CBTT/bên liên quan, 295 tr) ⇒ 2 cơ quan, 2 loại vi phạm trong 16 tháng.
3. Nhóm kiểm soát (Đỗ Hữu Hạ 30,18% + HH Finance 5,81%, người liên quan) 35,99% = 71,2% phiếu ĐHĐCĐ 2026; Trưởng BKS kiêm KTT công ty con; kiểm soát CRV 89,35% biểu quyết (không phụ thuộc uỷ quyền 7,37%), CRV free float ~3% — chuẩn duy trì niêm yết chưa kiểm.
4. **Tiền gửi 678,3 tỷ tại NH TMCP Sài Gòn Tài Lộc** (~21% tiền+HTM) gần như không rút khi HTM giảm 2.025 — INCONCLUSIVE (B9).
5. BLQ trong tập đoàn ĐÃ công bố (BC quản trị 6T 2026; NQ HĐQT 16/04, 23/06, 21/07/2026; TCH cho CRV vay 30 tỷ, hạn mức 500 tỷ) — điểm tích cực; còn mở BLQ NGOÀI tập đoàn (HH Finance, gia đình Đỗ).
6. Dragon Capital bán ròng xuống 4,71% (15/06/2026).
7. BCTC 6T FY26 chưa soát xét (AASC dự kiến 30/11); sử dụng vốn chào bán 865,5 tỷ (M7).
8. **Dữ liệu NQ mới**: NQ HĐQT 08/2026 phát hành 91,2 tr cp thưởng 10% (ĐKCC 04/09/2026) — đã phản ánh (SH 1.003,3 tr). Không thấy NQ HĐQT 10–11/2026.
9. "Không có khởi tố/kiểm toán ngoại trừ": nguồn = GAPS 31/10/2026 (27 PDF hoanghuy.vn) + web search 05/11/2026 (cafeland, baophapluat, stockbiz) — không có kết quả mới.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| BCTC soát xét 6T FY26 (AASC) | 30/11/2026 | LN mẹ 6T ±5% của 663,1, không ngoại trừ | điều chỉnh >5% / ngoại trừ ⇒ hạ tâm ~1.000, nâng WARNING |
| Quý 10–12/2026 | ~31/01/2027 | LN mẹ ≥400 + NMTT NC-II bổ sung ⇒ biên/thặng dư lên | NMTT giảm không bổ sung, biên gộp <40% |
| BCTC Q3 riêng CRV | khi có | tiêu NMTT NC-II chậm hơn ước | nhanh hơn (B5) ⇒ backlog hết sớm |
| Xác minh Sài Gòn Tài Lộc | khi có | rút được/không hạn chế | hạn chế rút ⇒ đưa stress 678 vào kịch bản có xác suất |
| Quỹ đất mới có giá bán | 2027 | biên gộp ≥35% có số ⇒ cộng thặng dư | vượt dự toán/chậm pháp lý |
**HARD ABANDON**: (a) kiểm toán ngoại trừ/từ chối ý kiến; (b) khởi tố pháp nhân TCH/CRV hoặc lãnh đạo chủ chốt; (c) tiền gửi 678,3 bị phong toả; (d) cho bên liên quan NGOÀI tập đoàn vay/bảo lãnh. Sleeve 10–40 tr ⇒ không tranche.
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng; giá gần P10 do định giá, không do sự kiện.

## 9. Mở
BCTC Q3 riêng CRV · xác minh NH Sài Gòn Tài Lộc · legal-vn: uỷ quyền 7,37% + chuẩn niêm yết CRV · BLQ ngoài tập đoàn · BQ OShares 912,1 tr (trước cp thưởng) · SOTP HHS ~0,5x (B7) chưa dùng làm neo. Chưa qua fundamental-skeptic.

## Phụ lục — đổi so với vòng 1
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| CK holding | tâm 20% trong base | trục {0;10;20;30} đều (kỳ vọng 15%) | điều 3 |
| Tâm | 3 kịch bản | kỳ vọng lưới 108 ô | điều 4 |
| Cross-check | — | P/B-ROE 2 biến thể (3.442 / 4.600) | điều 10 |
| Song song | CK quản trị, quỹ đất mới (lệch lên) | + quỹ đất mới −10%, stress 678, thặng dư lịch sử, holding 0% | điều 2 |
| Cờ | 5 | + Sài Gòn Tài Lộc, BLQ đã công bố/ngoài tập đoàn, kiểm soát CRV 89,35%, cp thưởng 08/2026, nguồn+ngày tra | điều 5 |
