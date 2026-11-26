# -*- coding: utf-8 -*-
"""Selfcheck: gỡ cờ có người duyệt (anomaly_gate) + rút cờ giá giả (anomaly_scan). Offline."""
import datetime, io, json, os, sys, tempfile, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCAN_DIR = os.environ.get("ANOMALY_SCAN_DIR", os.path.join(HERE, "mike", "agents", "Taylor"))
sys.path.insert(0, SCAN_DIR)
import pandas as pd
import anomaly_gate as g
import anomaly_scan as s

assert os.path.dirname(os.path.abspath(g.__file__)) == HERE
assert os.path.dirname(os.path.abspath(s.__file__)) == os.path.abspath(SCAN_DIR)
fails = []
def chk(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

tmp = tempfile.mkdtemp(); os.makedirs(tmp + "/data"); g.WORKDIR = tmp
FL = {"PVT": {"last_alert": "2026-10-29"}, "PNJ": {"last_alert": "2026-10-29"},
      "OLD": {"last_alert": "2026-08-01"}, "_meta": {"generated_at": "x"}}
json.dump(FL, open(tmp + "/data/anomaly_flags.json", "w"))
CL = tmp + "/data/anomaly_clearances.json"
OK = {"ticker": "PVT", "flag_date": "2026-10-29", "verdict": "SECTOR_OR_MARKET", "evidence": "url",
      "decided_by": "user", "decided_on": "2026-11-27"}
def ex(asof="2026-11-27"):
    with contextlib.redirect_stdout(io.StringIO()):
        return g.anomaly_excluded(asof)
def put(*rows): json.dump({"clearances": list(rows)}, open(CL, "w"))

chk("khong co file => nhu cu", ex() == {"PVT", "PNJ"})
put(OK); chk("go dung PVT", ex() == {"PNJ"})
chk("decided_on > asof => chua go (look-ahead)", ex("2026-11-26") == {"PVT", "PNJ"})
for name, row in [("agent tu duyet", {**OK, "decided_by": "agent"}), ("BAD_COMPANY", {**OK, "verdict": "BAD_COMPANY"}),
                  ("khac ngay co", {**OK, "flag_date": "2026-10-01"}), ("evidence rong", {**OK, "evidence": " "}),
                  ("evidence null", {**OK, "evidence": None}),
                  ("thieu truong", {k: v for k, v in OK.items() if k != "decided_by"})]:
    put(row); chk(name + " => khong go", ex() == {"PVT", "PNJ"})
open(CL, "w").write("{hong"); chk("file hong => khong go", ex() == {"PVT", "PNJ"})
os.remove(CL)
json.dump({**FL, "PVT": {"last_alert": "2026-10-29", "retracted": {"ret_now": -1}}}, open(tmp + "/data/anomaly_flags.json", "w"))
chk("co da rut => khong chan", ex() == {"PNJ"})

# ── rút cờ giả ──
def px(close, price):
    days = pd.to_datetime(["2026-09-16", "2026-09-17", "2026-09-18"])
    return pd.DataFrame({"time": days, "ticker": "AAA", "Close": close, "Price": price,
                         "Volume": 1e6, "Volume_1M": 1e6, "VNINDEX": [1800, 1800, 1800]})
def flag(): return {"AAA": {"last_alert": "2026-09-18", "tier": "H", "reasons": "IDIOCRASH", "ret": -22.77}}
flat = [20000, 20000, 19500]
f = flag(); chk("gia da nhat quan, khac xa ret ghi => rut", s.retract_fake_flags(f, px(flat, flat), set()) == ["AAA"] and "retracted" in f["AAA"])
chk("Close hong nhung Price con sap => KHONG rut", s.retract_fake_flags(flag(), px(flat, [20000, 20000, 15446]), set()) == [])
chk("Price phang nhung Close van sap => KHONG rut", s.retract_fake_flags(flag(), px([20000, 20000, 15446], flat), set()) == [])
crash = [20000, 20000, 18600]   # -7%: luat IDIOCRASH van no
f = flag(); f["AAA"]["ret"] = -22.77
chk("luat van no => KHONG rut", s.retract_fake_flags(f, px(crash, crash), set()) == [])
f = flag(); f["AAA"]["ret"] = -2.6; chk("ret khong doi => KHONG rut", s.retract_fake_flags(f, px(flat, flat), set()) == [])
chk("thieu cot Price => KHONG rut", s.retract_fake_flags(flag(), px(flat, flat).drop(columns="Price"), set()) == [])
chk("phien co khong co trong du lieu => KHONG rut", s.retract_fake_flags(flag(), px(flat, flat).iloc[:2], set()) == [])

# write_flags: cờ nổ lại phải xoá `retracted`
s.FLAGS_PATH = tmp + "/data/w.json"
json.dump({"AAA": {**flag()["AAA"], "retracted": {"ret_now": -2.5}}}, open(s.FLAGS_PATH, "w"))
al = pd.DataFrame([{"time": pd.Timestamp("2026-10-01"), "ticker": "AAA", "tier": "H", "reasons": "IDIOCRASH",
                    "ret": -7.0, "idio": -6.0, "vol_x": 2.0}])
s.write_flags(al)
chk("co moi => bo retracted", "retracted" not in json.load(open(s.FLAGS_PATH))["AAA"])
print(f"{'PASS' if not fails else 'FAIL'} ({len(fails)} loi)")
sys.exit(1 if fails else 0)
