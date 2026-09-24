# -*- coding: utf-8 -*-
"""Self-check cho bản vá cơ sở tiền của `compute_active_nav.py` (job Taylor_20260810_004252).

BUG ĐÃ SỬA (§cash trong docstring của script): cash lấy từ `DNSEBroker.get_cash()` =
`availableCash` — tiền TIÊU ĐƯỢC NGAY, không gồm tiền bán chưa settle T+2 / cổ tức phải thu,
và không trừ nợ margin. Với active_nav (mẫu của mọi phép sizing) điều đó khai THIẾU NAV đúng
bằng lượng tiền đang trên đường về: SpaceX 2026-08-09 762.476.143đ vs NAV thật ~961.311.265đ.
Sau vá: cash = `totalCash − totalDebt`, fail-closed qua 3 guard tái dùng từ `park_holdings`.

MỌI CA ĐỀU CHẠY QUA HÀM THẬT `compute_active_nav.cash_basis()` — không có ca nào chỉ khẳng
định suông. Với mỗi guard "chặn được", có ca CHỨNG MINH NGƯỢC: cùng payload nhưng gỡ đúng
điều kiện gây lỗi thì hàm trả số bình thường (nếu không, PASS chỉ chứng minh hàm luôn None).

Không chạm DNSE / BQ / bus / file production. Chạy: python3 mike/bin/compute_active_nav_selfcheck.py
"""
import glob
import importlib.util
import os
import subprocess
import sys

WC = "/home/trido/thanhdt/WorkingClaude"
MIKE_BIN = os.path.join(WC, "mike", "bin")

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


can = load_module("_sc_compute_active_nav", os.path.join(MIKE_BIN, "compute_active_nav.py"))


def stock(**kw):
    """Payload `balances` thật của DNSE: [{"stock": {...}, "derivative": {...}}]."""
    return [{"stock": kw, "derivative": {}}]


# Số THẬT, đọc từ DNSE SpaceX 2026-08-09 19:10 (dẫn trong §cash) — dùng làm ca vàng.
SPACEX_0809 = dict(totalCash=203_656_265, totalDebt=0, availableCash=4_821_143,
                   cashDividendReceiving=0, depositInterest=318)

print("A. Công thức cơ sở — totalCash − totalDebt, KHÔNG phải availableCash")
v, d = can.cash_basis(stock(**SPACEX_0809))
check("A1 ca vàng SpaceX 08-09: cash = totalCash (203.656.265), KHÔNG availableCash (4.821.143)",
      v == 203_656_265 and d["reason"] is None and d["cash_basis"] == "totalCash-totalDebt",
      f"v={v:,.0f}" if v is not None else f"v=None ({d['reason']})")

v, d = can.cash_basis(stock(totalCash=500_000_000, totalDebt=120_000_000,
                            availableCash=80_000_000, depositInterest=1))
check("A2 account có nợ margin: TRỪ totalDebt (500tr − 120tr = 380tr)", v == 380_000_000,
      f"v={v}")

v, _ = can.cash_basis(stock(totalCash=0, totalDebt=0, availableCash=0, depositInterest=0)
                      )
check("A2b nợ > tiền (margin call) vẫn trả số ÂM, không kẹp về 0 — kẹp = giấu mất rủi ro",
      can.cash_basis(stock(totalCash=10_000_000, totalDebt=90_000_000,
                           availableCash=0, depositInterest=1))[0] == -80_000_000)

# `availableCash` KHÔNG được có mặt trong công thức dưới bất kỳ hình thức nào: ba payload
# khác nhau CHỈ ở availableCash phải cho CÙNG một kết quả.
vals = {can.cash_basis(stock(totalCash=300_000_000, totalDebt=0, availableCash=ac,
                             depositInterest=1))[0]
        for ac in (0, 1_000_000, 300_000_000)}
check("A3 đổi riêng availableCash KHÔNG làm đổi kết quả (chứng minh nó đã ra khỏi công thức)",
      vals == {300_000_000}, f"vals={vals}")

v, d = can.cash_basis(stock(totalCash=12_272_672, totalDebt=0, availableCash=5_818_854,
                            cashDividendReceiving=6_453_500, depositInterest=318))
check("A4 ZaloPay 08-07: hằng đẳng thức 5.818.854 + 6.453.500 + 318 = 12.272.672 = totalCash",
      v == 12_272_672 and d["cash_dividend_receiving_vnd"] == 6_453_500,
      f"v={v}")

print()
print("B. Guard fail-closed — tái dùng nguyên vẹn từ park_holdings (3 vòng quant-skeptic 08-09)")
# B1 — block `stock` TOÀN 0 (sự cố thật DNSE 2026-07-27, cả 2 bản đọc 19:04:59 và 19:10:20).
v, d = can.cash_basis(stock(totalCash=0, totalDebt=0, availableCash=0,
                            depositInterest=0, cashDividendReceiving=0))
check("B1 block stock toàn 0 ⇒ None + nêu lý do (KHÔNG trả 0đ như tiền thật)",
      v is None and "TOÀN SỐ 0" in (d["reason"] or ""), f"reason={d['reason']}")

# B2 — lỗi feed chỉ ăn phần tiền, depositInterest còn sống ⇒ B1 KHÔNG bắt được.
v, d = can.cash_basis(stock(totalCash=0, totalDebt=0, availableCash=0, depositInterest=318))
check("B2 chỉ 3 field tiền = 0 (depositInterest≠0 nên guard B1 mù) ⇒ vẫn None",
      v is None and d["reason"] is not None, f"reason={d['reason']}")

# B3 — lỗi ăn ĐÚNG 2/3 field: B1 và B2 đều mù, chỉ bất biến kế toán cứu.
v, d = can.cash_basis(stock(totalCash=0, totalDebt=0, availableCash=5_000_000,
                            depositInterest=318))
check("B3 totalCash 0 < availableCash 5tr ⇒ vi phạm bất biến ⇒ None (ca lọt qua B1+B2)",
      v is None and "bất biến" in (d["reason"] or ""), f"reason={d['reason']}")

# B4/B5 — thiếu field hẳn (DNSE đổi schema / lỗi parse) ⇒ None, không suy ra từ field khác.
for miss in ("totalCash", "totalDebt"):
    kw = dict(SPACEX_0809)
    kw.pop(miss)
    v, d = can.cash_basis(stock(**kw))
    check(f"B4 thiếu `{miss}` ⇒ None, KHÔNG suy ra từ availableCash",
          v is None and miss in (d["reason"] or ""), f"reason={d['reason']}")

v, d = can.cash_basis([])
check("B5 payload rỗng (API lỗi) ⇒ None, không nổ exception", v is None and d["reason"])

print()
print("C. CHỨNG MINH NGƯỢC — mỗi guard chặn đúng CÁI NÓ NHẮM, không phải chặn tất")
# Gỡ đúng điều kiện gây lỗi của từng ca B ⇒ phải trả số bình thường trở lại. Không có nhóm C
# này thì mọi PASS ở B cũng đúng với một hàm `return None, {...}` vô điều kiện.
v, _ = can.cash_basis(stock(totalCash=1, totalDebt=0, availableCash=0,
                            depositInterest=0, cashDividendReceiving=0))
check("C1 B1 nhưng totalCash=1 (block không còn toàn 0) ⇒ trả 1, không chặn", v == 1)
v, _ = can.cash_basis(stock(totalCash=1, totalDebt=0, availableCash=0, depositInterest=318))
check("C2 B2 nhưng totalCash=1 ⇒ trả 1, không chặn", v == 1)
v, _ = can.cash_basis(stock(totalCash=5_000_000, totalDebt=0, availableCash=5_000_000,
                            depositInterest=318))
check("C3 B3 nhưng totalCash == availableCash (bất biến THOẢ, dạng ≥) ⇒ trả 5tr, không chặn",
      v == 5_000_000)
v, _ = can.cash_basis(stock(**SPACEX_0809))
check("C4 B4 nhưng đủ field ⇒ trả số bình thường", v == 203_656_265)

print()
print("D. Hình dạng payload — balances có/không bọc `stock`, list hay dict")
for label, bal in (("list bọc stock", stock(**SPACEX_0809)),
                   ("dict bọc stock", {"stock": dict(SPACEX_0809)}),
                   ("dict phẳng", dict(SPACEX_0809)),
                   ("list phẳng", [dict(SPACEX_0809)])):
    v, d = can.cash_basis(bal)
    check(f"D {label} ⇒ cùng kết quả 203.656.265", v == 203_656_265, f"v={v}")

print()
print("E. RANH GIỚI — bản vá KHÔNG được đụng đường sức-mua-thực-thi")
sys.path.insert(0, WC)
from trading_bot.brokers import DNSEBroker   # noqa: E402
import inspect  # noqa: E402
src_get_cash = inspect.getsource(DNSEBroker.get_cash)
check("E1 DNSEBroker.get_cash() VẪN ưu tiên `availablecash` (check_plan_funding/executor "
      "hỏi sức mua tức thời, không phải NAV — sửa nó = nới lỏng gate tiền)",
      "availablecash" in src_get_cash and src_get_cash.index("availablecash")
      < src_get_cash.index("totalcash"))

src_can = open(os.path.join(MIKE_BIN, "compute_active_nav.py"), encoding="utf-8").read()
# Kiểm bằng AST, KHÔNG bằng chuỗi: docstring §cash CÓ nhắc `get_cash()` như văn xuôi giải
# thích vì sao không dùng nó — grep chuỗi sẽ báo động giả trên chính lời giải thích đó.
import ast  # noqa: E402
_calls = {n.func.attr for n in ast.walk(ast.parse(src_can))
          if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
check("E2 compute_active_nav KHÔNG còn LỆNH GỌI get_cash() nào (kiểm bằng AST) — đường cũ cắt hẳn",
      "get_cash" not in _calls, f"calls={sorted(_calls)}")

src_jit = open(os.path.join(MIKE_BIN, "compute_jit_unpark.py"), encoding="utf-8").read()
check("E3 compute_jit_unpark (L2) VẪN dùng availableCash — cố ý, hỏi 'tiêu được ngay bao nhiêu'",
      "availableCash" in src_jit or "cash_available" in src_jit)

print()
print("F. Fail-closed đến tận đầu ra — None PHẢI thoát mã 4, KHÔNG ghi đè file cũ")
# Đọc chính nguồn: nhánh `cash is None` phải sys.exit trước mọi lệnh mở file ghi.
body = src_can[src_can.index("def main("):]
i_none, i_write = body.index("if cash is None:"), body.index("json.dump(")
check("F1 nhánh `cash is None` nằm TRƯỚC lệnh ghi file trong main()", i_none < i_write)
check("F2 nhánh đó thoát bằng sys.exit(4), không tiếp tục",
      "sys.exit(4)" in body[i_none:i_none + 900])
check("F3 KHÔNG có fallback âm thầm về availableCash trong nhánh lỗi",
      "cash_available" not in body[i_none:i_none + 900].replace(
          "availableCash` (xem §cash", ""))

print()
print("G. Off-book staleness — `_dt_stale` (code-quality-weekly 2026-09-06: NameError khi "
      "manual_offbook_assets_vnd != 0 + asof set, dormant vì 2 account live đang để 0)")
check("G1 `_dt_stale` là module `datetime` thật (không phải biến chưa import)",
      hasattr(can, "_dt_stale") and can._dt_stale.__name__ == "datetime")
_g2_ns = {"_dt_stale": getattr(can, "_dt_stale", None)}
try:
    exec(
        "age_days = (_dt_stale.date.fromisoformat('2026-09-06') - "
        "_dt_stale.date.fromisoformat('2026-08-01')).days",
        _g2_ns,
    )
    _g2_ok, _g2_detail = _g2_ns["age_days"] == 36, f"age_days={_g2_ns['age_days']}"
except (NameError, AttributeError) as e:
    _g2_ok, _g2_detail = False, f"{type(e).__name__}: {e}"
check("G2 tính age_days cho off-book asof KHÔNG NameError (compute_active_nav.py:~249)",
      _g2_ok, _g2_detail)

print()
print("H. Account KHÔNG vị thế VẪN ghi file (code-quality 2026-09-13 compute_active_nav.py:269)")
# Chạy main() THẬT với DNSE/profile giả + --out file tạm. Trước vá: `return` sớm ⇒ không có
# file ⇒ active_nav_{account}.json CŨ sống tiếp tới 5 ngày ở consumer. Nhưng DNSE CÓ trả
# positions rỗng tạm thời (arch-review 2026-09-13) ⇒ file trước còn cổ phiếu thì phải chặn.
import json as _json  # noqa: E402
import shutil as _shutil  # noqa: E402
import tempfile as _tempfile  # noqa: E402
_h_tmp = _tempfile.mkdtemp(prefix="can_sc_")
_h_out = os.path.join(_h_tmp, "active_nav_SELFCHK.json")
_h_cash, _h_detail = can.cash_basis(stock(totalCash=100_000_000, totalDebt=0,
                                          availableCash=100_000_000, depositInterest=1))


def _h_no_prices(*a, **k):
    raise AssertionError("resolve_prices bị gọi với danh mục rỗng")


def _h_run(prev=None, extra=()):
    """Chạy main() với 0 vị thế; prev = nội dung file active_nav lần trước (None = chưa có).
    Trả (file sau khi chạy hoặc None, mã exit hoặc None, lỗi khác)."""
    if os.path.exists(_h_out):
        os.remove(_h_out)
    if prev is not None:
        _json.dump(prev, open(_h_out, "w", encoding="utf-8"))
    saved = (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices, sys.argv)
    can.get_account_profile = lambda label: {"account_id": "SC", "manual_offbook_assets_vnd": 7_000_000}
    can.live_balance_and_positions = lambda aid, label: (_h_cash, {}, _h_detail, 5_000_000.0)
    can.resolve_prices = _h_no_prices
    sys.argv = ["compute_active_nav.py", "--account", "SELFCHK", "--out", _h_out, *extra]
    code, err = None, None
    try:
        can.main()
    except SystemExit as e:
        code = e.code
    except BaseException as e:  # noqa: BLE001 — lỗi nào cũng phải thành FAIL có tên
        err = f"{type(e).__name__}: {e}"
    finally:
        (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices,
         sys.argv) = saved
    res = _json.load(open(_h_out, encoding="utf-8")) if os.path.exists(_h_out) else None
    return res, code, err


try:
    _h_res, _h_code, _h_err = _h_run()
    check("H1 0 vị thế, chưa có file trước (account mới) ⇒ main() GHI file, không exit/exception",
          _h_res is not None and _h_code is None and _h_err is None, f"code={_h_code} err={_h_err}")
    check("H2 total_nav = active_nav = cash 100tr + egg 5tr + offbook 7tr = 112tr, positions rỗng",
          bool(_h_res) and _h_res["total_nav"] == 112_000_000 and _h_res["active_nav"] == 112_000_000
          and _h_res["positions"] == [] and _h_res["total_stock_value"] == 0,
          f"res={ {k: _h_res.get(k) for k in ('total_nav', 'active_nav', 'positions')} if _h_res else None}")
    check("H3 computed_at = hôm nay ICT (consumer kiểm tươi theo nội dung)",
          bool(_h_res) and _h_res["computed_at"] == can.today_ict().isoformat())

    _h_prev = {"computed_at": "2026-09-11", "total_stock_value": 900_000_000.0, "active_nav": 1e9}
    _h_res, _h_code, _h_err = _h_run(prev=_h_prev)
    check("H4 0 vị thế nhưng file trước còn 900tr cổ phiếu (DNSE trả rỗng tạm thời) ⇒ exit 5, "
          "file cũ GIỮ NGUYÊN", _h_code == 5 and _h_res == _h_prev and _h_err is None,
          f"code={_h_code} err={_h_err}")
    _h_res, _h_code, _h_err = _h_run(prev=_h_prev, extra=("--confirm-flat",))
    check("H5 CHỨNG MINH NGƯỢC H4: cùng file trước + --confirm-flat ⇒ ghi 112tr (bán sạch thật)",
          _h_code is None and bool(_h_res) and _h_res["total_nav"] == 112_000_000,
          f"code={_h_code} err={_h_err}")
    _h_res, _h_code, _h_err = _h_run(prev={"computed_at": "2026-09-11", "total_stock_value": 0})
    check("H6 file trước cũng 0 cổ phiếu ⇒ ghi bình thường, không đòi --confirm-flat",
          _h_code is None and bool(_h_res) and _h_res["total_nav"] == 112_000_000,
          f"code={_h_code} err={_h_err}")
finally:
    _shutil.rmtree(_h_tmp, ignore_errors=True)

print()
print("I. Giá BQ theo NGÀY CỦA TỪNG MÃ (code-quality 2026-09-13 compute_active_nav.py:171)")
_i_sql = can.bq_close_sql(["HPG", "AAA", "FPT"], "2026-09-11")
check("I1 SQL chọn phiên mới nhất THEO TỪNG MÃ, không còn subquery MAX của mã đầu alphabet",
      "PARTITION BY t.ticker" in _i_sql and "t2." not in _i_sql and "'AAA' AND" not in _i_sql,
      _i_sql.strip().replace("\n", " "))
check("I2 --asof giữ nguyên: lọc t.time <= asof", "t.time <= '2026-09-11'" in _i_sql)
check("I3 không --asof ⇒ không lọc ngày", "t.time <=" not in can.bq_close_sql(["FPT"]))
# Mã ĐẦU alphabet (AAA) ngừng giao dịch từ 09-05: trước vá cả danh mục lấy giá 09-05.
_i_px, _i_lag, _i_new = can.parse_close_rows([
    {"ticker": "AAA", "Close": "9000", "time": "2026-09-05"},
    {"ticker": "FPT", "Close": "72700", "time": "2026-09-11"},
    {"ticker": "HPG", "Close": "21300", "time": "2026-09-11"}])
check("I4 mỗi mã giữ giá của CHÍNH nó; AAA tụt ngày bị gọi tên, không bị bỏ",
      _i_px == {"AAA": 9000.0, "FPT": 72700.0, "HPG": 21300.0}
      and _i_lag == {"AAA": "2026-09-05"} and _i_new == "2026-09-11",
      f"px={_i_px} lag={_i_lag}")
check("I5 rows rỗng ⇒ không nổ", can.parse_close_rows([]) == ({}, {}, None))

print()
print("J. §excluded_dividend — cổ tức phải thu mã excluded loại khỏi active_nav tới khi tiền THẬT "
      "về (Option B, user quyết 2026-09-19, ZaloPay DGC 80tr/2026-09-25; bản vá vòng 2 arch-review "
      "2026-09-19: tín hiệu dừng loại là cash_dividend_receiving_vnd tự hạ, KHÔNG phải ngày)")
DGC_CFG = [{"ticker": "DGC", "amount_vnd": 80_000_000, "expected_arrival_date": "2026-09-25"}]

p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 80_000_000, "2026-09-19")
check("J1 ca thật ZaloPay 09-19: trước ngày dự kiến, còn báo đủ 80tr ⇒ loại đủ, overdue=False",
      p == 80_000_000 and d == [{"ticker": "DGC", "amount_vnd": 80_000_000,
                                 "expected_arrival_date": "2026-09-25", "overdue": False}],
      f"p={p} d={d}")

# J2 — R1 (arch-review 2026-09-19): ĐÚNG/SAU ngày dự kiến mà DNSE VẪN báo đủ 80tr (tiền về TRỄ)
# ⇒ PHẢI tiếp tục loại (không được tự ý ngừng theo lịch — đó chính là bug bản đầu tái lập).
p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 80_000_000, "2026-09-25")
check("J2 ĐÚNG ngày dự kiến nhưng vẫn báo đủ 80tr (tiền CHƯA về thật) ⇒ VẪN loại, overdue=True",
      p == 80_000_000 and d[0]["overdue"] is True, f"p={p} d={d}")

p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 80_000_000, "2026-09-30")
check("J3 SAU ngày dự kiến 5 hôm, DNSE VẪN báo đủ 80tr ⇒ VẪN loại — không tái lập bug gốc "
      "(active_nav không được tự phồng lại chỉ vì qua lịch)", p == 80_000_000 and d[0]["overdue"])

# J4 — CHỨNG MINH NGƯỢC J2/J3: tín hiệu dừng loại là chính remaining tụt xuống 0 (tiền đã settle
# thật), không phải ngày — dù asof đã qua rất xa expected_arrival_date.
p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 0, "2026-09-30")
check("J4 SAU ngày dự kiến VÀ DNSE đã hạ receivable về 0 (tiền đã về thật) ⇒ hết loại, p=0",
      p == 0 and d == [], f"p={p} d={d}")

p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 80_000_000, "2026-09-01")
check("J5 rất sớm trước ngày dự kiến vẫn loại đủ 80tr, overdue=False", p == 80_000_000
      and d[0]["overdue"] is False)

# J6 — KẸP bằng cash_dividend_receiving_vnd thật: tiền đã về MỘT PHẦN (DNSE tự hạ field xuống
# dưới 80tr) ⇒ không được loại quá số đang thực sự treo (đúng cả trước lẫn sau ngày dự kiến).
p, d = can.excluded_dividend_pending({"DGC"}, DGC_CFG, 30_000_000, "2026-09-19")
check("J6 cash_dividend_receiving hiện chỉ còn 30tr (thấp hơn config 80tr) ⇒ kẹp ở 30tr, "
      "KHÔNG trừ quá số treo thật", p == 30_000_000 and d[0]["amount_vnd"] == 30_000_000,
      f"p={p} d={d}")

# J7 — mã KHÔNG thuộc excluded_tickers của lần gọi này (vd account khác/scope khác) ⇒ bỏ qua
# entry đó dù config vẫn còn, tránh loại nhầm dividend của mã đang được quản lý chủ động.
p, d = can.excluded_dividend_pending(set(), DGC_CFG, 80_000_000, "2026-09-19")
check("J7 ticker KHÔNG nằm trong excluded_tickers truyền vào ⇒ bỏ qua entry, p=0", p == 0 and d == [])

# J8 — nhiều entry chia sẻ CÙNG một field tổng `remaining` (DNSE không tách theo mã, đúng giới
# hạn nêu trong docstring): TCM coi như đã settle thật (remaining chỉ còn đúng phần DGC) ⇒ entry
# DGC (đứng trước trong list) ăn hết remaining, TCM không còn gì để trừ dù vẫn nằm trong config.
MIXED_CFG = [{"ticker": "DGC", "amount_vnd": 80_000_000, "expected_arrival_date": "2026-09-25"},
            {"ticker": "TCM", "amount_vnd": 10_000_000, "expected_arrival_date": "2026-09-10"}]
p, d = can.excluded_dividend_pending({"DGC", "TCM"}, MIXED_CFG, 80_000_000, "2026-09-19")
check("J8 remaining=80tr (đúng bằng phần DGC) ⇒ DGC ăn hết, TCM không còn gì để trừ dù còn config",
      p == 80_000_000 and len(d) == 1 and d[0]["ticker"] == "DGC", f"p={p} d={d}")

# J9 — config rỗng/None (SpaceX, RocketX...) ⇒ không đổi hành vi cũ, p luôn 0.
check("J9 config rỗng ⇒ p=0 (account không khai excluded_dividend_receivable không bị ảnh hưởng)",
      can.excluded_dividend_pending({"DGC"}, [], 80_000_000, "2026-09-19") == (0.0, [])
      and can.excluded_dividend_pending({"DGC"}, None, 80_000_000, "2026-09-19") == (0.0, []))

# J10 — R3 (arch-review 2026-09-19): expected_arrival_date sai định dạng PHẢI nổ rõ, không được
# âm thầm loại vĩnh viễn (đo thật trong review: '25/09/2026'/'2026-9-25'/'tháng 9' đều lọt qua so
# sánh chuỗi thô của bản đầu và loại 80tr mãi mãi).
for _bad_date in ("25/09/2026", "2026-9-25", "tháng 9", "9999-99-99"):
    _bad_cfg = [{"ticker": "DGC", "amount_vnd": 80_000_000, "expected_arrival_date": _bad_date}]
    try:
        can.excluded_dividend_pending({"DGC"}, _bad_cfg, 80_000_000, "2026-09-19")
        check(f"J10 expected_arrival_date sai định dạng {_bad_date!r} PHẢI raise ValueError", False)
    except ValueError as e:
        check(f"J10 expected_arrival_date sai định dạng {_bad_date!r} raise ValueError rõ ràng",
              "expected_arrival_date" in str(e), f"msg={e}")

# J11 — entry không phải dict (config hỏng/tự chế) ⇒ raise rõ, không AttributeError mù.
try:
    can.excluded_dividend_pending({"DGC"}, ["DGC"], 80_000_000, "2026-09-19")
    check("J11 entry không phải dict PHẢI raise ValueError", False)
except ValueError as e:
    check("J11 entry không phải dict raise ValueError rõ ràng (không phải AttributeError mù)",
          "không phải dict" in str(e), f"msg={e}")

# J12 — entry thiếu expected_arrival_date hẳn (None/rỗng) ⇒ vẫn loại được (overdue luôn False,
# không có ngày để so), không bắt buộc phải khai ngày mới dùng được cơ chế.
p, d = can.excluded_dividend_pending({"DGC"}, [{"ticker": "DGC", "amount_vnd": 80_000_000}],
                                     80_000_000, "2026-09-19")
check("J12 entry không khai expected_arrival_date ⇒ vẫn loại, overdue=False (không có ngày để so)",
      p == 80_000_000 and d[0]["overdue"] is False and d[0]["expected_arrival_date"] is None,
      f"p={p} d={d}")

# J13 — end-to-end qua main() thật: 1 vị thế excluded, cash chứa 80tr receivable của mã đó,
# asof hôm nay < expected_arrival_date ⇒ active_nav phải THIẾU đúng 80tr so với total_nav (trừ
# excluded_mv); dùng --asof cố định để không phụ thuộc ngày hệ thống chạy selfcheck.
_j_tmp = _tempfile.mkdtemp(prefix="can_sc_j_")
_j_out = os.path.join(_j_tmp, "active_nav_JSELFCHK.json")
_j_cash80, _j_detail80 = can.cash_basis(stock(totalCash=200_000_000, totalDebt=0,
                                              availableCash=120_000_000, depositInterest=1,
                                              cashDividendReceiving=80_000_000))
_j_cash0, _j_detail0 = can.cash_basis(stock(totalCash=200_000_000, totalDebt=0,
                                            availableCash=120_000_000, depositInterest=1,
                                            cashDividendReceiving=0))
try:
    saved_j = (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices, sys.argv)
    can.get_account_profile = lambda label: {
        "account_id": "JSC", "excluded_tickers": ["DGC"],
        "excluded_dividend_receivable": [{"ticker": "DGC", "amount_vnd": 80_000_000,
                                          "expected_arrival_date": "2026-09-25"}]}
    can.resolve_prices = lambda tickers, asof: ({"DGC": 50_000}, {"DGC": "bq_close"}, None)

    can.live_balance_and_positions = lambda aid, label: (
        _j_cash80, {"DGC": {"total": 1000}}, _j_detail80, 0.0)
    sys.argv = ["compute_active_nav.py", "--account", "JSELFCHK", "--out", _j_out,
               "--asof", "2026-09-19"]
    can.main()
    _j_res = _json.load(open(_j_out, encoding="utf-8"))
    # total_nav = cash 200tr + mv(DGC) 1000*50000=50tr = 250tr; excluded_mv = 50tr (DGC excluded)
    # ⇒ trước bản vá active_nav = 200tr; sau bản vá phải trừ thêm 80tr receivable ⇒ 120tr.
    check("J13 end-to-end main(): active_nav = 200tr − 80tr receivable = 120tr (KHÔNG phải 200tr)",
          _j_res["active_nav"] == 120_000_000 and _j_res["total_nav"] == 250_000_000
          and _j_res["excluded_dividend_receivable_pending_vnd"] == 80_000_000,
          f"active_nav={_j_res.get('active_nav')} total_nav={_j_res.get('total_nav')}")

    # J14 — R1 end-to-end: asof QUA ngày dự kiến nhưng DNSE VẪN báo đủ 80tr (cash80, không đổi)
    # ⇒ active_nav PHẢI VẪN 120tr, KHÔNG được tự phồng lại về 200tr chỉ vì qua lịch.
    sys.argv[-1] = "2026-09-30"
    can.main()
    _j_res2 = _json.load(open(_j_out, encoding="utf-8"))
    check("J14 R1: asof qua ngày dự kiến NHƯNG receivable vẫn 80tr ⇒ active_nav VẪN 120tr "
          "(không tái lập bug gốc)",
          _j_res2["active_nav"] == 120_000_000
          and _j_res2["excluded_dividend_receivable_pending_vnd"] == 80_000_000
          and _j_res2["excluded_dividend_receivable_detail"][0]["overdue"] is True,
          f"active_nav={_j_res2.get('active_nav')}")

    # J15 — CHỨNG MINH NGƯỢC J13/J14: tiền THẬT SỰ về (DNSE hạ cashDividendReceiving về 0)
    # ⇒ hết loại, active_nav = 200tr — không phụ thuộc asof có qua ngày dự kiến hay chưa.
    can.live_balance_and_positions = lambda aid, label: (
        _j_cash0, {"DGC": {"total": 1000}}, _j_detail0, 0.0)
    sys.argv[-1] = "2026-09-25"
    can.main()
    _j_res3 = _json.load(open(_j_out, encoding="utf-8"))
    check("J15 CHỨNG MINH NGƯỢC: DNSE hạ cashDividendReceiving về 0 ⇒ hết loại, active_nav = 200tr",
          _j_res3["active_nav"] == 200_000_000
          and _j_res3["excluded_dividend_receivable_pending_vnd"] == 0,
          f"active_nav={_j_res3.get('active_nav')}")
finally:
    (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices,
     sys.argv) = saved_j
    _shutil.rmtree(_j_tmp, ignore_errors=True)

print()
print("K. Ghi NGUYÊN TỬ ra `out_path` (§5 coding_guidelines, C2 arch-review vòng 7) — kill GIỮA "
      "lúc ghi tmp KHÔNG được làm mất/hỏng file NAV canonical của lần chạy trước. Ca này chạy "
      "main() trong SUBPROCESS RIÊNG (os._exit thật, không phải mock/exception) vì kill giữa "
      "chừng không mô phỏng được bằng try/except trong cùng tiến trình selfcheck.")
_k_tmp = _tempfile.mkdtemp(prefix="can_sc_k_")
_k_out = os.path.join(_k_tmp, "active_nav_KSELFCHK.json")
_k_good_prior = {"computed_at": "2026-09-20", "total_nav": 999_000_000.0,
                  "active_nav": 999_000_000.0, "total_stock_value": 999_000_000.0,
                  "positions": [], "marker": "GOOD_PRIOR_UNTOUCHED_BY_KILL"}
with open(_k_out, "w", encoding="utf-8") as _kf:
    _json.dump(_k_good_prior, _kf)
with open(_k_out, "rb") as _kf:
    _k_good_prior_bytes = _kf.read()

# Shim chạy trong subprocess riêng: monkeypatch `json.dump` bên trong compute_active_nav để
# ghi vài byte JSON DỞ DANG rồi `os._exit(137)` NGAY — mô phỏng kill -9 giữa lúc ghi tmp,
# TRƯỚC dòng `os.replace(tmp, out_path)`. Token PLACEHOLDER thay bằng `.replace()` (không
# `.format()`) vì thân shim có literal `{`/`}` của JSON — `.format()` sẽ nổ trên chúng.
_k_shim_src = '''\
import sys, os
sys.path.insert(0, MIKE_BIN_PLACEHOLDER)
import compute_active_nav as can


def _crashing_dump(obj, fp, **kw):
    fp.write('{"computed_at": "CORRUPT_PARTIAL_FROM_KILL_MID_WRITE')
    fp.flush()
    os.fsync(fp.fileno())
    os._exit(137)


can.json.dump = _crashing_dump
can.get_account_profile = lambda label: {"account_id": "KSC"}
can.live_balance_and_positions = lambda aid, label: (
    100000000.0, {}, {"reason": None, "cash_basis": "totalCash-totalDebt",
                       "cash_total_vnd": 100000000.0, "cash_debt_vnd": 0.0,
                       "cash_available_vnd": 100000000.0,
                       "cash_dividend_receiving_vnd": 0.0}, 0.0)
can.resolve_prices = lambda tickers, asof: ({}, {}, None)
sys.argv = ["compute_active_nav.py", "--account", "KSELFCHK", "--out", OUT_PATH_PLACEHOLDER,
            "--confirm-flat"]
try:
    can.main()
except SystemExit:
    pass
'''
_k_shim_path = os.path.join(_k_tmp, "_kill_shim.py")
with open(_k_shim_path, "w", encoding="utf-8") as _kf:
    _kf.write(_k_shim_src.replace("MIKE_BIN_PLACEHOLDER", repr(MIKE_BIN))
                          .replace("OUT_PATH_PLACEHOLDER", repr(_k_out)))

_k_proc = subprocess.run([sys.executable, _k_shim_path], capture_output=True, timeout=30)
check("K1 shim con THẬT SỰ crash bằng os._exit(137) (không lặng lẽ rơi vào nhánh khác)",
      _k_proc.returncode == 137,
      f"returncode={_k_proc.returncode} stderr={_k_proc.stderr.decode(errors='replace')[:300]}")

with open(_k_out, "rb") as _kf:
    _k_out_after_kill = _kf.read()
check("K2 file canonical KHÔNG bị hỏng/mất sau kill giữa lúc ghi tmp — byte-identical với "
      "bản TỐT của lần chạy trước (os.replace không hề chạy)",
      _k_out_after_kill == _k_good_prior_bytes,
      f"after_kill={_k_out_after_kill[:80]!r}")

_k_leftover_tmp = glob.glob(os.path.join(_k_tmp, "active_nav_KSELFCHK.json.*.tmp"))
check("K3 phần ghi dở nằm ở file TMP riêng (không phải out_path) — chứng minh cơ chế mkstemp "
      "+ os.replace thật sự tách 2 file, không ghi thẳng vào canonical",
      len(_k_leftover_tmp) == 1
      and open(_k_leftover_tmp[0], encoding="utf-8").read() == '{"computed_at": "CORRUPT_PARTIAL_FROM_KILL_MID_WRITE',
      f"leftover={_k_leftover_tmp}")

# K4 — CHỨNG MINH NGƯỢC K1-K3: chạy lại BÌNH THƯỜNG (không crash) trên CÙNG out_path, với
# tmp cũ còn sót lại từ vụ kill ⇒ lần chạy sau vẫn ghi thành công, không bị khoá/kẹt bởi tmp mồ côi.
saved_k = (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices, sys.argv)
try:
    can.get_account_profile = lambda label: {"account_id": "KSC"}
    can.live_balance_and_positions = lambda aid, label: (
        100_000_000.0, {}, {"reason": None, "cash_basis": "totalCash-totalDebt",
                             "cash_total_vnd": 100_000_000.0, "cash_debt_vnd": 0.0,
                             "cash_available_vnd": 100_000_000.0,
                             "cash_dividend_receiving_vnd": 0.0}, 0.0)
    can.resolve_prices = lambda tickers, asof: ({}, {}, None)
    sys.argv = ["compute_active_nav.py", "--account", "KSELFCHK", "--out", _k_out,
                "--confirm-flat"]
    can.main()
finally:
    (can.get_account_profile, can.live_balance_and_positions, can.resolve_prices,
     sys.argv) = saved_k
_k_res_recovered = _json.load(open(_k_out, encoding="utf-8"))
check("K4 CHỨNG MINH NGƯỢC: lần chạy BÌNH THƯỜNG sau đó (tmp mồ côi còn sót) vẫn ghi ĐÚNG "
      "(active_nav = cash 100tr, hết marker GOOD_PRIOR cũ) — kill lần trước không để lại khoá",
      _k_res_recovered.get("active_nav") == 100_000_000
      and _k_res_recovered.get("marker") is None,
      f"res={ {k: _k_res_recovered.get(k) for k in ('active_nav', 'marker')} }")
_shutil.rmtree(_k_tmp, ignore_errors=True)

print()
if fails:
    print(f"❌ {len(fails)} FAILED: {fails}")
    sys.exit(1)
print("✅ ALL CHECKS PASS")
