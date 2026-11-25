# PVT — Rà lại DD theo luật B5 + E15/E16 (25/11/2026, job Taylor_20261125_032446, đợt 3 job B)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/PVT/REPORT_r3.md`, md5 `cb1534fc…`) theo `dd_recheck_20261125w3/HANDOFF.md`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/pvt_r3.py` + `assumptions_r3.json` (md5 `5f07cb59fc4cfb43b5ff875fba642803`, không sửa). Đổi DUY NHẤT một tham số theo luật mới: **terminal RONIC = Ke (D4, user 22/11/2026 19:07)** thay cho RONIC = ROE kịch bản; rồi chạy lại đổi r (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` bị TRIM khỏi git ngày 19/11 (commit `14ad1c925`). Khôi phục bằng `git archive 14ad1c925^ agents/Taylor/research/{dd_redo_20261105/PVT,dd_redo_20261105/_common_014127,dd_redo_20261105/_shared,dd_PVT_20261029,…}` ra `/tmp/ddrestore_PVT/agents/Taylor/research/`. md5 mọi dòng `LOCK` trong `calc_r3/LOCK_md5.txt` khớp (assert trong code), TRỪ `data/deposit_rate_vn_events.csv` — file append-only, đã thêm dòng sau 06/11 (09/11, 16/11); giá trị as-of 03/11 và 06/11 không đổi (control khớp byte chứng minh).
- **Calc:** `calc/calc_recheck.py`. **Chân CONTROL:** chạy lại `pvt_r3.py` ⇒ `pvt_r3_out.txt` md5 `23f5090f…` và `grid_pvt_r3.csv` md5 `58d04616…` = LOCK r3 (assert); tâm 18.841 / P10 13.903 / P90 24.207 (RONIC = ROE) assert; độ nhạy r cũ tái lập trùng r3 §3 (20.755 / 19.750 / 18.015 / 17.262).
- Chạy 2 lần: `calc/run1.txt` = `calc/run2.txt` md5 `e6639533…`. Output `calc/calc_recheck_out.json`.
- Mù giá: không đọc giá mới. Giá 20.550 (BQ 06/11/2026) kế thừa r3, chỉ cho nhãn và % dưới giá. CK 5 tỷ 0,6711% lấy nguyên `SUMMARY.json` r3.

## 0. Kết luận

**TÂM (base, r 13,5%, terminal RONIC = Ke, sau CK 0,67% @5 tỷ): 18.956 đ/cp — vùng 15.021–23.164 (P10–P90 lưới 90 kết cục). Đổi +0,61% so với r3 (18.841; 13.903–24.207) do áp D4.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 20.798 đ/cp (+9,72% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **RẺ** — phân vị [fade 16, hold 18], 120 tháng, N hiệu dụng ≈ 4.5

- **Nhãn** (giá 20.550, BQ 06/11/2026, kế thừa r3): **TRONG vùng** (+8,4% so tâm; 67,1% trọng số kết cục dưới giá). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 18.956 = 16.113). Nhãn không đổi so với r3.
- **Tâm đổi +0,61% (≤5%), lớp nhãn không đổi.** Vùng hẹp lại (P10 +1.118, P90 −1.043) vì RONIC = Ke triệt tiêu tác động của hệ số ROE lên phần tăng trưởng terminal.
- **Bước 0 (tham số nền bị phủ?): CÓ — một tham số: terminal RONIC.** r3 đặt RONIC = ROE kịch bản (0,8…1,2 × 0,9…1,1 × 13,15% ⇒ 9,5%–17,4%, cả trên lẫn dưới Ke) — bị D4 (22/11) phủ. Đây là thay thế CƠ HỌC bằng chính script có sẵn (r3 §3 ghi sẵn độ nhạy "RONIC = Ke ⇒ ~18.989", chưa chạy lại; chạy thật ra 18.956), không cần phán đoán mới ⇒ áp luôn trong recheck rồi mới chạy skeptic trên bản đã áp (không chạy skeptic trên tham số bị phủ). Các tham số nền khác: CK holding v5 — không có tầng holding (PVT Logistics/PVTrans con hợp nhất, NCI 19,6%); r: neo 03/11 7,40%, đọc lại 25/11 7,40% ⇒ Δ = 0, r = 13,5%; độ nhạy r ở r3 đã tính từ mô hình (khớp từng đồng).
- **Sizing (V8):** nếu có ý định mua (nhãn TRONG ⇒ không có tín hiệu), trần đề xuất **2% NAV** (đầu dưới dải chuẩn: moat NONE, LN ở đỉnh chu kỳ cước, ý kiến kiểm toán 2025 chưa kiểm). ADV 250 phiên 94,6 tỷ ⇒ CK ≤0,06% ở cỡ sleeve.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | **D4 terminal RONIC = Ke** | RONIC = ROE kịch bản | RONIC = Ke (= r của nút lưới): reinv_T = 1 − g/r | **+115 đ (+0,61%)**; P10 13.903 → 15.021; P90 24.207 → 23.164 |
| 2 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 3 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20; `calc/dd_history_label_PVT_2026-11-20.*`) | 0 |
| 4 | D4 dải Ke 12,3–13,4% | Chỉ ±50/±100bp | Bổ sung: 20.798 / 19.097 | 0 |
| 5 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị; FCFE ≤ 0 ⇒ chỉ V_ngắn) | 0 |
| 6 | D3 capex tuân thủ | Chưa soát | Soát §3: dry-dock/đăng kiểm bắt buộc + TT99 | 0 (độ nhạy) |
| 7 | V8 sizing | "sleeve 10–40 triệu" | Trần 2% NAV | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — mô hình r3 + D4, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%), β = 1 (giả định), Δ đến 25/11 = 0. Trục r của lưới (−50/0/+50bp) dịch theo r tâm; RONIC terminal = r của nút.

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 20.550 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 20.798 | 16.391 | 25.527 | +1.842 | +9,72% | 47,8% |
| 12,5% (−100bp) | 20.466 | 16.143 | 25.100 | +1.510 | +7,97% | 54,3% |
| 13,0% (−50bp) | 19.682 | 15.560 | 24.093 | +726 | +3,83% | 60,7% |
| 13,4% (đầu trên dải Ke) | 19.097 | 15.126 | 23.344 | +141 | +0,74% | 67,1% |
| **13,5% BASE** | **18.956** | **15.021** | **23.164** | 0 | 0 | 67,1% |
| 14,0% (+50bp) | 18.283 | 14.520 | 22.297 | −673 | −3,55% | 74,3% |
| 14,5% (+100bp) | 17.656 | 14.052 | 21.492 | −1.300 | −6,86% | 80,9% |

- Bản r3 (RONIC = ROE) ±100bp tái lập trùng r3 §3: 20.755 / 19.750 / 18.015 / 17.262 (chân control độ nhạy).
- Nhãn TRONG ở mọi mức r trong bảng. Ở r 12,3% tâm 20.798 > giá 20.550 (+1,2%) — chỉ báo kèm (E15 không dùng cho luật 4/nhãn).
- Độ nhạy r của PVT lớn (≈ ±7%/100bp) vì giá trị chủ yếu nằm ở terminal (g 3%).

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** ĐÃ SỬA (xem §1 #1). Pha dự báo (Q4/2026 + LN mẹ 2027) giữ nguyên tỷ lệ giữ lại theo ROE kịch bản (moat NONE ⇒ không thưởng, không trừ ở pha dự báo, V5 + user 08/11).
- **D3 capex tuân thủ:** vận tải biển có chi BẮT BUỘC không tạo doanh thu: dry-dock/đăng kiểm định kỳ (5 năm, trung gian 2,5 năm), lắp hệ thống xử lý nước dằn (BWM), tuân thủ EEXI/CII. Mô hình FCFE-ROE coi chúng nằm trong ROE lịch sử (trung vị `ROE_Trailing` 2015–25 đã gánh chi phí sửa chữa lớn trích trước). **Lệch có thể:** từ 01/01/2026 TT99/2025 + TT43/2026 ngừng trích trước sửa chữa lớn ⇒ LN 2026 (và base LN mẹ 2027 = Q3/2026 × 4 = 1.500) thiên lệch TĂNG; cận dưới quan sát được: hoàn nhập dự phòng phi tiền mặt 85,4 tỷ/9T (r3 §5). Độ nhạy cũ (skeptic 08/11, chưa chạy lại) ~73 tỷ/năm phần mẹ ⇒ ~−98 đ. Không có số chi dry-dock tiền mặt theo năm ⇒ KHÔNG vào base, chuyển độ nhạy/E17.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0); dải Ke 12,3–13,4% nay đã báo (§2); ±50/±100bp tính từ mô hình.
- **E15/E16:** đã thêm (§0). E16 "RẺ" in nguyên văn — thước cơ học RI-ROE5Y, N hiệu dụng ≈ 4.5, KHÔNG dùng làm cổng/nhãn.
- **V3 thanh khoản:** đã đủ (r3 §7): trước CK 19.084, sau CK 5 tỷ (0,67%) 18.956; sleeve 10–40 triệu CK 0,03–0,06%. Nhãn theo sau CK.
- **V5 moat:** đã đủ — 5F 07–08/11/2026 (`ADDENDUM_5F.md`, < 12 tháng): **NONE** (lợi thế captive PVN/quy mô không ra lợi nhuận > Ke), `moat_durable=false`; biên GPM 15% ở trung vị peer. Rủi ro số 1 = chu kỳ cước tàu dầu (LN 2026 ở đỉnh). D4 (RONIC = Ke) nay khớp kết luận NONE.
- **V6 (bổ sung, chỉ hiển thị):** `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 29/10; khôi phục từ `3750ca176^`): V_ngắn **22.045** (LNST chuẩn hoá 1.114 tỷ, ROE 14,1%, g 12,75%, g/ROE 0,90 ⇒ tái đầu tư bị chặn ở 80%) / **V_dài: không có — "normalized 3y FCFE ≤ 0 (capex > CFO, heavy reinvestment)"** ⇒ theo luật chỉ V_ngắn + giải thích: PVT đang trong pha mua tàu (ĐHĐCĐ 2026 duyệt capex 3.445 tỷ; 9T/26 nguyên giá tăng 979,6 tỷ) nên FCFE 3 năm âm; đây là "FCFE thấp vì đầu tư tăng trưởng (capex)", không phải cảnh báo đắt. Caveat: r engine dd_blend ≠ 13,5%; "chưa qua tiêu chí khoá trước, chỉ theo dõi".
- **V7:** không dùng snapshot vĩ mô.
- **V8:** trần 2% NAV (§0).

### Việc còn mở kế thừa (không chặn nhãn)
1. Ý kiến kiểm toán BCTC 2025 / soát xét H1/2026 — chưa kiểm (độ nhạy np27 1.250 ≈ −335 đ ở bản r3).
2. Định lượng TT99 (chi dry-dock tiền mặt so với hoàn nhập trích trước).
3. PVT có đăng ký mua quyền PDV (PVT Logistics chào bán ~56,9 tr cp) hay không.
4. Tỷ trọng TC/spot + đáo hạn hợp đồng thuê tàu; số/ngày NQ kế hoạch 5 năm.
5. Pháp lý: chưa quét lại sau 08/11/2026.

## 4. Giả định khoá
Như r3 §2 + `assumptions_r3.json` (md5 `5f07cb59…`), DUY NHẤT thay terminal RONIC = Ke theo luật D4 (không phải do giá). File khoá r3 `calc_r3/LOCK_md5.txt` md5 `d3661962465620cb74d508e14fee1e08` (= `assumptions_md5` sổ rev2); thay đổi D4 nằm trong `calc/calc_recheck.py` (hàm `value_ps(…, ronic_ke=True)`).
