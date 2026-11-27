---
kind: ops-playbook
title: "Playbook: NAV thiếu dòng, cổng exdate_frame, PRICE_XCHECK & Báo cáo ngày"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Playbook: NAV thiếu dòng, cổng exdate_frame, PRICE_XCHECK & Báo cáo ngày

> Tách nguyên văn từ [`../ops_runbook.md`](../ops_runbook.md) (2026-11-27, giữ trần <40 KB).

### NAV thiếu dòng `nav_history` — 2 đường ghi (aria-G, 2026-09-13)
Đường 1 = `eod_trading_report.sh` 19:10 (chỉ ở case HOLD / render đầy đủ — case không-plan và không-state thoát sớm, KHÔNG ghi NAV). Đường 2 = `nav_snapshot_daily.sh` 19:50: có dòng hôm nay ⇒ bỏ qua; có marker `state/nav_pending_retry/<acct>_<date>.*` ⇒ nhường `nav_sync_retry.sh`. Tin 🔴 từ đường 2:
1. `rc=2` sau 2 lần retry: đọc `logs/nav_snapshot_daily.log` (thiếu balances/vị thế/giá). Còn trong tối ⇒ chạy tay `mike/bin/nav_snapshot_daily.sh` (idempotent, an toàn chạy lại).
2. `rc=3` (sanity ±15%): nạp/rút tiền thật? ⇒ xác nhận rồi mới chạy lại với `NAV_SANITY_MAX_PCT` lớn hơn; không thì là lỗi dữ liệu.
3. ⛔ Sang NGÀY SAU mới phát hiện thiếu ⇒ KHÔNG chạy wrapper/`daily_nav_snapshot.py --date <ngày cũ>` đường live (vị thế broker LIVE ≠ vị thế ngày đó, ghi số sai âm thầm) — backfill bằng `--from-raw` (ghi `nav_is_estimate=True`).
5. **`rc=5` (corp_action_gate_v2 — KHỐI LƯỢNG vị thế đổi ngoài lệnh khớp thật).** Mã MỚI, KHÁC
   hẳn rc=4: **không** có marker `nav_pending_retry`, **không** được `nav_sync_retry.sh` retry,
   `nav_snapshot_daily.sh` rơi vào nhánh `*)` ⇒ 🔴 ngay. Cố ý: rc=4 là "giá chưa đồng bộ, chờ là
   xong"; rc=5 là "KL vị thế đã đổi, chờ KHÔNG bao giờ xong".
   - Bằng chứng trên đĩa: `data/execution_logs/nav_gate_block_<account>_<date>.json` (KHÔNG phải
     `nav_snapshot_*` — tách tên cố ý để không đè artifact audit của ngày đã có NAV). Đọc
     `corp_action_gate_v2.share_event_blocks` / `.qty_unexplained`.
   - **`share_event_blocks`** = phần dư KL khớp ĐÚNG tỉ lệ thực hiện của sự kiện cổ phiếu có
     ex-date = phiên kế tiếp ⇒ broker credit sớm thật (mẫu VHM/MBB/BID/VIX/MSB/VIB). Xử lý: chờ
     `corp_action_auto_confirm.py` (cron 19:25 ICT) ghi `_status=CONFIRMED` + `qty_multiplier` vào
     `data/corp_actions.json`, rồi backfill `python3 mike/bin/daily_nav_snapshot.py --account <X>
     --date <ngày> --from-raw`. CHỈ mã đã CONFIRMED mới được quy ngược KL; LIVE vẫn chặn.
   - **`qty_unexplained`** = KL đổi, lệnh khớp thật không giải thích được, và không khớp tỉ lệ sự
     kiện nào (kể cả ca lịch corp-action THIẾU sự kiện). ⛔ KHÔNG backfill trước khi có người đối
     soát KL thật với sổ broker (§27) — chưa biết nguyên nhân thì chưa biết quy ngược bao nhiêu.
   - Gate có thể đang chạy mà **thiếu lịch**: `corp_action_gate_v2.active=false` trong artifact +
     dòng ⚠️ trong log = snapshot `corp_action_daily_<date>.json` thiếu/hỏng/lệch `asof`. Trục
     KHỐI LƯỢNG vẫn bảo vệ; chỉ mất khả năng GÁN tên sự kiện cho phần dư.
6. Chạy tay `eod_trading_report.sh` SAU khi đường 2 đã ghi sẽ ghi đè dòng bằng bản đọc mới hơn (đường 1 không có guard, cố ý giữ nguyên) — sau 19:10 dữ liệu đóng cửa đã ổn định nên số phải trùng; lệch ⇒ soi `balance_ts` 2 lần đọc.

### `compute_active_nav.py` exit 5 — account về 0 vị thế (thêm 2026-09-13, commit c9edd4c6)
Hôm trước có cổ phiếu, hôm nay feed trả 0 vị thế ⇒ script **cố ý dừng exit 5, KHÔNG ghi**
`active_nav_<account>.json` (file cũ giữ nguyên) — chống feed DNSE rỗng tạm thời ghi NAV thấp giả
(chỉ tiền+egg, thiếu ~9 lần). Cron `compute_active_nav_all.sh` sẽ log rc=1 cho account đó.
1. Kiểm `positions` trong `dnse_raw_<hôm nay>.jsonl` mới nhất (lọc account_no, §12).
2. Feed rỗng tạm ⇒ chạy lại sau vài phút, KHÔNG thêm cờ.
3. Account THẬT đã bán sạch (đối chiếu fill thật §27) ⇒ `python3 mike/bin/compute_active_nav.py --account <X> --confirm-flat`.

### `compute_active_nav.py` exit 6/7 — cổng §exdate_frame (thêm 2026-09-24, audit dispatch corp-action-audit-c1c2)
KHÁC exit 5 (0 vị thế) — hai mã này chặn khi VẪN có vị thế nhưng KHÔNG dựng được một hệ quy
chiếu giá/khối-lượng đáng tin. Cả hai đều **KHÔNG ghi đè** `active_nav_<account>.json` (file cũ
giữ nguyên), nên hệ quả người vận hành thấy là **file NAV canonical đứng yên/quá hạn**, không
phải một con số sai lặng lẽ.

1. **`rc=6` — khối lượng vị thế đổi NGOÀI lệnh khớp thật, không quy được về một hệ quy chiếu
   giá.** Log in kèm danh sách mã bị chặn + lý do (`bin/compute_active_nav.py`, khối
   `if blocked:` ngay sau `exdate_frame.classify_positions`). Đây là ca **broker đã CREDIT SỚM**
   khối lượng của một sự kiện tỉ lệ (thưởng CP/cổ tức CP/tách) trước khi vendor
   `tav2_bq.corporate_action` xác nhận, và script không tự suy được giá cùng hệ cho phần dư đó.
   - Việc cần làm (đúng thứ tự, script tự nói trong thông điệp lỗi — đọc lại trước khi làm tay):
     (1) mã "KHÔNG dựng được giá cùng hệ" — NGƯỜI xác minh giá tham chiếu sau sự kiện (bảng giá
     sở/HOSE, thông báo GDKHQ) đối chiếu với `marketPrice` broker; (2) mã "CHƯA GIẢI THÍCH ĐƯỢC"
     — kiểm journal fill + lịch corp-action đúng như dòng log nêu.
   - ⛔ **Chạy lại KHÔNG tự hết rc=6** nếu chưa có thêm bằng chứng: script này không đọc
     `data/corp_actions.json`, nên đường phục hồi của `corp_action_auto_confirm.py --from-raw`
     (đường của `daily_nav_snapshot.py`, § rc=5 ở trên) **KHÔNG áp dụng ở đây** — đừng chờ cron
     19:25 rồi chạy lại tưởng sẽ tự thông, đó là hai script khác nhau đọc hai nguồn khác nhau.
   - Muốn xem con số mà KHÔNG ghi đè canonical: `--out <đường dẫn tạm khác canonical>` (script
     tự chối nếu `--out` trỏ lại chính canonical, xem [F2]/rc=7 ngay dưới).
2. **`rc=7` — `--asof` là ngày KHÁC hôm nay và `--out` (mặc định hoặc truyền tay) trỏ vào file
   canonical.** Cổng §exdate_frame chỉ chạy được ở nhánh `asof == hôm nay` (vị thế luôn LIVE, còn
   giá của một `--asof` quá khứ ở hệ quy chiếu khác) — nên script **từ chối ghi** thay vì âm thầm
   bỏ qua cổng bảo vệ. Gặp mã này:
   - Muốn refresh số sizing thật: bỏ hẳn `--asof` (mặc định hôm nay, LIVE + cổng chạy bình
     thường).
   - Muốn khảo sát/đối chiếu một ngày quá khứ: thêm `--out <đường dẫn khác canonical>` — kết quả
     đó **KHÔNG dùng làm mẫu số sizing** (vị thế LIVE trộn giá lịch sử là NGOÀI phạm vi cổng).
   - `--asof ""` (biến chưa set trong một lệnh script hoá) tương đương KHÔNG truyền — từ 2026-09-23
     (F1) không còn trượt qua cổng như bug gốc; nếu vẫn thấy rc=7 với asof rỗng, đó là bug MỚI,
     báo ngay đừng tự "sửa" bằng cách bỏ dấu ngoặc.
   - Không có tự động khôi phục cho hai mã này — cron `compute_active_nav_all.sh` chỉ log rc≠0,
     KHÔNG autofix (đúng domain "chạm sizing/gate" — §13, cần người quyết).

### NAV bị chặn bởi cổng PRICE_XCHECK (rc=4) — trước khi coi là sự cố

1. Gap `close_price` vs `marketPrice` vị thế **ĐÚNG BẰNG giá trị quyền** của một corp-action có
   ex-date = **phiên giao dịch KẾ TIẾP** ⇒ là **KỲ VỌNG**, không phải broker stuck: DNSE hạ giá
   tham chiếu vị thế vào TỐI TRƯỚC ngày ex, BQ/close thì chưa. Ca chuẩn: DGC tối T6 2026-09-11,
   46.750 vs 38.750, cổ tức tiền 2 đợt (3.000+5.000) ex T2 2026-09-14 — khớp từng đồng.
2. ⛔ **KHÔNG có tự động — làm TAY, theo thứ tự này** (bản nháp tự nhận diện bị arch-review vòng 2
   trả NEEDS_CHANGES 2026-09-12, đã gỡ; xem `kb/canonical.md` § DNSE ex-date):
   a. tra ex-date + giá trị quyền: `tav2_bq.corporate_action` (qua `corp_action_lib.pricing_events`,
      KHÔNG dùng `events()` executed_only — nó trả RỖNG đúng ngày cần) hoặc
      `kb/data_registry/price-volume/corp_action_pending.md`;
   b. **chỉ khi là cổ tức TIỀN MẶT** và `close − Σ cổ tức = marketPrice` (khớp trong 1 bước giá):
      đây là ca kỳ vọng, không phải sự cố;
   c. trước khi bỏ qua cổng, PHẢI kiểm bằng tay bất biến của §21: khoản phải thu ĐÃ bị trừ khỏi
      tiền chưa — `cum_dividend_excl.amount` trong `nav_snapshot_<account>_<date>.json` phải ≈
      `qty × cổ tức/cp` (ca DGC 09-11: 10.000 × 8.000 = 80.000.000 ✔). Nếu `amount=0` mà
      `cashDividendReceiving` của broker vẫn còn khoản đó ⇒ **đừng bỏ qua cổng**: NAV sẽ đếm 2 lần
      đúng bằng cổ tức. NAV đúng mark **giá CUM của phiên đó**, không phải giá broker đã điều chỉnh.
3. **Sự kiện CỔ PHIẾU (thưởng/trả cổ tức bằng cp/tách): KHÔNG BAO GIỜ bỏ qua cổng.** Broker credit
   KHỐI LƯỢNG cùng lúc hạ giá (VIB 2026-09-09 19:07: 500→547 và 15.050→13.700), mà nhánh `is_today`
   không quy đổi ngược qty ⇒ bỏ qua sẽ thổi phồng NAV (VIB +711.100đ, VHM 1:1 +100% vị thế).
   ✅ Lỗ hổng CŨ (sự kiện tỉ lệ NHỎ, thực đo min 1,03%, giá rơi <5% nên cổng PRICE_XCHECK không
   bật) **ĐÃ ĐÓNG** bởi `corp_action_gate_v2`: gate chặn theo bằng chứng KHỐI LƯỢNG (phần dư sau
   khi trừ lệnh khớp thật), độc lập biên độ giá ⇒ rc=5, xem mục 5 § NAV thiếu dòng.
   ⚠️ **ĐIỀU KIỆN CÒN LẠI — fail-open CÓ CHỦ ĐÍCH, đóng bằng tay:** trục KHỐI LƯỢNG cần một bản
   ghi vị thế TRƯỚC `date` để so. Khi **KHÔNG có BẤT KỲ bản ghi `dnse_raw_*.jsonl` nào** trước
   ngày đang tính (account mới, hoặc khoảng trống dữ liệu), `qty_prev = None` ⇒ gate KHÔNG chặn:
   không có cơ sở so sánh thì chặn là đoán mò. Ca "bản ghi ngày trước CÓ, nhưng VẮNG mã này"
   thì **KHÔNG** rơi vào đây — nó được quy `qty_prev = 0` (mã mới mua + sự kiện tỉ lệ ~1% vẫn bị
   chặn; đo thật tháng 9: 1/600 ticker-day, phần dư = 0,0 chính xác ⇒ không có false-block).
   Ngày đầu tiên có dữ liệu của một account ⇒ đối soát KL bằng tay với sổ broker.
4. Mọi ca còn lại xử lý như cũ: `nav_sync_retry.sh` retry tới 21:15 ICT rồi escalate bus question.

### LỆCH NGUỒN CỔ TỨC trong báo cáo — Discord "cần Winston (data-ops)" (thêm 2026-09-24, audit dispatch corp-action-audit-c1c2)
`report_return_gate.py` đối chiếu tiền cổ tức broker thật với vendor `tav2_bq.corporate_action`
cho mọi vị thế đang giữ; khi hai nguồn lệch (hoặc BQ lỗi hạ tầng không tra được), `report_return_gate`
in ra dòng máy đọc `VENDOR_MISMATCH_ALERT|...`/`VENDOR_LOOKUP_FAILED|...`, và **`bin/vendor_mismatch_alert.sh`**
(gọi từ `eod_trading_report.sh` + `check_report_cadence.sh`, đọc từ stdin) bắt lấy khối đó rồi bắn
Discord vào **topic Trading report** (`$TRADING_REPORT_THREAD`) với tiêu đề "⚠️ LỆCH NGUỒN CỔ TỨC
— cần Winston (data-ops)" hoặc "⚠️ VENDOR LOOKUP THẤT BẠI — cần Winston (data-ops)".

**Người trực (không phải Winston) thấy tin này — làm theo thứ tự:**
1. Đọc hết nội dung tin Discord trước khi làm gì khác — nó đã tự phân loại đúng 1 trong 3 nhánh
   lý do (script tự nói, KHÔNG cần đoán — §29):
   - **`cash_mismatch`** (hai nguồn bất đồng SỐ cổ tức) → việc của Winston: đối soát
     `tav2_bq.corporate_action` với sổ broker cho đúng (mã, ex-date) nêu trong tin.
   - **`stock_leg_ignored`** (nghi giá rơi do CHIA TÁCH bị đọc nhầm thành cổ tức) → việc của
     Winston: xác nhận lại sự kiện CỔ PHIẾU (ISS) với vendor, KHÔNG phải đối soát tiền.
   - **`lookup_failed`** (BQ lỗi hạ tầng, KHÔNG tra được vendor — khác hẳn "vendor xác nhận 0 sự
     kiện") → thường TỰ HẾT khi BQ khoẻ lại; kiểm `bin/bq_freshness_check.sh` trước khi làm gì
     khác. Chỉ escalate Winston nếu lỗi LẶP LẠI nhiều lượt liên tiếp (không phải 1 lần).
2. **Gọi Winston** — đây là domain "vận hành TRADING/data/pipeline/report" (bảng § Phân domain
   tự sửa lỗi ở cuối file này), fixer = Winston. Cách gọi (chọn 1, tuỳ ai đang trực):
   - Agent/Mike đang trong phiên tương tác: `Agent` tool với `subagent_type: data-ops`, hoặc
     dispatch ngang hàng `DISPATCH_FROM=<agent> mike/bin/dispatch.sh Winston "đối soát lệch
     nguồn cổ tức <mã> ex-date <ngày>, xem chi tiết topic Trading report"`.
   - User đọc Discord trực tiếp: trả lời ngay trong thread đó (Winston/Mike theo dõi topic này).
   - ⚠️ **KHÔNG có auto-route** cho ca này: script tự ghi bus `Mike error vendor-mismatch-<file>`
     (kênh PHỤ, không phải kênh chính) nhưng `bin/ops_health_check.sh` **chỉ xét
     `event_type == "question"`, bỏ qua `error`** — nên event này KHÔNG tự lên hàng chờ xử lý của
     ai. Discord là kênh CHÍNH, phải có người chủ động đọc và dispatch tay.
3. **Biết đã gỡ chặn chưa** — KHÔNG có cờ "đã xử lý" tự động cập nhật ngược lại tin Discord cũ.
   Xác nhận bằng 1 trong 2 cách:
   - Chạy lại thủ công: `python3 mike/bin/report_return_gate.py <report_path>` — hết
     `VENDOR_MISMATCH_ALERT`/`VENDOR_LOOKUP_FAILED` cho đúng (mã, ex-date) đó ⇒ đã thông (vendor
     đã cập nhật hoặc BQ đã khoẻ lại).
   - Đợi báo cáo NGÀY KẾ TIẾP (đường phát lại THẬT của cơ chế này — file tên khác nên chạy lại
     toàn bộ pipeline từ đầu): còn giữ vị thế mã đó ⇒ gate tự quét lại đúng cặp (mã, ex-date)
     trong `LOOKBACK_DAYS=120`; sạch ⇒ không còn tin mới cho mã đó.
   - ⛔ **Bán hết vị thế TRƯỚC khi lệch nguồn được xử lý** = mất khả năng tái tạo cảnh báo (event
     rơi khỏi phạm vi quét vì không còn giữ mã) — nếu đã bán, đối soát lệch nguồn này coi như
     xong về mặt báo cáo (không còn ảnh hưởng số tương lai) nhưng VẪN nên xác nhận với Winston
     cho việc khác (kiểm dữ liệu vendor nói chung), không tự đóng coi như hết trách nhiệm.
   - De-dup 1 lần/file/ngày ở `state/vendor_mismatch_alerted.json` — thấy tin liên tục nhiều
     NGÀY KHÁC NHAU cho CÙNG một (mã, ex-date) nghĩa là vẫn CHƯA xử lý, không phải bug spam.

### Báo cáo NGÀY bị cổng tỉ suất CHẶN (K1, từ merge `fix/daily-report-return-gate-20261010`)
Từ K1, tỉ suất từng mã trong báo cáo ngày lấy từ công cụ §21 và cổng giao hàng KIỂM từng dòng vị thế
(`MÃ <giá trị>M, ±x.xx%`). Cổng chặn thì báo cáo ngày của tài khoản đó KHÔNG được gửi.

**Triệu chứng.** Tối 19:10 không có báo cáo ngày của một tài khoản ở topic Trading report · bus có
`Mafee error eod-trading-report-delivery-incomplete`, trường `cause` là LÝ DO THẬT (không còn câu cố định
"delivery chưa đủ kênh") · sáng hôm sau sweep 08:30 bắn `🔴 Delivery INCOMPLETE — <file> — <lý do thật>`
và lặp mỗi ngày cho tới khi báo cáo đó giao xong.

**Làm theo thứ tự:**
1. Đọc lý do — KHÔNG đoán: `grep -n '❌ CHẶN' -A8 mike/logs/eod_trading_report.log | tail -40` (khối cuối là
   lượt mới nhất). Cùng log, các dòng `portfolio_status: <MÃ> (…) không có tỉ suất §21: …` nêu lý do thật
   của từng mã mà báo cáo ghi "(chưa có tỉ suất)".
2. Rẽ theo CHÍNH dòng ❌ CHẶN đó:
   - `… (dòng vị thế báo cáo ngày, dòng N): báo cáo X% vs kỳ vọng Y%` — số lúc SINH báo cáo khác số lúc
     CỔNG chạy: hai lần đọc `dnse_raw` cách nhau ~2–3 phút rơi vào hai bản ghi `positions` khác nhau
     (nợ đã ghi F8, hiếm). ⇒ chạy lại (bước 3). Chạy lại mà vẫn lệch ⇒ lỗi code, dispatch Taylor kèm khối chặn.
   - `mục 'Chi tiết … (n mã)' … cổng chỉ đọc được …` — dây bẫy định dạng: có vị thế in theo dạng cổng không
     đọc được. KHÔNG chạy lại (sẽ chặn y hệt). Đây là hợp đồng `portfolio_status.py` ↔
     `report_return_gate.POSBIT_RE` bị ai đó sửa một phía ⇒ dispatch Taylor; chạy
     `python3 mike/bin/portfolio_status_selfcheck.py` (các ca "HỢP ĐỒNG với cổng") để thấy phía nào trôi.
   - `… cổng KHÔNG dựng được giá vốn thô để kiểm — …` / `giá đóng cửa phiên … CHƯA có trên BQ` /
     `giá đóng cửa của <MÃ> trên BQ dừng ở phiên …` — DỮ LIỆU: cổ tức chưa giải được, hoặc BQ chưa nạp
     phiên. Báo cáo đúng ra đã KHÔNG in tỉ suất mã đó; bị chặn nghĩa là lúc sinh và lúc cổng chạy thấy
     dữ liệu khác nhau ⇒ kiểm `bq_freshness_check.sh` rồi chạy lại (bước 3).
   - `LỆCH NGUỒN VENDOR` / `VENDOR LOOKUP THẤT BẠI` ⇒ mục ngay trên (Winston).
   - `cause` là một dòng lỗi Python — rẽ theo ĐUÔI của dòng đó (`run_gate` không bắt lỗi của
     `position_returns`, nên lệnh fail-closed CỐ Ý cũng hiện ra dạng này):
     · kết thúc bằng `— CHẶN` hoặc `CHẶN (fail-closed)` (vd `ValueError: không lấy được giá thô … từ BQ … — CHẶN`,
       `FileNotFoundError: thiếu …dnse_raw… — CHẶN (fail-closed)`, `ValueError: thiếu giá đóng cửa … — CHẶN`)
       ⇒ HẠ TẦNG/DỮ LIỆU: kiểm BQ (`bq_freshness_check.sh`) / file `dnse_raw` của ngày đó rồi chạy lại (bước 3).
     · exception khác (`KeyError: …`, `TypeError: …`, `… (cổng con thoát lỗi, không in khối chặn)`) ⇒ cổng SẬP
       do lỗi code: dispatch Taylor kèm traceback trong log. KHÔNG chạy lại.
3. Chạy lại cho ĐÚNG tài khoản + ngày:
   `mike/bin/eod_trading_report.sh --account <SpaceX|ZaloPay> --date <YYYY-MM-DD>`
   Phía GIAO thì an toàn: `report_delivery_gate` hash-bound — kênh đã có bằng chứng không gửi lại.
   ⚠️ Phía NAV thì KHÔNG phải lúc nào cũng an toàn: `eod_trading_report.sh` gọi `daily_nav_snapshot.py` ở chế
   độ live — lấy vị thế HIỆN TẠI của broker nhân giá đóng cửa ngày D rồi GHI ĐÈ dòng `nav_history` ngày D.
   · Chạy lại trong CÙNG buổi tối, hoặc cho ngày quá khứ nhưng TRƯỚC lệnh khớp đầu tiên của phiên kế
     (trước 09:15): được.
   · Sau lệnh khớp đầu tiên của phiên kế: PHẢI sao lưu dòng `nav_history` ngày D trước khi chạy, và sau đó
     khôi phục bằng `daily_nav_snapshot.py --from-raw --date D` — nếu không, NAV ngày D bị viết lại bằng khối
     lượng của ngày sau (xem "NAV thiếu dòng `nav_history`" mục 6).
   · Chạy lại cũng kích lại dispatch risk-auditor nếu còn file `eod_mismatch_*` của ngày đó.
4. KHÔNG sửa tay con số trong file báo cáo, KHÔNG `--skip-validation` / `--skip-return-gate` để "cho qua":
   số không qua cổng là số chưa kiểm.

**Báo cáo ra nhưng có dòng "⚠️ Chưa có bảng tình trạng danh mục cho báo cáo hôm nay — đội vận hành đang
kiểm tra."** = `portfolio_status.py` lỗi hoặc quá trần 600s. Lý do thật: `grep -n 'portfolio_status: KHÔNG'
mike/logs/eod_trading_report.log | tail -5`. Báo cáo vẫn đi (không có tỉ suất nào để kiểm); muốn bổ sung
khối danh mục thì chạy lại như bước 3 sau khi nguyên nhân (thường là BQ) hết.

**Thời lượng mới (ngày có lệnh).** `portfolio_status` 128–158s + cổng 35–36s ≈ 2'45"–3'15" mỗi tài khoản,
hai tài khoản nối tiếp ⇒ EOD xong ≈ 19:16–19:17 (đo trên dữ liệu thật 02/10 + 09/10, ngoài giờ). Chưa thấy
báo cáo lúc 19:12 KHÔNG phải sự cố. Chi tiết + ca xấu nhất: `kb/cron_registry.md` hàng 19:10.

**Rác.** Sổ nhớ BQ của lượt (`/tmp/eod_bq_memo.*`) tự xoá khi script thoát; lượt bị SIGKILL để lại thì lượt
kế tiếp tự dọn cái cũ hơn 1 ngày. Không cần dọn tay.

**Lùi một bước** (khi chính K1 là thủ phạm và cần báo cáo ngày đi ngay): `git revert -m 1 <merge commit của
fix/daily-report-return-gate-20261010>` trên repo `mike`, rồi chạy lại lệnh ở bước 3. Không có knob env nào
tắt K1. Sau khi lùi, báo cáo ngày quay về tỉ suất tự tính trên `costPrice` (sai với mã có cổ tức) và cổng lại
không đọc dòng vị thế báo cáo ngày — chỉ là tạm, phải vá tiến.

**Bật tài khoản live MỚI (ảnh hưởng tới cổng này).** Trước lệnh mua đầu tiên của tài khoản mới phải có **≥2 bản ghi
`positions` rỗng** của nó trong `dnse_raw` (bot poll ít nhất 2 lần). Lý do: công cụ §21 coi MỘT bản đọc rỗng đơn lẻ
ngay trước bản ghi có vị thế là có thể do lỗi API (fail-closed) ⇒ mã tài khoản mới mua ngay sau đó bị coi là "sổ bắt
đầu khi đã giữ", các bước nhảy nhiễu cũ của mã đó bị phủ quyết và mã mất kỳ vọng ở MỌI tài khoản (tái hiện với DRI,
arch-review 7812f586). Nhịp ghi hiện tại (≥9 bản ghi mỗi tối + 1 bản ~04:55) thoả sẵn; chỉ cần nhớ khi onboarding.
