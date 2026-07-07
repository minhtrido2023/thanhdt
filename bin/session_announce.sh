#!/usr/bin/env bash
# session_announce.sh <lunch|afternoon|close>
#
# Thông báo MỐC PHIÊN giao dịch bằng ngôn ngữ thân thiện vào Trading Daily (user yêu cầu
# 2026-07-07: "diễn giải hoạt động vận hành của team một cách minh bạch, tường minh...
# thân thiện hơn với người dùng") — trước đây bot dừng nghỉ trưa (pkill 11:30) hoàn toàn
# im lặng, user không biết bot đang nghỉ hay đã chết.
#
# Kèm tiến độ thực từng account live (đọc journal thật, không đoán):
#   lunch     11:31 ICT — phiên sáng kết thúc, bot tạm ngưng, hẹn 13:00
#   afternoon 13:01 ICT — phiên chiều bắt đầu, bot đã khởi động lại
#   close     14:50 ICT — phiên đóng (ATC ~14:45), lệnh treo tự hủy, EOD report 15:00
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_DAILY_THREAD="1521470705563340910"
PHASE="${1:?usage: session_announce.sh <lunch|afternoon|close>}"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"

# Tiến độ mỗi account live: "SpaceX 0/0 (HOLD)" / "ZaloPay 1/2 lệnh hoàn tất"
PROGRESS="$(cd "$WC_ROOT" && python3 - "$TODAY" << 'PYEOF'
import csv, json, os, sys
sys.path.insert(0, ".")
from trading_bot.config import live_dnse_labels

today = sys.argv[1]
lines = []
for acc in live_dnse_labels():
    plan_path = os.path.join("data", "trade_plans", f"plan_{acc}_{today}.json")
    n_orders = None
    if os.path.exists(plan_path):
        try:
            n_orders = len(json.load(open(plan_path, encoding="utf-8")).get("orders", []))
        except Exception:
            pass
    if n_orders is None:
        lines.append(f"  • {acc}: không có plan hôm nay")
        continue
    if n_orders == 0:
        lines.append(f"  • {acc}: HOLD — không có lệnh nào hôm nay (đúng kế hoạch)")
        continue
    jpath = os.path.join("data", "execution_logs", f"exec_{acc}_{today}_journal.csv")
    done = set()
    if os.path.exists(jpath):
        with open(jpath, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("event") == "DONE":
                    done.add(row.get("parent_id"))
    lines.append(f"  • {acc}: {len(done)}/{n_orders} lệnh hoàn tất")
print("\n".join(lines))
PYEOF
)"

case "$PHASE" in
  lunch)
    MSG="🕦 **Phiên giao dịch sáng kết thúc (11:30)** — bot tạm ngưng giao dịch giờ nghỉ trưa, sẽ tự khởi động lại vào đầu phiên chiều lúc **13:00**.
Tiến độ đến giờ nghỉ:
$PROGRESS"
    ;;
  afternoon)
    MSG="🕐 **Phiên giao dịch chiều bắt đầu (13:00)** — bot đã khởi động lại, tiếp tục xử lý các lệnh còn dang dở trong kế hoạch hôm nay.
Tiến độ hiện tại:
$PROGRESS"
    ;;
  close)
    MSG="🔔 **Phiên giao dịch kết thúc** — đợt khớp lệnh định kỳ đóng cửa (ATC) vừa hoàn tất lúc ~14:45; lệnh nào còn treo bot sẽ tự hủy và dừng trong ít phút tới.
Tiến độ cuối ngày:
$PROGRESS
📊 Báo cáo tổng kết chi tiết (lệnh khớp, NAV) sẽ gửi vào topic **Trading report** lúc **15:00**."
    ;;
  *)
    echo "Unknown phase: $PHASE" >&2; exit 1 ;;
esac

echo "$MSG"
"$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_DAILY_THREAD" 2>/dev/null || true
