# Mike fleet — context pack (v1215)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-07-20T12:17:55] Taylor/finding — Low-beta/BAB (#4) + idio-vol (#15): NO-GO ca hai — beta thap o VN chi la proxy ILLIQUIDITY (Scholes-Williams), sai dau trong pool thanh khoan; idio-vol = Dev bin doi ten + nen phuong sai 2 duoi chu khong phai alpha: {"job": "Taylor_20260720_121019", "loai": "BACKTEST THAM DO — khong wire gi", "N_trials_khai_bao_truoc": 2, "trials": ["F3 low-beta/BAB (candidate #4, chinh)",  …
- [2026-07-20T12:20:17] Mike/finding — dollarbill-fabricated-stoploss-rule: {"issue": "plan_SpaceX_2026-07-21.json SELL VIX order note claims: Ke hoach 07-20 da uy quyen stop nay khong can duyet them (rule V2.4) — SAI. Khong co stop_los …
- [2026-07-20T12:19:49] Wags/finding — wags-fix: missed-wakeup-after-bg-dispatch — PATTERN 18/147 (12,2%), yếu tố kích hoạt = bundle văn xuôi (~25x): {"incident": "missed-wakeup-after-bg-dispatch", "severity": "coordination-reliability", "confirmed": true, "evidence": {"dispatch_bg": ["Winston_20260720_114006 …
- [2026-07-20T12:26:58] Taylor/finding — cutloss -20% CO THAT nhung CHI cho BAL stock leg — LAG khong co, custom30V parking khong co (xac minh file:dong): {"job": "Taylor_20260720_122525", "ket_luan": "USER NHO DUNG — ton tai cutloss -20% cung, nhung pham vi CHI LA BAL book stock positions. Khong ap dung cho LAG,  …
- [2026-07-20T12:36:15] DollarBill/answer — new-plan-discipline-rules-acknowledged: {"summary": "Đã đọc và ghi nhớ 4 quy tắc mới cho việc viết plan", "rules": ["1. Không tự bịa rule chưa verify trong code — phải kiểm tra trading_rules.json + co …
- [2026-07-20T12:35:25] Mike/decision — vix-hold-per-production-rule: {"instruction_from_user": "Tuan thu production rule, khong phai y kien ca nhan. Voi lap plan, co the dua ra lua chon (neu on) de user chon, nhung tren co so tua …
- [2026-07-20T12:39:20] Mike/decision — plan-SpaceX-2026-07-21-approved: {"date": "2026-07-21", "account": "SpaceX", "approved_by": "user", "basis": "production V2.4 — VIX SELL removed (fabricated stop-loss, no such rule exists for c …
- [2026-07-20T13:02:21] Mike/decision — plan-ZaloPay-2026-07-21-approved: {"date": "2026-07-21", "account": "ZaloPay", "approved_by": "user", "basis": "production V2.4 — deadline concern (17:00 ICT withdrawal) resolved: user confirmed …
<!--RECENT-END-->

# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-07-20

## CAPIT (bear-washout) — nguồn vốn CHỐT, đang theo dõi khả năng fire (2026-07-20)
Breadth_oversold đang tăng dần (0,166 07-13 → 0,2176 07-17), tiến gần ngưỡng washout_gate=0,3 —
Taylor audit readiness (`Taylor_20260720_074025`) tìm thấy mâu thuẫn công thức vốn (MD "size × free
cash" vs code paper "NAV_LAG × capit_size", chênh ~100x) vì free-cash luôn ≈0 ở NEUTRAL parking.
**User CHỐT (2026-07-20): công thức `NAV_book_LAG × capit_size` ĐÚNG ý đồ.** Nguồn vốn: user tự RÚT
Trứng vàng trong ngày khi CAPIT kích hoạt, để có tiền sẵn sàng sáng hôm sau. Đã wire note này vào
`bin/bq_freshness_check.sh` (chỉ chèn khi `capit_fired=true`, tránh nhiễu ngày thường) — DollarBill
sẽ tự thấy hướng dẫn khi lập plan T+1 lúc CAPIT fire, không cần Mike can thiệp tay mỗi lần.
2 điểm cần biết nếu fire: (a) sát biên "grind" (91 vs cửa sổ 20-90 phiên — lệch 1 phiên khiến size
full 0,75 thay vì 0,375 nếu tính grind); (b) dd52w hiện tại (~-7%) sẽ là mức nông nhất từng fire
trong lịch sử 2014-2026 (kỷ lục cũ -7,4%) — ngoài rìa mẫu dữ liệu đã biết. Kiểm tra lại
`data/golive_v23_status.json` (`capit_fired`) sau cron 19:00 mỗi tối để biết đã fire chưa.

**PNJ EXCLUDED khỏi rổ CAPIT — due-diligence gate đã wire + verify (2026-07-20, job
`Taylor_20260720_081359`).** PNJ đang khủng hoảng thật (P-Lab bị bắt vì buôn lậu kim cương, scandal
02/07, giá sập ~-32%, team đã kết luận AMBIGUOUS trong `agents/Taylor/research/
calculated_fear_state_backstop.md` §7, cổng xác nhận thật là BCTC Q3/2026 ~cuối tháng 10 — KHÔNG
phải case sạch như PNJ-2015). quant-skeptic CONFIRMED (cao): PNJ pbz=-2,699, xếp HẠNG 1 trong pool
CAPIT ngày 07-17 — nếu không có gate, CAPIT sẽ mua PNJ full size đúng lúc khủng hoảng. Cơ chế:
`anomaly_scan.py` (build từ ground-truth DGC+PNJ) ghi `data/anomaly_flags.json` (cờ 30 ngày, TTL
verify không rò rỉ), CAPIT basket-selection lọc bỏ mọi ticker có cờ active TRƯỚC bước chọn pbz —
gate CHUNG, không hardcode tên, tự áp dụng cho case tương lai. Đã wire vào `ops_health_check.sh`
08:20+12:45 (tier-H alert Trading Daily, tier-W ghi cờ im lặng). Rổ hiện tại (nếu fire hôm nay):
NCT, PVT, SAB, VNM (PNJ đã loại). **Giới hạn thật cần nhớ**: gate KHÔNG backtest được (n=1, không
có lịch sử point-in-time), coi là bảo hiểm chi phí chưa đo được, đừng trích dẫn như alpha đã kiểm
chứng; sau khi loại PNJ (mã thanh khoản nhất), rổ neo vào NCT (ADV 2,18 tỷ/ngày, sát sàn 2 tỷ) —
vấn đề sizing NCT có sẵn từ trước, gate làm nặng thêm chút, cần theo dõi nếu fire thật.
> ⚠️ File này inject vào MỌI phiên/dispatch — giữ NHỎ. Chỉ để mục LIVE/đang-mở. Dự án ĐÓNG (NO-GO/
> KHÉP KÍN/XONG) → chuyển thành 1 file `kb/projects/<slug>.md` + thêm 1 dòng vào `kb/projects/INDEX.md`
> (INDEX được inject, chi tiết chỉ `cat` khi cần). Đừng để nhật ký dự án đã đóng tích lại ở đây.
> ⚠️ Sự cố ĐÃ GIẢI QUYẾT (fix xong + verify) → rút về **1-2 câu + pointer `kb/INCIDENTS.md`**
> ngay khi đóng, KHÔNG giữ nguyên play-by-play ở đây "cho chắc" (bài học sự cố model-drift/
> context-bloat 2026-07-17 — file này phình 0→36KB trong 3 tuần chủ yếu vì narrative sự cố đã
> đóng không được rút gọn, đè phí token lên MỌI dispatch qua `context_pack.md`).

## Vận hành/kiến trúc daemon — trạng thái ổn định (không đổi gần đây)
Remote-control daemon `mike@Mike.service` tắt hẳn từ 07-07 (user chỉ dùng Discord qua
`ccdb-mike.service`, 2 service độc lập; bật lại: `systemctl --user enable --now mike@Mike.service`).
Model mặc định Mike = Sonnet 5, đồng bộ ở 3 tầng config (`.claude/settings.json` +
`ccdb-mike/.env` + `sessions.db` bảng `settings` — DB là nguồn ưu tiên cao nhất; sự cố malformed
model-string qua `/model` command đã fix ở tầng validation, xem [[reference-ccdb-model-config-layers]]
+ [[project-discord-only-workflow-remote-control-disabled]] trong memory Mike).

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate user 2026-07-07)
User chỉ đạo: lỗi vận hành phát sinh thì TỰ FIX rồi báo cáo, không chờ user báo/nhắc việc.
Tài liệu chuẩn tắc: **`kb/ops_runbook.md`** (timeline ngày, mỗi bước check gì, ranh giới tự
sửa). Cơ chế: `bin/ops_autofix.sh` — checker phát hiện lỗi → dispatch Winston (opus, hạ từ
fable 2026-07-17 — xem `kb/INCIDENTS.md` "Model-tier drift") chẩn đoán + sửa + verify + báo
Trading Daily; đã wire vào `ops_health_check.sh` (08:20/12:45) và
`sync_bq_cache_daily.sh` (23:45). Cooldown 1h/vấn đề chống bão dispatch. **Ranh giới cứng
(không bao giờ tự sửa, escalate question + Telegram):** trade plan, trading_rules.json,
logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Mike trong phiên sống thấy
lỗi ops → tự sửa trực tiếp cùng ranh giới đó, không cần chờ checker.

## Onboarding account mới cho team Mike (thêm 2026-07-06, user yêu cầu chuẩn hoá quy trình)
Khi user nói "giao quyền quản lý tài khoản X cho team Mike" → làm theo
`kb/account_onboarding_runbook.md` theo đúng thứ tự, không tự bịa quy trình. Tóm tắt: cron
dùng-chung (preflight/ops-health-check/send-plan-report/eod-report/dispatch-DollarBill) đã
tổng quát hoá qua `trading_bot.config.live_dnse_labels()` + `bin/for_each_live_account.sh` —
account mới `enabled:true/mode:live/broker:dnse` trong `trading_bot_accounts.json` tự động
được các bước này nhận, KHÔNG cần sửa cron. Riêng 4 dòng cron THỰC THI THẬT (`run_bot.sh`,
`bot_heartbeat.sh`, lunch-pkill) KHÔNG tự động — luôn hỏi user xác nhận trước khi thêm (điểm
không thể đảo ngược: bot tự đặt lệnh thật lần đầu, không người duyệt giữa chừng).

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking target
  **70%** của phần idle cash khi BAL/LAG rỗng (`trading_rules.json` v2.1 `neutral_parking`,
  đổi ≠0.70 cần `risk_dial_override` xác nhận, không thì Mafee tự block plan) — chọn 70% thay
  vì 93.8% go-live gốc vì backtest risk-adjusted thắng rõ (Sharpe 1.78 vs 1.66, job
  `Taylor_20260703_130720`, quant-skeptic CONFIRMED). run_bot.sh 09:05 ICT mỗi T2-T6. NAV/vị
  thế hiện tại: đọc `nav_history_SpaceX.csv` hoặc EOD report mới nhất (Trading report topic),
  đừng dùng số hardcode cũ ở đây. Chuỗi sự cố go-live tuần đầu (trim 07-06, bug tên file plan
  `_v2`, T+2 sellable-chiều, giá EOD sai nguồn) đều đã fix+verify — chi tiết: `kb/INCIDENTS.md`
  (tìm "2026-07-06").
- **ZaloPay** (DNSE 0001743768, tên cũ `dnse_main`): V2.4 LIVE từ 2026-07-06, **CASH-ONLY**
  (không margin) — cơ hội so sánh V2.4 có/không margin. **DGC (vị thế legacy) EXCLUDED khỏi
  rebalancing** qua `excluded_tickers` (`secrets/trading_bot_accounts.json`, enforce cứng ở
  `bot_execute.py`) — lý do: HOSE hạn chế giao dịch (lãnh đạo bị khởi tố 17/03/2026, ước gỡ
  hạn chế ~11-12/2026); Taylor giữ vì lý do đầu tư riêng, không phải kẹt thanh khoản. Sizing
  V2.4 dùng `active_nav` (`bin/compute_active_nav.py --account ZaloPay`), không dùng NAV tổng.
  Cơ chế `excluded_tickers` viết tổng quát cho account tương lai có vị thế legacy tương tự —
  `kb/coding_guidelines.md` §7. Transition 5 ngày (07-07→07-13, bán dần vị thế cũ sang
  custom30V) đã XONG — `kb/projects/zalopay-transition-0713.md`. Known gap: `daily_nav_snapshot.py`
  chưa tính đúng P&L cho vị thế legacy (NAV/active_nav đã đúng, chỉ breakdown P&L báo cáo còn thiếu).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking vs VNINDEX đến 2026-09-30. DollarBill phụ trách.

### Trứng vàng DNSE (idle-cash off-book) — cả 2 account (thêm 2026-07-17)
User chuyển tiền rảnh sang sản phẩm tiền gửi "Trứng vàng" DNSE — **hoàn toàn ngoài phạm vi
OpenAPI** (cạn 19 endpoint pattern + SDK chính thức, xác nhận Mafee_20260716_170856). Số dư
hiện biết (user tự báo, **CẦN CẬP NHẬT LẠI mỗi lần nạp/rút**): SpaceX 302.108.211đ, ZaloPay
147.473.247đ (asof 2026-07-16) — lưu ở `manual_offbook_assets_vnd/_asof/_note` trong
`secrets/trading_bot_accounts.json` (default field mới ở `trading_bot/config.py`
ACCOUNT_DEFAULTS). Đã wire vào `daily_nav_snapshot.py` (NAV += offbook, KHÔNG cộng vào cash)
và `compute_active_nav.py` (active_nav += offbook, cơ sở sizing cho DollarBill) — quant-skeptic
CONFIRMED 2026-07-17. `bq_freshness_check.sh`'s DollarBill dispatch tự thêm note khi
`manual_offbook_assets_vnd≠0`.
⚠️ **QUY TẮC BẮT BUỘC — không tự động**: khi user báo đã RÚT tiền từ Trứng vàng ra (vd để
DollarBill lên plan mua), Mike PHẢI cập nhật/giảm `manual_offbook_assets_vnd` NGAY trong cùng
lượt — nếu quên, NAV/active_nav sẽ bị đếm trùng (cash tăng lại + offbook vẫn giữ số cũ). Không
rủi ro tiền thật (executor chỉ check cash/ppse live khi đặt lệnh — quant-skeptic xác nhận
fail-safe), nhưng sẽ làm sai NAV báo cáo + sizing plan. Staleness WARN tự in khi asof >21 ngày
chưa cập nhật (cả 2 script trên) — không tự block, chỉ nhắc.
⚠️ Chưa xác minh: SpaceX có dấu hiệu ppse/pp0Buy báo sức mua cao dù availableCash≈0 sau khi
chuyển Trứng vàng (Mafee_20260716_164743) — CHƯA rõ DNSE có tự tính gộp không, đừng giả định.

## Đang R&D
- **Taylor · EXTREME-regime gate PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `extreme_regime_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`); global default + SpaceX/live GIỮ `False`. Week-1 stress-injection PASS 24/24 (`stress_extreme_regime.py`: arm 2-poll · sell-to-floor · buy-pause · cadence ×0.25 + negative controls). **Target kết thúc ~2026-07-28 (~20 phiên).** 3 điều kiện còn lại trước LIVE: (a) ZERO false-trigger qua ~4 tuần benign, (b) không can thiệp NORMAL-path, (c) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor · vol-scale buy chase-cap (patch#3) PAPER-TRADING** (bắt đầu 2026-07-01, user duyệt trực tiếp): `chase_cap_vol_scale_enabled=True` CHỈ trên account paper `main` (override trong `trading_bot_accounts.json`, k=2.0/ceil=0.04); global default + SpaceX/live GIỮ `False`. Executor-path stress PASS 15/15 (`stress_vol_scale_chase_cap.py`: wiring · WIDEN clamp-to-ceil · MONOTONE · fail-safe rvol absent/0/<0 · paper limit > static + NEG-control live→static). **Target kết thúc ~2026-07-14 (~10 phiên — ngắn hơn EXTREME vì fire trên gap-up thường, tích event nhanh).** Điều kiện trước LIVE: (a) paper sạch (wiring đúng trên quote thật + fail-safe khi thiếu rvol cache), (b) không can thiệp NORMAL-path ngày non-gap, (c) skeptic rerun REAL-fill vs `min(open,L)` proxy trên correlated gap-up @NAV target, (d) user sign-off. **KHÔNG bật gì ở live.**
- **Taylor**: sector sweep #10+ (chờ Mike dispatch)
- **Taylor · fill-timing khung giờ (BUY 10:45-11:15 / SELL 09:15-09:45)**: ĐÃ xử lý xong 2026-07-02 (job Taylor_20260702_031608, note cũ ở dòng này lỗi thời). Edge THẬT & IS/OOS-stable (BUY tại 11:15 rẻ hơn open +17.6bps/lệnh, t=12.0; SELL tại open đúng, +11.8bps vs ATC) nhưng **KHÔNG flip `fill_timing_live_gate` ngay** — cần paper tích lũy ~3-4 tuần fill (từ go-live 2026-07-01, mới ~3-4 phiên) để `execution_quality_review.py` xác nhận NET-of-noise capture (noise 110-220bps >> edge 17bps) → quant-skeptic → user sign-off mới flip. Checkpoint tự nhiên: ~cuối tháng 7.
- **V2.5**: R&D-complete, DISABLED. Reminder: 2026-07-07 Mike hỏi user go-ahead integration.
- **Taylor · DC-book (ConvergePort) NEUTRAL idle-cash waterfall PAPER-TRADING** (bắt đầu 2026-07-06,
  user duyệt trực tiếp, job `Taylor_20260706_125540` + `Taylor_20260706_131247`): khi NEUTRAL và
  BAL/LAG rỗng (đúng tình trạng SpaceX từ ~04/2026), thứ tự ưu tiên giải ngân phần tiền rảnh:
  **BAL/LAG (full trước, không đổi) → DC book/ConvergePort (double-confirm sector-lens BUY ∧ 8L
  rating≤2, capacity ~10-15B ex-DHG) → custom30V (phần còn lại)**. Khi BAL/LAG có deal trở lại → rút
  ưu tiên ngược lại, bán custom30V trước rồi mới đến DC book (reverse-unwind). Backtest xác nhận: DC
  làm top-priority (thay BAL/LAG) = REFUTE mạnh (12.05% CAGR/DD-38.4% vs R3 28.05%/DD-18.8%); DC làm
  lớp giữa (đúng thứ tự trên) = +5.0pp trên sleeve parking, ước tính +3.5pp/năm cho SpaceX-now. **Caveat
  quan trọng: DSR phần excess này chỉ 0.775 (<0.95 ngưỡng an toàn) — bảo hiểm hợp lý, CHƯA phải alpha
  tin cậy cao** → lý do bắt buộc phải paper trước, không wire live ngay. Chạy CHỈ trên account paper
  `main` (override trong `trading_bot_accounts.json`), global default + SpaceX/live GIỮ nguyên (không
  đổi gì). **Đã thêm vào EOD daily report** (theo yêu cầu user 2026-07-06) — xem section paper sleeve
  trong `eod_trading_report.sh` output.
  **Review = EVENT-ANCHORED, KHÔNG PHẢI ngày cố định** (user quyết định 2026-07-06, sau khi Taylor tự
  đính chính lý do "3 tháng" không phải vì DSR mà vì chu-kỳ cơ chế): mốc review = khi chu kỳ
  reverse-unwind ĐẦU TIÊN (LAG dự kiến refill cuối 07, job `Taylor_20260704_033932`) hoàn tất + settle
  4-6 tuần sau đó. Sàn ~2 tháng (đủ thấy trọn unwind+settle), trần ~2026-10-06 (tránh mùa BCTC Q3).
  Nếu LAG refill trượt lịch → mốc review trượt theo, KHÔNG giữ cứng 10-06. **Mike + Taylor cùng theo
  sát diễn biến portfolio để đề xuất ngày review cụ thể khi đủ điều kiện** — không tự động, không
  phải 1 con số đã chốt sẵn.

  **⚠️ AGENDA SỬA tại mốc review (thêm 2026-07-13, job `Taylor_20260713_100550`, user xác nhận CHƯA
  sửa ngay — để tự nhiên chạy sai thêm một thời gian nhằm quan sát whipsaw thật qua đúng đợt LAG
  refill, rồi sửa gộp 1 lần tại mốc review).** Phát hiện quan trọng: **paper sleeve ĐANG CHẠY SAI so
  với chính spec đã backtest/pin** — dùng trigger NHỊ PHÂN (BAL/LAG có deal → tắt hẳn DC book) thay vì
  spec đúng là DC book chạy LIÊN TỤC trên phần tiền dư (residual). Hậu quả đo được: 57.8% ngày
  NEUTRAL-có-✓✓ vẫn có deal BAL/LAG mới trong khi tiền park còn ~38% NAV → bản nhị phân đang chạy hiện
  tại **TỆ HƠN CẢ baseline không có DC book** (CAGR 27.26% / DD −17.8% / Calmar 1.53 / turnover 20.7×,
  so với spec đúng 27.56% / −15.5% / 1.77 / 3.18× và baseline R3 27.35% / −17.6% / 1.55). 4 việc cần
  làm tại mốc review, theo đúng thứ tự ưu tiên:
  1. **Đổi trigger sang continuous-residual** (quan trọng nhất — đây là bug thực chất, không phải tối ưu thêm).
  2. Đồng bộ lịch rebalance DC book vào q2m5 (giống custom30V) — tự giảm whipsaw ~4 lần, đã backtest (job `Taylor_20260706_173317`).
  3. Cap gộp 0.15/tên (chống trùng mã DC↔custom30V vượt trần name_cap 10% NAV khi sleeve lớn — job `Taylor_20260707_042827`).
  4. Liquidity floor 3B thay hard-exclude DHG đơn thuần (job `Taylor_20260707_042827`).
  Đã kiểm tra kỹ 4 góc còn lại (sizing/depth-weight, ✓✓ làm tiebreaker BAL/LAG, mở rộng CRISIS/BEAR,
  sector-lens đứng riêng) — **không còn không gian cải thiện thật**, không cần backtest thêm cho các
  góc đó khi tới review, chỉ cần làm đúng 4 việc trên.

## Workflow ngày trading (SpaceX, T2-T6, giờ ICT)
1. **17:30** — `bq_freshness_check.sh`: BQ fresh → dispatch DollarBill lập plan T+1
2. **19:30** — `send_plan_report.sh`: gửi plan T+1 vào Trading Daily thread (duyệt trước 08:45 sáng mai)
3. **08:20** — `ops_health_check.sh --label "Trước phiên sáng"` (thêm 2026-07-06, theo yêu cầu user) —
   kiểm tra vận hành tự động TRƯỚC preflight: xung đột file plan (bài học sự cố 07-06), lỗi lặp lại
   bất thường trong journal (loại trừ WAIT_T2_SETTLEMENT/mẫu T+2 đã biết), circuit breaker, câu hỏi
   (question) chưa trả lời trong 48h — post tóm tắt vào **Trading Daily** (vận hành sống, không phải
   Trading report). Script: `bin/ops_health_check.sh`.
4. **08:45** — `preflight_check.sh`: kiểm tra sẵn sàng trước giờ mở cửa (GREEN/RED)
5. **09:05** — `run_bot.sh --auto-otp`: thực thi plan (phiên sáng)
6. **09:00-14:55** — `bot_heartbeat.sh` mỗi 5': giám sát liveness + digest fill mới
7. **11:30** — dừng bot giờ nghỉ trưa (`pkill -f "[b]ot_execute.py --account SpaceX"`, sửa 2026-07-06
   tối — pattern cũ tự khớp luôn dòng lệnh gọi chính nó qua `sh -c`, xem `kb/INCIDENTS.md`; vô hại
   vì `session_phase()` đã tự idle đúng qua trưa dù pkill không hiệu quả, nhưng vẫn cần fix cho đúng)
8. **12:45** — `ops_health_check.sh --label "Trước phiên chiều"` (thêm 2026-07-06) — kiểm tra lại toàn
   bộ khâu vận hành sau phiên sáng, trước khi resume phiên chiều — cùng nội dung kiểm tra như bước 3,
   chạy lại để bắt vấn đề phát sinh trong phiên sáng trước khi vào phiên chiều.
9. **13:00** — `run_bot.sh --auto-otp`: resume phiên chiều
10. **~14:50** — phiên đóng (ATC), bot tự cancel lệnh treo, ghi `exec_*_report.md`
11. **15:00** — `eod_trading_report.sh`: **báo cáo tổng kết EOD** (thêm 2026-07-01) — đọc `state.json`
   (giá khớp thực từng lệnh), tính tổng lệnh/mua-bán/khớp đủ-một phần-chưa khớp/tổng giá trị VND,
   post vào **Trading report topic** (đổi từ Trading Daily 2026-07-03, xem dưới). **Thêm 2026-07-03**:
   gọi `bin/daily_nav_snapshot.py` để in kèm NAV thật cuối ngày + biến động so hôm trước (MTM cổ phiếu
   từ BQ, cash/nợ margin từ balances API thật) — ghi vào `data/execution_logs/nav_history_SpaceX.csv`,
   nguồn duy nhất mọi báo cáo ngày/tuần/tháng dùng chung. Xem `kb/coding_guidelines.md` §6 "Standing
   pipeline" cho quy trình xác minh bắt buộc + phân biệt độ sâu nội dung theo từng loại báo cáo.

**3 Discord topic tách biệt (cập nhật 2026-07-03 — thêm Trading report):**
- **Trading Daily (1521470705563340910)** — nội dung VẬN HÀNH SỐNG trong ngày: preflight, run_bot,
  heartbeat, BQ freshness, `ops_health_check.sh` (08:20 + 12:45, thêm 2026-07-06). (EOD report đã
  CHUYỂN sang Trading report — xem dưới.)
- **DollarBill plan channel (1521183164364754974)** — riêng cho việc LẬP KẾ HOẠCH của DollarBill
  (`send_plan_report.sh`, và mọi `dispatch.sh DollarBill ...` khác dù cron hay ad-hoc). Root cause
  thread-leak (dispatch notify theo thread Mike đang active) đã fix ở tầng `dispatch.sh` qua hàm
  `_agent_thread_override` — route CỐ ĐỊNH cho DollarBill bất kể Mike gọi từ topic nào.
- **Per-job thread routing tổng quát (thêm 2026-07-06)** — `_agent_thread_override` chỉ đúng cho
  agent LUÔN thuộc 1 topic cố định (DollarBill). Nhưng Taylor phục vụ NHIỀU topic song song (vd
  user tách riêng "nghiên cứu 8L" và "nghiên cứu vĩ mô", cả 2 đều dispatch Taylor) — báo cáo hoàn
  thành từng job phải về ĐÚNG topic đã yêu cầu job đó, không phải topic Mike đang hoạt động lúc
  job xong. Fix: `dispatch.sh` giờ ghi `discord_thread_id` NGAY vào job record lúc dispatch (chụp
  1 lần, không đổi), mọi thông báo (nhận việc/xong/fail/circuit-breaker/usage-limit) đọc lại field
  này qua `_job_thread_id <job_id>` thay vì suy ra "topic hiện tại". Xem `kb/INCIDENTS.md`.
- **Trading report (1522576692638388364, thêm 2026-07-03, user chỉ đạo)** — kênh DUY NHẤT cho
  **báo cáo tổng hợp** trading ngày/tuần/tháng (khác với alert vận hành sống ở Trading Daily). Đã
  chuyển đích `eod_trading_report.sh` (báo cáo EOD + cảnh báo đối soát mismatch) sang topic này.
  Báo cáo tuần/tháng (khi Mike tự soạn thủ công theo yêu cầu user, vd báo cáo tuần go-live SpaceX
  2026-07-03) cũng đích đến topic này. User cũng dùng topic này để giao các yêu cầu vận hành liên
  quan đến báo cáo trading.

**Duyệt plan — LUÔN mirror vào DollarBill plan channel (thêm 2026-07-02, user chỉ đạo):** khi
user duyệt/thảo luận duyệt plan trực tiếp với Mike ở BẤT KỲ topic Discord nào khác (không riêng
plan channel), Mike vẫn xử lý ngay tại chỗ (không ép user đổi topic), NHƯNG phải
`notify_thread.sh` xác nhận vào **1521183164364754974** ngay sau đó — channel này luôn là bản ghi
đầy đủ mọi lần duyệt, dù hội thoại thật diễn ra ở đâu. Lý do: tránh rải rác/loãng topic khác.

**Escalation khi plan T+1 không sẵn sàng (thêm 2026-07-01, sau sự cố DollarBill "timeout" nhưng
plan thực ra đã ghi xong — dispatch.sh job status không đáng tin 100%):** `send_plan_report.sh`
19:30 ICT giờ verify ARTIFACT thật (file `plan_<account>_<T+1 date>.json` đúng ngày kỳ vọng qua
`next_trading_day()`, có field `orders`) — KHÔNG tin job status. Nếu thiếu/sai ngày/hỏng schema →
**ESCALATE thật**: Telegram + Discord (như cũ) VÀ ghi bus event `question` (`plan-t1-not-ready`) để
Mike tự đọc được ở phiên sau, không chỉ trông chờ user thấy Telegram rồi tới hỏi. KHÔNG tự động
retry/re-dispatch (an toàn hơn — con người quyết định bước tiếp theo, đúng nguyên tắc human-in-the-loop
của toàn hệ thống).

## Cron quan trọng khác (ICT)
| Giờ | Lịch | Việc |
|---|---|---|
| 23:45 | T2-T6 | sync_bq_cache_daily.sh |
| 02:00 | Daily | kb_nightly.sh — archive events, trim memory |
| 02:00 | Thứ 6 | kb_nightly.sh → dispatch Mike editorial KB review |
| 00:00 | Daily | backup.sh → GitHub |

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Sự cố đã đóng, chỉ còn 2 mục thật sự CÒN TREO (rút gọn 2026-07-17, chi tiết đầy đủ `kb/INCIDENTS.md`)
Audit cron 07-12 (C1 DT5G-cache-bug + H2 freshness-false-block) — cả 2 **FIXED+VERIFIED**
(commit `4995262`, `6459b6d`, quant-skeptic CONFIRMED). BQ cache monolith 07-13 (27 file đọc
nhầm `ticker_prune.parquet` chết) — **FIXED** (Winston_20260713_143546, archived). 2026-07-14
HOLD — 1 ngày đã qua, không còn ảnh hưởng vận hành (DollarBill tự tính lại plan mỗi ngày).
Cross-account contamination trong `reconcile_equity.py`/`verify_account_snapshot.py` (phát
hiện 2026-07-19 khi Taylor soạn báo cáo tuần 07-13→07-17, job `Taylor_20260719_055139`) —
**FIXED** cả 2 file (mirror đúng fix `daily_nav_snapshot.py` 07-06/07: filter theo account_no
tự tra config, raise nếu không lọc được thay vì âm thầm dùng nhầm account); thiếu 1 dòng NAV
ZaloPay 07-14 (no-plan day, không có journal) — backfill bằng vị thế THẬT từ `dnse_raw`
`kind=positions` + giá đóng cửa BQ 07-14 (963.451.542đ), verify khớp broker positions record.

**Còn treo thật** (2 mục):
1. Dọn crontab paper-trading lạc hậu — diff đã có (`Winston_20260712_151206`), **chưa áp dụng**
   (chờ Mike review). Ưu tiên thấp, không khẩn.
2. **`ticker_financial`/`ticker_prune` corruption 07-14/15** (rows 07-08→07-14 bị xóa/ghi đè
   upstream) — mitigations đã xong (depth-check gate commit `1b66428`, backup time-travel
   `*_ttbackup_fresh_20260714`), nhưng **quyết định khôi phục dữ liệu từ backup vẫn CHỜ USER**
   (đang hỏi BQ admin upstream). Mike KHÔNG tự khôi phục/tạm dừng cron cho tới khi có quyết
   định. Kiểm tra nhanh còn treo hay đã xong: `kb/INCIDENTS.md` (tìm "ticker_prune cũng bị
   corruption") + hỏi lại user nếu > vài ngày chưa thấy cập nhật ở đây.

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-01. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`). **Live từ 2026-07-01.**

### Mục tiêu
Vận hành chiến lược **production V2.4**, **go-live 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- **R3 NEUTRAL-only @50B: CAGR 27.84% / Sharpe 1.84 / DD −18.2% / Calmar 1.53** (pin threads=1,
  re-pin 2026-07-12 sau khi đóng kênh MOM_N/MOM_S trong TIER_BAL — commit `4fbd492`, quant-skeptic
  CONFIRMED; xem `data/results_registry.md` + `plan_close_mom_20260712.md`). Số cũ 28.05%/28.82% đã
  lỗi thời qua 2 lần re-pin (DT5G swap 07-11, rồi MOM closure 07-12).
- Bootstrap 5th-pct: CAGR 18.6%, DD −28.6% (anchor DD ~−29%, KHÔNG phải −18%).
- **NEUTRAL parking custom30V = phần tin cậy nhất: +7.4pp Full.** (30 mã, cap 0.10)
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### Đã thử, BỊ LOẠI — không wire
custom30V permanent-exclude 7 tên (−1.0pp); LAG SUE-tilt 3 tầng (−0.66pp); hold-neutral exit (−47B);
stability floor ROE_Min<0 (−0.45pp); liq-tilt custom30 (REFUTED); deep-discount sleeve (PARKED);
pbcombo dual-vehicle (Calmar 1.48→1.37); gq_score growth gate (−IC); composite v3 as entry-selector (NO).

### MOM_N/MOM_S ĐÃ ĐÓNG (2026-07-12) — không phải "thử bị loại", là thay đổi production chính thức
Sau chuỗi R&D đầy đủ (momdeal Phase 1 CP1 NO-GO 0/13 feature → nhánh DVR-8L-sizing CP-DVR1 NO-GO →
đo tác động Scope A/B → kiểm tra tách MOM_N-vs-MOM_S, tất cả quant-skeptic CONFIRMED), user duyệt
đóng `MOMENTUM_N`+`MOMENTUM_S` khỏi `TIER_BAL` (giữ nguyên `MOMENTUM`/`MEGA` generic — Scope B đóng
cả họ bị số đo bác, generic vẫn đóng góp thật). Lý do: thành công lịch sử của 2 tier này chủ yếu do
dồn mẫu regime 2020-21, không phải pattern lặp lại được; hậu-2021 gần như hoà vốn. Chi tiết đầy đủ:
`plan_close_mom_20260712.md`, `plan_dvr_8l_sizing_20260712.md`, `plan_momentum_deals_20260711.md`.

### DT5G — market regime gate
- Production: `tav2_bq.vnindex_5state_dt5g_live` qua `get_gated_state()`.
- **KHÔNG đọc** `vnindex_5state` — đó là v3.4b BASE (153 transitions ≠ DT5G 49 transitions).
- Gate phòng thủ (insurance), KHÔNG phải return-enhancer.
- State hiện tại 2026-07-01: **NEUTRAL(3)**, DT5G_macro HEALTHY.

### 8L Rating & Composite
- Composite v3 LIVE (`rating_8l.py`): value = ey(1/PE) + cfy(1/PCF) + ps(1/PS). Golden floor: ROE_Min3Y≥0 ∧ CF_OA_3Y>0.
- **1/PE dominant factor** (IC +0.125, 94% hit). Rating = binary gate ≤3, KHÔNG phải return-tilt.
- Value dominates ALL regimes kể cả BULL. Moat governance: chỉ WIDE (đã audit 5F) mới notch.

### Hạ tầng giao dịch
- `bot_execute.py --auto-otp`: execution deterministic (Python, không phải LLM headless).
- `bin/run_bot.sh`: wrapper gọi bot_execute.py, Discord notify, publish bus event.
- **`data/BOT_STOP`** = kill-switch tức thì.
- BQ Local Cache (DuckDB, threads=1): `data/bq_cache/`, ~100ms vs 5-15s BQ. Sync 23:45 ICT.
- Auto-OTP Gmail: `gmail_otp_reader.py` dùng `internalDate` filter (KHÔNG `newer_than`).
- PHS: **BLOCKED** (lỗi -700003, chờ credential) → paper only.
- **Workflow ngày trading đầy đủ** (T2-T6): BQ freshness(17:30) → plan T+1(19:30) → preflight(08:45)
  → execute sáng(09:05) → resume chiều(13:00) → **EOD report(15:00, `eod_trading_report.sh`, thêm
  2026-07-01)**. Toàn bộ post vào 1 Discord thread — Trading Daily (1521470705563340910).

### Kiến trúc fleet
- Companion daemon: **CHỈ Mike**. Mọi agent khác (Taylor, Bill, Mafee, v.v.) headless/native on-demand.
- Winston/Spyros/Wendy = native subagent `Agent(subagent_type=...)`, không còn daemon.
- Dispatch đúng: `bin/dispatch.sh`. Directive = mandate dài hạn only (deprecated cho task).
- Self-dispatch chặn. Agent → Mike phải escalate (event `question`), KHÔNG spawn Mike headless.
- **quant-skeptic**: REFUTED/INCONCLUSIVE = KHÔNG wire. Bắt buộc trước mọi thay đổi production.
- **Execution**: bot_execute.py (Python) cho đặt lệnh thật. LLM headless bị classifier block khi thao tác tiền.

### Quy chuẩn làm việc
1. Backtest: self-check 0 VND + walk-forward IS(2014–19)/OOS(2020+) + threads=1. Edge rớt OOS = loại.
2. No look-ahead: `profit_*` chỉ train, KHÔNG filter live.
3. Pin kết quả: `data/results_registry.md`. Ghi bus ngay (`append_event.sh`).
4. Human-in-the-loop: Taylor (rules) → Bill (plan, user duyệt) → Mafee (plan-bound only).
5. **Multiple-testing discipline (chốt 2026-07-05, R&D Q3 program H2, Bailey-López de Prado):** mọi
   wire production khai báo **N trials** (số config đã so sánh để tới đó) + **DSR** (Deflated Sharpe
   Ratio) trên NAV daily của config sắp deploy. **DSR < 0.95 → RED FLAG**, không wire nếu chưa có
   sign-off rõ ràng (bổ sung cho, không thay thế, gate quant-skeptic + walk-forward IS/OOS hiện có).
   Khi wire được chọn từ 1 họ ≥~8 biến thể (parking/lever/basket sweep): báo thêm **PBO** (Probability
   of Backtest Overfitting, CSCV) — PBO≥0.5 = ưu tiên config robust-trung vị thay vì IS-best. Kèm
   **per-year leave-one-out** khi edge OOS mỏng năm — 1-2 năm carry hết edge = reshuffle-luck, không
   phải signal bền (bài học Wave1/H8a-tiebreaker 2026-07-05: OOS CAGR/Calmar tăng đúng luật nhưng
   toàn bộ đến từ 2021+2023, LOO rớt → route qua skeptic trước khi wire). V2.4/R3 đã qua chuẩn DSR/PBO
   (DSR≈1.0, PBO≈0.20 — xem `data/results_registry.md` mục "DSR / PBO Robustness Annex", script
   `dsr_pbo_annex.py`).

### Cổ phiếu — quy tắc nhanh
- **BANNED vĩnh viễn**: PC1, VVS, KSF, NKG, HSG, HVN, VJC, NVL, GEG, SBA, DMC/IMP/TRA, TOS, VTP.
- Banking (MBB/ACB/HDB): Tier 1. FPT: Tier 1. CTR: Tier 2. Pharma: buy-and-hold only (timing phá alpha).
- DGC: 2 nhánh tách biệt — compounder-screen (exclude) ≠ special-situation case.
- Sector sweeps #1–9 xong: tất cả = lens/tilt, không phải standalone book (banking có OOS edge nhưng 74% trong custom30V).

### Backup / DR
`~/thanhdt/backup.sh` → GitHub `minhtrido2023/thanhdt` (private). Daily 00:00 ICT.

## Dự án đã đóng — chi tiết theo yêu cầu (đọc khi cần: `cat kb/projects/<file>.md`)
- 2026-07-20 **Deposit-rate auto-crosscheck automation** → `kb/projects/deposit-rate-autocheck.md` — DONE — refresh_deposit_rate_vn.sh tự dispatch Winston xác nhận + ghi (không cần người), 10 vòng quant-skeptic REFUTED→fix→re-review (mỗi vòng 1 lỗi thật, khác nhau) rồi CONFIRMED — kể cả 1 bug thật trong `deposit_rate_vn.current_deposit_rate()` (consumer, không phải chỉ writer).
- 2026-07-17 **DCF upgrade (earning-power · GDP terminal-g · refresh-gate)** → `kb/projects/dcf-earning-power-upgrade.md` — TRIỂN KHAI XONG — Việc1 earning-power NO-GO (giữ FCFE); Việc3 `cap_rf` = default hiển thị `dcf_valuation.py` (level fix, không alpha, DCF non-decisional); Việc2 refresh-gate cron LIVE ngày 11. quant-skeptic CONFIRMED.
- 2026-07-13 **World Cup + rổ lãi suất huy động (Pillar A′)** → `kb/projects/wc-deposit-rate-gate.md` — ĐÓNG cả 2 hướng — N quá mỏng / 0-4 GO, không wire production.
- 2026-07-13 **Plan-approval gate (second-chance cron + code-gate)** → `kb/projects/plan-approval-gate.md` — XONG — second-chance re-send 23:00 + code-gate bot_execute.py, hiệu lực 09:05 07-14 (commits 4216295/27e1282/54d488c).
- 2026-07-13 **Plan ZaloPay transition day 5/5 (FINAL)** → `kb/projects/zalopay-transition-0713.md` — XONG — bán VIB + mua BID, ngày cuối chuỗi transition 07-07→07-13.
- 2026-07-13 **DT5G BULL-giả bug → audit freshness toàn hệ thống** → `kb/projects/dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN — EW-leg path fix + CRITICAL custom30V basket fix + F3 re-pin; live không sai.
- 2026-07-13 **Báo cáo tuần 07-06→07-10 + chống tái diễn** → `kb/projects/weekly-report-mechanism.md` — XONG — đã gửi + WARN check báo cáo tuần/tháng quá hạn (commit 7147ac3).
- 2026-07-13 **Audit dữ liệu 8L (mùa BCTC Q2)** → `kb/projects/8l-data-audit.md` — XONG — 8L đầy đủ; 3 fix cache/cadence/doc dispatch (Winston_20260713_103213).
- 2026-07-12 **lag_edge_health.csv staleness** → `kb/projects/lag-edge-health-staleness.md` — KHÔNG phải bug — mtime-tươi/content-cũ đọc nhầm; falsifiable check ~08-25.
- 2026-07-12 **fa_ratings/8L re-tune + rebuild builder** → `kb/projects/fa-ratings-rebuild.md` — Re-tune 8L NO-GO (16/16); rebuild fa_ratings builder HOÀN TẤT, BQ-write-identity fixed.
- 2026-07-12 **V2.5 leverage verification** → `kb/projects/v2.5-leverage-nogo.md` — NO-GO, giữ DISABLED — edge là IS-artifact (OOS âm), DSR<0.95.
- 2026-07-12 **LAG-weight (tăng tỷ trọng PEAD)** → `kb/projects/lag-weight.md` — ĐÓNG — chấp nhận kết luận mô tả, không tăng trần w_LAG.
- 2026-07-12 **Dự án momentum-deals (đóng kênh MOM_N/MOM_S)** → `kb/projects/momentum-deals.md` — KHÉP KÍN — production LIVE, re-pin R3 27.84%/1.84/-18.2/1.53 (commit 4fbd492+9df396d).
- 2026-07-12 **Dự án Q-sleeve (rổ nhỏ chất lượng cao)** → `kb/projects/q-sleeve.md` — NO-GO cả 2 trục, quant-skeptic CONFIRMED.
- 2026-07-12 **Audit sẵn sàng mùa BCTC Q2/2026** → `kb/projects/bctc-q2-readiness-audit.md` — KHÉP KÍN — fix CRITICAL LAG-blind + MEDIUM freshness + 3 mục nhỏ, đều verified.
- 2026-07-03 **Usage-limit auto-resume** → `kb/projects/usage-limit-auto-resume.md` — XONG — dispatch.sh phát hiện usage-limit → pending_resumes → resume_pending.py cron.
- 2026-07-02 **Reliability hardening (4 việc AgentOps)** → `kb/projects/reliability-hardening.md` — XONG — circuit breaker + idempotency guard + trace_id + INCIDENTS.md (commit e1d9b7c).

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/ (index ở trên). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
