# DD CSV (Hoá chất Cơ bản Miền Nam) · ứng viên LAG_LO · **r5 — 23/11/2026** · job `Taylor_20261123_120254`

> **r5 thay r4 (`REPORT_r4.md`). Đây là vòng skeptic CUỐI của ca này** (user duyệt 23/11 19:00).
> Lịch sử: r2 (`REPORT.md`) → skeptic r1 REFUTED → r3 → skeptic r2 INCONCLUSIVE → r4 → skeptic r3 INCONCLUSIVE (`skeptic/r3.json`) → **r5**.
>
> Tâm (sau CK thanh khoản cỡ 5 tỷ): r2 20.717 → r3 11.041 → r4 11.224 → **r5 10.447 đ/cp (−6,9% so với r4)**. Nhãn giữ **TRÊN vùng**. Đính chính chi tiết: Phụ lục E-C.
>
> Chỉ nghiên cứu: không đặt lệnh, không wire, không gửi email, không ghi sổ giá.
>
> **Khoá giả định.** Khoá mù giá gốc vẫn là `calc/assumptions_r3.json` (md5 `05e886fe…`, `LOCK_r3_prerun.txt`). r5 **khoá lại sau khi đã thấy giá** (giá 20.300 đã biết từ r3/r4), lý do: skeptic r3. r5 **không truy vấn giá mới** (postlock dùng lại `px_csv_r3.csv` md5 `7d2e86d2`). Mọi thay đổi r5 lấy từ BCTC kiểm toán FY2025 hoặc là sửa phương pháp đúng như skeptic r3 khuyến nghị; không tham số nào chỉnh theo giá.
> - `calc/assumptions_r5.json`, `calc/model_r5.py`, `calc/LOCK_r5.txt` (md5 toàn bộ đầu vào, gồm `src/fy2025_HN_kiemtoan.pdf` md5 `af037ff241cdafdefac5d928ed39a9a1` và ảnh trang `src/png_r5/`).
> - Schema v1: `calc/lock_v1_r5.json`, `dd_assumptions_lint.py --strict` **0 vi phạm**.
>
> **Tái lập** (từ thư mục CSV/): `/home/trido/thanhdt/wc_venv/bin/python -I calc/model_r5.py` (chạy 2 lần: `run1_r5.txt` = `run2_r5.txt`, md5 `346004d382dee8466a8f6ef8feb4d455`); `calc/postlock_r5.py` cho thanh khoản và nhãn. Model r5 tái lập đúng r4 khi tắt ba thay đổi: 11.417 trước CK (khớp r4).

## 1. Kết luận (r5)
| | Tâm | P10 | P25 | P50 | P75 | P90 | Giá 20/11 | Nhãn |
|---|---|---|---|---|---|---|---|---|
| Trước chiết khấu thanh khoản | 10.627 | 6.564 | 8.376 | 10.632 | 12.763 | 14.842 | 20.300 | TRÊN vùng |
| **Sau CK, cỡ 5 tỷ (headline)** | **10.447** | **6.453** | 8.234 | 10.452 | 12.547 | **14.591** | 20.300 | **TRÊN vùng** |
| Sau CK, cỡ 1 tỷ | 10.546 | 6.514 | 8.312 | 10.552 | 12.666 | 14.730 | 20.300 | TRÊN vùng |
| Sau CK, cỡ 40 tr | 10.611 | 6.554 | 8.363 | 10.616 | 12.743 | 14.820 | 20.300 | TRÊN vùng |

- **Giá so với vùng.** Giá 20.300 cao hơn tâm **94,3%** và cao hơn P90 39,1%. Toàn bộ trọng số lưới (729 kết cục) nằm dưới giá.
- **Luật 4 trượt.** Ngưỡng 0,85 × tâm = **8.880**.
- **Giá ngụ ý:** r ≈ **7,21%** (lãi huy động 12T ≈ 1,11%, hiện 7,40%). Kể cả φ = 0 (không trừ đồng capex thay thế nào) chỉ ra **19.073** < giá ⇒ không có φ ≥ 0 nào đạt giá.
- **Ba thay đổi so với r4** (cầu nối §6): APV cho capex cam kết **+446**, chu kỳ tái đầu tư trong base **−269**, trích quỹ KTPL theo số kiểm toán **−954** đ/cp.
- **Sizing (V8): 0% NAV tại giá hiện tại.** Nếu giá ≤ 8.880 thì xét 2% NAV, trần 4%; mỗi phiên ≤ 1 tỷ.

## 2. Chất lượng lợi nhuận (tái dùng r4 §2, đã được skeptic r1–r3 kiểm khớp)
- LN mẹ 2026: Q3 85,40 tỷ (+47,9% YoY), Q2 130,03 tỷ, 9T 258,32 tỷ (+49,5%). Phần vượt: giá H2SO4, phốt pho vàng, hàng thương mại (G3). Lợi nhuận thật nhưng chu kỳ.
- LN mẹ 2019–2025 (BQ, 2025 khớp BCTC kiểm toán 208,948 tỷ): 244,02 / 179,66 / 208,93 / 353,21 / 209,18 / 240,78 / 208,95. Trung bình **234,96**; TTM **294,49**.

## 3. Bảng cân đối, dòng tiền, quỹ (30/09/2026 + BCTC kiểm toán FY2025)
- **Tiền ròng dùng cho định giá 484,69 tỷ** = tiền 154,63 + tiền gửi 630,60 − vay NH 259,62 − quỹ KTPL (mã 323) 25,92 − quỹ KH&CN (mã 344) 15,00. CĐKKS 49,96 tỷ.
- **Trích quỹ KTPL từ LNST — ĐÍNH CHÍNH r5: 9,55%, không phải 2,43%.**
  - BCTC kiểm toán FY2025, TM33 (trang in 36, `src/png_r5/fy2025_kt_p38.jpg`): trích quỹ khen thưởng, phúc lợi từ LN 2025 = **20.900.000.000** đ trên LNST mẹ 208.948.230.404 = **10,00%**; từ LN 2024 = **21.689.605.950** trên 238.636.262.415 = **9,09%** (NQ ĐHĐCĐ 02/2025). Trung bình **9,55%**.
  - TM23.1 (`src/png_r5/fy2025_kt_p32.jpg`) xác nhận dòng ra khỏi VCSH: 2025 "trích lập quỹ từ lợi nhuận" mẹ 85,13 tỷ, trong đó 63,54 vào quỹ ĐTPT (giữ trong VCSH) ⇒ 21,59 tỷ ra quỹ KTPL; 2024: 95,18 − 74,04 = 21,15 tỷ.
  - r4 dùng 2,43% = chỉ phần trích **bổ sung** 9T/26 (TM17a Q3: 2,431 + 2,656 tỷ) — bỏ sót phần chính. Đây là lỗi số liệu Taylor tự phát hiện khi đọc lại BCTC kiểm toán cho hạng mục chu kỳ tái đầu tư.
  - Độ nhạy: 2,43% (r4) ⇒ 11.401; 11,4% (gồm cả trích quỹ ở công ty con, phần mẹ 5,50 tỷ năm 2025) ⇒ 10.199.
- **TSCĐ hữu hình 31/12/2025** (TM11, `src/png_r5/fy2025_kt_p25.jpg`): nguyên giá 1.137,43 tỷ; giá trị còn lại 44,60 tỷ. **Nguyên giá TSCĐ đã hết khấu hao nhưng vẫn còn sử dụng 1.049,44 tỷ = 92,3%** (31/12/2024: 939,55 tỷ). Khấu hao 2025 **33,90** tỷ, 2024 **44,60** tỷ (LCTT mã 02, `fy2025_kt_p10.jpg`; khớp TM31). Capex (mã 21) 2025 **59,26**, 2024 **22,44** tỷ. Capex 2017–25 BQ `CF_Invest_P0` trung bình ≈ 42 tỷ/năm (skeptic r3 tự query; 2025 BQ 59,26 khớp BCTC).
- **Lãi vay:** lãi hiệu dụng 9T/26 6,37%/năm (r4 §3). Dòng tiền 9T: CFO +197,8; capex 265,7. Trả trước người bán 242,4 tỷ: không thuyết minh (G2). Số cổ phiếu 110.499.910 (mã 411; khớp số CP bình quân TM33).

## 4. Nhơn Trạch = phần thay thế bắt buộc (D3) + phần tăng trưởng (V4a)
Dữ kiện, φ (0,5/0,65/0,8), lịch, cưỡng chế, bồi thường, đất HCM: **giữ nguyên r4 §4** (nguồn: cafef 04/08/2026, danchuphapluat 18/08/2026, baodauthau 03/07/2025, BCTN 2021, TCCT 21/05/2025, QĐ 2408, QĐ 1122, TB 610).

**Công thức base r5** (tỷ đồng, chia 110,50 triệu cp):
```
Giá trị = (E·(1+dE) − 32,65)·(1 − 9,55%)/r + 484,69 − 49,96
          + (1−φ)·346,48                                          [phần tăng trưởng đã chi, giá vốn]
          − φ·[1.497,5 − NPV_tài_trợ(kd)]/(1+8,0%)^t              [APV: capex cam kết còn chi ở r_commit; vay 1.212/10 năm]
          + φ·1.844·20%/L·niên_kim(r,L)/(1+r)^t                   [lá chắn thuế khấu hao lần xây đầu, L=12]
          − φ·1.844·(1 − 20%·niên_kim(r,L)/L)/((1+r)^N − 1)/(1+r)^t   [CHU KỲ tái đầu tư mỗi N năm, mỗi chu kỳ có lá chắn riêng]
          + npv·(1−φ)·1.844                                        [trục NPV phần tăng trưởng, kỳ vọng 0]
```
- **APV (sửa lỗi logic skeptic r3).** Toàn bộ capex còn chi 1.497,5 tỷ là dòng cam kết ⇒ chiết khấu ở **r_commit = 8,0% cố định** (= kd trước thuế 6,37% đo + 1,6pp ước lượng). Khoản vay 1.212 tỷ là quyết định tài trợ riêng: giải ngân tại t, trả gốc đều 10 năm (kỳ hạn 10 năm: baodauthau; lịch trả cụ thể **không kiểm chứng được** ⇒ trả gốc đều là ước lượng), NPV tài trợ = 1.212 − PV₈%(gốc + lãi × (1 − 20%)) = **+79,7 tỷ** tại kd 8% (= lá chắn thuế lãi vay). kd tăng ⇒ giá trị **giảm** (kd 9,5%: −2,9%; kd 6,4%: +3,1%) — đúng chiều kinh tế, khác r4.
- **Chu kỳ tái đầu tư (killer objection skeptic r3) — đưa vào base.**
  - Mỗi N năm sau lần xây đầu, phần thay thế φ·1.844 phải xây lại; mỗi chu kỳ được lá chắn khấu hao riêng (L = 12), chiết khấu ở Ke.
  - **N là đời kinh tế, không phải đời khấu hao kế toán.** Bằng chứng độc lập: 92,3% nguyên giá TSCĐ đã hết khấu hao vẫn đang chạy (TM11 kiểm toán) ⇒ đời kinh tế ≫ L = 12. Lá chắn thuế theo L = 12 là đúng vì thuế đi theo khấu hao kế toán; chi phí thay thế đi theo đời kinh tế. Hai đời khác nhau là nhất quán, không phải mâu thuẫn — nhưng r4 sai ở chỗ không có chu kỳ nào.
  - Trục **N = 20/30/40 năm, trọng số 0,25/0,5/0,25 (ước lượng)**. Cận dưới 20 = mức skeptic r3. Nguyên giá / capex lịch sử ≈ 1.137 / 42 ≈ 27 năm.
  - **Thận trọng:** KHÔNG trừ capex duy trì ~39 tỷ/năm đã nằm trong E (khấu hao 2025 33,9 / 2024 44,6 ≈ capex 59,3 / 22,4 ⇒ E lịch sử ≈ FCF chế độ cũ). Phần này có thể trùng một phần với chu kỳ (chiều RẺ, không định lượng).
  - Tác động: **−269 đ/cp**. Độ nhạy N = 12 (= L kế toán, mức skeptic): **8.540 (−18,3%)** — bị bác làm base vì trái với bằng chứng 92,3% tài sản hết khấu hao vẫn dùng.

**Tại tham số trung tâm** (φ 0,65, t 1,75, N 30, CƠ SỞ): giá trị **10.668** trước CK.

**Bồi thường / hoàn nguyên / đất HCM:** như r4 — bồi thường base 0 (có căn cứ NĐ 88/2024, VB 719 nhưng không có số), hoàn nguyên **không kiểm chứng được** (WARNING + độ nhạy), đất HCM là đất thuê ⇒ 0.

## 5. 5F tầng (b) — TÁI DÙNG (< 12 tháng)
`data/moat_tags.csv` (2026-06-05): NARROW · COST/SCALE; ROE_Min5Y 13,66% ≈ Ke. Không thưởng moat, RONIC = Ke (D4). Độ nhạy thưởng moat: 11.792, vẫn TRÊN vùng.

## 6. Định giá
**Chi phí vốn (V1):** r = 13,5% + 1,0 × (7,40% − 7,40%) = **13,50%** (`deposit_rate_vn.effective_deposit_rate('2026-11-23')` = cctg_12m 7,40%).

| Lãi huy động | Tâm (sau CK 5 tỷ) | Δ |
|---|---|---|
| −100bp | 11.395 | +9,1% |
| −50bp | 10.905 | +4,4% |
| +50bp | 10.020 | −4,1% |
| +100bp | 9.620 | −7,9% |

β = 0,5: ±100bp ⇒ 10.905 / 10.020. Dải Ke nội địa (D4): Ke 12,3% ⇒ 11.603; Ke 13,4% ⇒ 10.536.

**Kịch bản** (0,25/0,5/0,25, ước lượng; dE ±10%), tại tham số trung tâm, trước CK: XẤU (LN 179,7) **7.315** · CƠ SỞ (235,0) **10.668** · TỐT (TTM 294,5) **14.277**. Lưới 729 kết cục = 3 kịch bản × 3 dE × 3 φ × 3 thời điểm × 3 NPV × 3 N. Sau CK 5 tỷ: min 2.038, max 19.915.

**Cầu nối r4 → r5** (sau CK 5 tỷ, cùng model):
| Bước | Tâm | Δ |
|---|---|---|
| r4 tái lập | 11.224 | |
| + APV (capex cam kết ở 8%, NPV vay 10 năm) | 11.670 | +446 |
| + chu kỳ tái đầu tư N 20/30/40 | 11.401 | −269 |
| + trích quỹ KTPL 9,55% (kiểm toán) = **r5** | **10.447** | −954 |

**Độ nhạy** (sau CK 5 tỷ; base 10.447):
| Độ nhạy | Tâm | Δ |
|---|---|---|
| φ = 1,0 / 0,8 | 5.802 / 8.457 | −44,5% / −19,0% |
| φ = 0,5 / 0,33 / 0 | 12.437 / 14.693 / 19.073 | +19,0% / +40,6% / +82,6% |
| Chu kỳ N = 12 (= L kế toán, mức skeptic) | 8.540 | −18,3% |
| Chu kỳ N = 20 / N = 40 | 10.045 / 10.667 | −3,8% / +2,1% |
| Không chu kỳ (= r4) | 10.716 | +2,6% |
| Quỹ KTPL 2,43% (r4) / 11,4% (gồm công ty con) | 11.401 / 10.199 | +9,1% / −2,4% |
| kd 6,4% / 9,5% (r_commit giữ 8%) | 10.770 / 10.144 | +3,1% / −2,9% |
| r_commit = Ke (capex cam kết chiết khấu ở 13,5%) | 12.038 | +15,2% |
| Không APV (cách r4: vay ở kd sau thuế, VCSH ở Ke) | 10.001 | −4,3% |
| Không lá chắn thuế khấu hao | 9.589 | −8,2% |
| Đời khấu hao 8 / 20 năm | 10.638 / 10.196 | +1,8% / −2,4% |
| Không chiết khấu thời gian capex (t = 0) | 9.566 | −8,4% |
| TỐT thay bằng CƠ SỞ (TB2 dừng) | 9.560 | −8,5% |
| Gián đoạn 0/−25/−50% (0,4/0,4/0,2) | 10.120 | −3,1% |
| Hoàn nguyên môi trường −100 tỷ | 9.558 | −8,5% |
| Bồi thường BH1 +100 tỷ | 11.337 | +8,5% |
| G2: 200 tỷ ứng trước là của Nhơn Trạch | 12.083 | +15,7% |
| Giá điện +5% (giả định điện = 50% dịch vụ mua ngoài, ước lượng) | 9.720 | −7,0% |
| Thưởng moat (RONIC 18,3%, g 4%) | 11.792 | +12,9% |

**V6 (chỉ hiển thị):** V_ngắn (LN trung vị 2023–25 = 209,2 tỷ, g = 0) = **8.951** sau CK. V_dài: FCFE ≤ 0 trong giai đoạn capex ⇒ chỉ báo V_ngắn. Không ghi sổ.

**Đối chiếu nhanh:** P/E trên LN chuẩn hoá 9,5x; P/E TTM 7,6x; P/B mẹ 1,23x.

## 7. Thanh khoản và sizing (V3, V8)
σ ngày 2,25%; ADV250 **8,88 tỷ**; ADV60 7,32 tỷ (không đổi so với r4, cùng `px_csv_r3.csv`). CK: 5 tỷ **1,69%** (Q/ADV 56%, ngoài vùng hiệu chỉnh); 1 tỷ 0,76%; 40 tr 0,15%. Thoát 5 tỷ: 5,6 phiên ở 10% tham gia (2,8 ở 20%). Free float ≤ 35%. **Sizing V8: 0% NAV**; xét 2% (trần 4%) chỉ khi giá ≤ 8.880, mỗi phiên ≤ 1 tỷ.

## 8. Mốc đổi nhận định CẢ HAI chiều
| Chiều | Mốc (kiểm bằng BCTC/CBTT) | Tác động |
|---|---|---|
| NÂNG | Công bố cơ cấu capex/công suất theo dây chuyền cho thấy φ < 0,5 | ≈ +1.330 đ/cp mỗi −0,1 φ |
| NÂNG | Số bồi thường BH1 (NĐ 88/2024, VB 719) | +890 đ/cp mỗi 100 tỷ |
| NÂNG | Thuyết minh xác nhận ~200 tỷ trả trước là của Nhơn Trạch (G2) | +1.636 đ/cp |
| NÂNG | Q4/26 ≥ 70 tỷ và Q1/27 ≥ 60 tỷ, doanh thu axit vẫn cao sau khi TB2 dừng | Xác nhận TỐT |
| NÂNG | Lãi huy động 12T −100bp | +948 đ/cp |
| HẠ | Q4/26 doanh thu/biên H2SO4 sụt sau khi TB2 dừng | Bỏ TỐT ⇒ ~9.560 |
| HẠ | Vượt dự toán 1.844 tỷ / trễ > 6 tháng | phần còn chi tăng; trục NPV (−) |
| HẠ | Chi phí hoàn nguyên do công ty chịu, có số | −890 đ/cp mỗi 100 tỷ |
| HẠ | ĐHĐCĐ 2027 trích quỹ KTPL > 10% LNST | ≈ −134 đ/cp mỗi +1pp |
| HẠ | Biên gộp quý < 20% hoặc LN mẹ quý < 40 tỷ trong giai đoạn di dời | dồn về XẤU; gián đoạn |

**HARD ABANDON:** kiểm toán ngoại trừ BCTC 2026; dừng sản xuất > 1 quý không có công suất thay thế; vay để chia cổ tức.

## 9. Pháp lý, quản trị, kiểm toán (chỉ WARNING, không vào tâm)
Như r4 §9: cưỡng chế BH1 / dừng TB2 là đề án chuyển đổi KCN, không phải xử phạt; cờ quản trị "không chấp hành tháo dỡ" (QĐ 2408). Kiểm toán FY2025 FAC 041/2025 chấp nhận toàn phần; soát xét 6T/2026 FAC 044/2026 chấp nhận toàn phần; `audited_fy_missing = false`. NQ HĐQT 2026 và NQ tổng vốn Nhơn Trạch không có trong `src/` (không kiểm chứng được, ảnh hưởng ước lượng < 1%).

## 10. Giả định [ước lượng] (đầy đủ ở `calc/assumptions_r5.json`)
Trọng số kịch bản 0,25/0,5/0,25; dE ±10%; φ 0,5/0,65/0,8; thời điểm 0,5/1,75/3,0 năm; NPV tăng trưởng ±20%; **N 20/30/40 (0,25/0,5/0,25)**; kd 8,0% (6,37% đo + 1,6pp); **r_commit 8,0%**; **vay trả gốc đều 10 năm**; L 12 năm; lãi tiền gửi sau thuế 32,65 tỷ/năm; **trích quỹ 9,55% (đo, kiểm toán)**; bồi thường = 0; hoàn nguyên = 0; điện không tách được.

## 11. File
`REPORT_r5.md` (bản này) · `calc/assumptions_r5.json`, `calc/model_r5.py`, `calc/run1_r5.txt`/`run2_r5.txt`, `calc/model_r5_out.json`, `calc/postlock_r5.py`/`_out.json`, `calc/lock_v1_r5.json`, `calc/LOCK_r5.txt`, `calc/fin_dep_bq_r5.sql`/`.csv` (BQ EBITDA/CF_Invest — trường EBITDA_P0 không dùng được để tách khấu hao, chỉ dùng CF_Invest đối chiếu) · `src/png_r5/fy2025_kt_p10/p25/p32/p36/p38.jpg` (ảnh trang trích từ `src/fy2025_HN_kiemtoan.pdf`). Bản r2–r4 giữ nguyên.

## Phụ lục E · Đính chính
E-A (r2 → r3) và E-B (r3 → r4): xem `REPORT_r4.md` Phụ lục E.

**E-C. Từ r4 sang r5** (skeptic r3 INCONCLUSIVE medium, `skeptic/r3.json`)

| # | Hạng mục skeptic r3 | Loại | Xử lý trong r5 | Tâm |
|---|---|---|---|---|
| H1 | **Không có chu kỳ tái đầu tư** nhà máy mới trong base, trong khi lá chắn thuế dùng L = 12 (killer objection) | (a) + (b) | **Đưa vào base:** chu kỳ φ·1.844 mỗi N năm, mỗi chu kỳ có lá chắn riêng. Cơ sở độc lập cho N ≫ 12: TM11 kiểm toán FY2025, 92,3% nguyên giá TSCĐ hết khấu hao vẫn sử dụng. Giá trị N chính xác không đo được ⇒ trục 20/30/40 (ước lượng). N = 12 ở độ nhạy (−18,3%) | −269 |
| H1b | Chưa đối chiếu khấu hao P&L với capex ~42 tỷ/năm | (a) | Đo từ BCTC kiểm toán: khấu hao 2025 33,90 / 2024 44,60 tỷ; capex 59,26 / 22,44 tỷ ⇒ E lịch sử đã gánh mức tái đầu tư duy trì ≈ khấu hao. Không trừ khỏi chu kỳ (thận trọng) | — |
| H2 | Gián đoạn sản xuất 2026–31 không nằm trong base | (b) | Giữ ở độ nhạy (−3,1%): TB2 dừng là sự thật, nhưng Q3/26 (6 tuần sau dừng) LN +47,9% YoY ⇒ chưa có cơ sở đo mức giảm; luật: điều chỉnh GIẢM cần cơ sở độc lập. Mốc kiểm: BCTC Q4/26 | độ nhạy |
| H3 | TỐT mâu thuẫn TB2 dừng | (c) | Không kiểm chứng được tới BCTC Q4/26; giữ, độ nhạy −8,5%, mốc §8 | độ nhạy |
| H4 | Hoàn nguyên môi trường không có số | (c) | Không kiểm chứng được; WARNING, độ nhạy −8,5% / 100 tỷ | độ nhạy |
| H5 | Biểu giá điện xút–clo không được nhắc | (c) | BCTC không tách chi phí điện; TM31 FY2025 dịch vụ mua ngoài 610,1 tỷ (2024: 497,7) là cận trên. E 2019–25 đã gồm biểu giá tới 2025. Độ nhạy giá điện +5% (điện = 50% DV mua ngoài, ước lượng) −7,0%; tiết kiệm điện của công nghệ mới: không có số | độ nhạy |
| H6 | Chiết khấu capex ở kd làm giá trị tăng khi kd tăng | (a) | **Sửa bằng APV** (đúng khuyến nghị skeptic): capex cam kết ở r_commit 8% cố định; NPV tài trợ vay 10 năm riêng. kd 9,5% ⇒ −2,9% (đúng chiều) | +446 |
| H7 | Chiều RẺ: hiệu suất nhà máy mới | (c) | Không có số; ghi nhận chiều | — |
| H8 | Chiều RẺ: bồi thường BH1 | (c) | Không có số; độ nhạy +8,5% / 100 tỷ | độ nhạy |
| H9 | Chiều RẺ: φ theo capex < 0,65 | (c) | Không có dữ liệu capex theo dây chuyền; ≈ ±1.330 / 0,1 φ | độ nhạy |
| H10 | Chiều RẺ: G2 trả trước 242 tỷ | (c) | BCTC Q3 không thuyết minh; độ nhạy +15,7% | độ nhạy |
| T1 | *(Taylor tự phát hiện khi đọc lại BCTC kiểm toán)* Trích quỹ KTPL 2,43% sai | (a) | TM33 + TM23.1 kiểm toán FY2025: 10,00% (2025), 9,09% (2024) ⇒ **9,55% vào base** | −954 |

**Chiều và lý do đổi tâm:** −777 đ/cp (−6,9%), chủ yếu do T1 (lỗi số liệu, có nguồn kiểm toán) và H1 (chu kỳ, có cơ sở kiểm toán cho đời kinh tế); H6 kéo lên (sửa phương pháp theo đúng khuyến nghị skeptic). Nhãn TRÊN vùng không đổi ở mọi độ nhạy trên.

**Còn mở sau r5 (không đủ nguồn độc lập):** giá trị N chính xác; gián đoạn 2026–31 (chờ Q4/26); TỐT vs TB2; hoàn nguyên; chi phí điện; bồi thường; φ theo capex; G2; lịch trả nợ vay dự án.
