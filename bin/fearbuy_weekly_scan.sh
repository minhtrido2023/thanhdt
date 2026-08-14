#!/usr/bin/env bash
# fearbuy_weekly_scan.sh — quét tin xấu/cơ hội "mua khi sợ hãi có tính toán" (calculated fear-buy),
# phân loại theo playbook QUALIFY/NON/AMBIGUOUS trong
# agents/Taylor/research/calculated_fear_state_backstop.md.
#
# HAI CHẾ ĐỘ, MỘT SCRIPT (không dựng script thứ hai — E2/E3, job Taylor_20260814_041116):
#
#   --mode weekly  (mặc định)  cron 08:10 ICT thứ SÁU. Cửa sổ tin 7 ngày.
#       Mục đích: SĂN CƠ HỘI. Mandate user 2026-07-23 — TV1/DGC được user tình cờ để ý,
#       không phải do quét hệ thống; lượt này đóng khoảng trống đó.
#
#   --mode monday              cron 08:00 ICT thứ HAI. Cửa sổ tin 3 ngày (sau phiên T6 → CN).
#       ⚠️ MỤC ĐÍCH LÀ BẢO VỆ PHÍA MUA, KHÔNG PHẢI "BÁN KỊP" — đừng đọc nhầm về sau.
#       Lý do định lượng (§C.3 research/portfolio_wide_badnews_protection_20260814.md, đo
#       10 năm; script tái lập: research/weekday_idiocrash_stats_20260814.py): sau một cú sập
#       riêng lẻ vào thứ HAI, lợi suất phiên kế tiếp trung bình ~0% — KHÔNG khác 0 có ý nghĩa
#       thống kê (bootstrap 95% CI chứa 0), P(phiên sau âm) ~42-43%. Bán lúc đó KHÔNG cứu được
#       gì. Sau cú sập thứ SÁU mới là −3,10% (CI không chứa 0). Giá trị của
#       lượt quét sáng thứ Hai nằm ở chỗ khác: bot 09:05 thứ Hai đặt lệnh theo plan đã duyệt
#       CUỐI TUẦN, tức trước khi tin cuối tuần tồn tại. Lượt này để người duyệt biết luận
#       điểm của một mã sắp mua vừa gãy trong lúc mình ngủ — RÚT lệnh mua, không phải bán tháo.
#       (Khoảng trống là THẬT và đo được: thứ Hai tập trung 1,409× tỉ lệ sập riêng lẻ,
#       p=2,1e-37, và lệch BẤT ĐỐI XỨNG — chiều tăng chỉ 1,115×.)
#
# Đây là DISPATCH wrapper (cần LLM: đọc tin, phân loại QUALIFY/NON/AMBIGUOUS), không phải
# checker tất định — cùng khuôn với bq_freshness_check.sh, khác check_sbv_weekly.sh.
#
# ESCALATE-ONLY: không tự mua, không tự bán, không đổi plan. Chỉ phát hiện + báo người.
set -euo pipefail
WORKDIR="/home/trido/thanhdt/WorkingClaude"
MIKEDIR="$WORKDIR/mike"
TODAY=$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)

# Phân tích tham số: mọi thứ KHÔNG nhận ra đều phải rc=2, không được âm thầm rơi về weekly.
# Bản cũ (`[ "${1:-}" = "--mode" ] && ...`) khiến `fearbuy_weekly_scan.sh monday` — thiếu cờ —
# chạy chế độ WEEKLY với rc=0 và không một dòng cảnh báo: cron/người gõ nhầm sẽ tưởng lượt thứ
# Hai đang chạy trong khi nó chưa từng chạy. Cùng nhóm lỗi §28 (một kênh im lặng bị đọc thành
# "ổn"). `--mode tuesday` đã bị reject rc=2 sẵn ở case dưới — chỗ này chỉ áp nhất quán.
MODE="weekly"
case "${1:-}" in
  "") ;;
  --mode)
    [ -n "${2:-}" ] || { echo "fearbuy_weekly_scan.sh: --mode thiếu giá trị (weekly|monday)" >&2; exit 2; }
    MODE="$2"; shift 2
    [ "$#" -eq 0 ] || { echo "fearbuy_weekly_scan.sh: tham số thừa sau --mode $MODE: $*" >&2; exit 2; }
    ;;
  *)
    echo "fearbuy_weekly_scan.sh: tham số lạ '$1' — chỉ nhận '--mode weekly' hoặc '--mode monday'." >&2
    echo "  (gõ thiếu cờ --mode từng âm thầm chạy chế độ weekly với rc=0; nay là lỗi cứng.)" >&2
    exit 2
    ;;
esac

case "$MODE" in
  weekly)
    WINDOW_DESC="7 ngày qua"
    SCAN_LABEL="Quét hàng tuần định kỳ (thứ Sáu) — SĂN CƠ HỘI"
    BUS_TOPIC="fearbuy-weekly-scan"
    PURPOSE="Tìm case fear-buy mới trong tuần + rà lại trạng thái case đang theo dõi."
    ;;
  monday)
    # Cửa sổ 3 ngày = đúng khoảng kênh giá mù về mặt cấu trúc: tin nổ T7/CN không có phiên
    # nào để giá phản ứng, và lượt quét tin thứ Sáu đã chạy TRƯỚC khi tin tồn tại.
    WINDOW_DESC="3 ngày qua (từ sau phiên thứ Sáu tới hết Chủ Nhật)"
    SCAN_LABEL="Quét sáng thứ Hai — BẢO VỆ PHÍA MUA trước phiên 09:00"
    BUS_TOPIC="fearbuy-monday-scan"
    PURPOSE="Phủ khoảng trống tin cuối tuần TRƯỚC khi bot 09:05 đặt lệnh theo plan đã duyệt từ cuối tuần. Mục tiêu là RÚT lệnh mua vào mã vừa gãy luận điểm — KHÔNG phải bán tháo hàng đang giữ (số liệu cho thấy bán sau cú sập thứ Hai không cứu được gì)."
    ;;
  *) echo "fearbuy_weekly_scan.sh: --mode phải là weekly hoặc monday (nhận: $MODE)" >&2; exit 2 ;;
esac

# Route to Taylor's designated thread for this research line (user directive, this thread).
TAYLOR_THREAD="taylor_research"

# WATCHLIST SỐNG — thay danh sách mã chép cứng trong prompt (E2). Sinh từ vị thế thật của cả 2
# account qua anomaly_scan.load_universe(), đã có cổng độ tươi (E1) nên khối text tự nói ra khi
# nó đang đọc sổ cũ. Fail-soft: không sinh được thì nói thẳng trong prompt, KHÔNG im lặng bỏ qua
# (im lặng = LLM tự bịa danh sách, đúng cái đang muốn diệt).
UNIVERSE_BLOCK=$(timeout 200 python3 "$MIKEDIR/agents/Taylor/anomaly_scan.py" --print-universe 2>/dev/null || true)
if [ -z "$UNIVERSE_BLOCK" ]; then
  UNIVERSE_BLOCK="KHONG SINH DUOC WATCHLIST SONG (anomaly_scan.py --print-universe loi).
  BAT BUOC: tu chay lenh do va bao loi trong ket qua. TUYET DOI KHONG tu bia danh sach ma tu tri nho."
fi

PROMPT=$(cat <<EOF
$SCAN_LABEL — $TODAY. Cửa sổ tin: $WINDOW_DESC.

MỤC ĐÍCH LƯỢT NÀY: $PURPOSE

Playbook chuẩn: mike/agents/Taylor/research/calculated_fear_state_backstop.md — đọc kỹ trước khi
áp dụng, đừng tự chế tiêu chí khác. QUALIFY = scandal CÁ NHÂN (không lan pháp nhân) + tài sản lõi
tách biệt/còn vận hành + CF_OA thực >= NP + solvent + định giá đủ rẻ. NON = lõi tự hỏng/lan pháp
nhân/BCTC thổi phồng. AMBIGUOUS = chưa đủ rõ, cần cổng xác nhận cụ thể (thường BCTC quý tới).
Trục quyết định: cáo buộc chạm LÕI (sổ tín dụng với ngân hàng / tài sản sản xuất với phi tài
chính) hay chỉ chạm CÁ NHÂN? Đó là trục đã tách đúng PNJ-2015 (QUALIFY) khỏi PNJ-2026 (AMBIGUOUS)
và OGC (NON). KHÔNG dựng khung phân loại mới.

--- DANH MỤC ĐANG GÁC (sinh tự động lúc chạy, không phải danh sách chép tay) ---
$UNIVERSE_BLOCK
-------------------------------------------------------------------------------

VIỆC CẦN LÀM:

1. Refresh anomaly_scan.py cho phiên gần nhất (IDIOCRASH/FLOOR2 — cờ rơi mạnh mang tính riêng lẻ,
   loại nhiễu beta thị trường chung). Liệt kê mã MỚI xuất hiện cờ trong cửa sổ trên chưa từng được
   phân loại (grep lịch sử case trong backstop.md để biết mã nào đã có kết luận). Nếu output của
   anomaly_scan báo WATCHLIST QUÁ HẠN thì NÓI RA trong kết quả — kết luận sạch trên sổ cũ vô giá trị.

2. Quét RỘNG hơn anomaly_scan (vốn chỉ bắt tín hiệu giá/KL) — WebSearch tin tức trong cửa sổ trên.
   Dùng BỘ TỪ KHOÁ THEO NHÓM dưới đây, đúng nhóm của từng mã trong danh mục đang gác ở trên:

   a) CHUNG — áp cho MỌI mã (cả 2 nhóm):
      khởi tố / bắt tạm giam lãnh đạo · thanh tra · điều tra · đình chỉ giao dịch · hạn chế giao
      dịch · từ chối kiểm toán / ý kiến ngoại trừ · chậm nộp BCTC · cắt margin · huỷ niêm yết ·
      corporate-action bất thường (đổi tỉ lệ/huỷ chi trả đã công bố)

   b) NHÓM NGÂN HÀNG — BỔ SUNG (thiết kế §4.2
      research/bank_tailrisk_insurance_design_20260814.md, không viết lại):
      kiểm soát đặc biệt · chuyển giao bắt buộc · rút tiền hàng loạt · khởi tố chủ tịch/TGĐ ngân
      hàng · cho vay sân sau · thao túng cổ phiếu ngân hàng

   c) NHÓM NGOÀI NGÂN HÀNG — BỔ SUNG:
      tai nạn/sự cố nhà máy · thu hồi sản phẩm · mất giấy phép/mỏ · kê biên tài sản · tranh chấp
      lãnh đạo

   Ngoài danh mục đang gác, vẫn quét rộng thị trường để TÌM case fear-buy mới (mã chưa nắm giữ) —
   hai việc này không loại trừ nhau.

3. Với MỖI case mới tìm được: áp đúng bộ lọc QUALIFY/NON/AMBIGUOUS, không vội kết luận — nếu case
   nào có tài sản lõi định giá được riêng (kiểu SOTP như TV1) hoặc dòng tiền/cổ tức mạnh (kiểu DGC),
   nhớ kiểm tra góc đó, đừng chỉ nhìn governance/audit risk một chiều (bài học 2 lần bị user sửa —
   TV1 và DGC ban đầu đều bị đánh giá quá thận trọng vì bỏ sót giá trị tài sản/dòng tiền thật).

4. Với mã ĐANG GIỮ mà dính tin trong cửa sổ: nói rõ ẢNH HƯỞNG TỚI PHÍA MUA trước — có mã nào đang
   nằm trong plan/rổ ứng viên mua sắp tới mà luận điểm vừa gãy không? Đó là câu hỏi lượt này phải
   trả lời. Với case đã có kết luận trong backstop.md: chỉ echo trạng thái/catalyst có gì mới không.

5. Nếu KHÔNG có case mới: báo ngắn gọn "không có case mới, N mã rà qua, 0 QUALIFY" — im lặng hoàn
   toàn KHÔNG được (nguyên tắc quiet-heartbeat: phải phân biệt được "đã quét, sạch" với "pipeline
   chết"). N = số mã trong danh mục đang gác ở trên.

6. Cập nhật backstop.md nếu có case mới đủ dữ liệu để ghi (dùng đúng format §6/§7 hiện có).

Đây là recon ESCALATE-ONLY, KHÔNG phải quyết định mua/bán — chỉ báo cáo case đáng chú ý để user/Mike
xem xét due-diligence sâu hơn, giống quy trình đã làm với TV1/DGC. Không tự đổi plan, không tự đặt
lệnh. Không cần quant-skeptic (chưa chạm production/tiền thật).

BẮT BUỘC (hợp đồng đầu ra máy đọc được — xem mike/kb/dispatch_output_contract.md — dispatch này
chạy nền, không ai chờ trực tiếp): dù có case mới hay không, KẾT THÚC bằng ĐÚNG lệnh sau, nguyên
văn topic:
mike/bin/append_event.sh Taylor finding "$BUS_TOPIC" "<JSON: n_ma_ra_qua, n_case_moi, qualify_list, watchlist_stale>"
EOF
)

# FEARBUY_DRY_RUN=1 → chỉ IN prompt đã dựng, không dispatch, không notify (cùng khuôn
# OPS_HEALTH_DRY_RUN của ops_health_check.sh). Có đường chạy thử là điều kiện để §15 "verify by
# running, not by reading" thực hiện được: một dấu nháy ở dòng 60 của prompt 90 dòng thì đọc lại
# không bắt được, mà chạy thật thì tốn 1 dispatch Opus + 1 tin Discord mỗi lần verify.
if [ "${FEARBUY_DRY_RUN:-0}" = "1" ]; then
  echo "=== [dry-run] mode=$MODE topic=$BUS_TOPIC — prompt sẽ gửi cho Taylor ==="
  echo "$PROMPT"
  exit 0
fi

"$MIKEDIR/bin/dispatch.sh" Taylor "$PROMPT" --bg --timeout 2400 --retries 1 --model opus --effort high --thread "$TAYLOR_THREAD"

# Post-condition check của LẦN CHẠY TRƯỚC CÙNG CHẾ ĐỘ (khảo sát vận hành 2026-08-01) — cùng lý do/
# mẫu như weekly_ops_audit.sh: job này KHÔNG có "lần gọi lại" tự nhiên trong tuần, điểm đúng để tự
# kiểm là ĐẦU lần chạy TUẦN SAU. Cửa sổ 9 ngày (rộng hơn chu kỳ 7 ngày 1 chút).
# Kiểm theo topic RIÊNG của từng chế độ: gộp chung thì lượt thứ Hai sống sẽ che lấp lượt thứ Sáu
# chết (và ngược lại) — đúng nhóm lỗi §28 "suy từ sự vắng mặt của một kênh".
SINCE_LAST_WEEK="$(TZ=UTC date -u -d '9 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"
# has-event-PREFIX chứ không phải has-event khớp tuyệt đối (§26, bug thật wags_autofix.sh
# 2026-08-11): producer thường thêm hậu tố tự do vào topic, khớp tuyệt đối biến "có nhưng khác
# chữ" thành "không tìm thấy" ⇒ cảnh báo giả mỗi tuần rồi bị bỏ qua.
if [ -n "$SINCE_LAST_WEEK" ] && ! python3 "$MIKEDIR/bin/mike_json.py" has-event-prefix "$MIKEDIR/bus" Taylor \
     "$SINCE_LAST_WEEK" "finding:$BUS_TOPIC" >/dev/null 2>&1; then
  "$MIKEDIR/bin/notify.sh" "🟡 fearbuy_scan (--mode $MODE): KHÔNG tìm thấy finding '$BUS_TOPIC' nào trong 9 ngày qua — lần chạy trước có thể đã lạc đề/chết im." >/dev/null 2>&1 || true
fi
