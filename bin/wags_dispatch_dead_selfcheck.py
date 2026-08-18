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
import json
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
    sf = os.path.join(d, "posts.txt")
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
_post_s() {{ printf '%s\\n%s\\n' "$1" "$2" >> {sf}; }}
{block}
echo "REACHED_END_OF_BLOCK"
"""
    p = subprocess.run(["bash", "-c", harness], capture_output=True, text=True)
    # errors="surrogateescape", KHÔNG phải strict (arch-review round 2, coord-2026-08-16):
    # ca kiểm chính của file này CỐ TÌNH tạo byte hỏng. Đọc strict thì hàm này nổ
    # UnicodeDecodeError TRƯỚC khi tới assertion ⇒ vẫn RED (rc≠0) nên không im lặng, nhưng
    # thông điệp là traceback chứ không phải tên assertion, tức người đọc không biết chốt
    # nào vừa gãy. Surrogate lọt qua đây sẽ bị chính assertion "không lọt \udcxx" tố cáo.
    rd = lambda f: (open(f, encoding="utf-8", errors="surrogateescape").read()
                    if os.path.exists(f) else "")
    return p, rd(nf), rd(qf), rd(sf)


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
    p, notify, postq, _posts = run_block(block, dispatch_rc=1, out=REAL_OUT)
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
    p2, _, postq2, _ = run_block(block, dispatch_rc=2, out=dirty)
    try:
        json.loads(postq2.strip().split("\n")[1])
        ok2 = True
    except Exception:
        ok2 = False
    check("out chứa nháy kép + nháy đơn + backslash ⇒ payload VẪN là JSON hợp lệ", ok2,
          postq2[:300])
    check("exit code khác 1 cũng được ghi đúng", '"dispatch_exit":"2"' in postq2, postq2[:200])

    print("\ncase_err_tail_tieng_viet_cat_giua_ky_tu_da_byte")
    # arch-review coord-2026-08-16 killer objection. LANG="C" ⇒ `cut -c` đếm BYTE. Dòng lỗi
    # THẬT của ca 08-13 dài 383 byte và có tiếng Việt; byte 300 rơi đúng ranh giới ký tự nên
    # nó thoát NHỜ MAY (ký tự tiếng Việt 3 byte ⇒ 2/3 vị trí là vỡ). Ca dưới cố tình đặt
    # ranh giới vào chỗ vỡ. KHÔNG được chỉ assert "payload là JSON hợp lệ": json.loads PASS
    # ca hỏng này (surrogate vẫn parse) — phải assert BYTE ghi ra là UTF-8 hợp lệ VÀ
    # load_jsonl đọc lại được, vì bus là append-only: một dòng hỏng làm câm cả file mãi mãi.
    # ĐỘ DÀI PAD PHẢI TÍNH, KHÔNG ĐƯỢC HARDCODE (arch-review round 2 bắt được: bản đầu
    # hardcode pad=297 nhưng tiền tố "timeout " dài 8 byte nên phần ASCII thành 305 byte —
    # `cut -c1-300` cắt giữa đám 'x', tiếng Việt KHÔNG HỀ lọt vào 300 byte đầu, và mutation
    # test gỡ hẳn `| iconv` VẪN PASS 100%. Test xanh vì lý do chẳng liên quan gì tới thứ nó
    # khai đang bảo vệ — đúng hình thái bug TZ 07-31). Tính pad từ CHÍNH chuỗi sẽ dùng, rồi
    # ASSERT tiền đề: 300 byte đầu phải KHÔNG decode được. Nếu ai đó sửa câu tiếng Việt hay
    # đổi tiền tố, tiền đề gãy và test kêu NGAY thay vì âm thầm hết kiểm gì.
    _pfx, _tail_gap = "timeout ", 1   # 1 byte cho dấu cách `tr "\n" " "` phụ vào cuối
    viet = "dispatch Wags kết thúc bất thường (exit=1) — hết hạn xác thực, phiên đã cũ"
    pad = None
    for _n in range(200, 300):
        _raw = (_pfx + "x" * _n + viet).encode("utf-8")
        if len(_raw) <= 300:
            continue
        try:
            _raw[:300].decode("utf-8")
        except UnicodeDecodeError:
            pad = "x" * _n
            break
    check("TIỀN ĐỀ: dựng được chuỗi mà 300 byte đầu cắt ĐÚNG giữa ký tự đa byte "
          "(không có nó thì mọi assertion dưới đây vô nghĩa)", pad is not None,
          f"pad={pad if pad is None else len(pad)}")
    if pad is None:
        pad = "x" * 276
    p4, _, postq4, _ = run_block(block, dispatch_rc=1, out=f"{_pfx}{pad}{viet}\n")
    line = postq4.strip().split("\n")[1] if len(postq4.strip().split("\n")) > 1 else ""
    try:
        line.encode("utf-8")
        utf8_ok = True
    except UnicodeEncodeError:
        utf8_ok = False
    check("err_tail cắt giữa ký tự đa byte ⇒ dòng bus VẪN là UTF-8 hợp lệ", utf8_ok,
          repr(line[:120]))
    check("và không lọt surrogate nào (\\udcxx) vào payload",
          not any(0xDC80 <= ord(c) <= 0xDCFF for c in line), repr(line[:120]))

    # Đọc lại BẰNG CHÍNH load_jsonl production — nếu nó chết thì mọi consumer cũng chết.
    d2 = tempfile.mkdtemp(prefix="wags_dispatch_dead_bus_")
    bus_line = os.path.join(d2, "W.jsonl")
    with open(bus_line, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(json.dumps({"topic": "t", "payload": json.loads(line)},
                           ensure_ascii=False) + "\n")
    probe = (f"import sys; sys.path.insert(0,{os.path.join(ROOT,'bin')!r}); "
             # load_jsonl nhận DANH SÁCH đường dẫn — truyền chuỗi thì nó lặp qua từng KÝ TỰ,
             # ra 0 dòng và rc=0, tức assertion xanh/đỏ vì lý do chẳng liên quan gì đến UTF-8.
             f"import mike_json; print(len(mike_json.load_jsonl([{bus_line!r}])))")
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True)
    check("load_jsonl production đọc lại được dòng đó (rc=0, không UnicodeDecodeError)",
          r.returncode == 0 and r.stdout.strip() == "1",
          f"rc={r.returncode} out={r.stdout.strip()} err={r.stderr.strip()[-300:]}")

    print("\ncase_exit5_la_TU_RESUME_khong_phai_chet")
    # Ca thật 2026-08-18T00:29:30Z: job Wags_20260818_001950 hết max-turns ⇒ dispatch.sh
    # exit 5 ⇒ nhánh `!= 0` gói thành question "agent sua loi CHUA CHAY" — trong khi agent
    # ĐANG được resume chạy tiếp và về sau nộp finding thật. exit 5 là mã DUY NHẤT của
    # dispatch.sh cho nhóm "đã lên lịch tự resume" (usage-limit / provider-fallback /
    # max-turns), xem bin/dispatch.sh dòng ~1596-1610 + khối chú thích đầu file.
    # NGUYÊN VĂN từ log thật (logs/wags_pipeline_20260818_001949.log) — CÓ DẤU, không phải
    # bản chuyển tự cho dễ đậu. Bản trước dùng chuỗi ASCII "KHONG PHAI loi task"; nếu regex
    # production chỉ bắt bản có dấu thì test vẫn xanh còn production fail-closed oan mỗi lần.
    OUT5 = ("JOB Wags_20260818_001950 (from=Mike, timeout=1500s)\n"
            "NOTE: dispatch Wags (job Wags_20260818_001950) hết turn budget "
            "(--max-turns=50) — KHÔNG PHẢI lỗi task.\n"
            "      Đã tự động lên lịch resume NGAY với trần cao hơn "
            "(bin/resume_pending.py sẽ tự chạy lại).\n")
    p5, notify5, postq5, posts5 = run_block(block, dispatch_rc=5, out=OUT5,
                                            label="coord-2026-08-18")
    check("exit=5 + có dấu hiệu resume ⇒ KHÔNG post question dispatch-failed",
          "wags-autofix-dispatch-failed" not in postq5, postq5[:300])
    check("exit=5 ⇒ CÓ post question để nợ arch-review không rơi vào hư không",
          postq5.strip() != "", "không post gì")
    q_topic = postq5.splitlines()[0] if postq5 else ""
    # Tiền tố PHẢI nằm trong WAGS_SELF_Q_PREFIXES của bin/ops_health_check.sh, nếu không thì
    # question này kéo COORD_WARN dispatch lại chính vòng fix vừa dừng (vòng tự nuôi §14).
    # Ca kiểm đồng bộ 2 danh sách nằm ở bin/ops_health_check_selfcheck.py ca 11b.
    check("topic dùng tiền tố review-needed (WARN-ONLY, không kéo re-dispatch)",
          "wags-autofix-review-needed" in q_topic, q_topic)
    check("exit=5 ⇒ KHÔNG ghi event `status` mồ côi nữa (không consumer nào đọc)",
          posts5.strip() == "", posts5[:300])
    check("exit=5 ⇒ DỪNG pipeline (bản resume mới là bản chạy tiếp)",
          "REACHED_END_OF_BLOCK" not in p5.stdout, p5.stdout[:200])
    check("exit=5 ⇒ KHÔNG báo động 🔴 (không phải sự cố)", "🔴" not in notify5, notify5[:200])
    # Khoảng trống arch-review là THẬT và không tự lành: pipeline chết trước bước review,
    # còn bản resume chỉ chạy lại dispatch chứ không chạy lại pipeline. Im lặng ở đây đúng
    # là hình thái "monitoring fix creates silence" đã cắn 2026-08-06.
    check("tin báo NÓI RÕ arch-review sẽ không tự chạy cho vòng resume",
          "ARCH-REVIEW" in notify5 and "KHONG tu chay" in notify5, notify5[:400])
    # required_change #4 (arch-review coord-2026-08-18): câu cũ "khong can ai ra tay" nói về
    # CẢ vòng retry LẪN arch-review — sai vế sau. Và neo cứng "qua bin/resume_pending.py"
    # sai cho nhánh provider-fallback (dispatch.sh spawn job --bg, không qua pending_resumes).
    check("tin báo KHÔNG còn câu 'khong can ai ra tay' trống trơn",
          "khong can ai ra tay" not in notify5.lower(), notify5[:400])
    check("tin báo KHÔNG neo cứng vào bin/resume_pending.py (sai cho provider-fallback)",
          "resume_pending.py" not in notify5, notify5[:400])
    check("tin báo tách rõ 2 vế: retry tự lo, arch-review là việc của NGƯỜI",
          "VONG RETRY" in notify5.upper() and "VIEC CUA NGUOI" in notify5.upper(),
          notify5[:400])
    try:
        obj5 = json.loads(postq5.strip().split("\n")[1])
        ok5 = isinstance(obj5, dict) and obj5.get("dispatch_exit") == "5"
    except Exception as e:
        obj5, ok5 = None, False
        print(f"       (lỗi parse: {e})")
    check("payload parse được thành JSON object và ghi đúng exit=5", ok5, postq5[:300])
    check("payload cũng ghi lại khoảng trống arch-review (bus đọc được, không chỉ Discord)",
          "arch_review" in postq5, postq5[:300])

    print("\ncase_exit5_provider_fallback_cung_phai_duoc_nhan")
    # Site exit-5 THỨ BA của dispatch.sh (dòng ~1598) in câu chữ HOÀN TOÀN KHÁC hai site kia:
    # KHÔNG có "KHÔNG PHẢI lỗi task", KHÔNG có "lên lịch resume". Mẫu nhận dạng chỉ bắt 2 cụm
    # đó sẽ fail-closed OAN cho đúng nhánh fallback — và fail-closed oan ở đây nghĩa là mỗi
    # lần provider hết quota lại đẻ 1 question "DISPATCH CHẾT" giả.
    OUT5_FB = ("JOB Wags_20260818_010203 (from=Mike, timeout=1500s)\n"
               "NOTE: dispatch Wags (job Wags_20260818_010203) provider 'fable' hết "
               "usage/rate limit — đã fallback NGAY sang claude (job mới chạy nền, "
               "không chờ reset).\n")
    p7, notify7, postq7, posts7 = run_block(block, dispatch_rc=5, out=OUT5_FB,
                                            label="coord-2026-08-18-fb")
    check("provider-fallback: KHÔNG bị gán nhãn DISPATCH CHẾT",
          "wags-autofix-dispatch-failed" not in postq7 and "🔴" not in notify7,
          (postq7 + notify7)[:300])
    check("provider-fallback: vẫn ra question review-needed",
          "wags-autofix-review-needed" in (postq7.splitlines()[0] if postq7 else ""),
          postq7[:300])
    check("provider-fallback: DỪNG pipeline", "REACHED_END_OF_BLOCK" not in p7.stdout,
          p7.stdout[:200])

    print("\ncase_RED_exit5_khong_co_dau_hieu_resume_thi_FAIL_CLOSED")
    # Đối chứng ÂM (arch-review coord-2026-08-18 required_change #2). Fixture cũ chỉ có
    # đường HẠNH PHÚC: rc=5 kèm đúng dòng NOTE. Nhưng rc=5 là mã thoát của CẢ LỆNH
    # dispatch.sh — một lỗi thật ở tầng khác (oauth hết hạn, wrapper, nhánh tương lai) cũng
    # có thể trả 5 mà KHÔNG hề có chuỗi resume nào. Không có ca này thì lỗ hổng "tin con số,
    # không tin nội dung" luôn xanh: vòng fix biến mất im lặng, không question, không ai biết.
    OUT5_BAD = ("JOB Wags_20260818_014455 (from=Mike, timeout=1500s)\n"
                "Failed to authenticate: OAuth session expired and could not be refreshed\n"
                "WARNING: dispatch Wags ket thuc bat thuong (exit=5, job "
                "Wags_20260818_014455)\n")
    p6, notify6, postq6, posts6 = run_block(block, dispatch_rc=5, out=OUT5_BAD,
                                            label="coord-2026-08-18-bad")
    check("RED: exit=5 KHÔNG có dòng NOTE resume ⇒ VẪN phải post question (không nuốt)",
          postq6.strip() != "", "không post gì — vòng fix biến mất im lặng")
    b_topic = postq6.splitlines()[0] if postq6 else ""
    check("RED: topic là dispatch-failed, KHÔNG phải review-needed (fail-CLOSED)",
          "wags-autofix-dispatch-failed" in b_topic
          and "review-needed" not in b_topic, b_topic)
    check("RED: KHÔNG ghi bất kỳ status resume-pending nào", posts6.strip() == "",
          posts6[:300])
    check("RED: KHÔNG có chữ resume-pending ở đâu cả (kể cả question)",
          "resume-pending" not in postq6 and "resume-pending" not in posts6,
          (postq6 + posts6)[:300])
    check("RED: payload giữ dấu vết OAuth để người biết phải gia hạn cái gì",
          "authenticate" in postq6.lower() or "expired" in postq6.lower(), postq6[:300])
    check("RED: có báo động 🔴 (đây LÀ sự cố, khác ca exit=5 hợp lệ)",
          "🔴" in notify6, notify6[:300])
    check("RED: DỪNG pipeline", "REACHED_END_OF_BLOCK" not in p6.stdout, p6.stdout[:200])

    print("\ncase_CONTROL_dispatch_song_thi_khong_duoc_chan")
    p3, notify3, postq3, posts3 = run_block(block, dispatch_rc=0, out="moi thu binh thuong\n")
    check("CONTROL: dispatch exit=0 ⇒ KHÔNG post question dispatch-failed",
          postq3.strip() == "", postq3[:200])
    check("CONTROL: dispatch exit=0 ⇒ chạy tiếp xuống phần sau (không exit sớm)",
          "REACHED_END_OF_BLOCK" in p3.stdout, p3.stdout[:200])
    check("CONTROL: dispatch exit=0 ⇒ không báo động 🔴 oan", "🔴" not in notify3, notify3[:200])
    check("CONTROL: dispatch exit=0 ⇒ KHÔNG ghi status resume-pending oan",
          posts3.strip() == "", posts3[:200])

    print()
    if _fails:
        print(f"FAIL: {len(_fails)} assertion hỏng")
        for n in _fails:
            print(f"  - {n}")
        sys.exit(1)
    print("OK: toàn bộ assertion PASS")


if __name__ == "__main__":
    main()
