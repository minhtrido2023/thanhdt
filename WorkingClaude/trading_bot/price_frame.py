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

NĂM CỔNG. G1/G2/G3 tái dùng NGUYÊN `no_chase_ceiling.check_reference_snapshot()` (job trước,
đã CONFIRMED) — không viết lại. G4/G5 là mới, sinh ra từ đúng hai cách hỏng job này đo được:

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

FAIL-CLOSED MỌI HƯỚNG: thiếu dữ liệu / không tra được / bất kỳ cổng nào fail ⇒ `ok=False` và
caller KHÔNG được sinh lệnh cho mã đó. Không đoán, không rơi về mặc định (đúng triết lý job
Taylor_20260815_034407).
"""
import datetime as dt
from zoneinfo import ZoneInfo

from .no_chase_ceiling import check_reference_snapshot
from .vn_market import tick_size

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

# §16 coding_guidelines: mọi mốc thời gian trong file này neo TZ TƯỜNG MINH, không bao giờ
# mượn TZ của process (cron/headless không export TZ — đã cắn thật nhiều lần trong repo này).
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")


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


# ──────────────────────────────────────────────────────── giá phiên cum cuối (I/O — DNSE ohlc)

def p_cum_from_broker(broker, ticker, exright_date):
    """Giá ĐÓNG của phiên giao dịch cuối cùng TRƯỚC `exright_date` → (giá | None, info).

    Nguồn = DNSE `/price/ohlc` 1D — CÙNG feed với `q.ref` đang được đối soát, nên hai vế của
    G5 không lệch cơ sở giá vì lý do vụn vặt. Bar được lọc **strictly < exright_date**: bar
    của chính ngày GDKHQ đã ở hệ MỚI, lấy nhầm nó là tự đối soát mình với mình.
    (Vì sao không lấy `tav2_bq.ticker.Price`: xem bẫy §1.1 ở docstring module — dòng ngày
    GDKHQ không nhất quán giữa các sự kiện; phiên cum thì hai nguồn đều đúng, chọn DNSE cho
    thống nhất feed.)
    """
    d = _date(exright_date)
    if d is None:
        return None, {"reason": f"exright_date không parse được ({exright_date!r})"}
    client = getattr(broker, "client", None)
    if client is None or not hasattr(client, "ohlc"):
        return None, {"reason": "broker không có client DNSE — không lấy được giá phiên cum"}
    try:
        # §16: neo TZ TƯỜNG MINH. Bar 1D của DNSE mang `t` = 09:00 **ICT** của ngày giao dịch;
        # đọc/ghi mốc đó bằng TZ của process (cron không export TZ, máy đặt UTC) làm lệch NGÀY
        # của bar và có thể lấy nhầm chính bar ngày GDKHQ làm "phiên cum" — tức tự đối soát
        # mình với mình, đúng thứ hàm này sinh ra để tránh.
        to_ts = int(dt.datetime.combine(d, dt.time(9, 0), tzinfo=_ICT).timestamp())
        raw = client.ohlc(ticker, resolution="1D", **{"from": to_ts - 30 * 86400, "to": to_ts})
    except Exception as exc:                                        # noqa: BLE001
        return None, {"reason": f"DNSE ohlc lỗi: {type(exc).__name__}: {exc}"}
    closes = raw.get("c") if isinstance(raw, dict) else None
    stamps = raw.get("t") if isinstance(raw, dict) else None
    if not isinstance(closes, list) or not isinstance(stamps, list) or len(closes) != len(stamps):
        return None, {"reason": "ohlc thiếu/lệch mảng t↔c — không xác định được bar nào là phiên nào"}
    best_ts, best_px = None, None
    for ts, c in zip(stamps, closes):
        try:
            bar_d = dt.datetime.fromtimestamp(int(ts), _ICT).date()
        except (TypeError, ValueError, OSError, OverflowError):
            continue
        if bar_d >= d:
            continue                    # bar ngày GDKHQ trở đi đã ở hệ MỚI — loại
        px = _pos(c)
        if px is not None and (best_ts is None or ts > best_ts):
            best_ts, best_px = ts, px
    if best_px is None:
        return None, {"reason": f"không có bar phiên nào trước {d} trong 30 ngày gần nhất"}
    return best_px, {"reason": f"phiên cum cuối {dt.datetime.fromtimestamp(best_ts, _ICT).date()}: "
                               f"{best_px:,.0f}đ (DNSE ohlc 1D)"}


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
        prev_high=None if ex_today else prev_high)
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
                "reason": f"NGÀY GDKHQ, hệ quy chiếu MỚI xác nhận bởi 5/5 cổng: {info5['reason']}"})
    return out
