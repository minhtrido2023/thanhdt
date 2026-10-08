## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- 🆕 **PIN DẢI 2 SỐ — user chốt 2026-09-28 08:02 ICT** (registry mục **"2026-09-28 (septies)"**):
  R3 (pin đo ở knob park 0,30; live nay = 0) = **23,37% (`pin0%`, NGƯỠNG SÀN — tiền nhàn rỗi 0%/năm) … 25,71% (`pin1M`, NGƯỠNG
  TRẦN — lãi huy động 1 tháng Big-4 cá nhân PIT trả cho MỌI tiền nhàn rỗi)**. **CẢ HAI là số pin
  chính thức, không cái nào SUPERSEDE cái nào; CẤM trích 1 số mà không kèm quy ước.** Chênh
  +2,34pp trong đó **2,05pp (87,8%) là SỐ HỌC TRỰC TIẾP** (tiền nhàn rỗi 46,4% NAV, trước trả 0%
  nay ~3,5%/năm), chỉ 0,285pp là đường giao dịch — DƯỚI sàn nhiễu W2b 0,46pp ⇒ **KHÔNG đọc là
  "hệ tốt lên"**, đây là đổi thước đo áp đều mọi phương tiện. Quy đổi thực tế ~21,9% … ~24,2%.
  ⚠️ **Neo sizing DD vẫn lấy đầu SÀN −25,2%** (KHÔNG lấy −23,6% của đầu trần) — sizing đứng ở cận
  xấu, neo thực tế KHÔNG đổi. Điểm THẬN TRỌNG trong dải = chân `dep1m_21s` FIFO = **25,24%** — **GIỮ 25,24% làm số chính, KHÔNG re-pin** (chân TRẢ KHI ĐÁO HẠN = điểm trung thực của luật user = **25,34%**, FIFO; chênh **+0,10pp = 1/5 sàn nhiễu** ⇒ không đổi pin; vẫn là MỘT TRONG dải — luật CẤM trích 1 số trần trụi giữ nguyên); ⚠️ **KHÔNG gọi là "điểm thực tế"**. Chân maturity, min_age, giới hạn `pin1M`: `kb/projects/r3-pin-history.md`.
- **R3 NEUTRAL-only @50B: CAGR 23.37% / Sharpe 1.88 / DD −14.6% / Calmar 1.60** = **`pin0%` (đầu SÀN của dải)** — pin CHÍNH THỨC từ
  **2026-09-27 (sexies)**, Final NAV 684,52B, ledger md5 `4707bcbe…`, IS 20,00% / OOS 26,50%,
  self-check 0 VND. **Số SẠCH đầu tiên trên CẢ HAI chiều**: nhãn edge-health causal (`known_date`,
  FAIL-C đã đóng) **và** đúng knob park live LÚC ĐO (0,30; **live nay = 0, park TẮT từ 2026-10-01**). Neo sizing DD (bootstrap 5th) = **−25,2%**;
  DSR 1,0000 · PBO(68) 0,2085.
  ✅ **Ba rail park ĐÃ ĐỒNG BỘ** (commit mike `1f15139b` đồng bộ ở 0,30; **live HIỆN = 0,0 từ 2026-10-01**, user chốt — xem current_ops): R1 MUA `ETF_PARK`, R2 BÁN `compute_park_trim.py PARK_TARGET_F1`, R3 policy `trading_rules.json`. ⚠️ "R3" ở đây = rail policy, KHÁC "R3" ở số pin (config backtest R3 NEUTRAL-only). Cổng cơ học `bin/park_rail_consistency_selfcheck.py` đọc giá trị 3 rail bằng AST, rc=1 khi lệch. ✅ R2 ĐỌC R3 từ commit `adb125b7` (27/09): `compute_park_trim.py` lấy `trading_rules.json` `neutral_parking.default_park_of_idle_pct` làm nguồn sự thật duy nhất, fail-closed.
  Lịch sử pin (quinquies, 24,42%, 28,86%, 27,x%), `LAG_ADV_BASIS`, fidelity `liq<=0` → `kb/projects/r3-pin-history.md` — **KHÔNG trích +1,62pp như "edge mới"**; **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng**. ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho CAPIT pool/maturity. LAG fidelity: Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không
  bằng backtest thêm — sổ theo dõi + **mốc cứng 2026-12-15 / 2027-03-31**:
  `kb/projects/lag-adv-filter-tracking.md`, chi tiết cơ chế: `agents/Taylor/research/
  lag_fidelity_decomp_20260803/T5_DECISION.md`.
- Bootstrap 5th-pct + P(DD<−30%) + chuỗi số SUPERSEDED: `kb/projects/r3-pin-history.md`.
- ⚠️ **CÒN MỞ — CẦN USER QUYẾT (mở 2026-10-08)**: số pin R3 (dải 23,37%…25,71%) và neo sizing DD **−25,2%** đều ĐO Ở park 0,30; live là park **0%** từ 2026-10-01, **CHƯA re-pin ở 0** ⇒ chưa có neo DD đo đúng knob live. Chân park=0 cũ (22,37%, trước FAIL-C) KHÔNG có bootstrap DD. Không tự re-pin; chờ user quyết có đo lại không.
- **DSR/PBO đã hết trôi — họ trial nay GHIM bằng `DSR_FAMILY_MANIFEST`** (merge `f2cfb124`):
  **DSR 1,0000** (ann-SR R3 **1,815** trên ledger pin park 0,30; 1,616 ở bản @0,7). **Số pin của V2.4 là PBO = 0,2085** (chạy lại trên ledger pin park 0,30 — **không đổi**, vì CSCV
  đo trên HỌ TRIAL, ledger R3 không thuộc họ) trên họ gốc phục dựng
  68 file (`mike/research/dsr_family_manifest_20260927/man_2026_07_recon.json`, md5 `2cea9626…`) —
  khớp 0,2088 pin từ 2026-07 ⇒ phục dựng đúng. ⚠️ caveat: registry 2026-07 không lưu tên file,
  68 file này dựng lại theo `mtime`, không phải danh sách gốc (chi tiết: `kb/projects/r3-pin-history.md`).
  **PBO 0,5013 trên "họ hôm nay" (486 file) KHÔNG phải PBO của V2.4** — đó là **chỉ báo sức ép
  multiple-testing TÍCH LUỸ** của thư mục `data/` (80→0,2088 · 477→0,3993 · 486→0,5013): nó nói về
  tốc độ thử của đội, không nói về độ bền của config đang deploy. *0,3993 (bis) SUPERSEDED làm số pin.*
- **3 bản sửa đo lường ĐÃ LIVE trên main 2026-09-27** (user duyệt 13:38 ICT):
  **FAIL-F** annualize theo LỊCH 365,25 trong `bootstrap_nav.py` + `dsr_pbo_annex.py` (WC merge
  `3c944443`) — bỏ cơ sở "N/252 phiên" vốn thổi CAGR bootstrap cao giả ~+0,3pp.
  **FAIL-H** `nav_period_returns.py` có số hạng dòng tiền (TWR) + cổng NAV-jump 5% fail-closed
  (mike merge `2b6ab8ac`) — lần NẠP/RÚT đầu tiên không còn bị công bố thành lãi/lỗ giả.
  **egg** `reconcile_equity.py` cộng `egg.totalValue` (mike merge `6a89e51b`) — residual thật
  2026-09-27 còn **SpaceX +0,0281% / ZaloPay +0,0107% NAV** (trước: 9,58% / 11,96%).
- ✅ **FAIL-C ĐÓNG 2026-09-27** (A/B: `kb/projects/r3-pin-history.md`). Anchor R3
  đổi 23,43% → **23,37%**; xem registry mục "2026-09-27 (sexies)". Tồn dư KHÔNG gấp, không ảnh
  hưởng số: đường LIVE `golive_recommend_v23.py:293` và `edge_health_monitor.py:188` (`neg_streak`)
  vẫn index trên `entry` — benign hôm nay (live luôn lấy dòng cuối ⇒ cùng `w_LAG=0,50`), nhưng
  `neg_streak` chạm ngưỡng sớm ~1,2 tháng.
  (Ghi chú cũ FAIL-F branch + PBO 2 cây — xem FAIL-F merge `3c944443` và `DSR_FAMILY_MANIFEST` merge `f2cfb124` ở trên; nguyên văn: `kb/projects/r3-pin-history.md`.)
- **NEUTRAL parking custom30V @0,30 (đo ở 0,30; production nay park 0% từ 2026-10-01) = +1.06pp CAGR** (23.43% vs 22.37% park=0) — và ở
  30% parking làm **TỐT hơn** rủi ro: DD −16,1%→−14,4%, Calmar 1,39→**1,63**, Sharpe 1,95→1,88.
  ⚠️ 0,30 vs 0,0 **không phân biệt được bằng dữ liệu** (paired block bootstrap P=0,479) ⇒ 0,30 là
  sở thích rủi ro user chốt, không phải mức thắng có ý nghĩa thống kê.
  Bản @park 0,7 + "+7.4pp Full" SUPERSEDED: `kb/projects/r3-pin-history.md`. Giữ/bỏ parking là **quyết định của user**, Taylor không tự đảo.
- Trước khi đề xuất ý tưởng R&D hoặc thay đổi chiến lược/tham số, `grep` `kb/projects/INDEX.md` để không lặp lại NO-GO đã đóng (`bin/kb_recall.sh "<từ khoá>"`).
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** = V2.4 + lever MGE=1.5 — **NO-GO 2026-07-12** (edge là IS-artifact, OOS âm, DSR<0.95; quant-skeptic CONFIRMED), giữ **DISABLED** (`trading_rules.json` v25_leverage). Account sẵn sàng nhưng KHÔNG bật. Chi tiết: `kb/projects/v2.5-leverage-nogo.md`.

### ⚠️ `*_screen.py` — "8L top-25" TRƯỚC 2026-09-27 là 25 mã XẤU NHẤT (đã vá, nhưng số cũ HẾT HIỆU LỰC)
Lỗi `ascending=False` trên thang 1-5 (1 = TỐT NHẤT), **16/20 file**, merge `ec9750f2`; chi tiết + mức sai: `kb/projects/screen-sort-direction-bug-20260927.md`. 🔴 **HỆ QUẢ NGHIÊN CỨU — đừng trích số cũ nữa**: **kết luận "sleeve này bổ sung alpha mới, không lặp 8L" KHÔNG còn suy được từ những con số cũ.**

⚠️ **CÒN PHẢI LÀM (§8, chưa làm — cần user duyệt vì chạm artifact đã pin)**: mọi file output
`data/*_verdict.json` / `*_monthly.csv` (chứa `ortho_8l`) **hiện vẫn mang số THEO BUG**. Phải
**sinh lại 16 screen** rồi cập nhật, cho tới lúc đó đọc các file đó là đọc số sai. Đường tiền
LIVE **không** ảnh hưởng: `*_screen.py` là lens nghiên cứu/discretionary, không nuôi V2.4/park.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

**MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12)** — thay đổi production chính thức, không phải "thử bị loại":
`MOMENTUM_N`+`MOMENTUM_S` gỡ khỏi `TIER_BAL` (giữ `MOMENTUM`/`MEGA` generic — vẫn đóng góp thật).
Lý do + chuỗi R&D: `kb/projects/momentum-deals.md`, `plan_close_mom_20260712.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State live hôm nay = `kb/current_ops.md` / `golive_state_today` (fact động, KHÔNG pin ở đây).

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
  ⚠️ **+0.125 ĐÚNG, đừng hạ** — đề xuất +0.096/+0.034 (nhân `Price/Close` "khử look-ahead") ĐÃ BỊ
  BÁC BỎ 2026-08-02: `PE` vốn đã ở cơ sở `Price` thô PIT đúng; nhân vào là ĐƯA look-ahead VÀO
  (R3 xấu −1,70pp). Xem `kb/data_registry/fundamentals/valuation_pe_pb_pcf_ps.md` "Bẫy (4)".
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- **`data/BOT_STOP`** = kill-switch tức thì.
- Giờ chuẩn tắc chuỗi ngày trading (T2-T6) + xử lý khi lỗi: `kb/ops_runbook.md`. Routing Discord:
  `kb/current_ops.md`. BQ cache / auto-OTP / PHS: `kb/KNOWLEDGE.md` §4.

### Kiến trúc fleet
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.
- Daemon / dispatch / escalate (cơ chế đầy đủ): `MIKE.md` + `kb/KNOWLEDGE.md` §3.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể: báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (ca Wave1/H8a-tiebreaker 2026-07-05: `kb/KNOWLEDGE.md` §8). V2.4/R3 đã qua chuẩn
   DSR/PBO — xem mục **DSR/PBO** ở trên (họ trial GHIM bằng `DSR_FAMILY_MANIFEST`, merge `f2cfb124`); bản cập nhật 2026-09-27 (bis): `kb/projects/r3-pin-history.md`.

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP, BAF
  (thêm 2026-08-26 — leverage trap + capital market extraction, xem `kb/KNOWLEDGE.md` §6).
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 (đã đóng, kết luận lens/tilt): `kb/KNOWLEDGE.md` §7.

## Mandate — Margin crisis sleeve Loại-2 adaptive (chốt 2026-08-25, user duyệt)

**Thị trường VN có 90%+ nhà đầu tư cá nhân → overreaction là đặc trưng CẤU TRÚC, không phải noise.**
Framework margin cho khủng hoảng phải ADAPTIVE theo loại crisis, không phải rigid policy chỉ đúng cho thị trường đã trưởng thành.

**Phân loại Bobby (real-time BLIND):**
- **Loại 1** — STRUCTURAL/MULTI_YEAR: tự củng cố, giải quyết lâu (VN 2008-2012) → KHÔNG margin
- **Loại 2** — CONFIDENCE_LIQUIDITY/CONTAINABLE: có policy anchor rõ, phục hồi nhanh hơn (2020, 2022-23) → CÓ THỂ margin với 3 điều kiện

**3 điều kiện bắt buộc (ANĐ — thiếu 1 = KHÔNG escalate):**
1. Bobby Loại-2 **real-time BLIND** (chạy TRƯỚC khi biết forward return — tránh hindsight)
2. PIT filter PASS (universe_pit — không dùng ticker_prune cho quyết định này)
3. ≥1 chỉ báo overreaction xác nhận (VIX spike / intermarket dislocate / breadth collapse cực đoan)
→ Kết quả: ESCALATE lên Mike + user — KHÔNG auto-trade, KHÔNG bypass human-in-the-loop

**Statistical significance sai tool cho N=3-5 crisis** — dùng causal framework + human judgment.
Observable indicators + escalation process là deliverable đúng, không phải auto-trade rule.

**Trần (xác nhận 2026-08-25, Spyros CONDITIONAL-APPROVE):**
- Equity sleeve: ≤5% NAV vốn tự có (cơ sở: 1% NAV max loss / 20% exit kỷ luật = 5%)
- Exposure: ≤6,5% NAV (≠ ≤5% — f=1,3 của RocketX thật, không phải f=2,0 giả định)
- Bobby confidence "ambiguous" (vd 2018): size −50% = ≤2,5% NAV equity

**Chi tiết framework + payload escalate:** `agents/Taylor/research/crisis_margin_framework_adaptive_20260825.md`
**Chính sách đầy đủ (đơn mã + sleeve Loại-2):** `kb/projects/discretionary-margin-policy-20260823.md`

## Quy ước phân tích conditional — trục 2 mặc định (chốt 2026-08-22, user duyệt)

**Breadth-tercile PIT thay Value Radar zone làm trục 2 mặc định cho mọi phân tích conditional.**

⚠️ **RANH GIỚI HIỆU LỰC — đọc trước khi dùng (bổ sung 2026-09-27, job `Taylor_20260927_022338`).**
Trục này được chọn **CHỈ vì CẤU TRÚC MẪU**, không vì nó tách được lợi suất hay IC:
- **KHÔNG có bằng chứng trục này tách tín hiệu.** (0/27 ô BH FDR 08-22; job E 09-27 0/4 — `kb/projects/breadth-tercile-axis-20260822.md`)
- ⇒ Dùng để **MÔ TẢ / phân tầng mẫu**. **Đừng suy ra tín hiệu từ nhãn ô**, đừng coi "trục mặc
  định" là "trục có thông tin". (H5 2026-09-26 đã đọc quá nghĩa đúng theo hướng này rồi báo
  "trục mặc định trượt 4/4" — nó trượt một tiêu chí 08-22 chưa bao giờ tuyên bố đạt.)
- Không trục nào khác qua được cùng chuẩn (0/12). Lý do chọn + **cách tính breadth chuẩn (3 chi tiết từng làm tái lập lệch)**: `kb/projects/breadth-tercile-axis-20260822.md`.
Value Radar vẫn giữ vai trò DISPLAY-ONLY trong báo cáo (§6b coding_guidelines). Không wire vào sizing.

Quyết định gốc 2026-08-22 + tái kiểm 2026-09-27 (verdict **A — quy ước ĐỨNG, không đổi trục**): `kb/projects/breadth-tercile-axis-20260822.md`.

## QUY TẮC — DNSE điều chỉnh giá vị thế TỐI TRƯỚC ngày ex-date (user chốt 2026-09-12, bài học lặp ≥3 lần)
**Sự thật broker:** DNSE cập nhật `marketPrice` của vị thế theo giá đã điều chỉnh corp-action vào
**tối hôm trước ex-date** (T−1 evening), trong khi `close_price` BQ tới lúc đó vẫn là giá CHƯA
điều chỉnh. ⇒ xcheck NAV lệch đúng bằng giá trị quyền là **KỲ VỌNG, không phải stuck, không cần
verify DNSE, không escalate**. Ca chuẩn: DGC 11/09/2026 tối T6 — BQ 46.750 vs broker 38.750, cổ
tức tiền 8.000đ (2 đợt 3.000+5.000) ex-date T2 14/09 ⇒ 46.750−8.000 = 38.750 khớp chính xác.

⚠️ **PHẢI TÁCH HAI LỚP — sửa 2026-09-12 sau arch-review (job Wags_20260912_052122), bản trước gộp
chung và sẽ dạy làm SAI:**
- **Cổ tức TIỀN MẶT** (DGC 09-11): broker chỉ đổi GIÁ. NAV vẫn mark **giá CUM của phiên đó**
  (không phải giá broker đã điều chỉnh) — vì `cum_dividend_double_count` (§21) đã loại khoản
  phải thu ra khỏi tiền; lấy giá broker mà vẫn loại khoản phải thu thì NAV **hụt đúng bằng cổ
  tức** (ca DGC: 80 triệu = −8,1% NAV ZaloPay). Đây là ca DUY NHẤT được tự động cho qua.
- **Cổ tức bằng CỔ PHIẾU / thưởng / tách** (VHM 08-05, MBB 08-11, VIB 09-09): broker đổi **CẢ giá
  LẪN khối lượng** cùng lúc — đo thật trên `dnse_raw_2026-09-09.jsonl` 19:07: VIB openQuantity
  500→547 **và** marketPrice 15.050→13.700 trong cùng bản ghi. Vị thế LIVE (qty MỚI) nhân giá CUM
  ⇒ NAV thổi phồng (VIB +711.100đ; VHM 1:1 sẽ là +100% giá trị vị thế). ⇒ **VẪN CHẶN, cần người
  xử lý** — không có ngoại lệ tự động.
**Cách xử lý khi gặp:** tra ex-date mã đó (`tav2_bq.corporate_action` qua
`corp_action_lib.pricing_events` — KHÔNG dùng `events()` executed_only, nó trả rỗng đúng ngày cần).
⛔ **Cơ chế tự nhận diện CHƯA được wire — tới 2026-09-12 việc này vẫn làm TAY.** Bản nháp
  (`expected_exdate_adjustment`) bị arch-review gỡ, lý do: `kb/projects/corp-action-nav-chain-20260922.md`. **tự động hoá SAI ở đây còn tệ hơn tự tay xử lý mỗi quý vài lần.**
Runbook thao tác tay: `kb/ops_runbook.md` § PRICE_XCHECK.

## QUY TẮC — Case có vấn đề PHÁP LÝ: vẫn phân tích như bình thường, chỉ WARNING tình trạng pháp lý (user chốt 2026-09-27 23:51 ICT)

**Chỉ đạo nguyên văn:** *"Những case pháp lý, nếu có báo cáo tài chính thì cứ dựa báo cáo phân
tích như bình thường, chỉ warning về tình trạng pháp lý nếu có thôi."*

Áp dụng cho MỌI agent làm định giá / due-diligence / báo cáo (Taylor, DollarBill, Wendy,
fundamental-skeptic):
- Có BCTC ⇒ **phân tích bình thường** trên số liệu đó (định giá, dự báo quý, DCF, nhận định).
  KHÔNG tự từ chối phân tích, KHÔNG tự hạ kết luận, KHÔNG tự loại mã chỉ vì có yếu tố pháp lý.
- Tình trạng pháp lý đi vào báo cáo dưới dạng **WARNING tường minh** (nêu sự việc + nguồn +
  ảnh hưởng đã biết), KHÔNG phải một cổng chặn ngầm.
- **Không đổi** 3 cổng đã có, chúng độc lập với luật này: `BANNED` vĩnh viễn (hằng số trong
  code), `excluded_tickers` per-account (vd DGC ở ZaloPay), và `data/forensic_flags.csv`
  `severity=exclude`. Luật này nói về **cách VIẾT phân tích**, không nới cổng nào.
- Rủi ro pháp lý của việc **lưu trữ/công bố** ghi chú pháp lý (vd đưa `forensic_flags.csv` vào
  mirror GitHub): **user tự đánh giá và tự báo khi có thông tin** — không cần Mike chặn chờ
  legal-vn soát trước.

Liên quan: `kb/current_ops.md` (DGC 2 nhánh tách biệt), §21 (UNVERIFIED thì CẤM công bố tỉ suất
— đó là cổng SỐ LIỆU, không phải cổng pháp lý).
