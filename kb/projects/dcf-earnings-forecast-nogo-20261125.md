---
kind: project
owner: Winston
status: closed-nogo
updated: 2026-11-25
title: "Dự báo earnings quý ↔ tâm DCF-VN — ĐÓNG NO-GO (J1→J4 + J3.1), 25/11/2026"
---
# Dự báo earnings quý ↔ tâm DCF-VN — ĐÓNG NO-GO (J1→J4 + J3.1), 25/11/2026

**Trạng thái: ĐÓNG, KHÔNG wire.** Nghiên cứu thuần; quant-skeptic chỉ chạy cho J2, J3 (cả hai REFUTED/medium, phần vá và NO-GO đứng; phần diễn giải bị bác đã sửa chữ). J4 và J3.1 chưa qua skeptic vì kết luận là NO-GO.
Nhánh `session/Taylor_20261125_011012` (worktree `wt-dcf-earnfc-20261125d`, head `c82a9971b`) — CHƯA merge; kết luận đầy đủ: `agents/Taylor/research/dcf_earnings_forecast_20261125f/REPORT.md` (trang 1), thư mục d/e/f cùng cha.

## Kết luận nên nhớ
- **ĐÚNG:** D0 lạc quan có hệ thống về earnings quý kế (R 1,27 IS / 1,18 OOS so với naive mùa vụ). Một ensemble đơn giản (ENS) hơn naive ~10–12% ở h=1–2, không hơn từ h≥3 — công cụ hiển thị, không phải alpha.
- **Gap tâm-giá chủ yếu = "ROE 5 năm ≠ ROE hiện tại"** (đại số persistence, gần hằng đẳng thức kế toán, KHÔNG phải phát hiện). Giá thêm thông tin nhỏ: IC −0,055 IS / −0,054 OOS sau kiểm soát đủ (số cũ −0,132/−0,108 gấp đôi, đã sửa). `nlv` dùng cùng `rim_vb` với D0 nên không phải null độc lập.
- **Chu kỳ hàng hoá/ngành CÓ ảnh hưởng lớn tới sai số earnings, nhưng KHÔNG biến được thành dự báo/định giá tốt hơn E/P hay ENS.** "D0 lạc quan ở đáy, bi quan ở đỉnh" chỉ là đại số persistence; "mã chu kỳ → neo D0, còn lại → E/P" chỉ đúng IS 6/6, OOS E/P ≥ D0 (IC36 0,1665 vs 0,1468; D0 thắng 1/4 năm), lập sau khi thấy số, N hiệu dụng ~3–4 ⇒ **KHÔNG phải ứng viên PREREG**.
- **NO-GO:** vòng cập nhật tâm C1–C5 (không biến thể nào ≥ E/P); dự báo có chu kỳ (pha, giá hàng hoá World Bank — tệ hơn naive OOS 1,336, ROE 8 năm); chu kỳ ngành LOO từ BCTC (J4: cả 5 biến thể thua E/P ~−0,036…−0,039 IC36 OOS; tốt nhất M4 capex ngành hơn null persistence chỉ +0,0019 IC36 ≈ 1%, 3/4 năm, DSR 0,765).
- Null persistence P1 dự báo ROE tốt hơn D0 (R² OOS 0,305 vs 0,217) nhưng xoá thông tin xếp hạng riêng của D0 (IC phần dư −0,002 vs +0,089) ⇒ không thay tâm D0.

## ⚠️ Caveat khi trích dẫn
- J4: bug chỉ số LOO được sửa SAU khi thấy số; bản lỗi cho NO_NEW=true, bản sửa lật thành false (M4/M2 đạt 3/4 năm). Kết luận thực dụng giữ nguyên (độ lớn ~0) nhưng tiêu chí dừng không còn "sạch". 3 lựa chọn chưa ghi trong PRELOCK_J4: mẫu fit chỉ `in_universe`; S1 mức (M1) vs hạng (M2–M5); capex `|capex_ttm|`.
- Không có chuỗi giá ngành PIT phủ IS 2014–2019 ngoài World Bank (đã tra `data_registry`). **Muốn đi tiếp về chu kỳ phải THU THẬP DỮ LIỆU** (giá/tồn kho ngành PIT từ 2014 — việc Winston), không phải thêm biến thể mô hình. Đừng mở lại hướng này bằng biến thể mới trên dữ liệu hiện có.

## Dùng được gì (display-only)
- Panel **V3.2** (vá mc ảo, md5 `a24678ff0a8b2166ac3328624cc0cd13`, 609/56.549 dòng in_universe 2014+ đổi) thay V3.1 cho mọi lần chạy lại nhánh DCF-VN; |ΔIC36| ≤ 0,006, không kết luận nào đổi.
- Dòng chẩn đoán "ROE TTM vs ROE 5 năm" cạnh tâm D0 (ROE TTM < ROE 5 năm ⇒ D0 gần chắc quá lạc quan quý kế); ENS h=1 nếu cần số LNST quý kế để hiển thị.
- E/P vẫn là thước phải vượt ở mọi tập con OOS kể cả mã chu kỳ.

Chỉ đạo user 25/11 09:15 ICT: thử hướng C, nếu không có gì mới thì quay lại A rồi B (file này = B).
