# PAT — rà lại DD đợt 3 (25/11/2026, job Taylor_20261125_032448) — **DỪNG ở Bước 0**

Nguồn: `dd_PAT_rebuttal_20261117/C/r5/VALUATION_r5.md` (md5 `64aa2b2d…`, sổ rev3) · mô hình `C/r5/calc_r5/model_r5.py` (md5 `f6cd2e0e…`, không bị TRIM; CONTROL cây trộn 66.470,1 = r5) · skeptic `C/skeptic/r1.json` (DD_GENERAL, REFUTED medium, 24/11, report_md5 khớp) · probe `calc/step0_probe_pat.py` (2 lần chạy trùng md5 `2e2a3b46…`, `calc/run1.txt`).

## Bước 0 (tham số nền bị phủ?): **CÓ — RONIC terminal (D4, user 22/11 19:07)**
- r5 khoá 22/11 09:48Z (16:48 ICT), TRƯỚC luật D4. Terminal = `el×(1+g)×0,8×0,94/(r−g)` với g 2% và KHÔNG tái đầu tư ⇒ RONIC ngầm = ∞ > Ke. Moat PAT NARROW/NONE (dd_PAT_20261114: CAPTIVE_SUPPLY/PERMIT; bản objective: NONE) ⇒ không có lý do WIDE ⇒ D4 bắt buộc RONIC = Ke (TV = NOPAT_{T+1}/r).
- Các tham số nền khác: r 13,5% (`effective_deposit_rate('2026-11-25')` = 7,40%, Δ 0) — đạt; không holding; độ nhạy r tính từ mô hình (r5 §2) — đạt.
- Theo HANDOFF đợt 3 ⇒ **DỪNG mã này: không chạy skeptic, không dựng E17/adj.json, không viết LEDGER_PROPOSAL** (tâm base sẽ đổi). Số dưới đây là đo để Mike/user quyết rev6, KHÔNG phải tâm mới đã phản biện.

## Số đo (trước CK; sau CK 10% trong ngoặc) — mù giá
| Biến thể | Tâm | Δ |
|---|---|---|
| r5 (sổ rev3) | 66.470 (59.823) | — |
| **D4: terminal RONIC = Ke** | **65.510 (58.959)** | **−1,44%** (TV chỉ ≈10% giá trị — chuỗi tường minh tới 2045) |
| D4 — vùng sau CK | P10 33.457 · **P25 40.550** · P50 58.633 · **P75 73.753** · P90 86.116 | (r5: 41.000–74.900) |
| D4 + Ke 12,3% (E15) | 70.651 (63.586) | +7,85% so D4 |
| D4 + gỡ bước H1/26 "sạch" → ô D (killer skeptic r1) | 61.697 (55.527) | −5,82% so D4 |
| Hạn thuê đất KCN hết 2042 / 2034, không gia hạn, không TV | 57.539 / 45.479 | −12,2% / −30,6% so D4 |

**E16 (nguyên văn, asof 2026-11-20):** PAT: so với lịch sử 10 năm của chính mã — **KHÔNG CHẮC (proxy lệch DD, k=0.35–0.88)** — phân vị [fade 8, hold 9], 53 tháng, N hiệu dụng ≈ 9.3 (…) ⚠ LỢI NHUẬN SỤT? (ROE TTM/5Y=0.57); ROE5Y bị kẹp 45%.

## Vì sao không làm cơ học
Riêng D4 chỉ −1,44% (≤5%, có thể xác nhận cơ học), nhưng hạng mục skeptic r1 chưa đóng lớn hơn nhiều và đụng CÙNG tâm base: killer ô H1/26 −5,8% (có cơ sở bằng chứng A1:133,143 của fleet), hạn thuê đất (2034 trong `blind_val_20261114/assumptions_blind.md` vs ~2042) −12…−31%, capex môi trường KCN Tằng Loỏng (chưa có số), cầm cố ACB 130 tỷ (skeptic ước −7,8%). Áp D4 + killer đã là −7,2% > 5% ⇒ B2 phản biện đầy đủ. E17 dựng trên base sắp đổi là làm hai lần.

## Đề xuất cho Mike/user (chọn 1)
- **(a) rev6 đầy đủ (khuyến nghị):** áp D4 + ô D (hoặc hiệu chỉnh O2 chỉ trên Q2/26) + truy hợp đồng thuê đất KCN (hạn, gia hạn, hoàn nguyên) + cầm cố ACB/BIDV → khoá → skeptic DD_GENERAL → E17. Mục cần dữ kiện ngoài: hạn thuê đất (BCTC KT thuyết minh/HĐ thuê, CBTT) — lớn nhất.
- (b) rev6 cơ học chỉ D4 (58.959 sau CK, P25–P75 40.550–73.753), giữ REFUTED_OPEN + E17 trên base đó; chấp nhận killer/hạn thuê nằm trong E17/độ nhạy.

## Nhãn hiện tại
Giữ sổ rev3: REFUTED_OPEN, tâm 59.823 sau CK. Mọi biến thể trên đều < giá tham chiếu 70.200 (17/11, kế thừa) và luật 4 không đạt ⇒ kết luận "không có biên an toàn" của r5 KHÔNG đổi ở bất kỳ biến thể nào (đọc sau khoá).

## Khuyến nghị lớp: **FULL** (rev6 + skeptic), chờ Mike/user chọn (a)/(b).
