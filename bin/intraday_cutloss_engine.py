#!/usr/bin/env python3
"""intraday_cutloss_engine.py — engine THUẦN (không I/O, không broker) cho cổng giá trong phiên
+ bộ máy cutloss 4 chế độ. Driver I/O: `bin/intraday_price_watch.py`.

Đặc tả = plan user ĐÃ DUYỆT `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md`
(mục "Q1", "Chiến lược cutloss đề xuất", "4 chế độ", "Bảo vệ khi giá rơi nhanh", "Quy tắc chung",
duyệt 01:12 + 01:54 ICT 06/10). Mọi ngưỡng dưới đây chép từ plan — đổi số = đổi chính sách, phải
qua user, KHÔNG tune theo replay.

PHẠM VI HIỆN TẠI = SHADOW: engine chỉ SINH "lệnh dự định" (intent) + mô phỏng khớp để tiến trạng
thái. Không có hàm nào ở đây gọi broker. Mô hình khớp (`simulate_*`) là GIẢ ĐỊNH để shadow tiến
được qua các chế độ — KHÔNG phải dự báo khớp thật; log ghi đủ snapshot để chấm lại bằng mô hình
khác sau 5 phiên.
"""

import datetime as dt
import re
import unicodedata

# ---------------------------------------------------------------- tham số (từ plan đã duyệt)
TRIG_RET = -0.05          # giá ≤ −5% so tham chiếu
TRIG_IDIO = -0.04         # ∧ idio (ret − ret VNINDEX) ≤ −4 điểm %
EPS = 1e-9

INVEST_MIN, INVEST_MIN_COMPRESSED = 20, 10     # điều tra tối đa (phút từ T0)
REPLY_MIN, REPLY_MIN_COMPRESSED = 30, 15       # hạn trả lời (phút từ lúc gửi báo cáo)
ROOM_COMPRESS = 0.03                           # room ≤ 3% trước phán quyết ⇒ chế độ rút gọn

ROOM_FAST, ROOM_URGENT = 0.03, 0.015
SPEED_FAST = -0.01                             # %/5 phút
DEPTH_BAND = 0.02                              # depth2 = KL mua trong 2% dưới giá khớp
MODE1_TRANCHES = ((0, 0.50), (10, 0.75), (20, 1.00))   # (phút từ lúc bắt đầu bán, % luỹ kế)
MODE1_DEPTH_SHARE = 0.30
MODE1_REPRICE_MIN = 2
NO_REBUY_SESSIONS = 10

EXCHANGE_BAND = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}
LOT = 100

# ---------------------------------------------------------------- MẶC ĐỊNH AN TOÀN (r2, CHỜ USER CHỐT)
# (a) Không có phán quyết của agent (hết giờ điều tra / dispatch hỏng / bị trần chặn) ≠ "CHƯA RÕ"
#     do agent kết luận ⇒ GIỮ + cảnh báo lớn, KHÔNG bán 50%. Hằng số NON_AGENT_DEFAULT ở dưới
#     (sau định nghĩa HOLD); đổi thành SELL_HALF = quay về hành vi r1.
# (d) Ngưỡng TƯƠNG ĐỐI theo biên độ sàn (~45% biên) — CHỈ GHI LOG song song để so, hành động vẫn
#     theo TRIG_RET/TRIG_IDIO. HOSE −5% đã cách sàn −7% ≤2% ⇒ mọi kích hoạt HOSE đều rút gọn.
REL_TRIG = {"HOSE": -0.03, "HNX": -0.045, "UPCOM": -0.07}
REL_IDIO = -0.03
# Cảnh báo GỘP "cả thị trường" (không dispatch từng mã): ≥ N mã cùng kích hoạt trong 1 lượt quét,
# hoặc ≥ M mã chạm sàn, hoặc thiếu VNINDEX (idio = ret — không tách được riêng/chung).
MARKET_WIDE_MIN_HITS = 3
MARKET_WIDE_MIN_FLOOR = 2
REPLY_PREFIX_SHADOW = "SHADOW"   # trong shadow lệnh trả lời PHẢI có tiền tố này (tránh nhầm lệnh thật)

# Giả định mô hình khớp shadow (KHÔNG phải tham số chính sách):
PART_RESTING = 0.30       # lệnh LO đang chờ (không ở sàn) ăn ≤30% KL khớp mới phát sinh
FLOOR_QUEUE_SHARE = 0.10  # lệnh xếp hàng ở giá sàn ăn ≤10% KL khớp tại sàn (vị trí hàng đợi không biết)
AUCTION_RESULT_WAIT_MIN = 20  # chờ KL phiên ATO/ATC tối đa (phút từ lúc đặt) rồi coi khớp 0

# Phán quyết / hành động / book
BROKEN, NOISE, UNCLEAR = "BROKEN", "NOISE", "UNCLEAR"
VERDICT_VN = {BROKEN: "GÃY", NOISE: "NHIỄU", UNCLEAR: "CHƯA RÕ"}
SELL_ALL, SELL_HALF, HOLD = "SELL_ALL", "SELL_HALF", "HOLD"
NON_AGENT_DEFAULT = HOLD          # mặc định an toàn (a) — xem khối MẶC ĐỊNH AN TOÀN ở trên
ACTION_VN = {SELL_ALL: "BÁN toàn bộ", SELL_HALF: "BÁN 50%", HOLD: "GIỮ"}
DISCRETIONARY, UNKNOWN = "DISCRETIONARY", "UNKNOWN"
V24_BOOKS = ("BAL", "LAG", "CAPIT", "CUSTOM30V")
MODE_VN = {1: "1-Bình thường", 2: "2-Nhanh", 3: "3-Khẩn", 4: "4-Kẹt sàn"}


# ---------------------------------------------------------------- cổng kích hoạt
def trigger_check(last, ref, floor, vni_last, vni_ref, ret_thr=None, idio_thr=None):
    """→ dict hoặc None (thiếu last/ref ⇒ KHÔNG phát biểu được, không phải "không kích hoạt").

    VNINDEX thiếu ⇒ idio = ret (coi VNINDEX đi ngang) và gắn cờ `vni_missing`: nghiêng về BÁO
    (shadow không đặt lệnh, báo thừa rẻ hơn bỏ sót)."""
    if not last or not ref:
        return None
    ret_thr = TRIG_RET if ret_thr is None else ret_thr
    idio_thr = TRIG_IDIO if idio_thr is None else idio_thr
    ret = last / ref - 1
    vni_ret = (vni_last / vni_ref - 1) if (vni_last and vni_ref) else None
    idio = ret - vni_ret if vni_ret is not None else ret
    at_floor = floor is not None and last <= floor + EPS
    price_hit = ret <= ret_thr + EPS and idio <= idio_thr + EPS
    reasons = []
    if at_floor:
        reasons.append("CHẠM SÀN")
    if price_hit:
        reasons.append(f"ret {ret*100:+.1f}% ∧ idio {idio*100:+.1f}%")
    return {"hit": bool(at_floor or price_hit), "ret": ret, "vni_ret": vni_ret, "idio": idio,
            "at_floor": at_floor, "reason": " + ".join(reasons), "vni_missing": vni_ret is None}


def trigger_check_rel(last, ref, floor, vni_last, vni_ref, exchange):
    """Ngưỡng tương đối theo biên độ sàn — CHỈ để ghi log so sánh (mặc định an toàn d)."""
    return trigger_check(last, ref, floor, vni_last, vni_ref,
                         ret_thr=REL_TRIG[(exchange or "HOSE").upper()], idio_thr=REL_IDIO)


def market_wide_reason(hits):
    """hits: các trigger dict ĐÃ kích hoạt trong 1 lượt quét → lý do gộp "cả thị trường" | None."""
    if not hits:
        return None
    if any(h.get("vni_missing") for h in hits):
        return "thiếu VNINDEX (idio = ret, không tách được riêng/chung)"
    if len(hits) >= MARKET_WIDE_MIN_HITS:
        return f"{len(hits)} mã cùng kích hoạt trong 1 lượt quét"
    if sum(1 for h in hits if h.get("at_floor")) >= MARKET_WIDE_MIN_FLOOR:
        return "nhiều mã cùng chạm sàn"
    return None


# ---------------------------------------------------------------- phán quyết → hành động
def default_action(verdict, book, source="agent", no_auto_sell=False):
    """Mặc định khi user im lặng (user chốt 01:00 + 01:12 ICT 06/10):
    GÃY ⇒ bán hết; CHƯA RÕ ⇒ bán 50%; NHIỄU ⇒ giữ. Discretionary sleeve CHỈ tự bán khi GÃY.
    Book không xác định (UNKNOWN) xử như discretionary — GIẢ ĐỊNH của Taylor (không tự bán khi
    mơ hồ về nguồn gốc vị thế), báo cáo gắn cờ để user thấy.
    r2 (mặc định an toàn, chờ user chốt): `no_auto_sell` (excluded_tickers / hạn chế giao dịch) ⇒
    GIỮ; phán quyết KHÔNG đến từ agent (`source` ≠ "agent") ⇒ NON_AGENT_DEFAULT (GIỮ)."""
    if no_auto_sell:
        return HOLD
    if source != "agent":
        return NON_AGENT_DEFAULT
    if verdict == BROKEN:
        return SELL_ALL
    if book in (DISCRETIONARY, UNKNOWN):
        return HOLD
    if verdict == UNCLEAR:
        return SELL_HALF
    return HOLD


def verdict_deadline(t0, compressed):
    return t0 + dt.timedelta(minutes=INVEST_MIN_COMPRESSED if compressed else INVEST_MIN)


def reply_deadline(report_at, compressed):
    return report_at + dt.timedelta(minutes=REPLY_MIN_COMPRESSED if compressed else REPLY_MIN)


def target_qty(action, qty):
    if action == SELL_ALL:
        return int(qty)
    if action == SELL_HALF:
        return int(qty) // 2
    return 0


# ---------------------------------------------------------------- đọc trả lời user
# Lệnh phải đứng RIÊNG một dòng ("BÁN PNJ", cho phép @mention phía trước và dấu câu cuối) — câu
# thường như "không bán PNJ" / "hôm qua đã bán PNJ" KHÔNG được hiểu thành lệnh bán.
_REPLY_HEAD = r"(?m)^\s*(?:<@!?\d+>\s*)*"
_REPLY_BODY = r"(GIU|BAN\s*50\s*%|BAN)\s+([A-Z0-9]{3})\s*[.!]*\s*$"
_REPLY_ACTION = {"GIU": HOLD, "BAN": SELL_ALL}


def _fold(s):
    s = (s or "").replace("Đ", "D").replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").upper()


def _reply_re(prefix):
    return re.compile(_REPLY_HEAD + (rf"{prefix}\s+" if prefix else "") + _REPLY_BODY)


def parse_reply(messages, ticker, since, until=None, prefix=None):
    """Lệnh MỚI NHẤT của user cho đúng `ticker` trong [since, until].

    messages: [{"is_bot", "content", "created_at": datetime ICT naive}] (driver đã đổi giờ).
    Bỏ tin bot, tin trước `since` (= lúc gửi báo cáo/T0), tin sau `until`. → (action, msg) | (None, None).
    `prefix` (vd "SHADOW"): bắt buộc đứng ngay trước động từ — "BÁN PNJ" trần KHÔNG được hiểu."""
    best = None
    rx = _reply_re(_fold(prefix) if prefix else None)
    for m in messages:
        if m.get("is_bot"):
            continue
        ts = m.get("created_at")
        if ts is None or ts < since or (until is not None and ts > until):
            continue
        for verb, tk in rx.findall(_fold(m.get("content"))):
            if tk != ticker.upper():
                continue
            act = SELL_HALF if verb.startswith("BAN") and "50" in verb else _REPLY_ACTION[verb.split()[0]]
            if best is None or ts >= best[1]["created_at"]:
                best = (act, m)
    return best if best else (None, None)


# ---------------------------------------------------------------- phiên theo sàn
def exchange_phase(hose_phase, now, exchange):
    """vn_market.session_phase() theo lịch HOSE ⇒ quy về sàn của mã.
    HNX: không có ATO (09:00 đã khớp liên tục); UPCOM: không ATO/ATC, khớp liên tục tới 15:00."""
    ex = (exchange or "HOSE").upper()
    if ex == "HOSE" or hose_phase in ("LUNCH",):
        return hose_phase
    if hose_phase == "ATO":
        return "MORNING"
    if ex == "UPCOM":
        if hose_phase == "ATC" or (hose_phase == "CLOSED" and now.time() < dt.time(15, 0)
                                   and now.weekday() < 5):
            return "AFTERNOON"
    return hose_phase


def api_order_type(kind, exchange):
    """Loại lệnh gửi DNSE cho 1 intent → (orderType | None, ghi chú xác minh).

    Đã XÁC MINH bằng log thật: LO (974 lệnh); ATC trên HOSE (VHC 600cp ZaloPay 2026-07-10 14:30:19,
    `orderType":"ATC"`, price null, Pending); ATC trên UPCOM bị DNSE từ chối HTTP 400 "Invalid
    ordertype for the exchange" (SCL 2026-10-01). CHƯA xác minh: ATO (0 lệnh thật), MP — wrapper
    `dnse_api.place_order` ghi HOSE nhận "LO, ATO, ATC, MTL", vnstock connector ghi "MP/MTL" ⇒
    tên tham số thật của MP chưa chắc là "MTL" hay "MP"."""
    ex = (exchange or "HOSE").upper()
    if kind == "LO":
        return "LO", "đã xác minh"
    if kind == "ATC":
        if ex == "UPCOM":
            return None, "UPCOM không có ATC (DNSE 400, SCL 2026-10-01) ⇒ rơi về LO"
        return "ATC", "đã xác minh HOSE (VHC 2026-07-10); HNX theo docstring dnse_api"
    if kind == "ATO":
        if ex != "HOSE":
            return None, f"{ex} không có ATO ⇒ rơi về LO lúc mở phiên"
        return "ATO", "CHƯA xác minh bằng lệnh thật (docstring dnse_api)"
    if kind == "MP":
        if ex == "UPCOM":
            return None, "UPCOM chỉ LO ⇒ rơi về LO tại giá mua thứ 2"
        return "MTL", "CHƯA xác minh: MP=MTL theo dnse_api docstring; vnstock ghi 'MP/MTL'"
    return None, f"loại lệnh lạ {kind}"


# ---------------------------------------------------------------- chỉ số thị trường
def room_of(last, floor, ref):
    return (last - floor) / ref if (last and floor is not None and ref) else None


def speed_of(last, px_5m_ago):
    return (last / px_5m_ago - 1) if (last and px_5m_ago) else 0.0


def depth2_of(bids, last):
    if not last:
        return 0
    lo = last * (1 - DEPTH_BAND) - EPS
    return int(sum(q for p, q in bids if p is not None and p >= lo))


def select_mode(room, speed, depth2, q, at_floor_no_bid):
    """Chế độ theo snapshot (CHƯA áp luật chỉ-leo-thang — xem escalate())."""
    if at_floor_no_bid:
        return 4
    if (room is not None and room <= ROOM_URGENT + EPS) or depth2 < q:
        return 3
    if speed <= SPEED_FAST + EPS or (room is not None and room <= ROOM_FAST + EPS):
        return 2
    return 1


def escalate(prev, new):
    """Chỉ được LEO thang trong ngày, không lùi về chế độ chậm hơn."""
    return max(prev or 0, new)


def round_lot(q):
    return int(q // LOT) * LOT


def tick_of(price, exchange):
    ex = (exchange or "HOSE").upper()
    if ex in ("HNX", "UPCOM"):
        return 100
    return 10 if price < 10_000 else (50 if price < 50_000 else 100)


def floor_price(ref, exchange):
    """Giá sàn = ref×(1−biên độ) làm tròn LÊN bước giá (không vượt biên độ)."""
    raw = ref * (1 - EXCHANGE_BAND[(exchange or "HOSE").upper()])
    t = tick_of(raw, exchange)
    n = int(raw / t)
    return n * t if abs(n * t - raw) < EPS else (n + 1) * t


# ---------------------------------------------------------------- mô hình khớp shadow
def match_book(price, qty, bids):
    """Lệnh bán LO giá `price` khớp NGAY với bên mua giá ≥ price, theo giá bên mua."""
    left, got, val = qty, 0, 0.0
    for p, q in sorted(bids, key=lambda x: -x[0]):
        if left <= 0 or p is None or p < price - EPS:
            break
        take = min(left, int(q))
        got += take
        val += take * p
        left -= take
    return got, (val / got if got else None)


def _fill_resting(o, snap):
    """Lệnh đang chờ ăn KL khớp MỚI phát sinh (dvol) — không ăn lại sổ đã thấy lúc đặt."""
    dvol = max(0, int(snap.get("dvol") or 0))
    last, floor = snap.get("last"), snap.get("floor")
    if not dvol or not last:
        return 0, None
    if floor is not None and abs(o["price"] - floor) < EPS and last <= floor + EPS:
        return min(o["qty"], int(dvol * FLOOR_QUEUE_SHARE)), floor
    if last >= o["price"] - EPS:
        # lệnh bán chờ dưới/ngang giá khớp ⇒ ăn dòng lệnh mua MỚI ở giá khớp hiện tại (≥ giá đặt)
        return min(o["qty"], int(dvol * PART_RESTING)), max(o["price"], last)
    return 0, None


# ---------------------------------------------------------------- bộ máy cutloss (1 tài khoản)
def new_execution(target, started_at):
    return {"target": int(target), "sold": 0, "value": 0.0, "mode": 0, "mode_history": [],
            "started_at": started_at.isoformat(timespec="seconds"), "open": [],
            "atc_sent": False, "ato_sent": False, "status": "EXECUTING"}


def _place(ex, kind, price, qty, now, snap, exchange, board, intents, note=""):
    api, vnote = api_order_type(kind, exchange)
    fallback = api is None
    if fallback:     # rơi về LO
        kind_eff = "LO"
        if kind == "MP":
            bids = sorted(snap.get("bids") or [], key=lambda x: -x[0])
            price = bids[1][0] if len(bids) > 1 else (bids[0][0] if bids else snap.get("floor"))
        elif kind in ("ATC", "ATO"):
            price = snap.get("floor") if ex["mode"] >= 3 else (snap.get("bid") or snap.get("floor"))
        api = "LO"
    else:
        kind_eff = kind
    it = {"kind": kind, "kind_effective": kind_eff, "api_order_type": api, "verify": vnote,
          "price": price, "qty": int(qty), "board": board, "at": now.isoformat(timespec="seconds"),
          "mode": ex["mode"], "note": note}
    intents.append(it)
    # khớp ngay phần "chủ động" (marketable) — auction: chờ tick sau (KL phiên định kỳ)
    if kind_eff in ("ATO", "ATC"):
        ex["open"].append({"kind": kind_eff, "price": price, "qty": int(qty),
                           "placed_at": now.isoformat(timespec="seconds"), "auction": True})
        return it
    if kind_eff == "MP":
        got, avg = match_book(-1e18, qty, (sorted(snap.get("bids") or [], key=lambda x: -x[0]))[:2])
    else:
        got, avg = match_book(price, qty, snap.get("bids") or [])
    it["sim_fill"] = got
    if got:
        ex["sold"] += got
        ex["value"] += got * avg
    rem = int(qty) - got
    if rem > 0 and kind_eff != "MP":       # MP dư: sàn tự chuyển LO — mô phỏng: huỷ, tick sau đặt lại
        ex["open"].append({"kind": kind_eff, "price": price, "qty": rem,
                           "placed_at": now.isoformat(timespec="seconds"), "auction": False})
    return it


def _cancel_open(ex, now, intents, keep=None):
    kept = []
    for o in ex["open"]:
        if keep is not None and keep(o):
            kept.append(o)
        else:
            intents.append({"kind": "CANCEL", "price": o["price"], "qty": o["qty"],
                            "at": now.isoformat(timespec="seconds"), "mode": ex["mode"],
                            "note": f"huỷ {o['kind']} chờ {o['qty']}cp @{o['price']}"})
    ex["open"] = kept


def step_execution(ex, snap, phase, now, exchange, sellable, bot_stop):
    """1 nhịp (≈1 phút) của bộ máy bán cho 1 tài khoản → (intents, events).

    snap: {last, ref, floor, bid, bids:[(giá, KL)…], px_5m_ago, dvol (KL khớp mới từ nhịp trước),
           auctions: {"ATO"|"ATC": (giá khớp, KL)} — kết quả phiên định kỳ của HÔM NAY nếu đã có}
    phase: phiên ĐÃ quy theo sàn (exchange_phase). sellable: KL bán được hiện có (broker) — phần
    đã "bán" trong shadow trừ ở đây (shadow không đổi số dư thật)."""
    intents, events = [], []
    if ex["status"] != "EXECUTING":
        return intents, events
    if bot_stop:
        events.append("BOT_STOP: data/BOT_STOP tồn tại ⇒ KHÔNG sinh lệnh")
        return intents, events

    # 1) khớp các lệnh đang chờ (mô hình shadow)
    still = []
    for o in ex["open"]:
        if o.get("auction"):
            if phase in ("ATO", "ATC"):
                still.append(o)
                continue
            res = (snap.get("auctions") or {}).get(o["kind"])
            if res is None:
                age = (now - dt.datetime.fromisoformat(o["placed_at"])).total_seconds() / 60.0
                if age <= AUCTION_RESULT_WAIT_MIN:
                    still.append(o)       # chưa có KL phiên định kỳ (dữ liệu trễ) ⇒ chờ
                    continue
                events.append(f"{o['kind']}: quá {AUCTION_RESULT_WAIT_MIN}' không có KL phiên định kỳ "
                              f"⇒ coi khớp 0 (mô phỏng), bán tiếp bằng khớp liên tục")
                continue
            apx, avol = res[0], int(res[1] or 0)
            at_floor = apx is not None and snap.get("floor") is not None and apx <= snap["floor"] + EPS
            got = min(o["qty"], int(avol * FLOOR_QUEUE_SHARE) if at_floor else avol)
            if got:
                ex["sold"] += got
                ex["value"] += got * (apx or o["price"] or 0)
            events.append(f"{o['kind']} kết quả: khớp mô phỏng {got}/{o['qty']} @ {apx}")
            continue                      # phần dư lệnh định kỳ hết hiệu lực
        got, px = _fill_resting(o, snap)
        if got:
            ex["sold"] += got
            ex["value"] += got * px
            o["qty"] -= got
        if o["qty"] > 0:
            still.append(o)
    ex["open"] = still

    if any(o.get("auction") for o in ex["open"]) and phase not in ("ATO", "ATC"):
        events.append("chờ kết quả phiên định kỳ trước khi đặt lệnh liên tục")
        return intents, events
    remaining = ex["target"] - ex["sold"]
    if remaining <= 0:
        _cancel_open(ex, now, intents)
        ex["status"] = "DONE"
        events.append("DONE: đã bán đủ KL mục tiêu (mô phỏng)")
        return intents, events
    sell_left = max(0, int(sellable) - ex["sold"])
    resting = sum(o["qty"] for o in ex["open"])
    q = min(remaining, sell_left)
    if remaining > sell_left:
        events.append(f"WAIT_T2: {remaining - sell_left}cp chưa bán được (T+2 chưa về) — bán khi về")
    if q <= 0:
        return intents, events

    if phase == "LUNCH":
        events.append("LUNCH: nghỉ trưa — 13:00 tiếp tục đúng chế độ đang có")
        return intents, events
    if phase in ("PRE", "CLOSED"):
        events.append("NGOÀI GIỜ: chờ phiên sau (HOSE: ATO trước 09:15; HNX/UPCOM: LO lúc mở)")
        return intents, events
    if phase == "ATO":
        if not ex["ato_sent"]:
            _cancel_open(ex, now, intents)
            even = round_lot(q)
            if even:
                _place(ex, "ATO", None, even, now, snap, exchange, "even", intents, "phần dư phiên trước")
            ex["ato_sent"] = True
        return intents, events
    if phase == "ATC":
        if not ex["atc_sent"]:
            _cancel_open(ex, now, intents)
            even = round_lot(q)
            if even:
                _place(ex, "ATC", None, even, now, snap, exchange, "even", intents, "14:30 ⇒ ATC phần dư")
            ex["atc_sent"] = True
        return intents, events

    # 2) khớp liên tục: chọn chế độ (chỉ leo thang)
    last, floor, ref = snap.get("last"), snap.get("floor"), snap.get("ref")
    if not last or floor is None or not ref:
        events.append("THIẾU GIÁ (last/sàn/TC) ⇒ không sinh lệnh nhịp này")
        return intents, events
    bids = [(p, q_) for p, q_ in (snap.get("bids") or []) if p is not None and q_]
    room = room_of(last, floor, ref)
    spd = speed_of(last, snap.get("px_5m_ago"))
    d2 = depth2_of(bids, last)
    at_floor_no_bid = floor is not None and last is not None and last <= floor + EPS and not bids
    new = select_mode(room, spd, d2, q, at_floor_no_bid)
    mode = escalate(ex["mode"], new)
    if mode != ex["mode"]:
        events.append(f"MODE {MODE_VN.get(ex['mode'], '-')} → {MODE_VN[mode]} "
                      f"(room {room*100 if room is not None else float('nan'):.2f}%, "
                      f"speed {spd*100:+.2f}%/5', depth2 {d2}, Q {q})")
        ex["mode_history"].append([now.isoformat(timespec="seconds"), mode])
        ex["mode"] = mode
    best_bid = max((p for p, _ in bids), default=None)

    if mode >= 3:
        # MỘT lệnh LO giá sàn cho toàn bộ Q; giữ lệnh sàn đang có (ưu tiên thời gian)
        _cancel_open(ex, now, intents, keep=lambda o: abs(o["price"] - floor) < EPS)
        have = sum(o["qty"] for o in ex["open"])
        add = q - have
        if add > 0:
            even, odd = round_lot(add), add - round_lot(add)
            if even:
                _place(ex, "LO", floor, even, now, snap, exchange, "even", intents,
                       "LO giá sàn — khớp theo giá bên mua, dư xếp hàng ở sàn")
            if odd:
                _place(ex, "LO", floor, odd, now, snap, exchange, "odd", intents, "lô lẻ")
        return intents, events

    if mode == 2:
        _cancel_open(ex, now, intents)              # đặt lại mỗi 1'
        top2 = sorted(bids, key=lambda x: -x[0])[:2]
        child = min(q, int(sum(x[1] for x in top2)))
        even, odd = round_lot(child), (q - round_lot(q)) if child >= q else 0
        if even:
            _place(ex, "MP", None, even, now, snap, exchange, "even", intents,
                   "MP lệnh con ≤ KL 2 mức giá mua tốt nhất")
        if odd and best_bid:
            _place(ex, "LO", best_bid, odd, now, snap, exchange, "odd", intents, "lô lẻ")
        return intents, events

    # mode 1: 3 đợt 50/25/25 trong ~20', LO tại giá mua tốt nhất, ≤30% depth2, 2' chưa khớp ⇒ đặt lại
    started = dt.datetime.fromisoformat(ex["started_at"])
    mins = (now - started).total_seconds() / 60.0
    frac = max(f for m, f in MODE1_TRANCHES if mins >= m - EPS)
    allowed = int(ex["target"] * frac + EPS) - ex["sold"]
    if ex["open"]:
        age = (now - dt.datetime.fromisoformat(ex["open"][0]["placed_at"])).total_seconds() / 60.0
        if age < MODE1_REPRICE_MIN - EPS:
            return intents, events
        _cancel_open(ex, now, intents)
        resting = 0
    child = min(allowed - resting, q, int(d2 * MODE1_DEPTH_SHARE))
    if child > 0 and best_bid:
        even = round_lot(child)
        odd = (q - round_lot(q)) if child >= q else 0
        if even:
            _place(ex, "LO", best_bid, even, now, snap, exchange, "even", intents,
                   f"đợt {frac*100:.0f}% luỹ kế")
        if odd:
            _place(ex, "LO", best_bid, odd, now, snap, exchange, "odd", intents, "lô lẻ")
    return intents, events


def avg_price(ex):
    return ex["value"] / ex["sold"] if ex.get("sold") else None
