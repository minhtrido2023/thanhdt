#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho realized P&L + cổ tức trong reconcile_equity.py (aria-A1, 2026-09-13).

Chạy:  python3 mike/bin/reconcile_equity_realized_selfcheck.py
Phải PASS y hệt khi chạy từ thư mục khác và không có TZ (§16 + skill `verify-before-done`):
       cd /tmp && env -u TZ python3 <repo>/mike/bin/reconcile_equity_realized_selfcheck.py

Bug gốc: vế trái đẳng thức chỉ có lãi/lỗ CHƯA thực hiện ⇒ residual +23,7tr (+2,41% NAV) SpaceX
2026-08-28, vì realized −31,0tr và cổ tức ròng +11,6tr đã nằm trong tiền mặt (vế phải) mà vế trái
không có. Fixture TỔNG HỢP, dựng trong thư mục tạm — không đọc dnse_raw thật, không gọi broker,
không gọi BQ. Ca end-to-end chứng minh NGƯỢC: `--no-realized` (= công thức cũ) trên cùng fixture
PHẢI lệch đúng bằng realized + cổ tức, nếu không test chỉ đang khẳng định suông.
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import reconcile_equity as RE             # noqa: E402
import verify_account_snapshot as VAS     # noqa: E402
import dividend_adjusted_return as DAR    # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def near(a, b, tol=0.01):
    return abs(a - b) <= tol


def ev(ts, tk, side, qty, price):
    return (ts, f"{tk}-{ts}-{side}", tk, side, float(qty), float(price))


print("1. realized theo lô-đang-sống")
r = RE.realized_pnl_from_events({"2026-07-01": [
    ev("2026-07-01T09:00", "AAA", "buy", 100, 10_000),
    ev("2026-07-01T09:10", "AAA", "buy", 100, 12_000),
    ev("2026-07-01T10:00", "AAA", "sell", 150, 13_000)]}, "2026-07-01", [])
check("bình quân 11.000, bán 150@13.000 ⇒ +300.000", near(r["realized"], 300_000), r)
check("không có phần untraced", r["untraced_sell_proceeds"] == 0, r)
check("buy/sell value", near(r["buy_value"], 2_200_000) and near(r["sell_value"], 1_950_000), r)

print("2. hằng đẳng thức realized + unrealized = Σbán − Σmua + MTM (có lô reset kiểu LPB)")
evs = {"2026-07-01": [ev("2026-07-01T09:00", "LPB", "buy", 900, 50_000)],
       "2026-07-06": [ev("2026-07-06T09:00", "LPB", "sell", 900, 52_000)],
       "2026-07-15": [ev("2026-07-15T09:00", "LPB", "buy", 900, 51_000),
                      ev("2026-07-15T13:00", "LPB", "sell", 400, 53_000)]}
r = RE.realized_pnl_from_events(evs, "2026-07-20", [])
book = VAS.build_cost_books(evs, "2026-07-20", [])["LPB"]
mtm_px = 49_000
unreal = book.qty * mtm_px - book.basis
lhs = r["realized"] + unreal
rhs = r["sell_value"] - r["buy_value"] + book.qty * mtm_px
check("realized = 900×2.000 + 400×2.000 = 2.600.000", near(r["realized"], 2_600_000), r)
check("hằng đẳng thức đóng tới đồng", near(lhs, rhs), f"{lhs} vs {rhs}")
check("lô còn lại khớp CostBook của verify_account_snapshot (500 @51.000)",
      near(book.qty, 500) and near(book.avg_cost, 51_000), (book.qty, book.avg_cost))

print("3. bán legacy vượt KL trace được ⇒ KHÔNG bịa giá vốn")
r = RE.realized_pnl_from_events({"2026-07-07": [ev("2026-07-07T09:00", "VIB", "sell", 1000, 20_000)]},
                                "2026-07-10", [])
check("realized = 0", r["realized"] == 0, r)
check("untraced = 20.000.000, gắn đúng mã", near(r["untraced_sell_proceeds"], 20_000_000)
      and list(r["untraced_by_ticker"]) == ["VIB"], r)
r = RE.realized_pnl_from_events({"2026-07-07": [ev("2026-07-07T09:00", "VIB", "buy", 300, 20_000),
                                                ev("2026-07-07T10:00", "VIB", "sell", 500, 21_000)]},
                                "2026-07-10", [])
check("bán 500 khi chỉ trace 300: realized 300×1.000, untraced 200×21.000",
      near(r["realized"], 300_000) and near(r["untraced_sell_proceeds"], 4_200_000), r)

print("4. corp-action: mua trước ex-date, bán sau ex-date (chia 1:2)")
ca = [{"ticker": "BBB", "ex_date": "2026-07-10", "qty_multiplier": 2.0}]
r = RE.realized_pnl_from_events({"2026-07-01": [ev("2026-07-01T09:00", "BBB", "buy", 100, 20_000)],
                                 "2026-07-15": [ev("2026-07-15T09:00", "BBB", "sell", 200, 11_000)]},
                                "2026-07-20", ca)
check("200×11.000 − 2.000.000 = +200.000, không untraced",
      near(r["realized"], 200_000) and r["untraced_sell_proceeds"] == 0, r)

print("5. cổ tức ròng — số thật MBB 17/07/2026 (gộp 2.400.000, thuế 5% lúc chi trả)")
d = RE.net_cash_dividends({"2026-07-09": 2_400_000, "2026-07-16": 855_000, "2026-06-30": 999_999},
                          855_000, "2026-07-01", "2026-07-20", 0.05)
check("ngoài cửa sổ bị loại, gộp 3.255.000", near(d["gross"], 3_255_000), d)
check("đã chi trả 2.400.000, thuế 120.000, ròng 3.135.000",
      near(d["paid"], 2_400_000) and near(d["tax"], 120_000) and near(d["net"], 3_135_000), d)
d = RE.net_cash_dividends({"2026-09-11": 80_000_000}, 80_000_000, "2026-07-01", "2026-09-11", 0.05)
check("còn nguyên phải thu ⇒ chưa trừ thuế (DGC 09-11)", near(d["tax"], 0) and near(d["net"], 80_000_000), d)

print("6. lãi margin ước tính theo ngày lịch, carry-forward")
m = RE.margin_interest_estimate({"2026-07-02": 365_000_000, "2026-07-04": 0}, "2026-07-01",
                                "2026-07-05", 0.125)
check("ngày 1 nợ 0, ngày 2-3 nợ 365tr ⇒ 2×125.000 = 250.000", near(m, 250_000), m)

print("7. end-to-end main() trên fixture tạm + lọc account_no (§12)")
ACC, OTHER = "0000000001", "0000000002"
with tempfile.TemporaryDirectory() as tmp:
    def raw(date, recs):
        with open(os.path.join(tmp, f"dnse_raw_{date}.jsonl"), "w", encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec) + "\n")

    def order(acct, oid, tk, side, qty, px, ts):
        return {"id": oid, "accountNo": acct, "symbol": tk, "side": side, "fillQuantity": qty,
                "averagePrice": px, "modifiedDate": ts}

    def bal(acct, ts, cash, rcv=0, debt=0):
        return {"kind": "balances", "ts": ts, "account_no": acct,
                "payload": {"stock": {"totalCash": cash, "availableCash": cash - rcv,
                                      "totalDebt": debt, "depositFeeAmount": 0,
                                      "cashDividendReceiving": rcv}}}

    capital = 100_000_000
    # D1: mua 1.000 CCC @50.000 + 500 DDD @40.000. D2: bán 600 CCC @55.000. Cổ tức DDD 500×2.000 ghi phải thu D2.
    # Account KHÁC có lệnh + số dư trong CÙNG file — nếu lọc hỏng, số sẽ lệch.
    raw("2026-07-01", [
        {"kind": "orders", "payload": {"orders": [
            order(ACC, 1, "CCC", "NB", 1000, 50_000, "2026-07-01T09:00"),
            order(ACC, 2, "DDD", "NB", 500, 40_000, "2026-07-01T09:05"),
            order(OTHER, 9, "CCC", "NS", 5000, 90_000, "2026-07-01T09:06")]}},
        bal(ACC, "2026-07-01T20:00", capital - 70_000_000),
        bal(OTHER, "2026-07-01T20:00", 999_000_000, rcv=50_000_000),
    ])
    realized_true = 600 * 5_000
    div_gross = 1_000_000
    cost_left = 400 * 50_000 + 500 * 40_000
    fees = cost_left * 0.075 / 100
    cash_d2 = capital - 70_000_000 + 600 * 55_000 + div_gross
    # Tiền mặt dựng sao cho đẳng thức MỚI đóng đúng 0: trừ phí theo đúng công thức vế trái.
    cash_d2 -= fees
    raw("2026-07-02", [
        {"kind": "orders", "payload": {"orders": [order(ACC, 3, "CCC", "NS", 600, 55_000, "2026-07-02T10:00")]}},
        bal(OTHER, "2026-07-02T20:00", 1, rcv=80_000_000, debt=500_000_000),
        bal(ACC, "2026-07-02T20:00", cash_d2, rcv=div_gross),
    ])
    mtm = 400 * 52_000 + 500 * 41_000
    unreal = mtm - cost_left
    snap = {"account": "FIX", "asof": "2026-07-02", "dates_included": ["2026-07-01", "2026-07-02"],
            "total_unrealized_pnl": unreal, "total_mtm_value": mtm, "total_cost_value": cost_left}

    old_vas, old_dar = VAS.EXEC_DIR, DAR.EXEC_LOG_DIR
    VAS.EXEC_DIR, DAR.EXEC_LOG_DIR = tmp, tmp
    try:
        outs = {}
        for tag, extra in (("after", []), ("before", ["--no-realized"])):
            sp = os.path.join(tmp, f"verified_snapshot_FIX_{tag}.json")
            json.dump(snap, open(sp, "w"))
            argv = ["reconcile_equity.py", "--account", "FIX", "--account-no", ACC,
                    "--starting-capital", str(capital), "--snapshot", sp,
                    "--balance-raw", os.path.join(tmp, "dnse_raw_2026-07-02.jsonl")] + extra
            old_argv, sys.argv = sys.argv, argv
            buf = io.StringIO()
            try:
                with redirect_stdout(buf), redirect_stderr(buf):
                    RE.main()
                rc = 0
            except SystemExit as e:
                rc = e.code or 0
            finally:
                sys.argv = old_argv
            outs[tag] = (rc, json.load(open(sp.replace("verified_snapshot", "reconcile_equity"))), buf.getvalue())
    finally:
        VAS.EXEC_DIR, DAR.EXEC_LOG_DIR = old_vas, old_dar

    rc_a, a, txt_a = outs["after"]
    rc_b, b, _ = outs["before"]
    check("realized đọc lại từ fill đúng account = 3.000.000", near(a["realized_pnl"], realized_true), a["realized_pnl"])
    check("cổ tức gộp 1.000.000 (chưa chi trả ⇒ chưa thuế); số dư account KHÁC không lọt vào",
          near(a["cash_dividends"]["gross"], div_gross) and near(a["cash_dividends"]["tax"], 0), a["cash_dividends"])
    check("cash vế phải = đúng bản ghi của account mình", near(a["cash"], cash_d2), a["cash"])
    check("Σmua/Σbán chỉ của account mình", near(a["fill_buy_value"], 70_000_000)
          and near(a["fill_sell_value"], 33_000_000), (a["fill_buy_value"], a["fill_sell_value"]))
    check("SAU sửa: residual = 0, rc=0", near(a["residual"], 0, 1.0) and rc_a == 0, (a["residual"], rc_a))
    check("CHỨNG MINH NGƯỢC: công thức cũ lệch đúng −(realized + cổ tức)",
          near(b["residual"], -(realized_true + div_gross), 1.0), b["residual"])
    check("công thức cũ giữ nguyên unrealized/fee (không đổi)",
          near(b["unrealized_pnl"], a["unrealized_pnl"]) and near(b["trading_fees_used"], a["trading_fees_used"])
          and near(a["trading_fees_used"], fees), (b["trading_fees_used"], fees))
    check("diễn giải: phí trên doanh số + thuế bán được in",
          "TỔNG khớp mua+bán" in txt_a and "Thuế TNCN" in txt_a and "DƯ SAU DIỄN GIẢI" in txt_a)
    check("diễn giải: phí 0,075%×103tr − phí vế trái; thuế 0,1%×33tr",
          near(a["explain_fee_on_turnover_gap_est"], 103_000_000 * 0.00075 - fees)
          and near(a["explain_sell_tax_est"], 33_000), (a["explain_fee_on_turnover_gap_est"], a["explain_sell_tax_est"]))

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
