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
    d["orders"] = [PlannedOrder(**{k: v for k, v in o.items() if k in known})
                   for o in d["orders"]]
    known_plan = {f.name for f in dataclasses.fields(TradePlan)}
    return TradePlan(**{k: v for k, v in d.items() if k in known_plan})
