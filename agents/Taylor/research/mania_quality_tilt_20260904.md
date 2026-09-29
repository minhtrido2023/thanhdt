# Mania → chọn mã / nghiêng tỷ trọng chất lượng (thay vì bật/tắt thị trường)

> Job `Taylor_20260903_171818` (follow-up thứ 6, ĐỔI NHÁNH). **RESEARCH-ONLY, không wire.** Đọc
> trước: `market_mania_euphoria_detector_20260903.md` (định nghĩa episode N=7/N=14, breadth+spread),
> `mania_deep_dive_2006_2007_and_cracking_20260903.md` (DIVERGE_DAY), `mania_exit_reentry_roundtrip_20260903.md`
> (kết luận: market-timing bằng tín hiệu đỉnh KHÔNG có edge round-trip).

## Tóm tắt 1 dòng

Sau 5 vòng đóng nhánh "bật/tắt thị trường theo tín hiệu đỉnh", nhánh "nghiêng tỷ trọng chất lượng"
cho kết quả **tương tự: không có bằng chứng đủ mạnh để hành động**. Junk premium trong mania **có
đảo ngược nhẹ nhưng không nhất quán** (Q1). Rổ chất lượng (golden-floor + ey top-decile) **có một
biên độ vượt trội khi mania đang diễn ra, nhưng KHÔNG có thêm bảo vệ trong 6 tháng sau** — biên độ
sau episode còn THẤP HƠN biên độ nền thông thường của chính nó (Q2). Nghiêng THÊM tỷ trọng khi phát
hiện mania cho cải thiện CAGR gần như bằng 0 so với không làm gì (Q3). **Kết luận đóng chuỗi**: bản
thân việc GIỮ tilt giá-trị/chất-lượng tĩnh (đúng tinh thần gate 8L production) đã mang lại ~+3pp/năm
so với VNINDEX một cách ổn định — đó là edge thật, nhưng nó **không liên quan gì đến việc phát hiện
mania**; cố thêm một lớp phản ứng động theo tín hiệu mania không cải thiện được gì đáng kể.

---

## ⚠️ Kỷ luật chống vòng tròn (đọc trước khi đọc số liệu)

Chân 2 của MANIA detector định nghĩa bằng **Risk_Rating** basket (junk Risk_Rating≥5 thắng quality
Risk_Rating≤2). Mọi phép đo trong file này dùng **rổ khác hẳn**: PE (định giá) + ROE_Min3Y/CF_OA
(chất lượng cơ bản), equal-weight, so với **VNINDEX cap-weighted** — không đụng tới Risk_Rating hay
breadth ở bất kỳ bước chọn mã nào. Q1 vẫn dùng basket Risk_Rating (vì đó chính là câu hỏi "junk
premium đảo ngược" — không tránh được, nhưng đo ở giai đoạn SAU episode, không phải TRONG episode
— tránh đo lại định nghĩa).

---

## §1. Định nghĩa lại tập episode (tái dùng nguyên văn từ job trước)

- **N7 (ngưỡng chính, p90/p75)**: `mania_20260903/mania_episodes.csv`, 2009→2025.
- **N14 (ngưỡng nới, p85/p60)**: `qualitytilt/episodes_n14.csv` — regenerate lại từ
  `qualitytilt/episodes_n14.py` (dùng đúng logic gốc `analyze_mania.py`, chỉ đổi threshold), khớp
  N=14 đã báo cáo ở job gốc. Panel: `qualitytilt/mania_daily_full.csv` (2008-06-02→2026-09-03,
  4.558 phiên, `n_total≥30`).

---

## §2. Q1 — Junk premium có ĐẢO NGƯỢC sau episode không?

### 2.1 Thiết kế

Dùng `ret_lowrisk`/`ret_highrisk` **đã có sẵn** trong `mania_daily.csv` (basket Risk_Rating≤2 vs
≥5, `universe_pit`, tái dùng nguyên văn, không tính lại). Đo spread **quality trừ junk**
(`qmj = logret_low - logret_high`, dấu ngược `spread21` gốc) cộng dồn trong 1/3/6/12 tháng
(21/63/126/252 phiên) **SAU** ngày kết thúc episode.

**Base rate bắt buộc**: cùng phép đo (tổng `qmj` trên cửa sổ độ dài h) lấy tại MỌI điểm bắt đầu
trong panel (không điều kiện mania), step=5 phiên → phân phối nền. So sánh trung bình episode với
trung bình nền, KHÔNG chỉ nhìn dấu tuyệt đối.

### 2.2 Kết quả

| Ngưỡng | Horizon | n_ep | Mean episode | Mean nền (base) | **Excess so nền** | %episode dương |
|---|---|---:|---:|---:|---:|---:|
| N7 | +1M | 7 | +1,78% | +0,62% | **+1,15pp** | 71% |
| N7 | +3M | 7 | +5,54% | +2,12% | **+3,42pp** | 71% |
| N7 | +6M | 7 | +9,17% | +4,73% | **+4,44pp** | 57% |
| N7 | +12M | 6 | +4,45% | +9,41% | **−4,96pp** | 50% |
| N14 | +1M | 14 | +2,36% | +0,62% | **+1,73pp** | 64% |
| N14 | +3M | 14 | +7,13% | +2,12% | **+5,01pp** | 86% |
| N14 | +6M | 14 | +7,81% | +4,73% | **+3,08pp** | 71% |
| N14 | +12M | 13 | +12,62% | +9,41% | **+3,20pp** | 69% |

Artifact: `qualitytilt/q1_spread_reversal.py`.

### 2.3 Đọc kết quả

**Quan sát nền quan trọng nhất, phải nói trước**: spread quality−junk **DƯƠNG ngay cả KHÔNG điều
kiện gì** (base_mean +0,62%→+9,41% theo horizon dài dần) — đây là "low-risk anomaly" quen thuộc:
basket rủi ro thấp có xu hướng thắng basket rủi ro cao theo thời gian bất kể có mania hay không.
Vì vậy câu hỏi thật không phải "spread có dương sau mania không" (gần như luôn dương do nền đã
dương) mà là "**excess** so với nền có dương và NHẤT QUÁN không".

**Excess dương ở 6/8 hàng, nhưng KHÔNG nhất quán**: N7+12M excess **ÂM** (−4,96pp, và %dương chỉ
50%) — episode 2020 (fwd12m thấp hơn hẳn nền vì 2021 tiếp tục là năm junk/penny thắng thế mạnh) kéo
số liệu N7 xuống. N14+12M lại dương (+3,20pp) vì có thêm episode khác cân bằng lại. **Đây chính là
dấu hiệu N nhỏ (6-14) không đủ ổn định để tin một chiều duy nhất** — không phải bằng chứng phủ định
hoàn toàn, mà là bằng chứng KHÔNG ĐỦ MẠNH để dùng làm rule.

**Caveat thống kê bắt buộc**: cửa sổ nền dùng overlapping windows (step=5 phiên, cửa sổ dài tới 252
phiên) → tự tương quan cao, N hiệu dụng của phân phối nền nhỏ hơn nhiều so với n hiển thị (887-908).
Không tính p-value hình thức, không claim "significant".

**Trả lời Q1**: **junk premium có xu hướng đảo ngược một phần sau mania (excess dương ở đa số
horizon/ngưỡng), nhưng biên độ khiêm tốn (1-5pp) và KHÔNG nhất quán ở horizon dài nhất (12 tháng,
đảo dấu giữa N7/N14)** — không đủ để dùng làm rule quay lại junk/quality có hệ thống.

---

## §3. Q2 — Rổ chất lượng thật (PE+golden-floor) tự bảo vệ xuyên mania thế nào?

### 3.1 Xây rổ — 2 biến thể, cả hai PIT

Dùng cột `PE` trong `tav2_bq.ticker` (đã verify PIT-correct, cơ sở `Price` thô — không phải `Close`
— theo `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md`), JOIN `universe_pit`
(`in_universe=TRUE`), quarterly rebalance (75 quý, rebalance = phiên đầu tiên mỗi quý xuất hiện
trong panel), equal-weight, buy-and-hold trong quý (không rebalance nội-quý — quy ước chuẩn).

- **Biến thể A — "ey_top_decile (naive)"**: chỉ lọc `PE>0`, chọn decile PE thấp nhất (ey cao nhất).
- **Biến thể B — "golden_floor+ey"**: thêm sàn chất lượng production
  (`ROE_Min3Y≥0` ∧ TTM CFO = `CF_OA_P0+P1+P2+P3 > 0`, đọc trực tiếp từ `ticker` daily — cùng cadence
  PIT với PE, không tự join `Release_Date`) TRƯỚC khi lấy decile PE thấp nhất trong phần đạt sàn.

**Phát hiện phụ quan trọng (không phải câu hỏi chính nhưng phải báo)**: 2 biến thể cho kết quả
KHÁC NHAU RẤT XA khi backtest KHÔNG điều kiện mania, toàn giai đoạn 2008-06→2026-09 (18,7 năm,
`qualitytilt/build_quality_basket2.py` + `build_gf_nav.py`, self-check tổng tỷ trọng=100% mỗi
rebalance, sai số max 5,3e-15):

| Basket | CAGR | Total return | So VNINDEX cùng cửa sổ (CAGR 8,36%, total +348%) |
|---|---:|---:|---|
| ey_top_decile (naive) | **+2,58%** | +60,8% | **kém xa** — value-trap |
| golden_floor+ey | **+11,47%** | +759,4% | **vượt** +3,1pp/năm |

⚠️ **PE thấp KHÔNG lọc kèm floor chất lượng là một cái bẫy value-trap thật, đo được bằng dữ liệu** —
khớp đúng ghi chú đã có trong memory (`custom30V selector roadmap`: "ey-only is pragmatic-for-now,
not final"). Từ đây chỉ dùng **golden_floor+ey** cho phần trả lời Q2/Q3 (basket "naive" bị loại vì
không phải một proxy chất lượng hợp lý — tự nó đã thua thị trường không điều kiện).

### 3.2 Đo qua 3 giai đoạn episode + base rate

`excess = return(basket) − return(VNINDEX)` trong (a) trong episode, (b) 6 tháng sau episode,
(c) round-trip (đầu episode → +6 tháng). **Base rate**: excess trung bình của CHÍNH basket này so
VNINDEX trên cửa sổ NGẪU NHIÊN cùng độ dài (median độ dài episode thật), lấy 3.000 điểm bắt đầu
ngẫu nhiên toàn panel — vì basket này đã có excess dương KHÔNG điều kiện (+3,1pp/năm), phải trừ nền
đó ra mới biết mania có thêm gì không.

| Ngưỡng | Giai đoạn | n | Ep mean | Base mean (nền, basket này) | **Excess so nền** | %dương |
|---|---|---:|---:|---:|---:|---:|
| N7 | Trong episode | 7 | +4,23% | +0,42% | **+3,81pp** | 57% |
| N7 | +6 tháng sau | 7 | −1,33% | +2,18% | **−3,51pp** | 43% |
| N7 | Round-trip | 7 | +3,12% | +2,60% | **+0,51pp** | 71% |
| N14 | Trong episode | 14 | +4,69% | +0,28% | **+4,41pp** | 71% |
| N14 | +6 tháng sau | 14 | +0,71% | +2,18% | **−1,46pp** | 50% |
| N14 | Round-trip | 14 | +5,61% | +2,94% | **+2,67pp** | 71% |

Artifact: `qualitytilt/q2_full_analysis.py`, `q2_phases_N7.csv`, `q2_phases_N14.csv`.

### 3.3 Đọc kết quả

**(a) TRONG episode: rổ chất lượng vượt trội hơn cả biên độ nền của chính nó** (+3,8 đến +4,4pp
vượt base, nhất quán ở cả 2 ngưỡng, %dương 57-71%). Đây có ý nghĩa: khi mania diễn ra (breadth rất
rộng, VNINDEX cap-weighted có thể bị kéo bởi vài mã vốn hoá lớn trong khi rally lan rộng đa số mã
nhỏ/vừa), rổ equal-weight chất lượng ĐƯỢC HƯỞNG LỢI từ chính breadth rộng đó — không mâu thuẫn với
chân 2 detector (Risk_Rating), vì đây là so sánh khác hẳn (PE+quality equal-weight vs VNINDEX
cap-weighted, không phải quality vs junk).

**(b) 6 THÁNG SAU episode: KHÔNG có thêm bảo vệ — ngược lại, excess THẤP HƠN nền ở cả 2 ngưỡng**
(−3,51pp và −1,46pp). Đây là câu trả lời trực tiếp và **là phát hiện quan trọng nhất của Q2**: rổ
chất lượng KHÔNG "tự động phòng thủ tốt hơn bình thường" trong giai đoạn ngay sau một đỉnh mania —
nó vẫn tham gia đầy đủ vào đợt điều chỉnh sau đó (khớp §4 job trước: maxDD 6 tháng sau episode
trung bình −14,3%, không phân biệt theo chất lượng cổ phiếu).

**(c) Round-trip (đầu episode → +6 tháng)**: kết quả trộn lẫn — N7 gần như PHẲNG so với nền
(+0,51pp, trong biên độ nhiễu N=7), N14 dương vừa phải (+2,67pp). Không đủ nhất quán để khẳng định
"xuyên mania tốt hơn nền".

**Trả lời Q2**: **rổ chất lượng KHÔNG tự bảo vệ xuyên mania theo nghĩa "không cần làm gì thêm".**
Nó có một khoảng vượt trội THẬT trong lúc mania diễn ra (tham gia rally tốt hơn thường lệ), nhưng
**mất hết lợi thế đó — thậm chí kém hơn biên độ nền — trong 6 tháng sau khi mania kết thúc**. Cái
"tự bảo vệ" duy nhất có bằng chứng là **edge KHÔNG-điều-kiện dài hạn** (+3,1pp/năm so VNINDEX suốt
18,7 năm, không liên quan gì tới có mania hay không) — chính là những gì gate 8L production đã làm.

---

## §4. Q3 — Có nên nghiêng THÊM khi thấy mania không?

### 4.1 Thiết kế (N_TRIALS=2, khai trước)

Portfolio blend hàng ngày: `w_quality(t)` (rổ golden_floor+ey) vs `1-w_quality(t)` (VNINDEX).
Baseline **50/50 không đổi**. MAIN: `w_quality = 50% + tilt_add` khi `MANIA_DAY[t-1]` bật (đúng
ngưỡng chính p90/p75, dùng flag NGÀY, không phải episode đã lọc gap/min-length — sát nghĩa
"khi thấy mania" nhất). 2 mức tilt thử: **+25pp và +50pp** (không grid-search thêm). Phí đổi trạng
thái 0,1% mỗi lần weight đổi (CLAUDE.md §Backtest). Panel: 2008-06→2026-09, 4.558 phiên.

**Control (CTRL, giống CTRL2 job trước)**: đặt tilt vào các RUN NGẪU NHIÊN cùng **phân phối độ dài**
với 56 run MANIA_DAY thật (median 3 phiên, không phải scatter từng ngày rời rạc — kiểm tra sơ bộ
cho thấy scatter rời rạc làm phí giao dịch áp đảo so sánh, đã sửa để công bằng), bootstrap n=200.

### 4.2 Kết quả

| | CAGR | Sharpe | maxDD | So baseline (không tilt) |
|---|---:|---:|---:|---|
| Baseline 50/50 (không tilt) | 10,94% | 0,644 | −52,3% | — |
| MAIN tilt +25pp trên MANIA_DAY | 10,90% | 0,639 | −52,2% | **−0,04pp** |
| MAIN tilt +50pp trên MANIA_DAY | 11,52% | 0,662 | −51,7% | **+0,58pp** |
| CTRL +25pp (n=200, cùng cấu trúc run) | 10,30% (±0,33pp) | 0,613 | — | MAIN vượt 95% draw |
| CTRL +50pp (n=200, cùng cấu trúc run) | 10,39% (±0,75pp) | 0,614 | — | MAIN vượt 94% draw |

Artifact: `qualitytilt/q3_tilt_more_v2.py` (v1 dùng control scatter-ngày lỗi vì phí giao dịch áp
đảo — đã tự phát hiện và sửa, giữ lại `q3_tilt_more.py` làm bằng chứng quy trình).

### 4.3 Đọc kết quả

**MAIN thắng CTRL rõ** (percentile 94-95%) — nghĩa là biết ĐÚNG NGÀY để tilt (theo MANIA_DAY thật)
tốt hơn tilt vào ngày ngẫu nhiên cùng cấu trúc. Nhưng **so với đơn giản KHÔNG LÀM GÌ (baseline
50/50 cố định), cải thiện tuyệt đối gần như bằng KHÔNG**: tilt+25pp còn tệ hơn một chút (−0,04pp),
tilt+50pp chỉ hơn +0,58pp CAGR sau 18,7 năm — nằm trong biên độ mà một N=2-mức-thử trên N=7-14
episode không thể phân biệt được với nhiễu.

**Trả lời Q3**: **KHÔNG nên nghiêng thêm.** "Thắng control ngẫu nhiên" không đồng nghĩa "đáng làm"
— biên độ tuyệt đối quá nhỏ để bù lại rủi ro overfit (chọn đúng 2 mức tilt sau khi đã biết kết quả
Q1/Q2 mixed) và độ phức tạp vận hành thêm.

---

## §5. Kết luận đóng chuỗi

**Trả lời trực tiếp 3 câu hỏi:**
1. **Junk premium có đảo ngược không?** Có xu hướng nhẹ, KHÔNG nhất quán (đảo dấu ở horizon 12
   tháng giữa N7/N14) — không dùng làm rule.
2. **Rổ chất lượng có tự bảo vệ xuyên mania không?** KHÔNG theo nghĩa "thêm bảo vệ khi có mania" —
   nó CÓ một biên độ vượt trội trong lúc mania diễn ra nhưng MẤT biên độ đó (xuống dưới cả mức nền)
   trong 6 tháng sau. Cái duy nhất thật là edge **không điều kiện** dài hạn (~+3pp/năm), không liên
   quan tới phát hiện mania.
3. **Có nên nghiêng thêm khi thấy mania không?** KHÔNG — cải thiện tuyệt đối ~0 đến +0,6pp CAGR,
   không đáng đánh đổi rủi ro overfit/vận hành.

**Cả 3 câu đều "không có gì hành động được theo hướng phản ứng-động-với-mania".** Nhưng khác với 5
vòng trước (toàn bộ đều KHÔNG tìm thấy gì), vòng này tìm thấy một sự thật có giá trị thật:
**golden-floor + value tilt tĩnh (đúng tinh thần gate 8L production) đã mang lại ~+3,1pp/năm so
VNINDEX suốt 18,7 năm một cách ổn định, không cần biết trước có mania hay không** — và một phản
chứng đáng nhớ: **ey-thấp KHÔNG kèm sàn chất lượng là value-trap thật (CAGR 2,6% vs 11,5% khi có
golden-floor)**, khớp đúng lo ngại đã ghi trong `custom30V selector roadmap` memory.

**Khuyến nghị đóng chuỗi nghiên cứu mania (N=6 job, 2026-09-03→04)**: không có tín hiệu bắt-đỉnh
hay phản ứng-động nào (breadth/RSI/junk-premium/quality-tilt) vượt qua được kiểm định
random-control có ý nghĩa kinh tế. Giá trị thật của toàn bộ chuỗi là 2 mảnh: (a) xác nhận LẠI rằng
gate/tilt production hiện có (8L rating, golden-floor) đã đúng hướng và KHÔNG cần thêm lớp phản ứng
theo mania; (b) cảnh báo cụ thể, có số liệu, về bẫy value-trap của ey-only screen — hữu ích trực
tiếp cho custom30V roadmap dù không liên quan gì tới mania nữa.

---

## §6. Giới hạn

1. **N nhỏ ở mọi phép đo** (6-14 episode) — không tính DSR/PBO (không đề xuất wire). Mọi kết luận
   "không nhất quán" cần đọc với tinh thần N nhỏ, không phải "đã chứng minh không có edge".
2. **Golden-floor dùng TTM CFO (`CF_OA_P0..P3` từ bảng `ticker` daily), không phải `CF_OA_3Y` từ
   `ticker_financial`** — tránh phải tự join `Release_Date` (đúng dặn dò dispatch), nhưng là một
   xấp xỉ nhẹ hơn golden-floor gốc trong `rating_8l.py` (thiếu điều kiện 3-năm). Không ảnh hưởng
   hướng kết luận (basket vẫn CAGR 11,47% vs 8,36% VNINDEX — biên đủ lớn để chịu được sai số nhỏ
   từ xấp xỉ này).
3. **Q3 dùng blend liên tục (không phải units thực), phí 0,1% mỗi lần đổi weight** — mô hình hoá
   đơn giản hơn engine round-trip đầy đủ của job trước, nhưng đủ cho câu hỏi "có đáng tilt không".
4. **Basket ey_top_decile "naive" bị loại khỏi Q2/Q3 sau khi phát hiện value-trap** — không phải
   silent-drop, đã báo rõ ở §3.1 kèm số liệu (CAGR 2,58% vs 11,47%).
5. **RESEARCH-ONLY**, không qua quant-skeptic (không đề xuất production change).

---

## Self-check đã chạy

- Weight-sum tại mỗi rebalance = 100% (assertion, không phải quan sát): sai số max **5,33e-15**
  (`build_gf_nav.py`), **1,67e-16** ban đầu (`build_quality_basket.py` bản lỗi) — cả hai xác nhận
  engine equal-weight đúng.
- **Bug tự phát hiện + tự sửa, ghi lại minh bạch**: bản đầu `build_quality_basket.py` join
  `universe_pit` trực tiếp cho CẢ giá cổ phiếu → NAV sập còn 0,89% (mã rời universe_pit tạm thời/
  vĩnh viễn làm mất giá trị nắm giữ). Sửa bằng cách tách: `universe_pit` CHỈ dùng để CHỌN mã tại
  ngày rebalance; giá nắm giữ hàng ngày lấy từ `tav2_bq.ticker` KHÔNG lọc universe (448+318 mã
  từng được chọn, pull riêng). `build_quality_basket2.py`/`build_gf_nav.py` là bản đã sửa.
- Q3 v1→v2: phát hiện control "tilt ngày ngẫu nhiên rời rạc" bị phí giao dịch (738 lần đổi vs 112
  lần thật) áp đảo, làm méo so sánh — tự sửa sang control cùng cấu trúc run (§4.3), giữ cả 2 file
  làm bằng chứng quy trình.
- PIT: `PE`/`ROE_Min3Y`/`CF_OA_P0..3` đều đọc từ `tav2_bq.ticker` (đã verify PIT cơ sở `Price` thô
  theo data_registry) tại ĐÚNG ngày rebalance, không dùng cột `profit_*`.

## Artifact

`qualitytilt/` — `episodes_n14.py/.csv`, `mania_daily_full.csv`, `q1_spread_reversal.py`,
`universe_pe.csv` (BQ pull, 1,44M dòng), `build_quality_basket.py/2.py`, `full_close.csv` (BQ pull,
448 mã, 1,66M dòng), `quality_basket_nav.csv`, `golden_floor_snap.csv` (BQ pull), `build_gf_basket.py`,
`build_gf_nav.py`, `gf_basket_nav.csv`, `q2_full_analysis.py`, `q2_phases_N7/N14.csv`,
`q3_tilt_more_v2.py`.
Bus: `mania-quality-tilt-verdict-20260904`.
