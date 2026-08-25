# Early-recovery margin lever trên main book V2.4 — f = 1,1 / 1,2 / 1,3

> Job `Taylor_20260825_125936` · 2026-08-25 · **RESEARCH-ONLY. KHÔNG wire, KHÔNG sửa
> `trading_rules.json`, KHÔNG đổi code production.**
> Câu hỏi (Mike): sau khủng hoảng, khi DT5G đã xác nhận thoát đáy + định giá còn rẻ + episode được
> Bobby xếp Loại-2 — nhân toàn bộ position sizing của main book V2.4 lên ×f trong cửa sổ đó tốt hơn
> hay tệ hơn base?

## VERDICT: **NO-GO cho lever điều-kiện-hoá-theo-early-recovery.**

Ba lý do độc lập, mỗi lý do tự nó đủ để dừng:

1. **N thật = 2 episode vĩ mô độc lập, và ~94% toàn bộ hiệu ứng đến từ MỘT episode (COVID
   2020).** Leave-one-out: bỏ COVID ⇒ ΔCAGR ở f=1,3 rơi từ **+3,26pp xuống +0,20pp**.
2. **KHÔNG có một phiên nào trong mẫu IS (2014-2019).** Mọi cửa sổ đều nằm ở 2020+ ⇒
   walk-forward IS/OOS — điều kiện bắt buộc của quy chuẩn backtest fleet — **không thể thực hiện
   được về mặt cấu trúc**, không phải "chưa làm".
3. **Chân đối chứng vô-điều-kiện ĐÁNH BẠI cửa sổ.** Lever y hệt f=1,3 áp cho **MỌI phiên
   không-CRISIS/BEAR** cho CAGR **+8,97pp** với **Calmar 1,66 TỐT HƠN base (1,62)**, trong khi cửa
   sổ early-recovery chỉ cho +3,26pp / Calmar 1,62. Và sau khi bỏ COVID, cửa sổ còn **kém hiệu quả
   hơn** chân vô điều kiện tính trên mỗi phiên active (0,130 vs 0,378 pp/100 phiên). ⇒ **Việc điều
   kiện hoá theo "early recovery" không tạo ra edge nào** — thứ tạo ra số đẹp là một sự thật khác
   hẳn, xem ngay dưới.

**Phát hiện có giá trị nhất của job này KHÔNG phải câu trả lời về margin, mà là điều kiện tiên
quyết mà câu hỏi giả định sai:**

> **V2.4 R3 hiện KHÔNG hề dùng đòn bẩy ở bất kỳ đâu, và gross exposure trung bình chỉ 0,604 —
> tối đa toàn mẫu 0,942.** Ở f=1,3 trong cửa sổ, số vốn thực sự phải VAY tối đa chỉ **14,8% NAV**
> (148tr trên NAV 1 tỷ) và chỉ **118/279 phiên** có vay đồng nào. Độ nhạy lãi vay 8%→15%/năm làm
> đổi CAGR đúng **0,05pp**. ⇒ Đây **không phải câu hỏi về margin**. Đây là câu hỏi *"vì sao book
> chạy ở 60% vốn?"* — một câu hỏi khác, lớn hơn, và chưa được trả lời.

---

## 0. Nguồn dữ liệu + self-check control leg

Tra `mike/kb/data_registry/index.md` trước khi chọn nguồn (§9 coding_guidelines). Nguồn dùng:

| Nguồn | Status | Dùng làm gì |
|---|---|---|
| `tav2_bq.vnindex_5state_dt5g_live` (+ mirror `data/vnindex_5state_dt5g_live.csv`) | CANONICAL | DT5G state/transition. **KHÔNG** dùng `vnindex_5state` (v3.4b BASE — bẫy đã ghi). |
| `data/v23_..._advprice_exp_repin0803_price_univpit.csv` | CSV pin R3 08-03 (registry §"2026-08-03 — ⭐ RE-PIN R3…") | 3.107 dòng `DAILY`: NAV, gross, state, VNINDEX. |
| `kb/data_registry/market-state/vn_macro_regime_history.md` | CANONICAL | Phân loại Bobby **BLIND to forward-return**. KHÔNG tự phân loại lại. |
| `data/value_radar_series.csv` + `value_radar.py` | CANONICAL, **DISPLAY-ONLY** | Nhãn định giá. ⚠️ xem cảnh báo §6.3. |
| `pt_v23_audit_2014.py` (đọc, không chạy) | production | Xác minh `SB_GATE` — xem §4. |

Không query BQ nặng: chỉ 1 query transition DT5G (đối soát mirror local, khớp).

### Self-check control leg — **PASS TUYỆT ĐỐI**
Recompute độc lập từ CSV pin (không dùng số in sẵn):

| | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 14-19 | OOS 20+ |
|---|---|---|---|---|---|---|---|
| Số pin registry | 28,86% | 1,90 | −17,8% | 1,62 | 1.178,01B | 27,09% | 30,48% |
| **Recompute job này** | **28,8627%** | **1,8999** | **−17,7851%** | **1,6229** | **1.178,0099B** | **27,09%** | **30,48%** |

⇒ harness hợp lệ, mọi Δ dưới đây là chênh lệch thật của đúng biến được đổi.

### Phương pháp mô phỏng — khai báo rõ vì nó là giới hạn lớn nhất
Đây là **overlay ở tầng NAV**, KHÔNG phải chạy lại engine:

```
r_lev(t) = f·r_base(t) − borrow(t)·i/252 − TC·|Δf|·g(t−1)
borrow(t) = max(0, f·g(t−1) − 1)          [quy ước "vay thật"]
          hoặc (f−1) khi cửa sổ mở         [quy ước dispatch, "vay phẳng"]
```
Chính xác về mặt toán học khi scale MỌI vị thế theo tỷ lệ và tiền nhàn rỗi lãi 0% (đúng quy ước
CLAUDE.md): `r_base(t) = g(t)·(return tài sản)` ⇒ nhân sizing ×f cho `f·r_base(t)`, và TC cũng
được scale đúng ×f vì nó đã nằm trong `r_base`. `i = 10%/năm`, `TC = 0,1%/chiều` (CLAUDE.md).
Tín hiệu tính trên dữ liệu **≤ t−2**, lever áp cho return ngày t ⇒ **trễ 1 phiên thực thi**, khớp
quy ước T+1 của engine. Độ nhạy lag 0/1/2/3/5 phiên: CAGR 32,11/32,12/32,20/32,11/32,21 — không
phụ thuộc lag.

**Overlay KHÔNG mô hình hoá** (phải mang theo khi đọc mọi con số): (a) capacity — ×1,3 ở NAV 50B
với cap 10%/mã + trần ADV; (b) mã nào thực sự được cấp margin ở DNSE; (c) đường margin-call
path-dependent; (d) ramp 3 phiên của engine. Vì vậy mọi số CAGR dưới đây là **cận trên lạc quan**.

---

## Bước 1-2 — Cửa sổ + N episode

### Toàn bộ 14 lần DT5G thoát CRISIS/BEAR → NEUTRAL/BULL (2014→nay), causal

| Exit | Từ→Đến | dd52 tại exit | dd đáy spell | Radar | PE pct 10Y | Bobby Loại-2? | Qua cổng? |
|---|---|---|---|---|---|---|---|
| 2014-06-09 | CRISIS→NEUTRAL | −6,9% | −15,4% | 48,0 | 74,7 | không | — |
| 2015-05-05 | BEAR→NEUTRAL | −13,7% | −14,9% | 35,8 | 62,8 | không | — |
| 2016-01-05 | BEAR→NEUTRAL | −10,8% | −11,7% | 27,0 | 46,1 | không | — |
| 2017-01-04 | CRISIS→NEUTRAL | −2,1% | −3,5% | 81,1 | 94,3 | không | — |
| 2018-06-21 | CRISIS→NEUTRAL | −19,5% | −22,6% | **90,7 ĐẮT** | 96,7 | **có** (ambiguous) | ✗ định giá |
| 2018-12-07 | BEAR→NEUTRAL | −20,4% | −23,8% | **81,6 ĐẮT** | 89,6 | **có** | ✗ định giá |
| 2019-06-04 | CRISIS→NEUTRAL | −8,5% | −15,5% | 75,7 | 82,7 | không | — |
| 2020-01-14 | BEAR→NEUTRAL | −5,7% | −7,4% | 62,3 | 71,6 | không | — |
| **2020-05-27** | CRISIS→NEUTRAL | −16,3% | **−35,7%** | 48,8 TRUNG TÍNH | 56,4 | **có** (clean) | **✓** |
| **2020-07-17** | BEAR→NEUTRAL | −14,9% | −17,8% | 47,0 TRUNG TÍNH | 58,7 | **có** | **✓** (cùng episode) |
| **2022-08-17** | BEAR→NEUTRAL | −16,6% | −23,4% | 28,9 RẺ | 22,7 | **có** (clean) | **✓** |
| **2023-04-12** | BEAR→NEUTRAL | −27,6% | **−40,3%** | 12,9 RẺ | 5,1 | **có** | **✓** (cùng episode SCB) |
| 2023-11-30 | CRISIS→NEUTRAL | −12,2% | −17,4% | 7,3 RẺ | 13,7 | không | — |
| 2024-08-30 | CRISIS→NEUTRAL | −1,4% | −7,9% | 32,5 RẺ | 45,6 | không | — |

**Cổng Bobby có bị hindsight không? — KHÔNG, và tôi kiểm được điều đó bằng máy.** Lo ngại chính
đáng: Bobby phân loại năm 2026, blind với forward-return nhưng KHÔNG blind với việc *episode nào
đáng được đặt tên*. Nên tôi dựng **proxy cơ học thuần PIT** thay cho cổng Bobby: `dd đáy spell
≤ −20%` (đo được tại T chỉ bằng dữ liệu quá khứ) + cùng cổng định giá. Kết quả: proxy chọn ra
**đúng cùng một tập** {2020-05-27, 2022-08-17, 2023-04-12}. ⇒ cổng Bobby ở kỷ nguyên DT5G **có
thể thay bằng một luật cơ học triển khai live được**, không phải tri thức hồi tố.

### DECLARE N
- **4 exit** qua cổng, nhưng gộp theo episode vĩ mô của Bobby: **2020-05-27 + 2020-07-17 = 1
  episode (COVID)**; **2022-08-17 + 2023-04-12 = 1 episode (SCB/Fed)**.
- ⇒ **N = 2 episode vĩ mô độc lập.** (2018 là episode Loại-2 thứ ba nhưng **bị cổng định giá loại**
  — radar 90,7/81,6 = ĐẮT. Bobby vốn đã cho nó N_eff 0,5 "ambiguous severity".)
- Sổ Bobby ghi N_effective toàn lịch sử ~3,5, nhưng **kỷ nguyên DT5G (2014+) chỉ còn ~2,5, và sau
  cổng định giá còn 2**.
- **N = 2 ⇒ đây là forensic mô tả, KHÔNG PHẢI kiểm định thống kê.** DSR/PBO **không áp dụng** (N<5,
  không đủ power; và không có họ cấu hình nào được *chọn* qua grid — tôi chạy 4 mức f + 3 bộ
  episode + 1 biến thể cổng, `N_trials` nhỏ nhưng ĐỦ để mọi "số đẹp nhất" ở đây phải đọc như
  in-sample).

### Cửa sổ thực tế NGẮN hơn nhiều so với giả định "chu kỳ NEUTRAL→BULL kéo dài"

| Cửa sổ | Mở | Đóng | Số ngày lịch | Lý do đóng |
|---|---|---|---|---|
| COVID-1 | 2020-05-27 | 2020-07-01 | 35 | **DT5G quay lại BEAR** |
| COVID-2 | 2020-07-17 | 2020-12-07 | 143 | **Radar chuyển ĐẮT** |
| SCB-1 | 2022-08-17 | 2022-09-19 | 33 | **DT5G quay lại BEAR** |
| SCB-2 | 2023-04-12 | 2023-10-23 | 194 | **DT5G quay lại CRISIS** |

**Trần 18 tháng KHÔNG BAO GIỜ ràng buộc** (kiểm cả 6/12/18/24/36 tháng — chỉ trần 6 tháng mới cắn,
một lần). Đời sống cửa sổ trung vị ≈ **4 tháng**, không phải 18. Tiền đề "chu kỳ NEUTRAL→BULL kéo
dài, rủi ro đã xả" **bị chính dữ liệu bác**: 3/4 cửa sổ chết vì DT5G whipsaw ngược về BEAR/CRISIS.

---

## Bước 3 — Kết quả f = 1,0 / 1,1 / 1,2 / 1,3

### 3.1 Bộ A — đúng chữ dispatch (Bobby Loại-2 + radar ≤67), 279 phiên active (9,0% mẫu)

| f | CAGR | Δ | Sharpe | MaxDD | Calmar | Final NAV | Vay tối đa | Phiên có vay |
|---|---|---|---|---|---|---|---|---|
| **1,0 (base)** | 28,86% | — | **1,90** | **−17,8%** | **1,62** | 1.178,0B | 0 | 0 |
| 1,1 | 29,17% | +0,31 | 1,90 | −18,1% | 1,61 | 1.213,8B | 0,0% | 0 |
| 1,2 | 29,48% | +0,62 | 1,89 | −19,0% | 1,55 | 1.249,8B | 6,0% NAV | 47 |
| **1,3** | **29,75%** | **+0,89** | 1,88 | **−19,9%** | **1,50** | 1.283,7B | 14,8% NAV | 118 |

**Đọc: CAGR tăng, RỦI RO ĐIỀU CHỈNH GIẢM.** Calmar 1,62 → 1,50 (−7,4%), Sharpe 1,90 → 1,88,
MaxDD xấu đi 2,1pp. Ở quy ước lãi vay "phẳng" của dispatch ((f−1)×NAV×10%) còn tệ hơn: f=1,3 cho
CAGR 29,44 / Calmar 1,46.

### 3.2 MaxDD xấu đi ở ĐÂU — cơ chế cụ thể, không phải trung bình

MaxDD base −17,79% xảy ra **2018-07-05** (đỉnh 2018-04-05) — **nằm NGOÀI mọi cửa sổ**. Drawdown
sâu thứ nhì là **−17,22% ngày 2020-07-27** — **nằm TRONG cửa sổ COVID-2, đúng 10 ngày sau khi cửa
sổ mở (2020-07-17)**. Nhân ×1,3 đẩy nó vượt mốc 2018 ⇒ MaxDD mới −19,9%.

Đó là làn sóng COVID thứ hai (ổ dịch Đà Nẵng cuối 7/2020). **Cửa sổ mở ra ngay trước một cú sụt
mạnh.** Đây không phải xui — nó là chính xác cái rủi ro mà "DT5G đã xác nhận thoát đáy ⇒ rủi ro đã
xả" bỏ qua: DT5G cam kết 10 phiên để RA khỏi CRISIS/BEAR (bất đối xứng có chủ đích), nên điểm nó
xác nhận thoát vẫn nằm sâu trong vùng còn biến động cao.

### 3.3 Per-episode breakdown (interest = vay thật)

| f | Episode | Phiên | Return base trong cửa sổ | Return levered | Δ | DD trong cửa sổ (base→lev) |
|---|---|---|---|---|---|---|
| 1,3 | **2020 COVID** | 125 | +26,88% | +35,68% | **+8,80pp** | −13,0% → −17,0% |
| 1,3 | 2022 SCB leg-1 | 21 | **−6,08%** | **−7,91%** | **−1,83pp** | −7,3% → −9,4% |
| 1,3 | 2023 SCB leg-2 | 133 | +15,51% | +20,08% | +4,56pp | −11,4% → −14,7% |

**1/3 chân là chân THUA.** Cửa sổ SCB-1 mở 2022-08-17 rồi chết 33 ngày sau khi DT5G quay lại BEAR
— trong 21 phiên đó thị trường mất 6,08%, và lever biến nó thành −7,91%.

### 3.4 Leave-one-out — chỗ giả thuyết gãy

Bộ A, f=1,3, so với base 28,86%:

| Bỏ | CAGR | ΔCAGR vs base | Calmar |
|---|---|---|---|
| (không bỏ gì) | 29,75% | **+0,89pp** | 1,50 |
| bỏ **2020 COVID** | 29,06% | **+0,20pp** | 1,63 |
| bỏ 2022 SCB leg-1 | 29,96% | +1,10pp *(TỐT LÊN khi bỏ)* | 1,51 |
| bỏ 2023 SCB leg-2 | 29,35% | +0,49pp | 1,48 |

⇒ **77% hiệu ứng nằm ở COVID**; bỏ nó đi thì Δ còn +0,20pp — nhỏ hơn cả sai số vintage dữ liệu của
chính con số pin R3. **LOO không đạt.** (Ở biến thể mạnh nhất §3.6, tỷ lệ này còn cực đoan hơn:
**94%**.)

### 3.5 Self-check quy mô vốn vay (đúng yêu cầu dispatch)

Ở f=1,3, quy chiếu NAV 1 tỷ VND: **vay tối đa 148tr** (14,8% NAV), lãi tối đa **~14,8tr/năm**, và
chỉ **118/279 phiên** có vay > 0. Con số dispatch nêu (vay 300tr, lãi 30tr) là **quy ước "vay
phẳng"** — nó giả định luôn vay đủ (f−1)×NAV, trong khi thực tế book chỉ đầu tư 60-72% vốn nên
×1,3 phần lớn chỉ là **triển khai tiền nhàn rỗi**, không vay. Bằng chứng quyết định: đổi lãi vay
**8% → 15%/năm chỉ làm CAGR đổi 0,05pp** (32,13 → 32,08). Một "chiến lược margin" mà độ nhạy với
lãi vay ≈ 0 thì nó không phải chiến lược margin.

### 3.6 Biến thể D — bỏ cổng định giá (phát hiện ngoài kế hoạch, phải khai)

Cổng định giá đóng cửa sổ COVID-2 vào **2020-12-07** vì radar chuyển ĐẮT — tức nó **cắt đúng phần
mạnh nhất của sóng hồi phục 2021**. Thử bỏ cổng đó (cửa sổ chỉ đóng khi DT5G về BEAR/CRISIS hoặc
trần 18 tháng), 543 phiên active:

| f | CAGR | Δ | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|
| 1,2 | 31,06% | +2,20 | 1,93 | −19,0% | 1,64 |
| **1,3** | **32,12%** | **+3,26** | **1,93** | −19,9% | **1,62** |

Đây là cấu hình *duy nhất* không làm xấu risk-adjusted (Sharpe 1,93 > 1,90; Calmar 1,62 = base).
**Nhưng nó chết ở LOO nặng hơn:** bỏ COVID ⇒ CAGR 29,06%, **Δ chỉ còn +0,20pp** = **93,9% hiệu ứng
đến từ một episode**. Và nó là kết quả tìm được **sau khi đã nhìn số** của bộ A ⇒ in-sample, không
được đọc như bằng chứng.

*(Bootstrap khối 63 phiên B=2.000 cho biến D ra 90% CI [+0,97; +4,68]pp, P(Δ≤0)=0,1% — **tôi KHÔNG
dùng con số này làm bằng chứng và khuyến nghị không ai trích nó**. Nó coi ~49 khối là độc lập trong
khi N thật = 2 episode; đây đúng lỗi "N là số dòng, không phải số sự kiện độc lập" mà skill
`quant-research` cấm. LOO mới là phép kiểm đúng ở đây, và LOO trượt.)*

### 3.7 Walk-forward — **KHÔNG THỰC HIỆN ĐƯỢC**

| Bộ | Phiên active IS (2014-2019) | Phiên active OOS (2020+) |
|---|---|---|
| A | **0** | 279 |
| D | **0** | 543 |

Không có một phiên IS nào. Quy chuẩn fleet ("walk-forward IS/OOS, edge rớt OOS = loại") **không
áp dụng được về mặt cấu trúc**. Đây không phải thiếu sót có thể bù bằng chạy thêm — DT5G chỉ có
data từ 2014, và trong 2014-2019 chỉ có đúng episode 2018, mà 2018 bị cổng định giá loại.

---

## Bước 4 — EX-BULL vs early-recovery

### ⚠️ Đính chính tiền đề dispatch: **hệ hiện tại KHÔNG cho 130% ở EX-BULL**

Dispatch viết "Hệ hiện tại cho 130% ở EX-BULL". Kiểm bằng code, không suy đoán:

- `pt_v23_audit_2014.py:74` — `SB_GATE = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.0}` với comment
  nguyên văn **`# single-book DT5G exposure (no EXBULL leverage)`**.
- `pt_v23_audit_2014.py:458` — `MGE` (gross cap) **mặc định `0` = OFF**, và comment `:462` ghi
  kết quả audit trước: *"combined gross maxed 0.995@1.3 / 0.966@1.5, borrow ~0 VND"*.
- Đo thực tế trên CSV pin: **gross tối đa toàn mẫu 0,942**; theo state:

| DT5G state | Phiên | Gross TB | Gross trung vị | Gross max |
|---|---|---|---|---|
| 1 CRISIS | 489 | 0,344 | 0,407 | 0,936 |
| 2 BEAR | 241 | 0,195 | 0,142 | 0,672 |
| 3 NEUTRAL | 1.895 | **0,722** | 0,716 | 0,939 |
| 4 BULL | 422 | **0,607** | 0,467 | 0,942 |
| 5 EX-BULL | 60 | **0,622** | 0,500 | 0,920 |

**"130% EX-BULL" là ngữ nghĩa của thang trạng thái DT5G trong tài liệu, KHÔNG phải hành vi của
book V2.4.** Book chưa bao giờ vượt 100% gross. Nên "bỏ lever EX-BULL" là **no-op** — không có gì
để bỏ. Câu so sánh Bước 4 vì vậy là *giả định vs giả định*, và tôi trình bày nó đúng như vậy.

### So sánh (tất cả f=1,3, lãi vay thật, đều là GIẢ ĐỊNH chưa tồn tại)

| Cấu hình | Phiên active | CAGR | Δ | Sharpe | MaxDD | Calmar | pp/100 phiên active |
|---|---|---|---|---|---|---|---|
| **BASE R3** | 0 | 28,86% | — | **1,90** | **−17,8%** | 1,62 | — |
| **chỉ EX-BULL** | 60 | 29,22% | +0,36 | **1,90** | **−17,8%** | **1,64** | **0,600** |
| A. early-recovery + cổng định giá | 279 | 29,75% | +0,89 | 1,88 | −19,9% | 1,50 | 0,319 |
| D. early-recovery, bỏ cổng định giá | 543 | 32,12% | +3,26 | 1,93 | −19,9% | 1,62 | 0,600 |
| D + EX-BULL (cộng dồn?) | 570 | 32,11% | +3,25 | 1,93 | −19,9% | 1,62 | — |

**Trả lời Bước 4: đánh đổi "bỏ lever EX-BULL để lấy lever early-recovery" là một trao đổi TỆ.**
Lever chỉ ở EX-BULL (60 phiên) cho **+0,36pp mà KHÔNG làm xấu MaxDD một chút nào (−17,8% giữ
nguyên) và Calmar TỐT LÊN (1,64)**. Cửa sổ early-recovery cần 279-543 phiên phơi nhiễm để đổi lấy
2,1pp MaxDD xấu đi. Và **hai thứ không cộng dồn** (32,11 ≈ 32,12) vì EX-BULL nằm gọn trong cửa sổ D.

Nhưng lưu ý ngay: +0,36pp trên 60 phiên trong 12,5 năm cũng là hiệu ứng **quá nhỏ và N quá bé**
(EX-BULL xuất hiện 2 lần: cuối 2020/đầu 2021 và 8-9/2025) để đề xuất bất kỳ điều gì. **Tôi KHÔNG
đề xuất lever EX-BULL** — chỉ trả lời so sánh được hỏi.

---

## Bước 5 (thực chất là §3.8) — CHÂN ĐỐI CHỨNG dispatch không hỏi, nhưng quyết định câu trả lời

Nếu điều kiện hoá theo early-recovery có giá trị, nó phải **đánh bại lever không điều kiện hoá**.
Đây là chân đối chứng duy nhất tách được *"edge của CỬA SỔ"* khỏi *"edge của việc triển khai tiền
nhàn rỗi"*. Tất cả f=1,3, lãi vay thật:

| Cấu hình | Phiên | CAGR | Δ | Sharpe | MaxDD | Calmar | pp/100 phiên |
|---|---|---|---|---|---|---|---|
| BASE R3 | 0 | 28,86% | — | 1,90 | −17,8% | 1,62 | — |
| A. early-recovery + định giá | 279 | 29,75% | +0,89 | 1,88 | −19,9% | 1,50 | 0,319 |
| D. early-recovery bỏ định giá | 543 | 32,12% | +3,26 | 1,93 | −19,9% | 1,62 | 0,600 |
| chỉ BULL + EX-BULL | 482 | 31,13% | +2,27 | 1,91 | −20,0% | 1,55 | 0,471 |
| **E. MỌI phiên NEUTRAL** | 1.893 | **35,37%** | **+6,51** | 1,88 | −20,7% | **1,71** | 0,344 |
| **F. MỌI phiên không-CRISIS/BEAR** | 2.375 | **37,83%** | **+8,97** | **1,91** | −22,8% | **1,66** | 0,378 |

**Đọc bảng này là toàn bộ verdict:**
1. Lever **vô điều kiện** (F) cho **+8,97pp với Sharpe 1,91 ≈ base và Calmar 1,66 > base 1,62** —
   tức tốt hơn cửa sổ early-recovery ở **mọi chiều**, kể cả rủi ro điều chỉnh.
2. Cửa sổ D có hiệu suất/phiên cao hơn (0,600 vs 0,378) — **nhưng toàn bộ chênh lệch đó là COVID**.
   Bỏ COVID: D còn +0,20pp trên 154 phiên = **0,130 pp/100 phiên, KÉM HƠN chân vô điều kiện 0,378**.
   ⇒ **Sau khi khử một episode, việc điều kiện hoá theo early-recovery làm giảm hiệu quả chứ không tăng.**
3. Cổng định giá — thành phần "còn rẻ" mà giả thuyết coi là cốt lõi — **làm hại**: A (có cổng)
   29,75/Calmar 1,50 vs D (bỏ cổng) 32,12/Calmar 1,62. Nó loại đúng episode 2018 (tốt) nhưng cũng
   cắt đúng sóng 2021 (rất tệ). Đây cũng chính là điều Phụ lục C
   (`market_regime_probability_20260729.md`) đã cảnh báo: **0/17 lăng kính Value Radar qua
   BH/Bonferroni, đầu "RẺ" không đơn điệu** — và registry ghi radar là **DISPLAY-ONLY, CẤM wire
   vào quyết định**. Job này vừa đo được lý do định lượng của lệnh cấm đó.

⚠️ **E/F KHÔNG PHẢI khuyến nghị.** Chúng là chân đối chứng chẩn đoán. Chúng cực kỳ in-sample, chạy
bằng overlay (không có capacity/margin-eligibility/margin-call), và — quan trọng nhất — chúng
**đặt cược toàn bộ vào việc DT5G không bỏ sót cú sập kế tiếp**, trong khi KB đã chốt: *"DT5G là
CHỐT RỦI RO FAIL-SAFE, không phải công cụ tăng lợi nhuận; toàn bộ edge ròng đến từ một lần siết
2023."* Anchor DD của base là **~−29% (bootstrap 5th-pct)**, không phải −17,8%; nhân 1,3 lên vùng
**~−38%**. Đó mới là con số phải nhìn khi cân nhắc bất kỳ mức f nào.

---

## Bước 5 (đúng đề) — Observable conditions + escalation

Vì verdict là NO-GO, phần này viết dưới dạng **điều kiện để MỞ LẠI câu hỏi**, không phải checklist
để arm cửa sổ. Đây là thứ có giá trị lâu hơn con số backtest N=2.

### 5.1 Checklist observable (nếu/khi được arm — hiện KHÔNG được arm)

| # | Điều kiện | Chỉ báo cụ thể / nguồn | Ai xác nhận |
|---|---|---|---|
| 1 | DT5G đã COMMIT thoát CRISIS/BEAR | `get_gated_state()` trả `NEUTRAL`/`BULL` **committed** (không phải candidate); `dna_report.build_dt_gate_line()` cho biết đang tích luỹ hay đã chốt | Winston (data-ops) — freshness `macro_health.json` <1440′ |
| 2 | `macro_health` tươi, gate KHÔNG fail-safe về DT4 | `get_gated_state()` không rơi về DT4 | Winston |
| 3 | Episode vừa qua là Loại-2 | `kb/data_registry/market-state/vn_macro_regime_history.md`; **nếu episode chưa có entry ⇒ dispatch macro-strategist (Bobby) với NGÀY + hành động giá, TUYỆT ĐỐI không kèm forward-return/giả thuyết backtest** | Bobby (macro-strategist), blind |
| 3b | Proxy PIT thay thế cổng Bobby | `dd` đáy spell CRISIS/BEAR vừa qua **≤ −20%** so với đỉnh 52 tuần trước spell — tính bằng dữ liệu quá khứ tại T | Taylor (cơ học, kiểm được) |
| 4 | Định giá | Value Radar ≤67 **HOẶC** PE percentile rolling-10Y <50 — ⚠️ **job này đo được cổng này LÀM HẠI** (§3.8 mục 3). Nếu mở lại, mặc định nên là **KHÔNG dùng cổng này** | Taylor |
| 5 | Không có kill-switch/gate đang mở | `data/BOT_STOP` không tồn tại; `trading_rules.json` không có STATUS=DISABLED liên quan | Mafee |
| 6 | Capacity | ×f trên rổ hiện tại còn nằm trong trần ADV 20% + cap 10%/mã — **overlay KHÔNG kiểm điều này**, phải kiểm thật | DollarBill + Mafee |

### 5.2 Escalation — KHÔNG auto, KHÔNG bypass human (giữ nguyên như dispatch yêu cầu)

```
Taylor phát hiện checklist 1-6 đủ
  → append_event Taylor question "early-recovery-window-arm" (kèm số DT5G/dd/radar/capacity)
  → Mike escalate lên user (topic Trading report / Plan approval)
  → USER ARM tường minh: ghi f + ngày hết hạn vào trading_rules.json (user duyệt, §Taylor mandate)
  → DollarBill lập plan với f tương ứng; mọi lệnh vẫn qua gate P0 check_plan_funding() (KHÔNG cộng egg — §25)
  → Mafee thực thi plan-bound
```
Không tầng nào trong chuỗi này được tự động hoá. **Cửa sổ có hạn dùng** — hết hạn tự đóng, muốn
gia hạn phải arm lại.

### 5.3 De-lever — cái gì tự động, cái gì escalate

| Điều kiện | Hành động | Cơ chế |
|---|---|---|
| DT5G về **BEAR hoặc CRISIS** | **DE-LEVER TỰ ĐỘNG về f=1,0**, không hỏi | Đây là cách 3/4 cửa sổ lịch sử thực sự kết thúc — phải là đường tự động, không phải quyết định |
| Trần thời gian hết hạn | DE-LEVER TỰ ĐỘNG | (lịch sử: **chưa bao giờ cắn** — DT5G luôn đóng trước) |
| Radar chuyển ĐẮT | **ESCALATE, không tự de-lever** | Radar là DISPLAY-ONLY (registry) + job này đo được cổng này làm hại ⇒ không được là trigger cơ học |
| Gross thực vượt 1,0 (bắt đầu vay thật) | ESCALATE user trước khi vượt | Lịch sử chỉ 118/279 phiên chạm vay; vượt 1,0 là ngưỡng chất, không phải lượng |
| `macro_health` stale / gate rơi về DT4 | **DE-LEVER TỰ ĐỘNG về f=1,0** (fail-closed) | Cùng tinh thần fail-safe của `get_gated_state()` |

---

## 6. Giới hạn phải mang theo khi trích dẫn job này

1. **N = 2 episode vĩ mô độc lập.** Mọi con số là forensic mô tả. **DSR/PBO không áp dụng** (N<5).
   Bootstrap khối ở §3.6 **KHÔNG hợp lệ ở tầng episode** — tôi để nó trong báo cáo kèm cảnh báo chỉ
   để người sau không phải chạy lại rồi tưởng đã tìm ra bằng chứng.
2. **0 phiên IS.** Walk-forward không thực hiện được — không phải chưa làm.
3. **Overlay tầng NAV, không chạy lại engine.** Không có capacity 50B, không có margin-eligibility
   của DNSE, không có margin-call path, không có ramp 3 phiên. Mọi CAGR là **cận trên lạc quan**.
   Nếu ai muốn biến bất kỳ dòng nào ở đây thành đề xuất wire, **bắt buộc chạy lại engine thật**
   (`pt_v23_audit_2014.py`, `MGE`/`FORCE_REAL_LEVER` đã có sẵn đường code) + self-check 0 VND +
   quant-skeptic — overlay KHÔNG đủ.
4. **Value Radar mang bias không-PIT ở thành phần spread** (bẫy #3 registry: 26 mốc lãi suất neo
   hồi tố 1 lần ngày 2026-06-19). Cột PE percentile trong bảng §1 sạch hơn nhưng vẫn dựa trên
   `tav2_bq.ticker` có điều chỉnh hồi tố. Vì cổng định giá hoá ra **làm hại**, hướng của bias này
   không cứu được kết luận.
5. **Vintage**: CSV pin R3 08-03 dùng snapshot `bq_cache_asof20260729_postrestate`, `AUDIT_END=
   2026-06-19`. Không so số ở đây với số khác vintage.
6. **Anchor DD của base là ~−29% (bootstrap 5th-pct), KHÔNG phải −17,8%.** Mọi MaxDD trong báo cáo
   là realized-path, không phải rủi ro kỳ vọng.

## 7. Việc KHÔNG làm (đúng chỉ đạo)
Không bàn V2.5 leverage (NO-GO vĩnh viễn). Không backtest standalone margin sleeve (Loại-2 crisis
sleeve — việc khác, xem `crisis_margin_framework_adaptive_20260825.md` /
`margin_cap_recovery_forensic_20260825.md`). Không wire, không đụng `trading_rules.json`.

## 8. Câu hỏi ĐÁNG mở tiếp (KHÔNG phải đề xuất — cần user quyết định có mở không)

Job này bác giả thuyết được hỏi, nhưng phơi ra một câu hỏi khác **lớn hơn và chưa ai trả lời**:

> **V2.4 R3 chạy ở gross trung bình 0,604 và chưa bao giờ vượt 0,942.** Trong NEUTRAL — 61% số
> phiên của mẫu — trần là 0,7 và rổ parking custom30V lấp tới 0,72. Trong BULL/EX-BULL, gross còn
> **THẤP HƠN** (0,607/0,622) không phải vì trần rủi ro mà vì **không đủ tín hiệu để lấp book**.

Đây không phải câu hỏi margin — không cần vay đồng nào để đi từ 0,60 lên 0,85. Nó là câu hỏi
**"trần NEUTRAL 0,7 có đúng không"** và **"vì sao book rỗng nhất đúng lúc thị trường tốt nhất"**.
V2.5-leverage NO-GO **không trả lời câu này** (nó test `MGE` với borrow-room CAPIT-only, một cơ chế
khác hẳn). Nếu mở, phải mở như một job engine-thật với walk-forward IS/OOS đầy đủ — điều mà câu hỏi
early-recovery **về mặt cấu trúc không thể có**.

---
### Files
`mike/agents/Taylor/research/early_recovery_margin_lever_20260825/` — `step0_control.py` (self-check
control leg), `step1_windows.py` + `exits.csv` (14 exit + cổng), `step2_sim.py` (overlay 3 bộ × 4 f
× 2 quy ước lãi), `step3_loo_exbull.py` (per-episode + LOO + EX-BULL), `step4_boot.py` (bootstrap +
độ nhạy lag/lãi), `step5_control_uncond.py` (chân đối chứng vô điều kiện), `base_daily.csv`.
