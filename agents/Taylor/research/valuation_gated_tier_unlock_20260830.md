# Valuation-gated tier-unlock cho SIGNAL_V11 — backtest toàn lịch sử 2008-2026

Job `Taylor_20260830_124256`. User đã duyệt hướng 1 (2026-08-30 19:42 ICT, decided_by user) từ
`production_mechanism_2009_2018_20260830.md` Câu A: SIGNAL_V11 khoá cứng tier momentum mạnh vào
`state5 IN (4,5)` là nguyên nhân chính bỏ lỡ 2009. **NGHIÊN CỨU — KHÔNG wire, KHÔNG sửa
`signal_v11_sql.py`/`macro_state_live.py`/bất kỳ production code nào.**

## Tóm tắt kết quả

Cơ chế ứng viên (pb_z per-ticker, threshold **import nguyên văn** từ nghiên cứu độc lập
2026-06-22, không tune cho 2009) **mở đúng 2009** (335 phiên-mã, 28 mã, 69 episode, đa dạng
ngành) **và có edge dương on toàn lịch sử** (episode-level t=7.47, IS +4.95%/OOS +2.90%, cả hai
CÙNG DẤU) **trên một plateau ngưỡng ổn định** (-0.1 đến -0.6 đều dương, không fragile). Phát
hiện phụ quan trọng: nghiên cứu recovery-deploy 2026-06-22 (đang được dùng làm căn cứ "đã
validate") **thực ra CHƯA BAO GIỜ test được 2009** — `vnindex_5state_dt5g_live` chỉ có dữ liệu
từ **2014-01-02**, nên toàn bộ tháng 2009 bị `dropna()` âm thầm loại khỏi study đó dù nhãn ghi
"2009-2026". Cần **quant-skeptic verify** trước khi coi là ứng viên đủ chín để trình wire (chưa
làm trong job này — xem "Bước kế tiếp").

---

## 1. Giải quyết warm-up (thay vì bỏ qua như hôm trước)

`value_radar_series.csv` (index-level percentile rolling-10Y, floor 2008-01-01) không đủ warm-up
cho 2009 (minp=500 phiên, 2009 mới có ~350-500 phiên kể từ floor). Ba lựa chọn, đánh đổi:

| Lựa chọn | Ưu | Nhược | Chọn? |
|---|---|---|---|
| **(A) pb_z per-ticker** (PB vs `PB_MA5Y`/`PB_SD5Y` của CHÍNH MÃ, từ BQ `ticker`/`ticker_prune`) | Có coverage thật từ 2008 (n=11 mã tháng 09/2008, tăng dần); **ĐÃ dùng trong production** (`pe_z` cùng công thức trong `COMPOUNDER_BUY`, `signal_v11_sql.py` dòng 111) và **đã validate** làm timing lens trong 8L IC panel (marginal IC +0.050) — không phải phát minh mới | `PB_MA5Y` của các mã niêm yết 2006-2007 gộp cả đỉnh bong bóng vào trung bình 5 năm → z-score có thể bị pha loãng (đã kiểm: KHÔNG xảy ra ở đây, med_pbz vẫn cực âm -1.3 → -0.9 suốt 09/2008-05/2009, xem §2) | ✅ **CHỌN** |
| (B) percentile cửa sổ ngắn hơn (vd 500-1000 phiên, minp=120) của composite value_radar | Nhất quán với hiển thị Value Radar hiện có | Composite gồm CẢ spread lãi suất (thành phần yếu nhất, `deposit_rate_vn` calibrate hồi tố 2026-06-19 — dùng cho 2008-2009 sẽ mang bias biết-trước NẶNG hơn); là biến thể non-canonical cần tự dựng, chưa ai kiểm | ❌ không chọn (không cần, (A) đã giải quyết được) |
| (C) ngưỡng tuyệt đối cố định (PE/PB neo cứng, không percentile) | Đơn giản nhất, không cần lịch sử | Đúng loại overfit-1-episode nếu neo nhìn 2009; muốn khách quan phải lấy mốc từ nguồn ĐỘC LẬP (vd Graham heuristic) — yếu hơn (A) vốn đã có sẵn threshold độc lập | ❌ không chọn |

**Chọn (A)** vì nó vừa giải quyết warm-up vừa là con đường "tái dùng cái đã validate" đúng như
dispatch yêu cầu, không phải tự nghĩ ra công thức/ngưỡng mới.

## 2. PRE-REGISTERED trước khi backtest (không nhìn 2009 rồi chỉnh)

- **Ngưỡng**: `pb_z_ticker <= -0.3`. Import **nguyên văn, không đổi 1 chữ số** từ
  `probe_recovery_signal.py`/finding `Taylor 2026-06-22T08:09:05Z` (archive
  `2026-W26-W27-raw-events.md`) — nghiên cứu đó test recovery-deploy ALLOCATION overlay (market-
  median pb_z), hoàn toàn KHÔNG liên quan tới câu hỏi 2009 hôm nay khi được chốt. Đây chính là
  "khoá cơ sở trước khi chạm dữ liệu 2009" theo đúng yêu cầu dispatch.
- **Công thức**: `pb_z = SAFE_DIVIDE(PB - PB_MA5Y, NULLIF(PB_SD5Y,0))` — y hệt cột `pe_z` đang
  sống trong `signal_v11_sql.py` (đổi PE→PB), y hệt định nghĩa "pb_z" trong 8L IC panel
  2026-06-21.
- **Cơ chế**: 6 tier momentum mạnh bị khoá cứng bởi dispatch (`MEGA/S_PRO/MOMENTUM/
  MOMENTUM_QUALITY/MOMENTUM_S/MOMENTUM_A`, tất cả hiện đòi `state5 IN (4,5)`) được OR thêm điều
  kiện: `state5 IN (1,2,3) AND pb_z_ticker <= -0.3`. `AVOID_bear` (veto toàn bộ state 1-2) chỉ áp
  khi KHÔNG thoả điều kiện mới. Không đụng `COMPOUNDER_BUY`/`DEEP_VALUE_RECOVERY`/`MOMENTUM_N`/
  `MOMENTUM_S_N` (ngoài phạm vi dispatch, đã có gate riêng).
- **State5 dùng để test**: DT5G/DT4-base CANONICAL — ghép `phaseA_dt5g_2007_2019.csv` (job
  `Taylor_20260830_114100`, tái dựng có audit) cho <2014-01-02 + bảng production
  `tav2_bq.vnindex_5state_dt5g_live` cho ≥2014-01-02. **KHÔNG** dùng `tav2_bq.vnindex_5state`
  (v3.4b BASE, bẫy CLAUDE.md) — xem Phát hiện phụ #2 bên dưới về việc `signal_v11_sql.py` hiện
  tại đang join nhầm bảng đó.

## 3. Backtest toàn lịch sử (không chỉ riêng 2009)

Panel: `tav2_bq.ticker`+`ticker_1m` fallback, universe `ticker_prune`, `liq>=1e9`, `ta>=100`
(tái dùng nguyên công thức `ta`/`fa_tier`/`pe_z`/`liq` từ `signal_v11_sql.py`, thêm `pb_z`),
2008-01-01→2026-06-15, 142.501 phiên-mã. Script:
`valuation_gated_tier_unlock_20260830/{pull_candidates.py,analyze.py}`.

**Kết quả cấp phiên-mã** (nhóm A = "mở mới" bởi tier-unlock, so 2 đối chứng):

| Nhóm | n | mean fwd profit_2M | median | win% |
|---|---|---|---|---|
| A: mở mới (state 1-3 + cheap) | 5.307 | **+5.14%** | +1.62% | 54.4% |
| B: baseline hiện tại (state 4-5, đã fire) | 8.983 | +10.58% | +6.24% | 63.4% |
| C: đối chứng đúng (state 1-3, KHÔNG cheap, bị loại) | 62.787 | +2.41% | +0.00% | 49.7% |

A > C rõ rệt (đúng hướng: valuation THẬT SỰ phân biệt được, không phải noise) nhưng A < B (mở
sớm hơn baseline, kỳ vọng thấp hơn baseline vì baseline chỉ fire khi trend đã CONFIRM bằng state
cao — hợp lý, không phải dấu hiệu xấu).

**Kết quả cấp EPISODE** (gộp phiên liên tiếp cùng mã, gap>7 phiên = episode mới; dùng return của
NGÀY ĐẦU episode để tránh tự tương quan trong episode — đơn vị N đúng nghĩa "sự kiện độc lập" theo
skill quant-research, không phải đếm dòng):

- **N = 1.399 episode** (1 thiếu profit_2M). **mean +4.03%, median +0.58%, win 51.0%.**
- **t-stat episode-level = 7,47** (n=1.399) — không phải kết quả may rủi thống kê.
- Bootstrap (5.000 lần, resample có hoàn lại trên episode): mean 5th/50th/95th pct =
  **+3,16% / +4,03% / +4,94%**. **P(mean ≤ 0) = 0,0%** trên toàn bộ 5.000 lần resample.
- **IS (<2020) mean +4,95%** (n=774) vs **OOS (≥2020) mean +2,90%** (n=625) — **cả hai CÙNG
  DẤU DƯƠNG**, đúng chữ ký robustness fleet yêu cầu (IS AND OOS positive), dù OOS yếu hơn IS
  (giảm ~41% biên độ — cần quant-skeptic đánh giá mức giảm này có đáng ngại không).

**2009 cụ thể — có mở đúng không:**
- **335 phiên-mã, 28 mã riêng biệt, 69 episode bắt đầu trong 2009** — không phải 1-2 lần trùng
  hợp. Danh sách mã đa dạng ngành thật: BCC(xi măng), BMP(nhựa), BVS(CK), CII(hạ tầng),
  DMC/IMP(dược), FPT(công nghệ), GIL(dệt may), KDC(thực phẩm), NBC(than), PAC(ắc quy),
  PGC/PLC(gas), PVD(dầu khí), REE(đa ngành), SJS(BĐS), SMC(thép), TMS(logistics), VNM(sữa),
  VSH/SJD(thuỷ điện) — **không tập trung 1 ngành** (khác cảnh báo risk-auditor từng nêu cho
  discretionary-funnel PB-adaptive, nơi CTCK/hoá chất chiếm >20% cohort).
- Episode sớm nhất fire **2009-05-19 (GIL)**, đúng lúc DT5G vẫn còn CRISIS (state=1, cap chưa hết
  hạn tới 05-18) nhưng đã cực rẻ (pb_z -0.87) — đây CHÍNH LÀ cửa sổ mà Câu A báo cáo hôm trước xác
  nhận hệ **0% invested tuyệt đối** suốt 2009. Cơ chế này thực sự chạm đúng lỗ hổng.

**Robustness sweep ngưỡng** (KHÔNG dùng để CHỌN số mới — chỉ kiểm tra -0.3 có nằm trên thềm ổn
định hay là điểm may rủi đơn lẻ):

| ngưỡng | n mở mới | mean% | median% | win% | n 2009 |
|---|---|---|---|---|---|
| -0.1 | 8.792 | 4.79 | 1.82 | 54.7 | 420 |
| -0.2 | 7.864 | 5.11 | 1.89 | 55.1 | 376 |
| **-0.3** | **6.858** | **5.10** | **1.92** | **55.1** | **335** |
| -0.4 | 5.911 | 5.04 | 1.82 | 54.7 | 285 |
| -0.5 | 4.872 | 5.48 | 2.00 | 55.7 | 242 |
| -0.6 | 3.942 | 5.26 | 2.31 | 56.5 | 177 |

**Plateau ổn định** trên toàn dải -0.1→-0.6 (mean dao động hẹp 4,79-5,48%, win 54,7-56,5%) — -0.3
KHÔNG phải điểm may rủi bị fit, và 2009 được mở ở MỌI ngưỡng test (177-420 phiên-mã tuỳ ngưỡng).
Đây đúng dạng "robust plateau" mà 2026-06-22 finding (depth-scaled deploy) đã ghi nhận cho cùng họ
chỉ báo pb_z.

## 4. Ràng buộc "đừng re-tune DT5G" — tôn trọng

Đây là cơ chế MỚI ở tầng SIGNAL_V11 (selector), không đụng bất kỳ tham số nào của `macro_state_live.py`
(DT 4-gate 10/25, macro cap, breadth guard) hay `vnindex_5state_dt5g_live`. DT5G/DT4 dùng làm INPUT
đọc-only (`state5`) giống hệt cách sản xuất đang đọc, không sửa logic sinh state.

## 5. EASING_FLOOR — không revive, đúng cam kết

Không dùng bất kỳ tín hiệu lãi suất/refi nào trong cơ chế này. `pb_z` là valuation thuần tuý
(PB vs lịch sử riêng mã), không neo vào chính sách tiền tệ — đúng bài học 2026-06-22 (rate signal
lag/mơ hồ, valuation-vs-own-history mới là bộ lọc phân biệt thật).

---

## Phát hiện phụ (không nằm trong scope sửa hôm nay, ghi lại để không lặp lại)

**#1 — Nghiên cứu "đã validate" 2026-06-22 thực ra chưa test được 2009.** `probe_recovery_signal.py`
tự nhận "Monthly panel 2009-2026" nhưng đọc state từ `tav2_bq.vnindex_5state_dt5g_live`
(**verify trực tiếp BQ hôm nay: `MIN(time) = 2014-01-02`**). `.dropna(subset=["state"])` ở dòng
cuối cùng của pipeline đó **âm thầm loại hết mọi tháng 2009-2013** khỏi thống kê n=39/n=3 đã trích
dẫn nhiều lần (kể cả trong dispatch hôm nay). Kết luận "cheap n=3, chỉ 2 episode (COVID+SCB)" của
finding đó là ĐÚNG cho phạm vi 2014-2026 nó thực sự chạy, nhưng **nhãn "2009-2026" là sai** — nên
sửa nhãn hoặc chạy lại với state nguồn ghép giống job hôm nay nếu muốn kết luận đúng phạm vi đã
công bố. Không sửa file đó hôm nay (ngoài phạm vi dispatch).

**#2 — `signal_v11_sql.py` hiện tại join `tav2_bq.vnindex_5state` (v3.4b BASE) làm `state5`, không
phải `vnindex_5state_dt5g_live`/DT5G production thật.** Đây đúng bẫy CLAUDE.md "bảng không hậu tố
KHÔNG PHẢI DT5G". Baseline dùng để so sánh trong backtest hôm nay dùng state5 CANONICAL (đã sửa),
nên có thể lệch nhẹ so với hành vi historical THẬT của `signal_v11_sql.py` (dùng state khác, nhiều
transition hơn vì không qua DT4-gate/macro-cap). Ảnh hưởng cụ thể tới production V2.4 hiện tại
chưa đo — cần job riêng nếu muốn định lượng (không phải hôm nay).

## quant-skeptic verdict: REFUTED-as-presented (2026-08-30, medium confidence)

Dispatch bắt buộc quant-skeptic trước khi coi là đủ chín — đã chạy, kết quả: **hướng edge (dấu
dương) khả năng vẫn sống, nhưng các con số dùng để gọi nó "robust/không phải fluke" KHÔNG đứng
vững** khi bị tấn công độc lập. 4 điểm fail cụ thể (đã tự verify lại bằng BQ/recompute, không chỉ
tin báo cáo):

1. **t=7,47 phóng đại ~3 lần.** 1.399 episode chỉ trải trên **172 tháng-lịch riêng biệt** (top-20
   tháng chiếm 34% tổng episode — cùng 1 sự kiện regime kích nhiều mã cùng lúc, không độc lập).
   Cluster theo tháng: **t rơi còn ~2,17**, **47% cluster-tháng có mean ÂM**. Dấu vẫn sống
   (cluster bootstrap P(mean≤0)=0%) nhưng độ tin cậy bị báo cáo thổi phồng.
2. **OOS suy giảm ĐƠN ĐIỆU, không phải nhiễu quanh 1 mốc.** Trượt điểm cắt: 2019→+2,97%,
   2020→+2,90%, 2021→+1,25%, 2022→+0,89%. Theo năm: **2022 mean −5,76%**, **2026(partial)
   −9,40%**; nhiều năm "mean dương" có **median ÂM** (2009 median −1,03%; 2019 median −0,91%) —
   dương là do đuôi kéo, không phải kết quả điển hình. Welch IS-vs-OOS p≈0,058 (biên giới).
3. **Ô nhiễm mã BANNED chưa lọc.** DMC/IMP (2/69 episode 2009) nằm trong danh sách banned
   vĩnh viễn — báo cáo liệt kê mà KHÔNG gắn cờ. Toàn lịch sử: **52/1400 (3,7%) episode** dính
   banned (HSG một mình 17 episode, NVL 10, HVN 6, GEG 6...). Chưa recompute loại banned.
4. **Baseline dùng state5 KHÁC state thật `signal_v11_sql.py` đang chạy.** Production join
   `tav2_bq.vnindex_5state` (v3.4b BASE), không phải DT5G. Đo trực tiếp 2014-2026: v3.4b BASE có
   515 ngày state 4/5 (203 EXBULL) vs DT5G-live 482 ngày (chỉ 60 EXBULL) — khác nhau đáng kể. Cả
   hai đồng ý 2009 không đạt state 4/5 (kết luận gốc VẪN ĐỨNG), nhưng 95% episode (2014-2026)
   được đo trên counterfactual sai so với production thật.

Điểm PASS (đã tự verify độc lập, không chỉ tin báo cáo): profit_2M không rò vào logic chọn lọc
(đúng như thiết kế); `PB_MA5Y`/`PB_SD5Y` xác nhận nhân quả thật qua BQ (HDB niêm yết 2018-01,
`PB_MA5Y` NULL tới 2020-06 — đúng hành vi trailing, không phải cửa sổ centered); ngưỡng -0.3
đúng là import từ nghiên cứu độc lập trước, không tune cho 2009; recompute IS/OOS khớp chính xác
số đã báo cáo.

**5 việc phải làm lại trước khi đưa lại cho quant-skeptic lần 2** (theo đúng khuyến nghị): (a)
chạy lại baseline+mechanism trên ĐÚNG bảng production join (`vnindex_5state` v3.4b, không phải
DT5G splice) cho đoạn 2014-2026; (b) tính lại significance với cluster-robust SE theo tháng/
episode-regime; (c) loại 15 mã banned trước khi trích bất kỳ số tổng hợp nào, báo lại cỡ mẫu
(2009: 28→26 mã, toàn kỳ: 1400→1348 episode); (d) định lượng capacity/ADV thật cho nhóm mã mỏng
nhất (S55/DMC/MHC/NBC, 1,1-3,9 tỷ/ngày — không đủ cho NAV 50B+); (e) backtest cấp NAV đầy đủ
(không chỉ profit_2M cross-section) — đúng mục "Bước kế tiếp #2" đã tự đặt ra trước khi có verdict.

**Kết luận cho user: CHƯA đủ điều kiện xem xét wire.** Không tự sửa lại vòng 2 hôm nay (ngoài
ngân sách job) — cần job riêng nếu muốn tiếp tục theo hướng này.

## Bước kế tiếp (chưa làm, ngoài phạm vi job hôm nay)
1. **quant-skeptic REQUIRED** trước khi đề xuất wire — đặc biệt kiểm: (a) OOS suy giảm biên độ
   ~41% có phải dấu hiệu suy yếu thật hay nhiễu N nhỏ; (b) `PB_MA5Y`/`PB_SD5Y` có point-in-time
   thật không (giả định dựa trên cùng họ cột với `PE_MA5Y`/`PE_SD5Y` đã production, CHƯA tự verify
   độc lập lại hôm nay); (c) capacity/liquidity của 28 mã 2009 (nhiều mã nhỏ, có che was margin
   thực thi được không ở thời điểm đó — câu hỏi lịch sử, không ảnh hưởng thiết kế nhưng ảnh hưởng
   "lỡ bao nhiêu pp thực tế").
2. Nếu quant-skeptic CONFIRMED: cần thêm 1 lớp — mô phỏng ảnh hưởng lên **NAV/CAGR toàn chiến
   lược** (không chỉ profit_2M cấp phiên-mã), vì đây là điều kiện MỞ THÊM ứng viên, chưa chắc
   NAV-weighting/position-sizing sẽ khai thác hết edge đo được ở đây.
3. Sửa nhãn/re-run `probe_recovery_signal.py` phạm vi đúng (Phát hiện phụ #1) nếu muốn dùng lại
   làm căn cứ cho quyết định khác trong tương lai.

## File liên quan
- `valuation_gated_tier_unlock_20260830/pull_candidates.py`, `analyze.py` — script (ephemeral)
- `valuation_gated_tier_unlock_20260830/panel_raw.csv`, `panel_classified.csv`,
  `new_fires_detail.csv`, `new_fires_episodes.csv`, `dt5g_prod_2014plus.csv` — output ephemeral
- `exp_insider/phaseA_dt5g_2007_2019.csv` (job `Taylor_20260830_114100`, DT5G reconstructed 2006-2019)
- `production_mechanism_2009_2018_20260830.md` (Câu A, job hôm nay trước đó — nguồn nguyên nhân gốc)
- `mike/kb/archive/2026-W26-W27-raw-events.md` (nguồn pb_z threshold -0.3, 2026-06-22)
- `signal_v11_sql.py`, `probe_recovery_signal.py` (production/research code đọc, KHÔNG sửa)
