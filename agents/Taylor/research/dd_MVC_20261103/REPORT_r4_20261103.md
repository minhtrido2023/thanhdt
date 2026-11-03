# DD — MVC (CTCP Vật liệu và Xây dựng Bình Dương, UPCOM) · bản r3 (nội bộ) · as-of 03/11/2026 · job `Taylor_20261103_093502`

> NGHIÊN CỨU READ-ONLY. Không phải khuyến nghị mua/bán. User quyết. Email: **CHƯA gửi** (chờ user báo "gửi email").
> Bản r1/r2 (job `Taylor_20261103_082601`, `_085129`) giữ nguyên làm tham chiếu nội bộ: `REPORT_r2_20261103.md` — mọi phần BCTC/ngành/quản trị (§1–§6 của bản đó) vẫn hiệu lực; bản r3 này thay **toàn bộ phần định giá** (§7 cũ).
> Đầu vào phản biện: `SKEPTIC2_20261103.md` (+ `calc/bridge.py`, `calc/tot_stack.py` của skeptic). Chỉ đạo user 03/11 16:18: dựa DD NNC; mù giá; nghiên cứu kỹ nghịch lý "giá đá đi ngang ⇒ MVC < phần góp NNC"; đầu ra phải hành động được.
> Đơn vị: tỷ đồng; đ/cp = tỷ × 10 (100 tr cp). Giả định tự đặt gắn **(ước lượng)**.

## 0. Mù giá — thứ tự thời gian (mtime ICT, `r3/calc/`; md5 `r3/calc/LOCK_md5_r3.txt`)
| Giờ (03/11) | Bước |
|---|---|
| 16:37:17–16:37:34 | `price_path.py` + `gpm_bq.csv` (BQ `ticker_financial` GPM_P0/Revenue_P0 — không cột giá/PE) → `price_path_out.txt` |
| 16:38:49 | `valuation_base.py` = bản đông lạnh `calc/valuation.py` r1/r2 (md5 d3fb9637…) |
| 16:40:33–16:40:34 | `model_r3.py` → `model_r3_out.txt/.json`, `grid_r3.csv` (ngưỡng ĐĂNG KÝ TRƯỚC trong docstring) |
| 16:41:10 | **KHOÁ** `LOCK_md5_r3.txt` (11 file) |
| 16:41:28 | MỚI đọc giá: `px_0211.csv` (tav2_bq.ticker MVC 02/11 Close 13.700) |
| 16:41:58–16:42:07 | `compare_r3.py` → `compare_r3_out.txt`; md5 sau-khoá ghi phần dưới của LOCK; `md5sum -c` 11 file trước OK |
| 16:45:01 | `post_lock_combo.py` (tổ hợp điều kiện đổi nhận định, cùng mô hình, không sửa tham số) |

Giới hạn mù giá (thẳng thắn): giá 13.700 có trong BRIEF r1 (08:25Z) và trong bộ nhớ phiên ⇒ r3 không chứng minh được "chưa từng thấy giá"; chứng minh được: (a) không truy vấn giá MVC/NNC trước 16:41:28, (b) tham số mới r3 (đường giá, trọng số) suy từ GPM/CPI có file, (c) ngưỡng đăng ký trước khi chạy. Kênh neo kế thừa từ NNC-DD (đường giá cơ sở 380→300 của FPTS) vẫn còn — r3 giữ mức, nhưng kiểm bằng dữ liệu độc lập (§2) và gán đúng nhãn.

## 1. Kết luận r3
- **Tâm (giá trị kỳ vọng) 20.181 đ/cp** — W kịch bản 25/50/20/5 × đường giá phẳng 10 / g2031 50 / thực 40; r 13%, holding 15%; hạng mục riêng MVC độc lập [`model_r3_out.txt` dòng 1].
- **Ngưỡng (lưới 243 bộ tham số, đăng ký trước):** [r4: thang mới — xem mục 8 (r4)] cũ: RẺ RÕ ≤ 15.261 · nghiêng rẻ 15.261–17.471 · **HỢP LÝ 17.471–22.946** · nghiêng đắt 22.946–25.383 · **ĐẮT ≥ 25.383**. Hiển thị NĐT: 15.300 / 17.500–22.900 / 25.400.
- **Dải theo kịch bản (49.152 ô có trọng số):** P10 8.291 · P25 11.434 · P50 16.201 · P75 25.451 · P90 39.975 — lệch phải; dùng đo rủi ro, không làm ngưỡng.
- **Sau khoá:** giá 13.700 = 0,68× tâm ⇒ **RẺ CÓ ĐIỀU KIỆN** (thang r4: 13.000–17.500; không còn "rẻ rõ"); 37% kết cục có trọng số < 13.700 [`compare_r3_out.txt`].
- So r2 (tâm 19.540, vùng 14.600–24.500 = phẳng…thực): tâm +641; vùng hẹp lại (P25–P75 rộng 5,5k thay 9,9k) và có ngưỡng hai đầu.

## 2. Nghịch lý "giá đá đi ngang ⇒ MVC < giá trị phần góp NNC" — trả lời bằng số
Cầu nối kịch bản cơ sở, hạng mục riêng ở mức cơ sở [`model_r3_out.txt` mục 1]:

| tỷ đồng | phẳng (stress) | g2031 | thực |
|---|---|---|---|
| A. Tân Lập | 556,1 | 692,0 | 884,0 |
| B1. Mỏ mới: PV vận hành | 620,1 | 869,8 | 1.134,7 |
| B2. Mỏ mới: PV capex còn phải chi (1.061,6) | −933,1 | −933,1 | −933,1 |
| B3. Mỏ mới: đất ĐÃ chi (CIP 431,9 — nằm trong nợ ròng) | −431,9 | −431,9 | −431,9 |
| **CHƯƠNG TRÌNH MỎ MỚI (B1+B2+B3)** | **−744,9** | **−495,2** | **−230,3** |
| BOT + gạch/xăng + Q4 + MCC/NHC/ICD + đất ở | 343,6 | 343,6 | 343,6 |
| Nợ ròng KHÔNG gồm đất mỏ (−116,6 + 431,9) | +315,3 | +315,3 | +315,3 |
| **= Phần trực tiếp** | 470,1 | 855,7 | 1.312,6 |
| Phần NNC trước holding · holding 15% | 553,5 · −83,0 | 669,7 · −100,5 | 801,9 · −120,3 |
| **Phần NNC (sau holding)** | 470,5 | 569,3 | 681,6 |
| **TỔNG MVC** | **940,6 (9.406 đ/cp)** | 1.424,9 (14.249) | 1.994,2 (19.942) |

- **TỔNG MVC < phần NNC: 0/12 ô** (4 kịch bản × 3 đường giá). Các mốc "phần góp NNC": sổ sách VCSH NNC × 9,659 tr cp = **289,0 tỷ** (BQ BVPS Q3/26 29.915 [`nnc_book.txt`]); giá trị mô hình 470,5 (phẳng cơ sở). Tổng MVC (940,6) lớn hơn cả hai.
- Điều đúng là **PHẦN TRỰC TIẾP < phần NNC** ở 4/12 ô: cơ sở-phẳng (470,1 < 470,5) và rất xấu ở cả 3 đường. Ở cơ sở-phẳng, nguyên nhân DUY NHẤT là chương trình mỏ mới −744,9 (= −313,0 tiến về phía trước + −431,9 đã chi); bỏ chương trình, phần trực tiếp = 1.215,0. Tân Lập (556,1) tự nó > phần NNC.
- **Huỷ >700 tỷ có hợp lý?** Chỉ xảy ra ở cơ sở-phẳng. (i) 431,9 là chi phí chìm — đã chi, không hồi lại trừ khi bán đất; (ii) phần còn kiểm soát được là −313: một ban điều hành duy lý không chi tiếp 1.062 tỷ khi biết giá danh nghĩa đi ngang vĩnh viễn — lựa chọn dừng (bán lại đất 30% = +129,6) đưa chương trình về −302,3; (iii) MVC + NNC (cùng chủ tịch, cùng cụm) đã đấu giá ⇒ ưu tiên bộc lộ: người trong ngành không kỳ vọng giá phẳng (có thể đặt cược sai — winner's curse — nên không coi là bằng chứng mạnh); (iv) chi phí cơ hội: 1.500 tỷ nếu không đầu tư sẽ nằm ở tiền gửi/trả nợ — đã phản ánh vì r 13% > lãi vay. ⇒ Mô hình giữ giả định "chạy theo NQ ĐHĐCĐ" ở cơ sở (thận trọng); độ nhạy "sàn dừng dự án mọi kịch bản" **+732**.
- Kết luận nghịch lý: là hệ quả của (giá phẳng vĩnh viễn) × (mỏ mới vẫn chạy) × (đất đã chi tính là mất), không phải "MVC < NNC". Giá phẳng vĩnh viễn là stress — §3.

## 3. Đường giá đá — dữ liệu độc lập, không dùng nhãn FPTS [`price_path_out.txt`]
Phương pháp: giá bán ngầm = (1−GPM_gốc)/(1−GPM_năm) × CPI (cpi_vn.py, bình quân năm), giả định chi phí đơn vị THỰC không đổi (ước lượng; mỏ xuống sâu ⇒ chi phí thực tăng ⇒ phép này đánh giá THẤP giá thực; nhưng chiều sai số tổng KHÔNG xác định: đòn bẩy vận hành, cơ cấu sản phẩm, 4 mã cùng vùng nên số mẫu độc lập ít). GPM gộp quý theo doanh thu.

| | NNC | KSB | DHA | VLB (gốc 2016) | MVC (gốc 2017) |
|---|---|---|---|---|---|
| GPM 2012 / 2019 / 2025 / 9T26 | 33,0 / 31,0 / 42,8 / 51,6% | 34,2 / 48,3 / 42,6 / 34,9% | 15,0 / 30,9 / 34,0 / 37,2% | 26,8(16) / 20,0 / 27,4 / 31,9% | 17,3(17) / 9,4 / 23,3 / 31,7% |
| Giá danh nghĩa ngầm 2025 (gốc=1) | 1,77 (4,5%/năm) | 1,74 (4,4%) | 1,95 (5,3%) | 1,33 (3,2%) | 1,38 |
| GPM 2025 NẾU giá danh nghĩa phẳng | −1,5% | 0,3% | −28,8% | 3,2% | −5,5% |

CPI 2012→2025 ×1,515 (3,25%/năm). Cửa sổ 4 năm (36, chồng lấp, 4 mã tương quan ⇒ N độc lập thực nhỏ): giá thực giảm bất kỳ 42%, ≥10% 8%, ≥15% 3%, ≥25% **0%**. Cửa sổ 8 năm giá danh nghĩa tăng ≤5%: **1/20**; trung vị +34%.
Mốc Bobby §3 (đọc MÙ): ≤2020 1x2 tại mỏ 140–150k/tấn → đầu 2026 177k (Đồng Nai cũ, ≈+20–25% danh nghĩa) và 230–240k (Bình Phước cũ) — cùng chiều. Giá Sở XD Đồng Nai theo quý: không có chuỗi (Bobby: "không đọc giá đá bằng một con số Sở công bố"; F2 P(Q2/27 > +7%)=0,30, ±7% 0,55, < −7% 0,15).
**Đỉnh hiện tại:** NNC 9T26 giá thực ngầm 1,39 = cao nhất chuỗi (TB 2012–25 ≈1,03 ⇒ +35%). Đỉnh cũ (đếm tay từ bảng): NNC 2017 1,15→2019 0,97 (−16%); NNC 2021 1,11→2022 0,85 (−23%, diesel); KSB 2019–20 1,27→2023 1,11 (−13%); DHA 2015 1,21→ đi ngang (−4%); VLB 2016→2019 (−8%) ⇒ **3/5 đỉnh giảm thực ≥10% trong 3–4 năm, 0/5 ≥25%**.

**Đường giá (áp lên mức kịch bản NNC_SCN theo tiền 2026):**
- **flat — STRESS 10%:** danh nghĩa phẳng mãi; giá thực cơ sở 2040 ≈0,55× 2026. 1/20 cửa sổ 8 năm từng gần phẳng, 0/36 cửa sổ 4 năm giảm thực ≥25% ⇒ tần suất thực nghiệm ≈5%; lấy 10% (gấp đôi) vì sóng cung mới 2027–28 là thật.
- **g2031 — 50%:** vách kịch bản, KHÔNG chuyển lạm phát tới 2030, +3%/năm từ 2031. Cơ sở: giá thực 2030 = 0,70×, 2031+ 0,75× 2026 — khớp hồi về TB thực 2012–25 của NNC (1,03/1,39 = 0,74×) ⇒ đường "hồi về trung bình lịch sử".
- **real — 40%:** mức kịch bản giữ giá trị thực từ 2026: cơ sở 2028–30 0,79×, 2031+ 0,84× — dừng trên TB lịch sử (lý do: tiền cấp quyền đấu giá R%, VĐ4 2027–28). Trọng số thấp hơn g2031 vì đỉnh 2026 cao bất thường.
- **Trọng số kịch bản W 25/50/20/5 giữ nguyên:** "tốt" ≈ không hồi về (2/5 đỉnh lịch sử giảm <10%: −4%, −8%) ⇒ 25–40%; lấy đầu thấp 25% vì cung đấu giá mới (gồm 2 mỏ MVC) đã công bố. Đối xứng: 15/60/20/5 −2.779; 35/50/10/5 +3.891.
- Nhãn đúng cho vách 2028 cơ sở: **giả định nhóm nghiên cứu, tham khảo kịch bản cung mới FPTS** (không phải Bobby — Bobby đặt trũng 2027, hồi 2028).

## 4. Áp M1–M7 (SKEPTIC2) — hiệu ứng đo [`model_r3_out.txt` mục 3–4]
| # | Sửa | Kết quả r3 |
|---|---|---|
| Đường giá | phẳng/thực 50:50 → 10/50/40 | 19.540 → 20.796 (+1.256) |
| Bỏ xếp chồng | hạng mục riêng MVC độc lập với kịch bản NNC | 20.796 → **20.181** (−616). Phương án skeptic "mọi mục riêng ở 'tốt' = cơ sở": −1.338 (đó là bỏ upside, không phải bỏ xếp chồng — nêu cả hai) |
| M1 | REL 0,80/0,95/1,00 kèm COST_A, COST_B hiệu chỉnh giữ biên 2026 | +710 / −795 / −1.283 (r2 báo sai −3.300/+3.900) |
| M2 | Mỏ mới trễ 1 năm MỌI kịch bản: vách KHÔNG lùi −864; vách + sản lượng + mốc lạm phát lùi −683. Chỉ cơ sở (định nghĩa skeptic): −422 / −198 | Dùng −683 (lùi đồng bộ) |
| M3 | Tornado 2 chiều đủ | capex ±30% ∓2.184 · chi phí mỏ mới 105k/165k +2.341/−2.334 · Tân Lập ±15% +1.487/−1.456 · holding 0/30% +1.179/−1.162 · sàn dừng mọi kb +732 · r 11/15% +2.741/−2.270 · PW 25/50/25 −1.438, 5/35/60 +1.281 · GP Tân Lập 2035/2045 −1.601/+1.260 · đất ở 0 −1.560 |
| M4 | Tiêu đề bỏ "cơ sở phẳng < giá" | phẳng = stress; cơ sở g2031 = 14.605 (kỳ vọng hạng mục riêng) / 14.249 (hạng mục riêng ở cơ sở) |
| M5 | fig_10 tách đất mỏ | đã tách: chương trình mỏ mới −4.952 đ/cp (g2031), nợ ròng ex đất +3.153 |
| M6 | Công bố xếp chồng lạc quan | xem dòng "Bỏ xếp chồng" |
| M7 | r 13% cho dự án vay 75% không tính lá chắn thuế | công bố trong báo cáo NĐT §5 (r 13% không tính lá chắn thuế: chiều thận trọng cho phần này); r 11% chỉ là cận |
| Chưa trong mô hình | Cụm công nghiệp ≤500 tỷ (thu hồi 70/50%) | −1.300 / −2.100 (từ r2 `calc/valuation_v2_out.txt`) |

## 5. NNC nhất quán (D1) — đầu vào cho MVC [`model_r3_out.txt` mục 5]
V_NNC = N_ex + 0,103·V_MVC, V_MVC từ mô hình (không giá thị trường). Kỳ vọng W 25/50/20/5: **phẳng 62.220 · g2031 73.337 · thực 86.914 đ/cp NNC; tâm PW 10/50/40 = 77.656.** (Skeptic với xếp chồng: 61.352 / 85.516.) Đã ghi vào `../dd_NNC_20261030/REPORT.md` (mục bổ sung 03/11). D2 sửa nhãn tại NNC REPORT dòng bảng kịch bản + investor_report_v2 bảng kịch bản; D4: Phụ lục E investor_report_v2 viết lại trung tính (bỏ bảng "người phản biện đã bắt"). KHÔNG dựng lại PDF NNC, KHÔNG gửi email NNC.

## 6. Ngưỡng hành động + điều làm vùng thu hẹp
| Vùng (đ/cp) | Nhận định | Đổi nhận định khi |
|---|---|---|
| ≤13.000 (r4; cũ 15.300 "rẻ rõ") | RẺ CÓ BIÊN AN TOÀN (P10 lưới mở rộng − cụm CN) · 13.000–17.500 RẺ CÓ ĐIỀU KIỆN | Lên: các mốc tích cực dưới. Xuống: tổ hợp tiêu cực đủ (tâm 13.864) |
| 17.500–22.900 | HỢP LÝ (P25–P75) | |
| ≥25.400 | ĐẮT (P90) | Chỉ hợp lý nếu tổ hợp tích cực (tâm 25.540–28.015) |

| Mốc · ngày | Đo gì | Tác động [`post_lock_combo_out.txt`, tornado] |
|---|---|---|
| BCTC Q4/26 · ≈20–30/01/2027 | Biên gộp ≥35% / <28% | W 35/50/10/5 +3.891 / W 15/60/20/5 −2.779 |
| ĐHĐCĐ 2027 + BCTN 2026 · ≈04/2027 | Cơ cấu 1.500 tỷ; hạn GP Tân Lập | capex ∓2.184; GP 2045 +1.260 / 2035 −1.601 |
| GP khai thác mỏ mới · 30/06/2027 | Có/không | trễ 1 năm −683 |
| Giá Sở XD Đồng Nai Q2/27 vs Q3/26 · ≈31/08/2027 | > +7% / < −7% | PW 5/35/60 +1.281 / PW 25/50/25 −1.438 |
| Tổ hợp | Tiêu cực đủ (W15 + PW25 + capex +30%) **13.864**; nhẹ 16.048 · Tích cực đủ (W35 + PW5/35/60 + capex −30%) **28.015**; nhẹ 25.540 | |

## 7. So với giá (SAU khoá) [`compare_r3_out.txt`]
Giá 02/11/2026 13.700 (tav2_bq.ticker Close = Price, KL 71.700) = 0,68× tâm ⇒ **RẺ CÓ ĐIỀU KIỆN** (r4). Định giá ngược: (a) cả 100% đường phẳng vẫn 14.227 > giá ⇒ thị trường không chỉ định giá "giá đá phẳng"; (b) giữ cơ sở 50/rất xấu 5: tốt 8% / xấu 37%; (e) bỏ hẳn kịch bản tốt: xấu 16% + rất xấu 5% = tiêu cực 21%; (d) r hàm ý ≈20% (r 20% → 13.714). ⇒ Giá hiện tại hàm ý gần như KHÔNG có kịch bản tốt, hoặc chi phí vốn ~20% (chiết khấu thanh khoản/quản trị/UPCOM). Thanh khoản ADV trung vị 0,19 tỷ/phiên (r2 `calc/px_median_out.txt`) — một lý do hợp lệ cho chiết khấu.

## 8 (r4). Thang ngưỡng có điều kiện — job `Taylor_20261103_095718` (skeptic vòng 3: CONFIRMED medium)
Tính trên lưới mở rộng 2.187 bộ (243 tham số × W {15/60/20/5, 25/50/20/5, 35/50/10/5} × PW {25/50/25, 10/50/40, 5/35/60}) — `r4/ext_r4.py` → `r4/ext_r4_out.txt` (tái lập số skeptic: P10 14.333; cụm CN: 13.033):
| | P10 | P25 | P50 | P75 | P90 |
|---|---|---|---|---|---|
| Lưới mở rộng 2.187 | 14.333 | 17.096 | 20.418 | 23.952 | 27.344 |
| trừ cụm CN 500 tỷ thu hồi 70% (−1.300) | **13.033** | 15.796 | | | |
| trừ cụm CN thu hồi 50% (−2.100) | 12.233 | 14.996 | | | |
Tỷ trọng kết cục < 13.700: 7,2% (lưới mở rộng) · 12,8% (cụm CN 70%) · 16,8% (cụm CN 50%). Kịch bản tốt = 48,2% giá trị kỳ vọng (22,1% riêng ô tốt × giá thực).
**Thang chốt:** RẺ CÓ BIÊN AN TOÀN ≤13.000 (≈P10 lưới mở rộng + cụm CN 70%) · RẺ CÓ ĐIỀU KIỆN 13.000–17.500 · HỢP LÝ 17.500–22.900 (P25–P75 lưới 243, giữ nguyên tâm 20.181) · ĐẮT ≥25.400 (P90 lưới 243). Giá 13.700 nằm trong vùng ĐIỀU KIỆN, cao hơn ngưỡng biên an toàn ≈5%.
**Hai điều kiện của nhãn "rẻ có điều kiện":** (1) P(kịch bản tốt) ≥ ≈10% (giá hàm ý ≈8% vs 25% giả định); (2) vốn mỏ mới ≤1.500 tỷ và cụm công nghiệp NPV ≈ 0.
Đính chính khác: "2/5 không giảm" → "2/5 giảm <10% (−4%, −8%)"; "nghiêng thận trọng" → "chiều sai số không xác định". Thân báo cáo NĐT 1.811 từ (không bảng/hình/phụ lục; cũ 2.211).

## Phụ lục E (nội bộ) — áp đính chính SKEPTIC2 vào r3
| Mục skeptic | Trạng thái | Bằng chứng |
|---|---|---|
| A cầu nối + tách đất | Áp, tái lập khớp số skeptic (556,1 / −313,0 / 343,6 / −116,6 / 470,5 / 940,6) | §2; `model_r3_out.txt` mục 1 |
| A trễ 1 năm −470→+86 | Áp có điều chỉnh: định nghĩa skeptic (chỉ cơ sở, lùi vách) đo được −198 trên tâm r3 (khác +86 vì r3 lùi cả mốc lạm phát g2031 và trọng số đường giá khác); báo NĐT −683 (mọi kịch bản) | §4 M2 |
| B holding/sàn/Ke/tornado/xếp chồng/option đất | Áp: tornado 2 chiều, công bố | §4 |
| B kênh neo NNC-DD | Thừa nhận; kiểm mức 380→300 bằng GPM (khớp hồi về TB thực lịch sử, §3) | §0, §3 |
| C chân phẳng = stress, g2031, lưới 81 ô | Áp; lưới mở rộng 243 ô (thêm REL hiệu chỉnh) — P10 15.261 / P90 25.383 (skeptic 81 ô: 15.400 / 23.500) | §1 |
| D1 NNC hệ phương trình | Áp; số r3 §5 | §5 |
| D2 nhãn | Sửa tại NNC REPORT + investor_report_v2 | git diff dd_NNC_20261030 |
| D3 "cận dưới 59k" là stress | Ghi nhận; NNC đã bổ sung đoạn "phẳng là STRESS" | NNC REPORT mục bổ sung |
| D4 "bản trước" | Viết lại Phụ lục E investor_report_v2 trung tính | grep 0 dòng |
| M1–M7 | Áp hết | §4 |

## Tệp
`r3/calc/`: price_path.py · gpm.sql · gpm_bq.csv · price_path_out.txt · price_path_implied.csv · valuation_base.py · model_r3.py · model_r3_out.{txt,json} · grid_r3.csv · nnc_book.txt · LOCK_md5_r3.txt · px_0211.csv · compare_r3.py · compare_r3_out.txt · post_lock_combo.py · post_lock_combo_out.txt.
Báo cáo NĐT (đè): `investor_report/MVC_DD_investor_report_20261103.{md,pdf,html}`, `EMAIL_SUBJECT.txt`, `SELFCHECK.md`, `figs/` (mới: fig_14_price_path).
