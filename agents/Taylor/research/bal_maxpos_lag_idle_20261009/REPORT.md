# BAL giữ quá 12 vị thế khi LAG không có deal — job `Taylor_20261008_163222`

> **Phạm vi:** chỉ PAPER, knob nằm trên branch research. Không đổi `trading_rules.json`, production,
> hay main. Registry chỉ ghi ra file `.proposed`.
> Cơ sở: user duyệt Nhánh 2 lúc 08/10/2026 22:53 ICT. Mẫu số là R3 ở knob live park=0, pin 08/10.

## 0. Verdict: **NO-GO** theo PREREG — điều kiện 1, 2, 4 hỏng ở cả 4 chân, cả hai quy ước carry

**Không lấp được.** Nới trần BAL 12 → 16/20 **làm giảm** CAGR 1,1–2,1pp. Mức giảm đi cùng chiều ở
IS lẫn OOS, ở cả carry 0% (pin0%) và carry lãi 1M (pin1M). Hai lý do:

1. **Không với tới được cash LAG.** BAL và LAG là hai sổ cái độc lập. Allocator chỉ trộn **chuỗi
   return** của hai sổ. Tên thứ 13 trở đi chỉ tiêu được cash dư của chính sổ BAL: trung vị 0,7% NAV
   BAL ở thời điểm bị chặn. Trong khi đó 37–41% NAV gộp là cash LAG nằm yên ở sổ kia. Bằng chứng
   trực tiếp: NAV cuối của LAG là **426,8135B ở cả 6 chân**, không lệch một đồng.
2. **Ứng viên ngoài top-12 yếu hơn**, và nới trần làm hỏng đường đi của BAL. Cash BAL ở BULL chỉ
   giảm từ 7,3% xuống 4,3%, nghĩa là chỉ thêm ~3% NAV BAL được dùng. Nhưng tỷ lệ vị thế size dưới 5%
   tăng từ 14% lên 29%. Số lệnh STOP tăng từ 29 lên 51. Năm 2021, năm BAL mạnh nhất, giảm từ
   +122% xuống +84% (trần 16) và +65% (trần 20). Phản ứng liều–tác dụng đơn điệu: trần càng nới,
   thiệt càng nặng (§3).

**Áp vào NEUTRAL (trạng thái live 08/10):** không áp được. Ở NEUTRAL, BAL chỉ chạm trần ở 1,6% số
phiên LAG-idle, trung bình giữ 3 tên, cash 72%. Trần 12 không phải thứ đang giữ cash nhàn rỗi ở
NEUTRAL. Đây cũng là lý do BAL đang 0 mã hôm nay: thiếu tín hiệu, không phải hết slot.

## 1. Cổng 0 (rẻ, chạy trước): trần CÓ chạm, nhưng không phải nút thắt của tiền nhàn rỗi

**Nguồn số.**
- Phần A dựng lại từ ledger pin p0_off (`gate0_ledger.py`).
- Phần B lấy từ log `SLOT_AUDIT_LOG` của chính chân control (`gate0_slots.py`). Log này ghi lại
  **mọi** quyết định first-fill của BAL: `SLOT_BLOCK`, `CASH_SKIP`, `FILL_START`. Phần log đã được
  chứng minh trơ (§2).

**Theo trạng thái, chỉ tính các phiên LAG-idle** (LAG không có lệnh mua):

| State | Phiên LAG-idle | % phiên có ứng viên bị chặn bởi slot | Ứng viên bị chặn / phiên | Cash BAL lúc bị chặn (trung vị / p90, % NAV BAL) | Cash LAG nhàn rỗi (% NAV gộp) |
|---|---:|---:|---:|---:|---:|
| CRISIS | 395 | 0,5% | 11,5 | 12,5% / 22,4% | 24,2% |
| BEAR | 198 | 0% | – | – | 0% |
| NEUTRAL | 1.506 | 1,6% | 2,7 | 9,2% / 10,7% | 34,1% |
| **BULL** | 333 | **79,6%** | 7,5 | **0,5%** / 16,0% | 37,1% |
| **EXBULL** | 52 | **76,9%** | 10,6 | 7,1% / 17,8% | 40,6% |

- Gộp BULL+EXBULL: cash BAL lúc bị chặn trung bình 5,6%, trung vị 0,7%. **52% số phiên bị chặn có
  cash dưới 1% NAV BAL.**
- BAL vượt 12 tên được (trung bình 13,6 ở BULL) vì engine chỉ đếm vị thế ĐÃ HOÀN TẤT khi kiểm slot.
  Lệnh đang khớp dở không bị tính. Size mỗi tên = 10% NAV BAL, nên ~10 tên đã ăn hết cash. **Ở BULL,
  BAL vừa đầy slot vừa hết tiền.**
- **Chất lượng ứng viên bị chặn.** Dữ liệu được gộp thành *episode*: cùng mã bị chặn ở các phiên cách
  nhau ≤5 phiên tính là một. Có 531 episode, trong đó 430 không bao giờ vào được lệnh trong 20 phiên
  sau đó. Forward return tính từ giá Open ngày đáng lẽ khớp, tới Close sau 45 phiên (= `hold_days`
  của BAL). Excess tính so với VNI.

  | | N | Excess trung bình | Excess trung vị | Hit |
  |---|---:|---:|---:|---:|
  | Bị chặn, IS | 29 | −3,2% | −6,8% | 38% |
  | Bị chặn, OOS | 401 | +1,6% | −2,6% | 44% |
  | Đã vào, IS | 86 | +5,3% | −0,5% | 49% |
  | Đã vào, OOS | 305 | +4,0% | +0,8% | 52% |

  Excess trung bình OOS dương là nhờ năm 2020 (+12,5%, 60 episode). Năm 2025 là −7,3%.
- ⚠️ **Về N.** Các episode chồng thời gian, và các cửa sổ 45 phiên chồng lên nhau. Số quan sát độc
  lập thực tế là cỡ ~40 cụm ngày ở IS và ~300 ở OOS. Phần chất lượng này chỉ cho **hướng** (pha loãng),
  không có p-value. Kết luận cuối cùng dựa vào backtest NAV ở §3.
- **Vì sao vẫn chạy treatment dù cổng 0 đã gợi ý dừng.** Điều kiện dừng ghi trong dispatch là "gần như
  không có ứng viên bị chặn". Điều kiện này không thoả: ở BULL có rất nhiều ứng viên bị chặn. Bốn chân
  treatment rẻ (~8 phút chạy song song) và cho con số dứt khoát.

## 2. Chân CONTROL ✅

| Chân | md5 | Kỳ vọng | Kết quả |
|---|---|---|---|
| `bmx_ctl_off` | `537e349b5589408c994f8aceafeb9a39` | pin p0_off | **BYTE-IDENTICAL** |
| `bmx_ctl_1m` | `a6ba34d83a4d374a73293d897c0b43d9` | pin p0_1m | **BYTE-IDENTICAL** |

- Code chạy là `research/bal-maxpos-lag-idle-20261009` @ **`bb700ab6`**, rẽ từ worktree repin `f66dab18`.
  Đó là nơi duy nhất có knob `IDLE_CARRY_TIER`.
- Hai control chạy với knob `BAL_MAX_POS` để mặc định (12) **và bật** `SLOT_AUDIT_LOG`. Như vậy chứng
  minh cùng lúc rằng knob mặc định và phần log đều trơ.
- Self-check 0 VND trên cả 2 sổ, ở mọi chân (6/6).
- `run_leg.sh` là bản copy của `repin_park0_dep1m_20261008/run_leg.sh`, chỉ đổi `SRC` và `OUT`
  (đã `diff`). Env cố định: `BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0`, NAV 50B,
  `AUDIT_END=2026-06-19`, snapshot `bq_cache_asof20260729_postrestate`, `$DNA_PYEXE`, threads=1.

## 3. Bốn chân treatment (cửa sổ 2014-01-02 → 2026-06-19)

| Chân | md5 | CAGR | ΔFULL | ΔIS | ΔOOS | Δ khi bỏ 2020+21 | LOO năm: Δ tốt nhất (bỏ 2021) | Sharpe (Δ) | MaxDD (Δ) | Boot DD 5th (ctl) | DSR excess |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `bmx_m16_off` | `f9f079ab…` | 20,93% | **−1,19pp** | −0,36 | −1,98 | −0,38 | −0,47 | 1,83 (−0,10) | −16,5% (−0,3) | −24,8% (−23,9) | 0,003 |
| `bmx_m20_off` | `5a99b18d…` | 20,57% | **−1,55pp** | −0,50 | −2,54 | −0,42 | −0,43 | 1,81 (−0,11) | −16,6% (−0,3) | −25,0% (−23,9) | 0,001 |
| `bmx_m16_1m` | `98641c49…` | 24,28% | **−1,14pp** | −0,31 | −1,92 | −0,11 | −0,23 | 2,11 (−0,05) | −14,2% (−0,3) | −21,4% (−21,5) | 0,013 |
| `bmx_m20_1m` | `e0100f45…` | 23,33% | **−2,09pp** | −0,50 | −3,61 | −0,69 | −0,77 | 2,04 (−0,12) | −14,4% (−0,5) | −22,2% (−21,5) | 0,000 |

Control: pin0% 22,12%, pin1M 25,42%.

**Chấm theo PREREG**, áp riêng cho từng chân:

| Điều kiện | Kết quả |
|---|---|
| 1. ΔIS > 0 và ΔOOS > 0 | ❌ cả 4 chân |
| 2. Leave-one-year-out vẫn dương | ❌ bỏ bất kỳ năm nào Δ vẫn âm (tốt nhất là bỏ 2021: −0,23…−0,77pp); bỏ 2020+21 vẫn âm |
| 3. Boot DD 5th không xấu hơn control quá 1,0pp | 3/4 đạt: `m16_off` −0,9pp, `m16_1m` +0,1pp, `m20_1m` −0,7pp. ❌ `m20_off` −1,1pp |
| 4. DSR ≥ 0,95 | ❌ DSR ≤ 0,013 ở cả 4 chân |

⇒ **NO-GO** (điều kiện 1, 2, 4 hỏng ở cả 4 chân). N_trials = 4. PBO không áp dụng vì số biến thể < 8 và không có biến thể nào được khuyến
nghị.

- **Mức thiệt theo năm** (Δ return năm, pp): 2021 lần lượt −14,4 / −21,7 / −17,9 / −26,0. Năm 2025
  cũng âm cả 4 chân (−1,0 / −0,6 / −4,4 / −6,8). Các năm 2015-17 và 2019 gần 0. Năm 2022 hơi dương.
  Bỏ 2021 (LOO) thì Δ vẫn âm, nên hại không chỉ do một năm.
- **Dự báo khai trước bị bác.** PREREG dự báo |ΔCAGR| ≤ 0,15pp, dựa trên giả định tiền thêm chỉ là cash
  dư ~5,6%. Phần cash đúng là ít (BULL: 7,3% → 4,3%). Cái dự báo bỏ sót là **hiệu ứng đường đi**:
  trần cao hơn thì hàng đợi pending dài hơn (`max_positions×3`: 36 → 48/60) và slot rộng hơn. Khi một
  tên cũ hết hạn và nhả cash, cash đó chảy vào ứng viên xếp sau, tức yếu hơn, thay vì chờ tín hiệu mạnh
  mới. Thêm vào đó nhiều vị thế "vụn" (size dưới 5%) chiếm slot. Tôi ghi rõ điều này thay vì sửa lại
  dự báo cho khớp.
- **Cơ chế, đo từ `diag_mech.py`:**

  | | ctl | m16 | m20 |
  |---|---:|---:|---:|
  | Số lệnh BAL bắt đầu | 396 | 446 | 470 |
  | Tỷ lệ vị thế size dưới 5% | 14% | 22% | 29% |
  | Số lệnh STOP | 29 | 40 | 51 |
  | BAL năm 2021 | +122% | +84% | +65% |

  Riêng năm 2021, lệnh DEEP_VALUE_RECOVERY tăng từ 58 lên 79/93. ⚠️ **BAL thực chất là sổ
  DVR/RE_BACKLOG**, không phải momentum. Trong toàn ledger chỉ có 29 dòng giao dịch MOMENTUM và 3 dòng
  MEGA. Câu "pha loãng alpha momentum" trong dispatch nên đọc là "pha loãng xếp hạng ưu tiên tier của
  DVR/RE_BACKLOG".

**Capacity** (`capacity.py`, chân m20_off). Size lúc bắt đầu lệnh, so với trung vị giá trị giao dịch
20 phiên (Price×Volume, raw PIT):

| Mức NAV | Slot 1–12: size trung vị | Slot 1–12: %ADV (trung vị / p90) | Slot 13+: size trung vị | Slot 13+: %ADV (trung vị / p90) |
|---|---:|---:|---:|---:|
| 50B ban đầu | 4,5B | 43% / 324% | 3,5B | 22% / 251% |
| 1B live | 0,09B | 0,9% / 6,5% | 0,07B | 0,45% / 5,0% |

- Ở NAV live, capacity không phải vấn đề.
- Ở 50B thì các tên trong top-12 vốn đã vượt ADV. Engine xử lý bằng cách khớp rải nhiều phiên (ramp),
  có trần thanh khoản.
- Size ở đây tính theo NAV tại thời điểm vào lệnh. NAV tăng dần từ 50B lên ~600B, nên đây là ước lượng
  thô.

## 4. Caveat

- **Chỉ đo được một kiểu "lấp tiền nhàn rỗi bằng BAL": nới trần trong cùng một sổ.** Cách duy nhất để
  thật sự dùng cash LAG là đổi allocator: hạ `w_LAG` (dời vốn sang BAL) khi LAG cạn tín hiệu. Đó là
  thiết kế khác hẳn, và cổng 0 đã cho thấy nó dễ thất bại vì hai lý do:
  - Ở BULL, BAL đã hết cash và hết slot. Vốn dời sang sẽ rơi vào chính các ứng viên ngoài top-12, mà
    nhóm này yếu hơn: excess trung vị OOS −2,6%, hit 44%.
  - Ứng viên bị chặn ở OOS vẫn có excess trung bình +1,6%/45 phiên so với VNI, nhưng con số này do 2020
    gánh.
  ⇒ **Không đề xuất mở hướng allocator-động**, trừ khi user muốn. Nếu làm thì phải dùng PREREG mới.
- **Biến thể "chỉ khi LAG idle ≥ ngưỡng" đã bị bỏ trong PREREG, trước khi có số.** Lý do: ở BULL/EXBULL,
  LAG idle chiếm 79–87% số phiên, và trần chỉ chạm ở hai state này. Biến thể có điều kiện vì vậy sẽ hại
  gần bằng biến thể "luôn luôn".
- **Thứ tự commit.** PREREG được commit `7f7ff730` lúc 23:46:19. 4 chân treatment khởi động vài giây
  trước đó: lần commit đầu bị `git add` từ chối vì `logs/` nằm trong `.gitignore`, trong khi lệnh
  chạy nối sau đã khởi động. Lúc commit **chưa có output treatment nào**: CSV đầu tiên xuất hiện sau
  khoảng 7 phút, và tôi đã kiểm `ls data/*exp_bmx_m*` = 0 ngay lúc commit. Nội dung PREREG không sửa
  sau đó.
- Log `SLOT_AUDIT` dùng `atexit`. Đây là instrumentation chỉ có ở branch research, không merge.
- quant-skeptic: chưa gọi, theo dispatch (Mike gọi). Finding này là "giữ nguyên production" nên không
  bắt buộc qua cổng skeptic. Nên gọi nếu có ý định trích dẫn nó làm lý do bác hướng allocator.

## 5. Tái lập
```bash
R=mike/agents/Taylor/research/bal_maxpos_lag_idle_20261009; C="BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0"
$R/run_leg.sh bmx_ctl_off $C IDLE_CARRY_TIER=off   SLOT_AUDIT_LOG=$R/slot_audit_ctl_off.csv
$R/run_leg.sh bmx_m20_1m  $C IDLE_CARRY_TIER=dep1m BAL_MAX_POS=20 SLOT_AUDIT_LOG=$R/slot_audit_m20_1m.csv   # (tương tự m16/m20 × off/dep1m)
$DNA_PYEXE $R/gate0_ledger.py; $DNA_PYEXE $R/gate0_slots.py $R/slot_audit_ctl_off.csv <ctl_off ledger>
$DNA_PYEXE $R/evaluate.py; $DNA_PYEXE $R/diag_mech.py; $DNA_PYEXE $R/capacity.py $R/slot_audit_m20_off.csv
$DNA_PYEXE bootstrap_nav.py <ledger>     # từ WorkingClaude/
```
Code: worktree `mike/agents/Taylor/wt-balmaxpos-1009`, branch `research/bal-maxpos-lag-idle-20261009`
@ `bb700ab6`. Ledger nằm ở `data/*_exp_bmx_*_univpit*.csv`, tên không phải canonical.
