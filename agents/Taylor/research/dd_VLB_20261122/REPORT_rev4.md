# DD — VLB (CTCP Xây dựng và SX VLXD Biên Hòa, UPCoM) · rev4 · 23/11/2026 · job `Taylor_20261123_120307`

> Rev4 = vòng sửa CUỐI theo verdict skeptic r2 (INCONCLUSIVE medium, `skeptic/r2.json`, chấm trên `REPORT_rev3.md`). KHÔNG ghi đè rev3.
> Chỉ là nghiên cứu: không khuyến nghị, không đặt lệnh.
> Mô hình: `model/dcf_vlb_r4.py` (md5 `05cc094364d09b4c90b3ffbf7ecac207`) · output `model/output_r4.txt` · cầu nối `model/bridge_r4.txt`.
> File khoá giả định: `assumptions_VLB_r4.json` (md5 `08740786baa1e16556cc848439ba9d3d`); `dd_assumptions_lint` 0 vi phạm.
> Nguồn MỚI rev4 (tải 23/11/2026 từ cafef.vn `du-lieu/Ajax/PageNew/FileBCTC.ashx`, bản công ty nộp, có chữ ký số):
> Số trang = trang PDF. [KT25 p.x] = `src/BCTC_KiemToan_2025.pdf` (md5 `a251aaf3a2fcdd2d5fae5ca591faaebd`) · [BCTN p.x] = `src/BCTN_2025.pdf` (md5 `bc03c6ff99bb65e30021eb32676f3d6d`)
> · [HĐQT 16/01/26] = `src/NQHDQT_20260116_KHSXKD2026.pdf` · [HĐQT 30/10/25], [HĐQT 17/11/25], [ĐHĐCĐ BT 09/12/25] = `src/NQHDQT_20251030.pdf`, `src/NQHDQT_20251117.pdf`, `src/NQDHCDBT_20251209.pdf`.
> Nguồn giữ từ rev3: [Q3 p.x] `src/BCTC_Q3_2026.pdf` · [H1 p.x] `src/BCTC_BanNien_2026.pdf` · [NQ p.x] `src/nhan_su_0617.pdf` · [BV26 p.x] `src/BVSC_VLB_update_202602.pdf` · [FP p.x] `src/FPTS_VLB_update_20260406.pdf`.
> **Mù giá:** giả định khoá trước §8. Giới hạn (khai thật): rev trước đã có giá 20/11; trong lúc tìm tài liệu ở rev này, thẻ meta trang cafef VLB có hiện giá chiều 23/11
> (48.600). Không dùng giá đó cho bất kỳ giả định nào; mọi thay đổi giả định ở rev4 đều xuất phát từ tài liệu nguồn mới (BCTN, BCTC kiểm toán) — xem §1.

## 0. Kết luận

- **Tâm giá trị** (kỳ vọng trọng số 3 kịch bản, sau chiết khấu thanh khoản Q = 5 tỷ):
  - **47.661 đ/cp** theo cơ sở 30/9/2026.
  - **45.161 đ/cp** theo cơ sở ex-div (trừ cổ tức tạm ứng 2026 2.500 đ, GDKHQ 19/11/2026). Đây là cơ sở so giá và ghi sổ.
  - So với rev3: **42.800 → 45.161 (+5,5%)** cùng cơ sở ex-div. Trước CK: 46.689 → 49.123 (+5,2%).
- **Vùng** (ex-div, sau chiết khấu): xấu **34.783** · cơ sở **44.940** · tốt **55.983**.
- **Ba thay đổi gây dịch tâm** (cầu nối trước CK, `model/bridge_r4.txt`):
  1. **Hạn giấy phép theo nguồn sơ cấp của công ty** [BCTN p8, có số GP] thay bảng tổng hợp BVSC: Thạnh Phú 1 **31/7/2042** (BVSC: 1/2038),
     Tân Cang 1 **01/01/2039** (BVSC: 1/2038), Thiện Tân 2 **30/6/2038** (BVSC: 8/2041) ⇒ **+3,5%**. Đời mỏ bình quân 11,2 → **12,5 năm**.
  2. **LN gốc không còn phẳng 310.** Năm 1 = lõi TTM 357,4; phần vượt mức giữa chu kỳ (lõi FY25 kiểm toán **265,05** × 1,02^t) giảm tuyến tính
     về 0 ở năm 3 ⇒ **−3,0%** (xử lý killer objection của skeptic r2).
  3. **Vốn lưu động quay vòng** (ứng trước đủ 76,9 + WC ròng 67,1) tất toán khi đóng từng mỏ thay vì trừ ngay ⇒ **+4,0%**.
- **BCTC kiểm toán 2025 ĐÃ CÓ** [KT25 p7-8]: A&C, BC số 1.0386/26/TC-AC ngày 20/3/2026, **chấp nhận toàn phần, không đoạn nhấn mạnh**;
  không có sự kiện trọng yếu sau ngày kết thúc năm [KT25 p39]. ⇒ `audited_fy_missing = false`.
- **Moat NARROW / LOCATION** (tag 2026-06-05, tái dùng). Đồng hồ cắt hào: 1/2039 (TC1), 6/2038 (TT2), 7/2042 (TP1).
- **Pháp lý:** chỉ WARNING (tiền cấp quyền đảo chiều 2022↔2026; rà soát Soklu; đất theo Kiểm toán NN). Không vào base.

## 1. Đính chính so với rev trước (từng hạng mục skeptic r2 → xử lý)

Phân loại: **(a)** = có nguồn độc lập, đưa vào base · **(b)** = kịch bản/độ nhạy · **(c)** = không kiểm chứng được, ghi ảnh hưởng ước lượng.

| # | Hạng mục skeptic r2 | Xử lý rev4 | Loại | Tác động (tâm trước CK) |
|---|---|---|---|---|
| 1 | **Killer objection:** LN gốc 310 tăng 2%/năm suốt 11–13 năm, cao hơn mọi năm lõi đã kiểm toán (lõi FY25 264,8; 2017–2024 ≤218), dựa TTM ở đỉnh chu kỳ | Lõi FY25 lấy thẳng từ KQKD kiểm toán [KT25 p13]: (376,993 − DTTC 30,655 − LN khác 15,031) × 0,8 = **265,05**; FY24 cùng định nghĩa **212,1**. Đường cơ sở: năm 1 = TTM 357,4 → năm 2 321,4 → năm 3 285,5 → sau đó mức giữa chu kỳ 265,05 tăng 2%/năm (năm 6: 303,0). Cơ sở độc lập cho việc giảm dần: KQKD kiểm toán FY24/FY25; BVSC [BV26 p3] cầu cụm Tân Cang giảm sau Long Thành GĐ1; BCTN 2025 ghi Long Thành GĐ1 "cơ bản hoàn thành" năm 2025 [BCTN p16]. Không hạ thêm về 212 (FY24) vì giá bán 2025–26 đã nâng theo thuế tài nguyên/chi phí (QĐ 62/2025, [Q3 p19-21]) — không có cơ sở độc lập cho đảo chiều giá | (a) | **−3,0%**. Độ nhạy: phẳng 265 g0 −11,2%; mid = lõi FY24 −15,7%; giữ TTM +15,4%; phẳng 310 (r3) +4,4%; fade 1 năm −1,2%; fade 4 năm +2,1% |
| 2 | Kịch bản xấu chỉ đặt bù trừ = 0, không mô hình truy thu kiểu 2022 (>270 tỷ) | Thêm dòng **STRESS ngoài mô hình**: truy thu 270 tỷ trước thuế × 0,8 = **−4.623 đ/cp** trên kịch bản xấu ⇒ 33.803 (trước CK). Không đưa vào trọng số: chiều sự kiện 2026 là nộp THỪA (ngược 2022), không có văn bản nào báo truy thu mới; trigger = HARD ABANDON (§9) | (b) | 0 trên tâm; stress −4.623 đ/cp |
| 3 | Ứng trước chỉ trừ phần giá vốn (51,5) thay vì đủ 76,9 (+540 đ/cp) | Trừ **đủ 76,938** [Q3 p3] | (a) | gộp vào #4 |
| 4 | VLĐ + ứng trước trừ ngay tại 30/9 thay vì khi đóng mỏ (≈ −4%) | Thống nhất quy ước: số dư quay vòng 144,0 tỷ (ứng trước 76,938 + WC ròng 67,06 [Q3 p2-3]) tất toán khi từng mỏ đóng theo tỷ trọng, PV @13,5%. Thuế phải nộp 61,75 và quỹ KTPL 107,47 + trích tạm 35,93 vẫn trừ ngay | (a) | **+4,0%** (quy ước r3 = độ nhạy −3,8%) |
| 5 | Ký quỹ vượt dự phòng 22,66 tỷ có thể sai chiều (ký quỹ thường = chi phí hoàn nguyên được duyệt) | Không tìm được phương án cải tạo PHMT được duyệt để đối chiếu ⇒ giữ base theo BS [Q3 p16, p21]; ghi độ nhạy | (c) | Nếu = 0: **−65 đ/cp** (<0,2%) |
| 6 | Trữ lượng TP1/TC1 sau 2038 = 0 dù có tiền lệ Soklu gia hạn (+8,7%) | **Phần lớn được giải bằng nguồn sơ cấp**: hạn GP thật TP1 31/7/2042, TC1 01/01/2039 [BCTN p8]. Còn lại khi hết GP (tính): TP1 ~7,9 · TT2 ~3,8 · TC1 ~3,1 tr m³ ⇒ gia hạn tới hết trữ lượng chỉ vào kịch bản tốt (chưa có văn bản; BCTN p41: đang làm thủ tục huy động 44,3 ha TC1) | (a)+(b) | Hạn GP BCTN vs BVSC: **+3,5%**. Gia hạn 3 mỏ tới hết trữ lượng trên cơ sở: +6,3% |
| 7 | Báo độ nhạy trọng số gia hạn 25% → 50% | Đã chạy: trọng số kịch bản tốt 50% (xấu 0,25 / cơ sở 0,25 / tốt 0,50) | (b) | **+5,8%** |
| 8 | Dư bù trừ 97,6 tỷ tính 0 (tối đa +802 đ/cp) | Đời mỏ dài hơn ⇒ dư còn **71,5 tỷ**. NĐ 193/2025 Đ139 k8 chỉ nói "bù trừ kỳ sau" — không có cơ sở hoàn tiền ⇒ base 0 | (c) | Nếu được hoàn: **+494 đ/cp** |
| 9 | **Thiếu hạng mục 1 — BCTC kiểm toán FY2025** | **Đã tải** (cafef, bản có chữ ký số). Ý kiến A&C **chấp nhận toàn phần**, không nhấn mạnh [KT25 p7-8]; không sự kiện sau kỳ [KT25 p39]; LNST 301,437 khớp NQ ĐHĐCĐ. Thuyết minh tiền cấp quyền: khoản nộp thừa 343,93 được Thuế xác định 29/5/2026 — SAU ngày ký kiểm toán (20/3/2026) nên không có trong BCTC 2025; soát xét H1/26 chấp nhận toàn phần [H1 p7]. BCTC 2025 là bản scan, rev4 chỉ đọc các trang 3–8, 11–12, 38 | (a) | `audited_fy_missing`: true → **false** |
| 10 | **Thiếu hạng mục 2 — số hiệu/bản gốc giấy phép** (chỉ có bảng BVSC) | BCTN 2025 [BCTN p8] — công ty tự công bố — có **số GP + ngày cấp + hạn + trữ lượng 31/12/2025** cho cả 5 mỏ: TP1 GP 1048/GP-UBND 11/04/2016; TT2 GP 1362/GP-UBND 28/05/2015; TC1 GP 661/QĐ-UBND 28/02/2018; SK2 GP 31/GP-UBND 28/02/2025; SK5 GP 30/GP-UBND 28/02/2025. Bản quét GP của UBND vẫn không có. Cột "thời gian còn lại" của BCTN lệch +1 năm so với chính ngày hạn ⇒ dùng ngày hạn (thận trọng). BCTN cũng ghi "điều chỉnh giấy phép khai thác tại TC1, TP1, TT2 … bổ sung khai thác đất, đá phong hóa" [BCTN p36] ⇒ có thể là lý do bảng BVSC khác | (a) | xem #6. Phần dư rủi ro: bản quét GP chưa đọc (c), ±1 năm hạn 3 mỏ chính ≈ ±3% cơ sở (ước lượng theo cầu nối #6) |
| 11 | **Thiếu hạng mục 3 — NQ HĐQT 12 tháng về đầu tư/đền bù** | Đọc đủ NQ trong 12 tháng (danh sách CBTT cafef): HĐQT 30/10/2025 + 17/11/2025 (điều chỉnh cổ tức 2025 lên 30%), ĐHĐCĐ BT 09/12/2025 (thông qua cổ tức), HĐQT 16/01/2026 (KH SXKD 2026). **Không có cam kết đầu tư/đền bù.** BCTN 2025 [BCTN p41]: thủ tục huy động 44,3 ha TC1, xin mở rộng 20 ha Soklu — chưa có số vốn ⇒ V4 NPV = 0 | (a) | 0 |
| 12 | DTTC/thu nhập khác FY25 lấy từ BVSC; op 9T/25 ước lượng | DTTC 30,655 / LN khác 15,031 nay từ [KT25 p13]. Op 9T/25 vẫn ước lượng (DTTC 9T/25 ≈ 70% cả năm) — ảnh hưởng chỉ lên mức TTM năm 1 | (a)/(c) | Lõi FY25 264,8 → 265,05 |
| 13 | Trữ lượng mốc "hết 2023" + Soklu mốc giả định | Thay bằng trữ lượng **31/12/2025** [BCTN p8] (cộng 84,424 tr m³) | (a) | +0,7% (bước A cầu nối) |

**Thông tin mới không do skeptic hỏi:** KH 2026 của HĐQT: LNTT **275 tỷ**, SX/tiêu thụ 6,8 tr m³ [HĐQT 16/01/26]; BCTN ghi 280 tỷ [BCTN p40].
Không dùng làm neo: KH 2025 là ~175 tỷ LNTT và thực hiện đạt 215,42% [BCTN p37]; LNTT 9T/26 không gồm khoản 343,93 đã là 363,7 tỷ [Q3 p5].

## 2. Net cash 30/9/2026

- Phần trừ ngay: 812,584 (tiền 27,576 + HTM 785,008) − quỹ KTPL 107,466 − thuế phải nộp 61,748 − trích quỹ tạm 9T 35,93 = **607,44 tỷ** [Q3 p2-3, p22].
- Số dư quay vòng tất toán khi đóng mỏ: ứng trước 76,938 + WC ròng 67,06 = **144,0 tỷ**; PV ≈ 32,7 tỷ (cơ sở) ⇒ net cash hiệu dụng **574,7 tỷ**
  (r3: 488,84 trừ ngay).
- Không vay. 20,5 tỷ HTM cầm cố bảo lãnh [Q3 p15], tính đủ. Đã gồm cổ tức tạm ứng 2026 2.500 đ/cp (≈116,8 tỷ, trả 17/12/2026).

## 3. Khoản bù trừ 329,36 tỷ (giữ r3)

Ghi thu nhập khác Q2/26 theo TB Thuế TP Đồng Nai 29/5 và 02/6/2026 [Q3 p19 V.17, p24 VI.6]; số dư 30/9 329,36; tốc độ cấn trừ 19,42 tỷ/năm.
Chỉ cấn trừ khi 3 mỏ TC1/TP1/TT2 còn GP; PV @7,4% = **159,9 tỷ** (cơ sở; r3 150,2), dư khi hết đời **71,5 tỷ** (tính 0).

## 4. Giấy phép, trữ lượng, đời mỏ — nguồn sơ cấp [BCTN p8]

| Mỏ | Số GP | Hạn GP | Công suất (tr m³/năm) | Trữ lượng 31/12/2025 (tr m³) | Khai thác ng.khối/năm (ước lượng) | Đời từ 30/9/26 | Dư khi hết GP (tính) | Tỷ trọng LN |
|---|---|---|---|---|---|---|---|---|
| Tân Cang 1 | 661/QĐ-UBND 28/02/2018 | 01/01/2039 | 1,5 | 22,571743 | 1,500 | **12,25** (hạn) | 3,07 | 32,0% |
| Thạnh Phú 1 | 1048/GP-UBND 11/04/2016 | 31/7/2042 | 1,8 | 35,407949 | 1,659 | **15,83** (hạn) | 7,89 | 30,3% |
| Thiện Tân 2 | 1362/GP-UBND 28/05/2015 | 30/6/2038 | 1,5 | 22,527367 | 1,500 | **11,75** (hạn) | 3,78 | 29,0% |
| Soklu 2 | 31/GP-UBND 28/02/2025 | 28/11/2031 | 0,4 | 2,303277 | 0,212 | **5,16** (hạn) | 1,05 | 3,9% |
| Soklu 5 | 30/GP-UBND 28/02/2025 | 28/08/2029 | 0,5 | 1,613878 | 0,265 | **2,91** (hạn) | 0,65 | 4,8% |

- Hạn GP ràng buộc ở cả 5 mỏ. **Đời bình quân theo tỷ trọng LN: 12,46 năm** (r3: 11,2). Tỷ trọng LN theo sản lượng 2025 [FP p4, p6] (ước lượng).
- Khác bảng BVSC [BV26 p7]: TP1 +4,6 năm, TC1 +1 năm, TT2 −3,2 năm. Chọn BCTN vì là công bố sơ cấp có số GP; BVSC là bảng tổng hợp thứ cấp.

## 5. 5F — tái dùng tag 2026-06-05 (<12 tháng)

NARROW / LOCATION, ROIC_Min5Y 22,6% (`data/moat_tags.csv`). Kiểm nhanh: đồng hồ cắt hào nay có ngày theo GP gốc (TT2 6/2038, TC1 1/2039,
TP1 7/2042); 32 mỏ Đồng Nai, công suất thiết kế 22 tr m³/năm [BCTN p16] — VLB ~5,7 tr m³ nguyên khối ≈ 26% ⇒ không đổi tầng.
Mô hình không có tham số moat, không terminal.

## 6. Định giá (MÙ giá) — `model/dcf_vlb_r4.py`

**V1 — r:** 13,5% tại neo; lãi huy động 12T hiệu dụng **7,4%** (cctg_12m 02/11; Big-4 6,8%; `deposit_rate_vn` last_update 16/11, đọc lại 23/11)
= mức tại neo ⇒ Δ = 0, r **13,5%**, β = 1.

| Lãi huy động | −100bp | −50bp | +50bp | +100bp |
|---|---|---|---|---|
| Tâm trước CK (β1) | 50.810 (+3,4%) | 49.949 (+1,7%) | 48.330 (−1,6%) | 47.569 (−3,2%) |
| β 0,5 | 49.949 (+1,7%) | 49.532 (+0,8%) | 48.723 (−0,8%) | 48.330 (−1,6%) |

Dải Ke nội địa (D4, báo kèm): 12,3% ⇒ 51.164 (+4,2%); 13,4% ⇒ 49.285 (+0,3%).

**Kịch bản** (trọng số giữ r1–r3, không re-tune). Dòng tiền = LN lõi × (1 − 14,84% quỹ) × tỷ trọng mỏ còn hoạt động; không terminal; thuế 20% đã trong LN.

| Kịch bản | w | Đường LN lõi (tỷ, sau thuế) | Đời mỏ | Bù trừ | PV vận hành | PV bù trừ | Ký quỹ | Net cash hiệu dụng | **đ/cp (30/9, trước CK)** |
|---|---|---|---|---|---|---|---|---|---|
| Xấu | 0,25 | 250 phẳng | theo GP BCTN | 0 (đảo chiều) | 1.217,6 | 0 | 3,1 | 574,7 | **38.426** |
| Cơ sở | 0,50 | 357,4 → 321,4 → 285,5 → 265,05×1,02^t | theo GP BCTN | có | 1.546,8 | 159,9 | 3,1 | 574,7 | **48.895** |
| Tốt | 0,25 | 357,4 × 1,02^t | gia hạn 3 mỏ chính tới hết trữ lượng | có | 2.053,2 | 179,1 | 1,7 | 582,1 | **60.276** |
| **Tâm kỳ vọng** | | | | | | | | | **49.123** |

**V3 — Thanh khoản** (sau khoá; giữ r3, `model/px_vlb.csv`): ADV trung vị 250 phiên 1,14 tỷ (68 phiên 0,92); σ 1,34%; spread CS 0,35%;
d(1 tỷ) **1,43%** · d(5 tỷ, tham chiếu) **2,98%**; thoát 5 tỷ ở 20% ADV mất 21,8 phiên. Free float thực ≈ 18,9% (Dofico 49,08%, KSB 21,95%, Hóa An 10,05% [Q3 p22]).

| Sau CK Q = 5 tỷ | Xấu | Cơ sở | Tốt | **Tâm** |
|---|---|---|---|---|
| Cơ sở 30/9/2026 | 37.283 | 47.440 | 58.483 | **47.661** |
| **Ex-div (−2.500, so với giá/ghi sổ)** | **34.783** | **44.940** | **55.983** | **45.161** |

**Độ nhạy khác** (tâm trước CK 49.123; cơ sở 48.895):
- Bù trừ chiết khấu @13,5%: −1,5%. Quỹ 12,4%: +2,0%.
- Đường LN cơ sở: phẳng 265 g0 −11,2%; mid = lõi FY24 −15,7%; giữ TTM +15,4%; fade 1 năm −1,2%; fade 4 năm +2,1%.
- Gia hạn 3 mỏ chính tới hết trữ lượng (trên cơ sở): +6,3%. Hạn GP theo bảng BVSC (r3): −2,7%.
- Trọng số kịch bản tốt 50%: +5,8%.
- Quy ước VLĐ r3 (trừ ngay): −3,8%.
- Dư bù trừ được hoàn: +494 đ/cp. Ký quỹ vượt dự phòng = 0: −65 đ/cp.
- STRESS ngoài mô hình: truy thu kiểu 2022 −4.623 đ/cp trên kịch bản xấu (HARD ABANDON).

**V6 (chỉ hiển thị):** V_ngắn (Gordon vô hạn, LN năm 1 357,4, g 2%, tái đầu tư 5%, + net cash 607,4) = 66.811; V_dài (hữu hạn, cơ sở) = 48.895;
D = 0,312 < ln2 ⇒ không cờ. V_ngắn cao hơn vì Gordon ngầm giả định mỏ vô hạn và LN đỉnh chu kỳ. Dòng C4/D2: không tính ("chưa qua tiêu chí khoá trước, chỉ theo dõi").

**V4:** không có dự án tăng trưởng có số vốn (§1 #11) ⇒ không cần NPV = 0. Capex tuân thủ = hoàn nguyên môi trường: dự phòng 16,22 tỷ đã trích; phần ký quỹ thừa xem §1 #5.

**V5:** 5F tái dùng (<12 tháng), §5.

## 7. Hạng mục không kiểm chứng được (ghi thẳng)

1. **Bản quét giấy phép của UBND**: không có; số GP/ngày/hạn lấy từ BCTN 2025 công ty công bố. Ảnh hưởng ước lượng ±1 năm hạn 3 mỏ chính ≈ ±3% cơ sở.
2. **Quyết định phê duyệt tiền cấp quyền** (nghĩa vụ còn lại, nghĩa vụ mới nếu gia hạn/cấp lại trữ lượng): không có. Kịch bản xấu = 0; truy thu = stress.
3. **Dư bù trừ 71,5 tỷ có được hoàn hay không**: +494 đ/cp nếu được hoàn; base 0.
4. **Phương án cải tạo PHMT được duyệt** (để biết ký quỹ = chi phí hoàn nguyên hay thừa): ±65 đ/cp.
5. **Biên LN từng mỏ**: chưa có; LN chia theo sản lượng 2025.
6. **Op 9T/25** (cho mức TTM năm 1): ước lượng; chỉ tác động năm 1–2 của đường cơ sở.
7. **Toàn văn thuyết minh BCTC 2025** (bản scan 39 trang): đã đọc ý kiến kiểm toán, BCĐKT phần vốn, KQKD, sự kiện sau kỳ; chưa đọc từng thuyết minh.

## 8. Pha SAU KHOÁ — so giá

- Giá tham chiếu **48.100 đ** (20/11/2026, đã không hưởng cổ tức 2.500 đ từ 19/11; lấy từ entry sổ rev3, không truy vấn mới). Ghi chú: meta trang cafef
  hiện 48.600 (chiều 23/11) — thấy ngẫu nhiên khi tải tài liệu, không phải nguồn DNSE, không dùng làm price_ref.
- **Giá/tâm ex-div = 48.100 / 45.161 = 1,07** ⇒ giá TRÊN tâm 6,5%, trong vùng ±15% (38.387–51.935); trên cơ sở 44.940, dưới cận tốt 55.983.
- **Nhãn:** "Trong vùng hợp lý, nghiêng đắt nhẹ". Giá hàm ý LN giữ cao hơn mức giữa chu kỳ lâu hơn 2 năm, hoặc có gia hạn GP.
- **Không đủ điều kiện vào sleeve:** ngưỡng 0,85 × tâm = **38.387 đ**.
- **Sizing V8:** chuẩn 2–4% NAV/mã; thanh khoản trói: 5 tỷ cần ~22 phiên ở 20% ADV. Đề xuất >5 tỷ cần user duyệt riêng. Hiện không đề xuất vào.

## 9. Mốc khoá trước + điều kiện đổi nhận định (CẢ HAI chiều) — khoá 23/11/2026 (rev4)

| Mốc | Ngày chấm | Ngưỡng |
|---|---|---|
| M1 BCTC Q4/2026 | ~20/01/2027 | Sản lượng đá Q4 ≥ 1,85 tr m³ **và** DT/m³ ≥ 215.000 đ (kiểm tra năm 1 của đường LN: lõi TTM ≥ 340) |
| M2 Thuyết minh tiền cấp quyền | ~20/01/2027 | Cấn trừ ~4–6 tỷ/quý; không TB phải nộp bổ sung |
| M3 BCTC kiểm toán 2026 | ~31/03/2027 | Chấp nhận toàn phần; không ngoại trừ/nhấn mạnh về 343,93 tỷ |
| M4 Văn bản gia hạn/điều chỉnh GP TT2/TC1 (hạn 6/2038, 1/2039) | bất kỳ CBTT | Có văn bản ⇒ đánh giá lại đời mỏ |
| M5 BCTC Q2/2027 | ~20/07/2027 | Lõi TTM ≤ 330 ⇒ đường fade đúng hướng; ≥ 357 ⇒ cân nhắc fade 4 năm (+2,1%) |

- **Đổi LÊN:** văn bản gia hạn 3 mỏ tới hết trữ lượng (+6,3% cơ sở); LN lõi giữ ≥ TTM qua 2027 (tới +15,4% cơ sở); dư bù trừ được hoàn (+494 đ/cp); lãi huy động −100bp (+3,4%).
- **Đổi XUỐNG:** TB truy thu/huỷ khoản bù trừ (−3.423 đ/cp cơ sở; HARD ABANDON nếu phải nộp bổ sung); rà soát/thu hồi GP lan sang 3 mỏ chính (HARD ABANDON);
  LN lõi về mức FY24 (−15,7% cơ sở); sản lượng Q4 < 1,6 tr m³; ý kiến kiểm toán có ngoại trừ (HARD ABANDON); lãi huy động +100bp (−3,2%).

## 10. Pháp lý / quản trị — chỉ WARNING

- ⚠️ Tiền cấp quyền: tiền lệ đảo chiều 2022 (nộp bổ sung) ↔ 2026 (nộp thừa).
- ⚠️ Thanh tra CP ⇒ rà soát GP Soklu. SK2/SK5 đã được cấp GP mới 28/02/2025 (GP 31, 30/GP-UBND) [BCTN p8].
- ⚠️ Kiểm toán NN kiến nghị xử lý đất sử dụng sai mục đích (báo chí 11/2025).
- BCTN 2025: đền bù diện tích còn lại gặp khó (chủ đất chưa đồng ý giá) — chưa có số [BCTN p36].
- Không giao dịch bán hàng với bên liên quan [Q3 p23]. Không đưa vào base.

## 11. Cho Mike ghi sổ

`LEDGER_PROPOSAL_VLB.json` (cùng thư mục): tâm **45.161** (ex-div, sau CK); vùng **34.783–55.983**; center_alt (cơ sở) **44.940**;
`audited_fy_missing = false`; `skeptic_final` theo kết quả skeptic r3 (không tự nâng nhãn).
