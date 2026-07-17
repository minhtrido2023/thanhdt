#!/usr/bin/env bash
# wags_autofix.sh "<label>" "<details>"          — pipeline đầy đủ (fix → review → báo cáo)
# wags_autofix.sh --review-topic "<substr>"      — chỉ chạy arch-review trên finding Wags mới nhất khớp substr
#
# CƠ CHẾ TỰ ĐỘNG cho lỗi VẬN HÀNH/TƯƠNG TÁC GIỮA CÁC AGENT team Mike (user mandate
# 2026-07-07): Wags (Fleet Ops Coordinator) tìm lỗi + tự sửa → arch-reviewer (chuyên gia
# kiến trúc tổ chức/điều phối agent, ~/.claude/agents/arch-reviewer.md, model fable, sinh
# ra để BÁC BỎ) audit lại → báo cáo hoàn tất vào TOPIC ARCHITECTURE (1521475726329516122).
#
# Phân định domain với ops_autofix.sh (Winston): Winston = lỗi vận hành TRADING/data/
# pipeline/report; Wags = lỗi ĐIỀU PHỐI giữa agent (dispatch treo/timeout, circuit breaker,
# question tồn, job board, bus, notification routing). Xem kb/ops_runbook.md.
#
# Verdict NEEDS_CHANGES/REFUTED → báo ⚠ vào topic architecture + bus question (không tự
# ép Wags sửa vòng 2 vô hạn — con người quyết ở vòng 2, chống ping-pong).
# Chống bão: cooldown 1h/label (chung cơ chế state/autofix của ops_autofix).
#
# Xác minh theo mức rủi ro (cost-opt #2, 2026-07-17): arch-reviewer (model fable, ~1500s
# timeout) chạy MẶC ĐỊNH cho MỌI fix trước đây — đúng cho fix chạm dispatch.sh/hooks (dùng
# chung toàn team), nhưng lãng phí cho fix cosmetic (sửa chữ thông báo, doc). Giờ
# bin/wags_risk_tier.py phân loại DỰA TRÊN files_changed Wags tự báo (không tin Wags tự
# chấm rủi ro): mọi file khớp allowlist ngắn, cố tình bảo thủ (kb/*.md, MIKE.md, notify.sh,
# chính wags_autofix.sh/ops_autofix.sh/jobs.sh) → "low" → bỏ qua arch-reviewer, chỉ ghi vào
# state/autofix/sample_queue.jsonl để audit lấy mẫu sau; BẤT KỲ gì khác (mặc định fail-safe
# "high" khi thiếu field/không phân loại được) → vẫn bắt buộc như cũ.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
ARCH_TOPIC="1521475726329516122"
CLAUDE="/home/trido/.local/bin/claude"
AGENT_DEF="$HOME/.claude/agents/arch-reviewer.md"
AUTOFIX_COOLDOWN="${AUTOFIX_COOLDOWN:-3600}"

# stdout PHẢI câm: notify_thread.sh in {"status":"sent"} ra stdout, từng lọt vào
# `tail -1` của caller và bị parse nhầm thành verdict (sự cố 2026-07-08, 2 question
# wags-fix-not-confirmed giả dù arch-reviewer đã CONFIRMED).
_notify_arch() { "$ROOT/bin/notify_thread.sh" "$1" "$ARCH_TOPIC" >/dev/null 2>&1 || true; }

# ---------- arch-review 1 finding của Wags (dùng chung cho cả 2 mode) ----------
_arch_review() {  # $1 = topic substring để chọn finding; in verdict_json ra stdout
  local substr="$1"
  local inbox="$ROOT/bus/inbox/Wags.jsonl"
  [ -f "$inbox" ] || { echo '{"verdict":"INCONCLUSIVE","summary":"Wags chưa có finding nào trên bus"}'; return 1; }
  local sel
  sel="$(python3 - "$inbox" "$substr" <<'PY'
import json, sys
inbox, sub = sys.argv[1], sys.argv[2]
pick = None
for ln in open(inbox, encoding="utf-8"):
    ln = ln.strip()
    if not ln: continue
    try: e = json.loads(ln)
    except Exception: continue
    if e.get("event_type") != "finding": continue
    if sub and sub.lower() not in (e.get("topic","") + json.dumps(e.get("payload",""))).lower(): continue
    pick = e
if not pick: sys.exit(3)
print(json.dumps({"topic": pick.get("topic",""), "finding": pick, "trace_id": pick.get("trace_id","")}, ensure_ascii=False))
PY
)" || { echo '{"verdict":"INCONCLUSIVE","summary":"không tìm thấy finding Wags khớp"}'; return 1; }
  local topic finding trace_id
  topic="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.load(sys.stdin)["topic"])')"
  finding="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["finding"], ensure_ascii=False))')"
  trace_id="$(printf '%s' "$sel" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("trace_id") or "")')"

  local sys_prompt log verdict_json
  sys_prompt="$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$AGENT_DEF")"
  mkdir -p "$ROOT/logs"
  log="$ROOT/logs/arch_review_$(date -u +%Y%m%d_%H%M%S).log"
  ( cd "$WC_ROOT" && "$CLAUDE" -p "$sys_prompt

--- FINDING CỦA WAGS CẦN AUDIT ---
$finding

Codebase: $WC_ROOT (fleet tooling ở $ROOT). Mở artifact thật finding trích dẫn (file/commit/
log/bus event), chạy đủ 7 hướng tấn công, rồi in ĐÚNG khối VERDICT_JSON." \
      --permission-mode auto --allowedTools "Bash Read Grep Glob" \
      --model fable --max-turns 40 > "$log" 2>"$log.err" ) || true

  verdict_json="$(python3 - "$log" "$topic" <<'PY'
import json, re, sys
log, topic = sys.argv[1], sys.argv[2]
try:
    txt = open(log, encoding="utf-8", errors="replace").read()
except Exception:
    txt = ""
m = re.search(r"<<<VERDICT_JSON>>>(.*?)<<<END_VERDICT>>>", txt, re.S)
if not m:
    print(json.dumps({"finding_topic": topic, "verdict": "INCONCLUSIVE", "confidence": "low",
                      "summary": "arch-reviewer không in được khối VERDICT_JSON — xem log"}))
    sys.exit(0)
try:
    obj = json.loads(m.group(1).strip())
except Exception as e:
    obj = {"finding_topic": topic, "verdict": "INCONCLUSIVE", "confidence": "low",
           "summary": "VERDICT_JSON không parse được: %s" % e}
obj.setdefault("finding_topic", topic)
print(json.dumps(obj, ensure_ascii=False))
PY
)"
  # ghi verdict lên bus (deterministic, ngoài agent) — cùng trace với finding gốc
  "$ROOT/bin/append_event.sh" arch-reviewer verification "ARCH-REVIEW: $topic" "$verdict_json" "$trace_id" >/dev/null 2>&1 || true
  printf '%s\n' "$verdict_json"
}

# ---------- mode: review-only ----------
if [ "${1:-}" = "--review-topic" ]; then
  substr="${2:?usage: wags_autofix.sh --review-topic <substr>}"
  v="$(_arch_review "$substr")"
  echo "$v"
  verdict="$(printf '%s' "$v" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("verdict","?"))')"
  summary="$(printf '%s' "$v" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("summary",""))')"
  _notify_arch "🧪 **Arch-review (ad-hoc)** — finding Wags khớp '$substr': **$verdict** — $summary"
  exit 0
fi

# ---------- mode: pipeline đầy đủ ----------
LABEL="${1:?usage: wags_autofix.sh \"<label>\" \"<details>\"  |  --review-topic <substr>}"
DETAILS="${2:-"(không có chi tiết — đọc log checker gọi tới)"}"

STATE_DIR="$ROOT/state/autofix"; mkdir -p "$STATE_DIR"
SLUG="$(printf '%s' "wags-$LABEL" | tr -cs 'a-zA-Z0-9' '-' | cut -c1-60)"
STAMP="$STATE_DIR/$SLUG.last"; NOW=$(date +%s)
if [ -f "$STAMP" ] && [ $((NOW - $(cat "$STAMP" 2>/dev/null || echo 0))) -lt "$AUTOFIX_COOLDOWN" ]; then
  _notify_arch "🔁 [wags-autofix] Vấn đề '$LABEL' TÁI DIỄN trong cooldown — fix trước có thể chưa ăn, cần người xem: $DETAILS"
  exit 0
fi
echo "$NOW" > "$STAMP"

_notify_arch "🔧 **[wags-autofix] Nhận issue điều phối: '$LABEL'** — Wags đang chẩn đoán + sửa; arch-reviewer sẽ audit trước khi báo hoàn tất. Chi tiết issue:
$DETAILS"

# Pipeline chạy nền tách session (setsid) — caller (cron/Mike turn) không bị giữ; job
# board + bus vẫn theo dõi được từng bước (nguyên tắc MIKE.md §1: không canh foreground).
PIPELOG="$ROOT/logs/wags_pipeline_$(date -u +%Y%m%d_%H%M%S).log"
setsid bash -c '
  ROOT="'"$ROOT"'"; LABEL='"$(printf %q "$LABEL")"'; DETAILS='"$(printf %q "$DETAILS")"'
  ARCH_TOPIC="'"$ARCH_TOPIC"'"
  _notify_arch() { "$ROOT/bin/notify_thread.sh" "$1" "$ARCH_TOPIC" >/dev/null 2>&1 || true; }

  # 1) Wags fix (đồng bộ trong pipeline nền; timeout rộng vì job chẩn đoán sâu). Wags
  #    tự nhận context ops-mini qua chính agents/Wags/CLAUDE.md (cost-opt #1b,
  #    2026-07-17) — không cần cờ gì ở đây. BẮT BUỘC báo files_changed (mảng đường dẫn
  #    tương đối) trong payload finding — đây là
  #    input DUY NHẤT cho phân loại rủi ro ở bước 2 (không dựa vào Wags tự chấm "rủi ro
  #    thấp", tránh Wags tự miễn review cho chính nó — verify ARTIFACT, không tin
  #    self-report, cùng nguyên tắc đã áp dụng ở idempotency guard/ghost-order).
  out="$("$ROOT/bin/dispatch.sh" Wags "NHIỆM VỤ WAGS-AUTOFIX (issue điều phối giữa agent, mandate 2026-07-07): '"'"'$LABEL'"'"'
CHI TIẾT: $DETAILS
Quy trình: (1) chẩn đoán từ artifact thật (jobs.sh list cột HB_AGE, trace.sh, bus, log) — đọc kb/ops_runbook.md + working memory của bạn trước; (2) SỬA trong ranh giới: được sửa tooling điều phối (dispatch.sh/jobs.sh/mike_json.py/ops_autofix/wags_autofix/checker) sau khi test, TUYỆT ĐỐI không đụng trading (plan/executor/cron thực thi/trading_rules); (3) verify artifact sau sửa (chạy lại lệnh lỗi, xác nhận hết); (4) ghi bus finding topic bắt đầu bằng '"'"'wags-fix: $LABEL'"'"' kèm root_cause/fix/verify/commit + field \"files_changed\": [danh sách ĐẦY ĐỦ đường dẫn tương đối bạn đã sửa, vd [\"bin/dispatch.sh\",\"MIKE.md\"]] — field này quyết định fix có cần arch-reviewer audit đầy đủ hay không, KHÔNG được bỏ trống hay báo thiếu file." --timeout 1500 --retries 0 --model fable 2>&1)" || true
  echo "$out" >> "'"$PIPELOG"'"

  # 2) Phân loại rủi ro (cost-opt #2, 2026-07-17): fix chỉ đụng path an toàn tuyệt đối
  #    (kb/docs, notify.sh, chính wags_autofix.sh/ops_autofix.sh/jobs.sh) -> bỏ qua
  #    arch-reviewer đắt tiền, chỉ log vào hàng đợi audit lấy mẫu. Bất kỳ gì khác
  #    (đặc biệt dispatch.sh/hooks — plumbing DÙNG CHUNG toàn team) -> vẫn bắt buộc như
  #    cũ. Fail-safe mặc định "high" nếu không phân loại được (xem wags_risk_tier.py).
  tier="$("$ROOT/bin/wags_risk_tier.py" "'"$ROOT"'/bus/inbox/Wags.jsonl" "wags-fix: $LABEL" 2>>"'"$PIPELOG"'" || echo high)"

  if [ "$tier" = "low" ]; then
    mkdir -p "'"$ROOT"'/state/autofix"
    printf "%s\n" "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"label\":\"$LABEL\",\"topic\":\"wags-fix: $LABEL\"}" \
      >> "'"$ROOT"'/state/autofix/sample_queue.jsonl"
    _notify_arch "✅ **[wags-autofix] HOÀN TẤT issue '"'"'$LABEL'"'"'** (LOW-RISK — chỉ đụng docs/tooling tự chứa, bỏ qua arch-reviewer đầy đủ, đưa vào hàng đợi audit lấy mẫu). Wags đã tự verify. Chi tiết: bus finding '"'"'wags-fix: $LABEL'"'"'; log pipeline: '"$PIPELOG"'"
  else
  # arch-review finding vừa tạo — KHÔNG tail -1 mù: chọn dòng JSON cuối có key
  # "verdict" (chống output lạ chen vào stdout, vd {"status":"sent"} của notify)
  v="$("$ROOT/bin/wags_autofix.sh" --review-topic "wags-fix: $LABEL" 2>>"'"$PIPELOG"'" | python3 -c "import json,sys
last={}
for ln in sys.stdin:
    ln=ln.strip()
    if not ln: continue
    try: o=json.loads(ln)
    except Exception: continue
    if isinstance(o,dict) and \"verdict\" in o: last=o
print(json.dumps(last, ensure_ascii=False))")"
  verdict="$(printf "%s" "$v" | python3 -c "import json,sys
try: print(json.load(sys.stdin).get(\"verdict\",\"?\"))
except Exception: print(\"?\")")"
  summary="$(printf "%s" "$v" | python3 -c "import json,sys
try: print(json.load(sys.stdin).get(\"summary\",\"\"))
except Exception: print(\"\")")"

  # 3) báo cáo hoàn tất vào topic architecture (user yêu cầu: báo khi issue hoàn tất)
  if [ "$verdict" = "CONFIRMED" ]; then
    _notify_arch "✅ **[wags-autofix] HOÀN TẤT issue '"'"'$LABEL'"'"'** — Wags đã sửa, arch-reviewer audit: **CONFIRMED** ($summary). Chi tiết: bus finding '"'"'wags-fix: $LABEL'"'"' + verification cùng trace; log pipeline: '"$PIPELOG"'"
  else
    _notify_arch "⚠️ **[wags-autofix] Issue '"'"'$LABEL'"'"' CẦN NGƯỜI XEM** — arch-reviewer verdict: **$verdict** ($summary). Fix của Wags KHÔNG được tự coi là xong; xem bus verification + log '"$PIPELOG"'."
    "$ROOT/bin/append_event.sh" Wags question "wags-fix-not-confirmed: $LABEL" \
      "{\"verdict\":\"$verdict\",\"pipelog\":\"'"$PIPELOG"'\"}" >/dev/null 2>&1 || true
  fi
  fi
' >> "$PIPELOG" 2>&1 < /dev/null &

echo "[wags_autofix] pipeline launched for '$LABEL' (log: $PIPELOG)"
