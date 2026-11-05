# MVC — DD redo VÒNG 2 (05/11/2026, job Taylor_20261105_020023)

**Kết luận (số từ `calc/mvc_redo_r2_out.txt`, MỨC KẾT CỤC, 34.992 kết cục = 4.374 ô × 8):**
tâm **15.276 đ/cp sau CK 5 tỷ** (16.694 trước) · **P10 9.857 · P50 13.748 · P90 23.516** sau CK (min 7.788).
Giá 04/11/2026 **13.800** ⇒ −9,7% so tâm ⇒ **TRONG vùng**; **50,6% trọng số kết cục nằm dưới giá** — giá ≈ trung vị kết cục.
Ở cỡ 1 tỷ (cỡ khả thi hơn): tâm 16.060 · P10 10.363 · P50 14.453 · P90 24.723 · 43,0% dưới giá · cũng TRONG vùng. Luật 4: **không đạt**. **Không đủ điều kiện sleeve fear-buy §2.5.**
So với sổ cũ (P25–P75, nhãn "RẺ CÓ ĐIỀU KIỆN"): nhãn đổi **do định nghĩa vùng** (P10–P90 ở mức kết cục), không phải do cơ bản.

Engine = MVC r9 (`nnc_model_r6` tiêm r + `r8/calc/model_r8.py`), import, không sửa. Chân đối chứng: tham số trung tâm có trễ GP = **16.482 = pin r9**. Kiểm toán: lưới vòng 1 (có trễ, không có trục mới) ở mức kết cục ⇒ P10 9.687 · P50 14.122 · P90 23.054 · 46,4% dưới giá (sau CK). LOCK md5 đủ chuỗi (`calc/LOCK_r2_md5.txt`, 18 file). Chạy 2 lần trùng byte.

## 1. Đã sửa gì (theo E_CORRECTIONS, kiểm bằng calc)
1. **Bỏ "ghi theo giá vốn, NPV 0" sai chữ**: vòng 1 trừ chi phí trễ GP kỳ vọng P(0/1/2 năm)=0,30/0,40/0,30 × sổ sách 438,4 tỷ (chỉ dựa nhận định Bobby F6, trái kế hoạch ĐHĐCĐ "khai thác 2028"). Đo lại: **−527 đ/cp** (riêng mỏ mới MVC), −571 khi tính cả CIP Tam Lập của NNC qua sở hữu chéo. **Đã bỏ khỏi base**; tham số trung tâm không trễ = **17.053** trước CK (E_CORRECTIONS ghi 17.009 — lệch 44 đ do bản này bỏ trễ cả bên NNC cho nhất quán với NNC r2).
2. **Đưa lại trục biên chu kỳ Tân Lập {25%, 30%, ~NNC}** (trọng số đều — **[UL]**). Tại tham số: 25% −1.105 · 30% −575. Skeptic ước P50 −8%, tỷ trọng dưới giá 40%→56% (mức ô); đo ở mức kết cục: bỏ trục ⇒ 46,0% dưới giá; có trục ⇒ 50,6%.
3. Thêm **trục trần chu kỳ SL 1,40** (giống NNC r2, cùng lý do đối xứng): −849 tại tham số.
4. Phân vị ở mức kết cục (8 kết cục/ô) bằng `_shared/wpct.py`.

## 2. Ba con số "tâm" (§4)
| | Trước CK | Sau CK 5 tỷ |
|---|---|---|
| Tâm = kỳ vọng lưới | 16.694 | **15.276** |
| Giá trị tại tham số trung tâm (không trễ) | 17.053 | 15.605 |
| P50 kết cục | 15.024 | 13.748 |

**P90 do nhánh STRUCTURAL (trọng số 0,20 của Bobby) quyết định**: nhánh này một mình có trung vị 22.265, P90 32.320 (sau CK). Trọng số STRUCTURAL 0,15 ⇒ P90 22.324; 0,10 ⇒ 20.758; 0,30 ⇒ 25.418. Nhánh CYCLICAL: tâm 12.855, 66,7% dưới giá. Số ô thực: mỗi nhánh 1.458 ô × 8 kết cục (STRUCTURAL không phụ thuộc trục SL/ADMIN/trần/biên Tân Lập nhưng vẫn đếm đủ để trọng số đúng — vòng 1 nêu "81 vs 243" là số ô *khác giá trị*).

## 3. Lưới — trục và giả định tự đặt
Trạng thái biên 0,20/0,45/0,35 (Bobby, nhận định) × chi phí Tân Lập 0,85/1,0/1,15 × REL giá Tân Lập/NNC 0,88/0,91/0,95 × sản lượng năm thường 3 mức × hạn GP Tân Lập 2035/W/2045 × ánh xạ ADMIN 3 mức × **biên Tân Lập 25%/30%/~NNC [UL]** × **trần branch/SL 1,40**; trong ô: 4 kịch bản W0 25/50/20/5 × 2 đường giá 50/50. r 13,5% cố định.
Ngoài lưới (độ nhạy tại tham số, trước CK): trễ GP (Bobby F6) −527 · mỏ mới "hai phía" (upside + NPV giá xấu, lệch NPV0 không có IRR từ dữ liệu — luật 20) −2.080 · ADMIN perm05 +1.432 / full −241 (đã trong lưới) · bỏ thuê Núi Nhỏ bên NNC −329. Lãi huy động: −100bp +2,4% · −50bp +1,2% · +50bp −1,1% · +100bp −2,2%.

## 4. Base — điều chỉnh lệch sổ sách/NPV0
| Khoản | Ảnh hưởng | Cơ sở | Nguồn |
|---|---|---|---|
| Hai mỏ mới đã chi 438,4 tỷ | 0 | sổ sách, NPV0 thật | BCTC HN Q3/2026 |
| Đất 30 tỷ; cụm CN; mua NNC lên 51% | 0 | sổ sách / NPV0 | ĐHĐCĐ 2026 |
| Cổ phần NNC 44,07% | giải đồng thời | V_NNC từ mô hình NNC (không giá thị trường), cùng quy ước bỏ trễ GP | nnc_model_r6 |

Gordon (r9, một biến thể — MVC nợ ròng, không có thu nhập lãi tiền gửi đáng kể để tách): ROE chuẩn hoá trộn 10,1% ⇒ **10.382**, thấp hơn giá; tâm r9 hàm ý ROE 14,2%.

## 5. Thanh khoản
ADV trung vị 250 phiên **0,44 tỷ**, 60 phiên **0,19 tỷ**; σ 2,52%.
- Cỡ **5 tỷ** (quy ước fleet): CK **8,49%** (ADV60 12,98%). **Q/ADV250 = 11,3× (ADV60 26×) — ngoại suy ngoài vùng hiệu chỉnh luật căn bậc hai**; thoát lệnh 113/57 phiên ở 10/20% ADV. Nhãn chính vẫn tính ở 5 tỷ để so được với các mã khác.
- Cỡ **1 tỷ** (Q/ADV 2,3×): CK 3,80% (ADV60 5,80%) — nhãn không đổi (TRONG vùng).
- Cỡ sleeve thật 10–40 triệu: CK **0,38–0,76%** (ADV60 0,58–1,16%).

## 6. WARNING pháp lý / quản trị (đầy đủ)
- Sở hữu chéo MVC 44,07% NNC ↔ NNC 10,3% MVC; Chủ tịch HĐQT MVC = Chủ tịch Thanh Lễ và NNC; Trưởng BKS MVC = TGĐ Thanh Lễ.
- **Ủy quyền ĐHĐCĐ MVC 2026 mua NNC lên 51%** (~1,52 triệu cp, ước ~72 tỷ; giá/đối tác chưa công bố) — giao dịch bên liên quan.
- Nếu MVC ≥51% NNC: **Luật DN Đ195 có thể buộc NNC thoái 10,3% MVC** (~142 tỷ ≈ 325–760 phiên ADV của MVC) ⇒ áp lực cung lớn — **cần legal-vn xác minh**.
- ĐHĐCĐ 2026 còn duyệt **cụm công nghiệp tới 500 tỷ** ngoài 1.500 tỷ mỏ mới ⇒ nợ ròng có thể ~1,4–1,5 nghìn tỷ trước khi mỏ có doanh thu, D/E ~0,9–1,0 (cờ #1 `dd_MVC_20261103/SKEPTIC_20261103.md`, chưa đóng).
- Dư nợ BIDV 452 tỷ > hạn mức 350 tỷ đã công bố; tạm ứng 60,6 tỷ chưa thuyết minh đối tượng.
- "Chưa thấy xử phạt/khởi tố MVC 2026": WebSearch **05/11/2026** không ra kết quả (nguồn duyệt: Simplize hồ sơ/tin MVC, BCTN). Simplize ghi MVC sở hữu NNC **43,55%** (khác 44,07% — chưa đối soát).

## 7. Mốc đổi nhận định (hai chiều), HARD ABANDON, tranche
| Mốc | Thời điểm | Tích cực hơn nếu | Tiêu cực hơn nếu |
|---|---|---|---|
| BCTC Q4/2026 | ~01/2027 | Biên gộp quý ≥35%; nợ ròng theo lộ trình | Biên <28% khi DT đi ngang |
| Giá đá Sở XD Đồng Nai | Q2/2027 | Tăng >7% | Giảm >7% |
| GP khai thác 2 mỏ mới / tổng vốn | 2027 | Cấp đúng hạn (khai thác 2028), vốn ≤1.500 tỷ | Trễ ≥1 năm (khi đó áp −527); vốn >1.950 tỷ |
| HĐQT/CBTT khởi động cụm CN | bất kỳ | Hoãn | Chi >100 tỷ |
| Hợp đồng tín dụng; nợ ròng | Q4/2026–2027 | Vay dài hạn thay ngắn hạn | Nợ ròng vượt lộ trình >150 tỷ |
| Giá cổ phiếu | — | < P10 9.857 ⇒ DƯỚI vùng | > P90 23.516 ⇒ TRÊN vùng |

**HARD ABANDON** (đề xuất, chờ user duyệt): (1) MVC mua NNC lên 51% giá cao hơn giá trị mô hình NNC hoặc từ bên liên quan không có thẩm định; (2) NNC bị buộc thoái 10,3% MVC qua thị trường (áp lực cung); (3) nợ ròng > 1,5 nghìn tỷ trước khi mỏ mới có doanh thu; (4) GP mỏ mới bị từ chối/thu hồi.
**Tranche**: thanh khoản quá mỏng cho cỡ lớn — nếu có vị thế, ≤1 tỷ chia 3 lần, mỗi lần ≤20% ADV60.

## Phụ lục — đổi gì so với vòng 1
| | Vòng 1 | **Vòng 2** | Lý do |
|---|---|---|---|
| Tâm sau CK | 15.082 (tham số, có trễ) | **15.276** (kỳ vọng lưới, không trễ) | bỏ trễ +571 tại tham số; trục biên TL + trần (−) |
| P10 / P50 / P90 sau CK | 11.941 / 14.424 / 20.989 | **9.857 / 13.748 / 23.516** | mức kết cục (chủ yếu) + trục mới |
| % trọng số dưới giá | 40,3% (ô) | **50,6%** (kết cục) | |
| Nhãn | TRONG vùng | **TRONG vùng** | không đổi |

Không sửa `kb/dd_price_zones.json`. Chưa qua fundamental-skeptic vòng 2 (Mike chạy).
