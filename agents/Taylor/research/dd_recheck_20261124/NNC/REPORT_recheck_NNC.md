# NNC — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095517)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/NNC/REPORT_r3.md`, 08/11/2026) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên `calc/nnc_redo_r3.py` + `assumptions_r3.json` (khoá md5 `c36da69593e28d05ad92acca530a2cb4`, không sửa) cùng engine `dd_NNC_20261030` r3–r6 và `dd_MVC_20261103` r6. Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** các file output/assumptions đã bị TRIM khỏi git ngày 19/11. Khôi phục vào `/tmp/ddrestore_B/agents/Taylor/research/` bằng `git archive` từ `14ad1c925^` (dd_redo_20261105), `ef7472f56^` (dd_NNC_20261030), `bffae9c42^` (dd_MVC_20261103). md5 của 14 file đầu vào khớp `LOCK_r3_md5.txt` (assert trong code).
- **Calc:** `calc/calc_recheck.py` (md5 `1d4d670d…`). Cách đổi r: thay `common.r_of` ⇒ R của r3 = r mới, và r3 tự gán `N6.R_ANCHOR = R`; wrapper `N3.EV3` đọc giá trị này lúc gọi ⇒ mọi ô lưới dùng r mới. Mỗi r chạy một tiến trình con riêng. Hai kiểm tái lập r2 bên trong r3 chỉ đúng ở r 13,5%, nên được tắt khi r ≠ 13,5% (đã chạy đầy đủ ở CONTROL).
- **Chân CONTROL:** ở r 13,5%, stdout trùng byte `nnc_redo_r3_out.txt` (md5 `857c7adb…`) và `nnc_redo_r3_out.json` md5 `02a4e6ca…` (assert). Tâm 61.273 / P10 30.375 / P90 95.341 cũng được assert.
- Chạy 2 lần: `run1.txt` = `run2.txt` = md5 `a4c910d5…`. Output `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá mới. Giá 47.200 (BQ 06/11/2026) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 61.273 đ/cp — vùng 30.375–95.341. KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 63.725 đ/cp (+4,00% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (N hiệu dụng thấp, 1.81)** — phân vị [fade 85, hold 92], 120 tháng, N hiệu dụng ≈ 1.8 ⚠ ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.86)

- **Nhãn** (giá 47.200, BQ 06/11/2026, kế thừa r3): **TRONG vùng**. Luật 4 ĐẠT (giá ≤ 0,85 × 61.273 = 52.082) — chỉ là điều kiện được XÉT làm candidate, user duyệt từng lần. Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ cần soát cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: sở hữu chéo MVC↔NNC tính bằng giải hệ (NNC = N_ex + 0,103 × V_MVC; MVC = D_MVC + 0,4407 × V_NNC), holding 0% ở base, đã có độ nhạy 15%. Base 0% cùng hướng với đề xuất base 0% của `ck-hhs-reference-range-20261124` v5. (ii) r: neo 03/11 7,40%, đọc lại 24/11 vẫn 7,40% ⇒ Δ = 0. (iii) RONIC terminal: không áp — mỏ hữu hạn (GP Mũi Tàu tới 2043), DCF 2027–2043, không có giá trị cuối vô hạn; Gordon chỉ để đối chiếu. (iv) Độ nhạy r: r3 chưa có ±50/±100bp tính bằng đ/cp ⇒ nay đã tính từ mô hình (§2).
- Sizing: giữ ngoại lệ **5% NAV** đã duyệt riêng (05/11); không đề xuất đổi.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | V1 độ nhạy ±50/±100bp | Không có trong REPORT_r3 | **Bổ sung**, tính từ mô hình (§2): −1.847 … +2.024 đ/cp | 0 |
| 2 | D4 dải Ke 12,3–13,4% | Chưa có | Bổ sung: 63.725 / 61.467 | 0 |
| 3 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 4 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20), kèm cờ ĐỈNH LỢI NHUẬN? | 0 |
| 5 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị) | 0 |
| 6 | D3 capex tuân thủ | Chưa soát | Soát §3 | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%, cctg_12m 02/11). β = 1 (giả định). Δ đến 24/11 = 0.

| r | Tâm (sau CK) | Trước CK | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 47.200 |
|---|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 63.725 | 66.136 | 30.591 | 100.340 | +2.452 | +4,00% | 27,2% |
| 12,5% (−100bp) | 63.297 | 65.691 | 30.554 | 99.467 | +2.024 | +3,30% | 27,2% |
| 13,0% (−50bp) | 62.261 | 64.617 | 30.463 | 97.355 | +988 | +1,61% | 27,4% |
| 13,4% (đầu trên dải Ke) | 61.467 | 63.792 | 30.393 | 95.736 | +194 | +0,32% | 28,1% |
| **13,5% BASE** | **61.273** | **63.591** | **30.375** | **95.341** | 0 | 0 | 28,2% |
| 14,0% (+50bp) | 60.329 | 62.611 | 30.290 | 93.417 | −944 | −1,54% | 28,9% |
| 14,5% (+100bp) | 59.426 | 61.674 | 30.208 | 91.579 | −1.847 | −3,01% | 29,3% |

- Độ nhạy r vừa phải vì dòng tiền hữu hạn tới 2043 và một phần lớn giá trị nằm ở tiền ròng + cổ phần MVC theo mô hình. P10 gần như không đổi theo r (30,2–30,6k), vì nhánh đáy bị chi phối bởi kịch bản giá xấu, không phải bởi chiết khấu.
- Nhãn TRONG ở mọi mức r trong bảng. Luật 4 đạt ở mọi mức r trong bảng (ngưỡng thấp nhất 0,85 × 59.426 = 50.512 > 47.200) — chỉ báo kèm; E15 không dùng cho luật 4.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** không áp dụng — mô hình mỏ hữu hạn (DCF Mũi Tàu 2027–2043, kèm cho thuê), không có TV vô hạn. Gordon P/B chỉ là đối chiếu thô (r3 §6). Không lệch.
- **D3 capex tuân thủ:** base đã trừ **dự phòng phục hồi môi trường 4,50 tỷ** và dự phòng truy thu 22,37 tỷ ở bảng cân đối, đồng thời cộng ký quỹ PHMT 4,57 tỷ (đối xứng, `model_r3.py` dòng 10/47 của dd_NNC). **Cần kiểm chứng**, chưa có số: (i) chi PHMT/đóng cửa mỏ phát sinh thêm tới 2043, ngoài số dư dự phòng hiện tại; (ii) tiền cấp quyền khai thác/thuế tài nguyên định kỳ có nằm đủ trong chi phí K của mô hình không (truy thu đã chạm mỏ lõi — cờ E12). Không có nguồn ⇒ không vào base, không ước số.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0). Dải Ke và ±50/±100bp nay đã báo (§2).
- **E15/E16:** đã thêm (§0). Cờ E16 "ĐỈNH LỢI NHUẬN? (ROE TTM/5Y=1.86)" khớp nhận định r3: GPM TTM 53% là chu kỳ giá, không phải bằng chứng hào (ADDENDUM_5F). Chỉ hiển thị.
- **V3 thanh khoản:** đã đủ (r3 §5) — trước CK 63.591, sau CK 5 tỷ (3,65%, Q/ADV250 = 2,4x) 61.273; nhãn theo sau CK. Cỡ sleeve 10–40 tr: 0,16–0,33%.
- **V5 moat:** đã đủ — 5F 07–09/11/2026 (`ADDENDUM_5F.md`) < 12 tháng: **NARROW · LOCATION**, rủi ro số 1 = đồng hồ giấy phép/Nhà nước trên mỏ đơn lẻ Mũi Tàu (~94% DT, GP tới 2043). Errata 08/11: độ nhạy CHẶT-3C chưa chạy lại trên lưới r3 — vẫn mở (chỉ là độ nhạy, NARROW không trừ ở base).
- **V6 (bổ sung, chỉ hiển thị):** lấy nguyên từ `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 20/10; file bị TRIM 19/11, khôi phục từ `3750ca176^`). V_ngắn **68.074** (LNST chuẩn hoá 114,6 tỷ, ROE 19,0%, g 12,75%, g/ROE 0,67 < 0,8) / V_dài **68.527** / D = **0,007** < ln2 ⇒ không cờ. Caveat: r theo engine dd_blend, không phải 13,5%; LNST chuẩn hoá ở đỉnh chu kỳ (cờ E16) ⇒ hai nền máy có thể cao. Không trộn vào tâm.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** ngoại lệ 5% NAV đã duyệt riêng — giữ.

### Việc còn mở kế thừa (không chặn nhãn)
1. Chưa kiểm PDF: tiền gửi 322,44 / dự phòng 22,37 / quỹ KTPL 16,78 (errata r3).
2. Độ nhạy CHẶT-3C chưa chạy lại trên lưới r3.
3. Đính chính 4 (co giãn đối xứng) chưa tái lập được số của skeptic.
4. Bằng chứng hợp đồng thuê Núi Nhỏ (trục thuê).

## 4. WARNING (giữ r3 §7)
Sở hữu chéo MVC (44,07%) + uỷ quyền mua lên 51%, rủi ro buộc thoái theo D195; truy thu tài nguyên chạm Mũi Tàu; truy thu Núi Nhỏ ~42 tỷ; bên liên quan NHC (61% phải thu). Chưa tra lại tin pháp lý sau 05/11. Pháp lý chỉ WARNING.

## 5. Phạm vi đề nghị cho phản biện (§E4)
Moat (NARROW/LOCATION, đồng hồ GP 2043), cân bằng hai chiều (lên: Ke đầu dưới +4,0%, nhánh STRUCTURAL; xuống: cờ đỉnh lợi nhuận, truy thu, P10 30,4k), thiếu hạng mục (D3 — chi PHMT/đóng cửa mỏ, tiền cấp quyền), và kiểm bảng độ nhạy r §2.
