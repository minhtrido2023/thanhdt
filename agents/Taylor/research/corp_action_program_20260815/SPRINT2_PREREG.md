# SPRINT 2 — PRE-REGISTRATION (cash dividend)

> **Committed BEFORE any outcome was computed.** Job `Taylor_20260815_121850`, 2026-08-15.
> Base: Sprint 1 ledger, commit `f8cb4596` (`out/event_ledger.csv.gz`, 35.465 sự kiện).
> Sau khi commit file này, **không sửa nó nữa**. Mọi lệch khỏi kế hoạch → `SPRINT2_DEVIATIONS.md`.

---

## 0. Ranh giới kế thừa từ gate CONDITIONAL PASS của Sprint 1

| | |
|---|---|
| ✅ ĐƯỢC | ex-date mechanical study · post-ex-date drift · neo **duy nhất** vào `exright_date` |
| ❌ CẤM | announcement study **dưới mọi hình thức** · dùng `public_date`/`known_date` làm ngày biết tin (kể cả tập con "trông sạch") |
| ❌ CẤM | đọc `ticker.Price` của dòng **đúng ngày ex-date** · trộn `Price` thô với `Close` hồi tố trong cùng một biểu thức · suy mức cổ tức từ `Close/Price` |
| ✅ BẮT BUỘC | số cổ tức chỉ lấy từ `div_total_on_exdate` (đã dedup theo ĐỢT rồi mới cộng) — không tự SUM dòng thô |

Nếu module A không dựng được giá ex-day thô một cách an toàn ⇒ **fail closed**: bỏ module A hoặc
hạ xuống descriptive-only. Không lấp bằng `Price` dòng ex-date.

---

## 1. Câu hỏi & giả thuyết

**Q-A (cơ học ex-date).** Ngày GDKHQ cổ tức tiền mặt, giá thực tế rơi bao nhiêu so với mức lý
thuyết (giá tham chiếu = giá cum − cổ tức)? Có lệch hệ thống không, và lệch đó có phụ thuộc tỉ
suất cổ tức không?

- **H-A0 (null):** lợi suất ex-day điều chỉnh thị trường `AR_ex` = 0 ⇒ thị trường rơi đúng bằng
  cổ tức, không có phần bù/thiệt hệ thống.
- **H-A1 (alt):** `AR_ex` ≠ 0. Tài liệu quốc tế thường thấy giá rơi **ít hơn** cổ tức (drop ratio
  < 1 ⇒ `AR_ex` > 0), quy cho thuế/microstructure. VN có đặc thù: **sở giao dịch ẤN ĐỊNH** giá
  tham chiếu ex-date = giá cum − cổ tức (làm tròn bước giá), nên `AR_ex` đo **phản ứng quanh mức
  đã bị áp đặt**, không phải quá trình khám phá giá tự do. ⇒ dấu kỳ vọng không được tiên đoán.

**Q-B (drift sau ex-date).** Sau ngày GDKHQ, cổ phiếu vừa đi ex có lợi suất bất thường không?

- **H-B0 (null):** `BHAR_20` = 0.
- **H-B1 (alt):** `BHAR_20` ≠ 0, và tăng theo tỉ suất cổ tức (giả thuyết "phục hồi sau khi bị
  cắt giá kỹ thuật" / dividend clientele).

**Cả hai câu hỏi đều có thể trả lời NULL. Kết quả null sẽ được báo cáo nguyên vẹn.**

---

## 2. Population

### 2.1 Nguồn sự kiện
`out/event_ledger.csv.gz` → `event_family = 'CASH_DIVIDEND'` ∧ `actionable = 1`
(⇒ `executed` ∧ có `exright_date` ∧ `value_per_share > 0`).
Gộp về **một quan sát cho mỗi cặp (ticker, exright_date)**, số cổ tức = `div_total_on_exdate`.

### 2.2 Cắt thời gian
`exright_date` ∈ [**2014-01-01**, **2026-06-30**]. Giới hạn dưới 2014 vì đó là mốc universe/DT5G
warm-up. Một sự kiện chỉ vào mẫu của horizon `h` **nếu phiên T+h tồn tại trong dữ liệu**
(`tav2_bq.ticker` tới 2026-08-14) ⇒ N khác nhau theo horizon, **phải báo N riêng cho từng horizon**.

### 2.3 Hai population, khai báo trước

| tên | định nghĩa | vai trò |
|---|---|---|
| **P-CORE** | 2.1 + 2.2 + có giá + `universe_pit.in_universe = TRUE` tại **đúng `exright_date`** (point-in-time) | **population CHÍNH** cho mọi kết luận cấp danh mục (Module B primary) |
| **P-WIDE** | 2.1 + 2.2 + có giá, **không** đòi universe_pit | chỉ dùng cho Module A (mô tả cơ học) và như một lát robustness của Module B |

Kỳ vọng từ Sprint 1 §6.3: P-CORE ≈ 3.032 sự kiện thô (trước bộ lọc nhiễm), P-WIDE ≈ 9.400.

⚠️ `universe_pit` có cờ `backfilled`. Tỉ lệ backfilled sẽ được **đo và công bố**; nếu >0 thì
tuyên bố "point-in-time" là point-in-time **theo thiết kế của rule**, không phải theo dấu vết
lịch sử của chính bảng — và phải nói ra như vậy.

### 2.4 Điều kiện giá (áp cho mọi module)
1. Ticker có phiên với `time = exright_date` **đúng bằng ngày**, `Close > 0` (nếu không có phiên
   đúng ngày ⇒ **loại**, đếm riêng; không được trượt sang phiên kế tiếp).
2. Có ít nhất 1 phiên trước ex-date và `h` phiên sau.
3. `Volume` trên phiên ex-date **> 0** (không có giao dịch ⇒ không có khám phá giá). Loại, đếm riêng.

---

## 3. Quy tắc loại nhiễm (contamination / overlap) — CỐ ĐỊNH

Nguồn: chính `event_ledger` (mọi `actionable = 1`, mọi họ).

| mã | quy tắc | áp cho |
|---|---|---|
| **X1a** | Có sự kiện ISS actionable thuộc subtype **điều chỉnh giá** (`STOCK_DIVIDEND` · `BONUS` · `RIGHTS`) trên cùng ticker với `exright_date` trong `[ex − 21, ex + W_h]` **ngày lịch** ⇒ loại | mọi module |
| **X1b** | Có **cặp (ticker, ex-date) CASH_DIVIDEND khác** trong `[ex − 21, ex + W_h]` ngày lịch ⇒ loại | mọi module |
| **X1c** | `W_h = 21` với `h ≤ 20`; `W_h = 90` với `h = 60` | — |
| **X2** | Loại 3 mã có chuỗi `Price` hỏng đã xác định ở Sprint 1 C3: **DNN, BCB, PTX**. Thêm: loại sự kiện có `P_cum_raw(T−1) < 1.000` VND | mọi module |
| **X3** | Tỉ suất gộp `y = div_total_on_exdate / P_cum_raw(T−1)`. Loại `y > 0,50`; **báo riêng** số bị loại, không loại im lặng | mọi module |
| **X4** | *(chỉ Module A)* hệ số điều chỉnh `r = Price/Close` phải tồn tại và > 0 tại T−1 và T+1..T+3, **và ổn định** trên T+1..T+3 trong ±0,1% (chứng cứ không có sự kiện điều chỉnh xen giữa) | Module A |

`W_h = 21`/`90` là dung sai **duy nhất** được khai báo. Không thử nhiều mức rồi chọn mức đẹp; một
mức thay thế (`W_h = 5`) được khai báo trước như **1 trial robustness**, kết quả báo dù tốt hay xấu.

---

## 4. Outcome & event window — CỐ ĐỊNH

Ký hiệu: `C_k` = `ticker.Close` (**đã hồi tố**) tại phiên lệch `k` so với phiên ex-date (`k = 0`
là chính phiên ex-date). `P_k` = `ticker.Price` (thô). `r_k = P_k / C_k`.

### 4.1 Đồng nhất thức được dùng thay cho việc đọc `Price` dòng ex-date

Với quy ước hồi tố **nhân** (`C_k = P_k × ∏ factor` các sự kiện SAU k), và
`factor_ex = (P_cum − D)/P_cum`:

```
C_0 / C_{−1}  ==  P_0 / (P_{−1} − D)   ==  P_ex_thô / giá tham chiếu lý thuyết
```

⇒ **lợi suất ex-day trên `Close` CHÍNH LÀ lợi suất so với giá tham chiếu lý thuyết**, và nó
**không đọc `Price` của dòng ex-date**. Đây là đường thoát khỏi bẫy dữ liệu đã biết.

Giá ex-day **thô** (chỉ cho outcome phụ) dựng lại bằng `P̂_0 = C_0 × r_{+1}` — lấy hệ số từ phiên
**T+1**, không bao giờ từ dòng ex-date. Hợp lệ vì `r` là hằng giữa hai sự kiện (X4 kiểm điều này).

**Nghĩa vụ chứng minh (phải làm, kết quả báo dù đạt hay không):**
- (i) so `r_{−1}/r_{+1}` với `P_{−1}/(P_{−1} − D)` trên toàn mẫu → tỉ lệ khớp ±0,2% / ±1%;
- (ii) **spot-check tay 12 sự kiện** phân tầng theo tỉ suất, in đủ `P_{−1}, C_{−1}, C_0, r_{+1}, D`;
- (iii) đối chiếu `P̂_0` với `P_0` thật ở những sự kiện `P_0` KHÔNG hỏng, để định lượng bẫy.
- Nếu (i) < 80% khớp trong ±1% ⇒ **fail closed**, module A hạ descriptive-only và nói rõ vì sao.

### 4.2 Module A — outcomes

| | tên | định nghĩa | vai trò |
|---|---|---|---|
| A-P | `AR_ex` | `C_0/C_{−1} − 1` − `VNI_0/VNI_{−1} − 1` | **primary A** |
| A-S1 | `DR` | `(P_{−1} − P̂_0) / D` (drop ratio) | phụ |
| A-S2 | `AVOL_0` | `Vol_0 / mean(Vol_{−60..−6}) − 1` | phụ |
| A-S3 | `AVOL_{1..5}` | như trên, trung bình T+1..T+5 | phụ |

`VNI` = `Close` của `ticker = 'VNINDEX'` trong `tav2_bq.ticker`, lấy theo **ngày lịch** của chính
phiên T−1/T+0 của cổ phiếu (xử lý đúng trường hợp cổ phiếu nghỉ giao dịch lệch thị trường).

**Module A được tuyên bố DESCRIPTIVE / MICROSTRUCTURE, không bao giờ là ALPHA** — vì giá tham
chiếu ex-date do sở ấn định, không phải kết quả khám phá giá.

### 4.3 Module B — outcomes

**Benchmark chính:** danh mục **equal-weighted `universe_pit`**, đo trên **cùng cơ sở `Close` hồi
tố**. Lý do khai báo trước: VNINDEX là chỉ số **giá** còn `Close` của cổ phiếu là chuỗi **đã cộng
lại cổ tức** ⇒ so hai cơ sở khác nhau tạo thiên lệch dương hệ thống. Benchmark EW cùng cơ sở khử
thiên lệch đó. `EW_ret(d)` = trung bình `C_i(d)/C_i(d_prev) − 1` trên các mã `in_universe = TRUE`
tại cả `d` và `d_prev`.

| | tên | định nghĩa | vai trò |
|---|---|---|---|
| **B-P** | **`BHAR_20`** | `C_{+20}/C_0 − 1` **trừ** lợi suất tích luỹ EW-universe trên **cùng khoảng ngày lịch** | **PRIMARY DUY NHẤT của Sprint 2** |
| B-S1 | `BHAR_5`, `BHAR_10`, `BHAR_60` | như trên, h = 5/10/60 | phụ (họ 4 horizon) |
| B-S2 | `BHAR_20^VNI` | benchmark đổi sang VNINDEX | phụ |
| B-S3 | contrast bin | bin tỉ suất cao nhất − thấp nhất, trên `BHAR_20` | phụ |
| B-S4 | `BHAR_20` trên P-WIDE | population thay thế | phụ |

**Cửa sổ bắt đầu tại GIÁ ĐÓNG CỬA phiên ex-date (T+0)**, không phải T+1 — vì giá tham chiếu đã
được áp từ đầu phiên ex-date, nên T+0 là thời điểm sớm nhất một nhà đầu tư *thực sự có thể* hành
động trên thông tin "đã đi ex". Chọn cố định, không thử cả hai rồi chọn.

---

## 5. Heterogeneity — bin tỉ suất CỐ ĐỊNH

`y = div_total_on_exdate / P_{−1}` (**GỘP**, trước thuế TNCN 5%).

| bin | khoảng |
|---|---|
| Y1 | [0 %, 2 %) |
| Y2 | [2 %, 4 %) |
| Y3 | [4 %, 6 %) |
| Y4 | [6 %, 10 %) |
| Y5 | [10 %, 50 %] |

5 bin, chốt trước, **không tái phân bin theo kết quả**. (Neo vào Sprint 1: p50 yield 4,40%,
p99 18,13% ⇒ bin phủ đúng phân bố thật.)

**IS / OOS:** IS = `exright_date` 2014-01-01…2019-12-31 · OOS = 2020-01-01…2026-06-30.
Chuẩn fleet (`coding_guidelines` §18 / `kb/KNOWLEDGE.md`). Edge rớt OOS = **loại**.

---

## 6. Model & inference

1. **Effect size + CI trước, p-value sau.** Mọi con số chính đi kèm CI 95%.
2. **CI chính = stationary block bootstrap** trên **tháng lịch của ex-date** (block = 1 tháng,
   10.000 lần resample, seed cố định `20260815`). Lý do: cổ tức VN dồn cục theo mùa ⇒ các sự
   kiện cùng tháng tương quan chéo mạnh; bootstrap theo sự kiện độc lập sẽ cho CI hẹp giả.
3. **Kiểm chứng chéo bằng hồi quy** OLS `BHAR_20 ~ y + log(ADV60) + mom_6m_skip1m + rvol_60d
   + log(mcap_PIT) + ey(1/PE) + PB + FE(ICB lv1) + FE(năm)`, sai số chuẩn **cluster hai chiều
   theo `ticker` và theo `tháng ex-date`**.
   - `mcap_PIT` = `P_{−1} × OShares` với `OShares` từ `ticker_financial` ở quý **mới nhất có
     `Release_Date ≤ T−1`**. Nếu coverage < 80% ⇒ **bỏ biến size**, dùng `log(ADV60)` một mình,
     và ghi vào `SPRINT2_DEVIATIONS.md`.
   - **Cấm** kéo bất kỳ trường restated / forward-looking nào (`profit_*`, `_center_*`, mọi cột
     đo sau ex-date) vào mô hình chỉ để R² đẹp.
   - `ICB_Code` là phân ngành **hiện tại** ⇒ look-ahead nhẹ, phải công bố; chỉ dùng làm FE, không
     làm biến kết luận.
4. **Luôn báo median + p10/p25/p50/p75/p90 + tỉ lệ > 0**, không chỉ mean. Một mean dương do đuôi
   thì không phải edge dùng được.
5. **N khai báo theo SỰ KIỆN ĐỘC LẬP và SỐ MÃ ĐỘC LẬP**, không theo số dòng (Sprint 1 C7).

### 6.1 Số trials khai báo trước

| họ | trials |
|---|---:|
| B-primary `BHAR_20` | 1 |
| horizon phụ 5/10/60 | 3 |
| benchmark thay thế (VNINDEX) | 1 |
| 5 bin tỉ suất | 5 |
| contrast bin cao−thấp | 1 |
| IS / OOS | 2 |
| population P-WIDE | 1 |
| robustness §7 (6 lát) | 6 |
| **Tổng khai báo** | **20** |

- Họ **primary** = 4 horizon ⇒ ngưỡng Bonferroni cho B-P: **p < 0,0125**.
- Mọi phát hiện phụ phải sống sót **Holm** trên toàn bộ 20 trials mới được gọi là phát hiện.
- Chạy thêm trial ngoài danh sách này ⇒ **bắt buộc** ghi `SPRINT2_DEVIATIONS.md` và tính lại
  hiệu chỉnh.
- Không tính DSR/PBO ở sprint này vì **không có chiến lược nào được chọn từ một họ cấu hình** —
  đây là estimation, không phải selection. Nếu Sprint 2 kết thúc ở ALPHA CANDIDATE thì DSR/PBO là
  **cổng bắt buộc của sprint sau**, trước bất kỳ đề xuất wire nào.

---

## 7. Robustness bắt buộc (6 lát, đã tính vào 20 trials)

| # | lát | mục đích |
|---|---|---|
| R1 | IS 2014-2019 vs OOS 2020+ | edge có bền không |
| R2 | ADV60 trên/dưới trung vị · (mcap trên/dưới trung vị nếu coverage đủ) | có phải hiện vật thanh khoản/size |
| R3 | Loại 1% ngoại lai hai đuôi `BHAR_20` (winsorise + trimmed mean) | có phải do vài ca |
| R4 | Dung sai nhiễm thay thế `W_h = 5` | kết luận có nhạy với quy tắc loại không |
| R5 | **Placebo**: neo giả vào `ex − 40` phiên trên **chính các mã đó**, cùng toàn bộ pipeline | pipeline có tự sinh hiệu ứng không |
| R6 | **Pre-trend**: `BHAR_{−20→−1}` trước ex-date | hiệu ứng có bắt đầu từ trước không |
| — | **Per-year leave-one-out** trên `BHAR_20` | 1-2 năm có gánh hết edge không (bắt buộc, coi là 1 phần của R1) |

**Không cắt lát ngành × regime × năm** — N ≈ 3.000 trên 13 năm không đủ; cắt là bịa độ chính xác.
DT5G regime chỉ được dùng làm **mô tả** (phân bố sự kiện theo state), không làm lát thống kê.

Sàn N cho mọi lát: **N ≥ 200 sự kiện và ≥ 60 mã độc lập**, nếu không thì báo "N không đủ" thay vì
báo một con số.

---

## 8. Tradability — chỉ ở mức SCREENING

Không tối ưu chiến lược, không quét tham số, không sizing. Một phép trừ duy nhất, khai báo trước:

```
BHAR_net = BHAR_20  −  0,05 × y  −  0,002  −  0,003
                        thuế TNCN   phí 2 chiều   spread/slippage
                        5% cổ tức   (0,1%×2)      giả định 30bps khứ hồi
```

Cơ sở: `CLAUDE.md` §Backtest (TC 0,1%/chiều) · thuế cổ tức cá nhân 5% (số của `div_total_on_exdate`
là **GỘP**) · 30bps slippage là giả định thận trọng cho mã trong `universe_pit`, **không** hiệu
chỉnh theo kết quả.

⚠️ Tách bạch tuyệt đối trong báo cáo: **microstructure/descriptive** (module A, và mọi thứ đo
quanh mức giá do sở ấn định) **KHÔNG BAO GIỜ** được gọi là ALPHA.

---

## 9. Tiêu chí thành công / thất bại — CHỐT TRƯỚC

**ALPHA CANDIDATE** — phải đạt **TẤT CẢ**:
- (a) `BHAR_20` mean ≥ **+0,75%** với CI 95% block-bootstrap **không chứa 0**, và p < 0,0125
  (Bonferroni họ 4 horizon);
- (b) **cùng dấu ở CẢ IS và OOS**, độ lớn OOS ≥ ½ độ lớn IS, và **CI của OOS không chứa 0**;
- (c) `BHAR_net` (§8) vẫn > 0;
- (d) **median `BHAR_20` > 0** (không phải hiệu ứng đuôi);
- (e) per-year leave-one-out: **không năm nào gánh > 50%** tổng hiệu ứng;
- (f) placebo R5 **không** cho hiệu ứng cùng cỡ, và pre-trend R6 không giải thích được hiệu ứng.

**RISK / DUE-DILIGENCE** — hiệu ứng phát hiện được nhưng trượt (c), (d), (e) hoặc (f); hoặc hiệu
ứng **âm** (⇒ giữ qua ex-date là một chi phí phải biết khi lập plan, không phải cơ hội).

**DESCRIPTIVE ONLY** — còn lại, và **mặc định cho toàn bộ Module A**.

Không có nhánh nào ở trên dẫn tới "wire". Wire cần một sprint riêng với DSR/PBO + quant-skeptic +
user duyệt (`coding_guidelines` §18, `kb/KNOWLEDGE.md` §Quy chuẩn 5).

---

## 10. Deliverables

`SPRINT2_PREREG.md` (file này, commit riêng trước outcome) · `sprint2_build.py` ·
`sprint2_analyze.py` · `selfcheck_sprint2.py` · `SPRINT2_CASH_DIVIDEND.md` ·
`SPRINT2_DEVIATIONS.md` · `out2/*.csv` + `out2/*.json` + `out2/sql/*.sql` · plot khi cần.

Mọi lỗi đo của chính Sprint 2 → `SPRINT2_DEVIATIONS.md` (hoặc bổ sung `ISSUES_LEDGER.md`).
**Kết quả null / refuted được giữ nguyên trong báo cáo**, không cắt bỏ.
