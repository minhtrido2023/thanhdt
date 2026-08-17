---
kind: operating-procedure
title: Mike model and provider routing
source: MIKE.md (OKF split 2026-08-15)
---

## Model routing — ladder 3 tầng theo độ phức tạp task (cập nhật 2026-07-14, user yêu cầu)

**Checklist thủ công SAU MỖI LẦN đổi model của chính Mike** (bài học sự cố schema-drift 07-06,
`kb/incidents/2026-07/`, tìm `2026-07-06-*`): hỏi thử "liệt kê các tham số của Agent tool hiện có",
khác §8 → cập nhật §8 + snippet `dispatch.sh` NGAY. Không xây cron cho việc này.
`bin/model_config_watch.py` (watchdog.sh mỗi 10') phòng thủ RIÊNG cho model CONFIG, không thay
được tool-schema drift ở trên.

`dispatch.sh` nhận `--model NAME` (`sonnet|opus|haiku|fable`, validate lúc parse — sai giá trị thì
exit 1 trước mọi side effect); không truyền → model mặc định của CLI. Áp cho cả 2 nhánh (`--bg` và
đồng bộ). Native subagent (`Agent(subagent_type=...)`) có sẵn tham số `model` — cùng nguyên tắc.

**Nguyên tắc: model chọn theo TASK, không phải theo AGENT cố định** — cùng một Taylor lúc chạy
query BQ cơ học, lúc thiết kế backtest/giả thuyết mới; gắn cứng "Taylor = model X" sai một nửa số
lần. Quyết định bởi **Mike, tại thời điểm dispatch**.

**Ladder ưu tiên (SỬA 2026-07-14): Sonnet → Opus → Fable. Ưu tiên Opus/Sonnet; Fable CHỈ cho task
cực kỳ phức tạp.**

| # | Câu hỏi | YES → |
|---|---|---|
| Q1 | Tra cứu/query/check cơ học, có 1 đáp án đúng rõ ràng? | **Sonnet 5** (mặc định, omit `--model`) |
| Q2 | Phức tạp thường: cân nhắc trade-off, tổng hợp nhiều nguồn, sinh giả thuyết, phản biện/soi lỗi tinh vi, hoặc chạm production chưa có template? | **Opus** (`--model opus`) |
| Q3 | **CỰC KỲ phức tạp**: thiết kế chiến lược/hệ thống mới từ đầu, backtest đa-giả-thuyết nhiều tầng, verify đối kháng khó nhất — vượt tầm Opus? | **Fable 5** (`--model fable`) — hiếm |

Không chắc → mặc định Sonnet 5. Lưỡng lự Opus-hay-Fable → chọn **Opus**. Tránh dùng model đắt cho
việc thường lệ.

**⚠️ "Omit `--model`" KHÔNG có nghĩa là "Sonnet 5" — nó có nghĩa là "lấy model trong
`agents/<id>/.claude/settings.json`".** `dispatch.sh` khi `MODEL` rỗng thì **không truyền cờ nào**,
nên CLI tự lấy từ file đó. Hai thứ này chỉ trùng nhau CHỪNG NÀO cả 8 `settings.json` còn ghi
`claude-sonnet-5` — kiểm bằng:
```bash
for a in $(ls agents/); do printf '%-11s %s\n' "$a" \
  "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('model','-'))" agents/$a/.claude/settings.json)"; done
```
**Đã từng lệch và không ai thấy** (sửa 2026-08-03): commit `759ed5e8` (2026-06-23) gắn model theo
AGENT — Taylor=`claude-opus-4-8`, 6 agent còn lại=`claude-sonnet-4-6`; chính sách 2026-07-14 thay
thế nhưng **`settings.json` không được cập nhật**. Hệ quả đo được: `--model sonnet` →
`claude-sonnet-5`, nhưng **omit** → `claude-sonnet-4-6` (đời trước); Taylor omit →
`claude-opus-4-8` (tầng ĐẮT NHẤT, ngược ý "mặc định = tầng rẻ"). 64/400 job gần nhất chạy
`model=default`. Nay cả 8 đã về `claude-sonnet-5`; đổi model 1 agent thì phải sửa cả mô tả này.

**⚠️ Sự cố model-drift đã đo được (2026-07-17, chi tiết `kb/incidents/2026-07/2026-07-17-model-tier-drift-fable.md`)**: %fable dispatch lên
58%/tuần dù hầu hết là task "phức tạp thường" (Q2, tầng Opus), không phải Q3 — compute wall-clock
tăng 150% trong khi job count giảm. Lưới an toàn (không thay quyết định thật của Mike): `dispatch.sh`
in nhắc stderr mỗi lần `--model fable`; `bin/spend_report.py` cảnh báo khi %fable tổng ≥30% (Friday
editorial review). Tự hỏi đúng Q1-Q3, đừng phản xạ chọn tier cao khi việc "nghe có vẻ quan trọng".

**Gợi ý xác suất ban đầu theo loại việc** (không phải rule cứng theo tên agent):
- **Sonnet 5**: `bq-analyst`, `fleet-scout`, `corp-scanner`, `data-ops` (freshness/pipeline, rule-based),
  `Mafee` (thực thi plan-bound), `ops_health_check`/`preflight_check`-style.
- **Opus** (tầng phức tạp mặc định): `Taylor` khi làm R&D/backtest/sinh giả thuyết, `quant-skeptic`,
  `DollarBill` khi plan có trade-off không tầm thường, `risk-auditor`/`legal-vn` khi câu hỏi mang
  tính diễn giải.
- **Fable 5**: chỉ khi task thực sự **cực kỳ phức tạp** (thiết kế chiến lược mới toàn diện, chuỗi
  giả thuyết lớn nhiều tầng vượt tầm Opus) — dùng dè, không phải mặc định cho R&D thường.

### Provider routing — CHỌN CLI trước, rồi mới chọn model (thêm 2026-08-03, multi-CLI)

`dispatch.sh` nhận thêm **`--provider claude|opencode|codex`**. Bỏ qua ⇒ `claude` (mọi lệnh dispatch
cũ chạy y nguyên, 0 thay đổi hành vi — chứng minh bằng `bin/cli_provider_selfcheck.sh` so argv
byte-for-byte). Khai báo provider ở **`kb/cli_providers.json`** — thêm CLI mới = thêm 1 entry,
KHÔNG sửa `dispatch.sh`.

**Chính sách user 2026-08-03: coi `deepseek-v4-flash-free` ngang tầm Sonnet ⇒ CHỦ ĐỘNG đẩy việc
tầng-Sonnet sang opencode để tiết kiệm quota claude.** Nay là kênh chia tải mặc định cho tầng rẻ,
không còn là "chỉ dùng khi cần ý kiến trái chiều".

**Chính sách user 2026-08-16: Codex CLI làm cổng router.** `ocgo/deepseek-v4-flash` là default cho
implementation/execution; `gpt-5.6-sol` chỉ dùng cho planning khi user tự set `/model` hoặc dispatch
có `--model gpt-5.6-sol` (ChatGPT đang usage-limit 08-16). Claude giữ cho production/trading/approval
và những việc chưa rõ phạm vi.

**Chọn provider theo 3 bước, hỏi ĐÚNG THỨ TỰ (dừng ở bước nào ra `claude` thì dừng luôn):**

**Bước 1 — Task có GHI gì không?** (sửa file/code/KB, sinh plan, đặt lệnh, ghi BQ, đổi cron)
- Ghi production/approval/trading, `run_bot`, `trading_rules`, `secrets`, `crontab`, `BOT_STOP`,
  `dispatch.sh`, hoặc agent Mafee/DollarBill/Mike ⇒ **`claude`**.
- Ghi implementation rõ phạm vi repo WorkingClaude và user chọn codex ⇒ có thể dùng
  **`--provider codex`** (default DeepSeek flash).
- opencode vẫn **không có tool `write`/`edit`** (đã xác minh: chỉ có
  bash·glob·grep·read·webfetch·websearch·skill·task·todowrite) và `bash` bị deny-by-default.

**Bước 2 — Task có nằm trên ĐƯỜNG GĂNG vận hành không?** (plan T+1, EOD report, run_bot,
alert chặn thực thi, bất cứ thứ gì có deadline trong ngày)
→ **CÓ ⇒ `claude`.** Độ trễ free tier chưa đo đủ mẫu (mới n=1 quan sát bất thường) — không đặt
cược deadline vào biến chưa biết.

**Bước 3 — Còn lại (chỉ ĐỌC, không deadline): áp ladder Q1-Q3 như cũ, nhưng Q1 đổi đích.**

| | Loại task | Đích |
|---|---|---|
| **Q1** | Tra cứu web (lãi suất, tin tức, corp-action), đọc/tóm tắt/so sánh tài liệu, phản biện một kết luận, smoke test, kiểm tra trạng thái | **`--provider opencode`** ⟵ *đổi từ Sonnet* |
| **Q2** | Trade-off, tổng hợp nhiều nguồn, sinh giả thuyết, soi lỗi tinh vi | `claude --model opus` |
| **Q3** | Cực kỳ phức tạp, vượt tầm Opus | `claude --model fable` (hiếm) |

**Ngoại lệ cần nhớ: `bq` KHÔNG nằm trong allowlist của opencode** ⇒ mọi task cần query BigQuery
vẫn phải đi `claude`, dù nó chỉ là tra cứu cơ học.

Agent được phép trên opencode: `Taylor · Winston · Wendy · Spyros · Wags`
(`DollarBill`/`Mafee`/`Mike` bị chặn — surface tiền thật + điều phối).

**Đo hiệu quả chia tải**: `python3 bin/spend_report.py --days 7` — có dòng `offload: N/M job (x%)`
và `model mix` tách riêng `opencode` khỏi model của claude.

**Auto-fallback claude khi provider phụ hết usage/rate limit (chốt 2026-08-03, user mandate)**:
`dispatch.sh` tự phát hiện lỗi dạng usage-limit ở BẤT KỲ provider phụ nào (opencode/deepseek...)
và **fallback NGAY sang claude** (không chờ) — khác cách xử lý cho chính claude (đợi tới giờ reset
dự đoán được rồi thử lại): claude có cửa sổ 5h/tuần đo được qua `usage_watch.py`, provider phụ có
`usage_probe=null` (không đoán được giờ hồi quota) nên "chờ rồi thử lại provider đó" chỉ là đoán
mù, còn claude là quota ĐỘC LẬP. Cơ chế: `_maybe_fallback_provider_on_usage_limit()` trong
`dispatch.sh`, chạy TRƯỚC `_maybe_schedule_usage_resume` ở cả 2 nhánh (`--bg` và đồng bộ) — spawn
1 job `--bg` mới cho ĐÚNG agent/prompt/effort đó nhưng KHÔNG truyền `--provider`/`--model` (rơi về
routing claude, tức Sonnet cho việc Q1 vốn được route sang opencode). Tự động, không cần gì thêm.

| Provider | Trạng thái |
|---|---|
| **claude** | ✅ mặc định |
| **opencode** | ✅ dùng được ngay, 0 credentials |
| **codex** | ✅ gateway: default `ocgo/deepseek-v4-flash`; `gpt-5.6-sol` optional manual plan (usage-limited 2026-08-16) |
| **antigravity** (`agy`) | ❌ `enabled:false` — cần cài `agy` + login Gemini + điền `models` thật |

### Codex gateway routing — Phase 1 (2026-08-16)

`codex` đã enabled trong `kb/cli_providers.json`; `default_model = ocgo/deepseek-v4-flash`.

- Implementation/research trong repo: `--provider codex` (omit `--model` → DeepSeek flash).
- Task implement nặng hơn cần suy luận: `--provider codex --model ocgo/deepseek-v4-pro`.
- Planning/spec: `--provider codex --model gpt-5.6-sol` nhưng chỉ khi Sol còn usage; chưa tự đặt
  Sol làm default vì canary 08-16 hit usage limit.
- Claude vẫn là default provider khi bỏ `--provider`, và bắt buộc cho Mafee/DollarBill/Mike,
  production/trading/approval, run_bot, thay đổi `dispatch.sh`/core.

```bash
# CÁCH DÙNG CHÍNH — công cụ chuyên dụng, tự lo prompt phản biện + ghi bus:
bin/second_opinion.sh <file-hoặc-kết-luận> [--agent Taylor] [--bg]

# Hoặc dispatch thủ công (omit --model ⇒ default_model = deepseek free):
bin/dispatch.sh Taylor "Phản biện kết luận X. Chỉ đọc, đừng sửa gì." --provider opencode
bin/dispatch.sh Taylor "Implement feature Y trong repo. Ghi code, chay test." --provider codex
bin/dispatch.sh Taylor "Lap spec/plan cho Z." --provider codex --model gpt-5.6-sol --effort high

bin/cli_provider.sh list                 # provider đang bật
bin/cli_provider.sh check opencode       # CLI có chạy được không (phân biệt 'provider hỏng' vs 'task lỗi')
```

Agent được phép trên codex: `Taylor · Winston · Wendy · Spyros · Wags` (giống opencode).
`DollarBill`/`Mafee`/`Mike` bị chặn — surface tiền thật + điều phối.

**`bin/second_opinion.sh` — việc chính đang chạy trên opencode.** Phản biện độc lập về một kết
luận/tài liệu, ghi lên bus dưới topic `second-opinion: <chủ đề>`. **ADVISORY, KHÔNG phải cổng
duyệt** — cổng thật vẫn là `verify_finding.sh` (quant-skeptic) và `arch-reviewer`, cố ý giữ trên
một CLI đã hiệu chuẩn. Lần chạy đầu (job `Wags_20260803_041742`) đã bắt được **1 lỗi bằng chứng
thật** trong chính tài liệu kiểm chứng của Mike — xem
`agents/Wags/verify_opencode_adapter_20260803.md` §Hậu kiểm.

⚠️ `allow_agents` trong registry chỉ chặn ở tầng `dispatch.sh` — agent có Bash vẫn gọi thẳng
binary được. Cưỡng chế THẬT là `permission` trong `agents/<id>/opencode.json`, và **nó không phải
sandbox bảo mật**: pattern khớp trên chuỗi lệnh nên lệnh trong allowlist vẫn có thể kèm chuyển
hướng (`grep x y > z`) để ghi file. Giảm bề mặt **tai nạn**, không chặn được chủ đích.

Ví dụ: `bin/dispatch.sh Taylor "Thiết kế lại toàn bộ hệ thống chọn cổ phiếu từ đầu" --model fable --effort high`
· `bin/dispatch.sh Taylor "Backtest thêm 1 sector cho family có sẵn" --model opus --effort high`
· `bin/dispatch.sh Taylor "Query PE hiện tại của VNM"` (omit `--model` → Sonnet 5, medium).

**Reasoning-effort per dispatch — `--effort LEVEL` (chính sách user 2026-07-14):** `dispatch.sh`
nhận `--effort low|medium|high|xhigh|max`, validate lúc parse, ghi vào job record (`effort=`), áp
cho cả `--bg` lẫn đồng bộ.
- **Mặc định (omit `--effort`) = `medium`** — mọi task thường lệ chỉ dùng `medium`.
- **Task phức tạp → `--effort high`** (thiết kế backtest/giả thuyết mới, phản biện tinh vi, chạm
  production chưa có template).
- **Chặn cứng: model `fable` tối đa `high`.** Truyền `xhigh`/`max` cùng `--model fable` sẽ tự clamp
  về `high` + cảnh báo stderr (không bao giờ chạy fable ở xhigh/max). `xhigh`/`max` chỉ dành cho
  model khác (vd `opus`) khi thực sự cần.
- Ghép với ladder model: lookup cơ học → omit cả hai (**Sonnet, medium**); phức tạp thường →
  **`--model opus --effort high`**; cực kỳ phức tạp → **`--model fable --effort high`** (fable trần
  high).

**⚠️ Kỷ luật riêng cho dispatch TƯƠNG TÁC của chính Mike (chốt 2026-08-10, sau audit token-usage;
bổ sung 2026-08-16: góp ý bên thứ ba — giữ mặc định `medium` cho audit/fix thường, chỉ dùng `high`
khi thực sự phức tạp).**
`bin/spend_report.py`'s "Effort-tier mix by agent" bắt được Taylor 88-94% `effort=high` trong 14
ngày, KHÔNG ai giám sát — và chính Mike cũng làm y hệt trong 1 saga cùng ngày (5 lần dispatch Wags
liên tiếp, cả 5 đều `--model opus --effort high` không cân nhắc riêng từng lần, kể cả lần chỉ là
"xác nhận trạng thái, redispatch tiếp tục" đáng lẽ `medium` đã đủ). Đây là hành vi con người, không
sửa được bằng code (5d trong `bin/kb_nightly.sh`'s Friday review chỉ ĐO, không tự sửa) — quy tắc
cụ thể để tự áp dụng mỗi lần dispatch tương tác:
- Mặc định `medium`. Chỉ gõ `--effort high` khi tự trả lời được câu hỏi cụ thể: "task NÀY cần
  agent tự lập kế hoạch/suy luận nhiều bước MỚI, hay chỉ là tiếp nối/xác nhận/redispatch việc đã
  rõ hướng?" — vế sau KHÔNG cần high.
- Redispatch sau timeout/hết turn CHỈ giữ nguyên `--effort high` nếu job gốc đã ở high VÀ lý do
  hết giờ là "việc thật sự khó" (không phải overhead dispatch/context) — không phản xạ copy y
  nguyên flag cũ.

**Bảng phân loại nhanh — audit/fix là nguồn drift chính (2026-08-16):**

| Task type | Model | Effort | Lý do |
|---|---|---|---|
| Selfcheck sweep, verify artifact | Sonnet | medium | Rule-based, kết quả binary PASS/FAIL |
| Ops autofix cơ học (rotate, trim, crontab check) | Sonnet | medium | Deterministic, không cần suy luận mới |
| Bug fix với nguyên nhân đã xác định | Sonnet/Opus | **medium** | Thực thi theo spec đã rõ |
| Audit freshness / health check | Sonnet | medium | Read + compare, không sinh giả thuyết |
| Wags autofix theo verdict có sẵn | Sonnet | medium | Tiếp nối verdict của arch-reviewer |
| **Redispatch "tiếp tục từ working memory"** | giữ model gốc | **medium** | Context đã load, không cần effort mới |
| Code review / phản biện tinh vi | Opus | high | Cần suy luận đa chiều |
| Backtest/giả thuyết mới chưa có template | Opus | high | Thiết kế từ đầu |
| Fix bug MÀ nguyên nhân chưa rõ | Opus | high | Cần tự điều tra |
| Thiết kế hệ thống/chiến lược mới | Fable | high | Cực kỳ phức tạp |

Dấu hiệu đang cần medium, không phải high: "vá đúng chỗ đã xác định", "chạy lại selfcheck", "tiếp
tục sau resume", "check xem đã xong chưa", "apply verdict có sẵn". Nếu không có từ nào như "thiết
kế", "giả thuyết mới", "tại sao lại hỏng", "chưa hiểu rõ" → mặc định medium.
