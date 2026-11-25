# PVT — Tâm kỳ vọng điều chỉnh (E17 / V9) · 25/11/2026 · job Taylor_20261125_032446 (resume Taylor_20261125_053004)

**Tâm kỳ vọng điều chỉnh: 18.184 đ/cp (dải 16.806–18.586; −4,07% so với tâm base 18.956); căn cứ 2 hạng mục bậc B**

- Lý do áp V9: skeptic DD_GENERAL `skeptic/r1.json` = **REFUTED (medium)** ⇒ sổ đề xuất `REFUTED_OPEN`.
- Phương pháp khoá trước: `PREREG_adj.md` (md5 `ef5157cb3f762d58623ed550ebc214c7`) + `PREREG_adj_v2.md` (md5 `835dfc1e07f9c67ac7f6c3028b529d13`); kiểm kê hạng mục mã này khoá TRƯỚC khi tính ở `ADJ_PREREG_PVT.md` (md5 `9d8b4c5385260ad40c863a206eba5c67`, assert trong code).
- Tính: `calc/calc_adj.py` — mọi hạng mục chạy QUA mô hình r3 + D4 (cùng `value_ps` của `calc_recheck.py`, lưới 90 kết cục, sau CK 0,67%). CONTROL: `pvt_r3_out.txt` md5 `23f5090f…` = LOCK r3; tâm base tái lập 18.956 (assert). Hai lần chạy trùng byte (`calc/adj_run1.txt` = `adj_run2.txt`, md5 `65e243bd…`). P1 nhân (1−k) lên LN đã trừ P2 ⇒ tổ hợp chạy qua mô hình −4,072% vs cộng tuyến tính −4,085%. |Σ| = 4,07% < 5%.
- MÙ GIÁ: không đọc giá thị trường khi dựng.

## Hạng mục vào tâm
| # | Hạng mục | Hướng | Bậc | Đầu vào [dải] | m % tâm | p [dải] | p×m | Nguồn |
|---|---|---|---|---|---|---|---|---|
| P1 | Trích quỹ KTPL từ LNST mẹ — FY2025 "Phân phối quỹ" ra khỏi VCSH phần mẹ 81,63 tỷ = 7,47% LN mẹ 2024; 9T/26 "Điều chỉnh khác" mẹ −150,33 (14,5% LN mẹ 2025, chưa tách KTPL/khác), quỹ KTPL mã 323 183,60 → 220,57 | xuống | B (2 kỳ cùng hướng) | k = 7,47% [7,47%; 14,5% (ước lượng)] nhân vào mọi dòng LN mẹ | −7,47% | 0,50 [0,25; 0,75] | **−3,74%** | S killer; T bảng biến động VCSH FY25 + 9T/26, BS mã 323; H |
| P2 | LN mẹ Q3/26 × 4 gồm hoàn nhập dự phòng sửa chữa lớn phi tiền mặt (TT99) 85,4 tỷ/9T ⇒ phần mẹ sau thuế −73,2 tỷ/năm | xuống | B (1 kỳ) | np27 −73,2, Q4/26 −18,3 [np27 −36,6; −73,2] | −0,70% | 0,50 [0,25; 0,75] | **−0,35%** | r3 §5; T |
| | **Σ (qua mô hình)** | | | | | | **−4,07%** | |

Dải 16.806–18.586 = tổ hợp chạy qua mô hình, mỗi hạng mục ở cực trị (p, m) cho tâm nhỏ nhất / lớn nhất. Đóng góp cực trị: P1 [−10,88%; −1,87%], P2 [−0,53%; −0,09%]. Không có hạng mục chiều LÊN đạt bậc ≥ C+ (skeptic cũng ghi "không tìm thấy khoản tăng nào có bằng chứng độc lập") — các khoản lên nằm ở bậc C bên dưới, cùng chuẩn bằng chứng với chiều xuống.

## Chỉ độ nhạy (bậc C — KHÔNG vào tâm)
- C1 Chi dry-dock/đăng kiểm tiền mặt vượt/thấp hơn hoàn nhập (xuống): không có số theo năm.
- C2 Ý kiến kiểm toán FY2025 / soát xét H1 (xuống): chưa có văn bản (độ nhạy np27 1.250 ≈ −335 đ ở r3).
- C3 NPV tàu mua thêm theo hợp đồng captive PVN / quyền mua PDV chiết khấu (lên): không có số độc lập.
- C4 Đáo hạn hợp đồng TC/spot (hai chiều): chưa có.
- C5 Q4 mùa vụ cao hơn Q3 (lên): không có bằng chứng.

## Tham số luật (KHÔNG vào Σ)
- L1 r 13,5% > dải Ke: Tâm @ Ke 12,3% = 20.798 (+9,72%) — dòng E15 ở REPORT_recheck §0.
- L2 Terminal RONIC = Ke (D4) — đã nằm trong base.
- Cổ tức: 9T/26 chia cổ phiếu (đã vào SH); không thấy cổ tức tiền đã công bố chưa GDKHQ trong nguồn (chưa kiểm sau 08/11) ⇒ một dòng tâm.

## Bảng điều kiện đổi số
| Sự kiện / dữ kiện | Ngày dự kiến | Hướng | Δ tâm điều chỉnh |
|---|---|---|---|
| NQ ĐHĐCĐ 2027 / BCTC kiểm toán 2026 công bố tỷ lệ trích KTPL ≈ 7,5% (P1 lên A, p 0,90) | ~03–04/2027 | xuống | −3,10% (≈ −564 đ) |
| — tỷ lệ trích thực ≈ 14,5% (toàn bộ "điều chỉnh khác" 9T/26 là KTPL), p 0,90 | như trên | xuống | −9,68% (≈ −1.760 đ) |
| Thuyết minh cho thấy không trích KTPL từ LN mẹ (P1 đóng, k = 0) | BCTC năm 2026 | lên | +3,88% (≈ +706 đ) |
| BCTC năm 2026 xác nhận hoàn nhập TT99 lặp lại cả năm (P2 lên A, p 0,90) | ~03/2027 | xuống | −0,28% (≈ −51 đ) |
| Chi dry-dock tiền mặt ≈ hoàn nhập (P2 đóng) | BCTC năm | lên | +0,35% (≈ +64 đ) |
| Ý kiến kiểm toán FY2025 ngoại trừ / điều chỉnh LN (C2 lên A/B) | khi đọc được | xuống | chạy lại np27 (rev mới); np27 1.250 ⇒ ≈ −335 đ |
| Hợp đồng TC đáo hạn / giá cước tàu dầu đảo chiều (C4) | theo hợp đồng | hai chiều | chạy lại trục kịch bản (rev mới) |

Nhãn `skeptic_final` = REFUTED_OPEN là trạng thái phản biện, KHÔNG phải quan điểm đầu tư. Tâm điều chỉnh KHÔNG thay tâm base trong sổ/luật 0,85×tâm/luật 4; watch chỉ dùng để SIẾT đáy.
