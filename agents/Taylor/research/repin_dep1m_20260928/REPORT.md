# RE-PIN R3 theo quy ước tiền nhàn rỗi mới (`dep1m`) — job `Taylor_20260927_170645`

> **Phạm vi: PAPER + REGISTRY.** Không đổi `trading_rules.json`, không đổi rail, không merge vào
> canonical, không tự ghi `data/results_registry.md`. Park giữ **0,30** y nguyên — đây là **đổi
> QUY ƯỚC ĐO**, không đổi mô hình.
>
> Cơ sở: user chốt 23:58 ICT 2026-09-27 (Discord): *"Đồng ý giữ lại parking tỉ lệ 0.3. Tiền mặt
> thì neo theo lãi suất huy động 1 tháng. Lấy căn cứ này làm số pin"*.

Code: worktree `mike/agents/Taylor/wt-repin-dep1m-2809`, branch `research/repin-dep1m-2709`,
commit **`d3c37631`** (nhánh cha = `5a9d424c` của W2b).

---

## 0. Một dòng

**Số pin mới: CAGR 25,71% / Sharpe(252) 2,06 / MaxDD −14,0% / Calmar 1,83 / Final NAV 864,86B**
(cửa sổ 2014-01-02 → 2026-06-19, 12,46 năm, NAV 50B, park 0,30).
Neo DD để sizing đổi từ **−25,2% → −23,6%** (bootstrap 5th-pct).
**+2,34pp CAGR so anchor 23,37%, trong đó 2,05pp là SỐ HỌC TRỰC TIẾP** (tiền nhàn rỗi chiếm 46,4%
NAV, giờ được trả ~3,5%/năm thay vì 0%) và chỉ 0,285pp là engine đi đường giao dịch khác — phần
sau **nằm dưới sàn nhiễu W2b (0,46pp)** nên không phân biệt được với nhiễu.

---

## 1. Tier `dep1m` — dữ liệu và cách dựng lại

Nguồn mới (Mike kéo 2026-09-27 tối, trước khi FiinPro-X trial hết hạn 28/09 — **nguồn chết sau
đó**): `research/idle_cash_proxy_20260927/fiinprox_deposit_1m_big4_monthly_2019_2026.csv` —
lãi suất **huy động kỳ hạn 1 tháng, khách CÁ NHÂN, bình quân nhóm Big 4**, 92 tháng
2019-02 → 2026-09, mỗi tháng chụp ngày 15 (cột `asof`).

| Đoạn | Bản chất | Số tháng trong cửa sổ 2014-01…2026-06 |
|---|---|---|
| 2019-02 → 2026-09 | **SỐ THẬT** FiinPro công bố | **89** |
| trước 2019-02 | **DỰNG LẠI** = `sbv_low + offset` | **53** |
| 8 tháng khuyết `sbv_low` | forward-fill mốc tháng trước | 8 (2015-02, 2016-02, 2016-08, 2017-01…03, 2017-05, 2017-09) |

Route FiinPro trả **HTTP 500 cho mọi ngày ≤ 2018-12** (Mike dò 2014/2015/2016/2018 đều rỗng) ⇒
không thể kéo thêm. Vì vậy phải bắc cầu.

### 1.1 Chọn cầu — tự đo lại, không tin số Mike đưa

| Cầu ứng viên | n | median | mean | sd | p25 | p75 | corr | Dùng được? |
|---|---|---|---|---|---|---|---|---|
| dep1m − **SBV 12M-thấp** (`sbv_low`) | 90 | **−2,525** | −2,857 | **0,883** | −3,400 | −2,300 | **+0,619** | **CÓ** |
| dep1m − liên NH 1M | 92 | −0,240 | −0,863 | 2,472 | −3,045 | +1,342 | −0,141 | **KHÔNG** |

Đo lại độc lập (`idle_rate_proxy_selfcheck.py --dep1m`) — **khớp số Mike đưa**: median −2,525 /
sd 0,883 / p25 −3,400 / p75 −2,300 / corr +0,619. Với cầu liên NH tôi được sd 2,472 & corr −0,141
(Mike: 2,456 / −0,134) — lệch do Mike đo trên tập con 90 tháng chung với SBV; **kết luận y hệt**:
liên ngân hàng có sd gấp **2,8×** và tương quan ÂM ⇒ không bắc cầu được.

**Offset dùng cho số pin = MEDIAN −2,525pp** (luật định trước của dispatch; trung vị bền với đuôi).
Kiểm tra liên tục ở mối nối: 2019-01 recon = 6,60 − 2,525 = **4,075%**; 2019-02 thật = **4,500%**
⇒ bước nhảy +0,43pp, không có đoạn vỡ.

### 1.2 Luật point-in-time giữ nguyên
Mốc tháng T **chỉ dùng từ ngày đầu tháng T+1** (y như 2 tier cũ). Không back-fill số thật về quá
khứ (`dep1m_src` đánh dấu `real`/`recon`, có fixture test chứng minh mask này THẬT sự chặn — xem
§2). Tháng thiếu ⇒ **forward-fill mốc đã công bố trước đó**, KHÔNG nội suy tương lai; ngày trước khi
chuỗi bắt đầu ⇒ **0% fail-safe** và engine **in ra số phiên bị 0%**.

> **Số phiên bị trả 0%: 0** (cả chân full-window và chân cửa sổ hẹp) — chuỗi dựng lại bắt đầu
> 2011-01 nên phủ kín cửa sổ backtest. Engine tự in dòng này mỗi lần chạy, không phải tôi khẳng định.

---

## 2. Selfcheck (bước 1)

`idle_rate_proxy_selfcheck.py` — **50 assertion cũ giữ nguyên PASS**, nâng lên **102 assertion**
(+52 cho tier dep1m: T9 khớp CSV từng giá trị, T10 công thức recon + nhãn src, T11 biên PIT
real/recon + ff lùi, T12 phủ cửa sổ + trần break-even 7%, T13 override offset chỉ đổi đoạn recon,
T14 bằng chứng offset/coverage, T15 fixture chống back-fill).

**Mutation: 15/15 bị giết** (7 cũ + 8 mới M8…M15).

Hai mutation ứng viên **bị loại vì CHỨNG MINH ĐƯỢC LÀ TƯƠNG ĐƯƠNG**, ghi ra thay vì im lặng bỏ:
- đảo `real.combine_first(recon)` → `recon.combine_first(real)`: hai mask rời nhau ⇒ kết quả y
  nguyên với mọi đầu vào.
- bỏ `.clip(lower=0)` ở nhánh recon: `min(sbv_low)` trên đoạn recon = **6,4** (2015-03), offset âm
  nhất dùng ở bất kỳ chân nào là p25 = −3,4 ⇒ 3,0 > 0 ⇒ clip **không bao giờ chặn**.

Thay bằng M10 (khai sai `DEP1M_REAL_FROM`) và M11 (tháng khuyết trả 0% thay vì ff) — cả hai bị giết.

**TZ**: PASS dưới `Asia/Ho_Chi_Minh`, `UTC`, `America/New_York`, `Pacific/Kiritimati` và
`env -u TZ`; mutation 15/15 cũng bị giết dưới `TZ=UTC`. Chạy bằng `$DNA_PYEXE`.

**Cổng cấu hình** (`pt_v23_audit_2014.py`): `IDLE_CARRY_TIER=dep1m` → tag `_idledep1m`;
`IDLE_DEP1M_OFFSET_PP` là **trục đối số ⇒ vào tên file** (§8, `-3.4` → `_offm3p400`) và bị **chặn
cứng** nếu đặt kèm tier khác (`ValueError`, đã test); `bogus` bị từ chối; `off` cho tag rỗng.

---

## 3. Cổng bắt buộc — chân control (bước 2) ✅

| | |
|---|---|
| Chân | `rp_ctrl` = lệnh pin anchor R3 nguyên văn + `IDLE_CARRY_TIER=off` |
| md5 ledger | **`4707bcbeb7e801d49a4a851ffd91d5e7`** |
| md5 anchor R3 | `4707bcbeb7e801d49a4a851ffd91d5e7` |
| `cmp` | **sạch — BYTE-IDENTICAL** |
| Metric | CAGR 23,37% / Sharpe(252) 1,88 / MaxDD −14,6% / Calmar 1,60 / NAV 684,52B |
| self-check | BAL + LAG: cash-flow identity 0 VND, final NAV identity 0 VND |

⇒ Thêm tier dep1m **không làm lệch đường đi khi tắt**. Mọi Δ đọc sau đây là của riêng quy ước carry.

---

## 4. Chân pin mới (bước 3)

Lệnh = lệnh pin anchor R3 **nguyên văn** (job `Taylor_20260927_131635`), chỉ thêm
`IDLE_CARRY_TIER=dep1m`; `PARK_STATES=3:0.3` giữ nguyên.

| Đại lượng | Anchor R3 (carry 0%) | **PIN MỚI (`dep1m`)** | Δ |
|---|---|---|---|
| CAGR | 23,37% | **25,71%** | **+2,34pp** |
| Sharpe(252) | 1,88 | **2,06** | +0,18 |
| MaxDD | −14,6% | **−14,0%** | +0,6pp (hẹp hơn) |
| Calmar | 1,60 | **1,83** | +0,23 |
| Final NAV | 684,52B | **864,86B** | +180,34B |
| md5 ledger | `4707bcbe…` | **`bcd0469f42c2f76937a6ebb10aae9b40`** | |
| self-check | 0 VND | **0 VND** (BAL + LAG, cash-flow + final NAV identity) | |

### Walk-forward

| Đoạn | CAGR | Sharpe¹ | MaxDD | Calmar | NAV |
|---|---|---|---|---|---|
| FULL 2014-01-02…2026-06-19 (12,46y) | 25,71% | 2,05 | −14,0% | 1,83 | 50,0B → 864,86B |
| **IS 2014-2019** (5,99y) | 22,47% | 2,02 | −14,0% | 1,60 | 50,0B → 168,47B |
| **OOS 2020+** (6,46y) | **28,71%** | 2,08 | −13,0% | **2,20** | 169,29B → 864,86B |

¹ Sharpe cột này = `leg_metrics.py` (simple return, annualize theo **thời gian lịch**, 249,28
obs/năm) nên FULL ra 2,05 chứ không phải 2,06 mà engine in (`sqrt(252)`). Bootstrap/DSR dùng **log
return** nên in 1,988. **Ba quy ước, không được trộn**; số của record = cột engine in ra (2,06),
vì đó đúng quy ước sinh ra con số 1,88 của anchor.

**OOS tốt hơn IS ở mọi chiều** (CAGR +6,24pp, Sharpe +0,06, DD hẹp hơn 1,0pp, Calmar +0,60) ⇒
edge không rớt OOS.

Carry thực áp: mean **3,501%/năm**, min 1,600%, max 4,975%, 0 phiên bị 0%.

### Theo năm (ctrl → pin)

> **QUY ƯỚC GỐC (bắt buộc đọc trước khi trích Δ):** đây là số engine tự in ở khối `ANNUAL`, gốc là
> **PHIÊN ĐẦU TIÊN CỦA CHÍNH NĂM ĐÓ** (`pt_v23_audit_2014.py`: `s_y.iloc[-1]/s_y.iloc[0]-1`),
> **KHÔNG** phải cuối năm trước. Hai quy ước cho Δ khác nhau ở những năm có gap giao thừa lớn:
> 2021 = **−4,70pp** theo gốc đầu-năm nhưng **−3,64pp** theo gốc cuối-năm-trước (quant-skeptic
> 2026-09-27 đo lại). Mọi số dưới đây là gốc **đầu năm**; cấm trộn hai quy ước trong một bảng.

| Năm | carry 0% | dep1m | Δpp | | Năm | carry 0% | dep1m | Δpp |
|---|---|---|---|---|---|---|---|---|
| 2014 | +50,44% | +54,93% | +4,49 | | 2021 | +110,44% | +105,74% | **−4,70** |
| 2015 | +18,96% | +21,61% | +2,65 | | 2022 | −2,32% | −3,10% | **−0,78** |
| 2016 | +10,56% | +12,80% | +2,24 | | 2023 | +16,68% | +19,52% | +2,84 |
| 2017 | +16,86% | +19,10% | +2,24 | | 2024 | +19,89% | +22,20% | +2,31 |
| 2018 | +21,28% | +23,62% | +2,34 | | 2025 | +30,58% | +37,96% | +7,38 |
| 2019 | +4,72% | +5,95% | +1,23 | | 2026 (½) | −2,28% | −1,24% | +1,04 |
| **2020** | **+22,03%** | **+25,57%** | **+3,54** | | | | | |

**11/13 năm tốt hơn, 2 năm xấu hơn** (2021 −4,70pp, 2022 −0,78pp). Dòng 2020 bị thiếu ở bản đầu
(quant-skeptic 2026-09-27 mục `arithmetic_mechanism` — bảng chỉ có 12 dòng trong khi văn bản nói
13 năm); đã bổ sung, **kết luận 11/13 không đổi** vì 2020 là một năm TỐT hơn.

Dải Δ theo năm (−4,70 … +7,38pp) **rộng hơn nhiều** so với hiệu ứng số học đều (~+2pp) ⇒ đúng dấu
hiệu nhiễu đường đi mức-năm mà W2b đã đo (swing 13–28pp/năm/book).

---

## 5. Neo sizing DD đo lại (bước 4)

`bootstrap_nav.py`, circular block **L=21, B=4000, seed=12345** (hằng số trong file, không đổi).

| | anchor (carry 0%) | **PIN MỚI** |
|---|---|---|
| **DD 5th-pct (neo sizing)** | −25,2% | **−23,6%** |
| DD median | −16,4% | −15,6% |
| DD actual | −14,6% | −14,0% |
| CAGR 5th-pct | 15,5% | **17,8%** |
| Sharpe 5th-pct | 1,26 | 1,45 |
| P(DD < −30%) | 1,1% | **0,5%** |
| P(DD < −40%) | 0,0% | 0,0% |

Đối chứng bootstrap **stationary (Politis-Romano)**: CAGR 5th 17,7% / DD 5th −23,1% / P(DD<−30%)
0,4% — nhất quán với circular block.

> **Số user dùng để sizing: DD 5th-pct = −23,6%** (không phải −14,0% actual).
> Bootstrap chỉ đo bất định LẤY MẪU, không mô hình đổi regime ⇒ bất định thật RỘNG HƠN.

### DSR / PBO — manifest ghim tường minh (không glob động)

`data/dsr_family_manifest_repin_dep1m_2026-09-28.json` (**N=4**) và `…_ext.json` (**N=14**).
Họ trial = 4 cấu hình ĐÃ ĐƯỢC SO VỚI NHAU khi chốt số pin: 1 chân quy ước cũ (carry 0%) + 3 chân
`dep1m` × {median, p25, p75}. Bản `_ext` thêm 10 chân W2/Q2 cùng phương tiện cùng ngày = **chặn
trên thận trọng** của cửa sổ trial.

| | N=4 | N=14 |
|---|---|---|
| **DSR** @N_csv | **1,0000** | **1,0000** |
| DSR @N_reg=120 | 1,0000 | 1,0000 |
| DSR @N_reg=200 (thận trọng) | **1,0000** | **1,0000** |
| **PBO** | **0,5000** | **0,1258** |
| logit λ median | −0,00 | +2,64 |

**DSR = 1,0000 ở mọi N** ⇒ ngưỡng `DSR<0,95 = RED FLAG` không bị đụng.

**PBO = 0,5000 trên họ N=4 CHẠM đúng ngưỡng cờ đỏ `PBO≥0,5` — phải nói thẳng, và đây là cách đọc
đúng:** giá trị 0,5000 là giá trị **THOÁI HOÁ**, không phải bằng chứng overfit. 4 chân gần cộng
tuyến — tương quan log-return ngày **0,98771 … 0,99998** (`rp_pin` vs `rp_p75` = **0,99998**) —
nên CSCV không phân biệt được chân nào, logit λ median = 0,00 và P(λ<0) = 0,5 **đúng bằng tung xu**.
Trên họ N=14 PBO = 0,1258.

**Và cái remedy mà luật CLAUDE.md kê cho PBO≥0,5 — "chọn config robust-trung vị, không IS-best" —
đã được làm TRƯỚC khi đo:** offset **median** là luật định trước của dispatch, và trên số thực tế
chân median cho **CAGR THẤP NHẤT** trong 3 chân (25,71 < 25,80 p75 < 25,89 p25). Không thể là
IS-best-picking.

---

## 6. Băng bất định của cầu (bước 5)

### 6.1 Ba offset, cùng mọi thứ khác

| Offset | carry mean | CAGR | Sharpe(252) | MaxDD | Calmar | DD 5th |
|---|---|---|---|---|---|---|
| p25 −3,400pp | 3,139%/y | **25,89%** | 2,08 | −14,1% | 1,84 | −23,27% |
| **median −2,525pp (PIN)** | 3,501%/y | **25,71%** | 2,06 | −14,0% | 1,83 | −23,56% |
| p75 −2,300pp | 3,594%/y | **25,80%** | 2,06 | −14,0% | 1,84 | −23,43% |
| **Dải** | | **0,181pp** | 0,02 | 0,1pp | **0,01** | 0,29pp |

**Dải engine KHÔNG ĐƠN ĐIỆU theo offset**: chân p25 trả carry **thấp nhất** (3,139%/năm) lại cho
CAGR **cao nhất**; chân median trả carry cao hơn lại cho CAGR thấp nhất. Quan hệ nhân quả bị đảo ⇒
**trật tự trong dải này là nhiễu đường đi**, không phải hiệu ứng của offset. Dải **overlay** (không
cho engine phản ứng) thì đơn điệu đúng chiều: 25,207 < 25,421 < 25,476 (dải 0,269pp).

⇒ Kết luận **chắc**: cả dải (0,181pp engine / 0,269pp overlay) **nằm dưới sàn nhiễu W2b của chính
chân đã park (0,46pp)** và dưới MDE một-chân (0,4pp). **Số pin không nhạy cảm với lựa chọn offset
trong khoảng p25–p75.** Điều KHÔNG kết luận được: chân nào trong 3 chân "tốt hơn".

### 6.2 Chân đối chứng KHÔNG CẦN BẮC CẦU

Cửa sổ **2019-03-01 → 2026-06-19** (7,30y, 1.824 phiên). Bắt đầu 01/03 chứ không 01/02/2019 vì luật
PIT: mọi phiên tháng 02/2019 sẽ đọc mốc 01/2019 = **số dựng lại**. Engine tự in xác nhận:
**88 tháng SỐ THẬT / 0 dựng lại / 0 ff**.

| | carry 0% | dep1m | Δ |
|---|---|---|---|
| CAGR | 22,86% | **24,86%** | **+2,00pp** |
| Sharpe(252) | 1,70 | 1,83 | +0,13 |
| MaxDD | −17,5% | −16,0% | +1,5pp |
| Calmar | 1,31 | 1,56 | +0,25 |
| Final NAV | 224,77B | 253,02B | |
| md5 | `2988c7a3c44de4daf55a71d960cc0c3a` | `13d8e1de79915d1f31737054b90b558a` | |
| self-check | 0 VND | 0 VND | |

**Hiệu ứng carry đo trên DỮ LIỆU THẬT MỘT MÌNH = +2,00pp.** Trên toàn cửa sổ = +2,34pp. Chênh
0,34pp đến từ giai đoạn 2014-2019 lãi suất cao hơn (recon 4,08–4,98%/năm vs thực tế 2019+ trung
bình 3,08%) ⇒ **đoạn dựng lại KHÔNG bịa ra hiệu ứng**, nó chỉ mở rộng hiệu ứng đúng theo hướng lãi
suất lịch sử cao hơn.

---

## 7. Tách số học vs đường giao dịch (bước 6 — không lặp lỗi W2)

Overlay carry **lên chính đường NAV carry-0%** của chân control (không cho engine định tuyến lại
lệnh) ⇒ tách hiệu ứng SỐ HỌC. Công thức tái sử dụng nguyên văn `w2b_overlay.py` (đã quant-skeptic
CONFIRMED 2026-09-27 16:44Z), không dẫn xuất lại:
`nav_ov(d) = nav_ov(d−1)·(1+r_eng(d)) + max(idle(d−1),0)·rate(d)/252·nav_ov(d−1)/nav_eng(d−1)`,
`idle = bal_cash_ref + lag_cash_ref`.

| Cửa sổ | Δ TỔNG (engine) | Δ SỐ HỌC (overlay) | Δ ĐƯỜNG ĐI | % số học |
|---|---|---|---|---|
| FULL 2014-01…2026-06 (53/150 tháng dựng lại) | **+2,337pp** | **+2,052pp** | **+0,285pp** | 87,8% |
| Không bắc cầu 2019-03…2026-06 (0 tháng dựng lại) | +2,007pp | +1,989pp | **+0,018pp** | 99,1% |

Tiền nhàn rỗi chiếm trung bình **46,4% NAV** (full) / **50,0%** (cửa sổ hẹp) — đó là đòn mà carry
tác động qua.

**Đọc đúng:**
- +2,34pp **KHÔNG** phải "chiến lược tốt hơn". 2,05pp là **số học trực tiếp**: tiền nhàn rỗi ~46%
  NAV giờ được trả ~3,5%/năm thay vì 0%.
- Chỉ **0,285pp** là engine đi đường giao dịch khác, và 0,285pp **nằm dưới** sàn nhiễu W2b của chân
  đã park (0,46pp) và dưới MDE một-chân (0,4pp) ⇒ **không phân biệt được với nhiễu**. Trên cửa sổ
  không bắc cầu phần này gần bằng 0 (0,018pp).
- Δ tổng +2,34pp gấp ~5× sàn nhiễu ⇒ **đọc được**, và pin được vì đây là MỘT cấu hình đo dưới MỘT
  quy ước mới.

**Cảnh báo kế thừa (bắt buộc mang theo):** mọi so sánh **PHƯƠNG TIỆN** (park vs không park,
custom30V vs custom30 vs C6/C10) VẪN ở trạng thái W2b — *engine không có sức phân giải*. Con số pin
mới **KHÔNG mở lại** câu hỏi đó. Muốn so phương tiện dưới quy ước `dep1m` thì phải chạy **ensemble
~160–190 chân** như W2b đề xuất, không phải đọc một lần chạy.

---

## 8. Lệnh tái lập (quant-skeptic chạy lại)

```bash
WT=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-repin-dep1m-2809/WorkingClaude   # commit d3c37631
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/repin_dep1m_20260928
DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python

# 1) selfcheck tier dep1m (102 assertion + 15/15 mutation), và dưới TZ ngoại
cd $WT && $DNA_PYEXE idle_rate_proxy_selfcheck.py --mutations
TZ=UTC $DNA_PYEXE idle_rate_proxy_selfcheck.py --mutations
env -u TZ $DNA_PYEXE idle_rate_proxy_selfcheck.py
$DNA_PYEXE idle_rate_proxy_selfcheck.py --dep1m          # bằng chứng offset + coverage

# 2) CỔNG: control phải byte-identical anchor R3
$R/run_leg.sh rp_ctrl BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off
cmp /home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_etfcreatpit_exp_reverify_j131635_univpit.csv \
    /home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_wtnamecap_advprice_etfcreatpit_exp_rp_ctrl_univpit.csv

# 3) chân pin + băng bất định + chân không bắc cầu
$R/run_leg.sh rp_pin  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m
$R/run_leg.sh rp_p25  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m IDLE_DEP1M_OFFSET_PP=-3.400
$R/run_leg.sh rp_p75  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m IDLE_DEP1M_OFFSET_PP=-2.300
$R/run_leg.sh rp_w19_off   AUDIT_START=2019-03-01 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off
$R/run_leg.sh rp_w19_dep1m AUDIT_START=2019-03-01 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m

# 4) metric + IS/OOS + md5 mọi chân
cd /home/trido/thanhdt/WorkingClaude && $DNA_PYEXE $R/leg_metrics.py <ledger...>

# 5) tách số học vs đường đi
$DNA_PYEXE $R/rp_decomp.py                    # -> rp_decomp.json  (bản cửa sổ hẹp: rp_decomp_w19.json)

# 6) neo DD + DSR/PBO
$DNA_PYEXE bootstrap_nav.py <pin_ledger> <anchor_ledger>
$DNA_PYEXE $R/build_rp_manifest.py            # và --extended
DSR_FAMILY_MANIFEST=data/dsr_family_manifest_repin_dep1m_2026-09-28.json \
  DSR_R3_CSV=<pin_ledger> $DNA_PYEXE dsr_pbo_annex.py
```

Env cố định trong `run_leg.sh` (copy nguyên văn lệnh pin anchor R3): `NAV_TOTAL_B=50`
`ETF_LIQ=custompitg` `AUDIT_END=2026-06-19` `BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate`
`BQ_CACHE_THREADS=1` `BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet`
`TZ=Asia/Ho_Chi_Minh`, interpreter `$DNA_PYEXE`. Phần thực thi của `run_leg.sh` **byte-identical**
với `run_leg.sh` của W2/Q2 (chỉ khác dòng comment + SRC/OUT).

## 9. Bảng md5 mọi ledger

| Chân | md5 | Ghi chú |
|---|---|---|
| anchor R3 (`reverify_j131635`) | `4707bcbeb7e801d49a4a851ffd91d5e7` | tham chiếu |
| `rp_ctrl` | `4707bcbeb7e801d49a4a851ffd91d5e7` | **byte-identical** ⇒ cổng qua |
| **`rp_pin`** | **`bcd0469f42c2f76937a6ebb10aae9b40`** | **số pin** |
| `rp_p25` | `832dee61dfba746dbffd55b5e3b71830` | offset p25 |
| `rp_p75` | `92fcf1c7fa911c23ac28611288a1f001` | offset p75 |
| `rp_w19_off` | `2988c7a3c44de4daf55a71d960cc0c3a` | cửa sổ không bắc cầu, carry 0% |
| `rp_w19_dep1m` | `13d8e1de79915d1f31737054b90b558a` | cửa sổ không bắc cầu, dep1m |

## 10. Giới hạn — phải mang theo khi trích số này

1. **53/150 tháng của cửa sổ là SỐ DỰNG LẠI**, không phải số công bố. Băng p25–p75 cho thấy số pin
   không nhạy với offset (dải 0,18pp), và chân không-bắc-cầu cho +2,00pp so +2,34pp — nhưng đây vẫn
   là một chuỗi hai chất lượng khác nhau nối lại.
2. **Nguồn upstream ĐÃ CHẾT**: FiinPro-X trial hết hạn 28/09/2026. Mốc sau 2026-09 phải lấy từ NHNN
   trực tiếp (không API) hoặc mua subscription.
3. Đoạn 2011-01→2025-10 của chuỗi `sbv_low` (xương sống của cầu) **chưa có nguồn thứ hai xác minh**
   — di sản từ registry W1, không phải phát sinh mới.
4. **Đây là lãi tiền gửi thị trường, KHÔNG phải carry egg DNSE thật (8,543%/năm spot 09/2026).** Egg
   trả cao hơn cả đầu mút cao thống kê NHNN ~1pp — đó là spread SẢN PHẨM, DNSE không cam kết. Số pin
   này cố ý dùng đầu THẬN TRỌNG, tức nếu egg giữ mức hiện tại thì thực tế còn tốt hơn số pin.
5. **Không kết luận gì về XẾP HẠNG PHƯƠNG TIỆN** — xem §7.
6. Quy đổi thực tế theo CLAUDE.md: CAGR thật ≈ CAGR backtest − 1,5% (phí + slippage + thuế) ⇒
   25,71% → ~**24,2%**.

---

# 11. CHÂN `dep1m_21s` — "rút trước hạn thì hưởng 0%" (job `Taylor_20260928_010454`)

> Cơ sở: user chốt **08:02 ICT 2026-09-28** (Discord): *"Đồng ý áp dụng chân tùy chọn chỉ trả carry
> cho phần tiền nằm im 21 phiên trở lên. Nhưng cũng chưa chính xác thận trọng. Thực tế nếu rút trước
> hạn coi như hưởng lãi 0%. Nên áp dụng bản pin 2 con số cho dễ hình dung. Cần note rõ pin0%, và
> pin1M để có ngưỡng sàn và trần."*
> Vẫn **PAPER + REGISTRY**: `trading_rules.json` không đổi, rail không đổi, park giữ 0,30.

## 11.1 Đặt knob ở ĐÂU, và vì sao

**Chọn: KNOB ENGINE trong `simulate_holistic_nav.py`, KHÔNG phải tier mới trong `idle_rate_proxy.py`.**

Lý do là ranh giới trách nhiệm, không phải tiện tay: `idle_rate_proxy.py` là hàm **ngày → lãi suất**.
Nó không biết — và không được biết — số dư tiền, dòng tiền vào/ra, hay tuổi của từng lô. "Tuổi tiền"
là **trạng thái của simulator**. Nhồi nó vào module rate sẽ buộc module đó nhận thêm tham số tiền mặt
mà 3 tier cũ không cần, và quy tắc tuổi thì áp được cho MỌI nguồn carry (`baseline`/`floor`/`flat`),
tức nó **vuông góc** với việc chọn lãi suất. Vì vậy:

| Trục | Ở đâu | Env |
|---|---|---|
| Lãi suất bao nhiêu | `idle_rate_proxy.py` (giữ nguyên, **không sửa logic**) | `IDLE_CARRY_TIER=dep1m` |
| Tiền nào được trả | `simulate_holistic_nav.py` (mới) | `IDLE_CARRY_MIN_AGE=21` |
| Tiêu lô nào trước | `simulate_holistic_nav.py` (mới) | `IDLE_CARRY_AGE_ORDER=fifo\|lifo` |

**§8 — cả hai trục mới là TRỤC ĐỐI SỐ ⇒ cả hai vào tên file**: tag `_idledep1m_21sfifo` /
`_idledep1m_21slifo`. Đặt `IDLE_CARRY_AGE_ORDER` khi `MIN_AGE=0`, hoặc `MIN_AGE>0` khi không có nguồn
carry, đều **raise cứng** (không sinh được một chân im lặng y hệt chân control).

## 11.2 Ngữ nghĩa đã cài — và điều KHÔNG được làm

Sổ lô tiền `[[tuổi_phiên, số_tiền], …]` xếp theo tuổi (đầu = già nhất), đối chiếu về đúng `cash` thật
**hai lần mỗi phiên**; tuổi tăng **một lần ở ĐẦU phiên**.

- Lô sinh ở phiên nào có **tuổi 0** ⇒ đủ tuổi khi `tuổi ≥ 21` ⇒ **lần đầu được trả ở phiên thứ 22**
  của lô. Phiên 1–21 trả **0 VND**.
- **KHÔNG TRUY LĨNH, bằng thiết kế.** Lô nằm 100 phiên không bao giờ được trả bù 21 phiên đầu. Truy
  lĩnh đòi biết lô đó có sống sót không ⇒ **nhìn trước**. Lãi được trả **không nhập vào gốc lô**: nó
  xuất hiện như tiền mới ở lần đối chiếu cuối phiên và **tự đếm tuổi từ 0**.
- Tiền bị tiêu trước phiên 22 hưởng 0% **tự động** (chưa từng được cộng) ⇒ không cần cơ chế thu hồi.
- `cash < 0` (margin) ⇒ sổ lô rỗng; tiền về sau đó là lô tuổi 0, chờ lại từ đầu.

**Vì sao phải đối chiếu HAI lần/phiên** (đây là chỗ dễ sai nhất): step 4 (trả lãi) nằm **sau** exit,
**trước** entry. Nếu chỉ đối chiếu ở step 4 thì dòng RA của phiên `s` (mua, step 5) và dòng VÀO của
phiên `s+1` (tiền bán về, step 0) **triệt tiêu nhau** ⇒ lô già không bao giờ bị ăn ⇒ phần tiền đã
tiêu vẫn được trả lãi. Mutation **M6** dựng đúng cảnh đó và **bị giết** (khe hở thật: 824.896 VND
thay vì > 240 triệu).

## 11.3 FIFO vs LIFO — quy ước tiêu tiền

FIFO (tiêu lô **CŨ** trước ⇒ giết lô đã già ⇒ **ÍT** lãi) = chân **PIN**, đúng chỉ đạo dispatch (luật
định trước, không chọn lại sau khi thấy số). LIFO (tiêu lô **MỚI** trước, giữ lô già ⇒ **NHIỀU** lãi)
= chân **độ nhạy**. Số đo xác nhận đúng chiều: tiền đủ tuổi/tiền nhàn rỗi = **51,3%** (FIFO) vs
**57,0%** (LIFO).

## 11.4 Cổng bắt buộc đã QUA

| Cổng | Kết quả |
|---|---|
| `rp_ctrl2` (`IDLE_CARRY_TIER=off`) | md5 **`4707bcbeb7e801d49a4a851ffd91d5e7`** = anchor R3, **byte-identical** ✅ |
| `rp_pin2` (chân `dep1m` cũ, chạy lại trên code MỚI) | md5 **`bcd0469f42c2f76937a6ebb10aae9b40`** = đúng số pin 27/09 ✅ |
| self-check 2 chân `_21s` | BAL + LAG: cash-flow identity **0 VND**, final NAV identity **0 VND** ✅ |
| borrow cost | **0 VND** cả 2 chân (max gross 1,000) |

Cổng thứ hai (`rp_pin2`) không được dispatch yêu cầu nhưng là cổng **mạnh hơn**: nó chứng minh việc
thêm sổ lô tuổi **không làm lệch** chân `dep1m` đã pin hôm trước, chứ không chỉ chân tắt.

## 11.5 Selfcheck riêng cho quy tắc tuổi tiền

`idle_cash_age_selfcheck.py` (mới) — **50 assertion PASS**, **11/11 mutation bị giết**.

- **T1–T6 UNIT** trên `idle_lots_reconcile` / `idle_lots_eligible`: tạo lô, bất biến `Σlô == cash`,
  biên tuổi 20/21/22, FIFO vs LIFO, tiền-về-rồi-đi-trong-1-phiên, margin xoá sổ, tiêu hết, thứ tự lạ.
- **T7–T10 END-TO-END** một lần `simulate()` thật trên panel 60 phiên giá cố định,
  `deposit_annual = 0,0252` ⇒ `r/252 = 1,0e-4` chẵn ⇒ **kiểm tay từng số**: lãi đầu tiên đúng ở
  index 21 (= phiên thứ 22), đúng `NAV₀ × r/252 = 100.000 VND`, và **phiên 23 = phiên 22** (chứng
  minh lãi không tự gộp vào gốc lô).
- **T11 round-trip** trên panel 2 mã dựng riêng để dòng RA/VÀO **bắc qua** mốc step-4 (mã BBB bán ở
  phiên 32, mã AAA mua ở phiên 31) — chính là cảnh chỉ reconcile-6z mới bắt được.

**Mutation (mỗi cái phải BỊ GIẾT):** M1 bỏ ngưỡng tuổi · M2 **truy lĩnh** · M3 đảo FIFO/LIFO ·
M4 off-by-one sớm 1 phiên · M5 off-by-one muộn 1 phiên · M6 bỏ reconcile cuối phiên (tiền ra/vào bị
net mất) · M7 không tăng tuổi đầu phiên · M8 lô sinh ra ở tuổi 1 · M9 lô mới chèn đầu sổ (phá thứ tự
tuổi) · M10 trả lãi trên TỔNG cash · M11 lãi được gộp vào lô đã đủ tuổi.

**2 mutation ứng viên bị loại vì CHỨNG MINH ĐƯỢC LÀ TƯƠNG ĐƯƠNG** (ghi ra trong file, không im lặng
bỏ): (E1) bỏ `max(target,0)` — với target âm vòng lặp vẫn tiêu đến khi sổ rỗng ⇒ `Σlô == 0 == max(t,0)`
ở cả hai bản; (E2) đảo thứ tự `reconcile` ↔ `eligible` ở step 4 — tương đương **CÓ ĐIỀU KIỆN**, và
điều kiện đó chính là reconcile-6z: giữa 6z(s−1) và step 4(s) **chỉ có dòng VÀO**, nên `cash ≥ Σlô`
luôn đúng và tập lô đủ tuổi y nhau. Bỏ 6z thì E2 **không còn** tương đương — và M6 đã chặn việc bỏ 6z.

**TZ**: assertion PASS dưới `Asia/Ho_Chi_Minh`, `UTC`, `America/New_York`, `Pacific/Kiritimati` và
`env -u TZ`; mutation **11/11 cũng bị giết dưới `TZ=UTC`**. Chạy bằng `$DNA_PYEXE`.

## 11.6 Số của chân `_21s`

| Đại lượng | pin0% (SÀN) | **21s FIFO = PIN** | 21s LIFO (độ nhạy) | pin1M (TRẦN) |
|---|---|---|---|---|
| CAGR | 23,37% | **25,24%** | 24,95% | 25,71% |
| Sharpe(252) | 1,88 | **2,03** | 2,00 | 2,06 |
| MaxDD | −14,6% | **−14,4%** | −14,4% | −14,0% |
| Calmar | 1,60 | **1,75** | 1,73 | 1,83 |
| Final NAV | 684,52B | **825,92B** | 802,45B | 864,86B |
| IS 2014-2019 | 20,00% | **21,39%** (Sh 1,92 / DD −14,4 / Cal 1,48) | 21,53% | 22,47% |
| OOS 2020+ | 26,50% | **28,85%** (Sh 2,10 / DD −13,4 / Cal 2,15) | 28,14% | 28,71% |
| **Bootstrap DD 5th-pct** | **−25,2%** | **−23,9%** | −24,2% | −23,6% |
| Bootstrap CAGR 5th-pct | 15,5% | **17,3%** | 17,0% | 17,8% |
| Bootstrap Sharpe 5th | 1,26 | **1,42** | 1,39 | 1,45 |
| P(DD < −30%) | 1,1% | **0,4%** | 0,7% | 0,5% |
| md5 ledger | `4707bcbe…` | **`d73f983d7d6a4b7028343be65c9ed7cf`** | `62baf89e2f6bad3887e5c969957676ce` | `bcd0469f…` |
| self-check | 0 VND | **0 VND** | 0 VND | 0 VND |

Bootstrap: `bootstrap_nav.py`, circular block **L=21, B=4000, seed=12345** (hằng số trong script, y
lệnh pin). **OOS > IS ở mọi chiều** trên cả 2 chân `_21s` ⇒ edge không rớt OOS.

> **Sharpe — 3 quy ước, không được trộn** (y như §4): cột trên là **cột engine in ra** (`sqrt(252)`),
> vì đó đúng quy ước sinh ra số 1,88 của anchor. `leg_metrics.py` (annualize theo thời gian lịch,
> 249,28 obs/năm) cho 2,02 / 1,99 / 1,87; bootstrap (log return) cho các số Sharpe 5th ở bảng.
> Số của record = **cột engine**.

### ✅ KIỂM TÍNH NHẤT QUÁN (cổng dispatch) — QUA
`23,37% < 25,24% < 25,71%` ✔ và `23,37% < 24,95% < 25,71%` ✔. Bootstrap DD 5th cũng nằm đúng giữa:
`−25,2% < −23,9% < −23,6%` ✔ và `−25,2% < −24,2% < −23,6%` ✔. **Không có đại lượng nào ra ngoài dải.**

### Tiền đủ tuổi và số phiên trả 0% (engine tự in, đã đối soát độc lập)

Số dưới đây là của **ledger thật** (`v23audit_BAL` / `v23audit_LAG`), KHÔNG gộp lượt `_base` —
BAL được `simulate()` **hai lần** mỗi run (lượt đầu dựng đường CAPIT trigger), gộp lại thì con số
không thuộc ledger nào cả.

| Chân | Sổ | tiền đủ tuổi / NAV_ref (mean) | median | tổng tiền / NAV_ref | **phiên trả 0% vì CHƯA ĐỦ TUỔI** | số lô tb |
|---|---|---|---|---|---|---|
| FIFO | BAL | **41,69%** | 45,55% | 54,84% | **606 / 2.979 = 20,3%** | 83,8 |
| FIFO | LAG | **18,03%** | **0,00%** | 47,86% | **1.676 / 2.919 = 57,4%** | 8,9 |
| LIFO | BAL | 44,41% | 51,33% | 54,26% | 390 / 3.015 = 12,9% | 29,0 |
| LIFO | LAG | 19,74% | 0,51% | 47,86% | 882 / 2.924 = 30,2% | 12,6 |

**Sổ LAG có median tiền đủ tuổi = 0,00%** — LAG quay vòng 25 phiên nên tiền của nó gần như không bao
giờ nằm im nổi 21 phiên. Đó chính là phần over-pay mà user muốn cắt: dưới quy ước `pin1M`, ~48% NAV
tiền nhàn rỗi của LAG được trả **đủ** lãi kỳ hạn 1 tháng.

**Đối soát độc lập** (không tin số engine tự in): tôi dựng lại tiền lãi từ **đồng nhất thức tiền**
của chính ledger — `interest(d) = cash(d) − cash(d−1) − Σ(TX net)` (đúng cái self-check engine dùng)
— rồi suy ngược `matured = interest / (rate/252)`. Kết quả khớp engine tới **0,01pp**: FIFO BAL
41,70% / LAG 18,03%; LIFO BAL 44,42% / LAG 19,75%. Chân control cho tổng lãi **0,000B** (đúng: không
trả đồng nào). Tổng lãi đã trả: pin1M **51,58B** · 21s FIFO **28,07B** (54,4% của pin1M) · 21s LIFO
**28,92B**.

## 11.7 ⚠️ TÁCH SỐ HỌC / ĐƯỜNG ĐI — CẢNH BÁO MỚI, KHÔNG CÓ Ở CHÂN pin1M

Overlay (`overlay_21s.py`, cùng công thức truy hồi với `w2b_overlay.py` đã được quant-skeptic
CONFIRMED 2026-09-27; tự kiểm chứng: nó tái lập Δ số học của pin1M = **+2,042pp** so với +2,052pp báo
cáo trước — lệch 0,010pp):

| Chân | Δ TỔNG (engine) | Δ SỐ HỌC | **Δ ĐƯỜNG ĐI** | % số học | tiền đủ tuổi / NAV |
|---|---|---|---|---|---|
| pin1M | +2,337pp | +2,042pp | +0,295pp *(dưới sàn 0,46)* | 87,4% | 46,16% |
| **21s FIFO (PIN)** | **+1,873pp** | **+1,116pp** | **+0,758pp** ⚠️ *(1,6× sàn 0,46)* | 59,6% | **24,57%** |
| 21s LIFO | +1,584pp | +1,191pp | +0,393pp *(dưới sàn)* | 75,2% | 26,29% |

**Ba kết luận, phải trích kèm nhau:**

1. **Chiều SỐ HỌC đúng và đơn điệu**: LIFO trả nhiều lãi hơn FIFO (+1,191 vs +1,116pp), khớp đúng
   với tiền đủ tuổi 57,0% vs 51,3%. Quy ước hoạt động như thiết kế.
2. **Thứ tự CAGR engine thì ĐẢO** (FIFO 25,24 > LIFO 24,95) hoàn toàn vì phần đường đi
   (0,758 vs 0,393pp). Khoảng cách FIFO/LIFO = **0,289pp < sàn nhiễu W2b 0,46pp** ⇒ theo đúng chỉ
   đạo dispatch: **đây là BẤT ĐỊNH QUY ƯỚC, không phải kết quả**. Engine **không xếp hạng được**
   fifo vs lifo. Pin FIFO vì đó là **luật định trước** (và là quy ước thận trọng về CARRY), không vì
   nó cho số cao hơn.
3. **Phần đường đi của chính chân PIN (0,758pp) VƯỢT sàn nhiễu 0,46pp** — điều KHÔNG xảy ra ở pin1M
   (0,295pp). Ở mức 1,6σ thì nó **vẫn không có ý nghĩa thống kê**, nhưng nó không còn nằm gọn trong
   sàn như chân pin1M ⇒ **số 25,24% "bẩn" hơn số 25,71%.** Cách đọc phòng thủ:

   | Cách đọc | CAGR | Vị trí trong dải [23,37 ; 25,71] |
   |---|---|---|
   | **SỐ HỌC** (chỉ hiệu ứng quy ước) | **24,49%** | **47,8%** |
   | ENGINE (số của record) | 25,24% | 80,1% |

   Vị trí **47,8%** theo số học khớp gần khít với **51,3%** tiền đủ tuổi/tiền nhàn rỗi (lệch 3,5pp)
   ⇒ cách đọc số học **nhất quán nội tại** với quy ước. 32,3pp vị-trí còn lại của cách đọc engine là
   **đường đi**, không phải quy ước. Ai cần một con số để suy luận về hiệu ứng CỦA QUY ƯỚC thì dùng
   **24,49%**; số của record (tái lập được từ ledger) là **25,24%**.

## 11.8 Lệnh tái lập

```bash
R=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/repin_dep1m_20260928/run_leg.sh
$R rp_ctrl2   BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off
$R rp_pin2    BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m
$R rp_21sfifo BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m \
              IDLE_CARRY_MIN_AGE=21 IDLE_CARRY_AGE_ORDER=fifo
$R rp_21slifo BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m \
              IDLE_CARRY_MIN_AGE=21 IDLE_CARRY_AGE_ORDER=lifo
# selfcheck + bootstrap + overlay
cd .../wt-repin-dep1m-2809/WorkingClaude && $DNA_PYEXE idle_cash_age_selfcheck.py --mutations
cd .../wt-repin-dep1m-2809/WorkingClaude && $DNA_PYEXE idle_cash_age_selfcheck.py --all-tz
cd /home/trido/thanhdt/WorkingClaude && $DNA_PYEXE bootstrap_nav.py <4 ledger>
cd /home/trido/thanhdt/WorkingClaude && $DNA_PYEXE .../overlay_21s.py <ctrl.csv> <21s.csv> ...
```
Env cố định y §8 của báo cáo này (`NAV_TOTAL_B=50 ETF_LIQ=custompitg AUDIT_END=2026-06-19
BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1
BASKET_CA_SNAPSHOT=…corp_action_share_20260927.parquet TZ=Asia/Ho_Chi_Minh`, `$DNA_PYEXE`).

## 11.9 Giới hạn RIÊNG của chân `_21s` (cộng thêm §10, không thay thế)

1. **Δ đường đi 0,758pp vượt sàn nhiễu 0,46pp** ⇒ xem §11.7 điểm 3. Đây là giới hạn NẶNG NHẤT của
   chân này và là lý do phải công bố cả cách đọc số học 24,49%.
2. **Ngưỡng 21 phiên là quy ước, không phải phép đo.** Nó xấp xỉ "1 tháng giao dịch"; DNSE/ngân hàng
   tính kỳ hạn theo **ngày dương lịch** (30 ngày ≈ 20–22 phiên tuỳ tháng và ngày lễ). Chưa đo độ
   nhạy theo ngưỡng (14/21/30 phiên) — nếu cần thì đó là một họ chân mới, và mọi chân thêm vào đều
   làm **tăng N của DSR/PBO**.
3. **FIFO/LIFO không xếp hạng được** (0,289pp < 0,46pp). Quy ước tiêu tiền thật của một danh mục
   không phải FIFO cũng không phải LIFO — nó là bất kỳ thứ tự nào tuỳ lệnh; hai chân này là hai
   **cận**, không phải hai ứng viên.
4. Vẫn **KHÔNG mở lại** câu hỏi xếp hạng PHƯƠNG TIỆN park (§7 + §8 của báo cáo) — engine không có
   sức phân giải, và chân `_21s` làm phần đường đi **to hơn** chứ không nhỏ hơn.
5. CAGR thật ≈ CAGR backtest − 1,5% ⇒ 25,24% → ~**23,7%** (cách đọc số học 24,49% → ~**23,0%**).
