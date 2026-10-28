# Khung ngành — HOÁ CHẤT – PHÂN BÓN (26/10/2026)

> Khung bối cảnh cấp ngành, KHÔNG phải tín hiệu mua/bán. Nhãn: **[BQ]** `ticker_financial` (file
> `bq_fin_funnel_sectors_2025Q1_2026Q3.csv`) · **[WB]** World Bank CMO `data/{urea,dap,brent,rubber,caustic_soda}_monthly.csv`
> (CANONICAL, `kb/data_registry/feeds/commodity_wb_cmo.md`) · **[P4]** `data/phosphorus_weekly.csv` (SunSirs ngày) ·
> **[DD]** `research/dd_DDV_20261026/REPORT.md` (BCTC Q3 có ký) · **[W]** báo chí qua WebSearch 26/10, chưa mở bản gốc.
> ⚠️ `GPM_P0` của BQ KHÔNG phải biên gộp quý (DDV Q3/26: BQ 0,10 vs BCTC 3,7% — [DD] §1). Trang này dùng LNST là số chính.

**Mã funnel (10; 154 lượt)** — ICB 1357 (98): đạm urê **DCM, DPM, DHB** · lân/DAP **DDV** · phốt pho–hoá chất **DGC, PAT, CSV**.
ICB 1353 (56): **DRI, PHR** (cao su — chu kỳ khác, chỉ ghi chú) · **HII** (nhựa/thương mại).
Ba chu kỳ con đang đi NGƯỢC nhau — đọc "hoá chất" như một khối là sai.

## Pha chu kỳ theo nhánh
| Nhánh | Pha | Bằng chứng định lượng |
|---|---|---|
| **Urê (DCM, DPM, DHB)** | **Đỉnh đã qua — LN báo cáo còn trễ giá** | Urê TB quý [WB]: Q1/26 538 → **Q2/26 694** (đỉnh tháng 4: 857) → **Q3/26 399 USD/t** (−42% QoQ; T9 407,5). LNST gộp 3 mã [BQ]: Q1/26 1.417 tỷ, Q2/26 2.597 tỷ (DCM 1.068 +36%, DPM 906 +125%, DHB 623 vs 42). Q3/26 chưa có số trong BQ. Brent TB [WB] Q3/26 97 USD (T9 **116,8**) — giá khí đầu vào DCM/DPM gắn dầu FO ⇒ ép biên 2 đầu (mức gắn cụ thể **chưa đo**). |
| **DAP (DDV)** | **Biên sụp dù giá đầu ra đỉnh** | DAP [WB] 781→794→801 USD/t (T7→T9), cao nhiều năm; nhưng lưu huỳnh ~3,6x YoY, NH3 +74% (VNDirect qua [DD]) ⇒ biên gộp DDV 21,9% (Q3/25) → **3,7% (Q3/26)**; LNST 9,6 vs 221 tỷ (−96%), lõi kinh doanh −4,4 tỷ [DD][BQ]. |
| **Phốt pho vàng (DGC, PAT)** | **Đáy giữa — giá đi ngang thấp, DGC có rủi ro riêng** | P4 TB tháng [P4]: T6 33.357 → T7 27.006 → T8 27.986 → T9 27.847 → T10 (đến 23/10) 28.093 NDT/t. DGC LNST [BQ]: Q1/26 409 (−49%), Q2/26 380 (−55%). Mysteel dự báo dư cung P4 2026 ~45,5 kt [W]. |
| Cao su (DRI, PHR) | tăng giá | Cao su [WB] 2,75 USD/kg T9/26 vs 2,11 T9/25 (+30%); LNST gộp DRI+PHR+HII Q2/26 +244% YoY [BQ] (HII là thương mại, nhiễu). |

## Động lực 2–3 quý tới
1. Urê: Q3–Q4/26 là quý đầu LN phản ánh giá ~400 USD (vs ~540–690 H1) trong khi khí đầu vào theo dầu cao ⇒ LN đạm giảm mạnh YoY từ Q4/26 (ước lượng). Hạn ngạch XK urê TQ cấp lại từ T5/26 [W]; Vietcap hạ urê TĐ 2026 về 500 USD [W].
2. DAP: TQ hạn chế XK phosphate ít nhất tới T8–T9/26, có nguồn nói tới T4–T5/2027 [W] ⇒ giữ giá DAP cao; biên DDV phụ thuộc giá S hợp đồng — tồn kho NVL 617 tỷ mua giá đỉnh sẽ đi vào giá vốn Q4/26 [DD].
3. P4/DGC: Nghi Sơn (2.400 tỷ) kế hoạch vận hành Q4/26 [W]; vụ án 3/2026 (14 bị can gồm Chủ tịch, Phó Chủ tịch), khai trường 25 & 19B tạm dừng [W] ⇒ rủi ro nguồn quặng là rủi ro DOANH NGHIỆP, không phải ngành.
4. VAT 5% phân bón (khấu trừ đầu vào, hiệu lực 1/7/2025) — đã nằm trong nền so sánh từ Q3/26; tác động biên **chưa đo**.

## Rủi ro cấu trúc / chính sách
Chính sách XK của Trung Quốc (urê, phosphate, P4) quyết định giá thế giới nhiều hơn cung cầu VN · giá khí PV GAS gắn dầu (cú sốc Brent T3–T4 và T9/2026) · môi trường/khai thác tài nguyên (case DGC) · DHB D/E cao (2,85 Q2/26 [BQ]).

## Chỉ báo dẫn dắt
| # | Chỉ báo | Nguồn | Tần suất |
|---|---|---|---|
| 1 | Urê, DAP, Brent | `data/urea_monthly.csv`, `dap_monthly.csv`, `brent_monthly.csv` (WB CMO, CANONICAL, cron ngày 5+10) | tháng |
| 2 | Phốt pho vàng P4 TQ | `data/phosphorus_weekly.csv` (SunSirs, cập nhật tới 23/10) — **⚠️ CHƯA có trong `kb/data_registry/`** (grep 0 kết quả) ⇒ phải đăng ký trước khi wire vào bất cứ thứ gì | ngày |
| 3 | Lưu huỳnh / NH3 CFR | **không có feed** — chỉ qua báo cáo CTCK/BCTC DDV | — |
| 4 | Xút (đầu ra CSV) | `data/caustic_soda_monthly.csv` — **dừng ở 2026-05 (680)**, nghi stale ⇒ báo Winston | tháng |
| 5 | LNST quý 3 mã đạm + DDV + DGC | `tav2_bq.ticker_financial` (CANONICAL) | quý |

## DỰ BÁO CÓ THỂ BÁC BỎ — kiểm chứng **2027-05-20**
**F-CHEM-1 (urê)**: Tổng LNST **DCM + DPM + DHB** quý **Q1/2027 thấp hơn Q1/2026 (1.417 tỷ [BQ]) ít nhất 25%**, tức ≤ ~1.063 tỷ.
Chấm: `SUM(NP_P0)` 3 mã, `quarter="2027Q1"`, `ticker_financial`. ≤1.063 ⇒ ĐÚNG; >1.063 ⇒ SAI. Điều kiện vô hiệu: urê [WB] TB Q1/2027 > 540 USD/t
(tức giá quay lại mức Q1/26 — khi đó dự báo không còn đo cơ chế tôi đặt cược; ghi "vô hiệu", không tính đúng/sai).
**F-CHEM-2 (DAP)**: Biên gộp DDV (BCTC: LN gộp/DT thuần) quý **Q4/2026 < 8%** (kiểm ngay khi BCTC Q4 ra, hạn chót 2027-02-28).
<8% ⇒ ĐÚNG (giá vốn còn mang nguyên liệu đỉnh); ≥8% ⇒ SAI. Ngưỡng 8% lấy từ điều kiện đổi verdict ở [DD] §6.

## Thiếu dữ liệu
Chưa có LNST Q3/26 của DCM/DPM/DHB/DGC/PAT/CSV (hạn công bố cuối T10). Không có giá khí PV GAS, giá than, giá S/NH3
theo thời gian thực. Số [W] là tóm tắt tìm kiếm chưa mở trang gốc.

URL: news.metal.com (Wengfu P4 6/8) · sunsirs.com …33016 · mysteel.net …5110731 · fertilizerdaily.com 20260729 · producer.com (Argus) ·
timeslive.co.za 2026-05-27 (hạn ngạch urê TQ) · doanhnhan.baophapluat.vn (DGC khởi tố) · mekongasean.vn …53793 (Nghi Sơn) ·
mekongasean.vn …60713 (DCM XK). Đầy đủ: `sources_web_20261026.md`.
