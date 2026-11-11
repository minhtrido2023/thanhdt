# -*- coding: utf-8 -*-
"""Selfcheck: anomaly_flags_freshness so với PHIÊN giao dịch gần nhất, không so ngày lịch.
Chạy: python3 anomaly_gate_freshness_session_selfcheck.py  (nên chạy 3 TZ: env -u TZ / TZ=America/New_York / TZ=UTC)."""
import datetime as dt, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anomaly_gate as ag

tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "data"))
ag.WORKDIR = tmp   # KHÔNG đọc file production
bad = []

def put(gen_utc):
    with open(os.path.join(tmp, "data", "anomaly_flags.json"), "w") as f:
        json.dump({"_meta": {"generated_at": gen_utc}}, f)

def chk(name, ref, gen_utc, want_stale):
    put(gen_utc)
    r = ag.anomaly_flags_freshness(ref)
    ok = r["is_stale"] == want_stale
    print(("PASS" if ok else "FAIL"), name, r["is_stale"], r["reason"])
    if not ok: bad.append(name)

FRI_1245 = "2026-11-06T05:45:00Z"   # T6 12:45 ICT
# T7 / CN: file T6 là đúng → KHÔNG stale
chk("T7 file T6", "2026-11-07", FRI_1245, False)
chk("CN file T6", "2026-11-08", FRI_1245, False)
# T2 (phiên) file T6 → stale thật
chk("T2 file T6 (stale thật)", "2026-11-09", FRI_1245, True)
# thường: T4 file T3 → stale; file cùng ngày → tươi
chk("T4 file T3 stale", "2026-11-11", "2026-11-10T05:45:00Z", True)
chk("T4 file T4 fresh", "2026-11-11", "2026-11-11T05:45:00Z", False)
# lễ liền kề (08-31, 09-01, 09-02 nghỉ; phiên cuối trước đó = T6 08-28)
chk("lễ 09-02 file 08-28 (fresh)", "2026-09-02", "2026-08-28T05:45:00Z", False)
chk("lễ 09-02 file 08-27 (stale thật)", "2026-09-02", "2026-08-27T05:45:00Z", True)
# file ghi SAU phiên gần nhất (quét tay T7) vẫn tươi
chk("T7 file T7", "2026-11-07", "2026-11-07T03:00:00Z", False)
# mặc định ref=None không crash
put(FRI_1245); ag.anomaly_flags_freshness()
print("anchor T7->", ag.last_session_on_or_before("2026-11-07"), "CN->", ag.last_session_on_or_before("2026-11-08"),
      "09-02->", ag.last_session_on_or_before("2026-09-02"))
sys.exit(1 if bad else 0)
