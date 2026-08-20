#!/usr/bin/env bash
# batch_wake.sh <batch_id> <job_id> <thread_id> <single_job_wake_prompt>
#
# MỘT lượt wake cho CẢ một đợt fan-out, thay vì một lượt cho mỗi job.
#
# Vì sao tồn tại (RCA agents/Mike/research/plan_pipeline_3loi_rca_20260820.md, lỗi #1):
# bq_freshness_check.sh dispatch DollarBill cho MỖI account live — tách per-account là CỐ Ý
# (hàng rào chống nhiễm chéo tài khoản, sự cố 2026-07-19) và KHÔNG được gộp. Nhưng mỗi
# `_bg_wrapper` xong lại tự gọi wake_thread.sh ĐỘC LẬP ⇒ N lượt push cách nhau vài chục giây
# vào cùng một thread. ccdb chỉ dedupe task PENDING, không dedupe session RUNNING ⇒ lượt thứ
# hai mở phiên Mike SONG SONG với phiên thứ nhất ⇒ 2 lần post cùng nội dung (đo thật: 08-18
# cách 31s, 08-20 cách 83s trong logs/wake_thread.log). Fix đúng chỗ là tầng WAKE, không phải
# tầng dispatch.
#
# Quyết định "ai được bắn" nằm ở mike_json.py batch-claim-wake (test-and-set nguyên tử dưới
# flock, cùng kiểu jobs.sh claim-reply). Script này chỉ dịch 4 mã exit đó thành hành động —
# tách ra khỏi dispatch.sh để phần logic dễ sai này chạy được độc lập trong selfcheck
# (bin/dispatch_batch_wake_selfcheck.sh) thay vì chỉ test được qua một dispatch thật.
#
# Exit: 0 = đã bắn wake gộp cho batch · 1 = im lặng (người khác đã/sẽ bắn) ·
#       2 = không biết batch ⇒ đã bắn wake ĐƠN LẺ như hành vi cũ (fail-safe: thà thừa còn hơn
#           nuốt mất) · 3 = sai tham số.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

batch_id="${1:?usage: batch_wake.sh <batch_id> <job_id> <thread_id> <single_job_prompt>}"
job_id="${2:?usage: batch_wake.sh <batch_id> <job_id> <thread_id> <single_job_prompt>}"
thread_id="${3:?usage: batch_wake.sh <batch_id> <job_id> <thread_id> <single_job_prompt>}"
single_prompt="${4:?usage: batch_wake.sh <batch_id> <job_id> <thread_id> <single_job_prompt>}"

BATCH_DIR="$ROOT/bus/batches"
JOBS_DIR="$ROOT/bus/jobs"

_single_wake() {  # hành vi TRƯỚC khi có batch — giữ nguyên từng chữ
  "$ROOT/bin/wake_thread.sh" "$thread_id" "$single_prompt" "$job_id" 2>/dev/null || true
}

# stderr đi vào FILE chứ không /dev/null: nó chở BẰNG CHỨNG "im lặng có chủ ý" (xem dưới).
# mktemp hỏng ⇒ err_f rỗng ⇒ không có bằng chứng ⇒ mọi lượt đều rơi về wake đơn lẻ. Ồn ào,
# nhưng đúng chiều fail-safe: thà thừa một push còn hơn nuốt mất.
# CHÍNH SCRIPT NÀY sở hữu việc ghi chẩn đoán của nó, và ghi FAIL-SOFT (arch-reviewer vòng 5,
# BLOCKER). Bản trước bắt dispatch.sh làm hộ bằng `2>>logs/wake_thread.log` — nhưng bash KHÔNG
# CHẠY LỆNH nếu không mở được file redirect, và `|| true` nuốt luôn mã lỗi: đo end-to-end với
# `chmod 000 logs/wake_thread.log` ⇒ 2 job batch done, batch record đủ, 0 lượt wake, CÂM tuyệt
# đối. Tức một bản vá có mục đích duy nhất là TĂNG QUAN SÁT lại biến "ghi log được" thành điều
# kiện để wake nổ. Luật đúng đã có sẵn ở bin/wake_thread.sh:134 — "ghi log KHÔNG được biến một
# push đã thành công thành exit 1". Ở đây cũng vậy: `|| true` bọc ĐÚNG lệnh ghi, không bọc
# đường wake. Dấu thời gian NEO CỨNG ICT (§16) vì file này bị daily_retro.sh đếm theo `^$TODAY`.
LOGF="$ROOT/logs/wake_thread.log"
_log() {
  printf '%s batch_wake: %s | batch=%s job_id=%s\n' \
    "$(TZ='Asia/Ho_Chi_Minh' date -Iseconds)" "$1" "$batch_id" "$job_id" \
    >> "$LOGF" 2>/dev/null || true
}

err_f="$(mktemp 2>/dev/null || true)"
if [ -z "$err_f" ]; then
  # Không có chỗ chứa bằng chứng ⇒ mọi lượt rơi về wake đơn lẻ ⇒ N member = N push, tức BUG
  # GỐC sống lại. Đúng chiều fail-safe nhưng KHÔNG ĐƯỢC IM — đây là chính file mà RCA 08-20
  # dùng để đếm số lượt push, nơi người điều tra "sao hôm nay 2 lượt" nhìn đầu tiên.
  _log "mktemp HỎNG (TMPDIR=${TMPDIR:-/tmp}) — không kiểm được bằng chứng im-lặng, rơi về wake ĐƠN LẺ ⇒ có thể trùng lượt push"
fi
# shellcheck disable=SC2064
[ -n "$err_f" ] && trap 'rm -f "$err_f"' EXIT INT TERM

# Truyền THẲNG thread_id đang cầm (chính pin mà _bg_wrapper vừa notify) thay vì để
# mike_json đọc lại từ record — một sự thật, một cách đọc (arch-reviewer N-a vòng 2).
members="$(python3 "$ROOT/bin/mike_json.py" batch-claim-wake \
             "$BATCH_DIR" "$batch_id" "$job_id" "$JOBS_DIR" "$thread_id" \
             2>"${err_f:-/dev/null}")"
rc=$?

# IM LẶNG CHỈ KHI CÓ BẰNG CHỨNG (arch-reviewer vòng 3, BLOCKER-1). Mã 1 và 2 CŨNG chính là mã
# thoát của python3 khi nó KHÔNG BAO GIỜ chạy tới cmd_batch_claim_wake — SyntaxError/ImportError
# trong mike_json.py ⇒ 1; file thiếu hoặc subcommand bị đổi tên (rollback lệch pha giữa hai
# file) ⇒ main() sys.exit(2). Đo thật trên bản copy: cả hai ca đều ra 0 lượt wake, không log
# không notify. Suy "im lặng" từ mã thoát trần là suy từ sự VẮNG MẶT; chỉ marker in TẠI CHÍNH
# chỗ ra quyết định mới là bằng chứng. Vòng 2 (S1) mới bọc try/except BÊN TRONG hàm ⇒ lớp
# "python chưa chạy tới hàm" lọt lưới.
#
# NEO `^` LÀ BẮT BUỘC, không phải cho gọn (arch-reviewer vòng 4, BLOCKER). Traceback SyntaxError
# của Python IN LẠI NGUYÊN VĂN DÒNG NGUỒN — mà dòng định nghĩa marker trong mike_json.py chính
# là một chuỗi chứa marker. Đo thật: cú pháp hỏng ngay dòng đó ⇒ traceback echo marker ⇒ grep
# không neo KHỚP ⇒ im lặng, 0 wake — đúng ô mà cả commit này tồn tại để bịt. Ba đường im hợp lệ
# đều in marker ở CỘT 0; traceback thụt 4 dấu cách. Neo là thứ duy nhất tách được hai cái đó,
# nên marker chỉ "không giả mạo được" KHI CÒN NEO — đừng gỡ `^`.
_silent_ok() { [ -n "$err_f" ] && grep -q '^BATCH-SILENT-OK' "$err_f"; }
_dump_err() {   # chẩn đoán phải tới được NGƯỜI ĐỌC: dispatch.sh gọi script này với 2>/dev/null
  [ -n "$err_f" ] || return 0
  cat "$err_f" >&2
  while IFS= read -r _l; do [ -n "$_l" ] && _log "claim stderr: $_l"; done < "$err_f"
  return 0
}

case "$rc" in
  1|2)   # 1 = đã có người claim / mọi member đã replied · 2 = anh em còn chạy, người cuối bắn
     if _silent_ok; then exit 1; fi
     _dump_err
     _log "KHÔNG BIẾT: batch-claim-wake thoát $rc mà KHÔNG có bằng chứng im-lặng-có-chủ-ý (mike_json.py hỏng/thiếu/đổi subcommand?) — wake ĐƠN LẺ để không nuốt mất lượt"
     echo "KHÔNG BIẾT: batch-claim-wake thoát $rc mà KHÔNG có bằng chứng im-lặng-có-chủ-ý (mike_json.py hỏng/thiếu/đổi subcommand?) — wake ĐƠN LẺ để không nuốt mất lượt." >&2
     _single_wake
     exit 2 ;;
  0) ;;          # tới lượt mình
  *) # 3 = KHÔNG BIẾT (batch thiếu/hỏng/không phải member). Không biết thì BẮN, đừng im:
     # một lượt wake thừa tốn đúng một exit-1 của claim-reply, một lượt wake bị nuốt là
     # thread ngủ vô hạn (đúng lớp lỗi mà cả kiến trúc wake này sinh ra để diệt).
     _dump_err
     _single_wake
     exit 2 ;;
esac

# Prompt GỘP: một phiên Mike post kết quả của MỌI job trong batch. claim-reply vẫn chạy
# per-job (MIKE.md §8.4) — batch chỉ gộp lượt ĐÁNH THỨC, không gộp quyền post: nếu một job
# đã được post bởi lượt khác thì claim-reply của riêng nó trả exit 1 và job đó bị bỏ qua.
n_members="$(printf '%s\n' "$members" | grep -c . || true)"
list=""
while IFS=$'\t' read -r m_job m_to m_st; do
  [ -n "$m_job" ] || continue
  list="$list
- \`$m_job\` ($m_to, status=$m_st)"
done <<< "$members"

prompt="Đầu tiên, BATCH \`$batch_id\` — $n_members job cùng một đợt fan-out vừa xong. Đây là lượt đánh thức DUY NHẤT cho cả batch (đừng chờ thêm lượt nào khác, và đừng mở lượt riêng cho từng job).
Với MỖI job dưới đây, theo đúng thứ tự: chạy \`$ROOT/bin/jobs.sh claim-reply <job_id>\` → exit 1: BỎ QUA job đó (đã có người post). exit 0: đọc kết quả bằng \`$ROOT/bin/jobs.sh status <job_id>\` + logfile ghi trong job record rồi post. exit 2: báo job record thiếu, đừng im lặng. exit 3: job chưa xong, post progress, KHÔNG claim.
Danh sách job:$list
Nếu KHÔNG job nào claim được (tất cả exit 1) → ScheduleWakeup(noop:true,stop:true), DỪNG, không post gì. Post kết quả các job trong CÙNG một lượt này, đừng đoán nội dung từ tóm tắt."

"$ROOT/bin/wake_thread.sh" "$thread_id" "$prompt" "$job_id" 2>/dev/null || true
exit 0
