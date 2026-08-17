# -*- coding: utf-8 -*-
"""price_frame.py — "con số này thuộc PHIÊN NÀO": một hệ quy chiếu giá duy nhất cho mỗi lệnh.

Thiết kế D1 của `mike/agents/Taylor/research/exdate_order_pipeline_20260815/README.md` §8
(job Taylor_20260815_050425, điều tra + thiết kế; job Taylor_20260815_054822 code hoá).

NGUYÊN LÝ DẪN ĐƯỜNG (README §8, rút từ §3 — đọc lại trước khi sửa file này):

    Đừng đi tìm "nguồn giá đúng" — hãy cưỡng chế "MỘT hệ quy chiếu duy nhất".

Cách hỏng thật ĐÃ ĐO ĐƯỢC không phải "dùng nguồn giá xấu", mà là **trộn hai hệ quy chiếu**:
khối lượng ở hệ MỚI × giá ở hệ CŨ (hoặc ngược lại) qua một ngày giao dịch không hưởng quyền
(GDKHQ). Cùng cơ chế đã gây sự cố NAV MBB 2026-08-11 (+5,01tr, ~0,5% NAV SpaceX) — sự cố đó
đã vá ở TẦNG NAV (`verify_account_snapshot`), tầng ĐẶT LỆNH thì chưa. File này là tầng đó.

ĐỘ LỚN NẾU CẮN (đo thật, README §4, n=22 ngày-mã GDKHQ của chính 40 mã ta đã đặt lệnh):
median |dịch giá tham chiếu| = **5,46%**, max **50,0%** (VHM 2026-08-06), 12/22 vượt 5%.
Để so sánh: toàn bộ cơ chế chống-đuổi-giá của hệ làm việc ở thang 1–4%. Sai hệ quy chiếu
KHÔNG phải nhiễu — nó nuốt trọn cơ chế bảo vệ. Tần suất ≈ 1 sự kiện mỗi 2,4 phiên.

SÁU CỔNG. G1/G2/G3 tái dùng NGUYÊN `no_chase_ceiling.check_reference_snapshot()` (job trước,
đã CONFIRMED) — không viết lại. G4/G5/G6 là mới, sinh ra từ đúng ba cách hỏng đã đo được:

  **G4 — bất biến ĐỒNG-HỆ (mới).** Mọi lô của cùng MỘT mã trong CÙNG một bản đọc `positions`
  phải có cùng `marketPrice`. Bằng chứng cơ chế (README §3, `dnse_raw_2026-08-14.jsonl`,
  BID ex 08-17, 19:10:23, một tài khoản, một mã, MỘT bản đọc):

      {"symbol":"BID","openQuantity":107,"tradeQuantity":100,"marketPrice":35800,"loanPackageId":1826}
      {"symbol":"BID","openQuantity":300,"tradeQuantity":300,"marketPrice":38850,"loanPackageId":1258}

  DNSE điều chỉnh **THEO TỪNG GÓI VAY**, không phải theo mã, và **KHÔNG NGUYÊN TỬ**. G4 là
  cổng DUY NHẤT bắt được ca này: G1/G2/G3 đều mù vì mỗi lô riêng lẻ tự nó nhất quán.
  ⚠️ `DNSEBroker.get_positions()` CỘNG GỘP các lô và giữ "marketPrice mới nhất khác None" ⇒
  nhìn từ đó thì bản đọc trên trông hoàn toàn lành. Phải đọc RAW (`positions_raw()`).

  **G5 — đối soát chéo hai đường dữ liệu ĐỘC LẬP (mới).** `q.ref` của feed DNSE phải khớp
  công thức sở giao dịch dựng lại từ bảng vendor `tav2_bq.corporate_action`:

      ref = (P_cum − Σ cổ_tức_tiền + Σ r_quyền_mua × giá_phát_hành) / (1 + Σ r_làm_tăng_CP)

  Khớp TUYỆT ĐỐI 2/2 ca kiểm chứng độc lập (README §1.2): MBB 08-11 (24.250+0,1×10.000)/1,25
  = 20.200 = đúng ảnh chụp app DNSE của user; SSI 08-17 (24.500−1.000)/1,2 = 19.583 → tick
  → 19.600 = đúng `q.ref`. Đây là ĐỐI SOÁT, **không phải nguồn** — README §D5: không bao giờ
  tự tính lại giá tham chiếu để THAY `q.ref`.

  **G6 — bản đọc thuộc ĐÚNG phiên đang xét (mới, 2026-08-18, job Taylor_20260817_171334).**
  `q.ref` là authoritative CHỈ KHI bản ghi `secdef` sinh ra nó nói về phiên ta đang gác. Đo
  thật trên chính BID 08-17: bản ghi `secdef.time = 2026-08-17 19:23:45.110` mang
  `basicPrice 35,9 / ceiling 38,4 / floor 33,4` — đó là tham chiếu phiên **08-18** (= giá đóng
  cửa 08-17), không phải 35.800đ của phiên GDKHQ 08-17. Shadow chạy 21:41 ICT đọc đúng bản ghi
  đã lật đó ⇒ G5 báo "công thức sở lệch 2 bước giá" trong khi công thức đúng tới từng đồng.
  ⚠️ Bài học chung: cổng đối soát báo SAI NGUYÊN NHÂN dẫn người sửa đi chữa phần đang đúng —
  nên "so hai con số" bao giờ cũng phải kèm "hai con số này có cùng hệ quy chiếu THỜI GIAN không".
  Bằng chứng ba đường độc lập rằng 35.800đ MỚI là tham chiếu phiên 08-17: (1) công thức sở
  38.250/1,068433 = 35.800,1 → tick → 35.800; (2) `positions.marketPrice` của cả 3 lô BID
  suốt buổi sáng 08-17 (04:44→08:13 ICT) = 35.800, chỉ đổi thành 35.900 từ 19:05 (giá ĐÓNG
  CỬA); (3) `tav2_bq.ticker.Close` 08-14 (đã điều chỉnh hồi tố) = 35.800.

⚠️ BẪY `event_status` — đã cắn thật, quant-skeptic REFUTED vòng 1 (`corp_action_daily.py:422`):
sự kiện TƯƠNG LAI mang trạng thái **`announced`**, chỉ đổi sang `executed` ở lần reload
~22:2x ICT của CHÍNH NGÀY sự kiện. Cổng phải lọc `!= "not_executed"`, **TUYỆT ĐỐI KHÔNG**
lọc `== "executed"` — lọc thế thì mỗi ngày nó trả RỖNG và im lặng, đúng lúc cần nó nhất.
`corp_action_lib.events(executed_only=True)` KHÔNG dùng được ở đây vì lý do đó; dùng
`corp_action_lib.pricing_events()`.

⚠️ BẪY `ticker.Price` ở dòng NGÀY GDKHQ (README §1.1, phát hiện mới của job này, CHƯA có
trong data_registry): `Price` của chính dòng ngày GDKHQ **không nhất quán giữa các sự kiện** —
VHM 2026-08-06 ghi 153.000 (giá phiên TRƯỚC, trễ một phiên, sai đúng hệ số quyền 2,0) trong
khi MBB 2026-08-11 ghi 20.350 (đã ở hệ mới). ⇒ `P_cum` ở đây LUÔN lấy từ phiên cum CUỐI CÙNG
(strictly trước `exright_date`), không bao giờ từ dòng ngày GDKHQ.

⚠️ NGUỒN `P_cum` = `tav2_bq.ticker.Price` (giá THÔ của phiên đóng cửa cuối cùng trước
`exright_date`), KHÔNG phải DNSE `/price/ohlc` và KHÔNG phải BQ `Close`: DNSE OHLC trả lịch sử
ĐÃ ĐIỀU CHỈNH (BID 08-14 ra 35.800đ thay vì 38.250đ) và BQ `Close` cũng điều chỉnh hồi tố; cả
hai đều là hệ quy chiếu MỚI và sẽ làm G5 dựng kỳ vọng sai rồi chặn oan hoặc thả lỏng oan từng
mã có sự kiện. Phiên cum cuối lấy bằng câu truy vấn `time < exright_date` — không dựa vào bất
kỳ con số nào của dòng ngày GDKHQ (bẫy VHM 08-06 phía trên).

FAIL-CLOSED MỌI HƯỚNG: thiếu dữ liệu / không tra được / bất kỳ cổng nào fail ⇒ `ok=False` và
caller KHÔNG được sinh lệnh cho mã đó. Không đoán, không rơi về mặc định (đúng triết lý job
Taylor_20260815_034407).
"""
import datetime as dt

from .no_chase_ceiling import EXCHANGE_BAND_PCT, check_reference_snapshot
from .vn_market import normalize_price_vnd, tick_size

# Giá phát hành của QUYỀN MUA — tham số DUY NHẤT của công thức G5 mà bảng vendor KHÔNG có
# (`value_per_share` của mọi dòng ISS đều NULL, kiểm 2026-08-15 trên 14 sự kiện thật).
# README §4 đã cảnh báo phải có nguồn hoặc fail-closed; chọn **fail-closed** + sổ tay hẹp:
#   · Khoá = (ticker, exright_date) chứ không phải ticker — cùng mã có thể phát hành nhiều đợt
#     giá khác nhau; khoá theo mã thôi là mời một con số cũ áp cho đợt mới.
#   · Số MBB dưới đây lấy từ công bố của MBB và được xác nhận NGƯỢC bằng chính kết quả:
#     (24.250 + 0,10 × 10.000)/1,25 = 20.200 = đúng giá tham chiếu app DNSE hiển thị 08-11.
#   · Thiếu khoá ⇒ G5 FAIL-CLOSED (không lặng lẽ coi giá phát hành = 0 — coi như 0 sẽ hạ giá
#     tham chiếu kỳ vọng xuống và biến một cổng đối soát thành cỗ máy báo động giả).
RIGHTS_ISSUE_PRICE = {
    ("MBB", "2026-08-11"): 10_000.0,
}

# Cửa sổ "mã đang ở gần một sự kiện" cho các consumer chỉ cần biết CÓ/KHÔNG (vd merge_park:
# lệch L1/L2 có phải cú lật hệ quy chiếu không). Đơn vị là NGÀY LỊCH, không phải phiên.
# Vì sao 4 chứ không phải 2: cú lật có thể bắt đầu từ T-1 (đo được: VHM lật T-1 trưa, BID lật
# T-1 19:10, MBB lật qua đêm — README §3.1) và **T-1 cách T tới 3 NGÀY LỊCH khi vắt qua cuối
# tuần** — đúng ca BID: artifact L1/L2 sinh tối T6 2026-08-14 cho phiên T2 2026-08-17. Cửa sổ
# 2 ngày sẽ MÙ đúng ca thật đã xảy ra. 4 ngày phủ cả khe cuối tuần dài, và nới rộng ở đây chỉ
# làm consumer NGHI NGỜ HƠN (cửa sổ chỉ là điều kiện CẦN — phải kèm lệch giá vượt ngưỡng mới
# chặn), nên sai số nghiêng về phía an toàn.
EX_WINDOW_DAYS = 4

# Phân loại phương thức phát hành → có làm TĂNG SỐ CP của cổ đông hiện hữu không. Nguồn chuẩn
# tắc là `corp_action_lib.PRICE_ADJUSTING_ISS`; ở đây chỉ tách riêng nhánh QUYỀN MUA vì nó là
# loại duy nhất có thêm dòng tiền vào (cổ đông phải TRẢ giá phát hành).
RIGHTS_METHOD = "Quyền mua CP cho Cổ đông hiện hữu"

def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v


def _pos(x):
    v = _f(x)
    return v if v is not None and v > 0 else None


def _date(x):
    try:
        return dt.date.fromisoformat(str(x)[:10])
    except (TypeError, ValueError):
        return None


def _dtime(x):
    """Chuỗi thời gian của feed → `datetime` naive (giờ ICT, feed DNSE không mang tzinfo)."""
    s = str(x or "").strip()
    if not s:
        return None
    try:
        v = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S"):
            try:
                v = dt.datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        else:
            return None
    return v.replace(tzinfo=None) if v.tzinfo is None else v.astimezone(
        dt.timezone(dt.timedelta(hours=7))).replace(tzinfo=None)


# ─────────────────────────────────────────────────── lịch sự kiện (I/O — BQ, tra 1 lần/phiên)

def pricing_events(tickers, since, until):
    """Sự kiện LÀM ĐỔI GIÁ trong `(since, until]` → list dict thô. Rỗng khi `tickers` rỗng.

    Chỉ là lớp mỏng trên `corp_action_lib.pricing_events()` (lọc `!= not_executed`) + bộ lọc
    phân loại `is_price_adjusting()`. Tách ra ở đây để price_frame có MỘT cửa vào duy nhất và
    để caller không phải nhớ hai cái bẫy (trạng thái `announced`, ESOP không điều chỉnh giá).
    """
    tickers = sorted({str(t).strip().upper() for t in (tickers or []) if str(t or "").strip()})
    if not tickers:
        return []
    # import TRỄ (BQ/CLI chỉ cần khi thật sự tra) + tự neo repo root vào sys.path:
    # `corp_action_lib` nằm ở gốc repo chứ không trong package `trading_bot`, nên caller chạy
    # từ thư mục khác (cron, script trong mike/bin) sẽ không thấy nó. Không neo ở đây thì lỗi
    # hiện ra dưới dạng "không tra được lịch" ⇒ cổng fail-open im lặng, đúng thứ phải tránh.
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    import corp_action_lib as cal
    rows = cal.pricing_events(tickers, since=str(since), until=str(until))
    return [r for r in rows if cal.is_price_adjusting(r)]


def events_by_ticker_date(events):
    """[event] → {(ticker, 'YYYY-MM-DD'): [event, ...]}.

    GỘP theo (mã, ngày) là bắt buộc chứ không phải tiện tay: sở giao dịch tính MỘT giá tham
    chiếu cho CẢ CỤM sự kiện rơi cùng ngày. Tách ra tính riêng cho sai kết quả ở đúng những ca
    khó nhất (MBB 08-11 = cổ tức CP 15% + quyền mua 10%; SSI 08-17 = tiền 1.000 + thưởng 20%).
    """
    out = {}
    for e in events or []:
        tk = str(e.get("ticker") or "").strip().upper()
        d = _date(e.get("exright_date"))
        if tk and d:
            out.setdefault((tk, d.isoformat()), []).append(e)
    return out


def events_on(events_map, ticker, session_date):
    """Cụm sự kiện của `ticker` rơi ĐÚNG `session_date` (list, có thể rỗng)."""
    d = _date(session_date)
    return list(events_map.get((str(ticker).strip().upper(), d.isoformat() if d else ""), []))


def has_event_in_window(events_map, ticker, session_date, days=EX_WINDOW_DAYS):
    """Mã có sự kiện làm-đổi-giá nào trong ±`days` ngày quanh `session_date` không → (bool, list).

    Dùng cho consumer chỉ cần phân biệt "nhiễu giá thường" với "có thể là cú lật hệ quy chiếu"
    (README §6.2 — merge_park). KHÔNG dùng thay `events_on()` ở đường sinh lệnh: ở đó phải là
    ĐÚNG NGÀY, không phải gần ngày.
    """
    d = _date(session_date)
    if d is None:
        return False, []
    tk = str(ticker).strip().upper()
    hits = []
    for k, evs in (events_map or {}).items():
        if k[0] != tk:
            continue
        kd = _date(k[1])
        if kd is not None and abs((kd - d).days) <= days:
            hits.extend(evs)
    return bool(hits), hits


# ────────────────────────────────────────────────────────── công thức sở giao dịch (hàm THUẦN)

def adjustment(events):
    """Cụm sự kiện cùng ngày → (điều chỉnh | None, info). Hàm THUẦN.

    → `{"cash": Σ cổ tức tiền/CP, "ratio": Σ tỉ lệ làm tăng số CP, "rights_value": Σ r×giá
    phát hành, "share_factor": 1 + ratio}`. `share_factor` chính là hệ số nhân SỐ LƯỢNG CP mà
    broker áp vào vị thế (VHM 08-06: 2,0 — đúng con số biến 500cp thành 1.000cp).

    Ngữ nghĩa cột (kiểm trên 14 sự kiện thật ngày 2026-08-15, không suy đoán từ tên):
      · `DIV`: `value_per_share` = tiền mặt VND/CP. `exercise_ratio` của DIV là tiền/mệnh giá
        (700/10.000 = 0,07) — **KHÔNG PHẢI** tỉ lệ CP, dùng nhầm là sai ngay.
      · `ISS`: `exercise_ratio` = tỉ lệ thập phân (0,15 = 15%). `value_per_share` LUÔN NULL,
        kể cả quyền mua ⇒ giá phát hành phải tra `RIGHTS_ISSUE_PRICE`, thiếu ⇒ fail-closed.
    """
    cash, ratio, rights_value, parts = 0.0, 0.0, 0.0, []
    for e in events or []:
        code = str(e.get("event_code") or "").strip().upper()
        if code == "DIV":
            v = _f(e.get("value_per_share"))
            if v is None or v < 0:
                return None, {"reason": f"DIV thiếu/rác value_per_share ({e.get('value_per_share')!r})"}
            cash += v
            parts.append(f"tiền {v:,.0f}đ/CP")
            continue
        if code != "ISS":
            return None, {"reason": f"event_code lạ ({code!r}) — không biết áp vào công thức nào"}
        r = _f(e.get("exercise_ratio"))
        if r is None or r <= 0:
            return None, {"reason": f"ISS thiếu/rác exercise_ratio ({e.get('exercise_ratio')!r})"}
        method = str(e.get("issue_method_name_vi") or "").strip()
        ratio += r
        if method == RIGHTS_METHOD:
            tk = str(e.get("ticker") or "").strip().upper()
            d = _date(e.get("exright_date"))
            px = _pos(RIGHTS_ISSUE_PRICE.get((tk, d.isoformat() if d else "")))
            if px is None:
                return None, {"reason": (
                    f"QUYỀN MUA {tk}@{d} tỉ lệ {r:.4f} nhưng KHÔNG biết giá phát hành — bảng "
                    f"vendor không có cột này (value_per_share NULL) và sổ tay RIGHTS_ISSUE_PRICE "
                    f"chưa khai. FAIL-CLOSED thay vì coi giá phát hành = 0")}
            rights_value += r * px
            parts.append(f"quyền mua {r:.4f} @ {px:,.0f}đ")
        else:
            parts.append(f"{method or 'ISS'} {r:.4f}")
    if not parts:
        return None, {"reason": "cụm sự kiện rỗng"}
    return ({"cash": cash, "ratio": ratio, "rights_value": rights_value,
             "share_factor": 1.0 + ratio},
            {"reason": " + ".join(parts)})


def expected_reference_price(p_cum, events, symbol="", exchange="HOSE"):
    """Giá tham chiếu KỲ VỌNG của ngày GDKHQ theo công thức sở → (giá | None, info). THUẦN.

    `p_cum` = giá của phiên cum CUỐI CÙNG (phiên giao dịch đã đóng ngay TRƯỚC `exright_date`),
    giá THÔ — không phải `Close` điều chỉnh của BQ, và không bao giờ là `Price` của chính dòng
    ngày GDKHQ (bẫy VHM 08-06, xem docstring module).

    Kết quả trả về là số CHƯA làm tròn bước giá; `info["tick"]` mang bước giá để caller đặt
    dung sai. CỐ Ý không tự làm tròn: quy ước làm tròn của sở (nearest/half-up) là thứ ta
    KHÔNG kiểm chứng độc lập được, nên biến nó thành DUNG SAI (±1 tick) thay vì thành một
    giả định im lặng nằm giữa hai con số đang được đối soát với nhau.
    """
    base = _pos(p_cum)
    if base is None:
        return None, {"reason": f"thiếu/rác giá phiên cum cuối ({p_cum!r})"}
    adj, info = adjustment(events)
    if adj is None:
        return None, info
    num = base - adj["cash"] + adj["rights_value"]
    den = 1.0 + adj["ratio"]
    if den <= 0 or num <= 0:
        return None, {"reason": f"công thức cho kết quả không hợp lệ (tử {num:,.0f}, mẫu {den})"}
    px = num / den
    return px, {"reason": (f"({base:,.0f} − {adj['cash']:,.0f} + {adj['rights_value']:,.0f}) / "
                           f"{den:.4f} = {px:,.1f}đ  [{info['reason']}]"),
                "tick": tick_size(px, symbol=symbol or "", exchange=exchange or "HOSE"),
                "share_factor": adj["share_factor"], "p_cum": base}


# ─────────────────────────────────────────────────────────────────────────── G4 (hàm THUẦN)

def check_same_frame(position_rows, ticker):
    """G4 — mọi lô của `ticker` trong CÙNG bản đọc `positions` có cùng `marketPrice` không.

    → `(ok, info)`. `position_rows` = list dict RAW của DNSE (mỗi dòng = một deal/gói vay),
    KHÔNG phải output đã gộp của `DNSEBroker.get_positions()` — bản gộp giữ đúng một
    `marketPrice` nên bằng chứng cần kiểm đã bị xoá trước khi tới đây.

    KHÔNG có lô nào ⇒ `ok=True` (mã chưa nắm giữ thì không có hai hệ để trộn — đây là ca
    THƯỜNG của một lệnh MUA mới, không phải thiếu dữ liệu). `marketPrice` rỗng/≤0 ở MỌI lô ⇒
    `ok=True` với lý do ghi rõ: feed không cấp trường này thì G4 không phát biểu được gì, và
    các cổng G1/G2/G3/G5 vẫn đứng nguyên. Có lô mang giá và lô KHÔNG mang giá ⇒ **fail-closed**
    (một nửa bản đọc câm là đúng chữ ký của một cú lật đang diễn ra).
    """
    tk = str(ticker).strip().upper()
    lots = []
    for r in position_rows or []:
        sym = str(r.get("symbol") or r.get("instrument") or r.get("code") or "").strip().upper()
        if sym != tk:
            continue
        if str(r.get("status") or "OPEN").upper() == "CLOSED":
            continue
        qty = _f(r.get("openQuantity") if r.get("openQuantity") is not None else r.get("quantity"))
        if qty is not None and qty <= 0:
            continue
        lots.append({"marketPrice": _f(r.get("marketPrice")),
                     "openQuantity": qty,
                     "loanPackageId": r.get("loanPackageId")})
    info = {"ticker": tk, "n_lots": len(lots), "lots": lots}
    if not lots:
        info["reason"] = "không có lô nào của mã này trong bản đọc — G4 không áp dụng"
        return True, info
    priced = [l for l in lots if _pos(l["marketPrice"])]
    if not priced:
        info["reason"] = ("feed không cấp marketPrice cho lô nào — G4 không phát biểu được "
                          "(các cổng khác vẫn hiệu lực)")
        return True, info
    if len(priced) != len(lots):
        info["reason"] = (f"{len(lots) - len(priced)}/{len(lots)} lô THIẾU marketPrice trong khi "
                          f"lô khác có — bản đọc không nhất quán, có thể đang giữa cú lật")
        return False, info
    distinct = sorted({round(float(l["marketPrice"]), 4) for l in priced})
    info["distinct_market_prices"] = distinct
    if len(distinct) > 1:
        lo, hi = min(distinct), max(distinct)
        info["reason"] = (
            f"TRỘN HAI HỆ QUY CHIẾU: {len(priced)} lô của {tk} trong CÙNG một bản đọc positions "
            f"mang {len(distinct)} giá khác nhau {[f'{p:,.0f}' for p in distinct]} "
            f"(lệch {hi / lo - 1:+.2%}) — DNSE điều chỉnh theo TỪNG GÓI VAY và cú lật KHÔNG "
            f"nguyên tử. Mọi phép tính cộng dồn qua các lô này đều sai.")
        return False, info
    info["reason"] = f"{len(priced)} lô cùng một giá {distinct[0]:,.0f}đ — đồng hệ quy chiếu"
    return True, info


# ─────────────────────────────────────────────────────────────────────────── G6 (hàm THUẦN)

# Giờ sở đóng cửa phiên (ATC HOSE khớp 14:45). Bản ghi `secdef` mang dấu thời gian SAU mốc này
# là bản ghi đã LẬT sang phiên kế — đo thật: BID `secdef.time = 2026-08-17 19:23:45.110` mang
# `basicPrice 35,9 / ceiling 38,4 / floor 33,4`, tức tham chiếu phiên **08-18** (= giá đóng cửa
# phiên 08-17), trong khi tham chiếu THẬT của phiên GDKHQ 08-17 là 35.800đ.
SECDEF_ROLL_CUTOFF = dt.time(15, 0)
# Trần "cũ tới mức không giải thích được": phiên kế cách bản ghi tối đa 5 NGÀY LỊCH (đủ cho khe
# cuối tuần dài + 1 ngày lễ). Xa hơn ⇒ fail-closed, không đoán.
SECDEF_MAX_AGE_DAYS = 5


def band_tol_one_tick(ref, symbol="", exchange="HOSE", floor_tol=0.01):
    """Dung sai G2 đủ nuốt việc SỞ làm tròn trần/sàn về bước giá → `band_tol` cho
    `check_reference_snapshot`. THUẦN.

    `check_reference_snapshot` mặc định `band_tol=0.01` = 1% **tương đối trên biên độ** = ±0,07pp
    với HOSE. Đo thật trên feed DNSE 2026-08-18 (8 mã): sở luôn làm tròn trần XUỐNG bước giá gần
    nhất, và với mã giá thấp một bước giá đáng nhiều hơn 0,07pp ⇒ 4/8 mã bị G2 chặn OAN dù **8/8
    đều nằm trong ĐÚNG một bước giá** so với biên lý thuyết:

        VIX 13.350 → trần 14.250 (lý thuyết 14.284,5) = +6,742%  ← đúng mã GDKHQ 2026-08-20
        HHP 14.250 → 15.200 (15.247,5) = +6,667%   MBB 19.900 → 21.250 (21.293) = +6,784%
        VGT 11.600 → 13.300 (13.340)   = +14,655%  [UPCOM]
        (qua được với dung sai cũ: BID +6,964%, RAL +6,941%, FPT +6,977%, QNS +14,912%)

    Chính docstring của `check_reference_snapshot` đã ghi dải đo được là "HOSE 6,69–7,00%" —
    rộng hơn hẳn dung sai nó tự đặt. Đây là mâu thuẫn nội bộ, không phải phát hiện mới về sở.

    CHỈ NỚI, KHÔNG BAO GIỜ SIẾT: `max(floor_tol, …)` giữ nguyên hành vi cho mã giá cao (nơi một
    bước giá < 0,07pp). Hàm này CỐ Ý không sửa mặc định của `check_reference_snapshot` — luật A
    (`no_chase_ceiling`) đang chạy LIVE với dung sai đó; đổi mặc định là đổi hành vi live, việc
    khác, cổng khác. Ở đây chỉ đường D1-D3 (chưa live, đang SHADOW_PENDING) dùng.
    """
    r = _pos(ref)
    band = EXCHANGE_BAND_PCT.get(str(exchange or "").strip().upper())
    if r is None or not band:
        return floor_tol
    tick = tick_size(r, symbol=symbol or "", exchange=exchange or "HOSE")
    if not tick or tick <= 0:
        return floor_tol
    return max(float(floor_tol), float(tick) / (r * band))


def check_snapshot_session(secdef_time, session_date):
    """G6 — bản ghi giá tham chiếu của feed đang mô tả PHIÊN NÀO → `(ok, info)`. THUẦN.

    Sinh ra từ ca THẬT 2026-08-17: shadow chạy 21:41 ICT đọc `secdef` đã lật sang phiên kế và
    G5 báo FAIL với thông điệp "công thức sở sai" — trong khi công thức đúng tới từng đồng và
    thứ sai là **giờ chạy**. Một cổng đối soát báo sai NGUYÊN NHÂN nguy hiểm gần bằng không có
    cổng: nó dẫn người sửa đi chữa phần đang đúng.

    Không đoán theo đồng hồ máy chạy — đọc dấu thời gian FEED TỰ KHAI (`secdef.time`) rồi suy
    ra phiên mà bản ghi mô tả:
      · giờ < 15:00 ⇒ bản ghi mô tả phiên CỦA CHÍNH NGÀY đó ⇒ phải trùng `session_date`;
      · giờ ≥ 15:00 ⇒ bản ghi đã lật, mô tả phiên KẾ TIẾP ⇒ `session_date` phải LỚN HƠN ngày
        của bản ghi (không cần lịch phiên: "lớn hơn" phủ đúng cả khe cuối tuần).

    THIẾU trường (`None`/rỗng) ⇒ `ok=True` với lý do ghi rõ — feed không cấp thì cổng này không
    phát biểu được gì và G1/G2/G3/G4/G5 vẫn đứng nguyên (cùng tiền lệ với `check_same_frame`
    khi thiếu `marketPrice`). CÓ trường nhưng KHÔNG parse được ⇒ **fail-closed**: một trường
    tồn tại mà ta đọc không nổi là dấu hiệu feed đã đổi định dạng, không phải chuyện im lặng bỏ qua.
    """
    d = _date(session_date)
    info = {"secdef_time": None if secdef_time is None else str(secdef_time),
            "session_date": str(session_date), "cutoff": SECDEF_ROLL_CUTOFF.isoformat()}
    if d is None:
        info["reason"] = f"session_date không parse được ({session_date!r})"
        return False, info
    if secdef_time is None or not str(secdef_time).strip():
        info["reason"] = ("feed không cấp dấu thời gian bản ghi tham chiếu — G6 không phát biểu "
                          "được (các cổng khác vẫn hiệu lực)")
        return True, info
    ts = _dtime(secdef_time)
    if ts is None:
        info["reason"] = (f"CÓ dấu thời gian nhưng KHÔNG parse được ({secdef_time!r}) — feed có "
                          f"thể đã đổi định dạng ⇒ fail-closed thay vì bỏ qua im lặng")
        return False, info
    rolled = ts.time() >= SECDEF_ROLL_CUTOFF
    frame_note = ("sau giờ đóng cửa ⇒ mô tả phiên KẾ TIẾP" if rolled else
                  "trong phiên ⇒ mô tả phiên của chính ngày đó")
    info.update({"snapshot_ts": ts.isoformat(), "rolled_past_close": rolled,
                 "age_days": (d - ts.date()).days})
    if rolled:
        ok = ts.date() < d
    else:
        ok = ts.date() == d
    if ok and (d - ts.date()).days > SECDEF_MAX_AGE_DAYS:
        info["reason"] = (f"bản ghi tham chiếu cũ {(d - ts.date()).days} ngày lịch so với phiên "
                          f"{d} (trần {SECDEF_MAX_AGE_DAYS}) — không đoán, fail-closed")
        return False, info
    if not ok:
        info["reason"] = (
            f"BẢN ĐỌC KHÔNG THUỘC PHIÊN ĐANG XÉT: bản ghi tham chiếu của feed mang dấu thời gian "
            f"{ts:%Y-%m-%d %H:%M:%S} ({frame_note}) nên nó mô tả một phiên KHÁC {d} — mọi đối "
            f"soát trên nó nói về phiên sai. Chạy lại TRONG phiên {d} (trước {SECDEF_ROLL_CUTOFF:%H:%M} "
            f"giờ VN); đây KHÔNG phải bằng chứng công thức sở sai.")
        return False, info
    info["reason"] = (f"bản ghi tham chiếu {ts:%Y-%m-%d %H:%M:%S} ({frame_note}) đúng là của "
                      f"phiên {d}")
    return True, info


# ─────────────────────────────────────────────────────────────────────────── G5 (hàm THUẦN)

def check_ref_vs_events(ref, p_cum, events, symbol="", exchange="HOSE", tol_ticks=1):
    """G5 — `q.ref` của feed DNSE có khớp công thức sở dựng từ `corporate_action` không.

    → `(ok, info)`. Dung sai = `tol_ticks` × bước giá (mặc định 1 tick, README §8-D1).

    Đây là đối soát **HAI ĐƯỜNG DỮ LIỆU ĐỘC LẬP** — feed giao dịch DNSE vs bảng vendor trên
    BigQuery. Hai đường cùng sai theo cùng một hướng là chuyện gần như không xảy ra, nên khớp
    thì kết luận mạnh hơn hẳn "tự tính lại rồi tin chính mình".
    """
    live = _pos(ref)
    if live is None:
        return False, {"reason": f"không có giá tham chiếu sống để đối soát ({ref!r})"}
    exp, info = expected_reference_price(p_cum, events, symbol=symbol, exchange=exchange)
    info = dict(info)
    info.update({"ref_live": live, "ref_expected": exp})
    if exp is None:
        info["reason"] = f"không dựng được giá tham chiếu kỳ vọng: {info.get('reason')}"
        return False, info
    tol = max(1.0, float(tol_ticks) * float(info.get("tick") or 100))
    dev = live - exp
    info.update({"tol_vnd": tol, "dev_vnd": dev, "dev_pct": dev / exp})
    if abs(dev) > tol:
        info["reason"] = (
            f"ĐỐI SOÁT CHÉO THẤT BẠI: giá tham chiếu sống {live:,.0f}đ lệch {dev:+,.0f}đ "
            f"({dev / exp:+.2%}) so với công thức sở dựng từ corporate_action "
            f"{exp:,.1f}đ (dung sai ±{tol:,.0f}đ = {tol_ticks} bước giá). {info.get('reason')}")
        return False, info
    info["reason"] = (f"khớp công thức sở trong ±{tol:,.0f}đ: sống {live:,.0f} vs kỳ vọng "
                      f"{exp:,.1f} ({info.get('reason')})")
    return True, info


# ─────────────────────────────────────────────── giá phiên cum cuối (I/O — BQ raw `Price`)

def p_cum_from_bq(ticker, exright_date, bq_query=None):
    """Giá THÔ của phiên giao dịch cuối cùng TRƯỚC `exright_date` → (giá | None, info).

    Nguồn = `tav2_bq.ticker.Price` — cột giá THÔ (cùng hệ quy chiếu với giá live DNSE), lấy
    dòng `time < exright_date` mới nhất. KHÔNG dùng `Close` (đã điều chỉnh hồi tố) và KHÔNG
    dùng DNSE OHLC (lịch sử đã điều chỉnh — BID 08-14 trả 35.800đ thay vì 38.250đ, đúng lỗi
    G5 shadow thật 2026-08-17). Không bao giờ lấy dòng của chính ngày GDKHQ (bẫy VHM 08-06
    trong docstring module). `bq_query` chỉ để selfcheck tiêm fixture offline; production mặc
    định dùng `corp_action_lib.bq`.
    """
    d = _date(exright_date)
    if d is None:
        return None, {"reason": f"exright_date không parse được ({exright_date!r})"}
    tk = str(ticker).strip().upper()
    if not tk:
        return None, {"reason": f"ticker rỗng ({ticker!r})"}
    sql = f"""
        SELECT t.Price AS px, CAST(t.time AS STRING) AS d
        FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
        WHERE t.ticker = '{tk}'
          AND t.time < DATE '{d.isoformat()}'
          AND t.Price > 0
        ORDER BY t.time DESC
        LIMIT 1
    """
    try:
        if bq_query is None:
            import os
            import sys
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root not in sys.path:
                sys.path.insert(0, root)
            import corp_action_lib as cal
            run = cal.bq
        else:
            run = bq_query
        rows = run(sql)
    except Exception as exc:                                        # noqa: BLE001
        return None, {"reason": f"BQ raw price lỗi: {type(exc).__name__}: {exc}"}
    if not isinstance(rows, list) or len(rows) != 1:
        return None, {"reason": "BQ raw price không trả đúng 1 dòng phiên cum cuối — "
                                "dữ liệu thiếu/tách rời, fail-closed"}
    row = rows[0]
    px = _pos(normalize_price_vnd(row.get("px")))
    if px is None:
        return None, {"reason": f"BQ raw price trả giá rác cho phiên cum ({row!r})"}
    row_d = _date(str(row.get("d") or "")[:10])
    if row_d is None or row_d >= d:
        return None, {"reason": f"BQ raw price trả dòng không phải phiên trước {d} ({row!r})"}
    return px, {"reason": f"phiên cum cuối {row_d.isoformat()}: {px:,.0f}đ "
                          f"(tav2_bq.ticker.Price thô, trước GDKHQ {d.isoformat()})"}


def p_cum_from_broker(broker, ticker, exright_date):
    """Giá phiên cum cuối cho G5 — production đọc BQ raw `Price`, selfcheck tiêm fixture.

    Hàm nhận `broker` để giữ chữ ký call-site cũ; selfcheck gán `broker.cum_prices` là một
    dict {ticker: giá} để chạy offline không cần mạng. Production broker KHÔNG có thuộc tính
    đó ⇒ đi qua `p_cum_from_bq()` fail-closed.
    """
    d = _date(exright_date)
    if d is None:
        return None, {"reason": f"exright_date không parse được ({exright_date!r})"}
    cum_prices = getattr(broker, "cum_prices", None)
    if isinstance(cum_prices, dict):
        tk = str(ticker).strip().upper()
        px = _pos(normalize_price_vnd(cum_prices.get(tk)))
        if px is None:
            return None, {"reason": f"fixture cum_prices thiếu/rác {tk} ({cum_prices.get(tk)!r})"}
        return px, {"reason": f"phiên cum cuối fixture: {px:,.0f}đ (tav2_bq.ticker.Price thô)"}
    return p_cum_from_bq(ticker, d)


# ────────────────────────────────────────────────────────────────────── hàm chính (D1)

def resolve_reference(broker, ticker, session_date, events_map=None, quote=None,
                      position_rows=None, p_cum=None, prev_low=None, prev_high=None,
                      tol_ticks=1):
    """"Giá tham chiếu của mã này cho phiên này thuộc hệ quy chiếu nào" → dict.

    → `{ref_price, frame_session, ex_today, share_factor, ok, reason, gate, info}`.

    Mọi dependency đều TIÊM ĐƯỢC (`events_map`/`quote`/`position_rows`/`p_cum`) để selfcheck
    dựng lại được ca thật mà không cần DNSE hay BQ; None ⇒ tự đi lấy. Đây là lý do các ca
    chứng minh ngược (bản đọc BID 19:10:23, plan_main 08-11) chạy được offline, tất định.

    THỨ TỰ CỔNG — mỗi cổng bắt một cách hỏng mà các cổng kia MÙ, nên không cổng nào bỏ được:
      G4  đồng-hệ giữa các lô (chỉ áp khi có sự kiện: ngày thường lô lệch giá là chuyện khác)
      G1  sàn xác định được          ┐ tái dùng nguyên check_reference_snapshot() của job trước
      G2  biên độ trần/sàn khớp sàn  │ (đã CONFIRMED) — KHÔNG viết lại logic đã có
      G3  ref ∈ [Low, High] phiên trước ┘ ⇒ **BỎ QUA có chủ đích khi ex_today** (xem dưới)
      G6  bản đọc thuộc đúng phiên đang xét ← chỉ áp khi ex_today; đứng TRƯỚC G5 vì G5 chỉ có
          nghĩa khi hai vế cùng nói về một phiên
      G5  đối soát chéo công thức sở ← chỉ áp khi ex_today (ngày thường không có gì để dựng)

    G3 bị bỏ khi `ex_today=True` là ĐÚNG, không phải nới lỏng: ngày GDKHQ giá tham chiếu ĐÃ
    điều chỉnh nên nằm NGOÀI biên phiên trước theo đúng thiết kế (SSI 19.600 vs biên
    [24.000; 24.900]). Docstring `check_reference_snapshot` đã lường trước và yêu cầu caller
    khai lý do — G5 chính là thứ THAY CHỖ nó: mất một bất biến, thêm một đối soát mạnh hơn.
    """
    tk = str(ticker).strip().upper()
    d = _date(session_date)
    out = {"ticker": tk, "session_date": str(session_date), "ref_price": None,
           "frame_session": None, "ex_today": None, "share_factor": None,
           "ok": False, "gate": None, "reason": "", "info": {}}
    if d is None:
        out["gate"], out["reason"] = "G0", f"session_date không parse được ({session_date!r})"
        return out

    # ── lịch sự kiện ─────────────────────────────────────────────────────────────────────
    if events_map is None:
        try:
            evs = pricing_events([tk], since=(d - dt.timedelta(days=1)).isoformat(),
                                 until=d.isoformat())
            events_map = events_by_ticker_date(evs)
        except Exception as exc:                                    # noqa: BLE001
            out["gate"] = "GX"
            out["reason"] = (f"KHÔNG tra được lịch sự kiện quyền ({type(exc).__name__}: {exc}) — "
                             f"không biết hôm nay có phải ngày GDKHQ không ⇒ fail-closed")
            return out
    today_events = events_on(events_map, tk, d)
    ex_today = bool(today_events)
    out["ex_today"] = ex_today
    out["info"]["events"] = [
        {"code": e.get("event_code"), "status": e.get("event_status"),
         "ratio": e.get("exercise_ratio"), "value_per_share": e.get("value_per_share"),
         "method": e.get("issue_method_name_vi")} for e in today_events]

    # ── G4 — đồng hệ giữa các lô (chỉ có nghĩa khi đang ở/quanh một sự kiện) ─────────────
    if ex_today:
        if position_rows is None:
            getter = getattr(broker, "positions_raw", None)
            if callable(getter):
                try:
                    position_rows = getter()
                except Exception as exc:                            # noqa: BLE001
                    out["gate"] = "G4"
                    out["reason"] = (f"KHÔNG đọc được positions RAW ({type(exc).__name__}: {exc}) "
                                     f"— không kiểm được bất biến đồng-hệ vào ngày GDKHQ")
                    return out
            else:
                position_rows = []
                out["info"]["g4_note"] = ("broker không cấp positions_raw() — G4 chạy trên tập "
                                          "rỗng (không có vị thế để trộn hệ)")
        ok4, info4 = check_same_frame(position_rows, tk)
        out["info"]["G4"] = info4
        if not ok4:
            out["gate"], out["reason"] = "G4", info4["reason"]
            return out

    # ── G1/G2/G3 — snapshot giá tham chiếu sống ──────────────────────────────────────────
    if quote is None:
        try:
            quote = broker.get_quote(tk)
        except Exception as exc:                                    # noqa: BLE001
            out["gate"] = "G0"
            out["reason"] = f"DNSE không trả quote: {type(exc).__name__}: {exc}"
            return out
    ok123, info123 = check_reference_snapshot(
        getattr(quote, "ref", None), getattr(quote, "ceiling", None),
        getattr(quote, "floor", None), getattr(quote, "exchange", None),
        getattr(quote, "exchange_known", False),
        prev_low=None if ex_today else prev_low,
        prev_high=None if ex_today else prev_high,
        band_tol=band_tol_one_tick(getattr(quote, "ref", None), symbol=tk,
                                   exchange=getattr(quote, "exchange", None) or "HOSE"))
    if ex_today:
        info123["g3_skipped"] = ("ngày GDKHQ: tham chiếu ĐÃ điều chỉnh nên nằm ngoài biên phiên "
                                 "trước là ĐÚNG — G5 thay chỗ G3")
    out["info"]["G123"] = info123
    if not ok123:
        out["gate"] = info123.get("gate") or "G1"
        out["reason"] = info123.get("reason") or "snapshot giá tham chiếu không hợp lệ"
        return out
    ref = float(quote.ref)
    exchange = str(getattr(quote, "exchange", "") or "").upper()

    if not ex_today:
        out.update({"ref_price": ref, "frame_session": d.isoformat(), "share_factor": 1.0,
                    "ok": True, "gate": None,
                    "reason": f"phiên thường (không có sự kiện quyền): {info123.get('reason')}"})
        return out

    # ── G6 — bản đọc tham chiếu có thuộc ĐÚNG phiên này không ───────────────────────────
    # Đặt TRƯỚC G5 có chủ đích: G5 chỉ có nghĩa khi hai vế cùng nói về một phiên. Chạy G5
    # trước rồi mới hỏi phiên thì thông điệp lỗi đã sai người nhận (ca thật 2026-08-17).
    ok6, info6 = check_snapshot_session(getattr(quote, "secdef_time", None), d)
    out["info"]["G6"] = info6
    if not ok6:
        out["gate"], out["reason"] = "G6", info6["reason"]
        return out

    # ── G5 — đối soát chéo với công thức sở ──────────────────────────────────────────────
    if p_cum is None:
        p_cum, info_cum = p_cum_from_broker(broker, tk, d)
        out["info"]["p_cum"] = info_cum
        if p_cum is None:
            out["gate"] = "G5"
            out["reason"] = (f"NGÀY GDKHQ nhưng không lấy được giá phiên cum cuối để đối soát "
                             f"({info_cum.get('reason')}) ⇒ fail-closed")
            return out
    ok5, info5 = check_ref_vs_events(ref, p_cum, today_events, symbol=tk, exchange=exchange,
                                     tol_ticks=tol_ticks)
    out["info"]["G5"] = info5
    if not ok5:
        out["gate"], out["reason"] = "G5", info5["reason"]
        return out

    out.update({"ref_price": ref, "frame_session": d.isoformat(),
                "share_factor": info5.get("share_factor"), "ok": True, "gate": None,
                "reason": f"NGÀY GDKHQ, hệ quy chiếu MỚI xác nhận bởi 6/6 cổng: {info5['reason']}"})
    return out
