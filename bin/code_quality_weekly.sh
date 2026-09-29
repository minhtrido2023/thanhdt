#!/usr/bin/env bash
# code_quality_weekly.sh — Tầng 2 của kb/projects/code-quality-review-plan-20260823.md.
#
# READ-ONLY, 1 lần/tuần (cron Chủ Nhật 10:00 ICT = `0 3 * * 0` UTC). Tính scope BẰNG MÁY (diff 7 ngày + 1 hot-core file round-robin, trần 25
# file), gọi native agent `code-reviewer` (headless, giống cơ chế verify_finding.sh gọi
# quant-skeptic — claude -p trực tiếp, KHÔNG qua dispatch.sh vì code-reviewer không có
# agents/<id>/ home dir), rồi 1 lượt phản biện độc lập cho finding severity >= medium trước
# khi ghi báo cáo. KHÔNG sửa code, KHÔNG commit, KHÔNG đóng/mở bus question thay người.
#
# Usage:
#   code_quality_weekly.sh              # chạy thật
#   code_quality_weekly.sh --dry-run    # in scope + prompt, KHÔNG gọi claude
#
# Scope (việc J ARIA 2026-09-13): file T0-T2 của kb/production_manifest.json có commit 7 ngày
# (bin/code_quality_scope.py); manifest HEAD lệch thực tế/không đọc được ⇒ WARN + fallback diff 7 ngày + HOT_CORE.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="$(cd "$ROOT/.." && pwd)"  # = /home/trido/thanhdt/WorkingClaude; suy từ ROOT để selfcheck dựng sandbox
CLAUDE="${CQ_CLAUDE:-/home/trido/.local/bin/claude}"  # override CHỈ để selfcheck chặn gọi LLM thật
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

# JSON trung gian đi qua file tạm (xem ghi chú §15 ở bước 4) — tạo sớm vì bước scope cũng dùng.
TMPDIR_CQ="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_CQ"' EXIT

# --- Hot-core round-robin: 1 file/tuần dù không đổi (plan §4 mục 2) — dùng cho CẢ 2 nguồn scope ---
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

# --- 0. Nguồn scope: kb/production_manifest.json (việc J ARIA, job Wags_20260913_075550) ---
# Chỉ dùng bản HEAD của manifest khi nó còn khớp thực tế — đúng phép so bước (3) của
# production_manifest_selfcheck.sh: tái sinh từ crontab thật rồi `--check` với HEAD (khớp = rc 0).
# Gọi thẳng generator, KHÔNG exec selfcheck: selfcheck chèn dòng cron giả trỏ score_live_signals.py,
# nên khi nó với tới được từ gốc cron này thì generator ghi file R&D đó thành T2 production. Probe
# tự-chứng-minh của selfcheck vẫn chạy ở run_selfchecks.sh. Mọi lỗi ⇒ fail-closed về scope cũ
# (diff 7 ngày + hot-core round-robin) kèm WARN nêu lý do — không bao giờ im lặng đổi nguồn.
scope_source="fallback"; scope_reason=""
dropped=""
manifest_f="$TMPDIR_CQ/production_manifest.json"
check_log="$TMPDIR_CQ/manifest_check.log"
if ! crontab -l >"$TMPDIR_CQ/crontab" 2>/dev/null; then
  scope_reason="không đọc được crontab -l — không kiểm được manifest lệch HEAD"
elif ! git -C "$ROOT" show HEAD:kb/production_manifest.json >"$manifest_f" 2>/dev/null; then
  scope_reason="không đọc được HEAD:kb/production_manifest.json ở repo mike"
elif ! (cd "$WORKDIR" && python3 "$ROOT/bin/production_manifest.py" --crontab "$TMPDIR_CQ/crontab" \
      --check "$manifest_f") >"$check_log" 2>&1; then
  # bỏ dòng WARN (T3 vào/rời) generator in TRƯỚC khối DRIFT — không thì lý do thật bị che. awk chứ
  # không `grep -v | head`: grep rc=1 (toàn WARN) / SIGPIPE + pipefail trong phép gán ⇒ set -e giết script
  detail="$(awk '!/^WARN/ && n<3 {print; n++}' "$check_log" | paste -sd' ' -)"
  scope_reason="manifest HEAD lệch thực tế (production_manifest.py --check): ${detail:-rc≠0, chỉ có dòng WARN}"
elif manifest_scope="$(python3 "$ROOT/bin/code_quality_scope.py" --manifest "$manifest_f" \
      --wc-root "$WORKDIR" --repo "$WORKDIR" --repo "$ROOT" --since "7 days ago" \
      --max-files "$MAX_FILES" --dropped-out "$TMPDIR_CQ/manifest_dropped.txt" --pin "$hot_file" \
      2>"$TMPDIR_CQ/scope.err")"; then
  scope_source="manifest"
else
  scope_reason="code_quality_scope.py lỗi: $(tail -n1 "$TMPDIR_CQ/scope.err")"
fi

if [ "$scope_source" = "manifest" ]; then
  log "Nguồn scope: MANIFEST (HEAD kb/production_manifest.json, hot-core đầu rồi T0-T2 có commit 7 ngày, T0 trước). $(cat "$TMPDIR_CQ/scope.err")"
  full_scope="$manifest_scope"
  dropped="$(cat "$TMPDIR_CQ/manifest_dropped.txt")"
  if [ -n "$dropped" ]; then
    log "TRẦN $MAX_FILES FILE VƯỢT — file bị rớt (KHÔNG bị quét tuần này):"
    printf '%s\n' "$dropped" | while read -r f; do [ -n "$f" ] && log "  DROPPED: $f"; done
  fi
else
  log "WARN: nguồn scope = FALLBACK danh sách cũ (diff 7 ngày + HOT_CORE) — $scope_reason"
# (nhánh fallback = logic scope cũ, giữ nguyên không thụt lề để diff/blame còn đọc được)
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
  # arch-review aria-J vòng 2: grep rc=1 (diff rỗng/toàn file loại trừ) và `[ -f ] && echo` là lệnh
  # cuối vòng (file cuối theo sort đã bị xoá/đổi tên) + pipefail trong phép gán ⇒ set -e giết script
  # IM sau dòng WARN, trước bus/Discord. Nhánh này chạy đúng lúc manifest lệch nên phải sống.
  (cd "$repo" && git log --since="7 days ago" --name-only --pretty=format: -- . 2>/dev/null \
    | { grep -E '\.(py|sh)$' || true; } | { grep -vE "$EXCLUDE_RE" || true; } | sort -u \
    | while read -r f; do [ ! -f "$toplevel/$f" ] || echo "$toplevel/$f"; done)
}

diff_wc="$(_diff_files "$WORKDIR")"
diff_mike="$(_diff_files "$ROOT")"
scope_files="$(printf '%s\n%s\n' "$diff_wc" "$diff_mike" | { grep -v '^$' || true; } | sort -u)"

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
fi  # hết nhánh fallback

n_scoped=$(printf '%s\n' "$full_scope" | grep -c . || true)
if [ "$scope_source" = "manifest" ]; then
  scope_label="nguồn manifest T0-T2, T0 xếp đầu; hot-core round-robin: $hot_file"
  focus_line="File hot-core được chọn round-robin tuần này (xem kỹ hơn các file khác): $hot_file. Phần còn lại đã xếp theo tầng production (T0 money-path trước)."
else
  scope_label="nguồn FALLBACK diff 7 ngày ($scope_reason); hot-core round-robin: $hot_file"
  focus_line="File hot-core được chọn round-robin tuần này (xem kỹ hơn các file khác): $hot_file"
fi
log "Scope tuần này: $n_scoped file ($scope_label)"
# `[ -z ] ||` chứ không `[ -n ] &&`: scope rỗng (hợp lệ ở nguồn manifest) ⇒ vòng trả 1 ⇒ set -e giết script
printf '%s\n' "$full_scope" | while read -r f; do [ -z "$f" ] || log "  - $f"; done

if [ "$n_scoped" -eq 0 ]; then
  log "0 file trong scope ($scope_label) — thoát, không gọi claude."
  # nguồn manifest: rỗng chỉ khi không có commit T0-T2 VÀ file hot-core tuần này không tồn tại
  [ -n "$dry" ] && exit 0
  empty_note="không có file T0-T2 nào có commit 7 ngày qua"
  [ "$scope_source" = "manifest" ] || empty_note="scope rỗng bất thường, kiểm lại _diff_files"
  "$ROOT/bin/append_event.sh" "$REVIEWER_ID" status "code-quality-weekly-$TODAY" \
    "{\"n_files_scanned\":0,\"n_findings\":0,\"note\":\"$empty_note\"}" >/dev/null
  exit 0
fi

# --- 3. Build prompt: system prompt của code-reviewer + danh sách file + yêu cầu output ---
# 2 dòng '---' đầu file là frontmatter YAML — bỏ, giữ phần thân bắt đầu từ dòng 'Bạn là...'
agent_body="$(awk '/^---$/{c++; next} c>=2' "$AGENT_DEF")"

prompt="$(cat <<PROMPT_EOF
$agent_body

## Nhiệm vụ lượt này (code_quality_weekly.sh, tự động, $TODAY)

Review đúng $n_scoped file dưới đây. Với MỖI file, đọc thật (Read tool), áp toàn bộ method +
4 check chuyên biệt ở trên. $focus_line

Danh sách file:
$full_scope

Trả về DUY NHẤT 1 khối JSON, không thêm chữ nào khác, giữa 2 dòng đánh dấu:
<<<FINDINGS_JSON>>>
{"findings": [{"file": "...", "line": 0, "category": "...", "severity": "low|medium|high",
"summary": "...", "evidence": "...", "owner": "Taylor|Wags|Mike", "suggested_fix": "..."}],
"files_reviewed": $n_scoped, "files_clean": ["..."]}
<<<END_FINDINGS>>>

"findings" RỖNG là kết quả hợp lệ nếu thật sự không thấy gì đáng báo — đừng bịa finding để có
nội dung. "files_clean" liệt kê file đã đọc kỹ và không thấy vấn đề gì. "suggested_fix" (tuỳ
chọn nhưng NÊN có): 1-2 câu hướng sửa cụ thể — báo cáo này giờ có thể được dispatch TỰ ĐỘNG cho
Taylor/Wags xử lý ngay (Tầng 3, xem plan §CẬP NHẬT 2026-09-17), "suggested_fix" giúp họ không
phải tự đoán ý định sửa từ đầu.
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
python3 - "$verified_f" "$report_file" "$TODAY" "$n_scoped" "$scope_label" <<'PY'
import json, sys
data_f, out, today, n_scoped, scope_label = sys.argv[1:6]
d = json.load(open(data_f))
findings = d.get("findings", [])
lines = [f"# Code quality weekly — {today}", "",
         f"File đã quét: {n_scoped} ({scope_label})",
         f"Finding: {len(findings)}" + (f" (từ {d.get('n_before_verify')} trước verify)" if d.get("n_before_verify") else ""),
         ""]
if not findings:
    lines.append("Không có finding nào đáng báo tuần này.")
for f in findings:
    lines.append(f"## {f.get('file')}:{f.get('line',0)} — {f.get('category')} ({f.get('severity')})")
    lines.append(f"- Owner đề xuất: {f.get('owner','?')}")
    lines.append(f"- {f.get('summary','')}")
    lines.append(f"- Bằng chứng: {f.get('evidence','')}")
    if f.get("suggested_fix"):
        lines.append(f"- Hướng sửa đề xuất: {f.get('suggested_fix')}")
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

# Copy verified.json ra chỗ BỀN (cạnh report .md) — arch-review round 2 code_quality_autodispatch:
# $TMPDIR_CQ bị `trap rm -rf EXIT` xoá khi script này thoát, nên nếu bước 7 dispatch fail và cần
# rerun tay sau đó, input phải còn tồn tại để đọc lại (không thì "rerun" chỉ là câu nói suông).
verified_durable="$REPORT_DIR/verified_${TODAY}.json"
if cp "$verified_f" "$verified_durable"; then
  verified_f="$verified_durable"
else
  log "WARN: copy verified.json ra $verified_durable THẤT BẠI — bước 7 auto-dispatch sẽ dùng bản tạm (mất khi script thoát, rerun tay sau này sẽ không đọc lại được). Tiếp tục bằng bản tạm."
fi

dropped_f="$TMPDIR_CQ/dropped.txt"
printf '%s\n' "$dropped" > "$dropped_f"
event_payload="$(python3 - "$verified_f" "$n_scoped" "$hot_file" "$report_file" "$dropped_f" "$scope_source" "$scope_reason" <<'PY'
import json, sys
verified_f, n_scoped, hot_file, report_file, dropped_f, scope_source, scope_reason = sys.argv[1:8]
d = json.load(open(verified_f))
dropped_list = [l for l in open(dropped_f, encoding="utf-8").read().splitlines() if l]
print(json.dumps({
    "n_files_scanned": int(n_scoped), "n_findings": len(d.get("findings", [])),
    "n_before_verify": d.get("n_before_verify"), "hot_core_this_week": hot_file or None,
    "scope_source": scope_source, "scope_fallback_reason": scope_reason or None,
    "report_file": report_file, "dropped_from_scope": dropped_list,
}, ensure_ascii=False))
PY
)"
"$ROOT/bin/append_event.sh" "$REVIEWER_ID" finding "code-quality-weekly-${TODAY}" "$event_payload" >/dev/null

summary_line="✅ code-quality-weekly ($TODAY): $n_scoped file quét, $n_final finding (sau verify)."
[ "$n_final" -eq 0 ] && summary_line="✅ code-quality-weekly ($TODAY): $n_scoped file quét, 0 finding — sạch."
[ "$scope_source" = "manifest" ] || summary_line="$summary_line ⚠️ SCOPE FALLBACK (không dùng production manifest): $scope_reason"

ARCH_TID="$("$ROOT/bin/discord_channel.sh" "$ARCH_THREAD_NAME" 2>/dev/null || true)"
if [ -n "$ARCH_TID" ]; then
  "$ROOT/bin/notify_thread.sh" "$summary_line Báo cáo: $report_file" "$ARCH_TID" 2>/dev/null || true
else
  log "WARN: không resolve được topic '$ARCH_THREAD_NAME' từ discord_channels.json — không gửi Discord."
fi

# --- 7. Tầng 3 auto-dispatch (user chốt 2026-09-17, plan §CẬP NHẬT 2026-09-17) ---
# Dispatch owner (Taylor/Wags) xử lý NGAY finding không chạm ranh giới cứng; escalate (bus
# question + Discord, KHÔNG dispatch) finding chạm logic đặt lệnh/NAV sống hoặc owner không rõ.
if [ "$n_final" -gt 0 ]; then
  log "Auto-dispatch (Tầng 3): $n_final finding → phân loại escalate/Taylor/Wags..."
  set +e
  autodispatch_out="$(python3 "$ROOT/bin/code_quality_autodispatch.py" \
    --verified "$verified_f" --date "$TODAY" --report-file "$report_file" --root "$ROOT" \
    --wc-root "$WORKDIR" ${ARCH_TID:+--arch-thread "$ARCH_TID"})"
  _ad_rc=$?
  set -e
  if [ $_ad_rc -eq 0 ]; then
    log "Auto-dispatch xong: $autodispatch_out"
  else
    log "WARN: code_quality_autodispatch.py rc=$_ad_rc — không dispatch được, xem log/kiểm tay. Output: $autodispatch_out"
  fi
else
  log "0 finding sau verify — không có gì để auto-dispatch."
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
