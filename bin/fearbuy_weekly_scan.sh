#!/usr/bin/env bash
# fearbuy_weekly_scan.sh — Weekly scan for "mua khi sợ hãi có tính toán" (calculated fear-buy)
# candidates: individual-stock crisis situations (company-specific scandal/crash), classified
# via the QUALIFY/NON/AMBIGUOUS playbook in agents/Taylor/research/calculated_fear_state_backstop.md.
#
# Mandate: user, 2026-07-23 — "tập trung dò tìm thêm, hàng tuần để có cơ hội tăng alpha cho hệ
# thống mà không phải đánh đổi rủi ro quá nhiều." Cases found so far (TV1, DGC) were surfaced
# ad-hoc by user attention, not a systematic sweep — this closes that gap.
#
# This is a DISPATCH wrapper (LLM judgment required: news interpretation, QUALIFY/NON/AMBIGUOUS
# classification), not a deterministic checker — mirrors bq_freshness_check.sh's DollarBill
# dispatch pattern, not check_sbv_weekly.sh's pure-bash pattern.
set -euo pipefail
WORKDIR="/home/trido/thanhdt/WorkingClaude"
MIKEDIR="$WORKDIR/mike"
TODAY=$(date +%Y-%m-%d)

# Route to Taylor's designated thread for this research line (user directive, this thread).
TAYLOR_THREAD="1521735922066919515"

PROMPT=$(cat <<EOF
Quét hàng tuần định kỳ ($TODAY) cho sleeve "mua khi sợ hãi có tính toán" (calculated fear-buy) —
mandate user 2026-07-23: dò tìm thêm cơ hội mỗi tuần, không chỉ chờ user tình cờ để ý (như TV1/DGC).

Playbook chuẩn: mike/agents/Taylor/research/calculated_fear_state_backstop.md — đọc kỹ trước khi
áp dụng, đừng tự chế tiêu chí khác. QUALIFY = scandal CÁ NHÂN (không lan pháp nhân) + tài sản lõi
tách biệt/còn vận hành + CF_OA thực ≥ NP + solvent + định giá đủ rẻ. NON = lõi tự hỏng/lan pháp
nhân/BCTC thổi phồng. AMBIGUOUS = chưa đủ rõ, cần cổng xác nhận cụ thể (thường BCTC quý tới).

VIỆC CẦN LÀM:

1. Refresh anomaly_scan.py cho phiên gần nhất (IDIOCRASH/FLOOR2 — cờ rơi mạnh mang tính riêng lẻ,
   loại nhiễu beta thị trường chung). Liệt kê mã MỚI xuất hiện cờ trong 7 ngày qua chưa từng được
   phân loại (grep lịch sử case trong backstop.md để biết mã nào đã có kết luận).

2. Quét RỘNG hơn anomaly_scan (vốn chỉ bắt tín hiệu giá/KL) — WebSearch tin tức khởi tố/bắt giữ
   lãnh đạo doanh nghiệp niêm yết VN trong 7-14 ngày qua mà scan giá/KL có thể bỏ sót (case phản
   ứng chậm, hoặc cổ phiếu thanh khoản thấp không đủ volume để trigger IDIOCRASH).

3. Với MỖI case mới tìm được: áp đúng bộ lọc QUALIFY/NON/AMBIGUOUS, không vội kết luận — nếu case
   nào có tài sản lõi định giá được riêng (kiểu SOTP như TV1) hoặc dòng tiền/cổ tức mạnh (kiểu DGC),
   nhớ kiểm tra góc đó, đừng chỉ nhìn governance/audit risk một chiều (bài học 2 lần bị user sửa
   tuần này — TV1 và DGC ban đầu đều bị đánh giá quá thận trọng vì bỏ sót giá trị tài sản/dòng
   tiền thật).

4. Với case ĐÃ có trong watchlist (TV1, DGC, PNJ...): chỉ cần echo trạng thái/catalyst hiện tại có
   gì mới không (đọc lại phần đã ghi trong backstop.md, không làm lại từ đầu trừ khi có tin mới).

5. Nếu KHÔNG có case mới tuần này: báo ngắn gọn "không có case mới, N mã rà qua, 0 QUALIFY" — im
   lặng hoàn toàn KHÔNG được (nguyên tắc quiet-heartbeat: phải phân biệt được "đã quét, sạch" với
   "pipeline chết").

6. Cập nhật backstop.md nếu có case mới đủ dữ liệu để ghi (dùng đúng format §6/§7 hiện có).

Đây là recon hàng tuần, KHÔNG phải quyết định mua — chỉ báo cáo case đáng chú ý để user/Mike xem
xét due-diligence sâu hơn nếu quan tâm, giống quy trình đã làm với TV1/DGC. Không cần quant-skeptic
(chưa chạm production/tiền thật).

BẮT BUỘC (hợp đồng đầu ra máy đọc được — xem mike/kb/dispatch_output_contract.md — dispatch này
chạy nền, không ai chờ trực tiếp): dù có case mới hay không, KẾT THÚC bằng ĐÚNG lệnh sau, nguyên
văn topic:
mike/bin/append_event.sh Taylor finding "fearbuy-weekly-scan" "<JSON: n_ma_ra_qua, n_case_moi, qualify_list>"
EOF
)

"$MIKEDIR/bin/dispatch.sh" Taylor "$PROMPT" --bg --timeout 2400 --retries 1 --model opus --effort high --thread "$TAYLOR_THREAD"

# Post-condition check của LẦN CHẠY TUẦN TRƯỚC (khảo sát vận hành 2026-08-01) — cùng lý do/mẫu
# như weekly_ops_audit.sh: job này KHÔNG có "lần gọi lại" tự nhiên trong tuần, điểm đúng để tự
# kiểm là ĐẦU lần chạy TUẦN SAU. Cửa sổ 9 ngày (rộng hơn chu kỳ 7 ngày 1 chút).
SINCE_LAST_WEEK="$(TZ=UTC date -u -d '9 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"
if [ -n "$SINCE_LAST_WEEK" ] && ! python3 "$MIKEDIR/bin/mike_json.py" has-event "$MIKEDIR/bus" Taylor \
     "$SINCE_LAST_WEEK" "finding:fearbuy-weekly-scan" >/dev/null 2>&1; then
  "$MIKEDIR/bin/notify.sh" "🟡 fearbuy_weekly_scan: KHÔNG tìm thấy finding 'fearbuy-weekly-scan' nào trong 9 ngày qua — lần chạy tuần trước có thể đã lạc đề/chết im." >/dev/null 2>&1 || true
fi
