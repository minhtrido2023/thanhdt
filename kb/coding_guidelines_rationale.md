# Coding Guidelines — RATIONALE (câu chuyện gốc từng mục)

> **File này KHÔNG được auto-inject vào phiên của bất kỳ agent nào.** Nó là tầng 2 của
> `kb/coding_guidelines.md`: luật + cơ chế enforce sống ở file kia (được `@`-import mỗi phiên bởi
> Mike/Taylor/DollarBill/Mafee/Winston); **câu chuyện sự cố gốc** — diễn biến, bằng chứng, cách
> phát hiện, cái đã cân nhắc rồi bỏ — sống ở đây. Cùng tầng với `kb/incidents/`: đọc khi cần hiểu
> VÌ SAO một luật tồn tại, hoặc trước khi định sửa/gỡ một luật.
>
> Tách ra ngày **2026-08-08** (job `Taylor_20260808_053649`, user duyệt sau 3 vòng nén thất bại
> 2026-08-01 / 2026-08-03 / 2026-08-05: file đã tăng lên 48792 byte, vượt xa ngưỡng 40KB). Lý do
> nén hoài không xuể: `coding_guidelines.md` thực chất là một **sổ nhật ký bài học append-only** —
> mỗi bài học mới thêm narrative, không có gì co lại bao giờ.
>
> **Đánh số bám đúng `coding_guidelines.md`.** Mục nào có entry `kb/incidents/` riêng thì ở đây chỉ
> trỏ, không chép lại (nguồn chuẩn tắc là entry incident). Mục nào KHÔNG có entry riêng thì narrative
> đầy đủ nằm ở đây — đây là bản duy nhất, đừng xoá.

## Mục lục nhanh — narrative gốc nằm ở đâu

| Mục | Narrative đầy đủ ở đâu |
|---|---|
| Enforcement policy (header) | `kb/incidents/2026-08/2026-08-01-shellcheck-precommit-gate.md` + §header dưới đây |
| §5 Idempotent side effects | `kb/incidents/2026-07/2026-07-02-double-buy-concurrent-bot-execute.md` |
| §5b `MIKE_BOT_TEST_MODE` | **file này** |
| §6 Report provenance (cost basis) | `kb/incidents/2026-07/2026-07-03-weekly-report-estimated-cost-basis.md` |
| §6 Bright-line DNSE-vs-BQ (2026-07-09) | **file này** (`kb/INCIDENTS.md` là STUB REDIRECT, không chứa) |
| §7 Legacy/excluded holdings | **file này** (`kb/INCIDENTS.md` là STUB REDIRECT, không chứa) |
| §8 Canonical filename collision | **file này** |
| §9 data_registry check | **file này** (`kb/INCIDENTS.md` là STUB REDIRECT, không chứa) |
| §10 Archive superseded variants | `kb/incidents/2026-07/2026-07-11-fa-ratings-8l-silent-write-failure.md` |
| §11 cron_registry check | `kb/incidents/2026-07/2026-07-12-audit-cron-order-publish-cache-t1.md` |
| §12 Cross-account contamination | `kb/incidents/index.md` (3 entry: 2026-07-06, 2026-07-19, 2026-07-21) |
| §13 `.proposed` convention | **file này** |
| §14 Producer→consumer freshness | **file này** |
| §15 Bash quoting | `kb/incidents/2026-08/2026-08-01-shellcheck-precommit-gate.md` |
| §16 Timezone anchoring | **file này** |
| §17 Retention-tier readers | **file này** |
| §18 / §19 / §22 | các file `SKILL.md` tương ứng |
| §18b srcwalk | `kb/projects/srcwalk-benchmark-20260803.md` + **file này** |
| §20 `decided_by` | **file này** |
| §21 Cổ tức per-position | `kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md` + **file này** |
| §23 Selfcheck theo phạm vi | `agents/Taylor/research/test_suite_inventory_20260808.md` + **file này** |

---

## Header — Enforcement policy: vì sao "1 CI rule" > "1 dòng ghi chú"

Mandate user 2026-08-01: "đẩy bài học cũ ra công cụ/linter thay vì văn xuôi". Neo vào 2 nguồn
ngành:

- **Google SRE workbook**: action item tốt nhất của một postmortem là **1 CI rule**, không phải
  1 dòng ghi chú trong doc — ghi chú phụ thuộc vào việc người sau có đọc và có nhớ hay không.
- **Kỷ luật Semgrep**: "1 rule bắt đúng 2 lần còn hơn 1 rule bắt nhầm 200 lần" — **luôn test rule
  mới trên file thật trước khi bật**. Một rule ồn làm xói mòn niềm tin vào cả cái gate nhanh hơn
  là không có rule nào.

Hệ quả thực tế trong repo này: 2 rule đã được cân nhắc rồi **KHÔNG ship** vì trượt chuẩn trên
(§15 Semgrep cho §12; §16 lint `datetime.now()`), và 1 rule ĐÃ ship vì đạt chuẩn
(`bin/shellcheck_gate.sh`). Xem chi tiết ở từng mục.

---

## §5b — `MIKE_BOT_TEST_MODE=1`: 232 event giả trong 4 ngày, 4 lần tái diễn

**Root cause (4 lần tái diễn 2026-08-03/04/05/07, formal hoá retro 08-05, escalate retro 08-07):**
`trading_bot/executor.py::_publish_bot_event()` gọi THẲNG `mike/bin/append_event.sh Mafee ...` từ
6 chỗ (`GHOST_ORDER_DETECTED`, `LEVER_PACKAGE_UNAUTHORIZED`, `dcf-rich-fill`, `dd-redflag-fill`,
`STEP_FAIL`, `fill_lagging`) mà KHÔNG có guard môi trường → mọi selfcheck dựng `Executor` rồi chạy
qua các nhánh đó ghi event GIẢ vào bus production, gắn `agent_id` THẬT `Mafee`, làm nhiễu
`consolidate.sh`/KB/retro hằng ngày. Đo được **232 event giả** trong 4 ngày: 149
`LEVER_PACKAGE_UNAUTHORIZED` + 83 `dd-redflag-fill`.

**Vì sao phải là biến môi trường TƯỜNG MINH, không suy từ field sẵn có:** đã kiểm kê 3 ứng viên
(`account` label, `plan_date` sentinel 2099-*, `strategy="selfcheck"`) — cả 3 đều KHÔNG nhất quán
giữa các file selfcheck. `capit_lever_selfcheck.py` **CỐ Ý** dùng label THẬT `SpaceX`/`ZaloPay` để
cổng duyệt khớp production; `paper_main_window_selfcheck.py` dùng `plan_date=TODAY` thật. Chính sự
không nhất quán này là LÝ DO bug tái diễn qua các file viết độc lập bởi các phiên khác nhau.

**Vì sao `PYTEST_CURRENT_TEST` một mình không đủ:** `test_trading_bot.py` chạy dạng script
(`python test_trading_bot.py`, không có `def test_*`) nên pytest không đặt biến đó. Đừng giả định
"tên là test_ thì pytest lo".

---

## §6 — Bright-line DNSE-vs-BQ: sự cố 2026-07-09

⚠️ `kb/INCIDENTS.md` (pointer cũ trong `coding_guidelines.md`) đã thành **STUB REDIRECT** từ
2026-07-30 và KHÔNG chứa narrative này; cũng không có entry riêng trong `kb/incidents/index.md`
cho ca này. Bản dưới đây là bản duy nhất.

BQ (`tav2_bq.ticker`/`ticker_1m`) chỉ sync qua đêm (`sync_bq_cache_daily.sh`, 23:45 ICT). Một
truy vấn "hôm nay" chạy TRƯỚC lần sync đó **về mặt cấu trúc** đọc giá đóng cửa của HÔM QUA — không
phải lỗi ngẫu nhiên, không phải vấn đề độ trễ. Sự cố 2026-07-09: một plan generator định giá 2/4
lệnh bằng giá đóng cửa BQ cũ (lệch **+5.7%**) trong khi 2 lệnh còn lại dùng DNSE sống — cùng một
plan, 2 nguồn giá khác vintage.

Hệ quả về cách viết dispatch prompt: nêu thành MUST vô điều kiện kèm 1 ví dụ sai-vs-đúng cụ thể
(mẫu: prompt DollarBill trong `bq_freshness_check.sh`). Một câu nhắc chung chung "verify your
data" KHÔNG chặn được LLM với tay sang cái tên gần đúng nhất.

**Về pipeline 4 bước (§6 file luật):** phí giao dịch **0.075%** trên giá vốn thật là con số ĐÃ
SỬA ngày 2026-07-03 (trước đó dùng nhầm 0.1%); lãi margin **12.5%/yr** là con số user cung cấp,
**chưa đối chiếu hợp đồng DNSE**, nên phần dư sau khi trừ nó vẫn phải gọi là "ước lượng", không
phải "đã giải thích".

---

## §7 — Onboarding account có vị thế legacy: ca ZaloPay/DGC

⚠️ `kb/INCIDENTS.md` là STUB REDIRECT, không chứa narrative này.

Account ZaloPay được đưa vào quản lý khi ĐANG giữ sẵn một vị thế DGC mà bot không hề mua — vị thế
này nằm dưới hạn chế giao dịch của HOSE (lãnh đạo bị khởi tố), nên không được rebalance, không
được bán theo tín hiệu. Đây không phải ca cá biệt: các account tương lai đưa vào quản lý gần như
chắc chắn cũng có vị thế cũ tương tự, nên cơ chế phải tổng quát (`excluded_tickers` khai trong
config) chứ không phải một nhánh `if ticker == "DGC"` trong code.

**Vì sao phải size theo `active_nav` chứ không phải NAV tổng:** khi 1/3 vốn bị khoá trong một vị
thế excluded, sizing theo NAV tổng sẽ triển khai một lượng vốn KHÔNG tồn tại — plan sẽ đòi mua
nhiều hơn số tiền thật có. `bin/compute_active_nav.py` tính từ vị thế/giá LIVE của broker, KHÔNG
phụ thuộc journal thực thi của mình — khác `verify_account_snapshot.py`/`daily_nav_snapshot.py` vốn
cần lịch sử fill mà một vị thế có sẵn từ trước không hề có.

**Khe hở test-infrastructure cùng root cause, khác file:** `Executor.__init__` nạp `state.json`
từ đường dẫn MẶC ĐỊNH `(account, plan_date)` **trước khi** code test kịp trỏ nó sang tmpdir — một
file cũ còn sót từ lần chạy trước sẽ âm thầm làm hỏng trạng thái khởi đầu của lần chạy sau. Xem
comment `TAG` trong `ghost_order_selfcheck.py` cho pattern đúng.

---

## §8 — Sự cố ghi đè CSV pin R3 (2026-07-06)

Tên file output được dựng chỉ từ MỘT TẬP CON các knob env — cụ thể `BASKET_SELECT`/chế độ kết hợp
KHÔNG có suffix nào trong tên file — nên một thí nghiệm hợp lệ đã âm thầm ghi đè baseline
production đang được pin. **Một cái lock sẽ KHÔNG cứu được**: cả 2 lần chạy đều hợp lệ, chúng chỉ
va nhau ở đúng một cái tên file output.

Kết quả bị mất là `## KẾT QUẢ THAM CHIẾU phiên 2026-06-19` trong `data/results_registry.md` —
trích dẫn nó bằng **tiêu đề mục**, không bằng số dòng: số dòng trôi mỗi khi có entry mới chèn vào.

**Bẫy interpreter khi tái tạo baseline:** registry pin `$DNA_PYEXE`
(= `/home/trido/thanhdt/wc_venv/bin/python`, pandas 3), KHÔNG phải `python3` hệ thống — pandas 2.3
không unpickle được `data/earnings_surprise_data.pkl` (`NotImplementedError` trong
`NDArrayBacked.__setstate__`). Chép lệnh nguyên văn, đừng thay `python3` vào.

### §8b — vì sao snapshot `bq_cache_asof*` không tái tạo được

Chốt 2026-07-30 sau audit `fleet_housekeeping` (job `Wags_20260730_112912`). Mỗi snapshot ~**2,0GB**
và **không tái tạo được**: BQ time-travel đã tắt, còn `ticker`/`ticker_prune` bị TRUNCATE+rebuild
mỗi ngày — xoá sai = mất vĩnh viễn bằng chứng của một lần pin.

Ví dụ "mốc lịch sử đặc biệt" cụ thể: `bq_cache_asof20260728` là ảnh chụp TRƯỚC lần restate DT5G
2026-07-29, và là bằng chứng DUY NHẤT cho attribution **+0,47pp** CAGR do trôi dữ liệu. Không bao
giờ xoá theo tuổi. Nguồn: Taylor job `Taylor_20260729_155142`,
`agents/Taylor/research/asof_vintage_label_20260729.md`.

---

## §9 — SIGNAL_V11 base-leak (2026-07-11)

⚠️ `kb/INCIDENTS.md` là STUB REDIRECT, không chứa narrative này (chỉ có nhắc thoáng qua ở
`kb/incidents/retro/retro-2026-07-11.md`).

Bốn consumer production âm thầm đọc một bảng TRAP — bảng này ĐÃ được đánh dấu là trap trong
`CLAUDE.md`, nhưng **không có gì bắt buộc phải kiểm tra** trước khi một script mới chọn một cái tên
*nghe có vẻ đúng* — thay vì bảng regime production thật. Kết quả: một sổ paper-trading đang chạy
sống đã vào lệnh **6 mã** trên một tín hiệu giả.

Bài học cấu trúc: cảnh báo dạng văn xuôi ở một file khác (`CLAUDE.md`) không chặn được lỗi chọn
nguồn; thứ chặn được là một **registry phải tra** (`mike/kb/data_registry/`, 1 nguồn = 1 file, có
trạng thái `CANONICAL`/`TRAP`/`DEPRECATED`) + một câu lệnh grep cụ thể trong dispatch prompt.

---

## §13 — Vì sao "để uncommitted" KHÔNG phải cách giữ bản chờ duyệt (2026-07-30, 2 lần cùng ngày)

Dặn agent "sửa `kb/canonical.md` nhưng để CHƯA commit, chờ Mike đọc diff" — cả 2 lần
`bin/consolidate.sh` (cron mỗi giờ + tự trigger sau MỌI dispatch) quét `git add kb/` +
`commit -- kb/` **BLANKET**, cuốn bản sửa dở vào commit thường lệ trước khi Mike kịp đọc. Khi bị
cuốn, `publish_context.sh` xuất bản bản CHƯA duyệt kèm banner "đã duyệt" — cổng mở nhưng tự nhận
đóng.

**Phương án "hold-list" đã bị arch-reviewer BÁC BỎ:** `state/kb_pending_review.txt` + TTL +
pathspec exclude không đủ, vì `fleet_backup.sh` (00:00, `git add -A`) và `kb_nightly.sh` (02:00,
`git add kb/`) vẫn quét blanket **ĐỘC LẬP**, không biết gì về hold-list. Đo được **32,8%** job
dispatch rơi đúng khung giờ TTL không kịp cảnh báo trước khi một sweeper quét qua.

**Vì sao `.proposed` thắng:** nó không cần state file, không cần TTL, không cần lock — một file
`.proposed` mồ côi là vô hại. `kb_nightly.sh` chỉ cần `find kb/ -name '*.proposed' -mtime +1` để
nhắc dọn định kỳ, đó là lời nhắc chứ không phải gate.

**Chỗ 2 sự cố hôm đó bị hiểu nhầm:** "để uncommitted" bị đọc thành "sửa tại chỗ, đừng git commit",
trong khi mối nguy thật KHÔNG nằm ở thao tác git của agent mà ở các sweeper chạy nền.

---

## §14 — DT5G cron-order: 6 giờ đọc sớm, ẩn suốt nhiều tuần (2026-07-10)

Bus question gốc: `retro-pattern-recurring-dataprovenance-2`.

`daily_refresh_v34b` tính DT5G lúc 23:15, nhưng `bq_freshness_check` đọc nó lúc 17:30 — tức **6
giờ TRƯỚC** khi lần tính của ngày đó chạy, nên nó âm thầm đọc giá trị của HÔM QUA, mỗi ngày, không
sót ngày nào.

Đây KHÔNG phải lỗi nhầm nguồn BQ-vs-DNSE (luật §6 không phủ được ca này — DT5G không có nguồn
sống tương đương DNSE): đây là **2 cron job nội bộ đua nhau**, bị che giấu nhiều tuần bởi một
tolerance (`MAX_STATE_LAG=2`) đủ lỏng để không bao giờ trip trên một lần đọc trễ 1 ngày.

Failure mode tổng quát rút ra: *"code âm thầm tiêu thụ dữ liệu chưa sẵn sàng, được che bởi một
tolerance hoặc một giả định lịch chạy rộng hơn rủi ro thật."* `MAX_STATE_LAG=2` ngày chính là
anti-pattern cụ thể: nó phủ lên một lần đọc sớm 6 giờ mang tính CẤU TRÚC suốt nhiều tuần, chỉ vì
"chậm 2 ngày" nghe không có vẻ khẩn cấp.

---

## §16 — TZ: bug thật nhưng tiềm ẩn, chỉ lộ khi chạy tay (2026-07-31)

`bin/dt5g_writer_watch.py`: host chạy `Etc/UTC` (đã xác nhận bằng `timedatectl`), nhưng code đọc
`lastModifiedTime` của BQ bằng `datetime.fromtimestamp(ms/1000.0)` kèm một comment SAI khẳng định
"process TZ = ICT". Một lần ghi lúc 19:01 ICT bị dán nhãn "12:01", lệch 7h và trượt ra ngoài mọi
cửa sổ thời gian tính theo ICT.

**Vì sao nó không bao giờ nổ trên production:** các caller production đều `source wc_env.sh`
(export `TZ=Asia/Ho_Chi_Minh`) trước khi chạy script. Nó chỉ lộ ra khi Mike chạy code bằng tay
(không thừa kế `TZ`) và qua chính selfcheck của script chạy dưới `env -u TZ`. Đây là ví dụ mẫu cho
§19: một selfcheck thừa kế `TZ` đúng của chính tác giả thì PASS bất kể code đúng hay sai.

**Đã cân nhắc rồi KHÔNG ship:** một static lint gate bắt `datetime.now()`/`date.today()` thiếu
`tz=` — đo thật trên repo được **243 matches**, 0 bug sống trong số đó, và vài false positive
(kể cả chính dòng comment giải thích của nó). Cùng phán quyết với Semgrep-rule ở §12/§15. Thứ ship
thay thế: doc này + một dòng export `TZ=Asia/Ho_Chi_Minh` trong crontab (đóng khe hở env môi
trường) + thói quen "chạy đúng code path thật" của §14.

---

## §17 — Reader chỉ quét tier nóng (2026-08-01, audit kiến trúc fleet vs Paseo)

`mike_json.py`'s `trace`/`verify-coverage` chỉ glob `bus/inbox/*.jsonl` nóng — bất cứ thứ gì đã
qua ngưỡng archive (`kb_nightly.sh` Phase 1b2 = 30d cho bus event, `fleet_housekeeping.sh` Phase
1b3 cho `bus/jobs/`) bị đọc thành "not found" thay vì "archived".

Cùng hình dạng với bug check-#5 của `ops_health_check.sh` ngày 2026-07-31 (2 câu hỏi vô hình suốt
một tháng, đã fix qua `ops_health_check_selfcheck.py`) — **nhưng KHÔNG cùng cách sửa**.

**Đã đề xuất rồi BÁC BỎ:** một `conservation_check.py` tổng quát (count_before == count_after +
archived). Lý do bác: mọi mover hiện có ĐỀU đã bảo toàn số đếm, nên check đó sẽ không bắt được cả
2 bug. Khuyết tật nằm ở **từng READER**: reader NÀY — cái đang báo cáo trạng thái chưa giải quyết
để một con người ra quyết định — có quét mọi tier mà mover có thể đặt dữ liệu vào không?

**Ranh giới:** reader hot-only hiển thị "hoạt động gần đây" (mục "MỚI NHẤT" của `context_pack.md`)
là hot-only ĐÚNG THIẾT KẾ. Cũng đã bác bỏ việc viết lại archive-aware hàng loạt cho mọi bus reader:
`cmd_recent`/`cursor-advance` đúng là hot-only ("cái gì mới", không phải "cái gì còn nợ") — đổi
chúng là thay đổi hành vi không ai yêu cầu.

---

## §18b — srcwalk: bài học phương pháp quan trọng hơn kết luận (2026-08-03)

Bản §18b **đầu tiên** (sáng 2026-08-03) viết "srcwalk thay Read/grep làm mặc định" dựa trên **N=1
symbol và N=1 file** — đúng cái lỗi mà §18 và skill `quant-research` cấm (khai N là số sự kiện độc
lập, không phải số dòng dữ liệu).

Benchmark N=200 symbol + N=150 file chạy sau đó **bác bỏ đúng một nửa kết luận**: srcwalk thắng áp
đảo ở ĐỌC file, nhưng THUA grep ở TÌM. Kỷ luật "khai N + báo CI" áp cho cả quyết định về CÔNG CỤ
làm việc, không riêng backtest tài chính.

Số liệu + script tái lập: `kb/projects/srcwalk-benchmark-20260803.md`,
`agents/Mike/srcwalk_bench/`. Quy tắc hành động đầy đủ: `WorkingClaude/CLAUDE.md` § Code navigation.

---

## §20 — `decided_by`: self-verification tự lừa mình (2026-08-01, saga "coord-" vòng 5)

Vòng self-fix của Wags cho check #5 lập luận rằng "pool câu hỏi quá hạn có tỉ lệ tự rút = **0%**"
chính là bug nó đang sửa, rồi dùng "pool về 0" làm bằng chứng bản fix đã hiệu quả. arch-reviewer
bắt được mâu thuẫn: một phiên Mike đã đóng ~15 câu hỏi cũ trong một đợt dọn dẹp KHÔNG liên quan,
trùng thời điểm. **Không có gì trên event đóng ghi lại AI đã quyết định** — nên bước tự-xác-minh
không tài nào phân biệt được "dọn dẹp trùng hợp" với "cơ chế của bản fix đang chạy đúng".

Đây là bản tổng quát hoá của một rủi ro arch-reviewer từng nêu hẹp hơn ở vòng 2 (đừng để một CRON
tự hết hạn một quyết định đang thực sự chờ người) — cùng mối nguy khi một con người HOẶC một agent
tự đóng câu hỏi bằng phán đoán của mình, dù lập luận tốt đến đâu, mà user không xác nhận.

**Không ship:** enforce ở `append_event.sh` — sẽ đụng vào mọi caller trong fleet chỉ vì một field
chỉ có ý nghĩa với event đóng-câu-hỏi. Thay bằng convention + report của
`bin/bus_question_audit.py`.

---

## §21 — Cổ tức: lỗi đảo dấu một kết luận attribution (2026-08-02)

Ba báo cáo client-facing tháng 7/2026 (tuần 20-24, tuần 27-31, và báo cáo tháng 7) tính lãi/lỗ
từng mã bằng `(giá cuối kỳ − giá vốn)/giá vốn`.

**Cơ chế lỗi:** ngày chốt quyền (ex-date), giá sàn tham chiếu giảm **đúng bằng** cổ tức — giá trị
chuyển từ *giá cổ phiếu* sang *tiền mặt*. Công thức trên chỉ bắt phần giá, nên **báo lỗ oan** cho
mã trả cổ tức cao: NCT **−11,6% → −3,1%**, SAB **−8,1% → −1,7%**.

**Nghiêm trọng hơn con số:** lỗi này **đảo dấu một kết luận attribution** — rổ CAPIT bị mô tả là
"chỉ gánh 2,6% mức lỗ" trong khi thực tế rổ đó **LÃI +5,66tr**.

**Vì sao lỗi sống sót lâu:** NAV tổng vẫn ĐÚNG (tiền cổ tức đã nằm trong `totalCash`), nên mọi
phép đối soát NAV đều PASS. Đây là ca kinh điển "tổng đúng nhưng attribution từng dòng sai" —
cùng họ với §6.

Chi tiết cơ chế, 4 cái bẫy cụ thể và cách kiểm chứng bằng 3 nguồn độc lập:
`mike/kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md`.

---

## §23 — Kiểm kê bộ selfcheck 2026-08-08: 9 FAIL, 0 regression thật

Job `Taylor_20260808_035850` đã **CHẠY THẬT** cả 51/51 selfcheck ở repo root. Báo cáo đầy đủ:
`agents/Taylor/research/test_suite_inventory_20260808.md`.

Kết quả: chạy hết mất ~5 phút *cộng* 3 lần timeout BQ 150s, trả về **9 FAIL**, trong đó **0 là
regression code thật**:
- **6 ca** assert lên trạng thái SỐNG đã đổi (rổ due-diligence, số đếm `universe_pit`, file plan
  production),
- **2 ca** harness tự gãy,
- **1 ca** môi trường.

Vì vậy chạy cả bộ cho một sửa đổi 3 dòng vừa tốn kém vừa **vô ích**: 9 đèn đỏ nền làm một
regression thật lẫn vào nhiễu, không ai phân biệt nổi.

**Về `test_*.py` ở repo root:** 165 file, thực chất là script backtest/R&D được đặt tên theo lịch
sử, **154/165 không đụng từ 2026-06-21**. Không archive chúng (là artifact nghiên cứu, đúng §10
mục 4) nhưng cũng đừng bao giờ gộp vào "chạy bộ test".
