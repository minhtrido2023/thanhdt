# Mike fleet — context pack (v3760)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-10-09T21:02:33] Mike/finding — weekly-ops-audit-2026-10-10: {"report": "**Weekly ops audit 10/10** — 1 bug thật (selfcheck-only) đã tự sửa, 0 regression production, 0 escalation mới. Bus còn **1 PENDING** (giảm từ 22 tuầ …
- [2026-10-09T22:09:25] Wags/answer — selfcheck-red: mike/bin/annualization_basis_selfcheck.py — recovered 2026-10-09: {"context": "selfcheck_baseline_diff tự đóng: ca đỏ này đã XANH trở lại", "file": "mike/bin/annualization_basis_selfcheck.py", "artifact": "chạy lại lúc 2026-10 …
- [2026-10-09T22:09:25] Wags/answer — selfcheck-red: mike/bin/plan_position_drift_check_selfcheck.py — recovered 2026-10-09: {"context": "selfcheck_baseline_diff tự đóng: ca đỏ này đã XANH trở lại", "file": "mike/bin/plan_position_drift_check_selfcheck.py", "artifact": "chạy lại lúc 2 …
- [2026-10-10T02:00:04] Mike/finding — report-cadence-scheduled-weekly_2026-10-05_2026-10-09: {"kind": "weekly", "period": "tuần 2026-10-05 → 2026-10-09", "target_file_spacex": "/home/trido/thanhdt/WorkingClaude/mike/reports/SpaceX_weekly_report_2026-10- …
- [2026-10-10T02:21:57] Taylor/finding — weekly-report-2026-10-05_to_2026-10-09: {"files": ["mike/reports/SpaceX_weekly_report_2026-10-05_to_2026-10-09.md", "mike/reports/ZaloPay_weekly_report_2026-10-05_to_2026-10-09.md"], "nav_end": {"Spac …
<!--RECENT-END-->

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
- **AlphaLens Paper**: FPT/ACB/MBB/HDB — **ĐÃ ĐÓNG 2026-10-01** (user chọn A: không wire live) → `kb/projects/rnd-pipeline-tracker.md`.
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
- Migration `ticker_prune` → `universe_pit` (G5-G9) → `universe-pit-migration.md`
- LAG ADV>0 filter — đo edge vs hiện vật fill → `lag-adv-filter-tracking.md` — chủ Taylor, mở 2026-08-03.
  **KHÔNG kết luận gì** trước 2 mốc cứng: checkpoint **2026-12-15**, rà soát đầy đủ **2027-03-31**.
- CASH_VENDOR gate (số cổ tức từ `tav2_bq.corporate_action` khi broker không giải được) →
  `cash-vendor-gate-tracking.md` — user chốt 2026-08-15 **giữ ĐÓNG**; mở lại chỉ khi có ≥1 sự
  kiện ISS/hỗn hợp VÀ đã qua **2026-09-13**, và vẫn cần user xác nhận lần nữa lúc đó.

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
- ✅ **park=0 ĐÃ PIN (user duyệt 2026-10-08 23:30)**: **`pin0%` 22,12% … `pin1M` 25,42%** (egg = lãi 1M Big-4 PIT, KHÔNG 8,543%); **neo DD GIỮ −25,2%** (park0 đo −23,9%); park 0 vs 0,3 KHÔNG phân biệt được. 25,42% chỉ là ĐẦU TRẦN. Registry mục "2026-10-08".
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

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/INDEX.md (KHÔNG nạp sẵn — `bin/kb_recall.sh "<từ khoá>"` hoặc grep). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
