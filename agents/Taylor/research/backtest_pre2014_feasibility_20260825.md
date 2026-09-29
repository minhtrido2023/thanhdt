# Feasibility: chạy backtest V2.4 trước 2014 (2008 hoặc 2010)? (2026-08-25)

**Job** `Taylor_20260825_052019`. **CHỈ feasibility check — KHÔNG chạy backtest** (đúng phạm vi
dispatch). Motivation: `macro-margin-review_20260825.md` (job `_040602`) đã chỉ ra toàn bộ track
record thực nghiệm V2.4/DT5G (2014+) chưa từng chạm episode Loại 1 (mega-crisis 2007-2012) — nếu
muốn kiểm tra V2.4 dưới một khủng hoảng cơ cấu thật, cửa sổ 2014+ không trả lời được, cần lùi về
trước 2014.

## Tóm tắt câu trả lời

**Ràng buộc binding NHẤT không phải universe hay DT5G như giả định trong dispatch — mà là độ đầy đủ
dữ liệu định giá `ticker_financial` (PE/PCF/PS) cho composite 8L rating.**

| Ràng buộc | Sớm nhất KHÔNG binding | Ghi chú |
|---|---|---|
| Universe size (`universe_pit`) | **2007** (180 mã, đã >>50 mã) | Không binding — xem (a) |
| DT5G warm-up | **~2006** (kỹ thuật), **2014** (deploy production hiện tại) | Soft constraint — xem (b) |
| `universe_pit` MIN(time) | **2000-07-28** | Không binding — xem (c) |
| 8L rating data (PE+PCF+PS đủ 3) | **2013** (80,5% coverage) | **BINDING** — xem (d) |

**Năm sớm nhất khuyến nghị cho backtest fidelity cao (gần production nhất): 2013.**
**Năm sớm nhất về mặt kỹ thuật (không crash, chạy được) nhưng chấp nhận suy biến rõ: 2008.**

## (a) Universe size — KHÔNG binding, dùng `universe_pit` thay vì `ticker_prune`

`ticker_prune` (bảng legacy, tuyển thủ công): 2008≈105, 2009≈141, 2010≈206, 2011≈179, 2012≈170,
2013≈157, 2014≈203 — mốc dispatch nêu (2008≈105, 2014≈203) khớp đúng.

**Nhưng `ticker_prune` KHÔNG còn là universe canonical của V2.4** — đã bị thay bởi `universe_pit`
từ 2026-07-22 (`kb/data_registry/price-volume/universe_pit.md`, status CANONICAL — production_since
2026-07-22; consumer gồm `golive_recommend_v23.py`, `custom_basket.py`). Đo lại trên `universe_pit`
(BQ, 2026-08-25):

| Năm | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| n mã `universe_pit` | 180 | 243 | 375 | 546 | 608 | 629 | 644 | 663 |

Cao hơn hẳn `ticker_prune` mọi năm (universe_pit rộng hơn vì tiêu chí khác — median trading value
60 phiên >=1 tỷ VND thực, KHÔNG tuyển thủ công — xem `mike/bin/build_universe_pit.py` §BỘ TIÊU CHÍ
v1). **Đã >>50 mã (mốc thống kê tối thiểu trong dispatch) ngay từ 2007.** Universe **không phải**
ràng buộc binding, kể cả lùi về 2007.

## (b) DT5G warm-up — soft constraint, KHÔNG hard-block như CLAUDE.md gợi ý

`tav2_bq.vnindex_5state_dt5g_live` (bảng LIVE, deployed): MIN(time) = **2014-01-02** — khớp đúng
CLAUDE.md ("warm-up từ 2014"). `get_gated_state()` (wrapper production, dùng trong
`golive_recommend_v23.py`) đọc bảng này + fail-closed về DT4 nếu thiếu/stale → backtest chạm ngày
trước 2014-01-02 qua `get_gated_state()` sẽ luôn fallback DT4 (không phải lỗi, mà THIẾT KẾ fail-safe).

**Nhưng đọc thẳng source `macro_state_live.py::get_macro_state(start, end)` (hàm TÍNH ra DT5G, cái
bảng LIVE chỉ là kết quả deploy hàng ngày của nó) lộ ra dòng comment 2026-06-02 rất rõ (dòng
124-129):**
> "Respect `start` but never warm up LESS than the default 2014 floor... start<2014 -> qstart=start
> (pre-2014 research, **data exists back to 2000**)."

Tức là code ĐÃ CHỦ Ý hỗ trợ research pre-2014. Kiểm tra 3 input mà `get_macro_state()` cần:

| Input | Nguồn | MIN(time) đo thật |
|---|---|---|
| Base v3.4b state | `tav2_bq.vnindex_5state_tam_quan_v34b_clean` (BQ) | **2000-07-28** |
| VIX/SPX (Pillar B, US panic) | `data/us_market_history.csv` | **2000-01-03** |
| SBV refi rate (Pillar A) | `sbv_macro_overlay.SBV_REFI_EVENTS` | **2006-01-01** (34 mốc) |

Cả 3 input đều phủ trước 2008 — **binding thật sự của DT5G computation nếu tính lại = 2006-01-01**
(SBV refi event sớm nhất), không phải 2014. Gọi `get_macro_state("2008-01-01", "2013-12-31")` trực
tiếp (bỏ qua wrapper `get_gated_state()`) về mặt kỹ thuật **CHẠY ĐƯỢC** không lỗi.

**Nhưng — điều KHÔNG có, quan trọng để không tưởng nhầm "đã sẵn sàng":** DT5G's edge (module
docstring, dòng 23-29) **CHƯA TỪNG được A/B validate ngoài 2014+** ("IS 2014-19 = +0.00pp EXACTLY
... n=4 de-risk episodes (all post-2020)"). Chạy `get_macro_state()` lùi về 2008-2013 là **VÙNG
CHƯA KIỂM CHỨNG** — code chạy được không có nghĩa fused-signal (ngưỡng VIX/SPX/refi cố định, tuning
trên era 2014+) hành xử đúng trong khủng hoảng 2008 (VIX/refi biến động biên độ lớn hơn nhiều — SBV
refi nhảy 6,5%→15% trong 4 tháng 2008, so với biên độ 2014+ nhỏ hơn nhiều). Cần một bước validate
riêng (không thuộc phạm vi feasibility check này) trước khi tin số DT5G tính lại cho 2008-2013.

## (c) `universe_pit` MIN(time) — KHÔNG binding

= 2000-07-28 (đo BQ trực tiếp), đúng bằng MIN(time) của `tav2_bq.ticker` nguồn — script build đọc
CHỈ từ `ticker` thô, PIT-by-construction (asof=chính ngày đó cho mỗi phiên lịch sử, xem
`build_universe_pit.py::main()` dòng 419-420). Không phải ràng buộc.

## (d) 8L Rating data — **BINDING NHẤT**

`ticker_financial` PE/PCF/PS coverage (đo BQ, % số dòng quý có giá trị non-null):

| Năm | %PE non-null | %(PE∧PCF∧PS đều non-null) |
|---|---:|---:|
| 2007 | 26,7% | 0,3% |
| 2008 | 70,8% | 0,0% |
| 2009 | 72,5% | 1,0% |
| 2010 | 69,6% | 3,4% |
| 2011 | 76,6% | 14,0% |
| 2012 | 72,8% | 34,0% |
| **2013** | 90,0% | **80,5%** |
| 2014 | 92,7% | 92,0% |

**PCF gần như KHÔNG TỒN TẠI trước 2011** (0 dòng năm 2008!) — composite giá trị 3-lens của 8L
(`ey=1/PE + cfy=1/PCF + ps=1/PS`, `rating_8l.py`) không có đủ dữ liệu để hoạt động như thiết kế
trước 2011, và chỉ đạt độ đầy đủ >80% từ **2013**.

**Giảm nhẹ (không phải zero-risk)**: `rating_8l.py` dòng 758 — công thức là **coverage-aware**
(`value = Σ(wᵢ·pctᵢ trên lens CÓ MẶT)/Σ(wᵢ có mặt)`, KHÔNG `fillna(0.5)`), nên KHÔNG crash khi
thiếu PCF/PS — nó tự động co về **PE-only** khi 2 lens kia NaN. Vì 1/PE là lens dominant nhất theo
IC đã đo (`context_taylor_mini.md`: "1/PE dominant, IC +0,125, 94% hit"), một backtest 2008-2011
về mặt kỹ thuật **chạy được và không phải vô nghĩa** — nhưng nó đang test một **biến thể PE-only**
của composite, KHÔNG phải composite 3-lens đã validate (IC breakdown theo sector: "cfy DOMINANT
trong CYCLICAL +0,141; ps DOMINANT trong consumer +0,135" — 2 hiệu ứng này biến mất hoàn toàn khi
PCF/PS đều NaN). Golden floor (ROE_Min3Y>=0 ∧ CF_OA_3Y>0) coverage khá hơn PE (72-81% từ 2008), nên
gate chất lượng vẫn hoạt động tương đối tốt kể cả giai đoạn sớm.

## Kết luận & khuyến nghị

**Năm sớm nhất backtest fidelity cao (gần production nhất, cả 4 ràng buộc thoả >80% coverage):
2013.** Universe/universe_pit dư dả, PE coverage 90%, PE∧PCF∧PS coverage 80,5% (đủ để composite
3-lens hoạt động phần lớn thay vì suy biến PE-only), và DT5G tính lại qua `get_macro_state()` trực
tiếp technically khả thi (dù CHƯA validate era này).

**Năm sớm nhất về kỹ thuật, chấp nhận rõ suy biến: 2008** (bao trọn đáy sâu nhất VNINDEX −71,0%
2008-2009, và đúng episode Loại-1 mà `macro-margin-review_20260825.md` xác định backtest hiện tại
chưa từng chạm). Universe đủ (243 mã), golden-floor gate hoạt động (PE 70,8%), NHƯNG:
1. 8L value composite suy biến gần như thuần PE-only (cfy/ps ~0% coverage) — không phải composite
   3-lens đang chạy production.
2. DT5G phải tính lại qua `get_macro_state()` trực tiếp (không phải bảng LIVE) — **CHƯA validate**
   fused-signal trong regime biến động biên độ lớn hơn 2014+ nhiều (VIX/refi 2008 nhảy vọt).

## Việc CẦN LÀM trước khi chạy backtest thật (nếu Mike/user chọn tiến hành, dispatch job riêng)

1. **Validate `get_macro_state()` pre-2014** — so DT5G tính lại (2008-2013) với sự kiện lịch sử đã
   biết (2008 khủng hoảng phải trigger CRISIS cap, không phải NEUTRAL) trước khi tin số. KHÔNG giả
   định fused-signal đã tuning cho 2014+ tự động đúng ở biên độ 2008.
2. **Quyết định rõ: chạy composite 8L PE-only 2008-2012 có được chấp nhận hay phải giới hạn ở 2013+**
   — đây là quyết định phạm vi (scope), không phải kỹ thuật, nên để Mike/user chọn.
3. Theo `.claude/skills/quant-research/` — N độc lập events (không phải row count), self-check 0
   VND, walk-forward, DSR/PBO, quant-skeptic CONFIRMED trước khi coi bất kỳ kết quả nào là production-
   grade — đúng quy chuẩn `context_taylor_mini.md` §Quy chuẩn backtest.

**KHÔNG chạy backtest trong job này** (đúng phạm vi dispatch) — nếu feasible và Mike/user muốn tiến
hành, cần dispatch một Taylor job riêng.
