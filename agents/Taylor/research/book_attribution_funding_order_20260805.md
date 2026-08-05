# PARK không chặn BAL/LAG — nó ăn phần dư. Và toàn bộ ưu thế risk-adjusted của V2.4 là ĐA DẠNG HOÁ, không phải alpha của sổ nào

**Job** `Taylor_20260805_163403` · **Ngày** 2026-08-05 · **Tác giả** Taylor
**Trạng thái**: 4/4 câu hỏi trả lời bằng số đo · **quant-skeptic CONFIRMED (confidence high)**, có
recompute độc lập từng con số · **KHÔNG sửa file production nào** (`git diff` rỗng trên
`simulate_holistic_nav.py`, `pt_v22_dt5g.py`, `golive_recommend_v23.py`).
**Đây là câu hỏi HIỂU CƠ CHẾ, không phải đề xuất thay đổi.** Không kết luận gì về wire.

---

## 0. Nguồn dữ liệu & gate tự kiểm

Mọi số dưới đây đo trên **một** file: CSV chân control đã verify
`data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_jit_A_control_univpit.csv`
(**md5 `7d053e6201c9d107685ff4d1dd9d2d2a`** — chính là CSV do lần chạy production sinh ra, đã đối
chiếu ở `park_unpark_live_wiring_20260803.md` §C1).

| Gate | Kết quả |
|---|---|
| Tái lập số pin R3 | `final_nav 1.178,0099B` · **CAGR 28,86% · Sharpe 1,90 · MaxDD −17,8% · Calmar 1,62** ✓ khớp tuyệt đối |
| Self-check dòng tiền | `cash_flow_identity_max_err ≈ 3,8e−5 VND`, `final_nav_identity_err = 0,0` **cả 2 sổ**; `combination_replay_err_vnd = 0,0` |
| Phạm vi | 3.107 phiên, 2014-01-02 → 2026-06-19 (12,46 năm) |
| Công thức chỉ tiêu | copy **nguyên văn** từ `exp_park_jit_20260803/agg_metrics.py:64-73` ⇒ so trực tiếp được với bảng 2×2 §E2 vòng trước |

Script (chỉ ĐỌC): `mike/agents/Taylor/exp_book_attrib_20260805/book_attrib.py` · `funding_order.py`.

**⚠️ Tiền đề dispatch đã lỗi thời:** dispatch ghi *"chân thứ 4 (tắt 4c) CHƯA ĐO"*. **Đã đo rồi** —
phụ lục §E của `park_unpark_live_wiring_20260803.md` (job `Taylor_20260803_180602`) chạy đủ **2×2**
(A/D/C/E). Tôi không chạy lại, chỉ trích lại ở §2.4.

---

## 1. CÂU HỎI 1 — Backtest chạy thực sự thế nào?

### Trả lời thẳng: **KHÔNG. PARK không chiếm 70-80% trước rồi chặn BAL/LAG. PARK nhận phần DƯ.**

Bốn bằng chứng độc lập, xếp theo độ mạnh.

### 1.1 Thứ tự thi hành trong MỘT phiên — park mua ở bước CUỐI

Vòng lặp ngày của `simulate_holistic_nav.py`, đọc theo comment khối:

| Bước | Dòng | Việc | Chiều PARK |
|---|---|---|---|
| 4c | `893` | ETF **PRE-FILL SELL** — chỉ nhả park khi target theo state tụt xuống | **BÁN** |
| 5 | `973` | **Thực thi lệnh mua BAL/LAG đang chờ** — trong đó có JIT bán park nếu thiếu tiền (`1136-1139`) | **BÁN** (theo nhu cầu) |
| 6 | `1310` | Đọc tín hiệu hôm nay → xếp hàng cho T+1 | — |
| 6b | `1347` | ETF **POST-FILL SWEEP** — **đường MUA park DUY NHẤT**, quét tiền còn thừa | **MUA** |
| 7 | `1436` | Ghi NAV | — |

Chính comment trong code (`simulate_holistic_nav.py:895-899`) nói thẳng:

> *"BA-deal-first semantics (user 2026-05-23): ETF is a parking lot for IDLE cash. … Net effect:
> **deals get priority, ETF holds only the remainder**. This block is SELL-only."*

### 1.2 🔴 Bằng chứng cơ học mạnh nhất — sizing lệnh tính trên NAV **ĐÃ GỒM** park

`simulate_holistic_nav.py:1120` và `1129-1132`:

```python
cur_nav = cash + cash_etf_now + cur_pos_mv + pending_mv     # <- cash_etf_now = PARK, nằm TRONG NAV
...
target_value = cur_nav * effective_tw[play_type]            # size lệnh = % của NAV đó
```

⇒ **Park to hay nhỏ KHÔNG làm lệnh BAL/LAG nhỏ đi.** Quy mô lệnh là một tỷ lệ của NAV tổng, mà park
nằm trong NAV. Đây là chỗ giả thuyết "park chiếm chỗ rồi chặn lệnh" chết về mặt cơ học, không cần
số liệu.

### 1.3 Trần 70% là 70% của **QUỸ TIỀN**, không phải của danh mục

`simulate_holistic_nav.py:908-910`: `total_cash_pool = cash + current_etf_value` ;
`target_etf = total_cash_pool * etf_frac`.

Cổ phiếu đã mua **nằm ngoài** quỹ này hoàn toàn — park không thể đẩy chúng ra. Đo park/NAV thật:

| Sổ | park/NAV toàn kỳ (mean / median) | park/NAV riêng NEUTRAL (mean / median / p90) |
|---|---|---|
| BAL | 31,3% / 35,4% | 51,3% / 58,2% / 70,0% |
| LAG | 23,8% / **0,7%** | 39,0% / 55,0% / 70,1% |

Park chỉ bật ở NEUTRAL (`PARK_STATES="3:0.7"`) ⇒ park/NAV = **0,0%** ở CRISIS/BEAR/BULL/EXBULL.
Median park/NAV của sổ LAG toàn kỳ là **0,7%** — nói "PARK chiếm 70-80% danh mục ngay từ đầu" là sai
với mọi cách đo.

### 1.4 Đo thật: park bị **rút cạn xuống dưới chính target của nó** để nuôi lệnh

Phép thử sạch: khối 4c **không bao giờ** bán park xuống **dưới** target (nó bán đúng `−delta`, dừng
ở target). Nên bất kỳ phiên NEUTRAL nào (target 70%) mà **kết phiên** park/pool < 70% ⇒ park bị bán
bởi **đường khác** = JIT nuôi lệnh mua.

| Sổ | Phiên NEUTRAL | park/pool **< 10%** | median park/pool |
|---|---|---|---|
| BAL | 1.895 | **115 (6,1%)** | **70,0%** (đúng target) |
| LAG | 1.895 | **118 (6,2%)** | **70,0%** |

Phân bố **lưỡng cực**: hoặc đứng đúng 70%, hoặc bị rút gần sạch. Nếu PARK có quyền ưu tiên, tập này
phải **RỖNG**.

### 1.5 Trace một phiên NEUTRAL cụ thể — **2018-08-08**, sổ LAG

```
mở phiên :  cash 13,954B   cổ phiếu 26,847B   park 52,533B
đóng phiên: cash  0,000B   cổ phiếu 94,905B   park  0,000B
```

27 lệnh mua PEAD khớp (ACB 9,49B · CKD 10,43B · DTT 11,41B · GMX 12,59B · PTS 13,85B · VGC 6,33B …)
tổng **≈ 68B**. Nguồn tiền: 13,95B tiền mặt + **52,53B bán sạch park** (15 dòng
`sell CUSTOM_VN30EXVIC_PITG`). **Park bị thanh lý 100% để nhường chỗ cho deal.** Trong khi state =
NEUTRAL, target park = 70% — engine vẫn phá trần target để nuôi lệnh, đúng thiết kế "deal-first".

Ba trace khác cùng dạng (2017-04-26 park 46,9→28,6B; 2017-10-27 49,7→31,1B; 2018-10-26 59,3→35,6B)
— nằm trong output script.

### 1.6 Tổng hợp

| Số đo | Giá trị |
|---|---|
| book-day có lệnh mua cổ phiếu | 1.156 |
| … bán park cùng ngày | 431 (37,3%) |
| … **mua** park cùng ngày | 143 (12,4%) ← quét phần dư, song song với deal |
| Tổng khối lượng mua cổ phiếu | 15.210,1B |
| Tổng bán park / mua park | 8.789,4B / 8.427,0B |
| **Lệnh bị BỎ ở chân control** | **0** |
| Lệnh bị bỏ khi tắt JIT (= live hôm nay) | 8.995 |
| Lệnh bị bỏ khi tắt cả 2 đường bán park | 25.682 |

### 1.7 ⚠️ Điều tôi KHÔNG đo được — nói thẳng

Lệnh có thể bị **CO NHỎ** thay vì bị bỏ: `simulate_holistic_nav.py:1191-1192`

```python
if cash + _margin_room < target_value * 0.99:
    target_value = (cash + _margin_room) * 0.95
```

và JIT bị chặn trần thanh khoản ngày `_etf_day_cap(today)` (`:1137`). **Tôi CHƯA đo tần suất nhánh
co lệnh này binding trong chân control** — CSV audit không ghi `target_value` gốc. Muốn đo phải chạy
lại có instrument. Vậy nên phát biểu đúng là: **park không làm rớt lệnh nào (0), nhưng "0 lệnh rớt"
không đồng nghĩa "0 lệnh bị thu nhỏ".**

---

## 2. CÂU HỎI 2 — Đóng góp riêng từng book

### 2.1 Vì sao phép tách này là CHÍNH XÁC, không phải xấp xỉ

`nav_bal` và `nav_lag` được mô phỏng bằng **hai lời gọi `simulate()` độc lập hoàn toàn**
(`pt_v22_dt5g.py:723` và `:751`), mỗi sổ seed **25B**, tín hiệu riêng, bảng giá riêng. Allocator ở
bước 8 (`:765-808`) chỉ nhân **hai số vô hướng** với suất sinh lời ngày của từng sổ — **không có
feedback nào vào sizing bên trong sổ**.

⇒ "Tắt LAG" **chính xác bằng** đường NAV của riêng sổ BAL; "tắt BAL" **chính xác bằng** đường NAV của
riêng sổ LAG. Không cần chạy lại backtest, và không mất mát gì khi tách.

### 2.2 Bảng kết quả

| Chân | CAGR | Sharpe | MaxDD | Calmar | Final NAV | IS 2014-19 | OOS 2020+ |
|---|---|---|---|---|---|---|---|
| **A control = V2.4 (số pin)** | 28,86% | **1,90** | **−17,8%** | **1,62** | 1.178,01B | 27,09% | 30,48% |
| **BAL alone** (tắt LAG) | 27,57% | 1,57 | −22,2% | 1,24 | 519,49B | **20,82%** | **34,11%** |
| **LAG alone** (tắt BAL) | **28,89%** | 1,68 | −24,5% | 1,18 | 590,76B | **28,37%** | 29,41% |
| static 35/65, bỏ band | 28,45% | 1,83 | −19,7% | 1,44 | 1.131,63B | 25,98% | 30,79% |
| static 50/50, bỏ band | 28,25% | 1,84 | −18,1% | 1,56 | 1.110,25B | 24,88% | 31,46% |

| So với control | ΔCAGR | ΔSharpe | ΔMaxDD | ΔCalmar |
|---|---|---|---|---|
| BAL alone | −1,29pp | −0,33 | −4,4pp | −0,38 |
| LAG alone | **+0,03pp** | −0,22 | −6,7pp | **−0,44** |
| static 35/65 | −0,41pp | −0,07 | −1,9pp | −0,18 |
| static 50/50 | −0,61pp | −0,06 | −0,3pp | −0,06 |

**Tương quan suất sinh lời ngày BAL vs LAG = 0,496.**

### 2.3 Đọc bảng — kết luận chính

> **Không sổ nào một mình thắng cặp về risk-adjusted.** LAG một mình **bằng** control về CAGR
> (+0,03pp) nhưng **mất 0,44 Calmar** và MaxDD tệ hơn 6,7pp. BAL một mình kém cả hai chiều.
> Ưu thế Sharpe 1,90 / Calmar 1,62 của V2.4 đến **chủ yếu từ ĐA DẠNG HOÁ** giữa hai sổ tương quan
> chỉ 0,50 — không phải từ alpha vượt trội của sổ nào.

**Đính chính do quant-skeptic bắt (đúng, tôi nhận):** phiên bản đầu tôi viết *"TOÀN BỘ ưu thế là đa
dạng hoá"* — **hơi quá**. Trộn tĩnh 50/50 đã cho Calmar **1,56**; control được **1,62**. Nên
~**0,06 Calmar** là công của **bản thân allocator động** (band ±10pp + tilt edge-conditional), phần
còn lại mới là đa dạng hoá thuần. Diễn đạt đúng: *đa dạng hoá là nguồn chính, allocator động thêm
một phần nhỏ nhưng đo được.*

**Hai sổ mạnh ở hai thời kỳ khác nhau** — đây mới là lý do cặp thắng:

| | IS 2014-19 | OOS 2020+ |
|---|---|---|
| BAL | 20,82% | **34,11%** |
| LAG | **28,37%** | 29,41% |

LAG gánh nửa đầu mẫu, BAL gánh nửa sau. Per-year rõ hơn: 2014 LAG **+73,2%** vs BAL +9,5%;
2020 BAL **+62,9%** vs LAG +3,2%; 2022 BAL −13,5% vs LAG **+1,3%**; 2023 LAG **+38,3%** vs BAL +12,0%.

### 2.4 Chân thứ 4 (tắt rebalance PARK) — **đã đo từ 2026-08-03**, trích lại

Bảng 2×2 ở `park_unpark_live_wiring_20260803.md` §E2 (cùng cấu hình, md5 4 chân khác nhau,
self-check 0 VND cả 4):

| Chân | L1 `PREFILL` | L2 `JIT` | CAGR | Sharpe | MaxDD | Calmar | buy bị bỏ |
|---|---|---|---|---|---|---|---|
| **A** = số pin | on | on | 28,86% | **1,90** | **−17,8%** | **1,62** | 0 |
| **D** | **off** | on | 29,92% | 1,76 | −25,1% | 1,19 | 0 |
| **C** | on | **skip** | 28,08% | 1,88 | −17,9% | 1,57 | 8.995 |
| **E = LIVE hôm nay** | **off** | **skip** | **33,16%** | **1,48** | **−33,7%** | **0,98** | 25.682 |

Tắt đường bán park làm **CAGR TĂNG** nhưng **MaxDD gần gấp đôi** — vì park là 30 blue-chip, không
phải tiền mặt, nên trần park 70% quỹ tiền thực chất là một **trần tỷ trọng cổ phiếu** trá hình.

---

## 3. CÂU HỎI 3 — Band ±10pp có vận hành thật trong mô phỏng không?

### 3.1 Con số 100% là **HIỂN NHIÊN THEO ĐỊNH NGHĨA** — đừng đọc nó như bằng chứng

| Số đo | Giá trị |
|---|---|
| `\|w_LAG_thực − w_LAG_target\| ≤ 10pp` | **3.107 / 3.107 = 100,00%** |
| Vượt 10pp | **0** (gap lớn nhất quan sát 9,54pp) |

**Đây là tautology, không phải phát hiện.** Band **CHÍNH LÀ** trigger rebalance
(`pt_v22_dt5g.py:797-800`: hễ `|cl/P − w_tgt| > 0,10` thì snap `cl = w_tgt × P` ngay trong phiên) ⇒
một lần vượt band **không thể tồn tại** đến cuối phiên. Đo "% trong band" là đo lại chính định nghĩa.

### 3.2 Con số THẬT SỰ có thông tin

| Số đo | Giá trị |
|---|---|
| Số lần REBAL thực sự nổ | **37** trong 12,46 năm = **3,0 lần/năm** |
| Tổng ma sát rebalance | **3.878,7 tr VND** |
| Gap median / p90 / p99 | 0,85pp / 4,14pp / **8,83pp** |
| Target 0,00 (BEAR) | 241 phiên (7,8%) |
| Target 0,50 | 1.753 phiên (56,4%) |
| Target 0,65 (edge-health ≥4%) | 1.113 phiên (35,8%) |

⇒ **Cơ chế CÓ vận hành thật**, nhưng thưa: p99 gap 8,83pp cho thấy nó thường xuyên áp sát trần rồi
mới nổ. Và nó **không sinh lệnh cổ phiếu nào** — chỉ là kế toán vốn hậu kỳ (đã chốt ở §A1 vòng trước).

### 3.3 🔴 Nhưng "w_LAG" đang đo SAI thứ mà tên nó gợi ý

`w_LAG` tính **cash + cổ phiếu + park** của sổ LAG. Nó là **VỐN PHÂN BỔ cho sleeve**, KHÔNG phải
**tiền đang làm việc trong deal PEAD**. Tách ra:

| Thành phần | mean | p25 | median | p75 |
|---|---|---|---|---|
| LAG **cổ phiếu** | 43,0% | 0,0% | 20,0% | 97,6% |
| LAG park | 23,8% | 0,0% | 0,7% | 64,1% |
| LAG tiền mặt | 33,2% | 0,9% | 26,6% | 30,8% |
| BAL cổ phiếu | 31,5% | 0,0% | 18,3% | 49,2% |
| BAL park | 31,3% | 0,0% | 35,4% | 61,4% |
| BAL tiền mặt | 37,2% | 17,0% | 26,6% | 53,9% |

**Sổ LAG phân bố LƯỠNG CỰC, không phải giải ngân đều:**

| Tỷ trọng cổ phiếu của sổ LAG | Số phiên | % |
|---|---|---|
| [0%, 5%) — **gần như không có deal nào** | 1.245 | **40,1%** |
| [5%, 20%) | 309 | 9,9% |
| [20%, 40%) | 190 | 6,1% |
| [40%, 60%) | 106 | 3,4% |
| [60%, 101%) — **gần như all-in** | 1.257 | **40,5%** |

Theo state DT5G (mean tỷ trọng cổ phiếu sổ LAG): CRISIS 53,2% · BEAR 28,0% · NEUTRAL 42,2% ·
BULL 43,7% · EXBULL 41,1%.

---

## 4. CÂU HỎI 4 — Trả lời thẳng

### 4.1 "LAG có hiếm khi đạt gần target ngay trong chính backtest không?"

**Phải phân biệt hai câu hỏi bị gộp làm một:**

**(a) Về VỐN PHÂN BỔ — LAG luôn đạt target. Không hề hiếm.**
100% số phiên nằm trong band, 37 lần snap về đúng target trong 12,46 năm. Cơ chế 2-book + band
**vận hành thật trong mô phỏng**, không phải trên giấy. Nhưng như §3.1 nói, con số 100% là hiển
nhiên theo định nghĩa — bằng chứng thật là 37 lần snap + ma sát 3.878,7tr đã trả.

**(b) Về TIỀN THẬT SỰ NẰM TRONG DEAL PEAD — thì ĐÚNG, thưa hơn nhiều so với ấn tượng "65% vào LAG".**
Trên **40,1% số phiên**, sổ LAG giữ **dưới 5%** NAV của nó trong cổ phiếu PEAD. Trung bình chỉ 43,0%.
Phần còn lại là tiền mặt (33,2%) và park (23,8%).

> **Nói cách khác: "w_LAG = 65%" KHÔNG có nghĩa 65% tài sản đang chạy chiến lược PEAD.**
> Nó có nghĩa 65% vốn được *giao* cho sleeve LAG — mà sleeve đó, gần một nửa thời gian, đang
> ngồi tiền mặt hoặc park vì **không có tín hiệu PEAD nào đủ điều kiện**.

Đây **không phải bug**, và **không phải khác biệt live-vs-backtest** — chính bản mô phỏng đã pin
28,86% cũng chạy như vậy. Nhưng nó **có** làm sai lệch cách đọc: ai nhìn `w_lag_current = 0,495` mà
hiểu là "một nửa danh mục đang chạy PEAD" là đang hiểu sai mẫu số. Đúng như §A3 vòng trước đã chỉ ra
với ca `plan_ZaloPay_2026-07-31` (sim 49,5% gồm park vs DollarBill 30,5% chỉ cổ phiếu).

### 4.2 "LAG có edge thật và có được ưu tiên đúng trong mô phỏng không?" — bằng chứng cụ thể

**Có, cả hai — nhưng edge của LAG là edge THỜI KỲ, không phải edge vượt trội thường trực.**

| Bằng chứng | Số đo |
|---|---|
| LAG alone CAGR | **28,89%** — cao hơn BAL alone (27,57%) và ngang control (28,86%) |
| LAG alone IS 2014-19 | **28,37%** vs BAL **20,82%** → LAG gánh gần trọn nửa đầu mẫu |
| LAG alone OOS 2020+ | 29,41% vs BAL **34,11%** → nửa sau thì BAL gánh |
| Năm LAG cứu hệ | 2014 **+73,2%** (BAL +9,5%) · 2023 **+38,3%** (BAL +12,0%) · 2022 **+1,3%** (BAL −13,5%) |
| Năm LAG tụt lại | 2016 +4,0% (BAL +24,6%) · 2020 +3,2% (BAL +62,9%) |
| **Được ưu tiên đúng?** | **Có.** 0 lệnh bị bỏ ở chân control; park bị bán 8.789,4B để nuôi deal; ca 2018-08-08 park bị thanh lý 100% cho LAG |
| Rủi ro độc lập | LAG alone MaxDD **−24,5%**, Calmar 1,18 — **kém control rõ**; nó cần BAL để cân |

**Điều KHÔNG được suy ra từ đây:** không được đọc "LAG alone 28,89% ≈ control 28,86%" thành "bỏ BAL
đi cũng thế". Calmar rơi 1,62 → 1,18 và MaxDD xấu đi 6,7pp. Và caveat §2.5 dưới đây.

### 4.3 ⚠️ Giới hạn phải nói rõ

1. **Sổ 25B, vốn cấp 17,5B/32,5B.** Mỗi sổ được mô phỏng ở nền vốn **25B**, rồi allocator mới gán
   17,5B/32,5B. Nghĩa là sizing vị thế **bên trong** mỗi sổ tính trên 25B chứ không trên vốn thực
   được cấp. Phép tách của tôi **chính xác với engine ĐÚNG NHƯ NÓ ĐƯỢC ĐẶC TẢ**, nhưng một lần triển
   khai một-sổ thật ở 50B sẽ đụng trần ADV/capacity khác. **Tôi KHÔNG chạy lại ở 50B.**
2. **Chưa đo tần suất "co lệnh"** (§1.7) — biết 0 lệnh bị bỏ, chưa biết bao nhiêu lệnh bị thu nhỏ.
3. **CSV audit gộp reason_tag**: `pt_v23_audit_2014.py` đổi cả `PREFILL_STATE_REBAL` lẫn
   `JIT_FOR_BA_BUY` thành `ETF_REBAL_state<N>`. Tôi tách được hai đường bằng **suy luận cơ học**
   (4c không thể bán dưới target — §1.4), không bằng đọc tag. quant-skeptic đề xuất giữ tag mịn cho
   lần sau — hợp lý, chưa làm.
4. **Không chạy DSR/PBO** — cố ý: đây là nghiên cứu mô tả cơ chế trên một run ĐÃ pin, `N_trials = 0`,
   không chọn cấu hình nào, không đề xuất gì để wire.

---

## 5. quant-skeptic — CONFIRMED (confidence high)

Log đầy đủ: `mike/logs/verify_20260805_164057_3879435.log`.

- `reproducibility_selfcheck` **pass** — reviewer **tự chạy lại cả 2 script** và tái lập **từng con
  số** trong cả 4 claim, kể cả trace 2018-08-08 **đúng đến từng VND**.
- `arithmetic_mechanism` **pass** — `cap_bal + cap_lag = combined_nav` (replay err 0,0); xác nhận hai
  `simulate()` độc lập tại `pt_v22_dt5g.py:723/751` và allocator vô hướng `:765-808`.
- `look_ahead_leak` / `oos_robustness` / `panel_curation_bias` **pass**; `param_overfit` **na**.
- **`killer_objection`**: framing *"TOÀN BỘ ưu thế là đa dạng hoá"* hơi quá — allocator động góp
  ~0,06 Calmar so với trộn tĩnh 50/50. **Đã sửa ở §2.3.** Không đổi con số nào.

---

## 6. Ba câu tóm tắt cho người quyết định

1. **PARK không chặn deal — nó ăn phần dư.** Sizing lệnh tính trên NAV đã gồm park
   (`simulate_holistic_nav.py:1120`), trần 70% áp trên quỹ tiền chứ không trên danh mục, park mua ở
   bước cuối cùng của phiên, và trên thực tế park bị bán 8.789B để nuôi deal — có ngày bị thanh lý
   sạch 100%. **0 lệnh bị bỏ** ở chân control.
2. **Không sổ nào một mình thắng cặp.** LAG alone 28,89%/Calmar 1,18 · BAL alone 27,57%/Calmar 1,24 ·
   cặp 28,86%/**Calmar 1,62**. Ưu thế đến chủ yếu từ **đa dạng hoá** (tương quan 0,50, hai sổ gánh hai
   thời kỳ khác nhau), cộng ~0,06 Calmar từ allocator động.
3. **Nghi ngờ của user đúng — nhưng đúng ở chỗ khác chỗ đang chỉ.** Cơ chế band **có** vận hành thật
   trong mô phỏng (37 lần snap, ma sát 3.878,7tr). Cái "chỉ trên giấy" là **cách đọc `w_LAG`**: nó là
   vốn *giao cho* sleeve, không phải tiền *đang chạy* PEAD — và **40,1% số phiên sổ LAG giữ dưới 5%
   NAV trong cổ phiếu PEAD**.

**KHÔNG đề xuất thay đổi production nào trong báo cáo này.**
