# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-10-08 (trim context_pack #5 — CHỈ DI CHUYỂN nguyên văn sang `kb/projects/*.md`, để pointer 1 dòng; mục lục `kb/projects/context-pack-trim-20261008.md`).
> Chi tiết CAPIT/domain-constraint/due-diligence/cron/daemon: `cat kb/current_ops_ext.md`

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking **0% (TẮT)** — user chốt 2026-10-01 10:26 ICT (`decided_by: user`: "Park 0% chốt. Chỉ thay đổi khi lãi suất huy động có xu hướng hạ"); lịch sử 0,70→0,80 (08-04)→0,30 (09-27)→0,0 (10-01). 3 rail đồng bộ = 0,0 (merge 10-01, arch-review APPROVED, `park_rail_consistency_selfcheck` rc=0). Hiệu lực từ plan nháp đêm 01→02/10; tiền nhàn rỗi nằm ở Trứng vàng. **TRIGGER QUAY LẠI = lãi huy động có XU HƯỚNG HẠ ⇒ chỉ CẢNH BÁO user, KHÔNG tự khôi phục park** — định nghĩa user chốt 2026-10-01 12:40 ICT: Big-4 12M tháng này < tháng trước HOẶC CCTG đợt mới < đợt trước; cảnh báo do cron tuần `refresh_deposit_cctg_weekly.sh` (08:05 ICT thứ Hai) gửi Trading Daily. run_bot.sh 09:05 ICT T2-T6. NAV: `nav_history_SpaceX.csv` hoặc EOD report.
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, CASH-ONLY. **DGC EXCLUDED** (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026). Sizing dùng `active_nav`. Cùng target parking 0% (không có override riêng).
- **PNJ EXCLUDED cả 2 account** (SpaceX+ZaloPay, `excluded_tickers` trong `secrets/trading_bot_accounts.json`) từ 2026-09-30, quyết định USER trên bus question `Taylor/pnj-trong-ro-custom30v-live-can-user-duyet-chan` (mở 2026-09-28) — option A. Lý do: hạ bậc AMBIGUOUS→NON do công bố DN 25-27/09 (0 vị thế thật ở cả 2 account tại thời điểm loại, xác nhận qua `data/execution_logs/dnse_raw_2026-09-30.jsonl`), cần "scrutiny exam" trước khi trở lại candidate rổ custom30V. **REVIEW TRIGGER = khi PNJ công bố BCTC Quý 3/2026** (KHÔNG phải TTL theo ngày) — lúc đó chạy lại due-diligence đầy đủ (kiểu fundamental-skeptic DGC/TV1), KHÔNG tự động khôi phục.
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,9tr / ZaloPay ~102,2tr (đo 09-27), đã cộng NAV tự động — KHÔNG phải `availableCash`. ⚠️ **RÚT VỀ TRONG NGÀY, KHÔNG phải T+1**. ⚠️ **KHÔNG phải tiền gửi ngân hàng**; lãi đo thật **8,543%/năm** và DNSE **tự khấu trừ TNCN trước khi trả** nên số đó đã là net. "Tài khoản Không Ngủ" là SẢN PHẨM KHÁC (trần 30 tỷ), đừng lẫn. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.
  ⚠️ **ĐÍNH CHÍNH BẢN CHẤT 2026-09-27 (legal-vn, bus `dnse-trung-vang-legal-review-20260927`) — KHÔNG phải repo.** khách **SỞ HỮU THẬT** trái phiếu niêm yết, **lưu ký tại VSDC**; **Việt Nam KHÔNG CÓ Quỹ bảo vệ nhà đầu tư**. Ba rủi ro THẬT + thuế + căn cứ: `kb/projects/dnse-trung-vang-legal-review-20260927.md`.
  🔴 **2 CÂU CHƯA TRẢ LỜI ĐƯỢC, phải hỏi DNSE bằng VĂN BẢN**: (1) trái phiếu lưu ký đứng tên KHÁCH
  hay nominee DNSE? (2) MÃ trái phiếu + TCPH cụ thể? — chưa biết (2) thì **không đo được tập trung
  per-name**. Quyền yêu cầu sao kê chi tiết: TT121 Đ17-18. DNSE từ chối nêu mã = **red flag**.
  ✅ **USER CHỐT 2026-10-05 08:3x ICT (`decided_by: user`): Trứng vàng KHÔNG phải sleeve thông thường mà là một dạng của cash, coi tương đương tiền ⇒ KHÔNG có cơ chế "vượt trần"; trần ~2%/TCPH và sleeve ≤10% NAV ở trên KHÔNG áp dụng.** (2 câu hỏi DNSE bằng văn bản về nominee/mã TCPH vẫn là thông tin tham khảo, không chặn.)

- **[2026-10-03 10:34 ICT, user chốt] Định nghĩa XU HƯỚNG HẠ (chính xác hoá)**: ngay khi Big-4 điều chỉnh GIẢM lãi tiết kiệm 12 tháng HOẶC lãi chứng chỉ tiền gửi 6 tháng THẤP HƠN so với tuần thống kê trước ⇒ cảnh báo user (cron tuần `refresh_deposit_cctg_weekly.sh` + `deposit_cctg_trend_check.py`); vẫn CHỈ cảnh báo, không tự khôi phục park. User cũng DUYỆT rating_8l/DCF dùng effective rate (đã LIVE từ 10-01).

## Macro kill-switch A (lãi huy động > 7,5%) — merged 2026-10-01, DISPLAY-ONLY
- Code trên WC main (`deposit_rate_vn.macro_killswitch_a_status()`, `cctg_rate_vn.py`, dòng hiển thị trong `dna_report`/`value_radar`); quant-skeptic vòng 7 CONFIRMED, user duyệt. effective = max(Big-4 12M, CCTG Big-4), ngưỡng `> 7,5%`. **CCTG = kỳ hạn 12 THÁNG, lấy CAO NHẤT trong các NH Big-4 có phát 12M (user chốt 2026-10-05; trước đó 6M — anchor 09-30 7,5% là 6M, REBASE 10-05 = 7,4% BIDV/VietinBank; cặp 7,5→7,4 là artifact đổi kỳ hạn, đã ack trong state trend-check). Big-4 12M: cùng NH có online lẫn quầy ⇒ lấy số CAO NHẤT.** **KHÔNG có code path production nào đọc nó** — sleeve recovery vẫn paper, chưa chặn lệnh nào.
- ✅ **CCTG + Big-4 12M có auto-fetch HÀNG TUẦN** (cron `5 1 * * 1` = 08:05 ICT thứ Hai, LIVE từ 2026-10-01; 2 nguồn khác chủ + chéo ≤0,1pp + guard URL tái dùng; lệch/thiếu ⇒ KHÔNG ghi, nhắc xác nhận tay `manual_verify`; log `logs/refresh_deposit_cctg_weekly.log`). Rủi ro còn lại không code chặn được: tác tử bịa nhất quán cả URL lẫn rate. (Trước đó nhập tay.) Anchor 2026-09-30 = 7,5%; không cập nhật ⇒ stale >45 ngày ⇒ **ARMED vĩnh viễn từ 2026-11-15**. Big-4 stale ≈ 2026-10-20 (cùng cơ chế fail-closed).
- Trước khi wire vào gate thật: siết `deposit_rate_vn.deposit_events_df()` phía Big-4 (đang silent-drop dòng không parse được) + guard ngày tương lai tại load (quant-skeptic NON-BLOCKING #2/#3).
- ✅ **rating_8l NEUTRAL tilt + chuỗi DCF (dcf_valuation, dcf_refresh_gate, custom30_yield_labels, due_diligence) DÙNG effective rate = max(Big-4 12M, CCTG 6M)** — LIVE trên WC main từ 2026-10-01 (merge `d87a6f89`, user duyệt 12:40, quant-skeptic vòng 2 CONFIRMED). **Fail-closed**: CCTG stale >45 ngày hoặc lỗi ⇒ cả 5 consumer rơi về Big-4 6,8% + WARNING (không phải ARMED). **Knob lùi**: env `DEPOSIT_RATE_CCTG_OVERLAY=0` (chỉ nhận đúng chuỗi "0"; lan tới mọi launcher source `wc_env.sh`, NGOẠI LỆ cron `dcf_refresh_gate` không source). `golive_recommend_v23.py:~991` (cổng CAPIT margin PIT, ngưỡng 9,0%) CỐ Ý vẫn Big-4-only — user chốt 2026-10-01 16:42: GIỮ Big-4, chỉ THÊM dòng hiển thị "effective vs 9%". **TRIGGER XEM LẠI đổi sang effective** = CCTG có ≥3 tháng dữ liệu + cron tuần chạy ổn, HOẶC effective ≥ ~8% (lúc đó dispatch Taylor đo khoảng cách CCTG−Big-4 lịch sử rồi quant-skeptic + user duyệt riêng). Tác động đo, dòng hiển thị PIT, follow-up: `kb/projects/deposit-rate-effective-rate-20261001.md`.

## Cutloss SHADOW — mốc OOS: `agents/Taylor/research/intraday_cutloss_replay_v2_20261009/PREREG.md`
- `bin/intraday_price_watch.py` (chạy thử, KHÔNG đặt lệnh thật). Tin nhắn dạng **"SHADOW GIỮ/BÁN/BÁN 50% <MÃ>"** trong Trading Daily là lệnh cho script chạy thử — **Mike KHÔNG coi là lệnh giao dịch thật, KHÔNG dispatch Mafee/DollarBill theo dòng đó.** Chỉ hành động khi user nói rõ ngoài tiền tố SHADOW.

## Corp-action broker-primary SHADOW (`MIKE_CA_BROKER_SOURCE=shadow`) — KHÔNG bật live trước khi đủ tiêu chí user chốt 2026-10-09 (≥3 sự kiện chỉnh giá thật, 0 CONFIRMABLE sai…); **mốc xem lại 2026-12-15**: `kb/projects/corp-action-broker-primary-live-criteria.md`

## Signal holds
- Không có hold nào đang mở. VPI/BAL hold (08-19→09-16) đã gỡ 2026-09-16, user duyệt RESUME,
  không còn escalate riêng. Chi tiết: `kb/projects/amh-adaptivity-review-20260910.md`.

## CAPIT — vị thế THẬT đang giữ (`capit_fired` ≠ "đang giữ")
⚠️ `capit_fired` tính lại mỗi phiên, KHÔNG phải cờ vị thế. Đọc `data/golive_v23_status.json` (`n_capit_basket`, `capit_adv_caps`). **PNJ EXCLUDED** (due-diligence gate, 07-20, TTL ~08-23). Chi tiết: `kb/current_ops_ext.md § CAPIT`.

## Domain-constraint layer
- **P1 LIVE**: `filter_lag_rating_orders()` — gate 8L rating≤3 tầng ORDER. 14/14+22/22 selfcheck.
- **P0 ACTIVE (HARD BLOCK)**: `check_plan_funding()` trong `bot_execute.py:536` từ 08-04. Chi tiết 2 bug đã vá (08-07): `kb/current_ops_ext.md § Domain-constraint`.

## Features đang LIVE — đọc đầu phiên, không để mất dấu
> Cập nhật mỗi khi có feature mới go-live. Source of truth: `kb/projects/paper_programs_registry.json`.

- **EXTREME-regime gate** (`extreme_regime_enabled=True`) — LIVE SpaceX+ZaloPay từ **2026-08-22** (account overrides `secrets/trading_bot_accounts.json`). Default config=False, override=True. Alert pipeline: `bin/extreme_regime_dd_alert.sh` hook trong `run_bot.sh`. Commit `07726527`.
- **Vol-scale buy chase-cap** (`chase_cap_vol_scale_enabled=True`) — LIVE toàn bộ từ **2026-08-04** (`config.py:190`). k=2.0, ceil=4%, clamp static→ceil theo 20d rvol.
- **fill_timing HYBRID** (`fill_timing_live_gate=False`, `fill_timing_hybrid_live_gate=False`) — LIVE từ **2026-08-26** (user duyệt option A). BUY blocks: 11:00/11:15/13:00/13:15/13:30. SELL blocks: 09:15/09:30/09:45/10:00. Monitoring: fill-vs-open mỗi ~10 phiên, rollback nếu mean >+22bps. Commit `9be375a4`.
- **CAPIT margin lever** (`capit_margin_lever.enabled=True`) — LIVE từ **2026-08-24**. Ngày có CAPIT margin phải chạy `approve_margin_day.py` TRƯỚC bot.
- **Domain-constraint P1** (`filter_lag_rating_orders()`, 8L rating≤3 gate) — LIVE. 14/14+22/22 selfcheck.
- **close_repair.py — Layer 2 self-computed back-adjustment khi vendor backfill kẹt vĩnh viễn** (`MIKE_CLOSE_REPAIR` mặc định ON) — LIVE từ **2026-09-28**, commit `3c55c249`. Tự tính hệ số (xác nhận 2 nguồn độc lập, lệch <0,006%), fail-closed khi không đủ bằng chứng. Vòng review + VND/VNM: `kb/projects/corp-action-nav-chain-20260922.md`.
- **NAV corp-action L1 — cảnh báo TRƯỚC ex-date** (`bin/nav_exdate_forecast.py`) — LIVE từ **2026-09-22**, commit `2a7dd54e`. Wire `[pipeline-0]` trong `bq_freshness_check.sh` (TRƯỚC `exit 1` đầu tiên) ⇒ chuỗi 19:00 in cảnh báo corp-action của mã ĐANG GIỮ vào plan report + Discord. Selfcheck 58/58.
- **NAV corp-action gate v2 (L2-L4)** (`classify_qty_residual` + `_mult_explains` trong `daily_nav_snapshot.py`) — LIVE từ **2026-09-22**, commit `4dcc3643`, **5 vòng arch-review**. Thay tripwire so giá MÙ bằng PHÂN LOẠI:
  · sự kiện CỔ PHIẾU ⇒ chặn **rc=5** theo bằng chứng KL credit sớm THẬT (phần dư sau khi trừ FILL trong ngày khớp tỉ lệ sự kiện) — KHÔNG chặn theo lịch, KHÔNG phụ thuộc ngưỡng giá 5% ⇒ đóng lỗ hổng sự kiện tỉ lệ nhỏ
  · 3 nhánh còn lại (cổ tức TIỀN ⇒ mark giá CUM + trừ khoản phải thu; `--from-raw` quy ngược KL; không giải thích được ⇒ nói thẳng, §29): `kb/projects/corp-action-nav-chain-20260922.md`
- **Ex-date price-frame — KL và GIÁ phải CÙNG hệ quy chiếu** (`bin/exdate_frame.py` + wire vào `compute_active_nav.py` / `park_holdings.py` / `compute_park_trim.py` / `compute_jit_unpark.py`) — LIVE từ **2026-09-24**, commit `508bb607`, **3 vòng arch-review**. Sự cố gốc + nhánh định giá: `kb/projects/corp-action-nav-chain-20260922.md`.
  · không dựng được giá cùng hệ, hoặc KL đổi chưa giải thích được ⇒ **rc=6, KHÔNG ghi file** (mẫu số sizing: số sai tệ hơn số cũ)
  · `park_holdings` phát `frame_blocked_tickers` ⇒ `compute_park_trim`/`compute_jit_unpark` trả **BLOCKED_FRAME** thay vì trim trên mẫu số phồng
  ⚠️ **CÙNG LỚP LỖI CÒN 4 CALL-SITE CHƯA VÁ** (xem `kb/memory/Mike.md`): `dividend_adjusted_return.py:473-478` (chạm SỐ CÔNG BỐ nhà đầu tư §21 — ưu tiên cao nhất), `discretionary_margin_gate.py:335` (sleeve margin tiền thật, latent), `report_return_gate.py` (lỗ hổng phủ im lặng), `discretionary_accumulation_inject.py:124`, + `due_diligence.py:173-202 adv_vnd()` (chiều an toàn). arch-reviewer nói rõ **KHÔNG khẳng định đã quét hết**.
  Selfcheck 38/0 + 64/0 + 8/0 qua 3 TZ. rc=5 là mã MỚI: `eod_trading_report.sh` không ghi marker, `nav_sync_retry.sh` không retry 2h, `nav_snapshot_daily.sh` escalate ngay. Runbook rc=5 ĐÃ LIVE ở `kb/ops_runbook.md` (mục 5, ~dòng 142).

- **KL hưởng quyền neo bằng BẰNG CHỨNG, không bằng KL cuối ngày cum** (`bin/dividend_adjusted_return.py` — `qty_entitled`/`credit_frame`) — LIVE từ **2026-09-24**, commit `1608a267`, arch-review APPROVED. Call-site **thứ 3** cùng lớp lỗi corp-action, chạm SỐ CÔNG BỐ nhà đầu tư (§21).
  · vá: neo theo bằng chứng KHỐI LƯỢNG (`classify_qty_residual`) + bằng chứng GIÁ (`verify_post_event_price`); thiếu bằng chứng ⇒ `status="unknown"` ⇒ **BỎ phương trình** (không coi như 0), fail-closed
  · Chi tiết, Q1 (không số công bố nào bị ảnh hưởng) và VIỆC LÀM SAU (`broker_qty()` lấy lô cuối): `kb/projects/corp-action-nav-chain-20260922.md`.

- **LỆCH NGUỒN VENDOR ⇒ hạ UNVERIFIED + cảnh báo ĐÚNG NGƯỜI (Winston)** (`bin/dividend_adjusted_return.py` + `bin/report_return_gate.py` + `bin/vendor_mismatch_alert.sh` MỚI) — LIVE từ **2026-09-24**, commit `dc147859` và `6b751298` (nhánh con D1). Chỉ đạo user 2026-09-24: *"vendor mismatch thì hạ về unverified rồi raise warning lên để tôi kêu winston xử lý."* Nhánh D1, hợp đồng dòng máy đọc 7 trường, đường phát lại, selfcheck: `kb/projects/corp-action-nav-chain-20260922.md`.
  · broker vs `tav2_bq.corporate_action` lệch >1% hoặc >1đ/cp ⇒ `kind=UNVERIFIED`, lý do mang **CẢ HAI** số + gọi tên Winston (§21: UNVERIFIED thì CẤM công bố tỉ suất)
  · **ĐÃ VÁ 2026-09-24, commit `206dd348`**: `bq_corp_action` NÉM LẠI exception thay vì `except Exception: return None`; nhãn **`lookup_failed`** tách khỏi `unavailable`.
  · **`broker_qty()` gộp TỔNG lô** — LIVE từ 2026-09-24, merge `4b59c6d1`. §21: **KHÔNG số công bố nào đổi**.
  · **VÁ 2026-09-24, commit `a56203f2`**: gap test-only `report_return_gate.py:732` đã bịt. ⚠️ arch-reviewer tìm thêm 3 nhánh anh em CÙNG lớp vacuous-anchor CHƯA vá: `:723` (`cash_mismatch`), `:727` (`stock_leg_ignored`), `:737` (`reasons_present - {...}`) — chi tiết: `kb/projects/corp-action-nav-chain-20260922.md`.

- **Bẫy đường dẫn selfcheck — MỌI selfcheck import module qua `load_module()`/`sys.path.insert` phải TỰ ĐỔI theo worktree, không hardcode canonical** (phát hiện 2026-09-24 khi verify C2, commit `a56203f2`). Ca gốc + bản vá: `kb/projects/corp-action-nav-chain-20260922.md`.
  ⚠️ **CÒN MỞ — 3 file khác nghi cùng lớp bug, CHƯA vá** (Taylor quan sát, arch-reviewer xác nhận 3/3 nhưng lưu ý phạm vi khác nhau): `bin/paper_corp_action_selfcheck.py:28-31` và `bin/send_plan_report_park_jit_selfcheck.py:28-30` cắn **worktree `mike/`**; `bin/due_diligence_corp_flags_selfcheck.py:19-21` cắn **worktree ngoài `mike/`** (repo `WorkingClaude` gốc — `trading_bot/due_diligence.py`), KHÔNG cắn worktree `mike/` vì module đó không tồn tại trong `mike/`. arch-review vòng 4-site (2026-09-24) tìm thêm 1 file: `bin/nav_cum_dividend_selfcheck.py:32-35` (`WC_ROOT` đếm dirname sai trong worktree lồng, **crash** `FileNotFoundError` khi chạy ngoài canonical — CHƯA vá).

- **4 call-site còn lại của lớp lỗi corp-action — audit xong 2026-09-24 (dispatch `Taylor_20260924_064510`), arch-review theo TỪNG VIỆC — CẢ 4 ĐÃ LIVE, ĐÓNG HẲN CHUỖI AUDIT NÀY:**
  · **Việc 4 `report_return_gate.py:558-573` unmatched — APPROVED, LIVE, commit `569be662`.** · **Việc 3 `verify_account_snapshot.py:307` `broker_positions_from_raw()` — APPROVED vòng 2, LIVE, commit `96ee1bb8`+`7700582d`.** · **Việc 1 `discretionary_accumulation_inject.py` `broker_filled_qty()` — APPROVED vòng 2, LIVE, commit `5e6fb9af`+`642d4f5a`.** (⚠️ **Lưu ý docstring** (chưa sửa, không chặn): câu "tự khớp" chỉ ĐÚNG TUYỆT ĐỐI khi `baseline_qty_before_program=0` (đúng cả 2 state LIVE hôm nay); `baseline>0` thì thiếu `(r−1)×baseline` cp vĩnh viễn, hướng AN TOÀN (mua thiếu, không overbuy).) · **Việc 2 `discretionary_margin_gate.py` arm_price — APPROVED vòng 12, LIVE, merge `c5247def` (12 commit vòng 3→12, từ `26ef0c58` tới `bc22bed2`).** Chi tiết từng việc: `kb/projects/corp-action-nav-chain-20260922.md`.

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

## Measurement integrity audit — cadence định kỳ (mở 2026-09-27, sau retro custom30V double-count)
Lý do: bug custom30V double-count (`mcap = Close_adj × OShares`, −4,48pp CAGR) sống trong production nhiều tháng, KHÔNG bị bắt bởi self-check 0 VND LẪN quant-skeptic → `kb/projects/measurement-integrity-audit-20260927.md`.
**Review quý — next ~2026-12-27: dispatch Taylor lặp lại đúng phương pháp `measurement-integrity-
audit-2026-09-27` (6 bất biến × mọi chuỗi return/level/weight/NAV đang production), rồi quant-
skeptic verify từng finding trước khi wire.** Artifact/phương pháp gốc:
`agents/Taylor/research/measurement_integrity_audit_20260927/`. quant-skeptic đã thêm đòn tấn
công thứ 8 (double-count corp-action adjustment) vào checklist chuẩn (`~/.claude/agents/
quant-skeptic.md`) — audit định kỳ vẫn cần vì đòn 8 chỉ bắt ĐÚNG lớp lỗi đã biết, không thay
được việc chủ động quét tìm lớp lỗi MỚI.

## Macro watch — rủi ro cấu trúc BĐS VN (mở 2026-08-26)
Bobby classify STRUCTURAL_ACCUMULATION/AMBIGUOUS. Thesis + lead indicators + playbook đã chốt:
`kb/projects/vn-realestate-structural-risk-20260826.md`. KHÔNG đổi V2.4/DT5G/margin theo thesis này.
**Review quý — next ~2026-11-26: dispatch Bobby refresh bảng lead indicators + quét
`kb/structural_break_watch.json`** (6 sự kiện cấu trúc: nâng hạng, KRX, T+, luật margin, room
ngoại, sản phẩm mới). Protocol: `kb/projects/amh-structural-break-protocol-20260910.md` —
sự kiện kích hoạt ⇒ BẮT BUỘC re-validate đúng tầng, mặc định vẫn là KHÔNG đổi tham số.

## Vận hành hàng ngày = TỰ PHÁT HIỆN → TỰ SỬA → BÁO CÁO (mandate 2026-07-07)
Ranh giới cứng (KHÔNG tự sửa): trade plan, trading_rules.json, logic đặt lệnh, crontab dòng thực thi, xoá dữ liệu, BOT_STOP. Chi tiết: `kb/ops_runbook.md`.

## Workflow ngày trading — Discord topic routing
- **Trading Daily (1521470705563340910)** — preflight, run_bot, heartbeat, ops_health_check.sh
- **DollarBill plan (1521183164364754974)** — lập kế hoạch. **Mirror duyệt plan vào đây dù đang ở topic khác.**
- **Trading report (1522576692638388364)** — báo cáo tổng hợp ngày/tuần/tháng (KHÔNG phải alert)
- Dispatch Taylor → ghi `discord_thread_id` vào job record ngay lúc dispatch, đọc lại qua `_job_thread_id`.
- Plan T+1 không sẵn sàng → ESCALATE (Telegram + Discord + bus question `plan-t1-not-ready`), KHÔNG retry tự động.

## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)
- R&D pipeline (mọi thử nghiệm paper-only) → `rnd-pipeline-tracker.md`
- **Tài khoản = quỹ mở** (đo hiệu suất; user duyệt 2026-10-10) → `fund-unit-performance-policy-20261010.md`
- Migration `ticker_prune` → `universe_pit` (G5-G9) → `universe-pit-migration.md`
- LAG ADV>0 filter — đo edge vs hiện vật fill → `lag-adv-filter-tracking.md` — chủ Taylor, mở 2026-08-03.
  **KHÔNG kết luận gì** trước 2 mốc cứng: checkpoint **2026-12-15**, rà soát đầy đủ **2027-03-31**.
- CASH_VENDOR gate (số cổ tức từ `tav2_bq.corporate_action` khi broker không giải được) →
  `cash-vendor-gate-tracking.md` — user chốt 2026-08-15 **giữ ĐÓNG**; mở lại chỉ khi có ≥1 sự
  kiện ISS/hỗn hợp VÀ đã qua **2026-09-13**, và vẫn cần user xác nhận lần nữa lúc đó.
