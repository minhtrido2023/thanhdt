# W1 — Proxy lãi tiền nhàn rỗi cho backtest (thay giả định 0%)
Job `Taylor_20260927_101337` · 2026-09-27 · **PAPER-ONLY. Không wire, không đổi config/rail, không đặt lệnh.**
Phạm vi = §2 + W1 của `mike/kb/projects/custom30v-revalidation-plan-20260927.md` (user duyệt §7 lúc 17:11 ICT).
Artifact: `/home/trido/thanhdt/WorkingClaude/idle_rate_proxy.py` + `idle_rate_proxy_selfcheck.py`,
`carry_paired_tiered.py` + `carry_paired_tiered_results.json`, registry `.proposed`.

## KẾT LUẬN MỘT DÒNG
Hai chuỗi FiinPro **ĐẠT** cổng đối chiếu (3 mốc/chuỗi, lệch **0,00pp**), haircut đo được là
**2,04pp** chứ không phải 1,0pp quy ước — và với proxy tầng 1 (trung bình **4,16%/năm**, **không
tháng nào** vượt break-even 7,00%) thì **luận điểm "park 0,30 thắng 0,80 trên CẢ CAGR" của Job U
là hiệu ứng TẦNG 3 (khuyến mãi DNSE 8,543%), không phải hiệu ứng lịch sử**. Trên tầng 1/2, park
0,80 **CAGR cao hơn** 0,61–0,71pp. Quyết định 0,80→0,30 **vẫn đứng**, nhưng đứng **chỉ trên cổng
DD** (0,80 FAIL cổng ở cả 4 tầng) và trên `P(Calmar 0,30>0,80) = 0,86–0,91`, **không** trên CAGR.
Q3 chưa kết luận (đúng phạm vi dispatch) — số đã đủ để W2/W3 dùng.

---

## 1. ĐỐI CHIẾU CHÉO — ĐẠT, nhưng chỉ phủ 2025-11 → 2026-09

Cổng dispatch: ≥3 mốc/chuỗi, lệch >0,2pp ở bất kỳ mốc ⇒ hạ UNVERIFIED và dừng.

### 1a. `fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv` — 3/3 mốc khớp TUYỆT ĐỐI

| Mốc | Snapshot (thấp/cao) | Nguồn độc lập | Lệch |
|---|---|---|---|
| 2025-11 | **4,9 / 6,2** | báo cáo NHNN tháng 11/2025 dẫn lại (diendandoanhnghiep): "trên 12 tháng đến 24 tháng **4,9-6,2%/năm**" | **0,00 / 0,00pp** |
| 2026-01 | **5,1 / 6,5** | NHNN tháng 01/2026 dẫn lại (thuvienphapluat): ">12→24 tháng tăng đều 0,1pp hai đầu, lên **5,1–6,5%/năm**" | **0,00 / 0,00pp** |
| 2026-06 | **5,9 / 7,3** | bảng NHNN tháng 6/2026 (nhipsongkinhdoanh, in nguyên bảng): "Trên 12 tháng đến 24 tháng **5,9-7,3%/năm**" | **0,00 / 0,00pp** |

**⚠️ ĐÍNH CHÍNH ĐỊNH NGHĨA (quan trọng hơn cả con số).** Nhãn FiinPro "Lãi suất huy động **bình
quân** trên 12 tháng (cao nhất/thấp nhất)" **SAI hai lần**:
1. Không phải "bình quân" — là **HAI ĐẦU MÚT của khoảng lãi suất phổ biến** NHNN công bố.
2. "Trên 12 tháng" thực chất là dòng **"Trên 12 tháng đến 24 tháng"**, **KHÔNG** gồm dòng "Trên
   24 tháng" (tháng 6/2026: 7,1-7,8%; tháng 11/2025: 6,7-7,4%). Ai đọc nhãn mà tưởng đã gồm
   kỳ hạn dài nhất sẽ dùng số THẤP hơn thực tế.

Đây là một dấu hiệu TỐT cho mục đích của ta: đầu mút "thấp nhất" ≈ nhóm NHTM Nhà nước, tức mức
bảo thủ — đúng thứ cần cho baseline.

### 1b. `fiinprox_interbank_avg_rate_monthly_2014_2026.csv` — 3/3 mốc khớp, 9 quan sát tenor

| Mốc | Snapshot | Nguồn độc lập | Lệch |
|---|---|---|---|
| 2026-09 (period `2026-09-25`) — **cả 7 tenor** | O/N 1,10 · 1W 5,06 · 2W 5,35 · 1M 6,25 · 3M 7,20 · 6M 7,55 · 9M 8,00 | bảng chính thức SBV `dttktt.sbv.gov.vn/.../lsttlnh`, phiên **24/09/2026**: trùng khớp **7/7** | **0,00pp × 7** |
| 2026-08 (period `2026-08-31`) O/N **1,19** | 1,19 | diendandoanhnghiep 31/08/2026 "NHNN bơm ròng cuối tháng, lãi suất liên ngân hàng về **1,19%**" | **0,00pp** |
| 2026-08 phiên 27/08 (kiểm hướng, không phải mốc snapshot) | — | znews/thoibaonganhang: O/N 1,20 ngày 27/08, giảm về 1,19 cuối tuần ⇒ nhất quán chiều | — |

**⚠️ PHÁT HIỆN CẤU TRÚC — chuỗi này KHÔNG phải bình quân tháng.** Nó là **bản in của MỘT phiên
cuối tháng** (bằng chứng: 2026-09 khớp 7/7 tenor với bảng SBV ngày 24/09, và nhãn `period` là
ngày cuối tháng chứ không phải `YYYY-MM`). Lãi suất O/N VN dao động **0%–16,39%** trong 2026
(Trading Economics: đỉnh mọi thời 16,39% ngày 03/02/2026; báo chí 2026: "tăng vọt lên 13%",
"rơi về gần 0%"). Vì vậy:
- Một phiên **không** đại diện cho tháng ⇒ tầng 2 (`floor`) là **MỘT KỊCH BẢN**, không phải ước
  lượng trung tâm. Đã ghi vào docstring module (Bẫy #1).
- Các tenor dài **mỏng thanh khoản**: doanh số trung vị 9M = **830 tỷ**, 6M = 4.863 tỷ, so với
  O/N 896.204 tỷ và 1W 220.126 tỷ. Giá 9M/6M là single-print, không dùng cho quyết định.

### 1c. Điều CHƯA làm được — nói thẳng
**Cả 3 mốc mỗi chuỗi đều nằm trong 2025-11 → 2026-09.** Tìm nguồn độc lập cho 2014-2024 không ra:
báo cáo tháng NHNN thời kỳ đó không còn index công khai, các URL `sbv.gov.vn/ShowProperty` trả 404,
CEIC/TradingEconomics/FXEmpire trả 403/404 cho truy cập không đăng nhập. Nghĩa là **đoạn lịch sử
2011-01 → 2025-10 — chính đoạn backtest dùng — chưa có nguồn thứ hai xác minh**. Bằng chứng gián
tiếp duy nhất: định nghĩa chuỗi đã được pin chính xác ở 3 mốc gần và hình dạng chuỗi khớp các mốc
định tính đã biết (đỉnh siết 2022-11→2023-06, sàn COVID 2020-12 O/N 0,42%). Đề xuất registry vì
vậy **giới hạn phạm vi xác minh**, không tuyên bố toàn chuỗi.

---

## 2. HAIRCUT TẦNG 1 — đo được **2,04pp**, không phải 1,0pp

Đo khoảng cách (SBV thấp nhất >12–24M − lãi BQ liên NH kỳ hạn) trên **143 tháng 2014-01 → 2026-08**
(`idle_rate_proxy_selfcheck.py --haircut`):

| tenor liên NH | median | p25 | p75 | mean | sd | % tháng ÂM |
|---|---|---|---|---|---|---|
| qua đêm | +4,060 | +1,885 | +5,340 | +3,549 | 2,300 | 4,2% |
| 1 tháng | +2,640 | +1,145 | +4,060 | +2,421 | 2,060 | 13,3% |
| **3 tháng (dispatch chỉ định)** | **+2,040** | **+0,360** | **+3,150** | +1,587 | 1,923 | 21,0% |
| 6 tháng | +1,500 | +0,130 | +2,130 | +0,983 | 1,717 | 24,5% |

**Chốt `HAIRCUT_PP = 2,04`** (median, tenor 3 tháng). Ba lý do, theo đúng thứ tự quan trọng:
1. **Dispatch W1 mục 2 chỉ định** median của khoảng cách "12M thấp nhất − liên NH 3M" thay con số
   quy ước — đây là số đó, không phải số tôi chọn.
2. **Median chứ không mean**: chuỗi liên NH là một phiên duy nhất mỗi tháng (mục 1b) nên đuôi rất
   dày — mean 1,587 bị kéo bởi 21% tháng âm (những tháng liên NH 3M vọt trên lãi tiền gửi, vd
   2022-11: liên NH 3M 9,65% vs SBV thấp 5,7%). Trung vị bền với đúng loại nhiễu này.
3. **Con số quy ước 1,0pp trong bản kế hoạch quá NHỎ** — nó làm baseline cao hơn thực tế ~1pp,
   tức nghiêng kết luận về phía "tiền có lợi", đúng chiều thiên lệch mà W1 phải khử.

Hệ quả: baseline 2014-01→2026-08 có **mean 4,133% / median 4,360% / min 2,760% / max 5,460%**.

---

## 3. `idle_rate_proxy.py` — 3 tầng, PIT thật, KHÔNG wire vào engine

`r_idle(date, tier)` → %/năm, `tier ∈ {baseline, floor, spot}`; `r_idle_series(dates, tier)`.

| tier | công thức | ghi chú |
|---|---|---|
| `baseline` | SBV thấp nhất(>12–24M) − 2,04pp, clip ≥0 | dùng cho MỌI số pin/so sánh |
| `floor` | max(0, liên NH **1 tháng**) | kịch bản stress; **không** phải chặn dưới theo thứ tự (xem dưới) |
| `spot` | 8,543% hằng, **raise** nếu date ∉ [2026-08-18, 2027-03-31] | biên dưới = ngày `egg.totalValue` khác 0; biên trên = giới hạn "cửa sổ nhìn trước ≤6 tháng" của §2.2 |

**PIT thật:** mốc tháng T chỉ dùng từ ngày đầu tháng T+1, forward-fill mốc TRƯỚC gần nhất, raise
(không trả 0 im lặng) nếu ngày nằm trước mốc đầu tiên. Quy ước T+1 này là **CHẶN TRÊN của độ tươi
thật** — NHNN công bố "Diễn biến lãi suất tháng T" trong tháng T+1, thường giữa tháng, nên thực tế
còn trễ hơn ⇒ proxy hơi ƯU ÁI, không ngược thời gian.

**⚠️ `floor` KHÔNG luôn ≤ `baseline`** (2022-11: floor 8,65 vs baseline 3,66; 2025-12: 7,53 vs 2,96;
2026-06: 8,20 vs 3,86). Nó là kịch bản khác, không phải chặn dưới theo thứ tự. Module **cố ý không**
tự lấy `min()` — muốn chặn dưới thực sự thì làm ở phía gọi, tường minh. Đã ghi Bẫy #3 trong docstring.

**Selfcheck `idle_rate_proxy_selfcheck.py`: 50 assertion PASS, mutation 7/7 BỊ GIẾT.**

| mutation | bị bắt bởi |
|---|---|
| M1 bỏ lag PIT (dùng chính tháng của ngày) | T3 "31/08 dùng mốc 2026-07" |
| M2 forward-fill → lấy mốc TƯƠNG LAI gần nhất | T4 (raise) |
| M3 bỏ cổng ngày của tier `spot` | T5 "spot PHẢI raise cho 2014-08-01" |
| M4 đảo dấu haircut (cộng thay vì trừ) | T2 |
| M5 bỏ lọc dòng "Doanh số" (VND lọt vào cột %) | T1 biên [0,30]% |
| M6 `floor` đổi sang tenor qua đêm | T2 |
| M7 haircut dùng mean thay median | T8 `HAIRCUT_PP == median` |

Không đọc đồng hồ hệ thống (0 hit `now()/today()/time.time/fromtimestamp`) ⇒ **không phụ thuộc TZ**;
xác nhận bằng cách chạy lại PASS dưới `env -u TZ`, `TZ=America/Los_Angeles`,
`TZ=Pacific/Kiritimati`, `TZ=UTC` (coding_guidelines §16 + skill `verify-before-done`).

---

## 4. ĐO LẠI BREAK-EVEN JOB U THEO THÁNG — `carry_paired_tiered.py`

Đúng khuôn Job U: 12 leg pin `*_parkgrid_*_univpit.csv` (dùng 3 tag 000/030/080), credit carry lên
`max(bal_cash_ref+lag_cash_ref, 0)` theo ngày dương lịch, paired block bootstrap **L=21 B=4000
seed=12345**. **Chỉ đổi MỘT biến**: lãi tiền nhàn rỗi từ HẰNG SỐ → VECTO theo ngày qua `r_idle`.
Cửa sổ leg pin: **2014-01-02 → 2026-06-19**, 3.107 ngày, 12,46 năm.

**Hai chân đối chứng tái hiện ĐÚNG số pin Job U** (điều kiện đọc số, không phải sau khi đọc):

| | CAGR act (0,00/0,30/0,80) | E[Calmar] | DD5th |
|---|---|---|---|
| tier `zero` (mô phỏng giả định 0%) | 22,366 / 23,430 / 24,950 | 1,5073 / 1,4761 / 1,2159 | −24,00 / −25,15 / −31,98 |
| Job U `base0pct` (pin) | 22,366 / 23,430 / 24,950 | 1,5073 / 1,4761 / 1,2159 | −24,00 / −25,15 / −31,98 |
| tier `flat_8.543` | 28,435 / 28,393 / 28,048 | 2,1156 / 1,9622 / 1,4386 | −21,21 / −22,44 / −29,96 |
| Job U `carry` (pin, 8,55%) | 28,441 / 28,397 / 28,051 | 2,1161 / 1,9627 / 1,4387 | −21,21 / −22,44 / −29,96 |

(lệch ≤0,006pp CAGR = đúng chênh 8,543 vs 8,550 — chủ ý, không phải sai số.)

### Bảng kết quả theo tầng

| tier | mean %/năm (gia quyền ngày) | park | CAGR act | E[CAGR] | **E[Calmar]** | **DD5th** | cổng DD |
|---|---|---|---|---|---|---|---|
| **1 `baseline`** | **4,157** | 0,00 | 25,32% | 25,39% | **1,798** | **−22,43%** | OK |
| | | **0,30** | **25,85%** | 25,93% | **1,708** | **−23,75%** | OK |
| | | 0,80 | **26,46%** | 26,58% | 1,323 | −31,01% | **FAIL** |
| **2 `floor`** | **3,612** | 0,00 | 24,94% | 25,01% | **1,762** | **−22,54%** | OK |
| | | **0,30** | **25,53%** | 25,61% | **1,678** | **−23,87%** | OK |
| | | 0,80 | **26,24%** | 26,36% | 1,308 | −31,10% | **FAIL** |
| 3 `flat 8,543` (tham chiếu) | 8,543 | 0,00 | 28,44% | 28,51% | 2,116 | −21,21% | OK |
| | | 0,30 | 28,39% | 28,47% | 1,962 | −22,44% | OK |
| | | 0,80 | 28,05% | 28,17% | 1,439 | −29,96% | FAIL |
| 0 `zero` (giả định cũ) | 0,000 | 0,30 | 23,43% | 23,51% | 1,476 | −25,15% | OK |
| | | 0,80 | 24,95% | 25,07% | 1,216 | −31,98% | FAIL |

Cổng DD = `DD5th ≥ DD5th(park=0) − 2,0pp` (prereg v2). Floor: −24,43% (tầng 1) / −24,54% (tầng 2).

### Xác suất ghép cặp — **con số quyết định**

| tier | **P(Calmar 0,30 > 0,80)** | **P(CAGR 0,30 > 0,80)** | P(Calmar 0,00 > 0,30) | break-even |
|---|---|---|---|---|
| 1 `baseline` | **0,8680** | **0,3695** | 0,6050 | phải ×**1,660** cả đường cong (⇔ mean **6,90%/năm**) |
| 2 `floor` | **0,8632** | **0,3528** | 0,5995 | phải ×**1,860** (⇔ mean **6,72%/năm**) |
| 3 `flat 8,543` | 0,9075 | 0,5647 | 0,6737 | ×0,820 (⇔ 7,005%/năm — **tái hiện đúng 7,00% của Job U**) |
| 0 `zero` | 0,8030 | 0,2190 | 0,5205 | — |

Với đường cong biến thiên theo tháng, "break-even" không còn là một con số phẳng, nên đo bằng hệ
số nhân λ cần áp lên TOÀN đường cong để `CAGR(0,30) == CAGR(0,80)`; λ>1 nghĩa là tầng đó **chưa**
tới break-even. **Baseline không có tháng nào vượt 7,00%** (max 5,46%) — assertion T7 trong selfcheck
neo chính điều này.

---

## 5. BỐN ĐIỀU W2/W3 PHẢI MANG THEO (không kết luận Q3)

1. **Bỏ hẳn "0%".** Giả định cũ làm park=0,80 trông tốt hơn thực tế trên CAGR (+1,52pp) và làm
   đuôi DD của mọi cấu hình xấu hơn thực tế ~1,3–2,8pp. Tầng 1 là baseline mới.
2. **Luận điểm CAGR của Job U là TẦNG 3.** `P(CAGR 0,30>0,80)` = 0,565 ở 8,543% nhưng chỉ
   **0,353–0,370** ở tầng 1/2. Theo §4 bullet 4 của kế hoạch, điều này phải ghi là **"thắng nhờ
   khuyến mãi DNSE"**, không được wire theo.
3. **Cái ĐỨNG VỮNG là cổng DD, và nó đứng trên CẢ 4 tầng**: park 0,80 cho DD5th −31,0…−32,0% so
   với floor −23,2…−26,0% ⇒ FAIL bất kể carry. `P(Calmar 0,30>0,80)` = 0,80–0,91 trên mọi tầng.
   Quyết định 15:48 ICT hôm nay không bị lung lay bởi W1.
4. **Số mới mở ra câu hỏi cho W2, tôi KHÔNG trả lời ở đây**: `E[Calmar]` của **park = 0,00** cao
   hơn park 0,30 trên **mọi** tầng (1,798 vs 1,708 ở tầng 1; `P(0,00>0,30)` = 0,52–0,67). Đó đúng
   là nhánh 1 của cây quyết định Q3 (`D ≥ A`) và phải đo trong khuôn A/B/C/D của W2, không suy từ
   đây — lưới này chỉ có 3 mức park, không có ứng viên rổ nào khác.

## 6. Việc CHỜ DUYỆT (không tự làm)
- `mike/kb/data_registry/macro/fiinprox_rates_snapshot_20260927.md.proposed` — nâng
  `UNVERIFIED-PIT-CANDIDATE` → `CANONICAL-PIT` **giới hạn phạm vi xác minh 2025-11→2026-09**
  (§13: Mike duyệt, KHÔNG merge). Người duyệt cần quyết một điều tường minh: **đoạn 2011-01→2025-10
  chưa có nguồn thứ hai** — chấp nhận dùng cho backtest hay không.
- quant-skeptic CONFIRMED (đòn 1 look-ahead + đòn 7 số học) trước khi W2 dùng proxy này làm baseline.
