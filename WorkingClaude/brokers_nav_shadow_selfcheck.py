#!/usr/bin/env python3
"""Selfcheck — code-quality-weekly 2026-09-13, batch 1 (job Taylor_20260913_050827):

#3 make_broker() nhánh live truyền `loan_package_id=` cho mọi BROKER_CLASSES ⇒ PHSBroker phải
   nhận tham số (trước đây TypeError). RED control: bản brokers.py ở base (git) PHẢI ném.
#2 DNSEBroker.get_nav(): cờ `nav_include_egg_offbook` OFF ⇒ trả ĐÚNG TỪNG BYTE giá trị của
   bản trước sửa (so với module nạp từ git, cùng client giả); shadow (+egg +offbook, bộ 3 guard
   canonical) ghi `nav_basis_note`; shadow ném exception ⇒ get_nav vẫn trả giá trị cũ (cả OFF
   lẫn ON); ON + guard feed-0 từ chối ⇒ giá trị cũ; sys.path không bị đổi.

Base so sánh = `b53d26b4` (repo ngoài, trước bản vá) — GHIM CỐ Ý: hợp đồng "OFF từng byte" là so
với code TRƯỚC cq-20260913. Ai cố ý đổi nhánh OFF của get_nav sau này thì cập nhật ref/assert.
Không kết nối DNSE/PHS thật: client giả, `_raw_log=None` (không ghi dnse_raw thật).
Chạy: source wc_env.sh && env -u TZ MIKE_BOT_TEST_MODE=1 $DNA_PYEXE brokers_nav_shadow_selfcheck.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import types

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)

import trading_bot.brokers as B                        # noqa: E402

FAILS = []
N = 0


def check(name, cond, detail=""):
    global N
    N += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + str(detail)) if detail else ''}")
    if not cond:
        FAILS.append(name)


def load_base_brokers():
    """brokers.py trước bản vá (commit gốc của repo ngoài chứa WorkingClaude/)."""
    top = subprocess.run(["git", "-C", WC, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = os.path.relpath(os.path.join(WC, "trading_bot", "brokers.py"), top)
    ref = os.environ.get("BROKERS_SELFCHECK_BASE_REF", "b53d26b4")  # repo ngoài, trước bản vá
    src = subprocess.run(["git", "-C", top, "show", f"{ref}:{rel}"],
                         capture_output=True, text=True, check=True).stdout
    with tempfile.TemporaryDirectory(prefix="brokers_base_") as d:
        path = os.path.join(d, "brokers_base.py")
        open(path, "w", encoding="utf-8").write(src)
        spec = importlib.util.spec_from_file_location("trading_bot._brokers_base", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod, ref


class FakeClient:
    def __init__(self, bal):
        self.bal = bal
        self.loan_package_id = 1258

    def balances(self, account_id):
        return self.bal


def dnse(mod, bal, label="SpaceX", flag=False):
    b = mod.DNSEBroker(account_id="000TEST", label=label)
    b.client = FakeClient(bal)
    b._raw_log = None
    b.get_positions = lambda: {"AAA": {"total": 1000, "sellable": 1000},
                               "BBB": {"total": 300, "sellable": 0}}
    px = {"AAA": 23456.0, "BBB": 101300.0}
    b.get_quote = lambda s: mod.Quote({"symbol": s, "lastPrice": px[s], "refPrice": px[s]})
    b.get_cash = lambda: 7_777_777.0
    if flag:
        b.nav_include_egg_offbook = True
    return b


MV = 1000 * 23456.0 + 300 * 101300.0
PAYLOADS = {
    "normal+egg": {"stock": {"totalCash": 203_656_265, "totalDebt": 50_000_000,
                             "availableCash": 4_821_143, "depositInterest": 12},
                   "egg": {"totalValue": 100_200_000}},
    "no-egg": {"stock": {"totalCash": 12_272_672, "totalDebt": 0, "availableCash": 5_818_854,
                         "depositInterest": 318}},
    "totalCash0<avail (T18p)": {"stock": {"totalCash": 0, "totalDebt": 0,
                                          "availableCash": 5_000_000, "depositInterest": 3},
                                "egg": {"totalValue": 1_000_000}},
    "block all-zero": {"stock": {"totalCash": 0, "totalDebt": 0, "availableCash": 0,
                                 "depositInterest": 0}, "egg": {"totalValue": 0}},
    "missing totalDebt": {"stock": {"totalCash": 9_000_000, "availableCash": 1_000_000}},
}


def main():
    base, ref = load_base_brokers()
    print(f"[base = {ref}:trading_bot/brokers.py]")

    q = B.Quote({"symbol": "AAA", "lastPrice": 23456.0})
    check("Quote giả dựng được, last đúng đơn vị VND", q.ok() and q.last == 23456.0, q)

    print("\n#3 make_broker phs mode=live")
    cfg = {"mode": "live", "paper_init_cash": 1, "paper_fee_rate": 0}
    prof = {"label": "phs_live_test", "broker": "phs", "credentials_file": None,
            "account_id": "X", "loan_package_id": None}
    try:
        b = B.make_broker(cfg, profile=prof)
        check("không TypeError, trả PHSBroker chưa connect", isinstance(b, B.PHSBroker)
              and b.client is None)
    except TypeError as e:
        check("không TypeError", False, e)
    try:
        base.make_broker(cfg, profile=prof)
        check("RED control: bản base PHẢI TypeError", False, "không ném")
    except TypeError as e:
        check("RED control: bản base TypeError", "loan_package_id" in str(e), e)
    bd = B.make_broker(dict(cfg, nav_include_egg_offbook=True),
                       profile=dict(prof, broker="dnse", label="dnse_t"))
    check("make_broker dnse live gán cờ từ cfg", bd.nav_include_egg_offbook is True)
    bd2 = B.make_broker(cfg, profile=dict(prof, broker="dnse", label="dnse_t"))
    check("make_broker dnse live cờ mặc định OFF", bd2.nav_include_egg_offbook is False)

    print("\n#2 get_nav OFF == base từng byte, shadow note, fail-safe")
    for name, bal in PAYLOADS.items():
        old = dnse(base, bal).get_nav()
        path_before = list(sys.path)
        nb = dnse(B, bal)
        v = nb.get_nav()
        check(f"[{name}] OFF == base ({old!r})", v == old and repr(v) == repr(old)
              and type(v) is type(old), f"new={v!r}")
        check(f"[{name}] sys.path không đổi", sys.path == path_before)
        check(f"[{name}] note NAV_BASIS old=", (nb.nav_basis_note or "").startswith(
            f"NAV_BASIS old={old:.0f} "), nb.nav_basis_note)
        nb_on = dnse(B, bal, flag=True)
        on = nb_on.get_nav()
        egg = float((bal.get("egg") or {}).get("totalValue") or 0)
        st = bal["stock"]
        guard = (all(not v for v in st.values()) or
                 (st.get("totalCash") is not None and st.get("availableCash") is not None
                  and st["totalCash"] < st["availableCash"]) or
                 st.get("totalDebt") is None)
        if guard:
            check(f"[{name}] ON + guard canonical từ chối ⇒ old", on == old and "new=None" in
                  nb_on.nav_basis_note and nb_on.nav_basis_note.endswith("=ON"),
                  nb_on.nav_basis_note)
        else:
            exp = st["totalCash"] - st["totalDebt"] + MV + egg + 0.0   # SpaceX offbook=0
            check(f"[{name}] ON = cash_basis+mv+egg+offbook ({exp:,.0f})", on == exp, on)
            check(f"[{name}] ON − OFF == egg+offbook", on - old == egg, on - old)

    bal = PAYLOADS["normal+egg"]
    old = dnse(base, bal).get_nav()

    def boom(self, *a, **k):
        raise RuntimeError("shadow nổ cố ý")
    for flag in (False, True):
        nb = dnse(B, bal, flag=flag)
        nb._nav_owned_shadow = types.MethodType(boom, nb)
        v = nb.get_nav()
        check(f"shadow ném, cờ={'ON' if flag else 'OFF'} ⇒ trả old", v == old, v)
        check(f"shadow ném, cờ={'ON' if flag else 'OFF'} ⇒ note nguyên văn lỗi",
              "RuntimeError: shadow nổ cố ý" in nb.nav_basis_note, nb.nav_basis_note)
    # Loader canonical hỏng (file mất / import lỗi) ⇒ vẫn old
    real_loader = B._load_compute_active_nav
    try:
        B._load_compute_active_nav = lambda: (_ for _ in ()).throw(FileNotFoundError("mất file"))
        nb = dnse(B, bal, flag=True)
        v = nb.get_nav()
        check("loader canonical lỗi, cờ ON ⇒ old + note lỗi", v == old and
              "FileNotFoundError" in nb.nav_basis_note, nb.nav_basis_note)
        # offbook: profile có manual_offbook ⇒ cộng vào (dùng cash_basis THẬT)
        can = real_loader()
        stub = types.SimpleNamespace(cash_basis=can.cash_basis,
                                     get_account_profile=lambda lb: {"manual_offbook_assets_vnd": 5_000_000})
        B._load_compute_active_nav = lambda: stub
        nb = dnse(B, bal, flag=True)
        v = nb.get_nav()
        check("offbook profile 5tr cộng vào ON", v == old + 100_200_000 + 5_000_000, v - old)
    finally:
        B._load_compute_active_nav = real_loader
    # nhánh OFF không gọi thêm API balances nào (shadow dùng lại cùng bản đọc)
    calls = []
    nb = dnse(B, bal)
    orig = nb.client.balances
    nb.client.balances = lambda a: (calls.append(a), orig(a))[1]
    nb.get_nav()
    check("get_nav chỉ gọi balances 1 lần (như base)", len(calls) == 1, calls)

    print(f"\n{N - len(FAILS)}/{N} PASS")
    if FAILS:
        print("FAIL:", FAILS)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
