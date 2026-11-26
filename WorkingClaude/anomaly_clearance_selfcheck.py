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
      "decided_by": "user", "decided_on": "2026-11-27", "approval_ref": "link"}
def ex(asof="2026-11-27"):
    with contextlib.redirect_stdout(io.StringIO()):
        return g.anomaly_excluded(asof)
def put(*rows): json.dump({"clearances": list(rows)}, open(CL, "w"))

chk("khong co file => nhu cu", ex() == {"PVT", "PNJ"})
put(OK); chk("go dung PVT", ex() == {"PNJ"})
chk("decided_on > asof => chua go (look-ahead)", ex("2026-11-26") == {"PVT", "PNJ"})
for name, row in [("agent tu duyet", {**OK, "decided_by": "agent"}), ("BAD_COMPANY", {**OK, "verdict": "BAD_COMPANY"}),
                  ("khac ngay co", {**OK, "flag_date": "2026-10-01"}), ("evidence rong", {**OK, "evidence": " "}),
                  ("evidence null", {**OK, "evidence": None}), ("approval_ref rong", {**OK, "approval_ref": ""}),
                  ("NONE_FOUND qua som", {**OK, "verdict": "NONE_FOUND", "decided_on": "2026-11-04"}),
                  ("thieu truong", {k: v for k, v in OK.items() if k != "decided_by"})]:
    put(row); chk(name + " => khong go", ex() == {"PVT", "PNJ"})
put({**OK, "verdict": "NONE_FOUND"}); chk("NONE_FOUND du 7 ngay => go", ex() == {"PNJ"})
put({"ticker": "X"}, OK); chk("dong hong chi mat dong do", ex() == {"PNJ"})
open(CL, "w").write("{hong"); chk("file hong => khong go", ex() == {"PVT", "PNJ"})
os.remove(CL)
json.dump({**FL, "PVT": {"last_alert": "2026-10-29", "retracted": {"ret_now": -1, "on": "2026-11-27"}}},
          open(tmp + "/data/anomaly_flags.json", "w"))
chk("co da rut => khong chan", ex() == {"PNJ"})
chk("rut SAU asof => replay van chan", ex("2026-11-26") == {"PVT", "PNJ"})
with contextlib.redirect_stdout(io.StringIO()):
    sk = g.anomaly_skipped("2026-11-27")
chk("anomaly_skipped noi ra co khong ap dung", sk == {"PVT": ("2026-10-29", "cờ giá giả đã rút")})

# ── rút cờ giả ──
DAYS = pd.bdate_range("2026-07-20", "2026-09-18")
def px(close_tail, price_tail, vol1m=1e6, ticker="AAA"):
    """Chuỗi phẳng 20.000, ba phiên cuối (16-18/09) theo *_tail."""
    n = len(DAYS) - 3
    return pd.DataFrame({"time": DAYS, "ticker": ticker, "Close": [20000] * n + close_tail,
                         "Price": [20000] * n + price_tail, "Volume": 1e6, "Volume_1M": vol1m,
                         "VNINDEX": 1800.0})
def flag(**kw): return {"AAA": {"last_alert": "2026-09-18", "tier": "H", "reasons": "IDIOCRASH", "ret": -22.77, **kw}}
flat = [20000, 20000, 19500]
def rt(f, d, hold=()): return s.retract_fake_flags(f, d, set(hold))

f = flag(); chk("gia nhat quan, khac xa ret ghi => rut", rt(f, px(flat, flat)) == ["AAA"] and "retracted" in f["AAA"])
chk("Close phang, Price -10% => KHONG rut", rt(flag(), px(flat, [20000, 20000, 18000])) == [])
chk("Close phang, Price van -22% => KHONG rut", rt(flag(), px(flat, [20000, 20000, 15446])) == [])
chk("Price phang, Close van sap => KHONG rut", rt(flag(), px([20000, 20000, 15446], flat)) == [])
crash = [20000, 20000, 18600]
chk("luat van no o phien co => KHONG rut", rt(flag(), px(crash, crash)) == [])
early = [18400, 18400, 17950]          # H1: sap that 16/09 (-8%), co 18/09 la gia
f = flag(); chk("H1 sap that truoc do con trong TTL => KHONG rut", rt(f, px(early, early)) == [] and "retracted" not in f["AAA"])
chk("ret khong doi => KHONG rut", rt(flag(ret=-2.6), px(flat, flat)) == [])
chk("thieu cot Price => KHONG rut", rt(flag(), px(flat, flat).drop(columns="Price")) == [])
chk("phien co khong co du lieu => KHONG rut", rt(flag(), px(flat, flat).iloc[:-1]) == [])
chk("cua so du lieu khong phu 30 ngay => KHONG rut", rt(flag(), px(flat, flat).iloc[-5:]) == [])
chk("thanh khoan < 1 ty => KHONG rut", rt(flag(), px(flat, flat, vol1m=10000)) == [])
nan = [20000, 20000, float("nan")]
chk("gia NaN => KHONG rut", rt(flag(), px(nan, nan)) == [])
# H3: da rut nhung luat no lai => khoi phuc
f = flag(retracted={"on": "2026-09-19", "ret_now": -2.5}); rt(f, px(crash, crash))
chk("H3 luat no lai => bo retracted", "retracted" not in f["AAA"])
# tier H da ban: nguong VOLSPIKE tier H (>=5x) chi con nhan qua flag['tier']
vs = px(flat, flat); vs.loc[vs.index[-1], "Volume"] = 6e6
chk("tier-H da ban van dung nguong H => KHONG rut", rt(flag(), vs, hold=()) == [])

# write_flags / main wiring
s.FLAGS_PATH = tmp + "/data/w.json"
def load(): return json.load(open(s.FLAGS_PATH))
def alert(day): return pd.DataFrame([{"time": pd.Timestamp(day), "ticker": "AAA", "tier": "H", "reasons": "IDIOCRASH",
                                      "ret": -8.0, "idio": -8.0, "vol_x": 2.0}])
json.dump(flag(retracted={"on": "2026-09-19", "ret_now": -2.5}), open(s.FLAGS_PATH, "w"))
s.write_flags(alert("2026-10-01")); chk("co moi => bo retracted", "retracted" not in load()["AAA"])
json.dump(flag(), open(s.FLAGS_PATH, "w"))
with contextlib.redirect_stdout(io.StringIO()):
    ret = s.write_flags(alert("2026-09-16"), prices=px(early, early))
chk("H2 backfill phien cu khong ghi de, khong rut", load()["AAA"]["ret"] == -22.77 and ret == [])
json.dump(flag(), open(s.FLAGS_PATH, "w"))
s.load_universe = lambda now_ict=None: ({"AAA"}, set(), {"is_stale": False, "asof": "x", "reason": ""})
s.load_prices = lambda *a: px(flat, flat)
emit = tmp + "/emit.json"; sys.argv = ["x", "--asof", "2026-09-18", "--emit-json", emit]
with contextlib.redirect_stdout(io.StringIO()):
    s.main()
chk("main(): rut co + dua vao emit-json", [r["ticker"] for r in json.load(open(emit))["retracted"]] == ["AAA"])

# escalate: co rut phai toi nguoi, 1 lan
sys.path.insert(0, os.environ.get("ANOMALY_BIN_DIR", os.path.join(HERE, "mike", "bin")))
import anomaly_escalate as ae
assert os.path.dirname(os.path.abspath(ae.__file__)) == os.path.abspath(sys.path[0])
sent = []
ae._notify = lambda m, dry: (sent.append(m), True)[1]; ae._dispatch_bg = lambda *a: "job"
ae.LEDGER = tmp + "/led.json"
em = json.load(open(emit))
with contextlib.redirect_stdout(io.StringIO()):
    ae.escalate(em); ae.escalate(em)
chk("escalate bao co rut dung 1 lan", len(sent) == 1 and "AAA" in sent[0])

print(f"{'PASS' if not fails else 'FAIL'} ({len(fails)} loi)")
sys.exit(1 if fails else 0)
