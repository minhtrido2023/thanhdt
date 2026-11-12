# GĐ2-A — panel deal BAL/LAG, bảng đơn biến, placebo, H1–H5 (job `Taylor_20261112_122858`, 12/11/2026)

Brief: `brief.md` (plan `kb/projects/bal-lag-live-gap-research-plan-20261112.md` §3 bước 1–2). Không mô hình đa biến, không wire,
không đề xuất luật. Mọi số dưới đây đo trong phiên này từ các file trong thư mục (md5 ở `MD5SUMS.txt`).

## 0. Kết luận (chỉ phần đã đo)

1. **0/90 đặc trưng qua BH-FDR (q<0,10) ở CẢ IS lẫn OOS cùng dấu** (`univariate_pass.csv` rỗng). Placebo (hoán vị excess
   trong năm, 10 lần) cũng cho 0 lần "qua cả hai" ⇒ tiêu chí không bị lỏng, nhưng dữ liệu không trả lời được câu "deal nào đáng".
2. **Value của LAG mạnh IS, CHẾT OOS.** IS: `pe_rel5y` ρ −0,228 (q 0,020), `ey` +0,203 (q 0,020), `spread_ey_hurdle` +0,207
   (q 0,027), `PE` −0,182 (q 0,041), `comp_v3` +0,138 (q 0,082); hoán vị-trong-năm p ≤ 0,019 cho cả 5 ⇒ không phải hiệu ứng năm.
   OOS cùng các đặc trưng: ρ −0,08…+0,08, p_boot 0,11–0,97. ⇒ Prior "value/quality dương và mạnh lên" **bị bác** ở mức deal
   LAG 2020+. (BAL: `ey` IS −0,10 / OOS +0,15 p 0,043 — đổi dấu, không qua FDR.)
3. **OOS chỉ có biến ngữ cảnh thị trường/vĩ mô "qua" FDR** (LAG `refi` ρ −0,263 q 0,042; BAL `dd52` +0,226 q 0,042; LAG `breadth`
   +0,251 q 0,057; LAG `cpi_yoy` −0,285 q 0,064) — **và đúng bằng mức placebo**: placebo OOS trung bình 4,5 phát hiện q<0,10
   (trung vị 4, max 14) vs thật 4. Block bootstrap theo tháng KHÔNG khử được hiệu ứng mức-năm (vĩ mô gần hằng trong năm) ⇒
   4 phát hiện OOS này **không phân biệt được với hiệu ứng năm**; không đọc là tín hiệu. IS: thật 7 vs placebo TB 1,2.
4. **mom_200 không chết sau 2020 ở mức deal — vì vốn không sống ở mức deal**: IS ρ −0,05 (LAG) / −0,10 (BAL), OOS +0,15 / +0,12,
   không ô nào qua FDR. DT5G / breadth / radar: IS ≈ 0 (đúng prior), OOS dương nhưng thuộc nhóm hiệu ứng năm ở mục 3.
5. **H1–H5 (5 phép thử khai trước + 1 đối chứng H4b; Bonferroni 0,05/5 = 0,01):**
   | H | IS Δ excess TB (n trong/ngoài, p) | OOS Δ excess TB (n, p) | Đọc |
   |---|---|---|---|
   | H1 LAG SUE≥P67(IS)=1,93 & ey_pct≥2/3 | **+6,83pp** (49/248, p 0,011) | +3,69pp (34/286, p 0,327) | cùng dấu, OOS không ý nghĩa |
   | H2 BAL ey−hurdle>0 | +2,92pp (49/23, p 0,580) | +7,82pp (123/62, p 0,072) | cùng dấu, không qua 0,01 |
   | H3 HH 3T tăng (BAL+LAG, có map) | +7,50pp (10/12, p 0,520) | +0,90pp (36/19, p 0,797) | N quá nhỏ |
   | H4 LAG edge pctile<20: excess TB<0? | TB **+3,14pp** (111, p 0,104) | TB **+0,28pp** (67, p 0,917) | KHÔNG thua tiết kiệm; OOS ≈ hoà |
   | H4b đối chứng edge<20 vs ≥20 | +0,45pp (p 0,833) | **−6,05pp** (67/290, p 0,054) | OOS kém hơn, chưa qua |
   | H5 hurdle 3T TĂNG (BAL+LAG) | +2,46pp (58/321, p 0,497) | **−11,58pp** (99/448, p<0,001) | **OOS qua Bonferroni; IS không** |
   H5 OOS: bỏ từng năm 2020–2026 ⇒ Δ −8,5 … −12,8pp (không do 1 năm); chỉ trong 2022–23: trong −5,07 (26) vs ngoài +6,35 (85).
   Nhưng chỉ ~3 episode hurdle-tăng OOS (2022Q4–23Q1, 2025Q1 [+2,45], 2025Q3–26Q1) ⇒ **N độc lập ≈ 3 episode, không phải 99 deal.**
   IS 3 episode (2017Q1/2018Q1/2019Q1) đều dương — và hurdle trước 2019 là mốc tay đông cứng (`deposit_rate_vn.DEPOSIT_EVENTS`),
   nên "hurdle tăng" IS là mốc tay, không phải chuỗi công bố. ⇒ H5 là **ứng viên mạnh nhất cho vòng sau, chưa phải kết luận**.
6. **Live (OOS thật, rất nhỏ — nói thẳng):** deal đã đóng 4 BAL + 4 LAG dòng = **1 sự kiện BAL (VPI, −21,1…−21,7pp) + 3 sự kiện
   LAG** (SCL +18,7/+20,0pp, CSV −0,14pp, VPB −8,97pp). Mọi deal live (kể cả 9 đang mở) vào khi `lag_edge_pct` 10–13 (<20, vùng
   H4b OOS kém) và DT5G=3. Không suy luận được gì thống kê từ 4 sự kiện.
7. **Phát hiện phụ quan trọng (fidelity engine):** 46,9% (IS) / 44,5% (OOS) deal LAG engine có tổng tiền mua > 100% ADV20
   (Price thô × Volume) ở quy mô 50B; BAL 5,6% / 6,1%. LAG engine có 782/1.446 holding bị `ABANDONED_REFUND` (khớp không đủ
   tối thiểu) — loại khỏi panel. Đây là độ lệch đã biết (`LIQ_ZERO_BLOCK` opt-in, `pt_v23_audit_2014.py` ~L265) nhưng nghĩa là
   **gần nửa nhãn LAG đến từ deal live không thể khớp nổi**. `log_adv20` LAG là đặc trưng DUY NHẤT dương ở cả IS (ρ +0,167,
   p_perm_year 0,007) lẫn OOS (+0,132, p_perm_year 0,027) theo phép hoán vị-trong-năm (không qua FDR theo bootstrap: q 0,128 / 0,340).

## 1. Nguồn deal & nhãn

- **Engine**: `../live_gap_phase1b_20261112/ledgers/…_exp_gap_C1fix_v3_univpit.csv` md5 `89e96ba6…` — code vá mergesort
  (`sb_fix`), LAG caches frozen 11-12 (data CURRENT), `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`, AUDIT_END
  2026-06-19, `NAV_TOTAL_B=50 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off`, self-check
  0 VND BAL + LAG (log `../live_gap_phase1b_20261112/logs/exp_gap_C1fix_v3.log`). Không phải số pin R3.
- Deal = 1 `holding_id` (gộp các lần khớp ramp). Loại `ETF_PARK`, `CAPITB/L`, holding có `ABANDONED_REFUND`, holding còn mở cuối kỳ
  (`MTM_UNREALIZED`, 1). Lợi suất = Σ(bán − phí)/Σ(mua + phí) − 1. ngày tín hiệu `sig_date` = phiên ngay trước lần khớp đầu (T+1).
- **Live**: `../live_gap_phase0_20261112/fills_booked.csv` (`book_inferred` ∈ BAL/LAG), FIFO theo acct×mã×book, phí 0,097%/chiều (§6).
- **Nhãn**: excess = lợi suất − `hurdle_pit.accrual_pct(first_fill, exit)` (lãi đơn act/365, mức bậc thang PIT); hit = excess>0.
- **N**: deal có nhãn engine BAL 268 / LAG 664. Sự kiện độc lập (cùng book+mã, vào lại ≤5 phiên sau lần thoát cuối = 1 sự kiện):
  | book | era | N deal | N sự kiện | N tháng | excess TB | trung vị | hit |
  |---|---|---|---|---|---|---|---|
  | BAL | IS 2014–19 | 72 | 72 | 28 | +2,35 | −2,43 | 0,44 |
  | BAL | OOS 2020+ | 196 | 190 | 37 | +9,55 | +4,79 | 0,57 |
  | LAG | IS | 307 | 307 | 39 | +3,86 | +0,86 | 0,53 |
  | LAG | OOS | 357 | 357 | 35 | +5,20 | +2,74 | 0,55 |
  Cụm thời gian mới là ràng buộc thật: N tháng 28–39/ô; deal cùng tháng cùng chịu 1 cú thị trường.

## 2. Đặc trưng (nguồn + quy tắc PIT tại `sig_date`)

| Nhóm | Cột | Nguồn | PIT |
|---|---|---|---|
| cơ bản | PE, PB, PCF, ey=1/PE, cfy=1/PCF, pe_rel5y=PE/PE_MA5Y, pb_z5y, ROE_Min5Y, ROIC5Y, FSCORE, cfoa_pos (CF_OA_P0>0) | `data/bq_cache/ticker` (11-11) | cột tài chính join theo `ID_Release`; PE/PB trên Price thô (registry valuation bẫy 4) |
| | psy = doanh thu TTM / (Price × OShares) | `ticker_financial` merge_asof `Release_Date` | công thức `rating_8l` ps |
| | comp_v3 = TB phân vị ey/cfy/psy (≥2/3 trục) so với cross-section `universe_pit` cùng phiên | trên + `bq_cache/universe_pit` | cross-section cùng phiên |
| | rating8l | `bq_cache/fa_ratings_8l` merge_asof | as-of 8L (registry: có thể trễ ≤7 ngày) |
| | sue = (NP_P0−NP_P4)/sd(4 hiệu YoY), np_yoy, rev_yoy | `sb_fix/data/earnings_surprise_data.pkl` | `Release_Date` ≤ sig, tolerance 120 ngày |
| kỹ thuật | mom_200, D_RSI, D_CMF, dd52, rvol20, adv20 (Price×Volume TB20), adv_pct = tổng mua/adv20, log_adv20 | `bq_cache/ticker` | đóng cửa sig |
| thị trường | dt5g_state | `bq_cache/vnindex_5state_dt5g_live` (KHÔNG đọc bảng trần) | bảng công bố; `get_gated_state` là wrapper live fail-safe nên dùng bảng nó đọc |
| | dt5g_cand_clock = chuỗi phiên `state_raw≠state` | cùng bảng | PROXY, không phải `get_dt_gate_clock()` |
| | vni_dd52, vni_pe | dòng VNINDEX / mirror | đóng cửa sig |
| | breadth, breadth_terc | universe_pit, mẫu số MA200 không NULL, tercile rolling 252 phiên trước, ngưỡng tường minh | từ 2015-01-05 (universe_pit bắt đầu); breadth của sig = t−1 của phiên khớp |
| | radar_score | `value_radar.load_series(update=False)` | DISPLAY-ONLY; registry: phân vị trước 2026-06 mang bias biết-trước |
| vĩ mô | hurdle_pct, hurdle_chg3m (91 ngày lịch) | `hurdle_pit.H` | bậc thang PIT; trước 2019 mốc tay |
| | spread_ey_hurdle = 100·ey − hurdle; spread_mkt_hurdle = 100/VNINDEX_PE − hurdle | trên | |
| | refi, refi_chg6m | `sbv_macro_overlay.SBV_REFI_EVENTS` | ngày hiệu lực |
| | cpi_yoy | `cpi_vn.merge_cpi(pit=True)` | dịch +1 tháng |
| | vix, spx_dd_1y | `data/us_market_history.csv` | phiên Mỹ ≤ sig−1 ngày lịch |
| hàng hoá | comm_chg3m (log 3T) | WB CMO tháng (Brent/Urea/Iron ore/Rubber TSR20/Sugar world) khả dụng từ ngày 10 tháng M+1; hog `hog_price_vn.csv` (TB 3 miền, từ 2019) +1 ngày; ONI anom khả dụng ngày 20 tháng sau mùa | map tay ~60 mã (`TICK_COMM`); còn lại NaN. Độ phủ 13% BAL / 7% LAG |
| edge | ic_mom_sec12, ic_pe_sec12 = TB 12 IC tháng gần nhất ĐÃ BIẾT (tháng m dùng khi m+4 tháng ≤ sig) theo ngành `edge_health_monitor.map_sector` | `data/edge_panel.csv`, `monthly_ic` | fwd_3m ⇒ trễ 4 tháng |
| | lag_edge_mean12, lag_edge_pct (phân vị mean12 so lịch sử của chính nó đến sig, ≥24 mốc) | `sb_fix/data/lag_edge_health.csv` theo `known_date` | known_date |

**Bỏ (không dựng PIT được / không có nguồn đủ dài):** USD/VND (`macro_indicator` UNVERIFIED, `macro_daily.csv` không có trong
registry và có dòng 2026-12-31 tương lai); BDI (chuỗi thật chỉ từ 2026-05); SunSirs (chỉ chuỗi gần đây, sau AUDIT_END); tín dụng
(`fiinprox_money_credit` UNVERIFIED); moat/forensic tag (không có lịch sử PIT); capit edge (CAPIT bị loại khỏi panel).
Vintage: deal từ engine BQ cache 07-29; đặc trưng từ `bq_cache` 11-11 (1 vintage chung cho engine + live) — trục vintage lệch, đã khai.

## 3. Phương pháp & khai số thử

- Đơn vị kiểm định = sự kiện độc lập. Thống kê = Spearman ρ(đặc trưng, excess).
- p chính = block bootstrap theo THÁNG `sig_date`, B=2000 (seed 20261112). p phụ = hoán vị excess trong năm, B=1000.
- Họ FDR: 45 đặc trưng × 2 book = 90 phép thử mỗi era (ô < 30 sự kiện hoặc <3 giá trị khác nhau ⇒ bỏ, không tính); BH tách IS/OOS.
  Qua = q<0,10 cả IS & OOS cùng dấu. **Tổng phép thử đơn biến: 180** (90 × 2 era). Bảng thập phân vị: `deciles.csv`
  (IS BAL chỉ 72 sự kiện ⇒ ~7/decile — đọc thận trọng).
- Placebo: hoán vị excess trong năm, chạy lại toàn pipeline (B=500), R=10 (`placebo.csv`): q<0,10 IS TB 1,2 (max 4), OOS TB 4,5
  (max 14), qua-cả-hai 0/10.
- H1–H5: đúng 5 giả thuyết của plan + H4b đối chứng mô tả; ngưỡng cố định trước (SUE P67 lấy từ IS = 1,927 rồi áp sang OOS;
  ey_pct ≥ 2/3; ey−hurdle > 0; comm_chg3m > 0; edge pctile < 20; hurdle_chg3m > 0). **12 phép thử** (6 × 2 era). Δ = TB excess
  trong − ngoài, p block-bootstrap tháng B=2000.
- DSR/PBO: không có họ cấu hình chiến lược nào được chọn theo kết quả ở giai đoạn này ⇒ chưa áp dụng; bắt buộc ở bước mô hình.
- Lực thống kê (ước lượng, chưa chạy `rnd_preflight_power.py`): với ~300 sự kiện nhưng chỉ 35–39 cụm tháng, ρ phát hiện được
  cỡ ≥0,2 — hiệu ứng mức-deal nhỏ hơn thế sẽ không bao giờ qua ở N này.

## 4. Hệ quả cho vòng sau (không phải đề xuất luật)
- Bảng 3 bậc ĐÁNG/TRUNG TÍNH/BỎ dựa trên đặc trưng vi mô hiện có **không có nền**: không đặc trưng nào bền IS→OOS.
- Ứng viên duy nhất đáng kiểm tiếp là **H5 (hurdle đang tăng)** — nhưng nó là biến **thời điểm** (GĐ3), N ≈ 3 episode OOS; cần
  Bobby gắn nhãn regime MÙ và kiểm theo episode, không theo deal.
- Câu hỏi fidelity: nhãn LAG engine trộn ~45% deal vượt ADV. Trước bất kỳ mô hình nào, nên dựng lại panel với `LIQ_ZERO_BLOCK=lag`
  (hoặc lọc adv_pct ≤ ngưỡng) để nhãn phản ánh deal live khớp được.

## 5. Tái lập
```bash
cd mike/agents/Taylor/research/live_gap_phase2a_20261112
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python build_panel.py   # panel.csv/.parquet (~30s)
TZ=Asia/Ho_Chi_Minh /home/trido/thanhdt/wc_venv/bin/python analyze.py       # events/univariate/deciles/hypotheses/placebo (~2 phút)
md5sum -c MD5SUMS.txt
```
`build_panel.py` đọc `data/bq_cache` sống (manifest md5 trong MD5SUMS) — cache bị sync lại thì panel đổi; khi đó so manifest trước.
