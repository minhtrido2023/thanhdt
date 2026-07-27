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

    Trần = LAG_ADV_PCT × ADV × share, ADV = Volume_3M_P50 × Close đúng công thức backtest
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
            _block(f"ADV = 0 (Volume_3M_P50×Close, data {data_date}) — mã không có thanh "
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
