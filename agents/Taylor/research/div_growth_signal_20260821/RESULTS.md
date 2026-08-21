# KẾT QUẢ — Div growth trajectory có predict forward return không? **NO-GO**

- **Job**: `Taylor_20260821_111228` (HƯỚNG B_SIGNAL) · **PREREG**: `PREREG.md`, commit `fe8290e2`
  (đăng ký TRƯỚC khi chạy bất kỳ query outcome nào)
- **Script**: `analyze.py` · **SQL**: `q_panel.sql` · **Artifact**: `panel.csv`, `panel_enriched.csv`,
  `results_ic.csv`, `results_ic_monthly.csv`, `results_groups.csv`, `results_h3.csv`
- **KHÔNG WIRE.** `div_growth_signal` giữ nguyên **DISPLAY_ONLY** như commit `67a20f88`.
  Chờ Mike review + quant-skeptic.
- **0 deviation** so với PREREG (không có `DEVIATIONS.md`).

## 1. Verdict

| | |
|---|---|
| **PREREG §6** | **NO-GO** — H1 **không đạt ở giai đoạn nào**: IC(cagr, BHAR_60) = **+0,0240** (FULL, t_NW=1,84), IS **+0,0368** (t=1,64), OOS **+0,0121** (t=0,90). Ngưỡng đăng ký: IC>0,04 **và** t≥2,0. |
| **Độ bền của verdict** | Không phụ thuộc lựa chọn SE: IC **thấp hơn ngưỡng 0,04 ở MỌI scope**, kể cả khi dùng t naive (FULL t=2,57 nhưng IC vẫn 0,024). |
| **H2 (categorical)** | **BÁC BỎ, và NGƯỢC HƯỚNG**: `GROWING − DECLINING` BHAR_60 = **−0,23pp** (t=−0,69, p=0,49); IS −0,26pp, OOS −0,16pp. Không giai đoạn nào dương. |
| **H3 (portfolio relevance)** | **KHÔNG SPARSE** — GROWING = **32,9%** của STABLE-3 universe (IS 34,4% / OOS 31,8%), xa ngưỡng 15%. Đây là mảnh DUY NHẤT của giả thuyết đứng vững, nhưng nó chỉ nói "nhãn đủ phổ biến để đáng đo", không nói nhãn có giá trị dự báo. |

## 2. Mẫu

- **52.960 ticker-month**, 549 mã, **150 tháng** (2014-01-27 → 2026-06-15), universe_pit PIT tại
  đúng ngày cắt, `Close` (giá điều chỉnh) làm hệ quy chiếu primary.
- STABLE-3 = **17.526 ticker-month (33,1%** của panel). Trong đó có `div_growth_cagr` xác định
  (`div3>0`) = **15.094**; `NO_HISTORY` (stable3 nhưng cửa sổ thứ 4 rỗng) = 2.432 (13,9%).
- Phân bố nhãn trong STABLE-3: GROWING 32,9% · DECLINING 32,4% · STABLE 20,9% · NO_HISTORY 13,9%.
- Trung bình **100 mã/cross-section tháng** (IS 86 / OOS 114) ⇒ IC theo tháng có mẫu đủ dày.
- **N độc lập KHÔNG phải 15.094.** Đơn vị độc lập gần nhất = **149 tháng** (và ngay cả thế BHAR_60
  vẫn chồng lấn ~3 tháng ⇒ đã dùng SE Newey–West lag 3 như đăng ký).

## 3. H1 — IC Spearman theo cross-section tháng (PRIMARY)

| scope | y | n_months | mean IC | median IC | % tháng IC>0 | t (NW lag3) | t (naive) |
|---|---|---:|---:|---:|---:|---:|---:|
| **FULL** | **BHAR_60** | 149 | **+0,0240** | +0,0274 | 59,1% | **1,84** | 2,57 |
| **IS (≤2019)** | **BHAR_60** | 72 | **+0,0368** | +0,0410 | 61,1% | **1,64** | 2,43 |
| **OOS (≥2020)** | **BHAR_60** | 77 | **+0,0121** | +0,0202 | 57,1% | **0,90** | 1,08 |
| EX_REGIME (bỏ CRISIS/EX-BULL) | BHAR_60 | 128 | +0,0241 | +0,0221 | 57,0% | 1,62 | 2,28 |
| EX_BANK (bỏ ICB 8355) | BHAR_60 | 149 | +0,0231 | +0,0301 | 60,4% | 1,71 | 2,42 |
| FULL | BHAR_20 | 150 | +0,0113 | +0,0089 | 52,7% | 1,21 | 1,23 |
| OOS | BHAR_20 | 78 | **+0,0009** | +0,0056 | 51,3% | 0,09 | 0,08 |
| FULL | BHAR_60 (`Price` đối chứng) | 149 | +0,0215 | +0,0215 | 55,0% | 1,66 | 2,28 |

**Đọc đúng**: dấu **nhất quán dương ở mọi scope** và 59% tháng dương — tức đây không phải nhiễu
thuần túy — nhưng **độ lớn chỉ bằng ~60% ngưỡng đăng ký** và **suy giảm rõ từ IS sang OOS**
(0,037 → 0,012, giảm 67%). BHAR_20 gần như bằng 0 ở OOS (+0,0009). Đây là hồ sơ điển hình của
một biến có tương quan thật nhưng **quá yếu để làm entry factor**, chứ không phải một edge bị
che bởi nhiễu.

**Đối chứng cơ học trên `Price`**: +0,0215 vs `Close` +0,0240 — gần trùng ⇒ bẫy hệ quy chiếu
`Close`-vs-`Price` KHÔNG chi phối kết quả (khác HƯỚNG A job `_103727` nơi nó cắn −6,83pp).

## 4. H2 — nhãn categorical (secondary)

`BHAR_60` trung bình, `Close`:

| scope | GROWING | STABLE | DECLINING | GROWING−DECLINING | t Welch | p | block-boot 95% |
|---|---:|---:|---:|---:|---:|---:|---|
| FULL | +0,45pp (n=5.707) | +0,97pp (n=3.608) | +0,68pp (n=5.612) | **−0,23pp** | −0,69 | 0,49 | [−0,95 ; +0,51] |
| IS | −0,30pp | −0,38pp | −0,03pp | −0,26pp | −0,57 | 0,57 | [−1,40 ; +0,91] |
| OOS | +1,04pp | +1,72pp | +1,20pp | −0,16pp | −0,34 | 0,74 | [−1,04 ; +0,73] |
| EX_REGIME | +0,33pp | +0,54pp | +0,66pp | −0,33pp | −0,93 | 0,35 | [−1,17 ; +0,47] |

⇒ **Nhãn 3 bậc không tách được lợi suất.** Nhóm giữa (STABLE) thậm chí có mean cao nhất ở FULL và
OOS — quan hệ không đơn điệu theo nhãn.

**Mâu thuẫn biểu kiến IC dương vs H2 âm — không phải lỗi tính**: IC là tương quan **hạng, tính
trong từng tháng** (so sánh tương đối cùng thời điểm); H2 là hiệu **trung bình gộp qua 150 tháng**
(bị chi phối bởi vài tháng đuôi và bởi thành phần mã khác nhau giữa 2 nhóm). Hai đại lượng trả lời
2 câu khác nhau. Điều đáng chú ý: **cách production đang dùng nhãn (3 bậc, ngưỡng cứng ±5%) là
cách MẤT thông tin nhất** — phần tín hiệu ít ỏi nằm ở biến liên tục và ở thứ hạng trong cùng
cross-section, không ở nhãn.

## 5. Hàm ý

1. **Giữ `div_growth_signal` ở DISPLAY_ONLY.** Không có cơ sở nâng lên entry factor/scoring.
2. **Nếu về sau muốn thử lại, phải PREREG RIÊNG** và đổi thiết kế theo đúng chỗ tín hiệu nằm:
   dùng **z-score/rank của `cagr` trong cross-section** (không phải nhãn 3 bậc), và test như một
   **tilt trọng số trong rổ đã chọn**, không phải cổng vào/ra. Kết quả job này KHÔNG cho phép
   kết luận trước về hướng đó.
3. **Không được diễn giải kết quả này thành "cổ tức tăng là xấu"** — H2 âm nhưng CI bootstrap chứa
   0 ở mọi scope; đây là "không phân biệt được", không phải "ngược dấu có ý nghĩa".
