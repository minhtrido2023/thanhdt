# NNC — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020023)

**Kết luận (số từ `calc/nnc_redo_r2_out.txt`, phân vị ở MỨC KẾT CỤC, 3.888 kết cục = 486 ô × 8):**
tâm **57.589 đ/cp sau CK** (59.760 trước) · **P10 30.219 · P50 52.916 · P90 93.649** (sau CK; min 21.023).
Giá 04/11/2026 **46.900** ⇒ −18,6% so tâm, nằm TRONG vùng; **37,5% trọng số kết cục nằm dưới giá**.
Nhãn **TRONG vùng giữ nguyên** nhưng câu "sát cận dưới" của vòng 1 là **ảo ảnh của lỗi nén phân tán** (vòng 1 tính phân vị trên kỳ vọng từng ô) — cận dưới thật thấp hơn giá 36%. Luật 4 (giá ≤ 0,85 × tâm): đạt. **Không đủ điều kiện sleeve fear-buy §2.5** (không có sự kiện sợ hãi/khủng hoảng; đây là DD định giá thường).

Chân kiểm toán: chạy lại đúng lưới vòng 1 (có trễ GP, không có trục trần) ở mức kết cục ⇒ P10 33.028 · P50 55.951 · P90 96.315 · 30,4% dưới giá — **tái lập số skeptic** (P50 skeptic 56.033, lệch 0,15% do cách nội suy). Engine import `dd_NNC_20261030/r6/calc/nnc_model_r6.py` (không sửa); md5 đủ chuỗi upstream ở `calc/LOCK_r2_md5.txt`; chạy 2 lần ra trùng byte.

## 1. Ba con số "tâm" — tách bạch (chuẩn §4)
| Định nghĩa | Trước CK | Sau CK |
|---|---|---|
| Tâm = kỳ vọng trọng số của lưới (dùng làm "tâm") | 59.760 | **57.589** |
| Giá trị tại tham số trung tâm (không trễ GP) | 61.407 | 59.177 |
| P50 kết cục | 54.910 | 52.916 |

Phân phối lệch phải: P90 do **nhánh STRUCTURAL (trọng số 0,20 của Bobby)** quyết định — nhánh này tự nó trải P10 32,9k … P90 132,7k, trung vị 93,0k. Độ nhạy theo trọng số STRUCTURAL (trước CK): 0,10 ⇒ tâm 56.249 / P90 85.523; 0,15 ⇒ 58.004 / 93.271; 0,30 ⇒ 63.271 / 106.025. P10 hầu như không đổi (31,1–31,4k).

## 2. Đã sửa gì so với vòng 1 (theo E_CORRECTIONS, đã kiểm bằng calc)
1. **Mức kết cục**: mỗi ô tách 4 kịch bản (tốt/cơ sở/xấu/rất xấu, W0 25/50/20/5) × 2 đường giá (g2031/thực, 50/50). Trục trộn đường giá 70-30/50-50/30-70 với trọng số đều cho đúng phân phối PW0 trên cùng giá trị kết cục ⇒ gộp (không làm đổi phân phối).
2. **Lưới đối xứng**: đưa lại trục **trần chu kỳ SL 1,40** (−3.335 tại tâm; vòng 1 loại vì "chỉ chiều xuống" trong khi giữ trục ADMIN chỉ lệch lên). Thêm trục **thuê Núi Nhỏ {tới 2043 / tới 2030 / không}**, trọng số đều = **giả định [UL]** (thời hạn chưa xác minh, KT25 9.1 "cam kết: Không có"). Báo song song: bỏ trục trần ⇒ tâm 61.328 / P10 32.263 / P50 56.941 / P90 98.915; bỏ trục thuê ⇒ 61.520 / 33.227 / 56.590 / 98.886 (trước CK).
3. **NPV0 thật**: vòng 1 viết "Tam Lập 1 khu II theo vốn đã chi, NPV 0" nhưng engine trừ chi phí trễ GP kỳ vọng P(0/1/2 năm)=0,30/0,40/0,30 (Bobby F6, chỉ là nhận định) — −458 đ/cp cho CIP Tam Lập và −248 cho mỏ mới MVC qua sở hữu chéo. **Đã bỏ khỏi base** (cả hai); "có trễ" thành độ nhạy −705 (trước CK).
4. Gordon báo hai biến thể (mục 6). Thanh khoản ở cỡ sleeve thật (mục 5).

## 3. Lưới — trục, trọng số, giả định tự đặt
| Trục | Mức | Trọng số | Nguồn |
|---|---|---|---|
| Trạng thái biên từ 2028 | STRUCTURAL / ADMIN_GATED / CYCLICAL | 0,20 / 0,45 / 0,35 | Bobby (nhận định, không phải tần suất) |
| K chi phí | 0,87 / 0,97 / 1,07 | đều | KT25 7.2 ±10% |
| Sản lượng năm thường | (1,05;1,05) / (1,10;1,20) / (1,20;1,30) | đều | r5 |
| Ánh xạ ADMIN | perm05 / ramp / full | đều | r5 (skeptic R4) |
| Trần chu kỳ | theo SL nhánh / SL 1,40 (236,1k) | đều | **mới vòng 2** |
| Thuê Núi Nhỏ | 2043 / 2030 / không | đều **[UL]** | **mới vòng 2**; "2030" xấp xỉ theo tỷ lệ PV (60,2% PV dòng thuê nằm sau 2030) |
| Trong ô: kịch bản × đường giá | 4 × 2 | W0 × PW0 | r3 |

r cố định 13,5% (lãi huy động 12T hiệu dụng 7,40% @ cctg_12m 02/11/2026 = điểm neo, β=1). Độ nhạy r như vòng 1 (≈ ±1,5%/50bp).

Ra khỏi lưới (báo độ nhạy, trước CK, so với tham số trung tâm 61.407): (+) trả trước CNBP 59,2 tỷ là tiền thuê đã trả **+2.126** (chưa xác minh) · (+) mỏ đối thủ hết GP từ 2034 **+5.065** · STRESS đường giá danh nghĩa phẳng **−12.392** · trễ GP (Bobby F6) **−705**. Hai trục cộng và một trục trừ cùng loại "chưa có dữ liệu" đều nằm ngoài ⇒ không chọn chiều.

## 4. Base — điều chỉnh lệch sổ sách/NPV0
| Khoản | Ảnh hưởng | Cơ sở | Nguồn |
|---|---|---|---|
| CIP Tam Lập 1 khu II 83,51 tỷ | 0 (sổ sách) | NPV 0 thật — vòng 2 KHÔNG trừ trễ GP | BCTC riêng Q3/2026, XDCB dở dang |
| Ký quỹ PHMT 4,57 + DTA 4,31 | +424 | sổ sách, đối xứng với dự phòng đã trừ | Q3 V9, V19a tr.2 |
| Thu nhập cho thuê Núi Nhỏ 11,13 tỷ/năm | 0 … +3.402 | **không còn cố định trong base**: trục 3 mức | KT25 7.1–7.2 |

Tiền ròng sau nghĩa vụ (30/09/2026): tiền 25,47 + tiền gửi có kỳ hạn 322,44 + CK kinh doanh 0,13 − vay (5,00 + 69,89) − dự phòng truy thu 22,37 − quỹ KTPL 16,78 − cổ tức phải trả 5,89 − dự phòng môi trường 4,50. **Đính chính vòng 1**: có người mua trả trước 5,03 tỷ (mã 312) — câu "không có tiền ứng trước" là sai; khoản này nhỏ (≈230 đ/cp), chưa trừ riêng trong engine (open issue nhỏ).

## 5. Thanh khoản
ADV trung vị 250 phiên **2,10 tỷ**, 60 phiên **1,39 tỷ**; σ ngày 2,35% (BQ `tav2_bq.ticker`, 03/11/2025–04/11/2026).
- Cỡ tham chiếu **5 tỷ** (quy ước fleet; Q/ADV250 = 2,4× — trong vùng hiệu chỉnh của luật căn bậc hai): CK **3,63%** (ADV60: 4,46%). **Nhãn tính ở cỡ này.**
- Cỡ sleeve thật (10–40 triệu; NAV SpaceX ≈0,94 tỷ): CK **0,16–0,32%** (ADV60: 0,20–0,40%) — gần như không đáng kể.

## 6. Kiểm chéo Gordon / ROE
P/B = (ROE − 3%)/(13,5% − 3%) × BVPS 29.915: ROE chuẩn hoá **không lãi tiền gửi 14,7% ⇒ 33.250**; **có lãi tiền gửi 17,2% ⇒ 40.480**. Cả hai **thấp hơn giá** 46.900. Tâm 59.760 hàm ý ROE bền **24,0%** — cao hơn nhiều so với ROE chuẩn hoá ⇒ tâm dựa vào biên đá giữ cao hơn trung bình chu kỳ; đây là điểm yếu chính của luận điểm.

## 7. WARNING pháp lý / quản trị (đầy đủ, mang theo cờ chưa đóng)
- **Sở hữu chéo** MVC 44,07% NNC ↔ NNC 10,3% MVC. **ĐHĐCĐ MVC 2026 uỷ quyền mua NNC lên 51%** (giá/đối tác chưa công bố — giao dịch bên liên quan). Nếu MVC ≥51%, Luật DN Đ195 có thể buộc NNC thoái 10,3% MVC (≈142 tỷ ≈ 325–760 phiên ADV của MVC) ⇒ áp lực cung — **cần legal-vn xác minh**. Simplize ghi 43,55% (lệch nguồn, chưa đối soát).
- **Truy thu chạm mỏ lõi Mũi Tàu** (cờ E12, `dd_NNC_20261030/SKEPTIC_20261031.md`, CHƯA ĐÓNG): dự phòng tiền cấp quyền 0,84 tỷ (Q3 V19a) sau CQKTKS 1,735 tỷ (KT25 7.8).
- **Tổng truy thu Núi Nhỏ ≈42 tỷ** (dự phòng 15,58 + 5,95 + đã nộp 20,43 năm 2026) ≈ **1.900 đ/cp** — không nhỏ. Bỏ chữ "nhỏ" và "rủi ro scandal di cư thấp" của vòng 1.
- **Bên liên quan NHC** (giám đốc NNC là Chủ tịch NHC): 61% phải thu; DT dịch vụ 2025 18,92 tỷ ≈ DT từ NHC 18,41 tỷ ⇒ thu nhập cho thuê Núi Nhỏ nhiều khả năng đến từ bên liên quan (đã đưa thành trục lưới).
- Định hướng dồn tiền giữ lại vào BĐS; cổ tức tiền 2025 ≈15% LNST. Biên đá ở đỉnh 15 năm (GPM Q3/26 57,9%).
- "Chưa thấy xử phạt/khởi tố 2026": **WebSearch 05/11/2026** (từ khoá NNC/MVC + xử phạt/truy thu/khởi tố) không ra kết quả; kèm BCTC Q3/2026 và kiểm toán 2025 chấp nhận toàn phần. Tra được CBTT **17/04/2026: NNC trúng đấu giá quyền khai thác khoáng sản (UBND TP.HCM)** — dữ liệu mới, **chưa đối chiếu** là mỏ nào/giá/hạn; nếu là Tam Lập 1 khu II thì cờ "chưa có GP" đóng và độ nhạy trễ GP mất ý nghĩa. **Chưa đưa vào mô hình** vì chưa đọc văn bản gốc.

## 8. Mốc đổi nhận định (hai chiều), HARD ABANDON, tranche
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| BCTC Q4/2026, Q1/2027 | ~20/01, ~20/04/2027 | Biên gộp ≥55% | Biên <45% khi doanh thu đi ngang |
| Giá đá Sở XD | Q2/2027 | > Q3/2026 +7% | < −7% |
| Vành đai 4 / mỏ đấu giá trong cụm | tới 30/06/2027 | ≥20% khối lượng; mỏ mới chậm | <20%; mỏ mới cấp sớm |
| Hợp đồng thuê Núi Nhỏ | khi có thuyết minh | có thời hạn tới 2043, bên thứ ba | chỉ tới 2030 / bên liên quan, giá dưới thị trường |
| Giá cổ phiếu | — | < P10 30.219 ⇒ DƯỚI vùng | > P90 93.649 ⇒ TRÊN vùng |

**HARD ABANDON** (thoát bất kể giá): (1) thu hồi/đình chỉ GP Mũi Tàu; (2) truy thu mới làm tổng truy thu tăng vật chất (> +20 tỷ, ≈ +900 đ/cp); (3) MVC lên ≥51% kéo theo buộc thoái sở hữu chéo với giá bất lợi cho cổ đông thiểu số; (4) dồn tiền giữ lại vào BĐS (nghị quyết đầu tư > 30% tiền ròng).
**Tranche** (nếu user muốn vị thế): 1/3 tại giá hiện tại, 1/3 sau BCTC Q4/2026 nếu biên ≥50%, 1/3 khi rõ hợp đồng thuê — đề xuất, chờ user duyệt.

## Phụ lục — đổi gì so với vòng 1 và sổ mức giá cũ
| | Vòng 1 | **Vòng 2** | Lý do |
|---|---|---|---|
| Tâm sau CK | 58.497 | **57.589** | vòng 1 = giá trị tại tham số trung tâm (có trễ); vòng 2 = kỳ vọng lưới (§4). Trước CK: lưới trục vòng 1 không trễ 63.098 → thêm trục trần + thuê 59.760 (−3.338); bỏ trễ GP +705 tại tham số |
| P10 / P50 / P90 sau CK | 44.917 / 56.395 / 85.649 | **30.219 / 52.916 / 93.649** | mức kết cục (chủ yếu) + trục mới |
| % trọng số dưới giá | 17,6% (ô) | **37,5%** (kết cục) | |
| Nhãn | TRONG vùng | **TRONG vùng** | không đổi; vùng rộng ra do định nghĩa (mức kết cục), không do cơ bản |

Sổ mức giá cũ (rev4, 03/11; P25–P75 lưới kỳ vọng): 55.000 / 58.500 / 66.900 — tâm đổi −1,6%. **Không sửa `kb/dd_price_zones.json`.** Chưa qua fundamental-skeptic vòng 2 (Mike chạy).
