#!/usr/bin/env python3
"""L2 — JIT unpark: đề xuất lệnh BÁN PARK **đúng bằng phần thiếu** để tài trợ một lệnh mua BAL/LAG.

⚠️ CHỈ ĐỌC — script này KHÔNG đặt lệnh, KHÔNG ghi vào plan. Đầu ra là một khối JSON ĐỀ XUẤT
   (đúng dạng để wire vào một field riêng của plan sau này); nó vẫn phải đi qua đúng cơ chế
   duyệt hiện có (user duyệt plan → Mafee plan-bound) như mọi lệnh khác.

VÌ SAO (§A5/§B3 `park_unpark_live_wiring_20260803.md`, xác nhận lại job Taylor_20260805_163403 —
quant-skeptic CONFIRMED): engine mô phỏng tài trợ deal BAL/LAG bằng **bán PARK ngay lúc mua**
(`JIT_FOR_BA_BUY`, simulate_holistic_nav.py:1134-1186), KHÔNG chỉ bằng sweep-về-trần (L1, đã live).
Live hiện nay thiếu đường này ⇒ khi cash không đủ, live **defer nguyên lệnh** trong khi engine
**bán PARK rồi mua**, hoặc **co lệnh** xuống theo sức mua. Lý do wire = TRUNG THÀNH THIẾT KẾ
(live phải chạy đúng cơ chế đã tạo ra số pin R3 28,86%), **KHÔNG PHẢI** lý do lợi nhuận —
ablation 2026-08-03 cho thấy thiếu L2 không rớt OOS đủ mạnh để coi là mất tiền thật.

CÔNG THỨC — mọi hằng số đều PORT, không có tham số mới (file:dòng ghi ngay tại chỗ khai báo):

    for order in các lệnh MUA book BAL/LAG (theo thứ tự priority của plan):
        target_value = qty × ref_price
        if cash >= target_value × 0,99:            # engine dòng 1134 — không trigger
            cash -= target_value;  continue
        needed = min((target_value − max(cash,0))/(1 − friction), etf_day_cap_remaining)
        #        ^^ engine dòng 1137 KHÔNG chia (1−friction); gross-up là phương án (B) user duyệt
        #           2026-08-06 — xem khối chú thích tại chỗ tính. Engine bù phần hụt bằng fill
        #           nhiều phiên, live chỉ có MỘT phiên nên phải gross-up mới thu ròng đủ.
        → bán PARK đúng `needed`  (pro-rata theo trọng số hiện tại, FIFO theo lô trong từng mã)
        cash += Σ(giá trị bán) × (1 − friction)                           # engine dòng 1164-1166
        # Fallback y hệt engine dòng 1189-1194 (chạy SAU JIT, trên cash đã cộng tiền bán):
        if cash + margin_room < target_value × 0,99:
            target_value = (cash + margin_room) × 0,95
        if target_value < 1.000.000:  → BỎ lệnh
        else nếu nhỏ hơn ban đầu     → CO lệnh (qty mới = round_lot(target_value / ref_price))

Đây chính là chỗ live khác engine hôm nay: live defer NGUYÊN lệnh, engine CO lệnh. L2 đề xuất
đúng hành vi engine.

CHIA LỆNH BÁN THEO MÃ — dùng lại nguyên quy ước của L1 (`compute_park_trim.py`, §B4):
  · PRO RATA theo trọng số PARK hiện tại; **không** bán sạch vài mã (bán sạch = đổi cấu trúc rổ
    = đổi hẳn thứ đã backtest). Trong mỗi mã: **FIFO theo lô** (`entry_date`).
  · Trần TỔNG/phiên = `_etf_day_cap` (ETF_LIQ_PCT × ADV rổ) — DÙNG LẠI hàm của L1, không đặt
    trần mới. Phần không bán được phiên này KHÔNG phân bổ lại sang mã khác (§D2 — carry-over);
    hệ quả là lệnh mua bị CO lại, đúng như engine.
  · Trần RIÊNG mỗi mã = gate LAG live (`LAG_ADV_PCT × ADV_mã × share`), fail-closed per-name y
    hệt L1: không đo được ADV / ADV cũ hơn LAG_ADV_MAX_STALE_DAYS / ADV ≤ 0 ⇒ không bán mã đó.
  · **Rời rạc hoá theo lô chẵn** (điểm live KHÔNG có trong engine — engine bán được cổ phần lẻ
    của MỘT quỹ ETF, live phải bán bội số 100cp của 30 mã): chia pro-rata rồi làm tròn XUỐNG lô,
    phần dư phân bổ tiếp theo **largest-remainder** (mã nào còn thiếu nhiều nhất so với phần
    pro-rata của nó được thêm 1 lô trước). Đây là quy tắc LÀM TRÒN, không phải tham số mới: nếu
    bỏ nó thì mọi `needed` nhỏ (< 100cp × giá × 30 mã) sẽ ra 0 lệnh và L2 im lặng không làm gì —
    đúng dạng lỗi im lặng §14 muốn tránh. Tie-break xác định (unmet giảm dần, rồi ticker tăng
    dần) ⇒ chạy lại cho kết quả y hệt.
  · **Làm tròn LÊN đúng 1 lô khi vẫn còn hụt** — phương án (C), user John duyệt 2026-08-06 (job
    `Taylor_20260806_033014`). Nếu sau largest-remainder mà `Σ bán < needed`, bán THÊM đúng 1 lô
    RẺ NHẤT còn dư địa; theo điều kiện dừng ở trên, lô đó chắc chắn đưa `Σ bán` VƯỢT `needed` ⇒
    thu ròng đủ, lệnh mua không bị co. **Đảo bất biến cũ "Σ bán ≤ needed"**, cận trên mới:
        needed ≤ Σ bán < needed + (giá trị 1 lô rẻ nhất còn dư địa)
    Lý do: đo trên sổ thật 2026-08-06, hụt **1.792đ** vẫn làm mất TRỌN **10tr** lệnh mua (chân mua
    `round_lot(min(tv, bp)/px)` không có dung sai). Lô thêm vào vẫn phải lọt HẾT trần cứng (TỔNG/
    phiên, per-name, sellable T+2); không lọt ⇒ không thêm, lệnh mua co lại như cũ.

RANH GIỚI CỨNG (§B5) — giống hệt L1:
  · Giá/tiền đọc DNSE, KHÔNG BQ (§6). Dùng `availableCash`, KHÔNG `totalCash`.
  · `excluded_tickers` (vd DGC ở ZaloPay) — KHÔNG BAO GIỜ bán.
  · Chỉ đụng lô có `book == "PARK"`. Vị thế CAPIT (stop_exempt/slot_exempt), LAG, BAL,
    DISCRETIONARY_SPECIAL, LEGACY_ORPHAN **không nằm trong `park_lots`** ⇒ cấu trúc không thể
    chạm tới (có kiểm tra bất biến `_assert_park_only`, fail-closed nếu sai).
  · Ticker `UNVERIFIED` — KHÔNG sinh lệnh (§21). Đối soát sổ-vs-broker LỆCH ⇒ không đề xuất gì.
  · Sizing theo `active_nav`: L2 KHÔNG tự tính size lệnh mua — nó chỉ đọc `qty × ref_price` mà
    plan (đã sizing theo active_nav ở tầng trên) đưa ra. L2 chỉ CẤP VỐN, không tạo quyền mua:
    mọi lệnh mua vẫn đi qua gate live hiện có (DD, 8L rating≤3, cap_lag_orders %ADV,
    filter_lag_rating_orders).
  · L2 KHÔNG có điều kiện phụ nào ngoài "có lệnh mua BAL/LAG thật" (§B4).

DÙNG CHUNG TRẦN VỚI L1: L1 và L2 tiêu cùng một trần thanh khoản/phiên và cùng số cổ phiếu vật
lý. Truyền `--l1-json <file>` (đầu ra `compute_park_trim.py --out`) để trừ trước phần L1 đã đề
xuất (trần tổng, trần per-name, và số cp sellable). Không truyền = coi như L1 không chạy phiên
này — CHÚ Ý: chạy cả hai mà không nối sẽ đề xuất bán trùng cùng số cp.

    python3 mike/bin/compute_jit_unpark.py --account SpaceX [--asof ...] [--plan <path>]
        [--l1-json data/.../park_trim.json] [--margin-room 0] [--json] [--out <file>]
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

from park_holdings import park_holdings, today_ict, norm_book          # noqa: E402
from compute_park_trim import etf_day_cap_live, live_share             # noqa: E402
from trading_bot.plan import (LAG_ADV_PCT, LAG_ADV_MAX_STALE_DAYS,     # noqa: E402
                              _adv_for_gate)
from trading_bot.vn_market import LOT, round_lot                       # noqa: E402

# ── Hằng số PORT từ engine — KHÔNG cái nào tự chế ────────────────────────────
JIT_TRIGGER_FRAC = 0.99      # simulate_holistic_nav.py:1134  `cash < target_value * 0.99`
SHRINK_FRAC = 0.95           # simulate_holistic_nav.py:1194  `(cash + _margin_room) * 0.95`
MIN_ORDER_VND = 1_000_000    # simulate_holistic_nav.py:1195  `if target_value < 1_000_000`
ETF_FRICTION = 0.0015        # pt_v23_audit_2014.py:1946 `etf_rebalance_friction=0.0015` (R3)
# Margin room cho lệnh BAL/LAG = 0 trong cấu hình R3 đã pin: `max_gross_exposure` chỉ bật khi
# env `_mge` (V2.5) và khi bật thì `margin_tiers` giới hạn về CAPIT-only
# (pt_v23_audit_2014.py:1959-1961). V2.5 đang DISABLED ⇒ mặc định 0. Đổi được bằng --margin-room
# NHƯNG đó là thay đổi chính sách, cần user duyệt.
DEFAULT_MARGIN_ROOM_VND = 0.0
TRIGGER_BOOKS = ("BAL", "LAG")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")


# ───────────────────────────────────────────────────────────────── đầu vào plan

def load_plan_orders(account_label, asof, plan_path=None):
    """Đọc RAW JSON của plan (không qua `load_plan()`): cần nguyên field `book`/`play_type`/
    `priority` mà dataclass PlannedOrder có thể lọc mất. Trả (orders, path, err)."""
    path = plan_path or os.path.join(PLAN_DIR, f"plan_{account_label}_{asof}.json")
    if not os.path.exists(path):
        return None, path, f"không có file plan {os.path.basename(path)}"
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:                                    # plan hỏng ⇒ fail-closed
        return None, path, f"plan không parse được: {e}"
    return (d.get("orders") or []), path, None


def _ref_price(o):
    """Cùng thứ tự fallback với `trading_bot.plan.load_plan` — không tự chế field mới."""
    for k in ("ref_price", "mtm_price_ref", "price"):
        v = o.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
    return None


def trigger_orders(orders):
    """Lệnh MUA book BAL/LAG, theo thứ tự `priority` (thiếu priority → giữ thứ tự trong plan).

    PARK buy (`custom30V_parking`) và CAPIT buy KHÔNG phải trigger: L2 chỉ port đúng nhánh
    `JIT_FOR_BA_BUY` của engine (tài trợ deal BAL/LAG)."""
    out = []
    for i, o in enumerate(orders or []):
        if str(o.get("side", "")).lower() != "buy":
            continue
        if norm_book(o.get("book")) not in TRIGGER_BOOKS:
            continue
        out.append((i, o))
    out.sort(key=lambda x: (x[1].get("priority") if isinstance(x[1].get("priority"), (int, float))
                            else 10 ** 9, x[0]))
    return [o for _, o in out]


# ────────────────────────────────────────────────────── rổ PARK bán được (sống)

def _assert_park_only(lots):
    """Bất biến: mọi lô đưa vào bộ phân bổ phải là book PARK. Sai ⇒ fail-closed (không tự lọc
    rồi đi tiếp — lô lạ ở đây nghĩa là `park_holdings` đổi hợp đồng, phải để người xem)."""
    bad = sorted({l.get("book") for l in lots if (l.get("book") or "") != "PARK"})
    return None if not bad else f"park_lots chứa book KHÔNG phải PARK: {bad}"


def build_pool(h, asof, share, adv_fn, l1_used=None):
    """Rổ PARK bán được + trần per-name. Trả (pool {tk: {...}}, blocked [...], err)."""
    l1_used = l1_used or {}
    err = _assert_park_only(h["park_lots"])
    if err:
        return None, [], err
    excluded = set(h["excluded_tickers"])
    # Mã LỆCH ĐỐI SOÁT luôn bị cấm bán, kể cả khi caller không khai nó vào `unverified_tickers`.
    # Suy THẲNG từ `h["reconcile"]` thay vì nhận qua tham số: `build_pool` là hàm duy nhất dựng rổ
    # bán của L2, nên cưỡng chế ở đây thì không đường gọi nào lách được — kể cả selfcheck bơm
    # holdings tay, kể cả caller tương lai gọi `build_pool` trực tiếp mà không qua cổng 0.
    unver = set(h["unverified_tickers"]) | {
        m["ticker"] for m in ((h.get("reconcile") or {}).get("mismatches") or [])}
    bpos = h.get("broker_positions", {}) or {}

    per_tk, blocked = {}, []
    for l in h["park_lots"]:
        d = per_tk.setdefault(l["ticker"], {"qty": 0, "mv": 0.0, "px": l["market_price"],
                                            "lots": []})
        d["qty"] += l["qty"]
        d["mv"] += l["mv_vnd"]
        d["lots"].append(l)

    pool = {}
    for tk in sorted(per_tk):
        d = per_tk[tk]
        if tk in excluded:
            blocked.append({"ticker": tk, "reason": "excluded_tickers — CẤM bán"})
            continue
        if tk in unver:
            blocked.append({"ticker": tk, "reason": "sổ UNVERIFIED — cấm sinh lệnh (§21)"})
            continue
        px = float(d["px"] or 0)
        if px <= 0:
            blocked.append({"ticker": tk, "reason": "không có marketPrice broker"})
            continue
        adv, data_date, e = adv_fn(tk, asof)
        if e:
            blocked.append({"ticker": tk, "reason": f"không đo được ADV: {e}"})
            continue
        if data_date:
            try:
                lag_days = (dt.date.fromisoformat(asof) - dt.date.fromisoformat(data_date)).days
            except Exception:
                lag_days = None
            if lag_days is not None and lag_days > LAG_ADV_MAX_STALE_DAYS:
                blocked.append({"ticker": tk, "reason": f"ADV data {data_date} cũ {lag_days} ngày "
                                                        f"(> {LAG_ADV_MAX_STALE_DAYS})"})
                continue
        if not adv or adv <= 0:
            blocked.append({"ticker": tk, "reason": f"ADV ≤ 0 (data {data_date})"})
            continue

        used = l1_used.get(tk, {})
        cap_i = LAG_ADV_PCT * adv * share - float(used.get("value_vnd", 0.0))
        sellable = int(bpos.get(tk, {}).get("sellable", d["qty"]))
        avail_qty = min(int(d["qty"]), sellable) - int(used.get("qty", 0))
        if cap_i <= 0 or avail_qty < LOT:
            blocked.append({"ticker": tk, "reason":
                            f"hết dư địa sau phần L1 đã đề xuất (trần còn {cap_i:,.0f}đ, "
                            f"còn bán được {max(avail_qty, 0):,}cp)"})
            continue
        pool[tk] = {"px": px, "qty": int(d["qty"]), "sellable": sellable,
                    "avail_qty": avail_qty, "cap_remaining_vnd": cap_i, "mv": d["mv"],
                    "adv_vnd": adv, "adv_data_date": data_date, "lots": d["lots"],
                    "sold_qty": 0}
    return pool, blocked, None


def allocate(needed, pool, ceiling=None):
    """Chia `needed` VND ra lệnh bán theo mã: pro-rata theo MV hiện tại, làm tròn XUỐNG lô, phần
    dư phân bổ theo largest-remainder; nếu vẫn còn thiếu thì **làm tròn LÊN đúng 1 lô rẻ nhất còn
    dư địa** (phương án C — xem khối chú thích ở cuối hàm), luôn trong mọi trần/khả năng bán.

    `ceiling`: trần CỨNG cho TỔNG giá trị bán (VND) = trần TỔNG/phiên còn lại. Lô làm tròn LÊN chỉ
    được thêm khi tổng vẫn ≤ `ceiling`. None = không có trần ngoài (chỉ selfcheck dùng).

    Trả {ticker: qty} (chỉ mã có qty ≥ 1 lô). KHÔNG cập nhật `pool` — caller tự trừ."""
    if needed <= 0 or not pool:
        return {}
    mv_base = sum(d["mv"] for d in pool.values())
    if mv_base <= 0:
        return {}

    def headroom_qty(tk):
        d = pool[tk]
        by_cap = round_lot(d["cap_remaining_vnd"] / d["px"])
        return max(0, min(round_lot(d["avail_qty"] - d["sold_qty"]), by_cap))

    want = {tk: (pool[tk]["mv"] / mv_base) * needed for tk in pool}
    alloc = {}
    for tk in sorted(pool):
        d = pool[tk]
        q = min(round_lot(want[tk] / d["px"]), headroom_qty(tk))
        alloc[tk] = max(0, round_lot(q))

    spent = sum(alloc[tk] * pool[tk]["px"] for tk in alloc)
    while True:
        residual = needed - spent
        cands = [tk for tk in pool
                 if alloc[tk] + LOT <= headroom_qty(tk)
                 and LOT * pool[tk]["px"] <= residual + 1e-6]
        if not cands:
            break
        # largest-remainder: mã còn thiếu nhiều nhất so với phần pro-rata của nó được ưu tiên.
        tk = min(cands, key=lambda t: (-(want[t] - alloc[t] * pool[t]["px"]), t))
        alloc[tk] += LOT
        spent += LOT * pool[tk]["px"]

    # ── (C) LÀM TRÒN LÊN đúng 1 lô — user John duyệt 2026-08-06 (job Taylor_20260806_033014) ──
    # Vòng lặp trên dừng khi MỌI lô còn dư địa đều ĐẮT HƠN phần dư `needed − spent`, nên thêm đúng
    # 1 lô bất kỳ trong số đó CHẮC CHẮN đưa `spent` vượt `needed` ⇒ thu ròng ≥ phần thiếu của lệnh
    # mua ⇒ lệnh mua không bị co. Đây là chỗ ĐẢO bất biến cũ "Σ bán ≤ needed": đo 2026-08-06 trên
    # sổ thật, hụt 1.792đ vẫn làm MẤT TRỌN 10tr lệnh mua (chân mua `round_lot(min(tv,bp)/px)` không
    # có dung sai) — bán dư ≤ 1 lô PARK rẻ nhất là giá phải trả, có cận trên chặt:
    #     needed ≤ Σ bán < needed + (giá trị 1 lô rẻ nhất còn dư địa)
    # Mọi trần CỨNG vẫn nguyên: per-name `cap_remaining_vnd` + sellable/T+2 (`headroom_qty`) và
    # trần TỔNG/phiên (`ceiling`). Không lô nào lọt hết các trần ⇒ KHÔNG thêm, ca đó co lệnh y cũ.
    if spent < needed - 1e-6:
        cands = [tk for tk in pool
                 if alloc[tk] + LOT <= headroom_qty(tk)
                 and (ceiling is None or spent + LOT * pool[tk]["px"] <= ceiling + 1e-6)]
        if cands:
            alloc[min(cands, key=lambda t: (LOT * pool[t]["px"], t))] += LOT
    return {tk: q for tk, q in alloc.items() if q >= LOT}


def _fifo_lots(lots, qty):
    """Lô bị tiêu thụ, đúng thứ tự entry_date (để audit được) — y hệt L1."""
    remain, out = int(qty), []
    for lot in sorted(lots, key=lambda x: (x["entry_date"], x.get("source", ""))):
        if remain <= 0:
            break
        take = min(lot["qty"], remain)
        out.append({"entry_date": lot["entry_date"], "qty": take,
                    "cost_price": lot["price"], "source": lot.get("source", "")})
        remain -= take
    return out


# ─────────────────────────────────────────────────────────────────── lõi tính

def compute_jit_unpark(account_label, asof=None, orders=None, holdings=None, plan_path=None,
                       share_override=None, adv_fn=None, day_cap_override=None,
                       margin_room_vnd=DEFAULT_MARGIN_ROOM_VND, l1_result=None):
    """Trả dict mô tả đầy đủ quyết định. `*_override`/`adv_fn`/`holdings`/`orders` chỉ để
    selfcheck bơm dữ liệu; production để None."""
    asof = asof or today_ict()
    adv_fn = adv_fn or _adv_for_gate
    h = holdings if holdings is not None else park_holdings(account_label, asof)

    out = {"layer": "L2_JIT_UNPARK", "account_label": account_label, "asof": asof,
           "park_mv_vnd": h["park_mv_vnd"], "cash_available_vnd": h["cash_available_vnd"],
           "reconcile_ok": h["reconcile"]["ok"],
           "unverified_tickers": h["unverified_tickers"],
           "excluded_tickers": h["excluded_tickers"],
           "margin_room_vnd": float(margin_room_vnd),
           "friction": ETF_FRICTION,
           "orders": [], "buy_amendments": [], "blocked": [], "notes": []}

    # ── Cổng 0: sổ chưa đối soát được ─────────────────────────────────────────
    # Song song với `compute_park_trim.py` cùng bản vá 2026-08-10 (xem README ở
    # agents/Taylor/pending_park_trim_partial_reconcile_20260810/) — nhưng ĐƠN GIẢN HƠN HẲN, và
    # lý do đáng ghi lại: L2 **không có mẫu số nào để méo**. `park_mv_vnd` ở đây chỉ dùng để IN
    # RA (dòng `out` này + bản in CLI); cỡ lệnh bán suy từ nhu cầu tiền của TỪNG lệnh mua và số
    # cp bán được của TỪNG mã, không từ `0,8 × pool`. Vì vậy L2 chỉ cần: (a) không chặn cả tài
    # khoản khi lệch một phía, (b) cấm bán chính mã lệch. KHÔNG cần hiệu chỉnh `park_mv`.
    #
    # Vì sao PHẢI vá cùng lúc với L1, không để lại sau: hai cổng đọc CÙNG một `h["reconcile"]`.
    # Vá mỗi L1 ⇒ plan có lệnh trim nhưng đường cấp vốn JIT cho lệnh MUA vẫn chết ⇒ vẫn không
    # vào được lệnh ở phiên entry chuẩn = vẫn đúng chế độ hỏng 2026-08-06, chỉ khác chỗ chết.
    out["reconcile_partial"] = False
    if not h["reconcile"]["ok"]:
        mismatches = h["reconcile"]["mismatches"]
        over = [m for m in mismatches if m["diff"] > 0]
        if over:
            out["decision"] = "BLOCKED_RECONCILE"
            out["notes"].append(
                "sổ lô LỆCH theo hướng SỔ NHIỀU HƠN broker (diff>0) ⇒ không sinh đề xuất nào — "
                "chữ ký kế toán hỏng (ghost order / fill sót journal), cần người xem. "
                f"Lệch: {mismatches}")
            return out
        out["reconcile_partial"] = True
        # Cưỡng chế TẠI ĐÂY, không giả định caller đã khai (cùng lý do như L1).
        out["unverified_tickers"] = sorted(set(out["unverified_tickers"])
                                           | {m["ticker"] for m in mismatches})
        out["notes"].insert(0, (
            "⚠️ ĐỐI SOÁT LỆCH MỘT PHÍA (broker NHIỀU HƠN sổ) — vẫn cấp vốn bằng các mã PARK KHỚP "
            "TUYỆT ĐỐI; mã lệch bị CẤM bán. Cỡ lệnh L2 không phụ thuộc mẫu số pool nên phần lệch "
            "không làm sai số tiền. Chữ ký này thường là corp action chưa vào "
            f"data/corp_actions.json — NGƯỜI vẫn phải xử lý dứt điểm. Lệch: {mismatches}"))

    # ── Đầu vào plan ─────────────────────────────────────────────────────────
    if orders is None:
        orders, ppath, perr = load_plan_orders(account_label, asof, plan_path)
        out["plan_path"] = os.path.basename(ppath)
        if perr:
            out["decision"] = "BLOCKED_NO_PLAN"
            out["notes"].append(f"{perr} ⇒ không có lệnh mua nào để xét (L2 chỉ chạy khi có lệnh "
                                f"mua BAL/LAG thật)")
            return out
    buys = trigger_orders(orders)
    out["n_buy_orders_bal_lag"] = len(buys)
    if not buys:
        out["decision"] = "NO_TRIGGER"
        out["notes"].append("không có lệnh MUA book BAL/LAG trong plan ⇒ L2 no-op "
                            "(đúng thiết kế: L2 chỉ chạy khi có lệnh mua thật)")
        return out

    cash = float(h["cash_available_vnd"] or 0)
    out["cash_start_vnd"] = cash

    # ── Trần TỔNG/phiên — DÙNG LẠI `_etf_day_cap` của L1, không đặt trần mới ──
    if day_cap_override is not None:
        day_cap, cap_err = float(day_cap_override), None
    else:
        day_cap, _basket, cap_err = etf_day_cap_live(asof)
    if cap_err or day_cap is None or day_cap <= 0:
        out["decision"] = "BLOCKED_DAYCAP"
        out["notes"].append(f"không đo được trần thanh khoản rổ ({cap_err}) ⇒ fail-closed, "
                            f"không bán PARK")
        return out

    # ── Phần L1 đã tiêu trong cùng phiên (nếu có) ────────────────────────────
    l1_used, l1_total = {}, 0.0
    if l1_result:
        for o in (l1_result.get("orders") or []):
            v = float(o.get("value_vnd") or 0)
            d = l1_used.setdefault(o["ticker"], {"value_vnd": 0.0, "qty": 0})
            d["value_vnd"] += v
            d["qty"] += int(o.get("qty") or 0)
            l1_total += v
        out["l1_reserved_vnd"] = l1_total
        out["l1_reserved_tickers"] = sorted(l1_used)
    day_cap_remaining = day_cap - l1_total
    out["etf_day_cap_vnd"] = day_cap
    out["etf_day_cap_remaining_start_vnd"] = day_cap_remaining

    share, live_labels, share_err = (share_override, None, None) if share_override is not None \
        else live_share()
    if share_err or not share:
        out["decision"] = "BLOCKED_SHARE"
        out["notes"].append(f"{share_err} ⇒ fail-closed, không bán PARK")
        return out
    out["adv_share"] = share
    out["live_labels"] = live_labels

    pool, blocked, pool_err = build_pool(h, asof, share, adv_fn, l1_used)
    out["blocked"] = blocked
    if pool_err:
        out["decision"] = "BLOCKED_BOOK_INVARIANT"
        out["notes"].append(f"{pool_err} ⇒ fail-closed, không bán gì")
        return out

    # ── Duyệt từng lệnh mua theo thứ tự plan ─────────────────────────────────
    sells = {}          # ticker → qty tích luỹ trong phiên
    any_trigger = False
    for o in buys:
        oid = o.get("id") or f"BUY-{o.get('ticker')}"
        px_ref = _ref_price(o)
        qty0 = int(o.get("qty") or 0)
        if px_ref is None or px_ref <= 0 or qty0 <= 0:
            out["buy_amendments"].append({"order_id": oid, "ticker": o.get("ticker"),
                                          "status": "BLOCKED_NO_REF",
                                          "reason": "thiếu ref_price/qty hợp lệ ⇒ không xét"})
            continue
        tv0 = qty0 * px_ref
        rec = {"order_id": oid, "ticker": o.get("ticker"), "book": norm_book(o.get("book")),
               "play_type": o.get("play_type"), "qty_plan": qty0, "ref_price": px_ref,
               "target_value_vnd": tv0, "cash_before_vnd": cash, "jit_sell_vnd": 0.0,
               "jit_proceeds_net_vnd": 0.0}

        triggered = cash < tv0 * JIT_TRIGGER_FRAC
        gross = net = 0.0
        if triggered:
            any_trigger = True
            # Phương án (B), user John duyệt 2026-08-06 (job Taylor_20260806_025613): GROSS-UP
            # phí ma sát. Engine bán cổ phần LẺ nên `needed = tv0 - cash` rồi fill nốt phần thiếu
            # ở phiên sau; live có MỘT phiên nên phải bán đủ để **thu ròng** bằng phần thiếu:
            #     needed × (1 − friction) = tv0 − cash   ⇒   needed = (tv0 − cash)/(1 − friction)
            # Dùng đúng hằng số ETF_FRICTION đã PORT, KHÔNG thêm tham số mới.
            needed = min((tv0 - max(cash, 0.0)) / (1.0 - ETF_FRICTION), day_cap_remaining)
            rec["needed_vnd"] = max(needed, 0.0)
            rec["day_cap_remaining_before_vnd"] = day_cap_remaining
            # `ceiling=day_cap_remaining`: lô làm tròn LÊN của (C) vẫn phải lọt trần TỔNG/phiên.
            # Khi trần này ĐANG BÓ (needed == day_cap_remaining) thì không lô nào lọt ⇒ (C) tự tắt,
            # hành vi y hệt trước — đúng: trần thanh khoản là trần CỨNG, không nới vì lệnh mua.
            alloc = allocate(needed, pool, ceiling=day_cap_remaining) if needed > 0 else {}
            mv_pool = sum(x["mv"] for x in pool.values()) or 1.0
            for tk in sorted(alloc):
                d = pool[tk]
                q = alloc[tk]
                val = q * d["px"]
                out["orders"].append({
                    "ticker": tk, "side": "sell", "qty": int(q), "ref_price": d["px"],
                    "value_vnd": val, "book": "PARK", "play_type": "JIT_UNPARK",
                    "for_order_id": oid, "for_ticker": o.get("ticker"),
                    "weight_in_park": d["mv"] / mv_pool,
                    "adv_cap_remaining_vnd": d["cap_remaining_vnd"], "adv_vnd": d["adv_vnd"],
                    "adv_data_date": d["adv_data_date"], "sellable": d["sellable"],
                    "fifo_lots": _fifo_lots(d["lots"], q),
                    "reason": (f"L2 JIT: tài trợ {oid} ({o.get('ticker')}) — cần "
                               f"{needed/1e6:,.1f}tr, bán pro-rata PARK w={d['mv']/mv_pool:.1%}"),
                })
                d["sold_qty"] += q
                d["cap_remaining_vnd"] -= val
                sells[tk] = sells.get(tk, 0) + q
                gross += val
            net = gross * (1.0 - ETF_FRICTION)
            cash += net
            day_cap_remaining -= gross
            rec.update({"jit_sell_vnd": gross, "jit_proceeds_net_vnd": net,
                        "jit_shortfall_vnd": max(0.0, needed - gross),
                        "day_cap_binding": needed < (tv0 - max(rec["cash_before_vnd"], 0.0)) - 1})

        # ── Fallback engine (dòng 1189-1195) — chạy SAU JIT, trên cash mới ────
        bp = cash + float(margin_room_vnd)
        tv = tv0 if bp >= tv0 * JIT_TRIGGER_FRAC else bp * SHRINK_FRAC
        rec["buying_power_vnd"] = bp
        if tv < MIN_ORDER_VND:
            rec.update({"status": "DROP", "qty_final": 0, "target_value_final_vnd": 0.0,
                        "cash_after_vnd": cash,
                        "reason": f"sức mua sau JIT chỉ còn {tv/1e6:,.2f}tr < 1tr ⇒ engine BỎ "
                                  f"lệnh (simulate_holistic_nav.py:1195)"})
            if gross > 0:
                out["notes"].append(
                    f"⚠️ {oid}: đã đề xuất bán PARK {gross/1e6:,.1f}tr nhưng lệnh mua bị BỎ "
                    f"(<1tr) — engine cũng hành xử đúng vậy (bán trước, xét ngưỡng sau), tiền "
                    f"nằm lại ở cash. Người duyệt nên cân nhắc bỏ luôn phần bán này.")
            out["buy_amendments"].append(rec)
            continue
        # Không tiêu quá sức mua THẬT: engine fill `buy_value = min(remaining, daily_max, _bp)`
        # (dòng 1216) và fill nốt phần dư ở các phiên sau; một lệnh live chỉ có MỘT phiên nên
        # phần dư đó thành ra co qty. Đây là khác biệt HIỆN VẬT engine-vs-live, đã ghi rõ, và
        # nó chỉ đi theo hướng thận trọng (không bao giờ đặt lệnh vượt sức mua).
        qf = round_lot(min(tv, bp) / px_ref)
        if qf < LOT:
            rec.update({"status": "DROP", "qty_final": 0, "target_value_final_vnd": 0.0,
                        "cash_after_vnd": cash,
                        "reason": f"sức mua {bp/1e6:,.2f}tr < 1 lô @ {px_ref:,.0f} ⇒ bỏ lệnh"})
            out["buy_amendments"].append(rec)
            continue
        spend = qf * px_ref
        cash -= spend
        if qf >= qty0:
            rec.update({"status": "FUNDED_BY_JIT" if triggered else "FUNDED_BY_CASH",
                        "reason": ((f"bán PARK {gross/1e6:,.1f}tr (thu ròng {net/1e6:,.1f}tr sau "
                                    f"friction {ETF_FRICTION:.2%}) ⇒ đủ tiền mua nguyên lệnh")
                                   if triggered else
                                   (f"cash {rec['cash_before_vnd']/1e6:,.1f}tr ≥ "
                                    f"{JIT_TRIGGER_FRAC:.2f}×target {tv0/1e6:,.1f}tr ⇒ không cần "
                                    f"bán PARK"))})
        else:
            rec.update({"status": "SHRINK",
                        "reason": (f"sức mua sau JIT {bp/1e6:,.1f}tr < target {tv0/1e6:,.1f}tr ⇒ "
                                   f"CO lệnh về {tv/1e6:,.1f}tr ({qty0:,}cp → {int(qf):,}cp). "
                                   f"Live hôm nay defer NGUYÊN lệnh — đây chính là chỗ lệch với "
                                   f"engine.")})
        rec.update({"qty_final": int(qf), "target_value_final_vnd": spend,
                    "cash_after_vnd": cash})
        out["buy_amendments"].append(rec)

    out["cash_end_vnd"] = cash
    out["etf_day_cap_remaining_end_vnd"] = day_cap_remaining
    out["jit_sell_total_vnd"] = sum(o["value_vnd"] for o in out["orders"])
    out["sells_by_ticker"] = dict(sorted(sells.items()))
    if not any_trigger:
        out["decision"] = "NO_JIT_NEEDED"
        out["notes"].append("mọi lệnh mua BAL/LAG đều đủ tiền mặt ⇒ không bán PARK")
    elif out["orders"]:
        out["decision"] = "JIT"
    elif not pool:
        out["decision"] = "BLOCKED_ALL_NAMES"
        out["notes"].append("có lệnh mua thiếu tiền nhưng KHÔNG mã PARK nào đủ điều kiện bán "
                            "(trần ADV / UNVERIFIED / excluded / T+2) ⇒ lệnh mua bị co hoặc bỏ")
    else:
        out["decision"] = "NO_SELL_POSSIBLE"
        out["notes"].append("có lệnh mua thiếu tiền, rổ PARK vẫn bán được, nhưng phần thiếu nhỏ "
                            "hơn 1 lô chẵn (hoặc hết trần/phiên) ⇒ không sinh lệnh bán; lệnh mua "
                            "bị co theo sức mua hiện có")
    return out


# ─────────────────────────────────────────────────────────────────────── CLI

def main():
    ap = argparse.ArgumentParser(
        description="L2 JIT unpark — CHỈ ĐỌC, đề xuất lệnh bán PARK tài trợ lệnh mua BAL/LAG")
    ap.add_argument("--account", required=True)
    ap.add_argument("--asof", default=None)
    ap.add_argument("--plan", default=None, help="đường dẫn plan JSON (mặc định: "
                                                 "data/trade_plans/plan_<account>_<asof>.json)")
    ap.add_argument("--l1-json", default=None,
                    help="đầu ra `compute_park_trim.py --out` của CÙNG phiên, để trừ trước phần "
                         "trần/cổ phiếu L1 đã đề xuất (không truyền = coi như L1 không chạy)")
    ap.add_argument("--margin-room", type=float, default=DEFAULT_MARGIN_ROOM_VND,
                    help="dư địa margin cho lệnh BAL/LAG (VND). Mặc định 0 = đúng cấu hình R3 "
                         "đã pin (V2.5 DISABLED); đổi khác là thay đổi chính sách, cần user duyệt")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None,
                    help="ghi kết quả JSON ra file (khuyến nghị cho consumer máy đọc — stdout "
                         "còn có dòng log kết nối broker nên không parse thẳng được)")
    a = ap.parse_args()
    l1 = json.load(open(a.l1_json, encoding="utf-8")) if a.l1_json else None
    r = compute_jit_unpark(a.account, a.asof, plan_path=a.plan, margin_room_vnd=a.margin_room,
                           l1_result=l1)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=1, default=str)
        print(f"[jit_unpark] JSON → {a.out}")
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
        return 0
    print(f"=== L2 JIT-UNPARK (ĐỀ XUẤT, chưa vào plan nào) — {r['account_label']} "
          f"asof={r['asof']} — {r['decision']} ===")
    if "cash_start_vnd" in r:
        print(f"  cash đầu {r['cash_start_vnd']/1e6:,.2f}tr | PARK {r['park_mv_vnd']/1e6:,.2f}tr "
              f"| {r.get('n_buy_orders_bal_lag', 0)} lệnh mua BAL/LAG")
    if "etf_day_cap_vnd" in r:
        print(f"  trần TỔNG/phiên = {r['etf_day_cap_vnd']/1e9:,.2f} tỷ; còn lại đầu kỳ "
              f"{r['etf_day_cap_remaining_start_vnd']/1e9:,.2f} tỷ"
              + (f" (đã trừ L1 {r['l1_reserved_vnd']/1e6:,.1f}tr)" if r.get("l1_reserved_vnd")
                 else ""))
    for m in r["buy_amendments"]:
        print(f"  · {m['order_id']:<16} {m.get('status'):<16} "
              f"{m.get('qty_plan', 0):>7,}cp → {m.get('qty_final', 0):>7,}cp   "
              f"bán PARK {m.get('jit_sell_vnd', 0)/1e6:>7,.2f}tr")
        print(f"      {m.get('reason', '')}")
    for o in r["orders"]:
        print(f"   BÁN {o['ticker']:<5} {o['qty']:>7,}cp @ {o['ref_price']:>9,.0f} = "
              f"{o['value_vnd']/1e6:>8,.2f}tr  (cho {o['for_order_id']})")
    if r["orders"]:
        print(f"  Σ bán PARK đề xuất = {r['jit_sell_total_vnd']/1e6:,.2f}tr")
    for b in r["blocked"]:
        print(f"   – bỏ qua {b['ticker']}: {b['reason']}")
    for n in r["notes"]:
        print(f"   ⚠ {n}")
    print("  (script CHỈ ĐỌC — không đặt lệnh, không ghi plan; đề xuất vẫn phải qua duyệt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
