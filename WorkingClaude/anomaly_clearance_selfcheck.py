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
low = px(flat, flat, vol1m=10000); low["Volume"] = 10000   # vol_x=1: chi san GTGD 1 ty chan
chk("thanh khoan < 1 ty => KHONG rut", rt(flag(), low) == [])
nan = [20000, 20000, float("nan")]
chk("gia NaN => KHONG rut", rt(flag(), px(nan, nan)) == [])
# H3: da rut nhung luat no lai => khoi phuc
f = flag(retracted={"on": "2026-09-19", "ret_now": -2.5}); rt(f, px(crash, crash))
chk("H3 luat no lai => bo retracted", "retracted" not in f["AAA"])
f = flag(retracted={"on": "2026-09-19", "ret_now": -2.5})
with contextlib.redirect_stdout(io.StringIO()):
    rt(f, px(early, early))
chk("phien TRUOC do no lai => cung khoi phuc", "retracted" not in f["AAA"])
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
import datetime as _dt
s._ict_now = lambda: _dt.datetime(2026, 9, 21, 9, 0)
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
ae.GOLIVE_STATUS, ae.FLAGS, ae.CLEARANCES = tmp + "/golive.json", tmp + "/flags_ae.json", tmp + "/cl_ae.json"
em = json.load(open(emit))
with contextlib.redirect_stdout(io.StringIO()):
    ae.escalate(em); ae.escalate(em)
chk("escalate bao co rut dung 1 lan", len(sent) == 1 and "AAA" in sent[0])

# CAPIT bi co chan => giao tra tin 1 lan, khong tu go
json.dump({"capit_dd_excluded": ["PVT"]}, open(ae.GOLIVE_STATUS, "w"))
json.dump({"PVT": {"last_alert": "2026-10-29", "reasons": "IDIOCRASH", "ret": -6.8}}, open(ae.FLAGS, "w"))
jobs = []; sent.clear(); ae._dispatch_bg = lambda t, p, d: (jobs.append((t, p)), "job")[1]
with contextlib.redirect_stdout(io.StringIO()):
    ae.escalate({"asof": "2026-11-27"}); ae.escalate({"asof": "2026-11-27"})
chk("CAPIT bi chan => giao tra tin dung 1 lan, cam tu ghi",
    len(jobs) == 1 and jobs[0][0] == "Wendy" and "KHÔNG ghi" in jobs[0][1] and len(sent) == 1)
json.dump({"clearances": [{"ticker": "PVT", "flag_date": "2026-10-29"}]}, open(ae.CLEARANCES, "w"))
ae.LEDGER = tmp + "/led2.json"; jobs.clear()
with contextlib.redirect_stdout(io.StringIO()):
    ae.escalate({"asof": "2026-11-27"})
chk("co da duyet go => khong tra tin lai", jobs == [])

# anomaly_clear.py
import anomaly_clear as ac
os.makedirs(tmp + "/wc/data"); json.dump({"PVT": {"last_alert": "2026-10-29"}}, open(tmp + "/wc/data/anomaly_flags.json", "w"))
base = ["PVT", "2026-10-29", "SECTOR_OR_MARKET", "--evidence", "u", "--approval-ref", "r", "--decided-by", "user"]
def run(argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            ac.main(argv, wc=tmp + "/wc"); return True
        except SystemExit:
            return False
chk("anomaly_clear ghi dong hop le", run(base) and run(base)
    and len(json.load(open(tmp + "/wc/data/anomaly_clearances.json"))["clearances"]) == 1)
g.WORKDIR = tmp + "/wc"
chk("dong do anomaly_clear ghi duoc gate chap nhan", ("PVT", "2026-10-29") in g.anomaly_clearances("2099-01-01"))
chk("sai ngay co / agent / BAD_COMPANY bi tu choi",
    not run(["PVT", "2026-10-01"] + base[2:]) and not run(base[:-1] + ["agent"])
    and not run(["PVT", "2026-10-29", "BAD_COMPANY"] + base[3:]))

# loai tay CAPIT
UX = tmp + "/wc/data/capit_user_exclusions.json"
chk("khong co file loai tay", g.capit_user_excluded("2026-11-27") == ({}, None))
row = {"ticker": "VGC", "from": "2026-11-27", "until": "2027-03-15", "decided_by": "user", "approval_ref": "r"}
def putx(*r): json.dump({"exclusions": list(r)}, open(UX, "w"))
putx(row)
chk("loai tay trong han", "VGC" in g.capit_user_excluded("2026-11-27")[0] and "VGC" in g.capit_user_excluded("2027-03-15")[0])
chk("ngoai han => khong loai", g.capit_user_excluded("2026-11-26")[0] == {} and g.capit_user_excluded("2027-03-16")[0] == {})
putx({**row, "decided_by": "agent"}); chk("agent => khong loai + bao loi", g.capit_user_excluded("2026-11-27")[0] == {} and g.capit_user_excluded("2026-11-27")[1])
putx({k: v for k, v in row.items() if k != "until"}, row)
out, err = g.capit_user_excluded("2026-11-27"); chk("dong thieu until bi bo rieng", list(out) == ["VGC"] and err)
open(UX, "w").write("{hong"); chk("file hong => tra loi", g.capit_user_excluded("2026-11-27")[1])

print(f"{'PASS' if not fails else 'FAIL'} ({len(fails)} loi)")
sys.exit(1 if fails else 0)
