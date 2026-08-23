# Code-quality review định kỳ — kế hoạch (đề xuất 2026-08-23, chờ user duyệt)

> Trạng thái: **ĐỀ XUẤT** — chưa cài gì. Người duyệt: user. Chủ triển khai: Mike (điều phối),
> Wags (tooling mike/bin), Taylor (fix trong trading_bot/ khi có finding được duyệt).

## 0. Quyết định nền đã chốt trong hội thoại 13:20 ICT 2026-08-23

- **KHÔNG tạo daemon/agent thường trực tự sửa code.** Một agent "dọn rác" tự động sẽ false-positive
  đúng những thứ cố ý giữ (165 `test_*.py` ở root là artifact R&D — §23; R&D script `exp_*`/`probe_*`;
  `agents/<id>/` giữ để audit) và đi ngược §2/§3 coding_guidelines (không refactor khi không được yêu cầu).
- **Mô hình = REPORT-ONLY + người quyết + vòng "tốt nghiệp" ra gate cơ học.** Giống cách
  `arch-reviewer` audit Wags (read-only, trả verdict) và cách bài học đã được đẩy thành 4 pre-commit
  gate (`shellcheck_gate`, `repo_commit_gate`, `discord_id_gate`, `utc_text_gate`).

## 1. Số đo hiện trạng (đo 2026-08-23, để biết mình đang review cái gì)

| Thứ | Số | Hệ quả thiết kế |
|---|---:|---|
| `.py` toàn WorkingClaude (trừ venv/worktree) | ~2.455 | **Không quét toàn bộ** — vô nghĩa và đắt |
| `trading_bot/*.py` | 16 file / 11.269 dòng | **Lõi tiền thật** — luôn trong scope |
| `mike/bin` | 91 `.sh` + 124 `.py` | Tooling điều phối — scope theo diff |
| Commit/tuần WorkingClaude (4 tuần gần nhất) | 40–54 | Diff 7 ngày là kích thước review hợp lý |
| File nóng 30 ngày | `executor.py` 23, `plan.py` 18, `brokers.py` 16, `config.py` 12, `bot_execute.py` 12 | Đúng 5 file lõi §23 — nơi đáng review nhất |
| Linter Python hiện có | **Không có** (không ruff/pyflakes trong venv) | Tầng rẻ nhất đang thiếu — làm trước |
| Pre-commit gate hiện có | 4 (bash-only + text) | Chưa có gate nào cho Python |

## 2. Kiến trúc 3 tầng — rẻ trước, đắt sau, người ở cuối

```
Tầng 1  CƠ HỌC (ruff, mỗi commit, <2s)      → chặn lỗi chắc chắn (import thừa, tên chưa định nghĩa, f-string rỗng…)
Tầng 2  LLM REVIEW (1 lần/tuần, read-only)    → finding có §-guideline + file:line + bằng chứng, đã qua verify phản biện
Tầng 3  NGƯỜI (user/Mike duyệt)               → chọn: fix (dispatch owner) / bỏ qua / "tốt nghiệp" thành rule Tầng 1
```

Vòng tự cải thiện nằm ở mũi tên **Tầng 2 → Tầng 1**: finding nào lặp ≥2 tuần và có dạng cú pháp
⇒ viết gate cơ học, từ đó LLM không phải nhìn lại lớp lỗi đó nữa. Đây chính là "enforcement
policy" đã có trong coding_guidelines (user mandate 2026-08-01), giờ có cơ chế định kỳ thay vì
chờ sự cố.

## 3. Tầng 1 — ruff trong pre-commit (tuần 1)

- Cài `ruff` vào `wc_venv`. **Rule set hẹp, chỉ lỗi gần như chắc chắn**: `F` (pyflakes: F401 import
  thừa, F811 định nghĩa đè, F821 tên chưa định nghĩa, F841 biến không dùng), `E9` (lỗi cú pháp),
  `B006/B008` (mutable default). KHÔNG bật style (E501 độ dài dòng, quote…) — nhiễu, không phải bug.
- **Baseline-first, không block ngay**: chạy report trên toàn `trading_bot/ bot_execute.py
  mike/bin/*.py` → ghi `kb/code_quality_baseline.json` (giống `selfcheck_baseline.json`). Gate chỉ
  chặn **file thay đổi trong commit** và chỉ khi số lỗi **tăng so với baseline** của file đó
  (ratchet) — đúng bài học "test gate mới trên file thật trước khi bật" (coding_guidelines đầu file).
- Loại trừ tường minh trong `pyproject`/`ruff.toml`: `test_*.py` ở root, `exp_*`, `probe_*`,
  `stress_*`, `agents/*/research/`, `archive/`, `wc_venv/`.
- Selfcheck kèm theo: `code_quality_gate_selfcheck.sh` — fixture có F821 phải bị chặn, fixture sạch
  phải qua, file trong danh sách loại trừ phải được bỏ qua (3 bất biến, cùng mẫu các gate hiện có).
- Người làm: **Wags** (tooling mike/bin) + arch-reviewer audit. Không đụng logic trading.

## 4. Tầng 2 — LLM review hàng tuần, read-only (tuần 2 →)

**Script**: `mike/bin/code_quality_weekly.sh` (cron **Chủ Nhật 10:00 ICT** = `0 3 * * 0` UTC — sau
`spend_report_weekly` 09:00, trước `fleet_housekeeping` 22:00; KHÁC việc với `weekly_ops_audit.sh`
T7 03:30 vốn săn "bug đang sống trong production"). Đăng ký `kb/cron_registry.md` theo §11.

**Scope mỗi lần chạy** (tính bằng máy, không để LLM tự chọn):
1. `git diff --name-only HEAD@{7 days ago}` ở cả 2 repo, lọc `.py/.sh`, trừ danh sách loại trừ ở §3;
2. cộng **hot-core cố định** dù không đổi: `trading_bot/{plan,executor,brokers,config,plan_funding_gate}.py`,
   `bot_execute.py`, `mike/bin/{dispatch,ops_health_check,wags_autofix,ops_autofix}.sh` — mỗi tuần
   chỉ review **1 file hot-core theo vòng** (round-robin) để không quá tải;
3. trần 25 file/lần — vượt thì ưu tiên theo số commit chạm trong tuần, phần rớt **phải in ra** ("no
   silent caps").

**Agent**: native `code-reviewer` (file `~/.claude/agents/code-reviewer.md`, tools Bash/Read/Grep/Glob
— **read-only**, không Edit/Write), prompt bắt buộc:
- mỗi finding = `file:line` + **category** (`correctness` / `guideline:§N` / `dead-code` /
  `duplicate-formula` / `perf` / `simplification`) + severity + **bằng chứng** (đoạn code, output
  lệnh) + hành động đề xuất + **owner** (bảng §6);
- **cấm kết luận "không ai gọi" nếu chưa `grep -rn`** (CLAUDE.md bẫy srcwalk #2); cấm gắn nhãn
  `dead-code` cho bất kỳ file trong danh sách loại trừ;
- **cấm chạy dispatcher/checker ở chế độ live** để "xem thử" (luật mới `ops_runbook.md` 2026-08-23);
- phải tách "không tìm thấy bằng chứng" khỏi "tìm thấy và xấu" (§28, ops_runbook "3 luật checker").
- Check chuyên biệt cho repo này (đã cắn thật, LLM đáng tiền hơn regex ở đây):
  `duplicate-formula` — công thức NAV/cash §25 chép tay ở nhiều consumer (ca egg 08-18/08-19);
  `shared-file-no-account-filter` — đọc `dnse_raw_*.jsonl` mà không lọc `accountNo` trước phép
  tính (§12); `bare-datetime-now` — `datetime.now()`/`date -Iseconds` không neo TZ (§16, ca hôm
  nay `notify_thread.sh`); `assert-on-live-state` trong selfcheck (§23 hệ luận 1).

**Verify trước khi báo** (chống finding "nghe hợp lý nhưng sai"): mỗi finding severity ≥ medium đi
qua 1 lượt phản biện độc lập (pattern quant-skeptic: "cố bác bỏ, mặc định bác nếu không chắc") trước
khi vào báo cáo — dùng ngay skill `/code-review` mode `high` (có sẵn ReportFindings + verify pass)
thay vì viết lại. Finding bị bác → ghi vào phụ lục "đã bác" để tuần sau không lặp.

**Đầu ra**: `mike/reports/code_quality/code_quality_<YYYY-MM-DD>.md` + 1 bus `finding` topic
`code-quality-weekly-<date>` + 1 tin tóm tắt vào topic **Architecture** (`1521475726329516122`,
cùng nơi Wags/arch-reviewer). **Không** post Trading Daily (không phải alert vận hành). Tổng hợp
tuần nào không có finding nào ≥ medium thì vẫn 1 dòng "0 finding, N file đã quét" — im lặng hoàn
toàn không phân biệt được với pipeline chết (quy ước heartbeat đã có).

**Không làm**: không sửa file, không commit, không mở PR, không đóng/mở bus question thay người,
không chấm điểm "chất lượng code" bằng con số tổng (vô nghĩa, tạo áp lực sai).

## 5. Tầng 3 + vòng tốt nghiệp — cách hệ tự cải thiện dần (tuần 3 →)

**Sổ cái** `kb/code_quality_ledger.json` (máy ghi, người đọc): mỗi finding có `id`, `category`,
`file`, `first_seen`, `last_seen`, `weeks_seen`, `status ∈ {open, fixed, rejected, graduated}`,
`decided_by` (§20: chỉ ghi `user` khi user thật sự quyết).

Luật vận hành sổ cái — **thuần cơ học, không cần LLM**:
1. `weeks_seen ≥ 2` **và** category có dạng cú pháp (`bare-datetime-now`, import thừa, shared-file
   filter…) ⇒ script tự mở 1 bus `question` topic `code-quality-graduate: <category>` đề xuất viết
   gate Tầng 1 (pre-commit) — Wags làm, arch-reviewer audit, như mọi tooling khác.
2. `weeks_seen ≥ 2` **và** category là phán đoán (`simplification`, `perf`) ⇒ **không** escalate
   lại — chỉ giữ trong báo cáo, đánh dấu "đã nêu tuần N" (tránh vòng lặp tự nuôi, cùng lý do
   ops_health_check không re-trigger wags-fix).
3. Finding `rejected` bởi người ⇒ category+file đó **mute 8 tuần**; LLM tuần sau nhận danh sách mute
   trong prompt. Đây là cách "dạy" reviewer bằng quyết định thật thay vì sửa prompt tay.
4. Finding `fixed` ⇒ tuần sau script xác minh bằng artifact (grep/ruff trên HEAD), không tin
   commit message (MIKE.md quy chuẩn 2).

**Khi user/Mike duyệt fix**: dispatch **đúng owner** với `--write-scope` khai file, yêu cầu chạy
selfcheck **theo phạm vi** (§23, `selfcheck_scope_map.sh` + `grep -rl`), và với `trading_bot/*`
thêm quant-skeptic/arch-reviewer như mọi thay đổi production. Không có "fix hàng loạt".

## 6. Owner theo vùng (để finding có địa chỉ, không trôi)

| Vùng | Owner fix | Reviewer bắt buộc |
|---|---|---|
| `trading_bot/`, `bot_execute.py`, `deploy_golive_dt5g_v4/` | Taylor | arch-reviewer (và quant-skeptic nếu đổi logic sizing/tín hiệu) |
| `mike/bin/*.sh`, `mike/bin/*.py` điều phối | Wags | arch-reviewer |
| `mike/kb/*` | Mike (qua `.proposed` §13) | — |
| Script phân tích/R&D ở root (không phải `test_*`/`exp_*`) | Taylor | chỉ khi finding là `correctness` |

## 7. Đo xem nó có đáng tiền không — điều kiện SUNSET ghi sẵn

Theo dõi 6 tuần trong chính báo cáo tuần (1 bảng nhỏ, máy tính):
- `findings_confirmed / findings_raised` (tỷ lệ qua verify) — mục tiêu ≥ 0,5; dưới 0,3 hai tuần liền ⇒ siết prompt/scope;
- `accepted_by_human / confirmed` — dưới 0,2 sau 6 tuần ⇒ **tắt Tầng 2**, giữ Tầng 1 (gate rẻ vẫn đáng);
- số gate mới "tốt nghiệp" (đích: ≥1 gate/tháng trong 2 tháng đầu — có 4 ứng viên sẵn ở §4);
- số sự cố trong `kb/incidents/` có root cause thuộc lớp mà gate đã chặn (chỉ báo muộn, đọc theo quý).

Chi phí: 1 dispatch LLM/tuần cỡ `weekly_ops_audit.sh` (Opus/high, read-only) + ruff ≈ 0. Không thêm
daemon, không thêm thread Discord, không thêm cron ngoài 1 dòng Chủ Nhật.

## 8. Trình tự triển khai & cổng duyệt

| Tuần | Việc | Cổng |
|---|---|---|
| 1 | Wags: cài ruff + baseline + gate ratchet + selfcheck; đăng ký cron_registry | arch-reviewer CONFIRMED; user xem báo cáo baseline (số lỗi theo thư mục) |
| 2 | Mike: viết `code-reviewer.md` + `code_quality_weekly.sh` (chạy TAY 1 lần, chưa cron) | user đọc báo cáo đầu tiên, quyết có bật cron |
| 3 | Bật cron CN 10:00; bắt đầu ledger | — |
| 4–8 | Vận hành; vòng tốt nghiệp; bảng đo §7 trong mỗi báo cáo | Tuần 8: quyết giữ/tắt Tầng 2 theo §7 |

Việc đầu tiên nếu duyệt: dispatch Wags làm Tầng 1 (tuần 1). Tầng 2 chỉ bắt đầu khi Tầng 1 đã CONFIRMED.
