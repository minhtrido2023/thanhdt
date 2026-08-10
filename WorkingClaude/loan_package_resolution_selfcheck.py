#!/usr/bin/env python3
"""Selfcheck — gói vay hiệu lực của lệnh MUA phải (a) giải theo MÃ cho mọi lệnh không có
đòn bẩy chỉ định, (b) GIỐNG HỆT nhau giữa ppse-precheck (executor) và place_order (brokers).

Bug được vá (2026-08-07, ca DRI/UPCOM trên SpaceX — chẩn đoán Winston_20260807_065124):
lệnh MUA thường (không cash_only, không đòn bẩy) đi ra với loan_package_id=None ⇒
`dnse_api` rơi về gói DEFAULT account (1841, mainboard-only) ⇒ DNSE từ chối CẢ ppse lẫn
place_order với mã UPCOM ⇒ `get_max_buy_qty` trả None ⇒ WAIT_CASH lặp vô hạn, trông y hệt
"thiếu tiền" trong khi tài khoản thừa tiền.

KHÔNG kết nối DNSE thật (thị trường đóng; connect thật sẽ làm mới cache trading-token và
quấy nhiễu phiên live) — dùng client giả, `_raw_log=None` để không ghi vào dnse_raw thật.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.brokers import DNSEBroker              # noqa: E402
from trading_bot.plan_funding_gate import _effective_loan_package  # noqa: E402

ACCOUNT_DEFAULT = 1841          # gói default SpaceX (mainboard-only)
UPCOM_PKG = 1122                # gói hợp lệ cho mã UPCOM (ca TV1 thật 07-29)
LEVER_PKG = 1840                # gói đòn bẩy CAPIT "RocketX"


class FakeClient:
    """Giả DNSEClient: chỉ 2 hàm broker dùng ở đường này + biến ghi lại lệnh đã gửi."""

    def __init__(self, valid_ids):
        self.loan_package_id = ACCOUNT_DEFAULT
        self._valid = valid_ids
        self.sent = []            # [(symbol, loan_package_id đã gửi)]

    def loan_packages(self, account_id, symbol=None):
        return {"loanPackages": [{"id": i, "type": ("M" if i == LEVER_PKG else "N")}
                                 for i in self._valid]}

    def place_order(self, account_id, symbol, qty, side, order_type, price,
                    loan_package_id=None):
        self.sent.append((symbol, loan_package_id))
        return {"id": "OID-TEST"}

    def ppse(self, account_id, symbol, price, market_type="STOCK", loan_package_id=None):
        # qmaxBuy chỉ trả > 0 khi hỏi bằng gói HỢP LỆ cho mã — mô phỏng đúng hành vi DNSE
        # đã quan sát (gói sai ⇒ không đo được sức mua ⇒ executor kết luận "thiếu tiền").
        ok = loan_package_id in self._valid
        return {"qmaxBuy": 10000 if ok else 0, "pp0Buy": 5e8 if ok else 0}


class Order:
    def __init__(self, ticker, cash_only=False, loan_package_id=None):
        self.ticker = ticker
        self.cash_only = cash_only
        self.loan_package_id = loan_package_id
        self.side = "buy"


def make_broker(valid_ids):
    b = DNSEBroker(account_id="0002023347", label="SpaceX")
    b.client = FakeClient(valid_ids)
    b._raw_log = None             # không ghi vào data/execution_logs/dnse_raw_*.jsonl thật
    return b


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + detail) if detail else ''}")
    return bool(cond)


def main():
    ok = True

    # ── 1. Mainboard: gói default HỢP LỆ ⇒ KHÔNG đổi hành vi ────────────────────────────
    print("[1] Mainboard (default 1841 nằm trong danh sách hợp lệ) — phải giữ nguyên default")
    b = make_broker([ACCOUNT_DEFAULT, UPCOM_PKG])
    o = Order("MBB")
    eff, src = _effective_loan_package(o, b)
    b.place_order("MBB", 100, "buy", price=25000,
                  cash_only=False, loan_package_id=None)
    sent = b.client.sent[-1][1]
    ok &= check("gate/precheck giải ra gói default", eff == ACCOUNT_DEFAULT, f"eff={eff} src={src}")
    ok &= check("place_order gửi đúng gói default", sent == ACCOUNT_DEFAULT, f"sent={sent}")
    ok &= check("precheck == place_order (không lệch)", eff == sent)
    ok &= check("tương đương hành vi CŨ (None ⇒ dnse_api fallback default)",
                sent == b.client.loan_package_id,
                "lệnh mainboard đi ra y hệt trước khi vá")

    # ── 2. UPCOM: gói default KHÔNG hợp lệ ⇒ phải thay bằng gói khác, KHÔNG None ─────────
    print("[2] UPCOM/DRI (default 1841 KHÔNG hợp lệ) — phải thay bằng gói hợp lệ khác")
    b = make_broker([UPCOM_PKG])
    o = Order("DRI")
    eff, src = _effective_loan_package(o, b)
    b.place_order("DRI", 100, "buy", price=12000,
                  cash_only=False, loan_package_id=None)
    sent = b.client.sent[-1][1]
    ok &= check("gate/precheck KHÔNG trả None", eff is not None, f"eff={eff} src={src}")
    ok &= check("gate/precheck KHÔNG trả gói default sai", eff != ACCOUNT_DEFAULT)
    ok &= check("gate/precheck trả gói hợp lệ UPCOM", eff == UPCOM_PKG)
    ok &= check("place_order gửi đúng gói hợp lệ", sent == UPCOM_PKG, f"sent={sent}")
    ok &= check("precheck == place_order (không lệch)", eff == sent)

    # ── 3. Triệu chứng thật: ppse precheck của executor phải đo ra ĐỦ tiền cho DRI ───────
    print("[3] Tái hiện triệu chứng WAIT_CASH: get_max_buy_qty(DRI) trước/sau khi vá")
    b = make_broker([UPCOM_PKG])
    o = Order("DRI")
    qmax_bug = b.get_max_buy_qty("DRI", 12000,
                                 loan_package_id=getattr(o, "loan_package_id", None))
    qmax_fix = b.get_max_buy_qty("DRI", 12000,
                                 loan_package_id=_effective_loan_package(o, b)[0])
    ok &= check("cách CŨ (lp thô=None) đo ra 0 ⇒ WAIT_CASH vô hạn", qmax_bug == 0,
                f"qmax={qmax_bug}")
    ok &= check("cách MỚI (gói hiệu lực) đo ra sức mua thật", qmax_fix and qmax_fix > 0,
                f"qmax={qmax_fix}")

    # ── 4. Đòn bẩy CAPIT: KHÔNG đổi hành vi (validate như cũ, cả nhánh hợp lệ và không) ──
    print("[4] Đòn bẩy CAPIT chỉ định — hành vi phải y nguyên")
    b = make_broker([ACCOUNT_DEFAULT, LEVER_PKG])
    o = Order("VIX", loan_package_id=LEVER_PKG)
    eff, src = _effective_loan_package(o, b)
    b.place_order("VIX", 100, "buy", price=20000, cash_only=False,
                  loan_package_id=LEVER_PKG)
    sent = b.client.sent[-1][1]
    ok &= check("gói đòn bẩy hợp lệ ⇒ dùng đúng gói đòn bẩy", eff == LEVER_PKG == sent,
                f"eff={eff} sent={sent} src={src}")

    b = make_broker([ACCOUNT_DEFAULT])          # 1840 KHÔNG hợp lệ cho mã này
    o = Order("VIX", loan_package_id=LEVER_PKG)
    eff, src = _effective_loan_package(o, b)
    b.place_order("VIX", 100, "buy", price=20000, cash_only=False,
                  loan_package_id=LEVER_PKG)
    sent = b.client.sent[-1][1]
    ok &= check("gói đòn bẩy KHÔNG hợp lệ ⇒ rơi về default (fail-safe, không đòn bẩy)",
                eff == ACCOUNT_DEFAULT == sent, f"eff={eff} sent={sent} src={src}")

    # ── 5. cash_only vẫn giải theo mã như trước ─────────────────────────────────────────
    print("[5] Lệnh cash_only (DISCRETIONARY_SPECIAL) — vẫn giải theo mã như trước")
    b = make_broker([UPCOM_PKG])
    o = Order("TV1", cash_only=True)
    eff, _ = _effective_loan_package(o, b)
    b.place_order("TV1", 100, "buy", price=15000, cash_only=True, loan_package_id=None)
    ok &= check("cash_only giải đúng + không lệch", eff == UPCOM_PKG == b.client.sent[-1][1])

    # ── 6. Broker không hỗ trợ resolver (paper/PHS) ⇒ None, không crash ─────────────────
    print("[6] Broker không có _resolve_loan_package_id (paper) ⇒ None, không crash")
    class Dummy:
        pass
    eff, src = _effective_loan_package(Order("MBB"), Dummy())
    ok &= check("trả (None, account_default)", eff is None and src == "account_default",
                f"eff={eff} src={src}")

    # ── 7. executor.py thật sự dùng gói hiệu lực ở ppse precheck ────────────────────────
    print("[7] executor.py dùng _effective_loan_package cho ppse precheck (kiểm mã nguồn)")
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "trading_bot", "executor.py")
    with open(src_path, encoding="utf-8") as f:
        src_txt = f.read()
    ok &= check("gọi _effective_loan_package(o, self.broker)",
                "_effective_loan_package(o, self.broker)" in src_txt)
    qmax_call = "qmax = self.broker." + src_txt.split("qmax = self.broker.")[1].split("\n")[0]
    ok &= check("ppse precheck KHÔNG còn nhận lp thô của lệnh",
                "loan_package_id=_eff_lp" in qmax_call
                and 'getattr(o, "loan_package_id"' not in qmax_call, qmax_call.strip())

    # ── 8. Lệnh BÁN không cash_only ⇒ place_order KHÔNG resolve theo mã (bug 08-10) ──────
    print("[8] Lệnh BÁN (không cash_only, không đòn bẩy) — place_order phải gửi lp=None")
    b = make_broker([UPCOM_PKG])
    b.place_order("BID", 600, "sell", price=18000, cash_only=False, loan_package_id=None)
    sent = b.client.sent[-1][1]
    ok &= check("place_order gửi lp=None cho lệnh BÁN (DNSE tự chọn deal)", sent is None,
                f"sent={sent}")

    # ── 9. Lệnh MUA vẫn resolve theo mã như [1]/[2] (không hồi quy khi vá #8) ───────────
    print("[9] Lệnh MUA UPCOM sau khi vá #8 — vẫn resolve như trước (không hồi quy)")
    b = make_broker([UPCOM_PKG])
    b.place_order("DRI", 100, "buy", price=12000, cash_only=False, loan_package_id=None)
    sent = b.client.sent[-1][1]
    ok &= check("place_order vẫn resolve gói hợp lệ cho lệnh MUA", sent == UPCOM_PKG,
                f"sent={sent}")

    # ── 10. Lệnh BÁN đòn bẩy CHỈ ĐỊNH (CAPIT lever sell) — nhánh explicit vẫn ưu tiên ───
    print("[10] Lệnh BÁN có loan_package_id CHỈ ĐỊNH — nhánh explicit chạy TRƯỚC nhánh side")
    b = make_broker([ACCOUNT_DEFAULT, LEVER_PKG])
    b.place_order("VIX", 100, "sell", price=20000, cash_only=False,
                  loan_package_id=LEVER_PKG)
    sent = b.client.sent[-1][1]
    ok &= check("BÁN + gói chỉ định hợp lệ ⇒ vẫn gửi đúng gói chỉ định (không rơi về None)",
                sent == LEVER_PKG, f"sent={sent}")

    print("\n" + ("ALL PASS" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
