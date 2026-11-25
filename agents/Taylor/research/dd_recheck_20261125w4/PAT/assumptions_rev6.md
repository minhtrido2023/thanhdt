# PAT rev6 (sổ: dd_date 2026-11-17, rev 4) — KHOÁ GIẢ ĐỊNH trước khi chạy (25/11/2026, job Taylor_20261125_063651). MÙ GIÁ.

Nền: `dd_PAT_rebuttal_20261117/C/r5/calc_r5/model_r5.py` (md5 f6cd2e0ea89322b092b2e6a2bd4518b9; không sửa, chỉ bọc) + giả định khoá r5 (`assumptions_objective_r5.md` md5 872a9b82c9aaff679ea392beb4419123). Mọi giả định r5 GIỮ NGUYÊN trừ mục 1–2 dưới.

## Thay đổi base (đúng 2)
1. **D4 (luật, user 22/11 19:07):** terminal RONIC = Ke ⇒ TV = NOPAT_{2046}/r (thay `el×(1+g)×0,8×0,94/(r−g)` bằng cùng biểu thức × (r−g)/r). Lý do: moat NARROW/NONE (dd_PAT_20261114 REPORT 5F; bản objective NONE) ⇒ không có cơ chế WIDE.
2. **Ô (A tắt, B bật) → theo D (= r4, `cell='D'`)**, bỏ bước O2 "H1/26 sạch" (+4.800 ở r5). Lý do (skeptic r1 killer, bằng chứng fleet): `dd_PAT_rebuttal_20261117/A/A1_ore_mine_recovery.md:133,143` — KT25 còn khai thác tới khoảng đầu 2026–17/03, 2026 có ~2,5 tháng tự khai thác ⇒ H1/26 lẫn nguồn A; bằng chứng "không có kho quặng rẻ" dùng tồn kho PAT trong khi kho quặng ở DLC. Không hiệu chỉnh riêng Q2/26 ở base (1 quan sát, có thể lẫn kho quặng DLC) ⇒ chuyển thành hạng mục E17 chiều lên (bậc B, 1 quan sát: Q2/26 LNST% 21,2% — `dd_PAT_objective_20261114/factpack/F4_history_quarterly_bq.md:74`).

## Giữ nguyên (đã kiểm Bước 0)
- r = 13,5% (neo 03/11 lãi huy động 12T hiệu dụng 7,40%; đọc lại 25/11 Δ 0 — w3 SUMMARY). g = 2%. β=1.
- Không có tầng holding/CK holding. Chiết khấu thanh khoản V3 = 10% (giữ quy ước r5; ADV đo lại SAU khoá, chỉ để kiểm, không đổi tham số nếu không lệch bậc thanh khoản).
- Chuỗi tường minh tới 2045, hoạt động liên tục (gia hạn thuê đất KCN — giả định thông lệ, ước lượng). Tồn kho dư 44,44 tỷ KHÔNG giải phóng (r5). Cầm cố: base như r5 (70 tỷ BIDV bảo lãnh tiền điện = LOCKED70; các khoản khác là bảo đảm cho vay của chính PAT, không trừ). Capex = KH 45 tỷ/năm (r5).

## Hạng mục chỉ độ nhạy / E17 (khoá phân loại; độ lớn đo bằng mô hình sau khoá)
| # | Hạng mục | Hướng | Bậc | p (thang PREREG_adj) | Nguồn |
|---|---|---|---|---|---|
| 1 | Ô (A tắt,B bật) thật ra ở mức O2 (Q2/26 sau 17/03) | lên | B | 0,50 [0,25;0,75] (1 quan sát) | F4:74; A1:133,143 |
| 2 | Tồn kho dư 44,44 tỷ (30/09: 120,19 vs TB 3 mốc 75,75) được giải phóng | lên | B | 0,50 [0,25;0,75] (1 quan sát Q3; nền 31/12/25 bị UHY ngoại trừ — định tính, không tính ngược) | F2:79; model_r5 INV_EXCESS |
| 3 | Bảo đảm chéo Vietinbank 40 tỷ + 100.000 USD cho "công ty thành viên" bị thực hiện | xuống | C (độ lớn A 42,6 tỷ; xác suất không có dữ liệu) | — | F2:180-182 |
| 4 | Thuê đất KCN hết ~2034 (GPMB 13,158 tỷ còn lại, phân bổ ~1,63/năm ⇒ ~8,1 năm; cam kết thuê >5 năm 1,67 tỷ) KHÔNG gia hạn | xuống | C (ngày suy từ BCTC; xác suất không gia hạn không có dữ liệu) | — | F2:81; dd_PAT_20261114/assumptions_PAT.md:27 |
| 5 | Capex/chi phí tuân thủ môi trường xỉ P4 + khắc phục đổ thải KCN (D3) | xuống | C (không có số; lưu ý base đã đặt capex = KH 45 ≫ capex thực ~3/năm) | — | skeptic r1_raw:17 |
| 6 | ΔVLĐ phần ngoài tồn kho (phải thu…) | lên | C | — | skeptic r1_raw:23 |
| 7 | 70 tỷ BIDV hoàn theo mệnh giá (bảo lãnh chấm dứt) | lên | C | — | F2:177 |
| L1 | r 13,5% vs dải Ke 12,3–13,4% (E15) | lên | LUẬT | không vào Σ | V1/E15 |
| L2 | D4 RONIC terminal = Ke | xuống | LUẬT | không vào Σ | D4 |
Chống đếm hai lần: #2 chỉ là phần tồn kho; #6 là phần VLĐ còn lại. Nút T (giá chuyển giao DLC), A/B (quặng), TX (thuế XK) đã nằm trong cây — không thành hạng mục.
Tổ hợp E17 = chạy lại mô hình với #1 (cell O2) và #2 (inv) theo trọng số p (không cộng tuyến tính nếu |Σ|>5%; luôn chạy tổ hợp để đo).
