# PREREG — "Post-shock base formation": mẫu hình tạo đáy cấp ĐƠN MÃ sau biến cố

- **Job**: `Taylor_20260823_025658` (dispatch từ Mike; ý tưởng gốc của user/John)
- **Ngày viết prereg**: 2026-08-23 · **Tác giả**: Taylor (Quant/Algo)
- **Trạng thái khi viết**: đã tra `mike/kb/data_registry/` (index + `price-volume/universe_pit.md`
  + `rating-8l/fa_ratings_8l.md`), đã đọc `research/calculated_fear_state_backstop.md`, đã kiểm
  tra schema/độ phủ 3 bảng nguồn bằng `bq show`/`COUNT` (metadata thuần: min/max date, thang
  rating, số mã/năm). **CHƯA tính bất kỳ event nào, CHƯA tính bất kỳ forward return nào.**
- **Phạm vi**: R&D / PAPER-ONLY. **Không đề xuất wire production trong lần này kể cả khi CONFIRM**
  (phải qua quant-skeptic trước — `coding_guidelines.md` §18, KB "quant-skeptic CONFIRMED =
  điều kiện cần").

---

## 0. Vì sao đo cái này

V2.4 hiện KHÔNG có tầng timing cấp **đơn mã sau shock**: BAL = momentum (SIGNAL_V11), LAG = PEAD,
regime = DT5G theo VNINDEX, breadth = cấp thị trường. Playbook `calculated_fear_state_backstop.md`
**§3 tranche T2** đã mô tả bằng VĂN XUÔI — *"T2 (1/3) khi có ổn định giá (higher-low + volume cạn
kiệt)"* — nhưng **chưa bao giờ có ngưỡng số và chưa bao giờ được backtest**. Đây là lần đo nó.

Câu hỏi đo được: **"chờ giá tạo nền" có thực sự đánh đổi được (bỏ lỡ một phần hồi phục sớm) lấy
(giảm rủi ro đuôi rơi tiếp) hay không — và hiệu ứng đó có phụ thuộc chất lượng doanh nghiệp
(8L rating) như bằng chứng 2/2 vs 0/4 trong KB gợi ý?**

---

## 1. Giả thuyết (khai TRƯỚC, một đuôi có hướng)

- **H0**: entry sau khi nền được xác nhận (b) không khác entry ngay lúc chạm ngưỡng shock (a) về
  forward return, và không khác VNINDEX cùng kỳ.
- **H1a (hướng cố định)**: với nhóm **RATING_OK**, entry (b) có **median forward return
  60/120 phiên CAO HƠN** (a) và/hoặc cao hơn VNINDEX cùng kỳ.
- **H1b (hướng cố định)**: entry (b) có **P(rơi tiếp ≥ −30% trong 250 phiên) THẤP HƠN** (a).
- **H1c (hướng cố định)**: hiệu ứng ở nhóm **RATING_BAD yếu hơn hoặc âm** so với RATING_OK
  (chất lượng doanh nghiệp là biến điều kiện chính, không phải biến phụ).

Hướng được cố định dựa trên cơ chế giả định + bằng chứng định tính KB (2/2 QUALIFY hồi phục,
0/4 NON không hồi phục), **không** dựa trên bất kỳ số liệu nào của chính nghiên cứu này.

---

## 2. Nguồn dữ liệu (đã tra registry — `coding_guidelines.md` §9)

| Thứ | Nguồn | Status registry | Ghi chú |
|---|---|---|---|
| Universe PIT | `lithe-record-440915-m9.tav2_mike.universe_pit` (`in_universe`) | **CANONICAL** | 2000-07-28→2026-08-21; 2008 ≈157 mã/phiên, 2009 ≈188 → đủ nghĩa từ 2008 |
| Giá / khối lượng | `tav2_bq.ticker` — `Close` (ĐÃ điều chỉnh), `Volume` | **CANONICAL** (`ticker_ohlcv_tables.md`) | `Close` adjusted ⇒ forward return = **total return** (đã gồm cổ tức), đúng bài học VEA của KB |
| Rating 8L PIT | `tav2_bq.fa_ratings_8l` (`ticker`,`time`=eff_date,`rating`) | **CANONICAL** | **Chỉ có từ 2014-07-09** — xem §6 giới hạn |
| Benchmark | hàng `ticker='VNINDEX'` trong `tav2_bq.ticker` | CANONICAL | **KHÔNG** dùng cột mirror `t.VNINDEX` trên hàng cổ phiếu (registry: TRAP) |

**KHÔNG dùng**: mọi cột `profit_*` / `_center_*` (forward-looking, cấm dùng ngoài train — CLAUDE.md).
**KHÔNG dùng** `ticker_prune` (registry TRAP + thiếu tên, vd BAF) làm universe.
**KHÔNG dùng** danh sách mã hiện tại lọc ngược lịch sử (survivorship) — universe lấy PIT theo phiên.

⚠️ **Điều chỉnh khai trước — turnover**: registry cảnh báo `Trading_Value` là cột derived
(`Price × Volume`) và không dùng cho VWAP. Ở đây turnover chỉ là **thước cạn kiệt thanh khoản**, và
tôi tự tính `turnover = Close × Volume` (cùng một bảng, cùng cơ sở adjusted) thay vì đọc
`Trading_Value`. Caveat đã biết: nếu có chia tách/thưởng GIỮA cửa sổ shock và cửa sổ nền thì
`Volume` (thô) và `Close` (adjusted) lệch cơ sở; tác động phần lớn triệt tiêu trong TỈ SỐ
(base/shock) và sẽ được báo cáo như một caveat, không sửa lén sau khi thấy số.

---

## 3. Định nghĩa SỰ KIỆN (chốt trước, không sửa sau khi thấy kết quả)

Mọi đại lượng tính trên `Close` adjusted, chỉ trên các phiên mà mã có `in_universe = TRUE`.

### 3.1 Shock
- `hi60_t = max(Close[t−59 … t])`, `t_peak` = phiên đạt `hi60_t` (argmax, lấy phiên GẦN NHẤT nếu trùng).
- **Ngày shock `t_s`** = phiên ĐẦU TIÊN thoả CẢ HAI:
  1. `Close_t / hi60_t − 1 ≤ −0,25` (giảm ≥25% từ đỉnh rolling 60 phiên)
  2. `t − t_peak ≤ 20` phiên giao dịch (**tốc độ nhanh** — loại downtrend bào mòn từ từ)

### 3.2 Đáy cục bộ, xác nhận POINT-IN-TIME
Quét TIẾN từ `t_s`. Gọi `t_b` là phiên thoả:
- `Close[t_b] = min(Close[t_s … t_b])` (là đáy chạy tới thời điểm đó), **và**
- `min(Close[t_b+1 … t_b+5]) > Close[t_b]` (5 phiên không phá đáy mới)

`t_b` là phiên ĐẦU TIÊN thoả; **ngày biết được `t_b` = `t_b + 5`** (không sớm hơn — đây là chỗ dễ
nhìn trước nhất, sẽ có assert cơ học ở §5.3).
**Hết hạn**: không xác nhận được đáy trong **60 phiên** sau `t_s` ⇒ sự kiện bị loại khỏi nhánh (b),
nhưng VẪN nằm trong nhánh (a) và được đếm riêng ("shock không tạo được nền / rơi tiếp").

### 3.3 Cửa sổ nền K = 20 phiên
Cửa sổ nền = `[t_b+1 … t_b+20]`. Cửa sổ shock (mốc so sánh) = `[t_peak … t_b]` (nhánh rơi).
**Nền XÁC NHẬN** tại `t_conf = t_b + 20` khi ĐỦ CẢ BA:
1. **Vol nén**: `std(logret) trên nền < 0,5 × std(logret) trên shock`
2. **Thanh khoản cạn**: `mean(turnover) trên nền < 0,5 × mean(turnover) trên shock`
3. **Higher-low**: `min(Close trên nền) ≥ Close[t_b]` (không phá đáy shock)

Sự kiện thoả cả 3 = **BASE_FORMED**; không thoả = **NO_BASE** (vẫn giữ trong mẫu, dùng để đo
"chọn lọc" ở §4.3).

### 3.4 Độc lập (N = SỰ KIỆN, không phải số dòng)
- Sau `t_s` của mã X, **mọi shock mới của X bị chặn tới `t_s + 250` phiên** (bằng horizon dài nhất).
- N báo cáo = số sự kiện SAU khi chặn, tách theo nhóm.
- ⚠️ Sự kiện còn **cụm theo thời gian** (khủng hoảng thị trường: 2008, 2011, 2018, 2020-03, 2022)
  ⇒ N độc-lập-theo-mã VẪN thổi phồng thông tin. Xử lý ở §4.2 bằng **cluster bootstrap theo khối
  thời gian**, và báo cáo thêm **số cụm lịch** (số tháng có sự kiện) bên cạnh N.

---

## 4. Ba biến thể ENTRY + đo lường

Thực thi theo quy ước nhà: **entry tại `Close` của phiên KẾ TIẾP sau ngày tín hiệu (T+1)**.

| Biến thể | Ngày tín hiệu | Ngày entry |
|---|---|---|
| **(a) bắt dao rơi** | `t_s` | `t_s + 1` |
| **(b) chờ nền xác nhận** | `t_conf = t_b + 20` | `t_conf + 1` |
| **(c) benchmark** | — | VNINDEX cùng NGÀY entry, cùng horizon với biến thể đang so |

### 4.1 Chỉ số đo, cho MỖI biến thể × MỖI nhóm rating × horizon H ∈ {60, 120, 250} phiên
1. `fwd_H = Close[entry+H] / Close[entry] − 1` (total return, vì Close adjusted)
2. `exc_H = fwd_H − fwd_H(VNINDEX)` cùng ngày entry, cùng H
3. `maxDD_H` = drawdown lớn nhất từ entry trong H phiên: `min(Close[entry…entry+H]) / Close[entry] − 1`
4. **Rủi ro đuôi**: `P(rơi tiếp ≥ −30%)` = tỉ lệ sự kiện có `maxDD_250 ≤ −0,30`

Horizon thiếu dữ liệu (sự kiện quá gần cuối mẫu) ⇒ **loại khỏi đúng horizon đó**, N báo riêng theo
horizon. Không nội suy, không kéo dài.

### 4.2 Thống kê
- Thống kê điểm = **median** (theo dispatch; phân phối forward return lệch phải mạnh, mean không bền).
- **CI + p-value bằng cluster block bootstrap, L = 20 phiên giao dịch, 10.000 replicate**: sắp sự
  kiện theo `t_s`, cắt trục thời gian thành khối liên tiếp 20 phiên, **resample KHỐI (mang theo
  toàn bộ sự kiện trong khối)** ⇒ giữ nguyên cả tự tương quan lẫn cụm chéo-mã.
- p một đuôi theo hướng H1, tính bằng dịch phân phối bootstrap về H0 (`p = mean(θ* − mean(θ*) ≥ θ_obs)`).

### 4.3 So sánh CHÍNH — có PHÂN BIỆT hai hiệu ứng (khai trước)
So (a) trên TOÀN BỘ shock với (b) trên riêng BASE_FORMED sẽ **trộn lẫn** hai thứ khác nhau. Vì vậy:
- **So sánh CHÍNH (hiệu ứng THỜI ĐIỂM, ghép cặp)**: chỉ trên tập **BASE_FORMED**, so entry (a) vs
  entry (b) **theo từng sự kiện** (paired). Đây là câu hỏi thật: *"cùng những case này, chờ nền có
  hơn không?"*
- **So sánh PHỤ (hiệu ứng CHỌN LỌC)**: entry (a) trên BASE_FORMED vs entry (a) trên NO_BASE — trả
  lời *"bản thân việc tạo được nền có phải tín hiệu tốt không, độc lập với thời điểm vào"*.
- (c) VNINDEX dùng làm mốc trừ nền beta thị trường (bài học TIS trong KB: nhầm beta ngành/thị
  trường thành edge của pattern).

### 4.4 Nhóm rating (biến điều kiện CHÍNH)
Rating lấy **as-of `t_s`** (một ảnh chụp DUY NHẤT cho cả (a) và (b) ⇒ nhóm giống hệt nhau giữa hai
biến thể, so sánh mới apples-to-apples):
- `rating_now` = bản ghi `fa_ratings_8l` mới nhất có `time ≤ t_s`
- `rating_prev` = bản ghi mới nhất có `time ≤ t_s − 120 ngày lịch` (≈ 1 quý trước, đảm bảo khác vintage)
- `Δ = rating_now − rating_prev` (thang 1 = tốt nhất … 5 = xấu nhất ⇒ Δ dương = XẤU ĐI)

⚠️ **Điều chỉnh khai trước so với dispatch**: dispatch viết `RATING_BAD = rớt ≥2 bậc **hoặc rớt
xuống ≥6**`. Thang thật của `fa_ratings_8l` là **1–5** (đã kiểm: rating ∈ {1,2,3,4,5}), không có
bậc 6. Ánh xạ giữ nguyên tinh thần "rơi xuống tầng tệ nhất":

- **RATING_BAD** = `Δ ≥ 2` **HOẶC** `rating_now = 5`
- **RATING_OK** = có đủ cả hai vintage **và** KHÔNG phải BAD
  (tương đương: `Δ ≤ 1` và `rating_now ≤ 4`; bao trọn mệnh đề "vẫn ≤3 nếu trước đó đã ≤3")
- **RATING_NA** = thiếu một trong hai vintage (toàn bộ sự kiện trước ~2015 + mã chưa có rating).
  Báo cáo RIÊNG, **không** gộp vào OK, **không** dùng để kết luận.

---

## 5. Kỷ luật thống kê + tính đúng đắn

### 5.1 Họ kiểm định CHÍNH — **BH FDR 10% trên đúng 12 test** (khai trước, đóng băng)
Chỉ trên biến thể **(b)**, 2 nhóm rating × 3 horizon × 2 loại thống kê:

| # | Nhóm | Thống kê | Horizon |
|---|---|---|---|
| T1–T3 | RATING_OK | median `exc_H` (vượt VNINDEX) > 0 | 60/120/250 |
| T4–T6 | RATING_OK | median paired `fwd_H(b) − fwd_H(a)` > 0 | 60/120/250 |
| T7–T9 | RATING_BAD | median `exc_H` > 0 | 60/120/250 |
| T10–T12 | RATING_BAD | median paired `(b) − (a)` > 0 | 60/120/250 |

Mọi test khác (RATING_NA, hiệu ứng chọn lọc §4.3, IS/OOS tách riêng, LOO, biến thể ngưỡng) là
**PHỤ** — báo p thô, **không** được dùng để tuyên bố CONFIRM.

### 5.2 Cổng rủi ro đuôi (gate riêng, khai trước, NGOÀI họ BH)
`Δp = P(maxDD_250 ≤ −30% | b) − P(… | a)` trên tập BASE_FORMED, nhóm RATING_OK, ghép cặp.
Cổng đạt khi `Δp < 0` với **p một đuôi < 0,05** (cùng cluster block bootstrap). Để ngoài họ BH vì
đây là **điều kiện AND bắt buộc** (làm khắt khe hơn), không phải một khám phá cạnh tranh —
ghi rõ ở đây để không bị coi là bới thêm test sau khi thấy số.

### 5.3 Chống nhìn trước + self-check bắt buộc
1. **Assert cơ học look-ahead**: với mỗi sự kiện, kiểm tra `entry_date ≥ t_b + 5` cho nhánh (b) và
   `entry_date > t_s` cho nhánh (a); mọi input tín hiệu có index ≤ ngày tín hiệu. Vi phạm ⇒ crash,
   không cảnh báo suông.
2. **Đối chiếu TAY với bảng KB** (`calculated_fear_state_backstop.md` §1/§8): PNJ 8/2015, VEA
   8/2019, OGC 10/2014, PVX 2017, FLC 3/2022, HVN 2021, TIS 4/2019, HPG 11/2022, DGC 3/2026,
   TV1/PC1 5/2026. Ghi rõ case nào **rơi vào mẫu / không rơi vào mẫu và VÌ SAO** (đây là kiểm
   tra logic, không phải kiểm tra kết quả).
3. **Recompute độc lập**: 5 sự kiện lấy ngẫu nhiên (seed cố định) tính lại `fwd_60/120/250` bằng
   truy vấn BQ TRỰC TIẾP (không qua cache/pipeline chính), khớp tới 1e-6.
4. `threads=1`, seed cố định, mọi CSV trung gian ghi ra tên **không canonical** (§8
   coding_guidelines): tiền tố `postshock_` + ngày.
5. Không có NAV/vốn trong nghiên cứu này ⇒ **self-check "0 VND" không áp dụng**; ba mục 1–3 ở trên
   là bản tương đương về mặt kiểm toán (khai trước để không bị hiểu là bỏ bước).

### 5.4 Walk-forward + LOO
- **IS = `t_s` trong 2008-01-01 … 2019-12-31** · **OOS = 2020-01-01 trở đi**.
- **LOO theo năm**: bỏ từng năm, tính lại thống kê chính (RATING_OK, H=120). Chỉ chạy nếu
  **N(RATING_OK) ≥ 30**; nếu không, ghi rõ "N quá mỏng, LOO không chạy" thay vì chạy rồi diễn giải.

---

## 6. Giới hạn ĐÃ BIẾT TRƯỚC (ghi trước để không bị dùng như phát hiện sau)

1. **Rating PIT chỉ có từ 2014-07-09.** Mọi sự kiện shock trước ~2015 (gồm TOÀN BỘ khủng hoảng
   2008 và 2011) rơi vào **RATING_NA** ⇒ nhánh phân nhóm rating mất phần lớn khủng hoảng lớn nhất
   lịch sử VN. **Không** thay bằng rating hiện tại gán ngược (look-ahead, cấm).
   Hệ quả: mẫu có rating ≈ 2015→2026, có thể chỉ vài chục sự kiện mỗi nhóm ⇒ **khả năng
   INCONCLUSIVE vì N mỏng là kịch bản có xác suất cao, đã lường trước.**
2. **Cụm chéo-mã**: sự kiện dồn vào vài đợt khủng hoảng ⇒ số lượng thông tin độc lập thật gần
   với **số ĐỢT** hơn là số mã. Đã xử lý bằng cluster bootstrap, nhưng không xử lý hết được.
3. **Gross, chưa trừ chi phí**: không phí, không slippage, không thuế. Quy đổi thực tế theo
   CLAUDE.md: **CAGR thật ≈ CAGR backtest − 1,5%**. Với mã thanh khoản mỏng sau shock, slippage
   thực tế còn tệ hơn (bài học §27: TV1 khớp 100/2.000cp).
4. **Không mô hình hoá huỷ niêm yết/đình chỉ**: `tav2_bq.ticker` ngừng có dòng khi mã rời sàn ⇒
   case kiểu FLC (mất trắng) có thể bị **kết thúc chuỗi sớm** thay vì ghi nhận −100%. Sẽ đo
   và báo số sự kiện bị cụt chuỗi; **rủi ro đuôi báo cáo là CẬN DƯỚI**, không phải ước lượng đúng.
5. **`Close` adjusted** ⇒ total return, tốt cho đo, nhưng không tách được cổ tức khỏi re-rating.
6. Nghiên cứu này đo **pattern giá**, KHÔNG đo discriminator định tính của playbook (scandal chạm
   lõi hay chưa, chu kỳ vs cấu trúc). Rating 8L là **proxy định lượng**, không thay được §2/§2.5.

---

## 7. Tiêu chí phán quyết (khai trước, KHÔNG sửa khi có kết quả)

### ✅ CONFIRM — cần ĐỦ CẢ HAI khối
- **(A) Lợi ích**: nhóm **RATING_OK**, biến thể **(b)**, tại ít nhất một trong horizon **60 hoặc
  120**: median vượt (a) [paired] **HOẶC** median vượt VNINDEX [`exc_H`], với **CI 95% không chứa 0**,
  **VÀ** ít nhất 1 horizon qua **BH FDR 10%** trong họ 12 test §5.1.
- **(B) Rủi ro đuôi**: cổng §5.2 đạt — `P(rơi tiếp −30%)` của (b) **thấp hơn có ý nghĩa** (b)
  so với (a), p một đuôi < 0,05.

### ❌ REFUTE
Nhóm RATING_OK cho **median paired (b)−(a) ≤ 0 ở CẢ 3 horizon** và `exc_H ≤ 0` ở cả 3 horizon
(tức chờ nền không mang lại gì), hoặc cổng rủi ro đuôi đi **ngược hướng** có ý nghĩa (b tệ hơn a).

### ⚠️ INCONCLUSIVE
Mọi trường hợp còn lại — **đặc biệt gồm** `N(RATING_OK) < 20` sự kiện độc lập, hoặc số cụm lịch
< 5. Khi đó **BẮT BUỘC ghi rõ "N quá mỏng"** và **không** diễn giải dấu của point estimate như
bằng chứng.

### Trong MỌI trường hợp
**KHÔNG đề xuất wire production.** Đầu ra tối đa = khuyến nghị một trong: (i) paper shadow có
theo dõi, (ii) đóng sổ, (iii) mở rộng mẫu (thêm nguồn rating pre-2014 / hạ ngưỡng shock để tăng N)
— và mọi bước tiếp phải qua **quant-skeptic** trước.

---

## 8. Artifact sẽ sinh ra

- `postshock_base_formation_20260823.md` — báo cáo kết quả
- `postshock_events_20260823.csv` — 1 dòng/sự kiện: ticker, t_peak, t_s, t_b, t_conf, base_formed,
  rating_now/prev/Δ, nhóm, entry dates, fwd_60/120/250 (a) và (b), maxDD, cờ cụt-chuỗi
- `postshock_stats_20260823.csv` — thống kê theo nhóm × horizon × biến thể (median, CI, p, BH)
- `postshock_base_formation_20260823.py` — script tái lập (seed cố định, threads=1)
- Bus event `finding` với trace_id `Taylor_20260823_025658`

**Prereg này được commit TRƯỚC khi chạy bất kỳ tính toán kết quả nào. Mọi sai lệch so với prereg
sẽ được ghi thành mục "Sai lệch so với prereg" trong báo cáo kết quả, KHÔNG sửa ngược file này.**
