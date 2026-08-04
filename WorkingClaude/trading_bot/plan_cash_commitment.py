"""HEADROOM tiền còn lại của một plan — để LUỒNG SINH LỆNH THỨ HAI biết luồng thứ nhất
đã dự chi bao nhiêu TRƯỚC KHI tự thêm lệnh vào cùng một `orders[]`.

⚠️ CHƯA WIRE VÀO PRODUCTION. `mike/bin/discretionary_accumulation_inject.py` chưa gọi module
này; patch đề xuất ở `mike/agents/Taylor/research/discretionary_inject_cash_gate.patch`,
chờ Mike review + quant-skeptic duyệt.

VẤN ĐỀ (A2 — race condition tiền mặt giữa hai bộ sinh lệnh)
────────────────────────────────────────────────────────────
Cùng một file `data/trade_plans/plan_<account>_<date>.json`, cùng một `orders[]`, cùng một
túi tiền — nhưng có HAI bộ ghi vào, ở hai thời điểm khác nhau, không bộ nào cộng phần của
bộ kia:
  1. DollarBill (phiên LLM, dispatch ~19:0x) ghi lệnh V2.4 (BAL/LAG/CAPIT).
  2. `discretionary_accumulation_inject.py` (cron 20:30 ICT T2-T6) chèn lệnh gom
     `book=DISCRETIONARY_SPECIAL`. `grep -n "cash\|available\|ppse"` trên file đó →
     **0 kết quả**: bộ chèn size lệnh THUẦN theo `min(remaining, cap%ADV)`, KHÔNG hề đọc
     tiền. `compute_session_order()` (trading_bot/discretionary_accumulation.py:52) cũng
     không nhận tham số tiền nào.
Sự cố thật 2026-07-24 (SpaceX): V2.4 45,9M + tranche TV1 3,98M = 49,9M > cash 49,1M —
thiếu ~0,78M. Lần đó thoát vì DollarBill được nhắc thủ công và tự sửa (REV2: trừ TV1
3,98M trước rồi mới size PVT — xem `cash_planning.tv1_reserve_first` trong
`plan_SpaceX_2026-07-24.json`), tức bằng VĂN XUÔI + trí nhớ phiên LLM, không phải cơ chế.

CHIỀU NÀO CHẠY TRƯỚC? — trả lời dứt điểm, không phỏng đoán
──────────────────────────────────────────────────────────
Injector KHÔNG THỂ chạy trước: nó `return 0` no-op khi chưa có file plan
(`discretionary_accumulation_inject.py:141-144`). Nên trật tự luôn là **plan trước,
injector sau** ⇒ chỉ cần MỘT chiều kiểm tra: injector phải trừ phần plan đã dự chi.

Nhưng có một chiều NGƯỢC thật, khác với "injector chạy trước": **plan bị GHI LẠI SAU khi
injector đã chèn** (re-plan/sửa plan lúc 21:3x, 22:1x — đã xảy ra, xem cron
`send_plan_report --second-chance` 23:00 sinh ra chính vì ca sửa plan 22:17). Khi đó:
  • lệnh đã chèn BIẾN MẤT (file bị ghi đè toàn bộ),
  • dedup-2 của injector (`ledger` đã có bản ghi cho `plan_date`) khiến lần chạy sau
    **TỪ CHỐI chèn lại** ⇒ tranche bị bỏ IM LẶNG, không ai báo.
Xử lý ở đây: `replan_dropped_injection()` phát hiện đúng trạng thái đó (ledger có, order
không có) để caller chèn LẠI thay vì skip. An toàn với §5 (idempotency): `filled_qty` luôn
đọc lại từ broker chứ không từ ledger, và order id là tất định
(`BUY-<TICKER>-DISC-<plan_date>`) nên dedup-1 vẫn chặn trùng trong cùng một plan.

VẾ PHẢI — SỨC MUA CÒN LẠI, dùng lại nguyên mô hình của A1 (không nhân bản logic)
────────────────────────────────────────────────────────────────────────────────
`plan_funding_gate.check_plan_funding()` đã giải đúng bài toán "gói vay nào, đo pp0Buy
theo nhóm nào" (kể cả bẫy TV1/UPCOM gói 1122 vs 1841 làm pp0Buy=0 giả). Module này KHÔNG
tính lại: nó gọi thẳng hàm đó lấy `utilization` U của phần plan HIỆN CÓ, rồi

    headroom = (1 − U) × pp0Buy(gói vay của chính lệnh sắp chèn)

Cùng mô hình tiêu thụ tuyến tính mà A1 đã dùng và đã qua quant-skeptic.

KHI KHÔNG ĐO ĐƯỢC pp0Buy → CẬN TIỀN MẶT, và fail-safe NGƯỢC CHIỀU với A1
─────────────────────────────────────────────────────────────────────────
A1 (gate lúc thực thi) khi không đo được thì KHÔNG chặn — vì chặn oan làm lỡ deadline vào
lệnh LAG T+1, có phí thật. Ở đây chiều fail-safe ngược lại: **không đo được ⇒ KHÔNG chèn
thêm**. Lý do là tính chất của chính chương trình gom, không phải sở thích:
`accept_underfill: true`, `no_chase: true`, resting-bid **re-đặt mỗi phiên** trong cửa sổ
mềm 20 phiên — bỏ MỘT phiên gần như không tốn gì, trong khi chèn một lệnh không có tiền
đằng sau sẽ đẩy cả plan vào diện bị A1 chặn TOÀN BỘ lúc 09:05 (A1 chặn cả plan, không chặn
từng lệnh).
Cận tiền mặt:  bound = availableCash + Σ(lệnh BÁN trong plan) × (1 − FEE_RATE)
Không nhân hệ số đòn bẩy nào — đúng với thiết kế: lệnh DISCRETIONARY_SPECIAL là `cash_only`
("CASH — KHÔNG dùng margin", master plan TV1). Tiền bán được cộng vì `ppse` của DNSE cộng
tiền bán chờ về T+0 vào sức mua ngay phiên đó (đo được 2026-07-28 ZaloPay: pp0Buy 25,54M
trong khi availableCash chỉ 5,68M).

Module READ-ONLY: không ghi file, không đặt lệnh, không sửa plan. Caller quyết định.
"""

from trading_bot.plan_funding_gate import FEE_RATE, check_plan_funding

# Lệnh không có ref_price hợp lệ thì KHÔNG được coi là "chi phí 0" — đó là cách một lệnh
# tàng hình lọt qua phép cộng. Gặp là trả `unpriced` và caller phải fail-safe.
_UNKNOWN = object()


def _get(order, name, default=None):
    """Đọc field của order dù nó là dict (plan JSON thô) hay dataclass PlannedOrder."""
    if isinstance(order, dict):
        return order.get(name, default)
    return getattr(order, name, default)


def order_cost_vnd(order):
    """Chi phí TIỀN của một lệnh mua, đã gồm phí 0,075%. Trả `None` nếu thiếu giá/KL —
    KHÔNG trả 0 (xem `_UNKNOWN`)."""
    qty = _get(order, "qty")
    px = _get(order, "ref_price")
    if px in (None, 0):
        px = _get(order, "limit_price_vnd")
    try:
        qty = int(qty)
        px = float(px)
    except (TypeError, ValueError):
        return None
    if qty <= 0 or px <= 0:
        return None
    return qty * px * (1.0 + FEE_RATE)


def commitment_summary(orders, exclude_ids=()):
    """Cộng phần plan ĐÃ dự chi. Trả dict:
      buy_committed_vnd  : Σ chi phí lệnh MUA (gồm phí)
      sell_proceeds_vnd  : Σ tiền về từ lệnh BÁN (trừ phí) — dùng cho cận tiền mặt
      by_book            : {book: chi phí mua}
      unpriced           : [id,...] lệnh MUA không tính được chi phí (thiếu giá/KL)
      n_buys / n_sells
    `exclude_ids` để loại chính lệnh sắp chèn nếu nó đã nằm trong plan (tránh trừ hai lần).
    """
    excl = {str(i) for i in exclude_ids}
    buy = sell = 0.0
    by_book, unpriced = {}, []
    n_buys = n_sells = 0
    for o in orders or []:
        if str(_get(o, "id", "")) in excl:
            continue
        side = str(_get(o, "side", "") or "").lower()
        cost = order_cost_vnd(o)
        if side == "buy":
            n_buys += 1
            if cost is None:
                unpriced.append(str(_get(o, "id", "?")))
                continue
            buy += cost
            book = str(_get(o, "book", "") or "?")
            by_book[book] = by_book.get(book, 0.0) + cost
        elif side == "sell":
            n_sells += 1
            if cost is None:
                unpriced.append(str(_get(o, "id", "?")))
                continue
            # cost đã cộng phí; tiền BÁN về là gross − phí ⇒ chia lại rồi trừ phí.
            gross = cost / (1.0 + FEE_RATE)
            sell += gross * (1.0 - FEE_RATE)
    return {"buy_committed_vnd": buy, "sell_proceeds_vnd": sell, "by_book": by_book,
            "unpriced": unpriced, "n_buys": n_buys, "n_sells": n_sells}


class _GateOrder:
    """Hình dạng tối thiểu `check_plan_funding` đọc (`o.side/.qty/.ref_price/.ticker/
    .cash_only/.loan_package_id`). Cần vì injector cầm plan dạng **dict JSON thô** còn A1
    viết cho `PlannedOrder` dataclass — không có lớp này thì gate nổ `AttributeError` ngay
    lệnh đầu tiên."""

    __slots__ = ("ticker", "qty", "ref_price", "side", "cash_only", "loan_package_id")

    def __init__(self, o):
        self.ticker = _get(o, "ticker")
        self.qty = _get(o, "qty") or 0
        px = _get(o, "ref_price")
        self.ref_price = px if px not in (None, 0) else (_get(o, "limit_price_vnd") or 0)
        self.side = _get(o, "side")
        self.cash_only = bool(_get(o, "cash_only", False))
        self.loan_package_id = _get(o, "loan_package_id")


def _plan_orders(plan):
    """`orders[]` của plan dù plan là TradePlan (attribute) hay dict JSON thô."""
    if isinstance(plan, dict):
        return plan.get("orders") or []
    return getattr(plan, "orders", None) or []


def _as_gate_plan(plan):
    import types as _types
    return _types.SimpleNamespace(orders=[_GateOrder(o) for o in _plan_orders(plan)])


def _resolved_package(broker, ticker, cash_only):
    """Gói vay lệnh sắp chèn sẽ đi ra bằng — CÙNG hàm, CÙNG cache mà `place_order` dùng,
    nên số gate đo và số lệnh dùng không thể lệch (ca TV1 07-29)."""
    if cash_only:
        fn = getattr(broker, "_resolve_loan_package_id", None)
        if callable(fn):
            try:
                return fn(ticker), "resolved:cash_only"
            except Exception:
                pass
    return None, "account_default"


def residual_headroom(plan, broker, account_mode, ticker, unit_price,
                      cash_only=True, exclude_ids=()):
    """Còn BAO NHIÊU tiền cho một lệnh mua MỚI, sau khi trừ phần plan đã dự chi.

    Trả dict:
      headroom_vnd : float ≥ 0, hoặc None = KHÔNG XÁC ĐỊNH (caller phải fail-safe: không chèn)
      basis        : "pp0buy_residual" | "cash_bound" | "unknown" | "not_live"
      + committed_vnd, utilization, buying_power_vnd, cash_vnd, sell_proceeds_vnd, reason
    """
    summ = commitment_summary(_plan_orders(plan), exclude_ids=exclude_ids)
    base = {"committed_vnd": summ["buy_committed_vnd"],
            "sell_proceeds_vnd": summ["sell_proceeds_vnd"],
            "by_book": summ["by_book"], "unpriced": summ["unpriced"],
            "utilization": None, "buying_power_vnd": None, "cash_vnd": None}

    if str(account_mode or "").lower() != "live":
        # paper/backtest không có `ppse`; gate này là khái niệm của broker thật.
        return dict(base, headroom_vnd=None, basis="not_live",
                    reason=f"mode={account_mode} — không phải live, bỏ qua gate tiền")

    if summ["unpriced"]:
        # Một lệnh mua không tính được chi phí ⇒ phép cộng bên trái KHÔNG đầy đủ ⇒ mọi
        # headroom tính ra đều là số ảo. Không đoán.
        return dict(base, headroom_vnd=None, basis="unknown",
                    reason=(f"{len(summ['unpriced'])} lệnh trong plan thiếu giá/KL "
                            f"({', '.join(summ['unpriced'][:5])}) — không cộng đủ phần đã "
                            f"dự chi ⇒ không xác định được headroom"))

    # ── vế phải #1: sức mua CÒN LẠI theo mô hình tiêu thụ tuyến tính của A1 ───────────────
    verdict = check_plan_funding(_as_gate_plan(plan), broker, account_mode)
    base["utilization"] = verdict.get("utilization")
    if verdict["action"] == "BLOCK":
        return dict(base, headroom_vnd=0.0, basis="pp0buy_residual",
                    reason=("plan HIỆN TẠI đã vượt sức mua (A1 verdict=BLOCK: "
                            f"{verdict['reason']}) — headroom = 0, tuyệt đối không chèn thêm"))

    lp, lp_src = _resolved_package(broker, ticker, cash_only)
    bp = None
    try:
        bp = broker.get_buying_power(ticker, int(unit_price), loan_package_id=lp)
    except Exception:
        bp = None
    base["buying_power_vnd"] = bp

    u = verdict.get("utilization")
    if u is None and not summ["buy_committed_vnd"]:
        # `check_plan_funding` trả SKIPPED (utilization=None) khi plan CHƯA có lệnh mua nào
        # — trường hợp thường gặp nhất, không phải ngoại lệ. Chưa tiêu gì ⇒ U = 0, phải
        # dùng ĐÚNG sức mua pp0Buy chứ không rơi về cận tiền mặt: rơi nhầm nhánh ở đây làm
        # injector chỉ thấy availableCash (ca O: 5M thay vì 40M) ⇒ bỏ phiên oan.
        u = 0.0
    if bp is not None and bp > 0 and u is not None and verdict["action"] in ("OK", "SKIPPED"):
        headroom = max(0.0, (1.0 - u) * bp)
        return dict(base, headroom_vnd=headroom, basis="pp0buy_residual",
                    reason=(f"sức mua {bp:,.0f}đ (gói {lp}, {lp_src}) × phần chưa tiêu "
                            f"{(1.0-u)*100:.1f}% = {headroom:,.0f}đ còn lại sau "
                            f"{summ['n_buys']} lệnh mua đã có ({summ['buy_committed_vnd']:,.0f}đ)"))

    # ── vế phải #2: cận TIỀN MẶT (không đo được pp0Buy hoặc A1 trả UNVERIFIED) ────────────
    try:
        cash = float(broker.get_cash() or 0.0)
    except Exception:
        cash = None
    base["cash_vnd"] = cash
    if cash is None:
        return dict(base, headroom_vnd=None, basis="unknown",
                    reason=("không đọc được pp0Buy LẪN availableCash từ broker — "
                            "không xác định được headroom, fail-safe KHÔNG chèn"))
    bound = cash + summ["sell_proceeds_vnd"]
    headroom = max(0.0, bound - summ["buy_committed_vnd"])
    return dict(base, headroom_vnd=headroom, basis="cash_bound",
                reason=(f"pp0Buy không đo được (bp={bp}, A1 action={verdict['action']}) ⇒ cận "
                        f"TIỀN MẶT: cash {cash:,.0f}đ + tiền bán {summ['sell_proceeds_vnd']:,.0f}đ "
                        f"− đã dự chi {summ['buy_committed_vnd']:,.0f}đ = {headroom:,.0f}đ "
                        f"(KHÔNG nhân đòn bẩy: lệnh gom là cash_only theo thiết kế)"))


def cap_qty_to_headroom(qty, unit_price, headroom_vnd, lot_size):
    """Số lượng lớn nhất ≤ `qty`, chia hết cho lô, mà tiền (gồm phí) vẫn ≤ headroom.
    `headroom_vnd is None` ⇒ 0 (không xác định = không chèn)."""
    qty, lot = int(qty), max(1, int(lot_size))
    if headroom_vnd is None:
        return 0
    unit = float(unit_price) * (1.0 + FEE_RATE)
    if unit <= 0:
        return 0
    affordable = int(float(headroom_vnd) // unit)
    return max(0, min(qty, affordable - affordable % lot))


def gate_injected_order(order, plan, broker, account_mode, lot_size, exclude_ids=()):
    """Điểm vào DUY NHẤT cho injector: nhận order engine vừa sinh, trả (order|None, record).

    - `order=None` ⇒ bỏ phiên này (headroom < 1 lô, hoặc không xác định được).
    - order bị THU NHỎ về bội số lô mua nổi ⇒ record["action"]="SHRINK" (chương trình gom
      khai `accept_underfill: true` và re-đặt mỗi phiên nên thu nhỏ luôn tốt hơn bỏ phiên).
    - mode ≠ live ⇒ "PASS_NOT_LIVE", trả nguyên order (paper không có khái niệm ppse).
    """
    px = _get(order, "limit_price_vnd") or _get(order, "ref_price")
    h = residual_headroom(plan, broker, account_mode, _get(order, "ticker"), px,
                          cash_only=bool(_get(order, "cash_only", True)),
                          exclude_ids=exclude_ids)
    if h["basis"] == "not_live":
        return order, dict(h, action="PASS_NOT_LIVE", qty_before=_get(order, "qty"),
                           qty_after=_get(order, "qty"))
    want = int(_get(order, "qty") or 0)
    capped = cap_qty_to_headroom(want, px, h["headroom_vnd"], lot_size)
    rec = dict(h, qty_before=want, qty_after=capped, cost_before_vnd=order_cost_vnd(order))
    if capped <= 0:
        rec["action"] = "SKIP_NO_CASH"
        rec["human_note"] = (
            f"BỎ PHIÊN: lệnh gom {_get(order, 'ticker')} {want}cp cần "
            f"{(order_cost_vnd(order) or 0):,.0f}đ nhưng headroom chỉ còn "
            f"{h['headroom_vnd'] if h['headroom_vnd'] is None else format(h['headroom_vnd'], ',.0f')}đ "
            f"sau các lệnh V2.4 đã có trong plan. Chương trình gom re-đặt mỗi phiên "
            f"(accept_underfill) nên KHÔNG mất cơ hội vĩnh viễn — nhưng nếu muốn ƯU TIÊN "
            f"tranche này hơn V2.4, phải re-plan (quyết định của người, không của cron).")
        return None, rec
    if capped < want:
        if isinstance(order, dict):
            order = dict(order)
            order["qty"] = capped
            order["estimated_cost_vnd"] = int(capped * float(px))
            order["cash_gate_shrunk_from_qty"] = want
        else:
            order.qty = capped
        rec["action"] = "SHRINK"
        rec["human_note"] = (f"THU NHỎ {want}→{capped}cp cho vừa headroom "
                             f"{h['headroom_vnd']:,.0f}đ (phần còn lại re-đặt phiên sau).")
        return order, rec
    rec["action"] = "PASS"
    return order, rec


def replan_dropped_injection(plan_orders, ledger, plan_date, ticker, book):
    """True khi ledger ĐÃ ghi tranche cho `plan_date` nhưng plan KHÔNG còn order tương ứng
    ⇒ plan đã bị GHI LẠI sau khi injector chèn, tranche rơi mất im lặng.

    Caller phải chèn LẠI (không skip theo dedup-ledger). An toàn: `filled_qty` luôn đọc từ
    broker chứ không từ ledger, và id order là tất định nên dedup-1 vẫn chặn trùng.
    """
    in_ledger = any(str(e.get("plan_date")) == str(plan_date) for e in (ledger or []))
    in_plan = any(_get(o, "ticker") == ticker and _get(o, "book") == book
                  for o in (plan_orders or []))
    return bool(in_ledger and not in_plan)
