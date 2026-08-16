#!/usr/bin/env bash
# LIVE từ 2026-07-30 — arch-reviewer NEEDS_CHANGES(high)→11/12 áp dụng→user duyệt, cron hàng tuần
# đăng ký ở kb/cron_registry.md. Lần --apply đầu tay chạy: DELETE 1409 mục/0,86MB, ARCHIVE 720
# mục/0,52MB — verify: mike/logs top-level 1930→978 file.
#
# Audit + thiết kế: agents/Wags/research/fleet_housekeeping_audit_20260730.md (job Wags_20260730_112912)
#
# ─── Vì sao script này tồn tại ────────────────────────────────────────────────
# `mike/bus/` ĐÃ có cơ chế dọn (kb_nightly Phase 1b/1b2/1b3/1c, verified). `mike/logs/` KHÔNG có
# gì: 3080 file, 88% cũ hơn 7 ngày. Lợi ích chính là TOKEN (agent `ls`/glob dir 1928 entry ≈ 17K
# token), KHÔNG phải disk — cả logs/ chỉ 17 MB. Đừng dùng script này để giải quyết disk 91%; nguyên
# nhân đó là /workspace/kaffa_v2 45 GB, ngoài fleet (xem §5 báo cáo).
#
# ─── Ba nguyên tắc an toàn, đọc trước khi sửa ─────────────────────────────────
# 1. DRY-RUN LÀ MẶC ĐỊNH. Không có --apply thì không byte nào bị đổi.
# 2. ARCHIVE là mặc định, DELETE là ngoại lệ. Chỉ 5 category được DELETE, và mỗi cái đã kiểm chứng
#    NỘI DUNG (không phải chỉ tên/tuổi) trong báo cáo §2.1-2.2. `mike/logs` + `mike/bus` đều bị
#    .gitignore ⇒ KHÔNG có backup GitHub ⇒ xoá = mất vĩnh viễn. Đừng thêm category DELETE mà chưa
#    grep chứng minh 0 consumer.
# 3. DENY-LIST kiểm TRƯỚC mọi hành động, đứng ngoài logic từng category — để 1 pattern sai không
#    thể chạm surface tiền thật.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # …/mike
WC_ROOT="$(cd "$ROOT/.." && pwd)"                          # …/WorkingClaude
LOG="$ROOT/logs/fleet_housekeeping.log"

APPLY=0
ONLY=""
usage() {
  cat <<EOF
fleet_housekeeping.sh [--apply] [--only=cat1,cat2] [--help]

  (không cờ)      DRY-RUN: chỉ in ra sẽ động tới gì. MẶC ĐỊNH.
  --apply         Thực thi thật. Ghi $LOG + 1 bus event.
  --only=LIST     Chỉ chạy các category liệt kê (phẩy phân cách).

Category DELETE (đã xác minh nội dung, xem báo cáo §2):
  pid        logs/.dispatch_*.pid              — 0 reader trong toàn repo
  empty      logs/*.log|*.err size 0
  errnoise   logs/*.err chỉ chứa warning stdin của harness
  jobtmp     bus/jobs/*.json.tmp mồ côi (atomic-write bị kill)
  pycache    __pycache__/ (regenerable, đã gitignore cả 2 repo)

Category ARCHIVE (đảo ngược được, giữ nguyên nội dung):
  dispatchlog logs/dispatch_*.log  >30d  -> logs/archive/<YYYY-MM>/*.log.gz
  toollog     logs/{verify_,arch_review_,wags_pipeline_,daily_retro_draft_}* >30d
  registry    bus/registry/*.json  >30d  -> bus/registry/archive/
  rotate      logs/<cron>.log >10MB      -> .1.gz .2.gz .3.gz

Không có category OPT-IN nào. (\`datacold\` đã bị gỡ sau arch-review 2026-07-30 — xem §10 cuối file.)
EOF
}
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --only=*) ONLY="${a#--only=}" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "cờ không hiểu: $a" >&2; usage; exit 2 ;;
  esac
done

DEFAULT_CATS="pid empty errnoise jobtmp pycache dispatchlog toollog registry rotate"
want() {
  if [ -n "$ONLY" ]; then case ",$ONLY," in *",$1,"*) return 0 ;; *) return 1 ;; esac; fi
  case " $DEFAULT_CATS " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

# ── Đếm để báo cáo ───────────────────────────────────────────────────────────
N_DEL=0; B_DEL=0; N_ARC=0; B_ARC=0
# `return 0` cuối hàm là BẮT BUỘC: nếu để `[ "$APPLY" = 1 ] && printf …` là lệnh cuối thì say()
# trả 1 trong mọi lần dry-run ⇒ script exit 1 dù chạy THÀNH CÔNG (arch-review 2026-07-30 bắt được).
# Dưới cron dạng `... || notify` thì mỗi lần dry-run sẽ báo động giả → nhờn cảnh báo.
say() { printf '%s\n' "$*"; [ "$APPLY" = 1 ] && printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*" >>"$LOG"; return 0; }
hdr() { say ""; say "── $* ─────────────────────────────────────────"; }

# ── HÀNG RÀO CUỐI: deny-list ─────────────────────────────────────────────────
# Mọi category PHẢI gọi denied() trước khi động vào 1 path. Đây là lớp bảo vệ độc lập với logic
# pattern của từng category — cố ý trùng lặp với các điều kiện `find` ở dưới.
#   execution_logs/  = audit trail tài chính (sổ lệnh thật, dùng chung nhiều account)
#   bq_cache*        = snapshot vintage ghim, KHÔNG tái tạo được (BQ time-travel tắt,
#                      ticker/ticker_prune TRUNCATE+rebuild mỗi ngày)
#   agents/*/exp_*|probe_* = bằng chứng research đang được trích dẫn (20/22 dir, đã grep)
#   trade_plans/, plan_*.json, trading_rules.json = surface đặt lệnh, TUYỆT ĐỐI không chạm
denied() {
  case "$1" in
    */execution_logs/*|*/execution_logs) return 0 ;;
    */bq_cache*)                          return 0 ;;
    */_quarantine/*|*/data/archive/*)     return 0 ;;
    */trade_plans/*|*/plan_*.json)        return 0 ;;
    */trading_rules.json)                 return 0 ;;
    */agents/*/exp_*|*/agents/*/probe_*)  return 0 ;;
    */.git/*)                             return 0 ;;
    */run_bot_*)                          return 0 ;;   # bằng chứng thực thi bot
  esac
  return 1
}

do_delete() {   # do_delete <path> <lý do>
  local p="$1" why="$2" sz
  if denied "$p"; then say "  DENY-LIST chặn (không động): $p"; return; fi
  sz=$(stat -c %s "$p" 2>/dev/null || echo 0)
  N_DEL=$((N_DEL+1)); B_DEL=$((B_DEL+sz))
  if [ "$APPLY" = 1 ]; then rm -f -- "$p" && say "  DEL  $p ($sz B) — $why"
  else say "  [dry] DEL  $p ($sz B) — $why"; fi
}

do_archive() {  # do_archive <path> <thư mục đích>
  local p="$1" dest="$2" sz base ym
  if denied "$p"; then say "  DENY-LIST chặn (không động): $p"; return; fi
  sz=$(stat -c %s "$p" 2>/dev/null || echo 0)
  base="$(basename "$p")"
  ym="$(date -u -d "@$(stat -c %Y "$p")" +%Y-%m 2>/dev/null || echo unknown)"
  N_ARC=$((N_ARC+1)); B_ARC=$((B_ARC+sz))
  if [ "$APPLY" = 1 ]; then
    mkdir -p "$dest/$ym" || return
    # gzip TRƯỚC rồi mới bỏ bản gốc: nếu bị kill giữa chừng, file gốc vẫn còn (idempotent, §5).
    if gzip -c -6 -- "$p" > "$dest/$ym/$base.gz.part" 2>/dev/null \
       && [ -s "$dest/$ym/$base.gz.part" ] \
       && gzip -t "$dest/$ym/$base.gz.part" 2>/dev/null; then
      mv -f "$dest/$ym/$base.gz.part" "$dest/$ym/$base.gz"
      rm -f -- "$p"
      say "  ARC  $p -> $dest/$ym/$base.gz ($sz B)"
    else
      rm -f "$dest/$ym/$base.gz.part"
      say "  !! archive THẤT BẠI, giữ nguyên bản gốc: $p"
    fi
  else
    say "  [dry] ARC  $p -> $dest/$ym/$base.gz ($sz B)"
  fi
}

say "=== fleet_housekeeping $( [ "$APPLY" = 1 ] && echo APPLY || echo 'DRY-RUN (mặc định)') $(date -u +%FT%TZ) ==="
[ -n "$ONLY" ] && say "chỉ chạy category: $ONLY"

# ── HÀM CHUNG: job record của 1 dispatch log có còn tồn tại ở đâu không? ─────
# Dùng cho category `empty` (guard bằng-chứng-duy-nhất) và `dispatchlog` (guard trace.sh).
# Trả về job_id qua stdout nếu tên file có dạng dispatch_<job_id>.<ext>, rỗng nếu không phải.
jobid_of() {
  local b; b="$(basename "$1")"
  case "$b" in dispatch_*) ;; *) return 1 ;; esac
  b="${b#dispatch_}"; b="${b%.err}"; b="${b%.log}"
  printf '%s' "$b"
}
# 0 = có record (hot hoặc archive), 1 = KHÔNG có bản nào
has_job_record() {
  [ -f "$ROOT/bus/jobs/$1.json" ] || [ -f "$ROOT/bus/jobs/archive/$1.json" ]
}
# 0 = job CHƯA kết thúc (record hot, status không nằm trong terminal set) ⇒ TUYỆT ĐỐI không
# được xoá log/err của nó. Lý do không phải "cho gọn": logfile của job là BẰNG CHỨNG LIVENESS
# duy nhất của nhánh dispatch ĐỒNG BỘ — mike_json._pids_holding tìm worker qua ai đang giữ
# "$logfile.err", vì record đồng bộ không ghi pid nào cả. Xoá nó đi thì `job-live-pids` trả
# rỗng trên một job còn sống, và cú `job-set status=failed` ngay sau đó lọt guard: đúng lời
# nói dối của sự cố 2026-08-09, do chính cron hàng tuần gây ra (arch-reviewer round 4, K1).
# Nhánh `dispatchlog` (§6) đã có guard này từ trước; `empty` và `errnoise` thì chưa — mà .err
# của một job đồng bộ đang chạy thường ĐÚNG là "0 byte" hoặc "chỉ có warning stdin", tức là
# nằm gọn trong tiêu chí xoá của cả hai.
job_not_terminal() {
  local jf="$ROOT/bus/jobs/$1.json" st term
  [ -f "$jf" ] || return 1        # không có record hot ⇒ không phải job đang chạy
  st="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("status",""))' \
        "$jf" 2>/dev/null || echo '')"
  # Record không đọc nổi ⇒ coi như CHƯA kết thúc (giữ log). Không đọc được trạng thái thì
  # không được suy ra "đã xong".
  [ -n "$st" ] || return 0
  term="|$(python3 "$ROOT/bin/mike_json.py" terminal-statuses 2>/dev/null | tr '\n' '|')"
  case "$term" in
    *"|$st|"*) return 1 ;;        # đã terminal ⇒ xoá được
    *) return 0 ;;
  esac
}

# ── 1. pid — 0 reader trong toàn repo (báo cáo §2.1) ─────────────────────────
# `-mtime +1` cho nhất quán với empty/errnoise: file .pid là bản ghi DUY NHẤT của OS-pid một
# dispatch đang chạy (dùng để kill tay), không xoá của job vừa mới dispatch vài giây trước.
if want pid; then
  hdr "pid — logs/.dispatch_*.pid >1d (0 reader: chỉ dispatch.sh:753 GHI, không ai ĐỌC)"
  while IFS= read -r f; do do_delete "$f" "pid không ai đọc"; done \
    < <(find "$ROOT/logs" -maxdepth 1 -name '.dispatch_*.pid' -type f -mtime +1 2>/dev/null)
  # *.workerpid: _hb_aware_timeout ghi pid của worker để _sync_killed_guard giết được nó
  # trước khi đóng record. Nó TỰ xoá ở cả hai đường thoát bình thường, nên file còn sót >1d
  # nghĩa là dispatch.sh bị SIGKILL (không trap được) — rác, và là rác NGUY HIỂM nếu để lâu
  # vì pid trong đó có thể đã được kernel cấp lại cho tiến trình khác.
  hdr "workerpid — logs/*.workerpid >1d (chỉ sót khi dispatch.sh bị SIGKILL)"
  while IFS= read -r f; do do_delete "$f" "workerpid mồ côi (pid có thể đã bị cấp lại)"; done \
    < <(find "$ROOT/logs" -maxdepth 1 -name '*.workerpid' -type f -mtime +1 2>/dev/null)
fi

# ── 2. empty — file 0 byte, CÓ GUARD BẰNG-CHỨNG-DUY-NHẤT ─────────────────────
# Kiểm lại bằng `-s` ngay trước khi xoá (KHÔNG tin danh sách find đã cũ) — một job đang chạy có
# thể vừa ghi dòng đầu vào file mà lúc find còn rỗng.
#
# ⚠️ SỬA SAU ARCH-REVIEW (2026-07-30, killer objection — ĐÃ ĐO LẠI VÀ ĐÚNG): lý do biện minh cũ
# ("trạng thái fail đã nằm ở bus/jobs/<job>.json") SAI với 6/66 file (~9%):
#   Taylor_20260625_013357, Winston_20260624_144409, Winston_20260626_020936,
#   Taylor_20260625_022912, Mike_20260627_024240, Winston_20260626_020407
# — không có job record (hot lẫn archive), không bus event, không tham chiếu KB. logs/ lại bị
# .gitignore (0 backup GitHub) ⇒ với 6 job này, filename+mtime là artifact DUY NHẤT còn sót.
# Đây đúng lớp lỗi đã bắt được ở `jobtmp`; nay áp CÙNG guard đó cho `empty`.
if want empty; then
  hdr "empty — logs/*.log|*.err 0 byte + CÓ job record thật (không thì GIỮ: là dấu vết duy nhất)"
  while IFS= read -r f; do
    [ -s "$f" ] && { say "  bỏ qua (đã có nội dung sau khi quét): $f"; continue; }
    if jid="$(jobid_of "$f")" && ! has_job_record "$jid"; then
      say "  GIỮ (0 byte NHƯNG không có job record hot lẫn archive — artifact DUY NHẤT): $f"
      continue
    fi
    if jid="$(jobid_of "$f")" && job_not_terminal "$jid"; then
      say "  GIỮ (job CHƯA kết thúc — logfile là bằng chứng liveness duy nhất của sync dispatch): $f"
      continue
    fi
    do_delete "$f" "0 byte, job record còn tra được"
  done < <(find "$ROOT/logs" -maxdepth 1 -type f \( -name '*.log' -o -name '*.err' \) -size 0 -mtime +1 2>/dev/null)
fi

# ── 3. errnoise — .err chỉ chứa warning boilerplate của harness ───────────────
# Đã đọc thật 33 file .err không rỗng: 25 file đúng 157 B và chỉ có dòng warning này; 8 file còn
# lại có nội dung khác ⇒ GIỮ. Xoá theo NỘI DUNG, không theo tên/kích thước.
# SIẾT SAU ARCH-REVIEW: `grep -q` cho phép file vừa có warning vừa có dòng lỗi THẬT phía sau lọt
# qua. Nay yêu cầu MỌI dòng non-blank đều phải khớp warning. Đo thật trước khi đổi: cả 25 file
# hiện đúng 157 B và 0 dòng non-blank thừa ⇒ siết này mất 0 file, chỉ thêm an toàn.
if want errnoise; then
  hdr "errnoise — logs/*.err ≤200B mà MỌI dòng non-blank đều là warning stdin của harness"
  while IFS= read -r f; do
    [ "$(wc -c <"$f")" -le 200 ] || continue
    grep -q 'no stdin data received' "$f" 2>/dev/null || continue
    # còn dòng non-blank nào KHÔNG phải warning ⇒ có nội dung thật ⇒ giữ
    if grep -v '^[[:space:]]*$' "$f" | grep -qv 'no stdin data received'; then
      say "  GIỮ (có dòng khác ngoài warning): $f"; continue
    fi
    if jid="$(jobid_of "$f")" && job_not_terminal "$jid"; then
      say "  GIỮ (job CHƯA kết thúc — .err là handle liveness duy nhất của sync dispatch): $f"
      continue
    fi
    do_delete "$f" "chỉ có warning stdin, không phải lỗi"
  done < <(find "$ROOT/logs" -maxdepth 1 -type f -name '*.err' ! -size 0 -mtime +1 2>/dev/null)
fi

# ── 4. jobtmp — .json.tmp mồ côi ─────────────────────────────────────────────
# Chỉ xoá khi job record THẬT đã tồn tại (hot HOẶC trong bus/jobs/archive/ do Phase 1b3 chuyển đi)
# — nếu không thì .tmp có thể là bản duy nhất còn lại của record đó.
#
# ⚠️ Cái guard này ĐÃ BẮT ĐƯỢC 1 lỗi phân loại của chính tôi (2026-07-30): 3 file .tmp
# (Mafee_20260627_105458, Taylor_20260628_053125, Winston_20260628_053145) ban đầu tôi xếp
# "RÁC THẬT". Chạy dry-run thì guard giữ lại, kiểm tay thì KHÔNG có bản .json nào ở hot lẫn
# archive ⇒ 3 file .tmp này là DẤU VẾT DUY NHẤT của 3 job đó (bị truncate giữa dòng
# "prompt_summary", status còn "running"). Không phải rác. Bài học: điều kiện "đã có bản đầy đủ ở
# nơi khác" phải KIỂM, không được suy ra từ việc file có hậu tố .tmp.
if want jobtmp; then
  hdr "jobtmp — bus/jobs/*.json.tmp sót từ atomic-write bị kill"
  while IFS= read -r f; do
    real="${f%.tmp}"
    arch="$ROOT/bus/jobs/archive/$(basename "$real")"
    if [ -f "$real" ]; then do_delete "$f" "record thật còn ở hot: $(basename "$real")"
    elif [ -f "$arch" ]; then do_delete "$f" "record thật đã archive: $(basename "$arch")"
    else say "  GIỮ (không có bản đầy đủ ở hot lẫn archive — .tmp là dấu vết DUY NHẤT): $f"; fi
  done < <(find "$ROOT/bus/jobs" -maxdepth 1 -type f -name '*.json.tmp' -mtime +7 2>/dev/null)
fi

# ── 5. pycache — regenerable theo định nghĩa ─────────────────────────────────
# PHẠM VI SAU ARCH-REVIEW: chỉ $ROOT (mike/) + trading_bot/, KHÔNG quét cả $WC_ROOT.
# Lý do: đo thật 250 dir thì 219 dir / 14,0 MB nằm ở WorkingClaude/stockquery — app không thuộc
# fleet, ngoài phạm vi được giao. Thu hẹp lại còn ~6 MB nhưng đúng thẩm quyền.
if want pycache; then
  hdr "pycache — __pycache__/ trong mike/ + trading_bot/ (đã .gitignore, Python tự tạo lại)"
  while IFS= read -r d; do
    if denied "$d/"; then say "  DENY-LIST chặn: $d"; continue; fi
    sz=$(du -sb "$d" 2>/dev/null | cut -f1); sz=${sz:-0}
    N_DEL=$((N_DEL+1)); B_DEL=$((B_DEL+sz))
    if [ "$APPLY" = 1 ]; then rm -rf -- "$d" && say "  DEL  $d/ ($sz B)"
    else say "  [dry] DEL  $d/ ($sz B)"; fi
  done < <(find "$ROOT" "$WC_ROOT/trading_bot" -type d -name '__pycache__' -not -path '*/.git/*' 2>/dev/null)
fi

# ── 6. dispatchlog — ARCHIVE, KHÔNG XOÁ ──────────────────────────────────────
# Đo thật (báo cáo §2.3): lấy mẫu 12 log >30d, 4/12 KHÔNG có bản tóm tắt nào trên bus/KB. Cộng với
# logs/ bị .gitignore (0 backup GitHub) ⇒ xoá = mất dấu vết duy nhất của ~1/3 job. Nén + di chuyển.
#
# Ngưỡng 30d KHÔNG phải con số tuỳ ý: kb_nightly Phase 1b3 archive job record >30d, và
# `mike_json job-get` glob KHÔNG đệ quy ⇒ `trace.sh --log` (dòng 30-35, lấy path logfile TỪ job
# record rồi tail) hiện đã không tra được job >30d. Đặt cùng ngưỡng ⇒ log và job record rời hot
# cùng lúc, không tạo khoảng thời gian mà trace vẫn tìm log nhưng log đã đi.
# ⚠️ Nếu hạ xuống 14d (lợi token gấp đôi: 1007 vs 668 file) thì PHẢI thêm fallback tra
#    logs/archive/*/<name>.log.gz trong trace.sh — nếu không, --log im lặng không ra gì.
#
# ⚠️ GUARD THÊM SAU ARCH-REVIEW: lập luận "30d thì job record cũng đã rời hot" chỉ ĐÚNG MỘT NỬA.
# kb_nightly.sh:490 chỉ archive status TERMINAL {done,failed,timeout}; record `orphaned` /
# `usage_limited` / `cancelled` / `superseded` nằm hot VĨNH VIỄN ⇒ với nhóm đó `trace.sh --log`
# HIỆN ĐANG CHẠY ĐƯỢC và sẽ bị archive này làm im lặng MỚI. Đo thật 2026-07-30: 9 job (tất cả
# `orphaned`, 30,3–33,3d — Mafee_20260627_045844, Taylor_20260627_115036, Winston_20260627_195420,
# Winston_20260628_065538, Taylor_20260628_064658, Wendy_20260629_131236, Wendy_20260629_160847,
# Taylor_20260630_033117, Taylor_20260630_034617). Đây đúng nhóm job cần điều tra nhất (việc của
# Wags) ⇒ giữ log của chúng ở hot cho tới khi record rời đi.
if want dispatchlog; then
  hdr "dispatchlog — logs/dispatch_*.log >30d -> logs/archive/ (ARCHIVE; giữ lại job non-terminal)"
  while IFS= read -r f; do
    if jid="$(jobid_of "$f")" && [ -f "$ROOT/bus/jobs/$jid.json" ]; then
      st="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("status",""))' \
             "$ROOT/bus/jobs/$jid.json" 2>/dev/null || echo '')"
      # Terminal set lấy từ MỘT nguồn (mike_json.py terminal-statuses). Bản hardcode cũ ở
      # đây là {done,failed,timeout} — lệch với kb_nightly.sh và với chính mike_json.py, nên
      # log của job 'orphaned' (26 bản ghi) bị giữ hot vĩnh viễn (2026-08-10, arch-reviewer).
      # Rỗng = không có record ⇒ vẫn archive như cũ.
      _term="|$(python3 "$ROOT/bin/mike_json.py" terminal-statuses 2>/dev/null | tr '\n' '|')"
      case "$_term" in
        *"|$st|"*) ;;
        *) [ -n "$st" ] && { say "  GIỮ (job record còn hot, status=$st — trace.sh --log đang dùng được): $f"; continue; } ;;
      esac
    fi
    do_archive "$f" "$ROOT/logs/archive"
  done < <(find "$ROOT/logs" -maxdepth 1 -type f -name 'dispatch_*.log' -mtime +30 2>/dev/null)
fi

# ── 7. toollog ───────────────────────────────────────────────────────────────
if want toollog; then
  hdr "toollog — verify_/arch_review_/wags_pipeline_/daily_retro_draft_ >30d -> logs/archive/"
  while IFS= read -r f; do do_archive "$f" "$ROOT/logs/archive"; done \
    < <(find "$ROOT/logs" -maxdepth 1 -type f \
          \( -name 'verify_*' -o -name 'arch_review_*' -o -name 'wags_pipeline_*' \
             -o -name 'daily_retro_draft_*' \) -mtime +30 2>/dev/null)
fi

# ── 8. registry — gap duy nhất của bus mà kb_nightly không chạm ──────────────
# ⚠️ LOẠI TRỪ ROSTER SAU ARCH-REVIEW: `mike_json.py:402 cmd_fleet_status` glob bus/registry/*.json
# KHÔNG đệ quy ⇒ archive registry của 1 agent chính danh làm nó BIẾN MẤT khỏi bin/fleet_health.sh
# thay vì hiện `dead` — mất tín hiệu đúng lúc cần nhất (agent im lâu = dấu hiệu hỏng).
# Không phải giả thuyết: bus/registry/Bob.json đang 28 ngày, sẽ vượt 30d ngay tuần chạy đầu.
ROSTER='Mike Taylor Winston Wendy Spyros Mafee DollarBill Wags Bob'
if want registry; then
  hdr "registry — bus/registry/*.json >30d -> archive/ (trừ agent trong roster: $ROSTER)"
  while IFS= read -r f; do
    b="$(basename "$f" .json)"
    case " $ROSTER " in
      *" $b "*) say "  GIỮ (agent trong roster — archive sẽ làm biến mất khỏi fleet_health): $f"; continue ;;
    esac
    do_archive "$f" "$ROOT/bus/registry/archive"
  done < <(find "$ROOT/bus/registry" -maxdepth 1 -type f -name '*.json' -mtime +30 2>/dev/null)
fi

# ── 9. rotate — log cron append vô hạn, chưa ai rotate ───────────────────────
# discover.log 1,6M / notify.log 880K / watchdog.log 452K… Rotate bằng `cp + truncate` (KHÔNG mv)
# để process đang giữ fd ghi tiếp vào cùng inode không bị mất dòng.
# Ngưỡng hạ 10M -> 300K (2026-08-16, xem kb/coding_guidelines_ext.md §29): 10M chưa từng chạm
# tới cho CHÍNH 3 file comment trên nêu tên làm ví dụ (discover.log mới 1,7M sau nhiều tháng
# cron 10'/lần) — nghĩa là category này trên thực tế KHÔNG BAO GIỜ rotate chúng, để lỗi CŨ ĐÃ SỬA
# nằm mãi trong 200KB tail mà cron_health_check.py quét, gây báo động giả lặp lại mỗi ngày (ca
# thật: discover_sessions.py ENAMETOOLONG đã fix từ 2026-08-15 vẫn báo hằng ngày). 300K ≈ cỡ tail
# cron_health_check.py thực sự đọc, giữ "cửa sổ nóng" luôn đủ mới mà không rotate quá dày.
if want rotate; then
  hdr "rotate — logs/*.log >300KB (giữ 3 đời .1.gz .2.gz .3.gz)"
  while IFS= read -r f; do
    if denied "$f"; then say "  DENY-LIST chặn: $f"; continue; fi
    sz=$(stat -c %s "$f")
    if [ "$APPLY" = 1 ]; then
      # §5 idempotent: nén XONG và verify TRƯỚC, chỉ khi đó mới dịch thế hệ + truncate.
      # (Thứ tự cũ dịch thế hệ trước ⇒ gzip fail/bị kill = mất đời cũ nhất mà không thêm được gì.)
      if gzip -c -6 -- "$f" > "$f.1.gz.part" 2>/dev/null && [ -s "$f.1.gz.part" ] \
         && gzip -t "$f.1.gz.part" 2>/dev/null; then
        rm -f "$f.3.gz"; [ -f "$f.2.gz" ] && mv -f "$f.2.gz" "$f.3.gz"
        [ -f "$f.1.gz" ] && mv -f "$f.1.gz" "$f.2.gz"
        mv -f "$f.1.gz.part" "$f.1.gz"
        : >"$f"   # copytruncate: writer dùng >> ghi tiếp bình thường; writer dùng `>` sẽ để lại
                  # lỗ NUL sparse — chấp nhận được vì mọi log cron ở đây đều append.
        say "  ROT  $f ($sz B -> 0, đời trước ở $f.1.gz)"
      else
        rm -f "$f.1.gz.part"; say "  !! rotate THẤT BẠI, giữ nguyên (chưa dịch thế hệ): $f"
      fi
    else say "  [dry] ROT  $f ($sz B) -> $f.1.gz, truncate bản hot"; fi
    N_ARC=$((N_ARC+1)); B_ARC=$((B_ARC+sz))
  done < <(find "$ROOT/logs" -maxdepth 1 -type f -name '*.log' -size +300k 2>/dev/null)
fi

# ── 10. (ĐÃ GỠ) datacold — arch-review 2026-07-30 bác bỏ ─────────────────────
# Category cũ: gzip tại chỗ data/*.csv|pkl|parquet >60d "không có tham chiếu literal".
# GỠ HẲN, 3 lý do đo được (không phải quan điểm):
#   (a) Lợi ích thật chỉ 188 file / 42,26 MB (~30 MB sau nén) — báo cáo bản đầu ghi nhầm
#       671 file / 0,72 GB, đó là con số của ngưỡng >30d trong khi script chạy >60d ⇒ phóng đại
#       ~18 lần. 30 MB = 0,2% của 13 GB trống, không đáng đánh đổi gì.
#   (b) Phép thử an toàn SAI CẤU TRÚC: corpus prune $WC_ROOT/data nên KHÔNG đọc
#       data/results_registry.md (4447 dòng — chính là sổ ghim kết quả mà báo cáo §1.4 dựa vào),
#       và 30 mục trong sổ đó lưu tên rút gọn dạng "..._x.csv" nên `grep -qF` không bao giờ khớp.
#       Hôm nay 0 va chạm, nhưng phải đúng LẬP LUẬN chứ không chỉ đúng kết quả (§10 mục 1).
#   (c) Ngay cả khi chạy đúng, gzip không giảm số entry ⇒ KHÔNG giúp token, mục tiêu chính.
# Muốn làm lại: phải đưa data/*.md vào corpus, thêm .sql/.yaml/.ipynb + `crontab -l`, và có
# Taylor xác nhận từng nhóm file trước. Không thuộc phạm vi housekeeping tự động.

# ── Tổng kết ─────────────────────────────────────────────────────────────────
say ""
say "=== TỔNG KẾT ==="
say "DELETE : $N_DEL mục, $(awk -v b=$B_DEL 'BEGIN{printf "%.2f MB",b/1048576}')"
say "ARCHIVE: $N_ARC mục, $(awk -v b=$B_ARC 'BEGIN{printf "%.2f MB",b/1048576}') trước nén (gz đo thật ~3,5x)"
if [ "$APPLY" = 1 ]; then
  "$ROOT/bin/append_event.sh" Wags status "fleet-housekeeping chạy thật" \
    "{\"deleted_items\":$N_DEL,\"deleted_bytes\":$B_DEL,\"archived_items\":$N_ARC,\"archived_bytes\":$B_ARC,\"only\":\"${ONLY:-default}\",\"log\":\"$LOG\"}" \
    >/dev/null 2>&1 || true
else
  say ""
  say "Đây là DRY-RUN. Chạy lại với --apply để thực thi."
fi

exit 0
