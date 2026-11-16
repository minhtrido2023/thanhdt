# AI-momentum P1-V3 — nới ngưỡng sự kiện ×2 (PREREG v3)

Job `Taylor_20261115_162439` · nhánh `research/ai-momentum-p1-20261115` (worktree `agents/Taylor/wt-ai-momentum-p1`) · **chưa merge, chưa cron, chưa chạy forward.**
User chốt 15/11 23:24 ICT (`decided_by: user`): phương án A. Thư mục: `agents/Taylor/research/ai_momentum_20261115/`.

## Làm gì
- `PREREG_v3.md` (+`PREREG_v3.md5`, khoá md5 cả `prereg_v3.json` và `events_v3.csv`): mom20≥0,15; idio20≥0,10; volr≥1,2; liq≥1 tỷ; giữ Close≥HI_3M_T1, universe_pit rv1, rating_8l≤4 as-of, cooldown 90 ngày+khác quý, hàng đợi 10/tuần. v3 thay v2 trước mọi lần chạy forward.
- `ai_momentum_daily.py`: tham số đọc từ `prereg_v3.json` (một nơi); fail-closed nếu md5 lệch; mọi dòng JSONL (kể cả `skipped_capacity`) mang `prereg_version`+`prereg_md5`; scorer chỉ đếm dòng đúng md5; thêm `T1_ticker_sensitivity` (bootstrap cụm theo mã + chênh trên sự kiện đầu mỗi mã) — mô tả, ngoài họ BH.
- Hoán vị khối tháng GIỮ; hoán vị trong-năm/trong-tháng CẤM (luật 12/11). Ngưỡng kinh tế T1≥5pp, T2≥8pp giữ nguyên. Không đề xuất đổi tham số nào khác.

## Số liệu (đo trong phiên)
- `build_events.py . qual_days_loose.csv events_v3.csv`: R4 **N=560 sự kiện, 321 mã, 26 tháng, 21,5/tháng** (6 tháng gần May–Oct: 12,3/tháng). 168/321 mã có >1 sự kiện (tối đa 4). Phân bố rating R4: 1:34, 2:69, 3:198, 4:259. ex20 TB +2,97% / trung vị −0,12%, P(ex20>0)=48,6%.
- **Hàng đợi 10/tuần (nhân quả theo ngày): cắt 86/560 = 15,4%**; tuần TB 5,3 sự kiện, tuần cao nhất **32**, 12/106 tuần vượt 10 ⇒ cắt dồn vào cụm (ngày 2025-07-28 có 13 ⇒ 3 bị bỏ).
- Power (`power_sim_directional_v3.out`, phân phối ex20 thật, NSIM=150 ⇒ ±~0,04): T1 Δ8pp/Δ12pp — p_dir=0,4: N_dir=80 → 0,73/0,99; N_dir=150 → 0,95/1,00. p_dir=0,3: 0,78/1,00; 0,96/1,00.
- Tháng tới N_dir=80 / 150 (chưa cộng ~3 tháng ex60; trong ngoặc = có cắt hàng đợi): nhịp TB 21,5, p_dir 0,4: **9,3 (11,0) / 17,4 (20,6)**; p_dir 0,3: 12,4 (14,7) / 23,3 (27,5). Nhịp 6 tháng gần 12,3, p_dir 0,4: **16,3 (19,2) / 30,5 (36,0)**; p_dir 0,3: 21,7 (25,6) / 40,7 (48,0). FINAL N_scored=250: 11,6 (13,7) tháng ở nhịp TB; 20,3 (24,0) ở nhịp gần.
- Look định nghĩa theo N_dir (L1=80, L2=150), FINAL = N_scored≥250 hoặc 24 tháng — **không đổi so với v2**, khoá lại trong v3 §3.
- Dry-run đối chiếu SQL (nguồn `ai_momentum_daily.py`, ngưỡng v3) vs `events_v3.csv` R4: **8/8 ngày khớp 100%** (`dryrun_v3_compare.out`: gồm ngày 13 sự kiện → 10 processed + 3 skipped, 2 ngày đúng 10, ngày 0 sự kiện, ngày gần nhất 2026-11-12).
- Selfcheck: **29 test, 33 mutant (33 killed), ALL PASS** dưới `env -u TZ`, `TZ=UTC`, `TZ=America/New_York` (`selfcheck_v3_*.txt`). Mutant mới: đổi từng ngưỡng sang giá trị v2, lệch cap, mất `prereg_version/md5`, bỏ khoá md5, scorer đếm dòng prereg khác, bỏ/lot sensitivity.

## Cảnh báo còn tồn
1. **N_dir vẫn có thể thấp**: p_dir=0,3–0,4 mới đo trên mẫu 10 (thô). Ở nhịp 6 tháng gần, L1 xong ~16–26 tháng (+3 ex60) — sát trần 24 tháng; **L2 không tới được** trong 24 tháng. Chỉ khi nhịp về TB dài hạn mới có kết luận. Đo p_dir thật sau 40 sự kiện xử lý.
2. **Phụ thuộc theo mã**: 168 mã lặp. p khối-tháng không bắt phụ thuộc trong-mã; sensitivity chỉ mô tả — nếu CI cụm-mã chứa 0 thì phải báo "không bền vững".
3. **Cụm theo thời gian**: cắt hàng đợi 15,4% dồn vào tuần bùng nổ (cùng thời điểm thị trường); sự kiện bị cắt không được chấm ⇒ nguy cơ lệch chọn nhẹ (chọn theo liq trong ngày).
4. **liq≥1 tỷ gồm mã kém thanh khoản** ⇒ **chỉ PAPER, không đề xuất thực thi/sizing**. Mã BANNED (vd HVN) vẫn vào sự kiện với `dd_flag`.
5. ~~M2 fail-open~~ → ĐÃ NỐI (P1-M2-WIRE, xem mục M2 bên dưới). M2 vẫn fail-open theo thiết kế: provider/model có thể bị gỡ lần nữa (đã xảy ra: `deepseek-v4-flash-free`) ⇒ theo dõi `m2_status=FAIL` hằng ngày; FAIL kéo dài = T3 mất mẫu. Model free của Zen: không SLA.
6. Hồi tố: v3 chọn theo outcome P0? Không — ngưỡng do user chốt dựa trên bảng N hợp lệ (chưa xem outcome forward); nhưng events_v3 hồi tố đã thấy ex20 ≈ 0 (trung vị −0,12%): không dùng để suy edge.

## Bước kế (không phải của tôi)
Mike: arch-review + quant-skeptic, rồi merge; cài cron chỉ sau khi Wags xong M2 và user duyệt.

## M2 — đã nối (P1-M2-WIRE, 2026-11-15)
- Nhánh vẫn `research/ai-momentum-p1-20261115`, đã `merge --no-ff wags/m2-wrapper-20261115` (không xung đột; không sửa `second_opinion.sh`). `m2_adapter()` gọi `bin/second_opinion.sh --raw-prompt-file P --out R --text-out T --timeout 240` (bin tìm theo root của chính worktree). Chi tiết thay đổi prompt: `PREREG_v3_1.md` (+dòng no-tool, +khung JSON; không đổi md5 khoá v3).
- Blind chạy trước, không nhận JSON M1; challenge nhận gói + JSON M1. Lỗi (exit 10/11/12/2, timeout, parse, schema, event_id) ⇒ `m2_status=FAIL`, fail-open (T1/T2 chấm, loại khỏi T3). Raw text M2 lưu trong ledger (`m2_raw`).
- **Chạy thật retro 2 sự kiện** (HID_2026-09-17, DXP_2026-10-12; `retro_run_v31/`, ledger retro riêng): lần 1 FAIL 2/2 vì deepseek bịa tên trường/enum (không có khung định dạng) + `validate()` ném KeyError với kiểu `boolean`; sửa; lần 2: **m2_status OK 2/2**. Thời gian cả sự kiện (M1 + blind + challenge + M1 phản biện): 138,8s và 109,1s (tổng 247,9s). Chi phí M1 (gồm phản biện): $0,0508 và $0,0382 (M2 free). Mô tả thô, N=2 vô nghĩa thống kê: blind vs M1 — driver khớp 1/2, view20 khớp 1/2; challenge nêu missed 8/3, disagree 3/2; không sự kiện nào đổi view sau phản biện (flip 0/2).
- Selfcheck: `selfcheck_ai_momentum.py` **36 test / 44 mutant (44 killed) ALL PASS** dưới `env -u TZ`, `TZ=UTC`, `TZ=America/New_York` (`selfcheck_v31_*.txt`); `bin/second_opinion_selfcheck.sh` PASS 17 check ×3 TZ trên nhánh hợp nhất.
- ⚠️ Cảnh báo M2: (a) model free có thể bị gỡ/đổi bất cứ lúc nào (Wags §1) ⇒ cron nên báo khi `m2_status=FAIL` liên tiếp; (b) wrapper retry nội bộ, một sự kiện FAIL có thể mất tới ~timeout×retry; (c) deepseek còn bịa nếu prompt đổi ⇒ giữ khung định dạng; (d) M2 không có WebSearch (opencode deny), M1 retro cấm WebSearch ⇒ cả hai chỉ dựa trên gói.

## P1-ARCH-FIX vòng 2 (job `Taylor_20261115_170852`) — sửa TRỌN BỘ 6 BLOCKER + 13 "làm sau" của arch-reviewer
Giao thức mới = **PREREG v3.2** (`PREREG_v3_2.md` + khoá `PREREG_v3_2.md5`: md5 11 file giao thức + `CONST_PROTOCOL` = hash lệnh M1 live/retro, model/timeout/retries M2, `FORMAT_HINT`, `NO_TOOL_LINE`, `HIST_DAYS`, `FRESH_RATIO`). Lệch/thiếu ⇒ `SystemExit`; bỏ mọi fallback `''/{}`. Mỗi dòng ledger mang `prereg_version=v3.2` + `prereg_md5` + `protocol_md5`; scorer + G-proc lọc theo `protocol_md5`. **Chưa merge master, chưa cài cron, chưa chạy forward.** Cron wrapper `bin/ai_momentum_cron.sh` đã viết (KHÔNG cài).

| # | Việc | Cách làm | Chứng cứ |
|---|---|---|---|
| B1 | Lỗi hạ tầng ≠ nội dung | `InfraError` (không có binary, timeout, rc≠0, stdout không phải JSON, `is_error` auth/usage/rate-limit) ⇒ dừng, KHÔNG ghi dòng, exit 5, không tính trần tuần. Schema/parse/ngày>T/max-turns ⇒ `m1_status=FAIL` | `t_infra_*`, `t_kill_resume_midday`; mutant FileNotFoundError: chạy lại sau khi "sửa" ghi đủ sự kiện |
| B2 | Lịch sử tất định | `sql_eligible_range` (T−200..T−1, cùng bộ lọc) + `replay_history` (greedy per-mã 90 ngày + khác quý, cap tuần replay) — không đọc ledger; seed `events_v3.csv` chỉ còn là tham số khoá | đối chiếu BQ vs `events_v3.csv` R4 (bên dưới) |
| B3 | Selfcheck provider | fixture `deepseek-v4.1-flash-free`; gỡ `ling-3.0-flash-free`, `nemotron-3-ultra-free` khỏi `kb/cli_providers.json` (không file nào tham chiếu) | `cli_provider_selfcheck.sh` 23/23; `dispatch_token_telemetry_selfcheck.py`: I6 ok, **I7 vẫn FAIL (lỗi có sẵn trên master, không sửa)** |
| B4 | Lệnh M1 live | `--tools WebSearch --allowedTools WebSearch --max-turns 8 --max-budget-usd 0.60` (retro: `--tools ""`, max-turns 2) | thử độc lập bên dưới |
| B5 | Exit code + wrapper | 3 không phải ngày GD (T7/CN + `trading_bot.vn_market.is_holiday`), 4 BQ chưa về/đầy, 5 hạ tầng M1, 6 đang có luật chạy khác (`.run.lock` flock -n), 1 lỗi thật. `bin/ai_momentum_cron.sh`: flock -n + timeout 5400s, im lặng trừ rc ∉ {0,3,4,6} / M1 FAIL>0 / M2 FAIL liên tiếp ≥3 ⇒ `notify_thread.sh` topic Momentum Lab | `bin/ai_momentum_cron_selfcheck.sh` 17 ca × (1 + 7 mutant) |
| B6 | Freshness đo độ đầy | `MAX(time)≥T` **và** số dòng T ≥ 95% phiên trước, cho `ticker` (≠VNINDEX) và `universe_pit` (rv1, in_universe); thông điệp nội suy từ số đo (bỏ chữ cứng "đợi sync 23:45") | `t_freshness_depth` + 4 mutant |

**Bẫy tìm thấy khi đo thật**: `bq query` coi câu SQL mở đầu bằng `--` là cờ (`Unknown command line flag`) ⇒ marker SQL dùng `/* ... */`.

### Kiểm chứng B2 (đo trong phiên, BQ thật)
`replay_history(sql_eligible_range(T), T)`, so greedy trong [T−100, T−1] với `events_v3.csv` R4:
- T=2026-11-13: 51/51 khớp · T=2026-08-14: 34/34 · T=2026-05-15: 46/46 · T=2026-02-13: **90/91 (BQ thừa 1: GEE 2025-11-27)** — hiệu ứng biên chuỗi cooldown của cửa sổ 200 ngày, đúng như PREREG v3.2 §1 đã khai.
- Ca 2026-11-13: ứng viên `CTD`, `TV1`; lịch sử BQ `CTD=[2026-11-12]`, `TV1=[2026-11-12]` — cả hai khớp `events_v3.csv` R4 (CTD và TV1 đều có sự kiện 2026-11-12) ⇒ cả hai bị cooldown chặn ở 13/11 ⇒ kế hoạch ngày 13/11 = 0 xử lý, 0 gọi M1.
- Khoảng 2026-11-13 → ngày cài cron: mọi ngày đủ điều kiện trong cửa sổ 200 ngày tính vào lịch sử dù chưa từng chạy M1 (`live` vẫn chỉ cho T=hôm nay).

### B4 — thử độc lập WebSearch ở chế độ `-p` (không ledger, không BQ)
Lệnh: `claude -p --model sonnet --effort medium --setting-sources "" --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --system-prompt <1 lần WebSearch> --tools WebSearch --allowedTools WebSearch --no-session-persistence --output-format json --max-turns 6 --max-budget-usd 0.60`, cwd tmp rỗng, prompt "Tin mới nhất về FPT?".
Đo: rc=0, **15 s**, `num_turns=2`, `total_cost_usd=$0,0328`, `is_error=false`; `modelUsage` có thêm `claude-haiku-5-5` (WebSearch chạy qua sub-model); kết quả trích tin ngày 4/11/2026 (nguồn Bloomberg) ⇒ **WebSearch chạy được ở `-p`**. ⚠️ `usage.server_tool_use.web_search_requests` báo 0 dù tìm thật ⇒ KHÔNG dùng trường này đếm lượt tìm; dùng `num_turns` + cost (đã thêm `num_turns`, `web_search_requests` vào `usage` của dòng ledger để đối chiếu). Ước lượng (1 lệnh, N=1): chi phí live M1 ≥ $0,03/sự kiện, 15–60 s.
**Smoke test live đầy đủ để Mike làm sau** (ledger tạm, không đụng production; cần 1 ngày giao dịch và BQ đã đầy):
`python3 agents/Taylor/research/ai_momentum_20261115/ai_momentum_daily.py --date $(TZ=Asia/Ho_Chi_Minh date +%F) --mode live --ledger-dir /tmp/am_live_smoke` (exit 3/4 = chưa phải ngày GD / BQ chưa đầy; thêm `--dry-run` để chỉ in kế hoạch).

### Làm sau (a–g) — đã áp
(a) khoá md5 + hash hằng số, bỏ fallback, `protocol_md5` mỗi dòng, scorer lọc theo nó · (b) T3 loại `m2_status≠OK` (`t_t3_only_m2_ok`) · (c) `--model opencode/deepseek-v4.1-flash-free --retries 1 --timeout 240`, trần ngoài `(retries+1)·timeout + 5 + 60 = 545s`; ledger ghi `m2_model`, `m2_log` (đuôi stderr wrapper), `m2_reason` kèm stderr; **không sửa `second_opinion.sh`**: `TMPDIR` trỏ vào thư mục tạm của adapter (dọn cùng lúc) + `start_new_session` + `killpg` khi quá trần ⇒ không rò `/tmp/so-raw.*`; SIGTERM handler để `timeout` giết vẫn dọn · (d) mutant có chuỗi đích không tồn tại làm harness FAIL (`HarnessError`, có mutant tự-kiểm), thêm test cho rating/fin/news ≤T, freshness stale, cooldown từ ngày trước, kill-resume giữa ngày, evidence date/event_id qua `call_m1`, argv M1, system prompt không rỗng · (e) M2 `blind.evidence`/`challenge.missed[].date` ≤ T · (f) xem dưới · (g) G-proc lọc `protocol_md5`; `sql_outcomes` dùng `V3["universe_ruleset"]`; `--ledger-dir` mặc định = `<repo root của worktree>/data/ai_momentum`; selfcheck dọn thư mục tạm của chính nó (`am_sc_*`); alias `sonnet` có thể trôi ⇒ model thực tế nằm ở `usage[].models` mỗi dòng (ghi trong PREREG v3.2 §3).

### Chính sách ledger / backup (f)
Ledger = `mike/data/ai_momentum/ai_momentum_events.jsonl` (+ `packets/*.json`, ~vài KB/sự kiện). `fleet_backup` dùng `git add -A` ⇒ **chấp nhận để ledger + packets vào backup git** (append-only, md5/dòng, cần cho audit). KHÔNG commit `*.lock`: thêm `*.lock` vào `.gitignore` của repo mike; gỡ `retro_run_v31/ai_momentum_retro.jsonl.lock` đã lỡ commit (`git rm --cached`). Dung lượng ước lượng (chưa đo): ≤ 10 sự kiện/tuần × ~30–80 KB (gói + raw M2) ≈ <1 MB/tuần; xem lại sau 1 tháng.

### Việc còn lại (không phải của tôi)
Mike: smoke test live bằng `--ledger-dir` tạm → arch-review vòng 3 → quant-skeptic → user duyệt cài cron (đề xuất 20:00/21:30/23:00 ICT, `bin/ai_momentum_cron.sh`). Không đụng I7 telemetry (có sẵn trên master).

### Selfcheck vòng 2 (đo, output thật trong `selfcheck_v32_*_{unset,UTC,NY}.txt`, chạy dưới `env -u TZ` / `TZ=UTC` / `TZ=America/New_York`)
- `selfcheck_ai_momentum.py`: **59 test, 81 mutant (80 killed, trong đó 3 bị khoá md5 bắt lúc nạp + 1 mutant tự-kiểm harness) ALL PASS** ×3 TZ. Mutant mới (v3.2): hạ tầng bị nuốt ở `call_m1`, FileNotFoundError không thành InfraError, rc≠0, `is_error` usage/auth, ghi dòng khi hạ tầng hỏng, replay bỏ luật khác-quý / đọc ngày T / bỏ cap tuần, cooldown không dùng lịch sử BQ, SQL range đọc đến T, exit code 4/5 lẫn, bỏ kiểm ngày giao dịch, bỏ `run_lock`, freshness chỉ MAX(time) / thiếu đếm dòng / không raise, rating-fin-news không giới hạn ≤T, M1 bỏ kiểm evidence date / event_id, M2 bỏ kiểm ngày ≤T / không truyền `--model` / không killpg / không TMPDIR / mất stderr, T3 gồm M2 FAIL, ledger mặc định trỏ canonical, `sql_outcomes` hard-code ruleset. Mutant có chuỗi đích không tồn tại ⇒ harness FAIL (không còn tính KILLED).
- `bin/ai_momentum_cron_selfcheck.sh`: **17 ca × (1 + 7 mutant, 7 killed) ALL PASS** ×3 TZ.
- `bin/second_opinion_selfcheck.sh`: **PASS** ×3 TZ. `bin/cli_provider_selfcheck.sh`: **23/23 PASS** ×3 TZ.
- `bin/dispatch_token_telemetry_selfcheck.py`: **42 ok; I6 ok; I7 FAIL ×2** (`bg done sau retry`, `retry_causes`) ở cả 3 TZ + crash `FileNotFoundError calls.txt` — theo Mike là lỗi có sẵn trên master, **tôi không tự kiểm lại trên master** và không sửa.


## R3 (job `Taylor_20261116_011145`, 2026-11-16) — 2 BLOCKER + C + D(a–f)
**A — freshness (đã thay B6).** Đếm thô dòng `ticker` T vs phiên trước từ chối dữ liệu đã chốt của thứ Hai (bảng tăng dần trong tuần rồi tụt thứ Hai). Nay đo độ đầy = tỉ lệ mã `universe_pit` (rv1, `in_universe`) của **phiên trước** có dòng `ticker` tại T (`pv_cov/pv_n ≥ 0,95`), giữ `MAX(time)≥T` cho cả 2 bảng + `universe_pit` có mã in_universe tại T (`up_n>0`). Ngưỡng 0,95 giữ (min đo được 0,988 bên dưới; reviewer đo min 0,982). **Đo BQ thật** (`selfcheck_v33_freshness_real_bq.txt`): 11-09 338/342, 11-02 335/339, 10-26 338/342 (thứ Hai) · 09-03 351/355 (sau lễ) · 11-10/11-11/11-12/11-13 (≥0,997) → tất cả PASS; T=2026-12-30 (tương lai) và T=2026-11-16 (chưa có dữ liệu) → `DataNotReady` (`MAX(time)=… < T`).

**B — `run_claude_m1`.** Parse stdout JSON TRƯỚC khi xét rc. JSON hợp lệ + `is_error`/rc≠0: khớp `INFRA_RE` ⇒ `InfraError`; còn lại (`error_max_turns`/`error_max_budget_usd`/is_error khác) ⇒ `RuntimeError` ⇒ `m1_status=FAIL`, ghi dòng, tiếp tục. `InfraError` chỉ khi không binary/timeout/không có JSON hợp lệ/khớp `INFRA_RE`/rc≠0 mà JSON không nói lỗi nội dung. Test rc=1+JSON max-turns / max-budget (RuntimeError), rc=1+max-turns nhưng result "usage limit" (Infra), rc=1+success (Infra) + 3 mutant. Chưa chạy `claude` live.

**C — wrapper.** rc=4 ở lượt BẮT ĐẦU từ 23:00 ICT (`AI_MOMENTUM_FINAL_HOUR`, giờ lấy lúc bắt đầu, `10#` chống bát phân) ⇒ alert topic `momentum_lab` + exit 0. `kb/discord_channels.json`: entry `momentum_lab` đổi id sang topic MỚI `1571694105111691406` (topic cũ `1571541823615406201` đã đóng).

**D.** (a) 14 mutant sống mới (rebuttal M1 nuốt Infra, `m2_ok` luôn True, `>`→`>=` ở `cooldown_ok` và `replay_history`, run_lock chỉ giữ lúc vào, blind nhận M1 qua packet, streak đếm cả retro, INFRA_RE bỏ overloaded / 529, SQL elig bỏ cửa sổ hiệu lực rating, `for c in skip` không ghi / ghi stats rỗng, SIGTERM không kill nhóm M2, không đăng ký nhóm, SQL sự kiện ra khỏi hash) + 3 mutant freshness; mutant SQL sự kiện bị **khoá md5 bắt lúc nạp** (đếm riêng) và có thêm assert cấu trúc SQL. (b) alert M2-FAIL chỉ khi đổi trạng thái OK→FAIL (`logs/ai_momentum/m2_alert.state`). (c) `_sigterm` kill nhóm `second_opinion.sh` đang chạy (`_M2_PGIDS`). (d) `CONST_PROTOCOL` nay băm cả van bản `sql_candidates` + `sql_eligible_range` ⇒ **`PREREG_v3_2.md5` dòng `CONST_PROTOCOL` cập nhật** `0b2d79ea…` → `0d3046fd…` (chưa có sự kiện forward nào; `PREREG_v3_2.md` không đổi byte; `protocol_md5` mỗi dòng = md5 file khoá nên đổi theo). (e) crontab mẫu bên dưới. (f) **chưa khai** lễ 2027.

**(e) crontab mẫu — KHÔNG cài** (host UTC; 20:00/21:30/23:00 ICT = 13:00/14:30/16:00 UTC; wrapper tự export `TZ=Asia/Ho_Chi_Minh`):
```
0 13 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/ai_momentum_cron.sh
30 14 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/ai_momentum_cron.sh
0 16 * * 1-5 /home/trido/thanhdt/WorkingClaude/mike/bin/ai_momentum_cron.sh
```
(T2–T6 theo UTC trùng T2–T6 ICT cho cả 3 mốc vì 16:00 UTC = 23:00 ICT cùng ngày.)

**(f) Lễ 2027.** `trading_bot/vn_market.py` (repo canonical, ngoài worktree này) chưa khai Tết Âm lịch / Giỗ Tổ 2027 và `data_registry` không có nguồn xác thực (thông báo chính thức Chính phủ/SGDCK/DNSE) cho danh sách ngày nghỉ 2027 ⇒ KHÔNG đoán. Hệ quả: đến khi khai, wrapper coi ngày lễ 2027 là ngày thường ⇒ BQ không có dòng T ⇒ rc=4 (im lặng, trừ khi trúng mốc 23:00 ⇒ alert). Việc cần làm trước 02/2027: có nguồn xác thực ⇒ khai `_VARIABLE_HOLIDAYS`.

### Selfcheck R3 (output thật `selfcheck_v33_*_{unset,UTC,NY}.txt`)
- `selfcheck_ai_momentum.py`: **70 test, 101 mutant (100 killed gồm 1 mutant tự-kiểm harness; 13 bị khoá md5 bắt lúc nạp) ALL PASS** ×3 TZ (`env -u TZ`, `TZ=UTC`, `TZ=America/New_York`; lưu ý mutant `today bo neo ICT` chỉ bị bắt khi TZ máy ≠ ICT — chạy dưới TZ=ICT sẽ sống, đây là tính chất của mutant, không phải lỗi mã).
- `bin/ai_momentum_cron_selfcheck.sh`: **23 ca × (1 + 12 mutant, 12 killed) ALL PASS** ×3 TZ.
- `second_opinion_selfcheck.sh`: SELFCHECK PASS ×3 · `cli_provider_selfcheck.sh`: 23/23 PASS ×3 · `dispatch_token_telemetry_selfcheck.py`: 42 ok, **I7 FAIL ×2 + FileNotFoundError calls.txt ×3 TZ — lỗi có sẵn trên master, không đụng**.

## R3.1 (Mike tự sửa 16/11 10:xx ICT, user duyệt (a) sau arch-review vòng 3 NEEDS_CHANGES — 2 MAJOR test-gap + 4 MINOR)
1. **MAJOR** md5 `sql_freshness("2000-01-03")` vào `event_sql_md5` (CONST_PROTOCOL đổi `950b6883…`; chưa có ledger ⇒ an toàn) + assert chặt `FROM pv JOIN tkT USING(ticker)`, không `LEFT`, `t.time = DATE "{T}"`; 3 mutant SQL freshness mới (LEFT JOIN / tkT T-1 / phiên trước=T) bị khoá md5 bắt lúc nạp.
2. **MAJOR** `bin/ai_momentum_cron_selfcheck.sh`: ca KHÔNG tiêm `AI_MOMENTUM_HOUR` (`NOHOUR=1`) — FINAL_HOUR=giờ ICT thật ⇒ 1 alert, giờ+1 ⇒ 0; mutant "bỏ export TZ" + "date -u" bị bắt.
3. `alert()` trả rc thật; state `m2_alert.state=FAIL` chỉ ghi khi notify thành công (ca test + 2 mutant).
4. `run_claude_m1` đọc `errors[]` (vào blob INFRA_RE + msg); +6 ca test (errors[] infra/max-turns, budget is_error=false, stderr-INFRA khi JSON không subtype, JSON không subtype + stderr lạ ⇒ nội dung, JSON list ⇒ Infra) + 4 mutant.
5. Câu alert mốc cuối nói rõ hạn **24:00 ICT** (qua nửa đêm `main()` tự retro) + test + mutant.
6. **Lịch cron thống nhất = 3 mốc 13:00/14:30/16:00 UTC (20:00/21:30/23:00 ICT)**; "19:35" cũ bị bỏ. Khi USER cài crontab phải thêm 3 dòng vào `kb/cron_registry.md` CÙNG COMMIT (§11) — Mike không tự cài.
Không đổi: lịch lễ `vn_market` (nợ cũ: 2026-01-02, 2026-04-27 coi là ngày GD nhưng BQ không có ⇒ ồn ào rc=4 lúc 23:00, chấp nhận).
