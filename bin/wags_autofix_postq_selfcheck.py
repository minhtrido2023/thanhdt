#!/usr/bin/env python3
"""Selfcheck cho `_post_q` — đường GHI BUS QUESTION của bin/wags_autofix.sh.

VÌ SAO CÓ FILE NÀY. Hai call site cuối pipeline (verdict NEEDS_CHANGES/REFUTED và verdict
không tra ra được) ghi bus bằng `append_event.sh … >/dev/null 2>&1 || true`. Đó là ĐƯỜNG
ESCALATION DUY NHẤT: checker ops_health_check §5 đọc BUS — nó không đọc pipelog, không đọc
Discord. Nuốt exit code ⇒ khi append_event.sh hỏng (payload bị shell word-split — đã xảy ra
THẬT 13 event/6 agent từ 2026-07-14; quota; disk đầy) thì vòng fix kết thúc IM LẶNG: Discord
vẫn báo "cần người xem" nhưng backlog câu hỏi TRỐNG. Không ai theo dõi tiếp, và không ai biết
là mình không biết. Cùng phép sửa đã áp cho check_report_cadence.sh (commit 2ce53d7a).

Selfcheck KHÔNG chép lại logic: nó TRÍCH khối bash thật giữa WAGS_POSTQ_BEGIN/END rồi chạy
khối đó — TRONG ĐÚNG NGỮ CẢNH TRÍCH DẪN của production (nằm giữa `bash -c '…'`, nơi
`'"$PIPELOG"'` là phép nội suy của shell NGOÀI). Chạy khối ở ngữ cảnh khác thì nó không parse
nổi, và một selfcheck "xanh" vì khối không hề chạy còn tệ hơn không có selfcheck (đã cắn thật
ở check_report_cadence_selfcheck.py: 2 ca PASS giả).

  python3 bin/wags_autofix_postq_selfcheck.py

Hai ĐỐI CHỨNG ĐỎ (đều đã chạy tay khi viết, xem finding job Wags_20260814_050658):
  · Ràng buộc cấu trúc:  WAGS_AUTOFIX_SRC=<bản HEAD cũ> python3 bin/wags_autofix_postq_selfcheck.py
      ⇒ FATAL exit 1 (không có marker ⇒ selfcheck tự tuyên bố vô hiệu, KHÔNG pass rỗng).
  · Ràng buộc HÀNH VI:   WAGS_POSTQ_MUTANT=swallow python3 bin/wags_autofix_postq_selfcheck.py
      ⇒ tiêm lại đúng bản nuốt lỗi cũ (marker vẫn còn, trích vẫn được) ⇒ phải ĐỎ. Đây mới là
      đối chứng có giá trị: nó chứng minh các assert bám vào HÀNH VI, không phải bám vào việc
      khối có tồn tại hay không.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(os.environ.get("WAGS_AUTOFIX_SRC") or (ROOT / "bin" / "wags_autofix.sh"))
MUTANT = os.environ.get("WAGS_POSTQ_MUTANT", "")

fails, oks = [], []


def check(name, cond, detail=""):
    (oks if cond else fails).append(name)
    print(("  ✅ " if cond else "  ❌ ") + name + (f" — {detail}" if detail else ""))


def extract(begin, end):
    """Trích phần THÂN giữa 2 marker. Marker nằm trong comment có chữ mô tả đi kèm phía sau
    nên phải cắt tới HẾT DÒNG chứa marker — nếu không, đuôi comment lọt vào script và bash
    chết vì syntax error."""
    src = SRC.read_text(encoding="utf-8")
    m = re.search(re.escape(begin) + r"[^\n]*\n(.*?)[^\n]*" + re.escape(end), src, re.S)
    if not m:
        print(f"❌ FATAL: không trích được khối {begin}…{end} trong {SRC} — khối đã bị đổi "
              "tên/di chuyển, selfcheck VÔ HIỆU (không pass rỗng).")
        sys.exit(1)
    return m.group(1)


# Bản NUỐT LỖI cũ, dựng lại nguyên trạng để làm đối chứng đỏ (xem docstring).
_SWALLOW_BLOCK = '''
  _post_q() {
    "$ROOT/bin/append_event.sh" Wags question "$1" "$2" >/dev/null 2>&1 || true
  }
'''


def block():
    if MUTANT == "swallow":
        return _SWALLOW_BLOCK
    return extract("WAGS_POSTQ_BEGIN", "WAGS_POSTQ_END")


# Khung ngoài tái lập ĐÚNG production: `bash -c '…'` với các biến được nội suy từ shell ngoài
# bằng đúng thành ngữ '"$VAR"' mà wags_autofix.sh dùng. __BLOCK__ nằm TRONG dấu nháy đơn.
#
# ⚠️ Bài học khi viết file này (giữ lại vì dễ tái phạm): bản đầu tiên truyền payload JSON qua
# một biến của shell NGOÀI ('"$QPAYLOAD"'), tức thả chuỗi JSON THÔ vào mã nguồn của bash
# TRONG ⇒ đống `"` và `'` trong JSON tự phá cú pháp, payload tới nơi cụt còn `{verdict:...,
# note:co`. Ca đó ĐỎ, nhưng đỏ vì HARNESS sai chứ không phải production sai — production dựng
# payload ở tầng TRONG bằng `\"` thoát sẵn. Suýt "sửa" một lỗi không tồn tại. Nay harness dùng
# THẲNG biểu thức payload trích từ chính 2 call site thật (_post_q_call_exprs) nên không thể
# lệch khỏi production được nữa.
_HARNESS = r"""
ROOT=__ROOT__
LABEL=__LABEL__
PIPELOG=__PIPELOG__
ARCH_TOPIC=__ARCH_TOPIC__
bash -c '
  ROOT="'"$ROOT"'"; LABEL="'"$LABEL"'"
  ARCH_TOPIC="'"$ARCH_TOPIC"'"
  _notify_arch() { "$ROOT/bin/notify_thread.sh" "$1" "$ARCH_TOPIC" >/dev/null 2>&1 || true; }
__BLOCK__
  verdict="NEEDS_CHANGES"
  verdict_stdout="verdict: NEEDS_CHANGES (co dau cach)"
  bus_verdict="INCONCLUSIVE"
  _fnd="tim thay finding cua Wags"
  _post_q __TOPIC_EXPR__ __PAYLOAD_EXPR__
  echo "POSTQ_RC=$?"
  echo "STILL_ALIVE"
'
"""

# Giá trị các biến tầng TRONG mà harness set ở trên — dùng để đối chiếu payload nhận được.
_INNER = {
    "verdict": "NEEDS_CHANGES",
    "verdict_stdout": "verdict: NEEDS_CHANGES (co dau cach)",
    "bus_verdict": "INCONCLUSIVE",
    "_fnd": "tim thay finding cua Wags",
    "LABEL": "coord-2026-08-14",
}


def post_q_call_exprs():
    """Trích ĐÚNG biểu thức (topic, payload) của cả 3 call site thật trong wags_autofix.sh.

    Không tự chế payload trong test: payload thật mới là thứ có `\\"` lồng nhau, có `$verdict`
    chứa dấu cách, có '"$PIPELOG"' nội suy chéo tầng — tức đúng những chỗ hỏng được. Tự chế
    một payload "tương tự" là kiểm chứng bản sao chứ không phải kiểm chứng production.
    """
    src = SRC.read_text(encoding="utf-8")
    exprs = re.findall(r'^\s*_post_q\s+("[^\n]*?")\s*\\\n\s*("[^\n]*")\s*$', src, re.M)
    if len(exprs) != 4:
        print(f"❌ FATAL: cần đúng 4 call site _post_q trong {SRC}, tìm thấy {len(exprs)} — "
              "hình dạng call site đã đổi, selfcheck VÔ HIỆU.")
        sys.exit(1)
    return exprs

_APPEND_STUB = r"""#!/usr/bin/env bash
# Stub append_event.sh: ghi lại NGUYÊN các đối số (phân tách bằng ký tự đơn vị \x1f để phát
# hiện word-split — nếu payload bị tách thành nhiều $n thì số trường sẽ khác 4).
d="$(dirname "$0")/.."
printf '%s\x1f%s\x1f%s\x1f%s\x1fNARGS=%s\n' "$1" "$2" "$3" "$4" "$#" >> "$d/calls.log"
[ "$2" = question ] && [ -f "$d/FAIL_Q" ] && exit 7
[ "$2" = error ] && [ -f "$d/FAIL_ERR" ] && exit 9
exit 0
"""

_NOTIFY_STUB = r"""#!/usr/bin/env bash
printf '%s\n' "$1" >> "$(dirname "$0")/../notify.log"
exit 0
"""


def run_postq(fail_q=False, fail_err=False, site=0):
    """Chạy khối _post_q thật trên fixture, gọi bằng ĐÚNG biểu thức của call site `site`.

    Trả (stdout, stderr, calls, notifies)."""
    topic_expr, payload_expr = post_q_call_exprs()[site]
    td = tempfile.mkdtemp(prefix="postq_")
    root = Path(td)
    (root / "bin").mkdir()
    for name, body in (("append_event.sh", _APPEND_STUB), ("notify_thread.sh", _NOTIFY_STUB)):
        p = root / "bin" / name
        p.write_text(body, encoding="utf-8")
        p.chmod(0o755)
    if fail_q:
        (root / "FAIL_Q").touch()
    if fail_err:
        (root / "FAIL_ERR").touch()
    pipelog = root / "pipeline.log"
    script = (_HARNESS
              .replace("__ROOT__", shlex.quote(str(root)))
              .replace("__LABEL__", shlex.quote("coord-2026-08-14"))
              .replace("__PIPELOG__", shlex.quote(str(pipelog)))
              # Giá trị GIẢ, cố ý không phải Discord ID thật: fixture chỉ chuyển tiếp chuỗi
              # này sang stub notify_thread.sh, nội dung không ảnh hưởng assert nào — mà ID
              # trần trong code thì bị discord_id_gate chặn (đúng, xem incident 2026-08-02).
              .replace("__ARCH_TOPIC__", shlex.quote("<arch-topic-gia-cho-test>"))
              .replace("__TOPIC_EXPR__", topic_expr)
              .replace("__PAYLOAD_EXPR__", payload_expr)
              .replace("__BLOCK__", block()))
    sp = root / "run.sh"
    sp.write_text(script, encoding="utf-8")
    r = subprocess.run(["bash", str(sp)], capture_output=True, text=True)
    calls = [ln.split("\x1f") for ln in
             (root / "calls.log").read_text(encoding="utf-8").splitlines()] \
        if (root / "calls.log").exists() else []
    notifies = (root / "notify.log").read_text(encoding="utf-8").splitlines() \
        if (root / "notify.log").exists() else []
    return r.stdout, r.stderr, calls, notifies


# ── Ca 1: đường xanh — ghi bus OK thì im lặng, đúng 1 event, không báo động giả ───────────
def case_happy_path():
    out, err, calls, notif = run_postq(site=2)  # site=2 = wags-fix-not-confirmed
    check("xanh: _post_q trả 0 khi append_event.sh thành công", "POSTQ_RC=0" in out, out.strip())
    check("xanh: đúng 1 lần ghi bus (không ghi thêm event error thừa)", len(calls) == 1,
          f"calls={len(calls)}")
    check("xanh: event là question, đúng agent Wags",
          bool(calls) and calls[0][0] == "Wags" and calls[0][1] == "question", str(calls[:1]))
    check("xanh: KHÔNG cảnh báo giả ra stderr", "GHI BUS THAT BAI" not in err, err.strip()[:120])
    check("xanh: KHÔNG quấy Discord khi mọi thứ bình thường", notif == [], str(notif))


# ── Ca 2: append_event hỏng — phải kêu TO qua đủ 3 chốt ĐỘC LẬP ──────────────────────────
def case_bus_write_fails_is_loud():
    out, err, calls, notif = run_postq(fail_q=True, site=2)  # site=2 = wags-fix-not-confirmed
    check("đỏ→to: chốt 1 stderr — có WARN kèm ĐÚNG exit code thật (7)",
          "GHI BUS THAT BAI" in err and "exit=7" in err, err.strip()[:160])
    check("đỏ→to: stderr nói rõ HỆ QUẢ (checker §5 sẽ không thấy), không chỉ 'lỗi'",
          "escalation MAT" in err or "KHONG thay muc nay" in err, err.strip()[:160])
    err_evs = [c for c in calls if len(c) > 1 and c[1] == "error"]
    check("đỏ→to: chốt 2 — có event `error` riêng trên bus", len(err_evs) == 1, str(calls))
    check("đỏ→to: event error dùng topic ỔN ĐỊNH (grep được), không phải câu chữ tự do",
          bool(err_evs) and err_evs[0][2] == "wags-autofix-bus-write-failed", str(err_evs))
    check("đỏ→to: chốt 3 — có báo Discord (kênh KHÔNG đi qua bus)", len(notif) == 1, str(notif))
    check("đỏ→to: tin Discord nêu đủ exit + topic để người truy được",
          bool(notif) and "exit=7" in notif[0] and "wags-fix-not-confirmed" in notif[0],
          str(notif)[:200])
    check("đỏ→to: _post_q trả LẠI exit code thật cho caller (không nuốt thành 0)",
          "POSTQ_RC=7" in out, out.strip())


# ── Ca 3: cả đường tối giản CŨNG chết — không được im, và Discord vẫn phải chạy ──────────
def case_both_writes_fail():
    out, err, calls, notif = run_postq(fail_q=True, fail_err=True, site=2)
    check("bus chết hẳn: nói thẳng 'bus coi nhu CHET' (không im lặng bỏ qua)",
          "bus coi nhu CHET" in err, err.strip()[:200])
    check("bus chết hẳn: VẪN giữ WARN đầu tiên (2 sự cố ⇒ 2 dòng, không đè nhau)",
          "GHI BUS THAT BAI" in err, err.strip()[:200])
    check("bus chết hẳn: Discord VẪN được gọi — đây là kênh duy nhất còn tới được người",
          len(notif) == 1, str(notif)[:160])
    check("bus chết hẳn: vẫn trả exit code của lỗi GỐC (7), không phải lỗi phái sinh (9)",
          "POSTQ_RC=7" in out, out.strip())


# ── Ca 4: chính lớp lỗi sinh ra bản vá — payload THẬT tới nơi nguyên vẹn, 1 đối số ───────
def case_payload_not_word_split():
    # Dùng call site #2 (nhánh inconclusive): payload thật lớn nhất, có $verdict_stdout chứa
    # dấu cách + dấu ngoặc — đúng hình dạng đã làm 13 event/6 agent hỏng hồi 07-14.
    out, err, calls, notif = run_postq(site=3)
    check("word-split: payload thật vẫn là ĐÚNG 1 đối số ($4) — nếu _post_q để $2 trần thì "
          "append_event.sh nhận >4 đối số",
          bool(calls) and calls[0][4] == "NARGS=4", str(calls[:1])[:200])
    try:
        got = json.loads(calls[0][3]) if calls else None
    except Exception as e:
        got = None
        check("word-split: payload tới nơi vẫn là JSON hợp lệ", False, f"{e}: {calls[0][3][:160]}")
    if got is not None:
        check("word-split: payload tới nơi vẫn là JSON hợp lệ", True, "")
        check("word-split: trường có DẤU CÁCH giữ nguyên vẹn (không cụt ở từ đầu tiên)",
              got.get("verdict_stdout") == _INNER["verdict_stdout"],
              repr(got.get("verdict_stdout")))
        check("word-split: mọi trường biến tầng trong đều đúng giá trị",
              got.get("verdict") == _INNER["verdict"]
              and got.get("bus_verdict") == _INNER["bus_verdict"]
              and got.get("wags_finding") == _INNER["_fnd"], str(got)[:200])


# ── Ca 5: topic có dấu cách (mọi topic thật đều có: "wags-fix-not-confirmed: <label>") ───
def case_topic_with_space_intact():
    for site, want in ((0, "wags-autofix-review-needed: coord-2026-08-14"),
                       (1, "wags-autofix-dispatch-failed: coord-2026-08-14"),
                       (2, "wags-fix-not-confirmed: coord-2026-08-14"),
                       (3, "wags-arch-review-inconclusive: coord-2026-08-14")):
        out, err, calls, notif = run_postq(site=site)
        check(f"topic call site #{site} có dấu cách vẫn nguyên 1 đối số ($3) — '{want}'",
              bool(calls) and calls[0][2] == want, str(calls[:1])[:200])


# ── Ca 6: fail LOUD không được biến thành fail FATAL ─────────────────────────────────────
def case_nonzero_does_not_abort_pipeline():
    # wags_autofix.sh chạy `set -uo pipefail` (KHÔNG có -e), nhưng khối này nằm trong một
    # `bash -c` riêng. Nếu ai đó thêm `set -e` sau này, return khác 0 sẽ giết luôn phần đuôi
    # pipeline — đắt hơn hẳn lỗi mà nó đang báo. Khoá hành vi lại.
    out, err, calls, notif = run_postq(fail_q=True, site=2)
    check("ghi bus lỗi KHÔNG giết phần còn lại của pipeline (chỉ báo động, không abort)",
          "STILL_ALIVE" in out, out.strip())


# ── Ca 7: ràng buộc CẤU TRÚC trên file thật — sửa 1 chỗ không đủ, phải hết call site ─────
def case_no_swallowing_call_sites_left():
    # Guideline #4: sửa hành vi thì phải grep MỌI nơi hành vi đó được operationalize. Ca này
    # là thứ duy nhất bắt được "thêm call site thứ 3 rồi lại copy thành ngữ || true cũ".
    src = (ROOT / "bin" / "wags_autofix.sh").read_text(encoding="utf-8")
    q_lines = [ln for ln in src.splitlines()
               if "append_event.sh" in ln and " question " in ln]
    swallow = [ln for ln in q_lines if "|| true" in ln]
    check("cấu trúc: KHÔNG còn call site nào ghi question mà nuốt lỗi (`|| true`)",
          not swallow, str(swallow)[:200])
    posts = [ln for ln in src.splitlines() if re.search(r"^\s*_post_q\s", ln)]
    check("cấu trúc: cả 4 nhánh escalation (review-needed + dispatch-failed + NEEDS_CHANGES + inconclusive) đi qua _post_q",
          len(posts) == 4, f"{len(posts)} call site: {posts}")
    check("cấu trúc: _post_q được định nghĩa TRƯỚC mọi call site",
          src.index("_post_q()") < min(src.index(p) for p in posts) if posts else False)
    check("cấu trúc: _notify_arch (chốt 3) được định nghĩa trước _post_q dùng nó",
          src.index("_notify_arch()") < src.index("_post_q()"))


def main():
    print(f"— selfcheck _post_q (wags_autofix.sh) — SRC={SRC}"
          + (f"  [MUTANT={MUTANT}]" if MUTANT else ""))
    for fn in (case_happy_path, case_bus_write_fails_is_loud, case_both_writes_fail,
               case_payload_not_word_split, case_topic_with_space_intact,
               case_nonzero_does_not_abort_pipeline, case_no_swallowing_call_sites_left):
        print(f"\n[{fn.__name__}]")
        fn()
    total = len(oks) + len(fails)
    print(f"\n{'❌' if fails else '✅'} {len(oks)}/{total} PASS"
          + (f" — FAIL: {fails}" if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
