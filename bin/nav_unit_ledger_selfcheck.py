#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho SỔ ĐƠN VỊ QUỸ (`nav_unit_ledger.py`) và các số `nav_period_returns.py` lấy từ nó
(chính sách "tài khoản = quỹ mở", user duyệt 2026-10-10, bước 1/4).

Phủ: (A) hai fixture ĐÓNG BĂNG chép từ dữ liệu thật (asof 2026-10-09 và 2026-10-13) ⇒ đúng số đã công bố;
(B) ca tổng hợp có dòng tiền — luật gán D1 (ngày + giờ + `balance_ts`), đáp án tính tay hoặc dựng
từ tỉ suất biết trước; (C) sổ trên đĩa chỉ-ghi-thêm, khoá, ghi nguyên tử, từ chối thư mục dữ liệu
thật; (D) lãi/lỗ VND, tỉ suất gia quyền theo tiền, chặn quy năm; (E) module dòng tiền + cổng 5%;
(F) CLI của nhánh + cổng báo cáo trong sandbox (sổ lệch KHÔNG được tắt cổng).

Chạy: python3 mike/bin/nav_unit_ledger_selfcheck.py
      env -u TZ python3 … ;  TZ=America/New_York python3 …      (§16 — phải PASS y nguyên)
Không đọc mạng, không gọi BQ. Mọi file ghi ra nằm ở tempdir; KHÔNG tạo/sửa file nào trong data/.
"""
import datetime
import fcntl
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

import account_cash_flows as acf                      # noqa: E402
import nav_period_returns as npr                      # noqa: E402
import nav_unit_ledger as nul                         # noqa: E402

D = datetime.date
N = 0
NAV_FIELDS = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
              "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
INC = {"SpaceX": {"inception_date": "2026-07-01", "starting_capital": 1_000_000_000}}
REPORT = D(2026, 7, 10)
FIXTURE = BIN / "fixtures" / "nav_unit_ledger_asof_20261009"
# Hai giờ dùng suốt file, với NAV chụp 19:10 cùng ngày (mặc định của Env.write_nav):
IN_SESSION = "10:00"        # trước giờ đóng cửa 14:45 ⇒ luật gán ra "bod" trên chính phiên đó
AFTER_CLOSE = "16:00"       # sau đóng cửa, trước lúc chụp ⇒ "eod" trên chính phiên đó


def ok(cond, msg):
    global N
    if not cond:
        raise AssertionError(msg)
    N += 1


def raises(exc_type, fn, msg, needle=None):
    """`fn()` PHẢI raise đúng `exc_type` (và thông điệp chứa `needle`) — nếu không là assertion."""
    try:
        fn()
    except exc_type as exc:
        ok(needle is None or needle in str(exc), f"{msg}: thông điệp thiếu {needle!r}: {exc}")
        return str(exc)
    except Exception as exc:                                    # noqa: BLE001
        raise AssertionError(f"{msg}: phải raise {exc_type.__name__}, lại raise "
                             f"{type(exc).__name__}: {exc}") from exc
    raise AssertionError(f"{msg}: phải raise {exc_type.__name__}")


def must(fn, label):
    """`fn()` KHÔNG được raise: đầu vào hợp lệ mà bị từ chối cũng là sai, phải thành assertion."""
    try:
        return fn()
    except AssertionError:
        raise
    except Exception as exc:                                    # noqa: BLE001
        raise AssertionError(f"{label}: đầu vào hợp lệ không được raise, được "
                             f"{type(exc).__name__}: {exc}") from exc


class Env:
    """Một bộ nav_history + cash_flows + inception + thư mục sổ, tất cả trong tempdir."""

    def __init__(self, tmp, name, nav, flows):
        self.dir = Path(tmp) / name
        self.dir.mkdir()
        self.ledger_dir = self.dir / "ledger"
        self.ledger_dir.mkdir()
        self.flows_path = str(self.dir / "account_cash_flows.json")
        self.inc_path = str(self.dir / "account_inception.json")
        Path(self.inc_path).write_text(json.dumps(INC), encoding="utf-8")
        self.write_nav(nav)
        self.write_flows(flows)

    def write_nav(self, nav):
        """nav: [(YYYY-MM-DD, nav) | (YYYY-MM-DD, nav, is_estimate, balance_ts)]. `is_estimate`
        ghi nguyên văn (kể cả ""); `balance_ts` None ⇒ <ngày>T19:10:00, "" ⇒ ô trống."""
        lines = [",".join(NAV_FIELDS)]
        for rec in nav:
            d, v = rec[0], rec[1]
            est = rec[2] if len(rec) > 2 else False
            ts = rec[3] if len(rec) > 3 and rec[3] is not None else f"{d}T19:10:00"
            lines.append(f"{d},{v!r},0,0,0,0,0,{ts},0,{est},live")
        (self.dir / "nav_history_SpaceX.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_flows(self, flows):
        Path(self.flows_path).write_text(json.dumps({"SpaceX": flows}), encoding="utf-8")

    @property
    def sealed(self):
        return self.ledger_dir / "nav_unit_ledger_SpaceX.csv"

    def rows(self):
        return nul.load_nav_history("SpaceX", str(self.dir))

    def ledger_raw(self):
        return nul.build_account_ledger("SpaceX", str(self.dir), self.inc_path, self.flows_path)

    def returns_raw(self, report_date=REPORT, today=None):
        return npr.compute_period_returns(
            "SpaceX", report_date, self.rows(), nul.load_inception("SpaceX", self.inc_path),
            acf.load_flows("SpaceX", self.flows_path, require_file=True, today=today))

    def ledger(self):
        return must(self.ledger_raw, f"dựng sổ {self.dir.name}")

    def returns(self, report_date=REPORT, today=None):
        return must(lambda: self.returns_raw(report_date, today), f"tính kỳ {self.dir.name}")

    def cli_args(self, *extra, ledger_dir=True):
        return ([sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX",
                 "--nav-dir", str(self.dir), "--inception-path", self.inc_path,
                 "--flows-path", self.flows_path]
                + (["--ledger-dir", str(self.ledger_dir)] if ledger_dir else []) + list(extra))

    def cli(self, *extra, ledger_dir=True):
        return subprocess.run(self.cli_args(*extra, ledger_dir=ledger_dir),
                              capture_output=True, text=True)


def dep(date, amount, time_ict=IN_SESSION, timing=None):
    rec = {"date": date, "amount_vnd": amount, "kind": "deposit" if amount > 0 else "withdraw",
           "evidence": "selfcheck fixture"}
    if time_ict:
        rec["time_ict"] = time_ict
    if timing:
        rec["timing"] = timing
    return rec


def check_invariant(ledger, label):
    """Bất biến của sổ: đơn vị × giá = NAV từng dòng (lệch <= 1 đồng), giá và đơn vị > 0."""
    for row in ledger:
        gap = abs(row["units"] * row["unit_price"] - row["nav"])
        ok(gap <= 1.0, f"{label} {row['date']}: đơn vị×giá lệch NAV {gap:.6f} đồng (> 1)")
        ok(row["units"] > 0 and row["unit_price"] > 0, f"{label} {row['date']}: đơn vị/giá <= 0")


def by_date(ledger):
    return {r["date"]: r for r in ledger}


def pcts(r):
    return (r["inception"]["return_pct"], r["wtd"]["return_pct"], r["mtd"]["return_pct"])


# ------------------------------------------------------------------ A. số đã công bố
PUBLISHED = {"SpaceX": (-1.33, 1.024, 0.519), "ZaloPay": (-4.907, -1.162, -2.01)}   # asof 2026-10-09
FROZEN_EST = {"SpaceX": 8, "ZaloPay": 6}        # số dòng nav_is_estimate=True trong fixture
FIXTURE_1013 = BIN / "fixtures" / "nav_unit_ledger_asof_20261013"
PUBLISHED_1013 = {"SpaceX": (-2.091, -0.771, -0.256), "ZaloPay": (-6.199, -1.359, -3.342)}  # asof 2026-10-13


def _no_flow_checks(account, rows, inception, flows, label):
    f0, n0 = npr._inception_baseline(rows, inception)
    ledger, info = must(lambda: nul.build_ledger(rows, flows, f0, n0), f"{label}: dựng sổ")
    check_invariant(ledger, label)
    ok(ledger[0]["date"] == f0 and ledger[0]["unit_price"] == 10_000.0
       and ledger[0]["units"] == n0 / 10_000.0,
       f"{label}: dòng khởi điểm phải là {f0}, giá 10.000, đơn vị = vốn/10.000")
    ok(len(ledger) == 1 + sum(1 for r in rows if r[0] > f0),
       f"{label}: mỗi dòng nav_history sau khởi điểm phải có đúng một dòng sổ")
    ok(sum(r["nav_is_estimate"] for r in ledger) == sum(r.is_estimate for r in rows if r[0] > f0),
       f"{label}: cờ nav_is_estimate phải được mang theo đủ")
    ok(all(r["units"] == ledger[0]["units"] for r in ledger),
       f"{label}: không có dòng tiền ⇒ số đơn vị không được đổi")
    for d, nav in rows:
        if d < f0:
            continue
        r = must(lambda: npr.compute_period_returns(account, d, rows, inception, flows),
                 f"{label} {d}")
        p = r["inception"]
        ok(p["return_pct"] == round((nav / n0 - 1) * 100, 3),
           f"{label} {d}: không dòng tiền ⇒ tỉ số giá đơn vị phải == nav1/nav0 − 1")
        ok(p["mwr_pct"] == p["return_pct"] and p["pnl_vnd"] == nav - n0,
           f"{label} {d}: không dòng tiền ⇒ mwr == twr và pnl == nav1 − nav0")
        ok(p["nav1"] == nav and p["nav0"] == n0 and p["unit_price0"] == 10_000.0
           and abs(p["unit_price1"] - nav / n0 * 10_000.0) < 1e-4,
           f"{label} {d}: nav0/nav1/unit_price0/unit_price1 sai: {p}")
        ok(r["pending_flows"] == [] and r["dropped_flows"] == [],
           f"{label} {d}: không dòng tiền ⇒ pending_flows/dropped_flows phải là list rỗng")
        for per in ("inception", "wtd", "mtd"):
            ok(r[per]["annualized_return_pct"] is None
               and r[per]["mwr_annualized_pct"] is None
               and "không quy năm" in r[per].get("annualized_note", ""),
               f"{label} {d} {per}: kỳ {r[per]['days']} ngày < 365 phải KHÔNG quy năm")
    return ledger


def part_a_published():
    # N6: gốc cây tìm theo marker `wc_env.sh` (không đếm cấp thư mục) — hai module cùng một gốc.
    import wc_paths
    root = wc_paths.find_wc_root(str(BIN / "nav_unit_ledger.py"))
    ok(nul.WC_ROOT == acf.WC_ROOT == root and (Path(root) / "wc_env.sh").is_file()
       and nul.NAV_HISTORY_DIR == os.path.join(root, "data", "execution_logs")
       and acf.FLOWS_PATH == os.path.join(root, "data", "account_cash_flows.json"),
       f"N6: WC_ROOT của nav_unit_ledger/account_cash_flows phải là gốc có wc_env.sh ({root}), "
       f"được {nul.WC_ROOT} / {acf.WC_ROOT}")
    # --- A1. Fixture ĐÓNG BĂNG (chép từ data/ ngày 2026-10-11, dòng cuối 2026-10-09): neo "ra
    # đúng số đã công bố" KHÔNG phụ thuộc data/ sống ⇒ đính chính hợp lệ về sau không làm đỏ, và
    # không điều kiện nào bỏ qua được khối này.
    inc_path = str(FIXTURE / "account_inception.json")
    ledgers = {}
    for account, want in PUBLISHED.items():
        rows = nul.load_nav_history(account, str(FIXTURE))
        inception = nul.load_inception(account, inc_path)
        ok(rows[-1][0] == D(2026, 10, 9), f"fixture {account}: dòng cuối phải 2026-10-09")
        ok(sum(r.is_estimate for r in rows) == FROZEN_EST[account],
           f"fixture {account}: phải có đúng {FROZEN_EST[account]} dòng nav_is_estimate=True "
           f"(ô trống KHÔNG phải ước tính), được {sum(r.is_estimate for r in rows)}")
        ok(all(r.balance_ts for r in rows), f"fixture {account}: mọi dòng phải mang balance_ts")
        got = pcts(must(lambda: npr.compute_period_returns(account, D(2026, 10, 9), rows,
                                                           inception, []), f"fixture {account}"))
        ok(got == want, f"fixture {account} asof 2026-10-09 phải ra số đã công bố {want}, được {got}")
        ledgers[account] = _no_flow_checks(account, rows, inception, [], f"fixture {account}")
    sx, zp = ledgers["SpaceX"], ledgers["ZaloPay"]
    ok([r["unit_price"] for r in sx[-5:]] != [r["unit_price"] for r in zp[-5:]],
       "§12: sổ SpaceX và ZaloPay phải KHÁC nhau (giống nhau = đọc chung không lọc account)")

    # --- A2. Lịch sử DÀI HƠN, cũng ĐÓNG BĂNG (chép từ data/ ngày 2026-10-14, dòng cuối
    # 2026-10-13, kèm sổ dòng tiền lúc đó). Trước 2026-10-14 khối này đọc data/ SỐNG ⇒ số
    # assertion đổi theo mỗi dòng nav_history mới (4716 ↔ 4736 ↔ 4754) và selfcheck đỏ ở cây
    # không có data/ — sổ đã chốt cần test tất định (arch-review bước 2, G1).
    # Chỉ bỏ qua khối "nav1/nav0" khi fixture ĐÃ CÓ dòng tiền amount != 0, và bỏ qua thì IN RÕ.
    inc13 = str(FIXTURE_1013 / "account_inception.json")
    flows13 = str(FIXTURE_1013 / "account_cash_flows.json")
    for account, want in PUBLISHED_1013.items():
        rows = nul.load_nav_history(account, str(FIXTURE_1013))
        inception = nul.load_inception(account, inc13)
        flows = must(lambda: acf.load_flows(account, flows_path=flows13, require_file=True),
                     f"fixture 10-13 {account}: đọc flows")
        ok(rows[-1][0] == D(2026, 10, 13), f"fixture 10-13 {account}: dòng cuối phải 2026-10-13")
        got = pcts(must(lambda: npr.compute_period_returns(account, D(2026, 10, 13), rows,
                                                           inception, flows), f"fixture 10-13 {account}"))
        ok(got == want, f"fixture 10-13 {account} asof 2026-10-13 phải ra số đã công bố {want}, được {got}")
        f0, _ = npr._inception_baseline(rows, inception)
        real = [f for f in flows if f["amount_vnd"] and f["date"] > f0]
        if real:
            print(f"BỎ QUA khối 'không dòng tiền ⇒ nav1/nav0' trên fixture 10-13 của {account}: "
                  f"đã có {len(real)} dòng tiền amount != 0 sau {f0} (đầu tiên {real[0]['date']} "
                  f"{real[0]['amount_vnd']:+,.0f} VND). Neo số công bố vẫn chạy trên fixture 10-09.")
            check_invariant(must(lambda: nul.build_ledger(
                rows, flows, *npr._inception_baseline(rows, inception)), f"fixture 10-13 {account}")[0],
                f"fixture 10-13 {account}")
            continue
        _no_flow_checks(account, rows, inception, flows, f"fixture 10-13 {account}")


# ------------------------------------------------------------------ B. ca tổng hợp có dòng tiền
def part_b_synthetic(tmp):
    # --- B1. Nạp 200tr vào 1 tỷ đúng ngày thị trường +2%. Hai chuỗi NAV, mỗi chuỗi là sự thật
    # của MỘT thời điểm tiền vào; khai giờ kia phải ra số KHÁC, đúng số tính tay.
    #   chuỗi E (tiền vào SAU khi chốt): 1.000 × 1,02 + 200 = 1.220 tr
    #   chuỗi B (tiền vào TRONG phiên):  (1.000 + 200) × 1,02 = 1.224 tr
    nav_e = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
             ("2026-07-06", 1_220_000_000.0)]
    nav_b = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_224_000_000.0),
             ("2026-07-06", 1_224_000_000.0)]
    hand = {("E", AFTER_CLOSE): 2.0,                             # (1220 − 200)/1000 − 1
            ("E", IN_SESSION): round((1220 / 1200 - 1) * 100, 3),    # 1,667
            ("B", IN_SESSION): 2.0,                              # 1224/(1000 + 200) − 1
            ("B", AFTER_CLOSE): 2.4}                             # (1224 − 200)/1000 − 1
    ok(hand[("E", IN_SESSION)] == 1.667, "sanity đáp án tính tay")
    envs = {}
    for (series, t), want in hand.items():
        env = Env(tmp, f"b1_{series}_{t.replace(':', '')}", nav_e if series == "E" else nav_b,
                  [dep("2026-07-03", 200_000_000, t)])
        envs[(series, t)] = env
        got = env.returns()["inception"]["return_pct"]
        ok(got == want, f"B1 chuỗi {series}, tiền vào {t}: tính tay {want}%, được {got}%")
        check_invariant(env.ledger()[0], f"B1 {series}/{t}")
    row = by_date(envs[("E", AFTER_CLOSE)].ledger()[0])[D(2026, 7, 3)]
    ok(row["unit_price"] == 10_200.0, f"B1 sau đóng cửa: giá chốt 07-03 phải 10.200, được {row['unit_price']}")
    ok(abs(row["units_issued"] - 200_000_000 / 10_200) < 1e-6 and row["flow_eod_vnd"] == 200e6
       and row["flow_bod_vnd"] == 0.0,
       f"B1 sau đóng cửa: phát hành 200tr/10.200 = 19.607,843 đơn vị, được {row['units_issued']}")
    row = by_date(envs[("B", IN_SESSION)].ledger()[0])[D(2026, 7, 3)]
    ok(abs(row["units_issued"] - 20_000.0) < 1e-6 and row["unit_price"] == 10_200.0
       and row["flow_bod_vnd"] == 200e6 and row["flow_eod_vnd"] == 0.0,
       f"B1 trong phiên: phát hành 200tr/10.000 = 20.000 đơn vị ở giá phiên trước, được {row}")
    r = envs[("E", AFTER_CLOSE)].returns()["inception"]
    ok("net_flow_vnd" in r and "cash_flows" in r,
       f"B1: kỳ có dòng tiền phải xuất net_flow_vnd + cash_flows, được khoá {sorted(r)}")
    ok(r["pnl_vnd"] == 20_000_000.0 and r["net_flow_vnd"] == 200_000_000.0,
       f"B1: lãi/lỗ VND = 1.220 − 1.000 − 200 = 20tr, được {r['pnl_vnd']}")
    ok(r["nav1"] == 1_220_000_000.0 and r["unit_price0"] == 10_000.0 and r["unit_price1"] == 10_200.0,
       f"B1: nav1/unit_price0/unit_price1 phải 1.220tr/10.000/10.200, được {r}")
    cf = r["cash_flows"]
    ok(len(cf) == 1 and {"amount_vnd", "date", "evidence", "kind", "timing"} <= set(cf[0]),
       f"hợp đồng cash_flows phải giữ đủ 5 khoá cũ, được {cf}")
    ok(cf[0]["timing"] == "eod" and cf[0]["session_date"] == "2026-07-03"
       and cf[0]["time_ict"] == AFTER_CLOSE and cf[0]["date"] == "2026-07-03",
       f"B1: cash_flows phải nêu quy ước SUY RA (eod) + phiên được gán, được {cf}")
    full = envs[("E", AFTER_CLOSE)].returns(D(2026, 7, 3))
    ok(isinstance(full.get("day"), dict), f"B1: đã có phiên sau mốc khởi điểm thì `day` phải là một kỳ, được {full.get('day')!r}")
    ok(full["day"]["from_date"] == "2026-07-02" and full["day"]["to_date"] == "2026-07-03"
       and full["day"]["return_pct"] == 2.0 and full["day"].get("net_flow_vnd") == 200e6
       and full["day"]["pnl_vnd"] == 20_000_000.0 and full["day"]["unit_price_ratio"] == 1.02,
       f"B1: kỳ `day` = phiên gần nhất so với dòng sổ liền trước (+2,0%, lãi 20tr, nạp 200tr), được {full['day']}")
    nxt = envs[("E", AFTER_CLOSE)].returns(D(2026, 7, 6))
    ok(nxt["day"]["from_date"] == "2026-07-03" and nxt["day"]["return_pct"] == 0.0
       and "net_flow_vnd" not in nxt["day"] and nxt["inception"]["unit_price_ratio"] == 1.02,
       f"B1: phiên sau (thị trường đứng yên) ⇒ `day` 0,0%, không còn dòng tiền; được {nxt['day']}")
    only_inc = must(lambda: npr.compute_period_returns("SpaceX", D(2026, 7, 1), [nul.NavRow(D(2026, 7, 1), 1e9)],
                                                       INC["SpaceX"], []), "B1 báo cáo ĐÚNG ngày inception")
    ok(only_inc["day"] is None and only_inc["inception"]["return_pct"] == 0.0,
       f"B1: chưa có phiên nào sau mốc khởi điểm ⇒ `day` là None, được {only_inc['day']}")
    cf = envs[("B", IN_SESSION)].returns()["inception"]["cash_flows"]
    ok(cf[0]["timing"] == "bod" and cf[0]["session_date"] == "2026-07-03",
       f"B1: tiền vào trong phiên phải được ghi là bod, được {cf}")
    for key in ("from_date", "to_date", "nav0", "nav1", "return_pct"):
        ok(key in r, f"hợp đồng JSON cũ thiếu khoá {key}")
    # Biên giờ đóng cửa 14:45 (SESSION_CLOSE_ICT): 14:44 và 14:44:59 còn trong phiên; 14:45 là sau.
    for t, want_timing in (("14:44", "bod"), ("14:44:59", "bod"), ("14:45", "eod"), ("14:45:00", "eod")):
        env = Env(tmp, f"b1_close_{t.replace(':', '')}", nav_e, [dep("2026-07-03", 200_000_000, t)])
        got = by_date(env.ledger()[0])[D(2026, 7, 3)]["flows"][0]["timing"]
        ok(got == want_timing, f"B1 biên đóng cửa: tiền {t} phải là {want_timing}, được {got}")

    # --- B2. Giá đơn vị KHÔNG đổi vì dòng tiền: nạp/rút ngày thị trường đứng yên.
    flat = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_210_000_000.0),
            ("2026-07-06", 910_000_000.0), ("2026-07-07", 919_100_000.0)]
    for t in (AFTER_CLOSE, "09:30"):
        env = Env(tmp, f"b2_{t.replace(':', '')}", flat, [dep("2026-07-03", 200_000_000, t),
                                                          dep("2026-07-06", -300_000_000, t)])
        ledger = env.ledger()[0]
        check_invariant(ledger, f"B2 {t}")
        led = by_date(ledger)
        for d in (D(2026, 7, 3), D(2026, 7, 6)):
            ok(abs(led[d]["unit_price"] - 10_100.0) < 1e-6,
               f"B2 {t} {d}: thị trường đứng yên ⇒ giá phải giữ 10.100, được {led[d]['unit_price']}")
        ok(led[D(2026, 7, 3)]["units_issued"] > 0 > led[D(2026, 7, 6)]["units_issued"],
           f"B2 {t}: nạp phải PHÁT HÀNH (+), rút phải HUỶ (−) đơn vị")
        r = env.returns()["inception"]
        # 1.010/1.000 × (đứng yên) × (đứng yên) × 919,1/910 = +2,01%
        ok(r["return_pct"] == 2.01, f"B2 {t}: rút một phần — tính tay +2,01%, được {r['return_pct']}")
        ok(r["net_flow_vnd"] == -100_000_000.0 and r["pnl_vnd"] == 19_100_000.0,
           f"B2 {t}: pnl = 919,1 − 1.000 − (−100) = 19,1tr, được {r['pnl_vnd']}")

    # --- B3. Rút GẦN HẾT (còn 1tr) rồi +5% trên phần còn lại; rút HẾT ⇒ từ chối.
    near = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_000_000.0), ("2026-07-06", 1_050_000.0)]
    env = Env(tmp, "b3_near", near, [dep("2026-07-03", -999_000_000, AFTER_CLOSE)])
    ledger = env.ledger()[0]
    check_invariant(ledger, "B3")
    r = env.returns()["inception"]
    ok(r["return_pct"] == 5.0 and abs(ledger[-1]["units"] - 100.0) < 1e-6,
       f"B3 rút gần hết: tỉ suất phải +5,0% trên 100 đơn vị còn lại, được {r['return_pct']} / "
       f"{ledger[-1]['units']}")
    ok(r["pnl_vnd"] == 50_000.0, f"B3: pnl = 1,05 − 1.000 + 999 = 0,05tr, được {r['pnl_vnd']}")
    env = Env(tmp, "b3_all", near, [dep("2026-07-03", -1_000_000_000, "09:00")])
    raises(ValueError, env.ledger_raw, "B3 rút đầu ngày hết đơn vị", "rút đầu ngày")
    env = Env(tmp, "b3_all_eod", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 0.0)],
              [dep("2026-07-03", -1_000_000_000, AFTER_CLOSE)])
    raises(ValueError, env.ledger_raw, "B3 rút cuối ngày hết đơn vị", "rút cuối ngày")
    env = Env(tmp, "b3_neg", near, [dep("2026-07-03", 2_000_000, AFTER_CLOSE)])
    raises(ValueError, env.ledger_raw, "B3 nav − tiền eod < 0", "không tính được giá đơn vị")
    # nav ĐÚNG BẰNG tiền nạp sau đóng cửa ⇒ giá = 0: phải là lời từ chối có nghĩa, không phải chia 0.
    env = Env(tmp, "b3_zero", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 200_000_000.0)],
              [dep("2026-07-03", 200_000_000, AFTER_CLOSE)])
    raises(ValueError, env.ledger_raw, "B3 nav − tiền eod = 0", "không tính được giá đơn vị")
    raises(ValueError, lambda: nul.build_ledger([nul.NavRow(D(2026, 7, 2), 1e9)], [], D(2026, 7, 1), 0.0),
           "B3 vốn khởi điểm 0", "vốn khởi điểm phải > 0")

    # --- B4. Nạp ĐÚNG ngày inception: không phải dòng tiền (đã nằm trong vốn khởi điểm) ⇒ bị loại,
    # nhưng PHẢI hiện ở dropped_flows.
    plain = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_020_000_000.0),
             ("2026-07-06", 1_030_000_000.0)]
    base = Env(tmp, "b4_base", plain, [])
    env = Env(tmp, "b4_inc", plain, [dep("2026-07-01", 500_000_000)])
    ledger, info = env.ledger()
    ok(len(info["dropped"]) == 1 and info["dropped"][0]["amount_vnd"] == 500e6,
       f"B4: flow ngày inception phải nằm trong info['dropped'], được {info}")
    r = env.returns()
    ok({k: r[k] for k in ("inception", "wtd", "mtd")} == {k: base.returns()[k] for k in ("inception", "wtd", "mtd")}
       and r["inception"]["return_pct"] == 3.0,
       "B4: flow ngày inception không được đổi bất kỳ số nào")
    ok("net_flow_vnd" not in r["inception"], "B4: flow bị loại không được hiện trong kỳ")
    ok(len(r["dropped_flows"]) == 1 and r["dropped_flows"][0]["amount_vnd"] == 500e6
       and r["dropped_flows"][0]["date"] == "2026-07-01" and "2026-07-01" in r["dropped_flows"][0]["reason"]
       and r["pending_flows"] == [],
       f"B4: JSON công bố phải nêu flow bị loại ở dropped_flows kèm lý do, được {r['dropped_flows']}")
    p = env.cli(ledger_dir=False)
    ok(p.returncode == 0 and "bỏ flow 2026-07-01" in p.stderr and "+500,000,000" in p.stderr,
       f"B4: CLI sổ phải báo flow bị loại ra stderr, được {p.stderr[:300]}")
    # Dòng nav_history ĐÚNG ngày inception (khi đã có starting_capital) không phải một ngày của
    # sổ: mốc khởi điểm là vốn khởi điểm, không phải snapshot ngày đó — nhưng cờ ước tính của
    # ngày đó thì mang sang dòng khởi điểm.
    env = Env(tmp, "b4_row", [("2026-07-01", 999_000_000.0, True)] + plain, [])
    ledger = env.ledger()[0]
    ok(len(ledger) == 4 and ledger[0]["nav"] == 1_000_000_000.0 and ledger[0]["unit_price"] == 10_000.0,
       f"B4: dòng nav ngày inception không được thay mốc khởi điểm, được {ledger[0]}")
    ok(ledger[0]["nav_is_estimate"] is True and base.ledger()[0][0]["nav_is_estimate"] is False,
       "B4: cờ nav_is_estimate của dòng nav ngày inception phải vào dòng khởi điểm của sổ")
    ok(env.returns()["inception"]["return_pct"] == 3.0, "B4: tỉ suất từ đầu vẫn tính trên vốn khởi điểm")

    # --- B5. Ba dòng tiền CÙNG phiên: cộng theo từng quy ước, bod trước eod sau.
    #   07-03: 09:20 +100 (bod), 16:00 +200 và 16:30 −50 (eod)
    #   ⇒ r = (1.282,2 − 150)/(1.010 + 100) − 1 = +2% ⇒ cả kỳ 1,01 × 1,02 − 1 = +3,02%
    nav5 = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_282_200_000.0),
            ("2026-07-06", 1_282_200_000.0)]
    env = Env(tmp, "b5", nav5, [dep("2026-07-03", 200_000_000, "16:00"), dep("2026-07-03", -50_000_000, "16:30"),
                                dep("2026-07-03", 100_000_000, "09:20")])
    ledger = env.ledger()[0]
    check_invariant(ledger, "B5")
    row = by_date(ledger)[D(2026, 7, 3)]
    ok(row["flow_bod_vnd"] == 100e6 and row["flow_eod_vnd"] == 150e6,
       f"B5: bod 100tr, eod ròng 150tr, được {row['flow_bod_vnd']}/{row['flow_eod_vnd']}")
    want = round((1.01 * (1_282_200_000.0 - 150e6) / (1_010_000_000.0 + 100e6) - 1) * 100, 3)
    r = env.returns()["inception"]
    ok(want == 3.02 and r["return_pct"] == want, f"B5: tính tay {want}%, được {r['return_pct']}%")
    ok(r["net_flow_vnd"] == 250e6 and len(r["cash_flows"]) == 3,
       f"B5: phải công khai đủ 3 bản ghi, ròng 250tr, được {r.get('net_flow_vnd')}")
    ok([c["timing"] for c in r["cash_flows"]] == ["bod", "eod", "eod"]
       and [c["time_ict"] for c in r["cash_flows"]] == ["09:20", "16:00", "16:30"],
       f"B5: cash_flows phải theo thứ tự giờ, mỗi bản ghi đúng quy ước, được {r['cash_flows']}")

    # --- B5b. Dòng tiền ĐÚNG ngày mốc đầu kỳ (WTD: thứ Sáu tuần trước) thuộc kỳ TRƯỚC, không
    # thuộc kỳ này: giá chốt hôm đó đã là giá sau giao dịch.
    #   07-03 (thứ Sáu) sau đóng cửa +200 ; tuần 07-06…07-10: 1.220 → 1.244,4 = +2,0%
    env = Env(tmp, "b5b", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
                           ("2026-07-06", 1_232_200_000.0), ("2026-07-07", 1_244_400_000.0)],
              [dep("2026-07-03", 200_000_000, AFTER_CLOSE)])
    r = env.returns(D(2026, 7, 7))
    ok(r["wtd"]["from_date"] == "2026-07-03" and r["wtd"]["return_pct"] == 2.0
       and "net_flow_vnd" not in r["wtd"] and r["wtd"]["pnl_vnd"] == 24_400_000.0
       and r["wtd"]["mwr_pct"] == 2.0,
       f"B5b: WTD không được tính dòng tiền của ngày mốc đầu kỳ, được {r['wtd']}")
    ok(r["wtd"]["unit_price0"] == 10_200.0 and r["wtd"]["unit_price1"] == 10_404.0
       and r["wtd"]["nav0"] == 1_220_000_000.0 and r["wtd"]["nav1"] == 1_244_400_000.0,
       f"B5b: WTD phải nêu đúng hai giá đơn vị 10.200 → 10.404 và hai NAV, được {r['wtd']}")
    ok(r["inception"]["net_flow_vnd"] == 200e6 and r["inception"]["return_pct"] == 4.04,
       f"B5b: kỳ từ đầu thì CÓ dòng tiền đó (1,02 × 1,02 − 1 = 4,04%), được {r['inception']}")

    # Có dòng NAV ngày CHỦ NHẬT (snapshot chạy cuối tuần) ⇒ mốc đầu tuần WTD là chính dòng đó.
    env = Env(tmp, "b5b_sun", [("2026-07-03", 1_000_000_000.0), ("2026-07-05", 1_010_000_000.0),
                               ("2026-07-07", 1_020_100_000.0)], [])
    r = env.returns(D(2026, 7, 7))
    ok(r["wtd"]["from_date"] == "2026-07-05" and r["wtd"]["return_pct"] == 1.0
       and r["mtd"]["from_date"] == "2026-07-01",
       f"B5b: WTD phải tính từ dòng cuối TRƯỚC thứ Hai (Chủ nhật 07-05), được {r['wtd']}")

    # --- B5c. Dòng tiền ĐÚNG ngày CUỐI kỳ (sau đóng cửa ngày báo cáo) thuộc kỳ này.
    #   07-03 +1% ; 07-06 +1% rồi nạp 202 sau đóng cửa ⇒ NAV 1.020,1 + 202 = 1.222,1 ; tỉ suất +2,01%
    env = Env(tmp, "b5c", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_010_000_000.0),
                           ("2026-07-06", 1_222_100_000.0)], [dep("2026-07-06", 202_000_000, AFTER_CLOSE)])
    r = env.returns(D(2026, 7, 6))["inception"]
    ok(r["to_date"] == "2026-07-06" and r["return_pct"] == 2.01 and r.get("net_flow_vnd") == 202e6
       and r["pnl_vnd"] == 20_100_000.0 and len(r.get("cash_flows", [])) == 1,
       f"B5c: dòng tiền đúng ngày cuối kỳ phải nằm trong kỳ (pnl 20,1tr, ròng 202tr), được {r}")
    ok(r["mwr_pct"] == 2.01, f"B5c: tiền vào cuối kỳ (w=0) ⇒ mwr = (1.222,1 − 202)/1.000 − 1 = 2,01%, được {r['mwr_pct']}")

    # --- B6. BẢNG K1 của arch-review: thị trường ĐỨNG YÊN, NAV chụp 19:10, tiền vào/ra 20:00
    # thứ Sáu 07-03 (SAU lần chụp). Sự thật: tỉ suất 0,0% mọi ngày. Bản cũ: −20% / −4% vĩnh viễn.
    k1_dep = [("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.2e9), ("2026-07-07", 1.2e9)]
    k1_wd = [("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 0.8e9), ("2026-07-07", 0.8e9)]
    for label, nav, flows in (
            ("nạp 200tr 20:00, chỉ khai ngày+giờ", k1_dep, [dep("2026-07-03", 200_000_000, "20:00")]),
            ("nạp 200tr 20:00, khai thêm timing='bod'", k1_dep, [dep("2026-07-03", 200_000_000, "20:00", "bod")]),
            ("rút 200tr 20:00, chỉ khai ngày+giờ", k1_wd, [dep("2026-07-03", -200_000_000, "20:00")]),
            ("rút 200tr 20:00:30 (có giây)", k1_wd, [dep("2026-07-03", -200_000_000, "20:00:30")])):
        env = Env(tmp, f"b6_k1_{len(list(Path(tmp).iterdir()))}", nav, flows)
        for rd in (D(2026, 7, 3), D(2026, 7, 6), D(2026, 7, 7)):
            r = env.returns(rd)
            ok(pcts(r) == (0.0, 0.0, 0.0) and r["inception"]["pnl_vnd"] == 0.0
               and r["inception"]["mwr_pct"] == 0.0,
               f"K1 [{label}] asof {rd}: thị trường đứng yên ⇒ mọi tỉ suất 0,0% và pnl 0, được "
               f"{pcts(r)} pnl {r['inception']['pnl_vnd']} mwr {r['inception']['mwr_pct']}")
        ledger = env.ledger()[0]
        ok(all(row["unit_price"] == 10_000.0 for row in ledger),
           f"K1 [{label}]: giá đơn vị phải giữ 10.000 mọi dòng, được {[row['unit_price'] for row in ledger]}")
        row = by_date(ledger)[D(2026, 7, 6)]
        ok(row["flow_bod_vnd"] == flows[0]["amount_vnd"] and row["flow_eod_vnd"] == 0.0
           and by_date(ledger)[D(2026, 7, 3)]["flows"] == [],
           f"K1 [{label}]: tiền sau lần chụp thứ Sáu phải vào phiên thứ Hai ở giá chốt thứ Sáu, được {row}")
    # Trước khi có dòng thứ Hai (báo cáo chạy tối thứ Sáu/cuối tuần): TREO, hiện ra, không lỗi.
    env = Env(tmp, "b6_k1_fri", k1_dep[:2], [dep("2026-07-03", 200_000_000, "20:00")])
    r = env.returns(D(2026, 7, 5))
    ok(pcts(r) == (0.0, 0.0, 0.0) and len(r["pending_flows"]) == 1
       and r["pending_flows"][0]["amount_vnd"] == 200e6 and r["pending_flows"][0]["time_ict"] == "20:00"
       and "TREO" in r["pending_flows"][0]["reason"] and "2026-07-03" in r["pending_flows"][0]["reason"]
       and "net_flow_vnd" not in r["inception"],
       f"K1: tiền chưa vào dòng NAV nào phải TREO và HIỆN ở pending_flows, được {r['pending_flows']}")
    p = env.cli(ledger_dir=False)
    ok(p.returncode == 0 and "TREO" in p.stderr and "2026-07-03 20:00" in p.stderr
       and "+200,000,000" in p.stderr,
       f"K1: CLI sổ phải báo dòng tiền treo ra stderr, được rc={p.returncode} {p.stderr[:300]}")
    # Khai timing KHÁC kết quả suy ra ⇒ từ chối, thông điệp nêu CẢ HAI.
    env = Env(tmp, "b6_k1_mismatch", k1_dep, [dep("2026-07-03", 200_000_000, "20:00", "eod")])
    msg = raises(acf.CashFlowError, env.ledger_raw, "K1 khai eod cho tiền 20:00", "timing='eod'")
    ok("'bod'" in msg and "2026-07-06" in msg, f"K1: thông điệp phải nêu quy ước suy ra + phiên, được {msg}")
    raises(acf.CashFlowError, env.returns_raw, "K1 nav_period_returns cũng phải từ chối", "timing='eod'")
    p = env.cli("--seal")
    ok(p.returncode == 1 and "timing='eod'" in p.stderr and not env.sealed.exists(),
       f"K1: CLI phải rc=1, nêu lỗi, KHÔNG tạo sổ; được rc={p.returncode} {p.stderr[:200]}")
    # Thiếu giờ ⇒ từ chối ở CẢ hai cửa: đọc file, và flow dựng tay đưa thẳng vào build_ledger.
    env = Env(tmp, "b6_k1_notime", k1_dep, [dep("2026-07-03", 200_000_000, None)])
    raises(acf.CashFlowError, env.ledger_raw, "K1 thiếu time_ict (đọc file)", "thiếu time_ict")
    bare = {"date": D(2026, 7, 3), "amount_vnd": 200e6, "kind": "deposit", "evidence": "x",
            "timing": "eod", "time_ict": None}
    raises(acf.CashFlowError, lambda: nul.build_ledger(env.rows(), [bare], D(2026, 7, 1), 1e9),
           "K1 thiếu time_ict (flow dựng tay)", "không có time_ict")

    # --- B7. Nạp CUỐI TUẦN (N3/N4): thứ Bảy 07-04 10:00 nạp 100tr, thị trường đứng yên.
    sat = [dep("2026-07-04", 100_000_000, "10:00")]
    fri = [("2026-07-02", 1e9), ("2026-07-03", 1e9)]
    env = Env(tmp, "b7_sun", fri, sat)
    r = env.returns(D(2026, 7, 5))
    ok(pcts(r) == (0.0, 0.0, 0.0) and len(r["pending_flows"]) == 1,
       f"B7: Chủ nhật — bản ghi thứ Bảy được nhận ngay, treo, không lỗi; được {r}")
    env = Env(tmp, "b7_mon", fri + [("2026-07-06", 1.1e9)], sat)
    r = env.returns(D(2026, 7, 6))
    ok(pcts(r) == (0.0, 0.0, 0.0) and r["pending_flows"] == []
       and r["inception"]["cash_flows"][0]["session_date"] == "2026-07-06"
       and r["inception"]["cash_flows"][0]["timing"] == "bod",
       f"B7: thứ Hai — tiền thứ Bảy vào phiên 07-06 ở giá chốt thứ Sáu, tỉ suất 0,0%; được {r['inception']}")
    rows_mon = env.rows()
    ok(must(lambda: acf.unexplained_nav_jumps(rows_mon, acf.load_flows("SpaceX", env.flows_path)),
            "B7 cổng 5%") == [],
       "B7: cổng 5% so theo PHIÊN ĐƯỢC GÁN — nạp thứ Bảy phải giải thích bước nhảy thứ Hai")
    jumps = acf.unexplained_nav_jumps(rows_mon, [])
    ok(len(jumps) == 1 and jumps[0]["date"] == D(2026, 7, 6) and abs(jumps[0]["change_pct"] - 10.0) < 1e-9,
       f"B7: không có bản ghi thì bước nhảy +10% thứ Hai phải bị bắt, được {jumps}")

    # --- B8. `balance_ts` thật không cố định 19:10 (đo trên 135 dòng thật).
    # (a) ZaloPay 2026-07-27: dòng ngày T chụp SÁNG T+1 09:15:15.
    late = [("2026-07-24", 1e9), ("2026-07-27", 1.2e9, False, "2026-07-28T09:15:15"), ("2026-07-28", 1.2e9)]
    for t_date, t in (("2026-07-27", "20:00"), ("2026-07-28", "08:00"), ("2026-07-28", "09:15:15")):
        env = Env(tmp, f"b8a_{t_date[-2:]}_{t.replace(':', '')}", late, [dep(t_date, 200_000_000, t)])
        row = by_date(env.ledger()[0])[D(2026, 7, 27)]
        ok(row["flow_eod_vnd"] == 200e6 and row["unit_price"] == 10_000.0
           and pcts(env.returns(D(2026, 7, 28))) == (0.0, 0.0, 0.0),
           f"B8a: tiền {t_date} {t} đã nằm trong dòng 07-27 (chụp 07-28T09:15:15) ⇒ eod trên 07-27, "
           f"tỉ suất 0,0%; được {row['flow_eod_vnd']}/{row['unit_price']}")
    late2 = [("2026-07-24", 1e9), ("2026-07-27", 1e9, False, "2026-07-28T09:15:15"), ("2026-07-28", 1.2e9)]
    env = Env(tmp, "b8a_after", late2, [dep("2026-07-28", 200_000_000, "09:15:16")])
    row = by_date(env.ledger()[0])[D(2026, 7, 28)]
    ok(row["flow_bod_vnd"] == 200e6 and pcts(env.returns(D(2026, 7, 28))) == (0.0, 0.0, 0.0),
       f"B8a: tiền 07-28 09:15:16 (1 giây SAU lần chụp của dòng 07-27) ⇒ bod trên 07-28, được {row}")
    # (b) 2026-08-24: dòng ngày T chụp 04:49 sáng T (TRƯỚC phiên).
    early = [("2026-08-21", 1e9), ("2026-08-24", 1e9, False, "2026-08-24T04:49:59"), ("2026-08-25", 1.2e9)]
    # Tiền tới TRONG phiên 08-24 (sau lần chụp, trước đóng cửa): cơ chế "dòng đầu tiên chụp sau"
    # sẽ cho giao dịch ở giá chốt 08-24 — trái luật (phải là giá chốt 08-21) ⇒ từ chối, nêu cách sửa.
    for t in ("04:50", "10:00", "14:44:59"):
        env = Env(tmp, f"b8b_in_{t.replace(':', '')}", early, [dep("2026-08-24", 200_000_000, t)])
        msg = raises(acf.CashFlowError, env.ledger_raw, f"B8b tiền {t} trong phiên có NAV chụp trước phiên",
                     "tới TRONG phiên")
        ok("2026-08-24T04:49:59" in msg and "daily_nav_snapshot.py" in msg,
           f"B8b: thông điệp phải trích balance_ts đã đọc + cách sửa, được {msg}")
        ok("dnse_raw_2026-08-24.jsonl có bản ghi balances SAU giờ đóng cửa" in msg and "--date 2026-08-24 --from-raw" in msg and "bước 3" in msg,
           f"B8b (L6): lối ra phải nói ĐÚNG điều kiện — chỉ chụp lại được khi dnse_raw có balances sau "
           f"đóng cửa, không thì thuộc bước 3; được {msg}")
        raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 8, 25)), f"B8b nav_period_returns ({t})",
               "tới TRONG phiên")
    # Tiền tới SAU đóng cửa 08-24 (hoặc trong phiên 08-25) ⇒ luật: giá chốt 08-24, tức bod trên
    # 08-25. Nhưng dòng 08-24 chụp 04:49 — TRƯỚC phiên — nên NAV của nó KHÔNG phải giá chốt 08-24
    # (thiếu biến động phiên 08-24): tiền mới sẽ hưởng oan biến động đó, sai giá vĩnh viễn ⇒ từ chối.
    for t_date, t in (("2026-08-24", "14:45"), ("2026-08-24", "20:00"), ("2026-08-25", "10:00")):
        env = Env(tmp, f"b8b_src_{t_date[-2:]}_{t.replace(':', '')}", early, [dep(t_date, 200_000_000, t)])
        msg = raises(acf.CashFlowError, env.ledger_raw,
                     f"B8b tiền {t_date} {t}: dòng giá nguồn 08-24 chụp trước đóng cửa", "không phải giá chốt")
        ok("2026-08-24T04:49:59" in msg and "phiên 2026-08-25" in msg and "daily_nav_snapshot.py" in msg,
           f"B8b: thông điệp phải trích balance_ts của dòng giá nguồn + phiên được gán + cách sửa, được {msg}")
        ok("dnse_raw_2026-08-24.jsonl có bản ghi balances SAU giờ đóng cửa" in msg and "--date 2026-08-24 --from-raw" in msg and "bước 3" in msg,
           f"B8b (L6): lối ra của dòng giá nguồn chụp sớm phải nói đúng điều kiện, được {msg}")
        raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 8, 25)),
               f"B8b nav_period_returns ({t_date} {t})", "không phải giá chốt")
    # Chốt dòng giá nguồn cũng phải chạy khi R là dòng THỨ HAI của chuỗi (dòng giá nguồn là dòng đầu).
    two = [nul.NavRow(D(2026, 8, 24), 1e9, balance_ts="2026-08-24T04:49:59"),
           nul.NavRow(D(2026, 8, 25), 1.2e9, balance_ts="2026-08-25T19:10:00")]
    f25 = dict(dep("2026-08-25", 200e6, "10:00"), date=D(2026, 8, 25), timing=None)
    raises(acf.CashFlowError, lambda: acf.attach_flows_to_rows(two, [f25]),
           "B8b dòng giá nguồn là dòng ĐẦU chuỗi, chụp trước đóng cửa",
           "không phải giá chốt (thiếu biến động phần còn lại của phiên)")
    # Con số: phiên 08-24 +10% (dòng 08-24 chụp 04:49 vẫn ghi 1.000), nạp 220 lúc 20:00, phiên 08-25
    # đứng yên ⇒ NAV 08-25 = 1.100 + 220 = 1.320. Sự thật: +10,0%. Nếu nhận bản ghi này (giá nguồn
    # 10.000 thay vì 11.000) thì ra 1.320/1.220 − 1 = +8,197% — vĩnh viễn. Phải là LỖI, không phải số.
    moved = [("2026-08-21", 1e9), ("2026-08-24", 1e9, False, "2026-08-24T04:49:59"), ("2026-08-25", 1.32e9)]
    env = Env(tmp, "b8b_src_moved", moved, [dep("2026-08-24", 220_000_000, "20:00")])
    raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 8, 25)),
           "B8b thị trường +10% phiên 08-24, dòng 08-24 chụp trước phiên", "không phải giá chốt")
    # Cùng kịch bản nhưng dòng 08-24 chụp ĐÚNG giờ đóng cửa (14:45:00, NAV 1.100) ⇒ nhận, +10,0%.
    closed = [("2026-08-21", 1e9), ("2026-08-24", 1.1e9, False, "2026-08-24T14:45:00"), ("2026-08-25", 1.32e9)]
    env = Env(tmp, "b8b_src_closed", closed, [dep("2026-08-24", 220_000_000, "20:00")])
    row = by_date(env.ledger()[0])[D(2026, 8, 25)]
    ok(row["flow_bod_vnd"] == 220e6 and row["unit_price"] == 11_000.0
       and env.returns(D(2026, 8, 25))["inception"]["return_pct"] == 10.0,
       f"B8b: dòng giá nguồn chụp đúng 14:45:00 ⇒ bod trên 08-25 ở giá 11.000, +10,0%; được {row}")
    # Tiền tới TRƯỚC lần chụp 04:49: đã nằm trong dòng 08-24 ⇒ bod trên 08-24 (giá nguồn = dòng 08-21).
    early_in = [("2026-08-21", 1e9), ("2026-08-24", 1.2e9, False, "2026-08-24T04:49:59"), ("2026-08-25", 1.2e9)]
    env = Env(tmp, "b8b_before_snap", early_in, [dep("2026-08-24", 200_000_000, "04:49")])
    raises(acf.CashFlowError, env.ledger_raw, "B8b cùng phút với lần chụp 04:49:59", "HH:MM:SS")
    for t in ("04:00", "04:49:59"):                 # trước lần chụp, và ĐÚNG giây chụp (= đã chứa)
        env = Env(tmp, f"b8b_before_snap_{t.replace(':', '')}", early_in, [dep("2026-08-24", 200_000_000, t)])
        row = by_date(env.ledger()[0])[D(2026, 8, 24)]
        ok(row["flow_bod_vnd"] == 200e6 and pcts(env.returns(D(2026, 8, 25))) == (0.0, 0.0, 0.0),
           f"B8b: tiền 08-24 {t} đã nằm trong dòng 08-24 (chụp 04:49:59) ⇒ bod trên 08-24, được {row}")
    # Dòng chụp trước phiên KHÔNG làm giá nguồn thì không cản: tiền 08-26 10:00 ⇒ bod trên 08-26,
    # giá nguồn là dòng 08-25 (chụp 19:10). (Thứ Bảy 08-22 ở dưới: giá nguồn là dòng 08-21.)
    early_far = early + [("2026-08-26", 1.4e9)]
    env = Env(tmp, "b8b_next", early_far, [dep("2026-08-26", 200_000_000, "10:00")])
    ok(by_date(env.ledger()[0])[D(2026, 8, 26)]["flow_bod_vnd"] == 200e6,
       "B8b: dòng 08-24 chụp sớm không được cản dòng tiền 08-26 (giá nguồn là dòng 08-25)")
    # eod không dùng dòng liền trước làm giá nguồn: tiền 08-25 16:00 ⇒ eod trên 08-25 (giá của chính
    # dòng 08-25, chụp 19:10) — dòng 08-24 chụp sớm không liên quan.
    env = Env(tmp, "b8b_eod_after_early", early, [dep("2026-08-25", 200_000_000, "16:00")])
    row = by_date(env.ledger()[0])[D(2026, 8, 25)]
    ok(row["flow_eod_vnd"] == 200e6 and pcts(env.returns(D(2026, 8, 25))) == (0.0, 0.0, 0.0),
       f"B8b: tiền 08-25 16:00 ⇒ eod trên 08-25, không bị dòng 08-24 chụp sớm cản; được {row}")
    early2 = [("2026-08-21", 1e9), ("2026-08-24", 1.2e9, False, "2026-08-24T04:49:59"), ("2026-08-25", 1.2e9)]
    env = Env(tmp, "b8b_sat", early2, [dep("2026-08-22", 200_000_000, "10:00")])
    row = by_date(env.ledger()[0])[D(2026, 8, 24)]
    ok(row["flow_bod_vnd"] == 200e6 and pcts(env.returns(D(2026, 8, 25))) == (0.0, 0.0, 0.0),
       f"B8b: tiền thứ Bảy 08-22 nằm trong dòng 08-24 (chụp 04:49) ⇒ bod trên 08-24, được {row}")
    # (c) Cùng PHÚT với lần chụp: không có giây ⇒ từ chối; có giây ⇒ so chính xác (bằng = đã chứa).
    snap = [("2026-07-02", 1e9), ("2026-07-03", 1.2e9, False, "2026-07-03T19:10:51"), ("2026-07-06", 1.2e9)]
    snap_out = [("2026-07-02", 1e9), ("2026-07-03", 1e9, False, "2026-07-03T19:10:51"), ("2026-07-06", 1.2e9)]
    env = Env(tmp, "b8c_min", snap, [dep("2026-07-03", 200_000_000, "19:10")])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B8c cùng phút, không giây", "HH:MM:SS")
    ok("2026-07-03T19:10:51" in msg, f"B8c: thông điệp phải trích balance_ts đã đọc, được {msg}")
    for t, nav, key, day in (("19:10:00", snap, "flow_eod_vnd", D(2026, 7, 3)),
                             ("19:10:50", snap, "flow_eod_vnd", D(2026, 7, 3)),
                             ("19:10:51", snap, "flow_eod_vnd", D(2026, 7, 3)),
                             ("19:10:52", snap_out, "flow_bod_vnd", D(2026, 7, 6)),
                             ("19:11", snap_out, "flow_bod_vnd", D(2026, 7, 6)),
                             ("19:09", snap, "flow_eod_vnd", D(2026, 7, 3))):
        env = Env(tmp, f"b8c_{t.replace(':', '')}", nav, [dep("2026-07-03", 200_000_000, t)])
        ledger = env.ledger()[0]
        ok(by_date(ledger)[day][key] == 200e6 and all(r["unit_price"] == 10_000.0 for r in ledger),
           f"B8c: tiền {t} so với lần chụp 19:10:51 phải vào {key} của {day}, được "
           f"{[(str(r['date']), r['flow_bod_vnd'], r['flow_eod_vnd']) for r in ledger]}")
    # (d) balance_ts thiếu / không đọc được ở dòng CẦN XÉT ⇒ từ chối, trích đúng giá trị đã đọc.
    for label, ts, needle in (("thiếu", "", "không có balance_ts (đọc được: None)"),
                              ("hỏng", "19h10 hôm qua", "'19h10 hôm qua'")):
        for which in ("R", "P"):
            nav = [("2026-07-02", 1e9, False, ts if which == "P" else None),
                   ("2026-07-03", 1.2e9, False, ts if which == "R" else None), ("2026-07-06", 1.2e9)]
            env = Env(tmp, f"b8d_{label}_{which}", nav, [dep("2026-07-03", 200_000_000, AFTER_CLOSE)])
            msg = raises(acf.CashFlowError, env.ledger_raw, f"B8d balance_ts {label} ở dòng {which}", needle)
            ok(("2026-07-03" if which == "R" else "2026-07-02") in msg,
               f"B8d: thông điệp phải nêu dòng nav_history nào, được {msg}")
            raises(acf.CashFlowError, env.returns_raw, f"B8d nav_period_returns ({label}/{which})", needle)
    # ...nhưng dòng KHÔNG cần xét (cũ hơn dòng liền trước ngày của flow) hỏng thì không cản.
    nav = [("2026-07-02", 1e9, False, ""), ("2026-07-03", 1e9), ("2026-07-06", 1.2e9), ("2026-07-07", 1.2e9)]
    env = Env(tmp, "b8d_far", nav, [dep("2026-07-06", 200_000_000, AFTER_CLOSE)])
    ok(by_date(env.ledger()[0])[D(2026, 7, 6)]["flow_eod_vnd"] == 200e6,
       "B8d: balance_ts trống ở dòng không cần xét không được cản việc gán")
    # (e) balance_ts có múi giờ: 12:10+00:00 = 19:10 ICT.
    env = Env(tmp, "b8e_tz", [("2026-07-02", 1e9), ("2026-07-03", 1.2e9, False, "2026-07-03T12:10:00+00:00"),
                              ("2026-07-06", 1.2e9)], [dep("2026-07-03", 200_000_000, AFTER_CLOSE)])
    ok(by_date(env.ledger()[0])[D(2026, 7, 3)]["flow_eod_vnd"] == 200e6,
       "B8e: balance_ts có múi giờ phải quy về ICT trước khi so (12:10Z = 19:10 ICT > 16:00)")

    # --- B9. nav_history trùng ngày / sai thứ tự (N2).
    dup_rows = [nul.NavRow(D(2026, 7, 2), 1e9, balance_ts="2026-07-02T19:10:00"),
                nul.NavRow(D(2026, 7, 3), 1.2e9, balance_ts="2026-07-03T19:10:00"),
                nul.NavRow(D(2026, 7, 3), 1.2e9, balance_ts="2026-07-03T19:20:00")]
    for fl in ([], [dict(dep("2026-07-03", 200e6, AFTER_CLOSE), date=D(2026, 7, 3), timing=None)]):
        msg = raises(ValueError, lambda: nul.build_ledger(dup_rows, fl, D(2026, 7, 1), 1e9),
                     "B9 hai dòng cùng ngày", "HAI dòng cùng ngày")
        ok("2026-07-03" in msg, f"B9: thông điệp phải nêu ngày trùng, được {msg}")
    dup_early = [nul.NavRow(D(2026, 7, 1), 1e9), nul.NavRow(D(2026, 7, 1), 1e9), nul.NavRow(D(2026, 7, 2), 1e9)]
    raises(ValueError, lambda: nul.build_ledger(dup_early, [], D(2026, 7, 1), 1e9),
           "B9 hai dòng cùng ngày ở mốc khởi điểm", "HAI dòng cùng ngày")
    raises(ValueError, lambda: nul.build_ledger(dup_rows[1::-1], [], D(2026, 7, 1), 1e9),
           "B9 dòng sai thứ tự", "sai thứ tự")
    raises(ValueError, lambda: acf.unexplained_nav_jumps(dup_rows, []), "B9 cổng 5% trên dòng trùng ngày",
           "HAI dòng cùng ngày")
    env = Env(tmp, "b9_dup_file", [("2026-07-02", 1e9), ("2026-07-03", 1.2e9), ("2026-07-03", 1.2e9)], [])
    raises(ValueError, env.ledger_raw, "B9 file nav_history trùng ngày", "HAI dòng cùng ngày")
    p = env.cli(ledger_dir=False)
    ok(p.returncode == 1 and "HAI dòng cùng ngày" in p.stderr, f"B9: CLI phải rc=1: {p.stderr[:200]}")
    # Dòng nav_history có ô `nav` TRỐNG ⇒ bỏ qua dòng đó (không sập, không thành một ngày của sổ).
    blank = Env(tmp, "b9_blank_nav", plain, [])
    with open(blank.dir / "nav_history_SpaceX.csv", "a", encoding="utf-8") as fh:
        fh.write("2026-07-07,,0,0,0,0,0,2026-07-07T19:10:00,0,False,live\n")
    ok([r["date"] for r in blank.ledger()[0]] == [r["date"] for r in base.ledger()[0]],
       "B9: dòng nav_history có ô nav trống phải bị bỏ qua, sổ y như không có dòng đó")
    # File nav_history KHÔNG theo thứ tự ngày (không trùng) ⇒ đọc vào được sắp lại, sổ y nguyên.
    shuffled = Env(tmp, "b9_shuffled", [plain[2], plain[0], plain[1]], [])
    ok([(r["date"], r["unit_price"]) for r in shuffled.ledger()[0]]
       == [(r["date"], r["unit_price"]) for r in base.ledger()[0]],
       "B9: file nav_history xáo thứ tự dòng phải cho đúng sổ như file xếp đúng")

    # --- B10. market_only: gán theo NGÀY (không cần giờ), không đổi số nào, giải thích bước nhảy.
    jump = [("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.1e9)]
    mo = {"date": "2026-07-04", "amount_vnd": 0, "kind": "market_only", "evidence": "VNINDEX +10%"}
    env = Env(tmp, "b10_mo", jump, [mo])
    row = by_date(env.ledger()[0])[D(2026, 7, 6)]
    ok(len(row["flows"]) == 1 and row["flows"][0]["timing"] is None and row["units_issued"] == 0.0
       and env.returns(D(2026, 7, 6))["inception"]["return_pct"] == 10.0,
       f"B10: market_only thứ Bảy gán vào phiên thứ Hai, không đổi đơn vị, tỉ suất vẫn +10%; được {row}")
    ok(acf.unexplained_nav_jumps(env.rows(), acf.load_flows("SpaceX", env.flows_path)) == [],
       "B10: market_only phải mở cổng 5% cho phiên được gán")
    env = Env(tmp, "b10_mo_timing", jump, [dict(mo, timing="eod")])
    raises(acf.CashFlowError, env.ledger_raw, "B10 market_only khai timing", "market_only")

    # --- B11. Đáp án BIẾT TRƯỚC: dựng chuỗi NAV từ tỉ suất ngày cho sẵn + dòng tiền ngẫu nhiên
    # (trong phiên và sau đóng cửa), tỉ số giá đơn vị phải trả lại đúng tích (1 + r_t).
    rng = random.Random(20261011)
    for case in range(60):
        nav, true_factor, navs, flows = 1_000_000_000.0, 1.0, [], []
        day = D(2026, 7, 1)
        for _ in range(12):
            day += datetime.timedelta(days=1)
            r_t = rng.uniform(-0.03, 0.03)
            f_bod = f_eod = 0.0
            if rng.random() < 0.4:
                f_bod = float(round(nav * rng.uniform(-0.3, 0.3)))
                flows.append(dep(day.isoformat(), f_bod, IN_SESSION))
            nav_after = (nav + f_bod) * (1 + r_t)
            if rng.random() < 0.4:
                f_eod = float(round(nav_after * rng.uniform(-0.3, 0.3)))
                flows.append(dep(day.isoformat(), f_eod, AFTER_CLOSE))
            nav = nav_after + f_eod
            true_factor *= 1 + r_t
            navs.append((day.isoformat(), nav))
        env = Env(tmp, f"b11_{case}", navs, [f for f in flows if f["amount_vnd"]])
        ledger = env.ledger()[0]
        check_invariant(ledger, f"B11#{case}")
        got = ledger[-1]["unit_price"] / 10_000.0
        ok(abs(got / true_factor - 1) < 1e-9,
           f"B11#{case}: tỉ số giá {got!r} phải == tích tỉ suất thật {true_factor!r}")
        rp = env.returns(D(2026, 7, 13))["inception"]["return_pct"]
        ok(abs(rp - (true_factor - 1) * 100) <= 0.00051,
           f"B11#{case}: return_pct {rp} lệch tỉ suất thật {(true_factor - 1) * 100:.6f}")

    # --- B12. Nhân đôi mọi dòng tiền của ca "chỉ nạp vào tiền mặt, thị trường đứng yên từ lần nạp
    # đầu" ⇒ tỉ suất gia quyền thời gian KHÔNG đổi (tiền vào trong phiên lẫn sau đóng cửa).
    for t in (AFTER_CLOSE, "09:10"):
        results = []
        for k in (1, 2):
            stock = [1_000_000_000.0 * f for f in (1.01, 1.01 * 0.995, 1.01 * 0.995, 1.01 * 0.995,
                                                   1.01 * 0.995)]
            cash = [0.0, 0.0, 150e6 * k, 150e6 * k, 400e6 * k]
            days = ["2026-07-02", "2026-07-03", "2026-07-06", "2026-07-07", "2026-07-08"]
            env = Env(tmp, f"b12_{t.replace(':', '')}_{k}", [(d, s + c) for d, s, c in zip(days, stock, cash)],
                      [dep("2026-07-06", 150e6 * k, t), dep("2026-07-08", 250e6 * k, t)])
            ledger = env.ledger()[0]
            check_invariant(ledger, f"B12 {t} k={k}")
            results.append((env.returns()["inception"]["return_pct"], ledger[-1]["unit_price"]))
        ok(results[0][0] == results[1][0] == 0.495,
           f"B12 {t}: nhân đôi dòng tiền phải giữ tỉ suất +0,495%, được {results}")
        ok(abs(results[0][1] - results[1][1]) < 1e-6,
           f"B12 {t}: giá đơn vị cuối phải như nhau, được {results}")

    # --- B13. Dòng cho giá phải là phiên đóng cửa GẦN NHẤT trước thời điểm tiền vào/ra (arch-review
    # lần 2, B1). Thứ Sáu 07-03 +10% (1.000 → 1.100), nạp 220 SAU đóng cửa 07-03, thứ Hai 07-06 đứng
    # yên ⇒ NAV 1.320. Sự thật: giá 10.000 → 11.000 → 11.000 = +10,0%. nav_history THIẾU dòng 07-03
    # thì dòng cho giá lùi về 07-02 (10.000) ⇒ +8,197%, không lỗi — phải là LỖI nêu tên phiên thiếu.
    ok(acf._is_session_day(D(2026, 7, 3)) and not acf._is_session_day(D(2026, 7, 4))
       and not acf._is_session_day(D(2026, 9, 1)) and not acf._is_session_day(D(2026, 9, 2))
       and acf._is_session_day(D(2026, 9, 3)),
       "B13 sanity lịch phiên: 07-03 có phiên; thứ Bảy 07-04, nghỉ bù 09-01, Quốc khánh 09-02 không; 09-03 có")
    full = [("2026-07-02", 1e9), ("2026-07-03", 1.32e9), ("2026-07-06", 1.32e9)]
    gap = [("2026-07-02", 1e9), ("2026-07-06", 1.32e9)]
    env = Env(tmp, "b13_full", full, [dep("2026-07-03", 220_000_000, AFTER_CLOSE)])
    ok(by_date(env.ledger()[0])[D(2026, 7, 3)]["unit_price"] == 11_000.0
       and env.returns(D(2026, 7, 6))["inception"]["return_pct"] == 10.0,
       "B13: đủ dòng phiên 07-03 ⇒ eod trên 07-03 ở giá 11.000, +10,0%")
    # (a) thiếu dòng phiên + tiền tới từ giờ đóng cửa phiên đó trở đi ⇒ từ chối, nêu đúng tên phiên.
    for t_date, t in (("2026-07-03", "14:45"), ("2026-07-03", AFTER_CLOSE), ("2026-07-04", "10:00"),
                      ("2026-07-06", "08:00")):
        env = Env(tmp, f"b13_gap_{t_date[-2:]}_{t.replace(':', '')}", gap, [dep(t_date, 220_000_000, t)])
        msg = raises(acf.CashFlowError, env.ledger_raw, f"B13a thiếu dòng 07-03, tiền {t_date} {t}",
                     "THIẾU dòng của phiên 2026-07-03")
        ok("dòng cho giá là 2026-07-02" in msg and "--date 2026-07-03 --from-raw" in msg,
           f"B13a: thông điệp phải nêu dòng cho giá đã dùng + lệnh backfill đúng ngày, được {msg}")
        raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 7, 6)), f"B13a nav_period_returns ({t_date} {t})",
               "THIẾU dòng của phiên 2026-07-03")
        raises(acf.CashFlowError,
               lambda: acf.unexplained_nav_jumps(env.rows(), acf.load_flows("SpaceX", env.flows_path)),
               f"B13a cổng 5% ({t_date} {t})", "THIẾU dòng của phiên 2026-07-03")
    env = Env(tmp, "b13_gap_many", [("2026-07-02", 1e9), ("2026-07-08", 1.32e9)],
              [dep("2026-07-07", 220_000_000, "20:00")])
    raises(acf.CashFlowError, env.ledger_raw, "B13a thiếu NHIỀU phiên (07-03, 07-06, 07-07)",
           "THIẾU dòng của phiên 2026-07-07")
    # eod cũng phải kiểm: dòng 07-06 chụp sáng 07-08, tiền 16:00 ngày 07-07 đã nằm trong dòng đó ⇒
    # "eod trên 07-06" — nhưng phiên 07-07 đã đóng cửa trước khi tiền vào mà không có dòng.
    env = Env(tmp, "b13_gap_eod", [("2026-07-02", 1e9), ("2026-07-03", 1e9),
                                   ("2026-07-06", 1.2e9, False, "2026-07-08T09:00:00"), ("2026-07-08", 1.2e9)],
              [dep("2026-07-07", 200_000_000, "16:00")])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B13a eod trên dòng cũ hơn phiên đóng cửa gần nhất",
                 "THIẾU dòng của phiên 2026-07-07")
    ok("dòng cho giá là 2026-07-06" in msg, f"B13a eod: dòng cho giá phải là dòng R, được {msg}")
    # (b) tiền tới TRONG chính phiên thiếu dòng ⇒ vẫn nhận: bod ở giá chốt phiên TRƯỚC (07-02), đúng luật.
    for t in ("10:00", "14:44:59"):
        env = Env(tmp, f"b13_in_{t.replace(':', '')}", gap, [dep("2026-07-03", 220_000_000, t)])
        row = by_date(env.ledger()[0])[D(2026, 7, 6)]
        ok(row["flow_bod_vnd"] == 220e6 and abs(row["units_issued"] - 22_000.0) < 1e-6
           and abs(row["unit_price"] - 1.32e9 / 122_000) < 1e-6,
           f"B13b: tiền 07-03 {t} (trong phiên thiếu dòng) ⇒ bod trên 07-06, phát hành ở giá 10.000; được {row}")
    # (c) ngày nghỉ lễ THẬT (31/08–02/09/2026) và cuối tuần không phải "phiên thiếu dòng".
    hol = [("2026-08-28", 1e9), ("2026-09-03", 1.2e9)]
    for t_date, t in (("2026-08-29", "16:00"), ("2026-08-31", "16:00"), ("2026-09-01", "10:00"),
                      ("2026-09-02", "16:00"), ("2026-09-03", "08:00")):
        env = Env(tmp, f"b13_hol_{t_date[-2:]}_{t.replace(':', '')}", hol, [dep(t_date, 200_000_000, t)])
        row = by_date(env.ledger()[0])[D(2026, 9, 3)]
        ok(row["flow_bod_vnd"] == 200e6 and row["unit_price"] == 10_000.0,
           f"B13c: tiền {t_date} {t} (nghỉ lễ/cuối tuần) ⇒ bod trên 09-03 ở giá chốt 08-28, không bị bắt oan; được {row}")
    # (d) R là dòng ĐẦU của sổ: dòng cho giá là mốc khởi điểm (07-01).
    first_gap = [("2026-07-03", 1.32e9), ("2026-07-06", 1.32e9)]             # thiếu dòng phiên 07-02
    env = Env(tmp, "b13_i0_gap", first_gap, [dep("2026-07-02", 220_000_000, AFTER_CLOSE)])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B13d thiếu dòng 07-02, tiền sau đóng cửa 07-02",
                 "THIẾU dòng của phiên 2026-07-02")
    ok("dòng cho giá là 2026-07-01" in msg, f"B13d: dòng cho giá phải là mốc khởi điểm, được {msg}")
    env = Env(tmp, "b13_i0_in", first_gap, [dep("2026-07-02", 220_000_000, "10:00")])
    ok(by_date(env.ledger()[0])[D(2026, 7, 3)]["flow_bod_vnd"] == 220e6,
       "B13d: tiền TRONG phiên 07-02 (thiếu dòng) ⇒ bod trên 07-03 ở giá mốc khởi điểm, vẫn nhận")
    f02 = dict(dep("2026-07-02", 220e6, AFTER_CLOSE), date=D(2026, 7, 2), timing=None)
    raises(acf.CashFlowError, lambda: acf.assign_flow(env.rows(), f02, D(2026, 7, 1)),
           "B13d assign_flow có baseline_date", "THIẾU dòng của phiên 2026-07-02")
    ok(must(lambda: acf.assign_flow(env.rows(), f02), "B13d không có mốc trước dòng đầu") == (0, "bod"),
       "B13d: không truyền baseline_date ⇒ không có dòng cho giá để so, riêng ca dòng đầu không kiểm")
    # (e) DỮ LIỆU THẬT (fixture đóng băng asof 2026-10-09): cả hai TK thiếu dòng phiên 2026-08-06.
    for account in PUBLISHED:
        real = nul.load_nav_history(account, str(FIXTURE))
        inc = nul.load_inception(account, str(FIXTURE / "account_inception.json"))
        have = {r[0] for r in real}
        ok(D(2026, 8, 6) not in have and {D(2026, 8, 5), D(2026, 8, 7)} <= have,
           f"B13e sanity ({account}): fixture phải thiếu đúng dòng 08-06 giữa 08-05 và 08-07")

        def with_flow(t, account=account, real=real, inc=inc):
            flow = dict(dep("2026-08-06", 100e6, t), date=D(2026, 8, 6), timing=None)
            return npr.compute_period_returns(account, D(2026, 10, 9), real, inc, [flow])
        raises(acf.CashFlowError, lambda: with_flow(AFTER_CLOSE),
               f"B13e ({account}) nạp 16:00 ngày 08-06 — phiên thiếu dòng", "THIẾU dòng của phiên 2026-08-06")
        cf = must(lambda: with_flow("10:00"), f"B13e ({account}) nạp 10:00 ngày 08-06")["inception"]["cash_flows"]
        ok(cf[0]["timing"] == "bod" and cf[0]["session_date"] == "2026-08-07",
           f"B13e ({account}): nạp 10:00 ngày 08-06 ⇒ bod trên 08-07 ở giá chốt 08-05, vẫn nhận; được {cf}")

    # --- B14. `balance_ts` phải tăng NGHIÊM NGẶT (arch-review lần 2, L1). Dòng 07-03 sửa tay bằng số
    # dư chụp sáng 07-07; nạp 20:00 ngày 07-06 từng bị gán eod trên 07-03 (giá sai, im lặng).
    edited = [("2026-07-02", 1e9), ("2026-07-03", 1e9, False, "2026-07-07T09:00:00"), ("2026-07-06", 1.2e9),
              ("2026-07-07", 1.2e9)]
    env = Env(tmp, "b14_edited", edited, [dep("2026-07-06", 200_000_000, "20:00")])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B14 balance_ts lùi", "balance_ts không tăng nghiêm ngặt")
    ok("2026-07-07T09:00:00" in msg and "2026-07-06T19:10:00" in msg and "2026-07-03" in msg,
       f"B14: thông điệp phải trích hai balance_ts đã đọc + ngày dòng, được {msg}")
    raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 7, 7)), "B14 nav_period_returns",
           "balance_ts không tăng nghiêm ngặt")
    raises(acf.CashFlowError, lambda: acf.unexplained_nav_jumps(env.rows(), acf.load_flows("SpaceX", env.flows_path)),
           "B14 cổng 5%", "balance_ts không tăng nghiêm ngặt")
    same = [("2026-07-02", 1e9), ("2026-07-03", 1e9, False, "2026-07-06T19:10:00"), ("2026-07-06", 1.2e9)]
    env = Env(tmp, "b14_equal", same, [dep("2026-07-06", 200_000_000, AFTER_CLOSE)])
    raises(acf.CashFlowError, env.ledger_raw, "B14 hai dòng cùng balance_ts", "balance_ts không tăng nghiêm ngặt")
    # Ngoài đoạn liên quan (trước dòng liền trước dòng tiền đầu tiên) thì không cản; không có dòng
    # tiền nào (chỉ market_only) thì luật gán không dùng balance_ts ⇒ không kiểm.
    old = [("2026-07-02", 1e9, False, "2026-07-03T20:00:00"), ("2026-07-03", 1e9), ("2026-07-06", 1.2e9),
           ("2026-07-07", 1.2e9)]
    env = Env(tmp, "b14_old", old, [dep("2026-07-06", 200_000_000, AFTER_CLOSE)])
    ok(by_date(env.ledger()[0])[D(2026, 7, 6)]["flow_eod_vnd"] == 200e6,
       "B14: balance_ts lùi ở dòng NGOÀI đoạn liên quan không được cản việc gán")
    env = Env(tmp, "b14_market_only", edited, [{"date": "2026-07-06", "amount_vnd": 0, "kind": "market_only",
                                               "evidence": "sàn"}])
    ok(len(env.ledger()[0]) == 5, "B14: chỉ có market_only ⇒ không kiểm balance_ts, sổ dựng bình thường")

    # --- B15. Dòng nav_history của ngày KHÔNG có phiên chụp trước 14:45 vẫn là giá chốt phiên trước
    # (arch-review lần 2, L8) — không bị coi là "chụp trước đóng cửa" khi làm dòng cho giá.
    for name, nav_rows, flow_day in (
            ("sat", [("2026-07-03", 1e9), ("2026-07-04", 1e9, False, "2026-07-04T10:00:00"), ("2026-07-06", 1.2e9)],
             "2026-07-06"),
            ("hol", [("2026-08-28", 1e9), ("2026-09-02", 1e9, False, "2026-09-02T08:00:00"), ("2026-09-03", 1.2e9)],
             "2026-09-03")):
        env = Env(tmp, f"b15_{name}", nav_rows, [dep(flow_day, 200_000_000, "10:00")])
        row = by_date(env.ledger()[0])[D.fromisoformat(flow_day)]
        ok(row["flow_bod_vnd"] == 200e6 and row["unit_price"] == 10_000.0,
           f"B15 ({name}): dòng cho giá là ngày không phiên chụp sáng ⇒ vẫn nhận, giá 10.000; được {row}")

    # --- B16. Tiền tới ĐÚNG ngày không có phiên, SAU lần chụp của dòng ngày đó và trước 14:45
    # (arch-review lần 3, K2): ngày không phiên không có giờ đóng cửa nào để "tới trước" — dòng đó là
    # giá chốt phiên trước, tiền giao dịch ở giá ấy (bod trên dòng kế tiếp). Trước đây bị từ chối oan.
    for name, nav_rows, flow_day, flow_t, next_day in (
            ("sat", [("2026-07-03", 1e9), ("2026-07-04", 1e9, False, "2026-07-04T10:00:00"), ("2026-07-06", 1.2e9)],
             "2026-07-04", "11:00", "2026-07-06"),
            ("hol", [("2026-08-28", 1e9), ("2026-09-02", 1e9, False, "2026-09-02T08:00:00"), ("2026-09-03", 1.2e9)],
             "2026-09-02", "09:00", "2026-09-03")):
        env = Env(tmp, f"b16_{name}", nav_rows, [dep(flow_day, 200_000_000, flow_t)])
        row = by_date(env.ledger()[0])[D.fromisoformat(next_day)]
        ok(row["flow_bod_vnd"] == 200e6 and row["unit_price"] == 10_000.0,
           f"B16 ({name}): tiền {flow_day} {flow_t} sau lần chụp của dòng ngày KHÔNG phiên ⇒ bod trên "
           f"{next_day} ở giá 10.000, không bị từ chối; được {row}")
    # Đối chứng: cùng hình dạng nhưng dòng thuộc ngày CÓ phiên thì vẫn phải từ chối.
    env = Env(tmp, "b16_session", [("2026-07-02", 1e9), ("2026-07-03", 1e9, False, "2026-07-03T10:00:00"),
                                   ("2026-07-06", 1.2e9)], [dep("2026-07-03", 200_000_000, "11:00")])
    raises(acf.CashFlowError, env.ledger_raw, "B16 đối chứng: dòng ngày CÓ phiên chụp 10:00, tiền 11:00",
           "tới TRONG phiên")

    # --- B17. Dòng cho giá phải chụp khi phiên đóng cửa gần nhất ĐÚNG là phiên mà tiền giao dịch
    # theo giá của nó (arch-review lần 3, K3). Dòng 07-03 chụp TỐI 07-06 (chạy lại snapshot ngày cũ
    # theo đường live) ⇒ NAV của nó đã chứa biến động phiên 07-06; nạp sau đóng cửa 07-03 từng được
    # gán eod trên dòng đó — giá chốt "07-03" thật ra là giá 07-06, không lỗi, không cảnh báo.
    late = [("2026-07-02", 1e9), ("2026-07-03", 1.32e9, False, "2026-07-06T20:00:00"), ("2026-07-07", 1.32e9)]
    env = Env(tmp, "b17_late", late, [dep("2026-07-03", 220_000_000, AFTER_CLOSE)])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B17 dòng 07-03 chụp sau khi phiên 07-06 đóng cửa",
                 "không phải giá chốt phiên 2026-07-03")
    ok("2026-07-06T20:00:00" in msg and "phiên đóng cửa gần nhất là 2026-07-06" in msg and "dòng cho giá 2026-07-03" in msg,
       f"B17: thông điệp phải trích balance_ts đã đọc + phiên mà dòng đó thật sự phản ánh, được {msg}")
    raises(acf.CashFlowError, lambda: env.returns_raw(D(2026, 7, 7)), "B17 nav_period_returns",
           "không phải giá chốt phiên 2026-07-03")
    raises(acf.CashFlowError, lambda: acf.unexplained_nav_jumps(env.rows(), acf.load_flows("SpaceX", env.flows_path)),
           "B17 cổng 5%", "không phải giá chốt phiên 2026-07-03")
    # Chụp SÁNG phiên sau, trước giờ đóng cửa (ca thật ZaloPay 07-27 → 07-28T09:15): phiên đóng cửa
    # gần nhất vẫn là 07-03 ⇒ phải nhận như cũ.
    morning = [("2026-07-02", 1e9), ("2026-07-03", 1.32e9, False, "2026-07-06T09:15:00"), ("2026-07-06", 1.32e9)]
    env = Env(tmp, "b17_morning", morning, [dep("2026-07-03", 220_000_000, "20:00")])
    row = by_date(env.ledger()[0])[D(2026, 7, 3)]
    ok(row["flow_eod_vnd"] == 220e6 and row["unit_price"] == 11_000.0,
       f"B17: dòng 07-03 chụp 09:15 sáng 07-06 ⇒ eod trên 07-03 ở giá 11.000, vẫn nhận; được {row}")
    # Chiều ngược lại mà hai chốt cũ không thấy: dòng thứ Bảy 07-04 (ngày không phiên) nhưng chụp
    # GIỮA phiên thứ Sáu 07-03 ⇒ NAV của nó thiếu phần còn lại của phiên 07-03.
    early_sat = [("2026-07-02", 1e9), ("2026-07-04", 1e9, False, "2026-07-03T10:00:00"), ("2026-07-06", 1.32e9)]
    env = Env(tmp, "b17_early_sat", early_sat, [dep("2026-07-03", 220_000_000, AFTER_CLOSE)])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B17 dòng thứ Bảy chụp giữa phiên thứ Sáu",
                 "không phải giá chốt phiên 2026-07-03")
    ok("phiên đóng cửa gần nhất là 2026-07-02" in msg, f"B17: phải nêu phiên mà dòng đó phản ánh (07-02), được {msg}")

    # --- B18. Ba mutant còn sống sau arch-review lần 3 (K4).
    # L06 — `_last_session_closed_by` lùi TỪNG ngày: thứ Bảy/Chủ nhật/sáng thứ Hai đều về thứ Sáu.
    for when, want in ((datetime.datetime(2026, 7, 4, 16, 0), D(2026, 7, 3)),
                       (datetime.datetime(2026, 7, 5, 10, 0), D(2026, 7, 3)),
                       (datetime.datetime(2026, 7, 6, 10, 0), D(2026, 7, 3)),
                       (datetime.datetime(2026, 7, 6, 14, 45), D(2026, 7, 6)),
                       (datetime.datetime(2026, 7, 6, 14, 44, 59), D(2026, 7, 3))):
        ok(acf._last_session_closed_by(when) == want,
           f"B18/L06: phiên đóng cửa gần nhất tính tới {when} phải là {want}, được {acf._last_session_closed_by(when)}")
    # T05 — đoạn phải kiểm balance_ts bắt đầu từ dòng tiền SỚM NHẤT (hai dòng tiền, lỗi nằm giữa).
    two = [("2026-07-02", 1e9), ("2026-07-03", 1e9, False, "2026-07-07T09:00:00"), ("2026-07-06", 1.2e9),
           ("2026-07-07", 1.2e9), ("2026-07-08", 1.2e9), ("2026-07-09", 1.4e9)]
    env = Env(tmp, "b18_t05", two, [dep("2026-07-06", 200_000_000, "20:00"), dep("2026-07-09", 200_000_000, "10:00")])
    raises(acf.CashFlowError, env.ledger_raw, "B18/T05 balance_ts lùi nằm trước dòng tiền thứ hai",
           "balance_ts không tăng nghiêm ngặt")
    # T07 — phải kiểm MỌI cặp dòng liên tiếp, không chỉ cặp đầu (lỗi ở cặp thứ ba).
    third = [("2026-07-02", 1e9), ("2026-07-03", 1.2e9), ("2026-07-06", 1.2e9, False, "2026-07-08T09:00:00"),
             ("2026-07-07", 1.2e9), ("2026-07-08", 1.2e9)]
    env = Env(tmp, "b18_t07", third, [dep("2026-07-03", 200_000_000, AFTER_CLOSE)])
    msg = raises(acf.CashFlowError, env.ledger_raw, "B18/T07 balance_ts lùi ở cặp dòng thứ ba",
                 "balance_ts không tăng nghiêm ngặt")
    ok("2026-07-08T09:00:00" in msg and "2026-07-07T19:10:00" in msg, f"B18/T07: phải trích hai balance_ts, được {msg}")

    # --- B19. NAV / vốn khởi điểm không hữu hạn ⇒ LỖI nêu đúng giá trị, không ra "+nan%" (K5).
    fine = [("2026-07-02", 1e9), ("2026-07-03", 1.1e9)]
    env = Env(tmp, "b19_nan_nav", [("2026-07-02", 1e9), ("2026-07-03", float("nan")), ("2026-07-06", 1.1e9)], [])
    msg = raises(ValueError, env.ledger_raw, "B19 nav = nan", "không phải số hữu hạn")
    ok("2026-07-03" in msg and "nan" in msg, f"B19: thông điệp phải nêu dòng và giá trị đã đọc, được {msg}")
    raises(ValueError, lambda: env.returns_raw(D(2026, 7, 6)), "B19 nav_period_returns nav = nan", "không phải số hữu hạn")
    env = Env(tmp, "b19_inf_nav", [("2026-07-02", 1e9), ("2026-07-03", float("inf"))], [])
    raises(ValueError, env.ledger_raw, "B19 nav = inf", "không phải số hữu hạn")
    env = Env(tmp, "b19_fine", fine, [])
    for bad in (float("nan"), float("inf")):
        raises(ValueError, lambda: nul.build_ledger(env.rows(), [], D(2026, 7, 1), bad),
               f"B19 vốn khởi điểm = {bad}", "vốn khởi điểm phải > 0")
    ok(len(nul.build_ledger(env.rows(), [], D(2026, 7, 1), 1e9)[0]) == 3, "B19 đối chứng: số hữu hạn ⇒ dựng bình thường")


# ------------------------------------------------------------------ C. sổ trên đĩa chỉ-ghi-thêm
def part_c_sealed(tmp):
    nav = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_220_000_000.0, True),
           ("2026-07-06", 1_232_200_000.0)]
    flows = [dep("2026-07-03", 200_000_000, AFTER_CLOSE)]
    env = Env(tmp, "c_seal", nav, flows)

    # --- C0. KHÔNG chốt sổ thật trước bước 3 (D2). Thư mục dữ liệu "thật" ở đây là một tempdir
    # gán vào `nul.NAV_HISTORY_DIR` ⇒ kể cả khi cơ chế từ chối hỏng, selfcheck không chạm data/.
    fake_real = Path(tmp) / "fake_real_data"
    fake_real.mkdir()
    built = env.ledger()[0]
    orig_dir = nul.NAV_HISTORY_DIR
    nul.NAV_HISTORY_DIR = str(fake_real)
    try:
        target = nul.ledger_path("SpaceX", str(fake_real))
        ok(target == str(fake_real / "nav_unit_ledger_SpaceX.csv"), f"C0: ledger_path sai: {target}")
        raises(nul.SealRefused, lambda: nul.seal(target, built), "C0 chốt vào thư mục dữ liệu thật",
               "TỪ CHỐI chốt sổ")
        link = Path(tmp) / "link_to_real_data"
        os.symlink(fake_real, link)
        for alias in (str(fake_real) + "/./nav_unit_ledger_SpaceX.csv", str(link / "nav_unit_ledger_SpaceX.csv")):
            raises(nul.SealRefused, lambda: nul.seal(alias, built),
                   f"C0 chốt vào thư mục dữ liệu thật qua đường dẫn khác tên ({alias})", "TỪ CHỐI chốt sổ")
        ok(list(fake_real.iterdir()) == [], f"C0: bị từ chối thì KHÔNG được tạo file nào: {list(fake_real.iterdir())}")
        ok(must(lambda: nul.seal(target, built, write=False), "C0 chỉ đối chiếu") == ([], []),
           "C0: write=False trên thư mục dữ liệu thật chỉ đọc — được phép, không tạo file")
        ok(list(fake_real.iterdir()) == [], "C0: write=False không được tạo file (kể cả file khoá)")
    finally:
        nul.NAV_HISTORY_DIR = orig_dir
    # CLI: --seal mà thư mục sổ là thư mục dữ liệu mặc định ⇒ rc=3. Chạy main() trong tiến trình
    # con với NAV_HISTORY_DIR đã trỏ tempdir (cùng lý do an toàn như trên).
    def cli_default_dir(*extra):
        code = ("import sys, nav_unit_ledger as n; n.NAV_HISTORY_DIR = sys.argv.pop(1); "
                "raise SystemExit(n.main())")
        return subprocess.run(
            [sys.executable, "-c", code, str(fake_real), "--account", "SpaceX", "--nav-dir", str(env.dir),
             "--inception-path", env.inc_path, "--flows-path", env.flows_path, *extra],
            capture_output=True, text=True, cwd=str(BIN))
    p = cli_default_dir("--seal")
    ok(p.returncode == 3 and "TỪ CHỐI chốt sổ" in p.stderr and list(fake_real.iterdir()) == [],
       f"C0: --seal không --ledger-dir phải rc=3 và không tạo file, được rc={p.returncode} {p.stderr[:200]}")
    p = cli_default_dir("--seal", "--ledger-dir", str(fake_real))
    ok(p.returncode == 3 and list(fake_real.iterdir()) == [],
       f"C0: --seal --ledger-dir=<thư mục dữ liệu thật> cũng phải rc=3, được rc={p.returncode}")
    p = cli_default_dir()
    ok(p.returncode == 0 and "KHÔNG đối chiếu" in p.stdout and list(fake_real.iterdir()) == [],
       f"C0: không --ledger-dir, không --seal ⇒ chỉ dựng + in, nói rõ không đối chiếu: {p.stdout[-300:]}")
    ok(not hasattr(nul, "os") or "NAV_UNIT_LEDGER_DIR" not in (BIN / "nav_unit_ledger.py").read_text(encoding="utf-8")
       .split('"""', 2)[2], "C0: biến môi trường NAV_UNIT_LEDGER_DIR không được còn trên đường code")

    # --- C1. Chốt vào thư mục tường minh.
    p = env.cli()
    ok(p.returncode == 0 and "chưa chốt dòng nào" in p.stdout and not env.sealed.exists(),
       f"C: chạy không --seal KHÔNG được tạo file, được rc={p.returncode} {p.stdout[-200:]}")
    ok(list(env.ledger_dir.iterdir()) == [], "C: chạy không --seal không được để lại file nào")
    p = env.cli("--seal", "--asof", "2026-07-03")
    ok(p.returncode == 0 and "vừa THÊM 3 dòng" in p.stdout,
       f"C: --asof 07-03 phải chốt 3 dòng (khởi điểm + 2), được {p.stdout} {p.stderr}")
    ok(env.sealed.is_file(), f"C: sau --seal file sổ phải tồn tại: {list(env.ledger_dir.iterdir())}")
    first = env.sealed.read_bytes()
    lines = first.decode().splitlines()
    ok(lines[0] == ",".join(nul.LEDGER_FIELDS) and len(lines) == 4, f"C: header + 3 dòng, được {lines}")
    ok(lines[1].startswith("2026-07-01,1000000000.0,0.0,0.0,0.0,100000.0,10000.0,False"),
       f"C: dòng khởi điểm sai: {lines[1]}")
    ok(lines[3].endswith(",True") and lines[2].endswith(",False"),
       f"C: cờ nav_is_estimate của ngày nguồn phải vào sổ, được {lines[2:]}")
    inode_first = env.sealed.stat().st_ino
    p = env.cli("--seal")
    second = env.sealed.read_bytes()
    ok(p.returncode == 0 and "vừa THÊM 1 dòng" in p.stdout and second.startswith(first)
       and len(second.decode().splitlines()) == 5,
       "C: chốt tiếp phải THÊM 1 dòng và giữ nguyên từng byte cũ")
    ok(env.sealed.stat().st_ino != inode_first,
       "C: chốt tiếp phải THAY file bằng os.replace (inode mới), không ghi đè tại chỗ")
    ok(sorted(x.name for x in env.ledger_dir.iterdir())
       == ["nav_unit_ledger_SpaceX.csv", "nav_unit_ledger_SpaceX.csv.lock"],
       f"C: thư mục sổ chỉ được có file sổ + file khoá, không file tạm: {list(env.ledger_dir.iterdir())}")
    p = env.cli("--seal")
    ok(p.returncode == 0 and "vừa THÊM 0 dòng" in p.stdout and env.sealed.read_bytes() == second,
       "C: chốt lại khi không có dòng mới phải không đổi byte nào")
    sealed = nul.read_sealed(str(env.sealed))
    built = env.ledger()[0]
    ok(len(sealed) == len(built) and all(
        s[k] == b[k] for s, b in zip(sealed, built) for k in nul.LEDGER_FIELDS),
        "C: sổ đọc lại phải khớp ĐÚNG từng giá trị với chuỗi dựng (repr float khứ hồi)")
    ok(nul.diff_against_sealed(built, sealed) == [], "C: chuỗi dựng lại y nguyên ⇒ không lệch")
    frac = Env(tmp, "c_frac", [("2026-07-02", 1_010_000_000.25), ("2026-07-03", 1_020_000_000.0625)], [])
    p = frac.cli("--seal")
    back = must(lambda: nul.read_sealed(str(frac.sealed)), "C: đọc lại sổ có NAV lẻ")
    ok(p.returncode == 0 and [r["nav"] for r in back] == [1e9, 1_010_000_000.25, 1_020_000_000.0625]
       and frac.cli().returncode == 0,
       f"C: NAV có phần lẻ phải ghi/đọc lại đúng từng bit (không làm tròn), được {[r['nav'] for r in back]}")
    # Dung sai cột suy ra: lệch 1 ulp (nhiễu dấu phẩy động) KHÔNG phải lệch sổ; lệch 1e-9 thì CÓ.
    import math
    for key in ("units_issued", "units", "unit_price"):
        noisy = [dict(r) for r in sealed]
        noisy[2][key] = math.nextafter(noisy[2][key], math.inf)
        ok(nul.diff_against_sealed(built, noisy) == [],
           f"C: {key} lệch 1 ulp là nhiễu dấu phẩy động, không được báo lệch sổ")
        noisy[2][key] = sealed[2][key] * (1 + 1e-9)
        ok(len(nul.diff_against_sealed(built, noisy)) == 1,
           f"C: {key} lệch tương đối 1e-9 phải bị báo lệch sổ")
    # Cột suy ra bị sửa thành nan/inf trong danh sách đã chốt ⇒ PHẢI là lệch (N8).
    for bad in (float("nan"), float("inf")):
        for key in ("units_issued", "units", "unit_price"):
            tampered = [dict(r) for r in sealed]
            tampered[2][key] = bad
            diffs = nul.diff_against_sealed(built, tampered)
            ok(len(diffs) == 1 and f"2026-07-03 {key}:" in diffs[0],
               f"C: {key}={bad} trong sổ đã chốt phải bị báo lệch đúng 1 chỗ, được {diffs}")

    def drift(label, needle, nav2=None, flows2=None):
        env.write_nav(nav2 or nav)
        env.write_flows(flows2 if flows2 is not None else flows)
        for args in ((), ("--seal",)):
            p = env.cli(*args)
            ok(p.returncode == 2, f"C {label} {args}: phải rc=2, được {p.returncode}: {p.stderr[:300]}")
            ok(all(n in p.stderr for n in needle), f"C {label}: stderr phải nêu {needle}: {p.stderr}")
            ok(env.sealed.read_bytes() == second, f"C {label} {args}: sổ đã chốt KHÔNG được đổi byte nào")
        env.write_nav(nav)
        env.write_flows(flows)

    drift("NAV quá khứ +1đ", ["2026-07-02 nav:", "lệch +1.00 VND", "2026-07-02 unit_price:"],
          nav2=[("2026-07-02", 1_010_000_001.0)] + nav[1:])
    drift("xoá dòng quá khứ", ["2026-07-02: dòng đã chốt", "KHÔNG còn"], nav2=nav[1:])
    drift("chen dòng quá khứ", ["2026-07-04: dòng CHEN VÀO"],
          nav2=nav[:2] + [("2026-07-04", 1_220_000_000.0)] + nav[2:])
    drift("dòng tiền khai lùi ngày", ["2026-07-02 flow_eod_vnd:", "lệch +50,000,000.00 VND",
                                      "2026-07-06 units:"],
          flows2=flows + [dep("2026-07-02", 50_000_000, AFTER_CLOSE)])
    drift("đổi giờ dòng tiền đã chốt", ["2026-07-03 flow_bod_vnd:", "2026-07-03 flow_eod_vnd:"],
          flows2=[dep("2026-07-03", 200_000_000, IN_SESSION)])
    drift("đổi cờ ước tính", ["2026-07-03 nav_is_estimate: đã chốt True → dựng lại False"],
          nav2=[nav[0], nav[1][:2], nav[2]])
    ok(env.cli().returncode == 0, "C: khôi phục nguồn ⇒ khớp lại, rc=0")

    # Thêm ngày mới SAU dòng đã chốt: hợp lệ, không phải lệch.
    env.write_nav(nav + [("2026-07-07", 1_240_000_000.0)])
    p = env.cli("--seal")
    ok(p.returncode == 0 and "vừa THÊM 1 dòng" in p.stdout and env.sealed.read_bytes().startswith(second),
       f"C: ngày mới phải chốt thêm được, được rc={p.returncode} {p.stderr}")

    # Sổ hỏng ⇒ rc=1, không ghi đè — không coi như chưa có sổ.
    good = env.sealed.read_bytes()
    g = good.splitlines(keepends=True)

    def cell(line, idx, value):
        parts = line.decode().rstrip("\n").split(",")
        parts[idx] = value
        return (",".join(parts) + "\n").encode()

    for label, bad in (("ghi dở", good[:-1]), ("sai header", b"date,nav\n" + good.split(b"\n", 1)[1]),
                       ("ngày lùi", good + g[1]), ("ngày trùng dòng cuối", good + g[-1]),
                       ("cờ ước tính viết thường", b"".join(g[:-1]) + cell(g[-1], 7, "true")),
                       ("thiếu cột", b"".join(g[:-1]) + g[-1].rsplit(b",", 1)[0] + b"\n"),
                       ("unit_price = nan", b"".join(g[:2]) + cell(g[2], 6, "nan") + b"".join(g[3:])),
                       ("units = inf", b"".join(g[:2]) + cell(g[2], 5, "inf") + b"".join(g[3:]))):
        env.sealed.write_bytes(bad)
        for args in ((), ("--seal",)):
            p = env.cli(*args)
            ok(p.returncode == 1 and env.sealed.read_bytes() == bad,
               f"C sổ hỏng ({label}) {args}: phải rc=1 và không đụng file, được rc={p.returncode} {p.stderr[:200]}")
        raises(ValueError, lambda: nul.read_sealed(str(env.sealed)), f"C read_sealed sổ hỏng ({label})")
    env.sealed.write_bytes(good)

    # --- C2. Ghi NGUYÊN TỬ: lỗi giữa chừng (fsync nổ) ⇒ sổ cũ nguyên từng byte, không file tạm.
    env.write_nav(nav + [("2026-07-07", 1_240_000_000.0), ("2026-07-08", 1_250_000_000.0)])
    built = env.ledger()[0]
    calls = []
    real_fsync, real_replace = os.fsync, os.replace

    def boom(fd):
        calls.append("fsync")
        raise OSError("đĩa đầy (giả lập)")

    os.fsync = boom
    try:
        raises(OSError, lambda: nul.seal(str(env.sealed), built), "C2 fsync nổ", "đĩa đầy")
    finally:
        os.fsync = real_fsync
    ok(calls == ["fsync"], f"C2: phải fsync file tạm trước khi thay sổ, được {calls}")
    ok(env.sealed.read_bytes() == good, "C2: ghi dở thì sổ đã chốt phải nguyên từng byte")
    ok(not [x for x in env.ledger_dir.iterdir() if ".tmp." in x.name],
       f"C2: ghi dở không được để lại file tạm: {list(env.ledger_dir.iterdir())}")
    order = []
    os.fsync = lambda fd: (order.append("fsync"), real_fsync(fd))[1]
    os.replace = lambda a, b: (order.append(("replace", os.path.basename(a), os.path.basename(b))),
                               real_replace(a, b))[1]
    try:
        sealed_before, added = must(lambda: nul.seal(str(env.sealed), built), "C2 chốt bình thường")
    finally:
        os.fsync, os.replace = real_fsync, real_replace
    ok(len(order) == 2 and order[0] == "fsync" and order[1][0] == "replace"
       and order[1][1].startswith("nav_unit_ledger_SpaceX.csv.tmp.") and order[1][2] == "nav_unit_ledger_SpaceX.csv",
       f"C2: trình tự phải là fsync(file tạm) rồi os.replace(file tạm → sổ), được {order}")
    ok(len(added) == 1 and added[0]["date"] == D(2026, 7, 8) and len(sealed_before) == 5
       and env.sealed.read_bytes().startswith(good),
       f"C2: chốt bình thường phải thêm đúng dòng 07-08, được {added}")
    good = env.sealed.read_bytes()

    # --- C3. KHOÁ + đọc MỘT lần (N2): giữ khoá, chạy `--seal` ở tiến trình khác ⇒ nó phải CHỜ.
    # Trong lúc nó chờ, "tiến trình B" (chính test) chốt xong dòng 07-09. Nhả khoá ⇒ tiến trình
    # chờ phải đọc sổ SAU khi B ghi: không thêm dòng trùng, sổ vẫn đọc lại được.
    env.write_nav(nav + [("2026-07-07", 1_240_000_000.0), ("2026-07-08", 1_250_000_000.0),
                         ("2026-07-09", 1_260_000_000.0)])
    built = env.ledger()[0]
    lock_path = str(env.sealed) + ".lock"
    with open(lock_path, "a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        waiter = subprocess.Popen(env.cli_args("--seal"), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 1.5
        while time.monotonic() < deadline and waiter.poll() is None:
            time.sleep(0.05)
        blocked = waiter.poll() is None
        if blocked:
            env.sealed.write_bytes(good + nul._csv_line(built[-1]).encode())      # B chốt 07-09
        fcntl.flock(lock, fcntl.LOCK_UN)
    out, err = waiter.communicate(timeout=30)
    ok(blocked, f"C3: --seal phải CHỜ khi tiến trình khác đang giữ khoá sổ; nó đã chạy xong: {out} {err}")
    after = env.sealed.read_bytes()
    ok(waiter.returncode == 0 and "vừa THÊM 0 dòng" in out and after == good + nul._csv_line(built[-1]).encode(),
       f"C3: sau khi được khoá phải thấy dòng B vừa chốt và không thêm gì, được rc={waiter.returncode} {out} {err}")
    ok(len(must(lambda: nul.read_sealed(str(env.sealed)), "C3 đọc lại sổ")) == 7,
       "C3: sổ sau hai tiến trình chốt xen nhau phải đọc lại được, đúng 7 dòng")

    # --- C3b. HAI tiến trình `seal` thật: khoá phải ĐỘC QUYỀN. Tiến trình A dừng BÊN TRONG vùng
    # khoá (ngay trước khi đọc sổ) cho tới khi có file "go"; trong lúc đó tiến trình B không được
    # vào vùng khoá. Khoá chia sẻ (LOCK_SH) thì cả hai cùng vào ⇒ cùng đọc sổ cũ, cùng ghi.
    two = Env(tmp, "c3b_two", nav, flows)
    helper = (
        "import sys, os, time, datetime\n"
        f"sys.path.insert(0, {str(BIN)!r})\n"
        "import nav_unit_ledger as nul\n"
        "tag, d = sys.argv[1], sys.argv[2]\n"
        "orig = nul._seal_locked\n"
        "def slow(path, ledger, asof, write):\n"
        "    open(os.path.join(d, 'inside_' + tag), 'w').close()\n"
        "    end = time.monotonic() + 20\n"
        "    while not os.path.exists(os.path.join(d, 'go_' + tag)) and time.monotonic() < end:\n"
        "        time.sleep(0.02)\n"
        "    return orig(path, ledger, asof, write)\n"
        "nul._seal_locked = slow\n"
        f"ledger, _ = nul.build_account_ledger('SpaceX', d, {two.inc_path!r}, {two.flows_path!r})\n"
        f"sealed, added = nul.seal({str(two.sealed)!r}, ledger)\n"
        "print(len(added))\n")

    def spawn(tag):
        return subprocess.Popen([sys.executable, "-c", helper, tag, str(two.dir)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def wait_for(name, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end and not (two.dir / name).exists():
            time.sleep(0.02)
        return (two.dir / name).exists()

    proc_a = spawn("A")
    a_in = wait_for("inside_A", 20)
    proc_b = spawn("B")
    b_in_early = wait_for("inside_B", 1.5)
    (two.dir / "go_A").touch()
    (two.dir / "go_B").touch()
    out_a, err_a = proc_a.communicate(timeout=60)
    out_b, err_b = proc_b.communicate(timeout=60)
    ok(a_in and proc_a.returncode == 0 and proc_b.returncode == 0,
       f"C3b: cả hai tiến trình seal phải chạy xong rc=0, được A={proc_a.returncode} {err_a[-300:]} "
       f"B={proc_b.returncode} {err_b[-300:]}")
    ok(not b_in_early,
       "C3b: tiến trình B đã vào vùng khoá trong khi A còn giữ — khoá chốt sổ phải ĐỘC QUYỀN (LOCK_EX)")
    n_rows = len(must(lambda: nul.read_sealed(str(two.sealed)), "C3b đọc lại sổ"))
    ok((out_a.strip(), out_b.strip()) == (str(n_rows), "0") and n_rows == len(two.ledger()[0]),
       f"C3b: A thêm đủ {n_rows} dòng, B vào sau thấy sổ đã chốt và thêm 0; được A={out_a!r} B={out_b!r}")

    # --- C4. Thiếu sổ dòng tiền ⇒ đường dựng sổ từ chối (không đoán `[]`).
    os.remove(env.flows_path)
    raises(acf.CashFlowError, env.ledger_raw, "C4 thiếu account_cash_flows.json", "KHÔNG có sổ dòng tiền")
    p = env.cli()
    ok(p.returncode == 1 and "KHÔNG có sổ dòng tiền" in p.stderr, f"C4: CLI phải rc=1: {p.stderr[:200]}")


# ------------------------------------------------------------------ D. hai số của chủ TK + quy năm
def part_d_owner_numbers(tmp):
    def mwr(*a):
        return must(lambda: npr.money_weighted_return(*a), f"money_weighted_return{a}")

    # Nghiệm đóng: tiền vào ngay đầu kỳ (w=1) và ngay cuối kỳ (w=0).
    r, note = mwr(1000.0, 1260.0, [(1.0, 200.0)])
    ok(note is None and abs(r - 0.05) < 1e-12, f"D: w=1 ⇒ 1260/(1000+200) − 1 = 5%, được {r}")
    r, note = mwr(1000.0, 1260.0, [(0.0, 200.0)])
    ok(note is None and abs(r - 0.06) < 1e-12, f"D: w=0 ⇒ (1260−200)/1000 − 1 = 6%, được {r}")
    r, note = mwr(1000.0, 1050.0, [])
    ok(r == 1050.0 / 1000.0 - 1 and note is None, "D: không dòng tiền ⇒ nav1/nav0 − 1")
    # Giữa kỳ: nghiệm phải thoả phương trình (dư < 1e-6) và sát xấp xỉ Dietz 20/(1000 + 0,6×200).
    r, note = mwr(1000.0, 1220.0, [(0.6, 200.0)])
    ok(abs(1000.0 * (1 + r) + 200.0 * (1 + r) ** 0.6 - 1220.0) < 1e-6,
       f"D: nghiệm IRR không thoả phương trình, r={r}")
    ok(abs(r - 20.0 / 1120.0) < 2e-4, f"D: IRR {r} phải sát Dietz {20.0 / 1120.0}")
    # Lãi/lỗ đúng 0 ⇒ nghiệm R = 0 nằm ĐÚNG trên một điểm lưới (x = 1): vẫn phải tìm ra.
    r, note = mwr(1000.0, 1200.0, [(0.5, 200.0)])
    ok(note is None and r == 0.0, f"D: pnl = 0 ⇒ IRR phải đúng 0,0, được {r} {note}")
    # Ghi chú chỉ nêu điều ĐÃ ĐO, không khẳng định nguyên nhân (§29).
    # Đặt y = √x: 1000y² − 2120y + 1122 = 1000(y − 1,02)(y − 1,1) ⇒ x = 1,0404 và 1,21.
    r, note = mwr(1000.0, 78.0, [(0.5, -2120.0), (0.0, 1200.0)])
    ok(r is None and "2 nghiệm" in note and "+4.040%" in note and "+21.000%" in note,
       f"D: 2 nghiệm phải trả None + ghi chú liệt kê CẢ HAI nghiệm, được {r} {note}")
    # 1000y² − 2100y + 1200 có biệt thức âm ⇒ vô nghiệm.
    r, note = mwr(1000.0, 100.0, [(0.5, -2100.0), (0.0, 1300.0)])
    ok(r is None and "0 nghiệm" in note and "không đổi dấu trên lưới" in note,
       f"D: 0 nghiệm phải trả None + ghi chú, được {r} {note}")
    # 0 nghiệm vì LỖ quá −99,9% — dòng tiền KHÔNG hề đổi dấu: ghi chú không được đổ cho "đổi dấu".
    r, note = mwr(1000.0, 0.1, [(0.5, 10.0)])
    ok(r is None and "0 nghiệm" in note and "dòng tiền đổi dấu" not in note
       and "(tại −99,9%: +1; tại +99.900%: +1,000,316)" in note,
       f"D: lỗ >99,9% ⇒ 0 nghiệm, ghi chú nêu giá trị hàm ở hai đầu, không đoán nguyên nhân: {note}")
    # Một nghiệm dù rút gần hết giữa kỳ: 1000x − 990√x − 10,5 = 0.
    r, note = mwr(1000.0, 10.5, [(0.5, -990.0)])
    ok(note is None and abs(1000.0 * (1 + r) - 990.0 * (1 + r) ** 0.5 - 10.5) < 1e-6 and 0 < r < 0.01,
       f"D: rút gần hết vẫn phải có đúng một nghiệm nhỏ dương, được {r} {note}")

    # Trọng số thời gian = ĐÚNG mốc giá sổ đơn vị đã gán (kỳ 07-01 → 07-06 = 5 ngày lịch):
    #   16:00 ngày 07-03 ⇒ eod trên 07-03 ⇒ w = 3/5 ; 10:00 ⇒ bod, giá chốt 07-02 ⇒ w = 4/5.
    nav_e = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
             ("2026-07-06", 1_220_000_000.0)]
    for t, w in ((AFTER_CLOSE, 0.6), (IN_SESSION, 0.8)):
        env = Env(tmp, f"d_{t.replace(':', '')}", nav_e, [dep("2026-07-03", 200_000_000, t)])
        p = env.returns()["inception"]
        want = round(mwr(1e9, 1.22e9, [(w, 200e6)])[0] * 100, 3)
        ok(p["days"] == 5 and p["mwr_pct"] == want,
           f"D {t}: mwr_pct phải dùng w={w} ⇒ {want}, được {p['mwr_pct']}")
        ok(p["mwr_pct"] != p["return_pct"] or t == IN_SESSION,
           f"D {t}: có dòng tiền thì hai tỉ suất là hai số riêng")
        ok(p["pnl_vnd"] == 20_000_000.0, f"D {t}: pnl_vnd phải 20tr, được {p['pnl_vnd']}")
    ok(mwr(1e9, 1.22e9, [(0.6, 200e6)])[0] != mwr(1e9, 1.22e9, [(0.8, 200e6)])[0],
       "D: trọng số thời gian khác nhau phải cho IRR khác nhau")
    # Nạp thứ Bảy 07-04 ⇒ bod trên thứ Hai 07-06 ⇒ giá chốt THỨ SÁU 07-03 ⇒ w = (07-10 − 07-03)/9
    # = 7/9 — không phải Chủ nhật (5/9), không phải thứ Bảy (6/9), không phải thứ Hai (4/9).
    env = Env(tmp, "d_weekend", [("2026-07-02", 1e9), ("2026-07-03", 1e9), ("2026-07-06", 1.224e9),
                                 ("2026-07-10", 1.224e9)], [dep("2026-07-04", 200_000_000, "09:00")])
    p = env.returns(D(2026, 7, 10))["inception"]
    wants = {k: round(mwr(1e9, 1.224e9, [(k / 9, 200e6)])[0] * 100, 3) for k in (4, 5, 6, 7)}
    ok(len(set(wants.values())) == 4 and p["days"] == 9 and p["mwr_pct"] == wants[7] and p["return_pct"] == 2.0,
       f"D: nạp cuối tuần ⇒ IRR tính từ giá chốt thứ Sáu (w=7/9 ⇒ {wants[7]}), được {p['mwr_pct']} (các w khác: {wants})")
    # IRR ngoài khoảng tìm trên chuỗi thật: 1 tỷ, nạp 10tr giữa kỳ, còn 100 đồng ⇒ mwr null + ghi chú.
    env = Env(tmp, "d_wipe", [("2026-07-02", 1e9), ("2026-07-06", 1.01e9), ("2026-07-11", 100.0)],
              [dep("2026-07-06", 10_000_000, AFTER_CLOSE)])
    p = env.returns(D(2026, 7, 11))["inception"]
    ok(p["mwr_pct"] is None and p["mwr_annualized_pct"] is None and "0 nghiệm" in p.get("mwr_note", "")
       and p["return_pct"] == -100.0,
       f"D: IRR không xác định ⇒ mwr_pct null KÈM mwr_note trong JSON, được {p}")

    # Chặn quy năm: < 365 ngày lịch ⇒ None + lý do; từ 365 ⇒ có số, số mũ 365,25/ngày.
    ok(npr.ANNUALIZE_MIN_DAYS == 365 and npr.DAYS_PER_YEAR == 365.25, "D: ngưỡng 365 ngày, số mũ 365,25")
    ok(npr.annualize_or_null(1.10, 364) == (None, npr.annualize_or_null(1.10, 364)[1])
       and "364 ngày lịch < 365" in npr.annualize_or_null(1.10, 364)[1],
       f"D: 364 ngày phải None kèm lý do, được {npr.annualize_or_null(1.10, 364)}")
    ok(npr.annualize_or_null(1.10, 365) == (10.007, None),
       f"D: đúng 365 ngày +10% ⇒ 1,1^(365,25/365) − 1 = 10,007%, được {npr.annualize_or_null(1.10, 365)}")
    ok(npr.annualize_or_null(1.4641, 1461) == (10.0, None),
       f"D: 1461 ngày (= 4 × 365,25) +46,41% ⇒ quy năm đúng +10,0%, được {npr.annualize_or_null(1.4641, 1461)}")
    ok(npr.annualize_or_null(0.0, 400)[0] is None and "<= 0" in npr.annualize_or_null(0.0, 400)[1],
       "D: hệ số <= 0 ⇒ None kèm lý do")
    # Kỳ dài hơn 1 năm trên chuỗi: SpaceX-giả từ 2026-07-01, NAV +46,41% sau 1461 ngày.
    long_nav = [("2026-07-02", 1_000_000_000.0), ("2027-06-30", 1_050_000_000.0),
                ("2030-06-01", 1_400_000_000.0), ("2030-06-24", 1_450_000_000.0),
                ("2030-07-01", 1_464_100_000.0)]
    env = Env(tmp, "d_long", long_nav, [])
    short = env.returns(D(2027, 6, 30))["inception"]
    ok(short["days"] == 364 and short["annualized_return_pct"] is None
       and short["mwr_annualized_pct"] is None and "annualized_note" in short,
       f"D: 364 ngày trên chuỗi phải null kèm lý do, được {short}")
    long = env.returns(D(2030, 7, 1))
    ok(long["inception"]["days"] == 1461 and long["inception"]["annualized_return_pct"] == 10.0
       and long["inception"]["mwr_annualized_pct"] == 10.0
       and "annualized_note" not in long["inception"],
       f"D: 1461 ngày +46,41% ⇒ quy năm 10,0, được {long['inception']}")
    ok(long["mtd"]["annualized_return_pct"] is None and long["wtd"]["annualized_return_pct"] is None,
       "D: cùng báo cáo, kỳ MTD/WTD ngắn vẫn KHÔNG quy năm")
    # Kỳ dài CÓ dòng tiền: mwr quy năm phải lấy từ IRR, không lấy nhầm hệ số gia quyền thời gian.
    #   2027-06-30: +5% rồi nạp 1.000 sau đóng cửa ⇒ NAV 2.050 ; 2030-07-01: 2.050 × 1,2 = 2.460
    env = Env(tmp, "d_long_flow", [("2026-07-02", 1_000_000_000.0), ("2027-06-30", 2_050_000_000.0),
                                   ("2030-07-01", 2_460_000_000.0)], [dep("2027-06-30", 1_000_000_000, AFTER_CLOSE)])
    p = env.returns(D(2030, 7, 1), today=D(2030, 7, 1))["inception"]   # fixture ở tương lai: tiêm "hôm nay"
    irr = mwr(1e9, 2.46e9, [((1461 - 364) / 1461, 1e9)])[0]
    ok(p["return_pct"] == 26.0 and p["annualized_return_pct"] == npr.annualize_or_null(1.26, 1461)[0]
       and p["mwr_pct"] == round(irr * 100, 3)
       and p["mwr_annualized_pct"] == npr.annualize_or_null(1 + irr, 1461)[0]
       and p["mwr_annualized_pct"] != p["annualized_return_pct"],
       f"D: kỳ dài có dòng tiền — hai số quy năm phải là hai số riêng, đúng công thức; được {p}")
    # report_date mà dòng NAV gần nhất còn TRƯỚC mốc khởi điểm ⇒ từ chối có nghĩa.
    env = Env(tmp, "d_before", [("2026-06-29", 9e8), ("2026-07-02", 1e9)], [])
    raises(ValueError, lambda: env.returns_raw(D(2026, 6, 30)), "D report-date trước inception", "trước inception")
    raises(ValueError, lambda: env.returns_raw(D(2026, 6, 1)), "D report-date trước MỌI dòng nav_history",
           "không có dòng nav_history nào <= 2026-06-01")


# ------------------------------------------------------------------ E. module dòng tiền + cổng 5%
def part_e_flow_module(tmp):
    def load(records, account="SpaceX", **kw):
        path = Path(tmp) / "e_flows.json"
        path.write_text(json.dumps(records if isinstance(records, dict) else {"SpaceX": records}),
                        encoding="utf-8")
        return acf.load_flows(account, str(path), **kw)

    # Giờ đóng cửa: hằng số khai ở account_cash_flows phải khớp bảng phiên của trading_bot.
    ok(acf.SESSION_CLOSE_ICT == datetime.time(14, 45), f"E: SESSION_CLOSE_ICT phải 14:45, được {acf.SESSION_CLOSE_ICT}")
    vn_market = Path(acf.WC_ROOT) / "trading_bot" / "vn_market.py"
    if vn_market.is_file():
        sys.path.insert(0, acf.WC_ROOT)
        from trading_bot import vn_market as vm
        closed = [start for name, start, _end, _cont in vm.SESSIONS if name == "CLOSED"]
        ok(closed == [acf.SESSION_CLOSE_ICT],
           f"E: SESSION_CLOSE_ICT {acf.SESSION_CLOSE_ICT} lệch phiên CLOSED của trading_bot.vn_market {closed}")
    else:
        print(f"BỎ QUA đối chiếu SESSION_CLOSE_ICT với trading_bot/vn_market.py: không có {vn_market} "
              f"(cây sandbox không mang trading_bot)")

    # §12: bản ghi của account KHÁC không được lọt sang.
    both = {"SpaceX": [dep("2026-07-03", 1)], "ZaloPay": [dep("2026-07-06", 2), dep("2026-07-07", 3)]}
    ok([f["amount_vnd"] for f in load(both, "SpaceX")] == [1.0]
       and [f["amount_vnd"] for f in load(both, "ZaloPay")] == [2.0, 3.0]
       and load(both, "NoSuch") == [],
       "E §12: load_flows phải lọc đúng account (SpaceX 1 bản ghi, ZaloPay 2, account lạ 0)")
    # Sắp theo ngày rồi giờ, bất kể thứ tự trong file.
    got = load([dep("2026-07-06", 1, "09:00"), dep("2026-07-03", 2, "16:00"), dep("2026-07-03", 3, "09:00:30")])
    ok([(f["date"].isoformat(), f["time_ict"]) for f in got]
       == [("2026-07-03", "09:00:30"), ("2026-07-03", "16:00"), ("2026-07-06", "09:00")],
       f"E: load_flows phải sắp theo ngày rồi giờ, được {got}")
    ok(load([dep("2026-07-03", 1, "9:05")])[0]["time_ict"] == "09:05"
       and load([dep("2026-07-03", 1, "9:05:07")])[0]["time_ict"] == "09:05:07"
       and load([dep("2026-07-03", 1)])[0]["timing"] is None,
       "E: time_ict chuẩn hoá HH:MM / HH:MM:SS; không khai timing ⇒ None (không có mặc định)")
    bad = [({"date": "2026-07-03", "amount_vnd": 0, "kind": "deposit", "evidence": "x", "time_ict": "10:00"}, "deposit"),
           ({"date": "2026-07-03", "amount_vnd": 0, "kind": "withdraw", "evidence": "x", "time_ict": "10:00"}, "withdraw"),
           ({"date": "2026-07-03", "amount_vnd": 5, "kind": "deposit", "evidence": "x"}, "thiếu time_ict"),
           ({"date": "2026-07-03", "amount_vnd": -5, "kind": "withdraw", "evidence": "x"}, "thiếu time_ict"),
           ({"date": "2026-07-03", "amount_vnd": 5, "kind": "deposit", "evidence": "x", "time_ict": "25:00"}, "HH:MM"),
           ({"date": "2026-07-03", "amount_vnd": 5, "kind": "deposit", "evidence": "x", "time_ict": "10:00",
             "timing": "intraday"}, "timing='intraday'"),
           ({"date": "2026-07-03", "amount_vnd": 0, "kind": "market_only", "evidence": "x", "timing": "bod"},
            "market_only")]
    nan_rec = {"date": "2026-07-03", "kind": "deposit", "evidence": "x", "time_ict": "10:00"}
    bad += [({"date": "2026-07-03", "amount_vnd": 5, "kind": "deposit", "time_ict": "10:00"},
             "thiếu field bắt buộc 'evidence'"),
            ("không phải object", "phải là object"),
            # amount_vnd không hữu hạn (json nhận NaN/Infinity) — từng ra "+nan%" (L7).
            (dict(nan_rec, amount_vnd=float("nan")), "không phải số hữu hạn"),
            (dict(nan_rec, amount_vnd=float("inf")), "không phải số hữu hạn"),
            (dict(nan_rec, amount_vnd=float("-inf"), kind="withdraw"), "không phải số hữu hạn"),
            # date không phải chuỗi (L2): null, số.
            (dict(nan_rec, amount_vnd=5, date=None), "date không phải YYYY-MM-DD"),
            (dict(nan_rec, amount_vnd=5, date=20260703), "date không phải YYYY-MM-DD")]
    for rec, needle in bad:
        raises(acf.CashFlowError, lambda: load([rec]), f"E bản ghi hỏng {rec}", needle)
    raises(acf.CashFlowError, lambda: load({"SpaceX": {"date": "2026-07-03"}}), "E entry account không phải list",
           "phải là list")
    path = Path(tmp) / "e_root_list.json"
    path.write_text(json.dumps([dep("2026-07-03", 1)]), encoding="utf-8")
    raises(acf.CashFlowError, lambda: acf.load_flows("SpaceX", str(path)), "E gốc file là list (L2)",
           "gốc file phải là object")
    raises(ValueError, lambda: nul.load_inception("NoSuch", str(Path(tmp) / "b4_base" / "account_inception.json")),
           "E account lạ trong account_inception.json", "không có entry")

    # Bản ghi có ngày trong TƯƠNG LAI so với hôm nay (ICT) ⇒ từ chối — bắt ca gõ nhầm ngày.
    mo_rec = {"date": "2026-07-04", "amount_vnd": 0, "kind": "market_only", "evidence": "x"}
    for rec in (dep("2026-07-04", 5), mo_rec):
        msg = raises(acf.CashFlowError, lambda: load([rec], today=D(2026, 7, 3)), f"E ngày tương lai {rec['kind']}",
                     "TƯƠNG LAI")
        ok("2026-07-04" in msg and "hôm nay 2026-07-03" in msg, f"E: thông điệp phải nêu cả hai ngày, được {msg}")
        ok(len(must(lambda rec=rec: load([rec], today=D(2026, 7, 4)), "E bản ghi đúng ngày hôm nay")) == 1,
           "E: bản ghi ĐÚNG ngày hôm nay phải được nhận")
    # Không truyền `today` ⇒ đồng hồ thật neo ICT (không theo TZ của máy): 17:30 UTC ngày 07-03 là
    # 00:30 ngày 07-04 giờ ICT ⇒ bản ghi 07-04 được nhận, 07-05 bị từ chối.
    real_dt = acf.datetime

    class _Clock(real_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            inst = real_dt.datetime(2026, 7, 3, 17, 30, tzinfo=real_dt.timezone.utc)
            return inst.astimezone(tz) if tz else inst.replace(tzinfo=None)

    acf.datetime = types.SimpleNamespace(datetime=_Clock, date=real_dt.date, time=real_dt.time,
                                         timedelta=real_dt.timedelta)
    try:
        ok(len(must(lambda: load([dep("2026-07-04", 5)]), "E đồng hồ ICT 07-04")) == 1,
           "E: hôm nay mặc định phải tính theo giờ ICT (07-04 00:30 ICT), không theo UTC/TZ máy")
        raises(acf.CashFlowError, lambda: load([dep("2026-07-05", 5)]), "E đồng hồ ICT, bản ghi 07-05",
               "hôm nay 2026-07-04")
    finally:
        acf.datetime = real_dt
    ok(len(load([{"date": "2026-07-03", "amount_vnd": 0, "kind": "market_only", "evidence": "x"}])) == 1,
       "E: market_only không cần time_ict")
    raises(acf.CashFlowError, lambda: acf.load_flows("SpaceX", str(Path(tmp) / "khong_co.json"), require_file=True),
           "E thiếu file + require_file", "KHÔNG có sổ dòng tiền")
    ok(not hasattr(acf, "DEFAULT_TIMING"), "E: không còn hằng số mặc định timing nào")

    # Cổng 5% (`unexplained_nav_jumps`).
    ok(acf.NAV_JUMP_BLOCK_PCT == 5.0, f"E: ngưỡng cổng công bố phải đúng 5,0%, được {acf.NAV_JUMP_BLOCK_PCT}")

    def rows(*navs):
        days = [D(2026, 7, 2), D(2026, 7, 3), D(2026, 7, 6), D(2026, 7, 7)]
        return [nul.NavRow(d, v, balance_ts=f"{d}T19:10:00") for d, v in zip(days, navs)]

    def jumps(r, records, **kw):
        return [(j["date"].isoformat(), round(j["change_pct"], 2))
                for j in must(lambda: acf.unexplained_nav_jumps(r, load(records), **kw), "E cổng 5%")]

    ok(jumps(rows(1e9, 1.0499e9, 1.0499e9), []) == [] and jumps(rows(1e9, 1.0501e9, 1.0501e9), [])
       == [("2026-07-03", 5.01)], "E: +4,99% không bị bắt, +5,01% bị bắt")
    ok(jumps(rows(1e9, 0.9501e9, 0.9501e9), []) == [] and jumps(rows(1e9, 0.8e9, 0.8e9), [])
       == [("2026-07-03", -20.0)], "E: bước nhảy ÂM (rút lớn chưa khai) cũng phải bị bắt: −20% bị bắt, −4,99% không")
    r4 = rows(1e9, 1.2e9, 1.2e9, 0.9e9)
    ok(jumps(r4, []) == [("2026-07-03", 20.0), ("2026-07-07", -25.0)], "E: hai bước nhảy không bản ghi ⇒ cả hai")
    ok(jumps(r4, [dep("2026-07-03", 200_000_000, "10:00")]) == [("2026-07-07", -25.0)],
       "E: bản ghi nạp được gán vào 07-03 chỉ giải thích bước nhảy 07-03")
    ok(jumps(r4, [dep("2026-07-03", 200_000_000, "10:00"), dep("2026-07-06", -300_000_000, "20:00")]) == [],
       "E: rút 20:00 thứ Hai (sau lần chụp) được gán vào phiên thứ Ba ⇒ giải thích bước nhảy 07-07")
    ok(jumps(r4, [dep("2026-07-03", 200_000_000, "10:00"), dep("2026-07-06", -300_000_000, "10:00")])
       == [("2026-07-07", -25.0)],
       "E: cùng bản ghi nhưng khai 10:00 thứ Hai ⇒ gán vào 07-06, KHÔNG giải thích bước nhảy 07-07")
    mo = {"date": "2026-07-07", "amount_vnd": 0, "kind": "market_only", "evidence": "sàn"}
    ok(jumps(r4, [dep("2026-07-03", 200_000_000, "10:00"), mo]) == [],
       "E: market_only (amount 0) cũng là bản ghi giải thích bước nhảy")
    ok(jumps(r4, [], start=D(2026, 7, 3)) == [("2026-07-03", 20.0), ("2026-07-07", -25.0)]
       and jumps(r4, [], start=D(2026, 7, 7)) == [("2026-07-07", -25.0)],
       "E: start ĐÚNG ngày đến của bước nhảy ⇒ bước nhảy đó vẫn được xét")
    ok(jumps(r4, [], start=D(2026, 7, 6)) == [("2026-07-07", -25.0)]
       and jumps(r4, [], end=D(2026, 7, 6)) == [("2026-07-03", 20.0)]
       and jumps(r4, [], end=D(2026, 7, 7)) == [("2026-07-03", 20.0), ("2026-07-07", -25.0)],
       "E: start/end giới hạn theo ngày ĐẾN của bước nhảy, tính cả hai đầu mút")
    # Bản ghi không gán được (thiếu balance_ts ở dòng cần xét) ⇒ cổng phải TỪ CHỐI, không im.
    bare_rows = [nul.NavRow(D(2026, 7, 2), 1e9), nul.NavRow(D(2026, 7, 3), 1.2e9)]
    raises(acf.CashFlowError, lambda: acf.unexplained_nav_jumps(bare_rows, load([dep("2026-07-03", 200_000_000)])),
           "E cổng 5% với dòng thiếu balance_ts", "không có balance_ts")


# ------------------------------------------------------------------ F. sandbox: CLI nhánh + cổng
SANDBOX_FILES = ("nav_period_returns.py", "nav_unit_ledger.py", "account_cash_flows.py",
                 "report_delivery_gate.py", "wc_paths.py", "cash_identity.py", "dnse_fee_rates.py",
                 "corp_actions.py")


def part_f_sandbox(tmp):
    """`report_delivery_gate.ROOT` trỏ cây canonical khi chạy từ worktree ⇒ muốn thử CLI của CHÍNH
    cây này với cổng báo cáo phải dựng sandbox: bản sao bin/ + bản sao dữ liệu (fixture)."""
    wc = Path(tmp) / "sandbox" / "WC"
    (wc / "data" / "execution_logs").mkdir(parents=True)
    (wc / "mike" / "bin").mkdir(parents=True)
    (wc / "wc_env.sh").write_text("", encoding="utf-8")
    (wc / "mike" / "MIKE.md").write_text("sandbox\n", encoding="utf-8")
    for name in SANDBOX_FILES:
        shutil.copy2(BIN / name, wc / "mike" / "bin" / name)
    for account in PUBLISHED:
        shutil.copy2(FIXTURE / f"nav_history_{account}.csv", wc / "data" / "execution_logs")
    shutil.copy2(FIXTURE / "account_inception.json", wc / "data")
    flows_path = wc / "data" / "account_cash_flows.json"
    flows_path.write_text(json.dumps({"SpaceX": [], "ZaloPay": []}), encoding="utf-8")
    envv = {k: v for k, v in os.environ.items()
            if k not in ("TZ", "WC_ROOT", "MIKE_ROOT", "ACCOUNT_CASH_FLOWS_PATH")}

    def cli(account, date="2026-10-09"):
        return subprocess.run([sys.executable, "bin/nav_period_returns.py", "--account", account,
                               "--report-date", date], cwd=wc / "mike", capture_output=True,
                              text=True, env=envv)

    def gate(report_name, pct_text):
        report = Path(tmp) / report_name
        report.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | "
                          f"{pct_text} | x | y |\n", encoding="utf-8")
        code = ("import sys, pathlib; sys.path.insert(0, 'bin'); import report_delivery_gate as g\n"
                "print('ROOT=' + str(g.ROOT))\n"
                "for fn in (g._check_period_returns, g._check_nav_flow_records):\n"
                "    try:\n        fn(pathlib.Path(sys.argv[1])); print(fn.__name__ + ': PASS')\n"
                "    except RuntimeError as exc:\n        print(fn.__name__ + ': BLOCK ' + str(exc)[:300].replace('\\n', ' '))\n")
        return subprocess.run([sys.executable, "-c", code, str(report)], cwd=wc / "mike",
                              capture_output=True, text=True, env=envv)

    for account, want in PUBLISHED.items():
        p = cli(account)
        ok(p.returncode == 0, f"F: CLI sandbox {account} phải rc=0: {p.stderr[:300]}")
        ok(pcts(json.loads(p.stdout)) == want, f"F: CLI sandbox {account} phải ra {want}, được {p.stdout[:200]}")
        ok("unit_ledger" not in json.loads(p.stdout), "F: đường CLI không còn khối unit_ledger (không đọc sổ)")
        ok(isinstance(json.loads(p.stdout).get("cash_flow_warnings"), list)
           and "cash_flow_investor_line" in json.loads(p.stdout),
           "F: CLI phải in cash_flow_warnings (chi tiết vận hành) + cash_flow_investor_line cạnh số tỉ suất")
    # Cảnh báo đẳng thức tiền của CLI chỉ tính TỚI ngày báo cáo (sandbox không có dnse_raw nên mọi
    # cửa sổ có biến động tiền đều thành cảnh báo — đủ để đếm).
    n_early = len(json.loads(cli("SpaceX", "2026-07-10").stdout)["cash_flow_warnings"])
    n_late = len(json.loads(cli("SpaceX").stdout)["cash_flow_warnings"])
    ok(0 < n_early < n_late, f"F: cash_flow_warnings phải tính tới ngày báo cáo, được {n_early} (07-10) / {n_late} (10-09)")
    p = cli("SpaceX")
    out = json.loads(p.stdout)
    ok(out["cash_flow_investor_line"] and "biến động tiền chưa đối chiếu xong" in out["cash_flow_investor_line"]
       and all(f"nav_period_returns: {line}" in p.stderr for line in out["cash_flow_warnings"]),
       f"F: CLI phải đưa dòng trung tính vào JSON và in MỌI dòng vận hành ra stderr; được {out['cash_flow_investor_line']!r}")
    # Đẳng thức tiền hỏng tới mức không import được ⇒ CLI vẫn phải ra đủ số tỉ suất (đường cảnh báo).
    good_ci = (wc / "mike" / "bin" / "cash_identity.py").read_text(encoding="utf-8")
    (wc / "mike" / "bin" / "cash_identity.py").write_text("raise RuntimeError('hỏng giả')\n", encoding="utf-8")
    p = cli("SpaceX")
    (wc / "mike" / "bin" / "cash_identity.py").write_text(good_ci, encoding="utf-8")
    out = json.loads(p.stdout) if p.returncode == 0 else {}
    ok(p.returncode == 0 and pcts(out) == PUBLISHED["SpaceX"] and out["cash_flow_investor_line"] is None
       and len(out["cash_flow_warnings"]) == 1 and "KHÔNG chạy được" in out["cash_flow_warnings"][0]
       and "RuntimeError (hỏng giả)" in out["cash_flow_warnings"][0]
       and "nav_period_returns: " + out["cash_flow_warnings"][0] in p.stderr,
       f"F: cash_identity không import được ⇒ CLI vẫn rc=0 + đủ số, lỗi hiện ở JSON và stderr; được "
       f"rc={p.returncode} {p.stderr[-300:]}")
    name = "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
    p = gate(name, "-1,33%")
    ok(f"ROOT={wc / 'mike'}" in p.stdout, f"F: cổng phải chạy trên cây sandbox, được {p.stdout[:200]} {p.stderr[:200]}")
    ok("_check_period_returns: PASS" in p.stdout and "_check_nav_flow_records: PASS" in p.stdout,
       f"F: báo cáo ghi đúng số công bố phải qua cả hai cổng, được {p.stdout} {p.stderr[-300:]}")
    p = gate(name, "+9,99%")
    ok("_check_period_returns: BLOCK period-return BLOCK" in p.stdout,
       f"F: báo cáo ghi +9,99% phải bị cổng tỉ suất CHẶN, được {p.stdout} {p.stderr[-300:]}")

    # K2: một sổ đơn vị LỆCH nằm ngay trong thư mục dữ liệu KHÔNG được làm CLI lỗi, tức không được
    # tắt cổng tỉ suất (cổng fail-open với mọi rc != 0).
    rows = nul.load_nav_history("SpaceX", str(wc / "data" / "execution_logs"))
    inception = nul.load_inception("SpaceX", str(wc / "data" / "account_inception.json"))
    ledger = nul.build_ledger(rows, [], *npr._inception_baseline(rows, inception))[0]
    drifted = [dict(r, nav=r["nav"] + 1234.0) if i == len(ledger) - 1 else r for i, r in enumerate(ledger)]
    (wc / "data" / "execution_logs" / "nav_unit_ledger_SpaceX.csv").write_text(
        ",".join(nul.LEDGER_FIELDS) + "\n" + "".join(nul._csv_line(r) for r in drifted), encoding="utf-8")
    p = cli("SpaceX")
    ok(p.returncode == 0 and pcts(json.loads(p.stdout)) == PUBLISHED["SpaceX"],
       f"F/K2: sổ lệch trong thư mục dữ liệu — CLI vẫn phải rc=0 và ra đúng số, được rc={p.returncode} {p.stderr[:300]}")
    p = gate(name, "+9,99%")
    ok("_check_period_returns: BLOCK period-return BLOCK" in p.stdout,
       f"F/K2: có sổ lệch, báo cáo ghi +9,99% VẪN phải bị chặn, được {p.stdout} {p.stderr[-300:]}")

    # N1: dòng tiền treo phải hiện ở JSON của CLI + cảnh báo stderr; bản ghi thiếu giờ ⇒ cổng
    # dòng tiền CHẶN (fail-closed) dù cổng tỉ suất fail-open.
    flows_path.write_text(json.dumps({"SpaceX": [dep("2026-10-10", 40_000_000, "10:00")], "ZaloPay": []}),
                          encoding="utf-8")
    p = cli("SpaceX")
    out = json.loads(p.stdout) if p.returncode == 0 else {}
    ok(p.returncode == 0 and pcts(out) == PUBLISHED["SpaceX"] and len(out["pending_flows"]) == 1
       and out["pending_flows"][0]["amount_vnd"] == 40e6 and out["dropped_flows"] == [],
       f"F/N1: dòng tiền treo phải nằm trong pending_flows của CLI, được {p.stdout[-400:]} {p.stderr[:200]}")
    ok("dòng tiền TREO" in p.stderr and "2026-10-10 10:00" in p.stderr and "+40,000,000" in p.stderr,
       f"F/N1: CLI phải cảnh báo dòng tiền treo ra stderr, được {p.stderr[:300]}")
    flows_path.write_text(json.dumps({"SpaceX": [dep("2026-06-30", 40_000_000, "10:00")], "ZaloPay": []}),
                          encoding="utf-8")
    p = cli("SpaceX")
    ok(p.returncode == 0 and len(json.loads(p.stdout)["dropped_flows"]) == 1 and "dòng tiền BỊ LOẠI" in p.stderr,
       f"F/N1: dòng tiền trước mốc khởi điểm phải nằm trong dropped_flows + stderr, được {p.stderr[:300]}")
    flows_path.write_text(json.dumps({"SpaceX": [dep("2026-10-08", 40_000_000, None)], "ZaloPay": []}),
                          encoding="utf-8")
    p = cli("SpaceX")
    ok(p.returncode == 1 and "thiếu time_ict" in p.stderr and p.stdout == "",
       f"F: bản ghi thiếu giờ ⇒ CLI rc=1, không in số, được rc={p.returncode} {p.stderr[:200]}")
    p = gate(name, "+9,99%")
    ok("_check_nav_flow_records: BLOCK nav-flow BLOCK" in p.stdout and "thiếu time_ict" in p.stdout,
       f"F: bản ghi thiếu giờ ⇒ cổng dòng tiền phải CHẶN báo cáo (fail-closed), được {p.stdout} {p.stderr[-300:]}")
    # Cổng tỉ suất FAIL-CLOSED (bước 2): CLI rc≠0 ⇒ không có số chuẩn ⇒ báo cáo KHÔNG qua cổng, kể
    # cả khi con số trong báo cáo trông đúng. Trước đó nhánh này chỉ WARN rồi cho qua.
    for pct_text in ("+9,99%", "-1,33%"):
        p = gate(name, pct_text)
        ok("_check_period_returns: BLOCK period-return BLOCK" in p.stdout and "rc=1" in p.stdout
           and "_check_period_returns: PASS" not in p.stdout,
           f"F: CLI rc=1 ⇒ cổng tỉ suất phải CHẶN báo cáo ghi {pct_text} (fail-closed), được {p.stdout} {p.stderr[-300:]}")
    # N6: cùng các module đặt ở độ sâu KHÁC (`mike/agents/wt-*/bin`) vẫn phải tìm đúng gốc cây.
    deep = wc / "mike" / "agents" / "wt-deep" / "bin"
    deep.mkdir(parents=True)
    for name in SANDBOX_FILES:
        shutil.copy2(BIN / name, deep / name)
    p = subprocess.run([sys.executable, "-c", "import nav_unit_ledger as n, account_cash_flows as a; "
                        "print(n.WC_ROOT); print(a.WC_ROOT); print(n.NAV_HISTORY_DIR); print(a.FLOWS_PATH)"],
                       cwd=deep, capture_output=True, text=True, env=envv)
    ok(p.returncode == 0 and p.stdout.split() == [str(wc), str(wc), str(wc / "data" / "execution_logs"),
                                                 str(wc / "data" / "account_cash_flows.json")],
       f"F/N6: module ở mike/agents/wt-deep/bin phải neo gốc {wc}, được {p.stdout} {p.stderr[:200]}")

    # L7 + K5: NAV nguồn "nan" ⇒ CLI từ chối (rc=1, nêu dòng và giá trị), không in số nào; cổng tỉ
    # suất phải CHẶN, không được in "PASS ... vs canonical +nan%". (Nhánh "CLI rc=0 mà số chuẩn
    # NaN" của cổng vẫn được thử bằng đầu ra giả ở `cash_identity_selfcheck.py` phần K.)
    flows_path.write_text(json.dumps({"SpaceX": [], "ZaloPay": []}), encoding="utf-8")
    hist = wc / "data" / "execution_logs" / "nav_history_SpaceX.csv"
    good_hist = hist.read_text(encoding="utf-8")
    body = good_hist.rstrip("\n").split("\n")
    cells = body[-1].split(",")
    cells[1] = "nan"
    hist.write_text("\n".join(body[:-1] + [",".join(cells)]) + "\n", encoding="utf-8")
    p = cli("SpaceX")
    ok(p.returncode == 1 and p.stdout == "" and "không phải số hữu hạn" in p.stderr and "2026-10-09" in p.stderr,
       f"F/K5: NAV nguồn nan ⇒ CLI rc=1, không in số, nêu dòng hỏng; được rc={p.returncode} {p.stdout[:200]} {p.stderr[:200]}")
    p = gate("SpaceX_weekly_report_2026-10-05_to_2026-10-09.md", "+9,99%")     # `name` đã bị vòng N6 ghi đè
    ok("_check_period_returns: BLOCK period-return BLOCK" in p.stdout and "rc=1" in p.stdout
       and "period-return PASS" not in p.stdout,
       f"F/L7: NAV nguồn nan ⇒ cổng tỉ suất phải CHẶN (không xác minh được), được {p.stdout} {p.stderr[-300:]}")
    hist.write_text(good_hist, encoding="utf-8")

    os.remove(flows_path)
    p = cli("SpaceX")
    ok(p.returncode == 1 and "KHÔNG có sổ dòng tiền" in p.stderr and p.stdout == "",
       f"F: thiếu account_cash_flows.json ⇒ CLI công bố phải rc=1, không in số; được rc={p.returncode} {p.stdout[:120]}")
    return wc


def main():
    tmp = tempfile.mkdtemp(prefix="nav_unit_ledger_selfcheck_")
    try:
        part_a_published()
        part_b_synthetic(tmp)
        part_c_sealed(tmp)
        part_d_owner_numbers(tmp)
        part_e_flow_module(tmp)
        part_f_sandbox(tmp)
    except AssertionError as exc:
        print(f"ASSERT-FAIL (sau {N} assertion PASS): {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK — {N} assertion PASS (nav_unit_ledger_selfcheck.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
