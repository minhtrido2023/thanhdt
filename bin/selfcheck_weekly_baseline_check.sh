#!/usr/bin/env bash
# selfcheck_weekly_baseline_check.sh — chạy TOÀN BỘ selfcheck production HEAD và so với
# kb/selfcheck_baseline.json.
#
# ⚠️ TÊN FILE CÒN CHỮ "weekly" LÀ DI SẢN — NHỊP THẬT TỪ 2026-08-12 LÀ **HÀNG NGÀY** (cron 04:30
# ICT, xem kb/cron_registry.md). Không đổi tên vì 2 file lịch sử (kb/incidents/retro/2026-08-08,
# -09) tham chiếu tên này; viết lại hồ sơ sự cố cũ tệ hơn là mang một cái tên cũ. Lời gọi
# kb_nightly.sh Phase 5 (thứ Sáu) GIỮ NGUYÊN: sau lần chạy ngày, nó không tìm thấy đỏ mới nên
# không báo động trùng — nó chỉ còn vai trò cấp dữ liệu cho editorial review thứ Sáu.
#
# VÌ SAO CẦN (2026-08-08, coding_guidelines.md §23): "9 đỏ là bình thường" là chính lỗ hổng khiến
# regression thật lẫn vào nhiễu. Baseline biến "đỏ nào đã biết" từ tri thức truyền miệng thành 1
# file JSON diff được — đỏ MỚI (không có trong known_red) mới đáng báo động.
#
# BA THAY ĐỔI 2026-08-12 (job Wags_20260812_112724, sự cố 4 selfcheck đỏ 2 ngày không ai biết —
# `state/selfcheck_runs.json` CHỨNG MINH đã có máy quét thấy chúng FAIL lúc 2026-08-10T12:05:23Z,
# vấn đề là không ai ĐƯỢC BÁO):
#   1. NHỊP: tuần → ngày. Đỏ xuất hiện thứ Hai mà chỉ quét thứ Sáu = 4 ngày mù, trong khi lệnh
#      thật chạy mỗi phiên.
#   2. PHẠM VI: thêm `mike/bin/*_selfcheck.py` (34 selfcheck tooling fleet: cron, dispatch,
#      report, gate commit) — trước đây chỉ gốc WorkingClaude.
#   3. ESCALATION: tầng so sánh tách ra `bin/selfcheck_baseline_diff.py` — nó ghi `question` lên
#      bus 1-lần-1-ca + ack + Discord topic architecture, VÀ ghi ca đỏ mới vào known_red để
#      không báo lại mỗi ngày (bản cũ không ghi ⇒ ở nhịp ngày sẽ thành bão báo động giả).
#
# ⚠️ BẮT BUỘC dùng đúng $DNA_PYEXE (Python 3.12 + pandas 3) + GOOGLE_APPLICATION_CREDENTIALS +
# PATH có gcloud sdk — chạy sai môi trường tự tạo FAIL/TIMEOUT giả (đã đo thật tối 2026-08-08:
# 4/51 file báo lỗi sai chỉ vì Mike verify bằng system python3 thay vì $DNA_PYEXE). Env này lấy
# từ chính kb/selfcheck_baseline.json's required_env, không hardcode 2 lần.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC="/home/trido/thanhdt/WorkingClaude"

# ĐỘC QUYỀN 1 LẦN CHẠY — không phải phòng xa, đã CẮN THẬT ngày 2026-08-12: hai lần quét chạy
# chồng nhau (12:08Z và 12:15Z, một do người chạy tay lúc đang triage). Lần đó THOÁT NẠN nhờ
# tình cờ cách nhau 7' nên lần sau đọc được baseline lần trước vừa ghi. Nếu hai tầng diff đọc
# baseline CÙNG LÚC (bộ quét mất ~20', kết thúc sát nhau là chuyện thường), cả hai đều thấy
# `known_red` cũ ⇒ escalate ĐÔI mọi ca — đúng cái bão báo động giả mà cả cơ chế này sinh ra để
# chống. Bảo vệ "escalate đúng 1 lần" bằng thứ tự tình cờ thì không phải là bảo vệ.
# Chờ 5' rồi bỏ (không xếp hàng vô hạn): lần chạy kia dù sao cũng quét cùng một HEAD.
mkdir -p "$ROOT/logs"     # phải có TRƯỚC khi mở fd khoá (repo mới clone chưa có logs/)
# HAI KIỂU THẤT BẠI KHÁC HẲN NHAU, TUYỆT ĐỐI KHÔNG GỘP (đo thật lúc dựng khoá này: bản đầu gộp
# chúng, và một fd hỏng làm TOÀN BỘ bộ quét im lặng bỏ lượt rồi `exit 0` — cron báo thành công,
# không ai quét, đúng y sự cố 4-selfcheck-đỏ-2-ngày mà cơ chế này sinh ra để chống):
#   · MỞ ĐƯỢC fd nhưng khoá đang bị giữ ⇒ lần chạy kia đang làm đúng việc này ⇒ bỏ lượt, exit 0.
#   · KHÔNG mở nổi fd (thiếu quyền, ROOT sai) ⇒ KHÔNG được im lặng bỏ lượt. Kêu to rồi CHẠY TIẾP
#     không khoá: escalate đôi là nhiễu dọn được, còn không quét là mù — mà mù mới là sự cố gốc.
if exec 9>"$ROOT/logs/.selfcheck_sweep.lock"; then
    # Thời gian chờ để env đổi được CHỈ vì nhánh hết-giờ phải test được bằng thí nghiệm thật
    # (chờ 300s trong test là không ai chạy) — production luôn dùng mặc định 300.
    if ! flock -w "${SC_LOCK_WAIT_S:-300}" 9; then
        echo "⚠️ BỎ LƯỢT: một lần quét selfcheck khác đang chạy (>5'). Kết quả của nó cũng là HEAD này." >&2
        exit 0
    fi
else
    echo "❌ KHÔNG mở được file khoá $ROOT/logs/.selfcheck_sweep.lock — CHẠY TIẾP KHÔNG KHOÁ (rủi ro escalate đôi nếu có lần chạy song song). Sửa quyền thư mục logs/." >&2
    "$ROOT/bin/notify.sh" "⚠️ [selfcheck sweep] Không mở được file khoá — vẫn quét nhưng KHÔNG có bảo vệ chạy-song-song. Kiểm quyền $ROOT/logs/." >/dev/null 2>&1 || true
fi
BASELINE="$ROOT/kb/selfcheck_baseline.json"
DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export GOOGLE_APPLICATION_CREDENTIALS="/home/trido/thanhdt/gcloud_dtienthanh/application_default_credentials.json"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"
export MIKE_BOT_TEST_MODE=1

[ -x "$DNA_PYEXE" ] || { echo "FATAL: DNA_PYEXE không tồn tại: $DNA_PYEXE" >&2; exit 2; }
[ -f "$BASELINE" ] || { echo "FATAL: thiếu baseline: $BASELINE" >&2; exit 2; }

cd "$WC" || exit 2
RESULT_JSON="$ROOT/logs/selfcheck_weekly_$(date -u +%Y%m%d).json"
JSONL="$ROOT/logs/.selfcheck_weekly_raw_$$.jsonl"
mkdir -p "$ROOT/logs"
: > "$JSONL"

# Phạm vi = production HEAD của 2 repo sống. Glob thật mỗi lần chạy, KHÔNG danh sách chép tay
# (§23). CỐ Ý KHÔNG có `test_*.py`: 165 file đó ở gốc là script backtest/R&D đặt tên theo lịch
# sử, không phải test (§23 hệ luận 2). CỐ Ý KHÔNG đệ quy vào `mike/agents/**`: ở đó là bản sao
# worktree (wt-*), đề xuất chưa live (pending_*) và artifact R&D (exp_*/job_*) — quét vào là tự
# tạo nhiễu (state/selfcheck_runs.json của bin/run_selfchecks.sh cho thấy đúng hậu quả: 46 FAIL
# thì ~35 là nhiễu loại này, làm 4 ca đỏ THẬT chìm nghỉm).
mapfile -t SC_FILES < <( { ls -1 *_selfcheck.py; ls -1 mike/bin/*_selfcheck.py; } 2>/dev/null | sort -u )
echo "Phạm vi: ${#SC_FILES[@]} selfcheck (gốc WorkingClaude + mike/bin)."

for f in "${SC_FILES[@]}"; do
    tmo="$(python3 -c "
import json
b=json.load(open('$BASELINE'))
print(b['required_env']['slow_files'].get('$f', b['required_env']['default_timeout_s']))
")"
    # `$f` nay có thể chứa `/` (mike/bin/…) ⇒ phải làm phẳng cho tên file log tạm, nếu không
    # redirect ghi vào thư mục không tồn tại và MỌI ca mike/bin thành FAIL giả.
    log="/tmp/wk_sc_$$_${f//\//_}.log"
    timeout "$tmo" "$DNA_PYEXE" "$f" > "$log" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then st=PASS; elif [ $rc -eq 124 ]; then st=TIMEOUT; else st=FAIL; fi
    [ "$st" != "PASS" ] && { echo "--- $st: $f (rc=$rc) ---"; tail -8 "$log"; }
    python3 -c "import json,sys; print(json.dumps({'file': sys.argv[1], 'status': sys.argv[2]}))" "$f" "$st" >> "$JSONL"
    rm -f "$log"
done

# So với baseline + escalate. Tầng này TÁCH RA file riêng (2026-08-12) để test được bằng
# import — logic escalation nằm trong heredoc bash là thứ không ai viết selfcheck cho được,
# và nó chính là chỗ bug L2 (không ghi known_red ⇒ báo lại mỗi lần) sống 4 ngày.
python3 "$ROOT/bin/selfcheck_baseline_diff.py" "$BASELINE" "$RESULT_JSON" "$JSONL"
rc=$?
rm -f "$JSONL"

# rc=1 (có đỏ MỚI) và rc=2 (quét hỏng/rỗng) là HAI sự việc khác nhau và phải nói khác nhau —
# gộp chúng vào một thông điệp "phát hiện đỏ mới" là đúng lỗi close-the-loop bug B cảnh báo
# (một lần tra cứu thất bại đội lốt một kết luận thật).
if [ $rc -eq 1 ]; then
    "$ROOT/bin/notify.sh" "🔴 [selfcheck] Phát hiện selfcheck ĐỎ MỚI không có trong baseline — xem $RESULT_JSON. Đây là tín hiệu regression thật (baseline chỉ chứa đỏ đã biết/đã chấp nhận). Chi tiết từng ca đã lên bus question 'selfcheck-red: <file>' + Discord topic architecture." >/dev/null 2>&1 || true
    "$ROOT/bin/append_event.sh" Mike error "selfcheck-weekly-new-red" \
      "{\"result_file\": \"$RESULT_JSON\"}" >/dev/null 2>&1 || true
elif [ $rc -eq 2 ]; then
    "$ROOT/bin/notify.sh" "❌ [selfcheck] Lần quét HỎNG (quá ít kết quả) — KHÔNG kết luận được selfcheck nào đỏ, baseline giữ nguyên. Kiểm bin/selfcheck_weekly_baseline_check.sh." >/dev/null 2>&1 || true
fi
exit $rc
