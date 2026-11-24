# PVP — Tâm kỳ vọng điều chỉnh (E17, 24/11/2026, job Taylor_20261124_131351)

- **Phương pháp:** `dd_adjcenter_20261124/PREREG_adj.md` (md5 `ef5157cb…`) + `PREREG_adj_v2.md` (md5 `835dfc1e…`).
- **Kiểm kê khoá trước khi tính:** `INVENTORY_adj_PVP.md` (md5 `c0d80348…`). `calc_adj.py` assert cả 3 md5.
- **Tái lập:** chạy 2 lần, `adj_run1.txt` = `adj_run2.txt` (md5 `7adaad03…`). Output: `adj.json`.
- **Mù giá.** Tâm gốc = 23.099 đ/cp (LEDGER_PROPOSAL rev3 = sổ rev2; recheck không đổi tâm). `skeptic_final` = REFUTED_OPEN (r1 INCONCLUSIVE), giữ nguyên nghĩa là trạng thái phản biện.

## Kết luận
**Tâm kỳ vọng điều chỉnh: 22.988 đ/cp (Σ p×m = −0,48%; −0,48% so với tâm base). Dải theo cực trị (p, m): 22.766–23.044.** Căn cứ: 1 hạng mục bậc C+, 0 bậc A/B.
- Cổ tức: không có quyền tiền chưa chốt đã biết. Cổ tức 2025 1.000 đ đã trả 20/10/2026 và đã trừ trong tiền ròng ⇒ một dòng kết luận.
- Tâm dịch nhỏ vì phần lớn hạng mục skeptic mở là bậc C (không có dữ liệu cận trong tay) và hai chiều gần cân nhau:
  - Chiều xuống: lên đà, KTPL.
  - Chiều lên: phế liệu, chi phí công ty, NPV tàu.
- **Rủi ro lớn nhất KHÔNG nằm trong tâm:** ĐHĐCĐ bất thường mua tàu Aframax "số 3" (bảng §3, dòng 1).

## 1. Hạng mục vào tâm
| # | Hạng mục | Hướng | m (% tâm) [khoảng] | Bậc | p [thấp; cao] | p×m |
|---|---|---|---|---|---|---|
| 1 | Lên đà định kỳ sau TT99, chỉ nhánh "tốt" | ↓ | −0,96 [−1,92; −0,96] | C+ | 0,50 [0,25; 0,75] | −0,48 |
| | **Σ** | | | | | **−0,48** |

Cơ sở #1:
- **Áp đính chính skeptic r1 finding 1.** Lên đà theo đăng kiểm là chi bắt buộc, nên dấu chắc chắn. Nhánh xấu/cơ sở (EBITDA 300/400) neo mức 2025, lúc đó công ty còn trích sửa chữa vào giá vốn, nên đã gồm chi phí này. Chỉ nhánh tốt (550 ≈ run-rate 9T/26, sau TT99 ngừng trích) là thiếu.
- **Độ lớn:** đo bằng mô hình r3 (`calc/calc_d3_tot.py`). Cận bảo thủ = ½ mức trích cũ (k 0,5): −221 đ (−0,96%). Cận cao (k 1,0): −443 đ (−1,92%).
- **Cơ sở mức trích:** LCTT mã 03 9T/25 = 53,1 tỷ. Gán dòng này cho trích sửa chữa là suy luận ⇒ không lên bậc A. Chỉ có 1 quan sát ⇒ p theo B1.
- Bản đầu của recheck (−3,48%/−6,97%, áp mọi nhánh) đã bị skeptic bác vì đếm hai lần. Bản đó không dùng.

## 2. Chỉ độ nhạy (C / tham số luật) — KHÔNG vào tâm
| Hạng mục | Hướng | Độ nhạy (đo bằng mô hình trừ khi ghi "ước lượng") | Vì sao không vào tâm |
|---|---|---|---|
| Phế liệu đội tàu hiện hữu (base = 0) | ↑ | +1 tr USD ⇒ 23.216 (+0,51%); +5 tr USD ⇒ 23.684 (+2,53%) | Dấu chắc chắn nhưng không có LDT/giá phế liệu trong tay ⇒ không có cận |
| ĐHĐCĐ bất thường 23/10/2026 — tàu Aframax "số 3" (nguồn vốn, phát hành) | ↕ | Không định lượng được. Nếu không mua: NPV0 ⇒ 24.678 (+6,8%). Nếu phát hành dưới giá trị nội tại: pha loãng | Không có văn kiện trong tay |
| Trích quỹ KTPL hằng năm (ví dụ 5% LN sau thuế) | ↓ | −866 đ (−3,75%), **ước lượng**: 5% × PV(đội tàu + FSO − chi phí công ty) | Không có số dư/tốc độ chi quỹ trong tay |
| Chi phí công ty 10 năm [UL] | ↑ | 8 năm ⇒ 23.335 (+1,02%); 6 năm ⇒ 23.639 (+2,34%) | Tham số tự đặt; FSO hợp đồng tới 2036 |
| NPV tàu mới −30% nhánh xấu [UL] | ↑ | NPV0 ⇒ 24.678 (+6,8%); −30% vô điều kiện ⇒ 18.935 (−18,0%) | Độ lớn [UL] |
| [LUẬT] r 13,5% vs dải Ke (E15) | ↑ | Ke 12,3% ⇒ 23.593 (+2,14%) | Tham số luật V1, không vào Σ |
| [LUẬT] CK 5 tỷ 1,98% vs sleeve 0,18% | ↑ | — | Luật V3 |

Không đếm hai lần:
- D3 chỉ áp ở nhánh tốt; nhánh 300/400 đã gồm trích cũ.
- Biến thể NPV0 và biến thể "không mua" là cùng một trục. Ghi một lần ở dòng ĐHĐCĐ, dòng NPV −30% chỉ tham chiếu.

## 3. BẢNG ĐIỀU KIỆN ĐỔI SỐ
Δ tính trên tâm 23.099.

| Sự kiện / dữ kiện | Khi nào (ước lượng lịch) | Đổi gì | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|
| **Văn kiện/NQ ĐHĐCĐ bất thường (tàu Aframax "số 3"): giá, tuổi, nguồn vốn, có phát hành không** | đã họp/hoãn, hạn ≤30/11/2026 | Huỷ/hoãn mua ⇒ nhánh "không" (NPV0) | +1.579 | +6,8 |
| | | Phát hành cổ phiếu dưới giá trị nội tại ⇒ pha loãng SH; HARD ABANDON nếu dưới book | theo tỷ lệ phát hành | — |
| | | Tàu #3 nằm NGOÀI 116 tr USD ⇒ thêm trục mua tàu | theo giá tàu × NPV | — |
| Thuyết minh BCTC năm 2026: lịch lên đà từng tàu + chi phí lần gần nhất | 01–03/2027 | #1 C+→A; áp đúng nhánh | −221 … −443 (k 0,5–1,0) | −0,96 … −1,92 |
| LDT từng tàu (đăng kiểm/web công ty) + giá phế liệu | khi tra | Phế liệu C→A/B | +117 mỗi 1 tr USD | +0,51 mỗi 1 tr USD |
| NQ ĐHĐCĐ 2027: tỷ lệ trích KTPL | 03–04/2027 | KTPL C→A | ≈ −173 mỗi 1% LN (ước lượng) | ≈ −0,75 mỗi 1% |
| Ký phụ lục FSO 2036 đúng điều khoản BB 03/06/2025 | khi có | WARNING đóng; giữ base | 0 | 0 |
| Phụ lục FSO giá thấp hơn / hạn ngắn hơn | khi có | Biến thể bỏ dòng >5 năm | −610 | −2,6 |
| DT vận tải Q4/2026 < Q3 | ~20/01/2027 | Cước chu kỳ xuống: trọng số xấu ↑ (rev mới) | theo mô hình | — |
| 177 tỷ FSO năm 1 hoà giải được | BCTC năm 2026 | Trục 0,5/0,5 → 1/0 hoặc 0/1 | +639 / −639 | +2,8 / −2,8 |
| Lãi huy động 12T ±50bp (luật V1) | liên tục | r | −198 / +202 | −0,86 / +0,87 |
| Pháp lý | khi có | Chỉ WARNING | 0 | 0 |

**Điều kiện đổi số quan trọng nhất:** văn kiện ĐHĐCĐ bất thường về tàu Aframax "số 3". Đây là trục đã quyết nhãn ở r3 (NPV0 ⇒ DƯỚI vùng; −30% vô điều kiện ⇒ ≈ giá) và còn có thể đổi số cổ phiếu.
