#!/usr/bin/env python3
"""Selfcheck: mọi hàm mà `_bg_wrapper`/`_job_watcher` của `dispatch.sh` GỌI (TRỰC TIẾP hoặc
QUA bất kỳ hàm trung gian nào) phải nằm trong khối `export -f` ngay dưới (~dòng 1655) —
`_bg_wrapper`/`_job_watcher` chạy trong tiến trình con `bash -c NAME` (nhánh --bg, xem comment
tại dispatch.sh ngay trên dòng export -f), và `bash -c` chỉ thấy hàm shell nào đã được
`export -f`; thiếu một hàm trong chuỗi gọi ⇒ rc=127 "command not found" NGAY LÚC GỌI, bị
`if _ten_ham ...; then` nuốt mất (rơi xuống nhánh else) và KHÔNG AI THẤY vì `_detached_spawn`
trỏ stderr của tiến trình nền vào /dev/null.

Bug gốc (code-quality 2026-10-11): `_maybe_fallback_provider_on_usage_limit` (thêm commit
0a990021) được gọi trong `_bg_wrapper_run` nhưng quên thêm vào export -f ⇒ fallback sang
provider khác khi hết usage-limit KHÔNG chạy ở nhánh --bg. Bản selfcheck ĐẦU TIÊN (cùng ngày)
chỉ quét lệnh gọi TRỰC TIẾP trong thân `_bg_wrapper`/`_bg_wrapper_run`, bỏ sót (a) hàm không bắt
đầu bằng `_` hoặc có thụt lề (JSET/SUMMARY/_preempt_wakeup), (b) lệnh gọi GIÁN TIẾP qua 1 hàm
trung gian (`_looks_like_usage_limit` gọi từ TRONG `_maybe_fallback_provider_on_usage_limit`),
và (c) không kiểm `_job_watcher` — arch-reviewer bắt bằng mutation-test, bản này vá cả 3.

CÁCH KIỂM: trích NGUYÊN văn bản dispatch.sh thật bằng parser brace-aware (không chép tay),
tĩnh — không chạy dispatch, không side-effect. Phần B chạy LẠI đúng hàm kiểm A trên nhiều tập
export bị mutate (bỏ từng hàm một, kể cả hàm gọi gián tiếp) để tự chứng minh detector bắt được.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(os.path.dirname(HERE), "bin", "dispatch.sh")

pass_n = 0
fail_n = 0


def ck(label, cond, detail=""):
    global pass_n, fail_n
    if cond:
        print(f"  PASS {label}")
        pass_n += 1
    else:
        print(f"  FAIL {label}" + (f"   ({detail})" if detail else ""))
        fail_n += 1


FUNC_DEF_RE = re.compile(r'^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)\(\)[ \t]*\{[ \t]*(#.*)?$')
FUNC_ONELINER_RE = re.compile(r'^([ \t]*)([A-Za-z_][A-Za-z0-9_]*)\(\)[ \t]*\{(.*)\}[ \t]*;?[ \t]*(#.*)?$')


def parse_functions(lines):
    """-> {name: (start_idx, end_idx, body_text)}; idx 0-based, inclusive của def/end brace."""
    funcs = {}
    i = 0
    n = len(lines)
    while i < n:
        m1 = FUNC_ONELINER_RE.match(lines[i])
        m2 = None if m1 else FUNC_DEF_RE.match(lines[i])
        if m1:
            name = m1.group(2)
            funcs[name] = (i, i, m1.group(3))
            i += 1
            continue
        if m2:
            indent, name = m2.group(1), m2.group(2)
            close_re = re.compile(r'^' + re.escape(indent) + r'\}[ \t]*(#.*)?$')
            end = None
            for j in range(i + 1, n):
                if close_re.match(lines[j]):
                    end = j
                    break
            if end is None:
                funcs[name] = (i, i, "")  # không tìm được biên -> thân rỗng, báo riêng ở dưới
            else:
                funcs[name] = (i, end, "\n".join(lines[i + 1:end]))
            # KHÔNG nhảy tới end+1: tiếp tục quét TỪNG DÒNG để bắt cả hàm LỒNG BÊN TRONG thân
            # hàm này (ví dụ _discord/_log_state lồng trong _job_watcher) — is_nested() cần cả
            # hai phạm vi (lồng + chứa) đã có trong `funcs` mới xác định containment đúng.
            i += 1
            continue
        i += 1
    return funcs


def strip_full_line_comments(text):
    return "\n".join("" if ln.strip().startswith("#") else ln for ln in text.split("\n"))


def calls_in(text, candidate_names):
    text = strip_full_line_comments(text)
    found = set()
    for name in candidate_names:
        if re.search(r'(?<![A-Za-z0-9_])' + re.escape(name) + r'(?![A-Za-z0-9_])', text):
            found.add(name)
    return found


def is_nested(name, funcs):
    s, e, _ = funcs[name]
    for other, (os_, oe, _b) in funcs.items():
        if other == name:
            continue
        if os_ < s and e < oe:
            return True
    return False


def required_exports(entry_points, funcs):
    """Closure TRỰC TIẾP + GIÁN TIẾP các hàm phải export, bắt đầu từ entry_points."""
    all_names = list(funcs.keys())
    required = set()
    visited = set()
    worklist = list(entry_points)
    while worklist:
        name = worklist.pop()
        if name in visited:
            continue
        visited.add(name)
        if name not in funcs:
            continue  # lệnh ngoài (python3, grep, ...), không phải hàm bash trong file
        if not is_nested(name, funcs):
            required.add(name)
        _, _, body = funcs[name]
        for callee in calls_in(body, [n for n in all_names if n != name]):
            if callee not in visited:
                worklist.append(callee)
    return required


def missing_exports(required, exported):
    return required - exported


def parse_export_f_block(lines):
    """-> set tên trong khối `export -f ...` (gộp mọi dòng nối bằng \\)."""
    names = set()
    i = 0
    n = len(lines)
    while i < n:
        if re.match(r'^[ \t]*export -f\b', lines[i]):
            block = [lines[i]]
            j = i
            while block[-1].rstrip().endswith("\\"):
                j += 1
                block.append(lines[j])
            joined = " ".join(b.rstrip("\\").strip() for b in block)
            joined = re.sub(r'^export -f\b', '', joined)
            names = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', joined))
            return names
        i += 1
    return names


def main():
    print("[1] trích hàm + khối export -f từ dispatch.sh thật")
    with open(D) as fh:
        lines = fh.read().split("\n")
    funcs = parse_functions(lines)
    exported = parse_export_f_block(lines)

    ck("trích được >= 20 hàm (đổi cấu trúc file mạnh thì con số này tụt rõ, không im lặng)",
       len(funcs) >= 20, f"chỉ thấy {len(funcs)}")
    for must in ("_bg_wrapper", "_bg_wrapper_run", "_job_watcher",
                 "_maybe_fallback_provider_on_usage_limit", "JSET", "SUMMARY"):
        ck(f"tìm thấy định nghĩa hàm {must}", must in funcs, "parser không khớp được biên hàm")
    ck("trích được khối export -f (không rỗng)", len(exported) > 5, f"{exported}")

    print("\n[2] closure TRỰC TIẾP+GIÁN TIẾP từ 2 entry point --bg (_bg_wrapper, _job_watcher)")
    required = required_exports(["_bg_wrapper", "_job_watcher"], funcs)
    ck("closure tìm thấy _bg_wrapper_run (gọi từ _bg_wrapper)", "_bg_wrapper_run" in required)
    ck("closure tìm thấy _maybe_fallback_provider_on_usage_limit (gọi từ _bg_wrapper_run)",
       "_maybe_fallback_provider_on_usage_limit" in required)
    ck("closure tìm thấy _looks_like_usage_limit (GIÁN TIẾP, gọi từ TRONG hàm fallback, "
       "không trực tiếp từ _bg_wrapper_run)", "_looks_like_usage_limit" in required)
    ck("closure tìm thấy JSET/SUMMARY (không bắt đầu bằng _)",
       {"JSET", "SUMMARY"} <= required)
    ck("closure tìm thấy _preempt_wakeup (có thụt lề 2 space)", "_preempt_wakeup" in required)
    ck("closure KHÔNG yêu cầu export _discord/_log_state (định nghĩa LỒNG BÊN TRONG "
       "thân _job_watcher mỗi lần hàm đó chạy — không cần export riêng)",
       not ({"_discord", "_log_state"} & required), f"{required & {'_discord', '_log_state'}}")

    print("\n[3] export -f THẬT trong dispatch.sh hiện tại phải phủ hết closure")
    missing_real = missing_exports(required, exported)
    ck("mọi hàm trong closure đều có trong export -f thật", not missing_real, f"thiếu: {missing_real}")

    print("\n[4] mutation — chạy LẠI đúng hàm kiểm ở [3] trên export -f bị bớt từng hàm, "
          "phải đỏ (chứng minh detector có tác dụng, không phải tautology)")
    for victim in ("_maybe_fallback_provider_on_usage_limit", "_looks_like_usage_limit",
                   "JSET", "SUMMARY", "_preempt_wakeup", "_current_resume_count",
                   "_parse_reset_epoch", "_emit_full_prompt", "_job_watcher"):
        mutant = exported - {victim}
        miss = missing_exports(required, mutant)
        ck(f"bớt '{victim}' khỏi export -f -> detector đỏ (victim nằm trong missing)",
           victim in miss, f"missing={miss}")

    print(f"\n=== {pass_n}/{pass_n + fail_n} assertion PASS ===")
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
