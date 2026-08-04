"""GATE CỨNG tầng PLAN — Σ giá trị lệnh MUA phải ≤ SỨC MUA THẬT của broker.

⚠️ CHƯA WIRE VÀO PRODUCTION. Module này chưa được `bot_execute.py` gọi; patch chờ Mike review
+ quant-skeptic duyệt (`mike/agents/Taylor/research/plan_funding_gate_bot_execute.patch`).

VÌ SAO CẦN GATE CƠ HỌC (không phải thêm 1 dòng văn xuôi nữa)
────────────────────────────────────────────────────────────
Luật "Σ orders[] ≤ cash thực, tự SHRINK không list-rồi-đợi-tiền" (kb/context_planning_mini.md)
đã TÁI PHẠM 3 LẦN / 15 ngày — 07-23 (đòi rút Trứng vàng ảo), 07-27 (field `funding_required`,
460,7M vs cash 12,4M), 07-28 (văn xuôi "user sẽ nạp 136M", 146,5M vs cash 10,41M). Lần 3 xảy ra
SAU KHI luật đã được cấm bằng văn bản trong chính file context của DollarBill. Cả 3 lần chỉ thoát
nhờ một bước QA thứ hai TÌNH CỜ chạy. Đây đúng loại lỗi mà `kb/coding_guidelines.md` (Enforcement
policy) bắt phải chuyển thành check cơ học: luật này diễn đạt được thuần số học, không cần LLM
phán đoán gì.

TRẠNG THÁI 4 TẦNG TRƯỚC KHI CÓ MODULE NÀY (xác minh 2026-08-04, job Taylor_20260804_133014)
  1. DollarBill (nơi VIẾT plan)  — chỉ VĂN XUÔI trong context_planning_mini.md → đã thủng 3 lần.
  2. `bot_execute.py:_log_plan_buying_power_shadow` — SHADOW WARN_ONLY, `print` + 1 dòng CSV,
     không `return`/`raise`/`continue` nào. Log có ĐÚNG 1 dòng từ trước tới nay.
  3. `trading_bot/executor.py:1066` (`get_cash() < need` → `WAIT_CASH`) — per-ORDER, first-come-
     first-served: plan vượt tiền vẫn khớp N lệnh đầu rồi phần còn lại treo. Đó CHÍNH LÀ hành vi
     "list-rồi-đợi-tiền" mà luật cấm, chứ không phải cơ chế chặn nó.
  4. Mafee (`kb/context_execution_mini.md`) — KHÔNG có luật này ở bất kỳ hình thức nào.

VẾ PHẢI = SỨC MUA ĐO ĐƯỢC (`ppse.pp0Buy`), KHÔNG phải cash tĩnh
────────────────────────────────────────────────────────────────
Tôn trọng nguyên vẹn quyết định user 16:16 ICT 2026-07-28: từ chối luật cứng `Σ orders ≤ cash_vnd`
vì hệ CÓ dùng margin. `pp0Buy` là số của CHÍNH broker — đã gồm hạn mức vay của gói đang dùng và
tiền bán chờ về T+0 — nên gate chỉ bắt "vốn CHƯA TỒN TẠI", không cấm đòn bẩy.

Đọc DNSE SỐNG tại THỜI ĐIỂM THỰC THI (coding_guidelines §6 bright-line). KHÔNG dùng bất kỳ con số
cash nào ghi trong plan JSON đêm hôm trước — điều này còn được bảo đảm về mặt cấu trúc: `TradePlan`
KHÔNG có field cash nào cả (`nav_basis` chỉ có NAV). Quan trọng với kiến trúc injector: tranche TV1
trừ tiền lúc 20:30, SAU khi DollarBill viết plan ~19:0x; gate chạy 09:05 sáng hôm sau nên nhìn thấy
số dư SAU injector.

BẪY LỚN NHẤT — SỨC MUA PHỤ THUỘC GÓI VAY, ĐO SAI GÓI = CHẶN OAN CẢ PLAN
──────────────────────────────────────────────────────────────────────
Bằng chứng thật (không phải giả định): dòng DUY NHẤT từng được ghi vào
`data/plan_buying_power_shadow_log.csv` là `2026-07-29,SpaceX,5820000,0,dnse:ppse.pp0Buy@TV1,true`
— tức shadow log nói "would_block". Đó là FALSE POSITIVE:
  • `dnse_raw_2026-07-29.jsonl` 09:15:14 `loan_packages_resolve`: TV1 default=1841, valid_ids=[1122],
    resolved=**1122** (1841 là gói mainboard, KHÔNG hợp lệ cho TV1 trên UPCOM).
  • 09:15:15 `place_order` TV1 100cp @19.600 với `loan_package_id=1122` → DNSE **NHẬN** (id 36241).
  • 13:00:02 shadow log gọi `ppse` **không truyền loan_package_id** → rơi về gói default 1841 →
    `pp0Buy=0`, `qmaxBuy=0`.
Nghĩa là: nếu bật gate naive (một lần query `pp0Buy` bằng gói default) thì ngày 2026-07-29 nó đã
CHẶN OAN TOÀN BỘ plan SpaceX vì một hiện vật đo đạc. Vì vậy module này **giải gói vay ĐÚNG CÁCH
`place_order` sẽ giải** — CẢ HAI nhánh, không chỉ một (`cash_only` → `_resolve_loan_package_id`;
đòn bẩy CAPIT `order.loan_package_id` → `_validate_lever_package`, xem `_effective_loan_package`)
— rồi đo `pp0Buy` theo TỪNG NHÓM gói vay. Lệch nhánh nào cũng hỏng, nhưng hỏng theo hai CHIỀU
ngược nhau: nhánh `cash_only` lệch ⇒ chặn OAN (ca TV1), nhánh đòn bẩy lệch ⇒ đo THỪA sức mua gấp
đôi ⇒ BỎ LỌT đúng thứ gate sinh ra để chặn (quant-skeptic vòng 1, 2026-08-04).

CÔNG THỨC
─────────
  need_g  = Σ_(lệnh mua thuộc nhóm g) qty × ref_price × (1 + FEE_RATE)
  U       = Σ_g  need_g / pp0Buy_g              ("tỉ lệ sức mua bị tiêu thụ")
  CHẶN khi U > 1.0  (đúng `≤`, hoà đúng bằng sức mua thì KHÔNG chặn)
Nhóm đơn (mọi phiên thường lệ, tất cả lệnh dùng gói default) → rút gọn về đúng `Σ need ≤ pp0Buy`.
Nhiều nhóm: các gói vay chia nhau CÙNG một hũ tiền với hệ số vay khác nhau, nên cộng phân số tiêu
thụ là xấp xỉ tuyến tính đúng khi các gói cùng initialRate và hợp lý khi khác.

KHI KHÔNG ĐO ĐƯỢC `pp0Buy` (None hoặc ≤0) — KHÔNG chặn theo phản xạ, mà dùng CẬN NGOÀI
────────────────────────────────────────────────────────────────────────────────────────
Fail-closed máy móc ở đây là sai chiều: ca TV1 ở trên chứng minh "không đo được / đo ra 0" xảy ra
trên plan HỢP LỆ, và chặn oan cả plan có phí thật (lỡ deadline vào lệnh LAG T+1/T+2). Đồng thời
không được thả lỏng. Cách xử: so với CẬN NGOÀI không thể giải thích bằng đòn bẩy —
  bound = (availableCash + Σ giá trị lệnh BÁN trong plan) × FALLBACK_LEVERAGE_MULT
  Σ need > bound  →  CHẶN (mức "vốn không tồn tại", đòn bẩy tối đa 2× không thể giải thích nổi)
  ngược lại       →  UNVERIFIED: KHÔNG chặn, nhưng BÁO TO (bus error + Telegram) để người xem.
Đối chiếu 3 mốc THẬT (replay trong selfcheck):
  07-27 SpaceX 460,7M vs cash 12,4M  → bound 37,2M  → CHẶN ✔ (đúng, đây là sự cố thật)
  07-28 SpaceX 146,5M vs cash 10,41M → bound 31,2M  → CHẶN ✔ (đúng, đây là sự cố thật)
  07-29 SpaceX   5,82M vs cash 10,41M → bound 31,2M → KHÔNG chặn ✔ (đúng, đây là false positive)
Lưu ý `pp0Buy == 0` do hết tiền THẬT vẫn bị bắt: lúc đó cash≈0 ⇒ bound≈0 ⇒ Σ need > bound → CHẶN.

TÁC ĐỘNG KHI CHẶN: caller KHÔNG được đặt BẤT KỲ lệnh nào của plan đó (không thực thi một phần —
đó là toàn bộ điểm của gate), báo bus + Telegram, exit ≠ 0. Cùng khuôn `approval_block_reason()`.

Gate này READ-ONLY (mỗi nhóm gói vay 1 lần gọi `ppse`), không side-effect, an toàn với §5.
"""

# Phí giao dịch thật của SpaceX/ZaloPay tại DNSE = 0,075% (KHÔNG phải 0,1% — xác nhận 2026-07-03,
# dùng thống nhất với bin/reconcile_equity.py). Đây là phần "fee_est_vnd" trong Σ.
FEE_RATE = 0.00075

# Cận ngoài khi không đo được pp0Buy: bội số của (cash + tiền bán trong plan). Đòn bẩy tối đa
# thực tế của account margin là 2× vốn tự có (initialRate 0,5) ⇒ 3,0 để lại ~50% biên an toàn,
# đủ rộng để không chặn oan, đủ chặt để bắt cả 3 sự cố thật (14×–37×).
FALLBACK_LEVERAGE_MULT = 3.0

# Sai số dấu phẩy động khi so U với 1,0 — bảo đảm "hoà đúng bằng sức mua" KHÔNG bị chặn (`≤`).
_EPS = 1e-9


def _account_default_package(broker):
    """Gói vay mặc định của account — ĐÚNG giá trị `DNSEBroker._validate_lever_package` trả về
    khi gói chỉ định không dùng được (`self.client.loan_package_id`)."""
    return getattr(getattr(broker, "client", None), "loan_package_id", None)


def _effective_loan_package(order, broker):
    """Gói vay lệnh này THỰC SỰ sẽ đi ra bằng — giải ĐÚNG cách `DNSEBroker.place_order` giải.

    Sai lệch ở đây chính là nguồn false positive duy nhất từng quan sát được (ca TV1 07-29,
    xem docstring module). Trả (loan_package_id | None, nguồn_để_log).

    HAI nhánh, KHÔNG phải một (quant-skeptic vòng 1, 2026-08-04 — bản đầu chỉ giải đúng nhánh
    `cash_only`, nhánh đòn bẩy CAPIT tin thẳng id mà lệnh khai báo):
      • `order.loan_package_id` (đòn bẩy CAPIT do `apply_capit_lever` cấp) — `place_order`
        KHÔNG tin thẳng id này. `brokers.py:629-644` gọi `_validate_lever_package(symbol, want)`
        trước; gói không hợp lệ cho MÃ ĐÓ (hoặc không kiểm được) ⇒ lệnh đi ra bằng gói DEFAULT
        account, tức KHÔNG có đòn bẩy. Gói 1840 có initialRate 0,5 ⇒ sức mua GẤP ĐÔI gói 1841:
        đo bằng gói khai báo trong khi lệnh khớp bằng gói nhỏ hơn = đo THỪA sức mua đúng gấp
        đôi ⇒ gate bỏ lọt chính hành vi "list-rồi-đợi-tiền" nó sinh ra để ngăn.
      • `cash_only` — `_resolve_loan_package_id(ticker)` (ca TV1/UPCOM).
    Cả hai hàm broker đều cache theo (symbol[, want]) trong phiên ⇒ giá trị gate đo và giá trị
    `place_order` dùng KHÔNG THỂ lệch nhau.
    """
    lp = getattr(order, "loan_package_id", None)
    if lp is not None:
        fn = getattr(broker, "_validate_lever_package", None)
        if callable(fn):
            try:
                eff, ok, _note = fn(order.ticker, lp)
                return eff, ("lever:validated" if ok else "lever:invalid→account_default")
            except Exception:
                pass
        # Không kiểm được (broker không hỗ trợ, hoặc hàm lỗi bất thường — bản thân
        # `_validate_lever_package` đã tự nuốt mọi lỗi mạng và trả gói default). KHÔNG được
        # giả định đòn bẩy áp được: đo bằng gói default cho sức mua NHỎ HƠN — cùng chiều
        # fail-safe với chính `place_order` (thà chặn/under-deploy còn hơn vay vượt mức).
        return _account_default_package(broker), "lever:unvalidated→account_default"
    if getattr(order, "cash_only", False):
        fn = getattr(broker, "_resolve_loan_package_id", None)
        if callable(fn):
            try:
                # Cùng hàm, cùng cache theo symbol trong phiên → không thể lệch với place_order.
                return fn(order.ticker), "resolved:cash_only"
            except Exception:
                pass
    return None, "account_default"


def check_plan_funding(plan, broker, account_mode):
    """Verdict cấp PLAN. KHÔNG tự chặn gì — caller đọc `action` và quyết định.

    Trả dict:
      action  : "OK" | "BLOCK" | "UNVERIFIED" | "SKIPPED"
      reason  : chuỗi giải thích (đủ để đưa thẳng vào alert Telegram/bus)
      need_vnd, buying_power_vnd, utilization, groups[], fallback_bound_vnd
    """
    if str(account_mode or "").lower() != "live":
        return {"action": "SKIPPED", "reason": f"mode={account_mode} (không phải live) — "
                f"`ppse` là khái niệm của broker thật, paper/backtest không có",
                "need_vnd": 0.0, "buying_power_vnd": None, "utilization": None,
                "groups": [], "fallback_bound_vnd": None}

    buys = [o for o in plan.orders if str(o.side or "").lower() == "buy"]
    if not buys:
        return {"action": "SKIPPED", "reason": "plan không có lệnh MUA — không có gì để cấp vốn",
                "need_vnd": 0.0, "buying_power_vnd": None, "utilization": None,
                "groups": [], "fallback_bound_vnd": None}

    # ── gom lệnh mua theo gói vay hiệu lực ────────────────────────────────────────────────
    groups = {}
    for o in buys:
        lp, src = _effective_loan_package(o, broker)
        g = groups.setdefault(str(lp), {"lp": lp, "src": src, "orders": [], "need": 0.0})
        g["orders"].append(o)
        g["need"] += o.qty * o.ref_price * (1.0 + FEE_RATE)

    total_need = sum(g["need"] for g in groups.values())

    # ── đo pp0Buy từng nhóm, bằng ĐÚNG gói vay của nhóm đó ────────────────────────────────
    measured_util = 0.0
    unmeasured = []
    out_groups = []
    for key, g in sorted(groups.items()):
        probe = max(g["orders"], key=lambda o: o.qty * o.ref_price)
        bp = err = None
        try:
            bp = broker.get_buying_power(probe.ticker, int(probe.ref_price),
                                         loan_package_id=g["lp"])
        except Exception as ex:
            err = type(ex).__name__
        rec = {"loan_package_id": g["lp"], "package_source": g["src"],
               "n_orders": len(g["orders"]), "need_vnd": g["need"],
               "probe_ticker": probe.ticker, "probe_price": probe.ref_price,
               "buying_power_vnd": bp, "error": err}
        if bp is not None and bp > 0:
            rec["utilization"] = g["need"] / bp
            measured_util += rec["utilization"]
        else:
            rec["utilization"] = None
            unmeasured.append(rec)
        out_groups.append(rec)

    measured_bp = sum(r["buying_power_vnd"] for r in out_groups
                      if r["buying_power_vnd"] is not None and r["buying_power_vnd"] > 0)

    # ── (1) nhóm đo được đã vượt sức mua → CHẶN, không cần xét gì thêm ────────────────────
    if measured_util > 1.0 + _EPS:
        return {"action": "BLOCK", "groups": out_groups, "need_vnd": total_need,
                "buying_power_vnd": measured_bp, "utilization": measured_util,
                "fallback_bound_vnd": None,
                "reason": (f"Σ lệnh MUA {total_need:,.0f}đ VƯỢT sức mua thật của broker "
                           f"{measured_bp:,.0f}đ (pp0Buy, đã gồm hạn mức vay + tiền bán chờ về "
                           f"T+0) — tiêu thụ {measured_util*100:.1f}% sức mua. Plan đang chứa "
                           f"lệnh dựa trên vốn CHƯA TỒN TẠI; theo luật "
                           f"context_planning_mini.md phần thiếu phải nằm ở deferred_orders[], "
                           f"KHÔNG phải orders[].")}

    # ── (2) mọi nhóm đo được và không vượt → OK ───────────────────────────────────────────
    if not unmeasured:
        return {"action": "OK", "groups": out_groups, "need_vnd": total_need,
                "buying_power_vnd": measured_bp, "utilization": measured_util,
                "fallback_bound_vnd": None,
                "reason": (f"Σ lệnh MUA {total_need:,.0f}đ ≤ sức mua {measured_bp:,.0f}đ "
                           f"({measured_util*100:.1f}%)")}

    # ── (3) có nhóm không đo được → cận ngoài, chỉ chặn mức "vốn không tồn tại" ───────────
    try:
        cash = float(broker.get_cash() or 0.0)
    except Exception:
        cash = 0.0
    sell_value = sum(o.qty * o.ref_price for o in plan.orders
                     if str(o.side or "").lower() == "sell")
    bound = (cash + sell_value) * FALLBACK_LEVERAGE_MULT
    lps = ", ".join(str(r["loan_package_id"]) for r in unmeasured)
    common = (f"KHÔNG đo được pp0Buy cho {len(unmeasured)}/{len(out_groups)} nhóm gói vay "
              f"({lps}); cận ngoài = (cash {cash:,.0f}đ + lệnh bán {sell_value:,.0f}đ) × "
              f"{FALLBACK_LEVERAGE_MULT:g} = {bound:,.0f}đ")
    if total_need > bound:
        return {"action": "BLOCK", "groups": out_groups, "need_vnd": total_need,
                "buying_power_vnd": measured_bp if measured_bp else None,
                "utilization": measured_util, "fallback_bound_vnd": bound,
                "reason": (f"Σ lệnh MUA {total_need:,.0f}đ VƯỢT cả cận ngoài — {common}. "
                           f"Đòn bẩy tối đa 2× không giải thích được mức này ⇒ plan chứa lệnh "
                           f"dựa trên vốn CHƯA TỒN TẠI.")}
    return {"action": "UNVERIFIED", "groups": out_groups, "need_vnd": total_need,
            "buying_power_vnd": measured_bp if measured_bp else None,
            "utilization": measured_util, "fallback_bound_vnd": bound,
            "reason": (f"Σ lệnh MUA {total_need:,.0f}đ nằm trong cận ngoài nhưng CHƯA xác minh "
                       f"được bằng sức mua thật — {common}. KHÔNG chặn (ca TV1 2026-07-29 chứng "
                       f"minh đo-không-được xảy ra trên plan hợp lệ), nhưng cần người xem.")}


def funding_block_reason(plan, broker, account_mode):
    """Bọc mỏng theo khuôn `approval_block_reason()`: None = cho chạy, chuỗi = lý do CHẶN."""
    v = check_plan_funding(plan, broker, account_mode)
    return v["reason"] if v["action"] == "BLOCK" else None
