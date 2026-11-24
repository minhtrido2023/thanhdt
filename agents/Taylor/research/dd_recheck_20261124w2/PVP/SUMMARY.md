# PVP — rà lại DD đợt 2 (24/11/2026, job Taylor_20261124_131351)

**Tệp:**
- Báo cáo: `REPORT_recheck_PVP.md` (md5 `d34aa5f3…`).
- Calc: `calc/calc_recheck.py` — run1 = run2 md5 `91f4475b…`. CONTROL: lưới 270 ô trùng từng ô `pvp_r3_out.json` (LOCK).
- Đính chính D3: `calc/calc_d3_tot.py`.
- Skeptic: `skeptic/r1.json`.
- E17: `ADJ_CENTER.md` + `adj.json`.
- Đề xuất sổ: `LEDGER_PROPOSAL_PVP.json` (rev3).

⚠ `calc_r3/` gốc bị TRIM (`14ad1c925`). Khôi phục bằng `git archive 14ad1c925^ …dd_redo_20261105/{PVP,_common_014127,_shared} …dd_PVP_20261029` vào `/tmp/ddrestore_PVP`. 18/21 md5 LOCK khớp; 3 PDF nguồn không có trong git.

**Bước 0:** KHÔNG có tham số nền bị phủ. Không có tầng holding; r Δ = 0 (7,40%); RONIC không áp (SOTP chạy cạn); độ nhạy r đã tính từ mô hình ⇒ đã chạy skeptic.

## (a) Lệch theo luật mới
- **E15:** 23.593 (+2,14%).
- **E16:** **TRUNG TÍNH** (fade 66 / hold 56; N hiệu dụng 3.0; asof 20/11).
- **D4:** dải Ke 23.593 / 23.139; ±100bp: −1,70…+1,77%. Độ nhạy r thấp vì dòng tiền ngắn.
- **D3 — LỆCH:** lên đà định kỳ sau TT99 chưa nằm trong base. Bản đầu −3,5/−7,0% bị skeptic bác (đếm hai lần). Đo lại chỉ nhánh tốt: **−0,96…−1,92%**.
- **V6:** D = 0,44, không cờ.
- **V3/V5:** đã đủ (moat NONE).
- **V8:** 2% NAV.

## (b) Tâm / vùng / nhãn
| | r3 (sổ rev2) | recheck (rev3) | Δ |
|---|---|---|---|
| Tâm | 23.099 | 23.099 | 0% |
| Vùng | 13.799–30.338 | 13.799–30.338 | 0 |
| Nhãn @ 18.000 (06/11) | TRONG, luật 4 ĐẠT | TRONG, luật 4 ĐẠT | không đổi |
| skeptic_final | CONFIRMED (backfill rule) | **REFUTED_OPEN** | hạ nhãn |

## (c) Phản biện
`skeptic/r1.json`: **INCONCLUSIVE (medium)**, 0,96 USD.
- Cơ học đúng: skeptic tái lập md5 và cộng tay SOTP được 25.573 = tham số trung tâm.
- Chưa qua:
  - ĐHĐCĐ bất thường 23/10/2026 mua tàu Aframax "số 3" (nguồn vốn/phát hành chưa rõ).
  - Phế liệu = 0 chưa định lượng (chiều lên).
  - HTM không đọc lại được PDF.
- Đính chính D3 đã áp bằng đo lại. Tâm dịch 0% và nhãn không đổi ⇒ xác nhận cơ học, không chạy B2.

## (d) Tâm kỳ vọng điều chỉnh (E17)
**22.988 đ/cp (−0,48%), dải 22.766–23.044.** Căn cứ: 1 hạng mục C+ (lên đà, nhánh tốt). Các hạng mục còn lại là bậc C, chỉ ghi độ nhạy:
- phế liệu: +0,51%/1 tr USD;
- KTPL: −3,75% ở 5% LN (ước lượng);
- chi phí công ty 6–8 năm: +1,0…+2,3%;
- ĐHĐCĐ: NPV0 +6,8% / pha loãng.

**Điều kiện đổi số quan trọng nhất:** văn kiện ĐHĐCĐ bất thường về tàu "số 3" (hạn ≤30/11/2026).

## (e) Rủi ro / việc mở
1. Tra văn kiện ĐHĐCĐ 23/10 (hoặc phiên hoãn ≤30/11): tàu nào, giá, có phát hành không.
2. Lịch và chi phí lên đà từng tàu; LDT tàu cho giá trị phế liệu.
3. Khôi phục PDF CĐKT Q3 để đọc lại HTM 1.015,87.
4. Pháp lý chưa quét sau 05/11.
5. Selfcheck sổ tạm cho LEDGER_PROPOSAL: 0 lỗi. Thử thêm center_adj trên sổ tạm (`dd_ledger_append_center_adj.py --ledger /tmp/...`): 0 lỗi.

## (f) Khuyến nghị lớp: **MECH + việc mở 1 (FULL nếu văn kiện ĐHĐCĐ đổi trục mua tàu/số cổ phiếu)**
Phần luật mới đổi tâm 0%; E17 chỉ −0,48%. Muốn đóng đòn 8 phải có văn kiện ĐHĐCĐ (dữ kiện mới ⇒ rev mới), không phải làm lại mô hình.
