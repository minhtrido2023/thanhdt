# PREREG — BAL MAX_POS > 12 (job `Taylor_20261008_163222`)

Viết và commit **TRƯỚC** khi chạy bất kỳ chân treatment nào. Cổng 0 và 2 chân control đã chạy
xong (xem dưới). Chưa có số treatment nào tồn tại lúc commit file này.

## Câu hỏi
Khi LAG không có deal, nới trần số vị thế BAL (`MAX_POS_V11`, `pt_v23_audit_2014.py:731`) có lấp
được tiền nhàn rỗi bằng alpha thật không?

## Đã biết trước khi chạy treatment (cổng 0)
- **Cơ chế (đọc code).** BAL và LAG là hai sổ cái độc lập. Allocator chỉ trộn **chuỗi return** của
  hai sổ (`pt_v23_audit_2014.py` combination_note). Size một vị thế BAL = 10% NAV **sổ BAL**
  (`regime_size_overlay.FULL_SIZE`). Thiếu cash thì engine thu nhỏ size về `cash×0,95`, và bỏ lệnh
  nếu dưới 1 triệu VND (`simulate_holistic_nav.py` ~1188-1196).
  ⇒ Nới MAX_POS chỉ tiêu được **cash dư của chính sổ BAL**. Không chạm được cash LAG.
- **Số đo** (chân control, log `SLOT_AUDIT` khớp đúng engine):
  - Trần 12 có chặn ứng viên ở 80% phiên LAG-idle trong BULL và 77% trong EXBULL.
  - Ở NEUTRAL tỷ lệ này chỉ 1,6%, ở CRISIS 0,5%, ở BEAR 0%.
  - Cash BAL lúc bị chặn (BULL+EXBULL): trung bình 5,6% NAV BAL, trung vị 0,7%. 52% số phiên bị chặn
    có cash dưới 1%.
  - Cash LAG nhàn rỗi trong cùng các phiên này là 37–41% NAV gộp, nhưng knob không với tới được.
  - Có 430 episode ứng viên bị chặn và không bao giờ vào được. Excess 45 phiên so với VNI:
    - IS: −3,2%, so với +5,3% của các tên đã vào.
    - OOS: +1,6%, so với +4,0%.
    - Trung vị OOS −2,6%, hit 44%, so với 52% của tên đã vào.
    - Mean OOS dương là nhờ năm 2020 (+12,5%). Năm 2025 là −7,3%.

## Dự báo khai trước (để có thể bác bỏ)
|ΔCAGR FULL| ≤ 0,15pp ở mọi chân. Cận trên ước tính:
5,6% NAV BAL × ~45% tỷ trọng BAL × ~15,5% thời gian ở BULL/EXBULL × ~9%/năm excess.
Phép nhân này cho cỡ 0,03pp.

## Họ trial (N_trials = 2 cấu hình × 2 quy ước carry)
| Tag | Knob | Carry |
|---|---|---|
| `bmx_m16_off` | `BAL_MAX_POS=16` | off |
| `bmx_m20_off` | `BAL_MAX_POS=20` | off |
| `bmx_m16_1m` | `BAL_MAX_POS=16` | dep1m |
| `bmx_m20_1m` | `BAL_MAX_POS=20` | dep1m |

Mọi env còn lại giống hệt chân control: `run_leg.sh` + `BASKET_WT=namecap BASKET_SELECT=yieldcombo
PARK_STATES=3:0.0`. Park giữ 0. Knob áp **luôn luôn**, không theo state.

- **Đã bỏ biến thể "chỉ khi LAG idle ≥ ngưỡng"** (quyết trước khi thấy số treatment), vì hai lý do:
  1. Trần chỉ chặn ở BULL/EXBULL, mà ở đó LAG idle chiếm 79–87% số phiên. Biến thể có điều kiện vì
     vậy gần như trùng với "luôn luôn". Ngoài BULL/EXBULL thì trần gần như không chạm, nên điều kiện
     không đổi gì.
  2. Muốn làm biến thể này phải truyền lịch lệnh LAG sang `simulate()` của BAL. Đó là sửa lõi dùng
     chung (§23), không xứng với hiệu ứng tối đa kể trên.
- **Ngữ nghĩa knob.** `max_positions` còn quyết hàng đợi pending (`max_positions×3`), nên knob nới
  cả trần hàng đợi. Đây là một phần của "nới trần BAL", không phải trục riêng.

## Control (đã chạy, PASS)
- `bmx_ctl_off`: md5 `537e349b5589408c994f8aceafeb9a39`, byte-identical với pin p0_off.
- `bmx_ctl_1m`: md5 `a6ba34d83a4d374a73293d897c0b43d9`, byte-identical với pin p0_1m.
- Cả hai chạy trên code research `bb700ab6`, knob để mặc định 12 và **bật log `SLOT_AUDIT_LOG`**.
  Như vậy chứng minh cùng lúc rằng knob mặc định và phần log đều trơ (inertness).
- Self-check 0 VND trên cả 2 sổ.

## Ngưỡng GO (mọi điều kiện, áp riêng cho từng quy ước carry; kết luận chỉ GO nếu GO ở **cả** hai)
1. ΔCAGR > 0 ở **cả** IS 2014-19 lẫn OOS 2020+, so với control cùng carry.
2. Leave-one-year-out: bỏ bất kỳ 1 năm nào thì ΔCAGR FULL vẫn > 0. Ngoài ra ΔCAGR FULL không được
   rơi về ≤ 0 khi bỏ cặp năm 2020+2021.
3. Bootstrap DD 5th (`bootstrap_nav.py`, L=21, B=4000, seed=12345) không xấu hơn control quá
   1,0pp. Mốc control: off −23,9%, 1m −21,5%.
4. DSR ≥ 0,95 trên chuỗi excess ngày (treatment − control), với N_trials = 4.
   PBO không áp dụng vì số biến thể < 8.

Nếu hỏng bất kỳ điều kiện nào thì NO-GO. Nếu GO thì vẫn chỉ là ứng viên: phải qua quant-skeptic
(do Mike gọi), và capacity phải đạt ở 50B.

## Báo thêm
Size mỗi vị thế và %ADV ở NAV 1B (live) và 50B cho các vị thế mở thêm, so với vị thế 1–12.

## Ranh giới
Không đổi `trading_rules.json`, production hay main. Knob chỉ nằm trên branch
`research/bal-maxpos-lag-idle-20261009` (worktree `wt-balmaxpos-1009`). Registry chỉ ghi `.proposed`.
