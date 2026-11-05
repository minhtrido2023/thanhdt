# PVT — DD làm lại VÒNG 2 (05/11/2026, job `Taylor_20261105_020016`) — theo `../STANDARD_r2.md`

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua fundamental-skeptic. Số: `calc/model_r2_out.json` (khoá `calc/LOCK_r2_md5.txt`) → `SUMMARY.json`
> (vòng 1: `SUMMARY_r1.json`, `REPORT.md`). BCTC HN Q3/2026 + CV 983 (`../../dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt`); lịch sử BQ `ticker_financial`. §2–§4 vòng 1 không đổi.

## 0. Kết luận
| Ba con số (đ/cp) | Trước CK | Sau CK (5 tỷ, 0,67%) |
|---|---|---|
| **Tâm** (kỳ vọng trọng số lưới kết cục) | 17.794 | **17.675** |
| **P50 kết cục** | 17.542 | **17.425** |
| **Giá trị tại tham số trung tâm** (cơ sở, m=1, Δr=0, không mua thêm tàu) | 18.618 | 18.493 |
| **P10 / P90 kết cục** | 12.618 / 23.291 | **12.533 / 23.135** |

- n = **90 kết cục**; min 9.670, max 28.070. **78,3% trọng số nằm dưới giá**.
- Giá **04/11/2026: 21.000** ⇒ so tâm +18,8%, dưới P90 −9,2% ⇒ **TRONG vùng (phía trên, trên P75 20.624)**. Vòng 1: TRONG — nhãn không đổi.
- ⚠️ **Hai bản song song cho TRÊN vùng** (§1): neo kế hoạch 5 năm của chính HĐQT (tâm 11.456) và ROE bỏ lãi tiền gửi (tâm 14.219). Nhãn base dựa vào ROE lịch sử 13,15% gồm lãi tiền gửi.
- Không có nhánh trọng số nhỏ quyết định riêng P10/P90.

## 1. Lưới (điều 1–2)
| Trục | Điểm (trọng số) | Chiều | Cơ sở |
|---|---|---|---|
| LN mẹ 2027 / chu kỳ cước | 1.000/1.250/1.500; hệ số ROE 0,85/1,0/1,1 (0,35/0,45/0,20 [UL]) | hai | DD 29/10 §7 + Bobby blind |
| ROE giữa chu kỳ | 0,8…1,2 × 13,15% (trung vị `ROE_Trailing` Q4 2015–25, BQ) | hai | [UL] hệ số |
| Lãi huy động 12T | −50/0/+50bp (0,25/0,5/0,25 [UL]) | hai | neo 7,4% |
| **Mua tàu phần capex 2026 còn lại (MỚI)** | mua 2.465 tỷ / không (0,5/0,5 [UL]) × NPV xấu −30% / cơ sở 0 / tốt +30% [UL] (phần mẹ 80,4%) | hai | ĐHĐCĐ 2026: ≤5 tàu, 3.445 tỷ; 9T đã tăng nguyên giá 979,6 [TM12]; Bobby mục 7 (dồn mua ở đỉnh giá tàu cũ trước 31/12/2026) |

**Song song (điều 2, 5, 10):**
| Bản | Tâm sau CK | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|
| **Base** | 17.675 | 12.533 / 17.425 / 23.135 | 78,3% | TRONG |
| **Neo kế hoạch 5 năm NQ HĐQT** (LN mẹ 2027–30 = 933 tỷ/năm, ROE 9,46%) | 11.456 | 7.414 / 11.122 / 15.496 | 100% | **TRÊN** |
| **ROE bỏ lãi tiền gửi hiện tại** (215 tỷ/năm phần mẹ ⇒ ROE 10,97%) | 14.219 | 9.695 / 13.955 / 19.004 | 97,0% | **TRÊN** |
| NPV tàu = 0 mọi kịch bản (như vòng 1) | 17.761 | 13.133 / 17.631 / 22.878 | 79,8% | TRONG |
Cách tính neo kế hoạch: (6.750 [giữa 6.500–7.000] − 2026 ước 9T 1.581,8 × 4/3 [UL]) / 4 × (1 − CĐKKS 19,6%) = 933. Không đưa vào base: mục tiêu ban điều hành thường thận trọng (kế hoạch 2026 1.200 HN vs 9T thực 1.581,8) và không thay được ROE lịch sử 11 năm — nhưng là **dữ liệu quan sát được kéo xuống**, nên báo cạnh nhãn.
Loại không định lượng: TT99 (độ lớn chưa xác định), phát hành cổ phiếu tài trợ đội tàu (NQ 5 năm nêu là nguồn vốn, chưa có đợt cụ thể).

## 2. Base so với sổ sách (điều 3)
Không có khoản lệch sổ: nợ ròng 619,3 nằm trong LN sau lãi vay và VCSH (không trừ lần nữa); tàu mới NPV 0 tại tham số trung tâm. [UL]: LN 2027 + trọng số, hệ số ROE, g 3%, trục r, xác suất mua, biên độ NPV tàu, ước LN 2026 trong neo kế hoạch.

## 3. Thanh khoản (điều 6)
| | ADV 250 phiên | ADV 60 phiên |
|---|---|---|
| GTGD trung vị | 94,60 tỷ | 128,76 tỷ |
| CK 5 tỷ (nhãn) | **0,67%** (Q/ADV 5,3%, trong vùng hiệu chỉnh) | 0,51% |
| CK sleeve 10 / 20 / 40 triệu | 0,03% / 0,04% / 0,06% (dưới vùng hiệu chỉnh — spread chi phối) | 0,02% / 0,03% / 0,05% |

## 4. Cross-check Gordon/ROE (điều 10)
BVPS mẹ 19.066. Gồm lãi tiền gửi: ROE 13,15% ⇒ P/B Gordon 0,967 ⇒ **18.433 đ/cp**. Bỏ lãi tiền gửi hiện tại: ROE 10,97% ⇒ P/B 0,759 ⇒ **14.467**. PVT nợ ròng nên lãi gửi và lãi vay cùng thuộc cổ đông — bản bỏ lãi gửi là cận dưới kiểm chéo, không phải base; nhưng cả hai đều < giá 21.000.

## 5. Pháp lý / quản trị — WARNING (điều 5)
- Thay TGĐ 2 lần trong 4 tháng (Trần Ngọc Nguyên miễn nhiệm 01/07; Nguyễn Thanh Bình từ 03/08/2026), lý do không công bố.
- Bên PVN 22,4% DT 9T (Q3 31,7%); phải thu đơn vị PVN 1.144,7 tỷ (+130%).
- TT99/2025 + TT43/2026: ngừng trích trước sửa chữa lớn từ 01/01/2026 ⇒ biên 2026 thiên lệch tăng, độ lớn chưa xác định; "điều chỉnh khác" LCTT 9T/25 155,7 tỷ chưa giải thích.
- **Ý kiến kiểm toán 2025 / soát xét H1/2026: chưa có trong tay** (DD 29/10) — ngoại trừ/nhấn mạnh: chưa kiểm.
- Phải thu cũ liên quan Huỳnh Thị Huyền Như 73,1 tỷ đã dự phòng 100%; Chủ tịch đăng ký bán 200.000 cp rồi không bán (03–04/2026).
- Chưa thấy khởi tố/xử phạt: DD 29/10 + WebSearch 05/11/2026 09:00 ICT (không thấy NQ mua tàu cụ thể tháng 10–11/2026).
- Dữ liệu mới quan sát được: NQ HĐQT kế hoạch 2026–2030 (mekongasean 26/05/2026; số/ngày NQ chưa xác định) — đưa vào song song; ĐHĐCĐ 2026 capex ≤5 tàu 3.445 tỷ — đưa vào trục mua tàu.

## 6. Độ nhạy r (sau CK)
−100bp 19.479 · −50bp 18.521 · 0 17.675 · +50bp 16.868 · +100bp 16.149 — nhạy r nhất trong 4 mã; −100bp vẫn dưới giá.

## 7. So vòng 1
Tâm 17.751 → **17.675 (−0,4%)**; P10 13.001 → 12.533; P90 22.965 → 23.135; nhãn **TRONG → TRONG**. Trục r và trục mua tàu đối xứng nới hai đuôi; tâm gần như không đổi (NPV tàu kỳ vọng −0,3×0,35 + 0,3×0,2 = −4,5% × 0,5 xác suất mua).

## 8. Mốc đổi nhận định (điều 8)
- **Xấu đi** (sang TRÊN vùng): LNST mẹ Q4/2026 < 300 tỷ; tác động TT99 > 150 tỷ; mua tàu lớn ở đỉnh trước 31/12/2026 không có hợp đồng đầu ra; Bobby F2 (30/09/2027) ⇒ LN mẹ 9T/27 ≤ 900; ý kiến kiểm toán có ngoại trừ; giá > P90 23.135.
- **Tốt lên**: Bobby F1 (31/03/2027): BDTI ≤4.200 mà biên vận tải Q1/27 ≥20%; công bố ≥60% ngày tàu TC dài hạn tới 2028; lãi huy động −100bp (+10,2%); giá < P10 12.533 ⇒ DƯỚI vùng.
- **HARD ABANDON**: kiểm toán lộ doanh thu/tài sản bị thổi phồng; phát hành cổ phiếu dưới book để mua tàu; PVN ép giao dịch liên quan bất lợi.
- Tranche: không áp dụng. **Sleeve fear-buy §2.5: KHÔNG đủ điều kiện** — không có khủng hoảng, LN ở đỉnh; P/B 1,10 > trung vị lịch sử 0,91.

## 9. Còn mở
Ý kiến kiểm toán 2025 / soát xét H1; định lượng TT99; TC/spot + đáo hạn hợp đồng; số/ngày NQ kế hoạch 5 năm; room ngoại.

## 10. LOCK + tái lập
`calc/LOCK_r2_md5.txt`: model_r2_out.json, model_r2.py, model.py (vòng 1, import), common.py, common_r2.py, compare_r2.py, bq_px_liq_20261104.csv, _shared/wpct.py, deposit_rate_vn.py, data/deposit_rate_vn_events.csv, calc/bq_hist_out.csv, dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt, dd_PVT_20261029/REPORT.md.
`cd calc && $DNA_PYEXE -I model_r2.py && ../../_common_014127/lock_r2.sh PVT model.py bq_hist_out.csv <nguồn> && $DNA_PYEXE -I ../../_common_014127/compare_r2.py PVT` — chạy 2 lần **trùng byte** (cmp).
