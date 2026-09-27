#!/usr/bin/env python3
"""Selfcheck cho `daily_nav_snapshot.nav_jump_verdict()` — cổng NAV-jump ×
`data/account_cash_flows.json` (job Taylor_20260927_103434).

Import HÀM THẬT từ `daily_nav_snapshot` (không copy logic) nên mutation test có nghĩa.
Mọi file dòng tiền dùng trong test là file TẠM trong /tmp (tham số `flows_path`) ⇒ selfcheck
KHÔNG đọc và KHÔNG sửa `data/account_cash_flows.json` thật, không gọi broker, không gọi BQ.

Chạy:
  $DNA_PYEXE bin/nav_jump_flow_gate_selfcheck.py              # 4 môi trường TZ
  $DNA_PYEXE bin/nav_jump_flow_gate_selfcheck.py --mutations  # + mutation trên file thật
"""
import json
import os
import subprocess
import sys
import tempfile

# §5b: đặt TRƯỚC mọi import có thể kéo Executor vào, dù daily_nav_snapshot hiện không import nó.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "daily_nav_snapshot.py")

# Lịch sử NAV tổng hợp: 1 tỷ tròn để % đọc ra là số tròn, dễ soi ngưỡng.
HIST = [
    {"date": "2026-09-22", "nav": "1000000000"},
    {"date": "2026-09-23", "nav": "1000000000"},
    {"date": "2026-09-24", "nav": "1000000000"},
]
COMP = {"mtm_stock": 9e8, "cash": 1e8, "debt": 0, "egg": 0, "offbook": 0}
TODAY = "2026-09-25"
PREV = 1_000_000_000.0


def flows_file(records, account="SpaceX", tmpdir=None):
    fd, path = tempfile.mkstemp(suffix=".json", dir=tmpdir)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({account: records}, f)
    return path


def build_cases(verdict):
    """-> list (tên, callable()->list[str] các lỗi)."""
    C = []

    def case(name, fn):
        C.append((name, fn))

    # ---- 1. trong ngưỡng: không tra file, không chặn, không in gì -------------------------
    def c1():
        f = []
        # +14,9% < 15% ⇒ ok, message None. Truyền flows_path trỏ file KHÔNG TỒN TẠI để chứng
        # minh nhánh này thậm chí không cần đọc file.
        ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.149, 15.0, HIST,
                          components=COMP, flows_path="/tmp/__khong_ton_tai__.json")
        if not ok:
            f.append(f"+14,9% phải cho qua, được ok={ok}")
        if msg is not None:
            f.append(f"trong ngưỡng phải im lặng, được message={msg!r}")
        # phía âm
        ok2, msg2 = verdict("SpaceX", TODAY, PREV, PREV * 0.851, 15.0, HIST,
                            components=COMP, flows_path="/tmp/__khong_ton_tai__.json")
        if not ok2 or msg2 is not None:
            f.append(f"-14,9% phải cho qua im lặng, được ok={ok2} msg={msg2!r}")
        return f
    case("trong-nguong-khong-tra-file", c1)

    # ---- 2. vượt ngưỡng, KHÔNG khai dòng tiền ⇒ CHẶN + §29 trích đã đọc gì ---------------
    def c2():
        f = []
        p = flows_file([])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.20, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("+20% không khai dòng tiền PHẢI chặn")
            for need in ("TỰ CHẶN KHÔNG ĐĂNG", "account_cash_flows.json",
                         "0 bản ghi", "KHÔNG có bản ghi nào gán vào 2026-09-25",
                         "CHƯA xác định được nguyên nhân", "market_only"):
                if need not in (msg or ""):
                    f.append(f"thiếu bằng chứng §29 {need!r} trong message")
            if "+20.00%" not in (msg or ""):
                f.append("message không trích đúng biến động đã đo (+20.00%)")
            # KHÔNG được gợi ý nâng env var như lối thoát
            if "chạy lại với NAV_SANITY_MAX_PCT lớn hơn" in (msg or ""):
                f.append("vẫn gợi ý nâng NAV_SANITY_MAX_PCT — đúng lỗi đang sửa")
            if "KHÔNG cần sửa NAV_SANITY_MAX_PCT" not in (msg or ""):
                f.append("không nói rõ khai dòng tiền là cách đi qua đúng")
            if "mtm_stock 900,000,000" not in (msg or ""):
                f.append("không in số thành phần để chẩn đoán nhánh (b)")
        finally:
            os.remove(p)
        return f
    case("vuot-nguong-khong-khai-CHAN", c2)

    # ---- 3. vượt ngưỡng + deposit khai đủ ⇒ CHO QUA, message có vết ----------------------
    def c3():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "sao kê VCB 2026-09-25 ref 998", "timing": "bod"}])
        try:
            # nav 1,2B = 1B + 200tr nạp ⇒ phần dư 0%
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"deposit khai đủ phải CHO QUA, được ok={ok} msg={msg!r}")
            if "ĐƯỢC PHÉP GHI" not in (msg or ""):
                f.append("cho qua mà không để lại vết trong message")
            if "+0.00%" not in (msg or ""):
                f.append("không công bố phần dư sau khi trừ dòng tiền")
            if "sao kê VCB 2026-09-25 ref 998" not in (msg or ""):
                f.append("không trích evidence của bản ghi dòng tiền")
            if "+200,000,000" not in (msg or ""):
                f.append("không trích số tiền đã khai")
        finally:
            os.remove(p)
        return f
    case("deposit-khai-du-CHO-QUA", c3)

    # ---- 4. withdraw khai đủ ⇒ CHO QUA (kiểm cả chiều âm) --------------------------------
    def c4():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": -300_000_000, "kind": "withdraw",
                         "evidence": "rút Trứng vàng, email DNSE 2026-09-25", "timing": "bod"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 700_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"withdraw khai đủ phải CHO QUA, được ok={ok} msg={msg!r}")
            if "-300,000,000" not in (msg or ""):
                f.append("không trích số rút (âm)")
        finally:
            os.remove(p)
        return f
    case("withdraw-khai-du-CHO-QUA", c4)

    # ---- 5. dòng tiền khai KHÔNG giải thích hết ⇒ VẪN CHẶN ------------------------------
    def c5():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 1_000_000, "kind": "deposit",
                         "evidence": "nạp lẻ 1tr", "timing": "bod"}])
        try:
            # khai 1tr nhưng NAV nhảy +50% ⇒ phần dư ~+49,9% ⇒ chặn
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_500_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("khai 1tr mà NAV nhảy +50% PHẢI chặn (bản ghi không phải lời giải thích)")
            if "KHÔNG giải thích hết" not in (msg or ""):
                f.append("không nói rõ dòng tiền không giải thích hết")
            if "+49.90%" not in (msg or ""):
                f.append("không công bố phần dư còn lại sau khi trừ dòng tiền")
            if "nạp lẻ 1tr" not in (msg or ""):
                f.append("không trích bản ghi đã đọc")
        finally:
            os.remove(p)
        return f
    case("dong-tien-khai-thieu-VAN-CHAN", c5)

    # ---- 6. market_only ⇒ CHO QUA dù phần dư vẫn vượt ngưỡng ----------------------------
    def c6():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 0, "kind": "market_only",
                         "evidence": "VNINDEX -6,8% + 4 mã sàn, xác nhận bằng dnse_raw", "timing": "bod"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 800_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if not ok:
                f.append(f"market_only phải CHO QUA, được ok={ok} msg={msg!r}")
            if "market_only" not in (msg or ""):
                f.append("không nói rõ vì sao cho qua")
            if "VNINDEX -6,8%" not in (msg or ""):
                f.append("không trích evidence của market_only")
        finally:
            os.remove(p)
        return f
    case("market_only-CHO-QUA", c6)

    # ---- 7. bản ghi dòng tiền HỎNG ⇒ CHẶN + in đúng lỗi parser (§29) --------------------
    def c7():
        f = []
        # deposit amount âm = sai schema ⇒ CashFlowError
        p = flows_file([{"date": TODAY, "amount_vnd": -5, "kind": "deposit",
                         "evidence": "x", "timing": "bod"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.30, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("bản ghi hỏng PHẢI chặn (không suy 'không có dòng tiền')")
            if "KHÔNG ĐỌC ĐƯỢC" not in (msg or ""):
                f.append("không phân biệt 'không đọc được' với 'không có dòng tiền'")
            if "Lỗi thật:" not in (msg or ""):
                f.append("§29: không in lỗi parser thật")
            if "kind='deposit' phải có amount_vnd>0" not in (msg or ""):
                f.append("§29: không trích nội dung lỗi cụ thể mà parser vừa trả")
            if "KHÔNG nâng NAV_SANITY_MAX_PCT" not in (msg or ""):
                f.append("không cảnh báo lối thoát sai")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-hong-CHAN-va-in-loi-that", c7)

    # ---- 8. dòng tiền của ACCOUNT KHÁC không được tính (§12 tinh thần lọc account) -------
    def c8():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "nạp cho ZaloPay", "timing": "bod"}], account="ZaloPay")
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("dòng tiền của ZaloPay KHÔNG được giải thích cho SpaceX")
            if "0 bản ghi cho 'SpaceX'" not in (msg or ""):
                f.append("không nói rõ đã tra bản ghi của ĐÚNG account nào")
        finally:
            os.remove(p)
        return f
    case("dong-tien-account-khac-khong-tinh", c8)

    # ---- 9. biên ngưỡng: đúng 15,00% cho qua, 15,01% chặn -------------------------------
    def c9():
        f = []
        p = flows_file([])
        try:
            ok_eq, msg_eq = verdict("SpaceX", TODAY, PREV, PREV * 1.15, 15.0, HIST,
                                    components=COMP, flows_path=p)
            if not ok_eq or msg_eq is not None:
                f.append(f"đúng 15,00% phải cho qua im lặng (dùng >, không >=): ok={ok_eq}")
            ok_gt, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.1501, 15.0, HIST,
                               components=COMP, flows_path=p)
            if ok_gt:
                f.append("15,01% phải chặn")
        finally:
            os.remove(p)
        return f
    case("bien-nguong-15pct", c9)

    # ---- 10. bản ghi gần ngày (±3) được NÊU nhưng KHÔNG được coi là giải thích ----------
    def c10():
        f = []
        p = flows_file([{"date": "2026-09-18", "amount_vnd": 200_000_000, "kind": "deposit",
                         "evidence": "nạp tuần trước", "timing": "bod"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            # 09-18 là BOD, dòng nav đầu tiên >= 09-18 là 09-22 ⇒ KHÔNG gán vào 09-25
            if ok:
                f.append("dòng tiền 09-18 (gán vào 09-22) KHÔNG được giải thích cho 09-25")
            if "không có bản ghi nào trong ±3 ngày" not in (msg or ""):
                f.append("phải nói rõ đã soi cả ±3 ngày và không thấy")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-ngay-khac-khong-gan-sai", c10)

    # ---- 11. ngưỡng truyền vào được TÔN TRỌNG (env override vẫn hoạt động) -------------
    def c11():
        f = []
        p = flows_file([])
        try:
            ok, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.20, 25.0, HIST,
                            components=COMP, flows_path=p)
            if not ok:
                f.append("+20% với sanity_max=25 phải cho qua")
            ok2, _ = verdict("SpaceX", TODAY, PREV, PREV * 1.06, 5.0, HIST,
                             components=COMP, flows_path=p)
            if ok2:
                f.append("+6% với sanity_max=5 phải chặn")
        finally:
            os.remove(p)
        return f
    case("nguong-truyen-vao-duoc-ton-trong", c11)

    # ---- 12. file dòng tiền KHÔNG TỒN TẠI + vượt ngưỡng ⇒ chặn, coi như 0 bản ghi ------
    def c12():
        f = []
        ok, msg = verdict("SpaceX", TODAY, PREV, PREV * 1.30, 15.0, HIST,
                          components=COMP, flows_path="/tmp/__khong_ton_tai_2__.json")
        if ok:
            f.append("thiếu file dòng tiền + vượt ngưỡng PHẢI chặn (không mặc định cho qua)")
        if "0 bản ghi" not in (msg or ""):
            f.append("không nói rõ đã tra và thấy 0 bản ghi")
        return f
    case("thieu-file-dong-tien-CHAN", c12)

    # ---- 13. ngưỡng MẶC ĐỊNH của module phải đúng 15,0 (đo từ N=113 phiên) ------------
    def c13():
        import daily_nav_snapshot as dns
        f = []
        if dns.NAV_SANITY_DEFAULT_PCT != 15.0:
            f.append(f"NAV_SANITY_DEFAULT_PCT = {dns.NAV_SANITY_DEFAULT_PCT} (phải 15.0 — "
                     f"đo từ N=113 cặp phiên, max quan sát 4,148%; đổi thì phải đo lại)")
        # 5% (NAV_JUMP_BLOCK_PCT của cổng công bố) phải KHÁC ngưỡng này — hai câu hỏi khác nhau
        from account_cash_flows import NAV_JUMP_BLOCK_PCT
        if NAV_JUMP_BLOCK_PCT == dns.NAV_SANITY_DEFAULT_PCT:
            f.append("cổng ghi nav_history và cổng công bố đang dùng CÙNG ngưỡng — nếu là chủ ý "
                     "thì phải cập nhật comment §28 trong daily_nav_snapshot.py")
        return f
    case("nguong-mac-dinh-15", c13)

    return C


def run_suite(verbose=True):
    import importlib
    import daily_nav_snapshot
    importlib.reload(daily_nav_snapshot)
    verdict = daily_nav_snapshot.nav_jump_verdict
    cases = build_cases(verdict)
    n = 0
    fails = []
    for name, fn in cases:
        n += 1
        try:
            fs = fn()
        except Exception as exc:  # exception trong case = fail, không im lặng
            fs = [f"case raise {type(exc).__name__}: {exc}"]
        for x in fs:
            fails.append(f"{name}: {x}")
    if verbose:
        for x in fails:
            print("  FAIL " + x)
    return n, fails


MUTATIONS = [
    ("nguong-15->95", lambda t: t.replace(
        "NAV_SANITY_DEFAULT_PCT = 15.0", "NAV_SANITY_DEFAULT_PCT = 95.0")),
    ("nguong-mac-dinh-bang-cong-cong-bo", lambda t: t.replace(
        "NAV_SANITY_DEFAULT_PCT = 15.0", "NAV_SANITY_DEFAULT_PCT = 5.0")),
    ("in-nguong-gt->ge", lambda t: t.replace(
        "    if abs(day_change_pct) <= sanity_max:\n        return True, None",
        "    if abs(day_change_pct) < sanity_max:\n        return True, None")),
    ("khong-co-flow-van-cho-qua", lambda t: t.replace(
        "    today_flows = list(mapped.get(date_d, []))\n    if not today_flows:",
        "    today_flows = list(mapped.get(date_d, []))\n    if False:")),
    ("bo-kiem-phan-du", lambda t: t.replace(
        "    if abs(resid_pct) <= sanity_max:\n        return True, (",
        "    if True:\n        return True, (")),
    ("CashFlowError-cho-qua", lambda t: t.replace(
        "    except CashFlowError as exc:\n        # Bản ghi dòng tiền hỏng",
        "    except CashFlowError as exc:\n        return True, str(exc)\n        # Bản ghi dòng tiền hỏng")),
    ("resid-khong-tru-flow", lambda t: t.replace(
        "    resid_pct = ((nav - net_flow) / prev_nav - 1) * 100 if prev_nav else 0.0",
        "    resid_pct = (nav / prev_nav - 1) * 100 if prev_nav else 0.0")),
    ("market_only-bo-dieu-kien-amount", lambda t: t.replace(
        'if "market_only" in kinds and net_flow == 0:',
        'if "market_only" in kinds or True:')),
    ("net_flow-dao-dau", lambda t: t.replace(
        '    net_flow = sum(f["amount_vnd"] for f in today_flows)',
        '    net_flow = -sum(f["amount_vnd"] for f in today_flows)')),
    ("bo-loi-that-CashFlowError", lambda t: t.replace(
        'f"   Lỗi thật: {exc}\\n"', 'f"   (không xác định)\\n"')),
    ("bo-so-thanh-phan", lambda t: t.replace(
        "kiểm vị thế thiếu/giá sai ({_comp_line()}).", "kiểm vị thế thiếu/giá sai.")),
]


def child():
    n, fails = run_suite()
    print(f"__RESULT__ cases={n} fails={len(fails)}")
    return 1 if fails else 0


def main():
    args = sys.argv[1:]
    if os.environ.get("_NJF_CHILD") == "1":
        return child()

    tzs = [("ICT", "Asia/Ho_Chi_Minh"), ("UTC", "UTC"),
           ("NY", "America/New_York"), ("no-TZ", None)]
    print(f"target: {TARGET}")
    print(f"môi trường TZ: {[t[0] for t in tzs]}")
    rc = 0
    results = {}
    for tzname, tz in tzs:
        env = dict(os.environ, _NJF_CHILD="1")
        env.pop("TZ", None)
        if tz:
            env["TZ"] = tz
        out = subprocess.run([sys.executable, os.path.abspath(__file__)],
                             capture_output=True, text=True, env=env, timeout=300)
        line = [x for x in out.stdout.splitlines() if x.startswith("__RESULT__")]
        print(f"\n--- TZ={tzname} rc={out.returncode}")
        for x in out.stdout.splitlines():
            if not x.startswith("__RESULT__"):
                print(x if x.startswith("  ") else "  " + x)
        if not line:
            print(f"  FATAL: không đọc được __RESULT__ — stderr={out.stderr[-600:]}")
            rc = 1
            continue
        print("  " + line[0])
        results[tzname] = line[0]
        if out.returncode != 0:
            rc = 1
    if len(set(results.values())) > 1:
        print("\nFAIL: kết quả KHÁC nhau giữa các múi giờ:")
        for k, v in results.items():
            print(f"  {k}: {v}")
        rc = 1
    elif results:
        print(f"\nBẤT BIẾN theo TZ: cả {len(results)} môi trường cho cùng kết quả ✓")

    if "--mutations" in args or "--all" in args:
        orig = open(TARGET, encoding="utf-8").read()
        print(f"\nMUTATION ({len(MUTATIONS)} đột biến trên CHÍNH file thật):")
        killed, survived = 0, []
        try:
            for mname, mfn in MUTATIONS:
                mutated = mfn(orig)
                if mutated == orig:
                    survived.append(f"{mname} (KHÔNG áp được — pattern không khớp code hiện tại)")
                    print(f"  SKIP-NOAPPLY {mname}")
                    continue
                open(TARGET, "w", encoding="utf-8").write(mutated)
                env = dict(os.environ, _NJF_CHILD="1", TZ="Asia/Ho_Chi_Minh")
                out = subprocess.run([sys.executable, os.path.abspath(__file__)],
                                     capture_output=True, text=True, env=env, timeout=300)
                if out.returncode != 0:
                    killed += 1
                    nf = [x for x in out.stdout.splitlines() if x.startswith("__RESULT__")]
                    print(f"  killed   {mname}  ({nf[0] if nf else 'crash'})")
                else:
                    survived.append(mname)
                    print(f"  SURVIVED {mname}")
        finally:
            open(TARGET, "w", encoding="utf-8").write(orig)   # luôn phục hồi file thật
        # chứng minh đã phục hồi đúng
        if open(TARGET, encoding="utf-8").read() != orig:
            print("  FATAL: KHÔNG phục hồi được file thật sau mutation")
            rc = 1
        else:
            print("  (file thật đã được phục hồi nguyên trạng ✓)")
        print(f"\nMUTATION: {killed}/{len(MUTATIONS)} bị giết")
        if survived:
            print("  sống sót: " + "; ".join(survived))
            rc = 1

    print("\n" + ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
