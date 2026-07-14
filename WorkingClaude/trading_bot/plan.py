# -*- coding: utf-8 -*-
"""TradePlan — sản phẩm của bot_prepare_plan, đầu vào của bot_execute.

File: data/trade_plans/plan_<account>_<YYYY-MM-DD>.json
(ngày = ngày THỰC THI, T+1 của signal; mỗi account 1 plan riêng).
"""

import dataclasses
import datetime as dt
import json
import os

from .config import PLAN_DIR


@dataclasses.dataclass
class PlannedOrder:
    id: str                  # duy nhất trong plan, vd "BUY-PSI-01"
    ticker: str
    side: str                # "buy" | "sell"
    qty: int                 # đã làm tròn lô
    ref_price: float         # giá tham chiếu của plan (close ngày signal, VND)
    book: str = ""           # BAL | LAG | CAPIT | ETF | SYNC
    play_type: str = ""
    priority: int = 5        # nhỏ = làm trước (sell=1, buy theo weight)
    urgency: str = "normal"  # "normal" | "high" (high: cross spread ngay)
    note: str = ""
    # Pha 2 DCF (2026-07-14): informational, KHÔNG block lệnh.
    # {"status":"RICH"|"CHEAP"|"NOT_COMPUTED","margin_of_safety":<float|null>,"robust":<bool>,"as_of":"YYYY-MM-DD"}
    dcf_check: dict = dataclasses.field(default=None)
    # BẮT BUỘC ghi khi dcf_check.status=RICH AND robust=true AND side=buy; nếu trống → WARN.
    dcf_override_reason: str = ""

    @property
    def value(self):
        return self.qty * self.ref_price


@dataclasses.dataclass
class TradePlan:
    plan_date: str           # ngày thực thi YYYY-MM-DD
    signal_date: str
    strategy: str
    strategy_version: str
    state: int
    state_name: str
    nav_basis: dict          # {"account_nav":..,"paper_nav":..,"scale":..}
    orders: list             # list[PlannedOrder]
    account: str = "main"    # label account profile
    created_at: str = ""
    notes: list = dataclasses.field(default_factory=list)
    # Approval gate (2026-07-13, sau sự cố plan ZaloPay 07-13 chưa duyệt suýt chạy —
    # kb/INCIDENTS.md): plan generator (DollarBill) đặt requires_user_approval=true cho
    # plan cần user duyệt; Mike ghi approved_by sau khi user duyệt thật. bot_execute.py
    # enforce qua approval_block_reason() bên dưới. Default False = backward-compat:
    # plan cũ/paper (account main) không có field này phải chạy như trước.
    requires_user_approval: bool = False
    approved_by: str = None

    def path(self):
        return os.path.join(PLAN_DIR, f"plan_{self.account}_{self.plan_date}.json")

    def save(self):
        os.makedirs(PLAN_DIR, exist_ok=True)
        d = dataclasses.asdict(self)
        d["created_at"] = d["created_at"] or dt.datetime.now().isoformat(timespec="seconds")
        with open(self.path(), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        return self.path()

    @property
    def gross_value(self):
        return sum(o.value for o in self.orders)

    def summary(self):
        buys = [o for o in self.orders if o.side == "buy"]
        sells = [o for o in self.orders if o.side == "sell"]
        lines = [
            f"Plan [{self.account}] {self.plan_date} (signal {self.signal_date}, "
            f"{self.strategy} v{self.strategy_version}, "
            f"state {self.state}={self.state_name})",
            f"  NAV account {self.nav_basis.get('account_nav', 0)/1e6:,.0f}M | "
            f"paper {self.nav_basis.get('paper_nav', 0)/1e9:,.2f}B | "
            f"scale {self.nav_basis.get('scale', 0):.6f}",
            f"  {len(sells)} SELL ({sum(o.value for o in sells)/1e6:,.0f}M) | "
            f"{len(buys)} BUY ({sum(o.value for o in buys)/1e6:,.0f}M)",
        ]
        for o in sorted(self.orders, key=lambda x: x.priority):
            lines.append(f"    [{o.priority}] {o.side.upper():4s} {o.ticker:10s} "
                         f"{o.qty:>10,} @~{o.ref_price:>10,.0f} = {o.value/1e6:>8,.0f}M  "
                         f"{o.book}/{o.play_type} {o.note}")
        for n in self.notes:
            lines.append(f"  ⚠ {n}")
        return "\n".join(lines)


def load_plan(plan_date, account="main"):
    """Đọc plan của (account, plan_date)."""
    if not isinstance(plan_date, str):
        plan_date = plan_date.strftime("%Y-%m-%d")
    path = os.path.join(PLAN_DIR, f"plan_{account}_{plan_date}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    known = {f.name for f in dataclasses.fields(PlannedOrder)}
    orders = []
    for o in d["orders"]:
        filtered = {k: v for k, v in o.items() if k in known}
        # DollarBill's rebalance/trim plan schema (v2+) uses different field names
        # for the same concepts — normalize instead of crashing.
        if "id" not in filtered:
            filtered["id"] = f"{o.get('side', '?').upper()}-{o.get('ticker', '?')}-{o.get('priority', 0):02d}"
        if "ref_price" not in filtered:
            ref = o.get("mtm_price_ref") or o.get("ref_price") or o.get("price")
            if ref is None:
                raise ValueError(f"order {filtered.get('id')} thiếu ref_price/mtm_price_ref — "
                                  f"không có cơ sở giá tham chiếu để đặt lệnh.")
            filtered["ref_price"] = ref
        orders.append(PlannedOrder(**filtered))
    d["orders"] = orders
    # preflight_check.sh chấp nhận cả tên field thay thế approved_by_user — gate phải
    # nhất quán, không được để preflight báo GREEN mà bot lại chặn.
    if not d.get("approved_by") and d.get("approved_by_user"):
        d["approved_by"] = d["approved_by_user"]
    known_plan = {f.name for f in dataclasses.fields(TradePlan)}
    return TradePlan(**{k: v for k, v in d.items() if k in known_plan})


def filter_excluded_tickers(plan, excluded_tickers):
    """Loại bỏ mọi order cho mã trong `excluded_tickers` (legacy/special-situation holding
    ngoài rebalancing tự động — xem ACCOUNT_DEFAULTS trong config.py). Enforce cứng ở tầng
    này — không phụ thuộc vào việc plan generator (DollarBill/bot_prepare_plan.py) có nhớ
    loại trừ đúng hay không, để account nào cũng an toàn dù plan tạo ra thế nào.

    Trả về (plan đã lọc, list order đã bị chặn) — KHÔNG sửa plan tại chỗ, để caller tự log/báo.
    """
    excluded = set(excluded_tickers or [])
    if not excluded:
        return plan, []
    blocked = [o for o in plan.orders if o.ticker in excluded]
    plan.orders = [o for o in plan.orders if o.ticker not in excluded]
    return plan, blocked


def approval_block_reason(plan):
    """Code-gate approval — lớp phòng thủ THỨ HAI, độc lập với việc gửi plan cho user
    duyệt qua send_plan_report.sh (sự cố 2026-07-13: plan ZaloPay requires_user_approval=true
    + approved_by=null suýt chạy lúc 09:05 vì không có gate nào ở tầng executor).

    Trả None nếu được phép thực thi; ngược lại trả chuỗi lý do chặn (caller KHÔNG đặt
    lệnh nào, alert + exit khác 0). Fail-safe pause, không đoán — cùng nguyên tắc
    _ghost_tickers trong executor.py (coding_guidelines.md §5).

    Điều kiện chặn: requires_user_approval truthy AND approved_by trống AND có lệnh.
    - Thiếu field requires_user_approval (plan cũ / paper account main) → default False
      → chạy như trước (backward-compat, KHÔNG chặn giao dịch thường lệ).
    - orders=0 (HOLD) → không chặn dù chưa duyệt: không có gì để thực thi.
    - Plan LLM-authored có thể ghi "true"/"false" dạng CHUỖI — normalize trước khi xét
      ("false"/"no"/"0"/rỗng → không yêu cầu duyệt; chuỗi truthy khác → yêu cầu duyệt).
    """
    req = plan.requires_user_approval
    if isinstance(req, str):
        req = req.strip().lower() not in ("", "false", "no", "0", "none")
    if not req:
        return None
    if not plan.orders:
        return None
    approved = plan.approved_by
    if isinstance(approved, str):
        approved = approved.strip()
        # Plan LLM-authored có thể ghi null dạng CHUỖI ("None"/"null"/"nil"/"nan")
        # — vẫn là chưa duyệt, không để chuỗi truthy lọt qua gate.
        if approved.lower() in ("none", "null", "nil", "nan"):
            approved = ""
    if approved:
        return None
    return (f"plan {plan.plan_date} [{plan.account}] có requires_user_approval=true nhưng "
            f"approved_by trống — {len(plan.orders)} lệnh chưa được user duyệt, "
            f"bot TỪ CHỐI thực thi (không đoán, không tự bỏ qua).")
