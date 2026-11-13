# Luồng A5: pin chính xác trên mã đã commit, và bằng chứng cho neo sizing

Job `Taylor_20261113_071030`. ⚠️ PAPER. **KHÔNG đổi production, `trading_rules.json` hay neo sizing. KHÔNG merge.** Chưa qua quant-skeptic.
Mọi số dưới đây đo trong job này. Log ở `logs/`, ledger ở `ledgers/`, script ở thư mục này.

## 0. Kết luận

1. **Việc 1: cả hai đầu dải trùng byte trên mã đã commit.**
   - pin0% `80f509ec3dbbd55233412913407e6f53`, chạy trên main `7f25febc1`, worktree sạch.
   - pin1M `e2de0ac45c7c265827fc53ac0a750675`, chạy trên `e9a9aed1a`.
   - Main KHÔNG có `IDLE_CARRY_TIER`, xem §1.
   - Kết quả dải: **CAGR 22,91% (pin0%) … 26,61% (pin1M); DD5 −27,89% … −24,96%**.
   - Self-check 0 VND.
2. **Neo −25,2% có chứa fill ảo.** Đó là ledger `4707bcbe` (sexies 09-28): park **0,3**, `LIQ_ZERO_BLOCK` chưa tồn tại (tức hành vi `off`), ADV `bq`, quicksort. Chạy lại được, trùng byte.
   - Nhìn theo từng trục một, **chỉ một bước làm DD5 sâu thêm: bỏ fill ảo** (`LIQ_ZERO_BLOCK=lag`). Ở park 0,3 bước này là **−3,96pp**, ở park 0 là **−4,17pp**.
   - Các trục còn lại đều ≤0,34pp: mergesort, cache LAG adj v2, ADV pit.
3. **ADV live = ADV pit, đo trên lệnh thật.**
   - Mẫu: 48 lệnh mua LAG, gồm 32 cặp (mã, ngày) độc lập, 17 mã, 12 ngày.
   - ADV tại gate `cap_lag_orders` khớp pit ở 29/32 cặp, |log| tối đa 0,002.
   - ADV bq-ngày-fill (engine cũ) lệch ±4–10%.
   - **0/48 lệnh vượt trần, và cũng không có dòng "LAG trần %ADV" nào** trong 904 log run_bot. Ở cỡ NAV live (~1 tỷ), trần không bao giờ ràng buộc.
4. **DD live của sleeve BAL+LAG là −23,2%** ở cả hai tài khoản, trên 76 phiên.
   - Mức này nằm ở p10–13 phân phối engine không fill ảo, và p5–7 phân phối engine có fill ảo.
   - Hơi nghiêng về engine không fill ảo, nhưng **N=1 cửa sổ, 1–4 mã: KHÔNG phân biệt được hai engine.**
5. **Kết luận (d), §5.** Engine `lag` + `pit` trung thực hơn với live. Bằng chứng là code cộng với tái lập ADV trên lệnh thật, không phải P&L.
   - Neo −25,2% **không còn cơ sở**, vì nó dựa trên fill ảo mà live chặn cứng.
   - Nếu giữ đúng luật neo của user ("đầu sàn ở mức park XẤU HƠN trong {0; 0,3}") thì neo theo engine trung thực là **−29,09%** (park 0,3).
   - Nếu chỉ tính park live hiện hành (0) thì là **−27,89%**.
   - User quyết.

## 1. Việc 1: provenance

| Đầu | code | worktree | md5 ledger | trùng A3/A4 |
|---|---|---|---|---|
| pin0% | `7f25febc1dd55498322bc6201c6ea36b2f3ad94f` (= HEAD `main`) | `wt-livegapA4-1113`, `git status --porcelain` rỗng (run_leg.sh tự chặn nếu bẩn) | `80f509ec3dbbd55233412913407e6f53` | ✅ trùng byte `80f509ec` |
| pin1M | `e9a9aed1a04e8906b156dbfadef4d53a0af7aa31` (nhánh `research/live-gap-A5-r-20261113`) | `wt-livegapA4-1113-r`, sạch | `e2de0ac45c7c265827fc53ac0a750675` | ✅ trùng byte `e2de0ac4` |

- **`IDLE_CARRY_TIER` KHÔNG có trên main.** Kiểm bằng `git grep` trên `7f25febc1`. Knob vào code ở `75fba8a9e` / `9327043d2` (W2/Q2), còn tier `dep1m` ở `d3c376310` / `3c9e3d13d`. Các commit này chỉ nằm trên nhánh research: `research/repin-dep1m-2709`, `research/live-gap-D-20261112`, `research/live-gap-A2-r-20261113`.
- `e9a9aed1a` = `770393ce2` + **đúng 1 dòng** mà A4 chạy khi chưa commit: `LAG_ADV_SRC` mặc định `pit`. Bây giờ dòng đó đã commit.
  - Lịch sử: `770393ce2` → `49cd913ae` (PT_WORKDIR) → `2b8d80fab` (LIQ default) → `33f005209` (BAL gate knob, trơ) → … → `f66dab189` (dep1m).
  - Cách main 289 dòng `pt_v23_audit_2014.py`. Hai đầu dải vì vậy chạy trên **2 cây code khác nhau**, giống A4.
  - Tôi không cherry-pick knob carry vào main, để khỏi tạo code mới chưa review.
  - Bằng chứng phần khác nhau là trơ với cấu hình này: pin0% trên main = pin0% A3 trên `6bbb4a443`, và mọi control ở A3 §4 đều trùng byte.
- **Lệnh chạy:** `run_leg.sh <TAG> <m|r> adj`. Env đầy đủ:

  ```
  BASKET_WT=namecap BASKET_SELECT=yieldcombo PARK_STATES=3:0.0 IDLE_CARRY_TIER={off|dep1m}
  BASKET_CA_SNAPSHOT=data/snapshots/corp_action_share_20260927.parquet
  BQ_LOCAL_CACHE=data/bq_cache_asof20260729_postrestate BQ_CACHE_THREADS=1 NAV_TOTAL_B=50 ETF_LIQ=custompitg
  AUDIT_END=2026-06-19 TZ=Asia/Ho_Chi_Minh
  $DNA_PYEXE pt_v23_audit_2014.py v23a none postbull 0 edge
  ```

  `LIQ_ZERO_BLOCK` / `LAG_ADV_SRC` không đặt, tức mặc định `lag` / `pit`.
- **Data pin-era (md5):**

  | File | md5 |
  |---|---|
  | `bq_cache_asof20260729_postrestate/manifest.json` | `7f29e9ab…` |
  | 53 parquet (md5 của danh sách md5, `logs/bq_cache_parquet_md5.txt`) | `853799ce…` |
  | CA snapshot `corp_action_share_20260927.parquet` | `e3bf03ef…` |
  | LAG adj v2 (`sb/*_adj/LAG_MD5`): earnings_events_classified | `2fa62575` |
  | LAG adj v2: earnings_surprise_data.pkl | `d3136e80` |
  | LAG adj v2: lag_edge_health | `1cee2f59` |
  | LAG adj v2: earnings_px | `f791d802` |
  | LAG adj v2: lagged_pos_ov | `6c8ceb1d` |

  `LAG_MD5` trùng sandbox A4.
- **Số đo** (`logs/metrics_A5.log`, `logs/boot2_A5.log`; bootstrap circular L=21, B=4000, seed 12345, chạy đúng mã `bootstrap_nav.py` md5 f62f3853):

| Đầu | CAGR | Sharpe | MaxDD | IS / OOS | Boot CAGR5 | **DD5** | P(DD<−30%) | self-check |
|---|---|---|---|---|---|---|---|---|
| pin0% (sàn) | 22,91% | 1,78 | −17,1% | 16,47 / 29,12 | 14,72% | **−27,89%** | 2,73% | 0 VND BAL+LAG |
| pin1M (trần) | 26,61% | 2,04 | −14,8% | 19,80 / 33,20 | 18,13% | **−24,96%** | 0,80% | 0 VND BAL+LAG |

- **Đối chiếu:** trùng byte cả hai đầu. Không có trục code, data hay engine nào lệch.

## 2. Việc 2a: neo −25,2% chính xác là gì, và thang 1-trục

- **Neo** = `R3-anchor-pin0pct-sexies`, md5 `4707bcbeb7e801d49a4a851ffd91d5e7` (`PINS.jsonl` dòng 1). Lệnh: `PARK_STATES=3:0.3`, IDLE off, cache asof0729, NAV 50B, ETF_LIQ custompitg, AUDIT_END 06-19.
  - Thời đó chưa có `LIQ_ZERO_BLOCK` (tức `off`): ngày có `Volume_3M_P50` ≤0 hoặc NULL thì **mua trọn size, không trần = fill ảo**.
  - ADV = BQ `Volume_3M_P50` ngày fill (`bq`). Sort = quicksort. Data LAG = vintage 10-29.
- **Chạy lại được:** `run_leg_q.sh C30_off_q` (worktree quicksort Luồng A `dbfd9a4af`, `LIQ_ZERO_BLOCK=off`) cho ra `4707bcbe` **trùng byte**, self-check 0 VND.
- **Thang (pin0%, mỗi bước đúng 1 trục; md5 rút gọn; DD5 2 chữ số; `logs/boot2_A5.log` + `logs/boot2_pinned.log`):**

| Bước | trục đổi | park 0,3: md5 · CAGR · **DD5** · ΔDD5 | park 0: md5 · CAGR · **DD5** · ΔDD5 |
|---|---|---|---|
| Neo / L0 | — | `4707bcbe` · 23,37% · **−25,20%** | `537e349b` · 22,12% · **−23,90%** |
| L1 | quicksort → mergesort | `c95b4158` · 23,60% · −25,12% · +0,08 | `2f7739b5` · 22,31% · −23,56% · +0,34 |
| **L2** | **fill ảo → `LIQ_ZERO_BLOCK=lag`** | `6db7c630` · 25,06% · **−29,08% · −3,96** | `5ae929c6` · 23,44% · **−27,73% · −4,17** |
| L3 | data LAG vint → adj v2 | `151bd903` · 24,77% · −29,07% · +0,01 | `84f796bd` · 23,39% · −27,57% · +0,16 |
| L3P | ADV bq → pit (= mặc định main) | `dc8910f8` · 24,42% · **−29,09%** · −0,02 | `80f509ec` · 22,91% · **−27,89%** · −0,32 |

  - Đầu trần (pin1M), cùng nhóm: neo park 0,3 `bcd0469f` −23,56% → mới park 0,3 `5f55a5b3` **−27,30%** (CAGR 26,84%). Neo park 0 `a6ba34d8` −21,46% → `e2de0ac4` −24,96%.
  - Trục park (0,3 → 0) ở engine mới: −29,09 → −27,89 (+1,20pp). Ở engine neo: −25,20 → −23,90 (+1,30pp).
  - ⇒ **Δ neo cũ → engine mới cùng park 0,3 = −3,89pp, và −3,96pp trong đó đến từ đúng một trục: bỏ fill ảo.**
- Kiểm chéo: `P3_L3` (`151bd903`) trùng md5 với ledger `engine_liqz` của GĐ2B (`live_gap_phase2b_20261112`), chạy trên cây code khác.
- Self-check 0 VND (BAL + LAG, cash-flow + NAV identity) cả 8/8 chân (`logs/legs_summary.log`). RSS ≤4,36G, 4 chân song song.
- 2015 là năm thể hiện fill ảo rõ nhất: L1 18,6% → L2 4,2% (park 0,3), số lệnh mua LAG 4.582 → 7.438.

## 3. Việc 2b: ADV lúc đặt lệnh LAG thật so với pit (`lag_orders.py`, `adv_live_vs_pit.py`)

- **Nguồn** (đã tra `kb/data_registry`):
  - `data/trade_plans/plan_{SpaceX|ZaloPay}_{date}.json` (CANONICAL).
  - Journal `exec_{acct}_{date}_journal.csv`, file riêng mỗi account. Lọc account theo tên file và `assert plan.account` (§12).
  - `tav2_bq.ticker` Volume/Price/Close/Volume_3M_P50, kéo 13/11 (md5 `logs/bq_px_vol.csv` 06e12eb9).
- **Live dùng ADV nào:** `cap_lag_orders` → `due_diligence.adv_vnd(ticker, plan_date)` → dòng mới nhất ≤ ngày đặt lệnh, tức dòng **t-1** lúc 09:05, vì cache sync 23:45. Công thức là `Volume_3M_P50(t-1) × COALESCE(Price, Close)(t-1)`.
- **N:** 60 dòng mua LAG trong plan; 48 có qty>0 (SpaceX 30, ZaloPay 18); **32 cặp (mã, ngày) độc lập**, 17 mã, 12 ngày (07-27 → 11-09). Có fill: 15 lệnh. Lệnh có `adv_note` ghi số ADV lúc lập plan: 4.
- **Kết quả (32 cặp):**

| So sánh | median log | p5 / p95 | max \|log\| | khớp tuyệt đối |
|---|---|---|---|---|
| live(gate) / pit | +0,0000 | +0,0000 / +0,0012 | 0,0020 | 29/32 |
| bq-ngày-fill / pit | −0,0056 | −0,0439 / +0,0678 | 0,0973 | 0/32 |

  - 3 cặp lệch (APF ×2, HT1), lệch ≤0,2%, nguyên nhân chưa tách.
  - `adv_note` lúc lập plan (tối t-1, trước sync) khớp dòng **t-2** ở 4/4 lệnh (|log| ≤0,002, `logs/adv_note_check.log`). Như vậy cả lúc lập plan lẫn lúc gate, live **không bao giờ** thấy khối lượng ngày fill. Engine `bq` cũ thì có thấy (A4: nhìn trước 1 phiên).
- **Lệnh bị cap:** order/trần (trần = 0,20 × ADV × 1/2 account) max 0,85, median 0,02 ⇒ **0/48 vượt trần.**
  - grep 904 log `run_bot_*.log`: 0 dòng "LAG trần %ADV" / "LAG BỎ lệnh". Dòng %ADV duy nhất là CAPIT BLOCKED ngày 07-21.
  - Hệ quả: ở NAV live hiện nay, trục bq/pit **không đổi một lệnh nào**. Nó chỉ có nghĩa khi trần ràng buộc (NAV 50B của backtest).
- Corp-action: ADV = Volume thô × Price thô ở cả hai bên, nên tỉ lệ không bị ảnh hưởng. Mức tuyệt đối có thể thấp hơn thật 30–60 phiên sau thưởng/tách (skeptic A4 #2). Chưa đo theo từng mã.

## 4. Việc 2c: DD thực tế BAL+LAG live (`sleeve_dd.py`)

- **Live:** 96 fill BAL+LAG (`live_gap_phase0_20261112/fills_booked.csv`, 6 mã: VPI, HT1, MCH, SCL, VPB, CSV), 07-27 → 11-12, 76 phiên.
  - Định giá total-return theo BQ Close. Đơn vị = qty × Price/Close ngày fill, nên cổ tức/thưởng đã nằm trong Close.
  - Phí 0,097%/chiều, thuế bán 0,1%. TWR Modified-Dietz theo ngày.
  - Kiểm: units cuối không âm cho mọi mã, nghĩa là bán khớp mua.

| | TWR | **MaxDD** | sleeve max / cuối |
|---|---|---|---|
| SpaceX | +0,68% | **−23,25%** | 131 / 115 tr |
| ZaloPay | −11,23% | **−23,24%** | 93 / 79 tr |

- **Phân phối engine, cùng H = 76 phiên.** Lấy sleeve cổ phiếu BAL+LAG = `bal_stocks_ref` + `lag_stocks_ref`, với dòng tiền TX. Chỉ dùng park 0, vì ở park 0,3 `stocks_ref` gồm rổ park mà dòng tiền rổ không có trong TX (`logs/INVALID_sleeve_dd_park030.log`).

| Engine (park 0, pin0%) | trượt lịch sử p50 / p5 | bootstrap p50 / p5 | percentile của −23,2% (lịch sử / boot) |
|---|---|---|---|
| fill ảo `2f7739b5` (L1) | −10,60 / −24,11 | −10,09 / −23,58 | 7,0% / 5,3% |
| `lag` bq `5ae929c6` (L2) | −12,06 / −30,53 | −11,00 / −29,33 | 12,9% / 10,3% |
| `lag` bq `84f796bd` (L3) | −12,28 / −30,42 | −11,06 / −28,80 | 12,8% / 10,3% |
| `lag` pit `80f509ec` (L3P) | −12,25 / −30,75 | −11,02 / −28,83 | 12,9% / 10,3% |

- **Đọc:**
  - **N = 1 cửa sổ 4 tháng.** Sleeve live chỉ có 1–4 mã (VPI mua 62,0–62,6k ngày 09-17/18, bán 49,3–49,6k ngày 10-16), trong khi sleeve engine có hàng chục mã. Đuôi live dày hơn là do số mã ít, không phải do engine sai.
  - −23,2% nằm trong phân phối của cả hai engine. Tỉ số khả năng giữa hai engine chỉ khoảng 2× (p10 vs p5), **không đủ để phân biệt**.
  - DD tổng NAV live chủ yếu do park/DISC (GĐ1c), không đo lại ở đây.
  - Sleeve BAL+LAG live ≈5% NAV, nên −23% sleeve ≈ −1,2pp NAV (ước lượng).

## 5. Việc 2d: kết luận có cơ sở

**Engine nào trung thực hơn với live.** Engine `LIQ_ZERO_BLOCK=lag` + `LAG_ADV_SRC=pit` (mặc định main), dựa trên ba bằng chứng:
1. **Code live:** `cap_lag_orders` fail-closed CHẶN mọi lệnh LAG khi ADV ≤0, NULL hoặc cũ. Engine neo (`off`) lại mua trọn size đúng ở những ngày đó. Đây là hành vi live không thể làm, không phải nhiễu.
2. **Dữ liệu lệnh thật:** ADV live = pit ở 29/32 cặp. bq-ngày-fill lệch tới 10% và nhìn trước 1 phiên.
3. **Thang 1-trục:** toàn bộ chênh DD5 neo → mới (−3,89pp ở park 0,3) đến từ bước bỏ fill ảo (−3,96pp).

**Bằng chứng còn thiếu hoặc yếu:**
- Không có bằng chứng P&L live phân biệt hai engine (§4, N=1).
- Ở NAV live (~1 tỷ) trần ADV không ràng buộc, nên phần bq→pit chưa được kiểm bằng fill thật. Nó chỉ chi phối DD5 ≤0,3pp.
- Engine vẫn còn khác live ở các điểm sau:
  - Luật hủy `max_fill_days=5` / `min_fill_pct=0,30` không có ở live.
  - Engine dùng 20% ADV/phiên cho 1 sổ 50B, còn live là 20% × 1/2 account.
  - Cỡ NAV 50B vs ~1 tỷ: chưa chạy chân small-NAV trên engine mới.
  - ADV thấp hơn thật sau thưởng/tách.
  - Mức tác động của các điểm này **chưa đo**.

**Neo nào đúng (user quyết, nêu cả hai chiều):**
- **(A) Thay neo.** −25,2% được đo trên engine có fill ảo, và live chặn chính những fill đó, nên không còn cơ sở.
  - Áp nguyên luật neo user duyệt 10-08 ("đầu SÀN ở mức park XẤU HƠN trong {0; 0,3}", vì luật park có thể quay lại 0,3) lên engine trung thực: **neo = −29,09%** (park 0,3, pin0%). Park 0 cho −27,89%.
  - Lưu ý: ở engine mới, park 0,3 cho DD5 SÂU hơn park 0. Ở engine neo thì ngược lại (−25,20 vs −23,90 → park 0,3 vẫn xấu hơn). Thứ tự vì vậy không đổi, chỉ có mức thay đổi.
- **(B) Giữ −25,2% tạm thời.** Chỉ hợp lý nếu chấp nhận rằng chưa có bằng chứng P&L live và chưa đo các trục còn lại ở trên. Không có số đo nào trong job này ủng hộ −25,2% là mức đúng.
- Khuyến nghị kỹ thuật (không phải quyết định): (A) với −29,09%, sau khi quant-skeptic CONFIRMED. Nếu user chỉ muốn phủ park live hiện hành thì −27,89%. Tác động tiền thật hiện nhỏ (BAL+LAG ~5% NAV).

## 6. Tái lập

```bash
A5=mike/agents/Taylor/research/live_gap_exec_A5
$A5/make_sandboxes.sh                                    # sb/{m,r}_{adj,vint}; chặn nếu worktree bẩn
cd $A5 && xargs -P4 -L1 sh -c 'exec $0 "$@"' < batch.txt    # 8 chân; logs/legs_summary.log
$DNA_PYEXE boot2.py ledgers/*.csv                        # logs/boot2_A5.log (thang pinned: tmp/ từ data/pinned_ledgers → logs/boot2_pinned.log)
$DNA_PYEXE ../live_gap_exec_A2/metrics.py ledgers/*.csv  # logs/metrics_A5.log
python3 lag_orders.py logs/lag_orders.json; $DNA_PYEXE adv_live_vs_pit.py   # logs/adv_live_vs_pit.log
$DNA_PYEXE sleeve_dd.py <ledger park0>                   # logs/sleeve_dd*.log
```

Nhánh mới `research/live-gap-A5-r-20261113` @ `e9a9aed1a`: chỉ 1 dòng, research-only, KHÔNG merge. Không pin ledger mới, vì V1 trùng pin cũ và P3 là thí nghiệm.
