# HPG — Rà lại DD theo luật B5 + E15/E16 (25/11/2026, job Taylor_20261125_032443)

Bản rà lại **REPORT_r3** (`agents/Taylor/research/dd_redo_20261105/HPG/REPORT_r3.md`, dd_date 2026-10-31 rev4 sổ) theo HANDOFF `dd_recheck_20261125w3`. **Không làm lại mô hình**: tái dùng nguyên `calc_r3/hpg_r3.py` (md5 `8fbf2450…`, bản khoá sau sửa văn bản 08/11) + đường LN v3 31/10. Chỉ chạy lại để đổi **r** (E15, dải Ke, ±50/±100bp).

- **Nguồn calc:** `calc_r3/` bị TRIM khỏi git 19/11 (commit `14ad1c925`). Khôi phục: `git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_w3a/mike`. md5 7 file đầu vào khớp `calc_r3/LOCK_md5.txt` (assert).
- **Calc:** `calc/calc_recheck.py`. **Chân CONTROL:** chạy lại `hpg_r3.py` → stdout trùng `hpg_r3_out.txt` r3 (md5 `72b26013…`, bản tham chiếu `calc/ref_hpg_r3_out.txt` lấy bằng `git show 14ad1c925^:…`) ở MỌI dòng trừ các dòng `LOCK …` (script tự in md5: đường dẫn tương đối đổi theo thư mục khôi phục; `data/deposit_rate_vn_events.csv` repo ngoài thêm dòng 09/11, 16/11; md5 hpg_r3.py trong out là bản trước sửa văn bản 08/11). `grid_hpg_r3.csv` trùng md5 LOCK `b1c8c9ee…`. Tâm 21.338 / P10 13.316 / P90 28.993 assert.
- Chạy 2 lần: `calc/run1.txt` = `calc/run2.txt` (md5 `dacbd3bc…`).
- Mù giá: calc không đọc giá mới. Giá 21.200 (BQ 06/11/2026) kế thừa r3, chỉ dùng cho nhãn.

## 0. Kết luận

**TÂM (base, r 13,5%, sau CK 5 tỷ 0,15%): 21.338 đ/cp — vùng 13.316–28.993 (P10–P90 lưới 135 kết cục). KHÔNG ĐỔI so với r3.**
Tâm @ Ke 12,3% (cùng mô hình, chỉ đổi r): 23.625 đ/cp (+10,72% so với tâm base)
So với lịch sử 10 năm của chính mã (thước cơ học RI-ROE5Y, KHÔNG dùng tâm DD; chỉ hiển thị, không phải tín hiệu): HPG: so với lịch sử 10 năm của chính mã — **KHÔNG CHẮC (rẻ…trung tính)** — phân vị [fade 21, hold 60], 120 tháng, N hiệu dụng ≈ 5.4 (thước cơ học RI-ROE5Y của chính mã, KHÔNG dùng tâm DD; chỉ hiển thị)

- **Nhãn** (giá 21.200, BQ 06/11/2026, kế thừa r3): **TRONG vùng**, giá ≈ tâm (−0,6%). Luật 4 KHÔNG ĐẠT (ngưỡng 0,85 × 21.338 = 18.137). Nhãn không đổi so với r3.
- **Tâm đổi 0%, lớp nhãn không đổi** ⇒ phần luật mới là MECH. Bản cũ CONFIRMED (r3 08/11) chưa từng qua DD_GENERAL ⇒ chạy phản biện DD_GENERAL (HANDOFF).
- **Bước 0 (tham số nền bị phủ?): KHÔNG.** (i) CK holding v5: không áp (HPG không có tầng holding kiểu HHS; TLSH là khoản đầu tư theo sổ). (ii) r: neo 03/11 7,40%, đọc lại 25/11 vẫn 7,40% ⇒ Δ = 0, r = 13,5%; lãi tiền gửi sau thuế của vốn giữ lại ngoài cam kết 5,92% cũng không đổi. (iii) Terminal: g_RI = 0 mọi nhánh (r3 #3) ⇒ vốn tăng thêm sinh lời = Ke (D4); spread ROE_T − r trên vốn hiện hữu giữ phẳng, không tăng. (iv) Độ nhạy r r3 §4 đã tính từ mô hình; khớp lại từng đồng (§2).
- **Sizing (V8):** 0% mua mới ở giá tham chiếu (≈ tâm). Nếu về dưới ngưỡng luật 4 ⇒ tối đa **3% NAV** (trong chuẩn 2–4%; thanh khoản sâu ADV 589 tỷ, moat NARROW, WARNING quản trị TLSH ⇒ không lên 4%).

## 1. Thay đổi so với r3

| # | Luật | r3 | Recheck | Ảnh hưởng tâm |
|---|---|---|---|---|
| 1 | E15 | Chưa có | Dòng E15 ở §0 | 0 |
| 2 | E16 | Chưa có | Dòng E16 ở §0, nguyên văn (asof 2026-11-20) | 0 |
| 3 | D4 dải Ke 12,3–13,4% | Chỉ ±50/±100bp + trục ±1pp | Bổ sung: 23.625 / 21.513 | 0 |
| 4 | V6 hai nền | Chưa có | §3 (FCFE ≤ 0 ⇒ chỉ V_ngắn) | 0 |
| 5 | D3 capex tuân thủ | Chưa soát | §3 | 0 |
| 6 | V8 sizing 2–4% | Chưa có | §0 | 0 |

## 2. Độ nhạy r (V1 + D4 + E15) — cùng mô hình, chỉ đổi r (vốn giữ lại trong cam kết/XDCB sinh lời = r đổi theo; lãi tiền gửi sau thuế giữ 5,92%)

| r | Tâm | P10 | P90 | Δ tâm (đ/cp) | Δ tâm (%) | % trọng số dưới 21.200 |
|---|---|---|---|---|---|---|
| 12,3% (E15, đầu dưới dải Ke) | 23.625 | 14.619 | 32.232 | +2.287 | +10,72% | 35,0% |
| 12,5% (−100bp) | 23.213 | 14.385 | 31.649 | +1.875 | +8,79% | 37,2% |
| 13,0% (−50bp) | 22.239 | 13.830 | 30.269 | +901 | +4,22% | 43,9% |
| 13,4% (đầu trên dải Ke) | 21.513 | 13.416 | 29.241 | +175 | +0,82% | 46,7% |
| **13,5% BASE** | **21.338** | **13.316** | **28.993** | 0 | 0 | 46,7% |
| 14,0% (+50bp) | 20.501 | 12.837 | 27.809 | −837 | −3,92% | 53,3% |
| 14,5% (+100bp) | 19.722 | 12.391 | 26.709 | −1.616 | −7,57% | 58,9% |

- Bốn mốc ±50/±100bp khớp đúng r3 §4 (23.213 / 22.239 / 20.501 / 19.722).
- Nhãn TRONG ở mọi mức r trong bảng.

## 3. Soát luật B5 (D3/D4/V1–V8)

- **D4 terminal:** g_RI = 0 (vốn mới = Ke). ROE terminal sau thuế 20% (r3 §3): XẤU 10,36% · TRUNG LẬP 14,33% · TỐT 16,66% — spread trên vốn hiện hữu tồn tại vĩnh viễn ở TRUNG LẬP/TỐT (không fade); đây là tham số luật của r3 (moat NARROW ⇒ không trừ ở pha dự báo, V5), ghi để phản biện xét.
- **D3 capex tuân thủ:** không nhận diện được trong r3 một dòng chi bắt buộc-không-tạo-doanh-thu. Ứng viên: xử lý môi trường/khí thải khu liên hợp Dung Quất – Hải Dương (luật BVMT, giấy phép môi trường), cải tạo/hoàn nguyên mỏ. Không có số trong tài liệu đã đọc ⇒ **cần kiểm chứng** (thuyết minh cam kết vốn HN-Q3 TM41 chỉ ghi tổng 19.472 tỷ tại 30/06, chưa tách phần môi trường); không vào base, không ước. Cam kết vốn DQ2 = tăng trưởng ⇒ V4(a) sinh lời = r (NPV 0) — đã đúng ở r3.
- **V1/D4 r:** đúng neo (Δ = 0); dải Ke nay đã báo (§2).
- **E15/E16:** đã thêm (§0).
- **V3 thanh khoản:** đã đủ (r3 §8): trước CK 21.370, sau CK 5 tỷ (0,15%) 21.338; sleeve 10–40 tr dưới vùng hiệu chỉnh.
- **V5 moat:** đã đủ — 5F 07/11/2026 < 12 tháng: NARROW COST/SCALE, không bền ⇒ g_RI = 0. Kiểm nhanh 25/11: không đọc BCTC/CBTT mới.
- **V6 (bổ sung, chỉ hiển thị):** nền máy `dd_blend_20261111/out/apply_dd.csv` (as-of 10/11, fin_time 29/10; khôi phục từ `3750ca176^`): **FCFE chuẩn hoá 3 năm ≤ 0** (capex > CFO, tái đầu tư nặng — DQ2) ⇒ chỉ V_ngắn **12.577** (LNST chuẩn hoá 14.398 tỷ, ROE 10,2%, g 12,75% ⇒ ROE < g, tái đầu tư bị chặn ở 80%), không có V_dài/D. Đọc: dòng tiền âm vì đầu tư tăng trưởng (DQ2), KHÔNG phải cảnh báo đắt; V_ngắn sụp vì ROE TTM 10,2% < g. Không trộn vào tâm.
- **V7:** không dùng snapshot vĩ mô.

## 4. Lưu ý kế thừa r3 (đưa phản biện xét hai chiều — KHÔNG đổi base)
1. Nhánh TỐT đếm trùng lợi ích capex (bản J 20.673, −665; khoảng tâm 20.673–21.338).
2. Cam kết vốn 19.472 là số 30/06 (phần chi Q3 đã vào XDCB 30/09 ⇒ trùng ~−200 đ/cp ở mức r; ước lượng, chưa chạy lại).
3. Thuế: mốc 2035 là ước lượng; ETR hiện hành suốt 2030–34 trái GAPS.md:70 (DQ1 lên 10% từ ~2032); TAXF 0,80/0,88 (ETR 12%) vs ETR phân khúc thép đo được 6,5% (REPORT_v2 §3d) — chưa chạy lại. Bản B thuế 2030 ⇒ 20.648; bản C ETR vĩnh viễn ⇒ 22.119.
4. TLSH 9.915 tỷ theo sổ (bản E trục r2 ⇒ 21.144).
5. Chiều lên: g_RI kiểu r2 (bản D) 22.530 — bị loại vì thưởng moat ngầm; Ke đầu dưới +10,7%.

## 5. WARNING (giữ r3 §6)
Hệ Đại Quang Minh–TLSH (25,13% TLSH 7.995 tỷ; BĐS Hòa Phát 26,55%; liên danh sông Hồng) · bên mua 2 công ty BĐS chưa công bố · ưu đãi thuế DQ2 (CV 377/TCT-CS) · AD QĐ 1959/1902/1917 · tiền gửi cầm cố 8.294 tỷ · giao dịch nội bộ. Chưa quét pháp lý sau 08/11. Pháp lý chỉ WARNING.

## 6. Phạm vi đề nghị cho phản biện (§E4, DD_GENERAL)
Moat (NARROW + spread ROE_T > r vĩnh viễn trên vốn hiện hữu có là thưởng ngầm không), cân bằng hai chiều (xuống: §4.1–4.3, D3 môi trường; lên: Ke đầu dưới +10,7%, ETR thép 6,5% thấp hơn ETR 12% dùng trong TAXF ⇒ có thể làm tâm thấp đi), thiếu hạng mục (D3; quỹ KTPL trích từ LNST; cổ tức cổ phiếu/pha loãng; lợi ích CĐ không kiểm soát), và kiểm bảng độ nhạy r §2 (tái chạy theo lệnh ở đầu báo cáo).
