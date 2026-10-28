#!/usr/bin/env python3
"""Mutant vòng polish 21/10 (mục 1-5): mỗi mutant vá bin/vnindex_total_return.py của
worktree (argv[1]), chạy selfcheck, KHÔI PHỤC file; mutant phải làm selfcheck FAIL (chết)."""
import os
import subprocess
import sys

WT = sys.argv[1]
SRC = os.path.join(WT, "bin", "vnindex_total_return.py")
SC = os.path.join(WT, "bin", "vnindex_total_return_selfcheck.py")
CRON = os.path.join(WT, "bin", "fund_bench_cron.sh")
CRON_SC = os.path.join(WT, "bin", "fund_bench_cron_selfcheck.py")

MUT = {
    "P1 retry_of chỉ xét md5 (không dates/lý do/người)": (
        '                and all(prior.get(k_) == entry[k_] for k_ in ("dates", "reason", "confirmed_by")):',
        '                and True:'),
    "P2a undo ghi sổ SAU file": [
        ("            _append_log(log_path, entry)\n            _write_atomic(series_path, out)",
         "            _write_atomic(series_path, out)\n            _append_log(log_path, entry)")],
    "P2b undo không ghi sổ": (
        "            _append_log(log_path, entry)\n            _write_atomic(series_path, out)",
        "            _write_atomic(series_path, out)"),
    "P2c dòng sổ thiếu byte cũ ⇒ KeyError (bỏ kiểm UNDO_KEYS)": (
        "    if miss:\n        raise ValueError(", "    if False:\n        raise ValueError("),
    "P2d undo thiếu lý do vẫn chạy": (
        '    _need_reason_who(reason, confirmed_by, "hoàn tác")', "    pass"),
    "P2e undo chồng được phép": [
        ('        if last.get("kind") == "undo":\n            raise RestateRefused(', '        if False:\n            raise RestateRefused('),
        ('    if entry.get("kind") == "undo":\n        raise ValueError(', '    if False:\n        raise ValueError(')],
    "P2f undo không kiểm md5 file = md5_after ở tầng lệnh": [
        ('        if _md5(cur) != last.get("md5_after"):', '        if False:'),
        ('    if _md5(new_bytes) != entry["md5_after"]:', '    if False:')],
    "P2g undo không ghi 'undoes'": (
        '"undoes": last["md5_after"],', '"undoes": "",'),
    "P3a ack G4_MC bỏ NGÀY khỏi khoá": (
        '    return (date if isinstance(date, str) else date.isoformat(),\n            f"{G4_MC_ACK_PREFIX}',
        '    return ("",\n            f"{G4_MC_ACK_PREFIX}'),
    "P3b ack G4 số mã bỏ NGÀY khỏi khoá": (
        '    return (date if isinstance(date, str) else date.isoformat(), f"{G4_ACK_PREFIX}',
        '    return ("", f"{G4_ACK_PREFIX}'),
    "P3c mục ack không phải list ⇒ không kiểm (AttributeError)": (
        "    if not isinstance(v, list):\n        raise ValueError(f\"{path}: mục {sect} phải là list",
        "    if False:\n        raise ValueError(f\"{path}: mục {sect} phải là list"),
    "P3d phần tử mục ack không phải object ⇒ không kiểm": (
        "        if not isinstance(e, dict):\n            raise ValueError(f\"{path}: mục {sect} có phần tử",
        "        if False:\n            raise ValueError(f\"{path}: mục {sect} có phần tử"),
    "P5 --restate-sealed vẫn in seal_blocked": (
        '"anchor", "rows_before", "rows_after", "rechained_sealed")}}',
        '"anchor", "rows_before", "rows_after", "rechained_sealed")}, "seal_blocked": blocked}'),
    "P4a cron không đưa cặp cần ack lên đầu": (
        '    PAIRS="$(printf', '    PAIRS=""; : "$(printf', "cron"),
    "P4b cron không nói cảnh báo lặp": (
        "Cảnh báo lặp mỗi ngày T3-T7 tới khi dòng được seal hoặc ack.", "", "cron"),
}

def patch(text, pairs):
    for a, b in pairs:
        assert text.count(a) == 1, f"mẫu không khớp đúng 1 lần ({text.count(a)}): {a[:70]!r}"
        text = text.replace(a, b)
    return text


origs = {p: open(p, encoding="utf-8").read() for p in (SRC, CRON)}
dead = alive = 0
try:
    for name, spec in MUT.items():
        which = "vtr"
        if isinstance(spec, tuple) and len(spec) == 3:
            spec, which = spec[:2], spec[2]
        pairs = spec if isinstance(spec, list) else [spec]
        target, check = (CRON, CRON_SC) if which == "cron" else (SRC, SC)
        with open(target, "w", encoding="utf-8") as f:
            f.write(patch(origs[target], pairs))
        cp = subprocess.run([sys.executable, check], capture_output=True, text=True, env={**os.environ, "TZ": ""})
        last = (cp.stdout + cp.stderr).strip().splitlines()[-1][:160]
        with open(target, "w", encoding="utf-8") as f:
            f.write(origs[target])
        if cp.returncode != 0:
            dead += 1
            print(f"CHẾT  {name}: {last}")
        else:
            alive += 1
            print(f"SỐNG  {name}: {last}")
finally:
    for p, t in origs.items():
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
print(f"mutant chết {dead}/{dead + alive}")
sys.exit(1 if alive else 0)
