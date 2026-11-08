# PVP — ADDENDUM 5F (bước 3c) · 08/11/2026 · job `Taylor_20261107_172011` (resume của `_131638`/`_140014`)
> Bổ sung cho `REPORT_r2.md` (KHÔNG sửa REPORT/SUMMARY cũ). Số: `calc/5f/addendum_5f_out.json` + `calc/5f/addendum_5f_ext_out.json`
> (import `model_r2.py` nguyên trạng ⇒ quy ước chiết khấu cuối năm, năm 1 mũ 1, r=13,5% y hệt r2 — bài học H). BQ `tav2_bq.ticker_financial`
> truy vấn 08/11/2026. 5F = phán đoán LLM non-point-in-time ⇒ chỉ cho DD sống, KHÔNG vào backtest. Chưa qua fundamental-skeptic.

## 1. Vị thế & lợi thế cạnh tranh (5F) — LÀM MỚI
**Tái dùng hay làm mới:** làm mới — `data/moat_tags.csv` không có dòng PVP; `kb/projects/pvp-dd-20261029.md` + DD 29/10 không có audit 5F.
**Loại hình:** vận tải tàu dầu/hoá phẩm + 1 FSO (Đại Hùng Queen), thâm dụng tài sản, chu kỳ cước toàn cầu; công ty con PVTrans (64,92%).

| Lực | Đánh giá | Bằng chứng (nguồn) |
|---|---|---|
| Cạnh tranh nội ngành | CAO — price-taker cước quốc tế | cước theo BDTI (Bobby); peer nội địa cùng mảng PVT (EBITDA TTM 4.914 tỷ vs PVP 700), VTO [BQ 2026Q3] |
| Gia nhập mới | DỄ — rào cản chỉ là vốn | tàu mua được thị trường thứ cấp (56,3 tr USD/Aframax, báo cáo khả thi [AGM p44]); ROIC5Y peer ~8% < Ke ⇒ không có tô kinh tế để bảo vệ |
| Quyền lực người mua | CAO, tập trung | bên liên quan **63,3% DT 6T** (PVTrans 555,7 / BSR 199,5 / LPG VN 94,5 tỷ) [H1 p38]; giá FSO đã bị điều chỉnh (biên bản 03/06/2025), cam kết/năm giảm 415,8 → 135,7 (7/27) → 37,3 (7/31) [H1 p34] |
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
1. EBITDA đội tàu TB trọng số lưới **382,5** tỷ > TB chu kỳ **345,7** (proxy: EBITDA_P0 TTM dòng Q4 2016–25 TB 431 / 2026Q3 700 = 0,616 × 9T năm hoá 561; k = 0,904). Neo TB của chính PVP vì GPM TB 10 năm 14,3% ≈ trung vị peer 14,7% (TB 15,2%) ⇒ chọn neo ngành không đổi hướng; proxy EBITDA (gồm FSO) — cần kiểm chứng bằng EBITDA đội tàu tách riêng.
2. NPV tàu mới lệch khỏi 0: −30% (xấu, w 0,40) / 0 / **+30% (tốt, w 0,15)** ⇒ kỳ vọng −7,5%. Nhánh +30% là RONIC>Ke (thưởng không có cơ sở moat); nhánh −30% là RONIC<Ke có bằng chứng (IRR 7,67% < 11%).
Không có terminal/Gordon (niên kim 4–8 năm) ⇒ không có kênh RONIC terminal; giảm trừ pháp lý: không có (không vụ án) ⇒ không đếm đôi.

## 3. Bảng độ nhạy (sau CK 5 tỷ 2,00%; giá 04/11 18.400)
| Biến thể | Tâm | P10 | P50 | P90 | % dưới giá | Nhãn |
|---|---|---|---|---|---|---|
| WIDE giả định (NPV tàu +20 điểm mọi nhánh; KHÔNG có bằng chứng) | 26.194 | 18.022 | 26.105 | 36.688 | 14,7% | TRONG |
| Hiện hành r2 (≈ NARROW ngầm) | 22.366 | 12.702 | 22.377 | 32.834 | 30,6% | TRONG |
| Chỉ EBITDA→TB chu kỳ (A) | 21.217 | 11.796 | 21.303 | 31.428 | 33,2% | TRONG |
| Chỉ NPV tàu = 0 đối xứng (B) | 23.802 | 19.638 | 23.506 | 27.955 | 3,0% | DƯỚI |
| **NONE CHẶT-3C đối xứng (A+B) — headline, quy ước chờ Mike/user** | **22.653** | **18.917** | **22.444** | **26.471** | **4,0%** | **DƯỚI (ranh giới: giá thấp hơn P10 2,7%)** |
| NONE CAP (A + cắt CHỈ chiều lên NPV, giữ −30% có bằng chứng) | 20.356 | 11.796 | 21.303 | 26.471 | 33,2% | TRONG |
| Cỡ sleeve 40 tr (CK 0,18%): CHẶT-3C / CAP / r2 | 23.073 / 20.734 / 22.782 | 19.268 / 12.016 / 12.937 | | | 4,0 / 33,2 / 29,8% | DƯỚI / TRONG / TRONG |

Tách phần chênh (tâm, so r2): biên→TB chu kỳ **−1.149**; NPV đối xứng về 0 **+1.436** (bỏ cả đuôi −30% w 0,40 lẫn +30% w 0,15); cộng **+287**. P10 nhảy 12.702 → 18.917 hoàn toàn do bỏ đuôi NPV −30% + mua cả hai.

## 4. Thay đổi so với báo cáo hiện hành
Mô hình **có lệch luật 3c** (không ghi "nhất quán"). Bản chặt-3c đối xứng gần như giữ tâm (22.366 → 22.653, +1,3%) nhưng thu hẹp mạnh phân phối và **đổi nhãn TRONG → DƯỚI ở mức ranh giới** (cả cỡ 5 tỷ lẫn 40 tr). **Ý kiến Taylor (đề xuất, chờ Mike):** đối xứng hoá xoá mất bằng chứng IRR dự án < hurdle — đó là RONIC<Ke quan sát được, không phải "thưởng moat"; bản CAP (20.356, TRONG, P90 32.834 → 26.471) mô tả rủi ro thật sát hơn. Hai bản đều cắt P90 (bỏ +30% NPV). Không tự ghi dd_price_zones/SUMMARY; không đụng candidate/plan/lệnh.

## 5. Đề xuất dòng `data/moat_tags.csv` (KHÔNG tự ghi)
`PVP,NONE,NONE,L,"Tanker/FSO price-taker (ROIC5Y 8.8%/Min5Y 3.5% < Ke 13.5%, ~peer median 8.2%); 63% revenue related-party (PVTrans/BSR) with parent-set FSO rate stepping down 2027/2031; #1 risk = buying 116m USD of tankers at freight peak with project IRR 7.67% < own 11% hurdle",2026-11-08,5f,N`
(entry = L: ngành vận tải tàu dầu kém hấp dẫn cấu trúc — price-taker, rào cản chỉ là vốn; moat_upgrade = N.)
