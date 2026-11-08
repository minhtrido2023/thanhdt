> **QUY ƯỚC CUỐI (user chốt 08/11/2026 10:50 ICT):** KHÔNG áp luật 3c chặt. Moat chỉ được THÊM vào định giá khi bền; NARROW/NONE = không thưởng nhưng KHÔNG trừ. **Headline = mô hình cơ sở hiện hành (tâm 22.366 theo báo cáo gốc)**; mọi 'bản chặt-3c / headline mới / chờ duyệt' bên dưới chỉ còn là **độ nhạy rủi ro** ('nếu về trung bình ngành'), KHÔNG phải kết luận định giá. Các sửa lỗi dữ liệu/công thức/peer trong tài liệu này vẫn có hiệu lực. Không mã nào trong 20 mã có moat bền ⇒ không thêm tham số moat.
>
> **Ghi chú đồng bộ r3 (08/11. sau skeptic cuối CONFIRMED):** tâm hiện hành = **23.099** · P10 13.799 · P50 23.982 · P90 30.338 (sau CK 5 tỷ. giá 18.000 ngày 06/11. 20.5% trọng số kết cục dưới giá. TRONG vùng) theo `REPORT_r3.md`. 22.366 là tâm r2. r3 đối xứng trọng số cước (0.275/0.45/0.275). bỏ +30% NPV tàu nhánh tốt. chiết khấu FSO = r. cộng vốn lưu động ròng +37.0 tỷ; WARNING phụ lục FSO 2036 chưa ký. Các bảng dưới (22.366. A+CAP 20.356. 30.6% dưới giá) là khung r2. chỉ còn là lịch sử/độ nhạy.

# PVP — ADDENDUM 5F (bước 3c) · 08/11/2026 · job `Taylor_20261107_172011` · **vòng sửa sau skeptic: `Taylor_20261108_024220`** (bản trước: `ADDENDUM_5F_r1.md`)
> Bổ sung cho `REPORT_r2.md` (KHÔNG sửa REPORT/SUMMARY cũ). Số: `calc/5f/addendum_5f_out.json` + `calc/5f/addendum_5f_ext_out.json`
> (import `model_r2.py` nguyên trạng ⇒ quy ước chiết khấu cuối năm, năm 1 mũ 1, r=13,5% y hệt r2 — bài học H). BQ `tav2_bq.ticker_financial`
> truy vấn 08/11/2026. 5F = phán đoán LLM non-point-in-time ⇒ chỉ cho DD sống, KHÔNG vào backtest. Calc chạy lại 2 lần trùng byte 08/11 (md5 `acefdadf…` / `33a2a1c8…`), số không đổi so r1 — vòng này chỉ đổi QUY ƯỚC headline + diễn giải.

## 1. Vị thế & lợi thế cạnh tranh (5F) — LÀM MỚI
**Tái dùng hay làm mới:** làm mới — `data/moat_tags.csv` không có dòng PVP; `kb/projects/pvp-dd-20261029.md` + DD 29/10 không có audit 5F.
**Loại hình:** vận tải tàu dầu/hoá phẩm + 1 FSO (Đại Hùng Queen), thâm dụng tài sản, chu kỳ cước toàn cầu; công ty con PVTrans (64,92%).

| Lực | Đánh giá | Bằng chứng (nguồn) |
|---|---|---|
| Cạnh tranh nội ngành | CAO — price-taker cước quốc tế | cước theo BDTI (Bobby); peer nội địa cùng mảng PVT (EBITDA TTM 4.914 tỷ vs PVP 700), VTO [BQ 2026Q3] |
| Gia nhập mới | DỄ — rào cản chỉ là vốn | tàu mua được thị trường thứ cấp (56,3 tr USD/Aframax, báo cáo khả thi [AGM p44]); ROIC5Y peer ~8% < Ke ⇒ không có tô kinh tế để bảo vệ |
| Quyền lực người mua | CAO, tập trung | bên liên quan **63,3% DT 6T** = tổng 865,4/1.367,3 tỷ [H1 p38, theo DD 29/10]; riêng 3 bên nêu tên (PVTrans 555,7 / BSR 199,5 / LPG VN 94,5) = 849,7 = **62,1%**, 15,7 tỷ còn lại là bên liên quan khác; giá FSO đã bị điều chỉnh (biên bản 03/06/2025), cam kết/năm giảm 415,8 → 135,7 (7/27) → 37,3 (7/31) [H1 p34] |
| Quyền lực nhà cung cấp | TRUNG BÌNH–CAO ở đỉnh chu kỳ | mua tàu đỉnh cước: IRR dự án 7,67% < IRRmin 11% tự đặt [AGM p44], < Ke 13,5% |
| Sản phẩm thay thế | TRUNG BÌNH | đường ống/hãng khác cho tuyến nội địa — cần kiểm chứng, không có số |
| **Lực thứ 6 (đồng hồ cắt hào)** | CÓ | (a) FSO step-down 2027/2031 theo lịch cam kết; (b) Apollo ~21 tuổi (báo chí, cần kiểm chứng) ⇒ buộc tái đầu tư; (c) cước đang ở đỉnh (Bobby) |

**Ba điều kiện bền (bài học B — cả hai phía ROIC, ROE riêng):**
| | PVP | Peer TV (PVT/VTO/GSP/VIP/VOS) trung vị · TB | Ke |
|---|---|---|---|
| ROIC5Y / ROIC_Min5Y (2026Q3) | 8,8% / 3,5% | 8,2% · 8,0% / — | 13,5% |
| ROIC10Y / ROIC_Min10Y | 7,7% / 3,5% | — | |
| ROIC5Y đỉnh 10 năm (2024Q4) | 9,0% | | |
| ROE5Y / ROE_Min5Y (riêng, không thay ROIC) | 11,9% / 10,6% | | |
| GPM cả năm (dòng Q4 GPM_P0, TTM — bài học A) 2025 / TB 2016–25 | 12,1% / 14,3% | 14,7% · 15,2% (2025) | |
- (i) siêu ngạch nhiều chu kỳ: **KHÔNG** — mọi cửa sổ ROIC (kể cả cửa sổ thuận nhất 9,0%) < Ke; ngang trung vị peer. (ii) cơ chế rào cản: **không gọi tên được** (nhu cầu nội bộ tập đoàn là *cầu bị giữ*, không phải quyền định giá — bằng chứng: giá FSO bị cắt). (iii) **có đồng hồ**.
- Peer: nội địa; đối thủ trực tiếp mảng tàu dầu = PVT, VTO; GSP (LPG), VIP/VOS (hàng rời/hỗn hợp) chỉ cùng ngành rộng — giữ cho đủ cỡ mẫu; bỏ VOS/VIP: trung vị ROIC5Y = 8,2% (PVT/VTO/GSP), kết luận không đổi.
- **moat_tier = NONE · moat_type = NONE · rủi ro số 1:** tái đầu tư ở đỉnh chu kỳ (mua tàu 116 tr USD ≈ 1,55× vốn hoá, IRR < hurdle) trong khi khách hàng chính là công ty mẹ định giá cước.

## 2. Moat trong mô hình
Luật 3c cho NONE ⇒ không thưởng: **RONIC = Ke** (NPV tàu mới = 0) và **biên/EBITDA về TB chu kỳ**. Rà r2 (bài học C) — **KHÔNG nhất quán** ở 2 kênh:
1. EBITDA đội tàu TB trọng số lưới **382,5** tỷ > TB chu kỳ **345,7** (proxy: EBITDA_P0 TTM dòng Q4 2016–25 TB 431 / 2026Q3 700 = 0,616 × 9T năm hoá 561; k = 0,904). Neo TB của chính PVP vì GPM TB 10 năm 14,3% ≈ trung vị peer 14,7% (TB 15,2%) ⇒ chọn neo ngành không đổi hướng.
   **Kiểm cơ sở proxy 431 (vòng sửa):** proxy là EBITDA TỔNG công ty, áp lên đội tàu HIỆN TẠI. Hai sai lệch ngược chiều, KHÔNG đo được độ lớn ròng:
   (a) *Đội tàu trong cửa sổ có thể nhỏ hơn* ⇒ 431 hiểu thấp TB chu kỳ ⇒ A **phạt quá**. Bằng chứng (suy luận, không có số tàu theo năm): hao mòn lũy kế/khấu hao năm cho Pacific Era ~3,3 năm (vào sổ ~2023), Pacific Pride ~2 năm (~cuối 2024) [Q3 TM, calc DD 29/10]; TSCĐ hàm ý BQ (DT 4Q / FAssetTurn) tăng 1.280 → 1.637 tỷ 2023Q4→2024Q4. Không rõ 2016–22 có tàu thay thế đã bán hay không.
   (b) *FSO là cấu phần ổn định nằm trong cả tử lẫn mẫu* (FSO NG 1.874, đã khấu hao ~10 năm ⇒ có mặt suốt cửa sổ) ⇒ tỷ lệ tổng (F+a)/(F+b) > tỷ lệ đội tàu a/b ⇒ A **phạt thiếu**.
   ⇒ Coi A là ước lượng thô; cận trên khi bỏ A = **CAP riêng 21.505** (bảng §3). Cả hai bản đều TRONG — nhãn không phụ thuộc proxy.
2. NPV tàu mới lệch khỏi 0: −30% (xấu, w 0,40) / 0 / **+30% (tốt, w 0,15)** ⇒ kỳ vọng −7,5%. Nhánh +30% là RONIC>Ke (thưởng không có cơ sở moat) ⇒ **gỡ**. Nhánh −30% là RONIC<Ke có cơ sở QUAN SÁT ĐƯỢC (IRR dự án 7,67% < hurdle 11% của chính công ty, ĐHCĐ [AGM p44]) ⇒ **giữ**: luật 3c chỉ gỡ phần THƯỞNG, không gỡ kịch bản giảm có cơ sở (luật 03/11). Đối xứng hoá về 0 ở cả hai phía là **đảo ngược 3c** (NONE lại đáng giá hơn r2, +1.436 từ việc xoá nhánh xấu).
Không có terminal/Gordon (niên kim 4–8 năm) ⇒ không có kênh RONIC terminal; giảm trừ pháp lý: không có (không vụ án) ⇒ không đếm đôi.

## 3. Bảng độ nhạy (sau CK 5 tỷ 2,00%; giá 04/11 18.400)
| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| WIDE giả định (NPV tàu +20 điểm mọi nhánh; KHÔNG có bằng chứng) | 26.194 | 18.022 | 26.105 | 36.688 | 14,7% | TRONG |
| Hiện hành r2 (biên trên TB chu kỳ + nhánh NPV +30%; không có tier ngầm — NARROW cũng không được thưởng, = NONE theo 3c) | 22.366 | 12.702 | 22.377 | 32.834 | 30,6% | TRONG |
| Chỉ EBITDA→TB chu kỳ (A) | 21.217 | 11.796 | 21.303 | 31.428 | 33,2% | TRONG |
| Chỉ NPV tàu = 0 đối xứng (B) — loại, xoá nhánh có cơ sở | 23.802 | 19.638 | 23.506 | 27.955 | 3,0% | DƯỚI |
| CAP riêng (chỉ cắt +30% NPV; giữ biên r2) — cận trên nếu proxy A không đứng | 21.505 | 12.702 | 22.377 | 27.955 | 30,6% | TRONG |
| **NONE CHẶT-3C = A+CAP (EBITDA→TB chu kỳ + cắt CHỈ chiều lên NPV, giữ −30% có cơ sở) — HEADLINE** | **20.356** | **11.796** | **21.303** | **26.471** | **33,2%** | **TRONG** |
| Đối xứng (A+B) — loại (đảo ngược 3c); chỉ để đối chiếu | 22.653 | 18.917 | 22.444 | 26.471 | 4,0% | DƯỚI (biên 2,7% dưới P10) |
| Cỡ sleeve 40 tr (CK 0,18%): A+CAP (headline) / r2 / đối xứng (loại) | 20.734 / 22.782 / 23.073 | 12.016 / 12.937 / 19.268 | | | 33,2 / 29,8 / 4,0% | TRONG / TRONG / DƯỚI |

Tách phần chênh headline (tâm, so r2 22.366): biên→TB chu kỳ **−1.149**; cắt nhánh NPV +30% **−861** (21.505−22.366); cộng **−2.010** = 20.356 (cộng tính đúng). P10 12.702 → 11.796 (chỉ do A); P90 32.834 → 26.471.
Bản đối xứng (loại): +1.436 từ NPV về 0 hai phía ⇒ P10 nhảy lên 18.917 hoàn toàn nhờ xoá đuôi −30% — đó là nguồn duy nhất của nhãn DƯỚI. **Nhãn DƯỚI chỉ tồn tại ở quy ước đối xứng, biên 2,7%** (giá 18.400 dưới P10 18.917).

## 4. Thay đổi so với báo cáo hiện hành
Mô hình **có lệch luật 3c** (không ghi "nhất quán"): r2 thưởng ở 2 kênh (biên trên TB chu kỳ; nhánh NPV +30%). Bản chặt-3c đúng = **A+CAP: tâm 22.366 → 20.356 (−9,0%), P10 12.702 → 11.796, P90 32.834 → 26.471, 33,2% trọng số dưới giá ⇒ nhãn TRONG giữ nguyên** (cả cỡ 5 tỷ lẫn 40 tr). Nếu proxy chu kỳ A không đứng (§2 mục 1), cận trên là CAP riêng 21.505, vẫn TRONG. r1 đặt bản đối xứng làm headline và ghi đổi nhãn sang DƯỚI — **sai**: đối xứng hoá xoá kịch bản giảm có cơ sở quan sát được (IRR 7,67% < hurdle 11%), làm NONE đáng giá hơn r2 (+287 tâm, P10 +6.215) — ngược mục đích 3c. Không tự ghi dd_price_zones/SUMMARY; không đụng candidate/plan/lệnh.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
`PVP,NONE,NONE,L,"Tanker/FSO price-taker (ROIC5Y 8.8%/Min5Y 3.5% < Ke 13.5%, ~peer median 8.2%); 63% revenue related-party (PVTrans/BSR) with parent-set FSO rate stepping down 2027/2031; #1 risk = buying 116m USD of tankers at freight peak with project IRR 7.67% < own 11% hurdle",2026-11-08,5f,N`
(entry = L: ngành vận tải tàu dầu kém hấp dẫn cấu trúc — price-taker, rào cản chỉ là vốn; moat_upgrade = N.)
