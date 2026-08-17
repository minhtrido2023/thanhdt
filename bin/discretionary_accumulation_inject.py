#!/usr/bin/env python3
"""discretionary_accumulation_inject.py — chèn TỰ ĐỘNG lệnh gom low-liquidity discretionary
vào plan_<account>_<plan_date>.json (book=DISCRETIONARY_SPECIAL), thay cho việc chèn thủ công
từng tranche (case TV1 tranche 1 hiện phải chèn tay).

Cơ chế (playbook Taylor 2026-07-24, memo lowliq_execution_playbook_20260724.md):
  - Mỗi vị thế đang gom = 1 state file data/trade_plans/discretionary/state_<TICKER>_<account>.json.
  - Với mỗi state active: đọc VỊ THẾ THẬT từ broker (nguồn chân lý filled_qty) + giá/KL phiên
    gần nhất từ DNSE live (KHÔNG BQ — same-day, coding_guidelines §6), gọi engine
    trading_bot.discretionary_accumulation.compute_session_order → chèn lệnh vào plan.
  - IDEMPOTENT: chạy lại trong ngày KHÔNG chèn trùng, KHÔNG đếm 2 lần filled (filled luôn tính
    lại từ broker, ledger chỉ để audit).
  - FAIL-SAFE: thiếu broker/giá/KL → KHÔNG chèn lệnh (không mua bởi thiếu thông tin).
  - KHÔNG chạm kế toán V2.4 (chỉ chèn order book=DISCRETIONARY_SPECIAL, tách hẳn).

Chạy SAU khi DollarBill ghi plan (dispatch --bg ~19:0x) và TRƯỚC send_plan_report 21:00, để
user duyệt plan đã có sẵn lệnh gom. Plan vẫn requires_user_approval → Mafee chỉ execute sau khi
user duyệt (human gate giữ nguyên).

Usage:
  discretionary_accumulation_inject.py --account SpaceX [--plan-date YYYY-MM-DD] [--dry-run]
  (bỏ --plan-date → tự dùng next_trading_day())
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, WC_ROOT)

from trading_bot.discretionary_accumulation import (
    compute_session_order, validate_state, BOOK, DYNAMIC_CEILING_SESSIONS_DEFAULT)
from trading_bot.no_chase_ceiling import ANCHOR_BASIS_OFFICIAL_REF, check_reference_snapshot
from trading_bot.config import live_dnse_labels
from trading_bot.plan_cash_commitment import gate_injected_order, replan_dropped_injection
from trading_bot.vn_market import (
    session_phase, now_ict, normalize_price_vnd, is_holiday)

_ICT_TZ = ZoneInfo("Asia/Ho_Chi_Minh")   # §16: neo TZ tường minh, không tin TZ của process

# Phiên đang giao dịch (09:00–14:45 T2-T6) → day_volume của DNSE là KL DỞ DANG. Cơ chế
# opportunistic (compute_session_order) giả định day_volume là KHỐI LƯỢNG CẢ PHIÊN đã chốt để
# đo "người bán có xuất hiện không"; đọc giữa phiên = KL chưa đủ → quyết định opportunistic sai.
# → injector LIVE TỪ CHỐI chạy trong các phiên này (cron thật chạy 20:30 ICT = CLOSED). PRE
# (trước 09:00) và CLOSED (sau 14:45 / cuối tuần / lễ) đều an toàn: DNSE report phiên hoàn tất.
_SESSION_OPEN_PHASES = {"ATO", "MORNING", "LUNCH", "AFTERNOON", "ATC"}

DISC_DIR = os.path.join(WC_ROOT, "data", "trade_plans", "discretionary")
PLAN_DIR = os.path.join(WC_ROOT, "data", "trade_plans")
ACTIVE_NAV_DIR = os.path.join(WC_ROOT, "data", "execution_logs")


def _atomic_write_json(path, obj):
    """tmp + os.replace — kill giữa chừng không để lại file dở (coding_guidelines §5)."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def next_trading_day_str():
    from trading_bot.vn_market import next_trading_day
    return str(next_trading_day(dt.date.today()))


def load_active_states(account):
    """Đọc mọi state_*_<account>.json status=active. Trả (list (path, state), list bị bỏ qua).

    Danh sách BỊ BỎ QUA trả kèm là có chủ đích: chính một state `status="completed"` nằm im
    (TV1, 07-29 → 08-12) là thứ khiến toàn bộ cơ chế trần động không chạm được chương trình
    đang chạy, mà KHÔNG một artifact nào người duyệt plan đọc được nhắc tới. Caller ghi nó vào
    plan để lần sau nhìn thấy được thay vì phải suy ra.
    """
    out, skipped = [], []
    for path in sorted(glob.glob(os.path.join(DISC_DIR, f"state_*_{account}.json"))):
        try:
            state = json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            print(f"  [WARN] state file lỗi đọc, bỏ qua: {path}: {exc}")
            skipped.append({"state_file": os.path.relpath(path, WC_ROOT), "ticker": None,
                            "why": f"file lỗi đọc: {exc}"})
            continue
        rel = os.path.relpath(path, WC_ROOT)
        state["_state_file"] = rel
        if state.get("account") != account:
            print(f"  [WARN] {path}: account={state.get('account')} ≠ {account}, bỏ qua")
            skipped.append({"state_file": rel, "ticker": state.get("ticker"),
                            "why": f"account={state.get('account')} ≠ {account}"})
            continue
        if state.get("status") != "active":
            print(f"  [skip] {os.path.basename(path)}: status={state.get('status')}")
            skipped.append({"state_file": rel, "ticker": state.get("ticker"),
                            "why": f"status={state.get('status')} (≠ active) — chương trình "
                                   f"KHÔNG sinh lệnh; đúng ý thì bỏ qua, không thì bật lại state"})
            continue
        try:
            validate_state(state)
        except ValueError as exc:
            print(f"  [WARN] {path}: state không hợp lệ ({exc}) — bỏ qua, KHÔNG chèn")
            skipped.append({"state_file": rel, "ticker": state.get("ticker"),
                            "why": f"state không hợp lệ: {exc}"})
            continue
        out.append((path, state))
    return out, skipped


def broker_filled_qty(account, account_id, ticker, baseline):
    """filled_qty của CHƯƠNG TRÌNH = broker_total(ticker) − baseline_qty_before_program.
    None nếu không đọc được broker (fail-safe)."""
    try:
        from trading_bot.brokers import DNSEBroker
        b = DNSEBroker(account_id=account_id, credentials_file=None, label=account)
        b.connect()
        positions = b.get_positions()
    except Exception as exc:
        print(f"  [FAILSAFE] không đọc được broker positions ({ticker}): {exc}")
        return None, None
    total = int((positions.get(ticker) or {}).get("total", 0) or 0)
    return max(0, total - int(baseline)), b


def prev_session_market(broker, ticker):
    """Giá + turnover phiên hoàn tất gần nhất từ DNSE live (day_volume × last).
    Trả (turnover_vnd, price_vnd) — (None, None) nếu thiếu (fail-safe)."""
    try:
        q = broker.get_quote(ticker)
    except Exception as exc:
        print(f"  [FAILSAFE] DNSE quote {ticker} lỗi: {exc}")
        return None, None
    price = getattr(q, "last", None)
    vol = getattr(q, "day_volume", None)
    if not price or not vol or price <= 0 or vol <= 0:
        print(f"  [FAILSAFE] {ticker}: thiếu giá ({price}) hoặc KL ({vol}) từ DNSE")
        return None, None
    return float(vol) * float(price), float(price)


def bar_is_completed_session(bar_ts, now=None):
    """Bar 1D của DNSE (timestamp `t` = 09:00 ICT của NGÀY GIAO DỊCH đó) đã là phiên HOÀN TẤT chưa?

    True = phiên đã đóng ⇒ giá đóng cửa dùng được làm anchor.
    False = bar CHƯA hoàn tất (nến hôm nay đang chạy, hoặc bar ngày tương lai) ⇒ phải LOẠI.
    None = timestamp không parse được ⇒ caller fail-safe (bỏ trần động).

    Vì sao KHÔNG loại thẳng mọi bar mang ngày hôm nay: cron thật chạy 20:30 ICT, lúc đó phiên
    hôm nay ĐÃ đóng (14:45) nên giá đóng cửa hôm nay LÀ một phiên hoàn tất — bỏ nó đi làm anchor
    già thêm 1 phiên mà không tăng độ an toàn. Cái phải chặn là bar đọc GIỮA phiên (dry-run
    11:00) hoặc TRƯỚC phiên (PRE, 00:00–09:00, DNSE có thể trả bar stub), vì lúc đó `c` là giá
    LIVE đang chạy ⇒ trần "không đuổi giá" bị nhiễm chính cái giá nó đang đuổi.
    """
    now = now or now_ict()
    try:
        bar_date = dt.datetime.fromtimestamp(int(bar_ts), _ICT_TZ).date()
    except (TypeError, ValueError, OSError, OverflowError):
        return None
    today = now.date()
    if bar_date < today:
        return True
    if bar_date > today:
        return False                      # bar ngày tương lai = rác feed
    # Bar HÔM NAY: chỉ hoàn tất khi hôm nay là NGÀY GIAO DỊCH thật và phiên đã đóng (≥14:45).
    # Cuối tuần/lễ mà vẫn có bar mang ngày hôm nay ⇒ rác, loại (session_phase trả CLOSED cho cả
    # T7/CN nên phải kiểm lịch riêng, không dựa mỗi tên phiên).
    if now.weekday() >= 5 or is_holiday(today):
        return False
    return session_phase(now)[0] == "CLOSED"


def official_reference_price(broker, ticker):
    """Giá tham chiếu CHÍNH THỨC của phiên giao dịch kế tiếp → (giá | None, info).

    Nguồn = DNSE `q.ref` (secdef `refPrice`/`basicPrice`) — số do chính sở giao dịch công bố,
    nên đã đúng công thức RIÊNG của từng sàn và đã điều chỉnh theo giá trị quyền.

    🔴 VÌ SAO KHÔNG DÙNG `anchor_prices_for()` CHO LUẬT A (sửa lỗi 2026-08-15, job
    Taylor_20260815_034407): hàm đó trả GIÁ ĐÓNG CỬA. Giá đóng cửa == giá tham chiếu **chỉ ở
    HOSE/HNX trong ngày thường**. TV1 — mã DUY NHẤT chạy nhánh này — niêm yết **UPCOM**, nơi
    tham chiếu là BÌNH QUÂN GIA QUYỀN giá khớp lô chẵn phiên trước. Đo 259 phiên TV1: median
    lệch 0,389%, p90 1,333%, max 7,041%, và 47 phiên lệch >1%. Nhánh mean-N (luật B) KHÔNG
    đụng tới: nó cố ý là trung bình 5 phiên GIÁ ĐÓNG, một đại lượng khác hẳn.

    FAIL-CLOSED: quote lỗi / thiếu ref / snapshot không nhất quán ⇒ `(None, info)` và caller
    rơi về band CỐ ĐỊNH (không chèn lệnh sai, không crash)."""
    try:
        q = broker.get_quote(ticker)
    except Exception as exc:                                    # noqa: BLE001
        return None, {"reason": f"DNSE không trả quote: {type(exc).__name__}: {exc}"}
    ok, info = check_reference_snapshot(q.ref, q.ceiling, q.floor,
                                        q.exchange, getattr(q, "exchange_known", False))
    info["market_id"] = getattr(q, "market_id", None)
    return (float(q.ref) if ok else None), info


def anchor_prices_for(broker, state, ticker, now=None, with_dates=False):
    """Giá đóng cửa N phiên ĐÃ HOÀN TẤT gần nhất (cũ→mới) cho luật trần động P1, hoặc None.

    ⚠️ CHỈ dùng cho nhánh **mean-N (luật B)**. Luật A phải lấy anchor từ
    `official_reference_price()` — xem lý do ở docstring hàm đó.

    `with_dates=True` → trả `(prices, dates)` với `dates` là ngày ICT của ĐÚNG các bar đó
    (ISO, cùng thứ tự). LUẬT A bắt buộc có nó để khoá bất biến "anchor là phiên ĐÃ ĐÓNG TRƯỚC
    plan_date"; không suy được ngày từ giá nên thiếu ⇒ engine fail-safe về band cố định.
    Thất bại vẫn trả `None` (một giá trị, không phải tuple) ở cả hai chế độ — caller chỉ cần
    một phép kiểm `is None`.

    CHỈ gọi khi state bật `dynamic_ceiling.enabled` — mặc định (cờ tắt) hàm này không chạy,
    không thêm một lời gọi API nào so với trước.

    Nguồn = DNSE `/price/ohlc` resolution=1D — CÙNG feed với giá live đang dùng để đặt lệnh,
    nên không có rủi ro lệch cơ sở giá (adjusted `Close` của BQ ≠ giá thị trường thật, xem
    kb/data_registry/price-volume/ticker_close_vs_price_dividend_adj.md). Đây là dữ liệu LỊCH
    SỬ (phiên đã đóng) nên không phạm luật same-day §6, nhưng dùng DNSE vẫn là lựa chọn đúng
    hơn: một feed, một cơ sở giá.

    ⚠️ DNSE TRẢ CẢ NẾN HÔM NAY (xác nhận bằng probe live 2026-08-12 18:28 ICT: TV1/DGC đều có
    bar `t`=09:00 ICT ngày 08-12). Vì vậy PHẢI lọc theo mảng `t`, không được lấy `c[-n:]` trần
    trụi — đọc giữa phiên thì `c` cuối là giá LIVE, làm trần "không đuổi giá" nhiễm đúng cái
    giá nó đang đuổi (lỗi quant-skeptic bắt được ở log verify_20260812_104435_640589).
    `now` = neo thời gian để test tất định; None → now_ict().

    None ⇒ engine tự fail-safe về trần CỐ ĐỊNH (không chèn lệnh sai, không crash).
    """
    cfg = state.get("dynamic_ceiling") or {}
    if cfg.get("enabled") is not True:
        return None
    n = int(cfg.get("sessions", DYNAMIC_CEILING_SESSIONS_DEFAULT) or DYNAMIC_CEILING_SESSIONS_DEFAULT)
    try:
        client = getattr(broker, "client", None)
        if client is None:
            print(f"  [FAILSAFE] {ticker}: broker chưa có client DNSE → không lấy được anchor")
            return None
        # Lấy dư (n+10 phiên lịch, ~2 tuần) rồi cắt n phần tử cuối: DNSE trả theo phiên GIAO
        # DỊCH nên nghỉ lễ/cuối tuần không tạo lỗ hổng, nhưng lấy dư vẫn rẻ và chống hụt.
        # §16: gắn TZ ICT tường minh trước khi .timestamp() — now_ict() trả datetime NAIVE nên
        # .timestamp() trần trụi sẽ diễn giải theo TZ của process (sai khi cron/test không có TZ).
        now_eff = now or now_ict()
        to_ts = int(now_eff.replace(tzinfo=_ICT_TZ).timestamp())
        from_ts = to_ts - (n + 20) * 86400
        raw = client.ohlc(ticker, resolution="1D", **{"from": from_ts, "to": to_ts})
    except Exception as exc:
        print(f"  [FAILSAFE] {ticker}: DNSE ohlc lỗi ({exc}) → trần động không kích hoạt")
        return None
    closes = raw.get("c") if isinstance(raw, dict) else None
    stamps = raw.get("t") if isinstance(raw, dict) else None
    # `t` BẮT BUỘC phải có và khớp độ dài `c`: không có nó thì KHÔNG biết bar nào là phiên hoàn
    # tất ⇒ không giữ được lời hứa của docstring ⇒ fail-safe (KHÔNG đoán bừa theo vị trí mảng).
    if (not isinstance(closes, list) or not isinstance(stamps, list)
            or len(stamps) != len(closes) or not closes):
        print(f"  [FAILSAFE] {ticker}: ohlc thiếu/lệch mảng t↔c "
              f"(t={len(stamps) if isinstance(stamps, list) else 'n/a'}, "
              f"c={len(closes) if isinstance(closes, list) else 'n/a'}) → trần động không kích hoạt")
        return None
    completed, comp_dates, n_dropped = [], [], 0
    for ts, v in zip(stamps, closes):
        ok = bar_is_completed_session(ts, now)
        if ok is None:
            print(f"  [FAILSAFE] {ticker}: timestamp bar không parse được ({ts!r}) → bỏ trần động")
            return None
        if ok:
            completed.append(v)
            comp_dates.append(dt.datetime.fromtimestamp(int(ts), _ICT_TZ).date().isoformat())
        else:
            n_dropped += 1
    if n_dropped:
        print(f"  [anchor] {ticker}: loại {n_dropped} bar CHƯA hoàn tất (nến hôm nay đang chạy / "
              f"bar tương lai) — anchor chỉ dùng phiên đã đóng")
    if len(completed) < n:
        print(f"  [FAILSAFE] {ticker}: ohlc còn {len(completed)} phiên ĐÃ HOÀN TẤT < {n} "
              f"→ trần động không kích hoạt")
        return None
    out = []
    for v in completed[-n:]:
        try:
            # Cùng chuẩn hoá đơn vị với Quote (một số feed DNSE trả giá đơn vị NGHÌN). Kể cả
            # nếu hàm này sai, guard sanity trong resolve_price_band vẫn bắt được (anchor lệch
            # >2× giá mới nhất ⇒ fail-safe) — hai lớp, vì lỗi đơn vị đã cắn thật một lần rồi.
            out.append(float(normalize_price_vnd(float(v))))
        except (TypeError, ValueError):
            print(f"  [FAILSAFE] {ticker}: giá ohlc không parse được ({v!r}) → bỏ trần động")
            return None
    # Cắt ngày CÙNG một lát `[-n:]` với giá — hai danh sách phải song song từng phần tử, vì
    # luật A đọc `dates[-1]` để khoá bất biến "anchor là phiên ĐÃ ĐÓNG TRƯỚC plan_date".
    return (out, comp_dates[-n:]) if with_dates else out


def load_active_nav(account, now=None):
    """active_nav mới nhất của account, hoặc None (fail-safe) → (nav_vnd|None, info).

    Nguồn = `data/execution_logs/active_nav_<account>.json` do `mike/bin/compute_active_nav.py`
    ghi. Chọn nguồn này chứ KHÔNG tự tính lại vì script đó là nơi chuẩn tắc cho cơ sở tiền
    `totalCash − totalDebt` (§25 coding_guidelines — hai bug cùng loại trong hai ngày liên tiếp
    vì mỗi consumer tự lấy field tiền), đã fail-closed sẵn (guard nổ ⇒ KHÔNG ghi file, bản cũ ở
    lại nguyên), và nó chạy NGAY TRONG chuỗi lập plan (~19:0x) — tức đúng cơ sở NAV mà phần còn
    lại của plan hôm đó đã dùng.

    Vì file ghi AD-HOC (không cron riêng), mtime tươi KHÔNG chứng minh nội dung tươi (bẫy thật
    lag_edge_health 07-12) ⇒ cổng tươi đọc `computed_at` TRONG NỘI DUNG và đòi ĐÚNG ngày hôm
    nay (ICT, §16). Dung sai chặt là cố ý (§14): injector chạy 20:30 cùng ngày với producer
    19:0x, nên trễ tới một ngày đã là dấu hiệu chuỗi lập plan hỏng — lúc đó KHÔNG đặt lệnh còn
    hơn đặt theo NAV hôm qua.
    """
    path = os.path.join(ACTIVE_NAV_DIR, f"active_nav_{account}.json")
    rel = os.path.relpath(path, WC_ROOT)
    if not os.path.exists(path):
        return None, {"source": rel, "reason": f"chưa có file {rel}"}
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as exc:
        return None, {"source": rel, "reason": f"{rel} lỗi đọc: {exc}"}
    today = (now or now_ict()).date().isoformat()
    computed_at = str(d.get("computed_at"))
    nav = d.get("active_nav")
    info = {"source": rel, "computed_at": computed_at, "expected_date": today,
            "active_nav_vnd": nav, "cash_basis": d.get("cash_basis")}
    # §12: file dữ liệu mang nhãn account thì phải KIỂM nhãn, không tin tên file. Tên file đúng
    # mà nội dung của account khác = sizing account này bằng NAV account kia (tiền lệ thật
    # 2026-07-19, cross-account contamination). Rẻ, và bắt được cả lỗi copy file thủ công.
    if d.get("account") not in (None, account):
        info["reason"] = (f"{rel} có account={d.get('account')!r} ≠ {account} — nhiễm chéo "
                          f"account, KHÔNG dùng (§12)")
        return None, info
    if computed_at != today:
        info["reason"] = (f"{rel} computed_at={computed_at} ≠ hôm nay {today} — CŨ. "
                          f"Chạy `mike/bin/compute_active_nav.py --account {account}` rồi lặp lại.")
        return None, info
    if not isinstance(nav, (int, float)) or isinstance(nav, bool) or nav <= 0:
        info["reason"] = f"{rel} active_nav={nav!r} không phải số dương"
        return None, info
    info["reason"] = f"active_nav {float(nav):,.0f}đ (computed_at {computed_at})"
    return float(nav), info


def already_injected(plan, ticker):
    """Dedup: đã có order DISCRETIONARY_SPECIAL cho ticker này trong plan chưa?
    (bắt cả tranche chèn tay lẫn lần chạy trước — chống chèn trùng bất kể id scheme.)"""
    for o in plan.get("orders", []):
        if o.get("ticker") == ticker and o.get("book") == BOOK:
            return o.get("id")
    return None


def process_account(account, plan_date, dry_run):
    profile_path = os.path.join(WC_ROOT, "secrets", "trading_bot_accounts.json")
    accounts = json.load(open(profile_path, encoding="utf-8")).get("accounts", [])
    profile = next((a for a in accounts if a.get("label") == account), None)
    if not profile:
        print(f"[ERR] không tìm thấy account {account} trong trading_bot_accounts.json")
        return 1
    account_id = profile.get("account_id")  # key CHUẨN trong secrets (KHÔNG phải account_no)

    states, skipped_states = load_active_states(account)
    if not states and not skipped_states:
        print(f"[inject] {account} {plan_date}: KHÔNG có state discretionary nào — no-op.")
        return 0
    # CÓ state nhưng không state nào active vẫn đi tiếp: mục đích là ghi được lý do vào plan
    # (xem khối discretionary_inject_notes bên dưới). Vòng lặp chạy trên `states` rỗng ⇒ không
    # lệnh nào được sinh — đúng ý, chỉ khác ở chỗ nay nó nói ra tại sao.

    plan_path = os.path.join(PLAN_DIR, f"plan_{account}_{plan_date}.json")
    if not os.path.exists(plan_path):
        print(f"[inject] {account} {plan_date}: CHƯA có plan file ({plan_path}) — "
              "DollarBill chưa ghi xong? no-op (sẽ retry lần chạy sau).")
        return 0
    plan = json.load(open(plan_path, encoding="utf-8"))
    if str(plan.get("plan_date")) != plan_date:
        print(f"[inject] {account}: plan_date trong file ({plan.get('plan_date')}) ≠ "
              f"{plan_date} — KHÔNG chèn (tránh ghi nhầm ngày).")
        return 1
    plan.setdefault("orders", [])

    now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    account_mode = "live" if account in live_dnse_labels() else "paper"

    # active_nav CHỈ đọc khi có state khai target theo tỷ trọng — state target cố định không
    # phụ thuộc NAV, không được để nó chết lây vì một file NAV cũ.
    active_nav_vnd, nav_info = None, None
    if any(s.get("target_pct_active_nav") is not None for _, s in states):
        active_nav_vnd, nav_info = load_active_nav(account)
        tag = "active_nav" if active_nav_vnd else "FAILSAFE active_nav"
        print(f"  [{tag}] {nav_info['reason']}")

    # State BỊ BỎ QUA (completed/inactive/hỏng/sai account) ⇒ ghi vào plan. Đây chính là lỗ
    # hổng đã gây ra job này: state TV1 nằm im ở status="completed" từ 07-29, injector bỏ qua
    # đúng luật và IM LẶNG, nên không artifact nào người duyệt plan đọc được nhắc rằng có một
    # chương trình gom đang không sinh lệnh. Dedup theo (state_file, why) để lần chạy lại
    # (retry khi plan chưa kịp ghi) không nhân bản ghi chú.
    if skipped_states:
        notes = plan.setdefault("discretionary_inject_notes", [])
        seen = {(n.get("state_file"), n.get("note")) for n in notes}
        for sk in skipped_states:
            if (sk["state_file"], sk["why"]) in seen:
                continue
            notes.append({"at": now_iso, "ticker": sk["ticker"], "action": "state_skipped",
                          "state_file": sk["state_file"], "note": sk["why"]})
            print(f"  [note→plan] {sk['state_file']}: {sk['why']}")
        if not dry_run:
            _atomic_write_json(plan_path, plan)

    n_injected = 0
    broker = None

    for state_path, state in states:
        ticker = state["ticker"]
        print(f"--- {ticker} ({os.path.basename(state_path)}) ---")

        # dedup 1: order đã có trong plan
        existing = already_injected(plan, ticker)
        if existing:
            print(f"  [skip] đã có order {BOOK} cho {ticker} trong plan (id={existing}) — không chèn trùng.")
            continue
        # dedup 2: ledger đã ghi plan_date này — TRỪ KHI plan đã bị GHI LẠI sau lần chèn đó
        # (re-plan 21:3x/22:1x ghi đè toàn bộ orders[]). Ledger có bản ghi mà plan KHÔNG còn
        # order tương ứng ⇒ dedup theo ledger nuốt IM LẶNG tranche của phiên. An toàn để chèn
        # lại: filled_qty luôn đọc từ broker (không từ ledger) và id order là tất định nên
        # dedup-1 ở trên vẫn chặn trùng trong cùng một plan.
        ledger = state.setdefault("ledger", [])
        if replan_dropped_injection(plan.get("orders"), ledger, plan_date, ticker, BOOK):
            print(f"  [RE-INJECT] ledger đã ghi {plan_date} nhưng plan KHÔNG còn order "
                  f"{BOOK}/{ticker} — plan bị ghi lại sau lần chèn trước. Chèn LẠI.")
        elif any(e.get("plan_date") == plan_date for e in ledger):
            print(f"  [skip] ledger đã có bản ghi cho {plan_date} — không chèn trùng.")
            continue

        baseline = int(state.get("baseline_qty_before_program", 0) or 0)
        filled, broker = broker_filled_qty(account, account_id, ticker, baseline)
        prev_turnover = prev_price = anchors = anchor_dates = None
        anchor_basis = anchor_exchange = None
        if filled is not None and broker is not None:
            prev_turnover, prev_price = prev_session_market(broker, ticker)
            # LUÔN xin kèm ngày (`with_dates=True`), kể cả khi state chưa bật luật A: ngày lấy
            # từ ĐÚNG các bar đã dùng làm giá nên không tốn thêm lời gọi API nào, và nhánh
            # mean-N bỏ qua tham số này. Xin có điều kiện thì ngày ngày lật state file sẽ ra
            # fail-safe câm (thiếu anchor_dates ⇒ engine rơi về band cố định) — đúng cái bẫy
            # "đổi cấu hình mà không có gì đổi" mà job này sinh ra để tránh.
            res = anchor_prices_for(broker, state, ticker, with_dates=True)  # None khi cờ P1 tắt
            if res is not None:
                anchors, anchor_dates = res
                # LUẬT A: thay phần tử CUỐI (giá đóng phiên gần nhất) bằng GIÁ THAM CHIẾU CHÍNH
                # THỨC của phiên kế tiếp. Giữ nguyên `anchor_dates` — ngày vẫn là phiên ĐÃ ĐÓNG
                # sinh ra tham chiếu đó, nên bất biến #4 không đổi nghĩa. Nhánh mean-N không
                # chạm tới (`ceiling_rule` trống ⇒ `anchor_basis` để None ⇒ engine dùng như cũ).
                _cfg = state.get("dynamic_ceiling") or {}
                if str(_cfg.get("ceiling_rule") or "").strip().upper() == "A":
                    ref_px, ref_info = official_reference_price(broker, ticker)
                    if ref_px is None:
                        print(f"  [FAILSAFE] {ticker}: luật A không lấy được giá tham chiếu "
                              f"chính thức ({ref_info.get('reason')}) → band cố định")
                        anchors = anchor_dates = None
                    else:
                        print(f"  [anchor] {ticker}: luật A dùng GIÁ THAM CHIẾU chính thức "
                              f"{ref_px:,.0f}đ (sàn {ref_info.get('exchange')}, "
                              f"marketId={ref_info.get('market_id')}) thay giá đóng "
                              f"{anchors[-1]:,.0f}đ — lệch {ref_px/anchors[-1]-1:+.3%}")
                        anchors = anchors[:-1] + [float(ref_px)]
                        anchor_basis = ANCHOR_BASIS_OFFICIAL_REF
                        anchor_exchange = ref_info.get("exchange")

        order, decision = compute_session_order(
            state, filled, prev_turnover, prev_price, plan_date, now_iso,
            anchor_prices=anchors, active_nav_vnd=active_nav_vnd,
            anchor_dates=anchor_dates, anchor_basis=anchor_basis,
            anchor_exchange=anchor_exchange)
        print(f"  decision: {decision['action']} — {decision['reason']}")

        # đánh dấu completed vào state nếu engine báo (rule e: không mua quá)
        if decision.get("mark_completed") and state.get("status") == "active":
            state["status"] = "completed"
            state["completed_at"] = now_iso
            state["completed_reason"] = decision["reason"]
            if not dry_run:
                _atomic_write_json(state_path, {k: v for k, v in state.items()
                                                if not k.startswith("_")})
            print(f"  → state {ticker} đánh dấu COMPLETED.")
            continue

        if order is None:
            # skip/failsafe/halted/inactive: KHÔNG ghi ledger (để lần sau còn thử lại) —
            # trừ khi bạn muốn audit; ghi 1 dòng history không-inject nhẹ để trace.
            state.setdefault("history_noninject", []).append(
                {"plan_date": plan_date, "action": decision["action"],
                 "reason": decision["reason"], "at": now_iso})
            # Từ khi injector là CHỦ SỞ HỮU DUY NHẤT của lệnh gom này (DollarBill không còn gõ
            # tay — xem kb/context_planning_mini.md), một lần fail-safe/halt im lặng = lệnh biến
            # mất khỏi plan mà không ai thấy. Ghi lý do THẲNG vào plan để nó nằm trong artifact
            # user duyệt lúc 21:00, không chỉ trong log của cron.
            if decision["action"] in ("failsafe", "halted"):
                plan.setdefault("discretionary_inject_notes", []).append(
                    {"at": now_iso, "ticker": ticker, "action": decision["action"],
                     "state_file": state.get("_state_file"), "note": decision["reason"]})
                if not dry_run:
                    _atomic_write_json(plan_path, plan)
            if not dry_run:
                _atomic_write_json(state_path, {k: v for k, v in state.items()
                                                if not k.startswith("_")})
            continue

        # ── GATE TIỀN (A2): trừ phần plan V2.4 (~19:0x) đã dự chi TRƯỚC khi chèn ─────────
        # Hai bộ sinh lệnh cùng tiêu MỘT túi tiền và không bộ nào cộng phần của bộ kia. Vì
        # injector chạy sau (nó no-op khi chưa có file plan) nên đây là bên phải nhường.
        # Sự cố thật 2026-07-24 SpaceX: V2.4 45,9M + tranche TV1 3,98M = 49,9M > cash 49,1M.
        order, gate = gate_injected_order(order, plan, broker, account_mode,
                                          int(state["lot_size"]))
        print(f"  cash-gate: {gate['action']} — {gate['reason']}")
        if order is None:
            state.setdefault("history_noninject", []).append(
                {"plan_date": plan_date, "action": "skip_cash_gate",
                 "reason": gate.get("human_note") or gate["reason"],
                 "headroom_vnd": gate.get("headroom_vnd"),
                 "committed_vnd": gate.get("committed_vnd"), "at": now_iso})
            # Ghi vào PLAN để báo cáo 21:00 hiện lý do — race tiền im lặng biến thành một
            # quyết định người đọc được (muốn ưu tiên tranche hơn V2.4 thì user re-plan).
            plan.setdefault("cash_gate_notes", []).append(
                {"at": now_iso, "ticker": ticker, "action": gate["action"],
                 "note": gate.get("human_note") or gate["reason"]})
            if not dry_run:
                _atomic_write_json(state_path, {k: v for k, v in state.items()
                                                if not k.startswith("_")})
                _atomic_write_json(plan_path, plan)
            continue
        if gate["action"] == "SHRINK":
            order["note"] = order.get("note", "") + f" [CASH-GATE] {gate['human_note']}"

        # chèn order + ghi ledger (audit — KHÔNG dùng để đếm filled)
        plan["orders"].append(order)
        ledger.append({
            "plan_date": plan_date, "injected_qty": order["qty"],
            "limit_price_vnd": order["limit_price_vnd"], "order_id": order["id"],
            "filled_before": decision.get("filled_qty"),
            "opportunistic": decision.get("opportunistic"), "at": now_iso,
            "cash_gate": {k: gate.get(k) for k in
                          ("action", "headroom_vnd", "committed_vnd", "basis")}})
        n_injected += 1
        print(f"  [INJECT] {ticker} {order['qty']}cp @ ≤{order['limit_price_vnd']:,} "
              f"(filled {decision['filled_qty']}/{decision.get('target')}, "
              f"opportunistic={decision.get('opportunistic')})")

        if not dry_run:
            _atomic_write_json(state_path, {k: v for k, v in state.items()
                                            if not k.startswith("_")})

    if n_injected and not dry_run:
        plan.setdefault("discretionary_inject_log", []).append(
            {"at": now_iso, "n_injected": n_injected, "by": "discretionary_accumulation_inject.py"})
        _atomic_write_json(plan_path, plan)
        print(f"[inject] {account} {plan_date}: ĐÃ chèn {n_injected} lệnh vào {plan_path}.")
    elif n_injected and dry_run:
        print(f"[inject] {account} {plan_date}: DRY-RUN — sẽ chèn {n_injected} lệnh (không ghi).")
    else:
        print(f"[inject] {account} {plan_date}: không chèn lệnh nào.")
    return 0


def session_guard_ok(dry_run):
    """Cổng phiên: LIVE inject chỉ được chạy khi phiên đã ĐÓNG (day_volume đã chốt).
    - Phiên đang mở (ATO/MORNING/LUNCH/AFTERNOON/ATC) + LIVE → TỪ CHỐI (return False).
    - Phiên đang mở + dry-run → CHO chạy nhưng in WARN (dry-run không ghi gì; số chỉ minh hoạ).
    - PRE/CLOSED/cuối tuần/lễ → CHO chạy.
    Đặt ở main() (điểm vào lệnh thật), KHÔNG ở process_account() — để selfcheck gọi thẳng
    process_account() bất kể giờ nào vẫn chạy được (FakeBroker, không đọc DNSE thật)."""
    phase, _ = session_phase()
    now_str = now_ict().strftime("%F %H:%M ICT")
    if phase not in _SESSION_OPEN_PHASES:
        return True
    if dry_run:
        print(f"  [WARN] {now_str} phiên {phase} ĐANG MỞ — dry-run vẫn chạy, nhưng day_volume "
              "là KL DỞ DANG → cờ opportunistic chỉ MINH HOẠ, KHÔNG dùng làm quyết định thật.")
        return True
    print(f"[GUARD] {now_str} phiên {phase} đang giao dịch (09:00–14:45 T2-T6) — injector LIVE "
          "TỪ CHỐI chạy giữa phiên: day_volume chưa chốt → opportunistic sai. Chỉ chạy SAU đóng "
          "cửa (cron 20:30 ICT) hoặc dùng --dry-run để test.")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--plan-date", default=None, help="YYYY-MM-DD; bỏ trống → next_trading_day()")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not session_guard_ok(args.dry_run):
        return 2   # phân biệt guard-block với lỗi thật (rc=1) và thành công (rc=0)
    plan_date = args.plan_date or next_trading_day_str()
    return process_account(args.account, plan_date, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
