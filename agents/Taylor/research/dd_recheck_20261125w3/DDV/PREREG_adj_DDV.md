# PREREG_adj — DDV kiểm kê hạng mục E17 (khoá TRƯỚC khi tính; job Taylor_20261125_032443, 25/11/2026)
Phương pháp: `agents/Taylor/research/dd_adjcenter_20261124/PREREG_adj.md` (md5 ef5157cb3f762d58623ed550ebc214c7) + `PREREG_adj_v2.md` (md5 835dfc1e07f9c67ac7f6c3028b529d13), nguyên văn. File này CHỈ là kiểm kê hạng mục DDV + cách đo, không đổi phương pháp.
Mù giá. Tâm gốc = 15.911 (rev3 đề xuất = rev2 sổ + recheck, tâm không đổi). Nguồn: S = `skeptic/r1_raw.md`; B = BCTC riêng Q3/2026 `dd_DDV_20261026/src/en_p1.txt` (khôi phục `git archive ae0ff5446^`, md5 73ed59cb189fb9655457b0e276c1b2bf). DDV KHÔNG có công ty con (B:151 trống; B:479 chỉ góp 3,86% Thạch cao Đình Vũ) ⇒ BCTC riêng = bộ duy nhất (đóng mục phụ của S).

| # | Hạng mục | Hướng | Bậc | Nhánh p | Cách đo m (chạy mô hình r3, không cộng tay) |
|---|---|---|---|---|---|
| 1 | Trích quỹ KTPL hằng năm từ LNST (flow). Phân phối LN 2025 trong 9T26 (B:180,207-213): LN chưa PP 644,31 → còn 16,25 ⇒ phân phối 628,06 = quỹ ĐTPT +315,42 (B:207) + cổ tức 1.700 đ × 146,11tr = 248,39 + phần còn lại 64,25 (KTPL + khác). Quỹ KTPL 23,83 → 80,22 (+56,39 tối thiểu, chưa tính chi). Tỷ lệ = [56,39; 64,25] / LNST 2025 630,83 = [8,94%; 10,19%] | ↓ | A | mặc định A (0,90 [0,75;1]) — 1 kỳ, số trực tiếp BCTC | nhân (1−k) vào LN giữa chu kỳ trước khi trừ lãi gửi + f27 dương; m điểm k = 10,19%, khoảng m theo k ∈ [8,94%; 10,19%] |
| 2 | Tồn quỹ KTPL 80,22 tỷ (nợ phải trả, B:180) chưa trừ khỏi NC 1.108 (stock) | ↓ | A | mặc định A | NC − 80,22 |
| 3 | Khoản trừ lãi gửi 35,4 (trung điểm) vs proxy lịch sử TB 2015–25 −9…+26 tỷ/năm (S, too_low; r3 §1 bước 8) | ↑ | B | 1 quan sát (một chuỗi proxy) ⇒ 0,50 [0,25;0,75] | khoản trừ cố định 8,5 (trung điểm proxy) thay trục 70,9/35,4/0; khoảng m theo khoản trừ ∈ [26; −9] |
| 4 | Capex tuân thủ bãi thạch cao (S killer; B:856 CIP gồm dây chuyền thu hồi P2O5 trong thạch cao, đã chi nằm trong sổ) | ↓ | C | — | độ nhạy mỗi 100 tỷ NPV âm |
| 5 | Mức LN giữa chu kỳ: DT FY2025 đỉnh (TB 2021–25 → 12.452) vs NP TB 2021–25 284 > 229 / LTM 6.406 → 17.254 | ↕ | C (hai chiều, có số ngược nhau — không xác định dấu) | — | độ nhạy r3 §2 |
| 6 | Tiền ròng bị giữ (Vinachem 64%; 2025 giữ lại 50% LN vào ĐTPT, trả 39%) — kiểm chéo vốn hoá 11.555 | ↓ | C (dấu có, không cận thời hạn) | — | độ nhạy r3 §2 |
| 7 | Liven 217 tỷ mất (p 0,10 [UL]) | ↓ | C | — | r3 §2 (−146) |
| 8 | KTPL trên phần lãi gửi vượt mức nhúng trong biên lịch sử | ↓ | C | — | không đo |
| L1 | r 13,5% vs dải Ke (E15) | ↑ | luật | không vào Σ | 16.854 |
| L2 | Trọng số đường 2027 (0,45/0,40/0,15; đối xứng +425) — tham số house (PREREG §4) | ↑ | luật | không vào Σ | r3 §2 |
| D | Cổ tức: không có cổ tức đã công bố chưa trả (B:168 mã 313 trống) | — | cơ học | — | 0 |
|Σ| > 5% ⇒ chạy tổ hợp trong mô hình.
