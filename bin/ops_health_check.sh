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
#   7. [GỠ 2026-08-01] Báo cáo tuần/tháng quá hạn — chuyển sang bin/check_report_cadence.sh
#      (cron riêng 1 lần/ngày). Lý do gỡ khỏi đây: bản WARN cũ chỉ in 1 dòng, bị CHÔN trong
#      message chạy 4 lần/ngày (2 khung giờ x 2 account) — không có forcing function, kết quả
#      là WARN lặp lại ~20 lần suốt 5 ngày (07-27→08-01) mà không ai action, 2 tuần báo cáo
#      bị bỏ sót thật (kb/incidents/2026-08/2026-08-01-weekly-monthly-report-dead.md). Script
#      mới tự dispatch Taylor soạn+gửi khi quá hạn (không chỉ cảnh báo) + post riêng vào
#      Trading report topic (không chôn ở Trading Daily) + bus event question.
#
# Đây là lớp CẢNH BÁO SỚM bổ sung, KHÔNG thay thế preflight_check.sh (08:45) hay
# eod_trading_report.sh (15:00) — chạy TRƯỚC mỗi phiên để con người có thời gian phản ứng.
# Post tóm tắt vào Trading Daily (vận hành sống trong ngày), không phải Trading report
# (báo cáo tổng hợp) — đúng phân tách 2026-07-03.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
TRADING_DAILY_THREAD="trading_daily"

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
import glob, gzip, json, os, re, sys, subprocess, csv
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
# Sibling: bin/bus_question_audit.py port lại ĐÚNG thuật toán match dưới đây cho báo cáo
# TUẦN (kb_nightly.sh Phase 5, việc 11, thêm 2026-07-31) — đầy đủ không cắt AGED_SHOWN.
# Sửa thuật toán match ở đây (resolvers/_resolved) → sửa luôn bên đó, đừng để 2 bản lệch.
# 2 pass: answers gom TOÀN CỤC trước (append_event.sh ghi event vào file của TÁC GIẢ —
# bus/inbox/<agent_id>.jsonl — nên answer của agent KHÁC người hỏi nằm ở file khác;
# match trong-cùng-file như bản cũ khiến answer chéo-agent không bao giờ clear question,
# wags_autofix bị dispatch lặp cho question đã trả lời — fix Wags 2026-07-10).
# CHECK5_BEGIN — marker ỔN ĐỊNH: bin/ops_health_check_selfcheck.py trích ĐÚNG khối giữa
# CHECK5_BEGIN/CHECK5_END rồi chạy nó trên bus giả để khoá hồi quy (kb_nightly Phase 0).
# Đổi/xoá 2 marker này → selfcheck FAIL ngay, không im lặng. Khối chỉ được phép dùng:
# glob/gzip/json/os/re + biến wc_root + hàm W()/OK() (selfcheck cung cấp đúng bấy nhiêu).
import datetime as dt
_now = dt.datetime.now(dt.timezone.utc)
cutoff = _now - dt.timedelta(hours=48)
# Backlog TREO LÂU: câu hỏi >48h mà chưa có answer/decision trước đây RƠI KHỎI radar hoàn
# toàn (check chỉ nhìn 48h) → chết im, không owner, không ai nhắc user quyết (đúng gap mà
# comment nhánh dispatch dưới đã ghi nhận nhưng chưa bịt — sự cố THẬT: question
# Winston/dt5g-live-2-writer-can-quyet 2026-07-29, cần user chọn A/B/C, sẽ vô hình từ
# 2026-07-31). Dòng này CỐ TÌNH không dispatch autofix (xem grep COORD_WARN/OTHER_WARN):
# loại câu hỏi này chỉ user quyết được, spawn Wags lặp lại vô nghĩa — cần VISIBILITY cho
# người, không cần agent.
# KHÔNG cắt theo thời gian — câu hỏi treo mãi thì hiện mãi, chỉ cắt theo ĐỘ DÀI dòng in.
# LƯU Ý: "hiện mãi" chỉ đúng vì vòng lặp dưới quét CẢ bus/inbox/archive/*.jsonl.gz. Bản
# 2026-07-31 (round-3) tưởng đã gỡ hết horizon nhưng chỉ gỡ ở checker — horizon 30d THẬT
# nằm ở kb_nightly Phase 1b2 (archive) và vẫn cắt im lặng cho tới khi archive được đọc.
# Bản 2026-07-30 từng auto-close sau horizon 30 ngày (phát 1 `decision` "EXPIRED-30d" dưới
# agent_id=Mike). arch-reviewer NEEDS_CHANGES (high, round-2 coord-2026-07-30) bác: cơ chế
# đó DỰNG LẠI đúng lỗi nó định bịt — check #5 là kênh backlog DUY NHẤT của fleet (đã grep
# hết consolidate/daily_retro/kb_nightly/staleness_watch), nên sau EXPIRED question biến
# mất khỏi MỌI dòng báo cáo, chỉ hoãn chết-im từ 48h thành 30d; lại để MÁY viết `decision`
# nhân danh người trên escalation tiền thật (DGC ZaloPay 46,8% NAV) và ô nhiễm KB
# (kb_nightly giữ decision vĩnh viễn), qua một đường ghi bus nuốt lỗi im lặng.
# Chính sách IN (round-5, arch-reviewer required_change #1, NEEDS_CHANGES coord-2026-07-31):
# pool aged KHÔNG BAO GIỜ tự cạn — chỉ answer/decision của NGƯỜI mới đóng, drain rate thực
# nghiệm = 0 (2 câu hỏi 38d/34d không ai đụng suốt hơn 1 tháng). Bản cũ in 5 mục CŨ NHẤT
# nên chỉ cần thêm 2 zombie già hơn là escalation tiền thật MỚI (Taylor/DGC ZaloPay 46,8%
# NAV, 7d) bị chèn vào "…và N mục khác" = đổi cliff-30d-im-lặng lấy crowd-out-im-lặng.
# Fix: in ĐỦ khi pool còn nhỏ; khi buộc phải cắt thì cắt GIỮA, giữ CẢ đầu (treo lâu nhất)
# LẪN đuôi (mới nhất — thường là cái đang khẩn) trong tầm mắt.
AGED_SHOW_ALL_UPTO = 10   # ≤10 mục: in HẾT, không cắt
AGED_OLDEST = 5           # >10 mục: 5 mục cũ nhất …
AGED_NEWEST = 3           # … + 3 mục mới nhất
# Marker ỔN ĐỊNH để nhánh dispatch dưới (bash grep) nhận ra "dòng này chỉ để NGƯỜI đọc,
# không spawn agent". Trước đây routing dựa vào CHỮ HOA/câu chữ tiếng Việt của chính dòng
# WARN ("Câu hỏi TREO LÂU" vs "câu hỏi (question)") → đổi câu chữ là routing thay đổi im
# lặng, và topic tự do nhúng trong dòng (chứa "Circuit breaker"/"Job board:") có thể kéo
# cả dòng vào COORD_WARN → dispatch Wags oan (arch-reviewer required_change #5).
WARN_ONLY = "[WARN-ONLY]"
inbox_dir = os.path.join(wc_root, "mike", "bus", "inbox")
pending_q = []
pending_q_wagsfix = []   # xem chú thích ở khối "if pending_q_wagsfix" phía dưới
aged_q = []
if os.path.isdir(inbox_dir):
    # PHẢI quét CẢ archive: kb_nightly Phase 1b2 (EVENT_KEEP_DAYS=30) chuyển MỌI event cũ
    # hơn 30 ngày khỏi bus/inbox/*.jsonl sang bus/inbox/archive/<id>_<YYYY-MM>.jsonl.gz,
    # KHÔNG lọc theo event_type. Glob chỉ hot inbox = cliff 30 ngày IM LẶNG: câu hỏi chưa
    # ai trả lời tự biến mất khỏi kênh backlog duy nhất của fleet, không WARN, không dấu
    # vết (đã xảy ra THẬT 2 lần: Wendy/confirm-dnse-phs-margin-thresholds 2026-06-22 và
    # Taylor/cache-stability go-live blocker 2026-06-27 — cả hai CHƯA TỪNG được trả lời).
    # Quét cả 2 pass (question + resolver) trên cùng tập file, giữ matcher ở MỘT nơi
    # (arch-reviewer required_change #1/#2, NEEDS_CHANGES coord-2026-07-31). Chi phí không
    # đáng kể: toàn bộ archive ~778 event / 252KB nén.
    archive_dir = os.path.join(inbox_dir, "archive")
    archive_files = sorted(glob.glob(os.path.join(archive_dir, "*.jsonl.gz")))
    files = sorted(glob.glob(os.path.join(inbox_dir, "*.jsonl"))) + archive_files
    # Nếu kb_nightly Phase 1b2 đổi đường dẫn/đuôi file archive, glob dưới khớp 0 file và
    # check lặng lẽ quay về ĐÚNG cliff 30d cũ (chính lỗi round-3 mắc: sửa checker trong
    # khi horizon nằm chỗ khác). Thư mục tồn tại mà rỗng = tín hiệu đó → phải nói ra.
    if os.path.isdir(archive_dir) and not archive_files:
        W(f"bus/inbox/archive tồn tại nhưng KHÔNG khớp file *.jsonl.gz nào — backlog "
          f"câu hỏi (question) có thể THIẾU phần >30 ngày. Kiểm tra kb_nightly Phase 1b2 "
          f"(EVENT_KEEP_DAYS/đường dẫn archive) có đổi layout không.")
    # Đường lỗi ĐỌC phải đếm được, không nuốt: gz cắt cụt/hỏng từng làm 1 câu hỏi biến mất
    # hoàn toàn mà không một dòng cảnh báo nào (arch-reviewer required_change #2, tái hiện
    # được trên bản copy). Set theo path vì mỗi file được đọc 2 lần (pass resolver + pass
    # question) — không muốn đếm đôi.
    read_errors = {}
    def iter_events(path):
        opener = (lambda p: gzip.open(p, "rt", encoding="utf-8")) if path.endswith(".gz") \
                 else (lambda p: open(p, encoding="utf-8"))
        try:
            with opener(path) as f:
                for line in f:
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue
        except Exception as e:
            # File archive hỏng/đang ghi dở → bỏ qua file đó, KHÔNG làm chết cả check,
            # nhưng GHI LẠI để WARN bên dưới (im lặng ở đây = đúng lớp bug đang sửa).
            read_errors[os.path.basename(path)] = type(e).__name__
            return
    def _agent_of(path):
        # "Wendy.jsonl" → Wendy; "Wendy_2026-06.jsonl.gz" → Wendy (bỏ hậu tố tháng).
        name = os.path.basename(path).replace(".jsonl.gz", "").replace(".jsonl", "")
        return re.sub(r"_\d{4}-\d{2}$", "", name)
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
    seen_q = set()
    for p in files:
        agent = _agent_of(p)
        for rec in iter_events(p):
            if rec.get("event_type") != "question":
                continue
            try:
                ts_dt = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
            except Exception:
                continue
            if _resolved(rec.get("topic"), ts_dt):
                continue
            # Chống đếm đôi nếu 1 event vừa còn ở hot inbox vừa đã sang archive (kb_nightly
            # bị kill giữa chừng): khoá theo (agent, topic, ts).
            key = (agent, rec.get("topic"), rec.get("ts"))
            if key in seen_q:
                continue
            seen_q.add(key)
            if ts_dt >= cutoff:
                # wags-fix-not-confirmed:* là câu hỏi TỰ chính pipeline wags_autofix sinh ra khi
                # arch-reviewer verdict != CONFIRMED (xem bin/wags_autofix.sh). Đưa nó vào
                # pending_q (routable) như mọi câu hỏi khác từng khiến COORD_WARN dispatch LẠI
                # wags_autofix cho ĐÚNG issue vừa NEEDS_CHANGES — vòng phản hồi dương tự nuôi
                # (audit §14 kiến trúc fleet 2026-07-31, Fable plan + Opus critique: "output
                # của vòng lặp là input của vòng kế tiếp"). Comment thiết kế gốc của
                # wags_autofix.sh đã NÓI RÕ ý định "không tự ép vòng 2 vô hạn — con người quyết"
                # nhưng nhánh dispatch ở dưới (COORD_WARN) không tôn trọng ý định đó cho đúng
                # loại câu hỏi này. Tách riêng + gắn WARN_ONLY: vẫn hiện trong báo cáo cho
                # người thấy, KHÔNG tự re-trigger — người/Mike quyết vòng kế tiếp tường minh.
                if str(rec.get("topic") or "").startswith("wags-fix-not-confirmed:"):
                    pending_q_wagsfix.append(f"{agent}/{rec.get('topic')}")
                else:
                    pending_q.append(f"{agent}/{rec.get('topic')}")
            else:
                age_d = (_now - ts_dt).days
                aged_q.append((age_d, f"{agent}/{rec.get('topic')} ({age_d}d)"))
    if read_errors:
        # KHÔNG gắn [WARN-ONLY]: đây là lỗi TOOLING sửa được (khác với backlog chờ user).
        # Câu chữ cố ý chứa "câu hỏi (question)" để nhánh routing dưới đưa về COORD_WARN
        # → wags_autofix (Wags), không rơi vào OTHER_WARN → ops_autofix per-account.
        W(f"{len(read_errors)} file bus KHÔNG ĐỌC ĐƯỢC — backlog câu hỏi (question) có thể "
          f"THIẾU (bỏ sót toàn bộ event trong các file này): "
          f"{ {k: v for k, v in sorted(read_errors.items())} }")
if pending_q:
    W(f"Có {len(pending_q)} câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: {pending_q}")
elif not pending_q_wagsfix:
    OK("Không có câu hỏi (question) nào đang chờ xử lý trong 48h qua.")
if pending_q_wagsfix:
    W(f"{WARN_ONLY} {len(pending_q_wagsfix)} vòng wags-fix CHƯA CONFIRMED trong 48h qua — KHÔNG tự "
      f"re-trigger (đã qua ít nhất 1 vòng fix+arch-review, lặp tự động là vòng lặp tự nuôi vô "
      f"nghĩa — người/Mike quyết vòng kế tiếp tường minh, hoặc chờ cooldown hôm sau tự thử lại): "
      f"{pending_q_wagsfix}")
if aged_q:
    aged_q.sort(key=lambda x: -x[0])   # cũ nhất trước
    if len(aged_q) <= AGED_SHOW_ALL_UPTO:
        shown = [lbl for _, lbl in aged_q]
        W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần "
          f"USER quyết (in đủ): {shown}")
    else:
        # Cắt GIỮA: giữ cả mục treo lâu nhất LẪN mục mới nhất — zombie cũ không được phép
        # chèn escalation mới ra khỏi màn hình (xem chú thích AGED_SHOW_ALL_UPTO ở trên).
        # Cắt trên phần CÒN LẠI (không dùng aged_q[-N:]) — với N=0 thì aged_q[-0:] trả về
        # NGUYÊN danh sách, in trùng toàn bộ. Bẫy này bị mutation-test bắt được.
        oldest = [lbl for _, lbl in aged_q[:AGED_OLDEST]]
        rest = aged_q[AGED_OLDEST:]
        newest = [lbl for _, lbl in (rest[-AGED_NEWEST:] if AGED_NEWEST > 0 else [])]
        more = len(rest) - len(newest)
        W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần "
          f"USER quyết; {len(oldest)} cũ nhất: {oldest} …và {more} mục giữa… "
          f"{len(newest)} mới nhất: {newest}. Danh sách ĐẦY ĐỦ: bin/bus_question_audit.py")
# CHECK5_END

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

# 7. [GỠ 2026-08-01] Báo cáo tuần/tháng quá hạn — xem bin/check_report_cadence.sh (cron riêng).
#    today_d/_date/_timedelta vẫn cần cho mục 8 + phần retro bên dưới, giữ lại định nghĩa.
from datetime import date as _date, timedelta as _timedelta
today_d = _date.fromisoformat(today)

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

# 9. daily_retro.sh freshness (thêm 2026-08-01, sau sự cố script crash âm thầm 2 đêm liền
#    07-31/08-01 do lỗi quoting — kb/incidents/2026-08/2026-08-01-daily-retro-quoting-bug-
#    silent-2day-outage.md). daily_retro.sh chạy 00:30 ICT, review NGÀY HÔM QUA (ICT) và ghi
#    kb/incidents/retro/retro-<ngày đó>.md khi xong. Checker này chạy 08:20/12:45 ICT — đủ
#    trễ để lần chạy 00:30 đêm qua chắc chắn đã xong (hoặc đã crash). Thiếu file = dấu hiệu
#    daily_retro.sh crash/không hoàn tất — chính lớp lỗi mà bản thân RETRO được dựng ra để
#    bắt, nhưng lại là nạn nhân của nó (crash trước khi kịp tự báo). WARN-only, KHÔNG tự
#    sửa ở đây — rơi vào OTHER_WARN nên tự động dispatch ops_autofix.sh (Winston chẩn đoán+sửa).
retro_yday = today_d - _timedelta(days=1)
retro_file = os.path.join(wc_root, "mike", "kb", "incidents", "retro", f"retro-{retro_yday.isoformat()}.md")
if os.path.exists(retro_file):
    OK(f"daily_retro.sh: có entry cho {retro_yday} ({os.path.basename(retro_file)}).")
else:
    W(f"daily_retro.sh KHÔNG có entry RETRO cho {retro_yday} (thiếu {os.path.relpath(retro_file, wc_root)}) "
      f"— nghi cron 00:30 ICT đêm qua crash/không hoàn tất (đúng lớp lỗi 08-01: quoting bug làm "
      f"script chết trước khi kịp notify). Kiểm logs/daily_retro.log tìm lỗi bash gần nhất.")

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
