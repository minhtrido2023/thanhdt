# DD VCP — REV 4 (CTCP Xây dựng và Năng lượng VCP, UPCoM) · dd_date 2026-11-12 · rev4 23/11/2026 · job `Taylor_20261123_100924`

> NGHIÊN CỨU READ-ONLY. Không khuyến nghị, không đặt lệnh, không email. User quyết.
> Bản này THAY `REPORT_rev3b.md` (tâm sau CK 32.605). Phản biện vòng cuối r3 (`skeptic/r3.json`, INCONCLUSIVE medium) — §1 liệt kê xử lý TỪNG hạng mục. Bản cũ giữ nguyên.
> Khoá giả định: `calc_rev4/assumptions_rev4.json` + `calc_rev4/model_rev4.py` (md5 ở Phụ lục A, `calc_rev4/LOCK_prerun_rev4.txt`). Thay đổi rev4 CHỈ dựa trên nguồn mới; không truy vấn giá mới. Giá/ADV pha sau khoá đọc lại từ `calc_rev3/px_vcp_post_lock.csv` (giá đã xuất hiện trong rev3b — ghi minh bạch).
> Nguồn mới rev4 (`src_rev4/`, md5 `src_rev4/MD5.txt`, tải vcpholdings.com.vn 23/11/2026): **[BCTN20]** `10-baocaothuongniennam2020_9384.pdf` (scan) · **[BCTN21]** `bctn-vcp-2021-final_7248.pdf` · **[BCTN22]** `bao-cao-thuong-nien-nam-2022_3956.pdf` (scan) · **[BCTN24]** `bctn_2024_vn.pdf` · **[NQ26]** `nq_dhdcd_2026_vn.pdf` (md5 `b42fdb87c09eaec67f0852d4b72025c0`) · **[TL26]** `tl_dhdcd_2026_vn.pdf`. Ảnh trang đọc: `img4/`. Nguồn cũ giữ như rev3b: [KT25] [H1] [Q3] [BCTN23] [BCTN25] [BQ].

## 0. Kết luận

**Tâm 30.805 đ/cp trước chiết khấu thanh khoản; 29.686 đ/cp sau chiết khấu (vị thế 1 tỷ, 3,63%).**
**Vùng [18.398 ; 46.990]** trước CK = bear/bull; **sau CK [17.729 ; 45.282]**. r = 13,5%, terminal RONIC = Ke.

| | Rev2 (12/11) | Rev3b (23/11, skeptic r3) | **Rev4 (23/11)** |
|---|---|---|---|
| Tâm trước / sau CK | 41.560 / 40.273 | 33.837 / 32.605 | **30.805 / 29.686** (−9,0% so với rev3b sau CK) |
| Bear / Base / Bull (trước CK) | 21.669 / 40.475 / 67.385 | 21.832 / 34.532 / 46.990 | **18.398 / 30.085 / 46.990** |
| k thuỷ văn bình thường (× Etb) | không chuẩn hoá | 1,127 | **1,0 (Etb)** |
| N base (LNST mẹ, tỷ) | 441,5 | 332,8 | **282,5** |

**Giá 37.400 (đóng cửa 20/11/2026) = +26,0% so với tâm sau CK** ⇒ **TRONG VÙNG, TRÊN TÂM — không có biên an toàn** (0,85 × tâm = 25.233).
Sizing V8 (chuẩn 2–4% NAV/mã): **không đề xuất vị thế ở giá hiện tại**; thanh khoản nền (ADV60 trung vị 0,37 tỷ/phiên) giới hạn vị thế thực tế ≲ 0,3 tỷ.

**Thay đổi duy nhất làm dịch tâm: k = 1,127 → 1,0 (Etb)**, có cơ sở độc lập ba lớp (§2): Etb thiết kế; kế hoạch của chính công ty ở năm không đi sau năm ướt ≈ Etb (KH2020 Cửa Đạt 1,00; KH2022 0,963; KH2025 ≈0,99); chuỗi đo 6 năm 2020–2025 cho trung bình 1,009 (kể 2020) … 1,061 (2021–25). Các hạng mục khác của r3 được xác minh từ nguồn gốc là KHÔNG làm đổi base (bảo lãnh Đak Lô = nợ đã hợp nhất; NQ ĐHĐCĐ 2026 không có phát hành; thuế/phí tài nguyên đã trong chi phí).

**Rủi ro số 1 vẫn là phân bổ vốn** (cho vay cá nhân 823,4 tỷ 30/06/2026; ~1.000 tỷ góp vốn 9T/26 chưa thuyết minh; 46,8% cp VCP cầm cố cho trái phiếu). Pháp lý chỉ WARNING.

## 1. Đính chính so với rev trước — từng hạng mục skeptic r3

Loại: (a) định lượng có nguồn độc lập ⇒ base · (b) kịch bản/độ nhạy · (c) không kiểm chứng được + ảnh hưởng ước lượng.

| # | Hạng mục r3 | Xử lý rev4 | Loại | Tác động tâm (trước CK, so với 30.805) |
|---|---|---|---|---|
| 1 | **k = 1,127 thay vì Etb** (killer; bỏ qua KH2025 ≈0,99 Etb) | **Base k = 1,0.** Dựng chuỗi đo từ BCTN gốc: 2020 Cửa Đạt **311,609 tr kWh = 0,747 × Etb** ("thấp nhất kể từ khi phát điện", BCTN20 tr.13) · 2021 **614,817 / 712,9 = 0,862** (BCTN21 bảng SL) · 2022 **863,691 / 712,9 = 1,2115** (BCTN22 tr.16 — sửa số 1,264 rev3b suy từ chữ "70%") · 2023 0,8845 (BCTN23) · 2024 **(779 − NSX 22,614 − Đak Robaye 24,367)/712,9 = 1,027** (BCTN24; thay ước lượng 1,039) · 2025 1,320. KH công ty: 2020 Cửa Đạt 417,6 (=311,609/74,62%) = Etb; 2022 686,4 = 0,963; 2025 ≈0,99. KH2026 1,15 lập sau năm ướt | (a) | rev3b→rev4 −3.032 đ; độ nhạy k 1,061 (đo 2021–25) / 1,127 / 1,15: **32.412 / 34.142 / 34.749** |
| 2 | ΔB 427,9 cộng đủ giá sổ trong khi bull loại biên phế liệu Q3 + lãi dồn tích | Giữ ΔB theo giá sổ: ΔB là TÀI SẢN (stock) — LN một lần đã ghi nhận vẫn là vốn chủ thật; lãi dồn tích là khoản phải thu (rủi ro thu hồi nằm ở bear). Bull loại chúng khỏi N vì N là DÒNG lặp lại — hai phép không mâu thuẫn. Hiển thị độ nhạy trừ cả 132,7 tỷ khỏi ΔB ở base/bear | (b) | **29.617 (−3,9%)** |
| 3 | Hạn PPA + giá sau trả nợ Cửa Đạt | **Vẫn không kiểm chứng được** (HĐ 06/2012HĐ-NMĐ-Cửa Đạt + PL 11 không công bố hạn/giá). Bổ sung bằng chứng đo: Cửa Đạt CHÀO GIÁ thị trường điện (BCTN21: "chủ động bám sát thị trường và đưa ra phương án chào giá tối ưu"; BCTN23: giá thị trường giảm) — giá bình quân đo được **702 (2020) · 873 (2021) · 829 (2023) · 725,5 (2025) đ/kWh** ⇒ Pc 2025 trong base đã ở vùng thấp của chuỗi. Độ nhạy Pc −20% (ước lượng) giữ | (c) | từ năm 0 / 5: **26.551 (−13,8%) / 28.546 (−7,3%)** |
| 4 | **Bảo lãnh vay + hỗ trợ tài chính Đak Lô 1-3** (NQ HĐQT 05/2025, 11/2025) | Đak Lô 1-3 là **công ty con 99,27%** (VĐL 500 tỷ, BCTN25 tr.16 "Công ty con") ⇒ hợp nhất. Khoản vay dự án nằm trong **vay dài hạn HỢP NHẤT** [KT25 Phụ lục 04: dòng (9) VCB CN Bắc Hà Nội 192 tháng tài trợ dự án Đak Lô 1 / Đak Lô 3; dòng (12) MB CN Điện Biên Phủ]. Bảo lãnh của mẹ cho con hợp nhất KHÔNG tạo nghĩa vụ tăng thêm ở cấp hợp nhất ⇒ base 0. Dự án tăng trưởng NPV0 (V4a); không có tín hiệu rủi ro cụ thể (khởi công 03/2025, BCTN25 KH phát điện Q1/2027, Q2/2028) ⇒ không vào kịch bản. Hiển thị độ nhạy: vượt dự toán 20% TMĐT 1.213 × 99,27% = 240,8 tỷ mất trắng | (a)+(b) | base 0; độ nhạy **28.650 (−7,0%)** |
| 5 | **NQ ĐHĐCĐ 2026 chưa đọc** | Đã tải + đọc: **NQ 01/2026/NQ-ĐHĐCĐ ngày 11/5/2026**, thông qua 100%, 10 điều: báo cáo HĐQT/BKS/TV độc lập, BCTC 2025 kiểm toán, uỷ quyền chọn kiểm toán 2026, phân phối LN 2025 (TTr 02/2026), thù lao 2026, báo cáo sử dụng vốn trái phiếu tới 31/12/2025. Chương trình họp [TL26 tr.4–5] có 9 nội dung, **không có phát hành cổ phiếu, ESOP, cổ tức cổ phiếu, trần vay/bảo lãnh hay danh mục đầu tư mới**. ⇒ số cp 83.789.658 giữ nguyên. Lưu ý: link "NQ và BB ĐHĐCĐ 2026" trên web công ty trỏ nhầm file 2025 (`nq_bb_dhdcd_2026.pdf` = NQ 01/2025); file đúng là `VCP-NQ-DHDCD-TN-2026 Tieng Viet-.pdf` | (a) | 0 |
| 6 | **Tiền cấp quyền khai thác tài nguyên nước / giấy phép** | Các khoản thu theo sản lượng **đã hạch toán chi phí hằng năm ⇒ nằm trong N_2025**: thuế tài nguyên phải nộp trong năm 2025 **107,887 tỷ**, đã nộp 103,250 [KT25 Phụ lục 05], "(*) tính căn cứ trên sản lượng điện" [BCTN23 PL05]; phí DVMTR + thuế tài nguyên nước là khoản phải trả định kỳ [BCTN23 TM20]. Phần chuẩn hoá thuỷ văn (chi phí biên 14,6%) đã trừ theo sản lượng. **Tiền cấp quyền khai thác TNN không trình bày riêng; truy thu (nếu có) và thời hạn giấy phép các nhà máy đang chạy: KHÔNG kiểm chứng được.** Thời hạn dự án 50 năm (Đak Lô 1/3, KT25 TM12; Thác Ba, Đak Robaye, Đak Lô 4, BCTN23) | (a)+(c) | ≈0; truy thu không ước được (ước lượng < 1 năm thuế tài nguyên ≈ 107,9 tỷ ⇒ < −1.290 đ nếu xảy ra) |
| 7 | Pool ~1.000 tỷ góp vốn 9T/26 chưa thuyết minh | **Không kiểm chứng được** — Q3/26 chưa soát xét không thuyết minh; trang "Quyết định HĐQT" trên web không có văn bản 2026 liên quan. Giữ: base giá sổ (V4a), bear lỗ 50% | (c) | độ nhạy lỗ bear 0% / 100%: **32.595 / 29.015** |
| 8 | (phía rẻ) Bear chồng 3 cú sốc; bear N còn lãi cho vay của khoản coi là lỗ | Giữ cấu trúc bear (đã thông báo, trọng số 0,30). Hai lực ngược chiều (chồng sốc ⇒ thấp; còn lãi ⇒ cao), không có cơ sở định lượng riêng ⇒ không sửa; độ nhạy lỗ cho vay 0/100% hiển thị | (b) | 32.244 / 29.366 |
| 9 | (phía rẻ) Đak Lô/Thác Ba NPV0 | Luật user V4a — giữ | — | 0 |

Hạng mục r1/r2 (rev3b §1a–1b) giữ nguyên xử lý; không có nguồn mới đảo các hạng mục đó.

## 2. Chuẩn hoá thuỷ văn (rev4)

| Năm | Sản lượng (tr kWh) | Phạm vi | TH/Etb | Nguồn |
|---|---|---|---|---|
| 2020 | 311,609 | chỉ Cửa Đạt (Etb 417) | 0,747 (thấp kỷ lục) | BCTN20 tr.13 |
| 2021 | 614,817 | 6 nhà máy (Etb 712,9) | 0,862 | BCTN21 |
| 2022 | 863,691 | 6 nhà máy | 1,2115 | BCTN22 tr.16 |
| 2023 | 630,58 | 6 nhà máy (El Niño) | 0,8845 | BCTN23 tr.18 |
| 2024 | 779 − 22,614 − 24,367 = 732,0 | 6 nhà máy (bỏ NSX, Đak Robaye vào giữa năm) | 1,027 | BCTN24 |
| 2025 | 988,0 | thuỷ điện (Etb 748,3) | 1,320 | BCTN25 tr.34–36 |

- Trung bình 2021–25 = **1,061**; 6 năm kể 2020 (Cửa Đạt đại diện) = **1,009**. Cửa Đạt dao động mạnh hơn hệ thống nên dùng nó cho 2020 kéo xuống — vì vậy hai con số là CẬN của trung bình dài hạn, Etb (1,0) nằm ở cận dưới.
- Kế hoạch công ty (độc lập với chọn lựa của tôi): KH2020 Cửa Đạt = Etb; KH2022 = 0,963; KH2025 ≈ 0,99; chỉ KH2026 = 1,15 (sau năm ướt 2025).
- BCTN23 tr.18: lưu lượng về hồ Cửa Đạt 2023 ≈ 65% trung bình nhiều năm, SL Cửa Đạt 2023 = 367,4 = 0,881 × Etb ⇒ ở lưu lượng trung bình SL Cửa Đạt có thể > Etb (quan hệ phi tuyến, xả tràn, ưu tiên thuỷ lợi) — điểm này nghiêng lên, nên k = 1,061 được giữ làm độ nhạy phía trên (+5,2%).
- **Chọn base k = 1,0 (Etb)**: là chuẩn thiết kế công bố, khớp kế hoạch công ty ở năm bình thường, và nằm trong khoảng đo [1,009 ; 1,061]. Phần thuỷ văn vượt 2025 = **−139,5 tỷ LNST mẹ**.
- **N base = (441,46 − 139,5) × 0,9532 (thuế KH2026 15,3%) × 0,9816 (KT-PL) = 282,5 tỷ.** Kiểm chéo: N 2024 (năm ≈1,03 × Etb) = 306,5 [BQ/KT25] trước thuế-bước 2026 và KT-PL.
- Bảng nhà máy (Etb, DT/kWh, thuế, sở hữu) giữ như rev3b §2.

## 3–7. Bảng cân đối, dòng tiền, thuỷ điện, cổ đông, ngành, pháp lý

Giữ §3–§7 rev3b/rev2. Bổ sung rev4: số cp 83.789.658 xác nhận qua NQ ĐHĐCĐ 2026 (không phát hành); nợ dự án Đak Lô 1-3 nằm trong vay hợp nhất [KT25 PL04]; thuế tài nguyên 2025 107,887 tỷ đã trong chi phí [KT25 PL05]. Pháp lý: chỉ WARNING, không vào base.

## 8. Định giá — mù giá thị trường

**Công thức:** V = N / r (+ ΔB ở base/bear). N/r = giá trị tài sản cuối 2025 với terminal RONIC = Ke (D4). ΔB = 427,9 tỷ tài sản/dự án 2026 theo giá sổ (V4a NPV0). r = 13,5% (V1: lãi huy động 12T hiệu dụng 7,40% ngày 23/11/2026 = CCTG 12M 02/11, bằng điểm neo 03/11 ⇒ Δ = 0; β = 1 giả định). g không ảnh hưởng vì RONIC = Ke.

| Kịch bản | w | N (tỷ) | Cơ sở | Giá trị (tỷ) | đ/cp |
|---|---|---|---|---|---|
| Bear | 0,30 | 282,5 | Base − PV El Niño 2 năm (46,7 tỷ/năm = SL từ 1,0 xuống 0,8845 × Etb; PV 77,3) − lỗ cho vay 50% × 803,7 = 401,9 [H1 PL01] − lỗ 50% pool 1.000 chưa thuyết minh = 500 | 1.541,5 | **18.398** |
| Base | 0,45 | **282,5** | §2: 2025 chuẩn hoá về Etb, thuế KH2026, KT-PL; + ΔB 427,9 | 2.520,8 | **30.085** |
| Bull | 0,25 | 531,5 | (TTM Q3/26 700,8 − biên phế liệu vượt thường 74,9 − lãi dồn tích chưa thu 57,8) × thuế KH2026 × KT-PL; không chuẩn hoá thuỷ văn; không cộng ΔB | 3.937,3 | **46.990** |
| **Tâm** | | | Trọng số 0,30/0,45/0,25 giữ rev2 (**ước lượng**) | | **30.805** |

Output: `calc_rev4/model_out_rev4.json`.

**Độ nhạy tâm (trước CK, đ/cp; % so với 30.805):**

| Biến | Giá trị |
|---|---|
| Lãi huy động −100 / −50 / +50 / +100bp, β=1 | 33.240 (+7,9%) / 31.976 (+3,8%) / 29.718 (−3,5%) / 28.706 (−6,8%) |
| Lãi huy động −100 / −50 / +50 / +100bp, β=0,5 | 31.976 (+3,8%) / 31.379 (+1,9%) / 30.252 (−1,8%) / 29.718 (−3,5%) |
| Ke dải nội địa (D4) 12,3% / 13,4% | 33.774 / 31.032 |
| k = 1,061 (đo 2021–25) / 1,127 (rev3b) / 1,15 (KH2026) / không chuẩn hoá | 32.412 / 34.142 / 34.749 / 39.458 |
| Thuế 20% dài hạn từ năm 0 / 5 / 10 | 29.382 / 30.049 / 30.404 |
| Cửa Đạt Pc −20% từ năm 0 / 5 (ước lượng) | 26.551 / 28.546 |
| NSX nhượng quyền hết sau 20 năm (ước lượng) | 29.610 |
| ΔB trừ 132,7 (phần bull đã loại) | 29.617 |
| Đak Lô 1-3 vượt dự toán 20% mất trắng (ước lượng) | 28.650 |
| Base trừ lãi dồn tích 2025 chưa thu (24,8 tỷ sau thuế) | 29.264 |
| Lỗ cho vay bear 0% / 100% | 32.244 / 29.366 |
| Lỗ pool chưa thuyết minh ở bear 0% / 100% | 32.595 / 29.015 |
| Trọng số 0,35/0,45/0,20 · 0,40/0,40/0,20 · 0,25/0,45/0,30 | 29.375 · 28.791 · 32.235 |
| RONIC = ROE (ngầm thưởng; chỉ hiển thị) | 31.684 |

**V6 — hai nền (chỉ hiển thị, đầu vào rev2):** V_ngắn 37.394 · V_dài (FCFE mẹ 301,3/(r−g)) 31.269 · D = 0,179 < ln2 ⇒ không cờ. C4/D2 như rev3b — "chưa qua tiêu chí khoá trước, chỉ theo dõi".

### Pha SAU KHOÁ — giá và thanh khoản (V3)

`calc_rev4/post_lock_liquidity_rev4.py` trên `calc_rev3/px_vcp_post_lock.csv` (BQ `tav2_bq.ticker` tới 20/11/2026; không truy vấn mới):
- Giá đóng cửa 20/11/2026 **37.400**. Giá trị giao dịch trung vị: 250 phiên 0,273 tỷ, 60 phiên **0,37 tỷ**, 20 phiên 10,32 tỷ (đột biến sau KQ Q3). σ ngày 250 phiên 2,21%.

| Vị thế | Phiên thoát (10% / 20% ADV60) | Chiết khấu σ√(Q/ADV60) | Tâm sau CK | Vùng sau CK |
|---|---|---|---|---|
| **1,0 tỷ** (headline) | 27,0 / 13,5 | **3,63%** | **29.686** | 17.729 – 45.282 |
| 0,3 tỷ | 8,1 / 4,1 | 1,99% | 30.192 | 18.032 – 46.055 |
| 0,1 tỷ | 2,7 / 1,4 | 1,15% | 30.451 | 18.187 – 46.450 |

Nhãn theo giá trị sau CK 1 tỷ: **37.400 = +26,0% trên tâm 29.686; trong vùng [17.729 ; 45.282]; trên 0,85 × tâm = 25.233 ⇒ không có biên an toàn.** Free float, room ngoại: chưa đo.

## 9. Vị thế & lợi thế cạnh tranh (5F) — V5

DD đầy đủ 12/11/2026 (< 12 tháng) ⇒ tái dùng §9 rev2: **moat_tier NARROW (cơ chế giấy phép), định lượng ≈ NONE**; rủi ro số 1 = phân bổ vốn. Kiểm nhanh 23/11: (i) chuỗi 2020–2025 cho thấy biên độ sản lượng 0,75–1,32 × Etb — biên gộp điện cao năm 2025 là thuỷ văn, không phải hào; (ii) Cửa Đạt chào giá thị trường điện ⇒ không có hào về giá bán. Không có tham số moat trong mô hình.

## 10. Điều kiện đổi nhận định (hai chiều)

| Mốc | Nâng | Hạ |
|---|---|---|
| BCTC Q4/2026 (≤ 30/01/2027) | Thuyết minh pool 1.000 tỷ là tài sản sinh lời; LN gộp ngoài điện ≥ 100 tỷ có thuyết minh | Trích lập cho vay / pool; biên ngoài điện ≤ 5% |
| BCTC KT 2026 (≤ 31/03/2027) | Chấp nhận toàn phần; dư nợ cho vay cá nhân ≤ 400 tỷ | Ngoại trừ/nhấn mạnh ⇒ bear thành trung tâm |
| Sản lượng 2026 (BCTN 2026) | ≥ 1,15 × Etb và chuỗi 7 năm ≥ 1,06 ⇒ xét nâng k | ≤ 0,9 × Etb (El Niño) |
| Công bố PPA/giấy phép | Hạn PPA Cửa Đạt dài, giá không cắt | Pc Cửa Đạt giảm; truy thu tiền cấp quyền TNN |
| Lãi huy động 12T | −50bp ⇒ +3,8% | +50bp ⇒ −3,5% |

## Phụ lục A — Khoá và nguồn

- Khoá rev4: `calc_rev4/assumptions_rev4.json` md5 **`1cf0ebd3e759c13e8900fa62a380c755`**, `calc_rev4/model_rev4.py` md5 **`865887c2b475fe52303b5af1d93fbb3d`**, `model_out_rev4.json` `5e162e0494f88fc268b42afdbc867b8c` (`calc_rev4/LOCK_prerun_rev4.txt`, 2026-11-23 17:18 ICT). Chạy `OMP_NUM_THREADS=1 python3 calc_rev4/model_rev4.py`.
- `bin/dd_assumptions_lint.py calc_rev4/assumptions_rev4.json`: rc=0, 32 cảnh báo (file khoá theo định dạng riêng của DD này từ rev3, không theo schema v1; các độ nhạy L4/L5 có trong `model_out_rev4.json` và bảng §8). Chế độ cảnh báo, không chặn.
- Rev3b: `assumptions_rev3b.json` 8d93c85bd812d4841090ca0c80f40dac, `model_rev3b.py` ee7bf53e66855f3bdd3d3fbd57d38ba1. Khác biệt rev4: `hydro.k_base`=1,0, `ratio_history` thay bằng số đo, thêm khối `dak_lo_guarantee`, `water_rights`, `agm_2026`, `cuadat_price_history`, `dB_consistency`.
- Nguồn rev4: `src_rev4/MD5.txt`; ảnh trang `img4/` (b20_p13_top, b22_p16_tbl/tot, nqdh26_p1–2, tl26_p4–5, kt25_pl05, kt25_pl04_mb). Trang KT25 = chỉ số trang PDF.

## Phụ lục B — Còn mở / không kiểm chứng được

1. Bản chất ~1.000 tỷ góp vốn 9T/26 (bear trừ 50%; độ nhạy 32.595–29.015).
2. Hạn PPA Cửa Đạt và giá sau trả nợ (độ nhạy −7,3% … −13,8%; mức cắt 20% là ước lượng).
3. Ngày hết ưu đãi thuế từng nhà máy (−1,3% … −4,6%).
4. Thời hạn nhượng quyền NSX; tiền cấp quyền khai thác TNN (truy thu) và giấy phép các nhà máy đang chạy.
5. Trọng số kịch bản; gán bảng 1/2 BCTN25; SL 2024 từ tổng làm tròn 779 tr kWh (sai số ±0,1%).

## Phụ lục E — Phản biện

r1 (REPORT.md) INCONCLUSIVE · r2 (REPORT_rev3.md) INCONCLUSIVE · r3 (REPORT_rev3b.md, 0,93 USD) INCONCLUSIVE medium — killer k = 1,127. Rev4 xử lý ở §1. Skeptic r4 (vòng 3 của rev mới, vòng CUỐI user duyệt 23/11 17:03): `bin/dd_skeptic_run.py` trên bản này; không sửa báo cáo sau khi skeptic chạy.
