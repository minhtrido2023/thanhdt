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


def apply_capit_lever(plan, account_label, status_path=None, rules_path=None):
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

    Trả (plan đã sửa, list dict mô tả từng thay đổi) — KHÔNG log, caller tự báo.
    Mỗi dict: {"ticker","order_id","action","lever_f","loan_package_id","reason"}.
    """
    from .config import WORKDIR

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
                            "reason": f"plan ghi sẵn (f={o.lever_f!r}, lp={o.loan_package_id!r}) "
                                      f"— ghi đè bằng giá trị của artifact"})
            else:
                adj.append({"ticker": o.ticker, "order_id": o.id, "action": "APPLIED",
                            "lever_f": float(f_val), "loan_package_id": lp_val,
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
    return plan, adj


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
