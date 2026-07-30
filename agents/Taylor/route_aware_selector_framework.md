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

`v3latest` không phải phát hiện mới đáng mừng. `results_registry.md` (mục `## 🔬 IC PANEL 8L —
bản đồ marginal-IC đồng bộ của mọi lăng kính`, subsection "THREAD (b) ĐÓNG" — cite by section
title, không phải số dòng, 2026-06-22, drift-controlled, self-check 0 VND) **đã đo nó ở CẤP HỆ và bác**:

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

---

# §11. CƠ CHẾ — vì sao thước đo "chuẩn hơn" lại THUA thước đo "sai bản chất"

**Job** `Taylor_20260714_132942` · **NGHIÊN CỨU CƠ CHẾ, không có ứng viên wire** · 2026-07-14
Scripts: `route_exp/mech_bank_pbz.py`, `route_exp/mech_attribution.py`, `route_exp/mech_scale_drift.py`
Dữ liệu: panel PIT đông băng `data/value_panel_2014.csv` + `members_*.csv` đã dựng ở job 112932.
Không chạy arm backtest mới, không chạm production.

## 11.0 TRẢ LỜI NGẮN

> **`1/PCF` chưa bao giờ làm công việc ĐỊNH GIÁ cho ngân hàng. Nó làm công việc PHÂN BỔ NGÀNH.**
>
> User đúng: CFO ngân hàng là dòng chảy bảng cân đối, không phải tiền do lõi kinh doanh sinh ra.
> Nhưng nó sai **theo MỘT CHIỀU CÓ HỆ THỐNG**: CFO ngân hàng phình to theo huy động/cho vay, nên
> `1/PCF` của ngân hàng **luôn cao**. Đo được: ngân hàng ngồi ở **percentile 71 của TOÀN THỊ TRƯỜNG**
> trên trục `cfy=1/PCF`, trong khi phi-ngân-hàng ngồi ở **49.6** (trung tính). Vì phép cắt top-30 là
> **cắt CHÉO ngành**, cái lệch có hệ thống đó biến thành **suất nhập rổ**: `yieldcombo` là một
> **cỗ máy overweight ngân hàng đội lốt thước đo định giá**.
>
> Và ngân hàng VN **đã thắng**: +1.29pp fwd-2M so với phần còn lại của thị trường (2014→2026).
>
> ⇒ Thước đo sai đã **mua một vị thế đúng**. `v3route`/`v3latest` sửa **phép đo** — và trong lúc sửa,
> **thanh lý mất vị thế**. Backtest chấm **vị thế**, không chấm **phép đo**. Đó là toàn bộ câu chuyện.

Nói cách khác: hai mệnh đề dưới đây **cùng đúng**, không mâu thuẫn —
1. `pb_z` xếp hạng bank-vs-bank **đúng bản chất kinh tế hơn** `1/PCF`. (Tiền đề của user: ĐÚNG.)
2. Thay `1/PCF` bằng `pb_z` **làm hệ tệ đi**. (Số đo: ĐÚNG, −2.38pp.)

Chúng không mâu thuẫn vì **cái leg `1/PCF` bị thay thế không hề đang xếp hạng bank-vs-bank.** Nó
đang giữ tỷ trọng ngành. Sửa (1) mà không biết mình đang đụng (2) = sửa đúng câu hỏi sai.

## 11.1 Bằng chứng A — tiền đề "pb_z dự báo tốt hơn" KHÔNG được dữ liệu ủng hộ

IC rank cross-section **TRONG route BANK** (target `profit_2M` = T+40, gộp (ticker,quarter)=last đúng
như `_score_v3` đọc, 27 tên / 50 quý / TB 19.2 tên/quý — `mech_bank_pbz.py` [A]):

| lens | IC full | t | hit | IC IS | t IS | IC OOS | t OOS |
|---|---|---|---|---|---|---|---|
| **`pb_z`** (cheap=high) | **+0.065** | **1.17** | 58% | +0.023 | 0.22 | +0.096 | 1.51 |
| `cfy = 1/PCF` (thước đo "SAI") | **+0.086** | 1.65 | 49% | +0.140 | 1.52 | +0.033 | 0.65 |
| `ey = 1/PE` | **+0.181** | **3.79** | 65% | +0.167 | 2.16 | +0.194 | 3.32 |

**Đọc bảng này cho đúng:**
- `pb_z` trong bank: **t=1.17 — không phân biệt được với 0.** Nó KHÔNG phải tín hiệu xếp hạng tốt.
- Thước đo "sai bản chất" `1/PCF` xếp hạng bank-vs-bank **NHỈNH HƠN** `pb_z` (+0.086 vs +0.065).
- Cả hai **đều bị `1/PE` áp đảo** (+0.181, t=3.79) — và **cả hai arm đều đã có `1/PE`**. Nên phần
  "xếp hạng bank-vs-bank" gần như đã xong trước khi ai đó chạm vào leg thứ hai.

⚠️ **`+0.136` trong `rating_8l.py:649` KHÔNG tái lập được.** Comment ghi *"preserves BANK's real pb_z
+0.136 signal"* nhưng grep toàn repo: con số này **chỉ tồn tại dưới dạng comment** (`rating_8l.py:649`,
`custom_basket.py:367`) — **không có artifact, không có script, không có dòng registry gốc**. Đo lại
trên đúng panel custom30V ăn: **+0.065 (t=1.17)**. Job 112932 đã trích nó như "đã validate — không chế
số mới"; **nó chưa được validate ở bất cứ đâu tôi tìm được.** → cần ghi nhận là **số không truy vết
được**, không phải bằng chứng.

## 11.2 Bằng chứng B — H3 XÁC NHẬN: `pb_z` là cờ ĐUÔI, không phải trục XẾP HẠNG

Chính `rating_8l.py:646` đã tự ghi (từ 2026-06-19, không phải phát hiện mới):

> *"pb_z is **LINEAR-DEAD** (golden-cell flag only) + TRAP guard"*
> *"RETAIN pb_z (0.35) for its **NON-linear value the IC can't see** (golden-cell pb_z<=-1 dislocation
> +59%/96% 12M, timing, and the capital-destroyer TRAP guard)"*

Giá trị đã validate của `pb_z` là **phi tuyến** (cờ `pb_z ≤ −1`) + **guard bẫy**. `value_score_v2`
dùng nó qua leg **TUYẾN TÍNH** `0.35·(0.5 − pb_z/2)`. Dùng một trục tuyến tính để thu hoạch một hiệu
ứng đuôi = **category error** — đúng như H3 dự đoán.

Bucket `pb_z` trong BANK (`mech_bank_pbz.py` [B]) — hiệu ứng đuôi **CÓ THẬT nhưng gần như KHÔNG BAO
GIỜ nổ trong ngân hàng**:

| bucket pb_z | n | fwd2M | fwd2M IS | fwd2M OOS |
|---|---|---|---|---|
| **≤ −1 (golden cell)** | **40 (3.9%)** | **+9.30%** | +9.64% | +9.19% |
| −1..−0.3 (cheap) | 99 | +6.55% | +8.06% | +6.01% |
| −0.3..0.3 (normal) | 88 | +4.91% | +2.46% | +5.50% |
| 0.3..1 (rich) | 159 | +6.32% | +6.82% | +6.21% |
| **> +1 (very rich)** | **290 (43%)** | **+2.06%** | −3.37% | +3.14% |

- Golden cell (thứ DUY NHẤT của `pb_z` đã validate) **chỉ nổ 3.9% số bank-quarter**, và **0.0% trong
  2017 / 2018 / 2021** (`mech_scale_drift.py` [1]).
- Phân phối `pb_z` ngân hàng **lệch phải nặng**: median **+0.71**, **30% > +1**, chỉ 3.9% < −1. Lý do
  kinh tế: ngân hàng VN **re-rate LÊN từ nền thấp**, nên PB gần như luôn nằm TRÊN trung bình trượt 5Y
  của chính nó. ⇒ với ngân hàng, `pb_z` **không đo "rẻ"** — nó đo **"PB đã tăng bao nhiêu so với quá
  khứ gần của chính nó"**, tức một dạng **drift/momentum chậm của định giá**, không phải mức rẻ.
- Chiều đơn điệu vẫn có (Q5−Q1 +5.85pp) nhưng **không đều** (bucket "rich" +6.32% > "normal" +4.91%)
  → đúng chữ ký "linear-dead, tail-alive".

## 11.3 Bằng chứng C — khuyết tật THANG ĐO TUYỆT ĐỐI: leg này không nói "bank nào", nó nói "bao nhiêu bank"

Đây là điểm cấu trúc sâu nhất (`mech_scale_drift.py`).

Mọi leg khác trong selector (`ey`/`cfy`/`ps` của v3latest, và cả leg `ey` của chính v2) đều là
**PERCENTILE — chuẩn hoá lại MỖI QUÝ**. Leg `pb_z` là **TUYỆT ĐỐI**: `(0.5 − pb_z/2).clip(0,1)`.

| | trung bình | **sd QUA CÁC QUÝ** | range |
|---|---|---|---|
| leg TUYỆT ĐỐI `(0.5 − pb_z/2)` — bản đang dùng | 0.343 | **0.235** | 0.000 … 0.863 |
| leg PERCENTILE của **cùng `pb_z` đó** (đối chứng) | 0.573 | **0.083** | 0.519 … 1.000 |

- **38.7% phương sai `pb_z` của ngân hàng là một CÚ DỊCH CHUNG của cả ngành** (không phải khác biệt
  bank-vs-bank). Trung bình `pb_z` ngành swing **−0.78 … +3.05 = 3.83 z-unit** → leg tuyệt đối dịch cả
  ngành **1.92 điểm**, trong khi **toàn bộ range của leg chỉ là 0..1**. Leg bị **cú dịch chung của
  ngành lấn át hoàn toàn**.
- Hệ quả: khi PB toàn ngành ngân hàng cùng nhích lên so với lịch sử 5Y của chúng, **MỌI bank cùng bị
  hạ điểm một lúc** → **bank bị đẩy khỏi top-30 hàng loạt** — vì một lý do **không liên quan gì đến
  việc bank nào hấp dẫn hơn bank nào**. Percentile thì **miễn nhiễm** theo cấu trúc: median bank luôn
  ~0.5, nên nó **chỉ có thể nói "bank NÀO", không bao giờ nói "BAO NHIÊU bank"**.
- Xác nhận trên rổ thật: slot ngân hàng theo quý (`mech_F_bank_slot_counts.csv`), Spearman(Δ slot do
  route fix, median `pb_z` ngành) = **−0.153** — ngành trông càng "đắt vs lịch sử chính nó", fix càng
  đuổi bank ra. Trong các quý 2017Q4–2019Q3 (median `pb_z` ngành +0.9…+2.8) fix cắt đều **−1..−2 slot**;
  2021Q4 (median +2.33) cắt **−3 slot**.
- **Và đó là một cú đặt cược ngành KHÔNG CÓ KỸ NĂNG**: Spearman(Δ slot ngân hàng, bank-trừ-nonbank
  fwd2M chính quý đó) = **+0.127** (n=47; IS +0.084 / OOS +0.145) ≈ 0. Nó cắt tỷ trọng ngân hàng mà
  **không hề phân biệt được quý tốt với quý xấu**.

⇒ "Xếp hạng bank cho đúng trong route" **âm thầm mua kèm một cú đặt cược THỜI ĐIỂM NGÀNH không được
kiểm soát**, định giá bằng một **trung bình trượt sổ sách 5 năm**. Không ai yêu cầu cú đặt cược đó.

## 11.4 Bằng chứng D — cỗ máy overweight ngân hàng, và vì sao nó TRẢ TIỀN

`1/PCF` sai bản chất cho ngân hàng **theo một chiều cố định** (`mech_scale_drift` + kiểm tra trực tiếp):

| | percentile TOÀN THỊ TRƯỜNG trên `cfy=1/PCF` | trên `ey=1/PE` | coverage PCF>0 |
|---|---|---|---|
| **ngân hàng** | **0.711** | 0.629 | 0.742 |
| phi-ngân-hàng | 0.496 | 0.498 | 0.590 |

Ngân hàng ngồi ở **percentile 71** của cả thị trường trên trục `1/PCF` — không phải vì rẻ, mà vì CFO
của họ là dòng huy động/cho vay. Phép cắt top-30 **chéo ngành** biến cái lệch đó thành **suất nhập rổ**.

**Tỷ trọng ngân hàng THẬT trong rổ 30 tên** (`members_*.csv`, 48 quý):

| arm | bank share FULL | **IS 2014-19** | **OOS 2020+** | bank/quý |
|---|---|---|---|---|
| **`yieldcombo` (production)** | **24.1%** | 10.3% | **35.8%** | **7.23** |
| `v3latest` | 15.1% | 7.7% | 21.3% | 4.52 |
| `v3route3` | 13.0% | 4.9% | 19.9% | 3.90 |

**Ngân hàng VN có thắng thật không?** (fwd2M, panel đông băng)

| | bank | non-bank | **chênh** |
|---|---|---|---|
| FULL 2014→2026 | +4.06% | +2.77% | **+1.29pp** |
| IS 2014-19 | +2.10% | +1.62% | **+0.47pp** |
| **OOS 2020+** | +4.95% | +3.56% | **+1.39pp** |

## 11.5 ⇒ ĐÂY CHÍNH LÀ LỜI GIẢI CHO CÂU HỎI GỐC (v3latest IS+1.40 / OOS−0.78)

Ghép hai bảng trên. `v3latest` cắt tỷ trọng ngân hàng **−2.6pp trong IS** nhưng **−14.5pp trong OOS**
(vì OOS `yieldcombo` chất tới 35.8% ngân hàng). Nhân với mức thắng của ngành từng cửa sổ:

| cửa sổ | Δ bank share (v3latest − yieldcombo) | × (bank − nonbank) | = drag / 2M | **≈ drag / năm (×6)** |
|---|---|---|---|---|
| IS 2014-19 | **−2.6pp** | × +0.47pp | −0.012pp | **−0.07pp/yr** ≈ 0 |
| **OOS 2020+** | **−14.5pp** | × +1.39pp | −0.201pp | **−1.21pp/yr** |

**Chữ ký khớp chính xác cái đã pin ở registry (IS +1.40 / OOS −0.78).** Diễn giải bằng tiếng người:

> **`v3latest` KHÔNG "hết thiêng" OOS. Nó vẫn chọn cổ phiếu tốt như thường — nhưng nó ĐANG SHORT
> ngành đã thắng, và OOS ngành đó thắng đậm hơn hẳn (×3).** Phần alpha chọn-tên của composite gần như
> không đổi giữa 2 cửa sổ; phần **chi phí underweight ngân hàng thì nhân ba**. Cộng lại → dấu lật từ
> `+` sang `−`. Không có "overfit IS" nào ở đây theo nghĩa cổ điển (fit nhiễu quá khứ) — có một **vị
> thế ngành ẩn** bị đổi mà không ai khai báo.

*Giới hạn của phép quy này (ghi rõ, không giấu):* đây là ước lượng **equal-weight per-slot ×6**, KHÔNG
phải NAV namecap theo ngày, và fwd2M chồng lấn nên ×6 là thô. Nó khớp **CHIỀU và ĐỘ BẤT ĐỐI XỨNG
IS-vs-OOS** của số đã pin, **không** phải một phép tái lập −0.78pp. Dùng nó như bằng chứng cơ chế, đừng
quote như một con số hệ.

*Một proxy khác đã THẤT BẠI, ghi lại thay vì giấu:* phân rã Brinson equal-weight per-slot
(`mech_attribution.py`) cho dR IS **+0.052** — **sai dấu** so với cấp hệ (−2.56pp). Tôi **không dùng**
nó để quy công. Đúng bài học §10.4: proxy equal-weight đảo dấu với đúng họ selector này.

## 11.6 Các giả thuyết dispatch — phán quyết từng cái

| GT | Nội dung | Phán quyết | Bằng chứng |
|---|---|---|---|
| **H1** | `1/PCF` "sai" nhưng tình cờ mang thông tin qua kênh khác (tăng trưởng bảng cân đối) | ✅ **XÁC NHẬN — và mạnh hơn dự đoán** | Không chỉ "tình cờ có tin": nó là **lệch có hệ thống một chiều** → bank ở percentile 71 vs 49.6 → **overweight ngành cơ học**, và ngành đó thắng +1.29pp/2M. Kênh thật KHÔNG phải "thị trường thưởng tăng trưởng tín dụng" mà là **phép cắt chéo ngành biến lỗi đo thành tỷ trọng**. |
| **H2** | `pb_z` thấp = ngân hàng RỦI RO, không phải "rẻ" | ❌ **BÁC** | Bank `pb_z` thấp nhất mỗi quý: fwd2M **+5.08%** vs toàn bank **+4.06%** — **tốt hơn**, không phải bẫy. Không có chữ ký rủi ro đuôi (`mech_D_cheapest_bank.csv`; STB 2019-20 −1.5→−2.7 z rồi +24%/+41%, VBB 2022 +31.9%). Sòng phẳng: điểm này của finding gốc đứng vững. |
| **H3** | IC +0.136 đo cho MỤC ĐÍCH KHÁC → category error | ✅ **XÁC NHẬN (2 tầng)** | (a) `rating_8l.py:646` **tự ghi** `pb_z` "LINEAR-DEAD (golden-cell flag only)" — giá trị đã validate là **phi tuyến + trap guard**, bị dùng như leg **tuyến tính**. (b) Bản thân **+0.136 không truy vết được** — chỉ là comment, không artifact; đo lại được **+0.065 (t=1.17)**. |
| **H4** | Time-varying: chế độ ngân hàng VN đổi quanh 2020 | ⚠️ **KHÔNG ủng hộ (không có breakpoint)** | IC `pb_z` theo năm nhảy loạn 2 chiều cả trước lẫn sau 2020 (2016 −0.250 / 2018 +0.201 / 2020 +0.294 / 2021 −0.019 / 2023 −0.129 / 2025 +0.201) — **nhiễu, không phải gãy chế độ**. Cái ĐỔI quanh 2020 không phải `pb_z`, mà là **mức thắng của NGÀNH** (+0.47 → +1.39pp) và **tỷ trọng bank mà yieldcombo tự chất lên** (10.3% → 35.8%). |
| **H5** | v3latest lỗi ở trục không liên quan bank | ❌ **BÁC — vấn đề ĐÚNG là ở trục bank** | Phân rã đã pin (job 121717) + §11.5: toàn bộ độ bất đối xứng IS/OOS của v3latest quy về **thay đổi tỷ trọng ngân hàng**, đúng trục đang tranh luận. |
| **H6** *(thêm mới)* | Leg **TUYỆT ĐỐI** trong phép cắt **CHÉO** ngành = cược thời điểm ngành ẩn | ✅ **XÁC NHẬN** | §11.3: 38.7% phương sai là cú dịch chung; sd-qua-quý 0.235 (tuyệt đối) vs 0.083 (percentile); Spearman(Δslot, median pb_z ngành) −0.153; kỹ năng timing ≈ 0 (+0.127). |

## 11.7 ⚠️ RỦI RO MỚI PHÁT HIỆN — cần Mike/user quyết (KHÔNG wire gì)

Nghiên cứu này lộ ra một sự thật về **production đang chạy**, không phải về ứng viên bị loại:

> **custom30V production đang mang một vị thế OVERWEIGHT NGÂN HÀNG lớn, KHÔNG AI CHỦ Ý ĐẶT, và
> KHÔNG AI QUẢN.** 24.1% rổ toàn kỳ, **35.8% trong OOS 2020+**, có quý lên tới **15/30 tên** (2025Q2-Q3).
> Nó **không đến từ một quyết định** — nó là **tác dụng phụ của một lỗi đo lường** (`1/PCF` cho ngân
> hàng), đúng thứ user chỉ ra hôm nay.

Hai điều cần tách bạch khi quyết:
1. **Nó đã trả tiền** (+1.29pp/2M, **LOO 13/13 năm đều dương**, min +0.755 khi bỏ 2017) — nên "sửa cho
   đúng lý thuyết" = **phá giá trị thật**, đã chứng minh 2 lần (−0.78pp OOS, −2.38pp).
2. **Nhưng bằng chứng thống kê MỎNG**: spread bank-trừ-nonbank theo quý **t = 0.80, hit 46.9%**
   (IS t=0.25 / OOS t=0.83). ⇒ **KHÔNG phải alpha đã validate.** Nó là một **cú đặt cược ngành dai
   dẳng, sinh ra do tai nạn, đang thắng.**

**Hàm ý thẳng thắn:** không arm nào trong cuộc tranh luận này có alpha định giá đã validate ở tầng
ngân hàng. Cuộc so sánh `yieldcombo` vs `v3route` **được quyết định bởi một cú đặt cược ngành ngoài ý
muốn**, chứ **không phải bởi độ chính xác của thước đo** — đúng như user nghi ngờ rằng "thống kê thuần
có thể sai lệch logic", chỉ là nó sai lệch theo hướng **ngược** với dự đoán ban đầu.

Câu hỏi cho user/Mike (**không phải việc tôi tự quyết**): 24-36% rổ đỗ tiền nằm ở ngân hàng — **đó có
phải vị thế ta MUỐN giữ có chủ ý không?** Nếu CÓ → nên khai báo tường minh (một rule tỷ trọng ngành ta
kiểm soát được), thay vì để nó tiếp tục phát sinh như tác dụng phụ của một lỗi đo lường mà ta **đã biết
là lỗi**. Nếu KHÔNG → cũng đừng "sửa" bằng cách đổi selector: đã đo 2 lần, đổi selector làm hệ tệ đi.
Đây là câu hỏi **risk-concentration**, hợp lý để hỏi thêm Spyros. **Tôi không đề xuất thay đổi gì.**

## 11.8 Việc KHÔNG làm trong job này (đúng phạm vi dispatch)

- **Không** backtest sâu hướng route-aware khác. Có 1 hướng đáng ghi nhận **nhưng KHÔNG tự theo đuổi**:
  nếu muốn giữ tinh thần "chấm bank bằng thước đo của bank" mà **không** phá tỷ trọng ngành, dạng đúng
  là **percentile trong route** (§11.3 cho thấy nó ghim ~0.5, chỉ đổi "bank nào" chứ không đổi "bao
  nhiêu bank"). **Nhưng prior THẤP**: `pb_z` trong bank có IC +0.065 (t=1.17) — gần như không có gì để
  thu hoạch, và `1/PE` đã làm hết việc. Cần Mike/user quyết có mở dự án riêng không; **tôi không mở**.
- **Không** re-pin R3 (vẫn treo từ §10.9). **Không** sửa `rating_8l.py` (kể cả comment `+0.136` không
  truy vết được — sửa production giữa job research là sai, §3 coding_guidelines). Đề xuất: ai đó dọn
  comment đó thành "không truy vết được" trong một task riêng, kèm skeptic.

**Artifacts §11** (`route_exp/`): `mech_bank_pbz.py`, `mech_attribution.py`, `mech_scale_drift.py` ·
`mech_A_bank_linear_ic.csv`, `mech_A_bank_ic_by_year.csv`, `mech_B_pbz_buckets.csv`,
`mech_B_pbz_quintiles.csv`, `mech_C_bank_pick_profile.csv`, `mech_D_cheapest_bank.csv`,
`mech_E_{composition,brinson,dropped,added,crossroute}.csv`,
`mech_F_{sector_pbz,bank_slot_counts,timing_bet,leg_scales}.csv`.

---

# §12. THIẾT KẾ TỔNG HỢP `v4final` — 3 bước selector + giả thuyết DY-floor (job `Taylor_20260714_140127`)

Đây là thiết kế tổng hợp cuối theo 4 ý user sau khi xem trọn chuỗi 112932 → 121717 → 132942. Không
phải "thêm 1 biến thể thử nghiệm". Kết quả gồm **1 phát hiện đính chính premise của cả ngày**, **2/3
bước selector KHÔNG mất gì nhưng cũng KHÔNG được gì**, **1 bước NO-GO rõ ràng**, và **1 giả thuyết
của user ĐƯỢC DỮ LIỆU ỦNG HỘ**.

## 12.0 VERDICT NGẮN

| Ý user | Kết quả | Verdict |
|---|---|---|
| 1. Bỏ 1/PCF khỏi BANK/INS/SEC (`eyfin`) | FULL +0.08pp (IS −0.21 / OOS +0.37) | **TRUNG TÍNH** — không mất, không được |
| 2. Chỉ dùng ey cross-route (`eyonly`) | FULL −0.13pp vs A1; DD −18.1→−17.6, Calmar +0.04 | **TRUNG TÍNH**, rủi ro nhích tốt |
| 3. Cap tài chính 30% (`fincap`) | FULL **−0.64pp**, Sharpe −0.06, **DD KHÔNG đổi** | **NO-GO** (mua bảo hiểm không nhận được gì) |
| 4. DY = ngưỡng chặn giá (không phải return-predictor) | 6M: downside nông hơn **+2.34pp** (t=2.37, hit 68%), return KHÔNG hơn (t=0.17) | **ĐƯỢC ỦNG HỘ** tại 6M; 3M không |

**Không wire gì.** Bước 1+2 là ứng viên **đáng cân nhắc trên cơ sở NGUYÊN LÝ** (bỏ thước đo sai bản
chất, 2 chỉ tiêu → 1), **KHÔNG phải trên cơ sở alpha** — số đo nói "miễn phí", không nói "tốt hơn".
Bắt buộc quant-skeptic trước mọi cân nhắc wire.

## 12.1 ⚠️ ĐÍNH CHÍNH PREMISE — con số "24.1% / 35.8% / đỉnh 50%" là ĐẾM TÊN, KHÔNG PHẢI TỶ TRỌNG

Phát hiện quan trọng nhất của job này, và nó **sửa chính §11.7 ở trên**.

Cả ngày hôm nay (dispatch, §11.4/§11.7, và phần tư vấn của risk-auditor) đều neo vào "overweight ngân
hàng 24.1% cả kỳ / 35.8% OOS / đỉnh ~50%". Đo lại trên **vector tỷ trọng ngày THẬT** của chính
custom30V production (`reconcile_finweight.py`, `finweight_definitions.csv`):

| Định nghĩa | share ĐẾM TÊN (full / IS / OOS / đỉnh quý) | share TỶ TRỌNG (full / IS / OOS) |
|---|---|---|
| **BANK only** | **0.239 / 0.102 / 0.354 / 0.500** | **0.444 / 0.255 / 0.603** |
| BANK+INS+SEC | 0.305 / 0.146 / 0.439 / 0.587 | 0.474 / 0.272 / 0.644 |

Hàng **BANK-only, cột ĐẾM TÊN** tái lập **chính xác cả ba** con số đã lưu hành: 23.9% ≈ 24.1%, 35.4%
≈ 35.8%, đỉnh quý 50.0% = "đỉnh ~50%" (=15/30 tên). ⇒ **Con số đó là tỷ lệ ĐẾM TÊN của route BANK
trong rổ 30, không phải tỷ trọng vốn.**

**Tỷ trọng vốn thật gần GẤP ĐÔI: 44.4% toàn kỳ / 60.3% OOS 2020+ / 2026Q2 = 82.7%** (BANK+INS+SEC;
`fin_weight_by_quarter.csv`). Rổ đỗ tiền custom30V hôm nay **hơn 4/5 là tài chính theo vốn**.

Ba hệ quả phải nói thẳng:
1. **§11.7 vẫn đúng về bản chất nhưng NHẸ TAY một nửa** — vị thế ngành ngoài chủ ý còn lớn hơn đã báo.
2. **Lời khuyên "cap 30% là hợp lý" của risk-auditor được đưa ra trên nền 24.1%** — tức cap 30% khi đó
   **nghe như một trần rộng rãi, gần như không ràng buộc**. Trên tỷ trọng thật (47%) nó là **can thiệp
   cắt ~một nửa exposure**, ràng buộc 100% số ngày từ 2017Q1. Đây là hai chính sách khác hẳn nhau đội
   chung một cái tên. **Cần đưa lại số đúng cho risk-auditor/Spyros trước khi coi "30%" là đã có tư vấn.**
3. Chính là lớp lỗi cả ngày nay đang truy: **so hai đại lượng không cùng thứ nguyên**. Lần này nó
   không nằm trong code, nó nằm trong **cách chúng ta trích dẫn số cho nhau**.

## 12.2 Chuỗi ablation NEO LIỀN KỀ (mỗi arm khác arm ngay trước ĐÚNG 1 trục)

Chạy `run_arms.sh`, cùng vintage/config (`NAV_TOTAL_B=50 ETF_LIQ=custompitg PARK_STATES=3:0.7
AUDIT_END=2026-06-19`, threads=1, `EXP_TAG` mọi arm kể cả baseline → §8 an toàn).
**self-check 0 VND (BAL+LAG) cả 4 arm**, borrow 0 VND, max gross 1.000.

| arm | thay đổi vs arm trước | FULL | IS | OOS | Sharpe | MaxDD | Calmar |
|---|---|---|---|---|---|---|---|
| **A0** `yieldcombo`+namecap | = production LIVE | 27.09 | 23.37 | 30.58 | 1.81 | −18.3 | 1.48 |
| **A1** `eyfin` | financial bỏ chân 1/PCF (2×ey giữ nguyên range) | 27.17 | 23.16 | 30.95 | 1.82 | −18.1 | 1.50 |
| **A2** `eyonly` | mọi route chỉ 1 chỉ tiêu `rank_pct(1/PE)` | 27.04 | 23.00 | 30.85 | 1.81 | −17.6 | 1.54 |
| **A3** `eyonly`+`fincap0.30` | cap BANK+INS+SEC 30% | **26.40** | 22.45 | 30.12 | **1.75** | −17.6 | 1.50 |

**Delta neo liền kề:**
- **A1−A0 (bỏ PCF khỏi financial): +0.08pp FULL / −0.21 IS / +0.37 OOS.** Trái dấu IS-OOS, biên độ
  ~0.1-0.4pp trên 12.5 năm ⇒ **nhiễu, không phải edge**. Đọc đúng: bỏ thước đo sai cho ngân hàng
  **không làm hệ tệ đi** — nhưng cũng **không** phải "sửa cho đúng thì thắng".
- **A2−A1 (gộp về 1 chỉ tiêu): −0.13pp FULL, DD tốt hơn 0.5pp, Calmar +0.04.** Cũng trong nhiễu.
- **A2−A0 (cả bước 1+2 vs production): −0.05pp FULL / −0.37 IS / +0.27 OOS; DD −18.3→−17.6;
  Calmar 1.48→1.54.** ⇒ **return-neutral, rủi ro nhích tốt nhẹ (1 đường NAV, chưa chứng minh bền).**
- **A3−A2 (cap 30%): −0.64pp FULL / −0.55 IS / −0.73 OOS, Sharpe −0.06, và DD ĐỨNG YÊN −17.6.**

## 12.3 Vì sao cap 30% là NO-GO — và lần này KHÔNG suy diễn từ kết quả sáng nay

Dispatch yêu cầu đúng điều này: sáng nay sector-cap NO-GO nhưng cap đó áp lên pool **đã nhiễm bias
PCF**; lần này pool **đã sạch bias** (A2) trước khi cap. Kết luận **vẫn NO-GO, và mạnh hơn**:

> Cap lấy đi **0.64pp CAGR/năm đều cả IS lẫn OOS**, và **đổi lại KHÔNG được gì đo được**: MaxDD
> −17.6% → −17.6% (**không đổi**), Sharpe **xấu đi** 1.81→1.75, Calmar xấu đi 1.54→1.50.

Đây không phải "bảo hiểm đắt" — bảo hiểm ít nhất phải **trả tiền khi cháy**. Cắt exposure tài chính từ
47% xuống 26% mà **drawdown không nhúc nhích** nghĩa là: **tập trung tài chính KHÔNG phải nguồn gây
drawdown của hệ** trong 2014-2026. DD của hệ đến từ beta thị trường chung; ngân hàng trong pool này
không sụt sâu hơn thứ thay thế nó. Cap chỉ **đổi tên cầm** chứ không **đổi rủi ro đường giá**.

**Cảnh báo trung thực về giới hạn của kết luận này:** nó chỉ nói "không có cú sốc riêng ngành ngân hàng
trong 12.5 năm mẫu". Nó **không** bác rủi ro tập trung theo nghĩa kịch bản/đuôi (một cú sốc hệ thống
ngân hàng VN chưa từng xảy ra trong mẫu). Điểm risk-auditor nêu về **độ trễ cam kết CRISIS của DT5G
(enC=25 phiên)** vẫn đứng nguyên và **backtest này không trả lời được nó** — nó là câu hỏi kịch bản,
không phải câu hỏi lịch sử. ⇒ Nếu user muốn cap, hãy cap **vì lý do quản trị rủi ro đuôi có tuyên bố
rõ ràng, chấp nhận trả 0.64pp/năm**, chứ **đừng** cap vì tin rằng backtest cho thấy nó an toàn hơn —
số đo nói ngược.

## 12.4 Ý 4 — DY là NGƯỠNG CHẶN, không phải trục xếp hạng: **CLAIM ĐƯỢC ỦNG HỘ (6M)**

Test đúng câu hỏi bất đối xứng user đặt ra (`dy_floor_test.py`), **không** test IC(DY, return):
panel 2,878 quan sát / 262 mã / 48 ngày q2m5 2014-2026, DY = `Dividend_Min3Y`/`Price` (as-of
`Release_Date`, PIT), downside = `min(Close)/Close₀−1` trên Close **điều chỉnh** (cổ tức đã nằm sẵn
trong đường giá ⇒ mã DY cao **không** thể ăn gian bằng chính việc trả cổ tức).

Claim chỉ ĐƯỢC ỦNG HỘ khi **(a) downside nông hơn có ý nghĩa VÀ (b) return KHÔNG tốt hơn** — (b) quan
trọng ngang (a): nếu DY cao cũng lãi hơn thì DY chỉ là return-predictor khoác áo "ngưỡng chặn", và chỗ
của nó là trục xếp hạng chứ không phải rule chặn.

| cut | h | d_maxloss (HIGH−LOW) | t | hit/ngày | d_return | t | verdict |
|---|---|---|---|---|---|---|---|
| route×date | 3M | +0.80pp | 1.40 | 60% | −0.57pp | −0.56 | không |
| route×date | 6M | **+2.07pp** | **2.75** | **77%** | +0.48pp | 0.31 | **FLOOR** |
| route×date×**ey-tertile** | 6M | **+2.34pp** | **2.37** | **68%** | +0.35pp | 0.17 | **FLOOR** |
| **marginal cohort (ey rank 20-45)** | 6M | **+2.40pp** | **2.37** | **68%** | +2.95pp | 1.39 | **FLOOR** |

**Đọc kết quả:**
- Ở **6M**, mã DY cao sụt **nông hơn ~2.1-2.4pp**, và **quan trọng nhất: vẫn đúng sau khi khử ey**
  (double-sort trong ey-tertile: +2.34pp) ⇒ **không phải chỉ là hiệu ứng "rẻ" mà selector đã chấm rồi**
  — đây chính là confound nguy hiểm nhất và nó đã bị kiểm soát tường minh.
- Return **không** tốt hơn có ý nghĩa (t = 0.17-1.39 < 2) ⇒ **đúng chữ ký bất đối xứng user mô tả**:
  "không cho biết tăng đến đâu, nhưng chặn không cho giảm sâu".
- **3M KHÔNG được ủng hộ** (t=1.40-1.94) ⇒ hiệu ứng cần thời gian; đây là ngưỡng chặn dài hạn, không
  phải đệm phiên-tới-phiên.

**Sòng phẳng về giới hạn (không tự cứu giả thuyết):**
- t-stat **lạc quan** vì cửa sổ 6M chồng lấn + tên tương quan trong cùng ngày. Số đáng tin hơn là
  **hit-rate theo NGÀY: 68-77% trên 44-48 ngày độc lập hơn** (nhị thức 68%/44 ngày ⇒ p≈0.01). Vẫn đứng.
- Cohort biên có **d_return +2.95pp (t=1.39)** — không có ý nghĩa thống kê, nhưng **không nhỏ**. Nếu N
  lớn hơn làm nó thành có ý nghĩa thì DY tụt về loại "return-predictor", và khi đó **chỗ của nó là
  trục xếp hạng, không phải rule chặn**. Chưa kết luận được với N hiện có — **phải nói ra, không lờ đi**.
- Coverage: DY>0 chỉ trên **70.4%** quan sát ⇒ rule phải fail-open cho 30% còn lại.

**Đề xuất tích hợp (ý 4b) — PRE-REGISTER, CHƯA CHẠY, KHÔNG WIRE:**
Đúng vai "ngưỡng chặn", **không** ép vào công thức cộng điểm tuyến tính:
> **DY chỉ được quyền TIE-BREAK trong dải biên** (ey rank ~20-45, đúng cohort đã đo có hiệu ứng, và là
> chỗ duy nhất tie-break đổi được quyết định): trong dải biên, ưu tiên DY cao hơn khi lấp đủ 30 slot.
> Ngoài dải biên không đụng. Thiếu DY → giữ nguyên thứ tự ey (fail-open, không phạt).
Đây là **1 arm mới (A4)**, cần: selfcheck riêng (OFF byte-identical; chỉ dải biên bị đổi; thiếu DY =
no-op), N-ledger khai báo, **và quant-skeptic**. **Job này KHÔNG chạy A4** — chạy thêm 1 biến thể ở
cuối phiên đúng bằng cách sinh ra thứ mà cả ngày nay ta vừa mất công bác. Cần Mike/user quyết mở.

## 12.5 Bức tranh rổ tại rebal 2026-05-05 (`basket_20260505.md`)

| arm | tên tài chính | vs A0 |
|---|---|---|
| A0 (LIVE custom30V) | **18/30** | — |
| A1 `eyfin` | 17/30 | giữ 29/30 · IN `HPG` · OUT `MBS` |
| A2 `eyonly` | 16/30 | giữ 27/30 · IN `HPG`,`PNJ`,`SAB` · OUT `MBS`,`VCB`,`VGC` |
| A3 `eyonly`+cap30 | 16/30 | giữ 27/30 · IN `HPG`,`PNJ`,`SAB` · OUT `MBS`,`VCB`,`VGC` |

Lưu ý: **A3 chọn CÙNG 30 tên như A2** — cap là rule **tỷ trọng**, không đổi thành phần. Thay đổi thành
phần rất nhỏ (giữ 27-29/30) trong khi **tỷ trọng** đổi rất lớn (47%→26%) — thêm một minh hoạ cho §12.1:
**đếm tên và tỷ trọng là hai đại lượng khác nhau, đừng đọc cái này rồi kết luận cái kia.**

`HPG IN` trùng hướng với lệnh basket-swap trong plan 07-14/07-15 (bán HPG) — **nhưng đây KHÔNG phải
căn cứ đảo lệnh**: A1/A2 chưa qua skeptic, delta nằm trong nhiễu, và job này không đề xuất wire.

## 12.6 Xác nhận cap 30% giữ ĐÚNG trong thực tế (không chỉ tin code)

`v4final_selector_selfcheck.py` **12/12 PASS**, đo trên vector tỷ trọng thật:
- **fincap@0.30: max 0.3000 / mean 0.2995 trên 1090 ngày, 0 ngày vượt, 0 ngày infeasible.** Σw=1 mọi
  ngày (sai số 4.4e-16). Full panel 2014-2026 (`fin_weight_summary.csv`): **0.0% số ngày > 30%**.
- Bug thật đã bắt được nhờ đo thay vì tin: **`weight_scheme=sectorcap` có sẵn KHÔNG giữ được cap** —
  `_cap_names` chạy SAU `_cap_sector` và water-fill phần dư vào **mọi** tên chưa chạm trần, **kể cả
  financial** ⇒ cap danh nghĩa 0.30 thực giao **mean 0.427 / max 0.542, vi phạm 1090/1090 ngày**. Vì
  vậy dùng `_cap_group_jointly` (cấp ngân sách nhóm trước, water-fill name-cap TRONG từng nhóm) chứ
  không tái dùng `sectorcap` như dispatch gợi ý. **Nếu đã tái dùng `sectorcap`, arm A3 sẽ đo nhầm một
  cap 0.43 rồi gán nhãn 0.30.**
- `eyonly` không đọc PCF (đảo dấu toàn bộ PCF → 0 tên đổi); `eyfin` không đọc PCF cho financial (255
  pick, 0 khác) + **negative control**: cùng phép phá đó **CÓ** làm `yieldcombo` đổi 17/18 rebal ⇒ phép
  thử không phải no-op. OFF-path byte-identical vs `git show HEAD:custom_basket.py`.

## 12.7 VERDICT + việc còn treo

**Không wire gì. Không đụng production. Không đảo lệnh plan 07-14/07-15.**

- **Bước 1+2 (`eyonly`)**: ứng viên hợp lệ **về nguyên lý** (bỏ 1/PCF — thước đo sai bản chất cho ngân
  hàng; 2 chỉ tiêu → 1; triệt tiêu hẳn lớp lỗi thang-đo cross-route đã giết `v3route`), với bằng chứng
  **"không tốn gì"** (−0.05pp FULL, trong nhiễu) và rủi ro **nhích tốt** (DD +0.7pp, Calmar +0.06).
  **KHÔNG có bằng chứng alpha** — ai muốn wire phải wire vì **tính đúng đắn của mô hình**, không phải
  vì kỳ vọng lãi hơn. **Bắt buộc quant-skeptic.**
- **Bước 3 (cap 30%)**: **NO-GO** — trả 0.64pp/năm, DD không đổi, Sharpe xấu đi.
- **Ý 4 (DY floor)**: **claim của user ĐƯỢC ỦNG HỘ tại 6M**, kể cả sau khi khử confound giá rẻ. Đề xuất
  tích hợp dạng tie-break dải biên đã pre-register ở §12.4 — **chờ user/Mike quyết có mở arm A4**.
- **Treo (không thuộc job này):** (a) đưa **số tỷ trọng ĐÚNG (47% full / 82.7% 2026Q2)** lại cho
  risk-auditor/Spyros — tư vấn "cap 30% hợp lý" đã cho trên nền 24.1% đếm-tên; (b) re-pin R3 (vintage
  hôm nay 27.09 vs pin 27.84, treo từ §10.9); (c) sửa/chú thích §11.7 theo đính chính §12.1.

**Artifacts §12** (`v4final_exp/`): `run_arms.sh`, `dy_floor_test.py`, `basket_picture.py`,
`reconcile_finweight.py` · `logs/v4f_A{0,1,2,3}_*.log`, `logs/dy_floor.log` ·
`dy_floor_panel.csv`, `dy_floor_results.csv`, `fin_weight_by_quarter.csv`, `fin_weight_summary.csv`,
`finweight_definitions.csv`, `basket_20260505.md`. Code: `custom_basket.py` (`eyfin`/`eyonly`/`fincap`,
nhánh mới, nhánh cũ không đụng), `v4final_lib.py`, `v4final_selector_selfcheck.py`.

---

# §13. ĐỊNH HƯỚNG DÀI HẠN CHO SELECTOR — chỉ đạo của user (chủ tài khoản), 2026-07-14

Ghi lại nguyên văn ý chính sau khi user xem trọn kết quả ngày 2026-07-14 (chuỗi 112932 → 121717 →
132942 → 140127). **Đây là GHI CHÉP ĐỊNH HƯỚNG cho các phiên nghiên cứu SAU, không phải kết quả đo,
không phải yêu cầu backtest, và không mở rộng phạm vi bất kỳ job nào đang chạy.** Không diễn giải
thêm ngoài 4 ý dưới; phần "ghi chú neo" chỉ trỏ tới thứ ĐÃ có trong hệ thống để phiên sau không phải
đi tìm lại.

## 13.1 `ey` (1/PE) = thước đo THỰC DỤNG cho GIAI ĐOẠN NÀY — không phải điểm đến cuối cùng

> VN là thị trường mới nổi, trình độ nhà đầu tư trung bình chưa cao ⇒ một thước đo **đơn giản** phù
> hợp với giai đoạn này.

Ghi chú neo: khớp với số đo hiện có — 1/PE là factor mạnh nhất và route-neutral của hệ (KB: IC
+0.125, 94% hit; "Value dominates ALL regimes"; trong chính route BANK: IC +0.181 t=3.79, mạnh hơn cả
`pb_z` lẫn 1/PCF). Chấp nhận `ey` ở đây là chấp nhận **có ý thức về giai đoạn**, không phải kết luận
rằng `ey` là thước đo đúng nhất về bản chất.

## 13.2 Dài hạn: chỉ tiêu DÒNG TIỀN vẫn là mục tiêu đúng — cần XÂY, không phải bỏ

> Earnings (PE) có thể bị bóp méo bởi thủ thuật kế toán; dòng tiền hoạt động khó làm giả hơn. Nên một
> chỉ tiêu cash-flow **được xây ĐÚNG** (khác 1/PCF hiện tại — đang lệch cho ngân hàng) sẽ tách bạch
> doanh nghiệp tốt/xấu tốt hơn về lâu dài. **Đây là hướng cần XÂY DỰNG cho tương lai, không phải bỏ hẳn.**

Ghi chú neo: phân biệt rõ hai việc — §11/§12 bác **1/PCF như đang dùng** (thước đo sai bản chất khi áp
cho ngân hàng, xem §11.3), **KHÔNG** bác trục dòng tiền nói chung. `eyonly` (A2) là bước **lùi có chủ
đích** khỏi một thước đo sai, không phải tuyên bố "dòng tiền vô dụng". Yêu cầu bất biến cho bản xây
mới: phải **kháng thao túng** (manipulation-resistant) và phải **so sánh được chéo ngành** — chính lớp
lỗi thang-đo cross-route đã giết `v3route`.

## 13.3 Ngân hàng: trọng tâm là CHẤT LƯỢNG TÀI SẢN, không chỉ lợi nhuận ngắn hạn

> Ngành ngân hàng cần chú trọng **chất lượng tài sản** (không chỉ lợi nhuận ngắn hạn). Tham chiếu lại
> `banking_valuation_framework.md` / sector-lens **đã có sẵn** trong hệ thống thay vì tự phát minh lại
> phán đoán ngân hàng trong `custom_basket.py`.

Ghi chú neo: `mike/agents/Taylor/banking_valuation_framework.md` đã tồn tại. Chỉ đạo ở đây là **tái
dùng**, không tái phát minh — cùng nguyên tắc đã áp cho route map (`value_panel_2014.csv` dùng chung
với router của `rating_8l.py` để định nghĩa route không trôi giữa 2 engine).

## 13.4 Xếp hạng chéo ngành nên THAM KHẢO sector lens, không chỉ 1 factor toàn cục

> Ranking chéo ngành nên **tham khảo** Group-A 6-state sector lens (đã có trong `sector_lens_monitor.py`),
> không chỉ dựa 1 factor toàn cục (`ey`) đơn thuần. **Đây là gợi ý cho thiết kế TƯƠNG LAI, không phải
> yêu cầu backtest hôm nay.**

Ghi chú neo (bắt buộc đọc trước khi phiên sau thiết kế): `sector_lens_monitor.py` (repo root, **không**
nằm trong thư mục Taylor) tự ghi rõ lens Group-A là **NECESSARY-NOT-SUFFICIENT** — *"every Group-A lens
failed OOS as a standalone book (Rule 3)"* — và công cụ này là **display/audit, KHÔNG phải selector tự
động**. Khớp với KB sector sweep #1-9: *"tất cả = lens/tilt, không phải standalone book"*. Vì vậy chữ
**"tham khảo"** trong ý user là đúng nghĩa đen và phải giữ đúng nghĩa đen: lens vào như **ngữ cảnh/
tie-break/tilt**, **không** được nâng thành trục xếp hạng chính. Phiên sau đề xuất bất cứ dạng tích hợp
nào cũng phải neo vào ràng buộc này, nếu không sẽ tái lập đúng thứ đã bị bác OOS.

## 13.5 Ràng buộc thủ tục khi phiên sau mở hướng này

Không có gì trong §13 được wire thẳng. Mọi ứng viên sinh ra từ 4 ý trên vẫn phải qua đủ chuỗi hiện
hành: **ablation neo liền kề** (mỗi arm khác neo đúng 1 trục, §12.2) → **self-check 0 VND** →
**walk-forward IS/OOS** → **N-ledger + DSR** (Rule 5, multiple-testing discipline) → **quant-skeptic** →
user duyệt. §13 chỉ nói **hướng nào đáng đào**, không cấp miễn trừ cho hướng nào.

---

# §14. ARM A4 (DY tie-break) + QUÉT CAP THEO ĐỈNH — job `Taylor_20260714_152605`

Hai câu hỏi độc lập, mỗi câu 1 trục lệch khỏi neo A2 (`eyonly`), cùng vintage/config/session
(`NAV_TOTAL_B=50 ETF_LIQ=custompitg PARK_STATES=3:0.7 AUDIT_END=2026-06-19`, threads=1, `EXP_TAG` mọi
arm → §8 an toàn). **A2 được CHẠY LẠI trong chính phiên này** làm neo (số của job 140127 là số khác
phiên — không phải neo hợp lệ). self-check 0 VND cả 6 arm. Mọi số dưới đây **recompute độc lập từ CSV**
(`extract_peryear.py` + recompute MaxDD/Sharpe riêng), không đọc dòng print của script.

## 14.0 VERDICT NGẮN

| Việc | Kết quả | Verdict |
|---|---|---|
| **1. A4 — DY tie-break dải biên (ey 20-45)** | FULL **−0.00pp** (IS ±0.00 / OOS −0.01); **MaxDD −17.6 → −18.6 (XẤU ĐI 1.0pp)**; Calmar 1.54→1.45 | **NO-GO** |
| **2. Cap theo đỉnh, quét X ∈ {45,50,55,60}%** | chi phí 0.23-0.84pp/năm, **KHÔNG ĐƠN ĐIỆU**; **MaxDD ĐỨNG YÊN −17.6 ở MỌI mức**; **DD_IS XẤU ĐI** −15.3→−16.1 | **NO-GO mọi mức** |

**Không wire gì. Production 0 chạm.** Không có ứng viên nào cần quant-skeptic (không có kết quả sạch
để verify — cả hai đều tự bác).

## 14.1 Việc 1 — A4: DY tie-break là **NO-GO**, và nó thất bại ĐÚNG Ở CHỖ nó được kỳ vọng

Cơ chế đã được kiểm chứng trước khi đo (`a4_dy_selfcheck.py` **17/17 PASS**): band-only (ranks 1-19
bit-identical vs A2 trên cả 48 rebal), **fail-open đúng (140/140 tên không có DY>0 giữ NGUYÊN rank —
không bị đánh tụt)**, permutation-not-recut (tên có DY chiếm đúng slot cũ), OFF-path tái lập A2 chính
xác, và **negative control: 48/48 rebal ĐỔI thành phần** ⇒ luật KHÔNG hề trơ. DY>0 coverage trong rổ
A4 = 66.0% (950/1440 name-rebal), khớp mức 70.4% đã đo ở §12.4.

| arm | FULL | IS | OOS | Sharpe | MaxDD | Calmar | DD_IS | DD_OOS |
|---|---|---|---|---|---|---|---|---|
| **A2** `eyonly` (neo) | 27.04 | 23.00 | 30.85 | 1.80 | −17.6 | 1.54 | −15.3 | −17.6 |
| **A4** `eyonly`+DY 20:45 | **27.04** | **23.00** | **30.84** | 1.82 | **−18.6** | **1.45** | −15.2 | **−18.6** |

**Đọc kết quả — đây là một kết quả SẠCH và nó nói KHÔNG:**
- **Return neutral tới mức gần như tuyệt đối**: FULL −0.00pp, IS ±0.00pp, OOS −0.01pp. Trong khi
  **48/48 rebal đổi thành phần**. Một luật đảo tên ở MỌI kỳ mà tổng cộng lại đúng bằng 0 ⇒ **chữ ký
  của reshuffle noise thuần tuý**, không phải của một trục thông tin.
- **Và nó XẤU ĐI ĐÚNG Ở METRIC NÓ ĐƯỢC MUA VỀ ĐỂ CẢI THIỆN**: DY được đưa vào **chỉ vì** §12.4 đo được
  hiệu ứng **downside nông hơn** (+2.34pp, t=2.37, hit 68%). Ở cấp danh mục, MaxDD **sâu THÊM 1.0pp**
  (−17.6 → −18.6), toàn bộ nằm ở OOS (DD_OOS −17.6 → −18.6). Calmar 1.54 → 1.45.
- Sharpe nhích 1.80→1.82 — không cứu được gì: đó là 1 đường NAV, và nó đi kèm DD sâu hơn 1pp.

**Bài học cơ chế (quan trọng hơn con số, và nó KHÔNG bác §12.4):** hiệu ứng DY-floor ở §12.4 là **thật
ở CẤP TÊN** — đo đúng, khử confound đúng, hit-rate theo ngày đứng vững. Cái sai là **giả định ngầm rằng
một sàn ở cấp TÊN sẽ cộng dồn thành sàn ở cấp DANH MỤC**. Nó không. Rổ 30 tên, name_cap 0.10, rebal
quý: drawdown của rổ bị **beta thị trường** chi phối, không phải bởi độ sâu của từng tên — **chính xác
cùng một cơ chế §12.3 đã tìm ra cho tập trung ngành** (cắt financial 47%→26% mà DD không nhúc nhích).
Hai job độc lập, hai giả thuyết khác hẳn nhau, **cùng một kết luận**: ở hệ này, **DD không đến từ thứ
nằm trong selector**. Đây là bằng chứng thứ hai cho cùng một sự thật cấu trúc, không phải trùng hợp.

⇒ **Giả thuyết DY-floor của user KHÔNG bị bác ở cấp tên** (§12.4 giữ nguyên). Cái bị bác là **đường
tích hợp nó vào selector** — kể cả ở dạng bảo thủ nhất (tie-break, dải biên, fail-open, không cộng
điểm) mà chính nó đã pre-register. Không còn biến thể "nhẹ tay hơn" nào để thử: A4 đã là bản nhẹ tay
nhất có thể.

## 14.2 Việc 2 — quét cap theo đỉnh: **NO-GO mọi mức**, và "cap theo đỉnh" ≡ "cap phẳng tại X"

**⚠️ ĐÍNH CHÍNH THIẾT KẾ (phải nói trước, vì nó đổi bản chất đề xuất):** dispatch mô tả cap-theo-đỉnh
như một cơ chế MỚI, khác cap phẳng ("thay vì cap phẳng áp mọi ngày… cap CHỈ kích hoạt khi vượt X").
**Hai thứ đó là MỘT.** Một cap tại X **theo định nghĩa** không làm gì vào bất kỳ ngày nào tỷ trọng đã
dưới X — A3 (cap 0.30) cũng chưa từng "áp mọi ngày". Thứ duy nhất tách đề xuất của risk-auditor khỏi
A3 đã NO-GO là **MỨC** (0.30 → 0.45-0.60), **không phải cơ chế**. ⇒ không viết code mới, không có cơ chế
mới phải tin: đây là **quét MỨC** trên đúng nhánh `fincap` đã có (`BASKET_FIN_CAP`).

| arm | cap | FULL | IS | OOS | Sharpe | MaxDD | Calmar | **DD_IS** | chi phí vs A2 |
|---|---|---|---|---|---|---|---|---|---|
| **A2** | — | 27.04 | 23.00 | 30.85 | 1.80 | −17.6 | 1.54 | **−15.3** | — |
| A3 (job 140127) | 0.30 | 26.40 | 22.45 | 30.12 | 1.75 | −17.6 | 1.50 | — | −0.64 |
| **C45** | 0.45 | 26.20 | 22.63 | 29.54 | 1.75 | −17.5 | 1.49 | **−16.0** | **−0.84** |
| **C50** | 0.50 | 26.30 | 22.66 | 29.71 | 1.75 | −17.6 | 1.50 | **−16.1** | −0.74 |
| **C55** | 0.55 | 26.72 | 22.84 | 30.37 | 1.78 | −17.6 | 1.52 | **−16.1** | −0.32 |
| **C60** | 0.60 | 26.81 | 22.90 | 30.48 | 1.79 | −17.6 | 1.53 | **−16.1** | −0.23 |

**Trả lời đúng 3 câu risk-auditor hỏi:**

**(a) Có chặn được đúng episode đỉnh không? CÓ — về cơ học.** (`cap_peak_check.py`, đo trên vector tỷ
trọng THẬT, tái dẫn xuất độc lập qua `v4final_lib`, không tin nội bộ module.) Đỉnh uncapped trên nền
A2 = **0.867 theo NGÀY / 0.774 theo quý (2026Q2)**; mọi mức cap đều giữ đúng trần (max = X, sai số 0).
**Nhưng — và đây là điểm giết đề xuất — KHÔNG mức nào là "chỉ chạm đỉnh":**
> uncapped: mean **0.441**, **median quý 0.466**, p95 0.696.
> Số ngày cap thực sự RÀNG BUỘC: cap 0.45 → **53.6%** số ngày (26/48 quý) · 0.50 → **49.0%** (23/48) ·
> 0.55 → **46.4%** (22/48) · **0.60 → 34.7% số ngày (19/48 quý = 40% mẫu)**.

Phân bố tỷ trọng tài chính **nằm ngay trong dải 45-60%** được đề xuất làm trần ⇒ cap ở đó **không phải
rule đuôi, nó là ràng buộc thường ngày** trên gần một nửa mẫu. Muốn chạm **chỉ** đỉnh 2026Q2 phải đặt
trần ~0.75-0.80 — mức gần như không bao giờ ràng buộc (và do đó gần như vô nghĩa). **Điểm thiết kế mà
risk-auditor mô tả — "chặn được đỉnh mà hầu như không đụng phần còn lại" — KHÔNG TỒN TẠI trong phân bố
này.** (Ghi chú: §12.1 báo đỉnh 2026Q2 = 82.7% trên nền **A0**; trên nền **A2** là 77.4% quý / 86.7%
ngày ⇒ **`eyonly` KHÔNG làm giảm tập trung** — đừng đọc §12 rồi tưởng bước 1+2 đã xử lý xong việc này.)

**(b) Chi phí: 0.23-0.84pp/năm — và KHÔNG ĐƠN ĐIỆU theo mức.** cap **0.45 đắt hơn (−0.84pp) cả cap
0.30 (−0.64pp)**, dù 0.45 là ràng buộc LỎNG HƠN hẳn. Một ràng buộc lỏng hơn mà tốn nhiều hơn thì **không
phải một đánh đổi rủi ro-lợi nhuận** — nó là **nhiễu đường đi**. ⇒ không được đọc bảng này như "đường
cong chi phí" rồi chọn điểm tối ưu: thứ tự giữa các mức **không có ý nghĩa thống kê**, và tối ưu hoá
trên nó chính là fit vào nhiễu (đúng thứ Rule 5 tồn tại để chặn).

**(c) MaxDD: ĐỨNG YÊN ở MỌI mức — và IS còn XẤU ĐI.** −17.5/−17.6 khắp bảng, so với A2 −17.6. Đo thêm
**drawdown tách IS/OOS** (thứ dòng MaxDD gộp che mất): **DD_IS −15.3 → −16.0/−16.1 ở MỌI mức cap**.
> Cap không chỉ **không trả tiền khi cháy** — trong nửa IS của mẫu nó làm **cháy sâu hơn**.
Bảo hiểm mà làm tăng chính tổn thất nó được mua để chặn thì không phải bảo hiểm đắt; nó là một khoản
phí không mua gì. Kết luận §12.3 **giữ nguyên và mạnh hơn**: nó không còn là tính chất của riêng mức
0.30 — nó đúng **trên toàn dải 0.30-0.60**.

## 14.3 Khuyến nghị cho risk-auditor / Spyros — điểm "hiệu quả nhất" KHÔNG tồn tại theo số đo

Luận điểm còn đứng vững của risk-auditor (§12.3 đã ghi nhận, ở đây **không** bác): backtest chỉ nói
"không có cú sốc riêng ngành tài chính trong 12.5 năm mẫu"; nó **không** trả lời được kịch bản đuôi
chưa từng xảy ra, và **độ trễ cam kết CRISIS của DT5G (enC=25 phiên)** vẫn là một khoảng trống thật.
**Điều đó vẫn không tạo ra một điểm cap tốt trong dữ liệu:**
- Nếu user muốn cap **vì quản trị rủi ro đuôi có tuyên bố rõ ràng** → **cap 0.60 là rẻ nhất** (−0.23pp/
  năm, nằm trong nhiễu) mà vẫn bound được đỉnh 86.7% → 60%. Đây là mức tôi đề xuất **NẾU** user quyết
  mua bảo hiểm.
- Nhưng phải mua nó **với con mắt mở**: (i) nó ràng buộc **40% mẫu**, không phải "chỉ đỉnh"; (ii) nó
  **không** cải thiện DD ở bất kỳ đâu trong mẫu và làm DD_IS xấu đi ~0.8pp; (iii) thứ tự chi phí giữa
  các mức là nhiễu ⇒ **đừng tinh chỉnh mức** để "tối ưu", sẽ chỉ fit vào nhiễu.
- **Không được** mua nó vì tin backtest cho thấy nó an toàn hơn. Số đo nói **ngược**, ở cả 5 mức.

## 14.4 Lỗi phụ tìm được (đo mới thấy, không suy diễn) — RÒ Σw, 2/2965 ngày, KHÔNG trọng yếu

`cap_peak_check.py` báo `wsum_err` 0.0096 trên **mọi** mức cap trong khi nhánh uncapped chính xác tới
1e-16 ⇒ điều tra thay vì bỏ qua (`wsum_leak_diag.py`). Kết quả: **2/2965 ngày (2015-11-03/04)**,
đúng những ngày rổ chỉ có **1 tên tài chính**: `_cap_group_jointly` rescale name-cap theo ngân sách
nhóm (`ncap/b_in` = 0.10/0.30 = 0.333) rồi áp cho một nhóm 1 tên buộc phải sum=1 ⇒ infeasible ⇒ Σw =
0.990 thay vì 1 (phần thiếu rơi về tiền mặt ảo). Sai số **~1% NAV trong 2 phiên trên 12.5 năm** ⇒
**không trọng yếu, không đổi bất kỳ kết luận nào** (và không đủ để giải thích tính không đơn điệu ở
§14.2b — đó là nhiễu thật, không phải artifact). Ghi lại vì nhánh `fincap` là code audit-only; **nếu
sau này có ai định wire `fincap` vào production thì phải vá trước** (đúng cách: `gcap_eff` phải floor
theo cả năng lực nhóm IN, không chỉ nhóm OUT).

## 14.5 N-ledger (Rule 5 — multiple-testing discipline)

Họ `v4final` tới hết job này đã so **9 cấu hình selector**: A0 `yieldcombo` · A1 `eyfin` · A2 `eyonly`
· A3 cap0.30 · **A4 DY 20:45** · **C45/C50/C55/C60**. Cải thiện tốt nhất trên toàn họ so với production
A0 = **A2 −0.05pp FULL** (tức không có cải thiện nào). **Không tính DSR/PBO** — không phải vì bỏ qua
Rule 5, mà vì **không có ứng viên nào để wire**: DSR chỉ có nghĩa khi có một cấu hình sắp deploy.
Với N=9 và biên độ tốt nhất ≈ 0.00pp, không có gì sống sót nổi bất kỳ hiệu chỉnh multiple-testing nào.

## 14.6 VERDICT + việc còn treo

**Không wire gì. Production 0 chạm. Không đảo lệnh plan 07-14/07-15.** Không route sang quant-skeptic:
skeptic dùng để **thử bác một kết quả sạch trước khi wire** — ở đây cả hai arm **tự bác**, không có gì
để bảo vệ. (Nếu Mike/user vẫn muốn skeptic soi, thứ đáng soi nhất là §14.1: "hiệu ứng cấp tên không cộng
dồn thành hiệu ứng cấp danh mục" — đó là một khẳng định cơ chế, và nó bác một giả thuyết của user.)

- **Việc 1 (A4)**: **NO-GO** — return đúng bằng 0, DD xấu thêm 1.0pp. Đường tích hợp DY vào selector đã
  hết biến thể bảo thủ để thử. §12.4 (DY-floor cấp tên) **giữ nguyên hiệu lực**.
- **Việc 2 (cap đỉnh)**: **NO-GO mọi mức 0.45-0.60**, cùng lý do A3 và mạnh hơn (DD_IS xấu đi khắp dải).
  Nếu user muốn bảo hiểm đuôi theo tuyên bố quản trị → cap 0.60 rẻ nhất (−0.23pp), mua bằng **khẩu vị
  rủi ro**, không bằng bằng chứng.
- **Việc 3 (roadmap)**: XONG — §13.
- **Treo (giữ nguyên từ §12.7, job này không đụng):** (a) đưa số tỷ trọng ĐÚNG cho risk-auditor/Spyros
  — **§14.2 chính là bản trả lời đó, cần chuyển tới họ**; (b) re-pin R3 (vintage hôm nay 27.09 vs pin
  27.84, treo từ §10.9); (c) sửa/chú thích §11.7 theo đính chính §12.1.

**Artifacts §14** (`v4final_exp/`): `run_arms_a4.sh` (viec1|viec2), `a4_dy_selfcheck.py`,
`cap_peak_check.py`, `wsum_leak_diag.py` · `logs/v4f_{A2_eyonly_rerun,A4_dy2045,C45,C50,C55,C60}*.log`,
`logs/a4_selfcheck.log`, `logs/cap_peak_check.log`, `logs/wsum_leak_diag.log` ·
`cap_peak_summary.csv`, `cap_peak_by_quarter.csv`. Code: `custom_basket.py` (`BASKET_DY_TIEBREAK`,
nhánh mới, OFF-path byte-identical — nhánh cũ không đụng).
