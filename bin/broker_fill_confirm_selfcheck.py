"""broker_fill_confirm_selfcheck.py — selfcheck cho leg 3 đối soát fill (statement DNSE).

Chạy: python3 mike/bin/broker_fill_confirm_selfcheck.py

Nguyên tắc (coding_guidelines §23 hệ luận 1 + skill verify-before-done): KHÔNG assert lên trạng
thái SỐNG. Mọi ca dùng fixture tự dựng trong tmpdir; chỉ ca cuối cùng đọc CSV thật 11-08-2026
và ca đó tự SKIP khi file không còn (để test không mốc theo thời gian).

Mỗi ca "chặn được" đều đi kèm ca CHỨNG MINH NGƯỢC (bỏ guard ⇒ thật sự sai) — không khẳng định
suông (§24).
"""
import json
import os
import shutil
import sys
import tempfile

WC_ROOT = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, os.path.join(WC_ROOT, "mike", "bin"))

from broker_fill_confirm import (  # noqa: E402
    _norm_acct, account_no_for, broker_csv_path, load_broker_fills, reconcile_lines,
)

PASS = FAIL = 0
FAILURES = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        FAILURES.append(f"{name} — {detail}")
        print(f"  ❌ {name} — {detail}")


CSV_HEADER = ("ngay_gd,loai_lenh,ma,tieu_khoan,khoi_luong,gia_khop,gia_tri_khop,"
              "ty_le_phi,phi_tra_so,phi_dnse,thue\n")


def make_root(rows, date_iso="2026-08-11", accounts=None):
    """Dựng 1 WC_ROOT giả với secrets + CSV statement."""
    root = tempfile.mkdtemp(prefix="bfc_selfcheck_")
    os.makedirs(os.path.join(root, "data", "execution_logs"))
    os.makedirs(os.path.join(root, "secrets"))
    accounts = accounts if accounts is not None else [
        {"label": "ZaloPay", "account_id": "0001743768"},
        {"label": "SpaceX", "account_id": "0002023347"},
    ]
    with open(os.path.join(root, "secrets", "trading_bot_accounts.json"), "w") as f:
        json.dump({"accounts": accounts}, f)
    if rows is not None:
        with open(broker_csv_path(root, date_iso), "w", encoding="utf-8") as f:
            f.write(CSV_HEADER)
            f.writelines(rows)
    return root


def row(ma, acct, qty, price, side="MUA", fee_so=100, fee_dnse=700, tax=0):
    val = qty * price
    return f"11/08/2026,{side},{ma},{acct},{qty},{price},{val},0.00097,{fee_so},{fee_dnse},{tax}\n"


print("=== 1. _norm_acct: bẫy mất số 0 dẫn đầu ===")
check("'0002023347' == 2023347 (int do pandas parse)", _norm_acct("0002023347") == _norm_acct(2023347))
check("'0002023347' == '2023347.0' (float)", _norm_acct("0002023347") == _norm_acct("2023347.0"))
check("hai tiểu khoản KHÁC nhau vẫn khác", _norm_acct("0001743768") != _norm_acct("0002023347"))
check("chuỗi toàn số 0 không thành rỗng", _norm_acct("0000") == "0")
# CHỨNG MINH NGƯỢC: so sánh chuỗi thô (không normalize) thì thật sự sai.
check("chứng minh ngược: so chuỗi thô '0002023347' != '2023347'", str("0002023347") != str(2023347))

print("\n=== 2. Đọc CSV: leading zero KHÔNG được mất khi qua pandas ===")
root = make_root([row("DRI", "0002023347", 3700, 13262), row("TV1", "0002023347", 100, 19800)])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("available=True", b.available, b.reason)
check("DRI buy = 3700", b.qty("DRI", "buy") == 3700, f"got {b.qty('DRI','buy')}")
check("TV1 buy = 100", b.qty("TV1", "buy") == 100, f"got {b.qty('TV1','buy')}")
check("mã không có trong statement → 0", b.qty("XYZ", "buy") == 0)
# CHỨNG MINH NGƯỢC: đọc không dtype=str thì tieu_khoan thành int và mất số 0.
import pandas as pd  # noqa: E402
_naive = pd.read_csv(broker_csv_path(root, "2026-08-11"))
check("chứng minh ngược: pd.read_csv mặc định LÀM MẤT số 0 dẫn đầu",
      str(_naive["tieu_khoan"].iloc[0]) == "2023347",
      f"got {_naive['tieu_khoan'].iloc[0]!r}")
shutil.rmtree(root)

print("\n=== 3. Lọc account: 1 file GỘP 2 tiểu khoản (§12) ===")
root = make_root([row("DRI", "0002023347", 3700, 13262), row("DRI", "0001743768", 1900, 13263),
                  row("TV1", "0002023347", 100, 19800)])
sx = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
zp = load_broker_fills("2026-08-11", "ZaloPay", root, allow_fetch=False)
check("SpaceX DRI = 3700 (không cộng nhầm ZaloPay)", sx.qty("DRI", "buy") == 3700, f"got {sx.qty('DRI','buy')}")
check("ZaloPay DRI = 1900", zp.qty("DRI", "buy") == 1900, f"got {zp.qty('DRI','buy')}")
check("hai account cho kết quả KHÁC nhau (§12 self-check)", sx.by_key != zp.by_key)
check("ZaloPay KHÔNG có TV1 (không khớp = không có dòng)", zp.qty("TV1", "buy") == 0)
shutil.rmtree(root)

print("\n=== 4. Fail-safe: thiếu file / rỗng / sai layout / sai ánh xạ account ===")
root = make_root(None)
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("thiếu CSV → available=False, KHÔNG raise", not b.available)
check("lý do nêu ĐỦ CẢ 2 khả năng (chưa gửi / phiên khớp 0 nên không bao giờ gửi)",
      "chưa gửi" in b.reason and "khớp 0" in b.reason, b.reason)
shutil.rmtree(root)

root = make_root([])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("CSV rỗng → available=False", not b.available and "rỗng" in b.reason, b.reason)
shutil.rmtree(root)

# Vắng mặt tiểu khoản — 2 nguyên nhân KHÁC HẲN nhau, phải tách bằng bằng chứng trong file.
# (a) Khớp 0 THẬT: account khác mà mình biết CÓ trong file ⇒ ánh xạ đang chạy đúng.
root = make_root([row("DRI", "0001743768", 1900, 13263)])   # chỉ ZaloPay khớp, SpaceX không
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("(a) account khác có mặt → kết luận khớp 0 THẬT (available=True)", b.available, b.reason)
check("(a) by_key rỗng", b.by_key == {})
_l = reconcile_lines(b, {("TV1", "buy"): 1300}, {("TV1", "buy"): 0})
check("(a) khớp 0 thật + state 0 → KHÔNG báo lệch, chỉ báo khớp thiếu",
      not any("LỆCH" in ln for ln in _l) and any("0/1,300" in ln for ln in _l), _l)
shutil.rmtree(root)

# (b) Ánh xạ HỎNG: file chỉ chứa tiểu khoản mình KHÔNG biết ⇒ không có bằng chứng nào.
root = make_root([row("DRI", "0007777777", 1900, 13263)])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("(b) không account nào mình biết có mặt → available=False (fail-closed §25)", not b.available, b.reason)
check("(b) KHÔNG kết luận '0 fill' khi nghi map sai", "không kết luận 0 fill" in b.reason, b.reason)
# CHỨNG MINH NGƯỢC: nếu guard này vắng, leg 3 sẽ báo mã trong plan là "lệch" (báo động giả).
_lines_if_no_guard = reconcile_lines(
    type(b)(True, "", "", {}), {("DRI", "buy"): 1900}, {("DRI", "buy"): 1900})
check("(b) chứng minh ngược: coi như available với 0 fill ⇒ sinh cảnh báo LỆCH giả",
      any("LỆCH" in ln for ln in _lines_if_no_guard), _lines_if_no_guard)
shutil.rmtree(root)

root = make_root([row("DRI", "0002023347", 100, 13262)])
with open(broker_csv_path(root, "2026-08-11"), "w") as f:
    f.write("cot_la,cot_hoac\n1,2\n")
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("layout đổi (thiếu cột) → available=False", not b.available and "thiếu cột" in b.reason, b.reason)
shutil.rmtree(root)

root = make_root([row("DRI", "0002023347", 100, 13262)],
                 accounts=[{"label": "ZaloPay", "account_id": "0001743768"}])
b = load_broker_fills("2026-08-11", "Unknown", root, allow_fetch=False)
check("account không có trong secrets → available=False", not b.available, b.reason)
shutil.rmtree(root)

print("\n=== 5. reconcile_lines: phân loại 3 tình huống ===")
root = make_root([row("DRI", "0002023347", 3700, 13262), row("TV1", "0002023347", 100, 19800)])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)

# (a) Khớp thiếu do thanh khoản (ca TV1 thật) — cảnh báo, KHÔNG gọi là lệch.
lines = reconcile_lines(b, {("DRI", "buy"): 3700, ("TV1", "buy"): 2000},
                        {("DRI", "buy"): 3700, ("TV1", "buy"): 100})
txt = "\n".join(lines)
check("khớp thiếu → có dòng 'chỉ khớp 100/2,000'", "100/2,000" in txt, txt)
check("khớp thiếu KHÔNG bị gọi là LỆCH state", "LỆCH broker-statement" not in txt, txt)
check("vẫn xác nhận không lệch", "✅" in txt, txt)

# (b) Lệch thật giữa state và broker.
lines = reconcile_lines(b, {("DRI", "buy"): 3700}, {("DRI", "buy"): 1000})
txt = "\n".join(lines)
check("state 1000 vs broker 3700 → cảnh báo LỆCH", "LỆCH broker-statement" in txt, txt)
check("nêu đúng độ lệch +2,700", "+2,700" in txt, txt)

# (c) Fill NGOÀI kế hoạch — điểm mù của cả 2 leg cũ.
lines = reconcile_lines(b, {("DRI", "buy"): 3700}, {("DRI", "buy"): 3700})
txt = "\n".join(lines)
check("TV1 khớp nhưng không có trong plan → cảnh báo NGOÀI KẾ HOẠCH",
      "NGOÀI KẾ HOẠCH" in txt and "TV1" in txt, txt)

# (d) Không available → đúng 1 dòng thông tin, không cảnh báo giả.
lines = reconcile_lines(load_broker_fills("2099-01-01", "SpaceX", root, allow_fetch=False),
                        {("DRI", "buy"): 3700}, {("DRI", "buy"): 0})
check("không available → 1 dòng 'bỏ qua', không cảnh báo", len(lines) == 1 and "bỏ qua" in lines[0], lines)

# (e) Phí thật được nêu ra.
lines = reconcile_lines(b, {("DRI", "buy"): 3700, ("TV1", "buy"): 100},
                        {("DRI", "buy"): 3700, ("TV1", "buy"): 100})
check("có dòng phí/thuế thật", any("Phí/thuế THẬT" in ln for ln in lines), lines)
shutil.rmtree(root)

print("\n=== 6. Side buy/sell không lẫn nhau ===")
root = make_root([row("HPG", "0002023347", 500, 22000, side="MUA"),
                  row("HPG", "0002023347", 300, 22100, side="BÁN")])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("HPG buy = 500", b.qty("HPG", "buy") == 500, f"got {b.qty('HPG','buy')}")
check("HPG sell = 300", b.qty("HPG", "sell") == 300, f"got {b.qty('HPG','sell')}")
lines = reconcile_lines(b, {("HPG", "buy"): 500, ("HPG", "sell"): 300},
                        {("HPG", "buy"): 500, ("HPG", "sell"): 300})
check("mua+bán cùng mã, cùng khớp đủ → không cảnh báo lệch",
      not any("LỆCH" in ln for ln in lines), lines)
shutil.rmtree(root)

print("\n=== 7. Nhiều dòng khớp cùng (mã, chiều) phải CỘNG DỒN ===")
root = make_root([row("DRI", "0002023347", 100, 13300), row("DRI", "0002023347", 300, 13300),
                  row("DRI", "0002023347", 200, 13300)])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("3 dòng lẻ → tổng 600cp", b.qty("DRI", "buy") == 600, f"got {b.qty('DRI','buy')}")
check("tổng giá trị cộng dồn đúng", abs(b.value - 600 * 13300) < 1, b.value)
check("phí cộng dồn đúng (3 dòng x 800)", abs(b.fees - 2400) < 1, b.fees)
shutil.rmtree(root)

print("\n=== 8. Dữ liệu THẬT 2026-08-11 (tự SKIP nếu file đã dọn) ===")
real_csv = broker_csv_path(WC_ROOT, "2026-08-11")
if not os.path.exists(real_csv):
    print(f"  ⏭️  SKIP — không còn {real_csv}")
else:
    sx = load_broker_fills("2026-08-11", "SpaceX", WC_ROOT, allow_fetch=False)
    zp = load_broker_fills("2026-08-11", "ZaloPay", WC_ROOT, allow_fetch=False)
    check("SpaceX available", sx.available, sx.reason)
    check("ZaloPay available", zp.available, zp.reason)
    check("ánh xạ tiểu khoản thật hoạt động (SpaceX có fill)", len(sx.by_key) > 0)
    check("SpaceX TV1 = 100 (số thật, đối chiếu tay)", sx.qty("TV1", "buy") == 100, f"got {sx.qty('TV1','buy')}")
    check("SpaceX DRI = 3700 (số thật)", sx.qty("DRI", "buy") == 3700, f"got {sx.qty('DRI','buy')}")
    check("ZaloPay TV1 = 0 (không khớp gì → không có dòng)", zp.qty("TV1", "buy") == 0)
    check("ZaloPay DRI = 1900 (số thật)", zp.qty("DRI", "buy") == 1900, f"got {zp.qty('DRI','buy')}")
    check("2 account KHÁC nhau (§12)", sx.by_key != zp.by_key)
    # Tỉ lệ phí thật — đối chiếu với giả định 0,075% trong reconcile_equity.py.
    rate = 100.0 * sx.fees / sx.value
    check("phí thật nằm trong [0,08%; 0,10%] (KHÁC 0,075% đang giả định)",
          0.08 <= rate <= 0.10, f"rate={rate:.4f}%")
    print(f"     ↳ phí thật SpaceX 11/08: {rate:.4f}% giá trị khớp "
          f"({sx.fees:,.0f}đ / {sx.value:,.0f}đ)")

# Ca THẬT của nhánh (a): 2026-08-07 ZaloPay bị gate P0 chặn sạch 0/9 lệnh ⇒ statement hôm đó có
# dòng của SpaceX nhưng KHÔNG có dòng nào của ZaloPay. Phải kết luận "khớp 0 thật", không phải
# "hỏng ánh xạ". Tự SKIP nếu statement đã dọn.
_csv_0807 = broker_csv_path(WC_ROOT, "2026-08-07")
if os.path.exists(_csv_0807):
    zp7 = load_broker_fills("2026-08-07", "ZaloPay", WC_ROOT, allow_fetch=False)
    sx7 = load_broker_fills("2026-08-07", "SpaceX", WC_ROOT, allow_fetch=False)
    check("ca thật 08-07: SpaceX có fill", sx7.available and len(sx7.by_key) > 0, sx7.reason)
    check("ca thật 08-07: ZaloPay khớp 0 → available=True, by_key rỗng (không phải lỗi map)",
          zp7.available and zp7.by_key == {}, zp7.reason)
else:
    print(f"  ⏭️  SKIP ca thật 08-07 — không còn {_csv_0807}")

print("\n=== 9. Không phụ thuộc TZ hệ thống (§16) ===")
_saved_tz = os.environ.pop("TZ", None)
root = make_root([row("DRI", "0002023347", 100, 13300)])
b = load_broker_fills("2026-08-11", "SpaceX", root, allow_fetch=False)
check("chạy được khi không có TZ (ngày truyền tường minh, không dùng now())", b.available, b.reason)
shutil.rmtree(root)
if _saved_tz is not None:
    os.environ["TZ"] = _saved_tz

print(f"\n{'='*60}\nKẾT QUẢ: {PASS} PASS / {FAIL} FAIL")
if FAILURES:
    for f in FAILURES:
        print(f"  ❌ {f}")
sys.exit(1 if FAIL else 0)
