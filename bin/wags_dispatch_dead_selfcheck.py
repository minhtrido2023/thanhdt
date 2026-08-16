#!/usr/bin/env python3
"""wags_dispatch_dead_selfcheck.py — khoá hồi quy cho nhánh "DISPATCH CHẾT" của
bin/wags_autofix.sh.

## Sự cố được khoá (2026-08-13T01:20Z, question treo 3 ngày)

`logs/wags_pipeline_20260813_012008.log` ghi rõ:

    Failed to authenticate: OAuth session expired and could not be refreshed
    WARNING: dispatch Wags kết thúc bất thường (exit=1, job Wags_20260813_012008)
    no match: Wags has no event with topic starting with [...]

Agent sửa lỗi **chưa từng chạy**. Nhưng pipeline vẫn đi tiếp, đốt một lượt arch-reviewer
trên hư không, rồi gói kết quả rỗng thành question `wags-arch-review-inconclusive:
coord-2026-08-13` — một cái nhãn nói rằng ARCH-REVIEW không kết luận được. Người đọc
backlog thấy "arch-review inconclusive" thì không có lý do gì đi gia hạn OAuth, nên nó nằm
đó 3 ngày. Đây đúng root-cause-B của skill close-the-loop: **một lần tra cứu thất bại đội
lốt một kết luận**. Hai sự việc khác nhau phải ra hai topic khác nhau.

## Cách test

TRÍCH đúng khối giữa 2 marker `WAGS_DISPATCH_DEAD_{BEGIN,END}` trong wags_autofix.sh rồi
chạy nó trên stub `_notify_arch`/`_post_q` — KHÔNG chép lại logic sang đây (chép là để nó
trôi). Dữ liệu `$out` dùng NGUYÊN VĂN output thật của ca 08-13, không phải input tổng hợp
cho dễ đậu.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "bin", "wags_autofix.sh")

_fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))
        _fails.append(name)


def extract_block():
    """Khối production giữa 2 marker, đã gỡ escape nháy đơn của `setsid bash -c '...'`."""
    src = open(SCRIPT, encoding="utf-8").read()
    # Nuốt hết PHẦN CÒN LẠI CỦA DÒNG marker: sau marker còn đuôi comment, mà đuôi đó không
    # có dấu `#` mở đầu ⇒ bash đọc "(marker cho ...)" thành subshell và cả khối tắt ngóm
    # với "unexpected end of file". Bắt tới hết dòng, không chỉ tới hết token.
    m = re.search(r"# WAGS_DISPATCH_DEAD_BEGIN[^\n]*\n(.*?)# WAGS_DISPATCH_DEAD_END",
                  src, re.S)
    if not m:
        return None
    blk = m.group(1)
    # Khối sống trong `setsid bash -c '...'`, nên có HAI kiểu escape phải gỡ, đúng thứ tự:
    #  1. '"$VAR"'  = thoát ra nháy đơn để NỘI SUY biến của tiến trình NGOÀI (PIPELOG, ROOT)
    #                 rồi vào lại. Gỡ thành một token thường — nếu bỏ qua bước này, chuỗi
    #                 mất cân bằng nháy và cả khối không parse (đã cắn khi viết file này).
    #  2. '"'"'     = một dấu nháy đơn theo nghĩa đen.
    blk = re.sub(r"'\"\$(\w+)\"'", r"__\1__", blk)
    return blk.replace("'\"'\"'", "'")


# Output THẬT của ca 2026-08-13 (logs/wags_pipeline_20260813_012008.log).
REAL_OUT = """JOB Wags_20260813_012008 (from=Mike, timeout=1500s)
Failed to authenticate: OAuth session expired and could not be refreshed
WARNING: dispatch Wags ket thuc bat thuong (exit=1, job Wags_20260813_012008)
"""


def run_block(block, dispatch_rc, out, label="coord-2026-08-13"):
    """Chạy khối với stub ghi lại lời gọi ra 2 file, trả (rc, notify_lines, postq_lines)."""
    d = tempfile.mkdtemp(prefix="wags_dispatch_dead_")
    nf, qf = os.path.join(d, "notify.txt"), os.path.join(d, "postq.txt")
    # `out` đi qua FILE, không nội suy vào script. repr() của Python KHÔNG phải literal bash
    # (nó escape kiểu \' và \n mà nháy đơn bash hiểu theo nghĩa đen) — bản đầu làm vậy và
    # 2 ca "out bẩn" fail vì HARNESS sai chứ không phải production sai.
    of = os.path.join(d, "out.txt")
    with open(of, "w", encoding="utf-8") as f:
        f.write(out)
    harness = f"""
set -uo pipefail
PIPELOG=/dev/null
LABEL={label}
dispatch_rc={dispatch_rc}
out="$(cat {of})"
_notify_arch() {{ printf '%s\\n' "$1" >> {nf}; }}
_post_q() {{ printf '%s\\n%s\\n' "$1" "$2" >> {qf}; }}
{block}
echo "REACHED_END_OF_BLOCK"
"""
    p = subprocess.run(["bash", "-c", harness], capture_output=True, text=True)
    rd = lambda f: open(f, encoding="utf-8").read() if os.path.exists(f) else ""
    return p, rd(nf), rd(qf)


def main():
    block = extract_block()
    print("\ncase_markers")
    check("marker WAGS_DISPATCH_DEAD_{BEGIN,END} còn nguyên trong wags_autofix.sh",
          block is not None,
          "không trích được khối — marker bị đổi/xoá, selfcheck này mất hiệu lực")
    if block is None:
        print("\nFAIL: không có gì để test")
        sys.exit(1)

    print("\ncase_dispatch_chet_ra_dung_topic")
    p, notify, postq = run_block(block, dispatch_rc=1, out=REAL_OUT)
    check("dispatch chết ⇒ DỪNG pipeline (không chạy tiếp xuống arch-review)",
          "REACHED_END_OF_BLOCK" not in p.stdout, p.stdout[:200])
    check("dispatch chết ⇒ có post question", postq.strip() != "", "không post gì")
    # Chỉ soi DÒNG TOPIC (dòng 1). Payload cố ý CÓ chữ "arch-review" trong câu giải thích
    # "khong phai arch-review" — kiểm cả khối thì assertion tự bắn vào chân mình.
    topic_line = postq.splitlines()[0] if postq else ""
    check("topic nói DISPATCH-FAILED, KHÔNG phải arch-review",
          "wags-autofix-dispatch-failed" in topic_line and "arch-review-inconclusive"
          not in topic_line, topic_line)
    check("payload ghi lại exit code thật của dispatch", '"dispatch_exit":"1"' in postq,
          postq[:300])
    check("payload GIỮ được dấu vết OAuth (người đọc biết phải gia hạn cái gì)",
          "authenticate" in postq.lower() or "expired" in postq.lower(), postq[:300])
    check("payload nói rõ KHÔNG phải fix bị bác",
          "khong phai fix bi bac" in postq, postq[:300])
    check("tin báo cho người mang mức 🔴 và nói chưa hề có bản vá",
          "🔴" in notify and "chưa hề có bản vá" in notify, notify[:200])

    print("\ncase_payload_van_la_JSON_hop_le")
    import json
    lines = postq.strip().split("\n")
    try:
        obj = json.loads(lines[1])
        ok = isinstance(obj, dict)
    except Exception as e:
        obj, ok = None, False
        print(f"       (lỗi parse: {e})")
    check("payload post lên bus parse được thành JSON object", ok,
          lines[1][:300] if len(lines) > 1 else "")
    if ok:
        check("err_tail đã bị loại nháy/backslash (không phá JSON)",
              '"' not in obj.get("err_tail", "") and "\\" not in obj.get("err_tail", ""),
              repr(obj.get("err_tail"))[:200])

    print("\ncase_out_ban_co_nhay_va_backslash")
    dirty = 'error: "unauthorized" \\ token=\'abc\' expired at C:\\tmp\n'
    p2, _, postq2 = run_block(block, dispatch_rc=2, out=dirty)
    try:
        json.loads(postq2.strip().split("\n")[1])
        ok2 = True
    except Exception:
        ok2 = False
    check("out chứa nháy kép + nháy đơn + backslash ⇒ payload VẪN là JSON hợp lệ", ok2,
          postq2[:300])
    check("exit code khác 1 cũng được ghi đúng", '"dispatch_exit":"2"' in postq2, postq2[:200])

    print("\ncase_CONTROL_dispatch_song_thi_khong_duoc_chan")
    p3, notify3, postq3 = run_block(block, dispatch_rc=0, out="moi thu binh thuong\n")
    check("CONTROL: dispatch exit=0 ⇒ KHÔNG post question dispatch-failed",
          postq3.strip() == "", postq3[:200])
    check("CONTROL: dispatch exit=0 ⇒ chạy tiếp xuống phần sau (không exit sớm)",
          "REACHED_END_OF_BLOCK" in p3.stdout, p3.stdout[:200])
    check("CONTROL: dispatch exit=0 ⇒ không báo động 🔴 oan", "🔴" not in notify3, notify3[:200])

    print()
    if _fails:
        print(f"FAIL: {len(_fails)} assertion hỏng")
        for n in _fails:
            print(f"  - {n}")
        sys.exit(1)
    print("OK: toàn bộ assertion PASS")


if __name__ == "__main__":
    main()
