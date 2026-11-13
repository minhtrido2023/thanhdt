# Luồng A6: một cây code cho cả dải, small-NAV, DD5 theo dải, ADV sau sự kiện cổ phiếu

Job `Taylor_20261113_075112`. ⚠️ PAPER. **KHÔNG đổi production, `trading_rules.json` hay neo sizing. KHÔNG merge.** Chưa qua quant-skeptic.
Mọi số đo trong job này; log `logs/`, ledger `ledgers/`, script ở thư mục này.

## 0. Kết luận

1. **Việc 1 — xong.** Nhánh `research/live-gap-A6-carry-20261113` @ `262c117c3` = main `7f25febc1` + 7 commit carry (cherry-pick `-x`).
   Trên CÙNG cây: pin0% (mặc định `IDLE_CARRY_TIER` off) = `80f509ec` **trùng byte**; pin1M (`IDLE_CARRY_TIER=dep1m`) = `e2de0ac4` **trùng byte**. Self-check 0 VND 2/2.
   Selfcheck quét rộng 21 file × 3 TZ: mã thoát giống hệt main từng file (5 FAIL có sẵn ở cả hai nhánh, §1).
2. **Việc 2 — chênh ~4pp KHÔNG còn nguyên ở NAV nhỏ, nhưng DD5 tuyệt đối sâu hơn nhiều.**
   - Chênh DD5 ghép cặp (L3P − L1, 15 cấu hình bootstrap): **50B −4,11pp · 2B −1,28pp · 1B −1,58pp**.
   - Fill ảo vẫn tồn tại ở 1B (166 lệnh LAG, 26,9% vốn mua LAG của L1 — 156 lệnh có pit-ADV ≤0), nhưng tỉ trọng nhỏ hơn 50B (45,8%), vì ở 50B các lệnh thật bị trần ADV cắt còn fill ảo thì không.
   - **DD5 L3P ở NAV 1B: trung vị −32,75% [−33,34; −30,21]**, so với −27,30% ở 50B. L1 1B cũng −31,15%. CAGR 1B 27,04% (L3P) vs 22,97% (L1).
   - ⇒ Nếu neo sizing áp cho NAV live ~1 tỷ, engine 50B (cả neo cũ lẫn −29,09) có thể **quá nông**. Đây là câu hỏi mới cho user/skeptic, không phải kết luận.
3. **Việc 3 — −29,09% là cạnh dưới của dải, không phải tâm.** Seed 12345/L=21 là lần rút sâu nhất 15/15 ở neo, L3P park 0 và L3P park 0,3.
   | Ledger | DD5 trung vị [min; max] (15 cấu hình) |
   |---|---|
   | neo `4707bcbe` | −24,77 [−25,20; −23,55] |
   | L3P park 0 `80f509ec` | −27,30 [−27,89; −26,63] |
   | L3P park 0,3 `dc8910f8` | **−28,54 [−29,09; −27,99]** |
   | pin1M `e2de0ac4` | −24,59 [−24,97; −24,19] |
   Chênh ghép cặp so với neo: park 0,3 **−3,89 [−5,17; −3,37]**, park 0 −2,87 [−3,74; −2,33] ⇒ chênh bền, mức neo có bất định ~±0,6pp.
4. **Việc 4 — ADV thấp giả sau thưởng/cổ tức CP là thật nhưng nhỏ.** 3,4–4,3% (mã, ngày) mua LAG bị ảnh hưởng; adj/pit median 1,06, p95 1,49–1,57.
   Lệnh bị cap sai: **1,03% ở 1B, 3,79% ở 50B**; vốn mua bị cắt (cận trên) ≤0,69%. Không đủ đổi kết luận A5/A6.
   Phát hiện phụ: engine 1B có trần ADV ràng buộc ở 65,5% ngày mua LAG (ADV median 116 tr), trong khi live 0/48 lệnh — **lệch fidelity về tập mã LAG, chưa giải thích**.

## 1. Việc 1: nhánh carry

- Cherry-pick (thứ tự): `75fba8a9e` knob · `6bdd6924a` worktree isolation · `5a9d424ce` IDLE_CARRY_FLAT + META cash_identity · `d3c376310` tier dep1m · `aaed41eec` dep1m_21s · `568abc0e5` comment · `f66dab189` PAY_MODE=maturity.
  Một xung đột AA ở `idle_rate_proxy_selfcheck.py`: main chỉ có bản auto-backup `d775003a9` cũ hơn ⇒ lấy bản `d3c376310`.
- **Không đưa vào** (không cần cho carry, đều là knob research trơ): `bb700ab67` BAL_MAX_POS/SLOT_AUDIT, `2c69cfa62`/`33f005209` BAL_BUY_BLOCK. Phần còn lại của `e9a9aed1a` (LIQ default, PT_WORKDIR, mergesort, LAG_ADV_SRC) main đã có.
- `git diff --stat main 262c117c3`: 5 file, +1192/−10 — `idle_cash_age_selfcheck.py` +551 (mới), `idle_rate_proxy.py` 84, `idle_rate_proxy_selfcheck.py` 154, `pt_v23_audit_2014.py` 208, `simulate_holistic_nav.py` 205.
- Lệnh: `run_leg.sh V1_pin0 adj` / `run_leg.sh V1_pin1M adj IDLE_CARRY_TIER=dep1m` (env cố định = A5; sandbox `sb/c_{adj,vint}` symlink tới worktree sạch + data canonical + LAG adj v2/vintage; `LAG_MD5` trùng A5).
- **Selfcheck (§23 lõi ⇒ quét rộng):** mọi `*selfcheck*.py` nhắc `simulate_holistic_nav|pt_v23_audit_2014|idle_rate_proxy` (21 file) × TZ {ICT, `env -u TZ`, America/New_York}, chạy ở sandbox nhánh mới và sandbox main (`logs/selfcheck_A6.log`, `logs/selfcheck_main.log`): mã thoát **giống hệt từng file**.
  - FAIL ở CẢ HAI nhánh: `basket_price_basis`, `failopen_failclosed`, `lag_rating_stale` (sandbox không phải git/thiếu data — chạy trong worktree thì PASS ở cả hai, `logs/selfcheck_fail_inworktree.log`); `edge_wlag_gate` (thiếu CSV pin R3 ở cả hai); `universe_pit_p2` (T1.LIVE, cả hai). ⇒ có sẵn, không do nhánh.
  - `idle_cash_age_selfcheck` (mới), `idle_rate_proxy_selfcheck` PASS 3 TZ.

## 2. Việc 2: small-NAV (park 0, pin0%, 1 cây code, self-check 0 VND 6/6)

| Chân | md5 | CAGR | MaxDD | IS / OOS | DD5 trung vị [min; max] | DD5 s12345 L21 | lệnh LAG |
|---|---|---|---|---|---|---|---|
| 1B L1 (off, bq, vint) | `8da4a708` | 22,97 | −22,7 | 20,18 / 25,48 | −31,15 [−32,07; −28,47] | −31,77 | 765 |
| 1B L2 (lag, bq, vint) | `873ad442` | 26,72 | −24,4 | 21,61 / 31,51 | −32,35 [−33,05; −30,04] | −32,98 | 872 |
| 1B L3P (lag, pit, adj) | `ea64bb43` | 27,04 | −25,5 | 21,81 / 31,95 | **−32,75 [−33,34; −30,21]** | −33,34 | 872 |
| 2B L1 | `c8a4f1cf` | 22,41 | −22,7 | 20,89 / 23,70 | −31,30 [−32,19; −28,52] | −31,94 | 833 |
| 2B L2 | `0544acac` | 26,90 | −24,4 | 22,15 / 31,33 | −32,10 [−32,92; −29,68] | −32,83 | 989 |
| 2B L3P | `ff379e18` | 27,37 | −25,8 | 22,21 / 32,22 | −32,65 [−32,95; −29,80] | −32,94 | 995 |
| 50B L1 (A, `2f7739b5`) | — | 22,31 | −16,2 | | −23,57 [−24,23; −21,25] | −23,56 | 1456 |
| 50B L3P (`80f509ec`) | — | 22,91 | −17,1 | 16,47 / 29,12 | −27,30 [−27,89; −26,63] | −27,89 | 1874 |

- Chênh ghép cặp (`logs/boot_band_S_paired.log`): L3P−L1 1B −1,58 [−2,03; −0,85]; 2B −1,28 [−1,54; −0,59]; 50B −4,11 [−6,12; −2,95]. Phần lớn chênh nhỏ ở NAV nhỏ đến từ L1→L2 (bỏ fill ảo); L2→L3P (bq→pit) −0,11…−0,24.
- Lệnh khác nhau (`logs/lag_diff_S.log`, `logs/lag_diff_B50.log`; lệnh = holding (mã, ngày fill đầu)): 1B chỉ-L1 188 / chỉ-L3P 295 / chung 577; 2B 197 / 359 / 636; 50B 294 / 712 / 1162.
- Đọc: fill ảo là mã khối lượng 60 phiên = 0 nên không mua được ở BẤT KỲ NAV nào (xác nhận lại skeptic A5), nhưng **ảnh hưởng DD5 của nó phụ thuộc NAV** (45,8% → 26,9% vốn mua LAG). ~4pp ở 50B là tương tác fill ảo × trần ADV, không phải hằng số.
- **Điều quan trọng hơn:** ở 1–2B, sổ LAG mua trọn size vào mã thanh khoản thấp (ADV median 116 tr ở 1B) nên đuôi sâu hơn: DD5 −32,7 vs −27,3 ở 50B, MaxDD thực −25,5 vs −17,1. Engine 1B còn lệch live (65,5% ngày mua LAG bị trần ràng buộc vs live 0/48 lệnh) ⇒ **chưa kết luận được neo nào đúng cho NAV live**; cần quyết định neo áp cho cỡ NAV nào.

## 3. Việc 3: DD5 theo dải (`boot_band.py`, `logs/boot_band.log`)

- `bootstrap_nav.py` md5 f62f3853, exec nguyên mã, chỉ đặt global L ∈ {10, 21, 42} × SEED ∈ {12345, 1, 7, 2026, 31337}, B=4000. Bảng ở §0.3.
- Theo L (trung vị 5 seed), L3P park 0,3: L=10 −28,53, L=21 −28,86, L=42 −28,25.
- **N:** 15 cấu hình KHÔNG độc lập (cùng chuỗi lịch sử, seed dùng chung giữa ledger). Dải đo bất định Monte Carlo + chọn L, không đo bất định mô hình/regime.

## 4. Việc 4: ADV sau thưởng/cổ tức CP (`adv_split.py`, `logs/adv_split_{Av,A,AB}.log`)

- Nguồn (đã tra `kb/data_registry`): sự kiện = `data/snapshots/corp_action_share_20260927.parquet` (= `BASKET_CA_SNAPSHOT` engine), ISS `price_adjusting`, có `exright_date`. Giá/khối lượng = cache pin-era `bq_cache_asof20260729_postrestate/ticker` (đúng dữ liệu engine).
- pit-ADV tái lập đúng engine: max cost/(0,2·pitADV) = 1,000000, 0 vượt ở cả 3 ledger (`logs/adv_split_engine_match.log`). Control (không sự kiện) adj/pit = 1 tuyệt đối.
- Kiểm hệ số bằng giá k(ex−1)/k(ex+1), k=Price/Close (né bẫy Price đứng yên ngày GDKHQ): thưởng + cổ tức CP khớp |log|≤0,05 ở 84,7% (n=1217); quyền mua chỉ 12,5% (hệ số giá ≠ 1+r, số CP tăng phụ thuộc đăng ký) ⇒ **tiêu đề dùng Av = thưởng/cổ tức CP đã kiểm**; A (mọi thưởng/cổ tức CP) và AB (+ quyền mua, cận trên) để biên.

| Ledger | (mã, ngày) ảnh hưởng | adj/pit median / p95 / max | lệnh cap sai (bind ∧ adj>pit) | >5% | vốn mua thêm cận trên |
|---|---|---|---|---|---|
| 50B `80f509ec` | 298/6916 = 4,31% | 1,063 / 1,573 / 2,417 | 71/1874 = 3,79% | 48 = 2,56% | 0,69% |
| 2B `ff379e18` | 76/2337 = 3,25% | 1,065 / 1,497 / 1,733 | 12/995 = 1,21% | 8 = 0,80% | 0,12% |
| 1B `ea64bb43` | 62/1829 = 3,39% | 1,066 / 1,492 / 1,709 | 9/872 = 1,03% | 6 = 0,69% | 0,11% |

- Biên: lệnh cap sai 50B A 4,70% / AB 5,60%; 1B A 1,26% / AB 1,38%.
- Không chạy lại engine với ADV đã quy đổi (cần knob mới) ⇒ tác động lên DD5 **chưa đo**; cận trên vốn bị cắt <0,7% gợi ý nhỏ (ước lượng).

## 5. Chưa kết luận được

- Neo cho NAV live: engine 1B sâu hơn 50B ~5pp DD5 nhưng lệch live về tập mã/trần (§2). Cần: (a) user chốt neo áp cho cỡ NAV nào; (b) đo vì sao engine 1B chọn mã LAG kém thanh khoản hơn live (gate rating/ADV live?).
- Việc 4 chỉ đo phía cap; không đo DD5 sau quy đổi.
- Không pin ledger mới (thí nghiệm; V1 trùng pin cũ).

## 6. Tái lập

```bash
A6=mike/agents/Taylor/research/live_gap_exec_A6
$A6/make_sandboxes.sh                                   # sb/c_{adj,vint} ← wt-livegapA6-1113 (chặn nếu bẩn)
cd $A6 && xargs -P4 -L1 sh -c 'exec $0 "$@"' < batch.txt  # 8 chân; logs/legs_summary.log
$DNA_PYEXE ../live_gap_exec_A2/metrics.py ledgers/*_exp_S*  # logs/metrics_S.log
$DNA_PYEXE boot_band.py lab=ledger ...                  # logs/boot_band*.log
$DNA_PYEXE lag_diff.py <L1.csv> <L3P.csv>               # logs/lag_diff_*.log
ADV_EV_SET={Av|A|AB} $DNA_PYEXE adv_split.py lab=ledger ...
./selfchecks.sh <sandbox> <out>                         # logs/selfcheck_*.log
```
