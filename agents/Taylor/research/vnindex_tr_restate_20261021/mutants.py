#!/usr/bin/env python3
"""Mutant cho --restate-sealed (A) + seal-guard (C): mỗi mutant vá bin/vnindex_total_return.py của
worktree (argv[1]), chạy selfcheck, KHÔI PHỤC file; mutant phải làm selfcheck FAIL (chết)."""
import os
import subprocess
import sys

WT = sys.argv[1]
SRC = os.path.join(WT, "bin", "vnindex_total_return.py")
SC = os.path.join(WT, "bin", "vnindex_total_return_selfcheck.py")

MUT = {
    "A1 đính chính không ghi sổ": (
        '            with open(log_path, "a", encoding="utf-8") as f:\n'
        '                f.write(json.dumps(entry, ensure_ascii=False) + "\\n")',
        '            with open(log_path + ".khac", "a", encoding="utf-8") as f:\n'
        '                f.write(json.dumps(entry, ensure_ascii=False) + "\\n")'),
    "A2 đính chính không nối lại đuôi provisional": (
        "            new, blocked = _merge_lines(staged, rebuilt, acks, series_path)",
        "            _merge_lines(staged, rebuilt, acks, series_path)\n"
        "            new, blocked = \"\".join(staged).encode(\"utf-8\"), []"),
    "A3 đính chính không nối lại dòng sealed sau": (
        '            else:\n                r = raw\n            y = float(r["y_gross"]) if r["y_gross"] else 0.0\n'
        '            ratio = float(r["vnindex"]) / float(prev["vnindex"])\n'
        '            r["tr_gross"] = _fmt(chain(float(prev["tr_gross"]), ratio, y, 1.0), 15)\n'
        '            r["tr_net"] = _fmt(chain(float(prev["tr_net"]), ratio, y, 1.0 - DIV_TAX_RATE), 15)',
        '            else:\n                r = raw\n            y = float(r["y_gross"]) if r["y_gross"] else 0.0\n'
        '            ratio = float(r["vnindex"]) / float(prev["vnindex"])\n'
        '            if r is not raw:\n'
        '                r["tr_gross"] = _fmt(chain(float(prev["tr_gross"]), ratio, y, 1.0), 15)\n'
        '                r["tr_net"] = _fmt(chain(float(prev["tr_net"]), ratio, y, 1.0 - DIV_TAX_RATE), 15)'),
    "A4 thiếu lý do vẫn chạy": (
        "    if not isinstance(reason, str) or not reason.strip():",
        "    if False:"),
    "A5 thiếu người xác nhận vẫn chạy": (
        "    if not isinstance(confirmed_by, str) or not confirmed_by.strip():",
        "    if False:"),
    "A7 đính chính bỏ kiểm cổng dòng sau đính chính": (
        "        if still:\n            raise RestateRefused(",
        "        if False:\n            raise RestateRefused("),
    "A8 'không đổi' so cả byte (built_at mới ⇒ ghi sổ đính chính rỗng)": (
        "        if [_without_built_at(x) for x in new_sealed] == [_without_built_at(x) for x in lines[1 + k:2 + last_sealed]]:",
        "        if new == old_b:"),
    "C1 bỏ seal-guard": (
        "        if seal and hist:\n            errs = seal_blockers(",
        "        if False:\n            errs = seal_blockers("),
    "C2 seal-guard không lan sang dòng sau": (
        "        seal = n - 1 - j >= SEAL_AFTER and not blocked\n",
        "        seal = n - 1 - j >= SEAL_AFTER\n"),
    "C3 seal-guard bỏ qua ack": (
        "            errs = seal_blockers(hist[-2] if len(hist) > 1 else None, hist[-1], pr, acks)",
        "            errs = seal_blockers(hist[-2] if len(hist) > 1 else None, hist[-1], pr, set())"),
    "C4 sổ ack hỏng ⇒ coi như không có ack (im lặng)": (
        "    try:\n        return load_acks(acks_path)\n    except (OSError, ValueError) as exc:              # sổ ack hỏng ⇒ không seal theo giả định",
        "    try:\n        return load_acks(acks_path)\n    except (OSError, ValueError) as exc:              # sổ ack hỏng ⇒ không seal theo giả định\n        return set()"),
}

orig = open(SRC, encoding="utf-8").read()
dead = alive = 0
try:
    for name, pair in MUT.items():
        if pair is None:
            continue
        a, b = pair
        assert orig.count(a) == 1, f"{name}: mẫu không khớp đúng 1 lần ({orig.count(a)})"
        with open(SRC, "w", encoding="utf-8") as f:
            f.write(orig.replace(a, b))
        cp = subprocess.run([sys.executable, SC], capture_output=True, text=True, env={**os.environ, "TZ": ""})
        last = (cp.stdout + cp.stderr).strip().splitlines()[-1][:160]
        if cp.returncode != 0:
            dead += 1
            print(f"CHẾT  {name}: {last}")
        else:
            alive += 1
            print(f"SỐNG  {name}: {last}")
finally:
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(orig)
print(f"mutant chết {dead}/{dead + alive}")
sys.exit(1 if alive else 0)
