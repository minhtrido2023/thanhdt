---
kind: design
title: Multi-CLI dispatch — provider layer cho dispatch.sh (claude / opencode / codex)
owner: Mike
status: ĐÃ IMPLEMENT (claude + opencode LIVE; codex enabled=false chờ user login)
date: 2026-08-03
---

# ⚠️ ĐỌC MỤC NÀY TRƯỚC — bản gốc bên dưới SAI vài chỗ, arch-reviewer đã bác

Phần từ "# Multi-CLI dispatch" trở xuống là **bản đề xuất GỐC**, giữ nguyên làm dấu vết audit.
arch-reviewer trả **NEEDS_CHANGES (high)** với 11 required_changes. Những gì đã đổi khi build:

| Bản gốc nói | Thực tế |
|---|---|
| §5.1 "heartbeat do Stop hook ghi" ⇒ cần degrade `log-mtime` | **SAI.** `hooks/stop.sh`→`heartbeat.sh` chỉ ghi `bus/registry/<id>.json`; `grep -rn append_event hooks/` **rỗng**; `_hb_age` (`mike_json.py:547-559`) chỉ đọc `bus/inbox/`. Heartbeat nuôi `_hb_aware_timeout` đến từ dòng `append_event.sh` **trong prompt** (`dispatch.sh:686-687`) — bash thuần, **vốn đã provider-agnostic**. `log-mtime` bị **bỏ hẳn**: vừa thừa vừa là tín-hiệu-sống-giả đúng loại mà `_is_watcher_event` sinh ra để diệt. `_hb_aware_timeout` **không sửa 1 dòng nào**. |
| Artifact 3 `render_agent_profile.sh` + sinh `AGENTS.md` + flatten `@import` | **Không cần.** opencode đọc thẳng `CLAUDE.md` từ `--dir` (đã kiểm chứng) và có cơ chế native `instructions` nhận đường dẫn tuyệt đối. Thay bằng **`agents/<id>/opencode.json`** — file khai báo, track git, KHÔNG phải file dẫn xuất ⇒ triệt tiêu luôn race + nguy cơ bị `git add -A` cuốn (§13). |
| Phase 0: resolver in argv NUL-delimited, dispatch eval lại | **Bất khả thi**, đã đo: NUL bị `$( )` nuốt; array bash không vượt được `bash -c '_bg_wrapper'`. Thay bằng **`_build_argv()` dựng array bash NGAY TRONG `_bg_wrapper`**; registry chỉ trả FIELD, **không bao giờ vận chuyển argv**. |
| §9.1 `allow_agents` = gate read-only | **Phản tác dụng** — bản gốc chọn đúng Taylor (sở hữu `data/trading_rules.json` mà `bot_execute.py` đọc) + Wags (sửa `dispatch.sh`). Nay gate thật = `permission` pattern-map trong `opencode.json` (**đã kiểm chứng cưỡng chế lúc chạy**), `allow_agents` chỉ là đai thứ hai và **được ghi rõ là không airtight** (lỗ hổng chuyển hướng `>`). |
| §9.3 "opencode chưa cài" | Đã cài `opencode-ai@1.18.11`. Và nó là **ELF binary native** ⇒ **chạy được dưới PATH crontab**, khác codex (shim `#!/usr/bin/env node`, chết vì `/usr/bin/node`=v12.22.9 < `engines>=16`) — nên codex cần `env.PATH` pin interpreter. |
| — (không nêu) | **Bug production có sẵn**, arch-reviewer F9: `resume_pending.py` xoá record TRƯỚC `fire()`, **không kiểm `returncode`**, rồi notify "đã resume" vô điều kiện ⇒ dispatch fail = task chết + user nhận báo thành công giả. Nhánh `usage_limit` còn **mất luôn model/effort** (trái docstring của chính nó). Đã sửa cả 3 + thêm `provider`. |

**Đã build** (tất cả đã chạy thật, không phải chỉ viết ra):
`kb/cli_providers.json` · `bin/cli_provider.sh` · `bin/dispatch.sh` (`--provider`, `_build_argv`,
probe usage/turn-cap theo provider, circuit-breaker key `agent@provider`) ·
`agents/{Taylor,Winston,Wendy,Spyros,Wags}/opencode.json` · `bin/cli_provider_selfcheck.sh` ·
`bin/resume_pending.py` + `bin/mike_json.py` (field `provider`).

**Bằng chứng**: `cli_provider_selfcheck.sh` 16/16 PASS + mutation test FAIL đúng 5 ca argv claude ·
`dispatch_discord_topic_selfcheck.sh` 42/42 PASS (không regression) · `shellcheck_gate.sh` rc=0 ·
dispatch thật `Wendy_20260803_033110` qua opencode: `status=done`, `provider=opencode`,
`turn_cap=unsupported`, 2 bus event đúng `trace_id`, 17s.

**Còn nợ**: xem `verify_opencode_adapter_20260803.md` (§"Chưa kiểm được") + required_changes #5
(`done_unconfirmed` / auto-verify closure) **chưa làm** — xem cuối file.

---

# Multi-CLI dispatch — thiết kế provider layer (BẢN GỐC, giữ làm dấu vết)

**Mục tiêu (user, 2026-08-03):** `bin/dispatch.sh` hiện chỉ chạy được `claude`. Mở rộng để
dispatch được sang CLI khác (codex, opencode, antigravity…) nhằm **tận dụng thế mạnh của
nhiều model khác nhau**, với **một nơi duy nhất để config** — tham khảo cách Paseo làm.

## 0. Paseo làm thế nào (đã tra, để không thiết kế lại từ đầu)

Paseo (`getpaseo/paseo`, hỗ trợ 39 agent CLI) dùng **2 tầng**:
1. **First-class adapter viết bằng code** cho từng CLI có quirk riêng (`claude`, `codex`, …).
2. **Một protocol chung (ACP — Agent Client Protocol)** để mọi agent tuân thủ ACP cắm vào mà
   không cần code adapter mới.

Config: **1 file JSON duy nhất** `~/.paseo/config.json`, khai báo dưới `agents.providers.<id>`:

| Field | Ý nghĩa |
|---|---|
| `extends` | kế thừa từ provider first-class (`claude`/`codex`/…) hoặc `"acp"` |
| `label` | tên hiển thị |
| `env` | biến môi trường cho tiến trình |
| `command` | (ACP) lệnh spawn agent |
| `models` / `additionalModels` | thay hẳn / gộp thêm danh sách model |
| `disallowedTools` | tắt tool không hỗ trợ |
| `enabled` | bật/tắt provider |

Điểm mấu chốt Paseo tự nêu: *"mỗi agent chạy như tiến trình riêng bằng chính CLI của nó,
Paseo KHÔNG sửa/bọc hành vi của chúng"*. Đây đúng là mô hình dispatch.sh đang có
(`claude -p` = tiến trình OS độc lập) ⇒ **không cần đổi kiến trúc, chỉ cần tách adapter**.

**Khác biệt quan trọng với fleet mình:** Paseo là orchestrator đa-người-dùng, integration
surface là ACP/JSON-RPC. Fleet Mike đã có sẵn một integration surface **rẻ hơn và phù hợp
hơn: BUS**. `bin/append_event.sh` là bash thuần — **bất kỳ CLI nào chạy được shell đều ghi
được bus**. Nên fleet mình KHÔNG cần ACP; cần đúng 1 hợp đồng: "CLI nào cũng phải kết thúc
bằng 1 bus event mang `trace_id=<job_id>`".

## 1. Nguyên tắc thiết kế

> **Orchestration giữ nguyên 100% provider-agnostic. Chỉ tách phần CLI-specific ra adapter.**

Phần **KHÔNG đụng tới** (đã provider-agnostic sẵn, chỉ đọc job record + bus + logfile):
job board `bus/jobs/`, circuit breaker, `_hb_aware_timeout`, `_job_watcher`, Discord routing
(`_job_thread_id`/`--thread`), retry loop, `consolidate.sh`, notify, usage-limit auto-resume,
guards self-dispatch/target-Mike.

Phần **PHẢI tách ra** — đúng 6 trục CLI-specific:

| # | Trục | claude hôm nay | codex |
|---|---|---|---|
| 1 | **argv** | `-p "$P" --permission-mode auto --max-turns N --model M --effort E` | `exec -C DIR -m M -c model_reasoning_effort="E" --dangerously-bypass-approvals-and-sandbox` |
| 2 | **profile/identity** | `cd $AGENT_DIR` → `CLAUDE.md` + `@import` native | `AGENTS.md`, **không hiểu `@import`** ⇒ phải flatten |
| 3 | **hooks runtime** | `.claude/settings.json` → SessionStart/Stop (bơm working memory, heartbeat) | có hook riêng, schema khác; coi như **none** ở v1 |
| 4 | **heartbeat** | Stop hook ghi bus mỗi lượt ⇒ nuôi `_hb_aware_timeout` | **không có** ⇒ phải degrade |
| 5 | **phân loại lỗi** | `"Reached max turns"` (`:361`), `USAGE_LIMIT_PHRASE_RE` (`usage_limit_phrases.sh:27`) | wording khác |
| 6 | **lấy câu trả lời cuối** | `tail -c 500 logfile` (`:856`) | `-o <FILE>` (sạch hơn hẳn) |

**Tiền lệ đã trả giá:** `kb/incidents/2026-08/2026-08-02-ccdb-bridge-115-commits-behind-upstream.md:47-51`
đã ghi nhận **đúng lớp lỗi này ở repo khác** — truyền effort thang Claude (`"max"`) sang
`CodexRunner` vốn chỉ có `model_reasoning_effort`. Tức trục #1 không phải rủi ro lý thuyết.

## 2. Artifact 1 — `kb/cli_providers.json` (nơi config duy nhất)

Bắt chước **đúng pattern `kb/discord_channels.json`** mà fleet đã tin dùng: 1 registry JSON
có `_README` inline + 1 resolver script + fail-loud khi không phân giải được.

```jsonc
{
  "_README": ["REGISTRY DUY NHAT khai bao CLI provider cho bin/dispatch.sh.",
              "Them CLI moi = them 1 entry o day, KHONG sua dispatch.sh."],
  "default_provider": "claude",
  "providers": {
    "claude": {
      "label": "Claude Code",
      "bin": "/home/trido/.local/bin/claude",
      "enabled": true,
      "argv": {
        "base":     [],
        "prompt":   ["-p", "{PROMPT}"],
        "cwd":      "chdir",                      // dispatch cd vào AGENT_DIR
        "model":    ["--model", "{MODEL}"],
        "effort":   ["--effort", "{EFFORT}"],
        "turns":    ["--max-turns", "{TURNS}"],
        "autonomy": ["--permission-mode", "auto"]
      },
      "models": ["sonnet", "opus", "haiku", "fable"],
      "default_model": null,                       // omit ⇒ giữ default cua CLI
      "efforts": ["low", "medium", "high", "xhigh", "max"],
      "effort_caps": { "fable": "high" },           // chinh sach user 2026-07-14
      "profile":   { "mode": "file", "filename": "CLAUDE.md", "imports": "native" },
      "hooks":     "claude-settings",
      "heartbeat": "bus-hook",
      "final_message": { "mode": "log_tail", "bytes": 500 },
      "failure_patterns": {
        "usage_limit": "@bin/usage_limit_phrases.sh",
        "max_turns":   "Reached max turns"
      },
      "usage_probe": "@bin/usage_watch.py",          // doc ~/.claude/projects — xem §5.4
      "allow_agents": "*"
    },

    "codex": {
      "label": "OpenAI Codex CLI",
      "bin": "/home/trido/.nvm/versions/node/v22.23.0/bin/codex",
      "enabled": false,                            // BAT sau khi `codex login`
      "argv": {
        "base":     ["exec", "--skip-git-repo-check"],
        "prompt":   ["{PROMPT}"],                  // positional (hoac stdin)
        "cwd":      ["-C", "{CWD}"],
        "model":    ["-m", "{MODEL}"],
        "effort":   ["-c", "model_reasoning_effort=\"{EFFORT}\""],
        "turns":    null,                          // KHONG HO TRO — khai bao that
        "autonomy": ["--dangerously-bypass-approvals-and-sandbox"],
        "final_msg":["-o", "{FINAL_MSG_FILE}"]
      },
      "models": ["gpt-5.1-codex", "gpt-5.1-codex-mini"],
      "efforts": ["low", "medium", "high"],
      "profile":   { "mode": "file", "filename": "AGENTS.md", "imports": "flatten" },
      "hooks":     "none",
      "heartbeat": "log-mtime",
      "final_message": { "mode": "file" },
      "failure_patterns": { "usage_limit": "...", "max_turns": null },
      "usage_probe": null,                           // KHONG duoc dung probe cua claude (§5.4)
      "allow_agents": ["Taylor", "Wags"]             // v1: chi viec research/read-only (§9.1)
    }
  }
}
```

**Thêm 1 CLI mới = thêm 1 entry, không sửa `dispatch.sh`.** Đó là yêu cầu "một nơi có thể
config" của user.

## 3. Artifact 2 — `bin/cli_provider.sh` (resolver, mirror `bin/discord_channel.sh`)

```bash
bin/cli_provider.sh argv <provider> --agent-dir D --prompt-file F \
    [--model M] [--effort E] [--turns N] [--final-msg FILE]
# → in ra argv (NUL-delimited) để dispatch.sh eval an toàn
bin/cli_provider.sh field <provider> <key>      # vd: heartbeat, hooks, profile.mode
bin/cli_provider.sh list                        # provider nào enabled
```

**Fail-loud, không bao giờ âm thầm rơi về claude**: provider không tồn tại / `enabled:false` /
`bin` không có trên PATH ⇒ **exit 1, huỷ dispatch**. Cùng kỷ luật với `--thread` (2026-08-02:
"caller đã nêu đích danh thì không đoán").

**Prompt truyền qua FILE, không qua argv string.** Prompt fleet dài hàng chục KB, đầy `"` và
`` ` `` tiếng Việt — chính lớp lỗi §15 coding_guidelines (4 sự cố quoting 07-17→08-01). File
+ stdin cắt hẳn lớp lỗi này cho MỌI provider.

## 4. Artifact 3 — `bin/render_agent_profile.sh <agent> <provider>`

- `imports: native` (claude) → **no-op**, giữ nguyên hành vi hôm nay.
- `imports: flatten` (codex/…) → đọc `agents/<id>/CLAUDE.md`, thay mỗi dòng `@/abs/path.md`
  bằng nội dung file đó, ghi ra `agents/<id>/<filename>` (vd `AGENTS.md`).
  - Idempotent: so content-hash, không đổi thì không ghi (tránh churn git + mtime giả).
  - Thêm `agents/*/AGENTS.md` vào `.gitignore` — đây là **file dẫn xuất**, không phải config
    (khác chủ ý "agents/ configs ARE tracked" hiện có).
  - 8 agent hiện có đều dùng `@import` (Taylor/Mike → `context_pack.md` full; Wags →
    `context_ops_mini.md`; còn lại role-scoped) ⇒ flatten phải giữ đúng tier từng agent,
    không bơm full pack cho mọi provider (đó là cost-opt #1b đã tốn công sửa).

## 5. Ba chỗ SUY GIẢM — phải khai báo, tuyệt đối không giả vờ

Đây là phần dễ sai nhất, và đúng lớp lỗi fleet vừa trả giá 6 vòng trong saga discord-routing:
*cơ chế không tồn tại nhưng code hành xử như thể nó tồn tại*.

**5.1 Heartbeat → deadline.** `_hb_aware_timeout` gia hạn deadline khi bus heartbeat của agent
còn tươi. Heartbeat đó do **Stop hook của Claude Code** ghi. Provider `hooks: none` ⇒ không có
heartbeat ⇒ mọi job codex bị **giết cứng đúng TIMEOUT**, kể cả đang chạy tốt (chính 2 sự cố
Winston_20260707 / Wags_20260709 đã sinh ra cơ chế này).
→ Adapter khai báo `heartbeat: "bus-hook" | "log-mtime" | "none"`.
`log-mtime`: gia hạn khi **logfile được ghi thêm trong `HB_FRESH_S` vừa qua** (codex stream
output liên tục ⇒ tín hiệu thật). Yếu hơn bus-heartbeat nhưng **trung thực và có thật**, hơn
hẳn hard-kill. `none` ⇒ không gia hạn, ghi rõ trong job record để triage không đoán mò.

**5.2 Working memory + directive.** `hooks/session_start.sh` bơm `kb/memory/<id>.md` (working
memory agent tự ghi qua `remember.sh`) + directive mới. Provider `hooks: none` **mất sạch**.
→ `dispatch.sh` khi thấy `hooks: none` thì **prepend** 2 khối đó vào prompt file. Cùng nội
dung, khác đường vào — không mất tính liên tục giữa các phiên.

**5.3 Turn cap.** codex không có `--max-turns` ⇒ toàn bộ nhánh
`_maybe_schedule_maxturns_resume` (auto nâng trần + resume) là **dead code** ở đó.
→ `turns: null` ⇒ dispatch.sh **bỏ hẳn nhánh đó**, không bịa. Job record ghi
`turn_cap: "unsupported"` để người đọc job board không tưởng có lưới an toàn.

**5.4 ⚠️ Usage-limit probe đọc NHẦM tài khoản — bug thật, không phải suy giảm.**
`_looks_like_usage_limit()` (`dispatch.sh:284-299`) có 2 tầng: (a) khớp phrase trong log,
(b) **đối chứng bằng `bin/usage_watch.py --oneline`** — mà `usage_watch.py:22` đọc
`~/.claude/projects`, tức **usage của CLAUDE**. `_parse_reset_epoch` cũng lấy giờ reset từ đó
(`:326-328`).
⇒ Một job **codex** fail vì lý do bất kỳ, đúng lúc quota **claude** đang ≥95%, sẽ bị phân loại
nhầm thành "usage-limited", đẩy vào `bus/pending_resumes/` và **hẹn resume theo giờ reset của
claude** — sai tài khoản, sai giờ, lại còn không trip circuit breaker (cố ý bỏ qua). Job hỏng
thật sẽ lặng lẽ retry 3 lần rồi im.
→ Registry khai báo `usage_probe` per-provider (`"@bin/usage_watch.py"` cho claude, `null` cho
provider chưa có probe). `null` ⇒ **chỉ dùng tầng (a) phrase-match**, không đối chứng, không
đoán giờ reset (dùng buffer mặc định 5h). Đây là lỗi phải sửa **trong Phase 2**, không được để
lại "làm sau".

## 6. Closure trở thành hợp đồng phổ quát (nối với `kb/dispatch_output_contract.md`)

Với claude, exit-code + hooks + log còn cho vài tín hiệu phụ. Với CLI khác, **bus event là
tín hiệu closure DUY NHẤT đáng tin**. Nên đề xuất kèm:

`dispatch.sh` **tự verify** sau mỗi lần chạy — nó đã có sẵn `job_id`, đã inject
`[DISPATCH … job=$job_id]` và đã dặn agent `append_event.sh … '$job_id'` làm trace_id:

```bash
# sau khi rc==0, TRƯỚC khi JSET status=done:
if ! python3 bin/mike_json.py has-event-trace bus "$id" "$job_id"; then
   JSET status=done_unconfirmed …     # KHÁC 'done': chạy sạch nhưng không có kết quả máy-đọc-được
fi
```

Lợi ích kép: (a) bịt đúng lỗ hổng "6/10 pipeline dispatch nền không có bước kiểm hậu-điều-kiện"
mà `dispatch_output_contract.md` đang phải yêu cầu **từng caller tự viết** — làm 1 lần ở
dispatch.sh là phủ hết; (b) là lưới duy nhất cho provider không có hooks.
⚠️ Trạng thái mới `done_unconfirmed` ≠ `failed` — không được để nó trip circuit breaker
(chạy được nhưng không báo cáo ≠ agent hỏng).

## 7. Model routing thành 2 chiều — KHÔNG tự dịch tier giữa provider

MIKE.md §Model routing hiện là ladder 1 chiều `sonnet → opus → fable`. Đa provider thành
`provider × model`.

- `dispatch.sh` thêm `--provider NAME` (mặc định `default_provider` = claude ⇒ **mọi lệnh
  dispatch hiện có chạy y nguyên, 0 thay đổi hành vi**).
- `--model` validate theo **danh sách của provider đó**, sai ⇒ exit 1.
- **KHÔNG map alias tier xuyên provider** (kiểu `--model opus` tự thành `gpt-5.1-codex`).
  Đổi model ngầm chính là lớp sự cố model-drift 07-17 đã đo được. Muốn dùng codex thì nêu
  đích danh `--provider codex --model gpt-5.1-codex`.
- Ladder Q1/Q2/Q3 thêm **Q0: việc này có lý do cụ thể để dùng CLI khác không?** (vd cần
  second-opinion khác họ model, hoặc rate-limit claude đã cạn). Không có lý do ⇒ claude.
  Chống đúng thói "phản xạ chọn tier/CLI nghe có vẻ mạnh hơn".

## 8. Phân kỳ triển khai (mỗi phase tự verify được)

| Phase | Nội dung | Điều kiện PASS |
|---|---|---|
| **0** | `kb/cli_providers.json` + `bin/cli_provider.sh` + dispatch.sh gọi resolver cho provider `claude` | **argv sinh ra giống HỆT chuỗi hôm nay** (so byte-for-byte, in ra `set -x`). 0 thay đổi hành vi. Selfcheck lại toàn bộ `dispatch_discord_topic_selfcheck.sh` 42/42 |
| **1** | Prompt qua file + `render_agent_profile.sh` (flatten) | Flatten Taylor/Wags giữ đúng tier context; diff nội dung khớp `@import` |
| **2** | Adapter `codex` + degrade heartbeat `log-mtime` + `turns:null` | **Chặn: cần `codex login` (interactive, user tự chạy)**. Smoke test: dispatch Wags 1 việc read-only, phải ra bus event đúng trace_id |
| **3** | Auto-verify closure (§6) + `--provider` + cập nhật MIKE.md §Model routing | Test inject: job không ghi event ⇒ phải ra `done_unconfirmed` |
| **4** | arch-reviewer audit (bắt buộc — đây là thay đổi điều phối fleet) | verdict ≠ NEEDS_CHANGES trên blast_radius / fail_silent |

## 9. Rủi ro đã nhận diện

1. **Provider mới không có sandbox/permission tương đương** — codex cần
   `--dangerously-bypass-approvals-and-sandbox` để chạy headless không hỏi. CLI đó sẽ có
   quyền ghi file thật. **Ranh giới cứng của fleet (không tự sửa plan/trading_rules/lệnh/
   crontab thực thi) hiện được thực thi bằng PROMPT + CLAUDE.md, không phải bằng sandbox** ⇒
   provider mới thừa hưởng đúng mức bảo vệ đó, không hơn không kém. Khuyến nghị v1: **chỉ cho
   provider ngoài claude nhận việc read-only/research**, khai báo `allow_agents: [...]` trong
   registry để chặn ở tầng resolver.
2. **`codex` chưa login** (đã kiểm 2026-08-03: `codex login status` → *Not logged in*) ⇒ Phase 2
   bị chặn cho tới khi user chạy `codex login`.
3. **opencode / antigravity chưa cài** trên máy này — thiết kế phủ được nhưng chưa test được.
4. **Không đụng `Agent()` native subagent** — đó là đường dispatch thứ 2 (in-process, dùng cho
   Wendy/data-ops/risk-auditor…), nằm ngoài phạm vi này.
5. **Còn 2 call-site gọi `claude` NGOÀI dispatch.sh, hardcode, không có env override:**
   `bin/verify_finding.sh:23,100-104` (gate quant-skeptic) và `bin/wags_autofix.sh:37,77-85`
   (gate arch-reviewer). Cả hai đọc **native subagent def** `~/.claude/agents/*.md` — khái
   niệm chỉ Claude Code có, KHÔNG port được sang codex bằng registry này.
   → **Cố ý để nguyên**: đây là 2 cổng KIỂM CHỨNG của fleet (quant-skeptic gate mọi thay đổi
   production, arch-reviewer gate mọi thay đổi điều phối). Giữ chúng trên một CLI/model đã
   hiệu chuẩn là tính năng, không phải nợ. Ghi rõ ở đây để lần sau không ai tưởng bỏ sót.
6. **Chưa có registry khai báo agent** — nguồn sự thật về roster đang rải 4 nơi và **đã lệch**:
   `ls agents/*/` = 8; `bin/fleet_housekeeping.sh:285` ROSTER = 9 (thừa `Bob`, không có
   `agents/Bob/`); model nằm rời trong 8 file `.claude/settings.json`; context tier chỉ có
   dạng **comment** ở `dispatch.sh:64-76`. Đa provider làm chỗ lệch này đắt hơn (thêm chiều
   "agent nào được chạy provider nào"). Không gộp vào scope này, nhưng `allow_agents` ở §9.1
   là bước đầu tiên đặt thông tin đó vào 1 file có thể grep.

## 10. Cái KHÔNG làm (và vì sao)

- **Không dùng ACP** như Paseo: fleet đã có bus làm integration surface, ACP thêm 1 protocol +
  daemon mà không giải quyết vấn đề nào fleet đang có.
- **Không viết `dispatch_v2.sh` song song**: 2 đường dispatch = 2 nơi phải sửa mỗi lần, đúng
  lớp lỗi "6 pipeline tự viết lại quy tắc mỗi nơi một kiểu" mà `dispatch_output_contract.md`
  vừa phải dọn. Sửa tại chỗ, Phase 0 chứng minh 0 regression.
- **Không port hooks sang provider khác** ở v1: mỗi CLI một schema hook riêng: chi phí cao,
  giá trị thấp so với cách prepend vào prompt (§5.2).

---

# NỢ CÒN LẠI sau vòng implement 2026-08-03 (đừng coi là đã xong)

1. **required_change #5 — closure auto-verify CHƯA LÀM.** Ý tưởng `done_unconfirmed` bị hoãn vì
   arch-reviewer chỉ ra `mike_json.py:854` `sys.exit(1)` gộp mọi status lạ thành FAILED ⇒ mọi
   poller (`jobs.sh status/wait`, `watchdog.sh`, vòng ScheduleWakeup) sẽ đọc thành job hỏng, và
   `wakeup_profile.py:87` lọc mất mẫu. Muốn làm phải sửa exit-code mapping TRƯỚC. Dữ liệu nền đã
   có: reviewer đo 5/300 job done trong 14 ngày (1,7%) không có event `trace_id` ⇒ nhiễu thấp,
   ý tưởng đáng làm. `has-event-trace` cũng chưa tồn tại — viết bằng `_inbox_files()`/
   `_agent_files()` để quét CẢ archive (§17), đừng tự glob hot-only.
2. **Streaming log chưa đo** — chưa có mẫu task opencode đủ dài để xác nhận log ghi dần hay chỉ
   ghi lúc thoát. Không chặn gì hiện tại (heartbeat đi qua bus, không qua log), nhưng
   `_job_watcher`'s anomaly track ("log trống 60s/stale 120s") có thể báo động giả cho opencode.
3. ~~codex `profile=prompt-inline` chưa wire~~ → **XONG 2026-08-03** (`bin/render_profile_prompt.sh`
   + nhánh `CLI_PROFILE=prompt-inline` trong `dispatch.sh`). Bơm: CLAUDE.md tổ tiên + CLAUDE.md
   agent (đã expand `@import`) + working memory. Verify: selfcheck CA 12/13. codex giờ chỉ còn
   chờ `codex login` + `enabled:true`. Cơ chế này dùng chung cho **antigravity** (`agy`).
4. **§5.2 recap_prev + directive** — `hooks/session_start.sh` bơm 3 thứ; `render_profile_prompt.sh`
   nay đã phủ **working memory**, còn **recap phiên trước** (`recap_prev.py` đọc transcript
   `~/.claude`, không có khái niệm tương đương cho CLI khác) và **directive** (`bus/directives/`)
   thì **chưa**. Directive là cái đáng làm tiếp — nó rẻ (đọc 1 file JSONL) và là kênh Mike giao
   việc thường trực.
5. **Nhiễm chéo còn lại** (arch-reviewer F10, đã sửa 3/6): đã sửa `usage_probe`, circuit-breaker
   key, wakeup bucket. **Chưa**: `context_watch.py`, `is_serving.py`, `wakeup_audit.py` vẫn neo
   `~/.claude` ⇒ fleet_health CTX/SERVING mù cho job non-claude; `spend_report.py` gom theo field
   `model` nên thống kê model-mix (chỉ số đã bắt sự cố model-drift 07-17) sẽ loãng khi tên model
   trải nhiều provider.
6. **Lỗ hổng chuyển hướng trong `permission.bash`** — pattern khớp trên chuỗi lệnh, `grep x y > z`
   vẫn ghi được file. Đã ghi rõ trong từng `opencode.json`. Muốn bịt thật phải có sandbox tầng OS
   (bubblewrap/container), ngoài phạm vi lần này.
