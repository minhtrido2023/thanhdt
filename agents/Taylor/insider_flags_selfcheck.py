#!/usr/bin/env python3
"""insider_flags_selfcheck.py — kiểm tra writer atomic + reader cửa sổ 2 đầu.

Không gọi BQ (phần đối chiếu số liệu thật nằm ở `insider_flags.py --selftest`).
Chạy: /home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/insider_flags_selfcheck.py
"""
import json
import os
import sys
import tempfile

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
sys.path.insert(0, os.path.join(WC, "mike", "agents", "Taylor"))

import insider_flags as W
from anomaly_gate import insider_sell_flagged

ok = True


def check(label, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(f"  {'PASS' if cond else 'FAIL'} — {label}{(' | ' + extra) if extra else ''}")


REC = [{"ticker": "AAA", "last_alert": "2026-06-01", "tier": "W", "reasons": "INSIDER_SELL_1PCT",
        "sell_pct_osh": 0.05, "n_sellers": 2, "window_end": "2026-06-10"}]

with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "insider_flags.json")

    print("# 1. Ghi lần đầu + idempotent")
    W.write_flags(REC, p)
    first = open(p, encoding="utf-8").read()
    W.write_flags(REC, p)
    check("chạy 2 lần cùng input → file y hệt", open(p, encoding="utf-8").read() == first)
    check("không để lại .tmp", not os.path.exists(p + ".tmp"))

    print("# 2. Merge: last_alert MỚI HƠN thì cập nhật, CŨ HƠN thì giữ nguyên")
    newer = [dict(REC[0], last_alert="2026-07-01", sell_pct_osh=0.09)]
    W.write_flags(newer, p)
    check("cờ mới hơn ghi đè", json.load(open(p))["AAA"]["sell_pct_osh"] == 0.09)
    older = [dict(REC[0], last_alert="2026-05-01", sell_pct_osh=0.02)]
    W.write_flags(older, p)
    d = json.load(open(p))["AAA"]
    check("cờ cũ hơn KHÔNG ghi đè (không tạo bản ghi lai ngày-này/số-kia)",
          d["last_alert"] == "2026-07-01" and d["sell_pct_osh"] == 0.09, str(d))

    print("# 3. Atomic: hỏng GIỮA CHỪNG không để lại file half-written")
    good = open(p, encoding="utf-8").read()
    real_dump = json.dump
    def boom(obj, fh, **kw):
        fh.write('{"AAA": {"last_a')     # ghi dở rồi chết
        raise IOError("giả lập bị kill giữa chừng")
    json.dump = boom
    try:
        W.write_flags([dict(REC[0], last_alert="2026-07-20")], p)
    except IOError:
        pass
    finally:
        json.dump = real_dump
    check("file đích còn nguyên vẹn sau khi ghi hỏng",
          open(p, encoding="utf-8").read() == good)
    check("JSON đích vẫn parse được", isinstance(json.load(open(p)), dict))
    if os.path.exists(p + ".tmp"):
        os.remove(p + ".tmp")   # rác .tmp là chấp nhận được — đích chưa bao giờ hỏng

    print("# 4. File hỏng sẵn → ghi lại từ đầu, không nổ")
    open(p, "w").write("{ khong-phai-json")
    W.write_flags(REC, p)
    check("phục hồi được từ file hỏng", "AAA" in json.load(open(p)))

print("# 5. Reader — cửa sổ HAI ĐẦU (TTL 90 ngày), đọc file thật data/insider_flags.json")
real = json.load(open(os.path.join(WC, "data", "insider_flags.json"), encoding="utf-8"))
las = sorted(str(v["last_alert"]) for v in real.values())
now = insider_sell_flagged("2026-07-29")
check(f"asof hôm nay bắt được {len(now)}/{len(real)} cờ trong file", len(now) > 0)
check("mọi cờ trả về đều có last_alert <= asof (chống look-ahead)",
      all(str(v["last_alert"]) <= "2026-07-29" for v in now.values()))
before = insider_sell_flagged("2026-04-01")
check("replay ngày quá khứ TRƯỚC mọi cờ → rỗng (không áp cờ tương lai)", before == {},
      f"min last_alert trong file = {las[0]}")
future = insider_sell_flagged("2027-01-01")
check("asof quá xa (mọi cờ hết TTL 90d) → rỗng", future == {})
edge = insider_sell_flagged(las[-1])
check("asof == last_alert mới nhất → cờ đó vẫn active (biên trên inclusive)",
      len(edge) > 0)
check("trả về dict có số liệu bằng chứng (sell_pct_osh, n_sellers)",
      all({"sell_pct_osh", "n_sellers"} <= set(v) for v in now.values()))

print("# 6. FAIL-SAFE: file không tồn tại → {} chứ không nổ")
_orig = __import__("anomaly_gate").WORKDIR
import anomaly_gate
anomaly_gate.WORKDIR = "/khong/ton/tai"
check("thiếu file → trả {}", insider_sell_flagged("2026-07-29", quiet=True) == {})
anomaly_gate.WORKDIR = _orig

print("SELFCHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
