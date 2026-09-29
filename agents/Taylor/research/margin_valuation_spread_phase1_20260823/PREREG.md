# PRE-REGISTRATION — Phase 1 engine-tier, margin theo KHOẢNG CÁCH ĐỊNH GIÁ

> Job `Taylor_20260823_120317`. **Viết + commit TRƯỚC khi chạy bất kỳ leg engine nào.**
> Plan gốc user đã duyệt: `agents/Taylor/plan_margin_valuation_spread_20260823.md` (§4 họ chính sách,
> §7 cổng GO/NO-GO). Đây là **VÒNG CUỐI** trên tập 7 episode `dd52<=-20%` — user + Mike đã đồng thuận
> dừng đào biến thể mới trên tập này sau vòng này, bất kể GO hay NO-GO.

## §0. Trạng thái hiểu biết tại thời điểm viết (khai báo không-mù)

Tôi **không mù với outcome** ở tầng vị thế: chính tôi chạy Phase 0 (`_075808`), extreme-bottom
(`_083709`) và mechanism-classifier (`_110750`), nên đã biết forward-return của cả 7 episode.
**Cái thực sự out-of-sample ở vòng này là kết quả TẦNG ENGINE** (CAGR/MaxDD/DSR của danh mục V2.4
sau chi phí vay) — chưa từng đo cho bất kỳ biến thể spread nào. Ngưỡng, tập ARM, thước đo và tiêu chí
bác bỏ dưới đây khoá TRƯỚC khi chạy leg đầu tiên.

## §1. Hai lỗi của các vòng trước — đã sửa TRƯỚC khi chạy

1. **Đo spread theo NGÀY, không theo tháng.** Phase 0 lấy mẫu cuối tháng ⇒ bỏ sót hoàn toàn episode
   10-11/2022. Vòng này mọi điều kiện ARM đọc từ `daily_panel_spread.csv` (4.897 phiên, dựng ở
   `research/extreme_bottom_recognition_20260823/`) + `_dy_daily.csv` (DY median payer theo NGÀY,
   dựng mới hôm nay trên `tav2_mike.universe_pit`, 3.402 phiên 2013-01→2026-08).
2. **Lãi vay THẬT, không còn giả định.** Gói 1840 RocketX: `interest_rate` **12,5%/năm**,
   maintenance **40%**, liquidation **30%** — verified DNSE API (Mafee job `Mafee_20260823_083327`,
   ghi ở `kb/data_registry/trading-bot/dnse_openapi_v2_calling_guideline.md`).
   ⚠️ Đây là lãi suất **HÔM NAY**. Chuỗi lãi vay LỊCH SỬ vẫn là giả định `deposit + 5,0pp` — mắt xích
   yếu nhất, phải trích kèm mỗi lần dùng ngưỡng V1/V2/V4/V5/V6/V7.

## §2. Harness + bằng chứng trung thực (khoá trước)

- Engine: `engine_p1.py` = bản sao `exp_margin_kelly/p5_engine/engine_lever.py` + **đúng 2 hunk**
  (§2.1). Sim: `shn_lever.py` dùng lại **nguyên xi**, không sửa.
- Cấu hình R3 pin nguyên văn: `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`,
  `BQ_CACHE_THREADS=1`, `NAV_TOTAL_B=50`, `ETF_LIQ=custompitg`, `BASKET_WT=namecap`,
  `BASKET_SELECT=yieldcombo`, `PARK_STATES="3:0.7"`, `AUDIT_END=2026-06-19`, `$DNA_PYEXE`.
- **Điều kiện tin cậy #1 — chân control f=1,0 phải tái lập TUYỆT ĐỐI pin R3**:
  CAGR 28,8627% / MaxDD −17,7851% / Calmar 1,6229 / NAV cuối 1.178,0099B / IS 27,0925% / OOS 30,4786%.
- **Điều kiện tin cậy #2 — INERT**: `engine_p1.py` với `CAPIT_LEVER_LOO=""` và `CAPIT_LEVER_TRANCHE=""`
  phải tái lập **byte-identical** log/NAV của `E125_f13` (đã chạy 2026-08-03). Lệch ⇒ dừng, không đọc số.
- `self-check 0 VND` bắt buộc trên MỌI leg.

### 2.1 Hai hunk — khai báo chính xác, không thêm gì khác
**Hunk A (SỬA LỖI, bắt buộc cho tính đúng của mọi biến thể).** Trong `engine_lever.py`,
`forced_borrow_tiers` được đặt = **TẤT CẢ** tier `CAPIT*`, trong khi `CAPIT_LEVER_LOO` chỉ chặn việc
**nhân f** vào weight. Hệ quả: một sự kiện bị loại khỏi đòn bẩy **vẫn bị tính lãi vay** trên
`(f−1)/f` cost-basis của nó. Với D-step (LOO rỗng) lỗi này vô hại; với Phase 1 — nơi MỌI biến thể
đều có tập LOO khác rỗng — nó sẽ **phạt sai** mọi treatment leg. Hunk A lọc `forced_borrow_tiers`
theo đúng tập sự kiện được lever. Inert khi `CAPIT_LEVER_LOO=""` (⇒ kiểm tra INERT ở §2 phủ được).

**Hunk B (TÍNH NĂNG MỚI, chỉ phục vụ V8).** `CAPIT_LEVER_TRANCHE="lo:hi:m,..."` — hệ số nhân **VỐN
CHỦ SỞ HỮU** (equity) theo bậc dd52 tại ngày sự kiện, áp vào `wt_base` TRƯỚC khi nhân f.
**Chặn cứng khai trước:** `wt_base_tranche = min(m * wt_base, size × cash_frac_available)` — phần
tăng thêm KHÔNG BAO GIỜ được vượt tiền mặt rảnh của sổ, để "tăng vốn" không lặng lẽ biến thành
"tăng đòn bẩy" (đúng chữ của mandate: *tăng quy mô vốn, KHÔNG tăng f*). Inert khi env rỗng.

## §3. Bảng điều kiện ARM tại 15 sự kiện CAPIT của engine — **ĐO TRƯỚC, KHOÁ TRƯỚC**

Nguồn: `arm_conditions_events.csv` (script `build_arm_table.py`, chỉ dùng cột as-of ≤ ngày sự kiện,
0 cột forward). `dd52` theo engine (`vni_hist`), khớp panel trong ±0,3pp.

| E | ngày | dd52 | EY_med | margin(gt) | **EY−margin** | DY payer | deposit | **DY−dep** | DT5G |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 2014-05-08 | −13,2% | 10,06 | 12,0 | −1,94 | 7,08 | 7,0 | **+0,08** | 1 |
| 2 | 2015-08-24 | −17,8% | 11,15 | 10,5 | **+0,65** | 6,67 | 5,5 | **+1,17** | 3 |
| 3 | 2016-01-18 | −17,6% | 11,58 | 10,5 | **+1,08** | 6,73 | 5,5 | **+1,23** | 3 |
| 4 | 2018-05-28 | **−22,6%** | 10,23 | 11,8 | −1,57 | 6,10 | 6,8 | −0,70 | 1 |
| 5 | 2018-07-05 | **−25,3%** | 11,02 | 11,8 | −0,78 | 6,48 | 6,8 | −0,32 | 3 |
| 6 | 2020-02-03 | −9,4% | 12,11 | 11,5 | **+0,61** | 6,25 | 6,5 | −0,25 | 3 |
| 7 | 2020-03-11 | **−20,8%** | 12,32 | 11,5 | **+0,82** | 6,74 | 6,5 | **+0,24** | 2 |
| 8 | 2020-07-27 | **−23,4%** | 12,00 | 11,5 | **+0,50** | 6,86 | 6,5 | **+0,36** | 3 |
| 10 | 2022-06-15 | **−20,6%** | 8,12 | 10,5 | −2,38 | 4,59 | 5,5 | −0,91 | 2 |
| 12 | 2023-10-30 | −16,3% | 7,09 | 10,5 | −3,41 | 5,49 | 5,5 | −0,01 | 1 |
| 13 | 2024-04-17 | −7,5% | 6,50 | 10,0 | −3,50 | 4,58 | 5,0 | −0,42 | 4 |
| 14 | 2024-08-05 | −8,7% | 6,68 | 9,7 | −3,02 | 4,61 | 4,7 | −0,09 | 1 |
| 15 | 2025-04-03 | −8,0% | 7,17 | 9,8 | −2,63 | 4,48 | 4,8 | −0,32 | 4 |
| 16 | 2025-10-20 | −7,4% | 7,16 | 10,2 | −3,04 | 4,77 | 5,2 | −0,43 | 3 |
| 17 | 2026-03-09 | −13,1% | 8,16 | 11,0 | −2,84 | 4,29 | 6,0 | −1,71 | 3 |

Hai sự kiện bị chính cổng CAPIT chặn (`size=0`, không có vị thế nên không thể lever):
**E9 2022-04-19** (postbull, dd52 −8,0%) và **E11 2022-09-28** (dd52 −25,2%).

## §4. Tập ARM từng biến thể — SUY RA TỪ BẢNG §3, KHOÁ TRƯỚC KHI CHẠY

| # | Định nghĩa (plan §4) | f | **Tập sự kiện được lever** | N |
|---|---|---:|---|---:|
| **V0** | `dd52<=-20%` (PRODUCTION, control) | 1,3 | {4, 5, 7, 8, 10} | 5 |
| V1 | `EY_med − margin ≥ 0` | 1,3 | {2, 3, 6, 7, 8} | 5 |
| V2 | `EY_med − margin ≥ +1,0pp` | 1,3 | **{3}** | **1** |
| V3 | `DY_payer − deposit ≥ 0` | 1,3 | {0, 2, 3, 7, 8} | 5 |
| V4 | V1 ∪ V3 | 1,3 | {0, 2, 3, 6, 7, 8} | 6 |
| V5 | V2 ∧ DT5G ≥ 2 | 1,3 | **{3}** | **1** |
| V6 | V5, đòn bẩy cao hơn | 1,5 | **{3}** | **1** |
| V7 | V0 ∪ V5 — **câu hỏi H1 thật sự** | 1,3 | {3, 4, 5, 7, 8, 10} | 6 |
| V8 | V0 + thang tranche VỐN theo dd52 | 1,3 | {4, 5, 7, 8, 10} + hệ số m | 5 |
| BASE | không đòn bẩy | 1,0 | ∅ | 0 |

### 4.1 Ba hệ quả BẤT LỢI đã thấy được TRƯỚC khi chạy — ghi ra đây để không "phát hiện" chúng sau
1. **V8 ≡ V0 theo toán học.** Thang tranche khai trước là T1(−20…−27,5) / T2(−27,5…−35) /
   T3(−35…−45). **Cả 5 sự kiện armed đều nằm trong T1** (dd52 −20,6% … −25,3%); T2 và T3 **không có
   một sự kiện nào** trong cửa sổ engine 2014+. Nghĩa là V8 chạy ra **hệ số m = 1,00 ở mọi sự kiện**
   và phải trùng V0 tới từng đồng. ⇒ **V8 là KHÔNG KIỂM ĐỊNH ĐƯỢC ở tầng engine**, và cổng §7-6
   (dose-response theo thang V8) **không thể PASS**. Tôi vẫn chạy V8 — nhưng chỉ để dùng làm **kiểm
   tra inert thứ hai** cho Hunk B, không phải để lấy bằng chứng. Điểm sâu nhất trong cửa sổ engine mà
   cổng CAPIT có sinh sự kiện là E5 −25,3%; đáy 2022-11-15 (dd52 −40,3%) **không sinh washout event
   nào**, nên T3 không tồn tại kể cả về nguyên tắc.
2. **V2 = V5 = V6 có N = 1 sự kiện** (E3 2016-01-18). Một sự kiện không phải bằng chứng thống kê ở
   bất kỳ thước đo nào; DSR/PBO trên đó là vô nghĩa. Khai trước: dù các leg này ra số đẹp, **trần
   diễn giải là "một quan sát"**, và cổng §7-4 (LOO bỏ episode đóng góp lớn nhất) **tự động FAIL**
   vì bỏ episode duy nhất ⇒ delta = 0, không > 0.
3. **V7 ∖ V0 = {E3} duy nhất.** Toàn bộ "giá trị GIA TĂNG" của trục spread so với `dd52` đang chạy,
   ở tầng engine, quy về **một sự kiện 2016-01-18**. Đây chính là rủi ro tôi đã tự khai ở plan §10
   ("V7 ≈ V0 ⇒ NO-GO, khả năng cao nhất"), và nó đã hiện hình **trước khi chạy**.

**Không được sửa bảng §4 sau khi thấy kết quả.** Nếu muốn thang tranche khác hoặc ngưỡng khác, đó là
một prereg MỚI ở một vòng khác — mà vòng này đã được chốt là VÒNG CUỐI trên tập episode này.

## §5. Chi phí + kịch bản lãi vay (khoá trước)
- Leg **CHÍNH so registry**: `BORROW_ANNUAL=0,10` (quy ước `CLAUDE.md`).
- Leg **ĐỐI CHỨNG CHÍNH**: `BORROW_ANNUAL=0,125` — **số THẬT gói 1840**, không còn là giả định.
- Leg **STRESS**: `BORROW_ANNUAL=0,15`.
- TC 0,1%/chiều; lãi tiền gửi nhàn rỗi 0%/năm; MGE = f (1,3 hoặc 1,5), `MGE_CAPIT_ONLY=1`.
- Báo cáo luôn kèm quy đổi thực tế: **CAGR thật ≈ CAGR backtest − 1,5%**.

## §6. Mô hình gọi ký quỹ (khoá trước)
Số thật gói 1840: maintenance **40%**, liquidation **30%** (equity/market-value). Tính ở **cấp tài
khoản** theo từng phiên: `equity_ratio_t = NAV_t / (NAV_t + debt_t)`, `debt_t` lấy từ
`*_borrowledger.csv` (notional forced-borrow + tiền mặt âm tự nhiên, gộp theo NGÀY để không đếm 2 lần
— đúng bài học đính chính 2026-08-03). Kịch bản forced-sell: giá mở cửa T+1 + slippage 0,5%.
**Biến thể nào phát sinh margin call ở maintenance 40% (bất kỳ mức lãi vay nào, kể cả 15%) ⇒ LOẠI
THẲNG, không xét lợi nhuận.**

## §7. Thước đo + CỔNG GO/NO-GO — Y NGUYÊN plan §7, KHÔNG SỬA SAU KHI THẤY SỐ
Thước đo: CAGR / MaxDD / Sharpe / Calmar trên `combined_nav`, thời gian LỊCH; IS 2014-2019,
OOS 2020-01-01→2026-06-19; delta so với **BASE f=1,0** và so với **V0**.

**GO khi ĐỦ CẢ 6:**
1. **V7 > V0 ở CẢ IS và OOS**, và delta CAGR OOS **> 0**.
2. **≥1 biến thể** có delta CAGR FULL ≥ **+0,30pp** VÀ delta MaxDD xấu đi ≤ **0,50pp**.
3. **DSR ≥ 0,95** trên chuỗi excess của biến thể được đề xuất.
4. **LOO theo episode**: bỏ episode đóng góp lớn nhất, delta CAGR vẫn **> 0**.
5. **0 margin call** ở maintenance 40% + lãi vay 15%/năm.
6. **Dose-response đơn điệu** theo bậc thang spread (V1→V2) và bậc thang V8.

N_trials = **8** (V1…V8; V0 là control, không tính) ⇒ **chạy PBO/CSCV** (plan §6 mục 6 đặt ngưỡng ≥8).
PBO ≥ 0,5 ⇒ chọn cấu hình robust-trung vị, không lấy IS-best.

**NO-GO ⇒ ĐÓNG hướng.** Không shadow-monitor "để dành", không quay lại đào biến thể mới trên tập 7
episode này. **Kết quả trung gian** (qua 1-3, trượt 4-6): trần khuyến nghị = paper/shadow-monitor có
**mốc kết thúc cứng**, KHÔNG wire live.
Biến thể nào tốt hơn **nhờ arm trong CRISIS** ⇒ loại thẳng (mâu thuẫn DT5G, plan §2.5).
**quant-skeptic (`bin/verify_finding.sh --topic margin-valuation-spread-phase1`) là điều kiện CẦN**
trước khi coi bất kỳ khuyến nghị wire nào là hợp lệ.

## §8. Sai khác so với plan §6.1 — khai báo tường minh
Plan viết *"episode-windowed sim ±60 phiên, KHÔNG diff 2 full-run"*. Vòng này chạy **full-run diff**
trên cùng cấu hình tất định (stable-sort, `threads=1`, cache BQ pin), vì: (a) mọi cổng §7 được định
nghĩa trên CAGR/MaxDD/IS/OOS/DSR **của toàn kỳ** — cửa sổ ±60 phiên không sinh ra được các số đó;
(b) chân control tái lập pin R3 tuyệt đối nên "path-divergence noise" đo được chứ không phải giả định;
(c) đóng góp theo từng episode đo bằng **LOO knob** (`CAPIT_LEVER_LOO`), đúng công cụ đã dùng ở
D-step. Đây là sai khác **có chủ đích**, ghi trước khi chạy, không phải phát hiện sau.

## §9. Điều gì sẽ khiến chính tôi kết luận NO-GO
- V7 − V0 ≈ 0 (chênh < 0,10pp CAGR FULL) ⇒ spread không thêm gì ngoài `dd52` ⇒ NO-GO.
- Edge tan ở lãi vay 12,5% (số THẬT) ⇒ NO-GO ngay.
- Bất kỳ kết luận nào phụ thuộc **một** episode ⇒ NO-GO (đúng chỗ V2.5 đã chết).
- V8 trùng V0 tới từng đồng ⇒ nhánh tranche **không có bằng chứng engine**, không được khuyến nghị.
