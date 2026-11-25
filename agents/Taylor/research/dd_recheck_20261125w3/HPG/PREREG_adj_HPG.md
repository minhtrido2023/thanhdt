# PREREG_adj — HPG kiểm kê hạng mục E17 (khoá TRƯỚC khi tính; job Taylor_20261125_032443, 25/11/2026)
Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 ef5157cb3f762d58623ed550ebc214c7) + `PREREG_adj_v2.md` (md5 835dfc1e07f9c67ac7f6c3028b529d13), nguyên văn. Lý do áp E17 dù skeptic r1 CONFIRMED: còn hạng mục "thiếu" chưa đóng (missing_items fail dưới ngưỡng: KTPL, capex môi trường) — V9.
Mù giá. Tâm gốc 21.338. Nguồn: S = `skeptic/r1_raw.md`; N = `dd_HPG_20261031/calc/notes_bs.md` (khôi phục `git archive d73418593^`).

| # | Hạng mục | Hướng | Bậc | Nhánh p | Cách đo m (chạy hpg_r3.py, không cộng tay) |
|---|---|---|---|---|---|
| 1 | Trích từ LNST cho người không phải cổ đông: 9T26 quỹ KTPL −221,5 + thù lao HĐQT/BĐH −180,0 = 401,5 tỷ (N:94) / LNST mẹ 2025 15.453,2 (N:112) = 2,60%; riêng KTPL 1,43% | ↓ | A | mặc định A 0,90 [0,75;1] | đường LN × (1−k), k điểm 2,60%, khoảng k ∈ [1,43%; 2,60%] |
| 2 | Đếm trùng cam kết vốn: COMMIT 19.472 là số 30/06 (N:73) nhưng chi Q3 đã vào XDCB 30/09. Chi Q3 ≈ capex 9T 14.607,2 (N:44) − capex 6T phân khúc thép 8.312,9 (N:103) = 6.294,3 (ước lượng, cận trên vì 6T toàn tập đoàn ≥ thép) | ↓ | B | 1 quan sát ⇒ 0,50 [0,25;0,75] | COMMIT − 6.294,3; khoảng m theo COMMIT − [3.147; 6.294] |
| 3 | ETR thép thực 6T26 = 1.451,3 / 22.160,5 = 6,55% (N:103) thấp hơn ETR ~12% ngầm trong TAXF 0,80/0,88 ⇒ bước nhảy lên thuế 20% lớn hơn | ↓ | B | 1 kỳ ⇒ 0,50 [0,25;0,75] | TAXF = 0,80/(1−ETR); điểm ETR 6,55%, khoảng ETR ∈ [9,28% (giữa); 6,55%] |
| 4 | Nhánh TỐT đếm trùng lợi ích capex (r3 bản J; skeptic r3 08/11) | ↓ | B | 1 quan sát ⇒ 0,50 [0,25;0,75] | bản J (TỐT hưởng tiền gửi) − headline; khoảng m [½J; J] |
| C1 | Capex tuân thủ môi trường (D3) — cận trên bản I −4,1% (S); ký quỹ phục hồi MT 32,8 tỷ (N:96) | ↓ | C | — | độ nhạy |
| C2 | Mốc thuế 20%: 2030 (bản B) / vĩnh viễn ETR hiện hành (bản C) | ↕ | C | — | độ nhạy |
| C3 | KTPL ở trần 5% NQ 2026 (S) | ↓ | C | — | độ nhạy |
| C4 | Trục TLSH r2 (bản E) | ↓ | C | — | độ nhạy |
| M | Cổ tức 2026 15% chưa rõ hình thức (S): cổ phiếu ⇒ chỉ đổi cơ sở số cp khi GDKHQ; tiền ⇒ trừ cơ học | — | cơ học | — | ghi chú |
| L1 | r 13,5% vs dải Ke (E15) | ↑ | luật | không vào Σ | 23.625 |
| L2 | Vốn giữ lại vượt cam kết sinh lời = Ke thay lãi gửi 5,92% (S killer; D4/V4 diễn giải) | ↑ | luật | không vào Σ | DEP_AT = r |
| L3 | g_RI kiểu r2 (bản D) | ↑ | luật (moat) | không vào Σ | r3 |
|Σ| > 5% ⇒ tổ hợp trong mô hình.
