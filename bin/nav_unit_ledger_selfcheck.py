#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho SỔ ĐƠN VỊ QUỸ (`nav_unit_ledger.py`) và các số `nav_period_returns.py` lấy từ nó
(chính sách "tài khoản = quỹ mở", user duyệt 2026-10-10, bước 1/4).

Phủ: (A) dữ liệu thật 2 TK chưa có dòng tiền ⇒ đúng số đã công bố; (B) ca tổng hợp có dòng tiền,
đáp án tính tay hoặc dựng từ tỉ suất biết trước; (C) sổ trên đĩa chỉ-ghi-thêm; (D) lãi/lỗ VND,
tỉ suất gia quyền theo tiền, chặn quy năm.

Chạy: python3 mike/bin/nav_unit_ledger_selfcheck.py
      env -u TZ python3 … ;  TZ=America/New_York python3 …      (§16 — phải PASS y nguyên)
Không đọc mạng, không gọi BQ. Mọi file ghi ra nằm ở tempdir; KHÔNG tạo/sửa file nào trong data/.
"""
import datetime
import json
import os
import random
import subprocess
import sys
import tempfile
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
        """nav: [(YYYY-MM-DD, nav) | (YYYY-MM-DD, nav, is_estimate, balance_ts)]"""
        lines = [",".join(NAV_FIELDS)]
        for rec in nav:
            d, v = rec[0], rec[1]
            est = rec[2] if len(rec) > 2 else False
            ts = rec[3] if len(rec) > 3 and rec[3] else f"{d}T19:10:00"
            lines.append(f"{d},{v!r},0,0,0,0,0,{ts},0,{est},live")
        (self.dir / "nav_history_SpaceX.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_flows(self, flows):
        Path(self.flows_path).write_text(json.dumps({"SpaceX": flows}), encoding="utf-8")

    @property
    def sealed(self):
        return self.ledger_dir / "nav_unit_ledger_SpaceX.csv"

    def ledger_raw(self):
        return nul.build_account_ledger("SpaceX", str(self.dir), self.inc_path, self.flows_path)

    def returns_raw(self, report_date=REPORT):
        return npr.compute_period_returns(
            "SpaceX", report_date, nul.load_nav_history("SpaceX", str(self.dir)),
            nul.load_inception("SpaceX", self.inc_path),
            acf.load_flows("SpaceX", self.flows_path, require_file=True))

    def ledger(self):
        return must(self.ledger_raw, f"dựng sổ {self.dir.name}")

    def returns(self, report_date=REPORT):
        return must(lambda: self.returns_raw(report_date), f"tính kỳ {self.dir.name}")

    def cli(self, *extra):
        return subprocess.run(
            [sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX",
             "--nav-dir", str(self.dir), "--inception-path", self.inc_path,
             "--flows-path", self.flows_path, "--ledger-dir", str(self.ledger_dir), *extra],
            capture_output=True, text=True)


def dep(date, amount, timing=None, time_ict=None):
    rec = {"date": date, "amount_vnd": amount, "kind": "deposit" if amount > 0 else "withdraw",
           "evidence": "selfcheck fixture"}
    if timing:
        rec["timing"] = timing
    if time_ict:
        rec["time_ict"] = time_ict
    return rec


def check_invariant(ledger, label):
    """Bất biến của sổ: đơn vị × giá = NAV từng dòng (lệch <= 1 đồng), giá và đơn vị > 0."""
    for row in ledger:
        gap = abs(row["units"] * row["unit_price"] - row["nav"])
        ok(gap <= 1.0, f"{label} {row['date']}: đơn vị×giá lệch NAV {gap:.6f} đồng (> 1)")
        ok(row["units"] > 0 and row["unit_price"] > 0, f"{label} {row['date']}: đơn vị/giá <= 0")


def by_date(ledger):
    return {r["date"]: r for r in ledger}


# ------------------------------------------------------------------ A. dữ liệu thật, chưa dòng tiền
def part_a_real():
    # Số ĐÃ CÔNG BỐ asof 2026-10-09 (chân control đo trên master 6278becc trước khi sửa).
    published = {"SpaceX": (-1.33, 1.024, 0.519), "ZaloPay": (-4.907, -1.162, -2.01)}
    ledgers = {}
    for account, (inc_pct, wtd_pct, mtd_pct) in published.items():
        rows = npr.load_nav_history(account)
        inception = npr.load_inception(account)
        flows = acf.load_flows(account, require_file=True)
        f0, n0 = npr._inception_baseline(rows, inception)
        ledger, info = nul.build_ledger(rows, flows, f0, n0)
        ledgers[account] = ledger
        check_invariant(ledger, account)
        ok(ledger[0]["date"] == f0 and ledger[0]["unit_price"] == 10_000.0
           and ledger[0]["units"] == n0 / 10_000.0,
           f"{account}: dòng khởi điểm phải là {f0}, giá 10.000, đơn vị = vốn/10.000")
        ok(len(ledger) == 1 + sum(1 for r in rows if r[0] > f0),
           f"{account}: mỗi dòng nav_history sau khởi điểm phải có đúng một dòng sổ")
        ok(sum(r["nav_is_estimate"] for r in ledger) == sum(r.is_estimate for r in rows if r[0] > f0),
           f"{account}: cờ nav_is_estimate phải được mang theo đủ")
        if not [f for f in flows if f["date"] > f0]:
            ok(all(r["units"] == ledger[0]["units"] for r in ledger),
               f"{account}: chưa có dòng tiền ⇒ số đơn vị không được đổi")
            if rows[-1][0] >= D(2026, 10, 9):
                r = npr.compute_period_returns(account, D(2026, 10, 9), rows, inception, flows)
                got = (r["inception"]["return_pct"], r["wtd"]["return_pct"], r["mtd"]["return_pct"])
                ok(got == (inc_pct, wtd_pct, mtd_pct),
                   f"{account} asof 2026-10-09 phải ra số đã công bố {(inc_pct, wtd_pct, mtd_pct)}, "
                   f"được {got}")
            for d, nav in rows:
                if d < f0:
                    continue
                r = npr.compute_period_returns(account, d, rows, inception, flows)
                p = r["inception"]
                ok(p["return_pct"] == round((nav / n0 - 1) * 100, 3),
                   f"{account} {d}: không dòng tiền ⇒ tỉ số giá đơn vị phải == nav1/nav0 − 1")
                ok(p["mwr_pct"] == p["return_pct"] and p["pnl_vnd"] == nav - n0,
                   f"{account} {d}: không dòng tiền ⇒ mwr == twr và pnl == nav1 − nav0")
                for per in ("inception", "wtd", "mtd"):
                    ok(r[per]["annualized_return_pct"] is None
                       and r[per]["mwr_annualized_pct"] is None
                       and "không quy năm" in r[per].get("annualized_note", ""),
                       f"{account} {d} {per}: kỳ {r[per]['days']} ngày < 365 phải KHÔNG quy năm")
    sx, zp = ledgers["SpaceX"], ledgers["ZaloPay"]
    ok([r["unit_price"] for r in sx[-5:]] != [r["unit_price"] for r in zp[-5:]],
       "§12: sổ SpaceX và ZaloPay phải KHÁC nhau (giống nhau = đọc chung không lọc account)")


# ------------------------------------------------------------------ B. ca tổng hợp có dòng tiền
def part_b_synthetic(tmp):
    # --- B1. Nạp 200tr vào 1 tỷ đúng ngày thị trường +2%. Hai chuỗi NAV, mỗi chuỗi là sự thật
    # của MỘT quy ước; đọc bằng quy ước kia phải ra số KHÁC, đúng số tính tay.
    #   chuỗi E (tiền vào SAU khi chốt): 1.000 × 1,02 + 200 = 1.220 tr
    #   chuỗi B (tiền vào ĐẦU phiên):   (1.000 + 200) × 1,02 = 1.224 tr
    nav_e = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
             ("2026-07-06", 1_220_000_000.0)]
    nav_b = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_224_000_000.0),
             ("2026-07-06", 1_224_000_000.0)]
    eod = [dep("2026-07-03", 200_000_000)]                      # không khai timing = eod
    bod = [dep("2026-07-03", 200_000_000, "bod", "10:15")]
    hand = {("E", "eod"): 2.0,                                  # (1220 − 200)/1000 − 1
            ("E", "bod"): round((1220 / 1200 - 1) * 100, 3),    # 1,667
            ("B", "bod"): 2.0,                                  # 1224/(1000 + 200) − 1
            ("B", "eod"): 2.4}                                  # (1224 − 200)/1000 − 1
    ok(hand[("E", "bod")] == 1.667, "sanity đáp án tính tay")
    envs = {}
    for (series, timing), want in hand.items():
        env = Env(tmp, f"b1_{series}_{timing}", nav_e if series == "E" else nav_b,
                  eod if timing == "eod" else bod)
        envs[(series, timing)] = env
        got = env.returns()["inception"]["return_pct"]
        ok(got == want, f"B1 chuỗi {series} đọc theo {timing}: tính tay {want}%, được {got}%")
        check_invariant(env.ledger()[0], f"B1 {series}/{timing}")
    led = by_date(envs[("E", "eod")].ledger()[0])
    row = led[D(2026, 7, 3)]
    ok(row["unit_price"] == 10_200.0, f"B1 eod: giá chốt 07-03 phải 10.200, được {row['unit_price']}")
    ok(abs(row["units_issued"] - 200_000_000 / 10_200) < 1e-6 and row["flow_eod_vnd"] == 200e6
       and row["flow_bod_vnd"] == 0.0,
       f"B1 eod: phát hành 200tr/10.200 = 19.607,843 đơn vị, được {row['units_issued']}")
    led = by_date(envs[("B", "bod")].ledger()[0])
    row = led[D(2026, 7, 3)]
    ok(abs(row["units_issued"] - 20_000.0) < 1e-6 and row["unit_price"] == 10_200.0
       and row["flow_bod_vnd"] == 200e6 and row["flow_eod_vnd"] == 0.0,
       f"B1 bod: phát hành 200tr/10.000 = 20.000 đơn vị ở giá phiên trước, được {row}")
    r = envs[("E", "eod")].returns()["inception"]
    ok(r["pnl_vnd"] == 20_000_000.0 and r["net_flow_vnd"] == 200_000_000.0,
       f"B1: lãi/lỗ VND = 1.220 − 1.000 − 200 = 20tr, được {r['pnl_vnd']}")
    ok([sorted(c) for c in r["cash_flows"]] == [["amount_vnd", "date", "evidence", "kind", "timing"]],
       f"hợp đồng cash_flows phải giữ đúng 5 khoá cũ, được {r['cash_flows']}")
    for key in ("from_date", "to_date", "nav0", "nav1", "return_pct"):
        ok(key in r, f"hợp đồng JSON cũ thiếu khoá {key}")

    # --- B2. Giá đơn vị KHÔNG đổi vì dòng tiền: nạp/rút ngày thị trường đứng yên.
    flat = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_210_000_000.0),
            ("2026-07-06", 910_000_000.0), ("2026-07-07", 919_100_000.0)]
    for timing, t in (("eod", None), ("bod", "09:30")):
        env = Env(tmp, f"b2_{timing}", flat, [dep("2026-07-03", 200_000_000, timing if t else None, t),
                                              dep("2026-07-06", -300_000_000, timing if t else None, t)])
        ledger = env.ledger()[0]
        check_invariant(ledger, f"B2 {timing}")
        led = by_date(ledger)
        for d in (D(2026, 7, 3), D(2026, 7, 6)):
            ok(abs(led[d]["unit_price"] - 10_100.0) < 1e-6,
               f"B2 {timing} {d}: thị trường đứng yên ⇒ giá phải giữ 10.100, được {led[d]['unit_price']}")
        ok(led[D(2026, 7, 3)]["units_issued"] > 0 > led[D(2026, 7, 6)]["units_issued"],
           f"B2 {timing}: nạp phải PHÁT HÀNH (+), rút phải HUỶ (−) đơn vị")
        r = env.returns()["inception"]
        # 1.010/1.000 × (đứng yên) × (đứng yên) × 919,1/910 = +2,01%
        ok(r["return_pct"] == 2.01, f"B2 {timing}: rút một phần — tính tay +2,01%, được {r['return_pct']}")
        ok(r["net_flow_vnd"] == -100_000_000.0 and r["pnl_vnd"] == 19_100_000.0,
           f"B2 {timing}: pnl = 919,1 − 1.000 − (−100) = 19,1tr, được {r['pnl_vnd']}")

    # --- B3. Rút GẦN HẾT (còn 1tr) rồi +5% trên phần còn lại; rút HẾT ⇒ từ chối.
    near = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_000_000.0), ("2026-07-06", 1_050_000.0)]
    env = Env(tmp, "b3_near", near, [dep("2026-07-03", -999_000_000)])
    ledger = env.ledger()[0]
    check_invariant(ledger, "B3")
    r = env.returns()["inception"]
    ok(r["return_pct"] == 5.0 and abs(ledger[-1]["units"] - 100.0) < 1e-6,
       f"B3 rút gần hết: tỉ suất phải +5,0% trên 100 đơn vị còn lại, được {r['return_pct']} / "
       f"{ledger[-1]['units']}")
    ok(r["pnl_vnd"] == 50_000.0, f"B3: pnl = 1,05 − 1.000 + 999 = 0,05tr, được {r['pnl_vnd']}")
    env = Env(tmp, "b3_all", near, [dep("2026-07-03", -1_000_000_000, "bod", "09:00")])
    raises(ValueError, env.ledger_raw, "B3 rút đầu ngày hết đơn vị", "huỷ hết đơn vị")
    env = Env(tmp, "b3_all_eod", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 0.0)],
              [dep("2026-07-03", -1_000_000_000)])
    raises(ValueError, env.ledger_raw, "B3 rút cuối ngày hết đơn vị", "huỷ hết đơn vị")
    env = Env(tmp, "b3_neg", near, [dep("2026-07-03", 2_000_000)])
    raises(ValueError, env.ledger_raw, "B3 nav − tiền eod <= 0", "không tính được giá đơn vị")

    # --- B4. Nạp ĐÚNG ngày inception: không phải dòng tiền (đã nằm trong vốn khởi điểm) ⇒ bị loại.
    plain = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_020_000_000.0),
             ("2026-07-06", 1_030_000_000.0)]
    base = Env(tmp, "b4_base", plain, [])
    env = Env(tmp, "b4_inc", plain, [dep("2026-07-01", 500_000_000)])
    ledger, info = env.ledger()
    ok(len(info["dropped"]) == 1 and info["dropped"][0]["amount_vnd"] == 500e6,
       f"B4: flow ngày inception phải nằm trong info['dropped'], được {info}")
    ok(env.returns() == base.returns() and env.returns()["inception"]["return_pct"] == 3.0,
       "B4: flow ngày inception không được đổi bất kỳ số nào")
    ok("net_flow_vnd" not in env.returns()["inception"], "B4: flow bị loại không được hiện trong kỳ")
    # Dòng nav_history ĐÚNG ngày inception (khi đã có starting_capital) không phải một ngày của
    # sổ: mốc khởi điểm là vốn khởi điểm, không phải snapshot ngày đó.
    env = Env(tmp, "b4_row", [("2026-07-01", 999_000_000.0)] + plain, [])
    ledger = env.ledger()[0]
    ok(len(ledger) == 4 and ledger[0]["nav"] == 1_000_000_000.0 and ledger[0]["unit_price"] == 10_000.0,
       f"B4: dòng nav ngày inception không được thay mốc khởi điểm, được {ledger[0]}")
    ok(env.returns()["inception"]["return_pct"] == 3.0, "B4: tỉ suất từ đầu vẫn tính trên vốn khởi điểm")

    # --- B5. Hai (ba) dòng tiền CÙNG ngày: cộng theo từng quy ước, bod trước eod sau.
    #   07-03: bod +100, eod +200 và eod −50 ⇒ r = (1.282,2 − 150)/(1.010 + 100) − 1 = +2% ⇒ cả kỳ 1,01 × 1,02 − 1 = +3,02%
    nav5 = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_282_200_000.0),
            ("2026-07-06", 1_282_200_000.0)]
    env = Env(tmp, "b5", nav5, [dep("2026-07-03", 200_000_000), dep("2026-07-03", -50_000_000),
                                dep("2026-07-03", 100_000_000, "bod", "09:20")])
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

    # --- B5b. Dòng tiền ĐÚNG ngày mốc đầu kỳ (WTD: thứ Sáu tuần trước) thuộc kỳ TRƯỚC, không
    # thuộc kỳ này: giá chốt hôm đó đã là giá sau giao dịch.
    #   07-03 (thứ Sáu) eod +200 ; tuần 07-06…07-10: 1.220 → 1.244,4 = +2,0%
    env = Env(tmp, "b5b", [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
                           ("2026-07-06", 1_232_200_000.0), ("2026-07-07", 1_244_400_000.0)],
              [dep("2026-07-03", 200_000_000)])
    r = env.returns(D(2026, 7, 7))
    ok(r["wtd"]["from_date"] == "2026-07-03" and r["wtd"]["return_pct"] == 2.0
       and "net_flow_vnd" not in r["wtd"] and r["wtd"]["pnl_vnd"] == 24_400_000.0
       and r["wtd"]["mwr_pct"] == 2.0,
       f"B5b: WTD không được tính dòng tiền của ngày mốc đầu kỳ, được {r['wtd']}")
    ok(r["inception"]["net_flow_vnd"] == 200e6 and r["inception"]["return_pct"] == 4.04,
       f"B5b: kỳ từ đầu thì CÓ dòng tiền đó (1,02 × 1,02 − 1 = 4,04%), được {r['inception']}")

    # --- B6. Dòng tiền rơi vào ngày KHÔNG có dòng nav_history ⇒ fail-closed, không ghi sổ.
    env = Env(tmp, "b6_hole", plain, [dep("2026-07-04", 200_000_000)])       # thứ Bảy, eod mặc định
    raises(acf.CashFlowError, env.ledger_raw, "B6 eod ngày không có dòng NAV", "không có giá đơn vị chốt")
    p = env.cli("--seal")
    ok(p.returncode == 1 and "2026-07-04" in p.stderr and not env.sealed.exists(),
       f"B6: CLI phải rc=1, nêu ngày, KHÔNG tạo sổ; được rc={p.returncode} {p.stderr[:200]}")
    raises(acf.CashFlowError, env.returns_raw, "B6 nav_period_returns cũng phải từ chối", "2026-07-04")
    # sau dòng nav_history cuối = snapshot chưa chạy ⇒ treo, không lỗi, không đổi số
    env = Env(tmp, "b6_pending", plain, [dep("2026-07-08", 200_000_000)])
    ledger, info = env.ledger()
    ok(len(info["pending"]) == 1 and env.returns() == base.returns(),
       f"B6: flow sau dòng NAV cuối phải treo (pending) và không đổi số, được {info}")
    # bod khai tường minh ngày không phiên ⇒ gán vào phiên kế tiếp (luật cũ, giữ nguyên)
    env = Env(tmp, "b6_bod", plain, [dep("2026-07-04", 200_000_000, "bod", "08:00")])
    ok(by_date(env.ledger()[0])[D(2026, 7, 6)]["flow_bod_vnd"] == 200e6,
       "B6: bod thứ Bảy phải rơi vào phiên thứ Hai 07-06")

    # --- B7. eod có khai giờ SAU lúc chụp NAV ngày đó ⇒ nav chưa chứa tiền ⇒ từ chối.
    snap = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0, False,
                                               "2026-07-03T19:10:51")]
    env = Env(tmp, "b7_late", snap, [dep("2026-07-03", 200_000_000, None, "21:00")])
    raises(acf.CashFlowError, env.ledger_raw, "B7 eod sau snapshot", "chưa chứa khoản này")
    env = Env(tmp, "b7_early", snap, [dep("2026-07-03", 200_000_000, None, "16:00")])
    ok(env.ledger()[0][-1]["unit_price"] == 10_200.0, "B7: eod trước snapshot phải được nhận")

    # --- B8. Đáp án BIẾT TRƯỚC: dựng chuỗi NAV từ tỉ suất ngày cho sẵn + dòng tiền ngẫu nhiên,
    # tỉ số giá đơn vị phải trả lại đúng tích (1 + r_t). Hạt giống cố định.
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
                flows.append(dep(day.isoformat(), f_bod, "bod", "10:00"))
            nav_after = (nav + f_bod) * (1 + r_t)
            if rng.random() < 0.4:
                f_eod = float(round(nav_after * rng.uniform(-0.3, 0.3)))
                flows.append(dep(day.isoformat(), f_eod))
            nav = nav_after + f_eod
            true_factor *= 1 + r_t
            navs.append((day.isoformat(), nav))
        env = Env(tmp, f"b8_{case}", navs, [f for f in flows if f["amount_vnd"]])
        ledger = env.ledger()[0]
        check_invariant(ledger, f"B8#{case}")
        got = ledger[-1]["unit_price"] / 10_000.0
        ok(abs(got / true_factor - 1) < 1e-9,
           f"B8#{case}: tỉ số giá {got!r} phải == tích tỉ suất thật {true_factor!r}")
        rp = env.returns(D(2026, 7, 13))["inception"]["return_pct"]
        ok(abs(rp - (true_factor - 1) * 100) <= 0.00051,
           f"B8#{case}: return_pct {rp} lệch tỉ suất thật {(true_factor - 1) * 100:.6f}")

    # --- B9. Nhân đôi mọi dòng tiền của ca "chỉ nạp vào tiền mặt, thị trường đứng yên từ lần nạp
    # đầu" ⇒ tỉ suất gia quyền thời gian KHÔNG đổi (cả hai quy ước chốt).
    for timing, t in (("eod", None), ("bod", "09:10")):
        results = []
        for k in (1, 2):
            stock = [1_000_000_000.0 * f for f in (1.01, 1.01 * 0.995, 1.01 * 0.995, 1.01 * 0.995,
                                                   1.01 * 0.995)]
            cash = [0.0, 0.0, 150e6 * k, 150e6 * k, 400e6 * k]
            days = ["2026-07-02", "2026-07-03", "2026-07-06", "2026-07-07", "2026-07-08"]
            env = Env(tmp, f"b9_{timing}_{k}", [(d, s + c) for d, s, c in zip(days, stock, cash)],
                      [dep("2026-07-06", 150e6 * k, timing if t else None, t),
                       dep("2026-07-08", 250e6 * k, timing if t else None, t)])
            ledger = env.ledger()[0]
            check_invariant(ledger, f"B9 {timing} k={k}")
            results.append((env.returns()["inception"]["return_pct"], ledger[-1]["unit_price"]))
        ok(results[0][0] == results[1][0] == 0.495,
           f"B9 {timing}: nhân đôi dòng tiền phải giữ tỉ suất +0,495%, được {results}")
        ok(abs(results[0][1] - results[1][1]) < 1e-6,
           f"B9 {timing}: giá đơn vị cuối phải như nhau, được {results}")


# ------------------------------------------------------------------ C. sổ trên đĩa chỉ-ghi-thêm
def part_c_sealed(tmp):
    nav = [("2026-07-02", 1_010_000_000.0), ("2026-07-03", 1_220_000_000.0, True),
           ("2026-07-06", 1_232_200_000.0)]
    flows = [dep("2026-07-03", 200_000_000)]
    env = Env(tmp, "c_seal", nav, flows)
    p = env.cli()
    ok(p.returncode == 0 and "chưa chốt dòng nào" in p.stdout and not env.sealed.exists(),
       f"C: chạy không --seal KHÔNG được tạo file, được rc={p.returncode} {p.stdout[-200:]}")
    p = env.cli("--seal", "--asof", "2026-07-03")
    ok(p.returncode == 0 and "vừa THÊM 3 dòng" in p.stdout,
       f"C: --asof 07-03 phải chốt 3 dòng (khởi điểm + 2), được {p.stdout} {p.stderr}")
    first = env.sealed.read_bytes()
    lines = first.decode().splitlines()
    ok(lines[0] == ",".join(nul.LEDGER_FIELDS) and len(lines) == 4, f"C: header + 3 dòng, được {lines}")
    ok(lines[1].startswith("2026-07-01,1000000000.0,0.0,0.0,0.0,100000.0,10000.0,False"),
       f"C: dòng khởi điểm sai: {lines[1]}")
    ok(lines[3].endswith(",True") and lines[2].endswith(",False"),
       f"C: cờ nav_is_estimate của ngày nguồn phải vào sổ, được {lines[2:]}")
    p = env.cli("--seal")
    second = env.sealed.read_bytes()
    ok(p.returncode == 0 and "vừa THÊM 1 dòng" in p.stdout and second.startswith(first)
       and len(second.decode().splitlines()) == 5,
       "C: chốt tiếp phải THÊM 1 dòng và giữ nguyên từng byte cũ")
    p = env.cli("--seal")
    ok(p.returncode == 0 and "vừa THÊM 0 dòng" in p.stdout and env.sealed.read_bytes() == second,
       "C: chốt lại khi không có dòng mới phải không đổi byte nào")
    sealed = nul.read_sealed(str(env.sealed))
    built = env.ledger()[0]
    ok(len(sealed) == len(built) and all(
        s[k] == b[k] for s, b in zip(sealed, built) for k in nul.LEDGER_FIELDS),
        "C: sổ đọc lại phải khớp ĐÚNG từng giá trị với chuỗi dựng (repr float khứ hồi)")
    ok(nul.diff_against_sealed(built, sealed) == [], "C: chuỗi dựng lại y nguyên ⇒ không lệch")

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
          flows2=flows + [dep("2026-07-02", 50_000_000)])
    drift("đổi cờ ước tính", ["2026-07-03 nav_is_estimate: đã chốt True → dựng lại False"],
          nav2=[nav[0], nav[1][:2], nav[2]])
    ok(env.cli().returncode == 0, "C: khôi phục nguồn ⇒ khớp lại, rc=0")

    # Thêm ngày mới SAU dòng đã chốt: hợp lệ, không phải lệch.
    env.write_nav(nav + [("2026-07-07", 1_240_000_000.0)])
    p = env.cli("--seal")
    ok(p.returncode == 0 and "vừa THÊM 1 dòng" in p.stdout and env.sealed.read_bytes().startswith(second),
       f"C: ngày mới phải chốt thêm được, được rc={p.returncode} {p.stderr}")

    # Sổ hỏng (ghi dở / sai header) ⇒ rc=1, không ghi đè — không coi như chưa có sổ.
    good = env.sealed.read_bytes()
    for label, bad in (("ghi dở", good[:-1]), ("sai header", b"date,nav\n" + good.split(b"\n", 1)[1]),
                       ("ngày lùi", good + good.splitlines(keepends=True)[1])):
        env.sealed.write_bytes(bad)
        p = env.cli("--seal")
        ok(p.returncode == 1 and env.sealed.read_bytes() == bad,
           f"C sổ hỏng ({label}): phải rc=1 và không đụng file, được rc={p.returncode}")
    env.sealed.write_bytes(good)

    # nav_period_returns đối chiếu sổ đã chốt: khớp ⇒ ghi mốc; lệch ⇒ từ chối công bố.
    rows = nul.load_nav_history("SpaceX", str(env.dir))
    inception = nul.load_inception("SpaceX", env.inc_path)
    fl = acf.load_flows("SpaceX", env.flows_path)
    r = must(lambda: npr.compute_period_returns("SpaceX", REPORT, rows, inception, fl,
                                                sealed_path=str(env.sealed)), "C: sổ khớp")
    ok(r.get("unit_ledger", {}).get("sealed_through") == "2026-07-07",
       f"C: sealed_through sai: {r.get('unit_ledger')}")
    ok("unit_ledger" not in npr.compute_period_returns("SpaceX", REPORT, rows, inception, fl),
       "C: không truyền sealed_path ⇒ không có khối unit_ledger")
    rows2 = [nul.NavRow(rows[0][0], rows[0][1] + 5.0)] + rows[1:]
    raises(nul.LedgerDriftError, lambda: npr.compute_period_returns(
        "SpaceX", REPORT, rows2, inception, fl, sealed_path=str(env.sealed)),
        "C: NAV quá khứ đổi mà vẫn công bố", "lệch +5.00 VND")

    # Đường CLI thật của nav_period_returns (dữ liệu thật, sổ chốt vào TEMPDIR qua env).
    real_dir = Path(tmp) / "real_ledger"
    real_dir.mkdir()
    canonical = Path(nul.ledger_path("SpaceX", nul.NAV_HISTORY_DIR))
    existed = canonical.exists()
    p = subprocess.run([sys.executable, str(BIN / "nav_unit_ledger.py"), "--account", "SpaceX",
                        "--ledger-dir", str(real_dir), "--seal"], capture_output=True, text=True)
    ok(p.returncode == 0, f"C: chốt sổ SpaceX thật vào tempdir phải rc=0: {p.stderr}")
    sealed_file = real_dir / "nav_unit_ledger_SpaceX.csv"
    env_vars = dict(os.environ, NAV_UNIT_LEDGER_DIR=str(real_dir))
    cmd = [sys.executable, str(BIN / "nav_period_returns.py"), "--account", "SpaceX"]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_vars)
    last = npr.load_nav_history("SpaceX")[-1][0].isoformat()
    ok(p.returncode == 0
       and json.loads(p.stdout).get("unit_ledger", {}).get("sealed_through") == last,
       f"C: CLI nav_period_returns phải khớp sổ đã chốt tới {last}: {p.stdout[-300:]} {p.stderr}")
    text = sealed_file.read_text(encoding="utf-8").splitlines(keepends=True)
    parts = text[5].split(",")
    parts[1] = repr(float(parts[1]) + 1000.0)
    sealed_file.write_text("".join(text[:5] + [",".join(parts)] + text[6:]), encoding="utf-8")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env_vars)
    ok(p.returncode == 1 and "KHÁC chuỗi dựng lại" in p.stderr and "lệch -1,000.00 VND" in p.stderr,
       f"C: sổ đã chốt lệch ⇒ CLI nav_period_returns phải rc=1 nêu độ lệch: {p.stderr[:400]}")
    ok(canonical.exists() == existed, "selfcheck KHÔNG được tạo/xoá sổ thật trong data/")


# ------------------------------------------------------------------ D. hai số của chủ TK + quy năm
def part_d_owner_numbers(tmp):
    mwr = npr.money_weighted_return
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
    # Dòng tiền đổi dấu ⇒ có thể 2 nghiệm hoặc 0 nghiệm ⇒ None + ghi chú, không chọn hộ.
    # Đặt y = √x: 1000y² − 2120y + 1122 = 1000(y − 1,02)(y − 1,1) ⇒ x = 1,0404 và 1,21.
    r, note = mwr(1000.0, 78.0, [(0.5, -2120.0), (0.0, 1200.0)])
    ok(r is None and "2 nghiệm" in note, f"D: 2 nghiệm phải trả None + ghi chú, được {r} {note}")
    # 1000y² − 2100y + 1200 có biệt thức âm ⇒ vô nghiệm.
    r, note = mwr(1000.0, 100.0, [(0.5, -2100.0), (0.0, 1300.0)])
    ok(r is None and "0 nghiệm" in note, f"D: 0 nghiệm phải trả None + ghi chú, được {r} {note}")
    # Một nghiệm dù rút gần hết giữa kỳ: 1000x − 990√x − 10,5 = 0.
    r, note = mwr(1000.0, 10.5, [(0.5, -990.0)])
    ok(note is None and abs(1000.0 * (1 + r) - 990.0 * (1 + r) ** 0.5 - 10.5) < 1e-6 and 0 < r < 0.01,
       f"D: rút gần hết vẫn phải có đúng một nghiệm nhỏ dương, được {r} {note}")

    # Trọng số thời gian trên chuỗi thật của B1 (kỳ 07-01 → 07-06 = 5 ngày lịch):
    #   eod 07-03 ⇒ w = 3/5 ; bod 07-03 ⇒ có mặt từ cuối 07-02 ⇒ w = 4/5.
    nav_e = [("2026-07-02", 1_000_000_000.0), ("2026-07-03", 1_220_000_000.0),
             ("2026-07-06", 1_220_000_000.0)]
    for timing, t, w in (("eod", None, 0.6), ("bod", "10:00", 0.8)):
        env = Env(tmp, f"d_{timing}", nav_e, [dep("2026-07-03", 200_000_000, timing if t else None, t)])
        p = env.returns()["inception"]
        want = round(mwr(1e9, 1.22e9, [(w, 200e6)])[0] * 100, 3)
        ok(p["days"] == 5 and p["mwr_pct"] == want,
           f"D {timing}: mwr_pct phải dùng w={w} ⇒ {want}, được {p['mwr_pct']}")
        ok(p["mwr_pct"] != p["return_pct"] or timing == "bod",
           f"D {timing}: có dòng tiền thì hai tỉ suất là hai số riêng")
        ok(p["pnl_vnd"] == 20_000_000.0, f"D {timing}: pnl_vnd phải 20tr, được {p['pnl_vnd']}")
    ok(mwr(1e9, 1.22e9, [(0.6, 200e6)])[0] != mwr(1e9, 1.22e9, [(0.8, 200e6)])[0],
       "D: trọng số thời gian khác nhau phải cho IRR khác nhau")

    # Chặn quy năm: < 365 ngày lịch ⇒ None + lý do; đủ 365 ⇒ có số.
    ok(npr.annualize_or_null(1.10, 364) == (None, npr.annualize_or_null(1.10, 364)[1])
       and "364 ngày lịch < 365" in npr.annualize_or_null(1.10, 364)[1],
       f"D: 364 ngày phải None kèm lý do, được {npr.annualize_or_null(1.10, 364)}")
    ok(npr.annualize_or_null(1.10, 365) == (10.0, None), "D: đúng 365 ngày ⇒ +10% giữ nguyên")
    ok(npr.annualize_or_null(1.21, 730) == (10.0, None), "D: 730 ngày +21% ⇒ quy năm +10%")
    ok(npr.annualize_or_null(0.0, 400)[0] is None, "D: hệ số <= 0 ⇒ None")
    # Kỳ dài hơn 1 năm trên chuỗi: SpaceX-giả từ 2026-07-01, NAV +21% sau 730 ngày.
    env = Env(tmp, "d_long", [("2026-07-02", 1_000_000_000.0), ("2027-06-30", 1_050_000_000.0),
                              ("2028-05-31", 1_200_000_000.0), ("2028-06-23", 1_205_000_000.0),
                              ("2028-06-30", 1_210_000_000.0)], [])
    short = env.returns(D(2027, 6, 30))["inception"]
    ok(short["days"] == 364 and short["annualized_return_pct"] is None
       and short["mwr_annualized_pct"] is None and "annualized_note" in short,
       f"D: 364 ngày trên chuỗi phải null kèm lý do, được {short}")
    long = env.returns(D(2028, 6, 30))
    ok(long["inception"]["days"] == 730 and long["inception"]["annualized_return_pct"] == 10.0
       and long["inception"]["mwr_annualized_pct"] == 10.0
       and "annualized_note" not in long["inception"],
       f"D: 730 ngày +21% ⇒ quy năm 10,0, được {long['inception']}")
    ok(long["mtd"]["annualized_return_pct"] is None and long["wtd"]["annualized_return_pct"] is None,
       "D: cùng báo cáo, kỳ MTD/WTD ngắn vẫn KHÔNG quy năm")


def main():
    tmp = tempfile.mkdtemp(prefix="nav_unit_ledger_selfcheck_")
    try:
        part_a_real()
        part_b_synthetic(tmp)
        part_c_sealed(tmp)
        part_d_owner_numbers(tmp)
    except AssertionError as exc:
        print(f"ASSERT-FAIL (sau {N} assertion PASS): {exc}", file=sys.stderr)
        return 1
    print(f"OK — {N} assertion PASS (nav_unit_ledger_selfcheck.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
