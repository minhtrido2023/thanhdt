# PVT — kiểm kê hạng mục E17 (KHOÁ TRƯỚC khi tính; theo PREREG_adj.md md5 ef5157cb3f762d58623ed550ebc214c7 + PREREG_adj_v2.md md5 835dfc1e07f9c67ac7f6c3028b529d13)
Nguồn: S = `skeptic/r1_raw.md` (REFUTED medium); T = text BCTC HN Q3/2026 `dd_PVT_20261029/src/q3_pvt_hopnhat_text.txt` (khôi phục `/tmp/ddrestore_PVT`); H = `dd_redo_20261105/PVT/calc/bq_hist_out.csv` (BQ NP_P0 phần mẹ). MÙ GIÁ.
Tâm base = 18.956 (r3 + D4 RONIC = Ke, sau CK 0,6711%). Mọi hạng mục chạy QUA mô hình (`calc/calc_adj.py`, cùng `value_ps` D4).

| # | Hạng mục | Hướng | Bậc | m (đầu vào mô hình) | Nhánh thang p |
|---|---|---|---|---|---|
| P1 | Trích quỹ KTPL từ LNST mẹ (S killer). Quan sát: (i) FY2025 bảng biến động VCSH "Phân phối quỹ": LNST chưa PP −259,18, quỹ ĐTPT +177,54, NCI −26,99 ⇒ ra khỏi VCSH 108,62 (mẹ 81,63) = 7,47% LN mẹ 2024 (1.093,2, H) (T:3875–3877); (ii) 9T/26 "Điều chỉnh khác" mẹ −150,33, NCI −58,69 ra khỏi VCSH (= 14,5% LN mẹ 2025 1.037,77) và quỹ KTPL mã 323 tăng 183,60 → 220,57 (T: bảng VCSH + BS) — thành phần (iii) chưa tách KTPL/khác | xuống | B | tỷ lệ k nhân vào mọi dòng LN mẹ (Q4/26, LN 2027, terminal): k = 7,47% [7,47%; 14,5% (ước lượng, thành phần chưa tách)] | 2 kỳ cùng hướng ⇒ mặc định 0,50 [0,25; 0,75] |
| P2 | LN mẹ Q3/2026 × 4 (cơ sở LN 2027 và Q4/26) gồm hoàn nhập dự phòng sửa chữa lớn phi tiền mặt theo TT99: 85,4 tỷ/9T (r3 §5) ⇒ năm hoá × (1 − NCI 19,6%) × (1 − 20% thuế) = −73,2 tỷ/năm phần mẹ | xuống | B | np27 −73,2; Q4/26 −18,3 [np27 −36,6 (nửa); −73,2] | 1 kỳ (9T/26) ⇒ mặc định 0,50 [0,25; 0,75] |
| C1 | Chi dry-dock tiền mặt (tuân thủ đăng kiểm) vượt/thấp hơn hoàn nhập | xuống | C | không có số theo năm | chỉ độ nhạy |
| C2 | Ý kiến kiểm toán FY2025 / soát xét H1 chưa kiểm | xuống | C | không có văn bản | chỉ độ nhạy |
| C3 | NPV tàu mua thêm (hợp đồng captive PVN) / quyền mua PDV chiết khấu | lên | C | không có số độc lập | chỉ độ nhạy |
| C4 | Đáo hạn hợp đồng TC/spot | hai chiều | C | chưa có | chỉ độ nhạy |
| C5 | Q4 mùa vụ cao hơn Q3 | lên | C | không có bằng chứng | chỉ độ nhạy |
| L1 | r 13,5% > dải Ke (E15 20.798, +9,72%) | lên | luật | không vào Σ | — |
| L2 | Terminal RONIC = Ke (D4) | — | luật | không vào Σ (đã trong base) | — |
Chống đếm hai lần: P1 (phân phối LN cho người lao động) ≠ P2 (chất lượng LN kế toán phi tiền mặt); P1 áp trên LN đã trừ P2 (tích (1−k)), không cộng tuyến tính. Cổ tức: 9T/26 chia cổ phiếu (đã vào SH 516,9 tr); không có cổ tức tiền đã công bố chưa GDKHQ trong nguồn (chưa kiểm sau 08/11).
