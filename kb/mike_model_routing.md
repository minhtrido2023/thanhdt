---
kind: operating-procedure
title: Mike model and provider routing
source: MIKE.md (OKF split 2026-08-15)
---

## Routing đời 5.5 — BẢNG HIỆN HÀNH (user duyệt 2026-10-11 10:55 ICT, `decided_by: user`)

**Mục này là luật đang chạy.** Chỗ nào bên dưới mâu thuẫn với mục này thì mục này thắng; các mục
dưới giữ làm lịch sử + chi tiết cơ chế (provider, cầu chì vòng, kỷ luật effort) và vẫn hiệu lực ở
phần không mâu thuẫn. Ba điểm bị thay: (a) "Q1 → opencode" (2026-08-03) — nay Q1 → Haiku 5.5;
(b) "việc khó ⇒ Opus + `--effort high`" (2026-10-02/10-06) — nay Opus mặc định `medium`, `high` theo
danh sách dưới (ĐANG THỬ, xem mốc); (c) `ops_autofix.sh` ghim Opus — nay Sonnet.

Alias của CLI (đo 2026-10-11, CLI 2.1.295): `haiku` → `claude-haiku-5-5`, `sonnet` →
`claude-sonnet-5-5`, `opus` → `claude-opus-5-5`. Omit `--model` → model ghi trong
`agents/<id>/.claude/settings.json`: **6 agent = `claude-sonnet-5-5`** (Mike, Taylor, Wags, Winston,
Wendy, Spyros); **DollarBill + Mafee TẠM GIỮ `claude-sonnet-5`** (đường tiền — xem "Chạy thử plan"
ngay dưới; cảnh báo "Omit" ở mục sau).

Giá niêm yết API, USD / 1 triệu token vào / ra (bảng cached 2026-10-06 trong skill `claude-api`;
đội chạy gói thuê bao nên đây là thước TƯƠNG ĐỐI, không phải hoá đơn): Haiku 5.5 0,10 / 0,50
(prompt > 100K token: 0,50 / 2,50) · Sonnet 5.5 2 / 10 · Opus 5.5 4 / 20 · Fable 5.1 10 / 50.
Đọc cache: Sonnet 5.5 và Opus 5.5 CÙNG 0,20 ⇒ với job cache-hit cao, Opus đắt hơn Sonnet dưới 2 lần.

| Tầng | Model / effort | Việc | Điều kiện / lưu ý |
|---|---|---|---|
| **0** | `--model haiku` (effort omit = medium) | Kiểm trạng thái job/session (`fleet-scout`), phân loại log + bus event, smoke test, tra KB | CHỈ ĐỌC · dưới ~30 lượt · đầu ra kiểm được bằng mắt/script. KHÔNG dùng cho: ghi code/KB, query BQ, bất cứ việc nào mà bỏ sót im lặng sẽ lọt, vòng agent dài (prompt > 100K token giá nhảy 5 lần) |
| **1** | omit `--model` hoặc `--model sonnet`, effort omit = medium | Báo cáo ngày/tuần/tháng, plan T+1, Mafee, data-ops, corp-scanner, query BQ, sửa code đã biết đúng chỗ, áp `required_change`, ops autofix cơ học | Mặc định. KHÔNG hạ `low`: ở `low` Sonnet 5.5 hay báo xong khi chưa chạy kiểm |
| **2** | `--model opus` (effort omit = medium) | R&D / backtest theo khuôn có sẵn, due diligence, tổng hợp nhiều nguồn, lỗi chưa rõ nguyên nhân | Mặc định MỚI cho việc khó |
| **2+** | `--model opus --effort high` | Phản biện (arch-reviewer, quant-skeptic, fundamental-skeptic, code-reviewer), mọi thứ chạm tiền / cổng an toàn, thiết kế backtest MỚI từ đầu, lượt "review TOÀN BỘ nhánh một lần" (chế độ B) | `xhigh`/`max` chỉ khi đã ĐO được lợi trên việc đó |
| **3** | `--model fable --effort high` (trần high) | Chỉ LÊN KẾ HOẠCH việc cực khó | Hiếm; không tự thực thi (bright line bên dưới) |

**Chạy thử plan 2026-10-11 — vì sao DollarBill/Mafee CHƯA đổi.** Chạy lại đề lập plan SpaceX của
thứ Sáu 09/10 trên Sonnet 5.5, ghi ra `/tmp` (job `DollarBill_20261011_035729` và `_040016`): cả 2
lượt ra ĐÚNG quyết định (HOLD, 0 lệnh) với 5-7 lượt gọi thay vì 19 của bản thật; nhưng lượt đầu
CHÉP nguyên khối `state_note`/`nav_basis`/`jit_unpark_proposal` từ plan hôm trước (ngày as-of lệch
1 phiên) và cả 2 lượt tự báo "chưa chạy `load_plan()`". Giới hạn của phép thử: (a) ngày HOLD ⇒
không thử được sizing/giá tham chiếu; (b) đề có chữ "chạy thử" có thể làm model làm tắt; (c) lượt
đối chứng Sonnet 5 (`_040012`) HỎNG — nó đọc recap của lượt trước, không lập plan mà trỏ sang file
của lượt kia rồi báo xong ⇒ chạy 2 lượt liên tiếp cùng agent là nhiễm chéo qua working memory.
**Điều kiện đổi:** user quyết (dựa vào duyệt plan 21:00 + các cổng cơ học), hoặc có phép thử sạch
trên ngày CÓ lệnh. Tới lúc đó vòng `for` kiểm settings in ra 6 dòng `-5-5` + 2 dòng `-5` là ĐÚNG.

Không chắc tầng nào → tầng 1. Lưỡng lự 0-hay-1 → 1. Lưỡng lự 2-hay-2+ → hỏi "việc này có phải phản
biện / chạm tiền / thiết kế mới không?" — không ⇒ 2.

**🧪 ĐANG THỬ — Opus mặc định `medium` (2026-10-11 → mốc xem lại 2026-10-25).** Cơ sở: tài liệu
Anthropic nói Opus 5.5 ở `medium` ngang/hơn Opus 5 ở `high` với ~nửa token — số của HỌ, chưa đo
trên việc của đội. Số nền 14 ngày trước khi thử (27/9 → 11/10, từ `bus/jobs` theo `started_at`):
120 job Opus, trong đó `high` 88 (73%) / `medium` 30 / `xhigh` 2; Taylor opus/high n=79 trung vị
24,1 phút, opus/medium n=10 trung vị 9,5 phút (KHÁC loại việc — không phải so sánh có đối chứng);
verdict quant-skeptic 43 lượt: CONFIRMED 25 / REFUTED 8 / NEEDS_CHANGES 9 / INCONCLUSIVE 1
(không-CONFIRMED 42%); cầu chì vòng: 1 lần chặn + 2 lần override.
**Quay về `high` nếu** tới 2026-10-25 tỉ lệ không-CONFIRMED hoặc số lần chạm cầu chì vòng tăng rõ
so với số nền trong khi việc không khó hơn; ngược lại chốt `medium` làm luật. Mẫu nhỏ ⇒ đây là
phán đoán có số kèm theo, không phải kiểm định. Cron ghim `--effort high` (kb_nightly,
weekly_ops_audit, selfcheck_red_owner_sweep, fearbuy_weekly_scan, paper_checkpoint_escalation)
CHƯA đổi trong đợt thử — đợt thử đo trên dispatch tương tác của Mike, nơi phát sinh phần lớn job.

**Native subagent — ghim `model:` trong frontmatter `~/.claude/agents/*.md` (2026-10-11).** Trước
đó 10/12 file không ghim ⇒ thừa hưởng model của phiên gọi (phiên Mike = Opus), kể cả việc tra cứu.
Nay: `fleet-scout` = haiku · `bq-analyst`, `corp-scanner`, `data-ops`, `memo-optimizer` = sonnet ·
`quant-skeptic`, `fundamental-skeptic`, `macro-strategist`, `risk-auditor`, `legal-vn`,
`arch-reviewer`, `code-reviewer` = opus. Cần tầng khác cho MỘT lần gọi → truyền `model` ở lời gọi
`Agent(...)`, đừng sửa frontmatter. Bản trước khi sửa: `~/.claude/agents-bak-20261011/`.

**opencode / codex:** không còn là đích mặc định của Q1 (offload đo được 0% tuần 04-11/10 — luật
không chạy trên thực tế). Giữ cho `bin/second_opinion.sh` (giá trị = ý kiến từ model KHÁC) và khi
user chỉ định. Cơ chế provider + auto-fallback bên dưới không đổi.

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
| Q1 | Tra cứu/query/check cơ học, có 1 đáp án đúng rõ ràng? | **Sonnet** (mặc định, omit `--model`) — từ 2026-10-11 tách tiếp: chỉ-đọc ngắn kiểm được → Haiku (bảng hiện hành ở đầu file) |
| Q2 | Phức tạp thường: cân nhắc trade-off, tổng hợp nhiều nguồn, sinh giả thuyết, phản biện/soi lỗi tinh vi, hoặc chạm production chưa có template? | **Opus** (`--model opus`) |
| Q3 | **CỰC KỲ phức tạp**: thiết kế chiến lược/hệ thống mới từ đầu, backtest đa-giả-thuyết nhiều tầng, verify đối kháng khó nhất — vượt tầm Opus? | **Fable 5** (`--model fable`) — hiếm |

Không chắc → mặc định Sonnet. Lưỡng lự Opus-hay-Fable → chọn **Opus**. Tránh dùng model đắt cho
việc thường lệ.

**🔴 BRIGHT LINE — Fable = LÊN KẾ HOẠCH, không tự thực thi (user mandate, 2026-08-21)**

Fable CHỈ được dùng để **PLAN**: thiết kế kiến trúc, phân tích chiến lược, đề xuất phương án —
những việc mà OUTPUT là một bản kế hoạch/thiết kế để người hoặc Opus/Sonnet thực hiện tiếp.

Fable **KHÔNG được** dùng để **IMPLEMENT**: viết code thật, sửa file production, chạy backtest,
đặt lệnh, commit, hoặc bất kỳ hành động có side effect. Những việc đó dùng Opus (hoặc Sonnet).

Lý do: Fable chậm + đắt; việc implement không cần reasoning cực phức tạp của Fable — và quan
trọng hơn, **plan do Fable tạo ra vẫn cần human/Mike review trước khi wire vào production**. Để
Fable tự implement là bỏ qua bước review đó. Không có exception: kể cả khi dispatch prompt nghe có
vẻ "chỉ là implement một plan rõ ràng" — lúc đó dùng Opus, không phải Fable.

**⚠️ "Omit `--model`" KHÔNG có nghĩa là "Sonnet đời mới nhất" — nó có nghĩa là "lấy model trong
`agents/<id>/.claude/settings.json`".** `dispatch.sh` khi `MODEL` rỗng thì **không truyền cờ nào**,
nên CLI tự lấy từ file đó. Hai thứ này chỉ trùng nhau CHỪNG NÀO cả 8 `settings.json` còn ghi
`claude-sonnet-5-5` (trừ DollarBill/Mafee đang giữ `claude-sonnet-5` có chủ đích, 2026-10-11) — kiểm bằng:
```bash
for a in $(ls agents/); do printf '%-11s %s\n' "$a" \
  "$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('model','-'))" agents/$a/.claude/settings.json)"; done
```
**Đã từng lệch và không ai thấy** (sửa 2026-08-03): commit `759ed5e8` (2026-06-23) gắn model theo
AGENT — Taylor=`claude-opus-4-8`, 6 agent còn lại=`claude-sonnet-4-6`; chính sách 2026-07-14 thay
thế nhưng **`settings.json` không được cập nhật**. Hệ quả đo được: `--model sonnet` →
`claude-sonnet-5`, nhưng **omit** → `claude-sonnet-4-6` (đời trước); Taylor omit →
`claude-opus-4-8` (tầng ĐẮT NHẤT, ngược ý "mặc định = tầng rẻ"). 64/400 job gần nhất chạy
`model=default`. 2026-08-03 cả 8 về `claude-sonnet-5`.
**Lệch LẦN HAI (sửa 2026-10-11):** Sonnet 5.5 ra mắt, alias `sonnet` tự nhảy sang
`claude-sonnet-5-5` nhưng 8 `settings.json` ghim ID đầy đủ nên omit vẫn chạy `claude-sonnet-5` —
đo 3 ngày: 1.054 lượt đời cũ vs 522 lượt đời mới. Nay 6/8 ghi `claude-sonnet-5-5` (+ mặc định
của `bin/spawn_child.sh`); DollarBill/Mafee giữ đời cũ có chủ đích (xem đầu file). **Mỗi lần Anthropic ra đời model mới: chạy lại vòng `for` ở trên** — ID
đầy đủ KHÔNG tự cập nhật như alias. Đổi model 1 agent thì phải sửa cả mô tả này.

**⚠️ Sự cố model-drift đã đo được (2026-07-17, chi tiết `kb/incidents/2026-07/2026-07-17-model-tier-drift-fable.md`)**: %fable dispatch lên
58%/tuần dù hầu hết là task "phức tạp thường" (Q2, tầng Opus), không phải Q3 — compute wall-clock
tăng 150% trong khi job count giảm. Lưới an toàn (không thay quyết định thật của Mike): `dispatch.sh`
in nhắc stderr mỗi lần `--model fable`; `bin/spend_report.py` cảnh báo khi %fable tổng ≥30% (Friday
editorial review). Tự hỏi đúng Q1-Q3, đừng phản xạ chọn tier cao khi việc "nghe có vẻ quan trọng".

**Gợi ý xác suất ban đầu theo loại việc** (không phải rule cứng theo tên agent):
- **Sonnet**: `bq-analyst`, `corp-scanner`, `data-ops` (freshness/pipeline, rule-based) — `fleet-scout` sang Haiku từ 2026-10-11,
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

**Chính sách user 2026-08-03 (THAY bởi quyết định 2026-10-11 — xem bảng hiện hành ở đầu file):**
coi `deepseek-v4-flash-free` ngang tầm Sonnet ⇒ chủ động đẩy việc tầng-Sonnet sang opencode để
tiết kiệm quota claude. Từ 2026-10-11 tầng rẻ là Haiku 5.5; opencode quay về vai "ý kiến trái
chiều" (`second_opinion.sh`) hoặc khi user chỉ định.

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
| **Q1** | Tra cứu web (lãi suất, tin tức, corp-action), đọc/tóm tắt/so sánh tài liệu, phản biện một kết luận, smoke test, kiểm tra trạng thái | ~~`--provider opencode`~~ ⟵ *từ 2026-10-11: `claude --model haiku` nếu đạt điều kiện tầng 0, không thì Sonnet* |
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
· `bin/dispatch.sh Taylor "Query PE hiện tại của VNM"` (omit `--model` → Sonnet, medium).

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
  **`--model opus`** (medium — đang thử từ 2026-10-11; `--effort high` cho danh sách tầng 2+ ở đầu
  file); cực kỳ phức tạp → **`--model fable --effort high`** (fable trần high).

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

### Việc THƯỜNG NGÀY vs việc KHÓ (user chốt 2026-10-06 00:15 ICT) — luật gốc, 2 chế độ bên dưới chi tiết hoá

- **Việc thường ngày, đơn giản ⇒ `Sonnet` + `--effort medium`**: soạn/gửi báo cáo (ngày/tuần/THÁNG),
  nhắc việc hằng ngày, scan/kiểm tra định kỳ, cập nhật số liệu, đồng bộ registry, chạy lại pipeline
  có sẵn. Dispatch omit `--model` đã rơi về Sonnet (`agents/*/.claude/settings.json`) và effort
  `medium` (`dispatch.sh`) ⇒ cron nào không ghim là đúng luật.
- **Điều phối coding task KHÓ + NGHIÊN CỨU ⇒ `Opus`** (effort `medium` mặc định từ 2026-10-11;
  `high` theo danh sách tầng 2+ ở đầu file): thiết kế/sửa
  code chưa rõ nguyên nhân, R&D/backtest/due-diligence, đánh giá checkpoint paper-program.
- Kiểm kê cron ghim Opus (06/10): `fearbuy_weekly_scan.sh` (due-diligence = nghiên cứu, giữ),
  `paper_checkpoint_escalation.sh` (đánh giá gate R&D, giữ), `wags_autofix.sh` (sửa lỗi điều phối,
  giữ). `check_report_cadence.sh` báo cáo THÁNG opus/high ⇒ ĐỔI sang sonnet/medium.
- Bổ sung 2026-10-11 (user duyệt): `ops_autofix.sh` (Winston sửa lỗi vận hành cơ học) opus ⇒
  **sonnet**; ba cron ở dòng trên vẫn giữ Opus.

### Hai chế độ theo ĐỘ KHÓ + cắt vòng lặp polish (user chỉ đạo 2026-10-02 10:43 ICT)

Bối cảnh: audit token 9 ngày (24/9→02/10) — ngoài context phình của phiên Mike, chi phí Taylor tăng
vọt ở 27/9 (3.317 lượt Opus) và 01/10 (2.623 lượt Sonnet) vì chuỗi vòng polish nối đuôi nhau
(ATC UPCOM 4 vòng, lag-exit 6 vòng, price-frame 2 vòng), mỗi vòng = 1 dispatch + 1 arch-review.
Vấn đề không phải "chọn nhầm tầng model" mà là **đi từng bước nhỏ trên việc chưa được hiểu hết**.

**Chế độ A — việc NHẸ ⇒ `Sonnet` + `--effort medium`, KHÔNG lên Opus.** Gồm: sửa text/docstring/comment,
đổi message, fix code nhẹ đã biết đúng chỗ, thêm/bổ sung test cho mutation đã được nêu tên,
revert phần thừa theo chỉ định, áp verdict arch-review đã liệt kê sẵn từng `required_change`,
đồng bộ config/registry, dọn worktree. Dấu hiệu: reviewer đã chỉ ĐÚNG file:dòng/mutation cần giết.
Redispatch "vòng N chỉ test-only" cũng thuộc nhóm này — mặc định Sonnet medium.

**Chế độ B — việc MỚI/KHÓ/lỗi cứ phát sinh thêm ⇒ `Opus`, làm MỘT LẦN cho trọn** (lượt REVIEW toàn
bộ = `--effort high`; lượt SỬA theo danh sách đã lập = `medium` — đợt thử 2026-10-11).
Gồm: thiết kế mới chưa có template, bug chưa rõ nguyên nhân, chạm production/tiền/cổng an toàn,
hoặc review lộ ra lỗi MỚI khác loại với lỗi vòng trước. Cách chạy: (1) Opus high **review TOÀN BỘ**
diff/nhánh một lượt (không chỉ chỗ reviewer vừa chỉ) và lập danh sách đầy đủ mọi lỗi + mutation còn
sống; (2) sửa hết trong **một** dispatch; (3) arch-review xác nhận **một** lần. Không vá cuốn chiếu.

**Cầu chì cắt vòng (bắt buộc áp khi dispatch lại sau arch-review):**
- **Trước vòng 2 (user chốt 2026-10-07, retro Pattern A phương án a): review TOÀN BỘ nhánh MỘT lần** —
  reviewer liệt kê trọn bộ lỗi + mutation còn sống, vòng 2 sửa hết trong 1 dispatch. Áp cho MỌI đường
  (`dispatch.sh` lẫn `Agent()` — cầu chì code chỉ đếm `dispatch.sh`). Vòng 2 vẫn chế độ A nếu
  `required_change` đã cụ thể.
- **Vòng 3 mà arch-review VẪN trả NEEDS_CHANGES với phát hiện MỚI (không phải lặp lại vòng trước) ⇒ DỪNG
  polish, chuyển sang chế độ B** (Opus high review toàn bộ rồi sửa một lượt). Không dispatch vòng 4 kiểu cũ.
- **Giờ là CODE (2026-10-05):** `dispatch.sh` CHẶN (exit 7) dispatch vòng ≥4 cùng nhánh/worktree tới cùng agent
  trong 24h (`bin/dispatch_round_cap.py`); user đã duyệt ⇒ phiên tương tác chạy `DISPATCH_ROUND_CAP_OVERRIDE=1
  DISPATCH_ROUND_CAP_REASON="user duyệt <giờ>: <vì sao>" bin/dispatch.sh ...` (lý do BẮT BUỘC từ 2026-10-07 —
  thiếu/rỗng ⇒ vẫn chặn) (agent headless bị từ chối — honour system, `env -u JOB_ID` lách được; audit
  `logs/dispatch_round_cap.log`). Exit 7 chạy trước guard exit 2; miễn `[RESUME`/`[FALLBACK`/`[AUTO-CALLBACK`.
- Vòng test-only (không đổi logic production) quá 2 vòng ⇒ hỏi user trước khi tiếp, nêu rõ mutation còn sống.
- Mỗi lần dispatch tiếp theo phải tự trả lời được: "lần này lỗi cùng loại với vòng trước hay khác
  loại?" Cùng loại + chỉ rõ chỗ ⇒ A. Khác loại/ngày càng nhiều ⇒ B.
- Review lại bằng arch-reviewer: yêu cầu nó liệt kê TRỌN BỘ mutation/lỗi sống ngay vòng đầu, không
  dừng ở lỗi đầu tiên tìm được (nguyên nhân gốc của chuỗi 4-6 vòng).
Đo lại bằng `python3 bin/spend_report.py --days 7` (effort-tier mix + model mix) mỗi tuần.
