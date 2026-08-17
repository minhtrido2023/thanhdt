# Audit: ScheduleWakeup wakeup-miss + double-answer (job Wags_20260817_184558)

Ngày 2026-08-17 · read-only, KHÔNG sửa code · dữ liệu 2026-08-14 → 2026-08-17T18:47Z

## Kết luận 1 dòng

**Push CỨU KỊP — không có ca nào miss cả hai trên job async thật kể từ khi push deploy
(2026-08-15T01:05Z).** Double-answer là ưu tiên cao hơn. Nhưng tiền đề của MIKE.md §8 item 4
("push-wake và ladder-wake là 2 task ccdb ĐỘC LẬP, cùng fire") **ĐÃ SAI** so với code ccdb hiện
tại — ccdb đã tự cưỡng chế "tối đa 1 one-shot wakeup pending / thread". Root cause thật của
double-answer nằm ở chỗ khác.

---

## Bước 1 — Hậu quả thật của wakeup-miss

### 1a. Con số gốc bị nhiễu bởi lỗi của chính công cụ đo

`bin/wakeup_audit.py:87` phát hiện dispatch bằng:

```python
if "dispatch.sh" in cmd and "--bg" in cmd:
```

Đây là **substring match trên toàn bộ command**, nên một lệnh `notify_thread.sh "<văn bản NÓI VỀ
dispatch.sh ... --bg>"` bị đếm là một lần dispatch. Bắt được 2 ca thật:

| Turn bị đếm MISS | Thực tế |
|---|---|
| 2026-08-17T08:45:02Z | `notify_thread.sh` đăng bài giải thích lỗi wake-đúp — nội dung tin nhắn chứa chữ `dispatch.sh`/`--bg` |
| 2026-08-15T17:40:34Z | tương tự, không hề gọi dispatch |

Đo lại với detector neo vào **vị trí gọi lệnh** (đầu dòng / sau `;` `&&` `|` `timeout N`):

| Detector | Turn | Miss | Tỷ lệ |
|---|---|---|---|
| Hiện tại (substring) | 45 | 9 | 20,0% |
| Đã sửa (anchor lời gọi) | 30 | 7 | **23,3%** |

⚠️ Lưu ý ngược chiều trực giác: sửa false-positive làm **tỷ lệ TĂNG**, vì detector cũ cũng thổi
phồng MẪU SỐ (15 turn không phải dispatch bị tính vào "turn có dispatch"). Tức là **kỷ luật §8
thực tế TỆ HƠN con số 20% đang báo cáo**, không phải tốt hơn. Con số 27,3% ngày 08-17 cũng cần đo
lại bằng detector đã sửa trước khi dùng làm cơ sở quyết định.

### 1b. Với MỖI miss thật: push có cứu kịp không?

Nguồn bằng chứng (theo thứ tự tin cậy): journal `ccdb-mike.service` (`Task registered via API:
name=dispatch-wake-<job_id>` — log tạo push, **có thẩm quyền**) → transcript Mike (prompt wake
thực sự rơi vào phiên) → `bus/jobs/*.json`.

⚠️ `tasks.db` **KHÔNG dùng làm sổ audit được**: `sqlite_sequence=1739` nhưng `max(id)=1732` ⇒ 7
row đã bị XOÁ. Code hiện tại (`scheduler.py:180`) xoá row one-shot sau khi chạy. Không có bản ghi
bền nào chứng minh một push ĐÃ fire.

| # | Turn (UTC) | Job | Push? | Phán quyết |
|---|---|---|---|---|
| 1 | 08-14T04:51 | Taylor_20260814_050107 | không có cơ chế | **Miss cả hai** — nhưng TRƯỚC khi push deploy (c721a9cb, 08-15T01:05Z) |
| 2 | 08-15T00:56 | Taylor_20260815_005649 | ✅ | **Selftest** chạy trong worktree `wt-…-wakeladder` ("trả lời đúng 1 dòng: OK"). Chính là job MIKE.md dẫn làm bằng chứng verify push. Không phải miss vận hành |
| 3 | 08-17T02:01 | *không định vị được* | — | Lệnh nuốt stdout của `dispatch.sh` (chỉ echo "Taylor dispatched for HYBRID P0") ⇒ nếu dispatch fail thì **không ai thấy được**. Chưa kết luận |
| 4 | 08-17T07:54 | Taylor_20260817_075412 | ✅ fire +33s sau khi job xong | **Push CỨU** (replied 08:24:38) |
| 5 | 08-17T18:13 | Taylor_20260817_181353 | ✅ đến 18:16:28 | **Push CỨU** (replied 18:17:17, trễ 68s) |
| 6 | 08-17T18:41 | Taylor_20260817_184109 | ✅ đã tạo | Push đã đăng ký |
| 7 | 08-17T18:45 | Wags_20260817_184558 (job này) | đang chạy | Chưa xét được |

**⇒ Không có ca "miss CẢ HAI" nào trên job async thật kể từ 2026-08-15.**

### 1c. Độ tin cậy của push — và MỘT điểm mù cấu trúc

`_bg_wrapper` ghi `pid` ngay khi vào (`dispatch.sh:1199 JSET pid="$BASHPID"`), và nó là **nơi DUY
NHẤT** gọi `wake_thread.sh`. Nên trường `pid` là proxy chính xác cho "job có đi qua đường async
hay không". Đối chiếu 33 job `from=Mike` đã kết thúc từ 08-15:

| | push fire | push KHÔNG fire |
|---|---|---|
| **có `pid`** | 27 | 1 |
| **không `pid`** | 0 | **5** |

- Tương quan 32/33. Khi `_bg_wrapper` thật sự chạy, push fire **27/28 = 96%**.
- Ca hỏng duy nhất có `pid`: `Taylor_20260815_034407` — và nó **đã được ghi log**:
  `logs/wake_thread_errors.log` → `HTTP 409: Task name already exists`. Fail-soft hoạt động đúng,
  có dấu vết.
- **5 job không có `pid` ⇒ push KHÔNG BAO GIỜ fire, hoàn toàn im lặng.** Đây là dispatch đồng bộ
  / đường khác (caller đang block chờ kết quả), nên *không phải* wakeup-miss — nhưng nó là điểm mù
  cần biết: `from=Mike` **không** đủ để suy ra "sẽ có push".

---

## Bước 2 — Cơ chế double-answer

### 2a. `is-replied` / `mark-replied` — có race, nhưng KHÔNG phải nguyên nhân chính

`bin/jobs.sh:80-94`:

```bash
mark-replied)  MJ job-set "$JOBS_DIR" "$job_id" "replied_at=$(date -u +%FT%TZ)" ;;
is-replied)    val=$(MJ job-field "$JOBS_DIR" "$job_id" replied_at ...); [ -n "$val" ] ;;
```

Đây là **check-then-act (TOCTOU) không nguyên tử**: hai lượt cùng chạy `is-replied` (cùng nhận
exit 1) trước khi lượt nào kịp `mark-replied` thì cả hai đều trả lời.

Nhưng cửa sổ này **hẹp trong thực tế**: ccdb tuần tự hoá theo thread — mỗi thread chỉ có 1 Claude
CLI, và `_master_loop` bỏ qua task đang trong `self._running`. Hai lượt wake của CÙNG một thread
không chạy chồng nhau.

**Điểm yếu thật không phải race — mà là nó CHỈ LÀ KHUYẾN NGHỊ**: nó chỉ hoạt động nếu agent nhớ
gọi. Đo mức áp dụng (job `from=Mike`, đã kết thúc, từ 08-15):

- Tổng: **15/35 = 43%** có `replied_at`.
- Nhưng cơ chế mới landed **08-17 ~04:00Z**. Từ mốc đó: **13/14 ≈ 100%** (job thiếu duy nhất là
  `Taylor_20260817_184109`, vừa xong lúc audit).

⇒ Kỷ luật prose ĐANG được tuân thủ tốt. Đây không phải chỗ đang chảy máu.

### 2b. Tiền đề của MIKE.md §8 item 4 đã LỖI THỜI

MIKE.md nói: *"push-wake và ladder-wake là 2 task ccdb ĐỘC LẬP, cùng fire khi job xong. Không có
giao thức idempotency."*

**Code ccdb hiện tại phủ nhận điều này.** CẢ HAI nơi sinh wakeup đều gọi
`delete_pending_one_shot_by_thread()` ngay trước khi tạo:

- Bridge ScheduleWakeup của harness — `claude_discord/cogs/_run_helper.py:310`
- Push ngoài qua `POST /api/tasks` — `claude_discord/ext/api_server.py:677`

`task_repo.py:259` — `DELETE ... WHERE thread_id=? AND one_shot=1 AND enabled=1`.

⇒ Bất biến **"tối đa 1 one-shot wakeup pending mỗi thread"** đã được cưỡng chế ở tầng ccdb.
Quan sát thấy hoạt động thật 3 lần ngày 08-17:

```
11:39:18 api_server: Cancelled 1 pending one-shot wakeup(s) for thread 1538146805207011358
                     before creating dispatch-wake-Taylor_20260817_112844
10:35:21 / 16:50:13  (2 lần nữa)
```

(Hệ quả phụ, lành tính: 2 job cùng thread xong sát nhau thì push của job SAU xoá push của job
TRƯỚC — `Taylor_20260817_164625` bị `..._164649` xoá. Không mất việc: Mike tỉnh 1 lần rồi soát cả
bảng, `replied_at` của cả hai đều là 16:50:57.)

### 2c. Hai nguyên nhân double-answer THẬT còn lại

**(a) Compaction + interrupt replay — CÓ BẰNG CHỨNG TRỰC TIẾP**

Job `Taylor_20260817_112844`, transcript `bd1924de`:

```
11:39:21  scheduler: 1 task(s) due → fire task 1729, Claude CLI pid=1307292
11:39:35  [user] Job `Taylor_20260817_112844` (Taylor) đã hoàn thành: status=done. …
11:43:24  [system] "This session is being continued from a previous conversation
                    that ran out of context…"     ← auto-compaction
11:43:36  [user] [Request interrupted by user]
11:43:49  [queue-operation ×2]
11:43:49  [user] Job `Taylor_20260817_112844` (Taylor) đã hoàn thành: status=done. …   ← LẶP LẠI
11:44:37  scheduler: one-shot task 1729 disabled
```

Cùng một prompt wake được giao **2 lần** trong cùng phiên: lượt đầu cạn context → auto-compact →
bị ngắt → prompt trong hàng đợi được **phát lại**. ccdb chỉ fire task 1729 **một lần** — đây là
replay ở tầng harness/bridge, không phải task fire đúp.

→ `is-replied` PHÒNG ĐƯỢC ca này **nếu** prompt wake encode Bước B. Đây chính là lý do §8 item 4
tồn tại, và nó đúng — chỉ là chẩn đoán nguyên nhân ghi trong MIKE.md sai.

*(Đính chính trong quá trình audit: ban đầu tôi tưởng `Taylor_20260817_075412` cũng bị push 2 lần
lúc 11:43:24. Sai — đó là regex của tôi khớp phải phần TÓM TẮT COMPACTION có trích lại job id.
Chỉ có 1 ca replay thật.)*

**(b) `_running` chỉ nằm trong RAM + xoá row SAU khi turn xong — LỖ HỔNG SUY LUẬN, chưa bắt tận tay**

`scheduler.py:_master_loop` + `_run_task`:

```python
await self.repo.update_next_run(task_id, interval_seconds=task["interval_seconds"])  # +60s
asyncio.create_task(self._run_task(task))
...
await run_claude_with_config(...)      # BLOCK suốt cả lượt Claude (nhiều phút)
if task.get("one_shot"):
    await self.repo.delete(task_id)    # chỉ xoá SAU khi lượt xong
```

`wake_thread.sh` đặt `interval_seconds: 60`. Nên trong **toàn bộ** thời gian lượt chạy, row vẫn
`enabled=1` và `next_run_at` đã ở quá khứ ⇒ **due lại mỗi 30s**. Quan sát thật, 9 tick liên tiếp:

```
11:39:21  1 task(s) due   ← fire
11:40:51 / 11:41:21 / 11:41:51 / 11:42:21 / 11:42:51 / 11:43:21 / 11:43:51 / 11:44:21  1 task(s) due
11:44:37  one-shot task 1729 disabled
```

Thứ DUY NHẤT chặn chạy lại là `self._running: set[int]` — **chỉ trong bộ nhớ tiến trình**.
`ccdb-mike.service` restart **4 lần riêng ngày 08-17** (UTC 07:40, 08:45, 12:17, 16:39). Restart
giữa lượt ⇒ `_running` mất, row vẫn due ⇒ **fire lại đúng prompt cũ**.

Chưa bắt được tận tay trong 4 ngày này (các restart tình cờ không rơi vào giữa lượt wake), nhưng
đây là lỗ hổng sống, và tần suất restart cao khiến nó chỉ là vấn đề thời gian.

*(Ghi chú: bản deploy trước 08-17T16:39Z dùng `set_enabled(False)` thay vì `delete` — đó là lý do
18 row `dispatch-wake-*` còn sót lại `enabled=0` trong DB. Bản mới xoá hẳn. Cửa sổ rủi ro **giống
hệt nhau**, vì cả hai đều xảy ra SAU lượt.)*

---

## Bước 3 — Đề xuất fix dứt điểm

**Thứ tự ưu tiên: double-answer TRƯỚC.** Push cứu 96% miss khi job thật sự chạy async, và không có
ca miss-cả-hai nào từ 08-15. Còn double-answer thì có bằng chứng trực tiếp (2c-a) và một lỗ hổng
cấu trúc chưa bịt (2c-b).

### Cưỡng chế idempotency ở tầng cơ chế (không phụ thuộc agent nhớ)

**F1 — Bịt cửa sổ restart-replay (1 dòng, tầng ccdb, ăn tiền nhất).**
Đánh dấu row đã tiêu thụ **TRƯỚC** khi chạy, không phải sau. Trong `_run_task`, với `one_shot`:
gọi `set_enabled(task_id, enabled=False)` **ngay trước** `run_claude_with_config(...)`, giữ
`delete(task_id)` ở cuối để dọn. Bỏ hẳn phụ thuộc vào `_running` in-memory cho tính đúng đắn —
`_running` chỉ còn là tối ưu. Đây là repo `claude-code-discord-bridge`, ngoài phạm vi sửa của
Wags ⇒ **cần user quyết**.

**F2 — Biến `is-replied`/`mark-replied` thành một lời gọi nguyên tử.**
Thêm `jobs.sh claim-reply <job_id>`: test-and-set `replied_at` trong **một** thao tác
compare-and-swap của `mike_json.py`, exit 0 **chỉ cho caller ĐẦU TIÊN**. Xoá hẳn TOCTOU và rút
prose từ 2 bước còn 1. Giữ `mark-replied`/`is-replied` cho tương thích ngược. Đây là tooling điều
phối thuần ⇒ **Wags tự làm được**.

**F3 — Dedup token ở tầng ccdb (fix triệt để nhất, dài hơi hơn).**
Thêm cột `dedup_key` cho `scheduled_tasks`; scheduler từ chối chạy task có `dedup_key` đã thực thi.
`wake_thread.sh` đã có sẵn khoá tự nhiên là `job_id`. Diệt được CẢ replay-do-compaction (2c-a) lẫn
replay-do-restart (2c-b) mà agent không cần nhớ gì. Cùng repo với F1 ⇒ **cần user quyết**.

### Sửa nguồn sự thật đang sai

**F4 — Sửa MIKE.md §8 item 4.** Tiền đề "2 task ccdb độc lập cùng fire" đã sai. Ghi lại nguyên
nhân THẬT (compaction/interrupt replay + cửa sổ restart) để lần sau không ai fix nhầm chỗ. Giữ
nguyên yêu cầu Bước A/B — chúng vẫn đúng và vẫn cần.

**F5 — Sửa `bin/wakeup_audit.py:87`.** Neo phát hiện vào vị trí gọi lệnh thay vì substring. Đồng
thời tách một hạng mục nghiêm trọng hơn hẳn: **"turn có `--bg` nhưng KHÔNG sinh ra job record"** —
dispatch fail âm thầm thì push không thể cứu, vì job chưa từng tồn tại. Ca 08-17T02:01 là ứng viên
và không kiểm chứng được vì lệnh nuốt stdout của `dispatch.sh`.

**F6 — Cho push một dấu vết bền.** `wake_thread.sh` hiện chỉ log KHI HỎNG. ccdb thì xoá row sau
khi chạy ⇒ **không có bằng chứng nào chứng minh một push đã fire**. Log cả ca thành công
(`job_id` + task id) vào `logs/wake_thread.log`. Audit này phải đi vòng qua journal của systemd —
lần sau journal xoay vòng là mất sạch.

---

## Ranh giới đã giữ

Read-only. Không sửa file nào. F1/F3 nằm ở repo `claude-code-discord-bridge` (hạ tầng bridge dùng
chung cho mọi phiên) ⇒ escalate, không tự sửa. F2/F5/F6 là tooling điều phối trong `mike/bin/` —
Wags làm được sau khi có duyệt.
