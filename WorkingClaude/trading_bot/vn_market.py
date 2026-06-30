# -*- coding: utf-8 -*-
"""Cơ chế thị trường VN: phiên, lô, bước giá, biên độ.

Giả định máy chạy giờ Việt Nam (ICT).
"""

import datetime as dt

LOT = 100  # lô chẵn HOSE/HNX

# Ngày nghỉ lễ cố định hàng năm (tháng, ngày).
# Ngày lễ biến động (Tết ÂL, Giỗ Tổ, bù lễ theo quyết định từng năm) → xử lý sau.
_FIXED_HOLIDAYS = frozenset([
    (1,  1),   # Tết Dương lịch
    (4, 30),   # Ngày Giải phóng
    (5,  1),   # Quốc tế Lao động
    (9,  2),   # Quốc khánh
])

# Ngày nghỉ biến động được khai báo thủ công theo từng năm.
# Thêm vào đây khi có thông báo chính thức của SSC/HoSE.
# Format: set of date objects.
_VARIABLE_HOLIDAYS: set = set()

# (tên phiên, giờ bắt đầu, giờ kết thúc, có được đặt LO liên tục không)
SESSIONS = [
    ("PRE",       dt.time(0, 0),   dt.time(9, 0),   False),
    ("ATO",       dt.time(9, 0),   dt.time(9, 15),  False),
    ("MORNING",   dt.time(9, 15),  dt.time(11, 30), True),
    ("LUNCH",     dt.time(11, 30), dt.time(13, 0),  False),
    ("AFTERNOON", dt.time(13, 0),  dt.time(14, 30), True),
    ("ATC",       dt.time(14, 30), dt.time(14, 45), False),
    ("CLOSED",    dt.time(14, 45), dt.time(23, 59, 59), False),
]


def is_holiday(d):
    """True nếu d là ngày nghỉ lễ (cố định hoặc biến động đã khai báo)."""
    return (d.month, d.day) in _FIXED_HOLIDAYS or d in _VARIABLE_HOLIDAYS


def session_phase(now=None):
    """→ (tên phiên, continuous: bool). Cuối tuần / ngày lễ → CLOSED."""
    now = now or dt.datetime.now()
    if now.weekday() >= 5 or is_holiday(now.date()):
        return "CLOSED", False
    t = now.time()
    for name, start, end, cont in SESSIONS:
        if start <= t < end:
            return name, cont
    return "CLOSED", False


def next_trading_day(d):
    """Ngày giao dịch kế tiếp (bỏ T7/CN và ngày lễ)."""
    d = d + dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d += dt.timedelta(days=1)
    return d


def tick_size(price, symbol="", exchange="HOSE"):
    """Bước giá (VND). ETF/CCQ trên HOSE = 10đ mọi mức giá."""
    ex = (exchange or "HOSE").upper()
    if ex in ("HNX", "UPCOM", "UPCoM".upper()):
        return 100
    if symbol.upper().startswith(("E1", "FUE")):  # ETF
        return 10
    if price < 10_000:
        return 10
    if price < 50_000:
        return 50
    return 100


def round_price(price, symbol="", exchange="HOSE", direction="nearest"):
    """Làm tròn giá về bước giá hợp lệ. direction: nearest|down|up."""
    t = tick_size(price, symbol, exchange)
    q = price / t
    if direction == "down":
        n = int(q)
    elif direction == "up":
        n = int(q) + (0 if q == int(q) else 1)
    else:
        n = int(q + 0.5)
    return n * t


def round_lot(qty):
    """Làm tròn XUỐNG lô chẵn."""
    return int(qty // LOT) * LOT


def normalize_price_vnd(p):
    """Chuẩn hóa giá về VND. Một số feed trả giá đơn vị nghìn (27.5 thay vì 27500)."""
    if p is None:
        return None
    p = float(p)
    if 0 < p < 500:          # giá CP VN thực tế ≥ ~1000đ
        return p * 1000
    return p
