# FPT — Rà lại DD theo luật B5 + E15/E16 (24/11/2026, job Taylor_20261124_095517)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/FPT/REPORT_r3.md`) theo HANDOFF `dd_recheck_20261124`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/model_r3.py` + `assumptions_r3.json` (khoá md5 `a873ef0eb43c9d1354f2b376e916064f`, không sửa). Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` đã bị TRIM khỏi git ngày 19/11 (commit `14ad1c925`, weekly-orphan-review). Khôi phục bằng `git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105` ra `/tmp/ddrestore_B/` (đọc được tại đó). md5 của 9 file đầu vào khớp `LOCK_r3_prerun.txt` (assert trong code).
- **Calc:** `calc/calc_recheck.py` (md5 `166a2624…`). **Chân CONTROL:** chạy lại `model_r3.py` cho stdout md5 `51b85a47…` = `run1.txt` của r3, và `model_r3_out.json` md5 `17ddd898…` = LOCK_r3_post (assert). Tâm 57.312 / P10 45.270 / P90 68.466 cũng được assert.
- Chạy 2 lần: `run1.txt` = `run2.txt` = md5 `7a1b68e4…`. Output `calc/calc_recheck_out.json`.
- Mù giá: calc không đọc giá mới. Giá 50.800 (BQ 06/11/2026) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ): 57.312 đ/cp — vùng 45.270–68.466. KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 61.176 đ/cp (+6,74% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): **KHÔNG CHẮC (N hiệu dụng thấp, 2.46)** — phân vị [fade 3, hold 2], 120 tháng, N hiệu dụng ≈ 2.5

- **Nhãn** (giá 50.800, BQ 06/11/2026, kế thừa r3): **TRONG vùng**. Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 57.312 = 48.715). Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới chỉ cần soát cơ học (MECH).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding: FPT không có tầng holding kiểu HHS; FTEL (FOX) và FRT tính theo thị giá × tỷ lệ sở hữu, CK FTEL base 0% từ r3 — cùng hướng với đề xuất base 0% của `ck-hhs-reference-range-20261124`. (ii) r: neo 03/11 7,40%, đọc lại 24/11 vẫn 7,40% (`cctg_12m(2026-11-02)`, last_update 16/11) ⇒ Δ = 0, r = 13,5%. (iii) RONIC terminal = Ke đã áp ở r3 (D2). (iv) Độ nhạy r ở r3 đã tính từ mô hình, khớp lại từng đồng (§2).
- Sizing: giữ ngoại lệ **5% NAV** đã duyệt riêng (05/11); không đề xuất đổi.

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn `dd_history_label.py` (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ có ±50/±100bp | Bổ sung: 61.176 / 57.606 | 0 |
| 4 | V6 hai nền | Chưa có | Bổ sung bảng §3 (chỉ hiển thị) | 0 |
| 5 | D3 capex tuân thủ | Chưa soát | Soát: không nhận diện hạng mục (§3) | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r

r tại neo 03/11/2026 = 13,5% (lãi huy động 12T hiệu dụng 7,40%). β = 1 (giả định). Δ đến 24/11 = 0.

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 50.800 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 61.176 | 48.000 | 73.431 | +3.864 | +6,74% | 21,0% |
| 12,5% (−100bp) | 60.478 | 47.505 | 72.537 | +3.166 | +5,52% | 23,2% |
| 13,0% (−50bp) | 58.831 | 46.342 | 70.421 | +1.519 | +2,65% | 26,0% |
| 13,4% (đầu trên dải Ke) | 57.606 | 45.477 | 68.845 | +294 | +0,51% | 26,5% |
| **13,5% BASE** | **57.312** | **45.270** | **68.466** | 0 | 0 | 27,0% |
| 14,0% (+50bp) | 55.906 | 44.273 | 66.668 | −1.406 | −2,45% | 27,8% |
| 14,5% (+100bp) | 54.602 | 43.339 | 65.012 | −2.710 | −4,73% | 29,8% |

- Bốn mốc ±50/±100bp khớp đúng số r3 §4 (60.478 / 58.831 / 55.906 / 54.602).
- Nhãn TRONG ở mọi mức r trong bảng (P10 ≤ 48.000 < 50.800 < P90). Luật 4 ở r 12,3% (chỉ báo kèm, E15 không dùng cho luật 4): ngưỡng 52.000 > giá.
- Bản G (RONIC 5 năm chặn ở Ke) tại r 12,3%: tâm 53.826 (P10 48.000, P90 58.719) — bản mong manh nhất của r3 (50.652 ở 13,5%) vẫn > giá khi r ở đầu dưới dải.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal RONIC:** đã đúng — r3 D2 đặt RONIC terminal = Ke ở cả 3 kịch bản (conv_T = 1 − gT/Ke). Pha 5 năm giữ RONIC theo kịch bản (moat NARROW ⇒ không thưởng, không trừ ở pha dự báo, V5 + user 08/11). Độ nhạy chặn pha 5 năm: E/F/G = 54.472 / 52.311 / 50.652 (r3 §4). Không lệch.
- **D3 capex tuân thủ:** không nhận diện hạng mục chi bắt buộc-không-tạo-doanh-thu trong `assumptions_r3.json`/REPORT_r3. Hạng mục đầu tư duy nhất ở base là XDCB khuôn viên giáo dục 760 tỷ = giá sổ (NPV 0, growth). Viễn thông (FTEL) đi vào giá trị qua thị giá FOX (đã phản ánh capex của FTEL). **Cần kiểm chứng:** chưa đọc thuyết minh cam kết vốn/nghĩa vụ môi trường-PCCC của khối giáo dục/data center; không có số ⇒ không vào base, không ước.
- **V1/D4 r:** r 13,5% đúng neo + β×Δ (Δ = 0); dải Ke 12,3–13,4% nay đã báo (§2); ±50/±100bp tính từ mô hình.
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ (r3 §6): trước CK 57.420, sau CK 5 tỷ (0,188%) 57.312; nhãn theo sau CK.
- **V5 moat:** đã đủ — 5F 07–09/11/2026 (`ADDENDUM_5F.md`) < 12 tháng: NARROW, SWITCHING/COST/SCALE, rủi ro số 1 = đồng hồ GenAI cắt hào (Nhật Q3 giảm tốc). Kiểm nhanh 24/11: không có BCTC/CBTT mới được đọc trong recheck này.
- **V6 (bổ sung, chỉ hiển thị):** lấy nguyên từ `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11/2026, fin_time 29/10; file bị TRIM 19/11, khôi phục từ `3750ca176^`). V_ngắn **73.501** (LNST chuẩn hoá 8.961 tỷ, ROE 28,4%, g 12,3%, g/ROE 0,43 < 0,8) / V_dài **69.472** / D = **0,056** < ln2 ⇒ không cờ. Caveat: r của engine dd_blend (ERP-based), không phải 13,5% của DD; chưa chạy lại ở 13,5%. Hai nền máy cao hơn tâm DD ~21–28% do DD có lớp kịch bản (XẤU 0,275) + CK; không trộn vào tâm.
- **V7:** không dùng snapshot vĩ mô.
- **V8:** ngoại lệ 5% NAV đã duyệt riêng (FPT/NNC 05/11) — giữ, không đổi; > chuẩn 2–4% đã được user duyệt từng mã.

### Việc còn mở kế thừa (không chặn nhãn)
1. Lãi liên kết Q4/25 600 tỷ chưa kiểm (GAPS G10; độ nhạy 740 tỷ → 56.616).
2. Chưa quét pháp lý sau 01/11/2026 (WARNING r3 §10).
3. Errata 09/11 (SUMMARY.json key cũ) vẫn đúng; không ảnh hưởng số.

## 4. WARNING (giữ r3 §10)
FTEL / Bộ Công an / FOX free float; khoản 618,77 tỷ; vay ngoại tệ 30/09 trùng 30/06 [G15]; giao dịch bên liên quan; ETR 11,1→15,2% [G11]. Pháp lý chỉ WARNING.

## 5. Phạm vi đề nghị cho phản biện (§E4)
Moat (NARROW có đủ bằng chứng không; RONIC pha 5 năm TỐT ~93% với moat không bền), cân bằng hai chiều (lên: Ke đầu dưới +6,7%, hai nền máy cao hơn; xuống: chặn RONIC 5 năm → 50.652), thiếu hạng mục (D3 — có nghĩa vụ capex bắt buộc nào chưa vào base?), và kiểm bảng độ nhạy r §2.
