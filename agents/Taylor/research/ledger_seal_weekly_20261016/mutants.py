#!/usr/bin/env python3
"""Mutation cho ledger_seal_weekly.py: mỗi đột biến ghi tạm cạnh bản gốc (cùng bin/ ⇒ import y hệt),
chạy selfcheck với LEDGER_SEAL_WRAPPER=<đột biến>; selfcheck phải FAIL (rc≠0) ⇒ "bị bắt". Dùng: mutants.py <bin_dir>"""
import os, subprocess, sys
BIN = os.path.abspath(sys.argv[1])
SRC = open(os.path.join(BIN, "ledger_seal_weekly.py")).read()
M = [
 ("M1 gỡ fail-closed (TK lỗi ⇒ đi tiếp TK sau)", "            print(tail(out), flush=True)\n            return 1", "            print(tail(out), flush=True)\n            continue"),
 ("M2 gỡ idempotent mốc (luôn thêm)", "    if latest == line:\n        return False", "    if False:\n        return False"),
 ("M3 thêm --accept-preclose vào lệnh CLI", '"--asof", asof.isoformat()]', '"--asof", asof.isoformat(), "--accept-preclose", f"{asof}=auto"]'),
 ("M4 mọi rc=2 coi là NothingToSeal", "return rc == 2 and re.search(", "return rc == 2 or re.search("),
 ("M5 không gỡ WC_ROOT", 'os.environ.pop("WC_ROOT", None)', 'pass'),
 ("M6 asof bỏ điều kiện ≥5 phiên", "            if lag >= min_lag:", "            if True:"),
 ("M7 gỡ guard cây canonical", "    bad = guard_tree()", '    bad = ""'),
 ("M8 gỡ kiểm tiến trình ghi nav_history", "            if writers:", "            if False:"),
 ("M9 nhận SEAL_MD5 của TK khác", "and m.group(1) == account]", "]"),
 ("M10 gỡ khung giờ 19:00-22:00", "            if WRITE_WINDOW[0] <= now.time() < WRITE_WINDOW[1]:", "            if False:"),
 ("M11 now() không neo ICT", "    return datetime.datetime.now(ICT)", "    return datetime.datetime.now()"),
 ("M12 bus lỗi vẫn rc=0", '                  f"{bout[-400:]} — post tay finding {topic}; KHÔNG chốt gì thêm.", flush=True)\n            return 1', '                  f"{bout[-400:]} — post tay finding {topic}; KHÔNG chốt gì thêm.", flush=True)\n            continue'),
 ("M14 timeout CLI nuốt im (rc=0)", "        return 124, part +", "        return 0, part +"),
 ("M13 khớp writer theo chuỗi con", "if any(os.path.basename(a) in NAV_WRITERS for a in args)", "if any(w.split('.')[0] in ' '.join(args) for w in NAV_WRITERS)"),
]
caught = 0
for name, old, new in M:
    assert SRC.count(old) == 1, name
    p = os.path.join(BIN, f"ledger_seal_weekly_mut{M.index((name, old, new)) + 1}.py")
    open(p, "w").write(SRC.replace(old, new))
    try:
        for tz in (None, "Pacific/Kiritimati"):
            env = {k: v for k, v in os.environ.items() if k != "TZ"}
            if tz: env["TZ"] = tz
            env["LEDGER_SEAL_WRAPPER"] = p
            r = subprocess.run([sys.executable, os.path.join(BIN, "ledger_seal_weekly_selfcheck.py")],
                               capture_output=True, text=True, env=env, timeout=900)
            fl = [l.strip() for l in r.stdout.splitlines() if l.startswith("  FAIL")]
            ok = r.returncode != 0
            print(f"{'BẮT' if ok else 'SÓT'} TZ={tz or '<unset>'} {name} — {len(fl)} FAIL: {'; '.join(x[7:60] for x in fl[:3])}")
            caught += ok
    finally:
        os.unlink(p)
print(f"TỔNG: {caught}/{2 * len(M)} bị bắt")
sys.exit(0 if caught == 2 * len(M) else 1)
