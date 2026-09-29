# PB thích ứng theo chu kỳ cho phễu candidate discretionary — thiết kế + test sơ bộ

> Job `Taylor_20260830_060950` · 2026-08-30 · **RESEARCH-ONLY, chưa sửa
> `bin/discretionary_candidate_funnel.py`.** User duyệt hướng 13:08 ICT: nới ngưỡng PB cho phễu
> candidate NHƯNG phải adaptive theo chu kỳ thị trường, không phải ngưỡng tuyệt đối cố định.

## Kết luận 1 dòng

**Khả thi.** Thay `PB<1,0` tuyệt đối bằng **OR-logic**: `PB<1,0 (giữ nguyên) OR (PB nằm trong
percentile ≤55% cross-sectional PIT của universe_pit hôm đó AND PB<1,5)` — bắt được cả TV1
(percentile 50,1%) và DGC (45,9%) hôm nay, mà cohort washout+PIT lịch sử qua 7 episode dd52≤−20%
chỉ phình **+5,3%** (1193→1256 tên) và hôm nay phình **+15%** (113→130 tên) với 17 tên mới đều có
washout thật (dd52 −31% đến −58%). Không dùng Value Radar — percentile tính trực tiếp từ cross-
section `universe_pit` cùng ngày, tôn trọng đúng ràng buộc 08-22.

## 1. Ràng buộc phải tôn trọng (đã đọc lại trước khi thiết kế)

Theo `kb/memory/Mike.md` consolidation 2026-08-22T14:26/17:36 (`breadth-vs-radar-matrix-20260822`,
`b1-b2-b3-combined-20260822`): **breadth-tercile PIT** (`COUNTIF(Close>MA200)/COUNT(*)` trên
`tav2_mike.universe_pit`, phân vị trong 252 phiên TRƯỚC — không gồm hôm nay) là trục điều kiện
MẶC ĐỊNH cho phân tích conditional toàn fleet từ nay, thay Value Radar zone — vì radar là **kỷ
nguyên trá hình** (54% số năm bị 1 nhãn chiếm ≥90% phiên) trong khi breadth biến thiên thật trong
từng năm. Value Radar giữ vai trò **DISPLAY-ONLY** trong báo cáo (§6b coding_guidelines), **cấm**
dùng làm input gate cho sizing/screening.

Dispatch cho phép 2 lối thiết kế tôn trọng ràng buộc này: (a) ngưỡng điều kiện theo breadth-tercile,
hoặc (b) **percentile PIT cross-sectional** (không dùng Value Radar). Job này chọn **(b)** —
percentile PB tính trực tiếp trên cross-section `universe_pit` cùng ngày — vì nó tự động PIT
(không cần cửa sổ rolling, không look-ahead by construction: chỉ dùng dữ liệu CÙNG NGÀY, không
dùng lịch sử) và không cần dựng thêm bảng breadth×PB×episode với N=7 episode vốn đã mỏng. Đây
KHÔNG dùng Value Radar ở bất kỳ bước nào.

## 2. Phát hiện nền — PB<1,0 tuyệt đối KHÔNG ổn định độ chọn lọc qua chu kỳ (bằng chứng trực tiếp)

Cross-section PB toàn universe (bảng `tav2_bq.ticker`, `Volume>0`) tại các mốc arm/trough/end của
7 episode dd52≤−20% (`historical_pb_cross_section_by_episode.csv`):

| Episode | Mốc | median PB | % universe PB<1,0 (= độ chọn lọc thật của ngưỡng "1,0") |
|---|---|---|---|
| 2011-05 | trough | 0,47 | **86,5%** — gần như CẢ THỊ TRƯỜNG "qua" PB<1 |
| 2012-08 | trough | 0,52 | 86,2% |
| 2020-03 | trough | 0,70 | 68,9% |
| 2022-05 | trough | 0,72 | 66,6% |
| 2018-05 | arm | 0,90 | 57,5% |
| 2009-11 | arm | 1,43 | **19,4%** — chọn lọc thật sự |
| **Hôm nay 2026-08-30** | — | **1,08** (universe_pit) | **45,0%** |

**Đọc bảng**: ở đúng những đợt khủng hoảng hệ thống sâu nhất (2011-05, 2012-08), ngưỡng "PB<1,0"
gần như KHÔNG lọc gì cả — 86% thị trường thoả mãn nó, độ chọn lọc thật đến từ washout+dd52. Ở
những giai đoạn vừa phải/đầu chu kỳ (2009-11 arm), cùng con số "1,0" lại chọn lọc gắt (19,4%).
**Hôm nay universe_pit median PB = 1,084 — TRÙNG GẦN NHƯ TUYỆT ĐỐI với PB của chính TV1
(1,084)** — tức TV1 hiện đang nằm ĐÚNG TẠI trung vị thị trường, không phải "rẻ" hay "đắt" theo
market hiện tại, chỉ là RẺ so với chính nó lúc mới vào sleeve. Đây chính là cơ chế "ngưỡng tuyệt
đối lệch nghĩa theo chu kỳ" mà dispatch đặt ra — đã xác nhận bằng số, không phải suy diễn.

## 3. Thiết kế đề xuất

```
PB_qualify(ticker, date) =
    (PB(ticker,date) < 1.0)                                   # giữ nguyên nhánh cũ, KHÔNG rút bớt
    OR (
        percentile_rank(PB(ticker,date) trong universe_pit cross-section CÙNG ngày date) <= 0.55
        AND PB(ticker,date) < 1.5                              # trần chống-trôi (xem §6)
    )
```

- **PIT by construction**: percentile chỉ dùng dữ liệu CÙNG NGÀY (cross-section), không cần
  window lịch sử → không có rủi ro look-ahead kiểu §16/§23 rolling-window.
- **Cơ sở percentile = `universe_pit` (đã lọc chất lượng), KHÔNG phải toàn bộ mã niêm yết** —
  đúng với cách funnel hiện tại đã giới hạn scan vào `universe_pit`. Đã thử cả 2 cơ sở: dùng
  toàn bộ mã có Volume>0 (median PB hôm nay 0,88, TV1 rơi vào percentile 60,6% — bị pha loãng bởi
  một lô mã penny/junk PB cực thấp KHÔNG nằm trong universe_pit) cho kết quả khác hẳn — xác nhận
  `universe_pit` là cơ sở đúng (so sánh TV1/DGC với các mã CÙNG hạng chất lượng, không so với rác).
- **OR, không phải THAY THẾ**: giữ nguyên nhánh `PB<1,0` để không mất một tên nào cohort cũ đang
  bắt được — percentile chỉ CỘNG THÊM tên mới, không bao giờ RÚT tên cũ.
- **Trần chống-trôi PB<1,5**: percentile một mình không đủ an toàn — nếu thị trường vào một chu kỳ
  bull cực đoan (median PB dâng cao), percentile≤55% có thể trỏ vào những mã PB=3-4 vẫn "rẻ tương
  đối" nhưng không còn ý nghĩa "deep value" nữa. Trần 1,5 không bao giờ bó buộc ở dữ liệu đã test
  (TV1 1,084, DGC 1,005, và toàn bộ 17 tên mới hôm nay đều ≤1,166) — nó chỉ là an toàn cho tương
  lai, không đổi kết quả hiện tại.
- **Vì sao 55%, không phải 50%**: TV1 percentile hôm nay = 50,14% — NẰM SÁT ngưỡng 50% tới mức một
  ngày biến động giá bình thường có thể đẩy nó qua/lại. Chọn 55% để có biên an toàn thay vì chốt
  đúng ranh giới đã biết trước (tránh overfitting-tới-đúng-2-case).

## 4. Backtest ngược 7 episode dd52≤−20% — cohort washout(≥30%)+PIT, sensitivity theo cutoff

Universe: mọi ticker trong `universe_pit` PIT tại đúng ngày rơi sâu nhất (`worst dd_stock≤−30%`
trong cửa sổ mỗi episode), N=1.760 dòng ticker×episode. `n_absolute (PB<1,0)` = 1.193.

| Cutoff percentile | n_OR (abs OR percentile, trần PB<1,5) | Tăng so với tuyệt đối | Số tên MỚI do nhánh percentile |
|---|---|---|---|
| ≤30% | 1.196 | +0,3% | 3 |
| ≤40% | 1.208 | +1,3% | 15 |
| ≤50% | 1.227 | +2,8% | 34 |
| **≤55% (đề xuất)** | **1.256** | **+5,3%** | **63** |
| ≤60% | 1.302 | +9,1% | 109 |

→ Ở ngưỡng đề xuất 55%, phễu KHÔNG phình vô nghĩa qua toàn bộ 7 khủng hoảng lịch sử — cộng thêm
đúng 5,3% tên, và mức tăng CÀNG NHỎ ở đúng những episode khủng hoảng sâu nhất (2011-05: +0/193,
2012-08: +0/111, 2020-03: +0/157 — percentile không thêm gì vì ở đó PB<1,0 tuyệt đối ĐÃ quá lỏng
rồi, 86% thị trường qua nó, như §2 đã chỉ ra). Percentile chỉ có tác dụng đúng ở những giai đoạn
KHÔNG-khủng-hoảng-hệ-thống (2007-04 +7, 2009-11 +35, 2018-05 +18, 2022-05 +3) — đúng cơ chế cần.

## 5. Áp lên universe hôm nay — 113 → 130, bắt được cả TV1 và DGC

Washout(≥30%)+dd52(≤−20%) universe hôm nay (không lọc PB) = **187 mã** trong 355 mã `universe_pit`.
Absolute PB<1,0 = 113 (số đã biết từ `discretionary_sleeve_candidate_funnel_20260830`). OR-logic
(≤55%, trần 1,5) = **130** (+15,0%, 17 tên mới):

| Ticker | PB | Percentile | washout | dd52 |
|---|---|---|---|---|
| GEX | 1,002 | 45,6% | −41,4% | −41,4% |
| **DGC** | 1,005 | 45,9% | −58,4% | −55,1% |
| VCS | 1,016 | 46,7% | −33,2% | −33,2% |
| KDH | 1,023 | 47,0% | −50,8% | −50,8% |
| PVB | 1,034 | 47,3% | −47,9% | −47,9% |
| ELC | 1,041 | 48,2% | −44,9% | −44,9% |
| VIB | 1,064 | 49,3% | −33,2% | −31,3% |
| PXL | 1,069 | 49,6% | −47,5% | −39,9% |
| TNG | 1,081 | 49,9% | −31,6% | −31,6% |
| **TV1** | 1,084 | 50,1% | −48,0% | −48,0% |
| VDS | 1,092 | 50,7% | −52,1% | −52,1% |
| PAC | 1,093 | 51,0% | −48,7% | −40,7% |
| SZC | 1,104 | 51,3% | −49,0% | −46,6% |
| VIX | 1,110 | 52,4% | −55,7% | −55,7% |
| SHS | 1,133 | 53,0% | −45,9% | −45,9% |
| PLC | 1,136 | 53,3% | −45,8% | −45,8% |
| AGR | 1,166 | 55,0% | −34,5% | −34,5% |

Cả 17 tên đều có washout thật ≥31% và dd52≤−20% — không phải "rác lọt phễu vì nới ngưỡng", đây
đúng là các mã bị bán tháo sâu nhưng PB vừa vượt nhẹ 1,0.

**Nhắc lại — đây mới là TẦNG 1 (fear cohort).** 17 tên mới vẫn phải qua đủ quality floor
(golden floor + rating≤3), insider/redflag screen, và marginability check y hệt 113 tên cũ trước
khi có bất kỳ tên nào được coi là `fully_qualified`. Job này KHÔNG chạy lại 3 tầng đó cho 17 tên
mới — đó là việc của lần chạy funnel thật khi (nếu) đổi được duyệt.

## 6. Cảnh báo correlation-risk (yêu cầu mục 5 dispatch — chỉ FLAG, không backtest lại)

Trong 17 tên mới, **4/17 là công ty chứng khoán** (VDS, VIX, SHS, AGR) — một tỷ trọng ngành cao
bất thường so với cohort PB<1,0 cũ. `discretionary_sleeve_correlation_risk_20260830.md` đo
correlation trên cohort "PB<1,0 + washout≥30%" nói chung, KHÔNG tách riêng theo ngành — nhưng lưu ý
đã có trong chính báo cáo đó (§3): correlation đo trên nhóm **liquid** (nhóm chứng khoán/ngân hàng
thường thanh khoản cao hơn cohort deep-value trung bình) cho ρ CAO HƠN nhóm illiquid (0,30-0,49 vs
0,01-0,15 thô) — tức nếu 4 mã chứng khoán mới này có thanh khoản cao hơn trung vị cohort cũ, chúng
có khả năng mang correlation NỘI BỘ ngành cao hơn số ρ trung bình 0,17-0,25 đã dùng làm cơ sở tính
E[loss] cho sleeve 5/10/15%. **Đây là tín hiệu cần risk-auditor spot-check TRƯỚC KHI wire**, không
phải kết luận — job này không đo lại ρ cho riêng nhóm percentile-only.

## 7. Giới hạn

1. **Cutoff 55%/trần 1,5 được hiệu chỉnh biết trước TV1 (50,1%)/DGC (45,9%)** — không phải backtest
   độc lập hoàn toàn ngoài mẫu. Bằng chứng "không phình" ở §4 (chạy trên 7 episode 2007-2023,
   không dùng để chọn 55%) là lớp validate độc lập nhất có, nhưng vẫn nên đọc 55% như MỘT THAM SỐ
   THIẾT KẾ có biên an toàn (50%→55%), không phải con số tối ưu hoá thống kê.
2. **Không phải backtest lợi nhuận** — đây là thiết kế/coverage của một BỘ LỌC SÀNG LỌC (fear
   cohort layer), không phải tín hiệu return-dự đoán. DSR/PBO không áp dụng trực tiếp (không có
   chuỗi return để kiểm định); quy chuẩn liên quan là coverage/selectivity, đã trình bày ở §4.
3. **Percentile cơ sở `universe_pit` không có sẵn PIT cho MỌI episode cũ theo đúng nghĩa "đã biết
   tại thời điểm đó"** — dùng lại snapshot `in_universe=True` lịch sử từ bảng `tav2_mike.universe_pit`
   hiện tại (đã confirm bảng có dữ liệu PIT từ 2000, không phải suy diễn ngược) — đúng chuẩn PIT,
   không phải look-ahead.
4. **Chưa chạy quality floor/insider/marginability cho 17 tên mới** (§5) — cần chạy funnel thật.
5. **N=7 episode** cho bảng §4 — mẫu nhỏ như mọi phân tích dùng lại bộ episode này trong KB, đã
   biết hạn chế (2 episode đầu gần như 1 sự kiện kéo dài).

## 8. Đề xuất bước tiếp theo

**KHÔNG tự sửa** `bin/discretionary_candidate_funnel.py` trong job này (đúng phạm vi dispatch).
Nếu user muốn tiến tới wire:
1. quant-skeptic pass cho chính thiết kế này (đặc biệt tính "cutoff hiệu chỉnh biết trước 2 case"
   ở §7.1 — đây là điểm dễ bị REFUTE nhất).
2. risk-auditor spot-check correlation của cụm 4 mã chứng khoán mới (§6) trước khi cho phép chúng
   vào due-diligence sâu.
3. Nếu cả 2 pass: sửa `PB_MAX`/hàm `compute_fear_cohort()` trong
   `bin/discretionary_candidate_funnel.py` theo công thức §3, thêm cột `pb_percentile` +
   `pb_qualify_via` (`"absolute"`/`"percentile"`) vào output để người review biết tên nào qua
   nhánh nào.

## Liên quan
- `discretionary_sleeve_candidate_funnel_20260830.md` — phễu gốc (PB<1,0 tuyệt đối, 113 fear
  cohort hôm nay), job trước cùng chuỗi.
- `discretionary_sleeve_correlation_risk_20260830.md` — correlation crisis/normal, illiquid-vs-
  liquid tercile (dùng ở §6).
- `kb/memory/Mike.md` consolidation 2026-08-22 — quy ước breadth-tercile PIT / Value Radar
  display-only (tôn trọng ở §1).
- Data/code: `agents/Taylor/research/discretionary_funnel_adaptive_pb_20260830/`
  (`historical_pb_cross_section_by_episode.csv`, `coverage_comparison_pit_basis.csv`,
  `sensitivity_table_historical.csv`, `today_pb_cross_section.csv`,
  `today_fear_cohort_all_pb.csv`, `universe_pit_2006_2023.parquet`).
