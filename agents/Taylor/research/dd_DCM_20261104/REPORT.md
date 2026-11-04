# DD — DCM (CTCP – Tổng Công ty Phân bón Dầu khí Cà Mau, PVCFC) · as-of 04/11/2026 · job `Taylor_20261104_155446`

> NGHIÊN CỨU READ-ONLY, hồ sơ NỘI BỘ. Không phải khuyến nghị. fundamental-skeptic CHƯA chạy.
> Nguồn: **[BCTC]** = BCTC hợp nhất Q3/2026 (công bố 29/10/2026, Vietstock static2; bảng là ảnh scan, đọc từ `png/q326hn_*`) + Q2/2026, Q1/2026,
> Q4/2025 (cùng nguồn, `src/`); **[KT25]** BCTC HN 2025 kiểm toán (`src/web/`); **[NQ]** Nghị quyết ĐHĐCĐ 996/NQ-PVCFC 22/04/2026; **[BQ]** `tav2_bq`;
> **[Bobby]** `kb/data_registry/market-state/sector_read_phan_dam_ure_20261104.md` (đọc mù); **[CTCK]** = tài liệu môi giới (chỉ dùng số vận hành, KHÔNG dùng giá mục tiêu).
> **Thứ tự chạy, trung thực:** `calc/model.py` không nhận giá/vốn hoá/PE của DCM. Mô hình được khoá md5 lúc **23:12:56 ICT** (`calc/LOCK_md5.txt`), sau đó mới truy vấn giá (`calc/px_liq.sql`, `calc/compare_px.py`).
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
- **Bảng cân đối rất khoẻ:** net cash **7.539 tỷ = 14.241 đ/cp** (30/9/2026). CFO 9T **+2.331 tỷ**, là tiền thật. Kiểm toán 2025 (Deloitte) **chấp nhận toàn phần**.
- **Định giá (mù giá; r 13,5% @ huy động 7,40%):**
  - Kỳ vọng **28.072 đ/cp** = 0,50×CYC 28.512 + 0,30×ADMIN 30.576 + 0,20×STRUCT 23.217.
  - Lưới 540: P10 25.409 · P25 26.617 · P50 28.463 · P75 30.346 · P90 31.901.
  - Chiết khấu thanh khoản ≈ 0 ở quy mô ≤1% NAV (ADV 74 tỷ), nên giá trị SAU chiết khấu thanh khoản vẫn **28.072**.
- **So giá (sau khoá):** 33.000 (đóng cửa 04/11, BQ) cao hơn tâm **+17,6%** và cao hơn P90 3,4% ⇒ **ĐẮT** theo thang lưới (RẺ ≤P10 · RẺ CÓ ĐK ≤P25 · HỢP LÝ ≤P75 · NGHIÊNG ĐẮT ≤P90 · ĐẮT >P90).
  - Giá hàm ý biên urê−khí dài hạn **≈242 USD/t**. Mốc so sánh: TB chu kỳ 2016–25 = 179; 2025 = 257; hiện tại ≈222 [Bobby].
  - Nói cách khác, giá đang trả cho kịch bản "năm 2025 lặp lại mãi". Đó không phải phi lý, nhưng cần biên duy trì cao hơn trung bình 10 năm khoảng 35%.

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
- **Lãi vay tăng gấp đôi:** vay ngắn hạn thanh toán tiền khí lãi suất **1,8–4,8%** (TM24), trong khi tiền gửi HTM lãi khoảng 6%. Đây là carry dương có chủ đích, không phải căng thẳng tài chính.

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
| 3 | Giá khí & công thức | ~50% khí PM3 ở **46% MFO**; ~50% Petronas ở **12,7% Brent (2026) → 13,7% (2027+)**; Nam Du–U Minh từ ~Q4/2028 giá **10,39 USD/MMBtu +2,25%/năm**, chiếm 35–60%; cước ~1,14 [CTCK VDSC, dẫn "DCM, Rồng Việt"]. Hợp đồng gốc 3918/HĐ-DKVN 23/5/2012, PLHĐ 12 thêm Nam Du (ĐHĐCĐ bất thường 23/9/2026). **Sàn/trần, take-or-pay, LNG: chưa tìm thấy** | trung bình (thứ cấp) |
| 4 | Định mức khí | chưa có số | — |
| 5 | Tồn kho | 4.321 tỷ (1/1: 4.891), dự phòng 14,9 (hoàn nhập 67,4). Thành phẩm 1.982, hàng hoá 1.180 (tích trước vụ Đông Xuân). Hàng đang đi đường 227,8 (1/1: 7,7) | cao |
| 6 | Bảo dưỡng | 20/9–7/10/2026, ~17 ngày, trễ ~1,3 ngày so kế hoạch. Chi phí sửa chữa dài hạn chờ phân bổ 33,1 tỷ (TM11) ⇒ có phần vốn hoá/phân bổ. Lần trước: chưa thấy | trung bình |
| 7 | Thuế | VAT được khấu trừ **904,8 tỷ** (1/1: 520,9) ⇒ rủi ro nếu quay lại "không chịu thuế". Thuế XK 9T 285,4 tỷ. TNDN hiệu dụng 10,8%. Ưu đãi **10%/15 năm từ khi SX** (TM BCTC, dẫn qua Báo Đầu tư); năm hết ưu đãi **chưa xác minh** | trung bình |
| 8 | Thanh toán khí | Phải trả CN Khí Tây Nam Bộ (PV GAS) **941,8 tỷ** (1/1: 707,9) ≈ 1,5–2 tháng tiền khí (ước lượng). Phải thu PVN **261,0 tỷ** = quyết toán giá khí 2018 (NQ 2202/NQ-DKVN 2024), là khoản DCM được nhận lại | cao |
| 9 | Biên theo mảng | §2. Lãi tiền gửi 9T 228,4 = 8,9% LNTT | cao |
| 10 | Tỷ giá | USD 189,4 triệu tiền mặt; vay toàn VND. Lỗ/lãi tỷ giá theo quý ±60 tỷ | cao |
| 11 | Capex/dự án | XDCB 724 tỷ (kho cảng Nhơn Trạch 247; khí công nghiệp 158; HTS/LTS 152; Thạnh Hoá 66). KH 2026 734 tỷ; nâng công suất 118,5% → 125% thiết kế, 800–1.000 tỷ, cuối 2026 – Q3/2027 (vietnambiz 22/04). M&A 1,5–2 nghìn tỷ 2026–30 (thứ cấp). **Base NPV = 0** (luật 20) | trung bình |
| 12 | Phải thu đại lý | 313,3 tỷ (1/1: 678,4), dự phòng 67,0 (nợ cũ). Người mua trả trước 725,6 ⇒ kênh trả trước nhiều hơn nợ, không thấy dấu hiệu sell-in | cao |

## 4. Bảng cân đối & dòng tiền [BCTC 30/9/2026]
- **Net cash 7.539,1 tỷ:**
  - Tiền 3.470,5 + HTM 4.555,6 + **tiền gửi phong toả đảm bảo vay 2.219,9** (TM12; VCB 1.787, Agribank 433) − vay ngắn hạn 2.699,3 − dài hạn 7,5.
  - Ngày 1/1/2026 là 5.409 (sau đó đã trả cổ tức 1.058,8 tỷ).
  - Vay chủ yếu là vay ngắn hạn trả tiền khí, lãi thấp, được bảo đảm bằng chính tiền gửi phong toả. Vay dài hạn còn 74,5 tỷ.
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

## 5. Định giá — mù giá [`calc/model.py`, khoá md5 trước khi so giá]
**Phương pháp:**
- **Bước 1 — hồi quy.** LNST năm 2021–25 [BQ] được hồi quy theo biên proxy urê−khí của Bobby, tính trên WB [BQ]: **LNST ≈ −318 + 8,84 × biên** (n=5, phần dư −550…+369). Đây là thước đo thô, có nhãn (ước lượng).
  - Kiểm chéo: biên WB 9T/2026 là 340, mô hình dự báo LNST 2026 ≈ 2.688. Thực tế 9T là 2.285 + Q4.
- **Bước 2 — tách lãi tiền.** Lấy lãi tiền gửi ròng 2025 (218 tỷ trước thuế) ra khỏi LNST, để không vốn hoá tiền mặt ở r. Sau đó cộng lại net cash.
- **Bước 3 — dòng thời gian và thuế.**
  - Năm 1 (Q4/26–Q3/27): biên 222 [Bobby, trung vị forecast], thuế 10,8%.
  - Từ năm 2: vĩnh viễn ở biên dài hạn theo nhánh. **Thuế 20%** (ước lượng: giả định ưu đãi 15 năm tính từ 2012 hết vào 2026; độ nhạy 10% +1.313 đ/cp).
  - Tăng trưởng không tạo giá trị (RONIC = r). Capex mới NPV 0.
- **r = 13,5%**, neo theo lãi huy động 12T hiệu dụng **7,40%** (cctg_12m 02/11/2026; Big-4 6,8%; `deposit_rate_vn.consumer_deposit_rate_detail` ngày 04/11). β = 1. Khung Ke nội địa 12,3–13,4% (β1,1) ⇒ 13,5% nằm ở đầu trên.

| Nhánh [Bobby] | P | Biên dài hạn | LNST hoạt động dài hạn (thuế 20%) | Giá trị đ/cp |
|---|---|---|---|---|
| CYCLICAL | 0,50 | **179** = TB proxy 2016–25 (đo) | 962 tỷ (+ lãi tiền ròng ~174) | 28.512 |
| ADMIN_GATED | 0,30 | 179 + kỳ vọng thuế XK 0% (P 0,55 × ~381 tỷ/năm trước thuế, ước lượng từ TM21) | — | 30.576 |
| STRUCTURAL | 0,20 | **125** (ước lượng: Bobby "TQ bỏ sàn + Brent cao ⇒ biên 100–150"; khí Nam Du giá cố định, phần LNG) | 532 | 23.217 |
| **Kỳ vọng** | | | | **28.072** |

- Cơ sở mỗi khoản giảm trừ trong base:
  - (i) Thuế 20% từ 2027: TM BCTC nêu ưu đãi 10% trong 15 năm từ khi SX. Năm bắt đầu 2012 là ước lượng, **cần xác minh** (thứ tự ưu tiên #1).
  - (ii) Không giảm trừ vốn lưu động tối thiểu và không giảm trừ tiền phong toả: không có cơ sở, nên chỉ đưa vào độ nhạy.
- **Độ nhạy (đ/cp, so với 28.072):**
  - Lãi huy động ±50bp: −466/+503 (β1), −237/+247 (β0,5). ±100bp: −901/+1.045 (β1), −466/+503 (β0,5).
  - Thuế 10% vĩnh viễn: +1.313. Phong toả −332 tỷ: −627.
  - Biên năm 1 = 170: −765; = 285: +928.
  - Biên chu kỳ 150: −2.281; 210: +2.413. STRUCT 100: −488.
  - Giữ 1.500 tỷ vốn lưu động tối thiểu (ước lượng, không có trong base): −2.833.
  - Độ dốc hồi quy là điểm yếu lớn nhất: chỉ n=5.
- **Lưới 540** (r ±100bp × thuế 10/20% × biên chu kỳ 150/179/210 × năm 1 170/222/285 × STRUCT 100/125/150 × phong toả 0/−332): **P10 25.409 · P25 26.617 · P50 28.463 · P75 30.346 · P90 31.901**.
- **Thanh khoản [BQ, sau khoá]:**
  - GTGD trung vị 90 phiên **74,0 tỷ/ngày** (20 phiên 56,9; thấp nhất 90 phiên 23,5).
  - Một vị thế 0,5–1% NAV ở quy mô quỹ 50 tỷ chỉ bằng ~1% ADV, thoát trong 1 phiên ở mức tham gia 10%.
  - ⇒ **chiết khấu thanh khoản ≈ 0** (ước lượng; có cơ sở BQ). Giá trị **sau chiết khấu thanh khoản = 28.072**. Free float khoảng 24% (PVN 75,56%).
- **Kiểm chéo, chỉ đối chiếu (sau khoá; BQ 04/11):**

  | Mã | P/E | P/B | EV/EBITDA |
  |---|---|---|---|
  | DCM | 6,43 | 1,47 | 4,94 |
  | DPM | 8,54 | 1,17 | 8,15 |
  | DDV | 5,64 | 1,01 | 4,5 |

  - P/E và P/B trung bình 5 năm của DCM là 9,51 và 1,79.
  - P/E ex-cash của DCM trên LNST hoạt động chu kỳ: 10,3x (thuế 20%) và 9,3x (thuế 10,8%).
  - P/E TTM 6,5 thấp chỉ vì 4 quý gồm biên đỉnh Q1–Q2/26. Đừng đọc là rẻ.
- **Bối cảnh lãi suất (luật 17):** chưa chạy dòng r\* thị trường / TPCP 10Y. Phần này thuộc bản cho nhà đầu tư.

## 6. Mốc khoá trước & điều kiện đổi nhận định (CẢ HAI chiều)
Mốc theo forecast của Bobby (TB5 urê TE, biên proxy gốc 219):
- **24/11/2026:** trung vị biên 224.
- **03/01/2027:** trung vị biên 225.
- **04/03/2027:** trung vị biên 222.
- **BCTC Q4/2026:** khoảng cuối tháng 01/2027.
- **Nghị định thuế XK urê 0%:** hạn 31/03/2027, P 0,55.

**Nâng giá trị (tâm lên ≥ ~31.000) khi CÓ ÍT NHẤT HAI trong các điều sau:**
- (a) Q4/26 + Q1/27 LNST cộng lại ≥ 1.200 tỷ trong khi biên proxy ≤ 230. Tức biên thật của DCM cao hơn proxy và hồi quy đang đánh giá thấp.
- (b) Nghị định thuế XK 0% được ban hành (+~2.000 đ/cp ở nhánh ADMIN).
- (c) Xác nhận ưu đãi thuế 10% còn sau 2026 (+1.313).
- (d) Biên proxy TB5 ngày 04/03/2027 > 255.
- (e) Công bố sàn giá khí hoặc trần theo Brent có lợi.

**Hạ giá trị (tâm xuống ≤ ~25.500) khi CÓ MỘT trong các điều sau:**
- (a) Biên proxy < 170 ở hai mốc liên tiếp.
- (b) Xác nhận hệ số Petronas 13,7% Brent từ 2027 cộng với tỷ trọng LNG/Nam Du làm giá khí bình quân > 11 USD/MMBtu khi Brent < 80.
- (c) Tiền 332 tỷ phải trích lập, hoặc thêm khoản tiền bị phong toả.
- (d) VAT phân bón quay lại "không chịu thuế" (rủi ro dư VAT khấu trừ 905 tỷ).
- (e) "Chi phí tài chính khác" lặp lại ≥ 50 tỷ/quý mà không có giải thích.

Ở giá 33.000, nhãn chỉ chuyển về **HỢP LÝ** khi giá ≤ P75 30.346, hoặc khi tâm được nâng theo các điều kiện trên.

## 7. Pháp lý / quản trị — WARNING (không vào base)
- ⚠️ Tiền gửi 332 tỷ bị hạn chế tại Ngân hàng Việt Nam Hiện đại (MBV, tiền thân OceanBank) [TM5]. Đây là di sản; chưa có tiến độ xử lý.
- ⚠️ Thù lao HĐQT/BĐH 9T/26 **56,6 tỷ, gấp 3,25 lần cùng kỳ** (kinhtechungkhoan 30/10, dẫn TM BCTC; chưa đối chiếu trang gốc). Kế hoạch LN đặt rất thấp (1.182 so với thực hiện 9T 2.285) cộng với thưởng theo vượt kế hoạch ⇒ rủi ro lệch lợi ích (suy luận).
- ⚠️ Biến động nhân sự:
  - ĐHĐCĐ 04/2026 thay một số thành viên HĐQT/BKS, TGĐ mới Nguyễn Thanh Tùng.
  - PTGĐ Nguyễn Tuấn Anh nghỉ 17/09/2026.
  - ĐHĐCĐ bất thường 23/09/2026 (chưa tìm thấy kết quả biểu quyết).
- ⚠️ Bên liên quan chiếm ưu thế: PVN 75,56%, PV GAS là người bán khí duy nhất ⇒ giá khí là quyết định trong nội bộ tập đoàn.
  - Có tiền lệ quyết toán 2018 có lợi cho DCM (phải thu 261 tỷ).
  - PVN không có kế hoạch thoái vốn 2026.
- ⚠️ Thuế nhà thầu 43,2 tỷ (khoản vay ECA của PVN) đã dự phòng 100%, đang xin hoàn.
- Kiểm toán: **BCTC 2025 Deloitte chấp nhận toàn phần, không có đoạn nhấn mạnh** [KT25 tr.4]. LNST kiểm toán 1.961,8 so với chưa kiểm toán ~1.917 (+2,3%).
  - BCTC soát xét 6T/2026: chưa đọc trang kết luận (scan).
  - Bẫy trình bày nêu ở §2 (phân loại lại 102,9 tỷ; trình bày lại Q2/25; hai con số trích quỹ KH&CN 2025).
- Room ngoại: chưa xác minh.

## 8. Chưa xác minh (ưu tiên)
1. **Năm hết ưu đãi thuế TNDN** (ảnh hưởng 1.313 đ/cp).
2. Nội dung "chi phí tài chính khác" 71,2 tỷ Q3/26; khoản 102,9 tỷ phân loại lại vào dòng GVHB nào.
3. Công thức giá khí gốc: sàn/trần, take-or-pay, hệ số Petronas 2027, phần LNG. Hiện chỉ có nguồn CTCK.
4. Sản lượng, giá bán theo quý (báo chí lệch: H1 XK 351 kt hay 385 kt). Định mức khí MMBtu/t.
5. Kết luận soát xét 6T/2026; kết quả ĐHĐCĐ bất thường 23/9; tiến độ thu hồi 332 tỷ; room ngoại.
6. Độ dốc hồi quy LNST–biên chỉ có 5 điểm, phần dư lớn ⇒ nên thay bằng mô hình sản lượng × (giá − khí) khi có định mức khí.
7. Giá tham chiếu 33.000 lấy từ BQ, chưa đối chiếu DNSE.

## 9. Sản phẩm
- `calc/quarterly.py` (+`_out`): bóc theo quý.
- `calc/model.py` (+`_out`): định giá mù giá.
- `calc/LOCK_md5.txt`.
- `calc/compare_px.py`, `calc/px_liq.sql`, `calc/comps.sql`: chạy sau khoá.
- `png/`: ảnh trang BCTC.
- `src/web/`: NQ ĐHĐCĐ, KT 2025, soát xét 6T, tài liệu CTCK. Tài liệu CTCK có giá mục tiêu, KHÔNG dùng.
- Chưa làm: fundamental-skeptic, báo cáo cho nhà đầu tư, sổ `dd_price_zones.json` (chờ skeptic).
