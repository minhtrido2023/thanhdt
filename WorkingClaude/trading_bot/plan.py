# -*- coding: utf-8 -*-
"""TradePlan — sản phẩm của bot_prepare_plan, đầu vào của bot_execute.

File: data/trade_plans/plan_<account>_<YYYY-MM-DD>.json
(ngày = ngày THỰC THI, T+1 của signal; mỗi account 1 plan riêng).
"""

import copy
import dataclasses
import datetime as dt
import json
import os
import sys

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
    # Due-diligence (mandate 2026-07-21; bước xác nhận thêm 2026-08-03 sau case DHD):
    # informational, KHÔNG block lệnh — mirror ĐÚNG pattern dcf_check ngay trên.
    # {"has_red_flag":<bool>,"red_flags":[...],"as_of":"YYYY-MM-DD","data_date":"...","evidence":"..."}
    dd_check: dict = dataclasses.field(default=None)
    # BẮT BUỘC ghi khi dd_check.has_red_flag=true AND side=buy; nếu trống → WARN.
    dd_override_reason: str = ""
    # cash_only=True → executor chọn gói vay HỢP LỆ RIÊNG cho mã (query loan-packages
    # theo symbol) thay vì gói default account. Cần cho book DISCRETIONARY_SPECIAL trên
    # mã (vd TV1/UPCOM) mà gói 1841 mainboard của SpaceX KHÔNG hợp lệ → DNSE reject
    # "loanPackageId is required" (bug TV1 07-28; fix cũ "bỏ trường" cũng sai vì DNSE
    # bắt buộc trường này). Xem DNSEBroker._resolve_loan_package_id. Default False = mọi
    # order BAL/LAG/CAPIT giữ nguyên hành vi (gói default account, KHÔNG query thêm).
    # Nằm trong dataclasses.fields nên load_plan() KHÔNG lọc mất field này.
    cash_only: bool = False
    # ── ĐÒN BẨY MARGIN cho RIÊNG sleeve CAPIT (chính sách 2026-08-03, MẶC ĐỊNH TẮT) ────────
    # lever_f = hệ số đòn bẩy đã áp cho lệnh này; loan_package_id = gói vay DNSE dùng cho
    # ĐÚNG lệnh này (override gói default account). CẢ HAI chỉ được gán bởi apply_capit_lever()
    # từ artifact golive — KHÔNG BAO GIỜ tin giá trị do plan generator tự viết vào (LLM/người
    # sửa tay): hàm đó GỠ mọi giá trị không được artifact cho phép. Default None = hành vi cũ
    # nguyên vẹn (gói default account, không đòn bẩy) cho mọi lệnh BAL/LAG/CAPIT/ETF.
    lever_f: float = None
    loan_package_id: int = None
    # ── TRẦN GIÁ MUA TUYỆT ĐỐI (VND) — "bám giá thị trường nhưng KHÔNG BAO GIỜ vượt" ────────
    # Chỉ có hiệu lực với side="buy". Executor._limit_price() lấy min(trần đuổi %, trần này);
    # nếu ngay cả giá SÀN phiên cũng đã > trần này thì KHÔNG đặt lệnh (trả None) thay vì bị
    # `max(px, q.floor)` đẩy vượt. Nhờ đó plan KHÔNG còn phải neo ref_price thấp giả tạo
    # (kiểu anchor/1,04) để "trần đuổi % vô tình chạm đúng anchor" — cách đó khiến giá đặt
    # nằm xa giá đang khớp và gần như không khớp. Đặt ref_price = giá tham chiếu THẬT của thị
    # trường và trần này = anchor ⇒ lệnh bám q.ask sống (re-price mỗi slice_interval_min qua
    # _cancel_stale) mà vẫn bị chặn cứng ở anchor ở MỌI bước.
    # Tên field trùng với key `hard_no_chase_ceiling_vnd` mà discretionary_accumulation.py đã
    # sinh ra sẵn từ trước (trước đây bị load_plan() lọc mất vì không nằm trong dataclass) —
    # cùng khái niệm "no-chase ceiling", không tạo tên thứ hai cho cùng một thứ.
    # Default None = mọi lệnh cũ giữ nguyên hành vi (chỉ có trần đuổi % như trước).
    hard_no_chase_ceiling_vnd: float = None

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


# ── Field CHECK mà executor đọc như DICT — chuẩn hoá TẠI RANH GIỚI NẠP PLAN ────────────────
# Sự cố thật 2026-08-11 → 08-14 (bus question `plan-dd-check-string-gay-poll-fail-moi-fill`,
# incident kb/incidents/2026-08/2026-08-11-plan-dd-check-string-poll-fail.md): plan ghi
# `dd_check`/`dcf_check` dạng CHUỖI văn xuôi thay vì object ⇒ `Executor._sync_fills` gọi
# `_dd.get(...)` ⇒ AttributeError sau MỖI fill ⇒ 22 POLL_FAIL ZaloPay + 27 SpaceX trong một
# phiên (số POLL_FAIL khớp 1:1 số FILL). Fail-safe của `step()` giữ đúng an toàn tiền — không
# lệnh nào sai, không mất tiền — nhưng `_sync_fills` bỏ dở vòng lặp (order sau không cập nhật
# filled/done chu kỳ đó) và throughput tụt về ~1 chu kỳ/lần fill.
#
# HAI nguồn sinh chuỗi, KHÁC HẲN nhau ⇒ vá một chỗ KHÔNG đủ:
#   1. `discretionary_accumulation.py` — literal `"dcf_check": "N/A (SOTP/...)"`. LỖI CODE, cố
#      định, tái diễn mọi phiên gom (plan 08-13 và 08-14 vẫn còn). Đã vá tại nguồn cùng lượt
#      này: nay sinh dict `NOT_COMPUTED` đúng schema `_dcf_check_for_order`.
#   2. Plan do người/agent soạn tay (08-11, 08-12) — KHÔNG có code nào để vá. Chỉ ranh giới nạp
#      plan chặn được, và phải chặn theo KIỂU chứ không theo nguồn.
#
# Vì sao dạng chuẩn hoá này, chứ không phải hai dạng dễ nghĩ ra hơn:
#   · KHÔNG "coi như None" (bỏ hẳn field): text người viết là bằng chứng due-diligence thật
#     ("PASS — 0 red flag, đo 2026-08-11"); mất nó là mất audit trail, đúng thứ §24 cấm.
#   · KHÔNG rải `getattr(x, "get", None)` khắp executor — Winston nêu đúng: vá theo triệu chứng
#     thì lần thứ 3 lại hở ở call-site khác. Một helper, dùng ở ranh giới.
# Thay vào đó: quy về ĐÚNG schema mà mọi consumer đã biết đọc (`format_dcf_check` /
# `format_dd_check` / `_sync_fills`), ở dạng "CHƯA XÁC ĐỊNH" — KHÔNG phải "đã kiểm và sạch" —
# giữ nguyên text gốc trong field lý do, kèm cờ `schema_error=True` để đối soát về sau.
CHECK_FIELDS_AS_DICT = ("dcf_check", "dd_check")


def normalize_check_field(name, val, order_id="", warn=True):
    """Quy `dcf_check`/`dd_check` về dict (hoặc None). KHÔNG BAO GIỜ raise.

    dict → trả NGUYÊN VẸN (hành vi cũ byte-identical cho mọi plan đúng schema).
    None / chuỗi rỗng → None. Khác dict (chuỗi văn xuôi, số, list) → dict "chưa xác định".
    """
    if isinstance(val, dict) or val is None:
        return val
    if isinstance(val, str) and not val.strip():
        return None
    text = val if isinstance(val, str) else repr(val)
    if warn:
        # stderr, KHÔNG raise: một dòng dữ liệu sai schema không được làm hỏng việc nạp plan
        # (bot vẫn phải chạy), nhưng cũng KHÔNG được im lặng — im lặng là cách sự cố này sống
        # được 4 ngày.
        print(f"⚠️ plan schema: order {order_id or '?'} field `{name}` là "
              f"{type(val).__name__} chứ KHÔNG phải object → chuẩn hoá về dạng 'chưa xác "
              f"định' (schema_error=True), text gốc giữ trong payload. SỬA PHÍA SINH PLAN — "
              f"lớp chuẩn hoá này là lưới an toàn, không phải chỗ để dựa vào.", file=sys.stderr)
    if name == "dd_check":
        # `has_red_flag=None`, KHÔNG phải False: ta không biết có cờ đỏ hay không. False là một
        # KHẲNG ĐỊNH "đã kiểm, sạch" mà không ai kiểm — nếu text kia thật ra ghi một cờ đỏ thì
        # False xoá đúng cái cảnh báo cần giữ. None vẫn falsy nên `format_dd_check` /
        # `_sync_fills` (`is True`) im lặng y như trước; chỉ bản ghi là trung thực hơn.
        return {"has_red_flag": None, "red_flags": [], "schema_error": True,
                "evidence": f"schema_error (plan ghi {type(val).__name__}): {text[:200]}"}
    # `dcf_check` (và mọi field check thêm sau): `NOT_COMPUTED` là dạng "không có kết luận" mà
    # `format_dcf_check` + executor đã xử lý đúng từ trước — không tạo status thứ hai cho cùng
    # một ý (status lạ sẽ rơi vào nhánh hiển thị 🔴, đọc thành "đắt", tệ hơn là không hiện gì).
    return {"status": "NOT_COMPUTED", "margin_of_safety": None, "robust": False,
            "schema_error": True,
            "reason": f"schema_error (plan ghi {type(val).__name__}): {text[:120]}"}


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
        # Field executor đọc như dict — chuẩn hoá NGAY, trước khi PlannedOrder tồn tại. Xem
        # normalize_check_field() phía trên (sự cố POLL_FAIL 1:1-với-FILL 2026-08-11→08-14).
        for _cf in CHECK_FIELDS_AS_DICT:
            if _cf in filtered:
                filtered[_cf] = normalize_check_field(_cf, filtered[_cf],
                                                      filtered.get("id", ""))
        # Luật entry-window LAG V2.4 (user duyệt 2026-08-09): lệnh mua có `entry_anchor_price`
        # thì KHÔNG BAO GIỜ được khớp trên giá đó. Suy thẳng ra trần cứng ngay tại ranh giới
        # nạp plan — cùng tinh thần filter_excluded_tickers(): enforce Ở MỘT CHỖ, không phụ
        # thuộc việc plan generator (LLM/người sửa tay) có nhớ ghi thêm field thứ hai hay
        # không. Generator ghi sẵn trần cứng thì tôn trọng giá trị CHẶT HƠN (min), không nới.
        anchor = o.get("entry_anchor_price")
        if filtered.get("side") == "buy" and anchor:
            try:
                anchor = float(anchor)
            except (TypeError, ValueError):
                anchor = None
            if anchor and anchor > 0:
                # `cur` chỉ được thu hẹp trần, không bao giờ vô hiệu hoá nó: giá trị rác
                # (âm/0/không parse được) phải rơi về anchor, KHÔNG được giữ lại — giữ lại
                # thì _hard_buy_ceiling() thấy v<=0 sẽ tắt hẳn trần (quant-skeptic
                # 2026-08-09 bắt được; chưa mã nào sinh ra ca này nhưng đây là lỗi thật).
                try:
                    cur = float(filtered.get("hard_no_chase_ceiling_vnd") or 0)
                except (TypeError, ValueError):
                    cur = 0.0
                filtered["hard_no_chase_ceiling_vnd"] = (
                    min(cur, anchor) if cur > 0 else anchor)
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


def net_offsetting_orders(plan):
    """Gộp các lệnh NGƯỢC CHIỀU cùng mã trong CÙNG 1 plan thành 1 lệnh NET gửi broker.

    VÌ SAO (case thật plan ZaloPay 2026-07-27): SELL VPB 800 (book custom30V_parking, trim)
    + BUY VPB 700 (book LAG, entry mới) trong cùng 1 plan/ngày/account. "Book" là SỔ SÁCH
    NỘI BỘ, KHÔNG phải sub-account của broker — DNSE chỉ thấy TỔNG số cp một mã trong một
    tài khoản. Gửi cả 2 lệnh ra broker tốn phí+spread 2 lượt, trong khi 700cp chỉ là chuyển
    nội bộ custom30V→LAG ở cùng giá thị trường (0 phí/spread thật). Đo trên case: phí bán
    14.940 + phí mua 13.073 = 28.013đ; netting còn 1 lệnh SELL 100cp = 1.868đ → tiết kiệm
    26.145đ + 1 lượt đi qua spread bid-ask. Đây là GIẢM CHI PHÍ THỰC THI, KHÔNG phải alpha.

    NGUYÊN TẮC:
    - Gộp CHỈ ở tầng đặt lệnh ra broker. Sổ sách từng book (entry_price/hold_period/exit của
      LAG, target của park…) do TẦNG TRÊN giữ (paper-book mirror của V23Strategy, hoặc record
      riêng của DollarBill) — KHÔNG suy ngược từ lệnh đã gửi, nên netting ở đây không đụng tới
      kế toán/báo cáo từng book. Ở live, executor.py book-agnostic (journal FILL không ghi
      book) → gộp tại đây an toàn cho ledger từng book. V23Strategy tự net sẵn (mỗi mã 1
      target[t] rồi diff, không bao giờ sinh 2 chiều) — case cần gộp chỉ đến từ plan
      LLM-authored của DollarBill, nên hàm này là lưới an toàn tầng chuẩn hoá plan.
    - net = Σqty_buy − Σqty_sell (cùng mã). net=0 → KHÔNG gửi lệnh nào ra broker (100%
      chuyển nội bộ; cả 2 book vẫn coi như đã giao dịch ở giá TT vì ledger nằm ở tầng trên).
      net≠0 → ĐÚNG 1 lệnh theo chiều bên LỚN hơn, qty=|net|, book = book của bên lớn (phần
      dư của bên lớn sau khi đã "cấp vốn/hàng" nội bộ cho bên nhỏ).
    - CHỈ net khi 1 mã có CẢ buy VÀ sell trong plan. Một chiều (dù nhiều lệnh cùng chiều) →
      GIỮ NGUYÊN, không đổi hành vi (không gộp cùng chiều — ngoài phạm vi yêu cầu).

    THỨ TỰ trong pipeline (bot_execute.py): filter_excluded → NET → cap_capit → cap_lag →
    approval. Net TRƯỚC các trần %ADV là CÓ CHỦ ĐÍCH: trần %ADV đo TÁC ĐỘNG THỊ TRƯỜNG, mà
    chỉ phần NET mới thật sự chạm thị trường (phần chuyển nội bộ không tiêu thụ thanh khoản
    nào). Nếu bên MUA lớn hơn, lệnh net vẫn là BUY (book bên mua) → cap_capit/cap_lag vẫn áp
    trần lên phần dư đó bình thường. Nếu bên BÁN lớn hơn (case VPB) → net là SELL, các trần
    %ADV (chỉ áp buy) không đụng tới — đúng, vì tác động thị trường thật chỉ là bán |net|cp.

    Trả (plan đã sửa, list dict mô tả từng lần netting) — KHÔNG log, caller tự báo. Mỗi dict
    ghi đủ leg gốc từng book (buy_legs/sell_legs) để audit/báo cáo không mất thông tin book.
    """
    from collections import defaultdict

    by_ticker = defaultdict(list)
    for o in plan.orders:
        by_ticker[o.ticker].append(o)

    new_orders, adj, handled = [], [], set()
    for o in plan.orders:
        if id(o) in handled:
            continue
        group = by_ticker[o.ticker]
        buys = [g for g in group if (g.side or "").lower() == "buy"]
        sells = [g for g in group if (g.side or "").lower() == "sell"]
        if not (buys and sells):
            # một chiều (hoặc side lạ) → giữ nguyên toàn bộ group, đúng thứ tự xuất hiện
            for g in group:
                handled.add(id(g))
                new_orders.append(g)
            continue

        for g in group:
            handled.add(id(g))
        tb = sum(g.qty for g in buys)
        ts = sum(g.qty for g in sells)
        net = tb - ts
        internal = min(tb, ts)
        legs_desc = "; ".join(f"{g.side.upper()} {g.qty:,} {g.book or '?'}" for g in group)
        rec = {
            "ticker": o.ticker, "internal_qty": internal, "total_buy": tb,
            "total_sell": ts, "net_qty": net,
            "buy_legs": [{"book": g.book, "qty": g.qty, "note": g.note} for g in buys],
            "sell_legs": [{"book": g.book, "qty": g.qty, "note": g.note} for g in sells],
        }
        if net == 0:
            rec["action"] = "INTERNAL_ONLY"
            rec["net_side"] = None
            rec["reason"] = (f"mua {tb:,} = bán {ts:,} → 0 lệnh ra broker, 100% chuyển nội "
                             f"bộ {internal:,}cp giữa book ở giá thị trường [{legs_desc}]")
            adj.append(rec)
            continue  # net=0 → không thêm lệnh nào

        dom = buys if net > 0 else sells
        side = "buy" if net > 0 else "sell"
        lead = max(dom, key=lambda g: g.qty)  # leg lớn nhất bên dominant quyết định meta
        qty = abs(net)
        note = (f"NET {side.upper()} {qty:,}cp (dư của book {lead.book or '?'}) ← gộp các lệnh "
                f"ngược chiều cùng mã trong plan: [{legs_desc}]. Chuyển nội bộ {internal:,}cp "
                f"giữa book @giá thị trường (0 phí/spread); chỉ {qty:,}cp chạm broker.")
        net_order = PlannedOrder(
            id=f"NET-{o.ticker}-{side.upper()}",
            ticker=o.ticker, side=side, qty=qty, ref_price=lead.ref_price,
            book=lead.book, play_type=lead.play_type,
            priority=min(g.priority for g in dom),
            urgency=("high" if any((g.urgency or "") == "high" for g in dom) else lead.urgency),
            note=note,
            dcf_check=(lead.dcf_check if side == "buy" else None),
            dcf_override_reason=(lead.dcf_override_reason if side == "buy" else ""),
            dd_check=(lead.dd_check if side == "buy" else None),
            dd_override_reason=(lead.dd_override_reason if side == "buy" else ""),
        )
        new_orders.append(net_order)
        rec["action"] = "NETTED"
        rec["net_side"] = side
        rec["net_book"] = lead.book
        rec["reason"] = note
        adj.append(rec)

    plan.orders = new_orders
    return plan, adj


def cap_capit_orders(plan, account_label, status_path=None):
    """Áp trần %ADV cho lệnh MUA book CAPIT — enforce cứng, độc lập plan generator.

    Trần đọc từ `data/golive_v23_status.json` (`capit_adv_caps`: {account: {ticker: VND
    tuyệt đối}}, do golive_recommend_v23.py ghi). Trần TỔNG mỗi mã = X·ADV20·D (X=10%,
    D=2 phiên, ADV20 = median 20 phiên TRƯỚC ngày washout) và đã được CHIA cho các account
    live (pro-rata NAV) TRƯỚC khi ghi — hàm này chỉ đọc đúng phần của `account_label`.
    Cắt qty xuống bội số lô chẵn lớn nhất thỏa `qty*ref_price <= cap`; phần dư KHÔNG dồn
    sang tên khác — sleeve under-deploy có chủ đích, tiền để cash.

    VÌ SAO phải chia (bug đã sửa): trần %ADV là nguồn lực THỊ TRƯỜNG dùng chung cho một mã.
    Bản trước phát 1 trần phẳng {ticker: vnd} và MỖI account enforce full trần đó, nên N
    account cùng rổ CAPIT thì tổng tác động = N × 10% ADV (2 account → ~20%). Phải đọc
    `capit_adv_caps[account_label]`, KHÔNG BAO GIỜ đọc trần tổng ở đây.

    VÌ SAO đọc artifact chứ không đọc field trong order: cùng lý do filter_excluded_tickers
    tồn tại (coding_guidelines §7) — plan do DollarBill (LLM) sinh ra, một cap nằm trong
    plan chỉ có tác dụng khi generator NHỚ copy nó vào. Đọc thẳng artifact của golive thì
    generator quên cũng không mất cap.

    FAIL-CLOSED: có lệnh mua CAPIT mà artifact thiếu/hỏng/không có cap cho mã đó, artifact
    không có phần chia cho account này, artifact còn ở SCHEMA CŨ phẳng {ticker: vnd}, hoặc
    signal_date của artifact ≠ signal_date của plan (artifact cũ) → CHẶN lệnh đó, không
    thả không giới hạn. CAPIT là sự kiện sizing lớn và hiếm; thà không mua còn hơn mua
    quá tay vào đúng ngày thanh khoản cạn (coding_guidelines §5: không đoán, fail-safe).
    Riêng schema cũ: đọc nó như trần của riêng account này chính là tái lập bug N×10% ADV,
    nên nó phải CHẶN chứ không được "thử hiểu cho qua".

    Tác động lịch sử đo được (mike/agents/Taylor/exp_capitadvcap/selfcheck_capit_adv_cap.py,
    14 event washout 2014→2026, sleeve tham chiếu 0,38 tỷ): trần kích hoạt ở ĐÚNG 1/14
    event — NNC ngày 2016-01-18, lệch ~9 triệu VND ở 1 vị thế. KHÔNG phải "0/14 dormant".

    Trả (plan đã sửa, list dict mô tả từng điều chỉnh) — KHÔNG log, để caller tự báo.
    """
    from .config import WORKDIR
    from .vn_market import round_lot, LOT

    def _is_capit_buy(o):
        return (o.book or "").upper() == "CAPIT" and (o.side or "").lower() == "buy"

    if not any(_is_capit_buy(o) for o in plan.orders):
        return plan, []

    caps, err = {}, None
    path = status_path or os.path.join(WORKDIR, "data", "golive_v23_status.json")
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
        all_caps = st.get("capit_adv_caps") or {}
        if any(not isinstance(v, dict) for v in all_caps.values()):
            err = ("capit_adv_caps ở SCHEMA CŨ (phẳng {ticker: vnd}, chưa chia theo "
                   "account) — chạy lại golive_recommend_v23.py trước khi giao dịch CAPIT")
        elif account_label not in all_caps:
            err = (f"artifact không có phần trần %ADV cho account '{account_label}' "
                   f"(có: {sorted(all_caps)}) — account này không nằm trong danh sách "
                   f"live lúc golive chạy")
        else:
            caps = all_caps[account_label]
        if st.get("signal_date") and plan.signal_date and st["signal_date"] != plan.signal_date:
            caps, err = {}, (f"golive_v23_status.json là của signal_date "
                             f"{st['signal_date']} ≠ plan {plan.signal_date} (artifact cũ)")
    except Exception as ex:
        err = f"không đọc được {path}: {ex}"

    adj, keep = [], []
    for o in plan.orders:
        # so sánh theo _is_capit_buy chứ không phải `o in capit`: PlannedOrder là dataclass
        # có __eq__ theo giá trị, hai lệnh trùng hệt nhau sẽ so bằng nhau và lọc nhầm.
        if not _is_capit_buy(o):
            keep.append(o)
            continue
        cap = caps.get(o.ticker)
        if cap is None:
            adj.append({"ticker": o.ticker, "action": "BLOCKED", "qty_before": o.qty,
                        "qty_after": 0, "cap_vnd": None,
                        "reason": err or f"không có cap %ADV cho {o.ticker} trong artifact"})
            continue
        if o.ref_price <= 0:
            adj.append({"ticker": o.ticker, "action": "BLOCKED", "qty_before": o.qty,
                        "qty_after": 0, "cap_vnd": cap,
                        "reason": f"ref_price={o.ref_price} không hợp lệ, không kiểm tra được trần"})
            continue
        max_qty = round_lot(float(cap) / o.ref_price)
        if o.qty <= max_qty:
            keep.append(o)
            continue
        if max_qty < LOT:
            adj.append({"ticker": o.ticker, "action": "BLOCKED", "qty_before": o.qty,
                        "qty_after": 0, "cap_vnd": cap,
                        "reason": f"trần {cap:,.0f}đ < 1 lô @ {o.ref_price:,.0f}đ"})
            continue
        adj.append({"ticker": o.ticker, "action": "TRIMMED", "qty_before": o.qty,
                    "qty_after": max_qty, "cap_vnd": cap,
                    "reason": f"trần %ADV {cap:,.0f}đ (phần dư để cash, không dồn tên khác)"})
        o.qty = max_qty
        keep.append(o)
    plan.orders = keep
    return plan, adj


LAG_ADV_PCT = 0.20           # = liquidity_volume_pct của LIQ_LAG (pt_v23_audit_2014.py:1135)
LAG_ADV_MAX_STALE_DAYS = 30  # dòng ADV mới nhất cũ hơn ngần này ⇒ coi như không có dữ liệu


def cap_lag_orders(plan, account_label, asof=None, live_labels=None, account_mode="live"):
    """Áp trần %ADV cho lệnh MUA book LAG — enforce cứng, độc lập plan generator.

    VÌ SAO (lỗ hổng live-vs-backtest, phát hiện 2026-07-21, job Taylor_20260721_130404):
    baseline pinned R3 (CAGR 27,84%) mô phỏng book LAG với `LIQ_LAG = {liquidity_volume_pct:
    0.20, max_fill_days: 5}` (pt_v23_audit_2014.py:1135) + `min_fill_pct=0.30` là DEFAULT của
    engine (simulate_holistic_nav.py:354) — tức backtest KHÔNG BAO GIỜ mua quá 20% ADV một
    phiên. Đường live không có ràng buộc này (chỉ CAPIT có, `cap_capit_orders` ngay trên),
    nên một lệnh LAG trên mã mỏng (IVS ADV 0,18 tỷ/phiên) đặt được ở live với size mà
    backtest không bao giờ cho phép = giao dịch NGOÀI mô hình.

    Trần = LAG_ADV_PCT × ADV × share, ADV = Volume_3M_P50 × COALESCE(Price,Close) đúng công thức backtest
    (`due_diligence.adv_vnd`, đọc `data/bq_cache/ticker/` — trễ tối đa 1 phiên, chấp nhận
    được vì đây là trung vị 3 tháng; TUYỆT ĐỐI không dùng số này làm giá, §6 bright-line).

    ⚠️ CHẶT HƠN BACKTEST, CÓ CHỦ Ý — đọc kỹ trước khi so số với R3 (sửa sau khi quant-skeptic
    REFUTED bản đầu, 2026-07-21): engine mô phỏng viết `if liq and liq > 0` khi tra trần
    (simulate_holistic_nav.py:1169-1172), nên `liq == 0` HOẶC key thiếu ⇒ daily_max giữ
    nguyên = mua FULL size KHÔNG trần. Nói cách khác backtest KHÔNG chặn mã liq=0 như TMG —
    nó mua trọn. Gate này CHẶN chúng ⇒ đây là một sai lệch MỚI (theo hướng an toàn), KHÔNG
    phải "vá lại một lỗ hổng fidelity". Đo được trên chính rổ ứng viên LAG 2014+ (5.319 event,
    tái dựng từ earnings_events_classified.csv + gate NP_R≥15/prior_n_good≥4/pa_HL3≥5 +
    forensic): 14,8% số event có ADV KHÔNG đo được ở ngày vào lệnh — trong đó 12,8% là
    Volume_3M_P50 ≤ 0 ĐÚNG kiểu TMG. ⚠️ ĐỪNG coi đây là cận trên: 14,8% là tỷ lệ theo EVENT,
    còn tỷ lệ theo DEAL ĐƯỢC CẤP VỐN có thể CAO HƠN — trong engine, tên liq≤0 không bị trần
    nên fill trọn target NGAY trong 1 phiên rồi rời hàng đợi, còn tên đo được ADV bị bóp
    20%/phiên và giữ vốn tới 5 phiên ⇒ tên liq≤0 bị chọn vào nhóm được cấp vốn NHIỀU hơn tỷ
    lệ tự nhiên (quant-skeptic 2026-07-21 lần 2). Con số theo deal chưa đo. Nghĩa là:
    baseline 27,84% CAGR không còn mô tả
    đúng đường live sau khi bật gate này, muốn con số chuẩn phải re-pin bằng một lần chạy
    pt_v23 với engine coi liq≤0 là CHẶN. Quyết định giữ CHẶN (không nới theo backtest) là
    quyết định RỦI RO có chủ ý, cần user duyệt — không phải kết luận từ backtest.

    `share` = 1/N với N = số account LIVE (enabled + mode=live, MỌI broker — cố ý không dùng
    `live_dnse_labels()` vì nó lọc broker=='dnse' và sẽ đếm thiếu một account live sàn khác,
    làm tổng vượt 20%). LÝ DO chia: %ADV là nguồn lực THỊ TRƯỜNG dùng chung cho một mã, mỗi
    account enforce full 20% thì 2 account = 40% — đúng bug `cap_capit_orders` đã phải sửa.
    Chia ĐỀU (không pro-rata NAV như CAPIT) vì không có artifact fleet-level tính sẵn phần
    chia; tổng vẫn đúng 20%. Account paper dùng CÙNG share (không phải 1.0) để paper không
    lệch khỏi live — paper là bàn thử của live, khác share là tự tạo tracking error.

    Cắt (TRIM) chứ không chặn khi vượt trần: phần dư tự động được mua tiếp các phiên sau,
    KHÔNG cần cơ chế carry-over mới — plan sinh lại mỗi ngày theo diff target-vs-thật
    (`strategies.py`: `target[t]` từ paper book mirror, orders = target − real_pos), nên
    phần chưa khớp hôm nay tự xuất hiện lại trong plan hôm sau. Executor cũng đã
    `cancel_all_open("EOD")` cuối phiên nên không có lệnh treo qua đêm.

    FAIL-CLOSED (mirror cap_capit_orders): không đọc được cache / không có mã trong cache /
    thiếu Volume_3M_P50|Close / dữ liệu ADV cũ hơn LAG_ADV_MAX_STALE_DAYS / ADV ≤ 0 /
    ref_price ≤ 0 / trần < 1 lô / KHÔNG dựng được danh sách account live / account đang chạy
    mode=live mà KHÔNG có trong danh sách đó (config lệch ⇒ không biết chia bao nhiêu) →
    CHẶN lệnh đó. Không mua một mã còn hơn mua một mã mà ta không đo được thanh khoản HOẶC
    không biết mình được phép chiếm bao nhiêu %ADV (coding_guidelines §5).

    KHÔNG mô phỏng `max_fill_days=5` / `min_fill_pct=0.30`: đó là luật HỦY của simulation
    (bỏ deal nếu 5 phiên chưa fill ≥30%), live không có state đếm ngày-đang-fill. Đây là
    khác biệt fidelity CÒN LẠI, đã ghi nhận, không tự chế cơ chế mới ở đây.

    Trả (plan đã sửa, list dict mô tả từng điều chỉnh) — KHÔNG log, để caller tự báo.
    """
    from .vn_market import round_lot, LOT

    def _is_lag_buy(o):
        return (o.book or "").upper() == "LAG" and (o.side or "").lower() == "buy"

    if not any(_is_lag_buy(o) for o in plan.orders):
        return plan, []

    asof = str(asof or plan.plan_date)[:10]

    share, share_err = 1.0, None
    try:
        if live_labels is None:
            from .config import load_config, load_accounts
            live_labels = [p["label"] for p in load_accounts(load_config())
                           if p["enabled"] and p["cfg"]["mode"] == "live"]
        live_labels = list(live_labels or [])
        is_live = str(account_mode or "live").lower() == "live"
        if is_live and account_label not in live_labels:
            share_err = (f"account '{account_label}' chạy mode=live nhưng KHÔNG có trong danh "
                         f"sách account live ({sorted(live_labels) or 'RỖNG'}) — không xác "
                         f"định được phần %ADV được phép chiếm, config lệch")
        else:
            share = 1.0 / max(1, len(live_labels))
    except Exception as ex:
        share_err = f"không xác định được danh sách account live: {ex}"

    adj, keep = [], []
    for o in plan.orders:
        if not _is_lag_buy(o):
            keep.append(o)
            continue

        def _block(reason, cap=None):
            adj.append({"ticker": o.ticker, "action": "BLOCKED", "qty_before": o.qty,
                        "qty_after": 0, "cap_vnd": cap, "reason": reason})

        if share_err:
            _block(share_err)
            continue
        if o.ref_price <= 0:
            _block(f"ref_price={o.ref_price} không hợp lệ, không kiểm tra được trần")
            continue
        adv, data_date, err = _adv_for_gate(o.ticker, asof)
        if err:
            _block(f"không đo được ADV: {err}")
            continue
        if data_date:
            try:
                lag_days = (dt.date.fromisoformat(asof) - dt.date.fromisoformat(data_date)).days
            except Exception:
                lag_days = None
            if lag_days is not None and lag_days > LAG_ADV_MAX_STALE_DAYS:
                _block(f"dữ liệu ADV mới nhất {data_date} cũ {lag_days} ngày so với {asof} "
                       f"(> {LAG_ADV_MAX_STALE_DAYS}) — mã có thể ngừng giao dịch/huỷ niêm yết")
                continue
        if adv <= 0:
            _block(f"ADV = 0 (Volume_3M_P50×Price, data {data_date}) — mã không có thanh "
                   f"khoản thật, đóng góp 0 vào backtest")
            continue

        cap = LAG_ADV_PCT * adv * share
        max_qty = round_lot(cap / o.ref_price)
        if o.qty <= max_qty:
            keep.append(o)
            continue
        if max_qty < LOT:
            _block(f"trần {cap:,.0f}đ ({LAG_ADV_PCT:.0%} ADV × {share:.2f}) < 1 lô "
                   f"@ {o.ref_price:,.0f}đ", cap)
            continue
        adj.append({"ticker": o.ticker, "action": "TRIMMED", "qty_before": o.qty,
                    "qty_after": max_qty, "cap_vnd": cap,
                    "reason": f"trần {LAG_ADV_PCT:.0%} ADV × {share:.2f} = {cap:,.0f}đ "
                              f"(ADV {adv:,.0f}đ, data {data_date}); phần dư mua tiếp phiên sau"})
        o.qty = max_qty
        keep.append(o)
    plan.orders = keep
    return plan, adj


def _adv_for_gate(ticker, asof):
    """Tách riêng để self-check monkeypatch được nguồn ADV mà không cần bq_cache thật."""
    from .due_diligence import adv_vnd
    return adv_vnd(ticker, asof)


def _rating_gate_deps():
    """Nguồn cho gate rating LAG. Tách riêng để self-check monkeypatch được (như _adv_for_gate).

    Trả (bq, lag_filter_low_rating) — DÙNG LẠI nguyên hàm gate của tầng tín hiệu, không
    viết lại logic point-in-time.
    """
    import sys
    from .config import WORKDIR
    if WORKDIR not in sys.path:
        sys.path.insert(0, WORKDIR)
    from simulate_holistic_nav import bq
    from lag_rating_filter import lag_filter_low_rating
    return bq, lag_filter_low_rating


def filter_lag_rating_orders(plan, asof=None):
    """GATE CỨNG 8L rating ≤3 cho lệnh MUA book LAG — LƯỚI AN TOÀN Ở TẦNG ORDER.

    VÌ SAO: chính sách "ứng viên LAG phải có 8L rating ≤3, rating ≥4 auto-exclude" (user chốt
    2026-07-27 sau 2 case TRC rating=4/D rồi MST rating=4/E) tới nay CHỈ được enforce ở tầng
    SINH ứng viên (`lag_rating_filter.lag_filter_low_rating` gọi trong golive_recommend_v23.py).
    Docstring của chính gate đó ghi thẳng lỗ hổng: *"gate này KHÔNG có lưới an toàn ở executor"*
    (lag_rating_filter.py:33-34). Plan là JSON do LLM viết (DollarBill) hoặc người sửa tay — một
    lệnh `{"ticker":"MST","book":"LAG","side":"buy"}` viết thẳng vào plan đi qua được toàn bộ
    cascade hiện có (filter_excluded không biết mã, cap_lag_orders chỉ kiểm ADV) và ra tới broker
    dù rating=4. Hàm này đóng lỗ hổng đó — cùng nguyên tắc "enforce cứng, không phụ thuộc plan
    generator có nhớ hay không" của filter_excluded_tickers/cap_capit_orders/cap_lag_orders.

    KHÔNG phải chính sách mới: ngưỡng, phạm vi (chỉ book LAG), nguồn (`tav2_bq.fa_ratings_8l`,
    point-in-time `time ≤ asof`) đều dùng lại NGUYÊN hàm `lag_filter_low_rating` — thay đổi duy
    nhất là nơi gọi. Đánh đổi backtest đã biết + đã được user duyệt: xem docstring
    lag_rating_filter.py.

    FAIL-MODE — đồng bộ ĐÚNG hành vi gate S1 tầng tín hiệu (đọc lag_rating_filter.py §FAIL-SAFE):
      · TỪNG MÃ rating ≥4  → LOẠI lệnh đó (fail-closed).
      · TỪNG MÃ không có rating nào ≤ asof → LOẠI lệnh đó (fail-closed: "phải CÓ rating≤3 mới
        được vào" ⇒ không xác nhận được thì không mua).
      · CẢ NGUỒN hỏng (BQ lỗi / không import được) → GIỮ NGUYÊN plan (fail-OPEN) + 1 bản ghi
        action="FAIL_OPEN" để caller báo LOUD. Chặn sạch book LAG vì một lỗi mạng thiệt hại lớn
        hơn — cùng lý lẽ đã chốt ở tầng tín hiệu, KHÔNG tự sáng tác hành vi khác ở đây.

    Vị trí trong cascade (bot_execute.py): filter_excluded → net → cap_capit → cap_lag → **rating**
    → approval. Đặt sau cap_lag (cùng nhóm LAG); thứ tự với cap_lag không đổi kết quả vì cap_lag
    chỉ đổi qty còn gate này loại cả lệnh, nhưng đặt sau thì log cắt-trần không in cho lệnh rốt
    cuộc bị loại.

    Trả (plan đã lọc, list dict mô tả từng lệnh bị loại / cảnh báo) — KHÔNG log, caller tự báo.
    Mỗi dict: {"ticker", "order_id", "rating" (int|None), "action", "qty_before", "reason"}.
    """
    def _is_lag_buy(o):
        return (o.book or "").upper() == "LAG" and (o.side or "").lower() == "buy"

    lag_buys = [o for o in plan.orders if _is_lag_buy(o)]
    if not lag_buys:
        return plan, []

    asof = str(asof or plan.plan_date)[:10]
    tickers = sorted({o.ticker for o in lag_buys})
    try:
        import pandas as pd
        bq, lag_filter_low_rating = _rating_gate_deps()
        cand = pd.DataFrame({"ticker": tickers})
        _, dropped, src_err = lag_filter_low_rating(bq, cand, asof)
    except Exception as ex:
        dropped, src_err = [], f"{type(ex).__name__}: {ex}"

    if src_err:
        # Nguồn rating hỏng TOÀN BỘ → fail-open (giữ nguyên plan), nhưng phải BÁO ĐỘNG:
        # đây đúng là kịch bản mà lag_rating_filter.py yêu cầu "người đọc status/plan để ý".
        return plan, [{"ticker": None, "order_id": None, "rating": None,
                       "action": "FAIL_OPEN", "qty_before": None,
                       "reason": f"KHÔNG kiểm tra được 8L rating cho {tickers} ({src_err}) — "
                                 f"GIỮ NGUYÊN lệnh (fail-open, đồng bộ gate tầng tín hiệu). "
                                 f"CẦN NGƯỜI KIỂM TRA rating trước khi tin phiên này."}]

    bad = {d["ticker"]: d for d in dropped}
    if not bad:
        return plan, []
    blocked, keep = [], []
    for o in plan.orders:
        d = bad.get(o.ticker) if _is_lag_buy(o) else None
        if d is None:
            keep.append(o)
            continue
        blocked.append({"ticker": o.ticker, "order_id": o.id, "rating": d.get("rating"),
                        "action": "BLOCKED", "qty_before": o.qty, "reason": d.get("reason")})
    plan.orders = keep
    return plan, blocked


def _governance_gate_deps():
    """Nguồn cho gate quản trị LAG. Tách riêng để self-check monkeypatch được (như _rating_gate_deps).

    Trả `lag_filter_forensic_banned` — DÙNG LẠI nguyên hàm gate của tầng tín hiệu (BANNED +
    LAG_USER_EXCLUDED + cờ forensic), không viết lại ba nguồn ở đây. KHÔNG cần `bq`: cả ba
    nguồn đều cục bộ (2 hằng số trong code + 1 CSV).
    """
    import sys
    from .config import WORKDIR
    if WORKDIR not in sys.path:
        sys.path.insert(0, WORKDIR)
    from lag_forensic_filter import lag_filter_forensic_banned
    return lag_filter_forensic_banned


def filter_lag_governance_orders(plan, asof=None):
    """GATE QUẢN TRỊ (BANNED + user-loại + cờ forensic) cho lệnh MUA book LAG — TẦNG ORDER.

    VÌ SAO: `lag_forensic_filter.lag_filter_forensic_banned` (tầng SINH ứng viên, live từ
    2026-08-03) tự ghi trong docstring rằng lưới tương ứng ở TẦNG LỆNH **CHƯA có** — và đó
    chính là tầng mà sự cố thật đã xảy ra: **2026-07-23 DollarBill đưa IVS vào plan LAG CẢ HAI
    account** (SpaceX 1800cp + ZaloPay 2750cp) dù user đã loại tường minh 07-21. Gate tầng tín
    hiệu chặn được việc IVS TRỞ THÀNH ứng viên; nó KHÔNG chặn được một dòng
    `{"ticker":"IVS","book":"LAG","side":"buy"}` viết thẳng vào plan JSON (LLM hoặc người sửa
    tay). Trước hàm này, lớp phòng thủ duy nhất cho ca đó là TRÍ NHỚ của người lập plan — đúng
    khuôn thất bại mà `filter_lag_rating_orders` (P1) đã được xây để vá cho gate rating.

    KHÔNG phải chính sách mới: cả ba nguồn, ngữ nghĩa ngày hiệu lực (`date <= asof`) và fail-mode
    đều dùng lại NGUYÊN `lag_filter_forensic_banned` — thay đổi duy nhất là NƠI GỌI.

    FAIL-MODE — đồng bộ ĐÚNG hành vi gate tầng tín hiệu (không tự sáng tác hành vi khác):
      · Mã thuộc `BANNED` / `LAG_USER_EXCLUDED` → LOẠI lệnh (fail-closed tuyệt đối: hằng số
        trong code, không thể hỏng).
      · Mã có cờ forensic `exclude` đã hiệu lực tới `asof` → LOẠI lệnh.
      · `data/forensic_flags.csv` hỏng → hàm dưới vẫn áp 2 hằng số + trả `src_err`; ta GIỮ các
        lệnh còn lại (fail-open cho riêng nguồn CSV) + 1 bản ghi action="FAIL_OPEN_FORENSIC"
        để caller báo LOUD. Chặn sạch book LAG vì một file lỗi thì thiệt hại lớn hơn rủi ro.
      · Cả gate không import/chạy được → GIỮ NGUYÊN plan (fail-OPEN) + action="FAIL_OPEN".

    Vị trí trong cascade (bot_execute.py): filter_excluded → net → cap_capit → cap_lag →
    rating → **governance** → lever → approval. Đặt sau `rating` (cùng nhóm LAG); thứ tự giữa
    hai gate này KHÔNG đổi kết quả (cả hai loại hẳn lệnh, không đổi qty) — chỉ đổi việc log nào
    in ra trước cho một lệnh trúng cả hai điều kiện.

    Trả (plan đã lọc, list dict). Mỗi dict: {"ticker", "order_id", "kind"
    ("banned"|"user_exclude"|"forensic"|None), "flag_date", "action", "qty_before", "reason"}.
    """
    def _is_lag_buy(o):
        return (o.book or "").upper() == "LAG" and (o.side or "").lower() == "buy"

    lag_buys = [o for o in plan.orders if _is_lag_buy(o)]
    if not lag_buys:
        return plan, []

    asof = str(asof or plan.plan_date)[:10]
    tickers = sorted({o.ticker for o in lag_buys})
    try:
        import pandas as pd
        from .config import WORKDIR
        lag_filter_forensic_banned = _governance_gate_deps()
        cand = pd.DataFrame({"ticker": tickers})
        _, dropped, src_err = lag_filter_forensic_banned(cand, asof, workdir=WORKDIR)
    except Exception as ex:
        # Gate KHÔNG chạy được (import lỗi/pandas lỗi) → fail-open + báo động, giống
        # filter_lag_rating_orders. KHÔNG âm thầm bỏ qua.
        return plan, [{"ticker": None, "order_id": None, "kind": None, "flag_date": None,
                       "action": "FAIL_OPEN", "qty_before": None,
                       "reason": f"KHÔNG chạy được gate quản trị LAG cho {tickers} "
                                 f"({type(ex).__name__}: {ex}) — GIỮ NGUYÊN lệnh (fail-open). "
                                 f"CẦN NGƯỜI KIỂM TRA BANNED/user-loại/forensic trước khi tin "
                                 f"phiên này."}]

    bad = {d["ticker"]: d for d in dropped}
    blocked, keep = [], []
    for o in plan.orders:
        d = bad.get(o.ticker) if _is_lag_buy(o) else None
        if d is None:
            keep.append(o)
            continue
        blocked.append({"ticker": o.ticker, "order_id": o.id, "kind": d.get("kind"),
                        "flag_date": d.get("flag_date"), "action": "BLOCKED",
                        "qty_before": o.qty, "reason": d.get("reason")})
    plan.orders = keep
    if src_err:
        # Hai hằng số VẪN được áp (mọi lệnh bị chặn ở trên vẫn có hiệu lực); chỉ riêng nguồn
        # CSV forensic là không đọc được ⇒ nói to, đứng SAU các bản ghi BLOCKED.
        blocked.append({"ticker": None, "order_id": None, "kind": None, "flag_date": None,
                        "action": "FAIL_OPEN_FORENSIC", "qty_before": None,
                        "reason": f"KHÔNG đọc được cờ forensic ({src_err}) — BANNED + "
                                  f"LAG_USER_EXCLUDED VẪN áp, nhưng cờ forensic KHÔNG được "
                                  f"kiểm cho {tickers}. CẦN NGƯỜI KIỂM TRA."})
    return plan, blocked


# ── PHẠM VI USER DUYỆT cho đòn bẩy CAPIT (2026-08-03) — NGUỒN CHUẨN TẮC DUY NHẤT ──────────
# Ghim ở ĐÂY, tầng thực thi, chứ không phải chỉ ở tầng sinh tín hiệu. Lý do (arch-reviewer
# 2026-08-03, phát hiện F2): CẢ HAI file mà runtime đọc — `data/trading_rules.json` VÀ
# `data/golive_v23_status.json` — đều khớp `.gitignore:12` (`*.json`), tức không diff, không
# blame, không backup. Nếu envelope chỉ được ép ở `golive_recommend_v23.py` thì cổng CUỐI
# trước tiền vay vẫn tin tuyệt đối vào một artifact không ai canh: sửa `f: 5.0` vào artifact
# là đủ để vay gấp 5. Ép ở cả hai tầng ⇒ muốn nới thật phải sửa CODE (có version control)
# và đi qua review. `golive_recommend_v23.py` import chính 3 hằng này (không tự khai lại).
CAPIT_LEVER_APPROVED_F = 1.3
CAPIT_LEVER_APPROVED_PACKAGE = 1840          # DNSE "RocketX" (gói default account là 1841)
CAPIT_LEVER_APPROVED_ACCOUNTS = ["SpaceX"]   # ZaloPay cash-only ⇒ ngoài phạm vi

# TRẦN cho hai thừa số sinh ra mục tiêu VND (dùng ở _verify_targets_integrity) — NEO THEO
# `state` mà chính artifact công bố, KHÔNG phải trần phẳng.
#
# VÌ SAO KHÔNG PHẢI TRẦN PHẲNG (arch-reviewer vòng 3, phát hiện #2 — đo được, không phải lý
# thuyết): bản đầu đặt `capit_size ≤ 1,0`, mà 1,0 ĐÚNG BẰNG giá trị hợp lệ LỚN NHẤT
# (`capit_base` ở CRISIS). Ngày NEUTRAL thường lệ capit_size = 0,375 (0,75 × grind 0,5), nên
# trần phẳng không ràng buộc gì: sửa `capit_size` 0,375 → 1,0 rồi tính lại 2 số dẫn xuất là
# ba đẳng thức vẫn đúng, `nav_basis_vnd` KHÔNG đổi nên neo NAV sống cũng không thấy gì. Probe
# đo được **2,67×** mục tiêu (envelope tối đa lọt được 111,6% NAV, so với thiết kế 13,6%).
#
# Neo theo state đóng đúng bậc tự do đó: hai bảng dưới là BẢN SAO CỦA CODE SẢN XUẤT
# (`deploy_golive_dt5g_v4/golive_recommend_v23.py`: `capit_base()` dòng ~555 và
# `STATE_LAG_WEIGHT` dòng 97) — chép vào đây có chủ đích, vì tầng thực thi KHÔNG được import
# script golive (nó chạy BQ lúc import). Đổi bảng bên kia mà quên bên này ⇒ cổng SIẾT chặt
# hơn thực tế (không cấp đòn bẩy), tức lệch về phía an toàn; ca kiểm C30 ghim đúng cặp số này.
# `capit_size = capit_base(state) × (0,5 nếu grind)` ⇒ luôn ≤ capit_base(state).
_CAPIT_BASE_BY_STATE = {1: 1.0, 2: 0.5, 3: 0.75, 4: 0.5, 5: 0.5}    # CRISIS/BEAR/NEUTRAL/BULL/EX
_W_LAG_MAX_BY_STATE = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}  # golive.STATE_LAG_WEIGHT
# Nguồn ĐỘC LẬP để đối chiếu `state` mà artifact tự khai (publish_gated_state.py ghi, KHÁC
# tiến trình/khác file với golive_recommend_v23.py). Khai `state=1` để mở trần capit_size lên
# 1,0 thì phải sửa KHỚP cả file này — hai artifact, hai lần ghi, cùng một lời nói dối.
GOLIVE_STATE_TODAY_REL = ("deploy_golive_dt5g_v4", "golive_state_today.json")
# Neo NAV sống: chỉ chặn khi artifact khai NAV LỚN HƠN thực tế quá biên này (chiều duy
# nhất tạo ra vay vượt mức). Biên nới tay có chủ đích — giữa lúc công bố (~19:03) và lúc
# thực thi (~09:05 hôm sau) NAV đổi thật do giá mở cửa (biên độ HOSE ±7%/phiên) và do
# lệnh đã khớp. 15% >> nhiễu thật, << mọi bội số mà một lần sửa artifact nhắm tới.
CAPIT_LEVER_NAV_TOL = 0.15
# `approved_by` KHÔNG được là một chuỗi giữ chỗ hay tên một tác nhân tự động. Cùng tinh thần
# coding_guidelines §20 (`decided_by: "user"` chỉ ghi khi user xác nhận THẬT): bản ghi duyệt
# vay tiền phải trỏ về một NGƯỜI. So khớp NGUYÊN chuỗi (lower/strip), nên
# "user (John) — Mike ghi hộ lúc 21:37" vẫn hợp lệ; đúng một chữ "mike" thì không.
# `mike/bin/approve_margin_day.py` IMPORT chính danh sách này (một nguồn, không hai bản sao).
#
# ⚠️ ĐÂY LÀ QUY ƯỚC MỀM, KHÔNG PHẢI BỘ LỌC (arch-reviewer vòng 3 #9 — đo được): nó chặn
# "mike"/"bot"/"agent"/"auto" nhưng CHO QUA "system-auto", "Claude", "yes", "u", "-". Không
# cơ học hoá được việc "chuỗi này có trỏ về một người thật không" — cùng kết luận với
# coding_guidelines §20 (quy ước + báo cáo, không phải cổng). Thứ THẬT SỰ chặn agent tự duyệt
# là dấu vết: mỗi lần ghi đều bắn bus + Discord, và từ vòng 3 script còn đổi exit code khi
# dấu vết đó gửi KHÔNG thành công. Đừng đọc danh sách này như một lá chắn.
APPROVAL_PLACEHOLDERS = ("", "none", "null", "nil", "nan", "false", "0", "pending", "tbd",
                         "auto", "agent", "bot", "system", "mike", "dollarbill", "taylor",
                         "mafee", "winston", "wags", "spyros", "wendy")


def _artifact_state(st, state_path):
    """`state` của phiên, ĐÃ đối chiếu 2 nguồn độc lập → (state|None, lý do nếu không tin được).

    `state` quyết định trần của `capit_size`/`w_lag_target` (xem `_verify_targets_integrity`),
    nên nó tự trở thành một bậc tự do: khai `state=1` (CRISIS) là mở trần capit_size 0,75 → 1,0.
    Chốt lại bằng nguồn ĐỘC LẬP `golive_state_today.json` — file khác, do `publish_gated_state.py`
    ghi ở một bước khác của chuỗi, mang chính con số mà `get_gated_state()` công bố.

    Fail-closed (trả None) khi không đọc được HOẶC hai nguồn lệch nhau: không biết chắc state
    thì không biết trần nào đúng, và fail-safe ở đây là KHÔNG đòn bẩy (lệnh vẫn chạy vốn tự có).
    """
    try:
        s_art = int(st.get("state"))
    except (TypeError, ValueError):
        return None, (f"artifact không khai `state` hợp lệ ({st.get('state')!r}) — không xác "
                      f"định được trần sizing của phiên, KHÔNG cấp đòn bẩy")
    path = state_path
    try:
        with open(path, encoding="utf-8") as f:
            _pub = json.load(f) or {}
        s_pub = int(_pub["state"])
    except Exception as ex:
        return None, (f"không đọc được `state` từ nguồn độc lập {path} "
                      f"({type(ex).__name__}: {ex}) — không đối chiếu được state mà artifact "
                      f"tự khai, KHÔNG cấp đòn bẩy")
    # ĐỘ TƯƠI của nguồn độc lập (arch-reviewer vòng 4 #5). Hai file được sinh trong CÙNG chuỗi
    # 19:00-19:03 (`publish_gated_state.py` rồi `golive_recommend_v23.py`), nên `as_of` phải
    # bằng `signal_date`. Không kiểm thì một lần publish chết im lặng biến "artifact thứ hai"
    # thành vô nghĩa: nó vẫn khớp, nhưng khớp do TRÙNG giá trị của hôm qua chứ không phải do
    # được xác nhận. Đây đúng bài §14 (consumer phải tự kiểm độ tươi, không tin thứ tự cron).
    _asof, _sig = str(_pub.get("as_of") or ""), str(st.get("signal_date") or "")
    if _sig and _asof != _sig:
        return None, (f"nguồn state độc lập {os.path.basename(path)} có as_of={_asof!r} ≠ "
                      f"signal_date của artifact {_sig!r} — nó KHÔNG xác nhận phiên này (có "
                      f"thể publish_gated_state đã chết im lặng), KHÔNG cấp đòn bẩy")
    if s_art != s_pub:
        return None, (f"artifact khai `state`={s_art} nhưng nguồn độc lập "
                      f"golive_state_today.json khai {s_pub} — state quyết định trần sizing, "
                      f"hai nguồn lệch nhau ⇒ KHÔNG cấp đòn bẩy")
    return s_art, ""


def _verify_targets_integrity(t, basket, st=None, state_path=None, n_basket=None):
    """Kiểm TÍNH NHẤT QUÁN NỘI TẠI của khối `capit_slot_targets[<account>]` → "" nếu sạch,
    chuỗi lý do nếu hỏng (caller fail-closed).

    THU HẸP KHE ĐÃ GHI Ở `known_limits` (quant-skeptic 2026-08-03, ca kiểm C29b cũ): mốc neo
    trần VND dùng TRƯỜNG GỐC *của chính artifact đó*, nên nó chỉ chặn ca sửa MỘT trường.
    Sửa ĐỒNG BỘ cả hai (gốc ×3, levered = gốc ×3 ×1,3) thì mọi tỷ lệ vẫn đúng ⇒ qua sạch.

    Cách thu hẹp: golive KHÔNG chỉ công bố kết quả, nó công bố cả BA thừa số sinh ra kết quả
    (`nav_basis_vnd` × `w_lag_target` × `capit_size` → `capit_total_target_vnd`, rồi
    `/n_slots` → slot). Ba đẳng thức đó là ràng buộc MIỄN PHÍ mà một lần sửa tay/LLM gần
    như chắc chắn phá vỡ. Muốn giữ nguyên vẹn phải sửa ĐỒNG BỘ nhiều trường, và khi đó thừa
    số bị sửa lại rơi vào trần NEO THEO STATE (`w_lag`/`capit_size`, mà `state` lại bị chốt
    bằng một artifact thứ hai), hoặc vào neo NAV SỐNG đo ở tầng broker
    (`lever_live_preflight`). Bốn lớp, bốn nguồn: số học nội tại · bảng sizing trong code ·
    artifact state độc lập · sổ broker sống.

    ⚠️ **KHE NÀY THU HẸP, CHƯA ĐÓNG HẲN** (arch-reviewer vòng 3 đo được, đừng đọc đoạn trên
    thành "đã đóng"): bản trần PHẲNG đầu tiên cho lọt **2,67×** mục tiêu (envelope tối đa
    111,6% NAV) chỉ bằng cách sửa 3 trường nhất quán mà không đụng `nav_basis_vnd`. Neo theo
    state cắt bậc tự do đó xuống còn phần dư trong CÙNG một state (NEUTRAL: 0,375 → trần
    0,75, tức tối đa 2× chứ không phải 2,67×, và phải khai thêm `capit_grind=false`). Cổng
    THẬT SỰ chặn quy mô ở đây là **cổng người thứ hai** (`margin_day_approval`): user nhìn Σ
    tiền vay ở báo cáo 21:00 và duyệt đúng một rổ + một trần VND. Đây không phải chữ ký số:
    nó chứng minh "các con số còn giải thích được lẫn nhau", không chứng minh "chưa ai sửa".

    `st`/`state_path` — artifact đầy đủ + đường dẫn nguồn state ĐỘC LẬP, để đối chiếu `state`
    qua `_artifact_state`. Thiếu (gọi kiểu cũ) ⇒ bỏ qua neo state, giữ các kiểm còn lại.
    `n_basket` — `n_capit_basket` của artifact (rổ ĐẦY ĐỦ của phiên), dùng thay cho số khoá
    `capit_adv_caps` khi đối chiếu `n_slots` (xem bên dưới).
    """
    need = ("nav_basis_vnd", "w_lag_target", "capit_size", "nav_book_lag_vnd",
            "capit_total_target_vnd", "n_slots", "capit_slot_target_vnd")
    miss = [k for k in need if t.get(k) in (None, "")]
    if miss:
        return (f"artifact BẬT đòn bẩy nhưng `capit_slot_targets` thiếu thừa số để tự kiểm "
                f"{miss} — không đối chiếu được mục tiêu VND với NAV/cơ sở nào, KHÔNG cấp "
                f"đòn bẩy (fail-closed)")
    try:
        nav = float(t["nav_basis_vnd"]); w = float(t["w_lag_target"])
        size = float(t["capit_size"]); book = float(t["nav_book_lag_vnd"])
        tot = float(t["capit_total_target_vnd"]); n = int(t["n_slots"])
        slot = float(t["capit_slot_target_vnd"])
    except (TypeError, ValueError) as ex:
        return f"`capit_slot_targets` có trường không phải số ({ex}) — KHÔNG cấp đòn bẩy"
    if nav <= 0 or book <= 0 or tot <= 0 or slot <= 0 or n < 1:
        return (f"`capit_slot_targets` có giá trị ≤0 (nav={nav}, book={book}, total={tot}, "
                f"slot={slot}, n_slots={n}) — KHÔNG cấp đòn bẩy")
    # TRẦN NEO THEO STATE — thay trần phẳng (arch-reviewer vòng 3 #2: trần phẳng 1,0 = đúng
    # giá trị hợp lệ lớn nhất ⇒ không ràng buộc gì trên ngày NEUTRAL thường lệ).
    if st is not None and state_path is not None:
        s, s_err = _artifact_state(st, state_path)
        if s is None:
            return s_err
        # State lạ ⇒ TỪ CHỐI, không rơi về mặc định NEUTRAL (arch-reviewer vòng 4 #6): rơi về
        # mặc định nghĩa là `state=99` (khai khớp ở cả hai file) vẫn được trần của NEUTRAL.
        if s not in _CAPIT_BASE_BY_STATE or s not in _W_LAG_MAX_BY_STATE:
            return (f"state={s} không nằm trong bảng sizing đã biết "
                    f"{sorted(_CAPIT_BASE_BY_STATE)} — không có trần nào áp được, KHÔNG cấp "
                    f"đòn bẩy (fail-closed)")
        w_max = _W_LAG_MAX_BY_STATE[s]
        size_max = _CAPIT_BASE_BY_STATE[s]
        if not (0 < w <= w_max):
            return (f"w_lag_target={w} ngoài biên của state {s} (0; {w_max}] — thừa số này "
                    f"nhân thẳng vào vốn triển khai, giá trị lạ ⇒ KHÔNG cấp đòn bẩy")
        if not (0 < size <= size_max):
            return (f"capit_size={size} ngoài biên của state {s} (0; {size_max}] — "
                    f"`capit_size = capit_base(state) × grind` nên KHÔNG thể vượt "
                    f"capit_base({s})={size_max} ⇒ KHÔNG cấp đòn bẩy")
    elif not (0 < w <= 0.65) or not (0 < size <= 1.0):
        return (f"w_lag_target={w} / capit_size={size} ngoài biên cơ học — KHÔNG cấp đòn bẩy")

    def _off(a, b):
        """Lệch tương đối, chịu được làm tròn số nguyên của chính golive."""
        return abs(a - b) / max(abs(b), 1.0)

    if _off(book, nav * w) > 0.002:
        return (f"artifact TỰ MÂU THUẪN: nav_book_lag_vnd={book:,.0f} ≠ nav_basis_vnd "
                f"{nav:,.0f} × w_lag_target {w} = {nav * w:,.0f} — KHÔNG cấp đòn bẩy")
    if _off(tot, book * size) > 0.002:
        return (f"artifact TỰ MÂU THUẪN: capit_total_target_vnd={tot:,.0f} ≠ "
                f"nav_book_lag_vnd {book:,.0f} × capit_size {size} = {book * size:,.0f} — "
                f"đây ĐÚNG hình dạng của một lần sửa tay/regenerate hỏng, KHÔNG cấp đòn bẩy")
    if _off(slot, tot / n) > 0.002:
        return (f"artifact TỰ MÂU THUẪN: capit_slot_target_vnd={slot:,.0f} ≠ "
                f"capit_total_target_vnd {tot:,.0f} / n_slots {n} = {tot / n:,.0f} — "
                f"KHÔNG cấp đòn bẩy")
    # `n_slots` phải khớp rổ ĐẦY ĐỦ của phiên (`n_capit_basket`), KHÔNG phải số khoá
    # `capit_adv_caps` (arch-reviewer vòng 3 #4). Hai số này LỆCH NHAU một cách hợp lệ và
    # thường xuyên: `golive.capit_adv_caps()` bỏ mã thiếu `adv20` và tự in WARNING (mã đó bị
    # `cap_capit_orders` chặn riêng ở tầng dưới) trong khi `n_slots` vẫn chia theo rổ đầy đủ.
    # So với `len(basket)` thì một lỗ hổng dữ liệu ADV20 thường lệ — hay gặp đúng ở rổ washout,
    # nơi mã đang bị đình chỉ/thanh khoản cạn — sẽ TẮT đòn bẩy cả phiên và báo là "artifact TỰ
    # MÂU THUẪN", đẩy người trực đi điều tra giả mạo artifact cho một chuyện bình thường.
    if n_basket is not None and n != int(n_basket):
        return (f"artifact TỰ MÂU THUẪN: n_slots={n} ≠ n_capit_basket={n_basket} — mục tiêu/"
                f"slot đang chia theo một rổ KHÁC rổ CAPIT của phiên, KHÔNG cấp đòn bẩy")
    if basket and n < len(basket):
        return (f"artifact TỰ MÂU THUẪN: n_slots={n} NHỎ HƠN số mã có trần ADV trong rổ "
                f"({len(basket)}) — chia mục tiêu cho ít slot hơn số mã sẽ mua là chiều làm "
                f"slot TO ra, KHÔNG cấp đòn bẩy")
    return ""


def margin_day_approval(account_label, plan_date, approvals_dir=None):
    """CỔNG DUYỆT RIÊNG TỪNG NGÀY CÓ VAY (user chốt 2026-08-03) → (record, "") | (None, lý do).

    `capit_margin_lever.enabled=true` là ĐIỀU KIỆN CẦN (công tắc tổng, bật 1 lần) — user chốt
    thêm: MỖI NGÀY mà plan thực sự có lệnh được cấp đòn bẩy còn cần MỘT lần duyệt riêng cho
    ĐÚNG ngày đó. Bản ghi duyệt là file `data/margin_approvals/margin_approval_<account>_
    <plan_date>.json`, do `mike/bin/approve_margin_day.py` ghi khi user xác nhận thật.

    VÌ SAO KHÔNG dùng field trong chính file plan (như `approved_by` của plan-approval-gate):
    plan là JSON do LLM (DollarBill) sinh / người sửa tay — đặt cờ duyệt đòn bẩy vào đó là
    trao quyền duyệt cho nơi sinh plan, đúng cái mà `apply_capit_lever` tồn tại để chặn
    (coding_guidelines §7). File duyệt nằm NGOÀI plan, và không tầng sinh plan nào ghi nó.

    Fail-safe: thiếu/hỏng/không khớp ⇒ KHÔNG đòn bẩy (lệnh vẫn chạy bằng vốn tự có), KHÔNG
    chặn lệnh — under-deploy là sai số lành, vay không ai duyệt là tiền thật.
    """
    from .config import WORKDIR
    d = approvals_dir or os.path.join(WORKDIR, "data", "margin_approvals")
    path = os.path.join(d, f"margin_approval_{account_label}_{plan_date}.json")
    if not os.path.exists(path):
        return None, (f"CHƯA CÓ duyệt riêng cho ngày {plan_date} [{account_label}] "
                      f"({path}) — công tắc `enabled=true` là điều kiện CẦN, mỗi ngày có vay "
                      f"cần thêm 1 lần user duyệt riêng (mike/bin/approve_margin_day.py)")
    try:
        with open(path, encoding="utf-8") as f:
            rec = json.load(f) or {}
    except Exception as ex:
        return None, f"không đọc được bản ghi duyệt {path}: {type(ex).__name__}: {ex}"
    # Cờ THU HỒI đọc theo chiều NGƯỢC với cờ BẬT: `capit_lever_enabled` dùng `is True` (chỉ
    # đúng boolean mới bật được — fail-closed), còn ở đây BẤT KỲ giá trị lạ nào cũng phải
    # nghiêng về HUỶ. Lý do (arch-reviewer vòng 3 #3): đường thu hồi được thiết kế cho người
    # sửa gấp lúc 08:10, và người sửa tay JSON viết `"revoked": "true"` (chuỗi) hay `1` là
    # chuyện thường — với `is True` thì cả hai bị BỎ QUA im lặng và 09:05 vẫn vay. Một cờ huỷ
    # fail-OPEN là đúng thứ không được phép tồn tại trong bản ghi ủy quyền vay tiền.
    _rv = rec.get("revoked")
    if "revoked" in rec and _rv not in (False, None, "", 0, "false", "False", "no", "0"):
        return None, (f"bản ghi duyệt {plan_date} [{account_label}] đã bị THU HỒI "
                      f"(revoked={_rv!r}, lý do: {rec.get('revoked_reason') or 'không ghi'})")
    if str(rec.get("account") or "") != account_label:
        return None, (f"bản ghi duyệt ghi account={rec.get('account')!r} ≠ {account_label!r} "
                      f"— duyệt của account khác KHÔNG dùng chéo được")
    if str(rec.get("plan_date") or "") != str(plan_date):
        return None, (f"bản ghi duyệt ghi plan_date={rec.get('plan_date')!r} ≠ {plan_date!r} "
                      f"— duyệt của ngày khác KHÔNG dùng lại được (đổi tên file không đủ)")
    who = rec.get("approved_by")
    who = who.strip() if isinstance(who, str) else ""
    if who.lower() in APPROVAL_PLACEHOLDERS:
        return None, (f"bản ghi duyệt có approved_by={rec.get('approved_by')!r} — chưa phải "
                      f"một NGƯỜI duyệt thật (chuỗi giữ chỗ hoặc tên một tác nhân tự động)")
    if rec.get("lever_f") != CAPIT_LEVER_APPROVED_F:
        return None, (f"bản ghi duyệt ghi lever_f={rec.get('lever_f')!r} ≠ hệ số đã duyệt "
                      f"trong code {CAPIT_LEVER_APPROVED_F}")
    if rec.get("loan_package_id") != CAPIT_LEVER_APPROVED_PACKAGE:
        return None, (f"bản ghi duyệt ghi loan_package_id={rec.get('loan_package_id')!r} ≠ "
                      f"gói đã duyệt trong code {CAPIT_LEVER_APPROVED_PACKAGE}")
    try:
        cap = float(rec.get("max_lever_total_vnd"))
    except (TypeError, ValueError):
        cap = 0.0
    if cap <= 0:
        return None, (f"bản ghi duyệt thiếu/không hợp lệ `max_lever_total_vnd` "
                      f"({rec.get('max_lever_total_vnd')!r}) — không có trần thì bản duyệt "
                      f"không ràng buộc được điều gì")
    tickers = rec.get("tickers")
    if not isinstance(tickers, list) or not all(isinstance(x, str) and x for x in tickers) \
            or not tickers:
        return None, (f"bản ghi duyệt thiếu/không hợp lệ danh sách `tickers` "
                      f"({rec.get('tickers')!r}) — user duyệt một RỔ cụ thể, không duyệt khống")
    return rec, ""


def _enforce_margin_day_approval(plan, account_label, adj, approvals_dir=None):
    """Áp cổng duyệt-riêng-từng-ngày lên tập lệnh VỪA ĐƯỢC CẤP trong `adj` (sửa tại chỗ).

    Chạy SAU vòng cấp/gỡ của apply_capit_lever, ngay trong cùng hàm đó, để không có đường
    nào ra khỏi hàm với cờ vay mà chưa qua cổng này. Không khớp ⇒ GỠ SẠCH đòn bẩy của phiên
    (không chặn lệnh) + 1 dòng cấp-plan để log vận hành nói thẳng vì sao.
    """
    granted = [a for a in adj if a["action"] in ("APPLIED", "OVERRIDDEN")]
    if not granted:
        return
    rec, err = margin_day_approval(account_label, plan.plan_date, approvals_dir)
    if rec is not None:
        want = sum(float(a.get("value") or 0) for a in granted)
        cap = float(rec["max_lever_total_vnd"])
        approved_tk = set(rec["tickers"])
        extra = sorted({a["ticker"] for a in granted} - approved_tk)
        if extra:
            err = (f"plan cấp đòn bẩy cho mã {extra} KHÔNG có trong rổ user đã duyệt "
                   f"{sorted(approved_tk)} — rổ đổi sau khi duyệt thì phải duyệt lại")
        elif want > cap:
            err = (f"Σ giá trị lệnh được cấp đòn bẩy {want:,.0f} VND VƯỢT mức user đã duyệt "
                   f"{cap:,.0f} VND cho ngày {plan.plan_date} — duyệt lại nếu thật sự muốn "
                   f"tăng quy mô vay")
    if not err:
        return
    by_id = {o.id: o for o in plan.orders}
    for a in granted:
        o = by_id.get(a["order_id"])
        if o is not None:
            o.lever_f = None
            o.loan_package_id = None
        a["action"] = "DENIED"
        a["reason"] = (f"CỔNG DUYỆT RIÊNG NGÀY CÓ VAY: {err} — GỠ đòn bẩy, lệnh vẫn chạy "
                       f"bằng vốn tự có")
    adj.append({"ticker": "-", "order_id": "-", "action": "MARGIN_APPROVAL_REQUIRED",
                "lever_f": None, "loan_package_id": None,
                "reason": (f"{len(granted)} lệnh CAPIT ĐỦ điều kiện đòn bẩy nhưng KHÔNG có "
                           f"duyệt riêng hợp lệ cho ngày {plan.plan_date} [{account_label}]: "
                           f"{err}. Phiên này chạy bằng vốn tự có. Muốn có đòn bẩy: user xác "
                           f"nhận → Mike chạy `mike/bin/approve_margin_day.py --account "
                           f"{account_label} --date {plan.plan_date} --approved-by \"...\"` "
                           f"TRƯỚC 09:05.")})


def capit_lever_enabled(rules_path=None):
    """Công tắc BẬT/TẮT đọc từ `data/trading_rules.json` → (bật?, lý do nếu tắt).

    TÁCH RIÊNG khỏi artifact vì đây là công tắc VẬN HÀNH, và nó phải hoạt động ở thời điểm
    THỰC THI (arch-reviewer 2026-08-03, phát hiện F1). Chuỗi thời gian thật: golive công bố
    artifact ~19:03 → plan 21:00 → đặt lệnh 09:05 hôm sau. Nếu hàm cấp phép chỉ đọc artifact
    thì trong ~14h đó việc đặt `enabled=false` KHÔNG tắt được gì — công tắc duy nhất còn tác
    dụng sẽ là `BOT_STOP` (dừng toàn bộ giao dịch, quá tay). Đọc lại file chính sách ngay
    trước khi cấp cờ vay ⇒ tắt là tắt thật, ở mọi thời điểm.

    `is True`, KHÔNG `bool(...)`: `bool("false")` là True — một lỗi gõ có nháy sẽ BẬT đòn bẩy.
    Không đọc được file / thiếu khối ⇒ TẮT (fail-closed).
    """
    from .config import WORKDIR
    path = rules_path or os.path.join(WORKDIR, "data", "trading_rules.json")
    try:
        with open(path, encoding="utf-8") as f:
            blk = (json.load(f) or {}).get("capit_margin_lever") or {}
    except Exception as ex:
        return False, (f"không đọc được chính sách {path}: {type(ex).__name__}: {ex} — "
                       f"coi như TẮT")
    if not blk:
        return False, "trading_rules.json không có khối capit_margin_lever — coi như TẮT"
    if blk.get("enabled") is not True:
        return False, (f"capit_margin_lever.enabled={blk.get('enabled')!r} (không phải literal "
                       f"JSON true) — chính sách đòn bẩy ĐANG TẮT, cần user xác nhận riêng")
    return True, ""


def apply_capit_lever(plan, account_label, status_path=None, rules_path=None,
                      preview=False, approvals_dir=None, state_path=None):
    """ĐÒN BẨY MARGIN cho lệnh MUA book CAPIT — ĐÚNG MỘT CHỖ THỰC THI, cấp phép bởi artifact.

    CHÍNH SÁCH (user duyệt 2026-08-03, chuỗi nghiên cứu p1–p5 cùng ngày): vay margin CHỈ trên
    sleeve CAPIT, hệ số CỐ ĐỊNH f=1,3, cổng `dd52<=−20%`, gói vay DNSE 1840 "RocketX", CHỈ
    account SpaceX. Khai báo ở `data/trading_rules.json` → `capit_margin_lever`
    (**enabled=false** mặc định); tín hiệu của NGÀY do golive_recommend_v23.py công bố ở
    `data/golive_v23_status.json` → `capit_lever`.

    HAI CHIỀU, và chiều thứ hai mới là lý do hàm này tồn tại:
      · CẤP: lệnh mua book CAPIT được gắn `lever_f` + `loan_package_id` khi VÀ CHỈ KHI artifact
        nói `capit_lever.active=true` và account này nằm trong `capit_lever.accounts`.
      · GỠ: MỌI lệnh khác (khác book, khác chiều, account ngoài phạm vi, hoặc khi lever TẮT)
        bị XOÁ SẠCH hai field đó — kể cả khi plan tự ghi sẵn. Plan là JSON do LLM (DollarBill)
        sinh hoặc người sửa tay; một dòng `"loan_package_id": 1840` viết thẳng vào plan mà
        không có hàm này sẽ đi tới broker và tạo đòn bẩy KHÔNG AI DUYỆT. Cùng lý lẽ
        filter_excluded_tickers/cap_capit_orders tồn tại (coding_guidelines §7): quyền không
        nằm ở nơi sinh plan.

    FAIL-CLOSED mọi hướng: thiếu/hỏng artifact, artifact của signal_date khác plan, schema lạ,
    `active` không phải true, account ngoài danh sách, f<1 hoặc thiếu loan_package_id → KHÔNG
    cấp đòn bẩy (và vẫn GỠ cờ lạ). "Không vay được" chỉ làm hệ chạy đúng như V2.4 hôm nay;
    "vay nhầm" là tiền thật với rủi ro margin call — hai vế không cân nhau.

    KHÔNG đụng tới sizing/qty: số lượng do plan quyết định (tầng plan đọc
    `capit_slot_targets[<acct>].capit_slot_target_vnd_levered` mà golive đã tính sẵn), trần %ADV
    do cap_capit_orders() enforce TRƯỚC hàm này và KHÔNG nhân f (trần đo tác động thị trường,
    độc lập nguồn vốn). Hàm này chỉ quyết định lệnh đi ra broker bằng gói vay nào.

    Vị trí trong cascade (bot_execute.py): filter_excluded → net → cap_capit → cap_lag →
    lag_rating → **LEVER** → approval. Đặt CUỐI vì nó phải nhìn thấy tập lệnh chung cuộc: một
    lệnh bị các tầng trên loại thì không cần (và không được) gắn cờ vay.

    HAI CỔNG NGƯỜI, KHÔNG PHẢI MỘT (user chốt 2026-08-03): `capit_margin_lever.enabled=true`
    là công tắc TỔNG (bật 1 lần, cần user xác nhận riêng) — CẦN nhưng KHÔNG ĐỦ. Mỗi NGÀY mà
    hàm này thật sự cấp cờ vay cho ≥1 lệnh còn cần một bản ghi duyệt riêng cho ĐÚNG ngày đó
    (`margin_day_approval`, xem `_enforce_margin_day_approval` ở cuối hàm). Không có ⇒ gỡ
    sạch đòn bẩy của phiên, lệnh vẫn chạy bằng vốn tự có.

    Trả (plan đã sửa, list dict mô tả từng thay đổi) — KHÔNG log, caller tự báo.
    Mỗi dict: {"ticker","order_id","action","lever_f","loan_package_id","value","reason"}.

    `preview=True` — CHẾ ĐỘ XEM TRƯỚC cho bước duyệt (send_plan_report 21:00 và
    approve_margin_day.py) cần biết "nếu được duyệt thì những lệnh nào sẽ vay, bao nhiêu":
    bỏ qua ĐÚNG cổng duyệt-riêng-từng-ngày (nếu không thì vòng lặp chết — không xem trước
    được thứ đang chờ duyệt), giữ nguyên MỌI cổng còn lại. Để chế độ này không bao giờ trở
    thành đường vòng: hàm deepcopy plan NGAY DÒNG ĐẦU và trả `(None, adj)` — hàm KHÔNG TRẢ RA
    đối tượng plan nào mang cờ vay, kể cả khi caller gán lại biến, và cũng không ghi sổ
    `_lever_authorized`.
    ⚠️ Nó KHÔNG làm sạch plan mà caller TRUYỀN VÀO: một plan JSON tự ghi sẵn `lever_f`/
    `loan_package_id` thì sau lượt preview vẫn còn nguyên cờ đó trên đối tượng của caller
    (arch-reviewer vòng 3 #8). Hai caller hiện tại đều tự `load_plan` rồi vứt nên vô hại;
    caller mới PHẢI chạy lại `apply_capit_lever(...)` (không preview) trước khi thực thi —
    đừng dựa vào preview để "dọn" plan.
    """
    from .config import WORKDIR

    if preview:
        plan = copy.deepcopy(plan)

    def _is_capit_buy(o):
        return (o.book or "").upper() == "CAPIT" and (o.side or "").lower() == "buy"

    st, lever, err = {}, {}, None
    # CÔNG TẮC VẬN HÀNH đọc NGAY LÚC THỰC THI, độc lập với artifact (F1). Kiểm TRƯỚC tiên:
    # chính sách tắt thì không cần biết artifact nói gì.
    _pol_on, _pol_why = capit_lever_enabled(rules_path)
    if not _pol_on:
        err = _pol_why

    path = status_path or os.path.join(WORKDIR, "data", "golive_v23_status.json")
    if not err:
        try:
            with open(path, encoding="utf-8") as f:
                st = json.load(f)
            lever = st.get("capit_lever") or {}
            if not lever:
                err = ("artifact không có khối `capit_lever` (golive_recommend_v23.py bản cũ) — "
                       "KHÔNG áp đòn bẩy")
            # THIẾU signal_date ở BẤT KỲ bên nào ⇒ fail-closed (F6). Bản đầu chỉ so khi CẢ HAI
            # bên có giá trị, nên một plan không ghi signal_date sẽ chấp nhận artifact ở bất kỳ
            # tuổi nào. Với tiền vay, "không chứng minh được là tươi" phải đọc là "cũ".
            elif not st.get("signal_date") or not plan.signal_date:
                err = (f"không xác minh được độ tươi của artifact (signal_date artifact="
                       f"{st.get('signal_date')!r}, plan={plan.signal_date!r}) — KHÔNG áp đòn bẩy")
            elif st["signal_date"] != plan.signal_date:
                err = (f"golive_v23_status.json là của signal_date {st['signal_date']} ≠ plan "
                       f"{plan.signal_date} (artifact cũ) — KHÔNG áp đòn bẩy")
        except Exception as ex:
            err = f"không đọc được {path}: {type(ex).__name__}: {ex} — KHÔNG áp đòn bẩy"

    f_val = lever.get("f")
    lp_val = lever.get("loan_package_id")
    authorized = bool(
        not err
        and lever.get("active") is True
        and lever.get("scope") == "capit_only"
        and account_label in (lever.get("accounts") or [])
        and isinstance(f_val, (int, float)) and float(f_val) >= 1.0
        and lp_val is not None
    )
    # PHẠM VI DUYỆT ép ở CHÍNH tầng thực thi (F2) — không chỉ tin artifact. `f` và gói vay
    # quyết định ĐỘ LỚN khoản vay; artifact bị gitignore y như trading_rules.json, nên nếu
    # không so ở đây thì sửa một số trong artifact là đủ để vay vượt mức user duyệt.
    if authorized and (float(f_val) != CAPIT_LEVER_APPROVED_F
                       or lp_val != CAPIT_LEVER_APPROVED_PACKAGE
                       or account_label not in CAPIT_LEVER_APPROVED_ACCOUNTS):
        authorized = False
        err = (f"artifact LỆCH phạm vi user duyệt (f={f_val!r} ≠ {CAPIT_LEVER_APPROVED_F}, "
               f"gói={lp_val!r} ≠ {CAPIT_LEVER_APPROVED_PACKAGE}, account={account_label!r} "
               f"∉ {CAPIT_LEVER_APPROVED_ACCOUNTS}) — KHÔNG áp đòn bẩy; nới phạm vi phải sửa "
               f"CODE (trading_bot/plan.py), không sửa JSON")
    if not authorized and not err:
        if lever.get("active") is not True:
            err = (f"capit_lever.active={lever.get('active')!r} — {lever.get('reason') or 'lever TẮT'}")
        elif account_label not in (lever.get("accounts") or []):
            err = (f"account '{account_label}' KHÔNG trong phạm vi duyệt "
                   f"{lever.get('accounts')} — KHÔNG áp đòn bẩy")
        else:
            err = (f"tham số lever không hợp lệ (f={f_val!r}, loan_package_id={lp_val!r}, "
                   f"scope={lever.get('scope')!r}) — KHÔNG áp đòn bẩy")

    # RỔ CAPIT của phiên, theo account — `capit_adv_caps[<acct>]` là {mã: trần VND}. Kiểm
    # thành viên rổ NGAY TẠI ĐÂY (F5): tính chất "chỉ mã trong rổ" trước đây chỉ đúng nhờ
    # cap_capit_orders() chạy TRƯỚC trong cascade — một hợp đồng ngầm theo thứ tự gọi ở
    # bot_execute.py, không có gì trong hàm này bảo đảm. Hàm cấp quyền vay tiền phải tự đủ.
    basket = set()
    if authorized:
        basket = set((st.get("capit_adv_caps") or {}).get(account_label) or {})
        if not basket:
            authorized = False
            err = (f"artifact BẬT đòn bẩy nhưng `capit_adv_caps.{account_label}` rỗng — không "
                   f"xác định được rổ CAPIT của phiên, KHÔNG áp đòn bẩy (fail-closed)")

    # TÍNH NHẤT QUÁN NỘI TẠI của mục tiêu VND — thu hẹp khe "sửa ĐỒNG BỘ hai trường" mà vòng 2
    # còn để mở (xem docstring _verify_targets_integrity). Đặt TRƯỚC _anchored_cap vì mốc neo
    # của nó chỉ có nghĩa khi trường GỐC còn giải thích được bằng NAV × w_lag × capit_size.
    if authorized:
        _int_err = _verify_targets_integrity(
            (st.get("capit_slot_targets") or {}).get(account_label) or {}, basket,
            st=st, n_basket=st.get("n_capit_basket"),
            state_path=state_path or os.path.join(WORKDIR, *GOLIVE_STATE_TODAY_REL))
        if _int_err:
            authorized = False
            err = _int_err

    # TRẦN VND cho quyền vay (arch-reviewer 2026-08-03). "Được vay" mà không kèm trần khối
    # lượng là đúng hình dạng bug 07-21 (nhân capit_size hai lần, thiếu 87,1tr) — chỉ khác
    # là với gói 1840 (initialRate 0,5 ⇒ sức mua gấp đôi, Mafee đo 2026-08-03) một sai số
    # sizing của tầng sinh plan (DollarBill là LLM) sẽ bị chặn bởi 2× SỨC MUA thay vì bởi
    # tiền mặt. `cap_capit_orders` chỉ chặn %ADV/mã, KHÔNG chặn mục tiêu vốn — nên trần
    # phải nằm ở đây. Vượt trần ⇒ GỠ đòn bẩy (lệnh vẫn chạy, chỉ bằng vốn tự có), KHÔNG
    # huỷ lệnh: under-deploy là sai số lành, vay quá mức là rủi ro margin call.
    # ĐỆM: tách per-order và TỔNG (arch-reviewer vòng 2, phát hiện #5). Một lệnh cần đệm
    # thật vì làm tròn lô 100 trên slot ~65tr đã là ~7,7%; còn TỔNG thì không — sai số làm
    # tròn của N lệnh triệt tiêu lẫn nhau, nên giữ 1,10 ở tầng tổng biến envelope f=1,3
    # thành 1,43 trên thực tế (đo thật: 6 lệnh × 71,5tr = 357,5tr trên trần tổng 325tr).
    LEVER_VALUE_TOL = 1.10          # per-order: đệm làm tròn lô + giá nhích so với ref
    LEVER_TOTAL_TOL = 1.02          # tổng: chỉ đệm sai số làm tròn, KHÔNG nới envelope

    # TRẦN VND cho quyền vay — NEO VÀO TRƯỜNG GỐC, không tin số levered của artifact
    # (arch-reviewer vòng 2, phát hiện #1 — lỗ hổng CAO, đã probe hỏng thật).
    #
    # Bản đầu đọc thẳng `capit_*_target_vnd_levered` từ artifact. Nhưng đó CHÍNH LÀ file mà
    # F2 tuyên bố là không đáng tin (khớp `.gitignore:12 *.json` ⇒ không diff, không blame,
    # không backup). Envelope ghim trong code chỉ ép f / gói vay / account — tức là ép
    # *tỷ lệ*, KHÔNG ép *độ lớn*. Probe của arch-reviewer: để nguyên `f: 1.3` (khớp hằng
    # CAPIT_LEVER_APPROVED_F, qua sạch mọi cổng envelope), chỉ sửa hai trường VND ⇒ được
    # cấp đòn bẩy cho 10.000.000.000 VND trên một mốc 325.000.000 VND — vượt 30,8 lần.
    # F2 đóng cửa trước thì F4 mở cửa sau, cùng một file.
    #
    # Sửa: trần = min(số artifact tự khai, TRƯỜNG GỐC chưa nhân f × f ĐÃ DUYỆT TRONG CODE).
    # Trường gốc (`capit_total_target_vnd`) nằm ngay trong cùng dict và được tính từ NAV
    # book LAG × capit_size — sửa nó cũng làm sai lệch mọi con số CAPIT khác trong artifact
    # (báo cáo duyệt plan, cổng WARN 07-21 ở send_plan_report.sh), nên nó không phải là chỗ
    # sửa lén được. Nhân bằng CAPIT_LEVER_APPROVED_F chứ KHÔNG bằng `f_val` của artifact:
    # dùng f_val thì artifact lại tự nhân cho chính mình, quay về đúng lỗ hổng cũ.
    # Thiếu trường gốc ⇒ fail-closed (không có mốc độc lập nào để soi ⇒ không cấp đòn bẩy).
    def _anchored_cap(levered_key, base_key, tol):
        """→ (trần VND, lý do fail-closed nếu None)."""
        if err:
            return None, ""
        t = (st.get("capit_slot_targets") or {}).get(account_label) or {}
        base, lev = t.get(base_key), t.get(levered_key)
        if not base:
            return None, (f"artifact BẬT đòn bẩy nhưng thiếu trường GỐC `capit_slot_targets."
                          f"{account_label}.{base_key}` — không có mốc độc lập nào để soi trần "
                          f"vay, KHÔNG cấp đòn bẩy (fail-closed)")
        if not lev:
            return None, (f"artifact BẬT đòn bẩy nhưng thiếu `capit_slot_targets."
                          f"{account_label}.{levered_key}` — không có trần VND nào để soi khối "
                          f"lượng, KHÔNG cấp đòn bẩy (fail-closed)")
        anchored = float(base) * CAPIT_LEVER_APPROVED_F
        if float(lev) > anchored * 1.001:      # 0,1% cho làm tròn của chính golive
            return anchored * tol, (
                f"artifact khai `{levered_key}`={float(lev):,.0f} VƯỢT mốc neo "
                f"{anchored:,.0f} (= gốc {float(base):,.0f} × f duyệt "
                f"{CAPIT_LEVER_APPROVED_F}) — dùng mốc NEO, bỏ số artifact tự khai")
        return float(lev) * tol, ""

    slot_cap, slot_cap_err = _anchored_cap(
        "capit_slot_target_vnd_levered", "capit_slot_target_vnd", LEVER_VALUE_TOL)
    # TRẦN TỔNG (F4). Trần slot ở trên là PER-ORDER, và `cap_capit_orders` cũng per-order,
    # còn `Executor.state["parents"]` khoá theo `o.id` chứ không theo mã — nên N lệnh trùng
    # mã, mỗi lệnh vừa đúng trần slot, sẽ chạy CẢ N. Đo thật (arch-reviewer probe P4): 4 lệnh
    # × 65tr = 260tr được cấp đòn bẩy trên một slot levered 65tr. Với gói 1840 (initialRate
    # 0,5) ràng buộc chặn cuối cùng là 2× SỨC MUA chứ không phải tiền mặt ⇒ phải có trần tổng.
    total_cap, total_cap_err = _anchored_cap(
        "capit_total_target_vnd_levered", "capit_total_target_vnd", LEVER_TOTAL_TOL)
    lever_spent = 0.0

    adj = []
    for o in plan.orders:
        had = (o.lever_f is not None) or (o.loan_package_id is not None)
        # cash_only đi với bộ giải gói vay THEO MÃ (bug TV1 07-28) — hai cơ chế chọn gói vay
        # không được chồng lên nhau; CAPIT không bao giờ cash_only, nên đây là kiểm tra phòng xa.
        eligible = authorized and _is_capit_buy(o) and not getattr(o, "cash_only", False)
        # Lý do từ chối RIÊNG của lệnh này — KHÔNG ghi đè `err` (thông điệp cấp-plan dùng
        # chung cho mọi lệnh; sửa nó trong vòng lặp sẽ rò lý do của mã này sang mã sau).
        deny = ""
        # `slot_cap`/`total_cap` ĐÃ gồm đệm tolerance (tính trong _anchored_cap) — KHÔNG
        # nhân lại ở đây, nếu không đệm sẽ được áp hai lần.
        if eligible and slot_cap is None:
            eligible, deny = False, slot_cap_err
        elif eligible and o.value > slot_cap:
            eligible, deny = False, (
                f"giá trị lệnh {o.value:,.0f} VND vượt trần vay {slot_cap:,.0f} "
                f"(mốc neo = slot gốc × f duyệt {CAPIT_LEVER_APPROVED_F} × đệm "
                f"{LEVER_VALUE_TOL}) — GỠ đòn bẩy, lệnh vẫn chạy bằng vốn tự có")
        elif eligible and o.ticker not in basket:
            eligible, deny = False, (
                f"{o.ticker} KHÔNG thuộc rổ CAPIT của phiên ({sorted(basket)}) — GỠ đòn bẩy. "
                f"Lệnh mang nhãn book CAPIT nhưng không có trong rổ artifact công bố là mâu "
                f"thuẫn dữ liệu, không phải cơ sở để vay tiền")
        elif eligible and total_cap is None:
            eligible, deny = False, total_cap_err
        elif eligible and (lever_spent + o.value) > total_cap:
            eligible, deny = False, (
                f"tổng lệnh đã cấp đòn bẩy {lever_spent:,.0f} + lệnh này {o.value:,.0f} = "
                f"{lever_spent + o.value:,.0f} VND vượt trần TỔNG {total_cap:,.0f} "
                f"(mốc neo = tổng gốc × f duyệt {CAPIT_LEVER_APPROVED_F} × đệm "
                f"{LEVER_TOTAL_TOL}) — GỠ đòn bẩy lệnh này, lệnh vẫn chạy bằng vốn tự có")
        if eligible:
            lever_spent += o.value
            if had and (o.lever_f != float(f_val) or o.loan_package_id != lp_val):
                adj.append({"ticker": o.ticker, "order_id": o.id, "action": "OVERRIDDEN",
                            "lever_f": float(f_val), "loan_package_id": lp_val,
                            "value": o.value,
                            "reason": f"plan ghi sẵn (f={o.lever_f!r}, lp={o.loan_package_id!r}) "
                                      f"— ghi đè bằng giá trị của artifact"})
            else:
                adj.append({"ticker": o.ticker, "order_id": o.id, "action": "APPLIED",
                            "lever_f": float(f_val), "loan_package_id": lp_val,
                            "value": o.value,
                            "reason": f"CAPIT buy, cổng {lever.get('gate')} đạt "
                                      f"(dd52={lever.get('dd52_pct')}%)"})
            o.lever_f = float(f_val)
            o.loan_package_id = lp_val
            continue
        if deny:
            # Lệnh ĐÁNG LẼ được cấp nhưng bị trần VND chặn. Ghi lại KỂ CẢ khi lệnh không có
            # cờ sẵn để gỡ: nếu im lặng thì một plan sizing sai sẽ chạy như một phiên
            # CAPIT bình thường và không ai biết đòn bẩy đã bị rút khỏi nó.
            adj.append({"ticker": o.ticker, "order_id": o.id, "action": "DENIED",
                        "lever_f": o.lever_f, "loan_package_id": o.loan_package_id,
                        "reason": deny})
            o.lever_f = None
            o.loan_package_id = None
            continue
        if had:
            adj.append({"ticker": o.ticker, "order_id": o.id, "action": "STRIPPED",
                        "lever_f": o.lever_f, "loan_package_id": o.loan_package_id,
                        "reason": (err if not authorized else
                                   f"lệnh {o.side}/{o.book or '?'}"
                                   f"{'/cash_only' if getattr(o, 'cash_only', False) else ''} "
                                   f"KHÔNG thuộc phạm vi đòn bẩy (chỉ CAPIT buy)")})
            o.lever_f = None
            o.loan_package_id = None

    # CỔNG NGƯỜI THỨ HAI — duyệt riêng cho ĐÚNG ngày có vay (user chốt 2026-08-03). Đặt ở
    # ĐÂY, trong cùng hàm cấp phép, chứ không ở một tầng khác: mọi đường ra khỏi hàm này với
    # cờ vay đều phải đi qua nó. `preview` bỏ qua đúng cổng này (và chỉ cổng này) để bước
    # duyệt xem trước được tập lệnh đang chờ duyệt — an toàn vì preview chạy trên bản sao và
    # trả về `None` thay cho plan (xem docstring).
    if not preview:
        _enforce_margin_day_approval(plan, account_label, adj, approvals_dir)

    # ── SỔ "ĐÃ ĐƯỢC CẤP PHÉP" cho lưới an toàn tầng lệnh ────────────────────────────────
    # Executor._lever_package_audit hỏi "mã này có được cấp phép đòn bẩy hôm nay không" và
    # trước đây suy ra câu trả lời từ CHÍNH `o.loan_package_id` của plan. Điều đó SAI kể từ
    # khi `lever_live_preflight` tồn tại: nó GỠ cờ vay ở lượt chạy sau (13:00 ICT, cron
    # "khởi động lại sau nghỉ trưa" — có thật trong crontab), trong khi các lệnh gói 1840 của
    # lượt 09:05 VẪN nằm trên sổ broker. Audit khi đó thấy "đòn bẩy trên mã không được cấp
    # phép" và PAUSE cả rổ CAPIT suốt buổi chiều kèm một sự cố NÓI SAI — trong khi đòn bẩy đó
    # đã qua ĐỦ CẢ HAI cổng người sáng hôm ấy (arch-reviewer vòng 3 #1, probe tái lập được).
    #
    # Tách hai khái niệm: `o.loan_package_id` = "lệnh này ĐI RA bằng gói vay nào" (preflight
    # được phép hạ về None), còn sổ dưới đây = "hôm nay ai ĐÃ ĐƯỢC CẤP PHÉP vay" (chỉ hàm này
    # ghi, sau khi qua mọi cổng kể cả duyệt-ngày; preflight KHÔNG được đụng). Đặt trên đối
    # tượng plan RUNTIME, không phải field dataclass: `load_plan` lọc theo field khai báo
    # (plan.py:143/150) nên một plan JSON tự ghi `_lever_authorized` KHÔNG thể chạm tới nó —
    # nếu để dạng field thì chính nó thành đường qua mặt lưới an toàn cuối cùng.
    if not preview:
        _granted = {}
        for a in adj:
            if a["action"] in ("APPLIED", "OVERRIDDEN") and a.get("loan_package_id") is not None:
                _granted.setdefault(str(a["loan_package_id"]), set()).add(a["ticker"])
        # HỢP với sổ ĐÃ GHI RA ĐĨA của phiên (arch-reviewer vòng 4 #3). Sổ chỉ nằm trong RAM
        # là trạng thái một tiến trình cho một sự kiện đã xảy ra THẬT ngoài hệ (lệnh gói 1840
        # nằm trên sổ broker) — đúng cái coding_guidelines §5 cấm. Lượt 13:00 là tiến trình
        # MỚI: nếu hàm này từ chối vì BẤT KỲ lý do gì (người vận hành tắt `enabled=false` giữa
        # phiên, `--revoke`, artifact publish lại), sổ RAM rỗng ⇒ audit lại dựng đúng sự cố
        # GIẢ mà vòng 3 vừa đóng, và unpause chỉ bằng tay sửa JSON. Đọc file ⇒ lượt sau kế
        # thừa được sự thật "sáng nay ai đã được cấp".
        plan._lever_authorized, plan._lever_ledger_prior = _lever_ledger_merge(
            account_label, plan.plan_date, _granted)

    # KHÔNG ĐƯỢC IM LẶNG khi plan đã sizing theo đòn bẩy mà thực thi lại không có đòn bẩy
    # (arch-reviewer vòng 2, phát hiện #3a). Kịch bản thật: golive công bố artifact có đòn
    # bẩy lúc ~19:03, plan sizing 1,3× lúc 21:00, rồi người vận hành đặt `enabled=false`
    # trong đêm (đúng cái công tắc F1 vừa tạo ra). Sáng hôm sau các lệnh KHÔNG mang cờ vay
    # sẵn nên vòng lặp trên không có gì để "GỠ" ⇒ `adj` rỗng ⇒ bot_execute.py in 0 dòng.
    # Hệ vào phiên với khối lượng tính cho 1,3× vốn nhưng chỉ có 1,0× vốn, và triệu chứng
    # duy nhất là WAIT_CASH "thiếu tiền" — không phân biệt được với thiếu tiền bình thường.
    # Ghi 1 dòng cấp-plan để người đọc log thấy NGAY nguyên nhân.
    if not authorized:
        try:
            # ĐỌC LẠI artifact ở đây: khi công tắc chính sách TẮT, `err` được đặt TRƯỚC khi
            # mở artifact nên `st` còn rỗng — chính là ca kiểm C30 bắt được. Cảnh báo này
            # cần biết artifact có mục tiêu đã nhân f hay không, nên phải tự đọc.
            _st = st
            if not _st:
                with open(path, encoding="utf-8") as _f:
                    _st = json.load(_f) or {}
            _t = (_st.get("capit_slot_targets") or {}).get(account_label) or {}
            if _t.get("capit_slot_target_vnd_levered") and any(_is_capit_buy(o)
                                                               for o in plan.orders):
                adj.append({"ticker": "-", "order_id": "-", "action": "PLAN_SIZED_LEVERED_BUT_OFF",
                            "lever_f": None, "loan_package_id": None,
                            "reason": (
                                f"artifact CÓ mục tiêu đã nhân f "
                                f"(`capit_slot_target_vnd_levered`="
                                f"{float(_t['capit_slot_target_vnd_levered']):,.0f} VND/mã) nhưng "
                                f"đòn bẩy KHÔNG được cấp: {err}. Lệnh CAPIT có thể đã được sizing "
                                f"theo mục tiêu ĐÃ NHÂN f trong khi chỉ có vốn tự có — chờ đợi "
                                f"WAIT_CASH/khớp thiếu là HẬU QUẢ của việc này, không phải thiếu "
                                f"tiền bất thường. Muốn dừng đòn bẩy GIỮA PHIÊN thì dùng "
                                f"`data/BOT_STOP` (dừng hẳn), không dùng `enabled=false` (chỉ đổi "
                                f"cấp vốn, không đổi khối lượng plan đã chốt).")})
        except Exception:
            pass

    # ARTIFACT NÓI ĐÒN BẨY ĐANG BẬT MÀ TA TỪ CHỐI — luôn để lại đúng 1 dòng, kể cả khi không
    # có cờ nào để "GỠ" và không có mục tiêu levered để cảnh báo sizing (ca artifact thiếu
    # `capit_slot_targets`, thiếu thừa số, tự mâu thuẫn…). Trước đây những ca đó fail-closed
    # ĐÚNG nhưng IM LẶNG: một artifact hỏng trông y hệt một ngày không có sự kiện CAPIT.
    # Điều kiện `active is True` giữ log vận hành thường lệ sạch: ngày chính sách tắt/không có
    # washout thì artifact không claim gì, và hàm này vẫn trả 0 dòng như trước.
    if (not authorized and lever.get("active") is True
            and not any(a["ticker"] == "-" for a in adj)
            and any(_is_capit_buy(o) for o in plan.orders)):
        adj.append({"ticker": "-", "order_id": "-", "action": "LEVER_REFUSED_ARTIFACT_ACTIVE",
                    "lever_f": None, "loan_package_id": None, "value": 0,
                    "reason": (f"artifact công bố `capit_lever.active=true` nhưng KHÔNG cấp "
                               f"được đòn bẩy: {err}. Phiên chạy bằng vốn tự có — đúng chiều "
                               f"an toàn, nhưng đây là DỮ LIỆU HỎNG cần người xem, không phải "
                               f"một ngày bình thường không có sự kiện.")})
    return (None if preview else plan), adj


def preview_margin_day(account_label, plan_date, status_path=None, rules_path=None,
                       state_path=None):
    """"Nếu được duyệt thì phiên {plan_date} sẽ vay những gì" → dict, dùng CHUNG cho:
      · `mike/bin/send_plan_report.sh` — nêu bật trong báo cáo user duyệt (~21:00);
      · `mike/bin/approve_margin_day.py` — ghi ĐÚNG rổ + trần đó vào bản ghi duyệt;
      · `capit_lever_selfcheck.py` nhóm I.
    Một nguồn duy nhất ⇒ số user NHÌN THẤY lúc duyệt == số bị ràng buộc lúc thực thi; hai
    bản sao công thức là cách chắc chắn nhất để hai con số trôi khỏi nhau.

    Chạy `apply_capit_lever(preview=True)`: đủ MỌI cổng (chính sách, envelope code, rổ, trần
    VND neo, nhất quán artifact) trừ đúng cổng duyệt-riêng-từng-ngày — thứ đang chờ user.

    `total_vnd` là CẬN TRÊN: preview chạy trên plan THÔ, chưa qua trần %ADV `cap_capit_orders`
    (áp lúc thực thi và chỉ cắt xuống). Σ thật lúc 09:05 ≤ số này ⇒ trần trong bản ghi duyệt
    không bao giờ chặn oan một plan không đổi.
    """
    plan = load_plan(plan_date, account=account_label)
    out = {"account": account_label, "plan_date": plan_date, "orders": [], "tickers": [],
           "total_vnd": 0.0, "borrow_vnd": 0.0, "lever_f": None, "loan_package_id": None,
           "reasons": [], "error": ""}
    if plan is None:
        out["error"] = f"không có file plan_{account_label}_{plan_date}.json"
        return out
    _, adj = apply_capit_lever(plan, account_label, status_path=status_path,
                               rules_path=rules_path, preview=True, state_path=state_path)
    granted = [a for a in adj if a["action"] in ("APPLIED", "OVERRIDDEN")]
    out["reasons"] = [a["reason"] for a in adj
                      if a["action"] in ("DENIED", "STRIPPED", "PLAN_SIZED_LEVERED_BUT_OFF")]
    if not granted:
        return out
    out["orders"] = [{"order_id": a["order_id"], "ticker": a["ticker"],
                      "value_vnd": float(a.get("value") or 0)} for a in granted]
    out["tickers"] = sorted({a["ticker"] for a in granted})
    out["total_vnd"] = sum(o["value_vnd"] for o in out["orders"])
    out["lever_f"] = granted[0]["lever_f"]
    out["loan_package_id"] = granted[0]["loan_package_id"]
    f = float(out["lever_f"] or 1.0)
    # Phần VƯỢT trên vốn tự có mới là tiền VAY (lever_formula của golive): với f=1,3 thì
    # 1 − 1/1,3 = 23,1% giá trị lệnh.
    out["borrow_vnd"] = out["total_vnd"] * (1 - 1 / f) if f > 0 else 0.0
    return out


def _lever_ledger_path(account_label, plan_date, exec_dir=None):
    from .config import EXEC_DIR
    return os.path.join(exec_dir or EXEC_DIR,
                        f"exec_{account_label}_{plan_date}_lever_authorized.json")


def _lever_ledger_merge(account_label, plan_date, granted, exec_dir=None):
    """Sổ "hôm nay ai ĐÃ ĐƯỢC CẤP PHÉP vay" — hợp `granted` vào sổ trên đĩa → dict đã hợp.

    Cùng vòng đời với `exec_<account>_<date>_state.json` (một phiên = một cặp file), ghi
    NGUYÊN TỬ (§5). CỐ Ý **không** khoá theo `plan_created_at`: nếu plan được phát hành lại
    giữa ngày, các lệnh gói 1840 đã đi ra dưới plan cũ vẫn là lệnh THẬT và vẫn đã được cấp
    phép hợp lệ — audit tầng lệnh phải tiếp tục biết điều đó, nếu không ta lại dựng sự cố giả.
    (Khác `_session_already_placed`, vốn hỏi "phiên đang chạy có biết đúng những lệnh vay này
    chưa" nên PHẢI khoá theo vân tay nội dung — tập id lệnh vay; xem docstring hàm đó.)

    Ranh giới tin cậy: ai ghi được file này thì cũng ghi được `state.json` — cùng thư mục,
    cùng mức quyền, và `state.json` đã là chân lý của lưới chống double-buy từ trước. Đây
    không mở rộng bề mặt tấn công, chỉ dùng lại đúng bề mặt sẵn có.

    ĐỌC CÓ LỌC (arch-reviewer vòng 5 #2): chỉ nhận đúng gói vay đã duyệt trong code, và ép
    kiểu chặt. Sổ là đầu vào ngoài tiến trình, mà `_lever_package_audit` bơm thẳng khoá của
    nó vào tập `packages` nó đi soi — một sổ hỏng mang khoá 1841 (gói DEFAULT của account) làm
    guard bắt đầu soi MỌI lệnh BAL/LAG thường lệ và pause sạch cả phiên (probe đo được:
    `pause=['FPT','SAB']`). Lọc 1 dòng, bán kính nổ về 0. Ép kiểu vì `set("SAB")` cho ra
    `{'S','A','B'}` nếu ai đó ghi value là chuỗi thay vì list.

    Trả (dict đã hợp, dict nội dung TRƯỚC khi hợp) — cái sau để `_strip` biết phần nào do
    CHÍNH tiến trình này cấp mà thu hồi, phần nào là của lệnh tiến trình trước đã đặt thật.
    """
    path = _lever_ledger_path(account_label, plan_date, exec_dir)
    ok_lp = str(CAPIT_LEVER_APPROVED_PACKAGE)
    prior = {}
    try:
        with open(path, encoding="utf-8") as f:
            for lp, tks in ((json.load(f) or {}).get("granted") or {}).items():
                if str(lp) != ok_lp:
                    continue
                if isinstance(tks, str):
                    tks = [tks]
                prior[str(lp)] = {str(t) for t in (tks or [])}
    except Exception:
        pass
    out = {lp: set(tks) for lp, tks in prior.items()}
    for lp, tks in (granted or {}).items():
        if str(lp) != ok_lp:
            continue
        out.setdefault(str(lp), set()).update(str(t) for t in tks)
    _lever_ledger_write(path, out)
    return out, prior


def _lever_ledger_write(path, granted):
    """Ghi sổ, nguyên tử. KHÔNG raise (sổ hỏng không được làm chết phiên) nhưng PHẢI nói ra.

    Câm ở đây là fail-silent thật (arch-reviewer vòng 5 #4): ghi hỏng ⇒ lượt 13:00 mất phần
    kế thừa ⇒ dựng lại đúng sự cố giả mà sổ này sinh ra để chặn, mà không một dòng nào giải
    thích vì sao. Hàm chạy trong ngữ cảnh stdout được ghi vào log run_bot nên `print` là đủ.

    Sổ RỖNG thì KHÔNG tạo file mới (vòng 5 #3): tính năng đang TẮT vẫn chạy qua đây mỗi phiên
    trên MỌI account, tạo ~2 file rỗng/ngày trong `data/execution_logs/` mà không ai sở hữu
    vòng đời. File đã tồn tại thì vẫn ghi (để `_strip` thu hồi được về rỗng).
    """
    try:
        if not granted and not os.path.exists(path):
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"granted": {lp: sorted(tks) for lp, tks in granted.items()}}, f,
                      ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception as ex:
        print(f"⚠ KHÔNG ghi được sổ cấp phép đòn bẩy {path} ({type(ex).__name__}: {ex}) — "
              f"lượt chạy sau trong CÙNG phiên sẽ không kế thừa được tập mã đã cấp, và lưới "
              f"an toàn tầng lệnh có thể báo 'đòn bẩy không ai duyệt' NHẦM cho lệnh hợp lệ.")


def _session_already_placed(account_label, plan_date, order_ids=None, exec_dir=None):
    """Phiên đang chạy đã đặt lệnh con nào chưa, VÀ nó có biết đúng những lệnh này không
    → (bool, mô tả ngắn).

    Đọc CHÍNH file state mà `Executor` sẽ load (`exec_<account>_<date>_state.json`,
    executor.py:78-79) — nguồn duy nhất ghi lại "lệnh đã thật sự đi ra", cập nhật ngay sau
    mỗi `place_order` (coding_guidelines §5). Không đọc được ⇒ coi như CHƯA đặt: đó là chiều
    thận trọng (preflight giữ toàn quyền GỠ, tức không cấp đòn bẩy).

    ── VÂN TAY NỘI DUNG, KHÔNG PHẢI `created_at` (vòng 6, rủi ro dư #1 của §11.10) ──────────
    Bản trước khoá theo `plan_created_at` cho khớp `Executor._load_state` (executor.py:202).
    Kiểm artifact THẬT cho thấy đó là **code chết trên đường production**: không plan
    `data/trade_plans/plan_*.json` nào do DollarBill/người sinh có khoá `created_at` (chỉ
    `TradePlan.save()` mới điền, mà production không đi qua đường đó) ⇒ `plan.created_at ==
    ""` và state cũng ghi `plan_created_at: ""` ⇒ so sánh `"" == ""` LUÔN khớp ⇒ nhánh này
    luôn trả `started=True`, tức lưới "phát hiện plan phát hành lại giữa ngày" CHƯA BAO GIỜ
    kích hoạt thật, dù fixture có `created_at` kiểm rất kỹ.

    Thay bằng thứ plan thật LUÔN có: **tập id lệnh** (`order_ids`, caller truyền tập id của
    đúng những lệnh đang mang cờ vay). Điều kiện `started` = state có ≥1 lệnh con đã đặt VÀ
    **mọi** id trong `order_ids` đã có mặt trong `state["parents"]` — tức phiên đang chạy đã
    biết đúng những lệnh này. Một lệnh vay MỚI xuất hiện giữa ngày (id chưa từng có trong
    state) ⇒ `started=False` ⇒ preflight GỠ như phiên sạch, đúng ý đồ ban đầu.

    Vì sao SO SÁNH BAO HÀM (`⊆`) chứ không BẰNG NHAU: một fail-safe phía trên (`cap_capit_orders`,
    `filter_lag_rating_orders`…) có thể loại bớt lệnh giữa hai lượt chạy — plan v2 NHỎ hơn
    state không sinh khoản vay mới nào nên không phải rủi ro, mà bắt bằng-nhau ở đó sẽ GỠ oan
    đòn bẩy hợp lệ buổi chiều. Chỉ chiều THÊM lệnh mới là chiều nguy hiểm.

    Vì sao được phép LỆCH khỏi `Executor._load_state` (nới ràng buộc vòng 4 #2): hai bên chỉ
    cần khớp ở MỘT chiều — chiều "Executor chạy phiên SẠCH mà ta lại tưởng đã đặt lệnh", vì
    chỉ chiều đó mới cho lệnh vay mới đi ra với WARN. Vân tay nội dung **chặt hơn hoặc bằng**
    quyết định resume của Executor trên mọi đầu vào (Executor `""==""` → resume; ta còn đòi
    thêm id khớp), nên chiều nguy hiểm là bất khả; chiều còn lại (`started=False` trong khi
    Executor resume) chỉ dẫn tới GỠ đòn bẩy = chạy vốn tự có = under-deploy, "sai số lành"
    đúng nguyên tắc fail-safe của cả module này.

    Giới hạn còn lại, có chủ đích: đổi RIÊNG `qty` mà giữ nguyên id (`BUY-SAB-01`) thì vân tay
    này không thấy — state của Executor không lưu qty ở tầng parent, và bắt nó lưu thêm sẽ
    phải sửa cả bên ghi (ngoài phạm vi 1 điểm). Quy mô của ca đó bị chặn bởi cổng người thứ
    hai: `_enforce_margin_day_approval` so Σ VND của LỆNH THẬT với trần `max_lever_total_vnd`
    trong bản duyệt của đúng ngày ⇒ qty phình lên quá trần thì GỠ SẠCH cờ vay trước khi tới
    đây. Ghi lại ở §12 báo cáo wiring, không phải chỗ chưa ai nghĩ tới.
    """
    from .config import EXEC_DIR
    d = exec_dir or EXEC_DIR
    path = os.path.join(d, f"exec_{account_label}_{plan_date}_state.json")
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f) or {}
    except Exception:
        return False, ""
    if order_ids is not None:
        known = set((st.get("parents") or {}))
        new_ids = {str(i) for i in order_ids} - known
        if new_ids:
            return False, ""
    n_child = sum(len(p.get("children") or []) for p in (st.get("parents") or {}).values())
    n_filled = sum(1 for p in (st.get("parents") or {}).values() if (p.get("filled") or 0) > 0)
    if n_child:
        return True, (f"state {os.path.basename(path)} có {n_child} lệnh con đã đặt, "
                      f"{n_filled} mã đã khớp")
    return False, ""


def lever_live_preflight(plan, account_label, broker, mode, status_path=None,
                         excluded_tickers=None, offbook_vnd=0.0):
    """PREFLIGHT SỐNG trước khi đặt bất kỳ lệnh đòn bẩy nào — CHỈ GỠ, không bao giờ cấp.

    Hai việc mà chỉ tầng broker sống làm được, nên không thể nằm trong apply_capit_lever
    (chạy trước khi connect):

    (1) **NEO NAV SỐNG** (đóng nốt khe artifact hai-trường, §10.3 báo cáo wiring). Ba đẳng
        thức nội tại ở `_verify_targets_integrity` buộc kẻ muốn thổi mục tiêu phải sửa cả
        `nav_basis_vnd`; đây là chỗ bắt đúng nước đi đó — đo lại NAV từ SỔ BROKER SỐNG
        (tiền + vị thế × giá thị trường, trừ excluded_tickers, cộng off-book) theo đúng công
        thức `mike/bin/compute_active_nav.py` mà chính golive dùng làm cơ sở. Chỉ chặn CHIỀU
        artifact khai NAV LỚN HƠN thực tế (chiều duy nhất sinh ra vay vượt mức); NAV thực tế
        lớn hơn artifact chỉ là sizing thận trọng, không phải rủi ro.

    (2) **ĐỌC THẬT `pp0Buy` theo ĐÚNG gói vay của lệnh** (việc kiểm tay ở phiên LIVE đầu tiên,
        `known_limits` mục 2 — nay có lưới TỰ ĐỘNG chạy trước, không thay người). Diễn tập
        paper KHÔNG phủ được tầng này (`PaperBroker` không có `ppse`), nên trước khi bot đặt
        lệnh vay tiền THẬT lần đầu, nó phải tự chứng minh đọc được sức mua ở gói 1840. Đọc
        KHÔNG được (mạng lỗi/None/≤0) ⇒ GỠ đòn bẩy phiên đó (chạy vốn tự có), KHÔNG đoán.

    KHÔNG gỡ khi pp0Buy đọc ĐƯỢC nhưng NHỎ HƠN Σ lệnh: gỡ đòn bẩy lúc đó làm lệnh cần NHIỀU
    tiền hơn (gói 1840 initialRate 0,5 ⇒ sức mua gấp đôi) — sai chiều fail-safe. Chỉ CẢNH BÁO
    to; phần không đủ tiền để `executor` xử như mọi phiên (WAIT_CASH).

    Chỉ chạy ở account mode=live. Paper/backtest: bỏ qua có ghi dòng log — `pp0Buy` là khái
    niệm của broker thật, và không có khoản vay thật nào để bảo vệ.

    Trả (plan, list dict) — cùng schema `adj` của apply_capit_lever.
    """
    levered = [o for o in plan.orders if getattr(o, "loan_package_id", None) is not None]
    if not levered:
        return plan, []
    total = sum(o.value for o in levered)
    tickers = sorted({o.ticker for o in levered})
    started, started_why = _session_already_placed(account_label, plan.plan_date,
                                                   {o.id for o in levered})

    def _strip(reason):
        """GỠ — nhưng CHỈ khi phiên chưa đặt lệnh nào. Đã đặt rồi thì hạ xuống CẢNH BÁO.

        VÌ SAO BẤT ĐỐI XỨNG (arch-reviewer vòng 3 #1): cron chạy `run_bot.sh` HAI lượt mỗi
        phiên (09:05 và 13:00 ICT "khởi động lại sau nghỉ trưa"), lượt sau là tiến trình MỚI
        chạy lại trọn cascade. Ở lượt 13:00 cả hai phép đo của preflight đều lệch một cách
        BÌNH THƯỜNG, không phải vì artifact giả: `availableCash` đã trừ phần tiền bị giữ cho
        lệnh đang treo nên NAV sống đo được THẤP hơn cơ sở tối qua (đo được −46% ở sizing
        CRISIS, −14,5% ở NEUTRAL — ăn gần hết biên 15%), và `pp0Buy@1840` tụt về ~0 sau khi
        sleeve đã giải ngân xong. GỠ khi ấy vừa VÔ ÍCH (lệnh đã ra rồi) vừa CÓ HẠI: nó khiến
        `Executor._lever_package_audit` mất tập cấp phép và PAUSE cả rổ CAPIT cả buổi chiều.
        Sổ `plan._lever_authorized` đã chặn đúng ca đó ở tầng audit; đây là lớp thứ hai, chặn
        ngay từ nguồn — và quan trọng hơn, nó giữ đòn bẩy cho phần rổ CHƯA giải ngân xong.

        Giá trị bảo vệ KHÔNG mất: mục tiêu của preflight là chặn khoản vay đầu tiên đi ra
        trên một cơ sở vốn giả. Lượt 09:05 (phiên sạch, chưa lệnh nào) vẫn GỠ đầy đủ.
        """
        if started:
            return plan, [{"ticker": "-", "order_id": "-", "action": "LIVE_PREFLIGHT_WARN",
                           "lever_f": None, "loan_package_id": None, "value": total,
                           "reason": (f"{reason} — NHƯNG phiên này ĐÃ đặt lệnh ({started_why}), "
                                      f"nên KHÔNG gỡ đòn bẩy: ở lượt chạy lại (13:00 ICT) NAV "
                                      f"sống/pp0Buy tụt là chuyện bình thường giữa lúc giải "
                                      f"ngân, còn gỡ thì làm audit tầng lệnh mất tập cấp phép "
                                      f"và treo cả rổ CAPIT. Chỉ CẢNH BÁO — người trực xem lại.")}]
        # THU HỒI khỏi sổ cấp phép — nhưng CHỈ phần do CHÍNH tiến trình này vừa cấp
        # (arch-reviewer vòng 4 #1, thu hẹp lại ở vòng 5 #1).
        #
        # Vì sao chỉ gỡ cờ trên lệnh là chưa đủ: đúng lúc preflight tuyên bố "cơ sở vốn KHÔNG
        # có thật", `Executor._lever_package_audit` lại MÙ với chính những mã đó — lệnh 1840
        # thật trên SAB cho `pause=set()`, bỏ sổ đi thì `pause={'SAB'}`.
        #
        # Vì sao KHÔNG được trừ sạch: sổ CỐ Ý day-scoped (lệnh cũ vẫn là lệnh thật đã được
        # cấp phép hợp lệ), trong khi điều kiện vào nhánh STRIP này lại ĐI QUA
        # `_session_already_placed` vốn khoá theo VÂN TAY của CHÍNH tập lệnh vay lượt này
        # (trước vòng 6 là `created_at`). Plan phát hành lại giữa ngày với lệnh vay MỚI ⇒
        # `started=False` dù lệnh 1840 buổi sáng vẫn sống trên sổ broker ⇒ trừ sạch sẽ
        # xoá đúng bản ghi đó và dựng lại sự cố giả (probe vòng 5: `pause=['SAB']`). `prior` =
        # nội dung sổ TRƯỚC khi tiến trình này hợp vào, tức phần thuộc về lệnh đã đi ra thật.
        _led = getattr(plan, "_lever_authorized", None)
        if _led:
            _prior = getattr(plan, "_lever_ledger_prior", None) or {}
            _tks = {o.ticker for o in levered}
            for _lp in list(_led):
                _led[_lp] -= (_tks - _prior.get(_lp, set()))
                if not _led[_lp]:
                    del _led[_lp]
            _lever_ledger_write(_lever_ledger_path(account_label, plan.plan_date), _led)
        for o in levered:
            o.lever_f = None
            o.loan_package_id = None
        return plan, [{"ticker": "-", "order_id": "-", "action": "LIVE_PREFLIGHT_STRIP",
                       "lever_f": None, "loan_package_id": None, "value": total,
                       "reason": (f"{reason} — GỠ đòn bẩy khỏi {len(levered)} lệnh "
                                  f"({', '.join(tickers)}), lệnh VẪN chạy bằng vốn tự có")}]

    if str(mode or "").lower() != "live":
        return plan, [{"ticker": "-", "order_id": "-", "action": "LIVE_PREFLIGHT_SKIPPED",
                       "lever_f": None, "loan_package_id": None, "value": total,
                       "reason": f"account mode={mode!r} (không phải live) — bỏ qua neo NAV "
                                 f"sống + đọc pp0Buy; không có khoản vay thật nào ở đây"}]

    # ── (1) neo NAV sống ────────────────────────────────────────────────────────────────
    from .config import WORKDIR
    path = status_path or os.path.join(WORKDIR, "data", "golive_v23_status.json")
    try:
        with open(path, encoding="utf-8") as f:
            t = ((json.load(f) or {}).get("capit_slot_targets") or {}).get(account_label) or {}
        nav_art = float(t["nav_basis_vnd"])
    except Exception as ex:
        return _strip(f"không đọc được `nav_basis_vnd` từ {path} ({type(ex).__name__}: {ex}) "
                      f"⇒ không có mốc nào để đối chiếu với NAV sống")
    excluded = set(excluded_tickers or [])
    try:
        cash = float(broker.get_cash() or 0)
        pos = broker.get_positions() or {}
        mv = excl_mv = 0.0
        missing = []
        for sym, p in pos.items():
            q = broker.get_quote(sym)
            px = (q.last or q.ref) if q is not None and getattr(q, "ok", lambda: False)() else None
            if not px:
                missing.append(sym)
                continue
            v = float(p.get("total", 0)) * float(px)
            mv += v
            if sym in excluded:
                excl_mv += v
        if missing:
            return _strip(f"không định giá được vị thế {sorted(missing)} ⇒ NAV sống không đủ "
                          f"tin cậy để làm mốc neo (fail-closed, không đoán giá)")
        nav_live = cash + mv + float(offbook_vnd or 0) - excl_mv
    except Exception as ex:
        return _strip(f"không đo được NAV sống từ broker ({type(ex).__name__}: {ex}) ⇒ không "
                      f"xác minh được cơ sở vốn mà mục tiêu vay dựa vào")
    if nav_live <= 0:
        return _strip(f"NAV sống đo được = {nav_live:,.0f} VND (≤0) — vô lý, fail-closed")
    if nav_art > nav_live * (1 + CAPIT_LEVER_NAV_TOL):
        return _strip(
            f"artifact khai `nav_basis_vnd`={nav_art:,.0f} VND nhưng NAV SỐNG đo từ sổ broker "
            f"= {nav_live:,.0f} VND (vượt {nav_art / nav_live - 1:+.1%} > biên "
            f"{CAPIT_LEVER_NAV_TOL:.0%}) ⇒ mục tiêu vay đang dựa trên một cơ sở vốn KHÔNG có "
            f"thật")

    # ── (2) pp0Buy theo ĐÚNG gói vay của lệnh ───────────────────────────────────────────
    probe = max(levered, key=lambda o: o.value)
    lp = probe.loan_package_id
    try:
        bp = broker.get_buying_power(probe.ticker, int(probe.ref_price), loan_package_id=lp)
    except Exception as ex:
        return _strip(f"đọc sức mua gói vay {lp} lỗi ({type(ex).__name__}: {ex}) ⇒ chưa chứng "
                      f"minh được bot đặt được lệnh bằng tiền vay thật")
    # ĐỌC KHÔNG ĐƯỢC (None) ⇒ GỠ — đó là điều kiện mà bước này tồn tại để chứng minh: bot có
    # thật sự nói chuyện được với tầng `ppse` theo đúng gói vay hay không (diễn tập paper
    # không phủ được). Nhưng `bp == 0` là ĐỌC ĐƯỢC, chỉ là hết sức mua — trạng thái BÌNH
    # THƯỜNG sau khi sleeve giải ngân xong, và gỡ đòn bẩy lúc hết tiền làm lệnh cần NHIỀU tiền
    # hơn (gói 1840 initialRate 0,5 ⇒ sức mua gấp đôi): đúng chiều sai của fail-safe, cùng lý
    # lẽ với nhánh `bp < total` ngay dưới (arch-reviewer vòng 3 #1, chân thứ hai).
    if bp is None:
        return _strip(f"đọc sức mua gói vay {lp} trả về None ⇒ chưa chứng minh được bot đặt "
                      f"được lệnh bằng tiền vay thật (kiểm tay `pp0Buy@{lp}` trước khi bật lại)")
    out = [{"ticker": "-", "order_id": "-", "action": "LIVE_PREFLIGHT_OK",
            "lever_f": getattr(probe, "lever_f", None), "loan_package_id": lp, "value": total,
            "reason": (f"NAV sống {nav_live:,.0f} VND vs artifact `nav_basis_vnd` "
                       f"{nav_art:,.0f} ({nav_art / nav_live - 1:+.1%}, biên "
                       f"{CAPIT_LEVER_NAV_TOL:.0%}) · sức mua pp0Buy@{lp} đo trên "
                       f"{probe.ticker}@{probe.ref_price:,.0f} = {bp:,.0f} VND vs Σ lệnh đòn "
                       f"bẩy {total:,.0f} VND ({len(levered)} lệnh: {', '.join(tickers)})")}]
    if bp < total:
        out.append({"ticker": "-", "order_id": "-", "action": "LIVE_PREFLIGHT_WARN",
                    "lever_f": None, "loan_package_id": lp, "value": total,
                    "reason": (f"sức mua đo được {bp:,.0f} VND < Σ lệnh đòn bẩy {total:,.0f} "
                               f"VND — KHÔNG gỡ đòn bẩy (gỡ sẽ cần NHIỀU tiền hơn, sai chiều "
                               f"fail-safe); phần thiếu sẽ đi đường WAIT_CASH như mọi phiên"
                               + (f". Phiên đã đặt lệnh ({started_why}) ⇒ sức mua tụt là "
                                  f"chuyện bình thường của lượt chạy lại." if started else ""))})
    return plan, out


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
