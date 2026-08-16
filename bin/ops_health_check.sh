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
    last_ts = {}          # event -> ts cuối cùng gặp
    last_success_ts = ""  # ts cuối của 1 lệnh đi ra/khớp THÀNH CÔNG
    with open(jpath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ev = row.get("event", "?")
            ts = row.get("ts", "") or ""
            counts[ev] += 1
            if ts:
                last_ts[ev] = max(last_ts.get(ev, ""), ts)
                if ev in ("PLACE", "FILL", "DONE"):
                    last_success_ts = max(last_success_ts, ts)
            if ev == "PLACE_FAIL":
                place_fail_notes[row.get("note", "")] += 1
    total_place_fail = counts.get("PLACE_FAIL", 0)
    t2_signature = sum(v for k, v in place_fail_notes.items() if "Trade quantity not enough" in k)
    other_place_fail = total_place_fail - t2_signature
    concerning = {k: v for k, v in counts.items()
                  if k in ("POLL_FAIL", "POSITIONS_FAIL", "GHOST_ORDER", "CANCEL_FAIL") and v > 20}
    if other_place_fail > 20:
        concerning["PLACE_FAIL (không phải T+2)"] = other_place_fail
    # Đếm CẢ NGÀY thì 1 sự cố đã sửa xong vẫn kêu tới hết phiên (ca thật ZaloPay 2026-08-10:
    # 944 PLACE_FAIL dứt hẳn 10:32, restart 10:35 → 8/8 lệnh bán khớp, checker 12:45 vẫn báo ⚠️).
    # Có PLACE/FILL/DONE thành công SAU lần lỗi cuối = bằng chứng đã phục hồi thật → hạ xuống ℹ️.
    resolved = {}
    for k in list(concerning):
        ev_key = "PLACE_FAIL" if k.startswith("PLACE_FAIL") else k
        lt = last_ts.get(ev_key, "")
        if lt and last_success_ts > lt:
            resolved[k] = (concerning.pop(k), lt)
    if concerning:
        W(f"Journal hôm nay có lỗi lặp lại bất thường: {concerning} — kiểm tra "
          f"exec_{account}_{today}_journal.csv.")
    else:
        OK("Journal hôm nay không có lỗi lặp lại bất thường ngoài các trường hợp đã biết rõ nguyên nhân.")
    for k, (n, lt) in resolved.items():
        lines.append(f"ℹ️ {n} lượt {k} hôm nay nhưng ĐÃ DỨT — lần cuối {lt[11:19]}, sau đó có "
                     f"PLACE/FILL thành công lúc {last_success_ts[11:19]} (đã phục hồi, không cần xử lý).")
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
# glob/gzip/json/os/re + biến wc_root + hàm W()/OK() (selfcheck cung cấp đúng bấy nhiêu)
# — MỌI thứ ngoài danh sách đó khối PHẢI tự import TẠI ĐÂY, không dựa vào import ở đầu
# heredoc (nằm NGOÀI marker, selfcheck không trích). Sự cố 2026-08-07: commit f0946444
# dùng defaultdict mà chỉ có import ở dòng 48 → production vẫn chạy, nhưng selfcheck
# (và qua đó cả paper_checkpoint_escalation_selfcheck) NameError → gác hồi quy chết im.
import datetime as dt
from collections import defaultdict
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
# MIỄN CẮT cho lớp WAGS_SELF_Q_PREFIXES (vòng fix+arch-review chưa CONFIRMED). Lý do: lớp
# này KHÔNG bao giờ tự đóng — nó đã bị loại khỏi auto-dispatch (pending_q_wagsfix, đúng: lặp
# tự động là vòng tự nuôi), nên dòng báo cáo này là kênh DUY NHẤT đưa nó tới người; mà nó lại
# lão hoá theo NGÀY, tức càng treo lâu càng trôi về giữa danh sách = đúng chỗ bị cắt. Kết
# cục: cơ chế duy nhất để thoát bị chính cơ chế báo cáo giấu đi.
# ⚠️ Trạng thái thực tế khi thêm (2026-08-14): nhánh cắt giữa CHƯA TỪNG chạy trong
# production (grep "mục giữa" logs/ops_health.log = 0; max từng thấy 9 mục ≤ 10) — 4 mục
# wags-fix-not-confirmed treo lâu hôm nay ĐỀU đã được in đủ, cắt-giữa KHÔNG phải nguyên nhân
# chúng bị bỏ quên. Đây là bịt lỗ TRƯỚC KHI nó cắn, và nó sắp cắn: 20 câu hỏi đang pending,
# 12 trong số đó (10 selfcheck-red + 2 wags-*) qua mốc 48h trong vòng 1 ngày ⇒ aged_q vượt 10.
# Cắt GIỮA vẫn giữ nguyên cho mọi loại câu hỏi khác.
# Trần cứng để chính lớp miễn trừ không thành đường crowd-out mới (nếu vượt: nói RÕ đã cắt
# bao nhiêu — không bao giờ cắt im lặng).
AGED_WAGS_MAX = 20
# Marker ỔN ĐỊNH để nhánh dispatch dưới (bash grep) nhận ra "dòng này chỉ để NGƯỜI đọc,
# không spawn agent". Trước đây routing dựa vào CHỮ HOA/câu chữ tiếng Việt của chính dòng
# WARN ("Câu hỏi TREO LÂU" vs "câu hỏi (question)") → đổi câu chữ là routing thay đổi im
# lặng, và topic tự do nhúng trong dòng (chứa "Circuit breaker"/"Job board:") có thể kéo
# cả dòng vào COORD_WARN → dispatch Wags oan (arch-reviewer required_change #5).
WARN_ONLY = "[WARN-ONLY]"
# ACK "đã triage, chờ NGƯỜI" (Wags coord-2026-08-03). Vấn đề: một câu hỏi <48h mà Wags đã
# triage và kết luận "THẬT — cần user/thời gian quyết, KHÔNG có fix tooling nào" vẫn nằm
# trong pending_q → COORD_WARN → dispatch wags_autofix LẠI, 2 lần/ngày, cho tới khi câu hỏi
# quá 48h mới rơi vào nhánh aged_q (vốn đã WARN_ONLY vì ĐÚNG lý do này). Ca thật: run
# 2026-08-03T01:20 triage 4 câu hỏi, kết luận Mike/retro-pattern-recurring-silent-cron-spof-2
# + Winston/ops-autofix-unresolved:run-bot-fail-ZaloPay-2026-08-03 đều cần NGƯỜI; Mike weekly
# editorial 02:38 xác nhận lại y hệt; 05:45 checker vẫn đốt thêm 1 job Wags cho đúng 2 câu đó.
# Cơ chế: agent ghi 1 event `status` topic "triaged-needs-human: <topic câu hỏi gốc>". Nó
# CHỈ tắt auto-dispatch, KHÔNG đóng câu hỏi (không đụng resolvers/_resolved), KHÔNG giấu khỏi
# báo cáo — chỉ chuyển dòng WARN sang [WARN-ONLY] để người vẫn thấy. Fail-closed: không có ack
# → hành vi y hệt trước. Không cần hạn dùng: quá 48h câu hỏi tự sang aged_q (cũng WARN_ONLY).
# Bổ sung 2026-08-11 (Wags coord-2026-08-11) — ack CÓ CỬA SỔ cho topic TÁI PHÁT:
# ack mặc định chỉ ăn cho ĐÚNG instance câu hỏi đã có lúc triage (a_ts >= q_ts). Với topic do
# CRON tự sinh lại y nguyên mỗi đêm (ca thật: Mike/context-bloat-same-day — kb_nightly Phase
# 4.6 phát lại 08-01, 08-05, 08-10 cho CÙNG một quyết định người chưa trả lời; Wags đã triage
# 08-06 kết luận "cần user chọn A/B"), mỗi lần phát lại sinh 1 câu hỏi ts MỚI hơn ack ⇒ ack
# hết tác dụng ⇒ đốt thêm 1 job wags_autofix để kết luận lại y hệt. Ack có thể khai
# `"suppress_days": N` trong payload để phủ CẢ các lần phát lại CÙNG TOPIC trong N ngày.
# Ràng buộc giữ nguyên tinh thần cũ: (a) chỉ tắt auto-dispatch, câu hỏi VẪN in [WARN-ONLY];
# (b) fail-closed — payload không đọc được / N không phải số / N<=0 ⇒ cửa sổ 0 = hành vi cũ;
# (c) cắt trần ACK_MAX_SUPPRESS_DAYS để không có ack nào tắt dispatch vĩnh viễn.
ACK_PREFIX = "triaged-needs-human:"
ACK_MAX_SUPPRESS_DAYS = 14
# Mọi tiền tố question do CHÍNH pipeline wags_autofix sinh ra ở CUỐI một vòng fix+arch-review
# (xem bin/wags_autofix.sh bước 3). Tất cả đều là OUTPUT của vòng lặp; đưa lại vào INPUT
# (pending_q → COORD_WARN → dispatch wags_autofix) là vòng phản hồi dương tự nuôi.
# ⚠️ THÊM 2026-08-12 — "wags-arch-review-inconclusive:" thiếu ở đây là REGRESSION THẬT, không
# phải phòng xa: nhánh đó được TÁCH RA khỏi "wags-fix-not-confirmed:" hôm 08-11 (commit
# 35625a6f) nhưng danh sách miễn trừ này không được cập nhật theo ⇒ question
# "wags-arch-review-inconclusive: coord-2026-08-11" (08-11T05:57:50Z) rơi vào pending_q, kéo
# COORD_WARN dispatch coord-2026-08-12 (logs/wags_pipeline_20260812_012009.log), job đó CŨNG
# INCONCLUSIVE và đẻ tiếp question coord-2026-08-12 — đúng vòng lặp audit §14 (2026-07-31) đã
# đóng cho tiền tố cũ.
# ⇒ LUẬT: thêm bất kỳ nhánh `append_event.sh Wags question` MỚI nào vào wags_autofix.sh thì
# PHẢI thêm tiền tố đó vào tuple này CÙNG LÚC (và pin bằng selfcheck ca 10/11).
WAGS_SELF_Q_PREFIXES = ("wags-fix-not-confirmed:", "wags-arch-review-inconclusive:")
inbox_dir = os.path.join(wc_root, "mike", "bus", "inbox")
pending_q = []
pending_q_wagsfix = []   # xem chú thích ở khối "if pending_q_wagsfix" phía dưới
# Câu hỏi ĐÃ được triage và kết luận "chỉ NGƯỜI quyết được, không có fix tooling" →
# vẫn HIỆN đầy đủ trong báo cáo nhưng KHÔNG spawn wags_autofix nữa (xem ACK_PREFIX).
pending_q_needs_human = []
pending_q_meta = []      # (agent, topic, ts) song song pending_q — chỉ để dựng dòng HINT
closure_cands = []       # (agent, topic, ts) mọi finding/answer/decision — chỉ để HINT
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
    resolvers = []          # (topic, ts, explicit refs from payload.resolves)
    acks = []                # (topic_câu_hỏi_được_ack, hạn_ack) — xem ACK_PREFIX
    # HINT-ONLY (Wags coord-2026-08-03): ngoài resolver ĐÚNG quy ước, gom thêm MỌI
    # finding/answer/decision (kèm agent + ts) để GỢI Ý "có thể đã đóng nhưng sai quy ước".
    # KHÔNG dùng để đóng câu hỏi — chỉ in thêm 1 dòng [WARN-ONLY] cho người/Wags triage
    # nhanh. Ca thật: Winston hỏi `nav-zalopay-2207-dong-thu-6-can-duyet` (08-02 08:41) rồi
    # 32 phút sau đăng KẾT QUẢ dưới dạng `finding` với topic ĐỔI KHÁC
    # (`...-dong-thu-6-da-sua-quant-skeptic-CONFIRMED`) → không phải answer/decision, cũng
    # không chứa nguyên topic gốc → matcher (đúng, fail-closed) vẫn báo pending 17h sau và
    # đốt 1 job Wags. Nới matcher để tự đóng ca này là NGUY HIỂM (prefix chung sẽ đóng oan
    # escalation tiền thật) → chọn gợi ý, không tự đóng.
    for p in files:
        agent_p = _agent_of(p)
        for rec in iter_events(p):
            etype = rec.get("event_type")
            if etype == "status" and str(rec.get("topic") or "").startswith(ACK_PREFIX):
                try:
                    a_ts = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
                except Exception:
                    continue   # fail-closed: ack không đọc được ts thì KHÔNG tắt dispatch
                # Cửa sổ phủ các lần CRON phát lại cùng topic (xem ACK_MAX_SUPPRESS_DAYS).
                # Mọi đường lỗi đều rơi về 0 ngày = hành vi cũ (chỉ phủ instance đã có).
                _pl = rec.get("payload")
                if isinstance(_pl, str):
                    try:
                        _pl = json.loads(_pl)
                    except Exception:
                        _pl = {}
                _sd = 0
                if isinstance(_pl, dict):
                    try:
                        _sd = int(_pl.get("suppress_days") or 0)
                    except Exception:
                        _sd = 0
                _sd = max(0, min(_sd, ACK_MAX_SUPPRESS_DAYS))
                acks.append((rec["topic"][len(ACK_PREFIX):].strip(),
                             a_ts + dt.timedelta(days=_sd)))
                continue
            if etype in ("answer", "decision", "finding"):
                t = rec.get("topic")
                if not t:
                    continue
                try:
                    r_ts = dt.datetime.fromisoformat(rec.get("ts", "").replace("Z", "+00:00"))
                except Exception:
                    # Không đọc được ts → coi như rất cũ, KHÔNG cho đóng gì (fail-closed:
                    # thà báo pending thừa hơn làm mù 1 alert thật).
                    continue
                closure_cands.append((agent_p, t, r_ts))
                if etype != "finding":
                    _rp = rec.get("payload")
                    if isinstance(_rp, str):
                        try:
                            _rp = json.loads(_rp)
                        except Exception:
                            _rp = {}
                    _raw = _rp.get("resolves", []) if isinstance(_rp, dict) else []
                    if isinstance(_raw, str):
                        _raw = [_raw]
                    _explicit = {str(x).strip() for x in _raw
                                 if isinstance(_raw, list) and str(x).strip()}
                    resolvers.append((t, r_ts, _explicit))
    def _resolved(q_topic, q_ts, q_agent=""):
        # Exact-match, HOẶC resolver CHỨA nguyên topic câu hỏi (quy ước hậu-tố trạng thái) —
        # và resolver phải xuất hiện SAU câu hỏi. Chỉ 1 chiều (resolver ⊇ topic-hỏi) để 1
        # decision topic-ngắn KHÔNG vô tình khớp câu hỏi dài khác chủ đề.
        if not q_topic:
            return False
        refs = {q_topic}
        if q_agent:
            refs.add(f"{q_agent}/{q_topic}")
        return any(r_ts >= q_ts and
                   ((r == q_topic or q_topic in r) or bool(refs & explicit))
                   for r, r_ts, explicit in resolvers)
    def _same_ref(a, b):
        """Hai chuỗi có trỏ CÙNG một câu hỏi không, chấp nhận cặp trần ↔ 'Agent/topic'.

        Bất đối xứng do arch-review d65167a9 bắt: `_resolved` tự dựng refs={topic,
        agent/topic} nên nó khớp cả 2 dạng, còn `_resolved_exact` so NGUYÊN CHUỖI với
        `explicit` ⇒ con đóng bằng decision gộp khai resolves=["Mike/con-B"] (đúng khuôn
        bin/close_bus_question.py) mà rollup_of viết dạng trần ["con-B"] thì KHÔNG khớp,
        escalation TỔNG kẹt pending VĨNH VIỄN và đốt job wags_autofix mỗi ngày — đúng vòng
        lãng phí mà rollup_of ra đời để diệt.

        CHỈ bóc tiền tố ở bên NÀO CÓ '/' và chỉ khi bên kia KHÔNG có: nếu bóc cả hai thì
        "Mike/x" sẽ khớp "Taylor/x" — hướng false-CLOSED, nguy hiểm hơn hẳn false-pending
        đang sửa. Đây vẫn là exact-match, không phải nới về substring.
        """
        if a == b:
            return True
        if "/" in a and "/" not in b:
            return a.split("/", 1)[1] == b
        if "/" in b and "/" not in a:
            return b.split("/", 1)[1] == a
        return False

    def _resolved_exact(q_topic, q_ts):
        # Như _resolved nhưng BỎ nhánh substring (`q_topic in r`). Dùng RIÊNG cho topic con
        # của `rollup_of`. Lý do (arch-review coord-2026-08-14, killer_objection): danh sách
        # topic con do NGƯỜI viết tay ⇒ với substring, MỘT resolver duy nhất có thể thoả
        # NHIỀU topic con cùng lúc và `all()` đóng luôn escalation TỔNG trong khi câu hỏi con
        # vẫn đang pending. Tái lập được: rollup_of=["patternB","backlog"] + đúng 1 decision
        # "retro-patternB-and-backlog-summary" ⇒ tổng tự đóng dù patternB chưa ai quyết; và
        # topic con viết CẮT CỤT ("retro-pattern-recurring") khớp bừa vào resolver dài hơn.
        # Cùng lý do `_acked` chọn exact: nới tay ở đây đóng oan escalation của USER — đắt
        # hơn nhiều so với 1 job wags_autofix thừa. `resolves` (khai tường minh) vẫn tính.
        if not q_topic:
            return False
        return any(r_ts >= q_ts and
                   (_same_ref(q_topic, r) or any(_same_ref(q_topic, e) for e in explicit))
                   for r, r_ts, explicit in resolvers)
    def _rollup_resolved(rec, q_ts):
        # Câu hỏi TỔNG (escalation gom nhiều câu hỏi con đã mở sẵn) — ca thật
        # `Mike/retro-escalation-2026-08-13-patternB-and-backlog` (08-13T17:46): user quyết
        # 08-14T00:31, Mike đăng `decision` đóng CẢ 2 câu hỏi con trong cùng 1 giây, nhưng
        # topic TỔNG không có event đóng riêng ⇒ check #5 vẫn báo pending và đốt nguyên 1 job
        # wags_autofix (coord-2026-08-14) chỉ để kết luận "đã quyết rồi". Resolver khớp theo
        # topic-string nên không có cách nào biết topic tổng ⊃ 2 topic con.
        # Cơ chế: câu hỏi tổng KHAI TƯỜNG MINH `"rollup_of": ["topic-con-1", ...]` trong
        # payload; đóng khi MỌI topic con có resolver đăng SAU câu hỏi tổng (dùng
        # _resolved_exact, giữ nguyên ràng buộc thời gian — không pre-resolve lần escalate sau).
        # OPT-IN + fail-closed ở MỌI đường lỗi (thiếu field / không phải list / rỗng / payload
        # không parse được ⇒ False = hành vi cũ). KHÔNG suy diễn topic con từ văn bản payload:
        # đó đúng thứ §28 coding_guidelines cấm (so chuỗi mô tả tự do) và đóng oan 1
        # escalation tiền thật đắt hơn nhiều so với 1 job thừa.
        pl = rec.get("payload")
        if isinstance(pl, str):
            try:
                pl = json.loads(pl)
            except Exception:
                return False
        if not isinstance(pl, dict):
            return False
        raw = pl.get("rollup_of")
        if not isinstance(raw, list):
            return False
        subs = [str(s).strip() for s in raw if str(s).strip()]
        if not subs:
            return False
        # Dạng "Agent/topic" (đúng chuỗi checker in ra, người hay copy thẳng) được xử lý
        # DUY NHẤT một chỗ: `_same_ref` bên trong `_resolved_exact`. Trước đây chỗ này bóc
        # tiền tố TRƯỚC rồi gọi _resolved_exact, nên khi _same_ref cũng bóc ở phía `explicit`
        # là bóc HAI LẦN: rollup_of=["Mike/con"] khớp được resolves=["Taylor/con"] — đóng
        # escalation của agent này bằng quyết định của agent KHÁC, tức false-CLOSED, hướng
        # lỗi nguy hiểm nhất. Selfcheck ca 15e giữ đúng chốt đối chứng này.
        return all(_resolved_exact(s, q_ts) for s in subs)
    def _acked(q_agent, q_topic, q_ts):
        # Khớp CHÍNH XÁC (không substring như _resolved): ack chỉ tắt auto-dispatch nên sai
        # sót về phía "vẫn dispatch" là an toàn; nới lỏng match ở đây thì 1 ack topic ngắn
        # có thể tắt dispatch cho câu hỏi khác chưa ai xem. Chấp nhận cả dạng "Agent/topic"
        # (đúng chuỗi checker in ra) để người copy thẳng từ báo cáo.
        if not q_topic:
            return False
        # `a_until` = ts ack + suppress_days (mặc định 0 ⇒ đúng điều kiện cũ "ack đăng SAU
        # câu hỏi"); >0 phủ thêm các lần cron phát lại CÙNG topic trong cửa sổ đó.
        want = (q_topic, f"{q_agent}/{q_topic}")
        return any(a in want and a_until >= q_ts for a, a_until in acks)
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
            if _resolved(rec.get("topic"), ts_dt, agent) or _rollup_resolved(rec, ts_dt):
                continue
            # Chống đếm đôi nếu 1 event vừa còn ở hot inbox vừa đã sang archive (kb_nightly
            # bị kill giữa chừng): khoá theo (agent, topic, ts).
            key = (agent, rec.get("topic"), rec.get("ts"))
            if key in seen_q:
                continue
            seen_q.add(key)
            if ts_dt >= cutoff:
                # WAGS_SELF_Q_PREFIXES là câu hỏi TỰ chính pipeline wags_autofix sinh ra khi
                # arch-reviewer verdict != CONFIRMED, hoặc khi chuỗi kiểm chứng không ra được
                # phán quyết (INCONCLUSIVE — xem bin/wags_autofix.sh). Đưa nó vào
                # pending_q (routable) như mọi câu hỏi khác từng khiến COORD_WARN dispatch LẠI
                # wags_autofix cho ĐÚNG issue vừa NEEDS_CHANGES — vòng phản hồi dương tự nuôi
                # (audit §14 kiến trúc fleet 2026-07-31, Fable plan + Opus critique: "output
                # của vòng lặp là input của vòng kế tiếp"). Comment thiết kế gốc của
                # wags_autofix.sh đã NÓI RÕ ý định "không tự ép vòng 2 vô hạn — con người quyết"
                # nhưng nhánh dispatch ở dưới (COORD_WARN) không tôn trọng ý định đó cho đúng
                # loại câu hỏi này. Tách riêng + gắn WARN_ONLY: vẫn hiện trong báo cáo cho
                # người thấy, KHÔNG tự re-trigger — người/Mike quyết vòng kế tiếp tường minh.
                if str(rec.get("topic") or "").startswith(WAGS_SELF_Q_PREFIXES):
                    pending_q_wagsfix.append(f"{agent}/{rec.get('topic')}")
                elif _acked(agent, str(rec.get("topic") or ""), ts_dt):
                    pending_q_needs_human.append(f"{agent}/{rec.get('topic')}")
                else:
                    pending_q.append(f"{agent}/{rec.get('topic')}")
                    pending_q_meta.append((agent, str(rec.get("topic") or ""), ts_dt))
            else:
                age_d = (_now - ts_dt).days
                # Cờ thứ 3: câu hỏi này có thuộc lớp vòng-wags-fix (miễn cắt) không —
                # phân loại tại NGUỒN bằng ĐÚNG tuple WAGS_SELF_Q_PREFIXES mà nhánh <48h
                # dùng, để hai bên không trôi ra khỏi nhau khi thêm tiền tố mới.
                _is_wags = str(rec.get("topic") or "").startswith(WAGS_SELF_Q_PREFIXES)
                aged_q.append((age_d, f"{agent}/{rec.get('topic')} ({age_d}d)", _is_wags))
    if read_errors:
        # KHÔNG gắn [WARN-ONLY]: đây là lỗi TOOLING sửa được (khác với backlog chờ user).
        # Câu chữ cố ý chứa "câu hỏi (question)" để nhánh routing dưới đưa về COORD_WARN
        # → wags_autofix (Wags), không rơi vào OTHER_WARN → ops_autofix per-account.
        W(f"{len(read_errors)} file bus KHÔNG ĐỌC ĐƯỢC — backlog câu hỏi (question) có thể "
          f"THIẾU (bỏ sót toàn bộ event trong các file này): "
          f"{ {k: v for k, v in sorted(read_errors.items())} }")
else:
    # Sai wc_root ⇒ inbox_dir không tồn tại ⇒ MỌI danh sách rỗng ⇒ nhánh `elif` dưới in ✅
    # "không có câu hỏi" — im lặng hoá TOÀN BỘ kênh backlog của fleet mà không một lời cảnh
    # báo. Chính arch-reviewer vấp phải khi audit coord-2026-08-14 (check fail_silent, "nên
    # mở ticket riêng"). Cùng họ với cliff-30-ngày ở trên: một lần TRA CỨU thất bại không
    # được phép đội lốt một kết luận "sạch".
    W(f"KHÔNG tìm thấy thư mục bus/inbox ({inbox_dir}) — backlog câu hỏi (question) KHÔNG "
      f"kiểm tra được lượt này (KHÔNG phải '0 câu hỏi'). Nhiều khả năng wc_root sai.")
if pending_q:
    W(f"Có {len(pending_q)} câu hỏi (question) trong 48h qua CHƯA thấy answer tương ứng: {pending_q}")
    # Dòng HINT: câu hỏi nào có sự kiện đăng SAU nó trông như đã xử lý xong nhưng ghi bus
    # sai quy ước (đăng `finding`/đổi topic thay vì `answer`/`decision` GIỮ NGUYÊN topic
    # gốc). Chỉ GỢI Ý: không đóng, không loại khỏi pending_q, không đổi routing dòng WARN.
    # HAI tín hiệu (OR):
    #   (a) STEM  — topic dùng chung tiền tố dài (≥ STEM_MIN ký tự), BẤT KỲ tác giả nào.
    #   (b) TOKEN — chia sẻ ≥1 "từ hiếm" (≥ TOKEN_MIN ký tự, df ≤ DF_MAX topic trên toàn
    #       bus, không nằm trong STOPWORDS) VÀ đăng trong vòng WIN_H giờ sau câu hỏi.
    # Vì sao BỎ ràng buộc "cùng tác giả" của bản cũ: người đóng câu hỏi THƯỜNG là agent
    # KHÁC người hỏi (chính DollarBill đề xuất Winston là người phụ trách). Đây đúng lớp
    # root cause của sự cố 2026-07-10 (matcher per-file làm answer chéo-agent không bao
    # giờ khớp) — bản HINT thêm 2026-08-03 vô tình tái lập ràng buộc same-author đó, nên
    # ca thật `DollarBill/rubber-alert-52w-label-sai` (Winston sửa xong sau 3h42, đăng
    # `finding` topic khác) không được gợi ý và đốt 1 job Wags ngày 2026-08-07.
    # Vì sao TOKEN cần df/stoplist/cửa sổ thời gian: đo trên toàn bus (1820 topic ứng viên,
    # 63 câu hỏi) — token-overlap TRẦN (không lọc) gợi ý 61/63 câu hỏi = vô nghĩa, và tệ
    # hơn là gán nhầm alert tiền thật `plan-t1-not-ready-SpaceX` cho 1 finding LAG-rating
    # không liên quan. Lọc df ≤ 15 loại tên account dùng chung khắp nơi (zalopay df=76,
    # spacex df=67) nhưng giữ danh từ miền (rubber df=12); + cửa sổ 48h + stoplist từ
    # chung chung → còn 9 gợi ý, ~5 đúng thật (rubber, fill_timing, mafee-stamp,
    # retro-backlog, và dnse-phs-margin-thresholds do Mafee đóng chéo-agent).
    STEM_MIN = 16
    TOKEN_MIN = 5     # bỏ từ ngắn/chức năng
    DF_MAX = 15       # "hiếm" = xuất hiện ở ≤ 15 topic trên toàn bus (xem đo lường trên)
    WIN_H = 48        # người đóng câu hỏi thường đăng trong vòng 2 ngày
    # Từ nghiệp vụ CHUNG CHUNG: đủ hiếm để lọt df nhưng không nói lên chủ đề nào cả —
    # đo được là nguồn của 4/9 gợi ý sai (ready/watch/context/chase/phien).
    STOPWORDS = {"ready", "watch", "context", "chase", "phien", "trong", "khong", "duoc"}
    def _rare_toks(s, df=None):
        ws = {w for w in re.split(r"[^0-9a-z]+", s.lower())
              if len(w) >= TOKEN_MIN and w not in STOPWORDS}
        return ws if df is None else {w for w in ws if df[w] <= DF_MAX}
    topic_df = defaultdict(int)
    for _, c_topic, _ in closure_cands:
        for w in _rare_toks(c_topic):
            topic_df[w] += 1
    hints = []
    for q_agent, q_topic, q_ts in pending_q_meta:
        q_rare = _rare_toks(q_topic, topic_df)
        for c_agent, c_topic, c_ts in closure_cands:
            if c_topic == q_topic or c_ts < q_ts:
                continue
            why = None
            if len(os.path.commonprefix([q_topic, c_topic])) >= STEM_MIN:
                why = "cùng tiền tố"
            elif q_rare & _rare_toks(c_topic) and \
                    (c_ts - q_ts).total_seconds() <= WIN_H * 3600:
                why = "chung từ hiếm " + ",".join(sorted(q_rare & _rare_toks(c_topic)))
            if why:
                who = "cùng tác giả" if c_agent == q_agent else f"tác giả khác: {c_agent}"
                hints.append(f"{q_agent}/{q_topic} ~ [{who}; {why}] {c_topic}")
                break
    if hints:
        W(f"{WARN_ONLY} {len(hints)}/{len(pending_q)} câu hỏi trên CÓ THỂ đã xử lý xong "
          f"nhưng ghi bus SAI QUY ƯỚC (có sự kiện đăng sau, cùng tiền tố topic HOẶC chung "
          f"từ hiếm trong {WIN_H}h — GỢI Ý thôi, phải tự kiểm chứng; quy ước đóng: "
          f"`answer`/`decision` GIỮ NGUYÊN topic câu hỏi): {hints}")
elif os.path.isdir(inbox_dir) and not pending_q_wagsfix and not pending_q_needs_human:
    # Điều kiện isdir là BẮT BUỘC: không quét được ≠ quét xong và sạch (xem `else` ở trên).
    OK("Không có câu hỏi (question) nào đang chờ xử lý trong 48h qua.")
if pending_q_needs_human:
    W(f"{WARN_ONLY} {len(pending_q_needs_human)} câu hỏi ĐÃ TRIAGE, chờ NGƯỜI quyết (không "
      f"có fix tooling — KHÔNG tự dispatch lại, vẫn hiện ở đây cho tới khi có "
      f"answer/decision thật): {pending_q_needs_human}")
if pending_q_wagsfix:
    W(f"{WARN_ONLY} {len(pending_q_wagsfix)} vòng wags-fix CHƯA CONFIRMED trong 48h qua (gồm cả "
      f"NEEDS_CHANGES/REFUTED lẫn INCONCLUSIVE — 'không tra ra phán quyết' KHÁC 'fix bị bác', "
      f"đọc topic để phân biệt) — KHÔNG tự re-trigger (đã qua ít nhất 1 vòng fix+arch-review, lặp "
      f"tự động là vòng lặp tự nuôi vô nghĩa — người/Mike quyết vòng kế tiếp tường minh, hoặc chờ "
      f"cooldown hôm sau tự thử lại): {pending_q_wagsfix}")
if aged_q:
    aged_q.sort(key=lambda x: -x[0])   # cũ nhất trước
    if len(aged_q) <= AGED_SHOW_ALL_UPTO:
        shown = [lbl for _, lbl, _w in aged_q]
        W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần "
          f"USER quyết (in đủ): {shown}")
    elif any(w for _, _, w in aged_q):
        # MIỄN CẮT lớp vòng-wags-fix (xem AGED_WAGS_MAX ở trên): in ĐỦ nhóm này, rồi mới
        # áp cắt-giữa lên PHẦN CÒN LẠI. Không đổi hành vi khi backlog ≤ 10 và không đổi gì
        # cho các loại câu hỏi khác.
        wags_all = [lbl for _, lbl, w in aged_q if w]
        wags = wags_all[:AGED_WAGS_MAX]
        wags_cut = len(wags_all) - len(wags)
        rest_pairs = [(a, lbl) for a, lbl, w in aged_q if not w]
        if len(rest_pairs) <= AGED_OLDEST + AGED_NEWEST:
            rest_txt = f"{len(rest_pairs)} mục còn lại (in đủ): {[lbl for _, lbl in rest_pairs]}"
        else:
            oldest = [lbl for _, lbl in rest_pairs[:AGED_OLDEST]]
            tail = rest_pairs[AGED_OLDEST:]
            newest = [lbl for _, lbl in (tail[-AGED_NEWEST:] if AGED_NEWEST > 0 else [])]
            rest_txt = (f"{len(rest_pairs)} mục còn lại — {len(oldest)} cũ nhất: {oldest} "
                        f"…và {len(tail) - len(newest)} mục giữa… {len(newest)} mới nhất: {newest}")
        W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần USER "
          f"quyết. VÒNG WAGS-FIX chưa đóng ({len(wags)} mục, MIỄN CẮT vì đã tắt auto-dispatch, "
          f"dòng này là kênh duy nhất tới người)"
          f"{f' — CẢNH BÁO đã cắt {wags_cut} mục wags vượt trần {AGED_WAGS_MAX}' if wags_cut else ''}"
          f": {wags}. {rest_txt}. Danh sách ĐẦY ĐỦ: bin/bus_question_audit.py")
    else:
        # Cắt GIỮA: giữ cả mục treo lâu nhất LẪN mục mới nhất — zombie cũ không được phép
        # chèn escalation mới ra khỏi màn hình (xem chú thích AGED_SHOW_ALL_UPTO ở trên).
        # Cắt trên phần CÒN LẠI (không dùng aged_q[-N:]) — với N=0 thì aged_q[-0:] trả về
        # NGUYÊN danh sách, in trùng toàn bộ. Bẫy này bị mutation-test bắt được.
        oldest = [lbl for _, lbl, _w in aged_q[:AGED_OLDEST]]
        rest = aged_q[AGED_OLDEST:]
        newest = [lbl for _, lbl, _w in (rest[-AGED_NEWEST:] if AGED_NEWEST > 0 else [])]
        more = len(rest) - len(newest)
        W(f"{WARN_ONLY} Câu hỏi TREO LÂU (>48h, chưa ai quyết) — {len(aged_q)} mục, cần "
          f"USER quyết; {len(oldest)} cũ nhất: {oldest} …và {more} mục giữa… "
          f"{len(newest)} mới nhất: {newest}. Danh sách ĐẦY ĐỦ: bin/bus_question_audit.py")
# CHECK5_END

# 5b. Hàng đợi CÁCH LY của append_event.sh (bus/_rejected.jsonl) — thêm 2026-08-16 theo
#     arch-review coord-2026-08-16 required_change #3. append_event.sh chặn arg bị shell
#     word-split và ghi nguyên văn vào đây thay vì để event hỏng lọt lên bus; nhưng 28/42
#     call site gọi kèm `2>/dev/null || true` nên thông điệp fail-loud bị vứt VÀ exit code
#     bị nuốt ⇒ với nhóm đó, event biến mất không dấu vết trừ file này. File không người
#     đọc = đúng hình thái "lỗi chết trong log không ai đọc" mà chính cơ chế cách ly sinh
#     ra để diệt. Dòng dưới là NGƯỜI ĐỌC đó; người DỌN là fleet_housekeeping.sh category
#     `rotate`. Cố ý ĐỂ NGOÀI CHECK5_BEGIN/END: khối đó có hợp đồng namespace hạn chế với
#     ops_health_check_selfcheck.py (chỉ glob/gzip/json/os/re + W/OK + wc_root).
# 5b_BEGIN — marker ỔN ĐỊNH cho bin/ops_health_check_rejected_selfcheck.py. Khối chỉ được
# dùng: os/json + wc_root + W()/OK() (selfcheck cung cấp đúng bấy nhiêu); mọi thứ khác PHẢI
# tự import TẠI ĐÂY (xem sự cố defaultdict 2026-08-07 ghi ở đầu CHECK5).
_qf = os.path.join(wc_root, "mike", "bus", "_rejected.jsonl")
if os.path.exists(_qf):
    import datetime as _dt
    _q24, _qtot, _qbad = [], 0, 0
    _qcut = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=24)
             ).strftime("%Y-%m-%dT%H:%M:%SZ")
    _qerr = None
    try:
        # errors="replace": file này chứa arg ĐÃ BỊ CHẶN vì hỏng — đọc nó mà chết
        # UnicodeDecodeError thì check cảnh báo lại tự thành sự cố im lặng thứ hai.
        with open(_qf, encoding="utf-8", errors="replace") as _f:
            for _ln in _f:
                _ln = _ln.strip()
                if not _ln:
                    continue
                _qtot += 1
                # try BỌC CẢ THÂN VÒNG LẶP, không chỉ json.loads (arch-review round 2):
                # bản đầu để `_r.get(...)` NGOÀI try nên một dòng JSON không-phải-object
                # (vd `12345`) ném AttributeError thoát thẳng ra `except` bao ngoài ⇒ vòng
                # quét ĐỨT giữa chừng, mọi bản ghi PHÍA SAU vô hình. Reader sinh ra để diệt
                # fail-silent mà tự fail-silent. Dòng hỏng giờ chỉ tăng _qbad rồi đi tiếp.
                try:
                    _r = json.loads(_ln)
                    if not isinstance(_r, dict):
                        raise ValueError("dòng JSON không phải object")
                    if str(_r.get("ts", "")) >= _qcut:
                        _q24.append(_r)
                except Exception:
                    _qbad += 1
                    continue
    except Exception as _e:
        _qerr = _e
    if _qerr is not None:
        # W() chứ KHÔNG phải lines.append: lines.append in ra ℹ️ mà KHÔNG tăng biến `warn`
        # ⇒ không escalate, đúng thứ hình thái im lặng mà cả khối này đi diệt.
        W(f"Không đọc được bus/_rejected.jsonl ({_qerr}) — hàng đợi cách ly của "
          f"append_event.sh đang KHÔNG được giám sát; event bị chặn sẽ mất dấu vết.")
    if _q24 or _qbad:
        # Ép kiểu + đặt TRONG vùng an toàn: file này chứa dữ liệu HỎNG theo thiết kế, một
        # bản ghi méo (reason là list, argv là dict) từng đủ sức ném ra ngoài heredoc và
        # giết CẢ 11 check của ops_health_check, không riêng khối này (arch-review round 2).
        def _q_who(_r):
            _a = _r.get("argv")
            return str(_a[0]) if isinstance(_a, list) and _a else "?"
        _who = sorted({_q_who(_r) for _r in _q24})
        _why = sorted({str(_r.get("reason") or "?").split("\n")[0][:70] for _r in _q24})
        W(f"append_event.sh đã CÁCH LY {len(_q24)} bản ghi trong 24h qua "
          f"({_qtot} bản ghi trong file hiện tại"
          f"{f', {_qbad} dòng không parse được' if _qbad else ''}) "
          f"— đây là event KHÔNG BAO GIỜ lên bus: agent gọi bị shell word-split payload và "
          f"phần lớn call site nuốt stderr nên agent tưởng đã ghi thành công. "
          f"Agent: {_who}. Lý do: {_why}. "
          f"Xem `tail bus/_rejected.jsonl`; sửa cách quote ở call site rồi ghi LẠI event "
          f"(hàng đợi này là PHÁP Y, không ai tự phát lại — payload hỏng phát lại vẫn hỏng).")
    elif _qtot:
        OK(f"Hàng đợi cách ly append_event.sh: {_qtot} bản ghi cũ trong file hiện tại, "
           f"24h qua không có ca mới.")
# 5b_END — bin/ops_health_check_rejected_selfcheck.py TRÍCH khối giữa 5b_BEGIN/5b_END rồi
# chạy trên namespace stub. Đổi/xoá 2 marker này ⇒ selfcheck FAIL ngay, không im lặng.

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

# 10. notify_thread.sh không phân giải được topic ⇒ TIN NHẮN BỊ NUỐT (thêm 2026-08-02, saga
#     discord-routing vòng 4). notify_thread.sh ghi 1 dòng vào logs/notify_thread_errors.log
#     mỗi lần nó không gửi được; mọi caller đều bọc `2>/dev/null || true` nên KHÔNG ai thấy
#     lỗi qua exit code. Trước check này KHÔNG script nào đọc file đó — fail-loud mà không có
#     người đọc thì vẫn là fail-silent (đã mất thật 1 tin momentum_deals 2026-08-02T23:14).
#     WARN-only, cửa sổ 24h để cảnh báo tự tắt sau khi hết lỗi.
#
#     Marker `[WARN-ONLY]` là CỐ Ý (thêm vòng 5, arch-reviewer MINOR-3): cảnh báo này dựa trên
#     MTIME nên KHÔNG tắt được bằng cách sửa root cause — sửa xong nó vẫn kêu tới hết 24h. Nếu
#     để nó rơi vào OTHER_WARN thì mỗi ngày dispatch tới 4 job autofix (08:20 + 12:45 × 2
#     account) cho một sự cố đã xử lý xong. Dòng này chỉ cần NẰM TRONG báo cáo cho người đọc.
# CHECK10_BEGIN — marker ỔN ĐỊNH: bin/ops_health_check_selfcheck.py trích ĐÚNG khối giữa
# CHECK10_BEGIN/CHECK10_END rồi chạy nó trên log giả. Đổi/xoá marker ⇒ selfcheck FAIL ngay.
import time as _time
nte_file = os.path.join(wc_root, "mike", "logs", "notify_thread_errors.log")
if os.path.exists(nte_file) and (_time.time() - os.path.getmtime(nte_file)) < 86400:
    try:
        # Chỉ lấy dòng MỞ ĐẦU BẢN GHI (có timestamp) — thông điệp lỗi có thể tràn nhiều dòng
        # (discord_channel.sh in thêm danh sách tên hợp lệ), lấy dòng cuối thô sẽ ra đúng cái
        # đuôi vô nghĩa đó.
        _nte_lines = [l for l in open(nte_file, encoding="utf-8", errors="replace").read().splitlines()
                      if re.match(r"^\d{4}-\d{2}-\d{2}T", l)]
    except Exception:
        _nte_lines = []
    # notify_thread.sh ghi HAI loại bản ghi vào cùng file, và chúng có hệ quả NGƯỢC nhau:
    # "DA TU SUA VA GUI" = phát hiện caller đảo thứ tự đối số, script TỰ SỬA và tin ĐÃ ĐẾN
    # nơi; mọi bản ghi còn lại = tin KHÔNG gửi được. Trước 2026-08-16 check này gộp cả hai
    # dưới một tiêu đề "TIN NHẮN ĐÃ BỊ NUỐT" ⇒ báo cho người rằng một tin đã giao là bị mất
    # (arch-review coord-2026-08-12 required_change #3: "sửa cả người ĐỌC, không chỉ người
    # GHI"). Một lần tra cứu/nhận dạng sai không được đội lốt một kết luận về sự cố thật.
    _nte_swap = [l for l in _nte_lines if "DA TU SUA VA GUI" in l]
    _nte_hard = [l for l in _nte_lines if "DA TU SUA VA GUI" not in l]
    if _nte_hard:
        W(f"[WARN-ONLY] notify_thread.sh có lỗi gửi Discord trong 24h qua — TIN NHẮN ĐÃ BỊ NUỐT. "
          f"Dòng cuối: {_nte_hard[-1][:300]} — kiểm tên topic trong mike/kb/discord_channels.json "
          f"và quyền chạy bin/discord_channel.sh.")
    elif _nte_swap:
        W(f"[WARN-ONLY] notify_thread.sh: {len(_nte_swap)} call site ĐẢO THỨ TỰ đối số trong 24h "
          f"qua — tin ĐÃ ĐƯỢC GỬI (script tự sửa), KHÔNG mất tin. Sửa call site cho đúng "
          f"`notify_thread.sh \"<message>\" <topic>`. Dòng cuối: {_nte_swap[-1][:300]}")
    elif not _nte_lines:
        W(f"[WARN-ONLY] notify_thread_errors.log vừa được ghi trong 24h qua nhưng KHÔNG đọc "
          f"được bản ghi nào có timestamp — không kết luận được có mất tin hay không.")
    else:
        OK("notify_thread.sh: không có lỗi gửi Discord trong 24h qua.")
else:
    OK("notify_thread.sh: không có lỗi gửi Discord trong 24h qua.")
# CHECK10_END

# 11. Quét selfcheck production: đã chạy gần đây chưa + đang có ca ĐỎ nào (thêm 2026-08-12,
#     job Wags_20260812_112724 — sự cố 4 selfcheck đỏ 2 ngày không ai biết).
#     ĐỌC ARTIFACT, KHÔNG chạy lại 92 selfcheck: bộ quét mất ~15-25' và đã chạy 1 lần/ngày bằng
#     cron riêng (bin/selfcheck_weekly_baseline_check.sh, 04:30 ICT). Nhét nó vào đường nóng
#     08:20 — 25' trước preflight — là biến một checker rẻ thành thứ tranh CPU với phiên sáng.
#     PHÂN TẦNG ROUTING có chủ đích:
#       · bộ quét CHẾT/ôi → WARN thường (routable → ops_autofix): cron hỏng là lỗi SỬA ĐƯỢC, và
#         im lặng ở đây biến chính cơ chế phát hiện thành thứ nó sinh ra để chống.
#       · CÓ ca đỏ        → [WARN-ONLY]: bộ quét ĐÃ escalate từng ca (bus question + Discord).
#         Để routable nữa thì mỗi ngày 4 job autofix cho việc đã báo — đúng vòng lặp mà check #10
#         và ACK_PREFIX ở trên đã phải bịt 2 lần.
# CHECK11_BEGIN — marker ỔN ĐỊNH (giống CHECK5/CHECK10): selfcheck trích đúng khối này rồi chạy
# trên artifact giả. Đổi/xoá marker ⇒ bin/ops_health_check_selfcheck.py FAIL ngay.
_scb = os.path.join(wc_root, "mike", "kb", "selfcheck_baseline.json")
_scl = sorted(glob.glob(os.path.join(wc_root, "mike", "logs", "selfcheck_weekly_*.json")))
_SC_STALE_H = 36     # cron 1 lần/ngày → 36h cho phép lỡ đúng 1 lần rồi mới kêu
try:
    if not _scl:
        raise FileNotFoundError("chưa có file kết quả selfcheck_weekly_*.json nào")
    with open(_scl[-1], encoding="utf-8") as _f:
        _scr = json.load(_f)
    _sc_ts = dt.datetime.fromisoformat(str(_scr.get("ts")).replace("Z", "+00:00"))
    _sc_age_h = (dt.datetime.now(dt.timezone.utc) - _sc_ts).total_seconds() / 3600.0
    with open(_scb, encoding="utf-8") as _f:
        _sc_red = (json.load(_f) or {}).get("known_red") or {}
    if _sc_age_h > _SC_STALE_H:
        W(f"Quét selfcheck ÔI: lần cuối {_scr.get('ts')} ({_sc_age_h:.0f}h trước, ngưỡng "
          f"{_SC_STALE_H}h) — nghi cron 04:30 ICT chết. Chạy tay: "
          f"bash mike/bin/selfcheck_weekly_baseline_check.sh")
    elif _sc_red:
        # Tách 2 loại: `auto` = tự phát hiện, CHƯA AI TRIAGE (việc còn nợ); còn lại là đỏ người
        # đã xem và chấp nhận có lý do (vd IAM) — gộp chung thì việc nợ chìm vào cái đã chấp nhận,
        # đúng lớp nhiễu đang sửa.
        _sc_new = sorted(k for k, v in _sc_red.items() if isinstance(v, dict) and v.get("auto"))
        _sc_ack = sorted(k for k, v in _sc_red.items() if not (isinstance(v, dict) and v.get("auto")))
        if _sc_new:
            W(f"{WARN_ONLY} {len(_sc_new)} selfcheck production ĐỎ CHƯA AI TRIAGE (mỗi ca đã có "
              f"bus question 'selfcheck-red: <file>', KHÔNG dispatch lại ở đây): "
              # KHÔNG cắt danh sách: verify thật 2026-08-12 cho thấy `[:8]` giấu mất
              # t2_settlement_selfcheck.py (guard settlement) khỏi báo cáo hằng ngày. Việc nợ bị
              # cắt khỏi báo cáo = việc không tồn tại; dài vài dòng rẻ hơn nhiều so với mù.
              f"{_sc_new}"
              + (f" · {len(_sc_ack)} ca đỏ đã chấp nhận có lý do." if _sc_ack else "")
              + f" Quét {_sc_age_h:.0f}h trước, {_scr.get('pass')}/{_scr.get('total')} PASS.")
        else:
            OK(f"Quét selfcheck: {_scr.get('pass')}/{_scr.get('total')} PASS, 0 ca đỏ chưa triage "
               f"({len(_sc_ack)} đỏ đã chấp nhận có lý do; quét {_sc_age_h:.0f}h trước).")
    else:
        OK(f"Quét selfcheck: {_scr.get('pass')}/{_scr.get('total')} PASS, 0 ĐỎ "
           f"(quét {_sc_age_h:.0f}h trước).")
except FileNotFoundError as _e:
    W(f"Quét selfcheck CHƯA TỪNG CHẠY / thiếu artifact ({_e}) — cron 04:30 ICT chưa cài hoặc "
      f"chưa tới lần chạy đầu.")
except Exception as _e:
    # Fail LOUD: artifact hỏng KHÔNG được rơi về im lặng — im lặng ở đây nghĩa là "không biết
    # selfcheck nào đang đỏ" mà lại trông y hệt "không có ca đỏ nào".
    W(f"Quét selfcheck: KHÔNG đọc được artifact ({type(_e).__name__}) — không kết luận được có "
      f"selfcheck nào đỏ hay không.")
# CHECK11_END

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
    # Cổng độ tươi watchlist (§14, 2026-08-14) — kiểm TRƯỚC tier-H: quét sổ cũ thì kết luận
    # "không có tín hiệu" không có giá trị, phải nói ra chứ không được nuốt vào dòng ✅.
    ANOMALY_STALE_NOTE=""
    if echo "$ESC_OUT" | grep -q "watchlist QUÁ HẠN"; then
      ANOMALY_WARN=1
      ANOMALY_STALE_NOTE="🕒 $(echo "$ESC_OUT" | grep 'watchlist QUÁ HẠN') — đang quét theo SỔ CŨ, mã mua sau ngày đó không được theo dõi. Kiểm compute_active_nav_all.sh 20:15 ICT.
"
    fi
    if echo "$ESC_OUT" | grep -q "tier-H MỚI"; then
      ANOMALY_WARN=1
      ANOMALY_SUMMARY="🚨 Anomaly (giá/khối lượng): $(echo "$ESC_OUT" | grep 'tier-H MỚI') — ĐÃ khởi động due-diligence (Wendy+Spyros), chi tiết ở alert riêng phía trên. KHÔNG tự mua/bán, chờ user/Mike duyệt."
    elif echo "$ESC_OUT" | grep -q "trạng thái sàn"; then
      ANOMALY_SUMMARY="📋 Anomaly: $(echo "$ESC_OUT" | grep 'trạng thái sàn') — nhãn theo dõi thực thi (không phải cảnh báo sớm)."
    else
      ANOMALY_SUMMARY="✅ Anomaly scan (giá/khối lượng + trạng thái sàn): không có tín hiệu tier-H mới."
    fi
    ANOMALY_SUMMARY="${ANOMALY_STALE_NOTE}${ANOMALY_SUMMARY}"
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
# OPS_HEALTH_DRY_RUN=1 → chỉ IN báo cáo, không gửi Discord / không ghi bus / không dispatch
# autofix (thêm Wags coord-2026-08-03). Trước đây KHÔNG có đường chạy thử: mỗi lần verify 1
# fix của check này đều bắn 1 tin Trading Daily thật + 1 bus event + có thể spawn job autofix
# → người sửa hoặc né verify, hoặc gây nhiễu vận hành. Mặc định (biến không set) = y như cũ.
DRY_RUN="${OPS_HEALTH_DRY_RUN:-0}"
if [ "$DRY_RUN" = "1" ]; then
  echo "[DRY-RUN] bỏ qua: notify_thread (+dự phòng notify_telegram) / append_event / dispatch autofix"
else
# DELIVER_BEGIN — giao báo cáo tới người: Discord trước, Telegram nếu Discord hỏng.
#
# VÌ SAO CÓ NHÁNH DỰ PHÒNG (2026-08-03, vòng 6 arch-reviewer, sự cố registry 2026-08-02):
# `notify_thread.sh` với TÊN `trading_daily` phân giải qua `discord_channel.sh` →
# `kb/discord_channels.json` — CHÍNH registry đã hỏng thật hôm 2026-08-02. Nghĩa là check #10
# (đọc `logs/notify_thread_errors.log` để phát hiện sự cố định tuyến) trước đây tự vô hiệu hoá
# đúng lúc cần nhất: registry hỏng KÉO DÀI ⇒ chính báo cáo tố cáo nó cũng câm ⇒ không ai được
# báo gì cả. Khâu GHI độc lập với Discord là chưa đủ — khâu GIAO cũng phải có đường thoát.
# `notify_telegram.sh` đi thẳng HTTPS tới api.telegram.org: không bridge 127.0.0.1:8199, không
# registry, credential riêng ⇒ không chết chung nguyên nhân.
# CHỈ chạy khi Discord THẤT BẠI (không gửi song song — tránh nhân đôi tin mỗi 08:20/12:45).
if ! "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_DAILY_THREAD" 2>/dev/null; then
  if ! "$ROOT/bin/notify_telegram.sh" "⚠️ [Discord không gửi được — đường dự phòng Telegram]
$MSG"; then
    # Cả 2 đường chết: ghi vào chính file mà check #10 đọc, để lượt chạy sau tố cáo được.
    mkdir -p "$ROOT/logs"
    printf '%s ops_health_check: CA HAI duong bao deu that bai (Discord %s + Telegram) — bao cao %s KHONG toi tay ai.\n' \
      "$(date -Iseconds)" "$TRADING_DAILY_THREAD" "${ACCOUNT}-${TODAY}" \
      >> "$ROOT/logs/notify_thread_errors.log" 2>/dev/null || true
    echo "ops_health_check: CẢ Discord LẪN Telegram đều không gửi được báo cáo" >&2
  fi
fi
# DELIVER_END
"$ROOT/bin/append_event.sh" Mike status "ops-health-check-${ACCOUNT}-${TODAY}" \
  "{\"account\":\"${ACCOUNT}\",\"label\":\"${LABEL}\",\"warn_count\":${WARN_COUNT:-0}}" 2>/dev/null || true
fi

# Tự sửa thay vì chỉ cảnh báo (mandate user 2026-07-07, xem kb/ops_runbook.md) — trừ
# trường hợp DUY NHẤT plan chưa duyệt/chưa có (việc của user, autofix không tạo/duyệt
# plan được). Chia domain (mandate mở rộng 2026-07-07): lỗi ĐIỀU PHỐI giữa agent
# (circuit breaker, question tồn đọng) → Wags (wags_autofix, có arch-reviewer audit);
# lỗi vận hành trading/pipeline còn lại → Winston (ops_autofix). Cả 2 tự chống lặp 1h.
if [ "${WARN_COUNT:-0}" -gt 0 ] && [ "$DRY_RUN" != "1" ]; then
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
