#!/usr/bin/env bash
# code_quality_weekly.sh — Tầng 2 của kb/projects/code-quality-review-plan-20260823.md.
#
# READ-ONLY, 1 lần/tuần (dự kiến cron Chủ Nhật 10:00 ICT — CHƯA bật, chạy tay tuần đầu theo
# plan §8 tuần 2). Tính scope BẰNG MÁY (diff 7 ngày + 1 hot-core file round-robin, trần 25
# file), gọi native agent `code-reviewer` (headless, giống cơ chế verify_finding.sh gọi
# quant-skeptic — claude -p trực tiếp, KHÔNG qua dispatch.sh vì code-reviewer không có
# agents/<id>/ home dir), rồi 1 lượt phản biện độc lập cho finding severity >= medium trước
# khi ghi báo cáo. KHÔNG sửa code, KHÔNG commit, KHÔNG đóng/mở bus question thay người.
#
# Usage:
#   code_quality_weekly.sh              # chạy thật
#   code_quality_weekly.sh --dry-run    # in scope + prompt, KHÔNG gọi claude
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="/home/trido/thanhdt/WorkingClaude"
CLAUDE="/home/trido/.local/bin/claude"
AGENT_DEF="$HOME/.claude/agents/code-reviewer.md"
REVIEWER_ID="code-reviewer"
ROTATION_STATE="$ROOT/state/code_quality_weekly_rotation.json"
REPORT_DIR="$ROOT/reports/code_quality"
ARCH_THREAD_NAME="architecture"
MAX_FILES=25

dry=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done

mkdir -p "$REPORT_DIR" "$ROOT/state" "$ROOT/logs"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
LOG="$ROOT/logs/code_quality_weekly_${TODAY}.log"
log() { echo "[$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%dT%H:%M:%S%z)] $*" | tee -a "$LOG"; }
log "=== code_quality_weekly START ($TODAY) ==="

# --- 1. Scope: diff 7 ngày (2 repo), lọc .py/.sh, trừ danh sách loại trừ (khớp pyproject.toml
# §3 của plan) ---
EXCLUDE_RE='(^|/)test_[^/]*\.py$|(^|/)(exp|probe|stress)_[^/]*\.py$|(^|/)agents/[^/]*/research/|(^|/)archive/|(^|/)wc_venv/'

# `$repo` (WorkingClaude) có thể là THƯ MỤC CON của git toplevel thật (ở đây toplevel =
# /home/trido/thanhdt, WorkingClaude chỉ là 1 thư mục bên trong đó) — `git log --name-only`
# luôn trả path tương đối với TOPLEVEL, không phải với $repo. Dùng `git rev-parse
# --show-toplevel` để dựng path tuyệt đối đúng, đừng giả định $repo == toplevel (bug thật đo
# 2026-08-23: nối nhầm ra .../WorkingClaude/WorkingClaude/foo.py, mọi -f test đều fail rỗng).
_diff_files() {
  local repo="$1" toplevel
  toplevel="$(cd "$repo" && git rev-parse --show-toplevel)"
  # `-- .` khoá pathspec vào $repo: nếu $repo là thư mục con của 1 toplevel lớn hơn (đúng ca
  # WorkingClaude/ ⊂ toplevel /home/trido/thanhdt), `git log` KHÔNG có pathspec sẽ quét commit
  # chạm bất kỳ đâu trong toplevel, không chỉ $repo.
  (cd "$repo" && git log --since="7 days ago" --name-only --pretty=format: -- . 2>/dev/null \
    | grep -E '\.(py|sh)$' | grep -vE "$EXCLUDE_RE" | sort -u \
    | while read -r f; do [ -f "$toplevel/$f" ] && echo "$toplevel/$f"; done)
}

diff_wc="$(_diff_files "$WORKDIR")"
diff_mike="$(_diff_files "$ROOT")"
scope_files="$(printf '%s\n%s\n' "$diff_wc" "$diff_mike" | grep -v '^$' | sort -u)"

# --- 2. Hot-core round-robin: 1 file/tuần dù không đổi ---
HOT_CORE=(
  "$WORKDIR/trading_bot/plan.py"
  "$WORKDIR/trading_bot/executor.py"
  "$WORKDIR/trading_bot/brokers.py"
  "$WORKDIR/trading_bot/config.py"
  "$WORKDIR/trading_bot/plan_funding_gate.py"
  "$WORKDIR/bot_execute.py"
  "$ROOT/bin/dispatch.sh"
  "$ROOT/bin/ops_health_check.sh"
  "$ROOT/bin/wags_autofix.sh"
  "$ROOT/bin/ops_autofix.sh"
)
N_HOT=${#HOT_CORE[@]}
idx=0
if [ -f "$ROTATION_STATE" ]; then
  idx="$(python3 -c "import json; print(json.load(open('$ROTATION_STATE')).get('next_idx',0))" 2>/dev/null || echo 0)"
fi
idx=$(( idx % N_HOT ))
hot_file="${HOT_CORE[$idx]}"
next_idx=$(( (idx + 1) % N_HOT ))

if [ -z "$dry" ]; then
  python3 -c "
import json
json.dump({'next_idx': $next_idx, 'last_picked': '$hot_file', 'last_run': '$TODAY'}, open('$ROTATION_STATE.tmp','w'), ensure_ascii=False, indent=2)
" && mv "$ROTATION_STATE.tmp" "$ROTATION_STATE"
fi

full_scope="$(printf '%s\n%s\n' "$scope_files" "$hot_file" | grep -v '^$' | sort -u)"
n_total=$(printf '%s\n' "$full_scope" | grep -c . || true)

dropped=""
if [ "$n_total" -gt "$MAX_FILES" ]; then
  # Ưu tiên theo số commit chạm trong tuần (đếm bằng git log --follow trên từng repo) —
  # đơn giản hoá: giữ nguyên thứ tự (đã sort theo path), cắt tại MAX_FILES, log phần rớt.
  # (no silent caps — coding_guidelines "Quality patterns")
  kept="$(printf '%s\n' "$full_scope" | head -n "$MAX_FILES")"
  dropped="$(printf '%s\n' "$full_scope" | tail -n +"$((MAX_FILES+1))")"
  full_scope="$kept"
  log "TRẦN $MAX_FILES FILE VƯỢT — $((n_total - MAX_FILES)) file bị rớt (KHÔNG bị quét tuần này):"
  printf '%s\n' "$dropped" | while read -r f; do [ -n "$f" ] && log "  DROPPED: $f"; done
fi

n_scoped=$(printf '%s\n' "$full_scope" | grep -c . || true)
log "Scope tuần này: $n_scoped file (hot-core round-robin: $hot_file)"
printf '%s\n' "$full_scope" | while read -r f; do [ -n "$f" ] && log "  - $f"; done

if [ "$n_scoped" -eq 0 ]; then
  log "0 file trong scope (không có thay đổi 7 ngày qua, hot-core rỗng lạ) — thoát, không gọi claude."
  "$ROOT/bin/append_event.sh" "$REVIEWER_ID" status "code-quality-weekly-$TODAY" \
    "{\"n_files_scanned\":0,\"n_findings\":0,\"note\":\"scope rỗng bất thường, kiểm lại _diff_files\"}" >/dev/null
  exit 0
fi

# --- 3. Build prompt: system prompt của code-reviewer + danh sách file + yêu cầu output ---
# 2 dòng '---' đầu file là frontmatter YAML — bỏ, giữ phần thân bắt đầu từ dòng 'Bạn là...'
agent_body="$(awk '/^---$/{c++; next} c>=2' "$AGENT_DEF")"

prompt="$(cat <<PROMPT_EOF
$agent_body

## Nhiệm vụ lượt này (code_quality_weekly.sh, tự động, $TODAY)

Review đúng $n_scoped file dưới đây. Với MỖI file, đọc thật (Read tool), áp toàn bộ method +
4 check chuyên biệt ở trên. File hot-core được chọn round-robin tuần này (xem kỹ hơn các file
khác): $hot_file

Danh sách file:
$full_scope

Trả về DUY NHẤT 1 khối JSON, không thêm chữ nào khác, giữa 2 dòng đánh dấu:
<<<FINDINGS_JSON>>>
{"findings": [{"file": "...", "line": 0, "category": "...", "severity": "low|medium|high",
"summary": "...", "evidence": "...", "owner": "Taylor|Wags|Mike"}], "files_reviewed": $n_scoped,
"files_clean": ["..."]}
<<<END_FINDINGS>>>

"findings" RỖNG là kết quả hợp lệ nếu thật sự không thấy gì đáng báo — đừng bịa finding để có
nội dung. "files_clean" liệt kê file đã đọc kỹ và không thấy vấn đề gì.
PROMPT_EOF
)"

if [ -n "$dry" ]; then
  echo "=== SCOPE ($n_scoped file) ==="; printf '%s\n' "$full_scope"
  echo "=== PROMPT (2000 ký tự đầu) ==="; printf '%s\n' "${prompt:0:2000}"
  echo "..."; echo "[dry-run] không gọi claude."
  exit 0
fi

# --- 4. Gọi code-reviewer (headless, giống verify_finding.sh gọi quant-skeptic) ---
ts="$(date -u +%Y%m%d_%H%M%S)"
review_log="$ROOT/logs/code_quality_review_${ts}.log"
set +e
"$CLAUDE" -p "$prompt" \
  --permission-mode auto \
  --allowedTools "Bash Read Grep Glob" \
  --max-turns 80 \
  > "$review_log" 2>"$review_log.err"
_rc=$?
set -e
log "code-reviewer xong, rc=$_rc, log=$review_log"

findings_json="$(python3 - "$review_log" <<'PY'
import json, sys, re
log = sys.argv[1]
txt = open(log, encoding="utf-8", errors="replace").read()
m = re.search(r"<<<FINDINGS_JSON>>>(.*?)<<<END_FINDINGS>>>", txt, re.S)
if not m:
    print(json.dumps({"findings": [], "files_reviewed": 0, "files_clean": [],
        "parse_error": "no FINDINGS_JSON block found"}))
    sys.exit(0)
raw = m.group(1).strip()
try:
    obj = json.loads(raw)
except Exception:
    repaired = re.sub(r",(\s*[}\]])", r"\1", raw)
    try:
        obj = json.loads(repaired)
    except Exception as e:
        print(json.dumps({"findings": [], "files_reviewed": 0, "files_clean": [],
            "parse_error": "unparseable JSON: %s" % e}))
        sys.exit(0)
print(json.dumps(obj, ensure_ascii=False))
PY
)"

# Toàn bộ JSON trung gian đi qua FILE TẠM, không nhúng qua bash string interpolation vào
# python -c (bài học §15/dispatch-prompt-heredoc: JSON thật có thể chứa ', ", `, và có thể
# vượt ARG_MAX — file + argv path luôn an toàn, interpolation không bao giờ an toàn).
TMPDIR_CQ="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_CQ"' EXIT
findings_raw_f="$TMPDIR_CQ/findings_raw.json"
printf '%s' "$findings_json" > "$findings_raw_f"

n_findings="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1])).get("findings",[])))' "$findings_raw_f" 2>/dev/null || echo 0)"
log "Tìm thấy $n_findings finding thô (trước verify)."

# --- 5. Verify pass cho finding severity >= medium (1 lượt phản biện độc lập, gộp — không
# per-finding để tránh N+1 dispatch tốn kém không cần thiết) ---
medium_plus_f="$TMPDIR_CQ/medium_plus.json"
python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
f=[x for x in d.get("findings",[]) if x.get("severity") in ("medium","high")]
json.dump(f, open(sys.argv[2],"w"), ensure_ascii=False)
' "$findings_raw_f" "$medium_plus_f"
n_medium_plus="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$medium_plus_f" 2>/dev/null || echo 0)"

verified_f="$TMPDIR_CQ/verified.json"
cp "$findings_raw_f" "$verified_f"
if [ "$n_medium_plus" -gt 0 ]; then
  log "Verify pass cho $n_medium_plus finding severity>=medium..."
  medium_plus_content="$(cat "$medium_plus_f")"
  verify_prompt="$(cat <<VERIFY_EOF
Bạn là reviewer phản biện ĐỘC LẬP. Dưới đây là danh sách finding chất lượng code do 1 reviewer
khác đề xuất. Nhiệm vụ DUY NHẤT: cố REFUTE từng finding — đọc lại đúng file:line được trích,
xác nhận bằng chứng có ĐÚNG như mô tả không. Mặc định REFUTE nếu không tự xác nhận được bằng
chứng bằng Read/Grep thật.

Findings cần verify:
$medium_plus_content

Trả JSON duy nhất giữa 2 dòng đánh dấu:
<<<VERIFY_JSON>>>
{"verified": [{"file": "...", "line": 0, "survives": true, "note": "..."}]}
<<<END_VERIFY>>>
VERIFY_EOF
)"
  set +e
  "$CLAUDE" -p "$verify_prompt" \
    --permission-mode auto \
    --allowedTools "Bash Read Grep Glob" \
    --max-turns 40 \
    > "$review_log.verify" 2>"$review_log.verify.err"
  set -e
  verify_result_f="$TMPDIR_CQ/verify_result.json"
  python3 - "$review_log.verify" "$verify_result_f" <<'PY'
import json, sys, re
log, out = sys.argv[1], sys.argv[2]
txt = open(log, encoding="utf-8", errors="replace").read()
m = re.search(r"<<<VERIFY_JSON>>>(.*?)<<<END_VERIFY>>>", txt, re.S)
result = {"verified": []}
if m:
    raw = m.group(1).strip()
    try:
        result = json.loads(raw)
    except Exception:
        pass
json.dump(result, open(out, "w"), ensure_ascii=False)
PY
  # Lọc findings: giữ low-severity nguyên vẹn (không cần verify); medium/high chỉ giữ nếu
  # verify "survives":true (mặc định LOẠI nếu verify không nhắc tới file:line đó — an toàn
  # hơn báo sai).
  python3 - "$findings_raw_f" "$verify_result_f" "$verified_f" "$n_findings" <<'PY'
import json, sys
orig_f, verify_f, out_f, n_before = sys.argv[1:5]
orig = json.load(open(orig_f))
verify = json.load(open(verify_f))
survives_keys = {(v['file'], v.get('line', 0)) for v in verify.get('verified', []) if v.get('survives')}
kept = []
for f in orig.get('findings', []):
    if f.get('severity') not in ('medium', 'high'):
        kept.append(f)
        continue
    if (f.get('file'), f.get('line', 0)) in survives_keys:
        f['verified'] = True
        kept.append(f)
    # else: bị lọc — không sống sót verify
orig['findings'] = kept
orig['n_before_verify'] = int(n_before)
json.dump(orig, open(out_f, "w"), ensure_ascii=False)
PY
fi

n_final="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1])).get("findings",[])))' "$verified_f" 2>/dev/null || echo "$n_findings")"
log "Sau verify: $n_final finding còn lại (từ $n_findings thô)."

# --- 6. Ghi báo cáo + bus + Discord ---
report_file="$REPORT_DIR/code_quality_${TODAY}.md"
python3 - "$verified_f" "$report_file" "$TODAY" "$n_scoped" "$hot_file" <<'PY'
import json, sys
data_f, out, today, n_scoped, hot_file = sys.argv[1:6]
d = json.load(open(data_f))
findings = d.get("findings", [])
lines = [f"# Code quality weekly — {today}", "",
         f"File đã quét: {n_scoped} (hot-core tuần này: `{hot_file}`)",
         f"Finding: {len(findings)}" + (f" (từ {d.get('n_before_verify')} trước verify)" if d.get("n_before_verify") else ""),
         ""]
if not findings:
    lines.append("Không có finding nào đáng báo tuần này.")
for f in findings:
    lines.append(f"## {f.get('file')}:{f.get('line',0)} — {f.get('category')} ({f.get('severity')})")
    lines.append(f"- Owner đề xuất: {f.get('owner','?')}")
    lines.append(f"- {f.get('summary','')}")
    lines.append(f"- Bằng chứng: {f.get('evidence','')}")
    if f.get("verified"):
        lines.append("- Đã qua verify độc lập: sống sót phản biện.")
    lines.append("")
clean = d.get("files_clean", [])
if clean:
    lines.append(f"## File đã đọc kỹ, không có vấn đề ({len(clean)})")
    for c in clean:
        lines.append(f"- {c}")
open(out, "w", encoding="utf-8").write("\n".join(lines))
PY
log "Báo cáo: $report_file"

dropped_f="$TMPDIR_CQ/dropped.txt"
printf '%s\n' "$dropped" > "$dropped_f"
event_payload="$(python3 - "$verified_f" "$n_scoped" "$hot_file" "$report_file" "$dropped_f" <<'PY'
import json, sys
verified_f, n_scoped, hot_file, report_file, dropped_f = sys.argv[1:6]
d = json.load(open(verified_f))
dropped_list = [l for l in open(dropped_f, encoding="utf-8").read().splitlines() if l]
print(json.dumps({
    "n_files_scanned": int(n_scoped), "n_findings": len(d.get("findings", [])),
    "n_before_verify": d.get("n_before_verify"), "hot_core_this_week": hot_file,
    "report_file": report_file, "dropped_from_scope": dropped_list,
}, ensure_ascii=False))
PY
)"
"$ROOT/bin/append_event.sh" "$REVIEWER_ID" finding "code-quality-weekly-${TODAY}" "$event_payload" >/dev/null

summary_line="✅ code-quality-weekly ($TODAY): $n_scoped file quét, $n_final finding (sau verify)."
[ "$n_final" -eq 0 ] && summary_line="✅ code-quality-weekly ($TODAY): $n_scoped file quét, 0 finding — sạch."

ARCH_TID="$("$ROOT/bin/discord_channel.sh" "$ARCH_THREAD_NAME" 2>/dev/null || true)"
if [ -n "$ARCH_TID" ]; then
  "$ROOT/bin/notify_thread.sh" "$summary_line Báo cáo: $report_file" "$ARCH_TID" 2>/dev/null || true
else
  log "WARN: không resolve được topic '$ARCH_THREAD_NAME' từ discord_channels.json — không gửi Discord."
fi

# Gửi email (credential: WC_ROOT/secrets/gmail_smtp_app_password.json)
if python3 "$ROOT/bin/send_report_email.py" "$report_file" \
     --subject "Code quality weekly $TODAY — $n_final finding" \
     --skip-return-gate "code-quality report không có tỉ suất lợi nhuận, gate không áp dụng" \
     >> "$LOG" 2>&1; then
  log "Email gửi thành công."
else
  log "WARN: email thất bại (exit $?), xem log — không chặn script."
fi

log "=== code_quality_weekly DONE ==="
