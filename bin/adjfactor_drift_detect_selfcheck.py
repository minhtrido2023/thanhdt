#!/usr/bin/env python3
"""Selfcheck cho LAYER 1 detect-only: `adjfactor_drift_detect.py` + `adjfactor_drift_alert.sh`.

Chạy KHÔNG cần BigQuery: mọi assertion về CÔNG THỨC và về NGƯỠNG dùng chuỗi giá tổng hợp, dựng
đúng CHỮ KÝ của các ca thật đã đo (FPT/VPB/XHC/GEX/DGC/DXG + ffill toàn thị trường 2026-01-30).
Phần `alert.sh` chạy trong ROOT sandbox với `notify_thread.sh`/`append_event.sh` là stub, nên
selfcheck KHÔNG BAO GIỜ gửi Discord thật hay ghi bus thật.

  python3 bin/adjfactor_drift_detect_selfcheck.py            # tất cả
  python3 bin/adjfactor_drift_detect_selfcheck.py --py       # chỉ phần Python
  python3 bin/adjfactor_drift_detect_selfcheck.py --sh       # chỉ phần shell

§16/§19: phần shell chạy LẶP dưới 3 môi trường TZ (`env -u TZ`, `TZ=UTC`, `TZ=America/New_York`)
— một selfcheck thừa hưởng đúng `TZ` của tác giả thì PASS bất kể code có neo TZ hay không.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adjfactor_drift_detect as det  # noqa: E402

FAILS = []
N = 0
VACUOUS = []       # môi trường TZ mà ở thời điểm chạy này không phân biệt được ngày với ICT
NON_VACUOUS = []


def ck(label, cond, detail=""):
    global N
    N += 1
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}   {detail}")
        FAILS.append(label)


def bar(d, price, close, lo=None, hi=None):
    """Một phiên. lo/hi mặc định bao quanh `close` (frame ĐÃ điều chỉnh, đúng như BQ)."""
    return {"d": d, "price": float(price), "close": float(close),
            "lo": float(lo if lo is not None else close * 0.99),
            "hi": float(hi if hi is not None else close * 1.01)}


def ev(ex, code, method=None, ratio=None, dps=None, tk="XXX"):
    return {"ticker": tk, "exright_date": ex, "event_code": code,
            "issue_method_name_vi": method, "exercise_ratio": ratio, "value_per_share": dps}


def flat_series(dates, price, r_vendor):
    """Chuỗi trong đó hệ số vendor ẩn = `r_vendor` ở mọi phiên (Close = Price / r_vendor)."""
    return [bar(d, price, price / r_vendor) for d in dates]


D = [f"2026-0{m}-{dd:02d}" for m in (6, 7, 8) for dd in range(1, 11)]   # 30 "phiên"


# ---------------------------------------------------------------- 1. công thức

def t_formula():
    print("\n[1] group_price_factor — công thức giá tham chiếu của sàn")
    s = [bar("2026-05-04", 46750, 46750)]

    f, code, _n = det.group_price_factor("2026-05-05", [ev("2026-05-05", "ISS", "Cổ phiếu thưởng", 0.1)], s)
    ck("thưởng 10% -> f=1.1", f == 1.1 and code == "", f"f={f} code={code!r}")

    # GEX 2026-05-05: sàn dùng 1+0,45 = 1,450 (vendor 1,450191); TÍCH 1,20*1,25 = 1,500 lệch -3,32%
    f, _c, _n = det.group_price_factor("2026-05-05", [
        ev("2026-05-05", "ISS", "Cổ phiếu thưởng", 0.20),
        ev("2026-05-05", "ISS", "Trả Cổ tức bằng Cổ phiếu", 0.25)], s)
    ck("GEX cùng ngày: CỘNG tỉ lệ -> 1.45", abs(f - 1.45) < 1e-9, f"f={f}")
    ck("GEX: KHÔNG phải tích 1.20*1.25=1.50", abs(f - 1.50) > 1e-3, f"f={f}")

    # DGC 2026-09-14: tiền 3.000 + 5.000 trên giá thô 46.750 -> 46750/38750 = 1,206452
    f, _c, _n = det.group_price_factor("2026-09-14", [
        ev("2026-09-14", "DIV", dps=3000), ev("2026-09-14", "DIV", dps=5000)], s)
    ck("DGC cùng ngày: CỘNG tiền -> 1.206452", abs(f - 46750 / 38750) < 1e-9, f"f={f}")
    ck("DGC: KHÔNG phải tích hai hệ số đơn (1.196544)", abs(f - 1.196544) > 1e-3, f"f={f}")

    # Chân cổ phiếu + chân tiền cùng ngày: (1+q) * P/(P-D), không phải cộng rời
    f, _c, _n = det.group_price_factor("2026-09-14", [
        ev("2026-09-14", "ISS", "Cổ phiếu thưởng", 0.1), ev("2026-09-14", "DIV", dps=1000)], s)
    ck("cổ phiếu + tiền cùng ngày -> (1+q)*P/(P-D)",
       abs(f - 1.1 * 46750 / 45750) < 1e-9, f"f={f}")


# ------------------------------------------------------ 2. fail-closed + mã lý do

def t_failclosed():
    print("\n[2] UNCOMPUTABLE — fail-closed, mã lý do suy TỪ bằng chứng (§29)")
    s = [bar("2026-05-04", 46750, 46750)]
    cases = [
        ("quyền mua cổ đông hiện hữu", [ev("2026-05-05", "ISS", det.RIGHTS_METHOD, 0.5)],
         "rights_issue_no_subscription_price"),
        ("ISS ratio không parse", [ev("2026-05-05", "ISS", "Cổ phiếu thưởng", "abc")],
         "iss_ratio_unparsable"),
        ("ISS ratio <= 0", [ev("2026-05-05", "ISS", "Cổ phiếu thưởng", 0)],
         "iss_ratio_nonpositive"),
        ("DIV dps không parse", [ev("2026-05-05", "DIV", dps="x")], "div_dps_unparsable"),
        ("DIV dps <= 0", [ev("2026-05-05", "DIV", dps=0)], "div_dps_nonpositive"),
        ("event_code lạ", [ev("2026-05-05", "XXX")], "unsupported_event_code"),
        ("tiền >= giá thô", [ev("2026-05-05", "DIV", dps=999999)], "cash_exceeds_price"),
    ]
    for label, evs, want in cases:
        f, code, note = det.group_price_factor("2026-05-05", evs, s)
        ck(f"{label} -> None + {want}", f is None and code == want, f"f={f} code={code!r}")
        ck(f"{label}: note có số/giá trị thật, không phải câu đoán",
           any(ch.isdigit() for ch in note), f"note={note!r}")

    f, code, _n = det.group_price_factor("2026-05-01", [ev("2026-05-01", "DIV", dps=500)], s)
    ck("không có phiên cum trong cửa sổ -> no_cum_session_in_window",
       f is None and code == "no_cum_session_in_window", f"f={f} code={code!r}")

    # Sự kiện CỔ PHIẾU THUẦN vẫn tính được kể cả khi dòng giá không dùng được (không cần giá nào)
    f, _c, _n = det.group_price_factor("2026-05-05", [ev("2026-05-05", "ISS", "Cổ phiếu thưởng", 0.1)], [])
    ck("cổ phiếu thuần: tính được dù KHÔNG có dòng giá nào", f == 1.1, f"f={f}")


# --------------------------------------------------------- 3. guard ffill Price

def t_ffill_guard():
    print("\n[3] price_stale_suspect — guard ffill `Price`, và KHÔNG bắt oan dòng khoẻ")
    # Ca FPT 2025-06-11 (regression thật): Price THÔ 117.900 cao hẳn trên band ĐÃ ĐIỀU CHỈNH
    # [97.750, 99.520]. Bản naive so trực tiếp -> bắt oan 44/51 mã control.
    healthy = [bar("2025-06-10", 117000, 98500, lo=97000, hi=99000),
               bar("2025-06-11", 117900, 98800, lo=97750, hi=99520)]
    ck("dòng KHOẺ (Price thô trên band đã điều chỉnh) KHÔNG bị nghi",
       det.price_stale_suspect(healthy, 1) is False)

    # ffill thật: Price = đúng close của T-1 trong khi band của T không chứa nó
    ffill = [bar("2026-01-29", 117000, 117000, lo=116000, hi=118000),
             bar("2026-01-30", 116800, 120000, lo=119500, hi=121000)]
    ck("dòng ffill (Price ngoài band đã nâng về frame thô) BỊ nghi",
       det.price_stale_suspect(ffill, 1) is True)

    ck("phiên đầu chuỗi (không có láng giềng) KHÔNG kết luận nghi",
       det.price_stale_suspect(ffill, 0) is False)
    ck("thiếu hi/lo -> KHÔNG kết luận nghi",
       det.price_stale_suspect([bar("a", 1, 1, 0, 0), bar("b", 1, 1, 0, 0)], 1) is False)

    # Guard được unit-test ở trên, nhưng KHÔNG có gì chốt rằng `group_price_factor` THẬT SỰ GỌI nó.
    # Mutation M11 (arch-review 2026-09-27) xoá lệnh gọi mà vẫn 142/142 PASS ⇒ một `Price` đã ffill
    # sẽ được dùng làm `P_cum` và sinh cáo buộc SAI. Chốt bằng cách theo dõi lệnh gọi thật.
    calls = []
    real = det.price_stale_suspect
    try:
        det.price_stale_suspect = lambda ser, i: (calls.append((len(ser), i)), real(ser, i))[1]
        det.group_price_factor("2026-05-05", [ev("2026-05-05", "DIV", dps=500)],
                               [bar("2026-05-03", 46750, 46750), bar("2026-05-04", 46750, 46750)])
    finally:
        det.price_stale_suspect = real
    ck("group_price_factor THẬT SỰ gọi price_stale_suspect cho chân tiền (M11)",
       len(calls) == 1 and calls[0][1] == 1, f"calls={calls}")


# ------------------------------------------------------------- 4. đường hệ số

def t_curve():
    print("\n[4] build_factor_curve — tích theo ex-date, dedupe, taxonomy")
    s = [bar(d, 100, 100) for d in D]
    # Hai ex-date NẰM TRONG chuỗi (D = ngày 01..10 mỗi tháng) để kiểm được cả biên "ex == t".
    evs = [ev("2026-07-05", "ISS", "Cổ phiếu thưởng", 0.1),
           ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2)]
    curve, used, _notes, unknown, corr0 = det.build_factor_curve(s, evs)
    ck("2 ex-date liên tiếp: r_pred trước cả hai = 1.1*1.2",
       abs(curve["2026-06-01"] - 1.32) < 1e-9, f"{curve['2026-06-01']}")
    ck("giữa hai ex-date: chỉ hệ số của ex-date SAU",
       abs(curve["2026-07-10"] - 1.2) < 1e-9, f"{curve['2026-07-10']}")
    ck("sau cả hai: r_pred = 1.0", abs(curve["2026-08-10"] - 1.0) < 1e-9, f"{curve['2026-08-10']}")
    ck("ex-date ĐÚNG ngày không tính hệ số của CHÍNH nó (tích lấy ex > t)",
       abs(curve["2026-07-05"] - 1.2) < 1e-9, f"{curve['2026-07-05']}")
    ck("không có unknown", unknown == [] and len(used) == 2)
    ck("2 ex-date khác code, không dòng trùng code -> corr_ex rỗng", corr0 == set(), f"{corr0}")

    # Dedupe: hai dòng y hệt nhau = MỘT số hạng; hai tranche KHÁC số = CỘNG
    curve2, _u, _n, _unk, _c = det.build_factor_curve(s, [
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2),
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2)])
    ck("dòng trùng y hệt -> dedupe thành 1 (1.2, không phải 1.4)",
       abs(curve2["2026-07-01"] - 1.2) < 1e-9, f"{curve2['2026-07-01']}")
    curve3, _u, _n, _unk, _c = det.build_factor_curve(s, [
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2),
        ev("2026-08-05", "ISS", "Trả Cổ tức bằng Cổ phiếu", 0.1)])
    ck("hai tranche KHÁC nhau -> CỘNG (1.3)",
       abs(curve3["2026-07-01"] - 1.3) < 1e-9, f"{curve3['2026-07-01']}")

    # Taxonomy: ESOP không làm rơi giá (tái dùng corp_action_lib, không tự định nghĩa)
    curve4, used4, _n, _unk, _c = det.build_factor_curve(s, [
        ev("2026-08-05", "ISS", "Phát hành cho CBCNV", 0.05)])
    ck("ESOP KHÔNG điều chỉnh giá -> r_pred = 1.0 ở mọi phiên",
       all(abs(v - 1.0) < 1e-12 for v in curve4.values()) and used4 == [])


# -------------------------------------------------------------- 5. persistence

def t_persistence():
    print("\n[5] longest_bad_run — ngưỡng persistence (bộ lọc ffill 2026-01-30)")
    tol = 0.003
    ck("lệch 1 phiên lẻ -> run=1 (< min_run 3)",
       det.longest_bad_run([("a", 0), ("b", 0.05), ("c", 0)], tol)[0] == 1)
    ck("lệch 2 phiên -> run=2 (< min_run 3)",
       det.longest_bad_run([("a", 0), ("b", .05), ("c", .05), ("d", 0)], tol)[0] == 2)
    ck("lệch đúng 3 phiên liên tiếp -> run=3",
       det.longest_bad_run([("a", 0), ("b", .05), ("c", .05), ("d", .05)], tol)[0] == 3)
    ck("hai cụm 2 phiên rời nhau KHÔNG gộp thành 4",
       det.longest_bad_run([("a", .05), ("b", .05), ("c", 0), ("d", .05), ("e", .05)], tol)[0] == 2)
    ck("lệch 0.29% (dưới sàn 0.3%, ca DXG) -> run=0",
       det.longest_bad_run([(str(i), 0.0029) for i in range(50)], tol)[0] == 0)
    ck("lệch ÂM cũng tính (|dev|)",
       det.longest_bad_run([("a", -.05), ("b", -.05), ("c", -.05)], tol)[0] == 3)
    run, bad = det.longest_bad_run([("a", 0), ("b", .01), ("c", .09), ("d", .01)], tol)
    ck("trả về đúng cụm dài nhất", run == 3 and [d for d, _x in bad] == ["b", "c", "d"])


# ------------------------------------------------------------- 6. scan_ticker

def t_scan():
    print("\n[6] scan_ticker — verdict, chiều lệch, và fail-closed từng phần")
    evs = [ev("2026-08-20", "ISS", "Cổ phiếu thưởng", 0.1)]

    # Chữ ký FPT: vendor chưa áp hệ số -> r_obs = 1.0 trong khi r_pred = 1.1
    v, p = det.scan_ticker(flat_series(D, 100, 1.0), evs, 0.003, 3, D[0])
    ck("chữ ký FPT -> DRIFT", v == "DRIFT", f"v={v}")
    ck("dev = -9.0909% (= 1 - 1/1.1)", abs(p["dev"] + 0.0909090909) < 1e-6, f"{p.get('dev')}")
    ck("dir = vendor_missing (r_obs < r_pred)", p["dir"] == "vendor_missing")
    ck("run = số phiên trước ex-date", p["run"] == len([d for d in D if d < "2026-08-20"]),
       f"run={p['run']}")
    ck("KHÔNG partial (không có ex-date uncomputable)", p["partial"] is False)

    # Vendor ĐÃ áp đúng hệ số -> khớp
    v, p = det.scan_ticker([bar(d, 100, 100 / (1.1 if d < "2026-08-20" else 1.0)) for d in D],
                           evs, 0.003, 3, D[0])
    ck("vendor áp đúng -> AGREE", v == "AGREE", f"v={v} p={p}")

    # Chiều NGƯỢC: vendor có hệ số mà ta không suy ra được -> nghi bảng TA thiếu
    v, p = det.scan_ticker(flat_series(D, 100, 1.25), evs, 0.003, 3, D[0])
    ck("r_obs > r_pred -> dir = our_table_missing",
       v == "DRIFT" and p["dir"] == "our_table_missing", f"v={v} dir={p.get('dir')}")

    # Một ex-date UNCOMPUTABLE nhiễm MỌI phiên trước nó -> KHÔNG được báo DRIFT
    rights = [ev("2026-08-20", "ISS", det.RIGHTS_METHOD, 0.5)]
    v, p = det.scan_ticker(flat_series(D, 100, 1.0), rights, 0.003, 3, D[0])
    ck("quyền mua ở cuối cửa sổ -> UNCOMPUTABLE, KHÔNG phải DRIFT", v == "UNCOMPUTABLE", f"v={v}")
    ck("UNCOMPUTABLE nêu đúng mã lý do",
       p["unknown"][0][1] == "rights_issue_no_subscription_price", f"{p['unknown']}")

    # Ca XHC: ex-date uncomputable ở GIỮA, lệch thật NẰM SAU nó -> vẫn phải bắt được,
    # nhưng chỉ đánh giá từ ex-date uncomputable trở đi (phần trước đã bị nhiễm).
    mixed = [ev("2026-06-15", "ISS", det.RIGHTS_METHOD, 0.5),
             ev("2026-08-20", "ISS", "Cổ phiếu thưởng", 0.1)]
    v, p = det.scan_ticker(flat_series(D, 100, 1.0), mixed, 0.003, 3, D[0])
    ck("ca XHC: uncomputable ở giữa + lệch sau -> DRIFT", v == "DRIFT", f"v={v}")
    ck("ca XHC: đánh dấu partial", p["partial"] is True)
    ck("ca XHC: cửa sổ chấm điểm bắt đầu TỪ ex-date uncomputable, không sớm hơn",
       p["d0"] >= "2026-06-15", f"d0={p.get('d0')}")

    # eval_from = rìa cửa sổ đánh giá: phiên trước đó chỉ để tìm phiên cum, không chấm điểm
    v, p = det.scan_ticker(flat_series(D, 100, 1.0), evs, 0.003, 3, "2026-07-05")
    ck("eval_from cắt đúng: không chấm phiên trước rìa", p["d0"] >= "2026-07-05", f"{p.get('d0')}")

    v, p = det.scan_ticker([], evs, 0.003, 3, D[0])
    ck("chuỗi rỗng -> NODATA", v == "NODATA", f"v={v}")

    # `ex` phải là ex-date mà hệ số của nó đang THIẾU (ex-date sớm nhất SAU cụm lệch), KHÔNG phải
    # ex-date sớm nhất trong cửa sổ. Bản trước dùng min(used) ⇒ nêu sai tên sự kiện VÀ làm khoá
    # de-dup của alert.sh chặn oan một lỗi MỚI tới 7 ngày (arch-review 2026-09-27).
    two = [ev("2026-06-05", "ISS", "Cổ phiếu thưởng", 0.1),
           ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2)]
    #      vendor áp ĐÚNG hệ số của 06-05 nhưng THIẾU hệ số của 08-05 ⇒ chỉ phần sau 06-05 lệch
    ser = [bar(d, 100, 100 / (1.1 if d < "2026-06-05" else 1.0)) for d in D]
    v, p = det.scan_ticker(ser, two, 0.003, 3, D[0])
    ck("ex = ex-date BỊ HỎNG (08-05), không phải ex-date sớm nhất (06-05)",
       v == "DRIFT" and p["ex"] == "2026-08-05", f"v={v} ex={p.get('ex')}")
    ck("cụm lệch kết thúc TRƯỚC ex-date bị hỏng", p["d1"] < "2026-08-05", f"d1={p.get('d1')}")

    # M24 (arch-review vòng 3): bản vá F3 CHƯA có assertion nào — mutation revert về
    # `min(used, default="")` vẫn 301/301. Ca cắn là `our_table_missing`: ex-date còn THIẾU theo định
    # nghĩa KHÔNG nằm trong `used`, nên `ex > d1` luôn rỗng và fallback quyết định khoá de-dup.
    only_a = [ev("2026-06-05", "ISS", "Cổ phiếu thưởng", 0.1)]   # bảng TA chỉ biết ex 06-05
    #        vendor áp CẢ 06-05 lẫn một ex-date ta KHÔNG có -> r_obs > r_pred trên toàn cửa sổ
    ser2 = [bar(d, 100, 100 / 1.2) for d in D]
    v, p = det.scan_ticker(ser2, only_a, 0.003, 3, D[0])
    ck("our_table_missing: KHÔNG vay tên ex-date vendor làm ĐÚNG (M24)",
       v == "DRIFT" and p["ex"] != "2026-06-05", f"v={v} ex={p.get('ex')}")
    ck("our_table_missing: khoá nói thẳng 'không xác định được ex-date nào thiếu'",
       p["ex"].startswith("unknown_gap@"), f"ex={p.get('ex')}")
    # R3-2: khoá phải BẤT BIẾN theo cửa sổ. Cùng một lệch, hai `asof` liên tiếp (chuỗi dài thêm 1
    # phiên ⇒ `d1` trôi) phải cho CÙNG khoá — neo vào `d1` thì báo lại mỗi ngày.
    ser2b = ser2 + [bar("2026-08-11", 100, 100 / 1.2)]
    v2, p2 = det.scan_ticker(ser2b, only_a, 0.003, 3, D[0])
    ck("R3-2: `d1` trôi sang phiên mới nhưng khoá de-dup KHÔNG đổi",
       p2["ex"] == p["ex"] and p2["d1"] != p["d1"],
       f"ex {p['ex']}->{p2['ex']} | d1 {p['d1']}->{p2['d1']}")
    # R3-3: khoá của `too_few_sessions_to_compare` cũng không được trôi theo rìa cửa sổ nạp
    v3, q3 = det.scan_ticker([bar("2026-08-09", 100, 100)], [], 0.003, 3, "2026-08-08")
    v4, q4 = det.scan_ticker([bar("2026-08-08", 100, 100), bar("2026-08-09", 100, 100)], [],
                             0.003, 3, "2026-08-08")
    ck("R3-3: khoá too_few KHÔNG trôi theo rìa trái cửa sổ nạp",
       v3 == v4 == "UNCOMPUTABLE" and q3["unknown"][0][0] == q4["unknown"][0][0] == "no_ex_in_window",
       f"{q3['unknown'][0][0]!r} vs {q4['unknown'][0][0]!r}")


# -------------------------------------------- 7. hợp đồng dòng máy đọc + CLI

def t_contract():
    print("\n[7] guard tham số CLI + hợp đồng dòng máy đọc (round-trip THẬT, không grep nguồn)")
    py = open(os.path.join(HERE, "adjfactor_drift_detect.py")).read()

    ck("--min-run dưới 3 bị TỪ CHỐI (không cho hạ ngưỡng persistence)", _exits_2(["--min-run", "2"]))
    ck("--dev-tol <= 0 bị TỪ CHỐI", _exits_2(["--dev-tol", "0"]))
    ck("--dev-tol >= 0.5 bị TỪ CHỐI (dung sai vô nghĩa = tắt cảnh báo mà trông như đang chạy)",
       _exits_2(["--dev-tol", "0.9"]))

    # Hard-constraint #1/#2: KHÔNG được import để SỬA hai file của cổng §21. `git diff --name-status`
    # là bằng chứng đúng (không phải grep chuỗi) — assertion cũ dùng `A or (B not in py)` nên PASS
    # với bất kỳ import có alias, tức là không chứng minh gì (arch-review 2026-09-27).
    # Câu hỏi đúng là "NHÁNH NÀY có chạm hai file đó không", không phải "commit gần nhất trong
    # LỊCH SỬ chạm chúng lúc nào" — `git log -1 -- <paths>` trả về commit cũ bất kỳ và luôn FAIL.
    root = os.path.dirname(HERE)
    paths = ["bin/report_return_gate.py", "bin/dividend_adjusted_return.py"]
    base = subprocess.run(["git", "-C", root, "merge-base", "HEAD", "master"],
                          capture_output=True, text=True).stdout.strip()
    ck("xác định được merge-base với master", bool(base), "git merge-base rong")
    committed = subprocess.run(["git", "-C", root, "diff", "--name-only", base, "HEAD", "--",
                                *paths], capture_output=True, text=True).stdout.strip()
    working = subprocess.run(["git", "-C", root, "status", "--porcelain", "--", *paths],
                             capture_output=True, text=True).stdout.strip()
    ck("nhánh này KHÔNG chạm report_return_gate.py / dividend_adjusted_return.py (commit + worktree)",
       committed == "" and working == "", f"committed={committed!r} working={working!r}")
    ck("detector chỉ ĐỌC dividend_adjusted_return (ACCOUNTS/broker_qty), không gọi hàm ghi/tính §21",
       "dar.broker_qty" in py and "dar.detect_adjustments" not in py
       and "dar.dividend_adjusted" not in py)

    # ROUND-TRIP: dựng dòng bằng ĐÚNG hàm producer, chạy qua alert.sh thật, rồi so TỪNG TRƯỜNG
    # trên câu Discord. Mutation M1 (hoán `dir` với `held`) trước đây PASS 142/142 và sinh nhãn SAI
    # "ĐANG NẮM LIVE: vendor_missing" — round-trip này giết nó.
    payload = {"ex": "2026-09-24", "r_obs": 1.0, "r_pred": 1.26041, "dev": -0.206608,
               "run": 78, "d0": "2026-05-28", "d1": "2026-09-17", "dir": "vendor_missing",
               "corr": "0"}
    line = det.marker_drift("VPB", payload, "SpaceX,ZaloPay")
    f = line.split("|")
    ck("marker_drift: 12 trường", len(f) == 12, f"{len(f)}: {f}")
    ck("marker_drift: thứ tự trường đúng vị trí (tag,tk,ex,r_obs,r_pred,dev,run,d0,d1,dir,held,corr)",
       f[0] == "ADJFACTOR_DRIFT" and f[1] == "VPB" and f[2] == "2026-09-24"
       and f[3] == "1.000000" and f[4] == "1.260410" and f[5] == "-0.206608" and f[6] == "78"
       and f[7] == "2026-05-28" and f[8] == "2026-09-17" and f[9] == "vendor_missing"
       and f[10] == "SpaceX,ZaloPay" and f[11] == "0", f"{f}")

    u = det.marker_uncomputable("MBB", "2026-08-11", "rights_issue_no_subscription_price", "SpaceX")
    ck("marker_uncomputable: 5 trường đúng vị trí",
       u.split("|") == ["ADJFACTOR_UNCOMPUTABLE", "MBB", "2026-08-11",
                        "rights_issue_no_subscription_price", "SpaceX"], f"{u}")
    n = det.marker_nodata("CMP", "none")
    ck("marker_nodata: 3 trường đúng vị trí",
       n.split("|") == ["ADJFACTOR_NODATA", "CMP", "none"], f"{n}")
    fd = det.marker_feed("STALE", {"max_ingested_ict": "2026-09-20T22:00:00+07:00",
                                   "max_public": "2026-09-19", "rows": "36428", "age_days": 5,
                                   "reason": "chua co lan nap nao"})
    ck("marker_feed: 7 trường đúng vị trí",
       fd.split("|") == ["ADJFACTOR_FEED", "STALE", "2026-09-20T22:00:00+07:00", "2026-09-19",
                         "36428", "5", "chua co lan nap nao"], f"{fd}")
    sc = det.marker_scan("2026-09-25", 54, 16, 13, 23, 2)
    ck("marker_scan: 7 trường đúng vị trí",
       sc.split("|") == ["ADJFACTOR_SCAN", "2026-09-25", "54", "16", "13", "23", "2"], f"{sc}")

    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        body = "\n".join([line, u, n, det.marker_feed("FRESH", {}), sc]) + "\n"
        r = _run_alert(tmp, tgt, body)
        # rc PHẢI được chốt, không bỏ trống: body có 1 dòng DRIFT ⇒ hợp đồng là rc=10. Bỏ `r` đi
        # (ruff F841) thì round-trip chỉ còn kiểm NỘI DUNG câu Discord, không kiểm việc lượt quét
        # có báo đúng hạng thoát hay không.
        ck("round-trip: body có DRIFT -> alert trả rc=10", r.returncode == 10,
           f"rc={r.returncode} {r.stderr[-200:]!r}")
        msg = open(os.path.join(tmp, "sink", "notify.txt")).read()
        ck("round-trip: `held` của dòng producer thành nhãn ĐANG NẮM LIVE (không phải `dir`)",
           "ĐANG NẮM LIVE: SpaceX,ZaloPay" in msg and "ĐANG NẮM LIVE: vendor_missing" not in msg,
           f"{[l for l in msg.splitlines() if 'VPB' in l]}")
        ck("round-trip: `dir` của dòng producer thành câu nguyên nhân vendor (không phải held)",
           "THIẾU hệ số" in msg and "dir=SpaceX" not in msg)
        ck("round-trip: `dev` in ra đúng -20.66%", "-20.66%" in msg)
        ck("round-trip: `run` in ra đúng 78 phiên", "78 phiên" in msg)
        ck("round-trip: `d0..d1` in ra đúng cửa sổ", "2026-05-28..2026-09-17" in msg)
        ck("round-trip: `ex` in ra đúng ex-date bị hỏng", "(ex 2026-09-24)" in msg)
        ck("round-trip: NODATA mã không nắm -> chỉ đếm, không nêu tên", "CMP" not in msg)
        ck("round-trip: mã UNCOMPUTABLE đang nắm -> nêu tên + mã lý do",
           "MBB" in msg and "rights_issue_no_subscription_price" in msg)


def _exits_2(argv):
    """rc==2 (argparse từ chối)? Chạy detector như tiến trình con, nhưng KHÔNG cho chạm BigQuery.

    Các assertion "giá trị ĐÚNG vẫn được nhận" đi QUA cổng argparse rồi vào `run_scan` thật ⇒ trước
    bản này nó phát một truy vấn `feed_freshness()` + `price_rows` + `events` THẬT và đọc cả
    `data/execution_logs/` (arch-review vòng 3, R3-5: 9,6s, `# vi the LIVE: 30 ma`). Chỉ-đọc nên
    KHÔNG vi phạm §5b hay ranh giới detect-only, nhưng LAYER1.md §1 hứa "không cần BigQuery" và một
    selfcheck phụ thuộc mạng thì hỏng ở nơi khác vì lý do không liên quan. `MIKE_ADJFACTOR_NO_BQ=1`
    làm mọi lối ra BQ raise ngay ⇒ rc=1 (hạ tầng), vẫn phân biệt được với rc=2 (sai đối số).
    """
    env = dict(os.environ, MIKE_ADJFACTOR_NO_BQ="1")
    r = subprocess.run([sys.executable, os.path.join(HERE, "adjfactor_drift_detect.py")] + argv,
                       capture_output=True, text=True, env=env)
    return r.returncode == 2


# --------------------------------------------------------------- 8. alert.sh

ALERT_STUB_NOTIFY = """#!/usr/bin/env bash
printf '%s\\n' "$1" > "$MIKE_SELFCHECK_SINK/notify.txt"
echo "$2" > "$MIKE_SELFCHECK_SINK/topic.txt"
exit ${MIKE_SELFCHECK_NOTIFY_RC:-0}
"""
ALERT_STUB_BUS = """#!/usr/bin/env bash
printf '%s\\n' "$4" >> "$MIKE_SELFCHECK_SINK/bus.jsonl"
exit ${MIKE_SELFCHECK_BUS_RC:-0}
"""

DRIFT_HELD = ("ADJFACTOR_DRIFT|VPB|2026-09-24|1.000000|1.260410|-0.206608|78|2026-05-28"
              "|2026-09-17|vendor_missing|SpaceX,ZaloPay|0")
DRIFT_FREE = ("ADJFACTOR_DRIFT|FPT|2026-09-21|1.000000|1.100000|-0.090909|75|2026-05-28"
              "|2026-09-14|vendor_missing|none|0")
UNCOMP_HELD = "ADJFACTOR_UNCOMPUTABLE|MBB|2026-08-11|rights_issue_no_subscription_price|SpaceX"
UNCOMP_FREE = "ADJFACTOR_UNCOMPUTABLE|RYG|2026-09-03|rights_issue_no_subscription_price|none"
NODATA_HELD = "ADJFACTOR_NODATA|ZZZ|SpaceX"
NODATA_FREE = "ADJFACTOR_NODATA|CMP|none"
FEED_FRESH = "ADJFACTOR_FEED|FRESH|2026-09-26T22:43:40+07:00|2026-09-25|36428|-1|"
FEED_STALE = ("ADJFACTOR_FEED|STALE|2026-09-18T22:00:00+07:00|2026-09-17|36000|6"
              "|chua co lan nap nao ke tu phien 2026-09-25")
SCAN = "ADJFACTOR_SCAN|2026-09-25|54|2|2|23|2"


def _sandbox(tmp):
    """ROOT giả với stub notify/append_event — selfcheck KHÔNG chạm Discord/bus thật."""
    os.makedirs(os.path.join(tmp, "bin"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "sink"), exist_ok=True)
    for name, body in (("notify_thread.sh", ALERT_STUB_NOTIFY), ("append_event.sh", ALERT_STUB_BUS)):
        p = os.path.join(tmp, "bin", name)
        open(p, "w").write(body)
        os.chmod(p, 0o755)
    tgt = os.path.join(tmp, "bin", "adjfactor_drift_alert.sh")
    open(tgt, "w").write(open(os.path.join(HERE, "adjfactor_drift_alert.sh")).read())
    os.chmod(tgt, 0o755)
    return tgt


def _run_alert(tmp, tgt, stdin_text, env_extra=None, args=("1234",)):
    env = dict(os.environ)
    env["MIKE_SELFCHECK_SINK"] = os.path.join(tmp, "sink")
    env.update(env_extra or {})
    return subprocess.run(["bash", tgt, *args], input=stdin_text, capture_output=True,
                          text=True, env=env)


def t_alert(tz_label, env_tz):
    print(f"\n[8] adjfactor_drift_alert.sh  (TZ: {tz_label})")
    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        state = os.path.join(tmp, "state", "adjfactor_drift_alerted.json")

        # Lối im lặng THẬT đòi CẢ BA: 0 marker, feed FRESH, và có mã được quét. Bản trước chỉ đưa
        # văn bản rác (không có dòng FEED) và vẫn kỳ vọng rc=0 — tức chốt đúng bug F5 (thiếu FEED bị
        # đọc thành "feed ổn"). Giờ ca đó là một assertion RIÊNG bên dưới và phải GỬI.
        r = _run_alert(tmp, tgt, "khong co marker nao\n" + FEED_FRESH + "\n" + SCAN + "\n", env_tz)
        ck(f"[{tz_label}] 0 marker + feed FRESH + có mã quét -> rc=0, không gửi gì",
           r.returncode == 0 and not os.path.exists(os.path.join(sink, "notify.txt")),
           f"rc={r.returncode} {r.stderr[-200:]!r}")

        body = "\n".join([DRIFT_HELD, DRIFT_FREE, UNCOMP_HELD, UNCOMP_FREE,
                           FEED_FRESH, SCAN]) + "\n"
        r = _run_alert(tmp, tgt, body, env_tz)
        ck(f"[{tz_label}] có lệch -> rc=10", r.returncode == 10, f"rc={r.returncode} {r.stderr}")
        msg = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] Discord nêu mã ĐANG NẮM riêng và có nhãn LIVE",
           "VPB" in msg and "ĐANG NẮM LIVE: SpaceX,ZaloPay" in msg)
        ck(f"[{tz_label}] Discord nói rõ Layer 1 KHÔNG công bố/sửa số",
           "KHÔNG công bố" in msg and "report_return_gate" in msg)
        ck(f"[{tz_label}] UNCOMPUTABLE của mã NẮM được nêu tên + 'không kết luận là khớp'",
           "MBB" in msg and "không kết luận là khớp" in msg)
        ck(f"[{tz_label}] UNCOMPUTABLE của mã KHÔNG nắm chỉ đếm, không nêu tên", "RYG" not in msg)
        ck(f"[{tz_label}] có dòng việc-cần-làm quy đúng người (Winston cho vendor_missing)",
           "Winston" in msg)

        bus = [json.loads(l) for l in open(os.path.join(sink, "bus.jsonl")) if l.strip()]
        ck(f"[{tz_label}] bus ghi 1 event, published_any_number=False",
           len(bus) == 1 and bus[0]["published_any_number"] is False, f"{bus}")
        ck(f"[{tz_label}] bus giữ TOÀN BỘ marker (kể cả mã không nắm) — dấu vết audit đầy đủ",
           len(bus[0]["drift_markers"]) == 2 and len(bus[0]["uncomputable_markers"]) == 2)
        # 3 khoá, KHÔNG phải 2: hai khoá DRIFT dạng `<mã>|<ex>` + MỘT khoá UNCOMPUTABLE dạng
        # `<mã>|<ex>|<reason_code>` (chỉ mã đang NẮM — `RYG` held=none không sinh khoá). Bản trước
        # của assertion này chốt 2 khoá, tức chốt đúng cái BUG arch-review 2026-09-27 tìm ra: nhánh
        # uncomputable KHÔNG de-dup nên bắn Discord cả 3 lượt liên tiếp trên cùng input. `code` phải
        # nằm TRONG khoá vì đổi mã lý do là đổi việc phải làm.
        ck(f"[{tz_label}] state de-dup ghi đúng 3 khoá (2 DRIFT `mã|ex` + 1 UNCOMP `mã|ex|code`)",
           os.path.exists(state) and sorted(json.load(open(state))) ==
           ["FPT|2026-09-21", "MBB|2026-08-11|rights_issue_no_subscription_price",
            "VPB|2026-09-24"], f"{state}")

        today_ict = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                                   capture_output=True, text=True).stdout.strip()
        # §16/§19 — ASSERTION NÀY PHẢI KHÔNG VÔ NGHĨA. Ở 11:45 ICT thì ICT/UTC/New_York cùng MỘT
        # ngày lịch, nên bỏ hẳn neo `TZ='Asia/Ho_Chi_Minh'` khỏi alert.sh vẫn PASS (mutation M7,
        # arch-review 2026-09-27) — và nó chỉ cắn trong khoảng 00:00-10:59 ICT, tức ĐÚNG giờ cron
        # đề xuất (00:10). Dùng TZ có lệch cực đại (+14 / −11) thì với MỌI thời điểm, ít nhất một
        # trong hai khác ngày với ICT; và nếu TZ của lượt này không khác ngày thì nói THẲNG là vô
        # nghĩa thay vì đếm nó như một assertion đã PASS.
        host_today = subprocess.run(["bash", "-c", "date +%F"], capture_output=True, text=True,
                                    env={**os.environ, **(env_tz or {})}).stdout.strip()
        if host_today == today_ict:
            print(f"  --   [{tz_label}] assertion neo-TZ VÔ NGHĨA ở thời điểm này "
                  f"(ngày host == ngày ICT == {today_ict}) — không tính là PASS")
            VACUOUS.append(tz_label)
        else:
            ck(f"[{tz_label}] ngày trong state là ngày ICT ({today_ict}), KHÔNG phải ngày host "
               f"({host_today})",
               set(json.load(open(state)).values()) == {today_ict},
               f"{json.load(open(state))} vs ICT {today_ict}")
            NON_VACUOUS.append(tz_label)

        # Lượt 2 cùng ngày: de-dup CHẶN Discord nhưng VẪN ghi bus (dấu vết không được mất)
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_HELD, DRIFT_FREE, FEED_FRESH, SCAN]) + "\n",
                       env_tz)
        ck(f"[{tz_label}] lượt 2: de-dup -> KHÔNG gửi Discord, rc=10",
           r.returncode == 10 and not os.path.exists(os.path.join(sink, "notify.txt")),
           f"rc={r.returncode}")
        bus2 = [l for l in open(os.path.join(sink, "bus.jsonl")) if l.strip()]
        ck(f"[{tz_label}] lượt 2: bus VẪN ghi (de-dup chỉ áp cho Discord)", len(bus2) == 2)

        # UNCOMPUTABLE của mã NẮM cũng PHẢI de-dup. Bản đầu không de-dup nhánh này và
        # `N_UNCOMP_HELD > 0` luôn phá de-dup ⇒ arch-review 2026-09-27 đo: gửi Discord CẢ BA lượt
        # liên tiếp trên cùng input, với 5 mã đang nắm đã ở trạng thái này ⇒ spam hằng ngày.
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_HELD, UNCOMP_HELD, FEED_FRESH, SCAN]) + "\n",
                       env_tz)
        ck(f"[{tz_label}] lượt 3 y hệt: uncomputable của mã nắm CŨNG bị de-dup, KHÔNG gửi",
           not os.path.exists(os.path.join(sink, "notify.txt")) and r.returncode == 10,
           f"rc={r.returncode}")
        st = json.load(open(state))
        ck(f"[{tz_label}] khoá uncomputable gồm cả reason_code",
           "MBB|2026-08-11|rights_issue_no_subscription_price" in st, f"{sorted(st)}")

        # Mã lý do ĐỔI = việc phải làm đổi ⇒ khoá khác ⇒ phải gửi lại
        r = _run_alert(tmp, tgt, "\n".join([
            UNCOMP_HELD.replace("rights_issue_no_subscription_price", "price_ffill_suspect"),
            FEED_FRESH, SCAN]) + "\n", env_tz)
        ck(f"[{tz_label}] cùng (mã,ex) nhưng reason_code KHÁC -> vẫn gửi",
           os.path.exists(os.path.join(sink, "notify.txt")))

        # NODATA của mã có thể đang nắm: nêu tên; của mã không nắm: chỉ đếm
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([NODATA_HELD, NODATA_FREE, FEED_FRESH, SCAN]) + "\n",
                       env_tz)
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] NODATA mã đang nắm được nêu tên", "ZZZ" in m and "CMP" not in m)
        ck(f"[{tz_label}] khoá NODATA được ghi state (`<mã>|nodata`)",
           "ZZZ|nodata" in json.load(open(state)), f"{sorted(json.load(open(state)))}")
        # M4 (arch-review vòng 2): nhánh NODATA de-dup không có assertion nào — mutation xoá nó vẫn
        # 233/233. Chốt idempotence bằng lượt LẶP LẠI y hệt trên input CHỈ có NODATA.
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([NODATA_HELD, NODATA_FREE, FEED_FRESH, SCAN]) + "\n",
                       env_tz)
        ck(f"[{tz_label}] lượt 2 chỉ-NODATA y hệt -> de-dup, KHÔNG gửi lại (M4)",
           not os.path.exists(os.path.join(sink, "notify.txt")), f"rc={r.returncode}")

        # F5: THIẾU dòng FEED = fail-closed, KHÔNG được coi là "feed ổn" rồi im lặng.
        r = _run_alert(tmp, tgt, "khong co gi\n" + SCAN + "\n", env_tz)
        ck(f"[{tz_label}] 0 marker + THIẾU dòng FEED -> VẪN gửi Discord (F5, không im lặng)",
           os.path.exists(os.path.join(sink, "notify.txt")) and r.returncode == 10,
           f"rc={r.returncode} {r.stderr[-200:]!r}")
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] thiếu FEED: nói rõ là ĐIỂM MÙ, không phải 'feed ổn'",
           "MISSING" in m and "ĐIỂM MÙ" in m, f"{m[:300]!r}")

        # F2/F7: universe RỖNG (N_SCANNED=0) là điểm mù — bản trước ghi bus rồi thoát im lặng.
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join(
            [FEED_FRESH, "ADJFACTOR_SCAN|2026-09-25|0|0|0|0|0"]) + "\n", env_tz)
        ck(f"[{tz_label}] universe RỖNG + feed FRESH -> VẪN gửi Discord (F2)",
           os.path.exists(os.path.join(sink, "notify.txt")), f"rc={r.returncode}")
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] universe rỗng: nói rõ ĐIỂM MÙ + quy việc, không phải 'không có sự kiện'",
           "UNIVERSE RỖNG" in m and "Winston" in m, f"{m[:300]!r}")

        # F4: dòng DRIFT corr=1 KHÔNG được quy cho Winston (chưa đủ căn cứ cáo buộc vendor)
        os.remove(os.path.join(sink, "notify.txt"))
        corr_line = DRIFT_HELD.replace("VPB|2026-09-24", "AAA|2026-09-05")[:-1] + "1"
        r = _run_alert(tmp, tgt, "\n".join([corr_line, FEED_FRESH, SCAN]) + "\n", env_tz)
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] corr=1: câu Discord nói NGHI BẢN ĐÍNH CHÍNH, không khẳng định vendor sai",
           "NGHI BẢN ĐÍNH CHÍNH" in m and "THIẾU hệ số" not in m, f"{m[:500]!r}")
        ck(f"[{tz_label}] corr=1: KHÔNG sinh dòng việc backfill cho Winston (F4)",
           "yêu cầu backfill" not in m, f"{m[:600]!r}")
        ck(f"[{tz_label}] corr=1: vẫn nêu mã + vẫn ghi bus (không im lặng bỏ qua)",
           "AAA" in m and "ĐANG NẮM LIVE" in m)

        # `held=skipped` KHÔNG được in thành "ĐANG NẮM LIVE: skipped" (F7)
        os.remove(os.path.join(sink, "notify.txt"))
        # Mã + ex-date MỚI: `VPB|2026-09-24` đã bị de-dup ở các lượt trên nên sẽ không gửi gì.
        skip_line = DRIFT_HELD.replace("VPB|2026-09-24", "SKP|2026-09-07") \
                              .replace("|SpaceX,ZaloPay|0", "|skipped|0")
        r = _run_alert(tmp, tgt, "\n".join([skip_line, FEED_FRESH, SCAN]) + "\n", env_tz)
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] held=skipped KHÔNG bị in thành 'ĐANG NẮM LIVE: skipped' (F7)",
           "ĐANG NẮM LIVE: skipped" not in m and "CHƯA TRA" in m, f"{m[:400]!r}")

        # R3-7: một trường thứ 13 thêm về sau KHÔNG được làm mất nhánh cờ đính chính. `read` dồn phần
        # còn lại vào biến CUỐI, nên thiếu biến hứng thì `corr` thành "1|extra" ⇒ so `= "1"` thất bại
        # ⇒ dòng quay về "vendor THIẾU hệ số" + TODO Winston, tái lập F4 một cách im lặng.
        os.remove(os.path.join(sink, "notify.txt"))
        wide = (DRIFT_HELD.replace("VPB|2026-09-24", "W13|2026-09-08")[:-1] + "1|truong_moi")
        r = _run_alert(tmp, tgt, "\n".join([wide, FEED_FRESH, SCAN]) + "\n", env_tz)
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] dòng có trường thứ 13 -> cờ corr VẪN đọc đúng (R3-7)",
           "NGHI BẢN ĐÍNH CHÍNH" in m and "yêu cầu backfill" not in m, f"{m[:500]!r}")
        # và dòng 11 trường (bản CŨ, không có corr) vẫn phải đọc được như corr=0
        os.remove(os.path.join(sink, "notify.txt"))
        old11 = DRIFT_HELD.replace("VPB|2026-09-24", "O11|2026-09-06")[:-2]
        ck("fixture 11 trường dựng đúng (không còn trường corr)", len(old11.split("|")) == 11, old11)
        r = _run_alert(tmp, tgt, "\n".join([old11, FEED_FRESH, SCAN]) + "\n", env_tz)
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] dòng 11 trường (không có corr) -> coi như corr=0, vẫn quy việc bình thường",
           "O11" in m and "NGHI BẢN ĐÍNH CHÍNH" not in m, f"{m[:400]!r}")

        # R3-4: KHÔNG MỞ được file lock là lỗi MÔI TRƯỜNG -> chạy TIẾP (fail-open về phía GỬI), và
        # thông điệp phải trích LỖI THẬT chứ không khẳng định "một lượt khác đang chạy" (§29 dạng 2).
        os.remove(os.path.join(sink, "notify.txt"))
        lockdir = os.path.join(tmp, "state")
        # Phải XOÁ .lock cũ trước khi khoá thư mục: mở một file ĐÃ TỒN TẠI để ghi chỉ cần quyền trên
        # FILE (0600, ta sở hữu), không cần quyền trên thư mục — để nguyên thì ca này không tái hiện
        # được và assertion trở thành vô nghĩa.
        for f in os.listdir(lockdir):
            if f.endswith(".lock"):
                os.remove(os.path.join(lockdir, f))
        mode = os.stat(lockdir).st_mode
        os.chmod(lockdir, 0o500)                      # read-only: mở file .lock sẽ thất bại
        try:
            r = _run_alert(tmp, tgt, "\n".join([
                DRIFT_HELD.replace("VPB|2026-09-24", "LCK|2026-09-04"), FEED_FRESH, SCAN]) + "\n",
                env_tz)
            sent = os.path.exists(os.path.join(sink, "notify.txt"))
            ck(f"[{tz_label}] state/ read-only -> VẪN gửi Discord (fail-open về phía GỬI) (R3-4)",
               sent, f"rc={r.returncode} {r.stderr[-300:]!r}")
            ck(f"[{tz_label}] lock không mở được: trích LỖI THẬT, KHÔNG nói 'lượt khác đang chạy'",
               "KHONG MO duoc file lock" in r.stderr
               and "Permission denied" in r.stderr
               and "dang giu" not in r.stderr, f"{r.stderr[-600:]!r}")
        finally:
            os.chmod(lockdir, mode)

        # Vòng 4 mục 1: `flock` KHÔNG CHẠY ĐƯỢC (rc 126/127) là lỗi MÔI TRƯỜNG, không phải tranh
        # chấp ⇒ phải chạy TIẾP không lock, KHÔNG được tắt Discord và KHÔNG được nói "lượt khác đang
        # giữ". Giả lập bằng một `flock` giả luôn rc=127 đặt đầu PATH.
        os.remove(os.path.join(sink, "notify.txt"))
        fakebin = os.path.join(tmp, "fakebin")
        os.makedirs(fakebin, exist_ok=True)
        fl = os.path.join(fakebin, "flock")
        open(fl, "w").write("#!/usr/bin/env bash\necho 'flock: command not found' >&2\nexit 127\n")
        os.chmod(fl, 0o755)
        env_nf = dict(env_tz, PATH=fakebin + os.pathsep + os.environ.get("PATH", ""))
        r = _run_alert(tmp, tgt, "\n".join([
            DRIFT_HELD.replace("VPB|2026-09-24", "NFL|2026-09-03"), FEED_FRESH, SCAN]) + "\n",
            env_nf)
        ck(f"[{tz_label}] flock không chạy được -> VẪN gửi Discord (môi trường, không tranh chấp)",
           os.path.exists(os.path.join(sink, "notify.txt")), f"rc={r.returncode} {r.stderr[-300:]!r}")
        ck(f"[{tz_label}] flock không chạy được: KHÔNG nói 'lượt khác đang giữ', trích LỖI THẬT",
           "dang giu" not in r.stderr and "KHONG CHAY DUOC" in r.stderr
           and "command not found" in r.stderr, f"{r.stderr[-400:]!r}")

        # M47: lock THẬT SỰ bị giữ -> ghi BUS rồi mới bỏ Discord. Thứ tự này là cả điểm của R3-4;
        # không có assertion thì một refactor sau có thể lặng lẽ khôi phục ca mất CẢ HAI kênh.
        os.remove(os.path.join(sink, "notify.txt"))
        bus_before = len([l for l in open(os.path.join(sink, "bus.jsonl")) if l.strip()])
        holder = subprocess.Popen(
            ["bash", "-c", f'exec 9>"{state}.lock"; flock 9; sleep 8'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            import time
            time.sleep(0.5)
            r = _run_alert(tmp, tgt, "\n".join([
                DRIFT_HELD.replace("VPB|2026-09-24", "HLD|2026-09-02"), FEED_FRESH, SCAN]) + "\n",
                dict(env_tz, ADJFACTOR_LOCK_WAIT="1"))
            bus_after = len([l for l in open(os.path.join(sink, "bus.jsonl")) if l.strip()])
            ck(f"[{tz_label}] lock bị giữ -> BUS VẪN ghi (dấu vết audit không mất) (M47)",
               bus_after == bus_before + 1, f"{bus_before} -> {bus_after}")
            ck(f"[{tz_label}] lock bị giữ -> KHÔNG gửi Discord (không trùng), rc=11",
               not os.path.exists(os.path.join(sink, "notify.txt")) and r.returncode == 11,
               f"rc={r.returncode} {r.stderr[-300:]!r}")
        finally:
            holder.kill()
            holder.wait()

        # M45: ghi state thất bại -> KHÔNG bung traceback trần, nói rõ hệ quả + lỗi thật (§29).
        # (Lượt M47 ở trên ĐÚNG là không gửi, nên notify.txt có thể không tồn tại.)
        if os.path.exists(os.path.join(sink, "notify.txt")):
            os.remove(os.path.join(sink, "notify.txt"))
        for f in os.listdir(lockdir):
            if f.endswith(".lock"):
                os.remove(os.path.join(lockdir, f))
        os.chmod(lockdir, 0o500)
        try:
            r = _run_alert(tmp, tgt, "\n".join([
                DRIFT_HELD.replace("VPB|2026-09-24", "STW|2026-09-01"), FEED_FRESH, SCAN]) + "\n",
                env_tz)
            ck(f"[{tz_label}] ghi state hỏng -> KHÔNG bung traceback trần (M45)",
               "Traceback (most recent call last)" not in r.stderr, f"{r.stderr[-400:]!r}")
            ck(f"[{tz_label}] ghi state hỏng -> nói rõ 'lượt sau GỬI LẠI' + lỗi thật",
               "GUI LAI" in r.stderr and "Permission denied" in r.stderr, f"{r.stderr[-400:]!r}")
        finally:
            os.chmod(lockdir, mode)

        # Feed KHÔNG tươi: luôn lên Discord, đứng đầu, kèm lý do THẬT của detector, và nói rõ
        # "khớp" bên dưới không đáng tin. Đây là ca im-lặng-bằng-sạch mà arch-review chỉ ra.
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([FEED_STALE, SCAN]) + "\n", env_tz)
        ck(f"[{tz_label}] feed STALE mà KHÔNG có lệch nào -> VẪN gửi Discord (rc=10)",
           os.path.exists(os.path.join(sink, "notify.txt")) and r.returncode == 10,
           f"rc={r.returncode} {r.stderr[-200:]!r}")
        m = open(os.path.join(sink, "notify.txt")).read()
        ck(f"[{tz_label}] feed STALE: trích LÝ DO THẬT detector in ra, không phải câu đoán",
           "chua co lan nap nao ke tu phien 2026-09-25" in m, f"{m[:400]!r}")
        # So KHÔNG phân biệt hoa/thường: câu thật viết "KHÔNG đáng tin" (in hoa để nhấn). Chốt cứng
        # một cách viết hoa là chốt vào cách TRÌNH BÀY, không phải vào nội dung cần đảm bảo.
        ck(f"[{tz_label}] feed STALE: nói rõ mọi kết luận 'khớp' không đáng tin",
           "không đáng tin" in m.lower(), f"{m[:400]!r}")
        ck(f"[{tz_label}] feed STALE: quy việc cho Winston + cấm đóng bằng 'đã quét không thấy gì'",
           "Winston" in m and "ĐIỂM MÙ" in m)
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([FEED_FRESH, SCAN]) + "\n", env_tz)
        ck(f"[{tz_label}] feed FRESH + không marker nào -> rc=0, im lặng",
           r.returncode == 0 and not os.path.exists(os.path.join(sink, "notify.txt")),
           f"rc={r.returncode}")

        # Discord hỏng -> KHÔNG ghi de-dup cho khoá mới, và in LỖI THẬT
        with tempfile.TemporaryDirectory() as tmp2:
            tgt2 = _sandbox(tmp2)
            e = dict(env_tz or {})
            e["MIKE_SELFCHECK_NOTIFY_RC"] = "3"
            r = _run_alert(tmp2, tgt2, body, e)
            st2 = os.path.join(tmp2, "state", "adjfactor_drift_alerted.json")
            ck(f"[{tz_label}] Discord hỏng -> state de-dup RỖNG (không nói dối 'đã cảnh báo')",
               json.load(open(st2)) == {}, f"{open(st2).read()}")
            ck(f"[{tz_label}] Discord hỏng -> stderr nêu LỖI THẬT, rc=10",
               "THAT BAI" in r.stderr and r.returncode == 10, f"rc={r.returncode} {r.stderr!r}")

        # State hỏng -> fail-OPEN về phía gửi (thà cảnh báo lặp hơn mất cảnh báo) + nêu lỗi thật
        with tempfile.TemporaryDirectory() as tmp3:
            tgt3 = _sandbox(tmp3)
            os.makedirs(os.path.join(tmp3, "state"), exist_ok=True)
            open(os.path.join(tmp3, "state", "adjfactor_drift_alerted.json"), "w").write('{"a":')
            r = _run_alert(tmp3, tgt3, body, env_tz)
            ck(f"[{tz_label}] state JSON cụt -> VẪN gửi Discord",
               os.path.exists(os.path.join(tmp3, "sink", "notify.txt")), f"{r.stderr!r}")
            ck(f"[{tz_label}] state JSON cụt -> stderr nêu lỗi thật, không im lặng",
               "KHONG doc duoc state" in r.stderr or "state cu hong" in r.stderr, f"{r.stderr!r}")

        # Khối mã ĐANG NẮM không bao giờ bị cắt, dù nhiều hơn trần MAX_OTHER_LINES
        with tempfile.TemporaryDirectory() as tmp4:
            tgt4 = _sandbox(tmp4)
            many_held = [DRIFT_HELD.replace("VPB", f"H{i:02d}") for i in range(9)]
            many_free = [DRIFT_FREE.replace("FPT", f"F{i:02d}") for i in range(20)]
            r = _run_alert(tmp4, tgt4, "\n".join(many_held + many_free + [SCAN]) + "\n", env_tz)
            m = open(os.path.join(tmp4, "sink", "notify.txt")).read()
            ck(f"[{tz_label}] 9 mã NẮM đều có tên trên Discord (không cắt)",
               all(f"H{i:02d}" in m for i in range(9)))
            ck(f"[{tz_label}] mã KHÔNG nắm bị cắt ở trần + nói rõ còn bao nhiêu",
               "và 14 mã nữa" in m, f"{[l for l in m.splitlines() if 'mã nữa' in l]}")

        # held=unknown KHÔNG được in dưới tiêu đề "mã không nắm" (khẳng định SAI về phơi nhiễm
        # tiền thật, §29 dạng 2) và KHÔNG được bị trần MAX_OTHER_LINES cắt. Bản đầu gộp nó vào
        # `none`, arch-review 2026-09-27 đo được VPB −20,66% in ra như mã không nắm.
        with tempfile.TemporaryDirectory() as tmp5:
            tgt5 = _sandbox(tmp5)
            unk = [DRIFT_HELD.replace("VPB", f"U{i:02d}").replace("SpaceX,ZaloPay", "unknown")
                   for i in range(9)]
            free = [DRIFT_FREE.replace("FPT", f"F{i:02d}") for i in range(10)]
            _run_alert(tmp5, tgt5, "\n".join(unk + free + [FEED_FRESH, SCAN]) + "\n", env_tz)
            m = open(os.path.join(tmp5, "sink", "notify.txt")).read()
            ck(f"[{tz_label}] held=unknown có mục RIÊNG, không nằm dưới 'Mã không nắm'",
               "KHÔNG TRA ĐƯỢC VỊ THẾ" in m)
            unk_sec = m.split("KHÔNG TRA ĐƯỢC VỊ THẾ")[1].split("__**")[0]
            ck(f"[{tz_label}] cả 9 mã held=unknown đều có tên (KHÔNG bị trần cắt)",
               all(f"U{i:02d}" in unk_sec for i in range(9)),
               f"{[i for i in range(9) if f'U{i:02d}' not in unk_sec]}")
            other_sec = m.split("Mã không nắm")[1].split("__**")[0]
            ck(f"[{tz_label}] không mã unknown nào lọt vào khối 'Mã không nắm'",
               not any(f"U{i:02d}" in other_sec for i in range(9)))
            ck(f"[{tz_label}] có dòng việc-cần-làm cho ca không tra được vị thế",
               "broker_qty" in m)

        r = _run_alert(tmp, tgt, body, env_tz, args=())
        ck(f"[{tz_label}] thiếu đối số topic -> rc=2", r.returncode == 2, f"rc={r.returncode}")


# ------------------------------------------------------- 9. runner adjfactor_drift_daily.sh

def t_runner():
    print("\n[9] adjfactor_drift_daily.sh — tách cờ, và rc=1/2 KHÔNG được đọc thành 'sạch'")
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "bin"))
        os.makedirs(os.path.join(tmp, "sink"))
        sink = os.path.join(tmp, "sink")
        # Detector giả: ghi lại ĐÚNG đối số nó nhận được, rồi trả rc theo env.
        det_stub = os.path.join(tmp, "bin", "adjfactor_drift_detect.py")
        open(det_stub, "w").write(
            "#!/usr/bin/env bash\n"
            'printf "%s\\n" "$@" > "$MIKE_SELFCHECK_SINK/det_args.txt"\n'
            'printf "%s\\n" "${MIKE_SELFCHECK_DET_OUT:-}"\n'
            'exit ${MIKE_SELFCHECK_DET_RC:-0}\n')
        os.chmod(det_stub, 0o755)
        alert_stub = os.path.join(tmp, "bin", "adjfactor_drift_alert.sh")
        open(alert_stub, "w").write(
            "#!/usr/bin/env bash\n"
            'printf "%s\\n" "$@" > "$MIKE_SELFCHECK_SINK/alert_args.txt"\n'
            'cat > "$MIKE_SELFCHECK_SINK/alert_stdin.txt"\n'
            "exit 10\n")
        os.chmod(alert_stub, 0o755)
        for name, body in (("notify_thread.sh", ALERT_STUB_NOTIFY),):
            q = os.path.join(tmp, "bin", name)
            open(q, "w").write(body)
            os.chmod(q, 0o755)
        tgt = os.path.join(tmp, "bin", "adjfactor_drift_daily.sh")
        open(tgt, "w").write(open(os.path.join(HERE, "adjfactor_drift_daily.sh")).read())
        os.chmod(tgt, 0o755)

        def run(args, rc=0, out=SCAN):
            env = dict(os.environ)
            env["MIKE_SELFCHECK_SINK"] = sink
            env["MIKE_SELFCHECK_DET_RC"] = str(rc)
            env["MIKE_SELFCHECK_DET_OUT"] = out
            for f in ("det_args.txt", "alert_args.txt", "notify.txt"):
                if os.path.exists(os.path.join(sink, f)):
                    os.remove(os.path.join(sink, f))
            return subprocess.run(["bash", tgt, *args], capture_output=True, text=True, env=env)

        r = run(["--dry-run", "--tickers", "FPT"], rc=10)
        det_args = open(os.path.join(sink, "det_args.txt")).read().split()
        ck("--dry-run KHÔNG bị chuyển vào detector (nó sẽ rc=2 và gửi Discord thật)",
           "--dry-run" not in det_args and det_args == ["--tickers", "FPT"], f"{det_args}")
        ck("--dry-run ĐƯỢC chuyển vào alert",
           "--dry-run" in open(os.path.join(sink, "alert_args.txt")).read())
        ck("runner trả rc của alert khi detector chạy được", r.returncode == 10, f"rc={r.returncode}")
        ck("output detector được đưa nguyên vào stdin của alert",
           SCAN in open(os.path.join(sink, "alert_stdin.txt")).read())

        r = run(["--dry-run"], rc=1, out="[FATAL] BQ chet: TimeoutExpired")
        ck("detector rc=1 -> KHÔNG gọi alert (không có kết luận nào để cảnh báo)",
           not os.path.exists(os.path.join(sink, "alert_args.txt")))
        ck("detector rc=1 -> runner trả rc=1, KHÔNG phải 0/10", r.returncode == 1, f"rc={r.returncode}")
        ck('detector rc=1 -> thông điệp nói rõ "KHÔNG phải không có lệch"',
           "KHÔNG phải" in r.stderr and "FATAL" in r.stderr, f"{r.stderr[-300:]!r}")
        ck("detector rc=1 + --dry-run -> KHÔNG gửi Discord",
           not os.path.exists(os.path.join(sink, "notify.txt")))

        # M31 (arch-review vòng 3): F2 chỉ được chốt cho rc=1, nên mutation NỚI allow-list thành
        # `0|10|11|124|137` vẫn 301/301 — trong khi CHÍNH cái bị vá là "một rc BẤT NGỜ phải là thất
        # bại". Chốt bằng đúng hai rc mà kernel/timeout sinh ra.
        for bad_rc in (124, 137, 3):
            r = run(["--dry-run"], rc=bad_rc, out=SCAN)
            ck(f"detector rc={bad_rc} (ngoài allow-list) -> runner trả {bad_rc}, KHÔNG phải 0/10 (M31)",
               r.returncode == bad_rc, f"rc={r.returncode}")
            ck(f"detector rc={bad_rc} -> KHÔNG gọi alert, và nói rõ KHÔNG phải 'không có lệch'",
               "KHONG goi alert" in r.stderr and "KHÔNG phải" in r.stderr, f"{r.stderr[-200:]!r}")
        # rc=11 (điểm mù) NẰM TRONG allow-list: nó có kết luận, phải đi tiếp sang alert
        r = run(["--dry-run"], rc=11, out="\n".join([UNCOMP_HELD, FEED_FRESH, SCAN]))
        ck("detector rc=11 (điểm mù) -> VẪN gọi alert (nằm trong allow-list)",
           "KHONG goi alert" not in r.stderr, f"{r.stderr[-200:]!r}")

        r = run([], rc=1, out="[FATAL] BQ chet")
        ck("detector rc=1 KHÔNG dry-run -> CÓ gửi Discord cảnh báo hạ tầng",
           os.path.exists(os.path.join(sink, "notify.txt")))
        ck("cảnh báo hạ tầng trích LỖI THẬT detector in ra, không phải câu đoán",
           "BQ chet" in open(os.path.join(sink, "notify.txt")).read())

        r = run(["--dry-run"], rc=0, out=SCAN)
        ck("detector rc=0 (sạch) -> vẫn gọi alert (alert tự exit 0 nếu không có marker)",
           os.path.exists(os.path.join(sink, "alert_args.txt")))


# --------------------------------------------------- 11. lỗi hạ tầng KHÔNG được thành "sạch"

def t_infra():
    print("\n[11] detector: BQ chết -> rc=1 (KHÔNG phải 0/11) và in LỖI THẬT")
    # Mutation M15 (arch-review 2026-09-27): đổi `return 1` thành `return 0` trong nhánh FATAL vẫn
    # 142/142 PASS — hành vi ĐÚNG nhưng không được test. Phần shell chỉ test bằng detector-stub có
    # rc lấy từ env, nên nó không phủ được nhánh này của chính Python.
    real = det.cal.bq
    try:
        def boom(*_a, **_k):
            raise RuntimeError("bq CLI khong chay duoc (gia lap)")
        det.cal.bq = boom
        import io
        import contextlib
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = det.main(["--tickers", "FPT", "--no-holdings"])
    finally:
        det.cal.bq = real
    ck("cal.bq ném -> rc=1", rc == 1, f"rc={rc}")
    ck("stderr có nhãn [FATAL] + LỖI THẬT (loại + thông điệp), không phải câu đoán",
       "[FATAL]" in err.getvalue() and "RuntimeError" in err.getvalue()
       and "bq CLI khong chay duoc" in err.getvalue(), f"{err.getvalue()!r}")
    ck("stderr nói rõ KHÔNG kết luận gì", "KHONG ket luan gi" in err.getvalue())

    # Universe rỗng KHÔNG được là rc=0: cohort 30 ngày rỗng là bất khả về cấu trúc ở VN.
    try:
        det.cal.bq = lambda sql, **_k: ([{"d": "2026-09-25"}] if "MAX(t.time)" in sql else [])
        import io
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = det.main(["--no-holdings"])
    finally:
        det.cal.bq = real
    ck("universe rỗng -> rc=11 (điểm mù), KHÔNG phải 0", rc == 11, f"rc={rc}")
    ck("universe rỗng -> nói rõ 'DIEM MU', không phải 'khong co lech'",
       "DIEM MU" in out.getvalue(), f"{out.getvalue()[-300:]!r}")


def t_feedgate():
    print("\n[12] feed_gate — phân loại độ tươi feed nguồn (bảng TRAP, writer ngoài repo)")
    real = det.cal.feed_freshness
    try:
        def mk(ing):
            return lambda: {"max_ingested": ing, "max_public": "2026-09-25", "n": "36428"}
        det.cal.feed_freshness = mk("2026-09-25 15:43:40")
        ck("nạp cùng ngày phiên -> FRESH", det.feed_gate("2026-09-25")[0] == "FRESH")
        det.cal.feed_freshness = mk("2026-09-23 15:00:00")
        st, d = det.feed_gate("2026-09-25")
        ck("nạp trước phiên 2 ngày -> STALE", st == "STALE", f"{st}")
        ck("STALE có lý do TRÍCH TỪ SỐ ĐÃ ĐỌC, không phải câu cố định",
           "2026-09-25" in d["reason"] and str(d["age_days"]) in d["reason"], f"{d}")
        det.cal.feed_freshness = mk("2026-09-10 15:00:00")
        st, d = det.feed_gate("2026-09-25")
        ck(f"nạp cũ > {det.FEED_DEAD_DAYS} ngày -> DEAD", st == "DEAD", f"{st}")
        det.cal.feed_freshness = mk("khong-phai-ngay")
        st, d = det.feed_gate("2026-09-25")
        ck("max_ingested không đọc được -> UNREADABLE (KHÔNG fail-open thành FRESH)",
           st == "UNREADABLE", f"{st}")
        ck("UNREADABLE trích giá trị thô đã đọc vào lý do",
           "khong-phai-ngay" in d["reason"], f"{d}")

        def raiser():
            raise RuntimeError("BQ timeout (gia lap)")
        det.cal.feed_freshness = raiser
        st, d = det.feed_gate("2026-09-25")
        ck("feed_freshness() ném -> UNREADABLE + LỖI THẬT trong lý do",
           st == "UNREADABLE" and "RuntimeError" in d["reason"] and "BQ timeout" in d["reason"],
           f"{st} {d}")
    finally:
        det.cal.feed_freshness = real
    ck("FEED_DEAD_DAYS khớp nguồn chuẩn tắc corp_action_daily.py", det.FEED_DEAD_DAYS == 5)


# ---------------------------------- 13. run_scan PHÁT RA GÌ (kill M7/M8/M18/M19)

def t_emit():
    """Chốt hợp đồng ở TẦNG `run_scan`, không chỉ ở `marker_*`.

    arch-review vòng 2: `marker_*` đã được unit-test và `alert.sh` đã được test bằng dòng viết tay,
    nhưng KHÔNG có gì chốt rằng `run_scan` THẬT SỰ in ra marker nào và trả rc nào. 4 mutation sống
    sót 233/233 vì đúng khe này:
      M7  — bỏ `print(marker_feed(...))`      ⇒ alert.sh không thấy FEED ⇒ im lặng (F5)
      M8  — bỏ `feed_status != FRESH` khỏi rc ⇒ feed chết trả rc=0 = "sạch"
      M18 — bỏ `print(marker_nodata(...))`    ⇒ mã đang NẮM không có giá không sinh ra gì
      M19 — `held=None` gán nhãn `none`       ⇒ khẳng định SAI "không nắm" (F1)
    Cách chốt: chạy `run_scan` thật với mọi lối ra BQ được thay bằng dữ liệu tổng hợp, rồi so TỪNG
    dòng stdout — đây là mức duy nhất bắt được cả 4.
    """
    print("\n[13] run_scan — marker thật phát ra + rc thật (kill M7/M8/M18/M19)")

    class A:
        asof = "2026-08-10"; ex0 = "2026-06-01"; ex1 = "2026-08-10"; ex_days = 30
        lookback_days = 120; dev_tol = 0.003; min_run = 3; tickers = None; no_holdings = False

    evs = [ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.1, tk="HELDX")]

    def run(feed_ing, held_ret, with_nodata):
        """(rc, stdout) của một lượt run_scan thật."""
        saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
                 det.cal.events, det.bq_max_session)
        tks = ["HELDX"] + (["NOPRICE"] if with_nodata else [])
        try:
            det.cohort_tickers = lambda a, b: tks
            det.bq_max_session = lambda: A.asof
            # HELDX: vendor CHƯA áp hệ số -> DRIFT. NOPRICE: không có dòng giá nào -> NODATA.
            det.price_rows = lambda t, s, e: [
                {"tk": "HELDX", "d": b["d"], "close": b["close"], "price": b["price"],
                 "hi": b["hi"], "lo": b["lo"]} for b in flat_series(D, 100, 1.0)]
            det.held_map = lambda asof, **kw: held_ret
            det.cal.feed_freshness = lambda: {"max_ingested": feed_ing,
                                              "max_public": "2026-08-10", "n": "36428"}
            det.cal.events = lambda t, since=None, until=None: evs
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = det.run_scan(A)
            return rc, buf.getvalue()
        finally:
            (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session) = saved

    # --- M7: dòng FEED phải CÓ trong stdout thật
    rc, out = run("2026-08-10 15:00:00", {"HELDX": "SpaceX"}, False)
    ck("run_scan IN RA dòng ADJFACTOR_FEED (M7)",
       any(l.startswith("ADJFACTOR_FEED|FRESH|") for l in out.splitlines()), f"{out[:300]!r}")
    ck("run_scan in ra dòng DRIFT cho mã lệch", "ADJFACTOR_DRIFT|HELDX|" in out)
    ck("dòng DRIFT mang nhãn nắm THẬT (không phải 'none')",
       "|vendor_missing|SpaceX|" in out,
       f"{[l for l in out.splitlines() if l.startswith('ADJFACTOR_DRIFT')]}")
    ck("có DRIFT -> rc=10", rc == 10, f"rc={rc}")

    # --- M19: held_map() trả None (nguồn hỏng) PHẢI thành `unknown`, KHÔNG được thành `none`
    rc, out = run("2026-08-10 15:00:00", None, False)
    dl = [l for l in out.splitlines() if l.startswith("ADJFACTOR_DRIFT")]
    ck("held_map()=None -> nhãn `unknown`, KHÔNG phải `none` (M19/F1)",
       dl and dl[0].endswith("|unknown|0"), f"{dl}")
    ck("held_map()=None: KHÔNG có dòng nào mang nhãn `none`",
       not any(l.endswith("|none|0") for l in dl), f"{dl}")

    # --- F7: --no-holdings là `skipped`, KHÁC `unknown` (không được sinh dòng việc 'broker_qty lỗi')
    A.no_holdings = True
    rc, out = run("2026-08-10 15:00:00", None, False)
    dl = [l for l in out.splitlines() if l.startswith("ADJFACTOR_DRIFT")]
    ck("--no-holdings -> nhãn `skipped`, KHÔNG phải `unknown` (F7)",
       dl and dl[0].endswith("|skipped|0"), f"{dl}")
    A.no_holdings = False

    # --- M18: NODATA phải có DÒNG RIÊNG, không chỉ là một con số trong SCAN
    rc, out = run("2026-08-10 15:00:00", {"HELDX": "SpaceX"}, True)
    ck("mã không có dòng giá -> IN RA ADJFACTOR_NODATA (M18)",
       "ADJFACTOR_NODATA|NOPRICE|" in out, f"{out[:400]!r}")
    ck("dòng NODATA mang nhãn nắm (mã không nắm vẫn phải có dòng để bus thấy)",
       "ADJFACTOR_NODATA|NOPRICE|none" in out)

    # --- M8: feed KHÔNG tươi phải vào rc, kể cả khi mọi mã đều KHỚP
    def run_clean(feed_ing):
        saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
                 det.cal.events, det.bq_max_session)
        try:
            det.cohort_tickers = lambda a, b: ["OKX"]
            det.bq_max_session = lambda: A.asof
            # vendor áp ĐÚNG hệ số -> AGREE, 0 uncomputable, 0 nodata
            det.price_rows = lambda t, s, e: [
                {"tk": "OKX", "d": b["d"], "close": b["close"], "price": b["price"],
                 "hi": b["hi"], "lo": b["lo"]}
                for b in (bar(d, 100, 100 / (1.1 if d < "2026-08-05" else 1.0)) for d in D)]
            det.held_map = lambda asof, **kw: {}
            det.cal.feed_freshness = lambda: {"max_ingested": feed_ing,
                                              "max_public": "2026-08-10", "n": "36428"}
            det.cal.events = lambda t, since=None, until=None: [
                ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.1, tk="OKX")]
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = det.run_scan(A)
            return rc, buf.getvalue()
        finally:
            (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session) = saved

    rc, out = run_clean("2026-08-10 15:00:00")
    ck("mọi mã khớp + feed FRESH -> rc=0 (trạng thái 'không có gì' DUY NHẤT)", rc == 0, f"rc={rc}")
    ck("lượt sạch vẫn in ADJFACTOR_SCAN", "ADJFACTOR_SCAN|" in out)
    rc, out = run_clean("2026-07-20 15:00:00")     # cũ > FEED_DEAD_DAYS
    ck("mọi mã khớp nhưng feed CHẾT -> rc=11, KHÔNG phải 0 (M8)", rc == 11, f"rc={rc}")
    ck("feed chết in ra status DEAD để alert.sh đọc được",
       any(l.startswith("ADJFACTOR_FEED|DEAD|") for l in out.splitlines()),
       f"{[l for l in out.splitlines() if l.startswith('ADJFACTOR_FEED')]}")


# --------------------------- 14. held_map fail-closed + corr (F1 / F4 / F6 / F8)

def t_held_and_corr():
    print("\n[14] held_map fail-closed · corr đính chính · knob làm-im (F1/F4/F6/F8)")

    # --- F1: broker_qty() trả {} KHÔNG raise ⇒ phải là None (unknown), không phải {} (none)
    import types
    fake = types.ModuleType("dividend_adjusted_return")
    fake.ACCOUNTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
    fake.broker_qty = lambda acct: {}
    sys.modules["dividend_adjusted_return"] = fake
    try:
        ck("broker_qty() trả {} (không raise) -> held_map = None, KHÔNG phải {} (F1)",
           det.held_map("2026-09-25") is None)
        # ảnh chụp CŨ hơn ngưỡng -> None (§14)
        fake.broker_qty = lambda acct: {("VPB", "2026-09-01"): 1000}
        ck(f"ảnh chụp cũ > {det.HELD_MAX_STALE_DAYS} ngày -> held_map = None (freshness §14)",
           det.held_map("2026-09-25") is None)
        fake.broker_qty = lambda acct: {("VPB", "2026-09-25"): 1000}
        hm = det.held_map("2026-09-25")
        ck("ảnh chụp TƯƠI -> trả map thật", hm == {"VPB": "SpaceX,ZaloPay"}, f"{hm}")
        fake.broker_qty = lambda acct: {("VPB", "2026-09-25"): 0}
        ck("qty = 0 -> KHÔNG tính là đang nắm", det.held_map("2026-09-25") == {})

        # R3-1: MỘT tài khoản hỏng cũng phải fail-closed. Vòng 2 chỉ chặn ca CẢ HAI rỗng, nên một
        # tài khoản hỏng bị `continue` bỏ qua lặng lẽ ⇒ mã chỉ nắm ở tài khoản đó bị gán `none`
        # (đo thật trên dar THẬT: ZaloPay hỏng ⇒ CSV/DGC thành 'none', đúng lại failure mode F1).
        fake.broker_qty = lambda acct: ({("VPB", "2026-09-25"): 1000}
                                        if acct == "0002023347" else {})
        ck("MỘT tài khoản rỗng (tài khoản kia khoẻ) -> held_map = None (R3-1)",
           det.held_map("2026-09-25") is None)
        fake.broker_qty = lambda acct: {("VPB", "2026-09-25"): 1000}
        ck("CẢ HAI tài khoản trả vị thế -> mới được dùng nhãn nắm",
           det.held_map("2026-09-25") == {"VPB": "SpaceX,ZaloPay"})
    finally:
        sys.modules.pop("dividend_adjusted_return", None)

    # --- F4: ex-date có >1 dòng CÙNG event_code -> corr_ex, và corr=1 tới được dòng máy đọc
    s = [bar(d, 100, 100) for d in D]
    _c, _u, _n, _unk, corr = det.build_factor_curve(s, [
        ev("2026-08-05", "DIV", dps=500), ev("2026-08-05", "DIV", dps=800)])
    ck("2 dòng DIV cùng ex-date (nghi đính chính) -> corr_ex có ex-date đó (F4)",
       corr == {"2026-08-05"}, f"{corr}")
    # ca thật: DIV 500 + "Điều chỉnh 800" trên giá thô, vendor áp 1.017410 mà ta suy 1.028603
    ser = [bar(d, 46750, 46750 / (1.017410 if d < "2026-08-05" else 1.0)) for d in D]
    v, p = det.scan_ticker(ser, [ev("2026-08-05", "DIV", dps=500),
                                 ev("2026-08-05", "DIV", dps=800)], 0.003, 3, D[0])
    ck("ca đính chính -> DRIFT với corr=1 (caveat đi CÙNG cáo buộc, §29)",
       v == "DRIFT" and p["corr"] == "1", f"v={v} corr={p.get('corr')}")
    ck("dòng máy đọc mang corr=1 ở trường cuối",
       det.marker_drift("AAA", p, "SpaceX").endswith("|SpaceX|1"),
       det.marker_drift("AAA", p, "SpaceX"))
    # và ca KHÔNG đính chính phải là corr=0 (nếu luôn 1 thì cờ vô nghĩa)
    v2, p2 = det.scan_ticker(flat_series(D, 100, 1.0),
                             [ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.1)], 0.003, 3, D[0])
    ck("ca thường -> corr=0 (cờ phân biệt được, không phải luôn bật)", p2["corr"] == "0")

    # --- F8: AGREE phải nghĩa là ĐÃ SO; quá ít phiên -> UNCOMPUTABLE, không phải AGREE
    v, p = det.scan_ticker([bar("2026-08-09", 100, 100)],
                           [ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.1)], 0.003, 3, "2026-08-08")
    ck(f"chỉ so được 1 phiên (< {det.MIN_EVAL_SESSIONS}) -> UNCOMPUTABLE, KHÔNG phải AGREE (F8)",
       v == "UNCOMPUTABLE", f"v={v} p={p}")
    ck("mã lý do nói rõ thiếu phiên để so",
       v == "UNCOMPUTABLE" and p["unknown"][0][1] == "too_few_sessions_to_compare",
       f"{p.get('unknown')}")

    # --- F6: chiều LÀM IM của các knob bị từ chối cứng
    ck("--min-run 9999 bị TỪ CHỐI (chiều làm im) (F6)", _exits_2(["--min-run", "9999"]))
    ck("--lookback-days 2 bị TỪ CHỐI (chiều làm im)", _exits_2(["--lookback-days", "2"]))
    ck("--ex-days 0 bị TỪ CHỐI", _exits_2(["--ex-days", "0"]))
    # R3-6: trần cũ 0.5 cao hơn sàn bằng chứng 0,3% hai bậc; `--dev-tol 0.4` đã biến lệch lớp VPB
    # −20,66% thành AGREE. Đây là chiều LÀM IM, phải chặn như min-run/lookback.
    ck(f"--dev-tol 0.4 bị TỪ CHỐI (> DEV_TOL_MAX={det.DEV_TOL_MAX}, chiều làm im) (R3-6)",
       _exits_2(["--dev-tol", "0.4"]))
    ck("--dev-tol 0.003 (mặc định, sàn bằng chứng) VẪN được nhận",
       not _exits_2(["--dev-tol", "0.003", "--no-holdings", "--asof", "1999-01-01",
                     "--tickers", "ZZZ"]))
    ck("R3-5: selfcheck KHÔNG chạm BigQuery — cổng MIKE_ADJFACTOR_NO_BQ có tác dụng thật",
       det.bq_guard_active({"MIKE_ADJFACTOR_NO_BQ": "1"}) is True
       and det.bq_guard_active({}) is False)
    ck("--min-run 3 (mặc định) VẪN được nhận — cổng không chặn oan giá trị đúng",
       not _exits_2(["--min-run", "3", "--no-holdings", "--asof", "1999-01-01",
                     "--tickers", "ZZZ"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--py", action="store_true")
    ap.add_argument("--sh", action="store_true")
    a = ap.parse_args()
    do_py = a.py or not a.sh
    do_sh = a.sh or not a.py

    print("=== selfcheck adjfactor Layer 1 (DETECT-ONLY) ===")
    if do_py:
        t_formula()
        t_failclosed()
        t_ffill_guard()
        t_curve()
        t_persistence()
        t_scan()
        t_contract()
        t_infra()
        t_feedgate()
        t_emit()
        t_held_and_corr()
    if do_sh:
        # §16/§19: LẶP dưới 4 môi trường TZ. `unset TZ` = ca cron thật (không có TZ trong env).
        # `Pacific/Kiritimati` (+14) và `Pacific/Midway` (−11) là hai đầu cực: với MỌI thời điểm,
        # ít nhất một trong hai khác NGÀY LỊCH với ICT (+07) ⇒ assertion neo-TZ không bao giờ vô
        # nghĩa cả bốn lượt. `UTC` giữ lại vì đó là TZ thật của nhiều môi trường CI.
        for label, envd in (("unset TZ", {"__unset_tz__": "1"}),
                            ("TZ=UTC", {"TZ": "UTC"}),
                            ("TZ=Pacific/Kiritimati", {"TZ": "Pacific/Kiritimati"}),
                            ("TZ=Pacific/Midway", {"TZ": "Pacific/Midway"})):
            if "__unset_tz__" in envd:
                envd = {}
                os.environ.pop("TZ", None)
            t_alert(label, envd)
        t_runner()
        print("\n[10] meta — assertion neo-TZ có thật sự phân biệt được không (§19)")
        ck(f"có ít nhất MỘT môi trường TZ phân biệt được ngày host với ngày ICT "
           f"(không vô nghĩa): {NON_VACUOUS or 'KHÔNG CÓ'}",
           len(NON_VACUOUS) >= 1, f"vacuous={VACUOUS}")

    print(f"\n=== {N - len(FAILS)}/{N} assertion PASS ===")
    if FAILS:
        print("FAIL:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
