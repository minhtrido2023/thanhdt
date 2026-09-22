#!/usr/bin/env python3
"""daily_nav_snapshot.py --account SpaceX --date 2026-07-03 [--starting-capital 1000000000]

Tính NAV thật cuối ngày (dùng chung nguyên tắc với verify_account_snapshot.py /
reconcile_equity.py — KHÔNG đọc field ước tính, chỉ dùng fill thật + giá BQ + balance API
thật) và ghi vào lịch sử `data/execution_logs/nav_history_{account}.csv` để daily/weekly/
monthly report đều đọc từ MỘT nguồn duy nhất, nhất quán.

In ra 1 đoạn tóm tắt ngắn (dùng cho daily report — đơn giản, chỉ NAV + biến động) và ghi
JSON chi tiết ra `data/execution_logs/nav_snapshot_{account}_{date}.json`.

`--from-raw` (aria-A2, 2026-09-13): tính lại NAV cho một --date QUÁ KHỨ bị thiếu dòng, CHỈ từ
bản ghi positions + balances cuối ngày của đúng account trong `dnse_raw_{date}.jsonl` — không gọi
broker (đường thường luôn lấy vị thế LIVE, sai với ngày cũ đã có giao dịch sau đó). Giá = cột
`Price` (THÔ) của BQ, KHÔNG phải `Close`: `Close` điều chỉnh hồi tố từ hôm nay ⇒ với ngày trước
một corp-action nó lệch giá bảng điện (đo thật VHM 21/07: Close 68.200, broker 136.900). Dòng
ghi `nav_is_estimate=True` + `nav_source`. Giá BQ lệch `marketPrice` của vị thế >5% chỉ được
chấp nhận khi có bằng chứng cơ khí: marketPrice = giá phiên TRƯỚC (feed trễ, ca PVT/TCB 10/08)
hoặc corp-action CONFIRMED ex_date sau --date mà Price/mult khớp (broker ghi có sớm, ca MSB
27/08 ⇒ quy KL về trước sự kiện). Còn lại ⇒ rc=4, không ghi, không đoán.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import subprocess
import sys
import time as _time

# Chuẩn hóa TZ = ICT cho TOÀN BỘ tiến trình (server chạy UTC): mọi timestamp script này
# tạo ra (kể cả bản ghi balances do brokers._log_raw ghi hộ) phải CÙNG múi giờ với journal
# của bot (bot chạy TZ ICT qua run_bot.sh) — thiếu dòng này, invariant so sánh
# balance_ts vs fill_ts bên dưới so UTC với ICT và từ chối nhầm (bug tự cắn 2026-07-07).
os.environ["TZ"] = "Asia/Ho_Chi_Minh"
_time.tzset()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402

# gốc cây neo theo marker `wc_env.sh` (wc_paths) — đếm cấp dirname SAI khi script chạy
# từ worktree `mike/agents/wt-*/bin/` (sự cố 2026-09-12, chặn báo cáo nhà đầu tư).
WC_ROOT = wc_paths.find_wc_root(__file__)
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE_TMPL = os.path.join(EXEC_DIR, "nav_history_{account}.csv")
CORP_ACTIONS_FILE = os.path.join(WC_ROOT, "data", "corp_actions.json")


def confirmed_qty_multiplier_after(ticker, asof_date):
    """Tích các `qty_multiplier` CONFIRMED trong corp_actions.json cho `ticker` có `ex_date`
    SAU `asof_date`. Trả 1.0 nếu không có sự kiện nào áp dụng.

    Dùng để quy đổi NGƯỢC vị thế broker LIVE (đã phản ánh sự kiện) về vị thế tại `asof_date`
    (trước sự kiện) — broker_positions() luôn trả ảnh chụp HIỆN TẠI bất kể --date, và DNSE
    credit cổ phiếu sớm hơn ex_date 1 phiên (mẫu hình VHM/MBB/BID/VIX/MSB/VIB, xem
    corp_action_auto_confirm.py), nên vị thế LIVE hôm nay có thể đã lớn hơn vị thế thật tại
    một --date lịch sử gần đây dù ex_date ghi sau ngày đó.
    """
    if not os.path.exists(CORP_ACTIONS_FILE):
        return 1.0
    with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
        actions = json.load(f).get("actions") or []
    mult = 1.0
    for a in actions:
        if str(a.get("ticker", "")).upper() != ticker.upper():
            continue
        if not str(a.get("_status", "")).upper().startswith("CONFIRMED"):
            continue
        ex_date = str(a.get("ex_date") or "")[:10]
        if ex_date and ex_date > asof_date:
            try:
                mult *= float(a.get("qty_multiplier") or 1.0)
            except (TypeError, ValueError):
                pass
    return mult


def trading_dates_with_fills(account, upto_date):
    dates = []
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, f"exec_{account}_*_journal.csv"))):
        base = os.path.basename(path)
        date = base[len(f"exec_{account}_"):-len("_journal.csv")]
        if date <= upto_date:
            dates.append(date)
    return dates


def today_sell_value(account, date):
    """Tổng giá trị lệnh BÁN đã khớp trong ngày (dùng để cảnh báo balance có thể còn stale
    khi so với biến động cash — xem ghi chú ở latest_balance)."""
    path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
    if not os.path.exists(path):
        return 0.0
    latest_by_child = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL" or str(row.get("side") or "").lower() != "sell":
                continue
            child_oid = row.get("child_oid")
            ts = row.get("ts", "")
            prev = latest_by_child.get(child_oid)
            if prev is None or ts >= prev[0]:
                latest_by_child[child_oid] = (ts, float(row.get("qty") or 0),
                                               float(row.get("price") or 0))
    return sum(qty * price for _, qty, price in latest_by_child.values())


RAW_PRICE_PREV_MATCH_PCT = 0.5   # marketPrice coi là "giá phiên trước" khi lệch ≤ ngưỡng này


def raw_positions(account_no, date):
    """({sym: {"qty", "marketPrice"}}, ts) từ bản ghi positions CUỐI CÙNG của account trong
    dnse_raw_{date}.jsonl. Cùng quy tắc với `verify_account_snapshot.broker_positions_from_raw`
    (lọc account tuyệt đối §12, gộp loan package theo mã) — thêm `ts` để kiểm bất biến
    "vị thế mới hơn cú khớp cuối" giống balance. Không có bản ghi ⇒ (None, None)."""
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return None, None
    latest, latest_ts = None, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if rec.get("kind") != "positions" or rec.get("account_no") != account_no:
                continue
            latest, latest_ts = rec.get("payload", {}).get("positions") or [], rec.get("ts")
    if latest is None:
        return None, None
    out = {}
    for p in latest:
        qty = float(p.get("openQuantity") or 0)
        if qty <= 0:
            continue
        row = out.setdefault(p.get("symbol"), {"qty": 0.0, "marketPrice": p.get("marketPrice")})
        row["qty"] += qty
    return out, latest_ts


def bq_raw_prices(tickers, date):
    """({tk: Price}, {tk: Price phiên trước}, lỗi) — cột `Price` THÔ đúng phiên --date (không
    lấy phiên cũ hơn: thiếu dòng đúng ngày ⇒ mã đó thiếu giá, main() từ chối)."""
    from verify_account_snapshot import BQ_PATH_PREFIX
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    sql = f"""
    SELECT ticker, Price, prev_price FROM (
      SELECT t.ticker, t.time, t.Price,
             LAG(t.Price) OVER (PARTITION BY t.ticker ORDER BY t.time) AS prev_price
      FROM tav2_bq.ticker AS t
      WHERE t.ticker IN ({tick_list})
        AND t.time BETWEEN DATE_SUB(DATE '{date}', INTERVAL 20 DAY) AND DATE '{date}')
    WHERE time = DATE '{date}'
    """
    env = dict(os.environ)
    env["PATH"] = BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    out = subprocess.run(["bq", "query", "--use_legacy_sql=false",
                          "--project_id=lithe-record-440915-m9", "--format=json",
                          "--max_rows=5000", sql], capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None, None, (out.stderr.strip() or out.stdout.strip())
    rows = json.loads(out.stdout)
    prices = {r["ticker"]: float(r["Price"]) for r in rows if r.get("Price") is not None}
    prev = {r["ticker"]: float(r["prev_price"]) for r in rows if r.get("prev_price") is not None}
    return prices, prev, None


def classify_raw_price_gap(ticker, date, price, prev_price, market_price, tol_pct, actions=None):
    """Giải thích lệch giữa BQ `Price` và `marketPrice` của vị thế trong dnse_raw — PURE.

    Trả ("ok", None) nếu lệch ≤ tol; ("stale_market_price", None) nếu marketPrice = giá phiên
    trước (≤RAW_PRICE_PREV_MATCH_PCT); ("early_credit", mult) nếu một corp-action CONFIRMED có
    ex_date > date và price/mult khớp marketPrice trong tol; ngược lại ("unexplained", None).
    """
    if not market_price or not price:
        return "ok", None
    if abs(price - market_price) / market_price * 100 <= tol_pct:
        return "ok", None
    if prev_price and abs(prev_price - market_price) / market_price * 100 <= RAW_PRICE_PREV_MATCH_PCT:
        return "stale_market_price", None
    if actions is None:
        actions = []
        if os.path.exists(CORP_ACTIONS_FILE):
            with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
                actions = json.load(f).get("actions") or []
    for a in actions:
        if str(a.get("ticker", "")).upper() != ticker.upper():
            continue
        if not str(a.get("_status", "")).upper().startswith("CONFIRMED"):
            continue
        if str(a.get("ex_date") or "")[:10] <= date:
            continue
        try:
            mult = float(a.get("qty_multiplier") or 1.0)
        except (TypeError, ValueError):
            continue
        if mult != 1.0 and abs(price / mult - market_price) / market_price * 100 <= tol_pct:
            return "early_credit", mult
    return "unexplained", None


def _corp_action_daily_snapshot(date):
    """corp_action_daily_<date>.json (Lớp 6, ghi bởi cron `30 0 * * 1-5` = 00:30 **UTC** =
    **07:30 ICT** SÁNG chính `date`) — dữ liệu
    CÓ THẬT lúc gate NAV chạy 19:10, khác nguồn `cum_dividend_double_count` dùng (BQ, chỉ xác
    nhận được sau khi có ít nhất 1 phiên MỚI hơn `date`). None nếu snapshot thiếu/hỏng — gọi nơi
    PHẢI coi đó là "không xác nhận được sự kiện nào", không phải "chắc chắn không có sự kiện".

    ⚠️ Đọc giờ cron này SAI rất dễ (arch-review vòng 2 đọc `30 0` thành 00:30 ICT): host chạy
    Etc/UTC, và dòng `TZ=Asia/Ho_Chi_Minh` ở đầu crontab chỉ set ENV cho script chứ KHÔNG đổi
    cách cron parse giờ — chỉ `CRON_TZ=` làm việc đó (chính crontab tự ghi chú điều này ở dòng
    vn_realestate_monthly_check). Bằng chứng trên đĩa: mọi snapshot có
    `generated_at` = <date>T07:30:01+07:00 và mtime 07:30-07:33 ICT."""
    sys.path.insert(0, MIKE_BIN)
    from corp_action_daily import snapshot_path as _ca_snapshot_path
    path = _ca_snapshot_path(date)
    if not os.path.exists(path):
        # Bình thường (cron 07:30 chưa chạy/chưa deploy ở ngày cũ) — KHÔNG phải lỗi, im lặng.
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # File CÓ TỒN TẠI nhưng đọc/parse lỗi — bất thường thật (P3/§29: nói ra bằng chứng,
        # không đoán/không nuốt). Coi như "không xác nhận được" (fail-safe, KHÔNG chặn cứng
        # toàn bộ NAV vì lỗi này — corp_action_gate_v2 chỉ MỞ RỘNG bảo vệ, chưa từng có trước
        # đây), nhưng phải VISIBLE để người vận hành biết snapshot hỏng, không âm thầm mất
        # bảo vệ nhánh 1/2 của gate.
        print(f"⚠️ [{date}] corp_action_daily snapshot ({path}) tồn tại nhưng đọc/parse lỗi "
              f"({e}) — corp_action_gate_v2 KHÔNG xác nhận được sự kiện nào hôm nay (coi như "
              f"rỗng, KHÔNG chặn NAV vì lỗi này), nhưng cần kiểm tra snapshot.", file=sys.stderr)
        return None


def held_event_next_session(snap, date, ticker):
    """Sự kiện (nếu có) của `ticker` trong `upcoming_events_held` có ex-date/effective-date
    ĐÚNG BẰNG phiên giao dịch KẾ TIẾP `date` — cửa sổ "TỐI NAY" mà corp_action_gate_v2 quan tâm
    (broker điều chỉnh đêm nay cho phiên mai). Không dùng `days_ahead` thô (cuối tuần/lễ làm
    hiệu ngày lịch khác hiệu phiên — cùng bẫy `nav_exdate_forecast.trading_day_window`)."""
    if not snap:
        return None
    sys.path.insert(0, WC_ROOT)   # module này chạy từ mike/bin, trading_bot nằm ở WC_ROOT
    from trading_bot.vn_market import next_trading_day
    nxt = next_trading_day(datetime.date.fromisoformat(date)).isoformat()
    for e in snap.get("upcoming_events_held") or []:
        if e.get("ticker") == ticker and e.get("date") == nxt:
            return e
    return None


def previous_raw_qty(account_no, ticker, date):
    """(qty, ngày dùng) của `ticker` ở bản ghi positions HỢP LỆ GẦN NHẤT trước `date` trong
    dnse_raw — bằng chứng KHỐI LƯỢNG cho NHÁNH 1 của corp_action_gate_v2 (credit sớm sự kiện
    CỔ PHIẾU), độc lập biên độ giá nên bắt được cả tỉ lệ nhỏ (~1%, giá rơi <5%, lỗ hổng L4 đã
    biết). (None, None) nếu không có bản ghi nào (mã mới, hoặc thiếu file)."""
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        d = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        if d >= date:
            continue
        pos, _ts = raw_positions(account_no, d)
        if pos:
            return (pos.get(ticker) or {}).get("qty"), d
    return None, None


def _corp_action_gate_status(snap, date):
    """(active, note) — corp_action_gate_v2 có ĐANG dựa trên lịch corp-action TIN CẬY của ĐÚNG
    `date` không. §14: cặp producer→consumer phải có freshness-check THẬT, và gate phải NÓI khi
    nó bị tắt tiếng thay vì `return None` im lặng (arch-review vòng 2, mục [5]).

    Producer CÓ fail thật — bằng chứng trên đĩa: `corp_action_daily_2026-08-27_FAILED.json`
    (01:25) tồn tại cạnh bản OK ghi sau đó; một lần fail không retry ⇒ `snapshot_path(date)`
    không có file và MỌI nhánh dựa LỊCH của gate âm thầm mất tác dụng.

    Chỉ nhánh dựa LỊCH mới chết theo. Nhánh KHỐI LƯỢNG (`classify_qty_residual`) đọc vị thế
    broker + journal fill, KHÔNG đụng file này, nên vẫn sống — note dưới đây nói đúng phần mất.
    """
    if not snap:
        return False, (f"thiếu/không đọc được corp_action_daily_{date}.json — gate KHÔNG biết mã "
                       f"nào có sự kiện tối nay (nhánh KHỐI LƯỢNG vẫn chạy; nhánh cổ tức tiền mặt "
                       f"và việc gán tỉ lệ thực hiện cho phần dư KL đều TẮT)")
    bad = []
    if snap.get("asof") != date:
        bad.append(f"asof={snap.get('asof')!r} ≠ ngày đang tính {date!r}")
    if snap.get("status") != "OK":
        bad.append(f"status={snap.get('status')!r}")
    if snap.get("usable") is not True:
        bad.append(f"usable={snap.get('usable')!r}")
    if bad:
        return False, ("snapshot corp_action_daily KHÔNG dùng được (" + "; ".join(bad) +
                       ") — nhánh KHỐI LƯỢNG vẫn chạy; nhánh cổ tức tiền mặt và việc gán tỉ lệ "
                       "thực hiện cho phần dư KL đều TẮT")
    return True, (f"corp_action_daily asof={date} status=OK usable=True "
                  f"feed_status={snap.get('feed_status')!r}")


def net_fills_between(account, after_date, upto_date, cache=None):
    """{ticker: KL RÒNG đã khớp THẬT (mua +, bán −)} cho các ngày trong khoảng (after, upto].

    ⚠️ BẪY ĐÃ ĐO LẠI (job Taylor_20260922_115410): cột `qty` của dòng FILL trong journal là
    LŨY KẾ theo `child_oid`, KHÔNG phải phần tăng thêm — cộng thẳng mọi dòng sẽ đếm trùng cú
    khớp từng phần (bug 2026-07-06 HDB). Vì vậy KHÔNG tự parse CSV ở đây mà tái dùng
    `verify_account_snapshot.journal_fill_events()` (đã giữ dòng CUỐI mỗi child_oid) — nguồn có
    thẩm quyền theo coding_guidelines §6.

    Đo thật trên 104 cặp phiên liên tiếp của CẢ 2 account (2026-08-01 → 2026-09-22): công thức
    SAI (cộng dồn) sinh 25 "phần dư"; công thức ĐÚNG còn 12, và cả 12 đều là corp-action thật
    (VHM 1:1 · MBB 15% · BID 6,8433% · VIX 5% · MSB 20% · VIB 9,5%), 0 ca nhiễu. Nói cách khác
    dùng sai công thức ⇒ chặn NAV oan ~1 lần/tuần; dùng đúng ⇒ phần dư ≠ 0 là bằng chứng sạch.
    """
    key = (account, after_date, upto_date)
    if cache is not None and key in cache:
        return cache[key]
    sys.path.insert(0, MIKE_BIN)
    from verify_account_snapshot import journal_fill_events
    prefix, suffix = f"exec_{account}_", "_journal.csv"
    out = {}
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, prefix + "*" + suffix))):
        d = os.path.basename(path)[len(prefix):-len(suffix)]
        if not (after_date < d <= upto_date):
            continue
        events, _err = journal_fill_events(account, d)
        for _ts, _oid, tk, side, qty, _px in events or []:
            out[tk] = out.get(tk, 0.0) + (qty if side == "buy" else -qty)
    if cache is not None:
        cache[key] = out
    return out


def confirmed_share_event_multiplier(ticker, date, ex_date=None, actions=None):
    """`qty_multiplier` của corp-action ĐÃ CONFIRMED trong data/corp_actions.json áp cho `ticker`
    sau `date` (và khớp đúng `ex_date` nếu truyền); None nếu không có.

    Vai trò DUY NHẤT: trả lại đường PHỤC HỒI `--from-raw` mà corp_action_gate_v2 vòng 1 khoá
    VĨNH VIỄN (killer objection, arch-review vòng 2). Chênh lệch KL `qty_now ≠ qty_prev` KHÔNG
    BAO GIỜ tự biến mất, nên gate chặn theo bằng chứng đó ở CẢ chế độ --from-raw ⇒ mọi lần
    backfill về sau vẫn rc=5, mất VĨNH VIỄN dòng nav_history của ngày credit sớm (~1 lỗ/tuần —
    đo thật 12 sự kiện/104 cặp phiên; nav_history là nguồn DUY NHẤT của §31/WTD/MTD/since-inception).

    Đường tự lành CŨ (đã chạy thật 2026-09-09): gate 19:10 trả rc=4 → `corp_action_auto_confirm.py`
    (cron 19:25) ghi CONFIRMED + qty_multiplier=1.095 cho VIB → `--from-raw` quy ngược KL.

    Mô hình TIN CẬY KHÔNG ĐỔI: `_status` chỉ thành CONFIRMED qua corp_action_auto_confirm.py
    (2 nguồn độc lập) hoặc người ký. Chế độ LIVE (không --from-raw) vẫn CHẶN — tự quy đổi ngược
    KL ở LIVE nằm NGOÀI phạm vi user đã duyệt.
    """
    if actions is None:
        if not os.path.exists(CORP_ACTIONS_FILE):
            return None
        with open(CORP_ACTIONS_FILE, encoding="utf-8") as f:
            actions = json.load(f).get("actions") or []
    for a in actions:
        if str(a.get("ticker", "")).upper() != ticker.upper():
            continue
        if not str(a.get("_status", "")).upper().startswith("CONFIRMED"):
            continue
        a_ex = str(a.get("ex_date") or "")[:10]
        if not a_ex or a_ex <= date:
            continue
        if ex_date and a_ex != str(ex_date)[:10]:
            continue
        try:
            mult = float(a.get("qty_multiplier") or 1.0)
        except (TypeError, ValueError):
            continue
        if mult != 1.0:
            return mult
    return None


QTY_RESIDUAL_EPS = 1e-6
QTY_RATIO_TOL_SHARES = 1.0   # broker làm tròn cổ phiếu lẻ: VIB 500 × 0,095 = 47,5 → credit 47
QTY_RATIO_TOL_PCT = 0.02     # + biên 2% cho lô lớn: BID 1.100 × 0,068433 = 75,28 → credit 75


def classify_qty_residual(ev, qty_now, qty_prev, net_fill, prev_date):
    """PURE. KHỐI LƯỢNG một mã đổi bao nhiêu mà LỆNH KHỚP THẬT không giải thích được.

    §29 — hàm này tồn tại để thông điệp của gate khẳng định nguyên nhân bằng bằng chứng CODE ĐÃ
    ĐỌC, không phải một nguyên nhân viết cứng sẵn. Bản vòng 1 chỉ kiểm `qty_now != qty_prev` rồi
    in "Sự kiện CỔ PHIẾU đã CREDIT SỚM THẬT": mua/bán chính mã đó đúng phiên cum là đủ để câu đó
    SAI và sinh rc=5 GIẢ — trong khi journal FILL đã nằm sẵn trong scope của main().

      "ok"                  — KL không đổi, hoặc đổi ĐÚNG BẰNG khối lượng đã khớp thật.
      "share_event_credit"  — phần dư khớp ĐÚNG tỉ lệ thực hiện của sự kiện CỔ PHIẾU tối nay;
                              CHỈ nhánh này mới được nói "broker đã credit sớm".
      "qty_unexplained"     — KL đổi, không do lệnh khớp, không khớp tỉ lệ nào ⇒ nói thẳng "chưa
                              giải thích được". Đây cũng là chỗ đóng gap D (KL đổi thật nhưng
                              LỊCH thiếu/sai sự kiện) — trước đây rơi vào nhánh giá, không ai chặn.

    `exercise_ratio` CHỈ dùng cho sự kiện CỔ PHIẾU. Sự kiện DIV cũng mang `exercise_ratio` nhưng
    đó là tỉ lệ cổ tức trên MỆNH GIÁ (DRI 2026-09-22: 0.1 = 1.000đ/10.000đ), không phải tỉ lệ cổ
    phiếu — dùng nhầm sẽ "giải thích" khống một cú đổi KL 10%.

    qty_prev=None (mã mới mua, hoặc thiếu file ngày trước) ⇒ "ok": KHÔNG có cơ sở so sánh thì
    KHÔNG chặn (fail-open có chủ đích — gate này chỉ MỞ RỘNG bảo vệ, chưa từng có trước đây).
    """
    if qty_prev is None or qty_now is None:
        return "ok", None
    delta = qty_now - qty_prev
    resid = delta - (net_fill or 0.0)
    if abs(resid) <= QTY_RESIDUAL_EPS:
        return "ok", None
    detail = {"qty_prev": qty_prev, "qty_now": qty_now, "qty_delta": delta,
              "net_fill": net_fill or 0.0, "residual": resid, "prev_qty_date": prev_date,
              "ex_date": (ev or {}).get("date"), "event_code": (ev or {}).get("event_code")}
    is_share_event = bool(ev and ev.get("price_adjusting") and ev.get("event_code") != "DIV")
    ratio = None
    if is_share_event and ev.get("exercise_ratio") is not None:
        try:
            ratio = float(ev["exercise_ratio"])
        except (TypeError, ValueError):
            ratio = None
    if ratio:
        expected = qty_prev * ratio
        detail.update({"exercise_ratio": ratio, "expected_residual": expected})
        if abs(resid - expected) <= max(QTY_RATIO_TOL_SHARES, abs(expected) * QTY_RATIO_TOL_PCT):
            detail["evidence"] = "residual_matches_exercise_ratio"
            return "share_event_credit", detail
    detail["evidence"] = "residual_not_explained_by_fills_or_ratio"
    return "qty_unexplained", detail


def _write_json_atomic(path, obj):
    """tmp + os.replace — cùng pattern `_write_nav_history` (§5): kill giữa chừng không được để
    lại file JSON dở dang cho reader tin."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


CASH_DIV_PRICE_TOL_VND = 200  # dung sai so khớp "mkt_price ≈ price_ref − value_per_share" —
# rộng hơn 1 bước giá thường gặp (50-100đ dải 10k-50k) vì broker có thể tự làm tròn/refresh
# giá tham chiếu qua nhiều bước trong đêm (đo thật DRI 2026-09-21: 14.800→13.800→13.700, 2 bước).


def classify_corp_action_gap(ev, qty_now, qty_prev, price_ref, mkt_price, tol_pct,
                             cum_div_amount, cum_div_tickers, cum_div_warnings):
    """Phân loại lệch giá/KL của MỘT mã đang giữ — THIẾT KẾ v2 (job Taylor_20260922_111128,
    thay bản feat/nav-corpaction-gate cũ BỊ arch-review bác 2 lỗi: L3 kiểm bất biến qua nguồn
    BQ không thể có dữ liệu lúc 19:10; L4 lẫn PHÁT HIỆN lịch với CHẶN giá). PURE — không đọc
    file/gọi mạng, nhận sẵn mọi input đã tính. Trả (verdict, detail):

      (Nhánh KHỐI LƯỢNG đã TÁCH sang `classify_qty_residual` ở arch-review vòng 2 — nó phải
        trừ lệnh khớp thật trước khi kết luận, và phải chạy cho MỌI mã đang giữ chứ không chỉ
        mã có sự kiện trên lịch. Hàm này giờ chỉ lo phần GIÁ.)
      "cash_div_confirmed" — NHÁNH 2: cổ tức tiền mặt, broker hạ giá tham chiếu SỚM 1 đêm
        (mkt_price ≈ price_ref − value_per_share). PASS chỉ khi bất biến "khoản cổ tức của
        CHÍNH mã này CHƯA nằm 2 lần trong tiền" được xác nhận DƯƠNG qua `cum_div_amount`/
        `cum_div_tickers` (đã tính MỘT LẦN ở main() bằng `cum_dividend_double_count`, KHÔNG
        gọi lại BQ ở đây — P2/TOCTOU). Có `cum_div_warnings` (không khẳng định được) hoặc
        amount không khớp kỳ vọng (khoản đã nằm trong tiền từ trước, delta=0) ⇒ KHÔNG confirm,
        rơi xuống "unexplained" — FAIL-CLOSED đúng yêu cầu LỖI 1.
      "unexplained" — NHÁNH 3: không khớp nhánh nào, GIỮ NGUYÊN hành vi hiện tại (rc=4, tự
        retry ngắn hạn qua nav_sync_retry.sh).
      "ok" — NHÁNH 4: không có gì bất thường (không sự kiện, hoặc lệch giá trong dung sai).
    """
    kind = None
    if ev and ev.get("price_adjusting"):
        kind = "CASH_DIV" if ev.get("event_code") == "DIV" else "SHARE_EVENT"

    if not price_ref or not mkt_price:
        return "ok", None
    diff_pct = abs(price_ref - mkt_price) / mkt_price * 100
    if diff_pct <= tol_pct:
        return "ok", None

    if kind == "CASH_DIV":
        vps_raw = ev.get("value_per_share")
        vps = float(vps_raw) if vps_raw is not None else None
        if vps is not None and abs(mkt_price - (price_ref - vps)) <= CASH_DIV_PRICE_TOL_VND \
                and qty_now is not None:
            expected = qty_now * vps
            # Hai đường xác nhận, KHÁC vai (giống cum_dividend_double_count) — cố ý KHÔNG đòi
            # `not cum_div_warnings`: warning phổ biến nhất (đo thật DRI 2026-09-21) là BQ và
            # giá trị công bố lệch ~10% (net-of-tax vs gross), KHÔNG phải sai attribution — nếu
            # đòi 0 warning tuyệt đối, chính ca acceptance test của thiết kế này sẽ KHÔNG BAO
            # GIỜ pass, tự mâu thuẫn với mục đích tồn tại của nhánh này.
            #   * in_bq_list: BQ (nguồn ĐỘC LẬP) đã tự xác nhận CHÍNH mã này có ex-date đang
            #     chờ (cum_dividend_double_count.pending) — attribution chắc chắn, bỏ qua sai
            #     số biên độ (tax/rounding).
            #   * magnitude_ok: fallback cho ca BQ CHƯA CÓ dữ liệu (live 19:10, LỖI 1) — không
            #     có attribution độc lập, nên đòi khớp SỐ TIỀN trong dung sai chặt hơn (1%).
            in_bq_list = ev.get("ticker") in (cum_div_tickers or [])
            magnitude_ok = bool(cum_div_amount) and abs(cum_div_amount - expected) <= max(10.0, expected * 0.01)
            confirmed = bool(cum_div_amount) and (in_bq_list or magnitude_ok)
            if confirmed:
                return "cash_div_confirmed", {
                    "value_per_share": vps, "expected_amount": expected,
                    "cum_div_amount": cum_div_amount, "price_ref": price_ref, "mkt_price": mkt_price}

    return "unexplained", {"price_ref": price_ref, "mkt_price": mkt_price, "diff_pct": diff_pct}


def broker_positions(account_label, account_no):
    """Vị thế THẬT từ API broker (source of truth) → {sym: {"qty": ..., "marketPrice": ...}}.

    Bug 2026-07-07 (kb/INCIDENTS.md): NAV từng lấy mtm_stock từ verify_account_snapshot.py
    — tái dựng vị thế TỪ LỊCH SỬ FILL journal. Đúng cho account clean-slate (SpaceX), nhưng
    account có vị thế legacy không có fill history (ZaloPay: DGC/VPB/VIB/VHC/TCM/TLG ~976tr)
    bị BỎ SÓT toàn bộ → EOD report đăng NAV 17,5tr (-98%) lên Trading report. Nguyên tắc:
    NAV đo TÀI SẢN THẬT → hỏi broker; journal chỉ dùng cho cost-basis/P&L attribution.

    marketPrice đi kèm để main() đối chiếu chéo với dnse_close_prices() (bug 2026-08-05: VHM
    chia thưởng cổ phiếu 1:1, vị thế broker cập nhật qty/marketPrice đúng ngay trong ngày
    nhưng close_price() G1 trả giá CŨ trước sự kiện — mtm_stock bị thổi phồng đúng bằng giá
    trị 1 vị thế, cả 2 tài khoản SpaceX/ZaloPay).
    """
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import DNSEBroker
    try:
        b = DNSEBroker(account_id=account_no, quote_only=False, label=account_label)
        b.connect()
        pos = b.get_positions()
        # Side effect CÓ CHỦ ĐÍCH: get_cash() ghi 1 bản ghi "balances" TƯƠI (kèm account
        # tag) vào dnse_raw hôm nay — ngày HOLD bot không chạy lệnh nào nên không có bản
        # ghi balance, latest_balance() sẽ không có gì để đọc nếu thiếu bước này.
        try:
            b.get_cash()
        except Exception:
            pass
        return {sym: {"qty": p["total"], "marketPrice": p.get("marketPrice")}
                for sym, p in pos.items() if p.get("total", 0) > 0}
    except Exception as e:
        print(f"⚠️ Không đọc được positions broker ({account_label}): {e}", file=sys.stderr)
        return None


def latest_balance(raw_path, account_no=None):
    """Bản ghi 'balances' MỚI NHẤT cho ĐÚNG account_no trong file dnse_raw_{date}.jsonl.

    Bug 2026-07-06 (kb/INCIDENTS.md): file này dùng CHUNG cho MỌI account cùng ngày (tên
    file chỉ theo ngày, không theo account) — trước khi ZaloPay go-live cùng ngày với
    SpaceX, chỉ 1 account nên không lộ. Khi 2 account cùng gọi balances() trong 1 ngày,
    bản ghi xen kẽ — lấy "bản ghi cuối cùng" mù quáng có thể lấy NHẦM account, gây báo NAV
    sai (SpaceX báo 688.5tr thay vì 983.0tr thật do lẫn balance của ZaloPay). Field
    account_no được _log_raw() ghi thêm từ 2026-07-06 (trading_bot/brokers.py); bản ghi cũ
    hơn không có field này — nếu account_no được truyền vào mà không lọc được gì, RAISE rõ
    ràng thay vì âm thầm dùng bản ghi có thể sai account.
    """
    if not os.path.exists(raw_path):
        return None
    latest = None
    seen_other_account = False
    with open(raw_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("kind") != "balances":
                continue
            if account_no is not None and rec.get("account_no") not in (None, account_no):
                seen_other_account = True
                continue
            latest = rec
    if latest is None and seen_other_account:
        raise RuntimeError(
            f"dnse_raw file có bản ghi balances nhưng KHÔNG bản nào khớp account_no="
            f"{account_no!r} — file này dùng chung cho nhiều account, tránh dùng nhầm.")
    return latest


def _stock_all_zero(stock):
    """Khối `stock` TOÀN SỐ 0 = lỗi API tạm thời của DNSE (xem invariant trong main())."""
    nums = [v for v in stock.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    return bool(nums) and not any(nums)


def previous_balance(account_no, date):
    """Bản ghi 'balances' hợp lệ MỚI NHẤT của account, ở phiên TRƯỚC `date`.

    Dùng để đo mức TĂNG của `cashDividendReceiving` trong ngày (xem
    cum_dividend_double_count). Bỏ qua bản ghi toàn-số-0 vì nó tạo ra một cú sụt rồi bật
    giả trong chuỗi và làm hỏng phép so delta.
    """
    for path in sorted(glob.glob(os.path.join(EXEC_DIR, "dnse_raw_*.jsonl")), reverse=True):
        d = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
        if d >= date:
            continue
        latest = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("kind") != "balances":
                    continue
                if account_no is not None and rec.get("account_no") not in (None, account_no):
                    continue
                if _stock_all_zero(rec.get("payload", {}).get("stock") or {}):
                    continue
                latest = rec
        if latest is not None:
            return latest
    return None


# Thị trường đóng 14:45 ICT; DNSE ghi khoản cổ tức phải thu trong đợt xử lý sau phiên. Bản ghi
# balance từ 16:00 trở đi coi là "cuối ngày" — đủ muộn để đã thấy đợt xử lý đó.
CUM_DIV_EOD_HHMM = "16:00"


def cum_dividend_double_count(account_no, date, positions, cur_bal, prev_bal,
                              events=None, bq_max_date=None):
    """Cổ tức tiền mặt ĐÃ nằm trong `totalCash` nhưng giá cổ phiếu CHƯA rơi ex-date.

    BUG GỐC (báo cáo tuần 27–31/07/2026 Mục 11.5, 5 dòng NAV lịch sử sai): DNSE ghi khoản
    `cashDividendReceiving` vào số dư ngay TỐI NGÀY CUỐI CÙNG CÒN HƯỞNG QUYỀN (last-cum-date),
    trong khi giá đóng cửa phiên đó VẪN CÒN bao gồm quyền nhận cổ tức. NAV cuối ngày =
    cổ phiếu (giá cum) + tiền (đã gồm khoản phải thu) → ĐẾM 2 LẦN cùng một khoản cổ tức, tự
    triệt tiêu ở phiên kế tiếp khi giá rơi về mức không hưởng quyền. NAV tổng cuối tháng vẫn
    đúng, nên mọi phép đối soát NAV đều PASS — đó là lý do lỗi sống sót (xem coding_guidelines §21).

    HAI ĐƯỜNG XÁC ĐỊNH, cố ý tách vai:
      * SỐ TIỀN phải trừ = mức TĂNG thật của `cashDividendReceiving` so với bản ghi balance
        hợp lệ cuối cùng của phiên trước. Chỉ số này mới biết chắc "bao nhiêu tiền đang thực
        sự nằm trong totalCash" (chia tách cổ phiếu không sinh tiền → delta = 0, tự loại).
      * TÍNH HỢP LỆ (có đúng là chưa qua ex-date không) = tỉ số Close/Price trong BQ
        (`dividend_adjusted_return.detect_adjustments_batch`) — nguồn có thẩm quyền về ex-date.
        NHƯNG cú nhảy tỉ số chỉ lộ ra ĐÚNG Ở phiên ex, nên chạy live lúc 19:10 (BQ mới sync
        tới hôm qua) sẽ KHÔNG thấy gì. Vì vậy khi BQ chưa có phiên nào sau `date`, ta lùi về
        quy tắc thời điểm: bản ghi phiên trước là bản CUỐI NGÀY (≥16:00) ⇒ khoản tăng chắc
        chắn mới được ghi tối nay ⇒ ex-date là phiên sau ⇒ trừ.

    Ca thật minh hoạ vì sao cần cả hai (SpaceX 09/07/2026, MBB): khoản 2.400.000đ lần đầu
    QUAN SÁT được lúc 09/07 15:00 nhưng ex-date đúng là 09/07 (giá đã rơi) — bản ghi phiên
    trước lại là bản GIỮA PHIÊN (08/07 15:00), không kết luận được bằng thời điểm. BQ (lịch
    sử) trả lời dứt khoát: không còn ex-date nào phía sau 09/07 ⇒ KHÔNG trừ. Đúng.

    Trả về dict (đưa nguyên vào JSON snapshot để truy vết được về sau).
    """
    res = {"amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [],
           "bq_max_date": bq_max_date, "note": "", "warnings": []}
    cur_cd = float((cur_bal.get("payload", {}).get("stock") or {}).get("cashDividendReceiving") or 0)
    if prev_bal is None:
        if cur_cd:
            res["warnings"].append(
                f"Không có bản ghi balances hợp lệ nào ở phiên trước {date} — KHÔNG kiểm được "
                f"cổ tức phải thu ({cur_cd:,.0f}đ) có bị đếm 2 lần hay không.")
        return res
    prev_cd = float((prev_bal.get("payload", {}).get("stock") or {}).get("cashDividendReceiving") or 0)
    res["delta"] = cur_cd - prev_cd
    if res["delta"] <= 0:
        return res

    if events is None and positions:
        try:
            sys.path.insert(0, MIKE_BIN)
            from dividend_adjusted_return import detect_adjustments_batch
            d0 = datetime.date.fromisoformat(date)
            events, bq_max_date = detect_adjustments_batch(
                sorted(positions), (d0 - datetime.timedelta(days=15)).isoformat(),
                (d0 + datetime.timedelta(days=15)).isoformat())
            res["bq_max_date"] = bq_max_date
        except Exception as e:  # BQ hỏng/không với tới được → vẫn còn quy tắc thời điểm
            res["warnings"].append(f"Không tra được ex-date từ BigQuery ({e}) — chỉ dựa vào "
                                   f"thời điểm bản ghi balance.")
            events = None

    pending = [a for tk, advs in (events or {}).items() if tk in positions
               for a in advs if a.last_cum_date <= date < a.ex_date]
    # BQ chỉ KẾT LUẬN ĐƯỢC khi đã có ít nhất 1 phiên sau `date` (ex-date lộ ra ở phiên ex).
    if events is not None and bq_max_date and bq_max_date > date and not pending:
        res["note"] = (f"cashDividendReceiving tăng {res['delta']:,.0f}đ nhưng BQ (dữ liệu tới "
                       f"{bq_max_date}) xác nhận không mã nào còn ex-date sau {date} — khoản này "
                       f"ĐÃ qua ex-date, không trừ.")
        return res

    prev_ts = prev_bal.get("ts", "")
    prev_is_eod = len(prev_ts) >= 16 and prev_ts[11:16] >= CUM_DIV_EOD_HHMM
    if not pending and not prev_is_eod:
        res["warnings"].append(
            f"cashDividendReceiving tăng {res['delta']:,.0f}đ nhưng KHÔNG kết luận được đã qua "
            f"ex-date hay chưa: BQ chưa có phiên sau {date} và bản ghi balance phiên trước "
            f"({prev_ts or '?'}) là bản GIỮA PHIÊN. KHÔNG tự trừ — cần người đối chiếu.")
        return res

    res["amount"] = res["delta"]
    res["tickers"] = sorted({a.ticker for a in pending})
    if pending:
        # main() truyền {mã: {"qty", "marketPrice"}} (từ 2026-08-05), selfcheck truyền {mã: qty} —
        # bản cũ nhân thẳng dict × float ⇒ TypeError ngay khi `pending` khác rỗng (lộ ra lúc
        # backfill 22/07, aria-A2; đường live 19:10 hiếm khi có pending nên chưa từng nổ).
        def _qty(v):
            return float(v.get("qty") or 0) if isinstance(v, dict) else float(v or 0)
        res["expected_bq"] = sum(_qty(positions.get(a.ticker, 0)) * a.per_share for a in pending)
        tol = max(10.0, res["delta"] * 0.005)
        if abs(res["expected_bq"] - res["delta"]) > tol:
            res["warnings"].append(
                f"Cổ tức chờ theo BQ ({res['expected_bq']:,.0f}đ cho {res['tickers']}) LỆCH so với "
                f"mức tăng thật của cashDividendReceiving ({res['delta']:,.0f}đ) — trừ theo số "
                f"tiền thật trong tài khoản, nhưng cần người kiểm tra nguyên nhân lệch.")
        res["note"] = (f"Trừ {res['amount']:,.0f}đ cổ tức phải thu của {', '.join(res['tickers'])} "
                       f"(ex-date {sorted({a.ex_date for a in pending})[0]}) — giá đóng cửa {date} "
                       f"vẫn CÒN quyền, cộng vào tiền nữa là đếm 2 lần.")
    else:
        res["note"] = (f"Trừ {res['amount']:,.0f}đ cổ tức phải thu vừa ghi nhận tối {date} "
                       f"(bản ghi phiên trước {prev_ts} là bản cuối ngày ⇒ ex-date là phiên sau; "
                       f"BQ chưa có dữ liệu sau {date} để xác nhận mã cụ thể).")
    return res


def load_history(account):
    path = HISTORY_FILE_TMPL.format(account=account)
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    return path, rows


def _write_nav_history(hist_path, hist_rows, fieldnames):
    """Atomic write (tmp + os.replace) — cùng pattern executor.py _save_state (review
    vòng 2 2026-07-02, kb/coding_guidelines.md §5): nav_history là nguồn duy nhất mọi
    báo cáo ngày/tuần/tháng dùng chung, kill mid-write không được để lại file truncate
    dở dang (đã xảy ra 2026-07-06: mất 2 dòng lịch sử). os.replace = rename nguyên tử
    trên POSIX — reader luôn thấy hoặc file cũ hoặc file mới, không bao giờ file dở.

    extrasaction="ignore": lịch sử cũ có thể mang field từ version trước của script
    (vd cột đã bỏ) — không để 1 dòng cũ làm hỏng cả file.
    """
    tmp = hist_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: row.get(k, "") for k in fieldnames} for row in hist_rows)
    os.replace(tmp, hist_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None)
    ap.add_argument("--date", required=True)
    ap.add_argument("--starting-capital", type=float, default=1_000_000_000)
    ap.add_argument("--from-raw", action="store_true",
                    help="backfill ngày QUÁ KHỨ chỉ từ dnse_raw_{date}.jsonl (positions+balances cuối "
                         "ngày) + BQ Price thô, không gọi broker; ghi nav_is_estimate=True")
    args = ap.parse_args()

    # account_no: dùng --account-no nếu có, else tự tra secrets/trading_bot_accounts.json
    # theo label — tránh phải nhớ truyền tay mỗi lần gọi (và là điều kiện BẮT BUỘC để lọc
    # đúng account trong dnse_raw_{date}.jsonl dùng chung, xem latest_balance()).
    account_no = args.account_no
    sys.path.insert(0, WC_ROOT)
    from trading_bot.config import load_config, load_accounts
    _profiles = load_accounts(load_config())
    _match = next((p for p in _profiles if p["label"] == args.account), None)
    if not account_no:
        account_no = _match.get("account_id") if _match else None
    # Tài sản off-book (vd "Trứng vàng" DNSE — không lộ qua OpenAPI, xem
    # trading_bot/config.py ACCOUNT_DEFAULTS): user tự báo, Mike cập nhật config khi thay
    # đổi. Cộng vào NAV THẬT (không cộng vào 'cash' — cash vẫn phải là sức mua thực sự khả
    # dụng ở tài khoản môi giới), tránh NAV báo THẤP hơn thực tế sau khi user chuyển tiền
    # sang sản phẩm này, và tránh sanity-guard bên dưới chặn oan 1 ngày biến động lớn do
    # chuyển tiền thật (không phải lỗi dữ liệu).
    offbook = float((_match or {}).get("manual_offbook_assets_vnd") or 0)
    offbook_note = (_match or {}).get("manual_offbook_assets_note") or ""
    offbook_asof = (_match or {}).get("manual_offbook_assets_asof") or ""
    # Staleness WARN (quant-skeptic review 2026-07-17): số off-book là user tự báo, KHÔNG có
    # API xác nhận lại — nếu asof quá cũ, cảnh báo thay vì âm thầm tin mãi 1 con số có thể đã
    # đổi (user rút bớt/rút hết mà quên báo, hoặc Mike quên cập nhật config).
    offbook_stale_warning = None
    if offbook and offbook_asof:
        import datetime as _dt_stale
        try:
            age_days = (_dt_stale.date.fromisoformat(args.date)
                        - _dt_stale.date.fromisoformat(offbook_asof)).days
            if age_days > 21:
                offbook_stale_warning = (
                    f"manual_offbook_assets_asof ({offbook_asof}) đã {age_days} ngày — xác nhận "
                    f"lại số dư Trứng vàng/off-book với user trước khi tin tưởng hoàn toàn.")
        except ValueError:
            pass

    dates = trading_dates_with_fills(args.account, args.date)
    if not dates:
        print(f"ℹ️ [{args.date}] Chưa có ngày giao dịch nào cho {args.account} — bỏ qua NAV snapshot.")
        return 0

    # verify_account_snapshot: giờ chỉ là CROSS-CHECK advisory (cost-basis/đối soát journal)
    # — NAV không còn phụ thuộc nó (xem docstring broker_positions về bug 2026-07-07).
    import datetime as _dt
    today_iso = _dt.date.today().isoformat()   # TZ đã ép Asia/Ho_Chi_Minh ở đầu module
    is_today = args.date == today_iso
    if args.from_raw and args.date >= today_iso:
        print(f"❌ [{args.date}] --from-raw chỉ dành cho ngày QUÁ KHỨ — hôm nay dùng đường live.",
              file=sys.stderr)
        return 2

    verify_warning = None
    if args.from_raw:
        # verify_account_snapshot chỉ là cross-check advisory và dùng BQ `Close` điều chỉnh —
        # chạy lại cho ngày cũ vừa sai giá vừa ghi đè file của ngày đó. Bỏ qua có chủ đích.
        verify_warning = "from-raw: bỏ cross-check verify_account_snapshot (advisory, không vào NAV)."
    else:
        snapshot_out = os.path.join(EXEC_DIR, f"verified_snapshot_{args.account}_{args.date}.json")
        cmd = [sys.executable, os.path.join(MIKE_BIN, "verify_account_snapshot.py"),
               "--account", args.account, "--dates", ",".join(dates), "--asof", args.date,
               "--out", snapshot_out]
        if account_no:
            cmd += ["--account-no", account_no]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode not in (0,):
            verify_warning = (f"verify_account_snapshot (cross-check journal) rc={r.returncode} — "
                              f"NAV vẫn tính từ vị thế broker thật; cần xem cost-basis/đối soát riêng.")

    # ── mtm_stock = vị thế BROKER THẬT × giá đóng cửa verified ──
    positions_ts = None
    if args.from_raw:
        positions, positions_ts = raw_positions(account_no, args.date)
    else:
        positions = broker_positions(args.account, account_no)
    if not positions:
        print(f"❌ [{args.date}] Không lấy được vị thế broker"
              f"{' (không có bản ghi positions của account trong dnse_raw ngày này)' if args.from_raw else ''}"
              f" — KHÔNG tính NAV (tránh đăng số thiếu vị thế).", file=sys.stderr)
        return 2
    sys.path.insert(0, MIKE_BIN)
    from verify_account_snapshot import dnse_close_prices, bq_close_prices
    tickers = sorted(positions)

    # Quy đổi NGƯỢC vị thế broker LIVE về đúng --date lịch sử cho các mã đã dính corp-action
    # CONFIRMED có ex_date SAU --date (xem docstring confirmed_qty_multiplier_after — bug
    # 2026-09-10: VIB bonus issue credit sớm 1 phiên trước ex_date). Không áp khi is_today vì
    # khi đó vị thế LIVE đúng là vị thế thật của chính args.date, không cần quy đổi.
    corp_action_adj = {}
    if not is_today and not args.from_raw:   # vị thế raw là của CHÍNH --date, xem xcheck from-raw
        for t in tickers:
            mult = confirmed_qty_multiplier_after(t, args.date)
            if mult != 1.0:
                corp_action_adj[t] = mult
                positions[t]["qty"] = positions[t]["qty"] / mult

    prev_prices = {}
    if is_today:
        prices = dnse_close_prices(tickers)
    elif args.from_raw:
        prices, prev_prices, _perr = bq_raw_prices(tickers, args.date)
        if prices is None:
            print(f"❌ [{args.date}] Không lấy được giá BQ Price: {_perr}", file=sys.stderr)
            return 2
    else:
        prices, _perr = bq_close_prices(tickers, args.date)
        prices = prices or {}
    missing = [t for t in tickers if t not in prices]
    if missing:
        print(f"❌ [{args.date}] Thiếu giá đóng cửa verified cho {missing} — KHÔNG tính NAV "
              f"(không đoán giá).", file=sys.stderr)
        return 2

    # ── Balance/cash/cum_div: tính TRƯỚC gate giá (P2, arch-review 2026-09-22) — corp_action_gate_v2
    # nhánh CASH_DIV cần `cum_div` để xác nhận bất biến "khoản cổ tức của mã này chưa nằm 2 lần
    # trong tiền" TRƯỚC KHI quyết định có nới gate hay không; tính lại BQ lần 2 ở dưới (như bản
    # cũ) là đúng lỗi TOCTOU arch-review đã bắt (đường khác dẫn về đúng lỗi v1, coding_guidelines
    # §14/§28) — một khi lần tính THỨ NHẤT nới gate mà lần THỨ HAI lỗi/lệch, NAV có thể thiếu
    # khoản trừ mà không ai biết. Tính DUY NHẤT MỘT LẦN, dùng lại ở cả hai nơi.
    raw_path = os.path.join(EXEC_DIR, f"dnse_raw_{args.date}.jsonl")
    try:
        bal = latest_balance(raw_path, account_no=account_no)
    except RuntimeError as e:
        print(f"⚠️ [{args.date}] {e}", file=sys.stderr)
        return 2
    if bal is None:
        print(f"⚠️ [{args.date}] Không có record balances thật trong {raw_path} — "
              f"KHÔNG tính NAV (tránh dùng số ước tính/cũ).", file=sys.stderr)
        return 2

    stock = bal["payload"]["stock"]

    # INVARIANT (bug 2026-07-27, Taylor phát hiện qua báo cáo tuần 07-27→07-31): DNSE có lúc
    # trả về block `stock` TOÀN SỐ 0 (cả totalCash/availableCash/depositInterest/
    # depositFeeAmount/cashDividendReceiving = 0) — đó là API lỗi tạm thời, KHÔNG phải tiền
    # mặt thật về 0. Ngày 27/07 cả 2 lần đọc 19:04:59 và 19:10:20 đều toàn 0, script cũ nhận
    # số 0 đó và ghi NAV=804.077.200 (thiếu đúng 32.011.420đ tiền mặt = -3,83% NAV), làm
    # thổi phồng vol năm hoá 26,5%→37,7% và MaxDD -16,12%→-19,33% trong báo cáo tuần.
    # Tài khoản live có cổ phiếu thì depositInterest/depositFeeAmount gần như không bao giờ
    # đồng loạt bằng 0 → toàn-0 = dấu hiệu lỗi feed rõ ràng. FAIL-SAFE: từ chối ghi, KHÔNG
    # tự đoán số đúng (người chạy lại script/lấy bản đọc tươi hôm sau mới là nguồn thật).
    if _stock_all_zero(stock):
        print(f"❌ [{args.date}] Balance record ({bal.get('ts')}) trả về TOÀN SỐ 0 "
              f"(totalCash=0, totalDebt=0, và mọi field số khác =0) — đây là lỗi API tạm "
              f"thời của DNSE, KHÔNG phải NAV thật về 0. KHÔNG tính NAV để tránh ghi số sai "
              f"vào nav_history. Chạy lại script để lấy bản đọc balance tươi; nếu cuối ngày "
              f"vẫn toàn 0, lấy bản đọc đầu phiên hôm sau (TRƯỚC cú khớp đầu tiên) và điền "
              f"tay sau khi đối chiếu.", file=sys.stderr)
        return 2

    cash, debt = stock["totalCash"], stock["totalDebt"]
    # Trứng vàng — từ 2026-08-18, DNSE expose qua API (field egg.totalValue trong balances).
    # Đọc tự động từ bản ghi log, không cần user báo tay nữa. manual_offbook_assets_vnd vẫn
    # dùng cho tài sản off-book KHÁC egg (nếu có trong tương lai).
    egg_value = float((bal.get("payload", {}).get("egg") or {}).get("totalValue") or 0)

    # INVARIANT (bug 2026-07-07 lần 2, user chỉ ra): bản ghi balance phải MỚI HƠN cú khớp
    # CUỐI CÙNG trong ngày — ngày vừa mua vừa bán, DNSE cập nhật tiền theo TỪNG khớp
    # (mua khớp T0: totalCash → secureAmount trong vòng vài phút), snapshot chụp GIỮA
    # 2 cú khớp sẽ lệch đúng bằng giá trị lệnh sau (ZaloPay: balance 13:00:02 vs VCB khớp
    # 13:00:22 → NAV thừa 6,1tr vì cổ phiếu đã đếm VCB mà tiền chưa trừ).
    jpath = os.path.join(EXEC_DIR, f"exec_{args.account}_{args.date}_journal.csv")
    last_fill_ts = ""
    if os.path.exists(jpath):
        with open(jpath, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("event") == "FILL" and row.get("ts", "") > last_fill_ts:
                    last_fill_ts = row["ts"]
    if args.from_raw and last_fill_ts and (positions_ts or "") <= last_fill_ts:
        print(f"❌ [{args.date}] Bản ghi positions trong dnse_raw ({positions_ts}) CŨ HƠN cú khớp "
              f"cuối cùng ({last_fill_ts}) — vị thế chưa phản ánh đủ lệnh, KHÔNG backfill.",
              file=sys.stderr)
        return 2
    if last_fill_ts and bal.get("ts", "") <= last_fill_ts:
        print(f"❌ [{args.date}] Balance record ({bal.get('ts')}) CŨ HƠN cú khớp cuối cùng "
              f"({last_fill_ts}) — tiền chưa phản ánh đủ lệnh đã khớp, KHÔNG tính NAV. "
              f"Chạy lại script (nó tự đọc balance tươi qua broker_positions/get_cash).",
              file=sys.stderr)
        return 2

    # ── Cổ tức phải thu ghi TRƯỚC ex-date: loại ra khỏi tiền để không đếm 2 lần ──
    # (bug 2026-08-02, coding_guidelines §21 — xem docstring cum_dividend_double_count)
    cum_div = cum_dividend_double_count(account_no, args.date, positions, bal,
                                        previous_balance(account_no, args.date))
    cash_broker = cash
    cash -= cum_div["amount"]

    # ── Đối chiếu chéo close_price(G1) vs marketPrice của CHÍNH vị thế broker (bug
    # 2026-08-05: VHM chia thưởng cổ phiếu 1:1, qty/marketPrice của vị thế cập nhật đúng
    # ngay trong ngày nhưng close_price() G1 vẫn trả giá TRƯỚC sự kiện — mtm_stock bị thổi
    # phồng đúng bằng giá trị 1 vị thế, cả SpaceX lẫn ZaloPay). Chỉ đối chiếu được khi
    # is_today (marketPrice của vị thế broker luôn là ảnh chụp HIỆN TẠI, vô nghĩa với
    # --date lịch sử). Lệch >PRICE_XCHECK_TOLERANCE_PCT gần như chắc chắn hoặc (a) corporate
    # action broker chưa đồng bộ hết mọi nguồn giá, hoặc (b) field marketPrice của vị thế
    # tự đồng bộ TRỄ hơn close_price ở EOD (ca PVT 2026-09-08: broker cập nhật marketPrice
    # trễ ~65' sau giờ đóng cửa, không phải corp-action) — script này không phân biệt được
    # 2 trường hợp, nên vẫn fail-safe từ chối cả hai, không đoán giá nào đúng hơn. rc=4
    # (khác rc=2 "thiếu dữ liệu") để caller (`nav_sync_retry.sh`) biết đây là case ĐÁNG
    # RETRY tự động trong 1 cửa sổ ngắn, thay vì escalate ngay như (a).
    #
    # v2 + arch-review vòng 2 (job Taylor_20260922_115410). Gate soi MỖI mã đang giữ qua HAI
    # trục ĐỘC LẬP, trước khi rơi vào "unexplained"/rc=4:
    #   • KHỐI LƯỢNG (`classify_qty_residual`) — chạy cho MỌI mã, KHÔNG cần lịch: phần KL đổi
    #     mà lệnh khớp thật không giải thích được. Đây là trục bắt được cả sự kiện tỉ lệ nhỏ
    #     (~1%, giá rơi <5%, lỗ hổng L4 cũ) LẪN ca "KL đổi thật nhưng LỊCH thiếu/sai sự kiện"
    #     (gap D) — trước đây rơi vào nhánh giá và KHÔNG ai chặn.
    #   • LỊCH (`corp_action_daily_<date>.json`, cron `30 0` UTC = 07:30 ICT chính `date`) — dữ liệu CÓ THẬT
    #     lúc gate chạy 19:10, khác bản cũ bị bác vì chờ BQ xác nhận phiên hôm nay (luôn rỗng).
    #     Lịch chỉ dùng để GIẢI THÍCH phần dư (gán tỉ lệ thực hiện) và cho nhánh cổ tức tiền mặt;
    #     mất lịch KHÔNG làm mất bảo vệ trục khối lượng (xem `_corp_action_gate_status`).
    ca_snap = _corp_action_daily_snapshot(args.date)
    ca_gate_active, ca_gate_note = _corp_action_gate_status(ca_snap, args.date)
    if not ca_gate_active:
        print(f"⚠️ [{args.date}] corp_action_gate_v2 KHÔNG xác nhận được lịch corp-action: "
              f"{ca_gate_note}.", file=sys.stderr)
    share_event_blocks = []      # phần dư KHỚP tỉ lệ sự kiện ⇒ credit sớm ĐÃ CHỨNG MINH
    qty_unexplained = []         # phần dư KHÔNG khớp gì ⇒ nói thẳng "chưa giải thích được"
    cash_div_confirmed = {}
    corp_action_recovered = {}   # --from-raw + corp-action ĐÃ CONFIRMED ⇒ quy ngược KL như cũ
    fill_cache = {}
    if args.from_raw or is_today:
        for t in tickers:
            ev = held_event_next_session(ca_snap, args.date, t)
            qty_now = (positions[t] or {}).get("qty")
            qty_prev, prev_d = previous_raw_qty(account_no, t, args.date)
            net_fill = (net_fills_between(args.account, prev_d, args.date, fill_cache).get(t)
                        if prev_d else None)
            qverdict, qdetail = classify_qty_residual(ev, qty_now, qty_prev, net_fill, prev_d)
            if qverdict != "ok":
                mult = confirmed_share_event_multiplier(t, args.date, (ev or {}).get("date"))
                if args.from_raw and mult:
                    # ĐƯỜNG PHỤC HỒI (mục [1] arch-review vòng 2) — KHÔI PHỤC hành vi CŨ, không
                    # phải tính năng mới: quy ngược KL về trước sự kiện đúng như vòng lặp
                    # `confirmed_qty_multiplier_after` ở trên vẫn làm cho ngày lịch sử. Cố ý
                    # KHÔNG phó mặc cho `classify_raw_price_gap`/early_credit như bản vòng 1 gợi
                    # ý: nhánh đó chỉ bật khi lệch giá > PRICE_XCHECK_TOLERANCE_PCT, nên sự kiện
                    # tỉ lệ nhỏ sẽ lọt — đúng lỗ hổng L4 mà gate này sinh ra để đóng.
                    corp_action_recovered[t] = dict(qdetail, qty_multiplier=mult)
                    corp_action_adj[t] = mult
                    positions[t]["qty"] = qty_now / mult
                elif qverdict == "share_event_credit":
                    share_event_blocks.append((t, qdetail))
                else:
                    qty_unexplained.append((t, qdetail))
            if ev:
                verdict, detail = classify_corp_action_gap(
                    ev, qty_now, qty_prev, prices.get(t), (positions[t] or {}).get("marketPrice"),
                    5.0, cum_div["amount"], cum_div["tickers"], cum_div["warnings"])
                if verdict == "cash_div_confirmed":
                    cash_div_confirmed[t] = detail
    for t, d in sorted(corp_action_recovered.items()):
        print(f"ℹ️ [{args.date}] {t}: KL {d['qty_prev']:,.0f}→{d['qty_now']:,.0f} (lệnh khớp "
              f"{d['net_fill']:+,.0f}, phần dư {d['residual']:+,.0f}) khớp corp-action ĐÃ CONFIRMED "
              f"trong data/corp_actions.json (qty_multiplier {d['qty_multiplier']}) — chế độ "
              f"--from-raw: KHÔNG chặn, quy ngược KL về {positions[t]['qty']:,.2f} như hành vi "
              f"trước gate. Chế độ LIVE vẫn chặn.", file=sys.stderr)
    if share_event_blocks or qty_unexplained:
        parts = []
        for t, d in share_event_blocks:
            parts.append(
                f"{t}: KL {d['qty_prev']:,.0f}→{d['qty_now']:,.0f} (so với {d['prev_qty_date']}), "
                f"lệnh khớp thật {d['net_fill']:+,.0f} ⇒ phần dư {d['residual']:+,.0f} KHỚP tỉ lệ "
                f"{d['exercise_ratio']} của {d['event_code']} ex-date {d['ex_date']} "
                f"(kỳ vọng {d['expected_residual']:,.2f}) ⇒ broker ĐÃ CREDIT SỚM")
        for t, d in qty_unexplained:
            why = (f"lịch có {d['event_code']} ex-date {d['ex_date']} nhưng phần dư KHÔNG khớp tỉ "
                   f"lệ {d.get('exercise_ratio')} (kỳ vọng {d.get('expected_residual')})"
                   if d.get("ex_date") else
                   "lịch corp-action KHÔNG có sự kiện nào cho mã này vào phiên kế tiếp")
            parts.append(
                f"{t}: KL {d['qty_prev']:,.0f}→{d['qty_now']:,.0f} (so với {d['prev_qty_date']}), "
                f"lệnh khớp thật {d['net_fill']:+,.0f} ⇒ phần dư {d['residual']:+,.0f} CHƯA GIẢI "
                f"THÍCH ĐƯỢC — {why}")
        n = len(share_event_blocks) + len(qty_unexplained)
        print(f"🚨 [{args.date}] KHỐI LƯỢNG vị thế đổi NGOÀI lệnh khớp thật cho {n} mã "
              f"({len(share_event_blocks)} khớp tỉ lệ sự kiện, {len(qty_unexplained)} chưa giải "
              f"thích được) — KHÔNG tính NAV, CẦN NGƯỜI xử lý: {'; '.join(parts)}. "
              f"[lịch: {ca_gate_note}] "
              f"Đường phục hồi cho mã ĐÃ khớp tỉ lệ: chờ corp_action_auto_confirm.py (cron 19:25) "
              f"ghi _status=CONFIRMED + qty_multiplier vào data/corp_actions.json rồi chạy lại "
              f"`daily_nav_snapshot.py --from-raw --date {args.date}` — CHỈ mã đã CONFIRMED mới "
              f"được quy ngược KL. Mã 'CHƯA GIẢI THÍCH ĐƯỢC' phải có người xác minh trước.",
              file=sys.stderr)
        # P4 (arch-review vòng 1): bằng chứng quyết định gate phải nằm trên ĐĨA, không chỉ stdout.
        # §8 (arch-review vòng 2, mục [3]): tên RIÊNG, KHÔNG phải nav_snapshot_{acct}_{date}.json —
        # chạy lại tay sau một ngày đã ghi NAV thành công sẽ ĐÈ MẤT artifact audit mà
        # dividend_adjusted_return.py viện dẫn làm nguồn xác nhận độc lập. Ghi atomic (§5).
        _write_json_atomic(
            os.path.join(EXEC_DIR, f"nav_gate_block_{args.account}_{args.date}.json"),
            {"account": args.account, "date": args.date, "nav": None,
             "gate_verdict": "qty_change_block", "rc": 5,
             "corp_action_gate_v2": {
                 "active": ca_gate_active, "note": ca_gate_note,
                 "share_event_blocks": [{"ticker": t, "detail": d} for t, d in share_event_blocks],
                 "qty_unexplained": [{"ticker": t, "detail": d} for t, d in qty_unexplained]}})
        return 5

    PRICE_XCHECK_TOLERANCE_PCT = 5.0
    mismatched = []
    raw_price_notes = []
    if args.from_raw:
        for t in tickers:
            if t in corp_action_recovered:
                # KL của mã này ĐÃ được quy ngược ở gate trên bằng qty_multiplier CONFIRMED —
                # KHÔNG để classify_raw_price_gap/early_credit chia LẦN HAI.
                d = corp_action_recovered[t]
                raw_price_notes.append(
                    f"{t}: corp-action ĐÃ CONFIRMED (qty_multiplier {d['qty_multiplier']}) — quy KL "
                    f"{d['qty_now']:,.0f} về {positions[t]['qty']:,.2f} (trước sự kiện); mark giá "
                    f"BQ Price {prices.get(t)} của chính ngày {args.date}.")
                continue
            if t in cash_div_confirmed:
                d = cash_div_confirmed[t]
                raw_price_notes.append(
                    f"{t}: cổ tức tiền mặt {d['value_per_share']:,.0f}đ/cp, broker đã hạ giá "
                    f"tham chiếu sớm (marketPrice {d['mkt_price']:,.0f} ≈ giá cum {d['price_ref']:,.0f} "
                    f"− cổ tức) — mark giá CUM, cổ tức phải thu đã trừ khỏi tiền mặt riêng "
                    f"(cum_dividend_double_count, không đếm 2 lần).")
                continue
            kind, mult = classify_raw_price_gap(t, args.date, prices.get(t), prev_prices.get(t),
                                                (positions[t] or {}).get("marketPrice"),
                                                PRICE_XCHECK_TOLERANCE_PCT)
            mp, cp = (positions[t] or {}).get("marketPrice"), prices.get(t)
            if kind == "stale_market_price":
                raw_price_notes.append(f"{t}: marketPrice {mp:,.0f} = giá phiên trước "
                                       f"{prev_prices[t]:,.0f} (feed trễ) — dùng BQ Price {cp:,.0f}")
            elif kind == "early_credit":
                corp_action_adj[t] = mult
                positions[t]["qty"] = positions[t]["qty"] / mult
                raw_price_notes.append(f"{t}: broker ghi có corp-action sớm (Price {cp:,.0f}/{mult} ≈ "
                                       f"marketPrice {mp:,.0f}) — quy KL về trước sự kiện")
            elif kind == "unexplained":
                mismatched.append((t, cp, mp, abs(cp - mp) / mp * 100))
    elif is_today:
        for t in tickers:
            if t in cash_div_confirmed:
                continue
            mp = (positions[t] or {}).get("marketPrice")
            cp = prices.get(t)
            if not mp or not cp:
                continue
            diff_pct = abs(cp - mp) / mp * 100
            if diff_pct > PRICE_XCHECK_TOLERANCE_PCT:
                mismatched.append((t, cp, mp, diff_pct))
    else:
        # Lịch sử: CHỈ đối chiếu các mã VỪA bị quy đổi corp-action ở trên. So trực tiếp
        # close_price lịch sử (trước sự kiện) với marketPrice LIVE (sau sự kiện) của mã
        # KHÔNG có corp-action sẽ luôn lệch do biến động giá bình thường qua thời gian —
        # không phải bug, nên nhóm đó giữ nguyên hành vi cũ (bỏ qua, không gate). Với mã CÓ
        # corp-action, quy đổi close_price lịch sử về cùng cơ sở với marketPrice hiện tại
        # (chia cho đúng multiplier đã dùng để quy đổi qty) rồi mới so — lệch còn lại sau khi
        # đã trừ phần corp-action là dấu hiệu bug KHÁC (multiplier sai, thiếu sự kiện...).
        for t, mult in corp_action_adj.items():
            mp = (positions[t] or {}).get("marketPrice")
            cp = prices.get(t)
            if not mp or not cp:
                continue
            cp_adj = cp / mult
            diff_pct = abs(cp_adj - mp) / mp * 100
            if diff_pct > PRICE_XCHECK_TOLERANCE_PCT:
                mismatched.append((t, cp_adj, mp, diff_pct))
    if mismatched:
        detail = "; ".join(f"{t}: close_price={cp:,.0f} vs vị thế broker marketPrice={mp:,.0f} "
                           f"(lệch {d:.1f}%)" for t, cp, mp, d in mismatched)
        print(f"❌ [{args.date}] Giá close_price(G1) và marketPrice của vị thế broker LỆCH "
              f">{PRICE_XCHECK_TOLERANCE_PCT:.0f}% cho {len(mismatched)} mã — KHÔNG tính NAV "
              f"(broker chưa đồng bộ hết nguồn giá — corp-action hoặc trễ marketPrice EOD, "
              f"xem VHM 2026-08-05 / PVT 2026-09-08): "
              f"{detail}. Sẽ tự retry trong cửa sổ ngắn; nếu vẫn lệch sau đó cần kiểm tra thủ công.",
              file=sys.stderr)
        return 4

    mtm_stock = sum(pos["qty"] * prices[t] for t, pos in positions.items())

    # NAV = Tiền + Cổ phiếu − Nợ (đúng như app DNSE hiển thị "Tài sản ròng" — user xác nhận
    # 2026-07-06 bằng ảnh chụp thật, khớp chính xác đến từng đồng: 709.276.086 + 683.590.000
    # − 409.863.737 = 983.002.349). KHÔNG cần tự ước tính "tiền bán chờ T+2" cộng riêng —
    # `totalCash` của DNSE RỐT CUỘC cũng tự cộng khoản này vào, chỉ là CẦN THỜI GIAN để hệ
    # thống broker cập nhật (có vẻ qua 1 đợt đối soát cuối ngày, không tức thời sau khớp
    # lệnh). Bài học rút ra CÙNG NGÀY (xem kb/INCIDENTS.md): lần đọc balance sớm hơn cùng
    # ngày (giữa phiên chiều) từng cho totalDebt=0 SAI — không phải do nợ được trả ngay như
    # suy luận ban đầu, mà đơn giản là dữ liệu balance LÚC ĐÓ CHƯA CẬP NHẬT XONG (stale).
    # Lần đọc sau (cuối ngày) mới đúng, khớp ảnh chụp thật. => KHÔNG tự suy luận/mô hình hoá
    # thêm gì — chỉ cần đảm bảo balance record dùng để tính NAV là bản MỚI NHẤT trong ngày
    # (đã tự động nhờ latest_balance() lấy dòng cuối), và cảnh báo rõ nếu có dấu hiệu stale.
    # + egg_value: Trứng vàng tự đọc từ API (field egg.totalValue trong balances), live từ 2026-08-18.
    # + offbook: tài sản off-book user tự báo KHÁC egg — cộng thẳng vào NAV thật,
    # KHÔNG lẫn vào 'cash' (cash vẫn = sức mua thật ở tài khoản môi giới).
    nav = mtm_stock + cash - debt + offbook + egg_value

    sell_today = today_sell_value(args.account, args.date)
    stale_warning = None
    if sell_today > 1_000_000 and cash < sell_today * 0.5:
        stale_warning = (f"Hôm nay có bán {sell_today:,.0f}đ nhưng tiền mặt ({cash:,.0f}đ) "
                         f"không phản ánh tương xứng — balance có thể CHƯA cập nhật xong "
                         f"(đối soát cuối ngày), nên chạy lại script này muộn hơn/ngày mai "
                         f"để lấy số chính xác trước khi tin tưởng hoàn toàn.")

    hist_path, hist_rows = load_history(args.account)
    prev_nav = None
    for row in hist_rows:
        if row["date"] < args.date:
            prev_nav = float(row["nav"])
    if prev_nav is None:
        prev_nav = args.starting_capital

    day_change = nav - prev_nav
    day_change_pct = day_change / prev_nav * 100 if prev_nav else 0

    # SANITY GUARD (bài học 2026-07-07: NAV -98.25% được auto-đăng lên Trading report vì
    # không tầng nào chặn số phi lý): |biến động ngày| vượt ngưỡng → KHÔNG ghi lịch sử,
    # KHÔNG in NAV — in cảnh báo escalate để con người xem. VNINDEX biên độ ±7%/ngày; NAV
    # account biến động >15%/ngày gần như chắc chắn là bug dữ liệu (hoặc nạp/rút tiền lớn —
    # trường hợp đó con người xác nhận rồi chạy lại với NAV_SANITY_MAX_PCT cao hơn).
    sanity_max = float(os.environ.get("NAV_SANITY_MAX_PCT", "15"))
    if abs(day_change_pct) > sanity_max:
        print(f"🔴 NAV {args.date} ({args.account}) TỰ CHẶN KHÔNG ĐĂNG: {nav:,.0f} VND "
              f"(biến động {day_change_pct:+.2f}%/ngày vượt ngưỡng ±{sanity_max:.0f}%) — "
              f"gần như chắc chắn lỗi dữ liệu (vị thế thiếu/giá sai). Cần người kiểm tra; "
              f"nếu là nạp/rút tiền thật → chạy lại với NAV_SANITY_MAX_PCT lớn hơn.")
        return 3

    hist_rows = [row for row in hist_rows if row["date"] != args.date]
    hist_rows.append({"date": args.date, "nav": f"{nav:.0f}", "mtm_stock": f"{mtm_stock:.0f}",
                       "cash": f"{cash:.0f}", "margin_debt": f"{debt:.0f}",
                       "offbook_assets": f"{offbook:.0f}", "egg_assets": f"{egg_value:.0f}",
                       "balance_ts": bal["ts"],
                       "cum_dividend_excl": f"{cum_div['amount']:.0f}",
                       "nav_is_estimate": "True" if args.from_raw else "False",
                       "nav_source": (f"backfill dnse_raw positions@{positions_ts} balances@{bal['ts']} "
                                      f"+ BQ Price" if args.from_raw else "live")})
    hist_rows.sort(key=lambda r: r["date"])
    # `cash` = tiền THẬT của broker TRỪ cổ tức phải thu chưa qua ex-date (cum_dividend_excl),
    # để bất biến nav = mtm_stock + cash − margin_debt + offbook_assets luôn đúng trên mọi dòng.
    fieldnames = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets",
                  "egg_assets", "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
    _write_nav_history(hist_path, hist_rows, fieldnames)

    since_inception = nav - args.starting_capital
    since_inception_pct = since_inception / args.starting_capital * 100

    lines = [
        f"💰 **NAV {args.date}: {nav:,.0f} VND** ({day_change:+,.0f} VND, {day_change_pct:+.2f}% so với hôm trước)",
        f"   Cổ phiếu {mtm_stock:,.0f} · Tiền mặt {cash:,.0f} · Nợ margin {debt:,.0f}"
        + (f" · Trứng vàng {egg_value:,.0f}" if egg_value else "")
        + (f" · Off-book {offbook:,.0f}" if offbook else ""),
        f"   Từ go-live: {since_inception:+,.0f} VND ({since_inception_pct:+.2f}%)",
    ]
    if cum_div["amount"]:
        lines.append(f"   ℹ️ Đã LOẠI {cum_div['amount']:,.0f} VND cổ tức phải thu khỏi tiền mặt "
                      f"(broker báo {cash_broker:,.0f}) — {cum_div['note']}")
    for w in cum_div["warnings"]:
        lines.append(f"   ⚠️ {w}")
    if offbook:
        lines.append(f"   ℹ️ Off-book {offbook:,.0f} VND ({offbook_note or 'không có ghi chú'}, "
                      f"user tự báo asof {offbook_asof or '?'}) — KHÔNG lộ qua API broker, đã "
                      f"cộng vào NAV nhưng KHÔNG tính là tiền mặt khả dụng để đặt lệnh ngay.")
    if offbook_stale_warning:
        lines.append(f"   ⚠️ {offbook_stale_warning}")
    if debt > 1_000_000:
        lines.append(f"   ⚠️ Đang có nợ margin thật {debt:,.0f} VND — theo dõi lãi vay tích lũy.")
    if stale_warning:
        lines.append(f"   ⚠️ {stale_warning}")
    if verify_warning:
        lines.append(f"   ℹ️ {verify_warning}")
    if args.from_raw:
        lines.append(f"   ℹ️ BACKFILL ƯỚC TÍNH (nav_is_estimate=True): positions {positions_ts}, "
                     f"balances {bal['ts']}, giá BQ Price thô")
        for n in raw_price_notes:
            lines.append(f"   ℹ️ {n}")
    print("\n".join(lines))

    out = {"account": args.account, "date": args.date, "nav": nav,
           "mtm_stock": mtm_stock, "cash": cash, "cash_broker": cash_broker,
           "cum_dividend_excl": cum_div, "margin_debt": debt,
           "egg_assets": egg_value, "egg_assets_auto": True,
           "offbook_assets": offbook, "offbook_assets_note": offbook_note,
           "offbook_assets_asof": offbook_asof, "offbook_stale_warning": offbook_stale_warning,
           "stale_warning": stale_warning, "prev_nav": prev_nav, "day_change": day_change,
           "day_change_pct": day_change_pct, "since_inception": since_inception,
           "since_inception_pct": since_inception_pct, "balance_ts": bal["ts"],
           "nav_is_estimate": bool(args.from_raw), "positions_ts": positions_ts,
           "raw_price_notes": raw_price_notes, "corp_action_qty_adj": corp_action_adj,
           # [5] arch-review vòng 2: P4 trước chỉ ghi bằng chứng ở nhánh rc=5 + cash_div_confirmed
           # ⇒ không audit được ca gate INERT (không mã nào khớp) hay ca gate bị TẮT TIẾNG vì
           # thiếu/hỏng snapshot lịch. Ghi luôn ở đường THÀNH CÔNG để mỗi ngày có NAV đều trả lời
           # được "hôm đó gate có đang bảo vệ không, dựa trên lịch nào".
           "corp_action_gate_v2": {
               "active": ca_gate_active, "note": ca_gate_note,
               "n_tickers_checked": len(tickers) if (args.from_raw or is_today) else 0,
               "share_event_blocks": [], "qty_unexplained": [],
               "cash_div_confirmed": cash_div_confirmed,
               "corp_action_recovered": corp_action_recovered},
           "source": "verify_account_snapshot.py (fills) + dnse_raw balances (real broker API, "
                     "chọn bản GHI CUỐI CÙNG trong ngày — balance có thể cần thời gian đối soát "
                     "cuối phiên mới phản ánh đúng, xem cảnh báo staleness nếu có) + "
                     "egg.totalValue từ balances API (tự động, live từ 2026-08-18) + "
                     "manual_offbook_assets_vnd (trading_bot_accounts.json, user tự báo, KHÔNG "
                     "có API — xem note/asof)"}
    with open(os.path.join(EXEC_DIR, f"nav_snapshot_{args.account}_{args.date}.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
