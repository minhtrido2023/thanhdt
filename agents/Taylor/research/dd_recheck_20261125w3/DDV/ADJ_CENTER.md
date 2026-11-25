# DDV — Tâm kỳ vọng điều chỉnh (E17/V9, 25/11/2026, job Taylor_20261125_032443)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`) + kiểm kê khoá trước `PREREG_adj_DDV.md` (md5 `215e58ec…`); `calc/calc_adj.py` assert cả ba + chân CONTROL model_r3 (stdout md5 = run1 r3) + tái lập headline 15.911. Chạy 2 lần trùng byte (`calc/adj_run1.txt` = `adj_run2.txt`, md5 `0c30b312…`). Mù giá. Tâm gốc 15.911 (rev3 đề xuất; tâm không đổi so rev2 sổ). `skeptic_final` = REFUTED_OPEN (skeptic r1 INCONCLUSIVE) — trạng thái phản biện, không phải quan điểm đầu tư.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 15.050 đ/cp (Σ p×m = −5,41%). Dải theo cực trị (p, m): 14.401–16.264.**
Không có cổ tức đã công bố chưa trả (mã 313 trống, BCTC Q3) ⇒ một dòng.
|Σ| > 5% ⇒ tính bằng tổ hợp trong mô hình (trộn 8 nhánh bật/tắt theo p, cùng lưới 405 kết cục + CK 1,47%); mô hình tuyến tính theo 3 hạng mục nên tổ hợp = tuyến tính (−5,409%).

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | **Trích quỹ KTPL hằng năm từ LNST**: phân phối LN 2025 trong 9T26 — LN chưa PP 644,31 → 16,25 tỷ: ĐTPT +315,42; cổ tức 1.700 đ ⇒ 248,39; còn 64,25 (KTPL + khác); quỹ KTPL 23,83 → 80,22 (+56,39 tối thiểu). Tỷ lệ 10,19% [8,94%] LNST 2025 630,83 (en_p1.txt:180,207–213) — áp vào LN giữa chu kỳ + LN 2027 dương | ↓ | −6,74 [−6,74; −5,92] | A | 0,90 [0,75; 1] | −6,07 |
| 2 | **Tồn quỹ KTPL 80,22 tỷ** (nợ phải trả, en_p1.txt:180) chưa trừ khỏi tiền ròng 1.108 | ↓ | −3,40 | A | 0,90 [0,75; 1] | −3,06 |
| 3 | **Khoản trừ lãi gửi** 35,4 → 8,5 (trung điểm proxy lịch sử TB 2015–25 −9…+26 tỷ/năm; S symmetry; r3 §1 bước 8) | ↑ | +7,44 [+2,61; +12,28] | B | 0,50 [0,25; 0,75] | +3,72 |
| | **Σ** | | | | | **−5,41** |

Cơ sở chọn p: #1/#2 số trực tiếp BCTC (1 kỳ phân phối; tỷ lệ tương lai = giả định lặp lại, cùng thang A mặc định); #3 một chuỗi proxy (NP/0,8 − EBIT, BQ) = 1 quan sát; 2023/24 +43/+50 tỷ nằm trong chính chuỗi đó, không phải quan sát ngược độc lập.

## 2. Chỉ độ nhạy (C / luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy | Vì sao không vào tâm |
|---|---|---|---|
| Capex tuân thủ bãi thạch cao Đình Vũ (killer của skeptic) | ↓ | −674 đ/cp (−4,2%) mỗi 100 tỷ NPV âm | C: dấu chắc nhưng không có cận — BCTC Q3 chỉ cho biết dây chuyền thu hồi P2O5 trong thạch cao nằm trong XDCB (đã chi, en_p1.txt:856); bãi do CTCP Thạch cao Đình Vũ (DDV góp 3,86%, en_p1.txt:479) vận hành; chưa có số cam kết |
| Mức LN giữa chu kỳ (DT FY2025 đỉnh) | ↕ | TB DT 2021–25 ⇒ 12.452 (−21,7%); LTM ⇒ 17.254 (+8,4%); NP TB 2021–25 284 > 229 mô hình (chiều lên) | C hai chiều: số ngược nhau, không xác định dấu |
| Tiền ròng bị giữ lại (Vinachem 64%) | ↓ | vốn hoá lãi gửi ⇒ 11.555 (−27,4%) | C: 2025 giữ 50% LN vào ĐTPT nhưng vẫn trả 39%; không có cận thời hạn |
| Liven 217 tỷ mất (p 0,10 [UL]) | ↓ | −146 | C |
| KTPL trên phần lãi gửi vượt mức nhúng trong biên | ↓ | chưa đo | C |
| [LUẬT] r 13,5% vs Ke 12,3% (E15) | ↑ | 16.854 (+5,93%) | tham số luật V1 |
| [LUẬT] trọng số đường 2027 đối xứng 1/3 | ↑ | 16.336 (+2,7%) | tham số house (PREREG §4) |

Không đếm hai lần: #1 flow ≠ #2 stock; #3 chỉ chỉnh khoản trừ, không đụng trục LN giữa chu kỳ (C hai chiều riêng); BCTC riêng = bộ duy nhất (DDV không có công ty con, en_p1.txt:151) — đóng mục phụ của skeptic.

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ (Δ trên tâm 15.911; xấp xỉ cộng)
| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| NQ ĐHĐCĐ 2027 phân phối LN 2026: tỷ lệ KTPL thật | 03–04/2027 | #1 p→1, m theo tỷ lệ; mỗi 1pp LNST ⇒ ∓0,66% tâm | tỷ lệ 5% ⇒ +439 so với tâm adj; 10,19% ⇒ −107 | +2,76 / −0,67 |
| BCTC Q4/2026 số dư quỹ KTPL | ~20/01/2027 | tính lại #2 (mỗi 10 tỷ ⇒ −67 đ) | theo số | — |
| Thu nhập TC kiểm toán 2015–22 (BCTC năm cũ trên website) | khi đọc | #3 B→A; khoản trừ 26 ⇒ +2,6%, −9 ⇒ +12,3% | +415 … +1.953 | — |
| Giấy phép môi trường / NQ HĐQT / thuyết minh cam kết vốn bãi thạch cao | BCTC Q4/2026, ĐHĐCĐ 2027 | C→A; mỗi 100 tỷ cam kết không tạo DT | −674 / 100 tỷ | −4,2 |
| BCTC Q4/2026 + 2027: DT ≥ 5.652 bền (2 năm liền) | 01/2027–01/2028 | C mức LN giữa chu kỳ: có chiều lên | 0 … +1.343 | 0 … +8,4 |
| DT 2027 về ≤ 3.700 (giá DAP/S về TB) | 2027 | C mức LN: chiều xuống | đến −3.459 | −21,7 |
| Công bố cổ tức tiền lớn / kế hoạch dùng tiền | ĐHĐCĐ 2027 | C tiền bị giữ: đóng chiều xuống | 0 | 0 |
| Liven: thu đủ / trích lập | BCTC Q4/2026 | C | 0 / −1.475 nếu mất 100% | — |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −344 / +371 | −2,2 / +2,3 |

**Điều kiện đổi số quan trọng nhất:** cam kết vốn bãi thạch cao (C, mỗi 100 tỷ −4,2%) và tỷ lệ KTPL thật năm 2026 (#1).
