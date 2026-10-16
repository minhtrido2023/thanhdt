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
        for d in (self.exec, self.state, os.path.join(self.data, "margin_approvals")):
            os.makedirs(d)
        self.acc, self.navs, self.incep = [], {}, {}
        self.cash = {}
        self.nos, self.auto_pos, self.pos_written = {}, True, set()
        self.rules()
        self._j(os.path.join(self.state, "episodes.json"), {"episodes": []})

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

    def nav(self, label, date, nav, est=False, ts="19:10:00"):
        """`ts`: giờ chụp trong chính ngày đó ("HH:MM:SS") hoặc dấu thời gian đầy đủ ("…T…").
        Mặc định kèm một bản ghi positions cuối phiên KHÔNG có vị thế gói vay."""
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

    def flows(self, label, recs):
        self.cash[label] = recs
        self._j(os.path.join(self.data, "account_cash_flows.json"), self.cash)

    def approval(self, label, date, revoked=None, account=None):
        rec = {"account": account or label, "plan_date": date, "approved_by": "user (fixture)"}
        if revoked is not None:
            rec["revoked"] = revoked
        self._j(os.path.join(self.data, "margin_approvals",
                             f"margin_approval_{label}_{date}.json"), rec)

    def cli(self, now, *extra):
        """Gọi main() với cờ tuỳ ý (đóng/mở episode, ack…). Trả (rc, output)."""
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
    node = json.load(open(real, encoding="utf-8"))["macro_kill_switches"]["C_episode_drawdown_breaker"]
    check("A4b file THẬT CÓ khoá số episode_drawdown_limit_pct và monitor đọc ĐÚNG khoá đó",
          node.get(m.EPISODE_NUMERIC_KEY) == th["episode"] and "khoá số" in th["episode_source"],
          f"{node.get(m.EPISODE_NUMERIC_KEY)} {th}")
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
        check("A7b K1: thiếu ngưỡng nhưng sổ có dòng phiên ⇒ VẪN kèm số tạm tính −10%",
              b["daily"]["value"] is not None and abs(b["daily"]["value"] + 0.10) < 1e-9
              and "tạm tính -10,00%" in fx.msgs()[0], f"{b['daily']}")
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
        check("E4 MẤT sổ dòng tiền ⇒ KHÔNG coi như 'không có dòng tiền': số chỉ là TẠM TÍNH, −75% "
              "chưa trừ lần rút ⇒ TẠM TÍNH VƯỢT NGƯỠNG (K1), lý do nêu file",
              b["daily"]["status"] == m.BREACH_PROV and b["drawdown"]["status"] == m.BREACH_PROV
              and "account_cash_flows.json" in b["daily"]["reason"]
              and abs(b["daily"]["value"] + 0.75) < 1e-9, f"{b['daily']}")
        check("E4b K8: thông báo thiếu sổ KHÔNG gợi ý tạo file rỗng để qua",
              "Tạo file" not in b["daily"]["reason"] and "[]" not in b["daily"]["reason"]
              and "sao lưu" in b["daily"]["reason"], b["daily"]["reason"])
        fx.navs_seq("A", [(D1, 100e6), (D2, 100e6), (D3, 99e6)])      # mất sổ, số tạm tính xa ngưỡng
        n = len(fx.msgs())
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]
        check("E4c mất sổ + tạm tính −1% ⇒ KHÔNG ĐO ĐƯỢC kèm số, VẪN đẩy tin (không thuộc luật giảm tin)",
              b["daily"]["status"] == m.UNMEASURABLE and b["daily"]["value"] is not None
              and not b["daily"].get("quiet") and len(fx.msgs()) == n + 1, f"{b['daily']}")
        fx.navs_seq("A", [(D1, 100e6), (D2, 200e6), (D3, 50e6)])
        # dòng tiền khai SAU lần chụp NAV cuối cùng ⇒ chưa dòng nào chứa nó (treo)
        fx.flows("A", [dep, wd, {"date": D3, "time_ict": "23:00", "amount_vnd": 5e6,
                                 "kind": "deposit", "evidence": "fixture"}])
        rc, out, st = fx.run(D3, now=f"{D3}T23:30:00")
        b = st["accounts"]["A"]["brakes"]
        check("E5 dòng tiền TREO (chưa dòng NAV nào chụp sau nó) ⇒ KHÔNG ĐO ĐƯỢC, kèm số tạm tính (K1)",
              b["daily"]["status"] == m.UNMEASURABLE and "TREO" in b["daily"]["reason"]
              and b["daily"]["value"] is not None and not b["daily"].get("quiet"), f"{b['daily']}")
        fx.nav("A", D3, 40e6)                      # còn dòng treo mà số tạm tính đã vượt ngưỡng
        rc, out, st = fx.run(D3, now=f"{D3}T23:40:00")
        b = st["accounts"]["A"]["brakes"]
        check("E6 dòng tiền TREO + tạm tính vượt ngưỡng ⇒ TẠM TÍNH VƯỢT NGƯỠNG (tin đỏ), không còn "
              "là 'không đo được' trơn", b["daily"]["status"] == m.BREACH_PROV
              and "TREO" in b["daily"]["reason"]
              and "touch " in m.alert_text("A", st["accounts"]["A"]), f"{b['daily']}")
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
        check("F3 chỉ vướng cờ ước tính + tạm tính −1,01% (cách ngưỡng 3,99pp) ⇒ rc=1, status vẫn KHÔNG "
              "ĐO ĐƯỢC, nhưng KHÔNG đẩy tin (luật giảm tin)",
              rc == 1 and fx.msgs() == [] and b["daily"].get("quiet") is True
              and st["accounts"]["A"]["alert"]["suppressed"] == ["daily", "drawdown"],
              f"{len(fx.msgs())} {st['accounts']['A']['alert']}")
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
              b["daily"]["status"] == m.UNMEASURABLE and D5 in b["daily"]["reason"]
              and not b["daily"].get("quiet"), f"{b['daily']}")
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


def t_idempotent():
    print("[K/L] gửi trùng · đánh dấu ngay · gửi lỗi · file trạng thái")
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 70e6)])
        rc, out, st = fx.run(D2)
        check("K1 lần đầu: 1 tin", len(fx.msgs()) == 1 and st["accounts"]["A"]["alert"]["sent_now"])
        check("K1c status.alert ghi rõ tin đi vào SINK nào (K5)",
              st["accounts"]["A"]["alert"]["sink"] == fx.sink, f"{st['accounts']['A']['alert']}")
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
        check("H6 phiên trước có vi phạm ⇒ dòng sáng rc=5 (riêng cho phanh chạm) + nêu ĐÃ CHẠM",
              rc == m.HEALTH_RC_BREACH == 5 and "ĐÃ CHẠM" in line, f"{rc} {line}")
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
        fx.rules(numeric=-0.12)                 # trigger mặc định ghi -0.15 (-15%)
        th, err = m.load_thresholds(rp)
        check("A13b khoá số −0.12 LỆCH câu chữ trigger −0.15 ⇒ KHÔNG ĐO ĐƯỢC, không chọn hộ",
              th["episode"] is None and "LỆCH" in err.get("episode", ""), f"{th} {err}")
        fx.rules(numeric=-0.15)
        th, err = m.load_thresholds(rp)
        check("A13c khoá số khớp câu chữ ⇒ dùng khoá số", th["episode"] == -0.15 and err == {},
              f"{th} {err}")
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
        check("W7 dòng ops_health: rc=5 + nêu TẠM TÍNH … ĐÃ VƯỢT", rc == 5 and "ĐÃ VƯỢT" in line,
              f"{rc} {line}")
        rc, out, st = fx.run(D3, now=f"{D4}T00:30:00")
        check("W8 chạy lại: không gửi trùng", len(fx.msgs()) == 2)
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
              e["status"] == m.UNMEASURABLE and "--close-episode" in e["reason"] and rc == 1
              and not e.get("quiet"), f"{e}")
        os.remove(os.path.join(fx.exec, f"dnse_raw_{D6}.jsonl"))
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G1b episode đang mở mà KHÔNG đọc được positions phiên đó ⇒ KHÔNG ĐO ĐƯỢC kèm lý do, "
              "vẫn cho số tạm tính", e["status"] == m.UNMEASURABLE and e["value"] is not None
              and "không kiểm được vị thế gói vay" in e["reason"]
              and f"dnse_raw_{D6}.jsonl" in e["reason"] and not e.get("quiet"), f"{e}")
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
    # --- B5 ca 2: ngày duyệt chỉ có positions 04:58 ⇒ VẪN thử phiên kế; điểm vào = mốc XẤU hơn
    fx = Fx()
    try:
        fx.auto_pos = False
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 110e6), (D3, 93.5e6)])
        fx.positions("111", D1, [("AAA", 1, 1841)])
        fx.positions("111", D2, [("BBB", 500, 1840)], ts="04:58:00")
        fx.positions("111", D3, [("BBB", 500, 1840)])
        fx.approval("L", D2)
        rc, out, st = fx.run(D3)
        a, eps = st["accounts"]["L"], fx.episodes()
        check("G10 ngày duyệt không đọc được positions ⇒ VẪN thử phiên kế và MỞ ở đó; điểm vào = mốc "
              "sớm nhất có thể (D1), mốc kia (D2) giữ làm điểm vào phụ",
              len(eps) == 1 and eps[0]["opened_date"] == D3 and eps[0]["entry_ref_date"] == D1
              and eps[0]["entry_ref_alt_dates"] == [D2]
              and D2 in eps[0]["evidence"]["unreadable_sessions"], f"{eps} {a['notes']}")
        e = a["brakes"]["episode"]
        check("G10b phanh đo theo điểm vào XẤU hơn: −15% từ D2 (không phải −6,5% từ D1) ⇒ BREACH, có ghi chú",
              e["status"] == m.BREACH and abs(e["value"] - (93.5 / 110 - 1)) < 1e-9
              and "XẤU hơn" in e.get("note", "") and any("XẤU hơn" in n for n in a["notes"]), f"{e}")
    finally:
        fx.close()
    # --- B5: bản duyệt CÓ THẬT nhưng vị thế tới muộn ⇒ lý do KHÔNG được nói "không có bản duyệt"
    fx = Fx()
    try:
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 99e6), (D3, 98e6), (D4, 97e6)])
        fx.positions("111", D4, [("BBB", 500, 1840)])
        fx.approval("L", D1)
        rc, out, st = fx.run(D4)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G10c có vị thế vay, có bản duyệt D1 (vị thế tới muộn hơn phiên kế) ⇒ lý do ĐỌC từ bản "
              "duyệt: nêu ngày + vì sao chưa mở, không nói 'không có bản duyệt' (§29)",
              e["status"] == m.UNMEASURABLE and f"bản duyệt margin đọc được tới phiên này: {D1}" in e["reason"]
              and "ý định" in e["reason"] and "không thấy bản duyệt" not in e["reason"], e["reason"])
    finally:
        fx.close()
    # --- không có bản duyệt nào ⇒ nói đúng thế; mở TAY
    fx = Fx()
    try:
        fx.account("L", "111")
        fx.navs_seq("L", [(D1, 100e6), (D2, 99e6), (D3, 84e6)])
        fx.positions("111", D2, [("BBB", 500, 1840)])
        fx.positions("111", D3, [("BBB", 500, "1840")])      # broker trả mã gói dạng CHUỖI
        rc, out, st = fx.run(D3)
        a = st["accounts"]["L"]
        check("G10d vị thế vay mà KHÔNG có bản duyệt nào ⇒ KHÔNG ĐO ĐƯỢC, nói đúng 'không thấy bản duyệt'; "
              "mã gói dạng chuỗi \"1840\" vẫn nhận ra (K11/§28 — không thành NO_EPISODE im lặng)",
              fx.episodes() == [] and a["brakes"]["episode"]["status"] == m.UNMEASURABLE
              and "không thấy bản duyệt margin nào" in a["brakes"]["episode"]["reason"]
              and "--open-episode" in a["brakes"]["episode"]["reason"], f"{a['brakes']['episode']}")
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D2)
        check("G11 mở tay thiếu --opened-by/--reason ⇒ từ chối", rc == 2 and fx.episodes() == [], out)
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D6,
                         "--opened-by", "u", "--reason", "r")
        check("G12 mở tay với ngày TƯƠNG LAI ⇒ từ chối", rc == 2 and fx.episodes() == [], out)
        n = len(fx.msgs())
        rc, out = fx.cli(f"{D3}T22:10:00", "--open-episode", "L", "--opened-date", D2,
                         "--opened-by", "user (fixture)", "--reason", "sao kê broker: giải ngân 06/10")
        eps = fx.episodes()
        check("G13 mở tay hợp lệ ⇒ ghi episode, điểm vào mặc định = chốt phiên trước ngày mở",
              rc == 0 and len(eps) == 1 and eps[0]["entry_ref_date"] == D1
              and eps[0]["evidence"]["manual"] is True and eps[0]["opened_by"] == "user (fixture)",
              f"{rc} {out} {eps}")
        check("G13b ...và gửi MỘT dòng báo lệnh tay (ai, lý do, trước/sau) vào kênh",
              len(fx.msgs()) == n + 1 and "LỆNH TAY --open-episode" in fx.msgs()[-1]
              and "user (fixture)" in fx.msgs()[-1] and "sao kê broker" in fx.msgs()[-1]
              and "trước:" in fx.msgs()[-1] and "sau:" in fx.msgs()[-1], fx.msgs()[-1])
        rc, out, st = fx.run(D3, now=f"{D3}T22:20:00")
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G14 ...và phanh −15% đo được ngay: −16% ⇒ BREACH", e["status"] == m.BREACH
              and abs(e["value"] - (-0.16)) < 1e-9, f"{e}")
        check("G14b lượt đo kế NÊU lệnh tay trong notes + trong tin",
              any("LỆNH TAY --open-episode" in x for x in st["accounts"]["L"]["notes"])
              and "LỆNH TAY --open-episode" in fx.msgs()[-1], f"{st['accounts']['L']['notes']}")
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
    for last, lever_at_close, want in ((86e6, True, m.OK), (85e6, False, m.BREACH)):
        fx = _episode_fx(last)
        try:
            fx.run(D4)
            if not lever_at_close:                           # đã tất toán ngay trong ngày đóng
                fx.positions("111", D5, [("AAA", 100, 1841)])
            rc, out = fx.cli(f"{D5}T15:30:00", "--close-episode", "L", *close)   # TRƯỚC lượt 22:05
            rc, out, st = fx.run(D5)
            e = st["accounts"]["L"]["brakes"]["episode"]
            check(f"G21 đóng episode TRƯỚC lượt tối của chính ngày đóng ⇒ phiên đó VẪN đo với episode "
                  f"({want}, không phải NO_EPISODE xanh)", e["status"] == want
                  and abs(e["value"] - (last / 100e6 - 1)) < 1e-9 and "đóng tay" in e.get("note", ""),
                  f"{e}")
        finally:
            fx.close()
    fx = _episode_fx(95e6)
    try:
        fx.run(D5)
        fx.cli(f"{D5}T22:30:00", "--close-episode", "L", *close)
        fx.nav("L", D6, 94e6)
        fx.positions("111", D6, [("BBB", 500, 1840)])
        rc, out, st = fx.run(D6)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("G21b phiên SAU ngày đóng: episode hết hiệu lực; còn vị thế vay ⇒ kêu 'không có episode'",
              e["status"] == m.UNMEASURABLE and "KHÔNG có episode nào đang mở" in e["reason"], f"{e}")
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
        check("X14 ops_health: account nổ ⇒ rc=3 (tới được vận hành); account chạm phanh ⇒ rc=5",
              hrc == 3 and "MONITOR LỖI" in line and hrc_b == 5, f"{hrc} {line} | {hrc_b}")
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
        check("N16 phiên = mốc đầu chuỗi ⇒ lý do nói đúng việc đó", "ĐẦU TIÊN" in r, r)
    finally:
        fx.close()


def t_total_basis():
    print("[I/R56] cơ sở đo = NAV TOÀN TÀI KHOẢN cho mọi account · lọc account (§12)")
    fx = Fx()
    try:
        fx.account("S", "111")
        fx.account("Z", "222", excluded=("XXX",))            # có khai excluded_tickers
        fx.account("Y", "333")                               # cùng chuỗi NAV với Z, không khai
        fx.navs_seq("S", [(D1, 101e6), (D2, 100e6), (D3, 99.5e6)])
        for a in ("Z", "Y"):
            fx.navs_seq(a, [(D1, 100e6), (D2, 99.8e6), (D3, 90.4e6)])
        fx.positions("222", D3, [("XXX", 10000, 1841)])      # Z đang giữ mã "loại trừ"
        rc, out, st = fx.run(D3)
        s, z, y = (st["accounts"][k] for k in "SZY")
        check("I1 account khai excluded_tickers VẪN đo trên NAV tổng: −9,42% ⇒ BREACH (không còn "
              "'phần bot quản lý' che)", z["brakes"]["daily"]["status"] == m.BREACH
              and abs(z["brakes"]["daily"]["value"] - (90.4 / 99.8 - 1)) < 1e-12, f"{z['brakes']['daily']}")
        check("I2 excluded_tickers KHÔNG ảnh hưởng gì: Z và Y (cùng chuỗi NAV) ra y hệt ba phanh",
              z["brakes"] == y["brakes"] and z["unit_price"] == y["unit_price"], f"{z['brakes']} {y['brakes']}")
        check("I3 hai account khác chuỗi cho hai kết quả KHÁC nhau (§12)",
              s["unit_price"] != z["unit_price"] and s["overall"] == m.OK and z["overall"] == m.BREACH,
              f"{s['overall']} {z['overall']}")
        check("I4 status/tin ghi cơ sở đo 'NAV toàn tài khoản'; không còn khoá/câu chữ của phần quản lý",
              st["basis"] == m.BASIS_VI and "basis" not in z and "excluded_value" not in z
              and all("NAV toàn tài khoản" in t and "phần bot quản lý" not in t for t in fx.msgs())
              and len(fx.msgs()) == 2, f"{sorted(z)} {len(fx.msgs())}")
        check("I5 state-dir không còn file nào của bộ máy mã loại trừ",
              not [f for f in os.listdir(fx.state) if "excluded" in f or "sleeve" in f],
              f"{os.listdir(fx.state)}")
        src = read(os.path.join(BIN, "nav_loss_brake_monitor.py"))
        check("I6 mã nguồn không còn đọc excluded_tickers / active_nav / corp_action_daily",
              '"excluded_tickers"' not in src and "active_nav_" not in src
              and "corp_action_daily" not in src and "managed_sleeve" not in src)
    finally:
        fx.close()
    fx = _episode_fx(95e6)                                   # L có episode (điểm vào D1)
    try:
        fx.account("M", "222")
        fx.navs_seq("M", [(D1, 100e6), (D2, 99e6), (D3, 98e6), (D4, 97e6), (D5, 96e6)])
        rc, out, st = fx.run(D5)
        check("R56 episode của account L KHÔNG phủ sang account M (§12): L đo −5% OK, M 'không có episode'",
              brakes(st, "L")["episode"] == m.OK and brakes(st, "M")["episode"] == m.NO_EPISODE,
              f"{brakes(st, 'L')} {brakes(st, 'M')}")
    finally:
        fx.close()


def t_quiet_rule():
    print("[luật giảm tin] chỉ cờ ước tính + cách ngưỡng > 2,0pp ⇒ không đẩy tin; đúng biên 2,00 ⇒ đẩy")
    check("T0 hằng số có tên = 2,0 điểm %", m.QUIET_ESTIMATE_MARGIN_PP == 2.0)
    raw = []
    for name, cap, start, nav, quiet in (
            ("T1 −3,00% (cách ngưỡng ĐÚNG 2,00pp) ⇒ VẪN đẩy", 100e6, 100e6, 97e6, False),
            # vốn 700tr, NAV 1.100 → 1.067tr: đúng −3% nhưng phép chia cho −0,02999999999999991
            ("T1b −3,00% mà dấu phẩy động cho khoảng cách 2,000000000000009pp ⇒ VẪN đẩy",
             700e6, 1100e6, 1067e6, False),
            ("T2 −2,9999% (cách 2,0001pp) ⇒ KHÔNG đẩy", 100e6, 100e6, 97_000_100, True)):
        fx = Fx()
        try:
            fx.account("A", "111", capital=cap)
            fx.navs_seq("A", [(D1, start), (D2, start)])
            fx.nav("A", D3, nav, est=True)
            rc, out, st = fx.run(D3)
            a = st["accounts"]["A"]
            b = a["brakes"]["daily"]
            raw.append(b["distance_pp"])
            check(name, b["status"] == m.UNMEASURABLE and bool(b.get("quiet")) == quiet
                  and len(fx.msgs()) == (0 if quiet else 1) and rc == 1
                  and ("daily" in a["alert"]["suppressed"]) == quiet, f"{b} msgs={len(fx.msgs())}")
            if quiet:
                check("T2b ca không đẩy: status vẫn KHÔNG ĐO ĐƯỢC kèm số tạm tính + lý do cờ ước tính",
                      a["overall"] == m.UNMEASURABLE and b["value"] is not None
                      and "nav_is_estimate" in b["reason"] and a["alert"]["sent_now"] is False, f"{b}")
                hrc, line = fx.health("A", f"{D4}T08:20:00")
                check("T2c dòng kiểm sáng: rc=1 (không đỏ), có số tạm tính + nói rõ không đẩy tin tối",
                      hrc == 1 and "tạm tính -3,00%" in line and "KHÔNG đẩy tin tối" in line
                      and "ĐÃ" not in line, f"{hrc} {line}")
                log = [json.loads(x) for x in read(os.path.join(fx.state, "run_log.jsonl")).splitlines()]
                check("T2d nhật ký lượt chạy ghi account bị giảm tin", log[-1]["suppressed"] == ["A"]
                      and log[-1]["sent"] == [], f"{log[-1]}")
        finally:
            fx.close()
    check("T1d ca T1b thật sự cho khoảng cách NHỈNH hơn 2,0 nếu so trần (EPS của luật có việc)",
          raw[1] > 2.0 and raw[0] <= 2.0, f"{raw}")
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 100e6)])
        fx.nav("A", D3, 99e6, est=True, ts="04:49:59")       # ước tính + chụp lệch giờ
        rc, out, st = fx.run(D3)
        b = st["accounts"]["A"]["brakes"]["daily"]
        check("T3 có THÊM lý do khác ngoài cờ ước tính ⇒ đẩy như cũ dù số xa ngưỡng",
              not b.get("quiet") and len(fx.msgs()) == 1 and "04:49:59" in b["reason"], f"{b}")
        fx.nav("A", D3, 99e6, est=True)
        fx.nav("A", D4, 98.5e6)                              # dòng phiên sạch, MỐC SO là dòng ước tính
        n = len(fx.msgs())
        rc, out, st = fx.run(D4)
        b = st["accounts"]["A"]["brakes"]
        check("T4 cờ ước tính ở dòng MỐC SO, số xa ngưỡng ⇒ không đẩy; lỗ từ đỉnh đo được bình thường",
              b["daily"]["status"] == m.UNMEASURABLE and b["daily"].get("quiet") is True
              and b["drawdown"]["status"] == m.OK and len(fx.msgs()) == n and rc == 1, f"{b['daily']}")
        fx.nav("A", D5, 98e6, est=True)
        fx.nav("A", D5, 75.5e6, est=True)                    # từ đỉnh −24,5%: cách ngưỡng 0,5pp
        rc, out, st = fx.run(D5)
        b = st["accounts"]["A"]["brakes"]
        check("T5 tạm tính vượt ngưỡng (ngày) ⇒ tin đỏ; phanh lỗ-từ-đỉnh cách ngưỡng 0,5pp ⇒ không quiet",
              b["daily"]["status"] == m.BREACH_PROV and b["drawdown"]["status"] == m.UNMEASURABLE
              and not b["drawdown"].get("quiet") and len(fx.msgs()) == n + 1, f"{b}")
    finally:
        fx.close()
    fx = _episode_fx(86.5e6)
    try:
        fx.nav("L", D5, 86.5e6, est=True)                    # episode −13,5% (cách 1,5pp); ngày −2,26%
        rc, out, st = fx.run(D5)
        a = st["accounts"]["L"]
        check("T6 mỗi phanh xét RIÊNG: episode cách ngưỡng 1,5pp ⇒ đẩy; lỗ một ngày cách 2,74pp ⇒ quiet",
              a["brakes"]["episode"]["status"] == m.UNMEASURABLE and not a["brakes"]["episode"].get("quiet")
              and a["brakes"]["daily"].get("quiet") is True and len(fx.msgs()) == 1
              and a["alert"]["keys"] == [f"L|{D5}|episode|UNMEASURABLE"]
              and a["alert"]["suppressed"] == ["daily", "drawdown"],
              f"{a['alert']} {a['brakes']}")
    finally:
        fx.close()


def t_human_actions():
    print("[K2] lệnh tay ghi state: kiểm bản duyệt · một dòng vào kênh · hiện ở lượt đo kế")
    by = ["--acked-by", "user (fixture)", "--reason", "cùng episode"]
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
        n = len(fx.msgs())
        rc, out, st = fx.run(D4)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("HA0 bản duyệt mới chưa ack, số xấu nhất −0,8% (xa ngưỡng) ⇒ KHÔNG ĐO ĐƯỢC và VẪN đẩy tin "
              "(không thuộc luật giảm tin)", e["status"] == m.UNMEASURABLE and not e.get("quiet")
              and len(fx.msgs()) == n + 1, f"{e}")
        rc, out = fx.cli(f"{D5}T10:00:00", "--ack-approval", "L", "--approval-date", "2027-01-01", *by)
        check("HA1 ack bản duyệt ngày TƯƠNG LAI ⇒ từ chối rc=2, không ghi gì",
              rc == 2 and "TƯƠNG LAI" in out and fx.episodes()[0]["acked_approvals"] == [], f"{rc} {out}")
        rc, out = fx.cli(f"{D5}T10:00:00", "--ack-approval", "L", "--approval-date", D3, *by)
        check("HA2 ack bản duyệt KHÔNG TỒN TẠI ⇒ từ chối rc=1, nêu các bản đang có, không ghi gì",
              rc == 1 and "không có bản duyệt margin" in out and D4 in out
              and fx.episodes()[0]["acked_approvals"] == []
              and not os.path.exists(os.path.join(fx.state, "human_actions.jsonl")), f"{rc} {out}")
        n = len(fx.msgs())
        rc, out = fx.cli(f"{D5}T10:00:00", "--ack-approval", "L", "--approval-date", D4, *by)
        t = fx.msgs()[-1]
        check("HA3 ack hợp lệ ⇒ rc=0 + ĐÚNG MỘT dòng vào kênh: lệnh, ai, lý do, trước/sau",
              rc == 0 and len(fx.msgs()) == n + 1 and t.startswith("📝") and "--ack-approval" in t
              and "user (fixture)" in t and "cùng episode" in t and "trước:" in t and D4 in t, t)
        acts = [json.loads(x) for x in read(os.path.join(fx.state, "human_actions.jsonl")).splitlines()]
        check("HA4 sổ lệnh tay có một dòng (ai, lý do, trước/sau)", len(acts) == 1
              and acts[0]["cmd"] == "--ack-approval" and acts[0]["by"] == "user (fixture)"
              and acts[0]["account"] == "L", f"{acts}")
        fx.account("M", "222")
        fx.navs_seq("M", [(D4, 100e6), (D5, 100e6), (D6, 100e6)])
        rc, out, st = fx.run(D5)
        check("HA5 lượt đo kế NÊU lệnh tay trong notes (kể cả khi mọi phanh xanh) và in ra log",
              any("LỆNH TAY --ack-approval" in x for x in st["accounts"]["L"]["notes"])
              and "LỆNH TAY --ack-approval" in out, f"{st['accounts']['L']['notes']}")
        check("HA5b ...account KHÁC trong cùng lượt đo KHÔNG thấy lệnh tay của L (§12)",
              st["accounts"]["M"]["notes"] == [], f"{st['accounts']['M']['notes']}")
        rc, out, st = fx.run(D6)
        check("HA6 lượt đo phiên SAU nữa không nhắc lại",
              not any("LỆNH TAY" in x for x in st["accounts"]["L"]["notes"] + st["accounts"]["M"]["notes"]),
              f"{st['accounts']['L']['notes']}")
        with open(os.path.join(fx.state, "human_actions.jsonl"), "a", encoding="utf-8") as f:
            f.write('{"at": "2026-')
        rc, out, st = fx.run(D6)
        check("HA7 sổ lệnh tay cụt ⇒ notes nói đúng lỗi đọc được (§29), không coi là 'không có lệnh'",
              any("sổ lệnh tay" in x and "JSONDecodeError" in x for x in st["accounts"]["L"]["notes"]),
              f"{st['accounts']['L']['notes']}")
    finally:
        fx.close()
    fx = _episode_fx(95e6)
    try:
        fx.run(D5)
        os.environ.pop(m.SINK_ENV, None)                     # không sink + state giả ⇒ gửi bị từ chối
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(fx.args(f"{D5}T22:30:00") + ["--close-episode", "L", "--closed-by", "u",
                                                     "--reason", "r"])
        check("HA8 lệnh tay ghi được state nhưng KHÔNG gửi được dòng báo ⇒ rc=3 + ❌ nói rõ; sổ lệnh "
              "tay vẫn có để lượt đo kế nêu", rc == 3 and "KHÔNG gửi được dòng báo lệnh tay" in buf.getvalue()
              and fx.episodes()[0]["closed_date"] == D5
              and os.path.exists(os.path.join(fx.state, "human_actions.jsonl")), f"{rc} {buf.getvalue()}")
    finally:
        fx.close()


def t_k_items():
    print("[K3/K4/K5/K11] --now trên state sống · state-dir không ghi được · sink trên state sống · "
          "positions thiếu khoá · giờ chụp điểm vào · ghi chú đỉnh")
    class LiveStateCtx(m.Ctx):               # thư mục vẫn là thư mục TẠM, chỉ cờ state sống bật
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.state_is_live = True

    fx = Fx()
    try:
        fx.account("A", "111")
        fx.navs_seq("A", [(D1, 100e6), (D2, 70e6)])
        real_ctx, m.Ctx = m.Ctx, LiveStateCtx
        try:
            rc, out = fx.cli(f"{D2}T22:00:00")
            rc2, out2 = fx.cli(f"{D2}T22:00:00", "--close-episode", "A", "--closed-by", "x",
                               "--reason", "y")
            rc3, out3 = fx.cli(f"{D2}T22:00:00", "--health-line", "--account", "A")
        finally:
            m.Ctx = real_ctx
        check("K3 --now khi state là state SỐNG ⇒ từ chối rc=2 trước khi làm bất cứ gì (lượt đo, lệnh "
              "tay, health-line): không status, không tin",
              rc == rc2 == rc3 == 2 and (out + out2 + out3).count("TỪ CHỐI --now") == 3
              and not os.path.exists(os.path.join(fx.state, "status.json")) and fx.msgs() == [],
              f"{rc} {rc2} {rc3} {out}")
        blocker = os.path.join(fx.root, "blk")
        open(blocker, "w").close()                           # state-dir nằm DƯỚI một file ⇒ không tạo được
        argv = ["--data-root", fx.data, "--state-dir", os.path.join(blocker, "st"), "--secrets",
                fx.secrets, "--now", f"{D2}T22:00:00"]
        os.environ[m.SINK_ENV] = fx.sink
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = m.main(argv)
            rc2 = m.main(argv + ["--close-episode", "A", "--closed-by", "u", "--reason", "r"])
        check("K4 state-dir không tạo/khoá được ⇒ rc=3 (không traceback, không rc=1) + MỘT tin 'monitor "
              "lỗi' kèm lỗi thật", rc == 3 and len(fx.msgs()) == 1
              and "MONITOR PHANH LỖ NAV LỖI" in fx.msgs()[0] and "NotADirectoryError" in fx.msgs()[0],
              f"{rc} {fx.msgs()} {buf.getvalue()[-300:]}")
        check("K4b lệnh tay gặp cùng lỗi ⇒ rc=3 + ❌ nêu lỗi, không traceback",
              rc2 == 3 and "NotADirectoryError" in buf.getvalue(), f"{rc2}")
        # --- K5: sink trên state SỐNG không được tính là đã gửi
        ctx = m.Ctx(fx.data, fx.state, fx.secrets)
        ctx.is_live = True
        out = m.send_once(ctx, ["A|x|daily|BREACH"], lambda: "tin thử K5")
        check("K5 tin đi vào sink khi state là state SỐNG ⇒ KHÔNG tính đã gửi: sent_now=False, có "
              "send_error, KHÔNG ghi khoá chống-trùng, status ghi rõ sink",
              out["sent_now"] is False and "sink" in (out["send_error"] or "")
              and out["sink"] == fx.sink and not os.path.exists(ctx.sent_path), f"{out}")
        # --- K11: bản ghi positions cuối cùng không có khoá payload.positions
        with open(os.path.join(fx.exec, f"dnse_raw_{D2}.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": f"{D2}T19:20:00", "kind": "positions", "account_no": "111",
                                "payload": {"error": "timeout"}}) + "\n")
        rc, out, st = fx.run(D2)
        e = st["accounts"]["A"]["brakes"]["episode"]
        check("K11a bản ghi positions thiếu khoá payload.positions ⇒ 'không đọc được' (KHÔNG coi là "
              "không giữ gì), nêu khoá đọc được", e["status"] == m.UNMEASURABLE
              and "KHÔNG có danh sách payload.positions" in e["reason"] and "error" in e["reason"], f"{e}")
    finally:
        fx.close()
    check("K11b mã gói vay chuẩn hoá trước khi so (§28)", m._pkg_id("1840") == 1840
          and m._pkg_id(1840.0) == 1840 and m._pkg_id(" 1840 ") == 1840 and m._pkg_id(None) is None
          and m._pkg_id("1840.5") is None and m._pkg_id(1841) == 1841)
    fx = _episode_fx(95e6)
    try:
        fx.nav("L", D1, 100e6, ts="04:49:59")                # dòng ĐIỂM VÀO chụp lệch giờ
        rc, out, st = fx.run(D5)
        e = st["accounts"]["L"]["brakes"]["episode"]
        check("K11c dòng điểm vào episode không phải giá chốt ⇒ phanh episode chỉ TẠM TÍNH, nêu giờ chụp",
              e["status"] == m.UNMEASURABLE and "04:49:59" in e["reason"] and e["value"] is not None
              and not e.get("quiet"), f"{e}")
    finally:
        fx.close()
    fx = Fx()
    try:
        fx.account("A", "111")
        fx.nav("A", D1, 110e6, est=True)                     # ĐỈNH là dòng ước tính
        fx.navs_seq("A", [(D2, 100e6), (D3, 99e6)])
        rc, out, st = fx.run(D3)
        d = st["accounts"]["A"]["brakes"]["drawdown"]
        hrc, line = fx.health("A", f"{D4}T08:20:00")
        check("K11d ghi chú 'đỉnh chưa phải giá chốt' ĐƯỢC IN ra (log lượt chạy + dòng kiểm sáng)",
              d["status"] == m.OK and "đỉnh chưa phải giá chốt" in out
              and "đỉnh chưa phải giá chốt" in line and "nav_is_estimate" in line, f"{out} | {line}")
    finally:
        fx.close()


def main():
    os.environ.pop(m.SINK_ENV, None)
    for t in (t_thresholds, t_threshold_parsing, t_daily_edges, t_float_edge, t_dd_edges, t_episode,
              t_flows, t_fail_loud, t_close_capture, t_provisional_breach, t_total_basis,
              t_quiet_rule, t_episode_guards, t_human_actions, t_k_items, t_idempotent,
              t_monitor_failures, t_health_and_clock):
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
