#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN của `cash_identity.py` (đẳng thức tiền) và các chỗ nối cảnh báo của nó
(`daily_nav_snapshot.cash_identity_report`, `report_delivery_gate.cash_flow_warnings`,
`cash_identity.notify_snapshot`, cổng tỉ suất fail-closed).

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
import re
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
ci.ACKS_PATH = ci.CORP_ACTIONS_PATH = ci.NOTIFY_SCRIPT = _NOWHERE
os.environ.pop("ACCOUNT_CASH_FLOWS_PATH", None)
os.environ.pop("PYTEST_CURRENT_TEST", None)
os.environ["MIKE_BOT_TEST_MODE"] = "1"       # không lần gọi nào ở đây được gửi tin thật (§5b)
os.environ["MIKE_MANUAL_ACTIONS_FILE"] = _NOWHERE   # sổ lệnh tay THẬT không được đọc

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

    count = 0

    def __init__(self, tmp, name):
        World.count += 1                 # tên được dùng lại trong vòng lặp ⇒ mỗi thế giới một thư mục
        self.dir = Path(tmp) / f"{World.count:03d}_{name}"
        (self.dir / "logs").mkdir(parents=True)
        self.events = {a: [] for a in ACCOUNTS}
        self.snaps = {a: {d: datetime.datetime.combine(d, datetime.time(19, 10, 5 + i))
                          for d in DAYS} for i, a in enumerate(ACCOUNTS)}
        self.flows = {a: [] for a in ACCOUNTS}
        self.seed = {}
        self.acks = None                 # None = không có file lời xác nhận; dict = nội dung file
        self.acks_text = None            # chuỗi thô ghi thẳng ra file lời xác nhận (file hỏng)
        self.corp_actions = []           # record của sổ sự kiện cổ phiếu đã ký
        self.start = {"cash": 200_000_000.0, "egg": 300_000_000.0, "debt": 0.0}
        self.egg_rate = ci.EGG_DAILY_RATE  # lãi Trứng vàng THẬT của thế giới giả
        self.price = True                # bản ghi vị thế có marketPrice
        self.raw_lines = {}              # date -> các dòng thô chèn vào cuối file dnse_raw ngày đó
        self.blank_ts = set()            # (account, date) có balance_ts rỗng
        self.no_positions = set()        # (account, date) không ghi bản ghi positions
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
                "seed_path": str(self.dir / "seed.json"), "today": TODAY,
                "acks_path": str(self.dir / "acks.json"),
                "corp_actions_path": str(self.dir / "corp_actions.json")}

    def ack(self, account, day0, day1, residual, **extra):
        """Thêm một lời xác nhận cho cửa sổ (dòng `day0` → dòng `day1`) của `account`."""
        snaps = {d.day: s for d, s in self.snaps[account].items()}
        rec = {"window": {"from": snaps[day0].isoformat(), "to": snaps[day1].isoformat()},
               "acked_residual_vnd": residual, "reason": "lý do giả", "evidence": "sao kê giả",
               "confirmed_by": "selfcheck", "confirmed_date": "2026-03-20"}
        rec.update(extra)
        self.acks = self.acks or {}
        self.acks.setdefault(account, []).append(rec)
        return self

    def build(self):
        raw = {}                                     # ngày -> list (ts, dòng json)
        order_id = 0

        def log(day, ts, rec):
            raw.setdefault(day, []).append((ts.isoformat(), json.dumps(rec, ensure_ascii=False)))

        for account, account_no in ACCOUNTS.items():
            cash, debt, egg, recv, offbook = (self.start["cash"], self.start["debt"],
                                              self.start["egg"], 0.0, 0.0)
            qty = {"AAA": 30_000.0, "BBB": 20_000.0}
            pending = sorted(self.events[account], key=lambda e: e[0])
            rows, last_day = [], None
            for day in DAYS:
                snap = self.snaps[account][day]
                if last_day is not None:             # lãi Trứng vàng theo ngày lịch, lãi kép
                    for _ in range((snap.date() - last_day).days):
                        egg += egg * self.egg_rate
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
                    elif kind == "bonus":            # cổ phiếu thưởng ghi có, không kèm tiền
                        qty[args[0]] = qty.get(args[0], 0.0) + args[1]
                    elif kind == "interest":         # DNSE ghi nợ lãi vay dồn
                        debt += args[0]
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
                if (account, day) not in self.no_positions:
                    log(snap.date(), snap, {
                        "ts": ts, "kind": "positions", "account_no": account_no,
                        "payload": {"positions": [dict(
                            {"symbol": s, "accountNo": account_no, "openQuantity": q},
                            **({"marketPrice": PRICE} if self.price else {})) for s, q in qty.items()]}})
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
        for day in set(raw) | set(self.raw_lines):   # hai tài khoản XEN KẼ trong cùng file
            with open(self.dir / "logs" / f"dnse_raw_{day.isoformat()}.jsonl", "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for _, line in sorted(raw.get(day, [])))
                f.writelines(line + "\n" for line in self.raw_lines.get(day, []))
        (self.dir / "flows.json").write_text(json.dumps(self.flows), encoding="utf-8")
        (self.dir / "inception.json").write_text(json.dumps(
            {a: {"account_no": no, "inception_date": "2026-02-27", "starting_capital": 1_000_000_000}
             for a, no in ACCOUNTS.items()}), encoding="utf-8")
        (self.dir / "seed.json").write_text(json.dumps(self.seed), encoding="utf-8")
        (self.dir / "corp_actions.json").write_text(
            json.dumps({"actions": self.corp_actions}), encoding="utf-8")
        if self.acks_text is not None:
            (self.dir / "acks.json").write_text(self.acks_text, encoding="utf-8")
        elif self.acks is not None:
            (self.dir / "acks.json").write_text(json.dumps(self.acks), encoding="utf-8")
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


def open_days(result):
    return [w["date1"].day for w in result["suspects"]]


def set_cell(world, account, day, column, value):
    """Sửa một ô của nav_history đã dựng (mô phỏng dòng hỏng/khác dạng)."""
    path = world.dir / "logs" / f"nav_history_{account}.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = lines[0].split(",").index(column)
    for i, line in enumerate(lines):
        if line.startswith(f"2026-03-{day:02d},"):
            cells = line.split(",")
            cells[idx] = value
            lines[i] = ",".join(cells)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def order(account, oid, symbol, side, qty, moment=None, **fields):
    """Một lệnh kiểu DNSE để chèn tay vào dnse_raw (`extra_raw`)."""
    out = {"id": oid, "accountNo": ACCOUNTS[account], "symbol": symbol, "side": side,
           "fillQuantity": qty, "averagePrice": PRICE}
    if moment is not None:
        out["modifiedDate"] = utc_z(moment)
    out.update(fields)
    return out


def no_signed_pct(line):
    """S7: không có phần trăm mang dấu (cổng tỉ suất đọc `<MÃ> … ±x%` thành tỉ suất của mã đó)."""
    return re.search(r"[+\-−]\s*\d[\d.,]*\s*%", line) is None and "VND" not in line


def run_checks(tmp):
    digest = []

    def note(label, result):
        digest.append([label] + [[w["date1"].isoformat(), w["checkable"], round(w.get("unexplained", 0.0), 2),
                                  bool(w.get("suspect")), w.get("kind")] for w in result["windows"]])

    def quiet(name):
        return World(tmp, name)

    D = datetime.date
    thr = ci.THRESHOLD_PCT
    ok(thr == 0.05, f"ngưỡng phải là 0,05% NAV (đo 2026-10-12), được {thr}")
    ok(ci.SESSION_CLOSE_ICT == acf.SESSION_CLOSE_ICT == datetime.time(14, 45), "giờ đóng cửa dùng chung")

    # ---- A. chỉ có khoản nội bộ ⇒ 0 cảnh báo, phần dư ~0, cả hai tài khoản
    base = internal_only(World(tmp, "base")).build()
    base_res = {a: base.check(a) for a in ACCOUNTS}
    for account, res in base_res.items():
        note(f"A/{account}", res)
        ok(len(res["windows"]) == len(DAYS) - 1 and all(w["checkable"] for w in res["windows"]),
           f"A: {account} phải có {len(DAYS) - 1} cửa sổ kiểm được, được {len(res['windows'])}")
        ok(not res["suspects"] and res["drift"] is None and not res["source_errors"],
           f"A: {account} chỉ có khoản nội bộ ⇒ 0 chờ khai, không trôi, được "
           f"{[(w['date1'], w['unexplained']) for w in res['suspects']]} / {res['drift']}")
        worst = max(abs(w["unexplained"]) for w in res["windows"])
        ok(worst < 500, f"A: {account} phần dư lớn nhất phải < 500đ (chỉ còn lãi kép), được {worst:,.2f}")
        ok(not any(w["qty_gaps"] or w["qty_unverified"] for w in res["windows"]),
           f"A: {account} lệnh đủ log ⇒ số lượng vị thế phải khớp ở MỌI cửa sổ")
        # G3: cửa sổ mốc khởi điểm → dòng đầu luôn được liệt kê "không kiểm được", ngoài `windows`.
        ok(res["uncheckable"] == [res["baseline"]] and res["baseline"]["date0"] == D(2026, 2, 27)
           and res["baseline"]["date1"] == DAYS[0] and "mốc khởi điểm" in res["baseline"]["reason"]
           and res["baseline"] not in res["windows"],
           f"A/G3: {account} phải liệt kê cửa sổ mốc khởi điểm là không kiểm được, được {res['uncheckable']}")
    w = window(base_res["SpaceX"], 3)
    ok(w["sell"] == 200_000_000 and w["n_fills"] == 1 and abs(w["fees"] - 200_000_000 * FEE_SELL) < 1e-6,
       f"A: bán 200tr phải ra phí+thuế {200_000_000 * FEE_SELL:,.0f}, được {w['fees']:,.2f}")
    ok(window(base_res["SpaceX"], 4)["dividend"] == 6_000_000, "A: cổ tức chốt quyền = mức tăng phải thu")
    ok(window(base_res["SpaceX"], 10)["dividend"] == -300_000, "A: chi trả cổ tức ⇒ trừ đúng thuế 5%")
    ok(abs(window(base_res["SpaceX"], 9)["egg_interest"] - 450_000_000 * ci.EGG_DAILY_RATE * 3) < 1_000,
       f"A: lãi Trứng vàng qua cuối tuần = 3 ngày, được {window(base_res['SpaceX'], 9)['egg_interest']:,.0f}")
    ok(all(w["egg_out"] == 0 for w in base_res["SpaceX"]["windows"]),
       "A: chuyển tiền VÀO Trứng vàng không được tính là rút Trứng vàng")
    # §12: ZaloPay bán 200tr ngày 10/03 trong CÙNG file dnse_raw — không được lọt vào SpaceX
    ok(window(base_res["SpaceX"], 10)["n_fills"] == 0 and window(base_res["ZaloPay"], 10)["sell"] == 200_000_000,
       "A/§12: lệnh của ZaloPay không được tính cho SpaceX")
    ok(window(base_res["ZaloPay"], 4)["dividend"] == 0, "A/§12: cổ tức của SpaceX không được tính cho ZaloPay")
    rep = ci.report("SpaceX", **base.paths)
    ok(rep == {"investor_line": None, "ops_lines": [], "ops_today": [], "error": None},
       f"A: tài khoản sạch ⇒ không dòng nào ở bất kỳ kênh nào, được {rep}")
    # G3: lượt chụp ĐẦU TIÊN của một tài khoản (chỉ có một dòng nav_history) phải nói ra ở kênh vận hành.
    rep = ci.report("SpaceX", asof=DAYS[0], **base.paths)
    ok(rep["investor_line"] is None and len(rep["ops_today"]) == 1 and "không kiểm được cửa sổ" in rep["ops_today"][0]
       and "mốc khởi điểm" in rep["ops_today"][0] and "2026-02-27" in rep["ops_today"][0],
       f"A/G3: lượt chụp đầu tiên phải báo cửa sổ mốc khởi điểm không kiểm được, được {rep}")

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
                hit = open_days(res["SpaceX"])
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
                       and ("tiền nạp vào chưa khai" if sign > 0 else "tiền rút ra chưa khai") in line
                       and f"phần dư {ci._sd(got)}" in line and f"2026-03-{day1:02d}" in line
                       and "Đã đọc:" in line and "account_cash_flows.json" in line
                       and "cash_identity_acks.json" in line and f"acked_residual_vnd = {got:.0f}" in line,
                       f"{tag}: cảnh báo phải nêu tài khoản, chiều, số tiền, ngày, bằng chứng, cách đóng; được {line}")
                    ok(no_signed_pct(line), f"{tag}/S7: dòng không được có 'VND' hay phần trăm mang dấu; được {line}")
                    ok(ci.LABEL_QUANTITY not in line, f"{tag}: lệnh đủ log ⇒ không được nói số lượng không kết luận được; được {line}")

    # ---- B2. NHÃN (S2): chỉ gọi "nghi nạp/rút" khi không khoản nội bộ chưa mô hình nào phủ được
    for amount, kind, needle in ((-5_000_000, ci.LABEL_EXTERNAL, "nghi tiền RÚT ra"),
                                 (200_000_000, ci.LABEL_EXTERNAL, "nghi tiền NẠP vào"),
                                 (80_000_000, ci.LABEL_EXTERNAL, "nghi tiền NẠP vào"),
                                 (57_000_000, ci.LABEL_INTERNAL, "cổ tức tiền mặt ghi và chi trả trong cùng cửa sổ")):
        res = quiet(f"B2_{amount}").add("SpaceX", at(10, "10:30"), "external", amount).build().check("SpaceX")
        line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
        ok(open_days(res) == [10] and window(res, 10)["kind"] == kind and f"— {kind}:" in line and needle in line
           and no_signed_pct(line),
           f"B2: {amount:+,.0f} không dư nợ/không rút Trứng vàng ⇒ nhãn '{kind}' ({needle}); được {line}")
    ok("cổ tức gộp khoảng 60.000.000 đ, bằng 12,0% giá trị cổ phiếu đầu cửa sổ" in line and "tiền nạp vào chưa khai" in line,
       f"B2 (R8): ứng viên cổ tức phải nêu cổ tức gộp (57tr / 0,95 = 60tr = 12% của 500tr cổ phiếu; 80tr ròng = "
       f"16,8% thì vượt trần 15% ⇒ nghi nạp); được {line}")

    # ---- C. hai tài khoản đổi vai: dòng tiền ở ZaloPay, SpaceX sạch
    wd = internal_only(World(tmp, "C")).add("ZaloPay", at(11, "20:00"), "external", -3_000_000).build()
    res = {a: wd.check(a) for a in ACCOUNTS}
    note("C/ZaloPay", res["ZaloPay"])
    ok(open_days(res["ZaloPay"]) == [12] and not res["SpaceX"]["suspects"],
       "C: rút 3tr ở ZaloPay tối 11/03 (sau lần chụp) ⇒ bắt ở cửa sổ → 12/03 của ZaloPay, SpaceX sạch")

    # ---- D. đã khai / khai sai
    amount = 5_000_000.0

    def declared(name, records, ext=amount):
        wd = internal_only(World(tmp, name)).add("SpaceX", at(10, "10:30"), "external", ext)
        wd.flows["SpaceX"] = records
        return wd.build().check("SpaceX")

    def rec(date, time_ict, amt, kind="deposit"):
        out = {"date": date, "amount_vnd": amt, "kind": kind, "evidence": "sao kê giả của selfcheck"}
        return dict(out, time_ict=time_ict) if time_ict else out

    res = declared("D_ok", [rec("2026-03-10", "10:30", amount)])
    note("D/ok", res)
    ok(not res["suspects"] and window(res, 10)["declared"] == amount and abs(window(res, 10)["unexplained"]) < 500,
       f"D: khai đúng ngày giờ số tiền ⇒ hết cảnh báo, được {[(w['date1'], w['unexplained']) for w in res['suspects']]}")
    res = declared("D_wd", [rec("2026-03-10", "10:30", -amount, "withdraw")], ext=-amount)
    ok(not res["suspects"] and window(res, 10)["declared"] == -amount and abs(window(res, 10)["unexplained"]) < 500,
       f"D: RÚT 5tr khai đúng (số âm) ⇒ hết cảnh báo, được {window(res, 10)['declared']:,.0f} / "
       f"{window(res, 10)['unexplained']:,.0f}")
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
    ok(open_days(res) == [10] and abs(window(res, 10)["unexplained"] - amount / 2) < 500,
       "D: khai thiếu một nửa ⇒ vẫn cảnh báo phần còn lại")
    ok("đã trừ +2.500.000 đ dòng tiền đã khai" in ci.suspect_line("SpaceX", res["suspects"][0]),
       "D: cảnh báo phải nói đã trừ bao nhiêu dòng tiền đã khai")

    # ---- D2. S1: `market_only` của sổ dòng tiền KHÔNG đóng được cửa sổ nào
    for day in ("2026-03-09", "2026-03-10", "2026-03-11"):
        res = declared(f"D_mo_{day}", [rec(day, None, 0, "market_only")])
        ok(open_days(res) == [10] and window(res, 10)["acked"] is None,
           f"D2/S1: market_only ngày {day} không được tắt cảnh báo của cửa sổ → 10/03, được {open_days(res)}")
    wd = quiet("D_r3").add("SpaceX", at(10, "10:30"), "external", 200_000_000)       # ca R3 của reviewer
    wd.flows["SpaceX"] = [rec("2026-03-10", None, 0, "market_only")]
    ok(open_days(wd.build().check("SpaceX")) == [10], "D2/S1 (R3): nạp 200tr chưa khai + market_only cùng ngày ⇒ vẫn bị bắt")

    # ---- D3. lời xác nhận ở FILE RIÊNG: mang số tiền đã xem, chỉ có hiệu lực khi còn khớp
    def acked(name, residual, ext=amount, pair=(9, 10), account="SpaceX", **extra):
        wd = internal_only(World(tmp, name)).add("SpaceX", at(10, "10:30"), "external", ext)
        wd.ack(account, pair[0], pair[1], residual, **extra)
        return wd.build()

    seen = window(declared("D_seen", []), 10)["unexplained"]             # phần dư người xác nhận nhìn thấy
    tol = window(base_res["SpaceX"], 10)["nav0"] * thr / 100
    wd = acked("D3_ok", round(seen))
    res = wd.check("SpaceX")
    note("D3/ok", res)
    ok(not res["suspects"] and window(res, 10)["acked"]["confirmed_by"] == "selfcheck"
       and abs(window(res, 10)["unexplained"] - seen) < 1e-6 and window(res, 10)["kind"],
       "D3: lời xác nhận đúng cửa sổ, đúng số ⇒ thôi cảnh báo, phần dư vẫn nguyên trong bảng")
    ok("(đã có lời xác nhận khớp)" in ci._table(res) and "ĐANG MỞ" not in ci._table(res),
       "D3: bảng phải đánh dấu cửa sổ đã có lời xác nhận")
    ok(ci.report("SpaceX", **wd.paths) == {"investor_line": None, "ops_lines": [], "ops_today": [], "error": None},
       "D3: cửa sổ đã xác nhận ⇒ không còn dòng nào ở kênh nào")
    ok(not acked("D3_in", round(seen + tol - 2_000)).check("SpaceX")["suspects"],
       "D3: phần dư đo được lệch số đã xác nhận ÍT hơn ngưỡng ⇒ lời xác nhận còn hiệu lực")
    res = acked("D3_out", round(seen + tol + 2_000)).check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(open_days(res) == [10] and "LỜI XÁC NHẬN KHÔNG CÒN KHỚP" in line and "lệch" in line
       and ci._sd(round(seen + tol + 2_000)) in line and "selfcheck" in line and no_signed_pct(line),
       f"D3: lệch quá ngưỡng ⇒ mở lại và nêu phần chênh + số đã xác nhận; được {line}")
    # S1: lời xác nhận 5tr không che được một khoản nạp 200tr đến SAU trong cùng cửa sổ
    res = acked("D3_s1", round(seen), ext=amount + 200_000_000).check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(open_days(res) == [10] and "lệch +200.000.000 đ" in line,
       f"D3/S1: nạp 200tr cùng cửa sổ đã xác nhận 5tr ⇒ phải báo lại đúng phần chênh; được {line}")
    for pair, label in (((10, 11), "cửa sổ kế"), ((6, 10), "đúng mốc cuối, sai mốc đầu"), ((9, 11), "đúng mốc đầu, sai mốc cuối")):
        ok(open_days(acked("D3_win", round(seen), pair=pair).check("SpaceX")) == [10],
           f"D3: lời xác nhận ghi cửa sổ KHÁC ({label}) ⇒ không đóng cửa sổ này — phải khớp CẢ HAI mốc chụp")
    ok(open_days(acked("D3_acct", round(seen), account="ZaloPay").check("SpaceX")) == [10],
       "D3/§12: lời xác nhận nằm ở mục ZaloPay không đóng cửa sổ của SpaceX (dù trùng mốc giờ)")
    wd = acked("D3_dup", round(seen)).ack("SpaceX", 9, 10, round(seen))
    res = wd.build().check("SpaceX")
    ok(open_days(res) == [10] and "không biết dùng cái nào" in ci.suspect_line("SpaceX", res["suspects"][0]),
       "D3: hai lời xác nhận cho cùng một cửa sổ ⇒ không cái nào được dùng")
    wd = internal_only(World(tmp, "D3_none")).add("SpaceX", at(10, "10:30"), "external", amount).build()
    ok(not os.path.exists(wd.paths["acks_path"]) and not wd.check("SpaceX")["source_errors"],
       "D3: KHÔNG có file lời xác nhận = chưa có lời nào (không phải lỗi)")
    bad_files = {
        "JSON hỏng": ("{broken", "JSONDecodeError"),
        "gốc là list": ("[]", "gốc phải là object"),
        "mục không phải list": (json.dumps({"SpaceX": {}}), "phải là list"),
    }
    good = acked("D3_tpl", round(seen)).acks["SpaceX"][0]
    for label, patch in {"thiếu evidence": {"evidence": " "}, "thiếu confirmed_by": {"confirmed_by": None},
                         "residual là chuỗi": {"acked_residual_vnd": "5000000"},
                         "residual là true": {"acked_residual_vnd": True},
                         "residual NaN": {"acked_residual_vnd": float("nan")},
                         "window hỏng": {"window": {"from": "hôm qua", "to": good["window"]["to"]}},
                         "thiếu window": {"window": None}, "ngày xác nhận hỏng": {"confirmed_date": "20/03"},
                         "qty gaps = 0": {"acked_qty_gaps": {"AAA": 0}},
                         "qty gaps là list": {"acked_qty_gaps": ["AAA"]}}.items():
        bad_files[label] = (json.dumps({"SpaceX": [good, dict(good, **patch)]}), "SpaceX[1]")
    for label, (text, needle) in bad_files.items():
        wd = internal_only(World(tmp, "D3_bad")).add("SpaceX", at(10, "10:30"), "external", amount)
        wd.acks_text = text
        res = wd.build().check("SpaceX")
        ok(open_days(res) == [10] and len(res["source_errors"]) == 1 and wd.paths["acks_path"] in res["source_errors"][0]
           and needle in res["source_errors"][0] and "KHÔNG lời xác nhận nào có hiệu lực" in res["source_errors"][0],
           f"D3: file lời xác nhận hỏng ({label}) ⇒ coi như không có lời nào + nói rõ file và lỗi; được "
           f"{open_days(res)} / {res['source_errors']}")
        rep = ci.report("SpaceX", **wd.paths)
        ok(rep["error"] is None and any(wd.paths["acks_path"] in x for x in rep["ops_today"])
           and rep["investor_line"], f"D3: file hỏng ({label}) không làm gãy đường hiển thị, lỗi đi kênh vận hành")

    # ---- E. lần chụp giữa phiên: lệnh trước và sau lần chụp phải vào đúng cửa sổ
    wd = World(tmp, "E")
    wd.snaps["SpaceX"][D(2026, 3, 4)] = at(4, "10:00:00")
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

    # ---- E2. đọc bản ghi lệnh: bản mới nhất, giá khớp, giờ cập nhật, loại bản ghi
    def hand_orders(name, records, snap4=None, events=()):
        wd = World(tmp, name)
        if snap4:
            wd.snaps["SpaceX"][D(2026, 3, 4)] = snap4
        for ev in events:
            wd.add("SpaceX", *ev, log=False)
        wd.extra_raw[("SpaceX", D(2026, 3, 4))] = records
        return wd.build().check("SpaceX")

    def orders_rec(ts, *orders, tag=True):
        out = {"kind": "orders", "ts": ts, "payload": {"orders": list(orders)}}
        return dict(out, account_no=ACCOUNTS["SpaceX"]) if tag else out

    sell600 = (at(4, "10:00"), "sell", "AAA", 600)
    res = hand_orders("E2_latest", [
        orders_rec("2026-03-04T10:00:01", order("SpaceX", 7, "AAA", "NS", 300, at(4, "10:00"))),
        orders_rec("2026-03-04T10:00:09", order("SpaceX", 7, "AAA", "NS", 600, at(4, "10:00:08")))], events=[sell600])
    ok(not res["suspects"] and window(res, 4)["sell"] == 6_000_000 and window(res, 4)["n_fills"] == 1,
       f"E2: một lệnh khớp dần (300 rồi 600) ⇒ lấy bản ghi MỚI NHẤT, không cộng dồn; được bán {window(res, 4)['sell']:,.0f}")
    res = hand_orders("E2_price", [orders_rec("2026-03-04T10:00:01", order(
        "SpaceX", 7, "AAA", "NS", 600, at(4, "10:00"), price=9_000.0))], events=[sell600])
    ok(not res["suspects"] and window(res, 4)["sell"] == 6_000_000,
       f"E2: giá đặt 9.000 ≠ giá khớp 10.000 ⇒ dùng averagePrice; được bán {window(res, 4)['sell']:,.0f}")
    res = hand_orders("E2_noavg", [orders_rec("2026-03-04T10:00:01", dict(order(
        "SpaceX", 7, "AAA", "NS", 600, at(4, "10:00"), price=PRICE), averagePrice=None))], events=[sell600])
    ok(not res["suspects"] and window(res, 4)["sell"] == 6_000_000, "E2: không có averagePrice ⇒ rơi về price")
    res = hand_orders("E2_lower", [orders_rec("2026-03-04T10:00:01", order("SpaceX", 7, "AAA", "ns", 600, at(4, "10:00")))],
                      events=[sell600])
    ok(not res["suspects"] and window(res, 4)["sell"] == 6_000_000, "E2: mã chiều lệnh viết thường ('ns') vẫn là lệnh bán")
    res = hand_orders("E2_place", [{"kind": "place_order", "ts": "2026-03-04T10:00:01", "account_no": ACCOUNTS["SpaceX"],
                                    "payload": {"resp": order("SpaceX", 7, "AAA", "NS", 600, at(4, "10:00"))}}],
                      events=[sell600])
    ok(not res["suspects"] and window(res, 4)["sell"] == 6_000_000, "E2: bản ghi place_order cũng là nguồn lệnh khớp")
    # lệnh TẠO trước lần chụp 10:00 nhưng KHỚP (cập nhật cuối) sau đó ⇒ thuộc cửa sổ kế tiếp
    late = order("SpaceX", 7, "AAA", "NS", 600, at(4, "11:00"), createdDate=utc_z(at(4, "09:30")))
    res = hand_orders("E2_modified", [orders_rec("2026-03-04T11:00:01", late)], snap4=at(4, "10:00:00"),
                      events=[(at(4, "11:00"), "sell", "AAA", 600)])
    ok(not res["suspects"] and (window(res, 4)["n_fills"], window(res, 5)["n_fills"]) == (0, 1),
       "E2: xếp lệnh vào cửa sổ theo modifiedDate (lúc khớp), không theo createdDate")
    only_created = order("SpaceX", 7, "AAA", "NS", 600, createdDate=utc_z(at(4, "11:00")))
    res = hand_orders("E2_created", [orders_rec("2026-03-04T11:00:01", only_created)], snap4=at(4, "10:00:00"),
                      events=[(at(4, "11:00"), "sell", "AAA", 600)])
    ok(not res["suspects"] and window(res, 5)["n_fills"] == 1, "E2: thiếu modifiedDate ⇒ dùng createdDate")
    # không đọc được giờ ⇒ coi như khớp lúc ĐÓNG CỬA của ngày file (sau lần chụp 10:00), không phải 00:00
    res = hand_orders("E2_notime", [orders_rec("2026-03-04T11:00:01", order(
        "SpaceX", 7, "AAA", "NS", 600, modifiedDate="không rõ"))], snap4=at(4, "10:00:00"),
        events=[(at(4, "11:00"), "sell", "AAA", 600)])
    ok(not res["suspects"] and (window(res, 4)["n_fills"], window(res, 5)["n_fills"]) == (0, 1),
       "E2: lệnh không đọc được giờ ⇒ gán giờ đóng cửa của ngày giao dịch")

    # ---- F. C1: số lượng cổ phiếu được đối chiếu ở MỌI cửa sổ
    wd = World(tmp, "F").add("SpaceX", at(5, "10:00"), "sell", "AAA", 600, log=False)
    wd.add("ZaloPay", at(4, "10:00"), "buy", "AAA", 100)                  # ZaloPay CÓ lệnh ngày 04/03
    wd.extra_raw[("ZaloPay", D(2026, 3, 5))] = [                          # bản ghi orders cũ, chỉ có lệnh ZaloPay
        {"kind": "orders", "ts": "2026-03-05T10:00:00",
         "payload": {"orders": [order("ZaloPay", 55, "BBB", "NB", 0, at(5, "10:00"))]}}]
    wd.build()
    res = wd.check("SpaceX")
    w = window(res, 5) if res["suspects"] else {}
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(open_days(res) == [5] and w["kind"] == ci.LABEL_QUANTITY and w["qty_gaps"] == {"AAA": -600.0}
       and w["qty_values"] == {"AAA": -6_000_000.0},
       f"F: bán 600 AAA không có log ⇒ cửa sổ 'không kết luận được' với AAA −600, được {w.get('qty_gaps')}")
    ok(f"— {ci.LABEL_QUANTITY}:" in line and "AAA -600 cp (khoảng 6.000.000 đ theo giá thị trường)" in line
       and "nếu đó là lệnh đặt ngoài bot ở giá thị trường thì còn" in line
       and "KHÔNG chứng minh được là không có nạp/rút" in line and 'acked_qty_gaps = {"AAA": -600.0}' in line
       and no_signed_pct(line), f"F: dòng phải nêu mã, số lượng, giá trị ước tính, cách đóng; được {line}")
    ok("KHÔNG có bản ghi orders nào của tài khoản các ngày 2026-03-04, 2026-03-05 ⇒" in line,
       f"F/§12: lệnh của ZaloPay các ngày đó không được tính là 'có bản ghi orders' của SpaceX; được {line}")
    wd.seed = {"SpaceX": {"missing_fills_broker_confirmed": [
        {"date": "2026-03-05", "ticker": "AAA", "side": "sell", "qty": 600, "price": PRICE,
         "evidence": "email khớp lệnh giả"}]}}
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["sell"] == 6_000_000 and not window(res, 5)["qty_gaps"],
       "F: fill broker xác nhận trong account_seed_capital ⇒ đẳng thức và số lượng đều khép")
    ok(not wd.check("ZaloPay")["suspects"] and window(wd.check("ZaloPay"), 5)["n_fills"] == 0,
       "F/§12: fill xác nhận của SpaceX không được tính cho ZaloPay")

    # Hai ca tái hiện của reviewer: tiền của lệnh ngoài bot BÙ TRỪ đúng khoản nạp/rút ⇒ phần dư ~0.
    def offsetting(name, ext, side, n, price=True):
        wd = quiet(name).add("SpaceX", at(4, "10:00"), "external", ext)
        wd.add("SpaceX", at(4, "10:05"), side, "AAA", n, log=False)
        wd.price = price
        return wd.build()

    for name, ext, side, n, gap, value in (("F_R1", 50_000_000, "buy", 5_000, 5_000.0, "50.000.000 đ"),
                                           ("F_R2", -60_000_000, "sell", 6_000, -6_000.0, "60.000.000 đ")):
        wd = offsetting(name, ext, side, n)
        res = wd.check("SpaceX")
        note(name, res)
        w = window(res, 4)
        ok(open_days(res) == [4] and not w["over"] and w["kind"] == ci.LABEL_QUANTITY and w["qty_gaps"] == {"AAA": gap},
           f"{name} (C1): nạp/rút {ext:+,.0f} đi kèm lệnh ngoài bot — phần dư tiền {w['unexplained']:+,.0f} dưới "
           f"ngưỡng nhưng số lượng lệch ⇒ PHẢI mở cửa sổ; được {open_days(res)} {w['qty_gaps']}")
        lines = ci.warning_lines("SpaceX", **wd.paths)
        rep = ci.report("SpaceX", **wd.paths)
        remaining = re.search(r"thì còn ([+-][\d.]+) đ tiền vào/ra chưa giải thích", lines[0])
        ok(len(lines) == 1 and remaining and abs(float(remaining.group(1).replace(".", "")) - ext) < 500,
           f"{name}: dòng vận hành phải ước được khoản tiền vào/ra còn lại ≈ {ext:+,.0f}; được {lines}")
        ok(rep["investor_line"] and f"lớn nhất {value}" in rep["investor_line"],
           f"{name}: dòng nhà đầu tư phải nêu độ lớn theo giá trị cổ phiếu; được {rep['investor_line']}")
    wd = offsetting("F_R1_noprice", 50_000_000, "buy", 5_000, price=False)
    line = ci.warning_lines("SpaceX", **wd.paths)[0]
    ok("AAA +5.000 cp (bản ghi vị thế không có giá ⇒ không ước được giá trị)" in line and "thì còn" not in line,
       f"F: bản ghi vị thế không có giá ⇒ nói rõ không ước được, không bịa số; được {line}")
    seen_r1 = window(offsetting("F_R1_seen", 50_000_000, "buy", 5_000).check("SpaceX"), 4)["unexplained"]
    wd = offsetting("F_R1_ack", 50_000_000, "buy", 5_000).ack("SpaceX", 3, 4, round(seen_r1), acked_qty_gaps={"AAA": 5_000})
    ok(not wd.build().check("SpaceX")["suspects"], "F: lời xác nhận ghi đúng số lượng đã xem ⇒ đóng cửa sổ")
    for label, gaps in (("không ghi số lượng", {}), ("số lượng khác", {"AAA": 4_000}), ("mã khác", {"BBB": 5_000})):
        wd = offsetting("F_R1_ackbad", 50_000_000, "buy", 5_000).ack("SpaceX", 3, 4, round(seen_r1), acked_qty_gaps=gaps)
        res = wd.build().check("SpaceX")
        ok(open_days(res) == [4] and "số lượng đổi ngoài lệnh đo được AAA +5.000 cp khác số đã xác nhận"
           in ci.suspect_line("SpaceX", res["suspects"][0]),
           f"F: lời xác nhận {label} ⇒ không đóng được cửa sổ có số lượng lệch")

    # ---- F2. arch-review vòng 2: N3 (cận dưới giờ), N4 (bản ghi rỗng), N6 (mã biến mất / lô trùng / thanh lý hết)
    def pos_rec(*lots, tag=True, ts=None):
        """Bản ghi positions thủ công; mỗi lot = (mã, số lượng). Có thể có hai lot cùng mã (lô trùng)."""
        no = ACCOUNTS["SpaceX"]
        out = {"kind": "positions", "payload": {"positions": [
            {"symbol": sym, "accountNo": no, "openQuantity": q, "marketPrice": PRICE} for sym, q in lots]}}
        if tag:
            out["account_no"] = no
        if ts:
            out["ts"] = ts
        return out

    def hand_positions(name, records, events=(), day=4):
        wd = World(tmp, name)
        for ev in events:
            wd.add("SpaceX", *ev)
        wd.no_positions.add(("SpaceX", D(2026, 3, day)))
        wd.extra_raw[("SpaceX", D(2026, 3, day))] = records
        return wd.build()

    # N3: chỉ còn bản ghi vị thế BUỔI SÁNG của ngày 04/03 (trước lệnh mua tay 10:30) ⇒ KHÔNG được dùng thay
    # cho bản buổi tối; cửa sổ phải báo "không đối chiếu được số lượng", không báo sạch.
    wd = hand_positions("F2_N3", [pos_rec(("AAA", 30_000.0), ("BBB", 20_000.0), ts="2026-03-04T10:00:00")],
                        events=[(at(4, "10:30"), "buy", "AAA", 5_000, ), ])
    res = wd.check("SpaceX")
    ok(window(res, 4)["qty_unverified"] and window(res, 4)["qty_gaps"] == {}
       and wd.build().check("SpaceX")["windows"][1]["qty_unverified"],
       f"F2/N3: chỉ có bản ghi vị thế buổi sáng ⇒ không đối chiếu được số lượng (không báo sạch); được "
       f"{window(res, 4)['qty_unverified']!r} / {window(res, 4)['qty_gaps']}")
    ok(ci.RawLog is not None and hasattr(ci.RawLog, "positions_at"), "F2/N3: RawLog.positions_at phải tồn tại")
    log_obj = ci.RawLog(ACCOUNTS["SpaceX"], str(wd.dir / "logs"))
    ok(log_obj.positions_at(at(4, "19:10:05")) is None
       and log_obj.positions_at(at(4, "10:05:00")) is not None and log_obj.positions_at(at(4, "09:51:00")) is not None
       and log_obj.positions_at(at(4, "09:49:00")) is None and log_obj.positions_at(at(4, "10:11:00")) is None,
       "F2/N3: bản ghi vị thế chỉ được nhận trong ±10 phút quanh lần chụp (biên 09:50 và 10:10)")

    # N4: bản ghi positions RỖNG (lỗi đọc broker) trong khi NAV có cổ phiếu ⇒ không đối chiếu được, KHÔNG báo
    # "mất sạch AAA/BBB".
    wd = hand_positions("F2_N4", [pos_rec(ts="2026-03-04T19:10:07")])
    res = wd.check("SpaceX")
    ok(not res["suspects"] and window(res, 4)["qty_unverified"] and not window(res, 4)["qty_gaps"]
       and window(res, 5)["qty_unverified"] and "bản ghi rỗng trong khi NAV có cổ phiếu" in window(res, 4)["qty_unverified"],
       f"F2/N4: bản ghi vị thế rỗng khi NAV có cổ phiếu ⇒ không đối chiếu được ở CẢ HAI cửa sổ kề nó; được "
       f"{res['suspects']} / {window(res, 4)['qty_unverified']}")
    # N6/C10: thanh lý HẾT thật (mtm=0) ⇒ bản ghi rỗng là sự thật, phải đối chiếu được và khớp lệnh bán.
    wd = hand_positions("F2_C10", [pos_rec(ts="2026-03-04T19:10:07")],
                        events=[(at(4, "10:00"), "sell", "AAA", 30_000), (at(4, "10:01"), "sell", "BBB", 20_000)])
    res = wd.check("SpaceX")
    ok(not res["suspects"] and not window(res, 4)["qty_unverified"] and not window(res, 4)["qty_gaps"]
       and window(res, 4)["n_fills"] == 2,
       f"F2/C10: bán hết cổ phiếu, bản ghi rỗng đúng sự thật ⇒ đối chiếu được và khớp; được {res['suspects']} "
       f"{window(res, 4)['qty_unverified']} {window(res, 4)['qty_gaps']}")
    # N6/C07: một mã BIẾN MẤT khỏi bản ghi vị thế (không có lệnh bán) trong khi mã khác còn ⇒ phải báo lệch.
    wd = hand_positions("F2_C07", [pos_rec(("BBB", 20_000.0), ts="2026-03-04T19:10:07")])
    res = wd.check("SpaceX")
    ok(4 in open_days(res) and window(res, 4)["qty_gaps"] == {"AAA": -30_000.0}
       and window(res, 5)["qty_gaps"] == {"AAA": 30_000.0},     # hôm sau AAA hiện lại ⇒ cửa sổ kề bên lệch ngược
       f"F2/C07: mã AAA biến mất khỏi vị thế không kèm lệnh bán ⇒ lệch AAA −30.000; được {open_days(res)} {window(res, 4)['qty_gaps']}")
    # N6/C09: hai LÔ cùng mã phải được CỘNG, không ghi đè (ZaloPay thật có 168 cặp ngày-mã nhiều lô).
    wd = hand_positions("F2_C09", [pos_rec(("AAA", 10_000.0), ("AAA", 20_000.0), ("BBB", 20_000.0), ts="2026-03-04T19:10:07")])
    res = wd.check("SpaceX")
    ok(not res["suspects"] and not window(res, 4)["qty_gaps"] and not window(res, 4)["qty_unverified"],
       f"F2/C09: AAA chia hai lô 10.000 + 20.000 = 30.000 ⇒ khớp, không lệch; được {window(res, 4)['qty_gaps']}")

    # N8: cửa sổ THIẾU BẰNG CHỨNG đã kết thúc trong 30 ngày qua phải có mặt trong dòng đếm hằng tối;
    # cửa sổ mốc khởi điểm (luôn không kiểm được, cấu trúc) thì không.
    wd = World(tmp, "F2_N8")
    wd.no_positions.add(("SpaceX", D(2026, 3, 4)))
    wd.build()
    rep = ci.report("SpaceX", asof=D(2026, 3, 13), **wd.paths)
    thin_lines = [x for x in rep["ops_today"] if "chưa kiểm được hoặc chưa đối chiếu được số lượng" in x]
    ok(len(thin_lines) == 1 and "2 cửa sổ trong 30 ngày qua" in thin_lines[0] and "2026-03-04, 2026-03-05" in thin_lines[0],
       f"F2/N8: cửa sổ không đối chiếu được số lượng phải vào dòng đếm hằng tối; được {rep['ops_today']}")
    rep0 = ci.report("SpaceX", asof=D(2026, 3, 13), **internal_only(World(tmp, "F2_N8_clean")).build().paths)
    ok(not any("chưa kiểm được hoặc chưa đối chiếu được" in x for x in rep0["ops_today"]),
       f"F2/N8: thế giới sạch (chỉ có cửa sổ mốc khởi điểm không kiểm được) ⇒ dòng đếm KHÔNG nhắc; được {rep0['ops_today']}")
    rep = ci.report("SpaceX", asof=D(2026, 4, 20), **wd.paths)         # 47 ngày sau ⇒ quá THIN_DAYS, hết nhắc
    ok(ci.THIN_DAYS == 30 and not any("chưa kiểm được hoặc chưa đối chiếu được" in x for x in rep["ops_today"]),
       f"F2/N8: cửa sổ thiếu bằng chứng quá {ci.THIN_DAYS} ngày thì thôi nhắc hằng tối (vẫn thấy ở CLI); được {rep['ops_today']}")

    # Cổ phiếu thưởng/cổ tức cổ phiếu ĐÃ KÝ giải thích được số lượng tăng; chưa ký / lệch ⇒ không.
    def bonus(name, n=3_000, **patch):
        wd = quiet(name).add("SpaceX", at(5, "12:00"), "bonus", "BBB", n)
        record = {"ticker": "BBB", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.15, "ex_date": "2026-03-06",
                  "broker_effective_ts": "2026-03-05T12:00:00", "_status": "CONFIRMED — selfcheck"}
        record.update(patch)
        wd.corp_actions = [] if patch.get("drop") else [record]
        return wd.build()

    wd = bonus("F_bonus")
    res = wd.check("SpaceX")
    ok(not res["suspects"] and not window(res, 5)["qty_gaps"]
       and any("BBB +3.000 cp khớp sự kiện đã ký BBB-2026-03-06-STOCK_DIVIDEND" in n for n in window(res, 5)["notes"]),
       f"F: +3.000 BBB = 20.000 × 15% đã ký ⇒ không cảnh báo, có ghi chú; được {window(res, 5)['notes']}")
    ok(not wd.check("ZaloPay")["suspects"], "F: tài khoản không nhận cổ phiếu thưởng vẫn sạch")
    for label, kw in (("sổ không có sự kiện", {"drop": True}), ("sự kiện chưa ký", {"_status": "PROPOSED"}),
                      ("sự kiện của mã khác", {"ticker": "AAA"}),
                      ("ghi có ngoài cửa sổ", {"broker_effective_ts": "2026-03-09T12:00:00"}),
                      ("hệ số khác", {"qty_multiplier": 1.2})):
        res = bonus("F_bonus_bad", **kw).check("SpaceX")
        ok(open_days(res) == [5] and window(res, 5)["qty_gaps"] == {"BBB": 3_000.0},
           f"F: {label} ⇒ +3.000 BBB không được giải thích, được {open_days(res)}")
    ok(open_days(bonus("F_bonus_3001", n=3_001).check("SpaceX")) == [5]
       and open_days(bonus("F_bonus_2999", n=2_999).check("SpaceX")) == [5],
       "F: số tăng lệch mức sự kiện một cổ phiếu (3.001 / 2.999 thay vì 3.000) ⇒ không khớp")
    wd = quiet("F_bonus_frac").add("SpaceX", at(4, "10:00"), "buy", "BBB", 1).add("SpaceX", at(5, "12:00"), "bonus", "BBB", 3_000)
    wd.corp_actions = [{"ticker": "BBB", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 1.15, "ex_date": "2026-03-06",
                        "broker_effective_ts": "2026-03-05T12:00:00", "_status": "CONFIRMED — selfcheck"}]
    ok(not wd.build().check("SpaceX")["suspects"], "F: 20.001 × 15% = 3.000,15 ⇒ broker bỏ phần lẻ, +3.000 vẫn khớp")
    wd = quiet("F_bonus_broken").add("SpaceX", at(5, "12:00"), "bonus", "BBB", 3_000).build()
    (wd.dir / "corp_actions.json").write_text("{", encoding="utf-8")
    res = wd.check("SpaceX")
    ok(open_days(res) == [5] and len(res["source_errors"]) == 1 and wd.paths["corp_actions_path"] in res["source_errors"][0]
       and "JSONDecodeError" in res["source_errors"][0],
       f"F: sổ sự kiện cổ phiếu hỏng ⇒ không giải thích gì + nêu file và lỗi, không ném; được {res['source_errors']}")

    # Không đọc được vị thế ở một đầu: không đối chiếu được số lượng — nói ra, không coi là sạch.
    wd = quiet("F_nopos")
    wd.no_positions.add(("SpaceX", D(2026, 3, 5)))
    wd.build()
    res = wd.check("SpaceX")
    ok(not res["suspects"] and [w["date1"].day for w in res["windows"] if w["qty_unverified"]] == [5, 6]
       and "không đọc được vị thế ở lần chụp 2026-03-05 19:10:05" in window(res, 5)["qty_unverified"],
       "F: thiếu bản ghi positions ⇒ hai cửa sổ quanh nó không đối chiếu được số lượng (phần dư tiền ~0 ⇒ không mở)")
    rep5, rep9 = ci.report("SpaceX", asof=D(2026, 3, 5), **wd.paths), ci.report("SpaceX", asof=D(2026, 3, 9), **wd.paths)
    ok(len(rep5["ops_today"]) == 1 and "KHÔNG đối chiếu được số lượng" in rep5["ops_today"][0]
       and rep5["investor_line"] is None and rep9["ops_lines"] == []
       and len(rep9["ops_today"]) == 1 and "2 cửa sổ trong 30 ngày qua" in rep9["ops_today"][0]
       and "ℹ️" not in rep9["ops_today"][0],
       f"F/N8: lượt chụp đúng ngày thiếu vị thế báo MỘT dòng chi tiết; các lượt sau chỉ còn dòng ĐẾM (không lặp chi tiết); "
       f"được {rep5} / {rep9}")
    ok("(không đối chiếu được số lượng)" in ci._table(res), "F: bảng phải đánh dấu cửa sổ không đối chiếu được số lượng")
    wd = quiet("F_nopos_over").add("SpaceX", at(5, "10:00"), "external", -5_000_000)
    wd.no_positions.add(("SpaceX", D(2026, 3, 5)))
    res = wd.build().check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(open_days(res) == [5] and window(res, 5)["kind"] == ci.LABEL_EXTERNAL
       and "KHÔNG đối chiếu được số lượng cổ phiếu với lệnh khớp" in line,
       f"F: thiếu vị thế + phần dư vượt ngưỡng ⇒ vẫn xét theo tiền, kèm ghi chú; được {line}")
    # §12: bản ghi positions KHÔNG gắn tài khoản (log cũ) chứa vị thế của cả hai — chỉ nhận của mình.
    wd = quiet("F_legacy_pos")
    wd.no_positions.add(("SpaceX", D(2026, 3, 5)))
    wd.extra_raw[("SpaceX", D(2026, 3, 5))] = [{"kind": "positions", "payload": {"positions": [
        {"symbol": "AAA", "accountNo": ACCOUNTS["SpaceX"], "openQuantity": 30_000, "marketPrice": PRICE},
        {"symbol": "BBB", "accountNo": ACCOUNTS["SpaceX"], "openQuantity": 20_000, "marketPrice": PRICE},
        {"symbol": "AAA", "accountNo": ACCOUNTS["ZaloPay"], "openQuantity": 999_999, "marketPrice": PRICE}]}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and not any(w["qty_gaps"] or w["qty_unverified"] for w in res["windows"]),
       f"F/§12: vị thế của ZaloPay trong bản ghi chung không được cộng vào SpaceX; được "
       f"{[(w['date1'].day, w['qty_gaps']) for w in res['windows'] if w['qty_gaps']]}")

    # ---- G. khoản nội bộ quanh Trứng vàng và ký quỹ
    def egg_out(name, out, loss):
        return quiet(name).add("SpaceX", at(10, "16:00"), "egg_out", out, loss=loss).build()

    wd = egg_out("G_small", 100_000_000, 100_000_000 * ci.EGG_WITHDRAW_COST)
    ok(ci.report("SpaceX", **wd.paths)["ops_lines"] == [] and abs(window(wd.check("SpaceX"), 10)["egg_cost"] - 201_300) < 200,
       "G: rút 100tr Trứng vàng, khấu trừ đúng mức đã đo (dưới ngưỡng) ⇒ không dòng nào")
    wd = egg_out("G_big", 280_000_000, 280_000_000 * ci.EGG_WITHDRAW_COST)       # ca R5 của reviewer
    res = wd.check("SpaceX")
    note("G/big", res)
    rep = ci.report("SpaceX", asof=D(2026, 3, 10), **wd.paths)
    ok(not res["suspects"] and abs(window(res, 10)["unexplained"]) < 1_000 and window(res, 10)["info"]
       and len(rep["ops_today"]) == 1 and rep["ops_today"][0].startswith("ℹ️") and ci.LABEL_INTERNAL in rep["ops_today"][0]
       and "khấu trừ ƯỚC TÍNH" in rep["ops_today"][0] and rep["investor_line"] is None and no_signed_pct(rep["ops_today"][0]),
       f"G (R5): rút 280tr — đẳng thức khép nhờ ước tính lớn hơn ngưỡng ⇒ nhắc MỘT lần ở kênh vận hành với "
       f"nhãn nội bộ, không vào báo cáo; được {rep}")
    ok(ci.report("SpaceX", asof=D(2026, 3, 11), **wd.paths)["ops_today"] == [], "G (R5): lượt chụp hôm sau không nhắc lại")
    res = egg_out("G_over", 280_000_000, 2_000_000).check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(open_days(res) == [10] and window(res, 10)["kind"] == ci.LABEL_INTERNAL
       and "khấu trừ rút Trứng vàng lớn hơn mức đã đo" in line and "nghi tiền" not in line
       and "Trứng vàng rút ròng 280.0" in line and "đã tính khấu trừ rút trước hạn 563." in line,
       f"G: mất 2tr khi rút 280tr (0,7% < trần 1%) ⇒ 'cần xác nhận khoản nội bộ', không gọi là rút tiền; được {line}")
    res = egg_out("G_far", 280_000_000, 5_000_000).check("SpaceX")
    ok(open_days(res) == [10] and window(res, 10)["kind"] == ci.LABEL_EXTERNAL,
       "G: mất 5tr khi rút 280tr (1,8% > trần 1%) ⇒ không còn là khấu trừ hợp lý ⇒ nghi rút")

    def levered(name, posted):
        wd = quiet(name).add("SpaceX", at(10, "16:00"), "interest", posted)
        wd.start["debt"] = 300_000_000.0
        return wd.build().check("SpaceX")

    res = levered("G_margin", 1_000_000)                                           # ca R6 của reviewer
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    est = 301_000_000 * ci.MARGIN_RATE_ANNUAL_NOTE / 365
    ok(open_days(res) == [10] and window(res, 10)["kind"] == ci.LABEL_INTERNAL and "lãi vay ký quỹ DNSE ghi dồn" in line
       and "có dư nợ ký quỹ (300.000.000 đ → 301.000.000 đ)" in line and f"lãi vay ước {ci._d(est)} cho 1 ngày" in line
       and "nghi tiền" not in line,
       f"G (R6): DNSE ghi dồn 1tr lãi vay trên dư nợ 300tr ⇒ nhãn nội bộ + ghi chú dư nợ (tính trên dư nợ LỚN hơn); được {line}")
    res = levered("G_margin_far", 5_000_000)
    ok(open_days(res) == [10] and window(res, 10)["kind"] == ci.LABEL_EXTERNAL,
       "G: 5tr trên dư nợ 300tr vượt mọi mức lãi một kỳ (≈3,7tr) ⇒ nghi rút")
    ok(not [w for w in quiet("G3").build().check("SpaceX")["windows"] if w["notes"]],
       "G: tài khoản yên tĩnh không được có ghi chú nào")

    # ---- G4. off-book khai tay và cổ tức bị loại khỏi cột cash đều nằm trong "tiền sở hữu"
    wd = World(tmp, "G4").add("SpaceX", at(4, "16:00"), "offbook_in", 120_000_000)
    wd.add("SpaceX", at(5, "17:30"), "dividend_declared", 4_000_000)
    wd.cum_div_excl[("SpaceX", D(2026, 3, 5))] = 4_000_000.0
    res = wd.build().check("SpaceX")
    note("G4", res)
    ok(not res["suspects"] and max(abs(w["unexplained"]) for w in res["windows"]) < 500,
       f"G4: chuyển sang off-book + cổ tức đang bị loại khỏi cột cash ⇒ đẳng thức vẫn khép, được "
       f"{[(w['date1'].day, round(w['unexplained'])) for w in res['windows']]}")
    ok(any("off-book khai tay" in n for n in window(res, 4)["notes"]), "G4: cửa sổ có off-book phải có ghi chú")
    # Bản ghi balances KHÔNG gắn tài khoản (log cũ) nằm đúng lúc chụp: không được dùng cho ai cả.
    wd = World(tmp, "G5")
    wd.no_balances.add(("SpaceX", D(2026, 3, 5)))
    wd.extra_raw[("SpaceX", D(2026, 3, 5))] = [
        {"kind": "balances", "payload": {"stock": {"cashDividendReceiving": 9_000_000}, "egg": {"totalValue": 1}}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["dividend"] == 0 and window(res, 6)["dividend"] == 0
       and any("không đọc được cashDividendReceiving" in n for n in window(res, 5)["notes"]),
       "G5/§12: bản ghi balances không gắn tài khoản không được tính là của SpaceX (coi như không có)")
    # Bản ghi balances của mình nhưng THIẾU field phải thu ⇒ thiếu bằng chứng, không phải "phải thu = 0".
    wd = World(tmp, "G5b").add("SpaceX", at(4, "17:30"), "dividend_declared", 6_000_000)
    wd.no_balances.add(("SpaceX", D(2026, 3, 5)))
    wd.extra_raw[("SpaceX", D(2026, 3, 5))] = [
        {"kind": "balances", "account_no": ACCOUNTS["SpaceX"], "payload": {"stock": {"totalCash": 1}}}]
    res = wd.build().check("SpaceX")
    ok(window(res, 5)["dividend"] == 0 and window(res, 6)["dividend"] == 0
       and any("không đọc được cashDividendReceiving ở lần chụp 2026-03-05 19:10:05" in n for n in window(res, 5)["notes"]),
       f"G5b: bản ghi balances thiếu cashDividendReceiving ⇒ ghi chú thiếu bằng chứng (không tính thành chi trả "
       f"6tr); được cổ tức {window(res, 5)['dividend']:,.0f} / {window(res, 5)['notes']}")
    # Bản ghi orders KHÔNG gắn tài khoản (log trước 2026-07-06) chứa lệnh của CẢ HAI tài khoản và một
    # lệnh chưa khớp: mỗi tài khoản chỉ nhận lệnh mang accountNo của mình.
    wd = World(tmp, "G6").add("SpaceX", at(5, "10:00"), "sell", "AAA", 600, log=False)
    wd.add("ZaloPay", at(5, "10:01"), "sell", "BBB", 5_000, log=False)
    legacy = [order("SpaceX", 901, "AAA", "NS", 600, at(5, "10:00")),
              order("ZaloPay", 902, "BBB", "NS", 5_000, at(5, "10:01")),
              dict(order("SpaceX", 903, "BBB", "NB", 0, at(5, "10:02"), price=PRICE), averagePrice=None)]
    wd.extra_raw[("SpaceX", D(2026, 3, 5))] = [{"kind": "orders", "payload": {"orders": legacy}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["n_fills"] == 1 and window(res, 5)["sell"] == 6_000_000,
       f"G6/§12: bản ghi orders không gắn tài khoản — SpaceX chỉ nhận lệnh 901 của mình, được "
       f"{window(res, 5)['n_fills']} lệnh, bán {window(res, 5)['sell']:,.0f}")
    ok(window(wd.check("ZaloPay"), 5)["sell"] == 50_000_000 and not wd.check("ZaloPay")["suspects"],
       "G6/§12: lệnh 902 thuộc ZaloPay")
    # Phải thu cổ tức đọc ở bản ghi balances ĐÚNG lúc chụp — không phải bản sớm hơn hay muộn hơn trong ngày.
    wd = World(tmp, "G7").add("SpaceX", at(5, "09:00"), "dividend_declared", 7_000_000)
    wd.extra_raw[("SpaceX", D(2026, 3, 4))] = [
        {"kind": "balances", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-04T23:00:00",
         "payload": {"stock": {"cashDividendReceiving": 7_000_000}, "egg": {"totalValue": 1}}}]
    wd.extra_raw[("SpaceX", D(2026, 3, 5))] = [
        {"kind": "balances", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-05T08:00:00",
         "payload": {"stock": {"cashDividendReceiving": 0}, "egg": {"totalValue": 1}}}]
    res = wd.build().check("SpaceX")
    ok(not res["suspects"] and window(res, 5)["dividend"] == 7_000_000 and window(res, 6)["dividend"] == 0,
       f"G7: nhiều bản ghi balances trong ngày (08:00 trước, 23:00 sau lần chụp) ⇒ dùng bản lúc chụp 19:10; được "
       f"cổ tức {window(res, 5)['dividend']:,.0f} / {window(res, 6)['dividend']:,.0f}")

    # ---- H. thiếu bằng chứng ⇒ nói rõ, không coi là 0 một cách im lặng
    wd = World(tmp, "H").add("SpaceX", at(4, "17:30"), "dividend_declared", 6_000_000)
    wd.no_balances.add(("SpaceX", D(2026, 3, 4)))
    res = wd.build().check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok(res["suspects"] and "không đọc được cashDividendReceiving ở lần chụp 2026-03-04 19:10:05" in line,
       f"H: thiếu bản ghi balances ⇒ cảnh báo phải nói không đọc được phải thu cổ tức; được {line}")
    wd = World(tmp, "H2")
    wd.blank_ts.add(("SpaceX", D(2026, 3, 5)))
    res = wd.build().check("SpaceX")
    broken = [w for w in res["uncheckable"] if not w.get("baseline")]
    ok([w["date1"].day for w in broken] == [5, 6] and not res["suspects"] and "balance_ts rỗng" in broken[0]["reason"],
       f"H: dòng thiếu balance_ts ⇒ 2 cửa sổ quanh nó KHÔNG kiểm được, được {broken}")
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 2 and all("không kiểm được cửa sổ" in x for x in lines),
       f"H: cửa sổ không kiểm được phải hiện ở cảnh báo, được {lines}")
    for label, moment in (("TRƯỚC", at(4, "18:00")), ("ĐÚNG GIÂY", at(4, "19:10:05"))):
        wd = World(tmp, "H3")
        wd.snaps["SpaceX"][D(2026, 3, 5)] = moment
        res = wd.build().check("SpaceX")
        broken = [w for w in res["uncheckable"] if not w.get("baseline")]
        ok([w["date1"].day for w in broken] == [5] and "không sau dòng" in broken[0]["reason"],
           f"H: dòng 05/03 chụp {label} lần chụp của dòng 04/03 ⇒ cửa sổ không kiểm được, nêu hai lần chụp")
    wd = quiet("H4").build()
    set_cell(wd, "SpaceX", 5, "nav", "0")
    broken = [w for w in wd.check("SpaceX")["uncheckable"] if not w.get("baseline")]
    ok([w["date1"].day for w in broken] == [6] and "NAV dòng 2026-03-05 = 0" in broken[0]["reason"],
       f"H: NAV đầu cửa sổ = 0 ⇒ không chia được ⇒ không kiểm được, được {broken}")
    for cell in ("nan", "inf", "abc"):
        set_cell(wd, "SpaceX", 5, "nav", cell)
        lines = ci.warning_lines("SpaceX", **wd.paths)
        ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0] and "nav_history_SpaceX.csv" in lines[0]
           and "2026-03-05" in lines[0], f"H: NAV '{cell}' ⇒ một dòng nêu file + dòng hỏng, không ném; được {lines}")
    set_cell(wd, "SpaceX", 5, "nav", "")
    res = wd.check("SpaceX")
    ok(len(res["windows"]) == len(DAYS) - 2 and window(res, 6)["date0"] == D(2026, 3, 4) and not res["suspects"],
       "H: dòng thiếu nav bị bỏ ⇒ cửa sổ nối từ dòng trước sang dòng sau, đẳng thức vẫn khép")
    wd = internal_only(World(tmp, "H_shuffled")).build()
    path = wd.dir / "logs" / "nav_history_SpaceX.csv"
    body = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([body[0]] + body[:0:-1]) + "\n", encoding="utf-8")
    res = wd.check("SpaceX")
    ok([w["date1"] for w in res["windows"]] == DAYS[1:] and not res["suspects"]
       and [round(w["unexplained"], 2) for w in res["windows"]] == [round(w["unexplained"], 2) for w in base_res["SpaceX"]["windows"]],
       "H: nav_history ghi NGƯỢC thứ tự ngày vẫn cho đúng các cửa sổ liên tiếp")
    # `balance_ts` có múi giờ (UTC) phải được quy về ICT — kết quả y như khi ghi giờ ICT trần.
    wd = internal_only(World(tmp, "H5")).build()
    for day in DAYS:
        set_cell(wd, "SpaceX", day.day, "balance_ts",
                 (wd.snaps["SpaceX"][day] - datetime.timedelta(hours=7)).isoformat() + "+00:00")
    res = wd.check("SpaceX")
    ok([round(w["unexplained"], 2) for w in res["windows"]] == [round(w["unexplained"], 2) for w in base_res["SpaceX"]["windows"]]
       and [w["n_fills"] for w in res["windows"]] == [w["n_fills"] for w in base_res["SpaceX"]["windows"]],
       "H: balance_ts dạng UTC có múi giờ phải cho đúng kết quả của giờ ICT trần")

    # ---- H6. S6: một bản ghi dnse_raw sai kiểu chỉ làm cửa sổ LIÊN QUAN không kiểm được
    no = ACCOUNTS["SpaceX"]
    bad_records = {
        "payload là list": (json.dumps({"ts": "2026-03-05T10:00:00", "kind": "orders", "account_no": no, "payload": [1, 2]}),
                            "payload của bản ghi orders là list"),
        "fillQuantity 'abc'": (json.dumps(orders_rec("2026-03-05T10:00:00", order("SpaceX", 9, "AAA", "NS", "abc", at(5, "10:00")))),
                               "abc"),
        "JSON hỏng": ('{"ts": "2026-03-05T10:00:00", "kind": "orders", "account_no": "' + no + '", "payload": {', "JSONDecodeError"),
        "balance ts hỏng": (json.dumps({"ts": "sáng nay", "kind": "balances", "account_no": no, "payload": {"stock": {}}}), "sáng nay"),
        "vị thế KL hỏng": (json.dumps({"ts": "2026-03-05T10:00:00", "kind": "positions", "account_no": no, "payload": {
            "positions": [{"symbol": "AAA", "accountNo": no, "openQuantity": None}, {"symbol": "BBB", "accountNo": no, "openQuantity": "x"}]}}), "x"),
    }
    for label, (raw_line, needle) in bad_records.items():
        wd = quiet("H6").add("SpaceX", at(11, "10:00"), "external", -5_000_000)
        wd.raw_lines[D(2026, 3, 5)] = [raw_line]
        wd.build()
        n_line = len((wd.dir / "logs" / "dnse_raw_2026-03-05.jsonl").read_text(encoding="utf-8").splitlines())
        res = wd.check("SpaceX")
        broken = [w for w in res["uncheckable"] if not w.get("baseline")]
        ok([w["date1"].day for w in broken] == [5, 6] and open_days(res) == [11]
           and all(w["checkable"] for w in res["windows"] if w["date1"].day not in (5, 6)),
           f"H6/S6 ({label}): chỉ hai cửa sổ chạm ngày 05/03 không kiểm được, cửa sổ khác vẫn kiểm (bắt được "
           f"khoản rút ngày 11/03); được {[w['date1'].day for w in broken]} / {open_days(res)}")
        reason = broken[0]["reason"] if broken else ""
        ok("1 bản ghi dnse_raw không đọc được" in reason and "dnse_raw_2026-03-05.jsonl" in reason
           and f"dòng {n_line} —" in reason and needle in reason,
           f"H6/S6 ({label}): lý do phải nêu file, số dòng {n_line}, lỗi; được {reason}")
        lines = ci.warning_lines("SpaceX", **wd.paths)
        ok(len(lines) == 3 and sum("không kiểm được cửa sổ" in x for x in lines) == 2,
           f"H6/S6 ({label}): đường hiển thị không ném, nêu 2 cửa sổ không kiểm được + 1 cửa sổ mở; được {len(lines)} dòng")
    wd = quiet("H6_other")
    wd.raw_lines[D(2026, 3, 5)] = [json.dumps({"ts": "2026-03-05T10:00:00", "kind": "orders",
                                               "account_no": ACCOUNTS["ZaloPay"], "payload": [1]})]
    wd.build()
    ok(all(w["checkable"] for w in wd.check("SpaceX")["windows"])
       and [w["date1"].day for w in wd.check("ZaloPay")["windows"] if not w["checkable"]] == [5, 6],
       "H6/§12: bản ghi hỏng gắn rõ tài khoản ZaloPay chỉ ảnh hưởng ZaloPay")
    wd = quiet("H6_many")
    wd.raw_lines[D(2026, 3, 5)] = [bad_records["JSON hỏng"][0]] * 5
    reason = [w for w in wd.build().check("SpaceX")["uncheckable"] if not w.get("baseline")][0]["reason"]
    ok("5 bản ghi dnse_raw không đọc được" in reason and "… và 2 bản ghi nữa" in reason,
       f"H6/S6: nhiều bản ghi hỏng ⇒ in số bản ghi bị bỏ, trích 3 cái đầu; được {reason}")

    # ---- I. `asof`, lỗi nguồn, và đường hiển thị không bao giờ ném lỗi
    wd = internal_only(World(tmp, "I")).add("SpaceX", at(10, "10:30"), "external", amount).build()
    ok(not wd.check("SpaceX", asof=D(2026, 3, 9))["suspects"]
       and len(wd.check("SpaceX", asof=D(2026, 3, 10))["suspects"]) == 1,
       "I: asof trước ngày có dòng tiền ⇒ chưa thấy; asof đúng ngày ⇒ thấy")
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 1 and ci.WARNING_MARKER in lines[0], f"I: warning_lines phải ra đúng 1 dòng, được {lines}")
    wd2 = internal_only(World(tmp, "I2")).add("SpaceX", at(10, "10:30"), "external", amount)
    wd2.add("SpaceX", at(10, "09:20"), "sell", "AAA", 1_000)
    wd2.extra_raw[("SpaceX", D(2026, 3, 10))] = [
        {"kind": "positions", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-10T23:30:00",
         "payload": {"positions": [{"symbol": "AAA", "accountNo": ACCOUNTS["SpaceX"], "openQuantity": 1}]}}]
    lines = ci.warning_lines("SpaceX", **wd2.build().paths)
    ok(len(lines) == 1 and "1 lệnh khớp (bán 10.000.000 đ" in lines[0] and ci.LABEL_QUANTITY not in lines[0],
       f"I: có lệnh BÁN đủ log + bản ghi vị thế 23:30 (sau lần chụp) ⇒ vị thế vẫn phải khớp; được {lines}")
    # cuối tuần không phải "ngày không có bản ghi orders"
    res = quiet("I3").add("SpaceX", at(7, "11:00"), "external", -5_000_000).build().check("SpaceX")
    line = ci.suspect_line("SpaceX", res["suspects"][0]) if res["suspects"] else ""
    ok("các ngày 2026-03-06, 2026-03-09 ⇒" in line and "2026-03-07" not in line.split("Cách đóng")[0].split("các ngày")[1],
       f"I: ghi chú ngày không có bản ghi orders chỉ tính ngày thường; được {line}")
    os.remove(wd.paths["flows_path"])
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0] and "KHÔNG có sổ dòng tiền" in lines[0],
       f"I: thiếu sổ dòng tiền ⇒ một dòng nêu đúng lỗi, không ném; được {lines}")
    lines = ci.warning_lines("KhongCo", **base.paths)
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0], f"I: tài khoản lạ ⇒ một dòng lỗi; được {lines}")
    lines = ci.warning_lines("SpaceX")                 # không truyền đường dẫn ⇒ mặc định đã bị vô hiệu
    ok(len(lines) == 1 and "KHÔNG chạy được" in lines[0] and "KHONG_DUOC_DOC" in lines[0],
       f"I: selfcheck không được chạm dữ liệu mặc định; được {lines}")
    # G8: dòng lỗi đi vào log cron mỗi tối ⇒ không được khớp bộ dò lỗi của cron_health_check.py
    import cron_health_check as chc
    lines = ci.warning_lines("SpaceX", **dict(base.paths, inception_path=os.path.join(tmp, "khong_co.json")))
    ok(len(lines) == 1 and "FileNotFoundError" in lines[0] and "khong_co.json" in lines[0] and "[Errno" not in lines[0]
       and not chc.ERROR_RE.search(lines[0]) and not chc.ERROR_RE.search("nav_period_returns: " + lines[0]),
       f"I/G8: dòng lỗi phải nêu lỗi thật nhưng không khớp ERROR_RE của cron_health_check; được {lines}")
    ok(chc.ERROR_RE.search("FileNotFoundError: [Errno 2] x"), "I/G8: phép thử phải phân biệt được (dạng thô CÓ khớp)")
    import nav_period_returns as npr_mod
    ok(not chc.ERROR_RE.search("x — " + npr_mod._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")))
       and "b.csv" in npr_mod._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")),
       "G8: dòng lỗi dự phòng của nav_period_returns.py phải nêu lỗi thật mà không khớp ERROR_RE của cron_health_check")

    cli = [sys.executable, os.path.join(BIN, "cash_identity.py")]
    env = {k: v for k, v in os.environ.items() if k not in ("WC_ROOT", "MIKE_ROOT")}

    def run_cli(world, account="SpaceX", *extra):
        args = [x for k in ("nav_dir", "raw_dir", "flows_path", "inception_path", "seed_path", "acks_path",
                            "corp_actions_path") for x in ("--" + k.replace("_", "-"), world.paths[k])]
        return subprocess.run(cli + ["--account", account] + args + list(extra), capture_output=True, text=True, env=env)

    wd = internal_only(World(tmp, "I_cli")).add("SpaceX", at(10, "10:30"), "external", amount).build()
    p = run_cli(wd)
    ok(p.returncode == 3 and ci.WARNING_MARKER in p.stdout and "ĐANG MỞ" in p.stdout and "khởi điểm" in p.stdout,
       f"I: CLI có cửa sổ đang mở ⇒ rc=3 + bảng + dòng cảnh báo; được rc={p.returncode} {p.stderr[-200:]}")
    p = run_cli(wd, "SpaceX", "--asof", "2026-03-09")
    ok(p.returncode == 0 and ci.WARNING_MARKER not in p.stdout, f"I: CLI --asof trước ngày có dòng tiền ⇒ rc=0; được {p.returncode}")
    p = run_cli(wd, "SpaceX", "--json")
    blob = json.loads(p.stdout)
    ok(p.returncode == 3 and blob["n_windows"] == 9 and len(blob["suspects"]) == 1 and blob["baseline"]["date0"] == "2026-02-27"
       and blob["suspects"][0]["snap0"] == "2026-03-09T19:10:05", "I: CLI --json phải đọc được, có baseline + suspects")
    p = run_cli(wd, "KhongCo")
    ok(p.returncode == 1 and "KHÔNG chạy được" in p.stderr and "Traceback" not in p.stderr,
       f"I: CLI tài khoản lạ ⇒ rc=1 + một dòng lỗi; được rc={p.returncode} {p.stderr[-200:]}")
    wd.seed = {"SpaceX": {"missing_fills_broker_confirmed": [{"ticker": "AAA"}]}}
    p = run_cli(wd.build())
    ok(p.returncode == 1 and "KHÔNG chạy được" in p.stderr and "KeyError" in p.stderr and "Traceback" not in p.stderr,
       f"I: sổ fill xác nhận thiếu field ⇒ CLI rc=1 + lỗi đã gặp, không traceback; được rc={p.returncode} {p.stderr[-200:]}")

    # ---- L. S3: phần dư TRÔI có hệ thống mà không cửa sổ nào tự vượt ngưỡng
    def drip(name, per_day, days=range(3, 14)):
        wd = quiet(name)
        for day in days:
            if D(2026, 3, day) in DAYS:
                wd.add("SpaceX", at(day, "10:00"), "external", per_day)
        return wd.build()

    wd = drip("L_drip", -450_000)                                                  # ca R10 của reviewer
    res = wd.check("SpaceX")
    note("L/drip", res)
    drift = res["drift"] or {}
    ok(not res["suspects"] and drift and drift["n_windows"] == 9 and drift["same_sign"] == 9
       and abs(drift["sum_vnd"] + 9 * 450_000) < 2_000 and drift["sum_pct"] < -0.4 and drift["new"] is False,
       f"L (R10): rút nhỏ giọt 450k × 9 phiên (mỗi cửa sổ dưới ngưỡng) ⇒ phải có dòng trôi; được {drift}")
    lines = ci.warning_lines("SpaceX", **wd.paths)
    ok(len(lines) == 1 and ci.DRIFT_MARKER in lines[0] and "9 cửa sổ gần nhất (2026-03-02 → 2026-03-13)" in lines[0]
       and "9/9 cửa sổ cùng chiều" in lines[0] and "Đo lại hằng số" in lines[0] and "khoản nhỏ lặp lại" in lines[0]
       and no_signed_pct(lines[0]), f"L (R10): dòng trôi phải nêu khoảng, tổng, số cửa sổ cùng chiều, việc phải làm; được {lines}")
    rep = {d: ci.report("SpaceX", asof=D(2026, 3, d), **wd.paths) for d in (3, 4, 5)}
    ok(rep[3]["ops_lines"] == [] and len(rep[4]["ops_today"]) == 1 and ci.DRIFT_MARKER in rep[4]["ops_today"][0]
       and "cộng lại" in rep[4]["ops_today"][0],
       f"L: lượt chụp ĐẦU TIÊN tổng vượt ngưỡng (04/03) gửi chi tiết; trước đó (03/03) chưa có gì; được {rep[3]} / {rep[4]}")
    ok(len(rep[5]["ops_today"]) == 1 and "phần dư trôi có hệ thống đã báo từ lượt trước" in rep[5]["ops_today"][0]
       and "cộng lại" not in rep[5]["ops_today"][0] and "cộng lại" in rep[5]["ops_lines"][0],
       f"L: các lượt sau chỉ nhắc MỘT dòng đếm (chi tiết vẫn có ở CLI); được {rep[5]}")
    ok(all(r["investor_line"] is None for r in rep.values()),
       "L: dòng trôi không gắn cửa sổ nào (không ai đóng được) ⇒ KHÔNG vào báo cáo nhà đầu tư")
    wd = quiet("L_rate")                                                           # ca R11: lãi Trứng vàng thật thấp hơn hằng số
    wd.egg_rate, wd.start = 0.03 / 365, dict(wd.start, egg=500_000_000.0)
    res = wd.build().check("SpaceX")
    note("L/rate", res)
    ok(not res["suspects"] and res["drift"] and res["drift"]["sum_vnd"] < 0 and all(w["egg_out"] == 0 for w in res["windows"])
       and max(abs(w["pct_nav"]) for w in res["windows"]) < thr,
       f"L (R11): hằng số lãi Trứng vàng đã cũ ⇒ từng cửa sổ dưới ngưỡng, không bị coi là rút, nhưng tổng phải "
       f"báo trôi; được {res['drift']}")
    res = quiet("L_one").add("SpaceX", at(10, "10:30"), "external", -5_000_000).build().check("SpaceX")
    ok(open_days(res) == [10] and res["drift"] is None,
       "L: cửa sổ đã tự vượt ngưỡng (đang mở) không được cộng vào tổng trôi lần nữa")
    ok(drip("L_under", -40_000).check("SpaceX")["drift"] is None, "L: 40k × 9 phiên = 0,036% < ngưỡng ⇒ không trôi")
    wd = drip("L_margin", -250_000)          # NAV 700tr sau khi trừ nợ ⇒ 250k = 0,036% (dưới ngưỡng)
    wd.start["debt"] = 300_000_000.0
    lines = ci.warning_lines("SpaceX", **wd.build().paths)
    ok(len(lines) == 1 and "lãi vay ước" in lines[0] and "có thể là nguyên nhân" in lines[0],
       f"L: trôi ở tài khoản có dư nợ ⇒ nêu lãi vay ước tính là ứng viên; được {lines}")
    long_world = quiet("L_window")
    ok(ci.DRIFT_WINDOWS == 20, "L: cửa sổ trượt = 20 lần chụp gần nhất")
    del long_world

    # ---- M. hằng số ghim bằng số THẬT đóng băng (không tự sinh từ chính hằng số)
    def frozen(day, nav, mtm, cash, egg, hhmmss):
        date = D(2026, 10, day)
        return {"date": date, "nav": nav, "mtm": mtm, "cash": cash, "debt": 0.0, "offbook": 0.0, "egg": egg,
                "cum_div_excl": 0.0, "k": cash + egg, "snap_error": None,
                "snap": datetime.datetime.combine(date, datetime.time(*hhmmss))}

    # nav_history SpaceX thật 2026-10-08 → 10-09 → 10-12 (không chuyển tiền ↔ Trứng vàng, không lệnh).
    real = [frozen(8, 987_341_794.0, 477_815_800.0, 9_109_043.0, 500_416_951.0, (19, 10, 46)),
            frozen(9, 986_698_574.0, 477_055_600.0, 9_109_074.0, 500_533_900.0, (19, 10, 51)),
            frozen(12, 986_247_378.0, 476_253_550.0, 9_109_084.0, 500_884_744.0, (19, 10, 49))]
    empty = os.path.join(tmp, "khong_co_dnse_raw")
    os.makedirs(empty, exist_ok=True)
    wins = ci.build_windows(real, ci.RawLog("0", empty), [])
    ok([round(w["unexplained"]) for w in wins] == [-103, -476] and all(abs(w["pct_nav"]) < 0.0001 for w in wins),
       f"M: lãi Trứng vàng thật của SpaceX 10-08→10-12 (116.949 đ/1 ngày, 350.844 đ/3 ngày) phải khép trong "
       f"vài trăm đồng với EGG_DAILY_RATE; được {[round(w['unexplained']) for w in wins]}")
    # Hai lần rút Trứng vàng thật 2026-09-17 (số rút ròng theo đẳng thức, số mất đo ở vòng 1).
    for label, out, lost in (("SpaceX", 49_948_690, 100_576), ("ZaloPay", 31_217_900, 62_839)):
        ok(abs(out * ci.EGG_WITHDRAW_COST - lost) < 50,
           f"M: khấu trừ rút Trứng vàng {label} 09-17 thật {lost:,} đ trên {out:,} đ; hằng số cho {out * ci.EGG_WITHDRAW_COST:,.0f}")
    ok(ci.DIVIDEND_TAX_RATE == 0.05 and ci.EGG_WITHDRAW_COST < ci.EGG_WITHDRAW_COST_CAP == 0.01, "M: hằng số thuế/trần")

    # ---- J. chỗ nối: dòng 💰 NAV (MỘT dòng trung tính), kênh vận hành, cổng giao báo cáo
    wd = internal_only(World(tmp, "J")).add("SpaceX", at(10, "10:30"), "external", amount)
    wd.add("ZaloPay", at(10, "20:00"), "external", 3_000_000)                    # nạp thật, có khai
    wd.flows["ZaloPay"] = [rec("2026-03-10", "20:00", 3_000_000),               # vào dòng 11/03
                           rec("2026-03-13", "20:00", 7_000_000)]               # sau lần chụp cuối ⇒ TREO
    wd.build()
    import daily_nav_snapshot as dns
    ok(not chc.ERROR_RE.search("x — " + dns._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")))
       and "b.csv" in dns._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")),
       "G8: dòng lỗi dự phòng của daily_nav_snapshot.py phải nêu lỗi thật mà không khớp ERROR_RE của cron_health_check")
    kw = {k: v for k, v in wd.paths.items()}
    got = window(wd.check("SpaceX"), 10)["unexplained"]
    rep10 = dns.cash_identity_report("SpaceX", "2026-03-10", **kw)
    inv = rep10["investor_line"] or ""
    ok(inv == f"ℹ️ Có 1 khoản {ci.INVESTOR_MARKER} (lớn nhất {ci._d(abs(got))}); tỉ suất kỳ chứa ngày đó có thể được điều chỉnh.",
       f"J/C2: báo cáo nhà đầu tư nhận đúng MỘT dòng trung tính; được {inv!r}")
    ok(len(inv) < 160 and "\n" not in inv and no_signed_pct(inv)
       and not re.search(r"dnse|json|market_only|cash_identity|nav_history|nghi|rút|nạp|\.py|acked|SpaceX", inv, re.I),
       f"J/C2: dòng nhà đầu tư không tên file/field/hàm nội bộ, không 'nghi nạp/rút', không phần trăm có dấu; được {inv!r}")
    ok(len(rep10["ops_today"]) == 1 and rep10["ops_today"] == rep10["ops_lines"] and ci.WARNING_MARKER in rep10["ops_today"][0]
       and "Đã đọc:" in rep10["ops_today"][0], f"J/C2: chi tiết đầy đủ đi kênh vận hành ở lượt chụp đúng ngày; được {rep10['ops_today']}")
    rep11 = dns.cash_identity_report("SpaceX", "2026-03-11", **kw)
    ok(rep11["investor_line"] == inv and len(rep11["ops_today"]) == 1 and "còn 1 cửa sổ cũ chưa đóng (kết thúc 2026-03-10)" in rep11["ops_today"][0]
       and "Đã đọc:" not in rep11["ops_today"][0] and "cash_identity.py --account SpaceX" in rep11["ops_today"][0]
       and rep11["ops_lines"] == rep10["ops_lines"],
       f"J/C2: lượt chụp hôm sau chỉ gộp MỘT dòng đếm ở kênh vận hành (không lặp chi tiết); được {rep11['ops_today']}")
    empty_rep = {"investor_line": None, "ops_lines": [], "ops_today": [], "error": None}
    ok(dns.cash_identity_report("SpaceX", "2026-03-09", **kw) == empty_rep
       and dns.cash_identity_report("ZaloPay", "2026-03-13", **kw) == empty_rep,
       "J: ngày trước dòng tiền / tài khoản khác ⇒ không có dòng nào")
    bad = dns.cash_identity_report("SpaceX", "không-phải-ngày", **kw)
    ok(bad["investor_line"] is None and len(bad["ops_today"]) == 1 and "KHÔNG chạy được" in bad["ops_today"][0],
       f"J: đường hiển thị không được ném lỗi, lỗi đi kênh vận hành (không vào báo cáo); được {bad}")
    sys.modules["cash_identity"] = None                # import hỏng (ImportError, không phải ValueError)
    try:
        bad = dns.cash_identity_report("SpaceX", "2026-03-10", **kw)
    finally:
        sys.modules["cash_identity"] = ci
    ok(bad["investor_line"] is None and bad["error"] and "KHÔNG chạy được" in bad["ops_today"][0]
       and "ModuleNotFoundError" in bad["ops_today"][0] and not chc.ERROR_RE.search(bad["ops_today"][0]),
       f"J: cash_identity không import được ⇒ lượt chụp NAV vẫn sống, lỗi đi kênh vận hành; được {bad}")

    # khối `cash_flow_ops` của nav_snapshot + bước gửi kênh vận hành (tách khỏi lượt chụp)
    snap_dir = Path(tmp) / "snap"
    snap_dir.mkdir()
    snap_path = snap_dir / "nav_snapshot_SpaceX_2026-03-10.json"
    ok(dns.cash_flow_ops_record(str(snap_path), []) == {"lines": [], "status": "không có gì để gửi"}
       and dns.cash_flow_ops_record(str(snap_path), ["a"]) == {"lines": ["a"], "status": "chưa gửi"},
       "J: chưa có nav_snapshot cũ ⇒ 'chưa gửi' / 'không có gì để gửi'")
    calls = snap_dir / "notify.sh.calls"
    script = snap_dir / "notify.sh"
    script.write_text('#!/bin/sh\nprintf \'%s\\n@@%s\\n\' "$1" "$2" >> "$0.calls"\nexit ${FAKE_NOTIFY_RC:-0}\n', encoding="utf-8")
    script.chmod(0o755)

    def write_snap(lines, status="chưa gửi"):
        snap_path.write_text(json.dumps({"account": "SpaceX", "nav": 1, "cash_flow_ops": {"lines": lines, "status": status}}),
                             encoding="utf-8")

    def notify(**kwargs):
        return ci.notify_snapshot("SpaceX", "2026-03-10", "trading_daily", exec_dir=str(snap_dir),
                                  notify_script=str(script), **kwargs)

    def status_now():
        return json.loads(snap_path.read_text(encoding="utf-8"))["cash_flow_ops"]["status"]

    write_snap(rep10["ops_today"])
    rc, msg = notify()
    ok(rc == 0 and "chế độ test" in msg and not calls.exists() and status_now() == "chưa gửi",
       f"J/§5b: MIKE_BOT_TEST_MODE=1 ⇒ KHÔNG gửi gì, không đổi trạng thái; được {rc} {msg}")
    os.environ.pop("MIKE_BOT_TEST_MODE")
    try:
        rc, msg = notify()
        sent = calls.read_text(encoding="utf-8")
        ok(rc == 0 and "đã gửi 1 dòng tới trading_daily" in msg and sent == rep10["ops_today"][0] + "\n@@trading_daily\n"
           and status_now().startswith("đã gửi trading_daily lúc 20"),
           f"J/C2: gửi đúng chi tiết của lượt chụp tới kênh theo TÊN, ghi trạng thái; được {rc} {msg} / {status_now()}")
        rc, msg = notify()
        ok(rc == 0 and "không gửi lại" in msg and calls.read_text(encoding="utf-8") == sent,
           f"J/§5: chạy lại ⇒ không gửi lần hai; được {rc} {msg}")
        kept = dns.cash_flow_ops_record(str(snap_path), rep10["ops_today"])
        ok(kept["status"] == status_now() and dns.cash_flow_ops_record(str(snap_path), ["khác"])["status"] == "chưa gửi",
           "J/§5: chụp lại cùng ngày, nội dung KHÔNG đổi ⇒ giữ 'đã gửi'; nội dung đổi ⇒ 'chưa gửi'")
        write_snap(["x", "y"])
        os.environ["FAKE_NOTIFY_RC"] = "3"
        rc, msg = notify()
        ok(rc == 1 and "KHÔNG gửi được 2 dòng" in msg and "rc=3" in msg and status_now().startswith("GỬI HỎNG lúc 20"),
           f"J: gửi hỏng ⇒ rc=1, nêu mã thoát, trạng thái ghi GỬI HỎNG; được {rc} {msg} / {status_now()}")
        os.environ.pop("FAKE_NOTIFY_RC")
        rc, msg = notify()
        ok(rc == 0 and status_now().startswith("đã gửi") and calls.read_text(encoding="utf-8").endswith("x\ny\n@@trading_daily\n"),
           f"J: lượt sau gửi lại cái đã hỏng (nhiều dòng = một tin); được {rc} {msg}")
        write_snap(["x"])
        rc, msg = ci.notify_snapshot("SpaceX", "2026-03-10", "trading_daily", exec_dir=str(snap_dir),
                                     notify_script=str(snap_dir / "khong_co.sh"))
        ok(rc == 1 and "FileNotFoundError" in msg and "[Errno" not in msg and status_now().startswith("GỬI HỎNG"),
           f"J: không có script gửi ⇒ rc=1 + lỗi đã gặp, không ném; được {rc} {msg}")
        write_snap([])
        ok(notify()[0] == 0 and "không có chi tiết" in notify()[1], "J: không có dòng nào ⇒ rc=0, không gửi")
        rc, msg = ci.notify_snapshot("SpaceX", "2026-03-11", "trading_daily", exec_dir=str(snap_dir), notify_script=str(script))
        ok(rc == 1 and "nav_snapshot_SpaceX_2026-03-11.json" in msg, f"J: thiếu nav_snapshot ⇒ rc=1 nêu file; được {rc} {msg}")
        snap_path.write_text("{", encoding="utf-8")
        ok(notify()[0] == 1 and dns.cash_flow_ops_record(str(snap_path), ["a"])["status"] == "chưa gửi",
           "J: nav_snapshot hỏng ⇒ bước gửi rc=1; lượt chụp coi như chưa gửi")
        p = subprocess.run(cli + ["--account", "SpaceX", "--notify-snapshot", "2026-03-11", "--nav-dir", str(snap_dir)],
                           capture_output=True, text=True, env=dict(env, MIKE_BOT_TEST_MODE="1"))
        ok(p.returncode == 1 and "nav_snapshot_SpaceX_2026-03-11.json" in p.stderr and "Traceback" not in p.stderr,
           f"J: CLI --notify-snapshot thiếu file ⇒ rc=1 + một dòng stderr; được {p.returncode} {p.stderr[-200:]}")
        ok(p.stderr.startswith("NOTIFY_FAILED: cash_identity:") and chc.ERROR_RE.search(p.stderr),
           f"J/N1: gửi hỏng phải mang NOTIFY_FAILED để cron_health_check bắt được; được {p.stderr[:120]!r}")
        write_snap(["x"])
        p = subprocess.run(cli + ["--account", "SpaceX", "--notify-snapshot", "2026-03-10", "--nav-dir", str(snap_dir)],
                           capture_output=True, text=True, env=dict(env, MIKE_BOT_TEST_MODE="1"))
        ok(p.returncode == 0 and "NOTIFY_FAILED" not in p.stdout + p.stderr,
           f"J/N1: không gửi (chế độ test) ⇒ rc=0 và KHÔNG có NOTIFY_FAILED; được {p.returncode} {p.stderr[-120:]}")
        nsd = (Path(BIN) / "nav_snapshot_daily.sh").read_text(encoding="utf-8")
        ok(re.search(r'has_row "\$ACCOUNT"; then\n.*?cash_identity\.py" --account "\$ACCOUNT" --notify-snapshot "\$TODAY" \\\n'
                     r'\s+--channel trading_daily >&2 \|\| true\n\s+else', nsd, re.S),
           "J/N2: nav_snapshot_daily.sh phải gửi chi tiết đẳng thức tiền ngay sau khi NAV đã ghi (trong nhánh has_row), "
           "bằng TÊN kênh trading_daily, lỗi gửi không đổi mã thoát")
    finally:
        os.environ["MIKE_BOT_TEST_MODE"] = "1"
        os.environ.pop("FAKE_NOTIFY_RC", None)

    # Chỗ gọi bước gửi trong lượt cron: chạy NGUYÊN hàm `_nav_section` của eod_trading_report.sh với
    # hai script giả — chỉ gọi khi NAV đã ghi (rc=0), đúng tham số, lỗi gửi không đổi thân báo cáo.
    eod_src = (Path(BIN) / "eod_trading_report.sh").read_text(encoding="utf-8")
    m = re.search(r"^_nav_section\(\) \{\n.*?^\}\n", eod_src, re.S | re.M)
    ok(m is not None, "J: không trích được hàm _nav_section từ eod_trading_report.sh")
    fake_root = Path(tmp) / "fake_root"
    (fake_root / "bin").mkdir(parents=True)
    (fake_root / "bin" / "daily_nav_snapshot.py").write_text(
        "import os, sys\nprint('[dnse] nhiễu')\nprint('💰 NAV giả')\nprint('   dòng trung tính')\n"
        "sys.exit(int(os.environ.get('FAKE_NAV_RC', '0')))\n", encoding="utf-8")
    (fake_root / "bin" / "cash_identity.py").write_text(
        "import os, sys\nopen(os.path.join(os.path.dirname(__file__), 'calls.txt'), 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
        "print('stdout của bước gửi')\nprint('stderr của bước gửi', file=sys.stderr)\n"
        "sys.exit(int(os.environ.get('FAKE_NOTIFY_RC', '0')))\n", encoding="utf-8")
    calls_file = fake_root / "bin" / "calls.txt"

    def nav_section(nav_rc, notify_rc=0):
        if calls_file.exists():
            calls_file.unlink()
        script = (f'ROOT="{fake_root}"; ACCOUNT=SpaceX; PLAN_DATE=2026-03-10\n{m.group(0)}\n_nav_section\n'
                  'printf "%s" "$NAV_SECTION"\n')
        p = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                           env=dict(env, FAKE_NAV_RC=str(nav_rc), FAKE_NOTIFY_RC=str(notify_rc)))
        return p, (calls_file.read_text(encoding="utf-8") if calls_file.exists() else "")

    p, called = nav_section(0)
    ok(p.returncode == 0 and called == "--account SpaceX --notify-snapshot 2026-03-10 --channel trading_daily\n"
       and p.stdout == "💰 NAV giả\n   dòng trung tính" and "bước gửi" not in p.stdout and "bước gửi" in p.stderr,
       f"J/C2: NAV rc=0 ⇒ gọi bước gửi kênh vận hành đúng tham số; đầu ra của nó KHÔNG vào thân báo cáo; được "
       f"{called!r} / {p.stdout!r} / {p.stderr[-200:]!r}")
    p, called = nav_section(0, notify_rc=1)
    ok(p.returncode == 0 and p.stdout == "💰 NAV giả\n   dòng trung tính" and called,
       "J/C2: bước gửi hỏng (rc=1) không đổi thân báo cáo, không làm hỏng lượt cron")
    for nav_rc in (2, 4, 5):
        p, called = nav_section(nav_rc)
        ok(called == "" and p.returncode == 0, f"J/C2: NAV rc={nav_rc} (chưa ghi nav_history) ⇒ KHÔNG gọi bước gửi; được {called!r}")
    retry_src = (Path(BIN) / "nav_sync_retry.sh").read_text(encoding="utf-8")
    ok(retry_src.count('--notify-snapshot "$PLAN_DATE"') == 1 and retry_src.find('if [ "$RC" = "0" ]; then')
       < retry_src.find('--notify-snapshot "$PLAN_DATE"') < retry_src.find('if [ "$RC" != "4" ]; then')
       and "--channel trading_daily" in retry_src,
       "J/C2: nav_sync_retry.sh gọi bước gửi kênh vận hành đúng một lần, trong nhánh chụp bù thành công")

    with contextlib.redirect_stderr(io.StringIO()):
        import report_delivery_gate as g
    ok(not chc.ERROR_RE.search("x — " + g._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")))
       and "b.csv" in g._exc_text(FileNotFoundError(2, "No such file or directory", "/a/b.csv")),
       "G8: dòng lỗi dự phòng của report_delivery_gate.py phải nêu lỗi thật mà không khớp ERROR_RE của cron_health_check")
    ok(g.INVESTOR_FLOW_MARKER == ci.INVESTOR_MARKER and g.OPS_FLOW_MARKER == ci.WARNING_MARKER,
       "J: cổng và module phải dùng cùng hai cụm đánh dấu")
    gate_kw = {k: v for k, v in wd.paths.items()}
    report = Path(tmp) / "SpaceX_weekly_report_2026-03-09_to_2026-03-13.md"
    report.write_text("# báo cáo giả\n", encoding="utf-8")
    ops, investor = g.cash_flow_warnings(report, **gate_kw)
    ok(len(ops) == 1 and ci.WARNING_MARKER in ops[0] and "(SpaceX)" in ops[0] and investor == [inv],
       f"J: cổng phải thấy khoản chưa đối chiếu của SpaceX (chi tiết + dòng nhà đầu tư), được {ops} / {investor}")
    both = Path(tmp) / "SpaceX_ZaloPay_weekly_report_2026-03-09_to_2026-03-13.md"
    both.write_text("x\n", encoding="utf-8")
    ops, investor = g.cash_flow_warnings(both, **gate_kw)
    ok(len(ops) == 2 and g.PENDING_FLOW_MARKER in ops[1] and "(ZaloPay)" in ops[1]
       and "+7,000,000 đ" in ops[1] and investor == [inv] and no_signed_pct(ops[1]),
       f"J: cổng phải thấy cả dòng tiền TREO của ZaloPay, được {ops}")
    day10 = Path(tmp) / "ZaloPay_daily_report_2026-03-10.md"
    day10.write_text("x\n", encoding="utf-8")
    ops, investor = g.cash_flow_warnings(day10, **gate_kw)
    ok(len(ops) == 1 and g.PENDING_FLOW_MARKER in ops[0] and "+3,000,000 đ" in ops[0]
       and "2026-03-10 20:00" in ops[0] and investor == [],
       f"J: báo cáo ngày 10/03 — khoản khai 20:00 (sau lần chụp) còn TREO tính tới ngày đó; được {ops}")
    early = Path(tmp) / "SpaceX_ZaloPay_daily_report_2026-03-09.md"
    early.write_text("x\n", encoding="utf-8")
    ok(g.cash_flow_warnings(early, **gate_kw) == ([], []), "J: báo cáo ngày 09/03 — chưa có gì để cảnh báo")
    other = Path(tmp) / "spend_report_2026-03-13.md"
    other.write_text("x\n", encoding="utf-8")
    ok(g.cash_flow_warnings(other, **gate_kw) == ([], []), "J: báo cáo không thuộc tài khoản nào ⇒ bỏ qua")
    # lỗi khi kiểm dòng tiền TREO phải hiện ra (không nuốt), phần đẳng thức vẫn chạy
    broken_kw = dict(gate_kw, nav_dir=os.path.join(tmp, "khong_co_thu_muc"))
    ops, investor = g.cash_flow_warnings(day10, **broken_kw)
    ok(len(ops) == 2 and g.PENDING_FLOW_MARKER in ops[0] and "KHÔNG kiểm được dòng tiền treo" in ops[0]
       and "KHÔNG chạy được" in ops[1] and investor == [],
       f"J: không đọc được nav_history ⇒ cả hai phép kiểm nói rõ lỗi của mình, không ném; được {ops}")

    def warn(path, kwargs=gate_kw, poison=None):
        real, g.cash_flow_warnings = g.cash_flow_warnings, (poison or (lambda r: real(r, **kwargs)))
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                g._warn_cash_flows(path)               # không được ném: cảnh báo, không chặn
        finally:
            g.cash_flow_warnings = real
        return err.getvalue()

    for text, present, absent in (
            ("x\n", ["CẢNH BÁO (không chặn) ⚠️ " + ci.WARNING_MARKER, f"KHÔNG có dòng '{ci.INVESTOR_MARKER}'", inv], ["mang cụm vận hành"]),
            (f"…\n   {inv}\n", ["CẢNH BÁO (không chặn) ⚠️ " + ci.WARNING_MARKER], ["KHÔNG có dòng", "mang cụm vận hành"]),
            (f"⚠️ {ci.WARNING_MARKER} (SpaceX) …\n{inv}\n", ["mang cụm vận hành 'DÒNG TIỀN CHỜ KHAI'"], ["KHÔNG có dòng"])):
        report.write_text(text, encoding="utf-8")
        out = warn(report)
        ok(all(x in out for x in present) and not any(x in out for x in absent),
           f"J/C2: cổng in chi tiết ở stderr, nhắc khi báo cáo thiếu dòng trung tính hoặc mang dòng vận hành; "
           f"cần {present}, cấm {absent}; được {out}")
    ok(warn(early) == "", "J: không có gì để cảnh báo ⇒ cổng im lặng")
    # S5: đường "chỉ cảnh báo" không được chặn giao báo cáo bằng một crash
    sys.modules["cash_identity"] = None
    try:
        out = warn(report)
    finally:
        sys.modules["cash_identity"] = ci
    ok("Đẳng thức tiền (SpaceX) KHÔNG chạy được" in out and "ModuleNotFoundError" in out,
       f"J/S5: cash_identity không import được ⇒ _warn_cash_flows không ném, lỗi ở stderr; được {out}")

    def boom(_report):
        raise ZeroDivisionError("nổ giả")

    out = warn(report, poison=boom)
    ok("không kiểm được dòng tiền treo/chưa đối chiếu" in out and "ZeroDivisionError (nổ giả)" in out,
       f"J/S5: mọi lỗi trong đường cảnh báo bị bắt và in ra; được {out}")

    # deliver() đầu-cuối với kênh giả: cash_identity hỏng ⇒ báo cáo VẪN giao đủ hai kênh.
    delivered = []
    saved = (g.run_checked, g.LEGACY_EMAIL_STATE, g._check_nav_flow_records, g.cash_flow_warnings)
    g.run_checked = lambda cmd: delivered.append(Path(cmd[1] if cmd[0] == sys.executable else cmd[0]).name)
    g.LEGACY_EMAIL_STATE = Path(tmp) / "legacy_email.json"
    g._check_nav_flow_records = lambda r: None          # cổng chặn riêng, có selfcheck riêng (đọc dữ liệu mặc định)
    g.cash_flow_warnings = lambda r: saved[3](r, **gate_kw)
    sys.modules["cash_identity"] = None
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = g.deliver(day10, Path(tmp) / "delivery_state.json", "trading_report",
                           Path(tmp) / "notify", Path(tmp) / "email")
    finally:
        sys.modules["cash_identity"] = ci
        g.run_checked, g.LEGACY_EMAIL_STATE, g._check_nav_flow_records, g.cash_flow_warnings = saved
    ok(rc == 0 and delivered == ["report_return_gate.py", "notify", "email"]
       and "Đẳng thức tiền (ZaloPay) KHÔNG chạy được" in err.getvalue() and "INCOMPLETE" not in err.getvalue(),
       f"J/S5: cash_identity không import được ⇒ deliver() vẫn rc=0, giao Discord + email, lỗi ở stderr; được rc={rc} "
       f"{delivered} / {err.getvalue()}")

    import inspect
    src = inspect.getsource(g.deliver)
    order_ = [src.find(x) for x in ("_check_nav_flow_records(report)", "_warn_cash_flows(report)",
                                    'record["artifact_validated_at"] = now()')]
    ok(-1 not in order_ and order_ == sorted(order_),
       f"J: deliver() phải gọi _warn_cash_flows sau cổng nav-flow và trước khi đóng dấu đã kiểm, được {order_}")

    # ---- K. cổng tỉ suất FAIL-CLOSED khi CLI không đưa ra được số chuẩn
    inv_report = Path(tmp) / "SpaceX_weekly_report_2026-10-05_to_2026-10-09.md"

    def table(cell_text):
        inv_report.write_text("### 3.2 Hiệu suất lũy kế\n" + cell_text, encoding="utf-8")

    table("| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,33% | x |\n")

    class Proc:
        def __init__(self, stdout):
            self.stdout = stdout

    def gate_with(fake):
        real = g.subprocess.run
        g.subprocess.run = fake
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                g._check_period_returns(inv_report)
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
    table("| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,00% | x |\n")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1}}'))
    ok(got.startswith("PASS"), f"K: số chuẩn là số nguyên −1 khớp −1,00% ⇒ qua; được {got}")
    table("| Từ khi bắt đầu hoạt động (01/07 → 09/10) | −1,33% | x |\n")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1.33}}'))
    ok(got.startswith("PASS") and "period-return PASS" in got, f"K: số khớp ⇒ qua; được {got}")
    got = gate_with(lambda cmd, **kw: Proc('{"inception": {"return_pct": -1.20}}'))
    ok(got.startswith("BLOCK") and "lệch 0.130pp" in got, f"K: lệch 0,13pp ⇒ CHẶN; được {got}")
    # S4: dòng CÓ MẶT mà ô số không đọc ra một tỉ suất hữu hạn ⇒ CHẶN kèm nguyên ô (không gọi CLI)
    called = []

    def good(cmd, **kw):
        called.append(cmd)
        return Proc('{"inception": {"return_pct": -1.33}}')

    for cell in ("+nan%", "n/a", "—", "−1.330,5%", "", "nan%", "-%", "+inf%", "9" * 400 + "%"):
        table(f"| Từ khi bắt đầu hoạt động (01/07 → 09/10) | {cell} | x |\n")
        got = gate_with(good)
        ok(got.startswith("BLOCK period-return BLOCK") and f"ô số là {cell!r}" in got and "không đọc ra một tỉ suất hữu hạn" in got,
           f"K/S4: ô số {cell!r} ⇒ CHẶN kèm nguyên ô; được {got}")
    table("| Từ khi bắt đầu hoạt động (01/07 → 09/10) |\n")
    got = gate_with(good)
    ok(got.startswith("BLOCK period-return BLOCK") and "ô số là ''" in got, f"K/S4: dòng thiếu cột số ⇒ CHẶN; được {got}")
    ok(called == [], f"K/S4: ô hỏng ⇒ chặn trước khi gọi CLI, được {len(called)} lần gọi")
    table("| WTD | −1,33% | x |\n")
    got = gate_with(good)
    ok(got.startswith("PASS") and "không có dòng 'Từ khi bắt đầu hoạt động'" in got and called == [],
       f"K/S4: báo cáo KHÔNG có dòng đó ⇒ chỉ WARN, bỏ qua (không có gì để so); được {got}")
    ok(g._parse_inception_return_pct("| Từ khi bắt đầu hoạt động | +2,5% |") == 2.5
       and g._parse_inception_return_pct("| Từ khi bắt đầu hoạt động | n/a |") is None
       and g._parse_inception_return_pct("không có dòng") is None, "K: hàm đọc số giữ nguyên hợp đồng cũ")

    # ---- M. LỆNH TAY ĐÃ KHAI (manual_actions) giải thích phần dư — chỉ khi broker xác nhận
    import importlib.util
    MAN_QTY, MAN_OID = 6_000, "20260304_900001"          # bán tay 60tr ≫ ngưỡng (~0,5tr)

    def broker_order(qty=MAN_QTY, avg=PRICE, oid=MAN_OID):
        return {"id": oid, "symbol": "AAA", "side": "NS", "orderType": "LO", "orderStatus": "Filled",
                "price": PRICE, "quantity": qty, "fillQuantity": qty, "averagePrice": avg,
                "transDate": "2026-03-04", "modifiedDate": utc_z(at(4, "14:26"))}

    def man_rec(account="SpaceX", qty=MAN_QTY, status="VERIFIED", bo=None, account_no=None, oid=MAN_OID):
        no = account_no or ACCOUNTS[account]
        return {"id": f"MA-20260304-{account}-AAA-SELL-{oid[-6:]}", "date": "2026-03-04", "time_ict": "14:26:00",
                "account": account, "account_no": no, "ticker": "AAA", "side": "sell", "qty": qty,
                "price": PRICE, "broker_order_id": oid, "source": "selfcheck", "note": "",
                "declared_at": "2026-03-04T15:00:00+07:00",
                "verification": {"verified_at": "2026-03-04T15:01:00+07:00", "method": "dnse_api.order_history",
                                 "envelope_account_no": no, "broker_order": bo or broker_order(qty), "status": status}}

    def manual_world(name, recs, sold=MAN_QTY, copies=None, seller="SpaceX", extra_sold=0, ledger_text=None):
        """`seller` bán tay `sold` cp AAA lúc 04/03 14:26 (KHÔNG có bản ghi orders); `copies` =
        [(tiểu khoản envelope, bản ghi broker)] chép vào dnse_raw kind=order_history (mặc định: bản
        sao của mỗi dòng sổ dưới ĐÚNG tiểu khoản của nó)."""
        wd = World(tmp, name)
        wd.add(seller, at(4, "14:26"), "sell", "AAA", sold, log=False)
        if extra_sold:
            wd.add(seller, at(4, "14:40"), "sell", "AAA", extra_sold, log=False)
        if copies is None:
            copies = [(r["verification"]["envelope_account_no"], r["verification"]["broker_order"]) for r in recs]
        wd.raw_lines[D(2026, 3, 4)] = [json.dumps(
            {"ts": "2026-03-04T15:01:00", "kind": "order_history", "account_no": no, "payload": {"data": [bo]}},
            ensure_ascii=False) for no, bo in copies]
        wd.build()
        (wd.dir / "manual.json").write_text(ledger_text if ledger_text is not None else
                                            json.dumps({"schema_version": 1, "actions": recs}), encoding="utf-8")
        return wd

    def mcheck(wd, account="SpaceX", mod=ci, **kw):
        return mod.check_account(account, **dict(dict(wd.paths, manual_actions_path=str(wd.dir / "manual.json")), **kw))

    def explained(res):
        w = window(res, 4)
        return (not res["suspects"] and w["kind"] is None and abs(w["unexplained"]) < 1
                and w.get("manual") == [man_rec()["id"]] and w["qty_gaps"] == {})

    # M0. không có lệnh tay trong sổ ⇒ đúng là cửa sổ mở "không kết luận được" (đối chứng)
    res = mcheck(manual_world("M0_none", []))
    ok(open_days(res) == [4] and window(res, 4)["kind"] == ci.LABEL_QUANTITY and window(res, 4)["qty_gaps"] == {"AAA": -MAN_QTY}
       and "manual" not in window(res, 4),
       f"M0: bán tay KHÔNG khai ⇒ cửa sổ 04/03 mở, AAA -6000; được {open_days(res)} {window(res, 4).get('qty_gaps')}")
    note("M0", res)

    # M(a). khai VERIFIED + bản sao dnse_raw ⇒ hết suspect, giá trị tiền = KL × giá khớp − phí − thuế
    good_world = manual_world("Ma_ok", [man_rec()])
    res = mcheck(good_world)
    ok(explained(res) and window(res, 4)["sell"] == MAN_QTY * PRICE
       and abs(window(res, 4)["fees"] - MAN_QTY * PRICE * FEE_SELL) < 1e-6,
       f"M(a): lệnh tay VERIFIED ⇒ cửa sổ đóng, bán 60tr, phí+thuế bán đúng biểu; được suspects={open_days(res)} "
       f"w={ {k: window(res, 4).get(k) for k in ('sell', 'fees', 'unexplained', 'kind', 'manual')} }")
    ok(any("đã tính lệnh tay đã khai AAA bán 6.000 cp" in n for n in window(res, 4)["notes"]),
       "M(a): cửa sổ ghi chú lệnh tay đã tính (kênh vận hành)")
    note("Ma", res)
    rep = ci.report("SpaceX", **dict(good_world.paths, manual_actions_path=str(good_world.dir / "manual.json")))
    ok(rep["error"] is None and rep["investor_line"] is None
       and not any(ci.WARNING_MARKER in line for line in rep["ops_today"] + rep["ops_lines"]),
       f"M(a)/kênh: đường THÀNH CÔNG ⇒ không dòng nhà đầu tư, không cảnh báo vận hành; được {rep}")
    # cùng thế giới, ack cũ khoá đúng 2 mốc (phần dư trước khi có sổ) ⇒ không cần, không làm hỏng
    good_world.ack("SpaceX", 3, 4, MAN_QTY * PRICE * (1 - FEE_SELL), acked_qty_gaps={"AAA": -MAN_QTY}).build()
    (good_world.dir / "manual.json").write_text(json.dumps({"schema_version": 1, "actions": [man_rec()]}), encoding="utf-8")
    res = mcheck(good_world)
    ok(explained(res) and window(res, 4)["acked"] is None and not window(res, 4)["ack_mismatch"],
       "M(a)/ack: lệnh tay tự giải thích ⇒ ack cũ không được dùng tới, không báo lệch")
    res = mcheck(good_world, manual_actions_path=str(good_world.dir / "khong_co.json"))
    ok(not res["suspects"] and window(res, 4)["acked"] is not None,
       "M(a)/ack: bỏ sổ lệnh tay ⇒ ack cũ khớp cửa sổ VẪN hợp lệ (đóng cửa sổ như trước)")

    # M(b). khai ≠ thực ⇒ vẫn suspect
    res = mcheck(manual_world("Mb_more", [man_rec()], extra_sold=1_000))
    ok(open_days(res) == [4] and window(res, 4)["qty_gaps"] == {"AAA": -1_000.0} and window(res, 4).get("manual"),
       f"M(b): khai 6000 mà thực bán 7000 ⇒ vẫn mở với phần dư AAA -1000; được {window(res, 4).get('qty_gaps')}")
    res = mcheck(manual_world("Mb_price", [man_rec(bo=broker_order(avg=9_000.0))]))
    ok(open_days(res) == [4] and window(res, 4)["qty_gaps"] == {} and window(res, 4)["over"]
       and abs(window(res, 4)["unexplained"] - MAN_QTY * 1_000 * (1 - FEE_SELL)) < 1,
       f"M(b): giá khớp broker 9.000 trong khi tiền thật về theo 10.000 ⇒ phần dư 6tr vẫn cờ; được "
       f"{window(res, 4)['unexplained']:,.0f}")
    res = mcheck(manual_world("Mb_less", [man_rec(qty=5_000)]))
    ok(open_days(res) == [4] and window(res, 4)["qty_gaps"] == {"AAA": -1_000.0},
       "M(b): khai 5000 (broker xác nhận 5000) mà vị thế giảm 6000 ⇒ vẫn mở phần dư -1000")

    # M(c). không VERIFIED / thiếu bằng chứng ⇒ không mở gì
    for label, recs, copies, why in (
            ("Mc_unverified", [man_rec(status="UNVERIFIED")], None, "chưa xác nhận broker"),
            ("Mc_rejected", [man_rec(status="REJECTED")], None, "chưa xác nhận broker"),
            ("Mc_nocopy", [man_rec()], [], "không có bản sao khớp từng byte"),
            ("Mc_tampered", [man_rec()], [(ACCOUNTS["SpaceX"], dict(broker_order(), averagePrice=10_500))],
             "không có bản sao khớp từng byte"),
            ("Mc_qty", [dict(man_rec(), qty=6_500)], None, "KL khớp")):
        res = mcheck(manual_world(label, recs, copies=copies))
        ok(open_days(res) == [4] and "manual" not in window(res, 4)
           and any("KHÔNG được tính" in n and why in n for n in window(res, 4)["notes"]),
           f"M(c) {label}: không đủ bằng chứng ⇒ cửa sổ vẫn mở + ghi lý do '{why}'; được {open_days(res)} "
           f"{[n for n in window(res, 4)['notes'] if 'lệnh tay' in n]}")
    wd = manual_world("Mc_channel", [man_rec(status="UNVERIFIED")])
    rep = ci.report("SpaceX", **dict(wd.paths, manual_actions_path=str(wd.dir / "manual.json")))
    inv = rep["investor_line"] or ""
    ok(ci.INVESTOR_MARKER in inv and no_signed_pct(inv)
       and not any(x in inv for x in ("lệnh tay", "KHAI", "manual", ".json", "dnse_raw", "MA-2026"))
       and any("KHÔNG được tính" in line for line in rep["ops_lines"]),
       f"M(c)/kênh: khai chưa xác nhận ⇒ báo cáo nhà đầu tư chỉ một dòng trung tính, lý do nội bộ chỉ ở "
       f"kênh vận hành; được investor={inv!r}")
    wd = manual_world("Mc_broken", [man_rec()], ledger_text="{hỏng")
    res = mcheck(wd)
    rep = ci.report("SpaceX", **dict(wd.paths, manual_actions_path=str(wd.dir / "manual.json")))
    ok(open_days(res) == [4] and any("manual.json" in e and "KHÔNG lệnh tay" in e for e in res["source_errors"])
       and rep["error"] is None and "manual.json" not in (rep["investor_line"] or "")
       and any("manual.json" in line for line in rep["ops_lines"]),
       f"M(c): sổ hỏng ⇒ không giải thích gì, lỗi nêu file ở kênh vận hành, không làm gãy report; được {res['source_errors']}")

    # M(d). §12 — tài khoản khác không ảnh hưởng
    base_z = mcheck(manual_world("Md_base", []), "ZaloPay")
    wd = manual_world("Md_other", [man_rec()])
    ok([(w["date1"], round(w["unexplained"], 6), w["suspect"]) for w in mcheck(wd, "ZaloPay")["windows"]]
       == [(w["date1"], round(w["unexplained"], 6), w["suspect"]) for w in base_z["windows"]],
       "M(d): lệnh tay VERIFIED của SpaceX không chạm đẳng thức ZaloPay (cùng file dnse_raw)")
    ok(not any(man_rec()["id"] in n for w in mcheck(wd, "ZaloPay")["windows"] for n in w["notes"]),
       "M(d): dòng khai của SpaceX không được lọt cả ghi chú vào cửa sổ ZaloPay (§12 lọc trước khi xét)")
    res = mcheck(manual_world("Md_label", [man_rec(account="SpaceX", account_no=ACCOUNTS["ZaloPay"])]))
    ok(open_days(res) == [4] and "manual" not in window(res, 4),
       "M(d): dòng khai nhãn SpaceX nhưng tiểu khoản ZaloPay (bản sao dưới ZaloPay) ⇒ KHÔNG giải thích SpaceX")
    res = mcheck(manual_world("Md_envelope", [man_rec()], copies=[(ACCOUNTS["ZaloPay"], broker_order())]))
    ok(open_days(res) == [4] and "manual" not in window(res, 4),
       "M(d): bản sao order_history nằm dưới envelope tiểu khoản KHÁC ⇒ không tính (§12)")
    res = mcheck(manual_world("Md_zalo", [man_rec(account="ZaloPay")], seller="ZaloPay"), "ZaloPay")
    ok(not res["suspects"] and window(res, 4).get("manual"), "M(d): cùng cơ chế chạy đúng cho ZaloPay")

    # M2. không đếm đôi: sao kê (fill broker xác nhận) thắng; lệnh đã nằm trong orders thì bỏ qua
    wd = manual_world("M2_seed", [man_rec()])
    wd.seed = {"SpaceX": {"missing_fills_broker_confirmed": [
        {"date": "2026-03-04", "ticker": "AAA", "side": "sell", "qty": MAN_QTY, "price": PRICE}]}}
    wd.build()
    (wd.dir / "manual.json").write_text(json.dumps({"schema_version": 1, "actions": [man_rec()]}), encoding="utf-8")
    res = mcheck(wd)
    ok(not res["suspects"] and window(res, 4)["sell"] == MAN_QTY * PRICE and "manual" not in window(res, 4)
       and any("sao kê thắng" in n for n in window(res, 4)["notes"]),
       f"M2: sao kê đã có fill cùng ngày/mã/chiều ⇒ không cộng lệnh tay lần nữa; được bán {window(res, 4)['sell']:,.0f}")
    wd = World(tmp, "M2_orders")
    wd.add("SpaceX", at(4, "14:26"), "sell", "AAA", MAN_QTY, log=False)
    wd.extra_raw[("SpaceX", D(2026, 3, 4))] = [{"kind": "orders", "account_no": ACCOUNTS["SpaceX"], "ts": "2026-03-04T14:30:00",
                                                "payload": {"orders": [order("SpaceX", 900001, "AAA", "NS", MAN_QTY, at(4, "14:26"))]}}]
    wd.raw_lines[D(2026, 3, 4)] = [json.dumps({"ts": "2026-03-04T15:01:00", "kind": "order_history",
                                               "account_no": ACCOUNTS["SpaceX"], "payload": {"data": [broker_order()]}})]
    wd.build()
    (wd.dir / "manual.json").write_text(json.dumps({"schema_version": 1, "actions": [man_rec()]}), encoding="utf-8")
    res = mcheck(wd)
    ok(not res["suspects"] and window(res, 4)["sell"] == MAN_QTY * PRICE and "manual" not in window(res, 4),
       f"M2: lệnh đã có trong bản ghi orders (cùng mã lệnh) ⇒ không đếm đôi; được bán {window(res, 4)['sell']:,.0f}")

    # M3. sổ rỗng / vắng ⇒ y hệt khi chưa có tính năng
    for label, text in (("M3_empty", json.dumps({"schema_version": 1, "actions": []})), ("M3_missing", None)):
        wd = internal_only(World(tmp, label)).add("SpaceX", at(10, "10:30"), "external", 5_000_000.0).build()
        if text is not None:
            (wd.dir / "manual.json").write_text(text, encoding="utf-8")
        a, b = mcheck(wd), wd.check("SpaceX")
        ok(json.dumps(ci._jsonable(a), sort_keys=True) == json.dumps(ci._jsonable(b), sort_keys=True),
           f"M3 {label}: sổ rỗng/vắng ⇒ kết quả trùng từng byte với lúc không truyền sổ")

    # M4. MUTANT — bỏ trừ giá trị tiền / bỏ kiểm VERIFIED ⇒ các kiểm tra trên phải ĐỎ
    src = Path(BIN, "cash_identity.py").read_text(encoding="utf-8")

    def mutant(tag, old, new):
        ok(src.count(old) == 1, f"M4 {tag}: chuỗi đột biến phải xuất hiện đúng 1 lần trong cash_identity.py")
        path = Path(tmp) / f"cash_identity_mut_{tag}.py"
        path.write_text(src.replace(old, new), encoding="utf-8")
        spec = importlib.util.spec_from_file_location(f"cash_identity_mut_{tag}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    mut_e = mutant("e", '"qty": qty, "value": qty * price, "manual_id"', '"qty": qty, "value": 0.0, "manual_id"')
    res = mcheck(manual_world("M4_e", [man_rec()]), mod=mut_e)
    ok(not explained(res) and open_days(res) == [4],
       "M4(e): đột biến bỏ giá trị tiền của lệnh tay ⇒ M(a) phải đỏ (cửa sổ vẫn mở vì phần dư tiền 60tr)")
    mut_f = mutant("f", "ok, why = ma.evidence_check(rec, account_no, ed) if", 'ok, why = (True, "") if')
    res = mcheck(manual_world("M4_f", [man_rec(status="UNVERIFIED")]), mod=mut_f)
    ok(not open_days(res),
       "M4(f): đột biến bỏ kiểm VERIFIED ⇒ dòng UNVERIFIED mở được cửa sổ ⇒ kiểm tra M(c) phải bắt (ĐỎ)")
    res = mcheck(manual_world("M4_f_ok", [man_rec(status="UNVERIFIED")]))
    ok(open_days(res) == [4], "M4(f): bản thật vẫn giữ cửa sổ mở với cùng dữ liệu")
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
