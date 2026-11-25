# VLB — Tâm kỳ vọng điều chỉnh (E17, 25/11/2026, job Taylor_20261125_032448)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`); `calc/calc_adj_vlb.py` assert cả hai + md5 mô hình rev4 (`05cc0943…`), CONTROL 45.161. 2 lần chạy trùng md5 (`calc/run1.txt` = `run2.txt`, `77755633…`). MÙ GIÁ. Tâm gốc 45.161 (proposal rev5 = sổ rev4). `skeptic_final` REFUTED_OPEN = trạng thái phản biện (r3 DD_GENERAL INCONCLUSIVE), không phải quan điểm đầu tư.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 43.626 đ/cp (dải 40.056–45.906; −3,40% so với tâm base); căn cứ 4 hạng mục bậc B.**
|Σ tuyến tính| = 3,40% ≤ 5% ⇒ dùng cộng tuyến tính (kiểm tra tổ hợp nội suy tham số: 43.505, −3,67% — chênh 0,27pp, ghi nhận). Cổ tức tạm ứng 2.500 đ đã GDKHQ 19/11 ⇒ tâm đã ex-div, không còn dòng cơ học.

## 1. Hạng mục vào tâm (m = % tâm base, chạy lại mô hình rev4 từng hạng mục)
| # | Hạng mục | Hướng | m điểm [thấp; cao] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| I1 | Neo giữa chu kỳ: cơ sở mid = TB lõi FY24/FY25 (238,6) thay lõi FY25 265,05; kịch bản xấu = lõi FY24 212,1 phẳng thay 250. Thấp: mid = lõi FY24; cao: chỉ đổi mid | ↓ | −4,79 [−7,46; −2,67] | B | 0,35 [0,15; 0,55] — có quan sát NGƯỢC bằng số (9T/26 lõi năm hoá 352,8; Q3/26 403,0) | −1,68 |
| I2 | Phải trả NLĐ 54,215 tỷ (mùa vụ, chi Tết) trừ ngay thay vì tất toán khi đóng mỏ. Thấp: thêm 26% số dư VLĐ còn lại (co theo LN fade) trả ở năm 2,5 | ↓ | −1,96 [−2,51; −1,96] | B | 0,50 [0,25; 0,75] — 1 quan sát (số dư 30/9) | −0,98 |
| I3 | Chênh dòng tiền vs LNST = khấu hao − chi TSCĐ + tăng giảm chi phí trả trước (đền bù đất qua CFO): 2024 +29,07 · 2025 −72,35 · 9T/26 +9,76 ⇒ TB 2,75 năm **−12,19 tỷ/năm** [2025–9T26: −35,77; 9T26 năm hoá: +13,01], theo tỷ trọng mỏ còn hoạt động, PV @13,5% | ↓ | −3,26 [−9,56; +3,48] | B | 0,35 [0,15; 0,55] — 3 kỳ, dấu trái nhau | −1,14 |
| I4 | Năm 1 cơ sở xuất phát từ lõi Q3/26 ×4 = 403,0 thay TTM 357,4 (fade 2 năm giữ nguyên). Thấp: 9T/26 năm hoá 352,8 | ↑ | +1,14 [−0,11; +1,14] | B | 0,35 [0,15; 0,55] — ngược: 9T/26 năm hoá < TTM; KH 2026 LNTT 275 | +0,40 |
| | **Σ tuyến tính** | | | | | **−3,40** |

Nguồn: I1 — `dd_VLB_20261122/skeptic/r3_raw.md:9-14` + `model/dcf_vlb_r4.py` (OP_FY24/OP_FY25 từ KT25 tr.13); I2 — `dcf_vlb_r4.py:30` (wc_liab 54,215) + `r3_raw.md:16-18`; I3 — `src/BCTC_KiemToan_2025.pdf` tr.14 PDF (LCTT mã 02/12/21), `src/BCTC_Q3_2026.pdf` tr.6 PDF (mã 02/12/21), BCTN 2025 tr.54-55 (đền bù 71,883 tỷ/47.417,8 m²) + `r3_raw.md:29-36`; I4 — `src/BCTC_Q3_2026.pdf` tr.5 PDF (mã 30, 21) + `r3_raw.md:26-27`.
Chống đếm hai lần: I3 GỘP "khấu hao không cộng lại" (↑) và "đền bù diện tích còn lại" (↓) của r3 vì là cùng một dòng tiền (đền bù trả qua chi phí trả trước, phân bổ vào LNST); phần có lịch sử vào I3, phần vượt lịch sử = C. I1 (mức giữa chu kỳ) và I4 (điểm xuất phát năm 1) tác động hai tham số khác nhau của cùng đường LN — tổ hợp kiểm tra chênh 0,27pp.

## 2. Chỉ độ nhạy — không vào tâm
| Hạng mục | Độ nhạy | Lý do |
|---|---|---|
| [LUẬT] r 13,5% vs dải Ke (E15) | 47.142 (+4,39%) | V1 — tham số luật, không vào Σ |
| Đền bù phần diện tích còn lại trong ranh GP VƯỢT mức lịch sử (BCTN 2025: "gặp khó", chủ đất chưa đồng ý giá) | ước lượng skeptic 90–130 tỷ ≈ −4…−6% | C — chưa có diện tích/đơn giá còn lại (đơn giá 2025 ≈ 15,2 tỷ/ha chỉ là một giao dịch) |
| Kịch bản tốt gia hạn 3 mỏ không tính tiền cấp quyền/đền bù mới | chiều xuống, chưa có số | C |
| Bù trừ chiết khấu @13,5% | −1,5% (trước CK, rev4) | đếm hai lần với kịch bản xấu (bù trừ = 0) |
| Dư bù trừ được hoàn / ký quỹ = 0 | +494 / −65 đ/cp | C (rev4 §7) |
| Truy thu tiền cấp quyền kiểu 2022 | −4.623 đ/cp trên kịch bản xấu | STRESS + HARD ABANDON |

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
| Sự kiện | Khi nào | Đổi gì | Δ tâm adj |
|---|---|---|---|
| **BCTC Q4/2026: lõi Q4 (LN thuần HĐKD − DTTC)** | ~20/01/2027 | lõi năm 2026 ≥ 400 ⇒ I4 p 0,35→0,65, I1 p→0,15 | ≈ +1,3% (ước lượng: +0,34 +0,96 pp) |
| | | lõi Q4 năm hoá ≤ 265 (mức giữa chu kỳ) ⇒ I1 p→0,65, I4 p→0,15 | ≈ −1,7% (−1,44 −0,23 pp) |
| BCĐKT 31/12/2026: phải trả NLĐ | ~20/01/2027 | giảm ≥50% so 54,2 (mùa vụ) ⇒ I2 B→A p 0,9 / còn ≥54 ⇒ p 0,25 | −0,8% / +0,5% |
| **LCTT KT 2026: chi phí trả trước + chi TSCĐ vs khấu hao** | ~03/2027 | chênh 2026 ≥ 0 ⇒ I3 p 0,15; đền bù mới ≥50 tỷ ⇒ p 0,65 | +0,7% / −1,0% |
| CBTT đền bù/thuê đất phần diện tích còn lại có số tiền | bất kỳ | C → A (vào tâm theo số) | ≈ −4…−6% nếu 90–130 tỷ (ước lượng skeptic) |
| Văn bản gia hạn GP TT2/TC1/TP1 tới hết trữ lượng | bất kỳ CBTT | kịch bản cơ sở +6,3% (rev4) | ≈ +3% tâm (ước lượng: w cơ sở 0,5) |
| TB truy thu/huỷ khoản bù trừ | bất kỳ | HARD ABANDON | −3.423 đ/cp cơ sở (rev4) |
| Lãi huy động 12T ±50bp | liên tục | r (V1) | −1,70% / +1,77% |

**Điều kiện đổi số quan trọng nhất:** lõi Q4/2026 (BCTC ~20/01/2027) — quyết định cả I1 (giữa chu kỳ) lẫn I4 (điểm xuất phát), hai hạng mục cùng đường LN.
