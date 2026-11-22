# THESIS CARD — FPT (A1, 22/11/2026) · chỉ đọc, không đổi định giá/lệnh/stop

**Giá mới nhất 20/11: 45.000 — DƯỚI đáy vùng rev3 (45.270) 0,6%, thấp hơn giá vốn 12,0%, đã xuyên mốc −10%.** (BQ `tav2_bq.ticker` t.ticker='FPT', đọc 22/11)

## 1. Luận điểm (rev3, `dd_price_zones.json` FPT rev 3; `REPORT_r3.md` §1)
- Giá trị kỳ vọng trọng số **57.312** (vùng P10–P90 **45.270–68.466**; lưới XẤU/CƠ SỞ/TỐT 0,275/0,45/0,275, sau CK 0,19% @5 tỷ). Lúc vào (giá 50.800) thấp hơn tâm 11,4%; 27,0% trọng số kết cục dưới giá.
- Nhãn lúc ghi: TRONG vùng. Skeptic: fundamental-skeptic lần cuối CONFIRMED (medium, 09/11). **Không đủ điều kiện fear-buy §2.5.** Với giá 45.000 hôm nay, theo ngưỡng của chính r3 §9 nhãn sẽ thành **DƯỚI vùng (<45.270)** — chưa ai chấm lại, đây là phép so ngưỡng, không phải định giá mới.
- Mong manh: chặn RONIC 5 năm ở ROIC5Y → tâm 52.311; chặn ở Ke → 50.652 (r3 §2 D5, bản G). Tâm chỉ dựa vào giả định tăng trưởng 5 năm tạo giá trị.

## 2. Mốc kiểm chứng
| Mốc | Ngày | Trạng thái |
|---|---|---|
| Cổ tức tạm ứng 1.000đ, chốt quyền | 30/11 (r3 §10); ngày GDKHQ **chưa kiểm** | giá hiện chưa điều chỉnh |
| TIME 25 phiên (vào 06/11) | 11/12 (`disc-fpt-nnc-approval` 06/11 14:19) | đã qua 11/25 phiên |
| Livermore chấm H20 | 03/12 | chấm tay |
| BCTC Q4/2026, kiểm toán 2026 | **chưa kiểm** lịch | — |

## 3–4. Điều kiện HUỶ và dữ kiện mới từ 06/11
| Điều kiện huỷ (nguồn: r2 §8/r3 §9) | Đã xảy ra? | Dữ kiện mới → tác động |
|---|---|---|
| Kiểm toán ngoại trừ/từ chối | chưa có BCTC kiểm toán mới | không đổi (chưa kiểm tin) |
| Khoản 618,8 tỷ là chi phí không thu hồi, lớn hơn đã ghi | chưa kiểm | không đổi |
| FTEL bị thu hồi/chuyển giao ngoài giá thị trường | chưa kiểm sau 01/11 (r3 §10: "chưa quét pháp lý sau 01/11") | **chưa kiểm** |
| CFO 2026 âm cả năm | chưa có số năm | không đổi |
| Mốc hạ: LN mẹ 2026 <+10% & conv <0,5; ROIC5Y | chưa có dữ liệu mới | không đổi |
| **Giá-ngụ-ý của thị trường** (r3 §5: giá 50.800 ⇔ r≈16,2% hoặc RONIC bị chặn ≈Ke hoặc trọng số XẤU ≈0,69) | giá nay 45.000 thấp hơn nữa ⇒ thị trường chiết khấu nặng hơn kịch bản XẤU của DD (P10 45.270) | **yếu đi về mặt giá-xác-nhận**; chưa phân biệt được "thị trường biết điều chưa có trong DD" với "bán tháo" |

Dữ kiện giá/khối lượng (BQ): 06/11 50.800 → 20/11 45.000 (−11,4%); VNINDEX 1.725,36 → 1.688,79 (−2,1%). Giảm liên tiếp 16–20/11 (49.400→45.000); KL 18/11 16,2M, 19/11 18,4M, 20/11 15,7M, so Volume_1M 10,3M/10,7M/11,1M ≈ 1,6×/1,7×/1,4×. Livermore (`livermore_reads` LVR-STK-2026-11-05-FPT): H20_DIR DOWN, P_TOUCH_MINUS10 0,30 (low ≤47.610) — đã xảy ra; "cancel 42.990" nêu trong brief **không tìm thấy** trong file đó. CBTT/tin FPT từ 06/11: **chưa kiểm** (không có nguồn tin trong phiên headless này).

## 5. Khoảng cách từ giá 45.000
| Mốc | Giá | Giá hiện so mốc |
|---|---|---|
| Giá vốn SpaceX (800cp, broker `costPrice`, dnse_raw 20/11) | 51.137,5 | −12,0% |
| Giá vốn ZaloPay (500cp) | 51.160 | −12,0% |
| Stop −10% SpaceX / ZaloPay | 46.023,8 / 46.044 | **đã xuyên** (thấp hơn 2,2%) |
| Đáy vùng rev3 | 45.270 | −0,6% |
| Ngưỡng luật 4 (≤0,85×tâm) | 48.715 | thấp hơn 7,6% ⇒ đạt, nhưng §2.5 vẫn không đủ ĐK |
| Tâm rev3 | 57.312 | cần +27,4% |
| Target +10% | ~56.250 | cần +25,0% |
Hệ thống đã đề xuất SELL (alert state 19–20/11); plan 20/11 hủy lệnh bán (theo brief).

## 6. Câu hỏi để user quyết (không khuyến nghị)
**Ủng hộ miễn stop:** giá ở/dưới P10 của DD, ~chạm đáy vùng; 4 điều kiện huỷ cứng chưa xảy ra (chưa có tin ngược); cổ tức 1.000đ (+2,2%) sắp chốt; luật 4 đạt.
**Chống miễn stop:** stop đã xuyên 2,2% và đà giảm kèm KL ~1,4–1,7× trung bình tháng; giá thấp hơn kịch bản XẤU ⇒ có thể thị trường biết điều DD chưa có; 3/4 điều kiện huỷ "chưa kiểm" chứ không phải "chưa xảy ra"; Livermore DOWN đúng hướng; chân trời DD (5 năm) lệch chân trời deal 25 phiên; 11/25 phiên còn 14 phiên.
Hỏi: (a) miễn stop hay giữ −10%/25 phiên? (b) nếu miễn: đặt ngưỡng huỷ thay thế nào (vd. giá < ? hoặc sự kiện nào)? (c) có chạy quét tin/pháp lý FTEL–Bộ Công an sau 01/11 trước khi quyết không?
