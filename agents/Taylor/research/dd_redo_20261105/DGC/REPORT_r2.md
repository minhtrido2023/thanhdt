# DGC — DD làm lại VÒNG 2 (05/11/2026, job `Taylor_20261105_020016`) — theo `../STANDARD_r2.md`

> NGHIÊN CỨU nội bộ, không phải khuyến nghị. Chưa qua fundamental-skeptic (Mike chạy). Mọi số: `calc/model_r2_out.json` (khoá md5 cùng mọi file
> upstream ở `calc/LOCK_r2_md5.txt` TRƯỚC khi đọc giá/ADV) → `SUMMARY.json` (bản vòng 1: `SUMMARY_r1.json`, `REPORT.md`). BCTC: BCTC HN Q3/2026 gốc
> (`../../dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md`). Phần §2–§4 (chất lượng LN, net cash, khách hàng) **không đổi** so `REPORT.md` vòng 1.

## 0. Kết luận
| Ba con số tách bạch (đ/cp) | Trước CK | Sau CK (5 tỷ, 0,71%) |
|---|---|---|
| **Tâm** = kỳ vọng trọng số của lưới kết cục | 45.088 | **44.767** |
| **P50 kết cục** | 44.953 | **44.633** |
| **Giá trị tại tham số trung tâm** (cơ sở, khai trường dừng, dự phòng hữu hạn 4 quý, NS sổ sách, m=1, Δr=0) | 40.806 | 40.515 |
| **P10 / P90 kết cục** | 32.752 / 57.511 | **32.518 / 57.101** |

- n = **810 kết cục**; min **23.462**, max 70.079 (sau CK). **12,2% trọng số nằm dưới giá**.
- Giá **04/11/2026: 33.450** ⇒ so tâm −25,3%, trên P10 +2,9% ⇒ **TRONG vùng (sát P10)**. Vòng 1: DƯỚI vùng (P10 34.557).
- **Nhãn đổi KHÔNG phải do đổi định nghĩa vùng** (cả hai vòng P10–P90): do thêm trục dự phòng lặp đối xứng (đuôi dưới dày hơn) + trục r.
- Phân phối là hỗn hợp **2 nhánh khai trường** (mỗi nhánh w 0,5): tâm nhánh dừng 38.225 / mở lại 51.950 (trước CK). **P90 do nhánh mở lại quyết định; P10 do nhánh dừng + lặp vĩnh viễn.** Tâm khác giá trị tại tham số trung tâm 4,3k chính vì trọng số mở lại 0,5 [UL].

## 1. Lưới (điều 1–2)
| Trục | Điểm (trọng số) | Chiều | Cơ sở |
|---|---|---|---|
| Kịch bản EBIT lõi 2027/28 | xấu 671/713 · cơ sở 1.008/1.126 · tốt 1.375/1.538 (0,3/0,5/0,2 [UL]) | hai | nền r12 `out_A_forecast.csv` |
| Khai trường 25/19B | dừng · mở lại giữa 2028 +1.000 LN gộp/năm (0,5/0,5 [UL]) | **lên** | r12 CFG_B |
| **Dự phòng môi trường (MỚI)** | một lần 0 · hữu hạn 4 quý · lặp vĩnh viễn 100 tỷ/quý (1/3 mỗi nhánh [UL]) | **xuống** | 2 quý liên tiếp 100 tỷ (BCTC); r12 §11 "chưa phân định"; tiền lệ TKV ~1.000+ tỷ/năm (ERRATA r11) |
| **Nghi Sơn (MỚI, đối xứng)** | −500 · 0 · +500 tỷ quanh sổ sách 1.408,8 (0,25/0,5/0,25 [UL]) | hai | biên độ = chênh 2.900 vs 2.400 (TBTCVN 17/09/2025) |
| Hệ số EBIT lõi | 0,8/0,9/1,0/1,1/1,2 (đều) | hai | [UL] |
| **Lãi huy động 12T (MỚI)** | −50/0/+50bp (0,25/0,5/0,25 [UL]), β=1 | hai | neo 7,4% CCTG 12M |

Tác động trục dự phòng (đ/cp, sau CĐKKS, lá chắn thuế 0 [UL]): hữu hạn **−915**, vĩnh viễn **−7.696**. Vòng 1 chỉ trừ dự phòng ở Q4 của kịch bản xấu ⇒ lệch một chiều so với trục mở lại khai trường — đã sửa.

**Trục loại khỏi base + bản song song CÓ trục (điều 2):**
| Bản | Cơ sở loại | Tâm sau CK | P10 / P50 / P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|
| **Base** | — | 44.767 | 32.518 / 44.633 / 57.101 | 12,2% | TRONG |
| + trục pháp lý (haircut tiền ròng 3/9/29%, w r12 0,2/0,5/0,3) | luật user 02/11: vụ án = WARNING | 41.837 | 29.355 / 41.761 / 54.552 | 21,2% | TRONG |
| khai trường dừng vĩnh viễn (w mở lại 0) | — (độ nhạy trọng số [UL]) | 37.953 | 29.771 / 37.513 / 45.756 | 24,4% | TRONG |
| dừng + pháp lý (cạnh xấu của cả hai trục liên quan vụ án) | — | 35.023 | 26.360 / 34.889 / 43.599 | **41,7%** | TRONG |
NPV độc lập Nghi Sơn r11 (−3.245/+2.524/+6.781 đ/cp) không đưa vào lưới: đầu vào [UL], ERRATA r11 chỉ cho dùng làm độ nhạy.

## 2. Base so với sổ sách (điều 3)
Tham số trung tâm **không trừ khoản nào ngoài nghĩa vụ đã ghi sổ**: dự phòng phải trả 200 (−511 đ/cp), quỹ KTPL 592,8 (−1.514), Nghi Sơn XDCB theo giá vốn (+3.599). Không còn haircut pháp lý, không còn −500 Nghi Sơn trong base (đã thành trục đối xứng). Mọi [UL]: trọng số kịch bản, trọng số khai trường, trọng số + lá chắn thuế dự phòng, trọng số NS, hệ số EBIT, trọng số trục r, g 3%, RONIC 20%, thuế dài hạn 15%.

## 3. Thanh khoản (điều 6)
| | ADV 250 phiên (03/11/25–04/11/26) | ADV 60 phiên (10/08–04/11/26) |
|---|---|---|
| GTGD trung vị | 86,75 tỷ | **18,32 tỷ** (HOSE hạn chế, chỉ phiên chiều) |
| CK 5 tỷ (tham chiếu nhãn) | **0,71%** (Q/ADV 5,8%, trong vùng hiệu chỉnh) | 1,11% (Q/ADV 27%, **ngoài** vùng hiệu chỉnh ~0,1–20% [UL]) |
| CK sleeve 10 / 20 / 40 triệu | 0,03% / 0,05% / 0,06% (Q/ADV <0,1%, dưới vùng — tác động thực do spread chi phối) | 0,05% / 0,07% / 0,10% |
Nhãn dùng cỡ 5 tỷ / ADV 250. Với ADV 60 nhãn không đổi (P10 sau CK = 32.752 × (1−1,11%) = 32.388 < giá).

## 4. Cross-check Gordon/ROE (điều 10)
LN mẹ 9T/26 năm hoá 1.689 tỷ, VCSH mẹ 13.073,9: (a) gồm lãi tiền gửi: ROE 12,9% ⇒ Gordon P/B **32.531 đ/cp**; (b) bỏ lãi tiền gửi, ROE trên VCSH hoạt động 21,7% + tiền ròng theo sổ ⇒ **44.551**. Đây là LN đáy (khai trường dừng, dự phòng 200) ⇒ mức sàn kiểm chéo, không phải ước tính. (a) thấp hơn vì vốn hoá tiền gửi ở ROE ≈ lãi gửi.

## 5. Pháp lý / quản trị — WARNING đầy đủ (điều 5; không vào base)
- Vụ án môi trường/khai thác/kế toán: CT HĐQT cũ Đào Hữu Huyền (18,38%) tạm giam 17/03/2026; khởi tố thêm TGĐ Lưu Bách Đạt, TV HĐQT Nguyễn Quốc Trung, PTGĐ Phùng Trọng Tú, GĐ mỏ KT25 Trịnh Quốc Khánh (07/2026). **Pháp nhân: chưa thấy quyết định khởi tố** — nguồn: quét 01–29/10 (`dd_DGC_20261029/inputs/legal_and_news_scan_20261029.md`) + WebSearch 05/11/2026 09:00 ICT (kết quả mới nhất ~08/2026, không có tin 10–11/2026). Điều 76 BLHS cho phép truy cứu pháp nhân tội 227/235; hình phạt 235 gồm đình chỉ có thời hạn.
- **Ý kiến ngoại trừ BCTC kiểm toán 2025**: 950,9 tỷ tồn kho chưa đủ bằng chứng + nội dung vụ án (VietnamFinance 06/10/2026) — **chưa đóng**.
- HOSE hạn chế giao dịch từ 26/05/2026 (chậm nộp BCTC kiểm toán), cảnh báo từ 30/06, cắt margin Q4/2026 — chưa thấy gỡ (phản ánh ở ADV 60).
- Dự phòng môi trường không được trừ thuế khi trích (TT48/2019, legal-vn 29/10).
- Công ty con: PAT — CT HĐQT miễn nhiệm sau khởi tố (28/07); TSB đổi lãnh đạo 05–06/10.
- Dữ liệu mới quan sát được: NQ HĐQT 34 (15/10/2026) Nghi Sơn — chạy thử Q4/2026, thương mại Q1/2027, **NQ không ghi vốn** ⇒ giữ trục ±500.

## 6. Độ nhạy r (sau CK, β=1, lấy trung bình các trục khác)
−100bp 47.192 · −50bp 45.903 · 0 44.767 · +50bp 43.685 · +100bp 42.724.

## 7. So vòng 1
Tâm sau CK 47.168 → **44.767 (−5,1%)**; P10 34.557 → 32.518; P90 58.796 → 57.101; nhãn DƯỚI → **TRONG (sát P10)**. Lý do: trục dự phòng lặp (bình quân 3 nhánh −2.870 đ/cp, đã tính phần CĐKKS); ngược chiều: bỏ dự phòng Q4 khỏi kịch bản xấu và bỏ −500 NS ở kịch bản xấu (thay bằng trục đối xứng); trục r (lồi). Cầu nối từng bước: chưa đo riêng.

## 8. Mốc đổi nhận định (điều 8)
- **Xấu đi**: BCTC Q4/2026 (~30/01/2027) trích thêm dự phòng ≥100 tỷ ⇒ dồn trọng số sang "lặp" (tâm về ~41k, giá rơi gần P25); quyết định khởi tố pháp nhân / đình chỉ nhà máy; biên gộp Q4 <16%; tổng mức Nghi Sơn 2.900 cùng phạm vi.
- **Tốt lên**: khai trường 25/19B mở lại (CBTT) ⇒ nhánh mở lại (tâm 51.950 trước CK); Q4 không dự phòng mới và biên ≥20% ⇒ dồn về "một lần"; BCTC kiểm toán 2025/2026 không ngoại trừ; gỡ hạn chế giao dịch; giá < P10 32.518 ⇒ DƯỚI vùng.
- **HARD ABANDON** (theo `calculated_fear_state_backstop.md` §3): khởi tố/kê biên pháp nhân hoặc rút giấy phép khai thác; BCTC kiểm toán lộ tiền/tồn kho bị thổi phồng (liên quan 950,9 tỷ ngoại trừ); đình chỉ/huỷ niêm yết thành hiện thực.
- **Tranche** (vị thế lớn): 3 phần theo §3 (T1 khi QUALIFY + giá ≤ book; T2 ổn định giá; T3 catalyst xác nhận: gỡ hạn chế / kiểm toán sạch).
- **Sleeve fear-buy**: DGC thuộc nhóm (a)+(b)/(d); §2 tiêu chí #2 (NN chi phối >50%) **KHÔNG đạt** (tư nhân) ⇒ **không đủ điều kiện sleeve fear-buy theo §2**; hồ sơ §6 cũ (AMBIGUOUS) không đánh giá lại ở đây.

## 9. Còn mở
Vốn Nghi Sơn 2.400/2.900 chưa có văn bản gốc; mọi trọng số [UL] ở §1; EBIT 2027–28 chưa cập nhật lưu huỳnh/P4 sau 28/10; LCTT lệch 48,23 tỷ; ngoại trừ kiểm toán 2025; room ngoại.

## 10. LOCK + tái lập (điều 9, 12)
`calc/LOCK_r2_md5.txt` gồm: model_r2_out.json, model_r2.py, model.py (vòng 1, import), common.py, common_r2.py, compare_r2.py, bq_px_liq_20261104.csv, _shared/wpct.py, deposit_rate_vn.py, data/deposit_rate_vn_events.csv, MIKE_EXTRACT_BCTC_Q3_2026.md, r12 out_A_forecast.csv, legal_and_news_scan_20261029.md, ERRATA_r11_skeptic_round5.md.
```
cd calc && $DNA_PYEXE -I model_r2.py && ../../_common_014127/lock_r2.sh DGC model.py <các file nguồn như trên> && $DNA_PYEXE -I ../../_common_014127/compare_r2.py DGC
```
Chạy 2 lần: `model_r2_out.json` và `SUMMARY.json` **trùng byte** (cmp, 05/11/2026).
