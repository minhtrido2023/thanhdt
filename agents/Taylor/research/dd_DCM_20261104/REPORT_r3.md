# DD — DCM (CTCP – Tổng Công ty Phân bón Dầu khí Cà Mau, PVCFC) · as-of 04/11/2026 · **VÒNG 3 (r3 = r2 + sửa chữ theo skeptic vòng 2, Mike áp; KHÔNG chạy lại mô hình, số định giá = r2)** · job `Taylor_20261104_162755` (r1: `REPORT.md`, giữ nguyên)

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. r2 áp đính chính của fundamental-skeptic (REFUTED mức văn bản/mô hình, tin cậy medium; phần bóc số BCTC đúng).
> **Đã áp / không áp (mỗi điểm đều kiểm lại trên trang BCTC gốc `png/r2q3_*`, render từ `src/DCM_Q3_2026_Hopnhat.pdf`):**
> - **S1 thuế — ÁP.** pdf p21 (tr.17) ghi "Năm 2026 là năm thứ 15 … ưu đãi 10%" (CV 4641/TCT-CS) ⇒ 20% từ 2027 có nguồn gốc. Đóng mục chưa xác minh #1. Δ năm 1 = **−187 đ/cp** (trùng ước lượng skeptic). Bỏ độ nhạy "thuế 10% vĩnh viễn" và điều kiện nâng (c).
> - **S2 quỹ KTPL — ÁP.** pdf p41: tạm trích 136,19 tỷ = 5,97% LNST 9T/26; CĐKT mã 323 (pdf p6): 265,34 tỷ. Trừ cả hai: **−1.316 đ/cp** (skeptic ước −1.289; lệch do làm tròn %).
> - **S3 biên dài hạn — ÁP.** Bảng quét biên + nhãn có điều kiện (§0, §5). Tâm vẫn là 1 số, nêu rõ phụ thuộc lựa chọn biên.
> - **S4 vay khí/tiền phong toả — ÁP (sửa diễn giải; net cash gộp không đổi).** Mâu thuẫn TM24(i) ↔ TM12 đọc lại trên ảnh, đúng như skeptic nêu (§1, §4).
> - **ADMIN — ÁP.** Chuẩn hoá thuế XK theo FY25 (5% × 4.051,6 = 202,6 tỷ) và P 0,55 độc lập mọi nhánh: **+451 đ/cp** (skeptic ước +479).
> - **Chi phí khí — kịch bản HAI CHIỀU theo Brent (ngoài base)** (r3 sửa dấu sai của r2, xem §5); TM38 đọc lại: bên bán khí đổi từ PVN sang PV GAS (§3 mục 3).
> - **WARNING §7 — ÁP đủ.** Không điểm nào kiểm lại thấy sai.
> - Tổng r1→r2 (kỳ vọng): **28.072 → 27.021 (−1.051)**. Skeptic ước tâm 27.100–27.400; r2 thấp hơn 80–380, vì S2 trừ 1.316 thay vì 1.289 và ADMIN +451 thay vì +479 (sai khác nhỏ, chưa khoá được nguyên nhân chi tiết hơn).
> Nguồn: **[BCTC]** = BCTC hợp nhất Q3/2026 (công bố 29/10/2026, Vietstock static2; bảng là ảnh scan, đọc từ `png/q326hn_*`) + Q2/2026, Q1/2026,
> Q4/2025 (cùng nguồn, `src/`); **[KT25]** BCTC HN 2025 kiểm toán (`src/web/`); **[NQ]** Nghị quyết ĐHĐCĐ 996/NQ-PVCFC 22/04/2026; **[BQ]** `tav2_bq`;
> **[Bobby]** `kb/data_registry/market-state/sector_read_phan_dam_ure_20261104.md` (đọc mù); **[CTCK]** = tài liệu môi giới (chỉ dùng số vận hành, KHÔNG dùng giá mục tiêu).
> **Thứ tự chạy, trung thực (r1):** `calc/model.py` không nhận giá/vốn hoá/PE của DCM; khoá md5 lúc **23:12:56 ICT** (`calc/LOCK_md5.txt`), sau đó mới truy vấn giá.
> **Thứ tự chạy, trung thực (r2) — QUAN TRỌNG:** mọi chỉnh sửa r2 (S1–S4, ADMIN, quét biên) làm **SAU khi đã thấy giá 33.000 và nhãn ĐẮT của r1**. Không có "mù giá" thật ở vòng này; tôi chỉ đảm bảo `calc/model_r2.py` không nhận giá làm đầu vào (khoá md5 23:30:41 ICT, `calc/LOCK_r2_md5.txt`) và so giá ở `calc/compare_px_r2.py` chạy sau khoá. Việc mở rộng quét biên (r3: KHÔNG đối xứng — 1 mức dưới tâm, 3 mức trên) (150…260, cả hai phía TB 10 năm), **KHÔNG dùng để dịch tâm theo hướng giá**: tâm vẫn đặt ở biên TB 10 năm = 179 như r1. Nếu có thiên lệch còn lại thì nó nằm ở chỗ skeptic và tôi đều đã biết giá khi chỉnh.
> Brief của Mike không nêu giá DCM. Giả định do tôi tự đặt gắn nhãn **(ước lượng)**.

## 0. Kết luận
- **Giả thuyết "LNST tăng nhờ giá urê/xuất khẩu, không phải khoản một lần": ĐÚNG ở mảng sản xuất, nhưng phần tăng bị bào mòn bởi tài chính và chi phí.**
  - Q3/26 so với Q3/25: LN gộp thuần **+442 tỷ**. Mike ra +592 vì lấy doanh thu gộp, bỏ sót giảm trừ doanh thu 258,1 tỷ.
  - Phần bị ăn mất: CPBH −87, QLDN −47, **tài chính ròng −189** (gồm "chi phí tài chính khác" **71,2 tỷ** mới xuất hiện, chưa giải thích; tỷ giá đảo chiều −106). LNTT còn +123.
- **Q3 giảm mạnh so với Q2 (LNST 1.067 → 432) do biên urê, không do một lần:**
  - LN gộp urê 1.792 → 908 tỷ (−884).
  - Xuất khẩu urê 2.684 → 740 tỷ: mùa thấp điểm, giá bán đi xuống từ đỉnh tháng 4.
  - Bảo dưỡng tổng thể bắt đầu 20/9.
  - QLDN thấp hơn Q2 297 tỷ, đỡ một phần.
- **Bảng cân đối rất khoẻ:** net cash gộp **7.539 tỷ = 14.241 đ/cp** (30/9/2026); **trừ quỹ khen thưởng phúc lợi 265,3 tỷ ⇒ 7.274 tỷ = 13.740 đ/cp**. CFO 9T **+2.331 tỷ**, là tiền thật. Kiểm toán 2025 (Deloitte) **chấp nhận toàn phần**.
- **Định giá r2 (mù giá đầu vào; r 13,5% @ huy động 7,40%; thuế 20% từ 2027; trừ quỹ KTPL):**
  - Kỳ vọng **27.021 đ/cp** = 0,50×CYC 28.017 + 0,30×ADMIN 28.017 + 0,20×STRUCT 23.037. (ADMIN ≡ CYC về số vì xác suất chính sách 0,55 nay áp độc lập cho mọi nhánh.)
  - Lưới 270: P10 24.065 · P25 25.121 · P50 26.745 · P75 28.458 · P90 29.691.
  - Chiết khấu thanh khoản ≈ 0 ở quy mô ≤1% NAV (ADV 74 tỷ) ⇒ giá trị sau chiết khấu thanh khoản vẫn **27.021**.
- **⚠️ Tâm này là một lựa chọn phán đoán về biên dài hạn (S3):** 179 USD/t = TB 10 năm 2016–25 nằm ở **mép dưới** dải bền 180–260 của Bobby (trung vị 10 năm theo tháng của Bobby: 152). Xác suất CYC/ADMIN/STRUCT 0,50/0,30/0,20 của Bobby là cho "2–4 quý tới", không phải trọng số vĩnh viễn; tôi dùng chúng làm trọng số cho trạng thái dài hạn vì không có thứ thay thế đo được, và nói rõ đó là lựa chọn.
  - Giá trị theo biên dài hạn (đ/cp, `calc/model_r2_out.txt` dòng 3): **150 → 24.876 · 179 → 27.009 · 220 → 30.025 · 242 → 31.643 · 260 → 32.967** (kỳ vọng nhánh 0,8×biên + 0,2×STRUCT 125).
- **So giá (sau khoá; giá đã thấy từ r1):** 33.000 (đóng cửa 04/11, BQ; chưa đối chiếu DNSE) cao hơn tâm **+22,1%**.
  - **Nhãn CÓ ĐIỀU KIỆN:** **ĐẮT nếu biên dài hạn = TB 10 năm (179)** — trên P90 lưới 270 (29.691). **NGHIÊNG ĐẮT / HỢP LÝ nếu biên dài hạn nằm giữa dải bền 180–260**: ở 220 giá cao hơn EV 9,9% (NGHIÊNG ĐẮT); ở ≥ ~233 (100% CYC) hoặc ≥ ~260 (có STRUCT 20%) giá ≈ giá trị (HỢP LÝ). Lưới mở rộng 360 ô LỆCH LÊN (biên 150/179/220/260): P75 31.204 · P90 33.075 ⇒ 33.000 rơi vào NGHIÊNG ĐẮT theo lưới này; lưới đối xứng (138/179/220 → P90 30.458; 98/138/179/220/260 → P90 32.715) vẫn ĐẮT. ĐẮT RÕ (≈+33%) nếu biên = trung vị 152.
  - Giá hàm ý biên dài hạn **≈233 USD/t (100% CYC) hoặc ≈260 (có STRUCT 20%)**; mốc: TB 2016–25 = 179 · 2025 = 257 · hiện tại ≈222 [Bobby]. Giá đang trả cho "biên 2025 duy trì gần như vĩnh viễn"; đó không phi lý nhưng cần biên cao hơn TB 10 năm 30–45% và không có cú sụp cấu trúc.
  - **Nhãn một chữ ở tâm công bố = ĐẮT** (theo lưới 270), nhưng nó **phụ thuộc lựa chọn biên 179**; đừng đọc nhãn mà bỏ điều kiện.

## 1. CÂU HỎI SỐ 1 — LN gộp tăng nhưng LNTT chỉ +123: bóc từng dòng [BCTC; `calc/quarterly.py`]
| Dòng (tỷ) | Q3/25 | Q3/26 | Δ | Ghi chú |
|---|---|---|---|---|
| DT gộp | 3.096,4 | 5.999,6 | +2.903 | |
| Giảm trừ (chiết khấu thương mại) | 108,1 | 258,1 | **−150** | Mike bỏ dòng này ⇒ +592 sai, đúng là +442 |
| LN gộp thuần | 656,7 | 1.098,7 | **+442,0** | biên 22,0% → **19,1%** |
| CP bán hàng | 271,1 | 358,4 | −87,3 | vận chuyển 101,6→146,2 (+44,5); quảng cáo 85,0→109,3 (+24,3); nhân viên +11,9 (TM33 9T−6T) |
| QLDN | 107,4 | 154,1 | −46,7 | xem bẫy trình bày §2 |
| DT tài chính | 128,6 | 56,2 | −72,5 | lãi tiền gửi 74,7→81,3 (+6,6); **lãi tỷ giá +53,8 → −25,2** (Q3 đảo bút toán chưa thực hiện) |
| CP tài chính | 28,1 | 144,4 | −116,3 | lãi vay 19,0→37,4 (+18,4); lỗ tỷ giá 9,1→35,8 (+26,8); **CP tài chính khác 0→71,2** |
| LN khác | −0,3 | 3,4 | +3,7 | |
| **LNTT** | 378,6 | 501,4 | **+122,8** | khớp tổng ±0,1 |
| LNST | 328,0 | 432,3 | +104,3 | thuế hiệu dụng ~13,8% (Q3) |

- **Tỷ giá:** xoay chiều −105,8 tỷ (Q3/25 lãi ròng +44,7; Q3/26 lỗ ròng −61,1). DCM nắm USD 189,4 triệu ngoài bảng (30/9; 1/1: 75,3 triệu) [TM27], nên khoản này **đi theo VND/USD, không bền theo cả hai chiều**.
- **"Chi phí tài chính khác" 71,2 tỷ** (9T 71,30 − 6T 0,13; TM32): **không có thuyết minh**. Có thể là phí L/C, chiết khấu thanh toán hoặc dự phòng (chưa xác minh). Đây là câu hỏi số 1 cần hỏi IR.
- **Thuế xuất khẩu:** không nằm trong giảm trừ. TM29 chỉ có chiết khấu thương mại/giảm giá/hàng trả lại, nên thuế XK nằm trong GVHB hoặc CPBH. Số thuế XK phát sinh 9T/26 là **285,4 tỷ** (TM21, bên "phải thu") ≈ 5% × DT xuất khẩu tự sản xuất.
- **Lãi vay tăng gấp đôi (diễn giải r2, S4):** vay ngắn hạn VND để thanh toán tiền khí lãi suất **1,8–4,8%** (TM24(i), pdf p33). r1 gọi đây là "carry dương có chủ đích" — **SAI**, bỏ:
  - **2.219,9 tỷ tiền phong toả là tiền gửi KHÔNG kỳ hạn** (TM12, pdf p26: "tiền gửi ngân hàng không kỳ hạn bị phong toả để đảm bảo cho các khoản vay"; VCB 1.787,3, Agribank 432,6) ⇒ lãi gần 0, không phải HTM lãi ~6%.
  - DCM còn nắm USD **189,44 triệu ngoài bảng** (TM27) ≈ 5.000 tỷ (ước lượng, ~26.400 đ/USD) — **lớn hơn** tiền mặt 3.470 tỷ.
  - ⇒ Cấu trúc nhiều khả năng là **vay VND lãi thấp để giữ USD = một vị thế tỷ giá**, khớp với lỗ tỷ giá ròng 61 tỷ Q3. Đây là **suy luận**, BCTC không nói thẳng.
  - **Net cash gộp vẫn đúng** (tiền + HTM + phong toả − vay); chỉ diễn giải và chất lượng lãi tiền gửi đổi.
  - **Mâu thuẫn trong chính BCTC, KHÔNG chọn một phía:** TM24(i) ghi các khoản vay này **"không có tài sản bảo đảm"**, còn TM12 ghi tiền gửi phong toả **"để đảm bảo các khoản vay"**. r1 (L105) viết "được bảo đảm bằng chính tiền gửi phong toả" là chọn một phía — bỏ. Việc cần hỏi IR: vay có hay không có đảm bảo; nếu có đảm bảo thì 2.219,9 tỷ không rút được tự do trước khi trả vay.

**Q2/26 → Q3/26 (LNST 1.067 → 432):** LN gộp −902; trong đó urê −884 (DT urê 3.894 → 2.573; xuất khẩu 2.684 → 740; biên gộp urê 46,0% → 35,3%).
- QLDN 451,7 → 154,1 (+298 có lợi): Q2 gánh trích quỹ KH&CN 249,6 tỷ cho cả năm.
- Tài chính ròng +57 → −88 (−145). CPBH +59 có lợi.
- **Giá bán bình quân urê (ước lượng, sản lượng từ báo chí lệch nhau):**
  - Q2 ≈ 15,3 tr đ/t (3.894 tỷ / ~255 kt; VDSC: XK 174 + nội địa 81) [CTCK].
  - Q3 xuất khẩu ≈ 11,9 tr đ/t ≈ 453 USD/t (740 tỷ / ~62 kt = 413 kt 9T − 351 kt H1; tapchikinhtetaichinh 19/08 + mekongasean 16/10).
  - Tức giảm **~−23%** so với Q2, trong khi giá khí gắn dầu không giảm (Brent +68% YoY [Bobby]).
- **Bảo dưỡng tổng thể:** dừng từ 20/9 tới 7/10/2026 (~17 ngày; PetroTimes 15/09, TNCK 07/10). Khoảng 11 ngày rơi vào Q3, phần còn lại sang Q4. Sản lượng tháng 9: XK chỉ 18,1 kt.

## 2. Chuỗi quý & chất lượng lợi nhuận [BCTC, `calc/quarterly_out.txt`]
| Quý | DT thuần | LN gộp | Biên | CPBH | QLDN | TC ròng | LNTT | LNST | LN gộp urê | biên urê | XK urê / DT urê |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1/25 | 3.407 | 885 | 26,0% | 339 | 172 | 78 | 454 | 412 | 876 | 35,9% | 57% |
| Q2/25* | 6.037 | 1.241 | 20,6% | 214 | 229 | 92 | 888 | 788 | 881 | 36,3% | 31% |
| Q3/25 | 2.988 | 657 | 22,0% | 271 | 107 | 101 | 379 | 328 | 537 | 39,0% | 58% |
| Q4/25 | 4.528 | 1.252 | 27,6% | 382 | 473 | 35 | 436 | 389 | 1.155 | 48,1% | 47% |
| Q1/26 | 5.286 | 1.346 | 25,5% | 352 | 179 | 56 | 878 | 789 | 1.212 | 41,5% | 64% |
| Q2/26 | 6.712 | 2.001 | 29,8% | 418 | 452 | 57 | 1.187 | 1.067 | 1.792 | 46,0% | 69% |
| Q3/26 | 5.742 | 1.099 | 19,1% | 358 | 154 | −88 | 501 | 432 | 908 | 35,3% | 29% |

\*Q2/25 đã trình bày lại trong BCTC Q2/26: LNST 806,4 → 787,7 (−18,7). Biên urê tính trên DT gộp từng sản phẩm (TM28/30, hiệu YTD).
- **Bẫy trình bày (không đổi lợi nhuận):**
  - BCTC 9T/26 chuyển **102,9 tỷ "phân bổ giá trị tiềm năng phát triển"** của H1 từ GVHB sang QLDN. 9T − Q3 ≠ H1 đã công bố (GVHB −105,2; QLDN +102,9; LNTT −3,4).
  - Hệ quả: số **QUÝ** lấy từ cột Q3 của KQKD. Số theo sản phẩm Q3 = 9T − 6T có thể lệch ~105 tỷ ở một dòng GVHB (chưa rõ dòng nào; nếu là urê thì biên urê Q3 ≈ 31,3%).
  - Khoản 102,9 tỷ này đã phân bổ hết (số dư 0 tại 30/9) ⇒ **không lặp lại**.
  - BCTC 2025 có hai con số trích quỹ KH&CN: 196,7 tỷ (TM QLDN) và 95,0 tỷ (TM chi phí theo yếu tố).
- **Mảng không phải urê đang lớn lên:**
  - NPK Q3/26: DT 1.624, LN gộp 306 (cùng kỳ 93).
  - Phân bón thương mại: DT 1.536, LN gộp 152 (cùng kỳ 96).
  - Biên thấp nhưng là phần bù lại khi urê xuống.
- **Một lần / không bền trong 9T/26:**
  - Hoàn nhập dự phòng tồn kho **67,4 tỷ** (TM10, làm tăng LN).
  - Phân bổ tiềm năng 102,9 (làm giảm LN, hết).
  - Trích quỹ KH&CN 249,6: định kỳ, ≤10% thu nhập chịu thuế, giảm thuế.
  - Tỷ giá −61 trong Q3.
  - LN tài chính lõi = lãi tiền gửi (9T **228,4 tỷ** trên số dư tiền+HTM+ký quỹ khoảng 8–10 nghìn tỷ ⇒ ~3–4%/năm, ước lượng) − lãi vay 97,2.
- **9T/26:** LNST 2.285 (+49,6%) = **193% kế hoạch năm** (1.182 [NQ]). Kế hoạch đặt rất thấp.

## 3. Trả lời 12 mục "DD cần kiểm gì" của Bobby (§8)
| # | Mục | Trả lời bằng số | Mức chắc |
|---|---|---|---|
| 1 | ASP nội địa vs XK | BCTC **không công bố giá/sản lượng**. DT urê 9T: nội địa 4.103 / XK 5.289 tỷ. ASP ước: Q2 ~15,3, Q3 XK ~11,9 tr đ/t (§1) | thấp (báo chí lệch) |
| 2 | Sản lượng | 9T tiêu thụ urê **741,0 kt** (nội địa 327,8 = 66% KH; XK 413,2 = 150% KH); NPK 176,8; thương mại 300,5 (mekongasean 16/10). 2025: urê quy đổi SX 966,7 kt, tiêu thụ 804,7 [NQ] | trung bình |
| 3 | Giá khí & công thức | ~50% khí PM3 ở **46% MFO**; ~50% Petronas ở **12,7% Brent (2026) → 13,7% (2027+)**; VDSC: Nam Du thay Petronas từ 2028, hoà vốn Brent 75,8; Nam Du–U Minh từ ~Q4/2028 giá **10,39 USD/MMBtu +2,25%/năm**, chiếm 35–60%; cước ~1,14 [CTCK VDSC, dẫn "DCM, Rồng Việt"]. Hợp đồng gốc 3918/HĐ-DKVN 23/5/2012, PLHĐ 12 thêm Nam Du (ĐHĐCĐ bất thường 23/9/2026). **Sàn/trần, take-or-pay, LNG: chưa tìm thấy.** **Bên bán khí đổi [TM38, pdf p42]:** mua từ PVN (Tập đoàn) 9T/25 **3.109,5 tỷ** → 9T/26 **22,4 tỷ**; mua từ CN Khí Tây Nam Bộ–PV GAS 9T/25 **3,4 tỷ** → 9T/26 **4.258,1 tỷ**. Tổng mua hàng/dịch vụ từ nhóm Tập đoàn 3.445,7 → 4.691,4 tỷ (**+36,2%**, đo). Chi phí khí **bất đối xứng**: xem §5 mục "Chi phí khí" | trung bình (thứ cấp) |
| 4 | Định mức khí | chưa có số | — |
| 5 | Tồn kho | 4.321 tỷ (1/1: 4.891), dự phòng 14,9 (hoàn nhập 67,4). Thành phẩm 1.982, hàng hoá 1.180 (tích trước vụ Đông Xuân). Hàng đang đi đường 227,8 (1/1: 7,7) | cao |
| 6 | Bảo dưỡng | 20/9–7/10/2026, ~17 ngày, trễ ~1,3 ngày so kế hoạch. Chi phí sửa chữa dài hạn chờ phân bổ 33,1 tỷ (TM11) ⇒ có phần vốn hoá/phân bổ. Lần trước: chưa thấy | trung bình |
| 7 | Thuế | VAT được khấu trừ **904,8 tỷ** (1/1: 520,9) ⇒ rủi ro nếu quay lại "không chịu thuế". Thuế XK 9T 285,4 tỷ. TNDN hiệu dụng 10,8%. Ưu đãi 10% cho Dự án Nhà máy Đạm Cà Mau **hết sau 2026**: BCTC HN Q3/26 tr.17 (pdf p21): "Năm 2026 là năm thứ 15 … được hưởng ưu đãi thuế suất TNDN 10%" (CV 4641/TCT-CS) ⇒ **20% từ 2027** (đã xác minh trang gốc). Dự án NPK còn ưu đãi riêng (miễn 4 năm + giảm 50% 9 năm; năm bắt đầu không nêu) | cao |
| 8 | Thanh toán khí | Phải trả CN Khí Tây Nam Bộ (PV GAS) **941,8 tỷ** (1/1: 707,9) ≈ 1,5–2 tháng tiền khí (ước lượng). Phải thu PVN **261,0 tỷ** = quyết toán giá khí 2018 (NQ 2202/NQ-DKVN 2024), là khoản DCM được nhận lại | cao |
| 9 | Biên theo mảng | §2. Lãi tiền gửi 9T 228,4 = 8,9% LNTT | cao |
| 10 | Tỷ giá | USD 189,4 triệu tiền mặt; vay toàn VND. Lỗ/lãi tỷ giá theo quý ±60 tỷ | cao |
| 11 | Capex/dự án | XDCB 724 tỷ (kho cảng Nhơn Trạch 247; khí công nghiệp 158; HTS/LTS 152; Thạnh Hoá 66). KH 2026 734 tỷ; nâng công suất 118,5% → 125% thiết kế, 800–1.000 tỷ, cuối 2026 – Q3/2027 (vietnambiz 22/04). M&A 1,5–2 nghìn tỷ 2026–30 (thứ cấp). **Base NPV = 0** (luật 20) | trung bình |
| 12 | Phải thu đại lý | 313,3 tỷ (1/1: 678,4), dự phòng 67,0 (nợ cũ). Người mua trả trước 725,6 ⇒ kênh trả trước nhiều hơn nợ, không thấy dấu hiệu sell-in | cao |

## 4. Bảng cân đối & dòng tiền [BCTC 30/9/2026]
- **Net cash 7.539,1 tỷ:**
  - Tiền 3.470,5 + HTM 4.555,6 + **tiền gửi phong toả đảm bảo vay 2.219,9** (TM12; VCB 1.787, Agribank 433) − vay ngắn hạn 2.699,3 − dài hạn 7,5.
  - Ngày 1/1/2026 là 5.409 (sau đó đã trả cổ tức 1.058,8 tỷ).
  - Vay chủ yếu là vay ngắn hạn VND trả tiền khí, lãi 1,8–4,8% (TM24(i)). **BCTC tự mâu thuẫn về bảo đảm:** TM24(i) nói không có tài sản bảo đảm, TM12 nói tiền gửi phong toả "để đảm bảo các khoản vay" — chưa chọn phía nào (xem §1). Vay dài hạn còn 7,5 tỷ (CĐKT mã 339) + nợ dài hạn đến hạn trả 64,8 + thuê tài chính đến hạn 2,2 (TM24) = 74,5 tỷ.
- **Quỹ khen thưởng phúc lợi 265,3 tỷ** (CĐKT mã 323, pdf p6; 1/1: 290,0) và tạm trích 136,19 tỷ 9T/26 (TM37, pdf p41; 5,97% LNST) là phần lợi nhuận/tiền thuộc về người lao động chứ không về cổ đông: r2 **trừ cả hai** (§5).
- **⚠️ Tiền gửi 332 tỷ bị hạn chế giao dịch** tại Ngân hàng TNHH MTV Việt Nam Hiện đại – CN Cà Mau (TM5). BGĐ cho là thu hồi được, không trích dự phòng. Base GIỮ, độ nhạy −332 tỷ = −627 đ/cp.
- VCSH 11.883 tỷ (BVPS mẹ 22.383 đ). Quỹ KH&CN dài hạn 1.059 tỷ: là nợ phải trả nhưng chi cho R&D/thiết bị của chính DCM; không trừ.
- **CFO 9T/26 +2.331 tỷ** (9T/25 −2.017 do tích tồn kho 1.609). Chi tiết: tồn kho giảm +570; phải trả +335; phải thu −1.225 (gồm VAT +384, ký quỹ tăng).
  - Capex 546. Gửi HTM ròng 380. Cổ tức 1.051.
- **Cổ tức** [NQ, KT bảng VCSH]:
  - 2024: 20% tiền mặt (1.058,8 tỷ, chi 2025; tỷ lệ chi trả 75% LNST 2024).
  - 2025: 20% (1.058,8, chi 21/7/2026; tỷ lệ 54%).
  - **Kế hoạch 2026: 10% (529,4 tỷ).**
  - Đã trích quỹ ĐTPT 656,6 tỷ ngay từ LN 2026.
  - ⇒ Chi trả thấp hơn khả năng: tiền mặt tiếp tục tích luỹ.

## 5. Định giá r2 — mù giá ĐẦU VÀO [`calc/model_r2.py`, khoá md5 23:30:41 trước khi so giá; giá đã thấy từ r1]
**Phương pháp (đổi so với r1 được đánh dấu ⟵):**
- **Bước 1 — hồi quy** (không đổi). LNST năm 2021–25 [BQ] theo biên proxy urê−khí của Bobby (WB): **LNST ≈ −318 + 8,84 × biên** (n=5, phần dư −550…+369). Điểm yếu lớn nhất vẫn là n=5.
- **Bước 2 — tách lãi tiền** (không đổi): lãi tiền gửi ròng 2025 (218 tỷ trước thuế) ra khỏi LNST rồi cộng lại net cash.
- **Bước 3 — thuế ⟵ S1.** Thuế lâu dài **20%** (có nguồn: BCTC Q3/26 tr.17). Năm 1 (Q4/26–Q3/27) dùng thuế pha trộn = 0,25×10,8% + 0,75×20% = **17,7%** (r1: 10,8% cả năm).
- **Bước 4 — quỹ KTPL ⟵ S2.** LNST hoạt động nhân (1 − 5,97%); net cash trừ số dư quỹ 265,3 tỷ. *Cơ sở dữ liệu:* LNST 9T/26 2.282,09 và tạm trích 136,19 [TM37, pdf p41]; số dư quỹ [CĐKT mã 323, pdf p6]. Giả định: tỷ lệ trích 5,97% lặp lại hằng năm (ước lượng từ 1 kỳ 9 tháng).
- **Bước 5 — thuế xuất khẩu ⟵ ADMIN.**
  - (i) r1 năm hoá 285,4 tỷ (9T/26) ⇒ 380,5 tỷ/năm, mà 9T/26 xuất khẩu bất thường (150% kế hoạch). r2 **chuẩn hoá theo xuất khẩu urê FY25**: 5% × 4.051,6 = **202,6 tỷ/năm** trước thuế (−289 đ/cp so với 380,5 ở xác suất cũ).
  - (ii) r1 đặt P 0,55 bên trong nhánh trọng số 0,30 (xác suất hiệu dụng 16,5%). r2 áp **P chính sách 0,55 độc lập cho mọi nhánh**: kỳ vọng +111,4 tỷ/năm trước thuế từ năm 2, vào cả CYC lẫn STRUCT. Hệ quả: nhánh ADMIN trùng CYC về số (biên giống nhau); trọng số 0,50+0,30 vẫn giữ để minh bạch.
  - Năm 1 không tính khoản này (nghị định hạn 31/03/2027).
- **r = 13,5%**, neo theo lãi huy động 12T hiệu dụng **7,40%** (cctg_12m 02/11/2026; `deposit_rate_vn.consumer_deposit_rate_detail` 04/11), β=1 (không đổi).
- Tăng trưởng không tạo giá trị (RONIC = r); capex mới NPV 0 (luật 20).

**Cầu nối r1 → r2 (kỳ vọng, đ/cp; `calc/model_r2_out.txt` dòng 2):**

| Bước | Giá trị | Δ | Ước lượng skeptic |
|---|---|---|---|
| r1 | 28.072 | | |
| + S1 thuế năm 1 | 27.886 | −187 | −187 |
| + S2 quỹ KTPL (trừ LNST −814; trừ số dư −501) | 26.570 | −1.316 | −1.289 |
| + ADMIN (chuẩn hoá + P độc lập) | 27.021 | +451 | +479 |
| **r2** | **27.021** | **−1.051** | |

| Nhánh | P | Biên dài hạn | Giá trị đ/cp |
|---|---|---|---|
| CYCLICAL | 0,50 | **179** = TB proxy 2016–25 (đo) — **lựa chọn phán đoán, xem bảng dưới** | 28.017 |
| ADMIN_GATED | 0,30 | 179 (chính sách đã vào mọi nhánh) | 28.017 |
| STRUCTURAL | 0,20 | **125** (ước lượng: Bobby "TQ bỏ sàn + Brent cao ⇒ biên 100–150") | 23.037 |
| **Kỳ vọng** | | | **27.021** |

**Bảng biên dài hạn → giá trị/cp (S3; chỉ 1 mức dưới tâm, 3 mức trên ⇒ lệch lên; không chọn theo giá):**

| Biên dài hạn (USD/t) | LNTT hoạt động (tỷ) | CYC 100% | Kỳ vọng (0,8×biên + 0,2×STRUCT125) |
|---|---|---|---|
| 150 | 913 | 25.336 | 24.876 |
| **179 (TB 10 năm, tâm)** | 1.201 | 28.002 | **27.009** |
| 220 (giữa dải bền) | 1.607 | 31.772 | 30.025 |
| 242 | 1.825 | 33.795 | 31.643 |
| 260 (cận trên dải bền) | 2.004 | 35.450 | 32.967 |

(Dòng 179 dùng chính xác 179,0; tâm dùng 179,16 ⇒ 27.021.) Tâm công bố vẫn ở 179 vì đó là số đo duy nhất (TB 10 năm của proxy WB); chọn điểm khác trong dải 180–260 sau khi đã thấy giá sẽ là dịch tâm theo giá. Hai chiều bất định đều thật: dải bền của Bobby gồm cả 2021–22 bất thường (kéo biên lên), còn trung vị 10 năm theo tháng 152 thấp hơn tâm (kéo xuống).

- **Độ nhạy kỳ vọng (đ/cp, so với 27.021):**
  - Lãi huy động +50bp / −50bp: β1 −456 / +491; β0,5 −232 / +241. ±100bp: β1 −881 / +1.021; β0,5 −456 / +491.
  - Phong toả −332 tỷ: −627. Biên năm 1 = 170: −664; = 285: +804.
  - Biên chu kỳ 150: −2.145; 210: +2.268. STRUCT 100: −460.
  - Chính sách thuế XK: P=0 → 25.988 (−1.033); P=1 → 27.866 (+845). Nếu dùng lại 380,5 thay 202,6: +908.
- **NPK — ưu đãi còn lại, PHÍA TĂNG** (cùng trang p21: miễn 4 năm + giảm 50% 9 năm; **năm bắt đầu KHÔNG nêu**): giảm 50% thuế (20%→10%) trên phần LNTT NPK trong N năm còn lại từ năm 2. Phần LNTT NPK (ước lượng 10–20%; LN gộp NPK Q3/26 306 tỷ trên 1.099 tổng) × N (5/10 năm, ước lượng): **+65 (10%, 5 năm) · +100 (10%, 10 năm) · +131 (20%, 5 năm) · +200 (20%, 10 năm) đ/cp**. Không vào base. Nhỏ: ≤ +0,7% kỳ vọng.
- **Chi phí khí 2027–30 — HAI CHIỀU, là cược theo Brent** (ngoài base; nguồn VDSC Q3/26 `src/web/vietstock_doc22472_VDSC_DCM_Q3_2026.pdf`, chưa thấy hợp đồng; r3 sửa lỗi dấu của r2):
  - **Petronas 12,7% → 13,7% Brent từ 2027:** khoảng 8,5 USD/t, tức ≈216 tỷ/năm trước thuế (50% khí, Brent TB 2016–25 = 67,8). Theo cùng nguồn, tỷ trọng Petronas đi 50% → 15% (2028) → 0% (2029) vì Nam Du thay thế ⇒ tác động chủ yếu là chuyển tiếp 2027–28: **≈ −400 đ/cp** (ước lượng). Chỉ khi Nam Du trễ và Petronas giữ 50% vĩnh viễn thì mới là −2.216.
  - **Nam Du 10,39 USD/MMBtu (+2,25%/năm) từ ~Q4/2028, THAY khí Petronas** (không thay khí PM3 theo proxy Bobby). Hoà vốn với Petronas 13,7% ở Brent ≈ **75,8** (VDSC nêu đúng mức này: Petronas 13,7% × 75,8 ≈ 10,38 USD/MMBtu ≈ giá Nam Du). Tác động đ/cp, tỷ trọng Nam Du 35% / 60%, Brent phẳng; trong ngoặc là có leo thang 2,25%/năm của Nam Du so với Brent danh nghĩa đứng yên (tính lại bởi skeptic, `/tmp/fsk_gas_check.py`, chưa nằm trong `calc/` của Taylor):
    - Brent 67,8: −2.010 (−5.801) / −3.445 (−9.945)
    - Brent 82: +1.540 (−2.252) / +2.640 (−3.860)
    - Brent 90: +3.540 (−252) / +6.068 (−432)
  - **Không cộng dòng Petronas với dòng Nam Du.** Rủi ro khí không một chiều: ở Brent TB 10 năm là chi phí; ở Brent 2026 (TB 94 [BQ]; tháng 10 ≈107 [Bobby]) là tiết kiệm. Riêng điều khoản leo thang 2,25%/năm nghiêng về phía hạ. *(r2 so Nam Du với proxy chung của Bobby và ghi −4.543…−11.947; con số đó SAI DẤU ở Brent cao và đã bị rút.)*
- **Thuế lịch sử 2021–24 thấp hơn 10,8% (chưa vào tâm):** thư giải trình của DCM cho thuế hiệu dụng Q2/24 ≈4,7%, Q3/24 ≈8,3%, Q4/24 ≈10,7% (`txt/DCM_Q2_2025_Hopnhat.txt`, `DCM_Q3_2025`, `DCM_Q4_2025`), phù hợp giai đoạn "giảm 50% trong 9 năm" ở p21. Hồi quy LNST~biên quy về LNTT bằng thuế 10,8% cho mọi năm ⇒ tâm có thể bị thổi **+280…+560 đ/cp** (ước lượng skeptic); sửa chỉ làm nhãn ĐẮT rõ hơn.
- **Dải trích quỹ KTPL:** 5,97% (9T/26, dùng trong mô hình) so với 4,65% (9T/25: 70,87/1.525,23, cùng trang p41) ⇒ dùng 4,65% thì tâm +187 đ/cp.
- **Lưới 270** (r±100bp × biên TC 150/179/210 × năm 1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332; thuế 20%): **P10 24.065 · P25 25.121 · P50 26.745 · P75 28.458 · P90 29.691**.
  - Lưới mở rộng 360 ô (biên 150/179/220/260) **LỆCH LÊN** (chỉ 1 mức dưới tâm, 3 mức trên; TB biên 202 > 179; chỉ để tham khảo). Lưới đối xứng quanh 179 vẫn cho ĐẮT ở 33.000: 138/179/220 → P90 30.458; 98/138/179/220/260 → P90 32.715. Lưới 360: P10 24.331 · P25 25.705 · P50 28.255 · P75 31.204 · P90 33.075.
- **Thanh khoản [BQ, sau khoá]:** GTGD trung vị 90 phiên **74,0 tỷ/ngày** (20 phiên 56,9; thấp nhất 90 phiên 23,5). Vị thế 0,5–1% NAV ở quỹ 50 tỷ (tài khoản thực tế nhỏ hơn nhiều, ≈1 tỷ ⇒ kết luận càng chắc) ≈ 1% ADV, thoát 1 phiên ở mức tham gia 10% ⇒ **chiết khấu thanh khoản ≈ 0** (ước lượng; cơ sở BQ). Giá trị sau chiết khấu thanh khoản = **27.021**. Free float ≈ 24% (PVN 75,56%).
- **So giá (sau khoá, `calc/compare_px_r2_out.txt`):** 33.000 vs tâm 27.021 = **+22,1%** (vs CYC +17,8%).
  - Biên dài hạn hàm ý của giá: 233 (100% CYC) / 260 (có STRUCT 20%).
  - Ở biên 150/179/220/242/260 giá cao hơn EV lần lượt **+32,7% / +22,2% / +9,9% / +4,3% / +0,1%**.
  - Nhãn theo lưới 270: ĐẮT (>P90 29.691). Theo lưới mở rộng lệch lên: NGHIÊNG ĐẮT (≤ P90 33.075); theo lưới đối xứng: ĐẮT. **ĐẮT RÕ nếu biên = trung vị 10 năm theo tháng 152 (giá cao hơn EV ≈ +33%).**
- **Kiểm chéo, chỉ đối chiếu (sau khoá; BQ 04/11):**

  | Mã | P/E | P/B | EV/EBITDA |
  |---|---|---|---|
  | DCM | 6,43 | 1,47 | 4,94 |
  | DPM | 8,54 | 1,17 | 8,15 |
  | DDV | 5,64 | 1,01 | 4,5 |

  - P/E và P/B trung bình 5 năm của DCM: 9,51 và 1,79. P/E TTM 6,5 thấp vì 4 quý gồm biên đỉnh Q1–Q2/26 — đừng đọc là rẻ.
- **Bối cảnh lãi suất (luật 17):** chưa chạy dòng r\* thị trường / TPCP 10Y. Phần này thuộc bản cho nhà đầu tư.

## 6. Mốc khoá trước & điều kiện đổi nhận định (CẢ HAI chiều)
Mốc theo forecast của Bobby (TB5 urê TE, biên proxy gốc 219):
- **24/11/2026:** trung vị biên 224.
- **03/01/2027:** trung vị biên 225.
- **04/03/2027:** trung vị biên 222.
- **BCTC Q4/2026:** khoảng cuối tháng 01/2027.
- **Nghị định thuế XK urê 0%:** hạn 31/03/2027, P 0,55 (đã tính độc lập mọi nhánh).

**Luật đổi nhận định (r3, sửa B2 của skeptic): MỘT điều kiện xảy ra ⇒ CHẠY LẠI mô hình; tâm chỉ dời ±2.000 khi tổng tác động đủ lớn. Cùng một luật cho cả hai chiều.** Tác động đơn lẻ (đ/cp): biên năm 1 = 170: −664 (−2.145 nếu biên dài hạn về 150); 332 tỷ MBV: −627; "chi phí tài chính khác" ≥50 tỷ/quý lặp vĩnh viễn ≈ −2.100.

**Điều kiện NÂNG giá trị:**
- (a) Q4/26 + Q1/27 LNST cộng lại ≥ 1.200 tỷ trong khi biên proxy ≤ 230 (biên thật của DCM cao hơn proxy, hồi quy đang đánh giá thấp). *Ghi chú: ngưỡng lấy từ r1. LNST công bố là số TRƯỚC khi trích KTPL (TM37) nên không cần hiệu chỉnh vì KTPL; thứ cần hiệu chỉnh là thuế 20% từ Q1/27.*
- (b) Nghị định thuế XK 0% được ban hành (cộng ≈ +1.033 so với P=0 trong lưới r2, tức xác suất 0,55 → 1 cộng +845).
- (c) *(đã bỏ — ưu đãi 10% hết sau 2026, có nguồn p21.)* Thay bằng: xác nhận năm bắt đầu ưu đãi NPK còn dài (+65…+200).
- (d) Biên proxy TB5 ngày 04/03/2027 > 255.
- (e) Nam Du vào đúng hạn khi Brent dài hạn ≥ ~85 (+1.500 trở lên, Brent phẳng); hoặc công bố sàn/trần giá khí có lợi.

**Điều kiện HẠ giá trị:**
- (a) Biên proxy < 170 ở hai mốc liên tiếp.
- (b) Nam Du ≥35% khi Brent dài hạn < ~75 (từ −2.000 trở xuống); hoặc Nam Du trễ và Petronas giữ 50% ở 13,7% (−2.216). (Xem §5: rủi ro khí hai chiều theo Brent.)
- (c) Tiền 332 tỷ phải trích lập (−627), hoặc thêm khoản tiền bị phong toả; hoặc IR xác nhận 2.219,9 tỷ phong toả bảo đảm khoản vay (không rút tự do ⇒ net cash tự do nhỏ hơn).
- (d) VAT phân bón quay lại "không chịu thuế" (rủi ro dư VAT khấu trừ 905 tỷ).
- (e) "Chi phí tài chính khác" lặp lại ≥ 50 tỷ/quý mà không có giải thích; hoặc lỗ tỷ giá lặp lại (vị thế USD 189,4 triệu).

**Nhãn ở giá 33.000 (sau khoá):** theo lưới 270 là **ĐẮT** (chỉ về HỢP LÝ khi giá ≤ P75 28.458); nhưng **có điều kiện biên** — chuyển sang NGHIÊNG ĐẮT nếu biên dài hạn ≥ ~220 (giá +9,9% so với EV) và sang HỢP LÝ nếu biên ≥ ~233 (100% CYC) / ~260 (có STRUCT). Quan sát cần để phân biệt: biên proxy thực tế còn ≥ 220 sau mốc 04/03/2027 mà không có cú sụp cấu trúc.

## 7. Pháp lý / quản trị — WARNING (không vào base)
- ⚠️ Tiền gửi 332 tỷ bị hạn chế tại Ngân hàng Việt Nam Hiện đại (MBV, tiền thân OceanBank) [TM5 BCTC Q3/26; KT25 TM6 tr.21, 31/12/2025: Deloitte **không trích lập, không nhấn mạnh**]. Chưa có tiến độ xử lý.
- ⚠️ Thù lao HĐQT/BĐH/BKS 9T/26 **56,56 tỷ so với 17,39 tỷ cùng kỳ (gấp 3,25 lần)**, cùng một người cũng ≈ ×3 (VD Nguyễn Thanh Tùng 1,49 → 4,65 tỷ; Nguyễn Đức Hạnh 1,48 → 4,37 tỷ) [TM38(4), pdf p45, tr.41 — đã đối chiếu trang gốc]. Kế hoạch LN đặt rất thấp (1.182 so với thực hiện 9T 2.285) cộng với thưởng theo vượt kế hoạch ⇒ rủi ro lệch lợi ích (suy luận).
- ⚠️ Biến động nhân sự:
  - ĐHĐCĐ 04/2026 thay một số thành viên HĐQT/BKS, TGĐ mới Nguyễn Thanh Tùng.
  - PTGĐ Nguyễn Tuấn Anh "nghỉ 17/09/2026" — **nguồn báo chí, chưa có trong BCTC**: BCTC lập 15/10/2026 (pdf p45) vẫn liệt kê ông trong bảng thu nhập 9T/26 (4,30 tỷ).
  - ĐHĐCĐ bất thường 23/09/2026 (chưa tìm thấy kết quả biểu quyết).
- ⚠️ Bên liên quan chiếm ưu thế: PVN 75,56%. **Bên bán khí đổi (TM38, pdf p42):** 9T/25 mua từ PVN 3.109,5 tỷ; 9T/26 mua từ CN Khí Tây Nam Bộ–PV GAS 4.258,1 tỷ (PVN còn 22,4 tỷ); tổng mua nhóm Tập đoàn +36,2%. r1 viết "PV GAS là người bán khí duy nhất" — **bỏ**: người bán thay đổi theo kỳ, cả hai thuộc tập đoàn ⇒ giá khí vẫn là quyết định nội bộ.
- ⚠️ **"Giá trị tiềm năng phát triển" 102,9 tỷ** bắt nguồn từ Kết luận Thanh tra Chính phủ 07/7/2023 (Thuyết minh chính sách kế toán, pdf p18; phản ánh giá trị tại thời điểm cổ phần hoá 15/01/2015). Đã phân bổ hết (số dư 0 tại 30/9/2026; 1/1: 102,9).
- ⚠️ **Phải thu PVN 163,6 → 261,0 tỷ trong 9T/26** (TM8), chưa thu sau ~2,5 năm kể từ NQ 2202/NQ-DKVN: khoản tăng thêm, không phải số tiền đứng yên.
  - Có tiền lệ quyết toán giá khí 2018 có lợi cho DCM (phải thu 261 tỷ, chưa thu).
  - PVN không có kế hoạch thoái vốn 2026.
- ⚠️ Thuế nhà thầu 43,2 tỷ (khoản vay ECA của PVN) đã dự phòng 100%, đang xin hoàn.
- Kiểm toán: **BCTC 2025 Deloitte chấp nhận toàn phần, không có đoạn nhấn mạnh** [KT25 tr.4]. LNST kiểm toán 1.961,8 so với chưa kiểm toán ~1.917 (+2,3%).
  - BCTC soát xét 6T/2026: chưa đọc trang kết luận (scan).
  - Bẫy trình bày nêu ở §2 (phân loại lại 102,9 tỷ; trình bày lại Q2/25; hai con số trích quỹ KH&CN 2025).
- Room ngoại: chưa xác minh.

## 8. Chưa xác minh (ưu tiên)
1. ~~Năm hết ưu đãi thuế TNDN~~ **ĐÃ ĐÓNG (r2):** hết sau 2026, BCTC Q3/26 tr.17 (pdf p21). Còn mở: **năm bắt đầu ưu đãi NPK** (miễn 4 + giảm 50% 9 năm), độ lớn phần LNTT NPK.
2. Nội dung "chi phí tài chính khác" 71,2 tỷ Q3/26; khoản 102,9 tỷ phân loại lại vào dòng GVHB nào.
3. **Công thức giá khí gốc**: sàn/trần, take-or-pay, hệ số Petronas 2027, phần LNG, **giá 10,39 USD/MMBtu Nam Du là giá gì** (quy đổi?). Hiện chỉ có nguồn CTCK; kịch bản §5 hai chiều: −3.400…+6.100 (Brent phẳng), −9.900…−250 (có leo thang 2,25%/năm), trên dải Brent 67,8–90. Hỏi IR: Nam Du 10,39 có gồm cước không, điều khoản leo thang, lịch giảm Petronas.
4. Sản lượng, giá bán theo quý (báo chí lệch: H1 XK 351 kt hay 385 kt). Định mức khí MMBtu/t (dùng 25 của Bobby).
5. Kết luận soát xét 6T/2026; kết quả ĐHĐCĐ bất thường 23/9; tiến độ thu hồi 332 tỷ; room ngoại.
6. Độ dốc hồi quy LNST–biên chỉ có 5 điểm ⇒ nên thay bằng mô hình sản lượng × (giá − khí).
7. Giá tham chiếu 33.000 lấy từ BQ, chưa đối chiếu DNSE.
8. **Vay khí có/không có tài sản bảo đảm** (TM24(i) ↔ TM12) và **vị thế USD 189,4 triệu** có phải đối ứng với vay VND không (hỏi IR).
9. Tỷ lệ trích quỹ KTPL hằng năm: 5,97% (9T/26) so với 4,65% (9T/25) ⇒ dải tâm +187.
10. Thuế hiệu dụng 2021–24 (thấp hơn 10,8%) — Taylor đo từ BCTC năm; tâm có thể bị thổi +280…+560.

## 9. Sản phẩm
- `calc/quarterly.py` (+`_out`): bóc theo quý.
- `calc/model.py` (+`_out`): định giá r1 (giữ nguyên, md5 trong `LOCK_md5.txt`).
- `calc/model_r2.py` (+`model_r2_out.txt/.json`): định giá r2; `calc/LOCK_r2_md5.txt`.
- `calc/compare_px_r2.py` (+`_out`), `calc/px_liq.sql`, `calc/comps.sql`: chạy sau khoá.
- `png/r2q3_p{18,21,26,33,41,42,45}.png`: trang BCTC gốc đã kiểm lại cho S1–S4/WARNING (+`q326hn_p06.png` CĐKT).
- `png/`: ảnh trang BCTC.
- `src/web/`: NQ ĐHĐCĐ, KT 2025, soát xét 6T, tài liệu CTCK. Tài liệu CTCK có giá mục tiêu, KHÔNG dùng.
- Chưa làm: skeptic vòng 2, báo cáo cho nhà đầu tư, sổ `dd_price_zones.json`. **Không gửi email, không đặt lệnh, không sửa plan.**
