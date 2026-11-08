# NNC — DD redo VÒNG 3 (08/11/2026, job Taylor_20261108_164333)

**Kết luận** (số lấy từ `calc/nnc_redo_r3_out.txt`; phân vị tính ở MỨC KẾT CỤC bằng `_shared/wpct.py`; 5.832 kết cục = 729 ô × 8):
- Tâm **61.273 đ/cp sau CK** (63.591 trước CK).
- **P10 30.375 · P50 59.221 · P90 95.341** (sau CK); kết cục thấp nhất 21.020.
- Giá đóng cửa 06/11/2026 (BQ) **47.200** ⇒ thấp hơn tâm 23,0%, nằm **TRONG vùng**. **28,2% trọng số kết cục nằm dưới giá**; bản r2 tính ở giá mới là 38,1%.
- So với r2: tâm **+6,4%** (57.589 → 61.273). Nhãn không đổi.
- Luật 4 (giá ≤ 0,85 × tâm): ĐẠT.
- Không đủ điều kiện sleeve fear-buy §2.5: không có sự kiện sợ hãi hay khủng hoảng.

Lưới r2 được dựng lại trùng số đến từng đồng (trước CK 59.760; tham số trung tâm 61.407 — có assert). Engine `nnc_model_r6` và chuỗi upstream được import, không sửa file. Có 2 monkeypatch ở runtime, có cổng tắt để tái lập r2. Hai lần chạy cho output trùng byte. Md5 đủ upstream ở `calc/LOCK_r3_md5.txt`. Giả định được khoá ở `calc/assumptions_r3.json` trước lần chạy 1.

## 1. Từng đính chính của skeptic — kiểm bằng calc
| # | Đính chính | Kết quả kiểm | Áp? |
|---|---|---|---|
| 1 | Trần chu kỳ P_CYC tính bằng tiền 2026 nhưng lại nhân với đường g2031 ⇒ biên kẹt ở 26% (TB chu kỳ 34,3%) ⇒ đếm hai lần | ĐÚNG. Trần là khái niệm "biên TB chu kỳ"; chi phí tăng 3%/năm danh nghĩa, nên trần cũng phải tăng 3%/năm danh nghĩa trên MỌI đường giá. Sửa ở `np_bottom`: cap_thực = P_CYC×1,03^t / g(y,path). Đường thực không đổi. **+2.525 sau CK (khớp đúng số skeptic)** | **BASE** |
| 2 | Trục trần chỉ mở chiều giảm ⇒ thêm mức SL 1,05 | ĐÚNG theo luật đối xứng. Trần theo SL của nhánh là 260,6 / 249,7 / 242,9k; mức 1,05 cho 260,6k, mức 1,40 cho 236,1k. **+1.167 (khớp)**. ⚠️ Câu "giá 2024 ≈260k" của skeptic đúng nếu tính bằng DT thành phẩm kiểm toán: 257,44 tỷ / 1,05 tr m³ = 245,2k, × 1,03² = 260,1k. Nó KHÔNG đúng theo giá mỏ FPTS: 202,6k (FPTS lệch 21%, E3). Cơ sở ghi vào base là sản lượng 2024 = 1,05 | **BASE** |
| 3 | Thuê Núi Nhỏ [UL] chia đều ⇒ báo thêm bản "chỉ tới 2043" | Bản này cho tâm 62.980, P10 33.764, P90 98.698 (sau CK). Số skeptic 61.822 tính trên lưới chưa có đính chính 2, nên không so trực tiếp được | song song |
| 4 | min() chỉ cắt chiều lên ⇒ thêm bản co giãn đối xứng | Bỏ min cho tâm 62.035, P10 34.238. **KHÔNG tái lập được số của skeptic (64.022 / P10 28,2k)**: bỏ min thì chỉ có thể kéo giá LÊN về trần, nên P10 không thể giảm. Cần skeptic nêu công thức | độ nhạy |
| 5 | Kịch bản xấu (0,8 × 250k) thiếu dòng cơ sở dữ liệu; chồng đáy lên TB chu kỳ = đếm đôi một phần | Đã có cơ sở dữ liệu: FPTS dùng đường CƠ SỞ 0,8 tr m³ từ 2028, giá 237,6k / 209,8k (FPTS tr.1, tr.17; SKEPTIC_20261031 E3) — còn thấp hơn mức 250k của mô hình. Phần đếm đôi đưa vào độ nhạy "xấu không chồng": nâng giá kịch bản xấu lên tối thiểu bằng trần ở các nhánh stress ⇒ tâm 62.135 (+862), P10 34.509 | base giữ + độ nhạy |
| 6 | Tiền gửi 322,44 / dự phòng 22,37 / quỹ KTPL 16,78 chưa kiểm; trừ khoản người mua trả trước 5,03 | BQ `ticker_financial` 2026Q3 KHỚP: Cash_P0 25,47; vay 5,00 + 69,89. Các số 322,44 / 22,37 / 16,78 đã PASS đối chiếu độc lập (SKEPTIC_20261031:18, BCTC Q3); **chưa kiểm lại PDF trong phiên này**. Khoản trả trước 5,03 là vốn lưu động vận hành, mà mô hình bỏ VLĐ ở cả hai phía (thuế phải nộp cũng không trừ). Trừ một chiều −229 trong khi bỏ phải thu (BQ AR_P0 24,44) là lệch. Bản đối xứng +886 ⇒ đưa vào độ nhạy | độ nhạy |
| 6b | Sửa đường dẫn summary_r2.py trong LOCK | Đường dẫn đúng là `dd_redo_20261105/NNC/calc/summary_r2.py`; md5 d847ff75… vẫn khớp. Đã ghi chú vào LOCK_r2 | xong |

## 2. Bridge r2 → r3 (sau CK)
57.589 (pin r2, giá 04/11, CK 3,63%) → **57.581** (CK 06/11 3,65%) → **60.106** (D1 trần tăng theo lạm phát) → **61.273** (D2 thêm mức trần 1,05).

## 3. Ba con số "tâm"
| | Trước CK | Sau CK |
|---|---|---|
| Tâm = kỳ vọng lưới | 63.591 | **61.273** |
| Tại tham số trung tâm (không trễ GP) | 64.260 | 61.914 |
| P50 kết cục | 61.461 | 59.221 |

Phân phối lệch phải. P90 do nhánh STRUCTURAL (trọng số 0,20, nhận định của Bobby) quyết định; nhánh này có trung vị 93,0k trước CK. Đổi trọng số STRUCTURAL (sau CK): 0,10 ⇒ tâm ≈58,4k / P90 ≈84,7k; 0,30 ⇒ tâm ≈64,2k / P90 ≈102,2k. P10 gần như không đổi (~30,4–31,3k). Tách theo nhánh (trước CK): STRUCTURAL 87.847 · ADMIN 59.701 · CYCLICAL 54.732.

## 4. Lưới và giả định
Giữ như r2, cộng 2 thay đổi:
- trục trần {SL 1,05 / theo SL nhánh / SL 1,40}, trọng số đều;
- trần tăng theo lạm phát.

Các tham số [UL] (giả định tự đặt):
- trọng số trạng thái 0,20/0,45/0,35 (Bobby);
- trục thuê đều nhau;
- PW0 50/50;
- W0 25/50/20/5.

r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,5%** (cctg_12m 02/11; hiệu dụng tại 06/11).

Độ nhạy đơn tại tham số trung tâm (trước CK, so với 64.260):
- trễ GP (Bobby F6) −705;
- trần SL 1,40 −3.256;
- ADMIN perm05 +4.962 / full −837;
- bỏ thuê −3.402;
- trả trước CNBP là tiền thuê +2.126 (chưa xác minh);
- đối thủ hết GP từ 2034 +4.367;
- giá danh nghĩa phẳng −6.195 (r2: −12.392 — phần chênh chính là phần đếm đôi đã sửa ở D1);
- trả trước người mua: một chiều −229 / đối xứng +886.

## 5. Thanh khoản (BQ đến 06/11)
- ADV250 = 2,08 tỷ, ADV60 = 1,39 tỷ.
- CK ở cỡ 5 tỷ (Q/ADV250 = 2,4x): **3,65%** theo ADV250; 4,46% theo ADV60.
- Cỡ sleeve thật: 10 triệu → 0,16%; 40 triệu → 0,33% (không đáng kể).
- Nhãn tính theo cỡ 5 tỷ.

## 6. Giá đang ngụ ý gì
- Ở giá 47.200 (trước CK 48.988), Gordon ngụ ý **ROE bền ≈20,2%**, cao hơn ROE chuẩn hoá 14,7–17,2%.
- Ngay cả khi 100% là CYCLICAL, giá trị sau CK 52.737 vẫn **cao hơn giá 11,7%**.
- Giá chỉ khớp khi các kịch bản xấu/rất xấu (đường cơ sở FPTS) chiếm phần chủ đạo.
- Gordon ROE khoá 33.250 / thêm LN tài chính 40.480. ROE ngụ ý bởi tâm: 25,3%.

## 7. WARNING (giữ nguyên từ r2, chưa đóng)
- **Sở hữu chéo MVC.** MVC giữ 44,07% NNC (nguồn khác ghi 43,55%); NNC giữ 10,3% MVC. Có uỷ quyền mua NNC lên 51%; rủi ro buộc thoái theo D195 ⇒ cần legal-vn xác minh.
- **Truy thu tài nguyên** đã chạm mỏ lõi Mũi Tàu (dự phòng 0,84 tỷ) — cờ E12.
- **Truy thu Núi Nhỏ** ~42 tỷ (~1.900 đ/cp).
- **Bên liên quan NHC:** 61% phải thu; thu nhập cho thuê nhiều khả năng đến từ NHC.
- Tôi chưa tra lại tin pháp lý sau 05/11.

## 8. Mốc đổi nhận định
Giữ như r2 §8. Thêm 2 mốc:
- (a) Tìm được bằng chứng hợp đồng thuê Núi Nhỏ ⇒ thay trục thuê bằng giá trị thật (khoảng −1,7k … +1,7k).
- (b) Skeptic nêu công thức co giãn đối xứng ⇒ chạy lại đính chính 4.

Không đặt lệnh, không sửa `kb/dd_price_zones.json` (Mike ghi sổ sau phản biện cuối).
