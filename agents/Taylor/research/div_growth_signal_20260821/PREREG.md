# PREREG — Div growth trajectory có predict forward return không? (HƯỚNG B_SIGNAL)

- **Job**: `Taylor_20260821_111228` · **Ngày đăng ký**: 2026-08-21
- **Commit file này TRƯỚC khi chạy bất kỳ query outcome nào.** Mọi sai lệch so với spec dưới đây
  phải ghi vào `DEVIATIONS.md` cùng thư mục, kèm lý do, TRƯỚC khi đọc kết quả.
- **KHÔNG WIRE production dù verdict là gì.** Không tự gọi quant-skeptic.

## 1. Câu hỏi

Field `div_growth_signal` (GROWING/STABLE/DECLINING) đã wire DISPLAY_ONLY vào
`trading_bot/due_diligence.py` (commit `67a20f88`). Câu hỏi: **quỹ đạo tăng trưởng cổ tức có sức
dự báo lợi suất vượt trội phía trước không**, trong nhóm STABLE-3 payer? Nếu có → có thể nâng lên
entry factor / scoring. Nếu không → giữ nguyên DISPLAY_ONLY.

## 2. Định nghĩa biến (sao chép NGUYÊN semantics của production, không sáng tạo lại)

Tại mỗi ngày cắt `t` (phiên cuối tháng), với mỗi mã:

- 4 cửa sổ 365 ngày lùi từ `t`, dùng `corporate_action` `event_code='DIV'`,
  `event_status='executed'`, `value_per_share > 0`, khử trùng lặp bằng
  `ROW_NUMBER() OVER (PARTITION BY ticker, exright_date, dividend_year, dividend_stage_vi
  ORDER BY public_date DESC, id DESC) = 1` (đúng registry Bẫy 3).
  - `div0`, `n0` = cửa sổ `(t−365, t]`
  - `n1` = `(t−730, t−365]` · `n2` = `(t−1095, t−730]`
  - `div3`, `n3` = `(t−1460, t−1095]`
- `stable3 = n0≥1 ∧ n1≥1 ∧ n2≥1` (giống `build.py`/production, KHÔNG dùng n3).
- `div_growth_cagr = (div0/div3)^(1/3) − 1`, chỉ định nghĩa khi `stable3 ∧ div3 > 0`.
- Nhãn categorical (ngưỡng production `YIELD_FLOOR_DIV_GROWTH_HI/LO = ±0,05`):
  `GROWING` nếu `cagr > 0,05`; `DECLINING` nếu `cagr < −0,05`; ngược lại `STABLE`.
  `stable3 ∧ div3 = 0` ⇒ `NO_HISTORY` (không có cagr, KHÔNG vào test H1/H2).

**Chặt hơn production một bậc để bảo đảm PIT** (khai trước, không phải deviation): research yêu cầu
thêm `COALESCE(public_date, exright_date) <= t` — production chỉ lọc `exright_date <= asof`. Lý do:
bản ghi có `public_date` sau `t` là thông tin chưa tồn tại tại `t`.

## 3. Mẫu

- **Universe**: `tav2_mike.universe_pit` với `in_universe` **tại đúng ngày `t`** (PIT).
  **KHÔNG dùng `ticker_prune`.**
- **Ngày cắt**: phiên giao dịch cuối mỗi tháng lịch (theo lịch `VNINDEX` trong `tav2_bq.ticker`),
  từ **2014-01-31** đến ngày cuối cùng còn đủ 60 phiên forward.
- **Lọc test**: chỉ STABLE-3 payer **có `div_growth_cagr` xác định** (`div3>0`).
- **Loại**: `ticker='VNINDEX'`; dòng thiếu giá `Close` tại `t` hoặc thiếu `Close` tại `t+20`/`t+60`.
- **Ngân hàng (ICB 8355)**: production loại khỏi diễn giải (n=3). Research **giữ trong mẫu chính**
  (mẫu panel lớn hơn nhiều) nhưng báo thêm một scope `EX_BANK` làm robustness.

## 4. Biến kết quả

- `BHAR_20 = Close(t+20)/Close(t) − 1 − (VNINDEX(t+20)/VNINDEX(t) − 1)`
- `BHAR_60` tương tự với 60 phiên. **`Close` (giá điều chỉnh) là hệ quy chiếu PRIMARY** —
  cửa sổ có thể bắc qua ex-date nên `Price` (thô) sẽ dính bẫy pha loãng kế toán
  (bài học job `_103727`, HƯỚNG A: −6,83pp thuần kế toán). `Price` chỉ chạy làm đối chứng cơ học.

## 5. Giả thuyết (khoá trước)

- **H1 (PRIMARY)**: `IC(div_growth_cagr, BHAR_60) > 0,04` với `t ≥ 2,0`.
  - IC = Spearman rank correlation tính **trong từng cross-section tháng** (bỏ tháng có < 10 mã),
    IC tổng = trung bình các IC tháng.
  - `t` = `mean(IC)/SE(IC)` với **SE Newey–West lag 3** (BHAR_60 chồng lấn ~3 tháng ⇒ SE thường
    sẽ phóng đại t; khai trước, không phải lựa chọn hậu nghiệm).
- **H2 (secondary, categorical)**: `mean(BHAR_60 | GROWING) > mean(BHAR_60 | DECLINING)`,
  t-test độc lập (Welch), `p ≤ 0,05`. Báo kèm block-bootstrap theo tháng lịch (5.000 lần) vì
  quan sát chồng lấn ⇒ t-test naive quá lạc quan; **bootstrap KHÔNG lật verdict đã đăng ký**,
  chỉ để đọc độ lớn thật.
- **H3 (portfolio relevance)**: tỉ lệ `GROWING` trong tổng STABLE-3 universe (theo ticker-month).
  `< 15%` ⇒ gắn nhãn **SPARSE**.
- **Walk-forward**: IS `t ≤ 2019-12-31`, OOS `t ≥ 2020-01-01`. **Hai giai đoạn phải cùng dấu.**

## 6. Luật quyết định (§7)

| Verdict | Điều kiện |
|---|---|
| **GO** | H1 đạt (IC>0,04 ∧ t≥2,0) ở **cả IS và OOS** (cùng dấu) **VÀ** H3 không SPARSE |
| **WEAK** | H1 đạt ở đúng **một** giai đoạn (IS hoặc OOS), hoặc đạt cả hai nhưng H3 = SPARSE |
| **NO-GO** | H1 không đạt ở giai đoạn nào, hoặc IS/OOS **ngược dấu** |

H2 và BHAR_20 là **secondary** — không được dùng để lật verdict của H1 (chống cherry-pick horizon).

## 7. Robustness (báo cáo, không quyết GO)

1. Scope `EX_REGIME`: loại ngày cắt có DT5G state ∈ {0 CRISIS, 4 EX-BULL}
   (`tav2_bq.vnindex_5state_dt5g_live` — **KHÔNG** đọc `vnindex_5state`).
2. Scope `EX_BANK`: loại ICB 8355.
3. Đối chứng cơ học trên `Price`.
4. IC trên `BHAR_20`.

## 8. Artifact

`analyze.py`, `q_panel.sql`, `panel.csv`, `results_ic.csv`, `results_groups.csv`, `RESULTS.md`.
