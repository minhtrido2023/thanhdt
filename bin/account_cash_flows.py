#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dòng tiền NGOẠI SINH (nạp/rút vốn) của account — nguồn sự thật cho số hạng flow trong
tỉ suất công bố (`nav_period_returns.py`) và cho cổng chặn ở `report_delivery_gate.py`.

VÌ SAO LÀ FILE THỦ CÔNG — DNSE OpenAPI KHÔNG có nguồn nạp/rút (đã quét, không phải phỏng đoán):
  - `dnse_api.py` (SDK wrapper, 2026-09-27): 20 endpoint, KHÔNG có cash-statement/transaction/
    deposit/withdraw. Chỉ có `balances()` = SỐ DƯ tại một thời điểm, không phải SỔ dòng tiền.
  - `data/execution_logs/dnse_raw_*.jsonl` (86 file): 12 loại record, toàn bộ là
    orders/positions/balances/ppse/quote/place_order/cancel_order/loan_packages/accounts.
    KHÔNG có loại nào ghi nạp/rút.
  - Các field nghe giống dòng tiền trong `balances.stock` đều KHÔNG phải: `depositInterest`
    (lãi tiền gửi), `depositFeeAmount` (phí lưu ký/lãi vay đã post), `withdrawableCash` (hạn mức
    rút KHẢ DỤNG, không phải đã rút), `derivative.pendingDepositWithdraw` (chỉ tài khoản phái
    sinh, luôn 0 với 2 TK hiện tại).
  ⇒ Số nạp/rút chỉ con người biết. File này là nơi ghi, và `report_delivery_gate` là cơ chế
  cưỡng chế không cho quên (§6: verify artifact, đừng tin field nghe hợp lý).

SCHEMA `data/account_cash_flows.json`:
    {
      "_doc": "...",
      "SpaceX": [
        {"date": "2026-10-05", "time_ict": "10:30", "amount_vnd": 200000000, "kind": "deposit",
         "evidence": "sao kê DNSE 2026-10-05 + email xác nhận chuyển khoản"}
      ],
      "ZaloPay": []
    }
  Người khai chỉ ghi NGÀY + GIỜ + SỐ TIỀN (+ bằng chứng); quy ước chốt do CODE suy ra.
  - `date` + `time_ict`: thời điểm tiền THẬT SỰ vào/ra tài khoản, giờ ICT. `time_ict` là "HH:MM"
    hoặc "HH:MM:SS", BẮT BUỘC với deposit/withdraw (không còn mặc định im lặng nào). `date` sau
    hôm nay (giờ ICT) ⇒ CashFlowError: dòng tiền chỉ ghi SAU khi đã xảy ra (bắt gõ nhầm ngày).
  - `amount_vnd`: DƯƠNG = nạp vào, ÂM = rút ra. Số VND hữu hạn, không phải nghìn/triệu.
  - `kind`: "deposit" | "withdraw" | "market_only". `market_only` (amount_vnd PHẢI = 0) là lời
    KHẲNG ĐỊNH CÓ BẰNG CHỨNG rằng bước nhảy NAV ngày đó là biến động thị trường, không phải
    nạp/rút — đó là cách duy nhất để mở cổng chặn ở `report_delivery_gate`. Gán theo NGÀY (dòng
    nav_history đầu tiên có ngày >= `date`); không cần `time_ict`, không được khai `timing`.
    Bản ghi này KHÔNG đóng được cửa sổ nào của đẳng thức tiền (`cash_identity.py`): nó không
    mang số tiền nên từng che được khoản nạp bất kỳ cùng ngày. Lời xác nhận của đẳng thức tiền
    nằm ở file riêng `data/cash_identity_acks.json` và mang phần dư đã xem.
  - `evidence`: bắt buộc, non-empty. Không có bằng chứng ⇒ không được ghi (§6).
  - `timing`: TUỲ CHỌN, "bod" | "eod". Không khai ⇒ code tự suy. Có khai mà KHÁC kết quả suy ra
    ⇒ CashFlowError nêu cả hai (không âm thầm chọn một bên).
  - File KHÔNG tồn tại = CHƯA có dòng tiền nào được ghi (hợp lệ, không phải lỗi). Nó KHÔNG có
    nghĩa "không có dòng tiền nào xảy ra" — phân biệt 2 điều đó là việc của cổng NAV-jump.

LUẬT GÁN — MỘT luật duy nhất, định nghĩa ở `assign_flow` (user/Mike chốt 2026-10-11, D1):
tiền giao dịch ở giá đơn vị quỹ CHỐT GẦN NHẤT TRƯỚC thời điểm tiền vào/ra, và tham gia tỉ suất từ
sau đó. Cơ chế: R = dòng nav_history ĐẦU TIÊN có `balance_ts` >= thời điểm dòng tiền (dòng NAV đầu
tiên đã chứa khoản tiền).
  * thời điểm dòng tiền >= giờ đóng cửa của phiên R ⇒ "eod" trên R: giao dịch ở giá chốt của R
    (`nav_R` đã chứa tiền nên trừ ra trước khi chia).
  * ngược lại (trước/trong phiên R, cuối tuần/ngày nghỉ trước đó, tối hôm trước sau giờ chụp)
    ⇒ "bod" trên R: giao dịch ở giá chốt của dòng LIỀN TRƯỚC R.
  * chưa có R (snapshot chưa chạy) ⇒ dòng tiền TREO: không vào kỳ đo nào, và phải HIỆN ở đầu ra
    của mọi consumer (`nav_period_returns.py`: `pending_flows`).
  * dòng cần xét mà `balance_ts` thiếu/không parse được ⇒ CashFlowError trích đúng giá trị đã
    đọc (§29). Cùng PHÚT với lần chụp mà `time_ict` không có giây ⇒ CashFlowError (không đoán
    trước/sau) — khai lại "HH:MM:SS".
  * dòng nav_history ĐÚNG ngày của dòng tiền chụp TRƯỚC khi tiền vào/ra mà tiền lại tới trước
    giờ đóng cửa (NAV chụp giữa/trước phiên) ⇒ CashFlowError: cơ chế trên sẽ cho giao dịch ở
    giá chốt của chính ngày đó, trái luật — phải chụp lại NAV ngày đó sau đóng cửa.
  * "bod" trên R mà dòng LIỀN TRƯỚC R (dòng cho giá) chụp TRƯỚC giờ đóng cửa của chính nó ⇒
    CashFlowError: NAV dòng đó không phải giá chốt (thiếu biến động phần còn lại của phiên), tiền
    mới sẽ hưởng/chịu oan phần đó — phải chụp lại NAV ngày của dòng đó sau đóng cửa.
  * dòng cho giá (R nếu "eod"; dòng liền trước R, hoặc mốc khởi điểm, nếu "bod") có ngày TRƯỚC
    phiên đóng cửa gần nhất tính tới thời điểm tiền vào/ra ⇒ CashFlowError nêu tên phiên đó:
    nav_history THIẾU dòng của phiên ấy nên giá chốt thiếu biến động của nó (thật: cả hai TK
    thiếu dòng 2026-08-06). Phiên = thứ Hai–Sáu không thuộc `trading_bot.vn_market.is_holiday`.
  * dòng cho giá chụp khi phiên đóng cửa gần nhất KHÁC phiên đóng cửa gần nhất tính tới thời
    điểm tiền vào/ra ⇒ CashFlowError. Bắt cả chiều "chụp quá muộn": dòng mang ngày T nhưng chụp
    sau khi phiên T+1 đã đóng cửa (chạy lại snapshot ngày cũ theo đường live) — NAV dòng đó đã
    chứa biến động phiên T+1.
  * `balance_ts` (giờ ICT, `daily_nav_snapshot.py` ghi) phải TĂNG NGHIÊM NGẶT theo ngày của dòng,
    từ dòng liền trước dòng tiền đầu tiên tới hết ⇒ không thì CashFlowError (`attach_flows_to_rows`
    kiểm; dòng sửa tay bằng số dư chụp muộn hơn dòng sau từng cho giá sai im lặng).
  Đo 2026-10-11 trên 135 dòng thật: tăng nghiêm ngặt cả 135; 1 dòng chụp SÁNG HÔM SAU (ZaloPay 07-27 →
  07-28T09:15) — luật xử lý đúng vì so với `balance_ts` thật; 3 dòng chụp TRƯỚC giờ đóng cửa
  (SpaceX 07-02 09:46, cả hai TK 08-24 04:49) — tiền vào/ra từ sau lần chụp của ba dòng đó cho tới
  lần chụp của dòng kế tiếp (trong phiên đó, tối hôm đó, sáng phiên sau) sẽ bị từ chối. Chụp lại
  NAV một ngày cũ chỉ làm được khi `dnse_raw_<ngày>.jsonl` có bản ghi balances SAU giờ đóng cửa;
  2026-08-24 KHÔNG có (mỗi TK đúng một bản ghi balances lúc 04:49/04:50) ⇒ ba dòng trên chưa có
  lối ra, đường đính chính thuộc bước 3 của chính sách. Dòng nav_history của ngày KHÔNG có phiên
  (cuối tuần/nghỉ lễ) chụp giờ nào cũng là giá chốt của phiên trước đó — không bị coi là chụp
  trước đóng cửa khi làm dòng cho giá.

Selfcheck: `python3 mike/bin/nav_flow_term_selfcheck.py`
"""
import bisect
import datetime
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wc_paths import find_wc_root  # noqa: E402

WC_ROOT = find_wc_root(__file__)
FLOWS_PATH = os.path.join(WC_ROOT, "data", "account_cash_flows.json")
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

VALID_KINDS = ("deposit", "withdraw", "market_only")
VALID_TIMING = ("bod", "eod")
# Giờ đóng cửa phiên: hết ATC của HOSE. Nguồn: `trading_bot/vn_market.py` SESSIONS — dòng
# ("CLOSED", 14:45, …); module đó không có hằng số tên riêng cho giờ đóng cửa nên khai ở đây, và
# `nav_unit_ledger_selfcheck.py` so hằng số này với SESSIONS mỗi lần chạy (lệch ⇒ đỏ).
# Không có mặc định timing nào nữa (2026-10-11): data/account_cash_flows.json có 0 bản ghi cho cả
# 2 account lúc đổi ⇒ không bản ghi nào từng dựa vào mặc định cũ, không số lịch sử nào đổi.
SESSION_CLOSE_ICT = datetime.time(14, 45)

# Ngưỡng cổng NAV-jump: |Δnav ngày| vượt ngưỡng mà KHÔNG có bản ghi dòng tiền nào cho ngày đó
# ⇒ BLOCK. Đo thật trên toàn bộ lịch sử 2 TK ngày 2026-09-27 (N=113 cặp phiên liên tiếp:
# SpaceX 58 từ 2026-07-02, ZaloPay 55 từ 2026-07-07):
#     max|Δ| = 4,148% (ZaloPay 2026-08-07) · p95 = 3,105% · median = 0,826% · mean 1,09% sd 0,93%
# Chọn 5,0%: cao hơn max quan sát 0,85pp (0 false-positive trên cả 113 quan sát lịch sử —
# `nav_flow_term_selfcheck.py` kiểm lại con số này mỗi lần chạy), và thấp hơn nhiều mức nạp/rút
# đáng kể (200tr/1B = 20%). ĐÂY LÀ CỔNG THÔ, KHÔNG PHẢI CỔNG CHÍNH XÁC: dòng tiền nhỏ hơn ~5% NAV
# (≲50tr trên 1B) KHÔNG bị nó bắt — lớp bắt chặt hơn là residual "CHƯA GIẢI THÍCH ĐƯỢC" 0,3% NAV
# của `reconcile_equity.py` (§6 pipeline bước 3). Nói thẳng giới hạn thay vì để người dùng tưởng
# cổng này phủ mọi dòng tiền.
NAV_JUMP_BLOCK_PCT = 5.0


class CashFlowError(ValueError):
    """Bản ghi dòng tiền sai schema — fail-closed, không được bỏ qua im lặng."""


class NavRow(tuple):
    """Một dòng nav_history: vẫn là cặp `(date, nav)` cho mọi consumer cũ, mang thêm
    `.is_estimate` (cờ `nav_is_estimate` của ngày nguồn) và `.balance_ts` (lúc chụp số dư)."""

    def __new__(cls, date, nav, is_estimate=False, balance_ts=None):
        self = super().__new__(cls, (date, nav))
        self.is_estimate = is_estimate
        self.balance_ts = balance_ts
        return self


def _parse_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def _parse_time_ict(raw):
    """"HH:MM" | "HH:MM:SS" → chuỗi chuẩn hoá cùng độ chính xác. Sai dạng ⇒ ValueError."""
    text = str(raw)
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.datetime.strptime(text, fmt).strftime(fmt)
        except ValueError:
            continue
    raise ValueError(f"không phải HH:MM hoặc HH:MM:SS ({raw!r})")


def flow_moment(flow):
    """`(thời điểm tiền vào/ra — datetime ICT naive, có_giây)` của một bản ghi deposit/withdraw."""
    t = flow.get("time_ict")
    if not t:
        raise CashFlowError(
            f"flow {flow['date']} {flow['amount_vnd']:+,.0f} VND ({flow['kind']}) không có "
            f"time_ict (đọc được: {t!r}) — không biết tiền vào/ra trước hay sau lần chốt nào. "
            f"Khai giờ ICT lúc tiền vào/ra (HH:MM).")
    has_seconds = len(t) > 5
    parsed = datetime.datetime.strptime(t, "%H:%M:%S" if has_seconds else "%H:%M").time()
    return datetime.datetime.combine(flow["date"], parsed), has_seconds


def require_strictly_increasing(rows):
    """nav_history phải tăng NGHIÊM NGẶT theo ngày. Hai dòng cùng ngày từng làm một dòng tiền bị
    áp HAI lần (giá 10.000 → 8.333) — từ chối thay vì chọn hộ một dòng."""
    for prev, cur in zip(rows, rows[1:]):
        if cur[0] <= prev[0]:
            raise ValueError(
                f"nav_history không tăng nghiêm ngặt theo ngày: dòng {cur[0]} (nav {cur[1]:,.0f}) "
                f"đứng sau dòng {prev[0]} (nav {prev[1]:,.0f}) — "
                + ("HAI dòng cùng ngày" if cur[0] == prev[0] else "sai thứ tự")
                + "; sửa nav_history trước khi tính giá đơn vị.")


def load_flows(account, flows_path=None, require_file=False, today=None):
    """Trả list [{date, amount_vnd, kind, evidence, timing, time_ict}, ...] tăng dần theo ngày
    rồi giờ. `timing` ở đây là giá trị NGƯỜI KHAI (thường `None`); quy ước thật do `assign_flow` suy.

    Bản ghi sai schema ⇒ raise CashFlowError (KHÔNG bỏ qua: một bản ghi hỏng nghĩa là dòng tiền
    có xảy ra mà ta không đọc đúng, đúng lớp lỗi §28 "suy từ sự vắng mặt").

    **File THIẾU — hai chế độ, phân biệt theo người gọi (siết 2026-09-28, user duyệt):**
      · `require_file=True` ⇒ **raise CashFlowError**. Dùng cho đường CÔNG BỐ SỐ (§21/§31:
        `nav_period_returns.py`). Lý do: thiếu file thì "không có dòng tiền nào" và "đã mất sổ
        dòng tiền" LÀ HAI VIỆC KHÁC NHAU mà hàm này không phân biệt được — và nếu đoán sai theo
        hướng `[]` thì một lần NẠP tiền thật bị công bố thành LÃI, tức sai theo hướng có lợi cho
        mình, hướng tệ nhất để sai.
      · `require_file=False` (mặc định, giữ nguyên hành vi cũ) ⇒ trả `[]` **nhưng IN cảnh báo ra
        stderr** thay vì im lặng. Dùng cho đường không công bố (`daily_nav_snapshot.py`, vốn còn
        cổng NAV-jump 5% riêng).
    Bản ghi RỖNG khi file CÓ (account chưa từng có dòng tiền) là `[]` hợp lệ ở CẢ HAI chế độ —
    đó là "đã đọc và xác nhận không có", khác hẳn "không đọc được".

    `today` (date): hôm nay theo giờ ICT — bản ghi có `date` SAU ngày này bị từ chối. Bỏ trống =
    đồng hồ thật neo ICT; truyền vào chỉ để selfcheck.
    """
    if today is None:
        today = datetime.datetime.now(ICT).date()
    path = flows_path or os.environ.get("ACCOUNT_CASH_FLOWS_PATH") or FLOWS_PATH
    if not os.path.exists(path):
        if require_file:
            raise CashFlowError(
                f"KHÔNG có sổ dòng tiền {path} — người gọi yêu cầu bắt buộc (require_file=True)."
                " Thiếu file thì không phân biệt được 'chưa từng nạp/rút' với 'mất sổ', và đoán"
                " theo hướng rỗng sẽ công bố một lần NẠP thành LÃI. Tạo file (có thể là"
                ' {"<account>": []} nếu thật sự chưa có dòng tiền nào) rồi chạy lại.')
        print(f"[account_cash_flows] CẢNH BÁO: không có {path} ⇒ coi như KHÔNG có dòng tiền"
              f" nào cho '{account}'. Nếu account này ĐÃ từng nạp/rút, mọi tỉ suất tính từ đây"
              f" đều SAI (nạp bị tính thành lãi).", file=sys.stderr)
        return []
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if not isinstance(cfg, dict):
        raise CashFlowError(f"{path}: gốc file phải là object {{account: [...]}}, "
                            f"được {type(cfg).__name__}")
    raw = cfg.get(account, [])
    if not isinstance(raw, list):
        raise CashFlowError(f"{path}: entry của '{account}' phải là list, được {type(raw).__name__}")
    out = []
    for i, rec in enumerate(raw):
        where = f"{path}[{account}][{i}]"
        if not isinstance(rec, dict):
            raise CashFlowError(f"{where}: phải là object")
        for key in ("date", "amount_vnd", "kind", "evidence"):
            if key not in rec:
                raise CashFlowError(f"{where}: thiếu field bắt buộc '{key}'")
        try:
            d = _parse_date(rec["date"])
        except (TypeError, ValueError) as exc:
            raise CashFlowError(f"{where}: date không phải YYYY-MM-DD ({exc})") from exc
        if d > today:
            raise CashFlowError(
                f"{where}: date {d} nằm trong TƯƠNG LAI so với hôm nay {today} (giờ ICT) — dòng "
                f"tiền chỉ được ghi SAU khi đã xảy ra. Kiểm lại ngày (gõ nhầm?).")
        kind = rec["kind"]
        if kind not in VALID_KINDS:
            raise CashFlowError(f"{where}: kind='{kind}' không thuộc {VALID_KINDS}")
        try:
            amount = float(rec["amount_vnd"])
        except (TypeError, ValueError) as exc:
            raise CashFlowError(f"{where}: amount_vnd không phải số ({rec['amount_vnd']!r})") from exc
        if not math.isfinite(amount):
            raise CashFlowError(f"{where}: amount_vnd không phải số hữu hạn ({rec['amount_vnd']!r})")
        if not str(rec["evidence"]).strip():
            raise CashFlowError(f"{where}: evidence rỗng — không có bằng chứng thì không được ghi")
        if kind == "market_only" and amount != 0:
            raise CashFlowError(f"{where}: kind='market_only' phải có amount_vnd=0, được {amount:.0f}")
        if kind == "deposit" and amount <= 0:
            raise CashFlowError(f"{where}: kind='deposit' phải có amount_vnd>0, được {amount:.0f}")
        if kind == "withdraw" and amount >= 0:
            raise CashFlowError(f"{where}: kind='withdraw' phải có amount_vnd<0 (rút = số âm), "
                                f"được {amount:.0f}")
        timing = rec.get("timing")
        if timing is not None and timing not in VALID_TIMING:
            raise CashFlowError(f"{where}: timing='{timing}' không thuộc {VALID_TIMING}")
        time_ict = rec.get("time_ict")
        if time_ict is not None:
            try:
                time_ict = _parse_time_ict(time_ict)
            except ValueError as exc:
                raise CashFlowError(f"{where}: time_ict {exc}") from exc
        if kind == "market_only":
            if timing is not None:
                raise CashFlowError(
                    f"{where}: kind='market_only' không có tiền giao dịch nên không có timing "
                    f"(được timing='{timing}') — bỏ field này.")
        elif time_ict is None:
            raise CashFlowError(
                f"{where}: {kind} {amount:+,.0f} VND thiếu time_ict — BẮT BUỘC khai giờ ICT lúc "
                f"tiền vào/ra (HH:MM). Không có giờ thì không biết tiền giao dịch ở giá chốt "
                f"nào; code không còn mặc định hộ.")
        out.append({"date": d, "amount_vnd": amount, "kind": kind,
                    "evidence": str(rec["evidence"]), "timing": timing, "time_ict": time_ict})
    out.sort(key=lambda r: (r["date"], r["time_ict"] or ""))
    return out


def _snapshot_moment(row, flow):
    """Lúc chụp số dư của một dòng nav_history (datetime ICT naive). Thiếu/hỏng ⇒ fail-closed."""
    ts = getattr(row, "balance_ts", None)
    what = f"flow {flow['date']} {flow.get('time_ict')} {flow['amount_vnd']:+,.0f} VND"
    if not ts:
        raise CashFlowError(
            f"{what}: dòng nav_history {row[0]} không có balance_ts (đọc được: {ts!r}) ⇒ không "
            f"biết NAV ngày đó chụp trước hay sau khi tiền vào/ra. Không gán hộ.")
    try:
        snap = datetime.datetime.fromisoformat(str(ts))
    except ValueError as exc:
        raise CashFlowError(
            f"{what}: balance_ts của dòng nav_history {row[0]} không đọc được (đọc được: "
            f"{ts!r}; {exc}). Không gán hộ.") from exc
    if snap.tzinfo is not None:
        snap = snap.astimezone(ICT).replace(tzinfo=None)
    return snap


def _is_session_day(d):
    """`d` có phiên giao dịch không: thứ Hai–Sáu và không phải ngày nghỉ lễ đã khai."""
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    from trading_bot.vn_market import is_holiday       # import lười: chỉ luật gán cần lịch phiên
    return d.weekday() < 5 and not is_holiday(d)


def _last_session_closed_by(at):
    """Ngày của phiên gần nhất có giờ đóng cửa <= thời điểm `at`."""
    d = at.date() if at.time() >= SESSION_CLOSE_ICT else at.date() - datetime.timedelta(days=1)
    while not _is_session_day(d):
        d -= datetime.timedelta(days=1)
    return d


def _recapture_hint(d):
    """Lối ra khi NAV dòng `d` chụp trước đóng cửa — nói đúng điều kiện làm được (L6)."""
    return (f"Chụp lại NAV ngày {d} chỉ làm được khi data/execution_logs/dnse_raw_{d}.jsonl có bản "
            f"ghi balances SAU giờ đóng cửa (daily_nav_snapshot.py --account <TK> --date {d} "
            f"--from-raw); không có (như 2026-08-24) thì CHƯA có lối ra — đường đính chính thuộc "
            f"bước 3 của chính sách.")


def assign_flow(rows, flow, baseline_date=None):
    """LUẬT GÁN (xem docstring module). Trả `(chỉ số dòng R trong rows | None, timing | None)`.
    `None` ở chỉ số = TREO (chưa có dòng NAV nào chứa khoản tiền). `baseline_date`: ngày của mốc
    đứng TRƯỚC `rows[0]` (mốc khởi điểm của sổ) — dòng cho giá khi tiền được gán bod trên
    `rows[0]`; `None` = không có mốc nào, bỏ kiểm thiếu phiên cho riêng ca đó."""
    dates = [r[0] for r in rows]
    if flow["kind"] == "market_only":
        return next((i for i, d in enumerate(dates) if d >= flow["date"]), None), None
    at, has_seconds = flow_moment(flow)
    # Dòng liền trước ngày của flow cũng phải xét: nó có thể chụp SÁNG HÔM SAU (ZaloPay 07-27).
    start = max(0, bisect.bisect_left(dates, flow["date"]) - 1)
    for i in range(start, len(rows)):
        snap = _snapshot_moment(rows[i], flow)
        if not has_seconds and snap.replace(second=0, microsecond=0) == at:
            raise CashFlowError(
                f"flow {flow['date']} time_ict={flow['time_ict']} rơi đúng PHÚT chụp số dư của "
                f"dòng nav_history {rows[i][0]} (balance_ts {rows[i].balance_ts}) — không phân "
                f"biệt được tiền vào/ra trước hay sau lần chụp. Khai time_ict tới giây (HH:MM:SS).")
        close = datetime.datetime.combine(rows[i][0], SESSION_CLOSE_ICT)
        if snap < at < close and _is_session_day(rows[i][0]):
            # Tiền tới SAU lần chụp của dòng này nhưng TRƯỚC giờ đóng cửa của nó (NAV chụp
            # giữa/trước phiên). Dòng của ngày KHÔNG có phiên thì không có giờ đóng cửa nào để
            # đứng trước: nó chụp giờ nào cũng là giá chốt phiên trước đó. Cơ chế "dòng đầu tiên chụp SAU dòng tiền" sẽ đẩy khoản này sang
            # dòng kế tiếp, tức giao dịch ở giá chốt của CHÍNH dòng này — trái luật (tiền tới
            # trong phiên phải ở giá chốt phiên TRƯỚC), và NAV dòng này có thể đã chứa cổ phiếu
            # mua bằng tiền đó mà không chứa tiền. Không đoán: chụp lại NAV ngày đó sau đóng cửa.
            raise CashFlowError(
                f"flow {flow['date']} time_ict={flow['time_ict']} tới TRONG phiên, nhưng dòng "
                f"nav_history {rows[i][0]} chụp số dư lúc {rows[i].balance_ts} — trước khi tiền "
                f"vào/ra và trước giờ đóng cửa {SESSION_CLOSE_ICT:%H:%M} ⇒ NAV ngày đó không dùng "
                f"được để chốt giá cho khoản này. " + _recapture_hint(rows[i][0]))
        if snap >= at:
            timing = "eod" if at >= close else "bod"
            declared = flow.get("timing")
            if declared is not None and declared != timing:
                raise CashFlowError(
                    f"flow {flow['date']} time_ict={flow['time_ict']} khai timing='{declared}' "
                    f"nhưng suy ra từ dữ liệu là '{timing}' trên phiên {rows[i][0]} (NAV phiên đó "
                    f"chụp lúc {rows[i].balance_ts}, giờ đóng cửa {SESSION_CLOSE_ICT:%H:%M}). "
                    f"Bỏ field timing hoặc sửa ngày/giờ cho đúng.")
            if timing == "bod" and i > 0:
                # bod trên R = giao dịch ở giá chốt của dòng LIỀN TRƯỚC. Dòng đó phải chụp SAU
                # giờ đóng cửa của chính nó thì NAV của nó mới là giá chốt; chụp trước/giữa phiên
                # (2026-08-24 04:49 cả hai TK, SpaceX 07-02 09:46) thì thiếu biến động phần còn
                # lại của phiên đó, và tiền mới sẽ hưởng/chịu oan phần biến động ấy — vĩnh viễn.
                # Dòng của ngày KHÔNG có phiên thì chụp giờ nào cũng là giá chốt phiên trước đó.
                src = rows[i - 1]
                if (_snapshot_moment(src, flow) < datetime.datetime.combine(src[0], SESSION_CLOSE_ICT)
                        and _is_session_day(src[0])):
                    raise CashFlowError(
                        f"flow {flow['date']} time_ict={flow['time_ict']} được gán bod trên phiên "
                        f"{rows[i][0]} ⇒ giao dịch ở giá chốt của dòng nav_history {src[0]}, nhưng "
                        f"dòng đó chụp số dư lúc {src.balance_ts} — TRƯỚC giờ đóng cửa "
                        f"{SESSION_CLOSE_ICT:%H:%M} của chính nó ⇒ NAV dòng {src[0]} không phải giá "
                        f"chốt (thiếu biến động phần còn lại của phiên). " + _recapture_hint(src[0]))
            # Dòng cho giá phải là phiên đóng cửa GẦN NHẤT trước thời điểm tiền vào/ra. nav_history
            # thiếu dòng của một phiên (thật: 2026-08-06 cả hai TK) thì dòng cho giá lùi về phiên
            # trước nữa ⇒ giá chốt thiếu trọn biến động của phiên thiếu, không lỗi, không cảnh báo.
            src = rows[i] if timing == "eod" else (rows[i - 1] if i > 0 else None)
            src_date = src[0] if src is not None else baseline_date
            last = _last_session_closed_by(at)
            if src_date is not None and src_date < last:
                raise CashFlowError(
                    f"flow {flow['date']} time_ict={flow['time_ict']}: phiên {last} đã đóng cửa "
                    f"trước khi tiền vào/ra nhưng dòng cho giá là {src_date} — nav_history THIẾU "
                    f"dòng của phiên {last} ⇒ giá chốt thiếu biến động của phiên đó. Backfill dòng "
                    f"đó (daily_nav_snapshot.py --account <TK> --date {last} --from-raw — cần "
                    f"dnse_raw_{last}.jsonl có balances sau giờ đóng cửa) rồi tính lại.")
            if src is not None:
                # Bất biến gộp: NAV của dòng cho giá phải là giá chốt của ĐÚNG phiên `last`, tức
                # lúc chụp nó thì phiên đóng cửa gần nhất cũng là `last`. Hai chốt trên bắt chiều
                # "chụp quá sớm"; chốt này bắt nốt chiều "chụp quá muộn": dòng mang ngày T nhưng
                # chụp SAU khi phiên T+1 đã đóng cửa (chạy lại snapshot ngày cũ theo đường live đọc
                # số dư HIỆN TẠI) ⇒ NAV dòng đó đã chứa biến động phiên T+1, không lỗi, không cảnh báo.
                seen = _last_session_closed_by(_snapshot_moment(src, flow))
                if seen != last:
                    raise CashFlowError(
                        f"flow {flow['date']} time_ict={flow['time_ict']}: giao dịch ở giá chốt phiên "
                        f"{last} (phiên đóng cửa gần nhất trước khi tiền vào/ra), nhưng dòng cho giá "
                        f"{src[0]} chụp số dư lúc {src.balance_ts} — khi đó phiên đóng cửa gần nhất "
                        f"là {seen} ⇒ NAV dòng {src[0]} không phải giá chốt phiên {last}. Không gán "
                        f"hộ; dòng nav_history {src[0]} phải được chụp lại/đính chính (bước 3 của "
                        f"chính sách).")
            return i, timing
    return None, None


def attach_flows_to_rows(rows, flows, baseline_date=None):
    """Gán mỗi bản ghi dòng tiền vào ĐÚNG MỘT mốc quan sát NAV theo `assign_flow`.

    `rows`: NavRow tăng nghiêm ngặt theo ngày. Trả dict {ngày của dòng R: [flow, ...]}; mỗi flow
    là BẢN SAO có `timing` = quy ước đã suy ("bod"/"eod"; `None` với market_only) và
    `session_date` = ngày dòng R. Flow TREO nằm ở key `None` (timing giữ như người khai).
    `baseline_date`: xem `assign_flow`.
    """
    require_strictly_increasing(rows)
    money = [f for f in flows if f["kind"] != "market_only"]
    if money:
        # Luật gán tìm "dòng ĐẦU TIÊN chụp sau dòng tiền" ⇒ chỉ đúng khi lần chụp tăng theo ngày.
        first = min(f["date"] for f in money)
        s0 = max(0, bisect.bisect_left([r[0] for r in rows], first) - 1)
        for prev, cur in zip(rows[s0:], rows[s0 + 1:]):
            if _snapshot_moment(cur, money[0]) <= _snapshot_moment(prev, money[0]):
                raise CashFlowError(
                    f"balance_ts không tăng nghiêm ngặt: dòng nav_history {cur[0]} chụp số dư lúc "
                    f"{cur.balance_ts}, không sau dòng {prev[0]} ({prev.balance_ts}) — luật gán "
                    f"dựa trên lần chụp tăng theo ngày. Không gán hộ; sửa nav_history.")
    mapped = {}
    for f in flows:
        idx, timing = assign_flow(rows, f, baseline_date)
        if idx is None:
            mapped.setdefault(None, []).append(dict(f, session_date=None))
        else:
            mapped.setdefault(rows[idx][0], []).append(
                dict(f, timing=timing, session_date=rows[idx][0]))
    return mapped


def unexplained_nav_jumps(rows, flows, threshold_pct=NAV_JUMP_BLOCK_PCT,
                          start=None, end=None):
    """Bước nhảy NAV ngày vượt `threshold_pct` mà KHÔNG có bản ghi dòng tiền nào ĐƯỢC GÁN vào
    phiên đó (theo `assign_flow` — không so ngày ghi thô: nạp thứ Bảy giải thích bước nhảy thứ Hai).

    Trả list dict {date, prev_date, nav0, nav1, change_pct}. `start`/`end` (date) giới hạn theo
    ngày ĐẾN của bước nhảy; None = không giới hạn.
    """
    have = set(attach_flows_to_rows(rows, flows))        # key None (flow treo) không trùng ngày nào
    out = []
    for (d0, n0), (d1, n1) in zip(rows, rows[1:]):
        if start is not None and d1 < start:
            continue
        if end is not None and d1 > end:
            continue
        if not n0:
            continue
        chg = (n1 / n0 - 1) * 100
        if abs(chg) > threshold_pct and d1 not in have:
            out.append({"date": d1, "prev_date": d0, "nav0": n0, "nav1": n1, "change_pct": chg})
    return out
