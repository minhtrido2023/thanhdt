#!/usr/bin/env bash
# ops_health_check.sh --label "Trước phiên sáng" | "Trước phiên chiều"
#
# Kiểm tra sức khỏe vận hành tổng quát (không riêng 1 account) trước mỗi phiên giao dịch,
# đúc kết từ các sự cố THẬT phát hiện 2026-07-06 (xem kb/INCIDENTS.md):
#   1. Xung đột file plan (vd v1/v2 cùng ngày, chỉ 1 bản được executor đọc thật)
#   2. Vòng lặp lỗi bất thường trong journal (vd retry T+2 hàng ngàn lần)
#   3. Circuit breaker / job board bất thường
#   4. Câu hỏi (event_type=question) đang chờ user chưa trả lời
#   5. Kill-switch / macro freshness / BQ freshness (tái dùng preflight_check.sh)
#   6. Corp-action backlog (sự kiện tồn đọng >7 ngày chưa resolve, thêm 2026-07-10)
#   7. Báo cáo tuần/tháng quá hạn (WARN-only, thêm 2026-07-13 — bổ sung sau sự kiện tuan
#      07-06→07-10 bi bo sot toi 07-13 moi phat hien, user tu hoi):
#      - Thứ Hai: nếu file *_weekly_report_*.md mới nhất > 7 ngày → WARN
#      - Ngày ≥5 trong tháng: nếu không có *_monthly_report_*<thang-truoc>*.md → WARN
#      (Hiện chưa có file monthly nào, WARN ngay lần đầu chạy — đây là kỳ vọng, không phải bug)
#
# Đây là lớp CẢNH BÁO SỚM bổ sung, KHÔNG thay thế preflight_check.sh (08:45) hay
# eod_trading_report.sh (15:00) — chạy TRƯỚC mỗi phiên để con người có thời gian phản ứng.
# Post tóm tắt vào Trading Daily (vận hành sống trong ngày), không phải Trading report
# (báo cáo tổng hợp) — đúng phân tách 2026-07-03.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_DAILY_THREAD="1521470705563340910"

LABEL="Kiểm tra vận hành"
# --account LABEL — mặc định SpaceX để giữ nguyên hành vi cũ khi gọi không kèm cờ. Cron
# thật gọi qua for_each_live_account.sh (lặp mọi account enabled=live/dnse) — xem
# kb/account_onboarding_runbook.md.
ACCOUNT="SpaceX"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --account) ACCOUNT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date '+%Y-%m-%d %H:%M ICT')"

REPORT="$(python3 - "$WC_ROOT" "$TODAY" "$ACCOUNT" << 'PYEOF'
import glob, json, os, sys, subprocess, csv
from collections import defaultdict

wc_root, today, account = sys.argv[1:4]
lines = []
warn = 0

def W(msg):
    global warn
    warn += 1
    lines.append(f"⚠️ {msg}")

def OK(msg):
    lines.append(f"✅ {msg}")

# 1. BOT_STOP kill-switch
if os.path.exists(os.path.join(wc_root, "data", "BOT_STOP")):
    W("BOT_STOP đang BẬT — mọi giao dịch bị chặn.")
else:
    OK("BOT_STOP: CLEAR")

# 2. Xung đột file plan — mọi biến thể plan_<account>_<ngày...>*.json cho hôm nay/ngày kế tiếp
plan_dir = os.path.join(wc_root, "data", "trade_plans")
variants = defaultdict(list)
for p in glob.glob(os.path.join(plan_dir, f"plan_{account}_*.json")):
    base = os.path.basename(p)
    # nhóm theo ngày plan_date bên trong file (không theo tên file, để bắt đúng cả file đặt tên lạ)
    try:
        d = json.load(open(p, encoding="utf-8"))
        pd = d.get("plan_date")
    except Exception:
        continue
    if pd is None:
        continue
    mtime = os.path.getmtime(p)
    variants[pd].append((base, mtime, d.get("plan_version"), len(d.get("orders", []))))

canonical_name = lambda acc, date: f"plan_{acc}_{date}.json"
conflict_found = False
for pd, files in sorted(variants.items()):
    if pd < today:
        continue
    if len(files) <= 1:
        continue
    canon = canonical_name(account, pd)
    non_canon = [f for f in files if f[0] != canon and "superseded" not in f[0]]
    if not non_canon:
        continue
    canon_match = next((f for f in files if f[0] == canon), None)
    # Đã resolve nếu canonical khớp plan_version/orders với biến thể mới nhất — chỉ còn
    # dọn dẹp file thừa, KHÔNG phải nguy cơ chạy nhầm (khác sự cố gốc 07-06).
    still_risky = any(f[2:] != canon_match[2:] for f in non_canon) if canon_match else True
    if still_risky:
        conflict_found = True
        W(f"Plan {pd}: {len(files)} file khác nhau, canonical CHƯA khớp bản mới nhất "
          f"({', '.join(f[0] for f in files)}) — nguy cơ chạy nhầm plan cũ, xem lại NGAY.")
    else:
        lines.append(f"ℹ️ Plan {pd}: có file thừa đã resolve ({', '.join(f[0] for f in non_canon)}) "
                     f"— canonical '{canon}' đã khớp đúng nội dung, chỉ cần dọn dẹp khi rảnh, không khẩn.")
if not conflict_found:
    OK("Không phát hiện xung đột file plan (mỗi ngày chỉ 1 bản, hoặc bản cũ đã đánh dấu superseded).")

# 3. Journal hôm nay: tỷ lệ lỗi bất thường (loại trừ WAIT_T2_SETTLEMENT — đã là hành vi ĐÚNG từ 07-06,
#    và loại trừ PLACE_FAIL có note khớp mẫu T+2 đã biết rõ nguyên nhân — tránh báo động giả lặp lại)
jpath = os.path.join(wc_root, "data", "execution_logs", f"exec_{account}_{today}_journal.csv")
if os.path.exists(jpath):
    counts = defaultdict(int)
    place_fail_notes = defaultdict(int)
    with open(jpath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ev = row.get("event", "?")
            counts[ev] += 1
            if ev == "PLACE_FAIL":
                place_fail_notes[row.get("note", "")] += 1
    total_place_fail = counts.get("PLACE_FAIL", 0)
    t2_signature = sum(v for k, v in place_fail_notes.items() if "Trade quantity not enough" in k)
    other_place_fail = total_place_fail - t2_signature
    concerning = {k: v for k, v in counts.items()
                  if k in ("POLL_FAIL", "POSITIONS_FAIL", "GHOST_ORDER", "CANCEL_FAIL") and v > 20}
    if other_place_fail > 20:
        concerning["PLACE_FAIL (không phải T+2)"] = other_place_fail
    if concerning:
        W(f"Journal hôm nay có lỗi lặp lại bất thường: {concerning} — kiểm tra "
          f"exec_{account}_{today}_journal.csv.")
    else:
        OK("Journal hôm nay không có lỗi lặp lại bất thường ngoài các trường hợp đã biết rõ nguyên nhân.")
    if t2_signature > 20:
        lines.append(f"ℹ️ {t2_signature} lượt PLACE_FAIL 'Trade quantity not enough' (mẫu T+2 đã biết, "
                     f"xem kb/INCIDENTS.md 2026-07-06) — sẽ tự giảm sau khi bot dùng code mới (fix "
                     f"commit 2cee603, có hiệu lực từ lần restart tự nhiên tiếp theo).")
    t2_waits = counts.get("WAIT_T2_SETTLEMENT", 0)
    if t2_waits:
        lines.append(f"ℹ️ {t2_waits} lượt WAIT_T2_SETTLEMENT hôm nay (mã đang chờ qua T+2, sẽ tự bán được sau) — bình thường.")
else:
    lines.append(f"ℹ️ Chưa có journal hôm nay ({today}) — chưa tới giờ giao dịch hoặc chưa có phiên.")

# 4. Circuit breaker per-agent
circuit_dir = os.path.join(wc_root, "mike", "state", "circuit")
tripped = []
if os.path.isdir(circuit_dir):
    for p in glob.glob(os.path.join(circuit_dir, "*.json")):
        try:
            c = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if c.get("tripped_until", 0):
            tripped.append(os.path.basename(p).replace(".json", ""))
if tripped:
    W(f"Circuit breaker đang TRIPPED cho: {', '.join(tripped)} — dispatch các agent này sẽ bị chặn tạm thời.")
else:
    OK("Circuit breaker: tất cả agent bình thường (0 tripped).")

# 5. Câu hỏi (event_type=question) chưa được trả lời trong 48h gần nhất
# 2 pass: answers gom TOÀN CỤC trước (append_event.sh ghi event vào file của TÁC GIẢ —
# bus/inbox/<agent_id>.jsonl — nên answer của agent KHÁC người hỏi nằm ở file khác;
# match trong-cùng-file như bản cũ khiến answer chéo-agent không bao giờ clear question,
# wags_autofix bị dispatch lặp cho question đã trả lời — fix Wags 2026-07-10).
import datetime as dt
cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)
inbox_dir = os.path.join(wc_root, "mike", "bus", "inbox")
pending_q = []
if os.path.isdir(inbox_dir):
    files = glob.glob(os.path.join(inbox_dir, "*.jsonl"))
    def iter_events(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    answers = set()
    for p in files:
        for rec in iter_events(p):
            if rec.get("event_type") == "answer":
                answers.add(rec.get("topic"))
    for p in files:
        agent = os.path.basename(p).replace(".jsonl", "")
        for rec in iter_events(p):
            if rec.get("event_type") != "question":
                continue
            try:
                ts_dt = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
            except Exception:
                continue
            if ts_dt >= cutoff and rec.get("topic") not in answers:
                pending_q.append(f"{agent}/{rec.get('topic')}")
if pending_q:
    W(f"Có {len(pending_q)} câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: {pending_q}")
else:
    OK("Không có câu hỏi (question) nào đang chờ xử lý trong 48h qua.")

# 6. Corp-action backlog (data/corp_action_backlog.json, ghi bởi update_shares_live.py
#    --scan mỗi ngày 18:40 ICT — đọc file local, KHÔNG query BQ trực tiếp ở đây để giữ
#    check này nhẹ/nhanh). Sự cố 2026-07-10: scan trước đây chỉ lên tiếng khi có candidate
#    MỚI — DDV/EVG bị alert 2026-06-25/26 rồi im lặng 21 ngày không ai xử lý, không có gì
#    phát hiện ra cho tới khi user tự hỏi. File backlog + cảnh báo này đóng đúng gap đó.
backlog_path = os.path.join(wc_root, "data", "corp_action_backlog.json")
if os.path.exists(backlog_path):
    try:
        backlog = json.load(open(backlog_path, encoding="utf-8"))
        stale = [p for p in backlog.get("pending", [])
                 if (p.get("days_since_ex_date") or 0) > 7]
    except Exception as e:
        stale = None
        lines.append(f"ℹ️ Không đọc được corp_action_backlog.json: {e}")
    if stale is not None:
        if stale:
            stale_keys = [f"{p.get('ticker')}|{p.get('ex_date')}" for p in stale]
            W(f"{len(stale)} sự kiện corp-action đã alert >7 ngày trước, CHƯA resolve vào "
              f"shares_outstanding_live: {stale_keys} "
              f"— PE/PB các mã này có thể đang sai do OShares chưa cập nhật. Xử lý: Winston "
              f"phân loại cash/stock rồi `update_shares_live.py --ticker <mã>` hoặc `--ack-cash <mã>:<ex_date>`.")
        else:
            OK("Corp-action backlog: không có sự kiện nào tồn đọng >7 ngày.")
else:
    lines.append("ℹ️ Chưa có data/corp_action_backlog.json — update_shares_live.py --scan (18:40 ICT) chưa chạy lần nào kể từ khi thêm check này.")

# 7. Báo cáo tuần/tháng quá hạn (WARN-only, thêm 2026-07-13)
import re
from datetime import date as _date, timedelta as _timedelta

def _dates_from_fname(fname):
    """Trích tất cả YYYY-MM-DD trong tên file, trả về list date."""
    return [_date.fromisoformat(m) for m in re.findall(r'\d{4}-\d{2}-\d{2}', fname)]

reports_dir = os.path.join(wc_root, "mike", "reports")
today_d = _date.fromisoformat(today)

# --- 7a. Báo cáo tuần: chỉ kiểm tra vào thứ Hai ---
if today_d.weekday() == 0:  # Monday = 0
    weekly_files = glob.glob(os.path.join(reports_dir, "*_weekly_report_*.md"))
    weekly_max_dates = []
    for wf in weekly_files:
        dates = _dates_from_fname(os.path.basename(wf))
        if dates:
            weekly_max_dates.append(max(dates))
    most_recent_weekly = max(weekly_max_dates) if weekly_max_dates else None
    # Tuần trước: thứ Hai = today - 7, thứ Sáu = today - 3
    last_monday = today_d - _timedelta(days=7)
    last_friday = today_d - _timedelta(days=3)
    if most_recent_weekly is None or (today_d - most_recent_weekly).days > 7:
        W(f"Báo cáo tuần quá hạn — tuần {last_monday}→{last_friday} chưa có báo cáo, "
          f"Mike cần soạn (file mới nhất: {most_recent_weekly}).")
    else:
        OK(f"Báo cáo tuần: đã có (file mới nhất chứa ngày {most_recent_weekly}).")
else:
    day_name = ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"][today_d.weekday()]
    lines.append(f"ℹ️ Kiểm tra báo cáo tuần: bỏ qua (chỉ chạy thứ Hai, hôm nay {day_name}).")

# --- 7b. Báo cáo tháng: kiểm tra từ ngày 5 trong tháng ---
# Sàn go-live: live trading bắt đầu 2026-07-01 (SpaceX) — tháng nằm TRỌN trước đó
# không có dữ liệu tài khoản live nào để báo cáo, đòi báo cáo là false-positive
# (fix 2026-07-14, ops-autofix Winston: checker đòi báo cáo tháng 2026-06).
GO_LIVE_MONTH = (2026, 7)
if today_d.day >= 5:
    monthly_files = glob.glob(os.path.join(reports_dir, "*_monthly_report_*.md"))
    # Tháng trước
    if today_d.month == 1:
        last_month_year, last_month_num = today_d.year - 1, 12
    else:
        last_month_year, last_month_num = today_d.year, today_d.month - 1
    last_month_str = f"{last_month_year}-{last_month_num:02d}"
    has_last_month = any(last_month_str in os.path.basename(f) for f in monthly_files)
    if (last_month_year, last_month_num) < GO_LIVE_MONTH:
        lines.append(f"ℹ️ Kiểm tra báo cáo tháng: bỏ qua — tháng {last_month_str} "
                     f"trước go-live 2026-07, không có dữ liệu live để báo cáo.")
    elif not has_last_month:
        W(f"Báo cáo tháng quá hạn — tháng {last_month_str} chưa có báo cáo "
          f"(hôm nay ngày {today_d.day} >= 5), Mike cần soạn.")
    else:
        OK(f"Báo cáo tháng {last_month_str}: đã có.")
else:
    lines.append(f"ℹ️ Kiểm tra báo cáo tháng: bỏ qua (hôm nay ngày {today_d.day} < 5, chờ sau ngày 5).")

print("\n".join(lines))
print(f"__WARN_COUNT__={warn}")
PYEOF
)"

WARN_COUNT="$(echo "$REPORT" | grep -o '__WARN_COUNT__=[0-9]*' | cut -d= -f2)"
REPORT_BODY="$(echo "$REPORT" | grep -v '__WARN_COUNT__')"

# 6. Tái dùng preflight_check.sh cho phần macro_health/BQ freshness/plan approval hôm nay
#    (chỉ chạy khi còn plan hôm nay để tránh trùng lặp báo cáo lúc chưa có gì)
PREFLIGHT_TAIL=""
PREFLIGHT_WARN=0
if [ -f "$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${TODAY}.json" ]; then
  PREFLIGHT_TAIL="$(bash "$ROOT/bin/preflight_check.sh" --account "$ACCOUNT" 2>/dev/null | grep -E '^\s*(✅|❌|⚠️)' | sed 's/^/  /')"
  PREFLIGHT_WARN="$(echo "$PREFLIGHT_TAIL" | grep -cE '⚠️|❌')"
fi
WARN_COUNT=$(( ${WARN_COUNT:-0} + ${PREFLIGHT_WARN:-0} ))

MSG="🩺 **${ACCOUNT} — ${LABEL} — kiểm tra vận hành ${NOW_ICT}**
${REPORT_BODY}"
if [ -n "$PREFLIGHT_TAIL" ]; then
  MSG="${MSG}

Đối chiếu preflight (macro/BQ/approval):
${PREFLIGHT_TAIL}"
fi
if [ "${WARN_COUNT:-0}" -eq 0 ]; then
  MSG="${MSG}

**Kết luận: mọi khâu vận hành bình thường, không cần can thiệp.**"
else
  MSG="${MSG}

**Kết luận: có ${WARN_COUNT} điểm cần chú ý ở trên — xem chi tiết trước khi vào phiên.**"
fi

echo "$MSG"
"$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_DAILY_THREAD" 2>/dev/null || true
"$ROOT/bin/append_event.sh" Mike status "ops-health-check-${ACCOUNT}-${TODAY}" \
  "{\"account\":\"${ACCOUNT}\",\"label\":\"${LABEL}\",\"warn_count\":${WARN_COUNT:-0}}" 2>/dev/null || true

# Tự sửa thay vì chỉ cảnh báo (mandate user 2026-07-07, xem kb/ops_runbook.md) — trừ
# trường hợp DUY NHẤT plan chưa duyệt/chưa có (việc của user, autofix không tạo/duyệt
# plan được). Chia domain (mandate mở rộng 2026-07-07): lỗi ĐIỀU PHỐI giữa agent
# (circuit breaker, question tồn đọng) → Wags (wags_autofix, có arch-reviewer audit);
# lỗi vận hành trading/pipeline còn lại → Winston (ops_autofix). Cả 2 tự chống lặp 1h.
if [ "${WARN_COUNT:-0}" -gt 0 ]; then
  COORD_WARN="$(echo "$MSG" | grep -E '⚠️|❌' | grep -E "Circuit breaker|câu hỏi \(question\)" || true)"
  OTHER_WARN="$(echo "$MSG" | grep -E '⚠️|❌' | grep -vE "NOT_APPROVED|KHÔNG TÌM THẤY|Circuit breaker|câu hỏi \(question\)" || true)"
  if [ -n "$COORD_WARN" ]; then
    # Label KHÔNG kèm ACCOUNT: circuit breaker + question tồn đọng là trạng thái FLEET-WIDE
    # (đọc state/circuit/* + bus/inbox/* toàn cục, nội dung y hệt cho mọi account) — label
    # per-account làm loop for_each_live_account lách cooldown per-label của wags_autofix,
    # dispatch 2 job Wags song song sửa cùng 1 issue (sự cố 2026-07-08: coord-SpaceX +
    # coord-ZaloPay đụng độ khi cùng edit wags_autofix.sh).
    "$ROOT/bin/wags_autofix.sh" "coord-${TODAY}" "$COORD_WARN (checker run: account=${ACCOUNT})" 2>/dev/null || true
  fi
  if [ -n "$OTHER_WARN" ]; then
    "$ROOT/bin/ops_autofix.sh" "ops-health-${ACCOUNT}" "$MSG" 2>/dev/null || true
  fi
fi
