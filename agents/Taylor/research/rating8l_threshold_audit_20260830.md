# Audit ngưỡng cứng trong hệ 8L rating — 2026-08-30 (READ-ONLY, không sửa code)

Job Taylor_20260830_100832. Phạm vi: `rating_8l.py` (982 dòng) + consumer chính. Nguyên tắc phân
loại theo dispatch: (a) neo GIÁ THỊ TRƯỜNG (PE/PB/PS-based) → ứng viên adaptive; (b) neo KINH TẾ
TUYỆT ĐỐI (zero-anchor) → fix đúng; (c) chủ đích đã khoá (user 2026-07-27) → không đề xuất.

## Câu hỏi trung tâm — bins 1-5 cắt bằng CUTOFF TUYỆT ĐỐI, KHÔNG PHẢI rank/percentile

`rating_8l.py` có **HAI trục tách biệt hoàn toàn**, và chỉ MỘT trong hai có khuyết tật kiểu PB<1.0:

1. **QUALITY rating (1-5)** — `rate_row()`/`bin_core()`/`rate_securities/insurance/realestate/bank/power()`
   — 100% **cutoff tuyệt đối** trên tỷ số kế toán (không phải rank cross-sectional). VD:
   `bin_core`: `s>=10→1, >=7→2, >=4→3, >=2→4, else 5` trên core_score max-12.
2. **VALUE axis (`value_score_v2/v3`)** — **đã rank/percentile-based from the ground up**:
   `value_yield_pct` = `rank(pct=True)` trong route, `pb_z` = z-score so với lịch sử 5Y CỦA CHÍNH
   MÃ (không phải cutoff thị trường chung), `value_pct` = `value_score.rank(pct=True)`. Comment
   dòng 883-888 tự ghi rõ: "PERCENTILE bands... NOT a fitted hard cutoff". **KHÔNG có PE/PB/PS
   cutoff tuyệt đối nào trong trục value** — 3 chỗ duy nhất có `PB<0`/`PE<=0` (dòng 856, 961-963)
   là sanity-check số âm vô nghĩa, không phải ngưỡng thị trường.

**Kết luận trung tâm**: khuyết tật giống PB<1.0 KHÔNG tồn tại trong `rating_8l.py`. Trục dễ bị
"cùng con số, ý nghĩa khác theo chu kỳ" (value axis, dùng PE/PB/PS) đã tự adaptive từ 2026-06-16.
Trục còn cutoff tuyệt đối (quality rating 1-5) dùng **tỷ số kế toán** (ROE/ROIC/D-E/FSCORE/CFO-NP),
không phải bội số định giá theo giá — khác bản chất với PB<1.0.

## Kiểm kê đầy đủ ngưỡng cứng trong `rating_8l.py`

| Ngưỡng | file:line | Vai trò | Nhóm |
|---|---|---|---|
| `moat_tag`: GPM mean>=0.25, CV<=0.20 (8Q), ROE5Y>=0.15/0.10 | 187-203 | phân loại moat WEAK/MODERATE/STRONG | (b) tỷ số vận hành |
| `core_score`: ROIC3Y>=0.15/0.10, ROIC_Min3Y>=0.10/0.05, ROE_Trailing>=0.18/0.12, real_lev<=0.3/1.0, cfo_np>=1.0/0.7, FSCORE>=8/6 | 205-219 | 6-trục scorecard, max 12 | (b) tỷ số vận hành |
| `stability`: CV GPM<=0.20/0.40, ROE_Trailing/ROE3Y<=1.3/1.8 | 221-237 | phạt lợi nhuận đỉnh chu kỳ | (b) tỷ số vận hành |
| `redflag`: NP_TTM<0, real_lev>3 | 239-249 | red-flag cấu trúc | **(b) neo KINH TẾ TUYỆT ĐỐI đúng nghĩa** (NP<0, lev>3 là điểm zero/vỡ nợ, không trôi theo chu kỳ) |
| `bin_core`: s>=10→1,>=7→2,>=4→3,>=2→4,else 5 | 251-252 | cắt bin QUALITY từ core_score | cutoff tuyệt đối trên (b) |
| `eq_flag`: real_lev>=0.25, NP/GP>=0.65 (8Q)/0.90 (4Q), CF_OA_5Y<=0 | 254-295 | earnings-quality gate | (b) tỷ số vận hành |
| `rate_securities/insurance`: ROE tuyệt đối theo bậc (0.20/0.15/0.13/0.11/0.09/0.07/0.05) | 297-326 | rating ngành tài chính | (b) tỷ số vận hành |
| `rate_realestate`: ROE_Trailing>=0.18/0.10, ROIC3Y>=0.12/0.07, real_lev<=0.5/1.5, pipeline>=0.15 | 328-347 | rating BĐS | (b) tỷ số vận hành |
| `rate_bank`: ROE>=0.08/0.12/0.14/0.15, NPL<=0.012/0.020, coverage>=0.9/1.5 | 414-429 | rating ngân hàng | (b) tỷ số vận hành |
| **Golden floor**: ROE_Min3Y>=0, CF_OA_3Y>0 | consumer (funnel/custom30) | gate đầu tư | **(b) neo KINH TẾ TUYỆT ĐỐI — điểm ZERO thật, đã đúng, KHÔNG đề xuất đổi** |
| `PB<0` / `PE<=0` | 856, 961-963 | sanity-check | không phải ngưỡng, số âm vô nghĩa |

**Không có PE/PB/PS/EVEB cutoff tuyệt đối nào trong trục QUALITY hay VALUE của rating_8l.py.**

## Đo nhanh mức độ "trôi theo chu kỳ" của nhóm (b) — so sánh với PB<1.0

Query `tav2_bq.ticker_financial`, snapshot theo năm (không phải theo phiên như PB, nhưng đủ thấy
biên độ trôi):

| Năm | %ROIC3Y>=0.15 | %ROE_Trailing>=0.18 | %STLTDebt_Eq<=0.3 | %FSCORE>=8 |
|---|---|---|---|---|
| 2011 | 10.0% | 36.8% | 41.3% | 3.9% |
| 2015 | 31.9% | 24.6% | 46.3% | 6.5% |
| 2018 | 12.1% | 23.5% | 47.1% | 7.6% |
| 2020 | 20.3% | 18.1% | 50.4% | 8.2% |
| 2022 | 17.6% | 22.8% | 51.6% | 10.5% |
| 2024 | 14.8% | 15.3% | 53.2% | 9.2% |
| 2026 | 15.7% | 21.7% | 52.4% | 9.4% |

Biên độ dao động **2-4x** giữa năm cao/thấp — có trôi theo chu kỳ kinh tế thật (suy thoái nén ROE
toàn thị trường), nhưng đây là **tín hiệu kinh tế thật** (lợi nhuận doanh nghiệp giảm thật trong
suy thoái), không phải **artifact của việc thị trường tái định giá bội số** — khác bản chất với
PB<1.0 (86% thị trường năm 2011 vs 19% năm 2009: biên độ **4.5x** nhưng nguyên nhân là NHÀ ĐẦU TƯ
định giá lại, không phải doanh nghiệp đổi ROE). Kết luận: nhóm (b) có trôi nhưng là trôi ĐÚNG —
adaptive-hoá sẽ làm mất tín hiệu "chu kỳ đang xấu thật" mà scorecard cố tình muốn bắt.

## Consumer chính — ngưỡng nằm NGOÀI rating_8l.py

- **LAG order filter / funnel quality floor / DC double-confirm / production selectors**
  (`lag_dnpr_harness.py`, `sector_lens_monitor.py`, `custom_basket.py`, `unified_screener.py`,
  `bin/discretionary_candidate_funnel.py`…): tất cả đọc **`rating<=3`** hoặc **`rating<=2`** —
  cutoff NGUYÊN trên thang 1-5 đã tính sẵn, không phải cutoff mới trên tỷ số thô. Đây chính là
  gate **user đã khoá 2026-07-27** (feedback-lag-rating-gate-locked) — không đề xuất mở lại.
- **Moat governance (WIDE notch)**: `MOAT_TIER` — nhãn định tính (WIDE/NARROW/NONE) từ audit
  người (`data/moat_tags.csv`), không phải ngưỡng số — không áp dụng khung adaptive/fix-cứng.
- **D&A route classification (`v3_da`)**: `DA_HEAVY_SET` — **danh sách tên cố định** (DA/Rev>=5%
  TTM, đo 1 lần rồi chốt danh sách), không phải cutoff số động — không có khuyết tật kiểu PB.
- **PB-adaptive funnel đã wire hôm nay** (`discretionary_candidate_funnel.py`, commit 714b5889):
  đây CHÍNH LÀ nơi có PE/PB cutoff tuyệt đối thật (đã sửa) — nằm NGOÀI `rating_8l.py`, không phải
  trong nó.

## Kết luận cuối

**8L đã adaptive đúng chỗ cần (trục VALUE, dùng bội số giá) — KHÔNG cần mở hướng nghiên cứu mới
cho `rating_8l.py`.** Trục QUALITY dùng cutoff tuyệt đối nhưng trên NHÓM (b) neo kinh tế (tỷ số
vận hành), có trôi theo chu kỳ thật nhưng đó là tín hiệu đúng cần giữ, không phải artifact cần
fix. Golden floor (ROE_Min3Y>=0, CF_OA_3Y>0) và rating<=3 gate đều đúng loại, không đổi. Không có
ứng viên adaptive mới nào tương đương mức độ nghiêm trọng của PB<1.0 trong toàn hệ 8L.
