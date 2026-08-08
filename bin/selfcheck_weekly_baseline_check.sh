#!/usr/bin/env bash
# selfcheck_weekly_baseline_check.sh — chạy TOÀN BỘ 51 selfcheck ở gốc WorkingClaude/ 1 lần/tuần
# (gọi từ kb_nightly.sh Phase 5, chỉ thứ Sáu) và so với kb/selfcheck_baseline.json.
#
# VÌ SAO CẦN (2026-08-08, coding_guidelines.md §23): "9 đỏ là bình thường" là chính lỗ hổng khiến
# regression thật lẫn vào nhiễu. Baseline biến "đỏ nào đã biết" từ tri thức truyền miệng thành 1
# file JSON diff được — đỏ MỚI (không có trong known_red) mới đáng báo động.
#
# ⚠️ BẮT BUỘC dùng đúng $DNA_PYEXE (Python 3.12 + pandas 3) + GOOGLE_APPLICATION_CREDENTIALS +
# PATH có gcloud sdk — chạy sai môi trường tự tạo FAIL/TIMEOUT giả (đã đo thật tối 2026-08-08:
# 4/51 file báo lỗi sai chỉ vì Mike verify bằng system python3 thay vì $DNA_PYEXE). Env này lấy
# từ chính kb/selfcheck_baseline.json's required_env, không hardcode 2 lần.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC="/home/trido/thanhdt/WorkingClaude"
BASELINE="$ROOT/kb/selfcheck_baseline.json"
DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export GOOGLE_APPLICATION_CREDENTIALS="/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"
export MIKE_BOT_TEST_MODE=1

[ -x "$DNA_PYEXE" ] || { echo "FATAL: DNA_PYEXE không tồn tại: $DNA_PYEXE" >&2; exit 2; }
[ -f "$BASELINE" ] || { echo "FATAL: thiếu baseline: $BASELINE" >&2; exit 2; }

cd "$WC" || exit 2
RESULT_JSON="$ROOT/logs/selfcheck_weekly_$(date -u +%Y%m%d).json"
JSONL="$ROOT/logs/.selfcheck_weekly_raw_$$.jsonl"
mkdir -p "$ROOT/logs"
: > "$JSONL"

for f in *selfcheck*.py; do
    tmo="$(python3 -c "
import json
b=json.load(open('$BASELINE'))
print(b['required_env']['slow_files'].get('$f', b['required_env']['default_timeout_s']))
")"
    log="/tmp/wk_sc_$$_$f.log"
    timeout "$tmo" "$DNA_PYEXE" "$f" > "$log" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then st=PASS; elif [ $rc -eq 124 ]; then st=TIMEOUT; else st=FAIL; fi
    python3 -c "import json,sys; print(json.dumps({'file': sys.argv[1], 'status': sys.argv[2]}))" "$f" "$st" >> "$JSONL"
    rm -f "$log"
done

# So với baseline, quyết định cần báo động hay không, tự cập nhật known_red khi ĐỎ->XANH.
python3 - "$BASELINE" "$RESULT_JSON" "$JSONL" <<'PYEOF'
import json, sys, datetime
baseline_path, result_path, jsonl_path = sys.argv[1], sys.argv[2], sys.argv[3]
results = {}
with open(jsonl_path, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        results[rec["file"]] = rec["status"]
baseline = json.load(open(baseline_path, encoding="utf-8"))
known_red = baseline.get("known_red", {})

new_red = {k: v for k, v in results.items() if v != "PASS" and k not in known_red}
now_green = [k for k in known_red if results.get(k) == "PASS"]
still_red_known = {k: v for k, v in results.items() if v != "PASS" and k in known_red}

out = {"ts": datetime.datetime.utcnow().isoformat() + "Z",
       "total": len(results), "pass": sum(1 for v in results.values() if v == "PASS"),
       "new_red": new_red, "now_green_remove_from_baseline": now_green,
       "still_red_known": list(still_red_known.keys()), "raw": results}
json.dump(out, open(result_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

if now_green:
    for k in now_green:
        del baseline["known_red"][k]
    json.dump(baseline, open(baseline_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"BASELINE_UPDATED: {len(now_green)} file(s) removed from known_red (now green): {now_green}")

if new_red:
    print(f"NEW_RED: {len(new_red)} file(s) NOT in baseline: {new_red}")
    sys.exit(1)
print(f"OK: {out['pass']}/{out['total']} PASS, {len(still_red_known)} known-red unchanged")
PYEOF
rc=$?
rm -f "$JSONL"

if [ $rc -ne 0 ]; then
    "$ROOT/bin/notify.sh" "🔴 [selfcheck weekly] Phát hiện selfcheck ĐỎ MỚI không có trong baseline — xem $RESULT_JSON. Đây là tín hiệu regression thật (baseline chỉ chứa đỏ đã biết/đã chấp nhận)." >/dev/null 2>&1 || true
    "$ROOT/bin/append_event.sh" Mike error "selfcheck-weekly-new-red" \
      "{\"result_file\": \"$RESULT_JSON\"}" >/dev/null 2>&1 || true
fi
exit $rc
