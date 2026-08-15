# -*- coding: utf-8 -*-
"""exdate_gate.py — MỘT cổng, MỘT chỗ: lệnh của ngày GDKHQ phải đứng trọn trong hệ quy chiếu MỚI.

Thiết kế D2 của `mike/agents/Taylor/research/exdate_order_pipeline_20260815/README.md` §8
(job Taylor_20260815_050425 thiết kế; Taylor_20260815_054822 code hoá).

VÌ SAO MỘT CỔNG chứ không phải vá từng nơi: README §1 liệt kê **12 đường** (A→L) mà một con
số giá có thể đi vào một lệnh, và §5.3 chỉ ra bản vá NAV 08-11 đã vá đúng MỘT call-site rồi
để hở đúng kiểu §28 `coding_guidelines` cảnh báo. Vá 12 chỗ là mời cái thứ 13. Cổng này đứng
ở chỗ HẸP NHẤT mà MỌI plan live phải đi qua — cascade của `bot_execute.py`, cùng vị trí và
cùng lý lẽ với `filter_excluded_tickers` / `cap_lag_orders` / `filter_lag_rating_orders`
("enforce ở ĐÂY, không dựa vào plan generator nhớ áp").

BỐN VIỆC cổng làm cho mã có `exright_date == plan_date` (README §8-D2, đúng thứ tự):
  1. `ref_price` **BẮT BUỘC** lấy từ `price_frame.resolve_reference()` (`q.ref` đã qua 5 cổng),
     cấm mọi nguồn LỊCH SỬ.
  2. `qty` tính LẠI trên chính `ref_price` đó — giữ nguyên GIÁ TRỊ (VND) mà plan đã chủ ý,
     không giữ nguyên SỐ LƯỢNG. Số lượng là thứ dẫn xuất; giá trị mới là ý định của sizing.
  3. `hard_no_chase_ceiling_vnd` dựng lại trên `ref_price` đó.
  4. Anchor LỊCH SỬ quy đổi bằng hệ số của chính sự kiện, hoặc BỎ mã khỏi plan.

Không xác định được `exright_date`, hoặc `resolve_reference` fail bất kỳ cổng nào ⇒ **KHÔNG
sinh lệnh cho mã đó**, ghi lý do vào `notes[]`. Không đoán, không rơi về mặc định.

BẤT BIẾN QUAN TRỌNG NHẤT — **ngày THƯỜNG cổng này là NO-OP TUYỆT ĐỐI**: không có sự kiện ⇒
không mã nào lọt vào vòng lặp ⇒ 0 lệnh bị đọc, 0 lệnh bị sửa, 0 lời gọi DNSE thêm. Và ngay
trong ngày GDKHQ, nếu plan đã đứng sẵn ở hệ MỚI (ca thật MBB 2026-08-11: plan ghi 20.200,
đúng) thì mọi phép tính lại đều trả về CHÍNH con số cũ ⇒ vẫn 0 thay đổi. Cổng chỉ động vào
những lệnh THẬT SỰ sai hệ quy chiếu.

TẠI SAO BÁN LẠI KHẮT KHE HƠN MUA: vào ngày cổ tức CP/thưởng/quyền mua, số CP THẬT ở broker
NHÂN LÊN nhưng qty trong plan thì không. Đây chính là cơ chế "bán ảo" README §2 đo được (VHM
×2,0 ⇒ lệnh BÁN 500cp ảo đúng bằng phần thưởng vừa nhận). Không có cách nào suy ĐÚNG ý định
gốc từ một con số qty ở hệ cũ — bán 500 nghĩa là "bán nửa vị thế" hay "bán 500cp"? ⇒ với sự
kiện làm ĐỔI SỐ LƯỢNG, lệnh bán bị BỎ, không đoán. Cổ tức TIỀN MẶT không đổi số lượng nên
lệnh bán giữ nguyên qty, chỉ làm tươi `ref_price`.
"""
import datetime as dt
import math

from . import price_frame as pf
from .no_chase_ceiling import RULE_A, rule_a_ceiling, rule_a_in_force
from .vn_market import LOT, round_lot

# Ngưỡng "đáng gọi là đã đổi": dưới mức này thì tính lại ra đúng con số cũ (plan vốn đã đứng ở
# hệ MỚI). Dùng để phân biệt SỬA THẬT với làm-tròn-lại, cho log và cho phép kiểm hồi quy
# "0 lệnh đổi giá trị" phát biểu được chính xác.
PRICE_EPS_VND = 0.5


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def apply_exdate_gate(plan, broker, plan_date=None, events_map=None, resolver=None,
                      position_rows=None):
    """Cưỡng chế MỘT hệ quy chiếu cho mọi lệnh của ngày GDKHQ → (plan, adjustments).

    `plan` bị sửa TẠI CHỖ (giống `cap_lag_orders`/`apply_capit_lever` trong cùng cascade).
    `adjustments` = list dict `{action, ticker, reason, ...}` để caller in/log:
        REPRICED       — ref_price/qty/trần đã quy về hệ MỚI (có `*_before`/`*_after`)
        BLOCKED        — lệnh bị BỎ khỏi plan, kèm lý do cổng nào từ chối
        CALENDAR_FAIL  — không tra được lịch sự kiện ⇒ **KHÔNG chặn** (xem dưới)
        NO_EVENT       — có mã trong plan nhưng không mã nào GDKHQ hôm nay (1 dòng, thông tin)

    `resolver` cho phép selfcheck tiêm một `resolve_reference` tất định (chữ ký
    `(broker, ticker, session_date, events_map=..., position_rows=...)`); None ⇒ dùng
    `price_frame.resolve_reference`.

    ⚠️ QUYẾT ĐỊNH CÓ CHỦ Ý — tra lịch HỎNG thì cổng **FAIL-OPEN**, và đó không phải sơ suất:
    nguồn lịch là BigQuery, một hệ THỨ BA nằm ngoài đường đặt lệnh (DNSE). Cho nó quyền chặn
    toàn bộ giao dịch của một phiên là trao chìa khoá dừng-giao-dịch cho một phụ thuộc không
    ai giám sát theo phiên — cùng loại rủi ro mà `filter_lag_rating_orders` giải quyết bằng
    FAIL_OPEN + báo TO. Ở ĐÚNG NGÀY có sự kiện thì fail-open này KHÔNG để hở thật: mọi lệnh
    luật A vẫn đi qua `check_ref_vs_live()` ngay trước khi đặt (commit 59f9569), và một cú
    lật hệ quy chiếu ≥5% thì lệch xa dung sai 1% của cổng đó. Bằng chứng phải kêu to, không
    được im: caller PHẢI in `CALENDAR_FAIL` ở mức cảnh báo.
    """
    resolver = resolver or pf.resolve_reference
    plan_date = str(plan_date or getattr(plan, "plan_date", "") or "")[:10]
    adj = []
    orders = list(getattr(plan, "orders", []) or [])
    tickers = sorted({str(getattr(o, "ticker", "") or "").upper() for o in orders})
    tickers = [t for t in tickers if t]
    if not tickers or not plan_date:
        return plan, adj

    if events_map is None:
        try:
            d = dt.date.fromisoformat(plan_date)
            evs = pf.pricing_events(tickers, since=(d - dt.timedelta(days=1)).isoformat(),
                                    until=d.isoformat())
            events_map = pf.events_by_ticker_date(evs)
        except Exception as exc:                                    # noqa: BLE001
            adj.append({"action": "CALENDAR_FAIL", "ticker": None,
                        "reason": (f"KHÔNG tra được lịch sự kiện quyền cho {len(tickers)} mã "
                                   f"({type(exc).__name__}: {exc}) — cổng GDKHQ KHÔNG chạy "
                                   f"phiên này. Lưới còn lại: check_ref_vs_live() tầng đặt lệnh.")})
            return plan, adj

    ex_tickers = sorted({t for t in tickers if pf.events_on(events_map, t, plan_date)})
    if not ex_tickers:
        adj.append({"action": "NO_EVENT", "ticker": None,
                    "reason": f"không mã nào trong {len(tickers)} mã của plan có GDKHQ "
                              f"{plan_date} — cổng không đụng lệnh nào"})
        return plan, adj

    keep, dropped_ids = [], set()
    frames = {}
    for tk in ex_tickers:
        try:
            frames[tk] = resolver(broker, tk, plan_date, events_map=events_map,
                                  position_rows=position_rows)
        except Exception as exc:                                    # noqa: BLE001
            frames[tk] = {"ok": False, "gate": "GX", "ex_today": True,
                          "reason": f"resolve_reference lỗi: {type(exc).__name__}: {exc}"}

    for o in orders:
        tk = str(getattr(o, "ticker", "") or "").upper()
        if tk not in ex_tickers:
            keep.append(o)
            continue
        fr = frames.get(tk) or {}
        evs = pf.events_on(events_map, tk, plan_date)
        if not fr.get("ok"):
            dropped_ids.add(getattr(o, "id", None))
            adj.append({"action": "BLOCKED", "ticker": tk, "id": getattr(o, "id", None),
                        "side": getattr(o, "side", None), "qty_before": getattr(o, "qty", None),
                        "gate": fr.get("gate"),
                        "reason": (f"NGÀY GDKHQ {plan_date} nhưng KHÔNG chốt được hệ quy chiếu "
                                   f"(cổng {fr.get('gate')}): {fr.get('reason')}")})
            continue
        ok, note = _reprice_order(o, fr, evs)
        if not ok:
            dropped_ids.add(getattr(o, "id", None))
            adj.append({"action": "BLOCKED", "ticker": tk, "id": getattr(o, "id", None),
                        "side": getattr(o, "side", None), "qty_before": getattr(o, "qty", None),
                        "gate": "D2", "reason": note})
            continue
        keep.append(o)
        if note:
            adj.append(note)

    plan.orders = keep
    if dropped_ids:
        notes = list(getattr(plan, "notes", None) or [])
        notes.append(f"[GDKHQ] {len(dropped_ids)} lệnh bị BỎ vì không chốt được hệ quy chiếu "
                     f"ngày {plan_date}: {sorted(x for x in dropped_ids if x)}")
        try:
            plan.notes = notes
        except Exception:                                           # noqa: BLE001
            pass
    return plan, adj


def _reprice_order(o, frame, events):
    """Quy MỘT lệnh về hệ quy chiếu mới, tại chỗ → (ok, note_dict | lý do BỎ | None).

    None = hợp lệ và KHÔNG có gì đổi (plan vốn đã ở hệ mới) — im lặng đúng chỗ, để dòng log
    duy nhất xuất hiện là dòng nói về một thay đổi THẬT.
    """
    ref_new = _f(frame.get("ref_price"))
    ref_old = _f(getattr(o, "ref_price", None))
    if ref_new is None or ref_new <= 0:
        return False, "resolve_reference báo ok nhưng không có ref_price hợp lệ"
    if ref_old is None or ref_old <= 0:
        return False, f"lệnh thiếu/rác ref_price ({getattr(o, 'ref_price', None)!r})"

    adjm, _ = pf.adjustment(events)
    if adjm is None:
        return False, "không dựng được hệ số điều chỉnh của sự kiện (đã fail-closed ở G5)"
    changes_share_count = adjm["ratio"] > 0
    side = str(getattr(o, "side", "") or "").lower()
    qty_old = int(getattr(o, "qty", 0) or 0)

    # ── BÁN ────────────────────────────────────────────────────────────────────────────────
    if side == "sell":
        if changes_share_count:
            return False, (
                f"lệnh BÁN {qty_old:,}cp lập ở hệ quy chiếu CŨ, còn sự kiện hôm nay NHÂN số CP "
                f"thật lên ×{adjm['share_factor']:.4f} — không suy được ý định gốc từ một con số "
                f"qty (bán nửa vị thế? bán đúng 500cp?). Đây đúng cơ chế 'bán ảo' README §2 "
                f"(VHM ×2,0 sinh lệnh bán 500cp bằng đúng phần thưởng vừa nhận) ⇒ BỎ, không đoán")
        if abs(ref_new - ref_old) <= PRICE_EPS_VND:
            return True, None
        o.ref_price = ref_new
        return True, {"action": "REPRICED", "ticker": o.ticker, "id": getattr(o, "id", None),
                      "side": "sell", "ref_before": ref_old, "ref_after": ref_new,
                      "qty_before": qty_old, "qty_after": qty_old,
                      "reason": (f"cổ tức TIỀN MẶT (số CP không đổi): làm tươi ref_price "
                                 f"{ref_old:,.0f} → {ref_new:,.0f} theo giá tham chiếu "
                                 f"chính thức phiên GDKHQ")}

    if side != "buy":
        return True, None

    # ── MUA — giữ GIÁ TRỊ, tính lại SỐ LƯỢNG ───────────────────────────────────────────────
    notional = qty_old * ref_old
    qty_new = round_lot(notional / ref_new) if ref_new > 0 else 0
    factor = ref_new / ref_old
    ceil_note = _reanchor_ceiling(o, ref_new, factor)
    if ceil_note is False:
        return False, ("không quy đổi được TRẦN giá mua sang hệ quy chiếu mới — README §8-D2 "
                       "mục 4: không quy đổi chắc chắn được thì BỎ mã khỏi plan")

    if abs(ref_new - ref_old) <= PRICE_EPS_VND and qty_new == qty_old and not ceil_note:
        return True, None
    if qty_new < LOT:
        return False, (f"tính lại trên giá tham chiếu đúng {ref_new:,.0f}đ thì giá trị lệnh "
                       f"{notional:,.0f}đ không đủ 1 lô — BỎ thay vì đặt một lệnh không có "
                       f"trong ý định của plan")
    o.ref_price = ref_new
    o.qty = qty_new
    return True, {"action": "REPRICED", "ticker": o.ticker, "id": getattr(o, "id", None),
                  "side": "buy", "ref_before": ref_old, "ref_after": ref_new,
                  "qty_before": qty_old, "qty_after": qty_new,
                  "ceiling_before": ceil_note.get("before") if ceil_note else None,
                  "ceiling_after": ceil_note.get("after") if ceil_note else None,
                  "reason": (f"ngày GDKHQ: ref_price {ref_old:,.0f} → {ref_new:,.0f} "
                             f"({factor - 1:+.2%}), giữ nguyên giá trị {notional:,.0f}đ nên "
                             f"qty {qty_old:,} → {qty_new:,}cp"
                             + (f"; {ceil_note['reason']}" if ceil_note else ""))}


def _reanchor_ceiling(o, ref_new, factor):
    """Quy TRẦN giá mua về hệ mới → dict mô tả thay đổi | None (không có gì đổi) | False (BỎ).

    Hai nhánh, cố ý KHÔNG hợp nhất:

      · **Luật A đang hiệu lực** ⇒ neo lại vào chính giá tham chiếu chính thức của phiên
        GDKHQ, giữ nguyên τ. Đây là phép DỊCH HỆ QUY CHIẾU, không phải đổi chính sách: cùng
        một luật, cùng một τ user đã duyệt, chỉ đứng ở đúng phiên. Không làm việc này thì
        trần cũ (dựng trên giá cum) nới ra đúng bằng độ dịch của sự kiện — ca SSI −20,1% cho
        một trần CAO HƠN CẢ GIÁ TRẦN hợp lệ của phiên, tức luật A bị vô hiệu hoá, im lặng.

      · **Trần LỊCH SỬ không khai luật A** (di sản `entry_anchor_price`, README §6.1) ⇒ nhân
        hệ số `ref_mới / ref_cũ` của chính lệnh. Đó ĐÚNG là hệ số điều chỉnh của sự kiện, và
        đã được G5 đối soát độc lập với công thức sở dựng từ `corporate_action` ⇒ "quy đổi
        chắc chắn được" theo nghĩa README §8-D2 mục 4. Hệ số rác (≤0) ⇒ trả False ⇒ BỎ lệnh.

    KHÔNG BAO GIỜ dựng luật A cho một lệnh vốn không chạy luật A: đó là đổi chính sách trần ở
    tầng thực thi, nằm ngoài phạm vi bản vá này.
    """
    before = _f(getattr(o, "hard_no_chase_ceiling_vnd", None))
    if rule_a_in_force(o):
        tau = _f(getattr(o, "ceiling_tau", None))
        new_ceil, why = rule_a_ceiling(ref_new, tau)
        if new_ceil is None:
            return False
        if before is not None and abs(new_ceil - before) <= PRICE_EPS_VND:
            o.ceiling_anchor_price = ref_new
            return None
        o.hard_no_chase_ceiling_vnd = new_ceil
        o.ceiling_anchor_price = ref_new
        o.ceiling_rule = RULE_A
        return {"before": before, "after": new_ceil,
                "reason": (f"trần luật A neo lại vào giá tham chiếu phiên GDKHQ: "
                           f"{before:,.0f} → {new_ceil:,.0f} ({why})"
                           if before else f"trần luật A dựng lại: {why}")}
    if before is None or before <= 0:
        return None
    if not factor or factor <= 0 or not math.isfinite(factor):
        return False
    after = float(math.floor(before * factor))
    if abs(after - before) <= PRICE_EPS_VND:
        return None
    o.hard_no_chase_ceiling_vnd = after
    return {"before": before, "after": after,
            "reason": (f"trần lịch sử quy đổi ×{factor:.4f} sang hệ quy chiếu mới: "
                       f"{before:,.0f} → {after:,.0f}")}
