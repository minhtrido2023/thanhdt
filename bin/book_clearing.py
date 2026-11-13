#!/usr/bin/env python3
"""Lõi THUẦN của GĐ3 clearing PARK→LAG — sửa plan + kiểm ràng buộc, KHÔNG I/O broker.

Thiết kế: `kb/projects/book-clearing-plan-20261029.md`. Ba writer dùng chung module này để cùng một
định nghĩa "plan đã clearing" (một nguồn, không chép logic):
  · `clear_books.py --apply`   — ghi `plan["book_transfers"]` + giảm qty lệnh (cuối chuỗi plan 20:45)
  · `apply_book_transfers.py`  — trước `bot_execute`: ghi journal BOOK_TRANSFER hoặc PAUSE mã đó
  · `merge_park_orders.py`     — dựng lại vùng PARK ⇒ HOÀN TÁC clearing trước (đầu vào đã đổi)

HỢP ĐỒNG DỮ LIỆU — mỗi phần tử `plan["book_transfers"]`:
  id            XFER-<acct>-<plan_date>-<TK>-PARK-LAG (idempotent, = parent_id dòng journal)
  account, plan_date, ticker, from_book="PARK", to_book, qty (=m, >0), ref_price (giá lệnh MUA)
  buy_orders / sell_orders  [{id, orig_qty, qty_after}]  — lệnh đã bị giảm (qty_after=0 ⇒ đã gỡ
                khỏi orders[], bản gốc nằm ở `removed_orders`)
  removed_orders  [order dict gốc]  — để hoàn tác/đối chiếu
  status        PLANNED | APPLIED | PAUSED   (apply_book_transfers cập nhật)
Mỗi lệnh bị giảm mang `book_clearing = {"transfer_id", "orig_qty"}` ⇒ hoàn tác không cần đoán.

PHẠM VI ĐÍCH = CHỈ LAG (TO_BOOKS). KHÔNG chuyển PARK→BAL: stop-loss của BAL đo trên `avg_cost` broker
cấp MÃ (không cấp sổ), mà chuyển nhãn không dịch avg_cost (broker không biết sổ) ⇒ lô PARK đổi nhãn
sang BAL sẽ bị stop-loss BAL đo trên giá vốn sai cơ sở. LAG không áp stop-loss nên an toàn. Cặp PARK→BAL
trong plan được bỏ qua và ghi vào `blocked` với lý do `bal_stoploss_basis`.

Bất biến bảo toàn: Σ thay đổi vị thế mỗi mã KHÔNG đổi (mua −m, bán PARK −m). Bội lô: lệnh còn lại
giữ bội 100, phần lẻ của lệnh bán gốc (full-exit lẻ) được giữ nguyên (đã hợp lệ trước clearing).
"""
import copy
import dataclasses
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
LOT = 100
FROM_BOOK = "PARK"
TO_BOOKS = ("LAG",)
# Sổ đích BỊ LOẠI có chủ đích (user chọn phương án A, 05/11): cặp PARK→BAL luôn bị bỏ qua, lý do dưới.
SKIPPED_TO_BOOKS = {"BAL": "bal_stoploss_basis"}
KNOB_PATH = os.path.join(os.path.dirname(_HERE), "config", "book_clearing.json")
ST_PLANNED, ST_APPLIED, ST_PAUSED = "PLANNED", "APPLIED", "PAUSED"


def knob_enabled(path=KNOB_PATH):
    """(bật?, lý do). CHỈ `apply_to_plan is True` (bool) mới bật — thiếu file/JSON hỏng/chuỗi
    "true"/1 ⇒ TẮT (fail-closed về SHADOW)."""
    try:
        with open(path, encoding="utf-8") as f:
            v = json.load(f).get("apply_to_plan")
    except FileNotFoundError:
        return False, f"knob {path} không tồn tại ⇒ TẮT"
    except Exception as e:   # JSON hỏng / không phải object
        return False, f"knob {path} không đọc được ({type(e).__name__}: {e}) ⇒ TẮT"
    if v is True:
        return True, "apply_to_plan=true"
    return False, f"apply_to_plan={v!r} (chỉ bool true mới bật) ⇒ TẮT"


def _qty(o):
    v = o.get("qty")
    if isinstance(v, bool):
        raise ValueError(f"lệnh {o.get('id')} qty bool")
    q = float(v)
    if not math.isfinite(q) or q != int(q) or q < 0:
        raise ValueError(f"lệnh {o.get('id')} qty lạ {v!r}")
    return int(q)


def lot_feasible(m_raw, buy_qty, sell_qty):
    """m lớn nhất ≤ m_raw sao cho: lệnh MUA còn lại (buy − m) là bội lô 100, và lệnh BÁN còn lại
    (sell − m) hoặc bội 100, hoặc giữ đúng phần lẻ của lệnh bán gốc (full-exit lẻ đã hợp lệ).
    Không tồn tại ⇒ 0."""
    odd = sell_qty % LOT
    for m in range(int(m_raw), 0, -1):
        rest = sell_qty - m
        if (buy_qty - m) % LOT == 0 and (rest % LOT == 0 or rest % LOT == odd):
            return m
    return 0


def revert_clearing(plan):
    """Trả (plan MỚI, danh sách id đã hoàn tác). Khôi phục qty gốc cho mọi lệnh mang
    `book_clearing`, trả lại lệnh đã bị gỡ (qty_after=0), xoá `plan["book_transfers"]`.
    Transfer đã APPLIED (journal đã ghi) ⇒ KHÔNG được hoàn tác ⇒ ValueError (caller fail-closed)."""
    p = copy.deepcopy(plan)
    xs = p.get("book_transfers") or []
    applied = [x.get("id") for x in xs if isinstance(x, dict) and x.get("status") == ST_APPLIED]
    if applied:
        raise ValueError(f"plan có book_transfers đã APPLIED {applied} — journal đã ghi, không hoàn "
                         "tác được bằng sửa plan")
    orders = p.get("orders") or []
    for o in orders:
        bc = o.pop("book_clearing", None) if isinstance(o, dict) else None
        if isinstance(bc, dict) and bc.get("orig_qty") is not None:
            o["qty"] = int(bc["orig_qty"])
    have = {o.get("id") for o in orders if isinstance(o, dict)}
    for x in xs:
        for ro in (x.get("removed_orders") or []) if isinstance(x, dict) else []:
            ro = copy.deepcopy(ro)
            bc = ro.pop("book_clearing", None)   # lệnh bị giảm ở transfer trước rồi mới bị gỡ
            if isinstance(bc, dict) and bc.get("orig_qty") is not None:
                ro["qty"] = int(bc["orig_qty"])
            if ro.get("id") not in have:
                orders.append(ro)
                have.add(ro.get("id"))
    # PAUSED chỉ xảy ra sáng ngày thực thi (plan đã duyệt) và đã tự KHÔI PHỤC lệnh gốc (pause_transfer);
    # lệnh còn marker `book_clearing` được đưa về qty gốc ở trên, removed_orders không bị thêm đôi (have).
    p["orders"] = orders
    p.pop("book_transfers", None)
    return p, [x.get("id") for x in xs if isinstance(x, dict)]


def _reduce(orders_of, m, keep_odd):
    """Giảm tổng `m` trên danh sách lệnh (theo thứ tự ĐẢO — lệnh sau bị giảm trước), chỉ lấy phần
    bội lô nếu keep_odd. Trả [(order, orig, after)] hoặc None nếu không đủ."""
    out, rem = [], m
    for o in reversed(orders_of):
        if rem <= 0:
            break
        q = _qty(o)
        avail = q - (q % LOT) if keep_odd else q
        take = min(avail, rem)
        if take <= 0:
            continue
        out.append((o, q, q - take))
        rem -= take
    return out if rem == 0 else None


def apply_opportunities(plan, opps, account, plan_date, created_at):
    """Ghi các cơ hội (`clear_books.analyze()["opportunities"]`) vào plan. Plan đầu vào PHẢI chưa
    clearing (gọi `revert_clearing` trước). Trả (plan MỚI, transfers, skipped[{ticker, reason}])."""
    p = copy.deepcopy(plan)
    if p.get("book_transfers"):
        raise ValueError("plan đã có book_transfers — gọi revert_clearing trước")
    by_id = {o.get("id"): o for o in p.get("orders") or []}
    transfers, skipped = [], []
    for op in opps:
        m = int(op["transfer_qty"])
        if m <= 0:
            continue
        if op.get("to_book") not in TO_BOOKS:   # phòng thủ lớp 2: đích ngoài phạm vi (BAL...) không bao giờ ghi
            skipped.append({"ticker": op["ticker"],
                            "reason": SKIPPED_TO_BOOKS.get(op.get("to_book"), "to_book_out_of_scope")})
            continue
        buys = [by_id.get(i) for i in op["buy_order_ids"]]
        sells = [by_id.get(i) for i in op["park_sell_order_ids"]]
        if any(o is None for o in buys + sells) or len(set(op["buy_order_ids"])) != len(buys):
            skipped.append({"ticker": op["ticker"], "reason": "id lệnh không duy nhất/không tìm thấy"})
            continue
        rb = _reduce(buys, m, keep_odd=False)
        rs = _reduce(sells, m, keep_odd=True)
        if rb is None or rs is None:
            skipped.append({"ticker": op["ticker"], "reason": f"không giảm được {m}cp giữ bội lô"})
            continue
        xid = f"XFER-{account}-{plan_date}-{op['ticker']}-{FROM_BOOK}-{op['to_book']}"
        rec = {"id": xid, "account": account, "plan_date": plan_date, "ticker": op["ticker"],
               "from_book": FROM_BOOK, "to_book": op["to_book"], "qty": m,
               "ref_price": float(op["ref_price_buy"]),
               "play_type": str(buys[0].get("play_type") or ""),
               "buy_orders": [], "sell_orders": [], "removed_orders": [],
               "saving_est_vnd": op.get("saving_est_vnd", 0), "created_at": created_at,
               "created_by": "clear_books", "status": ST_PLANNED}
        for side, red in (("buy_orders", rb), ("sell_orders", rs)):
            for o, orig, after in red:
                rec[side].append({"id": o["id"], "orig_qty": orig, "qty_after": after})
                if after == 0:
                    ro = copy.deepcopy(o)
                    rec["removed_orders"].append(ro)
                    o["_drop"] = True
                else:
                    o["qty"] = after
                    # giữ qty GỐC NHẤT khi một lệnh bị nhiều transfer giảm (2 sổ đích cùng mã)
                    o.setdefault("book_clearing", {"transfer_id": xid, "orig_qty": orig})
        transfers.append(rec)
    p["orders"] = [o for o in p.get("orders") or [] if not o.pop("_drop", False)]
    if transfers:
        p["book_transfers"] = transfers
    return p, transfers, skipped


def final_qty_map(plan):
    """{order_id: qty CUỐI kỳ vọng} trên mọi transfer CHƯA PAUSE. Một lệnh có thể bị nhiều transfer
    giảm nối tiếp (2 sổ đích cùng mã chung lệnh bán PARK) ⇒ qty cuối = min(qty_after)."""
    out = {}
    for x in plan.get("book_transfers") or []:
        if not isinstance(x, dict) or x.get("status") == ST_PAUSED:
            continue
        for side in ("buy_orders", "sell_orders"):
            for r in x.get(side) or []:
                q = int(r.get("qty_after"))
                out[r.get("id")] = min(q, out.get(r.get("id"), q))
    return out


def binding_problems(plan, x):
    """Lệnh liên kết của transfer `x` trong plan HIỆN TẠI có đúng qty cuối kỳ vọng không? Trả list
    lỗi (rỗng = khớp). Đây là chỗ bắt mọi writer sửa plan SAU clearing (DollarBill sửa tay, re-run
    auto_exit…) — lệch ⇒ không biết Σ đã còn bảo toàn ⇒ caller PAUSE, không đoán."""
    probs = []
    by_id = {}
    for o in plan.get("orders") or []:
        by_id.setdefault(o.get("id"), []).append(o)
    final = final_qty_map(plan)
    for side in ("buy_orders", "sell_orders"):
        for ref in x.get(side) or []:
            got = by_id.get(ref.get("id"), [])
            want = final.get(ref.get("id"), int(ref.get("qty_after")))
            if want == 0:
                if got:
                    probs.append(f"{ref['id']} lẽ ra đã gỡ (qty cuối=0) nhưng vẫn còn trong orders")
                continue
            if len(got) != 1:
                probs.append(f"{ref['id']} xuất hiện {len(got)} lần (cần đúng 1)")
                continue
            try:
                q = _qty(got[0])
            except ValueError as e:
                probs.append(str(e))
                continue
            if q != want:
                probs.append(f"{ref['id']} qty={q} ≠ qty cuối kỳ vọng={want}")
            if str(got[0].get("ticker")) != str(x.get("ticker")):
                probs.append(f"{ref['id']} ticker={got[0].get('ticker')} ≠ {x.get('ticker')}")
    # bảo toàn: Σ giảm mua = Σ giảm bán = qty
    for side in ("buy_orders", "sell_orders"):
        d = sum(int(r["orig_qty"]) - int(r["qty_after"]) for r in x.get(side) or [])
        if d != int(x.get("qty") or -1):
            probs.append(f"Σ giảm {side}={d} ≠ qty chuyển {x.get('qty')}")
    return probs


def _orig_qty(o, ref):
    """qty GỐC (trước mọi clearing) của lệnh `o`: marker `book_clearing.orig_qty` nếu có (giữ qty gốc
    NHẤT khi nhiều transfer giảm nối tiếp), không thì `orig_qty` của ref."""
    bc = o.get("book_clearing") if isinstance(o, dict) else None
    if isinstance(bc, dict) and bc.get("orig_qty") is not None:
        return int(bc["orig_qty"])
    return int(ref["orig_qty"])


def approval_problem(plan):
    """Plan yêu cầu duyệt (requires_user_approval truthy) mà `approved_by` rỗng ⇒ lý do chặn, BẤT KỂ
    số lệnh. Khác `trading_bot.plan.approval_block_reason` ở đúng 1 điểm: nó trả None khi orders=[]
    (HOLD), nhưng clearing có thể làm orders rỗng (chỉ có cặp PARK bán + LAG mua) trong khi
    book_transfers vẫn đòi ghi journal ⇒ chữ ký duyệt phải có. Cùng chuẩn hoá chuỗi như bản gốc."""
    req = plan.get("requires_user_approval")
    if isinstance(req, str):
        req = req.strip().lower() not in ("", "false", "no", "0", "none")
    if not req:
        return None
    ap = plan.get("approved_by") or plan.get("approved_by_user")   # load_plan map approved_by_user→approved_by
    if isinstance(ap, str):
        ap = ap.strip()
        if ap.lower() in ("none", "null", "nil", "nan"):
            ap = ""
    if ap:
        return None
    return "plan requires_user_approval nhưng approved_by rỗng — chưa duyệt thì không ghi BOOK_TRANSFER"


def pause_transfer(plan, xid, reason, now_iso):
    """Plan MỚI: transfer `xid` → PAUSED và KHÔI PHỤC lệnh GỐC của nó (fail-safe = đúng hành vi
    production khi không có clearing): lệnh đã bị giảm trả về qty gốc, lệnh đã bị gỡ (qty_after=0,
    nằm ở `removed_orders`) trả lại vào orders[]. Nếu lệnh còn bị transfer KHÁC (chưa PAUSE) giảm
    chung thì chỉ trả phần của transfer này (qty gốc − Σ giảm của các transfer còn lại). Tính từ qty
    GỐC chứ không cộng delta lên qty hiện tại ⇒ plan bị sửa tay sau clearing vẫn về đúng gốc."""
    p = copy.deepcopy(plan)
    xs = [x for x in p.get("book_transfers") or [] if isinstance(x, dict)]
    for x in xs:
        if x.get("id") != xid:
            continue
        orders = p.setdefault("orders", [])
        by_id = {}
        for o in orders:
            by_id.setdefault(o.get("id"), o)
        # bản gốc lệnh đã bị gỡ có thể nằm ở transfer KHÁC (lệnh bán PARK bị 2 sổ đích giảm nối tiếp,
        # transfer sau mới gỡ hẳn) ⇒ tìm trên mọi transfer, ưu tiên transfer này
        gone = {}
        for y in [x] + [y for y in xs if y is not x]:
            for ro in y.get("removed_orders") or []:
                gone.setdefault(ro.get("id"), ro)
        restored = []
        for side in ("buy_orders", "sell_orders"):
            for ref in x.get(side) or []:
                oid = ref.get("id")
                o = by_id.get(oid)
                if o is None:
                    ro = gone.get(oid)
                    if ro is None:
                        raise ValueError(f"không khôi phục được {oid}: không còn trong orders và không có removed_orders")
                    o = copy.deepcopy(ro)
                    orders.append(o)
                    by_id[oid] = o
                others = sum(int(r["orig_qty"]) - int(r["qty_after"])
                             for y in xs if y is not x and y.get("status") != ST_PAUSED
                             for sd in ("buy_orders", "sell_orders") for r in y.get(sd) or []
                             if r.get("id") == oid)
                o["qty"] = _orig_qty(o, ref) - others
                restored.append(oid)
        x["status"] = ST_PAUSED
        x["paused_at"] = now_iso
        x["pause_reason"] = reason
        x["restored_orders"] = restored
    return p


def mark(plan, xid, status, **extra):
    p = copy.deepcopy(plan)
    for x in p.get("book_transfers") or []:
        if x.get("id") == xid:
            x["status"] = status
            x.update(extra)
    return p


def sell_cap_problems(plan):
    """Σ bán mỗi mã + Σ chuyển ra khỏi PARK (transfer CHƯA áp) ≤ min(sellable khai trong lệnh).
    Dùng cho clear_books (hậu kiểm) — preflight tự có bản riêng trong khối bash."""
    cap, sold = {}, {}

    def _cap_from(o):
        tk = o.get("ticker")
        for s in (o.get("sellable"), (o.get("merged_from") or {}).get("sellable_at_calc")):
            if s is not None:
                cap[tk] = min(cap.get(tk, 10 ** 12), int(s))

    for o in plan.get("orders") or []:
        if str(o.get("side") or "").lower() != "sell":
            continue
        sold[o.get("ticker")] = sold.get(o.get("ticker"), 0) + _qty(o)
        _cap_from(o)
    for x in plan.get("book_transfers") or []:
        if x.get("status") in (ST_PLANNED, None):
            sold[x["ticker"]] = sold.get(x["ticker"], 0) + int(x["qty"])
        # trần cũng lấy từ lệnh bán đã bị clearing GỠ (chỉ nó mang `sellable`) — như preflight
        for ro in x.get("removed_orders") or []:
            if isinstance(ro, dict) and str(ro.get("side") or "").lower() == "sell":
                _cap_from(ro)
    return [f"{tk}: bán+chuyển {q} > sellable {cap[tk]}" for tk, q in sorted(sold.items())
            if tk in cap and q > cap[tk]]


# ─────────────────────────────────────────── cổng book ĐÍCH (dùng lại NGUYÊN hàm của bot)

# Tên hàm cổng của bot_execute (trading_bot.plan) áp cho lệnh MUA, theo thứ tự bot gọi. KHÔNG có
# cap_lag_orders (xem docstring). `book_clearing_g3_selfcheck` có AST parity test: tập này phải
# BẰNG tập `filter_*` mà bot_execute.py gọi — bot thêm cổng mới mà quên ở đây ⇒ selfcheck đỏ.
GATE_STEPS = ("filter_excluded_tickers", "filter_signal_holds", "filter_dd_flag_orders",
              "filter_lag_dd_zone_orders", "filter_lag_rating_orders", "filter_lag_governance_orders")


CORP_ACTION_TIMEOUT_S = 30   # trần thời gian đọc BQ ở đường apply (đang giữ flock) — quá ⇒ chặn chuyển, fail-closed


def corp_action_problem(ticker, asof, plan_date, events_fn=None, timeout_s=None):
    """Chuyển nhãn một mã có sự kiện giá (ex-date cổ tức/phát hành) trong (asof, plan_date] ⇒ khung
    giá/KL của lệnh mua (lập lúc asof, cum-quyền) và lô sổ (ghi theo ngày thực thi, ex-quyền) lệch
    nhau ⇒ chặn (chưa có cách chuyển nhãn đúng qua ex-date). Lỗi đọc nguồn ⇒ CHẶN (fail-closed).
    `events_fn(tickers, since, until)`; mặc định corp_action_lib.pricing_events (gồm `announced`).
    Đọc nguồn chạy trong thread daemon, quá `timeout_s` (mặc định CORP_ACTION_TIMEOUT_S=30s) ⇒ CHẶN
    (PAUSE/khôi phục lệnh gốc ở caller) — không treo đường apply khi đang giữ flock.
    Trả lý do hoặc None."""
    if not asof:
        return "không biết asof (plan thiếu park_trim_proposal.asof/signal_date) ⇒ không kiểm được corp-action"
    try:
        if events_fn is None:
            wc = os.path.dirname(os.path.dirname(_HERE))
            if wc not in sys.path:
                sys.path.insert(0, wc)
            import corp_action_lib as _cal
            events_fn = _cal.pricing_events
        import threading
        box = {}

        def _call():
            try:
                box["ev"] = list(events_fn([ticker], since=str(asof), until=str(plan_date)) or [])
            except BaseException as e:   # noqa: BLE001 — chuyển lỗi về thread gọi
                box["err"] = e
        lim = CORP_ACTION_TIMEOUT_S if timeout_s is None else timeout_s
        th = threading.Thread(target=_call, daemon=True)
        th.start()
        th.join(lim)
        if th.is_alive():
            return f"đọc corp-action {ticker} quá {lim}s (BQ chậm) ⇒ chặn chuyển (fail-closed)"
        if "err" in box:
            raise box["err"]
        ev = box["ev"]
    except Exception as e:
        return f"không đọc được corp-action {ticker} ({type(e).__name__}: {e}) ⇒ chặn chuyển (fail-closed)"
    ev = [e for e in ev if isinstance(e, dict) and e.get("ticker", ticker) == ticker]
    if ev:
        e0 = ev[0]
        return (f"{ticker} có sự kiện giá {e0.get('event_code')} ex-date {e0.get('exright_date')} trong "
                f"({asof}, {plan_date}] ⇒ không chuyển nhãn qua ex-date")
    return None


def plan_asof(plan):
    return (plan.get("park_trim_proposal") or {}).get("asof") or plan.get("signal_date")


def target_book_gates(plan, x, excluded):
    """Lệnh MUA đích (qty GỐC, trước khi giảm) có qua đủ cổng của book đích không — đúng các hàm
    bot_execute chạy (đúng thứ tự GATE_STEPS): filter_excluded_tickers, filter_signal_holds,
    filter_dd_flag_orders, filter_lag_dd_zone_orders, filter_lag_rating_orders,
    filter_lag_governance_orders. KHÔNG gọi cap_lag_orders (trần %ADV đo TÁC ĐỘNG THỊ TRƯỜNG; phần
    chuyển nhãn không chạm thị trường — cùng lý lẽ docstring net_offsetting_orders).
    Khác bot: FAIL_OPEN của nguồn ⇒ CHẶN chuyển (cơ chế mới, không kế thừa fail-open).
    Trả (ok, lý do)."""
    wc = os.path.dirname(os.path.dirname(_HERE))
    if wc not in sys.path:
        sys.path.insert(0, wc)
    try:
        from trading_bot import plan as TP
    except Exception as e:
        return False, f"không import được trading_bot.plan ({type(e).__name__}: {e})"
    known = {f.name for f in dataclasses.fields(TP.PlannedOrder)}
    src = {o.get("id"): o for o in (plan.get("orders") or []) + (x.get("removed_orders") or [])}
    pos = []
    for r in x.get("buy_orders") or []:
        o = dict(src.get(r["id"]) or {})
        if not o:
            return False, f"không thấy lệnh mua {r['id']}"
        o.pop("book_clearing", None)
        o["qty"] = int(r["orig_qty"])
        try:
            pos.append(TP.PlannedOrder(**{k: v for k, v in o.items() if k in known}))
        except Exception as e:
            return False, f"lệnh mua {r['id']} không dựng được PlannedOrder ({type(e).__name__}: {e})"
    kp = {f.name for f in dataclasses.fields(TP.TradePlan)}
    base = {k: plan.get(k) for k in ("plan_date", "signal_date", "strategy", "strategy_version",
                                     "state", "state_name", "nav_basis")}
    base.update({k: v for k, v in plan.items() if k in kp and k not in ("orders",) and v is not None})
    try:
        tp = TP.TradePlan(**dict(base, orders=pos))
    except Exception as e:
        return False, f"không dựng được TradePlan ({type(e).__name__}: {e})"
    want = {o.id for o in pos}
    steps = [(name, (lambda t: TP.filter_excluded_tickers(t, sorted(excluded)))
              if name == "filter_excluded_tickers" else getattr(TP, name))
             for name in GATE_STEPS]
    for name, fn in steps:
        try:
            tp, acts = fn(tp)
        except Exception as e:
            return False, f"cổng {name} lỗi ({type(e).__name__}: {e})"
        for a in acts or []:
            act = a.get("action") if isinstance(a, dict) else None
            if act and str(act).startswith("FAIL_OPEN"):
                return False, f"cổng {name} FAIL_OPEN (nguồn hỏng) ⇒ không chuyển: {a.get('reason')}"
        left = {o.id for o in tp.orders}
        if want - left:
            why = "; ".join(str((a.get("reason") or a.get("hold") if isinstance(a, dict) else a))[:120]
                            for a in acts or [])
            return False, f"cổng {name} loại lệnh mua {sorted(want - left)}: {why}"
    return True, "qua " + "/".join(n.replace("filter_", "") for n in GATE_STEPS)
