# -*- coding: utf-8 -*-
"""Self-check P5 — ghi 10 mức giá chờ (`kind="quote_l2"`) vào dnse_raw_<date>.jsonl.

Context (job Taylor_20260812_095213): DNSE G1 trả `quotes[].bid/offer` = list 10 mức
{price, quantity} nhưng `DNSEBroker.get_quote` vứt bỏ (chỉ giữ mức 1) ⇒ KHÔNG tồn tại dữ liệu
KL CHỜ để trả lời "thật sự có bao nhiêu hàng dưới trần". P5 = LOGGING THUẦN, không đổi hành vi
đặt lệnh, không thêm lời gọi API.

Rủi ro THẬT của việc này KHÔNG nằm ở logic ghi, mà ở chỗ `dnse_raw_<date>.jsonl` là file KẾ
TOÁN DÙNG CHUNG (§12): 15+ consumer quét toàn file để dựng NAV/cost-basis/park. Thêm một `kind`
mới mà một consumer nào đó KHÔNG lọc theo `kind` ⇒ hỏng báo cáo tiền thật. Vì vậy phần lớn file
này là **đối soát consumer trên dữ liệu THẬT**: chạy consumer trên bản sao file thật, rồi chạy
lại trên đúng file đó đã CHÈN bản ghi quote_l2, và đòi kết quả GIỐNG HỆT.

Run: /home/trido/thanhdt/wc_venv/bin/python quote_l2_logging_selfcheck.py   (exit 0 = pass)
"""
import glob
import importlib
import json
import os
import shutil
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "mike", "bin"))
from trading_bot.brokers import DNSEBroker  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


# Payload G1 THẬT (hình dạng theo dnse_api.latest_quote → _pick_board("quotes")).
QT = {"symbol": "TV1",
      "bid": [{"price": 20.2, "quantity": 300}, {"price": 20.1, "quantity": 1200},
              {"price": 20.0, "quantity": 5000}] + [{"price": 19.9 - i * 0.1, "quantity": 100 * i}
                                                    for i in range(1, 9)],
      "offer": [{"price": 20.3, "quantity": 400}, {"price": 20.4, "quantity": 900}],
      "time": "2026-08-12T10:00:00"}
RAW = {"symbol": "TV1", "matchPrice": 20300, "totalVolumeTraded": 39500}


def fresh_broker(tmp, symbol_log=None):
    b = DNSEBroker(account_id="0002023347", label="SpaceX")
    b._raw_log = os.path.join(tmp, "dnse_raw_2099-01-01.jsonl")
    return b


def read_log(path):
    if not os.path.exists(path):
        return []
    return [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]


# ================================================================ A. Ghi đúng nội dung
with tempfile.TemporaryDirectory() as tmp:
    os.environ["DNSE_L2_LOG_SEC"] = "0"      # tắt throttle để test nội dung
    b = fresh_broker(tmp)
    b._log_l2("TV1", QT, RAW)
    recs = read_log(b._raw_log)
    check("A1 ghi đúng 1 bản ghi", len(recs) == 1, f"{len(recs)}")
    r = recs[0]
    check("A2 kind = 'quote_l2' (kind MỚI, không đụng kind cũ)", r["kind"] == "quote_l2", r.get("kind"))
    check("A3 có account_no + account_label ở TOP-LEVEL (§12 — file dùng chung nhiều account)",
          r["account_no"] == "0002023347" and r["account_label"] == "SpaceX")
    p = r["payload"]
    check("A4 giữ ĐỦ 10 mức bid (payload thật có 11 mức → cắt đúng 10)",
          len(p["bids"]) == 10 and p["n_bid"] == 10, f"{p['n_bid']}")
    check("A5 giữ đủ mức offer thật có", len(p["offers"]) == 2 and p["n_offer"] == 2)
    check("A6 giá chuẩn hoá về VND (feed trả 20.2 nghìn → 20.200)",
          p["bids"][0]["price"] == 20200.0 and p["offers"][0]["price"] == 20300.0,
          f"{p['bids'][0]}, {p['offers'][0]}")
    check("A7 giữ nguyên KL từng mức (đây là thứ DUY NHẤT ta không có ở bất kỳ nguồn nào khác)",
          [lv["quantity"] for lv in p["bids"][:3]] == [300, 1200, 5000], f"{p['bids'][:3]}")
    check("A8 kèm mốc neo để join với tape (last + day_volume)",
          p["last"] == 20300 and p["day_volume"] == 39500)
    check("A9 KHÔNG có key 'resp'/'orders' — execution_quality_review.py là consumer DUY NHẤT "
          "không lọc theo kind, nó đọc đúng 2 key này trên MỌI bản ghi",
          "resp" not in p and "orders" not in p)

# ================================================================ B. Không bao giờ raise
with tempfile.TemporaryDirectory() as tmp:
    b = fresh_broker(tmp)
    BAD = [("B1 qt=None", None), ("B2 qt là list", [1, 2, 3]), ("B3 qt rỗng", {}),
           ("B4 bid không phải list", {"bid": "x", "offer": "y"}),
           ("B5 mức giá là số trần trụi", {"bid": [20.2, 20.1], "offer": [20.3]}),
           ("B6 mức giá thiếu quantity", {"bid": [{"price": 20.2}], "offer": []}),
           ("B7 quantity là chuỗi rác", {"bid": [{"price": 20.2, "quantity": "abc"}], "offer": []}),
           ("B8 mức giá là None", {"bid": [None, {"price": 20.2, "quantity": 100}], "offer": []})]
    for nm, qt in BAD:
        try:
            b._log_l2("TV1", qt, RAW)
            check(f"{nm} ⇒ không raise", True)
        except Exception as exc:
            check(f"{nm} ⇒ không raise", False, repr(exc))
    # payload rỗng hoàn toàn thì KHÔNG ghi gì (đừng làm nhiễu file kế toán)
    recs = read_log(b._raw_log)
    check("B9 payload không có mức nào ⇒ KHÔNG ghi bản ghi rỗng",
          all(r["payload"]["n_bid"] or r["payload"]["n_offer"] for r in recs), f"{len(recs)} bản ghi")
    # ghi log hỏng (đường dẫn không ghi được) cũng không được làm hỏng luồng quote
    b2 = fresh_broker(tmp)
    b2._raw_log = "/proc/khong-ghi-duoc/x.jsonl"
    try:
        b2._log_l2("TV1", QT, RAW)
        check("B10 không ghi được file ⇒ nuốt lỗi, KHÔNG làm hỏng get_quote", True)
    except Exception as exc:
        check("B10 không ghi được file ⇒ nuốt lỗi, KHÔNG làm hỏng get_quote", False, repr(exc))

# ================================================================ C. Throttle
with tempfile.TemporaryDirectory() as tmp:
    os.environ["DNSE_L2_LOG_SEC"] = "3600"
    b = fresh_broker(tmp)
    for _ in range(50):
        b._log_l2("TV1", QT, RAW)
    for _ in range(50):
        b._log_l2("DGC", QT, RAW)
    recs = read_log(b._raw_log)
    check("C1 throttle: 100 lời gọi (2 mã) ⇒ đúng 2 bản ghi", len(recs) == 2, f"{len(recs)}")
    check("C2 throttle theo TỪNG MÃ, không phải toàn cục",
          {r["payload"]["symbol"] for r in recs} == {"TV1", "DGC"})
    os.environ["DNSE_L2_LOG_SEC"] = "0"
    b2 = fresh_broker(tmp)
    b2._raw_log = os.path.join(tmp, "dnse_raw_nothrottle.jsonl")
    for _ in range(5):
        b2._log_l2("TV1", QT, RAW)
    check("C3 DNSE_L2_LOG_SEC=0 ⇒ ghi mọi lần (nút chỉnh độ phân giải khi cần)",
          len(read_log(b2._raw_log)) == 5)

# ================================================================ D. get_quote KHÔNG đổi hành vi
class _FakeClient:
    """Trả đúng hình dạng payload DNSE; đếm số lời gọi để chứng minh P5 không thêm request."""
    def __init__(self):
        self.calls = {"secdef": 0, "latest_trade": 0, "latest_quote": 0}

    def secdef(self, s, board_id=None):
        self.calls["secdef"] += 1
        return {"secdefs": [{"symbol": s, "ceiling": 23000, "floor": 17000, "refPrice": 20000}]}

    def latest_trade(self, s, board_id=None):
        self.calls["latest_trade"] += 1
        return {"trades": [{"matchPrice": 20300, "totalVolumeTraded": 39500}]}

    def latest_quote(self, s, board_id=None):
        self.calls["latest_quote"] += 1
        return {"quotes": [QT]}


with tempfile.TemporaryDirectory() as tmp:
    os.environ["DNSE_L2_LOG_SEC"] = "0"
    b = fresh_broker(tmp)
    b.client = _FakeClient()
    q = b.get_quote("TV1")
    check("D1 Quote vẫn dựng được bình thường", q is not None and q.ok())
    check("D2 Quote giữ ĐÚNG mức 1 như trước (bid/ask không đổi nghĩa)",
          q.bid == 20200.0 and q.ask == 20300.0, f"bid={q.bid} ask={q.ask}")
    check("D3 Quote vẫn có day_volume/last/trần/sàn", q.day_volume == 39500 and q.last == 20300
          and q.ceiling == 23000 and q.floor == 17000)
    calls = dict(b.client.calls)
    b._quote_cache.clear()
    b.get_quote("TV1")
    check("D4 P5 KHÔNG thêm lời gọi API nào: 1 lần fetch = ĐÚNG 1 latest_quote + 1 latest_trade, "
          "secdef vẫn cache cả phiên",
          b.client.calls == {"secdef": calls["secdef"],
                             "latest_trade": calls["latest_trade"] + 1,
                             "latest_quote": calls["latest_quote"] + 1},
          f"{b.client.calls} vs {calls}")
    l2 = [r for r in read_log(b._raw_log) if r["kind"] == "quote_l2"]
    check("D5 mỗi lần FETCH THẬT ghi 1 bản ghi L2 (cache 3s không ghi trùng)", len(l2) == 2, f"{len(l2)}")
    b.get_quote("TV1")      # trong TTL 3s → cache
    check("D6 lần gọi trúng cache KHÔNG ghi thêm (không có bản ghi trùng lặp vô nghĩa)",
          len([r for r in read_log(b._raw_log) if r["kind"] == "quote_l2"]) == 2)


# ================================================================ E. CONSUMER KHÔNG VỠ (§12)
# Đây là phần quan trọng nhất. Dùng file dnse_raw THẬT (có orders/balances/positions/ppse của
# CẢ 2 account), chèn quote_l2 xen kẽ, đòi mọi consumer ra kết quả GIỐNG HỆT.
#
# Hai cái bẫy của chính bộ test này, đã cắn thật khi viết và phải chống bằng assert riêng:
#   (1) So sánh hai kết quả RỖNG cũng "giống hệt nhau" ⇒ mọi check E* dưới đây đều kèm một
#       assert KHÔNG-RỖNG. Không có nó thì đường dẫn sai làm test xanh mà chẳng kiểm gì.
#   (2) Chọn `asof` = HÔM NAY làm `park_holdings.read_broker_snapshot` đi thẳng ra broker LIVE
#       thay vì đọc file ⇒ test không hề chạm dữ liệu mình chèn. Dùng ngày QUÁ KHỨ.
DATE = "2026-08-11"      # ngày QUÁ KHỨ, có đủ orders/positions/balances/ppse của cả 2 account
SRC = os.path.join(ROOT, "data", "execution_logs", f"dnse_raw_{DATE}.jsonl")
ACCTS = [("SpaceX", "0002023347"), ("ZaloPay", "0001743768")]

if not os.path.exists(SRC):
    check(f"E0 có file dnse_raw THẬT {DATE} để đối soát", False, "thiếu file")
else:
    check(f"E0 dùng file THẬT dnse_raw_{DATE}.jsonl ({os.path.getsize(SRC)//1024}KB)", True)

    def build(workdir, inject):
        """Dựng CÙNG cấu trúc thư mục thật (<root>/data/execution_logs/) để mọi consumer —
        kể cả loại nhận `workdir` (capit_episode) — trỏ đúng chỗ."""
        d = os.path.join(workdir, "data", "execution_logs")
        os.makedirs(d, exist_ok=True)
        dst = os.path.join(d, f"dnse_raw_{DATE}.jsonl")
        if not inject:
            shutil.copy(SRC, dst)
            return d, dst
        base = {"ts": f"{DATE}T10:00:00+07:00", "kind": "quote_l2",
                "payload": {"symbol": "TV1", "bids": [{"price": 20200.0, "quantity": 300}],
                            "offers": [{"price": 20300.0, "quantity": 400}],
                            "n_bid": 1, "n_offer": 1, "last": 20300, "day_volume": 39500,
                            "note": "P5"}}
        recs = []
        for label, acc in ACCTS:
            r = json.loads(json.dumps(base))
            r["account_no"], r["account_label"] = acc, label
            recs.append(r)
        with open(SRC, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as o:
            for i, ln in enumerate(f):
                o.write(json.dumps(recs[i % 2], ensure_ascii=False) + "\n")
                o.write(ln)
        return d, dst

    def same(a, b):
        return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)

    def nonempty(x):
        return bool(x) and (len(x) > 0 if hasattr(x, "__len__") else True)

    with tempfile.TemporaryDirectory() as w0, tempfile.TemporaryDirectory() as w1:
        d0, p0 = build(w0, False)
        d1, p1 = build(w1, True)
        n0, n1 = len(read_log(p0)), len(read_log(p1))
        check("E1 file 'sau' = file 'trước' + đúng số bản ghi L2 chèn vào", n1 == 2 * n0, f"{n0}→{n1}")

        # --- daily_nav_snapshot.latest_balance — cơ sở NAV (§25) ---
        dns = importlib.import_module("daily_nav_snapshot")
        res = {(lb, w): dns.latest_balance(p, acc)
               for lb, acc in ACCTS for w, p in (("before", p0), ("after", p1))}
        check("E2 daily_nav_snapshot.latest_balance — GIỐNG HỆT trước/sau, cả 2 account",
              all(same(res[(lb, "before")], res[(lb, "after")]) for lb, _ in ACCTS))
        check("E2b …và kết quả KHÔNG RỖNG (nếu rỗng thì E2 chỉ đang so 2 cái None)",
              all(nonempty(v) for v in res.values()))
        check("E2c …và 2 account ra 2 kết quả KHÁC nhau — bằng chứng vẫn lọc account đúng (§12: "
              "giống hệt nhau giữa 2 account = dấu hiệu đọc chung không lọc)",
              not same(res[("SpaceX", "after")], res[("ZaloPay", "after")]))

        # --- park_holdings.read_broker_snapshot — positions + 3 guard tiền ---
        ph = importlib.import_module("park_holdings")
        res = {(lb, w): ph.read_broker_snapshot(lb, acc, DATE, exec_dir=d)
               for lb, acc in ACCTS for w, d in (("before", d0), ("after", d1))}
        check("E3 park_holdings.read_broker_snapshot — GIỐNG HỆT trước/sau, cả 2 account",
              all(same(res[(lb, "before")], res[(lb, "after")]) for lb, _ in ACCTS))
        # trả (positions, cash_available, meta) — kiểm CẢ vị thế lẫn tiền đều không rỗng
        check("E3b …và có vị thế + tiền thật (không rỗng — nếu rỗng thì E3 chỉ so 2 cái trống)",
              all(nonempty(v[0]) and v[1] is not None for v in res.values()),
              str({k: (len(v[0]), v[1]) for k, v in res.items()}))
        check("E3c …và 2 account ra vị thế KHÁC nhau (vẫn lọc account đúng)",
              not same(res[("SpaceX", "after")][0], res[("ZaloPay", "after")][0]))

        # --- verify_account_snapshot.dnse_fill_events — cost-basis CANONICAL (§6) ---
        vas = importlib.import_module("verify_account_snapshot")
        res = {}
        for lb, acc in ACCTS:
            for w, d in (("before", d0), ("after", d1)):
                vas.EXEC_DIR = d
                res[(lb, w)] = vas.dnse_fill_events(acc, DATE)
        vas.EXEC_DIR = os.path.join(ROOT, "data", "execution_logs")     # trả lại, không để rò
        check("E4 verify_account_snapshot.dnse_fill_events — GIỐNG HỆT trước/sau, cả 2 account",
              all(same(res[(lb, "before")], res[(lb, "after")]) for lb, _ in ACCTS))
        check("E4b …và có fill thật để so (không rỗng)",
              all(nonempty(v) for v in res.values()),
              str({k: len(v or []) for k, v in res.items()}))

        # --- report_return_gate.broker_positions — cổng tỉ suất (§21) ---
        rrg = importlib.import_module("report_return_gate")
        res = {}
        for lb, acc in ACCTS:
            for w, d in (("before", d0), ("after", d1)):
                rrg.EXEC_DIR = d
                res[(lb, w)] = rrg.broker_positions(acc, DATE)
        rrg.EXEC_DIR = os.path.join(ROOT, "data", "execution_logs")
        check("E5 report_return_gate.broker_positions — GIỐNG HỆT trước/sau, cả 2 account",
              all(same(res[(lb, "before")], res[(lb, "after")]) for lb, _ in ACCTS))
        check("E5b …và có vị thế thật (không rỗng)", all(nonempty(v) for v in res.values()),
              str({k: len(v) for k, v in res.items()}))

        # --- capit_episode._raw_records — đọc theo kind, nhận workdir ---
        ce = importlib.import_module("capit_episode")
        ok, ne = True, True
        for lb, _ in ACCTS:
            for kind in ("orders", "positions", "balances"):
                a, b = ce._raw_records(w0, DATE, kind, lb), ce._raw_records(w1, DATE, kind, lb)
                ok = ok and same(a, b)
                ne = ne and nonempty(a)
        check("E6 capit_episode._raw_records (orders/positions/balances) — GIỐNG HỆT trước/sau", ok)
        check("E6b …và cả 3 kind × 2 account đều CÓ bản ghi (không so 2 list rỗng)", ne)
        check("E6c …và không kind nào nhặt nhầm quote_l2 vào kết quả",
              all(r["kind"] == "orders" for r in ce._raw_records(w1, DATE, "orders", "SpaceX"))
              and len(ce._raw_records(w1, DATE, "quote_l2", "SpaceX")) > 0)

        # --- execution_quality_review: consumer DUY NHẤT không lọc kind → kiểm chính predicate
        pl = [r for r in read_log(p1) if r["kind"] == "quote_l2"][0]["payload"]
        check("E7 execution_quality_review: bản ghi L2 không có payload['resp'] dạng dict và "
              "không có payload['orders'] dạng list ⇒ vòng lặp _ingest của nó bỏ qua sạch",
              not isinstance(pl.get("resp"), dict) and not (pl.get("orders") or []))

print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ tất cả PASS — P5 chỉ THÊM log, không đổi Quote/không thêm API call, "
      "và 6 consumer kế toán trên dữ liệu THẬT ra kết quả không đổi.")
