#!/usr/bin/env bash
# run_selfchecks.sh [--live] — chạy lại MỌI selfcheck đang có trong fleet, không chỉ 4/66 như
# hiện trạng (khảo sát vận hành 2026-08-01, item #2 đã duyệt). Registry KHÔNG hand-maintain
# (sẽ trôi đúng kiểu file này sinh ra để bịt) — tự khám phá bằng glob mỗi lần chạy, tự phân
# loại offline/live bằng grep, tự ghi state + report snapshot. Nguồn sự thật = code thật lúc
# chạy, không phải 1 danh sách tĩnh ai đó gõ tay 1 lần rồi quên cập nhật.
#
# Mặc định: chỉ tier OFFLINE (không chạm bq/dnse_api/network — tuyệt đại đa số, an toàn chạy
# thường xuyên). --live: thêm tier LIVE (chạm BQ/DNSE thật — chậm hơn, có thể tốn quota).
#
# Loại trừ CÓ CHỦ Ý: thư mục exp_*/job_2026*/v4final_exp (coding_guidelines.md §8/§10 —
# artifact nghiên cứu 1 lần, namespaced, không phải regression test đứng — chạy lại vô nghĩa
# và một số phụ thuộc state/data đã archive từ lâu).
set -uo pipefail

WC_ROOT="/home/trido/thanhdt/WorkingClaude"
MIKE="$WC_ROOT/mike"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true
PY="${DNA_PYEXE:-python3}"

MODE="${1:-}"
RUN_LIVE=0
[ "$MODE" = "--live" ] && RUN_LIVE=1

STATE_FILE="$MIKE/state/selfcheck_runs.json"
REGISTRY_MD="$MIKE/kb/selfcheck_registry.md"
mkdir -p "$MIKE/state"

# 1) Khám phá — cùng exclude-pattern đã verify tay lúc thiết kế (khảo sát vận hành 2026-08-01).
mapfile -t FILES < <(cd "$WC_ROOT" && find . \( -iname "*selfcheck*.py" -o -iname "*selfcheck*.sh" \) \
  2>/dev/null | grep -v node_modules | grep -v __pycache__ \
  | grep -vE "/exp_|/job_2026|v4final_exp|/data/fscore_c30v" | sed 's|^\./||' | sort)

echo "Tìm thấy ${#FILES[@]} selfcheck (đã loại exp_*/job_2026*/v4final_exp — artifact 1 lần)."

# 2) Phân loại tier — grep heuristic. LẦN ĐẦU CHẠY THẬT (2026-08-01) bắt được chính heuristic
# này thiếu: chỉ khớp literal "bq query"/"bq show" bỏ sót MỌI script gọi qua wrapper
# `simulate_holistic_nav.bq()` (10 file) — 1 trong số đó (immutable_publish_selfcheck.py) ăn
# hết timeout 300s vì bị coi nhầm là offline. Thêm pattern import wrapper. Sai lệch còn lại chỉ
# ảnh hưởng THỨ TỰ chạy — file LIVE lọt lưới vẫn chạy (chỉ timeout dài hơn dự kiến), file
# offline bị phân nhầm "live" thì bị bỏ qua khi không có --live (an toàn hơn, không phải
# false-negative nguy hiểm).
is_live() {
  grep -qE "bq query|bq show|dnse_api|requests\.(get|post)|urllib\.request|subprocess.*[\"']bq |from simulate_holistic_nav import|import simulate_holistic_nav|state_publish_immutable" \
    "$WC_ROOT/$1" 2>/dev/null
}

PASS=0; FAIL=0; SKIP=0
RESULTS=()   # "file|tier|status|seconds"

for f in "${FILES[@]}"; do
  tier="offline"
  is_live "$f" && tier="live"
  if [ "$tier" = "live" ] && [ "$RUN_LIVE" -ne 1 ]; then
    SKIP=$((SKIP + 1))
    RESULTS+=("$f|$tier|SKIP(--live để chạy)|-")
    continue
  fi
  # offline = sandbox tmpdir, phải nhanh (giây) — 60s đủ rộng phòng máy chậm; live = BQ/network
  # thật, cho tới 300s. Timeout mismatch (offline hoá ra chậm) tự nó LÀ 1 finding đáng xem lại
  # phân loại, không chỉ tăng số cho qua.
  t=60; [ "$tier" = "live" ] && t=300
  start=$(date +%s)
  if [[ "$f" == *.sh ]]; then
    ( cd "$WC_ROOT" && timeout "$t" bash "$f" ) >/tmp/rsc_out.$$ 2>&1
    rc=$?
  else
    ( cd "$WC_ROOT" && timeout "$t" "$PY" "$f" ) >/tmp/rsc_out.$$ 2>&1
    rc=$?
  fi
  dur=$(( $(date +%s) - start ))
  if [ "$rc" -eq 0 ]; then
    PASS=$((PASS + 1)); status="PASS"
  else
    FAIL=$((FAIL + 1)); status="FAIL(rc=$rc)"
    echo "--- FAIL: $f (rc=$rc, ${dur}s) ---"
    tail -15 /tmp/rsc_out.$$
  fi
  RESULTS+=("$f|$tier|$status|${dur}s")
  rm -f /tmp/rsc_out.$$
done

# 3) Ghi state (JSON, machine-readable — cho lần chạy sau đối chiếu "mới FAIL" vs "FAIL từ lâu").
python3 - "$STATE_FILE" "${RESULTS[@]}" <<'PYEOF'
import json, sys, datetime
state_file = sys.argv[1]
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
try:
    prev = json.load(open(state_file))
except Exception:
    prev = {}
for row in sys.argv[2:]:
    f, tier, status, dur = row.split("|")
    entry = prev.get(f, {})
    entry["tier"] = tier
    entry["last_run"] = now
    entry["last_status"] = status
    if status.startswith("PASS"):
        entry["last_green"] = now
    prev[f] = entry
with open(state_file + ".tmp", "w") as fh:
    json.dump(prev, fh, ensure_ascii=False, indent=1, sort_keys=True)
import os
os.replace(state_file + ".tmp", state_file)
PYEOF

# 4) Snapshot registry.md — SINH LẠI mỗi lần chạy, không hand-maintain (tránh đúng lớp trôi
# việc này sinh ra để bịt). Header cảnh báo rõ đây là auto-generated.
{
  echo "---"
  echo "kind: reference"
  echo "title: Selfcheck registry — snapshot tự sinh, ĐỪNG sửa tay"
  echo "generated_by: bin/run_selfchecks.sh"
  echo "generated_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "---"
  echo
  echo "# Selfcheck registry (auto-generated, ĐỪNG sửa tay — sửa \`bin/run_selfchecks.sh\`)"
  echo
  echo "Chạy: \`bash mike/bin/run_selfchecks.sh [--live]\`. Lần gần nhất: $PASS PASS / $FAIL FAIL / $SKIP SKIP (live)."
  echo
  echo "| File | Tier | Status | Thời gian |"
  echo "|---|---|---|---|"
  for row in "${RESULTS[@]}"; do
    IFS='|' read -r f tier status dur <<< "$row"
    echo "| \`$f\` | $tier | $status | $dur |"
  done
} > "$REGISTRY_MD"

echo
echo "=== TỔNG: $PASS PASS / $FAIL FAIL / $SKIP SKIP (live, dùng --live để chạy) / ${#FILES[@]} tổng ==="
echo "State: $STATE_FILE | Registry: $REGISTRY_MD"
[ "$FAIL" -gt 0 ] && exit 1
exit 0
