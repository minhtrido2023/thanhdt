#!/usr/bin/env bash
# Selfcheck: khối đếm cảnh báo measured_by trong daily_retro.sh (2026-10-13) là FAIL-OPEN và KHÔNG
# làm đổi phần còn lại của retro. Chạy THẬT daily_retro.sh trong sandbox với dispatch.sh GIẢ (chỉ
# ghi lại prompt) — KHÔNG dispatch Mike/Wags thật, KHÔNG đụng bus/crontab thật.
# Bất biến: với helper {có | vắng | nổ | treo | in rác}: (1) rc retro không đổi, (2) vẫn đúng 3
# dispatch Mike→Wags→Mike, (3) prompt Wags + prompt finalize GIỐNG HỆT từng byte, (4) prompt draft
# chỉ khác nhau trong đoạn từ "2f." tới "2b.", (5) đoạn 2f luôn có câu KHÔNG escalate.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pass=0; fail=0
ok() { if [ "$2" = 1 ]; then pass=$((pass+1)); echo "PASS $1"; else fail=$((fail+1)); echo "FAIL $1 ${3:-}"; fi; }

mk() { # <dir> <helper_body|-> : dựng sandbox
  local d="$1" body="$2"
  mkdir -p "$d/bin" "$d/logs" "$d/state"
  cp "$ROOT/bin/usage_limit_phrases.sh" "$d/bin/"
  cp "${RETRO_SRC:-$ROOT/bin/daily_retro.sh}" "$d/bin/daily_retro.sh"
  printf '' > "$d/bin/time_claim_audit.py"
  printf '#!/usr/bin/env bash\nexit 0\n' > "$d/bin/notify.sh"
  printf '#!/usr/bin/env bash\nexit 0\n' > "$d/bin/append_event.sh"
  cat > "$d/bin/dispatch.sh" <<'STUB'
#!/usr/bin/env bash
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
n=$(( $(cat "$R/calls.n" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$R/calls.n"
printf '%s' "$2" > "$R/prompt.$n"; echo "$1" > "$R/target.$n"
if [ "$n" = 1 ]; then
  f="$R/$(printf '%s' "$2" | grep -o 'state/retro_draft_[0-9-]*\.md' | head -1)"
  printf '# RETRO — %s: 0 sự cố\n' "$(printf '%s' "$f" | grep -o '[0-9]\{4\}-[0-9-]*')" > "$f"
fi
echo CONFIRMED
STUB
  chmod +x "$d/bin/"*.sh
  [ "$body" = "-" ] || printf '%s\n' "$body" > "$d/bin/measured_by_warn_report.py"
  # Biến thể real: seed 1 cảnh báo MỚI để chứng minh số đếm THẬT (không phải câu fallback) vào prompt.
  if [ "$body" != "-" ] && [ "${SEED:-}" = 1 ]; then
    mkdir -p "$d/bus"
    printf '{"ts":"%s","agent_id":"Seed","topic":"seed-topic","trace_id":"T1"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$d/bus/_measured_by_warn.jsonl"
  fi
}
run() { # <dir> -> rc; chờ finalize nền
  local t0=$SECONDS
  ( cd "$1" && env -u TZ DAILY_RETRO_MB_TIMEOUT=2 bash bin/daily_retro.sh >/dev/null 2>&1 ); local rc=$?
  echo $((SECONDS - t0)) > "$1/elapsed"; sleep 1; echo "$rc"
}

T="$(mktemp -d)"; [ -n "${KEEP:-}" ] && echo "T=$T"; [ -n "${KEEP:-}" ] || trap 'rm -rf "$T"' EXIT
declare -A body=(
  [real]="$(cat "$ROOT/bin/measured_by_warn_report.py")"
  [absent]="-"
  [crash]=$'import sys\nsys.stderr.write("boom")\nraise SystemExit(7)'
  [hang]=$'import time\ntime.sleep(60)'
  [empty]=$'pass'
)
declare -A rc
VARIANTS="real absent crash hang empty"
for k in $VARIANTS; do
  SEED=$([ "$k" = real ] && echo 1 || echo 0) mk "$T/$k" "${body[$k]}"; rc[$k]="$(run "$T/$k")"
done
# TUỲ CHỌN (bằng chứng 1 lần, không chạy mặc định): BASELINE_RETRO=<daily_retro.sh BẢN CŨ> ⇒ thêm biến
# thể `old` (script cũ, không helper) và đòi nó khớp từng byte với `real` ngoài mục 2f.
if [ -n "${BASELINE_RETRO:-}" ]; then
  RETRO_SRC="$BASELINE_RETRO" mk "$T/old" "-"; rc[old]="$(run "$T/old")"; VARIANTS="$VARIANTS old"
fi

for k in $VARIANTS; do
  ok "[$k] rc retro = rc của biến thể real (${rc[$k]})" "$([ "${rc[$k]}" = "${rc[real]}" ] && echo 1 || echo 0)"
  ok "[$k] đúng 3 dispatch Mike→Wags→Mike" "$([ "$(cat "$T/$k/calls.n" 2>/dev/null)" = 3 ] && [ "$(cat "$T/$k/target.1")$(cat "$T/$k/target.2")$(cat "$T/$k/target.3")" = MikeWagsMike ] && echo 1 || echo 0)"
  # Chuẩn hoá đường dẫn sandbox (mỗi biến thể 1 thư mục) và RUN_START_TS (đổi theo giây) trước khi so.
  nrm() { sed -E "s|$T/$1|SANDBOX|g; s/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]{8}Z/RUN_START_TS/g" "$T/$1/prompt.$2"; }
  ok "[$k] prompt Wags giống real" "$([ "$(nrm "$k" 2)" = "$(nrm real 2)" ] && echo 1 || echo 0)"
  # finalize chứa draft/Wags (không có ngày/giờ tự đổi) ⇒ phải giống hệt
  ok "[$k] prompt finalize giống real" "$([ "$(nrm "$k" 3)" = "$(nrm real 3)" ] && echo 1 || echo 0)"
  strip() { python3 -c 'import re,sys;s=sys.stdin.read();print(re.sub(r"2f\..*?(?=2b\. VERIFY)","",s,flags=re.S))'; }
  ok "[$k] prompt draft chỉ khác trong mục 2f" "$([ "$(nrm "$k" 1 | strip)" = "$(nrm real 1 | strip)" ] && echo 1 || echo 0)"
  [ "$k" = old ] || ok "[$k] mục 2f có câu KHÔNG escalate" "$(grep -q 'KHÔNG escalate, KHÔNG tạo question' "$T/$k/prompt.1" && echo 1 || echo 0)"
done
ok "[real] số đếm THẬT của helper vào prompt (cảnh báo: 24h=1, agent Seed) — không phải câu fallback" "$(grep -q 'cảnh báo: 24h=1 ' "$T/real/prompt.1" && grep -q 'Seed=1' "$T/real/prompt.1" && ! grep -q 'helper không chạy được' "$T/real/prompt.1" && echo 1 || echo 0)"
for k in absent crash empty; do ok "[$k] mục 2f rơi về ĐÚNG câu fallback 'helper không chạy được'" "$(grep -q 'helper không chạy được' "$T/$k/prompt.1" && echo 1 || echo 0)"; done
ok "[hang] helper treo 60s bị timeout cắt: retro xong <20s (thực $(cat "$T/hang/elapsed")s)" "$([ "$(cat "$T/hang/elapsed")" -lt 20 ] && echo 1 || echo 0)"
ok "[hang] mục 2f rơi về ĐÚNG câu fallback (timeout cắt)" "$(grep -q 'helper không chạy được' "$T/hang/prompt.1" && echo 1 || echo 0)"
ok "mặc định timeout helper trong daily_retro.sh = 20s (selfcheck đặt 2s nên phải ghim tĩnh)" "$(grep -q 'DAILY_RETRO_MB_TIMEOUT:-20}' "${RETRO_SRC:-$ROOT/bin/daily_retro.sh}" && echo 1 || echo 0)"
# $LOG: mỗi lần chạy đúng 1 dòng [measured-by-warn] — để helper hỏng vĩnh viễn không bị im lặng (review 13/10, C3).
lg() { grep -h '\[measured-by-warn\]' "$T/$1/logs/daily_retro.log" 2>/dev/null; }
for k in real absent crash hang empty; do ok "[$k] đúng 1 dòng [measured-by-warn] trong \$LOG" "$([ "$(lg $k | wc -l)" = 1 ] && echo 1 || echo 0)"; done
ok "[real] dòng log báo 'ok' (có số đếm thật)" "$(lg real | grep -q ' ok$' && echo 1 || echo 0)" "$(lg real)"
for k in absent crash hang empty; do ok "[$k] dòng log đánh dấu KHÔNG-CÓ-SỐ-ĐẾM" "$(lg $k | grep -q 'KHÔNG-CÓ-SỐ-ĐẾM' && echo 1 || echo 0)" "$(lg $k)"; done
ok "[crash] dòng log mang stderr thật của helper ('boom')" "$(lg crash | grep -q 'boom' && echo 1 || echo 0)" "$(lg crash)"
# ── Nhánh VƯỢT NGƯỠNG classifier (decision-inbox vòng 2, mục 7): payload leo thang KHÔNG được rỗng ──
# Stub classifier_denial_count.py (cùng hình dạng JSON với bản thật) + retro_escalate.py (ghi lại --payload).
mkclf() { # <dir> <mike_count> <close_count>
  local d="$1"
  SEED=0 mk "$d" "-"
  cat > "$d/bin/classifier_denial_count.py" <<PYSTUB
import json
print(json.dumps({"day": "2026-11-13", "total": $2, "by_agent": {"Mike": $2, "Taylor": 0}, "by_cmd_top5": [], "close_bus_question": $3}))
PYSTUB
  cat > "$d/bin/retro_escalate.py" <<'PYSTUB'
import json, os, sys
a = sys.argv[1:]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "escalate.payload"), "w").write(a[a.index("--payload") + 1])
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "escalate.args"), "w").write(" ".join(a[:a.index("--payload")]))
PYSTUB
}
mkclf "$T/clf_over" 9 0;  rc[clf_over]="$(run "$T/clf_over")"
mkclf "$T/clf_close" 1 2; rc[clf_close]="$(run "$T/clf_close")"
mkclf "$T/clf_under" 1 0; rc[clf_under]="$(run "$T/clf_under")"
pj() { python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); v=d.get(sys.argv[2]); print("" if v is None else (json.dumps(v,ensure_ascii=False) if not isinstance(v,str) else v))' "$T/$1/escalate.payload" "$2" 2>/dev/null; }
for k in clf_over clf_close; do
  ok "[$k] retro_escalate được gọi với payload JSON hợp lệ" "$(python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$T/$k/escalate.payload" 2>/dev/null && echo 1 || echo 0)"
  ok "[$k] payload có summary KHÔNG rỗng (≥40 ký tự)" "$([ "$(pj $k summary | wc -c)" -ge 40 ] && echo 1 || echo 0)" "$(pj $k summary)"
  ok "[$k] payload có ≥2 options, mỗi option bắt đầu bằng nhãn A:/B:" "$(python3 -c 'import json,sys; o=json.load(open(sys.argv[1]))["options"]; sys.exit(0 if len(o)>=2 and all(x.startswith(chr(65+i)+":") for i,x in enumerate(o)) else 1)' "$T/$k/escalate.payload" 2>/dev/null && echo 1 || echo 0)"
  ok "[$k] payload có recommendation KHÔNG rỗng" "$([ -n "$(pj $k recommendation)" ] && echo 1 || echo 0)"
  ok "[$k] payload risk = normal (câu allow-list không phải câu tiền)" "$([ "$(pj $k risk)" = normal ] && echo 1 || echo 0)"
  ok "[$k] payload vẫn mang số đếm thô + measured_by" "$([ -n "$(pj $k by_agent)" ] && [ -n "$(pj $k measured_by)" ] && echo 1 || echo 0)"
  ok "[$k] gọi đúng --pattern classifier-denials-mike --days 1" "$(grep -q -- '--pattern classifier-denials-mike --days 1' "$T/$k/escalate.args" && echo 1 || echo 0)"
  ok "[$k] retro vẫn đủ 3 dispatch Mike→Wags→Mike" "$([ "$(cat "$T/$k/calls.n" 2>/dev/null)" = 3 ] && echo 1 || echo 0)"
done
ok "[clf_over] summary nêu số lần thật (9) và ngưỡng (5)" "$(pj clf_over summary | grep -q '9 lần' && pj clf_over summary | grep -q 'ngưỡng 5' && echo 1 || echo 0)" "$(pj clf_over summary)"
ok "[clf_close] ca close_bus_question bị chặn (2 lần) nêu trong summary" "$(pj clf_close summary | grep -q '2 lần chặn close_bus_question' && echo 1 || echo 0)" "$(pj clf_close summary)"
ok "[clf_under] dưới ngưỡng ⇒ KHÔNG escalate" "$([ ! -e "$T/clf_under/escalate.payload" ] && echo 1 || echo 0)"
echo "---"; echo "PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ]
