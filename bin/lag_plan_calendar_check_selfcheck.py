#!/usr/bin/env python3
"""Selfcheck cho mike/bin/lag_plan_calendar_check.py — hồi quy ca thật 24-28/07/2026.

Fixture ĐÓNG BĂNG (không đọc production sống): `bin/fixtures/lag_calendar_20260724/` = các dòng
book=LAG chép nguyên văn từ `deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-07-{23,24,27}.csv`
(md5 bản gốc lúc chép 2026-10-21: fe52a31e… / e0e83ddb… / 00176a19…). Plan JSON dựng lại theo
schema `lag_analysis` hiện hành, nội dung theo đúng artifact thật (trích dẫn ở từng ca):
  A. plan_SpaceX_2026-07-24: "T+2 entry 07-25" (THỨ BẢY) cho AGR/BSI/FTS/HCM.
  B. plan_SpaceX_2026-07-27: "CỬA SỔ ĐÃ ĐÓNG — MISSED"; plan_ZaloPay cùng ngày coi 07-27 là phiên
     chuẩn (mua VPB).
  C. plan_ZaloPay_2026-07-28: đọc signal 07-24 + "FLOOR_FAIL — skip" EVF/PSI/VCI; SpaceX cùng
     ngày signal 07-27, xếp VALID.
Có MUTATION: phá từng mảnh logic phải làm suite đỏ. Không import Executor (§5b không áp dụng),
không đọc dnse_raw (§12 không áp dụng). Chạy được dưới `env -u TZ` và TZ lạ (§16) — checker
không gọi now().

    python3 mike/bin/lag_plan_calendar_check_selfcheck.py
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lag_plan_calendar_check as C  # noqa: E402

FX = os.path.join(HERE, "fixtures", "lag_calendar_20260724")
SRC = "mike/bin/filter_lag_entry_window.py --account {a} --json"


def _plan(acct, pdate, signal, due=(), upcoming=(), orders=(), with_la=True):
    p = {"plan_date": pdate, "account": acct, "orders": list(orders), "deferred_orders": []}
    if with_la:
        p["lag_analysis"] = {"signal_date": signal, "source_script": SRC.format(a=acct),
                             "due_today": list(due), "lag_upcoming_for_next_plans": list(upcoming)}
    return p


def _due_from_ref(ref, decisions=None, day1_only=False):
    """Mục due_today ĐÚNG theo code (dựng plan đối chứng). decisions: {tk: (decision, why, extra)}"""
    out = []
    for tk, r in sorted(ref["due"].items()):
        if day1_only and r["entry_window_day"] != 1:
            continue
        dec, why, extra = (decisions or {}).get(tk, ("SKIP", "ADV thấp / thanh khoản mỏng", {}))
        it = {"ticker": tk, "entry_date": r["entry_date"],
              "entry_window_day": r["entry_window_day"], "decision": dec, "decision_why": why}
        it.update(extra)
        out.append(it)
    return out


def _codes(findings, account=None, ticker=None):
    return sorted({f["code"] for f in findings
                   if (account is None or account in str(f["account"]))
                   and (ticker is None or f["ticker"] == ticker)})


def suite(verbose=True):
    passed, failed = [], []

    def check(name, cond, detail=""):
        (passed if cond else failed).append(name)
        if verbose:
            print(("  ✓ " if cond else "  ✗ ") + name + (f"  [{detail}]" if detail and not cond else ""))

    # ── 0. Lịch giao dịch ────────────────────────────────────────────────────
    check("07-25-2026 (T7) không phải phiên", not C.is_trading_day("2026-07-25"))
    check("07-27-2026 (T2) là phiên", C.is_trading_day("2026-07-27"))
    check("phiên trước 07-27 là 07-24 (bỏ T7/CN)", str(C.prev_trading_day("2026-07-27")) == "2026-07-24")
    check("02-09 (Quốc khánh) không phải phiên", not C.is_trading_day("2026-09-02"))

    # ── A. 07-24 SpaceX: entry ước "07-25" (thứ Bảy) ─────────────────────────
    refA = C.reference("2026-07-24", FX)
    check("A: tham chiếu dựng được (signal 07-23)", refA["ok"] and refA["signal_date"] == "2026-07-23",
          str(refA.get("error")))
    for tk in ("AGR", "BSI", "FTS", "HCM"):
        check(f"A: code xếp {tk} sắp tới, entry 2026-07-27", refA["upcoming"].get(tk) == "2026-07-27",
              str(refA["upcoming"].get(tk)))
    dueA = _due_from_ref(refA, {"IVS": ("SKIP", "user loại 07-21 (thanh khoản ~0)", {}),
                                "TRC": ("SKIP", "8L rating ≥4", {})})
    upA_bad = [{"ticker": tk, "entry_date_est": "2026-07-25"} for tk in ("AGR", "BSI", "FTS", "HCM")]
    fA = C.check_plan(_plan("SpaceX", "2026-07-24", "2026-07-23", dueA, upA_bad), refA)
    for tk in ("AGR", "BSI", "FTS", "HCM"):
        check(f"A: {tk} entry 07-25 ⇒ NONTRADING + ENTRY_DATE_MISMATCH",
              {"LAG_CAL_NONTRADING_DATE", "LAG_CAL_ENTRY_DATE_MISMATCH"} <= set(_codes(fA, ticker=tk)),
              str(_codes(fA, ticker=tk)))
    upA_ok = [{"ticker": tk, "entry_date_est": d} for tk, d in refA["upcoming"].items()]
    fA_ok = C.check_plan(_plan("SpaceX", "2026-07-24", "2026-07-23", dueA, upA_ok), refA)
    check("A đối chứng: plan chép đúng code ⇒ 0 phát hiện", fA_ok == [], str(fA_ok[:3]))

    # ── B. 07-27: SpaceX "cửa sổ đã đóng", ZaloPay coi là phiên chuẩn ─────────
    refB = C.reference("2026-07-27", FX)
    check("B: tham chiếu dựng được (signal 07-24, KHÔNG phải 07-26 CN)",
          refB["ok"] and refB["signal_date"] == "2026-07-24", str(refB.get("error")))
    for tk in ("AGR", "BSI", "FTS", "HCM", "VPB"):
        r = refB["due"].get(tk) or {}
        check(f"B: code: {tk} entry 07-27 ngày 1/3",
              r.get("entry_date") == "2026-07-27" and r.get("entry_window_day") == 1, str(r))
    spx_b = _plan("SpaceX", "2026-07-27", "2026-07-24", due=[])          # "CỬA SỔ ĐÃ ĐÓNG"
    zlp_b = _plan("ZaloPay", "2026-07-27", "2026-07-24",
                  due=_due_from_ref(refB, {"VPB": ("BUY", "phiên chuẩn", {})}, day1_only=True))
    resB = C.run([spx_b, zlp_b], FX, excluded={"SpaceX": set(), "ZaloPay": {"DGC"}})
    for tk in ("AGR", "BSI", "FTS", "HCM"):
        check(f"B: SpaceX thiếu {tk} ⇒ LAG_CAL_DUE_MISSING",
              "LAG_CAL_DUE_MISSING" in _codes(resB["findings"], "SpaceX", tk))
    check("B: ZaloPay (đúng code) không có phát hiện riêng",
          not [f for f in resB["findings"] if f["account"] == "ZaloPay"],
          str([f for f in resB["findings"] if f["account"] == "ZaloPay"][:3]))
    check("B: cặp ⇒ LAG_X_DUE_SET_MISMATCH", "LAG_X_DUE_SET_MISMATCH" in resB["codes"])
    check("B: status FAIL", resB["status"] == "FAIL")
    spx_b_noLA = _plan("SpaceX", "2026-07-27", "2026-07-24", with_la=False)
    check("B: plan không có lag_analysis ⇒ LAG_CAL_ANALYSIS_MISSING",
          "LAG_CAL_ANALYSIS_MISSING" in _codes(C.check_plan(spx_b_noLA, refB)))
    # Hai account cùng tín hiệu phải ra cùng entry_date
    spx_b_shift = copy.deepcopy(zlp_b)
    spx_b_shift["account"] = "SpaceX"
    for it in spx_b_shift["lag_analysis"]["due_today"]:
        if it["ticker"] == "AGR":
            it["entry_date"] = "2026-07-28"
    resB2 = C.run([spx_b_shift, zlp_b], FX, excluded={})
    check("B: cùng mã khác entry_date giữa 2 account ⇒ LAG_X_ENTRY_DATE_MISMATCH",
          "LAG_X_ENTRY_DATE_MISMATCH" in _codes(resB2["findings"], ticker="AGR"))
    check("B: ... và ENTRY_DATE_MISMATCH riêng SpaceX",
          "LAG_CAL_ENTRY_DATE_MISMATCH" in _codes(resB2["findings"], "SpaceX", "AGR"))
    # entry_window_day sai
    spx_b_wd = copy.deepcopy(zlp_b)
    spx_b_wd["lag_analysis"]["due_today"][0]["entry_window_day"] = 2
    tk0 = spx_b_wd["lag_analysis"]["due_today"][0]["ticker"]
    check("B: entry_window_day lệch ⇒ LAG_CAL_WINDOW_DAY_MISMATCH",
          "LAG_CAL_WINDOW_DAY_MISMATCH" in _codes(C.check_plan(spx_b_wd, refB), ticker=tk0))
    # thiếu trường + nguồn
    spx_b_nf = copy.deepcopy(zlp_b)
    spx_b_nf["lag_analysis"]["due_today"][0].pop("entry_window_day")
    spx_b_nf["lag_analysis"]["source_script"] = "tự đọc CSV"
    fnf = C.check_plan(spx_b_nf, refB)
    check("B: thiếu entry_window_day ⇒ LAG_CAL_FIELD_MISSING", "LAG_CAL_FIELD_MISSING" in _codes(fnf))
    check("B: nguồn không phải filter ⇒ LAG_CAL_SOURCE_MISSING", "LAG_CAL_SOURCE_MISSING" in _codes(fnf))
    # lệnh LAG ngoài cửa sổ + lệnh BÁN LAG không bị kiểm lịch
    spx_b_ord = _plan("SpaceX", "2026-07-27", "2026-07-24",
                      due=_due_from_ref(refB, day1_only=True),
                      orders=[{"ticker": "EVF", "book": "LAG", "side": "buy"},
                              {"ticker": "SCL", "book": "LAG", "side": "sell"},
                              {"ticker": "AGR", "book": "LAG", "side": "buy",
                               "entry_anchor_date": "2026-07-27", "entry_window_day": 1}])
    ford = C.check_plan(spx_b_ord, refB)
    check("B: lệnh mua LAG EVF (chưa tới phiên) ⇒ LAG_CAL_ORDER_NOT_DUE",
          "LAG_CAL_ORDER_NOT_DUE" in _codes(ford, ticker="EVF"))
    check("B: lệnh BÁN LAG SCL không bị kiểm lịch", not _codes(ford, ticker="SCL"))
    check("B: lệnh mua AGR đúng lịch ⇒ không phát hiện", not _codes(ford, ticker="AGR"))
    # plan_date không phải phiên
    check("B: plan_date thứ Bảy ⇒ PLAN_DATE_NONTRADING",
          "LAG_CAL_PLAN_DATE_NONTRADING" in _codes(C.run(
              [_plan("SpaceX", "2026-07-25", "2026-07-24")], FX)["findings"]))

    # ── C. 07-28: ZaloPay signal 07-24 + "FLOOR_FAIL — skip"; SpaceX VALID ─────
    refC = C.reference("2026-07-28", FX)
    check("C: tham chiếu signal 07-27", refC["ok"] and refC["signal_date"] == "2026-07-27")
    for tk in ("EVF", "PSI", "VCI"):
        check(f"C: lăng kính cùng CSV: {tk} KHONG_SKIP_VI_FLOOR_FAIL",
              refC["lens"].get(tk) == "KHONG_SKIP_VI_FLOOR_FAIL", str(refC["lens"].get(tk)))
    spx_dec = {tk: ("DEFER", "sector_valuation_lens KHONG_SKIP_VI_FLOOR_FAIL; thiếu tiền", {})
               for tk in ("EVF", "PSI", "VCI")}
    zlp_dec = {tk: ("SKIP", "FLOOR_FAIL — skip", {}) for tk in ("EVF", "PSI", "VCI")}
    spx_c = _plan("SpaceX", "2026-07-28", "2026-07-27", _due_from_ref(refC, spx_dec, day1_only=True))
    zlp_c = _plan("ZaloPay", "2026-07-28", "2026-07-24", _due_from_ref(refC, zlp_dec, day1_only=True))
    resC = C.run([spx_c, zlp_c], FX, excluded={"SpaceX": set(), "ZaloPay": {"DGC"}})
    check("C: ZaloPay signal 07-24 ⇒ LAG_CAL_SIGNAL_MISMATCH",
          "LAG_CAL_SIGNAL_MISMATCH" in _codes(resC["findings"], "ZaloPay"))
    check("C: cặp ⇒ LAG_X_SIGNAL_MISMATCH", "LAG_X_SIGNAL_MISMATCH" in resC["codes"])
    for tk in ("EVF", "PSI", "VCI"):
        check(f"C: ZaloPay {tk} ⇒ LAG_DD_FLOOR_FAIL_NOT_GATE",
              "LAG_DD_FLOOR_FAIL_NOT_GATE" in _codes(resC["findings"], "ZaloPay", tk))
        check(f"C: cặp {tk} ⇒ LAG_X_DD_DECISION_MISMATCH",
              "LAG_X_DD_DECISION_MISMATCH" in _codes(resC["findings"], ticker=tk))
    check("C: SpaceX (đúng code) không có phát hiện riêng",
          not [f for f in resC["findings"] if f["account"] == "SpaceX"])
    # Khác biệt hợp lệ: khai tường minh riêng-account
    zlp_ex = _plan("ZaloPay", "2026-07-28", "2026-07-27", _due_from_ref(refC, dict(
        zlp_dec, EVF=("SKIP", "excluded_tickers của account", {"skip_reason_code": "EXCLUDED_TICKER"}),
        PSI=("SKIP", "đã giữ", {"skip_reason_code": "ALREADY_HELD"}),
        VCI=("DEFER", "thiếu tiền", {})), day1_only=True))
    resC2 = C.run([spx_c, zlp_ex], FX, excluded={"SpaceX": set(), "ZaloPay": {"EVF"}})
    check("C: EXCLUDED_TICKER có trong config ⇒ không DD mismatch",
          not _codes(resC2["findings"], ticker="EVF"), str(_codes(resC2["findings"], ticker="EVF")))
    check("C: ALREADY_HELD khai tường minh ⇒ không DD mismatch", not _codes(resC2["findings"], ticker="PSI"))
    check("C: cả cặp hợp lệ ⇒ PASS", resC2["status"] == "PASS", str(resC2["findings"][:3]))
    resC3 = C.run([spx_c, zlp_ex], FX, excluded={"SpaceX": set(), "ZaloPay": set()})
    check("C: EXCLUDED_TICKER không có trong config ⇒ LAG_X_EXCLUDED_UNVERIFIED",
          "LAG_X_EXCLUDED_UNVERIFIED" in _codes(resC3["findings"], ticker="EVF"))
    resC4 = C.run([spx_c, zlp_ex], FX, excluded=None)
    check("C: không đọc được config ⇒ LAG_X_EXCLUDED_UNVERIFIED (fail-closed)",
          "LAG_X_EXCLUDED_UNVERIFIED" in _codes(resC4["findings"], ticker="EVF"))
    # SKIP nêu cổng khác ⇒ không quy là FLOOR_FAIL misread
    zlp_other = _plan("ZaloPay", "2026-07-28", "2026-07-27", _due_from_ref(refC, dict(
        zlp_dec, EVF=("SKIP", "FLOOR_FAIL + DCF RICH", {})), day1_only=True))
    check("C: SKIP viện thêm RICH ⇒ không báo FLOOR_FAIL_NOT_GATE",
          "LAG_DD_FLOOR_FAIL_NOT_GATE" not in _codes(C.check_plan(zlp_other, refC), ticker="EVF"))

    # ── D. Rỗng LAG + thiếu CSV ──────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as td:
        resD = C.run([_plan("SpaceX", "2026-07-28", "2026-07-27")], td)
        check("D: thiếu CSV ⇒ UNCHECKABLE (không PASS im lặng)", resD["status"] == "UNCHECKABLE")

    # ── E. CLI + rc + report block (fixture, thư mục plan tạm) ───────────────
    with tempfile.TemporaryDirectory() as td:
        for p in (spx_c, zlp_c):
            with open(os.path.join(td, f"plan_{p['account']}_{p['plan_date']}.json"), "w") as f:
                json.dump(p, f, ensure_ascii=False)
        cp = subprocess.run([sys.executable, os.path.join(HERE, "lag_plan_calendar_check.py"),
                             "--account", "SpaceX", "--plan-date", "2026-07-28", "--plans-dir", td,
                             "--recs-dir", FX, "--report-block"], capture_output=True, text=True)
        check("E: CLI rc=1 khi FAIL", cp.returncode == 1, f"rc={cp.returncode} err={cp.stderr[-300:]}")
        check("E: report block nêu mã nguyên nhân", "LAG_X_SIGNAL_MISMATCH" in cp.stdout, cp.stdout[:200])
        os.remove(os.path.join(td, "plan_ZaloPay_2026-07-28.json"))
        cp2 = subprocess.run([sys.executable, os.path.join(HERE, "lag_plan_calendar_check.py"),
                              "--account", "SpaceX", "--plan-date", "2026-07-28", "--plans-dir", td,
                              "--recs-dir", FX, "--json"], capture_output=True, text=True)
        check("E: SpaceX đúng code một mình ⇒ rc=0", cp2.returncode == 0,
              f"rc={cp2.returncode} {cp2.stdout[-300:]}{cp2.stderr[-300:]}")
    # ── F. Nối dây send_plan_report.sh (sandbox, --dry-run, không gửi gì) ─────
    if os.environ.get("LAGCAL_SKIP_WIRING") != "1":
        for name, wrap_body, want in (
            ("F: report plan ca C hiện khối ⛔ kèm mã", "real", "LAG_X_SIGNAL_MISMATCH"),
            ("F: checker hỏng ⇒ 'KHÔNG KIỂM ĐƯỢC' + lỗi thật (§29)",
             "raise SystemExit('selfcheck: checker giả hỏng')", "checker giả hỏng"),
        ):
            sb = tempfile.mkdtemp(prefix="lagcal_wire_")
            pdir = os.path.join(sb, "data", "trade_plans")
            os.makedirs(pdir)
            for p in (spx_c, zlp_c):
                q = dict(p, state_source="DT5G_macro", state_name="NEUTRAL", state=3,
                         summary={"action": "HOLD", "reasons": ["selfcheck fixture"]},
                         requires_user_approval=False)
                with open(os.path.join(pdir, f"plan_{p['account']}_{p['plan_date']}.json"), "w") as f:
                    json.dump(q, f, ensure_ascii=False)
            wrap = os.path.join(sb, "wrap.py")
            with open(wrap, "w") as f:
                if wrap_body == "real":
                    f.write("import sys, subprocess\nsys.exit(subprocess.call([sys.executable, "
                            f"{os.path.join(HERE, 'lag_plan_calendar_check.py')!r}, *sys.argv[1:], "
                            f"'--recs-dir', {FX!r}]))\n")
                else:
                    f.write("import sys\nprint('selfcheck: checker giả hỏng', file=sys.stderr)\n"
                            "sys.exit(7)\n")
            env = dict(os.environ, SEND_PLAN_WORKDIR_OVERRIDE=sb,
                       SEND_PLAN_MARKER_DIR=os.path.join(sb, "markers"), SEND_PLAN_LAGCAL_CMD=wrap)
            cp = subprocess.run(["bash", os.path.join(HERE, "send_plan_report.sh"), "--account",
                                 "SpaceX", "--dry-run"], capture_output=True, text=True, env=env,
                                timeout=180)
            outp = cp.stdout + cp.stderr
            ok = want in outp and (wrap_body == "real" or "KHÔNG KIỂM ĐƯỢC" in outp)
            check(name, ok, outp[-400:])
    return passed, failed


def mutations():
    """Phá từng mảnh logic ⇒ suite PHẢI đỏ. Trả list (tên, số test đỏ)."""
    out = []
    muts = {
        "is_trading_day luôn True": ("is_trading_day", lambda d: True),
        "prev_trading_day = lịch trừ 1 ngày": ("prev_trading_day",
                                               lambda d: C._d(d) - C.dt.timedelta(days=1)),
        "_decision luôn None (bỏ so DD)": ("_decision", lambda it: None),
        "_entry_date luôn None": ("_entry_date", lambda it: None),
        "_OTHER_GATE khớp mọi chuỗi": ("_OTHER_GATE", C.re.compile(r"")),
        "ACCOUNT_SPECIFIC_SKIP rỗng": ("ACCOUNT_SPECIFIC_SKIP", set()),
    }
    os.environ["LAGCAL_SKIP_WIRING"] = "1"       # nối dây chạy subprocess ⇒ không thấy mutation
    for name, (attr, val) in muts.items():
        orig = getattr(C, attr)
        setattr(C, attr, val)
        try:
            _, failed = suite(verbose=False)
        except Exception as e:                               # noqa: BLE001
            failed = [f"exception {type(e).__name__}"]
        finally:
            setattr(C, attr, orig)
        out.append((name, len(failed)))
    return out


if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '<unset>')}")
    passed, failed = suite()
    print(f"\nsuite: {len(passed)} PASS / {len(failed)} FAIL")
    print("\nmutation (mỗi dòng phải có ≥1 test đỏ):")
    mut = mutations()
    mut_ok = True
    for name, n in mut:
        print(f"  {'✓' if n else '✗'} {name}: {n} test đỏ")
        mut_ok &= n > 0
    print(f"mutation: {sum(1 for _, n in mut if n)}/{len(mut)} bị bắt")
    sys.exit(0 if (not failed and mut_ok) else 1)
