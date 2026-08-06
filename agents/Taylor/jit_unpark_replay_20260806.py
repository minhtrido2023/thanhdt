#!/usr/bin/env python3
"""Replay L2 (JIT unpark) trên DỮ LIỆU THẬT — SpaceX/ZaloPay, asof 2026-08-05.

VÌ SAO PHẢI TIÊM LỆNH: trong cửa sổ replay được (bootstrap ngày 0 = 2026-08-04 ⇒ sổ lô không lùi
xa hơn), CẢ HAI account đều KHÔNG có lệnh mua BAL/LAG nào trong plan thật (plan 08-04/05/06 đều 0
lệnh) ⇒ không tồn tại case trigger thật để replay. Nên ở đây: **mọi thứ khác đều thật** — sổ lô
theo book (`park_holdings`, đối soát broker OK), vị thế + giá + `availableCash` từ bản ghi DNSE
thật của phiên, ADV thật (`_adv_for_gate` → bq_cache), trần rổ thật (`etf_day_cap_live`), share
thật (`live_share`) — CHỈ lệnh mua LAG là tiêm vào để kích hoạt đường JIT.

Đây KHÔNG phải bằng chứng lợi nhuận; nó trả lời đúng một câu: trên sổ thật hôm nay, L2 đề xuất
bán những gì, có tôn trọng mọi ranh giới cứng không.

    python3 mike/agents/Taylor/jit_unpark_replay_20260806.py
"""
import json
import os
import sys

BIN = "/home/trido/thanhdt/WorkingClaude/mike/bin"
sys.path.insert(0, BIN)
from compute_jit_unpark import compute_jit_unpark, build_pool         # noqa: E402
from compute_park_trim import live_share                              # noqa: E402
from park_holdings import park_holdings                               # noqa: E402
from trading_bot.plan import _adv_for_gate                            # noqa: E402
from trading_bot.vn_market import LOT                                 # noqa: E402

ASOF = "2026-08-05"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def cheapest_lot_vnd(h):
    """Giá trị 1 lô RẺ NHẤT trong rổ PARK ĐỦ ĐIỀU KIỆN BÁN của phiên — cận trên chi phí của (C).

    Dùng đúng `build_pool()` của module (không tự lọc lại) để cận này là cận THẬT: mã bị chặn
    (excluded / UNVERIFIED / ADV cũ / hết trần) không được tính, dù nó có rẻ hơn."""
    share, _lbl, err = live_share()
    if err or not share:
        return 0.0
    pool, _bl, perr = build_pool(h, ASOF, share, _adv_for_gate)
    if perr or not pool:
        return 0.0
    return LOT * min(d["px"] for d in pool.values())


def replay(account, buy_vnd, ticker="FPT", px=100_000):
    h = park_holdings(account, ASOF)
    qty = int(buy_vnd // px // 100 * 100)
    order = {"id": f"BUY-{ticker}-REPLAY", "ticker": ticker, "side": "buy", "qty": qty,
             "ref_price": px, "book": "LAG", "play_type": "LAG_HI", "priority": 10}
    r = compute_jit_unpark(account, asof=ASOF, orders=[order], holdings=h)

    print(f"\n=== {account} asof={ASOF} — lệnh LAG tiêm {qty:,}cp × {px:,}đ = "
          f"{qty*px/1e6:,.1f}tr ===")
    print(f"  sổ THẬT: PARK {h['park_mv_vnd']/1e6:,.2f}tr / {len(set(l['ticker'] for l in h['park_lots']))} mã"
          f" | cash {(h['cash_available_vnd'] or 0)/1e6:,.2f}tr"
          f" | đối soát {'OK' if h['reconcile']['ok'] else 'LỆCH'}"
          f" | excluded={h['excluded_tickers']} unverified={h['unverified_tickers']}")
    print(f"  decision={r['decision']}  trần TỔNG/phiên={r.get('etf_day_cap_vnd', 0)/1e9:,.2f} tỷ"
          f"  share={r.get('adv_share')}")
    m = r["buy_amendments"][0] if r["buy_amendments"] else {}
    print(f"  lệnh mua: {m.get('status')} {m.get('qty_plan', 0):,}cp → {m.get('qty_final', 0):,}cp"
          f" | needed {m.get('needed_vnd', 0)/1e6:,.2f}tr | bán PARK "
          f"{m.get('jit_sell_vnd', 0)/1e6:,.2f}tr (ròng {m.get('jit_proceeds_net_vnd', 0)/1e6:,.2f}tr)")
    for o in r["orders"]:
        print(f"    BÁN {o['ticker']:<5} {o['qty']:>6,}cp @ {o['ref_price']:>9,.0f} = "
              f"{o['value_vnd']/1e6:>7,.2f}tr  w={o['weight_in_park']:.1%}  "
              f"trần_ADV_còn={o['adv_cap_remaining_vnd']/1e6:,.0f}tr  sellable={o['sellable']:,}")
    for b in r["blocked"]:
        print(f"    – bỏ qua {b['ticker']}: {b['reason']}")
    for n in r["notes"]:
        print(f"    ⚠ {n}")

    # ── Bất biến kiểm trên DỮ LIỆU THẬT ─────────────────────────────────────
    books = {}
    for l in h["lots"]:
        books.setdefault(l["book"], set()).add(l["ticker"])
    sold = set(r["sells_by_ticker"])
    non_park = set().union(*[v for k, v in books.items() if k != "PARK"]) if books else set()
    inv = [
        ("chỉ bán mã thuộc sổ PARK", sold <= books.get("PARK", set())),
        ("KHÔNG đụng CAPIT/LAG/BAL/DISCRETIONARY", not (sold & (non_park - books.get("PARK", set())))),
        ("KHÔNG đụng excluded_tickers", not (sold & set(h["excluded_tickers"]))),
        ("KHÔNG đụng ticker UNVERIFIED", not (sold & set(h["unverified_tickers"]))),
        ("không bán quá số đang giữ", all(
            q <= sum(l["qty"] for l in h["park_lots"] if l["ticker"] == tk)
            for tk, q in r["sells_by_ticker"].items())),
        ("không bán quá sellable (T+2)", all(
            q <= h["broker_positions"].get(tk, {}).get("sellable", 0)
            for tk, q in r["sells_by_ticker"].items())),
        ("Σ bán ≤ trần TỔNG/phiên", r.get("jit_sell_total_vnd", 0)
         <= r.get("etf_day_cap_vnd", 0) + 1e-6),
        # ⚠️ Bất biến ĐÃ ĐỔI theo phương án (C), user John duyệt 2026-08-06. CŨ: `Σ bán ≤ needed`
        # (làm tròn XUỐNG, không bao giờ bán thừa) — nhưng đo được là nó làm MẤT TRỌN lệnh mua vì
        # hụt vài trăm nghìn. MỚI: được bán thừa, nhưng có CẬN TRÊN CHẶT = đúng 1 lô rẻ nhất của
        # rổ PARK bán được. Không phải "bán tuỳ ý" — cận trên này chính là thứ phải giữ.
        ("Σ bán < needed + 1 lô rẻ nhất (bán thừa CÓ cận trên chặt)",
         r.get("jit_sell_total_vnd", 0) < m.get("needed_vnd", 0) + cheapest_lot_vnd(h) + 1e-6),
        ("mọi qty là bội số lô chẵn", all(o["qty"] % 100 == 0 for o in r["orders"])),
        ("không bán sạch mã nào (giữ cấu trúc rổ)", all(
            q < sum(l["qty"] for l in h["park_lots"] if l["ticker"] == tk)
            for tk, q in r["sells_by_ticker"].items())),
    ]
    print("  — bất biến trên dữ liệu thật:")
    ok_all = True
    for name, ok in inv:
        ok_all &= ok
        print(f"    {'✅' if ok else '❌'} {name}")
    path = os.path.join(OUT_DIR, f"jit_unpark_replay_{account}_{ASOF}.json")
    json.dump(r, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(f"  → {os.path.basename(path)}")
    return ok_all


if __name__ == "__main__":
    ok = True
    # SpaceX: PARK ~644tr, cash ~4,8tr ⇒ lệnh LAG 80tr chắc chắn kích hoạt JIT.
    ok &= replay("SpaceX", 80_000_000)
    # ZaloPay: cash-only, có DGC excluded — chính là ca kiểm ranh giới excluded.
    ok &= replay("ZaloPay", 80_000_000)
    print(f"\n{'✅' if ok else '❌'} REPLAY: mọi bất biến "
          f"{'GIỮ' if ok else 'BỊ VI PHẠM'} trên dữ liệu thật")
    sys.exit(0 if ok else 1)
