#!/usr/bin/env python3
"""Selfcheck — cq-20260913 batch1 #1: gói vay default KHÔNG được rò giữa các account dùng chung
MỘT DNSEClient (`_DNSE_POOL` theo credentials_file; ZaloPay/SpaceX/RocketX cùng credentials=None).

Bug (brokers.py connect() cũ): `self.client.loan_package_id = self._loan_package_id` ⇒ account
connect sau đè default của account trước; `_resolve_loan_package_id`/`_validate_lever_package`
và dnse_api `place_order`/`ppse` (`lp = loan_package_id or self.loan_package_id`) đọc lại giá trị
đã bị đè. Đã xảy ra thật: dnse_raw 2026-08-11 ZaloPay resolve default=1841.

Dựng payload bằng CODE THẬT: `dnse_api.DNSEClient` thật (place_order/ppse/loan_packages thật),
chỉ `_request` bị thay bằng bộ ghi (không mạng). Danh sách gói theo account lấy từ dnse_raw thật
(SpaceX mainboard [1841 N, 1840 M], UPCOM [1122]; ZaloPay mainboard [1826, 1769], UPCOM [1258];
credentials default 1258).

Kiểm:
  A. Tiến trình NHIỀU account (connect SpaceX→RocketX→ZaloPay, gọi xen kẽ): mỗi account ra đúng
     gói của CHÍNH nó; ca lệnh T2 14/09 ZaloPay TV1 buy 200 cash_only ⇒ loanPackageId 1258.
  B. Tiến trình MỘT account: payload bản mới == bản base (git) TỪNG BYTE, cho cả 3 account
     — tức sửa lỗi rò KHÔNG đổi hành vi cron hiện tại (1 account/tiến trình).
  C. Tiến trình nhiều account == tiến trình một account (bản mới).
  D. RED control: bản base ở tiến trình nhiều account CHO RA gói sai (SpaceX bán ra 1122).
  F. (follow-up 1258) broker dựng KHÔNG truyền gói ⇒ tra profile theo account_id: SpaceX ra 1841
     (resolve default / ppse / place_order), ZaloPay (profile không gói) ra 1258 TỪNG BYTE như base;
     file profile lỗi/thiếu/mâu thuẫn ⇒ hành vi base + log nguyên văn, không ném. RED: base ra 1258.
  G. CHÍNH đường `mike/bin/discretionary_accumulation_inject.py::broker_filled_qty` (dựng broker
     như dòng gốc, client giả) ⇒ SpaceX 1841; cùng đường trên base ⇒ 1258 (RED).
  H. Biên: gói truyền TƯỜNG MINH thắng profile; account_id không khớp profile ⇒ gói credentials +
     log 1 lần; tra khi account_id còn None (trước connect) KHÔNG memo None.

File profile: fixture tạm (CFG.ACCOUNTS_FILE bị trỏ lại) — KHÔNG đọc secrets thật.

Chạy: source wc_env.sh && env -u TZ MIKE_BOT_TEST_MODE=1 $DNA_PYEXE loan_package_multi_account_selfcheck.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)

import contextlib                                      # noqa: E402
import io                                              # noqa: E402

import dnse_api                                        # noqa: E402
import trading_bot.brokers as B                        # noqa: E402
import trading_bot.config as CFG                       # noqa: E402

# Base = commit repo ngoài NGAY TRƯỚC bản vá #1 (GHIM CỐ Ý: hợp đồng "1 account từng byte").
BASE_REF = os.environ.get("LOANPKG_SELFCHECK_BASE_REF", "24df0f76")
CRED_DEFAULT = 1258
ACC = {"SpaceX": ("0002023347", 1841), "RocketX": ("000ROCKETX", 1122),
       "ZaloPay": ("0001743768", None)}
UPCOM = {"TV1", "DRI"}
# SAB: gói N lạ đứng TRƯỚC gói default ⇒ chỉ resolver đọc ĐÚNG default account mới giữ default
ODD = {"SAB": {"0002023347": [(9999, "N"), (1841, "N"), (1840, "M")],
               "000ROCKETX": [(9999, "N"), (1122, "N")],
               "0001743768": [(9999, "N"), (1258, "N")]}}
PKGS = {  # account_id -> (mainboard list, upcom list) — (id, type)
    "0002023347": ([(1841, "N"), (1840, "M")], [(1122, "N")]),
    "000ROCKETX": ([(1122, "N")], [(1122, "N")]),
    "0001743768": ([(1826, "N"), (1769, "M")], [(1258, "N")]),
}
# Fixture profile (khớp secrets thật về account_id/gói): SpaceX 1841, ZaloPay KHÔNG gói, RocketX 1122
PROFILES = [{"label": "main", "mode": "paper", "broker": "phs", "account_id": None},
            {"label": "ZaloPay", "mode": "live", "broker": "dnse", "account_id": "0001743768"},
            {"label": "SpaceX", "mode": "live", "broker": "dnse", "account_id": "0002023347",
             "loan_package_id": 1841},
            {"label": "RocketX", "mode": "live", "broker": "dnse", "account_id": "000ROCKETX",
             "loan_package_id": 1122}]
PROFILE_WARN = "dùng gói credentials"   # đuôi chung MỌI log của _profile_default_lp (khác log đòn bẩy)
FAILS, N = [], 0


def check(name, cond, detail=""):
    global N
    N += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + str(detail)) if detail else ''}")
    if not cond:
        FAILS.append(name)


def load_base():
    top = subprocess.run(["git", "-C", WC, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = os.path.relpath(os.path.join(WC, "trading_bot", "brokers.py"), top)
    src = subprocess.run(["git", "-C", top, "show", f"{BASE_REF}:{rel}"],
                         capture_output=True, text=True, check=True).stdout
    with tempfile.TemporaryDirectory(prefix="loanpkg_base_") as d:
        path = os.path.join(d, "brokers_base.py")
        open(path, "w", encoding="utf-8").write(src)
        spec = importlib.util.spec_from_file_location("trading_bot._brokers_base_lp", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def real_client(sent, tmp):
    c = dnse_api.DNSEClient(api_key="k", api_secret="s", otp_type="email_otp",
                            loan_package_id=CRED_DEFAULT,
                            token_cache=os.path.join(tmp, "no_token.json"))
    c.trading_token, c.token_expiry = "fake", 4102444800   # has_trading_token() True, không mạng

    def _request(method, path, query=None, body=None, trading=False):
        if path.endswith("/loan-packages"):
            acc = path.split("/")[2]
            main, up = PKGS[acc]
            sym = (query or {}).get("symbol")
            lst = ODD[sym][acc] if sym in ODD else (up if sym in UPCOM else main)
            return {"loanPackages": [{"id": i, "type": t} for i, t in lst]}
        if path == "/accounts/orders":
            sent.append(("order", body["accountNo"], json.dumps(body, sort_keys=True)))
            return {"id": len(sent)}
        if path.endswith("/positions"):
            return {"positions": [{"symbol": "HPG", "openQuantity": 300, "tradeQuantity": 300}]}
        if path.endswith("/ppse"):
            sent.append(("ppse", path.split("/")[2], json.dumps(query, sort_keys=True)))
            return {"qmaxBuy": 1000, "pp0Buy": 1e8}
        raise AssertionError(f"request không mong đợi: {method} {path}")
    c._request = _request
    return c


def install_pool(mod, tmp):
    sent = []
    client = real_client(sent, tmp)
    mod._DNSE_POOL.clear()
    mod._DNSE_POOL[os.path.abspath(mod.DEFAULT_DNSE_CREDENTIALS)] = client
    return sent


def brokers_for(mod, labels, tmp, pass_lp=True):
    """Dựng + connect THẬT (connect() của module) các broker dùng chung MỘT client pool.
    pass_lp=False ⇒ dựng như injector: KHÔNG truyền loan_package_id."""
    sent = install_pool(mod, tmp)
    out = {}
    for lb in labels:
        acc, lp = ACC[lb]
        kw = {"loan_package_id": lp} if pass_lp else {}
        b = mod.DNSEBroker(account_id=acc, label=lb, **kw)
        b._raw_log = None
        b.connect()
        out[lb] = b
    return out, sent


def script(b):
    """Chuỗi thao tác cố định cho 1 account; trả index để cắt `sent` theo account."""
    b.place_order("HPG", 100, "buy", price=25000)
    b.place_order("HPG", 100, "sell", price=25000)
    b.place_order("TV1", 200, "buy", price=20000, cash_only=True)
    b.place_order("VNM", 100, "buy", price=60000, loan_package_id=1840)
    b.place_order("TV1", 100, "buy", price=20000, loan_package_id=1840)
    b.get_max_buy_qty("HPG", 25000)
    b.get_buying_power("TV1", 20000)
    b.get_buying_power("VNM", 60000, loan_package_id=1840)
    b.place_order("SAB", 100, "buy", price=50000)
    b.place_order("SAB", 100, "buy", price=50000, loan_package_id=7777)


def by_account(sent):
    d = {}
    for kind, acc, payload in sent:
        d.setdefault(acc, []).append((kind, payload))
    return d


def lp_of(entry):
    kind, payload = entry
    p = json.loads(payload)
    return p.get("loanPackageId", "<KHÔNG CÓ KEY>")


def write_json(path, obj_or_text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text))
    return path


def run_captured(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn()
    return buf.getvalue()


def main():
    base = load_base()
    print(f"[base = {BASE_REF}:trading_bot/brokers.py]")
    tmp = tempfile.mkdtemp(prefix="loanpkg_sc_")
    good_accounts = write_json(os.path.join(tmp, "accounts_good.json"), {"accounts": PROFILES})
    CFG.ACCOUNTS_FILE = good_accounts
    # default `path=` của load_accounts bị đóng băng lúc định nghĩa hàm = secrets thật ⇒ trỏ nó vào
    # file không tồn tại: code dưới test mà quên truyền CFG.ACCOUNTS_FILE sẽ lộ ra ở mục F.
    CFG.load_accounts.__defaults__ = (os.path.join(tmp, "KHONG_DUOC_DOC_secrets.json"),)
    order3 = ["SpaceX", "RocketX", "ZaloPay"]

    print("\nA. nhiều account, bản mới — connect SpaceX→RocketX→ZaloPay, gọi xen kẽ")
    bs, sent = brokers_for(B, order3, tmp)
    for lb in order3:
        script(bs[lb])
    multi_new = by_account(sent)
    sp, rx, zp = (multi_new[ACC[x][0]] for x in order3)
    check("client dùng chung KHÔNG bị ghi đè (vẫn gói credentials)",
          bs["ZaloPay"].client.loan_package_id == CRED_DEFAULT, bs["ZaloPay"].client.loan_package_id)
    exp = {  # (SpaceX, RocketX, ZaloPay) theo thứ tự script()
        0: ("buy HPG", 1841, 1122, 1826),
        1: ("sell HPG", 1841, 1122, 1258),
        2: ("buy TV1 cash_only", 1122, 1122, 1258),
        3: ("buy VNM lever 1840 (ZaloPay/RocketX không hợp lệ ⇒ default account)", 1840, 1122, 1258),
        4: ("buy TV1 lever 1840 (không hợp lệ ⇒ default account)", 1841, 1122, 1258),
        5: ("ppse qmax HPG", "1841", "1122", "1258"),
        6: ("ppse pp0 TV1 (không truyền gói)", "1841", "1122", "1258"),
        7: ("ppse pp0 VNM lever 1840", "1840", "1840", "1840"),
        8: ("buy SAB (default hợp lệ nhưng không đứng đầu)", 1841, 1122, 1258),
        9: ("buy SAB lever 7777 (không hợp lệ ⇒ default account)", 1841, 1122, 1258),
    }
    for i, (nm, e_sp, e_rx, e_zp) in exp.items():
        got = (lp_of(sp[i]), lp_of(rx[i]), lp_of(zp[i]))
        check(f"[{nm}] SpaceX/RocketX/ZaloPay = {e_sp}/{e_rx}/{e_zp}", got == (e_sp, e_rx, e_zp), got)
    zp_tv1 = json.loads(zp[2][1])
    check("ca T2 14/09: ZaloPay TV1 buy 200 cash_only ⇒ loanPackageId 1258 (= lệnh thật 08-11→14)",
          zp_tv1.get("loanPackageId") == 1258 and zp_tv1["quantity"] == 200
          and zp_tv1["symbol"] == "TV1" and zp_tv1["side"] == "NB", zp_tv1)

    print("\nB. một account/tiến trình: bản mới == base TỪNG BYTE")
    single_new = {}
    for lb in order3:
        for mod, tag in ((B, "new"), (base, "base")):
            bs1, s1 = brokers_for(mod, [lb], tmp)
            script(bs1[lb])
            single_new.setdefault(lb, {})[tag] = s1
        check(f"[{lb}] payload new == base ({len(single_new[lb]['new'])} request)",
              single_new[lb]["new"] == single_new[lb]["base"])

    print("\nC. nhiều account (bản mới) == một account (bản mới)")
    for lb in order3:
        acc = ACC[lb][0]
        one = [(k, p) for k, _a, p in single_new[lb]["new"]]
        check(f"[{lb}] multi == single", multi_new[acc] == one)

    print("\nD. RED control: base ở tiến trình nhiều account rò gói")
    bsb, sentb = brokers_for(base, order3, tmp)
    for lb in order3:
        script(bsb[lb])
    mb = by_account(sentb)
    got_sp_sell = lp_of(mb[ACC["SpaceX"][0]][1])
    got_zp_sell = lp_of(mb[ACC["ZaloPay"][0]][1])
    check("base: SpaceX sell ra 1122 (gói RocketX) — bug tái hiện", got_sp_sell == 1122, got_sp_sell)
    check("base: ZaloPay sell ra 1122 (không phải 1258) — bug tái hiện", got_zp_sell == 1122, got_zp_sell)
    check("base: multi ≠ single cho SpaceX (bằng chứng bug có thật trong harness)",
          mb[ACC["SpaceX"][0]] != [(k, p) for k, _a, p in single_new["SpaceX"]["base"]])

    print("\nE. plan_funding_gate._effective_loan_package nhánh lever:unvalidated ⇒ default CỦA account")
    from trading_bot.plan_funding_gate import _effective_loan_package

    class _O:
        ticker, side, cash_only, loan_package_id = "VNM", "buy", False, 1840
    for mod, tag, exp_lp in ((B, "new", 1841), (base, "base", 1841)):
        bs1, _ = brokers_for(mod, ["SpaceX", "RocketX"], tmp)   # client dùng chung, SpaceX trước
        sb = bs1["SpaceX"]
        sb._validate_lever_package = lambda *a: 1 / 0            # ép nhánh không kiểm được
        eff, src = _effective_loan_package(_O(), sb)
        sent0 = len(_)
        sb.__dict__.pop("_validate_lever_package")
        sb.place_order("VNM", 100, "buy", price=60000, loan_package_id=7777)  # invalid ⇒ default
        wire = json.loads(_[sent0][2])["loanPackageId"]
        if tag == "new":
            check(f"[{tag}] gate đo gói {eff} == gói lệnh đi ra {wire} == 1841 ({src})",
                  eff == wire == exp_lp, (eff, wire))
            old_gate = getattr(sb.client, "loan_package_id", None)   # _account_default_package cũ
            check(f"[{tag}] RED: gate CŨ (đọc client) trên broker mới đo gói {old_gate} ≠ {wire}",
                  old_gate != wire, (old_gate, wire))
        else:
            check(f"[{tag}] RED: base gate/lệnh lệch hoặc sai gói ({eff}, {wire})",
                  not (eff == wire == exp_lp), (eff, wire))

    print("\nF. broker KHÔNG truyền gói ⇒ gói profile theo account_id (follow-up 1258)")
    ref = {lb: [(k, p) for k, _a, p in single_new[lb]["base"]] for lb in order3}   # base, CÓ truyền gói
    for mod, tag in ((B, "new"), (base, "base")):
        for lb in ("SpaceX", "ZaloPay"):
            bs1, s1 = brokers_for(mod, [lb], tmp, pass_lp=False)
            rawp = os.path.join(tmp, f"raw_{tag}_{lb}.jsonl")
            bs1[lb]._raw_log = rawp
            out = run_captured(lambda: script(bs1[lb]))
            got = [(k, p) for k, _a, p in s1]
            lps = [lp_of(e) for e in got]
            res = [r["payload"]["default"] for r in map(json.loads, open(rawp, encoding="utf-8"))
                   if r["kind"] == "loan_packages_resolve"]
            if tag == "new" and lb == "SpaceX":
                check("[new] SpaceX không gói: payload == SpaceX CÓ gói 1841 (base) TỪNG BYTE",
                      got == ref["SpaceX"], lps)
                check("[new] SpaceX không gói: buy HPG / sell HPG / ppse qmax / ppse pp0 = 1841",
                      (lps[0], lps[1], lps[5], lps[6]) == (1841, 1841, "1841", "1841"), lps)
                check("[new] SpaceX không gói: loan_packages_resolve.default toàn bộ = 1841",
                      bool(res) and set(res) == {1841}, res)
                check("[new] SpaceX không gói: không in cảnh báo tra profile", PROFILE_WARN not in out, out)
            elif tag == "new":
                check("[new] ZaloPay không gói: payload == base TỪNG BYTE (gói credentials 1258)",
                      got == ref["ZaloPay"], lps)
                check("[new] ZaloPay: resolve default = 1258, không cảnh báo",
                      bool(res) and set(res) == {1258} and PROFILE_WARN not in out, (res, out))
            elif lb == "SpaceX":
                check("[base] RED: SpaceX không gói ra 1258 (sell HPG / ppse pp0 / resolve default)",
                      lps[1] == 1258 and lps[6] == "1258" and set(res) == {1258}, (lps, res))

    # Fail-safe: file profile lỗi / thiếu / mâu thuẫn ⇒ đúng hành vi base (SpaceX không gói = 1258)
    bsb1, s_base = brokers_for(base, ["SpaceX"], tmp, pass_lp=False)
    script(bsb1["SpaceX"])
    base_nolp = [(k, p) for k, _a, p in s_base]
    dup = PROFILES + [{"label": "SpaceX_dup", "mode": "live", "broker": "dnse",
                       "account_id": "0002023347", "loan_package_id": 1840}]
    bad = {"JSON hỏng": (write_json(os.path.join(tmp, "accounts_bad.json"), '{"accounts": [,'),
                         "Lỗi thật: JSONDecodeError"),
           "thiếu file": (os.path.join(tmp, "khong_ton_tai.json"), "Lỗi thật: FileNotFoundError"),
           "trùng label": (write_json(os.path.join(tmp, "accounts_duplabel.json"),
                                      {"accounts": PROFILES + [PROFILES[2]]}), "Lỗi thật: ValueError"),
           "2 profile cùng account_id khác gói": (write_json(os.path.join(tmp, "accounts_dup.json"),
                                                            {"accounts": dup}), "[1840, 1841]")}
    for nm, (path, needle) in bad.items():
        CFG.ACCOUNTS_FILE = path
        try:
            bs1, s1 = brokers_for(B, ["SpaceX"], tmp, pass_lp=False)
            out = run_captured(lambda: script(bs1["SpaceX"]))
            got = [(k, p) for k, _a, p in s1]
            check(f"[new] {nm}: không ném, payload == base SpaceX không gói (1258) TỪNG BYTE",
                  got == base_nolp, [lp_of(e) for e in got])
            check(f"[new] {nm}: log nguyên văn chứa {needle!r}, đúng 1 lần (tra 1 lần/instance)",
                  out.count(needle) == 1 and out.count(PROFILE_WARN) == 1, out.strip())
        except Exception as exc:
            check(f"[new] {nm}: không được ném", False, f"{type(exc).__name__}: {exc}")
    CFG.ACCOUNTS_FILE = good_accounts

    print("\nG. CHÍNH đường discretionary_accumulation_inject.broker_filled_qty (dòng dựng broker gốc)")
    inj_path = os.path.join(WC, "mike", "bin", "discretionary_accumulation_inject.py")
    spec = importlib.util.spec_from_file_location("_dai_selfcheck", inj_path)
    inj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inj)
    real_mod = sys.modules["trading_bot.brokers"]
    for mod, tag in ((B, "new"), (base, "base")):
        sent = install_pool(mod, tmp)
        saved_exec = mod.EXEC_DIR
        mod.EXEC_DIR = tmp                                   # __init__ tính _raw_log từ EXEC_DIR
        sys.modules["trading_bot.brokers"] = mod             # `from trading_bot.brokers import DNSEBroker`
        try:
            filled, b = inj.broker_filled_qty("SpaceX", ACC["SpaceX"][0], "HPG", 100)
        finally:
            sys.modules["trading_bot.brokers"] = real_mod
            mod.EXEC_DIR = saved_exec
        if b is None or type(b).__module__ != mod.__name__:
            check(f"[{tag}] broker_filled_qty dựng broker từ đúng module", False, (filled, b))
            continue
        b._raw_log = os.path.join(tmp, f"raw_inj_{tag}.jsonl")
        b.place_order("HPG", 100, "sell", price=25000)
        b.get_buying_power("TV1", 20000)
        b._resolve_loan_package_id("TV1")
        rd = [r["payload"]["default"] for r in map(json.loads, open(b._raw_log, encoding="utf-8"))
              if r["kind"] == "loan_packages_resolve"][-1]
        lps = [lp_of((k, p)) for k, _a, p in sent]
        exp = (1841, "1841", 1841) if tag == "new" else (1258, "1258", 1258)
        check(f"[{tag}] filled=200 (300−100); sell / ppse / resolve.default = {exp}"
              + (" — RED" if tag == "base" else ""),
              filled == 200 and (lps[0], lps[1], rd) == exp, (filled, lps, rd))

    print("\nH. Biên: ưu tiên gói tường minh / không khớp profile / account_id None chưa memo")
    sent = install_pool(B, tmp)
    bx = B.DNSEBroker(account_id=ACC["SpaceX"][0], label="SpaceX", loan_package_id=1840)
    bx._raw_log = None
    bx.connect()
    bx.place_order("HPG", 100, "sell", price=25000)
    bx.get_buying_power("TV1", 20000)
    check("[new] SpaceX truyền gói 1840 ≠ profile 1841 ⇒ sell / ppse ra 1840 (tường minh thắng)",
          [lp_of((k, p)) for k, _a, p in sent] == [1840, "1840"],
          [lp_of((k, p)) for k, _a, p in sent])

    sent = install_pool(B, tmp)
    PKGS["0009999999"] = PKGS["0001743768"]
    bu = B.DNSEBroker(account_id="0009999999", label="Unknown")
    bu._raw_log = None
    out = run_captured(lambda: (bu.connect(), bu.place_order("HPG", 100, "sell", price=25000),
                                bu.get_buying_power("TV1", 20000)))
    check("[new] account_id không khớp profile ⇒ gói credentials 1258, log 'không profile nào' 1 lần",
          [lp_of((k, p)) for k, _a, p in sent] == [1258, "1258"]
          and out.count("không profile nào có account_id '0009999999'") == 1
          and out.count(PROFILE_WARN) == 1, ([lp_of((k, p)) for k, _a, p in sent], out.strip()))

    bn = B.DNSEBroker(label="SpaceX")
    first = bn._profile_default_lp()
    bn.account_id = ACC["SpaceX"][0]
    check("[new] tra khi account_id None ⇒ None, KHÔNG memo; gán account_id sau ⇒ 1841",
          first is None and bn._profile_default_lp() == 1841, (first, bn._profile_default_lp()))

    print(f"\n{N - len(FAILS)}/{N} PASS")
    if FAILS:
        print("FAIL:", FAILS)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
