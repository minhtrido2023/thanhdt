#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho nav_loss_brake_monitor.py — KHÔNG chạm mạng/Discord/broker/BQ, không đọc ghi
dữ liệu thật (trừ MỘT ca chỉ-đọc data/trading_rules.json để khoá hợp đồng tên khoá ngưỡng).

Mọi ca dựng một cây `data/` giả trong thư mục tạm rồi gọi `main()` với --data-root/--state-dir/
--secrets/--now; cảnh báo đi vào file sink (MIKE_LOSS_BRAKE_ALERT_SINK).

Chạy (§16/§19 — cả ba, khác biệt giữa chúng CHÍNH LÀ phát hiện):
    env -u TZ python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
    TZ=America/Los_Angeles python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/nav_loss_brake_monitor_selfcheck.py
"""
import contextlib
import datetime
import io
import json
import os
import shutil
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

import nav_loss_brake_monitor as m  # noqa: E402

PASS = FAIL = 0
TRIGGER = "cumulative NAV drawdown since the recovery episode's entry point > -0.15 (-15%)"
NAV_FIELDS = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
              "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
# Phiên thật liên tiếp (T6 02/10 → T2 12/10/2026), không dính ngày lễ.
ALL_D = D0, D1, D2, D3, D4, D5, D6 = ("2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",
                                      "2026-10-08", "2026-10-09", "2026-10-12")


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")


class Fx:
    """Một cây data/ giả. Mọi thứ ghi ra đĩa NGAY khi gọi."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="lossbrake_sc_")
        self.data = os.path.join(self.root, "data")
        self.exec = os.path.join(self.data, "execution_logs")
        self.state = os.path.join(self.data, "loss_brake")
        self.secrets = os.path.join(self.root, "secrets.json")
        self.sink = os.path.join(self.root, "sink.jsonl")
        for d in (self.exec, self.state, os.path.join(self.data, "margin_approvals"),
                  os.path.join(self.data, "corp_action_daily")):
            os.makedirs(d)
        self.acc, self.navs, self.incep = [], {}, {}
        self.cash, self.sleeve = {}, {}
        self.nos, self.auto_pos, self.pos_written = {}, True, set()
        self.rules()
        self._j(os.path.join(self.state, "episodes.json"), {"episodes": []})
        for d in ALL_D:               # mặc định: lịch corp-action mọi phiên đọc được, không sự kiện
            self.corp(d, [])

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)

    @staticmethod
    def _j(path, obj):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)

    def rules(self, daily=-0.05, trigger=TRIGGER, pkg=1840, drop=None, numeric=None):
        r = {"risk_circuit_breakers": {"daily_loss_limit_pct": daily},
             "macro_kill_switches": {"C_episode_drawdown_breaker": {"trigger": trigger}},
             "capit_margin_lever": {"loan_package_id": pkg}}
        if numeric is not None:
            r["macro_kill_switches"]["C_episode_drawdown_breaker"][m.EPISODE_NUMERIC_KEY] = numeric
        if drop == "daily":
            del r["risk_circuit_breakers"]["daily_loss_limit_pct"]
        self._j(os.path.join(self.data, "trading_rules.json"), r)

    def account(self, label, no, excluded=(), capital=100e6, inception=D0):
        self.acc.append({"label": label, "account_id": no, "excluded_tickers": list(excluded)})
        self._j(self.secrets, {"accounts": self.acc})
        self.incep[label] = {"inception_date": inception, "starting_capital": capital}
        self._j(os.path.join(self.data, "account_inception.json"), dict(self.incep, _doc="x"))
        self.navs[label] = {}
        self.nos[label] = no
        self.flows(label, [])
        self.flows(label, [], sleeve=True)

    def nav(self, label, date, nav, est=False, ts="19:10:00"):
        """`ts`: giờ chụp trong chính ngày đó ("HH:MM:SS") hoặc dấu thời gian đầy đủ ("…T…").
        Mặc định kèm một bản ghi positions cuối phiên KHÔNG có vị thế gói vay / mã loại trừ."""
        self.navs[label][date] = (nav, est, ts)
        if self.auto_pos and (self.nos[label], date) not in self.pos_written:
            self.positions(self.nos[label], date, [("AAA", 100, 1841)])
        path = os.path.join(self.exec, f"nav_history_{label}.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(",".join(NAV_FIELDS) + "\n")
            for d in sorted(self.navs[label]):
                n, e, t = self.navs[label][d]
                bts = t if "T" in t else f"{d}T{t}"
                f.write(f"{d},{n:.0f},0,{n:.0f},0,0,0,{bts},0,{'True' if e else 'False'},x\n")

    def navs_seq(self, label, pairs):
        for d, n in pairs:
            self.nav(label, d, n)

    def positions(self, no, date, items, ts="19:07:00"):
        """items: [(symbol, qty, loanPackageId)] — THÊM một bản ghi positions gắn account `no`."""
        self.pos_written.add((no, date))
        rec = {"ts": f"{date}T{ts}", "kind": "positions", "account_no": no,
               "payload": {"positions": [{"symbol": s, "openQuantity": q, "loanPackageId": p,
                                          "accountNo": no} for s, q, p in items]}}
        with open(os.path.join(self.exec, f"dnse_raw_{date}.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def active_nav(self, label, date, items, total_nav=None):
        """items: [(ticker, qty, price)] (mã loại trừ). total_nav mặc định = NAV cùng ngày."""
        if total_nav is None:
            total_nav = self.navs[label][date][0]
        self._j(os.path.join(self.exec, f"active_nav_{label}.json"),
                {"account": label, "computed_at": date, "total_nav": total_nav,
                 "positions": [{"ticker": t, "qty": q, "price": p, "excluded": True,
                                "price_source": "fixture"} for t, q, p in items]})

    def excl_seed(self, label, rows):
        """rows: [(date, {ticker: (qty, price)})] — ghi thẳng chuỗi mã loại trừ (ngày đã qua)."""
        out = []
        for d, det in rows:
            detail = {t: {"qty": q, "price": p} for t, (q, p) in det.items()}
            out.append({"date": d, "excluded_value": f"{sum(q * p for q, p in det.values()):.0f}",
                        "detail": json.dumps(detail, sort_keys=True), "source": "fixture",
                        "positions_ts": "", "recorded_at": "fixture"})
        m._append_excluded(os.path.join(self.state, f"excluded_value_history_{label}.csv"), out)

    def flows(self, label, recs, sleeve=False):
        store = self.sleeve if sleeve else self.cash
        store[label] = recs
        path = (os.path.join(self.state, "managed_sleeve_flows.json") if sleeve
                else os.path.join(self.data, "account_cash_flows.json"))
        self._j(path, store)

    def approval(self, label, date, revoked=None, account=None):
        rec = {"account": account or label, "plan_date": date, "approved_by": "user (fixture)"}
        if revoked is not None:
            rec["revoked"] = revoked
        self._j(os.path.join(self.data, "margin_approvals",
                             f"margin_approval_{label}_{date}.json"), rec)

    def corp(self, date, events, usable=True):
        path = os.path.join(self.data, "corp_action_daily", f"corp_action_daily_{date}.json")
        if events is None:                                   # None = không có snapshot phiên đó
            if os.path.exists(path):
                os.remove(path)
            return
        self._j(path, {"asof": date, "status": "OK", "usable": usable,
                       "upcoming_events_held": events})

    def cli(self, now, *extra):
        """Gọi main() với cờ tuỳ ý (đóng/mở episode, đính chính…). Trả (rc, output)."""
        os.environ[m.SINK_ENV] = self.sink
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(self.args(now) + list(extra))
        return rc, buf.getvalue()

    def episodes(self):
        with open(os.path.join(self.state, "episodes.json"), encoding="utf-8") as f:
            return json.load(f)["episodes"]

    def args(self, now):
        return ["--data-root", self.data, "--state-dir", self.state, "--secrets", self.secrets,
                "--now", now]

    def run(self, date, extra=(), sink=True, now=None):
        """Chạy monitor tối ngày `date` (22:00 ICT). Trả (rc, stdout+stderr, status dict)."""
        if sink:
            os.environ[m.SINK_ENV] = self.sink
        else:
            os.environ.pop(m.SINK_ENV, None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(self.args(now or f"{date}T22:00:00") + list(extra))
        st = None
        p = os.path.join(self.state, "status.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
        return rc, buf.getvalue(), st

    def health(self, label, now):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(self.args(now) + ["--health-line", "--account", label])
        return rc, buf.getvalue().strip()

    def msgs(self):
        if not os.path.exists(self.sink):
            return []
        with open(self.sink, encoding="utf-8") as f:
            return [json.loads(x)["text"] for x in f if x.strip()]


def brakes(st, label):
    return {b: st["accounts"][label]["brakes"][b]["status"] for b in m.BRAKES}


# ---------------------------------------------------------------------------------- các ca
def t_thresholds():
    print("[A] ngưỡng đọc từ trading_rules.json — không mặc định ngầm")
    real = os.path.join(m.WC_ROOT, "data", "trading_rules.json")
    th, err = m.load_thresholds(real)
    check("A1 file THẬT: daily = -0.05", th["daily"] == -0.05, f"{th} {err}")
    check("A2 file THẬT: episode = -0.15", th["episode"] == -0.15, f"{th} {err}")
    check("A3 file THẬT: gói vay là số nguyên", isinstance(th["lever_package_id"], int), f"{th}")
    check("A4 file THẬT: không lỗi ngưỡng", err == {}, f"{err}")
    check("A5 DD_THRESHOLD = 0.25 (risk_monitor.py:46)", m.DD_THRESHOLD == 0.25)
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 90e6)])
        fx.rules(drop="daily")
        rc, out, st = fx.run(D2)
        b = st["accounts"]["A"]["brakes"]
        check("A6 thiếu khoá daily ⇒ daily KHÔNG ĐO ĐƯỢC (dù NAV −10%)",
              b["daily"]["status"] == m.UNMEASURABLE, f"{b['daily']}")
        check("A7 lý do nêu đúng tên khoá", "daily_loss_limit_pct" in (b["daily"]["reason"] or ""))
        check("A8 thiếu khoá ⇒ in ❌ + rc≠0 + có gửi cảnh báo",
              "THIẾU NGƯỠNG" in out and rc == 1 and len(fx.msgs()) == 1, f"rc={rc} {out[:200]}")
        check("A9 phanh khác vẫn đo", b["drawdown"]["status"] == m.OK, f"{b['drawdown']}")
        fx.rules(trigger="drawdown > -0.15 or maybe -0.12")
        th, err = m.load_thresholds(os.path.join(fx.data, "trading_rules.json"))
        check("A10 trigger chứa 2 ngưỡng ⇒ từ chối đoán", "episode" in err and th["episode"] is None)
        fx.rules(daily=True)
        th, err = m.load_thresholds(os.path.join(fx.data, "trading_rules.json"))
        check("A11 daily kiểu bool ⇒ lỗi", "daily" in err)
    finally:
        fx.close()


def t_daily_edges():
    print("[B] lỗ một ngày — đúng biên / ngay trong biên")
    for name, nav, want in (("B1 đúng −5,00% ⇒ BREACH", 95_000_000, m.BREACH),
                            ("B2 −4,999999% ⇒ OK", 95_000_001, m.OK),
                            ("B3 −5,000001% ⇒ BREACH", 94_999_999, m.BREACH)):
        fx = Fx()
        try:
            fx.account("A", "111")
            fx.navs_seq("A", [(D1, 100e6), (D2, nav)])
            rc, out, st = fx.run(D2)
            check(name, brakes(st, "A")["daily"] == want, f"{st['accounts']['A']['brakes']['daily']}")
            check(name + " · rc/tin nhắn khớp", (rc == 1 and len(fx.msgs()) == 1) if want == m.BREACH
                  else (rc == 0 and fx.msgs() == []), f"rc={rc} msgs={len(fx.msgs())}")
            check(name + " · KHÔNG tạo BOT_STOP",
                  not os.path.exists(os.path.join(fx.data, "BOT_STOP")))
            if want == m.BREACH:
                check(name + " · tin in sẵn lệnh BOT_STOP cho người",
                      "touch " in fx.msgs()[0] and "BOT_STOP" in fx.msgs()[0])
        finally:
            fx.close()


def t_float_edge():
    print("[B4] đúng −5% nhưng phép chia dấu phẩy động cho −0,04999999999999993")
    fx = Fx()
    try:
        fx.account("A", "111", capital=300e6)
        fx.navs_seq("A", [(D1, 101e6), (D2, 95.95e6)])       # 95,95 = 101 × 0,95 CHÍNH XÁC
        rc, out, st = fx.run(D2)
        d = st["accounts"]["A"]["brakes"]["daily"]
        check("B4a ca này thật sự rơi phía trên ngưỡng nếu so trần", d["value"] > -0.05, f"{d}")
        check("B4b vẫn BREACH nhờ EPS", d["status"] == m.BREACH, f"{d}")
    finally:
        fx.close()


def t_dd_edges():
    print("[C] lỗ từ đỉnh — đúng biên / ngay trong biên")
    path = [(D1, 110e6), (D2, 106e6), (D3, 102e6), (D4, 98e6), (D5, 94e6)]
    for name, nav, want in (("C1 đúng −25,00% ⇒ BREACH", 82_500_000, m.BREACH),
                            ("C2 −24,999999% ⇒ OK", 82_500_001, m.OK)):
        fx = Fx()
        try:
            fx.account("A", "111")
            # đỉnh 110tr ở D1, đi xuống dần; D6 chốt nav
            fx.navs_seq("A", path + [(D6, nav)])
            rc, out, st = fx.run(D6)
            d = st["accounts"]["A"]["brakes"]["drawdown"]
            check(name, d["status"] == want, f"{d}")
            check(name + " · đỉnh đúng ngày", d["peak_date"] == D1, f"{d}")
        finally:
            fx.close()
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 90e6), (D2, 89e6)])
        rc, out, st = fx.run(D2)
        d = st["accounts"]["A"]["brakes"]["drawdown"]
        check("C3 đỉnh = mốc khởi điểm (giá 10.000) khi NAV chưa từng vượt vốn",
              d["peak_date"] == D0 and abs(d["value"] - (-0.11)) < 1e-9, f"{d}")
    finally:
        fx.close()


def _episode_fx(last_nav, approval=True, lever=True, revoked=None):
    fx = Fx()
    fx.account("L", "111")
    fx.navs_seq("L", [(D1, 100e6), (D2, 96e6), (D3, 92e6), (D4, 88.5e6), (D5, last_nav)])
    for d in (D1, D2, D3, D4, D5):
        fx.positions("111", d, [("AAA", 100, 1841)] + ([("BBB", 500, 1840)] if lever and d >= D2
                                                       else []))
    if approval:
        fx.approval("L", D2, revoked=revoked)
    return fx


def t_episode():
    print("[D] phanh −15% theo episode — mở/đóng, đúng biên")
    fx = _episode_fx(85_000_000)
    try:
        rc, out, st = fx.run(D5)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("D1 đúng −15,00% từ điểm vào ⇒ BREACH", e["status"] == m.BREACH, f"{e}")
        check("D2 điểm vào = chốt phiên TRƯỚC ngày mở", e.get("entry_ref_date") == D1, f"{e}")
        check("D3 các phanh khác không kêu (chỉ episode)",
              brakes(st, "L")["daily"] == m.OK and brakes(st, "L")["drawdown"] == m.OK,
              f"{brakes(st, 'L')}")
        eps = json.load(open(os.path.join(fx.state, "episodes.json"), encoding="utf-8"))["episodes"]
        check("D4 episode được GHI với bằng chứng", len(eps) == 1 and eps[0]["opened_date"] == D2
              and eps[0]["evidence"]["lever_positions"] == {"BBB": 500.0}, f"{eps}")
        rc2, _, _ = fx.run(D5)
        eps2 = json.load(open(os.path.join(fx.state, "episodes.json"), encoding="utf-8"))["episodes"]
        check("D5 chạy lại không mở trùng episode", len(eps2) == 1)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(fx.args(f"{D5}T22:30:00") + ["--close-episode", "L"])
        check("D6 đóng thiếu người/lý do ⇒ từ chối", rc == 2)
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(fx.args(f"{D5}T22:30:00") + ["--close-episode", "L", "--closed-by",
                                                     "user (fixture)", "--reason", "đã tất toán"])
        check("D7 đóng bằng cờ tay rc=0", rc == 0)
        fx.nav("L", D6, 80e6 * 1.06)          # +ngày mới, vẫn dưới −15% so với điểm vào cũ
        fx.positions("111", D6, [("AAA", 100, 1841)])
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("D8 sau khi đóng ⇒ 'không có episode', nói rõ chứ không im",
              e["status"] == m.NO_EPISODE and "không có episode" in e["reason"], f"{e}")
        eps3 = json.load(open(os.path.join(fx.state, "episodes.json"), encoding="utf-8"))["episodes"]
        check("D9 bản duyệt cũ không mở lại episode đã đóng", len(eps3) == 1)
    finally:
        fx.close()
    fx = _episode_fx(85_000_001)
    try:
        rc, out, st = fx.run(D5)
        check("D10 −14,999999% ⇒ OK", brakes(st, "L")["episode"] == m.OK and rc == 0,
              f"{st['accounts']['L']['brakes']['episode']}")
    finally:
        fx.close()
    fx = _episode_fx(85_000_000, lever=False)
    try:
        rc, out, st = fx.run(D5)
        a = st["accounts"]["L"]
        check("D11 có bản duyệt nhưng KHÔNG có vị thế gói vay ⇒ không mở (§27: ý định ≠ khớp)",
              a["brakes"]["episode"]["status"] == m.NO_EPISODE, f"{a['brakes']['episode']}")
        check("D12 ...và ghi chú nói rõ", any("ý định" in n for n in a["notes"]), f"{a['notes']}")
    finally:
        fx.close()
    fx = _episode_fx(85_000_000, approval=False)
    try:
        rc, out, st = fx.run(D5)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("D13 có vị thế gói vay mà KHÔNG có bản duyệt/episode ⇒ KHÔNG ĐO ĐƯỢC (kêu)",
              e["status"] == m.UNMEASURABLE and "1840" in e["reason"] and rc == 1, f"{e}")
    finally:
        fx.close()
    fx = _episode_fx(85_000_000, revoked=True)
    try:
        rc, out, st = fx.run(D5)
        eps = json.load(open(os.path.join(fx.state, "episodes.json"), encoding="utf-8"))["episodes"]
        check("D14 bản duyệt đã thu hồi ⇒ không mở episode", eps == [], f"{eps}")
    finally:
        fx.close()


def t_flows():
    print("[E] nạp/rút không thành lãi/lỗ giả")
    dep = {"date": D2, "time_ict": "10:00", "amount_vnd": 100e6, "kind": "deposit",
           "evidence": "fixture"}
    wd = {"date": D3, "time_ict": "10:00", "amount_vnd": -150e6, "kind": "withdraw",
          "evidence": "fixture"}
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 200e6), (D3, 50e6)])
        fx.flows("A", [dep, wd])
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]
        check("E1 rút 150tr (NAV 200→50) có khai ⇒ ngày 0%, không kêu",
              b["daily"]["status"] == m.OK and abs(b["daily"]["value"]) < 1e-9 and rc == 0,
              f"{b['daily']}")
        check("E2 nạp không đẩy đỉnh lên ⇒ từ đỉnh 0%",
              b["drawdown"]["status"] == m.OK and abs(b["drawdown"]["value"]) < 1e-9,
              f"{b['drawdown']}")
        fx.flows("A", [dep])                       # ĐỐI CHỨNG: bỏ khai lần rút
        rc, out, st = fx.run(D3)
        check("E3 đối chứng: KHÔNG khai lần rút ⇒ kêu (ca E1 có răng)",
              brakes(st, "A")["daily"] == m.BREACH and brakes(st, "A")["drawdown"] == m.BREACH,
              f"{brakes(st, 'A')}")
        os.remove(os.path.join(fx.data, "account_cash_flows.json"))
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]
        check("E4 MẤT sổ dòng tiền ⇒ KHÔNG ĐO ĐƯỢC (không coi như 'không có dòng tiền')",
              all(b[x]["status"] == m.UNMEASURABLE for x in m.BRAKES)
              and "account_cash_flows.json" in b["daily"]["reason"], f"{b['daily']}")
        # dòng tiền khai SAU lần chụp NAV cuối cùng ⇒ chưa dòng nào chứa nó (treo)
        fx.flows("A", [dep, wd, {"date": D3, "time_ict": "23:00", "amount_vnd": 5e6,
                                 "kind": "deposit", "evidence": "fixture"}])
        rc, out, st = fx.run(D3, now=f"{D3}T23:30:00")
        b = st["accounts"]["A"]["brakes"]
        check("E5 dòng tiền TREO (chưa dòng NAV nào chụp sau nó) ⇒ KHÔNG ĐO ĐƯỢC",
              b["daily"]["status"] == m.UNMEASURABLE and "TREO" in b["daily"]["reason"],
              f"{b['daily']}")
    finally:
        fx.close()


def t_fail_loud():
    print("[F/G/P] NAV ước tính · thiếu ngày · thiếu phiên liền trước")
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 99e6)])
        fx.nav("A", D3, 98e6, est=True)
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]
        check("F1 dòng nav_is_estimate ⇒ daily + drawdown KHÔNG ĐO ĐƯỢC",
              b["daily"]["status"] == m.UNMEASURABLE and b["drawdown"]["status"] == m.UNMEASURABLE,
              f"{brakes(st, 'A')}")
        check("F2 vẫn cho số tạm tính + lý do đọc từ cờ",
              b["daily"]["value"] is not None and "nav_is_estimate" in b["daily"]["reason"])
        check("F3 có gửi cảnh báo (không đo được ≠ an toàn)",
              rc == 1 and len(fx.msgs()) == 1 and "KHÔNG ĐO ĐƯỢC" in fx.msgs()[0])
        fx.nav("A", D4, 97e6)
        rc, out, st = fx.run(D4)
        b = st["accounts"]["A"]["brakes"]
        check("F4 hôm sau: mốc so là dòng ước tính ⇒ daily KHÔNG ĐO ĐƯỢC, drawdown đo được",
              b["daily"]["status"] == m.UNMEASURABLE and b["drawdown"]["status"] == m.OK,
              f"{brakes(st, 'A')}")
        # --- thiếu dòng của chính phiên phải có
        rc, out, st = fx.run(D5)
        b = st["accounts"]["A"]["brakes"]
        check("G1 thiếu dòng NAV phiên D ⇒ cả 3 phanh KHÔNG ĐO ĐƯỢC + rc=1",
              all(b[x]["status"] == m.UNMEASURABLE for x in m.BRAKES) and rc == 1, f"{brakes(st, 'A')}")
        check("G2 lý do nêu ngày thiếu + dòng mới nhất", D5 in b["daily"]["reason"]
              and D4 in b["daily"]["reason"], b["daily"]["reason"])
        fx._j(os.path.join(fx.exec, f"nav_gate_block_A_{D5}.json"),
              {"account": "A", "date": D5, "gate_verdict": "qty_change_block", "rc": 5})
        rc, out, st = fx.run(D5)
        r = st["accounts"]["A"]["brakes"]["daily"]["reason"]
        check("G3 có file chặn ⇒ lý do trích gate_verdict + rc ĐỌC ĐƯỢC (§29)",
              "qty_change_block" in r and "rc=5" in r, r)
        # --- có dòng D nhưng thiếu phiên liền trước
        fx.nav("A", D6, 96e6)
        rc, out, st = fx.run(D6)
        b = st["accounts"]["A"]["brakes"]
        check("P1 thiếu dòng phiên liền trước ⇒ daily KHÔNG ĐO ĐƯỢC (số gộp nhiều phiên)",
              b["daily"]["status"] == m.UNMEASURABLE and D5 in b["daily"]["reason"], f"{b['daily']}")
        check("P2 ...drawdown vẫn đo", b["drawdown"]["status"] == m.OK, f"{b['drawdown']}")
        fx.nav("A", D6, 80e6)
        rc, out, st = fx.run(D6)
        b = st["accounts"]["A"]["brakes"]["daily"]
        check("P3 số gộp nhiều phiên mà ĐÃ vượt ngưỡng ⇒ TẠM TÍNH VƯỢT NGƯỠNG, không còn là tin vàng",
              b["status"] == m.BREACH_PROV and D5 in b["reason"], f"{b}")
    finally:
        fx.close()
    # --- dòng ngày NGHỈ nằm giữa (2026-08-31 nghỉ lễ, nav_history thật vẫn có dòng)
    fx = Fx()
    try:
        fx.account("A", "111", inception="2026-08-27")
        fx.navs_seq("A", [("2026-08-28", 100e6), ("2026-08-31", 100.01e6), ("2026-09-03", 99e6)])
        rc, out, st = fx.run("2026-09-03")
        b = st["accounts"]["A"]["brakes"]["daily"]
        check("O1 dòng ngày nghỉ giữa hai phiên KHÔNG làm 'thiếu phiên liền trước'",
              b["status"] == m.OK and rc == 0, f"{b}")
        check("O2 mốc so = dòng của phiên liền trước (28/08), không phải dòng ngày nghỉ",
              abs(b["value"] - (99e6 / 100e6 - 1)) < 1e-12, f"{b}")
    finally:
        fx.close()


def _two_accounts():
    """S = account thường; Z = account có mã loại trừ XXX (10.000 cp)."""
    fx = Fx()
    fx.account("S", "111")
    fx.account("Z", "222", excluded=("XXX", "YYY"), capital=1000e6)
    fx.navs_seq("S", [(D1, 101e6), (D2, 100e6)])
    fx.navs_seq("Z", [(D1, 1000e6), (D2, 998e6)])
    fx.excl_seed("Z", [(D0, {"XXX": (10000, 46000)}), (D1, {"XXX": (10000, 46000)}),
                       (D2, {"XXX": (10000, 46750)})])
    return fx


def t_two_accounts_and_sleeve():
    print("[I/J/R/Q] hai account · phần bot quản lý · ca DGC 11/09 · chuỗi mã loại trừ")
    fx = _two_accounts()
    try:
        # D3: XXX GDKHQ cổ tức 8.000đ ⇒ giá 46.750 → 37.400. NAV tổng hụt GIẢ 80tr + 13,5tr giảm
        # thật của XXX (khoản phải thu chưa được ghi vào tiền) = −9,4%; phần quản lý KHÔNG đổi.
        fx.nav("S", D3, 99.5e6)
        fx.nav("Z", D3, 998e6 - 93.5e6)
        for d in (D3,):
            # cùng MỘT file raw chứa cả hai account; account 111 cũng "giữ XXX" để bắt lỗi lọc §12
            # ...và bản ghi của account KIA nằm SAU CÙNG trong file (bỏ lọc là lấy nhầm ngay)
            fx.positions("222", d, [("XXX", 10000, 1841), ("AAA", 50, 1841)])
            fx.positions("111", d, [("XXX", 777, 1841)], ts="23:30:00")
        fx.active_nav("Z", D3, [("XXX", 10000, 37400)])
        rc, out, st = fx.run(D3)
        s, z = st["accounts"]["S"], st["accounts"]["Z"]
        check("I1 S đo trên NAV toàn tài khoản, Z đo trên phần bot quản lý",
              s["basis"] == "total" and z["basis"] == "managed", f"{s['basis']} {z['basis']}")
        check("I2 hai account cho hai kết quả KHÁC nhau (§12)",
              s["unit_price"] != z["unit_price"] and s["overall"] != z["overall"],
              f"{s['overall']} {z['overall']}")
        check("I3 Z: giá trị mã loại trừ lấy ĐÚNG account (10.000 cp, không dính 777 của account kia)",
              z["excluded_value"] == 374_000_000 and z["excluded_detail"]["XXX"]["qty"] == 10000,
              f"{z['excluded_value']} {z['excluded_detail']}")
        check("I4 Z: NAV tổng hụt −9,37% (giả) chỉ HIỂN THỊ",
              abs(z["total_nav_info"]["daily"] - (-93.5 / 998)) < 1e-9, f"{z['total_nav_info']}")
        check("I5 Z: KHÔNG có phanh nào BREACH vì cú hụt giả của mã loại trừ",
              m.BREACH not in brakes(st, "Z").values(), f"{brakes(st, 'Z')}")
        r = z["brakes"]["daily"]["reason"] or ""
        check("I6 Z: nhưng cũng KHÔNG coi là an toàn — bẫy giá nhảy quá biên độ ⇒ KHÔNG ĐO ĐƯỢC",
              z["overall"] == m.UNMEASURABLE and "XXX" in r and "biên độ" in r, r)
        check("I7 S không bị ảnh hưởng: OK", s["overall"] == m.OK, f"{brakes(st, 'S')}")
        check("I8 chỉ Z có tin cảnh báo", len(fx.msgs()) == 1 and "— Z ·" in fx.msgs()[0],
              f"{fx.msgs()}")
        check("I9 tin của Z ghi rõ NAV tổng chỉ để tham chiếu",
              "KHÔNG kích phanh" in fx.msgs()[0] and "phần bot quản lý" in fx.msgs()[0])
        # người kiểm xong, khai: ngày D3 chưa có tiền nào sang phần quản lý
        fx.flows("Z", [{"date": D3, "amount_vnd": 0, "kind": "market_only",
                        "evidence": "fixture: GDKHQ, tiền chưa về"}], sleeve=True)
        rc, out, st = fx.run(D3)
        z = st["accounts"]["Z"]
        check("I10 sau khi KHAI ⇒ đo được, phần quản lý ngày 0% ⇒ OK",
              z["overall"] == m.OK and abs(z["brakes"]["daily"]["value"]) < 1e-9, f"{z['brakes']}")
        # D4: khoản phải thu 80tr được ghi vào tiền ⇒ NAV tổng +80tr = tiền VÀO phần quản lý
        fx.nav("S", D4, 99.5e6)
        fx.nav("Z", D4, 998e6 - 93.5e6 + 80e6)
        fx.positions("222", D4, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D4, [("XXX", 10000, 37400)])
        fx.flows("Z", [{"date": D3, "amount_vnd": 0, "kind": "market_only", "evidence": "x"},
                       {"date": D4, "time_ict": "09:00", "amount_vnd": 80e6, "kind": "deposit",
                        "evidence": "fixture: cổ tức XXX 8.000đ × 10.000"}], sleeve=True)
        rc, out, st = fx.run(D4)
        z = st["accounts"]["Z"]
        check("I11 cổ tức mã loại trừ có khai ⇒ KHÔNG thành lãi giả (ngày 0%, đỉnh không bị đẩy)",
              abs(z["brakes"]["daily"]["value"]) < 1e-9
              and z["brakes"]["drawdown"]["peak_date"] != D4, f"{z['brakes']}")
        # --- J: KL mã loại trừ đổi (bán 4.000 cp) mà chưa khai
        fx.nav("S", D5, 99.5e6)
        fx.nav("Z", D5, 998e6 - 93.5e6 + 80e6)
        fx.positions("222", D5, [("XXX", 6000, 1841)])
        fx.active_nav("Z", D5, [("XXX", 6000, 37400)])
        rc, out, st = fx.run(D5)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("J1 KL mã loại trừ đổi mà chưa khai ⇒ KHÔNG ĐO ĐƯỢC, nêu 10.000 → 6.000",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "10.000 → 6.000" in r, r)
        # --- R: chuỗi chỉ-ghi-thêm
        before = open(os.path.join(fx.state, "excluded_value_history_Z.csv"), encoding="utf-8").read()
        fx.active_nav("Z", D5, [("XXX", 6000, 99999)])      # giá khác hẳn — không được ghi đè
        fx.run(D5)
        after = open(os.path.join(fx.state, "excluded_value_history_Z.csv"), encoding="utf-8").read()
        check("R1 dòng đã ghi không bị ghi đè khi chạy lại", before == after)
        hist = os.path.join(fx.state, "excluded_value_history_Z.csv")
        m._append_excluded(hist, [{"date": D5, "excluded_value": "1", "detail": "{}",
                                   "source": "ghi đè?", "positions_ts": "", "recorded_at": "x"}])
        check("R1b _append_excluded tự nó cũng từ chối ghi đè dòng đã có",
              open(hist, encoding="utf-8").read() == before)
        # --- R: active_nav không đúng ngày ⇒ không lấy giá cũ
        fx.nav("Z", D6, 990e6)
        fx.nav("S", D6, 99.5e6)
        fx.positions("222", D6, [("XXX", 6000, 1841)])
        rc, out, st = fx.run(D6)                            # active_nav vẫn là của D5
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("R2 đang giữ mã loại trừ mà active_nav là của ngày khác ⇒ KHÔNG ĐO ĐƯỢC, nêu ngày",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and D5 in r and "computed_at" in r, r)
        fx.active_nav("Z", D6, [("XXX", 5000, 37400)])
        rc, out, st = fx.run(D6)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("R3 KL lệch giữa dnse_raw và active_nav ⇒ KHÔNG ĐO ĐƯỢC", "KL XXX lệch" in r, r)
        # ca DGC 11/09 dạng hai file định giá khác nhau: active_nav cao hơn nav_history 8%
        fx.active_nav("Z", D6, [("XXX", 6000, 37400)], total_nav=990e6 * 1.08)
        rc, out, st = fx.run(D6)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("R4 active_nav.total_nav lệch nav_history 8% ⇒ KHÔNG ĐO ĐƯỢC, không trừ giá khác hệ",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "định giá khác nhau" in r, r)
        fx.active_nav("Z", D6, [("XXX", 6000, 37400)], total_nav=990e6 * 1.0005)
        fx.flows("Z", fx.sleeve["Z"] + [{"date": D5, "amount_vnd": 0, "kind": "market_only",
                                         "evidence": "fixture"}], sleeve=True)
        rc, out, st = fx.run(D6)
        check("R5 lệch 0,05% (trong dung sai) ⇒ ghi được và đo được",
              st["accounts"]["Z"]["brakes"]["daily"]["status"] in (m.OK, m.BREACH),
              f"{st['accounts']['Z']['brakes']['daily']}")
    finally:
        fx.close()
    # --- Q: có excluded_tickers mà chưa có chuỗi ⇒ không âm thầm đo trên NAV tổng
    fx = Fx()
    try:
        fx.auto_pos = False
        fx.account("Z", "222", excluded=("XXX",))
        fx.navs_seq("Z", [(D1, 100e6), (D2, 99e6)])
        rc, out, st = fx.run(D2)                            # không có dnse_raw ⇒ không ghi được
        z = st["accounts"]["Z"]
        check("Q1 chưa có chuỗi mã loại trừ ⇒ KHÔNG ĐO ĐƯỢC (không rơi về NAV tổng), nêu đúng lý do",
              z["basis"] == "managed" and z["overall"] == m.UNMEASURABLE
              and "chưa có chuỗi" in z["brakes"]["daily"]["reason"], f"{z['brakes']['daily']}")
        fx.positions("222", D1, [("AAA", 5, 1841)])
        fx.positions("222", D2, [("AAA", 5, 1841)])
        fx.corp(D1, None)                                    # không giữ mã loại trừ ⇒ không cần lịch
        fx.corp(D2, None)
        rc, out, st = fx.run(D2)
        z = st["accounts"]["Z"]
        check("Q2 không giữ mã loại trừ nào ⇒ tự ghi 0 (không cần giá), lỗ một ngày đo được",
              z["brakes"]["daily"]["status"] == m.OK and z["excluded_value"] == 0,
              f"{z['brakes']['daily']}")
        check("Q3 ...có cảnh báo chuỗi bắt đầu muộn hơn mốc khởi điểm",
              any("chỉ bắt đầu từ" in w for w in z["warnings"]), f"{z['warnings']}")
        dd = z["brakes"]["drawdown"]
        check("Q4 chuỗi bắt đầu MUỘN hơn mốc khởi điểm ⇒ lỗ từ đỉnh KHÔNG ĐO ĐƯỢC (đỉnh cũ nằm "
              "ngoài chuỗi), không âm thầm đặt lại đỉnh",
              dd["status"] == m.UNMEASURABLE and "chỉ bắt đầu từ" in dd["reason"]
              and z["overall"] == m.UNMEASURABLE and rc == 1, f"{dd}")
        rc, line = fx.health("Z", f"{D3}T08:20:00")
        check("Q5 ...và dòng ops_health buổi sáng cũng nói ra (rc=1)",
              rc == 1 and "chỉ bắt đầu từ" in line, line)
        fx.excl_seed("Z", [(D0, {})])                       # vá mốc khởi điểm (không giữ mã nào)
        rc, out, st = fx.run(D2)
        check("Q6 vá xong dòng mốc khởi điểm ⇒ lỗ từ đỉnh đo được, đỉnh = mốc khởi điểm",
              st["accounts"]["Z"]["overall"] == m.OK
              and st["accounts"]["Z"]["brakes"]["drawdown"]["peak_date"] == D0, f"{st['accounts']['Z']['brakes']}")
    finally:
        fx.close()
    # --- lịch corp-action: cổ tức NHỎ (trong biên độ) vẫn bị bắt
    fx = _two_accounts()
    try:
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, 998e6)
        fx.positions("222", D3, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D3, [("XXX", 10000, 45750)])      # −2,1%: trong biên độ
        fx.corp(D3, [{"ticker": "XXX", "date": D3, "event_code": "DIV", "value_per_share": "1000.0",
                      "title": "Cổ tức tiền 1.000đ"},
                     {"ticker": "AAA", "date": D3, "event_code": "DIV", "value_per_share": "500"}])
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("T1 lịch corp-action có sự kiện mã loại trừ đúng ngày ⇒ KHÔNG ĐO ĐƯỢC + số tiền gợi ý",
              "lịch corp-action" in r and "10.000.000đ" in r, r)
        check("T2 sự kiện của mã KHÔNG loại trừ không gây bẫy", "AAA" not in r, r)
    finally:
        fx.close()
    fx = _two_accounts()
    try:
        fx.nav("Z", D4, 998e6)                                # bỏ qua D3: hai dòng cách 2 phiên
        fx.nav("S", D4, 100e6)
        fx.positions("222", D4, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D4, [("XXX", 10000, 46750 * 1.14)])   # +14% qua 2 phiên: trong biên
        rc, out, st = fx.run(D4)
        r = st["accounts"]["Z"]["brakes"]["drawdown"]
        check("T3 giá mã loại trừ +14% qua HAI phiên không bị coi là quá biên độ",
              r["status"] == m.OK, f"{r}")
    finally:
        fx.close()


def t_idempotent():
    print("[K/L] gửi trùng · đánh dấu ngay · gửi lỗi · file trạng thái")
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 70e6)])
        rc, out, st = fx.run(D2)
        check("K1 lần đầu: 1 tin", len(fx.msgs()) == 1 and st["accounts"]["A"]["alert"]["sent_now"])
        log = [json.loads(x) for x in read(os.path.join(fx.state, "run_log.jsonl")).splitlines()]
        check("K1b mỗi lượt chạy thật để lại MỘT dòng nhật ký (phiên, rc, account đã gửi)",
              len(log) == 1 and log[0]["session"] == D2 and log[0]["rc"] == 1
              and log[0]["sent"] == ["A"] and log[0]["accounts"] == {"A": m.BREACH}, f"{log}")
        sent = json.load(open(os.path.join(fx.state, "alerts_sent.json"), encoding="utf-8"))
        check("K2 dấu đã gửi nằm trên đĩa, đủ 2 phanh vi phạm",
              sorted(sent) == [f"A|{D2}|daily|BREACH", f"A|{D2}|drawdown|BREACH"], f"{sorted(sent)}")
        rc, out, st = fx.run(D2)
        check("K3 chạy lại cùng phiên: KHÔNG gửi trùng, rc vẫn 1",
              len(fx.msgs()) == 1 and rc == 1 and not st["accounts"]["A"]["alert"]["sent_now"])
        rc, out, st = fx.run(D2, now=f"{D3}T08:00:00")
        check("K4 chạy lại sáng hôm sau (cùng phiên D2): vẫn không gửi trùng", len(fx.msgs()) == 1)
        fx.nav("A", D3, 70e6)
        rc, out, st = fx.run(D3)
        check("K5 phiên sau còn vi phạm (từ đỉnh) ⇒ BÁO LẠI", len(fx.msgs()) == 2
              and brakes(st, "A") == {"daily": m.OK, "drawdown": m.BREACH, "episode": m.NO_EPISODE},
              f"{len(fx.msgs())} {brakes(st, 'A')}")
        check("L1 không sót file tạm", not [f for f in os.listdir(fx.state) if ".tmp" in f],
              f"{os.listdir(fx.state)}")
        check("L2 file trạng thái có đủ khoảng cách tới ngưỡng",
              abs(st["accounts"]["A"]["brakes"]["daily"]["distance_pp"] - 5.0) < 1e-6
              and st["session"] == D3 and st["schema"] == m.STATUS_SCHEMA,
              f"{st['accounts']['A']['brakes']['daily']}")
        # --- gửi lỗi: không sink + thư mục không phải mặc định ⇒ TỪ CHỐI gửi Discord thật
        fx.nav("A", D4, 60e6)
        rc, out, st = fx.run(D4, sink=False)
        a = st["accounts"]["A"]["alert"]
        check("K6 không sink + data-root giả ⇒ từ chối gửi thật, rc=3, in ❌",
              rc == 3 and a["send_error"] and "TỪ CHỐI" in a["send_error"] and "❌" in out,
              f"rc={rc} {a}")
        sent = json.load(open(os.path.join(fx.state, "alerts_sent.json"), encoding="utf-8"))
        check("K7 gửi lỗi ⇒ KHÔNG đánh dấu đã gửi", not any(D4 in k for k in sent), f"{sorted(sent)}")
        hrc, line = fx.health("A", f"{D5}T08:20:00")
        check("K7b gửi lỗi ⇒ dòng ops_health rc=3 + nêu GỬI CẢNH BÁO LỖI kèm lý do",
              hrc == 3 and "GỬI CẢNH BÁO LỖI" in line and "TỪ CHỐI" in line, f"{hrc} {line}")
        rc, out, st = fx.run(D4)
        check("K8 lượt sau gửi được ⇒ gửi bù đúng 1 tin", len(fx.msgs()) == 3 and rc == 1)
        # --- kill giữa chừng sau khi gửi, trước khi ghi status: dấu đã có ⇒ không gửi lại
        os.remove(os.path.join(fx.state, "status.json"))
        rc, out, st = fx.run(D4)
        check("K9 mất status.json nhưng dấu đã gửi còn ⇒ không gửi trùng", len(fx.msgs()) == 3)
    finally:
        fx.close()


def t_health_and_clock():
    print("[H/N] ops_health: file cũ · đồng hồ ICT")
    fx = Fx()
    try:
        fx.account("A", "111")
        rc, line = fx.health("A", f"{D3}T08:20:00")
        check("H1 chưa có file trạng thái ⇒ rc=2, nói rõ chưa từng chạy",
              rc == 2 and "CHƯA có" in line, line)
        fx.navs_seq("A", [(D1, 100e6), (D2, 99e6)])
        fx.run(D2)
        rc, line = fx.health("A", f"{D3}T08:20:00")
        check("H2 sáng hôm sau: file đúng phiên ⇒ rc=0, 1 dòng có khoảng cách tới ngưỡng",
              rc == 0 and "\n" not in line and "cách 4,00pp" in line and "không có episode" in line,
              line)
        rc, line = fx.health("A", f"{D4}T08:20:00")
        check("H3 monitor không chạy tối qua ⇒ file CŨ: rc=2, nêu phiên đang ghi + phiên phải có",
              rc == 2 and "CŨ" in line and D2 in line and D3 in line, line)
        rc, line = fx.health("B", f"{D3}T08:20:00")
        check("H4 account không có trong file ⇒ rc=2", rc == 2 and "không có account" in line, line)
        rc, line = fx.health("A", "2026-10-10T08:20:00")
        check("H5 thứ Bảy: phiên phải có là thứ Sáu 09/10 ⇒ file D2 là cũ", rc == 2 and D5 in line,
              line)
        fx.nav("A", D3, 90e6)
        fx.run(D3)
        rc, line = fx.health("A", f"{D4}T08:20:00")
        check("H6 phiên trước có vi phạm ⇒ dòng sáng rc=1 + nêu ĐÃ CHẠM", rc == 1 and "ĐÃ CHẠM" in line,
              line)
        with open(os.path.join(fx.state, "status.json"), "w", encoding="utf-8") as f:
            f.write('{"schema": 1, "session": ')
        rc, line = fx.health("A", f"{D4}T08:20:00")
        check("H7 file trạng thái cụt ⇒ rc=2, nêu không đọc được", rc == 2 and "không đọc được" in line,
              line)
    finally:
        fx.close()
    ict = m.ICT
    utc = datetime.timezone.utc
    es = m.expected_session
    check("N1 22:00 ICT thứ Hai ⇒ phiên hôm nay",
          es(datetime.datetime(2026, 10, 12, 22, 0, tzinfo=ict)) == datetime.date(2026, 10, 12))
    check("N2 21:49 ICT ⇒ còn là phiên trước (thứ Sáu)",
          es(datetime.datetime(2026, 10, 12, 21, 49, tzinfo=ict)) == datetime.date(2026, 10, 9))
    check("N3 15:00 UTC = 22:00 ICT ⇒ phiên hôm nay (không dùng ngày UTC)",
          es(datetime.datetime(2026, 10, 12, 15, 0, tzinfo=utc)) == datetime.date(2026, 10, 12))
    check("N4 17:30 UTC thứ Hai = 00:30 ICT thứ Ba ⇒ vẫn là phiên thứ Hai",
          es(datetime.datetime(2026, 10, 12, 17, 30, tzinfo=utc)) == datetime.date(2026, 10, 12))
    check("N5 chủ nhật ⇒ thứ Sáu",
          es(datetime.datetime(2026, 10, 11, 23, 0, tzinfo=ict)) == datetime.date(2026, 10, 9))
    check("N6 03/09 08:00 ⇒ 28/08 (31/08–02/09 nghỉ lễ)",
          es(datetime.datetime(2026, 9, 3, 8, 0, tzinfo=ict)) == datetime.date(2026, 8, 28))
    c = m.Ctx()
    check("N7 đồng hồ mặc định có múi giờ ICT tường minh",
          c.now.tzinfo is not None and c.now.utcoffset() == datetime.timedelta(hours=7))
    check("N8 Ctx mặc định = live; đổi state-dir ⇒ không còn live",
          c.is_live and not m.Ctx(state_dir=tempfile.gettempdir()).is_live)
    src = open(os.path.join(BIN, "nav_loss_brake_monitor.py"), encoding="utf-8").read()
    check("N9 mã nguồn không import broker/BQ",
          "DNSEBroker" not in src and "bigquery" not in src.lower() and "bq query" not in src)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def t_threshold_parsing():
    print("[A2] ngưỡng: kiểm khoảng · khoá số · ngưỡng dương")
    fx = Fx()
    try:
        rp = os.path.join(fx.data, "trading_rules.json")
        for name, trig in (("-0.5 (một chữ số)", "drawdown > -0.5"),
                           ("-0.015 (ba chữ số)", "drawdown > -0.015"),
                           ("1-0.15 (dính số khác)", "ratio 1-0.15 of entry"),
                           ("-0.45 (ngoài khoảng)", "drawdown > -0.45"),
                           ("-0.15 nhưng ghi (-20%)", "drawdown > -0.15 (-20%)")):
            fx.rules(trigger=trig)
            th, err = m.load_thresholds(rp)
            check(f"A12 trigger {name} ⇒ từ chối, không đoán", "episode" in err
                  and th["episode"] is None, f"{th} {err}")
        fx.rules(trigger="không có số nào", numeric=-0.12)
        th, err = m.load_thresholds(rp)
        check("A13 có khoá SỐ ⇒ dùng khoá số, không cần đọc chuỗi trigger",
              th["episode"] == -0.12 and "episode" not in err, f"{th} {err}")
        for bad in (0.15, -0.6, True, "-0.15"):
            fx.rules(numeric=bad)
            th, err = m.load_thresholds(rp)
            check(f"A14 khoá số {bad!r} ⇒ lỗi (không rơi về chuỗi trigger)",
                  "episode" in err and th["episode"] is None, f"{th} {err}")
        for bad in (0.05, 0, -1):
            fx.rules(daily=bad)
            th, err = m.load_thresholds(rp)
            check(f"A15 daily = {bad} (không âm thật sự / ngoài khoảng) ⇒ lỗi",
                  "daily" in err and th["daily"] is None, f"{th} {err}")
    finally:
        fx.close()


def t_close_capture():
    print("[B1] dòng NAV chụp ngoài cửa sổ giá chốt KHÔNG phải giá chốt")
    D = datetime.date.fromisoformat
    cp = m.close_capture_problem
    check("V1 14:45:00 đúng ngày ⇒ là giá chốt", cp(D(D2), f"{D2}T14:45:00") is None)
    check("V2 14:44:59 ⇒ trước giờ đóng cửa", "TRƯỚC giờ đóng cửa" in (cp(D(D2), f"{D2}T14:44:59") or ""))
    check("V3 08:59:59 sáng phiên kế ⇒ vẫn là giá chốt", cp(D(D2), f"{D3}T08:59:59") is None)
    check("V4 09:00:00 phiên kế ⇒ đã lẫn phiên sau", "SAU giờ mở cửa" in (cp(D(D2), f"{D3}T09:00:00") or ""))
    check("V5 thứ Sáu chụp sáng thứ Bảy / tối Chủ nhật ⇒ vẫn là giá chốt thứ Sáu",
          cp(D(D5), "2026-10-10T10:00:00") is None and cp(D(D5), "2026-10-11T23:00:00") is None)
    check("V6 thứ Sáu chụp 09:00 thứ Hai ⇒ không", cp(D(D5), f"{D6}T09:00:00") is not None)
    check("V7 thiếu balance_ts ⇒ nói rõ giá trị đọc được", "None" in (cp(D(D2), None) or "")
          and "'abc'" in (cp(D(D2), "abc") or ""))
    check("V8 có múi giờ: 07:45Z = 14:45 ICT ⇒ là giá chốt", cp(D(D2), f"{D2}T07:45:00+00:00") is None)
    check("V9 dòng ngày NGHỈ (31/08) chụp trong ngày ⇒ giá chốt của phiên 28/08",
          cp(D("2026-08-31"), "2026-08-31T19:10:00") is None)
    # ca của reviewer: D2 chụp 04:49 (= NAV chốt D1), phiên D2 thật −6%, D3 +2%
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6)])
        fx.nav("A", D2, 100e6, ts="04:49:59")
        rc, out, st = fx.run(D2)
        b = st["accounts"]["A"]["brakes"]
        check("V10 dòng D2 chụp 04:49 ⇒ lỗ một ngày KHÔNG ĐO ĐƯỢC, nêu giờ chụp (không báo 0,00% OK)",
              b["daily"]["status"] == m.UNMEASURABLE and "04:49:59" in b["daily"]["reason"]
              and rc == 1 and len(fx.msgs()) == 1, f"{b['daily']}")
        check("V11 ...lỗ từ đỉnh cũng vậy", b["drawdown"]["status"] == m.UNMEASURABLE
              and "04:49:59" in b["drawdown"]["reason"], f"{b['drawdown']}")
        fx.nav("A", D3, 100e6 * 0.94 * 1.02)
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]
        check("V12 hôm sau: MỐC SO là dòng chụp 04:49 ⇒ lỗ một ngày KHÔNG ĐO ĐƯỢC (không báo −4,12% OK)",
              b["daily"]["status"] == m.UNMEASURABLE and "04:49:59" in b["daily"]["reason"]
              and abs(b["daily"]["value"] - (0.94 * 1.02 - 1)) < 1e-9 and len(fx.msgs()) == 2,
              f"{b['daily']}")
        check("V13 ...lỗ từ đỉnh đo được (dòng D3 là giá chốt)", b["drawdown"]["status"] == m.OK,
              f"{b['drawdown']}")
        fx.nav("A", D3, 100e6, ts=f"{D4}T09:15:15")
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]["daily"]
        check("V14 dòng chụp 09:15 HÔM SAU ⇒ KHÔNG ĐO ĐƯỢC, nêu 'SAU giờ mở cửa'",
              b["status"] == m.UNMEASURABLE and "SAU giờ mở cửa" in b["reason"], f"{b}")
    finally:
        fx.close()


def t_provisional_breach():
    print("[B6] số TẠM TÍNH đã vượt ngưỡng là trạng thái riêng: tin đỏ, lệnh BOT_STOP, khoá riêng")
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 99e6)])
        rc, out, st = fx.run(D3)                            # 22:00 chưa có dòng D3
        check("W1 thiếu dòng ⇒ tin vàng KHÔNG ĐO ĐƯỢC, không có lệnh BOT_STOP",
              len(fx.msgs()) == 1 and "KHÔNG ĐO ĐƯỢC" in fx.msgs()[0] and "touch " not in fx.msgs()[0])
        fx.nav("A", D3, 99e6 * 0.92, est=True)              # dòng backfill ước tính về muộn: −8%
        rc, out, st = fx.run(D3, now=f"{D4}T00:15:00")
        a = st["accounts"]["A"]
        check("W2 dòng ước tính −8% ⇒ BREACH_PROVISIONAL (không phải KHÔNG ĐO ĐƯỢC)",
              a["brakes"]["daily"]["status"] == m.BREACH_PROV and a["overall"] == m.BREACH_PROV
              and rc == 1, f"{a['brakes']['daily']}")
        check("W3 ...và GỬI tin mới dù phiên này đã gửi 'KHÔNG ĐO ĐƯỢC' (khoá chống-trùng riêng)",
              len(fx.msgs()) == 2, f"{len(fx.msgs())}")
        t = fx.msgs()[-1]
        check("W4 tin đỏ: đầu tin TẠM TÍNH ĐÃ VƯỢT NGƯỠNG + lệnh BOT_STOP in sẵn",
              t.startswith("🚨") and "TẠM TÍNH ĐÃ VƯỢT NGƯỠNG" in t and "touch " in t
              and "BOT_STOP" in t and "🔴 Lỗ một ngày: TẠM TÍNH -8,00%" in t, t)
        sent = json.loads(read(os.path.join(fx.state, "alerts_sent.json")))
        check("W5 khoá chống-trùng mang trạng thái BREACH_PROVISIONAL",
              f"A|{D3}|daily|BREACH_PROVISIONAL" in sent and f"A|{D3}|daily|UNMEASURABLE" in sent,
              f"{sorted(sent)}")
        check("W6 vẫn KHÔNG tạo BOT_STOP", not os.path.exists(os.path.join(fx.data, "BOT_STOP")))
        rc, line = fx.health("A", f"{D4}T08:20:00")
        check("W7 dòng ops_health: rc=1 + nêu TẠM TÍNH … ĐÃ VƯỢT", rc == 1 and "ĐÃ VƯỢT" in line, line)
        rc, out, st = fx.run(D3, now=f"{D4}T00:30:00")
        check("W8 chạy lại: không gửi trùng", len(fx.msgs()) == 2)
    finally:
        fx.close()


def t_corp_calendar():
    print("[B2/N8/N9] bẫy lịch corp-action không fail-open · biên giá theo sàn")

    def day3(price=46750, corp="keep", sleeve=None, exch=None, z_nav=998e6):
        fx = _two_accounts()
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, z_nav)
        fx.positions("222", D3, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D3, [("XXX", 10000, price)])
        if corp != "keep":
            fx.corp(D3, corp[0], usable=corp[1])
        if sleeve is not None:
            fx.flows("Z", sleeve, sleeve=True)
        if exch is not None:
            fx._j(os.path.join(fx.state, "excluded_ticker_exchange.json"), exch)
        return fx

    fx = day3(corp=(None, True))
    try:
        rc, out, st = fx.run(D3)
        z = st["accounts"]["Z"]
        r = z["brakes"]["daily"]["reason"] or ""
        check("Y1 đang giữ mã loại trừ mà KHÔNG có snapshot lịch corp-action phiên đó ⇒ KHÔNG ĐO ĐƯỢC",
              z["overall"] == m.UNMEASURABLE and "KHÔNG kiểm được lịch corp-action" in r and D3 in r
              and f"không có corp_action_daily_{D3}.json" in r, r)
        fx.nav("Z", D4, 998e6)
        fx.nav("S", D4, 100e6)
        fx.positions("222", D4, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D4, [("XXX", 10000, 46750)])
        rc, out, st = fx.run(D4)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y2 bẫy chưa khai CHẶN TIẾP các phiên sau (không chỉ một ngày), vẫn nêu ngày gốc",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and f"gần nhất {D3}" in r, r)
        fx.flows("Z", [{"date": D3, "amount_vnd": 0, "kind": "market_only", "evidence": "x"}],
                 sleeve=True)
        rc, out, st = fx.run(D4)
        check("Y3 khai market_only cho ngày đó ⇒ đo lại được", st["accounts"]["Z"]["overall"] == m.OK,
              f"{st['accounts']['Z']['brakes']['daily']}")
    finally:
        fx.close()
    fx = day3(corp=([{"ticker": "XXX", "date": D3, "event_code": "DIV", "value_per_share": "1"}],
                    False))
    try:
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y4 snapshot usable=False ⇒ là bẫy 'không kiểm được', KHÔNG lấy sự kiện từ nó",
              "không dùng được" in r and "usable=False" in r and "hiệu lực" not in r, r)
    finally:
        fx.close()
    fx = day3(corp=([], False))
    try:
        rc, out, st = fx.run(D3)
        check("Y5 snapshot usable=False không có sự kiện nào ⇒ vẫn KHÔNG ĐO ĐƯỢC (không coi là sạch)",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE, f"{st['accounts']['Z']['brakes']['daily']}")
    finally:
        fx.close()
    fx = day3(corp=([{"ticker": "XXX", "date": D5, "event_code": "DIV", "value_per_share": "1000",
                      "title": "sắp tới"}], True))
    try:
        rc, out, st = fx.run(D3)
        check("Y6 sự kiện có ngày hiệu lực TƯƠNG LAI (D5) không gây bẫy ở D3",
              st["accounts"]["Z"]["overall"] == m.OK, f"{st['accounts']['Z']['brakes']['daily']}")
    finally:
        fx.close()
    # --- chuỗi bắc cầu qua ngày thiếu: sự kiện rơi đúng ngày thiếu vẫn phải bị bắt
    fx = _two_accounts()
    try:
        fx.nav("S", D4, 100e6)
        fx.nav("Z", D4, 998e6)                               # Z không có dòng D3
        fx.positions("222", D4, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D4, [("XXX", 10000, 45000)])      # −3,7% qua 2 phiên: trong biên
        fx.corp(D3, [{"ticker": "XXX", "date": D3, "event_code": "DIV", "value_per_share": "1500",
                      "title": "Cổ tức 1.500đ"}])
        rc, out, st = fx.run(D4)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y7 sự kiện rơi vào phiên KHÔNG có dòng (D3) vẫn bị bắt khi chuỗi bắc cầu D2→D4",
              f"hiệu lực {D3}" in r and "15.000.000đ" in r, r)
        fx.corp(D3, None)
        rc, out, st = fx.run(D4)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y8 ...và thiếu snapshot của phiên bị bắc cầu cũng là bẫy",
              "KHÔNG kiểm được lịch corp-action" in r and D3 in r, r)
    finally:
        fx.close()
    fx = _two_accounts()
    try:
        fx.auto_pos = False
        fx.nav("Z", D3, 998e6)                               # có dòng NAV D3 nhưng không có dnse_raw
        fx.auto_pos = True
        fx.nav("S", D4, 100e6)
        fx.nav("Z", D4, 998e6)
        rc, out, st = fx.run(D4)
        z = st["accounts"]["Z"]
        check("Y9 chuỗi có ngày thiếu ⇒ cảnh báo 'bắc cầu qua' nêu ngày thiếu",
              any("bắc cầu qua" in w and D3 in w for w in z["warnings"]), f"{z['warnings']}")
    finally:
        fx.close()
    # --- biên giá
    fx = day3(price=46750 * 1.2)
    try:
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y10 giá mã loại trừ +20% trong MỘT phiên (phía TRÊN biên) ⇒ bẫy",
              "quá biên độ" in r and "+20,00%" in r, r)
        check("Y11 chữ in ra không làm hỏng giá: '46.750' còn nguyên, biên ghi '±7,5%/phiên'",
              "46.750 → 56.100" in r and "±7,5%/phiên" in r, r)
        check("Y12 chưa khai sàn ⇒ dùng biên HOSE và NÓI là mặc định", "HOSE — mặc định" in r, r)
    finally:
        fx.close()
    fx = day3(price=46750 * 1.12, exch={"XXX": "UPCOM"})
    try:
        rc, out, st = fx.run(D3)
        check("Y13 mã khai sàn UPCOM: +12% một phiên nằm trong biên ±15% ⇒ không bẫy",
              st["accounts"]["Z"]["brakes"]["drawdown"]["status"] == m.OK,
              f"{st['accounts']['Z']['brakes']['daily']}")
    finally:
        fx.close()
    fx = day3(price=46750 * 1.12, exch={"XXX": "NASDAQ"})
    try:
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Y14 sàn khai không nhận ra ⇒ về biên hẹp nhất (kêu), nêu giá trị đã khai",
              "quá biên độ" in r and "'NASDAQ'" in r, r)
    finally:
        fx.close()


def t_managed_invariants():
    print("[B8] bất biến trên nhánh phần-bot-quản-lý")

    def day3(z_nav=998e6):
        fx = _two_accounts()
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, z_nav)
        fx.positions("222", D3, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D3, [("XXX", 10000, 46750)])
        return fx

    wd = {"date": D3, "time_ict": "10:00", "amount_vnd": -300e6, "kind": "withdraw", "evidence": "x"}
    fx = day3(z_nav=998e6 - 300e6)
    try:
        fx.flows("Z", [wd])
        rc, out, st = fx.run(D3)
        b = st["accounts"]["Z"]["brakes"]
        check("Z1 RÚT 300tr khỏi account có mã loại trừ, đã khai ⇒ phần quản lý ngày 0%, không kêu",
              b["daily"]["status"] == m.OK and abs(b["daily"]["value"]) < 1e-9
              and abs(b["drawdown"]["value"] - (530.5 / 540 - 1)) < 1e-9, f"{b['daily']} {b['drawdown']}")
        fx.flows("Z", [])
        rc, out, st = fx.run(D3)
        check("Z2 đối chứng: không khai lần rút ⇒ BREACH (ca Z1 có răng)",
              brakes(st, "Z")["daily"] == m.BREACH, f"{brakes(st, 'Z')}")
        fx.flows("Z", [wd])
        fx.flows("Z", [{"date": D3, "time_ict": "23:00", "amount_vnd": 5e6, "kind": "deposit",
                        "evidence": "x"}], sleeve=True)
        rc, out, st = fx.run(D3, now=f"{D3}T23:30:00")
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z3 dòng tiền GIỮA hai phần còn TREO (khai sau lần chụp NAV cuối) ⇒ KHÔNG ĐO ĐƯỢC",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "TREO" in r
              and "managed_sleeve_flows" in r, r)
        os.remove(os.path.join(fx.state, "managed_sleeve_flows.json"))
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z4 MẤT managed_sleeve_flows.json ⇒ KHÔNG ĐO ĐƯỢC (không coi như 'không có dòng tiền')",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "managed_sleeve_flows.json" in r, r)
    finally:
        fx.close()
    fx = day3()
    try:
        fx._j(os.path.join(fx.exec, "active_nav_Z.json"),
              {"account": "Z", "computed_at": D3, "total_nav": 998e6,
               "positions": [{"ticker": "XXX", "qty": 10000, "price": 0}]})
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z5 active_nav không có giá của mã loại trừ đang giữ ⇒ KHÔNG ĐO ĐƯỢC (không coi giá = 0)",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "không có giá của mã loại trừ XXX" in r, r)
        fx._j(os.path.join(fx.exec, "active_nav_Z.json"),
              {"account": "S", "computed_at": D3, "total_nav": 998e6,
               "positions": [{"ticker": "XXX", "qty": 10000, "price": 46750}]})
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z6 active_nav của ACCOUNT KHÁC (đúng ngày) ⇒ KHÔNG ĐO ĐƯỢC, nêu account đọc được",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "account='S'" in r, r)
    finally:
        fx.close()
    fx = day3()
    real = m._append_excluded
    try:
        def boom(path, rows):
            raise OSError("đĩa đầy (giả lập)")
        m._append_excluded = boom
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z7 GHI chuỗi mã loại trừ lỗi ⇒ KHÔNG ĐO ĐƯỢC kèm đúng lỗi đọc được (không nuốt)",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "đĩa đầy (giả lập)" in r
              and "OSError" in r, r)
    finally:
        m._append_excluded = real
        fx.close()
    # --- positions: lọc openQuantity>0, lấy bản ghi CUỐI, chụp sau giờ đóng cửa
    fx = _two_accounts()
    try:
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, 998e6)                               # bán hết XXX: tiền ở lại trong account
        fx.positions("222", D3, [("XXX", 10000, 1841)], ts="15:00:00")
        fx.positions("222", D3, [("XXX", 0, 1841), ("AAA", 5, 1841)], ts="19:07:00")
        fx.flows("Z", [{"date": D3, "time_ict": "10:00", "amount_vnd": 467.5e6, "kind": "deposit",
                        "evidence": "bán hết XXX"}], sleeve=True)
        rc, out, st = fx.run(D3)
        z = st["accounts"]["Z"]
        check("Z8 lấy bản ghi positions CUỐI ngày + bỏ dòng openQuantity=0 ⇒ giá trị mã loại trừ = 0, "
              "không cần giá", z["excluded_value"] == 0 and z["excluded_detail"] == {}
              and z["brakes"]["daily"]["status"] == m.OK, f"{z['excluded_value']} {z['brakes']['daily']}")
    finally:
        fx.close()
    fx = _two_accounts()
    try:
        fx.auto_pos = False
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, 998e6)
        fx.positions("111", D3, [("AAA", 1, 1841)])
        fx.positions("222", D3, [("XXX", 10000, 1841)], ts="04:58:00")
        fx.active_nav("Z", D3, [("XXX", 10000, 46750)])
        rc, out, st = fx.run(D3)
        r = st["accounts"]["Z"]["brakes"]["daily"]["reason"] or ""
        check("Z9 positions chỉ có bản chụp 04:58 (trước phiên) ⇒ không dùng làm danh mục cuối phiên",
              st["accounts"]["Z"]["overall"] == m.UNMEASURABLE and "04:58:00" in r
              and "trước giờ đóng cửa" in r, r)
    finally:
        fx.close()
    # --- đính chính có người + lý do, CSV gốc không đổi
    fx = day3()
    try:
        fx.run(D3)
        hist = os.path.join(fx.state, "excluded_value_history_Z.csv")
        before = read(hist)
        rc, out = fx.cli(f"{D3}T22:10:00", "--correct-excluded", "Z", "--date", D3,
                         "--detail", '{"XXX": {"qty": 10000, "price": 40000}}')
        check("Z10 đính chính thiếu người/lý do ⇒ từ chối", rc == 2 and "--corrected-by" in out, out)
        rc, out = fx.cli(f"{D3}T22:10:00", "--correct-excluded", "Z", "--date", D3, "--detail",
                         '{"AAA": {"qty": 1, "price": 1}}', "--corrected-by", "u", "--reason", "r")
        check("Z11 đính chính mã KHÔNG thuộc excluded_tickers ⇒ từ chối", rc == 2 and "AAA" in out, out)
        rc, out = fx.cli(f"{D3}T22:10:00", "--correct-excluded", "Z", "--date", D3, "--detail",
                         '{"XXX": {"qty": 10000, "price": 46000}}', "--corrected-by",
                         "user (fixture)", "--reason", "giá đóng cửa đúng là 46.000")
        rc2, out2, st = fx.run(D3)
        z = st["accounts"]["Z"]
        check("Z12 đính chính hợp lệ ⇒ giá trị đọc ra đổi theo, CSV gốc KHÔNG bị sửa",
              rc == 0 and z["excluded_value"] == 460e6 and read(hist) == before
              and abs(z["brakes"]["daily"]["value"] - (538 / 530.5 - 1)) < 1e-9,
              f"{rc} {z['excluded_value']} {z['brakes']['daily']}")
    finally:
        fx.close()


def t_episode_guards():
    print("[B4/B5/N5] episode: bằng chứng broker hai chiều · bản duyệt mới · mở tay")
    close = ["--closed-by", "user (fixture)", "--reason", "đã tất toán"]
    # --- B4a: episode còn mở mà broker hết vị thế gói vay
    fx = _episode_fx(95e6)
    try:
        fx.run(D5)
        fx.nav("L", D6, 96e6)                                # auto positions: không còn gói 1840
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G1 episode đang mở mà broker KHÔNG còn vị thế gói vay ⇒ KHÔNG ĐO ĐƯỢC, gợi ý đóng",
              e["status"] == m.UNMEASURABLE and "--close-episode" in e["reason"] and rc == 1, f"{e}")
        os.remove(os.path.join(fx.exec, f"dnse_raw_{D6}.jsonl"))
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G1b episode đang mở mà KHÔNG đọc được positions phiên đó ⇒ KHÔNG ĐO ĐƯỢC kèm lý do, "
              "vẫn cho số tạm tính", e["status"] == m.UNMEASURABLE and e["value"] is not None
              and "không kiểm được vị thế gói vay" in e["reason"]
              and f"dnse_raw_{D6}.jsonl" in e["reason"], f"{e}")
    finally:
        fx.close()
    # --- B4b: ca của reviewer — vào 100, lên 125, bản duyệt mới ở 125, về 105
    fx = Fx()
    try:
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 110e6), (D3, 125e6), (D4, 124e6), (D5, 105e6 / 0.96),
                          (D6, 105e6)])
        for d in (D2, D3, D4, D5, D6):
            fx.positions("111", d, [("BBB", 500, 1840)])
        fx.approval("L", D2)
        fx.run(D3)
        fx.approval("L", D4)
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G2 bản duyệt MỚI trong lúc episode còn mở ⇒ nêu ra; số xấu nhất −16% ⇒ TẠM TÍNH VƯỢT NGƯỠNG "
              "(không báo OK +5%)", e["status"] == m.BREACH_PROV and D4 in e["reason"]
              and abs(e["value"] - (105 / 125 - 1)) < 1e-9 and "+5,00%" in e["reason"], f"{e}")
        check("G3 ...không tự mở episode thứ hai", len(fx.episodes()) == 1, f"{fx.episodes()}")
        rc, out = fx.cli(f"{D6}T22:10:00", "--ack-approval", "L", "--approval-date", D4)
        check("G4 xác nhận thiếu người/lý do ⇒ từ chối", rc == 2, out)
        rc, out = fx.cli(f"{D6}T22:10:00", "--ack-approval", "L", "--approval-date", D4,
                         "--acked-by", "user (fixture)", "--reason", "cùng episode")
        rc2, out2, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G5 người xác nhận 'cùng episode' ⇒ đo tiếp từ điểm vào cũ: +5,00% OK",
              rc == 0 and e["status"] == m.OK and abs(e["value"] - 0.05) < 1e-9, f"{rc} {e}")
    finally:
        fx.close()
    # --- B5 ca 1: có vị thế vay không episode; hôm sau KHÔNG đọc được positions
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 99e6)])
        fx.positions("111", D2, [("BBB", 500, 1840)])
        rc, out, st = fx.run(D2)
        check("G6 vị thế gói vay không có episode ⇒ kêu", brakes(st, "A")["episode"] == m.UNMEASURABLE)
        fx.auto_pos = False
        fx.nav("A", D3, 98e6)                                # không có dnse_raw D3
        rc, out, st = fx.run(D3)
        e = st["accounts"]["A"]["brakes"]["episode"]
        check("G7 hôm sau KHÔNG có dnse_raw ⇒ phanh episode KHÔNG ĐO ĐƯỢC kèm lý do (chuông không tắt)",
              e["status"] == m.UNMEASURABLE and f"không có file dnse_raw_{D3}.jsonl" in e["reason"]
              and rc == 1, f"{e}")
        fx.positions("111", D3, [("BBB", 500, 1840)], ts="04:58:00")
        rc, out, st = fx.run(D3)
        e = st["accounts"]["A"]["brakes"]["episode"]
        check("G8 positions chỉ có bản chụp trước phiên ⇒ cũng KHÔNG ĐO ĐƯỢC, nêu giờ chụp",
              e["status"] == m.UNMEASURABLE and "04:58:00" in e["reason"], f"{e}")
        check("G9 hai phanh kia vẫn đo bình thường",
              brakes(st, "A")["daily"] == m.OK and brakes(st, "A")["drawdown"] == m.OK, f"{brakes(st, 'A')}")
    finally:
        fx.close()
    # --- B5 ca 2: ngày duyệt chỉ có positions 04:58 ⇒ không tự mở; mở TAY
    fx = Fx()
    try:
        fx.auto_pos = False
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 99e6), (D3, 84e6)])
        fx.positions("111", D1, [("AAA", 1, 1841)])
        fx.positions("111", D2, [("BBB", 500, 1840)], ts="04:58:00")
        fx.positions("111", D3, [("BBB", 500, 1840)])
        fx.approval("L", D2)
        rc, out, st = fx.run(D3)
        a = st["accounts"]["L"]
        check("G10 ngày duyệt không đọc được positions cuối phiên ⇒ KHÔNG tự mở, ghi chú chỉ đường mở tay",
              fx.episodes() == [] and a["brakes"]["episode"]["status"] == m.UNMEASURABLE
              and any("--open-episode" in n for n in a["notes"]), f"{a['notes']}")
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D2)
        check("G11 mở tay thiếu --opened-by/--reason ⇒ từ chối", rc == 2 and fx.episodes() == [], out)
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D6,
                         "--opened-by", "u", "--reason", "r")
        check("G12 mở tay với ngày TƯƠNG LAI ⇒ từ chối", rc == 2 and fx.episodes() == [], out)
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D2,
                         "--opened-by", "user (fixture)", "--reason", "sao kê broker: giải ngân 06/10")
        eps = fx.episodes()
        check("G13 mở tay hợp lệ ⇒ ghi episode, điểm vào mặc định = chốt phiên trước ngày mở",
              rc == 0 and len(eps) == 1 and eps[0]["entry_ref_date"] == D1
              and eps[0]["evidence"]["manual"] is True and eps[0]["opened_by"] == "user (fixture)",
              f"{rc} {out} {eps}")
        rc, out, st = fx.run(D3)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G14 ...và phanh −15% đo được ngay: −16% ⇒ BREACH", e["status"] == m.BREACH
              and abs(e["value"] - (-0.16)) < 1e-9, f"{e}")
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D3,
                         "--opened-by", "u", "--reason", "r")
        check("G15 mở tay khi đang có episode mở ⇒ từ chối", rc == 1 and len(fx.episodes()) == 1, out)
    finally:
        fx.close()
    # --- bản duyệt ngày d, vị thế xuất hiện ở PHIÊN KẾ ⇒ mở ở phiên kế
    fx = Fx()
    try:
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 99e6), (D3, 98e6), (D4, 97e6)])
        fx.positions("111", D3, [("BBB", 500, 1840)])
        fx.positions("111", D4, [("BBB", 500, 1840)])
        fx.approval("L", D2)
        rc, out, st = fx.run(D2)
        check("G16 tối ngày duyệt chưa có vị thế ⇒ chưa mở, ghi chú 'kiểm lại ở phiên kế'",
              fx.episodes() == [] and any("phiên kế" in n for n in st["accounts"]["L"]["notes"]),
              f"{st['accounts']['L']['notes']}")
        rc, out, st = fx.run(D3)
        eps = fx.episodes()
        check("G17 vị thế xuất hiện ở phiên kế ⇒ MỞ ở phiên kế, điểm vào = chốt ngày duyệt",
              len(eps) == 1 and eps[0]["opened_date"] == D3 and eps[0]["entry_ref_date"] == D2
              and eps[0]["approval_date"] == D2, f"{eps}")
        fx.run(D4)
        check("G18 chạy tiếp không mở trùng", len(fx.episodes()) == 1)
    finally:
        fx.close()
    # --- bản duyệt: account khác / tương lai / cũ hơn episode đã đóng / revoked chuẩn hoá
    fx = _episode_fx(95e6, approval=False)
    try:
        fx.approval("L", D2, account="OTHER")
        rc, out, st = fx.run(D5)
        check("G19 file duyệt mang tên L nhưng NỘI DUNG ghi account khác ⇒ không mở, có ghi chú",
              fx.episodes() == [] and any("OTHER" in n for n in st["accounts"]["L"]["notes"]),
              f"{st['accounts']['L']['notes']}")
    finally:
        fx.close()
    fx = _episode_fx(95e6, approval=False)
    try:
        fx.approval("L", D4)
        rc, out, st = fx.run(D3, now=f"{D3}T22:00:00")
        notes = st["accounts"]["L"]["notes"]
        check("G20 bản duyệt ngày TƯƠNG LAI so với phiên đang đo ⇒ chưa mở, chưa được nhắc tới "
              "(chỉ dùng dữ liệu <= phiên đo)", fx.episodes() == [] and not any(D4 in n for n in notes),
              f"{fx.episodes()} {notes}")
    finally:
        fx.close()
    fx = _episode_fx(95e6)
    try:
        fx.run(D5)
        rc, out = fx.cli(f"{D5}T22:30:00", "--close-episode", "L", *close)
        rc, out, st = fx.run(D5, now=f"{D5}T22:40:00")
        check("G21 đóng trong ngày D ⇒ từ chính phiên D episode không còn hiệu lực (ngày đóng không tính)",
              brakes(st, "L")["episode"] == m.UNMEASURABLE
              and "KHÔNG có episode nào đang mở" in st["accounts"]["L"]["brakes"]["episode"]["reason"],
              f"{st['accounts']['L']['brakes']['episode']}")
    finally:
        fx.close()
    fx = Fx()
    try:
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 99e6), (D3, 98e6), (D4, 97e6), (D5, 96e6), (D6, 95e6)])
        for d in (D1, D2, D3, D4):
            fx.positions("111", d, [("BBB", 500, 1840)])
        fx.approval("L", D3)
        fx.run(D4)
        fx.cli(f"{D5}T22:30:00", "--close-episode", "L", *close)
        fx.approval("L", D1)                                 # giấy tờ về muộn: CŨ hơn episode đã đóng
        fx.run(D6)
        eps = fx.episodes()
        check("G22 bản duyệt cũ hơn một episode đã đóng KHÔNG mở ra một episode ma (dù ngày đó có "
              "vị thế vay)", len(eps) == 1 and eps[0]["opened_date"] == D3 and eps[0]["closed_date"] == D5,
              f"{eps}")
    finally:
        fx.close()
    for val, opens in (("false", True), (0, True), ("true", False), (1, False), ("yes", False)):
        fx = _episode_fx(95e6, revoked=val)
        try:
            fx.run(D5)
            check(f"G23 revoked={val!r} ⇒ {'CHƯA thu hồi, mở' if opens else 'ĐÃ thu hồi, không mở'} "
                  f"(cùng chuẩn với trading_bot/plan.py)", (len(fx.episodes()) == 1) == opens,
                  f"{fx.episodes()}")
        finally:
            fx.close()
    # --- vị thế gói vay openQuantity=0 không phải vị thế; cờ ước tính ở episode
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 99e6)])
        fx.positions("111", D2, [("BBB", 0, 1840), ("AAA", 10, 1841)])
        rc, out, st = fx.run(D2)
        check("G24 dòng gói vay openQuantity=0 (đã đóng) KHÔNG phải vị thế ⇒ 'không có episode', rc=0",
              brakes(st, "A")["episode"] == m.NO_EPISODE and rc == 0, f"{st['accounts']['A']['brakes']['episode']}")
    finally:
        fx.close()
    fx = _episode_fx(95e6)
    try:
        fx.nav("L", D5, 95e6, est=True)
        rc, out, st = fx.run(D5)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G25 dòng ước tính ⇒ phanh episode cũng chỉ TẠM TÍNH (KHÔNG ĐO ĐƯỢC)",
              e["status"] == m.UNMEASURABLE and "nav_is_estimate" in e["reason"]
              and abs(e["value"] - (-0.05)) < 1e-9, f"{e}")
        fx.nav("L", D5, 84e6, est=True)
        rc, out, st = fx.run(D5)
        check("G26 ...ước tính −16% từ điểm vào ⇒ TẠM TÍNH VƯỢT NGƯỠNG",
              brakes(st, "L")["episode"] == m.BREACH_PROV, f"{st['accounts']['L']['brakes']['episode']}")
    finally:
        fx.close()


def t_monitor_failures():
    print("[B7/N1/N2/N10] monitor tự hỏng vẫn để lại status + tin · chạy khô · khoá")

    def two_down():
        fx = Fx()
        fx.account("A", "111")
        fx.account("B", "222")
        fx.navs_seq("A", [(D1, 100e6), (D2, 70e6)])
        fx.navs_seq("B", [(D1, 100e6), (D2, 70e6)])
        return fx

    fx = two_down()
    try:
        sp = os.path.join(fx.state, "alerts_sent.json")
        with open(sp, "w", encoding="utf-8") as f:
            f.write('{"A|2026-10-05|daily|BREACH": "2026-')        # sổ đã-gửi cụt
        rc, out, st = fx.run(D2)
        check("X1 sổ đã-gửi cụt, hai account −30% ⇒ VẪN gửi đủ 2 tin đỏ, có status",
              len(fx.msgs()) == 2 and st is not None and st["overall"] == m.BREACH and rc == 1,
              f"rc={rc} msgs={len(fx.msgs())} {out[-300:]}")
        check("X2 tin nói rõ sổ đã-gửi hỏng (có thể trùng) + lỗi đọc được",
              "sổ đã-gửi" in fx.msgs()[0] and "JSONDecodeError" in fx.msgs()[0], fx.msgs()[0][-300:])
        check("X3 sổ được dựng lại hợp lệ, bản hỏng cất sang .corrupt.*",
              isinstance(json.loads(read(sp)), dict)
              and any(".corrupt." in f for f in os.listdir(fx.state)), f"{os.listdir(fx.state)}")
        fx.run(D2)
        check("X4 lượt sau không gửi trùng", len(fx.msgs()) == 2)
    finally:
        fx.close()
    fx = two_down()
    try:
        ep = os.path.join(fx.state, "episodes.json")
        with open(ep, "w", encoding="utf-8") as f:
            f.write('{"episodes": [')
        rc, out, st = fx.run(D2)
        b = st["accounts"]["A"]["brakes"]
        check("X5 sổ episode cụt ⇒ hai phanh kia VẪN đo (BREACH), phanh episode KHÔNG ĐO ĐƯỢC kèm lỗi",
              b["daily"]["status"] == m.BREACH and b["episode"]["status"] == m.UNMEASURABLE
              and "sổ episode" in b["episode"]["reason"] and len(fx.msgs()) == 2, f"{b['episode']}")
        check("X6 ...file episode hỏng KHÔNG bị ghi đè", read(ep) == '{"episodes": [')
    finally:
        fx.close()
    fx = two_down()
    try:
        with open(fx.secrets, "w", encoding="utf-8") as f:
            f.write('{"accounts": [')
        rc, out, st = fx.run(D2)
        check("X7 cấu hình account không đọc được ⇒ rc=3, VẪN có status ghi lỗi thật + mọi account KHÔNG ĐO ĐƯỢC",
              rc == 3 and st is not None and "JSONDecodeError" in (st.get("error") or "")
              and st["overall"] == m.UNMEASURABLE and st["session"] == D2
              and all(a["overall"] == m.UNMEASURABLE for a in st["accounts"].values())
              and sorted(st["accounts"]) == ["A", "B"], f"rc={rc} {st and st.get('error')}")
        check("X8 ...và MỘT tin 'monitor lỗi' kèm lỗi thật", len(fx.msgs()) == 1
              and "MONITOR PHANH LỖ NAV LỖI" in fx.msgs()[0] and "JSONDecodeError" in fx.msgs()[0],
              f"{fx.msgs()}")
        fx.run(D2)
        check("X9 chạy lại cùng lỗi: không gửi trùng", len(fx.msgs()) == 1)
        hrc, line = fx.health("A", f"{D3}T08:20:00")
        check("X10 dòng ops_health: rc=3 (lỗi vận hành, KHÔNG phải WARN-ONLY) + nêu MONITOR LỖI",
              hrc == 3 and "MONITOR LỖI" in line, f"{hrc} {line}")
        check("X11 có nhật ký lượt chạy (bằng chứng monitor có chạy)",
              len(read(os.path.join(fx.state, "run_log.jsonl")).splitlines()) == 2)
    finally:
        fx.close()
    fx = two_down()
    try:
        fx.positions("111", D2, [("BBB", "abc", 1840)])          # dữ liệu broker hỏng ⇒ A nổ khi đo
        rc, out, st = fx.run(D2)
        a, b = st["accounts"]["A"], st["accounts"]["B"]
        check("X12 MỘT account nổ khi đo ⇒ account đó KHÔNG ĐO ĐƯỢC (không phải OK), nêu lỗi thật",
              a["overall"] == m.UNMEASURABLE and a.get("monitor_error") is True
              and "monitor lỗi khi đo A" in a["brakes"]["daily"]["reason"]
              and "ValueError" in a["brakes"]["daily"]["reason"], f"{a['brakes']['daily']}")
        check("X13 ...account kia vẫn đo + cả hai đều có tin; rc=3",
              b["brakes"]["daily"]["status"] == m.BREACH and len(fx.msgs()) == 2 and rc == 3,
              f"rc={rc} {len(fx.msgs())}")
        hrc, line = fx.health("A", f"{D3}T08:20:00")
        hrc_b, line_b = fx.health("B", f"{D3}T08:20:00")
        check("X14 ops_health: account nổ ⇒ rc=3 (tới được vận hành); account chạm phanh ⇒ rc=1",
              hrc == 3 and "MONITOR LỖI" in line and hrc_b == 1, f"{hrc} {line} | {hrc_b}")
    finally:
        fx.close()
    # --- N1: --date của phiên cũ ⇒ chạy khô
    fx = two_down()
    try:
        fx.run(D2)
        before, n = read(os.path.join(fx.state, "status.json")), len(fx.msgs())
        fx.nav("A", D3, 50e6)
        fx.nav("B", D3, 50e6)
        rc, out, st = fx.run(D4, extra=["--date", D3])
        check("N10 --date khác phiên phải đo ⇒ CHẠY KHÔ: không đổi status, không gửi, vẫn in số",
              read(os.path.join(fx.state, "status.json")) == before and len(fx.msgs()) == n
              and "CHẠY KHÔ" in out and "ĐÃ CHẠM" in out and rc == 1, out[-300:])
        rc, out, st = fx.run(D4, extra=["--date", D3, "--write-backdated"])
        check("N11 thêm --write-backdated ⇒ ghi status phiên đó + gửi",
              st["session"] == D3 and len(fx.msgs()) == n + 2, f"{st['session']} {len(fx.msgs())}")
        rc, out, st = fx.run(D3, extra=["--date", D3])
        check("N12 --date TRÙNG phiên phải đo ⇒ chạy thật như thường", "CHẠY KHÔ" not in out)
    finally:
        fx.close()
    fx = _two_accounts()
    try:
        fx.run(D2)
        fx.nav("S", D3, 100e6)
        fx.nav("Z", D3, 998e6)
        fx.positions("222", D3, [("XXX", 10000, 1841)])
        fx.active_nav("Z", D3, [("XXX", 10000, 46750)])
        hist = os.path.join(fx.state, "excluded_value_history_Z.csv")
        before, log = read(hist), read(os.path.join(fx.state, "run_log.jsonl"))
        rc, out, st = fx.run(D4, extra=["--date", D3])
        check("N12b chạy khô KHÔNG ghi chuỗi mã loại trừ, KHÔNG ghi nhật ký lượt chạy",
              read(hist) == before and read(os.path.join(fx.state, "run_log.jsonl")) == log
              and "CHẠY KHÔ" in out, out[-200:])
    finally:
        fx.close()
    # --- N2: khoá
    fx = two_down()
    wait = m.LOCK_WAIT_S
    try:
        import fcntl
        os.makedirs(fx.state, exist_ok=True)
        holder = open(os.path.join(fx.state, ".lock"), "a", encoding="utf-8")
        fcntl.flock(holder, fcntl.LOCK_EX)
        m.LOCK_WAIT_S = 0
        rc, out, st = fx.run(D2)
        check("N13 lượt khác đang giữ khoá ⇒ rc=4, không ghi status, không gửi",
              rc == 4 and st is None and fx.msgs() == [] and "khoá" in out, f"rc={rc} {out}")
        rc, out = fx.cli(f"{D2}T22:10:00", "--close-episode", "A", "--closed-by", "u", "--reason", "r")
        check("N14 --close-episode cũng phải chờ khoá ⇒ rc=4", rc == 4, out)
        holder.close()
        rc, out, st = fx.run(D2)
        check("N15 nhả khoá ⇒ chạy bình thường", rc == 1 and len(fx.msgs()) == 2)
    finally:
        m.LOCK_WAIT_S = wait
        fx.close()
    # --- N10: phiên là dòng đầu tiên của chuỗi
    fx = Fx()
    try:
        fx.account("A", "111", inception=D1)
        fx.nav("A", D1, 100e6)
        rc, out, st = fx.run(D1)
        r = st["accounts"]["A"]["brakes"]["daily"]["reason"]
        check("N16 phiên = mốc đầu chuỗi ⇒ lý do nói đúng việc đó (không đổ cho chuỗi mã loại trừ)",
              "ĐẦU TIÊN" in r and "mã loại trừ" not in r, r)
    finally:
        fx.close()


def t_backfill_tool():
    print("[B3] công cụ vá chuỗi mã loại trừ: chỉ THÊM ngày thiếu, ghi nguyên tử")
    import nav_loss_brake_backfill_excluded as bf
    fx = _two_accounts()
    try:
        for d in (D0, D1, D2):
            fx.positions("222", d, [("XXX", 10000, 1841)])
        fx.nav("Z", D3, 998e6)
        fx.positions("222", D3, [("XXX", 10000, 1841)])
        fx.nav("Z", D4, 998e6)
        fx.positions("222", D4, [("XXX", 10000, 1841)], ts="04:58:00")
        csvp = os.path.join(fx.root, "px.csv")
        with open(csvp, "w", encoding="utf-8") as f:
            f.write("time,ticker,Price,Close\n" + "".join(f"{d},XXX,50000,50000\n" for d in ALL_D))
        hist = os.path.join(fx.state, "excluded_value_history_Z.csv")
        before = read(hist)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = bf.main(["--price-csv", csvp, "--out-dir", fx.state, "--data-root", fx.data,
                          "--secrets", fx.secrets, "--account", "Z"])
        after = read(hist)
        check("BF1 dòng đã có (D0–D2, giá 46.000/46.750) KHÔNG bị ghi đè bằng giá 50.000 của CSV",
              rc == 0 and after.startswith(before.rstrip("\n")) and "46750" in after, buf.getvalue())
        check("BF2 chỉ THÊM ngày thiếu (D3) với giá từ CSV", f'{D3},500000000' in after, after[-300:])
        check("BF3 ngày chỉ có positions chụp trước phiên (D4) ⇒ bỏ qua, nêu lý do, không điền hộ",
              D4 not in after and "04:58:00" in buf.getvalue(), buf.getvalue())
        check("BF4 không sót file tạm", not [f for f in os.listdir(fx.state) if ".tmp" in f])
        src = read(os.path.join(BIN, "nav_loss_brake_backfill_excluded.py"))
        check("BF5 công cụ không còn xoá CSV trước khi ghi", "os.remove" not in src)
    finally:
        fx.close()


def main():
    os.environ.pop(m.SINK_ENV, None)
    for t in (t_thresholds, t_threshold_parsing, t_daily_edges, t_float_edge, t_dd_edges, t_episode,
              t_flows, t_fail_loud, t_close_capture, t_provisional_breach, t_two_accounts_and_sleeve,
              t_corp_calendar, t_managed_invariants, t_episode_guards, t_idempotent,
              t_monitor_failures, t_backfill_tool, t_health_and_clock):
        try:
            t()
        except Exception as exc:           # ca nổ giữa chừng = FAIL có tên, không phải traceback trần
            check(f"{t.__name__} chạy hết không nổ", False, f"{type(exc).__name__}: {exc}")
    os.environ.pop(m.SINK_ENV, None)
    print(f"\nnav_loss_brake_monitor_selfcheck: {PASS} PASS / {FAIL} FAIL "
          f"(TZ={os.environ.get('TZ', '<unset>')})")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
