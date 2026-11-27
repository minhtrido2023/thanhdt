---
kind: dd
owner: Taylor
status: closed
updated: 2026-11-14
title: "PAT — DD làm lại KHÁCH QUAN, mù giá thật (rev3, 14/11/2026) — kết quả"
---
# PAT — DD làm lại KHÁCH QUAN, mù giá thật (rev3, 14/11/2026) — kết quả
Brief: `kb/projects/pat-dd-redo-objective-20261114.md` (user 14/11 23:04 ICT). Topic Discord 1571194491489091644.

## Quy trình đã chạy (agent stateless, mù giá, không dùng Taylor có memory)
A. Fact pack 4 agent song song (Sonnet): F1 kế hoạch/giải trình/cổ tức, F2 giá vốn/DLC/vụ án, F3 quặng/thuế/đối thủ/điện, F4 chuỗi BQ 19 quý + hồi quy. Lọc từ khoá giá/PE/vốn hoá: sạch. `agents/Taylor/research/dd_PAT_objective_20261114/factpack/`.
B. Valuer Opus mù giá: khoá `assumptions_objective.md` md5 `4a177526f4fd099744aff766a2b1d3e0` → tâm 83.800 (76.700–102.600).
C. 2 skeptic mù giá (lạc quan / bi quan, Opus): lạc quan REFUTED (tâm hiệu chỉnh 65–78k), bi quan INCONCLUSIVE (92–96k); 0 lỗi dữ kiện (17–18 số khớp ảnh BCTC). Hai chiều chỉ cùng điểm: cây kịch bản sai (xác suất bất lợi vượt trần ≤0,125; thiếu nhánh "quặng chưa giải, giá giữ").
Đính chính 1 vòng: agent Opus MỚI khoá `assumptions_objective_r2.md` md5 `f2eb154f22bdbd38db92cb240d60235a` (17:06Z) → **FINAL_r2.md**.

## Kết quả cuối (r2, trước chiết khấu thanh khoản)
Tâm 64.700 đ/cp; P25–P75 49.600–79.200; P10–P90 36.200–100.200; tiền ròng 14.300 đ/cp trong đó. LNST bền vững cơ sở: EBIT 2027 123 tỷ, dài hạn 172 tỷ.
Chênh so bản gốc 83.800 (−19.100): thuế XK netback kênh DLC −9.900; nút quặng O3 −8.900; nút giá thực hiện −7.000; điện −3.100; DV/khác 9T −3.000; tiền ròng −2.300; cốc dài hạn TB 2023+ **+7.000**; thuế giữ 10% (xs 0,10) +2.200.
Điểm KÉM CHẮC NHẤT: (1) nút T giá DLC trả sau 01/01/2027 (xs 0,65/0,25/0,10, lập luận kinh tế/quản trị, CHƯA có văn bản; tài liệu lật: tờ trình GD bên liên quan ĐHĐCĐ 12/05 & 14/08/2026); (2) nút P truyền dẫn giá TQ→PAT chưa xác lập (nếu giữ giá: ~71.700; ±5% giá ⇒ ±38% giá trị); (3) nút O; (4) giá/tấn không xác định ±7pp (chưa có sản lượng).

## So với giá (SAU khi khoá)
Giá đóng cửa 13/11/2026 = 71.000 (BQ ticker, ORDER BY time DESC): cao hơn tâm 9,7%, TRONG vùng P25–P75; không có biên an toàn. Cổng luật 02/11 #4 (giá < 0,85×tâm = 54.995): KHÔNG đạt.

## Đã GỠ vì thiếu bằng chứng
Chiết khấu chuyển giá DLC (còn là WARNING −48.600 nếu DLC trả dưới netback 5%); phạt/truy thu vụ án; 42,6 tỷ cầm cố cho công ty thành viên (WARNING, −1.700); hoàn nguyên đất; hỗ trợ giá quặng (chỉ trong O1); mở rộng sản lượng; moat; giải phóng VLĐ; "giá/tấn đi ngang từ DV mua ngoài" làm bằng chứng (mâu thuẫn ±7pp).
