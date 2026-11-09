# SIP — DD redo VÒNG 3 (09/11/2026, job Taylor_20261108_180132)

Áp/kiểm đính chính fundamental-skeptic (`../TOP5D_CORRECTIONS_20261108.md` mục SIP) lên `REPORT_r2.md`. Số: `calc_r3/model_r3.py` → `model_r3_out.json/.txt`; chạy 2 lần trùng byte (`run1.txt` = `run2.txt`, md5 `e11f6f4b…`). Giả định khoá `calc_r3/assumptions_r3.json`; `calc_r3/LOCK_md5.txt` do `lock_r3.sh` ghi lúc 2026-11-09T01:07:58+0700, TRƯỚC lần chạy đầu (19 file upstream). Control: tái lập r2 ở giá/CK 04/11 = 54.230 / P10 43.784 / P90 68.713, trùng số r2.

## Kết luận
**Tâm 54.466 · P10 43.257 · P50 53.085 · P90 69.818** (sau CK 5 tỷ 1,39%). Giá 06/11 **50.100** ⇒ **TRONG vùng**, nằm dưới tâm 8,0%, **35,4%** trọng số kết cục dưới giá. **Luật 4 KHÔNG đạt** (ngưỡng 0,85×tâm = 46.296). Cỡ sleeve 40 triệu (CK 0,31%): tâm 55.062 · P10 43.730 · P90 70.581, TRONG vùng, 33,8% dưới giá, luật 4 cũng không đạt.
So r2 (54.230 @49.000): tâm +236, P10 −527, P90 +1.105. Nhãn không đổi. Tổng 6 đính chính gần như triệt tiêu nhau: RONIC=Ke −3.389, phần còn lại +3.638.

## Kiểm từng đính chính (calc, cầu luỹ kế, tâm sau CK 5 tỷ)
| # | Đính chính | Kết luận | Δ calc | Δ skeptic |
|---|---|---|---|---|
| 0 | giá/CK/r 06/11 (r giữ 13,50%: lãi huy động hiệu dụng 7,40% không đổi) | — | −13 | — |
| 1 | RONIC = Ke (moat NARROW không bền; ROE phồng do 15,1 nghìn tỷ tiền thuê nhận trước) | ĐÚNG, áp. Quy ước user 08/11 "không thưởng, không trừ" ⇒ ADDENDUM giữ RONIC=ROE5Y là thưởng moat, mâu thuẫn | −3.389 | −3.389 |
| 2 | Trọng số đất 20/50/30 → 25/50/25 | ĐÚNG, áp: nhánh xấu ~31 ha/năm đã là tốc độ 2025 (28,6 ha) nên nghiêng thêm là đếm hai lần; DT chưa thực hiện +1.701,8 trong 9T26 là dữ kiện chiều lên | +1.186 | +1.186 |
| 3 | Trục thu hồi 60% sang độ nhạy | ĐÚNG, áp: chỉ là nhận định [UL], trùng "đền bù tăng" trong nhánh 6 tỷ/ha; base NPV0 = 100% | +572 | +556 (khác thứ tự áp) |
| 4 | Tài sản sổ sách bị định giá 0: góp vốn khác 305,0 + phải thu thanh lý BCC 74,3 + uỷ thác MB Capital 17,5 | ĐÚNG, áp theo sổ (luật 20). Đã kiểm 305,0 = 321,2 − DP 16,2 (TM4c). VAT khấu trừ − DTL (+3.123) để ở độ nhạy vì chưa đọc thuyết minh | +1.616 | +1.617 |
| 5 | KTPL trên LN phân bổ từ DT chưa thực hiện | ĐÚNG, áp (×(1−NCI LN) cho nhất quán nhánh đất) | −563 | −563 |
| 6a | 937,1 ha là số 31/12/2025, đất cho thuê 9T26 bị đếm đôi | ĐÚNG hướng nhưng chưa có số ha (G12) ⇒ độ nhạy: mỗi 50 ha −756. Thiên lệch đã biết là XUỐNG | độ nhạy | −757 |
| 6b | Bản "mất trọn tạm ứng" trừ một tài sản không có trong mô hình | ĐÚNG. **Taylor sửa thêm** (skeptic không đề xuất): tạm ứng 643,7 (TM7, mục đích mua đất) đưa vào base theo giá vốn như chi phí đất (luật base = sổ sách; chiết khấu quản trị [UL] ⇒ độ nhạy, base 0%). Mất trọn = bản song song | +826 | — |
| 7 | Độ nhạy GPM đỉnh, NCI 9,9% | Độ nhạy, không vào tâm. Số khác skeptic vì cách đo khác: GPM ×0,9457 trên LN gộp vận hành −1.228 (skeptic −1.840); NCI cố định 9,9% thay cả trục +1.735 (skeptic +879) | — | — |
| 8 | WARNING bên liên quan VRG | Mang theo (chưa tự kiểm BKS/An Lộc) | — | — |
| 9 | Giá 50.100; nguồn BCTC | Giá từ BQ 06/11. PDF BCTC Q3 là ảnh scan, không có lớp text (pymupdf đọc được 423 ký tự / 49 trang) ⇒ số ngoài BQ **chưa kiểm bằng text**, chỉ đối chiếu `notes_read.md` (đọc từ ảnh) | — | — |

Không áp tạm ứng (= cơ sở của skeptic) cho tâm **53.640**, khớp điểm skeptic 53.653 (lệch −13 do giá/CK 06/11).

## Headline và các bản thay thế (song song, không thay headline)
| Bản | Tâm | P10 | P90 |
|---|---|---|---|
| **Headline r3** | **54.466** | 43.257 | 69.818 |
| Tạm ứng = 0 (như skeptic) | 53.640 | 42.640 | 68.745 |
| Mất trọn tạm ứng, p0,15 [UL] | 53.949 | 42.688 | — |
| Chiết khấu quản trị 10% [UL] | 49.020 | — | — |
| Quy ước r2: RONIC = ROE5Y | 57.855 | — | — |
| Trọng số đất r2 20/50/30 | 53.242 | — | — |

Đây là ba số khác nhau, không lẫn: tâm 54.466 là kỳ vọng của lưới; P50 53.085 là trung vị các kết cục; giá trị tại tham số trung tâm là 53.919. P10 gần như do nhánh đất XẤU quyết định (94%). P90 do riêng nhánh đất TỐT (trọng số 0,25).

## Độ nhạy (Δ tâm, không vào tâm)
VAT khấu trừ 890,5 − DTL 123,7 theo sổ **+3.123** · mỗi 50 ha đã cho thuê 9T26 **−756** · thu hồi 60% p0,25 **−655** · GPM về TB 2019–25 **−1.228** · NCI con cố định 9,9% (theo BCĐ) **+1.735** · bỏ tạm ứng **−826**.
Theo r: −100bp 57.161 (+4,9%) · +100bp 52.095 (−4,4%).
**Giá ngụ ý**: giá 50.100 tương ứng tỷ/ha ròng ×0,692 (nhánh cơ sở 8,30 thay vì 12 tỷ/ha), HOẶC r 15,45%.

## Lưới
7 trục độc lập, 1.458 kết cục. Đất (25/50/25) × tỷ/ha ×0,75/1/1,25 × g 2/3/4% (trục này không còn tác dụng khi RONIC=Ke) × lỗ tín dụng không bảo đảm 0/10/30% (0,60/0,25/0,15) × NCI con 8,5/20/31% × thuế tương lai ×0,8/1/1,2 × KTPL 7,25/9,04%. Thu hồi chi phí đất cố định 100%. Phân vị ở mức kết cục bằng `_shared/wpct.py`. CK 5 tỷ: Q/ADV120 = 127%, nằm NGOÀI vùng hiệu chỉnh luật căn bậc hai ⇒ CK 1,39% có thể thấp hơn thực tế.

## WARNING (pháp lý/quản trị — không vào tâm)
Giữ toàn bộ cờ r2: tín dụng phi ngân hàng 6.016 tỷ = 116% VCSH mẹ; tạm ứng nội bộ; vay-cho-vay; cổ tức 2025 vượt LNST; nhân sự. Thêm cờ bên liên quan VRG: BCC 667 Thế Hệ Mới ↔ VRG Long Thành tới 2060; cổ phiếu Cao su VN giá gốc 129,0, giá trị hợp lý 68,6; BKS có cán bộ VRG/TGĐ NTC; cổ đông An Lộc 19,79% chưa rõ quan hệ. Lệch tạm ứng TM7 643,7 ≠ TM40 635,6.

## Việc còn mở
G12 số ha cho thuê 9T26 · thuyết minh VAT/DTL · GPM 2021 nghi chép lặp · BCC 667 giả định đã nằm trong LN gộp vận hành (chưa kiểm) · G14 NCI từng công ty con · G16 tiền thuê đất trả Nhà nước · G1/G2 danh tính bên vay · BCTC Q3 HN chưa soát xét · chưa đối chiếu PDF bằng text.
Không đủ điều kiện sleeve fear-buy (DD trung dung). Không đặt lệnh, không ghi `kb/dd_price_zones.json`.
