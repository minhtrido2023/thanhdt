# PVP — DD làm lại VÒNG 3 (08/11/2026, job `Taylor_20261108_164335`) — áp đính chính fundamental-skeptic 08/11

Nguồn đính chính: `../TOP5C_CORRECTIONS_20261108.md` mục PVP. Chuẩn: `../STANDARD_r2.md`. Calc: `calc_r3/` (`pvp_r3.py` không đọc giá → LOCK → `pvp_r3_compare.py` đọc giá). Giá tham chiếu: đóng cửa 06/11/2026 = **18.000** (BQ `tav2_bq.ticker`, `calc_r3/px_pvp_r3_20261106.csv`). Không đặt lệnh, không sửa `kb/dd_price_zones.json`.

## 0. Kết luận
| | r2 (05/11, giá 18.400) | **r3 (giá 18.000)** |
|---|---|---|
| Tâm (kỳ vọng lưới, sau CK 5 tỷ) | 22.366 | **23.099** (+733) |
| P10 / P50 / P90 kết cục | 12.702 / 22.377 / 32.834 | **13.799 / 23.982 / 30.338** |
| % trọng số dưới giá | 30,6% (ở 18.000: 29,8%) | **20,5%** |
| Nhãn | TRONG | **TRONG vùng** (giá dưới tâm 22,1%) |

- **Nhãn phụ thuộc gần như hoàn toàn vào giả định NPV tàu mới** (nói thẳng): NPV0 mọi nhánh ⇒ P10 20.474 > 18.000 ⇒ **DƯỚI**; −30% vô điều kiện ⇒ tâm 18.935 ≈ giá. Headline giữ −30% chỉ ở nhánh xấu (dấu có dữ liệu IRR 7,67% < hurdle 11%, độ lớn [UL]).
- P10 do một nhánh quyết định: nhánh cước xấu (w 0,275) × mua cả hai tàu (NPV −30%).
- Không đủ điều kiện sleeve fear-buy §2.5 (không có khủng hoảng; đỉnh chu kỳ cước) — giữ nguyên r2.

## 1. Kiểm từng đính chính (calc, không chép)
| # | Đính chính skeptic | Kết quả kiểm | Áp? | Δ tâm sau CK |
|---|---|---|---|---|
| 1 | Trọng số cước 0,40/0,45/0,15 → 0,275/0,45/0,275 | Đúng: mức trung tâm 400 < 561 năm hoá 9T (421,1 tỷ 9T [Q3 p10,13-14]); lệch xuống thêm bằng trọng số là đếm chu kỳ lần 2, chỉ có nhận định Bobby | Có | **+2.411** |
| 2 | Cắt +30% NPV tàu nhánh tốt | Đúng: không có IRR/dữ liệu cho chiều lên. Giữ −30% nhánh xấu. Kiểm thêm độ lớn: niên kim 20 năm IRR 7,67% chiết khấu 13,5% ⇒ −32% (25 năm −42%), nhưng tài trợ vay 70% lãi thấp hơn Ke ⇒ độ lớn thật không xác định ⇒ để [UL] và báo song song | Có | **−1.579** |
| 3 | FSO chiết khấu 10% → r 13,5% | Đúng: spread 2,6pp không nguồn; bên thuê là công ty mẹ, đã điều chỉnh giá cước (BB 03/06/2025), phụ lục gia hạn chưa ký [H1 tr.31] | Có | **−453** |
| 4 | Thiếu VLĐ ròng ngoài tiền +37,0 tỷ | Đúng, kiểm trên ảnh CĐKT 30/09/2026: TS NH 2.317,940 − tiền 718,158 − HTM 1.015,871 = **583,910**; nợ NH 1.024,314 − vay 134,947 − cổ tức 109,526 − dự phòng 232,937 = **546,903** ⇒ **+37,007 tỷ = +357 đ/cp** trước CK | Có | **+350** |
| 5 | Trục FSO 177 tỷ giữ 0,5/0,5; 25.173 là ô lưới không phải tâm | Đồng ý. Biến thể "luôn thành tiền" tâm 23.738, "không bao giờ" 22.460 | Giữ trục | 0 |
| 6 | Độ nhạy 2 chiều phế liệu vs lên đà TT99 | Không có dữ liệu LDT/chi phí ⇒ độ nhạy đơn vị: **±117 đ/cp mỗi 1 tr USD** thu/chi cuối đời tàu hiện hữu | Độ nhạy | 0 |
| 7 | WARNING phụ lục gia hạn FSO 2036 chưa ký | Đúng (H1 tr.31: HĐ cũ đến 17/05/2026; BB 03/06/2025 thống nhất giá+hạn đến 31/12/2036; "đang trong quá trình hoàn tất thủ tục để ký phụ lục") ⇒ WARNING + biến thể bỏ dòng tiền >5 năm: tâm 22.489 | WARNING + độ nhạy | 0 |
| 8 | Giá 06/11 = 18.000 | Đúng (BQ). r2 ở giá mới: 29,8% dưới giá, TRONG | — | — |

Khớp skeptic: tổng d1+d2 = +832 (skeptic +1.694 −861 = +833; chênh do thứ tự áp — skeptic cắt trước, tôi đối xứng trước); d3 −453 (=), d4 +350 (skeptic +349). Tâm r3 23.099 vs điểm skeptic 23.199: chênh −100 do CK cập nhật ADV đến 06/11 và làm tròn. Phân vị r3 13.799/23.982/30.338 vs skeptic 13.886/24.085/30.431 — cùng hình dạng.

**Không áp** điều chỉnh 5F "A" (EBITDA × 0,904, ADDENDUM_5F): proxy chu kỳ là EBITDA TỔNG công ty, chiều sai lệch chưa đo, và cộng vào đính chính 1 sẽ đếm chu kỳ lần nữa ⇒ để biến thể (tâm 21.858, TRONG).

## 2. Lưới r3 + giả định khoá (`calc_r3/assumptions_r3.json`)
Kết cục = cước xấu/cơ sở/tốt (0,275/0,45/0,275; EBITDA đội tàu 300/400/550) × tuổi đời còn lại 4–8 năm × lãi huy động −50/0/+50bp (0,25/0,5/0,25; FSO cùng trục) × mua tàu cả hai 116 / chỉ #2 56,5 / không (0,50/0,35/0,15 [UL]) × 177 tỷ FSO năm 1 thành tiền/không (0,5/0,5 [UL]). **n = 270**, Σw = 1. r = 13,5% + 1,0×(7,40% − 7,40%) = **13,5%** (dep 12T hiệu dụng 06/11 = 03/11).

Ba con số: tâm 23.099 · P50 23.982 · giá trị tại tham số trung tâm (cơ sở, 6 năm, Δr=0, mua cả hai, FSO thành tiền) 25.066. Tâm nhánh trước CK: xấu 15.695 / cơ sở 24.740 / tốt 29.519. Phân phối hai đỉnh; min 9.559, max 33.620.

Cấu phần tại tham số trung tâm (tỷ): tiền ròng sau cổ tức 1.016,2 · VLĐ khác 37,0 · FSO 712,0 · đội tàu 1.340,5 · dự phòng sửa chữa −232,9 · chi phí công ty −220,7 · tàu mới 0.

Base so sổ sách (điều 3): mọi khoản lệch có cơ sở — cổ tức phải trả 109,5 (−1.056 đ/cp), dự phòng 232,9 (−2.246), chi phí công ty 10 năm (−2.128, 10 năm [UL]), VLĐ khác +357, NPV tàu mới kỳ vọng −1.612 (dấu: IRR [AGM p44]; độ lớn [UL]).

## 3. Headline và các biến thể song song (sau CK 5 tỷ, giá 18.000)
| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| **HEADLINE r3** | **23.099** | **13.799** | **23.982** | **30.338** | **20,5%** | **TRONG** |
| Trọng số Bobby 0,40/0,45/0,15 | 21.405 | 12.600 | 22.285 | 27.837 | 29,8% | TRONG |
| NPV tàu ±30% đối xứng (r2) | 24.678 | 13.799 | 23.982 | 36.375 | 20,5% | TRONG |
| NPV tàu = 0 mọi nhánh | 24.678 | 20.474 | 23.982 | 30.338 | 0,0% | **DƯỚI** |
| NPV tàu −30% vô điều kiện | 18.935 | 13.087 | 18.276 | 25.507 | 47,5% | TRONG |
| FSO chiết khấu 10% (r2) | 23.552 | 14.238 | 24.439 | 30.786 | 19,3% | TRONG |
| 177 tỷ FSO luôn thành tiền | 23.738 | 14.393 | 25.066 | 31.326 | 19,5% | TRONG |
| 177 tỷ FSO không thành tiền | 22.460 | 13.123 | 23.788 | 30.050 | 21,5% | TRONG |
| Bỏ dòng FSO > 5 năm (phụ lục chưa ký) | 22.489 | 13.200 | 23.363 | 29.727 | 22,1% | TRONG |
| Bỏ VLĐ khác (r2) | 22.749 | 13.449 | 23.633 | 29.988 | 21,6% | TRONG |
| 5F "A": EBITDA × 0,904 | 21.858 | 12.718 | 22.749 | 28.503 | 22,8% | TRONG |
| +1 tr USD phế liệu (đơn vị) | 23.216 | 13.886 | 24.108 | 30.441 | 20,5% | TRONG |

**Giá ngụ ý (18.000)**: EBITDA đội tàu phẳng mọi kịch bản ≈ **250 tỷ/năm** (45% mức 561 năm hoá 9T/26); hoặc mức 300/400/550 × 0,605 (182/242/333); hoặc NPV tàu mới vô điều kiện **−35%**. (Skeptic viết "~174 tỷ" — định nghĩa khác: chỉ dịch kịch bản cơ sở; con số của tôi là EBITDA phẳng, giữ mọi trục khác.)

## 4. Cross-check Gordon/ROE (điều 10)
Không áp dụng: SOTP dòng tiền chạy cạn (tiền ròng + FSO hợp đồng + niên kim đội tàu theo tuổi đời), không có giá trị tăng trưởng ⇒ moat (5F: NONE, `SUMMARY_5F.json`) không tác động; RONIC không dùng. Lãi tiền gửi nằm trong tiền ròng cộng riêng, không tính đôi.

## 5. Pháp lý / quản trị — WARNING
- **MỚI (đính chính 7)**: phụ lục gia hạn hợp đồng FSO Đại Hùng Queen đến 31/12/2036 **chưa ký**; HĐ cũ hết 17/05/2026; BB 03/06/2025 đã thống nhất giá+hạn mới; đối tác là công ty mẹ PVTrans, từng điều chỉnh giá cước [H1 tr.31]. Cam kết 1.163,7 tỷ trong BCTC tính theo giá/hạn chưa ký.
- Mua tàu 116 tr USD (~1,55× vốn hoá) đã duyệt ĐHĐCĐ 23/06; chưa ký thoả thuận nào với đối tác [H1 tr.31]; ĐHĐCĐ bất thường gia hạn 2 lần (≤30/11/2026), văn kiện chưa công bố (tra 05/11; chưa tra lại trong vòng này).
- IRR Aframax #2 7,67% < IRRmin 11% [AGM p44]; NPV vốn CSH dương chỉ nhờ đòn bẩy vay 70%.
- Bên liên quan 63,3% DT 6T (PVTrans, BSR, LPG VN); GD liên quan "theo thực tế phát sinh" không trần (NQ 16/HĐQT 18/08/2026).
- Đổi GĐ (23/06), PGĐ (12/08); free float ~28%.
- Chưa thấy khởi tố/điều tra (DD 29/10 + WebSearch 05/11/2026); kiểm toán bán niên chấp nhận toàn phần.

## 6. Cầu r2 → r3 (tâm sau CK)
| Bước | Tâm | Δ | Lý do |
|---|---|---|---|
| r2 công bố (CK ADV đến 04/11) | 22.366 | — | |
| Control r2 (center_pre 22.822,73 tái lập trùng), CK ADV đến 06/11 | 22.370 | +4 | chỉ đổi CK |
| Đ1 trọng số đối xứng | 24.781 | +2.411 | xem §1 |
| Đ2 cắt +30% NPV tàu nhánh tốt | 23.202 | −1.579 | |
| Đ3 FSO chiết khấu Ke | 22.749 | −453 | |
| Đ4 + VLĐ khác 37,0 tỷ | 23.099 | +350 | |
| r 06/11 | 23.099 | 0 | dep không đổi |

## 7. Thanh khoản
ADV (trung vị Price×Volume) 250 phiên 8,27 tỷ (σ ngày 2,55%), 60 phiên 21,58 tỷ (σ 2,90%). CK cỡ tham chiếu 5 tỷ: **1,98%** (ADV250; Q/ADV 60% — **ngoài vùng hiệu chỉnh** luật căn bậc hai 0,1–20%), 1,40% (ADV60). Cỡ sleeve thật: 10 tr 0,09% · 20 tr 0,13% · 40 tr 0,18% (trong vùng). Ở cỡ 40 tr: tâm 23.525, P10 14.053, P90 30.897 — TRONG. Nhãn theo cỡ 5 tỷ.

## 8. Mốc đổi nhận định
- **Xấu đi**: văn kiện ĐHĐCĐ bất thường duyệt giá tàu > khả thi hoặc **phát hành cổ phiếu**; phụ lục FSO ký với giá thấp hơn / hạn ngắn hơn 2036 (biến thể bỏ >5 năm: −610); DT vận tải Q4 (~20/01/2027) < Q3; 177 tỷ FSO không ghi nhận.
- **Tốt lên**: hoãn/huỷ mua tàu (nhánh "không"; NPV0 ⇒ DƯỚI vùng); ký phụ lục FSO đúng điều khoản BB 03/06/2025; ký TC dài hạn có giá; giá < P10 13.799 ⇒ DƯỚI vùng.
- **HARD ABANDON**: ký mua cả hai tàu tài trợ bằng phát hành cổ phiếu dưới book; PVTrans ép GD liên quan bất lợi (giá FSO/ủy thác dưới thị trường); đình chỉ/huỷ niêm yết.
- Tranche: không áp dụng. **Sleeve fear-buy §2.5: KHÔNG đủ điều kiện.**

## 9. Còn mở / chưa kiểm
177 tỷ FSO năm 1 chưa hoà giải · cơ cấu TC/chuyến/pool, đáo hạn HĐ tàu · tuổi tàu chỉ từ báo chí · văn kiện ĐHĐCĐ bất thường (chưa tra lại sau 05/11) · room ngoại · phế liệu vs lên đà TT99 (chỉ có độ nhạy đơn vị) · HTM 1.015,87 không có trong BQ (đọc từ ảnh CĐKT Q3 mã 123, khớp).

## 10. LOCK + tái lập
`calc_r3/LOCK_md5.txt`: 3 output model + 21 file upstream (script, giả định, SQL+CSV giá, `../calc/model.py`, `model_r2_out.json`, `common.py`, `wpct.py`, `deposit_rate_vn.py`/`cctg_rate_vn.py` + 2 CSV sự kiện, 3 PDF nguồn, REPORT 29/10, TOP5C, STANDARD_r2, REPORT_r2, SUMMARY_r2, SUMMARY_5F) — khoá TRƯỚC khi đọc giá; compare kiểm lại từng md5 trước khi chạy. Model chạy 2 lần trùng byte (`run1.md5` = `run2.md5`); compare 2 lần trùng byte (`cmp1.md5` = `cmp2.md5`). Interpreter `/home/trido/thanhdt/wc_venv/bin/python -I`.
