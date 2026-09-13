# -*- coding: utf-8 -*-
"""Selfcheck aria-K — executor chờ kết quả ATC sau khi vào CLOSED, trước khi bot tắt.

Sự cố gốc (Winston aria-I, bus 2026-09-13T07:59Z): ZaloPay 2026-07-10 child ATC oid 502431
(VHC SELL 600, `_atc_sweep` 14:30:19) khớp 14:45 @57.500, nhưng poll cuối 14:45:05 còn `New`;
run_session vào CLOSED → cancel_all_open (HTTP 400 closed session) → break, không poll lại ⇒
state parent filled=1200 vĩnh viễn, journal/dnse_raw thiếu 600cp.

Dựng lại bằng CODE THẬT (`run_session` + `Executor`), chỉ thay broker (FakeBroker theo đồng hồ
giả) và đồng hồ (`executor.now_ict`, `executor.time.sleep`) — chạy vài giây, không mạng, không bus
(MIKE_BOT_TEST_MODE=1, event bị chặn ghi ra sink tạm để assert, §5b).

  A. Tái hiện 07-10: New lúc 14:45:05 → Filled 600 @57.500 lúc 14:46 ⇒ state filled 1800/done,
     journal FILL oid 502431 qty 600, WAIT/DONE, await_atc, report ghi SAU khi chờ (1,800), thoát
     ≤14:46:20, 0 bus event.
  B. Timeout: lệnh mãi `New` ⇒ ATC_POSTCLOSE_TIMEOUT, state KHÔNG đổi, thoát đúng 14:55, đúng 1
     bus event `status`; chạy lại (resume) ⇒ vẫn 1 bus event (cờ state, §5).
  C. Không child mở ⇒ không chờ: 0 sleep, chỉ 1 poll (của step), wall <1s; và cancel THÀNH CÔNG
     (kiểu PaperBroker) ⇒ cũng không chờ.
  D. Idempotent (§5): kill giữa vòng poll rồi chạy lại — (D1) kill ở poll ⇒ FILL [300, 600] không
     lặp; (D2) kill giữa _sync_fills và _save_state ⇒ dòng FILL lặp CÙNG số luỹ kế (quy ước hiện có:
     max(qty) theo child_oid) — max vẫn 600, state filled đúng 1800.
  E. BOT_STOP giữa lúc chờ ⇒ ATC_POSTCLOSE_ABORT, không TIMEOUT, không bus.
  F. LO còn treo (không phải ATC) về `Canceled` 0 khớp (trạng thái DNSE thật; `Expired` chưa từng thấy) ⇒ child
     closed + nhả reservation, DONE.
  G. 2 account: account không có child mở KHÔNG bị poll thêm; account kia chờ tới khi khớp.
  H. Đồng hồ THẬT (không patch) + không child mở ⇒ return <1s; deadline so trên now_ict() ICT.
  I. poll_orders() lỗi TRONG lúc chờ ⇒ POLL_FAIL "postclose:", vòng chờ tiếp tục tới DONE; mọi poll lỗi
     ⇒ TIMEOUT ghi đúng lỗi thật (không bịa "không thấy trong sổ lệnh", §29), report vẫn ghi.
  J. Lỗi bất ngờ trong vòng chờ ⇒ ATC_POSTCLOSE_ERROR (journal + bus error), report VẪN ghi.
  K. Ngoài cửa sổ ⇒ ATC_POSTCLOSE_SKIP, 0 chờ: thứ Bảy 10:00 (session_phase CLOSED cả ngày), ngày lễ
     02/09, plan_date ≠ hôm nay.
  P. Có fill mới trong lúc chờ ⇒ đọc positions + cash 1 lần (dnse_raw mới hơn fill); không chờ ⇒ 0.
Chạy: env -u TZ MIKE_BOT_TEST_MODE=1 $DNA_PYEXE atc_postclose_selfcheck.py
      TZ=America/New_York MIKE_BOT_TEST_MODE=1 $DNA_PYEXE atc_postclose_selfcheck.py   (§16)
"""
import csv
import datetime as dt
import glob
import json
import os
import sys
import tempfile
import time as _real_time

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b — TRƯỚC khi dựng Executor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trading_bot.executor as X  # noqa: E402
from trading_bot.brokers import OrderUpdate  # noqa: E402
from trading_bot.vn_market import is_holiday  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402

TAG = "selfcheck-atcpost"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*")):
    os.remove(f)

fails = []
npass = 0


def check(name, cond, detail=""):
    global npass
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if cond:
        npass += 1
    else:
        fails.append(name)


class Killed(BaseException):
    """Mô phỏng process bị giết (không bị `except Exception` trong executor nuốt)."""


class Clock:
    def __init__(self, hhmmss, day=dt.date(2026, 7, 10)):
        self.t = dt.datetime.combine(day, dt.time.fromisoformat(hhmmss))
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += dt.timedelta(seconds=s)


class _TimeShim:
    def __init__(self, clock):
        self.sleep = clock.sleep


CLOCK = None
X.now_ict = lambda: CLOCK.now()


def install(clock, stop_file):
    global CLOCK
    CLOCK = clock
    X.time = _TimeShim(clock)
    X.STOP_FILE = stop_file


class FakeBroker:
    """script: oid -> list[(hh:mm:ss từ lúc nào, status, filled, avg)] — mục cuối có mốc ≤ now thắng."""
    name = "fake"

    def __init__(self, script, symbol="VHC", kill_on_poll=None):
        self.script, self.symbol, self.kill_on_poll = script, symbol, kill_on_poll
        self.polls = 0
        self.cancels = []
        self.positions_calls = self.cash_calls = 0
        self.fail_polls = set()     # số thứ tự poll sẽ ném RuntimeError (lỗi mạng giả)

    def poll_orders(self):
        self.polls += 1
        if self.kill_on_poll and self.polls == self.kill_on_poll:
            raise Killed()
        if self.polls in self.fail_polls:
            raise RuntimeError(f"HTTP 503 giả lập poll #{self.polls}")
        now = CLOCK.now().time()
        out = {}
        for oid, steps in self.script.items():
            cur = None
            for since, st, filled, avg in steps:
                if dt.time.fromisoformat(since) <= now:
                    cur = (st, filled, avg)
            if cur:
                out[oid] = OrderUpdate(oid, cur[0], cur[1], cur[2],
                                       raw={"symbol": self.symbol, "loanPackageId": 1258})
        return out

    def cancel_order(self, oid):
        self.cancels.append(oid)
        n = CLOCK.now()
        if n.time() >= dt.time(14, 45) or n.weekday() >= 5 or is_holiday(n.date()):
            raise RuntimeError("HTTP 400: Can not cancel the order in the closed session")
        return {}

    def place_order(self, *a, **k):
        raise AssertionError("place_order KHÔNG được gọi sau giờ đóng cửa")

    def get_positions(self):
        self.positions_calls += 1
        return {}

    def get_quote(self, *a, **k):
        return None

    def get_cash(self):
        self.cash_calls += 1
        return 10**12


class OkCancelBroker(FakeBroker):
    def cancel_order(self, oid):
        self.cancels.append(oid)
        return {}


def make_exec(tmp, broker, label=TAG, closed_filled=1200, atc_child=True, order=None,
              plan_date="2026-07-10"):
    o = order or PlannedOrder(id="SELL-VHC-01", ticker="VHC", side="sell", qty=1800,
                              ref_price=57600)
    plan = TradePlan(plan_date=plan_date, signal_date=plan_date, strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=[o],
                     account=label, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    ex = X.Executor(plan, broker, cfg, shared={})
    os.makedirs(os.path.join(tmp, label), exist_ok=True)
    ex.state_file = os.path.join(tmp, label, "state.json")
    ex.journal_file = os.path.join(tmp, label, "journal.csv")
    ex.report_file = os.path.join(tmp, label, "report.md")
    if os.path.exists(ex.state_file):            # resume sau "kill"
        ex.state = ex._load_state()
        return ex
    ps = ex.state["parents"][o.id]
    if closed_filled:
        ps["children"].append({"oid": "483161", "qty": closed_filled, "price": 57700,
                               "filled": closed_filled, "status": "closed", "released": True,
                               "ts": "2099-01-01T14:21:31"})
    if atc_child:
        ps["children"].append({"oid": "502431", "qty": o.qty - closed_filled, "price": None,
                               "filled": 0, "status": "open", "ts": "2099-01-01T14:30:19"})
        ps["atc_sent"] = True
    ps["filled"] = closed_filled
    ex._save_state()
    return ex


def journal(ex, event=None):
    if not os.path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if event is None or r["event"] == event]


def sink_events(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


CLOSED_OK = [("00:00:00", "Filled", 1200, 57700)]


def run(tmp, clock_start, execs, stop_file=None, day=dt.date(2026, 7, 10)):
    install(Clock(clock_start, day), stop_file or os.path.join(tmp, "NO_BOT_STOP"))
    X.run_session(execs)
    return CLOCK


with tempfile.TemporaryDirectory() as tmp:
    sink = os.path.join(tmp, "bus_sink.jsonl")
    os.environ["MIKE_BOT_TEST_EVENT_SINK"] = sink

    # ------------------------------------------------------------------ A
    print("A. tái hiện ZaloPay 2026-07-10 VHC oid 502431")
    tA = os.path.join(tmp, "A")
    bA = FakeBroker({"483161": CLOSED_OK,
                     "502431": [("14:30:19", "New", 0, None), ("14:46:00", "Filled", 600, 57500)]})
    exA = make_exec(tA, bA)
    c = run(tA, "14:45:05", [exA])
    psA = exA.state["parents"]["SELL-VHC-01"]
    ch = psA["children"][1]
    check("A1 state parent filled 1800 + done", psA["filled"] == 1800 and psA["done"],
          f"filled={psA['filled']} done={psA['done']}")
    fills = [(r["child_oid"], r["qty"], r["price"]) for r in journal(exA, "FILL")]
    check("A2 journal FILL oid 502431 qty 600 @57500", ("502431", "600", "57500") in fills, str(fills))
    check("A3 child await_atc=True (CANCEL_FAIL closed session) và đã closed",
          ch.get("await_atc") is True and ch["status"] == "closed", str(ch))
    evA = [r["event"] for r in journal(exA)]
    check("A4 journal CANCEL_FAIL → ATC_POSTCLOSE_WAIT → FILL → ATC_POSTCLOSE_DONE",
          evA.index("CANCEL_FAIL") < evA.index("ATC_POSTCLOSE_WAIT") < evA.index("FILL")
          < evA.index("ATC_POSTCLOSE_DONE") if all(e in evA for e in
          ("CANCEL_FAIL", "ATC_POSTCLOSE_WAIT", "FILL", "ATC_POSTCLOSE_DONE")) else False, str(evA))
    check("A5 không TIMEOUT", "ATC_POSTCLOSE_TIMEOUT" not in evA)
    with open(exA.report_file, encoding="utf-8") as f:
        rep = f.read()
    check("A6 report ghi SAU khi chờ (dòng 1,800 | 1,800 | 100%)",
          "| 1,800 | 1,800 | 100% |" in rep, rep.splitlines()[-4] if rep else "")
    check("A7 thoát trong 1 chu kỳ poll sau khi khớp (≤14:46:20)", c.now().time() <= dt.time(14, 46, 20),
          str(c.now().time()))
    check("A8 state trên đĩa = trong bộ nhớ (đã _save_state)",
          json.load(open(exA.state_file))["parents"]["SELL-VHC-01"]["filled"] == 1800)
    check("A9 0 bus event", sink_events(sink) == [], str(sink_events(sink)))
    check("P1 có fill trong lúc chờ ⇒ positions+cash đọc thêm đúng 1 lần sau chờ",
          bA.positions_calls == 2 and bA.cash_calls == 1,
          f"positions={bA.positions_calls} (1 của step) cash={bA.cash_calls}")

    # ------------------------------------------------------------------ B
    print("B. timeout 14:55 — lệnh mãi New")
    tB = os.path.join(tmp, "B")
    scriptB = {"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]}
    exB = make_exec(tB, FakeBroker(scriptB))
    before = json.dumps(exB.state["parents"], sort_keys=True)
    c = run(tB, "14:45:05", [exB])
    psB = exB.state["parents"]["SELL-VHC-01"]
    tj = journal(exB, "ATC_POSTCLOSE_TIMEOUT")
    check("B1 journal ATC_POSTCLOSE_TIMEOUT oid 502431", [r["child_oid"] for r in tj] == ["502431"],
          str([(r["child_oid"], r["note"]) for r in tj]))
    after = dict(json.loads(json.dumps(exB.state["parents"], sort_keys=True)))
    after["SELL-VHC-01"]["children"][1].pop("await_atc", None)
    check("B2 state parent KHÔNG đổi (ngoài cờ await_atc)",
          json.dumps(after, sort_keys=True) == before and psB["filled"] == 1200 and not psB["done"])
    check("B3 thoát đúng 14:55:00 (không vượt hạn)", c.now().time() == dt.time(14, 55), str(c.now().time()))
    check("B4 mọi sleep ≤ 15s", max(c.sleeps, default=99) <= 15 and len(c.sleeps) >= 30, f"n={len(c.sleeps)} max={max(c.sleeps, default=None)}")
    ev = [e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_TIMEOUT"]
    check("B5 đúng 1 bus event status ATC_POSTCLOSE_TIMEOUT kèm child",
          len(ev) == 1 and ev[0]["event_type"] == "status"
          and ev[0]["payload"]["children"][0]["oid"] == "502431"
          and "lệnh vẫn New" in ev[0]["payload"]["children"][0]["last_seen"], str(ev)[:300])
    check("B6 cờ state _atc_postclose_timeout đã lưu đĩa",
          bool(json.load(open(exB.state_file)).get("_atc_postclose_timeout")))
    check("B8 note TIMEOUT trích trạng thái poll thật", bool(tj) and "lệnh vẫn New" in tj[0]["note"],
          tj[0]["note"] if tj else "no TIMEOUT")
    exB2 = make_exec(tB, FakeBroker(scriptB))          # resume khi đang chờ (kill rồi chạy lại 14:54:50)
    c = run(tB, "14:54:50", [exB2])
    ev = [e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_TIMEOUT"]
    check("B7 chạy lại trong cửa sổ, hết hạn lần nữa ⇒ vẫn đúng 1 bus event (cờ state)",
          len(ev) == 1 and len(journal(exB2, "ATC_POSTCLOSE_TIMEOUT")) == 2, f"n={len(ev)}")

    # ------------------------------------------------------------------ C
    print("C. ngày thường — không child mở ⇒ không chờ")
    tC = os.path.join(tmp, "C")
    bC = FakeBroker({"483161": CLOSED_OK})
    exC = make_exec(tC, bC, atc_child=False)
    w0 = _real_time.monotonic()
    c = run(tC, "14:45:05", [exC])
    wall = _real_time.monotonic() - w0
    check("C1 0 sleep, 1 poll (của step), không WAIT", c.sleeps == [] and bC.polls == 1
          and not journal(exC, "ATC_POSTCLOSE_WAIT"), f"sleeps={c.sleeps} polls={bC.polls}")
    check("C2 wall time run_session < 1s", wall < 1.0, f"{wall:.3f}s")
    tC2 = os.path.join(tmp, "C2")
    bC2 = OkCancelBroker({"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]})
    exC2 = make_exec(tC2, bC2)
    c = run(tC2, "14:45:05", [exC2])
    check("C3 huỷ THÀNH CÔNG (PaperBroker) ⇒ không chờ, không await_atc",
          c.sleeps == [] and bC2.cancels == ["502431"]
          and "await_atc" not in exC2.state["parents"]["SELL-VHC-01"]["children"][1])

    # ------------------------------------------------------------------ D
    print("D. idempotent — kill giữa vòng poll rồi chạy lại")
    scriptD = {"483161": CLOSED_OK,
               "502431": [("14:30:19", "New", 0, None), ("14:45:30", "PartiallyFilled", 300, 57500),
                          ("14:46:00", "Filled", 600, 57500)]}
    tD1 = os.path.join(tmp, "D1")
    exD1 = make_exec(tD1, FakeBroker(scriptD, kill_on_poll=4))   # poll 1=step, 2=14:45:20, 3=14:45:35(300), 4=kill
    try:
        run(tD1, "14:45:05", [exD1])
        killed = False
    except Killed:
        killed = True
    disk = json.load(open(exD1.state_file))["parents"]["SELL-VHC-01"]
    check("D1a bị kill giữa vòng chờ, đĩa đã có partial 300", killed and disk["filled"] == 1500,
          f"killed={killed} filled={disk['filled']}")
    exD1b = make_exec(tD1, FakeBroker(scriptD))
    CLOCK_RESUME = "14:45:50"
    run(tD1, CLOCK_RESUME, [exD1b])
    f1 = [r["qty"] for r in journal(exD1b, "FILL") if r["child_oid"] == "502431"]
    check("D1b FILL oid 502431 = [300, 600], không lặp", f1 == ["300", "600"], str(f1))
    check("D1c state filled 1800 done", exD1b.state["parents"]["SELL-VHC-01"]["filled"] == 1800
          and exD1b.state["parents"]["SELL-VHC-01"]["done"])

    tD2 = os.path.join(tmp, "D2")
    exD2 = make_exec(tD2, FakeBroker(scriptD))
    orig_save = exD2._save_state
    fired = []

    def _save_then_kill():
        c502 = exD2.state["parents"]["SELL-VHC-01"]["children"][1]
        if c502.get("filled") == 300 and not fired:
            fired.append(1)
            raise Killed()
        orig_save()
    exD2._save_state = _save_then_kill
    try:
        run(tD2, "14:45:05", [exD2])
    except Killed:
        pass
    exD2b = make_exec(tD2, FakeBroker(scriptD))
    run(tD2, "14:45:50", [exD2b])
    f2 = [int(r["qty"]) for r in journal(exD2b, "FILL") if r["child_oid"] == "502431"]
    check("D2a kill giữa _sync_fills/_save_state ⇒ dòng lặp CÙNG số luỹ kế, max=600",
          fired and max(f2) == 600 and sorted(set(f2)) == [300, 600], str(f2))
    check("D2b state filled 1800 (không nhân đôi)",
          exD2b.state["parents"]["SELL-VHC-01"]["filled"] == 1800)

    # ------------------------------------------------------------------ E
    print("E. BOT_STOP giữa lúc chờ")
    tE = os.path.join(tmp, "E")
    stop = os.path.join(tmp, "E_BOT_STOP")

    class StopBroker(FakeBroker):
        def poll_orders(self):
            if CLOCK.now().time() >= dt.time(14, 46):
                open(stop, "w").close()
            return super().poll_orders()
    n_sink = len(sink_events(sink))
    exE = make_exec(tE, StopBroker({"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]}))
    c = run(tE, "14:45:05", [exE], stop_file=stop)
    evE = [r["event"] for r in journal(exE)]
    check("E1 ATC_POSTCLOSE_ABORT, không TIMEOUT, thoát trước 14:47",
          "ATC_POSTCLOSE_ABORT" in evE and "ATC_POSTCLOSE_TIMEOUT" not in evE
          and c.now().time() < dt.time(14, 47), f"{evE[-3:]} {c.now().time()}")
    check("E2 không bus event", len(sink_events(sink)) == n_sink)

    # ------------------------------------------------------------------ F
    print("F. LO còn treo → Canceled 0 khớp (trạng thái DNSE thật; 'Expired' chưa từng thấy trong dnse_raw)")
    tF = os.path.join(tmp, "F")
    oF = PlannedOrder(id="BUY-POW-01", ticker="POW", side="buy", qty=1000, ref_price=12000)
    bF = FakeBroker({"206151": [("14:20:00", "New", 0, None), ("14:47:10", "Canceled", 0, None)]},
                    symbol="POW")
    exF = make_exec(tF, bF, closed_filled=0, atc_child=False, order=oF)
    exF.state["parents"]["BUY-POW-01"]["children"].append(
        {"oid": "206151", "qty": 500, "price": 12000, "filled": 0, "status": "open",
         "ts": "2099-01-01T14:20:00"})
    exF._save_state()
    c = run(tF, "14:45:08", [exF])
    chF = exF.state["parents"]["BUY-POW-01"]["children"][0]
    check("F1 child closed + released, filled 0, DONE journal, thoát ≤14:47:30",
          chF["status"] == "closed" and chF.get("released") and chF["filled"] == 0
          and journal(exF, "ATC_POSTCLOSE_DONE") and c.now().time() <= dt.time(14, 47, 30),
          f"{chF} {c.now().time()}")
    check("F2 shared reservation POW trả về 0", exF.shared.get("POW", 0) == 0, str(exF.shared))

    # ------------------------------------------------------------------ G
    print("G. 2 account — chỉ poll account còn child mở")
    tG = os.path.join(tmp, "G")
    bG1 = FakeBroker({"483161": CLOSED_OK,
                      "502431": [("14:30:19", "New", 0, None), ("14:45:50", "Filled", 600, 57500)]})
    bG2 = FakeBroker({"483161": CLOSED_OK})
    exG1 = make_exec(tG, bG1, label=TAG + "-zp")
    exG2 = make_exec(tG, bG2, label=TAG + "-sx", atc_child=False)
    c = run(tG, "14:45:05", [exG1, exG2])
    check("G1 account có child mở khớp đủ", exG1.state["parents"]["SELL-VHC-01"]["filled"] == 1800)
    check("G2 account không child mở chỉ 1 poll", bG2.polls == 1, f"polls={bG2.polls}")

    # ------------------------------------------------------------------ I
    print("I. poll lỗi trong lúc chờ")
    tI = os.path.join(tmp, "I")
    bI = FakeBroker({"483161": CLOSED_OK,
                     "502431": [("14:30:19", "New", 0, None), ("14:45:30", "Filled", 600, 57500)]})
    bI.fail_polls = {2, 3}                       # poll 1 = step; 2,3 = 2 vòng chờ đầu lỗi
    exI = make_exec(tI, bI)
    run(tI, "14:45:05", [exI])
    pf = [r["note"] for r in journal(exI, "POLL_FAIL")]
    check("I1 2 POLL_FAIL 'postclose: HTTP 503', vòng chờ tiếp tục tới DONE + FILL 600",
          len(pf) == 2 and all(n.startswith("postclose: HTTP 503") for n in pf)
          and journal(exI, "ATC_POSTCLOSE_DONE")
          and exI.state["parents"]["SELL-VHC-01"]["filled"] == 1800, str(pf))
    check("I2 report vẫn ghi đủ", "| 1,800 | 1,800 | 100% |" in open(exI.report_file, encoding="utf-8").read())
    tI3 = os.path.join(tmp, "I3")
    bI3 = FakeBroker({"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]})
    bI3.fail_polls = set(range(2, 200))
    n_to = len([e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_TIMEOUT"])
    exI3 = make_exec(tI3, bI3, label=TAG + "-i3")
    run(tI3, "14:45:05", [exI3])
    tjI = journal(exI3, "ATC_POSTCLOSE_TIMEOUT")
    evI = [e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_TIMEOUT"][n_to:]
    check("I3 mọi poll lỗi ⇒ TIMEOUT nói 'chưa poll thành công' + lỗi thật, KHÔNG nói 'không có oid'",
          tjI and "chưa poll thành công" in tjI[0]["note"] and "HTTP 503" in tjI[0]["note"]
          and "KHÔNG có oid" not in tjI[0]["note"]
          and evI and "HTTP 503" in evI[0]["payload"]["children"][0]["last_seen"],
          tjI[0]["note"] if tjI else "no TIMEOUT")
    check("I4 report vẫn ghi khi timeout", os.path.exists(exI3.report_file))

    # ------------------------------------------------------------------ J
    print("J. lỗi bất ngờ trong vòng chờ không chặn report")
    tJ = os.path.join(tmp, "J")
    exJ = make_exec(tJ, FakeBroker({"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]}),
                    label=TAG + "-j")
    _orig_journal = exJ._journal

    def _journal_disk_full(event, *a, **k):
        if event == "ATC_POSTCLOSE_WAIT":
            raise OSError("No space left on device (giả lập)")
        return _orig_journal(event, *a, **k)
    exJ._journal = _journal_disk_full
    n_err = len([e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_ERROR"])
    run(tJ, "14:45:05", [exJ])
    errJ = journal(exJ, "ATC_POSTCLOSE_ERROR")
    check("J1 ATC_POSTCLOSE_ERROR journal (lỗi nguyên văn) + report vẫn ghi",
          errJ and "No space left" in errJ[0]["note"] and os.path.exists(exJ.report_file), str(errJ))
    check("J2 bus error ATC_POSTCLOSE_ERROR 1 lần",
          len([e for e in sink_events(sink) if e["topic"] == "ATC_POSTCLOSE_ERROR"]) == n_err + 1)

    # ------------------------------------------------------------------ K
    print("K. ngoài cửa sổ chờ ⇒ SKIP, không chờ")
    for name, day, hhmm, pdate in [("K1 thứ Bảy 10:00", dt.date(2026, 7, 11), "10:00:00", "2026-07-11"),
                                    ("K2 lễ 02/09 14:46", dt.date(2026, 9, 2), "14:46:00", "2026-09-02"),
                                    ("K3 plan_date ≠ hôm nay", dt.date(2026, 7, 10), "14:45:05", "2026-07-09"),
                                    ("K4 chạy lại 15:10 sau deadline", dt.date(2026, 7, 10), "15:10:00", "2026-07-10")]:
        tK = os.path.join(tmp, "K" + name[:2])
        bK = FakeBroker({"483161": CLOSED_OK, "502431": [("14:30:19", "New", 0, None)]})
        exK = make_exec(tK, bK, plan_date=pdate, label=f"{TAG}-{name[:2].lower()}")
        n_all = len(sink_events(sink))
        c = run(tK, hhmm, [exK], day=day)
        sk = journal(exK, "ATC_POSTCLOSE_SKIP")
        check(f"{name}: SKIP, 0 sleep, 1 poll, 0 WAIT/TIMEOUT, 0 bus",
              len(sk) == 1 and c.sleeps == [] and bK.polls == 1
              and not journal(exK, "ATC_POSTCLOSE_WAIT") and not journal(exK, "ATC_POSTCLOSE_TIMEOUT")
              and len(sink_events(sink)) == n_all, sk[0]["note"] if sk else f"sleeps={len(c.sleeps)}")
    check("P2 không chờ ⇒ 0 lần đọc cash thêm", bK.cash_calls == 0)

# ---------------------------------------------------------------------- H (đồng hồ thật)
print("H. đồng hồ thật, không patch")
import importlib  # noqa: E402
X2 = importlib.reload(X)       # bỏ mọi monkeypatch (now_ict/time/STOP_FILE)
with tempfile.TemporaryDirectory() as tmpH:

    exH = type("E", (), {"_postclose_pending": lambda self: [], "label": "h"})()
    w0 = _real_time.monotonic()
    X2._await_postclose_fills([exH])
    check("H1 không child mở ⇒ return <1s (đồng hồ thật)", _real_time.monotonic() - w0 < 1.0)
    from zoneinfo import ZoneInfo
    ict = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    check("H2 now_ict() = giờ ICT bất kể TZ process", abs((X2.now_ict() - ict).total_seconds()) < 5,
          f"TZ={os.environ.get('TZ')} now_ict={X2.now_ict():%H:%M:%S} ict={ict:%H:%M:%S}")
    check("H3 hằng số deadline 14:55 / poll 15s", X2.ATC_POSTCLOSE_DEADLINE == dt.time(14, 55)
          and X2.ATC_POSTCLOSE_POLL_SEC == 15)

for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*")):
    os.remove(f)
print(f"\n{npass} PASS / {len(fails)} FAIL" + (f" — {fails}" if fails else ""))
sys.exit(1 if fails else 0)
