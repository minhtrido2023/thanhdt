# DGC — DD làm lại mùa BCTC Q3/2026 (05/11/2026, job `Taylor_20261105_014127`)

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua fundamental-skeptic (Mike sẽ chạy). Mọi số định giá lấy từ `calc/model_out.json`,
> `calc/bridge_out.json`, `SUMMARY.json` (khoá md5 `calc/LOCK_md5.txt` TRƯỚC khi đọc giá/ADV). Số BCTC: BCTC hợp nhất Q3/2026 gốc
> (ký 28/10/2026, chưa soát xét), bản chép `../../dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md`. src/ đã có Q3 ⇒ không tải lại.
> Sector read: `kb/data_registry/market-state/sector_read_fertilizer_dap_20261028.md` (Bobby, blind) — đọc lưu huỳnh/DAP, không phủ phốt pho vàng.

## 0. Kết luận (số chuẩn hoá liên mã)
| | Trước CK thanh khoản | Sau CK thanh khoản (5 tỷ, 0,71%) |
|---|---|---|
| Tâm (kỳ vọng trọng số) | 47.506 | **47.168** |
| P10 / P50 / P90 | 34.805 / 46.897 / 59.218 | **34.557 / 46.563 / 58.796** |

- Giá đóng cửa **04/11/2026: 33.450** (BQ `tav2_bq.ticker`). So tâm **−29,1%**, so P10 **−3,2%**, so P90 −43,1% ⇒ **DƯỚI vùng**.
- r = **13,5%** = neo 13,5% @ lãi huy động 12T hiệu dụng **7,4%** (CCTG 12M, mốc 02/11/2026, `deposit_rate_vn.effective_deposit_rate('2026-11-03')`); 04/11 vẫn 7,4% ⇒ r không đổi.
- ⚠️ **Nhãn phụ thuộc trọng số "mở lại khai trường"** (0,5, ước lượng). Nếu gán 0 (khai trường dừng vĩnh viễn): tâm sau CK **40.363**, P10/P90 **32.553 / 47.922** ⇒ giá **TRONG vùng**, sát P10 (+2,8%). Giá 33.450 ≈ kịch bản xấu + khai trường dừng (33.796 trước CK).
- Lệch so zone cũ (A7–B7 Ke 13%, 33.514–38.832, trung điểm 36.173): **+30,4%** — phần lớn do đổi KHUNG (mục 8), không do BCTC mới.

## 1. Giả thuyết kiểm chứng
| Giả thuyết | Kết quả |
|---|---|
| LN Q3 phục hồi so Q2 | **Nửa đúng.** LNST mẹ Q3 478,2 tỷ vs Q3/25 751,6 (−36%); biên gộp Q3 20,5% vs 31,1% cùng kỳ. 9T mẹ 1.267,1 (−47%). |
| Tiền ròng lớn bảo vệ giá | **Đúng.** Tiền + HTM 9.761,2 − vay 1.391,0 = **8.370,2 tỷ (22.040 đ/cp)** sau khi đã chi cổ tức 9T 4.213 tỷ. |
| Nghi Sơn là gánh nặng giá trị | **Không có cơ sở ở base** (luật 03/11): XDCB 1.408,8 ghi theo giá vốn, NPV=0. |

## 2. Chất lượng lợi nhuận (BCTC HN Q3/2026)
- DT Q3 2.469,5 (−12,3% yoy); giá vốn 1.963,1; LN gộp 506,4. 9T: DT 7.009,5 (−17,7%), LN gộp 1.451,2 (biên 20,7% vs 33,3%).
- DT tài chính Q3 209,6 (9T 576,1) — lãi tiền gửi trên số dư ~10–11 nghìn tỷ; **không đưa vào giá trị lõi** (tiền ròng cộng riêng).
- Dự phòng phải trả **200 tỷ** ghi vào giá vốn (Q2 100 + Q3 100), nội dung "phục hồi/môi trường"; một lần hay lặp: **chưa phân định**.
- Giải trình: khai trường 25 tạm dừng phục vụ điều tra ⇒ dùng quặng mua ngoài; lưu huỳnh, điện, than cốc, NH3 tăng. Bobby: lưu huỳnh TQ đã −38% từ đỉnh tháng nhưng ME FOB chỉ −5…−10% ⇒ đỡ chi phí chậm.
- Thuế hiệu dụng 9T **13,2%**; CĐKKS 7,5% LNST.

## 3. Bảng cân đối / net cash thật (30/09/2026)
- Tiền 230,2 + HTM 9.531,0 (dự thu 93,2) − vay NH 1.391,0 = **8.370,2**. Không vay dài hạn. Không có tiền ứng khách cần tiêu.
- Nghĩa vụ trừ trong định giá: dự phòng 200,0; quỹ KTPL 592,8 ⇒ phần ngoài lõi = 8.370,2 − 200 − 592,8 + Nghi Sơn 1.408,8 = 8.986,2 tỷ, ×(1−2,97% VCSH CĐKKS) = **22.958 đ/cp** (`parts.other_ps_coso`).
- Tồn kho 2.085,9 (giảm 374 trong Q3), dự phòng giảm giá chỉ 0,29 tỷ. Phải thu NH 811,8 (khoản cho vay 819 đã thu hồi).
- CFO 9T **+755,6** (9T/25 1.250,2). ⚠️ LCTT bản gốc lệch nội bộ 48,23 tỷ ở khối đầu tư (lỗi in hoặc thiếu dòng).

## 4. Ghi nhận DT, khách hàng, cổ đông, thanh khoản
- DT bán hàng ghi khi giao (sản xuất hàng hoá); Q4 không có tính mùa vụ đặc biệt đã đo.
- Cổ đông lớn (30/09, 1 nguồn báo chí): Đào Hữu Huyền 18,38%, Ngô Thị Ngọc Lan 6,64%, Đào Hữu Kha 5,97% ⇒ free float ≈ **69,0%**. Room ngoại: chưa kiểm.
- Thanh khoản (BQ 250 phiên 03/11/2025–04/11/2026): GTGD trung vị **86,7 tỷ/ngày**, σ ngày 2,97%. Vị thế 5 tỷ thoát **0,6/0,4/0,3 phiên** ở tham gia 10/15/20%; CK thanh khoản Y=1: **0,71%** (Y 0,5/1,5: 0,36%/1,07%); 10 tỷ: 1,01%. ⚠️ HOSE hạn chế (chỉ phiên chiều) ⇒ thanh khoản tương lai có thể thấp hơn chuỗi 250 phiên.

## 5. Pháp lý / quản trị — WARNING (không loại, không định lượng trong base)
- Vụ án môi trường/khai thác: Chủ tịch HĐQT cũ Đào Hữu Huyền (18,38%) là 1 trong 14 bị can, đã miễn nhiệm 08/05/2026; khai trường 25 tạm dừng; 19B không có thông tin (`dd_DGC_20261029/inputs/legal_and_news_scan_20261029.md`).
- Khung hình phạt pháp nhân Điều 235 BLHS: phạt 6–40 tỷ hoặc đình chỉ có thời hạn; rủi ro lớn nhất là **đình chỉ nhà máy** (không định lượng). Rủi ro "scandal di cư": dự phòng 200 tỷ trong giá vốn — theo dõi có lặp lại Q4.
- Base cũ trừ haircut pháp lý 3/9/29% trên tiền ròng — **đã bỏ khỏi base** theo luật pháp lý = WARNING.

## 6. Định giá
**Cấu trúc** (`calc/model.py`): giá trị mẹ = lõi × (1−7,47%) + (tiền ròng − dự phòng − quỹ KTPL + Nghi Sơn sổ sách [+ vượt dự toán ở kịch bản xấu]) × (1−2,97%).
Lõi = DCF FCFF: Q4/2026 (EBIT 9T/3), 2027, 2028 rồi Gordon cuối 2028 (g 3%, RONIC 20%, thuế dài hạn 15% — đều **ước lượng**; thuế 2026–28 = 13,2% đo). Tỉ trọng terminal ở cơ sở/dừng: **77,9%**.

| Kịch bản (w) | EBIT lõi 2027 / 2028 | Khai trường dừng | Mở lại giữa 2028 (+1.000 LN gộp/năm) |
|---|---|---|---|
| Xấu (0,3): dự phòng lặp 100 tỷ/quý; Nghi Sơn vượt 500 tỷ | 671 / 713 | 33.796 | 47.503 |
| Cơ sở (0,5) | 1.008 / 1.126 | 41.721 | 55.428 |
| Tốt (0,2) | 1.375 / 1.538 | 48.265 | 61.972 |

(trước CK thanh khoản, đ/cp). EBIT 2027–28 lấy từ nền dự báo r12 (`out_A_forecast.csv`, biên gộp 14,5–19%) — **ước lượng** của DD cũ, giữ vì là phân tích chi phí quặng/lưu huỳnh đã qua phản biện; trọng số mở lại 0,5/0,5 **ước lượng** (không có cơ sở phân định).
- Nghi Sơn: base NPV=0, 1.408,8 tỷ = 3.599 đ/cp. Khoản giảm trừ duy nhất (−500 tỷ, chỉ kịch bản xấu) có **cơ sở dữ liệu**: Thời báo Tài chính VN 17/09/2025 nêu tổng mức 2.900 vs 2.400 tỷ.
- **Lưới P10–P90**: 3 kịch bản × 2 trạng thái khai trường × hệ số EBIT lõi 5 điểm 0,8/0,9/1,0/1,1/1,2 (đều) = **n 30**, trọng số ô = w_kb × w_khai trường / 5.
- Độ nhạy trọng số khai trường (tâm trước CK): w_mở lại 0 / 0,2 / 0,5 / 0,8 = **40.652 / 43.394 / 47.506 / 51.618**.

## 7. Độ nhạy r (lãi huy động), sau CK thanh khoản
| Δ lãi huy động 12T | −100bp | −50bp | 0 | +50bp | +100bp |
|---|---|---|---|---|---|
| β=1,0 | 49.814 (+5,6%) | 48.424 (+2,7%) | 47.168 | 46.027 (−2,4%) | 44.986 (−4,6%) |
| β=0,5 | 48.424 | 47.780 | 47.168 | 46.584 | 46.027 |

g×r (trước CK): g 2/3/4% ở r 12,5% = 49.190/50.171/51.402; r 14,5% = 44.863/45.309/45.856. Giá trị ít nhạy r vì 48% tâm là phần ngoài lõi (tiền ròng + Nghi Sơn sổ sách).

## 8. Phụ lục — ĐỔI gì so với DD cũ (zone 30/10: 33.514–38.832, không có tâm) và vì sao (lệch +30,4% > 10%)
Cầu nối trung điểm cũ 36.173 → tâm mới trước CK 47.506 (`calc/bridge_out.json`):
| Bước | đ/cp | Lý do |
|---|---|---|
| Gán trọng số 0,5 cho mở lại khai trường (cũ: A7/B7 không chọn; B7 chỉ tính +500 LN gộp năm 2028) | **+6.854** | Luật tâm = kỳ vọng trọng số; mở lại tính đủ từ 2029 |
| Nghi Sơn: −447 (ròng r12) → sổ sách 3.599, trừ vượt dự toán kịch bản xấu (−383 bình quân) | **+3.663** | Luật dự án mới base NPV=0 (03/11) |
| Bỏ haircut pháp lý tiền ròng (bình quân 13,8%) | **+2.951** | Pháp lý = WARNING |
| Phương pháp (DCF Gordon thay P/E 6–8), r 13,5% vs 13%, thuế/CĐKKS | −2.135 | phần dư |
Nguyên nhân chính: **khung (trọng số khai trường + Nghi Sơn + haircut)**, không phải số BCTC mới.

## 9. Mốc khoá trước + điều kiện đổi nhận định (hai chiều)
- **Xấu đi** (nhãn có thể sang TRONG/TRÊN vùng): (a) BCTC Q4/2026 (hạn ~30/01/2027) trích thêm dự phòng ≥100 tỷ ⇒ chuyển trọng số sang kịch bản lặp; (b) quyết định đình chỉ/khởi tố pháp nhân; (c) biên gộp Q4 < 16%; (d) thông báo tổng mức Nghi Sơn 2.900 cho cùng phạm vi.
- **Tốt lên**: (a) khai trường 25 hoặc 19B mở lại (CBTT) ⇒ w_mở lại → 1 (tâm trước CK ~55–62k ở cơ sở/tốt); (b) biên gộp Q4 ≥ 20% không có dự phòng mới; (c) lãi huy động 12T giảm ≥50bp (+2,7%).
- Tiêu chí §2.5 discretionary: hồ sơ riêng, không làm ở đây.

## 10. Còn mở
Vốn Nghi Sơn 2.400/2.900 chưa có văn bản gốc; trọng số mở lại khai trường; EBIT 2027–28 chưa cập nhật giá lưu huỳnh/P4 sau 28/10; LCTT lệch 48,23 tỷ; room ngoại; free float từ 1 nguồn báo chí.

Tái lập: `cd calc && $DNA_PYEXE -I model.py && md5sum model_out.json > LOCK_md5.txt && $DNA_PYEXE -I ../../_common_014127/compare.py DGC && $DNA_PYEXE -I bridge.py`.
