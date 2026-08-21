#!/usr/bin/env python3
"""Selfcheck cho nhánh CHỐNG-ĐẢO-ĐỐI-SỐ của bin/notify_thread.sh (Wags, 2026-08-12).

Vì sao có file này: chữ ký `notify_thread.sh "<message>" [topic]` đi NGƯỢC trực giác
`notify <where> <what>`, nên call site do agent viết tay gọi đảo thứ tự — và bản cũ nuốt
nguyên tin nhắn (3 lần trong 6 ngày, xem logs/notify_thread_errors.log). Test chạy CHÍNH
script production trên một ROOT giả, chỉ thay ĐÚNG một đường: khối POST Discord đổi thành
một dòng `SENT<TAB>topic<TAB>message` ra stdout. Neo thay thế được assert tường minh — đổi
transport mà quên sửa test thì test CHẾT ngay chứ không PASS giả.

Chạy: python3 mike/bin/notify_thread_argswap_selfcheck.py
      python3 mike/bin/notify_thread_argswap_selfcheck.py --red   # chạy trên bản TRƯỚC fix
                                                                   # (đọc từ git HEAD)
"""
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "bin", "notify_thread.sh")
CHAN = os.path.join(ROOT, "bin", "discord_channel.sh")

# Neo transport khớp bằng REGEX chứ không phải chuỗi tuyệt đối (sửa 2026-08-22, weekly ops
# audit): bản cũ so literal `python3 - "$thread_id" "$msg" << 'PY'`, nên khi notify_thread.sh
# thêm tham số thứ 3 `"$_stamp_flag"` (hỗ trợ --no-stamp, 2026-08-21) selfcheck này FATAL và
# đỏ im lặng suốt. Cái BẤT BIẾN cần neo là "heredoc python3 nhận $thread_id + $msg", không
# phải danh sách tham số đóng băng tại một ngày. Thêm tham số ⇒ vẫn khớp; đổi HẲN transport
# (không còn heredoc python3) ⇒ vẫn FATAL đúng như thiết kế.
ANCHOR_RE = re.compile(
    r'python3 -[^\n]*"\$thread_id"[^\n]*"\$msg"[^\n]*<< *\'PY\'\n')
ANCHOR_END = "\nPY\n"
# message được base64 hoá: message THẬT nhiều dòng, in thô thì dòng SENT bị vỡ và test sẽ
# báo "mất nội dung" trong khi script hoàn toàn đúng (đã cắn 1 lần khi viết file này).
FAKE_TRANSPORT = ('printf \'SENT\\t%s\\t%s\\n\' "$thread_id" '
                  '"$(printf \'%s\' "$msg" | base64 -w0)"\n')

TOPIC_NAME = "architecture"
LONG_MSG = "🩺 Winston ops-autofix — ops-health-SpaceX\n\n**Kết luận: KHÔNG có bug.**\nDòng 3."

fails = []
passes = []


def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"{'PASS' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def build_root(script_text):
    """Dựng ROOT giả: bin/notify_thread.sh (đã thay transport) + bin/discord_channel.sh THẬT
    + registry THẬT. Giữ discord_channel.sh thật để nhánh phân giải tên đi đúng đường
    production (đây chính là chỗ quyết định có đảo hay không)."""
    d = tempfile.mkdtemp(prefix="nt_selfcheck_")
    os.makedirs(os.path.join(d, "bin"))
    os.makedirs(os.path.join(d, "kb"))
    m = ANCHOR_RE.search(script_text)
    if not m:
        raise SystemExit(
            "FATAL: không tìm thấy neo transport %r trong notify_thread.sh — transport đã đổi, "
            "SỬA SELFCHECK NÀY thay vì bỏ qua." % ANCHOR_RE.pattern)
    i = m.start()
    j = script_text.find(ANCHOR_END, m.end() - 1)
    if j < 0:
        raise SystemExit("FATAL: không tìm thấy hết heredoc PY sau neo transport.")
    patched = script_text[:i] + FAKE_TRANSPORT + script_text[j + len(ANCHOR_END):]
    p = os.path.join(d, "bin", "notify_thread.sh")
    with open(p, "w", encoding="utf-8") as f:
        f.write(patched)
    os.chmod(p, 0o755)
    shutil.copy2(CHAN, os.path.join(d, "bin", "discord_channel.sh"))
    shutil.copy2(os.path.join(ROOT, "kb", "discord_channels.json"),
                 os.path.join(d, "kb", "discord_channels.json"))
    return d


def run(root, args, env_extra=None):
    env = dict(os.environ)
    env.pop("DISCORD_THREAD_ID", None)
    env.update(env_extra or {})
    r = subprocess.run(["bash", os.path.join(root, "bin", "notify_thread.sh")] + args,
                       capture_output=True, text=True, env=env, timeout=60)
    log = os.path.join(root, "logs", "notify_thread_errors.log")
    logtxt = open(log, encoding="utf-8").read() if os.path.exists(log) else ""
    return r, logtxt


def sent(stdout):
    """Trả (topic, message) từ dòng SENT, hoặc None nếu không gửi."""
    for line in stdout.splitlines():
        if line.startswith("SENT\t"):
            parts = line.split("\t", 2)
            raw = parts[2] if len(parts) > 2 else ""
            return (parts[1], base64.b64decode(raw).decode("utf-8") if raw else "")
    return None


def real_id(name):
    with open(os.path.join(ROOT, "kb", "discord_channels.json"), encoding="utf-8") as f:
        return str(json.load(f)["channels"][name]).strip('"')


def suite(script_text, label):
    """Trả về list (case_name, ok)."""
    out = []

    def rec(n, ok, detail=""):
        out.append((n, ok, detail))

    rid = real_id(TOPIC_NAME)
    if isinstance(rid, str) and not rid.isdigit():
        m = re.search(r"\d{17,20}", rid)
        rid = m.group(0) if m else rid

    # 1. Đường ĐÚNG, topic bằng TÊN.
    d = build_root(script_text)
    r, log = run(d, ["hello world message", TOPIC_NAME])
    s = sent(r.stdout)
    rec("1 dung-thu-tu/ten: gui dung topic+message",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == "hello world message",
        f"rc={r.returncode} sent={s}")
    rec("1b dung-thu-tu/ten: KHONG ghi error log", log == "", log[:120])
    shutil.rmtree(d)

    # 2. Đường ĐÚNG, topic bằng ID trần.
    d = build_root(script_text)
    r, log = run(d, [LONG_MSG, rid])
    s = sent(r.stdout)
    rec("2 dung-thu-tu/ID-tran: passthrough",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == LONG_MSG,
        f"rc={r.returncode} sent={s}")
    shutil.rmtree(d)

    # 3. ĐẢO: tên topic ở vị trí 1, message dài ở vị trí 2 — ĐÚNG ca thật 08-07/08-10/08-12.
    d = build_root(script_text)
    r, log = run(d, [TOPIC_NAME, LONG_MSG])
    s = sent(r.stdout)
    rec("3 DAO/ten: van gui duoc, khong nuot tin nhan",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == LONG_MSG,
        f"rc={r.returncode} sent={s}")
    rec("3b DAO/ten: co ghi 1 dong canh bao 'DOI SO BI DAO' de call site duoc sua",
        "DOI SO BI DAO" in log, log[:160])
    rec("3c DAO/ten: KHONG ghi 'TIN NHAN KHONG GUI' (dong log phai DUNG SU THAT)",
        "TIN NHAN KHONG GUI" not in log, log[:160])
    shutil.rmtree(d)

    # 4. ĐẢO với ID trần ở vị trí 1.
    d = build_root(script_text)
    r, log = run(d, [rid, LONG_MSG])
    s = sent(r.stdout)
    rec("4 DAO/ID-tran: van gui duoc",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == LONG_MSG,
        f"rc={r.returncode} sent={s}")
    shutil.rmtree(d)

    # 5. Cả hai vị trí đều KHÔNG phải topic → phải GIỮ hành vi cũ: fail loud, không đoán.
    d = build_root(script_text)
    r, log = run(d, ["mot message binh thuong", "khong_co_topic_nay"])
    rec("5 ca-hai-sai: van fail loud, khong gui",
        r.returncode != 0 and sent(r.stdout) is None, f"rc={r.returncode}")
    rec("5b ca-hai-sai: log 'KHONG phan giai duoc topic'",
        "KHONG phan giai duoc topic" in log, log[:160])
    shutil.rmtree(d)

    # 6. Chống dương-tính-giả: message NGẮN không dấu cách nhưng KHÔNG phải tên topic,
    #    topic vị trí 2 sai → không được im lặng coi là đảo.
    d = build_root(script_text)
    r, log = run(d, ["deploy_xong", "topic_sai_hoan_toan"])
    rec("6 khong-duong-tinh-gia: arg1 ngan nhung khong phai topic => van fail",
        r.returncode != 0 and sent(r.stdout) is None, f"rc={r.returncode}")
    shutil.rmtree(d)

    # 7. Chống dương-tính-giả nguy hiểm nhất: message CHÍNH LÀ tên topic hợp lệ, mà vị trí 2
    #    cũng hợp lệ → đường thành công thắng, KHÔNG được đảo.
    d = build_root(script_text)
    r, log = run(d, [TOPIC_NAME, TOPIC_NAME])
    s = sent(r.stdout)
    rec("7 ca-hai-deu-la-ten-topic: khong dao (duong thanh cong thang)",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == TOPIC_NAME,
        f"rc={r.returncode} sent={s}")
    rec("7b ca-hai-deu-la-ten-topic: khong ghi canh bao dao", "DOI SO BI DAO" not in log, log[:160])
    shutil.rmtree(d)

    # 8. Không truyền vị trí 2, có $DISCORD_THREAD_ID → hành vi cũ, tuyệt đối không đảo.
    d = build_root(script_text)
    r, log = run(d, [TOPIC_NAME], {"DISCORD_THREAD_ID": rid})
    s = sent(r.stdout)
    rec("8 thieu-arg2 + env: dung env, khong dao",
        r.returncode == 0 and s is not None and s[0] == rid and s[1] == TOPIC_NAME,
        f"rc={r.returncode} sent={s}")
    shutil.rmtree(d)

    # 9. Không truyền vị trí 2, không env → giữ nguyên fail-closed cũ.
    d = build_root(script_text)
    r, log = run(d, ["mot message"])
    rec("9 thieu-arg2 + khong env: van fail-closed",
        r.returncode != 0 and sent(r.stdout) is None, f"rc={r.returncode}")
    shutil.rmtree(d)

    # 10. Message nhiều dòng KHÔNG bị cắt/đổi khi đi qua nhánh đảo (nội dung nguyên vẹn).
    d = build_root(script_text)
    r, _ = run(d, [TOPIC_NAME, LONG_MSG])
    s = sent(r.stdout)
    rec("10 DAO: noi dung message nguyen ven tung ky tu",
        s is not None and s[1] == LONG_MSG, f"sent={s}")
    shutil.rmtree(d)

    return out


def main():
    red = "--red" in sys.argv
    if red:
        # ĐỐI CHỨNG ĐỎ: lấy bản notify_thread.sh ở git HEAD (TRƯỚC fix) và chạy Y HỆT bộ ca.
        # Ca 3/4/10 PHẢI FAIL ở đây — nếu chúng XANH cả trên bản cũ thì bộ test này không
        # kiểm chứng được gì.
        text = subprocess.run(["git", "-C", ROOT, "show", "HEAD:bin/notify_thread.sh"],
                              capture_output=True, text=True, check=True).stdout
        label = "RED (HEAD, truoc fix)"
    else:
        text = open(SRC, encoding="utf-8").read()
        label = "cay lam viec (sau fix)"
    print(f"=== notify_thread argswap selfcheck — {label}")
    results = suite(text, label)
    for n, ok, detail in results:
        check(n, ok, detail)
    print(f"\n{len(passes)} PASS / {len(fails)} FAIL")
    if red:
        must_fail = [n for n, ok, _ in results if n.startswith(("3 ", "3b", "3c", "4 ", "10"))]
        actually_failed = [n for n in must_fail if n in fails]
        print(f"[RED control] ca phai ĐỎ tren ban cu: {len(actually_failed)}/{len(must_fail)} "
              f"= {actually_failed}")
        return 0 if len(actually_failed) == len(must_fail) else 1
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
