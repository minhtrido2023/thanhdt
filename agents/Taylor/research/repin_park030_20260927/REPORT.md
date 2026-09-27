# RE-PIN R3 @ park 0,30 + hậu kiểm rail — job `Taylor_20260927_085509`

Ngày 2026-09-27 (16:1x ICT). Main WorkingClaude @ `ae81bd47`. **Không đặt lệnh, không sửa 2 rail
Mike đã đổi.** Registry: `data/results_registry.md` mục **"2026-09-27 (quinquies)"** (tiêu đề dispatch
ghi "quater" nhưng mục đó đã tồn tại).

## 1. Đính chính nhãn registry (XÁC MINH BẰNG GIT)
- `git log -L 99,99:deploy_golive_dt5g_v4/golive_recommend_v23.py` → `48d6d4b5` (2026-08-04):
  `ETF_PARK {3: 0.7} → {3: 0.8}`. Trước đó `c9cc670c` tạo file với 0.7.
- `data/trading_rules.json` chỉ vào git từ `760268a4` (2026-09-09) và **đã là 0.8**; backup
  `data/trading_rules.json.bak_20260927_park30` = **0.8**; `_meta.changelog` = "v2.3 (2026-08-04):
  0.70 → 0.80".
- Pin R3 (mục quater) chạy `PARK_STATES=3:0.7` và gắn nhãn "(production)" ⇒ **SAI 54 ngày**
  (2026-08-04 → 2026-09-27). Đã ghi ĐÍNH CHÍNH ngay tại mục cũ (gạch nhãn, **không xoá số**) + §0
  của mục mới.

## 2. Pin mới — khớp KHÍT leg lưới
CAGR **23,43%** / Sharpe **1,88** / MaxDD **−14,4%** / Calmar **1,63** / NAV **688,77B** /
IS **20,07%** / OOS **26,56%** · self-check 0 VND (BAL+LAG) · borrow 0 VND.
Ledger md5 `ff0d3a37d2ba682ca9b1244b2e36125d` — **byte-identical** với `parkgrid_030` ⇒ lệch
**0,00pp** (< trần dừng 0,05pp). Recompute độc lập `extract_peryear.py` khớp.

## 3. Bootstrap + DSR/PBO
Bootstrap (LỊCH, L=21, B=4000, seed 12345): CAGR 5th **15,6%** (med 23,4%), MaxDD 5th **−25,1%**
(med −16,5%), Sharpe 5th 1,27; P(DD<−30%) = **1,0%**; stationary 15,4% / −24,8%.
Annex (manifest 68 file ghim): ann-SR **1,815**, DSR **1,0000** (N=68/120/200),
**PBO(68) = 0,2085 không đổi** (CSCV chạy trên họ trial, không phụ thuộc ledger R3).

## 4. Đường tiền live (read-only)
Xem registry (quinquies) §7. Tóm: SpaceX PARK **387,08 tr = 80,8% pool** (target@0,30 = 143,72 tr,
δ −243,36 tr, phiên 1 bán 218,93 tr/19 mã, còn 24,43 tr carry-over → 35,1%); ZaloPay PARK
**157,02 tr = 60,1%** (target 78,42 tr, phiên 1 bán 53,08 tr/15 mã, còn 25,52 tr → 39,8%).
Reconcile ✅ cả 2, `unverified=[]`, T+2 không chặn, day-cap không binding, ràng buộc thật = %ADV
per-name + lô 100cp ⇒ ~2 phiên/TK. **Nhưng rail bán còn 0,80 ⇒ hiện tại L1 trả
`BLOCKED_ALL_NAMES`/`NO_TRIM`, 0 lệnh.**

## 5. Rail thứ ba (việc cần người duyệt)
`mike/bin/compute_park_trim.py:170 PARK_TARGET_F1 = 0.80` **hardcode**; `grep` toàn repo: **0 code
path đọc `default_park_of_idle_pct`**. `park_trim_daily.sh` không truyền `--target`.
`compute_park_add.py` (P2) import cùng hằng số. ⇒ user chốt 30% hiện **chỉ áp cho đường MUA**.

## 6. Hồi quy + cổng cơ học đề xuất
4 selfcheck park PASS (100 / 80×4TZ / 21 / all). Mới: `park_rail_consistency_selfcheck.py`
(đích đề xuất `mike/bin/`) — `ast`, so 3 rail bằng GIÁ TRỊ, `rc=1` khi lệch, `rc=2` fail-closed khi
không đọc được. Trên cây live **rc=1** (R1 0.3 / R2 0.8 / R3 0.3); `--selftest` **6/6 mutation**
đúng kỳ vọng. Chưa wire vào `run_selfchecks.sh` (chờ duyệt).

## 7. Caveat
FAIL-C còn vô hiệu (`label_col=entry`, 583 dòng) ⇒ 23,43% vẫn đo trên nhãn look-ahead 25 phiên.
