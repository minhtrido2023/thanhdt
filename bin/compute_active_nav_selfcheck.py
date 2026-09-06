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
import importlib.util
import os
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
if fails:
    print(f"❌ {len(fails)} FAILED: {fails}")
    sys.exit(1)
print("✅ ALL CHECKS PASS")
