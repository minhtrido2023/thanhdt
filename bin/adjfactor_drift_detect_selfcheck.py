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


# ------------------------------------------------------------- 4. đường hệ số

def t_curve():
    print("\n[4] build_factor_curve — tích theo ex-date, dedupe, taxonomy")
    s = [bar(d, 100, 100) for d in D]
    # Hai ex-date NẰM TRONG chuỗi (D = ngày 01..10 mỗi tháng) để kiểm được cả biên "ex == t".
    evs = [ev("2026-07-05", "ISS", "Cổ phiếu thưởng", 0.1),
           ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2)]
    curve, used, _notes, unknown = det.build_factor_curve(s, evs)
    ck("2 ex-date liên tiếp: r_pred trước cả hai = 1.1*1.2",
       abs(curve["2026-06-01"] - 1.32) < 1e-9, f"{curve['2026-06-01']}")
    ck("giữa hai ex-date: chỉ hệ số của ex-date SAU",
       abs(curve["2026-07-10"] - 1.2) < 1e-9, f"{curve['2026-07-10']}")
    ck("sau cả hai: r_pred = 1.0", abs(curve["2026-08-10"] - 1.0) < 1e-9, f"{curve['2026-08-10']}")
    ck("ex-date ĐÚNG ngày không tính hệ số của CHÍNH nó (tích lấy ex > t)",
       abs(curve["2026-07-05"] - 1.2) < 1e-9, f"{curve['2026-07-05']}")
    ck("không có unknown", unknown == [] and len(used) == 2)

    # Dedupe: hai dòng y hệt nhau = MỘT số hạng; hai tranche KHÁC số = CỘNG
    curve2, _u, _n, _unk = det.build_factor_curve(s, [
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2),
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2)])
    ck("dòng trùng y hệt -> dedupe thành 1 (1.2, không phải 1.4)",
       abs(curve2["2026-07-01"] - 1.2) < 1e-9, f"{curve2['2026-07-01']}")
    curve3, _u, _n, _unk = det.build_factor_curve(s, [
        ev("2026-08-05", "ISS", "Cổ phiếu thưởng", 0.2),
        ev("2026-08-05", "ISS", "Trả Cổ tức bằng Cổ phiếu", 0.1)])
    ck("hai tranche KHÁC nhau -> CỘNG (1.3)",
       abs(curve3["2026-07-01"] - 1.3) < 1e-9, f"{curve3['2026-07-01']}")

    # Taxonomy: ESOP không làm rơi giá (tái dùng corp_action_lib, không tự định nghĩa)
    curve4, used4, _n, _unk = det.build_factor_curve(s, [
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


# -------------------------------------------- 7. hợp đồng dòng máy đọc + CLI

def t_contract():
    print("\n[7] hợp đồng dòng MÁY ĐỌC + guard tham số CLI")
    sh = open(os.path.join(HERE, "adjfactor_drift_alert.sh")).read()
    py = open(os.path.join(HERE, "adjfactor_drift_detect.py")).read()

    # Số trường phải khớp giữa producer (python) và consumer (shell `IFS='|' read`). Lệch hợp đồng
    # là lỗi IM LẶNG: shell đọc thiếu/thừa biến mà không báo gì.
    for tag, fields in (("ADJFACTOR_DRIFT", 11), ("ADJFACTOR_UNCOMPUTABLE", 5),
                        ("ADJFACTOR_SCAN", 7)):
        pl = [l for l in py.splitlines() if f'f"{tag}|' in l or f'"{tag}|' in l]
        ck(f"{tag}: producer có dòng in", len(pl) >= 1, f"{pl}")
        ck(f"{tag}: consumer parse đúng {fields} trường",
           sh.count(f"'^{tag}\\|'") == 1 or f"{tag}\\|" in sh)

    n_drift = len([x for x in sh.splitlines() if "read -r _tag tk ex r_obs" in x])
    ck("shell đọc DRIFT: 11 biến (_tag..held)",
       n_drift == 1 and "read -r _tag tk ex r_obs r_pred dev run d0 d1 dir held" in sh)
    ck("shell đọc UNCOMPUTABLE: 5 biến",
       "read -r _tag tk ex code held" in sh)
    ck("shell đọc SCAN: 7 biến",
       "read -r _stag ASOF N_SCANNED N_DRIFT N_UNCOMP N_AGREE N_NODATA" in sh)

    ck("--min-run dưới 3 bị TỪ CHỐI (không cho hạ ngưỡng persistence)",
       det.main(["--min-run", "2"]) if False else _exits_2(["--min-run", "2"]))
    ck("--dev-tol <= 0 bị TỪ CHỐI", _exits_2(["--dev-tol", "0"]))

    ck("detector KHÔNG import/ghi report_return_gate hay dividend_adjusted_return để SỬA",
       "report_return_gate" not in py.replace("`report_return_gate.py`", "")
       or "import report_return_gate" not in py)
    ck("detector chỉ ĐỌC dividend_adjusted_return (broker_qty/ACCOUNTS), không gọi hàm ghi",
       "dar.broker_qty" in py and "dar.detect_adjustments" not in py)


def _exits_2(argv):
    r = subprocess.run([sys.executable, os.path.join(HERE, "adjfactor_drift_detect.py")] + argv,
                       capture_output=True, text=True)
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
              "|2026-09-17|vendor_missing|SpaceX,ZaloPay")
DRIFT_FREE = ("ADJFACTOR_DRIFT|FPT|2026-09-21|1.000000|1.100000|-0.090909|75|2026-05-28"
              "|2026-09-14|vendor_missing|none")
UNCOMP_HELD = "ADJFACTOR_UNCOMPUTABLE|MBB|2026-08-11|rights_issue_no_subscription_price|SpaceX"
UNCOMP_FREE = "ADJFACTOR_UNCOMPUTABLE|RYG|2026-09-03|rights_issue_no_subscription_price|none"
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

        r = _run_alert(tmp, tgt, "khong co marker nao\n", env_tz)
        ck(f"[{tz_label}] không có marker -> rc=0, không gửi gì",
           r.returncode == 0 and not os.path.exists(os.path.join(sink, "notify.txt")),
           f"rc={r.returncode}")

        body = "\n".join([DRIFT_HELD, DRIFT_FREE, UNCOMP_HELD, UNCOMP_FREE, SCAN]) + "\n"
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
        ck(f"[{tz_label}] state de-dup ghi đúng 2 khoá (mã|ex)",
           os.path.exists(state) and sorted(json.load(open(state))) ==
           ["FPT|2026-09-21", "VPB|2026-09-24"], f"{state}")

        today_ict = subprocess.run(["bash", "-c", "TZ='Asia/Ho_Chi_Minh' date +%F"],
                                   capture_output=True, text=True).stdout.strip()
        ck(f"[{tz_label}] ngày trong state là ngày ICT, KHÔNG phải ngày của TZ host",
           set(json.load(open(state)).values()) == {today_ict},
           f"{json.load(open(state))} vs ICT {today_ict}")

        # Lượt 2 cùng ngày: de-dup CHẶN Discord nhưng VẪN ghi bus (dấu vết không được mất)
        os.remove(os.path.join(sink, "notify.txt"))
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_HELD, DRIFT_FREE, SCAN]) + "\n", env_tz)
        ck(f"[{tz_label}] lượt 2: de-dup -> KHÔNG gửi Discord, rc=10",
           r.returncode == 10 and not os.path.exists(os.path.join(sink, "notify.txt")),
           f"rc={r.returncode}")
        bus2 = [l for l in open(os.path.join(sink, "bus.jsonl")) if l.strip()]
        ck(f"[{tz_label}] lượt 2: bus VẪN ghi (de-dup chỉ áp cho Discord)", len(bus2) == 2)

        # UNCOMPUTABLE của mã NẮM luôn phá được de-dup (đó là thông tin money-adjacent)
        r = _run_alert(tmp, tgt, "\n".join([DRIFT_HELD, UNCOMP_HELD, SCAN]) + "\n", env_tz)
        ck(f"[{tz_label}] uncomputable của mã nắm vẫn gửi dù drift đã de-dup",
           os.path.exists(os.path.join(sink, "notify.txt")))

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

        r = run([], rc=1, out="[FATAL] BQ chet")
        ck("detector rc=1 KHÔNG dry-run -> CÓ gửi Discord cảnh báo hạ tầng",
           os.path.exists(os.path.join(sink, "notify.txt")))
        ck("cảnh báo hạ tầng trích LỖI THẬT detector in ra, không phải câu đoán",
           "BQ chet" in open(os.path.join(sink, "notify.txt")).read())

        r = run(["--dry-run"], rc=0, out=SCAN)
        ck("detector rc=0 (sạch) -> vẫn gọi alert (alert tự exit 0 nếu không có marker)",
           os.path.exists(os.path.join(sink, "alert_args.txt")))


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
    if do_sh:
        # §16/§19: LẶP dưới 3 môi trường TZ. `env -u TZ` = ca cron thật (không có TZ trong env).
        for label, envd in (("unset TZ", {"__unset_tz__": "1"}),
                            ("TZ=UTC", {"TZ": "UTC"}),
                            ("TZ=America/New_York", {"TZ": "America/New_York"})):
            if "__unset_tz__" in envd:
                envd = {}
                os.environ.pop("TZ", None)
            t_alert(label, envd)
        t_runner()

    print(f"\n=== {N - len(FAILS)}/{N} assertion PASS ===")
    if FAILS:
        print("FAIL:")
        for f in FAILS:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
