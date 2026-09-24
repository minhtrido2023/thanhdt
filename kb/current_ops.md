# Current Operations — Mike fleet
> Mike cập nhật thủ công khi có thay đổi trạng thái quan trọng. Đọc trước mọi thứ khác khi restart.
> Cập nhật lần cuối: 2026-08-21 (token-cost trim #4 — warm sections → `kb/current_ops_ext.md`;
> giữ lại hot path: kill-switch, trading status, signal holds, routing rules).
> Chi tiết CAPIT/domain-constraint/due-diligence/cron/daemon: `cat kb/current_ops_ext.md`

## Kill-switches
- `data/BOT_STOP`: tạo file = dừng mọi giao dịch tức thì
- `state/NOTIFY_OFF`: tắt Telegram push tạm thời
- V2.5: `trading_rules.json v1.7` → v25_leverage STATUS=DISABLED

## Đang trading (LIVE)
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking **80%** idle cash (config F1, đổi từ 70% ngày 2026-08-04, `trading_rules.json` `neutral_parking.default_park_of_idle_pct`). run_bot.sh 09:05 ICT T2-T6. NAV: `nav_history_SpaceX.csv` hoặc EOD report.
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, CASH-ONLY. **DGC EXCLUDED** (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026). Sizing dùng `active_nav`. Cùng target parking 80% (không có override riêng).
- **AlphaLens Paper**: FPT/ACB/MBB/HDB, tracking đến 2026-09-30. DollarBill phụ trách.
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,2tr / ZaloPay ~38,8tr (đo 08-19), đã cộng NAV tự động — KHÔNG phải `availableCash`, cần rút T+1. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.

## Signal holds
- **VPI/BAL**: signal_hold 08-19→09-16 ĐÃ GỠ 2026-09-16. Review dựa trên `amh-adaptivity-review-20260910.md` (Taylor job A/B/C + quant-skeptic): lý do gốc của HOLD (edge-health dashboard báo mom_200 FLIPPED) đã bị bác — kênh đó REFUTED cho quyết định BAL; mom_200 IC hồi phục dương Q2/2026. User duyệt RESUME 2026-09-16 23:19 ICT: "tuân theo chiến lược production đã duyệt, không cần điều chỉnh gì" (`decided_by: user`, bus `answer/bal-vpi-checkpoint-resume-decision`). VPI/BAL trở lại logic bình thường từ plan kế tiếp — không còn escalate riêng.

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
- **NAV corp-action L1 — cảnh báo TRƯỚC ex-date** (`bin/nav_exdate_forecast.py`) — LIVE từ **2026-09-22**, commit `2a7dd54e`. Wire `[pipeline-0]` trong `bq_freshness_check.sh` (TRƯỚC `exit 1` đầu tiên) ⇒ chuỗi 19:00 in cảnh báo corp-action của mã ĐANG GIỮ vào plan report + Discord. Selfcheck 58/58.
- **NAV corp-action gate v2 (L2-L4)** (`classify_qty_residual` + `_mult_explains` trong `daily_nav_snapshot.py`) — LIVE từ **2026-09-22**, commit `4dcc3643`, **5 vòng arch-review**. Thay tripwire so giá MÙ bằng PHÂN LOẠI:
  · cổ tức TIỀN có bằng chứng ⇒ mark giá **CUM**, trừ khoản phải thu khỏi tiền (không đếm 2 lần)
  · sự kiện CỔ PHIẾU ⇒ chặn **rc=5** theo bằng chứng KL credit sớm THẬT (phần dư sau khi trừ FILL trong ngày khớp tỉ lệ sự kiện) — KHÔNG chặn theo lịch, KHÔNG phụ thuộc ngưỡng giá 5% ⇒ đóng lỗ hổng sự kiện tỉ lệ nhỏ
  · `--from-raw` + corp-action ĐÃ CONFIRMED + multiplier TÁI TẠO được KL trước sự kiện ⇒ quy ngược KL (giữ đường phục hồi cũ)
  · không giải thích được ⇒ nói THẲNG "chưa giải thích được", không đoán (§29)
- **Ex-date price-frame — KL và GIÁ phải CÙNG hệ quy chiếu** (`bin/exdate_frame.py` + wire vào `compute_active_nav.py` / `park_holdings.py` / `compute_park_trim.py` / `compute_jit_unpark.py`) — LIVE từ **2026-09-24**, commit `508bb607`, **3 vòng arch-review**. Sự cố gốc: đêm T-1 GDKHQ, DNSE credit KL mới vào `positions` NGAY (VPB 1.100→1.386) trong khi giá đóng cửa G1 phiên T-1 vẫn là giá CÒN QUYỀN ⇒ nhân chéo làm `active_nav` phồng (SpaceX +7.969.500 = +0,80%; ZaloPay +8.694.000 = +1,64%) và plan sinh lệnh PARK_TRIM trên rổ phồng.
  · mã có bằng chứng credit sớm ⇒ định giá bằng `marketPrice` của CHÍNH bản ghi vị thế, NHƯNG chỉ sau khi nó TÁI TẠO được giá cum qua hệ số sự kiện (KHÔNG tin thẳng `marketPrice` — ca SCL 08-28 đứng im, MBB 08-14 một bản đọc mang đồng thời 2 hệ)
  · không dựng được giá cùng hệ, hoặc KL đổi chưa giải thích được ⇒ **rc=6, KHÔNG ghi file** (mẫu số sizing: số sai tệ hơn số cũ)
  · `--asof` ngày khác hôm nay, hoặc `--out` trỏ vào chính file canonical (so bằng `realpath`) ⇒ **rc=7, TỪ CHỐI ghi**
  · `park_holdings` phát `frame_blocked_tickers` ⇒ `compute_park_trim`/`compute_jit_unpark` trả **BLOCKED_FRAME** thay vì trim trên mẫu số phồng
  Selfcheck 59/59 qua 5 TZ. Replay 14 account-night corp-action thật: 12/14 tự sửa giá, 2/14 gắn cờ (đều đã bị `BLOCKED_RECONCILE` chặn sẵn) ⇒ **0 báo động mới**.
  ⚠️ **CÙNG LỚP LỖI CÒN 4 CALL-SITE CHƯA VÁ** (xem `kb/memory/Mike.md`): `dividend_adjusted_return.py:473-478` (chạm SỐ CÔNG BỐ nhà đầu tư §21 — ưu tiên cao nhất), `discretionary_margin_gate.py:335` (sleeve margin tiền thật, latent), `report_return_gate.py` (lỗ hổng phủ im lặng), `discretionary_accumulation_inject.py:124`, + `due_diligence.py:173-202 adv_vnd()` (chiều an toàn). arch-reviewer nói rõ **KHÔNG khẳng định đã quét hết**.
  Selfcheck 38/0 + 64/0 + 8/0 qua 3 TZ. rc=5 là mã MỚI: `eod_trading_report.sh` không ghi marker, `nav_sync_retry.sh` không retry 2h, `nav_snapshot_daily.sh` escalate ngay. Runbook rc=5 ở `kb/ops_runbook.md.proposed` — **CHỜ MIKE DUYỆT ĐỂ ĐƯA LIVE (§13)**.

- **KL hưởng quyền neo bằng BẰNG CHỨNG, không bằng KL cuối ngày cum** (`bin/dividend_adjusted_return.py` — `qty_entitled`/`credit_frame`) — LIVE từ **2026-09-24**, commit `1608a267`, arch-review APPROVED. Call-site **thứ 3** cùng lớp lỗi corp-action, chạm SỐ CÔNG BỐ nhà đầu tư (§21).
  · `_qty_at` cũ lấy KL từ bản ghi positions CUỐI NGÀY `last_cum_date` = đúng đêm broker credit sớm; lá chắn `STOCK_SUSPECTED` bị vô hiệu vì sau credit sớm thì `qty[last_cum] == qty[ex_date]`
  · vá: neo theo bằng chứng KHỐI LƯỢNG (`classify_qty_residual`) + bằng chứng GIÁ (`verify_post_event_price`); thiếu bằng chứng ⇒ `status="unknown"` ⇒ **BỎ phương trình** (không coi như 0), fail-closed
  · ⚠️ hướng "neo theo `broker_effective_ts`" (Mike chỉ đạo) đã BỊ BÁC bằng dữ liệu thật: MBB 10/08 bản ghi cuối 19:12:13 vẫn chưa credit (mốc khai 19:32:49 đúng số nhưng SAI lý do); VPB 23/09 bản ghi duy nhất trước mốc là 04:51 SÁNG ⇒ neo ở đó bỏ mất lệnh khớp trong chính phiên cum (ca thật MBB bán 1.500→1.100 lúc 09:15)
  · `--selfcheck` 120/0 qua 3 TZ (58 ca cũ giữ nguyên); e2e `--resolve` BYTE-IDENTICAL với master
  **Q1 — ĐÃ KIỂM, KHÔNG SỐ CÔNG BỐ NÀO BỊ ẢNH HƯỞNG**: 24 sự kiện DIV+ISS cùng ex-date sau go-live 01/07 × 39 mã đã từng nắm giữ ⇒ **giao RỖNG** (Mike tự xác nhận bằng BQ + quét toàn bộ `dnse_raw`). Nhịp thật ~5-7 ca/năm ⇒ không phải ca hiếm, chỉ chưa cắn.
  ⚠️ **VIỆC LÀM SAU, ưu tiên cao nhất**: `dividend_adjusted_return.py:469-472` `broker_qty()` lấy **LÔ CUỐI** thay vì **TỔNG LÔ** ⇒ thiếu 25% KL thật ở **135 cặp (mã, ngày)** của ZaloPay (BID 14/08: 320 vs 427); `credit_frame` thì gộp lô ĐÚNG ⇒ hai quy ước cùng tồn tại trong một lần giải. Pre-existing + fail-closed, nhưng BID/VCB/MBB trả cổ tức tiền hằng năm nên sẽ cắn.

- **LỆCH NGUỒN VENDOR ⇒ hạ UNVERIFIED + cảnh báo ĐÚNG NGƯỜI (Winston)** (`bin/dividend_adjusted_return.py` + `bin/report_return_gate.py` + `bin/vendor_mismatch_alert.sh` MỚI) — LIVE từ **2026-09-24**, commit `dc147859` (**4 vòng**: 3 arch-review độc lập + 1 vòng sửa tài liệu/test) và `6b751298` (nhánh con D1, **2 vòng**, vòng cuối APPROVED 0 required_change). Chỉ đạo user 2026-09-24: *"vendor mismatch thì hạ về unverified rồi raise warning lên để tôi kêu winston xử lý."*
  · broker vs `tav2_bq.corporate_action` lệch >1% hoặc >1đ/cp ⇒ `kind=UNVERIFIED`, lý do mang **CẢ HAI** số + gọi tên Winston (§21: UNVERIFIED thì CẤM công bố tỉ suất)
  · **nhánh con D1**: vendor khai THUẦN CỔ PHIẾU (`vendor_cash=0, vendor_stock>0`) mà solver vẫn trả `CASH_CONFIRMED` ⇒ trước đây gán nhãn lành tính `broker_only` (không consumer nào đọc) và **CÔNG BỐ cổ tức KHÔNG TỒN TẠI, 0 cảnh báo**. Discriminator: `share_multiplier == 1.0` (solver chưa hề biết chân cổ phiếu). Chống quá-hạ-cấp: `share_multiplier > 1` ⇒ VẪN QUA; vendor thiếu hẳn dòng DIV (`cash=0, stock=0`) ⇒ VẪN CÔNG BỐ
  · `SANITY_REL=0.01` khiến "mult==1 mà nghiệm tiền vẫn ĐÚNG" gần như bất khả (cần ε ≤ 0,036% với c=1.000, P=27.800) ⇒ không thể lấy oan sự kiện hỗn hợp giải đúng. Họ **"quyền mua cho cổ đông hiện hữu"** (MBS 02/04, SHB 03/04) credit hàng tuần SAU ex-date nên `mult=1.0` ⇒ **cả hai lá chắn cũ hệ thống hoá việc trượt**, D1 là phòng thủ duy nhất
  · dòng máy đọc `VENDOR_MISMATCH_ALERT|<acct>|<mã>|<ex>|<broker>|<vendor>|<đang công bố>` giữ **ĐÚNG 7 trường NGUYÊN BYTE** (đo thật: thêm trường thứ 8 làm consumer đảo `blocked` 1→0 và nói "báo cáo vẫn gửi" đúng lúc đang CHẶN); mã lý do đi ở dòng TAG RIÊNG `VENDOR_MISMATCH_REASON|...`. Reason thiếu/rỗng ⇒ **fail-closed "unknown"**, KHÔNG đoán (§29)
  · `vendor_mismatch_alert.sh`: Discord là kênh **CHÍNH và là ĐIỀU KIỆN** để ghi de-dup — notify thất bại ⇒ in LỖI THẬT + **KHÔNG** ghi state; bus là kênh PHỤ, hỏng thì đi tiếp. State ghi nguyên tử `tmp+os.replace+fsync`. Câu Discord + "Việc cần làm" RẼ theo mã lý do (3 nhánh)
  · ⚠️ **đường phát lại**: KHÔNG phải sweep cùng file (`check_report_cadence.sh:76-81` bỏ qua file đã giao; `report_delivery_gate.py:238-239` return trước validate) mà là **báo cáo EOD NGÀY KẾ** (tên file khác, `LOOKBACK_DAYS=120` + còn nắm vị thế). Mất cảnh báo thật CHỈ khi notify chết đúng hôm đó **VÀ** bán hết vị thế trước báo cáo kế. Bus `error` KHÔNG phải backstop (`ops_health_check.sh:731` chỉ xét `question`)
  Selfcheck: `dividend_adjusted_return` **148/0**, `report_return_gate --selfcheck` **75/75**, `vendor_mismatch_alert_selfcheck` **57/0 qua 5 môi trường** (ICT, America/New_York, UTC, Pacific/Kiritimati, `env -u TZ`), gate `--root-only` PASS. K1 (39 mã × 6 tháng): **0/62** lệch nguồn thật; mẫu số ĐÚNG của ô rủi ro D1 = **6 ca `CASH_CONFIRMED`** (không phải 62), 0/6 khớp hình dạng ⇒ 0 dương tính giả.
  · **ĐÃ VÁ 2026-09-24, commit `206dd348`** (6 vòng: 4 arch-review độc lập + 2 vòng sửa): `bq_corp_action` NÉM LẠI exception thay vì `except Exception: return None`; nhãn **`lookup_failed`** tách khỏi `unavailable` (= vendor XÁC NHẬN 0 dòng, 25/62 ca thật, GIỮ nguyên hành vi). Trước đó BQ hỏng ⇒ **CẢ HAI lá chắn tắt IM LẶNG**.
    · dòng máy đọc RIÊNG `VENDOR_LOOKUP_FAILED|<acct>|<mã>|<ex>|<broker>|<had_broker_cash>|<published>` (7 trường); hợp đồng `VENDOR_MISMATCH_ALERT` giữ NGUYÊN BYTE
    · `had_broker_cash` chụp `(kind == CASH_CONFIRMED)` **TRƯỚC** khi hạ `kind` — lúc đó `CASH_CONFIRMED` chỉ có MỘT nguồn (`solve_from_broker`, nghiệm trên `cashDividendReceiving` THẬT) ⇒ `True ⟺ per_share LÀ tiền broker`, không phải proxy
    · **CHẶN chỉ khi `had_broker_cash AND published`** — ca chưa từng `CASH_CONFIRMED` thì `cash_per_share=0` trước VÀ sau khi BQ lỗi ⇒ không mất số công bố nào ⇒ không chặn oan. Đo K1: **6/62** ca `had_broker_cash=1`, **56/62** `=0` mà cả 56 đều có `per_share>0` ⇒ bản trước sẽ in câu SAI + chặn oan ~90% dòng
    · câu chẩn đoán RẼ theo provenance (§29): `=0` ⇒ *"broker CHƯA giải được số nào (ước lượng từ giá rơi Xđ/cp, KHÔNG phải tiền broker thật)"*; `=1` ⇒ *"broker đã giải Xđ/cp"*. Câu *"hai nguồn độc lập đang bất đồng + Gỡ chặn = Winston"* chỉ in khi CÓ nguồn thứ hai; ca thuần `lookup_failed` ⇒ *"gỡ chặn = chạy lại khi BQ khoẻ"*. 2 caller (`check_report_cadence.sh:112`, `eod_trading_report.sh:84`) rẽ bằng **grep tag** trên `$GATE_OUT`, KHÔNG suy từ rc=10
    Selfcheck: `dar` **159/0** · gate **93/93** · alert **78/0** · `check_report_cadence_selfcheck` 32/32 · `eod_trading_report_account_filter` 21/0 · `--root-only` PASS. Mike tự bắn 5 mutation + arch-reviewer 16 mutation, tất cả chết bằng assertion CÓ TÊN; E2E gate↔shell khớp 4/4 góc.
  · **`broker_qty()` gộp TỔNG lô** — LIVE từ 2026-09-24, merge `4b59c6d1`: trước đây nhiều lô cùng mã khác `loanPackageId` thì chỉ lô CUỐI sống sót. Đo thật ZaloPay: **BID 14/08 320 → 427**, **MBB 14/08 232 → 632**; 135 cặp (mã, ngày) lệch 25-66,7%, chỉ BID/MBB/VCB; SpaceX 0 cặp (latent). §21: **KHÔNG số công bố nào đổi** (resolve 3 mã × 2 TK byte-identical hai cây).
  · **VÁ 2026-09-24, commit `a56203f2`**: gap test-only `report_return_gate.py:732` đã bịt bằng `MUTATION-GUARD gate_lookup_failed_reasons_present_note` (anchor riêng, không vacuous). ⚠️ arch-reviewer tìm thêm 3 nhánh anh em CÙNG lớp vacuous-anchor CHƯA vá: `:723` (`cash_mismatch`), `:727` (`stock_leg_ignored`), `:737` (`reasons_present - {...}` — assertion `gate_vendor_reason_unknown_no_guess` hiện dùng chung anchor với `:694-696` nên không phân biệt được nhánh nào chết).

- **Bẫy đường dẫn selfcheck — MỌI selfcheck import module qua `load_module()`/`sys.path.insert` phải TỰ ĐỔI theo worktree, không hardcode canonical** (phát hiện 2026-09-24 khi verify C2, commit `a56203f2`). `compute_active_nav_selfcheck.py` hardcode `WC = "/home/trido/thanhdt/WorkingClaude"` dùng cho **MỌI ca A-J** (không chỉ Section K kill-mid-write) ⇒ chạy selfcheck từ BẤT KỲ worktree nào cũng luôn test code MASTER — mọi "PASS" trước đó không chứng minh gì về code đang sửa trong worktree. Vá: `MIKE_BIN = HERE` (tự đổi theo vị trí vật lý file selfcheck) + `WC` qua `wc_paths.find_wc_root(__file__)` (tiện ích dùng chung, đã có 36 file khác trong `bin/` dùng). arch-reviewer tự bắn mutation 2 chiều xác nhận: bản vá bắt được lỗi tiêm vào worktree, bản kiểu-cũ bỏ lọt hoàn toàn.
  ⚠️ **CÒN MỞ — 3 file khác nghi cùng lớp bug, CHƯA vá** (Taylor quan sát, arch-reviewer xác nhận 3/3 nhưng lưu ý phạm vi khác nhau): `bin/paper_corp_action_selfcheck.py:28-31` và `bin/send_plan_report_park_jit_selfcheck.py:28-30` cắn **worktree `mike/`**; `bin/due_diligence_corp_flags_selfcheck.py:19-21` cắn **worktree ngoài `mike/`** (repo `WorkingClaude` gốc — `trading_bot/due_diligence.py`), KHÔNG cắn worktree `mike/` vì module đó không tồn tại trong `mike/`.

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

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
