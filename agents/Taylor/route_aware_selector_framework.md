# Route-aware custom30V selector (`BASKET_SELECT=v3route`) — framework & evidence

**Job** `Taylor_20260714_112932` → **fix quyết định `Taylor_20260714_121717`** · **Status: RESEARCH
ONLY — NOT WIRED · VERDICT CUỐI = NO-GO (REFUTED giữ nguyên)** · Ngày 2026-07-14

> ⚠️ **ĐỌC §10 TRƯỚC §4-§9.** Toàn bộ §4-§9 (viết ở job 112932) quote edge **+7.63pp vs
> `yieldcombo`** và kết luận "lean GO". §10 chứng minh con số đó **quy sai công**: nó gần như hoàn
> toàn là **trục định giá composite 8L (`v3latest`)** — thứ CHƯA BAO GIỜ là chủ đề tranh luận và
> **đã bị bác từ 2026-06-22** vì thua OOS ở cấp hệ. Đóng góp THẬT của fix route, khi tách bạch, là
> **ÂM −2.38pp** (âm cả IS lẫn OOS). §4-§9 giữ lại nguyên văn làm dấu vết audit, KHÔNG phải kết luận.

---

## 1. Tại sao 1/PCF cho ngân hàng là sai — nguyên tắc user nêu

Production custom30V (`BASKET_SELECT=yieldcombo`) xếp hạng 30 tên bằng **`rank(1/PE) + rank(1/PCF)`,
cùng một thước đo cho MỌI tên, không phân biệt loại hình**.

`PCF` = Price / Cash Flow. Với **công ty sản xuất**, dòng tiền hoạt động là tiền thật do hoạt động
kinh doanh cốt lõi tạo ra — bán hàng, thu tiền. `1/PCF` cao = rẻ so với tiền mặt mà lõi kinh doanh
sinh ra. Đây là một tín hiệu value có nghĩa.

Với **ngân hàng**, cùng dòng "cash flow" đó phản ánh **biến động tiền gửi và cho vay** — một quý
huy động mạnh hoặc giảm dư nợ sẽ đẩy CFO lên rất cao mà **không** nói gì về việc lõi kinh doanh
sinh lời hay không. Nó là dòng chảy của *bảng cân đối*, không phải sản phẩm của hoạt động. Nói cách
khác: **cùng một tên gọi, hai đại lượng kinh tế khác nhau.** Xếp VCB cạnh HPG trên cùng trục `1/PCF`
là so sánh hai thứ không cùng đơn vị.

Nguyên tắc chung (đã ghi trong memory `feedback-finance-domain-grounding-not-pure-statistics`):
**kiểm tra tính so sánh được của metric giữa các nhóm dị chất TRƯỚC khi xếp hạng cross-sectional.**
`yieldcombo` vi phạm đúng nguyên tắc này.

## 2. Hệ đã tự giải quyết vấn đề này ở chỗ khác — `rating_8l.py`

Không cần phát minh gì mới: `rating_8l.py` (composite v3 LIVE) **đã** phân luồng và **đã** cho tài
chính một trục value riêng:

- Router `route_of()`: BANK / INSURANCE / SECURITIES / POWER / CYCLICAL / REALESTATE / COMPOUNDER
  (ICB_Code + `bank_lens_v3.csv` / `power_lens.csv` + override REE/HHS).
- Comment trong chính code: *"financials/RE/POWER **KEEP v2** (preserves BANK's real pb_z +0.136
  signal)"* — tức BANK/INSURANCE/SECURITIES **không bao giờ** chấm bằng `cfy=1/PCF`, mà bằng
  **`value_score_v2`**:

  ```
  value_score_v2 = 0.65 * ey_percentile_WITHIN_route      # 1/PE, xếp hạng TRONG nhóm route
                 + 0.35 * (0.5 - pb_z/2)                  # pb_z = P/B chuẩn hóa vs lịch sử 5Y của CHÍNH nó
                 + cfo_confirm (+0.05 / -0.08)            # 1/PCF chỉ còn là nudge nhỏ, KHÔNG phải trục chính
                 + track_bonus (+0.03 CF_OA_5Y>0, +0.03 ROE_Min5Y>0.10)
  ```

  `pb_z` là thước đo đúng cho ngân hàng: P/B so với chính lịch sử của nó — book value là đại lượng
  ngân hàng thật sự vận hành trên đó, và IC đo được **+0.136 cho BANK** (đã validate, không phải số
  tự chế).
- Xếp hạng **TRONG route** ("absolute cheapness = earnings-yield percentile, SECTOR-NEUTRAL (rank
  WITHIN route)") — bank đấu với bank, không đấu với nhà sản xuất.

**`v3route` = `v3latest` + đúng 1 thay đổi**: ba route tài chính (BANK/INSURANCE/SECURITIES) chuyển
sang `value_score_v2` verbatim. Mọi route khác **byte-identical** với `v3latest` → đây là ablation
sạch đúng 1 trục, cô lập chính xác điều user chất vấn.

> **Phạm vi có chủ ý**: `rating_8l` giữ v2 cho "financials/RE/POWER", nhưng `v3route` **chỉ** chuyển
> 3 route TÀI CHÍNH. REALESTATE/POWER giữ nguyên đường v3latest → nếu muốn là một ablation RIÊNG,
> không trộn vào phép đo này.

## 3. Selfcheck — `route_selector_selfcheck.py` (ALL PASS, 6/6)

Không tin comment, phải chứng minh trục thật sự đổi:

| # | Kiểm tra | Kết quả |
|---|----------|---------|
| 1 | OFF mặc định — không có env → không bao giờ vào nhánh v3route | OK (default `blend`) |
| 2 | BANK **thật sự** dùng pb_z, không lẫn cfy: bóp méo PCF của ACB → điểm v3route **không nhúc nhích (0.0000)**, trong khi v3latest đổi 0.0353; bóp méo pb_z → v3route đổi 0.0431 | OK |
| 3 | 1010 tên phi tài chính **không đổi 1 ly** vs v3latest; 79/79 tên tài chính ĐỀU đổi (không no-op ngầm) | OK |
| 4 | Xếp hạng TRONG route: shock PE toàn thị trường phi tài chính → 0 bank bị dịch chuyển | OK |
| 5 | Thiếu pb_z → **abstain** (score −1, xếp cuối), KHÔNG bịa 0.5; PB<0 → 0; golden floor giữ nguyên | OK |
| 6 | Số học v2 tái lập **đúng đến 6 chữ số** vs rating_8l (ACB: 0.538235 vs 0.538235) | OK |

**Rủi ro tồn dư (pre-existing, không do job này tạo ra):** `build_value_panel.py` khai báo route bằng
một **bản port copy-paste** của `rating_8l.route_of` (dòng 71: *"port of rating_8l.route_of"*), không
phải import. Tôi đã đối chiếu tay hai hàm — **hiện tại khớp 100%** (cùng thứ tự luật, cùng
COMMODITY_MAP/SUGAR/CEMENT/HOLDING/REALESTATE override). Nhưng đây đúng là **2 nguồn sự thật** mà
dispatch cảnh báo: sửa `rating_8l.route_of` mà quên panel → lệch âm thầm. **Đề xuất (chưa làm, ngoài
phạm vi job): panel import trực tiếp từ `rating_8l`.**

## 4. Kết quả — đo ở CẢ 2 cấp (bài học sector-cap sáng nay)

Cả 2 arm chạy **cùng hôm nay, cùng vintage dữ liệu**, `NAV_TOTAL_B=50`, `PARK_STATES=3:0.7`, DT5G,
`threads=1`, `AUDIT_END=2026-06-19`, `BASKET_WT=namecap`. **Self-check 0 VND cả 2 arm** (BAL+LAG).

### Cấp vehicle (custom30V standalone — cơ chế thật, không bị pha loãng)

| | CAGR | Sharpe | MaxDD | Calmar | CAGR IS | DD IS | CAGR OOS | DD OOS |
|---|---|---|---|---|---|---|---|---|
| yieldcombo | 29.83% | 1.24 | −40.98% | 0.73 | 23.53% | −31.99% | 35.89% | −40.98% |
| **v3route** | **37.47%** | **1.51** | **−36.39%** | **1.03** | **29.68%** | **−18.24%** | **45.12%** | **−36.39%** |
| **Δ** | **+7.63pp** | **+0.27** | **+4.59pp tốt hơn** | **+0.30** | **+6.15pp** | **+13.75pp** | **+9.24pp** | **+4.59pp** |

Thắng **mọi chiều, cả IS lẫn OOS**. Đây là bằng chứng cơ chế đúng — không phải một chiều đánh đổi
chiều khác (khác hẳn sector-cap sáng nay: xấu đi mọi chiều).

### Cấp hệ 2-book V2.4 đầy đủ (cái thật sự quyết định)

| | CAGR | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|
| baseline yieldcombo | 27.09% | 1.81 | −18.3% | 1.48 |
| **v3route** | **27.96%** | **1.88** | **−18.6%** | **1.50** |
| Δ | **+0.87pp** | +0.07 | **−0.3pp xấu hơn** | +0.02 |

Vehicle +7.63pp → hệ chỉ +0.87pp: đúng như kỳ vọng, vì custom30V chỉ là **chỗ đỗ tiền nhàn rỗi khi
NEUTRAL**, không phải toàn bộ NAV. **DD cấp hệ xấu đi nhẹ** (−18.3 → −18.6).

## 5. Kỷ luật multiple-testing (KB §5)

- **N trials**: v3route là 1 biến thể; họ selector code trong `custom_basket.py` = 10 mode
  (blend/yieldcombo/pbcombo/petop/pemom/v3comp/ps3/v3gated/v3latest/v3route).
- **DSR** (`route_robustness.py`, tái dùng implementation pinned của `dsr_pbo_annex.py`):
  **DSR = 1.0000 → PASS** ở mọi N (10 / 25 / 50 / 138 empirical family).
  ⚠️ **Tôi không coi DSR này là bằng chứng mạnh**: nó chấm NAV toàn hệ như một chiến lược độc lập —
  Sharpe đó do V2.4 quyết định, không phải do cú swap selector. Phép thử trung thực của SWAP là bảng
  LOO dưới đây + delta cấp vehicle.
- **Per-year LOO** (bài học Wave1/H8a 2026-07-05 — và đúng cái đã giết varA của chuỗi DCF sáng nay):

  **Edge CAGR dương 13/13 lần bỏ từng năm** (min **+0.36pp** khi bỏ 2017, max +1.48pp khi bỏ 2024).
  **Edge Calmar dương 12/13** (bỏ 2017 → −0.002, coi như hoà).

  → **Đây KHÔNG phải reshuffle-luck tập trung 1-2 năm.** Khác hẳn DCF varA (toàn bộ edge nằm ở
  2017/2021). Không năm nào carry hết edge.

- **Recompute độc lập từ CSV** (guidelines §8): script tự tính lại từ `combined_nav` → edge
  **+0.88pp** vs harness in **+0.87pp** (lệch do harness dùng calendar-time 12.46y, script dùng
  252-day 12.33y). **Khớp.**

## 6. ⚠️ Phản biện thật — 3 năm gần nhất v3route THUA ở cấp hệ

| năm | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | **2024** | **2025** | **2026** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Δ (pp) | +4.47 | +7.25 | +3.06 | +1.08 | −4.77 | +2.26 | +2.20 | +5.53 | **−5.57** | **−1.24** | **−2.37** |

Thắng 8/13 năm, mean +0.92pp/median +1.08pp — nhưng **cả 3 năm gần nhất đều ÂM**. Edge tập trung ở
2016-2018 + 2022-2023. Đây là **objection mạnh nhất** với một quyết định wire LIVE: cơ chế có thể
phụ thuộc regime (các năm ngân hàng dẫn dắt), và giai đoạn gần nhất — chính là giai đoạn giống hiện
tại nhất — nó làm hại.

LOO cho thấy bỏ 2024 thì edge TĂNG lên +1.48pp, tức các năm gần đây đang **kéo edge xuống**, không
phải tạo ra nó. Edge vẫn dương 13/13 nên không bị lật, nhưng **câu hỏi mở**: đây là noise 3 năm hay
là cơ chế đang xói mòn?

## 7. Bức tranh basket — rebal 2026-05-05 (30 tên thật)

**Overlap 21/30.** 9 tên ra, 9 tên vào:

- **DROPPED (9)**: BID·CTG·LPB·MBB·TCB·VCB [BANK], EVF [SECURITIES], DCM [CYCLICAL]
- **ADDED (9)**: FPT·GAS·VNM·PNJ·DGW·GEE [COMPOUNDER], DIG·HDG [REALESTATE], HPG [CYCLICAL]

| route | yieldcombo | v3route |
|---|---|---|
| BANK | **13** | **6** |
| COMPOUNDER | 7 | **13** |
| REALESTATE | 3 | 5 |
| SECURITIES | 5 | 4 |
| CYCLICAL | 2 | 2 |

**Tỷ trọng tài chính 18/30 → 10/30; riêng BANK 13/30 → 6/30.** Đúng điều user dự đoán: bỏ cái thước
1/PCF sai cho ngân hàng thì **hết một nửa số ngân hàng rơi ra** — chúng vào rổ được là nhờ một chỉ
số vô nghĩa với chúng, không phải vì rẻ thật.

**HPG / LPB (user hỏi đích danh):**
- **HPG** [CYCLICAL]: yieldcombo **OUT** → v3route **IN** (liq_rank 29). Ghi chú: HPG đang là tên
  basket-drift treo ở SpaceX (plan 07-14 bị user HOLD) — dưới v3route nó **thuộc về rổ**, tức lệnh
  bán HPG hôm nay sẽ là sai hướng nếu v3route được duyệt.
- **LPB** [BANK]: yieldcombo **IN** (liq_rank 10) → v3route **OUT**. LPB chính là tên plan 07-14
  định MUA thay HPG.

→ **Hai lệnh của plan 07-14 (bán HPG, mua LPB) bị v3route đảo ngược đúng 180°.** User HOLD hôm nay
là may. Đây là lý do phải chốt hướng selector TRƯỚC khi xử lý nốt basket-drift HPG.

Coverage: 93% tên tài chính có pb_z tại src_q 2026-01-01; phần còn lại **abstain** theo đúng luật
của rating_8l (không bịa điểm giữa).

## 8. Sự cố phát hiện & đã xử lý — canonical R3 CSV bị ghi đè

Run baseline (`BASKET_SELECT=yieldcombo` → `_sel_tag` rỗng theo thiết kế) **ghi đè lên đúng file
canonical registry-pinned** `..._wtnamecap.csv` lúc 18:42 — đúng mẫu sự cố §8 (2026-07-06).

- Xác minh: file canonical sau đó **md5-identical với `_exp_dcfctrl20260714.csv`** (vintage hôm nay,
  CAGR 27.09%), **KHÁC** R3 pinned (27.84%, md5 `4d736d91…` == `_exp_dropMOMN-MOMS.csv`).
- **Đã khôi phục**: canonical ← `R3_pinned_backup_20260714.csv`, verify md5 khớp lại đúng bản pinned.
  Bản rerun hôm nay giữ lại dưới tên tường minh `_exp_selbaseline20260714.csv` (audit).
- `_sel_tag` (đã thêm ở `pt_v23_audit_2014.py`) cố ý để yieldcombo/blend = tag rỗng nhằm giữ
  byte-identical cho production → **chính điều đó khiến baseline rerun trỏ vào file pinned**.
  Bài học: tag rỗng bảo vệ được *tên file production*, **không** bảo vệ được *artifact pinned* khỏi
  một lần rerun hợp lệ.

**Phát hiện phụ đáng báo động (ngoài phạm vi job, cần quyết định riêng):** baseline production chạy
lại hôm nay cho **27.09%**, trong khi registry pin **27.84%** (07-12). Lệch **−0.75pp** thuần do
**data vintage** (các fix cache 8L / ticker_prune chunked 07-13). Mọi run hôm nay nhất quán với nhau
nên **so sánh A/B vẫn hợp lệ**, nhưng **R3 pinned hiện KHÔNG tái lập được trên dữ liệu hôm nay** —
cần một quyết định re-pin riêng.

## 9. Verdict

**CẦN VERIFY THÊM — KHÔNG WIRE.** Lean GO về cơ chế, nhưng còn 1 objection thật chưa trả lời.

**Ủng hộ:**
1. Lỗi methodology là **thật và có nguyên tắc** (bank PCF ≠ manufacturer PCF), không phải data-mining.
2. Cách sửa **tái dùng thứ hệ đã tự validate** (`value_score_v2`, pb_z IC +0.136), không chế số mới.
3. Selfcheck 6/6 chứng minh trục thật sự đổi, ablation sạch 1 trục.
4. Vehicle level thắng **mọi chiều, IS lẫn OOS** (+7.63pp CAGR, DD tốt hơn 4.59pp).
5. **LOO 13/13 dương** — không phải luck 1-2 năm (khác DCF varA).
6. DSR PASS (dù tôi tự hạ trọng số bằng chứng này).

**Chống:**
1. **3 năm gần nhất (2024/2025/2026) đều ÂM ở cấp hệ** — giai đoạn giống hiện tại nhất.
2. Edge cấp hệ chỉ **+0.87pp**, **DD xấu đi 0.3pp**.
3. Baseline không tái lập được pinned R3 (vintage drift −0.75pp) → nền so sánh đang trôi.
4. Panel route vẫn là **port copy-paste**, chưa import (rủi ro lệch tương lai).

**Đề xuất cho Mike + user:**
1. **BẮT BUỘC quant-skeptic** trước mọi cân nhắc wire — killer objection cần giao đúng: *"edge âm 3
   năm gần nhất, tại sao vẫn nên tin?"*
2. Nếu skeptic CONFIRMED → cân nhắc wire, nhưng nhớ **v3route đảo ngược 2 lệnh plan 07-14
   (HPG/LPB)** → chốt hướng selector trước khi xử nốt basket-drift HPG.
3. Riêng biệt: quyết định re-pin R3 trên vintage mới, và cho panel import `rating_8l.route_of`.

**Artifacts**: `route_exp/` (logs, vehicle_metrics.csv, members_*.csv, basket_compare.py,
route_robustness.py), `route_selector_selfcheck.py`, CSV `_exp_selv3route` + `_exp_selbaseline20260714`.

---

# 10. FIX QUYẾT ĐỊNH (job `Taylor_20260714_121717`) — VERDICT: NO-GO

quant-skeptic **REFUTED** finding 112932: `value_score_v2` trộn một số hạng **tuyệt đối** (`0.35*(0.5
− pb_z/2)`, chỉ chạm 1.0 khi `pb_z ≤ −1`) vào một điểm số rồi đem **cắt top-30 CHÉO NGÀNH** với các
route khác vốn xây từ **percentile thuần** (luôn có tên chạm 1.0). `rating_8l` chưa từng so chéo
route nên thang đo lệch không quan trọng ở đó — phép cắt chéo ngành làm nó thành quyết định.

Fix đã làm đúng khuyến nghị. Nhưng thứ giết finding **không phải** cái fix — mà là một arm
**chưa từng ai đo**.

## 10.1 Lỗ hổng quy công: `v3latest` chưa bao giờ được đo

Mọi số quote từ trước (+7.63pp, +6.17pp) đều so với `yieldcombo`. Nhưng `v3route3` khác `yieldcombo`
ở **HAI chiều độc lập**:

| | thay đổi | có phải điều user nêu? |
|---|---|---|
| **(a)** | trục định giá: `rank(1/PE)+rank(1/PCF)` → **composite 8L `v3latest`** (ey/cfy/ps trọng số theo route, percentile TRONG route, coverage-aware, golden floor) — áp cho **MỌI** route | ❌ **Không.** Chưa từng là chủ đề. |
| **(b)** | **fix route tài chính**: BANK/INSURANCE/SECURITIES → `value_score_v2` (pb_z, bỏ lens 1/PCF) | ✅ Đây mới là premise "PCF ngân hàng ≠ PCF nhà máy". |

`v3route*` = `v3latest` + (b). Không đo `v3latest`, **(a) và (b) bị gộp làm một** và toàn bộ công
được ghi cho (b). Đo `v3latest` (`route_v3latest_arm.py`) là việc quyết định của job này.

## 10.2 Cấp vehicle — 5 arm, cùng vintage, cùng cấu hình

| | CAGR | Sharpe | MaxDD | Calmar | CAGR IS | CAGR OOS | fin/30 |
|---|---|---|---|---|---|---|---|
| yieldcombo (production) | 29.83% | 1.24 | −40.98% | 0.73 | 23.53% | 35.89% | 9.27 |
| **`v3latest`** (trục (a) đơn thuần) | **38.38%** | **1.51** | **−34.96%** | **1.10** | **32.07%** | **44.51%** | 6.98 |
| `v3route` (REFUTED, lệch thang) | 37.47% | 1.51 | −36.39% | 1.03 | 29.68% | 45.12% | 5.08 |
| `v3route2` (pct-norm, quá đà) | 36.22% | 1.47 | −36.29% | 1.00 | 29.49% | 42.76% | 6.19 |
| **`v3route3`** (quantile-match, **arm tham chiếu**) | 36.01% | 1.46 | −36.41% | 0.99 | 29.52% | 42.30% | 6.54 |

**`v3latest` thắng MỌI arm route ở MỌI chiều** (CAGR, MaxDD, Calmar; Sharpe hoà). Thêm fix route lên
trên nó chỉ làm **xấu đi**.

## 10.3 Phân rã sạch của +7.63pp (cộng khớp chính xác)

```
  +8.55pp   (a) trục composite 8L      v3latest − yieldcombo   <- KHÔNG liên quan route
  −2.38pp   (b) fix route THẬT SỰ      v3route3 − v3latest     <- premise của user, đã tách bạch
  +1.46pp   (c) artifact thang đo      v3route  − v3route3     <- đúng con bug skeptic bắt
  ────────
  +7.63pp   = con số headline của job 112932   ✓ (8.55 − 2.38 + 1.46 = 7.63)
```

Theo cửa sổ — **(b) ÂM ở CẢ HAI**, không phải hiện tượng một cửa sổ:

| | IS 2014-19 | OOS 2020-26 |
|---|---|---|
| (a) trục composite | **+8.54pp** | **+8.62pp** |
| (b) **fix route** | **−2.56pp** | **−2.20pp** |

> **Kết luận trực tiếp:** edge "route-aware repricing" **không tồn tại**. Tách khỏi trục composite,
> nó **âm bền vững ở cả IS lẫn OOS**. `+7.63pp` = công của một trục khác **cộng** một con bug thang đo,
> **trừ đi** tác hại của chính cái fix được đề xuất.

## 10.4 Đòn kết liễu thứ hai: `v3latest` ĐÃ BỊ BÁC TỪ 2026-06-22 — và cấp vehicle **ĐẢO DẤU** OOS

`v3latest` không phải phát hiện mới đáng mừng. `results_registry.md` (dòng ~145-154, THREAD (b),
2026-06-22, drift-controlled, self-check 0 VND) **đã đo nó ở CẤP HỆ và bác**:

| `v3latest` vs `yieldcombo` | IS | **OOS** | verdict |
|---|---|---|---|
| **cấp hệ 2-book** (2026-06-22) | +1.40pp | **−0.78pp** | **IS-overfit → GIỮ yieldcombo** |
| **cấp vehicle** (hôm nay) | +8.54pp | **+8.62pp** | "thắng mọi chiều" |

**Cấp vehicle nói OOS +8.62pp. Cấp hệ nói OOS −0.78pp.** Proxy không chỉ suy giảm — nó **đảo dấu**
phép so sánh OOS. Lý do có cơ sở: custom30V chỉ là **chỗ đỗ tiền nhàn rỗi khi NEUTRAL**, còn CAGR
cấp vehicle tính trên toàn kỳ **kể cả những đoạn sleeve không hề được dùng**.

⇒ **§4 của tài liệu này** ("thắng mọi chiều, cả IS lẫn OOS" ở cấp vehicle) dựa trên một proxy **đã
được chứng minh là đảo dấu** với đúng họ selector này. Chính job 112932 cũng đã thấy dấu hiệu: vehicle
+7.63pp → hệ chỉ +0.87pp. Đây là **bài học phương pháp chính** rút ra từ job này.

## 10.5 §3 ABSTAIN — không phải coverage-artifact (giả thuyết bị bác)

Nghi vấn: 2014-19 có ~20% lần loại tài chính là **ABSTAIN thuần** (thiếu `pb_z` do chưa đủ 5 năm PB)
→ hiệu ứng độ phủ dữ liệu đội lốt phán đoán định giá. Test: `V3R_ABSTAIN_IMPUTE=1` gán `pb_z` trung
vị route để tên đó **ở lại và bị chấm trên ey thật**.

| | CAGR | edge vs base | fin/30 |
|---|---|---|---|
| `v3route3` | 36.01% | +6.17pp | 6.54 |
| `v3route3_abstimp` | **36.46%** | **+6.63pp** | 7.46 |

Giữ lại các tên thiếu `pb_z` làm edge **TỐT LÊN +0.45pp**. ⇒ ABSTAIN **làm mất** edge chứ không tạo
ra nó. **Giả thuyết coverage-artifact bị BÁC** — sòng phẳng ghi nhận: đây là điểm finding gốc đứng vững.

## 10.6 §4 SENSITIVITY — plateau, nhưng là plateau quanh một đóng góp ÂM

| cell | edge vs base | vs `v3route3` | IS | OOS |
|---|---|---|---|---|
| `v3route3` (rating_8l verbatim) | +6.17pp | — | 29.52 | 42.30 |
| `W_ABS 0.55` | +5.72pp | −0.46 | 28.65 | 42.26 |
| `W_ABS 0.75` | +5.95pp | −0.22 | 29.57 | 41.81 |
| `cfo off` | +6.22pp | +0.04 | 29.78 | 42.12 |
| `cfo ×2` | +6.65pp | +0.48 | 29.52 | 43.28 |
| `track off` | +6.57pp | +0.39 | 29.78 | 42.83 |
| `track ×2` | +6.10pp | −0.08 | 29.93 | 41.73 |

Biên độ **+5.72 … +6.65pp** (sd 0.33) — **plateau thật**, default không phải spike đơn lẻ. Nhưng vì
mọi cell đều mang trong mình +8.55pp của trục (a), plateau này nằm quanh mức **−1.9 … −2.8pp so với
`v3latest`**: cơ chế **robust — robust ở chỗ hơi có hại**. Knob không cứu được.

## 10.7 §2 PLACEBO — CHẠY XONG NHƯNG BỊ CONFOUND; **verdict tự in của script là SAI**

20 seed count-matched (đúng số tài chính `v3route3` giữ mỗi quý, chọn tên ngẫu nhiên):

```
placebo edge: mean −2.13pp | median −2.22pp | sd 1.62 | min −5.61 | max +0.85
REAL edge   : +6.18pp   → beats 100% of placebos, z = +5.12
```

Script tự in *"placebo does NOT reproduce it → WHICH names are dropped carries real information"*.
**KHÔNG ĐƯỢC TRÍCH DÒNG NÀY.** Nó **sai** vì dính đúng con confound §10.1: placebo dựng trên
**ranking `yieldcombo`** (slot phi tài chính lấy từ `yieldcombo`), trong khi `v3route3` lấy phi tài
chính từ **`v3latest`**. Nên `z = +5.12` đang đo **trục (a)**, không đo việc chọn tên tài chính.

Placebo đúng phải dựng trên nền `v3latest`. **Không chạy** — vì thứ nó cần giải thích (một edge
dương của (b)) **không tồn tại**: (b) = −2.38pp. Placebo dùng để giải thích edge dương; effect âm thì
không cần placebo. Ghi lại đây thay vì giấu.

## 10.8 §5 — 2 lỗi phụ ĐÃ VÁ

- **`route_selector_selfcheck.py`**: thêm **[7] CROSS-ROUTE SCALE COMPARABILITY** — đo P90/sd điểm
  tài chính vs phi-tài-chính **mỗi quý** (6 test cũ đều trong-route/byte-identity nên mù hoàn toàn
  với lớp lỗi này). **ALL PASS (7 nhóm)**. Test bắt đúng bug:

  | mode | fin P90 | nonfin P90 | **gap** | sd ratio |
  |---|---|---|---|---|
  | `v3route` | 0.781 | 0.866 | **+0.107** (thấp hơn = bug REFUTED) | 0.86 |
  | `v3route2` | 0.965 | 0.866 | **−0.064** (quá đà, cùng lớp lỗi ngược dấu) | 1.16 |
  | `v3route3` | 0.897 | 0.866 | **−0.001** ✅ | 0.99 |

  Spearman trong-route `v3route` vs `v3route2`/`v3route3` = 0.9993/0.9995 → **thứ tự bank-vs-bank
  không đổi, chỉ phép cắt dịch**; 1010 tên phi tài chính byte-identical cả 3 arm.
- **`basket_compare.py`**: dòng chẩn đoán "85 names / 237 with pb_z" (237 > 85 vô lý) — nguyên nhân:
  PANEL là **daily**, đếm lẫn **rows vs names**. Đã dedupe `groupby(ticker).last()` đúng như selector
  thật đọc (`groupby(["ticker","qstart"]).last()`).

## 10.9 §6 — việc riêng

- **`build_value_panel.py` import `rating_8l.route_of`: KHÔNG LÀM (có lý do).** `route_of` là **hàm
  lồng** bên trong `rating_8l.py:443`, closure trên `bank_set`/`power_set` nạp trong thân hàm →
  không import được nếu không **refactor production 8L**. Sửa production cho mục đích thẩm mỹ, giữa
  một job research, là sai (coding_guidelines §3 surgical). **Đã verify port TƯƠNG ĐƯƠNG hôm nay**:
  `COMMODITY_MAP`/`SUGAR_SET`/`CEMENT_SET` khớp từng ký tự, cùng `bank_lens_v3.csv`/`power_lens.csv`,
  cùng thứ tự nhánh, cùng `power_set = power − bank`. ⇒ **finding không bị nhiễm**. Rủi ro trôi trong
  tương lai vẫn còn → nếu muốn xử lý, đó là task refactor riêng có skeptic.
- **Re-pin R3**: `27.09%` (vintage hôm nay) vs `27.84%` (pin) = **−0.75pp data-drift**, không phải
  bug. Vẫn **chờ quyết định của Mike/user** — không tự re-pin trong job này.

## 10.10 VERDICT CUỐI — NO-GO, KHÔNG WIRE GÌ

**REFUTED của quant-skeptic được GIỮ NGUYÊN.** Fix đã làm đúng và đủ; edge **không sống sót**.

| câu hỏi | trả lời |
|---|---|
| Edge sống sót qua percentile-norm? | Con số +6.17pp thì "sống" — **nhưng quy sai công**. Tách bạch: **−2.38pp**. |
| % artifact vs ABSTAIN vs edge thật | **artifact thang đo +1.46pp** · **trục composite (a) +8.55pp (không liên quan route)** · **ABSTAIN −0.45pp (làm mất edge, không tạo)** · **edge route thật: −2.38pp — ÂM** |
| Nguyên tắc user được minh oan? | **Không, bởi số liệu này.** Xem dưới. |

**Sòng phẳng với premise của user.** Kết quả này **không** chứng minh "PCF ngân hàng = PCF nhà máy".
Nó bác một điều hẹp hơn nhiều: **cách hiện thực hoá cụ thể này** — chấm lại ngân hàng bằng `pb_z`
qua `value_score_v2` **trong phép cắt top-30 chéo ngành** — **không tạo ra return edge**, mà làm mất
2.38pp. Chú ý sắc thái quan trọng: `v3latest` (arm thắng ở cấp vehicle) **cũng đã** xếp hạng
**TRONG route** (bank so bank) — tức nguyên tắc "đừng so ngân hàng với nhà máy trên cùng một thang"
**đã được hệ thực hiện sẵn ở đó**. Thứ gãy là bước mạnh hơn: **thay 1/PCF bằng pb_z**. Và ngay cả
`v3latest` cũng **đã bị bác ở cấp hệ** (OOS −0.78pp, 2026-06-22) — nên **không có gì ở đây để wire**.

**Bài học phương pháp (giá trị lâu dài nhất của job này):**
1. **Ablation phải neo vào arm LIỀN KỀ, không phải baseline production.** So `v3route` với
   `yieldcombo` gộp 2 trục và ghi hết công cho trục sai. Arm đúng là `v3latest`. Con bug này tồn tại
   **trước** cả bug thang đo skeptic bắt, và **lớn hơn** nó (8.55 vs 1.46).
2. **Cấp vehicle của custom30V là proxy ĐẢO DẤU cho cấp hệ** (v3latest OOS: +8.62pp vehicle →
   −0.78pp hệ). Sleeve chỉ chạy khi NEUTRAL. **Đừng bao giờ tuyên GO cho selector custom30V từ số
   vehicle.**
3. Verdict tự in của script (`placebo does NOT reproduce it`) **sai** khi thí nghiệm bị confound —
   phải đọc thiết kế, không copy dòng kết luận.

**KHÔNG đụng gì tới production.** Đặc biệt: kết quả này **KHÔNG** đảo ngược 2 lệnh HPG/LPB đang hoãn
trong plan 07-14 — đó là quyết định của user, không phải hệ quả tự động của backtest. (Nếu có, nó
càng **củng cố** việc không hành động theo `v3route`.)

**Đề xuất còn lại cho Mike + user:** (1) đóng hướng v3route; (2) quyết re-pin R3 (việc riêng, độc
lập); (3) nếu vẫn muốn theo đuổi nguyên tắc của user thì hướng đúng **không phải** selector — mà là
hỏi tại sao `v3latest` mạnh IS nhưng gãy OOS ở cấp hệ; đó là **dự án riêng có N-budget + pre-register**,
không phải phần đuôi của job này.

**Artifacts** (`route_exp/`): `route_fix_compare.py`, **`route_v3latest_arm.py`** (arm quyết định),
`route_abstain_sens.py`, `route_placebo.py` · `attribution_metrics.csv`, `abstain_sens_metrics.csv`,
`placebo_v3route3.csv`, `vehicle_metrics_fix.csv`, `vehicle_level_*.csv`, `members_*.csv` ·
`logs/{v3latest_arm,abstain_sens,placebo_v3route3,route_fix_compare}.log` ·
`route_selector_selfcheck.py` (7 nhóm ALL PASS).
