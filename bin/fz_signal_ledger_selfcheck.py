#!/usr/bin/env python3
"""Selfcheck fz_signal_ledger.py — chạy: env -u TZ python3 bin/fz_signal_ledger_selfcheck.py"""
import csv
import os
import sys
import tempfile
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fz_signal_ledger as L  # noqa: E402

FAILS = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def mkrow(setup="FZ-001", sym="AAA", sday="2026-11-10", ent=100.0, ex=106.0, fe=1.0, fx=1.0,
          drift=0.01, in_stats=1, status="closed", sid=None, entry="2026-11-11", exitd="2026-11-20"):
    net_old = L.net_ret(ent, fe, ex, fx, L.FEE_EXPORT, L.TAX_SELL)
    return {
        "setup": setup, "signal_day": sday, "symbol": sym, "status": status,
        "entry_ts": f"{entry} 09:15:00+07:00", "exit_ts": f"{exitd} 14:45:00+07:00",
        "exit_reason": "tp", "hold_sessions": 7, "entry_px": ent, "exit_px": ex, "f_entry": fe,
        "f_exit": fx, "net_ret_total": f"{net_old:.7f}", "market_drift_same_day": drift,
        "in_stats": in_stats, "signal_id": sid or f"{setup}:{sym}|{setup}:{sday}",
    }


def write_csv(path, rows, drop=None):
    cols = [c for c in L.REQUIRED_IN if c != drop]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


RATE = lambda d: 2.0  # noqa: E731
NOW = datetime(2026, 11, 20, 10, 0, tzinfo=L.ICT)


def ing(src, led, **kw):
    return L.ingest(src, led, rate_fn=kw.pop("rate_fn", RATE), now=NOW, **kw)


def main():
    td = tempfile.mkdtemp()
    led = os.path.join(td, "led.csv")
    src = os.path.join(td, "deals.csv")

    # 1. số học phí thật + excess nhân hệ số
    n = L.net_ret(100, 1, 106, 1, L.FEE_REAL, L.TAX_SELL)
    expect = 1.06 * (1 - 0.00097 - 0.001) / 1.00097 - 1
    check("net_ret phí thật 0,097%+thuế 0,1%", abs(n - expect) < 1e-12)
    check("rổ cùng phí: drift_export=0 => basket = K_real/K_old-1 (<0)", L.fee_adjust_basket(0.0) < 0)
    check("basket nhân hệ số, không cộng", abs(L.fee_adjust_basket(0.01) - (1.01 * L._k(L.FEE_REAL, L.TAX_SELL) / L._k(L.FEE_EXPORT, L.TAX_SELL) - 1)) < 1e-15)

    # 2. ingest cơ bản: lọc setup lạ / open / in_stats=0 / trước forward
    rows = [mkrow(sym="A"), mkrow(sym="B", setup="C-ONID"), mkrow(sym="C", status="open"),
            mkrow(sym="D", in_stats=0), mkrow(sym="E", sday="2026-10-01"),
            mkrow(sym="F", fe=1.0, fx=0.97, ex=103.0)]  # F có ex-date (f đổi)
    write_csv(src, rows)
    st = ing(src, led)
    got = list(csv.DictReader(open(led)))
    check("ingest: 2 dòng được ghi (A,F)", st["added"] == 2 and [g["symbol"] for g in got] == ["A", "F"], str(st))
    check("ingest: loại đúng lý do", (st["skip_other_setup"], st["skip_not_closed"], st["skip_overlap"], st["skip_before_forward"]) == (1, 1, 1, 1), str(st))
    a = got[0]
    check("net_ret_total sổ = phí thật", abs(float(a["net_ret_total"]) - n) < 1e-7)
    check("excess_vs_basket = net - basket", abs(float(a["excess_vs_basket"]) - (n - L.fee_adjust_basket(0.01))) < 1e-7)
    dep = 0.02 * 9 / 365
    check("dep pro-rata theo ngày lịch entry→exit", abs(float(a["dep_prorata"]) - dep) < 1e-7 and abs(float(a["excess_vs_dep"]) - (n - dep)) < 1e-7)
    f = got[1]
    check("giá điều chỉnh f_exit tính vào return", abs(float(f["gross_ret_adj"]) - (103 / 0.97 / 100 - 1)) < 1e-7)

    # 3. idempotent: ingest lại không đổi byte
    b1 = open(led, "rb").read()
    st2 = ing(src, led)
    check("idempotent: lần 2 added=0, byte y hệt", st2["added"] == 0 and st2["duplicate_skipped"] == 2 and open(led, "rb").read() == b1, str(st2))

    # 4. append-only: file thêm dòng mới, dòng cũ giữ nguyên là tiền tố
    write_csv(src, rows + [mkrow(sym="G", sday="2026-11-12", sid="FZ-001:G|x")])
    ing(src, led)
    b2 = open(led, "rb").read()
    check("append-only: bản cũ là tiền tố bản mới + thêm 1 dòng", b2.startswith(b1) and len(b2) > len(b1) and b2.count(b"\n") == b1.count(b"\n") + 1)

    # 5. trùng signal_id trong file => fail-closed, sổ không đổi
    write_csv(src, [mkrow(sym="H"), mkrow(sym="H")])
    try:
        ing(src, led)
        ok = False
    except L.LedgerError:
        ok = True
    check("trùng signal_id trong file => LedgerError, sổ không đổi", ok and open(led, "rb").read() == b2)

    # 6. thiếu cột => fail-closed
    write_csv(src, [mkrow(sym="I")], drop="market_drift_same_day")
    try:
        ing(src, led)
        ok = False
    except L.LedgerError as e:
        ok = "market_drift_same_day" in str(e)
    check("thiếu cột => LedgerError nêu tên cột, sổ không đổi", ok and open(led, "rb").read() == b2)

    # 7. xung đột: cùng signal_id, khác giá trị => fail-closed, KHÔNG ghi dòng khác trong file
    write_csv(src, [mkrow(sym="J"), mkrow(sym="A", ex=90.0)])
    try:
        ing(src, led)
        ok = False
    except L.LedgerError as e:
        ok = "KHÁC" in str(e)
    check("cùng id khác giá trị => LedgerError, không ghi dòng J", ok and open(led, "rb").read() == b2)

    # 8. NaN / giá <=0 / net_ret_total lệch phí export => fail-closed
    for label, bad in [("NaN", {**mkrow(sym="K"), "exit_px": float("nan")}),
                       ("giá<=0", {**mkrow(sym="K"), "entry_px": 0.0}),
                       ("net_ret_total lệch", {**mkrow(sym="K"), "net_ret_total": "0.5"})]:
        write_csv(src, [bad])
        try:
            ing(src, led)
            ok = False
        except (L.LedgerError, ZeroDivisionError):
            ok = True
        check(f"{label} => fail-closed", ok and open(led, "rb").read() == b2)

    # 9. lãi dep1m lỗi => fail-closed
    write_csv(src, [mkrow(sym="L")])
    try:
        ing(src, led, rate_fn=lambda d: float("nan"))
        ok = False
    except L.LedgerError:
        ok = True
    check("rate NaN => fail-closed", ok and open(led, "rb").read() == b2)

    # 10. atomic: không để lại file tmp; os.replace được dùng (kill giữa chừng không làm hỏng sổ)
    check("không còn file .tmp", not [x for x in os.listdir(td) if ".tmp." in x])
    real_replace = os.replace
    boom = {"n": 0}

    def bad_replace(a_, b_):
        boom["n"] += 1
        raise OSError("giả lập chết đúng lúc replace")
    write_csv(src, [mkrow(sym="M", sday="2026-11-13", sid="FZ-001:M|x")])
    os.replace = bad_replace
    try:
        ing(src, led)
    except OSError:
        pass
    finally:
        os.replace = real_replace
    check("chết ở os.replace => sổ giữ nguyên byte (không nửa vời)", boom["n"] == 1 and open(led, "rb").read() == b2)
    for x in os.listdir(td):
        if ".tmp." in x:
            os.remove(os.path.join(td, x))

    # 11. cụm: gap<=5 phiên cùng cụm, >5 tách; theo từng setup
    cl = [{"setup": "FZ-001", "signal_day": d, "symbol": "X", "excess_vs_basket": "0.01", "excess_vs_dep": "0.01"}
          for d in ["2026-11-02", "2026-11-04", "2026-11-09", "2026-11-23"]]  # 02→04:2, 04→09:3 (cùng), 09→23:10 (tách)
    cs = L.build_clusters(cl)["FZ-001"]
    check("cụm: [02,04,09] + [23]", [len(c) for c in cs] == [3, 1], str([len(c) for c in cs]))
    check("sessions_between loại T7/CN", L.sessions_between(date(2026, 11, 6), date(2026, 11, 9)) == 1)

    # 12. stop-early: 10 cụm đóng, mean excess <=0 => cờ; >0 => không cờ; <20 => go_eligible no
    def synth(excess):
        p = os.path.join(td, f"s_{excess}.csv")
        rs = []
        for i in range(10):
            d = date(2026, 11, 4).toordinal() + 14 * i  # cách 14 ngày lịch >5 phiên
            sd = date.fromordinal(d)
            while sd.weekday() >= 5:
                sd = date.fromordinal(sd.toordinal() + 1)
            rs.append({c: "" for c in L.LEDGER_COLS} | {
                "signal_id": f"S:{i}", "setup": "FZ-002", "signal_day": sd.isoformat(), "symbol": "Z",
                "excess_vs_basket": str(excess), "excess_vs_dep": str(excess)})
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=L.LEDGER_COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(rs)
        return p
    r0 = L.summarize(synth(-0.001), asof=date(2027, 6, 1))[0]
    r1 = L.summarize(synth(0.02), asof=date(2027, 6, 1))[0]
    check("10 cụm excess<0 => stop_early", r0["stop_early"] and r0["clusters_closed"] == 10)
    check("10 cụm excess>0 => không stop; <20 cụm => chưa xét GO", (not r1["stop_early"]) and (not r1["go_eligible_n"]))
    r2 = L.summarize(synth(-0.001), asof=date(2026, 12, 20))[0]
    check("cụm chưa 'đóng' (asof gần) không tính vào N", r2["clusters_closed"] < 10 and not r2["stop_early"])

    # 13. TZ: kết quả không phụ thuộc TZ host (ngày lấy từ chuỗi, now neo ICT)
    check("ingested_at mang offset +07:00", got[0]["ingested_at"].endswith("+07:00"))

    print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + str(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
