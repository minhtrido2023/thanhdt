#!/usr/bin/env bash
# work_tree_verify_daily.sh — xác minh HẰNG NGÀY các mục "chờ anh quyết" + "quá hạn" của cây việc với THỰC TẾ.
# Vì sao: cây chỉ derive từ bus/watchlist/ledger; mục nào xong bằng kênh khác (merge, cron đã cài, user chốt ở
# Discord) mà không ai ghi vào ledger thì cứ hiện "chờ/quá hạn" mãi (ca 2026-11-07: 6/12 mục chờ quyết sai).
# Luật: chỉ ĐÓNG/CẬP NHẬT khi có artifact dẫn được (commit, crontab, log, bus answer); không dẫn được => ghi note
# "verified_open" (làm mới `updated`) và GIỮ NGUYÊN trạng thái. KHÔNG quyết thay user, KHÔNG sửa code/cron/plan.
# Cron: 30 0 * * *  (07:30 ICT, trước build 07:50 và bản tin 08:00). Marker: state/work_tree/verified_<ngày ICT>.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CANON="$(python3 "$ROOT/bin/wc_paths.py" --mike-canonical 2>/dev/null || echo "$ROOT")"
TODAY="$(TZ=Asia/Ho_Chi_Minh date +%F)"
MARK="$CANON/state/work_tree/verified_$TODAY"
[ -e "$MARK" ] && [ "${1:-}" != "--force" ] && { echo "đã xác minh hôm nay"; exit 0; }
cd "$CANON" || exit 1
TZ=Asia/Ho_Chi_Minh timeout 120 python3 bin/work_tree_build.py --quiet || echo "WARN: build trước verify lỗi" >&2
read -r -d '' PROMPT <<'PEOF' || true
Xác minh cây việc (state/work_tree/merged.json) với THỰC TẾ. Với MỖI id trong attention.need_user và attention.overdue:
1) Đọc item (summary/waiting_on/due/links). 2) Tìm bằng chứng việc đã xong/đổi qua kênh khác: git log (--grep, --since=30 days) ở
mike/ và WorkingClaude/, crontab -l, kb/current_ops*.md, kb/memory/Mike.md, kb/projects/<stem>.md, bus answer (bin/bus_question_audit.py),
logs/. 3) Quyết:
 - ĐÃ XONG/THAY ĐỔI có bằng chứng dẫn được -> python3 bin/work_ledger.py --by Wags close <id> closed "<bằng chứng: commit/dòng cron/file>" (hoặc upsert needs_user=false waiting_on=... nếu chỉ hết cần user).
 - VẪN MỞ thật -> python3 bin/work_ledger.py --by Wags note <id> "verified_open <ngày ICT>: <1 câu: còn chờ gì, ai>" (không đổi status).
 - Không chắc -> coi là VẪN MỞ; KHÔNG đóng khi thiếu bằng chứng. Câu hỏi bus (busq:) KHÔNG đóng bằng ledger; nếu thật sự đã giải quyết thì
   dùng bin/close_bus_question.py theo skill bus-question-closure, KHÔNG khai decided_by user.
Cấm: quyết thay user, sửa code/cron/plan/trading_rules, gửi tin Discord. Cuối cùng chạy python3 bin/work_tree_build.py --quiet và
in: số mục đã đóng / cập nhật / giữ mở + 1 dòng mỗi mục đóng kèm bằng chứng.
PEOF
OUT="$(bin/dispatch.sh Wags "$PROMPT" --timeout 1500 2>&1)"; RC=$?
echo "$OUT" | tail -15
if [ $RC -eq 0 ]; then touch "$MARK"; else echo "work_tree_verify_daily: dispatch rc=$RC" >&2; fi
TZ=Asia/Ho_Chi_Minh timeout 120 python3 bin/work_tree_build.py --quiet
exit $RC
