#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck nhánh BROKER của corp-action (job Taylor_20261003_033512).

Phủ:
  A. Detector PURE (`corp_action_broker_detect`) — ca lành TPB/VPB/BID-dở, và MỌI lớp giả mạo mà
     docstring hứa loại: mua/lệnh ma (giá vốn tăng), bán trong cửa sổ, credit giữa phiên/sau nửa
     đêm (không có bằng chứng ex-date), 1 bản ghi, gói vay dở, quyền mua (giá không khớp KL),
     tài khoản giữ mã mà không được credit, chân tiền lệch giữa tài khoản/với vendor, thiếu giá
     cum, CP mới bán được, lệnh khớp muộn, hệ số vượt biên registry.
  B. `corp_action_auto_confirm.run_broker` trong SANDBOX (tmpdir; subprocess.run bị stub — 0 bus/
     Discord thật; KHÔNG chạm data/ production): shadow không ghi registry, live ghi + đọc lại
     được, idempotent (chạy lại 0 dòng sổ mới, 0 bus mới), mơ hồ ⇒ đúng 1 câu hỏi, registry có
     sẵn ⇒ bỏ qua, off ⇒ im, mode lạ ⇒ shadow, dry-run ⇒ 0 ghi, record cũ hỏng ⇒ rc=1 + 0 ghi.
  C. `exdate_frame` fallback registry — mặc định TẮT (hành vi cũ), bật ⇒ TPB được credited kèm
     chân tiền 500; record PROPOSED không bao giờ được dùng.
  D. `--replay` (đọc dnse_raw THẬT + BQ Price, chỉ ĐỌC): đúng 7 sự kiện thật CONFIRMABLE, ex-date
     khớp registry, hệ số tái tạo đúng KL broker, 0 ứng viên giả.
  E. `--mutations`: sửa tạm từng điều kiện trong file thật của worktree, chạy lại A–C ở tiến
     trình con, mong FAIL; khôi phục + kiểm sha256 sau mỗi đột biến. TỪ CHỐI (rc≠0) khi chạy từ
     cây canonical mike/bin; báo đột biến nào chỉ bị giết bởi crash (không assertion có tên).
  test_v5 (arch-review v4, 12 mục): _exchange_fn THẬT connect()+không ghi dnse_raw, broker crash ⇒
     vendor vẫn chạy+ghi, khoá ⇒ question 1 lần/ngày, lịch vendor thiếu/_FAILED ⇒ MƠ HỒ, lỗi hỏi N9
     không mất lô vendor, sổ hỏng ⇒ vẫn hỏi, khoá ASKED có id record, bq timeout, tỉ lệ lệch broker.

Chạy: python3 bin/corp_action_broker_detect_selfcheck.py [--replay] [--mutations]
Theo §16/§19: chạy thêm dưới `env -u TZ` và `TZ=America/New_York` — kết quả phải y hệt.
"""
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time as _time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import corp_action_broker_detect as BD  # noqa: E402
import corp_action_auto_confirm as cac  # noqa: E402
import corp_actions as CA  # noqa: E402
import exdate_frame as XF  # noqa: E402

for _m in (BD, cac, CA, XF):
    assert os.path.dirname(os.path.abspath(_m.__file__)) == HERE, \
        f"{_m.__name__} nạp từ {_m.__file__}, KHÔNG phải {HERE} — sys.path shadow bản worktree"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name if cond else (name, detail))
    if not cond:   # __stdout__: vẫn hiện khi test đang redirect_stdout (run_mutations đọc tên từ đây)
        print(f"❌ FAIL: {name} — {detail}", file=sys.__stdout__, flush=True)


_CRASHED = object()


def _call(name, fn, *a, **k):
    """Gọi fn; ngoại lệ ⇒ FAIL CÓ TÊN `name` thay vì làm cả selfcheck nổ — đột biến khiến code ném
    phải hiện ra là assertion nào bắt (arch-review v4: kill phải bởi assertion có tên, không chỉ crash)."""
    try:
        return fn(*a, **k)
    except Exception as e:      # noqa: BLE001
        check(name, False, f"ném {type(e).__name__}: {e}")
        return _CRASHED


# ─────────────────────────────────────────────────────────────── dựng bản ghi DNSE giả ──
D, PREV, EX = "2026-10-01", "2026-09-30", "2026-10-02"     # Thứ Năm → Thứ Sáu (phiên kế tiếp)
A1, A2 = ("0002023347", "SpaceX"), ("0001743768", "ZaloPay")
_TMPDIRS = []


def _mkdtemp(prefix):
    t = tempfile.mkdtemp(prefix=prefix)
    _TMPDIRS.append(t)
    return t


atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TMPDIRS])


def lot(lid, q, cost, mkt, mod="2026-10-01T12:15:00Z", trade=None, closed=0, accum=None,
        acct=A1[0], sym="TPB"):
    return {"id": lid, "symbol": sym, "accountNo": acct, "openQuantity": q,
            "tradeQuantity": q if trade is None else trade, "closedQuantity": closed,
            "accumulateQuantity": (q + closed) if accum is None else accum,
            "costPrice": cost, "marketPrice": mkt, "modifiedDate": mod}


def snap(ts, *lots_):
    by = {}
    for x in lots_:
        by.setdefault(x["symbol"], []).append(x)
    return (ts, by)


PRE_MOD = "2026-09-30T12:15:46.038358Z"          # 19:15 ICT 09-30 (cập nhật giá đêm trước)
CR_MOD = "2026-10-01T11:52:12.319371Z"           # 18:52 ICT 10-01 (credit)


def tpb_series(post_n=3, post_at="19:03", q1=230, cost1=14173.913, mkt1=12100, trade1=200,
               closed1=0, accum1=None, pre_ts=None, acct=A1[0], q0=200, cost0=16800, mkt0=14450):
    pre = lot(2674331, q0, cost0, mkt0, PRE_MOD, acct=acct, accum=q0)
    post = lot(2674331, q1, cost1, mkt1, CR_MOD, trade=trade1, closed=closed1,
               accum=(q1 if accum1 is None else accum1), acct=acct)
    pre_ts = pre_ts or [f"{PREV}T23:30:04", f"{D}T04:54:17", f"{D}T11:16:29"]
    s = [snap(t, pre) for t in pre_ts if t < f"{D}T{post_at}"]
    hh, mm = post_at.split(":")
    for i in range(post_n):
        s.append(snap(f"{D}T{hh}:{int(mm) + i:02d}:01", post))
    return s


def DEC(*a, **k):
    """decide() với sàn HOSE mặc định cho ca test (sàn là chốt riêng, kiểm ở X1–X3)."""
    k.setdefault("exchange", "HOSE")
    return BD.decide(*a, **k)


def V(series, day=D, fills=()):
    return BD.account_evidence(series, "TPB", day, fills)["verdict"]


def test_A():
    ev = BD.account_evidence(tpb_series(), "TPB", D)
    check("A1 TPB tài khoản CONFIRMABLE", ev["verdict"] == BD.CONFIRMABLE, ev)
    check("A1b chân tiền 500 suy từ giá vốn", ev.get("cash_leg") == 500.0, ev.get("cash_leg"))
    dec = DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400)
    check("A2 TPB quyết định CONFIRMABLE ×1.15", dec["verdict"] == BD.CONFIRMABLE
          and dec.get("qty_multiplier") == 1.15, dec.get("why"))
    rec = BD.build_record(dec, "2026-10-01T19:25:00+07:00")
    v = CA.validate(rec)
    check("A3 record qua validate(), CONFIRMED, chân tiền 500, ex phiên kế tiếp",
          v["_status"].startswith("CONFIRMED") and v["cash_leg_vnd_per_share"] == 500.0
          and v["ex_date"] == EX and rec["provenance"] == "broker", v)
    check("A3b broker_effective_ts = ts bản ghi đầu trạng thái mới (19:03:01 ICT → UTC), KHÔNG "
          "phải modifiedDate", rec["broker_effective_ts"] == "2026-10-01T12:03:01",
          rec["broker_effective_ts"])
    txt = " ".join(rec["evidence"])
    check("A3c evidence không khẳng định điều chưa kiểm (§29: 'đứng yên', 'credit None')",
          "đứng yên" not in txt and "None" not in txt and "giả thuyết hệ số 1 bị bác" in txt, txt)

    # mua / lệnh ma: KL tăng + giá vốn TĂNG
    check("A4 mua (giá vốn tăng) ⇒ NOT_CANDIDATE",
          V(tpb_series(cost1=(200 * 16800 + 30 * 14400) / 230, mkt1=14400)) == BD.NOT_CANDIDATE)
    check("A5 lệnh ma 1cp giá 100đ (giá vốn vẫn tăng) ⇒ NOT_CANDIDATE",
          V(tpb_series(q1=201, cost1=(200 * 16800 + 1 * 100) / 201)) == BD.NOT_CANDIDATE)
    check("A5b KL GIẢM ⇒ NOT_CANDIDATE", V(tpb_series(q1=190, cost1=16800)) == BD.NOT_CANDIDATE)
    check("A6 có bán trong cửa sổ ⇒ AMBIGUOUS", V(tpb_series(closed1=10, accum1=240)) == BD.AMBIGUOUS)
    check("A6b closedQuantity đổi (dù accum khớp) ⇒ AMBIGUOUS",
          V(tpb_series(closed1=10)) == BD.AMBIGUOUS)
    e = BD.account_evidence(tpb_series(post_at="11:20"), "TPB", D)
    check("A7 KL mới thấy lần đầu GIỮA PHIÊN (ts 11:20) ⇒ AMBIGUOUS",
          e["verdict"] == BD.AMBIGUOUS and "TRƯỚC giờ đóng cửa" in e["why"], e.get("why"))
    # B1 arch-review: KL đổi 11:16, rồi đêm DNSE refresh modifiedDate (KL không đổi) ⇒ vẫn MƠ HỒ
    mid = tpb_series(post_at="11:20", post_n=2) + tpb_series(post_at="19:13", post_n=2)[-2:]
    e = BD.account_evidence(mid, "TPB", D)
    check("A7b KL đổi giữa phiên + refresh đêm ⇒ AMBIGUOUS (thời điểm theo ts, không modifiedDate)",
          e["verdict"] == BD.AMBIGUOUS and "TRƯỚC giờ đóng cửa" in e["why"], e.get("why"))
    check("A8 không có bản ghi nào của phiên D ⇒ NOT_CANDIDATE",
          V(tpb_series(), day="2026-10-02") == BD.NOT_CANDIDATE)
    e = BD.account_evidence(tpb_series(pre_ts=["2026-09-28T23:30:04"]), "TPB", D)
    check("A8b bản ghi trạng thái cũ từ 09-28 (trước phiên liền trước 09-30) ⇒ AMBIGUOUS khoảng trống",
          e["verdict"] == BD.AMBIGUOUS and "khoảng trống" in e["why"], e.get("why"))
    check("A8c trạng thái cũ chỉ có ở phiên liền trước ⇒ vẫn CONFIRMABLE (VHM 08-05)",
          V(tpb_series(pre_ts=[f"{PREV}T19:10:12"])) == BD.CONFIRMABLE)
    check("A9 mới 1 bản ghi sau credit ⇒ INSUFFICIENT", V(tpb_series(post_n=1)) == BD.INSUFFICIENT)
    dup = tpb_series(post_n=1) + [(f"{D}T19:03:01", tpb_series(post_n=1)[-1][1])]
    check("A9b 2 bản ghi CÙNG GIÂY = 1 lần đọc ⇒ INSUFFICIENT", V(dup) == BD.INSUFFICIENT)
    check("A10 CP mới bán được ngay (trade > KL trước) ⇒ AMBIGUOUS",
          V(tpb_series(trade1=230)) == BD.AMBIGUOUS)
    fills = [(BD.modified_ict("2026-10-01T07:00:00Z"), 30, "NB")]
    check("A11 sổ lệnh có khớp sau bản ghi trước credit ⇒ AMBIGUOUS",
          V(tpb_series(), fills=fills) == BD.AMBIGUOUS)
    early_fill = [(BD.modified_ict("2026-10-01T02:00:00Z"), 30, "NB")]   # 09:00 < bản ghi 11:16
    check("A11b khớp TRƯỚC bản ghi trước-credit không làm hỏng",
          V(tpb_series(), fills=early_fill) == BD.CONFIRMABLE)
    check("A12 accumulateQuantity lệch KL ⇒ AMBIGUOUS", V(tpb_series(accum1=231)) == BD.AMBIGUOUS)
    frac5 = BD.modified_ict("2026-09-09T11:45:22.23138Z")
    check("A13 modifiedDate 5 chữ số thập phân parse được (VIB)",
          frac5 is not None and frac5.hour == 18 and frac5.minute == 45, frac5)
    nano = BD.modified_ict("2026-08-14T12:09:00.785778421Z")
    check("A13b modifiedDate nano giây parse được", nano is not None and nano.hour == 19, nano)
    check("A13c chân tiền không tròn đồng (500,3đ/cp) ⇒ AMBIGUOUS",
          V(tpb_series(cost1=(200 * 16800 - 200 * 500.3) / 230)) == BD.AMBIGUOUS)

    # mỗi lô (loan package)
    def two(ts, a, b):
        return snap(ts, a, b)
    p1, p2 = lot(1, 100, 16800, 14450), lot(2, 100, 16800, 14450)
    c1 = lot(1, 115, 14173.913, 12100, trade=100, accum=115)
    c2_bad = lot(2, 115, 14000.0, 12100, trade=100, accum=115)          # chân tiền lô khác
    pre2 = [two(f"{PREV}T23:30:04", p1, p2), two(f"{D}T11:16:29", p1, p2)]
    e = BD.account_evidence(pre2 + [two(f"{D}T19:03:01", c1, c2_bad), two(f"{D}T19:04:01", c1, c2_bad)],
                            "TPB", D)
    check("A27 hai lô đổi với chân tiền KHÁC nhau ⇒ AMBIGUOUS", e["verdict"] == BD.AMBIGUOUS
          and "KHÔNG cùng một sự kiện" in e["why"], e.get("why"))
    c3 = lot(3, 115, 14173.913, 12100, trade=100, accum=115)
    e = _call("A28 id lô đổi ⇒ AMBIGUOUS", BD.account_evidence,
              pre2 + [two(f"{D}T19:03:01", c1, c3), two(f"{D}T19:04:01", c1, c3)], "TPB", D)
    if e is not _CRASHED:
        check("A28 id lô đổi ⇒ AMBIGUOUS", e["verdict"] == BD.AMBIGUOUS and "id lô" in e["why"],
              e.get("why"))

    # ── decide ──
    mbb = DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400 * 1.12)
    check("A14 giá không khớp hệ số KL (quyền mua/khác sự kiện) ⇒ AMBIGUOUS, nói rõ KL∩giá rỗng",
          mbb["verdict"] == BD.AMBIGUOUS and "KHÔNG giao" in mbb.get("why", ""), mbb.get("why"))
    check("A15 thiếu giá cum ⇒ INSUFFICIENT",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], None)["verdict"] == BD.INSUFFICIENT)
    g = DEC("TPB", D, EX, {"SpaceX": ev}, [], 400)
    check("A15b giá vô nghĩa (giá cum ≤ chân tiền) ⇒ AMBIGUOUS nói đúng lý do",
          g["verdict"] == BD.AMBIGUOUS and "giá vô nghĩa" in g["why"], g.get("why"))
    check("A15c giá cum âm (dữ liệu rác) ⇒ INSUFFICIENT như thiếu giá",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], -1.0)["verdict"] == BD.INSUFFICIENT)
    check("A16 tài khoản khác giữ mã mà chưa credit ⇒ INSUFFICIENT",
          DEC("TPB", D, EX, {"SpaceX": ev}, ["ZaloPay"], 14400)["verdict"] == BD.INSUFFICIENT)
    ev2 = dict(ev, cash_leg=450.0)
    check("A17 chân tiền lệch giữa tài khoản ⇒ AMBIGUOUS",
          DEC("TPB", D, EX, {"SpaceX": ev, "ZaloPay": ev2}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)
    ev3 = dict(ev, mkt1=[12200.0])
    check("A17b marketPrice sau credit khác nhau giữa tài khoản ⇒ AMBIGUOUS",
          DEC("TPB", D, EX, {"SpaceX": ev, "ZaloPay": ev3}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)
    iss = {"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
           "exercise_ratio": 0.15}
    div = {"ticker": "TPB", "date": EX, "event_code": "DIV", "price_adjusting": True,
           "value_per_share": 800}
    for order, lst in (("ISS", [iss]), ("DIV,ISS", [div, iss]), ("ISS,DIV", [iss, div]),
                       ("ISS ngày khác", [dict(iss, date="2026-10-09")])):
        check(f"A18 vendor [{order}] ⇒ DEFER_VENDOR bất kể thứ tự/ngày (M1)",
              DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400, lst)["verdict"] == BD.DEFER_VENDOR)
    check("A19 vendor DIV 800 ≠ chân tiền 500 ⇒ AMBIGUOUS",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400, [div])["verdict"] == BD.AMBIGUOUS)
    check("A19b vendor DIV 300+200 (2 dòng cùng ex) = chân tiền 500 ⇒ CONFIRMABLE",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400,
                    [dict(div, value_per_share=300), dict(div, value_per_share=200)])["verdict"]
          == BD.CONFIRMABLE)
    check("A19c vendor DIV 800 ở NGÀY KHÁC ex ⇒ không đối chiếu, CONFIRMABLE",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400,
                    [dict(div, date="2026-11-20")])["verdict"] == BD.CONFIRMABLE)
    r19d = _call("A19d lịch vendor đọc hỏng ⇒ AMBIGUOUS", DEC, "TPB", D, EX, {"SpaceX": ev}, [], 14400,
                 BD.VENDOR_UNREADABLE)
    if r19d is not _CRASHED:
        check("A19d lịch vendor đọc hỏng ⇒ AMBIGUOUS", r19d["verdict"] == BD.AMBIGUOUS)
    amb = dict(ev, verdict=BD.AMBIGUOUS, why="x")
    check("A20 một tài khoản AMBIGUOUS ⇒ cả mã AMBIGUOUS",
          DEC("TPB", D, EX, {"SpaceX": ev, "ZaloPay": amb}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)
    ev_m = dict(ev, q0=100, q1=1200, m_lo=12.0, m_hi=12.01, cash_leg=0.0, mkt1=[1200.0])
    check("A21 hệ số > QTY_MULT_MAX ⇒ AMBIGUOUS (không để validate() nổ ở điểm ghi)",
          DEC("TPB", D, EX, {"SpaceX": ev_m}, [], 14400)["verdict"] == BD.AMBIGUOUS)
    disj = dict(ev, m_lo=1.2, m_hi=1.21)
    check("A22 hệ số KL hai tài khoản không giao nhau ⇒ AMBIGUOUS",
          DEC("TPB", D, EX, {"SpaceX": ev, "ZaloPay": disj}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)

    # ── B1 arch-review v1: GIÁ KHÔNG RƠI ⇒ không được CONFIRMABLE ──
    for lbl, q0_, q1_, px in (("+1% @14.400", 200, 202, 14400), ("+0,3% @14.400", 1000, 1003, 14400),
                              ("+4% @5.000", 1000, 1040, 5000)):
        ser = tpb_series(q0=q0_, cost0=16800, q1=q1_, cost1=round(q0_ * 16800 / q1_, 4), mkt0=px,
                         mkt1=px, trade1=q0_)
        e = BD.account_evidence(ser, "TPB", D)
        dd = DEC("TPB", D, EX, {"SpaceX": e}, [], px)
        check(f"N1 KL {lbl}, marketPrice == giá cum ⇒ AMBIGUOUS (giả thuyết không-sự-kiện)",
              e["verdict"] == BD.CONFIRMABLE and dd["verdict"] == BD.AMBIGUOUS
              and "không-sự-kiện" in dd["why"], (e["verdict"], dd.get("why")))
    late_ex = DEC("TPB", D, EX, {"SpaceX": ev}, [], 12100)          # giá cum đã ở hệ sau
    check("N2 CP về SAU ex-date (giá cum đã điều chỉnh) ⇒ AMBIGUOUS", late_ex["verdict"] == BD.AMBIGUOUS,
          late_ex.get("why"))

    # ── lịch (M4) ──
    check("K1 lịch thường (T5→T6) tin được", BD.calendar_guard(D, EX) is None)
    check("K2 MSB 08-27→08-28: mùa Quốc khánh 2026 ĐÃ khai báo ⇒ tin được",
          BD.calendar_guard("2026-08-27", "2026-08-28") is None)
    check("K3 Tết 2027 chưa khai báo ⇒ lý do", BD.calendar_guard("2027-02-04", "2027-02-05") is not None)
    check("K4 phiên kế tiếp cách > 4 ngày lịch ⇒ lý do",
          BD.calendar_guard("2026-10-01", "2026-10-07") is not None)
    tet = DEC("TPB", "2027-02-04", "2027-02-05", {"SpaceX": ev}, [], 14400)
    check("K5 decide với ex rơi mùa Tết chưa khai báo ⇒ AMBIGUOUS dù bằng chứng broker đủ",
          tet["verdict"] == BD.AMBIGUOUS and "Tết" in tet["why"], tet.get("why"))

    # BID-like: ZaloPay 2 gói vay, credit DỞ 19:10 (1 gói) rồi xong 20:15
    m0 = "2026-08-13T11:40:12Z"
    p1 = lot(1, 100, 39550, 38850, m0, acct=A2[0], sym="BID")
    p2 = lot(2, 300, 40316.6667, 38850, m0, closed=600, accum=900, acct=A2[0], sym="BID")
    c1 = lot(1, 107, 36962.6168, 35800, "2026-08-14T12:09:00.785778Z", trade=100, accum=107,
             acct=A2[0], sym="BID")
    c2 = lot(2, 320, 37796.875, 35800, "2026-08-14T13:15:09Z", trade=300, closed=600, accum=920,
             acct=A2[0], sym="BID")
    ser = [snap("2026-08-13T23:00:00", p1, p2), snap("2026-08-14T19:04:00", p1, p2),
           snap("2026-08-14T19:10:23", c1, p2)]
    e_mid = BD.account_evidence(ser, "BID", "2026-08-14")
    check("A23 gói vay dở (1 lô còn nguyên) ⇒ INSUFFICIENT, không phải AMBIGUOUS",
          e_mid["verdict"] == BD.INSUFFICIENT, e_mid)
    ser2 = ser + [snap("2026-08-14T20:15:02", c1, c2), snap("2026-08-14T20:30:02", c1, c2)]
    e_done = BD.account_evidence(ser2, "BID", "2026-08-14")
    check("A24 gói vay xong ⇒ lùi qua trạng thái dở, KL 400→427",
          e_done["verdict"] == BD.CONFIRMABLE and e_done["q0"] == 400 and e_done["q1"] == 427,
          e_done)
    # không lùi qua đoạn bắt đầu TRƯỚC 15:00, không lùi qua bước KHÔNG giống credit
    pre = lot(5, 200, 16800, 14450)
    mid_pre15 = lot(5, 210, 16000, 14450, trade=200, accum=210)              # credit-like, 11:00
    fin = lot(5, 241, 16000 * 210 / 241, 12100, trade=200, accum=241)
    e = BD.account_evidence([snap(f"{PREV}T23:30:04", pre), snap(f"{D}T11:00:00", mid_pre15),
                             snap(f"{D}T19:03:01", fin), snap(f"{D}T19:04:01", fin)], "TPB", D)
    check("A29 không lùi qua đoạn bắt đầu trước 15:00 ⇒ q0 = 210", e.get("q0") == 210, e)
    mid_buy = lot(5, 210, (200 * 16800 + 10 * 14400) / 210, 14450, trade=200, accum=210)
    fin2 = lot(5, 241, (200 * 16800 + 10 * 14400) / 241, 12100, trade=200, accum=241)
    e = BD.account_evidence([snap(f"{D}T11:16:00", pre), snap(f"{D}T19:01:00", mid_buy),
                             snap(f"{D}T19:03:01", fin2), snap(f"{D}T19:04:01", fin2)], "TPB", D)
    check("A30 không lùi qua bước giống MUA (giá vốn tăng) ⇒ q0 = 210", e.get("q0") == 210, e)
    sx = BD.account_evidence([snap("2026-08-13T23:00:00", lot(9, 1100, 42269.3675, 38850, m0, sym="BID")),
                              snap("2026-08-14T19:11:05", lot(9, 1175, 39571.3228, 35800,
                                                             "2026-08-14T12:08:57.584625573Z",
                                                             trade=1100, sym="BID")),
                              snap("2026-08-14T20:15:03", lot(9, 1175, 39571.3228, 35800,
                                                             "2026-08-14T12:08:57.584625Z",
                                                             trade=1100, sym="BID"))], "BID", "2026-08-14")
    dbid = DEC("BID", "2026-08-14", "2026-08-17", {"SpaceX": sx, "ZaloPay": e_done}, [], 38250)
    check("A26 BID 2 tài khoản ⇒ ×1.069 (số NGẮN NHẤT tái tạo 1100→1175 VÀ 400→427)",
          dbid["verdict"] == BD.CONFIRMABLE and dbid.get("qty_multiplier") == 1.069, dbid.get("why"))
    # ── vòng 3 (arch-review v2) ──
    mix = tpb_series()
    lots2 = [lot(1, 100, 16800, 14450), lot(2, 100, 16800, 14450)]
    post2 = [lot(1, 115, 14173.913, 12500, trade=100, accum=115),
             lot(2, 115, 14173.913, 14400, trade=100, accum=115)]
    mix = [snap(f"{PREV}T23:30:04", *lots2), snap(f"{D}T11:16:29", *lots2),
           snap(f"{D}T19:03:01", *post2), snap(f"{D}T19:04:01", *post2)]
    e = BD.account_evidence(mix, "TPB", D)
    check("X0 2 lô cùng credit nhưng marketPrice 12.500 vs 14.400 (= giá cum) ⇒ KHÔNG CONFIRMABLE (N1)",
          e["verdict"] == BD.INSUFFICIENT and "marketPrice khác nhau" in e["why"], e.get("why"))
    for exch, want in (("HNX", BD.CONFIRMABLE), ("UPCOM", BD.AMBIGUOUS), (None, BD.AMBIGUOUS)):
        r = BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400, exchange=exch)
        check(f"X1 sàn {exch} ⇒ {want}", r["verdict"] == want, r.get("why"))
    up = BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400)
    check("X2 decide KHÔNG truyền sàn ⇒ mặc định MƠ HỒ (fail-closed)",
          up["verdict"] == BD.AMBIGUOUS and "KHÔNG xác định" in up["why"], up.get("why"))
    # null-test nửa chân tiền: cổ tức 500 + KL ×1,01, marketPrice = cum − 500 (không sự kiện CP)
    ser = tpb_series(q1=202, cost1=round((200 * 16800 - 200 * 500) / 202, 4), mkt1=13900)
    e = BD.account_evidence(ser, "TPB", D)
    dd = DEC("TPB", D, EX, {"SpaceX": e}, [], 14400)
    check("X3 cổ tức 500 + KL ×1,01, giá = cum − 500 ⇒ AMBIGUOUS (null-test với chân tiền)",
          e["verdict"] == BD.CONFIRMABLE and e["cash_leg"] == 500 and dd["verdict"] == BD.AMBIGUOUS
          and "không-sự-kiện" in dd["why"], (e.get("cash_leg"), dd.get("why")))
    check("X4 KL mới thấy lần đầu 14:30 (sau ATC nhưng trước 15:00) ⇒ AMBIGUOUS",
          V(tpb_series(post_at="14:30")) == BD.AMBIGUOUS)
    check("X5 prev_trading_day bỏ qua lễ Quốc khánh 2026 + cuối tuần",
          BD.prev_trading_day("2026-09-03") == "2026-08-28", BD.prev_trading_day("2026-09-03"))
    # lô giảm KL trong khi lô khác tăng, chân tiền từng lô vẫn 500
    l1, l2 = lot(1, 100, 16800, 14450), lot(2, 100, 16800, 14450)
    c1 = lot(1, 140, 11642.8571, 12100, trade=100, accum=140)
    c2 = lot(2, 90, 18111.1111, 12100, trade=90, accum=90)
    e = BD.account_evidence([snap(f"{PREV}T23:30:04", l1, l2), snap(f"{D}T11:16:29", l1, l2),
                             snap(f"{D}T19:03:01", c1, c2), snap(f"{D}T19:04:01", c1, c2)], "TPB", D)
    check("X6 một lô GIẢM KL (chân tiền lô vẫn khớp) ⇒ AMBIGUOUS", e["verdict"] == BD.AMBIGUOUS,
          e.get("why"))
    check("X7 vendor DIV 550 vs chân tiền 500 ⇒ AMBIGUOUS (dung sai 1đ)",
          DEC("TPB", D, EX, {"SpaceX": ev}, [], 14400, [dict(div, value_per_share=550)])["verdict"]
          == BD.AMBIGUOUS)
    check("X8 lệnh khớp KHÔNG có giờ ⇒ AMBIGUOUS (không bỏ qua)",
          V(tpb_series(), fills=[(None, 30, "NB")]) == BD.AMBIGUOUS)
    at = BD.modified_ict("2026-10-01T04:16:29Z")                        # = 11:16:29 ICT, đúng ts0_last
    check("X9 lệnh khớp ĐÚNG giây bản ghi trước credit ⇒ AMBIGUOUS (>=)",
          V(tpb_series(), fills=[(at, 30, "NB")]) == BD.AMBIGUOUS)
    check("A25 simplest_in", BD.simplest_in(1.068182, 1.069091) == 1.069
          and BD.simplest_in(1.15, 1.155) == 1.15 and BD.simplest_in(1.26, 1.2608333) == 1.26
          and BD.simplest_in(1.0, 1.0) is None)


# ─────────────────────────────────────────────── A'. đọc file: §12 lọc account + scan_day ──

def _write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for x in sorted(lines, key=lambda x: x["ts"]):
            f.write(json.dumps(x) + "\n")


def _pos_lines(acct, label, series, day):
    return [{"ts": ts, "kind": "positions", "account_no": acct, "account_label": label,
             "payload": {"positions": [r for rows in by.values() for r in rows]}}
            for ts, by in series if ts.startswith(day)]


def test_files():
    tmp = _mkdtemp("brokerca_f_")
    ser1 = tpb_series()
    foreign = lot(77, 5000, 1000, 14450, acct=A2[0], sym="TPB")
    lines = _pos_lines(*A1, ser1, D)
    lines[-1]["payload"]["positions"].append(foreign)              # dòng lạ account trong bản ghi A1
    lines.append({"ts": f"{D}T19:30:00", "kind": "positions", "account_no": A2[0],
                  "account_label": A2[1], "payload": {"positions": [foreign]}})
    p = os.path.join(tmp, f"dnse_raw_{D}.jsonl")
    _write_lines(p, lines)
    s1 = BD.read_series(p, A1[0])
    qty = [BD.aggregate(by.get("TPB", []))["qty"] for _ts, by in s1]
    check("F1 §12 read_series: chỉ bản ghi + dòng của đúng account", qty[-1] == 230 and
          len(s1) == len([x for x in lines if x["account_no"] == A1[0]]), qty)
    order = lambda acct, oid, h: {"id": oid, "symbol": "TPB", "accountNo": acct,  # noqa: E731
                                  "transDate": D, "fillQuantity": 30, "side": "NB",
                                  "modifiedDate": f"{D}T{h}:00:00Z"}
    _write_lines(p, lines + [
        {"ts": f"{D}T20:00:00", "kind": "orders", "account_no": A2[0],
         "payload": {"orders": [order(A2[0], 1, "07")]}},
        {"ts": f"{D}T20:00:01", "kind": "orders", "account_no": A1[0],
         "payload": {"orders": [order(A2[0], 2, "07")]}},
        {"ts": f"{D}T20:00:02", "kind": "orders", "account_no": A2[0],        # bản ghi của A2
         "payload": {"orders": [order(A1[0], 3, "07")]}}])
    check("F2 §12 same_day_fills: lệnh account khác (bản ghi khác / dòng lạ) KHÔNG tính",
          BD.same_day_fills(p, A1[0], "TPB", D) == [], BD.same_day_fills(p, A1[0], "TPB", D))
    _write_lines(os.path.join(tmp, f"dnse_raw_{PREV}.jsonl"), _pos_lines(*A1, ser1, PREV))
    check("F3 previous_file KHÔNG trả file cùng ngày",
          BD.previous_file(D, tmp).endswith(f"dnse_raw_{PREV}.jsonl"), BD.previous_file(D, tmp))

    def scan(extra_day=(), extra_prev=(), px=14400):
        ex = _mkdtemp("brokerca_s_")
        _write_lines(os.path.join(ex, f"dnse_raw_{PREV}.jsonl"),
                     _pos_lines(*A1, ser1, PREV) + list(extra_prev))
        _write_lines(os.path.join(ex, f"dnse_raw_{D}.jsonl"), _pos_lines(*A1, ser1, D) + list(extra_day))
        return {r["ticker"]: r for r in BD.scan_day(D, lambda t, d: px, exec_dir=ex,
                                                     exchange_fn=lambda t: "HOSE")}
    r = scan()
    check("S1 scan_day TPB CONFIRMABLE ex 10-02", r.get("TPB", {}).get("verdict") == BD.CONFIRMABLE
          and r["TPB"]["ex_date"] == EX, r)
    held = tpb_series(acct=A2[0], q1=200, cost1=16800, mkt1=14450, trade1=200)
    r = scan(extra_day=_pos_lines(*A2, held, D), extra_prev=_pos_lines(*A2, held, PREV))
    check("S2 tài khoản khác giữ TPB mà KHÔNG được credit ⇒ INSUFFICIENT",
          r["TPB"]["verdict"] == BD.INSUFFICIENT and "ZaloPay" in r["TPB"]["why"], r["TPB"].get("why"))
    r = scan(extra_prev=_pos_lines(*A2, held, PREV))
    check("S3 tài khoản giữ TPB phiên trước mà KHÔNG có bản ghi hôm nay ⇒ INSUFFICIENT",
          r["TPB"]["verdict"] == BD.INSUFFICIENT and "không có bản ghi" in r["TPB"]["why"],
          r["TPB"].get("why"))
    r = scan(extra_day=[{"ts": f"{D}T20:00:00", "kind": "orders", "account_no": A1[0],
                         "payload": {"orders": [order(A1[0], 9, "07")]}}])
    check("S4 sổ lệnh broker CÙNG account có khớp sau bản ghi trước credit ⇒ AMBIGUOUS",
          r["TPB"]["verdict"] == BD.AMBIGUOUS and "KHỚP" in r["TPB"]["why"], r["TPB"].get("why"))


# ─────────────────────────────────────────────────────────────── B. run_broker sandbox ──
REAL_PX_FN = cac._px_cum_fn
REAL_EXCH_FN = cac._exchange_fn
REAL_WRITE = cac.write_corp_actions
REAL_VENDOR = cac.run_vendor
REAL_CA_DIR = cac.CA_DAILY_DIR


class _Bus:
    calls = []
    rc = 0

    @staticmethod
    def run(cmd, **kw):
        _Bus.calls.append(list(cmd))

        class R:
            returncode, stdout, stderr = _Bus.rc, "", ("bus giả lỗi" if _Bus.rc else "")
        return R()


def _abc_series(**kw):
    return [(ts, {"ABC": [dict(r, symbol="ABC", id=999) for r in by["TPB"]]})
            for ts, by in tpb_series(**kw)]


MISSING = object()        # _sandbox(vendor=MISSING): KHÔNG có file lịch vendor ngày D


def _sandbox(registry_actions=None, vendor=(), extra=(), series=None):
    """vendor=() (mặc định) ⇒ lịch vendor CÓ file, không sự kiện (feed STALE/đủ) — từ arch-review v4
    #5 file THIẾU là VENDOR_UNREADABLE nên ca lành phải có file; vendor=MISSING ⇒ không có file."""
    tmp = _mkdtemp("brokerca_")
    ex, ca = os.path.join(tmp, "exec"), os.path.join(tmp, "ca_daily")
    os.makedirs(ex)
    os.makedirs(ca)
    ser = series or tpb_series()
    if extra:                                                 # thêm mã vào CÙNG bản ghi
        ser = [(ts, dict(by, **xb)) for (ts, by), (_t, xb) in zip(ser, extra)]
    _write_lines(os.path.join(ex, f"dnse_raw_{PREV}.jsonl"), _pos_lines(*A1, ser, PREV))
    _write_lines(os.path.join(ex, f"dnse_raw_{D}.jsonl"), _pos_lines(*A1, ser, D))
    if vendor is not MISSING:
        with open(os.path.join(ca, f"corp_action_daily_{D}.json"), "w", encoding="utf-8") as f:
            f.write(vendor if isinstance(vendor, str) else json.dumps({"upcoming_events_held": list(vendor)}))
    reg = os.path.join(tmp, "corp_actions.json")
    with open(reg, "w", encoding="utf-8") as f:
        json.dump({"actions": registry_actions or []}, f)
    cac.EXEC_DIR, cac.CA_DAILY_DIR, cac.CORP_ACTIONS_FILE = ex, ca, reg
    cac.LEDGER_FILE = os.path.join(tmp, "ledger.jsonl")
    cac._px_cum_fn = lambda d: (lambda t, dd: {"TPB": 14400}.get(t))
    cac._exchange_fn = lambda: (lambda tk: "HOSE")
    cac.write_corp_actions = REAL_WRITE
    _Bus.calls, _Bus.rc = [], 0
    return tmp, reg


def _ledger_lines():
    if not os.path.exists(cac.LEDGER_FILE):
        return []
    return [json.loads(x) for x in open(cac.LEDGER_FILE, encoding="utf-8") if x.strip()]


def _ledger_write(entries):
    with open(cac.LEDGER_FILE, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _kinds(kind):
    return [c[3] for c in _Bus.calls if c[2] == kind]


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def test_B():
    real_run = subprocess.run
    subprocess.run = _Bus.run
    try:
        tmp, reg = _sandbox()
        h0 = _sha(reg)
        rc = cac.run_broker(D, mode="shadow")
        lg = _ledger_lines()
        check("B1 shadow rc=0, registry KHÔNG đổi", rc == 0 and _sha(reg) == h0)
        check("B2 shadow sổ: 1 intent CONFIRMABLE kèm record dự kiến + 1 done",
              [x["kind"] for x in lg] == ["intent", "done"] and lg[0]["verdict"] == BD.CONFIRMABLE
              and lg[0]["record"]["qty_multiplier"] == 1.15, lg)
        check("B3 shadow: 1 bus finding, 0 question", [c[2] for c in _Bus.calls] == ["finding"], _Bus.calls)
        n = len(_Bus.calls)
        cac.run_broker(D, mode="shadow")
        check("B4 shadow chạy lại idempotent (0 dòng sổ mới, 0 bus mới)",
              len(_ledger_lines()) == 2 and len(_Bus.calls) == n)

        tmp, reg = _sandbox()
        rc = cac.run_broker(D, mode="live")
        acts = CA.load_corp_actions(reg)
        check("B5 live: registry có TPB CONFIRMED ×1.15 ex 10-02 chân tiền 500 (đọc lại qua load_corp_actions)",
              rc == 0 and len(acts) == 1 and acts[0]["qty_multiplier"] == 1.15
              and acts[0]["ex_date"] == EX and acts[0]["cash_leg_vnd_per_share"] == 500.0, acts)
        check("B6 live: không file .tmp sót", not [f for f in os.listdir(tmp) if f.endswith(".tmp")])
        check("B7 live: bus finding corp-action-broker-confirm-TPB",
              _kinds("finding") == ["corp-action-broker-confirm-TPB"] and not _kinds("question"), _Bus.calls)
        h1, n = _sha(reg), len(_Bus.calls)
        cac.run_broker(D, mode="live")
        check("B8 live chạy lại: registry y nguyên, 0 bus mới", _sha(reg) == h1 and len(_Bus.calls) == n)

        manual = {"id": "TPB-2026-10-02-STOCK-DIVIDEND", "ticker": "TPB", "event_type": "STOCK_DIVIDEND",
                  "qty_multiplier": 1.15, "ex_date": EX, "broker_effective_ts": "2026-10-01T11:52:12",
                  "_status": "CONFIRMED — user"}
        tmp, reg = _sandbox([manual])
        h0 = _sha(reg)
        cac.run_broker(D, mode="live")
        check("B9 registry đã có (TPB, ex) ⇒ không ghi, không hỏi", _sha(reg) == h0 and not _Bus.calls)
        tmp, reg = _sandbox([dict(manual, _status="PROPOSED — chờ")])
        h0 = _sha(reg)
        cac.run_broker(D, mode="live")
        check("B9b record PROPOSED do người viết ⇒ broker KHÔNG ghi đè/ghi trùng", _sha(reg) == h0)
        tmp, reg = _sandbox([dict(manual, id="TPB-NEAR", ex_date="2026-10-05")])
        h0 = _sha(reg)
        cac.run_broker(D, mode="live")
        check("B20 registry có TPB ex 10-05 (cách ≤10 ngày, khác ex suy ra) ⇒ không ghi, hỏi (M4)",
              _sha(reg) == h0 and len(_kinds("question")) == 1
              and "ambiguous" in _kinds("question")[0], _Bus.calls)

        tmp, reg = _sandbox([dict(manual, id="TPB-PAST", ex_date="2026-09-28")])
        h0 = _sha(reg)
        cac.run_broker(D, mode="live")
        check("B20b registry có TPB ex 09-28 (QUÁ KHỨ, cách 3 ngày) ⇒ không ghi, hỏi",
              _sha(reg) == h0 and len(_kinds("question")) == 1, _Bus.calls)
        tmp, reg = _sandbox(vendor="[1, 2]")
        _call("B24b lịch vendor gốc là list ⇒ AMBIGUOUS question, 0 ghi", cac.run_broker, D, mode="live")
        check("B24b lịch vendor gốc là list ⇒ AMBIGUOUS question, 0 ghi",
              CA.load_corp_actions(reg) == [] and len(_kinds("question")) == 1, _Bus.calls)
        tmp, reg = _sandbox()
        cac._exchange_fn = lambda: (lambda tk: "UPCOM")
        cac.run_broker(D, mode="live")
        check("B27 live mã UPCOM ⇒ không ghi, hỏi",
              CA.load_corp_actions(reg) == [] and len(_kinds("question")) == 1, _Bus.calls)

        # gửi bù ở SHADOW (mode mặc định)
        tmp, reg = _sandbox()
        _Bus.rc = 1
        cac.run_broker(D, mode="shadow")
        _Bus.rc, _Bus.calls = 0, []
        cac.run_broker(D, mode="live")
        check("B28 pending SHADOW không bị gửi ở lượt LIVE", not [c for c in _Bus.calls
                                                                  if "shadow" in c[3]], _Bus.calls)
        _Bus.calls = []
        cac.run_broker(D, mode="shadow")
        lg = _ledger_lines()
        check("B28b lượt shadow sau GỬI BÙ (1 finding) + done cho pending",
              _kinds("finding") == [f"corp-action-broker-shadow-{D}"]
              and any(x["kind"] == "done" and x["key"][0] == "shadow" for x in lg), (lg, _Bus.calls))
        n = len(_Bus.calls)
        cac.run_broker(D, mode="shadow")
        check("B28c shadow lượt thứ ba ⇒ im (không gửi lặp mỗi ngày)", len(_Bus.calls) == n)

        tmp, reg = _sandbox()
        open(cac.LEDGER_FILE, "w").write('{"kind": "intent"\n')
        try:
            cac.run_broker(D, mode="live")
            check("B29 dòng sổ hỏng ⇒ CorpActionLedgerError (không nuốt)", False)
        except BD.CorpActionLedgerError:
            check("B29 dòng sổ hỏng ⇒ CorpActionLedgerError (không nuốt)",
                  CA.load_corp_actions(reg) == [] and not _Bus.calls)

        # INSUFFICIENT rồi lượt sau CONFIRMABLE ⇒ đóng câu hỏi cũ (§26)
        tmp, reg = _sandbox()
        cac._px_cum_fn = lambda d: (lambda t, dd: None)
        cac.run_broker(D, mode="live")
        cac._px_cum_fn = lambda d: (lambda t, dd: 14400)
        _Bus.calls = []
        cac.run_broker(D, mode="live")
        check("B30 INSUFFICIENT → CONFIRMED lượt sau ⇒ finding + answer đóng question insufficient",
              len(CA.load_corp_actions(reg)) == 1
              and _kinds("answer") == [f"corp-action-broker-insufficient-TPB-{D}"], _Bus.calls)

        tmp, reg = _sandbox()
        cac._px_cum_fn = lambda d: (lambda t, dd: 14400 * 1.12)       # giá không khớp
        cac.run_broker(D, mode="live")
        q = _kinds("question")
        qq = [c for c in _Bus.calls if c[2] == "question"]
        check("B10 live mơ hồ ⇒ đúng 1 question urgency high, registry rỗng",
              len(q) == 1 and "corp-action-broker-ambiguous-TPB" in q[0]
              and json.loads(qq[0][4])["urgency"] == "high"
              and CA.load_corp_actions(reg) == [], _Bus.calls)
        cac.run_broker(D, mode="live")
        check("B11 mơ hồ chạy lại ⇒ không hỏi lần 2", len(_kinds("question")) == 1)

        tmp, reg = _sandbox()
        cac._px_cum_fn = lambda d: (lambda t, dd: None)
        cac.run_broker(D, mode="live")
        q = [c for c in _Bus.calls if c[2] == "question"]
        check("B18 live INSUFFICIENT (thiếu giá cum) ⇒ question urgency normal, KHÔNG im (M3)",
              len(q) == 1 and "insufficient" in q[0][3] and json.loads(q[0][4])["urgency"] == "normal",
              _Bus.calls)
        iss = {"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
               "exercise_ratio": 0.16}
        div = {"ticker": "TPB", "date": EX, "event_code": "DIV", "price_adjusting": True,
               "value_per_share": 500}
        tmp, reg = _sandbox(vendor=[div, iss])
        cac.run_broker(D, mode="live")
        check("B19 live vendor [DIV, ISS] (vendor MISMATCH im) ⇒ DEFER_VENDOR + question, 0 ghi (M1)",
              CA.load_corp_actions(reg) == [] and len(_kinds("question")) == 1
              and "defer_vendor" in _kinds("question")[0], _Bus.calls)
        tmp, reg = _sandbox(vendor="{hỏng")
        _call("B24 lịch vendor đọc hỏng ⇒ AMBIGUOUS question, 0 ghi", cac.run_broker, D, mode="live")
        check("B24 lịch vendor đọc hỏng ⇒ AMBIGUOUS question, 0 ghi",
              CA.load_corp_actions(reg) == [] and len(_kinds("question")) == 1, _Bus.calls)

        # ── at-least-once (M2) ──
        tmp, reg = _sandbox()
        _Bus.rc = 1
        rc = cac.run_broker(D, mode="live")
        check("B16 bus lỗi sau ghi registry ⇒ rc=1, registry CÓ record, sổ KHÔNG có done",
              rc == 1 and len(CA.load_corp_actions(reg)) == 1
              and [x["kind"] for x in _ledger_lines()] == ["intent"], _ledger_lines())
        _Bus.rc, _Bus.calls = 0, []
        rc = cac.run_broker(D, mode="live")
        check("B16b lượt sau GỬI BÙ finding confirm + ghi done",
              rc == 0 and _kinds("finding") == ["corp-action-broker-confirm-TPB"]
              and [x["kind"] for x in _ledger_lines()] == ["intent", "done"], (_Bus.calls, _ledger_lines()))
        n = len(_Bus.calls)
        cac.run_broker(D, mode="live")
        check("B16c lượt thứ ba ⇒ im", len(_Bus.calls) == n)

        tmp, reg = _sandbox()

        def _boom(*a, **k):
            raise OSError("đĩa đầy (giả)")
        cac.write_corp_actions = _boom
        try:
            cac.run_broker(D, mode="live")
            check("B17 ghi registry nổ ⇒ ngoại lệ lan ra (run() bắt)", False)
        except OSError:
            check("B17 ghi registry nổ ⇒ ngoại lệ lan ra (run() bắt)", True)
        cac.write_corp_actions = REAL_WRITE
        cac.run_broker(D, mode="live")
        check("B17b lượt sau: intent dở + registry KHÔNG có record ⇒ question write-incomplete, 0 ghi",
              CA.load_corp_actions(reg) == [] and len(_kinds("question")) == 1
              and "write-incomplete" in _kinds("question")[0], _Bus.calls)

        tmp, reg = _sandbox()
        cac.write_corp_actions = lambda *a, **k: None                   # "ghi" mà không ghi
        rc = cac.run_broker(D, mode="live")
        check("B26 đọc lại sau ghi không thấy record ⇒ rc=1 + question write-incomplete (§6)",
              rc == 1 and len(_kinds("question")) == 1 and "write-incomplete" in _kinds("question")[0],
              (rc, _Bus.calls))
        cac.write_corp_actions = REAL_WRITE

        tmp, reg = _sandbox()
        os.environ["MIKE_CA_BROKER_SOURCE"] = "off"
        saved_vendor = cac.run_vendor
        try:
            cac.run_vendor = lambda *a, **k: 0
            rc = cac.run(D)
            check("B12 off ⇒ không sổ, không bus", rc == 0 and not _ledger_lines() and not _Bus.calls)
            os.environ["MIKE_CA_BROKER_SOURCE"] = "live"
            saved_scan = BD.scan_day
            BD.scan_day = lambda *a, **k: 1 / 0
            try:
                rc = _call("B23 crash nhánh broker ⇒ run() rc=1 + bus question (không chỉ nằm trong log cron)",
                           cac.run, D)
            finally:
                BD.scan_day = saved_scan
            check("B23 crash nhánh broker ⇒ run() rc=1 + bus question (không chỉ nằm trong log cron)",
                  rc == 1 and not _kinds("error") and len(_kinds("question")) == 1
                  and "broker-crash" in _kinds("question")[0], _Bus.calls)
        finally:
            cac.run_vendor = saved_vendor
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        os.environ["MIKE_CA_BROKER_SOURCE"] = "LIVEE"
        try:
            check("B13 mode gõ nhầm ⇒ shadow", cac.broker_mode() == "shadow")
        finally:
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        check("B13b mặc định = shadow", cac.broker_mode() == "shadow")

        tmp, reg = _sandbox()
        h0 = _sha(reg)
        cac.run_broker(D, dry_run=True, mode="live")
        check("B14 dry-run ⇒ 0 ghi, 0 bus", _sha(reg) == h0 and not _ledger_lines() and not _Bus.calls)

        broken = {"id": "X", "ticker": "VHM", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 13,
                  "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05", "_status": "CONFIRMED"}
        tmp, reg = _sandbox([broken])
        h0 = _sha(reg)
        rc = _call("B15 record cũ hỏng ⇒ rc=1, registry y nguyên, sổ KHÔNG ghi, có question",
                   cac.run_broker, D, mode="live")
        check("B15 record cũ hỏng ⇒ rc=1, registry y nguyên, sổ KHÔNG ghi, có question",
              rc == 1 and _sha(reg) == h0 and not _ledger_lines() and len(_kinds("question")) == 1,
              (rc, _Bus.calls))

        tmp, reg = _sandbox([broken], extra=_abc_series())
        h0 = _sha(reg)
        rc = cac.run_broker(D, mode="live")                      # ABC: không có giá ⇒ INSUFFICIENT
        topics = _kinds("question")
        check("B15b validate-reject KHÔNG nuốt câu hỏi của mã khác + nói rõ chạy lại --date",
              rc == 1 and _sha(reg) == h0
              and any("validate-reject" in t for t in topics)
              and any("insufficient-ABC" in t for t in topics)
              and any(f"--date {D}" in c[4] for c in _Bus.calls if "validate-reject" in c[3]),
              _Bus.calls)

        # ── v2 N9: vendor sống lại với ex ≠ ex của record BROKER ⇒ không ghi record thứ 2 ──
        brec = {"id": "TPB-2026-10-05-BROKER-SHARE-EVENT", "ticker": "TPB",
                "event_type": "BONUS_ISSUE", "qty_multiplier": 1.15, "ex_date": "2026-10-05",
                "broker_effective_ts": "2026-10-02T12:03:01", "_status": "CONFIRMED — broker",
                "provenance": "broker"}
        vcal = [{"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
                 "exercise_ratio": 0.15, "days_ahead": 1}]
        tmp, reg = _sandbox([brec], vendor=vcal)
        h0 = _sha(reg)
        cac.run_vendor(D)
        check("B31 vendor ex 10-02 vs record broker ex 10-05 ⇒ vendor KHÔNG ghi, hỏi",
              _sha(reg) == h0 and any("vendor-vs-broker-TPB" in t for t in _kinds("question")),
              _Bus.calls)
        tmp, reg = _sandbox([dict(brec, provenance=None, id="TPB-USER")], vendor=vcal)
        cac.run_vendor(D)
        check("B31b record NGƯỜI ký (không provenance broker) ⇒ nhánh vendor đi đường cũ (không hỏi mới)",
              not any("vendor-vs-broker" in t for t in _kinds("question")), _Bus.calls)

        # ── B2: sandbox lệch (sổ trỏ "production" mà dữ liệu sandbox) ⇒ từ chối, kể cả 1 trục ──
        saved = cac._PROD_DATA
        for lbl, exec_in, reg_in in (("cả 2 trục", False, False), ("chỉ EXEC_DIR", False, True),
                                     ("chỉ registry", True, False)):
            tmp, reg = _sandbox()
            prod = os.path.join(tmp, "PROD")                  # mô phỏng thư mục data/ production
            os.makedirs(prod)
            cac._PROD_DATA = os.path.realpath(prod)
            cac.LEDGER_FILE = os.path.join(prod, "ledger.jsonl")
            if exec_in:
                shutil.copytree(cac.EXEC_DIR, os.path.join(prod, "exec"))
                cac.EXEC_DIR = os.path.join(prod, "exec")
            if reg_in:
                shutil.copy(reg, os.path.join(prod, "corp_actions.json"))
                cac.CORP_ACTIONS_FILE = os.path.join(prod, "corp_actions.json")
            try:
                for fn_ in (lambda: cac.run_broker(D, mode="shadow"),
                            lambda: (setattr(cac, "run_vendor", lambda *a, **k: 0), cac.run(D))):
                    try:
                        fn_()
                        ok_ = False
                    except RuntimeError:
                        ok_ = True
                    check(f"B21 sandbox lệch ({lbl}) ⇒ RuntimeError, 0 file trong 'production'",
                          ok_ and os.listdir(prod) in ([], ["exec"], ["corp_actions.json"]),
                          os.listdir(prod))
            finally:
                cac._PROD_DATA = saved
                cac.run_vendor = REAL_VENDOR

        tmp, reg = _sandbox()
        import fcntl
        holder = open(cac.LEDGER_FILE + ".lock", "a")
        fcntl.flock(holder, fcntl.LOCK_EX)
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0
        try:
            rc = cac.run_broker(D, mode="live")
        finally:
            cac.LOCK_WAIT_S = saved_wait
            holder.close()
        check("B22 khoá EX đang bị giữ ⇒ rc=1, 0 ghi, 0 bus",
              rc == 1 and not _ledger_lines() and not _Bus.calls and CA.load_corp_actions(reg) == [])
        holder = open(cac.LEDGER_FILE + ".lock", "a")
        fcntl.flock(holder, fcntl.LOCK_SH)                    # tiến trình khác giữ khoá CHIA SẺ
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0
        try:
            rc = cac.run_broker(D, mode="live")
        finally:
            cac.LOCK_WAIT_S = saved_wait
            holder.close()
        check("B22b khoá phải là ĐỘC QUYỀN (SH đang giữ ⇒ không vào được)",
              rc == 1 and not _ledger_lines())
    finally:
        subprocess.run = real_run
        cac._px_cum_fn = REAL_PX_FN
        cac._exchange_fn = REAL_EXCH_FN
        cac.write_corp_actions = REAL_WRITE


def test_v4():
    """Vòng sửa+verify sau arch-review v3 (job Taylor_20261003_064854): N9 (REVOKED / idempotent /
    dry-run / ex TRƯỚC) + 11 đột biến sống. Mỗi assertion có TÊN, mỗi đột biến tương ứng ở MUTANTS."""
    import fcntl
    import types
    real_run, saved_vendor = subprocess.run, cac.run_vendor
    saved_env = os.environ.get("MIKE_CA_BROKER_SOURCE")
    cac.run_vendor = REAL_VENDOR
    subprocess.run = _Bus.run
    brec = {"id": "TPB-2026-10-05-BROKER-SHARE-EVENT", "ticker": "TPB", "event_type": "BONUS_ISSUE",
            "qty_multiplier": 1.15, "ex_date": "2026-10-05",
            "broker_effective_ts": "2026-10-02T12:03:01", "_status": "CONFIRMED — broker",
            "provenance": "broker"}
    vcal = [{"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
             "exercise_ratio": 0.15, "days_ahead": 1}]

    def vq():
        return [t for t in _kinds("question") if "vendor-vs-broker-TPB" in t]

    def done_keys():
        return [x["key"] for x in _ledger_lines() if x.get("kind") == "done"
                and x["key"][0] == "vendor-vs-broker"]
    try:
        # ── N9: chỉ record CONFIRMED khoá vendor ──
        for st in ("REVOKED — người thu hồi (sai ex)", "PROPOSED — chờ"):
            tmp, reg = _sandbox([dict(brec, _status=st)], vendor=vcal)
            cac.run_vendor(D)
            check(f"V1 N9 record broker {st[:8]} ⇒ KHÔNG khoá vendor, KHÔNG hỏi", not vq(), _Bus.calls)
        # ── N9: trước HOẶC sau đều chặn ──
        for ex_b, lbl in (("2026-10-05", "SAU"), ("2026-09-30", "TRƯỚC")):
            tmp, reg = _sandbox([dict(brec, ex_date=ex_b)], vendor=vcal)
            h0 = _sha(reg)
            cac.run_vendor(D)
            check(f"V2 N9 record broker CONFIRMED ex {lbl} ex vendor ⇒ không ghi, hỏi đúng 1 lần",
                  _sha(reg) == h0 and len(vq()) == 1, _Bus.calls)
        # ── N9: idempotent (hỏi 1 lần, bus rc=0 ⇒ done; lượt sau im) ──
        tmp, reg = _sandbox([brec], vendor=vcal)
        cac.run_vendor(D)
        n = len(_Bus.calls)
        cac.run_vendor(D)
        check("V3 N9 hỏi vendor-vs-broker idempotent: lượt 2 không gửi lại, sổ có đúng 1 done",
              len(vq()) == 1 and len(_Bus.calls) == n
              and done_keys() == [["vendor-vs-broker", "TPB", EX, brec["id"], "ASKED"]],
              (_Bus.calls, _ledger_lines()))
        # ── N9: bus lỗi ⇒ KHÔNG đánh dấu done ⇒ lượt sau hỏi lại ──
        tmp, reg = _sandbox([brec], vendor=vcal)
        _Bus.rc = 1
        cac.run_vendor(D)
        check("V3b N9 bus lỗi ⇒ sổ KHÔNG có done", not done_keys(), _ledger_lines())
        _Bus.rc, _Bus.calls = 0, []
        cac.run_vendor(D)
        check("V3c N9 lượt sau bus ổn ⇒ hỏi lại + done", len(vq()) == 1 and len(done_keys()) == 1,
              (_Bus.calls, _ledger_lines()))
        # ── N9: dry-run KHÔNG gửi bus, KHÔNG ghi sổ, KHÔNG ghi registry ──
        tmp, reg = _sandbox([brec], vendor=vcal)
        h0 = _sha(reg)
        cac.run_vendor(D, dry_run=True)
        check("V4 N9 vendor --dry-run ⇒ 0 bus, 0 sổ, registry y nguyên",
              not _Bus.calls and not _ledger_lines() and _sha(reg) == h0, (_Bus.calls, _ledger_lines()))

        # ── _exchange_fn THẬT (không stub): exchange_known / lỗi ⇒ None, KHÔNG mặc định HOSE ──
        state = {}

        class _Q:
            exchange = "HOSE"           # giá trị mặc định mà Quote.exchange trả khi không biết sàn

        def get_quote(tk):
            if state.get("raise"):
                raise ConnectionError("DNSE sập (giả)")
            q = _Q()
            q.exchange_known = state["known"]
            return q
        fake_b = types.ModuleType("trading_bot.brokers")
        fake_b.get_quote_source = lambda name: types.SimpleNamespace(get_quote=get_quote,
                                                                     connect=lambda: None)
        fake_pkg = types.ModuleType("trading_bot")
        fake_pkg.__path__ = []
        saved_mods = {k: sys.modules.get(k) for k in ("trading_bot", "trading_bot.brokers")}
        sys.modules["trading_bot"], sys.modules["trading_bot.brokers"] = fake_pkg, fake_b
        try:
            state["known"] = False
            check("V5 _exchange_fn: exchange_known=False ⇒ None (không tin Quote.exchange mặc định HOSE)",
                  REAL_EXCH_FN()("TPB") is None)
            state["known"] = True
            check("V5b _exchange_fn: exchange_known=True ⇒ sàn thật", REAL_EXCH_FN()("TPB") == "HOSE")
            state["raise"] = True
            check("V5c _exchange_fn: DNSE lỗi ⇒ None (không mặc định HOSE)", REAL_EXCH_FN()("TPB") is None)
        finally:
            for k, v in saved_mods.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v

        # ── khoá bao cả hai nhánh trong run() ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "shadow"
        probe = {}

        def lock_free():
            fh = open(cac.LEDGER_FILE + ".lock", "a")
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except BlockingIOError:
                return False
            finally:
                fh.close()
        saved_scan = BD.scan_day

        def spy_vendor(date_str, dry_run=False):
            probe["lock_existed"] = os.path.exists(cac.LEDGER_FILE + ".lock")
            probe["vendor"] = lock_free()
            return 0

        def spy_scan(*a, **k):
            probe["broker"] = lock_free()
            return saved_scan(*a, **k)
        tmp, reg = _sandbox()
        cac.run_vendor, BD.scan_day = spy_vendor, spy_scan
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0
        try:
            rc = cac.run(D)
        finally:
            cac.LOCK_WAIT_S = saved_wait
            cac.run_vendor, BD.scan_day = REAL_VENDOR, saved_scan
        check("V6 run(): nhánh vendor chạy DƯỚI khoá ledger (tiến trình khác không lấy được)",
              probe.get("vendor") is False, probe)
        check("V6b run(): nhánh broker chạy dưới khoá", probe.get("broker") is False, probe)
        check("V7 run_broker KHÔNG xin khoá lần 2 khi run() đã giữ (rc=0, intent+done có trong sổ)",
              rc == 0 and [x["kind"] for x in _ledger_lines()] == ["intent", "done"], (rc, _ledger_lines()))
        tmp, reg = _sandbox()
        probe.clear()
        cac.run_vendor = spy_vendor
        try:
            cac.run(D, dry_run=True)
        finally:
            cac.run_vendor = REAL_VENDOR
        check("V6c run(dry_run) không xin khoá (không tạo .lock)",
              probe.get("vendor") is True and probe.get("lock_existed") is False, probe)
        # khoá bị tiến trình khác giữ ⇒ rc=1, vendor KHÔNG chạy, có bus error (MINOR: shadow mặc định)
        tmp, reg = _sandbox()
        called = []
        cac.run_vendor = lambda *a, **k: called.append(1) or 0
        holder = open(cac.LEDGER_FILE + ".lock", "a")
        fcntl.flock(holder, fcntl.LOCK_EX)
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0
        try:
            rc = cac.run(D)
        finally:
            cac.LOCK_WAIT_S = saved_wait
            holder.close()
            cac.run_vendor = REAL_VENDOR
        check("V8 run() không lấy được khoá ⇒ rc=1, vendor KHÔNG chạy, sổ rỗng", rc == 1 and not called
              and not _ledger_lines(), (rc, called))
        check("V8b shadow không lấy được khoá ⇒ bus QUESTION corp-action-lock-unavailable (1 lần, "
              "không phải error — v4 #3)",
              _kinds("question") == [f"corp-action-lock-unavailable-{D}"] and not _kinds("error"),
              _Bus.calls)

        # ── _close_stale_questions: đóng ĐỦ 3 verdict, CHỈ đúng (live, mã, phiên) ──
        def old_intent(mode, tk, day, v):
            e = {"kind": "intent", "mode": mode, "ticker": tk, "credit_day": day, "ex_date": EX,
                 "verdict": v, "why": "seed"}
            return [e, {"kind": "done", "key": [mode, tk, day, v], "at": "2026-10-02T19:25:00+07:00"}]
        seed = []
        for v in (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR):
            seed += old_intent("live", "TPB", D, v)
        seed += old_intent("shadow", "TPB", D, BD.INSUFFICIENT)                 # khác mode
        seed += old_intent("live", "VPB", D, BD.INSUFFICIENT)                   # khác mã
        seed += old_intent("live", "TPB", PREV, BD.INSUFFICIENT)                # khác phiên
        seed += old_intent("live", "TPB", D, BD.CONFIRMABLE)[:0]
        tmp, reg = _sandbox()
        _ledger_write(seed)
        rc = cac.run_broker(D, mode="live")
        want = sorted(f"corp-action-broker-{v.lower()}-TPB-{D}"
                      for v in (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR))
        check("V9 _close_stale_questions đóng ĐỦ 3 verdict (INSUFFICIENT/AMBIGUOUS/DEFER_VENDOR) "
              "và CHỈ cùng (live, mã, phiên)", rc == 0 and sorted(_kinds("answer")) == want,
              (rc, _kinds("answer")))
        # registry không có record sau "ghi" ⇒ KHÔNG đóng câu hỏi cũ
        tmp, reg = _sandbox()
        _ledger_write(old_intent("live", "TPB", D, BD.INSUFFICIENT))
        cac.write_corp_actions = lambda *a, **k: None
        try:
            rc = cac.run_broker(D, mode="live")
        finally:
            cac.write_corp_actions = REAL_WRITE
        check("V9b registry KHÔNG có record ⇒ KHÔNG đóng question cũ (không answer giả)",
              rc == 1 and _kinds("answer") == [], (rc, _Bus.calls))

        # ── _bus: timeout truyền xuống subprocess + timeout ≠ đã gửi ──
        seen = {}

        def timing_out(cmd, **kw):
            seen.update(kw)
            raise subprocess.TimeoutExpired(cmd, kw.get("timeout", 0))
        subprocess.run = timing_out
        r_bus = cac._bus("finding", "t", {})
        check("V10 _bus: truyền timeout=BUS_TIMEOUT_S cho subprocess", seen.get("timeout") == cac.BUS_TIMEOUT_S
              and cac.BUS_TIMEOUT_S > 0, seen)
        check("V10b _bus: treo quá timeout ⇒ rc≠0 (KHÔNG coi như đã gửi)", r_bus != 0, r_bus)
        tmp, reg = _sandbox()
        rc = cac.run_broker(D, mode="shadow")
        check("V10c bus treo ⇒ run_broker rc=1, sổ KHÔNG có done (lượt sau gửi bù)",
              rc == 1 and [x["kind"] for x in _ledger_lines()] == ["intent"], (rc, _ledger_lines()))
        subprocess.run = _Bus.run

        # ── đọc lại registry hỏng (shadow, không có CONFIRMABLE live để che rc) ⇒ rc=1 ──
        broken = {"id": "X", "ticker": "VHM", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 13,
                  "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05", "_status": "CONFIRMED"}
        tmp, reg = _sandbox([broken])
        rc = cac.run_broker(D, mode="shadow")
        check("V11 shadow + registry hỏng khi đọc lại ⇒ rc=1 (không rc=0 im lặng)", rc == 1, rc)

        # ── dòng sổ định dạng cũ (không có 'key') ở trạng thái dở ⇒ gửi bù, không KeyError ──
        tmp, reg = _sandbox()
        _ledger_write([{"kind": "intent", "mode": "shadow", "ticker": "TPB",
                        "credit_day": D, "ex_date": EX, "verdict": BD.CONFIRMABLE,
                        "why": "định dạng cũ, không có key"}])
        try:
            rc = cac.run_broker(D, mode="shadow")
            ok_ = True
        except KeyError as e:
            rc, ok_ = None, False
            print(f"  KeyError {e}")
        check("V12 dòng sổ cũ không có 'key' ⇒ không KeyError, gửi bù + done đúng key",
              ok_ and rc == 0 and _kinds("finding") == [f"corp-action-broker-shadow-{D}"]
              and [x["key"] for x in _ledger_lines() if x["kind"] == "done"]
              == [["shadow", "TPB", D, BD.CONFIRMABLE]], (rc, _Bus.calls, _ledger_lines()))
    finally:
        subprocess.run = real_run
        cac.run_vendor = saved_vendor
        BD.scan_day = saved_scan if "saved_scan" in dir() else BD.scan_day
        cac.write_corp_actions = REAL_WRITE
        cac._px_cum_fn, cac._exchange_fn = REAL_PX_FN, REAL_EXCH_FN
        if saved_env is None:
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        else:
            os.environ["MIKE_CA_BROKER_SOURCE"] = saved_env


def test_v5():
    """Vòng sửa sau arch-review v4 (job Taylor_20261003_082621) — 12 mục. Mỗi assertion R* có TÊN,
    mỗi đột biến tương ứng ở MUTANTS (khối '── vòng v4 ──')."""
    import contextlib
    import fcntl
    import io
    real_run, saved_vendor, saved_scan = subprocess.run, cac.run_vendor, BD.scan_day
    saved_env = os.environ.get("MIKE_CA_BROKER_SOURCE")
    saved_append, saved_bus, saved_prod = BD.ledger_append, cac._bus, cac._PROD_DATA
    subprocess.run = _Bus.run
    brec = {"id": "TPB-2026-10-05-BROKER-SHARE-EVENT", "ticker": "TPB", "event_type": "BONUS_ISSUE",
            "qty_multiplier": 1.15, "ex_date": "2026-10-05",
            "broker_effective_ts": "2026-10-02T12:03:01", "_status": "CONFIRMED — broker",
            "provenance": "broker"}
    vcal = {"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
            "exercise_ratio": 0.15, "days_ahead": 1}
    abc_ev = dict(vcal, ticker="ABC")
    abc_ok = _abc_series(cost1=16800 / 1.15)           # vendor khớp: KL ×1,15, giá vốn ÷1,15
    abc_id = f"ABC-{EX}-BONUS-ISSUE"

    def q_topics(sub):
        return [t for t in _kinds("question") if sub in t]
    try:
        # ── #1 _exchange_fn THẬT: get_quote_source THẬT, chỉ stub get_dnse_client ──
        import trading_bot.brokers as TB
        mk = {"TPB": "STO", "UPC": "UPX", "XYZ": None}
        made = []

        class _Cli:
            def secdef(self, sym):
                row = {"symbol": sym, "boardId": "G1"}
                if mk[sym]:
                    row.update(marketId=mk[sym], basicPrice=14.4, ceilingPrice=15.4, floorPrice=13.4)
                return {"secdefs": [row]}

            def latest_trade(self, sym):
                if not mk[sym]:
                    raise ConnectionError("không có khớp (giả)")
                return {"trades": [{"boardId": "G1", "matchPrice": 14.45, "totalVolumeTraded": 1000}]}

            def latest_quote(self, sym):
                if not mk[sym]:
                    raise ConnectionError("không có sổ lệnh (giả)")
                return {"quotes": [{"boardId": "G1", "bid": [{"price": 14.4, "quantity": 100}],
                                    "offer": [{"price": 14.5, "quantity": 200}]}]}

        def fake_client(credentials_file=None):
            if made == ["boom"]:
                raise ConnectionError("DNSE login lỗi (giả)")
            made.append(1)
            return _Cli()
        raw_dir = _mkdtemp("brokerca_tbexec_")
        saved_tb = (TB.get_dnse_client, TB.EXEC_DIR, dict(TB._QUOTE_POOL))
        TB.get_dnse_client, TB.EXEC_DIR = fake_client, raw_dir
        TB._QUOTE_POOL.clear()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn = REAL_EXCH_FN()
                got = {tk: fn(tk) for tk in ("TPB", "UPC", "XYZ", "TPB")}
            check("R1 _exchange_fn THẬT: connect() ⇒ STO→HOSE, UPX→UPCOM, mã không marketId ⇒ None",
                  got == {"TPB": "HOSE", "UPC": "UPCOM", "XYZ": None}, got)
            check("R1b connect ĐÚNG 1 lần cho cả lượt (pool client)", made == [1], made)
            check("R1c KHÔNG ghi dòng nào vào dnse_raw (quote_l2/quote_unmapped) — file kế toán",
                  os.listdir(raw_dir) == [], os.listdir(raw_dir))
            TB._QUOTE_POOL.clear()
            made[:] = ["boom"]
            with contextlib.redirect_stdout(io.StringIO()):
                fn = REAL_EXCH_FN()
                got = [_call("R1d connect lỗi ⇒ None cho mọi mã, không ném", fn, tk) for tk in ("TPB", "UPC")]
            check("R1d connect lỗi ⇒ None cho mọi mã, không ném", got == [None, None], got)
            # đầu-cuối: run_broker --dry-run với _exchange_fn THẬT ⇒ TPB CONFIRMABLE (không AMBIGUOUS)
            TB._QUOTE_POOL.clear()
            made[:] = []
            tmp, reg = _sandbox()
            cac._exchange_fn = REAL_EXCH_FN
            before = sorted(os.listdir(cac.EXEC_DIR))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cac.run_broker(D, dry_run=True, mode="live")
            check("R1e run_broker --dry-run + _exchange_fn THẬT ⇒ TPB CONFIRMABLE ×1.15",
                  f"TPB ex {EX} {BD.CONFIRMABLE} ×1.15" in out.getvalue(), out.getvalue()[-600:])
            check("R1f --dry-run: 0 bus, 0 sổ, 0 file mới ở exec sandbox lẫn dnse_raw",
                  not _Bus.calls and not _ledger_lines() and sorted(os.listdir(cac.EXEC_DIR)) == before
                  and os.listdir(raw_dir) == [], (os.listdir(raw_dir), _Bus.calls))
        finally:
            TB.get_dnse_client, TB.EXEC_DIR = saved_tb[0], saved_tb[1]
            TB._QUOTE_POOL.clear()
            TB._QUOTE_POOL.update(saved_tb[2])
            cac._exchange_fn = lambda: (lambda tk: "HOSE")

        # ── #2/#8 broker crash (KHÔNG chỉ ZeroDivisionError) ⇒ vendor VẪN chạy TRƯỚC và ghi registry ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "live"
        for exc in (RuntimeError("detector nổ (giả)"), OSError("đĩa lỗi (giả)")):
            tmp, reg = _sandbox(vendor=[abc_ev], extra=abc_ok)
            order = []

            def spy_vendor(d, dry_run=False):
                order.append("vendor")
                return REAL_VENDOR(d, dry_run=dry_run)

            def crash(*a, **k):
                order.append("broker")
                raise exc
            cac.run_vendor, BD.scan_day = spy_vendor, crash
            try:
                rc = cac.run(D)
                raised = None
            except Exception as e:     # noqa: BLE001 — chính là điều cần bắt
                rc, raised = None, e
            finally:
                cac.run_vendor, BD.scan_day = REAL_VENDOR, saved_scan
            ids = [a["id"] for a in CA.load_corp_actions(reg)]
            nm = type(exc).__name__
            check(f"R2 broker crash {nm} ⇒ run_vendor ĐƯỢC GỌI, chạy TRƯỚC broker",
                  order == ["vendor", "broker"], order)
            check(f"R2b broker crash {nm} ⇒ registry CÓ record vendor {abc_id} + rc=1, không ném",
                  raised is None and rc == 1 and ids == [abc_id], (rc, raised, ids))
            check(f"R2c broker crash {nm} ⇒ 1 bus QUESTION broker-crash (r5 M-B), 0 error",
                  len(q_topics("broker-crash")) == 1 and not _kinds("error"), _Bus.calls)

        # ── #5 lịch vendor THIẾU / chỉ _FAILED ⇒ AMBIGUOUS (fail-closed) ──
        for lbl, failed_file in (("không có file", False), ("chỉ _FAILED.json", True)):
            tmp, reg = _sandbox(vendor=MISSING)
            if failed_file:
                with open(os.path.join(cac.CA_DAILY_DIR, f"corp_action_daily_{D}_FAILED.json"), "w") as f:
                    json.dump({"status": "FAILED", "upcoming_events_held": []}, f)
            with contextlib.redirect_stdout(io.StringIO()):
                cac.run_broker(D, mode="live")
            lg = [x for x in _ledger_lines() if x["kind"] == "intent"]
            check(f"R3 lịch vendor {lbl} ⇒ AMBIGUOUS + question, 0 ghi registry",
                  CA.load_corp_actions(reg) == [] and [x["verdict"] for x in lg] == [BD.AMBIGUOUS]
                  and len(q_topics("ambiguous-TPB")) == 1, (lg, _Bus.calls))

        # ── #6 lỗi ở đường hỏi N9 KHÔNG làm mất lô vendor ──
        for lbl in ("ledger_append OSError", "_bus ValueError"):
            tmp, reg = _sandbox([brec], vendor=[vcal, abc_ev], extra=abc_ok)
            if lbl.startswith("ledger"):
                def bad_append(*a, **k):
                    raise OSError("sổ không ghi được (giả)")
                BD.ledger_append = bad_append
            else:
                def bad_bus(kind, topic, payload):
                    if "vendor-vs-broker" in topic:
                        raise ValueError("payload lạ (giả)")
                    return saved_bus(kind, topic, payload)
                cac._bus = bad_bus
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = cac.run_vendor(D)
                raised = None
            except Exception as e:     # noqa: BLE001
                rc, raised = None, e
            finally:
                BD.ledger_append, cac._bus = saved_append, saved_bus
            ids = [a["id"] for a in CA.load_corp_actions(reg)]
            qf = [c for c in _Bus.calls if c[2] == "question" and "vendor-ask-failed" in c[3]]
            check(f"R4 N9 lỗi ({lbl}) ⇒ lô vendor VẪN ghi {abc_id}, không ném",
                  raised is None and abc_id in ids, (raised, ids))
            check(f"R4b N9 lỗi ({lbl}) ⇒ rc=1 + 1 bus question urgency high vendor-ask-failed",
                  rc == 1 and len(qf) == 1 and json.loads(qf[0][4])["urgency"] == "high",
                  (rc, _Bus.calls))

        # ── #7 sổ hỏng ⇒ VẪN hỏi (an toàn) ──
        tmp, reg = _sandbox([brec], vendor=[vcal])
        open(cac.LEDGER_FILE, "w").write('{"kind": "done"\n')
        with contextlib.redirect_stdout(io.StringIO()):
            cac.run_vendor(D)
        check("R5 sổ broker hỏng ⇒ vẫn hỏi vendor-vs-broker (không im)",
              len(q_topics("vendor-vs-broker-TPB")) == 1, _Bus.calls)

        # ── #9 khoá ASKED có id record broker: REVOKE + record broker MỚI ⇒ hỏi lại ──
        tmp, reg = _sandbox([brec], vendor=[vcal])
        with contextlib.redirect_stdout(io.StringIO()):
            cac.run_vendor(D)
            json.dump({"actions": [dict(brec, _status="REVOKED — người thu hồi"),
                                   dict(brec, id="TPB-2026-10-05-BROKER-NEW")]}, open(reg, "w"))
            cac.run_vendor(D)
            cac.run_vendor(D)
        check("R6 record broker mới (id khác) sau REVOKE ⇒ hỏi lại đúng 1 lần (tổng 2), lượt 3 im",
              len(q_topics("vendor-vs-broker-TPB")) == 2, _Bus.calls)

        # ── #12 vendor CÙNG ex, KHÁC tỉ lệ so với record broker ⇒ WARNING + hỏi 1 lần ──
        bsame = dict(brec, id="TPB-BROKER-SAME-EX", ex_date=EX)
        tmp, reg = _sandbox([bsame], vendor=[dict(vcal, exercise_ratio=0.16)])
        h0 = _sha(reg)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cac.run_vendor(D)
            cac.run_vendor(D)
        qq = [c for c in _Bus.calls if c[2] == "question"]
        check("R7 vendor ×1.16 vs record broker ×1.15 cùng ex ⇒ 1 question ratio-vs-broker (2 lượt), "
              "registry y nguyên, có WARNING",
              _sha(reg) == h0 and len(q_topics("vendor-ratio-vs-broker-TPB")) == 1 and len(qq) == 1
              and "WARNING" in out.getvalue(), (_Bus.calls, out.getvalue()[-400:]))
        tmp, reg = _sandbox([bsame], vendor=[dict(vcal, exercise_ratio=0.16)])
        with contextlib.redirect_stdout(io.StringIO()):
            cac.run_vendor(D, dry_run=True)
        check("R7b --dry-run ⇒ không hỏi", not _Bus.calls, _Bus.calls)
        user16 = dict(bsame, id="TPB-USER-1.16", provenance=None, qty_multiplier=1.16)
        for lbl, regrecs, ratio in (("cùng tỉ lệ", [bsame], 0.15),
                                    ("record NGƯỜI ký", [dict(bsame, provenance=None)], 0.16),
                                    # người ký ×1.16 + record broker ×1.15 đã REVOKED cùng ex
                                    ("record broker REVOKED", [user16, dict(bsame, _status="REVOKED")],
                                     0.16)):
            tmp, reg = _sandbox(regrecs, vendor=[dict(vcal, exercise_ratio=ratio)])
            with contextlib.redirect_stdout(io.StringIO()):
                cac.run_vendor(D)
            check(f"R7c {lbl} ⇒ không hỏi ratio-vs-broker", not q_topics("ratio-vs-broker"), _Bus.calls)

        # ── #3 không lấy được khoá ⇒ QUESTION urgency high, 1 lần/ngày; bus lỗi ⇒ lượt sau hỏi lại ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "shadow"
        tmp, reg = _sandbox()
        holder = open(cac.LEDGER_FILE + ".lock", "a")
        fcntl.flock(holder, fcntl.LOCK_EX)
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rcs = [cac.run(D), cac.run(D)]
                qq = [c for c in _Bus.calls if c[2] == "question"]
                check("R8 khoá bị giữ ⇒ rc=1 + đúng 1 question urgency high qua 2 lượt cùng ngày",
                      rcs == [1, 1] and len(qq) == 1 and "lock-unavailable" in qq[0][3]
                      and json.loads(qq[0][4])["urgency"] == "high", (rcs, _Bus.calls))
                tmp2, reg2 = _sandbox()
                holder2 = open(cac.LEDGER_FILE + ".lock", "a")
                fcntl.flock(holder2, fcntl.LOCK_EX)
                _Bus.rc = 1
                cac.run(D)
                _Bus.rc, _Bus.calls = 0, []
                cac.run(D)
                holder2.close()
            check("R8b bus lỗi lần đầu ⇒ lượt sau HỎI LẠI (marker không giữ)",
                  len(q_topics("lock-unavailable")) == 1, _Bus.calls)
        finally:
            cac.LOCK_WAIT_S = saved_wait
            holder.close()

        # ── #10 bq_unadjusted_close có timeout ──
        seen = {}

        def bq_hang(cmd, **kw):
            seen.update(kw)
            raise subprocess.TimeoutExpired(cmd, kw.get("timeout", 0))
        subprocess.run = bq_hang
        try:
            BD.bq_unadjusted_close({("TPB", PREV)})
            ok_ = False
        except RuntimeError:
            ok_ = True
        finally:
            subprocess.run = _Bus.run
        check("R9 bq_unadjusted_close truyền timeout>0 và treo ⇒ RuntimeError (không treo vô hạn)",
              ok_ and seen.get("timeout") == BD.BQ_TIMEOUT_S and BD.BQ_TIMEOUT_S > 0, seen)

        # ── #4 --mutations TỪ CHỐI cây canonical ──
        canon = os.path.join(cac.MIKE_ROOT, "bin")
        link = os.path.join(_mkdtemp("brokerca_link_"), "bin")
        os.symlink(canon, link)
        check("R10 _mutation_refusal: cây canonical mike/bin ⇒ từ chối", _mutation_refusal(canon) is not None)
        check("R10b symlink tới canonical ⇒ vẫn từ chối (realpath)", _mutation_refusal(link) is not None)
        check("R10c worktree khác ⇒ cho chạy", _mutation_refusal("/tmp/wt-x/bin", canon) is None)
        fake_canon = _mkdtemp("brokerca_fakecanon_")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                r_ = run_mutations(here=fake_canon, canon=fake_canon)
            ok_ = r_ is False
        except Exception as e:      # noqa: BLE001 — guard bị bỏ ⇒ đi mở file không tồn tại
            ok_ = False
            print(f"  run_mutations ném {type(e).__name__}: {e}")
        check("R10d run_mutations trên cây 'canonical' ⇒ trả False TRƯỚC khi chạm file",
              ok_ and os.listdir(fake_canon) == [], os.listdir(fake_canon))

        # ── SandboxMismatch KHÔNG bị _ask_guarded nuốt ──
        tmp, reg = _sandbox([brec], vendor=[vcal])
        prod = os.path.join(tmp, "PROD")
        os.makedirs(prod)
        cac._PROD_DATA = os.path.realpath(prod)
        cac.LEDGER_FILE = os.path.join(prod, "ledger.jsonl")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                cac.run_vendor(D)
            ok_ = False
        except cac.SandboxMismatch:
            ok_ = True
        finally:
            cac._PROD_DATA = saved_prod
        check("R11 sandbox lệch trong đường hỏi N9 ⇒ SandboxMismatch lan ra, 0 file 'production'",
              ok_ and os.listdir(prod) == [], os.listdir(prod))
    finally:
        subprocess.run = real_run
        cac.run_vendor, BD.scan_day = saved_vendor, saved_scan
        BD.ledger_append, cac._bus, cac._PROD_DATA = saved_append, saved_bus, saved_prod
        cac.write_corp_actions = REAL_WRITE
        cac._px_cum_fn, cac._exchange_fn = REAL_PX_FN, REAL_EXCH_FN
        if saved_env is None:
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        else:
            os.environ["MIKE_CA_BROKER_SOURCE"] = saved_env


# Bản sao Y NGUYÊN cấu trúc data/corp_action_daily/corp_action_daily_2026-10-02_FAILED.json THẬT
# (đọc 2026-10-03; chỉ đổi asof cho ngày D của sandbox).
FEED_DEAD_FIXTURE = {
    "asof": "2026-10-02", "status": "FAILED", "usable": False, "failed_gate": "feed_dead",
    "feed": {"max_ingested_utc": "2026-09-26 15:43:40.417516+00",
             "max_ingested_ict": "2026-09-26T22:43:40+07:00", "max_public_date": "2026-09-25",
             "rows": "36428", "age_days": 6, "prev_trading_day": "2026-10-01",
             "reason": "lần nạp gần nhất cũ 6 ngày (> 5) — bảng không còn refresh"},
    "selfcheck": [{"module": "corp_action_lib", "rc": 0, "tail": ["OK — corp_action_lib selfcheck PASS"]},
                  {"module": "oshares_live", "rc": 0, "tail": ["OK — oshares_live selfcheck PASS 102/102"]}],
    "generated_at": "2026-10-02T07:30:01+07:00", "model_version": "c26072b13a59"}


def _put_failed(content, day=None):
    day = day or D
    with open(os.path.join(cac.CA_DAILY_DIR, f"corp_action_daily_{day}_FAILED.json"), "w",
              encoding="utf-8") as f:
        f.write(content if isinstance(content, str) else json.dumps(content))


def test_v6():
    """Vòng r5 (job Taylor_20261003_091511): M-A feed_dead ⇒ broker vẫn CONFIRMABLE, M-B/M-C crash
    từng nhánh độc lập + question, M-D marker claim/sent/prune, và 9 đột biến sống của r4 (Q3-Q21)
    — mỗi assertion CÓ TÊN, mỗi đột biến ở MUTANTS (khối '── vòng r5 ──')."""
    import contextlib
    import fcntl
    import io
    saved_vendor, saved_scan, saved_env = cac.run_vendor, BD.scan_day, os.environ.get("MIKE_CA_BROKER_SOURCE")
    saved_append, saved_bus, real_run = BD.ledger_append, cac._bus, subprocess.run
    subprocess.run = _Bus.run
    brec = {"id": "TPB-2026-10-05-BROKER-SHARE-EVENT", "ticker": "TPB", "event_type": "BONUS_ISSUE",
            "qty_multiplier": 1.15, "ex_date": "2026-10-05", "_status": "CONFIRMED — broker",
            "provenance": "broker"}
    vcal = {"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
            "exercise_ratio": 0.15, "days_ahead": 1}
    bsame = dict(brec, id="TPB-BROKER-SAME-EX", ex_date=EX)
    quiet = contextlib.redirect_stdout

    def q_topics(sub):
        return [t for t in _kinds("question") if sub in t]

    def marker(tag, day=D):
        return f"{cac.LEDGER_FILE}.{tag}-{day}"
    try:
        # ── M-A: _FAILED feed_dead ⇒ lịch vendor RỖNG + cờ; gate khác / thiếu / hỏng ⇒ UNREADABLE ──
        real_fx = os.path.join(REAL_CA_DIR, "corp_action_daily_2026-10-02_FAILED.json")
        if os.path.exists(real_fx):
            real = json.load(open(real_fx, encoding="utf-8"))
            check("F0 fixture feed_dead KHỚP cấu trúc file THẬT 2026-10-02_FAILED (key + failed_gate)",
                  set(real) == set(FEED_DEAD_FIXTURE) and real["failed_gate"] == "feed_dead"
                  and set(real["feed"]) == set(FEED_DEAD_FIXTURE["feed"]), sorted(real))
        tmp, reg = _sandbox(vendor=MISSING)
        _put_failed(FEED_DEAD_FIXTURE)
        out = io.StringIO()
        with quiet(out):
            cac.run_broker(D, dry_run=True, mode="live")
        check("F1 --dry-run, lịch vendor ngày D CHỈ có _FAILED feed_dead (file thật) ⇒ TPB CONFIRMABLE ×1.15",
              f"TPB ex {EX} {BD.CONFIRMABLE} ×1.15" in out.getvalue(), out.getvalue()[-500:])
        check("F1b dry-run in cờ VENDOR_FEED_DEAD 'vendor feed chết, broker là nguồn xác định'",
              "VENDOR_FEED_DEAD" in out.getvalue() and "broker là nguồn xác định" in out.getvalue(),
              out.getvalue()[-500:])
        fn = cac._vendor_events_fn(D)
        check("F1c _vendor_events_fn feed_dead ⇒ [] cho mọi mã + thuộc tính feed_dead=True",
              fn("TPB") == [] and getattr(fn, "feed_dead", False) is True, fn("TPB"))
        with quiet(io.StringIO()):
            cac.run_broker(D, mode="live")
        lg = [x for x in _ledger_lines() if x["kind"] == "intent"]
        recs = CA.load_corp_actions(reg)
        check("F2 live + feed_dead ⇒ 1 intent CONFIRMABLE trong sổ có vendor_feed_dead=True + why gắn cờ",
              len(lg) == 1 and lg[0]["verdict"] == BD.CONFIRMABLE and lg[0].get("vendor_feed_dead") is True
              and cac.FEED_DEAD_TAG in lg[0]["why"], lg)
        check("F2b record registry ghi + evidence mang dòng VENDOR_FEED_DEAD",
              len(recs) == 1 and cac.FEED_DEAD_TAG in recs[0]["evidence"], [r["id"] for r in recs])
        tmp, reg = _sandbox()
        with quiet(io.StringIO()):
            cac.run_broker(D, mode="live")
        lg = [x for x in _ledger_lines() if x["kind"] == "intent"]
        check("F2c feed KHÔNG chết (file thường) ⇒ cờ vendor_feed_dead=False, why không gắn cờ",
              len(lg) == 1 and lg[0].get("vendor_feed_dead") is False and "VENDOR_FEED_DEAD" not in lg[0]["why"],
              lg)
        for lbl, content, failed_present in (
                ("_FAILED gate KHÁC (selfcheck)", dict(FEED_DEAD_FIXTURE, failed_gate="selfcheck"), True),
                ("_FAILED thiếu failed_gate", {k: v for k, v in FEED_DEAD_FIXTURE.items() if k != "failed_gate"}, True),
                ("_FAILED hỏng (không parse được)", '{"failed_gate": "feed_dead"', True),
                ("_FAILED là list, không phải object", '[1, 2]', True),
                ("KHÔNG có file nào", None, False)):
            tmp, reg = _sandbox(vendor=MISSING)
            if failed_present:
                _put_failed(content)
            out = io.StringIO()
            with quiet(out):
                r_ = _call(f"F3 {lbl} ⇒ không ném", cac.run_broker, D, mode="live")
            lg = [x for x in _ledger_lines() if x["kind"] == "intent"]
            check(f"F3 {lbl} ⇒ GIỮ VENDOR_UNREADABLE: AMBIGUOUS + 0 ghi registry + không cờ feed_dead",
                  r_ is not _CRASHED and [x["verdict"] for x in lg] == [BD.AMBIGUOUS]
                  and CA.load_corp_actions(reg) == [] and not lg[0].get("vendor_feed_dead")
                  and "MƠ HỒ" in out.getvalue(), (lg, out.getvalue()[-300:]))
        tmp, reg = _sandbox(vendor=[vcal])
        _put_failed(FEED_DEAD_FIXTURE)
        fn = cac._vendor_events_fn(D)
        check("F4 file lịch THƯỜNG và _FAILED cùng tồn tại ⇒ file thường thắng (không cờ feed_dead)",
              [e["event_code"] for e in fn("TPB")] == ["ISS"] and not getattr(fn, "feed_dead", False), fn("TPB"))

        # ── M-B: broker crash ⇒ QUESTION urgency high, 1 lần/ngày, độc lập từng ngày/nhánh ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "live"

        def boom(*a, **k):
            raise RuntimeError("detector nổ (giả)")
        tmp, reg = _sandbox()
        BD.scan_day = boom
        try:
            with quiet(io.StringIO()):
                rcs = [_call("G1 run lần 1", cac.run, D), _call("G1 run lần 2", cac.run, D)]
                _call("G1 ngày khác", cac.run, EX)
        finally:
            BD.scan_day = saved_scan
        qq = [c for c in _Bus.calls if c[2] == "question" and "broker-crash" in c[3]]
        check("G1 broker crash 2 lượt cùng ngày ⇒ rc=1 cả hai, ĐÚNG 1 question broker-crash-D urgency high",
              rcs == [1, 1] and [c[3] for c in qq if D in c[3]] == [f"corp-action-broker-crash-{D}"]
              and json.loads(qq[0][4])["urgency"] == "high", (rcs, _Bus.calls))
        check("G1b marker per-ngày: chạy NGÀY KHÁC ⇒ hỏi thêm 1 (tổng 2), 0 error",
              len(qq) == 2 and not _kinds("error"), _Bus.calls)
        # bus lỗi (rc≠0) ⇒ lượt sau hỏi lại; bus ném ⇒ cũng vậy (Q4)
        for lbl in ("rc≠0", "ném"):
            tmp, reg = _sandbox()
            BD.scan_day = boom
            if lbl == "rc≠0":
                _Bus.rc = 1
            else:
                def bus_raise(kind, topic, payload):
                    if "broker-crash" in topic:
                        raise ValueError("bus nổ (giả)")
                    return saved_bus(kind, topic, payload)
                cac._bus = bus_raise
            try:
                with quiet(io.StringIO()):
                    _call(f"Q4 bus {lbl} lượt 1", cac.run, D)
                    left = os.path.exists(marker("brokercrash"))
                    _Bus.rc, _Bus.calls = 0, []
                    cac._bus = saved_bus
                    _call(f"Q4 bus {lbl} lượt 2", cac.run, D)
            finally:
                BD.scan_day = saved_scan
                cac._bus = saved_bus
                _Bus.rc = 0
            check(f"Q4 bus {lbl} khi báo crash ⇒ marker KHÔNG còn + lượt sau HỎI LẠI (không im vĩnh viễn)",
                  not left and len(q_topics("broker-crash")) == 1, (left, _Bus.calls))
        check("G1c sau khi bus nhận (rc=0) marker có nội dung 'sent' (không chỉ claim rỗng)",
              os.path.exists(marker("brokercrash")) and open(marker("brokercrash")).read().strip() == "sent")

        # ── M-C: vendor crash ⇒ broker VẪN chạy độc lập + question vendor-crash ──
        tmp, reg = _sandbox()

        def vend_boom(d, dry_run=False):
            raise OSError("vendor nổ (giả)")
        cac.run_vendor = vend_boom
        try:
            with quiet(io.StringIO()):
                rc = _call("H1 vendor crash", cac.run, D)
        finally:
            cac.run_vendor = saved_vendor
        lg = [x for x in _ledger_lines() if x["kind"] == "intent"]
        check("H1 vendor crash ⇒ nhánh broker VẪN chạy: TPB CONFIRMABLE ghi registry, rc=1",
              rc == 1 and [x["verdict"] for x in lg] == [BD.CONFIRMABLE]
              and len(CA.load_corp_actions(reg)) == 1, (rc, lg))
        check("H1b vendor crash ⇒ đúng 1 question vendor-crash urgency high (không error)",
              len(q_topics("vendor-crash")) == 1 and not _kinds("error")
              and json.loads([c for c in _Bus.calls if "vendor-crash" in c[3]][0][4])["urgency"] == "high",
              _Bus.calls)
        tmp, reg = _sandbox()
        cac.run_vendor, BD.scan_day = vend_boom, boom
        try:
            with quiet(io.StringIO()):
                rc = _call("H2 cả hai nhánh nổ", cac.run, D)
        finally:
            cac.run_vendor, BD.scan_day = saved_vendor, saved_scan
        check("H2 cả 2 nhánh nổ cùng ngày ⇒ 2 question RIÊNG (vendor-crash + broker-crash), rc=1",
              rc == 1 and len(q_topics("vendor-crash")) == 1 and len(q_topics("broker-crash")) == 1, _Bus.calls)
        tmp, reg = _sandbox()

        def vend_mismatch(d, dry_run=False):
            raise cac.SandboxMismatch("lệch (giả)")
        cac.run_vendor = vend_mismatch
        try:
            with quiet(io.StringIO()):
                cac.run(D)
            ok_ = False
        except cac.SandboxMismatch:
            ok_ = True
        finally:
            cac.run_vendor = saved_vendor
        check("H3 SandboxMismatch trong 1 nhánh ⇒ lan ra run(), KHÔNG bị nuốt thành question", ok_
              and not q_topics("crash"), _Bus.calls)
        out = io.StringIO()
        tmp, reg = _sandbox()
        BD.scan_day = boom
        try:
            with quiet(out):
                cac.run(D, dry_run=True)
        finally:
            BD.scan_day = saved_scan
        check("H4 --dry-run + crash ⇒ KHÔNG hỏi, KHÔNG marker", not _Bus.calls
              and not os.path.exists(marker("brokercrash")), _Bus.calls)

        # ── M-D: claim/sent/prune ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "shadow"
        saved_wait, cac.LOCK_WAIT_S = cac.LOCK_WAIT_S, 0

        def run_locked(day=D):
            tmp_, reg_ = _sandbox()
            h = open(cac.LEDGER_FILE + ".lock", "a")
            fcntl.flock(h, fcntl.LOCK_EX)
            return h

        def ask_lock(day=D):
            with quiet(io.StringIO()):
                return _call("I ask_lock", cac.run, day)
        try:
            h = run_locked()
            ask_lock()
            check("Q3 marker khoá THEO NGÀY: ngày D rồi ngày EX ⇒ 2 question lock-unavailable (mỗi ngày 1)",
                  not ask_lock(EX) is None and len(q_topics("lock-unavailable")) == 2
                  and os.path.exists(marker("lockfail", D)) and os.path.exists(marker("lockfail", EX)),
                  _Bus.calls)
            h.close()
            # kill giữa claim và bus: claim RỖNG mồ côi
            for lbl, age, content, expect in (("claim rỗng MỚI (tiến trình khác đang gửi)", 5, "", 0),
                                              ("claim rỗng CŨ > 300s (chủ bị kill)", 3600, "", 1),
                                              ("marker 'sent' CŨ cả ngày", 86400, "sent\n", 0)):
                h = run_locked()
                with open(marker("lockfail"), "w") as f:
                    f.write(content)
                t = _time.time() - age
                os.utime(marker("lockfail"), (t, t))
                ask_lock()
                check(f"I1 {lbl} ⇒ hỏi {expect} lần", len(q_topics("lock-unavailable")) == expect,
                      _Bus.calls)
                h.close()
            # bus rc≠0 ⇒ marker không còn (không để claim rỗng chặn 300s)
            h = run_locked()
            _Bus.rc = 1
            ask_lock()
            left = os.path.exists(marker("lockfail"))
            _Bus.rc, _Bus.calls = 0, []
            ask_lock()
            check("I2 bus rc≠0 ⇒ marker bị xoá, lượt kế HỎI LẠI ngay (không chờ hết 300s)",
                  not left and len(q_topics("lock-unavailable")) == 1, (left, _Bus.calls))
            check("I2b sau khi bus nhận ⇒ marker có 'sent'", open(marker("lockfail")).read().strip() == "sent")
            h.close()
            # prune: marker cũ 60 ngày xoá, marker 1 ngày + sổ + khoá cũ giữ nguyên
            h = run_locked()
            old_t = _time.time() - 60 * 86400
            files = {}
            for nm in ("lockfail-2026-08-01", "vendorcrash-2026-08-01", "brokercrash-2026-08-01"):
                files[nm] = f"{cac.LEDGER_FILE}.{nm}"
                open(files[nm], "w").write("sent\n")
                os.utime(files[nm], (old_t, old_t))
            fresh = f"{cac.LEDGER_FILE}.lockfail-2026-09-30"
            open(fresh, "w").write("sent\n")
            open(cac.LEDGER_FILE, "w").write('{"kind": "done", "key": ["x"], "at": "t"}\n')
            os.utime(cac.LEDGER_FILE, (old_t, old_t))
            ledger_before = _sha(cac.LEDGER_FILE)
            ask_lock()
            check("I3 prune: marker 3 loại cũ 60 ngày bị xoá hết",
                  not any(os.path.exists(p_) for p_ in files.values()), [p_ for p_ in files.values() if os.path.exists(p_)])
            check("I3b prune: marker 1 ngày tuổi còn", os.path.exists(fresh))
            check("I3c prune KHÔNG đụng sổ ledger (dù cũ 60 ngày): còn + y nguyên nội dung",
                  os.path.exists(cac.LEDGER_FILE) and _sha(cac.LEDGER_FILE) == ledger_before)
            h.close()
        finally:
            cac.LOCK_WAIT_S = saved_wait

        # ── Q5/Q6/Q7/Q8 trên đường vendor-vs-record-broker ──
        os.environ["MIKE_CA_BROKER_SOURCE"] = "live"
        raw = lambda r: [dict(bsame, qty_multiplier=r)]          # noqa: E731
        for lbl, qm, flagged in (("số 1.20", 1.20, True), ("chuỗi '1.20'", "1.20", True),
                                 ("thiếu (None)", None, True), ("rác 'abc'", "abc", True),
                                 ("chuỗi '1.15' = hệ số vendor", "1.15", False), ("số 1.15", 1.15, False)):
            got = _call(f"Q5 qty_multiplier={lbl}", cac._broker_record_ratio_diff, raw(qm), "TPB", EX, 1.15)
            check(f"Q5 record broker qty_multiplier {lbl} ⇒ {'báo lệch' if flagged else 'không báo'}",
                  (got is not None) == flagged, got)
        check("Q6 _broker_record_ratio_diff chỉ xét CÙNG ex: record broker ex KHÁC, hệ số khác ⇒ None",
              cac._broker_record_ratio_diff([dict(bsame, ex_date="2026-10-09", qty_multiplier=1.5)],
                                            "TPB", EX, 1.15) is None)
        check("Q6b cùng ex, hệ số khác ⇒ có kết quả",
              cac._broker_record_ratio_diff([dict(bsame, qty_multiplier=1.5)], "TPB", EX, 1.15) is not None)
        # Q7: khoá hỏi có id record: REVOKE record cũ + record broker MỚI (id khác, vẫn lệch) ⇒ hỏi lại
        tmp, reg = _sandbox([bsame], vendor=[dict(vcal, exercise_ratio=0.16)])
        with quiet(io.StringIO()):
            cac.run_vendor(D)
            json.dump({"actions": [dict(bsame, _status="REVOKED — người thu hồi"),
                                   dict(bsame, id="TPB-BROKER-NEW-ID")]}, open(reg, "w"))
            cac.run_vendor(D)
            cac.run_vendor(D)
        check("Q7 khoá ratio-vs-broker CÓ id record: record broker mới sau REVOKE ⇒ hỏi lại (tổng 2), lượt 3 im",
              len(q_topics("vendor-ratio-vs-broker-TPB")) == 2, _Bus.calls)
        # Q8: record NGƯỜI ký (không lệch) ⇒ 'đã CONFIRMED rồi' + continue; không rơi xuống nhánh kiểm broker
        tmp, reg = _sandbox([dict(bsame, provenance=None, id="TPB-USER-SIGNED")], vendor=[vcal])
        h0 = _sha(reg)
        out = io.StringIO()
        with quiet(out):
            cac.run_vendor(D)
        check("Q8 đã CONFIRMED (người ký) ⇒ 'bỏ qua', registry y nguyên, 0 bus, KHÔNG kiểm broker tiếp",
              _sha(reg) == h0 and not _Bus.calls and "đã CONFIRMED rồi" in out.getvalue()
              and "kiểm broker" not in out.getvalue(), (_Bus.calls, out.getvalue()[-300:]))
        # Q11/Q20/Q21: đường lỗi hỏi người
        tmp, reg = _sandbox([brec], vendor=[vcal])

        def bad_bus(kind, topic, payload):
            if "vendor-vs-broker" in topic or "vendor-ask-failed" in topic:
                raise ValueError("payload lạ (giả)")
            return saved_bus(kind, topic, payload)
        cac._bus = bad_bus
        out = io.StringIO()
        try:
            with quiet(out):
                rc = _call("Q21 _bus ném ở cả vendor-ask-failed", cac.run_vendor, D)
        finally:
            cac._bus = saved_bus
        check("Q21 bus ném ở chính câu báo vendor-ask-failed ⇒ run_vendor KHÔNG ném, rc=1, in lỗi thật",
              rc == 1 and "không gửi được cả bus question báo lỗi" in out.getvalue(), (rc, out.getvalue()[-300:]))
        tmp, reg = _sandbox([brec], vendor=[vcal])
        cac._bus = lambda kind, topic, payload: (_ for _ in ()).throw(ValueError("x")) \
            if "vendor-vs-broker" in topic else saved_bus(kind, topic, payload)
        try:
            with quiet(io.StringIO()):
                cac.run_vendor(D)
        finally:
            cac._bus = saved_bus
        qf = [json.loads(c[4]) for c in _Bus.calls if "vendor-ask-failed" in c[3]]
        f0 = qf[0]["failed"][0] if qf and qf[0].get("failed") else {}
        check("Q11 mục lỗi hỏi người mang ĐỦ call + ticker + ex_date + error (người biết mã nào cần kiểm tay)",
              f0.get("call") == "_ask_vendor_vs_broker" and f0.get("ticker") == "TPB"
              and f0.get("ex_date") == EX and "ValueError" in f0.get("error", ""), qf)
        for exc in (RuntimeError("a"), KeyError("k"), OSError("o"), ValueError("v"), TypeError("t"),
                    BD.CorpActionLedgerError("l"), AttributeError("x")):
            failed = []

            def fn_(t, e, exc=exc):
                raise exc
            with quiet(io.StringIO()):
                r_ = _call(f"Q20 _ask_guarded {type(exc).__name__}", cac._ask_guarded, failed, fn_, "TPB", EX)
            check(f"Q20 _ask_guarded nuốt {type(exc).__name__} (gom vào failed, không ném)",
                  r_ is not _CRASHED and len(failed) == 1 and failed[0]["ticker"] == "TPB", failed)
    finally:
        subprocess.run = real_run
        cac.run_vendor, BD.scan_day = saved_vendor, saved_scan
        BD.ledger_append, cac._bus = saved_append, saved_bus
        cac.write_corp_actions = REAL_WRITE
        cac._px_cum_fn, cac._exchange_fn = REAL_PX_FN, REAL_EXCH_FN
        if saved_env is None:
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        else:
            os.environ["MIKE_CA_BROKER_SOURCE"] = saved_env


def test_px():
    """`_px_cum_fn` THẬT (đường live 19:25): hôm nay ⇒ DNSE G1 và CHỈ nguồn dnse_g1_today."""
    import types
    fake = types.ModuleType("verify_account_snapshot")
    state = {}

    def dcp(tickers, with_source=False):
        if state.get("raise"):
            raise ConnectionError("DNSE sập (giả)")
        return {tickers[0]: 14400.0}, {tickers[0]: state["src"]}
    fake.dnse_close_prices = dcp
    saved_mod, saved_today, saved_bq = sys.modules.get("verify_account_snapshot"), cac.today_ict, \
        BD.bq_unadjusted_close
    sys.modules["verify_account_snapshot"] = fake
    cac.today_ict = lambda: D
    BD.bq_unadjusted_close = lambda pairs: {p: 9999.0 for p in pairs}
    try:
        fn = REAL_PX_FN(D)
        state["src"] = "dnse_g1_today"
        check("P1 hôm nay + nguồn dnse_g1_today ⇒ dùng giá DNSE", fn("TPB", D) == 14400.0)
        state["src"] = "dnse_g1_prev_session"
        check("P2 hôm nay + nguồn KHÁC dnse_g1_today ⇒ None (§6 sai hệ)", fn("TPB", D) is None)
        state["raise"] = True
        check("P3 DNSE lỗi ⇒ None (không đoán)", fn("TPB", D) is None)
        check("P4 ngày quá khứ ⇒ BQ Price chưa điều chỉnh", fn("TPB", PREV) == 9999.0)
    finally:
        if saved_mod is None:
            sys.modules.pop("verify_account_snapshot", None)
        else:
            sys.modules["verify_account_snapshot"] = saved_mod
        cac.today_ict, BD.bq_unadjusted_close = saved_today, saved_bq


# ─────────────────────────────────────────────────────────────── C. exdate_frame fallback ──

def test_C():
    tmp = _mkdtemp("brokerca_xf_")
    reg = os.path.join(tmp, "corp_actions.json")
    rec = {"id": "TPB-B", "ticker": "TPB", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.15,
           "cash_leg_vnd_per_share": 500, "ex_date": EX, "broker_effective_ts": "2026-10-01T11:52:12",
           "_status": "CONFIRMED — test"}
    other = dict(rec, id="TPB-C", ex_date="2026-10-09")
    prop = dict(rec, id="VPB-P", ticker="VPB", _status="PROPOSED")
    json.dump({"actions": [rec, other, prop]}, open(reg, "w"))
    old_reg = CA.REGISTRY
    CA.REGISTRY = reg
    try:
        ev = XF.registry_event_next_session("TPB", D)
        check("C1 registry ev đúng ex phiên kế tiếp, mã vendor ISS, chân tiền 500",
              ev and ev["date"] == EX and ev["event_code"] == "ISS"
              and abs(ev["exercise_ratio"] - 0.15) < 1e-12 and ev["cash_leg_vnd_per_share"] == 500, ev)
        check("C2 record PROPOSED không bao giờ dùng", XF.registry_event_next_session("VPB", D) is None)
        check("C3 ex khác phiên kế tiếp ⇒ None", XF.registry_event_next_session("TPB", "2026-10-05") is None)
        check("C4 công tắc mặc định TẮT", XF.registry_fallback_enabled() is False)

        import types
        saved_tz = os.environ.get("TZ")
        import daily_nav_snapshot as real_dns                      # đặt TZ ở module level — khôi phục
        if saved_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = saved_tz
        _time.tzset()
        fake = types.ModuleType("daily_nav_snapshot")
        fake._corp_action_daily_snapshot = lambda asof: None
        fake._corp_action_gate_status = lambda snap, asof: (False, "lịch vendor thiếu (test)")
        fake.previous_raw_qty = lambda acct, tk, asof: (200.0, PREV)
        fake.net_fills_between = lambda *a, **k: {}
        fake.held_event_next_session = lambda snap, asof, tk: None
        fake.classify_qty_residual = real_dns.classify_qty_residual
        sys.modules["daily_nav_snapshot"] = fake
        try:
            cr, bl = XF.classify_positions("SpaceX", A1[0], D, {"TPB": {"total": 230}})
            check("C5 TẮT ⇒ hành vi cũ: TPB bị chặn", "TPB" in bl and not cr, (cr, bl))
            os.environ[XF.REGISTRY_FALLBACK_ENV] = "1"
            cr, bl = XF.classify_positions("SpaceX", A1[0], D, {"TPB": {"total": 230}})
            check("C6 BẬT ⇒ TPB credited, mang chân tiền 500 + nguồn registry",
                  "TPB" in cr and cr["TPB"].get("cash_leg_vnd_per_share") == 500
                  and cr["TPB"].get("event_source") == "corp_actions.json:TPB-B", (cr, bl))
            cr, bl = XF.classify_positions("SpaceX", A1[0], D, {"TPB": {"total": 240}})
            check("C7 BẬT nhưng KL không khớp hệ số ⇒ vẫn chặn (không nới cổng)", "TPB" in bl, (cr, bl))
            px, why = XF.verify_post_event_price(14400, 12100, 1.15, 500)
            check("C8 giá cùng hệ với chân tiền qua", px == 12100, why)
            json.dump({"actions": [dict(rec, provenance="broker")]}, open(reg, "w"))
            cr, bl = XF.classify_positions("SpaceX", A1[0], D, {"TPB": {"total": 230}})
            check("C9 record provenance=broker KHÔNG làm nguồn thứ hai cho cổng (M6) ⇒ vẫn chặn",
                  "TPB" in bl and not cr, (cr, bl))
            open(reg, "w").write("{hỏng")
            res = _call("C10 registry hỏng khi fallback BẬT ⇒ chặn đúng mã, nói lỗi thật",
                        XF.classify_positions, "SpaceX", A1[0], D, {"TPB": {"total": 230}})
            cr, bl = res if res is not _CRASHED else ({}, {})
            check("C10 registry hỏng khi fallback BẬT ⇒ chặn đúng mã, nói lỗi thật",
                  "TPB" in bl and "corp_actions.json" in bl["TPB"], (cr, bl))
        finally:
            os.environ.pop(XF.REGISTRY_FALLBACK_ENV, None)
            sys.modules["daily_nav_snapshot"] = real_dns
    finally:
        CA.REGISTRY = old_reg


# ─────────────────────────────────────────────────────────────── D. replay dữ liệu thật ──

EXPECTED = {("VHM", "2026-08-05"): "2026-08-06", ("BID", "2026-08-14"): "2026-08-17",
            ("VIX", "2026-08-19"): "2026-08-20", ("MSB", "2026-08-27"): "2026-08-28",
            ("VIB", "2026-09-09"): "2026-09-10", ("VPB", "2026-09-23"): "2026-09-24",
            ("TPB", "2026-10-01"): "2026-10-02"}


def test_D(start="2026-06-01", end="2026-10-03"):
    days, res = BD.replay(start, end)
    print(f"  replay {len(days)} phiên, {len(res)} ứng viên")
    got = {(r["ticker"], r["credit_day"]): r for r in res}
    check("D1 đúng tập 7 sự kiện thật, 0 ứng viên giả", set(got) == set(EXPECTED), sorted(got))
    reg = {a["ticker"] + a["ex_date"]: a for a in CA.load_all()}
    for (tk, day), ex in EXPECTED.items():
        r = got.get((tk, day))
        if not r:
            continue
        check(f"D2 {tk} CONFIRMABLE ex {ex}", r["verdict"] == BD.CONFIRMABLE and r["ex_date"] == ex,
              (r["verdict"], r["ex_date"], r["why"]))
        a = reg.get(tk + ex)
        if a and r.get("qty_multiplier"):
            check(f"D3 {tk} hệ số {r['qty_multiplier']} sát registry {a['qty_multiplier']} (≤0,1%)",
                  abs(r["qty_multiplier"] - a["qty_multiplier"]) <= 1e-3 * a["qty_multiplier"])
    t = got.get(("TPB", "2026-10-01"))
    check("D4 TPB chân tiền 500", t and t.get("cash_leg") == 500.0, t and t.get("cash_leg"))


# ─────────────────────────────────────────────────────────────── E. mutation ──

# Đột biến TƯƠNG ĐƯƠNG đã loại có chủ đích (không giết được vì không đổi hành vi):
#   `segs[-1][2].add(ts[:19])` → `add(ts)`: ts dnse_raw ghi bằng isoformat(timespec="seconds") nên
#   hai dạng trùng nhau; tập `set` đã gộp bản ghi cùng giây (A9b kiểm hành vi đó).
#   `m <= 1.0`, `px_ok is None`: khoảng KL ∩ giá đã ép m > 1 và giá khớp cùng dung sai.
#   `lid not in moved and moved` → bỏ `and moved`; null-test chỉ `[c]` (c=0 ⇒ trùng [0.0]).
# Đột biến SỐNG được CHẤP NHẬN (arch-review v2 liệt kê, ghi rõ để vòng sau không tưởng đã phủ):
#   `price_adjusting is True` (vendor ghi bool thật — chỉ khác với giá trị truthy lạ);
#   `_credit_like` bỏ điều kiện trade (chỉ ảnh hưởng lùi qua đoạn credit-dở; ca dở thật BID đã phủ);
#   `_near_duplicate` bỏ qua ex hỏng (validate() trước khi ghi đã chặn registry có ex hỏng).
MUTANTS = [
    ('bin/corp_action_broker_detect.py', '    if s1["cost"] - s0["cost"] > cost_tol(s0, s1):', '    if False:', 'bỏ lọc giá vốn tăng'),
    ('bin/corp_action_broker_detect.py', 'if s1["closed"] != s0["closed"]:', 'if False:', 'bỏ check bán'),
    ('bin/corp_action_broker_detect.py', 'if s1["trade"] > q0:', 'if False:', 'bỏ check trade'),
    ('bin/corp_action_broker_detect.py', '    if not (post_first.startswith(day) and post_first[11:19] >= CREDIT_WINDOW_START.isoformat()):', '    if not post_first.startswith(day):', 'bỏ mốc 15:00 theo ts'),
    ('bin/corp_action_broker_detect.py', '    if ts0_last[:10] < prev_trading_day(day):', '    if False:', 'bỏ check khoảng trống quan sát'),
    ('bin/corp_action_broker_detect.py', 'if n_post < MIN_POST_SNAPSHOTS:', 'if False:', 'bỏ đòi ≥2 bản ghi'),
    ('bin/corp_action_broker_detect.py', 'if abs((s1["accum"] - s0["accum"]) - (q1 - q0)) > 1e-9:', 'if False:', 'bỏ check accum'),
    ('bin/corp_action_broker_detect.py', 'if late:', 'if False:', 'bỏ check lệnh khớp muộn'),
    ('bin/corp_action_broker_detect.py', '    if abs(cash - c) > CASH_TOL_VND:', '    if False:', 'bỏ check chân tiền tròn'),
    ('bin/corp_action_broker_detect.py', '    if set(s0["lots"]) != set(s1["lots"]):', '    if False:', 'bỏ check id lô'),
    ('bin/corp_action_broker_detect.py', '            if lq1 < lq0 or abs(lcash - cash) > 1.0:', '            if False:', 'bỏ check từng lô'),
    ('bin/corp_action_broker_detect.py', '                if lid not in moved and moved:', '                if True:', "lô lệch luôn là 'dở'"),
    ('bin/corp_action_broker_detect.py', '    if q1 <= q0 or q0 <= 0:', '    if q0 <= 0:', 'cho phép KL giảm'),
    ('bin/corp_action_broker_detect.py', '    if not series[-1][0].startswith(day):', '    if False:', "bỏ 'không có bản ghi hôm nay'"),
    ('bin/corp_action_broker_detect.py', '    if lo2 >= hi2:', '    if False:', 'bỏ giao KL∩giá'),
    ('bin/corp_action_broker_detect.py', '    for c0 in sorted({c, 0.0}):', '    for c0 in []:', 'bỏ giả thuyết không-sự-kiện (B1)'),
    ('bin/corp_action_broker_detect.py', '    if holders_not_credited:', '    if False:', 'bỏ check tài khoản chưa credit'),
    ('bin/corp_action_broker_detect.py', '    if max(cash) - min(cash) > 1.0:', '    if False:', 'bỏ check chân tiền chéo'),
    ('bin/corp_action_broker_detect.py', '    if len(mkts) != 1:', '    if False:', 'bỏ check marketPrice chéo tài khoản'),
    ('bin/corp_action_broker_detect.py', '        if abs(v - c) > 1.0:', '        if False:', 'bỏ đối chiếu DIV vendor'),
    ('bin/corp_action_broker_detect.py', '            and str(e.get("date") or "")[:10] == ex_date]', '            ]', 'DIV vendor bỏ khớp ngày'),
    ('bin/corp_action_broker_detect.py', '        v = sum(_f(e.get("value_per_share")) for e in divs)', '        v = _f(divs[0].get("value_per_share"))', 'DIV chỉ lấy dòng đầu'),
    ('bin/corp_action_broker_detect.py', '    if m > QTY_MULT_MAX:', '    if False:', 'bỏ biên hệ số'),
    ('bin/corp_action_broker_detect.py', '        return dict(out, verdict=DEFER_VENDOR,', '        return dict(out, verdict=CONFIRMABLE,', 'không nhường vendor'),
    ('bin/corp_action_broker_detect.py', '    if share_ev:', '    if share_ev and share_ev[0] is vendor_events[0]:', 'nhường vendor theo thứ tự (M1)'),
    ('bin/corp_action_broker_detect.py', '    if vendor_events == VENDOR_UNREADABLE:', '    if False:', 'lịch vendor hỏng = không sự kiện'),
    ('bin/corp_action_broker_detect.py', '    if cal:                                                        # lịch không tin được ⇒ người', '    if False:', 'bỏ guard lịch'),
    ('bin/corp_action_broker_detect.py', '        if lo <= ex <= hi and not any(lo <= h <= hi for h in vn_market._VARIABLE_HOLIDAYS):', '        if False:', 'bỏ guard mùa nghỉ'),
    ('bin/corp_action_broker_detect.py', '    if (ex - d0).days > MAX_CREDIT_TO_EX_DAYS:', '    if False:', 'bỏ guard khoảng D→ex'),
    ('bin/corp_action_broker_detect.py', '    if not px_cum or px_cum <= 0:', '    if not px_cum:', 'giá cum 0 được dùng'),
    ('bin/corp_action_broker_detect.py', '    if m1 - tol <= 0 or px_cum - c <= 0:', '    if m1 - tol <= 0:', 'bỏ check giá vô nghĩa'),
    ('bin/corp_action_broker_detect.py', "(frac + '000000')[:6]", 'frac[:6]', 'parse 5 chữ số'),
    ('bin/corp_action_broker_detect.py', 'and _credit_like(segs[j - 1][1], segs[j][1]) and _credit_like(segs[j][1], s1)):', 'and True):', 'lùi qua bước không giống credit'),
    ('bin/corp_action_broker_detect.py', '    while (j >= 1 and segs[j][0] >= close_mark', '    while (j >= 1', 'lùi qua đoạn trước 15:00'),
    ('bin/corp_action_broker_detect.py', '    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 1) / q0', '    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 5) / q0', 'nới khoảng hệ số KL'),
    ('bin/corp_action_broker_detect.py', '            if d.get("kind") != "positions" or str(d.get("account_no")) != str(account_no):', '            if d.get("kind") != "positions":', '§12 read_series bỏ lọc bản ghi'),
    ('bin/corp_action_broker_detect.py', '                if str(p.get("accountNo")) != str(account_no):\n                    continue', '                pass', '§12 read_series bỏ lọc dòng'),
    ('bin/corp_action_broker_detect.py', '            if d.get("kind") != "orders" or str(d.get("account_no")) != str(account_no):', '            if d.get("kind") != "orders":', '§12 fills bỏ lọc bản ghi'),
    ('bin/corp_action_broker_detect.py', '                if (o.get("symbol") == ticker and str(o.get("accountNo")) == str(account_no)', '                if (o.get("symbol") == ticker', '§12 fills bỏ lọc dòng'),
    ('bin/corp_action_broker_detect.py', '        if d < day and (best is None or d > best[0]):', '        if d <= day and (best is None or d > best[0]):', 'previous_file lấy cùng ngày'),
    ('bin/corp_action_broker_detect.py', '        holders = [lbl for lbl in held_before.get(tk, []) if lbl not in per]', '        holders = []', 'scan_day bỏ holders'),
    ('bin/corp_action_broker_detect.py', '            if aggregate(rows)["qty"] > 0:\n                held_before', '            if False:\n                held_before', 'bỏ tài khoản vắng mặt hôm nay'),
    ('bin/corp_action_broker_detect.py', '            fills = same_day_fills(path, acct, tk, day)', '            fills = []', 'scan_day bỏ sổ lệnh'),
    ('bin/corp_action_auto_confirm.py', '        if (tk, ex) in in_registry:', '        if False:', 'không kiểm registry sẵn có'),
    ('bin/corp_action_auto_confirm.py', '        if tuple(entry["key"]) in intents:', '        if False:', 'bỏ idempotent sổ'),
    ('bin/corp_action_auto_confirm.py', '        dup = _near_duplicate(actions_raw, tk, date_str, ex)', '        dup = None', 'bỏ guard trùng gần (M4)'),
    ('bin/corp_action_auto_confirm.py', '    new_recs = [e["record"] for e in new if mode == "live" and e["verdict"] == BD.CONFIRMABLE]', '    new_recs = [e["record"] for e in new if e["verdict"] == BD.CONFIRMABLE]', 'shadow vẫn ghi registry'),
    ('bin/corp_action_auto_confirm.py', '        return "shadow"\n    return raw', '        return "live"\n    return raw', 'mode lạ ⇒ live'),
    ('bin/corp_action_auto_confirm.py', '            new_recs = []\n            rc = 1', '            rc = 1', 'nuốt lỗi validate (vẫn ghi registry)'),
    ('bin/corp_action_auto_confirm.py', '            if _finish_live(e, registry_ids) == 0:', '            if _finish_live(e, registry_ids) is not None:', 'done dù bus lỗi (M2)'),
    ('bin/corp_action_auto_confirm.py', '    pending = [e for k, e in intents.items() if k not in done and e.get("mode") == mode]', '    pending = []', 'không gửi bù (M2)'),
    ('bin/corp_action_auto_confirm.py', '        if rid in registry_ids:', '        if True:', 'báo confirm khi registry không có'),
    ('bin/corp_action_auto_confirm.py', '                rc = 1                                       # §6 verify artifact: không thấy ⇒ lỗi', '                pass', 'bỏ rc=1 khi đọc lại không thấy'),
    ('bin/corp_action_auto_confirm.py', '    urgency = "normal" if v == BD.INSUFFICIENT else "high"', '    return 0', 'live im lặng với INSUFFICIENT/DEFER/AMBIGUOUS (M3)'),
    ('bin/corp_action_auto_confirm.py', '        raise SandboxMismatch(f"LEDGER_FILE={LEDGER_FILE} là sổ PRODUCTION', '        print(f"LEDGER_FILE={LEDGER_FILE} là sổ PRODUCTION', 'bỏ guard sandbox lệch (B2)'),
    ('bin/corp_action_auto_confirm.py', '            if time.monotonic() - t0 > LOCK_WAIT_S:', '            if True:\n                return open(os.devnull)\n            if False:', 'bỏ khoá'),
    ('bin/corp_action_auto_confirm.py', 'MƠ HỒ")\n        return lambda tk: BD.VENDOR_UNREADABLE', 'MƠ HỒ")\n        return lambda tk: []', 'lịch vendor hỏng ⇒ coi rỗng'),
    ('bin/corp_action_auto_confirm.py', '                if src.get(ticker) != "dnse_g1_today":', '                if False:', 'bỏ cổng nguồn giá DNSE (§6)'),
    ('bin/corp_action_auto_confirm.py', '            _ask_day_once(f"{name}crash", date_str, f"corp-action-{name}-crash-{date_str}",', '            (lambda *a: 0)(f"{name}crash", date_str, f"corp-action-{name}-crash-{date_str}",', 'crash chỉ nằm trong log'),
    ('bin/exdate_frame.py', 'return os.environ.get(REGISTRY_FALLBACK_ENV, "0").strip() == "1"', 'return True', 'fallback mặc định BẬT'),
    ('bin/exdate_frame.py', '        if a["ex_date"] == nxt and a["id"] not in broker_ids:', '        if a["ex_date"] == nxt:', 'broker tự làm nguồn 2 (M6)'),
    ('bin/exdate_frame.py', '        if a["ex_date"] == nxt and a["id"] not in broker_ids:', '        if a["id"] not in broker_ids:', 'bỏ khớp ex phiên kế tiếp'),
    ('bin/exdate_frame.py', '                detail["cash_leg_vnd_per_share"] = ev.get("cash_leg_vnd_per_share", 0.0)', '                pass', 'rơi chân tiền'),
    ('bin/exdate_frame.py', '            except Exception as e:   # registry hỏng', '            except ZeroDivisionError as e:   # registry hỏng', 'fallback không bắt lỗi registry'),
    ('bin/corp_action_broker_detect.py', '    if len(s1["mkts"]) != 1:', '    if False:', 'bỏ chốt marketPrice lẫn lô (v2 N1)'),
    ('bin/corp_action_broker_detect.py', '    if exchange not in PRICE_GATE_EXCHANGES:', '    if False:', 'bỏ guard sàn UPCOM (v2 N7)'),
    ('bin/corp_action_broker_detect.py', 'PRICE_GATE_EXCHANGES = ("HOSE", "HNX")', 'PRICE_GATE_EXCHANGES = ("HOSE", "HNX", "UPCOM", None)', 'sàn lạ/None được tự xác nhận'),
    ('bin/corp_action_broker_detect.py', 'CREDIT_WINDOW_START = dt.time(15, 0)', 'CREDIT_WINDOW_START = dt.time(14, 0)', 'cửa sổ 15:00 → 14:00'),
    ('bin/corp_action_broker_detect.py', '    while d.weekday() >= 5 or is_holiday(d):\n        d -= dt.timedelta(days=1)', '    while d.weekday() >= 5:\n        d -= dt.timedelta(days=1)', 'prev_trading_day bỏ ngày lễ'),
    ('bin/corp_action_broker_detect.py', '            if lq1 < lq0 or abs(lcash - cash) > 1.0:', '            if abs(lcash - cash) > 1.0:', 'bỏ lq1<lq0 từng lô'),
    ('bin/corp_action_broker_detect.py', '    for c0 in sorted({c, 0.0}):', '    for c0 in [0.0]:', 'null-test chỉ [0.0] (v2 #6)'),
    ('bin/corp_action_broker_detect.py', '        if abs(v - c) > 1.0:', '        if abs(v - c) > 100.0:', 'dung sai DIV 1 → 100'),
    ('bin/corp_action_broker_detect.py', '    late = [f for f in fills if f[0] is None or f[0].isoformat()[:19] >= ts0_last[:19]]', '    late = [f for f in fills if f[0] is not None and f[0].isoformat()[:19] >= ts0_last[:19]]', 'fill không giờ bị bỏ qua'),
    ('bin/corp_action_broker_detect.py', 'f[0].isoformat()[:19] >= ts0_last[:19]]', 'f[0].isoformat()[:19] > ts0_last[:19]]', 'fill >= → >'),
    ('bin/corp_action_broker_detect.py', '                raise CorpActionLedgerError(f"{path}:{n} không phải JSON ({e})") from e', '                continue', 'dòng sổ hỏng bị nuốt'),
    ('bin/corp_action_auto_confirm.py', '            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)', '            fcntl.flock(fh, fcntl.LOCK_SH | fcntl.LOCK_NB)', 'khoá EX → SH'),
    ('bin/corp_action_auto_confirm.py', '    if _in_prod(LEDGER_FILE) and not (_in_prod(EXEC_DIR) and _in_prod(CORP_ACTIONS_FILE)):', '    if _in_prod(LEDGER_FILE) and not (_in_prod(EXEC_DIR) or _in_prod(CORP_ACTIONS_FILE)):', 'guard sandbox chỉ khi CẢ 2 trục lệch'),
    ('bin/corp_action_auto_confirm.py', '        if rex.isoformat() != ex and abs((rex - d0).days) <= NEAR_DUP_DAYS:', '        if rex.isoformat() != ex and 0 <= (rex - d0).days <= NEAR_DUP_DAYS:', 'trùng gần chỉ xét tương lai'),
    ('bin/corp_action_auto_confirm.py', '    urgency = "normal" if v == BD.INSUFFICIENT else "high"', '    urgency = "normal"', 'urgency luôn normal'),
    ('bin/corp_action_auto_confirm.py', '    except (OSError, json.JSONDecodeError, AttributeError) as e:\n        print(f"  ❌ lịch vendor {path} đọc hỏng', '    except (OSError, json.JSONDecodeError) as e:\n        print(f"  ❌ lịch vendor {path} đọc hỏng', 'lịch vendor gốc list ⇒ crash'),
    ('bin/corp_action_auto_confirm.py', '    except (OSError, json.JSONDecodeError, AttributeError) as e:\n                print(f"  ❌ lịch vendor {os.path.basename(failed)}', '    except (OSError, json.JSONDecodeError) as e:\n                print(f"  ❌ lịch vendor {os.path.basename(failed)}', 'r5 _FAILED gốc list ⇒ crash'),
    ('bin/corp_action_auto_confirm.py', '            finished = todo', '            finished = new', 'shadow không đóng pending (gửi lặp)'),
    ('bin/corp_action_auto_confirm.py', '    pending = [e for k, e in intents.items() if k not in done and e.get("mode") == mode]', '    pending = [e for k, e in intents.items() if k not in done]', 'pending lấy mọi mode'),
    ('bin/corp_action_auto_confirm.py', '                    _close_stale_questions(e, intents)', '                    pass', 'không đóng question cũ (§26)'),
    ('bin/corp_action_auto_confirm.py', '            new = [x for x in new if x["verdict"] != BD.CONFIRMABLE]\n            new_recs = []\n            rc = 1', '            return 1', 'validate-reject nuốt mã khác (v2 N2)'),
    ('bin/corp_action_auto_confirm.py', '        _bdup = _broker_record_near(actions_raw, ticker, ex_date)', '        _bdup = None', 'vendor ghi đè record broker ex khác (v2 N9)'),
    ('bin/corp_action_auto_confirm.py', '    lk = None if dry_run else _lock(LEDGER_FILE)', '    lk = None', 'run() không khoá nhánh vendor (v2 N3)'),
    # ── vòng sửa sau arch-review v3 (job Taylor_20261003_064854): mỗi dòng ↔ assertion V* ──
    ('bin/corp_action_auto_confirm.py', '        if not str(r.get("_status", "")).upper().startswith("CONFIRMED"):\n            continue      # REVOKED', '        if False:\n            continue      # REVOKED', 'N9 record broker REVOKED vẫn khoá vendor'),
    ('bin/corp_action_auto_confirm.py', '        if rex != d0 and abs((rex - d0).days) <= NEAR_DUP_DAYS:', '        if rex != d0 and 0 <= (rex - d0).days <= NEAR_DUP_DAYS:', 'N9 chỉ xét ex SAU'),
    ('bin/corp_action_auto_confirm.py', '    if tuple(key) in done:', '    if False:', 'N9 hỏi lặp mỗi lượt'),
    ('bin/corp_action_auto_confirm.py', '    if rc == 0:\n        now_ict', '    if True:\n        now_ict', 'N9 bus lỗi vẫn đánh dấu đã hỏi'),
    ('bin/corp_action_auto_confirm.py', '            if not dry_run:\n                _ask_guarded(ask_failed, _ask_vendor_vs_broker', '            if True:\n                _ask_guarded(ask_failed, _ask_vendor_vs_broker', 'N9 gửi bus khi --dry-run'),
    ('bin/corp_action_auto_confirm.py', "cache[tk] = q.exchange if getattr(q, \"exchange_known\", False) else None", 'cache[tk] = q.exchange', '_exchange_fn bỏ exchange_known'),
    ('bin/corp_action_auto_confirm.py', '                cache[tk] = None\n        return cache[tk]', '                cache[tk] = "HOSE"\n        return cache[tk]', '_exchange_fn lỗi ⇒ HOSE'),
    ('bin/corp_action_auto_confirm.py', '    if not dry_run and lk is None:', '    if False:', 'run() bỏ chặn khi không lấy được khoá'),
    ('bin/corp_action_auto_confirm.py', '    _LOCK_HELD = lk is not None   #', '    _LOCK_HELD = False   #', 'r5 run() không đặt cờ khoá cho 2 nhánh (tự khoá, regress WIP)'),
    ('bin/corp_action_auto_confirm.py', '    if _LOCK_HELD:\n        return _run_broker_locked', '    if False:\n        return _run_broker_locked', 'run_broker xin khoá lần 2'),
    ('bin/corp_action_auto_confirm.py', '        _ask_lock_unavailable(date_str, mode)\n        return 1', '        return 1', 'không có khoá ⇒ im (không hỏi)'),
    ('bin/corp_action_auto_confirm.py', '                and old.get("verdict") in (BD.INSUFFICIENT, BD.AMBIGUOUS, BD.DEFER_VENDOR)):', '                and old.get("verdict") in (BD.INSUFFICIENT,)):', '_close_stale chỉ INSUFFICIENT'),
    ('bin/corp_action_auto_confirm.py', '        if (old.get("mode") == "live" and old.get("ticker") == e["ticker"]', '        if (old.get("ticker") == e["ticker"]', '_close_stale bỏ lọc mode'),
    ('bin/corp_action_auto_confirm.py', '        if (old.get("mode") == "live" and old.get("ticker") == e["ticker"]', '        if (old.get("mode") == "live"', '_close_stale bỏ lọc mã'),
    ('bin/corp_action_auto_confirm.py', '                and old.get("credit_day") == e["credit_day"]', '                and True', '_close_stale bỏ lọc phiên'),
    ('bin/corp_action_auto_confirm.py', '                if e["verdict"] == BD.CONFIRMABLE and e["record"]["id"] in registry_ids:\n                    _close_stale_questions', '                if e["verdict"] == BD.CONFIRMABLE:\n                    _close_stale_questions', 'đóng question dù registry không có record'),
    ('bin/corp_action_auto_confirm.py', '                           capture_output=True, text=True, timeout=BUS_TIMEOUT_S)', '                           capture_output=True, text=True)', '_bus bỏ timeout'),
    ('bin/corp_action_auto_confirm.py', '        return 124', '        return 0', '_bus timeout coi như đã gửi'),
    ('bin/corp_action_auto_confirm.py', '        registry_ids = set()\n        rc = 1', '        registry_ids = set()', 'đọc lại registry hỏng ⇒ rc=0'),
    ('bin/corp_action_auto_confirm.py', '        e.setdefault("key", BD.ledger_key(e))', '        pass', 'bỏ setdefault key (sổ định dạng cũ)'),
    # ── vòng v4 (job Taylor_20261003_082621): mỗi dòng ↔ assertion R* trong test_v5 ──
    ('bin/corp_action_auto_confirm.py', '                s.connect()\n', '', '#1 _exchange_fn không connect()'),
    ('bin/corp_action_auto_confirm.py', '                s._raw_log = None\n', '', '#1 quote ghi dnse_raw production'),
    ('bin/corp_action_auto_confirm.py', '                src.append(None)\n        return src[0]', '                raise\n        return src[0]', '#1 connect lỗi ⇒ ném'),
    ('bin/corp_action_auto_confirm.py', '        if not src:\n', '        if True:\n', '#1 connect mỗi mã'),
    ('bin/corp_action_broker_detect_selfcheck.py', '"bin")\n    if os.path.realpath(here) == os.path.realpath(canon):', '"bin")\n    if False:', '#4 bỏ guard canonical'),
    ('bin/corp_action_broker_detect_selfcheck.py', '"bin")\n    if os.path.realpath(here) == os.path.realpath(canon):', '"bin")\n    if here == canon:', '#4 guard không realpath'),
    ('bin/corp_action_broker_detect_selfcheck.py', '    why = _mutation_refusal(here, canon)\n    if why:', '    why = None\n    if why:', '#4 run_mutations không gọi guard'),
    ('bin/corp_action_auto_confirm.py', '    except Exception as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', '    except ZeroDivisionError as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', '#6 lỗi N9 làm mất lô vendor'),
    ('bin/corp_action_auto_confirm.py', '        failed.append({"call"', '        0 and failed.append({"call"', '#6 lỗi N9 không báo'),
    ('bin/corp_action_auto_confirm.py', '            print(f"  ❌ không gửi được cả bus question báo lỗi: {type(e).__name__}: {e}")\n        rc = 1', '            print(f"  ❌ không gửi được cả bus question báo lỗi: {type(e).__name__}: {e}")', '#6 lỗi N9 rc=0'),
    ('bin/corp_action_auto_confirm.py', '    try:\n        return fn()\n    except SandboxMismatch:\n        raise\n', '    try:\n        return fn()\n', '#6 nuốt SandboxMismatch (_run_branch)'),
    ('bin/corp_action_auto_confirm.py', '    try:\n        fn(*args)\n    except SandboxMismatch:\n        raise\n', '    try:\n        fn(*args)\n', '#6 nuốt SandboxMismatch (_ask_guarded)'),
    ('bin/corp_action_auto_confirm.py', '        done = set()\n    if tuple(key) in done:', '        return\n    if tuple(key) in done:', '#7 X5 sổ hỏng ⇒ im'),
    ('bin/corp_action_auto_confirm.py', '    _ask_once(["vendor-vs-broker", ticker, ex_date, rid, "ASKED"],', '    _ask_once(["vendor-vs-broker", ticker, ex_date, "ASKED"],', '#9 khoá ASKED không có id record'),
    ('bin/corp_action_broker_detect.py', 'capture_output=True, text=True, env=env, timeout=BQ_TIMEOUT_S)', 'capture_output=True, text=True, env=env)', '#10 bq không timeout'),
    ('bin/corp_action_auto_confirm.py', '            _bratio = _broker_record_ratio_diff(actions_raw, ticker, ex_date, mult)', '            _bratio = None', '#12 tỉ lệ lệch im lặng'),
    ('bin/corp_action_auto_confirm.py', '        if bm is None or abs(bm - mult) > BROKER_VENDOR_MULT_TOL * mult:', '        if bm is None or abs(bm - mult) > 0.02 * mult:', '#12 dung sai 2%'),
    ('bin/corp_action_auto_confirm.py', '                or str(r.get("provenance", "")).lower() != "broker"\n                or not', '                or not', '#12 record người ký cũng hỏi'),
    ('bin/corp_action_auto_confirm.py', '                or not str(r.get("_status", "")).upper().startswith("CONFIRMED")):\n            continue\n        try:\n            bm', '                ):\n            continue\n        try:\n            bm', '#12 record REVOKED cũng hỏi'),
    ('bin/corp_action_auto_confirm.py', '                if not dry_run:\n                    _ask_guarded(ask_failed, _ask_ratio_vs_broker', '                if True:\n                    _ask_guarded(ask_failed, _ask_ratio_vs_broker', '#12 hỏi khi --dry-run'),
    # ── vòng r5 (job Taylor_20261003_091511): mỗi dòng ↔ assertion trong test_v6 ──
    ('bin/corp_action_auto_confirm.py', '            if gate == "feed_dead":', '            if True:', 'r5 M-A mọi _FAILED ⇒ feed_dead'),
    ('bin/corp_action_auto_confirm.py', '            if gate == "feed_dead":', '            if False:', 'r5 M-A feed_dead vẫn UNREADABLE'),
    ('bin/corp_action_auto_confirm.py', '                dead.feed_dead = True\n', '', 'r5 M-A bỏ cờ feed_dead'),
    ('bin/corp_action_auto_confirm.py', '                def dead(tk):\n                    return []', '                def dead(tk):\n                    return BD.VENDOR_UNREADABLE', 'r5 M-A feed_dead trả UNREADABLE'),
    ('bin/corp_action_auto_confirm.py', '        results = [dict(r, vendor_feed_dead=True, why=f"{FEED_DEAD_TAG}; {r[\'why\']}") for r in results]', '        pass', 'r5 M-A không gắn cờ vào kết quả'),
    ('bin/corp_action_auto_confirm.py', '                entry["record"]["evidence"].append(FEED_DEAD_TAG)', '                pass', 'r5 M-A record không mang cờ'),
    ('bin/corp_action_auto_confirm.py', '"vendor_feed_dead": bool(r.get("vendor_feed_dead")),', '"vendor_feed_dead": False,', 'r5 M-A sổ không lưu cờ'),
    ('bin/corp_action_auto_confirm.py', '            except (OSError, json.JSONDecodeError, AttributeError) as e:\n                print(f"  ❌ lịch vendor {os.path.basename(failed)}', '            except ZeroDivisionError as e:\n                print(f"  ❌ lịch vendor {os.path.basename(failed)}', 'r5 M-A _FAILED hỏng không bắt'),
    ('bin/corp_action_auto_confirm.py', '        return 1\n\n\ndef _run_both', '        return 0\n\n\ndef _run_both', 'r5 M-B nhánh nổ ⇒ rc=0'),
    ('bin/corp_action_auto_confirm.py', '                           "mode": mode, "urgency": "high"})\n        return 1\n\n\ndef _run_both', '                           "mode": mode, "urgency": "normal"})\n        return 1\n\n\ndef _run_both', 'r5 M-B crash question normal'),
    ('bin/corp_action_auto_confirm.py', '    except SandboxMismatch:\n        raise\n    except Exception as e:   # crash nhánh', '    except Exception as e:   # crash nhánh', 'r5 H3 _run_branch nuốt SandboxMismatch'),
    ('bin/corp_action_auto_confirm.py', '    rc_b = _run_branch("broker"', '    rc_b = 0 if rc else _run_branch("broker"', 'r5 M-C vendor lỗi ⇒ bỏ broker'),
    ('bin/corp_action_auto_confirm.py', '    return rc or rc_b', '    return rc', 'r5 M-C bỏ rc broker'),
    ('bin/corp_action_auto_confirm.py', '            _ask_day_once(f"{name}crash", date_str,', '            _ask_day_once("vendorcrash", date_str,', 'r5 M-B tag crash không theo nhánh'),
    ('bin/corp_action_auto_confirm.py', '        if not dry_run:\n            _ask_day_once(f"{name}crash"', '        if True:\n            _ask_day_once(f"{name}crash"', 'r5 H4 crash hỏi cả khi --dry-run'),
    ('bin/corp_action_auto_confirm.py', '        _ask_lock_unavailable(date_str, mode)\n        return 1', '        return 1', 'r5 M-D khoá ⇒ im (không hỏi)'),
    ('bin/corp_action_auto_confirm.py', '            if st.st_size > 0 or time.time() - st.st_mtime <= DAYMARK_STALE_S:', '            if True:', 'r5 M-D claim mồ côi không bao giờ chiếm lại'),
    ('bin/corp_action_auto_confirm.py', '            if st.st_size > 0 or time.time() - st.st_mtime <= DAYMARK_STALE_S:', '            if st.st_size > 0 or False:', 'r5 M-D claim đang gửi bị chiếm ngay'),
    ('bin/corp_action_auto_confirm.py', '            if st.st_size > 0 or time.time() - st.st_mtime <= DAYMARK_STALE_S:', '            if time.time() - st.st_mtime <= DAYMARK_STALE_S:', 'r5 M-D marker sent cũ bị hỏi lại'),
    ('bin/corp_action_auto_confirm.py', '            os.write(fd, b"sent\\n")', '            pass', 'r5 M-D không ghi sent'),
    ('bin/corp_action_auto_confirm.py', '    if rc != 0:\n        os.remove(marker)', '    if False:\n        os.remove(marker)', 'r5 M-D bus lỗi vẫn giữ marker (Q4 rc)'),
    ('bin/corp_action_auto_confirm.py', '        print(f"  ❌ không gửi được bus question {topic}: {type(e).__name__}: {e}")\n        rc = 1', '        print(f"  ❌ không gửi được bus question {topic}: {type(e).__name__}: {e}")\n        rc = 0', 'r5 Q4 bus khoá ném vẫn giữ marker'),
    ('bin/corp_action_auto_confirm.py', '    marker = f"{LEDGER_FILE}.{tag}-{date_str}"', '    marker = f"{LEDGER_FILE}.{tag}"', 'r5 Q3 marker không theo ngày'),
    ('bin/corp_action_auto_confirm.py', 'DAYMARK_KEEP_DAYS * 86400:', 'DAYMARK_KEEP_DAYS * 86400 * 1000:', 'r5 M-D prune không bao giờ xoá'),
    ('bin/corp_action_auto_confirm.py', '        for p in glob.glob(f"{LEDGER_FILE}.{tag}-*"):', '        for p in glob.glob(f"{LEDGER_FILE}*"):', 'r5 M-D prune xoá cả sổ/khoá'),
    ('bin/corp_action_auto_confirm.py', '            bm = float(r.get("qty_multiplier"))', '            bm = mult', 'r5 Q5 qty_multiplier không parse (coi = vendor)'),
    ('bin/corp_action_auto_confirm.py', '            bm = float(r.get("qty_multiplier"))', '            bm = float(r.get("qty_multiplier") or mult)', 'r5 Q5 thiếu qty_multiplier coi = vendor'),
    ('bin/corp_action_auto_confirm.py', '        if (str(r.get("ticker", "")).upper() != tk or str(r.get("ex_date", ""))[:10] != ex\n', '        if (str(r.get("ticker", "")).upper() != tk\n', 'r5 Q6 ratio-diff bỏ khớp ex'),
    ('bin/corp_action_auto_confirm.py', '    _ask_once(["vendor-ratio-vs-broker", ticker, ex_date, rid, "ASKED"],', '    _ask_once(["vendor-ratio-vs-broker", ticker, ex_date, "ASKED"],', 'r5 Q7 khoá ratio không rid'),
    ('bin/corp_action_auto_confirm.py', 'đã CONFIRMED rồi — bỏ qua.")\n            continue\n', 'đã CONFIRMED rồi — bỏ qua.")\n', 'r5 Q8 bỏ continue nhánh confirmed_set'),
    ('bin/corp_action_auto_confirm.py', '        failed.append({"call": fn.__name__, "ticker": args[0], "ex_date": args[1],\n                       "error"', '        failed.append({"call": fn.__name__,\n                       "error"', 'r5 Q11 ask_failed mất ticker/ex'),
    ('bin/corp_action_auto_confirm.py', '    except Exception as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', '    except (OSError, ValueError) as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', 'r5 Q20 _ask_guarded thu hẹp OSError/ValueError'),
    ('bin/corp_action_auto_confirm.py', '    except Exception as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', '    except RuntimeError as e:\n        import traceback\n        print(traceback.format_exc())\n        failed.append(', 'r5 Q20 _ask_guarded chỉ RuntimeError'),
    ('bin/corp_action_auto_confirm.py', '        except Exception as e:  # §29: kênh báo lỗi cũng hỏng', '        except ZeroDivisionError as e:  # §29: kênh báo lỗi cũng hỏng', 'r5 Q21 bus vendor-ask-failed ném thoát run_vendor'),
]


def _mutation_refusal(here=HERE, canon=None):
    """--mutations SỬA TẠI CHỖ file nguồn dưới dirname(here): chạy từ cây CANONICAL ⇒ mã production
    (cron 19:25 corp_action_auto_confirm + exdate_frame) mang đột biến ~14s mỗi đột biến
    (arch-review v4 #4). Chỉ cho chạy trong worktree. Trả lý do từ chối, hoặc None."""
    canon = canon or os.path.join(cac.MIKE_ROOT, "bin")
    if os.path.realpath(here) == os.path.realpath(canon):
        return (f"TỪ CHỐI --mutations: {here} là cây CANONICAL {canon} — đột biến sẽ sửa mã "
                f"production tại chỗ. Chạy từ worktree (git worktree add …).")
    return None


def run_mutations(here=HERE, canon=None):
    why = _mutation_refusal(here, canon)
    if why:
        print(f"❌ {why}")
        return False
    root = os.path.dirname(here)
    killed, survived, by_name, by_crash = [], [], [], []
    # PYTHONDONTWRITEBYTECODE: đột biến cùng KÍCH THƯỚC file, ghi trong cùng giây ⇒ `.pyc` cũ
    # (khoá mtime+size) bị coi là còn hợp lệ ⇒ tiến trình sau nạp bản ĐỘT BIẾN trước đó dù file
    # đã khôi phục — đã cắn thật khi viết file này ("(q1 + 5)" sống sót trong __pycache__).
    env = dict(os.environ, BROKERCA_SELFCHECK_CHILD="1", PYTHONDONTWRITEBYTECODE="1")
    pyc = os.path.join(here, "__pycache__")

    def _purge():
        if os.path.isdir(pyc):
            for f in os.listdir(pyc):
                if f.split(".")[0] in {os.path.basename(m[0])[:-3] for m in MUTANTS}:
                    os.remove(os.path.join(pyc, f))
    _purge()
    for rel, old, new, label in MUTANTS:
        p = os.path.join(root, rel)
        src = open(p, encoding="utf-8").read()
        h = hashlib.sha256(src.encode()).hexdigest()
        if src.count(old) != 1:
            survived.append(f"{label} (MẪU KHÔNG TÌM THẤY ĐÚNG 1 LẦN: {src.count(old)})")
            continue
        try:
            open(p, "w", encoding="utf-8").write(src.replace(old, new))
            r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env,
                               capture_output=True, text=True, timeout=300)
            if r.returncode == 0:
                survived.append(label)
            else:
                # Giết bởi assertion CÓ TÊN (dòng "❌ FAIL: <tên>") hay chỉ bởi crash — crash không
                # chứng minh assertion nào canh điều kiện đó (arch-review v4: đòi assertion có tên).
                names = [x.split("FAIL: ", 1)[1].split(" — ")[0] for x in r.stdout.splitlines()
                         if x.startswith("❌ FAIL: ")]
                killed.append(label)
                (by_name if names else by_crash).append(f"{label} ⇐ {names[0] if names else (r.stderr or r.stdout).strip().splitlines()[-1:]}")
        finally:
            open(p, "w", encoding="utf-8").write(src)
            assert hashlib.sha256(open(p, encoding="utf-8").read().encode()).hexdigest() == h, \
                f"KHÔNG khôi phục được {rel}"
            _purge()
    print(f"\nMUTATION: {len(killed)}/{len(MUTANTS)} bị giết ({len(by_name)} bởi assertion có tên, "
          f"{len(by_crash)} chỉ bởi crash)")
    if "-v" in sys.argv:
        for k_ in by_name:
            print(f"  ✓ {k_}")
    for k_ in by_crash:
        print(f"  ⚠ CHỈ CRASH: {k_}")
    for s_ in survived:
        print(f"  ⚠ SỐNG: {s_}")
    return not survived


def main():
    if "--mutations" in sys.argv and not os.environ.get("BROKERCA_SELFCHECK_CHILD"):
        why = _mutation_refusal()
        if why:
            print(f"❌ {why}")
            return 2
    test_A()
    test_files()
    test_B()
    test_v4()
    test_v5()
    test_v6()
    test_px()
    test_C()
    if "--replay" in sys.argv:
        test_D()
    print(f"\n{len(PASS)} PASS / {len(FAIL)} FAIL  (TZ={os.environ.get('TZ')!r}, "
          f"py={sys.version.split()[0]})")
    ok = not FAIL
    if "--mutations" in sys.argv and not os.environ.get("BROKERCA_SELFCHECK_CHILD"):
        ok = run_mutations() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
