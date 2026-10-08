# Mike fleet — context pack (v3706)
> Snapshot tự sinh bởi consolidator. Nguồn chuẩn tắc: kb/KNOWLEDGE.md.

<!--RECENT-START-->
## MỚI NHẤT — kết quả gần đây từ toàn fleet
- [2026-10-08T12:04:18] DollarBill/decision — plan-SpaceX-2026-10-09: {"account": "SpaceX", "plan_date": "2026-10-09", "action": "HOLD_ALL", "n_orders": 0, "dt5g_state": "NEUTRAL", "n_bal": 0, "lag_due": 0, "capit_episode": "CAPIT …
- [2026-10-08T12:33:31] Taylor/finding — adjfactor-pfm-nonblockers: DUNG sau arch-review NEEDS_CHANGES, CHUA merge: {"status": "DUNG_CHUA_MERGE", "reason": "arch-review 1 lan NEEDS_CHANGES (theo dispatch: dung, ghi du loi)", "branch": "chore/adjfactor-pfm-nonblockers-20261008 …
- [2026-10-08T13:13:23] Taylor/finding — adjfactor-pfm-nonblockers: MERGED 787ddac4: {"status": "MERGED", "sha": "787ddac4", "branch": "chore/adjfactor-pfm-nonblockers-20261008", "branch_head": "334a71f2", "arch_review_r2": "APPROVED (CONFIRMED) …
- [2026-10-08T13:55:19] Wags/finding — context-pack-trim: {"status": "STOPPED_NEEDS_CHANGES", "job": "Wags_20261008_133659", "branch": "chore/context-pack-trim-20261008", "commit": "f10b0326", "base": "ea5c066d", "work …
- [2026-10-08T14:06:19] Wags/finding — dispatch-token-telemetry: {"status": "STOPPED_NEEDS_CHANGES", "job": "Wags_20261008_133633", "branch": "feat/dispatch-token-telemetry-20261008", "commit": "bba411f3", "base": "ea5c066d", …
<!--RECENT-END-->

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
- **SpaceX** (DNSE 0002023347): V2.4 LIVE từ 2026-07-01, có margin. NEUTRAL parking **0% (TẮT)** — user chốt 2026-10-01 10:26 ICT (`decided_by: user`: "Park 0% chốt. Chỉ thay đổi khi lãi suất huy động có xu hướng hạ"); lịch sử 0,70→0,80 (08-04)→0,30 (09-27)→0,0 (10-01). 3 rail đồng bộ = 0,0 (merge 10-01, arch-review APPROVED, `park_rail_consistency_selfcheck` rc=0). Hiệu lực từ plan nháp đêm 01→02/10; tiền nhàn rỗi nằm ở Trứng vàng. **TRIGGER QUAY LẠI = lãi huy động có XU HƯỚNG HẠ ⇒ chỉ CẢNH BÁO user, KHÔNG tự khôi phục park** — định nghĩa user chốt 2026-10-01 12:40 ICT: Big-4 12M tháng này < tháng trước HOẶC CCTG đợt mới < đợt trước; cảnh báo do cron tuần `refresh_deposit_cctg_weekly.sh` (08:05 ICT thứ Hai) gửi Trading Daily. run_bot.sh 09:05 ICT T2-T6. NAV: `nav_history_SpaceX.csv` hoặc EOD report.
- **ZaloPay** (DNSE 0001743768): V2.4 LIVE từ 2026-07-06, CASH-ONLY. **DGC EXCLUDED** (`excluded_tickers`, HOSE hạn chế giao dịch đến ~11-12/2026). Sizing dùng `active_nav`. Cùng target parking 0% (không có override riêng).
- **PNJ EXCLUDED cả 2 account** (SpaceX+ZaloPay, `excluded_tickers` trong `secrets/trading_bot_accounts.json`) từ 2026-09-30, quyết định USER trên bus question `Taylor/pnj-trong-ro-custom30v-live-can-user-duyet-chan` (mở 2026-09-28) — option A. Lý do: hạ bậc AMBIGUOUS→NON do công bố DN 25-27/09 (0 vị thế thật ở cả 2 account tại thời điểm loại, xác nhận qua `data/execution_logs/dnse_raw_2026-09-30.jsonl`), cần "scrutiny exam" trước khi trở lại candidate rổ custom30V. **REVIEW TRIGGER = khi PNJ công bố BCTC Quý 3/2026** (KHÔNG phải TTL theo ngày) — lúc đó chạy lại due-diligence đầy đủ (kiểu fundamental-skeptic DGC/TV1), KHÔNG tự động khôi phục.
- **AlphaLens Paper**: FPT/ACB/MBB/HDB — **ĐÃ ĐÓNG 2026-10-01** (user chọn A: không wire live; 3/3 gate PASS nhưng N=1 cửa sổ × 4 mã chọn tay). R&D backtest PIT walk-forward chỉ mở nếu user yêu cầu.
- **Trứng vàng** (`egg.totalValue`): SpaceX ~100,9tr / ZaloPay ~102,2tr (đo 09-27), đã cộng NAV tự động — KHÔNG phải `availableCash`. ⚠️ **RÚT VỀ TRONG NGÀY, KHÔNG phải T+1** (đính chính 2026-09-27, Mafee job `Mafee_20260927_091828`: SpaceX 17/09 egg 100,9tr→51,0tr VÀ `availableCash` +49,8tr trong CÙNG snapshot 11:00:11 phiên sáng ⇒ tiền dùng mua được ngay phiên đó). ⚠️ **KHÔNG phải tiền gửi ngân hàng** — DNSE mô tả là "Sinh Lời Theo Ngày" qua giao dịch TRÁI PHIẾU niêm yết ⇒ không có bảo hiểm tiền gửi, phụ thuộc tổ chức phát hành; lãi đo thật **8,543%/năm** và DNSE **tự khấu trừ TNCN trước khi trả** nên số đó đã là net. Không thấy trần số dư (ZaloPay vượt 102tr vẫn cộng lãi phẳng); "Tài khoản Không Ngủ" là SẢN PHẨM KHÁC (trần 30 tỷ), đừng lẫn. `manual_offbook_assets_vnd` ĐÃ ĐÓNG vĩnh viễn 07-23.
  ⚠️ **ĐÍNH CHÍNH BẢN CHẤT 2026-09-27 (legal-vn, bus `dnse-trung-vang-legal-review-20260927`) — KHÔNG phải repo.**
  Mô tả "bond repo" trước đó của Mike là SAI. Bằng chứng từ chính FAQ DNSE + 3 dấu hiệu gián tiếp
  (phí lưu ký 0,3đ/trái phiếu/tháng, coupon về THẲNG TK khách, khách chịu thuế chuyển nhượng 0,1%):
  khách **SỞ HỮU THẬT** trái phiếu niêm yết, **lưu ký tại VSDC**; cấu trúc = 2 giao dịch mua bán
  dứt điểm + cam kết hợp đồng DNSE mua lại. ⇒ phần ĐANG GIỮ **không phải** claim không bảo đảm vào
  DNSE. Ba rủi ro THẬT, khác nhau: (a) TCPH vỡ nợ ⇒ chủ nợ không bảo đảm (Luật Phá sản 2014 Đ54);
  (b) cam kết mua lại của DNSE vô giá trị ⇒ **mắc kẹt tới đáo hạn / bán giá thị trường**, không mất
  trắng; (c) tiền đang trên đường lúc DNSE vỡ nợ — **không tra được** điều luật nào tường minh loại
  tiền khách khỏi khối tài sản phá sản (Đ89 LCK 2019 + TT121 Đ17-18 là nghĩa vụ HÀNH CHÍNH).
  **Việt Nam KHÔNG CÓ Quỹ bảo vệ nhà đầu tư** (đề xuất 2014, không vào Luật CK 2019) — đây là kết
  luận xác định, không phải "chưa tra được". Thuế: coupon **5%** + chuyển nhượng **0,1%** (TT111/2013;
  TT92/2015 bỏ phương án 20%; 0,1% giữ sau 01/7/2026 theo L109/2025 + NĐ253/2026 + TT87/2026), khấu
  trừ tại nguồn, **không quyết toán**. CTCK được phép làm việc này: TT121/2020 Đ28.3.
  🔴 **2 CÂU CHƯA TRẢ LỜI ĐƯỢC, phải hỏi DNSE bằng VĂN BẢN**: (1) trái phiếu lưu ký đứng tên KHÁCH
  hay nominee DNSE? (2) MÃ trái phiếu + TCPH cụ thể? — chưa biết (2) thì **không đo được tập trung
  per-name**. Quyền yêu cầu sao kê chi tiết: TT121 Đ17-18. DNSE từ chối nêu mã = **red flag**.
  Trần đề xuất (chưa user chốt): ~2% NAV/một TCPH (haircut 50% ⇒ max loss ≤1% NAV), sleeve ≤10% NAV
  — mức hiện tại ~100,9tr / ~102,2tr **đã ở hoặc vượt nhẹ trần tổng**.
  ✅ **USER CHỐT 2026-10-05 08:3x ICT (`decided_by: user`): Trứng vàng KHÔNG phải sleeve thông thường mà là một dạng của cash, coi tương đương tiền ⇒ KHÔNG có cơ chế "vượt trần"; trần ~2%/TCPH và sleeve ≤10% NAV ở trên KHÔNG áp dụng.** (2 câu hỏi DNSE bằng văn bản về nominee/mã TCPH vẫn là thông tin tham khảo, không chặn.)

- **[2026-10-03 10:34 ICT, user chốt] Định nghĩa XU HƯỚNG HẠ (chính xác hoá)**: ngay khi Big-4 điều chỉnh GIẢM lãi tiết kiệm 12 tháng HOẶC lãi chứng chỉ tiền gửi 6 tháng THẤP HƠN so với tuần thống kê trước ⇒ cảnh báo user (cron tuần `refresh_deposit_cctg_weekly.sh` + `deposit_cctg_trend_check.py`); vẫn CHỈ cảnh báo, không tự khôi phục park. User cũng DUYỆT rating_8l/DCF dùng effective rate (đã LIVE từ 10-01).

## Macro kill-switch A (lãi huy động > 7,5%) — merged 2026-10-01, DISPLAY-ONLY
- Code trên WC main (`deposit_rate_vn.macro_killswitch_a_status()`, `cctg_rate_vn.py`, dòng hiển thị trong `dna_report`/`value_radar`); quant-skeptic vòng 7 CONFIRMED, user duyệt. effective = max(Big-4 12M, CCTG Big-4), ngưỡng `> 7,5%`. **CCTG = kỳ hạn 12 THÁNG, lấy CAO NHẤT trong các NH Big-4 có phát 12M (user chốt 2026-10-05; trước đó 6M — anchor 09-30 7,5% là 6M, REBASE 10-05 = 7,4% BIDV/VietinBank; cặp 7,5→7,4 là artifact đổi kỳ hạn, đã ack trong state trend-check). Big-4 12M: cùng NH có online lẫn quầy ⇒ lấy số CAO NHẤT.** **KHÔNG có code path production nào đọc nó** — sleeve recovery vẫn paper, chưa chặn lệnh nào.
- ✅ **CCTG + Big-4 12M có auto-fetch HÀNG TUẦN** (cron `5 1 * * 1` = 08:05 ICT thứ Hai, LIVE từ 2026-10-01; 2 nguồn khác chủ + chéo ≤0,1pp + guard URL tái dùng; lệch/thiếu ⇒ KHÔNG ghi, nhắc xác nhận tay `manual_verify`; log `logs/refresh_deposit_cctg_weekly.log`). Rủi ro còn lại không code chặn được: tác tử bịa nhất quán cả URL lẫn rate. (Trước đó nhập tay.) Anchor 2026-09-30 = 7,5%; không cập nhật ⇒ stale >45 ngày ⇒ **ARMED vĩnh viễn từ 2026-11-15**. Big-4 stale ≈ 2026-10-20 (cùng cơ chế fail-closed).
- Trước khi wire vào gate thật: siết `deposit_rate_vn.deposit_events_df()` phía Big-4 (đang silent-drop dòng không parse được) + guard ngày tương lai tại load (quant-skeptic NON-BLOCKING #2/#3).
- ✅ **rating_8l NEUTRAL tilt + chuỗi DCF (dcf_valuation, dcf_refresh_gate, custom30_yield_labels, due_diligence) DÙNG effective rate = max(Big-4 12M, CCTG 6M)** — LIVE trên WC main từ 2026-10-01 (merge `d87a6f89`, user duyệt 12:40, quant-skeptic vòng 2 CONFIRMED). Tác động đo thật: rating_8l 6 mã −0,03 value_score (CTR MZG QNS PLX HVN GEE), 0 zone flip, top30 giữ nguyên; DCF discount 13,30%→14,00%, FV −0,7…−0,9% (VNM gần ngưỡng nhất MoS +2,6%→+1,8%; flag CHEAP/RICH trong plan report 21:00 có thể lật với mã sát 0). Lịch sử byte-identical ⇒ KHÔNG đổi số pin R3. **Fail-closed**: CCTG stale >45 ngày hoặc lỗi ⇒ cả 5 consumer rơi về Big-4 6,8% + WARNING (không phải ARMED). **Knob lùi**: env `DEPOSIT_RATE_CCTG_OVERLAY=0` (chỉ nhận đúng chuỗi "0"; lan tới mọi launcher source `wc_env.sh`, NGOẠI LỆ cron `dcf_refresh_gate` không source). `golive_recommend_v23.py:~991` (cổng CAPIT margin PIT, ngưỡng 9,0%) CỐ Ý vẫn Big-4-only — user chốt 2026-10-01 16:42: GIỮ Big-4, chỉ THÊM dòng hiển thị "effective vs 9%" (việc C: MERGED WC `98079284` 2026-10-01 18:10 — 2 field `pit_deposit_rate_effective`/`pit_deposit_effective_driver` trong `capit_lever` của golive_v23_status.json, quyết định BYTE-IDENTICAL, quant-skeptic CONFIRMED 576 kịch bản; nay CÓ dòng hiển thị trong plan markdown: "Cổng PIT: Big-4 X% (dùng cho quyết định, ngưỡng 9%) · effective Y% [driver] — chỉ hiển thị", kèm ⚠️ khi effective ≥ 9% mà Big-4 < 9%; follow-up MERGED WC 2026-10-01 18:20, quant-skeptic CONFIRMED 330 kịch bản). **TRIGGER XEM LẠI đổi sang effective** = CCTG có ≥3 tháng dữ liệu + cron tuần chạy ổn, HOẶC effective ≥ ~8% (lúc đó dispatch Taylor đo khoảng cách CCTG−Big-4 lịch sử rồi quant-skeptic + user duyệt riêng). Follow-up XONG 2026-10-01 (WC `358ad369`, mike `8d2aae54`): registry `cctg_rate_vn.md` đã áp (inventory consumer đúng: due_diligence + custom30_yield_labels chạy HẰNG NGÀY, DCF plan-report 21:00 là consumer user-visible), `ops_health_check` 8b WARN khi CSV CCTG hỏng/ngoài khoảng, selfcheck nạp đúng cây worktree.

## Cổng giá trong phiên + cutloss — SHADOW (cron bật 2026-10-06 11:10 ICT, 5 phiên đánh giá)
- `bin/intraday_price_watch.py` (chạy thử, KHÔNG đặt lệnh thật). Tin nhắn dạng **"SHADOW GIỮ/BÁN/BÁN 50% <MÃ>"** trong Trading Daily là lệnh cho script chạy thử — **Mike KHÔNG coi là lệnh giao dịch thật, KHÔNG dispatch Mafee/DollarBill theo dòng đó.** Chỉ hành động khi user nói rõ ngoài tiền tố SHADOW.

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
- **close_repair.py — Layer 2 self-computed back-adjustment khi vendor backfill kẹt vĩnh viễn** (`MIKE_CLOSE_REPAIR` mặc định ON) — LIVE từ **2026-09-28**, commit `3c55c249`. FPT (và mã tương lai cùng lớp lỗi) kẹt hồi tố corp-action NỬA CHỪNG trên `tav2_bq.ticker.Close` — bq_admin xác nhận self-heal vendor đóng băng sau 15 phiên, không bao giờ tự sửa tiếp. Tự tính hệ số (xác nhận 2 nguồn độc lập, lệch <0,006%), fail-closed khi không đủ bằng chứng. 2 vòng quant-skeptic CONFIRMED (vòng 1 điều kiện → 2 test mới lộ 2 bug thật chainffill/selfband → vá → vòng 2 lần 1 NOT_CONFIRMED bắt thêm gap → vá lại → vòng 2 CONFIRMED). Selfcheck trên cây đã merge: `close_repair_selfcheck` 855/855, 14/14 mutation; `paper_entry_adjust --selfcheck` 21/21 cả 3 trạng thái cờ. VND/VNM (Layer 1 detect-only UNCOMPUTABLE) đã điều tra riêng: KHÁC lớp lỗi FPT (VND vô hại/guard quá chặt, VNM là ex-date lệch 1 phiên trong `corporate_action` — `close_repair.py` xác nhận AN TOÀN không áp sai cho ca này, band-guard tự chối đúng).
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
  ⚠️ **CÒN MỞ — 3 file khác nghi cùng lớp bug, CHƯA vá** (Taylor quan sát, arch-reviewer xác nhận 3/3 nhưng lưu ý phạm vi khác nhau): `bin/paper_corp_action_selfcheck.py:28-31` và `bin/send_plan_report_park_jit_selfcheck.py:28-30` cắn **worktree `mike/`**; `bin/due_diligence_corp_flags_selfcheck.py:19-21` cắn **worktree ngoài `mike/`** (repo `WorkingClaude` gốc — `trading_bot/due_diligence.py`), KHÔNG cắn worktree `mike/` vì module đó không tồn tại trong `mike/`. arch-review vòng 4-site (2026-09-24) tìm thêm 1 file: `bin/nav_cum_dividend_selfcheck.py:32-35` (`WC_ROOT` đếm dirname sai trong worktree lồng, **crash** `FileNotFoundError` khi chạy ngoài canonical — CHƯA vá).

- **4 call-site còn lại của lớp lỗi corp-action — audit xong 2026-09-24 (dispatch `Taylor_20260924_064510`), arch-review theo TỪNG VIỆC — CẢ 4 ĐÃ LIVE, ĐÓNG HẲN CHUỖI AUDIT NÀY:**
  · **Việc 4 `report_return_gate.py:558-573` unmatched — APPROVED, LIVE, commit `569be662`.** Tách dòng vị thế CÒN GIỮ bị lệch KL (nghi corp-action credit sớm giữa lúc soạn báo cáo và lúc gate chạy) ra khỏi nhóm "đã thực hiện, ngoài phạm vi" (§29) — trước đây gộp chung, chẩn đoán sai nguyên nhân không kiểm chứng. Chỉ IN cảnh báo riêng, không đổi rc/checked/fails. Selfcheck 99/99 PASS × 8 tổ hợp (python3 + `$DNA_PYEXE` × 4 môi trường). Hồi quy 12 selfcheck liên quan sạch.
  · **Việc 3 `verify_account_snapshot.py:307` `broker_positions_from_raw()` — APPROVED vòng 2, LIVE, commit `96ee1bb8`+`7700582d`.** Giữ `marketPrice` LATEST khác-None (đúng quy ước `DNSEBroker.get_positions()`), docstring đã sửa đúng: vá PHÒNG NGỪA/đồng bộ quy ước, KHÔNG phải fix ca BID 08-14 (0/83 ngày dữ liệu thật đổi hành vi). arch-review vòng 2 xác nhận diff AST-identical sau strip docstring.
  · **Việc 1 `discretionary_accumulation_inject.py` `broker_filled_qty()` — APPROVED vòng 2, LIVE, commit `5e6fb9af`+`642d4f5a`.** Thiết kế lại sau REJECTED vòng 1: cổng quy đổi baseline CHỈ áp cho chế độ `target_qty` cố định (0 chương trình LIVE dùng, giữ làm hạ tầng phòng thủ) — chế độ `target_pct_active_nav` (TV1 SpaceX+ZaloPay, DUY NHẤT LIVE) bỏ QUA HẲN cổng, giữ nguyên `total − baseline` thô vì target tự nhân cùng hệ số sự kiện, TỰ KHỚP. Thêm khoá idempotency `(ticker, ex_date, event_code)` cho chế độ `target_qty`. arch-review vòng 2 tự mô phỏng lại bằng code production: HEAD giữ đúng 5,0000% active_nav; bản REJECTED (v1) overbuy 6,0317%. ⚠️ **Lưu ý docstring**: câu "tự khớp" chỉ ĐÚNG TUYỆT ĐỐI khi `baseline_qty_before_program=0` (đúng cả 2 state LIVE hôm nay) — `baseline>0` thì thiếu `(r−1)×baseline` cp vĩnh viễn, hướng AN TOÀN (mua thiếu, không overbuy), chưa sửa docstring (không chặn).
  · **Việc 2 `discretionary_margin_gate.py` arm_price — APPROVED vòng 12, LIVE, merge `c5247def` (12 commit vòng 3→12, từ `26ef0c58` tới `bc22bed2`).** Mảnh cuối cùng, khó đóng nhất trong cả 4 việc — **12 vòng arch-review độc lập**. Thiết kế lại hoàn toàn từ vòng 2: bỏ `exdate_frame.classify_positions` theo-ngày, đọc THẲNG registry PERSISTENT `data/corp_actions.json` qua `daily_nav_snapshot.confirmed_qty_multiplier_after(ticker, arm_date)`. Từ vòng 3→8, mỗi vòng đóng đúng 1 cửa mới của CÙNG lớp bug §29 ("chẩn đoán không dựa trên bằng chứng đã đọc") rồi lại lộ cửa kế tiếp: JSON-corrupt exception rơi vào nhánh thành công (vòng 3→4), file-missing silent-return làm y hệt (vòng 4→5, vá bằng `os.path.exists()`), record hỏng bên trong file hợp lệ + so sánh ngày bằng CHUỖI THÔ khiến 1 sự kiện thật (TRC 09-15, 9 ngày trước lúc vá) — hoặc hệ số phi lý — bị NUỐT ÂM THẦM (vòng 6→7, vá bằng `corp_actions.validate()` dùng chung cho cả điểm đọc VÀ điểm ghi); `nan`/hệ số phi lý lọt qua guard `<=1.0` (so sánh nan luôn False) khiến breach thật −42,3% báo thành "OK" (vòng 7, `math.isfinite` + `QTY_MULT_MAX`) — **biên đầu tiên chọn 2.0 SAI, tự query BQ xác nhận sẽ chặn oan sự kiện thật (TRC/DGC/F88), sửa về 10.0 khớp bất biến đã có sẵn** (vòng 8). Vòng 8 xác nhận **logic số học ĐÚNG bằng BigQuery thật** — vòng 9→12 thuần về lớp DELIVERY: cảnh báo −20% bắt buộc de-lever phải THẬT SỰ tới người khi bus/Discord có thể chết độc lập (không phải `elif` loại trừ lẫn nhau khi vừa có breach vừa có lỗi cùng lượt — vòng 9→10), guard `and` không bị làm loãng thành `or` (vòng 10→11→12), escalation message không bao giờ khẳng định điều chưa đọc được bằng chứng (record cũ/mới, `bad_idx=None` — vòng 9→10), và Discord không báo "✅ AUTO-CONFIRMED" cho 1 ghi chưa từng xảy ra (vòng 9→10, `pending_bus_posts` dời post-write). Vòng 12: test-only, đóng 2 gap pinning cuối, vòng 11 xác nhận KHÔNG còn lỗi hành vi. Selfcheck cuối 146/146 qua ≥4 môi trường + 2 interpreter (`python3`/`$DNA_PYEXE`); hồi quy 15+ selfcheck corp-action liên quan + `report_return_gate --selfcheck` sạch mọi vòng. `data/discretionary_margin_arms.json` không tồn tại (0 arm sống thật) ⇒ latent — đã vá xong TRƯỚC khi có arm đầu tiên, đúng như yêu cầu ban đầu.
  ⚠️ **Sự cố phụ phát sinh khi verify vòng 5** (không liên quan code, Mike tự gây ra): 1 script test đầu tiên quên override `gate.ARMS_PATH` trước khi gọi `save_arms()`, ghi lọt 1 arm giả (`ticker=VPB, note="seed"`) vào LIVE canonical `data/discretionary_margin_arms.json`. Phát hiện bởi arch-review vòng 6 (B5). Mike cố tự dọn (ghi `[]`) nhưng bị Bash/Write safety classifier chặn (đúng — file thuộc phạm vi dữ liệu sống ngoài worktree) — **CẦN USER TỰ DỌN hoặc cấp quyền**, xem tin nhắn Discord thread này ~17:53 ICT 2026-09-24. Không khẩn cấp (cron kế tiếp 15:20 ICT thứ Sáu 25/09) nhưng cần xử trước phiên đó — arm giả thiếu key `exit_alerts`/`exited` từng gây `KeyError` giết cả lượt check-exits trước khi vòng 11/12 vá phòng ngừa (`setdefault`).

## R&D pipeline — PAPER-ONLY, chi tiết `kb/projects/rnd-pipeline-tracker.md`
Fear-buy quét hàng tuần `bin/fearbuy_weekly_scan.sh` (Friday 08:10 ICT). Recon thuần, KHÔNG tự mua.

## Measurement integrity audit — cadence định kỳ (mở 2026-09-27, sau retro custom30V double-count)
Lý do: bug custom30V double-count (`mcap = Close_adj × OShares`, −4,48pp CAGR) sống trong
production nhiều tháng, KHÔNG bị bắt bởi self-check 0 VND (kiểm sổ sách mô phỏng, không kiểm
tính đúng kinh tế của công thức) LẪN quant-skeptic (7 đòn cũ nhắm overfit/gaming, không nhắm lỗi
kế toán double-count). Chỉ lộ ra vì có audit CHỦ ĐỘNG quét 23 chuỗi return/level/weight/NAV theo
6 bất biến cố định — audit đó còn tìm thêm 7 bug không liên quan (FAIL-C/F/H, egg reconcile,
FAIL-G ICB routing, DSR/PBO family drift). Kết luận: không đợi ai đó thấy số lạ mới đi tìm.
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

## Tri thức chung của đội (canonical — Mike biên tập; MỌI agent phải nắm)
> Cập nhật 2026-07-30. Chi tiết: `kb/KNOWLEDGE.md`. Số liệu gốc: `data/results_registry.md`.
> Codebase: `/home/trido/thanhdt/WorkingClaude` (BigQuery `tav2_bq`).
> **Mục tiêu**: vận hành chiến lược **production V2.4**, **live từ 2026-07-01**, tài khoản SpaceX (DNSE), 1B VND.

### V2.4 — chiến lược trung tâm (đã verify, self-check 0 VND, threads=1)
- = **V2.3A + custom30V parking (NEUTRAL) + gated-overflow (bear-washout) + HAG eq_flag fix**.
- 2 book: **BAL** (momentum SIGNAL_V11, yieldcombo: 1/PE + 1/PCF) + **LAG** (PEAD/earnings drift).
- Allocator w_LAG: {CRISIS 50 / BEAR 0 / NEUTRAL-BULL-EXBULL 65}, band ±10pp.
- 🆕 **PIN DẢI 2 SỐ — user chốt 2026-09-28 08:02 ICT** (registry mục **"2026-09-28 (septies)"**):
  R3 @park 0,30 = **23,37% (`pin0%`, NGƯỠNG SÀN — tiền nhàn rỗi 0%/năm) … 25,71% (`pin1M`, NGƯỠNG
  TRẦN — lãi huy động 1 tháng Big-4 cá nhân PIT trả cho MỌI tiền nhàn rỗi)**. **CẢ HAI là số pin
  chính thức, không cái nào SUPERSEDE cái nào; CẤM trích 1 số mà không kèm quy ước.** Chênh
  +2,34pp trong đó **2,05pp (87,8%) là SỐ HỌC TRỰC TIẾP** (tiền nhàn rỗi 46,4% NAV, trước trả 0%
  nay ~3,5%/năm), chỉ 0,285pp là đường giao dịch — DƯỚI sàn nhiễu W2b 0,46pp ⇒ **KHÔNG đọc là
  "hệ tốt lên"**, đây là đổi thước đo áp đều mọi phương tiện. Quy đổi thực tế ~21,9% … ~24,2%.
  ⚠️ **Neo sizing DD vẫn lấy đầu SÀN −25,2%** (KHÔNG lấy −23,6% của đầu trần) — sizing đứng ở cận
  xấu, neo thực tế KHÔNG đổi. Điểm THẬN TRỌNG trong dải = chân `dep1m_21s` FIFO = **25,24%** /
  Sharpe 2,03 / MaxDD −14,4% / Calmar 1,75 (LIFO 24,95% độ nhạy; engine KHÔNG xếp hạng được
  fifo/lifo — chênh 0,289pp dưới sàn nhiễu). quant-skeptic **CONFIRMED (medium)** 2026-09-28,
  8/8 check. ⚠️ **KHÔNG gọi là "điểm thực tế"**: lập luận "không truy lĩnh vì truy lĩnh = nhìn
  trước" SAI — trả lãi tại phiên 22 cho kỳ hạn đã đi hết là NHÂN QUẢ, nên engine TRẢ THIẾU 1-21
  ngày mỗi lô đáo hạn ⇒ số trung thực nằm strictly trong (25,24%; 25,71%). ⚠️ Phần ĐƯỜNG ĐI của
  chân này = 0,758pp = **1,6× sàn nhiễu 0,46pp** ⇒ điểm giữa KÉM CHẮC hơn hai đầu dải, đọc là
  "gần đầu trần" chứ không phải một con số chính xác.
  ✅ **Chân TRẢ KHI ĐÁO HẠN = điểm TRUNG THỰC của luật user = 25,34%** (FIFO; LIFO 25,42%), nằm
  strictly trong dải, quant-skeptic **CONFIRMED (high)** 2026-09-28 06:11Z 8/8. Chênh với 25,24%
  chỉ **+0,10pp = 1/5 sàn nhiễu** ⇒ **GIỮ 25,24% làm số chính, KHÔNG re-pin** (cận dưới đã verify,
  sizing đứng cận xấu). ⚠️ Đổi sang quy ước đúng làm SỐ HỌC tăng (+1,116→+1,520pp) nhưng ĐƯỜNG ĐI
  GIẢM (+0,758→**+0,448pp, DƯỚI sàn nhiễu**) ⇒ **cảnh báo "1,6× sàn nhiễu" KHÔNG áp dụng cho chân
  maturity**. ✅ **min_age là CAO NGUYÊN**: 20/21/22/23 = 25,35/25,24/25,22/25,21 — biên độ toàn
  dải 0,14pp = 30% sàn nhiễu ⇒ pin KHÔNG nhạy tham số (KHÔNG chứng minh 21 tối ưu, chỉ chứng minh
  chọn trong 20-23 không quan trọng). Chi tiết: registry §4b + §4c.
  quant-skeptic **CONFIRMED (high)** 2026-09-27 18:18Z, 8/8 check. ⚠️ Giới hạn của `pin1M`:
  53/150 tháng là SỐ DỰNG LẠI (FiinPro không có dữ liệu ≤2018-12, cầu = NHNN 12M-thấp −2,525pp);
  upstream FiinPro-X **đã hết hạn 28/09/2026**; đây là lãi thị trường, không phải carry egg DNSE.
- **R3 NEUTRAL-only @50B: CAGR 23.37% / Sharpe 1.88 / DD −14.6% / Calmar 1.60** = **`pin0%` (đầu SÀN của dải)** — pin CHÍNH THỨC từ
  **2026-09-27 (sexies)**, Final NAV 684,52B, ledger md5 `4707bcbe…`, IS 20,00% / OOS 26,50%,
  self-check 0 VND. **Số SẠCH đầu tiên trên CẢ HAI chiều**: nhãn edge-health causal (`known_date`,
  FAIL-C đã đóng) **và** đúng knob park live 0,30. Neo sizing DD (bootstrap 5th) = **−25,2%**;
  DSR 1,0000 · PBO(68) 0,2085.
  *~~23,43% / 1,88 / −14,4% / 1,63 / 688,77B (pin quinquies)~~ SUPERSEDED làm anchor 2026-09-27* —
  lý do: đo trên nhãn LOOK-AHEAD 25 phiên (`label_col=entry`), KHÔNG phải sai mô hình/sai knob;
  Δ gỡ look-ahead = −0,06pp CAGR. **Pin = `PARK_STATES=3:0.3` = ĐÚNG knob live** (user chốt park 30% lúc 15:48 ICT
  2026-09-27, `ae81bd47` đổi `trading_rules.json` + `ETF_PARK`); ledger byte-identical với leg lưới
  `parkgrid_030` ⇒ lệch 0,00pp. Neo sizing DD mới = **−25,2%** (bootstrap 5th-pct, nhãn as-of; @nhãn cũ −25,1% — neo thực tế không đổi).
  🚨 **ĐÍNH CHÍNH — pin cũ 24,42% mang nhãn "(production)" SAI**: production THẬT từ 2026-08-04 là
  park **0,8** (= 24,95% / 1,66 / −19,8% / 1,26, chưa từng được pin), trong khi registry pin
  `PARK_STATES=3:0.7` ⇒ **số pin lệch knob live suốt 54 ngày** (cùng lớp lỗi `LAG_ADV_BASIS` 08-03).
  24,42% và 24,95% GIỮ làm lịch sử, **không còn là anchor**.
  ✅ **Ba rail park ĐÃ ĐỒNG BỘ = 0,30** (commit mike `1f15139b`): R1 MUA `ETF_PARK={3:0.30}`, R2 BÁN `compute_park_trim.py PARK_TARGET_F1 = 0.30`, R3 policy `trading_rules.json` 0.30. Trước đó R2 còn hardcode 0,80 ⇒ bot MUA tới 30% nhưng chỉ TRIM khi vượt 80%, knob user chốt KHÔNG hiệu lực (đúng lớp lỗi im lặng 08-04, đảo chiều). Cổng cơ học `bin/park_rail_consistency_selfcheck.py` đọc giá trị 3 rail bằng AST, rc=1 khi lệch — live rc=0, selftest 6/6. ⚠️ R3 vẫn CHƯA có code path nào đọc (văn bản chính sách); việc wire R2 đọc R3 chờ arch-review.
  Nguồn: `data/results_registry.md` mục "2026-09-27 (quinquies)".
  *Bối cảnh bản 24,42% (lịch sử):* (Final NAV 761,11B, ledger md5 `2f9c3702…`; SUPERSEDE 24,38%/757,61B của
  sáng cùng ngày — chênh +0,04pp do ticket 1 "OShares bước tại EX-DATE" ở chân weight, merge `5c290848`), đo trên **`universe_pit`** (point-in-time, không look-ahead).
  ⚠️ **SỬA LỖI ĐO 2026-09-27, KHÔNG ĐỔI MÔ HÌNH** — không tune tham số nào, chân weight + membership
  byte-identical, đường tiền live không đụng. Chuỗi return rổ park custom30V từng chain trên
  `mcap = Close_adj × OShares`, nên mỗi bước số CP theo QUÝ thành một ngày return GIẢ trong khi
  `Close` đã điều chỉnh hồi tố cho cùng sự kiện ⇒ đếm hai lần. Gỡ ra = **−4,48pp**. Tái lập trên
  main: md5 `3f836927`, self-check 0 VND. Knob lùi `BASKET_RETURN_OSHARES=legacy`.
  **Số cũ 28.86% / 1.90 / −17.8% / 1.62 / 1.178,01B (pin 08-03) SUPERSEDED** — giữ làm lịch sử.
  ⇒ **V2.4 không còn là hệ ~29% CAGR; ở park 0,30 (production hiện hành) là ~23,4%** (quy đổi thực tế
  ≈ 21,9%); ~24,4% là bản @park 0,7 đã SUPERSEDED.
  Phần diễn giải `LAG_ADV_BASIS` dưới đây vẫn còn hiệu lực (nó nói về VÌ SAO mặc định là `price`):
  ⚠️ **KHÔNG phải "hệ tốt lên"** — KHÔNG có thay đổi mô hình nào. Đây là **đồng bộ registry theo
  code production**: mặc định `LAG_ADV_BASIS` (cơ sở giá của ADV book LAG) đã đổi `close`→`price`
  ngày 08-02 (commit `0062aa0`, để gỡ look-ahead + giữ bất biến "trần live == trần đã mô phỏng")
  nên số pin cũ không còn tái lập được bằng lệnh pin trên code hôm nay. Chân control (`close`) tái
  lập 27.24% TUYỆT ĐỐI cả 5 chỉ tiêu + cả 2 số IS/OOS ⇒ A/B hợp lệ. **Toàn bộ chênh nằm ở IS
  (+3,28pp), OOS chỉ +0,02pp** — hệ số `Close/Price` hội tụ về 1,00 gần đây nên chỉ khác ở nửa đầu
  mẫu; **KHÔNG trích +1,62pp như "edge mới"**. Chi tiết ở `data/results_registry.md` (mục
  **2026-08-03 RE-PIN R3 THEO ĐÚNG MẶC ĐỊNH PRODUCTION `LAG_ADV_BASIS=price`**), KHÔNG lặp lại ở đây.
  **Số lịch sử KHÁC VINTAGE / KHÁC CƠ SỞ / CÓ LỖI, không so trực tiếp**: 27.24%/1.81/−18.4%/1.48
  (pin 08-02, cơ sở ADV `close` — đúng với cơ sở đó, đã SUPERSEDED); 27.60%/1.84/−17.5%/1.58 (pin
  07-29, có look-ahead cơ sở giá rổ); 27.16%/1.81/−18.1%/1.50 (pin 07-22, đã mất, không tái lập
  được); 27.84%/1.84/−18.2%/1.53 (pin 07-12, `ticker_prune`).
  ⚠️ **MIXED-universe khi trích dẫn**: `universe_pit` cho cổng quyết định, `ticker_prune` vẫn cho
  CAPIT pool/maturity. Lỗi fidelity `liq<=0` — **cơ chế nay đã tách được (T1-T5, job
  `Taylor_20260803_021414`/`_045138`, quant-skeptic CONFIRMED cao)**: giả thuyết "hiện vật sức
  chứa" BỊ BÁC BỎ hai lần bằng hai knob trực giao (`%ADV/ngày` và NAV), cả hai lần bằng SAI DẤU
  đạo hàm — không phải "chưa loại trừ được". Nhưng **MỨC thì KHÔNG tách được**: cả hai chân đứng
  trên 1 tham số mô hình fill (trần 20% ADV/phiên) mà 90-96% số phiên-fill sống Ở TRẦN đó, trong
  khi fill THẬT (DNSE) mới chỉ xác nhận tới ~3,86% ADV/phiên — 2 thiên lệch NGƯỢC CHIỀU cùng bậc
  độ lớn (+4,08pp do sửa đúng nhóm mã không mua được vs. −4,0..4,5pp do giả định fill quá lỏng)
  gần **triệt tiêu nhau**. ⇒ **24,42% (cũ: 28,86%) ĐỌC LÀ ƯỚC LƯỢNG ĐIỂM có điều kiện vào 1 tham số chưa neo**,
  KHÔNG PHẢI cận dưới, không phải cận trên (đổi nhãn 2026-08-03, thay khoảng `[~27,2%;~31,3%]`
  đã hết hiệu lực) — **không trích +3,85pp/+4,08pp/+4,11pp như edge đã kiểm chứng** ở bất kỳ
  chiều nào. Follow-up 08-04 (gate động theo executability thật) củng cố thêm: giải quyết được
  vấn đề cơ học (vị thế kẹt 35%→0%) nhưng KHÔNG cho lợi nhuận bền (đổi dấu khi bỏ 2020-2021,
  PBO cao) — cùng chữ ký reshuffle-luck. Đóng hẳn câu hỏi CHỈ bằng tích luỹ fill thật, không
  bằng backtest thêm — sổ theo dõi + **mốc cứng 2026-12-15 / 2027-03-31**:
  `kb/projects/lag-adv-filter-tracking.md`, chi tiết cơ chế: `agents/Taylor/research/
  lag_fidelity_decomp_20260803/T5_DECISION.md`.
- Bootstrap 5th-pct: **CAGR 15.6%, DD −25.1% (neo sizing DD −25,1%, KHÔNG phải −14,4%)** — trên
  ledger pin **park 0,30** (2026-09-27 quinquies); P(DD<−30%)=**1,0%**, P(SR<1,0)=1,0%; stationary
  15,4% / −24,8%. *Bản @park 0,7 SUPERSEDED: 15,5% / −30,3%; @park 0,8: DD 5th −32,0%.*
  Ghi chú cách chạy (không đổi) của bản @0,7: **theo LỊCH** (FAIL-F đã merge `3c944443`; cơ sở phiên cũ
  thổi cao giả ~+0,2-0,3pp). `bootstrap_nav.py` L=21/B=4000/seed 12345; P(DD<−30%)=5,5%,
  P(SR<1,0)=3,4%; stationary-bootstrap cross-check 15,3% / −30,0%.
  *Chuỗi số cũ SUPERSEDED: 18,6%/−28,6% (06-29) → 15,6% (cơ sở phiên) → 15,4% → **15,5%/−30,3%**.*
- **DSR/PBO đã hết trôi — họ trial nay GHIM bằng `DSR_FAMILY_MANIFEST`** (merge `f2cfb124`):
  **DSR 1,0000** (ann-SR R3 **1,815** trên ledger pin park 0,30; 1,616 ở bản @0,7). **Số pin của V2.4 là PBO = 0,2085** (chạy lại trên ledger pin park 0,30 — **không đổi**, vì CSCV
  đo trên HỌ TRIAL, ledger R3 không thuộc họ) trên họ gốc phục dựng
  68 file (`mike/research/dsr_family_manifest_20260927/man_2026_07_recon.json`, md5 `2cea9626…`) —
  khớp 0,2088 pin từ 2026-07 ⇒ phục dựng đúng. ⚠️ caveat: registry 2026-07 không lưu tên file,
  68 file này dựng lại theo `mtime`, không phải danh sách gốc.
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
- ✅ **FAIL-C ĐÓNG 2026-09-27**: CSV sinh lại có `known_date`, `asof_label_selfcheck.py` PASS 0 vi
  phạm (bản cũ FAIL 5.488/5.488, sớm 25 phiên), Δ pin = **−0,06pp CAGR / −0,2pp MaxDD / −0,03
  Calmar / −4,25B NAV** (A/B một biến, chân control byte-identical với pin ⇒ Δ đọc được). Anchor R3
  đổi 23,43% → **23,37%**; xem registry mục "2026-09-27 (sexies)". Tồn dư KHÔNG gấp, không ảnh
  hưởng số: đường LIVE `golive_recommend_v23.py:293` và `edge_health_monitor.py:188` (`neg_streak`)
  vẫn index trên `entry` — benign hôm nay (live luôn lấy dòng cuối ⇒ cùng `w_LAG=0,50`), nhưng
  `neg_streak` chạm ngưỡng sớm ~1,2 tháng.
  2026-09-27 trên ledger pin mới (`bootstrap_nav.py`, L=21/B=4000/seed 12345); stationary-bootstrap
  cross-check 15.5% / −30.1%. ⚠️ **Annualize theo LỊCH (FAIL-F, sửa 2026-09-27 job Taylor_20260927_045241, branch `fix/nav-flow-term-annualize` CHƯA merge)**: bootstrap 5th-pct CAGR theo lịch = **15,4%** (theo phiên 15,6% — cao giả +0,18pp), Sharpe R3 1,61 (hiển thị 1,62); MaxDD −30,4% / P(DD<−30%) 5,35% KHÔNG đổi; **DSR và PBO KHÔNG phụ thuộc annualize** (đính chính framing audit). ⚠️ PBO đo ở 2 cây khác nhau cho **0,40 (main) vs 0,50 (worktree)** vì họ trial là glob động ⇒ PBO KHÔNG có nghĩa cho tới khi pin `family_manifest`. *Số cũ 18.6% / −28.6% SUPERSEDED (bản chạy 06-29, pin khác).*
- **NEUTRAL parking custom30V @0,30 (production) = +1.06pp CAGR** (23.43% vs 22.37% park=0) — và ở
  30% parking làm **TỐT hơn** rủi ro: DD −16,1%→−14,4%, Calmar 1,39→**1,63**, Sharpe 1,95→1,88.
  ⚠️ 0,30 vs 0,0 **không phân biệt được bằng dữ liệu** (paired block bootstrap P=0,479) ⇒ 0,30 là
  sở thích rủi ro user chốt, không phải mức thắng có ý nghĩa thống kê.
  *Bản @park 0,7 (SUPERSEDED làm production, giữ lịch sử):* **+2.05pp CAGR** (24.42% có park vs 22.37% park=0, cùng lệnh pin,
  đổi đúng 1 biến `PARK_STATES`; 30 mã, cap 0.10). ⚠️ **"+7.4pp Full" SUPERSEDED** — lệnh gốc của số
  đó không tồn tại trong registry; ở chân return LỖI delta là +6,49pp ⇒ **~2/3 của "+7,4pp" là return
  giả từ tăng trưởng số CP.** ⚠️ **Và chiều rủi ro ĐẢO DẤU**: parking làm Sharpe 1.95→1.69,
  DD −16.1%→−18.8%, Calmar 1.39→1.30. Ở pin mới parking **mua ~2pp CAGR bằng cách làm xấu mọi chỉ
  tiêu risk-adjusted** ⇒ câu "phần tin cậy nhất" KHÔNG còn đứng trên cơ sở risk-adjusted. Giữ/bỏ
  parking là **quyết định của user**, Taylor không tự đảo.
- Bull parking: NAV ≥150B. **(30, 0.15) = OVERFIT**, walk-forward bác.
- **V2.5** (future) = V2.4 + lever MGE=1.5, account sẵn sàng, DISABLED, reminder 2026-07-07.

### ⚠️ `*_screen.py` — "8L top-25" TRƯỚC 2026-09-27 là 25 mã XẤU NHẤT (đã vá, nhưng số cũ HẾT HIỆU LỰC)

**Lỗi**: `sort_values([rating, tv], ascending=False).head(25)` rồi gọi kết quả là "8L top-25".
`fa_ratings_8l.rating` là thang **1-5 kiểu xếp hạng tín nhiệm — 1 = AAA = TỐT NHẤT** (cổng
production là `rating<=3`), nên `ascending=False` lấy đúng nhóm rating **xấu nhất**. Lặp ở
**16/20 file**; sửa = `ascending=[True, False]` (tie-break thanh khoản giảm dần vốn đã ĐÚNG).
Merge `ec9750f2` (user duyệt 19:25 ICT 2026-09-27); selfcheck `screen_sort_direction_selfcheck.py`
bằng **AST** — 20 file · 107 lệnh sort · 0 vi phạm · 0 mơ hồ, giống nhau trên 4 môi trường TZ,
**7/7 mutation bị giết**, và chạy trên bản CHƯA sửa ra đúng 16 vi phạm ⇒ bắt bug thật, không tautology.

**Mức độ sai**: 146 kỳ rebal 2014-08→2026-09 — rating trung bình rổ **4,504 → 1,252**;
**145/146 kỳ hai rổ RỜI NHAU HOÀN TOÀN** (overlap 0,01/25); số kỳ rổ **không có mã nào `rating<=3`**:
**145/146 → 0**. Ví dụ 2026-09-25: bản cũ chọn rổ `rating {4:15, 5:10}` — **có cả NVL và HAG là
BANNED vĩnh viễn**; bản sửa chọn `rating {1:8, 2:17}` (ACB CTG FPT GAS MBB VCB VNM…).

🔴 **HỆ QUẢ NGHIÊN CỨU — đừng trích số cũ nữa**: **7/9 screen từng được báo là TRỰC GIAO với
8L top-25 (0-5%) thật ra TRÙNG 21-83%** (bank_compounder 4,9→64,1% · tech G_VN 0,0→83,3% ·
pharma 0,0→69,0% · aviation INFRA 0,0→53,4% · logistics PORT 0,0→37,1% · compounder 4,0→25,8% ·
retail_compounder 0,0→21,1%). ⇒ **kết luận "sleeve này bổ sung alpha mới, không lặp 8L" KHÔNG
còn suy được từ những con số cũ.** Muốn kết luận lại thì phải đo lại, không phải đọc lại.

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
   DSR/PBO — **cập nhật 2026-09-27: DSR 1.0000 (vẫn ≥0.95), PBO 0.3993 (cũ 0.2088)**. PBO tăng
   KHÔNG do bug return mà do HỌ TRIAL nở **80 → 477 CSV** (`family_paths()` là glob động ⇒ mỗi
   backtest R&D mới tự nhập họ). ⇒ **PBO đã pin KHÔNG tái lập được theo thời gian**; muốn so sánh
   được phải pin danh sách file (`family_manifest`) — CHƯA LÀM. Nguồn: `data/results_registry.md`
   mục "DSR / PBO Robustness Annex" + "2026-09-27 (bis) HẬU KIỂM SAU MERGE `a808a613`".

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
- **KHÔNG có bằng chứng trục này tách tín hiệu.** 08-22: **0/27 ô** qua BH FDR 10% (radar: 0/24 —
  hai trục HOÀ). Chính báo cáo gốc §7 viết **"KHÔNG wire"** và §6.3 "tốt hơn để **MÔ TẢ**, không
  phải để wire". Job E 2026-09-27 đo lại bằng thước khác (IC cross-sectional momentum/value) trên
  **12,6 năm** (IS 72 tháng / OOS 80 tháng): **0/4** — `ic_mom` đảo dấu IS +0,057 → OOS −0,038;
  `ic_ey` từ −0,082 (p_BH 0,0030, CI loại 0, đơn điệu) về +0,003 (p 0,886) = **artifact IS**.
  Không phải lỗi cửa sổ ngắn: hỏng y hệt trên cửa sổ dài gấp 1,6×.
- ⇒ Dùng để **MÔ TẢ / phân tầng mẫu**. **Đừng suy ra tín hiệu từ nhãn ô**, đừng coi "trục mặc
  định" là "trục có thông tin". (H5 2026-09-26 đã đọc quá nghĩa đúng theo hướng này rồi báo
  "trục mặc định trượt 4/4" — nó trượt một tiêu chí 08-22 chưa bao giờ tuyên bố đạt.)
- **Không trục nào khác qua được cùng chuẩn**: job E so 3 trục cùng khuôn (breadth / retail_net_share
  / DT5G state) = **0/12**. `retail_net_share` giữ được cùng dấu IS&OOS nhưng IS chỉ 9/7/5 tháng và
  **nguồn chết 28/09/2026** ⇒ không phải ứng viên thay thế.

Lý do (nguyên văn 08-22, vẫn đúng — tái lập CHÍNH XÁC 2026-09-27):
- Value Radar zone ≈ kỷ nguyên: 54% số năm bị 1 nhãn chiếm ≥90% phiên → n_effective ~2-3 chu kỳ, không bao giờ đủ sức thống kê
- Breadth-tercile PIT: **0%** năm bị 1 nhãn chiếm ≥90%; **2,0×** số episode so với radar (262 vs 131)

Cách tính breadth chuẩn — **định nghĩa đầy đủ, 3 chi tiết dưới đây từng làm tái lập lệch**:
- Nguồn: `tav2_mike.universe_pit` (CANONICAL)
- breadth_t = COUNT(Close_t > MA200_t | in_universe=True) / COUNT(in_universe=True)
  **Mẫu số chỉ đếm mã có `MA200` KHÔNG NULL.** Tính từ `data/bq_cache/ticker` mà không lọc
  `MA200 IS NOT NULL` → breadth 2016 ra **0,243 thay vì 0,730** (`bq-cache` registry, bẫy MA200 NULL
  2015-2017). Lọc đúng: corr 0,999954 với chuỗi gốc.
- Phân loại phiên t: dùng breadth_{t-1} (PIT, không look-ahead cùng phiên).
  ⚠️ **Đây KHÔNG phải biến thể sinh ra bảng §4 của báo cáo gốc** — bảng đó dùng breadth CÙNG PHIÊN
  (look-ahead corr **+0,109**, báo cáo tự thừa nhận) và §5a của chính nó cho thấy **trễ 1 phiên là
  mất tính đơn điệu**. Hai chuỗi cho số khác nhau đáng kể (ô HIGH excess **+5,5pp vs +16,6pp**, thứ
  tự tercile ĐẢO). Trích số 08-22 thì phải nói rõ biến thể nào.
- Tercile: phân vị rolling **252 phiên trước** (không phân vị toàn mẫu). Quy ước tie của bản gốc:
  `(# trong 252 phiên trước < breadth_t) / 253` — 4 quy ước hợp lý khác cho LOW 1.224-1.226 thay vì
  **1.232**. Và `pd.cut([0,1/3,2/3,1])` **ném mất `pct==0,0`** (63 phiên breadth thấp nhất lịch sử,
  tức các phiên VNI xấu nhất) ⇒ excess ô LOW tụt +27,4pp → +14,7pp. Dùng ngưỡng tường minh.

Value Radar vẫn giữ vai trò DISPLAY-ONLY trong báo cáo (§6b coding_guidelines). Không wire vào sizing.

Kết quả dẫn tới quyết định: breadth-vs-radar-matrix-20260822 (Taylor, B2) + user confirm 2026-08-22.
Tái kiểm + ranh giới hiệu lực: `agents/Taylor/research/breadth_tercile_recheck_20260927/report.md`
(bus `finding:breadth-tercile-08-22-recheck`, verdict **A — quy ước ĐỨNG, không đổi trục**).

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
(`expected_exdate_adjustment` trong `daily_nav_snapshot.py`, selfcheck 29/29) bị arch-review vòng 2
trả NEEDS_CHANGES và đã được GỠ khỏi cây làm việc, cất ở
`agents/Wags/research/nav_exdate_xcheck_wip_20260912.patch`. Lý do đáng nhớ: cổng ghép cặp của nó
kiểm PROXY (`cum_div["warnings"]`) chứ không kiểm BẤT BIẾN "khoản cổ tức phải thu của chính mã được
miễn đã bị trừ khỏi tiền" — mà `cum_dividend_double_count` có nhánh `delta<=0` trả `amount=0,
warnings=[]` IM LẶNG (đo thật `--date 2026-09-12`: 80 triệu vẫn nằm trong `totalCash`) ⇒ nới cổng
trong trạng thái đó sẽ đếm 2 lần đúng 80 triệu (+8,15% NAV, lọt cổng sanity ±15%) và ghi thẳng vào
`nav_history`. Nghĩa là: **tự động hoá SAI ở đây còn tệ hơn tự tay xử lý mỗi quý vài lần.**
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

## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`
<!-- Rút gọn 2026-08-10: mỗi dòng trước đây là 2-4 câu kể lại diễn biến. File này bơm vào MỌI
     dispatch có context_pack ⇒ tường thuật của việc ĐÃ ĐÓNG là chi phí trả lại mỗi phiên.
     Giữ đúng phần còn quyết định được hành vi sau này: TÊN · FILE · PHÁN QUYẾT (nhất là NO-GO,
     để không ai đề xuất lại). Diễn biến vẫn nguyên trong file chi tiết. -->
- 2026-09-07 Treasury-buyback OShares PIT overlay (VRE vs AIS gap) → `treasury-buyback-oshares-overlay-20260907.md` — **KHÔNG WIRE** (user chốt 09-08): overlay CONFIRMED 2 vòng quant-skeptic (162/14/29 mã), nhưng OShares chỉ nuôi 1/3 nhánh composite (sales_yield, không phải PE dominant factor), vấn đề chỉ ở cửa sổ lịch sử đã tự hết (live OShares đã đúng) — giữ làm công cụ tra cứu ad-hoc
- 2026-08-23 Chính sách margin đơn mã sleeve fear-buy discretionary → `discretionary-margin-policy-20260823.md` — **IMPLEMENTED 2026-08-29, cap RESYNC 2026-08-30 (commit a19fc256/022c48e7)**: per-name ≤5% NAV exposure, sleeve tổng ≤10% NAV exposure (f≤1,3, %ADV≤10%, exit tự áp −20% từ giá arm); gate `bin/discretionary_margin_gate.py` + cron check-exits 15:20 ICT; trigger 15% cần ≥3 case marginable đồng thời THẬT — chưa đạt
- 2026-08-23 Margin theo khoảng cách định giá + nhận diện đáy 11/2022 → `margin-valuation-spread-20260823.md` — **NO-GO** mọi cơ chế sizing/gate mới (5 vòng, Phase 1 engine quant-skeptic CONFIRMED high); `capit_margin_lever` dd52≤−20% GIỮ NGUYÊN; nhiễu harness 0,385pp ≫ hiệu ứng 0,009pp; đóng tập 7 episode, chỉ còn shadow-log spread EOD; hướng mở duy nhất = margin cấp CỔ PHIẾU trong sleeve fear-buy. **Đính chính 08-24**: thiếu trục "phòng thủ có mục tiêu" (2020/2022, dễ hồi) vs "cơ cấu tự cộng dồn" (2007-2012, không xử lý nhanh được) — 3/7 episode rất có thể là 3 sóng của 1 khủng hoảng, N độc lập thật ~4-5 không phải 7; không đổi verdict NO-GO, chỉ đổi cách đọc "phản ví dụ" 2010-08-25
- 2026-08-13→14 corporate_action BQ integration + paper-report bug fix → `corporate-action-bq-integration-0813.md` — XONG, Việc A/B wire an toàn (6 vòng), SANITY_FACTOR WARN phương án C wire+CONFIRMED 08-14 (1 gap coverage nhẹ còn mở), vòng 6 rc=1/KeyError chủ động bỏ qua
- 2026-07-31 CAPIT sizing bug 07-21 → `capit-sizing-bug-0721.md` — ĐÓNG, đã fix; user chốt KHÔNG bù phần thiếu
- 2026-07-28 DGC + TV1 fear-buy due-diligence → `dgc-tv1-fearbuy-discretionary.md` — XONG, cả 2 QUALIFIED, theo dõi discretionary riêng
- 2026-07-21 LAG 07-24 (IVS/TMG/TRC) → `lag-0724-ivs-tmg-trc.md` — XONG, gate %ADV + lọc thanh khoản LAG đã wire
- 2026-07-20 Deposit-rate auto-crosscheck → `deposit-rate-autocheck.md` — XONG, tự động, không cần người
- 2026-07-17 DCF upgrade → `dcf-earning-power-upgrade.md` — earning-power **NO-GO** (giữ FCFE); refresh-gate cron LIVE
- 2026-07-13 World Cup + rổ lãi suất huy động → `wc-deposit-rate-gate.md` — **NO-GO** cả 2 hướng, N quá mỏng
- 2026-07-13 Plan-approval gate → `plan-approval-gate.md` — XONG, re-send 23:00 + code-gate `bot_execute.py`
- 2026-07-13 Plan ZaloPay transition 5/5 → `zalopay-transition-0713.md` — XONG
- 2026-07-13 DT5G BULL-giả → audit freshness → `dt5g-bull-fake-freshness-audit.md` — KHÉP KÍN, live không sai
- 2026-07-13 Báo cáo tuần 07-06→07-10 → `weekly-report-mechanism.md` — XONG, có WARN quá hạn
- 2026-07-13 Audit dữ liệu 8L (BCTC Q2) → `8l-data-audit.md` — XONG
- 2026-07-12 lag_edge_health.csv staleness → `lag-edge-health-staleness.md` — KHÔNG phải bug; check lại ~08-25
- 2026-07-12 fa_ratings/8L → `fa-ratings-rebuild.md` — re-tune 8L **NO-GO**; rebuild builder XONG
- 2026-07-12 V2.5 leverage → `v2.5-leverage-nogo.md` — **NO-GO**, giữ DISABLED (edge là IS-artifact)
- 2026-07-12 LAG-weight (tăng tỷ trọng PEAD) → `lag-weight.md` — ĐÓNG, KHÔNG tăng trần w_LAG
- 2026-07-12 Momentum-deals (MOM_N/MOM_S) → `momentum-deals.md` — KHÉP KÍN, production LIVE
- 2026-07-12 Q-sleeve → `q-sleeve.md` — **NO-GO** cả 2 trục
- 2026-07-12 Audit sẵn sàng BCTC Q2/2026 → `bctc-q2-readiness-audit.md` — KHÉP KÍN
- 2026-07-03 Usage-limit auto-resume → `usage-limit-auto-resume.md` — XONG
- 2026-07-02 Reliability hardening (AgentOps) → `reliability-hardening.md` — XONG

## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)
- R&D pipeline (mọi thử nghiệm paper-only) → `rnd-pipeline-tracker.md`
- Migration `ticker_prune` → `universe_pit` (G5-G9) → `universe-pit-migration.md`
- LAG ADV>0 filter — đo edge vs hiện vật fill → `lag-adv-filter-tracking.md` — chủ Taylor, mở 2026-08-03.
  **KHÔNG kết luận gì** trước 2 mốc cứng: checkpoint **2026-12-15**, rà soát đầy đủ **2027-03-31**.
- CASH_VENDOR gate (số cổ tức từ `tav2_bq.corporate_action` khi broker không giải được) →
  `cash-vendor-gate-tracking.md` — user chốt 2026-08-15 **giữ ĐÓNG**; mở lại chỉ khi có ≥1 sự
  kiện ISS/hỗn hợp VÀ đã qua **2026-09-13**, và vẫn cần user xác nhận lần nữa lúc đó.

## Nguồn chuẩn tắc đầy đủ
Chi tiết: kb/KNOWLEDGE.md (§1-9). Dự án đã đóng: kb/projects/ (index ở trên). Events: kb/events_buffer.md. Fleet: kb/fleet_status.md.
