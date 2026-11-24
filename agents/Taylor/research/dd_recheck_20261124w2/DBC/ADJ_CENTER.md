# DBC — Tâm kỳ vọng điều chỉnh (E17, 24/11/2026, job Taylor_20261124_131354)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`), `calc/calc_adj.py` assert cả hai + md5 mô hình rev4. Chạy lại mô hình rev4 (CONTROL 17.673; tái lập 13.767 / 17.134 / 16.594 của rev4) với tỷ lệ vốn chủ tài trợ TÁCH cho XDCB và BĐS dở dang. 2 lần chạy trùng md5 `78596fdf…`. MÙ GIÁ. Tâm gốc 17.673 (proposal rev4 = sổ rev3). `skeptic_final` REFUTED_OPEN = trạng thái phản biện (r4 DD_GENERAL), không phải quan điểm đầu tư.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 16.439 đ/cp (dải 14.828–17.542; −6,98% so với tâm base); căn cứ 3 hạng mục bậc B.**
|Σ tuyến tính| = 7,13% > 5% ⇒ dùng TỔ HỢP chạy lại mô hình (−6,98%). Cổ tức tiền 2025 đã là nợ phải trả ⇒ không có dòng cơ học.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | XDCB tài trợ một phần bằng vay đặc thù: lãi vốn hoá 9,5 tỷ (2025) / 21,7 tỷ (2024) ÷ lãi BQ 4,51–4,56% ⇒ nợ đặc thù = 15% / 61% XDCB BQ ⇒ f_XDCB 0,62 [0,39; 0,92]; BĐS không vốn hoá lãi ⇒ f_BĐS 1 | ↓ | −8,95 [−14,83; −1,87] | B | 0,50 [0,25; 0,75] | −4,48 |
| 2 | BĐS dở dang 1,0× sổ sách dù DT BĐS 21,4 tỷ/năm vs 1.114 tỷ: haircut thời gian 33% [20; 40] | ↓ | −5,04 [−6,11; −3,05] | B (≥3 kỳ) | 0,65 [0,40; 0,90] | −3,27 |
| 3 | Lá chắn lỗ thuế 647 tỷ (129,4 tỷ) cho cả 3 kịch bản thay vì chỉ "tốt" | ↑ | +1,25 | B | 0,50 [0,25; 0,75] | +0,62 |
| | **Σ tuyến tính / tổ hợp** | | | | | **−7,13 / −6,98** |

Nguồn #1: `src_ocr/kt25_en_p34_ocr.txt:51-55` ("capitalized borrowing costs amounting to VND 9.5 billion (2024: VND 21.7 billion). These borrowing costs relate to specific borrowings taken to finance the construction of fixed assets"; ảnh `src_ocr/kt25_en_p34.png`), lãi vay LCTT `kt25_en_p12_ocr.txt:48` (261,1 / 263,7 tỷ), nợ vay BQ `ticker_financial` StDebt_P0+LtDebt_P0 Q4/23–Q4/25. Lãi vay đặc thù đã vốn hoá (không qua LNST) ⇒ KHÔNG cộng lại lãi vào LN.

## 2. Chỉ độ nhạy — không vào tâm
| Hạng mục | Độ nhạy | Lý do |
|---|---|---|
| Leverage-neutral 53% (skeptic r4) cho cả XDCB+BĐS | không cộng lại lãi 14.023 (−20,65%); có cộng lại lãi nợ chung 15.470 (−12,47%) | quy ước phân bổ, trái dữ kiện vốn hoá; bản không cộng lại lãi đếm hai lần chi phí nợ |
| [LUẬT] r 13,5% vs dải Ke (E15) | 19.669 (+11,29%) | V1 |
| [LUẬT] trượt cửa sổ ROE Q4/26 | +14,1…+20,1% cơ học | cửa sổ khai trước |
| EPR tái chế bao bì | −1,5…−4,5% | C (chưa có số) |
| Hết miễn giảm thuế | −3,0…−9,5% | C (skeptic r4: pass) |
| Quỹ đất trên giá gốc | chưa có số | C, chiều lên |
| TSSH / ESOP 2026 | −1,2…−2,4% / 17.595–17.444 | C |
| Phải thu NLĐ 237,1 tỷ | −539 đ/cp | WARNING |

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
| Sự kiện | Khi nào | Đổi gì | Δ tâm adj |
|---|---|---|---|
| **Thuyết minh vay/XDCB KT26: lãi vốn hoá + khoản vay đặc thù dự án** | ~03/2027 | #1 B→A p 0,9: f_XDCB thật (f 0,39 ⇒ 15.053; 0,92 ⇒ 17.343 cho riêng hạng mục) | ≈ −3,6% … +3,2% |
| Bàn giao BĐS có biên ≥20% / người mua trả trước | mỗi BCTC | #2 p 0,65→0,35 | ≈ +1,5% |
| Dở dang BĐS >1.400 tỷ, DT BĐS <50 tỷ/năm, hoặc trích lập | mỗi BCTC | #2 p→0,9 | ≈ −1,3% |
| BCTC Q4/26: LNST ≥120 tỷ, không trích TSSH / <−50 tỷ | ≤ 30/01/2027 | trọng số kịch bản 15/50/35 hoặc 35/50/15 | ±8,2% |
| KT26: dùng thêm lỗ chuyển sang | ~03/2027 | #3 p 0,5→0,65 | +0,2% |
| KT26 TM35: số EPR | ~03/2027 | C→A nếu >30 tỷ/năm | −4,5% |
| Lãi huy động 12T ±50bp | liên tục | r (V1) | −3,8% / +4,3% |

**Điều kiện đổi số quan trọng nhất:** tỷ lệ XDCB tài trợ bằng vay (thuyết minh vay/XDCB KT26) — hạng mục lớn nhất, dải m rộng nhất.
