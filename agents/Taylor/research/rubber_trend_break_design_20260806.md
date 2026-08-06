# Tầng cảnh báo TREND_BREAK cho giá cao su RSS3 — thiết kế + backtest

**Job** `Taylor_20260806_131319` · **Ngày** 2026-08-06 · **Tác giả** Taylor
**Trạng thái** ✅ **ĐÃ WIRE VÀO PRODUCTION 2026-08-06** (user duyệt, job `Taylor_20260806_141609`) —
`rubber_trend_break.py` (module mới) + `rubber_weekly.py` (`trend_break_check()`, note, main) +
`rubber_weekly_selfcheck.py` §8. Selfcheck **121/121 PASS** dưới 4 môi trường TZ (gồm `env -u TZ`);
quant-skeptic **REFUTED vòng 1** (bug thật: nhánh first-run nuốt cờ PROVISIONAL → nuôi 1 alert giả
sau này) → đã sửa + 8 regression check → **CONFIRMED vòng 2 (cao)**. Chi tiết ở §9 cuối file.
**Artifact** `mike/agents/Taylor/exp_rubber_trend/` (T1–T6, chạy lại được)
**Nối tiếp** bug band 52 tuần sáng nay (commit `d2aeb9f`, quant-skeptic CONFIRMED)

---

## 0. TL;DR — 5 câu trả lời cho 5 câu hỏi user

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | "Đường xu thế 100 ngày" = hồi quy hay MA? | **MA, không phải hồi quy.** OLS thua rõ trên mọi thước đo (precision 49–53% vs 73–85%, whipsaw 60–77% vs 8–20%). Và trong họ MA thì **MA200 (không phải MA100)** là điểm ngọt. |
| 2 | Đủ dữ liệu để tính MA100/MA200 ngày chưa? | **CHƯA — và còn rất xa.** Chuỗi ngày THẬT mới 34 print / 47 ngày lịch. MA100 ngày ETA **2026-11-04**, MA200 ngày ETA **2027-03-22**. |
| 3 | Vậy có làm được ngay không? | **CÓ** — chạy trên chuỗi **THÁNG World Bank** (244 tháng, 2006-04→2026-07, 0 tháng thiếu). MA10 tháng ≡ MA200 ngày. Đây cũng là lựa chọn ĐÚNG chứ không phải đắp tạm (§4). |
| 4 | Backtest có đứng vững không? | **Một nửa.** Bắt chu kỳ: **recall 5/5, precision 85%**, ổn định OOS, plateau chứ không phải điểm nhọn. Dự báo phần giảm còn lại: **KHÔNG có** (31% vs base 32%). |
| 5 | Độc lập hay thay thế WATCH/ALERT? | **Độc lập.** Khác chân trời thời gian, khác câu hỏi, khác nhịp bắn (1 lần/18,7 tháng vs hàng tuần). |

**Trạng thái hôm nay nếu tier này đã sống: `UPTREND`** — giá 2,680 vs MA10 **2,440**, tức **+9,8% TRÊN đường**, uptrend liên tục từ 2026-02, 0/2 tháng gần nhất dưới đường. **TREND_BREAK sẽ KHÔNG bắn.** Trực giác của user đúng: cú −6,6% tuần này là nhiễu trong một up-leg còn nguyên.

---

## 1. T1 — Dữ liệu có gì (làm trước, đúng bài học sáng nay)

Bug sáng nay sinh ra chính từ việc **đếm dòng thay vì kiểm tra độ phủ theo lịch**. Nên bước đầu tiên ở đây là đo lại đúng thứ đó, trước khi thiết kế bất cứ gì.

### Chuỗi NGÀY (`data/rubber_weekly.csv`)

```
rows total in file      : 41
rows RSS3 non-null      : 38
rows REAL (src != wb_seed): 34          <-- chỉ 34 print thật
first REAL / last REAL  : 2026-06-19 -> 2026-08-05
calendar span REAL      : 47 days (6.7 weeks)
max gap between prints  : 3 days
```

Tốc độ tích lũy thật đo được = **0,72 print/ngày lịch**:

| Cần | Có | ETA |
|---|---|---|
| MA100 ngày (100 obs) | 34 | **~2026-11-04** (còn ~3 tháng) |
| MA200 ngày (200 obs) | 34 | **~2027-03-22** (còn ~7,5 tháng) |

⚠️ **Không được dùng 4 dòng `wb_seed` để độn cho đủ.** Đó đúng là cái bẫy của bug sáng nay: seed không phải quan sát ngày thật, trộn vào rồi gọi là "MA200 ngày" là tự dối. **Kết luận cứng: hôm nay KHÔNG thể tính MA100/MA200 trên chuỗi ngày.**

### Chuỗi THÁNG (`data/rubber_monthly.csv`, World Bank Pink Sheet)

```
rows        : 244        range: 2006-04 -> 2026-07
missing months : 0       price range: 1.20 - 6.26 USD/kg
```

20,2 năm liền mạch, không thủng. **Đây là nền backtest duy nhất có ý nghĩa.**

### Quy đổi cửa sổ (21 phiên/tháng)

| Ngày | ≈ Tháng |
|---|---|
| MA100 ngày | MA4,8 → dùng **MA5 tháng** |
| MA200 ngày | MA9,5 → dùng **MA10 tháng** |

---

## 2. T5(A) — Hồi quy hay MA? (câu hỏi #1 của user)

Cùng một thước đo, cùng một mẫu, 5 chu kỳ giảm ≥25% trong 2006-04..2026-07:

| Định nghĩa đường | Confirm | Recall chu kỳ | Precision | Tần suất bắn | **Whipsaw** |
|---|---|---|---|---|---|
| OLS hồi quy 5 tháng (~100 phiên) | 1 kỳ | 4/5 | 23/43 = **53%** | 1/5,7 th | **60%** |
| OLS hồi quy 5 tháng | 2 kỳ | 4/5 | 17/35 = **49%** | 1/6,9 th | **77%** |
| OLS hồi quy 10 tháng (~200 phiên) | 1 kỳ | 4/5 | 12/25 = 48% | 1/9,7 th | 24% |
| OLS hồi quy 10 tháng | 2 kỳ | 4/5 | 12/21 = 57% | 1/11,6 th | 24% |
| MA5 tháng (~MA100 ngày) | 2 kỳ | 5/5 | 13/19 = 68% | 1/12,8 th | 11% |
| **MA10 tháng (~MA200 ngày)** | 1 kỳ | 5/5 | 11/15 = 73% | 1/16,2 th | 20% |
| **MA10 tháng (~MA200 ngày)** | **2 kỳ** | **5/5** | **11/13 = 85%** | **1/18,7 th** | **8%** |

**Kết luận: dùng MA, bỏ đường hồi quy.** Không phải sát nút — OLS thua ở *cả ba* trục cùng lúc: precision gần mức tung đồng xu (49–53%), whipsaw 60–77% (tức phần lớn tín hiệu bị đảo ngay trong 2 kỳ), và bắn dày gấp 3 lần. Lý do cơ học: đường hồi quy **xoay theo độ dốc** — trong một up-leg mạnh nó dốc lên nhanh hơn giá, nên chỉ cần giá đi ngang là "phá đường". Đó là thứ user đang muốn tránh, không phải thứ muốn bắt.

Và trong họ MA, **MA10 (≡ MA200 ngày) thắng MA5 (≡ MA100 ngày)** — nên đề xuất chốt ở **MA200-equivalent**, đúng khái niệm đội đã dùng cho cổ phiếu.

---

## 3. T3+T4 — Backtest: nó bắt được gì, và KHÔNG bắt được gì

### 3a. Bắt chu kỳ đảo chiều — ĐẠT

5 chu kỳ giảm thật ≥25% trong 20,2 năm (phát hiện bằng zigzag 25%):

| Đỉnh | Đáy | Mức giảm | Break confirm-2 kỳ | Trễ |
|---|---|---|---|---|
| 2008-09 (2,83) | 2008-12 (1,20) | −58% | 2008-10 | +1 th |
| 2011-02 (6,26) | 2016-01 (1,23) | −80% | 2011-07 | +5 th |
| 2017-02 (2,71) | 2018-11 (1,35) | −50% | 2017-07 | +5 th |
| 2019-06 (1,93) | 2020-04 (1,33) | −31% | 2019-09 | +3 th |
| 2021-03 (2,37) | 2022-11 (1,43) | −40% | 2021-07 | +4 th |

**Recall 5/5. Precision 11/13 = 85%** (2 báo ngoài chu kỳ: 2023-07, 2025-04).

### 3b. Có ổn định không, hay là dò tham số?

**Grid MA6→MA15 × confirm 1/2/3 kỳ (24 ô):**

```
MA  9 | c2: R 5/5  P 71%      MA 10 | c2: R 5/5  P 85%   <-- đề xuất
MA 11 | c2: R 5/5  P 91%      MA 12 | c2: R 5/5  P 89%
MA 15 | c2: R 5/5  P 80%      MA  5 | c2: R 5/5  P 68%
```

Recall **5/5 ở mọi ô** từ MA8 trở lên; precision là một **plateau rộng 71–91% suốt MA9→MA15**. MA10 nằm giữa plateau, **không phải đỉnh nhọn** — nghĩa là kết quả không phụ thuộc vào việc chọn đúng con số 10. (MA11 có precision cao hơn 91% nhưng chọn nó vì nó cao nhất mới đúng là dò tham số; MA10 được chọn vì nó là quy đổi tự nhiên của MA200 ngày — tham số đặt TRƯỚC khi nhìn kết quả.)

**IS/OOS** (IS 2006–2016, OOS 2017–2026):

| | Recall | Precision |
|---|---|---|
| IS MA10 c2 | 2/2 | 5/5 = 100% |
| **OOS MA10 c2** | **3/3** | **6/8 = 75%** |

Giữ được OOS. Precision rơi 100%→75% là mức rơi bình thường, không phải sụp.

### 3c. ⚠️ KHÔNG dự báo phần giảm còn lại — kết quả âm quan trọng nhất của cả nghiên cứu

Đây là chỗ tôi nghĩ dễ đọc sai nhất, nên nói thẳng:

**P(giá giảm tiếp thêm X% trong 6 tháng SAU khi tín hiệu bắn):**

| Ngưỡng | Base rate (mọi tháng) | Sau TREND_BREAK (MA10 c2) | Chênh |
|---|---|---|---|
| ≥10% | 46% | **38%** | **−8pp (tệ hơn base)** |
| ≥15% | 32% | **31%** | **−1pp (≈ base)** |
| ≥20% | 22% | **23%** | **+1pp (≈ base)** |

**Bằng 0.** Biết tín hiệu đã bắn **không** cho bạn thêm thông tin nào về việc giá còn giảm tiếp bao nhiêu.

Lợi suất forward cũng nói y hệt — MA10 c2: fwd-3m −4,10% (base +1,60%), nhưng **CI95 [−11,2; +3,1] chứa 0**; fwd-6m **+0,34pp**; fwd-12m **+6,36pp** (tức 12 tháng sau khi "phá xu thế", giá trung bình *cao hơn* base rate).

Lý do cơ học nằm ở **độ trễ** (T4): tín hiệu bắn trễ **trung vị 4 tháng** sau đỉnh, và tại thời điểm bắn **trung vị −24% của cú giảm đã đi qua rồi**. Nó xác nhận một chế độ đã bắt đầu; nó không nhìn thấy trước.

> **Cách đọc đúng: TREND_BREAK là XÁC NHẬN CHẾ ĐỘ, không phải DỰ BÁO.** Câu nó trả lời là "cấu trúc xu hướng dài hạn đã gãy chưa?" (85% đúng), không phải "giá sắp giảm nữa không?" (không biết). Nhãn trong tin nhắn phải nói đúng điều này, nếu không người đọc sẽ tự suy ra vế thứ hai.

### 3d. ⚠️ Và nó KHÔNG phải tín hiệu bán cổ phiếu cao su

Vì đội có GVR/PHR/DPR/DRI/TRC/HRC trong tầm ngắm, tôi kiểm luôn — rổ 6 mã, 236 tháng:

| Chân trời | Base rổ CP | Sau MA10 c2 | Chênh |
|---|---|---|---|
| fwd-3m | +7,57% | −0,68% | −8,25pp (CI chứa 0) |
| fwd-6m | +5,91% | +2,07% | −3,83pp (CI chứa 0) |
| **fwd-12m** | +12,51% | **+26,51%** | **+13,99pp, CI95 [+6,5;+50,4] — DƯƠNG, không chứa 0** |

Ở chân trời 12 tháng, cổ phiếu cao su lịch sử **tăng mạnh hơn base** sau khi giá hàng hóa phá xu thế. (Hợp lý: tín hiệu bắn gần vùng bi quan, cổ phiếu đã chiết khấu trước.) **Tuyệt đối không dùng tier này làm cớ bán GVR/PHR/DPR/DRI.** Nếu có ai muốn dùng theo chiều đó thì bằng chứng đang chỉ ngược lại.

---

## 4. T5(B) — Vì sao chạy trên chuỗi THÁNG là lựa chọn ĐÚNG, không phải đắp tạm

Câu hỏi tự nhiên: "chờ tới 2027-03 có chuỗi ngày đủ rồi chạy MA200 ngày cho chuẩn?" Tôi đo thử trên tài sản **có** chuỗi ngày dài thật — chính rổ cổ phiếu cao su (BQ, 2007+, 92 mã-năm):

| Mã | MA200 NGÀY | MA10 THÁNG |
|---|---|---|
| DPR (18,7y) | 94 lần (1/2,4 th) | 18 lần (1/12,5 th) |
| HRC (19,6y) | 108 lần (1/2,2 th) | 17 lần (1/13,8 th) |
| PHR (17,0y) | 73 lần (1/2,8 th) | 14 lần (1/14,5 th) |
| TRC (19,0y) | 54 lần (1/4,2 th) | 11 lần (1/20,8 th) |

**Chuỗi ngày bắn nhiều gấp ~5,2 lần chuỗi tháng trên CÙNG tài sản, CÙNG khái niệm đường.**

Và **xác nhận theo phiên không vá được**: confirm 2 phiên chỉ giảm 168→~130, confirm 5 phiên còn ~39–45 lần/mã; thêm vùng đệm 5% cũng chỉ 168→138. Vẫn còn xa mức 1/18,7 tháng của chuỗi tháng.

**Hàm ý:** MA200-ngày và MA200-tháng-quy-đổi là **hai vật thể khác nhau**, không thay thế cho nhau được. Con số 85% precision ở trên là của **chuỗi tháng**. Nếu đến 2027-03 ta chuyển sang chuỗi ngày, ta sẽ **triển khai một thứ chưa được backtest** và gần như chắc chắn nhiễu hơn nhiều lần. → **Chạy trên chuỗi tháng, và giữ nguyên như vậy kể cả sau khi chuỗi ngày đủ dài.** Chuỗi ngày lúc đó dùng để ước lượng tháng đang chạy cho mượt hơn, không phải để đổi nền tín hiệu.

Đây là lý do thực chất, không phải lý do tiện: giới hạn dữ liệu ở §1 tình cờ đẩy ta về đúng thiết kế nên chọn.

---

## 5. Đề xuất thiết kế cụ thể

Bản tham chiếu chạy được: `exp_rubber_trend/t6_reference_impl.py` (**selfcheck 17 PASS / 0 FAIL**, tái chạy PASS dưới `env -u TZ` và `TZ=America/New_York` — §7).

### 5.1 Định nghĩa

```
đường   = MA10 trên chuỗi THÁNG World Bank        (≡ MA200 ngày)
sự kiện = giá tháng đóng dưới đường, XÁC NHẬN 2 THÁNG LIÊN TIẾP
trạng thái = DOWNTREND / UPTREND  (đây là TRẠNG THÁI, không phải sự kiện một lần)
đóng    = cắt lên lại trên đường, cũng xác nhận 2 tháng
```

### 5.2 Chống nhiễu (câu hỏi #3 của user)

Ba lớp, cùng tinh thần với bản vá band sáng nay:

1. **Xác nhận 2 kỳ** — đúng thứ user gợi ý. Đo được: whipsaw **20% → 8%**, precision **73% → 85%**. Đây là lớp có giá trị đo được, không phải phỏng đoán.
2. **Chạy trên chuỗi tháng, không phải ngày** (§4) — lớp giảm nhiễu lớn nhất (5,2×), và là lớp mà nếu bỏ qua thì hai lớp kia không cứu nổi.
3. **Tháng đang chạy = PROVISIONAL.** Tháng hiện tại được ước lượng bằng trung bình các print NGÀY THẬT trong tháng (loại `wb_seed`). Tín hiệu phụ thuộc vào điểm ước lượng này **phải gắn cờ `PROVISIONAL`** và chỉ chốt khi WB công bố tháng đó. Đây chính là lỗ hổng đã tạo ra bug sáng nay ở dạng khác: một điểm dữ liệu chưa đầy đủ được đối xử như dữ liệu đã chốt.

### 5.3 Độc lập, không thay thế (câu hỏi #4 của user)

| | WATCH/ALERT (đang có) | **TREND_BREAK (mới)** |
|---|---|---|
| Câu hỏi | "tuần này có gì lạ không?" | "cấu trúc xu hướng dài hạn gãy chưa?" |
| Chân trời | 1 tuần | 6–24 tháng |
| Nhịp bắn | hàng tuần | **1 lần/18,7 tháng** |
| Nguồn | print ngày | chuỗi tháng WB |
| Kiểu | sự kiện | **trạng thái (có mở/đóng)** |

**Giữ cả hai, chạy song song.** Hai tầng cũ trả lời câu hỏi mà tầng mới không trả lời được (và ngược lại). Trộn vào một thang bậc sẽ hỏng cả hai — một cái bắn hàng tuần, một cái bắn 1,5 năm/lần thì không xếp chung thang được.

**Tên tier:** `TREND_BREAK` (như user đề xuất) — rõ nghĩa, không đụng WATCH/ALERT. Trạng thái đối xứng: `TREND_OK`.

### 5.4 Mẫu tin nhắn đề xuất

```
🔴 TREND_BREAK — cao su RSS3 phá xu thế dài hạn
   giá tháng 2,05 USD/kg < MA200-eq 2,31 (−11,3%), xác nhận 2 tháng (2026-09, 2026-10)
   lần gần nhất: 2021-07 · tần suất lịch sử ~1 lần/18,7 tháng
   ⚠️ ĐÂY LÀ XÁC NHẬN CHẾ ĐỘ, KHÔNG PHẢI DỰ BÁO GIẢM TIẾP.
      Backtest: P(giảm thêm ≥15%/6th) = 31% ≈ base 32%.
      KHÔNG phải tín hiệu bán cổ phiếu cao su (fwd-12m rổ CP: +26,5% vs base +12,5%).
```

Dòng cảnh báo cuối **bắt buộc** phải có. Không có nó, một tier tên "TREND_BREAK" màu đỏ bắn 1,5 năm/lần sẽ tự động được đọc thành "bán đi" — đúng cái mà số liệu bác bỏ.

---

## 6. Giới hạn — đọc trước khi quyết định

1. **N = 5 chu kỳ, 13 sự kiện.** "Recall 5/5" nghe tuyệt đối nhưng với N=5 thì khoảng tin cậy vẫn rộng. Đây là **toàn bộ** dữ liệu tồn tại (20,2 năm giá cao su thế giới), không phải mẫu bị cắt — nhưng nó là trần cứng, không mở rộng được bằng cách chạy thêm.
2. **N_trials ≈ 63** đã so sánh (T2: 18 ô, T3: 12+9, T4: 24). Với 63 phép so sánh, việc **1–2 khoảng CI95 vừa đủ loại 0 KHÔNG phải bằng chứng**. Vì vậy mọi kết luận ở trên chỉ dựa vào (i) recall/precision chu kỳ — cấu trúc đặt trước khi nhìn số, và (ii) plateau của grid; **không** dựa vào ô nào có p-value đẹp nhất. Đây cũng là lý do §3c được báo cáo như kết quả âm thay vì bị bỏ qua.
3. **Độ trễ là cố hữu, không tối ưu đi được.** Trung vị 4 tháng sau đỉnh, −24% đã mất. Grid ở §3b cho thấy đánh đổi này liên tục: confirm ngắn hơn → trễ ít hơn nhưng precision giảm. Không có ô nào vừa nhanh vừa chính xác.
4. **Không đo trên chuỗi ngày** vì chuỗi ngày chưa tồn tại (§1). §4 lập luận rằng ta cũng **không nên** chuyển sang chuỗi ngày — nhưng đó là lập luận suy ra từ tài sản đại diện (cổ phiếu cao su), không phải đo trực tiếp trên RSS3 ngày. Điểm này nên kiểm lại sau 2027-03.
5. **Không có look-ahead:** lợi suất forward tính từ `t+1` (`fwd()` dùng `price[i+1+h]/price[i+1]`), tức đã tính cả độ trễ công bố của WB Pink Sheet (~tuần đầu tháng sau). MA và cờ xác nhận đều nhân quả (`rolling` + `shift`).
6. **Đây là bằng chứng thống kê trên giá hàng hóa, không phải bằng chứng P&L.** RSS3 không phải công cụ ta giao dịch được. Bảng "thoát khi phá đường" (T3c: buy&hold 1,30× / MaxDD −80% vs thoát-khi-phá 5,30× / MaxDD −44%) là mô tả tính chất của đường xu thế, **không phải một chiến lược có thể triển khai**.

**Ghi chú đối chiếu nội bộ:** T2 in ra một phép đếm precision khác (4/13) do bộ dò chu kỳ greedy-argmax của nó chỉ tìm được 1 chu kỳ mega 2011–2016 nên gán nhầm 9 tín hiệu là "ngoài chu kỳ". T3 thay bằng zigzag 25% và tìm đúng 5 chu kỳ → **11/13 = 85% là con số đúng**, T2 đã bị thay thế. Nêu ra để ai đọc lại artifact không bị hai con số vênh nhau làm rối.

---

## 7. Selfcheck / tái lập

```bash
cd mike/agents/Taylor/exp_rubber_trend
P=/home/trido/thanhdt/wc_venv/bin/python
$P t1_data_availability.py     # dữ liệu có đủ không
$P t2_backtest.py              # lợi suất forward + tần suất
$P t3_cycle_and_stocks.py      # recall/precision + rổ cổ phiếu
$P t4_sensitivity.py           # grid + IS/OOS + độ trễ
$P t5_ols_and_daily_bridge.py  # hồi quy vs MA + cầu nối tháng→ngày
$P t6_reference_impl.py             # trạng thái hôm nay
$P t6_reference_impl.py --selfcheck # 17 PASS / 0 FAIL
```

Selfcheck chạy lại dưới `env -u TZ` và `TZ=America/New_York` — **17 PASS cả ba lần** (kỷ luật `verify-before-done`; code không phụ thuộc TZ vì mọi mốc thời gian đọc từ CSV, nhưng vẫn kiểm thay vì giả định).

**Production không bị đụng:** `git diff` trong `WorkingClaude` không có `rubber_weekly.py`; toàn bộ artifact nằm trong `mike/agents/Taylor/exp_rubber_trend/` (thư mục thí nghiệm, đúng `coding_guidelines §8`).

---

## 8. Khuyến nghị

**GO có điều kiện** — cơ chế đứng vững, nhưng chỉ cho đúng mục đích của nó.

| Hạng mục | Khuyến nghị | Độ tin cậy |
|---|---|---|
| Dùng MA thay đường hồi quy | **GO** | **CAO** — thua/thắng rõ trên cả 3 trục, cơ chế giải thích được |
| MA200-eq (MA10 tháng) thay MA100-eq | **GO** | **CAO** — plateau rộng, không nhạy tham số |
| Xác nhận 2 kỳ | **GO** | **CAO** — whipsaw 20%→8% đo được |
| Chạy trên chuỗi tháng (không phải ngày) | **GO** | **CAO** — 5,2× đo trên tài sản có chuỗi ngày thật |
| Tier độc lập, không thay WATCH/ALERT | **GO** | **CAO** — khác chân trời/nhịp/kiểu |
| Đọc là "xác nhận chế độ" | **GO** | **TRUNG BÌNH** — recall 5/5 & precision 85% nhưng N=5 |
| Đọc là "dự báo giảm tiếp" | **NO-GO** | **CAO** — 31% vs base 32%, kết quả âm rõ |
| Dùng để bán cổ phiếu cao su | **NO-GO** | **CAO** — fwd-12m rổ CP DƯƠNG so base, CI không chứa 0 |

**Nếu user duyệt**, quy trình còn lại đúng như phần band sáng nay: code → selfcheck → **quant-skeptic verify** → wire. Tôi không tự làm bước nào trong số đó.

**Lưu ý cho lần bắn đầu tiên:** tier này bắn 1 lần/18,7 tháng. Hiện đang `UPTREND` và cách đường **+9,8%**, nên nhiều khả năng **không bắn gì trong nhiều tháng tới**. Đó là hành vi đúng, không phải hỏng — nhưng nên có một dòng heartbeat định kỳ ("TREND_BREAK: UPTREND, +9,8% trên đường") để im lặng không bị nhầm với pipeline chết (đúng quy ước heartbeat của đội).

---

## 9. Wire vào production — 2026-08-06 (job `Taylor_20260806_141609`)

Tham số **không đổi** so với thiết kế đã duyệt: MA10 tháng (≡ MA200 ngày), xác nhận 2 kỳ, chạy
trên chuỗi THÁNG World Bank, tên tín hiệu `TREND_BREAK`/`TREND_OK`, độc lập WATCH/ALERT.

| File | Thay đổi |
|---|---|
| `rubber_trend_break.py` | **MỚI** — toàn bộ phần toán + văn bản cảnh báo. `evaluate()` trả `state` (có tháng tạm) và `state_firm` (CHỈ tháng đã công bố). |
| `rubber_weekly.py` | `trend_break_check()` (bắn **chỉ khi ĐỔI trạng thái**), 1 khối trong `data/rubber_watch.md`, 1 dòng heartbeat mỗi phiên. Diff thuần cộng thêm: chỉ 4 dòng cũ bị thay (chữ ký `render_note`, chỗ gọi nó, 1 dòng `L +=`). |
| `rubber_weekly_selfcheck.py` | §8: **61 check mới** (60 check cũ của tầng WATCH/ALERT giữ nguyên và vẫn PASS). |

**Ba hành vi cố ý:** (1) lần chạy đầu tiên = nhận trạng thái nền, **im lặng** (wire một tầng không
được tự trông như một tín hiệu) — và nền lấy từ **state_firm**, không bao giờ từ tháng chưa công bố;
(2) flip phụ thuộc tháng đang chạy → **PROVISIONAL**: chỉ bus cho Taylor, **không Telegram**, không
ghi state, dedupe theo tháng; (3) mọi tin nhắn (Telegram + payload bus + note) đều mang bắt buộc
dòng "XÁC NHẬN CHẾ ĐỘ, KHÔNG PHẢI tín hiệu bán/dự báo" kèm 31% vs base 32% và +26,5% vs +12,5%.

**Selfcheck:** 121/121 PASS, exit 0, chạy thật dưới `TZ=Asia/Ho_Chi_Minh`, `env -u TZ`,
`TZ=America/New_York`, `TZ=UTC` — kết quả giống hệt (kỷ luật `verify-before-done`).
Trong đó có bài **tái lập backtest** trên cửa sổ ĐÓNG BĂNG 2006-04..2026-07 (244 tháng): 5 chu kỳ
zigzag-25%, **recall 5/5**, **13 sự kiện / 11 trong chu kỳ = 85%**, 2 false positive đúng là
2023-07 và 2025-04, tần suất 18,8 tháng. Đóng băng cửa sổ để WB công bố thêm tháng không biến một
hồi quy thật thành "số nó chạy".

**quant-skeptic — REFUTED vòng 1, CONFIRMED vòng 2 (cao):**
- **Vòng 1 (`logs/verify_20260806_142956_269358.log`) — REFUTED, 1 lỗi THẬT:** nhánh first-run của
  `trend_break_check()` lấy `r['state']` (có thể phụ thuộc tháng CHƯA công bố) làm trạng thái nền
  ghi vĩnh viễn, **không** kiểm cờ `provisional` — trái đúng §5.2 lớp 3. Hậu quả: khi WB công bố số
  thật khác, hệ **chế ra một flip không có thật** và gửi Telegram/Bill.
- **Sửa:** `evaluate()` luôn trả `state_firm`/`since_firm`; first-run dùng `state_firm`; thêm 8 check
  (§8e-bis, §8e-ter). Chứng minh test bắt được bug thật bằng cách **gắn lại bug**: đúng 3 check FAIL
  (118/121), khôi phục → 121/121.
- **Vòng 2 (`logs/verify_20260806_143943_274132.log`) — CONFIRMED (cao):** reviewer tự chạy lại 4 lần
  ×4 TZ, tự gắn lại bug và xác nhận 3 check FAIL, tự đếm 60 check cũ vẫn PASS. Không phản biện nào
  sống sót; ứng viên gần nhất ("uớc lượng tháng tạm có thể *chặn* một flip thật không?") bị bác:
  với confirm=2, một tháng nối thêm chỉ có thể **THÊM** flip, không thể **HUỶ** flip mà các tháng đã
  công bố vừa tạo ra → xấu nhất là tín hiệu đến **chậm 1 kỳ**, không bao giờ mất.

**Trạng thái hôm nay:** `TREND_OK` (UPTREND từ 2026-02), 2,68 vs MA200-eq 2,44 = **+9,8%**. Đúng như
dự kiến ở §8: tầng này sẽ **im lặng nhiều tháng** — dòng heartbeat mỗi phiên tồn tại để im lặng
không bị nhầm với pipeline chết. Lần chạy cron thật kế tiếp sẽ khởi tạo trạng thái nền, không bắn gì.
