# RE-PIN R3 ở KNOB LIVE park = 0, tiền nhàn rỗi theo lãi huy động 1 tháng Big-4 — job `Taylor_20261008_155435`

> **Phạm vi: PAPER + REGISTRY `.proposed`.** Không đổi `trading_rules.json`, không merge knob vào
> main, không pin vào `data/pinned_ledgers/`, không sửa `data/results_registry.md`.
> Cơ sở: user duyệt Nhánh 1, 08/10/2026 22:53 ICT. Park live = 0 từ 2026-10-01 10:26 ICT (user chốt:
> *"Park 0% chốt. Chỉ thay đổi khi lãi suất huy động có xu hướng hạ."*).

## 0. Kết quả chính

| | **`pin0%` @park0 — SÀN** | **`pin1M` @park0 — TRẦN** (quy ước user chọn cho egg) |
|---|---|---|
| CAGR | **22,12%** | **25,42%** |
| Sharpe(252) | 1,93 | 2,17 |
| MaxDD | −16,2% | −13,9% |
| Calmar | 1,36 | 1,84 |
| **Bootstrap DD 5th** | −23,9% *(số đo, KHÔNG làm neo — xem dưới)* | −21,5% |

- **Neo sizing DD: GIỮ −25,2%** (sửa sau quant-skeptic, xem §4). Lý do: luật park của user có điều kiện
  lãi suất ("chỉ thay đổi khi lãi suất huy động có xu hướng hạ") nên knob có thể quay lại 0,3. Neo phải
  phủ mọi mức park có thể xảy ra, tức lấy mức xấu hơn trong {0; 0,3} ở đầu sàn = −25,2%. Còn −23,9%
  chỉ là số đo của park 0, không phải neo.
- **A/B park 0 vs 0,3, cùng quy ước dep1m.** CAGR không phân biệt được: P(park0 cao hơn) = **0,40**,
  ΔCAGR −0,29pp. DD và Calmar nghiêng về park 0 (P = **0,79** / **0,72**) nhưng chưa đạt ngưỡng 0,90.
  Khoảng 60% độ nghiêng Calmar (E[ΔCalmar] 0,160 → 0,063) đến từ chênh lệch đường đi của engine. Chỉ giữ phần số học thì
  P(Calmar) còn **0,565**, gần tung đồng xu.
  ⇒ Dữ liệu **không phản bác** quyết định park 0, nhưng cũng **không chứng minh** nó tốt hơn. Đây vẫn
  là lựa chọn theo khẩu vị rủi ro.
- Khi tiền nhàn rỗi được trả lãi 1M, cái giá CAGR của việc không park giảm từ −1,25pp (carry 0%)
  xuống −0,29pp. Phần giảm này gồm hai mảnh:
  - +0,46pp **số học**: park 0 để nhàn rỗi 57,6% NAV so với 46,4% ở park 0,3, phần chênh được hưởng
    ~3,5%/năm.
  - +0,50pp **đường đi**.

## 1. Cổng bắt buộc — chân CONTROL ✅ (chạy trước, cùng snapshot/env/`$DNA_PYEXE`/threads=1)

| Chân | Lệnh (ngoài env cố định của `run_leg.sh`) | md5 ledger | Kỳ vọng | Kết quả |
|---|---|---|---|---|
| `c_p30_off` | `PARK_STATES=3:0.3 IDLE_CARRY_TIER=off` | `4707bcbeb7e801d49a4a851ffd91d5e7` | `4707bcbe…` (anchor sexies) | **BYTE-IDENTICAL** |
| `c_p30_1m` | `PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m` | `bcd0469f42c2f76937a6ebb10aae9b40` | `bcd0469f…` (pin1M septies) | **BYTE-IDENTICAL** |
| `m_p30` (thêm) | như `c_p30_off`, nhưng chạy **code MAIN canonical** | `4707bcbeb7e801d49a4a851ffd91d5e7` | `4707bcbe…` | **BYTE-IDENTICAL** |

`run_leg.sh` = bản copy của `repin_dep1m_20260928/run_leg.sh`, chỉ khác dòng comment và `OUT`
(đã `diff`). `run_leg_main.sh` chỉ khác `SRC` (cây main), dùng cho chân kiểm lệch.

### 1.1 Worktree knob so với main — lệch gì, có ảnh hưởng không

- Dispatch ghi commit `d3c37631`. HEAD worktree hiện là **`f66dab18`**: thêm 3 commit (knob `_21s`
  `IDLE_CARRY_MIN_AGE`, một commit chỉ sửa comment, knob `IDLE_CARRY_PAY_MODE`). Hai knob mặc định
  tắt (`MIN_AGE=0`, `PAY_MODE=daily`). Hai control ở trên tái lập byte-identical trên chính HEAD này.
- Nhánh rẽ từ `2b2f6a28`. Main có thêm merge sau đó, sửa **5 file trong closure import tĩnh** của
  engine:

  | File | Thay đổi trên main |
  |---|---|
  | `pt_v23_audit_2014.py` | WORKDIR override + cảnh báo; tag `_etfcreatpit` chỉ khi `ETF_LIQ=creation`; LAG forensic fail-closed |
  | `custom_basket.py` | `forensic_flags.csv` fail-closed + fallback về cây canonical |
  | `deposit_rate_vn.py` | Overlay CCTG, display-only |
  | `dcf_valuation.py` | Sửa nhỏ |
  | `idle_rate_proxy.py` | +181 dòng; vẫn **không có** tier dep1m |

- **Lệch quan sát được:** khi chạy từ worktree, log in `[forensic exclude] none (No such file
  …/wt-repin-dep1m-2809/WorkingClaude/data/forensic_flags.csv)`. Code main tìm được file canonical
  và loại 8 mã (KSF VVS PC1 HHS L40 KLB DIG BFC). Cả 8 cờ đều có **ngày 2026-06-20, sau AUDIT_END
  2026-06-19**, nên lệch này trơ trong cửa sổ đo.
- **Bằng chứng:** chân `m_p30` chạy code main ra md5 `4707bcbe` (byte-identical). Riêng tên file
  khác (main không gắn `_etfcreatpit`). Chân `m_p0` (park 0, carry off, code main) cũng byte-identical — xem §1.2.
- ⇒ Với cấu hình này, phần worktree lệch main **không đổi một byte output**. Knob carry vẫn chỉ có
  trên branch `research/repin-dep1m-2709`, chưa merge — đúng ranh giới.

### 1.2 Chân `m_p0`
`m_p0` = `PARK_STATES=3:0.0`, carry off, chạy trên **code MAIN canonical**. Kết quả: md5
**`537e349b5589408c994f8aceafeb9a39`**, **BYTE-IDENTICAL** với `p0_off` chạy từ worktree. Chỉ khác tên
file: main không gắn `_etfcreatpit`.
- Main tìm thấy `data/forensic_flags.csv` và loại 8 mã từ ngày 2026-06-20.
- Self-check 0 VND.

⇒ Ở **cả hai mức park** đã chứng minh: phần lệch worktree↔main không đổi một byte output. Phần chưa
kiểm được trên main là knob carry dep1m, vì main không có knob này.

## 2. Bốn chân (cửa sổ 2014-01-02 → 2026-06-19, 12,46 năm, NAV 50B, `AUDIT_END=2026-06-19`)

CAGR, Sharpe(252), MaxDD, Calmar, NAV là số engine tự in. IS/OOS lấy từ `leg_metrics.py`: annualize
theo thời gian lịch, Sharpe trên simple return.

| Chân | CAGR | Sharpe(252) | MaxDD | Calmar | Final NAV | IS 2014-19 | OOS 2020+ | md5 |
|---|---|---|---|---|---|---|---|---|
| `c_p30_off` (pin0% @0,3) | 23,37% | 1,88 | −14,6% | 1,60 | 684,52B | 20,00% | 26,50% | `4707bcbe…` |
| `c_p30_1m` (pin1M @0,3) | 25,71% | 2,06 | −14,0% | 1,83 | 864,86B | 22,47% | 28,71% | `bcd0469f…` |
| **`p0_off` (pin0% @0 — SÀN)** | **22,12%** | 1,93 | **−16,2%** | 1,36 | 603,06B | 20,06% | 23,98% | `537e349b5589408c994f8aceafeb9a39` |
| **`p0_1m` (pin1M @0 — TRẦN)** | **25,42%** | 2,17 | **−13,9%** | 1,84 | 840,62B | 23,21% | 27,43% | `a6ba34d83a4d374a73293d897c0b43d9` |

Walk-forward chi tiết (`logs/leg_metrics.log`):

| Chân | Đoạn | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|
| `p0_off` | IS | 20,06% | 2,01 | −12,5% | 1,60 |
| `p0_off` | OOS | 23,98% | 1,87 | −15,6% | 1,54 |
| `p0_1m` | IS | 23,21% | 2,29 | −12,8% | 1,81 |
| `p0_1m` | OOS | 27,43% | 2,09 | −13,9% | 1,98 |

CAGR OOS cao hơn IS ở cả hai chân park 0 ⇒ edge không rớt OOS. Riêng `p0_off`: Sharpe và Calmar
OOS thấp hơn IS một chút, DD OOS sâu hơn. Đợt sụt lớn nhất là 2019-05 → 2020-03-24.

**Self-check:** cả 4 chân đều ra `[selfcheck BAL]` và `[selfcheck LAG]` với cash-flow identity
**0 VND** và final NAV identity **0 VND**. Borrow cost = 0 VND.

**Tính lại độc lập:** `extract_peryear.py` (`logs/extract_peryear.log`) khớp FULL/IS/OOS của cả 4
chân.

**Carry:** tier dep1m, offset −2,525pp. Phủ 89 tháng số thật, 53 tháng dựng lại, 8 tháng
forward-fill. Mean 3,501%/năm, min 1,600%, max 4,975%. Giá trị cuối cửa sổ 2,100%/năm. Có **0
phiên** bị trả 0% (engine tự in).

**Theo năm** (gốc = phiên đầu năm, khối `ANNUAL` của engine):

| Năm | p30_off | p30_1m | p0_off | **p0_1m** | p0_1m − p30_1m |
|---|---|---|---|---|---|
| 2014 | +50,44 | +54,93 | +54,17 | +59,31 | +4,38 |
| 2015 | +18,96 | +21,61 | +19,43 | +22,86 | +1,25 |
| 2016 | +10,56 | +12,80 | +10,37 | +12,63 | −0,17 |
| 2017 | +16,86 | +19,10 | +10,55 | +13,21 | **−5,89** |
| 2018 | +21,28 | +23,62 | +26,67 | +29,98 | +6,36 |
| 2019 | +4,72 | +5,95 | +2,79 | +5,23 | −0,72 |
| 2020 | +22,03 | +25,57 | +22,09 | +25,09 | −0,48 |
| 2021 | +110,44 | +105,74 | +96,78 | +103,81 | −1,93 |
| 2022 | −2,32 | −3,10 | −0,50 | **+1,92** | +5,02 |
| 2023 | +16,68 | +19,52 | +15,27 | +19,38 | −0,14 |
| 2024 | +19,89 | +22,20 | +17,35 | +19,17 | −3,03 |
| 2025 | +30,58 | +37,96 | +25,26 | +30,96 | **−7,00** |
| 2026 (½) | −2,28 | −1,24 | −2,89 | −3,25 | −2,01 |

So với park 0,3 (cùng dep1m), park 0 **thắng 4 năm, thua 9 năm**:
- Thắng: 2014, 2015, 2018, 2022. 2018 và 2022 là hai năm VNINDEX giảm.
- Thua đậm: 2017 và 2025, hai năm bull mạnh (VNINDEX +46%, +41%).

Đúng hình dạng của việc giảm phơi nhiễm: đánh đổi upside bull lấy đáy nông hơn. Không có dấu hiệu
alpha.

## 3. Tách SỐ HỌC / ĐƯỜNG ĐI (không lặp lỗi W2)

Overlay carry cộng lên **chính đường NAV carry-0%** của từng park (`w2b_overlay.overlay`, đã
quant-skeptic CONFIRMED 2026-09-27). Engine không được định tuyến lại lệnh.

| Park | Tiền nhàn rỗi TB (% NAV) | Δ TỔNG (engine) | Δ SỐ HỌC (overlay) | Δ ĐƯỜNG ĐI | % số học |
|---|---|---|---|---|---|
| 0,3 | 46,4% | +2,337pp | +2,052pp | +0,285pp | 87,8% |
| **0** | **57,6%** | **+3,299pp** | **+2,511pp** | **+0,788pp** | 76,1% |

Dòng park 0,3 tái lập đúng septies §7 (2,337 / 2,052 / 0,285).

**Đọc đúng:**
- Chênh **pin0% → pin1M @park0 = +3,30pp** **KHÔNG** có nghĩa hệ tốt lên. 2,51pp là số học thuần:
  57,6% NAV nhàn rỗi được trả ~3,5%/năm.
- ⚠️ **Phần đường đi ở park 0 = +0,79pp, VƯỢT sàn nhiễu W2b 0,46pp.** Sàn đó đo trên chân CÓ park;
  chưa có sàn đo cho chân park 0. Không có cơ chế nào khiến carry làm quyết định giao dịch tốt lên —
  carry chỉ cộng tiền. Kênh duy nhất là NAV lớn hơn ⇒ size lệnh, lô và trần ADV khác ⇒ chuỗi lệnh rẽ
  nhánh. Vì vậy tôi xếp nó là **biến thiên đường đi chưa giải thích**: không phải edge, và cũng không
  chứng minh được là nhiễu theo sàn hiện có.
- ⚠️ **Hệ quả cho MaxDD:**

  | Chuỗi | MaxDD | Đợt sụt |
  |---|---|---|
  | `p0_off` | −16,2% | 2019-05-29 → 2020-03-24 |
  | overlay `p0_off` + carry 1M (số học) | −15,5% | cùng đáy 2020-03-24 |
  | engine `p0_1m` | −13,9% | 2020-02-13 → 2020-03-24 |

  Năm 2019 khác nhau (+5,23% vs +2,79%) là **carry số học**, không phải đường đi: 62,9% NAV nhàn rỗi ×
  4,42%/năm ≈ 2,8pp (quant-skeptic đính chính). Carry đó nâng đỉnh lên mốc 02/2020 nên đỉnh đợt sụt
  dời chỗ. Hiệu ứng đường đi thật là **độ sâu cú sập Covid** tính từ gần cùng đỉnh 02/2020: engine
  −13,85% vs overlay −15,48%.
  ⇒ Khoảng **1,6pp** trong MaxDD −13,9% của đầu trần là đường đi, không phải carry. Trích MaxDD
  pin1M@park0 thì phải kèm câu này.

## 4. Bootstrap — neo DD đo ĐÚNG knob live

`bootstrap_nav.py`: circular block L=21, B=4000, seed=12345, annualize theo lịch (249,3 obs/năm).

| | `c_p30_off` | `c_p30_1m` | **`p0_off` (SÀN)** | **`p0_1m` (TRẦN)** | overlay p0 (số học) |
|---|---|---|---|---|---|
| **DD 5th** | −25,2% | −23,6% | **−23,9%** | **−21,5%** | −22,6% |
| DD median | −16,4% | −15,6% | −15,5% | −14,1% | −14,7% |
| CAGR 5th | 15,5% | 17,8% | **14,9%** | **18,0%** | 17,3% |
| Sharpe 5th | 1,26 | 1,45 | 1,32 | 1,57 | — |
| P(DD < −30%) | 1,1% | 0,5% | **0,7%** | **0,1%** | 0,3% |
| P(DD < −40%) | 0,0% | 0,0% | 0,0% | 0,0% | — |

- Cột `p0_*`: `bootstrap_nav.py` chạy riêng (`logs/bootstrap_p0_*.log`).
- Cột `c_p30_*`: số septies; paired bootstrap trong `park0_ab.json` tái lập được: −25,2 / −23,56.
- Cột overlay: chỉ có trong paired bootstrap.
- Hai cách chạy khớp nhau: DD 5th của `p0_1m` = −21,46% (paired) / −21,5% (standalone).

**ĐỀ XUẤT NEO SIZING DD: GIỮ −25,2%** — đầu **SÀN** (`pin0%`) của mức park **xấu hơn** trong các mức
có thể chạy live. Bản nháp đầu đề xuất hạ xuống −23,9%; **quant-skeptic bác, tôi đồng ý** vì 3 lý do:
- Luật park của user có điều kiện lãi suất ⇒ knob có thể quay lại 0,3. Neo sizing phải phủ cả hai mức.
- Paired test **không** chứng minh park 0 sụt nông hơn ở quy ước sàn: P(MaxDD₀ tốt hơn) chỉ 0,68,
  5th của ΔMaxDD là −1,9pp. MaxDD thực tế ở sàn còn **sâu hơn** khi park 0: −16,2% vs −14,6%.
- Hạ neo dựa trên "park 0 rủi ro thấp hơn" = một câu "park 0 tốt hơn" ⇒ phải quay về họ ≥12 trial của
  park grid 09-27 (DSR/PBO), là việc báo cáo này không làm.

−23,9% vẫn là **số đo đúng** của park 0 ở đầu sàn, giữ lại để tham chiếu. Nó không phải neo.
- Đầu trần −21,5% càng **không** dùng làm neo vì hai lý do:
  - Luật yêu cầu đứng ở cận xấu.
  - Khoảng 1,1pp của nó là đường đi (§3). Overlay số học thuần ra −22,6%.
- Bootstrap chỉ đo bất định **lấy mẫu**, không mô hình đổi regime ⇒ bất định thật còn rộng hơn.

## 5. A/B quan trọng nhất: park 0 vs 0,3 dưới CÙNG quy ước idle = dep1m

**Phương pháp:** paired block bootstrap. Dùng **một** chuỗi block index chung cho mọi chân
(`paired_w2.boot`, cùng engine với `paired_v2.py` của park_fraction_grid_20260927), L=21, B=4000,
seed=12345. Chênh lệch dưới đây là park 0 trừ park 0,3.

| Quy ước | P(CAGR₀ > CAGR₃₀) | ΔCAGR TB [5;95] | P(MaxDD₀ tốt hơn) | ΔMaxDD TB [5;95] | P(Calmar₀ > Calmar₃₀) | E[Calmar] 0 vs 0,3 |
|---|---|---|---|---|---|---|
| **dep1m (engine)** | **0,40** | −0,29pp [−2,17; +1,66] | **0,79** | +1,58pp [−1,03; +5,14] | **0,72** | **1,854 vs 1,695** |
| dep1m chỉ số học (overlay) | 0,24 | −0,79pp [−2,63; +1,11] | 0,69 | +1,01pp [−1,62; +4,48] | 0,565 | 1,733 vs 1,670 |
| off (carry 0%) | 0,13 | −1,25pp [−3,06; +0,61] | 0,68 | +0,98pp [−1,90; +4,50] | 0,49 | 1,488 vs 1,474 |

Dòng `off` khớp kết luận park grid 2026-09-27 (P(Calmar) = 0,479, khác vintage) ⇒ phương pháp nhất
quán.

**Tách ΔCAGR thực tế dưới dep1m, −0,286pp (25,42 vs 25,71). Các mảnh cộng lại đúng bằng tổng:**

| Mảnh | pp | Nghĩa |
|---|---|---|
| Park 0 vs 0,3 khi carry 0% | **−1,248** | Không cầm rổ custom30V trong NEUTRAL ⇒ mất phần lợi nhuận của phương tiện, chủ yếu ở năm bull |
| Carry số học trên phần tiền KHÔNG park | **+0,459** | Park 0 để nhàn rỗi thêm ~11pp NAV (57,6% vs 46,4%), hưởng ~3,5%/năm |
| Phần dư đường đi | **+0,503** | ≈ đường đi p0 (+0,79) − đường đi p30 (+0,285); **nhỉnh hơn** sàn W2b 0,46pp ⇒ không loại được là nhiễu, cũng không có cơ chế |

**Phân rã độc lập theo năm (leave-years-out Calmar, dep1m):**

| Bỏ năm | Calmar park 0 | Calmar park 0,3 |
|---|---|---|
| FULL | 1,835 | 1,833 |
| 2018 | 1,792 | 1,972 |
| 2019+2020 | 2,148 | 1,982 |
| 2021 | 1,457 | 1,451 |
| 2022 | 1,997 | 2,033 |
| 2025 | 1,801 | 1,760 |

Thứ hạng **đổi chiều** tùy năm bị bỏ, và Calmar FULL thực tế gần **bằng nhau** (1,835 vs 1,833).

Walk-forward A/B (dep1m):

| Đoạn | ΔCAGR | MaxDD park 0 | MaxDD park 0,3 |
|---|---|---|---|
| IS | +0,74pp | −12,8% | −14,0% |
| OOS | −1,28pp | −13,9% | −13,0% |

Dấu đảo giữa IS và OOS ở **cả CAGR lẫn DD**.

### Trả lời câu hỏi của user

> *Khi tiền nhàn rỗi được trả lãi 1M Big-4, quyết định park 0% có được dữ liệu ủng hộ không, hay vẫn
> là sở thích rủi ro?*

**Vẫn là sở thích rủi ro (không phân biệt được), nhưng giờ là một lựa chọn RẺ.**
1. **CAGR:** không phân biệt được. P = 0,40, khoảng 90% của ΔCAGR là [−2,2; +1,7]pp và chứa 0. Ở
   carry 0% park 0 tốn −1,25pp (P = 0,13, nghiêng rõ về 0,3). Carry 1M thu hẹp cái giá đó còn
   −0,29pp. Phần thu hẹp chắc chắn là số học (+0,46pp); phần còn lại (+0,50pp) là đường đi.
2. **Rủi ro (DD/Calmar):** nghiêng về park 0. Đây là hướng đúng cơ học của việc giảm phơi nhiễm
   NEUTRAL. Nhưng P(DD tốt hơn) = 0,79 và P(Calmar) = 0,72 đều dưới 0,90. Bỏ phần đường đi thì
   P(Calmar) = 0,565, gần tung đồng xu. LYO đổi chiều, IS/OOS đổi dấu.
3. ⇒ **Dữ liệu không phản bác park 0 và không đòi quay lại 0,3**, nhưng cũng **không cho phép nói
   "park 0 tốt hơn"**. Lý do đúng để giữ park 0 vẫn là lý do user đã nêu: khẩu vị rủi ro và bối cảnh
   lãi suất. Không phải backtest.
4. Điều kiện user đặt ra ("chỉ đổi khi lãi suất huy động có xu hướng hạ") là luật có **điều kiện
   theo lãi suất**. Backtest này **không điều kiện**, tức trung bình trên cả cửa sổ, nên nó **không
   kiểm định** luật đó. Có một hàm ý số học: lợi thế carry của park 0 tỉ lệ thuận với mức lãi suất.
   Lãi 1M Big-4 cuối cửa sổ là 2,10%/năm, thấp hơn mức TB 3,50% ⇒ ở mặt bằng lãi hiện tại, mảnh
   +0,46pp sẽ nhỏ hơn tương ứng (≈ ×0,6).

## 6. Kênh Trứng vàng (egg DNSE) — vì sao `pay_mode=daily` là mô hình đúng

- Tiền nhàn rỗi live nằm ở **Trứng vàng DNSE**: rút **trong ngày**, **không phạt rút trước hạn**.
  Lời phê "pin1M lạc quan vì rút trước hạn hưởng 0%" (septies §11, chân `_21s`) **không áp** cho
  kênh này. Lời phê đó đúng với tiền gửi kỳ hạn ngân hàng, không đúng với egg.
  ⇒ Các chân ở đây dùng `IDLE_CARRY_PAY_MODE=daily` (mặc định), **không gate tuổi tiền**
  (`IDLE_CARRY_MIN_AGE=0`). Mỗi phiên trả lãi cho số dư nhàn rỗi phiên trước ⇒ đúng cơ chế egg.
- **Mức lãi:** theo chỉ đạo user, **không** dùng 8,543%/năm net hiện tại của egg vì nó không luôn cao
  như vậy. Proxy là lãi huy động 1 tháng Big-4 cá nhân, point-in-time. Egg hiện trả cao hơn proxy
  nhiều ⇒ nếu egg giữ mức đó, thực tế còn tốt hơn đầu trần. Đây là spread sản phẩm, DNSE không cam
  kết, nên không đưa vào số pin.
- ⇒ Dưới hai giả định này, `pin1M`@park0 = **25,42%** là quy ước user chọn để mô tả kênh egg. Nhãn
  **vẫn là TRẦN** của dải 2 số theo CLAUDE.md. Lý do (quant-skeptic): lập luận egg chỉ trả lời lời phê
  "rút trước hạn = 0%". Nó không chứng minh rằng giai đoạn 2014-2019 đã có sản phẩm thanh khoản trong
  ngày trả đủ lãi kỳ hạn 1M. Muốn đổi nhãn thành "số chính" phải có user duyệt riêng — Mike trình. Đầu sàn `pin0%`@park0 = 22,12% vẫn được giữ làm cận xấu cho sizing.

## 7. Caveat — phải mang theo khi trích số

1. **53/150 tháng proxy là số DỰNG LẠI** (`sbv_low − 2,525pp`). FiinPro không có dữ liệu ≤2018-12,
   nguồn đã chết từ 28/09. Septies §6 cho thấy số pin không nhạy với offset p25–p75 (dải 0,18pp), và
   chân không bắc cầu 2019-03+ cho +2,00pp so với +2,34pp ⇒ đoạn dựng lại không bịa ra hiệu ứng.
   Riêng park 0, chân không-bắc-cầu **chưa chạy lại**.
2. **Đường đi +0,79pp ở park 0 vượt sàn W2b đo trên chân có park.** Sàn nhiễu cho chân park 0 chưa
   đo ⇒ MaxDD −13,9% và một phần Calmar của đầu trần có ~1,6pp là đường đi (§3).
3. **Không chạy DSR/PBO.** Lý do: **không có chọn lựa nào được làm trên dữ liệu này**. Knob park 0 do
   user chốt từ 2026-10-01, trước phép đo; quy ước dep1m chốt từ 2026-09-27. Đây là **một cấu hình đo
   dưới hai quy ước** + một **phép thử paired**, không phải tuyển config. Trục park đã có ≥12 trial
   (park grid 09-27) ⇒ mọi câu "park X là tốt nhất" phải qua DSR/PBO trên cả họ đó. Báo cáo này
   **không** đưa ra câu đó.
4. **quant-skeptic 2026-10-08: CONFIRMED-with-changes** (confidence medium). Đã áp đủ 5 sửa đổi:
   - giữ neo −25,2%;
   - giữ nhãn sàn/trần;
   - sửa quy nhân năm 2019;
   - điền §1.2;
   - cập nhật caveat này.

   Mọi số liệu đã được tái lập độc lập, khớp tuyệt đối. Script của skeptic: `qs_park0_recompute.py`.
   Rerun skeptic gợi ý, chưa làm:
   - chân sàn nhiễu W2b cho park 0;
   - chân không-bắc-cầu 2019-03+ ở park 0.
5. Proxy là lãi tiền gửi thị trường, **không phải** carry egg thật (§6).
6. Quy đổi thực tế theo CLAUDE.md: CAGR thật ≈ backtest − 1,5pp ⇒ 25,42% → **~23,9%** (trần),
   22,12% → ~20,6% (sàn).
7. Mọi so sánh phương tiện (custom30V vs khác) vẫn ở trạng thái W2b: engine không có sức phân giải.

## 8. Lệnh tái lập

```bash
N=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/repin_park0_dep1m_20261008
PY=/home/trido/thanhdt/wc_venv/bin/python     # $DNA_PYEXE
# code: worktree wt-repin-dep1m-2809, branch research/repin-dep1m-2709 @ f66dab18
# 1) CONTROL (phải byte-identical 4707bcbe / bcd0469f — lệch thì DỪNG)
$N/run_leg.sh c_p30_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=off
$N/run_leg.sh c_p30_1m  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3 IDLE_CARRY_TIER=dep1m
$N/run_leg_main.sh m_p30 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.3   # code MAIN
# 2) chân mới
$N/run_leg.sh p0_off BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=off
$N/run_leg.sh p0_1m  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER=dep1m
$N/run_leg_main.sh m_p0 BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0    # code MAIN
# 3) metric + IS/OOS + md5 + tính lại độc lập
cd /home/trido/thanhdt/WorkingClaude
$PY mike/agents/Taylor/research/repin_dep1m_20260928/leg_metrics.py <4 ledger>
$PY extract_peryear.py <ledger>
# 4) bootstrap neo DD
$PY bootstrap_nav.py <p0_off>;  $PY bootstrap_nav.py <p0_1m> <p0_off>
# 5) tách số học/đường đi + paired A/B + LYO
TZ=Asia/Ho_Chi_Minh $PY $N/park0_ab.py      # -> park0_ab.json
```

Ledger (trong `data/`, tên non-canonical theo §8):
- `p0_off`: `v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp_p0_off_univpit.csv`
- `p0_1m`: `v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_wtnamecap_advprice_etfcreatpit_exp_p0_1m_univpit_idledep1m.csv`

Registry đề xuất: `results_registry_park0_dep1m.proposed.md` (cùng thư mục).
