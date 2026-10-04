#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nhận diện sự kiện doanh nghiệp LÀM TĂNG SỐ LƯỢNG từ BROKER (DNSE) — NGUỒN CHÍNH THỨC; lịch
vendor `tav2_bq.corporate_action` chỉ để XÁC NHẬN CHÉO nếu có.

BROKER LÀ NGUỒN CHÍNH (user nâng cấp 2026-10-03 23:08 ICT — "broker DNSE là nguồn chính thức,
BigQuery chỉ là nguồn để xác nhận nếu có"; bản trước "vendor có sự kiện CP ⇒ nhường vendor" bị bỏ):
  · Broker CONFIRMABLE ⇒ ghi, BẤT KỂ vendor có/không có sự kiện. `vendor_crosscheck()` chỉ đối
    chiếu: khớp ⇒ `verified_by_vendor`; LỆCH (hệ số > 1%, chân tiền > 1đ/cp, ex-date khác, sự kiện
    điều chỉnh giá vendor có mà broker không mô tả được) ⇒ hạ `UNVERIFIED` (quy ước 2026-09-24
    "lệch nguồn vendor ⇒ hạ unverified + cảnh báo Winston") — KHÔNG lấy số vendor đè số broker.
  · Vendor không có sự kiện / feed chết / lịch thiếu hay hỏng ⇒ KHÔNG chặn broker, chỉ ghi nhận
    "chưa được vendor xác nhận" (`vendor_check.status`).
  · Chỉ GIÁ đổi, KL không đổi (`price_only_*`): KHÔNG đoán. Chỉ coi là cổ tức tiền khi DNSE ghi
    giảm tổng giá vốn đúng q×c VÀ `cashDividendReceiving` của tài khoản tăng khớp; ngược lại
    (vd quyền mua: giá tham chiếu hạ, KL về sau ex-date nhiều tuần) ⇒ AMBIGUOUS, người xác nhận.
    Cổ tức tiền KHÔNG ghi registry (`corp_actions.py`: sổ chỉ chứa sự kiện đổi KL).

NGOÀI PHẠM VI (broker mù — không viết code bắt): sự kiện KHÔNG đổi giá tham chiếu và không đổi KL
của mình — phát hành riêng lẻ, ESOP, chuyển đổi trái phiếu… Số CP lưu hành (`OShares`) cho các sự
kiện này chỉ phủ bằng BCTC QUÝ (`ticker_financial`, trễ ~3 tháng, có thể bị restated) và KHÔNG có
ngày hiệu lực. Mã KHÔNG giữ: broker không thấy gì — đường lịch sử/backtest/screening giữ nguyên
BQ + close_repair.

VÌ SAO CÓ FILE NÀY
------------------
`corp_action_auto_confirm.py` đòi NGUỒN 1 = lịch vendor (`upcoming_events_held`). Feed vendor chết
từ 2026-09-26 ⇒ ca TPB 2026-10-01 (ISS 15% + DIV 500đ) không được tự xác nhận, sổ lô lệch 200 vs
230, park-trim/active_nav bị chặn tới khi user ghi tay `data/corp_actions.json`. User duyệt
2026-10-01 (memory `feedback-broker-as-corp-action-source`) và 2026-10-03 (phương án B, tự động
hoá): broker là nguồn xác định khi vendor đứng.

⚠️ `corp_actions.py` ghi "KHÔNG BAO GIỜ tự suy corp action từ việc thấy qty lệch" — một lệnh bị
bỏ sót khỏi journal, GHOST_ORDER hay chuyển khoản chứng khoán cũng làm KL lệch. Module này KHÔNG
suy từ KL lệch. Nó đòi BA đại lượng broker ghi ĐỘC LẬP nhau cùng kể một câu chuyện, và mỗi đại
lượng loại được một lớp giả mạo khác nhau:

  (1) KHỐI LƯỢNG `openQuantity` tăng, `closedQuantity` đứng yên (không bán), `tradeQuantity`
      đứng yên (CP mới chưa được bán — đúng mẫu credit quyền, 8/8 ca thật), `accumulateQuantity`
      tăng ĐÚNG bằng phần tăng KL.
  (2) TỔNG GIÁ VỐN `Σ openQuantity × costPrice` KHÔNG TĂNG. Mua (kể cả lệnh ma ngoài journal) và
      chuyển khoản vào LUÔN làm tổng giá vốn tăng ⇒ bị loại ngay ở bước lọc ứng viên. Phần giảm
      (nếu có) chia cho KL trước sự kiện = chân cổ tức tiền mặt đi kèm (TPB: đúng 500đ/cp).
  (3) GIÁ `marketPrice` đêm đó = (giá đóng cửa cum − chân tiền) / hệ số — giá tham chiếu sở công
      bố cho phiên GDKHQ. Kiểm bằng CHÍNH `exdate_frame.verify_post_event_price` (dung sai
      200đ/0,5%) mà park_holdings/compute_active_nav đang dùng — không có phép thử thứ hai.
      VÀ phải BÁC được giả thuyết "không có sự kiện": `marketPrice` KHÔNG được khớp giá cum (hệ số
      1, có hoặc không chân tiền) trong cùng dung sai (arch-review v1 B1 — sự kiện tỉ lệ nhỏ
      ×1,01 @14.400 hay CP về SAU ex-date có giá không rơi vẫn lọt khoảng giao hệ số).
  + Hệ số KL suy từ (1) và hệ số giá suy từ (3) PHẢI giao nhau; mọi tài khoản đang giữ mã PHẢI
    cùng được credit và cho cùng chân tiền, cùng giá; trạng thái sau credit PHẢI đứng yên qua
    ≥ 2 bản ghi; mọi lô (loan package) phải đổi đồng thời (DNSE điều chỉnh KHÔNG NGUYÊN TỬ theo
    gói vay — BID 2026-08-14, `price_frame.py` §G4).

EX-DATE — KHÔNG đoán. Bằng chứng dùng: (a) trạng thái KL mới được THẤY LẦN ĐẦU ở bản ghi có `ts`
≥ 15:00 ICT phiên D (ts bản ghi, KHÔNG phải `modifiedDate` — DNSE đổi modifiedDate mọi lô mỗi tối
dù KL không đổi), bản ghi trạng thái cũ thuộc D hoặc phiên liền trước (không có khoảng trống quan
sát); (b) `marketPrice` đêm đó đã ở hệ SAU sự kiện so với giá đóng cửa D ⇒ sở đã hạ giá tham chiếu
cho phiên KẾ TIẾP ⇒ ex_date = `next_trading_day(D)`. Ex-date rơi vào mùa nghỉ lễ biến động mà
`trading_bot/vn_market.py` chưa khai báo (Tết ÂL, Giỗ Tổ, bù lễ) ⇒ MƠ HỒ (lịch có thể trả ngày
nghỉ). 7/7 sự kiện thật 2026-08→10 khớp mẫu này.

Fail-closed: bất kỳ điều kiện nào hỏng ⇒ AMBIGUOUS (không ghi, caller escalate). Thiếu dữ liệu
(chưa đủ bản ghi, không có giá cum) ⇒ INSUFFICIENT (không ghi). Hàm phát hiện là PURE: nhận
chuỗi bản ghi đã đọc + giá cum, không gọi mạng, không đọc TZ host.

CLI (chỉ ĐỌC, không ghi gì):
    python3 mike/bin/corp_action_broker_detect.py --replay 2026-08-01 2026-10-02
"""
import argparse
import datetime as dt
import glob
import json
import math
import os
import sys
from zoneinfo import ZoneInfo

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MIKE_BIN)
import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.append(WC_ROOT)                      # trading_bot.vn_market — CUỐI, không shadow bin/
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
LEDGER_FILE = os.path.join(WC_ROOT, "data", "corp_action_broker_ledger.jsonl")

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

# Credit quyền + hạ giá tham chiếu chỉ được tin là "cho phiên kế tiếp" khi xảy ra SAU giờ đóng cửa.
# 8/8 ca thật: 18:45–19:00 ICT. 15:00 = hết ATC HOSE; không nới về giữa phiên.
CREDIT_WINDOW_START = dt.time(15, 0)
MIN_POST_SNAPSHOTS = 2       # trạng thái sau credit phải lặp lại ≥ 2 bản ghi (không phải 1 lần đọc)
CASH_TOL_VND = 0.05          # sai số làm tròn costPrice (4 chữ số thập phân ⇒ ≤ ~1e-4đ/cp) quy về
                             # đ/cp. 0,5 cũ là kiểm CHẾT: |x − round(x)| ≤ 0,5 với mọi x
CASH_LEG_MIN_VND = 1.0       # |chân tiền| < 1đ/cp ⇒ coi như không có chân tiền
MAX_DECIMALS = 7             # vendor ghi tỉ lệ 7 chữ số (VPB 0,2604104)

# Verdict
NOT_CANDIDATE = "NOT_CANDIDATE"   # không có hình dạng credit (không tăng KL, hoặc tổng giá vốn TĂNG)
CONFIRMABLE = "CONFIRMABLE"
AMBIGUOUS = "AMBIGUOUS"
INSUFFICIENT = "INSUFFICIENT"
DEFER_VENDOR = "DEFER_VENDOR"     # CŨ (trước broker-primary 2026-10-03) — chỉ còn để đọc dòng sổ cũ
UNVERIFIED = "UNVERIFIED"         # broker CONFIRMABLE nhưng LỆCH vendor ⇒ không ghi CONFIRMED, hỏi Winston
CASH_DIVIDEND = "CASH_DIVIDEND"   # chỉ-giá-đổi đã khớp cashDividendReceiving ⇒ cổ tức tiền, không ghi registry


# ───────────────────────────────────────────────────────────────────────────── đọc dnse_raw ──

def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return v if math.isfinite(v) else 0.0


def modified_ict(md):
    """`modifiedDate` DNSE (UTC, hậu tố Z, tới nano giây) → datetime ICT; None nếu không parse."""
    s = str(md or "").strip()
    if not s:
        return None
    s = s.replace("Z", "")
    if "." in s:                                   # cắt nano giây về micro giây
        head, frac = s.split(".", 1)              # 3.10 fromisoformat chỉ nhận 3/6 chữ số:
        s = f"{head}.{(frac + '000000')[:6]}"      # VIB 2026-09-09 '…22.23138Z' (5 chữ số)
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ICT)


def aggregate(rows):
    """Gộp các lô (loan package) của MỘT mã trong MỘT bản ghi positions."""
    live = [r for r in rows if _f(r.get("openQuantity")) > 0]
    return {
        "qty": sum(_f(r.get("openQuantity")) for r in rows),
        "trade": sum(_f(r.get("tradeQuantity")) for r in rows),
        "closed": sum(_f(r.get("closedQuantity")) for r in rows),
        "accum": sum(_f(r.get("accumulateQuantity")) for r in rows),
        "cost": sum(_f(r.get("openQuantity")) * _f(r.get("costPrice")) for r in rows),
        "mkts": sorted({_f(r.get("marketPrice")) for r in live}),
        "mods": [str(r.get("modifiedDate") or "") for r in live],
        "lots": {str(r.get("id")): (_f(r.get("openQuantity")), _f(r.get("costPrice")))
                 for r in rows},
    }


def read_series(path, account_no):
    """[(ts, {sym: [rows]})] theo thời gian, CHỈ bản ghi positions của ĐÚNG account (§12).
    Bản ghi positions rỗng bị bỏ (lần đọc hỏng ≠ "không giữ gì")."""
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if d.get("kind") != "positions" or str(d.get("account_no")) != str(account_no):
                continue
            pos = (d.get("payload") or {}).get("positions") or []
            if not pos:
                continue
            by = {}
            for p in pos:
                if str(p.get("accountNo")) != str(account_no):
                    continue
                by.setdefault(p.get("symbol"), []).append(p)
            out.append((str(d.get("ts") or ""), by))
    out.sort(key=lambda x: x[0])
    return out


def accounts_in(path):
    """[(account_no, label)] xuất hiện trong file."""
    seen = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            a = d.get("account_no")
            if a and d.get("kind") == "positions" and a not in seen:
                seen[a] = d.get("account_label") or a
    return sorted(seen.items())


def previous_file(day, exec_dir=EXEC_DIR):
    """dnse_raw của NGÀY CÓ FILE gần nhất trước `day` (None nếu không có)."""
    best = None
    for p in glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl")):
        d = os.path.basename(p)[len("dnse_raw_"):-len(".jsonl")]
        if d < day and (best is None or d > best[0]):
            best = (d, p)
    return best[1] if best else None


def same_day_fills(path, account_no, ticker, day):
    """[(modified_ict, fillQuantity, side)] lệnh của mã có khớp trong ngày `day` theo sổ lệnh
    broker (kind=orders). Rỗng KHÔNG có nghĩa "chắc chắn không khớp" (sổ lệnh không phải lúc nào
    cũng được đọc) — nó chỉ là bằng chứng BỔ SUNG; chốt chặn chính là tổng giá vốn không tăng."""
    out = {}
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if d.get("kind") != "orders" or str(d.get("account_no")) != str(account_no):
                continue
            for o in (d.get("payload") or {}).get("orders") or []:
                if (o.get("symbol") == ticker and str(o.get("accountNo")) == str(account_no)
                        and str(o.get("transDate") or "")[:10] == day
                        and _f(o.get("fillQuantity")) > 0):
                    out[o.get("id")] = (modified_ict(o.get("modifiedDate")),
                                        _f(o.get("fillQuantity")), o.get("side"))
    return list(out.values())


# ───────────────────────────────────────────────────────────── phát hiện cấp TÀI KHOẢN (PURE) ──

def _key(s):
    return (s["qty"], s["closed"], s["accum"], round(s["cost"], 2))


def cost_tol(a, b):
    """Sai số TỔNG giá vốn chỉ do làm tròn `costPrice` (≤ 4 chữ số thập phân ⇒ ≤ 5e-5đ/cp mỗi
    lô). Tính trên TỔNG, không trên đ/cp: lệnh ma 1cp giá 100đ làm tổng tăng 100đ — chia cho KL
    thì còn 0,5đ/cp, lọt mọi sàn đ/cp (selfcheck A5)."""
    return 1e-4 * max(a["qty"], b["qty"]) + 0.01


def _credit_like(a, b):
    """a → b có hình dạng credit quyền (KL không giảm, giá vốn không tăng, không bán, không
    thêm CP bán được) — dùng để lùi qua trạng thái credit DỞ (DNSE credit từng gói vay)."""
    return (b["qty"] >= a["qty"] and b["cost"] - a["cost"] <= cost_tol(a, b)
            and b["closed"] == a["closed"] and b["trade"] == a["trade"])


def prev_trading_day(day):
    """Phiên liền trước `day` theo `vn_market` (lịch thiếu ngày nghỉ biến động ⇒ trả ngày MUỘN
    hơn thật ⇒ kiểm khoảng trống CHẶT hơn, không lỏng hơn)."""
    from trading_bot.vn_market import is_holiday
    d = dt.date.fromisoformat(day) - dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    return d.isoformat()


# Mùa nghỉ lễ BIẾN ĐỘNG mà `vn_market` không tự biết (Tết ÂL, Giỗ Tổ 10/3 ÂL, ngày bù quanh lễ cố
# định) — (tháng, ngày) đầu/cuối, cận rộng. `next_trading_day` trong các mùa này có thể trả một
# NGÀY NGHỈ ⇒ ex_date sai (arch-review v1 M4). Mùa được coi là ĐÃ KHAI BÁO khi `_VARIABLE_HOLIDAYS`
# có ít nhất 1 ngày của đúng năm trong mùa đó (người đã cập nhật lịch theo thông báo HoSE).
HOLIDAY_SEASONS = (((1, 10), (2, 28), "Tết Âm lịch"), ((3, 25), (5, 6), "Giỗ Tổ / 30-4 / 1-5"),
                   ((8, 28), (9, 6), "Quốc khánh + bù"), ((12, 28), (12, 31), "Tết Dương lịch"),
                   ((1, 1), (1, 4), "Tết Dương lịch"))
MAX_CREDIT_TO_EX_DAYS = 4       # D→ex bình thường 1 (T2–T5) hoặc 3 (T6); dài hơn = nghỉ lễ ⇒ hỏi người


def calendar_guard(day, ex_date):
    """None nếu ex_date suy từ lịch tin được; ngược lại lý do (⇒ AMBIGUOUS, người xác nhận)."""
    from trading_bot import vn_market
    d0, ex = dt.date.fromisoformat(day), dt.date.fromisoformat(ex_date)
    if (ex - d0).days > MAX_CREDIT_TO_EX_DAYS:
        return (f"phiên kế tiếp {ex_date} cách phiên credit {day} {(ex - d0).days} ngày lịch "
                f"(> {MAX_CREDIT_TO_EX_DAYS}) — kỳ nghỉ dài, người xác nhận ex-date")
    for (m0, d0_), (m1, d1), name in HOLIDAY_SEASONS:
        lo, hi = dt.date(ex.year, m0, d0_), dt.date(ex.year, m1, d1)
        if lo <= ex <= hi and not any(lo <= h <= hi for h in vn_market._VARIABLE_HOLIDAYS):
            return (f"ex_date suy ra {ex_date} nằm trong mùa nghỉ {name} {lo}→{hi} mà "
                    f"trading_bot/vn_market.py CHƯA khai báo ngày nghỉ biến động nào ⇒ "
                    f"next_trading_day có thể trả ngày nghỉ")
    return None


def account_evidence(series, ticker, day, fills=()):
    """PURE. Một tài khoản, một mã, phiên `day`. `series` = [(ts, {sym: rows})] gồm bản ghi CUỐI
    của file ngày trước + mọi bản ghi của `day` (đã sắp). Trả dict có `verdict`.

    Trạng thái TRƯỚC = đoạn (chuỗi bản ghi cùng KL/giá vốn) ngay trước đoạn cuối, lùi tiếp qua
    các đoạn TRUNG GIAN bắt đầu SAU 15:00 ICT nếu bước chuyển là credit-dở (BID 2026-08-14
    ZaloPay: 400 → 407 lúc 19:10 (1 gói) → 427 lúc 20:15 (gói còn lại)). Không lùi thì phần
    credit thứ hai bị so với trạng thái đã credit một nửa ⇒ hệ số sai.
    """
    segs = []                                       # [first_ts, state_cuối, {ts riêng biệt}]
    for ts, by in series:
        rows = by.get(ticker)
        st = aggregate(rows) if rows else aggregate([])
        if segs and _key(segs[-1][1]) == _key(st):
            segs[-1][1] = st
            segs[-1][2].add(ts[:19])               # 2 bản ghi cùng giây = 1 lần đọc API
        else:
            segs.append([ts, st, {ts[:19]}])
    if not segs or segs[-1][1]["qty"] <= 0:
        return {"verdict": NOT_CANDIDATE, "why": "không giữ mã ở bản ghi cuối"}
    post_first, s1, post_ts = segs[-1]
    n_post = len(post_ts)
    if not series[-1][0].startswith(day):
        return {"verdict": NOT_CANDIDATE, "why": f"không có bản ghi nào của {day}"}
    if len(segs) == 1:
        return {"verdict": NOT_CANDIDATE, "why": "KL/giá vốn không đổi trong cửa sổ quan sát"}
    j = len(segs) - 2
    close_mark = f"{day}T{CREDIT_WINDOW_START.isoformat()}"
    while (j >= 1 and segs[j][0] >= close_mark
           and _credit_like(segs[j - 1][1], segs[j][1]) and _credit_like(segs[j][1], s1)):
        j -= 1
    ts0, s0 = segs[j][0], segs[j][1]
    # mốc "bản ghi trước credit": bản ghi CUỐI của đoạn trước — dùng để xét lệnh khớp muộn
    ts0_last = max(ts for ts, by in series if ts < segs[j + 1][0]) if j + 1 < len(segs) else ts0
    q0, q1 = s0["qty"], s1["qty"]
    if q1 <= q0 or q0 <= 0:
        return {"verdict": NOT_CANDIDATE, "why": f"KL {q0:,.0f}→{q1:,.0f} không phải tăng từ vị thế có sẵn"}
    cash = (s0["cost"] - s1["cost"]) / q0
    if s1["cost"] - s0["cost"] > cost_tol(s0, s1):
        return {"verdict": NOT_CANDIDATE,
                "why": f"tổng giá vốn TĂNG {s1['cost'] - s0['cost']:+,.0f}đ ⇒ hình dạng mua/chuyển vào, không phải quyền"}

    ev = {"verdict": AMBIGUOUS, "q0": q0, "q1": q1, "ts_pre": ts0_last, "ts_post_first": post_first,
          "n_post": n_post, "cost0": round(s0["cost"], 4), "cost1": round(s1["cost"], 4),
          "trade0": s0["trade"], "trade1": s1["trade"], "mkt0": s0["mkts"], "mkt1": s1["mkts"],
          "lots": len(s1["lots"]), "segments_walked": len(segs) - 2 - j}
    hard, soft = [], []                     # hard ⇒ AMBIGUOUS; soft (đang điều chỉnh dở) ⇒ INSUFFICIENT
    if s1["closed"] != s0["closed"]:
        hard.append(f"closedQuantity {s0['closed']:,.0f}→{s1['closed']:,.0f} (có bán trong cửa sổ)")
    if abs((s1["accum"] - s0["accum"]) - (q1 - q0)) > 1e-9:
        hard.append(f"accumulateQuantity tăng {s1['accum'] - s0['accum']:+,.0f} ≠ KL tăng {q1 - q0:+,.0f}")
    if s1["trade"] > q0:
        # CP quyền mới credit CHƯA bán được (8/8 ca thật). Không đòi trade đứng yên tuyệt đối:
        # CP mua T−2 có thể về tài khoản (sellable) giữa bản ghi trước và sau — nhưng không bao
        # giờ vượt KL TRƯỚC sự kiện.
        hard.append(f"tradeQuantity {s1['trade']:,.0f} > KL trước sự kiện {q0:,.0f} (CP mới đã bán "
                    f"được — không phải mẫu credit quyền)")
    # THỜI ĐIỂM — đo bằng `ts` BẢN GHI, KHÔNG bằng `modifiedDate`: DNSE đổi modifiedDate MỌI lô
    # mỗi tối ~19:13–19:17 khi cập nhật giá dù KL không đổi (ACB SpaceX 09-29→10-02), nên
    # modifiedDate ≥15:00 không chứng minh gì (arch-review v1 B1). Bằng chứng giờ: trạng thái mới
    # được THẤY LẦN ĐẦU sau giờ đóng cửa của D. Bằng chứng ex-date thật nằm ở GIÁ (decide()).
    if not (post_first.startswith(day) and post_first[11:19] >= CREDIT_WINDOW_START.isoformat()):
        hard.append(f"trạng thái mới đã thấy từ {post_first} — TRƯỚC giờ đóng cửa {day} 15:00 "
                    f"(đổi KL trong phiên, không phải mẫu credit quyền tối T−1)")
    if ts0_last[:10] < prev_trading_day(day):
        hard.append(f"bản ghi cuối của trạng thái cũ là {ts0_last} — trước phiên liền trước "
                    f"{prev_trading_day(day)}: có khoảng trống quan sát, KL có thể đã đổi từ phiên "
                    f"khác")
    ev["broker_effective_ts"] = (dt.datetime.fromisoformat(post_first[:19]).replace(tzinfo=ICT)
                                 .astimezone(dt.timezone.utc).replace(tzinfo=None)
                                 .isoformat(timespec="seconds"))
    ev["modified_post"] = sorted(s1["mods"])          # chỉ tham khảo, KHÔNG phải bằng chứng
    if len(s1["mkts"]) != 1:
        # Các lô của CÙNG tài khoản mang marketPrice khác nhau ⇒ giá chưa nhất quán (gói vay đang
        # điều chỉnh dở, hoặc 1 lô nói "chưa điều chỉnh giá"). decide() cần ĐÚNG 1 giá; không
        # được chọn lọc giá nhỏ nhất (arch-review v2 N1 — bản v2 lỡ xoá chốt này).
        soft.append(f"các lô mang marketPrice khác nhau {s1['mkts']} — giá sau credit chưa nhất quán")
    if set(s0["lots"]) != set(s1["lots"]):
        hard.append(f"id lô đổi {sorted(s0['lots'])}→{sorted(s1['lots'])}")
    else:
        moved = {lid for lid in s0["lots"] if s1["lots"][lid] != s0["lots"][lid]}
        for lid, (lq0, lc0) in sorted(s0["lots"].items()):
            lq1, lc1 = s1["lots"][lid]
            if lq0 <= 0:
                continue
            lcash = (lq0 * lc0 - lq1 * lc1) / lq0
            if lq1 < lq0 or abs(lcash - cash) > 1.0:
                if lid not in moved and moved:
                    soft.append(f"lô {lid} còn NGUYÊN {lq0:,.0f}@{lc0:,.4f} trong khi lô khác đã "
                                f"đổi — DNSE đang điều chỉnh dở theo gói vay")
                else:
                    hard.append(f"lô {lid}: {lq0:,.0f}@{lc0:,.4f}→{lq1:,.0f}@{lc1:,.4f} (chân tiền "
                                f"lô {lcash:,.2f} ≠ vị thế {cash:,.2f}) — các lô KHÔNG cùng một sự kiện")
    late = [f for f in fills if f[0] is None or f[0].isoformat()[:19] >= ts0_last[:19]]
    if late:
        hard.append(f"sổ lệnh broker có {len(late)} lệnh KHỚP mã này sau bản ghi trước credit {ts0_last}")
    c = round(cash)
    if abs(cash - c) > CASH_TOL_VND:
        hard.append(f"chân tiền suy từ giá vốn {cash:,.4f}đ/cp không tròn đồng")
    ev["cash_leg"] = float(c) if abs(c) >= CASH_LEG_MIN_VND else 0.0
    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 1) / q0          # floor(q0·m) == q1 — đúng park_holdings
    if hard:
        ev["why"] = "; ".join(hard + soft)
        return ev
    if soft:
        ev["verdict"], ev["why"] = INSUFFICIENT, "; ".join(soft)
        return ev
    if n_post < MIN_POST_SNAPSHOTS:
        ev["verdict"] = INSUFFICIENT
        ev["why"] = (f"trạng thái sau credit mới có {n_post} lần đọc khác giây "
                     f"(< {MIN_POST_SNAPSHOTS})")
        return ev
    ev["verdict"] = CONFIRMABLE
    ev["why"] = "khớp mẫu credit quyền"
    return ev


# ─────────────────────────────────────────────────────────────── gộp cấp MÃ + hệ số (PURE) ──

def simplest_in(lo, hi):
    """Số thập phân ÍT CHỮ SỐ nhất trong [lo, hi). None nếu không có (≤ MAX_DECIMALS chữ số)."""
    for k in range(0, MAX_DECIMALS + 1):
        s = 10 ** k
        cand = math.ceil(lo * s - 1e-9) / s
        if lo - 1e-12 <= cand < hi:
            return round(cand, k)
    return None


VENDOR_UNREADABLE = "VENDOR_UNREADABLE"   # lịch vendor thiếu/hỏng ⇒ không biết vendor nói gì (KHÔNG chặn broker)

# ── đối chiếu vendor (CHỈ xác nhận — broker là nguồn chính) ──
QTY_CODES = ("ISS", "SPLIT")      # mã sự kiện vendor đổi KL (cùng quy ước nhánh vendor: hệ số = 1 + exercise_ratio)
VENDOR_MULT_TOL_PCT = 0.01        # quy ước 2026-09-24: lệch > 1% hệ số ⇒ UNVERIFIED
VENDOR_CASH_TOL_VND = 1.0         # quy ước 2026-09-24: lệch > 1đ/cp chân tiền ⇒ UNVERIFIED
VENDOR_EX_WINDOW_DAYS = 10        # sự kiện vendor cách ex broker ≤ N ngày lịch = có thể CÙNG sự kiện
V_VERIFIED, V_PARTIAL, V_MISMATCH = "VERIFIED", "PARTIAL", "MISMATCH"
V_NO_EVENT, V_UNREADABLE, V_FEED_DEAD = "NO_EVENT", "UNREADABLE", "FEED_DEAD"


def _vsum(e):
    return {k: e.get(k) for k in ("event_code", "date", "exercise_ratio", "value_per_share",
                                  "price_adjusting", "title") if k in e}


def _vnum(x):
    """Số vendor đọc được, hữu hạn, > 0 — ngược lại None (KHÔNG coi là 0: m1 arch-review v1)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) and v > 0 else None


def dedup_vendor(vendor_events):
    """Bỏ dòng vendor TRÙNG HỆT (cùng mã sự kiện/ngày/tỉ lệ/giá trị/tiêu đề) — feed ghi lặp một
    sự kiện ⇒ cộng tỉ lệ/DIV 2 lần ⇒ MISMATCH giả (m5). Hai sự kiện thật khác nhau luôn khác ít
    nhất một trường (tiêu đề) nên không bị gộp."""
    out, seen = [], set()
    for e in vendor_events:
        k = json.dumps(_vsum(e), sort_keys=True, default=str)
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def vendor_crosscheck(ex_date, m, cash, vendor_events):
    """PURE. Đối chiếu kết luận BROKER (hệ số KL `m` — 1.0 = KL không đổi —, chân tiền `cash`
    đ/cp, `ex_date`) với MỌI sự kiện vendor của mã. Trả {status, why, vendor}. KHÔNG bao giờ đổi
    số broker; chỉ nói vendor xác nhận, im, hay LỆCH.

      VERIFIED   vendor có sự kiện cùng ex và mọi trục broker khai đều khớp (hệ số ≤1%, tiền ≤1đ/cp)
      PARTIAL    vendor xác nhận một trục, trục kia vendor KHÔNG khai (vắng ≠ lệch, §28)
      MISMATCH   lệch ít nhất một trục, hoặc vendor có sự kiện CP ở ex KHÁC trong ±10 ngày, hoặc
                 vendor có sự kiện điều chỉnh giá loại khác cùng ex (broker không mô tả được)
      NO_EVENT   vendor đọc được, không có sự kiện nào gần ex
      UNREADABLE lịch vendor thiếu/hỏng
    Chỉ xét sự kiện `price_adjusting` (phát hành riêng lẻ/ESOP vendor có thể ghi ISS nhưng không
    đổi giá tham chiếu — ngoài phạm vi) và DIV."""
    if vendor_events == VENDOR_UNREADABLE:
        return {"status": V_UNREADABLE, "vendor": [],
                "why": "lịch vendor thiếu/đọc hỏng — chưa được vendor xác nhận (không chặn broker)"}
    ex = dt.date.fromisoformat(ex_date)
    near, problems = [], []
    for e in dedup_vendor(vendor_events):
        code = str(e.get("event_code") or "").upper()
        if not (e.get("price_adjusting") or code == "DIV"):
            continue
        try:
            d = dt.date.fromisoformat(str(e.get("date") or "")[:10])
        except ValueError:
            problems.append(f"vendor {code} có ngày không đọc được {e.get('date')!r}")
            continue
        if abs((d - ex).days) <= VENDOR_EX_WINDOW_DAYS:
            near.append((d, code, e))
    same = [(c, e) for d, c, e in near if d == ex]
    qty_same = [e for c, e in same if c in QTY_CODES]
    div_same = [e for c, e in same if c == "DIV"]
    odd_same = sorted({c for c, e in same if c not in QTY_CODES and c != "DIV"})
    qty_other = sorted({str(d) for d, c, e in near if d != ex and c in QTY_CODES})
    div_other = sorted({str(d) for d, c, e in near if d != ex and c == "DIV"})
    if qty_other:
        problems.append(f"ex-date: broker {ex_date} vs vendor sự kiện CP ex {qty_other}")
    if div_other and not any(c == "DIV" for c, e in same) and cash >= CASH_LEG_MIN_VND:
        problems.append(f"ex-date chân tiền: broker {cash:,.0f}đ/cp ex {ex_date} vs vendor DIV ex {div_other}")
    if odd_same:
        problems.append(f"vendor có sự kiện điều chỉnh giá {odd_same} cùng ex {ex_date} mà broker "
                        f"(KL ×{m}, tiền {cash:,.0f}đ/cp) không mô tả")
    qty_ok = cash_ok = None
    if qty_same:
        try:
            vm = 1.0 + sum(float(e.get("exercise_ratio")) for e in qty_same)
            if not math.isfinite(vm):
                raise ValueError(vm)
        except (TypeError, ValueError):
            problems.append(f"tỉ lệ vendor không đọc được {[e.get('exercise_ratio') for e in qty_same]}")
        else:
            if abs(vm - m) > VENDOR_MULT_TOL_PCT * m:
                problems.append(f"hệ số: broker ×{m} vs vendor ×{vm:.7g} (lệch {abs(vm - m) / m:.2%} "
                                f"> {VENDOR_MULT_TOL_PCT:.0%})")
            else:
                qty_ok = True
    elif m > 1.0:
        qty_ok = False
    dvals = [_vnum(e.get("value_per_share")) for e in div_same]
    if div_same and None in dvals:
        problems.append(f"giá trị DIV vendor không đọc được {[e.get('value_per_share') for e in div_same]}")
    elif div_same:
        v = sum(dvals)
        if abs(v - cash) > VENDOR_CASH_TOL_VND:
            problems.append(f"chân tiền: broker {cash:,.0f}đ/cp vs vendor DIV {v:,.0f}đ/cp "
                            f"(lệch > {VENDOR_CASH_TOL_VND:.0f}đ/cp)")
        else:
            cash_ok = True
    elif cash >= CASH_LEG_MIN_VND:
        cash_ok = False
    vendor = [_vsum(e) for d, c, e in near]
    if problems:
        return {"status": V_MISMATCH, "why": "; ".join(problems), "vendor": vendor}
    if not qty_same and not div_same:
        return {"status": V_NO_EVENT, "vendor": vendor,
                "why": "vendor không có sự kiện tương ứng — chưa được vendor xác nhận"}
    if qty_ok is not False and cash_ok is not False:
        return {"status": V_VERIFIED, "why": "vendor khớp broker", "vendor": vendor}
    miss = [x for x, ok in (("hệ số KL", qty_ok), ("chân tiền", cash_ok)) if ok is False]
    # Vendor CÓ sự kiện cùng ex (vd chỉ DIV) mà KHÔNG khai sự kiện CP broker thấy ⇒ trục KL — trục
    # duy nhất registry dùng — chưa ai xác nhận ⇒ `qty_unconfirmed` (caller hạ UNVERIFIED, m2).
    return {"status": V_PARTIAL, "vendor": vendor, "qty_unconfirmed": qty_ok is False,
            "why": f"vendor KHÔNG khai {miss} (vắng, không phải lệch) — phần còn lại khớp"}


PRICE_GATE_EXCHANGES = ("HOSE", "HNX")    # giá tham chiếu GDKHQ = f(giá ĐÓNG CỬA) chỉ ở 2 sàn này


def decide(ticker, day, ex_date, per_account, holders_not_credited, px_cum, vendor_events=(),
           exchange=None):
    """PURE. Quyết định cấp mã CHỈ từ broker (`_decide_qty`), rồi đối chiếu vendor
    (`vendor_crosscheck`) — vendor KHÔNG BAO GIỜ làm broker AMBIGUOUS/nhường quyền ghi; chỉ hạ
    CONFIRMABLE → UNVERIFIED khi LỆCH. Kết quả không-CONFIRMABLE vẫn mang `vendor_check` (để người
    làm sáng ca mơ hồ bằng lịch vendor nếu còn sống — KHÔNG tự ghi)."""
    out = _decide_qty(ticker, day, ex_date, per_account, holders_not_credited, px_cum, exchange)
    if out["verdict"] == NOT_CANDIDATE:
        return out
    if out["verdict"] == CONFIRMABLE:
        vc = vendor_crosscheck(ex_date, out["qty_multiplier"], out["cash_leg"], vendor_events)
        out["vendor_check"] = vc
        if vc["status"] == V_MISMATCH:
            out.update(verdict=UNVERIFIED,
                       why=f"broker {out['why']} — LỆCH VENDOR: {vc['why']} ⇒ hạ UNVERIFIED, Winston kiểm")
        elif vc.get("qty_unconfirmed"):
            out.update(verdict=UNVERIFIED,
                       why=(f"broker {out['why']} — VENDOR THIẾU trục KL: {vc['why']} (vendor có sự kiện "
                            f"khác cùng ex nhưng không khai sự kiện CP) ⇒ hạ UNVERIFIED, Winston kiểm"))
        return out
    out["vendor_check"] = ({"status": V_UNREADABLE, "vendor": [], "why": "lịch vendor thiếu/hỏng"}
                           if vendor_events == VENDOR_UNREADABLE else
                           {"status": "INFO", "why": "broker chưa quyết được — lịch vendor để người tham khảo",
                            "vendor": [_vsum(e) for e in vendor_events]})
    return out


def _decide_qty(ticker, day, ex_date, per_account, holders_not_credited, px_cum, exchange=None):
    """PURE. Gộp bằng chứng mọi tài khoản → quyết định cấp mã (KHÔNG nhìn vendor).

    per_account           {label: account_evidence(...)} — chỉ tài khoản có ứng viên (≠ NOT_CANDIDATE)
    holders_not_credited  [label] tài khoản ĐANG GIỮ mã ở bản ghi trước mà KHÔNG thấy credit (kể cả
                          tài khoản KHÔNG có bản ghi nào hôm nay — không quan sát được ≠ không giữ)
    px_cum                giá đóng cửa phiên `day` (hệ CÒN quyền) hoặc None
    exchange              sàn của mã (HOSE/HNX/UPCOM) hoặc None = không xác định. Chỉ HOSE/HNX
                          được tự xác nhận: UPCOM lấy tham chiếu = BÌNH QUÂN gia quyền phiên trước,
                          cổng giá dựng từ đóng cửa sai cơ sở ⇒ giả thuyết không-sự-kiện mất tác
                          dụng (arch-review v2 N7: ×1,03 giá cum 10.000 / tham chiếu 9.700 lọt).
    """
    from exdate_frame import FRAME_TOL_PCT, FRAME_TOL_VND, verify_post_event_price
    out = {"ticker": ticker, "credit_day": day, "ex_date": ex_date, "accounts": per_account,
           "px_cum": px_cum}
    reasons = []
    if not per_account:
        return dict(out, verdict=NOT_CANDIDATE, why="không tài khoản nào có ứng viên")
    for lbl, ev in sorted(per_account.items()):
        if ev["verdict"] != CONFIRMABLE:
            reasons.append(f"{lbl}: {ev['verdict']} — {ev.get('why')}")
    cal = calendar_guard(day, ex_date)
    if exchange not in PRICE_GATE_EXCHANGES:
        cal = "; ".join(x for x in (cal, (
            f"sàn {exchange or 'KHÔNG xác định được'} — cổng giá dựng từ giá đóng cửa chỉ đúng "
            f"HOSE/HNX (UPCOM tham chiếu = bình quân gia quyền)")) if x)
    if holders_not_credited:
        reasons.append(f"tài khoản {holders_not_credited} đang giữ mã mà CHƯA được credit cùng đêm")
    if cal:                                                        # lịch không tin được ⇒ người
        return dict(out, verdict=AMBIGUOUS, why="; ".join([cal] + reasons))
    if reasons:
        verdict = (INSUFFICIENT if all(ev["verdict"] in (CONFIRMABLE, INSUFFICIENT)
                                       for ev in per_account.values()) else AMBIGUOUS)
        return dict(out, verdict=verdict, why="; ".join(reasons))

    evs = list(per_account.values())
    cash = {ev["cash_leg"] for ev in evs}
    if max(cash) - min(cash) > 1.0:
        return dict(out, verdict=AMBIGUOUS, why=f"chân tiền khác nhau giữa tài khoản {sorted(cash)}")
    c = evs[0]["cash_leg"]
    mkts = {ev["mkt1"][0] for ev in evs}
    if len(mkts) != 1:
        return dict(out, verdict=AMBIGUOUS, why=f"marketPrice sau credit khác nhau giữa tài khoản {sorted(mkts)}")
    m1 = mkts.pop()
    lo = max(ev["m_lo"] for ev in evs)
    hi = min(ev["m_hi"] for ev in evs)
    out.update(cash_leg=c, market_price_post=m1, m_qty_interval=[round(lo, 8), round(hi, 8)])
    if lo >= hi:
        return dict(out, verdict=AMBIGUOUS, why=f"hệ số KL các tài khoản không giao nhau [{lo:.6f}, {hi:.6f})")
    if not px_cum or px_cum <= 0:
        return dict(out, verdict=INSUFFICIENT, why="không có giá đóng cửa cum của phiên credit")
    tol = max(FRAME_TOL_VND, m1 * FRAME_TOL_PCT)
    if m1 - tol <= 0 or px_cum - c <= 0:
        return dict(out, verdict=AMBIGUOUS, why=f"giá vô nghĩa (px_cum {px_cum}, chân tiền {c}, mkt {m1})")
    plo, phi = (px_cum - c) / (m1 + tol), (px_cum - c) / (m1 - tol)
    out["m_price_interval"] = [round(plo, 8), round(phi, 8)]
    lo2, hi2 = max(lo, plo), min(hi, phi + 1e-12)
    if lo2 >= hi2:
        return dict(out, verdict=AMBIGUOUS,
                    why=(f"hệ số KL [{lo:.6f}, {hi:.6f}) KHÔNG giao hệ số giá [{plo:.6f}, {phi:.6f}] "
                         f"(giá cum {px_cum:,.0f}, chân tiền {c:,.0f}, marketPrice {m1:,.0f}) — "
                         f"KL và giá không kể cùng một sự kiện (quyền mua? gói vay chưa xong?)"))
    m = simplest_in(lo2, hi2)
    if m is None or m <= 1.0:
        return dict(out, verdict=AMBIGUOUS, why=f"không chọn được hệ số hợp lý trong [{lo2}, {hi2})")
    from corp_actions import QTY_MULT_MAX
    if m > QTY_MULT_MAX:
        return dict(out, verdict=AMBIGUOUS, why=f"hệ số {m} > {QTY_MULT_MAX} (biên chặn registry) — người xác nhận")
    for lbl, ev in per_account.items():
        if int(math.floor(ev["q0"] * m + 1e-9)) != int(ev["q1"]):
            return dict(out, verdict=AMBIGUOUS,
                        why=f"{lbl}: floor({ev['q0']:,.0f}×{m}) ≠ {ev['q1']:,.0f}")
    px_ok, pwhy = verify_post_event_price(px_cum, m1, m, c)
    if px_ok is None:
        return dict(out, verdict=AMBIGUOUS, why=f"cổng giá: {pwhy}")
    # GIẢ THUYẾT KHÔNG: "không có sự kiện cổ phiếu" (hệ số 1, có/không chân tiền) cũng phải BỊ BÁC
    # bởi cùng cổng giá. Không bác được ⇒ giá KHÔNG rơi đủ để phân biệt ⇒ không có bằng chứng giá
    # (chuyển khoản CK giá vốn 0, CP về SAU ex-date, sự kiện tỉ lệ quá nhỏ so với dung sai).
    for c0 in sorted({c, 0.0}):
        null_ok, null_why = verify_post_event_price(px_cum, m1, 1.0, c0)
        if null_ok is not None:
            return dict(out, verdict=AMBIGUOUS,
                        why=(f"giá KHÔNG bác được giả thuyết không-sự-kiện (hệ số 1, chân tiền "
                             f"{c0:,.0f}): {null_why} ⇒ marketPrice {m1:,.0f} chưa rơi khỏi giá cum "
                             f"{px_cum:,.0f} — không có bằng chứng giá"))
    return dict(out, verdict=CONFIRMABLE, qty_multiplier=m, price_evidence=pwhy,
                why=f"KL+giá vốn+giá cùng kể sự kiện ×{m} chân tiền {c:,.0f}đ/cp")


# ─────────────────────────────────────────── CHỈ GIÁ đổi, KL KHÔNG đổi (cổ tức tiền / quyền mua) ──

CASHDIV_TOL_VND_PER_SHARE = 1.0   # cashDividendReceiving vs Σ q×c: dung sai 1đ/cp (quy ước 09-24)
PRICE_SCREEN_GAP = "_PRICE_SCREEN"   # "mã" giả của dòng báo thiếu dữ liệu sàng lọc chỉ-giá


def price_only_evidence(series, ticker, day):
    """PURE. Một tài khoản, một mã mà KL KHÔNG đổi giữa bản ghi CUỐI phiên trước (`series[0]`) và
    bản ghi cuối `day`. Hai tín hiệu broker ghi:
      · tổng giá vốn GIẢM (DNSE trừ cổ tức tiền vào costPrice — DGC 09-11 −8.000đ/cp, DRI 09-21:
        đúng bằng phần tăng cashDividendReceiving) ⇒ `cash_leg` = phần giảm / KL;
      · marketPrice đêm đổi so với đêm trước VÀ lượt cập nhật đêm D đã chạy (modifiedDate mọi lô ≥
        15:00 D). `stale` ⇒ DNSE chưa/không cập nhật giá đêm đó (VHM 08-12 giữ 72.100 cả ngày; VNM
        07-28 mang giá đóng cửa 07-27) — so giá đó với đóng cửa là báo động giả.
    Không tín hiệu nào ⇒ NOT_CANDIDATE. Ngược lại trả bằng chứng; quyết định ở cấp mã."""
    nc = {"verdict": NOT_CANDIDATE}
    if not series or series[0][0][:10] >= day or not series[-1][0].startswith(day):
        return dict(nc, why="không có cặp bản ghi phiên trước → phiên này")
    r0, r1 = series[0][1].get(ticker), series[-1][1].get(ticker)
    if not r0 or not r1:
        return dict(nc, why="không giữ mã ở cả hai mốc")
    s0, s1 = aggregate(r0), aggregate(r1)
    if s0["qty"] <= 0 or s1["qty"] != s0["qty"] or s1["closed"] != s0["closed"]:
        return dict(nc, why="KL/closedQuantity đổi — không phải dạng chỉ-giá")
    drop = s0["cost"] - s1["cost"]
    if drop < -cost_tol(s0, s1):
        return dict(nc, why="tổng giá vốn TĂNG khi KL không đổi — không phải dạng sự kiện")
    cash = drop / s0["qty"] if drop > cost_tol(s0, s1) else 0.0
    # Giá đêm chỉ là bằng chứng khi DNSE ĐÃ chạy lượt cập nhật đêm D: modifiedDate MỌI lô ≥ 15:00 D.
    # 07-28 thật: DNSE không chạy (VNM modifiedDate 07-27 19:34) mà bản ghi cuối 07-27 lại đọc TRƯỚC
    # lượt 19:34 ⇒ giá "đổi" so với mốc nhưng thực là đóng cửa 07-27 ⇒ 15 báo động giả nếu chỉ so giá.
    mark = dt.datetime.combine(dt.date.fromisoformat(day), CREDIT_WINDOW_START, tzinfo=ICT)
    mods = [modified_ict(m) for m in s1["mods"]]
    fresh = bool(mods) and all(m is not None and m >= mark for m in mods)
    stale = s1["mkts"] == s0["mkts"] or not fresh
    if cash == 0.0 and stale:
        return dict(nc, why="giá vốn và marketPrice đều không đổi")
    tail = []                                         # đoạn cuối cùng trạng thái (KL, giá vốn, giá)
    k1 = (s1["qty"], s1["closed"], round(s1["cost"], 2), tuple(s1["mkts"]))
    for ts, by in reversed(series):
        st = aggregate(by.get(ticker) or [])
        if (st["qty"], st["closed"], round(st["cost"], 2), tuple(st["mkts"])) != k1:
            break
        tail.append(ts)
    post_first, n_post = min(tail), len({t[:19] for t in tail})
    ev = {"verdict": CONFIRMABLE, "q": s1["qty"], "cash_raw": round(cash, 4),
          "cash_leg": float(round(cash)) if abs(round(cash)) >= CASH_LEG_MIN_VND else 0.0,
          "cost0": round(s0["cost"], 4), "cost1": round(s1["cost"], 4), "mkt0": s0["mkts"],
          "mkt1": s1["mkts"], "stale": stale, "ts_pre": series[0][0], "ts_post_first": post_first,
          "n_post": n_post}
    hard, soft = [], []
    if cash and abs(cash - round(cash)) > CASH_TOL_VND:
        hard.append(f"chân tiền suy từ giá vốn {cash:,.4f}đ/cp không tròn đồng")
    if not (post_first.startswith(day) and post_first[11:19] >= CREDIT_WINDOW_START.isoformat()):
        hard.append(f"trạng thái mới đã thấy từ {post_first} — trước 15:00 {day}")
    if cash and series[0][0][:10] < prev_trading_day(day):
        hard.append(f"mốc trước {series[0][0]} cách quá 1 phiên — khoảng trống quan sát")
    if len(s1["mkts"]) != 1:
        soft.append(f"các lô mang marketPrice khác nhau {s1['mkts']}")
    if n_post < MIN_POST_SNAPSHOTS:
        soft.append(f"trạng thái mới mới có {n_post} lần đọc khác giây (< {MIN_POST_SNAPSHOTS})")
    if hard:
        ev.update(verdict=AMBIGUOUS, why="; ".join(hard + soft))
    elif soft:
        ev.update(verdict=INSUFFICIENT, why="; ".join(soft))
    else:
        ev["why"] = "bằng chứng tài khoản nhất quán"
    return ev


def read_cashdiv(path, account_no):
    """[(ts, cashDividendReceiving)] từ bản ghi `balances` của ĐÚNG account (§12). Trường thiếu ⇒
    bỏ dòng (không coi là 0)."""
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if d.get("kind") != "balances" or str(d.get("account_no")) != str(account_no):
                continue
            pl = d.get("payload") or {}
            st = pl.get("stock") if isinstance(pl.get("stock"), dict) else pl
            v = st.get("cashDividendReceiving") if isinstance(st, dict) else None
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            if math.isfinite(v):
                out.append((str(d.get("ts") or ""), v))
    out.sort(key=lambda x: x[0])
    return out


def cashdiv_delta(points, day):
    """PURE. (delta, why) — phần TĂNG của cashDividendReceiving qua đêm `day`: giá trị cuối (phải
    lặp ≥ 2 lần đọc khác giây — 09-24 thật: 19:07 về 0 rồi 19:17 trở lại 3,7tr) trừ giá trị cuối
    trước 15:00 `day`. Thiếu dữ liệu ⇒ (None, lý do) — KHÔNG coi là 0."""
    mark = f"{day}T{CREDIT_WINDOW_START.isoformat()}"
    pre = [v for ts, v in points if ts < mark]
    if not pre:
        return None, "không có bản ghi balances trước 15:00 làm mốc"
    if not points or not points[-1][0].startswith(day):
        return None, f"không có bản ghi balances nào của {day}"
    last = points[-1][1]
    tail = set()
    for ts, v in reversed(points):
        if v != last:
            break
        tail.add(ts[:19])
    if len(tail) < MIN_POST_SNAPSHOTS:
        return None, f"cashDividendReceiving cuối {last:,.0f} mới có {len(tail)} lần đọc"
    return last - pre[-1], None


def decide_price_only(ticker, day, ex_date, per_account, px_cum, exchange, cashdiv, vendor_events=()):
    """PURE. Cấp mã cho dạng CHỈ-GIÁ. `cashdiv` {label: (delta, expected, why)} — delta = phần tăng
    cashDividendReceiving của tài khoản, expected = Σ q×chân tiền MỌI sự kiện (cả chân tiền của sự
    kiện CP như TPB) của tài khoản đêm đó.
      · có chân tiền (giá vốn giảm) ⇒ CASH_DIVIDEND chỉ khi MỌI tài khoản: cashDividendReceiving tăng
        khớp (≤1đ/cp) + cùng chân tiền + (HOSE/HNX có giá cum) giá đêm = cum − tiền. Không khớp ⇒
        AMBIGUOUS; thiếu dữ liệu ⇒ INSUFFICIENT. Vendor lệch ⇒ UNVERIFIED (Winston).
      · KHÔNG chân tiền mà giá tham chiếu bị hạ khỏi giá đóng cửa (HOSE/HNX, giá đêm đã cập nhật) ⇒
        AMBIGUOUS (quyền mua? CP về sau ex?) — KHÔNG đoán là cổ tức.
      · không đo được (thiếu giá cum/sàn) ⇒ `screen_gap` (caller gộp thành 1 dòng báo).
      · UPCOM không chân tiền ⇒ NOT_CANDIDATE: tham chiếu = bình quân gia quyền, giá không phải bằng
        chứng (giới hạn đã biết)."""
    from exdate_frame import FRAME_TOL_PCT, FRAME_TOL_VND, verify_post_event_price
    evs = list(per_account.values())
    out = {"kind": "PRICE_ONLY", "ticker": ticker, "credit_day": day, "ex_date": ex_date,
           "accounts": per_account, "px_cum": px_cum, "exchange": exchange}
    cs = [ev["cash_leg"] for ev in evs]
    c = max(cs)
    m1s = {tuple(ev["mkt1"]) for ev in evs}
    one_px = len(m1s) == 1 and len(next(iter(m1s))) == 1
    moved = None
    if exchange in PRICE_GATE_EXCHANGES and px_cum and px_cum > 0 and one_px:
        m1 = next(iter(m1s))[0]
        out["market_price_post"] = m1
        # ev KHÔNG chân tiền mà stale đã bị price_only_evidence loại; có chân tiền thì cổng giá dưới
        # vẫn chạy bất kể stale (giá chưa về cum−tiền ⇒ AMBIGUOUS, người xem).
        moved = abs(m1 - px_cum) > max(FRAME_TOL_VND, m1 * FRAME_TOL_PCT)
    if c == 0.0:
        if moved is None:
            if exchange in PRICE_GATE_EXCHANGES or exchange is None:
                return dict(out, verdict=INSUFFICIENT, screen_gap=True,
                            why=f"không sàng lọc được (sàn {exchange}, giá cum {px_cum}, giá đêm {sorted(m1s)})")
            return dict(out, verdict=NOT_CANDIDATE, why=f"sàn {exchange}: giá không phải bằng chứng")
        if not moved:
            return dict(out, verdict=NOT_CANDIDATE, why="giá đêm = giá đóng cửa trong dung sai")
        return dict(out, verdict=AMBIGUOUS, vendor_check={"status": "INFO", "why": "tham khảo",
                                                          "vendor": [_vsum(e) for e in vendor_events]}
                    if vendor_events != VENDOR_UNREADABLE else {"status": V_UNREADABLE, "vendor": [],
                                                               "why": "lịch vendor thiếu/hỏng"},
                    why=(f"giá tham chiếu bị điều chỉnh (đóng cửa {px_cum:,.0f} → giá đêm {out['market_price_post']:,.0f}) "
                         f"mà KL và tổng giá vốn KHÔNG đổi, không có chân tiền ⇒ KHÔNG đoán là cổ tức "
                         f"(quyền mua? CP thưởng về sau ex?) — người xác nhận"))
    out["cash_leg"] = c
    hard = [f"{lbl}: {ev['verdict']} — {ev.get('why')}" for lbl, ev in sorted(per_account.items())
            if ev["verdict"] == AMBIGUOUS]
    soft = [f"{lbl}: {ev['verdict']} — {ev.get('why')}" for lbl, ev in sorted(per_account.items())
            if ev["verdict"] == INSUFFICIENT]
    if max(cs) - min(cs) > VENDOR_CASH_TOL_VND:
        hard.append(f"chân tiền khác nhau giữa tài khoản {sorted(set(cs))}")
    for lbl in sorted(per_account):
        delta, expected, why = cashdiv.get(lbl, (None, None, "không có dữ liệu balances"))
        if delta is None:
            soft.append(f"{lbl}: {why}")
        elif abs(delta - expected) > CASHDIV_TOL_VND_PER_SHARE * per_account[lbl]["q"] + 1:
            hard.append(f"{lbl}: cashDividendReceiving tăng {delta:+,.0f} ≠ kỳ vọng {expected:,.0f} "
                           f"(Σ KL×chân tiền) ⇒ không xác nhận được là cổ tức tiền")
    if moved is not None:
        px_ok, pwhy = verify_post_event_price(px_cum, out["market_price_post"], 1.0, c)
        if px_ok is None:
            hard.append(f"cổng giá: {pwhy}")
        else:
            out["price_evidence"] = pwhy
    elif exchange in PRICE_GATE_EXCHANGES and not one_px:
        # HOSE/HNX mà các tài khoản/lô mang giá đêm KHÁC nhau ⇒ không biết giá nào là tham chiếu
        # mới ⇒ chưa kiểm được cổng giá (DNSE cập nhật dở?) ⇒ chưa đủ, chạy lại sau (arch-review M45).
        soft.append(f"giá đêm không thống nhất giữa tài khoản/lô {sorted(m1s)} ⇒ không kiểm được cổng giá")
    if moved is not None:
        gate = " + giá đêm khớp cum−tiền"
    elif exchange not in PRICE_GATE_EXCHANGES:
        gate = f" (sàn {exchange}: giá tham chiếu không phải bằng chứng, không dùng cổng giá)"
    else:
        gate = f" (sàn {exchange} nhưng KHÔNG có giá cum {px_cum!r} ⇒ CHƯA kiểm cổng giá)"
    if hard or soft:
        return dict(out, verdict=AMBIGUOUS if hard else INSUFFICIENT, why="; ".join(hard + soft),
                    vendor_check=vendor_crosscheck(ex_date, 1.0, c, vendor_events))
    vc = vendor_crosscheck(ex_date, 1.0, c, vendor_events)
    out["vendor_check"] = vc
    why = f"cổ tức tiền {c:,.0f}đ/cp: giá vốn DNSE giảm đúng q×c + cashDividendReceiving tăng khớp{gate}"
    if vc["status"] == V_MISMATCH:
        return dict(out, verdict=UNVERIFIED, why=f"{why} — LỆCH VENDOR: {vc['why']} ⇒ Winston kiểm")
    return dict(out, verdict=CASH_DIVIDEND, why=why)


# ──────────────────────────────────────────────────────────── điều phối 1 phiên (đọc file) ──

PRICE_SCREEN_BUDGET_S = 90       # ngân sách thời gian TỔNG cho sàng lọc chỉ-giá (gọi DNSE) mỗi lượt


def scan_day(day, px_cum_fn, vendor_events_fn=lambda tk: [], exec_dir=EXEC_DIR, cutoff=None,
             exchange_fn=lambda tk: None):
    """Mọi mã có ứng viên credit quyền ở phiên `day`, mọi tài khoản. Trả [decide(...)] (pha KL)
    + kết quả sàng lọc CHỈ-GIÁ (không ngân sách — replay/CLI). Cron dùng `scan_qty` rồi
    `scan_price_only` tách pha (RC4: ghi registry sự kiện KL TRƯỚC khi gọi DNSE cho chỉ-giá).

    px_cum_fn(ticker, day) → giá đóng cửa cum hoặc None. vendor_events_fn(ticker) → [ev] |
    VENDOR_UNREADABLE. exchange_fn(ticker) → "HOSE"/"HNX"/"UPCOM"/None (None ⇒ MƠ HỒ).
    `cutoff` ("HH:MM", chỉ cho replay) — bỏ bản ghi của `day` sau giờ đó, để mô phỏng đúng cái
    cron 19:25 nhìn thấy.
    """
    out, ctx = scan_qty(day, px_cum_fn, vendor_events_fn, exec_dir, cutoff, exchange_fn)
    return out + scan_price_only(ctx)


def scan_qty(day, px_cum_fn, vendor_events_fn=lambda tk: [], exec_dir=EXEC_DIR, cutoff=None,
             exchange_fn=lambda tk: None):
    """Pha KL: (kết quả decide() mọi mã có ứng viên credit, ctx cho `scan_price_only`). Chỉ gọi
    px_cum_fn/exchange_fn cho mã ỨNG VIÊN KL (vài mã) — không sàng lọc cả danh mục."""
    from trading_bot.vn_market import next_trading_day
    path = os.path.join(exec_dir, f"dnse_raw_{day}.jsonl")
    prev = previous_file(day, exec_dir)
    ex_date = next_trading_day(dt.date.fromisoformat(day)).isoformat()
    per_ticker, held_before, per_price, cashdiv_pts = {}, {}, {}, {}
    today_accts = dict(accounts_in(path))
    for acct, label in (accounts_in(prev) if prev else []):
        if acct in today_accts:
            continue
        # Tài khoản có ở phiên trước mà KHÔNG có bản ghi nào hôm nay ⇒ không quan sát được nó đã
        # được credit chưa — giữ mã nào ở bản ghi cuối thì là "đang giữ mà chưa thấy credit".
        pre = read_series(prev, acct)
        for tk, rows in (pre[-1][1].items() if pre else []):
            if aggregate(rows)["qty"] > 0:
                held_before.setdefault(tk, []).append(f"{label} (không có bản ghi {day})")
    for acct, label in sorted(today_accts.items()):
        series = read_series(path, acct)
        if cutoff:
            series = [x for x in series if x[0] <= f"{day}T{cutoff}"]
        if prev:
            pre = read_series(prev, acct)
            series = pre[-1:] + series
        if not series:
            continue
        tickers = set()
        for _ts, by in series:
            tickers |= {t for t, rows in by.items() if any(_f(r.get("openQuantity")) > 0 for r in rows)}
        for tk in sorted(tickers):
            fills = same_day_fills(path, acct, tk, day)
            ev = account_evidence(series, tk, day, fills)
            if ev["verdict"] != NOT_CANDIDATE:
                per_ticker.setdefault(tk, {})[label] = ev
            else:
                first, last = series[0][1].get(tk), series[-1][1].get(tk)
                if first and last and aggregate(first)["qty"] > 0 and aggregate(last)["qty"] > 0:
                    held_before.setdefault(tk, []).append(label)
                po = price_only_evidence(series, tk, day)
                if po["verdict"] != NOT_CANDIDATE:
                    per_price.setdefault(tk, {})[label] = po
        cashdiv_pts[label] = ((read_cashdiv(prev, acct)[-1:] if prev else []) + read_cashdiv(path, acct))
        if cutoff:
            cashdiv_pts[label] = [x for x in cashdiv_pts[label] if x[0] <= f"{day}T{cutoff}"]
    out = []
    for tk, per in sorted(per_ticker.items()):
        holders = [lbl for lbl in held_before.get(tk, []) if lbl not in per]
        px = px_cum_fn(tk, day)
        out.append(decide(tk, day, ex_date, per, holders, px, vendor_events_fn(tk),
                          exchange_fn(tk)))
    ctx = {"day": day, "ex_date": ex_date, "per_ticker": per_ticker, "per_price": per_price,
           "cashdiv_pts": cashdiv_pts, "px_cum_fn": px_cum_fn, "vendor_events_fn": vendor_events_fn,
           "exchange_fn": exchange_fn}
    return out, ctx


def scan_price_only(ctx, deadline=None, clock=None):
    """Pha CHỈ-GIÁ (cổ tức tiền / quyền mua) trên ctx của `scan_qty`. `deadline` (giá trị của
    `clock()`, mặc định time.monotonic) — NGÂN SÁCH THỜI GIAN TỔNG cho các lời gọi DNSE: kiểm
    TRƯỚC prefetch và TRƯỚC mỗi mã; hết ⇒ mã còn lại vào dòng thiếu dữ liệu (INSUFFICIENT, có lý do
    'hết ngân sách'), KHÔNG chờ thêm (RC4). Trần thực = deadline + 1 lời gọi đang dở (timeout của nó)."""
    import time
    clock = clock or time.monotonic
    day, ex_date = ctx["day"], ctx["ex_date"]
    per_ticker, per_price, cashdiv_pts = ctx["per_ticker"], ctx["per_price"], ctx["cashdiv_pts"]
    px_cum_fn, vendor_events_fn, exchange_fn = ctx["px_cum_fn"], ctx["vendor_events_fn"], ctx["exchange_fn"]
    out = []
    # ── CHỈ-GIÁ: mã KL không đổi ở MỌI tài khoản (mã có ứng viên KL ở bất kỳ tài khoản nào đã do
    # decide() lo — tài khoản chưa được credit nằm ở holders_not_credited, không xét lại ở đây).
    per_price = {tk: per for tk, per in per_price.items() if tk not in per_ticker}
    from trading_bot.vn_market import is_holiday
    d0 = dt.date.fromisoformat(day)
    if d0.weekday() >= 5 or is_holiday(d0):
        per_price = {}                  # ngày không có phiên ⇒ không có giá đóng cửa để so (08-01 T7)
    expected = {}                       # Σ KL×chân tiền MỌI sự kiện của tài khoản đêm đó
    for per in list(per_ticker.values()) + list(per_price.values()):
        for lbl, ev in per.items():
            q = ev.get("q0", ev.get("q", 0.0))
            expected[lbl] = expected.get(lbl, 0.0) + q * (ev.get("cash_leg") or 0.0)
    cashdiv = {}
    for lbl, pts in cashdiv_pts.items():
        delta, why = cashdiv_delta(pts, day)
        cashdiv[lbl] = (delta, expected.get(lbl, 0.0), why)
    def _over():
        return deadline is not None and clock() >= deadline
    if per_price and hasattr(px_cum_fn, "prefetch") and not _over():
        px_cum_fn.prefetch(sorted(per_price), day)      # 1 lời gọi DNSE cho cả lô (live)
    gaps = []
    for tk, per in sorted(per_price.items()):
        if _over():
            gaps.append(f"{tk} (hết ngân sách thời gian sàng lọc chỉ-giá — chưa gọi DNSE)")
            continue
        r = decide_price_only(tk, day, ex_date, per, px_cum_fn(tk, day), exchange_fn(tk),
                              cashdiv, vendor_events_fn(tk))
        if r.get("screen_gap"):
            gaps.append(f"{tk} ({r['why']})")
        elif r["verdict"] != NOT_CANDIDATE:
            out.append(r)
    if gaps:
        # MỘT dòng cho cả lô (DNSE chết ⇒ không spam 30 câu hỏi) — nhưng KHÔNG im lặng (§29).
        out.append({"kind": "PRICE_SCREEN_GAP", "ticker": PRICE_SCREEN_GAP, "credit_day": day,
                    "ex_date": ex_date, "accounts": {}, "verdict": INSUFFICIENT,
                    "why": (f"không sàng lọc được biến động CHỈ-GIÁ (cổ tức tiền/quyền mua) cho "
                            f"{len(gaps)} mã (thiếu giá cum/sàn hoặc hết ngân sách): {'; '.join(gaps)}")})
    return out


def held_tickers(day, exec_dir=EXEC_DIR):
    """{mã: [nhãn tài khoản]} đang giữ (openQuantity > 0) theo bản ghi positions CUỐI của MỖI tài
    khoản: file `day`; tài khoản KHÔNG có bản ghi nào ở `day` ⇒ bản ghi cuối file phiên trước
    (`held_before`, RC2 — bản cũ chỉ đọc file hôm nay ⇒ tài khoản vắng hôm nay bị coi là "không
    giữ"). Không có file nào đọc được ⇒ None (KHÔNG coi là "không giữ gì")."""
    path = os.path.join(exec_dir, f"dnse_raw_{day}.jsonl")
    prev = previous_file(day, exec_dir)
    today = dict(accounts_in(path)) if os.path.exists(path) else {}
    before = dict(accounts_in(prev)) if prev else {}
    if not today and not before:
        return None
    out = {}
    for acct, label in sorted(today.items()):
        ser = read_series(path, acct)
        for tk, rows in (ser[-1][1].items() if ser else []):
            if aggregate(rows)["qty"] > 0:
                out.setdefault(tk, []).append(label)
    for acct, label in sorted(before.items()):
        if acct in today:
            continue
        ser = read_series(prev, acct)
        for tk, rows in (ser[-1][1].items() if ser else []):
            if aggregate(rows)["qty"] > 0:
                out.setdefault(tk, []).append(f"{label} (bản ghi cuối {os.path.basename(prev)})")
    return out


# ─────────────────────────────────────────────────────────────── record + ledger (ghi file) ──

def build_record(dec, now_ict):
    """Record `data/corp_actions.json` cho quyết định CONFIRMABLE (ghi được) hoặc UNVERIFIED (đề xuất
    cho người — KHÔNG ghi) — provenance=broker, kèm `vendor_check` (vendor chỉ xác nhận)."""
    tk, ex, m, c = dec["ticker"], dec["ex_date"], dec["qty_multiplier"], dec["cash_leg"]
    vc = dec.get("vendor_check") or {"status": V_NO_EVENT, "why": "không có kết quả đối chiếu"}
    ev_lines = []
    for lbl, ev in sorted(dec["accounts"].items()):
        ev_lines.append(
            f"BROKER {lbl}: KL {ev['q0']:,.0f}→{ev['q1']:,.0f}, tradeQuantity "
            f"{ev['trade0']:,.0f}→{ev['trade1']:,.0f} (≤ KL trước), closedQuantity không đổi; "
            f"bản ghi cuối trạng thái cũ {ev['ts_pre']} ICT, trạng thái mới thấy lần đầu "
            f"{ev['ts_post_first']} ICT và lặp ở {ev['n_post']} lần đọc khác giây; tổng giá vốn "
            f"{ev['cost0']:,.2f}→{ev['cost1']:,.2f} (chân tiền {ev['cash_leg']:,.0f}đ/cp); "
            f"marketPrice {ev['mkt0']}→{ev['mkt1']}")
    ev_lines.append(f"GIÁ: {dec['price_evidence']}; giá cum = đóng cửa {dec['credit_day']} "
                    f"{dec['px_cum']:,.0f}; giả thuyết hệ số 1 bị bác; hệ số KL "
                    f"{dec['m_qty_interval']} ∩ hệ số giá {dec['m_price_interval']} ⇒ chọn {m}")
    ev_lines.append(f"EX-DATE SUY RA: KL mới thấy lần đầu sau 15:00 ICT phiên {dec['credit_day']} và "
                    f"marketPrice đã ở hệ sau sự kiện so với đóng cửa phiên đó ⇒ GDKHQ = phiên kế tiếp "
                    f"{ex} theo trading_bot/vn_market.py. KHÔNG từ công bố sàn.")
    ev_lines.append(f"VENDOR (chỉ xác nhận chéo): {vc['status']} — {vc['why']}")
    if dec["verdict"] == UNVERIFIED:
        status = (f"UNVERIFIED — corp_action_auto_confirm.py nhánh BROKER {now_ict}: broker ×{m} "
                  f"chân tiền {c:,.0f}đ/cp LỆCH vendor ({vc['why']}). Winston kiểm nguồn; người chốt: "
                  f"đổi thành 'CONFIRMED …' (giữ số broker) hoặc bỏ record")
    else:
        status = (f"CONFIRMED — corp_action_auto_confirm.py nhánh BROKER {now_ict} "
                  f"(provenance=broker — nguồn chính: KL + tổng giá vốn + giá tham chiếu; vendor "
                  f"{vc['status']}). Thu hồi: đổi _status thành 'REVOKED ...'")
    rec = {
        "id": f"{tk}-{ex}-BROKER-SHARE-EVENT",
        "ticker": tk,
        "event_type": "BONUS_ISSUE",
        "ratio_text": (f"Sự kiện tăng KL ×{m} suy từ broker (thưởng/cổ tức CP/chia tách KHÔNG phân "
                       f"biệt được từ broker)"
                       + (f", kèm chân tiền mặt {c:,.0f}đ/cp" if c else "")),
        "qty_multiplier": m,
        "ex_date": ex,
        "record_date": None,
        "broker_effective_ts": min(ev["broker_effective_ts"] for ev in dec["accounts"].values()),
        "_status": status,
        "provenance": "broker",
        "vendor_check": {"status": vc["status"], "why": vc["why"]},
        "verified_by_vendor": vc["status"] == V_VERIFIED,
        "confirmed_by": "corp_action_auto_confirm.py (agent, nhánh broker)",
        "decided_by": "agent",
        "confirmed_at": now_ict,
        "evidence": ev_lines,
        "verify_against_bq": (f"PENDING — chạy sau {ex}: python3 mike/bin/corp_actions.py "
                              f"--verify {tk}-{ex}-BROKER-SHARE-EVENT"),
        "note": ("ex_date SUY RA từ thời điểm broker credit; broker là nguồn chính — vendor chỉ xác "
                 "nhận chéo, KHÔNG đè số broker."),
    }
    if c:
        rec["cash_leg_vnd_per_share"] = c
    return rec


def ledger_key(e):
    """Khoá idempotent của 1 mục sổ. Mục đối chiếu REGISTRY (RC1) thêm id record ⇒ người thu hồi
    record cũ rồi ghi record khác cho cùng (mã, ex) ⇒ hỏi lại 1 lần cho record mới."""
    k = [e.get("mode"), e.get("ticker"), e.get("credit_day"), e.get("verdict")]
    rid = (e.get("registry_check") or {}).get("record_id")
    return k + [rid] if rid else k


def ledger_state(path=LEDGER_FILE):
    """Sổ 2 pha (at-least-once, arch-review v1 M2): dòng `kind=intent` ghi TRƯỚC mọi tác dụng ngoài
    (registry, bus), dòng `kind=done` ghi SAU khi bus nhận (rc=0). Trả (intents {key: entry},
    done {key}). Intent chưa có done = việc dở (kill / bus lỗi) ⇒ lượt sau GỬI BÙ, không bỏ qua.
    Dòng hỏng ⇒ CorpActionLedgerError (không im lặng coi như chưa từng có — sẽ ghi/hỏi lặp)."""
    intents, done = {}, set()
    if not os.path.exists(path):
        return intents, done
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                raise CorpActionLedgerError(f"{path}:{n} không phải JSON ({e})") from e
            k = tuple(d.get("key") or ledger_key(d))
            if d.get("kind") == "done":
                done.add(k)
            else:
                intents[k] = d
    return intents, done


class CorpActionLedgerError(RuntimeError):
    pass


def ledger_append(entries, path=LEDGER_FILE):
    """Ghi thêm vào sổ, ATOMIC (đọc cũ + tmp + os.replace) — kill giữa chừng không để lại dòng dở."""
    old = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
        if old and not old.endswith("\n"):
            old += "\n"
    import tempfile
    fd, tmp = tempfile.mkstemp(prefix=".corp_action_broker_ledger.", suffix=".tmp",
                               dir=os.path.dirname(path) or ".")    # tên riêng/tiến trình
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(old)
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# ───────────────────────────────────────────────────────────────────────────── replay CLI ──

BQ_TIMEOUT_S = 180


def bq_unadjusted_close(pairs):
    """{(ticker, day): Price} — cột `Price` CHƯA điều chỉnh (Close đã điều chỉnh hồi tố sẽ nằm
    ở hệ SAU sự kiện ⇒ sai hệ). CHỈ cho replay ngày QUÁ KHỨ (§6)."""
    import subprocess
    if not pairs:
        return {}
    tks = sorted({t for t, _ in pairs})
    days = sorted({d for _, d in pairs})
    sql = (f"SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Price FROM tav2_bq.ticker AS t "
           f"WHERE t.ticker IN ({','.join(repr(t) for t in tks)}) "
           f"AND t.time IN ({','.join(f'DATE {d!r}' for d in days)})")
    env = dict(os.environ)
    try:   # treo mạng/bq không được giữ khoá sổ của cron 19:25 vô hạn (arch-review v4 #10)
        r = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json",
                            "--project_id=lithe-record-440915-m9", "--max_rows=100000", sql],
                           capture_output=True, text=True, env=env, timeout=BQ_TIMEOUT_S)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"bq treo > {BQ_TIMEOUT_S}s") from e
    if r.returncode != 0:
        raise RuntimeError(f"bq lỗi: {(r.stderr or r.stdout).strip()[:300]}")
    return {(x["ticker"], x["d"]): _f(x["Price"]) for x in json.loads(r.stdout or "[]")}


def replay(start, end, exec_dir=EXEC_DIR, px_map=None, cutoff=None, exchange_fn=None):
    """Chạy `scan_day` trên mọi phiên có dnse_raw trong [start, end]. Chỉ ĐỌC. `exchange_fn` None ⇒
    giả định HOSE mọi mã (cách đo cũ cho sự kiện KL; với CHỈ-GIÁ sẽ báo nhầm mã UPCOM — truyền sàn
    thật nếu muốn đo nhánh đó)."""
    days = sorted(os.path.basename(p)[len("dnse_raw_"):-len(".jsonl")]
                  for p in glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl")))
    days = [d for d in days if start <= d <= end]
    exch = exchange_fn or (lambda t: "HOSE")
    asked = set()

    def _record(t, dd):                                # lượt 1: ghi lại MỌI cặp giá cần, trả None
        asked.add((t, dd))
    first = {d: scan_day(d, _record, exec_dir=exec_dir, cutoff=cutoff, exchange_fn=exch)
             for d in days}
    if px_map is None:
        px_map = bq_unadjusted_close(asked)
    out = []
    for d in days:
        if first[d]:
            out.extend(scan_day(d, lambda t, dd: px_map.get((t, dd)), exec_dir=exec_dir,
                                cutoff=cutoff, exchange_fn=exch))
    return days, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--replay", nargs=2, metavar=("START", "END"), required=True)
    ap.add_argument("--cutoff", default=None, help="HH:MM — mô phỏng lượt cron chạy lúc đó")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--real-exchange", action="store_true",
                    help="hỏi sàn THẬT qua DNSE marketId (chỉ đọc) thay vì giả định HOSE — cần để đo nhánh CHỈ-GIÁ")
    a = ap.parse_args()
    exch = None
    if a.real_exchange:
        from corp_action_auto_confirm import _exchange_fn
        exch = _exchange_fn()
    days, res = replay(*a.replay, cutoff=a.cutoff, exchange_fn=exch)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    print(f"replay {a.replay[0]}→{a.replay[1]}: {len(days)} phiên có dnse_raw, {len(res)} ứng viên "
          f"({'sàn THẬT qua DNSE' if exch else 'GIẢ ĐỊNH sàn HOSE mọi mã — live hỏi DNSE marketId'})")
    for r in res:
        print(f"  {r['credit_day']} {r['ticker']:4s} ex {r['ex_date']} {r['verdict']:12s} "
              f"×{r.get('qty_multiplier', '-')} cash {r.get('cash_leg', '-')} "
              f"vendor={(r.get('vendor_check') or {}).get('status', '-')} — {r['why'][:220]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
