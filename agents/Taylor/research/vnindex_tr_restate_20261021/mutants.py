#!/usr/bin/env python3
"""Mutant cho --restate-sealed (A) + seal-guard (C): mỗi mutant vá bin/vnindex_total_return.py của
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
        "        if all(_without_built_at(rows_after[d]) == _without_built_at(rows_before[d]) for d in rows_after):",
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
    "X7 bất biến C quét từ want[-1] thay vì want[0]": (
        "        for i in range(npos[want[0]], len(nrows)):",
        "        for i in range(npos[want[-1]], len(nrows)):"),
    "X9 ghi file TRƯỚC sổ (chết giữa chừng ⇒ file đổi mà không có sổ)": [
        ("        if write:\n            # sổ TRƯỚC, file SAU",
         "        if write:\n            _write_atomic(series_path, new)\n            # sổ TRƯỚC, file SAU"),
        ("            _write_atomic(series_path, new)\n    return {", "            pass\n    return {")],
    "X11 dòng chỉ-nối-lại được tính là có đổi": (
        "        if all(_without_built_at(rows_after[d]) == _without_built_at(rows_before[d]) for d in rows_after):",
        "        if [_without_built_at(x) for x in new_sealed] == [_without_built_at(x) for x in lines[1 + k:2 + last_sealed]]:"),
    "B3a sổ không lưu byte cũ dòng sealed bị nối lại": (
        "                rechained_before[d] = lines[1 + i]", "                pass"),
    "B3b sổ không lưu đuôi provisional cũ": (
        '"tail_before": lines[2 + last_sealed:],', '"tail_before": [],'),
    "B5 chạy lại sau crash không đánh dấu retry_of": (
        '        if prior and prior.get("series") == entry["series"]',
        '        if False and prior and prior.get("series") == entry["series"]'),
    "B2a ack vốn hoá không ràng giá trị": (
        'f"{G4_MC_ACK_PREFIX}:{int(round(mc_prev))}>{int(round(mc))}")',
        'f"{G4_MC_ACK_PREFIX}")'),
    "B2b ack vốn hoá bị bỏ qua": (
        '                g4_mc_ack_key(r["date"], p["mc_members_vnd"], r["mc_members_vnd"]) not in acks:',
        '                True:'),
    "B1 cron không báo seal_blocked": (
        '  if [ -n "$SEAL" ]; then', '  if false; then', "cron"),
    "C4 sổ ack hỏng ⇒ coi như không có ack (im lặng)": (
        "    try:\n        return load_acks(acks_path)\n    except (OSError, ValueError) as exc:              # sổ ack hỏng ⇒ không seal theo giả định",
        "    try:\n        return load_acks(acks_path)\n    except (OSError, ValueError) as exc:              # sổ ack hỏng ⇒ không seal theo giả định\n        return set()"),
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
