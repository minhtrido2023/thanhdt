#!/usr/bin/env python3
"""Selfcheck thesis_card_watch.build (dữ liệu bơm) + notify stub. env -u TZ / TZ=Pacific/Kiritimati."""
import copy
import datetime as dt
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thesis_card_watch as W  # noqa: E402
import thesis_cards as T  # noqa: E402

fails = []


def check(n, c, d=""):
    print(("PASS " if c else "FAIL ") + n + (f"  [{d}]" if d and not c else ""))
    if not c:
        fails.append(n)


doc = T.read_json(T.CARDS)
asof = dt.date(2026, 11, 24)
pos = {"SpaceX": {"FPT": {"qty": 800, "cost": 51137.5, "market": 45000}, "NNC": {"qty": 400, "cost": 46675, "market": 47450},
                  "VGS": {"qty": 2300, "cost": 20000, "market": 19200}},
       "ZaloPay": {"FPT": {"qty": 500, "cost": 51160, "market": 45000}, "NNC": {"qty": 300, "cost": 46950, "market": 47450},
                   "VGS": {"qty": 1500, "cost": 20000, "market": 19200}}}
ts = {"SpaceX": "2026-11-20T23:30:10", "ZaloPay": "2026-11-20T23:30:08"}
L, n = W.build(doc, asof, pos, ts, "dnse_raw_2026-11-20.jsonl")
txt = "\n".join(L)
check("mốc 27/11 (còn 3 ngày) được nhắc", "FPT-M1" in txt and "còn 3 ngày" in txt)
check("mốc 30/11 (6 ngày) chưa nhắc", "FPT-M2" not in txt)
check("FPT −12% chưa chạm ngưỡng 15%", "SpaceX FPT: giá 45.000 vs vốn 51.137,5 = -12,0%" in txt and "ZaloPay FPT: giá 45.000 vs vốn 51.160,0 = -12,0%" in txt and "T23:30:10." not in txt and "MỞ RÀ" not in txt, txt)
# mutation: giá 43.000 ⇒ −15,9% ⇒ mở rà
p2 = copy.deepcopy(pos)
p2["SpaceX"]["FPT"]["market"] = 43000
L2, n2 = W.build(doc, asof, p2, ts, "f")
check("giá −15,9% ⇒ MỞ RÀ 48 GIỜ (không phải lệnh bán)", any("MỞ RÀ 48 GIỜ" in x and "không phải lệnh bán" in x for x in L2))
check("đúng −15,0% ⇒ chạm", any("MỞ RÀ" in x for x in W.build(doc, asof, {"SpaceX": {"FPT": {"qty": 1, "cost": 100, "market": 85}}}, ts, "f")[0]))
check("−14,9% ⇒ chưa chạm", not any("MỞ RÀ" in x for x in W.build(doc, asof, {"SpaceX": {"FPT": {"qty": 1, "cost": 100, "market": 85.1}}}, ts, "f")[0]))
# quá hạn
L3, _ = W.build(doc, dt.date(2026, 12, 12), pos, ts, "f")
check("quá hạn chưa chấm ⇒ QUÁ HẠN", any("QUÁ HẠN" in x and "FPT-M1" in x for x in L3))
d4 = copy.deepcopy(doc)
for c in d4["cards"]:
    for m in c["milestones"]:
        if m["id"] == "FPT-M1":
            m["status"] = "checked_ok"
            m["checked_at"] = "2026-11-28"
L4, _ = W.build(d4, dt.date(2026, 12, 12), pos, ts, "f")
check("mốc đã chấm không nhắc lại", not any("FPT-M1" in x for x in L4))
# thẻ quá 30 ngày
L5, _ = W.build(doc, dt.date(2026, 12, 30), pos, ts, "f")
check("thẻ >30 ngày ⇒ nhắc rà", any(x.startswith("- FPT: last_review_at") for x in L5))
# fail-loud thiếu giá
L6, _ = W.build(doc, asof, {}, {}, None)
check("thiếu dữ liệu giá ⇒ nói thẳng lý do", any("KHÔNG đọc được giá" in x for x in L6))
L7, _ = W.build(doc, asof, {"SpaceX": pos["SpaceX"]}, ts, "f")
check("thiếu 1 account ⇒ cảnh báo, không đoán", any("ZaloPay: không có bản ghi" in x for x in L7))
L8, _ = W.build(doc, dt.date(2026, 11, 30), pos, ts, "f")
check("giá cũ >4 ngày ⇒ cảnh báo", any("giá cũ" in x for x in L8))
# notify stub: lệnh được gọi với TÊN kênh (không ID trần)
with tempfile.TemporaryDirectory() as td:
    stub = os.path.join(td, "stub.sh")
    out = os.path.join(td, "out.txt")
    open(stub, "w").write(f'#!/bin/bash\necho "$2" > {out}\n')
    os.chmod(stub, 0o755)
    env = dict(os.environ, TCW_NOTIFY_CMD=stub)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "thesis_card_watch.py"), "--asof", "2026-11-24", "--notify"],
                       env=env, capture_output=True, text=True)
    check("--notify gọi kênh theo TÊN", r.returncode == 0 and open(out).read().strip() == "discretionary_stocks", r.stderr)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "thesis_card_watch.py"), "--asof", "2026-11-24", "--notify", "--dry-run"],
                       env=env, capture_output=True, text=True)
    check("--dry-run không POST", "notify=off" in r.stdout)
check("kênh có trong discord_channels.json", "discretionary_stocks" in T.read_json(os.path.join(T.MIKE, "kb", "discord_channels.json"))["channels"])
print(f"\n{'ALL PASS' if not fails else 'FAILED: ' + str(fails)}  (TZ={os.environ.get('TZ')!r})")
sys.exit(1 if fails else 0)
