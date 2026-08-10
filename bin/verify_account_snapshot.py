#!/usr/bin/env python3
"""verify_account_snapshot.py --account SpaceX --date YYYY-MM-DD

Tính NAV/vị thế/giá vốn THẬT cho báo cáo — nguồn duy nhất được phép dùng để viết
báo cáo trading (ngày/tuần/tháng). KHÔNG được đọc trực tiếp các field avg_cost/*
trong eod_account_*.json hay bất kỳ file tóm tắt trung gian nào khác cho mục đích
tính lãi/lỗ — những field đó có thể chỉ là giá tham chiếu ước tính (ref_px_approx),
không phải giá khớp thật.

Nguồn sự thật (ưu tiên theo thứ tự):
  1. data/execution_logs/dnse_raw_{date}.jsonl — log thô từ API broker (authoritative:
     averagePrice + fillQuantity do chính DNSE trả về). Dùng để tính giá vốn bình quân
     gia quyền THẬT cho từng mã, dedupe theo order id (giữ bản ghi mới nhất).
  2. data/execution_logs/exec_{account}_{date}_journal.csv — journal FILL event nội bộ,
     dùng làm cross-check độc lập với (1). Nếu 2 nguồn lệch vượt ngưỡng -> cảnh báo,
     KHÔNG âm thầm chọn một bên.
  3. BigQuery tav2_bq.ticker — giá đóng cửa thị trường mới nhất, dùng để mark-to-market.

Quy ước giá vốn: bình quân gia quyền THEO LÔ ĐANG SỐNG (`CostBook`) — bán bớt rút cơ sở giá
vốn theo tỉ lệ (giá bình quân không đổi), vị thế về 0 thì cơ sở về 0 và lô mua lại sau đó
tính riêng. Khớp đúng quy ước `costPrice` của DNSE (đã đối chiếu 21 mã SpaceX + 15 mã
ZaloPay ngày 2026-08-10). Bug LPB 2026-08-10: xem docstring `CostBook`.

Fail-safe: nếu số lượng cổ phiếu tính từ dnse_raw không khớp broker-audited quantities
(khi có file eod_account_{date}.json để đối chiếu), hoặc không tìm thấy dữ liệu nguồn,
script THOÁT với exit != 0 và in cảnh báo rõ ràng — không tự đoán số liệu để báo cáo tiếp.
"""
import argparse
import datetime as _dt
import glob
import json
import os
import subprocess
import sys
from collections import defaultdict

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXEC_DIR = os.path.join(WC_ROOT, "data", "execution_logs")
BQ_PATH_PREFIX = "/home/trido/google-cloud-sdk/bin"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corp_actions import load_corp_actions  # noqa: E402


def corp_action_multiplier(ticker, fill_date, asof, actions):
    """Hệ số nhân KL cho 1 fill ngày `fill_date`, dùng để cộng dồn đúng vào raw_agg/journal_agg.

    Cùng quy tắc thời điểm với LotBook.corp_action_split (park_holdings.py) — lô mua TRƯỚC
    ex_date thì được hưởng quyền (nhân KL) NHƯNG chỉ áp dụng từ ngày báo cáo `asof` đã tới/qua
    ex_date (giá BQ/close_price chỉ phản ánh split TỪ ex_date trở đi — trước đó KL và giá đều
    phải giữ nguyên trạng thái CHƯA chia, khớp đúng giá thị trường thật của ngày đó, xem bug
    2026-08-05 VHM: broker credit KL sớm 1 phiên trước ex_date, nhưng giá BQ/close_price ngày
    đó CHƯA chia — áp multiplier sớm sẽ tạo ra đúng loại lệch mà bug gốc đã gây ra).

    Script này gộp fill theo NGÀY (không giữ lot rời như LotBook) nên không xử lý được ca bán
    xen giữa các lô có ex_date khác nhau của CÙNG mã — chưa gặp thực tế, nếu xảy ra sẽ cần
    nâng cấp lên lot-based giống park_holdings.py.
    """
    mult = 1.0
    for a in actions:
        if a["ticker"] == ticker and fill_date < a["ex_date"] <= asof:
            mult *= a["qty_multiplier"]
    return mult


class CostBook:
    """Giá vốn bình quân gia quyền CỦA LÔ ĐANG SỐNG — reset khi vị thế về 0.

    Quy ước kế toán chuẩn (và đúng quy ước `costPrice` của DNSE): lệnh BÁN rút cơ sở giá
    vốn theo TỈ LỆ tại đúng giá bình quân hiện hành (nên bán bớt KHÔNG làm đổi giá bình
    quân), và khi vị thế về 0 thì cơ sở giá vốn cũng về 0 — lô ĐÃ TẤT TOÁN không được
    trộn vào lô mua lại sau đó.

    Bug 2026-08-10 (LPB/SpaceX, job Taylor_20260810_044215): bản cũ cộng dồn buy_qty/
    buy_value qua MỌI ngày rồi chia một lần (buy_value/buy_qty), không hề biết vị thế đã
    về 0 giữa chừng. LPB mua 900 (01/07) → bán SẠCH 900 (06/07) → mua lại 900 (15/07) ra
    52.583,33 thay vì 51.466,67 (= đúng costPrice broker). Sai cả giá vốn lẫn P&L% của mã.
    """

    def __init__(self):
        self.qty = 0.0      # KL ròng đang nắm giữ (đã nhân hệ số corp-action)
        self.basis = 0.0    # tổng tiền vốn CÒN LẠI của lô đang giữ (VND)
        self.resets = 0     # số lần vị thế về 0 (mỗi lần = 1 lô tất toán, cơ sở về 0)

    def buy(self, qty, value):
        self.qty += qty
        self.basis += value

    def sell(self, qty):
        if self.qty > 0:
            self.basis -= self.basis * min(qty, self.qty) / self.qty
        self.qty -= qty
        if abs(self.qty) <= 1e-9:       # vị thế về 0 -> lô tất toán, cơ sở giá vốn về 0
            self.qty, self.basis = 0.0, 0.0
            self.resets += 1
        elif self.qty < 0:              # bán quá KL trace được (vị thế legacy mua trước bot)
            self.basis = 0.0

    @property
    def avg_cost(self):
        return self.basis / self.qty if self.qty > 0 else 0.0


def build_cost_books(events_by_date, asof, corp_actions):
    """{ticker: CostBook} từ các fill ĐÃ SẮP THEO THỜI GIAN.

    Thứ tự thời gian là BẮT BUỘC (không phải chi tiết trang trí): reset-khi-về-0 chỉ đúng
    khi lệnh được áp đúng trình tự thật — cả giữa các ngày lẫn trong cùng một ngày.
    """
    books = defaultdict(CostBook)
    for date in sorted(events_by_date):
        for _ts, _key, tk, side, qty, price in events_by_date[date]:
            m = corp_action_multiplier(tk, date, asof, corp_actions)
            if side == "sell":
                books[tk].sell(qty * m)
            else:
                books[tk].buy(qty * m, qty * price)
    return books


def aggregate_events(events):
    """{ticker: (net_qty, buy_qty, buy_value)} — gộp cả ngày, KHÔNG theo lô."""
    agg = defaultdict(lambda: [0.0, 0.0, 0.0])
    for _ts, _key, tk, side, qty, price in events:
        if side == "sell":
            agg[tk][0] -= qty
        else:
            agg[tk][0] += qty
            agg[tk][1] += qty
            agg[tk][2] += qty * price
    return {tk: tuple(v) for tk, v in agg.items()}


def dnse_fill_events(account_no, date):
    """Trả về ([(ts, order_id, ticker, side, qty, price)], err) — ĐÃ SẮP THEO THỜI GIAN.

    Nguồn sự thật của giá vốn: `averagePrice`/`fillQuantity` do chính DNSE trả về, dedupe
    theo order id (giữ bản ghi mới nhất). Giữ TỪNG fill rời (thay vì gộp sẵn theo ngày như
    trước) để CostBook áp được đúng trình tự mua/bán — điều kiện cần để phát hiện vị thế
    về 0 giữa ngày, không chỉ giữa các ngày.

    `ts` = `modifiedDate` (thời điểm bản ghi order mới nhất), KHÔNG phải dấu thời gian khớp
    từng phần — nên thứ tự TRONG ngày là xấp xỉ (đủ tốt: order bán/mua cùng mã trong 1 ngày
    tách nhau hàng phút). Thứ tự GIỮA các ngày luôn chính xác vì tách theo file ngày.
    """
    path = os.path.join(EXEC_DIR, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(path):
        return None, f"missing dnse_raw_{date}.jsonl"
    latest_by_id = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            orders = []
            if rec.get("kind") == "orders":
                orders = rec.get("payload", {}).get("orders") or []
            elif rec.get("kind") == "place_order":
                r = rec.get("payload", {}).get("resp") or {}
                if r.get("id") is not None:
                    orders = [r]
            for o in orders:
                oid = o.get("id")
                if oid is None:
                    continue
                if account_no and o.get("accountNo") not in (None, account_no):
                    continue
                latest_by_id[oid] = o  # ghi đè -> bản ghi mới nhất mỗi order id

    events = []
    for oid, o in latest_by_id.items():
        fq = o.get("fillQuantity") or 0
        if fq <= 0:
            continue
        raw_side = str(o.get("side") or "").upper()
        # NS (Normal Sell) = bán; NB (Normal Buy) hoặc side khác chưa gặp -> coi là mua
        side = "sell" if (raw_side.startswith("NS") or raw_side == "SELL") else "buy"
        ts = o.get("modifiedDate") or o.get("createdDate") or ""
        events.append((ts, oid, o.get("symbol"), side, float(fq),
                       float(o.get("averagePrice") or o.get("price") or 0)))
    events.sort(key=lambda e: (e[0], str(e[1])))
    return events, None


def true_fills_from_dnse_raw(account_no, date):
    """Trả về {ticker: (net_qty, buy_qty, buy_value)} từ log thô broker cho 1 ngày.

    net_qty = buy_qty - sell_qty (KL thật đang nắm giữ, để đối chiếu snapshot broker).
    buy_qty/buy_value CHỈ tính từ lệnh MUA — giá vốn bình quân gia quyền không đổi khi
    bán bớt (weighted-average costing chuẩn kế toán), nên KHÔNG được trộn giá bán vào.
    Bug 2026-07-06 (kb/INCIDENTS.md): bản cũ cộng dồn fillQuantity bất kể side, nên ngày
    có lệnh BÁN (trim 07-06) bị CỘNG thêm thay vì TRỪ, gây báo lệch số lượng giả.

    ⚠️ buy_qty/buy_value ở đây là TỔNG CẢ ĐỜI, KHÔNG theo lô — chia ra được giá vốn ĐÚNG
    chỉ khi vị thế chưa từng về 0. Giá vốn dùng cho báo cáo lấy từ `CostBook`/
    `build_cost_books()` (reset khi vị thế về 0), không lấy từ đây (bug LPB 2026-08-10).
    """
    events, err = dnse_fill_events(account_no, date)
    if events is None:
        return None, err
    return aggregate_events(events), None


def journal_fill_events(account, date):
    """Trả về ([(ts, child_oid, ticker, side, qty, price)], err) — ĐÃ SẮP THEO THỜI GIAN.

    Bản event-level của `true_fills_from_journal()` (xem docstring dưới về việc `qty` là
    LŨY KẾ theo child_oid nên chỉ được giữ dòng CUỐI mỗi child).
    """
    path = os.path.join(EXEC_DIR, f"exec_{account}_{date}_journal.csv")
    if not os.path.exists(path):
        return None, f"missing exec_{account}_{date}_journal.csv"
    import csv
    latest_by_child = {}  # child_oid -> (ts, ticker, side, cumulative_qty, price)
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL":
                continue
            child_oid = row.get("child_oid")
            ts = row.get("ts", "")
            prev = latest_by_child.get(child_oid)
            if prev is None or ts >= prev[0]:
                latest_by_child[child_oid] = (
                    ts, row.get("ticker"), str(row.get("side") or "").lower(),
                    float(row.get("qty") or 0), float(row.get("price") or 0))
    events = [(ts, oid, tk, "sell" if side == "sell" else "buy", qty, price)
              for oid, (ts, tk, side, qty, price) in latest_by_child.items()]
    events.sort(key=lambda e: (e[0], str(e[1])))
    return events, None


def true_fills_from_journal(account, date):
    """Cross-check độc lập từ journal CSV nội bộ (event=FILL). Cùng nguyên tắc net_qty
    (buy trừ sell) + cost basis chỉ từ buy như true_fills_from_dnse_raw() ở trên.

    QUAN TRỌNG: Executor._sync_fills ghi `qty` = c["filled"] LŨY KẾ của child order tại
    thời điểm đó (executor.py dòng ~386), KHÔNG PHẢI phần fill tăng thêm — 1 child có thể
    xuất hiện nhiều dòng FILL khi khớp từng phần (vd 600 rồi 2100 lũy kế, không phải 600+2100).
    Cộng dồn hết mọi dòng sẽ đếm trùng. Bug 2026-07-06 (kb/INCIDENTS.md): HDB báo lệch vì
    cộng cả dòng lũy kế trung gian lẫn dòng cuối. Fix: chỉ giữ dòng CUỐI (theo ts) mỗi
    child_oid, rồi mới cộng qua các child_oid khác nhau — giống hệt cách
    true_fills_from_dnse_raw() dùng latest_by_id cho cùng lý do.

    ⚠️ Cùng giới hạn với true_fills_from_dnse_raw(): buy_qty/buy_value là TỔNG CẢ ĐỜI,
    không theo lô — giá vốn dùng cho báo cáo lấy từ `build_cost_books()`.
    """
    events, err = journal_fill_events(account, date)
    if events is None:
        return None, err
    return aggregate_events(events), None


def bq_close_prices(tickers, as_of_date):
    env = dict(os.environ)
    env["PATH"] = BQ_PATH_PREFIX + ":" + env.get("PATH", "")
    tick_list = ",".join(f"'{t}'" for t in sorted(tickers))
    sql = f"""
    SELECT t.ticker, t.Close
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ({tick_list})
    AND t.time = (SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2
                  WHERE t2.ticker = '{sorted(tickers)[0]}' AND t2.time <= '{as_of_date}')
    """
    cmd = ["bq", "query", "--use_legacy_sql=false",
           "--project_id=lithe-record-440915-m9", "--format=json",
           "--max_rows=5000", sql]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if out.returncode != 0:
        return None, out.stderr.strip()
    rows = json.loads(out.stdout)
    return {r["ticker"]: float(r["Close"]) for r in rows}, None


def dnse_close_prices(tickers, with_source=False):
    """Giá tham chiếu ĐÚNG PHIÊN của từng mã qua API DNSE (đơn vị nghìn đồng → VND).

    Chỉ dùng khi --asof LÀ HÔM NAY: BQ tav2_bq.ticker chỉ sync đêm (23:45 ICT) nên
    khi eod_trading_report.sh chạy 15:00 ICT cùng ngày, BQ CHƯA CÓ giá đóng cửa hôm
    đó — bq_close_prices() lặng lẽ rơi về giá của ngày giao dịch gần nhất trước đó
    (2026-07-06: rơi về 07-03, lệch ~4.79tr VND cho SpaceX). Bug phát hiện 2026-07-06
    khi user đối chiếu bảng giá với app thật — field positions().marketPrice CŨNG sai
    (không phải giá ATC) nên không dùng; verify_finding: close_price()/latest_trade()
    boardId=G1 khớp 100% với nhau và khớp chính xác tới đồng với ảnh chụp app DNSE.

    ⚠️ CÁI BẪY THỨ HAI, NGƯỢC CHIỀU CÁI TRÊN (vá 2026-08-11, job Taylor_20260810_183618):
    `close_price` G1 là giá đóng cửa của PHIÊN GẦN NHẤT ĐÃ XONG. Khi hàm này chạy TRƯỚC
    khi phiên hôm nay đóng (tiền phiên 01:30, hay trong phiên 10:00), giá đó thuộc phiên
    TRƯỚC — và với một mã đang GIAO DỊCH KHÔNG HƯỞNG QUYỀN hôm nay, giá phiên trước là giá
    CHƯA điều chỉnh, trong khi `openQuantity` của broker thì ĐÃ điều chỉnh. Nhân giá cũ với
    số lượng mới = thổi phồng NAV. Ca thật MBB 2026-08-11 (cổ tức CP 15% + quyền mua 10:1
    giá 10.000đ): G1 close 24.250 (phiên 08-10) vs giá tham chiếu thật hôm nay 20.200 ⇒
    SpaceX +5.013.250đ ≈ +0,5% NAV, user bắt được bằng ảnh chụp app.

    Vì vậy: nếu giá G1 KHÔNG PHẢI của phiên hôm nay, giải giá THUỘC PHIÊN HÔM NAY qua
    `_today_session_price()`. Đây là lời giải TỔNG QUÁT: nó không cần biết mã nào có sự
    kiện gì, chỉ cần biết "giá đang cầm thuộc phiên nào". Nó cũng vá luôn UPCOM, nơi giá
    tham chiếu = giá BÌNH QUÂN phiên trước chứ không phải giá đóng cửa (TV1 08-11: close
    19.800 nhưng basicPrice 19.700 — app DNSE hiện 19.700).

    ⚠️ HAI CỬA SỔ, KHÔNG PHẢI MỘT (quant-skeptic phá được phạm vi bản vá đầu, vá nốt cùng
    job). `close_price()` hỏng theo HAI kiểu khác nhau tuỳ giờ chạy:
      · TIỀN PHIÊN (00:00–09:00): G1 trả `closePrice` phiên TRƯỚC, khác 0 ⇒ bắt bằng cách so
        `time` của chính entry G1 với hôm nay.
      · GIỮA PHIÊN (09:00–14:45): G1 trả `closePrice=0` ở MỌI board (phiên chưa đóng) ⇒
        entry G1 rơi khỏi bộ lọc, mã BIẾN MẤT khỏi kết quả, và caller
        (`compute_active_nav.resolve_prices`) rơi về BQ T-1 CHƯA điều chỉnh × qty ĐÃ điều
        chỉnh = TÁI LẬP NGUYÊN VẸN cùng khoản thổi phồng, chỉ khác nhãn `bq_close_stale`.
        Đây đúng là khung DollarBill hay chạy (sự cố 2026-08-07 11:5x, `retro-2026-08-07`
        §6 — gốc lỗi đã biết từ 08-07 mà chưa ai vá) và ex-date làm nó nặng gấp bội: 08-07
        lệch 1,13% NAV, MBB hôm nay lệch 20,0% trên một mã.
    Cả hai cửa sổ giờ đi chung một đường: G1 không thuộc phiên hôm nay (thiếu HOẶC cũ) ⇒
    `_today_session_price()`.

    KHÔNG đổi hành vi ở đường chạy chính EOD (17:30) / báo cáo 15:00: lúc đó G1 close ĐÃ
    thuộc phiên hôm nay ⇒ nhánh mới không kích hoạt, giá vẫn là giá ATC thật như cũ.

    `with_source=True` ⇒ trả (prices, sources) với sources[tk] ∈ {'dnse_g1_today',
    'dnse_trade_today', 'dnse_secdef_basic'} để consumer ghi provenance trung thực thay vì
    khai khống 'dnse_g1'.
    """
    sys.path.insert(0, WC_ROOT)
    from trading_bot.brokers import get_dnse_client
    client = get_dnse_client()
    from zoneinfo import ZoneInfo
    today = _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()   # §16
    prices, sources, substituted = {}, {}, []
    for tk in tickers:
        try:
            r = client.close_price(tk)
        except Exception:
            continue
        entries = (r or {}).get("prices") or []
        g1 = next((e for e in entries
                   if e.get("boardId") == "G1" and e.get("closePrice")), None)
        px, src = ((float(g1["closePrice"]) * 1000, "dnse_g1_today") if g1 else (None, None))
        # `time` dạng "2026-08-10 14:45:03.261" (giờ ICT của sàn). Thiếu/không parse được ⇒
        # GIỮ giá G1 (fail-safe về hành vi cũ, đã chạy đúng suốt), không đoán sang nhánh mới.
        g1_day = str((g1 or {}).get("time") or "")[:10].replace("/", "-")
        # g1 THIẾU = giữa phiên (closePrice=0 mọi board); g1_day < today = tiền phiên.
        if g1 is None or (g1_day and g1_day < today):
            alt_px, alt_src = _today_session_price(client, tk, today)
            if alt_px:
                if px is not None and abs(alt_px - px) > 0.5:
                    substituted.append(f"{tk} {px:,.0f}→{alt_px:,.0f} "
                                       f"(G1 close phiên {g1_day}, thay bằng {alt_src})")
                px, src = alt_px, alt_src
        # Không giải được giá phiên hôm nay VÀ không có G1 nào để giữ ⇒ bỏ qua, caller tự
        # rơi về BQ và gắn nhãn `bq_close_stale` (trung thực về provenance, như cũ).
        if px is None:
            continue
        prices[tk], sources[tk] = px, src
    if substituted:
        print(f"ℹ️ giá thuộc phiên HÔM NAY thay cho giá đóng cửa phiên trước — thường là mã "
              f"đang giao dịch không hưởng quyền: {'; '.join(substituted)}", file=sys.stderr)
    return (prices, sources) if with_source else prices


def _today_session_price(client, ticker, today):
    """Giá THUỘC PHIÊN `today` của một mã → (px_vnd, source) hoặc (None, None).

    Thứ tự ưu tiên, và LÝ DO của thứ tự đó:
      1. `latest_trade` G1 `matchPrice` — mark SỐNG, cùng vintage với `openQuantity`, đúng
         bright-line §6 (same-day: DNSE, never BQ). Đây cũng chính là hướng DollarBill đề
         xuất cho Taylor trong finding 2026-08-07 ("nên fallback sang latest_trade, KHÔNG
         phải BQ").
      2. `secdef.basicPrice` — giá tham chiếu CHÍNH THỨC của sàn cho phiên hiện tại, đã gồm
         mọi điều chỉnh corp action. Dùng khi mã CHƯA khớp lệnh nào trong phiên (đầu phiên,
         mã kém thanh khoản) và cả trước giờ mở cửa, lúc (1) về mặt định nghĩa không tồn tại.

    ⚠️ CỔNG VINTAGE TRÊN `latest_trade` LÀ BẮT BUỘC, KHÔNG PHẢI PHÒNG XA: ngoài giờ giao
    dịch endpoint này trả khớp lệnh của PHIÊN TRƯỚC, tức giá CHƯA điều chỉnh — đo thật lúc
    02:2x ICT 2026-08-11, MBB trả `matchPrice=24,25 / time=2026-08-10 14:45:03.260` đúng
    bằng con số sai mà cả bản vá này sinh ra để loại bỏ. Bỏ cổng `time == today` là tự tay
    dựng lại bug qua một cửa khác.

    Mọi lỗi mạng/thiếu trường ⇒ (None, None) để caller giữ hành vi cũ; hàm này chỉ được phép
    LÀM TỐT HƠN, không được phép làm hỏng đường đang chạy."""
    try:
        r = client.latest_trade(ticker)
    except Exception:
        r = None
    trades = (r or {}).get("trades") or []
    t = next((e for e in trades
              if e.get("boardId") == "G1" and (e.get("matchPrice") or 0) > 0), None)
    if t and str(t.get("time") or "")[:10].replace("/", "-") == today:
        return float(t["matchPrice"]) * 1000, "dnse_trade_today"
    basic = _secdef_basic_price(client, ticker)
    if basic and basic > 0:
        return basic, "dnse_secdef_basic"
    return None, None


def _secdef_basic_price(client, ticker):
    """`basicPrice` (nghìn đồng → VND) từ secdef — giá tham chiếu sàn công bố cho phiên hiện
    tại. Mọi boardId trả CÙNG một giá trị (kiểm 2026-08-11: MBB 7/7 board đều 20,2) nên ưu
    tiên G1 rồi lấy bất kỳ entry nào có số dương. Lỗi mạng/thiếu trường ⇒ None để caller giữ
    giá G1 cũ; hàm này chỉ được phép LÀM TỐT HƠN, không được phép làm hỏng đường đang chạy."""
    try:
        sd = client.secdef(ticker)
    except Exception:
        return None
    entries = [e for e in (sd or []) if isinstance(e, dict) and (e.get("basicPrice") or 0) > 0]
    if not entries:
        return None
    g1 = next((e for e in entries if e.get("boardId") == "G1"), entries[0])
    return float(g1["basicPrice"]) * 1000


def pnl_coverage_warnings(covered_tickers, live_positions):
    """So vị thế broker THẬT vs các mã trace được fill history → cảnh báo RÕ RÀNG cho
    từng vị thế legacy bị loại khỏi P&L (audit Taylor_20260711_031821 F6).

    Script này tính cost-basis/P&L CHỈ từ fill history (dnse_raw + journal) — account
    có vị thế mua từ TRƯỚC khi bot quản lý (ZaloPay: DGC/VPB/VIB/VHC/TCM/TLG/MSH) không
    có fill nào nên bị bỏ qua. Trước đây bỏ qua IM LẶNG — bẫy cho weekly/monthly report
    ZaloPay đầu tiên: P&L đọc như thể phủ 100% holdings trong khi thiếu cả nghìn tỷ vị
    thế legacy (coding_guidelines §7.4). Bài toán TÍNH P&L cho legacy là việc riêng về
    sau; việc của hàm này là không cho phép thiếu-mà-không-nói.

    Trả về (warnings: [str], legacy_tickers: [str]). Pure function để selfcheck được.
    """
    if live_positions is None:
        return (["WARN không đọc được positions broker — KHÔNG xác minh được P&L "
                 "coverage (vị thế legacy không fill history có thể đang bị bỏ sót "
                 "khỏi P&L mà không ai biết)"], [])
    covered = set(covered_tickers)
    legacy = [tk for tk in sorted(live_positions) if tk not in covered]
    warns = [f"WARN position {tk} excluded from P&L — no fill history (legacy); "
             f"tổng P&L bên dưới KHÔNG bao gồm mã này" for tk in legacy]
    return warns, legacy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True)
    ap.add_argument("--account-no", default=None,
                     help="broker account number to filter dnse_raw orders — nếu bỏ trống, "
                          "tự tra secrets/trading_bot_accounts.json theo --account (BẮT BUỘC "
                          "phải lọc: dnse_raw_{date}.jsonl dùng CHUNG cho mọi account cùng "
                          "ngày, xem incident 2026-07-19 job Taylor_20260719_055139 — chạy tay "
                          "thiếu account-no từng trộn fill 2 account).")
    ap.add_argument("--dates", required=True,
                     help="comma-separated trading dates with fills, e.g. 2026-07-01,2026-07-02")
    ap.add_argument("--asof", required=True, help="mark-to-market date (BQ close price)")
    ap.add_argument("--broker-snapshot", default=None,
                     help="optional eod_account_{date}.json path to cross-check quantities")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tolerance-pct", type=float, default=0.5,
                     help="max %% diff allowed between dnse_raw and journal cost basis before warning")
    args = ap.parse_args()

    if not args.account_no:
        sys.path.insert(0, WC_ROOT)
        from trading_bot.config import load_config, load_accounts
        _match = next((p for p in load_accounts(load_config()) if p["label"] == args.account), None)
        args.account_no = _match.get("account_id") if _match else None
        if not args.account_no:
            print(f"XÁC MINH THẤT BẠI — không tự tra được account_id cho '{args.account}' trong "
                  f"trading_bot_accounts.json và --account-no cũng không được truyền. dnse_raw "
                  f"dùng chung cho mọi account cùng ngày — KHÔNG được chạy thiếu bộ lọc account "
                  f"(nguy cơ trộn fill account khác).", file=sys.stderr)
            sys.exit(4)

    # sắp theo thứ tự thời gian: CostBook chạy theo trình tự mua/bán thật, truyền --dates
    # lộn xộn mà không sắp sẽ cho giá vốn sai (reset-khi-về-0 phụ thuộc trình tự).
    dates = sorted({d.strip() for d in args.dates.split(",") if d.strip()})
    warnings = []

    corp_actions = load_corp_actions()

    raw_agg = defaultdict(lambda: [0.0, 0.0, 0.0])      # ticker -> [net_qty, buy_qty, buy_value]
    journal_agg = defaultdict(lambda: [0.0, 0.0, 0.0])
    raw_events, journal_events = {}, {}
    for date in dates:
        rev, err = dnse_fill_events(args.account_no, date)
        if rev is None:
            warnings.append(f"FATAL: {err} — không có nguồn broker thật cho {date}")
            continue
        raw_events[date] = rev
        for tk, (nq, bq, bv) in aggregate_events(rev).items():
            m = corp_action_multiplier(tk, date, args.asof, corp_actions)
            raw_agg[tk][0] += nq * m
            raw_agg[tk][1] += bq * m
            raw_agg[tk][2] += bv   # tổng giá trị đã mua KHÔNG đổi khi nhân KL/chia giá vốn

        jev, jerr = journal_fill_events(args.account, date)
        if jev is None:
            warnings.append(f"WARN: {jerr} — bỏ qua cross-check journal cho {date}")
        else:
            journal_events[date] = jev
            for tk, (nq, bq, bv) in aggregate_events(jev).items():
                m = corp_action_multiplier(tk, date, args.asof, corp_actions)
                journal_agg[tk][0] += nq * m
                journal_agg[tk][1] += bq * m
                journal_agg[tk][2] += bv

    # Giá vốn CHÍNH THỨC: bình quân gia quyền theo LÔ ĐANG SỐNG (reset khi vị thế về 0).
    # KHÔNG dùng raw_agg[buy_value]/raw_agg[buy_qty] — xem CostBook (bug LPB 2026-08-10).
    raw_books = build_cost_books(raw_events, args.asof, corp_actions)
    journal_books = build_cost_books(journal_events, args.asof, corp_actions)

    if any(w.startswith("FATAL") for w in warnings):
        print("XÁC MINH THẤT BẠI — không đủ dữ liệu nguồn broker thật:", file=sys.stderr)
        for w in warnings:
            print(" -", w, file=sys.stderr)
        sys.exit(2)

    # cross-check dnse_raw vs journal (2 nguồn độc lập) — so KL NET (mua-bán), giá vốn chỉ từ mua
    for tk in set(raw_agg) | set(journal_agg):
        rq = raw_agg.get(tk, (0, 0, 0))[0]
        jq = journal_agg.get(tk, (0, 0, 0))[0]
        if rq == 0 and jq == 0:
            continue
        if abs(rq - jq) > 1e-6:
            warnings.append(f"WARN qty mismatch {tk}: dnse_raw={rq:.0f} journal={jq:.0f}")
        # so giá vốn theo cùng quy ước lô-đang-sống ở CẢ 2 nguồn (so 2 quy ước khác nhau
        # sẽ đẻ ra cảnh báo giả ở đúng những mã đã tất toán rồi mua lại, vd LPB)
        r_avg = raw_books[tk].avg_cost if tk in raw_books else 0
        j_avg = journal_books[tk].avg_cost if tk in journal_books else 0
        if r_avg and j_avg:
            diff_pct = abs(r_avg - j_avg) / r_avg * 100
            if diff_pct > args.tolerance_pct:
                warnings.append(
                    f"WARN cost mismatch {tk}: dnse_raw_avg={r_avg:,.0f} "
                    f"journal_avg={j_avg:,.0f} (diff {diff_pct:.2f}%%)")

    # cross-check quantities vs an independently-audited broker snapshot, if given
    if args.broker_snapshot and os.path.exists(args.broker_snapshot):
        snap = json.load(open(args.broker_snapshot, encoding="utf-8"))
        snap_qty = {p["ticker"]: p["qty"] for p in snap.get("positions", [])}
        for tk, q in snap_qty.items():
            rq = raw_agg.get(tk, (0, 0, 0))[0]
            if abs(rq - q) > 1e-6:
                warnings.append(
                    f"WARN qty vs broker-snapshot {tk}: dnse_raw={rq:.0f} snapshot={q:.0f}")

    tickers = sorted(raw_agg.keys())
    if not tickers:
        prices, price_source = {}, {}
    else:
        prices, perr = bq_close_prices(tickers, args.asof)
        if prices is None:
            print(f"XÁC MINH THẤT BẠI — không lấy được giá BQ: {perr}", file=sys.stderr)
            sys.exit(3)
        price_source = {tk: "bq_close" for tk in prices}
    if tickers and args.asof == _dt.date.today().isoformat():
        dnse_prices = dnse_close_prices(tickers)
        for tk, px in dnse_prices.items():
            prices[tk] = px
            price_source[tk] = "dnse_atc_g1"
        missing_today = [tk for tk in tickers if price_source.get(tk) != "dnse_atc_g1"]
        if missing_today:
            warnings.append(
                f"WARN dùng giá BQ (có thể trễ vài ngày do BQ chỉ sync đêm) thay vì "
                f"giá ATC DNSE hôm nay cho: {missing_today}")

    positions = []
    total_cost = total_mtm = 0.0
    for tk in tickers:
        qty = raw_agg[tk][0]
        if qty <= 0:
            continue  # đã bán hết (net_qty<=0) -> không còn nắm giữ, bỏ khỏi báo cáo vị thế
        book = raw_books[tk]
        cost = book.avg_cost  # bình quân gia quyền của LÔ ĐANG SỐNG (reset khi về 0)
        if book.resets:
            warnings.append(
                f"INFO {tk}: vị thế đã về 0 {book.resets} lần rồi mua lại — giá vốn tính "
                f"lại từ lô mới ({cost:,.2f}), KHÔNG trộn lô đã tất toán")
        px = prices.get(tk)
        if px is None:
            warnings.append(f"WARN no BQ price for {tk} as of {args.asof}")
            continue
        cv, mv = qty * cost, qty * px
        total_cost += cv
        total_mtm += mv
        positions.append({"ticker": tk, "qty": qty, "true_avg_cost": round(cost, 1),
                           "cost_basis_lot_resets": book.resets,
                           "mtm_price": px, "mtm_price_source": price_source.get(tk, "bq_close"),
                           "cost_value": cv, "mtm_value": mv,
                           "unrealized_pnl": mv - cv,
                           "unrealized_pnl_pct": (mv - cv) / cv * 100 if cv else 0})

    # P&L coverage vs vị thế broker THẬT (F6): mã đang nắm giữ mà không trace được fill
    # history (legacy, mua trước khi bot quản lý) trước đây bị bỏ qua ÂM THẦM khỏi P&L —
    # giờ log rõ từng mã + gắn cờ pnl_coverage_complete để report sau này không đọc nhầm
    # P&L partial thành P&L toàn account. Reuse broker_positions của daily_nav_snapshot
    # (import trong hàm — daily_nav_snapshot import ngược lại module này cũng ở function
    # level nên không tạo vòng import).
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from daily_nav_snapshot import broker_positions
        live_pos = broker_positions(args.account, args.account_no)
    except Exception as e:
        print(f"⚠️ Không kiểm tra được P&L coverage (broker_positions lỗi: {e})",
              file=sys.stderr)
        live_pos = None
    cov_warns, legacy_tickers = pnl_coverage_warnings(
        [p["ticker"] for p in positions], live_pos)
    warnings.extend(cov_warns)
    for w in cov_warns:
        print(f"⚠️ {w}", file=sys.stderr)

    result = {
        "account": args.account,
        "dates_included": dates,
        "asof": args.asof,
        "source": "dnse_raw (broker-native averagePrice/fillQuantity), cross-checked vs journal FILL events",
        "verified": not any(w.startswith("WARN qty") for w in warnings),
        "pnl_coverage_complete": (live_pos is not None and not legacy_tickers),
        "legacy_positions_excluded_from_pnl": legacy_tickers,
        "warnings": warnings,
        "positions": sorted(positions, key=lambda p: -p["unrealized_pnl"]),
        "total_cost_value": total_cost,
        "total_mtm_value": total_mtm,
        "total_unrealized_pnl": total_mtm - total_cost,
    }

    out_path = args.out or os.path.join(
        EXEC_DIR, f"verified_snapshot_{args.account}_{args.asof}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"== Verified snapshot: {args.account} as of {args.asof} ==")
    print(f"Nguồn: {result['source']}")
    print(f"Verified (không có lệch số lượng giữa broker vs journal): {result['verified']}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} cảnh báo:")
        for w in warnings:
            print(" -", w)
    print()
    for p in result["positions"]:
        print(f"{p['ticker']:6s} qty={p['qty']:7.0f} true_cost={p['true_avg_cost']:>10,.0f} "
              f"mtm_px={p['mtm_price']:>9,.0f} PnL={p['unrealized_pnl']:>+14,.0f} "
              f"({p['unrealized_pnl_pct']:+.2f}%)")
    print()
    print(f"TOTAL cost basis (true): {total_cost:>16,.0f}")
    print(f"TOTAL mark-to-market:    {total_mtm:>16,.0f}")
    print(f"Unrealized P&L:          {total_mtm-total_cost:>+16,.0f}")
    print(f"\nGhi ra: {out_path}")

    if not result["verified"]:
        print("\n❌ CÓ LỆCH SỐ LƯỢNG GIỮA 2 NGUỒN ĐỘC LẬP — KHÔNG dùng số liệu này để viết báo cáo "
              "cho đến khi điều tra rõ nguyên nhân.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
