# KẾT QUẢ — ISS/rights offering, test TRUNG VỊ: **CONFIRMED_BUT_RARE**

- **Job**: `Taylor_20260821_111228` (HƯỚNG C_RERUN) · **PREREG**: `PREREG.md`, commit `36c8b2fd`
  (đăng ký TRƯỚC khi chạy test outcome)
- **Script**: `analyze.py` · **Artifact**: `iss_ledger.csv`, `results_median.csv`, `results_h3.csv`,
  `results_h3_hits.csv` · Dữ liệu H1/H2 **tái dùng** `../iss_event_study_20260821/events.csv`+`control.csv`
- **KHÔNG WIRE.** Chờ Mike review + quant-skeptic. **0 deviation** so với PREREG.
- ⚠️ **Đây là LẦN NHÌN THỨ HAI trên cùng một mẫu** (PREREG §0). Xem §5 trước khi dùng p-value.

## 1. Verdict

| | |
|---|---|
| **PREREG §3** | **CONFIRMED_BUT_RARE** — H1 đạt ∧ H2 đạt ∧ dấu nhất quán IS+OOS ∧ **H3 hit = 1,65% < 5%** |
| **H1 (PRIMARY)** | `median(BHAR_60_close)` = **−3,51pp** (< −2pp), Wilcoxon **p = 2,6e−4**, 60,4% sự kiện âm ✓ |
| **H2 (điều kiện CẦN)** | `median(net_close)` (event − control ghép cặp ngành/ngày) = **−2,34pp**, Wilcoxon **p = 1,1e−3**, 57,9% âm ✓ — hiệu ứng **sống qua ghép cặp** |
| **H3 (portfolio impact)** | **34 / 2.056 deal (1,65%)** có ISS/Rights `executed` với ex-date trong [entry−60, entry]. IS 1,53% · OOS 1,73% · BAL 2,18% · LAG 1,48% |
| **Điều đáng lo nhất** | Ngưỡng **−2pp** mong manh: block-bootstrap cho `P(median ≥ −2pp)` = **13% (H1)**, **28% (H2)**, và **48% (H2 trên IS)**. "Có hiệu ứng âm" vững; "hiệu ứng ít nhất 2pp" thì **chưa**. |

## 2. H1 / H2 — trung vị, `Close` (PRIMARY)

| metric | scope | n | median | mean | %âm | Wilcoxon p | block-boot 95% (median) | P(med ≥ −2pp) |
|---|---|---:|---:|---:|---:|---:|---|---:|
| **BHAR_60** | **FULL** | 632 | **−3,51pp** | +1,22pp | 60,4% | **2,6e−4** | [−6,01 ; −1,47] | 13,0% |
| BHAR_60 | IS (≤2019) | 431 | −3,32pp | −0,03pp | 60,6% | 1,8e−3 | [−6,29 ; −1,08] | 21,0% |
| BHAR_60 | OOS (≥2020) | 201 | −3,59pp | +3,91pp | 60,2% | 5,3e−2 | [−8,08 ; −0,58] | 21,7% |
| BHAR_60 | EX_REGIME | 575 | −3,72pp | −0,47pp | 62,1% | **4,4e−5** | [−6,09 ; −1,62] | 7,5% |
| BHAR_60 | EX_REGIME_OOS | 155 | **−5,27pp** | −2,32pp | 66,5% | 1,0e−3 | [−9,06 ; −1,59] | 4,4% |
| BHAR_60 | EX_REGIME_STRICT | 302 | −4,55pp | −1,81pp | 64,9% | 1,6e−4 | [−7,10 ; −1,59] | 6,3% |
| **net (ghép cặp)** | **FULL** | 624 | **−2,34pp** | +1,57pp | 57,9% | **1,1e−3** | [−3,57 ; −1,29] | 27,9% |
| net | IS | 423 | −2,04pp | +1,24pp | 56,5% | 3,6e−2 | [−3,79 ; −0,75] | **48,5%** |
| net | OOS | 201 | −3,19pp | +2,26pp | 60,7% | 6,6e−3 | [−5,20 ; −1,19] | 11,5% |
| net | EX_REGIME_STRICT | 302 | −2,94pp | −0,95pp | 59,3% | 9,5e−4 | [−5,20 ; −1,39] | 10,2% |

**Đọc đúng ba điều:**
1. **Dấu tuyệt đối nhất quán** — 28/28 dòng scope×metric đều có trung vị âm; IS và OOS cùng dấu ở
   cả H1 lẫn H2; %âm luôn 55–67%. Đây là phần vững nhất của kết quả.
2. **Mean vẫn dương ở FULL/OOS** (+1,22pp / +3,91pp) — đúng như study trước: phân phối **lệch phải
   rất mạnh**, vài sự kiện tăng gấp bội kéo trung bình lên. Nói cách khác: rights offering làm
   **đa số** mã kém đi, nhưng **kỳ vọng** không âm. Với danh mục đủ phân tán, đại lượng có ý nghĩa
   kinh tế là **kỳ vọng**, không phải trung vị — đây là lý do KHÔNG được đọc kết quả này thành
   "bán/tránh mọi mã có rights offering".
3. **Loại CRISIS/EX-BULL làm hiệu ứng MẠNH lên** (−3,72pp, p=4,4e−5; OOS −5,27pp) — nhất quán với
   giả thuyết cơ chế (pha loãng + tín hiệu cần vốn) hơn là với nhiễu regime.

**Đối chứng cơ học `Price`**: `BHAR_60_price` FULL −3,99pp (p<1e−5) — **cùng kết luận, mạnh hơn**.
Nhưng `net_price` FULL chỉ −1,55pp (p=0,040) và **IS p=0,246 (không đạt)**. ⇒ phần hiệu ứng ròng
đo trên giá thô yếu hơn hẳn trên giá điều chỉnh. `Close` là hệ quy chiếu PRIMARY đã đăng ký (cửa sổ
bắt đầu TẠI/SAU ex-date nên `Close` không dính bẫy pha loãng), nhưng **khoảng cách này là một vết
cần quant-skeptic soi**, không được lờ đi.

## 3. H3 — tần suất ISS "trúng" vào danh mục THẬT (số quan trọng nhất)

Ghép 2.056 deal cổ phiếu BAL/LAG (CSV pin R3 2026-08-03, đã loại 526 `ETF_PARK`) với 1.568 sự kiện
ISS/Rights `executed`; điều kiện trúng = `exright_date ∈ [entry_date − 60 ngày, entry_date]`.

| scope | n_deal | n_hit | hit% | n_mã | n_mã dính |
|---|---:|---:|---:|---:|---:|
| **FULL** | **2.056** | **34** | **1,65%** | 610 | 30 |
| IS (≤2019) | 786 | 12 | 1,53% | 302 | 12 |
| OOS (≥2020) | 1.270 | 22 | 1,73% | 500 | 19 |
| BAL | 505 | 11 | 2,18% | 235 | 11 |
| LAG | 1.551 | 23 | 1,48% | 521 | 23 |

Trong 34 deal dính: trung vị **28,5 ngày** kể từ ex-date (min 2, max 58) ⇒ phân bố khá đều trong
cửa sổ, không dồn sát ex-date.

**Cận trên độ lớn tác động danh mục** (số học trên chính các số đã báo, KHÔNG phải một test mới):
kể cả nếu một cổng loại bỏ TOÀN BỘ 34 deal này và thu trọn hiệu ứng ròng −2,34pp, mức cải thiện
trung bình trên toàn bộ deal chỉ ≈ `1,65% × 2,34pp ≈ **0,04pp**`. Đó là mức **không đo được** trong
NAV backtest, và n=34 thì **không đủ để kiểm định** chính cổng đó.

## 4. Hàm ý

1. **Hiệu ứng có thật ở tầng trung vị, nhưng KHÔNG đáng wire thành cổng vào/ra.** Tần suất trúng
   1,65% khiến mọi phiên bản gate/exit-trigger đều là thay đổi cấu trúc lớn để đổi lấy ~0,04pp.
2. **Chỗ dùng đúng của tri thức này là DISPLAY/due-diligence**, không phải selector: khi một mã đang
   xét vừa có rights offering trong 60 phiên gần nhất, hiển thị cảnh báo cho người đọc plan —
   giống cách `div_growth_signal` và `yield_floor` đang dùng. **Không tự wire; đó là đề xuất.**
3. **Không mở rộng mẫu để "cứu" độ lớn.** Nếu Mike/user muốn theo tiếp, hướng đúng là đổi CÂU HỎI
   sang cái có tần suất đủ (vd toàn bộ ISS mọi `issue_method_code`, hoặc pha loãng theo `exercise_ratio`
   liên tục) và **PREREG lại từ đầu trên mẫu chưa nhìn** — không phải nhìn lần thứ ba vào 632 sự kiện này.

## 5. Giới hạn tự khai (đọc TRƯỚC khi trích số)

- **Lần nhìn thứ hai trên cùng mẫu.** p-value ở đây không có diễn giải tần suất sạch. Đọc
  Bonferroni 2 lần nhìn (`p ≤ 0,025`): H1 FULL (2,6e−4) và H2 FULL (1,1e−3) **vẫn qua**; nhưng
  **H2 trên IS (p=0,036) KHÔNG qua** ngưỡng điều chỉnh.
- **Ngưỡng −2pp mong manh** — xem cột `P(med ≥ −2pp)`: 13% / 28% / 48% (IS). Nếu PREREG đã đặt
  ngưỡng −3pp thay vì −2pp thì H2 đã trượt. Verdict này **nhạy với một hằng số đặt trước**.
- **Quan sát không độc lập hoàn toàn**: 632 sự kiện / 369 mã ⇒ trung bình 1,7 sự kiện/mã; block
  bootstrap theo tháng lịch xử lý phần chồng lấn thời gian, KHÔNG xử lý phần lặp theo mã.
- **Độ phủ**: 1.568 sự kiện Rights → 910 có dòng giá (`corporate_action` phủ 1.792 mã, `ticker`
  chỉ 1.272) → 632 `in_universe_pit`. Đây là giới hạn ĐỘ PHỦ dữ liệu, không phải survivorship
  (0 sự kiện mất vì thiếu 60 phiên giá phía sau).
- **`net_price` không sống qua IS** (§2) — dấu hiệu duy nhất trong bộ số này gợi ý một phần hiệu
  ứng ròng đến từ hệ quy chiếu giá điều chỉnh chứ không từ bản thân sự kiện.
