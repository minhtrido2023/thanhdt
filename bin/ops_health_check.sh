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
# eod_trading_report.sh (19:10) — chạy TRƯỚC mỗi phiên để con người có thời gian phản ứng.
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
# `tripped_until` KHÔNG tự bị xoá khi hết hạn — bin/mike_json.py circuit-check dọn LAZY,
# chỉ vào đúng lúc có dispatch mới tới agent đó. Nên test truthiness (`if tripped_until:`)
# báo TRIPPED VĨNH VIỄN cho mọi agent từng trip rồi không được dispatch lại. Sự cố thật
# 2026-08-19: breaker Taylor hết hạn 05:43:03Z, check này 05:45:07Z vẫn báo TRIPPED → đốt
# một job Wags(Opus) cho trạng thái đã tự khỏi. Hỏi mike_json (so với NOW, read-only) thay
# vì tự đọc file. KHÔNG fail-OPEN: lệnh lỗi phải KÊU, không được nuốt rồi in ✅.
circuit_dir = os.path.join(wc_root, "mike", "state", "circuit")
tripped, _cb_err = [], ""
try:
    _cb = subprocess.run([sys.executable, os.path.join(wc_root, "mike", "bin", "mike_json.py"),
                          "circuit-tripped", circuit_dir],
                         capture_output=True, text=True, timeout=30)
    if _cb.returncode != 0:
        _cb_err = (_cb.stderr or "rc=%d" % _cb.returncode).strip()[:200]
    else:
        for _ln in _cb.stdout.splitlines():
            _ln = _ln.strip()
            if not _ln:
                continue
            _ag, _, _rem = _ln.partition(" ")
            tripped.append(f"{_ag} (còn {int(_rem) // 60}p{int(_rem) % 60}s)" if _rem.isdigit() else _ag)
except Exception as e:
    _cb_err = f"{type(e).__name__}: {e}"[:200]
if _cb_err:
    W(f"Circuit breaker: KHÔNG kiểm tra được ({_cb_err}) — coi như CHƯA BIẾT, không phải 'bình thường'.")
elif tripped:
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
# CHECK5_NOW chỉ dành cho selfcheck ghim kịch bản lịch cố định; production không set biến này.
_now_env = os.environ.get("CHECK5_NOW", "")
_now = (dt.datetime.fromisoformat(_now_env.replace("Z", "+00:00"))
        if _now_env else dt.datetime.now(dt.timezone.utc))
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
# THÊM 2026-08-18 (arch-review coord-2026-08-18 required_change #3) —
# "wags-autofix-review-needed:": nhánh dispatch.sh exit=5 (đã lên lịch tự resume / tự
# fallback). Pipeline DỪNG trước bước arch-review nên vòng fix đó còn NỢ một lượt review;
# bản cũ ghi nợ đó bằng event `status` "wags-autofix-resume-pending:" — MỒ CÔI, không
# checker nào đọc, tức nợ biến mất im lặng. Giờ đi đường question để người thấy trong báo
# cáo ops hằng ngày, và nằm trong tuple này để KHÔNG kéo COORD_WARN dispatch lại chính
# vòng fix vừa dừng (nó đang tự chạy tiếp — re-dispatch là chạy song song với chính nó).
WAGS_SELF_Q_PREFIXES = ("wags-fix-not-confirmed:", "wags-arch-review-inconclusive:",
                        "wags-autofix-review-needed:")
# Cửa sổ ÂN HẠN trước khi 1 câu hỏi trở thành ROUTABLE (được phép kéo dispatch wags_autofix).
# Sự cố THẬT 2026-08-17: Taylor đăng question `hybrid-fill-live-deadline-20260817` lúc
# 02:01:45Z (đang trả lời chính dispatch mà Mike vừa giao lúc 02:00:06Z); một lần chạy
# ops_health_check lúc 02:06:15Z thấy nó "CHƯA có answer" sau ĐÚNG 4 phút 31 giây và dispatch
# job Wags coord-2026-08-17 (Opus). Mike đăng answer lúc 02:06:56Z — tức người phụ trách ĐANG
# xử lý, chỉ là chưa kịp ghi bus. Toàn bộ job Wags đó là false alarm thuần.
# Vì sao là lỗi CHECKER chứ không phải lỗi Taylor/Mike: "chưa có answer sau vài phút" KHÔNG
# mang thông tin gì về việc câu hỏi có bị bỏ rơi hay không — không con người nào, không agent
# nào trả lời trong khung đó. Điều kiện dispatch phải là "đã có đủ thời gian trả lời mà vẫn
# im", không phải "tại thời điểm quét chưa thấy answer" (đúng họ §28 coding_guidelines: đọc
# một BIỂU DIỄN tức thời rồi kết luận về sự thật bền).
# 60 phút: ân hạn chỉ an toàn khi vẫn còn lượt quét theo lịch TRƯỚC mốc ts+48h. Cron thật là
# 2 lần/ngày 01:20 + 05:45 UTC, CHỈ T2-T6 (`20 1 * * 1-5`, `45 5 * * 1-5`); khe hở lớn nhất
# T6 05:45Z → T2 01:20Z = 67h35 > cutoff 48h. Vì vậy KHÔNG áp dụng ân hạn nếu không còn lượt
# quét Mon-Fri nào trước ts+48h; nếu cứ hoãn, question trong T6 04:45-05:45Z sẽ rơi thẳng vào
# aged_q [WARN-ONLY] mà không bao giờ được dispatch (xem selfcheck ca 8d).
# KHÔNG im lặng: câu hỏi trong ân hạn vẫn IN ra báo cáo, chỉ mang marker [WARN-ONLY] để không
# rơi vào COORD_WARN (che giấu = đúng thứ mọi comment khác trong check #5 này đang chống).
QUESTION_GRACE_MIN = 60
# Hai hằng số này phải khớp crontab thật. Nếu cron đổi, cập nhật cả selfcheck ca 8d — không để
# ân hạn tự nới rộng khe cuối tuần của kênh escalate question.
CRON_SCAN_UTC_TIMES = ((1, 20), (5, 45))

def _future_scan_before(limit_ts):
    # Có ít nhất 1 lượt quét Mon-Fri diễn ra SAU lượt quét hiện tại và TRƯỚC ts+48h không.
    # Check #5 chạy TAY bất kỳ lúc nào nên phải xét tương đối với `_now`, không chỉ đếm lịch.
    day = _now.date()
    for offset in range(3):
        for hour, minute in CRON_SCAN_UTC_TIMES:
            cand = dt.datetime.combine(day + dt.timedelta(days=offset),
                                       dt.time(hour, minute), tzinfo=dt.timezone.utc)
            if cand.weekday() < 5 and _now < cand < limit_ts:
                return True
    return False

inbox_dir = os.path.join(wc_root, "mike", "bus", "inbox")
pending_q = []
pending_q_fresh = []     # <QUESTION_GRACE_MIN phút tuổi — hiện trong báo cáo, KHÔNG routable
pending_q_wagsfix = []   # xem chú thích ở khối "if pending_q_wagsfix" phía dưới
# Câu hỏi ĐÃ được triage và kết luận "chỉ NGƯỜI quyết được, không có fix tooling" →
# vẫn HIỆN đầy đủ trong báo cáo nhưng KHÔNG spawn wags_autofix nữa (xem ACK_PREFIX).
pending_q_needs_human = []
pending_q_meta = []      # (agent, topic, ts) song song pending_q — chỉ để dựng dòng HINT
closure_cands = []       # (agent, topic, ts) mọi finding/answer/decision — chỉ để HINT
aged_q = []
aged_q_meta = []         # (agent, topic, ts) song song aged_q — owner-hint PHẢI phủ cả >48h,
                          # đúng lúc bằng chứng "chưa ai nhận" mạnh nhất (xem khối owner-hint).
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
    resolvers = []          # (agent, topic, ts, explicit refs from payload.resolves)
    acks = []                # (topic_câu_hỏi_được_ack, a_ts, hạn_ack, suppress_days) — xem ACK_PREFIX
    # Tập agent-id CÓ THẬT trên bus. Dùng để quyết định một chuỗi dạng "X/y" là
    # "Agent/topic" hay chỉ là topic tự nó có dấu '/'. Lấy từ tên file inbox chứ KHÔNG
    # hardcode: fleet thêm agent thì tập này tự đúng. Xem `_split_ref`.
    known_agents = {_agent_of(p) for p in files}
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
                             a_ts, a_ts + dt.timedelta(days=_sd), _sd))
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
                    resolvers.append((agent_p, t, r_ts, _explicit))
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
                   for _ra, r, r_ts, explicit in resolvers)
    def _split_ref(s):
        """Chuẩn hoá một tham chiếu câu hỏi về cặp (agent, topic) rồi mới so sánh.

        Vì sao KHÔNG dùng `"/" in s` làm tiêu chí "đã ở dạng Agent/topic" (bản 8e9affc3 làm
        vậy, arch-review round 3 bắt được, tái lập cả 2 chiều):
        - FALSE-PENDING trên topic TỰ NÓ chứa '/': `selfcheck-red: mike/bin/job_cancel_guard
          _selfcheck.py` — lớp câu hỏi ĐÔNG NHẤT trong backlog thật — bị coi là "đã qualified"
          nên không bao giờ ghép được với dạng còn lại ⇒ rollup kẹt vĩnh viễn, đốt 1 job
          wags_autofix/ngày, đúng vòng lãng phí `rollup_of` ra đời để diệt.
        - FALSE-CLOSED chéo agent: sub TRẦN ["con-B"] + resolves ["Taylor/con-B"] khớp nhau
          vì chỉ MỘT bên có '/', trong khi câu hỏi thật là `Mike/con-B` ⇒ đóng escalation của
          agent này bằng quyết định của agent KHÁC. MIKE.md hứa "khác agent thì không khớp"
          nhưng lời hứa đó chỉ đúng khi CẢ HAI bên qualified.

        Cách đúng: tiền tố chỉ được bóc khi nó là agent-id CÓ THẬT trên bus (`known_agents`)
        — nên "selfcheck-red: mike/bin/x.py" là topic TRẦN, không phải "Agent/topic". Bên
        không khai agent trả về None (khác hẳn "agent rỗng"); phần so agent nằm ở `_same_ref`.
        Vẫn là exact-match trên phần topic, KHÔNG nới về substring.
        """
        if "/" in s:
            pfx, rest = s.split("/", 1)
            if pfx in known_agents and rest.strip():
                return pfx, rest.strip()
        return None, s      # None = chuỗi KHÔNG khai agent (khác với "khai agent rỗng")
    def _same_ref(a, a_agent, b):
        """`a` = topic con trong rollup_of (thuộc agent đăng escalation tổng = a_agent);
        `b` = một tham chiếu phía đóng (topic của resolver, hoặc 1 phần tử `resolves`).

        Ràng buộc agent chỉ áp khi bên đó THẬT SỰ khai agent. Lý do: quy ước đóng câu hỏi
        trên bus KHÔNG yêu cầu cùng agent — `_resolved` (đường chính) so topic-string thuần,
        và người đóng THƯỜNG là agent khác người hỏi. Bắt agent phải trùng ở CẢ topic của
        resolver sẽ phá đúng ca đóng thông thường (4 assertion 15b/15c đỏ khi thử).
        Nhưng khi một bên khai tường minh "Taylor/x" thì đó là lời khai VỀ CÂU HỎI NÀO, và
        lời khai đó phải được tôn trọng — nếu không, sub trần ["con-B"] của Mike bị đóng
        bằng resolves ["Taylor/con-B"] (false-CLOSED chéo agent, arch-review round 3).
        """
        a_ag, a_tp = _split_ref(a)
        b_ag, b_tp = _split_ref(b)
        if a_tp != b_tp:
            return False
        a_ag = a_ag or a_agent      # sub trần = câu hỏi của chính agent đăng tổng
        return b_ag is None or not a_ag or b_ag == a_ag

    def _resolved_exact(q_topic, q_ts, q_agent=""):
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
                   (_same_ref(q_topic, q_agent, r) or
                    any(_same_ref(q_topic, q_agent, e) for e in explicit))
                   for _r_a, r, r_ts, explicit in resolvers)
    rollup_misses = {}      # (agent, topic, ts) → [topic con CHƯA khớp] — chỉ để in gợi ý
    def _rollup_resolved(rec, q_ts, q_agent=""):
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
        if not isinstance(raw, list) or not raw:
            return False
        # Phần tử rỗng/sai kiểu ⇒ FAIL-CLOSED cả câu hỏi tổng, KHÔNG lọc lặng. Bản cũ lọc
        # (`if str(s).strip()`) nên `["con-A", ""]` chạy `all()` trên ÍT con hơn số đã khai:
        # người viết tưởng đang chốt 2 con, cơ chế chỉ kiểm 1 rồi đóng tổng — false-CLOSED
        # do lỗi CHÍNH TẢ, không có một dòng cảnh báo nào (arch-review round 3 tái lập được).
        subs = []
        for s in raw:
            if not isinstance(s, str) or not s.strip():
                return False
            subs.append(s.strip())
        # Dạng "Agent/topic" được xử lý DUY NHẤT một chỗ: `_split_ref` bên trong `_same_ref`
        # (xem docstring ở đó). Chỗ này TUYỆT ĐỐI không tự bóc tiền tố — bóc hai lần là ra
        # đúng ca false-CLOSED chéo agent.
        miss = [s for s in subs if not _resolved_exact(s, q_ts, q_agent)]
        if miss:
            # Fail-closed thì ĐÚNG nhưng IM LẶNG: người đăng escalation tổng không có cách
            # nào biết con nào chưa khớp (sai chính tả? sai agent? con đóng bằng hậu-tố?),
            # nên cứ để nó pending mãi. Ghi lại để in gợi ý một dòng bên dưới.
            rollup_misses[(q_agent, rec.get("topic"), rec.get("ts"))] = miss
            return False
        return True
    def _acked(q_agent, q_topic, q_ts):
        # Khớp CHÍNH XÁC (không substring như _resolved): ack chỉ tắt auto-dispatch nên sai
        # sót về phía "vẫn dispatch" là an toàn; nới lỏng match ở đây thì 1 ack topic ngắn
        # có thể tắt dispatch cho câu hỏi khác chưa ai xem. Chấp nhận cả dạng "Agent/topic"
        # (đúng chuỗi checker in ra) để người copy thẳng từ báo cáo.
        if not q_topic:
            return False
        # Hai chế độ, tuỳ có khai `suppress_days` hay không:
        # (a) suppress_days=0/không khai ⇒ hành vi cũ, VĨNH VIỄN cho ĐÚNG instance đã ack
        #     (a_ts >= q_ts) — không có "hết hạn" nào cho ca này (fixture case_triaged_
        #     needs_human_ack dựa đúng vào tính vĩnh viễn này, không được đổi).
        # (b) suppress_days=N>0 ⇒ BUG (arch-review NEEDS_CHANGES, coord-2026-09-03): bản cũ
        #     so `a_until >= q_ts` (q_ts = ts CỦA CÂU HỎI, cố định) — với câu hỏi KHÔNG bị
        #     cron phát lại (ts không đổi qua các lần chạy check), ack luôn đăng sau câu hỏi
        #     (a_ts > q_ts) nên a_until = a_ts + N >= a_ts > q_ts LUÔN đúng bất kể N ⇒ ack
        #     vĩnh viễn dù khai suppress_days — "N ngày rồi tự nổi lại" chưa từng hoạt động
        #     cho câu hỏi không tái phát (ca thật: Winston/deposit-rate-refresh-question).
        #     Sửa: so `a_until` với THỜI ĐIỂM CHẠY CHECK (_now) — đúng ý định "phủ N ngày
        #     kể từ lúc ack", còn khớp nguyên fixture case_ack_suppress_days_window (ack có
        #     thể đăng TRƯỚC câu hỏi để phủ 1 lần cron phát lại tới sau, vì nhánh này không
        #     đòi a_ts >= q_ts nữa — chỉ còn đòi cửa sổ chưa hết hạn theo NOW).
        want = (q_topic, f"{q_agent}/{q_topic}")
        return any(a in want and
                   ((sd <= 0 and a_ts >= q_ts) or (sd > 0 and a_until >= _now))
                   for a, a_ts, a_until, sd in acks)
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
            if _resolved(rec.get("topic"), ts_dt, agent) or _rollup_resolved(rec, ts_dt, agent):
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
                elif ((_now - ts_dt).total_seconds() < QUESTION_GRACE_MIN * 60
                      and _future_scan_before(ts_dt + dt.timedelta(hours=48))):
                    # Ân hạn: quá mới để kết luận "không ai trả lời" (xem QUESTION_GRACE_MIN),
                    # và sẽ còn lượt quét theo lịch TRƯỚC ts+48h để bắt nếu thật sự bị bỏ rơi.
                    # Đặt SAU 2 nhánh trên có chủ đích — chúng phân loại theo BẢN CHẤT câu hỏi
                    # (tự-sinh / đã triage), ân hạn chỉ nói về TUỔI, không được ghi đè phân loại.
                    pending_q_fresh.append(
                        f"{agent}/{rec.get('topic')} "
                        f"({int((_now - ts_dt).total_seconds() // 60)}m)")
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
                # Câu hỏi đã có ack `triaged-needs-human:` = ĐÃ TRIAGE, đang PARK chờ NGƯỜI
                # quyết. Vẫn liệt kê ở dòng "TREO LÂU" (nó đang mở thật, người cần thấy),
                # nhưng KHÔNG đưa vào nguồn owner-hint: gợi ý "dispatch <agent>" cho một câu
                # hỏi mà kết luận đã là "chỉ người quyết được" là WARN RÁC lặp 2 lần/ngày
                # VĨNH VIỄN — và nhiễu định kỳ chính là thứ làm cảnh báo thật bị bỏ qua.
                # Nhánh <48h đã lọc đúng như vậy sẵn (đi vào pending_q_needs_human, KHÔNG vào
                # pending_q_meta); nhánh >48h thiếu ⇒ mở rộng owner-hint sang aged (round 2)
                # làm lộ ra. arch-review round 2, required_change #2.
                if not _acked(agent, str(rec.get("topic") or ""), ts_dt):
                    aged_q_meta.append((agent, str(rec.get("topic") or ""), ts_dt))
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
    # Câu hỏi TỔNG khai `rollup_of` mà không đóng được: nói rõ CON NÀO chưa khớp. Không có
    # dòng này thì fail-closed đúng nhưng câm — người đăng escalation không phân biệt được
    # "con thật sự chưa ai quyết" với "gõ sai tên con / sai agent / con đóng bằng hậu-tố
    # trạng thái (rollup cố ý không nhận, xem MIKE.md)", nên nó pending mãi và mỗi ngày đốt
    # thêm 1 job wags_autofix. Chỉ GỢI Ý, không đổi routing dòng WARN ở trên.
    for (_ra, _rt, _), _miss in sorted(rollup_misses.items(), key=lambda kv: str(kv[0])):
        if _rt and any(_rt in str(_p) for _p in pending_q):
            W(f"{WARN_ONLY} rollup_of của '{_ra}/{_rt}': {len(_miss)} topic con CHƯA khớp "
              f"resolver nào — {_miss}. Kiểm 4 khả năng theo thứ tự: (1) con chưa ai quyết "
              f"thật; (2) chuỗi con gõ khác topic thật (phải TRÙNG KHÍT, kể cả tiền tố "
              f"'Agent/'); (3) con đóng bằng hậu-tố trạng thái ('<topic>-question-closed') "
              f"— rollup CỐ Ý không nhận dạng này, phải tự đăng answer giữ nguyên topic tổng; "
              f"(4) con THUỘC AGENT KHÁC '{_ra}' (người đăng tổng) mà lại viết TRẦN — dù chuỗi "
              f"trùng khít 100%, resolver phải ghi đủ 'Agent/topic' cho con không phải của "
              f"chính '{_ra}', xem MIKE.md § Escalation TỔNG.")
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
elif os.path.isdir(inbox_dir) and not pending_q_wagsfix and not pending_q_needs_human \
        and not pending_q_fresh:
    # Điều kiện isdir là BẮT BUỘC: không quét được ≠ quét xong và sạch (xem `else` ở trên).
    # `not pending_q_fresh` cũng BẮT BUỘC: có câu hỏi mới tinh chưa ai trả lời mà in ✅ "không
    # có câu hỏi nào đang chờ" là nói SAI — ân hạn hoãn DISPATCH, không xoá sự tồn tại.
    OK("Không có câu hỏi (question) nào đang chờ xử lý trong 48h qua.")
if pending_q_fresh:
    W(f"{WARN_ONLY} {len(pending_q_fresh)} câu hỏi (question) VỪA ĐĂNG (<{QUESTION_GRACE_MIN}"
      f" phút) chưa có answer — QUÁ MỚI để kết luận bị bỏ rơi, KHÔNG dispatch lượt này; lượt "
      f"kiểm tra kế tiếp sẽ tự đưa vào diện xử lý nếu vẫn im: {pending_q_fresh}")
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
# Dòng CHỦ SỞ HỮU: câu hỏi mà topic tự khai người phụ trách theo quy ước "…-needs-<agent>".
# Sự cố THẬT 2026-08-27→28: Wags đăng 4 question kết thúc bằng `-needs-taylor` lúc 13:33-13:42Z.
# Hệ quả TỰ ĐỘNG duy nhất của một câu hỏi treo là COORD_WARN → dispatch **Wags**; không có
# đường nào đưa nó tới Taylor. Cả 4 nằm im 19 giờ, rồi đốt đúng 1 job wags_autofix để Wags
# kết luận lại y hệt điều nó đã tự viết hôm trước — trong đó có 1 mục URGENT (BAF đã BANNED
# trong KNOWLEDGE.md nhưng 2 bản sao hằng số trong code chưa cập nhật ⇒ chạm lựa chọn live).
# Vì sao chỉ IN chứ KHÔNG tự dispatch peer: auto-dispatch chéo agent theo một chuỗi trong
# topic là tự phục hồi mù (user chốt 2026-08-03: lỗi mà đọc output là thấy thì đừng xây
# auto-retry) — và người phụ trách ở đây làm việc trong domain trading, nơi Wags/checker
# KHÔNG được tự kích hoạt. Dòng này chỉ biến "im lặng" thành "một lệnh copy được".
# NGUỒN = pending_q_meta (<48h) VÀ aged_q_meta (>48h) — bản đầu (coord-2026-08-28 round 1) chỉ
# phủ <48h, nghĩa là đúng lúc một câu hỏi -needs-<agent> treo LÂU NHẤT (bằng chứng "không ai
# nhận" mạnh nhất) thì dòng gợi ý lại BIẾN MẤT. arch-reviewer required_change #2, round 2, đã sửa.
_AGENTS_DIR = os.path.join(wc_root, "mike", "agents")
_KNOWN_AGENTS = {}
if os.path.isdir(_AGENTS_DIR):
    for _d in sorted(os.listdir(_AGENTS_DIR)):
        if not os.path.isdir(os.path.join(_AGENTS_DIR, _d)):
            continue
        # KHÔNG lọc "wt-*" (git worktree tạm) ở đây — điều kiện đó là CODE CHẾT, không phải
        # guard: token owner luôn là SEGMENT ĐẦU trước dấu '-' (`_tail[1].split("-")[0]` bên
        # dưới), nên với worktree tên `wt-<id>` token parse ra đúng chữ "wt" và không bao giờ
        # bằng khoá `wt-<id>`. Đo được: thêm lại điều kiện đó → selfcheck KHÔNG đổi một
        # assertion nào (mutation MU4, cố ý "expect survive"). Bất biến này được ghim bằng
        # ca 9g thay cho một dòng lọc không canh gì. arch-review round 2, required_change #4.
        _KNOWN_AGENTS[_d.lower()] = _d
_owner_q = {}
for _qa, _qt, _ in pending_q_meta + aged_q_meta:
    _tail = _qt.rsplit("-needs-", 1)
    if len(_tail) != 2:
        continue
    # Bỏ hậu tố mức-độ tuỳ ý người viết thêm (…-needs-taylor-urgent) rồi lấy token đầu, VÀ
    # cắt tiếp tại ':' / '/' — quy ước ack thật trên bus là `triaged-needs-human:<Agent>/<topic>`
    # (dạng không-dấu-cách, 6 topic thật trên bus hôm nay). Không cắt thì token parse ra
    # `human:Taylor/vol`, KHÔNG bằng "human" trong phép so tuyệt đối ngay dưới ⇒ rơi vào nhánh
    # "không khớp agent nào" và in WARN rác cho đúng loại câu hỏi đã được park cho NGƯỜI.
    # arch-review round 2, required_change #1.
    _own_raw = _tail[1].split("-")[0].split(":")[0].split("/")[0].strip()
    if not _own_raw or _own_raw.lower() in ("human", "user"):
        continue      # "needs-human/user" đã có kênh riêng (ACK_PREFIX) — không trùng lặp.
    # Gom KHÔNG phân biệt hoa-thường (người viết topic gõ tuỳ ý); tên IN RA lấy từ
    # _KNOWN_AGENTS (case chuẩn của agent thật), không phải nguyên văn người viết topic.
    _owner_q.setdefault(_own_raw.lower(), [_own_raw, []])[1].append(f"{_qa}/{_qt}")
for _own_key, (_own_raw, _qs) in sorted(_owner_q.items()):
    _canon = _KNOWN_AGENTS.get(_own_key)
    if _canon:
        # Không bọc <> quanh tên agent đã biết chắc — chỉ <việc> còn là chỗ người dùng phải tự
        # điền mới cần placeholder; in thẳng tên thật thì lệnh mẫu copy-paste được ngay.
        W(f"{WARN_ONLY} {len(_qs)} câu hỏi trên TỰ KHAI người phụ trách là '{_canon}' "
          f"(quy ước topic '…-needs-<agent>') — checker KHÔNG bao giờ tự dispatch chéo agent, "
          f"nên nếu chưa ai gọi thì nó nằm im. Kiểm bằng `bin/jobs.sh list` rồi gọi tường minh: "
          f"DISPATCH_FROM=Wags bin/dispatch.sh {_canon} \"<việc>\" --bg. Đóng bằng `answer`/"
          f"`decision` GIỮ NGUYÊN topic gốc: {_qs}")
    else:
        # Token không khớp agent thật nào (topic gõ sai, hoặc hậu tố "-needs-" không nói về
        # agent) — KHÔNG in lệnh dispatch cho một agent không tồn tại, chỉ nêu sự kiện.
        W(f"{WARN_ONLY} {len(_qs)} câu hỏi trên khai chủ '{_own_raw}' (quy ước topic "
          f"'…-needs-<agent>') nhưng KHÔNG khớp agent nào trong {_AGENTS_DIR} — cần người tự "
          f"tra, KHÔNG in lệnh dispatch: {_qs}")
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
    import hashlib as _hl
    # Sidecar ĐÃ-XỬ-LÝ (bin/bus_rejected_resolve.py ghi): khoá = sha256 DÒNG THÔ. File pháp
    # y append-only KHÔNG được sửa, nên "đã khôi phục event lên bus rồi" phải nói ở chỗ
    # khác — không có nó, một bản ghi đã xử lý xong vẫn báo động lặp đủ 24h (ca thật
    # 2026-08-18: bản ghi Taylor 08-17T16:49 đã được ghi lại lên bus 3 lần, checker vẫn
    # dựng lại cùng cảnh báo ở lần chạy sau). Sidecar hỏng/thiếu ⇒ coi như KHÔNG có gì được
    # xử lý (fail-loud: thà báo động thừa còn hơn nuốt một event mất thật).
    _qdone = set()
    _qrf = os.path.join(wc_root, "mike", "bus", "_rejected_resolved.jsonl")
    if os.path.exists(_qrf):
        try:
            with open(_qrf, encoding="utf-8", errors="replace") as _f:
                for _ln in _f:
                    try:
                        _qdone.add(json.loads(_ln)["key"])
                    except Exception:
                        continue
        except Exception:
            _qdone = set()
    _q24, _qtot, _qbad, _qres24 = [], 0, 0, 0
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
                        if _hl.sha256(_ln.encode("utf-8", "replace")).hexdigest() in _qdone:
                            _qres24 += 1
                        else:
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

        # ỨNG VIÊN RETRY — 6/6 ca cách ly tính tới 2026-08-24 đều được chính agent ghi lại
        # thành công trong vòng 47 giây, nhưng thông điệp cũ không nói điều đó nên mỗi ca đẻ
        # ra một job ops-autofix chỉ để đi tra lại đúng việc này. Đây là GỢI Ý bằng chứng,
        # KHÔNG phải auto-resolve: sidecar vẫn phải do người/agent đánh dấu sau khi đối chiếu
        # nội dung (hàng đợi này là pháp y — xem incident 2026-08-18-rejected-queue-no-closure).
        # Toàn bộ khối bọc try: thiếu bus/inbox (harness selfcheck) ⇒ không có gợi ý, không nổ.
        _qcand = []
        try:
            for _r in _q24:
                _a = _r.get("argv") if isinstance(_r.get("argv"), list) else []
                _ag = str(_a[0]) if _a else ""
                # trace_id là tham số CUỐI của append_event.sh. Khi payload bị word-split
                # (argc>5 — dạng cách ly PHỔ BIẾN NHẤT) nó vẫn nằm ở CUỐI, còn _a[4] chỉ là
                # một mảnh payload. Bám cứng _a[4] ⇒ đúng ca word-split không bao giờ khớp
                # ứng viên và checker khẳng định "MẤT THẬT" (ca thật 2026-08-31: 13 tham số,
                # event 2ceafcdb lên bus +42s vẫn bị báo mất). Thêm topic (_a[2] — KHÔNG bị
                # ảnh hưởng bởi split trong payload) làm bằng chứng thứ hai; khớp 1 trong 2
                # là đủ, không có bằng chứng nào thì KHÔNG nhận bừa event đầu tiên trong cửa sổ.
                _tr = str(_a[-1]) if len(_a) >= 5 else ""
                _tp = str(_a[2]) if len(_a) >= 3 else ""
                _ets = str(_r.get("ts") or "")
                _fp = os.path.join(wc_root, "mike", "bus", "inbox", _ag + ".jsonl")
                if not (_ag and _ets and os.path.exists(_fp)):
                    continue
                _t0 = _dt.datetime.strptime(_ets, "%Y-%m-%dT%H:%M:%SZ")
                _t1 = (_t0 + _dt.timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
                with open(_fp, encoding="utf-8", errors="replace") as _bf:
                    for _bl in _bf:
                        try:
                            _be = json.loads(_bl)
                            _bts = str(_be.get("ts") or "")
                            if not (_ets < _bts <= _t1):
                                continue
                            if not ((_tr and str(_be.get("trace_id") or "") == _tr)
                                    or (_tp and str(_be.get("topic") or "") == _tp)):
                                continue
                            _qcand.append(
                                f"{_ag}/{_ets} → {_bts} event {str(_be.get('event_id'))[:8]} "
                                f"topic {str(_be.get('topic'))[:60]}")
                            break
                        except Exception:
                            continue
        except Exception:
            _qcand = []
        _who = sorted({_q_who(_r) for _r in _q24})
        _why = sorted({str(_r.get("reason") or "?").split("\n")[0][:110] for _r in _q24})
        W(f"append_event.sh đã CÁCH LY {len(_q24)} bản ghi trong 24h qua "
          f"({_qtot} bản ghi trong file hiện tại"
          f"{f', {_qres24} ca khác trong 24h đã được đánh dấu xử lý' if _qres24 else ''}"
          f"{f', {_qbad} dòng không parse được' if _qbad else ''}) "
          f"— đây là event KHÔNG BAO GIỜ lên bus: guard của append_event.sh từ chối và "
          f"phần lớn call site nuốt stderr nên agent tưởng đã ghi thành công. "
          f"NGUYÊN NHÂN KHÁC NHAU THEO TỪNG CA (word-split, JSON không hợp lệ, payload cụt…) "
          f"— đọc đúng `Lý do` dưới đây, đừng mặc định là lỗi quote. "
          f"Agent: {_who}. Lý do: {_why}. "
          f"Xem `tail bus/_rejected.jsonl`; sửa đúng nguyên nhân ở call site rồi ghi LẠI event "
          f"(hàng đợi này là PHÁP Y, không ai tự phát lại — payload hỏng phát lại vẫn hỏng)."
          + (f" ỨNG VIÊN RETRY đã lên bus (cùng agent + cùng trace_id, ≤15 phút sau): "
             f"{_qcand} — nhiều khả năng agent đã TỰ ghi lại; ĐỐI CHIẾU nội dung rồi đánh dấu "
             f"bằng `bin/bus_rejected_resolve.py --index N --by <ai> --note ...`, đừng bỏ qua "
             f"bước đánh dấu (không đánh dấu = báo động lặp lại suốt 24h)." if _qcand else
             " KHÔNG tìm thấy ứng viên retry nào trên bus trong 15 phút sau đó — khả năng cao "
             "event MẤT THẬT, phải dựng lại nội dung từ argv rồi ghi lại."))
    elif _qtot:
        OK(f"Hàng đợi cách ly append_event.sh: {_qtot} bản ghi cũ trong file hiện tại, "
           f"24h qua không có ca CHƯA XỬ LÝ"
           f"{f' ({_qres24} ca mới đã được đánh dấu xử lý)' if _qres24 else ''}.")
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
        # 2026-09-04: mốc CSV đứng yên KHÔNG đồng nghĩa cron chưa chạy. refresh_deposit_rate_vn.sh
        # (cron ngày 3 hàng tháng) cố ý KHÔNG ghi số khi nguồn mâu thuẫn — nó escalate bus question
        # và giữ nguyên giá trị live. Bảo người xử lý "chạy refresh_deposit_rate_vn.sh" trong tình
        # huống đó là chỉ sai hướng (chạy lại sẽ escalate lại). Đọc ARTIFACT — log run gần nhất —
        # rồi mới nói nguyên nhân (§28 vắng-mặt-≠-chưa-làm, §29 không hardcode chẩn đoán).
        dep_runs = sorted(glob.glob(os.path.join(wc_root, "data", "refresh_deposit_rate_vn_*.log")))
        dep_hint = ("Chạy refresh_deposit_rate_vn.sh (nhắc) rồi append_deposit_rate.py để cập nhật.")
        if dep_runs:
            try:
                dep_tail = open(dep_runs[-1], encoding="utf-8", errors="replace").read()
                dep_run_days = (today_d - _date.fromtimestamp(os.path.getmtime(dep_runs[-1]))).days
                if "Escalated instead of writing a number" in dep_tail:
                    dep_hint = (f"KHÔNG phải cron hỏng: {os.path.basename(dep_runs[-1])} cho thấy job "
                                f"đã chạy {dep_run_days} ngày trước và ESCALATE đúng thiết kế (nguồn mâu "
                                f"thuẫn) — đang chờ NGƯỜI quyết qua bus question "
                                f"Winston/deposit-rate-refresh-question. Chạy lại sẽ escalate lại.")
                elif "refresh DONE" in dep_tail:
                    dep_hint = (f"Job đã chạy {dep_run_days} ngày trước ({os.path.basename(dep_runs[-1])}) "
                                f"nhưng CSV không đổi — đọc log đó trước khi chạy lại.")
            except Exception as _e:
                dep_hint += f" (không đọc được log run gần nhất: {type(_e).__name__}: {_e})"
        W(f"Lãi suất tiết kiệm (deposit_rate_vn) đã {dep_age} ngày chưa refresh "
          f"(mốc cuối {dep_last}, {dep_kind}) — input rating_8l NEUTRAL tilt sống. " + dep_hint)
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
# CHECK9_BEGIN — marker ỔN ĐỊNH (giống CHECK5/10/11/12): bin/ops_health_check_selfcheck.py trích
# ĐÚNG khối giữa CHECK9_BEGIN/CHECK9_END rồi chạy nó trên thư mục retro giả. Đổi/xoá marker ⇒
# selfcheck FAIL ngay.
#
# Cửa sổ 7 NGÀY, không phải 1 (sửa 2026-08-20, audit coord-2026-08-20 theo khuôn lỗi 08-18):
# bản cũ chỉ hỏi "có retro của HÔM QUA không". Nếu checker không chạy đúng ngày đó (cron chết,
# máy tắt), hoặc người đọc bỏ qua đúng báo cáo đó, thì hôm sau câu hỏi đã đổi sang ngày mới và
# lần retro bị mất KHÔNG BAO GIỜ được hỏi lại — cảnh báo tự bốc hơi thay vì tự đóng. Đây đúng
# gap `long_term_ops` arch-reviewer nêu 2026-08-20T01:29:01Z. Kênh ĐÓNG vẫn là artifact thật
# (file retro tồn tại ⇒ hết báo), nên quét rộng KHÔNG đẻ báo động lặp.
_retro_dir = os.path.join(wc_root, "mike", "kb", "incidents", "retro")
_RETRO_WINDOW_D = 7
# Sàn dưới = ngày retro CŨ NHẤT có thật trên đĩa: đừng bao giờ đòi retro của ngày trước khi cơ
# chế tồn tại (tự thích nghi, không cần chép ngày cứng vào code).
_retro_floor = None
try:
    _retro_have = sorted(re.findall(r"retro-(\d{4}-\d{2}-\d{2})\.md",
                                    " ".join(os.listdir(_retro_dir))))
    if _retro_have:
        _retro_floor = _date.fromisoformat(_retro_have[0])
except Exception:
    _retro_have = []
_retro_missing = []
for _i in range(1, _RETRO_WINDOW_D + 1):
    _d9 = today_d - _timedelta(days=_i)
    if _retro_floor is not None and _d9 < _retro_floor:
        continue
    if not os.path.exists(os.path.join(_retro_dir, f"retro-{_d9.isoformat()}.md")):
        _retro_missing.append(_d9.isoformat())
_retro_missing.sort()
if not _retro_have:
    lines.append("ℹ️ daily_retro.sh: chưa có entry RETRO nào trên đĩa — bỏ qua (chưa tới lần chạy đầu).")
elif _retro_missing:
    _yday9 = (today_d - _timedelta(days=1)).isoformat()
    _fresh9 = _yday9 in _retro_missing
    # ĐỪNG ĐOÁN NGUYÊN NHÂN — TRA LOG (coding_guidelines §28). Bản trước hardcode "nghi quoting
    # bug 08-01" vào thông điệp; hai lần liên tiếp nó dẫn autofix đi sai hướng: 2026-08-20 (lỗi
    # TRUYỀN TẢI API, script chạy trọn vẹn) và 2026-08-25 (HOST TẮT 08-24 15:30→08-25 09:45 ICT,
    # cron 00:30 không hề fire). Phân biệt được bằng đúng MỘT bit cơ khí: log daily_retro.log có
    # dòng START cho ngày cần review hay không. Có START ⇒ lỗi NẰM TRONG script/dispatch; không
    # START ⇒ script CHƯA BAO GIỜ chạy, tìm bug trong script là phí công.
    _log9 = os.path.join(wc_root, "mike", "logs", "daily_retro.log")
    _started9 = None
    if _fresh9:
        try:
            with open(_log9, "r", errors="replace") as _fh9:
                _started9 = (f"daily_retro START (reviewing {_yday9}" in _fh9.read())
        except OSError:
            _started9 = None
    if not _fresh9:
        _why9 = (" (KHÔNG gồm hôm qua — đây là (các) lần đã bị bỏ lỡ trước đó, bản check 1-ngày "
                 "cũ đã để trôi mất; vẫn là việc còn NỢ).")
    elif _started9 is True:
        _why9 = (f" (gồm HÔM QUA — logs/daily_retro.log CÓ dòng START cho {_yday9} ⇒ script ĐÃ "
                 "chạy nhưng không hoàn tất; nguyên nhân nằm TRONG chuỗi dispatch, đọc "
                 "logs/daily_retro_draft_*.log của đêm đó và phân lớp: usage-limit / lỗi truyền "
                 "tải API / Mike trả lạc đề).")
    elif _started9 is False:
        _why9 = (f" (gồm HÔM QUA — logs/daily_retro.log KHÔNG có dòng START cho {_yday9} ⇒ cron "
                 "00:30 ICT KHÔNG hề chạy: máy tắt hoặc cron không fire, KHÔNG phải bug trong "
                 "script. Xác nhận bằng `last -x` + mtime các file trong mike/logs/ quanh 00:30 "
                 "ICT TRƯỚC khi đi tìm bug; nếu đúng downtime thì mọi cron khác trong cùng cửa "
                 "sổ cũng đã bị bỏ lỡ.)")
    else:
        _why9 = (" (gồm HÔM QUA — KHÔNG đọc được logs/daily_retro.log để phân biệt 'script chạy "
                 "rồi chết' với 'cron không hề chạy'; kiểm thủ công, đừng giả định.)")
    W(f"daily_retro.sh THIẾU {len(_retro_missing)} entry RETRO trong {_RETRO_WINDOW_D} ngày qua: "
      f"{_retro_missing}" + _why9
      + " Viết bù entry để cảnh báo tự tắt.")
else:
    OK(f"daily_retro.sh: đủ entry RETRO cho {_RETRO_WINDOW_D} ngày qua "
       f"(mới nhất {(today_d - _timedelta(days=1)).isoformat()}).")
# CHECK9_END

# 9b. Pending decisions trong working memory phải có bus question backing (thêm 2026-08-16,
#     sau incident GDKHQ D1-D3 chỉ tracked trong memory — quyết định mất khi session restart).
#     Protocol: mọi pending user decision PHẢI được mở bus question trước khi vào working memory.
#     Pattern tìm: "## PENDING_DECISION: <topic>" trong kb/memory/Mike.md.
#     [WARN-ONLY]: chỉ báo cáo, không dispatch — đây là lỗi quy trình Mike tự sửa khi đọc báo cáo.
mike_mem_9b = os.path.join(wc_root, "mike", "kb", "memory", "Mike.md")
if os.path.exists(mike_mem_9b):
    try:
        import re as _re9b
        _mem9b = open(mike_mem_9b, encoding="utf-8").read()
        _pending9b = _re9b.findall(r'^##\s+PENDING_DECISION:\s*(.+)', _mem9b, _re9b.MULTILINE)
        if _pending9b:
            # Build set of open bus question topics (question posted, no answer/decision yet)
            _open9b = set()
            for _bd in [os.path.join(wc_root, "mike", "bus", "inbox"),
                        os.path.join(wc_root, "mike", "bus", "archive")]:
                if not os.path.isdir(_bd):
                    continue
                for _fn9b in sorted(os.listdir(_bd)):
                    if not _fn9b.endswith(".jsonl"):
                        continue
                    try:
                        for _ln9b in open(os.path.join(_bd, _fn9b), encoding="utf-8"):
                            try:
                                _ev9b = json.loads(_ln9b.strip())
                                _et9b = _ev9b.get("event_type", "")
                                _tp9b = _ev9b.get("topic", "")
                                if _et9b == "question":
                                    _open9b.add(_tp9b)
                                elif _et9b in ("answer", "decision"):
                                    _open9b.discard(_tp9b)
                            except Exception:
                                pass
                    except Exception:
                        pass
            _unbacked9b = [t.strip() for t in _pending9b if t.strip() not in _open9b]
            if _unbacked9b:
                W(f"[WARN-ONLY] check 9b: {len(_unbacked9b)} PENDING_DECISION trong working memory "
                  f"KHÔNG có bus question backing: {_unbacked9b}. "
                  f"Protocol vi phạm — quyết định chỉ trong memory sẽ mất khi session restart. "
                  f"Fix: bin/append_event.sh Mike question <topic> '{{...}}' TRƯỚC KHI viết vào memory.")
            else:
                OK(f"check 9b: {len(_pending9b)} PENDING_DECISION trong working memory, "
                   f"tất cả có bus question backing.")
    except Exception as _e9b:
        lines.append(f"ℹ️ check 9b: không đọc được Mike.md ({_e9b})")

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
import datetime as _dt
nte_file = os.path.join(wc_root, "mike", "logs", "notify_thread_errors.log")
if os.path.exists(nte_file) and (_time.time() - os.path.getmtime(nte_file)) < 86400:
    try:
        # Chỉ lấy dòng MỞ ĐẦU BẢN GHI (có timestamp) — thông điệp lỗi có thể tràn nhiều dòng
        # (discord_channel.sh in thêm danh sách tên hợp lệ), lấy dòng cuối thô sẽ ra đúng cái
        # đuôi vô nghĩa đó.
        _nte_all = [l for l in open(nte_file, encoding="utf-8", errors="replace").read().splitlines()
                    if re.match(r"^\d{4}-\d{2}-\d{2}T", l)]
    except Exception:
        _nte_all = []
    # Cửa sổ 24h phải áp lên TỪNG BẢN GHI, không chỉ lên mtime của FILE (sửa 2026-08-18).
    # File này append-only không xoay vòng ⇒ mtime chỉ nói "có ai đó vừa ghi", không nói bản
    # ghi NÀO mới. Trước sửa: một dòng tự-sửa mới (08-17) làm file tươi, rồi check đọc TOÀN BỘ
    # lịch sử và lôi lỗi thật từ 08-12 (6 ngày trước, đã xử lý) ra báo "TIN NHẮN ĐÃ BỊ NUỐT
    # trong 24h qua" — sai cả sự kiện lẫn mốc thời gian, và nhánh _nte_hard che luôn kết luận
    # ĐÚNG của bản ghi mới ("đã tự sửa, KHÔNG mất tin"). Bản ghi không đọc được giờ thì GIỮ
    # (fail-loud): không loại được khả năng nó vừa xảy ra.
    _nte_now = _time.time()

    def _nte_recent(l):
        try:
            return (_nte_now - _dt.datetime.fromisoformat(l.split(" ", 1)[0]).timestamp()) < 86400
        except Exception:
            return True

    _nte_lines = [l for l in _nte_all if _nte_recent(l)]
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
    elif not _nte_all:
        # File tươi nhưng KHÔNG có bản ghi nào có timestamp ⇒ không kết luận được (khác hẳn
        # với "có bản ghi nhưng đều cũ hơn 24h" — ca đó rơi xuống else và là OK thật).
        W(f"[WARN-ONLY] notify_thread_errors.log vừa được ghi trong 24h qua nhưng KHÔNG đọc "
          f"được bản ghi nào có timestamp — không kết luận được có mất tin hay không.")
    else:
        OK("notify_thread.sh: không có lỗi gửi Discord trong 24h qua.")
else:
    OK("notify_thread.sh: không có lỗi gửi Discord trong 24h qua.")
# CHECK10_END

# 10b. dispatch.sh TỪ CHỐI một prompt rỗng/quá ngắn (thêm 2026-08-21, job Wags_20260821_012007).
#      Guard ở dispatch.sh:116+ exit 1 và ghi 1 dòng vào logs/dispatch_rejected_prompts.log.
#      Nguồn sinh prompt rỗng có thể là NGƯỜI gõ (thấy stderr ngay, vô hại) hoặc MÁY — một
#      script tầng trên bọc `| tail -5` / `>> log` sẽ nuốt trọn exit 1. Không ai đọc file
#      này thì fail-loud lại thành fail-silent — đúng lỗi check 10 vừa bịt cho notify_thread.
#      WARN-only, cửa sổ 24h áp lên TỪNG BẢN GHI (không chỉ mtime file, bài học 2026-08-18).
# CHECK10B_BEGIN
drp_file = os.path.join(wc_root, "mike", "logs", "dispatch_rejected_prompts.log")
_drp_err = None
if os.path.exists(drp_file):
    try:
        _drp_all = [l for l in open(drp_file, encoding="utf-8", errors="replace").read().splitlines()
                    if re.match(r"^\d{4}-\d{2}-\d{2}T", l)]
    except Exception as e:
        # KHÔNG nuốt thành [] rồi in OK: file có mà đọc không được (perm/IO) thì đây là
        # "KHÔNG BIẾT", không phải "không có reject nào" — một detector chống fail-silent
        # mà tự fail-silent là vô nghĩa (arch-reviewer vòng 3).
        _drp_all, _drp_err = [], f"{type(e).__name__}: {e}"

    def _drp_recent(l):
        try:
            return (_time.time() - _dt.datetime.fromisoformat(l.split("\t", 1)[0]).timestamp()) < 86400
        except Exception:
            return True   # không đọc được ts thì GIỮ (fail-loud), không loại trừ

    _drp = [l for l in _drp_all if _drp_recent(l)]
    if _drp_err:
        W(f"[WARN-ONLY] KHÔNG ĐỌC ĐƯỢC logs/dispatch_rejected_prompts.log ({_drp_err}) — "
          f"không kết luận được có dispatch nào bị từ chối hay không; kiểm quyền/encoding file.")
    elif _drp:
        W(f"[WARN-ONLY] dispatch.sh đã TỪ CHỐI {len(_drp)} dispatch vì prompt rỗng/quá ngắn "
          f"trong 24h qua — nếu cột from= là một SCRIPT (không phải người gõ) thì có chỗ nào đó "
          f"đang dựng prompt rỗng và nuốt exit 1. Dòng cuối: {_drp[-1][:300]}")
    else:
        OK("dispatch.sh: không có dispatch nào bị từ chối vì prompt rỗng trong 24h qua.")
else:
    OK("dispatch.sh: không có dispatch nào bị từ chối vì prompt rỗng trong 24h qua.")
# CHECK10B_END

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

# 12. ccdb bridge NUỐT MẤT một wakeup one-shot (thêm 2026-08-17, job Wags_20260817_193233,
#     arch-review required_change #2). Bối cảnh: fix double-answer đổi scheduler thành XOÁ row
#     one_shot TRƯỚC khi chạy Claude. Đánh đổi có chủ ý — nhưng nó bỏ mất tính TỰ HỒI PHỤC:
#     trước đây thất bại giữa chừng thì row còn nguyên và tick sau chạy lại; giờ row đã mất,
#     KHÔNG ai retry. Mất 1 wakeup dispatch nghĩa là Mike ngồi chờ mãi một job đã xong.
#
#     Vì sao cần check này: mất wakeup là sự cố VÔ HÌNH theo đúng bản chất — "không có gì xảy
#     ra" trông y hệt "không có việc gì để làm". Scheduler đã ghi ERROR `ONE_SHOT_DROPPED`,
#     nhưng arch-reviewer grep ra ops_health_check.sh KHÔNG hề đọc log daemon ccdb (0 khớp cho
#     ccdb|scheduler|journalctl) ⇒ fail-loud mà không có người đọc thì vẫn là fail-silent, đúng
#     cái bẫy check #10 đã phải bịt một lần rồi.
#
#     [WARN-ONLY] có chủ ý: đây là sự cố ĐÃ XẢY RA RỒI, không sửa lại được bằng job autofix
#     (wakeup đã mất là mất); và cửa sổ 24h nghĩa là nó tự kêu tới hết ngày dù đã xử lý xong.
#     Việc của dòng này là LỌT VÀO MẮT NGƯỜI ĐỌC, không phải kích thêm 4 job/ngày.
# CHECK12_BEGIN — marker ỔN ĐỊNH (giống CHECK5/10/11): selfcheck trích đúng khối này chạy trên
# log giả. Đổi/xoá marker ⇒ bin/ops_health_check_selfcheck.py FAIL ngay.
try:
    _jr = subprocess.run(
        ["journalctl", "--user", "-u", "ccdb-mike", "--since", "-24h", "--no-pager", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    if _jr.returncode != 0:
        # KHÔNG nuốt: đọc không được journal thì ta KHÔNG BIẾT có mất wakeup hay không —
        # trạng thái đó phải trông khác hẳn "đã kiểm và sạch".
        W(f"[WARN-ONLY] check 12: không đọc được journal ccdb-mike (rc={_jr.returncode}: "
          f"{(_jr.stderr or '').strip()[:160]}) — KHÔNG kết luận được có wakeup one-shot nào "
          f"bị mất hay không.")
    elif not _jr.stdout.strip():
        # rc=0 + rỗng KHÔNG phải "sạch". `journalctl --user -u <tên sai>` trả ĐÚNG rc=0 với 0
        # byte (arch-review vòng 2 chạy thật: unit `definitely-not-a-unit` ⇒ rc=0). Daemon sống
        # ghi ~4800 dòng/24h, nên rỗng nghĩa là sai tên unit / sai scope (--user vs system) /
        # journal không giữ log — tức KHÔNG BIẾT, không phải "đã kiểm và sạch".
        W(f"[WARN-ONLY] check 12: journal ccdb-mike KHÔNG có dòng nào trong 24h qua — daemon "
          f"sống thì phải có log, nên đây là sai tên unit/scope hoặc daemon không ghi journal. "
          f"KHÔNG kết luận được có wakeup one-shot nào bị mất hay không.")
    else:
        # Hai marker, hai lớp sự cố khác nhau, đều là "đã claim + đã xoá row, không ai retry":
        # DROPPED = chưa từng vào Claude; INTERRUPTED = đã vào nhưng không chạy xong (restart
        # giữa lượt — chính lớp sự cố đẻ ra bản fix này, 4 lần ngày 2026-08-17).
        _dropped = [l for l in _jr.stdout.splitlines()
                    if "ONE_SHOT_DROPPED" in l or "ONE_SHOT_INTERRUPTED" in l]
        # Row còn sống nhưng KHÔNG giao được: retry mỗi 60s vô hạn, không TTL. Mike vẫn "chờ
        # mãi một job đã xong" y hệt ca mất wakeup, nên phải báo — nhưng báo RIÊNG vì cách xử
        # lý khác hẳn (ca này còn cứu được: un-archive thread là nó tự chạy).
        _unreach = [l for l in _jr.stdout.splitlines() if "has no reachable destination" in l]
        if _dropped:
            W(f"[WARN-ONLY] check 12: ccdb bridge MẤT {len(_dropped)} wakeup one-shot trong 24h "
              f"qua — job đã xong nhưng agent KHÔNG được đánh thức, không có gì retry. "
              f"Dòng cuối: {_dropped[-1][-300:]}")
        if _unreach:
            W(f"[WARN-ONLY] check 12: {len(_unreach)} wakeup one-shot KHÔNG giao được (thread "
              f"không có trong cache — thường do thread đã archive) trong 24h qua; row còn sống "
              f"và retry mỗi 60s nhưng agent VẪN chưa được đánh thức. Dòng cuối: "
              f"{_unreach[-1][-300:]}")
        if not _dropped and not _unreach:
            OK("check 12: ccdb bridge không mất wakeup one-shot nào trong 24h qua.")
except FileNotFoundError:
    W("[WARN-ONLY] check 12: không có lệnh journalctl — không giám sát được log ccdb bridge.")
except Exception as _e12:
    W(f"[WARN-ONLY] check 12: lỗi khi quét log ccdb bridge ({type(_e12).__name__}: "
      f"{str(_e12)[:120]}) — không kết luận được có mất wakeup hay không.")
# CHECK12_END

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
  PREFLIGHT_TAIL="$(PREFLIGHT_QUIET=1 bash "$ROOT/bin/preflight_check.sh" --account "$ACCOUNT" 2>/dev/null | grep -E '^\s*(✅|❌|⚠️)' | sed 's/^/  /')"
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

# 13. Hạn RÀ LẠI cờ forensic (user chốt 2026-09-04: "forensic cũng phải đưa thời hạn review
#     xử lý vào, không được để treo mãi"). Cờ forensic là lớp bảo vệ DUY NHẤT cho rủi ro
#     gian lận/thao túng — `adaptive_exclusion_v3_20260904.md` đã chứng minh gate tài chính
#     động KHÔNG thay được nó (false-positive 91,9%, DSR 0,14) — nên nó PHẢI ở lại, nhưng
#     không được phép nằm vĩnh viễn mà không ai nhìn lại.
#     Quá hạn → FAIL-CLOSED (giữ nguyên cờ) + escalate; KHÔNG tự gỡ. Chỉ chạy lượt ACCOUNT
#     đầu: danh sách cờ là FLEET-WIDE, per-account sẽ escalate trùng (cùng lý do như
#     ANOMALY_SCAN ở trên và như sự cố coord-SpaceX/coord-ZaloPay 2026-07-08).
FORENSIC_SUMMARY=""
FORENSIC_WARN=0
FORENSIC_CHECK="$ROOT/bin/forensic_flag_review_check.py"
if [ "$ACCOUNT" = "SpaceX" ] && [ -f "$FORENSIC_CHECK" ]; then
  # Bắt stderr LẠI để in ra khi hỏng, không ném vào /dev/null rồi đoán nguyên nhân (§29).
  FORENSIC_OUT="$(timeout 120 python3 "$FORENSIC_CHECK" 2>&1)"; FORENSIC_RC=$?
  if [ "$FORENSIC_RC" -eq 0 ]; then
    FORENSIC_SUMMARY="$FORENSIC_OUT"
  elif [ "$FORENSIC_RC" -eq 1 ]; then
    FORENSIC_WARN=1
    FORENSIC_SUMMARY="$FORENSIC_OUT"
  else
    FORENSIC_WARN=1
    FORENSIC_SUMMARY="⚠️ forensic-flag review check lỗi (rc=${FORENSIC_RC}) — KHÔNG kết luận được hạn rà lại. Lỗi thật: ${FORENSIC_OUT}"
  fi
fi
WARN_COUNT=$(( ${WARN_COUNT:-0} + ${FORENSIC_WARN:-0} ))

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
if [ -n "$FORENSIC_SUMMARY" ]; then
  MSG="${MSG}

Hạn rà lại cờ forensic (data/forensic_flags.csv — quá hạn KHÔNG tự gỡ cờ):
${FORENSIC_SUMMARY}"
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
# ROUTING_BEGIN
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
    # Truyền $OTHER_WARN, KHÔNG phải $MSG. Dòng "$MSG" là di sản commit a8e5b8a6 (2026-07-06),
    # thời điểm CHỈ có một nhánh autofix; khi nhánh COORD_WARN → Wags được tách ra sau đó,
    # lời gọi này không được sửa theo ⇒ Winston vẫn nhận TOÀN BỘ báo cáo, gồm cả triệu chứng
    # ĐIỀU PHỐI vừa được route sang Wags. Hệ quả đo được (Wags coord-2026-08-18): 2 ngày liên
    # tiếp Winston và Wags cùng chẩn đoán một câu hỏi tồn đọng — 08-17 (Winston_20260817_195843
    # kết luận "question Taylor/gdkhq-auto-accept còn mở thật" trong khi Wags_20260817_195842
    # được dispatch đúng cho việc đó) và 08-18 (Winston_20260818_001950 đóng 2 question gdkhq
    # lúc 00:21-00:22, Wags_20260818_001950 dispatch lúc 00:19:50 cho ĐÚNG 2 question đó).
    # Hai job Opus cho một triệu chứng. Truyền OTHER_WARN làm nhánh này ĐỐI XỨNG với nhánh
    # Wags ở trên (mỗi bên chỉ thấy domain của mình). ĐÁNH ĐỔI CÓ CHỦ ĐÍCH: Winston không còn
    # thấy các dòng NOT_APPROVED / "KHÔNG TÌM THẤY" (plan chưa duyệt) — vốn ĐÃ bị loại khỏi
    # routing có chủ đích vì là việc của user; chúng vẫn nằm nguyên trong báo cáo Trading Daily.
    "$ROOT/bin/ops_autofix.sh" "ops-health-${ACCOUNT}" "$OTHER_WARN (checker run: account=${ACCOUNT})" 2>/dev/null || true
  fi
# ROUTING_END
fi
