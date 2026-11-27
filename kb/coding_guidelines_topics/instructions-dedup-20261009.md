---
kind: coding-guideline-topic
title: "Instructions Dedup Archive 2026-10-09"
owner: Mike
status: canonical
updated: 2026-11-27
---

# Instructions Dedup Archive 2026-10-09

> Tách nguyên văn từ [`../coding_guidelines_ext.md`](../coding_guidelines_ext.md) (2026-11-27, giữ trần <40 KB).

## Dọn 2026-10-09 (instructions-dedup)

> Nguyên văn các khối chuyển từ `kb/coding_guidelines.md` (job `Wags_20261009_153812`, user duyệt 09/10,
> chế độ A: di chuyển, không viết lại). Không auto-load.
> Một số khối là MẢNH câu tách từ mục cùng số ở file chính — đọc kèm mục đó, không đọc riêng.

### §8c

- ⚠️ **Bẫy git đã cắn 2 lần khi xây đúng bộ cổng này**: `git show <rev>:<path>` tính path từ **GỐC
  REPO**, còn `git diff … -- <pathspec>` tính từ **CWD**. Nhầm một cái ⇒ diff rỗng ⇒ cổng **im lặng
  cho qua**. Dùng `:(top)` cho pathspec, và `rev-parse --show-prefix` cho `show`.
- ⚠️ **Đọc không được bản cũ ≠ sạch**: cả 2 cổng đều phải nói thẳng "KHÔNG GATE được" thay vì coi
  mọi thứ là mới (nếu không sẽ phun hàng trăm vi phạm giả và bị tắt hẳn trong một ngày).

### §16

**Cưỡng chế cơ học từ 2026-08-30 (user duyệt) — `bin/tz_anchor_gate.py`, pre-commit ở CẢ 2 repo**
(`mike/.pre-commit-config.yaml` + `/home/trido/thanhdt/.pre-commit-config.yaml`). Lý do bật: luật
văn xuôi này có từ 2026-07 mà code-quality-weekly 2026-08-30 vẫn tìm ra **5 vi phạm cùng lớp trong
1 tuần** (WC `20bf2f20`, mike `b26008a6`) — tất cả LATENT vì host ở +07 + crontab export che mất.
Phát hiện bằng **AST** (regex đếm sai: `datetime.now(tz)` vs `datetime.now()` chỉ khác ở việc CÓ
ARGUMENT, mà argument viết xuống dòng được), **ratchet per-file** so với
`kb/tz_anchor_baseline.json` (kiểm kê ngày bật: **157 vi phạm / 87 file**) — nợ cũ không bắt sửa
ngay, chỉ không được TĂNG. Cho qua: `datetime.now(_ICT)`, `datetime.now(ZoneInfo(...))`,
`datetime.now(timezone.utc)` (bước 1 của ICT-anchor). CHƯA phủ: `pd.Timestamp.now()`,
`date` trong bash, `datetime.fromtimestamp()`, và file .py NGOÀI `WorkingClaude/` (20 worktree
của repo ngoài — gate KÊU ra stderr nhưng không chặn được). Ba lối thoát, hệ quả KHÁC nhau:
`SKIP=tz-anchor-gate` (bị chặn do lệch nhánh — baseline neo theo canonical) · `MIKE_TZ_GATE=warn`
(qua 1 lần, **không** nâng baseline, lần sau vẫn chặn — cố ý khác `code_quality_gate.sh`) ·
`--update-baseline` (chỉ HẠ được; nâng phải thêm `--accept-new-debt`). Hook repo ngoài đi qua shim
`WorkingClaude/tz_anchor_gate_shim.sh` vì `.gitignore` của repo đó ẩn chính `WorkingClaude/mike/`
⇒ trỏ `entry` thẳng vào repo lồng sẽ hỏng cứng trong mọi worktree/clone mới. Selfcheck
`bin/tz_anchor_gate_selfcheck.py [--mutations|--all-tz]` — **137 assertion, 38/38 mutation bị giết
(34 trên gate .py + 4 trên shim .sh), đo dưới `$DNA_PYEXE`** (interpreter mà
`run_selfchecks.sh`/`selfcheck_weekly_baseline_check.sh` dùng thật; selfcheck tự đếm và tự in con
số nên không bao giờ lệch).
⚠️ **Hook chạy `python3` (3.10) còn 2 runner selfcheck chạy `$DNA_PYEXE` (3.12) ⇒ 7 file .py của
repo ngoài chỉ parse được ở 3.12** (f-string PEP 701). Gate phân biệt "không parse được" với
"sạch": KÊU ra stderr, KHÔNG gate file đó và KHÔNG đụng baseline của nó. Trước bản vá vòng 5 nó
trả 0 vi phạm im lặng rồi XOÁ key baseline ⇒ commit sau bị hard-block oan. Hệ quả vận hành:
`--seed-baseline` chạy bằng 3.10 sẽ TỪ CHỐI ghi (kiểm kê thiếu) — re-seed bằng `$DNA_PYEXE`.
Hook PHẢI có `verbose: true` ở cả 2 config: pre-commit chỉ in output hook khi rc≠0 hoặc verbose,
mà gate này cố ý fail-open ⇒ thiếu verbose thì fail-open thành fail-silent.
Ba biến `MIKE_TZ_GATE_ROOT/_BASELINE/_ROOTS` chỉ dành cho sandbox selfcheck và bị TỪ CHỐI nếu
thiếu `MIKE_TZ_GATE_SELFCHECK=1` (một biến sót lại đủ biến gate thành no-op im lặng).

**Mở rộng 2026-09-05 (user duyệt Discord) — RULE 2 cùng script, namespace baseline RIÊNG**
(`tdays_files` cạnh `files`, ratchet độc lập): chặn gọi hàm tên KHỚP TUYỆT ĐỐI `tdays` (không
phân biệt hoa/thường) trừ khi CHÍNH lệnh gọi đó có `vn_holidays=` (per-call), HOẶC hàm bao quanh
có tham chiếu `trading_bot.vn_market.is_holiday` (khớp tuyệt đối, per-scope). Sự cố gốc:
`macro_healthcheck.py::tdays()` dùng `np.busday_count` trần, nghỉ Quốc khánh 31/08→02/09 khiến
tuổi dữ liệu thật 1 phiên bị đếm thành 4 "trading day" ⇒ `macro_health=FAILED` giả, DT5G tắt qua
đêm — call-site thứ 3 của CÙNG lớp lỗi trong 2 ngày (`0b83f507`, `81cc0428` ở `mike/bin/`, rồi
`96ebd124` ở repo ngoài; `kb/incidents/2026-09/2026-09-04-macro-health-failed-holiday-tdays.md`).
Cố ý KHÔNG quét mù `np.busday_count` hay biến thể tên (`get_tdays`) — rủi ro false-positive cao
(biến thể tên từng tự bắt nhầm chính `tdays_violations()`/`test_*_tdays()` của gate/selfcheck khi
chạy `--scan` thật lần đầu). ⚠️ Bản đầu ân xá `vn_holidays=` theo CẢ SCOPE (không phải per-call) —
arch-review vòng 1 phát hiện no-op trên chính file gây sự cố: revert dòng vá thật về đúng bug SEV1
gốc vẫn KHÔNG bị bắt vì marker khác trong cùng scope còn sống; đã sửa thành per-call trước khi
commit. *→ docstring đầu `bin/tz_anchor_gate.py` (RULE 2).*

### §29 (mảnh dọn từ mục 29 của `coding_guidelines.md`, KHÁC "## 29." cron_health_check ở trên)

**Nửa CƠ HỌC đã tự động hoá — `bin/diagnosis_evidence_gate.py`** (pre-commit, `files:
^(bin|hooks)/.*\.sh$`): chặn cứng dạng thứ nhất (`2>/dev/null` + `|| die "…"`). Đo thật trước
khi chốt: 0 false-positive trên toàn bộ `bin/*.sh` + `hooks/*.sh` ở HEAD, và fire đúng dòng 108
của `git show 55b3f34c^:bin/append_event.sh` (bản đúng lúc lỗi). Bỏ qua có chủ đích:
`MIKE_DIAG_GATE=warn|off`.
