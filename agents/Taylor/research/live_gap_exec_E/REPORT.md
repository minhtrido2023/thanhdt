# Luồng E — W2b–W5 + counterfactual thực thi (job `Taylor_20261112_151839` → resume `…_162006`, 12/11/2026)

Nền: nhánh `research/live-gap-E-20261112` (worktree `wt-livegap-E-1112`), commit **`9de5f6ee8`** = `c27fe6823` (vá mergesort +
PARK_SCHEDULE/TIEBREAK_SEED) + hook research **mặc định TẮT**: `PARK_NOJIT_UNTIL`, `PARK_NOSELL_UNTIL`, `PARK_SELL_ALLOW_DATES`,
`ENTRY_BLOCK_FILE`. Unset ⇒ byte-identical (chân `ctl` md5 `0746de33…` = p1c). **KHÔNG merge, KHÔNG đổi production.**
Sandbox đóng băng `sb/` (data md5 = p1c `sandbox_data_md5.txt`, `diff` rỗng) và `sbv/` (3 file LAG vintage 10-29). Mọi chân
**self-check 0 VND** (BAL+LAG, cash-flow + final NAV). **N = 1 cửa sổ live (01/07→11/11, ~4 tháng) — mọi số dưới đây là mô tả
một đường đi, không phải ước lượng thống kê; không có CI.**

## 0. Kết luận (chỉ phần đã đo)

1. **Waterfall đóng (pp, inception→11/11; `waterfall.csv/png`)** — cộng số học bậc 1:

   | thành phần | SpaceX cold | SpaceX warm | ZaloPay cold | ZaloPay warm |
   |---|---|---|---|---|
   | ENGINE (park mục tiêu: 1,0→0,7 07-03→0,8 08-05→0,3 09-28→0 10-02, LZB, JIT bật) | −7,88 | −8,39 | −6,45 | −6,78 |
   | + fidelity park (buy-only tới 06/08, cho trim 07-06 = live) | +1,47 | +1,49 | +1,59 | +1,50 |
   | + W2b (chỉ luật mã cờ 03/11 có tác dụng) | −0,66 | −0,67 | −0,67 | −0,68 |
   | + W3 lệnh tay DISC (sổ, từ 04/08) | +1,24 | +1,24 | +1,15 | +1,15 |
   | + W4 fill thật vs Open (non-DISC) | −0,13 | −0,13 | −0,73 | −0,73 |
   | + W5 lãi egg (0,023397%/ngày đo) | +0,72 | +0,72 | +0,69 | +0,69 |
   | **dư chưa giải thích** | **+1,38** | **+1,88** | **+1,80** | **+2,24** |
   | LIVE (TWR GĐ0; ZaloPay = sleeve bot) | −3,86 | −3,86 | −2,61 | −2,61 |

   Gap ban đầu (live − engine park mục tiêu) +4,02…+4,53 SX / +3,84…+4,17 Z ⇒ đã quy được **~66% / ~59%** (cold/warm SX),
   **~53% / ~46%** (Z). Dư **dương** (live vẫn thắng) và **tập trung tháng 9** (gap α T9 +3,20 SX / +3,54 Z ở MỌI chân
   fidelity, trong khi T8/T10 ≈ 0 và T11 −0,8…−1,1).
2. **E1 fidelity.** Tắt bán/JIT rổ park tới 06/08 (đúng như live thiếu đường JIT/bán rổ) kéo engine lên +1,47…+1,59pp; riêng
   tắt JIT (`fidJ`) chỉ +0,83 SX/+0,44 Z ⇒ phần lớn là **bán rổ về mục tiêu**, không phải JIT. Cửa sổ con 07-20→07-31: gap
   **+2,96 → +1,08pp SX (cold)**, +3,43 → +1,65 Z; β gap còn +0,15/+0,18 ⇒ **killer của skeptic xác nhận về độ lớn** (T7 chiếm
   phần lớn gap trước fidelity). β park live cạnh engine (cold fidT, cả kỳ): **−4,01 / −4,89 SX**, **−3,63 / −3,61 Z** — nay
   park mới thật sự gần khớp; T7 e_park live/engine 81%/71% SX.
   - **Lệnh defer 07-28/29/31 KHÔNG giải thích phần live thắng — ngược dấu** (`e1_deferred.csv`): nếu khớp ở Open, 07-31 chúng
     lãi **+4,02pp SX / +0,59pp Z** gộp; ròng sau khi bán rổ park lấy tiền (r park engine 07-27→07-31 +5,0%) **+1,67pp SX / +0,01 Z**
     (xấp xỉ: Open ngày plan, bỏ phí). Tức defer làm live **thiệt** chứ không lợi trong 07-20→07-31. 4 mã LAG defer của SpaceX
     (CSV/EVF/PSI/VCI) **không có** trong lệnh của engine (engine LAG cuối T7 chỉ AGP/IVS) ⇒ khác tập tín hiệu, không phải khác thực thi.
   - **α live ex-egg** (α live cả kỳ − W5): SpaceX **+0,82 − 0,72 = +0,10pp**; ZaloPay **+1,39 − 0,69 = +0,70pp** (skeptic
     ước +0,07 / +0,94: SpaceX khớp; ZaloPay thấp hơn vì W5 dùng rate ĐO và mẫu số nav_b — egg nằm trong nav_b).
3. **E4 W2b — đo độc lập từng luật, áp từ ngày hiệu lực (blocklist `(ticker, ngày khớp)` point-in-time, `w2b_blocklists.py`):**
   | luật (hiệu lực) | Δ SX cold | Δ Z cold | trạng thái |
   |---|---|---|---|
   | sàn ADV 2 tỷ (08-10) | 0,000 | 0,000 | **inert trong cửa sổ** (ledger md5 = fidT) |
   | mã cờ: ngoài universe_pit_q ∪ quality≠OK ∪ ADV≤0,1 tỷ ∪ LAG NP_P4≤0 (11-03) | **−0,659** | **−0,670** | có tác dụng (warm −0,67/−0,68) |
   | LAG DD-zone gate (11-09) | 0,000 | 0,000 | **inert trong cửa sổ** (md5 = fidT) |
   | excluded_tickers (DGC ZaloPay; PNJ cả 2 TK từ 09-30) | — | — | **inert cho entry**: engine không mua DGC; PNJ chỉ vào 07-21 (CAPIT, trước 09-30) và bán 10-19 — luật chặn entry nên không chạm; vị thế PNJ 09-30→10-19 không mô hình |
   | CAPIT lever tắt (10-13) | — | — | **inert trong cửa sổ**: CAPIT event duy nhất 07-20, max gross 1,001, không entry CAPIT sau 10-13 |
   Gộp (`w2b_all`) = đúng bằng mã cờ (md5 trùng w2b_flag) ⇒ không tương tác. `LENH_QUA_LON_VS_ADV` không mô hình (phụ thuộc size).
4. **E2 — 37 phiên |Σbook − mtm|/NAV > 2% mỗi TK** (`e2_trace.csv`): **37/37 cả hai TK do GIÁ, 0 do LƯỢNG** — lượng sổ = broker
   mọi phiên (Q ≡ 0). `market_price` trong `live_books` (replay p1c chạy 12/11) = **BQ Close điều chỉnh hồi tố** theo corp-action
   xảy ra SAU ngày t (TCB, VPB, HDB, VHM ×2 ex 06/08, MBB, VPI); `mtm_stock` của nav_history dùng **Price thực = giá broker**
   (đúng). Max 9,67% SX / 10,08% Z ngày 04/08 (VHM chia ×2 ex 06/08 bị "trừ trước" 2 phiên); hết >2% sau 28/09 khi rổ park bán.
   **Không phải lỗi sổ live, không phải bootstrap 04/08, không phải lô CORP_ACTION** — là artefact giá của replay. Méo β do đó:
   **+0,05pp SX / +0,02pp Z** (`e2_beta_distort.csv`) ⇒ không đổi kết luận p1c; nhưng phân rã p1c dùng e_x hơi thấp cho các mã này.
5. **E3 tie-break trên vintage 10-29 (đúng cơ sở pin):** không seed **23,60%** (= vá mergesort, khớp p1b); 10 seed
   **TB 23,45%, sd 0,40, min 23,01 / max 24,26**, 4/10 seed < 23,37% ⇒ **pin 23,37% nằm giữa phân phối tie-break**
   (z ≈ −0,2). Chênh pin↔vá 0,23pp là nhiễu thứ tự, không phải look-ahead/lệch hệ thống.
6. **E5 W3/W4/W5:**
   - **W3 DISC** (P&L nắm giữ theo sổ book=DISCRETIONARY_SPECIAL, Close điều chỉnh ⇒ gồm cổ tức/thưởng): **+1,24pp SX / +1,15 Z**
     (T8 +0,41/+0,37, **T9 +1,01/+0,96**, T10 −0,25/−0,19). ⚠️ Bản theo fills (`fills_booked`) cho −0,71/−0,78 — **SAI**:
     `fills_booked` thiếu lệnh bán DISC (SpaceX DRI mua 3.700 − bán 2.500 trong file nhưng broker 11/11 = 0 cp) ⇒ không dùng.
     SCL nằm book **LAG** theo sổ bot (không phải DISC). VGS mua 12/11 ngoài cửa sổ. Bỏ P&L trong phiên khớp (fill→close).
   - **W4** (fill vs Open phiên khớp = giá engine; non-DISC; n=390/272 lệnh, 113/69 lệnh không gắn được book ⇒ tính là non-DISC):
     **−0,13pp SX / −0,73pp Z**; tách PRE ≤25/08 −0,17/−0,93 vs POST +0,04/+0,20 (khớp GĐ0: hybrid đã chữa slippage).
   - **W5 egg** = Σ egg_t/NAV_t × 0,023397%/ngày × ngày lịch: **+0,715pp SX** (egg TB 23,4% NAV) / **+0,689pp Z sleeve** (egg/nav_b;
     theo NAV cả TK +0,437). Rate ĐO (`kb/data_registry/trading-bot/cash_identity.md`, 80 cửa sổ 08-19→10-12), không phải 8,5% brief.

## 1. Đính chính phát biểu sai của p1c (`../live_gap_phase1c_20261112/REPORT.md`)
- **§0.3 "khi park khớp hai phía, β gần như cân"** — SAI tiền đề: chân "engine park live" của p1c dùng lịch 0,7 từ 01/07 + JIT
  bật, trong khi live giữ ~81% park suốt T7 (e_park T7 live/engine **81%/57%**). Park **chưa** khớp. Khớp thật (fidT): 81%/71%,
  β park cả kỳ −4,01/−4,89 SX. β tổng gần cân ở p1c là trùng hợp bù trừ (β park live âm hơn bù β tín hiệu engine dương hơn).
- **§0.4 "LAG mua 21–27/07 ngay trước pha giảm"** — SAI về timing: VNI 21/07 1.730 → 22/07 1.669 (một phiên −3,6%) → 27/07 1.669
  → **31/07 1.736 → 04/08 1.777**. Sau 21–27/07 là **hồi phục** (+4,0% tới 31/07, +6,5% tới 04/08), không phải pha giảm. Phần thua
  của engine 20–31/07 đến từ CAPIT+LAG mua 21/07 ở đỉnh trước phiên −3,6% và **bán rổ park về mục tiêu** (fidelity ở trên), không
  phải mua trước một xu hướng giảm.

## 2. Dư chưa giải thích (+1,4…+2,2pp) — giả thuyết, CHƯA đo
Theo sổ live (`resid_bybook_live.csv`), T9: PARK −1,89 / CAPIT +0,65 / DISC +1,01 / LAG +0,12 / BAL −0,30 (SX). DISC đã ở W3;
phần dư T9 nhiều khả năng là **thành phần rổ park live (mua 01–02/07, không tái cân bằng) ≠ rổ engine (namecap, tái cân bằng)** và
**cỡ CAPIT live (~31% NAV giữa T9) ≠ engine**. Hai giả thuyết này chưa có phép đo; không gán số.

## 3. Hạn chế
- Cộng gộp bậc 1, không tương tác; W3 dùng NAV_{t−1} mẫu số, bỏ P&L ngày khớp; W4 coi Open = giá engine (engine khớp Open T+1).
- `fills_booked` thiếu lệnh (xem W3) ⇒ W4 có thể thiếu một phần notional (chiều sai số chưa biết).
- E1 defer: Open ngày plan, bỏ phí, r park = chỉ số rổ engine. E2 dựa `live_books` replay p1c (giá Close hồi tố là của replay).
- Không đổi production; không re-pin (E3 chỉ chứng minh pin nằm trong phân phối tie-break).

## 4. Tái lập (từ `research/live_gap_exec_E/`)
```bash
./make_sandbox.sh                       # sb/ (=p1c data md5) + sbv/ (LAG vintage 10-29)
python3 w2b_blocklists.py               # blk_adv/flag/ddzone(/all).csv
P=4 ./run_queue.sh queue1.txt; P=4 ./run_queue.sh queue2.txt   # + chân cold trong logs/*.log (dòng EXIT= ghi đủ env)
cp sb/data/*gapE_*.csv ledgers/; python3 legret.py              # legs.csv (r kỳ + md5)
python3 decomposeE.py e1_decomp; python3 e1_deferred.py
python3 e2_trace.py; python3 resid_bybook.py; python3 e5_accounting.py; python3 waterfallE.py
```
md5 mọi ledger/CSV: `MD5SUMS.txt`. Ledger chính: base SX cold `3d580333`, fidT SX cold `3dc05018`, w2b_flag SX cold `1f88e81c`,
Z cold base `8f8c358a` / fidT `cdecd527` / w2b_flag `817f3099`; warm: SX base `d9dd2ac2` / fidT `37a56713` / w2b_flag `65c63688`,
Z base `a68c7464` / fidT `17153923` / w2b_flag `7490ff5a`.
