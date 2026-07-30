#!/usr/bin/env bash
# ops_health_check.sh --label "Trước phiên sáng" | "Trước phiên chiều"
#
# Kiểm tra sức khỏe vận hành tổng quát (không riêng 1 account) trước mỗi phiên giao dịch,
# đúc kết từ các sự cố THẬT phát hiện 2026-07-06 (xem kb/incidents/2026-07/, các file 2026-07-06-*):
#   1. Xung đột file plan (vd v1/v2 cùng ngày, chỉ 1 bản được executor đọc thật)
#   2. Vòng lặp lỗi bất thường trong journal (vd retry T+2 hàng ngàn lần)
#   3. Circuit breaker / job board bất thường
#   4. Câu hỏi (event_type=question) đang chờ user chưa trả lời — 2 dòng: trong 48h (có
#      dispatch autofix) và TREO LÂU >48h (WARN-only, không dispatch — chỉ user quyết được)
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
                     f"xem kb/incidents/2026-07/, các file 2026-07-06-*) — sẽ tự giảm sau khi bot dùng code mới (fix "
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

# 4b. Job board: bản ghi kẹt status=running vì tiến trình dispatch chết giữa chừng
# (sự cố 2026-07-19: Wags_20260719_173512 kẹt 'running' 2 ngày, không ai phát hiện vì
# job board đã đầy zombie cũ). Chỉ ĐỌC ở đây (--dry-run) — dọn thật bằng `bin/jobs.sh reap`.
# KHÔNG fail-OPEN: detector hỏng (sai path/python lỗi/timeout) phải KÊU, không được nuốt
# exception rồi in ✅ — đúng failure mode mà check này sinh ra để chặn (arch-reviewer
# NEEDS_CHANGES coord-2026-07-22).
_reap_out, _reap_err = [], ""
try:
    _p = subprocess.run(
        ["python3", os.path.join(wc_root, "mike", "bin", "mike_json.py"),
         "job-reap", os.path.join(wc_root, "mike", "bus", "jobs"), "3600", "--dry-run"],
        capture_output=True, text=True, timeout=60)
    if _p.returncode != 0 or _p.stderr.strip():
        _reap_err = (_p.stderr.strip() or f"exit={_p.returncode}")[:200]
    else:
        _reap_out = _p.stdout.splitlines()
except Exception as e:
    _reap_err = f"{type(e).__name__}: {e}"[:200]

if _reap_err:
    W(f"Job board: KHÔNG kiểm tra được (job-reap --dry-run lỗi: {_reap_err}) — không kết "
      f"luận được board sạch; chạy tay `bin/jobs.sh reap --dry-run` để xem.")
else:
    orphan_ids = [l.split()[1] for l in _reap_out if l.startswith("orphaned ")]
    if orphan_ids:
        W(f"Job board: {len(orphan_ids)} job kẹt status=running dù tiến trình đã chết (mới nhất: "
          f"{orphan_ids[0]}) — chạy `bin/jobs.sh reap` để đóng. Job MỚI xuất hiện ở đây nghĩa là "
          f"caller chết trước khi ghi kết quả → dùng bin/trace.sh xem việc có thực sự xong không.")
    else:
        OK("Job board: không có bản ghi nào kẹt status=running quá hạn.")

# 5. Câu hỏi (event_type=question) chưa được trả lời trong 48h gần nhất
# 2 pass: answers gom TOÀN CỤC trước (append_event.sh ghi event vào file của TÁC GIẢ —
# bus/inbox/<agent_id>.jsonl — nên answer của agent KHÁC người hỏi nằm ở file khác;
# match trong-cùng-file như bản cũ khiến answer chéo-agent không bao giờ clear question,
# wags_autofix bị dispatch lặp cho question đã trả lời — fix Wags 2026-07-10).
import datetime as dt
_now = dt.datetime.now(dt.timezone.utc)
cutoff = _now - dt.timedelta(hours=48)
# Horizon cho backlog TREO LÂU: câu hỏi >48h mà chưa có answer/decision trước đây RƠI KHỎI
# radar hoàn toàn (check chỉ nhìn 48h) → chết im, không owner, không ai nhắc user quyết
# (đúng gap mà comment nhánh dispatch dưới đã ghi nhận nhưng chưa bịt — sự cố THẬT:
# question Winston/dt5g-live-2-writer-can-quyet 2026-07-29, cần user chọn A/B/C, sẽ vô hình
# từ 2026-07-31). 30 ngày là horizon để câu hỏi bị bỏ hẳn không nhắc mãi mãi. Dòng này
# CỐ TÌNH không dispatch autofix (xem grep COORD_WARN/OTHER_WARN): loại câu hỏi này chỉ
# user quyết được, spawn Wags lặp lại vô nghĩa — cần VISIBILITY cho người, không cần agent.
aged_horizon = _now - dt.timedelta(days=30)
# Marker ỔN ĐỊNH để nhánh dispatch dưới (bash grep) nhận ra "dòng này chỉ để NGƯỜI đọc,
# không spawn agent". Trước đây routing dựa vào CHỮ HOA/câu chữ tiếng Việt của chính dòng
# WARN ("Câu hỏi TREO LÂU" vs "câu hỏi (question)") → đổi câu chữ là routing thay đổi im
# lặng, và topic tự do nhúng trong dòng (chứa "Circuit breaker"/"Job board:") có thể kéo
# cả dòng vào COORD_WARN → dispatch Wags oan (arch-reviewer required_change #5).
WARN_ONLY = "[WARN-ONLY]"
inbox_dir = os.path.join(wc_root, "mike", "bus", "inbox")
pending_q = []
aged_q = []
expired_q = []
if os.path.isdir(inbox_dir):
    files = glob.glob(os.path.join(inbox_dir, "*.jsonl"))
    def iter_events(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    # Resolver = answer HOẶC decision — 1 quyết định thường đóng câu hỏi mà không lặp lại
    # y hệt topic (vd decision "deposit-rate-autowrite-removed"), và người trả lời hay
    # thêm hậu-tố trạng thái vào topic gốc (…-question-closed / …-confirmed / … [RESOLVED]).
    # Khớp exact-topic như bản cũ bỏ sót cả 2 dạng → false-positive backlog, Wags bị
    # dispatch lặp cho câu hỏi ĐÃ giải quyết (sự cố Wags 2026-07-21: 2/5 "pending" thực ra
    # đã đóng — Winston deposit-rate + Taylor plan-SpaceX).
    # Resolver lưu kèm ts: một answer/decision chỉ đóng được câu hỏi phát SINH TRƯỚC nó.
    # Không so ts là điểm mù VĨNH VIỄN cho các topic alert LẶP không có ngày (vd
    # send_plan_report.sh:380 phát `plan-t1-not-ready-<ACCOUNT>`): 1 lần đóng bằng hậu-tố
    # `-question-closed` sẽ pre-resolve MỌI lần alert tương lai (ZaloPay mù từ answer
    # Winston 2026-07-14, SpaceX mù từ vệ sinh coord-2026-07-30) → alert plan T+1 chưa
    # sẵn sàng của account tiền thật biến mất khỏi check #5. Fix: required_change #1 của
    # arch-reviewer, NEEDS_CHANGES coord-2026-07-30.
    resolvers = []
    for p in files:
        for rec in iter_events(p):
            if rec.get("event_type") in ("answer", "decision"):
                t = rec.get("topic")
                if not t:
                    continue
                try:
                    r_ts = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
                except Exception:
                    # Không đọc được ts → coi như rất cũ, KHÔNG cho đóng gì (fail-closed:
                    # thà báo pending thừa hơn làm mù 1 alert thật).
                    continue
                resolvers.append((t, r_ts))
    def _resolved(q_topic, q_ts):
        # Exact-match, HOẶC resolver CHỨA nguyên topic câu hỏi (quy ước hậu-tố trạng thái) —
        # và resolver phải xuất hiện SAU câu hỏi. Chỉ 1 chiều (resolver ⊇ topic-hỏi) để 1
        # decision topic-ngắn KHÔNG vô tình khớp câu hỏi dài khác chủ đề.
        if not q_topic:
            return False
        return any((r == q_topic or q_topic in r) and r_ts >= q_ts for r, r_ts in resolvers)
    for p in files:
        agent = os.path.basename(p).replace(".jsonl", "")
        for rec in iter_events(p):
            if rec.get("event_type") != "question":
                continue
            try:
                ts_dt = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
            except Exception:
                continue
            if _resolved(rec.get("topic"), ts_dt):
                continue
            if ts_dt >= cutoff:
                pending_q.append(f"{agent}/{rec.get('topic')}")
            elif ts_dt >= aged_horizon:
                age_d = (_now - ts_dt).days
                aged_q.append(f"{agent}/{rec.get('topic')} ({age_d}d)")
            else:
                expired_q.append((agent, rec.get("topic"), (_now - ts_dt).days))
if pending_q:
    W(f"Có {len(pending_q)} câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: {pending_q}")
else:
    OK("Không có câu hỏi (question) nào đang chờ xử lý trong 48h qua.")
if aged_q:
    aged_q.sort()
    W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần USER quyết: {aged_q}")
# Hết horizon 30 ngày: TRƯỚC ĐÂY câu hỏi rơi khỏi radar KHÔNG dấu vết nào (đúng "chết im"
# mà dòng aged vừa bịt, chỉ hoãn 30 ngày — arch-reviewer required_change #4). Nay phát 1
# event decision "EXPIRED" để có dấu vết bền trên bus + 1 dòng WARN-only cho người thấy.
# Idempotent: topic event CHỨA nguyên topic câu hỏi và ts SAU nó → _resolved() lần chạy
# sau tự bỏ qua (không phát lại). Không làm mù alert lặp tương lai vì _resolved() so ts.
if expired_q:
    ae = os.path.join(wc_root, "mike", "bin", "append_event.sh")
    for agent, q_topic, age_d in expired_q:
        try:
            subprocess.run([ae, "Mike", "decision",
                            f"{q_topic} — EXPIRED-30d-khong-ai-tra-loi",
                            json.dumps({"expired_after_days": age_d, "asked_by": agent,
                                        "closed_by": "ops_health_check horizon 30d",
                                        "note": "Đóng theo HẾT HẠN, không phải đã trả lời — "
                                                "mở lại bằng question mới nếu vẫn cần quyết."},
                                       ensure_ascii=False)],
                           capture_output=True, timeout=30)
        except Exception:
            pass
    W(f"{WARN_ONLY} Câu hỏi HẾT HẠN 30 ngày (đóng theo hết hạn, đã ghi decision lên bus) — "
      f"{len(expired_q)} mục: {[f'{a}/{t} ({d}d)' for a, t, d in expired_q]}")

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

# 8. Lãi suất tiết kiệm (deposit_rate_vn) freshness — WARN-only, thêm 2026-07-17 (proposal §4).
#    Input LIVE cho rating_8l NEUTRAL tilt. Mốc cuối = collected_date mới nhất trong
#    data/deposit_rate_vn_events.csv, hoặc anchor cứng cuối cùng trong deposit_rate_vn.py nếu CSV
#    chưa có dòng nào. >45 ngày -> WARN (KHÔNG BLOCK — đây là tilt nhỏ ±0.03, không money-path).
#    Không import pandas ở đây (system python3 có thể thiếu) — đọc CSV bằng csv, anchor bằng regex.
dep_csv = os.path.join(wc_root, "data", "deposit_rate_vn_events.csv")
dep_last, dep_kind = None, None
if os.path.exists(dep_csv):
    try:
        with open(dep_csv, newline="") as f:
            drows = [r for r in csv.DictReader(f) if r.get("effective_date")]
        cds = [(r.get("collected_date") or r.get("effective_date")) for r in drows]
        cds = [c for c in cds if c]
        if cds:
            dep_last = max(_date.fromisoformat(c) for c in cds)
            dep_kind = "CSV live"
    except Exception:
        pass
if dep_last is None:  # CSV rỗng/không đọc được -> mốc cuối = anchor cứng cuối trong module
    try:
        with open(os.path.join(wc_root, "deposit_rate_vn.py")) as f:
            src = f.read()
        anchor_dates = re.findall(r'\("(\d{4}-\d{2}-\d{2})"\s*,', src)
        if anchor_dates:
            dep_last = max(_date.fromisoformat(d) for d in anchor_dates)
            dep_kind = "anchor cứng (CSV rỗng)"
    except Exception:
        pass
if dep_last is not None:
    dep_age = (today_d - dep_last).days
    if dep_age > 45:
        W(f"Lãi suất tiết kiệm (deposit_rate_vn) đã {dep_age} ngày chưa refresh "
          f"(mốc cuối {dep_last}, {dep_kind}) — input rating_8l NEUTRAL tilt sống. "
          f"Chạy refresh_deposit_rate_vn.sh (nhắc) rồi append_deposit_rate.py để cập nhật.")
    else:
        OK(f"Lãi suất tiết kiệm (deposit_rate_vn): mốc cuối {dep_last} ({dep_age} ngày, {dep_kind}).")
else:
    lines.append("ℹ️ deposit_rate_vn freshness: không đọc được mốc cuối (bỏ qua).")

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

# 9. Anomaly scan (thêm 2026-07-17, job Taylor_20260717_113024) — PHÂN VAI:
#    PRIMARY = tín hiệu GIÁ/KHỐI LƯỢNG tier-H (bắt DGC ĐÚNG ngày sự việc 2026-03-17;
#    trạng thái RES/diện-kiểm-soát mãi 2026-05-13 mới có → TRỄ 57 ngày lịch/~38 phiên).
#    Scan giá/volume (BQ cache, nhanh) LUÔN chạy; --status-check (DNSE, chậm/không ổn định)
#    best-effort có timeout, non-fatal. Tier-H trip MỚI → anomaly_escalate.py tự post
#    Trading Daily + dispatch Wendy(pháp lý)+Spyros(rủi ro) KHỞI ĐỘNG due-diligence —
#    KHÔNG tự mua/bán (quyết định cuối chờ user/Mike). Idempotent qua ledger
#    data/anomaly_escalations.json → 08:20 + 12:45 không escalate trùng cùng 1 trip.
#    Chỉ chạy trên lượt ACCOUNT đầu (universe fleet-wide, không per-account — tránh loop
#    for_each_live_account gọi trùng; SpaceX là account mặc định/đầu tiên).
ANOMALY_SUMMARY=""
ANOMALY_WARN=0
ANOMALY_SCAN="$WC_ROOT/mike/agents/Taylor/anomaly_scan.py"
if [ "$ACCOUNT" = "SpaceX" ] && [ -f "$ANOMALY_SCAN" ]; then
  EMIT="/tmp/anomaly_emit_${TODAY}.json"
  timeout 200 python3 "$ANOMALY_SCAN" --status-check --emit-json "$EMIT" >/dev/null 2>&1 \
    || timeout 90 python3 "$ANOMALY_SCAN" --emit-json "$EMIT" >/dev/null 2>&1 || true
  if [ -f "$EMIT" ]; then
    ESC_OUT="$(python3 "$WC_ROOT/mike/bin/anomaly_escalate.py" --emit-json "$EMIT" 2>&1 || true)"
    if echo "$ESC_OUT" | grep -q "tier-H MỚI"; then
      ANOMALY_WARN=1
      ANOMALY_SUMMARY="🚨 Anomaly (giá/khối lượng): $(echo "$ESC_OUT" | grep 'tier-H MỚI') — ĐÃ khởi động due-diligence (Wendy+Spyros), chi tiết ở alert riêng phía trên. KHÔNG tự mua/bán, chờ user/Mike duyệt."
    elif echo "$ESC_OUT" | grep -q "trạng thái sàn"; then
      ANOMALY_SUMMARY="📋 Anomaly: $(echo "$ESC_OUT" | grep 'trạng thái sàn') — nhãn theo dõi thực thi (không phải cảnh báo sớm)."
    else
      ANOMALY_SUMMARY="✅ Anomaly scan (giá/khối lượng + trạng thái sàn): không có tín hiệu tier-H mới."
    fi
  else
    ANOMALY_SUMMARY="ℹ️ Anomaly scan: không tạo được emit (BQ cache/DNSE tạm lỗi) — bỏ qua lượt này, tự chạy lại sau."
  fi
fi
WARN_COUNT=$(( ${WARN_COUNT:-0} + ${ANOMALY_WARN:-0} ))

MSG="🩺 **${ACCOUNT} — ${LABEL} — kiểm tra vận hành ${NOW_ICT}**
${REPORT_BODY}"
if [ -n "$PREFLIGHT_TAIL" ]; then
  MSG="${MSG}

Đối chiếu preflight (macro/BQ/approval):
${PREFLIGHT_TAIL}"
fi
if [ -n "$ANOMALY_SUMMARY" ]; then
  MSG="${MSG}

Quét bất thường (anomaly scan — cảnh báo sớm giá/khối lượng + theo dõi trạng thái sàn):
${ANOMALY_SUMMARY}"
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
  # Circuit breaker + question tồn đọng = lỗi ĐIỀU PHỐI → wags_autofix (Wags triage + re-escalate
  # lên Mike). GIỮ nhánh dispatch question ở đây có chủ đích: đây là kênh escalate CHỦ ĐỘNG duy
  # nhất cho question fleet-wide — bỏ nó thì question chết im sau cutoff 48h, không owner
  # (arch-reviewer NEEDS_CHANGES coord-2026-07-20: blast_radius/long_term_ops fail). Loop chỉ
  # ~2 job/ngày (bounded, không phải bão). Harm THẬT đã sửa ở tầng matching (_resolved() check
  # #5): false-positive — question ĐÃ đóng bằng answer/decision hậu-tố '-closed'/'-confirmed'
  # trước đây báo pending vĩnh viễn nên spawn Wags vô nghĩa — nay tự dọn, không cần chạm dispatch.
  # "Job board:" cũng là FLEET-WIDE (đọc bus/jobs toàn cục) → phải nằm ở COORD_WARN, nếu
  # không nó rơi vào OTHER_WARN → ops_autofix label per-account, chạy lặp theo số account
  # cho một tình trạng toàn cục (arch-reviewer NEEDS_CHANGES coord-2026-07-22).
  # Dòng mang marker "[WARN-ONLY]" bị loại khỏi CẢ HAI nhánh có chủ đích: chỉ user quyết được
  # (vd question TREO LÂU >48h A/B/C liên quan team ngoài), Wags/Winston không resolve được →
  # dispatch lặp 2 job/ngày là token thuần lãng phí. Dòng đó chỉ cần NẰM TRONG báo cáo Trading
  # Daily để user thấy (thêm Wags 2026-07-30, coord-2026-07-30). Lọc bằng MARKER chứ không bằng
  # câu chữ tiếng Việt: đổi wording WARN không còn âm thầm đổi routing, và topic tự do nhúng
  # trong dòng không kéo được dòng đó vào COORD_WARN (arch-reviewer required_change #5).
  ROUTABLE_WARN="$(echo "$MSG" | grep -E '⚠️|❌' | grep -vF '[WARN-ONLY]' || true)"
  COORD_WARN="$(echo "$ROUTABLE_WARN" | grep -E "Circuit breaker|câu hỏi \(question\)|Job board:" || true)"
  OTHER_WARN="$(echo "$ROUTABLE_WARN" | grep -vE "NOT_APPROVED|KHÔNG TÌM THẤY|Circuit breaker|câu hỏi \(question\)|Job board:" || true)"
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
