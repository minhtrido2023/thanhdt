# HPG — Tâm kỳ vọng điều chỉnh (E17/V9, 25/11/2026, job Taylor_20261125_032443)

Phương pháp: `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`) + kiểm kê khoá trước `PREREG_adj_HPG.md` (md5 `1544c227…`); `calc/calc_adj.py` assert cả ba + chân CONTROL hpg_r3 (stdout trừ dòng LOCK = r3) + tái lập 21.338 và bản J 20.673. Chạy 2 lần trùng byte (`calc/adj_run1.txt` = `adj_run2.txt`, md5 `2a0ed48d…`). Mù giá.
Vì sao có E17 dù skeptic r1 **CONFIRMED**: skeptic ghi `missing_items: fail (dưới ngưỡng trọng yếu)` — hạng mục thiếu chưa đóng (V9). Tâm base 21.338 GIỮ; E17 chỉ là dòng hiển thị + cổng Bậc 1 (chỉ siết).

## Kết luận
**Tâm kỳ vọng điều chỉnh: 20.203 đ/cp (Σ p×m = −5,32% tổ hợp; tuyến tính −5,44%). Dải theo cực trị (p, m): 19.823–20.956.**
Cổ tức 2026 15% chưa rõ hình thức (chưa công bố): nếu cổ phiếu ⇒ sau GDKHQ tâm/cp × 1/1,15 (cơ học, không đổi giá trị); nếu tiền ⇒ trừ đúng số đ/cp.

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | **Trích KTPL + thù lao HĐQT/BĐH từ LNST**: 9T26 −221,5 − 180,0 = 401,5 tỷ (notes_bs.md:94) / LNST mẹ 2025 15.453,2 (KT25, notes_bs.md:112) = 2,60% [riêng KTPL 1,43%] — đường LN × (1−k) | ↓ | −2,28 [−2,28; −1,26] | A | 0,90 [0,75; 1] | −2,05 |
| 2 | **Đếm trùng cam kết vốn**: 19.472 là số 30/06 (TM41), chi Q3 đã vào XDCB 30/09; chi Q3 ≈ capex 9T 14.607,2 − capex 6T thép 8.312,9 = 6.294 (ước lượng cận trên) | ↓ | −1,51 [−1,51; −0,75] | B | 0,50 [0,25; 0,75] | −0,76 |
| 3 | **ETR thép thực 6,55%** (6T26: 1.451,3/22.160,5, notes_bs.md:103) < ~12% ngầm trong TAXF 0,80/0,88 ⇒ bước nhảy thuế 20% lớn hơn | ↓ | −2,14 [−2,14; −1,10] | B | 0,50 [0,25; 0,75] | −1,07 |
| 4 | **Nhánh TỐT đếm trùng lợi ích capex** (bản J 20.673) | ↓ | −3,12 [−3,12; −1,56] | B | 0,50 [0,25; 0,75] | −1,56 |
| | **Σ (tuyến tính)** | | | | | **−5,44** |
Tổ hợp trong mô hình (16 nhánh bật/tắt theo p, lưới 135 kết cục, CK 0,15%): **−5,32%** (tương tác giữa #1/#3/#4 làm nhẹ đi 0,12pp).

Cơ sở p: #1 số trực tiếp BCTC (1 kỳ phân phối 9T26; skeptic đo kỳ 2025 2,1% cùng hướng); #2/#3/#4 một quan sát/ước lượng ⇒ B1.

## 2. Chỉ độ nhạy (C / luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Tâm khi áp | Vì sao không vào tâm |
|---|---|---|---|
| Capex tuân thủ môi trường (D3); cận trên = bản I (cam kết + XDCB lợi suất 0) | ↓ | 20.456 (−4,1%) | C: dấu chắc, không có cận bảo thủ khác 0; ký quỹ phục hồi MT chỉ 32,8 tỷ (notes_bs.md:96) |
| Mốc thuế 20%: 2030 / ETR hiện hành vĩnh viễn | ↕ | 20.648 / 22.119 | C hai chiều (mốc 2035 là ước lượng; GAPS:70 DQ1 lên 10% ~2032) |
| KTPL ở trần 5% (NQ ĐHĐCĐ 2026, theo skeptic) | ↓ | 20.400 (−4,4%) | trần, không phải tỷ lệ kỳ vọng; #1 đã lấy tỷ lệ thật |
| Trục TLSH r2 (mất giá trị lệch xuống) | ↓ | 21.144 (−0,9%) | C: không có dữ liệu suy giảm |
| Đường XẤU 16.000 tỷ vs run-rate lõi 9T26 ~25.600/năm (skeptic too_low) | ↑ | chưa đo | kịch bản xấu theo thiết kế; trọng số là tham số house |
| Vốn vượt cam kết trả nợ (chi phí vay 3,55–8,7%) thay vì gửi 5,92% | ↑ | chưa đo | gộp trong L2 dưới (cùng một trục lợi suất vốn giữ lại) |
| [LUẬT] r 13,5% vs Ke 12,3% (E15) | ↑ | 23.625 (+10,7%) | tham số luật V1 |
| [LUẬT] vốn vượt cam kết sinh lời = Ke (D4/V4 diễn giải; skeptic killer) | ↑ | 22.971 (+7,7%) | tham số luật (RONIC), PREREG v2 §4 |
| [LUẬT] g_RI kiểu r2 (thưởng moat) | ↑ | 22.530 (+5,6%) | moat NARROW ⇒ không thưởng (V5) |
Hai hạng mục chiều lên cuối bảng C được kiểm kê SAU khi khoá PREREG_adj_HPG (đọc lại symmetry của skeptic); xếp C/luật, không đổi Σ.

Không đếm hai lần: #2 (cam kết trùng XDCB) ≠ #4 (lợi ích capex trong đường LN nhánh TỐT) ≠ C1 (capex môi trường không tạo DT); #3 (mức ETR) ≠ C2 (mốc thời gian thuế).

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ (Δ trên tâm 21.338; xấp xỉ cộng)
| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm adj (đ/cp) | Δ % |
|---|---|---|---|---|
| NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL + thù lao từ LNST 2026 | 03–04/2027 | #1 p→1, k thật; mỗi 1pp LNST ⇒ ∓0,88% | k 5% ⇒ −500 | −2,3 |
| BCTC HN Q4/2026: TM cam kết vốn tại 31/12 + capex Q4 | ~30/01/2027 | #2 B→A (thay ước lượng bằng số cam kết mới) | 0 … −162 | 0 … −0,8 |
| BCTC soát xét/kiểm toán 2026: ETR phân khúc thép cả năm | 03/2027 | #3 thêm 1 quan sát; ETR ≥ 12% ⇒ #3 = 0 (+228); ≤ 7% ⇒ p 0,65 (−68) | +228 / −68 | +1,1 / −0,3 |
| BCTN 2026 / báo cáo PTBV: capex môi trường trong cam kết | 04/2027 | C1 → A theo số | đến −882 | đến −4,1 |
| Kết luận cơ quan thuế DQ2 là dự án mới (ưu đãi kéo dài) | khi có | C2 chiều lên (bản C) | đến +781 | +3,7 |
| DQ2 bị xếp "mở rộng" + quyết định truy thu | khi có | C2 chiều xuống + truy thu (chưa định lượng) | ≤ −690 | ≤ −3,2 |
| LNST lõi 2027 ≥ 28 nghìn tỷ (trên TRUNG LẬP) 2 quý | 2027 | #4 nhẹ đi (TỐT có cơ sở riêng) ⇒ p 0,35 | +166 | +0,8 |
| Công bố hình thức cổ tức 2026 15% | ĐHĐCĐ 2027 | cơ học số cp / trừ tiền | theo số | — |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −837 / +901 | −3,9 / +4,2 |

**Điều kiện đổi số quan trọng nhất:** capex môi trường trong cam kết vốn (C1, đến −4,1%) và tỷ lệ trích KTPL/thù lao 2026 (#1).
