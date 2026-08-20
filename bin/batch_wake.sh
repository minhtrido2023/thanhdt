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

members="$(python3 "$ROOT/bin/mike_json.py" batch-claim-wake \
             "$BATCH_DIR" "$batch_id" "$job_id" "$JOBS_DIR" 2>/dev/null)"
rc=$?

case "$rc" in
  1) exit 1 ;;   # đã có người claim
  2) exit 1 ;;   # còn anh em đang chạy — người cuối cùng sẽ bắn
  0) ;;          # tới lượt mình
  *) # 3 = KHÔNG BIẾT (batch thiếu/hỏng/không phải member). Không biết thì BẮN, đừng im:
     # một lượt wake thừa tốn đúng một exit-1 của claim-reply, một lượt wake bị nuốt là
     # thread ngủ vô hạn (đúng lớp lỗi mà cả kiến trúc wake này sinh ra để diệt).
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
