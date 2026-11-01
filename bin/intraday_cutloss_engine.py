#!/usr/bin/env python3
"""intraday_cutloss_engine.py — engine THUẦN (không I/O, không broker) cho cổng giá trong phiên
+ lịch HỒ SƠ DD KHỦNG HOẢNG. Driver I/O: `bin/intraday_price_watch.py`.

QUYẾT ĐỊNH USER 2026-11-01 20:05 ICT (nguyên văn): "việc cutloss không tự làm. Nếu có tín hiệu bán
mạnh, chỉ cần làm due diligence dạng khủng hoảng lấy tin trong vòng 1 tuần xử lý là được. Tôi sẽ
phải quyết bán, không thì mặc định giữ".
⇒ Module này KHÔNG còn bất kỳ logic bán nào (đã gỡ: phán quyết→hành động bán, hạn chót 20/30',
4 chế độ bán, mô phỏng khớp, ATO/ATC, cấm mua lại). Mặc định MỌI trường hợp = GIỮ. Tên file giữ
nguyên để không đổi cron/import (đổi tên = việc riêng).

Ngưỡng kích hoạt GIỮ NGUYÊN theo plan đã duyệt `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md`
(−5% ∧ idio −4%; chạm sàn; gộp cả thị trường) — đổi số = đổi chính sách, phải qua user.
"""

import datetime as dt

# ---------------------------------------------------------------- tham số (từ plan đã duyệt)
TRIG_RET = -0.05          # giá ≤ −5% so tham chiếu
TRIG_IDIO = -0.04         # ∧ idio (ret − ret VNINDEX) ≤ −4 điểm %
EPS = 1e-9

EXCHANGE_BAND = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}

# Ngưỡng TƯƠNG ĐỐI theo biên độ sàn — CHỈ GHI LOG song song để so (mặc định an toàn d).
REL_TRIG = {"HOSE": -0.03, "HNX": -0.045, "UPCOM": -0.07}
REL_IDIO = -0.03
# Cảnh báo GỘP "cả thị trường" (không mở hồ sơ từng mã): ≥ N mã cùng kích hoạt, hoặc ≥ M mã chạm
# sàn, hoặc thiếu VNINDEX. (A) luỹ kế trong cửa sổ trượt; (B) chạm sàn chỉ mở ca riêng khi idio đạt
# (user duyệt 09/10/2026 18:02 ICT, job Taylor_20261009_110243).
MARKET_WIDE_MIN_HITS = 3
MARKET_WIDE_MIN_FLOOR = 2
MARKET_WIDE_WINDOW_MIN = 60
FLOOR_MW_VNI = -0.02

# Nhãn kết luận hồ sơ DD (agent đặt; user quyết bán — hệ thống KHÔNG hành động theo nhãn)
BROKEN, NOISE, UNCLEAR = "BROKEN", "NOISE", "UNCLEAR"
VERDICT_VN = {BROKEN: "GÃY", NOISE: "NHIỄU", UNCLEAR: "CHƯA RÕ"}
DISCRETIONARY, UNKNOWN = "DISCRETIONARY", "UNKNOWN"

# ---------------------------------------------------------------- lịch hồ sơ DD khủng hoảng (user 2026-11-01)
DD_WINDOW_DAYS = 7            # thu thập tin 7 ngày LỊCH (ngày 1 = ngày kích hoạt)
DD_REMIND_DAYS = (3, 6)       # nhắc user nếu hồ sơ còn mở


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
    floor_mw = at_floor and vni_ret is not None and vni_ret <= FLOOR_MW_VNI + EPS
    reasons = []
    if at_floor:
        reasons.append("CHẠM SÀN")
    if price_hit:
        reasons.append(f"ret {ret*100:+.1f}% ∧ idio {idio*100:+.1f}%")
    # (B) `individual` = được mở ca RIÊNG: idio phải đạt (chạm sàn một mình không đủ) và không phải
    # "chạm sàn trong ngày VNINDEX ≤ −2%". hit ∧ ¬individual ⇒ driver đưa vào nhánh gộp (chỉ báo).
    return {"hit": bool(at_floor or price_hit), "ret": ret, "vni_ret": vni_ret, "idio": idio,
            "at_floor": at_floor, "reason": " + ".join(reasons), "vni_missing": vni_ret is None,
            "individual": bool(price_hit and not floor_mw), "floor_mw": bool(floor_mw)}


def not_individual_reason(tr):
    """Lý do 1 kích hoạt KHÔNG được mở ca riêng (B) → chuỗi | None."""
    if tr.get("individual"):
        return None
    if tr.get("floor_mw"):
        return f"chạm sàn ∧ VNINDEX {tr['vni_ret']*100:+.1f}% ≤ {FLOOR_MW_VNI*100:.0f}%"
    return f"chạm sàn nhưng idio {tr['idio']*100:+.1f}% chưa đạt {TRIG_IDIO*100:.0f}%"


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


LUNCH_BREAK = (dt.time(11, 30), dt.time(13, 0))


def trading_minutes(a, b):
    """Phút GIAO DỊCH từ a tới b (a ≤ b, cùng ngày): trừ nghỉ trưa 11:30–13:00 — cửa sổ 60' tính theo
    phút giao dịch, để 11:15 → 13:00 → 13:15 (45 phút giao dịch) vẫn là MỘT cửa sổ."""
    ls, le = (dt.datetime.combine(a.date(), t) for t in LUNCH_BREAK)
    lunch = max(0.0, (min(b, le) - max(a, ls)).total_seconds())
    return ((b - a).total_seconds() - lunch) / 60.0


def in_window(at, now, window_min=None):
    win = MARKET_WIDE_WINDOW_MIN if window_min is None else window_min
    return at.date() == now.date() and at <= now and trading_minutes(at, now) <= win + EPS


def window_market_wide_reason(events, now, window_min=None):
    """(A) Gộp theo cửa sổ trượt: events = [{"ticker", "at": datetime, "at_floor"}] — mọi kích hoạt
    (VNINDEX đọc được) trong ngày; đếm mã PHÂN BIỆT có kích hoạt trong `window` PHÚT GIAO DỊCH tới now
    (gồm cả biên) → lý do | None."""
    win = MARKET_WIDE_WINDOW_MIN if window_min is None else window_min
    rec = [e for e in events if in_window(e["at"], now, win)]
    tks = {e["ticker"] for e in rec}
    floors = {e["ticker"] for e in rec if e.get("at_floor")}
    since = min((e["at"] for e in rec), default=now)
    if len(tks) >= MARKET_WIDE_MIN_HITS:
        return f"{len(tks)} mã kích hoạt luỹ kế trong {win}' ({since:%H:%M}–{now:%H:%M})"
    if len(floors) >= MARKET_WIDE_MIN_FLOOR:
        return f"{len(floors)} mã chạm sàn luỹ kế trong {win}' ({since:%H:%M}–{now:%H:%M})"
    return None

# ---------------------------------------------------------------- tiện ích giá (KHÔNG XOÁ: selfcheck +
# fixture replay dùng để dựng giá sàn; không còn liên quan tới bán)
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


def dd_day(t0_date, today):
    """Ngày thứ mấy của hồ sơ (ngày LỊCH, ngày kích hoạt = 1)."""
    return (today - t0_date).days + 1


def dd_due(dossier, today):
    """→ danh sách việc tới hạn hôm nay cho 1 hồ sơ (thuần, idempotent theo cờ trong `dossier`):
      "final"     — hết DD_WINDOW_DAYS (hôm nay ≥ t0 + 7 ngày) hoặc agent báo sự kiện lớn, chưa xin kết luận
      "remind:N"  — đã tới ngày N ∈ DD_REMIND_DAYS (cron chỉ chạy ngày giao dịch ⇒ bắn ở lượt ĐẦU TIÊN
                    có ngày ≥ N), chưa nhắc, hồ sơ còn mở
      "daily"     — ngày 2..7, hôm nay chưa xin cập nhật
    Hồ sơ đã kết luận (`status` = CONCLUDED) ⇒ []."""
    if dossier.get("status") != "OPEN":
        return []
    n = dd_day(dt.date.fromisoformat(dossier["t0"][:10]), today)
    out = []
    if not dossier.get("final_requested") and (n > DD_WINDOW_DAYS or dossier.get("major_event")):
        out.append("final")
    sent = dossier.get("reminders") or []
    for r in DD_REMIND_DAYS:
        if n >= r and f"remind:{r}" not in sent and n <= DD_WINDOW_DAYS:
            out.append(f"remind:{r}")
    if 2 <= n <= DD_WINDOW_DAYS and today.isoformat() not in (dossier.get("daily_requested") or []) \
            and "final" not in out and not dossier.get("final_requested"):
        out.append("daily")
    return out
