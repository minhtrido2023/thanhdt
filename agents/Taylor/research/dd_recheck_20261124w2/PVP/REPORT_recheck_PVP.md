# PVP — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, đợt 2, job Taylor_20261124_131351)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/PVP/REPORT_r3.md`, sổ rev2, dd_date 2026-10-29). **Không làm lại mô hình**: tái dùng nguyên `calc_r3/pvp_r3.py` + `assumptions_r3.json` (md5 `1d0b7c67…`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp) và thêm **độ nhạy D3** (lên đà định kỳ).

- **Nguồn calc:** `calc_r3/` gốc bị TRIM khỏi git ngày 19/11 (`14ad1c925`). Khôi phục: `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{PVP,_common_014127,_shared} agents/Taylor/research/dd_PVP_20261029 | tar -x -C /tmp/ddrestore_PVP`. 18/21 dòng LOCK khớp md5. Lệch: 3 PDF nguồn không có trong git (không đọc lại được) và `data/deposit_rate_vn_events.csv` (thêm dòng sau 06/11; lãi hiệu dụng đọc lại vẫn 7,40%).
- **Calc:** `calc/calc_recheck.py`. Script assert md5 7 file đầu vào. **Chân CONTROL:** lưới 270 ô tái lập trùng từng ô với `pvp_r3_out.json` (md5 `3e9fc88c…`, LOCK). Tâm 23.099, P10 13.799, P90 30.338 cũng được assert.
- Chạy 2 lần: `run1.txt` = `run2.txt` = md5 `91f4475b…`. Output: `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá. Giá 18.000 (06/11/2026) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 23.099 đ/cp — vùng 13.799–30.338 (P10–P90). KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 23.593 đ/cp (+2,14% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **TRUNG TÍNH** — phân vị [fade 66, hold 56], 105 tháng, N hiệu dụng ≈ 3.0

- **Nhãn** (giá 18.000, 06/11/2026, kế thừa r3): **TRONG vùng**. Luật 4 ĐẠT (ngưỡng 0,85 × 23.099 = 19.634). Nhãn mong manh: NPV tàu mới −30% vô điều kiện ⇒ tâm 18.935 ≈ giá (r3 §3).
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ cần soát cơ học (MECH). Lệch mới ở **D3** (§3): chi phí lên đà định kỳ bắt buộc sau lần kế tiếp CHƯA có trong base. Chỉ ghi độ nhạy (cơ sở = suy luận), không đổi tâm.
- **Bước 0 (tham số nền bị phủ?): KHÔNG.**
  - (i) CK holding: PVP không có tầng holding.
  - (ii) r: neo 03/11 7,40%; đọc lại 24/11 vẫn 7,40% (`cctg_12m(2026-11-02)`, last_update 16/11) ⇒ Δ = 0, r = 13,5%.
  - (iii) RONIC terminal: không áp dụng. Mô hình là SOTP dòng tiền chạy cạn (tuổi đời 4–8 năm, không terminal tăng trưởng).
  - (iv) Độ nhạy r tính từ mô hình (§2).
- Sizing (V8): đề xuất **2% NAV** (đầu dưới chuẩn 2–4%) vì moat NONE + nhãn mong manh vào giả định NPV tàu mới.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Lưới có trục ±50bp, chưa báo dải Ke | Bổ sung bảng §2 | 0 |
| 4 | D3 capex tuân thủ | Chỉ có dự phòng 232,9 tỷ (lần lên đà 12 tháng tới) + độ nhạy đơn vị phế liệu/lên đà | Thêm độ nhạy lên đà định kỳ năm 2..n (§3) | 0 (độ nhạy −3,5%/−7,0%) |
| 5 | V6 hai nền | Chưa có | Bổ sung §3 (chỉ hiển thị) | 0 |
| 6 | V8 sizing | "sleeve 40 tr" | 2% NAV | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

- r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%), β = 1 (giả định). Δ đến 24/11 = 0.
- Lưới r3 có trục lãi huy động −50/0/+50bp (0,25/0,5/0,25). Bảng dưới dịch r gốc và giữ trục.
- Bỏ trục (r cố định 13,5%) cho tâm 23.098. Chênh −1 đ ⇒ trục r không làm lệch tâm.

| r | Tâm | P10 | P50 | P90 | Δ tâm (đ/cp) | Δ % |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 23.593 | 14.217 | 24.465 | 31.109 | +494 | +2,14 |
| 12,5% (−100bp) | 23.508 | 14.136 | 24.383 | 30.977 | +409 | +1,77 |
| 13,0% (−50bp) | 23.301 | 14.006 | 24.181 | 30.653 | +202 | +0,87 |
| 13,4% (đầu trên dải Ke) | 23.139 | 13.840 | 24.022 | 30.400 | +40 | +0,17 |
| **13,5% BASE** | **23.099** | **13.799** | **23.982** | **30.338** | 0 | 0 |
| 14,0% (+50bp) | 22.901 | 13.595 | 23.801 | 30.032 | −198 | −0,86 |
| 14,5% (+100bp) | 22.706 | 13.395 | 23.626 | 29.732 | −393 | −1,70 |

Độ nhạy r thấp vì các dòng tiền đều ngắn hạn: tiền ròng 1.016 tỷ không chiết khấu; FSO hợp đồng ≤10 năm; niên kim đội tàu 4–8 năm. Nhãn TRONG ở mọi mức r trong bảng.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** không áp dụng (không có giá trị tăng trưởng/terminal). Tàu mới: base NPV 0 ở nhánh cơ sở/tốt; −30% chỉ ở nhánh xấu, dấu dựa trên dữ liệu IRR 7,67% < 11% [AGM p44]. Đây là luật V4(a) có cơ sở độc lập, giữ như r3.
- **D3 capex tuân thủ — LỆCH (độ nhạy, không vào base).**
  - Lên đà/kiểm định đăng kiểm định kỳ là chi bắt buộc và không tạo doanh thu.
  - Base r3 chỉ trừ dự phòng 232,9 tỷ (số dư chuyển hết sang ngắn hạn ⇒ lần lên đà trong 12 tháng tới).
  - Từ TT99 công ty ngừng trích trước [H1 p15]. Vì vậy chi phí các lần lên đà SAU lần đó không còn đi qua giá vốn, tức không nằm trong EBITDA 300/400/550 (TOP5C_CORRECTIONS_20261108.md:41 cũng nêu "chi phí lên đà sau TT99 chưa nằm trong EBITDA").
  - Cơ sở độ lớn duy nhất trong tay: dòng LCTT mã 03 "dự phòng" 9T/25 = 53,1 tỷ (gán cho trích sửa chữa là **suy luận**, `dd_PVP_20261029/REPORT.md:73`) ⇒ 70,8 tỷ/năm trước thuế.
  - Độ nhạy: chi từ năm 2 tới hết tuổi đời n, sau thuế 20%, chiết khấu ở r.
    - k = 0,5 × 70,8: tâm **22.294 (−805; −3,48%)**, P10 12.784, P90 29.416.
    - k = 1,0 × 70,8: tâm **21.490 (−1.609; −6,97%)**, P10 11.839, P90 28.494.
  - Nhãn TRONG ở cả hai mức (giá 18.000 > P10). Luật 4 ở k = 1,0: ngưỡng 18.267 > 18.000 ⇒ vẫn ĐẠT (sát).
  - **Cần kiểm chứng:** lịch lên đà từng tàu + chi phí lần gần nhất (thuyết minh BCTC năm 2026 / TM chi phí trả trước dài hạn).
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0); dải Ke 12,3–13,4% nay đã báo (§2).
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ (r3 §7): CK 1,98% @5 tỷ (ADV250 8,27 tỷ; ngoài vùng hiệu chỉnh); sleeve 40 tr 0,18%. Nhãn theo sau CK.
- **V5 moat:** đã đủ. 5F ngày 08/11/2026 (`ADDENDUM_5F.md`, <12 tháng): **NONE**; rủi ro số 1 = tái đầu tư ở đỉnh chu kỳ (mua tàu 116 tr USD ≈ 1,55× vốn hoá, IRR < hurdle), khách hàng chính là công ty mẹ định giá cước. Kiểm nhanh 24/11: không có BCTC/CBTT mới được đọc trong recheck này.
- **V6 (bổ sung, chỉ hiển thị):**
  - Lấy nguyên từ `dd_blend_20261111/out/apply_dd.csv` (khôi phục `3750ca176^`; fin_time 21/10).
  - Số: V_ngắn **15.585** (LNST chuẩn hoá 201,4 tỷ, ROE 11,0%, g 12,75%) / V_dài **10.021** / D = **0,442** < ln2 ⇒ không cờ.
  - Caveat: engine Gordon-ROE dùng r riêng của nó. Mô hình này không phù hợp với tài sản chạy cạn có 1.016 tỷ tiền ròng (Gordon không cộng tiền ròng tách riêng). Không trộn vào tâm.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** 2% NAV (§0). Ở cỡ sleeve thật, CK < 0,2%.

### Việc còn mở kế thừa (không chặn nhãn)
1. Văn kiện ĐHĐCĐ bất thường (hạn ≤30/11/2026: mua tàu, có phát hành cổ phiếu không) — chưa tra lại sau 05/11.
2. Phụ lục FSO 2036 chưa ký (biến thể bỏ dòng >5 năm: 22.489).
3. 177 tỷ FSO năm 1 chưa hoà giải (trục 0,5/0,5).
4. HTM 1.015,87 tỷ đọc từ ảnh CĐKT (PDF không còn trong git để đọc lại).
5. Chưa quét pháp lý sau 05/11.

## 4. WARNING (giữ r3 §5)
- Phụ lục gia hạn FSO 2036 chưa ký; đối tác là công ty mẹ PVTrans, từng điều chỉnh giá cước.
- Mua tàu 116 tr USD, IRR #2 7,67% < 11%.
- Bên liên quan 63,3% DT 6T, không trần.
- Đổi GĐ/PGĐ.
- Pháp lý chỉ WARNING.

## 5. Phạm vi đề nghị cho phản biện (§E4)
- **Thiếu hạng mục:** D3 lên đà định kỳ (độ nhạy §3 — nên vào base? mức nào?); lãi tiền gửi trên tiền ròng có đếm đôi với giá trị tiền ròng không (r3 §4 nói không).
- **Cân bằng hai chiều:**
  - Chiều lên: NPV tàu = 0 ⇒ DƯỚI vùng; phế liệu.
  - Chiều xuống: NPV −30% vô điều kiện; lên đà; FSO > 5 năm.
- **Moat NONE** có nhất quán với giá trị đội tàu không (niên kim EBITDA chạy cạn, không thưởng).
- Kiểm bảng độ nhạy r §2.
