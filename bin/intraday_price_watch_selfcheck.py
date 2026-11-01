#!/usr/bin/env python3
"""intraday_price_watch_selfcheck.py — selfcheck cổng giá trong phiên + HỒ SƠ DD KHỦNG HOẢNG.

Viết lại 2026-11-01 (job Taylor_20261101_130722) theo quyết định user "cutloss không tự làm … mặc định
giữ": bộ cũ kiểm bộ máy bán (4 chế độ, ATO/ATC, phán quyết→bán, replay bán) — phần đó đã GỠ khỏi code
nên test của nó gỡ theo (bản cũ còn trong git history + agents/Taylor/research/intraday_watch_20261006/).

  A. engine thuần: cổng kích hoạt (ngưỡng GIỮ NGUYÊN), gộp cả thị trường, cửa sổ trượt, lịch hồ sơ dd_due.
  B. driver với phụ thuộc GIẢ + stub dispatch.sh (argv THẬT): kích hoạt ⇒ báo + mở hồ sơ + dispatch ngày 1;
     ghi chú agent (dd-note) ⇒ báo; ngày 2..7 cập nhật; nhắc ngày 3/6 (bù cuối tuần); hết 7 ngày / sự kiện
     lớn ⇒ kết luận; job chết ⇒ cảnh báo + CHƯA RÕ; kích hoạt lại khi hồ sơ mở; gộp cả thị trường;
     at-most-once; EOD_OOS.
  C. KHÔNG CÒN ĐƯỜNG BÁN: quét AST 2 module (tên/thuộc tính/chuỗi cấm, import module đặt lệnh) + đột biến
     (chèn đường bán vào bản sao ⇒ máy quét PHẢI bắt) + ReadOnlyDNSE chặn place_order + mọi log/tin của vòng
     đời đầy đủ không có sự kiện/lệnh bán, mọi tin DD nói "GIỮ".

Không gọi mạng, không gửi tin, không dispatch thật. State vào thư mục tạm. Giờ trong test là ICT naive
truyền tường minh ⇒ chạy được dưới mọi TZ (kiểm: env -u TZ, TZ=America/New_York).
Chạy: $DNA_PYEXE bin/intraday_price_watch_selfcheck.py [-v]
"""
import ast
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

import intraday_cutloss_engine as E  # noqa: E402
import intraday_price_watch as W  # noqa: E402

VERBOSE = "-v" in sys.argv
N_PASS, FAILS = 0, []


def check(name, cond, detail=""):
    global N_PASS
    if cond:
        N_PASS += 1
        if VERBOSE:
            print(f"  ok  {name}")
    else:
        FAILS.append(f"{name} {detail}")
        print(f"  FAIL {name} {detail}")


def T(hhmm, day="2026-10-06"):
    return dt.datetime.fromisoformat(f"{day}T{hhmm}")


# ================================================================ A. engine
def test_trigger():
    tr = E.trigger_check(95_000, 100_000, 93_000, 1000, 1000)
    check("trigger −5,0%/idio −4,0 biên ⇒ kích hoạt", tr["hit"])
    tr = E.trigger_check(95_100, 100_000, 93_000, 1000, 1000)
    check("trigger −4,9% ⇒ không", not tr["hit"])
    tr = E.trigger_check(94_000, 100_000, 93_000, 970, 1000)
    check("trigger −6% nhưng VNI −3% (idio −3) ⇒ không (cả thị trường)", not tr["hit"])
    tr = E.trigger_check(94_000, 100_000, 93_000, 990, 1000)
    check("trigger −6%, VNI −1% (idio −5) ⇒ kích hoạt", tr["hit"])
    tr = E.trigger_check(93_000, 100_000, 93_000, 940, 1000)
    check("chạm sàn ⇒ kích hoạt dù idio nhỏ", tr["hit"] and tr["at_floor"])
    tr = E.trigger_check(94_000, 100_000, 93_000, None, 1000)
    check("thiếu VNINDEX ⇒ idio=ret + cờ", tr["hit"] and tr["vni_missing"])
    check("thiếu last/ref ⇒ None (không phát biểu)", E.trigger_check(None, 100_000, 93_000, 1, 1) is None)
    # (d) ngưỡng tương đối theo biên độ sàn — chỉ log
    r = E.trigger_check_rel(96_500, 100_000, 93_000, 1000, 1000, "HOSE")
    check("rel HOSE −3,5% ⇒ kích hoạt (ngưỡng hiện hành thì không)", r["hit"]
          and not E.trigger_check(96_500, 100_000, 93_000, 1000, 1000)["hit"])
    check("rel HNX −4% ⇒ không (ngưỡng −4,5%)", not E.trigger_check_rel(96_000, 100_000, 90_000, 1000, 1000, "HNX")["hit"])
    check("rel UPCOM −6,5% ⇒ không (−7%)", not E.trigger_check_rel(93_500, 100_000, 85_000, 1000, 1000, "UPCOM")["hit"])
    check("rel UPCOM −7% ⇒ kích hoạt", E.trigger_check_rel(93_000, 100_000, 85_000, 1000, 1000, "UPCOM")["hit"])
    check("rel idio −3: HOSE −3,5% nhưng VNI −1% (idio −2,5) ⇒ không",
          not E.trigger_check_rel(96_500, 100_000, 93_000, 990, 1000, "HOSE")["hit"])
    # cảnh báo gộp cả thị trường
    h = lambda **k: {"hit": True, "vni_missing": False, "at_floor": False, **k}
    check("1 mã ⇒ không gộp", E.market_wide_reason([h()]) is None)
    check("2 mã ⇒ không gộp", E.market_wide_reason([h(), h()]) is None)
    check("3 mã ⇒ gộp", "3 mã" in (E.market_wide_reason([h(), h(), h()]) or ""))
    check("2 mã chạm sàn ⇒ gộp", "sàn" in (E.market_wide_reason([h(at_floor=True), h(at_floor=True)]) or ""))
    check("thiếu VNINDEX (1 mã) ⇒ gộp", "VNINDEX" in (E.market_wide_reason([h(vni_missing=True)]) or ""))
    check("không có mã ⇒ None", E.market_wide_reason([]) is None)

def test_window_and_due():
    ev = [{"ticker": t, "at": T(h), "at_floor": False} for t, h in (("A", "09:30"), ("B", "10:00"), ("C", "10:25"))]
    check("cửa sổ 60' giao dịch: 3 mã trong 55' ⇒ gộp", E.window_market_wide_reason(ev, T("10:25")) is not None)
    check("cửa sổ: 3 mã trải 2h ⇒ không gộp",
          E.window_market_wide_reason([{**e, "at": T(h)} for e, h in zip(ev, ("09:15", "10:30", "11:20"))],
                                      T("11:20")) is None)
    check("phút giao dịch trừ nghỉ trưa: 11:15→13:15 = 30'", abs(E.trading_minutes(T("11:15"), T("13:15")) - 30) < 1e-6)
    check("ngưỡng kích hoạt GIỮ NGUYÊN −5%/−4%", E.TRIG_RET == -0.05 and E.TRIG_IDIO == -0.04)
    d = {"status": "OPEN", "t0": "2026-10-06T10:00:00"}
    D = lambda s: dt.date.fromisoformat(s)  # noqa: E731
    check("dd_due ngày 1 ⇒ []", E.dd_due(d, D("2026-10-06")) == [])
    check("dd_due ngày 2 ⇒ daily", E.dd_due(d, D("2026-10-07")) == ["daily"])
    check("dd_due ngày 3 ⇒ remind:3 + daily", E.dd_due(d, D("2026-10-08")) == ["remind:3", "daily"])
    check("dd_due ngày 3 đã nhắc + đã cập nhật ⇒ []",
          E.dd_due({**d, "reminders": ["remind:3"], "daily_requested": ["2026-10-08"]}, D("2026-10-08")) == [])
    check("dd_due ngày 7 chưa nhắc 3,6 ⇒ bù cả 2", E.dd_due(d, D("2026-10-12"))[:2] == ["remind:3", "remind:6"])
    check("dd_due ngày 8 ⇒ final (không daily, không nhắc)", E.dd_due(d, D("2026-10-13")) == ["final"])
    check("dd_due sự kiện lớn ngày 2 ⇒ final", E.dd_due({**d, "major_event": {"day": 2}}, D("2026-10-07")) == ["final"])
    check("dd_due đã xin final ⇒ không xin lại",
          "final" not in E.dd_due({**d, "final_requested": {"at": "x"}}, D("2026-10-14")))
    check("dd_due CONCLUDED ⇒ []", E.dd_due({**d, "status": "CONCLUDED"}, D("2026-10-08")) == [])


# ================================================================ B. driver
class Clock:
    now = None


class FakeMarket:
    """Giá riêng từng mã: by = {mã: {"HH:MM": giá}} (ngày bất kỳ — giá theo giờ trong ngày)."""

    def __init__(self, clock, by, ref=100_000, exch="HNX", vni=(1000.0, 1000.0), pos=None):
        self.c, self.by, self.ref, self.exch, self.vni_, self.pos = clock, by, ref, exch, vni, pos or {}
        self.calls = []

    def quote(self, sym):
        self.calls.append(("quote", sym))
        last = None
        for hhmm, px in sorted(self.by.get(sym, {"09:00": self.ref}).items()):
            if T(hhmm, self.c.now.date().isoformat()) <= self.c.now:
                last = px
        return {"last": last, "ref": self.ref, "floor": E.floor_price(self.ref, self.exch), "bid": last,
                "bids": [], "exchange": self.exch, "exchange_known": True, "day_volume": 0}

    def bars(self, sym, day, index=False):
        return []

    def vni(self, now):
        return self.vni_

    def positions(self, account_id):
        self.calls.append(("positions", account_id))
        return self.pos

    def open_buys(self, account_id, sym):
        return []


def _uni(tks=("XYZ",), qty=1000, book="BAL"):
    return {tk: {"holdings": {"SpaceX": {"qty": qty, "sellable": qty, "cost": 110_000, "book": book,
                                         "account_id": "A1"}}, "buys": [], "watch": False} for tk in tks}


def _write_stub(d):
    rec = os.path.join(d, "rec")
    stub = os.path.join(d, "dispatch.sh")
    with open(stub, "w") as f:
        f.write(f"""#!/bin/bash
# stub: mô phỏng parser cờ + chặn self-dispatch của mike/bin/dispatch.sh thật; đếm số lần gọi
n=$(cat "{rec}.n" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "{rec}.n"
printf '%s\\0' "$@" > "{rec}.argv.$n"; printf '%s' "${{DISPATCH_FROM:-Mike}}" > "{rec}.from"
id="$1"; shift 2
from="${{DISPATCH_FROM:-Mike}}"
while [ $# -gt 0 ]; do
  case "$1" in
    --bg) ;;
    --thread|--timeout|--retries|--model|--effort) [ -n "$2" ] || exit 1; shift ;;
    *) echo "ERROR: unknown argument '$1'" >&2; exit 1 ;;
  esac
  shift
done
if [ "$from" = "$id" ]; then echo "ERROR: self-dispatch blocked ($from -> $id)." >&2; exit 2; fi
echo "DISPATCHED $id (job=${{id}}_job$n pid=1) → log: x"
""")
    os.chmod(stub, 0o755)
    return stub, rec


class Env:
    """1 thư mục tạm + thị trường giả + stub dispatch; job_status điều khiển được."""

    def __init__(self, by, uni=None, dispatch=True, vni=(1000.0, 1000.0)):
        self.tmp = tempfile.mkdtemp(prefix="ipw_dd_")
        self.clock = Clock()
        self.mkt = FakeMarket(self.clock, by, vni=vni)
        self.stub, self.rec = _write_stub(self.tmp)
        self.jobs = {}
        self.deps = W.Deps(self.mkt, W.Notifier(dry=True), self.tmp, dispatch=dispatch, accounts=[],
                           universe=uni if uni is not None else _uni(), nav=lambda lab: (1_000_000_000, "x"),
                           dispatch_bin=self.stub, job_status=lambda j: self.jobs.get(j), budget_s=1e9)

    def drive(self, start, end, day):
        t = T(start, day)
        while t <= T(end, day):
            self.clock.now = t
            W.run_tick(t, self.deps)
            t += dt.timedelta(minutes=1)
        return W._read_json(W.state_path(self.tmp, dt.date.fromisoformat(day)))

    def n_dispatch(self):
        p = self.rec + ".n"
        return int(open(p).read()) if os.path.exists(p) else 0

    def argv(self, i):
        return open(f"{self.rec}.argv.{i}").read().split("\0")[:-1]

    def note(self, did, kind, now, summary="s", label=None, major=False):
        a = types.SimpleNamespace(dossier=did, kind=kind, summary=summary, label=label, major_event=major,
                                  detail_file=None, state_dir=self.tmp)
        W.cmd_dd_note(a, now=now)

    def dossier(self, did):
        return W._read_json(W.dd_json(self.tmp, did))

    def sent(self):
        return self.deps.notifier.sent

    def log(self, day):
        p = os.path.join(self.tmp, f"shadow_{day}.jsonl")
        return [json.loads(x) for x in open(p)] if os.path.exists(p) else []

    def close(self):
        shutil.rmtree(self.tmp)


DROP = {"09:00": 100_000, "09:59": 94_000}     # −6%, VNINDEX phẳng ⇒ idio −6 ⇒ ca riêng


def test_lifecycle():
    e = Env({"XYZ": DROP})
    st = e.drive("09:15", "10:20", "2026-10-06")                 # Thứ Ba
    c = st["cases"]["XYZ"]
    did = "XYZ_2026-10-06"
    check("kích hoạt ⇒ ca DD_OPEN + hồ sơ", c["status"] == "DD_OPEN" and c.get("dossier") == did, c.get("status"))
    d = e.dossier(did)
    check("hồ sơ OPEN, mặc định HOLD, có DOSSIER.md", d and d["status"] == "OPEN" and d["default"] == "HOLD"
          and os.path.exists(os.path.join(d["dir"], "DOSSIER.md")))
    check("dispatch ngày 1 đúng 1 lần (job từ stub)", e.n_dispatch() == 1 and d["jobs"]["quick"]["job"] == "Taylor_job1",
          f"n={e.n_dispatch()} {d['jobs']}")
    av = e.argv(1)
    check("argv: Taylor --bg --retries 0 --timeout 1500 thread trading_daily",
          av[0] == "Taylor" and "--bg" in av and av[av.index("--retries") + 1] == "0"
          and av[av.index("--timeout") + 1] == "1500" and av[av.index("--thread") + 1] == "trading_daily", av[2:])
    check("DISPATCH_FROM=intraday_watch", open(e.rec + ".from").read() == "intraday_watch")
    check("prompt ngày 1: legal-vn + dd-note quick + KHÔNG đặt lệnh",
          "legal-vn" in av[1] and "dd-note --dossier XYZ_2026-10-06 --kind quick" in av[1] and "KHÔNG đặt" in av[1])
    t0 = [m for m in e.sent() if "CỔNG GIÁ TRONG PHIÊN" in m["msg"]]
    check("tin T0 qua discord+telegram+email, có MỞ HỒ SƠ + GIỮ",
          {m["channel"] for m in t0} == {"discord", "telegram", "email"}
          and all("MỞ HỒ SƠ DD KHỦNG HOẢNG" in m["msg"] and "MẶC ĐỊNH GIỮ" in m["msg"] for m in t0), t0[:1])
    # ghi chú ngày 1 ⇒ báo tóm tắt nhanh
    e.note(did, "quick", T("10:30", "2026-10-06"), summary="chưa thấy tin pháp lý")
    e.note(did, "quick", T("10:31", "2026-10-06"), summary="LẦN 2 không được ghi đè")
    check("dd-note ghi-một-lần", W._read_json(os.path.join(d["dir"], "notes", "quick.json"))["summary"]
          == "chưa thấy tin pháp lý")
    try:
        e.note(did, "daily", T("10:00", "2026-10-05"))
        check("dd-note từ chối ngày trước T0", False)
    except SystemExit:
        check("dd-note từ chối ngày trước T0", True)
    check("DOSSIER.md có mục Ngày 1", "Ngày 1 — tóm tắt nhanh" in open(os.path.join(d["dir"], "DOSSIER.md")).read())
    e.drive("10:32", "10:34", "2026-10-06")
    q = [m for m in e.sent() if "TÓM TẮT NHANH NGÀY 1" in m["msg"]]
    check("tóm tắt ngày 1 báo đúng 1 lần × 3 kênh", len(q) == 3, len(q))
    # ngày 2 (08:30) ⇒ cập nhật
    e.drive("08:30", "08:35", "2026-10-07")
    check("ngày 2 08:30: 1 dispatch daily", e.n_dispatch() == 2 and "--kind daily" in e.argv(2)[1], e.n_dispatch())
    check("ngày 2: không nhắc (mốc 3)", not any("NHẮC" in m["msg"] for m in e.sent()))
    e.drive("09:00", "09:05", "2026-10-07")
    check("ngày 2: không dispatch daily lần 2", e.n_dispatch() == 2)
    e.note(did, "daily", T("11:00", "2026-10-07"), summary="ĐHCĐ bất thường, không dính lõi")
    e.drive("11:01", "11:02", "2026-10-07")
    check("ghi chú daily ⇒ báo 1 dòng discord", any("ngày 2/7" in m["msg"] and m["channel"] == "discord"
                                                     for m in e.sent()))
    # ngày 3 ⇒ nhắc + cập nhật
    e.drive("08:30", "08:40", "2026-10-08")
    rem = [m for m in e.sent() if "NHẮC — hồ sơ DD khủng hoảng XYZ ngày 3/7" in m["msg"]]
    check("ngày 3: nhắc đúng 1 lần × (discord, telegram)", sorted(m["channel"] for m in rem) == ["discord", "telegram"],
          [m["channel"] for m in rem])
    check("nhắc có 'ANH QUYẾT' + GIỮ", all("ANH QUYẾT" in m["msg"] and "GIỮ" in m["msg"] for m in rem))
    check("ngày 3: dispatch daily", e.n_dispatch() == 3)
    # ngày 4,5 (T6) — ngày 6,7 là T7/CN (cron không chạy) ⇒ nhắc 6 bù vào T2 ngày 7
    e.drive("08:30", "08:31", "2026-10-09")
    e.drive("08:30", "08:31", "2026-10-10")     # Thứ Bảy: run_tick bỏ qua
    check("Thứ Bảy: không dispatch", e.n_dispatch() == 4, e.n_dispatch())
    e.drive("08:30", "08:31", "2026-10-12")     # T2 = ngày 7
    check("ngày 7 (T2): nhắc mốc 6 bù", any("ngày 7/7 (mốc 6)" in m["msg"] for m in e.sent()))
    check("ngày 7: dispatch daily", e.n_dispatch() == 5)
    # ngày 8 ⇒ kết luận
    e.drive("08:30", "08:31", "2026-10-13")
    check("ngày 8: dispatch final", e.n_dispatch() == 6 and "--kind final" in e.argv(6)[1]
          and "--label LABEL" in e.argv(6)[1] and e.argv(6)[e.argv(6).index("--timeout") + 1] == "1800")
    e.note(did, "final", T("09:30", "2026-10-13"), summary="KQKD sụp, kiểm toán ngoại trừ", label="BROKEN")
    e.drive("09:31", "09:32", "2026-10-13")
    d = e.dossier(did)
    check("final ⇒ CONCLUDED BROKEN (agent)", d["status"] == "CONCLUDED" and d["conclusion"]["label"] == "BROKEN"
          and d["conclusion"]["source"] == "agent", d.get("conclusion"))
    fin = [m for m in e.sent() if "KẾT LUẬN HỒ SƠ DD KHỦNG HOẢNG XYZ" in m["msg"]]
    check("kết luận báo 3 kênh, GÃY, ANH QUYẾT, mặc định GIỮ", len(fin) == 3 and all(
        "GÃY" in m["msg"] and "ANH QUYẾT" in m["msg"] and "MẶC ĐỊNH GIỮ" in m["msg"] for m in fin))
    e.drive("08:30", "08:31", "2026-10-14")
    check("sau kết luận: không dispatch nữa", e.n_dispatch() == 6)
    check("vị thế không bị đụng: market chỉ quote/positions", all(k in ("quote", "positions") for k, _ in e.mkt.calls))
    return e


def test_major_event_and_dead_jobs():
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    did = "XYZ_2026-10-06"
    e.drive("08:30", "08:31", "2026-10-07")
    e.note(did, "daily", T("10:00", "2026-10-07"), summary="khởi tố pháp nhân", major=True)
    e.drive("10:01", "10:02", "2026-10-07")
    check("sự kiện lớn ⇒ báo ⚠️ + dispatch final sớm", any("SỰ KIỆN LỚN" in m["msg"] for m in e.sent())
          and e.n_dispatch() == 3 and "--kind final" in e.argv(3)[1], e.n_dispatch())
    check("final_requested ghi lý do 'sự kiện lớn'", e.dossier(did)["final_requested"]["why"] == "sự kiện lớn")
    # job final chết, không ghi chú ⇒ CHƯA RÕ no_agent
    e.jobs["Taylor_job3"] = "timeout"
    e.drive("10:30", "10:31", "2026-10-07")
    d = e.dossier(did)
    check("final job chết ⇒ CONCLUDED UNCLEAR no_agent", d["status"] == "CONCLUDED"
          and d["conclusion"] == {**d["conclusion"], "label": "UNCLEAR", "source": "no_agent"}, d.get("conclusion"))
    check("báo CHƯA RÕ + ANH CẦN TỰ XEM", any("CHƯA RÕ" in m["msg"] and "ANH CẦN TỰ XEM" in m["msg"] for m in e.sent()))
    e.close()
    # job ngày 1 chết ⇒ cảnh báo + dừng dispatch tới hết ngày
    e = Env({"XYZ": DROP, "ABC": {"09:00": 100_000, "10:59": 93_000}}, uni=_uni(("XYZ", "ABC")))
    e.drive("09:15", "10:05", "2026-10-06")
    e.jobs["Taylor_job1"] = "failed"
    e.drive("10:06", "11:20", "2026-10-06")
    st = W._read_json(W.state_path(e.tmp, dt.date(2026, 10, 6)))
    check("job ngày 1 chết ⇒ cảnh báo thiếu tóm tắt", any("thiếu tóm tắt ngày 1" in m["msg"] for m in e.sent()))
    check("⇒ dispatch DỪNG, mã sau (ABC) không dispatch, tin T0 nói rõ", st.get("dispatch_halted")
          and e.n_dispatch() == 1 and "dispatch đã DỪNG" in (st["cases"]["ABC"]["investigation"].get("skipped") or "")
          and any("KHÔNG dispatch được tóm tắt ngày 1" in m["msg"] and "ABC" in m["msg"] for m in e.sent()),
          (e.n_dispatch(), st["cases"].get("ABC", {}).get("investigation")))
    check("ABC vẫn có hồ sơ OPEN (thu thập ngày sau)", (e.dossier("ABC_2026-10-06") or {}).get("status") == "OPEN")
    e.close()


def test_retrigger_marketwide_atmostonce():
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("09:15", "10:05", "2026-10-07")          # kích hoạt lại ngày 2 (giá lại −6% so TC giả)
    st = W._read_json(W.state_path(e.tmp, dt.date(2026, 10, 7)))
    c = st["cases"]["XYZ"]
    d = e.dossier("XYZ_2026-10-06")
    check("kích hoạt lại khi hồ sơ mở ⇒ DD_EXISTING, không hồ sơ mới", c["status"] == "DD_EXISTING"
          and not os.path.exists(W.dd_json(e.tmp, "XYZ_2026-10-07")), c["status"])
    check("lần kích hoạt lại ghi vào hồ sơ", len(d["retriggers"]) == 1)
    check("không dispatch ngày 1 lần 2 (chỉ quick ngày 1 + daily ngày 2)", e.n_dispatch() == 2, e.n_dispatch())
    check("tin báo hồ sơ ĐANG MỞ", any("ĐANG MỞ" in m["msg"] for m in e.sent()))
    e.close()
    # gộp cả thị trường: 3 mã cùng lượt ⇒ không ca/hồ sơ
    e = Env({t: DROP for t in ("AAA", "BBB", "CCC")}, uni=_uni(("AAA", "BBB", "CCC")))
    st = e.drive("09:15", "10:05", "2026-10-06")
    check("3 mã cùng lượt ⇒ gộp, 0 ca, 0 hồ sơ, 0 dispatch", not st["cases"] and not W.load_dossiers(e.tmp)
          and e.n_dispatch() == 0)
    check("tin gộp: KHÔNG mở hồ sơ + GIỮ", any("KHÔNG mở hồ sơ DD từng mã" in m["msg"] and "GIỮ" in m["msg"]
                                               for m in e.sent()))
    e.close()
    # at-most-once: cờ dispatch đã ghi mà không có job (bị cắt) ⇒ không dispatch lại
    e = Env({"XYZ": DROP})
    e.drive("09:15", "09:58", "2026-10-06")
    orig = W.dispatch_dd
    W.dispatch_dd = lambda *a, **k: (_ for _ in ()).throw(W.RunKilled("cắt giữa dispatch"))
    try:
        e.drive("09:59", "10:00", "2026-10-06")
    except W.RunKilled:
        pass
    W.dispatch_dd = orig
    e.drive("10:01", "10:03", "2026-10-06")
    d = e.dossier("XYZ_2026-10-06")
    check("bị cắt giữa dispatch ⇒ không dispatch lại + ghi chú", e.n_dispatch() == 0
          and "at-most-once" in (d["jobs"]["quick"].get("note") or ""), d["jobs"])
    check("…và vẫn gửi tin T0", any("CỔNG GIÁ TRONG PHIÊN" in m["msg"] for m in e.sent()))
    e.close()


def test_eod_oos():
    e = Env({"XYZ": DROP, "ABC": {"09:00": 100_000, "14:00": 99_000}}, uni=_uni(("XYZ", "ABC")))
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("14:54", "14:56", "2026-10-06")
    ev = [x for x in e.log("2026-10-06") if x["kind"] == "EOD_OOS"]
    check("EOD_OOS 1 dòng/ngày, có ca XYZ kèm dossier", len(ev) == 1 and any(
        r["ticker"] == "XYZ" and r["kind"] == "case" and r["dossier"] == "XYZ_2026-10-06" for r in ev[0]["rows"]))
    e.drive("14:54", "14:56", "2026-10-07")
    ev = [x for x in e.log("2026-10-07") if x["kind"] == "EOD_OOS"]
    check("ngày 2: hồ sơ mở ⇒ dòng kind=dossier, dd_day=2", ev and any(
        r["ticker"] == "XYZ" and r["kind"] == "dossier" and r["dd_day"] == 2 for r in ev[0]["rows"]), ev)
    e.close()


# ================================================================ C. không còn đường bán
FORBID_NAMES = {"SELL_ALL", "SELL_HALF", "step_execution", "new_execution", "default_action", "target_qty",
                "parse_reply", "write_no_rebuy", "_apply_decision", "select_mode", "match_book", "_place",
                "place_order", "cancel_order", "modify_order", "replace_order", "submit_order", "new_order",
                "execute_plan", "bot_execute"}
FORBID_STR = re.compile(r"CUTLOSS_TICK|DEFAULT_APPLIED|USER_REPLY|SHADOW BÁN|BÁN 50%|BÁN toàn bộ")
FORBID_MOD = re.compile(r"trading_bot\.(executor|plan|bot_execute|order)|executor|plan_funding_gate")


def scan_no_sell(src):
    """→ danh sách vi phạm (rỗng = sạch)."""
    bad = []
    for n in ast.walk(ast.parse(src)):
        name = (n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute)
                else n.name if isinstance(n, (ast.FunctionDef, ast.ClassDef)) else None)
        if name in FORBID_NAMES:
            bad.append(f"L{n.lineno}:{name}")
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and FORBID_STR.search(n.value):
            bad.append(f"L{n.lineno}:str:{FORBID_STR.search(n.value).group(0)}")
        if isinstance(n, ast.ImportFrom) and n.module and FORBID_MOD.search(n.module):
            bad.append(f"L{n.lineno}:import {n.module}")
        if isinstance(n, ast.Import):
            bad += [f"L{n.lineno}:import {a.name}" for a in n.names if FORBID_MOD.search(a.name)]
    return bad


def test_no_sell_path(lifecycle_env):
    for fn in ("intraday_price_watch.py", "intraday_cutloss_engine.py"):
        v = scan_no_sell(open(os.path.join(HERE, fn), encoding="utf-8").read())
        check(f"AST {fn}: 0 tên/chuỗi/import đường bán", not v, v[:8])
    # đột biến: chèn đường bán ⇒ máy quét PHẢI bắt (máy quét không mù)
    base = open(os.path.join(HERE, "intraday_price_watch.py"), encoding="utf-8").read()
    muts = {"place_order": "\ndef _x(m):\n    m.ro.place_order('XYZ', 100)\n",
            "SELL_ALL": "\nZ = E.SELL_ALL\n",
            "import executor": "\nfrom trading_bot.executor import Executor\n",
            "log CUTLOSS_TICK": "\ndef _y(d):\n    log_event(d, None, 'CUTLOSS_TICK')\n",
            "lệnh bán user": "\nCMD = 'SHADOW BÁN XYZ'\n",
            "new_execution": "\ndef new_execution(t):\n    return t\n"}
    for k, m in muts.items():
        check(f"đột biến [{k}] bị máy quét bắt", scan_no_sell(base + m), k)
    # runtime: proxy DNSE chặn mọi hàm đặt/huỷ lệnh
    class C:
        def place_order(self, *a):
            return "ĐÃ ĐẶT"
        cancel_order = place_order

        def latest_trade(self, s):
            return 1
    ro = W.ReadOnlyDNSE(C())
    for fn in ("place_order", "cancel_order"):
        try:
            getattr(ro, fn)("XYZ")
            check(f"ReadOnlyDNSE chặn {fn}", False)
        except PermissionError:
            check(f"ReadOnlyDNSE chặn {fn}", True)
    check("ReadOnlyDNSE cho inquiry", ro.latest_trade("XYZ") == 1)
    check("whitelist chỉ inquiry", W.ReadOnlyDNSE.ALLOWED == frozenset(
        {"secdef", "latest_trade", "latest_quote", "positions", "orders", "ohlc"}))
    # vòng đời đầy đủ (test_lifecycle): log không có sự kiện bán; mọi tin DD nói GIỮ; không tin nào mời lệnh bán
    e = lifecycle_env
    kinds = set()
    for f in os.listdir(e.tmp):
        if f.startswith("shadow_"):
            kinds |= {json.loads(x)["kind"] for x in open(os.path.join(e.tmp, f))}
    check("log vòng đời: 0 sự kiện bán/mặc định bán", not kinds & {"CUTLOSS_TICK", "DEFAULT_APPLIED", "USER_REPLY",
                                                                   "NO_AUTO_SELL", "VERDICT"}, kinds)
    msgs = [m["msg"] for m in e.sent()]
    dd = [m for m in msgs if any(k in m for k in ("CỔNG GIÁ", "DD khủng hoảng", "KẾT LUẬN", "NHẮC"))]
    check("mọi tin DD/cổng giá có 'GIỮ'", dd and all("GIỮ" in m for m in dd),
          [m[:80] for m in dd if "GIỮ" not in m])
    check("không tin nào mời lệnh 'BÁN <MÃ>'", not any(re.search(r"BÁN( 50%)? [A-Z]{3}\b", m) for m in msgs))
    state_files = [f for f in os.listdir(e.tmp) if f.startswith("state_")]
    check("state không có khối execution/actions_default", not any(
        "execution" in json.dumps(W._read_json(os.path.join(e.tmp, f))) or "actions_default" in
        json.dumps(W._read_json(os.path.join(e.tmp, f))) for f in state_files))
    e.close()


# ---------------------------------------------------------------- vòng 2: arch-review 2026-11-01
def _stub_fail(e, rc=4):
    open(e.stub, "w").write(f"#!/bin/bash\necho 'CIRCUIT TRIPPED' >&2; exit {rc}\n")
    os.chmod(e.stub, 0o755)


def _stub_nojob(e):
    open(e.stub, "w").write("#!/bin/bash\necho 'accepted'\n")
    os.chmod(e.stub, 0o755)


def _tick_to_final(e, until="2026-10-12"):
    """Mở ca ngày 6/10, chạy mỗi ngày giao dịch tới `until` (ngày 7 của hồ sơ)."""
    e.drive("09:15", "10:05", "2026-10-06")
    for d in ("2026-10-07", "2026-10-08", "2026-10-09", "2026-10-12"):
        e.drive("08:30", "08:31", d)
        if d == until:
            break


def _concl_msgs(e):
    return [m for m in e.sent() if "KHÔNG có báo cáo kết luận" in m["msg"]]


def test_final_never_stuck():
    did = "XYZ_2026-10-06"
    # (a1) dispatch kết luận rc!=0 (circuit breaker exit 4) ⇒ đóng CHƯA RÕ no_dispatch + 3 kênh
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    _stub_fail(e)
    e.drive("08:30", "08:30", "2026-10-13")          # 1 tick: đóng NGAY, không đợi lượt sau
    d = e.dossier(did)
    check("final rc!=0 ⇒ CONCLUDED UNCLEAR no_dispatch", d["status"] == "CONCLUDED"
          and d["conclusion"]["label"] == "UNCLEAR" and d["conclusion"]["source"] == "no_dispatch", d.get("conclusion"))
    check("final rc!=0 ⇒ tin 3 kênh có lỗi thật + ANH CẦN TỰ XEM + GIỮ",
          {m["channel"] for m in _concl_msgs(e)} == {"discord", "telegram", "email"}
          and all("CIRCUIT TRIPPED" in m["msg"] and "ANH CẦN TỰ XEM" in m["msg"] and "GIỮ" in m["msg"]
                  for m in _concl_msgs(e)), [m["msg"][:90] for m in _concl_msgs(e)][:1])
    n0 = len(e.sent())
    for day in ("2026-10-14", "2026-10-20"):
        e.drive("08:30", "08:31", day)
        e.drive("09:15", "09:16", day)
    check("đóng rồi ⇒ không báo/dispatch lại", len(e.sent()) == n0 and e.n_dispatch() == 5, (len(e.sent()) - n0, e.n_dispatch()))
    e.close()
    # (a2) dispatch cập nhật hằng ngày rc!=0 ⇒ health_alert, hồ sơ vẫn OPEN
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    _stub_fail(e)
    e.drive("08:30", "08:31", "2026-10-07")
    check("daily rc!=0 ⇒ health_alert dd_dispatch (không im lặng), hồ sơ vẫn OPEN",
          any("SỨC KHOẺ intraday-watch (dd_dispatch)" in m["msg"] and "HỎNG" in m["msg"] for m in e.sent())
          and e.dossier(did)["status"] == "OPEN", [m["msg"][:60] for m in e.sent()][-2:])
    e.close()
    # (a3) job 'issued' (không parse được job id) ⇒ quá hạn FINAL_OVERDUE_H ⇒ đóng
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    _stub_nojob(e)
    e.drive("08:30", "08:31", "2026-10-13")
    check("final 'issued' chưa quá hạn ⇒ còn OPEN", e.dossier(did)["status"] == "OPEN"
          and e.dossier(did)["jobs"]["final"]["job"] == "issued")
    e.drive("14:31", "14:32", "2026-10-13")
    check("final 'issued' quá 6h ⇒ CONCLUDED no_dispatch + tin", e.dossier(did)["status"] == "CONCLUDED"
          and e.dossier(did)["conclusion"]["source"] == "no_dispatch" and len(_concl_msgs(e)) == 3)
    e.close()
    # (a4) job final thật còn sống, quá hạn ⇒ đóng (job treo vô hạn không giữ hồ sơ OPEN)
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    e.drive("08:30", "08:31", "2026-10-13")
    e.jobs["Taylor_job6"] = "running"
    e.drive("12:00", "12:01", "2026-10-13")
    check("final job còn chạy, chưa quá hạn ⇒ OPEN", e.dossier(did)["status"] == "OPEN")
    e.drive("14:31", "14:32", "2026-10-13")
    check("final job treo quá 6h ⇒ đóng", e.dossier(did)["status"] == "CONCLUDED", e.dossier(did).get("conclusion"))
    e.close()
    # (a5) kết luận không bị trần 6 cập nhật/ngày chặn
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    st = W.load_state(e.tmp, dt.date(2026, 10, 13))
    W._stats(st)["dd_dispatches"] = W.MAX_DD_DISPATCH_PER_DAY
    W._save(e.deps, dt.date(2026, 10, 13), st)
    e.drive("08:30", "08:31", "2026-10-13")
    check("chạm trần 6/ngày ⇒ hồ sơ kết luận VẪN được dispatch", "--kind final" in e.argv(e.n_dispatch())[1]
          and e.dossier(did)["jobs"]["final"].get("job"), e.n_dispatch())
    e.close()
    # (b3) kill ngay sau khi lưu final_requested, trước _dd_dispatch ⇒ lượt sau tự đóng
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    od = W._dd_dispatch

    def kill_final(*a, **k):
        if a[4] == "final":
            raise W.RunKilled("SIGTERM trước dispatch final")
        return od(*a, **k)
    W._dd_dispatch = kill_final
    killed = False
    try:
        e.drive("08:30", "08:30", "2026-10-13")
    except W.RunKilled:
        killed = True
    finally:
        W._dd_dispatch = od
    check("kill trước dispatch final: đã kill + final_requested còn trên đĩa + chưa có job",
          killed and e.dossier(did)["final_requested"] and "final" not in e.dossier(did)["jobs"])
    e.drive("08:31", "08:32", "2026-10-13")
    check("... lượt sau tự đóng CHƯA RÕ + tin 3 kênh, KHÔNG dispatch final",
          e.dossier(did)["status"] == "CONCLUDED" and len(_concl_msgs(e)) == 3 and e.n_dispatch() == 5, e.n_dispatch())
    e.close()
    # (b4) kill GIỮA dispatch (đã ghi dispatch_attempted_at, chưa có job) ⇒ at-most-once + tự đóng
    e = Env({"XYZ": DROP})
    _tick_to_final(e)
    odd = W.dispatch_dd

    def kill_mid(dos, kind, *a, **k):
        if kind == "final":
            raise W.RunKilled("SIGTERM giữa dispatch final")
        return odd(dos, kind, *a, **k)
    W.dispatch_dd = kill_mid
    try:
        e.drive("08:30", "08:30", "2026-10-13")
    except W.RunKilled:
        pass
    finally:
        W.dispatch_dd = odd
    e.drive("08:31", "08:32", "2026-10-13")
    check("kill giữa dispatch final ⇒ lượt sau đóng, không dispatch lại (at-most-once)",
          e.dossier(did)["status"] == "CONCLUDED" and e.n_dispatch() == 5 and len(_concl_msgs(e)) == 3, e.n_dispatch())
    e.close()


def _kill_at_dossier_save(e, pred, start, end, day, before=False):
    """Mô phỏng kill đúng quanh save_dossier của hồ sơ thoả pred: sau (mặc định) hoặc TRƯỚC khi ghi đĩa."""
    osd = W.save_dossier
    hit = {"n": 0}

    def wrapped(state_dir, dos):
        if pred(dos) and not hit["n"]:
            hit["n"] = 1
            if before:
                raise W.RunKilled("SIGTERM trước save_dossier")
            osd(state_dir, dos)
            raise W.RunKilled("SIGTERM sau save_dossier")
        return osd(state_dir, dos)
    W.save_dossier = wrapped
    try:
        e.drive(start, end, day)
    except W.RunKilled:
        pass
    finally:
        W.save_dossier = osd
    return hit["n"] == 1


def _outbox_has(e, day, pat):
    st = W._read_json(W.state_path(e.tmp, dt.date.fromisoformat(day)))
    return any(pat in m["msg"] for m in (st or {}).get("outbox", []))


def _n_sent(e, pat):
    return len([m for m in e.sent() if pat in m["msg"]])


def test_save_order_kill():
    did = "XYZ_2026-10-06"
    # A) ghi chú quick đã relayed trên đĩa ⇒ tin PHẢI đã nằm trong outbox trên đĩa; chạy lại gửi đúng 1 lần/kênh
    for before in (False, True):
        e = Env({"XYZ": DROP})
        e.drive("09:15", "10:05", "2026-10-06")
        e.note(did, "quick", T("10:30", "2026-10-06"), summary="tóm tắt A")
        hit = _kill_at_dossier_save(e, lambda d: "quick.json" in d.get("relayed", []), "10:31", "10:31", "2026-10-06", before)
        tag = "TRƯỚC" if before else "SAU"
        if not before:
            check(f"B5-A kill {tag} save_dossier(note quick): đã kill + tin nằm trong outbox trên đĩa",
                  hit and _outbox_has(e, "2026-10-06", "TÓM TẮT NHANH NGÀY 1"))
        e.drive("10:32", "10:34", "2026-10-06")
        check(f"B5-A kill {tag} save_dossier ⇒ chạy lại: tóm tắt ngày 1 gửi ĐÚNG 3 tin (3 kênh, không mất/không trùng)",
              hit and _n_sent(e, "TÓM TẮT NHANH NGÀY 1") == 3, _n_sent(e, "TÓM TẮT NHANH NGÀY 1"))
        e.close()
    # B) ghi chú final ⇒ CONCLUDED
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("08:30", "08:31", "2026-10-07")
    e.note(did, "final", T("10:00", "2026-10-07"), summary="kết luận B", label="BROKEN")
    hit = _kill_at_dossier_save(e, lambda d: d.get("status") == "CONCLUDED", "10:01", "10:01", "2026-10-07")
    check("B5-B kill sau save_dossier(final note CONCLUDED): tin kết luận đã nằm trong outbox trên đĩa",
          hit and _outbox_has(e, "2026-10-07", "KẾT LUẬN HỒ SƠ DD KHỦNG HOẢNG"))
    e.drive("10:02", "10:04", "2026-10-07")
    check("B5-B ... chạy lại: kết luận gửi ĐÚNG 3 tin", _n_sent(e, "KẾT LUẬN HỒ SƠ DD KHỦNG HOẢNG") == 3,
          _n_sent(e, "KẾT LUẬN HỒ SƠ DD KHỦNG HOẢNG"))
    e.close()
    # C) job final chết không ghi chú
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("08:30", "08:31", "2026-10-07")
    e.note(did, "daily", T("10:00", "2026-10-07"), summary="khởi tố", major=True)
    e.drive("10:01", "10:02", "2026-10-07")
    e.jobs["Taylor_job3"] = "timeout"
    hit = _kill_at_dossier_save(e, lambda d: d.get("status") == "CONCLUDED", "10:30", "10:30", "2026-10-07")
    check("B5-C kill sau save_dossier(job final chết): tin CHƯA RÕ nằm trong outbox trên đĩa",
          hit and _outbox_has(e, "2026-10-07", "KHÔNG có báo cáo"))
    e.drive("10:31", "10:33", "2026-10-07")
    check("B5-C ... chạy lại: tin kết luận job chết gửi ĐÚNG 3 tin", _n_sent(e, "KHÔNG có báo cáo") == 3,
          _n_sent(e, "KHÔNG có báo cáo"))
    e.close()
    # D) _conclude_unclear
    for before in (False, True):
        e = Env({"XYZ": DROP})
        _tick_to_final(e)
        _stub_fail(e)
        hit = _kill_at_dossier_save(e, lambda d: (d.get("conclusion") or {}).get("source") == "no_dispatch",
                                    "08:30", "08:30", "2026-10-13", before)
        tag = "TRƯỚC" if before else "SAU"
        if not before:
            check("B5-D kill SAU save_dossier(_conclude_unclear): tin nằm trong outbox trên đĩa",
                  hit and _outbox_has(e, "2026-10-13", "KHÔNG có báo cáo kết luận"))
        e.drive("08:31", "08:33", "2026-10-13")
        check(f"B5-D kill {tag} save_dossier ⇒ chạy lại: tin CHƯA RÕ gửi ĐÚNG 3 tin", hit and len(_concl_msgs(e)) == 3,
              len(_concl_msgs(e)))
        e.close()


def test_reminders_exact():
    did = "XYZ_2026-10-06"

    def rem(e):
        return [m for m in e.sent() if "NHẮC —" in m["msg"]]
    # (c) vòng đời đầy đủ: ĐÚNG 2 nhắc × (discord, telegram) = 4 tin; cờ trong hồ sơ = [remind:3, remind:6]
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    for d in ("2026-10-07", "2026-10-08", "2026-10-09", "2026-10-12", "2026-10-13"):
        e.drive("08:30", "08:31", d)
        e.drive("09:15", "09:16", d)
    r = rem(e)
    check("vòng đời: đúng 4 tin nhắc (2 mốc × 2 kênh)", len(r) == 4, len(r))
    check("vòng đời: mỗi (mốc, kênh) đúng 1 lần", sorted((("mốc 3" in m["msg"]), m["channel"]) for m in r)
          == [(False, "discord"), (False, "telegram"), (True, "discord"), (True, "telegram")])
    check("cờ hồ sơ reminders == [remind:3, remind:6]", e.dossier(did)["reminders"] == ["remind:3", "remind:6"],
          e.dossier(did)["reminders"])
    e.close()
    # (b1) kill SAU khi tin vào hộp thư + state đã ghi, TRƯỚC khi đánh dấu hồ sơ ⇒ không mất, không gửi đôi
    for slot in ("after_state_before_mark", "before_state"):
        e = Env({"XYZ": DROP})
        e.drive("09:15", "10:05", "2026-10-06")
        e.drive("08:30", "08:31", "2026-10-07")
        if slot == "after_state_before_mark":
            osv, hit = W.save_dossier, {"n": 0}

            def bad_dossier(sd, dos, osv=osv, hit=hit):
                if "remind:3" in dos["reminders"] and not hit["n"]:
                    hit["n"] = 1
                    raise W.RunKilled("SIGTERM giữa nhắc (sau state, trước đánh dấu)")
                return osv(sd, dos)
            W.save_dossier = bad_dossier
        else:
            osv, hit = W._save, {"n": 0}

            def bad_save(deps, day, st, osv=osv, hit=hit):
                if any(m.get("key") == f"dd:{did}:remind:3" for m in st.get("outbox", [])) and not hit["n"]:
                    hit["n"] = 1
                    raise W.RunKilled("SIGTERM giữa nhắc (trước state)")
                return osv(deps, day, st)
            W._save = bad_save
        try:
            e.drive("08:30", "08:30", "2026-10-08")
        except W.RunKilled:
            pass
        finally:
            W.save_dossier = osv if slot == "after_state_before_mark" else W.save_dossier
            if slot == "before_state":
                W._save = osv
        check(f"kill nhắc [{slot}]: đã kill", hit["n"] == 1)
        e.drive("08:31", "08:40", "2026-10-08")
        e.drive("09:15", "09:16", "2026-10-08")
        m3 = [m for m in rem(e) if "mốc 3" in m["msg"]]
        check(f"kill nhắc [{slot}]: mốc 3 tới đúng 2 kênh, mỗi kênh 1 lần, hồ sơ đã đánh dấu",
              sorted(m["channel"] for m in m3) == ["discord", "telegram"]
              and "remind:3" in e.dossier(did)["reminders"], [m["channel"] for m in m3])
        e.close()
    # (d1) nghỉ dài hơn 7 ngày: tick đầu tiên là ngày 10 ⇒ CHỈ final (không nhắc muộn), 1 dispatch
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("08:30", "08:31", "2026-10-15")
    d = e.dossier(did)
    check("nghỉ >7 ngày: không nhắc muộn, final được xin đúng 1 lần",
          not rem(e) and d["final_requested"] and e.n_dispatch() == 2 and "--kind final" in e.argv(2)[1], e.n_dispatch())
    e.note(did, "final", T("09:30", "2026-10-15"), summary="x", label="NOISE")
    e.drive("09:31", "09:32", "2026-10-15")
    check("nghỉ >7 ngày: final ghi → CONCLUDED NOISE", e.dossier(did)["status"] == "CONCLUDED"
          and e.dossier(did)["conclusion"]["label"] == "NOISE")
    e.close()
    # (d2) nghỉ tới ngày 7: cả mốc 3 và 6 đều tới hạn ⇒ KHÔNG bắn cùng tick (mốc 3 tick này, mốc 6 tick sau)
    e = Env({"XYZ": DROP})
    e.drive("09:15", "10:05", "2026-10-06")
    e.drive("08:30", "08:30", "2026-10-12")
    check("tick đầu ngày 7: chỉ mốc 3", [("mốc 3" in m["msg"]) for m in rem(e)] == [True, True], len(rem(e)))
    e.drive("08:31", "08:31", "2026-10-12")
    check("tick sau: mốc 6, tổng 4 tin", len(rem(e)) == 4 and sum("mốc 6" in m["msg"] for m in rem(e)) == 2)
    e.close()


def test_labels_and_note_day():
    e = Env({"XYZ": DROP}, uni=_uni())
    e.mkt.by["XYZ"] = DROP
    e.drive("09:15", "10:05", "2026-10-06")
    check("nhãn tin = [CỔNG GIÁ], không còn [SHADOW]", e.sent() and all(m["msg"].startswith("[CỔNG GIÁ]")
                                                                        for m in e.sent()), e.sent()[:1])
    check("không còn câu 'bản live sẽ' trong tin T0", not any("bản live sẽ" in m["msg"] for m in e.sent()))
    pr = e.argv(1)[1]
    check("prompt dd-note truyền --day = ngày dispatch", "--day 2026-10-06" in pr, pr[-300:])
    # dd-note --day tường minh: ghi đúng ngày của bước dù đồng hồ đã qua nửa đêm
    did = "XYZ_2026-10-06"
    a = types.SimpleNamespace(dossier=did, kind="daily", summary="s", label=None, major_event=False,
                              detail_file=None, state_dir=e.tmp, day="2026-10-08")
    W.cmd_dd_note(a, now=T("00:20", "2026-10-09"))
    check("dd-note --day 2026-10-08 ⇒ daily_d3.json (không phải d4)",
          os.path.exists(os.path.join(e.dossier(did)["dir"], "notes", "daily_d3.json")))
    e.close()


def harden_tests():
    test_final_never_stuck()
    test_save_order_kill()
    test_reminders_exact()
    test_labels_and_note_day()


MUTANTS = [
    ("bỏ dos[\"reminders\"].append", 'dos["reminders"].append(act)', "pass"),
    ("bỏ nhánh rc!=0 của final", "if act == \"final\":\n                    _conclude_unclear(st, deps, now, dos, note)",
     "if act == \"final\":\n                    pass"),
    ("bỏ _stuck_final_reason", "why = _stuck_final_reason(dos, deps, now)\n        if why:", "why = None\n        if why:"),
    ("bỏ health_alert daily hỏng", "health_alert(st, \"dd_dispatch\", f\"dispatch cập nhật hồ sơ", "(lambda *a: 0)(st, \"dd_dispatch\", f\"dispatch cập nhật hồ sơ"),
    ("B5 đảo thứ tự cũ: save_dossier TRƯỚC _save (khối changed)",
     "            _save(deps, day, st)                 # outbox bền TRƯỚC, rồi mới ghi hồ sơ (relayed/CONCLUDED)\n            save_dossier(deps.state_dir, dos)",
     "            save_dossier(deps.state_dir, dos)\n            _save(deps, day, st)"),
    ("B5 đảo thứ tự cũ: save_dossier TRƯỚC enqueue (_conclude_unclear)",
     "    _save(deps, now.date(), st)            # outbox bền TRƯỚC, rồi mới đánh dấu hồ sơ (kill giữa chừng không mất tin)\n    save_dossier(deps.state_dir, dos)\n",
     "    save_dossier(deps.state_dir, dos)\n    _save(deps, now.date(), st)\n"),
    ("bỏ chặn 1 nhắc/tick", "if reminded:                 #", "if False:                 #"),
]


def run_mutants():
    import subprocess
    res = []
    for name, old, new in MUTANTS:
        d = tempfile.mkdtemp(prefix="ipw_mut_")
        for f in ("intraday_cutloss_engine.py", "intraday_price_watch.py", "intraday_price_watch_selfcheck.py"):
            shutil.copy(os.path.join(HERE, f), d)
        pw = os.path.join(d, "intraday_price_watch.py")
        src = open(pw, encoding="utf-8").read()
        applied = src.count(old) == 1
        open(pw, "w", encoding="utf-8").write(src.replace(old, new))
        env = dict(os.environ, IPW_ONLY_HARDEN="1", IPW_MUTANT_RUN="1")
        r = subprocess.run([sys.executable, "-I", os.path.join(d, "intraday_price_watch_selfcheck.py")],
                           capture_output=True, text=True, env=env, timeout=600)
        shutil.rmtree(d)
        res.append((name, applied, r.returncode != 0))
    return res


def main():
    print("intraday_price_watch_selfcheck")
    os.fsync = lambda fd: None
    if os.environ.get("IPW_ONLY_HARDEN"):
        harden_tests()
    else:
        test_trigger()
        test_window_and_due()
        env = test_lifecycle()
        test_major_event_and_dead_jobs()
        test_retrigger_marketwide_atmostonce()
        test_eod_oos()
        test_no_sell_path(env)
        harden_tests()
        if not os.environ.get("IPW_MUTANT_RUN") and "--no-mutants" not in sys.argv:
            for name, applied, caught in run_mutants():
                check(f"mutant [{name}] áp được và BỊ BẮT", applied and caught, f"applied={applied} caught={caught}")
    total = N_PASS + len(FAILS)
    print(f"\n{N_PASS}/{total} PASS" + (f" — {len(FAILS)} FAIL" if FAILS else ""))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
