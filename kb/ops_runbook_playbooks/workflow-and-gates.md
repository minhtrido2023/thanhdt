---
kind: ops-playbook
title: "Playbook: Classifier, Morning Run, Cổng DD/LAG & Pattern B"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Playbook: Classifier, Morning Run, Cổng DD/LAG & Pattern B

> Tách nguyên văn từ [`../ops_runbook.md`](../ops_runbook.md) (2026-11-27, giữ trần <40 KB).

## Nhật ký & kinh nghiệm

- Mọi sự cố ảnh hưởng workflow sống → **1 file mới** trong `kb/incidents/<YYYY-MM>/` (blameless,
  có commit hash) + 1 dòng trong `kb/incidents/index.md`. KHÔNG append vào `kb/INCIDENTS.md` (STUB).
- Fix xong PHẢI verify artifact thật (chạy lại checker, đối chiếu số thật) — không tin
  self-report của agent/job status (MIKE.md §Quy chuẩn #2).
- Số đã gửi cho user mà phát hiện sai → đính chính NGAY trên kênh đã gửi, không âm thầm sửa.
- Bug ở 1 script → grep các script khác làm việc TƯƠNG TỰ (bài học 07-06: 3 bug cùng dạng
  "logic trùng lặp không đồng bộ" trong 1 ngày).

## Headless agent bị classifier chặn git-write / BQ-write vào file production (tái diễn 09-27, 09-28)

**Triệu chứng:** agent chạy headless (dispatch) làm xong việc, đã có verdict CONFIRMED, nhưng
bước CUỐI (`git merge` vào main, `bq query 'CREATE OR REPLACE'`, ghi đè file production) bị
harness classifier từ chối. Agent quay ra escalate, việc treo cho tới khi có người chạy trong
phiên tương tác. Đã tốn ~2h (09-27 `fa_ratings_8l` restore 06:54→08:55) và 1 lần nữa 09-28
(`close_repair` merge `eec792d7`/`3c55c249`).

**Đây KHÔNG phải lỗi fleet — đừng đi debug `dispatch.sh`/quyền file.** Nhận diện bằng: job có
finding "ALL_VERIFIED_READY ... blocked-by-classifier", hoặc commit nằm trên feature branch mà
không merge được.

**Làm gì NGAY (đừng điều tra lại từ đầu):**
1. Xác minh công việc thật sự đã xong: verdict CONFIRMED trên bus + selfcheck PASS + commit tồn
   tại trên feature branch (`git log --oneline --all | grep <hash>`).
2. Người/phiên TƯƠNG TÁC chạy bước cuối (merge / BQ write). Headless retry sẽ hỏng lại.
3. Đóng question gốc bằng event `answer` NGAY sau khi merge — nếu không, checker §5 sẽ báo
   pending tiếp 2 lần/ngày dù việc đã xong (đúng lỗi đã xảy ra với
   `closerepair-fix-approval-needed`, mở 09-28T10:57Z, merge xong 09-28 mà vẫn pending 29/09).

**Giảm tần suất:** việc biết trước sẽ cần git-write vào main hoặc BQ write → dispatch dạng
TƯƠNG TÁC ngay từ đầu, đừng để headless chạy tới bước cuối rồi tắc. (Câu hỏi có nên bắt buộc
hoá quy tắc này vẫn đang chờ user — bus topic
`retro-pattern-recurring-classifier-blocks-headless-agent-production-write`.)

## Pattern B — fix THẬT đã merge nhưng câu hỏi bus không được đóng (tái diễn 08-13, 09-27, 09-28, 09-29 ×2)

**Triệu chứng.** Checker §5 / `bus_question_audit.py` báo một câu hỏi còn treo; `wags_autofix`
thức dậy và đốt trọn một job chỉ để đọc lại git log rồi kết luận "đã sửa từ lâu". Quyết định đi
qua kênh HÀNH ĐỘNG (user duyệt Discord + agent commit + merge) mà không ai ghi event `answer`.

**Trước khi chẩn đoán lại từ đầu, chạy 2 cái nhắc này:**
- `bin/question_commit_hint.py [--days N] [--max N] [--per-question N]` — quét git log 2 repo
  (mike + WorkingClaude) tìm commit TRÔNG NHƯ đã sửa từng câu hỏi còn treo. In CHÙM tối đa 2
  commit/câu hỏi (`--per-question` để xem nhiều hơn) kèm nhãn `[CHẮC|có thể / code|docs / điểm]`;
  commit có sửa file code xếp TRƯỚC commit docs-only kể cả khi điểm thấp hơn. Cắt ở cả 2 tầng
  (câu hỏi + commit) đều NÓI RA phần bị cắt. Nó là **GỢI Ý, KHÔNG tự đóng** — đọc commit rồi mới
  đóng bằng `bin/close_bus_question.py`.
  Wire: `wags_autofix.sh` **và** `bin/dispatch.sh` ở đường HOÀN TẤT THÀNH CÔNG của CẢ HAI nhánh
  (--bg trong `_bg_wrapper` + foreground) — user mandate 2026-09-30 "gọi là bắt buộc, không phải
  tuỳ chọn". Mọi call site `timeout 25 … || true`, fail-open. Ngoại lệ có chủ đích:
  `bin/verify_finding.sh` tự dựng job record riêng, không qua dispatch.sh (job verify không sinh
  commit fix nên không có gì để gợi ý).
- `bin/dispatch_question_hint.py` — cùng việc nhưng nguồn là prompt dispatch.

**Giới hạn đã biết (gap F5, THU HẸP 2026-09-30 nhưng CHƯA đóng).** Từ commit wiring
2026-09-30, hint còn chạy ở đường hoàn tất MỌI job qua dispatch.sh ⇒ agent vừa merge fix được
nhắc NGAY trong lượt đó (và agent giao việc thấy qua prompt AUTO-CALLBACK), tức nhiều ca được
đóng TRƯỚC khi checker 2 lần/ngày kịp bắn escalation. Nhưng đây là nhắc phía NGƯỜI LÀM, không
phải chặn phía CHECKER: job đã kết thúc trước khi hint in ra, và job do cron/Mike giao (from=Mike)
không có AUTO-CALLBACK nên hint chỉ nằm trong `$logfile`. Chỗ
bịt thật là `ops_health_check.sh` §5 / `bus_question_audit.py` hạ cấp escalation khi có bằng
chứng artifact — chưa làm, chờ user chốt (option A của câu hỏi
`retro-pattern-recurring-bus-question-closure-gap-real-fix-no-answer-event`). Lớp câu hỏi
`retro-pattern-recurring-*` bị hint LOẠI HẲN có chủ đích: nó nói về một pattern, không commit nào
đóng được, chỉ user chốt A/B/C.

**Luật vận hành:** merge xong một fix cho việc có bus question mở ⇒ đóng vòng NGAY trong cùng
lượt (`bin/close_bus_question.py` hoặc `append_event.sh <agent> answer <topic> …`). "Đã merge"
là sự kiện phải đóng question, không phải việc để lần sau.

## Lược sử
2026-07-07: viết lần đầu + wire autofix vào ops_health_check.sh & sync_bq_cache_daily.sh
(sau chuỗi sự cố 07-06: EOD crash, NAV sai 2 lần, cache thối 10 ngày, false-SEV1 macro).

## Classifier chặn headless agent ghi production / git merge (chốt phương án C, 2026-10-05)
Triệu chứng: Taylor/Wags headless báo "bị classifier chặn" khi `git merge` nhánh đã CONFIRMED, ghi file
production-adjacent, hoặc BQ `CREATE OR REPLACE` (ca thật 09-27 fa_ratings_8l restore mất ~2h; 09-28
close_repair merge). KHÔNG thử workaround khác (đổi đường, tách lệnh) — đó là cách đẻ rủi ro.
Xử lý tại chỗ, không điều tra lại:
1. Agent ghi bus `finding` có: branch + HEAD, verdict quant-skeptic/arch-review (CONFIRMED/APPROVED), lệnh merge/ghi CHÍNH XÁC cần chạy.
2. Mike (phiên tương tác) kiểm artifact: `git log main..<branch>`, selfcheck chạy lại, verdict thật trên bus — rồi tự chạy lệnh. Tiền thật/trading_rules vẫn cần user duyệt như thường lệ.
3. Trần chấp nhận: ~1-2h trễ/lần. Nếu tần suất >2 lần/tuần → xem lại phương án B (git write production dispatch dạng tương tác ngay từ đầu).
(bus: Mike/retro-pattern-recurring-classifier-blocks-headless-agent-production-write)

## Chạy TAY buổi sáng khi BQ xong muộn — `MIKE_MORNING_RUN=1` (thêm 2026-10-15, sau sự cố plan 15/10)
Sự cố gốc: 14/10 ticker_prune về BQ sau 19:45 ICT ⇒ 18:30 `daily_refresh_v34b` die, 19:00 gate publisher đòi
`as_of` = ngày lịch ⇒ plan 15/10 không lập; sáng 15/10 BQ đã đủ nhưng cả 2 script đều khóa theo NGÀY LỊCH nên
buổi sáng không có đường chạy hợp lệ. Cơ chế opt-in (cron KHÔNG đặt biến ⇒ 18:30/19:00 y nguyên):
- `bin/expected_session.py` — phiên gần nhất đã kỳ vọng có EOD (cutoff 17:00 ICT). `--morning` còn là RÀO:
  exit 3 nếu plan đích = HÔM NAY mà đã ≥ 08:30 ICT (preflight 08:45/bot 09:05 đã qua hoặc phiên đang chạy).
- Trình tự (đúng thứ tự, ĐỀU từ terminal của anh hoặc phiên có quyền; không có bước nào bỏ qua gate AN TOÀN dữ liệu):
  1. `MIKE_MORNING_RUN=1 /home/trido/thanhdt/WorkingClaude/daily_refresh_v34b_linux.sh` (kiểm ingest theo phiên, publish DT5G `as_of`=phiên).
  2. `MIKE_MORNING_RUN=1 mike/bin/bq_freshness_check.sh` — TODAY=phiên, plan đích=NEXT; gate publisher: mtime ∈ [phiên, hôm nay].
     Plan đích ĐÃ TỒN TẠI ⇒ `[SKIP-MORNING]` không ghi đè (ép: `MIKE_MORNING_FORCE=1`, chỉ khi chắc plan cũ chưa duyệt).
  3. ⚠️ **Chuỗi hạ nguồn KHÔNG theo morning mode** (nhắm `next_trading_day(ngày lịch hôm nay)` ⇒ sáng T5 sẽ nhắm T6).
     **CHỜ DollarBill xong TRƯỚC**: bước 2 dispatch `--bg` nên script trả về khi plan CHƯA có. Chạy `bin/jobs.sh status <job_id>`
     = done VÀ xác nhận `data/trade_plans/plan_<A>_<NEXT>.json` tồn tại. Chạy `auto_exit_inject` khi plan chưa có ⇒ in
     "CHƯA có plan file — no-op" và rc=0 (KHÔNG báo lỗi) ⇒ user duyệt plan THIẾU lệnh thoát T+25/T+45/T+60. Rồi, cho từng account A:
     - `python3 mike/bin/auto_exit_inject.py --account <A> --plan-date <NEXT>` — đọc output, KHÔNG được là dòng no-op. ⚠️ nó lấy
       `signal_date` = ngày lịch hôm nay ⇒ sessions_held lệch +1 so với cron (lệnh thoát có thể bắn SỚM 1 phiên) — soát từng lệnh thoát.
     - `python3 mike/bin/discretionary_accumulation_inject.py --account <A> --plan-date <NEXT>` (KHÔNG phải `inject_discretionary_orders.sh`, không có tham số ngày).
     - `python3 mike/bin/plan_position_drift_check.py --account <A> --date <PHIÊN>` (tự suy plan = next_trading_day(PHIÊN); truyền NEXT là SAI).
     - `send_plan_report.sh` nhắm next_trading_day(hôm nay) và không có tham số ghi đè ⇒ KHÔNG dùng được buổi sáng: đọc plan trực tiếp và gửi tóm tắt cho user duyệt qua Discord.
     - KHÔNG chạy được buổi sáng (cổng giờ): `late_plan_catchup.sh` (BEFORE_WINDOW trước 21:00), `park_trim_daily`/`jit_unpark_daily`/`merge_park_daily` (từ chối trước 15:00). Park đang 0% ⇒ coi như no-op, GHI RÕ "đã bỏ qua" khi báo user.
     - Xác nhận file plan rơi ĐÚNG `data/trade_plans/` (prompt DollarBill cũ ghi `data/plan_...` ở thư mục gốc; tồn tại `data/plan_ZaloPay_2026-10-14.json` ngoài `trade_plans/`).
  4. Prompt DollarBill ở morning mode tự ép `requires_user_approval=true` + ghi rõ "chạy tay buổi sáng".
- Hạn chế đã biết (arch-review 2026-10-15 vòng 1+2, NON-BLOCKING): rào 08:30 chỉ kiểm LÚC KHỞI ĐỘNG (pipeline 0-3 + DollarBill có thể kéo dài qua 08:45); `requires_user_approval` chỉ do prompt ép (mặc định code = False); không có lock (chạy 2 lần liên tiếp có thể dispatch DollarBill 2 lần); pipeline-0..3 vẫn chạy kể cả khi mọi plan đích đã tồn tại; prompt/`CAL_TODAY` chưa có test (mutation M10/M11/M17 lọt); CSV `golive_v23_recommendations_{ngày lịch}.csv` ≠ `signal_date` ⇒
  pipeline-3 push partition phiên đó thất bại (chỉ WARN); lần 19:00 cùng ngày ghi đè file khuyến nghị. Chưa chạy
  end-to-end pipeline-2/3 ở morning mode lần nào — lần đầu dùng thật phải theo dõi tay.
- Selfcheck: `bin/expected_session_selfcheck.py`, `bin/dt5g_publisher_gate_selfcheck.sh` (ca M1-M9),
  `bin/bq_freshness_morning_selfcheck.sh`, `WorkingClaude/daily_refresh_morning_selfcheck.sh`.

## Cổng DD trước plan LAG — Mike ghi ack + hợp đồng NO_PACK (thêm 2026-10-21, job Taylor_20261021_154311)
Mã LAG (due_today/upcoming) CHỈ vào `orders[]` khi `data/lag_dd/<mã>_<release>.json` CLEARED hoặc user ack PROCEED.
  `--gate` mới là nguồn sự thật: gói CLEARED vẫn ra `ACK_DROP`/`ACK_RESEARCH` nếu user đã loại/hoãn release đó (từ 2026-10-24);
  gỡ DROP = user đổi ý ⇒ ghi PROCEED bằng hash của gói hiện tại (ack mới nhất thắng).
- **Ai quyết**: CHỈ USER. Mike chỉ chép lại câu trả lời thật của user (coding_guidelines §20: `decided_by=user`).
- **Quy trình ghi ack** (user trả lời trên Discord topic plan_approval cho tin "🧾 DD trước plan"): tin in `hash`
  của bộ cờ user đã xem. Mike chạy
  `python3 mike/bin/lag_dd_ack.py --ticker <MÃ> --release-date <D> --decision PROCEED|DROP|RESEARCH --decided-by user --at <ISO có múi giờ lúc user trả lời> --flags-hash <hash TRONG TIN user đã trả lời> --source "<link/trích tin user>"`.
  `--flags-hash` và `--source` BẮT BUỘC; hash lệch gói hiện tại (gói đã sinh lại sau khi gửi tin) ⇒ lệnh TỪ CHỐI, KHÔNG ghi:
  khi đó chạy lại `lag_dd_pack.py --notify`, hỏi lại user với bộ cờ mới. Kiểm: `lag_dd_ack.py --gate <MÃ> --plan-date <D>` ⇒ `ACK_PROCEED`.
  Tuyệt đối không sửa tay `ack.json`, không lấy hash từ gói mới để "cho khớp".
- **NO_PACK ⇒ SKIP có hiệu lực NGAY khi merge**, trong khi hook 19:00 sinh gói CHƯA cài ⇒ ứng viên LAG mới
  đứng NGOÀI plan cho tới khi ai đó chạy `python3 mike/bin/lag_dd_pack.py [--signal-date D] --notify` (tay hoặc hook).
  Mùa BCTC: chạy trước 19:00 ICT mỗi ngày có ứng viên mới; gói quá 7 ngày so với plan_date ⇒ `PACK_STALE` (chạy lại).
  Gói <MÃ>_NA mới hơn gói có release thắng gói cũ (không dùng CLEARED cũ khi lần chạy mới nhất báo RELEASE_NA).
- **Không chạy `lag_dd_pack.py` vào T7/CN, trước 08:20, hoặc khi `ops_health_check`/`anomaly_scan` chết** (arch-review vòng 2): file anomaly cũ ⇒ ANOMALY_NA hàng loạt ⇒ gói CLEARED hôm trước bị hạ FLAG, `flags_hash` đổi ⇒ ack cũ thành ACK_STALE và phải hỏi lại user. `PACK_ASOF_MAX_DAYS=7`: kỳ nghỉ dài (Tết) chắc chắn ra PACK_STALE — chạy lại pack sau khi `anomaly_scan` đã chạy phiên giao dịch gần nhất.

- **Duyệt plan = chấp nhận (user chốt 2026-10-21 23:28 ICT, "Nếu tôi duyệt plan thì được phép mua. Không cần quá cứng")**: cổng DD KHÔNG chặn cứng ở tầng đặt lệnh (không thêm gate kiểu `filter_lag_rating_orders`). Khối 🔴 `LAG_DD_GATE_VIOLATION` trong báo cáo duyệt plan là cảnh báo để user thấy trước khi duyệt; user duyệt plan có khối đỏ ⇒ bot được mua như plan. Mã FLAG chưa ack vẫn mặc định đứng NGOÀI plan do DollarBill (fail-closed ở khâu lập plan); user muốn mua dù có cờ thì ghi ack PROCEED hoặc tự duyệt plan có mã đó.

## Rollback LAG cache điều chỉnh (`97b2a7197`, LIVE từ 10/11/2026, user phê chuẩn 13/11) — thêm 2026-11-13 (job `Taylor_20261113_021438`)
Khi nào: user/Mike quyết quay về cơ sở giá THÔ-append (vd validate fail nhiều ngày liền, BQ đổi điều chỉnh sai). Không chạm lệnh thật trực tiếp,
nhưng đổi ứng viên LAG ⇒ **làm trọn TRƯỚC 19:00 ICT** (chuỗi `bq_freshness_check.sh` 19:00 → golive đọc `earnings_events_classified.csv` + `pt_v22_dt5g_logs.csv`).
Không chạy cùng lúc cron 15:30 (`refresh_lagged_caches.py` có flock; thấy `lock bận` ⇒ chờ chain xong).
```bash
source /home/trido/thanhdt/WorkingClaude/wc_env.sh; cd "$WORKDIR_8L"
# BƯỚC 0 (CƠ HỌC, làm TRƯỚC mọi git revert): kiểm bản gốc rollback còn nguyên. Lệch ⇒ DỪNG, hỏi Taylor, KHÔNG revert.
printf '%s  %s\n' af4b8c1b72f4b133248516eff8b459b0 data/earnings_px.pkl.pre_adj afb2484e5fb702cd4335949d1a69db1b data/lagged_pos_ov.pkl.pre_adj | md5sum -c || { echo DUNG; exit 1; }
cd /home/trido/thanhdt && git checkout main
git revert --no-edit <commit-C2-nếu-đã-merge>   # nhánh feat/lag-cache-c2-20261113; thêm -m 1 NẾU C2 vào main bằng merge commit (ff/cherry-pick thì không); chưa merge thì bỏ dòng này
git revert --no-edit 97b2a7197                  # thử 13/11 trên main: sạch, không xung đột
cd "$WORKDIR_8L"
B=data/rollback_lagadj_$(TZ=Asia/Ho_Chi_Minh date +%Y%m%d); mkdir -p "$B"
cp -p data/earnings_px.pkl data/lagged_pos_ov.pkl data/lagged_carried.json "$B"/ && rm data/lagged_carried.json
for f in earnings_px lagged_pos_ov; do cp -p data/$f.pkl.pre_adj data/$f.pkl.rb_restore && mv data/$f.pkl.rb_restore data/$f.pkl; done
for s in refresh_lagged_caches.py pt_v12_macro.py pt_v4_dt5g.py pt_v22_dt5g.py "edge_health_monitor.py --refresh"; do
  $DNA_PYEXE $s || { echo "FAIL $s"; break; }; done
```
Kiểm sau: `refresh_lagged_caches.py` code cũ in `[1] earnings_px.pkl (daily Close)` + `+N rows -> ... new max <END>` (đường append) và exit 0; `lagged_pos_ov.pkl` không còn cột `Price` (helper `lag_adv_basis` đã bị revert cùng);
`pt_v22_dt5g_logs.csv` có dòng ngày hôm nay. Quá 19:00 ⇒ golive/plan ngày đó đã chạy trên cache adj: chạy lại chuỗi 19:00 + gửi lại plan (luật plan phải tới user trước ngày).
Không có knob env "append mode" — cố ý (giữ code cũ song song không tối thiểu; revert 1 commit đủ). Bối cảnh: `kb/projects/lag-cache-adjusted-20261110.md` §7.
