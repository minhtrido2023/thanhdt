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
from datetime import date, timedelta
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adjfactor_drift_detect as det  # noqa: E402

# Selfcheck KHÔNG BAO GIỜ chạm DNSE thật: `run_scan` gọi `live_exchange_fn()` để lấy bước giá cho luật
# PRICE_FIELD_MISMATCH. Bản thật giữ lại để test riêng ở [17] với broker giả.
_REAL_LIVE_EXCHANGE_FN = det.live_exchange_fn
det.live_exchange_fn = lambda: (lambda tk: None)

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


def ck_perm(label, cond, detail=""):
    """`ck` cho test dựa trên chmod: root (euid 0) bỏ qua quyền thư mục ⇒ ca không tái hiện được ⇒ N/A,
    KHÔNG phải FAIL và KHÔNG đếm là PASS."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print(f"  N/A  {label}   (euid=0: root bo qua chmod, khong tai hien duoc)")
        return
    ck(label, cond, detail)


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
POST_EX = ["2026-08-20", "2026-08-21", "2026-08-24"]   # 3 phiên có khớp từ ex 08-20 (gồm ex)


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

    # Chữ ký FPT: vendor chưa áp hệ số -> r_obs = 1.0 trong khi r_pred = 1.1. `POST_EX` = 3 phiên CÓ
    # khớp từ ex-date (FPT thật đã giao dịch lại) — thiếu chúng thì đúng là ca AWAITING_TRADE ([15]).
    v, p = det.scan_ticker(flat_series(D + POST_EX, 100, 1.0), evs, 0.003, 3, D[0])
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
    v, p = det.scan_ticker(flat_series(D + POST_EX, 100, 1.0), mixed, 0.003, 3, D[0])
    ck("ca XHC: uncomputable ở giữa + lệch sau -> DRIFT", v == "DRIFT", f"v={v}")
    ck("ca XHC: đánh dấu partial", p["partial"] is True)
    ck("ca XHC: cửa sổ chấm điểm bắt đầu TỪ ex-date uncomputable, không sớm hơn",
       p["d0"] >= "2026-06-15", f"d0={p.get('d0')}")

    # eval_from = rìa cửa sổ đánh giá: phiên trước đó chỉ để tìm phiên cum, không chấm điểm
    v, p = det.scan_ticker(flat_series(D + POST_EX, 100, 1.0), evs, 0.003, 3, "2026-07-05")
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
            ck_perm(f"[{tz_label}] state/ read-only -> VẪN gửi Discord (fail-open về phía GỬI) (R3-4)",
                    sent, f"rc={r.returncode} {r.stderr[-300:]!r}")
            ck_perm(f"[{tz_label}] lock không mở được: trích LỖI THẬT, KHÔNG nói 'lượt khác đang chạy'",
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
            ck_perm(f"[{tz_label}] ghi state hỏng -> KHÔNG bung traceback trần (M45)",
                    "Traceback (most recent call last)" not in r.stderr, f"{r.stderr[-400:]!r}")
            ck_perm(f"[{tz_label}] ghi state hỏng -> nói rõ 'lượt sau GỬI LẠI' + lỗi thật",
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


# ----------------------------- 15. AWAITING_TRADE — CHỜ GIAO DỊCH LẠI (job Taylor_20261008_032221)

def _vbar(d, price, close, vol):
    b = bar(d, price, close)
    b["vol"] = vol
    return b


def t_awaiting():
    """Ngưỡng 3 phiên khớp, chỉ cho `vendor_missing`/corr=0/ex-date thật, và hợp đồng dòng máy đọc.

    Chữ ký thật (asof 2026-10-07): 9 mã 0 dòng từ ex-date ⇒ awaiting; DRI/DVN/SHC 12/19/8 phiên ⇒
    DRIFT. SHC có 6 dòng `Volume=0` xen giữa — chúng KHÔNG được đếm là phiên khớp.
    """
    print("\n[15] AWAITING_TRADE — ngưỡng phiên khớp + ranh giới với DRIFT")
    EX = "2026-08-20"
    evs = [ev(EX, "ISS", "Cổ phiếu thưởng", 0.1)]
    pre = flat_series(D, 100, 1.0)                      # vendor CHƯA áp hệ số 1,1

    def post(vols):
        return [_vbar(d, 100, 100, v) for d, v in zip(POST_EX + ["2026-08-25", "2026-08-26",
                                                                 "2026-08-27", "2026-08-28"], vols)]

    ck("hằng số có tên AWAIT_MIN_TRADED_SESSIONS == 3", det.AWAIT_MIN_TRADED_SESSIONS == 3)

    # Volume phải đi CÙNG câu SQL giá đã có (không thêm truy vấn mới). Thiếu nó ⇒ mọi `vol` None ⇒
    # không bao giờ có awaiting (an toàn nhưng tắt tính năng một cách im lặng).
    seen_sql = []
    saved_bq = det._bq
    try:
        det._bq = lambda sql: seen_sql.append(sql) or []
        det.price_rows(["AAA"], "2026-08-01", "2026-08-28")
    finally:
        det._bq = saved_bq
    ck("price_rows: MỘT truy vấn, chọn `t.Volume AS vol`",
       len(seen_sql) == 1 and "t.Volume AS vol" in seen_sql[0], f"{seen_sql}")

    v, p = det.scan_ticker(pre, evs, 0.003, 3, D[0])
    ck("0 phiên từ ex-date -> AWAITING_TRADE, n_traded=0",
       v == "AWAITING_TRADE" and p.get("n_traded") == 0, f"v={v} n={p.get('n_traded')}")
    ck("awaiting vẫn mang đủ payload DRIFT (ex, dev, dir) — không mất bằng chứng",
       p.get("ex") == EX and p.get("dir") == "vendor_missing" and abs(p["dev"] + 0.0909090909) < 1e-6,
       f"{p.get('ex')} {p.get('dir')} {p.get('dev')}")

    v, p = det.scan_ticker(pre + post([1000, 500]), evs, 0.003, 3, D[0])
    ck("2 phiên khớp -> vẫn AWAITING_TRADE (cho vendor thời gian)",
       v == "AWAITING_TRADE" and p.get("n_traded") == 2, f"v={v} n={p.get('n_traded')}")

    v, p = det.scan_ticker(pre + post([1000, 500, 300]), evs, 0.003, 3, D[0])
    ck("3 phiên khớp mà vẫn lệch -> DRIFT thật", v == "DRIFT" and p.get("n_traded") == 3,
       f"v={v} n={p.get('n_traded')}")

    # ex-date TÍNH LUÔN: 3 phiên khớp đúng tại ex, ex+1, ex+2 ⇒ 3, không phải 2.
    v, p = det.scan_ticker(pre + post([1, 1, 1]), evs, 0.003, 3, D[0])
    ck("phiên ex-date được đếm (>= ex, không phải > ex)", v == "DRIFT" and p.get("n_traded") == 3,
       f"v={v} n={p.get('n_traded')}")

    # Chữ ký SHC: dòng `Volume=0` (ffill) KHÔNG phải phiên khớp.
    v, p = det.scan_ticker(pre + post([0, 0, 0, 0, 0, 700, 800]), evs, 0.003, 3, D[0])
    ck("dòng Volume=0 không đếm: 5 dòng 0 + 2 khớp -> AWAITING n=2",
       v == "AWAITING_TRADE" and p.get("n_traded") == 2, f"v={v} n={p.get('n_traded')}")
    v, p = det.scan_ticker(pre + post([0, 0, 0, 0, 600, 700, 800]), evs, 0.003, 3, D[0])
    ck("4 dòng 0 + 3 khớp -> DRIFT", v == "DRIFT" and p.get("n_traded") == 3,
       f"v={v} n={p.get('n_traded')}")

    # Volume thiếu/NULL nghiêng về CẢNH BÁO, không về im lặng.
    v, p = det.scan_ticker(pre + post([None, None, None]), evs, 0.003, 3, D[0])
    ck("Volume NULL đếm là CÓ khớp (fail về phía DRIFT)", v == "DRIFT", f"v={v} n={p.get('n_traded')}")
    ck("series_by_ticker giữ Volume NULL là None (không ép 0)",
       det.series_by_ticker([{"tk": "A", "d": "2026-08-20", "close": 1, "price": 1, "hi": 1,
                              "lo": 1, "vol": None}])["A"][0]["vol"] is None)
    ck("series_by_ticker đọc Volume số",
       det.series_by_ticker([{"tk": "A", "d": "2026-08-20", "close": 1, "price": 1, "hi": 1,
                              "lo": 1, "vol": "1500"}])["A"][0]["vol"] == 1500.0)

    # our_table_missing: 0 phiên vẫn DRIFT (lệch dương không giải thích được bằng "vendor chưa áp").
    v, p = det.scan_ticker(flat_series(D, 100, 1.25), evs, 0.003, 3, D[0])
    ck("our_table_missing + 0 phiên -> DRIFT, KHÔNG awaiting",
       v == "DRIFT" and p["dir"] == "our_table_missing" and p["ex"] == EX, f"v={v} {p.get('dir')}")
    ck("our_table_missing KHÔNG đi qua nhánh awaiting (không chứng từ 'chua du 3 phien')",
       not any("chua du" in n for n in p["notes"]) and "await_resid" not in p, f"{p['notes']}")

    # corr=1: 0 phiên vẫn DRIFT để caveat đính chính đi cùng cáo buộc.
    corr = [ev(EX, "DIV", dps=2), ev(EX, "DIV", dps=3)]     # f = 100/95 trên giá thô 100
    v, p = det.scan_ticker(pre, corr, 0.003, 3, D[0])
    ck("corr=1 + 0 phiên -> DRIFT (giữ cờ đính chính), KHÔNG awaiting",
       v == "DRIFT" and p.get("corr") == "1", f"v={v} corr={p.get('corr')}")

    # vendor_missing nhưng KHÔNG có ex-date nào để đếm (unknown_gap) -> DRIFT.
    v, p = det.scan_ticker(flat_series(D, 100, 0.9), [], 0.003, 3, D[0])
    ck("vendor_missing + unknown_gap -> DRIFT (không có ngày để đếm)",
       v == "DRIFT" and p["dir"] == "vendor_missing" and p["ex"].startswith("unknown_gap@"),
       f"v={v} ex={p.get('ex')}")
    ck("unknown_gap KHÔNG đi qua nhánh awaiting (không chứng từ 'chua du 3 phien')",
       not any("chua du" in n for n in p["notes"]) and "await_resid" not in p, f"{p['notes']}")

    # Chữ ký FPT `SETTLE_RUN=4` (arch-review vòng 2): vendor áp hệ số cho đúng 4 phiên cum cuối rồi
    # dừng. Dư tại phiên tệ nhất = 0 y như "chưa áp gì", nhưng 4 phiên giữa cụm lệch và ex-date KHỚP
    # ⇒ vendor ĐÃ chạy ⇒ phải là DRIFT, kể cả khi mới 1 phiên khớp từ ex-date.
    fpt = flat_series(D[:-4], 100, 1.0) + flat_series(D[-4:], 100, 1.1)
    v, p = det.scan_ticker(fpt + post([1000]), evs, 0.003, 3, D[0])
    ck("chữ ký FPT SETTLE_RUN=4 + 1 phiên khớp -> DRIFT, KHÔNG awaiting",
       v == "DRIFT" and p.get("d1") == D[-5] and p.get("n_traded") == 1, f"v={v} {p.get('d1')}")
    ck("chữ ký FPT: chứng từ nói rõ vendor đã áp một phần",
       any("vendor da ap mot phan" in n for n in p["notes"]), f"{p['notes']}")
    # Khe NHỎ NHẤT (arch-review vòng 2, B3): 1-2 phiên cum đã khớp vẫn là bằng chứng vendor đã chạy.
    for k in (1, 2):
        part = flat_series(D[:-k], 100, 1.0) + flat_series(D[-k:], 100, 1.1)
        v, p = det.scan_ticker(part + post([1000]), evs, 0.003, 3, D[0])
        ck(f"khe {k} phiên giữa cụm lệch và ex-date + 1 phiên khớp -> DRIFT, KHÔNG awaiting",
           v == "DRIFT" and p.get("d1") == D[-k - 1], f"v={v} {p.get('d1')}")
    v, p = det.scan_ticker(pre + post([1000]), evs, 0.003, 3, D[0])
    ck("cụm lệch chạm phiên cuối trước ex-date + 1 phiên khớp -> vẫn AWAITING",
       v == "AWAITING_TRADE" and p.get("d1") == D[-1], f"v={v} {p.get('d1')}")

    # Cổng NHẤT QUÁN (arch-review 2026-10-08, ca VHF thật: −67,30% quan sát vs −19,34% do hệ số chờ).
    v, p = det.scan_ticker(pre, evs, 0.003, 3, D[0])
    ck("awaiting khớp đúng hệ số chờ: dư = 0 (r_obs·Πf/r_pred − 1)",
       v == "AWAITING_TRADE" and abs(p.get("await_resid", 9)) < 1e-9, f"v={v} {p.get('await_resid')}")
    v, p = det.scan_ticker(flat_series(D, 100, 0.5), evs, 0.003, 3, D[0])
    ck("chữ ký VHF: 0 phiên nhưng lệch KHÔNG giải thích được bằng hệ số chờ -> DRIFT",
       v == "DRIFT" and p.get("n_traded") == 0 and abs(p["await_resid"] + 0.5) < 1e-9,
       f"v={v} n={p.get('n_traded')} du={p.get('await_resid')}")
    ck("chữ ký VHF: chứng từ ghi rõ vì sao không phải awaiting",
       any("KHONG giai thich duoc bang he so cho" in n for n in p["notes"]), f"{p['notes']}")
    v, p = det.scan_ticker(flat_series(D, 100, 1.0 * (1 - 0.0029)), evs, 0.003, 3, D[0])
    ck("dư |−0,29%| ≤ dev_tol -> vẫn AWAITING", v == "AWAITING_TRADE", f"v={v} {p.get('await_resid')}")
    v, p = det.scan_ticker(flat_series(D, 100, 1.0 * (1 + 0.0031)), evs, 0.003, 3, D[0])
    ck("dư |+0,31%| > dev_tol -> DRIFT", v == "DRIFT", f"v={v} {p.get('await_resid')}")
    v, p = det.scan_ticker(flat_series(D, 100, 0.5) + post([1, 1, 1]), evs, 0.003, 3, D[0])
    ck("≥3 phiên + lệch không giải thích -> DRIFT, KHÔNG ghi chứng từ 'chua du 3 phien'",
       v == "DRIFT" and not any("KHONG giai thich" in n for n in p["notes"]), f"v={v} {p['notes']}")
    # Hai ex-date đều CHỜ: Π phải gồm MỌI hệ số từ ex_named trở đi, không chỉ hệ số của ex_named.
    evs2 = evs + [ev("2026-08-27", "ISS", "Cổ phiếu thưởng", 0.2)]
    v, p = det.scan_ticker(pre, evs2, 0.003, 3, D[0])
    ck("hai ex-date cùng chờ (1,1×1,2): Π gồm cả hai -> AWAITING, dư 0",
       v == "AWAITING_TRADE" and abs(p.get("await_resid", 9)) < 1e-9 and abs(p["r_pred"] - 1.32) < 1e-9,
       f"v={v} r_pred={p.get('r_pred')} du={p.get('await_resid')}")
    # Che tạm (docstring): thiếu cả hệ số ex cũ A (đã có phiên) lẫn ex mới B (chưa khớp) -> dư ≠ 0 -> DRIFT.
    evs_ab = [ev("2026-07-05", "ISS", "Cổ phiếu thưởng", 0.1), ev(EX, "ISS", "Cổ phiếu thưởng", 0.2)]
    v, p = det.scan_ticker(pre, evs_ab, 0.003, 3, D[0])
    ck("thiếu cả hệ số ex cũ (A) lẫn ex chờ (B) -> DRIFT, không bị awaiting che",
       v == "DRIFT" and p["ex"] == EX, f"v={v} ex={p.get('ex')} du={p.get('await_resid')}")

    # Hợp đồng dòng máy đọc.
    m = det.marker_awaiting("VHF", {"ex": "2026-10-02", "n_traded": 0, "dev": -0.672973}, "none")
    ck("marker_awaiting đúng 6 trường theo thứ tự",
       m.split("|") == ["ADJFACTOR_AWAITING_TRADE", "VHF", "2026-10-02", "0", "none", "-0.672973"],
       m)

    # run_scan: mã đang NẮM thuộc awaiting mang nhãn nắm thật; DRIFT của mã khác byte-identical.
    class A:
        asof = "2026-08-28"; ex0 = "2026-06-01"; ex1 = "2026-08-28"; ex_days = 30
        lookback_days = 120; dev_tol = 0.003; min_run = 3; tickers = None; no_holdings = False

    rows = ([{"tk": "WAIT", **b} for b in pre]
            + [{"tk": "REAL", **b} for b in pre + post([1, 1, 1, 1])])
    saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session)
    try:
        det.cohort_tickers = lambda a, b: ["REAL", "WAIT"]
        det.bq_max_session = lambda: A.asof
        det.price_rows = lambda t, s_, e: rows
        det.held_map = lambda asof, **kw: {"WAIT": "SpaceX,ZaloPay"}
        det.cal.feed_freshness = lambda: {"max_ingested": "2026-08-28 15:00:00",
                                          "max_public": "2026-08-28", "n": "36428"}
        det.cal.events = lambda t, since=None, until=None: [
            dict(e, ticker=tk) for tk in ("REAL", "WAIT") for e in evs]
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = det.run_scan(A)
        out = buf.getvalue()
    finally:
        (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
         det.cal.events, det.bq_max_session) = saved
    lines = out.splitlines()
    aw = [l for l in lines if l.startswith("ADJFACTOR_AWAITING_TRADE|")]
    dr = [l for l in lines if l.startswith("ADJFACTOR_DRIFT|")]
    sc = [l for l in lines if l.startswith("ADJFACTOR_SCAN|")]
    ck("run_scan: mã đang NẮM awaiting -> dòng AWAITING mang nhãn nắm THẬT (không ẩn tiền thật)",
       aw == [f"ADJFACTOR_AWAITING_TRADE|WAIT|{EX}|0|SpaceX,ZaloPay|-0.090909"], f"{aw}")
    ck("run_scan: mã awaiting KHÔNG có dòng DRIFT", not any("|WAIT|" in l for l in dr), f"{dr}")
    _, p_real = det.scan_ticker(pre + post([1, 1, 1, 1]), evs, 0.003, 3, A.ex0)
    ck("run_scan: DRIFT của mã đủ phiên byte-identical với marker_drift (12 trường)",
       dr == [det.marker_drift("REAL", p_real, "none")] and len(dr[0].split("|")) == 12, f"{dr}")
    ck("run_scan: SCAN giữ 7 trường, n_drift = DRIFT THẬT (1), awaiting không cộng vào",
       sc == ["ADJFACTOR_SCAN|2026-08-28|2|1|0|0|0"], f"{sc}")
    # Bằng chứng awaiting phải nằm trong log (dòng máy đọc chỉ mang `dev`) — arch-review 2026-10-08.
    tab = [l for l in lines if l.startswith("WAIT ")]
    ck("run_scan: log có hàng bằng chứng awaiting (r_obs, r_pred, cửa sổ, ex, n_khop, dư)",
       len(tab) == 1 and "1.000000" in tab[0] and "1.100000" in tab[0] and EX in tab[0]
       and "+0.0000%" in tab[0] and "SpaceX,ZaloPay" in tab[0], f"{tab}")
    ck("run_scan: log có chứng từ hệ số của mã awaiting",
       any(l.startswith("   WAIT: ") for l in lines), f"{out[-600:]!r}")
    ck("run_scan: có DRIFT -> rc=10", rc == 10, f"rc={rc}")

    # awaiting-only: rc=11 (không phải 'sạch' 0)
    saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session)
    try:
        det.cohort_tickers = lambda a, b: ["WAIT"]
        det.bq_max_session = lambda: A.asof
        det.price_rows = lambda t, s_, e: [{"tk": "WAIT", **b} for b in pre]
        # `{}` chứ không phải một mã nắm khác: held_map thêm mã nắm NGOÀI cohort vào universe, mà mã
        # không có giá đó thành NODATA ⇒ rc=11 vì lý do KHÁC (mutation D12 từng sống đúng vì khe này).
        det.held_map = lambda asof, **kw: {}
        det.cal.feed_freshness = lambda: {"max_ingested": "2026-08-28 15:00:00",
                                          "max_public": "2026-08-28", "n": "36428"}
        det.cal.events = lambda t, since=None, until=None: [dict(e, ticker="WAIT") for e in evs]
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = det.run_scan(A)
        out = buf.getvalue()
    finally:
        (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
         det.cal.events, det.bq_max_session) = saved
    ck("fixture awaiting-only THUẦN: không DRIFT/UNCOMP/NODATA, SCAN 1|0|0|0|0",
       "ADJFACTOR_SCAN|2026-08-28|1|0|0|0|0" in out.splitlines(), f"{out[-400:]!r}")
    ck("chỉ có awaiting (feed FRESH) -> rc=11, KHÔNG phải 0", rc == 11, f"rc={rc}")
    ck("awaiting mã không nắm mang nhãn `none`",
       f"ADJFACTOR_AWAITING_TRADE|WAIT|{EX}|0|none|-0.090909" in out.splitlines())


AW_FREE = "ADJFACTOR_AWAITING_TRADE|VHF|2026-10-02|0|none|-0.672973"
AW_FREE2 = "ADJFACTOR_AWAITING_TRADE|PIS|2026-10-02|2|none|-0.091304"
AW_HELD = "ADJFACTOR_AWAITING_TRADE|DRX|2026-09-22|1|SpaceX,ZaloPay|-0.007002"
AW_UNK = "ADJFACTOR_AWAITING_TRADE|UNK|2026-09-22|0|unknown|-0.050000"
AW_SKIP = "ADJFACTOR_AWAITING_TRADE|SKP|2026-09-22|0|skipped|-0.050000"
DRIFT_VHF = ("ADJFACTOR_DRIFT|VHF|2026-10-02|0.405405|1.239669|-0.672973|8|2026-06-09"
             "|2026-06-18|vendor_missing|none|0")


def t_alert_awaiting(tz_label, env_tz):
    print(f"\n[16] alert.sh — AWAITING_TRADE  (TZ: {tz_label})")
    tail = "\n".join([FEED_FRESH, SCAN]) + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        state = os.path.join(tmp, "state", "adjfactor_drift_alerted.json")
        notify = os.path.join(sink, "notify.txt")

        # (a) chỉ awaiting của mã KHÔNG nắm + feed FRESH -> bus có, Discord KHÔNG.
        r = _run_alert(tmp, tgt, "\n".join([AW_FREE, AW_FREE2]) + "\n" + tail, env_tz)
        ck(f"[{tz_label}] awaiting-only (không nắm) -> KHÔNG gửi Discord, rc=0",
           r.returncode == 0 and not os.path.exists(notify), f"rc={r.returncode} {r.stderr[-300:]!r}")
        busf = os.path.join(sink, "bus.jsonl")
        bus = [json.loads(l) for l in open(busf) if l.strip()] if os.path.exists(busf) else []
        ck(f"[{tz_label}] awaiting-only vẫn ghi bus với ĐỦ danh sách",
           len(bus) == 1 and bus[0].get("awaiting_trade") == "2"
           and bus[0].get("awaiting_trade_markers") == [AW_FREE, AW_FREE2], f"{bus}")
        ck(f"[{tz_label}] awaiting KHÔNG sinh khoá de-dup cho mã không nắm",
           not os.path.exists(state) or json.load(open(state)) == {},
           f"{open(state).read() if os.path.exists(state) else None}")

        # (b) awaiting + DRIFT thật -> Discord; awaiting gộp MỘT dòng info, không vào TODO.
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, AW_FREE, AW_FREE2]) + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] DRIFT thật + awaiting -> có gửi Discord", r.returncode == 10 and msg,
           f"rc={r.returncode} {r.stderr[-300:]!r}")
        info = [l for l in msg.splitlines() if "Chờ giao dịch lại" in l]
        ck(f"[{tz_label}] awaiting gộp đúng MỘT dòng info chứa cả 2 mã",
           len(info) == 1 and "VHF" in info[0] and "PIS" in info[0], f"{info}")
        todo = msg.split("**Việc cần làm:**", 1)[-1].split("_Quét", 1)[0]
        ck(f"[{tz_label}] awaiting KHÔNG vào 'Việc cần làm'", "VHF" not in todo and "PIS" not in todo,
           f"{todo!r}")
        ck(f"[{tz_label}] awaiting KHÔNG thành dòng lệch '• **VHF**'", "• **VHF**" not in msg)
        ck(f"[{tz_label}] footer đếm awaiting riêng", "2 chờ giao dịch lại" in msg)
        ck(f"[{tz_label}] state chỉ có khoá DRIFT, không có khoá awaiting",
           sorted(json.load(open(state))) == ["FPT|2026-09-21"], f"{open(state).read()}")
        os.remove(notify)

        # (c) DRIFT đã de-dup + awaiting KHÔNG phá de-dup.
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, AW_FREE]) + "\n" + tail, env_tz)
        ck(f"[{tz_label}] DRIFT đã cảnh báo + awaiting -> KHÔNG gửi lại (de-dup còn nguyên)",
           r.returncode == 10 and not os.path.exists(notify), f"rc={r.returncode} {r.stderr[-300:]!r}")

        # (d) chỉ awaiting, KHÔNG có mã nào nắm, nhưng awaiting không chứa Winston dù có Discord vì feed.
        stale_tail = "\n".join([FEED_STALE, SCAN]) + "\n"
        r = _run_alert(tmp, tgt, AW_FREE + "\n" + stale_tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] awaiting-only + feed STALE -> VẪN gửi (feed là cảnh báo riêng)",
           r.returncode == 10 and "KHÔNG TƯƠI" in msg, f"rc={r.returncode}")
        ck(f"[{tz_label}] awaiting KHÔNG giao 'vendor thiếu hệ số' cho Winston",
           "Vendor thiếu hệ số điều chỉnh" not in msg)
        os.remove(notify)

        # (e) awaiting + uncomputable của mã nắm -> gửi (điều kiện quiet chỉ dành cho awaiting thuần).
        r = _run_alert(tmp, tgt, "\n".join([AW_FREE, UNCOMP_HELD]) + "\n" + tail, env_tz)
        ck(f"[{tz_label}] awaiting + uncomputable mã nắm -> có gửi Discord",
           r.returncode == 10 and os.path.exists(notify), f"rc={r.returncode}")
        if os.path.exists(notify):
            os.remove(notify)

    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        state = os.path.join(tmp, "state", "adjfactor_drift_alerted.json")
        notify = os.path.join(sink, "notify.txt")
        tail = "\n".join([FEED_FRESH, SCAN]) + "\n"

        # (f) mã ĐANG NẮM thuộc awaiting -> nêu tên + nhãn LIVE trên Discord, không Winston, de-dup.
        r = _run_alert(tmp, tgt, AW_HELD + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] awaiting mã ĐANG NẮM -> Discord nêu tên + nhãn LIVE",
           r.returncode == 10 and "DRX" in msg and "ĐANG NẮM LIVE: SpaceX,ZaloPay" in msg,
           f"rc={r.returncode} {msg[:300]!r}")
        ck(f"[{tz_label}] awaiting mã nắm KHÔNG giao Winston", "Winston" not in msg, f"{msg!r}")
        ck(f"[{tz_label}] awaiting mã nắm ghi khoá RIÊNG `mã|ex|awaiting_trade`",
           sorted(json.load(open(state))) == ["DRX|2026-09-22|awaiting_trade"],
           f"{open(state).read()}")
        os.remove(notify)
        r = _run_alert(tmp, tgt, AW_HELD + "\n" + tail, env_tz)
        ck(f"[{tz_label}] awaiting mã nắm lượt 2 -> de-dup, KHÔNG gửi lại",
           not os.path.exists(notify), f"rc={r.returncode}")

        # (g) held=unknown cũng phải nêu tên (có thể là tiền thật).
        r = _run_alert(tmp, tgt, AW_UNK + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] awaiting held=unknown -> nêu tên + 'KHÔNG TRA ĐƯỢC vị thế'",
           "UNK" in msg and "KHÔNG TRA ĐƯỢC vị thế" in msg, f"{msg[:300]!r}")
        if os.path.exists(notify):
            os.remove(notify)

        # (h) yêu cầu #3: mã giao dịch lại ≥3 phiên mà vẫn lệch -> DRIFT báo như MỚI, kể cả khi
        # state còn khoá DRIFT CŨ của nó (đo thật: VHF|2026-10-02 = 2026-10-06 trong state live).
        st = json.load(open(state))
        today = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                               capture_output=True, text=True).stdout.strip()
        st["VHF|2026-10-02"] = today
        json.dump(st, open(state, "w"))
        r = _run_alert(tmp, tgt, AW_FREE + "\n" + tail, env_tz, args=("1234", "--dry-run"))
        ck(f"[{tz_label}] --dry-run KHÔNG xoá khoá cũ",
           "VHF|2026-10-02" in json.load(open(state)), f"{open(state).read()}")
        r = _run_alert(tmp, tgt, AW_FREE + "\n" + tail, env_tz)
        ck(f"[{tz_label}] lượt awaiting XOÁ khoá DRIFT cũ `VHF|ex` (không gửi Discord)",
           "VHF|2026-10-02" not in json.load(open(state)) and not os.path.exists(notify),
           f"rc={r.returncode} {open(state).read()}")
        ck(f"[{tz_label}] xoá khoá awaiting KHÔNG đụng khoá khác",
           "DRX|2026-09-22|awaiting_trade" in json.load(open(state)), f"{open(state).read()}")
        r = _run_alert(tmp, tgt, DRIFT_VHF + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] awaiting -> DRIFT (≥3 phiên) báo như mã MỚI, không bị khoá cũ chặn",
           r.returncode == 10 and "• **VHF**" in msg and "Winston" in msg,
           f"rc={r.returncode} {r.stderr[-300:]!r}")

    # arch-review 2026-10-08: held=skipped, nhánh im lặng có UNCOMP/NODATA không nắm, tiêu đề khi chỉ
    # có awaiting mã nắm.
    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        notify = os.path.join(sink, "notify.txt")
        tail = "\n".join([FEED_FRESH, SCAN]) + "\n"

        # (i) held=skipped (`--no-holdings`) KHÔNG phải khẳng định vị thế: không nêu như mã nắm.
        r = _run_alert(tmp, tgt, AW_SKIP + "\n" + tail, env_tz)
        ck(f"[{tz_label}] awaiting held=skipped một mình -> im lặng như mã không nắm, rc=0",
           r.returncode == 0 and not os.path.exists(notify), f"rc={r.returncode} {r.stderr[-300:]!r}")
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, AW_SKIP]) + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] awaiting held=skipped KHÔNG in 'ĐANG NẮM LIVE: skipped' / không in đậm",
           "SKP (ex" in msg and "skipped" not in msg and "**SKP**" not in msg, f"{msg[-900:]!r}")
        ck(f"[{tz_label}] DRIFT thật + awaiting -> giữ tiêu đề '⚠️ LỆCH'",
           msg.startswith("⚠️ **LỆCH HỆ SỐ"), f"{msg[:120]!r}")
        if os.path.exists(notify):
            os.remove(notify)

        # (j) awaiting + UNCOMP/NODATA của mã KHÔNG nắm -> nhánh de-dup (rc=10), không phải im lặng rc=0.
        for lbl, extra in (("UNCOMPUTABLE", UNCOMP_FREE), ("NODATA", NODATA_FREE)):
            r = _run_alert(tmp, tgt, "\n".join([AW_FREE, extra]) + "\n" + tail, env_tz)
            ck(f"[{tz_label}] awaiting + {lbl} không nắm -> rc=10 qua nhánh de-dup, KHÔNG Discord",
               r.returncode == 10 and not os.path.exists(notify) and "(de-dup)" in r.stderr,
               f"rc={r.returncode} {r.stderr[-300:]!r}")

        # (k) lượt gửi CHỈ vì awaiting mã nắm: tiêu đề ℹ️, không '⚠️ LỆCH … ≥3 phiên', TODO không trống.
        r = _run_alert(tmp, tgt, AW_HELD + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        todo = msg.split("**Việc cần làm:**", 1)[-1].split("_Quét", 1)[0]
        ck(f"[{tz_label}] chỉ awaiting mã nắm -> tiêu đề ℹ️ CHỜ GIAO DỊCH LẠI, không '⚠️ LỆCH'",
           msg.startswith("ℹ️ **CHỜ GIAO DỊCH LẠI") and "⚠️ **LỆCH" not in msg, f"{msg[:200]!r}")
        ck(f"[{tz_label}] chỉ awaiting mã nắm -> 'Việc cần làm' nói rõ 'không có', không trống",
           todo.strip().startswith("không có"), f"{todo!r}")
        if os.path.exists(notify):
            os.remove(notify)

        # (l) NODATA mã nắm (TODO cũng rỗng) KHÔNG được đổi sang tiêu đề awaiting.
        r = _run_alert(tmp, tgt, "\n".join([NODATA_FREE.replace("|none", "|SpaceX"), AW_FREE])
                       + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] NODATA mã nắm + awaiting không nắm -> vẫn tiêu đề '⚠️ LỆCH', không ℹ️",
           msg.startswith("⚠️ **LỆCH HỆ SỐ"), f"{msg[:200]!r}")
        if os.path.exists(notify):
            os.remove(notify)

        # (m) awaiting mã nắm MỚI + MỘT cảnh báo thật khác ⇒ tiêu đề '⚠️ LỆCH' (mỗi điều kiện của nhánh
        # ℹ️ phải tự đứng được — mỗi ca dùng một mã awaiting nắm MỚI để N_AWAIT_HELD_NEW > 0).
        for i, (lbl, extra, tl) in enumerate((
                ("DRIFT mới", DRIFT_HELD, tail),
                ("UNCOMPUTABLE mã nắm", UNCOMP_HELD, tail),
                ("NODATA mã nắm", NODATA_HELD, tail),
                ("feed STALE", "", "\n".join([FEED_STALE, SCAN]) + "\n"))):
            aw = f"ADJFACTOR_AWAITING_TRADE|HW{i}|2026-09-22|0|SpaceX|-0.050000"
            r = _run_alert(tmp, tgt, "\n".join(x for x in (extra, aw) if x) + "\n" + tl, env_tz)
            msg = open(notify).read() if os.path.exists(notify) else ""
            ck(f"[{tz_label}] awaiting mã nắm mới + {lbl} -> tiêu đề '⚠️ LỆCH', không ℹ️",
               r.returncode == 10 and msg.startswith("⚠️ **LỆCH HỆ SỐ") and f"HW{i}" in msg,
               f"rc={r.returncode} {msg[:200]!r}")
            if os.path.exists(notify):
                os.remove(notify)

    # arch-review vòng 2: (n) DRIFT đã de-dup + awaiting mã nắm MỚI; (o) xoá khoá DRIFT cũ của mã NẮM;
    # (p) log nhánh awaiting-only không khẳng định "không mã nào nắm" khi mã nắm chỉ bị de-dup.
    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        state = os.path.join(tmp, "state", "adjfactor_drift_alerted.json")
        notify = os.path.join(sink, "notify.txt")
        tail = "\n".join([FEED_FRESH, SCAN]) + "\n"
        _run_alert(tmp, tgt, DRIFT_FREE + "\n" + tail, env_tz)          # FPT báo lần đầu -> de-dup
        if os.path.exists(notify):
            os.remove(notify)
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, AW_HELD]) + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] DRIFT đã de-dup + awaiting mã nắm mới -> KHÔNG nói 'Không có lệch thật'",
           r.returncode == 10 and msg.startswith("ℹ️") and "Không có lệch thật" not in msg
           and "1 lệch đã báo" in msg and "VẪN MỞ" in msg, f"rc={r.returncode} {msg[:300]!r}")
        todo = msg.split("**Việc cần làm:**", 1)[-1].split("_Quét", 1)[0]
        ck(f"[{tz_label}] DRIFT đã de-dup + awaiting mã nắm -> TODO nói 'không có việc MỚI'",
           todo.strip().startswith("không có việc MỚI"), f"{todo!r}")
        if os.path.exists(notify):
            os.remove(notify)

        today = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                               capture_output=True, text=True).stdout.strip()
        st = json.load(open(state))
        st["DRX|2026-09-22"] = today              # khoá DRIFT CŨ của chính mã nắm đang awaiting
        json.dump(st, open(state, "w"))
        r = _run_alert(tmp, tgt, AW_HELD + "\n" + tail, env_tz)    # khoá awaiting còn tươi -> im
        ck(f"[{tz_label}] awaiting mã NẮM: XOÁ khoá DRIFT cũ `DRX|ex` (đường tiền thật)",
           "DRX|2026-09-22" not in json.load(open(state))
           and "DRX|2026-09-22|awaiting_trade" in json.load(open(state)),
           f"rc={r.returncode} {open(state).read()}")
        ck(f"[{tz_label}] awaiting-only, mã nắm đã de-dup -> rc=0, log KHÔNG nói 'khong ma nao co the dang nam'",
           r.returncode == 0 and not os.path.exists(notify)
           and "khong ma nao co the dang nam" not in r.stderr and "da bao trong" in r.stderr,
           f"rc={r.returncode} {r.stderr[-300:]!r}")

        # vòng 2 B2: THIẾU dòng SCAN (N_DRIFT='?') + DRIFT đã de-dup + awaiting mã nắm MỚI -> vẫn KHÔNG
        # được nói 'Không có lệch thật' (điều kiện phải đọc từ chính dòng DRIFT, không từ SCAN).
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, AW_HELD.replace("DRX", "NSC"), FEED_FRESH])
                       + "\n", env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] thiếu SCAN + DRIFT de-dup + awaiting nắm -> KHÔNG nói 'Không có lệch thật' (B2)",
           msg.startswith("ℹ️") and "Không có lệch thật" not in msg and "1 lệch đã báo" in msg,
           f"rc={r.returncode} {msg[:300]!r}")
        if os.path.exists(notify):
            os.remove(notify)

        # vòng 2 B1: XOÁ khoá DRIFT cũ thất bại (state/ read-only) -> KHÔNG nói 'Discord DA gui roi'
        # (chưa gửi gì), trích lỗi thật, và ÉP gửi Discord nêu khoá còn sót (fail-open phía gửi).
        st = json.load(open(state))
        st["VHF|2026-10-02"] = today
        json.dump(st, open(state, "w"))
        sdir = os.path.dirname(state)
        for f in os.listdir(sdir):
            if f.endswith(".lock"):
                os.remove(os.path.join(sdir, f))
        mode = os.stat(sdir).st_mode
        os.chmod(sdir, 0o500)
        try:
            r = _run_alert(tmp, tgt, AW_FREE + "\n" + tail, env_tz)
        finally:
            os.chmod(sdir, mode)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] xoá khoá hỏng -> KHÔNG nói 'Discord DA gui roi', trích lỗi thật (B1)",
           "DA gui roi" not in r.stderr and "KHONG xoa duoc khoa DRIFT cu VHF|2026-10-02" in r.stderr
           and "Permission denied" in r.stderr, f"{r.stderr[-500:]!r}")
        ck(f"[{tz_label}] xoá khoá hỏng -> ÉP gửi Discord nêu khoá sót, rc=10 (B1)",
           r.returncode == 10 and "STATE DE-DUP KHÔNG XOÁ ĐƯỢC" in msg and "VHF|2026-10-02" in msg,
           f"rc={r.returncode} {msg[:300]!r}")
        ck(f"[{tz_label}] xoá khoá hỏng -> khoá VẪN còn (test thật sự chạm đường lỗi)",
           "VHF|2026-10-02" in json.load(open(state)), f"{open(state).read()}")



# ----------------------- 17. PRICE_FIELD_MISMATCH — LỆCH TRƯỜNG Price (job Taylor_20261008_080048)

REAL_1007 = {   # (d, Price, Close, Low, High, Volume) — tav2_bq.ticker thật, kéo 2026-10-08
    "DRI": [
        ("2026-09-03", 14300, 13330, 13140, 13420, 446520),
        ("2026-09-04", 14200, 13240, 13140, 13420, 350272),
        ("2026-09-07", 14200, 13240, 13240, 13420, 633939),
        ("2026-09-08", 14600, 13700, 13240, 13800, 1105628),
        ("2026-09-09", 14900, 13890, 13700, 14170, 1125946),
        ("2026-09-10", 14600, 13700, 13520, 13980, 859292),
        ("2026-09-11", 14400, 13520, 13330, 13700, 677165),
        ("2026-09-14", 14100, 13240, 13050, 13420, 785501),
        ("2026-09-15", 14400, 13420, 13050, 13420, 735869),
        ("2026-09-16", 14900, 13890, 13240, 14080, 2360195),
        ("2026-09-17", 14800, 13800, 13610, 13890, 425937),
        ("2026-09-18", 14800, 13800, 13700, 13890, 743050),
        ("2026-09-21", 14800, 13890, 13610, 13980, 1028231),
        ("2026-09-22", 14000, 14000, 13800, 14600, 417345),
        ("2026-09-23", 14500, 14500, 13900, 14500, 1824023),
        ("2026-09-24", 14800, 14800, 14500, 15100, 1515170),
        ("2026-09-25", 15000, 15100, 14800, 15700, 2804805),
        ("2026-09-28", 15000, 15000, 14700, 15200, 917701),
        ("2026-09-29", 16000, 16000, 14900, 16100, 2907544),
        ("2026-09-30", 15600, 15700, 15500, 16400, 1701325),
        ("2026-10-01", 15500, 15500, 15300, 16100, 1767331),
        ("2026-10-02", 16200, 16200, 15600, 16700, 1976061),
        ("2026-10-05", 16700, 16700, 16200, 16800, 2322100),
        ("2026-10-06", 16300, 16400, 16000, 16800, 1518800),
        ("2026-10-07", 16000, 16000, 15800, 16700, 2569000),
    ],
    "DVN": [
        ("2026-06-15", 20800, 19660, 19660, 19750, 3800),
        ("2026-06-16", 20800, 19660, 19570, 19660, 14210),
        ("2026-06-17", 20800, 19660, 19470, 19660, 21986),
        ("2026-06-18", 20700, 19570, 19380, 19660, 75587),
        ("2026-06-19", 20500, 19470, 19280, 19570, 39040),
        ("2026-06-22", 20400, 19470, 19280, 19470, 30134),
        ("2026-06-23", 20400, 19380, 19280, 19470, 2355),
        ("2026-06-24", 20400, 19280, 19090, 19380, 21720),
        ("2026-06-25", 20200, 19090, 19090, 19280, 9000),
        ("2026-06-26", 20200, 19090, 18810, 19190, 128886),
        ("2026-06-29", 20000, 18900, 18900, 19190, 4243),
        ("2026-06-30", 20200, 19090, 19000, 19090, 5801),
        ("2026-09-08", 18300, 17300, 17110, 17300, 16900),
        ("2026-09-09", 18100, 17110, 17110, 17300, 3100),
        ("2026-09-10", 18100, 17110, 17110, 17300, 8200),
        ("2026-09-11", 17200, 17200, 17200, 17400, 12700),
        ("2026-09-14", 17100, 17100, 17000, 17300, 4700),
        ("2026-09-15", 17500, 17500, 17200, 17500, 8431),
        ("2026-09-16", 17000, 17000, 17000, 17300, 5819),
        ("2026-09-17", 17100, 17300, 17000, 17600, 79412),
        ("2026-09-18", 16900, 17000, 16500, 17300, 8532),
    ],
    "SHC": [
        ("2026-06-24", 12000, 11430, 11430, 11430, 0), ("2026-06-25", 12000, 11430, 11430, 11430, 0),
        ("2026-06-26", 12000, 11430, 11430, 11430, 49),
        ("2026-06-29", 10900, 10380, 10380, 13140, 215), ("2026-06-30", 10900, 11810, 11810, 11810, 0),
        ("2026-07-01", 10900, 11810, 11810, 11810, 12), ("2026-07-02", 10900, 11810, 11810, 11810, 6),
        ("2026-07-03", 10900, 11810, 11810, 11810, 0), ("2026-07-06", 10900, 11810, 11810, 11810, 13),
        ("2026-07-07", 10900, 11810, 11810, 11810, 0), ("2026-07-08", 10900, 11810, 11810, 11810, 0),
        ("2026-07-09", 10900, 11810, 11810, 11810, 10),
        ("2026-07-10", 12400, 11810, 11810, 11810, 100), ("2026-07-13", 12400, 11810, 11810, 11810, 0),
        ("2026-07-14", 12400, 11810, 11810, 11810, 0), ("2026-07-15", 12400, 11810, 11810, 11810, 0),
        ("2026-09-03", 10200, 9710, 9710, 9710, 0), ("2026-09-04", 10500, 10000, 10000, 10000, 1300),
        ("2026-09-07", 10500, 10000, 10000, 10000, 0), ("2026-09-08", 10500, 10000, 10000, 10000, 0),
        ("2026-09-09", 10000, 10000, 10000, 10000, 100), ("2026-09-10", 10000, 10000, 10000, 10000, 0),
        ("2026-09-11", 10000, 10000, 10000, 10000, 0),
    ],
    "CC1": [
        ("2026-07-29", 38900, 37050, 37050, 37050, 125),
        ("2026-07-30", 38000, 36190, 36190, 36670, 6225),
        ("2026-07-31", 38000, 36190, 36190, 36190, 1225),
        ("2026-08-03", 37000, 35240, 35240, 35240, 101),
        ("2026-08-04", 37000, 35240, 35240, 35240, 212),
        ("2026-08-05", 40900, 38950, 34290, 38950, 672),
        ("2026-08-06", 40900, 36190, 36190, 36190, 36), ("2026-08-07", 40900, 36190, 36190, 36190, 26),
        ("2026-08-10", 40900, 36190, 36190, 36190, 6), ("2026-08-11", 38000, 36190, 36190, 36190, 962),
        ("2026-08-12", 38000, 36190, 36190, 36190, 251),
        ("2026-08-13", 38000, 36190, 36190, 36190, 429),
        ("2026-08-14", 37500, 35720, 35720, 35720, 1000),
        ("2026-09-11", 38700, 36860, 36860, 36860, 30), ("2026-09-14", 38700, 36860, 36860, 36860, 3),
        ("2026-09-15", 40100, 40100, 31400, 42000, 1996),
        ("2026-09-16", 38100, 38100, 38100, 38100, 128),
        ("2026-09-17", 38100, 38100, 38100, 38100, 13),
    ],
    "HC1": [
        ("2026-07-01", 13400, 12350, 12350, 12350, 1000),
        ("2026-07-02", 13400, 12350, 12350, 12350, 0), ("2026-07-03", 13400, 12350, 12350, 12350, 0),
        ("2026-07-06", 13400, 12350, 12350, 12350, 0), ("2026-07-07", 13400, 12350, 12350, 12350, 0),
        ("2026-07-08", 13500, 12450, 11980, 12450, 500), ("2026-07-09", 13500, 12080, 12080, 12080, 0),
        ("2026-07-10", 13500, 12080, 12080, 12080, 0), ("2026-07-13", 13500, 12080, 12080, 12080, 0),
        ("2026-07-14", 13500, 12080, 12080, 12080, 0), ("2026-07-15", 13500, 12080, 12080, 12080, 0),
        ("2026-07-16", 13500, 12080, 12080, 12080, 0), ("2026-07-17", 13500, 12080, 12080, 12080, 0),
        ("2026-07-20", 13500, 12080, 12080, 12080, 0), ("2026-07-21", 13500, 12080, 12080, 12080, 0),
        ("2026-07-22", 13000, 11980, 11800, 11980, 1500),
        ("2026-07-23", 13000, 11890, 11890, 11890, 0), ("2026-07-24", 13000, 11890, 11890, 11890, 0),
        ("2026-07-27", 13000, 11890, 11890, 11890, 0), ("2026-07-28", 13000, 11890, 11890, 11890, 0),
        ("2026-07-29", 13000, 11890, 11890, 11890, 0), ("2026-07-30", 13000, 11890, 11890, 11890, 0),
        ("2026-07-31", 13000, 11890, 11890, 11890, 0),
        ("2026-08-03", 12800, 11800, 11800, 11800, 1000),
        ("2026-08-04", 12800, 11800, 11800, 11800, 500), ("2026-08-05", 12800, 11800, 11800, 11800, 0),
        ("2026-08-06", 12800, 11800, 11800, 11800, 0), ("2026-09-17", 12800, 11800, 11800, 11800, 0),
        ("2026-09-18", 12800, 11800, 11800, 11800, 0), ("2026-09-21", 12800, 11800, 11800, 11800, 0),
        ("2026-09-22", 11800, 11800, 11800, 11800, 0), ("2026-09-23", 11800, 11800, 11800, 11800, 0),
        ("2026-09-24", 11500, 11500, 11500, 11500, 500),
    ],
    "VFR": [
        ("2026-06-23", 10000, 9380, 9380, 9380, 0), ("2026-06-24", 10000, 9380, 9380, 9380, 0),
        ("2026-06-25", 10000, 9380, 9380, 9380, 0), ("2026-06-26", 10000, 9380, 9380, 9380, 0),
        ("2026-06-29", 10500, 9840, 9840, 9840, 3000), ("2026-06-30", 10500, 9840, 9840, 9840, 0),
        ("2026-07-01", 11000, 10310, 10310, 10310, 100), ("2026-07-02", 10500, 9840, 9840, 9840, 9001),
        ("2026-07-03", 10500, 9840, 9840, 9840, 0), ("2026-07-06", 10500, 9840, 9840, 9840, 0),
        ("2026-07-07", 10500, 9840, 9840, 9840, 0), ("2026-07-08", 10500, 9840, 9840, 9840, 0),
        ("2026-07-09", 10500, 9840, 9840, 9840, 500), ("2026-07-10", 10500, 9840, 9840, 9840, 0),
        ("2026-07-13", 10500, 9840, 9840, 9840, 0), ("2026-07-14", 10500, 9840, 9840, 9840, 0),
        ("2026-07-15", 10500, 9840, 9840, 9840, 0), ("2026-07-16", 10500, 9840, 9840, 9840, 0),
        ("2026-07-17", 10500, 9840, 9840, 9840, 0), ("2026-07-20", 10500, 9840, 9840, 9840, 0),
        ("2026-07-21", 10500, 9840, 9840, 9840, 1013), ("2026-07-22", 10500, 9840, 9840, 9840, 0),
        ("2026-07-23", 10500, 9840, 9840, 9840, 0), ("2026-07-24", 10000, 9380, 9380, 9380, 600),
        ("2026-07-27", 10000, 9380, 8440, 9380, 3900), ("2026-07-28", 10000, 9190, 9190, 9190, 0),
        ("2026-07-29", 10000, 9190, 9190, 9190, 0), ("2026-07-30", 10000, 9190, 9190, 9190, 27),
        ("2026-07-31", 9800, 9190, 9190, 9190, 100), ("2026-08-03", 9500, 8910, 8910, 9190, 800),
        ("2026-08-04", 9500, 8910, 8910, 8910, 307), ("2026-08-05", 9000, 8440, 8440, 8440, 1000),
        ("2026-08-06", 9000, 8440, 8440, 8440, 0), ("2026-08-07", 9000, 8440, 8440, 8440, 0),
        ("2026-08-10", 9000, 8440, 8440, 8440, 0), ("2026-08-11", 9000, 8440, 8440, 8440, 0),
        ("2026-08-12", 9000, 8440, 8440, 8440, 0), ("2026-09-16", 10300, 9660, 9660, 9660, 1),
        ("2026-09-17", 10300, 9660, 9660, 9660, 100), ("2026-09-18", 10000, 9380, 8620, 9380, 1000),
        ("2026-09-21", 8900, 8900, 8900, 9200, 500), ("2026-09-22", 9000, 9000, 9000, 9000, 0),
        ("2026-09-23", 8600, 8600, 8600, 8900, 1001),
    ],
    "VHF": [
        ("2026-06-09", 1500, 3700, 3700, 3700, 0), ("2026-06-10", 1500, 3700, 3700, 3700, 0),
        ("2026-06-11", 1500, 3700, 3700, 3700, 0), ("2026-06-12", 1500, 3700, 3700, 3700, 0),
        ("2026-06-15", 1500, 3700, 3700, 3700, 0), ("2026-06-16", 1500, 3700, 3700, 3700, 0),
        ("2026-06-17", 1500, 3700, 3700, 3700, 0), ("2026-06-18", 1500, 3700, 3700, 3700, 0),
    ],
    "PBP": [
        ("2026-06-09", 12000, 11020, 11020, 11020, 100),
        ("2026-06-10", 12100, 11110, 11020, 11110, 200),
        ("2026-06-11", 12200, 11200, 11020, 11200, 300),
        ("2026-06-12", 12000, 11020, 10100, 11200, 1000),
        ("2026-06-15", 11900, 10930, 10930, 10930, 200),
        ("2026-06-16", 12200, 11200, 10930, 11200, 7200),
        ("2026-06-17", 12100, 11110, 10380, 11110, 1600),
        ("2026-06-18", 11800, 10840, 10470, 10930, 700),
        ("2026-06-19", 12000, 11020, 10740, 11020, 1300),
        ("2026-09-10", 11700, 10740, 10740, 11750, 300),
        ("2026-09-11", 11000, 10100, 10100, 10100, 300),
        ("2026-09-14", 10300, 10300, 9900, 10500, 2000),
        ("2026-09-15", 10300, 10300, 10300, 10300, 100), ("2026-09-16", 9900, 9900, 9900, 10300, 409),
    ],
}

# Dòng máy đọc THẬT của lượt quét asof 2026-10-07 — bản TRƯỚC thay đổi (baseline) và bản SAU.
REAL_DRIFT_BEFORE = {
    "DRI": "ADJFACTOR_DRIFT|DRI|2026-09-22|1.064955|1.072464|-0.007002|3|2026-09-10|2026-09-14"
           "|vendor_missing|SpaceX,ZaloPay|0",
    "DVN": "ADJFACTOR_DRIFT|DVN|2026-09-11|1.047766|1.058480|-0.010122|3|2026-06-19|2026-06-23"
           "|vendor_missing|none|0",
    "SHC": "ADJFACTOR_DRIFT|SHC|2026-09-09|0.922947|1.050000|-0.121003|8|2026-06-30|2026-07-09"
           "|vendor_missing|none|0",
    "CC1": "ADJFACTOR_DRIFT|CC1|2026-09-15|1.130146|1.050000|0.076330|3|2026-08-06|2026-08-10"
           "|our_table_missing|none|0",
    "HC1": "ADJFACTOR_DRIFT|HC1|2026-09-22|1.117550|1.084746|0.030241|9|2026-07-09|2026-07-21"
           "|our_table_missing|none|0",
    "VFR": "ADJFACTOR_DRIFT|VFR|2026-09-21|1.067073|1.063830|0.003049|16|2026-07-02|2026-07-23"
           "|our_table_missing|none|0",
    "VHF": "ADJFACTOR_DRIFT|VHF|2026-10-02|0.405405|1.239669|-0.672973|8|2026-06-09|2026-06-18"
           "|vendor_missing|none|0",
}
REAL_PFM_AFTER = {
    "DRI": "ADJFACTOR_PRICE_FIELD_MISMATCH|DRI|2026-09-22|1|tick_offset|2026-09-10|2026-09-14"
           "|SpaceX,ZaloPay|-0.007002",
    "DVN": "ADJFACTOR_PRICE_FIELD_MISMATCH|DVN|2026-09-11|1|tick_offset|2026-06-19|2026-06-23"
           "|none|-0.010122",
    "SHC": "ADJFACTOR_PRICE_FIELD_MISMATCH|SHC|2026-09-09|1|stale_price|2026-06-30|2026-07-09"
           "|none|-0.121003",
    "CC1": "ADJFACTOR_PRICE_FIELD_MISMATCH|CC1|2026-09-15|1|stale_price|2026-08-06|2026-08-10"
           "|none|0.076330",
}
REAL_EVENTS = {   # corporate_action thật (event_status executed) của từng mã
    "DRI": [ev("2026-09-22", "DIV", ratio=0.1, dps=1000.0, tk="DRI")],
    "DVN": [ev("2026-09-11", "DIV", ratio=0.1, dps=1000.0, tk="DVN")],
    "SHC": [ev("2026-09-09", "DIV", ratio=0.05, dps=500.0, tk="SHC")],
    "CC1": [ev("2026-09-15", "ISS", "Trả Cổ tức bằng Cổ phiếu", 0.05, tk="CC1")],
    "HC1": [ev("2026-09-22", "DIV", ratio=0.1, dps=1000.0, tk="HC1")],
    "VFR": [ev("2026-09-21", "DIV", ratio=0.06, dps=600.0, tk="VFR")],
    "VHF": [ev("2026-10-02", "DIV", ratio=0.029, dps=290.0, tk="VHF")],
    "PBP": [ev("2026-09-14", "ISS", "Trả Cổ tức bằng Cổ phiếu", 0.085, tk="PBP")],
}
REAL_HELD = {"DRI": "SpaceX,ZaloPay"}


def _real(tk, mut=None):
    s = [{"d": d, "price": float(p), "close": float(c), "lo": float(lo), "hi": float(hi),
          "vol": float(v)} for d, p, c, lo, hi, v in REAL_1007[tk]]
    for d, k, val in (mut or []):
        next(b for b in s if b["d"] == d)[k] = val
    return s


def _tick(exchange, tk="XXX"):
    from trading_bot import vn_market
    return lambda price: vn_market.tick_size(price, tk, exchange)


def _scan_real(tk, tick_fn="UPCOM", mut=None):
    """Quét fixture thật với ĐÚNG ngưỡng production; rìa đánh giá = phiên đầu của fixture (PBP/VHF:
    2026-06-09 = rìa cửa sổ 120 ngày thật)."""
    s = _real(tk, mut)
    tf = _tick(tick_fn, tk) if isinstance(tick_fn, str) else tick_fn
    return det.scan_ticker(s, REAL_EVENTS[tk], det.DEV_TOL, det.MIN_RUN, s[0]["d"], tick_fn=tf)


def _marker(tk, v, p):
    h = REAL_HELD.get(tk, "none")
    return det.marker_drift(tk, p, h) if v == "DRIFT" else (
        det.marker_price_field(tk, p, h) if v == "PRICE_FIELD_MISMATCH" else v)


def _pf(deltas, base=20000, step=100, n=30, rp=1.1, exchange="UPCOM", ex="2026-08-20",
        extra_events=(), closes=None):
    """Chuỗi tổng hợp: vendor ĐÚNG hệ số rp (Close = P/rp), rồi CỘNG `deltas[i]` đồng vào `Price` của
    phiên i (lỗi trường Price). Giá dao động trên lưới `step` để tỉ lệ ≠ hằng số."""
    ds = D[:n]
    prices = [base + step * ((i * 3) % 7) for i in range(n)]
    s = []
    for i, d in enumerate(ds):
        close = (closes[i] if closes else prices[i] / rp)
        b = _vbar(d, prices[i] + deltas.get(i, 0), close, 5000)
        s.append(b)
    evs = [ev(ex, "ISS", "Cổ phiếu thưởng", round(rp - 1, 10))] + list(extra_events)
    return s, evs, _tick(exchange)


def _scan_at(s, evs, w0, tf, dev_tol=None, min_run=None, until=None):
    """scan_ticker y như `run_scan` ở asof có win0 = `w0`: chuỗi nạp từ load0 = w0 − CUM_PAD_DAYS tới
    `until` (= asof; None = hết fixture), sự kiện (w0, until] vào đường hệ số, sự kiện điều chỉnh giá
    (load0, w0] chỉ thành NGÀY trong `pre_ex` — sự kiện/phiên SAU asof không bao giờ được thấy."""
    load0 = (date.fromisoformat(w0) - timedelta(days=det.CUM_PAD_DAYS)).isoformat()
    hi = until or "9999-12-31"
    s = [b for b in s if load0 <= b["d"] <= hi]
    ev_in = [e for e in evs if w0 < e["exright_date"] <= hi]
    pre = {e["exright_date"] for e in evs
           if load0 < e["exright_date"] <= w0 and det.cal.is_price_adjusting(e)}
    return det.scan_ticker(s, ev_in, dev_tol or det.DEV_TOL, min_run or det.MIN_RUN, w0, tick_fn=tf,
                           pre_ex=pre)


def t_price_field_window():
    """Vòng 3 B1 + toàn bộ ca biên của việc chọn láng giềng quanh một cụm: phán quyết KHÔNG được đổi theo
    vị trí win0; lệch hệ số thật vẫn DRIFT ở MỌI vị trí."""
    print("\n[17b] PRICE_FIELD_MISMATCH — cửa sổ trượt qua cụm (B1/NB1/NB2/NB3 + ca biên)")

    # (1) B1 thật: SHC cụm 06-30..07-09 (8 phiên stale). win0 GIỮA cụm từng ra DRIFT giả tất định.
    s_shc = _real("SHC")
    cl = [b["d"] for b in s_shc if "2026-06-30" <= b["d"] <= "2026-07-09"]
    for w0 in cl[1:-2]:
        v, p = _scan_at(s_shc, REAL_EVENTS["SHC"], w0, _tick("UPCOM", "SHC"))
        ck(f"B1 thật SHC: win0 = {w0} (GIỮA cụm) -> PRICE_FIELD_MISMATCH stale_price, cụm nối lùi về "
           f"đủ 06-30..07-09", v == "PRICE_FIELD_MISMATCH" and p["pfm_rules"] == "stale_price"
           and any("PRICE_FIELD_MISMATCH 2026-06-30..2026-07-09:" in n for n in p["notes"]),
           f"v={v} {p.get('notes', [])[-1:]}")
        ck(f"NB1 SHC win0 = {w0}: marker nêu span ĐẦY ĐỦ 06-30..07-09 như chứng từ (không bị cửa sổ cắt)",
           p.get("d0") == "2026-06-30" and p.get("d1") == "2026-07-09"
           and "|2026-06-30|2026-07-09|" in det.marker_price_field("SHC", p, "none"),
           f"d0={p.get('d0')} d1={p.get('d1')}")

    # (2) Trượt win0 qua TỪNG phiên của fixture thật (đúng cách run_scan chia sự kiện) ⇒ 0 DRIFT giả.
    for tk in ("DRI", "DVN", "SHC", "CC1"):
        s_ = _real(tk)
        bad = []
        for b in s_:
            v, p = _scan_at(s_, REAL_EVENTS[tk], b["d"], _tick("UPCOM", tk))
            if v == "DRIFT":
                bad.append(b["d"])
        ck(f"trượt win0 qua {len(s_)} phiên fixture thật {tk} -> 0 DRIFT", not bad, f"DRIFT tại {bad}")
    # Đối chứng ÂM thật: HC1/VFR (lệch hệ số thật) vẫn DRIFT khi win0 = phiên đầu fixture.
    for tk in ("HC1", "VFR"):
        s_ = _real(tk)
        v, _p = _scan_at(s_, REAL_EVENTS[tk], s_[0]["d"], _tick("UPCOM", tk))
        ck(f"ÂM thật {tk}: vẫn DRIFT qua đường _scan_at", v == "DRIFT", f"v={v}")

    # (3) Tổng hợp: cụm 1-bước 6 phiên D[8..13]; win0 trượt D[0..16].
    s_, evs_, tf_ = _pf({i: -100 for i in range(8, 14)})
    got = {}
    for w in range(0, 17):
        v, p = det.scan_ticker(s_, evs_, 0.003, 3, D[w], tick_fn=tf_, pre_ex=set())
        got[w] = v
        exp = "PRICE_FIELD_MISMATCH" if w <= 11 else "AGREE"
        span_ok = v != "PRICE_FIELD_MISMATCH" or any(f"PRICE_FIELD_MISMATCH {D[8]}..{D[13]}:" in n
                                                     for n in p["notes"])
        ck(f"cụm 6 phiên D[8..13], win0 = D[{w}] (trong cửa sổ {max(0, 14 - max(w, 8))} phiên) -> {exp}"
           f"{', cụm đủ D[8..13]' if exp != 'AGREE' else ''}", v == exp and span_ok, f"v={v}")
    # Cụm dài hơn chuỗi nạp lùi được: lead chỉ có 2 phiên trước cửa sổ, cả hai thuộc cụm ⇒ DRIFT.
    v, p = det.scan_ticker(s_[8:], evs_, 0.003, 3, D[10], tick_fn=tf_, pre_ex=set())
    ck("cụm lùi quá đầu chuỗi nạp (không thấy phiên khớp) -> DRIFT fail-closed, chứng từ nói vì sao",
       v == "DRIFT" and any("het chuoi nap" in n and f"{D[8]}..{D[9]} van lech" in n for n in p["notes"]),
       f"v={v} {p.get('notes', [])[-1:]}")
    # Phần nối trước cửa sổ phải đạt CÙNG luật: phiên D[8] lệch 3 bước ⇒ cả cụm DRIFT ở MỌI win0.
    s3, evs3, tf3 = _pf({**{i: -100 for i in range(8, 14)}, 8: -300})
    for w in (0, 9, 10, 11):
        v, _p = det.scan_ticker(s3, evs3, 0.003, 3, D[w], tick_fn=tf3, pre_ex=set())
        ck(f"phiên đầu cụm 3 bước, win0 = D[{w}] -> DRIFT (phần nối lùi cũng phải đạt luật)",
           v == "DRIFT", f"v={v}")
    # Láng giềng trái thật (sau khi lùi) chỉ khớp SÁT ngưỡng ⇒ DRIFT, không phụ thuộc win0.
    s4, evs4, tf4 = _pf({i: -100 for i in range(8, 14)})
    s4[7]["price"] = s4[7]["close"] * 1.1 * 1.0025
    for w in (0, 9, 11):
        v, p = det.scan_ticker(s4, evs4, 0.003, 3, D[w], tick_fn=tf4, pre_ex=set())
        ck(f"láng giềng trái D[7] +0,25% (khớp SÁT), win0 = D[{w}] -> DRIFT",
           v == "DRIFT" and any("SAT nguong" in n and D[7] in n for n in p["notes"]), f"v={v}")

    # (4) NB1: cụm GIỮA cửa sổ — láng giềng là phiên trong cửa sổ, KHÔNG phải phiên trước cửa sổ.
    s5, evs5, tf5 = _pf({10: -100, 11: -100, 12: -100})
    s5[9]["price"] = s5[9]["close"] * 1.1 * 1.0025
    v, p = det.scan_ticker(s5, evs5, 0.003, 3, D[5], tick_fn=tf5, pre_ex=set())
    ck("NB1: cụm giữa cửa sổ, phiên trước cửa sổ D[4] khớp tuyệt đối nhưng láng giềng thật D[9] +0,25% "
       "-> DRIFT", v == "DRIFT" and any("SAT nguong" in n and D[9] in n for n in p["notes"]), f"v={v}")

    # (5) Ex-date sát cụm. SAU: cụm bắt đầu ĐÚNG phiên ex-date (vendor đúng ở cả hai đoạn) ⇒ khác đoạn.
    rp6 = [1.1 * 1.05 if i < 10 else 1.1 for i in range(30)]
    s6, evs6, tf6 = _pf({10: -100, 11: -100, 12: -100, 13: -100}, closes=[
        (20000 + 100 * ((i * 3) % 7)) / rp6[i] for i in range(30)],
        extra_events=[ev(D[10], "ISS", "Cổ phiếu thưởng", 0.05)])
    v, p = det.scan_ticker(s6, evs6, 0.003, 3, D[0], tick_fn=tf6, pre_ex=set())
    ck("cụm bắt đầu ĐÚNG phiên ex-date (láng giềng trái ở đoạn trước) -> DRIFT",
       v == "DRIFT" and any("doan he so KHAC" in n for n in p["notes"]), f"v={v}")
    # Cùng ca nhưng ex-date nằm TRƯỚC cửa sổ (≤ win0, chỉ có trong pre_ex), win0 giữa cụm.
    v, p = _scan_at(s6, evs6, D[11], tf6)
    ck("ex-date trước cửa sổ = phiên đầu cụm, win0 giữa cụm -> phần nối dừng ở ex-date -> DRIFT",
       v == "DRIFT" and any("doan he so KHAC" in n and f"ex-date {D[10]} xen giua" in n
                            for n in p["notes"]), f"v={v} {p.get('notes', [])[-1:]}")
    # Đối chứng: ex-date trước cửa sổ nằm TRƯỚC láng giềng trái ⇒ không chen ⇒ PRICE_FIELD_MISMATCH.
    s7, evs7, tf7 = _pf({10: -100, 11: -100, 12: -100, 13: -100}, closes=[
        (20000 + 100 * ((i * 3) % 7)) / (1.1 * 1.05 if i < 7 else 1.1) for i in range(30)],
        extra_events=[ev(D[7], "ISS", "Cổ phiếu thưởng", 0.05)])
    v, p = _scan_at(s7, evs7, D[11], tf7)
    ck("ex-date trước cửa sổ (D[7], trong pre_ex) TRƯỚC láng giềng trái D[9] (không chen), win0 giữa cụm "
       "-> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH", f"v={v} {p.get('notes', [])[-1:]}")

    # Cổ tức tiền RẤT NHỎ (20đ ≈ 0,1% < biên láng giềng 0,15%) ngay sau cụm, vendor đúng ở cả hai đoạn:
    # chỉ cổng cùng-đoạn (r_pred láng giềng PHẢI) chặn được — biên độ lớn không bắt được.
    pr = [20000 + 100 * ((i * 3) % 7) for i in range(30)]
    f20 = (pr[12] - 100) / (pr[12] - 100 - 20)
    s14, evs14, tf14 = _pf({10: -100, 11: -100, 12: -100}, closes=[
        pr[i] / (1.1 * (f20 if i < 13 else 1.0)) for i in range(30)],
        extra_events=[ev(D[13], "DIV", dps=20)])
    v, p = det.scan_ticker(s14, evs14, 0.003, 3, D[0], tick_fn=tf14, pre_ex=set())
    ck("cổ tức tiền 20đ (≈0,1%) ex ngay SAU cụm -> láng giềng phải khác đoạn -> DRIFT (cổng cùng-đoạn)",
       v == "DRIFT" and any("doan he so KHAC" in n for n in p["notes"]), f"v={v} {p.get('notes', [])[-1:]}")
    # Cùng cổ tức nhỏ nhưng ex <= win0 (chỉ là NGÀY trong pre_ex, ex = phiên đầu cụm D[9]) và một ex-date
    # cũ hơn D[6]: phần nối phải dừng ở ex-date pre_ex MUỘN NHẤT (D[9]); dừng ở D[6] thì D[8] (lệch 0,1%
    # vì hệ số 20đ không nằm trong đường hệ số) bị nhận nhầm là láng giềng khớp.
    f20b = pr[8] / (pr[8] - 20)
    s15, evs15, tf15 = _pf({9: -100, 10: -100, 11: -100, 12: -100}, closes=[
        pr[i] / (1.1 * (1.05 if i < 6 else 1.0) * (f20b if i < 9 else 1.0)) for i in range(30)])
    v, p = det.scan_ticker(s15, evs15, 0.003, 3, D[10], tick_fn=tf15, pre_ex={D[6], D[9]})
    ck("hai ex-date trước cửa sổ (D[6], D[9] = cổ tức 20đ ở phiên đầu cụm) -> phần nối dừng ở D[9] -> DRIFT",
       v == "DRIFT" and any(f"ex-date {D[9]} xen giua" in n for n in p["notes"]),
       f"v={v} {p.get('notes', [])[-1:]}")

    # (6) Hai cụm cách nhau MỘT phiên khớp: phiên đó là láng giềng của cả hai.
    s8, evs8, tf8 = _pf({8: -100, 9: -100, 10: -100, 12: -100, 13: -100, 14: -100})
    for w, exp, nr in ((0, "PRICE_FIELD_MISMATCH", 2), (8, "PRICE_FIELD_MISMATCH", 2), (9, "PRICE_FIELD_MISMATCH", 1),
                       (10, "PRICE_FIELD_MISMATCH", 1), (12, "PRICE_FIELD_MISMATCH", 1),
                       (13, "AGREE", None)):
        v, p = det.scan_ticker(s8, evs8, 0.003, 3, D[w], tick_fn=tf8, pre_ex=set())
        ck(f"hai cụm cách 1 phiên, win0 = D[{w}] -> {exp}" + (f" n_runs={nr}" if nr else ""),
           v == exp and (nr is None or p.get("n_runs") == nr), f"v={v} n_runs={p.get('n_runs')}")
    s9, evs9, tf9 = _pf({8: -100, 9: -100, 10: -100, 12: -100, 13: -100, 14: -100})
    s9[11]["price"] = s9[11]["close"] * 1.1 * 1.0025
    for w in (0, 12):
        v, _p = det.scan_ticker(s9, evs9, 0.003, 3, D[w], tick_fn=tf9, pre_ex=set())
        ck(f"hai cụm, phiên giữa chỉ khớp SÁT (+0,25%), win0 = D[{w}] -> DRIFT", v == "DRIFT", f"v={v}")

    # (7) Cổ tức tiền 100đ vendor BỎ SÓT trên UPCOM = lệch ≈ −1 bước trên CẢ đoạn trước ex ⇒ không có láng
    # giềng cùng đoạn khớp ⇒ DRIFT ở mọi win0 (đối chứng ÂM của giới hạn đã biết "1-2 bước").
    s10, evs10, tf10 = _pf({}, n=30, extra_events=[ev(D[20], "DIV", dps=100)])
    for w in (0, 5, 10, 15, 17):
        v, p = _scan_at(s10, evs10, D[w], tf10)
        ck(f"ÂM cổ tức tiền 100đ vendor bỏ sót (≈ −1 bước cả đoạn), win0 = D[{w}] -> DRIFT",
           v == "DRIFT", f"v={v} {p.get('notes', [])[-1:]}")
    # và khi đoạn trước ex bị chặn trái bởi một ex-date trước cửa sổ: phần nối dừng ở đó ⇒ DRIFT.
    s11, evs11, tf11 = _pf({}, n=30, closes=[
        (20000 + 100 * ((i * 3) % 7)) / (1.1 * 1.05 if i < 7 else 1.1) for i in range(30)],
        extra_events=[ev(D[7], "ISS", "Cổ phiếu thưởng", 0.05), ev(D[20], "DIV", dps=100)])
    v, p = _scan_at(s11, evs11, D[10], tf11)
    ck("ÂM cổ tức tiền bỏ sót, đoạn bị chặn trái bởi ex-date trước cửa sổ -> DRIFT",
       v == "DRIFT" and any(f"ex-date {D[7]} xen giua" in n for n in p["notes"]), f"v={v}")

    # (8) Đối chứng ÂM lệch hệ số thật (chữ ký FPT, phiên 0..25) trượt win0 qua đoạn lệch ⇒ DRIFT mọi vị trí.
    s12, evs12, tf12 = _pf({}, n=30, closes=[(20000 + 100 * ((i * 3) % 7)) / (1.0 if i < 26 else 1.1)
                                             for i in range(30)])
    live = [w for w in range(0, 24) if _scan_at(s12, evs12, D[w], tf12)[0] != "DRIFT"]
    ck("ÂM chữ ký FPT, win0 trượt D[0..23] -> DRIFT ở MỌI vị trí", not live, f"không DRIFT tại {live}")

    # (9) NB3 §29: chứng từ cổng KẸP rẽ theo GIÁ TRỊ đo được — láng giềng lệch 12% không được gán
    # "sát ngưỡng / làm tròn Close".
    s13, _e, _t = _pf({}, n=10)
    s13[3]["price"] = s13[3]["close"] * 1.1 * 1.12
    for i in (4, 5, 6):
        s13[i]["price"] -= 100
    curve = {b["d"]: 1.1 for b in s13}
    rule, why = det.explain_price_field([4, 5, 6], s13, curve, 0.003, _tick("UPCOM"))
    ck("NB3: láng giềng lệch +12% -> lời 'CUNG lech > dev_tol', KHÔNG 'SAT nguong'/'lam tron'",
       rule is None and "CUNG lech" in why and "SAT nguong" not in why and "lam tron" not in why
       and "+12.0000%" in why, f"{why}")
    # Mn: láng giềng lệch ÂM lớn (−12%) phải bị loại như +12% — `abs()` trong cổng KẸP không được bỏ.
    for side, ix in (("trái", 3), ("phải", 7)):
        sn, _e, _t = _pf({}, n=10)
        sn[ix]["price"] = sn[ix]["close"] * 1.1 * 0.88
        for i in (4, 5, 6):
            sn[i]["price"] -= 100
        rule, why = det.explain_price_field([4, 5, 6], sn, {b["d"]: 1.1 for b in sn}, 0.003, _tick("UPCOM"))
        ck(f"Mn: láng giềng {side} lệch −12% -> không đổi nhãn, lời 'CUNG lech' + −12.0000%",
           rule is None and "CUNG lech" in why and "SAT nguong" not in why and "-12.0000%" in why, f"{why}")

    # Mz: láng giềng |dev| == dev_tol ĐÚNG BẰNG (dev_tol lấy từ chính phép đo) -> 'khop trong dev_tol, SAT nguong',
    # không phải 'CUNG lech > dev_tol' (đổi `<=` thành `<` sai nguyên nhân §29 đúng ở biên).
    sz, _e, _t = _pf({}, n=10)
    sz[3]["price"] = sz[3]["close"] * 1.1 * 1.004
    for i in (4, 5, 6):
        sz[i]["price"] -= 100
    nbz = abs((sz[3]["price"] / sz[3]["close"]) / 1.1 - 1.0)
    rule, why = det.explain_price_field([4, 5, 6], sz, {b["d"]: 1.1 for b in sz}, nbz, _tick("UPCOM"))
    ck("Mz: láng giềng |dev| == dev_tol đúng biên -> lời 'SAT nguong', không 'CUNG lech'",
       rule is None and "SAT nguong" in why and "CUNG lech" not in why, f"{why}")

    # Mc: pre_ex có ex-date SỚM HƠN mọi phiên trước cửa sổ (lead == before) -> lý do là HẾT CHUỖI NẠP, không
    # phải "ex-date xen giữa" (đổi `<` thành `<=` ở lead_why làm nói sai nguyên nhân §29).
    v, p = det.scan_ticker(s_[8:], evs_, 0.003, 3, D[10], tick_fn=tf_, pre_ex={D[8]})
    ck("Mc: ex-date pre_ex = phiên đầu chuỗi nạp, lead == before -> lý do 'het chuoi nap', không 'xen giua'",
       v == "DRIFT" and any("het chuoi nap" in n for n in p["notes"])
       and not any("xen giua" in n for n in p["notes"]), f"v={v} {p.get('notes', [])[-1:]}")

    # Md: CUM_PAD_DAYS = 25 là giới hạn đã biết của cụm nối lùi — cụm D[5..13] cần láng giềng D[4] nằm ngoài
    # chuỗi nạp của win0 = D[10] (load0 = 06-06) ⇒ DRIFT fail-closed. Đệm 40 ngày sẽ tìm được D[4] và đổi nhãn.
    ck("Md: hằng số CUM_PAD_DAYS = 25", det.CUM_PAD_DAYS == 25, f"{det.CUM_PAD_DAYS}")
    sm, evm, tfm = _pf({i: -100 for i in range(5, 14)})
    v, p = _scan_at(sm, evm, D[10], tfm)
    ck("Md: cụm D[5..13] cần láng giềng D[4] ngoài chuỗi nạp (load0 = win0 − 25 ngày) -> DRIFT, 'het chuoi nap'",
       v == "DRIFT" and any("het chuoi nap" in n for n in p["notes"]), f"v={v} {p.get('notes', [])[-1:]}")

    # NB6: `until` của _scan_at — phiên/sự kiện sau asof không được thấy (cùng ranh giới với run_scan).
    pa = [20000 + 100 * ((i * 3) % 7) for i in range(30)]
    sa, eva, tfa = _pf({i: -100 for i in range(8, 14)}, ex=D[24],
                       closes=[pa[i] / (1.1 if i < 24 else 1.0) for i in range(30)],
                       extra_events=[ev(D[28], "ISS", det.RIGHTS_METHOD, 0.2)])
    v_all, _p = _scan_at(sa, eva, D[0], tfa)
    v_cut, p_cut = _scan_at(sa, eva, D[0], tfa, until=D[26])
    ck("NB6 _scan_at(until): quyền mua ex D[28] sau asof D[26] bị cắt -> PRICE_FIELD_MISMATCH; không cắt -> "
       "UNCOMPUTABLE/DRIFT (uncomputable trong cửa sổ)",
       v_cut == "PRICE_FIELD_MISMATCH" and v_all in ("UNCOMPUTABLE", "DRIFT"), f"cut={v_cut} all={v_all}")

    # B1 (vòng 2): 3 cụm −1 bước {3,4,5}, {9..13}, {17,18,19}, win0 = D[0] ⇒ n_runs == 3 và marker nêu span của
    # cụm DÀI NHẤT trong cửa sổ (D[9]..D[13]) — giết mutation lấy span cụm CUỐI / cụm ĐẦU.
    s_b1, evs_b1, tf_b1 = _pf({**{i: -100 for i in (3, 4, 5, 17, 18, 19)}, **{i: -100 for i in range(9, 14)}})
    v, p = _scan_at(s_b1, evs_b1, D[0], tf_b1)
    ck("B1: 3 cụm (3 / 5 / 3 phiên), win0 = D[0] -> PRICE_FIELD_MISMATCH n_runs == 3",
       v == "PRICE_FIELD_MISMATCH" and p.get("n_runs") == 3, f"v={v} n_runs={p.get('n_runs')}")
    ck("B1: d0/d1 = span cụm dài nhất D[9]..D[13] (không phải cụm cuối D[17..19] hay cụm đầu D[3..5])",
       p.get("d0") == D[9] and p.get("d1") == D[13], f"d0={p.get('d0')} d1={p.get('d1')}")

    # NB6/K: phiên SAU asof không được thấy — cụm D[20..24] chỉ có sau `until` = D[15].
    pk = [20000 + 100 * ((i * 3) % 7) for i in range(30)]
    cl1 = [pk[i] / (1.1 if i < 1 else 1.0) for i in range(30)]   # hệ số 1,1 chỉ ở D[0]; ex = D[1]
    s_k, evs_k, tf_k = _pf({i: -100 for i in range(20, 25)}, ex=D[1], closes=cl1)
    v_cut, _p = _scan_at(s_k, evs_k, D[0], tf_k, until=D[15])
    v_all, _p = _scan_at(s_k, evs_k, D[0], tf_k)
    ck("K: cụm chỉ nằm SAU until -> AGREE khi cắt; PRICE_FIELD_MISMATCH khi không cắt",
       v_cut == "AGREE" and v_all == "PRICE_FIELD_MISMATCH", f"cut={v_cut} all={v_all}")
    # NB6/L: sự kiện ex SAU asof không được vào đường hệ số — ISS 5% ở D[10] mà Close chưa điều chỉnh.
    s_l, evs_l, tf_l = _pf({}, ex=D[1], closes=cl1, extra_events=[ev(D[10], "ISS", "Cổ phiếu thưởng", 0.05)])
    v_cut, _p = _scan_at(s_l, evs_l, D[0], tf_l, until=D[8])
    v_all, _p = _scan_at(s_l, evs_l, D[0], tf_l)
    ck("L: sự kiện ex D[10] sau until D[8] -> AGREE khi cắt; khác AGREE khi không cắt",
       v_cut == "AGREE" and v_all != "AGREE", f"cut={v_cut} all={v_all}")

    # NB4 sweep: ex-date uncomputable (quyền mua) tại D[5], cụm D[10..12]. ex > win0 ⇒ trong cửa sổ, chặn
    # đường PFM ⇒ DRIFT; ex <= win0 (chỉ còn là NGÀY trong pre_ex) ⇒ PRICE_FIELD_MISMATCH.
    s_n, evs_n, tf_n = _pf({10: -100, 11: -100, 12: -100},
                           extra_events=[ev(D[5], "ISS", det.RIGHTS_METHOD, 0.5)])
    got_n = {w: _scan_at(s_n, evs_n, D[w], tf_n)[0] for w in range(0, 9)}
    exp_n = {w: ("DRIFT" if w < 5 else "PRICE_FIELD_MISMATCH") for w in got_n}
    ck("NB4 sweep win0 = D[0..8], ex uncomputable D[5]: DRIFT khi win0 < ex, PFM khi win0 >= ex",
       got_n == exp_n, f"got={got_n}")


def t_price_field():
    """Lệch TRƯỜNG Price phải tách khỏi lệch HỆ SỐ thật; mọi đường không xác định được ⇒ hành vi cũ."""
    print("\n[17] PRICE_FIELD_MISMATCH — lệch trường Price vs lệch hệ số thật")
    ck("ngưỡng KHÔNG đổi: DEV_TOL 0,003, MIN_RUN 3", det.DEV_TOL == 0.003 and det.MIN_RUN == 3)
    ck("hằng số có tên: PFM_MAX_TICKS 2, PFM_TICK_FRAC 0,2, CLOSE_GRID_VND 10, PFM_NEIGHBOR_FRAC 0,5",
       det.PFM_MAX_TICKS == 2 and det.PFM_TICK_FRAC == 0.2 and det.CLOSE_GRID_VND == 10
       and det.PFM_NEIGHBOR_FRAC == 0.5)

    # (a) Số thật asof 2026-10-07: 4 mã đổi nhãn, đúng TỪNG TRƯỜNG của dòng máy đọc thật.
    for tk in ("DRI", "DVN", "SHC", "CC1"):
        v, p = _scan_real(tk)
        ck(f"thật {tk} -> PRICE_FIELD_MISMATCH, dòng máy đọc đúng từng byte",
           _marker(tk, v, p) == REAL_PFM_AFTER[tk], f"v={v} {_marker(tk, v, p)}")
    # (b) Mã còn lại GIỮ NGUYÊN dòng DRIFT cũ từng byte (VHF kiểm lại, không đoán).
    for tk in ("HC1", "VFR", "VHF"):
        v, p = _scan_real(tk)
        ck(f"thật {tk} -> vẫn DRIFT, dòng máy đọc Y NGUYÊN baseline",
           _marker(tk, v, p) == REAL_DRIFT_BEFORE[tk], f"v={v} {_marker(tk, v, p)}")
    v, p = _scan_real("VFR")
    ck("VFR thật: bị loại ngay ở cổng KẸP (láng giềng 07-01 +0,29% chỉ khớp SÁT ngưỡng)",
       any("KHONG phai loi truong Price" in n and "SAT nguong" in n and "2026-07-01" in n
           for n in p["notes"]), f"{[n for n in p['notes'] if 'Price' in n]}")
    v, p = _scan_real("PBP")
    ck("thật PBP (cụm 56 phiên từ rìa trái, lệch +0,41% ổn định) -> vẫn DRIFT our_table_missing",
       v == "DRIFT" and p["run"] >= 3 and p["d0"] == "2026-06-09" and p["dir"] == "our_table_missing",
       f"v={v} {p.get('run')} {p.get('d0')}")
    v, p = _scan_real("HC1")
    ck("HC1: chứng từ nói rõ vì sao KHÔNG phải lỗi trường Price (+3,96 bước)",
       any("KHONG phai loi truong Price" in n and "+3.96 buoc" in n for n in p["notes"]),
       f"{[n for n in p['notes'] if 'Price' in n]}")
    v, p = _scan_real("DRI")
    ck("DRI: chứng từ ghi số bước từng phiên + hai láng giềng khớp",
       any("tick_offset" not in n and "-1.00x100d" in n and "2026-09-09/2026-09-15" in n
           for n in p["notes"]), f"{p['notes']}")

    # (c) FAIL-CLOSED: không biết sàn ⇒ luật tick_offset không áp ⇒ DRIFT Y NGUYÊN bản cũ.
    for tk in ("DRI", "DVN"):
        v, p = _scan_real(tk, tick_fn=lambda price: None)
        ck(f"{tk}: sàn KHÔNG tra được -> DRIFT y nguyên baseline (fail-closed)",
           _marker(tk, v, p) == REAL_DRIFT_BEFORE[tk], f"v={v} {_marker(tk, v, p)}")
        v, p = _scan_real(tk, tick_fn=None)
        ck(f"{tk}: không truyền tick_fn (mặc định) -> DRIFT y nguyên baseline",
           _marker(tk, v, p) == REAL_DRIFT_BEFORE[tk], f"v={v}")
    v, p = _scan_real("SHC", tick_fn=None)
    ck("SHC: luật stale_price KHÔNG cần sàn -> vẫn PRICE_FIELD_MISMATCH khi sàn không biết",
       _marker("SHC", v, p) == REAL_PFM_AFTER["SHC"], f"v={v}")
    v, p = _scan_real("DVN", tick_fn="HOSE")
    ck("DVN nếu là HOSE (bước 50 ở 20.400) -> −4,17 bước > 2 -> DRIFT: bước phải theo SÀN THẬT",
       v == "DRIFT", f"v={v}")

    # (d) Đối chứng ÂM — lệch hệ số THẬT phải vẫn DRIFT.
    # FPT: vendor chưa áp 1,1 cho 26 phiên, áp đúng 4 phiên cum cuối (SETTLE_RUN=4) — cụm từ rìa trái.
    s, evs, tf = _pf({}, n=30, closes=[(20000 + 100 * ((i * 3) % 7)) / (1.0 if i < 26 else 1.1)
                                       for i in range(30)])
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("ÂM chữ ký FPT (r ổn định −9,09%, khớp chỉ ở 4 phiên cuối) -> DRIFT", v == "DRIFT", f"v={v}")
    # FPT "kẹt nửa chừng" có KẸP (phiên 0 và 26.. khớp): cổng kẹp lọt, nhưng −9,09% = ~20 bước.
    s, evs, tf = _pf({}, n=30, closes=[(20000 + 100 * ((i * 3) % 7)) / (1.0 if 0 < i < 26 else 1.1)
                                       for i in range(30)])
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("ÂM hệ số thật kẹp giữa 2 phiên khớp nhưng lệch ~20 bước -> DRIFT", v == "DRIFT", f"v={v}")
    ck("ÂM ... chứng từ nêu số bước", any("buoc 100d" in n for n in p["notes"]), f"{p['notes']}")

    # (e) Ranh giới luật tick_offset trên fixture tổng hợp UPCOM (bước 100).
    def run(deltas, **kw):
        s, evs, tf = _pf(deltas, **kw)
        return det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    v, p = run({10: -100, 11: -100, 12: -100})
    ck("1 bước ×3 phiên kẹp giữa phiên khớp -> PRICE_FIELD_MISMATCH tick_offset",
       v == "PRICE_FIELD_MISMATCH" and p["pfm_rules"] == "tick_offset" and p["n_runs"] == 1,
       f"v={v} {p.get('pfm_rules')}")
    v, _ = run({10: +200, 11: -100, 12: +100})
    ck("±1/±2 bước lẫn dấu -> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH", f"v={v}")
    v, _ = run({10: -300, 11: -300, 12: -300})
    ck("3 bước (> PFM_MAX_TICKS) -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({10: -100, 11: -100, 12: -300})
    ck("MỘT phiên 3 bước trong cụm -> DRIFT (mọi phiên phải đạt)", v == "DRIFT", f"v={v}")
    v, _ = run({10: -118, 11: -118, 12: -118})
    ck("dư 0,18 bước (≤ 0,2) -> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH", f"v={v}")
    v, _ = run({10: -125, 11: -125, 12: -125})
    ck("dư 0,25 bước (> 0,2) -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({10: -100, 11: -100, 12: -145})
    ck("MỘT phiên dư 0,45 bước -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({10: +18, 11: +18, 12: +18}, base=5000, step=0)
    ck("lệch 0,18 bước (>0,3% ở giá 5.000, nhưng làm tròn = 0 bước) -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({0: -100, 1: -100, 2: -100})
    ck("cụm chạm RÌA TRÁI cửa sổ (không có láng giềng trước) -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({27: -100, 28: -100, 29: -100})
    ck("cụm chạm RÌA PHẢI (phiên cuối) -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({1: -100, 2: -100, 3: -100})
    ck("cụm bắt đầu ở phiên thứ 2 (có 1 láng giềng trước) -> PRICE_FIELD_MISMATCH",
       v == "PRICE_FIELD_MISMATCH", f"v={v}")
    # láng giềng phải ở CÙNG đoạn hệ số: thêm ex-date ngay sau cụm (vendor đúng ở cả hai đoạn).
    rp2 = [1.1 * 1.05 if i <= 12 else 1.1 for i in range(30)]
    s, evs, tf = _pf({10: -100, 11: -100, 12: -100}, closes=[
        (20000 + 100 * ((i * 3) % 7)) / rp2[i] for i in range(30)],
        extra_events=[ev(D[13], "ISS", "Cổ phiếu thưởng", 0.05)])
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("láng giềng sau nằm bên kia một ex-date (đoạn hệ số khác) -> DRIFT", v == "DRIFT",
       f"v={v} {p.get('notes', [])[-1:]}")
    # hai cụm: một giải thích được, một không ⇒ DRIFT với payload Y NGUYÊN như khi không có luật mới.
    deltas = {5: -100, 6: -100, 7: -100, 15: -300, 16: -300, 17: -300, 18: -300}
    v, p = run(deltas)
    s, evs, _tf = _pf(deltas)
    v0, p0 = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=None)
    ck("hai cụm, một không giải thích được -> DRIFT, dòng máy đọc Y NGUYÊN bản không-luật",
       v == "DRIFT" and v0 == "DRIFT" and det.marker_drift("X", p, "none")
       == det.marker_drift("X", p0, "none"), f"v={v}")
    v, _ = run({5: -100, 6: -100, 7: -100, 15: -100, 16: -100, 17: -100})
    ck("hai cụm đều 1 bước -> PRICE_FIELD_MISMATCH, n_runs=2", v == "PRICE_FIELD_MISMATCH"
       and _.get("n_runs") == 2, f"v={v}")
    # cụm < MIN_RUN không cần giải thích (không phải DRIFT từ trước).
    v, _ = run({5: -300, 6: -300, 10: -100, 11: -100, 12: -100})
    ck("cụm 2 phiên 3 bước (< MIN_RUN) không chặn -> PRICE_FIELD_MISMATCH",
       v == "PRICE_FIELD_MISMATCH", f"v={v}")
    # ex-date UNCOMPUTABLE ⇒ giữ hành vi cũ (DRIFT partial).
    v, p = run({10: -100, 11: -100, 12: -100},
               extra_events=[ev(D[3], "ISS", det.RIGHTS_METHOD, 0.2)])
    ck("có ex-date uncomputable -> DRIFT partial như cũ, KHÔNG đổi nhãn",
       v == "DRIFT" and p.get("partial") is True, f"v={v}")

    # (e2) R1 arch-review vòng 2: rìa trái cửa sổ 120 ngày TRÔI mỗi ngày ⇒ khi `win0` trượt tới phiên đầu
    # cụm, láng giềng trái phải lấy từ chuỗi nạp trước cửa sổ (load0), không rơi về DRIFT giả.
    for tk, w0 in (("DRI", "2026-09-10"), ("SHC", "2026-06-30")):
        s_ = _real(tk)
        v, p = det.scan_ticker(s_, REAL_EVENTS[tk], det.DEV_TOL, det.MIN_RUN, w0,
                               tick_fn=_tick("UPCOM", tk), pre_ex=set())
        ck(f"R1 thật {tk}: win0 = phiên ĐẦU cụm ({w0}) -> láng giềng trái từ load0 -> vẫn "
           f"PRICE_FIELD_MISMATCH, dòng máy đọc đúng từng byte",
           _marker(tk, v, p) == REAL_PFM_AFTER[tk], f"v={v} {_marker(tk, v, p)} {p.get('notes', [])[-2:]}")
        v, p = det.scan_ticker(s_, REAL_EVENTS[tk], det.DEV_TOL, det.MIN_RUN, w0,
                               tick_fn=_tick("UPCOM", tk), pre_ex=None)
        ck(f"R1 {tk}: pre_ex=None (không biết ex-date trước cửa sổ) -> DRIFT y nguyên baseline "
           f"(fail-closed, hành vi cũ)", _marker(tk, v, p) == REAL_DRIFT_BEFORE[tk], f"v={v}")
        v, p = det.scan_ticker([b for b in s_ if b["d"] >= w0], REAL_EVENTS[tk], det.DEV_TOL,
                               det.MIN_RUN, w0, tick_fn=_tick("UPCOM", tk), pre_ex=set())
        ck(f"R1 {tk}: KHÔNG có phiên nào trước cửa sổ trong chuỗi nạp -> DRIFT (fail-closed)",
           v == "DRIFT" and any("ria TRAI" in n and "khong co phien nao truoc" in n
                                for n in p["notes"]), f"v={v} {p.get('notes', [])[-1:]}")
    # ex-date ≤ win0 KHÔNG nằm trong đường hệ số ⇒ một ex-date xen giữa láng giềng trước cửa sổ và cụm
    # là vô hình với cổng cùng-đoạn; phải chặn qua `pre_ex`.
    s_ = _real("DRI")
    v, p = det.scan_ticker(s_, REAL_EVENTS["DRI"], det.DEV_TOL, det.MIN_RUN, "2026-09-10",
                           tick_fn=_tick("UPCOM", "DRI"), pre_ex={"2026-09-10"})
    ck("R1 DRI: ex-date (≤ win0) xen giữa láng giềng trước cửa sổ và cụm -> khác đoạn -> DRIFT",
       _marker("DRI", v, p) == REAL_DRIFT_BEFORE["DRI"] and any(
           "doan he so KHAC" in n and "2026-09-10 xen giua" in n for n in p["notes"]), f"v={v}")
    v, p = det.scan_ticker(s_, REAL_EVENTS["DRI"], det.DEV_TOL, det.MIN_RUN, "2026-09-10",
                           tick_fn=_tick("UPCOM", "DRI"), pre_ex={"2026-09-09", "2026-08-01"})
    ck("R1 DRI: ex-date trước cửa sổ nhưng KHÔNG xen giữa (≤ láng giềng) -> vẫn PRICE_FIELD_MISMATCH",
       _marker("DRI", v, p) == REAL_PFM_AFTER["DRI"], f"v={v}")
    # Đối chứng ÂM: lệch hệ số THẬT kéo dài từ trước cửa sổ — láng giềng trước cửa sổ cũng lệch ⇒ DRIFT.
    for w in (3, 5, 8):
        s_, evs_, tf_ = _pf({}, n=30, closes=[(20000 + 100 * ((i * 3) % 7)) / (1.1 * 1.01 if i < 12
                                                                                   else 1.1)
                                              for i in range(30)])
        v, p = det.scan_ticker(s_, evs_, 0.003, 3, D[w], tick_fn=tf_, pre_ex=set())
        ck(f"R1 ÂM: lệch hệ số thật −1% phiên 0..11, win0 = phiên {w} (giữa đoạn lệch) -> DRIFT, "
           f"chứng từ: lùi hết chuỗi nạp vẫn lệch",
           v == "DRIFT" and p["d0"] == D[w] and any(
               "ria TRAI" in n and "het chuoi nap" in n and f"{D[0]}..{D[w - 1]} van lech" in n
               for n in p["notes"]), f"v={v} {p.get('d0')} {p.get('notes', [])[-1:]}")
    # và 1-bước kiểu DRI nhưng láng giềng trước cửa sổ lệch hệ số (không khớp RÕ) ⇒ DRIFT.
    s_, evs_, tf_ = _pf({10: -100, 11: -100, 12: -100})
    s_[9]["price"] = s_[9]["close"] * 1.1 * 1.002
    v, p = det.scan_ticker(s_, evs_, 0.003, 3, D[10], tick_fn=tf_, pre_ex=set())
    ck("R1 ÂM: win0 = phiên đầu cụm 1-bước, láng giềng TRƯỚC cửa sổ +0,20% -> DRIFT", v == "DRIFT",
       f"v={v}")
    v, p = det.scan_ticker(_pf({10: -100, 11: -100, 12: -100})[0], evs_, 0.003, 3, D[10], tick_fn=tf_,
                           pre_ex=set())
    ck("R1 tổng hợp: win0 = phiên đầu cụm 1-bước, láng giềng trước cửa sổ khớp -> PRICE_FIELD_MISMATCH",
       v == "PRICE_FIELD_MISMATCH", f"v={v}")

    # (f) Bước giá & độ phân giải: HOSE <10.000đ bước 10 < nhiễu làm tròn Close ⇒ fail-closed.
    v, _ = run({10: -20, 11: -20, 12: -20}, base=5000, step=10, exchange="HOSE")
    ck("HOSE giá 5.000 (bước 10): 2 bước nhưng KHÔNG phân giải được -> DRIFT", v == "DRIFT", f"v={v}")
    v, _ = run({10: -100, 11: -100, 12: -100}, base=30000, step=50, exchange="HOSE")
    ck("HOSE giá 30.000 (bước 50): −2 bước -> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH",
       f"v={v}")
    # ranh giới khung 10.000: Price 10.000 (bước 50) vs Close·r 9.900 (bước 10) ⇒ dùng bước MỊN.
    v, _ = run({10: 100, 11: 100, 12: 100}, base=9900, step=0, exchange="HOSE")
    ck("ranh giới khung HOSE 9.900→10.000: lấy bước mịn (10) -> không phân giải -> DRIFT",
       v == "DRIFT", f"v={v}")
    v, _ = run({10: -200, 11: -200, 12: -200}, base=30000, step=100, exchange="HNX")
    ck("HNX giá 30.000 (bước 100): −2 bước -> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH",
       f"v={v}")
    v, _ = run({10: -200, 11: -200, 12: -200}, base=30000, step=100, exchange="HOSE")
    ck("cùng chuỗi đó nếu HOSE (bước 50): −4 bước -> DRIFT", v == "DRIFT", f"v={v}")

    # (g) Luật stale_price — từng điều kiện là cần (biến thể của SHC thật).
    run_d = ["2026-06-30", "2026-07-01", "2026-07-02", "2026-07-03", "2026-07-06", "2026-07-07",
             "2026-07-08", "2026-07-09"]
    for label, mut in (
            ("MỘT phiên KL = 100 (một lô chẵn)", [("2026-07-01", "vol", 100.0)]),
            ("MỘT phiên KL NULL", [("2026-07-01", "vol", None)]),
            ("Price KHÔNG bằng láng giềng trước", [("2026-06-29", "price", 10800.0),
                                                    ("2026-06-29", "close", 10800 / 1.05)]),
            ("Price KHÔNG đứng giá suốt cụm", [("2026-07-03", "price", 11000.0)]),
            ("Close·r_pred KHÔNG bằng Price phiên sau", [("2026-07-10", "price", 12600.0),
                                                          ("2026-07-10", "close", 12600 / 1.05)]),
            ("Close của MỘT phiên GIỮA cụm lệch khỏi Price phiên sau", [("2026-07-03", "close", 11910.0)]),
            ("Price láng giềng trước CAO hơn giá đứng", [("2026-06-29", "price", 11000.0),
                                                        ("2026-06-29", "close", 11000 / 1.05)])):
        v, p = _scan_real("SHC", mut=mut)
        ck(f"SHC biến thể: {label} -> DRIFT", v == "DRIFT", f"v={v} {p.get('pfm_rules')}")
    # So với PRICE phiên sau, không phải Close phiên sau: láng giềng sau khớp +0,10%, cụm có Close·r_pred
    # = Price sau +0,25% (trong dev_tol) ⇒ stale_price; so Close/Close sẽ thành +0,35% ⇒ trượt.
    c_run = 12400 * 1.0025 / 1.05
    v, p = _scan_real("SHC", mut=[("2026-07-10", "close", 12400 / 1.05 / 1.001)]
                      + [(d, "close", c_run) for d in run_d])
    ck("SHC biến thể: Close·r_pred = Price phiên sau +0,25% -> vẫn stale_price (so với PRICE sau)",
       v == "PRICE_FIELD_MISMATCH" and p.get("pfm_rules") == "stale_price", f"v={v}")
    v, p = _scan_real("SHC", mut=[(d, "vol", 99.0) for d in run_d])
    ck("SHC biến thể: KL 99 (lô lẻ) mọi phiên -> vẫn stale_price", v == "PRICE_FIELD_MISMATCH"
       and p["pfm_rules"] == "stale_price", f"v={v}")
    v, p = _scan_real("SHC")
    ck("SHC: chứng từ trích Price đứng, KL, và Price phiên sau",
       any("Price DUNG 10900" in n and "2026-07-10 12400" in n for n in p["notes"]), f"{p['notes']}")

    # (g2) Cổng KẸP phải khớp RÕ (arch-review 2026-10-08 #1): láng giềng chỉ "trong ngưỡng" không đủ.
    s, evs, tf = _pf({10: -100, 11: -100, 12: -100})
    s[9]["price"] = s[9]["close"] * 1.1 * 1.002          # láng giềng trước +0,20% (trong 0,3%, ngoài 0,15%)
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("láng giềng trước +0,20% (khớp SÁT ngưỡng) -> DRIFT", v == "DRIFT", f"v={v}")
    s, evs, tf = _pf({10: -100, 11: -100, 12: -100})
    s[13]["price"] = s[13]["close"] * 1.1 * 0.998        # láng giềng sau −0,20%
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("láng giềng sau −0,20% -> DRIFT", v == "DRIFT", f"v={v}")
    s, evs, tf = _pf({10: -100, 11: -100, 12: -100})
    s[9]["price"] = s[9]["close"] * 1.1 * 1.001          # +0,10% ≤ 0,15%
    s[13]["price"] = s[13]["close"] * 1.1 * 0.999
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("hai láng giềng ±0,10% (≤ 0,15%) -> PRICE_FIELD_MISMATCH", v == "PRICE_FIELD_MISMATCH", f"v={v}")

    # Đối chứng ÂM chính (arch-review #1, mô phỏng sim2): vendor dùng f·(1+e) ĐỒNG NHẤT cả đoạn, `Close`
    # tròn 10đ ⇒ dev rải quanh e ⇒ cụm VỠ, kẹp giữa phiên "khớp". e sát DEV_TOL. Phải KHÔNG BAO GIỜ đổi nhãn.
    import random

    def sim(seed, e, exch, base, n=40):
        rnd = random.Random(seed)
        ds = [f"2026-05-{i + 1:02d}" if i < 31 else f"2026-06-{i - 30:02d}" for i in range(n + 1)]
        tick = _tick(exch)
        price, out = base, []
        for i in range(n):
            price = max(1000, price + tick(price) * rnd.choice([-2, -1, 0, 0, 1, 2]))
            close = round(price / (1.05 * (1 + e)) / 10) * 10
            out.append({"d": ds[i], "price": float(price), "close": float(close),
                        "hi": 0.0, "lo": 0.0, "vol": 50000.0})
        evs = [ev(ds[n], "ISS", "Cổ phiếu thưởng", 0.05)]
        return det.scan_ticker(out, evs, det.DEV_TOL, det.MIN_RUN, out[0]["d"], tick_fn=tick)

    cfgs = [(e, x, b) for e in (0.0028, 0.003, 0.0032) for x, b in
            (("HOSE", 15000), ("UPCOM", 30000), ("HNX", 33000))]
    leaked = sum(sim(sd, e, x, b)[0] == "PRICE_FIELD_MISMATCH" for e, x, b in cfgs for sd in range(150))
    saved_frac = det.PFM_NEIGHBOR_FRAC
    try:
        det.PFM_NEIGHBOR_FRAC = 1.0                      # không biên = bản c864ffda
        leaked_nomargin = sum(sim(sd, e, x, b)[0] == "PRICE_FIELD_MISMATCH"
                              for e, x, b in cfgs for sd in range(150))
    finally:
        det.PFM_NEIGHBOR_FRAC = saved_frac
    ck("ÂM lệch hệ số ĐỒNG NHẤT 0,28–0,32% vỡ cụm do làm tròn Close (1.350 chuỗi) -> 0 ca đổi nhãn",
       leaked == 0, f"leaked={leaked}")
    ck("... đối chứng không vô nghĩa: bỏ biên KẸP thì CÓ ca lọt", leaked_nomargin > 0,
       f"leaked_nomargin={leaked_nomargin}")

    # Hai luật trong cùng một mã: pfm_rules phải liệt kê CẢ HAI (không chỉ luật đầu).
    s, evs, tf = _pf({5: -100, 6: -100, 7: -100})
    p14, p18 = s[14]["price"], s[18]["price"]
    for i in (15, 16, 17):
        s[i]["price"], s[i]["close"], s[i]["vol"] = p14, p18 / 1.1, 0.0
    v, p = det.scan_ticker(s, evs, 0.003, 3, D[0], tick_fn=tf)
    ck("một cụm tick_offset + một cụm stale_price -> pfm_rules 'stale_price,tick_offset', n_runs 2",
       v == "PRICE_FIELD_MISMATCH" and p.get("pfm_rules") == "stale_price,tick_offset"
       and p.get("n_runs") == 2, f"v={v} {p.get('pfm_rules')} p14={p14} p18={p18}")
    # r_pred lớn làm nhiễu làm tròn Close lớn theo: HOSE bước 50 với r_pred 2,5 ⇒ ±12,5đ > 10đ.
    v, _ = run({10: -100, 11: -100, 12: -100}, base=30000, step=50, exchange="HOSE", rp=2.5)
    ck("HOSE bước 50 nhưng r_pred 2,5 (nhiễu ±12,5đ > 0,2 bước) -> không phân giải -> DRIFT",
       v == "DRIFT", f"v={v}")

    # (h) Hợp đồng dòng máy đọc.
    m = det.marker_price_field("DRI", {"ex": "2026-09-22", "n_runs": 1, "pfm_rules": "tick_offset",
                                       "d0": "2026-09-10", "d1": "2026-09-14", "dev": -0.007002},
                               "SpaceX,ZaloPay")
    ck("marker_price_field đúng 9 trường theo thứ tự",
       m.split("|") == ["ADJFACTOR_PRICE_FIELD_MISMATCH", "DRI", "2026-09-22", "1", "tick_offset",
                        "2026-09-10", "2026-09-14", "SpaceX,ZaloPay", "-0.007002"], m)

    # (i) live_exchange_fn: sàn THẬT qua marketId, fail-closed, cache, không ghi dnse_raw, stdout sạch.
    import io
    import types
    from contextlib import redirect_stdout
    calls = {"connect": 0, "quote": [], "raw_log": "unset"}

    class FakeQ:
        def __init__(self, tk):
            self.exchange = {"DRI": "UPCOM", "MUTE": "HOSE"}.get(tk, "HOSE")
            self.exchange_known = tk == "DRI"

    class FakeSrc:
        _raw_log = "dnse_raw_x.jsonl"

        def connect(self):
            calls["connect"] += 1
            calls["raw_log"] = self._raw_log
            print("[dnse] connect noise")

        def get_quote(self, tk):
            calls["quote"].append(tk)
            if tk == "BOOM":
                raise RuntimeError("timeout")
            return FakeQ(tk)

    import trading_bot.brokers as tb
    saved = tb.get_quote_source
    saved_env = os.environ.pop("MIKE_ADJFACTOR_NO_BQ", None)
    buf = io.StringIO()
    try:
        tb.get_quote_source = lambda name: FakeSrc()
        fn = _REAL_LIVE_EXCHANGE_FN()
        with redirect_stdout(buf):
            got = [fn("DRI"), fn("MUTE"), fn("BOOM"), fn("DRI")]
        os.environ["MIKE_ADJFACTOR_NO_BQ"] = "1"
        fn2 = _REAL_LIVE_EXCHANGE_FN()
        n_before = calls["connect"]
        got2 = fn2("DRI")
    finally:
        tb.get_quote_source = saved
        os.environ.pop("MIKE_ADJFACTOR_NO_BQ", None)
        if saved_env is not None:
            os.environ["MIKE_ADJFACTOR_NO_BQ"] = saved_env
    ck("live_exchange_fn: marketId biết -> 'UPCOM'; exchange_known=False -> None (KHÔNG mặc định HOSE);"
       " lỗi -> None", got == ["UPCOM", None, None, "UPCOM"], f"{got}")
    ck("live_exchange_fn: connect MỘT lần, cache theo mã", calls["connect"] == 1
       and calls["quote"] == ["DRI", "MUTE", "BOOM"], f"{calls}")
    # Whitelist sàn (arch-review vòng 2): chuỗi sàn lạ/viết thường từ field `exchange` tự do.
    class OddQ:
        def __init__(self, tk):
            self.exchange = {"LOW": "hnx", "ODD": "HCX", "SP": " UPCOM "}[tk]
            self.exchange_known = True

    class OddSrc(FakeSrc):
        def connect(self):                      # không đếm vào `calls` của các assertion khác
            pass

        def get_quote(self, tk):
            return OddQ(tk)
    saved_q = tb.get_quote_source
    saved_env = os.environ.pop("MIKE_ADJFACTOR_NO_BQ", None)
    try:
        tb.get_quote_source = lambda name: OddSrc()
        fn3 = _REAL_LIVE_EXCHANGE_FN()
        with redirect_stdout(io.StringIO()):
            got3 = [fn3("LOW"), fn3("ODD"), fn3("SP")]
    finally:
        tb.get_quote_source = saved_q
        if saved_env is not None:
            os.environ["MIKE_ADJFACTOR_NO_BQ"] = saved_env
    ck("live_exchange_fn: whitelist HOSE/HNX/UPCOM — 'hnx'->HNX, ' UPCOM '->UPCOM, sàn lạ 'HCX'->None "
       "(KHÔNG thành bước HOSE đoán)", got3 == ["HNX", None, "UPCOM"], f"{got3}")
    ck("live_exchange_fn: _raw_log=None trước connect (không ghi dnse_raw kế toán)",
       calls["raw_log"] is None, f"{calls['raw_log']!r}")
    ck("live_exchange_fn: tiếng ồn broker KHÔNG lên stdout (kênh máy đọc)", buf.getvalue() == "",
       repr(buf.getvalue()))
    ck("live_exchange_fn: MIKE_ADJFACTOR_NO_BQ=1 -> None, KHÔNG chạm broker",
       got2 is None and calls["connect"] == n_before, f"{got2} {calls}")
    del types
    n_conn = {"n": 0}

    class DeadSrc:
        _raw_log = "x"

        def connect(self):
            n_conn["n"] += 1
            raise RuntimeError("dnse down")

    saved = tb.get_quote_source
    try:
        tb.get_quote_source = lambda name: DeadSrc()
        fn = _REAL_LIVE_EXCHANGE_FN()
        got = [fn("AAA"), fn("BBB"), fn("CCC")]
    finally:
        tb.get_quote_source = saved
    ck("live_exchange_fn: connect HỎNG được nhớ — thử MỘT lần cho cả lượt, mọi mã None",
       got == [None, None, None] and n_conn["n"] == 1, f"{got} n={n_conn}")

    # (j) run_scan: dòng máy đọc, SCAN, rc, bảng bằng chứng; sàn tra LƯỜI (chỉ mã cần bước giá).
    class A:
        asof = "2026-08-28"; ex0 = "2026-06-01"; ex1 = "2026-08-28"; ex_days = 30
        lookback_days = 120; dev_tol = 0.003; min_run = 3; tickers = None; no_holdings = False

    s_pf, evs_pf, _tf = _pf({10: -100, 11: -100, 12: -100})
    s_dr, _e, _tf = _pf({}, closes=[(20000 + 100 * ((i * 3) % 7)) / (1.0 if i < 26 else 1.1)
                                    for i in range(30)])
    asked = []

    def scan(universe, rows, held):
        saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
                 det.cal.events, det.bq_max_session, det.live_exchange_fn)
        try:
            det.cohort_tickers = lambda a, b: universe
            det.bq_max_session = lambda: A.asof
            det.price_rows = lambda t, s_, e: rows
            det.held_map = lambda asof, **kw: held
            det.cal.feed_freshness = lambda: {"max_ingested": "2026-08-28 15:00:00",
                                              "max_public": "2026-08-28", "n": "36428"}
            det.cal.events = lambda t, since=None, until=None: [
                dict(e, ticker=tk) for tk in universe for e in evs_pf]
            det.live_exchange_fn = lambda: (lambda tk: asked.append(tk) or "UPCOM")
            b = io.StringIO()
            with redirect_stdout(b):
                rc = det.run_scan(A)
            return rc, b.getvalue()
        finally:
            (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session, det.live_exchange_fn) = saved

    rc, out = scan(["PFX", "REAL"], [{"tk": "PFX", **b} for b in s_pf]
                   + [{"tk": "REAL", **b} for b in s_dr], {"PFX": "SpaceX"})
    lines = out.splitlines()
    pf = [l for l in lines if l.startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|")]
    dr = [l for l in lines if l.startswith("ADJFACTOR_DRIFT|")]
    sc = [l for l in lines if l.startswith("ADJFACTOR_SCAN|")]
    ck("run_scan: dòng PRICE_FIELD_MISMATCH mang nhãn nắm THẬT",
       len(pf) == 1 and pf[0].startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|PFX|2026-08-20|1|tick_offset|")
       and pf[0].split("|")[7] == "SpaceX", f"{pf}")
    ck("run_scan: mã price-field KHÔNG có dòng DRIFT; DRIFT mã kia vẫn in",
       not any("|PFX|" in l for l in dr) and len(dr) == 1 and "|REAL|" in dr[0], f"{dr}")
    ck("run_scan: SCAN 7 trường, n_scanned GỒM price-field, n_drift KHÔNG",
       sc == ["ADJFACTOR_SCAN|2026-08-28|2|1|0|0|0"], f"{sc}")
    ck("run_scan: sàn chỉ tra cho mã cần bước giá (lười)", set(asked) == {"PFX"}, f"{asked}")
    tab = [l for l in lines if l.startswith("PFX ")]
    ck("run_scan: log có hàng bằng chứng price-field (r_obs, r_pred, cửa sổ, ex, luật)",
       len(tab) == 1 and "tick_offset" in tab[0] and "2026-08-20" in tab[0] and "SpaceX" in tab[0],
       f"{tab}")
    ck("run_scan: log có chứng từ price-field", any(l.startswith("   PFX: PRICE_FIELD_MISMATCH ")
                                                    for l in lines), f"{out[-500:]!r}")
    ck("run_scan: có DRIFT -> rc=10", rc == 10, f"rc={rc}")
    rc, out = scan(["PFX"], [{"tk": "PFX", **b} for b in s_pf], {})
    ck("chỉ có price-field (feed FRESH) -> rc=11, KHÔNG phải 0; SCAN 1|0|0|0|0",
       rc == 11 and "ADJFACTOR_SCAN|2026-08-28|1|0|0|0|0" in out.splitlines(), f"rc={rc}")
    # Đường fail-closed THẬT của run_scan (arch-review #2): sàn không biết ⇒ DRIFT y nguyên bản không-luật.
    s_hx, evs_hx, _tf = _pf({10: -200, 11: -200, 12: -200}, base=30000)

    def scan_ex(exch):
        saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
                 det.cal.events, det.bq_max_session, det.live_exchange_fn)
        try:
            det.cohort_tickers = lambda a, b: ["PFX"]
            det.bq_max_session = lambda: A.asof
            det.price_rows = lambda t, s_, e: [{"tk": "PFX", **b} for b in s_hx]
            det.held_map = lambda asof, **kw: {}
            det.cal.feed_freshness = lambda: {"max_ingested": "2026-08-28 15:00:00",
                                              "max_public": "2026-08-28", "n": "36428"}
            det.cal.events = lambda t, since=None, until=None: [dict(e, ticker="PFX") for e in evs_hx]
            det.live_exchange_fn = lambda: (lambda tk: exch)
            b = io.StringIO()
            with redirect_stdout(b):
                rc = det.run_scan(A)
            return rc, [l for l in b.getvalue().splitlines() if l.startswith("ADJFACTOR_")
                        and not l.startswith(("ADJFACTOR_FEED", "ADJFACTOR_SCAN"))]
        finally:
            (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session, det.live_exchange_fn) = saved

    _v0, p0 = det.scan_ticker(s_hx, evs_hx, 0.003, 3, A.ex0, tick_fn=None)
    rc, ln = scan_ex(None)
    ck("run_scan: sàn KHÔNG tra được -> DRIFT y nguyên bản không-luật (fail-closed ở đường production)",
       ln == [det.marker_drift("PFX", p0, "none")] and rc == 10, f"rc={rc} {ln}")
    rc, ln = scan_ex("HNX")
    ck("run_scan: sàn HNX (bước 100) -> −2 bước -> PRICE_FIELD_MISMATCH",
       len(ln) == 1 and ln[0].startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|PFX|"), f"{ln}")
    rc, ln = scan_ex("HOSE")
    ck("run_scan: cùng chuỗi, sàn HOSE (bước 50) -> −4 bước -> DRIFT y nguyên",
       ln == [det.marker_drift("PFX", p0, "none")], f"{ln}")
    # R1 ở đường production: `win0` = phiên đầu cụm (lookback 58 ngày ⇒ win0 2026-07-01 = D[10]).
    # Sự kiện phải nạp từ `load0` để biết ex-date ≤ win0; ex-date đó KHÔNG được vào đường hệ số.
    class A58(A):
        lookback_days = 58
    since_seen = []

    def scan_r1(extra, ser=None):
        saved = (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
                 det.cal.events, det.bq_max_session, det.live_exchange_fn)
        try:
            det.cohort_tickers = lambda a, b: ["PFX"]
            det.bq_max_session = lambda: A58.asof
            det.price_rows = lambda t, s_, e: [{"tk": "PFX", **b} for b in (ser or s_pf)]

            def evs(t, since=None, until=None):
                since_seen.append(since)
                return [dict(e, ticker="PFX") for e in list(evs_pf) + extra
                        if since < e["exright_date"] <= until]
            det.held_map = lambda asof, **kw: {}
            det.cal.feed_freshness = lambda: {"max_ingested": "2026-08-28 15:00:00",
                                              "max_public": "2026-08-28", "n": "36428"}
            det.cal.events = evs
            det.live_exchange_fn = lambda: (lambda tk: "UPCOM")
            b = io.StringIO()
            with redirect_stdout(b):
                det.run_scan(A58)
            return [l for l in b.getvalue().splitlines() if l.startswith("ADJFACTOR_")
                    and not l.startswith(("ADJFACTOR_FEED", "ADJFACTOR_SCAN"))]
        finally:
            (det.cohort_tickers, det.price_rows, det.held_map, det.cal.feed_freshness,
             det.cal.events, det.bq_max_session, det.live_exchange_fn) = saved
    ln = scan_r1([])
    ck("run_scan R1: win0 = phiên đầu cụm -> láng giềng trước cửa sổ -> PRICE_FIELD_MISMATCH",
       len(ln) == 1 and ln[0].startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|PFX|2026-08-20|1|tick_offset|"
                                          "2026-07-01|"), f"{ln}")
    ck("run_scan R1: sự kiện nạp từ load0 (= win0 − CUM_PAD_DAYS), không từ win0",
       since_seen[-1] == (date.fromisoformat("2026-07-01")
                          - timedelta(days=det.CUM_PAD_DAYS)).isoformat(), f"{since_seen}")
    ln = scan_r1([ev("2026-07-01", "ISS", "Cổ phiếu thưởng", 0.05)])
    ck("run_scan R1: ex-date = win0 (≤ win0) xen giữa láng giềng và cụm -> DRIFT (khác đoạn hệ số)",
       len(ln) == 1 and ln[0].startswith("ADJFACTOR_DRIFT|PFX|2026-08-20|"), f"{ln}")
    # NB6: r_pred của cụm (>= win0) KHÔNG đổi dù ex = win0 có vào đường hệ số hay không ⇒ KHÔNG dùng r_pred
    # để chứng minh "không vào đường hệ số" (từng là tautology). Phép thử thật là sự kiện KHÔNG tính được
    # ở đúng biên ex == win0: nếu lọt vào đường hệ số nó thành `unknown` ⇒ UNCOMPUTABLE/mất PFM oan.
    ln0 = scan_r1([ev("2026-07-01", "DIV", dps=0)])
    ln1 = scan_r1([ev("2026-07-01", "ISS", det.RIGHTS_METHOD, 0.2)])
    ck("Mk biên ex == win0: DIV 0đ / quyền mua (uncomputable) KHÔNG sinh UNCOMPUTABLE, dòng y nguyên bản "
       "chỉ có ex = win0 hợp lệ", not any(l.startswith("ADJFACTOR_UNCOMPUTABLE|") for l in ln0 + ln1)
       and ln0 == ln1 == scan_r1([ev("2026-07-01", "ISS", "Cổ phiếu thưởng", 0.05)]), f"{ln0} / {ln1}")
    # Mk thật sự bị giết ở chuỗi SẠCH (không cụm lệch): ex = win0 uncomputable lọt vào đường hệ số thì
    # `unknown` ⇒ UNCOMPUTABLE oan 1 ngày; đúng ra nó chỉ là NGÀY trong pre_ex ⇒ AGREE (không dòng nào).
    s_clean, _e, _t = _pf({})
    for what, e_ in (("quyền mua", ev("2026-07-01", "ISS", det.RIGHTS_METHOD, 0.2)),
                     ("DIV 0đ", ev("2026-07-01", "DIV", dps=0))):
        lnc = scan_r1([e_], ser=s_clean)
        ck(f"Mk chuỗi sạch: {what} ex == win0 -> KHÔNG UNCOMPUTABLE (AGREE, không dòng nào)", lnc == [], f"{lnc}")
    ln2 = scan_r1([ev("2026-07-02", "ISS", det.RIGHTS_METHOD, 0.2)])
    ck("Mk đối chứng: cùng quyền mua nhưng ex = win0 + 1 (trong cửa sổ) -> UNCOMPUTABLE",
       any(l.startswith("ADJFACTOR_UNCOMPUTABLE|PFX|2026-07-02|") for l in ln2), f"{ln2}")

    # NB2 (hồi quy bug TIP): sự kiện ex <= win0 KHÔNG tính được hệ số (quyền mua; DIV 0đ) chỉ được thành
    # NGÀY trong pre_ex — không được vào đường hệ số ⇒ không UNCOMPUTABLE, không partial, dòng y nguyên.
    base = scan_r1([])
    ln = scan_r1([ev("2026-06-08", "ISS", det.RIGHTS_METHOD, 0.2), ev("2026-06-09", "DIV", dps=0)])
    ck("NB2 run_scan: ex <= win0 uncomputable (quyền mua, DIV 0đ) -> KHÔNG UNCOMPUTABLE/partial, dòng "
       "PRICE_FIELD_MISMATCH y nguyên bản không có sự kiện đó",
       ln == base and len(ln) == 1 and ln[0].startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|PFX|")
       and not any(l.startswith("ADJFACTOR_UNCOMPUTABLE|") for l in ln), f"{ln} vs {base}")
    # Cùng sự kiện đó nhưng ex > win0 (trong cửa sổ) thì PHẢI fail-closed — đối chứng cho test trên.
    ln = scan_r1([ev("2026-07-03", "ISS", det.RIGHTS_METHOD, 0.2)])
    ck("NB2 đối chứng: quyền mua ex > win0 -> UNCOMPUTABLE/DRIFT partial (không đổi nhãn price-field)",
       any(l.startswith("ADJFACTOR_UNCOMPUTABLE|PFX|2026-07-03|") for l in ln)
       and not any(l.startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|") for l in ln), f"{ln}")

    ck("price-field mã không nắm mang nhãn `none`",
       any(l.startswith("ADJFACTOR_PRICE_FIELD_MISMATCH|PFX|") and l.split("|")[7] == "none"
           for l in out.splitlines()), f"{out[-400:]!r}")


PF_FREE = "ADJFACTOR_PRICE_FIELD_MISMATCH|DVN|2026-09-11|1|tick_offset|2026-06-19|2026-06-23|none|-0.010122"
PF_FREE2 = "ADJFACTOR_PRICE_FIELD_MISMATCH|SHC|2026-09-09|1|stale_price|2026-06-30|2026-07-09|none|-0.121003"
PF_HELD = ("ADJFACTOR_PRICE_FIELD_MISMATCH|DRI|2026-09-22|1|tick_offset|2026-09-10|2026-09-14"
           "|SpaceX,ZaloPay|-0.007002")
PF_UNK = "ADJFACTOR_PRICE_FIELD_MISMATCH|UNK|2026-09-22|1|tick_offset|2026-09-10|2026-09-14|unknown|-0.007"
PF_SKIP = "ADJFACTOR_PRICE_FIELD_MISMATCH|SKP|2026-09-22|1|tick_offset|2026-09-10|2026-09-14|skipped|-0.007"


def t_alert_price_field(tz_label, env_tz):
    print(f"\n[18] alert.sh — PRICE_FIELD_MISMATCH  (TZ: {tz_label})")
    tail = "\n".join([FEED_FRESH, SCAN]) + "\n"
    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        state = os.path.join(tmp, "state", "adjfactor_drift_alerted.json")
        notify = os.path.join(sink, "notify.txt")
        busf = os.path.join(sink, "bus.jsonl")

        # (a) chỉ price-field — KỂ CẢ mã ĐANG NẮM — feed FRESH: bus có, Discord KHÔNG, không khoá.
        r = _run_alert(tmp, tgt, "\n".join([PF_FREE, PF_FREE2, PF_HELD, PF_UNK]) + "\n" + tail, env_tz)
        ck(f"[{tz_label}] price-field-only (gồm mã nắm + unknown) -> KHÔNG gửi Discord, rc=0",
           r.returncode == 0 and not os.path.exists(notify), f"rc={r.returncode} {r.stderr[-300:]!r}")
        ck(f"[{tz_label}] price-field-only: log nói rõ lý do im lặng",
           "4 ma LECH TRUONG GIA" in r.stderr, f"{r.stderr[-300:]!r}")
        ck(f"[{tz_label}] price-field-only: log đếm ĐÚNG 2 mã có thể đang nắm (DRI + unknown), không nói 'khong ma nao'",
           "2 ma lech truong gia CO THE DANG NAM" in r.stderr, f"{r.stderr[-300:]!r}")
        bus = [json.loads(l) for l in open(busf) if l.strip()] if os.path.exists(busf) else []
        ck(f"[{tz_label}] price-field-only vẫn ghi bus với ĐỦ danh sách",
           len(bus) == 1 and bus[0].get("price_field_mismatch") == "4"
           and bus[0].get("price_field_mismatch_markers") == [PF_FREE, PF_FREE2, PF_HELD, PF_UNK],
           f"{bus}")
        ck(f"[{tz_label}] price-field KHÔNG sinh khoá de-dup",
           not os.path.exists(state) or json.load(open(state)) == {},
           f"{open(state).read() if os.path.exists(state) else None}")

        # (b) price-field + DRIFT thật -> Discord; price-field gộp MỘT dòng info, không TODO/Winston.
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_FREE, PF_FREE, PF_HELD, PF_UNK, PF_SKIP]) + "\n" + tail,
                       env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] DRIFT thật + price-field -> có gửi Discord", r.returncode == 10 and msg,
           f"rc={r.returncode} {r.stderr[-300:]!r}")
        info = [l for l in msg.splitlines() if "Lệch trường giá" in l]
        ck(f"[{tz_label}] price-field gộp đúng MỘT dòng info chứa cả 3 mã",
           len(info) == 1 and "DVN" in info[0] and "DRI" in info[0] and "UNK" in info[0], f"{info}")
        ck(f"[{tz_label}] price-field held=unknown -> nêu tên + 'KHÔNG TRA ĐƯỢC vị thế'",
           info and "**UNK**" in info[0] and "KHÔNG TRA ĐƯỢC vị thế" in info[0], f"{info}")
        ck(f"[{tz_label}] price-field mã không nắm KHÔNG in đậm", info and "**DVN**" not in info[0],
           f"{info}")
        ck(f"[{tz_label}] price-field held=skipped KHÔNG thành 'ĐANG NẮM LIVE: skipped'",
           info and "SKP" in info[0] and "**SKP**" not in info[0] and "LIVE: skipped" not in msg, f"{info}")
        ck(f"[{tz_label}] price-field mã nắm mang nhãn LIVE trong dòng info",
           info and "**DRI**" in info[0] and "ĐANG NẮM LIVE: SpaceX,ZaloPay" in info[0], f"{info}")
        todo = msg.split("**Việc cần làm:**", 1)[-1].split("_Quét", 1)[0]
        ck(f"[{tz_label}] price-field KHÔNG vào 'Việc cần làm'", "DVN" not in todo and "DRI" not in todo,
           f"{todo!r}")
        ck(f"[{tz_label}] price-field KHÔNG thành dòng lệch '• **DVN**'/'• **DRI**'",
           "• **DVN**" not in msg and "• **DRI**" not in msg)
        ck(f"[{tz_label}] footer đếm price-field riêng", "4 lệch trường giá" in msg, f"{msg[-400:]!r}")
        ck(f"[{tz_label}] state chỉ có khoá DRIFT", sorted(json.load(open(state))) == ["FPT|2026-09-21"],
           f"{open(state).read()}")
        os.remove(notify)

        # (c) price-field + feed STALE -> gửi vì FEED, price-field vẫn KHÔNG giao Winston.
        stale_tail = "\n".join([FEED_STALE, SCAN]) + "\n"
        r = _run_alert(tmp, tgt, PF_HELD + "\n" + stale_tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] price-field + feed STALE -> VẪN gửi (feed là cảnh báo riêng)",
           r.returncode == 10 and "KHÔNG TƯƠI" in msg, f"rc={r.returncode}")
        ck(f"[{tz_label}] price-field KHÔNG bật 'Vendor thiếu hệ số' (Winston)",
           "Vendor thiếu hệ số điều chỉnh" not in msg)
        os.remove(notify)

        # (d) khoá DRIFT CŨ `mã|ex` của mã nay là price-field bị XOÁ (để DRIFT thật sau đó không bị chặn);
        # --dry-run thì KHÔNG xoá.
        st = json.load(open(state))
        today = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                               capture_output=True, text=True).stdout.strip()
        st["DRI|2026-09-22"] = today
        json.dump(st, open(state, "w"))
        r = _run_alert(tmp, tgt, PF_HELD + "\n" + tail, env_tz, args=("1234", "--dry-run"))
        ck(f"[{tz_label}] price-field --dry-run KHÔNG xoá khoá cũ",
           "DRI|2026-09-22" in json.load(open(state)), f"{open(state).read()}")
        r = _run_alert(tmp, tgt, PF_HELD + "\n" + tail, env_tz)
        ck(f"[{tz_label}] lượt price-field XOÁ khoá DRIFT cũ `DRI|ex`, không gửi Discord",
           "DRI|2026-09-22" not in json.load(open(state)) and not os.path.exists(notify),
           f"rc={r.returncode} {open(state).read()}")
        ck(f"[{tz_label}] xoá khoá price-field KHÔNG đụng khoá khác",
           "FPT|2026-09-21" in json.load(open(state)), f"{open(state).read()}")
        drift_dri = REAL_DRIFT_BEFORE["DRI"]
        r = _run_alert(tmp, tgt, drift_dri + "\n" + tail, env_tz)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] price-field -> DRIFT thật về sau báo như MỚI, không bị khoá cũ chặn",
           r.returncode == 10 and "• **DRI**" in msg and "ĐANG NẮM LIVE" in msg,
           f"rc={r.returncode} {r.stderr[-300:]!r}")
        os.remove(notify)

        # (e) price-field + awaiting cùng lượt: hai dòng info RIÊNG, cả hai im khi không có gì khác.
        r = _run_alert(tmp, tgt, "\n".join([PF_FREE, AW_FREE]) + "\n" + tail, env_tz)
        ck(f"[{tz_label}] price-field + awaiting không nắm -> KHÔNG gửi Discord, rc=0",
           r.returncode == 0 and not os.path.exists(notify), f"rc={r.returncode}")
        ck(f"[{tz_label}] price-field mã KHÔNG nắm -> log KHÔNG nói 'CO THE DANG NAM'",
           "CO THE DANG NAM" not in r.stderr and "khong ma awaiting nao" in r.stderr, f"{r.stderr[-300:]!r}")

    # (f) xoá khoá hỏng ⇒ ép gửi Discord kèm LỖI THẬT (cùng cơ chế B1 của awaiting).
    with tempfile.TemporaryDirectory() as tmp:
        tgt = _sandbox(tmp)
        sink = os.path.join(tmp, "sink")
        notify = os.path.join(sink, "notify.txt")
        sdir = os.path.join(tmp, "state")
        os.makedirs(sdir)
        state = os.path.join(sdir, "adjfactor_drift_alerted.json")
        today = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                               capture_output=True, text=True).stdout.strip()
        json.dump({"DVN|2026-09-11": today}, open(state, "w"))
        os.chmod(sdir, 0o555)
        try:
            r = _run_alert(tmp, tgt, PF_FREE + "\n" + tail, env_tz)
        finally:
            os.chmod(sdir, 0o755)
        msg = open(notify).read() if os.path.exists(notify) else ""
        ck(f"[{tz_label}] price-field: xoá khoá cũ HỎNG -> ép gửi Discord kèm lỗi thật",
           r.returncode == 10 and "STATE DE-DUP KHÔNG XOÁ ĐƯỢC" in msg and "DVN|2026-09-11" in msg,
           f"rc={r.returncode} {r.stderr[-300:]!r}")


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
        t_awaiting()
        t_price_field()
        t_price_field_window()
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
            t_alert_awaiting(label, envd)
            t_alert_price_field(label, envd)
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
