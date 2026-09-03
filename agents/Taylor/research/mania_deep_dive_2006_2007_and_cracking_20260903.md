# Mania deep-dive: 2006-2007 lịch sử + "mania rạn nứt ở đỉnh" (cracking mania)

> Job `Taylor_20260903_150931` (follow-up của `Taylor_20260903_144602`) · 2026-09-03 ·
> **RESEARCH-ONLY, không wire production.** Đọc trước:
> `market_mania_euphoria_detector_20260903.md` (detector chính, N=7 2008-2026) — file này bổ sung,
> không thay thế.

---

## PHẦN 1 — Mania 2006-2007: có "cùng loài" với 7 episode 2008-2026 không?

### 1.1 Tính khả thi dữ liệu — KHÔNG áp được detector chuẩn nguyên bản

Đo trực tiếp trên BQ (`tav2_bq.ticker` JOIN `tav2_mike.universe_pit`), theo tháng 2004-2008:

| Giai đoạn | n_ticker (mọi mã) | n có `MA200` | n `universe_pit` |
|---|---:|---:|---:|
| 2005-01 | 16 | 13 | 8 |
| 2006-01 | 26 | 16 | 13 |
| 2006-04 (đỉnh đợt 1) | 28 | 17 | 19 |
| 2006-08 (đáy giữa 2 đợt) | 37 | 18 | 24 |
| 2007-03 (đỉnh đợt 2) | 132 | 30 | 98 |
| 2007-09 | 143 | 55 | 97 |
| 2007-10 | 149 | **131** | 112 |
| 2008-06 (panel chính bắt đầu) | 215 | 139 | 154 |

`n có MA200` nhảy vọt từ 55 (2007-09) lên 131 (2007-10) — **artifact cơ học**: MA200 cần 200 phiên
lịch sử từ ngày niêm yết, nên hầu hết mã niêm yết 2006-2007 (làn sóng IPO lớn nhất giai đoạn này)
chưa có MA200 hợp lệ suốt cả 2 đợt mania. Breadth tính trên 17-30 mã "có MA200" trong khi thị
trường thực tế đã có hàng trăm mã giao dịch — **không đại diện, không dùng breadth_pct252 nguyên
bản được**. CLAUDE.md §BigQuery bẫy #4 (2006≈19 mã) đã cảnh báo đúng hướng nhưng con số MA200-ready
còn thấp hơn cả `universe_pit` thô.

→ **Xác nhận giả thuyết dispatch: bỏ qua áp detector chuẩn, chuyển sang mô tả (descriptive).**

### 1.2 Phân tích descriptive thay thế — dùng `VNINDEX.csv` local

Nguồn: `data/VNINDEX.csv` (cột `Close`, `Breadth_MA20/50/200`, `VNINDEX_PE`, `VNINDEX_PE_PERCENTILE`,
`Trading_Value` — self-contained, không qua BQ). `Breadth_MA20/50/200` có dữ liệu từ đầu 2005;
`VNINDEX_PE` có từ 2006-04 (điểm mù: không có PE cho toàn bộ đợt 1). Đây là mức breadth THÔ (không
percentile hoá theo lịch sử của chính nó — lịch sử quá ngắn để percentile có nghĩa), chỉ dùng để
mô tả xu hướng, không so trực tiếp số với `breadth_pct252` của detector chính.

**Xác định ranh giới 2 đợt bằng đỉnh/đáy VNINDEX thực đo** (không suy đoán):

| Đợt | Đáy trước | Đỉnh | Return trong đợt | Thời gian |
|---|---|---|---:|---|
| **Đợt 1 (H1-2006)** | 2005-02-01 (232,41) | **2006-04-25 (632,69)** | **+172,3%** | ~14 tháng |
| Điều chỉnh giữa 2 đợt | | 2006-08-02 (399,80) | −36,8% từ đỉnh đợt 1 | ~3 tháng |
| **Đợt 2 (H2-2006→Q1-2007)** | 2006-08-02 (399,80) | **2007-03-12 (1.170,67)** | **+192,7%** | ~7 tháng |

(User nhớ đỉnh đợt 2 là 1.170,67 ngày 12/03/2007 — khớp chính xác với đỉnh đo được từ dữ liệu.)

**Hậu quả sau mỗi đỉnh** (VNINDEX.csv, session-based, cùng công thức maxDD dùng cho detector chính):

| Đỉnh | +1M | +2M | +3M | +6M | +12M | **maxDD trong 12 tháng sau** |
|---|---:|---:|---:|---:|---:|---:|
| 2006-04-25 | −13,8% | −20,5% | −30,5% | −16,9% | +47,9% | **−36,8%** |
| 2007-03-12 | −11,2% | −9,9% | −11,3% | −21,3% | −49,8% | **−50,2%** (mở đầu crash 2007-2009 −78%) |

Trading_Value (VNINDEX.csv) tăng ~8-18 lần từ đầu 2005 đến đỉnh đợt 2 (từ ~4×10⁷ lên
~4,8×10⁹ VND/phiên quanh 2007-06), phản ánh dòng tiền đổ vào ồ ạt đúng tinh thần "mua bất chấp".

### 1.3 So sánh với N=7 episode 2008-2026 (detector chính)

| Chỉ số | N=7 (2008-2026) | Đợt 2006-2007 |
|---|---|---|
| Return trong episode | +2,3% → +15,4% (21-41 phiên) | **+172,3% / +192,7%** (7-14 tháng) |
| maxDD trong 6-12 tháng sau | mean −14,3% (6M) | **−36,8% / −50,2%** (12M) |

Về **độ lớn**, 2 đợt 2006-2007 hơn N=7 khoảng **một bậc độ lớn** (return gấp ~15-20 lần biên độ
trung bình N=7; maxDD sau đó gấp 2,5-3,5 lần mean N=7) — không phải cùng phân phối.

### 1.4 Kết luận trung thực

**KHÔNG cùng loài với 7 episode 2008-2026 — là bubble sơ khai thị trường non trẻ**, không gộp vào
N thành N=9. Hai lý do độc lập, cả hai đều đủ để loại riêng:
1. **Chất lượng dữ liệu khác hẳn**: universe/MA200-coverage quá mỏng để tính chỉ báo breadth
   percentile theo đúng phương pháp — bất kỳ con số breadth nào tính ra cho giai đoạn này đều
   không so sánh được ngang hàng với N=7 (dùng universe hàng trăm-nghìn mã).
2. **Độ lớn khác hẳn**: biên độ tăng (+172-193% qua nhiều tháng) và hậu quả (−37% đến −50% maxDD
   12M, mở đầu một cuộc sập −78% kéo dài 2 năm) lớn hơn N=7 một bậc — đặc trưng bubble cổ điển của
   thị trường mới mở cửa (IPO wave 2006-2007, margin/tín dụng chưa có khung pháp lý, nhà đầu tư cá
   nhân lần đầu tiếp cận chứng khoán), khác về BẢN CHẤT với các episode "junk-thắng-quality trong
   một thị trường đã trưởng thành hơn" mà detector chính đo.

Nếu tương lai cần trích dẫn 2006-2007 như tiền lệ lịch sử (ví dụ minh hoạ "mania cực đoan nhất VN
từng có") — dùng được, nhưng phải nói rõ đây là quan sát ĐỊNH TÍNH ngoài mẫu N=7, không phải một
điểm dữ liệu thứ 8/9 trong cùng thống kê.

---

## PHẦN 2 — "Mania rạn nứt ở đỉnh" (cracking mania)

### 2.1 Định nghĩa chỉ báo

**Chân A — Divergence** (giá làm đỉnh mới trong khi breadth đã RƠI so với chính đỉnh gần đây của
nó — không phải mức tuyệt đối thấp, vì tại 2022-01-06 breadth_pct252 vẫn ở 0,62, TRÊN median,
nhưng đã rơi từ 0,99 năm tuần trước đó):
```
new_high_126(t)      = VNINDEX_close(t) là max trong 126 phiên gần nhất (kể cả t)
breadth_recent_max_63(t) = max(breadth_pct252) trong 63 phiên gần nhất (kể cả t)
breadth_drop(t)       = breadth_recent_max_63(t) − breadth_pct252(t)
DIVERGE_DAY            = new_high_126(t) VÀ breadth_drop(t) >= 0,30
```
`breadth_pct252` tái dùng nguyên hàm PIT-causal từ detector chính (percentile 252 phiên trước, loại
t). Ngưỡng 0,30 chọn bằng must-catch test (§2.3), không phải grid-search tối ưu hoá.

**Chân B — Concentration** (một/vài NHÓM ngành gánh cả chỉ số, phần còn lại không tăng — dùng
`ICB_Code` làm nhóm ngành thay vì Risk_Rating vì user yêu cầu rõ "theo NHÓM cổ phiếu"):
```
sector(ticker) = FLOOR(ICB_Code/1000)*1000            -- gộp về 9 nhóm ngành lớn ICB
sector_ret21(sector,t) = median 21-phiên log-return của các mã trong sector đó (universe_pit)
conc_spread(t) = max(sector_ret21) − median(sector_ret21)  -- nhóm dẫn đầu hơn nhóm trung vị bao nhiêu
conc_spread_pct252(t) = phân vị của conc_spread(t) so với chính nó, 252 phiên trước (PIT causal)
CONC_DAY = conc_spread_pct252(t) >= 0,90
```
Tính trong BigQuery (`crack/q_sector_dispersion.sql`, window function `LAG` + `APPROX_QUANTILES`,
176 MB, panel 2007-04→2026-09, 4.828 dòng), join với panel breadth có sẵn.

**CRACK_DAY = DIVERGE_DAY VÀ CONC_DAY** (thử nghiệm; xem §2.4 vì sao KHÔNG dùng làm chỉ báo chính).

### 2.2 Nguồn dữ liệu + PIT

- `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (in_universe=TRUE), cắt panel 2008-06-01→2026-09-03
  (khớp panel detector chính, 4.558 phiên).
- `ICB_Code` là mã ngành chi tiết (STRING/FLOAT, ~40+ nhóm nhỏ) — gộp về hàng nghìn (`FLOOR/1000`)
  để có nhóm đủ lớn (>=5 mã/ngày, lọc `HAVING n>=5`), tránh nhóm rác 1-2 mã.
- KHÔNG dùng `profit_*`. `sector_ret21`/`conc_spread`/`breadth_drop` chỉ dùng dữ liệu tính đến t.
- Artifact: `mania_20260903/crack/q_sector_dispersion.sql`, `sector_dispersion.csv`,
  `analyze_crack.py`, `crack_daily.csv`, `events_diverge_day.csv`, `events_conc_day.csv`,
  `events_crack_day.csv`.

### 2.3 Must-catch test — 2022-01-06 và 2018-04

**2022-01-06 (đỉnh mọi thời đại VNINDEX, 1.528,57) — chính là case định nghĩa "mania rạn nứt".**
DIVERGE_DAY flag = **TRUE** đúng ngày này (`breadth_drop=0,369`: breadth_pct252 rơi từ đỉnh
0,992 (2021-11-18) xuống còn 0,623 ngày 2022-01-06, trong khi VNINDEX vẫn đang làm đỉnh mới —
đúng cơ chế "giá lên bằng ít mã dần" mà finding 08-31 mô tả bằng lời).

**2018-04 (đỉnh 1.204,33 kèm điều chỉnh sau đó −25,8% trong 6 tháng)**: cửa sổ 2018-02-27→04-09
có 13/30 phiên DIVERGE_DAY (chuỗi liên tục dài nhất trong toàn bộ N=13 episode) — **cũng bắt được**.

CONC_DAY riêng lẻ **không** fire trong cả 2 cửa sổ trên (0 ngày trong 2018-04; 2022-01-06 riêng lẻ
CONC=False, CONC gần nhất là 2022-01-21→27, 2 tuần SAU đỉnh) — → §2.4 giải thích tại sao AND
với CONC làm mất case định nghĩa.

### 2.4 Backtest N=13 (DIVERGE) — outcome + so sánh 2 chân riêng lẻ

**DIVERGE_DAY, N=13 episode** (gộp gap≤10 phiên, 2016-2026, panel 2008-06 khởi động → episode đầu
tiên chỉ có thể xuất hiện sau khi đủ 252+63 phiên warm-up của breadth_pct252/breadth_recent_max_63,
nên N=13 hết nằm từ 2016 trở đi dù panel bắt đầu 2008):

| Horizon | n | mean | median | %âm |
|---|---:|---:|---:|---:|
| +1 tháng | 13 | −1,9% | −1,8% | 62% |
| +3 tháng | 13 | +0,2% | −3,4% | 62% |
| +6 tháng | 12 | −0,6% | +4,2% | 42% |
| **maxDD trong 6 tháng sau** | **13** | **−18,0%** | **−16,4%** | **100%** |

**CONC_DAY riêng lẻ, N=64 episode** (quá thường xuyên để là tín hiệu — theo THIẾT KẾ, ngưỡng p90
tự nhiên flag ~10% số phiên, đo được 10,2%, khớp): mean maxDD-6M −14,7%, median −13,0%. **CONC một
mình KHÔNG đặc trưng cho đỉnh** — nhiều episode CONC nằm ở ĐÁY/giai đoạn phục hồi (vd
2011-12-15→2012-01-12, VNINDEX ở gần đáy 348-364, sau đó +15,9%/+35,6%/+20,3% — phân tán ngành cao
vì dòng tiền luân chuyển vào nhóm dẫn dắt phục hồi, không phải dấu hiệu mania). CONC là tín hiệu
"phân tán ngành cao" trung tính hướng, không riêng đỉnh.

**CRACK_DAY (AND cả 2, gap≤10 phiên), N=6**: mean maxDD-6M −16,5%, median −14,4% — **nhưng làm
MẤT case định nghĩa 2022-01-06** (không nằm trong danh sách 6 episode, vì CONC gần nhất cách xa
>10 phiên). Kết luận: **CONC không cộng hưởng đúng lúc với DIVERGE ở case chuẩn** — AND hai chân
làm hỏng đúng test quan trọng nhất thay vì làm chỉ báo chặt hơn. **Dùng DIVERGE_DAY một mình làm
chỉ báo chính, KHÔNG AND với CONC.**

### 2.5 Base rate — cảnh báo bắt buộc trước khi diễn giải "100% có maxDD"

Đo base rate KHÔNG điều kiện (mọi ngày, lấy mẫu mỗi 21 phiên để giảm chồng lấn, cùng công thức
maxDD-6M, N=207 cửa sổ 2008-2026):

| | Base rate (không điều kiện) | DIVERGE (N=13) | CONC (N=64) |
|---|---:|---:|---:|
| mean maxDD-6M | **−14,7%** | −18,0% | −14,7% |
| median maxDD-6M | **−14,2%** | −16,4% | −13,0% |
| %cửa sổ có maxDD ≤−7% | **84,1%** | 100% | 100% |
| %cửa sổ có maxDD ≤−10% | **69,6%** | — | — |

**Đây là phát hiện quan trọng nhất của §2, và áp dụng NGƯỢC LẠI cho cả finding "100% episode có
điều chỉnh ≥7%" trong detector chính (job 09-03 trước):** VNINDEX vốn dĩ dao động mạnh — **84% số
cửa sổ 6-tháng BẤT KỲ, không cần điều kiện gì, đã có sẵn một đợt sụt ≥7% ở đâu đó**. Nên câu "100%
episode X có điều chỉnh ≥7% trong 6 tháng sau" **không phải bằng chứng edge mạnh** như đọc thoáng
qua — nó gần với việc gì cũng đúng ở thị trường biến động cỡ này. **Cái thật sự phân biệt DIVERGE
với nhiễu nền là biên độ**: mean −18,0% so với nền −14,7% (chênh ~3,3pp, khiêm tốn nhưng nhất
quán theo đúng hướng), và median −16,4% so với nền −14,2%. Không dramatic, nhưng đúng hướng và
DIVERGE bắt đúng cả 2 case định nghĩa (2022-01, 2018-04) mà CONC bỏ lỡ.

### 2.6 So sánh 2 công cụ — "mania đang diễn ra" vs "mania rạn nứt"

Không có ngày nào 2 detector cùng fire (đúng theo thiết kế: detector chính đòi breadth_pct252≥0,90
DUY TRÌ ≥21 phiên; DIVERGE đòi breadth đã RƠI ≥0,30 từ đỉnh — hai điều kiện loại trừ lẫn nhau tại
cùng thời điểm). Xem lead-lag bằng khoảng cách thời gian:

| Mania episode (chính) kết thúc | DIVERGE gần nhất sau đó | Khoảng cách |
|---|---|---|
| 2016-04-05→05-06 | 2016-09-26 | ~5 tháng |
| 2020-11-04→12-25 | 2021-04-20 | ~4 tháng |
| 2025-07-15→09-05 | 2025-10-16 | ~6 tuần |

Không nhất quán đủ để gọi là "lead-lag rule" (2012/2013/2014 mania episode: DIVERGE gần nhất không
xuất hiện tới 2016-09, cách >2 năm — không có quan hệ trực tiếp). Kết luận: 2 công cụ đo 2 pha
khác nhau của cùng hiện tượng (mania breadth-rộng ĐANG diễn ra vs breadth đã bắt đầu RẠN NỨT trong
khi giá vẫn quán tính tăng), nhưng **không đủ bằng chứng để nói cái này luôn báo trước cái kia
trong khoảng thời gian cố định** — mỗi case phải xem riêng.

### 2.7 Giới hạn

1. **N=13 (DIVERGE) là nhỏ** — đủ để thấy pattern định tính (100% có điều chỉnh, biên độ hơi lớn
   hơn nền), KHÔNG đủ để tính DSR/PBO có ý nghĩa hay chọn threshold "tối ưu" 0,30 (chọn bằng
   must-catch test, không phải grid search).
2. **Base rate quá cao (84% ở −7%) làm mọi ngưỡng "≥7%" gần như vô nghĩa để phân biệt tín hiệu** —
   nếu muốn dùng ngưỡng làm gate trong tương lai, phải so sánh với base rate cùng horizon, không
   báo số tuyệt đối một mình (§2.5).
3. **`sector = FLOOR(ICB_Code/1000)*1000` là gộp thô** (9 nhóm lớn) — chưa thử nhóm mịn hơn hay
   proxy Risk_Rating/size như dispatch gợi ý thay thế; CONC dùng ICB đã đủ để kết luận CONC một
   mình không đặc trưng đỉnh, không cần thử thêm proxy khác cho kết luận này.
4. **KHÔNG đo được NGÀY xảy ra maxDD trong cửa sổ 6 tháng** — chỉ biết có/không và biên độ, chưa
   biết độ trễ từ ngày DIVERGE tới đáy điều chỉnh.
5. **RESEARCH-ONLY.** Không đề xuất wire vào DT5G/CAPIT/gate nào. Không qua quant-skeptic (không
   cần vì không đề xuất production change).

### 2.8 Self-check tối thiểu

- `breadth_drop`/`conc_spread_pct252` đều tính causal (không nhìn tương lai) — kiểm bằng code
  (vòng lặp chỉ dùng `i-252:i`, loại `i`).
- Must-catch 2022-01-06 verify bằng đọc trực tiếp bảng ngày-by-ngày 2021-10→2022-01 (không suy từ
  tổng hợp) — breadth_pct252 giảm từ 0,992 (2021-11-18) → 0,623 (2022-01-06), khớp mô tả finding
  08-31 bằng số liệu độc lập.
- Base rate dùng cùng công thức maxDD với 2 detector (không đổi công thức giữa so sánh).

---

## §3 — Độ trễ từ DIVERGE tới đáy điều chỉnh

> Job `Taylor_20260903_153554` (follow-up thứ 3, đóng giới hạn #4 của §2.7). Đóng câu hỏi vận hành:
> chỉ báo DIVERGE_DAY dùng để **GIẢM TỶ TRỌNG (timing)** hay chỉ để **CẢNH GIÁC (không timing)**?

### 3.0 Định nghĩa t0 và phương pháp

**t0 = ngày DIVERGE đầu tiên của mỗi episode** (Variant A, chính) — vì đây là ngày sớm nhất một
người hành động thực tế nhận được cờ; dùng ngày cuối chuỗi (Variant B) sẽ giấu mất phần "đã bỏ lỡ
bao nhiêu trước khi cờ được XÁC NHẬN". Cả 2 biến thể đều tính (mục 3.6), Variant A là kết luận
chính.

Với mỗi t0: lấy cửa sổ tới đa 126 phiên kể từ t0 (bao gồm t0). Trong cửa sổ:
- **trough** = phiên có `VNINDEX_close` thấp nhất.
- **lag_sessions/lag_calendar_days** = khoảng cách t0→trough.
- **peak_after_signal_pct** = đỉnh cao nhất `VNINDEX_close` đạt được trong đoạn [t0, trough] (chỉ
  tính TRƯỚC hoặc TẠI trough, không tính sau) so với giá tại t0 — đây là phần "còn tăng thêm bao
  nhiêu trước khi đảo chiều".
- **dd_from_t0** = trough/giá t0 − 1 (khác `maxDD trong cửa sổ 6 tháng` ở §2.4 — số đó có thể tính
  từ một đỉnh XẢY RA SAU t0, tức cao hơn giá t0, nên độ lớn tuyệt đối thường lớn hơn dd_from_t0).
- **Episode bị TRUNCATE**: `2026-05-07` (t0 gần cuối panel, panel chỉ còn tới 2026-09-03, chưa đủ
  126 phiên) → LOẠI khỏi N, còn **N=12** cho toàn bộ thống kê phân phối bên dưới (đúng cảnh báo
  dispatch, tránh nó kéo lệch median).
- Base rate: lấy mẫu mỗi 21 phiên trên toàn panel 2008-06→2026-09 (N=203, cùng cách §2.5), loại
  6 mẫu cuối bị truncate cùng lý do → **N=197** dùng cho so sánh.
- Artifact: `crack/analyze_lag.py`, `crack/lag_events_t0_first.csv` (Variant A),
  `crack/lag_events_t0_last.csv` (Variant B), `crack/lag_base_rate.csv`.

### 3.1–3.3 Phân phối 3 đại lượng, N=12 (Variant A) so với nền N=197

| Đại lượng | | min | p25 | median | p75 | max | mean | std |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **lag_sessions** (t0→đáy) | DIVERGE | 0 | 14,25 | **49,5** | 94,25 | 126 | 53,3 | 46,3 |
| | Nền | 0 | 9 | **35,0** | 80 | 126 | 46,1 | 41,6 |
| **lag_calendar_days** | DIVERGE | 0 | 21,25 | **69,5** | 137 | 189 | 78,9 | — |
| | Nền | 0 | 13 | **52,0** | 117 | 189 | 66,9 | — |
| **peak_after_signal_pct** | DIVERGE | 0% | 0% | **2,0%** | 7,4% | 23,3% | 4,8% | 7,0% |
| | Nền | 0% | 0% | **1,6%** | 5,2% | 23,3% | 3,4% | 4,5% |
| **dd_from_t0** | DIVERGE | −34,1% | −13,0% | **−9,1%** | −3,4% | 0% | −10,9% | 10,4% |
| | Nền | −35,7% | −14,1% | **−5,9%** | −2,0% | 0% | −8,9% | 8,4% |

**Đọc kết quả — cả 3 chỉ số đều KHÔNG cho thấy DIVERGE có nội dung TIMING rõ rệt:**
- **Độ trễ tới đáy DÀI HƠN nền, không ngắn hơn** (median 49,5 phiên ≈ 2,3 tháng lịch so với 35
  phiên ≈ 1,7 tháng của nền) — ngược hướng với kỳ vọng "tín hiệu sớm ⇒ đáy tới nhanh". Phân phối
  rất rộng (IQR 14–94 phiên, tức có thể 3 tuần hoặc 4,5 tháng), N=12 nhỏ nên không nói được đây là
  khác biệt có ý nghĩa thống kê, chỉ nói được: **không có bằng chứng độ trễ ngắn/ổn định**.
- **peak_after_signal_pct KHÔNG nhỏ hơn nền** (median 2,0% vs 1,6%; p75 7,4% vs 5,2% — DIVERGE
  còn CAO HƠN nền một chút, chưa nói tới chuyện thấp hơn). 4/12 episode (33%) còn tăng ≥3% sau
  khi cờ bật, và max đạt **+23,3%** (episode 2017-12-28, kéo dài 66 phiên/~3 tháng trước khi tới
  đỉnh thật). Nghĩa là: **giảm tỷ trọng ngay tại t0 có xác suất đáng kể phải hy sinh một đoạn tăng
  còn lại, có ca hy sinh tới +23%**.
- **dd_from_t0 lớn hơn nền một chút** (median −9,1% vs −5,9%, mean −10,9% vs −8,9%, chênh ~2-3pp)
  — cùng hướng và cùng độ lớn khiêm tốn như chênh lệch maxDD ở §2.5 (18,0% vs 14,7%, ~3,3pp).
  Nhất quán nhưng khiêm tốn, không đủ để gọi là edge mạnh.

### 3.4 Điểm riêng 2 case định nghĩa — KHÔNG đại diện cho phân phối, nằm ở đuôi DÀI

| Case | t0 | trough | lag_sessions | lag_calendar_days | peak_after_signal_pct | sessions_to_peak | dd_from_t0 |
|---|---|---|---:|---:|---:|---:|---:|
| 2022-01-06 (đỉnh mọi thời đại) | 2022-01-06 | 2022-07-06 | **121** | 181 | 0,0% | 0 | −24,8% |
| 2018-04 (episode bắt đầu 2018-02-27) | 2018-02-27 | 2018-07-11 | **93** | 134 | 7,6% | 29 | −20,2% |

Xếp hạng trong phân phối N=12 (thứ tự tăng dần của lag_sessions: 0, 3, 9, 16, 17, 48, 51, 57, 93,
98, 121, 126): **2018-02-27 xếp hạng 9/12 (~p75), 2022-01-06 xếp hạng 11/12 (~p92)** — cả hai đều
nằm ở **đuôi dài nhất** của phân phối lag, không phải trường hợp trung vị. Đây là cảnh báo quan
trọng: 2 case dùng để must-catch định nghĩa chỉ báo (§2.3) đều là những ca **đáy tới CHẬM** (4,5–6
tháng), nên nếu chỉ nhìn 2 case này sẽ dễ ngộ nhận "đáy luôn tới muộn, còn thời gian ứng phó" —
thực tế phân phối đầy đủ có cả case đáy tới ngay lập tức (2017-10-09, 2021-04-20: lag=0/3 phiên,
đúng ngày hoặc vài ngày sau signal). Không dự đoán được TRƯỚC episode nào sẽ rơi vào nhóm nào.

### 3.5 Bảng đầy đủ N=13 episode (Variant A, kể cả case bị truncate để tham khảo)

| t0 (DIVERGE đầu tiên) | trough | lag (phiên) | lag (ngày lịch) | peak-after-signal | phiên tới đỉnh | DD từ t0 | Ghi chú |
|---|---|---:|---:|---:|---:|---:|---|
| 2016-09-26 | 2016-12-06 | 51 | 71 | +1,8% | 17 | −3,8% | |
| 2017-10-09 | 2017-10-09 | 0 | 0 | 0% | 0 | 0% | đáy = chính t0 |
| 2017-12-28 | 2018-07-05 | 126 | 189 | **+23,3%** | 66 | −7,9% | max window, còn tăng mạnh trước khi rơi |
| 2018-02-27 | 2018-07-11 | 93 | 134 | +7,6% | 29 | −20,2% | case định nghĩa "2018-04" |
| 2019-10-30 | 2020-03-24 | 98 | 146 | +2,4% | 5 | **−34,1%** | trùng COVID crash, DD lớn nhất mẫu |
| 2021-04-20 | 2021-04-26 | 3 | 6 | 0% | 0 | −4,1% | |
| 2021-05-12 | 2021-07-19 | 48 | 68 | +11,9% | 37 | −2,0% | tăng nhiều nhưng DD cuối nhỏ |
| 2021-06-25 | 2021-07-19 | 16 | 24 | +2,2% | 5 | −10,5% | |
| 2022-01-06 | 2022-07-06 | 121 | 181 | 0% | 0 | −24,8% | case định nghĩa, đỉnh mọi thời đại |
| 2025-05-27 | 2025-06-09 | 9 | 13 | +0,6% | 5 | −2,2% | |
| 2025-10-16 | 2025-11-10 | 17 | 25 | 0% | 0 | −10,5% | |
| 2025-12-23 | 2026-03-23 | 57 | 90 | +7,4% | 13 | −10,2% | |
| 2026-05-07 | 2026-07-22* | 54 | 76 | +1,0% | 7 | −12,6% | **TRUNCATE** (panel hết ở 2026-09-03, chưa đủ 126 phiên) — loại khỏi thống kê §3.1-3.3 |

### 3.6 Biến thể t0 — chỉ thử 1 biến thể có lý do rõ ràng (Variant B, không grid-search)

**Variant B: t0 = ngày DIVERGE CUỐI của mỗi episode** (thời điểm chuỗi đã "xác nhận", tương đương
chờ thêm vài phiên mới hành động):

| Đại lượng | median (A, t0=đầu) | median (B, t0=cuối) | std (A) | std (B) |
|---|---:|---:|---:|---:|
| lag_sessions | 49,5 | 38,5 | 46,3 | 44,5 |
| peak_after_signal_pct | 2,0% | 0% | 7,0% | 6,7% |
| dd_from_t0 | −9,1% | −10,0% | 10,4% | 10,3% |

Lag rút ngắn (dễ hiểu — t0 đã trôi thêm vài phiên trong episode), peak_after_signal giảm nhẹ
(nhiều episode chỉ 1 phiên nên A=B; với episode nhiều phiên, đợi tới cuối chuỗi bỏ lỡ ít upside
hơn). Nhưng **độ phân tán (std) hầu như không đổi** giữa 2 biến thể (46,3 vs 44,5 phiên; 10,4%
vs 10,3% cho DD) — đợi xác nhận chuỗi dài hơn KHÔNG làm độ trễ ổn định hơn có ý nghĩa. Không thử
thêm biến thể "ngày DIVERGE thứ 3" vì kết quả A/B đã đủ trả lời: vấn đề là ĐỘ RỘNG phân phối vốn có
của DD sau đỉnh VNINDEX, không phải do chọn sai điểm neo t0.

### 3.7 Kết luận — trả lời trực tiếp câu hỏi vận hành

**Chỉ báo DIVERGE_DAY là CẢNH GIÁC, KHÔNG PHẢI công cụ TIMING để giảm tỷ trọng đúng lúc.** Ba
bằng chứng độc lập, cùng hướng:
1. Độ trễ tới đáy trung vị (49,5 phiên/~2,3 tháng lịch) **dài hơn**, không ngắn hơn nền không điều
   kiện — nếu là timing signal tốt, đáy phải tới NHANH và ỔN ĐỊNH hơn nền, thực tế ngược lại.
2. 1/3 episode còn tăng đáng kể (≥3%) sau khi cờ bật, có ca tới **+23,3%** trong 66 phiên (~3
   tháng) trước khi đảo chiều — giảm tỷ trọng ngay tại t0 tốn thật, không phải giả thuyết.
3. Biên độ DD-từ-t0 lớn hơn nền chỉ ~2-3pp (median) — cùng độ lớn khiêm tốn như phát hiện §2.5,
   không đủ mạnh để bù cho chi phí cơ hội ở điểm 2.

Giá trị thật của chỉ báo là **nội dung định tính "cấu trúc thị trường đang xấu đi dưới bề mặt"**
(breadth co hẹp trong khi giá vẫn quán tính tăng — đúng cơ chế mô tả ở §2.1/finding 08-31), không
phải một đồng hồ đếm ngược có thể dùng để hẹn giờ giảm tỷ trọng. **Không đề xuất dùng DIVERGE_DAY
làm trigger sizing** — phù hợp hơn với vai trò "nâng cảnh giác, theo dõi sát hơn", để một chỉ báo
khác (hoặc DT5G) xác nhận trước khi hành động bằng tiền thật.

### 3.8 Giới hạn

- N=12 (sau loại truncate) rất nhỏ cho việc đo phân phối — không tính DSR/PBO (không đề xuất
  wire), số liệu chỉ đủ mức "không thấy bằng chứng timing", chưa đủ mức "chứng minh không có
  timing".
- Không kiểm định thống kê hình thức (không có scipy trong môi trường chạy job này) — so sánh chỉ
  bằng phân vị/mean/std, không có p-value. Với N=12 vs N=197 và độ chồng lấn lớn giữa 2 phân phối
  (std đều ~45 phiên trong khi median chỉ chênh ~15 phiên), khả năng cao một kiểm định hình thức
  cũng sẽ không bác bỏ "giống nền" — nhất quán với kết luận §3.7, không phải điểm yếu làm đảo
  ngược kết luận.
- `peak_after_signal_pct`/`dd_from_t0` đo trên đúng 1 cửa sổ 126 phiên kể từ t0 — nếu đáy thật nằm
  ngoài cửa sổ đó (như case 2026-05-07 bị loại), số liệu không phản ánh được; đã loại rõ ràng thay
  vì ước lượng thiếu.
- RESEARCH-ONLY, không qua quant-skeptic (không đề xuất production change).

### 3.9 Self-check

- `lag_metrics()` chỉ đọc `vni[t0_idx : window_end+1]` — không nhìn quá khứ trước t0, không nhìn
  vượt cửa sổ 126 phiên (causal cho outcome, đúng vai trò "forward window chỉ đo OUTCOME").
- Truncation phát hiện bằng so sánh `t0_idx+FWD` với `n-1` (số phiên thật còn lại trong panel),
  không suy đoán — loại đúng 1/13 episode (2026-05-07) và đúng 6/203 mẫu nền, khớp với ngày cuối
  panel `2026-09-03`.
- Đối chiếu chéo: episode 2022-01-06 và 2018-02-27 (case định nghĩa §2.3) tái xuất hiện đúng vị
  trí trong bảng 3.5 với ngày/giá khớp §2.3/§2.4 (2022-01-06 dd_from_t0 −24,8% ăn khớp hướng với
  maxDD-6M −24,79% đã có ở `events_diverge_day.csv` cột `maxdd_6m` — hai cách đo khác nhau [DD từ
  t0 vs maxDD nội cửa sổ] cho cùng episode ra số gần nhau vì đỉnh nội cửa sổ chính là t0 ở case
  này, peak_after_signal=0%).

---

## Artifact

- Phần 1: không có artifact BQ mới (kết luận từ query coverage `bq` inline + `data/VNINDEX.csv`
  local, không lưu file riêng — số liệu đã trích trực tiếp trong §1).
- Phần 2: `mania_20260903/crack/q_sector_dispersion.sql`, `sector_dispersion.csv`,
  `analyze_crack.py`, `crack_daily.csv`, `events_diverge_day.csv`, `events_conc_day.csv`,
  `events_crack_day.csv`.
- §3: `mania_20260903/crack/analyze_lag.py`, `lag_events_t0_first.csv` (Variant A, chính),
  `lag_events_t0_last.csv` (Variant B), `lag_base_rate.csv` (nền N=203).
- Bus: `mania-2006-2007-not-same-species-20260903` (Phần 1), `cracking-mania-diverge-detector-20260903` (Phần 2), `diverge-day-lag-to-trough-20260903` (§3).
