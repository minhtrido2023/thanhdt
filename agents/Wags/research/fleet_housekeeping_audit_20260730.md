# Audit rác/file tạm toàn hệ thống + thiết kế cơ chế dọn dẹp

**Job**: `Wags_20260730_112912` · **Ngày**: 2026-07-30 · **Loại**: AUDIT + DESIGN
**KHÔNG file nào bị xoá/di chuyển trong lần chạy này.** Script chỉ ở dạng nháp `.draft`, chưa
executable, chưa đăng ký cron.

> **Bản v2 — đã qua arch-review (verdict NEEDS_CHANGES, confidence high), đã sửa xong.**
> Reviewer bác bỏ 2 điểm THẬT và tôi đã đo lại xác nhận cả hai:
> 1. **Killer**: category `empty` xoá mất **6 file 0-byte là bằng chứng DUY NHẤT** (không job
>    record hot lẫn archive, không bus event, không KB; `logs/` lại `.gitignore`). Đúng lớp lỗi tôi
>    đã tự bắt ở `jobtmp` nhưng **quên áp cùng guard** — và 2 trong 6 file đó chính là mẫu ở §2.3
>    do tôi tự đo. → đã áp guard, dry-run nay GIỮ đủ 6/6.
> 2. **Số sai trong chính báo cáo này**: §3.3 khẳng định "không phải ước tính, là output dry-run
>    thật" nhưng dòng `datacold` lại là số của ngưỡng **>30d** trong khi script chạy **>60d** —
>    thật chỉ **188 file / 42,26 MB**, không phải 671 file / 0,72 GB (**phóng đại ~18 lần**).
>    → category `datacold` đã bị **gỡ hẳn**, các số dưới đây đã đo lại toàn bộ.
>
> Chi tiết 12 thay đổi + số trước/sau: **§6**. Số ở §0–§3 dưới đây là **bản đã sửa**.

---

## 0. Kết luận điều hướng trước (đọc 30 giây)

| Câu hỏi | Trả lời thật |
|---|---|
| Hệ thống có đang "nặng nề" vì rác fleet không? | **Không, về disk.** Sau khi thu phạm vi `pycache` về đúng fleet (mike/ + trading_bot/), toàn bộ rác thật ≈ **0,86 MB**. `mike/logs` chỉ 17 MB, `mike/bus` 9,7 MB. (Con số 20,3 MB ở bản v1 là do quét cả `WorkingClaude/stockquery` — app **ngoài** phạm vi fleet, 219/250 dir.) |
| Vậy vấn đề thật là gì? | **HAI vấn đề khác nhau, đừng trộn:** (1) **Token**: `ls data/` = ~19K token, `ls mike/logs/` = ~17K token — đây đúng là lo ngại của user và có thật. (2) **Disk**: `/` đang **91% (13 GB trống)** — nhưng nguyên nhân KHÔNG phải fleet. |
| Ai chiếm disk? | `/workspace/kaffa_v2` = **45 GB**, owner `hainguyen`, **không thuộc fleet/trading**. Toàn bộ `/home/trido/thanhdt` (cả WorkingClaude + mike) chỉ 13 GB. |
| Cơ chế dọn dẹp đã có chưa? | `bus/` **ĐÃ CÓ và đã xác minh chạy đúng** (kb_nightly Phase 1b/1b2/1b3/1c, Wags làm 2026-07-27). `logs/` **KHÔNG CÓ GÌ** — 0 cơ chế. `WorkingClaude/data` **KHÔNG CÓ GÌ** ngoài quy ước thủ công. |
| Rủi ro lớn nhất nếu dọn sai? | Một cron "xoá log > N ngày" nhìn vô hại nhưng **`mike/logs` và `mike/bus` đều bị `.gitignore`** ⇒ **không có bản backup GitHub nào**. Xoá = mất vĩnh viễn. Và **1/3 dispatch log cũ KHÔNG có bản tóm tắt nào trên bus/KB** (đo thật, xem §2.3). |

**Đề xuất ưu tiên**: làm phần token (archive theo file-count) vì nó rẻ và đúng lo ngại của user;
**đừng** dùng housekeeping fleet để "giải quyết" 91% disk — nó không giải quyết được, và áp lực
disk sẽ đẩy sang xoá bằng chứng. Vấn đề 91% cần 1 quyết định riêng của user về `/workspace` (§5).

---

## 1. Kiểm kê theo từng danh mục

### 1.1 `mike/logs/` — **KHÔNG CÓ CƠ CHẾ DỌN DẸP NÀO**

Tổng: **17 MB / 3080 file** (1928 file hiện, 1153 file ẩn `.pid`).

| Lớp file | Số file | Dung lượng | >7d | >14d | >30d | Kết luận |
|---|---|---|---|---|---|---|
| `.dispatch_*.pid` (ẩn) | 1153 | 9,1 KB | 1058 | — | — | **RÁC THẬT** — 0 reader (§2.1) |
| `*.err` rỗng 0 byte | 247 | 0 B | — | — | — | **RÁC THẬT** |
| `*.err` chỉ chứa warning boilerplate | 25 | 3,9 KB | — | — | — | **RÁC THẬT** (đã đọc nội dung, §2.2) |
| `*.err` có nội dung thật | 8 | 2,3 KB | — | — | — | GIỮ |
| `*.log` rỗng 0 byte | 66 | 0 B | — | — | — | **RÁC THẬT** |
| `dispatch_*.log` | 1294 | 1,7 MB | 1178 | 1007 | 668 | **ARCHIVE** (không xoá — §2.3) |
| `run_bot_*` (SpaceX/ZaloPay/main + autoheal) | 151 | 0,1 MB | — | 69 | **0** | GIỮ HOT (bằng chứng thực thi bot) |
| `verify_*`, `arch_review_*`, `wags_pipeline_*` | 294 | ~1 MB | — | — | 2 | ARCHIVE dần |
| Log cron dài (`discover.log` 1,6M, `notify.log` 880K, `watchdog.log` 452K…) | ~30 | ~4 MB | — | — | — | **CẦN ROTATE** — append vô hạn, chưa ai rotate |

Phân bố tuổi toàn dir: `>7d = 2727 (88%)`, `>14d = 2246`, `>30d = 1405`, `>90d = 0` (log cũ nhất
24/06 — khớp số Mike đo).

**Xác minh "không có cơ chế"**: `grep -rlE 'mtime \+|rm -rf|gzip|tar czf' bin/` chỉ ra
`kb_nightly.sh` + `paper_late_feeds.sh`, và không dòng nào trong `kb_nightly.sh` chạm `logs/`.
Không có `logrotate` config cho fleet. Crontab 64 dòng, 0 dòng housekeeping.

**Cảnh báo đã kiểm tra và loại trừ**: grep thấy các tên `exec_{account}_journal.csv`,
`nav_history_{account}.csv`, `dnse_raw_*.jsonl`, `verified_snapshot_*.json` — nghe như sổ lệnh nằm
trong `mike/logs/`. **Đã xác minh: KHÔNG.** Chúng nằm ở `$WC_ROOT/data/execution_logs/`
(`bin/bot_heartbeat.sh:27`, `bin/ops_health_check.sh:109`). Trong `mike/logs/` chỉ có 2 file tên
`eod_*` và cả hai là log text. ⇒ Quy tắc cho `mike/logs` không chạm sổ lệnh. Nhưng đây chính là
loại nhầm lẫn khiến 1 rule "xoá logs/*" thành thảm hoạ, nên ghi lại ở đây.

### 1.2 `mike/bus/` — **ĐÃ CÓ CƠ CHẾ, ĐÃ XÁC MINH CHẠY ĐÚNG** ✅

Tổng 9,7 MB. Cơ chế do Wags cài 2026-07-27 (`kb_nightly.sh`, commit 3ce951e→91c934e):

| Phase | Làm gì | Ngưỡng | Xác minh thực tế |
|---|---|---|---|
| 1b | Xoá heartbeat cũ khỏi `bus/inbox/*.jsonl` | 3d | ✅ chạy 07-29T19:00Z, removed 29 |
| 1b2 | Archive MỌI event-type cũ → `bus/inbox/archive/<id>_<YYYY-MM>.jsonl.gz` | 30d | ✅ moved 18 |
| 1b3 | Archive job record terminal → `bus/jobs/archive/` | 30d | ✅ moved 8 |
| 1c | Archive working-memory entry đã đóng | 14d | ✅ NOOP (0 đủ điều kiện) |

Hiện trạng: `bus/inbox` 3,3 MB / 10 file hot (Taylor 1,4 MB lớn nhất); `bus/inbox/archive` 220 KB;
`bus/jobs` 630 hot + **618 đã archive**; `bus/jobs/archive` 2,5 MB.

**Kiểm chứng nghi vấn "prune không chạy"**: đếm thấy còn 169 heartbeat cũ hơn 3d và 28 event cũ hơn
30d trong file hot. **Đây KHÔNG phải lỗi** — cutoff tính tại thời điểm chạy (07-29T19:00Z), các
event rơi vào khung 07-26T19:00→07-27T18:30 mới vừa "quá hạn" sau đó; 07-27 đúng là ngày Wags/Taylor
hoạt động cực nặng. Đêm nay sẽ dọn. ⇒ Cơ chế hoạt động đúng thiết kế, chỉ có lag ≤1 ngày.

**Gap duy nhất của bus**: `bus/registry/` **352 file / 1,4 MB, 310 file >7d, 70 file >30d — không
phase nào chạm tới**. `bus/directives/` 6 file nhỏ, tĩnh từ tháng 6, để nguyên.

**3 file `bus/jobs/*.json.tmp`** (885 B, `Winston_20260628_053145`, `Mafee_20260627_105458`,
`Taylor_20260628_053125`) — sót lại từ atomic-write bị kill ngày 27–28/06.

> 🔴 **ĐÍNH CHÍNH (tự bắt được khi dry-run script):** ban đầu tôi xếp 3 file này là "RÁC THẬT vì
> job record thật đã tồn tại bên cạnh". **SAI.** Guard trong script giữ lại, kiểm tay thì
> **không có bản `.json` nào ở `bus/jobs/` lẫn `bus/jobs/archive/`** ⇒ 3 file `.tmp` này là **dấu
> vết DUY NHẤT** của 3 job đó (bị truncate giữa dòng `prompt_summary`, `status` còn `"running"`).
> ⇒ **BẰNG CHỨNG PHẢI GIỮ, không xoá.** Category `jobtmp` hôm nay ra **0 mục** (đúng như mong đợi).
> Bài học ghi vào script: điều kiện "đã có bản đầy đủ ở nơi khác" phải KIỂM, không suy ra từ hậu tố
> `.tmp`. (Chúng không gây nhiễu `jobs.sh` vì `mike_json` glob `*.json` không khớp `*.json.tmp`.)

### 1.3 `mike/agents/*/exp_*`, `probe_*`, `research/`

| Agent | Tổng |
|---|---|
| **Taylor** | **282 MB** |
| Winston | 228 KB |
| Mafee | 120 KB |
| Spyros | 64 KB · Mike 60 KB · DollarBill 44 KB · Wags 32 KB · Wendy 24 KB |

⇒ Chỉ Taylor có khối lượng. 22 dir `exp_*`/`probe_*`; lớn nhất `exp_pb_exvic` 105 MB (20 file),
`research/` 57 MB (125 file), `exp_valframe` 34 MB, `exp_roe` 21 MB, `exp_insider` 16 MB.

**Kiểm tra citation (grep thật, không đoán)** — mỗi dir đối chiếu với `kb/INCIDENTS.md`,
`kb/current_ops.md`, `kb/canonical.md`, `kb/events_buffer.md`, `kb/KNOWLEDGE.md`,
`data/results_registry.md`, `bus/inbox/*.jsonl`:

- **20/22 dir được trích dẫn ≥1 nơi** ⇒ bằng chứng đang có hiệu lực.
- `exp_valframe` (34 MB) tra theo tên dir = 0 hit, nhưng grep partial `valframe` **CÓ** hit ở
  `agents/Taylor/research/fundamental_valuation_framework_20260729.md` ⇒ vẫn là bằng chứng.
- `probe_real_premium_20260713.py` (4 KB) = 0 hit — file script lẻ, quá nhỏ để đáng động.

⇒ **Toàn bộ `exp_*`/`probe_*` của Taylor = BẰNG CHỨNG PHẢI GIỮ.** Điều này khớp đúng
`coding_guidelines §10 mục 4` (không archive artifact audit-trail đã namespace vào dir experiment).

**Nhưng phát hiện 1 vấn đề khác, quan trọng hơn kích thước:**

> ⚠️ **`mike` repo ĐANG TRACK 279 MB CSV/pkl/parquet experiment trong git.**
> `git ls-files agents/Taylor` = 650 file, 293 MB. Blob lớn nhất: `exp_pb_exvic/t100_panel2.csv`
> 44,2 MB, `t100_panel.csv` 44,0 MB, `research/exit_signal_backtest_20260721/panel_c30v.pkl`
> 38,6 MB, `exp_valframe/panel150.parquet` 28,8 MB.
> `git count-objects -vH`: **loose 212,81 MB** / pack 26,97 MB ⇒ đúng là nguồn của `.git` 242 MB.
>
> Đối chiếu: repo ngoài (`/home/trido/thanhdt/.git`) **có** `.gitignore` chặn
> `*.csv *.tsv *.pkl *.parquet *.jsonl *.npy` với comment "regenerable from BigQuery". Repo `mike`
> **không có** rule tương ứng. ⇒ mỗi lần Taylor sửa 1 panel 44 MB, git tạo blob mới ⇒ `.git` phình
> **một chiều, không bao giờ giảm**, và **backup GitHub hằng ngày 00:00 ICT đẩy toàn bộ khối này**.
>
> `du` hiện tại chỉ 282 MB nhưng `.git` đã 242 MB — tỉ lệ 1:0,86 sau ~1 tháng. Đây là thứ sẽ
> "làm hệ thống nặng nề" theo đúng nghĩa user lo, chỉ là ở chỗ không ai nhìn.
>
> **Đây là quyết định vượt quyền Wags** (đổi chính sách git của repo fleet + có thể cần
> `git gc`/rewrite history) ⇒ escalate, §5 mục B.

### 1.4 `WorkingClaude/data/` — **KHÔNG CÓ CƠ CHẾ**

Tổng **11 GB**. Trong đó:

| Mục | Dung lượng | Ghi chú |
|---|---|---|
| `bq_cache/` (live) | 2,0 GB | cache đang dùng, mtime hôm nay |
| `bq_cache_asof20260728/` | 2,0 GB | **snapshot vintage cố ý ghim** (mốc TRƯỚC restate DT5G) |
| `bq_cache_asof20260729_postrestate/` | 2,0 GB | **snapshot vintage cố ý ghim** (số pin R3 hiện hành) |
| `archive/` | 369 MB | đã là dir archive đúng chuẩn, có `README.md`; 1 file `ticker_prune_monolith_frozen_20260626.parquet` 385 MB |
| `execution_logs/` | 116 MB | xem §1.6 |
| `intraday_1m/` 90 MB · `snapshots/` 69 MB · `fa8l_exp/` 54 MB · `qsleeve_logs/` 15 MB · `f3_exp/` 14 MB · `momdeal_exp/` 7,6 MB | | dir experiment/cache đã namespace |
| `_quarantine/` | 1,6 MB | 3 file FROZEN + README — đã đúng pattern, để nguyên |
| **File lẻ ở `data/` (maxdepth 1)** | **3,74 GB / 2041 file** | **đây là chỗ tốn token nhất** |

Phân bố tuổi file lẻ: `>7d = 1904 file / 3,50 GB`, `>30d = 1605 / 3,05 GB`,
`>60d = 821 / 1,50 GB`, `>90d = 33 / 0,12 GB`.

**Cross-reference (đo thật)**: lấy 1355 basename file `>30d` (csv/pkl/parquet/json/log), grep đối
chiếu với corpus 6919 file `.py/.sh/.md/.json/.txt` của cả `WorkingClaude` + `mike` (46 MB text):
- **684 file CÓ tham chiếu** trong code/doc.
- **671 file KHÔNG tìm thấy tham chiếu literal nào — tổng 0,72 GB.**
- Lớn nhất trong nhóm không tham chiếu: `ticker_prune_O1M_all.csv` 35 MB (89d), rồi ~20 file
  `v23_golive_audit_..._park3-70_4-70_...nav500B.csv` ~4,5–5 MB mỗi cái (42–46d) = output sweep
  grid tham số, đúng chuẩn §8 (có suffix experiment).
- Giao với `>60d`: chỉ **221 file / 0,08 GB** ⇒ phần lớn khối "không tham chiếu" là experiment
  30–60 ngày, tức **còn mới, có thể còn đang dùng**.

> ⚠️ **Giới hạn của phép đo này, phải nói rõ**: grep basename literal **KHÔNG** bắt được filename
> sinh động (f-string, `OUT_CSV=` env, ghép suffix từ biến). Đúng theo `§10 mục 1` ("never archive
> on a name-similarity guess alone") ⇒ **"không tham chiếu" ở đây KHÔNG đồng nghĩa "an toàn xoá"**.
> Nó chỉ là danh sách candidate để *archive có thể đảo ngược*, và mặc định phải là nén-tại-chỗ
> hoặc di chuyển, tuyệt đối không delete.

**Rác thật tìm thấy**: 8 file `.bak` (`VNINDEX.csv.bak` 294 KB, `breadth_data.csv.bak` 58 KB, 6 file
`*_monthly.csv.bak` ~3,7 KB) — nhưng `.bak` chính là bản backup thủ công, **không xoá tự động**,
chỉ nêu để user biết.

**Quy tắc giữ snapshot `bq_cache_asof*` — ĐÃ CÓ, nhưng CHỈ NẰM TRÊN BUS, chưa được codify:**
Taylor ghi rõ (finding 2026-07-29T16:34:40Z, `Taylor_20260729_155142`):
> "số pin CHÍNH THỨC hiện hành (R3) giữ thêm 1 snapshot cache đầy đủ ~2,0GB **xoay vòng** khi
> re-pin; mốc lịch sử đặc biệt giữ riêng […]. **Xoá snapshot cũ CHỈ SAU khi số pin mới qua
> quant-skeptic.**"

Hiện trạng **đúng chính sách**: 1 bản xoay vòng (`asof20260729_postrestate` = pin R3 hiện hành) +
1 mốc lịch sử (`asof20260728` = bằng chứng attribution trước restate). **Không có bản dư.**
Và finding r3-repin còn ghi `"trang_thai": "CHỜ quant-skeptic"` ⇒ **hiện tại chưa file nào đủ điều
kiện xoá.** Rủi ro user lo ("mỗi lần re-pin lại +2 GB") là thật nhưng đã có chính sách; gap là
chính sách nằm trong 1 bus event sẽ trôi khỏi KB, **không nằm trong
`coding_guidelines §8` hay `kb/data_registry/`** ⇒ đề xuất codify, §5 mục C.
Lưu ý kỹ thuật Taylor đã ghi: snapshot là **bản sao THẬT, không hardlink được** (sync ghi đè inode)
⇒ không có mẹo tiết kiệm chỗ, mỗi bản đúng 2,0 GB.

### 1.5 `WorkingClaude/sql_queries/` — tự ghi đè, KHÔNG tích luỹ ✅

47 MB / 56 file, trong đó 27 file `.csv` = 46,7 MB. **Cả 27 file đều >90 ngày** ⇒ đây không phải
cache tích luỹ mà là kết quả 1 lần chạy `gen_sql.py` cũ, mỗi strategy 1 file cố định tên
(`buy_*.sql`/`.csv`), lần chạy sau **ghi đè** chứ không thêm bản mới. Số file không tăng.
⇒ **Không phải nguồn phình.** `ls` chỉ 261 token. Không đề xuất động (nén được ~35 MB nếu cần chỗ,
nhưng `gen_sql.py` sẽ ghi lại `.csv` không nén ⇒ churn vô nghĩa).

### 1.6 `WorkingClaude/data/execution_logs/` — 🔴 COMPLIANCE, KHÔNG ĐỀ XUẤT XOÁ GÌ

116 MB / **310 file**: 134 `.json`, 64 `.csv` (sổ lệnh `exec_*_journal.csv`), 39 `.lock`,
37 `.md`, 27 `.jsonl` (`dnse_raw_*`), 7 `.txt`, 2 `.flag`.
Tuổi: **chỉ 3 file >30d, 0 file >90d** ⇒ dir này **hầu như toàn bộ là dữ liệu nóng của 30 ngày
gần nhất**, dùng chung nhiều account (SpaceX/ZaloPay/main).

**Kết luận: KHÔNG có gì để dọn ở đây.** Không có rác, không có file cũ đủ để nén có ý nghĩa
(3 file). Đề xuất duy nhất: **để nguyên hoàn toàn**, và ghi vào script 1 **deny-list cứng** để mọi
category sau này không bao giờ quét trúng đường dẫn này. `ls` = 2695 token, chấp nhận được.

*(Nhắc lại giới hạn quyền: đây là audit trail tài chính; nếu sau này thật sự cần nén file cũ, phải
hỏi user + Wendy/Spyros về nghĩa vụ lưu trữ trước, không phải quyết định của housekeeping.)*

### 1.7 Pattern khác quét được

| Phát hiện | Số lượng | Đánh giá |
|---|---|---|
| `__pycache__/` | **251 dir / 26 MB** | **RÁC THẬT** — regenerable theo định nghĩa, đã `.gitignore` cả 2 repo |
| `*.json.tmp` mồ côi trong `bus/jobs/` | 3 / 885 B | **RÁC THẬT** (§1.2) |
| `*.bak` trong `data/` | 8 / 366 KB | backup thủ công — nêu thôi, không tự động động |
| `core dump` | **0** | sạch |
| File trùng lặp >20 MB (cùng size) trong `data/` | **0** | sạch |
| `/tmp` | 1,5 GB, **0,92 GB >7d** | có `eyrisk_sc_*` 67+65+65 MB, `Kronos_src` 26 MB, `pytest-of-trido` 27 MB. Dùng chung nhiều user ⇒ **không đưa vào script tự động**, nêu để user biết |
| `~/.cache/pip` | **703 MB** | cache thuần, `pip cache purge` an toàn 100%, không mất bằng chứng nào |
| `~/.cache/uv` 110 MB, `huggingface` 110 MB | 220 MB | cache thuần |
| `~/.claude/projects` (transcript phiên) | **717 MB** (Mike 306 MB, Taylor 211 MB) | dữ liệu harness, **ngoài quyền fleet**, không đề xuất động |
| `~/backup_thanhdt` | **5,5 GB**, đóng băng 2026-06-21 (39 ngày) | bản backup thủ công cũ; **win disk lớn nhất trong `/home`** nhưng cần user quyết |

---

## 2. Phân loại: RÁC THẬT vs BẰNG CHỨNG PHẢI GIỮ

### 2.1 RÁC THẬT — `logs/.dispatch_*.pid` (1153 file) — bằng chứng grep

```
$ grep -rn '\.pid' --include='*.sh' --include='*.py' --include='*.md' mike/ | grep -v '\.git/'
bin/dispatch.sh:753:  echo "$pid" > "$ROOT/logs/.dispatch_${id}_${ts}.pid"
agents/Taylor/insider_flags.py:67,68   ← cột `x.pid` trong SQL BigQuery, KHÔNG liên quan
```
**1 dòng WRITE duy nhất, 0 dòng READ trong toàn repo.** Không watchdog, không reap, không
`jobs.sh`, không hook nào đọc. Đây là file được ghi ra rồi không ai dùng ⇒ rác thuần.
*(Kèm khuyến nghị: hoặc dispatch.sh dọn file `.pid` của chính nó khi kết thúc, hoặc bỏ hẳn dòng
753 — nhưng `dispatch.sh` là surface điều phối lõi, sửa nó phải qua arch-reviewer bắt buộc theo
`context_ops_mini` §3, nên tách khỏi phạm vi housekeeping.)*

### 2.2 RÁC THẬT — `.err`/`.log` không mang thông tin (338 file)

- **247 file `.err` đúng 0 byte** — xoá không mất gì.
- **66 file `.log` đúng 0 byte** — job chết trước khi in dòng đầu; thông tin "job này fail" đã nằm
  ở `bus/jobs/<job_id>.json` (status), không nằm ở file rỗng.
- **25 file `.err` đã ĐỌC nội dung**, tất cả đúng 157 B và chỉ chứa:
  `Warning: no stdin data received in 3s, proceeding without it…` ⇒ noise của harness, không phải
  lỗi. Đã kiểm bằng cách đọc thật, không suy đoán theo kích thước.
- **8 file `.err` GIỮ**: 6 file `dispatch_Mike_*.log.err` 287 B (07-09→07-13) +
  `dispatch_Winston_20260624_144409.log.err` 30 B — có nội dung khác boilerplate.

### 2.3 KHÔNG PHẢI RÁC — `dispatch_*.log` cũ ⇒ chỉ ARCHIVE

Nhiệm vụ yêu cầu kiểm chứng giả định "log cũ đã có bản tóm tắt trên bus/KB". **Đã lấy mẫu 12 file
`dispatch_*.log` >30d, grep job_id qua `bus/inbox/*.jsonl` + `bus/inbox/archive/*.gz` + toàn `kb/`:**

| Kết quả | Số |
|---|---|
| Có tham chiếu trong `kb/` (event/archive) | **8/12** |
| **KHÔNG có ở bus, KHÔNG có ở KB** | **4/12** (`Taylor_20260625_013357`, `Winston_20260626_033711`, `Mafee_20260627_041737`, `Taylor_20260629_102821`) |

⇒ **Giả định SAI ở ~1/3 trường hợp.** Kết hợp với việc `logs/` bị `.gitignore` (không có backup
GitHub), **xoá dispatch log = mất vĩnh viễn dấu vết duy nhất của 1/3 số job.**
⇒ Phân loại: **ARCHIVE (nén + di chuyển), tuyệt đối không delete.** Lợi ích cũng không phải disk
(cả 1294 file chỉ 1,7 MB) mà là **giảm số file ⇒ giảm token khi agent `ls`/glob**.

**Ràng buộc thiết kế phát hiện được** (không có thì archive sẽ âm thầm làm hỏng tool):
`bin/trace.sh <job_id> --log` (dòng 30–35) lấy đường dẫn logfile **từ job record** rồi `tail` đúng
path đó. Di chuyển hoặc gzip file ⇒ path sai ⇒ `--log` im lặng không ra gì.
Ghi nhận thêm: `kb_nightly` Phase 1b3 đã archive job record >30d vào `bus/jobs/archive/` và
`mike_json job-get` glob **không đệ quy** ⇒ `trace.sh --log` **hiện đã không tra được job >30d rồi**.
⇒ Nếu chọn ngưỡng 30d thì hai lớp (log + job record) rời đi cùng lúc, nhất quán; nếu chọn 14d để
tiết kiệm token nhiều hơn thì **phải kèm 3 dòng fallback trong `trace.sh`** tra `logs/archive/`.

### 2.4 BẰNG CHỨNG PHẢI GIỮ (không đề xuất xoá dưới bất kỳ hình thức nào)

| Nhóm | Lý do (đã grep xác nhận) |
|---|---|
| 22 dir `agents/Taylor/exp_*`/`probe_*` (282 MB) | 20/22 được trích dẫn trực tiếp; `exp_valframe` trích dẫn qua báo cáo research. Khớp `§10 mục 4`. |
| `data/bq_cache_asof20260729_postrestate` (2,0 GB) | snapshot của số pin R3 **hiện hành**; finding còn `CHỜ quant-skeptic` |
| `data/bq_cache_asof20260728` (2,0 GB) | mốc lịch sử TRƯỚC restate DT5G — bằng chứng attribution +0,47pp; Taylor ghi rõ "giữ riêng". **Không tái tạo được** (BQ time-travel tắt, `ticker`/`ticker_prune` TRUNCATE+rebuild mỗi ngày) |
| **toàn bộ `data/execution_logs/`** (116 MB) | compliance/audit trail tài chính — deny-list cứng |
| `data/archive/`, `data/_quarantine/` | đã là đích archive, có README |
| 671 file `data/*` "không tham chiếu" (0,72 GB) | grep literal không bắt filename động ⇒ chỉ được nén tại chỗ, có thể đảo ngược |
| 8 file `.err` có nội dung thật | dấu vết lỗi |

---

## 3. Thiết kế cơ chế dọn dẹp (nháp, CHƯA triển khai)

**File nháp**: `mike/bin/fleet_housekeeping.sh.draft` — hậu tố `.draft`, **không** `chmod +x`,
**không** đăng ký cron. (Đặt tên `.draft` có chủ đích theo `§10`: một file tên
`bin/fleet_housekeeping.sh` nằm sẵn trong `bin/` là đúng cái bẫy khiến agent/người sau tưởng nó
đã live và gọi thật.)

### 3.1 Nguyên tắc thiết kế

1. **`--dry-run` là MẶC ĐỊNH.** Không có `--apply` thì không byte nào bị đổi. Chạy trần
   `fleet_housekeeping.sh` = chỉ in ra.
2. **Archive là mặc định, delete là ngoại lệ phải khai báo.** Chỉ 4 category được xếp `DELETE`, và
   cả 4 đều đã kiểm chứng nội dung ở §2.1–2.2 (`.pid` 0 reader / file 0 byte / `.err` boilerplate
   đọc từng file / `.json.tmp` mồ côi / `__pycache__` regenerable).
3. **Delete có kiểm tra lại tại runtime, không tin ngưỡng tuổi.** File 0 byte được `test -s` lại
   ngay trước khi xoá; `.err` boilerplate được `grep` lại nội dung; không xoá theo pattern tên đơn
   thuần.
4. **Deny-list cứng, kiểm trước mọi category** — `execution_logs`, `bq_cache*`, `_quarantine`,
   `data/archive`, `trade_plans`, `trading_rules.json`, mọi `plan_*.json`, `.git`. Đây là hàng rào
   cuối, đứng ngoài logic từng category, để 1 lỗi pattern không thể chạm tới tiền thật.
5. **Archive giữ nguyên tên file** trong `logs/archive/<YYYY-MM>/` (nén cả lô thành `.tar.gz` theo
   tháng thì gọn hơn nhưng làm mất khả năng grep 1 file lẻ — chọn giữ file rời + `gzip` từng file,
   ưu tiên tra cứu được).
6. **Không tự cài cron trong bước này.** Nếu user duyệt: cron **hằng tuần** (không cần hằng ngày —
   khối lượng 1 tuần chỉ ~300 file), chèn **sau** `kb_nightly` để không tranh chấp, và **đăng ký
   `kb/cron_registry.md` trong cùng commit** theo `§11`.
7. **Ghi log + bus event mỗi lần chạy thật** với số file/byte thực tế đã động tới.

### 3.2 Bảng quy tắc theo category

Bảng dưới là **bản sau arch-review**. Mỗi guard in đậm là 1 required_change đã áp.

| # | Category | Đường dẫn | Ngưỡng | Hành động | Guard bằng chứng |
|---|---|---|---|---|---|
| 1 | `pid` | `mike/logs/.dispatch_*.pid` | **≥1d** | **DELETE** | §2.1 grep 0 reader; `-mtime +1` để không xoá pid của job vừa dispatch (là bản ghi OS-pid duy nhất để kill tay) |
| 2 | `empty` | `mike/logs/*.log`, `*.err` size 0 | ≥1d | **DELETE** | `test -s` lại **+ BẮT BUỘC có `bus/jobs/<job_id>.json` ở hot HOẶC archive**; không có ⇒ GIỮ (§6.1) |
| 3 | `errnoise` | `mike/logs/*.err` ≤200B | ≥1d | **DELETE** | **MỌI dòng non-blank** phải khớp warning (không còn `grep -q`) |
| 4 | `jobtmp` | `mike/bus/jobs/*.json.tmp` | ≥7d | **DELETE** | phải có bản `.json` đầy đủ ở hot/archive |
| 5 | `pycache` | **`mike/` + `trading_bot/`** (KHÔNG phải cả `WorkingClaude`) | mọi tuổi | **DELETE** | regenerable + đã gitignore; thu phạm vi vì 219/250 dir nằm ở `stockquery/` ngoài fleet |
| 6 | `dispatchlog` | `mike/logs/dispatch_*.log` | **>30d** | **ARCHIVE** → `logs/archive/<YYYY-MM>/*.log.gz` | §2.3 KHÔNG delete; **bỏ qua job có record hot NON-TERMINAL** (`orphaned`/`usage_limited`/`cancelled`/`superseded`) vì `trace.sh --log` của nhóm đó đang chạy được |
| 7 | `toollog` | `mike/logs/{verify_,arch_review_,wags_pipeline_,daily_retro_draft_}*` | >30d | ARCHIVE cùng đích | |
| 8 | `registry` | `mike/bus/registry/*.json` | >30d | ARCHIVE → `bus/registry/archive/` | **loại trừ 9 agent trong roster** — `cmd_fleet_status` glob không đệ quy ⇒ archive làm agent BIẾN MẤT khỏi `fleet_health.sh` thay vì hiện `dead` |
| 9 | `rotate` | `mike/logs/{discover,notify,watchdog,…}.log` | >10 MB | **ROTATE** (`.1.gz`, giữ 3 đời) | **nén+verify XONG mới dịch thế hệ** (thứ tự cũ: gzip fail = mất đời cũ nhất) |
| ~~10~~ | ~~`datacold`~~ | | | **ĐÃ GỠ HẲN** | lợi ích thật 42 MB không phải 0,72 GB; phép thử an toàn sai cấu trúc (§6.2) |
| — | `run_bot_*` | | | **KHÔNG động** | bằng chứng thực thi bot, 0 file >30d |
| — | `execution_logs`, `bq_cache*`, `agents/*/exp_*` | | | **DENY-LIST** | §2.4 |

### 3.3 Lần chạy đầu tiên — số ĐO THẬT (bản đã sửa sau arch-review)

Các số dưới đây là output `--dry-run` thật của script **bản v2**, chạy từng category
(`bash bin/fleet_housekeeping.sh.draft --only=<cat>`), không file nào bị đổi. Cột "v1" là số cũ,
giữ lại để thấy đúng chỗ nào đã sai và vì sao.

**Nhóm DELETE:**

| Category | v1 (sai/quá rộng) | **v2 đo thật** | Giải phóng | Vì sao đổi |
|---|---|---|---|---|
| `pid` | 1153 file | **1114 file** | 0,01 MB | thêm `-mtime +1` ⇒ giữ pid của job <1 ngày |
| `empty` | 289 file | **264 file** | ~0 MB | **guard giữ lại 25 file** (6 `.log` + 19 `.err`) không có job record |
| `errnoise` | 25 file | **25 file** | ~0 MB | siết "mọi dòng non-blank" ⇒ mất 0 file, đúng như dự đoán |
| `jobtmp` | 0 | **0** | 0 MB | guard giữ cả 3 (§1.2) |
| `pycache` | 250 dir / 20,29 MB | **5 dir / 0,84 MB** | 0,84 MB | thu về `mike/` + `trading_bot/`; 219 dir / 14,0 MB nằm ở `stockquery/` **ngoài fleet** |
| **Tổng** | 1467 file + 250 dir / 20,30 MB | **1408 mục / 0,86 MB** | | |

**Nhóm ARCHIVE:**

| Category | v1 | **v2 đo thật** | Trước nén | Vì sao đổi |
|---|---|---|---|---|
| `dispatchlog` | 668 | **664** | 0,50 MB | **giữ lại 5 log** của job record hot `orphaned` (trace.sh --log đang dùng được) |
| `toollog` | 2 | **2** | 0,01 MB | — |
| `registry` | 55 | **55** | 0,02 MB | roster-guard chưa bắn hôm nay (`Bob.json` mới 28d, sẽ vượt 30d trong ~2 ngày) |
| `rotate` | 0 | **0** | — | ngưỡng 10 MB, log lớn nhất 1,6 MB ⇒ hàng rào cho tương lai |
| **Tổng** | 725 / 0,52 MB | **721 mục / 0,52 MB** | → ~0,16 MB sau gz | |

**`datacold`: ĐÃ GỠ.** Số v1 (671 file / 0,72 GB → tiết kiệm ~0,5 GB) là **SAI** — đó là con số
của ngưỡng >30d trong khi script chạy >60d. Đo lại đúng: **188 file / 42,26 MB** (~30 MB sau nén).
Cộng với lỗi cấu trúc ở phép thử an toàn (§6.2) ⇒ gỡ hẳn, không phải hoãn.

**Tác động THẬT — nói thẳng:**

| | Trước | Sau (v2, mặc định) |
|---|---|---|
| Disk giải phóng | — | **0,86 MB** (v1 ghi 20,3 MB nhưng 14,0 MB trong đó ngoài phạm vi fleet) |
| File trong `mike/logs` (kể cả ẩn `.pid`) | 3082 | **~1179** (−62%) |
| `ls mike/logs/` | ~1928 entry / ~17K token | **~1260 entry / ~11K token** |
| `ls data/` | 2083 entry / ~19K token | **không đổi** (datacold đã gỡ) |
| Disk `/` | 91% | **91%** |

**Kết luận không được làm tròn cho đẹp: giá trị của script này là TOKEN, gần như bằng 0 về disk.**
Disk thu về 0,86 MB = 0,006% của 13 GB trống. Nếu mục tiêu là disk thì §5 (`/workspace` 45 GB,
`~/.cache/pip` 703 MB, `~/backup_thanhdt` 5,5 GB) là chỗ duy nhất có khối lượng — housekeeping fleet
**không** giải quyết được 91%.

### 3.4 Kiểm chứng script nháp đã làm

- `bash -n` PASS.
- Chạy `--dry-run` (mặc định) toàn bộ + từng category riêng: **không file nào bị đổi**, xác nhận
  `logs/fleet_housekeeping.log` **không được tạo** (script chỉ ghi log khi `--apply`).
- Guard `jobtmp` **đã bắt được 1 lỗi phân loại thật của chính báo cáo này** (§1.2) — bằng chứng
  rằng lớp kiểm-tại-runtime không phải trang trí.
- Deny-list đã test kích hoạt: các nhánh `execution_logs`/`bq_cache`/`exp_*` in
  `DENY-LIST chặn` thay vì hành động.
- **CHƯA** `chmod +x`, **CHƯA** đổi tên bỏ `.draft`, **CHƯA** thêm dòng cron nào.

---

## 4. Kết quả arch-review — 5 câu hỏi tôi tự nêu, đã có trả lời

Verdict: **NEEDS_CHANGES / confidence high** → đã sửa xong toàn bộ (§6).

| # | Câu tôi hỏi | Reviewer trả lời | Xử lý |
|---|---|---|---|
| 1 | `errnoise` dùng `grep -q` có để lọt file vừa có warning vừa có lỗi thật? | **CÓ nguy cơ. Và siết là MIỄN PHÍ**: đọc cả 25 file, tất cả đúng 157 B, 0 dòng non-blank thừa ⇒ siết mất 0 file | ĐÃ SIẾT — "mọi dòng non-blank phải khớp". Đo lại: vẫn 25 file, đúng như dự đoán |
| 2 | Ngưỡng 30d vs 14d cho `dispatchlog` | **Tiền đề 30d chỉ ĐÚNG MỘT NỬA**: `kb_nightly.sh:490` chỉ archive status TERMINAL; record `orphaned`/`usage_limited`/`cancelled`/`superseded` nằm hot VĨNH VIỄN ⇒ với nhóm đó `--log` đang chạy được và archive sẽ làm im lặng MỚI | GIỮ 30d + **thêm guard bỏ qua job non-terminal**. Đo thật: 9 job orphaned 30,3–33,3d; dry-run hôm nay giữ 5 |
| 3 | `datacold`: "0 tham chiếu literal" có đủ để gzip? | **KHÔNG — và lợi ích bị phóng đại ~18 lần.** Corpus prune mất `data/results_registry.md` (4447 dòng, chính nguồn §1.4), + 30 mục trong sổ lưu tên rút gọn nên `grep -qF` không bao giờ khớp | **GỠ HẲN** category. 30 MB không đáng đánh đổi |
| 4 | Deny-list đặt vậy đủ chưa, có kẽ nào lọt? | **PASS** — cả 8 nhánh mutation đều gọi `denied()` trước; bash `case` glob có match `/` nên path lồng sâu vẫn phủ; xác nhận nó BẮN thật 5 lần trong dry-run | giữ nguyên |
| 5 | Có category nào tôi xếp DELETE mà thực ra là bằng chứng? | **CÓ — đây là killer objection.** `empty`: 6 file `.log` 0-byte không có job record/bus/KB nào; lập luận "trạng thái fail đã ở job record" SAI với ~9% | ĐÃ ÁP GUARD (§6.1) |

**Reviewer còn tìm ra 5 rủi ro tôi KHÔNG nêu** — phần giá trị nhất của vòng review:

- **`registry` làm hỏng `fleet_health.sh`**: `mike_json.py:402 cmd_fleet_status` glob
  `bus/registry/*.json` **không đệ quy** ⇒ archive registry của 1 agent làm nó **biến mất** khỏi
  bảng sức khoẻ thay vì hiện `dead` — mất tín hiệu đúng lúc cần nhất. Không phải giả thuyết:
  `bus/registry/Bob.json` đang **28 ngày**, vượt 30d trong ~2 ngày nữa.
- **Script exit 1 khi dry-run THÀNH CÔNG** (`say()` kết thúc bằng `[ … ] && printf` ⇒ return 1),
  còn `--apply` lại exit 0 — **ngược**. Dưới cron `… || notify` sẽ báo động giả mỗi lần → nhờn
  cảnh báo, đúng bệnh fail-silent mà fleet đã dính nhiều lần.
- **`pid` không có age guard** trong khi `empty`/`errnoise` có ⇒ xoá pid của job vừa dispatch vài
  giây trước (là bản ghi OS-pid duy nhất để kill tay).
- **`pycache` scope creep**: 219/250 dir và **14,0/20,3 MB** nằm ở `WorkingClaude/stockquery` —
  app ngoài fleet ⇒ 69% "thành tích" disk đến từ chỗ không thuộc phạm vi được giao.
- **`rotate` không kill-idempotent**: dịch thế hệ (`rm .3.gz`, `.2→.3`, `.1→.2`) **trước** khi
  gzip mới thành công ⇒ gzip fail = mất đời cũ nhất mà không thêm được gì.

Reviewer cũng **xác minh độc lập** 2 lần tự đính chính của tôi (3 file `.json.tmp` là artifact duy
nhất; 4/12 log không có dấu vết — thực tế 3/4 còn **không có cả job record**) và xác nhận dry-run
thật sự inert (md5 fingerprint `find logs bus` giống hệt trước/sau).

## 5. Việc cần user/Mike quyết (vượt quyền Wags)

**A. Nguyên nhân thật của `/` 91%: `/workspace/kaffa_v2` = 45 GB, owner `hainguyen`**, không liên
quan fleet/trading, cùng filesystem với `/`. `/workspace` tổng 58 GB (thêm `py310` 7,3 GB,
`rmbg-env` 5,9 GB = virtualenv). Fleet chỉ chiếm 13 GB. **Wags không có quyền và không nên chạm.**
Nếu muốn giải quyết 91% thật thì đây là chỗ duy nhất có đủ khối lượng.

**B. Chính sách git của repo `mike`** (§1.3): thêm `*.csv *.pkl *.parquet` vào
`mike/.gitignore` cho `agents/*/exp_*`, `agents/*/probe_*`? Tác động: dừng phình `.git`, nhưng
**mất bản backup GitHub của 279 MB bằng chứng experiment** (trade-off thật, không phải win thuần) —
cần Taylor có ý kiến. Kèm câu hỏi phụ: có chạy `git gc` không (loose 212 MB → pack, thu hồi ~180 MB
mà **không** mất commit nào)? `git gc` an toàn, nhưng vẫn xin phép vì repo fleet là surface chung.

**C. Codify quy tắc snapshot `bq_cache_asof*`** (§1.4): chính sách của Taylor ("1 bản xoay vòng cho
số pin hiện hành + mốc lịch sử giữ riêng, chỉ xoá sau khi pin mới qua quant-skeptic") hiện chỉ tồn
tại trong 1 bus event. Đề xuất đưa vào `coding_guidelines §8` + `kb/data_registry/`. Nhắc: mỗi bản
đúng 2,0 GB và **không hardlink được**, nên trên disk 13 GB trống thì 2 bản là ngưỡng nên khoá cứng.

**D. Win disk an toàn nằm ngoài phạm vi được giao** — nêu để user quyết, Wags không tự làm:
`~/.cache/pip` **703 MB** (`pip cache purge`, 0 rủi ro) · `~/.cache/uv` + `huggingface` 220 MB ·
`/tmp` >7d **0,92 GB** (dùng chung nhiều user) · `~/backup_thanhdt` **5,5 GB** đóng băng từ
2026-06-21. Tổng khả dụng ≈ **7,3 GB** — nhiều gấp **260 lần** toàn bộ housekeeping fleet.

**E. Không đề xuất gì cho `execution_logs/`** ngoài "để nguyên". Chỉ 3 file >30d, nén không đáng,
và nghĩa vụ lưu trữ cần Wendy/Spyros xác nhận trước khi bàn tới.

---

## 6. Nhật ký sửa sau arch-review (v1 → v2)

12 required_changes, **đã áp 11, 1 chuyển thành việc riêng**. Mọi số dưới đây tôi đo lại độc lập
trước khi sửa — không sửa theo lời reviewer mà không kiểm.

### 6.1 BẮT BUỘC — `empty`: guard bằng-chứng-duy-nhất *(killer objection)*

Tôi đã tự phát minh guard này cho `jobtmp` (§1.2) rồi **quên áp cho `empty`** — dù 2 trong 6 file
nạn nhân chính là mẫu trong §2.3 do tôi tự đo. Đó là lỗi đáng nói nhất của vòng v1: không phải
thiếu thông tin, mà là **có dữ liệu đúng trong tay và không nối hai đầu lại**.

Đo lại xác nhận 6/6 file 0-byte không có `bus/jobs/<id>.json` ở hot lẫn archive:
`Taylor_20260625_013357`, `Winston_20260624_144409`, `Winston_20260626_020936`,
`Taylor_20260625_022912`, `Mike_20260627_024240`, `Winston_20260626_020407`.
Cộng với `logs/` bị `.gitignore` (`git ls-files logs/` = 0) ⇒ xoá = **mất vĩnh viễn dấu vết duy
nhất** của 6 dispatch.

Sau sửa: dry-run in `GIỮ (0 byte NHƯNG không có job record hot lẫn archive — artifact DUY NHẤT)`
cho **25 file** (6 `.log` + 19 `.err` cùng job). Số xoá 289 → **264**; lợi ích token gần như không
đổi, rủi ro mất bằng chứng về 0.

### 6.2 BẮT BUỘC — gỡ hẳn `datacold` + đính chính số sai trong báo cáo

Đây là lỗi của chính báo cáo, không phải của script: §3.3 v1 khẳng định **"các số dưới đây không
phải ước tính — chúng là output `--dry-run` thật"**, nhưng dòng `datacold` lại là con số của ngưỡng
**>30d** trong khi script chạy **>60d**. Chạy lại đúng lệnh: **188 file / 42,26 MB**, không phải
671 file / 0,72 GB ⇒ **phóng đại ~18 lần**.

Reviewer còn chỉ ra phép thử an toàn **sai cấu trúc**, không chỉ sai số: corpus (dòng 266)
`-path "$WC_ROOT/data" -prune` ⇒ **không đọc `data/results_registry.md`** — đúng cái sổ ghim kết
quả mà §1.4 của báo cáo này dựa vào; và 30 mục trong sổ lưu tên rút gọn (`..._nav20B.csv`) nên
`grep -qF` **không bao giờ** khớp được. Hôm nay 0 va chạm, nhưng **lập luận** phải đúng chứ không
chỉ **kết quả** (§10 mục 1). ⇒ Gỡ hẳn, không hoãn. 30 MB không đáng dựng lại hàng rào này.

### 6.3 Bảng 12 thay đổi

| # | Loại | Thay đổi | Bằng chứng đo lại |
|---|---|---|---|
| 1 | BẮT BUỘC | `empty` guard job-record | 6 file sole-artifact, dry-run giữ 25 |
| 2 | BẮT BUỘC | gỡ `datacold` | 188 file/42,26 MB (không phải 671/0,72 GB) |
| 3 | BẮT BUỘC | sửa §3.3 + bảng "Tác động THẬT" | đã viết lại toàn bộ, có cột v1 vs v2 |
| 4 | BẮT BUỘC | `dispatchlog` bỏ qua job non-terminal | 9 job `orphaned` 30,3–33,3d; dry-run giữ 5 |
| 5 | BẮT BUỘC | `registry` loại trừ roster | `Bob.json` 28d; `mike_json.py:402` glob không đệ quy |
| 6 | BẮT BUỘC | `exit 0` + `return 0` trong `say()` | trước: dry-run exit=1; sau: exit=0 |
| 7 | NÊN | `errnoise` siết "mọi dòng non-blank" | 25 → 25 file (mất 0, đúng dự đoán) |
| 8 | NÊN | `pid` thêm `-mtime +1` | 1153 → 1114 file |
| 9 | NÊN | `pycache` thu về `mike/`+`trading_bot/` | 250 dir/20,29 MB → 5 dir/0,84 MB |
| 10 | NÊN | `rotate` nén+verify xong mới dịch thế hệ | dormant (log lớn nhất 1,6 MB < 10 MB) |
| 11 | NÊN | retention cấp 2 cho `logs/archive/` | **KHÔNG làm** — xem dưới |
| 12 | TÁCH RIÊNG | bug `trace.sh --log` với job >30d | đã xác minh THẬT — xem dưới |

**#11 — cố ý không làm (§2 simplicity).** Reviewer đúng khi nói archive tăng một chiều, nhưng khối
lượng thật là **0,16 MB/tuần sau nén**; thêm 1 tầng retention nữa là code chưa ai cần cho vấn đề
chưa tồn tại. Ghi lại thành ngưỡng để người sau biết khi nào phải làm: **xem lại khi
`logs/archive/` vượt 100 MB hoặc 5000 file** (với tốc độ hiện tại ≈ **hơn 10 năm**).

**#12 — bug có sẵn, KHÔNG do housekeeping gây ra, cần việc riêng.** `bin/trace.sh:30-35` lấy path
logfile **từ job record** rồi `tail`; `cmd_job_get` (`bin/mike_json.py:744`) mở
`_job_path(jobs_dir, job_id)` **không đệ quy** ⇒ job đã vào `bus/jobs/archive/` (do kb_nightly
Phase 1b3 từ 2026-07-27) trả not-found. Kiểm thật: `bash bin/trace.sh DollarBill_20260627_052257
--log` không in gì trong khi `logs/dispatch_DollarBill_20260627_052257.log` **vẫn còn trên đĩa**.
⇒ `trace.sh --log` **hiện đã hỏng** cho mọi job >30d. Fix đúng = cho `cmd_job_get` fallback sang
`archive/` (+ fallback tra `logs/archive/*/<name>.log.gz` nếu sau này hạ ngưỡng xuống 14d).
Chưa sửa trong job này vì nằm ngoài phạm vi được giao — đề nghị mở việc riêng.

### 6.4 Kiểm chứng lại sau khi sửa

- `bash -n` PASS.
- Dry-run toàn bộ: **exit=0** (trước khi sửa: exit=1), fingerprint `find logs bus -printf '%p %s
  %T@'| md5sum` **giống hệt trước/sau** (`7df8152712…`), `logs/` vẫn **3082 file**, không tạo
  `logs/fleet_housekeeping.log`, không tạo thư mục archive nào.
- 4/5 guard **bắn thật** trong dry-run: `empty` giữ 25, `dispatchlog` giữ 5, `jobtmp` giữ 3,
  deny-list chặn 5. Hai guard ra 0 **đúng như dự đoán**: `errnoise` (siết không mất file nào) và
  `registry` roster (`Bob.json` mới 28d, chưa tới ngưỡng 30d).
- **CHƯA** `chmod +x`, **CHƯA** bỏ hậu tố `.draft`, **CHƯA** thêm dòng cron nào.
