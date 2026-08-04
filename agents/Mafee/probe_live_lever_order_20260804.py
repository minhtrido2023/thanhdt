#!/usr/bin/env python3
"""LỆNH THẬT — job Mafee_20260804_021040. Xác minh DNSE có nhận đúng
`loanPackageId=1840` (RocketX, initialRate=0,5) và ghi đúng nợ margin.

STANDALONE: gọi thẳng DNSEBroker. KHÔNG import bot_execute / Executor /
apply_capit_lever, KHÔNG đọc data/trading_rules.json, KHÔNG sửa
secrets/trading_bot_accounts.json.

Phạm vi cứng: SpaceX 0002023347 · MBB · 100 cp · MUA gói 1840 (override
per-order) · BÁN lại 100 cp cùng phiên.

Chống đặt trùng (§5 coding_guidelines): mọi order_id được ghi ngay vào
STATE_FILE NGAY SAU khi API trả về, atomic. Lệnh mua/bán chỉ đặt được 1 lần
— chạy lại thấy state đã có id thì TỪ CHỐI đặt tiếp.

Dùng:  python3 probe_live_lever_order_20260804.py {ppse|buy|watch|sell|balances}
"""
import json
import os
import sys
import time

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")

from trading_bot.brokers import DNSEBroker  # noqa: E402

ACC = "0002023347"          # SpaceX
SYMBOL = "MBB"
QTY = 100
LEVER_PKG = 1840            # RocketX — override CHỈ cho lệnh mua này
ACCOUNT_DEFAULT_PKG = 1841  # gói mặc định của account, KHÔNG đổi
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "probe_1840_state.json")


def dump(tag, obj):
    print(f"\n===== {tag} =====")
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str), flush=True)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(st):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STATE_FILE)


def broker():
    b = DNSEBroker(account_id=ACC, label="SpaceX_probe1840",
                   loan_package_id=ACCOUNT_DEFAULT_PKG)
    b.connect()
    if not b.client.has_trading_token():
        sys.exit("DỪNG: không có trading-token thật → không thể đặt lệnh. "
                 "KHÔNG suy diễn/giả lập.")
    return b


def show_market(b):
    q = b.get_quote(SYMBOL)
    dump(f"quote {SYMBOL} (RAW)", getattr(q, "raw", None) or q.__dict__)
    print(f"[q] last={q.last} bid={q.bid} ask={q.ask} ref={q.ref}", flush=True)
    return q


def cmd_ppse(b):
    for pkg in (ACCOUNT_DEFAULT_PKG, LEVER_PKG):
        r = b.client.ppse(ACC, SYMBOL, 24200, loan_package_id=pkg)
        dump(f"ppse {SYMBOL} @24200 gói {pkg} (RAW)", r)


def cmd_buy(b):
    st = load_state()
    if st.get("buy_order_id"):
        sys.exit(f"TỪ CHỐI: lệnh mua đã đặt rồi (id={st['buy_order_id']}). "
                 f"Không đặt trùng.")
    q = show_market(b)
    price = q.ask or q.last
    if not price:
        sys.exit("DỪNG: không lấy được giá ask/last.")
    price = int(round(price / 50.0) * 50)          # bước giá HOSE 50đ (<10k:10đ)
    if not (q.floor <= price <= q.ceiling):
        sys.exit(f"DỪNG: giá {price} ngoài biên [{q.floor}, {q.ceiling}].")
    print(f"\n[BUY] REQUEST: account={ACC} symbol={SYMBOL} qty={QTY} side=buy "
          f"order_type=LO price={price} loan_package_id={LEVER_PKG}", flush=True)
    st["buy_attempted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    st["buy_price"] = price
    save_state(st)                                  # ghi TRƯỚC khi gọi API
    oid = b.place_order(SYMBOL, QTY, "buy", price=price, order_type="LO",
                        loan_package_id=LEVER_PKG)
    st["buy_order_id"] = oid
    save_state(st)                                  # ghi NGAY sau khi API trả
    print(f"[BUY] order_id = {oid}", flush=True)
    dump("orders sau khi đặt mua (RAW)", b.client.orders(ACC))


def cmd_watch(b):
    st = load_state()
    oid = st.get("buy_order_id")
    if not oid:
        sys.exit("Chưa có buy_order_id.")
    deadline = time.time() + 600
    while time.time() < deadline:
        u = b.poll_orders().get(str(oid))
        if u is None:
            print(f"[watch] chưa thấy order {oid} trong sổ", flush=True)
        else:
            print(f"[watch] {time.strftime('%H:%M:%S')} status={u.status} "
                  f"filled={u.filled} avg={u.avg_price}", flush=True)
            if u.filled >= QTY:
                dump("order khớp đủ (RAW)", u.raw)
                st["buy_filled"] = u.filled
                st["buy_avg"] = u.avg_price
                save_state(st)
                return
            if getattr(u, "is_dead", False):
                dump("order CHẾT (RAW)", u.raw)
                sys.exit("DỪNG: lệnh bị hủy/từ chối — báo cáo, không đặt lại.")
        time.sleep(15)
    print("[watch] HẾT 10 PHÚT chưa khớp đủ — DỪNG, báo cáo.", flush=True)


def cmd_sell(b):
    st = load_state()
    if not st.get("buy_filled"):
        sys.exit("TỪ CHỐI: lệnh mua chưa khớp đủ → không bán.")
    if st.get("sell_order_id"):
        sys.exit(f"TỪ CHỐI: lệnh bán đã đặt rồi (id={st['sell_order_id']}).")
    pos = b.get_positions().get(SYMBOL, {})
    print(f"[sell] {SYMBOL} tồn kho: {pos}", flush=True)
    if pos.get("sellable", 0) < QTY:
        sys.exit(f"DỪNG: sellable {pos.get('sellable')} < {QTY} (T+2).")
    q = show_market(b)
    price = q.bid or q.last
    price = int(round(price / 50.0) * 50)
    if not (q.floor <= price <= q.ceiling):
        sys.exit(f"DỪNG: giá {price} ngoài biên.")
    print(f"\n[SELL] REQUEST: account={ACC} symbol={SYMBOL} qty={QTY} side=sell "
          f"order_type=LO price={price} loan_package_id=None (gói mặc định "
          f"{ACCOUNT_DEFAULT_PKG} do client gắn)", flush=True)
    st["sell_attempted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    st["sell_price"] = price
    save_state(st)
    oid = b.place_order(SYMBOL, QTY, "sell", price=price, order_type="LO")
    st["sell_order_id"] = oid
    save_state(st)
    print(f"[SELL] order_id = {oid}", flush=True)
    deadline = time.time() + 600
    while time.time() < deadline:
        u = b.poll_orders().get(str(oid))
        if u:
            print(f"[sell-watch] {time.strftime('%H:%M:%S')} status={u.status} "
                  f"filled={u.filled} avg={u.avg_price}", flush=True)
            if u.filled >= QTY:
                dump("lệnh bán khớp đủ (RAW)", u.raw)
                st["sell_filled"] = u.filled
                st["sell_avg"] = u.avg_price
                save_state(st)
                return
            if getattr(u, "is_dead", False):
                dump("lệnh bán CHẾT (RAW)", u.raw)
                sys.exit("DỪNG: lệnh bán bị hủy/từ chối.")
        time.sleep(15)
    print("[sell-watch] HẾT 10 PHÚT chưa khớp đủ — DỪNG, báo cáo.", flush=True)


def cmd_balances(b):
    dump("balances (RAW)", b.client.balances(ACC))
    dump("positions (RAW)", b.client.positions(ACC))
    dump("orders hôm nay (RAW)", b.client.orders(ACC))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"ppse": cmd_ppse, "buy": cmd_buy, "watch": cmd_watch,
          "sell": cmd_sell, "balances": cmd_balances}.get(cmd)
    if not fn:
        sys.exit(__doc__)
    fn(broker())
