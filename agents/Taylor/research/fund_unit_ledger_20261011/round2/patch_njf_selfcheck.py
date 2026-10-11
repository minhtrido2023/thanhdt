#!/usr/bin/env python3
"""Vá một lần `bin/nav_jump_flow_gate_selfcheck.py` cho luật gán D1 (job Taylor_20261010_182122).
Chạy: python3 patch_njf_selfcheck.py <đường dẫn file selfcheck>"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)


rep('''HIST = [
    {"date": "2026-09-22", "nav": "1000000000"},
    {"date": "2026-09-23", "nav": "1000000000"},
    {"date": "2026-09-24", "nav": "1000000000"},
]''', '''HIST = [
    {"date": "2026-09-22", "nav": "1000000000", "balance_ts": "2026-09-22T19:10:07"},
    {"date": "2026-09-23", "nav": "1000000000", "balance_ts": "2026-09-23T19:10:12"},
    {"date": "2026-09-24", "nav": "1000000000", "balance_ts": "2026-09-24T19:10:09"},
]
# Lúc chụp số dư của dòng HÔM NAY (dòng sắp ghi) — luật gán dòng tiền so với mốc này.
TODAY_TS = "2026-09-25T19:10:30"''')

rep('''    C = []

    def case(name, fn):
        C.append((name, fn))
''', '''    C = []
    raw_verdict = verdict

    def verdict(*a, **k):                     # mọi case mặc định: dòng hôm nay chụp lúc TODAY_TS
        k.setdefault("balance_ts", TODAY_TS)
        return raw_verdict(*a, **k)

    def case(name, fn):
        C.append((name, fn))
''')

rep('''"evidence": "VNINDEX -6,8% + 4 mã sàn, xác nhận bằng dnse_raw", "timing": "bod", "time_ict": "10:00"}])''',
    '''"evidence": "VNINDEX -6,8% + 4 mã sàn, xác nhận bằng dnse_raw"}])''')

NEW_CASES = r'''    # ---- 14. NẠP CUỐI TUẦN (arch-review N3): thứ Bảy 09-26 nạp 200tr, dòng thứ Hai 09-28 +20% --
    HIST_FRI = HIST + [{"date": "2026-09-25", "nav": "1000000000", "balance_ts": TODAY_TS}]
    MON, MON_TS = "2026-09-28", "2026-09-28T19:10:11"

    def c14():
        f = []
        for label, rec in (("thứ Bảy 10:00", {"date": "2026-09-26", "time_ict": "10:00"}),
                           ("thứ Sáu 20:00 (sau lần chụp)", {"date": "2026-09-25", "time_ict": "20:00"}),
                           ("thứ Hai 08:30", {"date": MON, "time_ict": "08:30"}),
                           ("thứ Hai 16:00 (sau đóng cửa)", {"date": MON, "time_ict": "16:00"})):
            p = flows_file([dict(rec, amount_vnd=200_000_000, kind="deposit", evidence="sao kê DNSE")])
            try:
                ok, msg = verdict("SpaceX", MON, PREV, 1_200_000_000.0, 15.0, HIST_FRI,
                                  components=COMP, flows_path=p, balance_ts=MON_TS)
                if not ok:
                    f.append(f"nạp {label} phải giải thích dòng thứ Hai, được ok={ok} msg={msg!r}")
                for need in ("ĐƯỢC PHÉP GHI", "+0.00%", "+200,000,000", "sao kê DNSE"):
                    if need not in (msg or ""):
                        f.append(f"nạp {label}: message thiếu {need!r}: {msg!r}")
                want = "[timing=eod]" if "16:00" in label else "[timing=bod]"
                if want not in (msg or ""):
                    f.append(f"nạp {label}: message phải nêu quy ước suy ra {want}: {msg!r}")
            finally:
                os.remove(p)
        return f
    case("nap-cuoi-tuan-giai-thich-dong-thu-hai", c14)

    # ---- 15. tiền vào SAU lần chụp hôm nay KHÔNG giải thích bước nhảy hôm nay ----------------
    def c15():
        f = []
        p = flows_file([{"date": TODAY, "time_ict": "20:00", "amount_vnd": 200_000_000,
                         "kind": "deposit", "evidence": "nạp tối nay"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("tiền 20:00 (sau lần chụp 19:10:30) KHÔNG được giải thích bước nhảy hôm nay")
            for need in ("1 bản ghi cho 'SpaceX'", "KHÔNG có bản ghi nào gán vào 2026-09-25",
                         "gần nhất trong ±3 ngày: 2026-09-25"):
                if need not in (msg or ""):
                    f.append(f"message thiếu {need!r}: {msg!r}")
        finally:
            os.remove(p)
        return f
    case("tien-sau-lan-chup-khong-giai-thich-hom-nay", c15)

    # ---- 16. file ĐỌC ĐƯỢC nhưng không GÁN được ⇒ chặn, tiêu đề nói ĐÚNG điều đó (§29) -------
    def c16():
        f = []
        p = flows_file([{"date": TODAY, "time_ict": "10:00", "amount_vnd": 200_000_000,
                         "kind": "deposit", "evidence": "sao kê"}])
        try:
            for label, kw, need in (
                    ("dòng hôm nay thiếu balance_ts", {"balance_ts": None},
                     "dòng nav_history 2026-09-25 không có balance_ts (đọc được: None)"),
                    ("dòng hôm nay balance_ts hỏng", {"balance_ts": "tối nay"}, "'tối nay'")):
                ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                                  components=COMP, flows_path=p, **kw)
                if ok:
                    f.append(f"{label}: không gán được bản ghi thì PHẢI chặn")
                for n2 in ("đọc được (1 bản ghi cho 'SpaceX')", "KHÔNG GÁN ĐƯỢC", "Lỗi thật:", need,
                           "KHÔNG nâng NAV_SANITY_MAX_PCT"):
                    if n2 not in (msg or ""):
                        f.append(f"{label}: message thiếu {n2!r}: {msg!r}")
                if "KHÔNG ĐỌC ĐƯỢC" in (msg or ""):
                    f.append(f"{label}: file đọc được mà tiêu đề vẫn nói 'KHÔNG ĐỌC ĐƯỢC'")
            hist_bad = [dict(r) for r in HIST]
            hist_bad[-1]["balance_ts"] = ""
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, hist_bad,
                              components=COMP, flows_path=p)
            if ok or "dòng nav_history 2026-09-24 không có balance_ts" not in (msg or ""):
                f.append(f"dòng lịch sử liền trước thiếu balance_ts phải chặn + nêu đúng dòng: {msg!r}")
            hist_dup = HIST + [dict(HIST[-1])]
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, hist_dup,
                              components=COMP, flows_path=p)
            if ok or "HAI dòng cùng ngày" not in (msg or "") or "KHÔNG GÁN ĐƯỢC" not in (msg or ""):
                f.append(f"nav_history trùng ngày phải chặn bằng thông điệp, không sập: {msg!r}")
        finally:
            os.remove(p)
        return f
    case("doc-duoc-nhung-khong-gan-duoc-CHAN", c16)

    # ---- 17. bản ghi thiếu giờ ⇒ chặn ở bước ĐỌC, tiêu đề 'KHÔNG ĐỌC ĐƯỢC' ------------------
    def c17():
        f = []
        p = flows_file([{"date": TODAY, "amount_vnd": 200_000_000, "kind": "deposit", "evidence": "x"}])
        try:
            ok, msg = verdict("SpaceX", TODAY, PREV, 1_200_000_000.0, 15.0, HIST,
                              components=COMP, flows_path=p)
            if ok:
                f.append("bản ghi thiếu time_ict PHẢI chặn (không còn mặc định timing)")
            for need in ("KHÔNG ĐỌC ĐƯỢC", "Lỗi thật:", "thiếu time_ict"):
                if need not in (msg or ""):
                    f.append(f"message thiếu {need!r}: {msg!r}")
            if "KHÔNG GÁN ĐƯỢC" in (msg or ""):
                f.append("lỗi ở bước ĐỌC mà tiêu đề lại nói 'KHÔNG GÁN ĐƯỢC'")
        finally:
            os.remove(p)
        return f
    case("ban-ghi-thieu-gio-CHAN", c17)

    # ---- 18. main() PHẢI truyền balance_ts của dòng sắp ghi — thiếu thì mọi ngày có dòng tiền
    # đều bị chặn oan ở cron (test hàm không bắt được việc tháo tham số ở chỗ gọi).
    def c18():
        src = open(TARGET, encoding="utf-8").read().split("def main(")[1]
        call = src.split("nav_jump_verdict(")[1].split("if jump_msg:")[0]
        return [] if 'balance_ts=bal["ts"]' in call else [
            f"main() gọi nav_jump_verdict mà không truyền balance_ts của dòng sắp ghi: {call!r}"]
    case("main-truyen-balance_ts", c18)

    return C


def run_suite(verbose=True):'''
rep('''    return C


def run_suite(verbose=True):''', NEW_CASES)

OLD_MUT = '''    ("bo-loi-that-CashFlowError", lambda t: t.replace(
        'f"   Lỗi thật: {exc}\\\\n"', 'f"   (không xác định)\\\\n"')),'''
NEW_MUT = r'''    ("bo-loi-that-CashFlowError", lambda t: t.replace(
        "Lỗi thật: {exc}", "(không xác định)")),
    ("loi-gan-cho-qua", lambda t: t.replace(
        "    except ValueError as exc:               # CashFlowError (thiếu giờ/balance_ts…) là ValueError",
        "    except ValueError as exc:\n        return True, str(exc)")),
    ("loi-gan-chi-bat-CashFlowError", lambda t: t.replace(
        "    except ValueError as exc:               # CashFlowError (thiếu giờ/balance_ts…) là ValueError",
        "    except CashFlowError as exc:")),
    ("tieu-de-gan-noi-khong-doc-duoc", lambda t: t.replace(
        "nhưng KHÔNG GÁN ĐƯỢC bản ghi vào phiên nào", "KHÔNG ĐỌC ĐƯỢC")),
    ("bo-balance_ts-dong-hom-nay", lambda t: t.replace(
        "+ [NavRow(date_d, nav, balance_ts=balance_ts)])", "+ [NavRow(date_d, nav)])")),
    ("bo-balance_ts-lich-su", lambda t: t.replace(
        '                balance_ts=(r.get("balance_ts") or None)) for r in hist_rows',
        '                balance_ts=None) for r in hist_rows')),
    ("lich-su-lay-ca-dong-hom-nay", lambda t: t.replace(
        'if r.get("date") and r["date"] < date and r.get("nav")]',
        'if r.get("date") and r["date"] <= date and r.get("nav")]')),
    ("main-bo-balance_ts", lambda t: t.replace(
        '"egg": egg_value, "offbook": offbook}, balance_ts=bal["ts"])',
        '"egg": egg_value, "offbook": offbook})')),'''
rep(OLD_MUT, NEW_MUT)
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
