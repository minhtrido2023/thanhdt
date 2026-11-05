# DD REDO VÒNG 2 — SAS (SASCO, UPCoM) · job `Taylor_20261105_020021` · 05/11/2026

> Chỉ NGHIÊN CỨU, không khuyến nghị. Áp `../STANDARD_r2.md`. Số: `calc/model_r2.py` → `calc/model_r2_out.txt/json`, `SUMMARY.json` (r1 ở `SUMMARY_r1.json`), `calc/LOCK_r2_md5.txt`; chạy 2 lần trùng byte.
> Số BCTC giữ vòng 1 (`REPORT.md` §2–§3; BCTC tổng hợp Q3/2026 gốc `src/Q3_2026_tonghop_kemgiaitrinh.pdf`). Giá **34.700 đ** (04/11/2026). Đơn vị tỷ đồng.

## 0. Kết luận (mức KẾT CỤC, sau CK thanh khoản 5 tỷ)

| | đ/cp |
|---|---|
| **Tâm** = kỳ vọng lưới (trước / sau CK) | 33.053 / **31.066** |
| **P50** kết cục (sau CK) | 30.806 |
| Giá trị tại tham số trung tâm (Δ −25%, N0, r 13,5%, g 3%; sau CK) | 30.869 |
| **P10 / P90** kết cục (sau CK) | **23.751 / 38.022** |
| n kết cục · % trọng số dưới giá · thấp nhất | 135 · **73,6%** · 19.056 |
| Giá 34.700 so tâm | **+11,7% ⇒ TRONG vùng (nửa trên)** — nhãn không đổi |

Tâm vòng 1 29.164 ⇒ vòng 2 **+6,5%**: (1) **phải thu dài hạn khác 242,0 (mã 215) ghi theo sổ** (+1.813 đ/cp trước CK) — vòng 1 loại khoản này "vì chưa đọc thuyết minh", tức lệch sổ sách không có dữ liệu (vi phạm điều 3); (2) thêm trục **g {2;3;4}%** — Gordon vô hạn mà vòng 1 cố định g; tính lồi theo g/r làm tâm kỳ vọng > giá trị tại tham số trung tâm. So vùng cũ 26/10 (32.600): −4,7%.
Ba con số: tâm 31.066 > P50 30.806 ≈ tham số trung tâm 30.869 (lệch phải nhẹ do Gordon lồi). Không nhánh trọng số nhỏ nào quyết định P10/P90.
**Thanh khoản là con số chi phối nhãn**: CK 6,0% ở cỡ 5 tỷ là quy ước, Q/ADV ≈ 850% — **ngoài xa vùng hiệu chỉnh**. Ở cỡ sleeve thật 40 tr (CK 0,54%) tâm 32.875, giá +5,6% so tâm, vẫn TRONG vùng.

## 1. Lưới (điều 1–2)
4 trục, 135 ô, mỗi ô 1 kết cục tất định; phân vị = `_shared/wpct.py`.
- **Có**: Δ Long Thành lên LN vận hành từ 2028 {−55; −40; −25; −10; +5}% (0,1/0,2/0,4/0,2/0,1) [UL; cận dưới ≈ mất toàn bộ mảng gắn khách quốc tế ~57% DT Q3] · N0 {466,6; 518,4; 570,2} · r {12,5; 13,5; 14,5}% · **g {2; 3; 4}% (mới)**; mỗi trục phụ 1/4–1/2–1/4. 2027 = nửa tác động [UL].
- **Loại + cơ sở + song song**:

| Trục loại | Lý do | Bản có trục / đối chiếu (sau CK) |
|---|---|---|
| Truy thu tiền thuê đất thêm | không có số/quyết định mới (2015–2024 đã hạch toán Q4/2025) | WARNING |
| Pha loãng khi phát hành/chuyển HOSE | chưa có giá/tỷ lệ; phát hành giá thị trường ≈ NPV 0 | WARNING |
| Suy giảm phải thu DH 242 / trích lập HTK 204 | chưa đọc thuyết minh, không có dữ liệu suy giảm | bỏ phải thu DH: tâm 29.362, P10/P90 22.047/36.317, % dưới giá 84,4% |
| (đối chiếu) bỏ trục g | — | tâm 30.971, P10/P90 23.751/37.934 |
| (đối chiếu) tái lập r1 (bỏ cả hai) | — | tâm 29.267 (≠ r1 29.164 vì r1 dùng 3 kịch bản, không lấy kỳ vọng trên trục r lồi) |

## 2. Khoản lệch sổ sách trong BASE (điều 3)
| Khoản | đ/cp | Cơ sở dữ liệu | Nguồn |
|---|---|---|---|
| Trừ phải trả NLĐ 141,2 + quỹ KTPL 99,7 + thuế 50,2 khỏi tiền | −2.183 | BCTC mã 315/323/314 | BCTC in tr.3–4 |
| Phải thu DH khác 242,0 theo sổ — **MỚI r2** | +1.813 | BCTC mã 215; không có dữ liệu suy giảm | BCTC in tr.1–2 |
| LN × 0,883 (trích quỹ không thuộc cổ đông) | — | EPS 2025 4.602 / (695,6 tỷ / 133,45 tr cp) | ĐHĐCĐ 2026 + BQ |
| Δ Long Thành tâm −25% | trục | lộ trình Cục HK 28/3/2027–25/3/2028; ~57% DT gắn khách quốc tế. **Độ lớn tâm = nhận định [UL]**, đã là trục xác suất 2 chiều | dd_SAS_20261026 §2–3 |
Tham số tự đặt [UL]: 5 mức Δ + trọng số; ±10% N0; nửa tác động 2027; trọng số g; β=1.

## 3. Cross-check Gordon/ROE (điều 10; Δ −25% vĩnh viễn, g 3%, không năm chuyển tiếp)
- Có thu nhập tài chính (vốn hoá cả 200,8/năm, không cộng tiền riêng): **37.150** · ROE 38,3%.
- Không thu nhập tài chính, cộng tiền + tài sản theo sổ: **33.112** · ROE vận hành (trừ tiền/TS) 71,2%.
Biến thể A cao hơn vì vốn hoá cổ tức đầu tư/lãi tiền gửi vô hạn với g 3% — không dùng.

## 4. Thanh khoản (điều 6)
| Cỡ | ADV250 0,59 tỷ (σ 2,07%) | ADV60 0,78 tỷ (σ 1,83%) |
|---|---|---|
| 10 / 20 / 40 tr (sleeve) | 0,27% / 0,38% / **0,54%** (40 tr = 6,8% ADV, trong vùng) | 0,21% / 0,29% / 0,41% |
| **5 tỷ (tham chiếu nhãn)** | **6,0%** — Q/ADV 847%, **NGOÀI vùng hiệu chỉnh**, 42–85 phiên @20–10% | 4,6% (638%, ngoài) |
Free float ~4,4% ⇒ cỡ 5 tỷ là phi thực tế với mã này; nhãn vẫn neo cỡ 5 tỷ theo quy ước, nhưng cùng nhãn (TRONG) ở cỡ sleeve.

## 5. Độ nhạy r theo lãi huy động (tâm trước CK, dịch cả trục r)
β=1: −100bp +7,8% · −50bp +3,7% · +50bp −3,4% · +100bp −6,4%. β=0,5: +3,7/+1,8/−1,7/−3,4%. Nhạy cao vì Gordon vô hạn.

## 6. ⚠️ WARNING pháp lý/quản trị (mang đủ cờ; không trừ base)
1. Mặt bằng ACV giao trực tiếp không đấu thầu (KL TTCP 2017); lô đất chưa hoàn tất thủ tục; truy thu tiền thuê đất 2015–2024 "hàng chục tỷ" hạch toán Q4/2025 [vietstock] — rủi ro truy thu thêm. Mặt bằng Long Thành gần như chắc phải đấu thầu.
2. Bên liên quan nhóm IPP (IPPG 24,98% / ACFC 14,89% / DAFC 4,92% / DAT 1,71%) vừa cổ đông vừa đối tác; lịch sử phải thu LD Nhà Việt ~292 tỷ, trích lập ~251 tỷ.
3. Free float ~4,4%; Chủ tịch nói tự vận hành miễn thuế "không thể kéo dài", đối tác mới chưa công bố điều khoản.
4. Kế hoạch chuyển HOSE + có thể phát hành thêm (chưa có lịch).
5. **Dữ liệu quản trị mới**: HĐQT bổ nhiệm TGĐ Dư Kim Thăng 03/08/2026; TGĐ cũ về ACV [cafef 04/08/2026]. Không thấy NQ HĐQT 10–11/2026 về Long Thành.
6. "Không thấy vụ việc hình sự/khởi tố liên quan SASCO": nguồn = DD 26/10/2026 (anninhthudo, thuonghieucongluan, vietstock) + web search 05/11/2026 (cafef, dnse, baophapluat) — không có kết quả mới.

## 8. Mốc đổi nhận định (hai chiều) + HARD ABANDON
| Mốc | Ngày chấm | Lên | Xuống |
|---|---|---|---|
| Kết quả thầu mặt bằng Long Thành | dự kiến trước 3/2027 | trúng miễn thuế/phòng chờ ⇒ Δ về +5…−10% | trượt gói chính ⇒ Δ −40…−55% (P10 ~23.800) |
| BCTC Q4/2026 | 31/01/2027 | LN vận hành Q4 ≥140, CFO > LNST | HTK phình + trích lập ⇒ N0 −10% |
| Thuyết minh phải thu DH 242 | BCTC năm 2026 | ký quỹ thu hồi được ⇒ giữ | suy giảm/không thu hồi ⇒ về bản "bỏ phải thu DH" (29.362) |
| Chuyển HOSE / phát hành | 2027 | ADV ≥3 tỷ ⇒ CK 5 tỷ ~2,7% | phát hành giá thấp ⇒ pha loãng |
**HARD ABANDON**: (a) ACV chấm dứt/thu hồi mặt bằng TSN trước 2027; (b) khởi tố/kết luận thanh tra chạm pháp nhân SASCO hoặc hợp đồng mặt bằng; (c) chuyển tiền/cho vay bên liên quan IPP không có bảo đảm. Sleeve 10–40 tr ⇒ không cần tranche (lưu ý 40 tr ≈ 6,8% ADV ⇒ chia ≥2 phiên).
**Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không khủng hoảng, giá trên tâm.

## 9. Mở
Thuyết minh V.5b (phải thu DH 242) · khoản bù DFS Q4/2025 · bên trả cổ tức đầu tư 195 · thầu Long Thành · HTK chưa trích lập · thiếu sector read · BQ `EPS`=0 mọi quý SAS. Chưa qua fundamental-skeptic.

## Phụ lục — đổi so với vòng 1
| Mục | Vòng 1 | Vòng 2 | Lý do |
|---|---|---|---|
| Phải thu DH 242 | không tính | theo sổ (+1.813 đ trước CK) | điều 3 |
| Trục g | cố định 3% | {2;3;4}% | điều 2 (biến nhạy nhất của Gordon) |
| Tâm | 3 kịch bản 30/45/25 | kỳ vọng lưới 135 ô | điều 4 |
| Thanh khoản | ADV250 | + ADV60, sleeve, cờ ngoài vùng hiệu chỉnh | điều 6 |
| Cờ | 4 | + nhân sự TGĐ 08/2026, nguồn+ngày tra | điều 5 |
