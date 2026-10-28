#!/usr/bin/env python3
"""Selfcheck logic thuần của dri_buy_gate_watch (không DNSE/BQ/Telegram)."""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dri_buy_gate_watch as g  # noqa: E402

D = dt.date
fails = []


def chk(name, cond):
    if not cond:
        fails.append(name)
    print(("ok  " if cond else "FAIL"), name)


def bars(closes, vols):
    return [(D(2026, 10, 1) + dt.timedelta(days=i), c, v) for i, (c, v) in enumerate(zip(closes, vols))]


calm = bars([14000] * 25, [1_000_000] * 25)
chk("G4 calm ≤trần = PASS", g.eval_g4(13_000, calm, 13_000)[0] == "PASS")
chk("G4 >trần = FAIL", g.eval_g4(13_100, calm, 13_000)[0] == "FAIL")
bad = bars([14000] * 24 + [13200], [1_000_000] * 24 + [2_500_000])
chk("G4 -5.7% & 2.5×KL ⇒ WAIT", g.eval_g4(13_000, bad, 13_000)[0] == "WAIT")
dip_lowvol = bars([14000] * 24 + [13200], [1_000_000] * 25)
chk("G4 -5.7% KL thường ⇒ không WAIT", g.eval_g4(13_000, dip_lowvol, 13_000)[0] == "PASS")
chk("G4 thiếu lịch sử ⇒ UNKNOWN (không suy PASS)", g.eval_g4(13_000, [], 13_000)[0] == "UNKNOWN")
chk("G4 không giá ⇒ UNKNOWN", g.eval_g4(None, calm, 13_000)[0] == "UNKNOWN")
t = D(2026, 11, 1)
chk("G3 256.8 ⇒ PARTIAL (còn Bobby thủ công)", g.eval_g3(256.8, D(2026, 10, 30), t)[0] == "PARTIAL")
chk("G3 238 ⇒ FAIL", g.eval_g3(238.0, D(2026, 10, 30), t)[0] == "FAIL")
chk("G3 cũ >5 ngày ⇒ UNKNOWN", g.eval_g3(256.8, D(2026, 10, 20), t)[0] == "UNKNOWN")
chk("G3 None ⇒ UNKNOWN", g.eval_g3(None, None, t)[0] == "UNKNOWN")
chk("G1 trước 30/10 ⇒ WAIT", g.eval_g1(D(2026, 10, 28))[0] == "WAIT")
chk("G1 sau 30/10 ⇒ MANUAL", g.eval_g1(D(2026, 11, 2))[0] == "MANUAL")
allpass = {k: ("PASS", "") for k in ("G0", "G1", "G2", "G3", "G4", "G5")}
chk("verdict mọi PASS ⇒ ĐỦ", g.verdict(allpass) == "ĐỦ")
one = dict(allpass, G5=("MANUAL", ""))
chk("verdict có MANUAL ⇒ CHƯA ĐỦ", g.verdict(one) == "CHƯA ĐỦ CỔNG")
msg = g.build_message(13_000, 13_100, 13_000, {**one, "G1": g.eval_g1(D(2026, 10, 28))}, D(2026, 10, 28))
chk("message nêu KẾT LUẬN + không đặt lệnh", "CHƯA ĐỦ CỔNG" in msg and "KHÔNG đặt lệnh" in msg)
print("FAILS:", fails or "none")
sys.exit(1 if fails else 0)
