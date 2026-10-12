#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN của `cash_identity.py` (đẳng thức tiền) và các chỗ nối cảnh báo của nó
(`daily_nav_snapshot.cash_identity_lines`, `report_delivery_gate.cash_flow_warnings`,
cổng tỉ suất fail-closed).

Khép kín = không broker, không BigQuery, không đọc/ghi `data/` thật: mọi nguồn là file giả dựng
trong thư mục tạm và truyền đường dẫn tường minh; các đường dẫn mặc định của module bị trỏ sang một
thư mục KHÔNG tồn tại ngay sau import, nên chỗ nào quên truyền đường dẫn sẽ hỏng ồn ào. Module được
import từ CHÍNH thư mục chứa file này (chạy được từ worktree).

Dùng: python3 mike/bin/cash_identity_selfcheck.py          (tự chạy lại dưới 3 múi giờ khác)
"""
import contextlib
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

import account_cash_flows as acf  # noqa: E402
import cash_identity as ci  # noqa: E402

for _mod in (acf, ci):
    assert os.path.dirname(os.path.abspath(_mod.__file__)) == BIN, f"{_mod.__name__} không import từ {BIN}"
_NOWHERE = os.path.join(tempfile.gettempdir(), "cash_identity_selfcheck_KHONG_DUOC_DOC")
ci.EXEC_DIR = ci.INCEPTION_PATH = ci.SEED_PATH = acf.FLOWS_PATH = _NOWHERE
os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)

N = 0
TODAY = datetime.date(2026, 3, 31)
ACCOUNTS = {"SpaceX": "9000000001", "ZaloPay": "9000000002"}
FEE_BUY = ci.FEE_RATE_BUY_PCT / 100
FEE_SELL = ci.FEE_RATE_SELL_PCT / 100 + ci.SELL_TAX_RATE
PRICE = 10_000.0
# Hai tuần phiên: thứ Hai 02/03 → thứ Sáu 13/03/2026 (không có ngày nghỉ lễ).
DAYS = [datetime.date(2026, 3, d) for d in (2, 3, 4, 5, 6, 9, 10, 11, 12, 13)]


def ok(cond, msg):
    global N
    if not cond:
        raise AssertionError(msg)
    N += 1


def at(day, hhmmss):
    """`at(3, "10:30")` → 2026-03-03 10:30:00 (ICT naive)."""
    parts = [int(x) for x in hhmmss.split(":")] + [0]
    return datetime.datetime(2026, 3, day, parts[0], parts[1], parts[2])


def utc_z(moment, exact=False):
    """ICT naive → chuỗi `modifiedDate` kiểu DNSE (UTC, 9 chữ số lẻ, hậu tố Z)."""
    return (moment - datetime.timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S") + ("Z" if exact else ".123456789Z")


class World:
    """Bộ dữ liệu giả cho hai tài khoản dùng CHUNG file dnse_raw. `events[account]` là list
    `(thời điểm, loại, tham số…)`; số dư tại mỗi lần chụp = số đầu + mọi sự kiện đã xảy ra."""

    def __init__(self, tmp, name):
        self.dir = Path(tmp) / name
        (self.dir / "logs").mkdir(parents=True)
        self.events = {a: [] for a in ACCOUNTS}
        self.snaps = {a: {d: datetime.datetime.combine(d, datetime.time(19, 10, 5 + i))
                          for d in DAYS} for i, a in enumerate(ACCOUNTS)}
        self.flows = {a: [] for a in ACCOUNTS}
        self.seed = {}
        self.blank_ts = set()            # (account, date) có balance_ts rỗng
        self.no_balances = set()         # (account, date) không ghi bản ghi balances
        self.cum_div_excl = {}           # (account, date) -> cổ tức bị loại khỏi cột cash của dòng đó
        self.extra_raw = {}              # (account, date) -> bản ghi dnse_raw thêm vào đúng lúc chụp

    def add(self, account, moment, kind, *args, **kw):
        self.events[account].append((moment, kind, args, kw))
        return self

    # --- đường dẫn truyền cho module
    @property
    def paths(self):
        return {"nav_dir": str(self.dir / "logs"), "raw_dir": str(self.dir / "logs"),
                "flows_path": str(self.dir / "flows.json"),
                "inception_path": str(self.dir / "inception.json"),
                "seed_path": str(self.dir / "seed.json"), "today": TODAY}

    def build(self):
        raw = {}                                     # ngày -> list (ts, dòng json)
        order_id = 0

        def log(day, ts, rec):
            raw.setdefault(day, []).append((ts.isoformat(), json.dumps(rec, ensure_ascii=False)))

        for account, account_no in ACCOUNTS.items():
            cash, debt, egg, recv, offbook = 200_000_000.0, 0.0, 300_000_000.0, 0.0, 0.0
            qty = {"AAA": 30_000.0, "BBB": 20_000.0}
            pending = sorted(self.events[account], key=lambda e: e[0])
            rows, last_day = [], None
            for day in DAYS:
                snap = self.snaps[account][day]
                if last_day is not None:             # lãi Trứng vàng theo ngày lịch, lãi kép
                    for _ in range((snap.date() - last_day).days):
                        egg += egg * ci.EGG_DAILY_RATE
                last_day = snap.date()
                while pending and pending[0][0] <= snap:
                    moment, kind, args, kw = pending.pop(0)
                    if kind in ("buy", "sell"):
                        symbol, n = args
                        value = n * PRICE
                        if kind == "buy":
                            cash -= value * (1 + FEE_BUY)
                            qty[symbol] = qty.get(symbol, 0.0) + n
                        else:
                            cash += value * (1 - FEE_SELL)
                            qty[symbol] = qty.get(symbol, 0.0) - n
                        if kw.get("log", True):
                            order_id += 1
                            log(moment.date(), moment, {
                                "ts": moment.isoformat(), "kind": "orders", "account_no": account_no,
                                "payload": {"orders": [{
                                    "id": order_id, "accountNo": account_no, "symbol": symbol,
                                    "side": "NB" if kind == "buy" else "NS", "fillQuantity": n,
                                    "averagePrice": PRICE, "orderStatus": "Filled",
                                    "modifiedDate": utc_z(moment, kw.get("exact", False))}]}})
                    elif kind == "dividend_declared":
                        cash += args[0]
                        recv += args[0]
                    elif kind == "dividend_paid":
                        recv -= args[0]
                        cash -= args[0] * ci.DIVIDEND_TAX_RATE
                    elif kind == "egg_in":
                        cash -= args[0]
                        egg += args[0]
                    elif kind == "egg_out":          # rút Trứng vàng, mất `loss` (khấu trừ lãi)
                        egg -= args[0]
                        cash += args[0] - kw.get("loss", 0.0)
                    elif kind == "offbook_in":       # chuyển tiền sang tài sản off-book khai tay
                        cash -= args[0]
                        offbook += args[0]
                    elif kind == "borrow":
                        cash += args[0]
                        debt += args[0]
                    elif kind == "repay":
                        cash -= args[0]
                        debt -= args[0]
                    elif kind == "external":         # nạp (+) / rút (−) THẬT, không ai khai
                        cash += args[0]
                    else:
                        raise ValueError(kind)
                mtm = sum(q * PRICE for q in qty.values())
                ts = snap.isoformat()
                if (account, day) not in self.no_balances:
                    log(snap.date(), snap, {
                        "ts": ts, "kind": "balances", "account_no": account_no,
                        "payload": {"stock": {"totalCash": cash, "totalDebt": debt,
                                              "cashDividendReceiving": recv},
                                    "egg": {"totalValue": egg}}})
                log(snap.date(), snap, {
                    "ts": ts, "kind": "positions", "account_no": account_no,
                    "payload": {"positions": [{"symbol": s, "accountNo": account_no,
                                               "openQuantity": q} for s, q in qty.items()]}})
                # Cổ tức phải thu chưa qua ex-date: daily_nav_snapshot TRỪ khỏi cột cash và ghi
                # riêng ở cum_dividend_excl (NAV không đổi) — đẳng thức phải cộng lại.
                excl = self.cum_div_excl.get((account, day), 0.0)
                rows.append([day.isoformat(), f"{mtm + cash - excl - debt + egg + offbook:.0f}", f"{mtm:.0f}",
                             f"{cash - excl:.0f}", f"{debt:.0f}", f"{offbook:.0f}", f"{egg:.0f}",
                             "" if (account, day) in self.blank_ts else ts, f"{excl:.0f}", "False", "live"])
                for extra in self.extra_raw.get((account, day), []):   # "ts" riêng nếu có, không thì lúc chụp
                    when = datetime.datetime.fromisoformat(extra["ts"]) if "ts" in extra else snap
                    log(when.date(), when, dict(extra, ts=when.isoformat()))
            with open(self.dir / "logs" / f"nav_history_{account}.csv", "w", encoding="utf-8") as f:
                f.write("date,nav,mtm_stock,cash,margin_debt,offbook_assets,egg_assets,balance_ts,"
                        "cum_dividend_excl,nav_is_estimate,nav_source\n")
                f.writelines(",".join(r) + "\n" for r in rows)
        for day, recs in raw.items():                # hai tài khoản XEN KẼ trong cùng file
            with open(self.dir / "logs" / f"dnse_raw_{day.isoformat()}.jsonl", "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for _, line in sorted(recs))
        (self.dir / "flows.json").write_text(json.dumps(self.flows), encoding="utf-8")
        (self.dir / "inception.json").write_text(json.dumps(
            {a: {"account_no": no, "inception_date": "2026-02-27", "starting_capital": 1_000_000_000}
             for a, no in ACCOUNTS.items()}), encoding="utf-8")
        (self.dir / "seed.json").write_text(json.dumps(self.seed), encoding="utf-8")
        return self

    def check(self, account, **kw):
        return ci.check_account(account, **dict(self.paths, **kw))


def internal_only(world):
    """Mọi loại khoản NỘI BỘ, không có dòng tiền ngoài nào: khớp lệnh lớn, cổ tức chốt quyền rồi
    chi trả, chuyển tiền ↔ Trứng vàng, vay rồi trả ký quỹ — không cái nào được thành cảnh báo."""
    world.add("SpaceX", at(3, "09:40"), "sell", "AAA", 20_000)          # bán 200tr
    world.add("SpaceX", at(4, "10:05"), "buy", "BBB", 5_000)
    world.add("SpaceX", at(4, "17:30"), "dividend_declared", 6_000_000)
    world.add("SpaceX", at(5, "16:00"), "egg_in", 150_000_000)
    world.add("SpaceX", at(9, "08:00"), "borrow", 100_000_000)
    world.add("SpaceX", at(9, "09:30"), "buy", "AAA", 9_000)
    world.add("SpaceX", at(10, "16:30"), "dividend_paid", 6_000_000)
    world.add("SpaceX", at(11, "16:00"), "repay", 100_000_000)
    world.add("ZaloPay", at(3, "13:10"), "buy", "AAA", 3_000)
    world.add("ZaloPay", at(10, "10:10"), "sell", "BBB", 20_000)        # ZaloPay bán 200tr ngày 10/03
    return world


def window(result, day1):
    return next(w for w in result["windows"] if w["date1"] == datetime.date(2026, 3, day1))


def run_checks(tmp):
    digest = []

    def note(label, result):
        digest.append([label] + [[w["date1"].isoformat(), w["checkable"], round(w.get("unexplained", 0.0), 2),
                                  bool(w.get("suspect"))] for w in result["windows"]])

    thr = ci.THRESHOLD_PCT
    ok(thr == 0.05, f"ngưỡng phải là 0,05% NAV (đo 2026-10-12), được {thr}")
    ok(ci.SESSION_CLOSE_ICT == acf.SESSION_CLOSE_ICT == datetime.time(14, 45), "giờ đóng cửa dùng chung")

    # ---- A. chỉ có khoản nội bộ ⇒ 0 cảnh báo, phần dư ~0, cả hai tài khoản
    base = internal_only(World(tmp, "base")).build()
    base_res = {a: base.check(a) for a in ACCOUNTS}
    for account, res in base_res.items():
        note(f"A/{account}", res)
        ok(len(res["windows"]) == len(DAYS) - 1 and not res["uncheckable"],
           f"A: {account} phải có {len(DAYS) - 1} cửa sổ kiểm được, được {len(res['windows'])}")
        ok(not res["suspects"], f"A: {account} chỉ có khoản nội bộ ⇒ 0 chờ khai, được "
                                f"{[(w['date1'], w['unexplained']) for w in res['suspects']]}")
        worst = max(abs(w["unexplained"]) for w in res["windows"])
        ok(worst < 500, f"A: {account} phần dư lớn nhất phải < 500đ (chỉ còn lãi kép), được {worst:,.2f}")
    w = window(base_res["SpaceX"], 3)
    ok(w["sell"] == 200_000_000 and w["n_fills"] == 1 and abs(w["fees"] - 200_000_000 * FEE_SELL) < 1e-6,
       f"A: bán 200tr phải ra phí+thuế {200_000_000 * FEE_SELL:,.0f}, được {w['fees']:,.2f}")
    ok(window(base_res["SpaceX"], 4)["dividend"] == 6_000_000, "A: cổ tức chốt quyền = mức tăng phải thu")
    ok(window(base_res["SpaceX"], 10)["dividend"] == -300_000, "A: chi trả cổ tức ⇒ trừ đúng thuế 5%")
    ok(abs(window(base_res["SpaceX"], 9)["egg_interest"] - 450_000_000 * ci.EGG_DAILY_RATE * 3) < 1_000,
       f"A: lãi Trứng vàng qua cuối tuần = 3 ngày, được {window(base_res['SpaceX'], 9)['egg_interest']:,.0f}")
    # §12: ZaloPay bán 200tr ngày 10/03 trong CÙNG file dnse_raw — không được lọt vào SpaceX
    ok(window(base_res["SpaceX"], 10)["n_fills"] == 0 and window(base_res["ZaloPay"], 10)["sell"] == 200_000_000,
       "A/§12: lệnh của ZaloPay không được tính cho SpaceX")
    ok(window(base_res["ZaloPay"], 4)["dividend"] == 0, "A/§12: cổ tức của SpaceX không được tính cho ZaloPay")

    # ---- B. dòng tiền ngoài CHƯA KHAI: ngay trên / ngay dưới ngưỡng × nạp/rút × 3 thời điểm
    cases = {"trong phiên": (at(10, "10:30"), 10), "sau đóng cửa": (at(10, "16:00"), 10),
             "cuối tuần": (at(7, "11:00"), 9)}
    for label, (moment, day1) in cases.items():
        nav0 = window(base_res["SpaceX"], day1)["nav0"]
        edge = nav0 * thr / 100
        for sign in (1, -1):
            for delta, expect in ((2_000, True), (-2_000, False)):
                amount = sign * (edge + delta)
                wd = internal_only(World(tmp, f"B_{day1}_{moment:%H%M}_{sign}_{delta}"))
                wd.add("SpaceX", moment, "external", amount).build()
                res = {a: wd.check(a) for a in ACCOUNTS}
                note(f"B/{label}/{sign}/{delta}", res["SpaceX"])
                hit = [w["date1"].day for w in res["SpaceX"]["suspects"]]
                tag = f"B: {'nạp' if sign > 0 else 'rút'} {abs(amount):,.0f} ({label}, ngưỡng {edge:,.0f})"
                ok(hit == ([day1] if expect else []), f"{tag} phải {'bị bắt ở cửa sổ → ' + str(day1) if expect else 'KHÔNG bị bắt'}, được {hit}")
                got = window(res["SpaceX"], day1)["unexplained"]
                ok(abs(got - amount) < 500, f"{tag}: số ước lượng phải ≈ {amount:,.0f}, được {got:,.0f}")
                ok(abs(window(res["SpaceX"], day1)["pct_nav"] - got / nav0 * 100) < 1e-9,
                   f"{tag}: %NAV phải tính trên NAV ĐẦU cửa sổ ({nav0:,.0f})")
                ok(not res["ZaloPay"]["suspects"], f"{tag}: ZaloPay cùng ngày KHÔNG có dòng tiền ⇒ phải sạch")
                ok(res["SpaceX"]["suspects"] != res["ZaloPay"]["suspects"] or not expect,
                   f"{tag}: hai tài khoản phải cho kết quả KHÁC nhau")
                if expect:
                    line = ci.suspect_line("SpaceX", res["SpaceX"]["suspects"][0])
                    ok(ci.WARNING_MARKER in line and "(SpaceX)" in line
                       and ("nghi NẠP vào" if sign > 0 else "nghi RÚT ra") in line
                       and f"{abs(got):,.0f} VND" in line and f"2026-03-{day1:02d}" in line
                       and "Đã đọc:" in line and "account_cash_flows.json" in line,
                       f"{tag}: cảnh báo phải nêu tài khoản, chiều, số tiền, ngày, bằng chứng; được {line}")
                    ok("số lượng vị thế khớp đúng với lệnh đã đọc" in line,
                       f"{tag}: lệnh đủ log ⇒ phải nói phần dư không đến từ lệnh thiếu log; được {line}")

    # ---- C. hai tài khoản đổi vai: dòng tiền ở ZaloPay, SpaceX sạch
    wd = internal_only(World(tmp, "C")).add("ZaloPay", at(11, "20:00"), "external", -3_000_000).build()
    res = {a: wd.check(a) for a in ACCOUNTS}
    note("C/ZaloPay", res["ZaloPay"])
    ok([w["date1"].day for w in res["ZaloPay"]["suspects"]] == [12] and not res["SpaceX"]["suspects"],
       "C: rút 3tr ở ZaloPay tối 11/03 (sau lần chụp) ⇒ bắt ở cửa sổ → 12/03 của ZaloPay, SpaceX sạch")

    # ---- D. đã khai / khai sai / khẳng định không phải nạp/rút
    amount = 5_000_000.0

    def declared(name, records):
        wd = internal_only(World(tmp, name)).add("SpaceX", at(10, "10:30"), "external", amount)
        wd.flows["SpaceX"] = records
        return wd.build().check("SpaceX")

    def rec(date, time_ict, amt, kind="deposit"):
        out = {"date": date, "amount_vnd": amt, "kind": kind, "evidence": "sao kê giả của selfcheck"}
        return dict(out, time_ict=time_ict) if time_ict else out

    res = declared("D_ok", [rec("2026-03-10", "10:30", amount)])
    note("D/ok", res)
    ok(not res["suspects"] and window(res, 10)["declared"] == amount and abs(window(res, 10)["unexplained"]) < 500,
       f"D: khai đúng ngày giờ số tiền ⇒ hết cảnh báo, được {[(w['date1'], w['unexplained']) for w in res['suspects']]}")
    wd = internal_only(World(tmp, "D_exact")).add("SpaceX", at(10, "19:10:05"), "external", amount)
    wd.flows["SpaceX"] = [rec("2026-03-10", "19:10:05", amount)]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 10)["declared"] == amount,
       "D: tiền vào ĐÚNG giây chụp (đã nằm trong số dư) khai đúng giây đó ⇒ thuộc cửa sổ kết thúc ở lần chụp ấy")
    res = declared("D_late", [rec("2026-03-10", "19:30", amount)])
    note("D/late", res)
    got = {w["date1"].day: round(w["unexplained"] / 1e6, 1) for w in res["suspects"]}
    ok(got == {10: 5.0, 11: -5.0},
       f"D: giờ khai SAU lần chụp (tiền đã nằm trong số dư) ⇒ hai cửa sổ lệch +5tr/−5tr, được {got}")
    res = declared("D_half", [rec("2026-03-10", "10:30", amount / 2)])
    ok([w["date1"].day for w in res["suspects"]] == [10] and abs(window(res, 10)["unexplained"] - amount / 2) < 500,
       "D: khai thiếu một nửa ⇒ vẫn cảnh báo phần còn lại")
    ok("đã trừ +2,500,000 VND dòng tiền đã khai" in ci.suspect_line("SpaceX", res["suspects"][0]),
       "D: cảnh báo phải nói đã trừ bao nhiêu dòng tiền đã khai")
    res = declared("D_ack", [rec("2026-03-10", None, 0, "market_only")])
    ok(not res["suspects"] and window(res, 10)["acked"] and abs(window(res, 10)["unexplained"] - amount) < 500,
       "D: bản ghi market_only đúng ngày ⇒ thôi cảnh báo nhưng phần dư vẫn hiện trong bảng")
    ok("đã khẳng định không nạp/rút" in ci._table(res), "D: bảng phải đánh dấu cửa sổ đã được khẳng định")
    for day in ("2026-03-09", "2026-03-11"):
        res = declared(f"D_ack_{day}", [rec(day, None, 0, "market_only")])
        ok([w["date1"].day for w in res["suspects"]] == [10],
           f"D: market_only ngày {day} KHÔNG thuộc cửa sổ → 10/03 ⇒ vẫn cảnh báo")
    res = declared("D_wknd", [rec("2026-03-07", None, 0, "market_only")])       # thứ Bảy
    ok([w["date1"].day for w in res["suspects"]] == [10], "D: market_only thứ Bảy chỉ phủ cửa sổ → thứ Hai")

    # ---- E. lần chụp giữa phiên: lệnh trước và sau lần chụp phải vào đúng cửa sổ
    wd = World(tmp, "E")
    wd.snaps["SpaceX"][datetime.date(2026, 3, 4)] = at(4, "10:00:00")
    wd.add("SpaceX", at(4, "09:30"), "sell", "AAA", 8_000).add("SpaceX", at(4, "11:00"), "buy", "BBB", 6_000)
    wd.add("SpaceX", at(4, "09:59:59"), "buy", "AAA", 1_000).add("SpaceX", at(4, "10:00:01"), "sell", "BBB", 2_000)
    wd.add("SpaceX", at(4, "10:00:00"), "buy", "AAA", 500, exact=True)       # đúng giây chụp: đã nằm trong số dư
    res = wd.build().check("SpaceX")
    note("E", res)
    ok(not res["suspects"] and max(abs(w["unexplained"]) for w in res["windows"]) < 500,
       f"E: chụp 10:00 giữa phiên — lệnh chia đúng theo giờ ⇒ phần dư ~0, được "
       f"{[(w['date1'].day, round(w['unexplained'])) for w in res['windows']]}")
    ok((window(res, 4)["n_fills"], window(res, 5)["n_fills"]) == (3, 2),
       "E: 2 lệnh trước 10:00 + 1 lệnh đúng 10:00:00 vào cửa sổ → 04/03, 2 lệnh sau vào cửa sổ → 05/03")

    # ---- F. lệnh khớp KHÔNG có log ⇒ cảnh báo kèm bằng chứng lệch vị thế; fill broker xác nhận ⇒ hết
    wd = World(tmp, "F").add("SpaceX", at(5, "10:00"), "sell", "AAA", 600, log=False).build()
    res = wd.check("SpaceX")
    ok([w["date1"].day for w in res["suspects"]] == [5], "F: bán 6tr không có log ⇒ phần dư dương bị bắt")
    line = ci.suspect_line("SpaceX", res["suspects"][0])
    ok("số lượng vị thế đổi KHÔNG khớp lệnh đã đọc: AAA -600" in line and "chưa chắc là nạp/rút" in line,
       f"F: phải chỉ ra AAA lệch −600 không có lệnh; được {line}")
    ok("KHÔNG có bản ghi orders nào của tài khoản các ngày 2026-03-04, 2026-03-05" in line,
       f"F: phải nói dnse_raw không có bản ghi orders những ngày nào; được {line}")
    wd.seed = {"SpaceX": {"missing_fills_broker_confirmed": [
        {"date": "2026-03-05", "ticker": "AAA", "side": "sell", "qty": 600, "price": PRICE,
         "evidence": "email khớp lệnh giả"}]}}
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["sell"] == 6_000_000,
       "F: fill broker xác nhận trong account_seed_capital ⇒ đẳng thức khép, hết cảnh báo")
    ok(not wd.check("ZaloPay")["suspects"] and window(wd.check("ZaloPay"), 5)["n_fills"] == 0,
       "F/§12: fill xác nhận của SpaceX không được tính cho ZaloPay")

    # ---- G. khoản nội bộ KHÔNG mô hình hoá ⇒ cảnh báo có ghi chú đúng loại
    wd = World(tmp, "G").add("SpaceX", at(10, "16:00"), "egg_out", 250_000_000, loss=600_000).build()
    res = wd.check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok([w["date1"].day for w in res["suspects"]] == [10] and "Trứng vàng giảm 250," in line
       and "khấu trừ lãi" in line, f"G: rút Trứng vàng mất 600k ⇒ cảnh báo kèm ghi chú Trứng vàng; được {line}")
    wd = World(tmp, "G2").add("SpaceX", at(3, "08:00"), "borrow", 300_000_000)
    wd.add("SpaceX", at(10, "16:00"), "external", -1_000_000).build()            # "lãi vay post dồn"
    line = ci.suspect_line("SpaceX", wd.check("SpaceX")["suspects"][0])
    ok("có dư nợ ký quỹ (300,000,000 → 300,000,000)" in line and "lãi vay ước" in line,
       f"G: cửa sổ có dư nợ ⇒ ghi chú lãi vay ước tính; được {line}")
    ok(not [w for w in World(tmp, "G3").build().check("SpaceX")["windows"] if w["notes"]],
       "G: tài khoản yên tĩnh không được có ghi chú nào")

    # ---- G4. off-book khai tay và cổ tức bị loại khỏi cột cash đều nằm trong "tiền sở hữu"
    wd = World(tmp, "G4").add("SpaceX", at(4, "16:00"), "offbook_in", 120_000_000)
    wd.add("SpaceX", at(5, "17:30"), "dividend_declared", 4_000_000)
    wd.cum_div_excl[("SpaceX", datetime.date(2026, 3, 5))] = 4_000_000.0
    res = wd.build().check("SpaceX")
    note("G4", res)
    ok(not res["suspects"] and max(abs(w["unexplained"]) for w in res["windows"]) < 500,
       f"G4: chuyển sang off-book + cổ tức đang bị loại khỏi cột cash ⇒ đẳng thức vẫn khép, được "
       f"{[(w['date1'].day, round(w['unexplained'])) for w in res['windows']]}")
    ok(any("off-book khai tay" in n for n in window(res, 4)["notes"]), "G4: cửa sổ có off-book phải có ghi chú")
    # Bản ghi balances KHÔNG gắn tài khoản (log cũ) nằm đúng lúc chụp: không được dùng cho ai cả.
    wd = World(tmp, "G5")
    wd.no_balances.add(("SpaceX", datetime.date(2026, 3, 5)))
    wd.extra_raw[("SpaceX", datetime.date(2026, 3, 5))] = [
        {"kind": "balances", "payload": {"stock": {"cashDividendReceiving": 9_000_000}, "egg": {"totalValue": 1}}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["dividend"] == 0 and window(res, 6)["dividend"] == 0
       and any("không đọc được cashDividendReceiving" in n for n in window(res, 5)["notes"]),
       "G5/§12: bản ghi balances không gắn tài khoản không được tính là của SpaceX (coi như không có)")
    # Bản ghi orders KHÔNG gắn tài khoản (log trước 2026-07-06) chứa lệnh của CẢ HAI tài khoản và một
    # lệnh chưa khớp: mỗi tài khoản chỉ nhận lệnh mang accountNo của mình.
    wd = World(tmp, "G6").add("SpaceX", at(5, "10:00"), "sell", "AAA", 600, log=False)
    legacy = [{"id": 901, "accountNo": ACCOUNTS["SpaceX"], "symbol": "AAA", "side": "NS", "fillQuantity": 600,
               "averagePrice": PRICE, "modifiedDate": utc_z(at(5, "10:00"))},
              {"id": 902, "accountNo": ACCOUNTS["ZaloPay"], "symbol": "BBB", "side": "NS", "fillQuantity": 5_000,
               "averagePrice": PRICE, "modifiedDate": utc_z(at(5, "10:01"))},
              {"id": 903, "accountNo": ACCOUNTS["SpaceX"], "symbol": "BBB", "side": "NB", "fillQuantity": 0,
               "price": PRICE, "modifiedDate": utc_z(at(5, "10:02"))}]
    wd.extra_raw[("SpaceX", datetime.date(2026, 3, 5))] = [{"kind": "orders", "payload": {"orders": legacy}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["n_fills"] == 1 and window(res, 5)["sell"] == 6_000_000,
       f"G6/§12: bản ghi orders không gắn tài khoản — SpaceX chỉ nhận lệnh 901 của mình, được "
       f"{window(res, 5)['n_fills']} lệnh, bán {window(res, 5)['sell']:,.0f}")
    ok(window(wd.check("ZaloPay"), 5)["sell"] == 50_000_000, "G6/§12: lệnh 902 thuộc ZaloPay")
    # Phải thu cổ tức đọc ở bản ghi balances ĐÚNG lúc chụp, không phải bản ghi muộn hơn trong ngày.
    wd = World(tmp, "G7").add("SpaceX", at(5, "09:00"), "dividend_declared", 7_000_000)
    wd.extra_raw[("SpaceX", datetime.date(2026, 3, 4))] = [
        {"kind": "balances", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-04T23:00:00",
         "payload": {"stock": {"cashDividendReceiving": 7_000_000}, "egg": {"totalValue": 1}}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["dividend"] == 7_000_000,
       f"G7: bản ghi balances 23:00 (sau lần chụp 19:10) không được dùng cho lần chụp 04/03, được cổ tức "
       f"{window(res, 5)['dividend']:,.0f}")

    # ---- H. thiếu bằng chứng ⇒ nói rõ, không coi là 0 một cách im lặng
    wd = World(tmp, "H").add("SpaceX", at(4, "17:30"), "dividend_declared", 6_000_000)
    wd.no_balances.add(("SpaceX", datetime.date(2026, 3, 4)))
    res = wd.build().check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(res["suspects"] and "không đọc được cashDividendReceiving ở lần chụp 2026-03-04 19:10:05" in line,
       f"H: thiếu bản ghi balances ⇒ cảnh báo phải nói không đọc được phải thu cổ tức; được {line}")
    wd = World(tmp, "H2")
    wd.blank_ts.add(("SpaceX", datetime.date(2026, 3, 5)))
    res = wd.build().check("SpaceX")
    ok([w["date1"].day for w in res["uncheckable"]] == [5, 6] and not res["suspects"]
       and "balance_ts rỗng" in res["uncheckable"][0]["reason"],
       f"H: dòng thiếu balance_ts ⇒ 2 cửa sổ quanh nó KHÔNG kiểm được, được {res['uncheckable']}")
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 2 and all("không kiểm được cửa sổ" in x for x in lines),
       f"H: cửa sổ không kiểm được phải hiện ở cảnh báo, được {lines}")
    wd = World(tmp, "H3")
    wd.snaps["SpaceX"][datetime.date(2026, 3, 5)] = at(4, "18:00")               # chụp TRƯỚC dòng 04/03
    res = wd.build().check("SpaceX")
    ok([w["date1"].day for w in res["uncheckable"]] == [5] and "không sau dòng" in res["uncheckable"][0]["reason"],
       "H: lần chụp không tăng ⇒ cửa sổ không kiểm được, nêu hai lần chụp")

    # ---- I. `asof`, lỗi nguồn, và đường hiển thị không bao giờ ném lỗi
    wd = internal_only(World(tmp, "I")).add("SpaceX", at(10, "10:30"), "external", amount).build()
    ok(not wd.check("SpaceX", asof=datetime.date(2026, 3, 9))["suspects"]
       and len(wd.check("SpaceX", asof=datetime.date(2026, 3, 10))["suspects"]) == 1,
       "I: asof trước ngày có dòng tiền ⇒ chưa thấy; asof đúng ngày ⇒ thấy")
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 1 and ci.WARNING_MARKER in lines[0], f"I: warning_lines phải ra đúng 1 dòng, được {lines}")
    wd2 = internal_only(World(tmp, "I2")).add("SpaceX", at(10, "10:30"), "external", amount)
    wd2.add("SpaceX", at(10, "09:20"), "sell", "AAA", 1_000)
    wd2.extra_raw[("SpaceX", datetime.date(2026, 3, 10))] = [
        {"kind": "positions", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-10T23:30:00",
         "payload": {"positions": [{"symbol": "AAA", "accountNo": ACCOUNTS["SpaceX"], "openQuantity": 1}]}}]
    lines = ci.warning_lines("SpaceX", **wd2.build().paths)
    ok(len(lines) == 1 and "1 lệnh khớp (bán 10,000,000" in lines[0]
       and "số lượng vị thế khớp đúng với lệnh đã đọc" in lines[0],
       f"I: có lệnh BÁN đủ log + bản ghi vị thế 23:30 (sau lần chụp) ⇒ vị thế vẫn phải khớp; được {lines}")
    os.remove(wd.paths["flows_path"])
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0] and "KHÔNG có sổ dòng tiền" in lines[0],
       f"I: thiếu sổ dòng tiền ⇒ một dòng nêu đúng lỗi, không ném; được {lines}")
    lines = ci.warning_lines("KhongCo", **base.paths)
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0], f"I: tài khoản lạ ⇒ một dòng lỗi; được {lines}")
    lines = ci.warning_lines("SpaceX")                 # không truyền đường dẫn ⇒ mặc định đã bị vô hiệu
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0] and "KHONG_DUOC_DOC" in lines[0],
       f"I: selfcheck không được chạm dữ liệu mặc định; được {lines}")

    # ---- J. chỗ nối: dòng 💰 NAV, cổng giao báo cáo
    wd = internal_only(World(tmp, "J")).add("SpaceX", at(10, "10:30"), "external", amount)
    wd.add("ZaloPay", at(10, "20:00"), "external", 3_000_000)                    # nạp thật, có khai
    wd.flows["ZaloPay"] = [rec("2026-03-10", "20:00", 3_000_000),               # vào dòng 11/03
                           rec("2026-03-13", "20:00", 7_000_000)]               # sau lần chụp cuối ⇒ TREO
    wd.build()
    import daily_nav_snapshot as dns
    kw = {k: v for k, v in wd.paths.items()}
    lines = dns.cash_identity_lines("SpaceX", "2026-03-10", **kw)
    ok(len(lines) == 1 and lines[0].startswith("   ⚠️ " + ci.WARNING_MARKER) and "5,000,00" in lines[0],
       f"J: dòng 💰 NAV phải mang cảnh báo chờ khai (thụt 3 dấu cách), được {lines}")
    ok(dns.cash_identity_lines("SpaceX", "2026-03-09", **kw) == [] and dns.cash_identity_lines("ZaloPay", "2026-03-13", **kw) == [],
       "J: ngày trước dòng tiền / tài khoản khác ⇒ không có dòng cảnh báo nào")
    lines = dns.cash_identity_lines("SpaceX", "không-phải-ngày", **kw)
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0], f"J: đường hiển thị không được ném lỗi, được {lines}")

    with contextlib.redirect_stderr(io.StringIO()):
        import report_delivery_gate as g
    gate_kw = {k: v for k, v in wd.paths.items()}
    report = Path(tmp) / "SpaceX_weekly_report_2026-03-09_to_2026-03-13.md"
    report.write_text("# báo cáo giả\n", encoding="utf-8")
    lines = g.cash_flow_warnings(report, **gate_kw)
    ok(len(lines) == 1 and ci.WARNING_MARKER in lines[0] and "(SpaceX)" in lines[0],
       f"J: cổng phải thấy khoản chờ khai của SpaceX, được {lines}")
    both = Path(tmp) / "SpaceX_ZaloPay_weekly_report_2026-03-09_to_2026-03-13.md"
    both.write_text("x\n", encoding="utf-8")
    lines = g.cash_flow_warnings(both, **gate_kw)
    ok(len(lines) == 2 and g.PENDING_FLOW_MARKER in lines[1] and "(ZaloPay)" in lines[1]
       and "+7,000,000 VND" in lines[1], f"J: cổng phải thấy cả dòng tiền TREO của ZaloPay, được {lines}")
    day10 = Path(tmp) / "ZaloPay_daily_report_2026-03-10.md"
    day10.write_text("x\n", encoding="utf-8")
    lines = g.cash_flow_warnings(day10, **gate_kw)
    ok(len(lines) == 1 and g.PENDING_FLOW_MARKER in lines[0] and "+3,000,000 VND" in lines[0]
       and "2026-03-10 20:00" in lines[0],
       f"J: báo cáo ngày 10/03 — khoản khai 20:00 (sau lần chụp) còn TREO tính tới ngày đó; được {lines}")
    early = Path(tmp) / "SpaceX_ZaloPay_daily_report_2026-03-09.md"
    early.write_text("x\n", encoding="utf-8")
    ok(g.cash_flow_warnings(early, **gate_kw) == [], "J: báo cáo ngày 09/03 — chưa có gì để cảnh báo")
    other = Path(tmp) / "spend_report_2026-03-13.md"
    other.write_text("x\n", encoding="utf-8")
    ok(g.cash_flow_warnings(other, **gate_kw) == [], "J: báo cáo không thuộc tài khoản nào ⇒ bỏ qua")
    for text, needle in (("x\n", "KHÔNG có cụm 'DÒNG TIỀN CHỜ KHAI'"),
                         (f"⚠️ {ci.WARNING_MARKER} …\n", "đã mang cụm cảnh báo")):
        report.write_text(text, encoding="utf-8")
        real, g.cash_flow_warnings = g.cash_flow_warnings, (lambda r: real(r, **gate_kw))
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                g._warn_cash_flows(report)             # không được ném: cảnh báo, không chặn
        finally:
            g.cash_flow_warnings = real
        ok("CẢNH BÁO (không chặn) ⚠️ " + ci.WARNING_MARKER in err.getvalue() and needle in err.getvalue(),
           f"J: cổng phải in cảnh báo và nói báo cáo đã mang nó hay chưa ({needle}); được {err.getvalue()}")

    # deliver() thật cần Discord + email nên không chạy ở đây; ghim chỗ gọi bằng cách đọc mã nguồn.
    import inspect
    src = inspect.getsource(g.deliver)
    order = [src.find(x) for x in ("_check_nav_flow_records(report)", "_warn_cash_flows(report)",
                                   'record["artifact_validated_at"] = now()')]
    ok(-1 not in order and order == sorted(order),
       f"J: deliver() phải gọi _warn_cash_flows sau cổng nav-flow và trước khi đóng dấu đã kiểm, được {order}")

    # ---- K. cổng tỉ suất FAIL-CLOSED khi CLI không đưa ra được số chuẩn
    inv = Path(tmp) / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"
    inv.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,33% | x |\n",
                   encoding="utf-8")

    class Proc:
        def __init__(self, stdout):
            self.stdout = stdout

    def gate_with(fake):
        real = g.subprocess.run
        g.subprocess.run = fake
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                g._check_period_returns(inv)
            return "PASS " + out.getvalue()
        except RuntimeError as exc:
            return "BLOCK " + str(exc)
        finally:
            g.subprocess.run = real

    def rc1(cmd, **kw):
        raise subprocess.CalledProcessError(1, cmd, output="", stderr="LỖI nav_period_returns: thiếu time_ict")

    got = gate_with(rc1)
    ok(got.startswith("BLOCK period-return BLOCK") and "rc=1" in got and "LỖI nav_period_returns: thiếu time_ict" in got,
       f"K: CLI rc=1 ⇒ báo cáo KHÔNG qua cổng, thông điệp trích lỗi của CLI; được {got}")
    for label, stdout in (("không phải JSON", "Traceback"), ("thiếu khoá inception", "{}"),
                          ("inception không phải object", '{"inception": 5}')):
        got = gate_with(lambda cmd, **kw: Proc(stdout))
        ok(got.startswith("BLOCK period-return BLOCK") and "rc=0 nhưng đầu ra không có số" in got,
           f"K: đầu ra {label} ⇒ CHẶN; được {got}")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": NaN}}'))
    ok(got.startswith("BLOCK") and "không phải số hữu hạn" in got, f"K: số chuẩn NaN ⇒ CHẶN; được {got}")
    for label, value in (("null", "null"), ("Infinity", "Infinity"), ("chuỗi", '"-1.33"')):
        got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": %s}}' % value))
        ok(got.startswith("BLOCK period-return BLOCK") and "không phải số hữu hạn" in got,
           f"K: số chuẩn {label} ⇒ CHẶN bằng thông điệp của cổng (không phải lỗi kiểu); được {got}")
    inv.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,00% | x |\n",
                   encoding="utf-8")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1}}'))
    ok(got.startswith("PASS"), f"K: số chuẩn là số nguyên −1 khớp −1,00% ⇒ qua; được {got}")
    inv.write_text("### 3.2 Hiệu suất lũy kế\n| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,33% | x |\n",
                   encoding="utf-8")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1.33}}'))
    ok(got.startswith("PASS") and "period-return PASS" in got, f"K: số khớp ⇒ qua; được {got}")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1.20}}'))
    ok(got.startswith("BLOCK") and "lệch 0.130pp" in got, f"K: lệch 0,13pp ⇒ CHẶN; được {got}")
    return digest


def main():
    tmp = tempfile.mkdtemp(prefix="cash_identity_selfcheck_")
    try:
        digest = run_checks(tmp)
    except AssertionError as exc:
        print(f"ASSERT-FAIL (sau {N} assertion PASS): {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sha = hashlib.sha256(json.dumps(digest, sort_keys=True).encode()).hexdigest()[:16]
    if "--child" in sys.argv:
        print(f"{N} {sha}")
        return 0
    ok(not os.path.exists(_NOWHERE), "selfcheck không được tạo thư mục dữ liệu mặc định giả")
    results = {"TZ gốc": f"{N - 1} {sha}"}
    for label, tz in (("không có TZ", None), ("America/New_York", "America/New_York"),
                      ("Pacific/Kiritimati", "Pacific/Kiritimati")):
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tz:
            env["TZ"] = tz
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--child"], env=env,
                           capture_output=True, text=True)
        results[label] = p.stdout.strip() if p.returncode == 0 else f"rc={p.returncode} {p.stderr.strip()[-300:]}"
    if len(set(results.values())) != 1:
        print(f"ASSERT-FAIL: kết quả đổi theo múi giờ: {results}", file=sys.stderr)
        return 1
    print(f"OK — {N} assertion PASS (cash_identity_selfcheck.py) · bất biến dưới 4 môi trường TZ "
          f"(digest {sha})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
