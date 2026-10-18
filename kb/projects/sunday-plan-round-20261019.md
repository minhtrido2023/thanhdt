# Vòng plan Chủ nhật mùa BCTC (2026-10-19, Taylor_20261018_173105 · vòng 2 Taylor_20261018_180113)

**Vấn đề:** re-rate 8L chạy mỗi ngày trong cửa sổ BCTC, chuỗi plan chỉ T2-T6 ⇒ BCTC công bố T7/CN không vào plan thứ Hai.
**Giải pháp:** `bin/sunday_plan_round.sh` (+ `_lib.py`, `_selfcheck.sh`) — chạy MỘT lần CN 19:00 ICT, KHÔNG sửa hành vi chuỗi T2-T6
(dùng env opt-in `MIKE_MORNING_RUN=1 MIKE_MORNING_FORCE=1` đã có + `MIKE_MORNING_NOTE_TAIL` mới, mặc định = văn bản cũ từng byte).

## Quyết định (a)/(b)/(c) mỗi account
- Plan được đưa qua ĐÚNG đường nạp của executor (`trading_bot.plan.load_plan` → `PlannedOrder`, sau `resolve_buy_ceiling`) rồi so:
  ticker, side, qty, `ref_price` làm tròn bước giá, urgency, book, cash_only, trần giá thực, priority, lever_f, loan_package_id
  + cấp plan: state, state_name, strategy, strategy_version, signal_date. **Không** so `order_type`/`limit_price_vnd` (`PlannedOrder`
  không có; executor không đọc). `PlannedOrder` không có trường "timing" — timing do cfg executor, không do plan.
- (a) giống → khôi phục NGUYÊN file thứ Sáu; thông báo **in approved_by đọc thật từ file** (§29), không nói suông "giữ duyệt".
- (b) khác → giữ plan mới, gỡ `approv*`/`mafee*`, `requires_user_approval=true`, tự gọi `send_plan_report.sh --account`, post diff.
- (c) job fail/timeout/chưa-xác-minh-dừng/plan hỏng/không đổi byte/freshness fail/injector fail/**artifact park thứ Sáu có đề xuất** → khôi phục thứ Sáu + bus `error` + lý do thật.
- Lỗi của MỘT account không kéo account khác: `decide` tự bọc (khôi phục RIÊNG account đó); không khôi phục được ⇒ `RESULT=x` (không bao giờ nói "đã khôi phục"). `qty` phải là int dương.

## Chốt chặn "job DollarBill ghi muộn" (vòng 2)
1. Job id luôn parse từ `freshness.log` **bất kể FRESH_RC** (freshness fail/timeout có thể đã dispatch rồi mới chết); mọi đường khôi phục
   (poll quá hạn, freshness fail, TERM/INT/EXIT) gọi `cancel_live` → lưu rc THẬT của `jobs.sh cancel` ngay sau lệnh.
2. `cmd_job_cancel` chỉ hành động khi status=`running`; `retrying`/`usage_limited`/`maxturns_pending` ⇒ no-op rc=0. Nên sau cancel wrapper **đọc lại bản ghi
   `bus/jobs/<id>.json`**: chỉ "đã dừng" khi status ngoài `LIVE_STATUSES`; với chờ-resume thì gỡ `bus/pending_resumes/<id>.json` (cất vào
   `state/.../pending_removed/` làm chứng cứ) — bản ghi resume đã mất ⇒ resume có thể đã bắn thành job MỚI id lạ ⇒ **không xác minh được ⇒ escalate**, không báo "đã huỷ".
   `retrying` thử cancel lại `SPR_CANCEL_TRIES` lần. Khi có account hỏng còn quét job DollarBill lạ đang sống bắt đầu sau lúc wrapper chạy.
3. `bq_freshness`/injector/sleep chạy nền + `wait` (trap TERM chạy NGAY, không đợi lệnh foreground), con chạy với `9>&-` (không giữ flock).
4. **Kiểm cuối đêm `--verify`** (cron 23:00 CN trong `--second-chance` + 08:30 T2): so md5 **NỘI DUNG** plan (đã bỏ `approv*`/`mafee*`/
   `requires_user_approval`) với manifest. Lệch ⇒ gỡ dấu duyệt, `requires_user_approval=true`, notify + bus error, rc=4. Lý do so nội dung chứ không so byte: user duyệt
   plan (b) hợp lệ chỉ đổi các trường duyệt; người ghi muộn đổi nội dung. (Khác lệnh gốc: lệnh gốc nói "md5 plan"; byte-md5 sẽ gỡ nhầm duyệt thật của user.)
5. Stash **idempotent**: manifest cùng ntd đã có ⇒ kế thừa stash thứ Sáu GỐC (không chụp lại từ đĩa); stash gốc hỏng ⇒ DỪNG. Recover cất file đĩa khác stash vào `superseded/`.
6. Recover chạy TRƯỚC cổng ngày, CHỈ manifest ntd ≥ hôm nay (tuần cũ ⇒ `stale_skipped`, không chép đè plan đã thực thi).

## Tầng park (MED-5)
`park_trim_daily` 19:30 → `jit_unpark_daily` 19:40 → `merge_park_daily` 20:20 đều tự bỏ qua cuối tuần (`park_trim_daily.sh:37`, `merge_park_daily.sh:43`) ⇒ plan CN **không có lệnh bán park**
mà plan thứ Sáu (đã qua `merge_park_orders.py --write`) có. Wrapper KHÔNG chạy chuỗi park. Quy tắc bảo thủ: artifact `park_trim_<A>_<ntd>.json`/`jit_unpark_<A>_<ntd>.json` thứ Sáu có `orders` qty>0
(hoặc `buy_amendments` không rỗng) hoặc **vắng/hỏng** ⇒ ép (c) giữ plan thứ Sáu; rỗng ⇒ so sánh bình thường. Wrapper chạy lại đúng compute_active_nav_all 20:15 → inject_discretionary 20:30 → auto_exit_inject 20:40 → drift 20:50.

## Side effect khi chạy CN (khai theo yêu cầu)
- `macro_healthcheck.py`: **gửi Telegram**, ghi lại `data/macro_health.json`.
- `bq_freshness_check.sh` (morning+force): ghi lại `golive_state_today.json`, `golive_v23_recommendations_*.csv`, `golive_v23_status`, `universe_pit` (phiên thứ Sáu), các `.pkl` cache; dispatch DollarBill (ghi plan).
- 3 injector: ghi vào plan ngày đích (`compute_active_nav_all` ghi `active_nav_<acct>.json`).
- `send_plan_report.sh` (account (b)): gửi Telegram/Discord. Wrapper: notify `trading_daily`, bus `error`, `state/sunday_plan_round/<ntd>/` (giữ `SPR_KEEP_WEEKS`=8 tuần done/recovered/stale).

## Cổng cuối tuần đã phát hiện
1. **`data/macro_health.json` (BLOCK thật):** `macro_state_live.get_gated_state(max_health_age_min=1440)` fail-closed về DT4_only khi file >24h; file do `daily_refresh_v34b_linux.sh` [11c] ghi T2-T6 ⇒ CN 19:00 đã ~48h. Wrapper chạy lại `macro_healthcheck.py` (tự đo độ tươi 4 nguồn, không nới ngưỡng).
2. `expected_session.py --morning`: CN → phiên=thứ Sáu, đích=thứ Hai; rào 08:30 chỉ áp khi đích=hôm nay ⇒ không vướng.
3. DollarBill prompt ghi `data/plan_<ACCT>_<ngày>.json` nhưng loader/bot đọc `data/trade_plans/…` (có file lạc `data/plan_ZaloPay_2026-10-14.json`). Wrapper chỉ nhìn `data/trade_plans/`; plan viết sai chỗ ⇒ (c) "file không đổi byte".
4. `plan_position_drift_check.py`: CN trả SKIP (không phải phiên) — chỉ cờ, không chặn; vị thế đổi do corp-action credit CN không được kiểm.

## Chưa kiểm được (không chạy thật)
`publish_gated_state` frozen-state guard ngày CN; giá DNSE cuối tuần trong `compute_active_nav`; dedupe ledger của `discretionary_accumulation_inject` khi chèn lại lần 2 cùng plan_date;
hành vi `jobs.sh cancel`/`bus/pending_resumes` trên bản ghi THẬT (selfcheck dùng stub mô phỏng đúng mã thoát/ngữ nghĩa đọc từ `mike_json.py`, không gọi bản thật);
`load_plan`+`resolve_buy_ceiling` với ceiling_rule "A" (chỉ test trần cũ); `macro_healthcheck.py` thật.
Không làm (tuỳ chọn): mẫu "file ứng viên" cần sửa prompt dispatch trong `bq_freshness_check.sh` (sửa hành vi T2-T6) — mục 1+2 đã đủ chốt chặn.
