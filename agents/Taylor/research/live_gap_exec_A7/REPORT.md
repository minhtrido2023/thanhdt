# Luồng A7: trần ADV phía bán, sàn ADV 2 tỷ của live, và neo DD5 theo cỡ NAV

Job `Taylor_20261113_134219`. ⚠️ PAPER. **KHÔNG đổi production, `trading_rules.json` hay neo sizing. KHÔNG merge. Không pin ledger mới.** Chưa qua quant-skeptic (Mike gọi).
Mọi số đo trong job này: log ở `logs/`, ledger ở `ledgers/` (gzip), script ở thư mục này.
Nhánh `research/live-gap-A7-sellcap-20261113` @ `414468bcb` (= A6 `262c117c3` + 2 commit), worktree `/home/trido/thanhdt/wt-livegapA7-1113`.

## 0. Kết luận

1. **Killer objection A6 không đứng vững.** Bật trần bán 0,2×ADV/phiên (carry phần dư) thì DD5 L3P gần như không đổi:
   1B **+0,12pp** [0,00; +0,22], 2B +0,13, 5B −0,20, 50B +0,45. CAGR 1B **tăng nhẹ** 27,04 → 27,37.
   Ở L3P, trần bán ràng buộc 164 lệnh thoát LAG ở 1B, carry tối đa 20 phiên, bị ép bán 1 lần.
   Như vậy: (a) −32,75 của A6 **không phải** sàn nông do bán hết tại Open; (b) CAGR 1B không bị thổi vì bán không trần.
   Chỉ L1 (còn fill ảo, ADV=0) sâu thêm −1,3…−1,5pp, vì mã không có thanh khoản thì không bán được.
2. **50B L1 cùng cây A6, cache adj:** chênh DD5 L3P−L1 = **−3,95pp [−6,08; −2,72]** (A6 trộn cache/commit: −4,11). Phần do trộn chỉ ~0,16pp.
3. **Vì sao engine 1B mua mã LAG kém thanh khoản hơn live: do CHỌN MÃ, không phải NAV hay cỡ lệnh.**
   Live có **sàn ADV3T ≥ 2 tỷ ở tầng tín hiệu** (`lag_liquidity_filter.ADV_MIN_VND`, user chốt 2026-08-10, cho cả LAG và BAL). Engine thì không có: LAG chỉ cần ADV>0, BAL lấy ngưỡng 1 tỷ trong SQL.
   - 58,7% holding LAG của engine 1B có ADV pit < 2 tỷ (chiếm 20,7% vốn mua LAG); 76,6% số holding này chạm trần.
   - Live: ADV p50 5,46 tỷ, cỡ lệnh p50 34,4 tr. Có 6/48 lệnh dưới 2 tỷ, và **cả 6 đều có tín hiệu trước 10/08**; từ 10/08 là 0/42.
   - Phản thực tế: đặt cỡ lệnh live vào chính các mã engine chọn thì vẫn có 34% lệnh vượt 0,2×ADV ⇒ nguyên nhân không nằm ở cỡ lệnh.
   - Đã thêm knob `SIG_ADV_MIN=2e9` để engine có sàn như live.
4. **Câu hỏi chính, neo DD5 cho NAV nào:**
   - NAV chiến lược live hiện nay là ~0,6–0,94 tỷ mỗi account, ~1,55 tỷ cộng lại. Hai account chia đôi %ADV nên dấu chân thị trường ≈ engine 1,5 tỷ.
   - Với engine trung thực với live (trần bán + sàn 2 tỷ), **DD5 vùng 1–2 tỷ = −33,2% [−33,8; −30,1]**. 1B và 2B gần như trùng nhau (ghép cặp −0,17pp).
   - Ở 5 tỷ là −31,2%, ở 50 tỷ là −26,0%.
   - ⇒ **Với NAV live hiện tại, neo DD5 đúng nằm quanh −33%, sâu hơn ~7pp so với engine 50B.** Neo −25,2% cũ và −27,9…−29,1% (A5/A6) đều đo ở 50B nên **quá nông** cho NAV live.
   - Không có artifact nào cho thấy kế hoạch nạp vốn trong 6–12 tháng tới. Dù NAV tăng theo CAGR backtest (ước lượng ~1,9–2 tỷ cộng lại sau 12 tháng), vẫn nằm trong vùng 1–5 tỷ, tức DD5 −31…−33.
   - **Lý do cơ chế:** ở 50B trần mua ADV làm sổ thiếu vốn triển khai. Tỉ trọng cổ phiếu trung bình 38,0% ở 50B so với 45,7% ở 1B. DD nông hơn ở 50B là hiện vật của giới hạn capacity, không phải rủi ro thấp hơn.
   - **Độ bất định** (§4.3): dải Monte Carlo/L khoảng ±0,6pp quanh trung vị, cạnh dưới −33,8. Bất định mô hình (engine ≠ live: allocator, rating gate, cổ tức…) chưa đo. **Live chưa phân xử được** (A5: DD live −23,2% trên 76 phiên, N=1 cửa sổ).
   - Tất cả đo ở **pin0%** (park 0). pin1M ở NAV nhỏ **chưa đo**.

## 1. Việc 1: knob trần ADV phía bán

**Code** (`git diff 262c117c3 414468bcb`):
- `simulate_holistic_nav.py`: thêm `sell_adv_cap`, `sell_adv_maxcarry=20`, `sell_cap_log`.
  - Chỉ áp ở đường thoát T+1 Open (`pending_exits`), là đường V2.4 dùng cho mọi lệnh đóng toàn phần.
  > ⚠️ **ĐÍNH CHÍNH 13/11 (arch-review A7 + A9):** dòng 37-38 dưới đây mô tả bản A7 @414468bcb, đã bị thay. Bản đúng (A9 @8b5f7fd0d, đã merge): trần bán tra **bảng ADV pit dày** (shift 1 phiên, không cắt sàn), và **ADV ≤0/thiếu ⇒ KHÔNG bán, carry tới phiên forced (maxcarry)** — KHÔNG phải "bán nốt". Xem `../live_gap_exec_A9/REPORT.md` §1.
  - Mỗi phiên bán ≤ cap × ADV(tk, ngày). Phần dư giữ nguyên vị thế (vẫn MTM, vẫn chiếm slot) rồi carry sang phiên sau. Mỗi lát chịu slippage bậc theo lát/ADV.
  - ADV lấy từ `liquidity_lookup` của chính book (`liq_lag` pit cho LAG, `liq_map` cho BAL). Tra **as-of**: giá trị gần nhất ≤ ngày bán, vì `liq_map` của BAL thưa (chỉ có ở dòng tín hiệu). Bản đầu `22ef7a77d` coi thiếu key là "không bán được"; đã phát hiện và sửa trước khi lấy số.
  - ADV ≤0, hoặc carry quá 20 phiên ⇒ bán nốt (đếm số lần "forced").
  - Khử trùng lặp: mã đang carry thì không xếp lệnh thoát mới.
- `pt_v23_audit_2014.py`:
  - `SELL_ADV_CAP` / `SELL_ADV_MAXCARRY`: áp cho cả `LIQ_FULL` và `LIQ_LAG`, tag `_sellcap0.2`.
  - `SIG_ADV_MIN` (§3): tag `_sigadv2000m`.
  - `SELL_CAP_LOG_OUT`: dump log từng lát.
- **Đường không có trần:** partial-sell cùng phiên (quality/state partial, không bật trong cấu hình này) và `_force_delever` (margin, OFF).

**Không đổi byte khi tắt knob:** pin0 `80f509ec` (V1 trên `22ef7a77d`, V2 trên `414468bcb`) và pin1M `e2de0ac4` (V1 `22ef7a77d`, V2 `414468bcb`) đều trùng byte. Self-check 0 VND cả BAL lẫn LAG ở **mọi** chân (17 lần chạy, `grep` 2 dòng/log).

**Bảng chân** (park 0, pin0%, cache asof0729_postrestate; `metrics.py` A2: CAGR lịch, IS 2014–19 / OOS 2020+):

| Chân | md5 | CAGR | IS / OOS | MaxDD | DD5 trung vị [min; max] | trần bán: lệnh thoát LAG bị cắt / forced |
|---|---|---|---|---|---|---|
| 1B L1 cap (vint) | `136ff4b4` | 23,41 | 21,25 / 25,31 | −24,1 | −32,74 [−33,36; −29,48] | 264 / 166 |
| 1B L3P cap | `790692d8` | 27,37 | 22,02 / 32,39 | −25,4 | −32,56 [−33,15; −30,05] | 164 / 1 |
| 2B L1 cap (vint) | `4cb879a4` | 22,71 | 21,23 / 23,97 | −24,1 | −32,91 [−33,65; −29,53] | 309 / 181 |
| 2B L3P cap | `fee53045` | 27,70 | 22,35 / 32,73 | −25,8 | −32,55 [−32,83; −29,57] | 202 / 1 |
| 5B L3P (off) | `1c5dcc4f` | 26,85 | 20,97 / 32,41 | −24,2 | −31,09 [−31,81; −29,19] | — |
| 5B L3P cap | `1f1e1c16` | 26,78 | 21,29 / 31,95 | −24,3 | −31,43 [−32,04; −29,25] | 285 / 2 |
| 50B L3P cap | `3bd2153d` | 23,27 | 17,41 / 28,89 | −17,7 | −26,79 [−27,36; −26,35] | 495 / 0 (BAL 153 / 3) |
| *A6 1B L3P off* | `ea64bb43` | 27,04 | 21,81 / 31,95 | −25,5 | −32,75 [−33,34; −30,21] | |
| *A6 50B L3P off = pin0* | `80f509ec` | 22,91 | 16,47 / 29,12 | −17,1 | −27,30 [−27,89; −26,63] | |

Chênh DD5 ghép cặp, cap − off (`logs/paired.log`, `logs/paired2.log`):

| NAV | L3P | L1 |
|---|---|---|
| 1B | +0,12 [0,00; +0,22] | −1,26 [−1,84; −0,55] |
| 2B | +0,13 [+0,02; +0,23] | −1,46 [−1,71; −0,67] |
| 5B | −0,20 [−0,36; +0,23] | — |
| 50B | +0,45 [+0,22; +0,60] | — |

- Đọc: lệnh thoát LAG chủ yếu là TIME (giữ 25 phiên). Bán dàn 2–5 phiên quanh ngày thoát gần như trung tính, có khi còn ăn thêm drift ⇒ CAGR không giảm.
- Trần bán chỉ có răng với mã ADV≈0 (L1). L3P đã chặn các mã này ở phía mua.
- Phân bố carry: `ledgers/sellcap_*.csv.gz` (cột carry/frac/liq/liq_src).

## 2. Việc 2: 50B L1 trên cây A6, cache adj

`B50_L1adj` (`LIQ_ZERO_BLOCK=off LAG_ADV_SRC=bq`, cache LAG adj, knob A7 tắt) md5 `f0197d85`: CAGR 23,09 (IS 20,16 / OOS 25,80), MaxDD −16,4, DD5 −23,74 [−24,46; −21,09].
- L3P (pin0) − L1 ghép cặp = **−3,95 [−6,08; −2,72]**, so với −4,11 ở A6 (L1 cũ `2f7739b5` = commit main cũ + cache vint).
- ⇒ Chênh ~4pp ở 50B là thật. Phần do trộn cache/commit ~0,16pp, đúng như skeptic ước lượng ("nhỏ").

## 3. Việc 3: vì sao engine 1B chọn mã LAG kém thanh khoản hơn live

`diag_lag.py` → `logs/diag_lag.log`, `logs/diag_lag_floor.log`. ADV dùng công thức pit (median Volume t-60..t-1 × PxAdv t-1) ở cả hai phía.

| | engine 1B L3P (872 holding, 2014→06/2026) | engine 1B, 07/2024→06/2026 (168) | live (48 lệnh, 32 cặp độc lập, 17 mã, 07-27→11-09) |
|---|---|---|---|
| ADV pit p25 / p50 | 54 tr / 0,93 tỷ | 92 tr / 1,57 tỷ | 4,2 tỷ / 5,46 tỷ |
| cỡ lệnh p50 | 108 tr (tổng holding) | 325 tr | 34,4 tr (3,65% NAV account) |
| lệnh / (0,2·ADV) > 1 | 48,4% holding (65,5% theo ngày mua, A6) | 52,4% | 0/46 (trần live thật ½ share: 0/46) |

- **Gate live mà engine thiếu:** `lag_filter_illiquid(min_adv_vnd=ADV_MIN_VND=2e9)` trong `golive_recommend_v23.py:870`, cộng `bal_filter_thin` 2 tỷ cho BAL. Còn `cap_lag_orders` (trần 0,2×ADV×½) thì engine có tương đương (0,2×ADV), nên đó **không** phải nguồn lệch.
- Engine 1B: 58,7% holding có ADV<2 tỷ, chiếm 20,7% vốn mua LAG. Trong nhóm này 76,6% chạm trần; nhóm ≥2 tỷ chỉ 8,3%.
- Live: 6/48 lệnh có ADV<2 tỷ (APF, SCL; 1,16–1,27 tỷ), tín hiệu 08-03→08-07, **trước khi sàn có hiệu lực 08-10**. Sau đó 0/42.
- **Phản thực tế:** đặt cỡ lệnh live p50 (34,4 tr) vào mã của engine thì 34,2% lệnh vượt 0,2×ADV (39,8% nếu tính ½ share). Đặt cỡ lệnh engine p50 vào mã của live thì 0% vượt.
  ⇒ Lệch đến từ **tập mã**, không phải NAV hay cỡ lệnh.
- **N / hạn chế:** hai kỳ không trùng nhau (cache engine dừng ở 2026-06-19, live bắt đầu từ 07-27), nên đây là so phân bố chứ không phải so cùng mã cùng ngày. Live chỉ có 32 cặp độc lập.
- **Knob `SIG_ADV_MIN=2e9`:** ADV3T = `Volume_3M_P50 × COALESCE(Price, Close)` tại ngày tín hiệu, đúng công thức live.
  - Loại 3255 ứng viên LAG (654 mã). Dòng tín hiệu BAL giảm 773.148 → 628.709.
  - Chân 1B có sàn: 28,45–28,49% CAGR. Tức là sàn làm CAGR 1B **tăng** +1,1pp so với không sàn, trong khi ở 50B nó gần như phẳng.
  - ⚠️ Đây là 1 chuỗi lịch sử. Nghiên cứu 08-04 đã cho PBO 0,916 cho ngưỡng này, nên **không** đọc +1,1pp như một edge.

## 4. Việc 4: neo DD5 theo cỡ NAV

### 4.1 NAV live (`data/execution_logs/nav_history_*.csv`, `active_nav_*.json`, 13/11)

| Account | total_nav | active_nav (chiến lược) | trong đó egg (Trứng vàng) | ghi chú |
|---|---|---|---|---|
| SpaceX | 942,2 tr | 942,2 tr | 751,8 tr | có nhà đầu tư ngoài |
| ZaloPay | 930,6 tr | 603,6 tr | 453,3 tr | loại vị thế legacy (`excluded_tickers`) |
| **Cộng** | 1,87 tỷ | **1,55 tỷ** | | 2 account mua cùng mã, chia ½ %ADV (`cap_lag_orders`) |

- Lúc đặt lệnh LAG: NAV account p50 951 tr (`logs/diag_lag.log`).
- **Dấu chân thị trường** = tổng NAV hai account trên cùng một mã ≈ engine 1,5 tỷ ở share ADV đầy đủ. Từng account riêng ≈ engine 0,94 tỷ nhưng chỉ được ½ trần.
- **Quy mô 6–12 tháng:** không tìm thấy artifact nào về kế hoạch nạp vốn. `account_cash_flows.json` chỉ có 1 lần chuyển 18 tr giữa hai account (10-29); grep `kb/projects`, `KNOWLEDGE`, memory không ra gì.
  Nếu tăng trưởng theo CAGR backtest 23–28% thì sau 12 tháng NAV cộng lại ~1,9–2,0 tỷ (**ước lượng**).

### 4.2 Bảng DD5 theo NAV, engine trung thực với live (trần bán 0,2 + sàn tín hiệu 2 tỷ, L3P, park 0, pin0%)

| NAV | md5 | CAGR (IS / OOS) | MaxDD | **DD5 trung vị [min; max]** | P(DD<−30%) trung vị | stock TB |
|---|---|---|---|---|---|---|
| 1B | `1ed65681` | 28,49 (21,50 / 35,19) | −24,8 | **−33,24 [−33,83; −30,27]** | 10,9% | 45,7% |
| 2B | `80426bf2` | 28,01 (21,36 / 34,36) | −24,6 | **−33,07 [−33,61; −30,10]** | 10,3% | 45,7% |
| 5B | `29bed685` | 27,40 (20,97 / 33,54) | −23,0 | −31,18 [−31,70; −28,72] | 6,7% | 45,1% |
| 50B | `abc3ed39` | 23,18 (18,50 / 27,60) | −16,8 | −25,96 [−26,72; −25,49] | 1,4% | 38,0% |

- Ghép cặp: 1B−2B −0,17 [−0,29; +0,03]; 1B−50B **−7,10 [−7,72; −4,52]**; 5B−50B −4,98.
- Tác dụng của sàn 2 tỷ (cap−cap ghép cặp): 1B −0,47, 2B −0,59, 5B +0,28, 50B +0,84 pp.
- Tác dụng của trần bán khi đã có sàn (1B): DD5 S1_L3PF − S1_L3PcF ≈ −0,02 (−33,26 vs −33,24) ⇒ không đáng kể.
- **stock TB** (`expo.py`, `logs/expo.log`) = (cổ phiếu BAL+LAG)/NAV trung bình theo ngày. 50B triển khai thấp hơn 7,7pp vì trần mua ADV ⇒ DD nông hơn là do thiếu vốn triển khai, không phải rủi ro chiến lược thấp hơn.

### 4.3 Neo nào cho mức NAV nào

| Mức NAV (dấu chân thị trường) | Áp dụng | Neo DD5 đề xuất (đầu sàn, pin0%) | Bất định |
|---|---|---|---|
| ≤ 2 tỷ (**live hiện nay**, cả 6–12 tháng tới nếu không nạp vốn) | SpaceX + ZaloPay | **≈ −33% (trung vị −33,2; cạnh dưới −33,8)** | dải MC/L ±0,6–3pp (max −30,1); mô hình chưa đo |
| ~5 tỷ | nếu nạp vốn lớn | ≈ −31% | như trên |
| ≥ 50 tỷ | chỉ nghiên cứu capacity | ≈ −26% (−27,3 nếu không sàn) | như trên |

- **Chưa đủ bằng chứng để nói neo nào "đúng" theo nghĩa đã được live xác nhận.** Bảng trên chỉ nói: *nếu* tin engine thì ở cỡ NAV live, DD5 sâu hơn bất kỳ neo nào đang dùng (−25,2 cũ; −27,9…−29,1 A5/A6), vì những neo đó đều đo ở 50B.
- Live hiện **không phân xử được**: DD live −23,2% trên 76 phiên (A5), là N=1 cửa sổ.
- **Bất định chưa đo:**
  - (a) pin1M ở NAV nhỏ. Ở 50B, pin1M nông hơn pin0 ~2,7pp (A6 §0.3); NAV nhỏ có thể tương tự, nhưng **chưa đo**.
  - (b) park 0,3 ở NAV nhỏ (A6: ở 50B sâu thêm −1,2pp).
  - (c) các gate live khác engine chưa mô phỏng: rating ≤3 LAG, governance, dd_zone, allocator thực thi theo plan DollarBill.
  - (d) trần ½ share ADV cho từng account: engine 1B/2B dùng share đầy đủ. Vì 1B ≈ 2B nên ảnh hưởng nhỏ (suy luận, chưa đo trực tiếp).
- **N độc lập:** 1 chuỗi lịch sử 2014→2026. 15 cấu hình bootstrap (L∈{10,21,42} × 5 seed, B=4000, `bootstrap_nav.py` md5 f62f3853) **không độc lập**. Dải chỉ đo bất định Monte Carlo + chọn L.

## 5. Tái lập

```bash
A7=mike/agents/Taylor/research/live_gap_exec_A7      # code: wt-livegapA7-1113 @414468bcb (git status sạch)
$A7/make_sandboxes.sh                                # sb/c_{adj,vint} (symlink; đã xoá sau job)
cd $A7 && xargs -P2 -L1 sh -c 'exec $0 "$@"' < batchA.txt   # + batchB.txt (batch.txt = lần 1, 2 chân cap bị dừng vì lỗi liq thưa)
$DNA_PYEXE ../live_gap_exec_A2/metrics.py ledgers/v23_*.csv
$DNA_PYEXE ../live_gap_exec_A6/boot_band.py lab=ledger ... > logs/boot_band.log ; $DNA_PYEXE paired.py logs/boot_band.log A-B ...
$DNA_PYEXE diag_lag.py lab=ledger ...   # việc 3
$DNA_PYEXE expo.py lab=ledger ...       # phơi nhiễm
```

Ledger trong `ledgers/` đã gzip (paired/boot_band đọc được `.gz`). V1/V2 trùng byte pin nên đã xoá (md5 ghi trong log).
