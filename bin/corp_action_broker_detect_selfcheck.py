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
     trình con, mong FAIL; khôi phục + kiểm sha256 sau mỗi đột biến.

Chạy: python3 bin/corp_action_broker_detect_selfcheck.py [--replay] [--mutations]
Theo §16/§19: chạy thêm dưới `env -u TZ` và `TZ=America/New_York` — kết quả phải y hệt.
"""
import hashlib
import json
import os
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
    if not cond:
        print(f"❌ FAIL: {name} — {detail}")


# ─────────────────────────────────────────────────────────────── dựng bản ghi DNSE giả ──
D, PREV, EX = "2026-10-01", "2026-09-30", "2026-10-02"     # Thứ Năm → Thứ Sáu (phiên kế tiếp)
A1, A2 = ("0002023347", "SpaceX"), ("0001743768", "ZaloPay")


def lot(lid, q, cost, mkt, mod, trade=None, closed=0, accum=None, acct=A1[0], sym="TPB"):
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


def tpb_series(post_n=3, mod=CR_MOD, q1=230, cost1=14173.913, mkt1=12100, trade1=200, closed1=0,
               accum1=None):
    pre = lot(2674331, 200, 16800, 14450, PRE_MOD)
    post = lot(2674331, q1, cost1, mkt1, mod, trade=trade1, closed=closed1,
               accum=(230 if accum1 is None else accum1))
    pre_d = dict(pre, accumulateQuantity=200)
    s = [snap(f"{PREV}T23:30:04", pre_d), snap(f"{D}T04:54:17", pre_d), snap(f"{D}T11:16:29", pre_d)]
    for i in range(post_n):
        s.append(snap(f"{D}T19:{3 + i:02d}:01", post))
    return s


def test_A():
    ev = BD.account_evidence(tpb_series(), "TPB", D)
    check("A1 TPB tài khoản CONFIRMABLE", ev["verdict"] == BD.CONFIRMABLE, ev)
    check("A1b chân tiền 500 suy từ giá vốn", ev.get("cash_leg") == 500.0, ev.get("cash_leg"))
    dec = BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400)
    check("A2 TPB quyết định CONFIRMABLE ×1.15", dec["verdict"] == BD.CONFIRMABLE
          and dec.get("qty_multiplier") == 1.15, dec.get("why"))
    rec = BD.build_record(dec, "2026-10-01T19:25:00+07:00")
    v = CA.validate(rec)
    check("A3 record qua validate(), CONFIRMED, chân tiền 500, ex phiên kế tiếp",
          v["_status"].startswith("CONFIRMED") and v["cash_leg_vnd_per_share"] == 500.0
          and v["ex_date"] == EX and rec["provenance"] == "broker", v)
    check("A3b broker_effective_ts = credit UTC (cùng quy ước registry)",
          rec["broker_effective_ts"] == "2026-10-01T11:52:12", rec["broker_effective_ts"])

    # mua / lệnh ma: KL tăng + giá vốn TĂNG
    buy = tpb_series(q1=230, cost1=(200 * 16800 + 30 * 14400) / 230, mkt1=14400)
    check("A4 mua (giá vốn tăng) ⇒ NOT_CANDIDATE",
          BD.account_evidence(buy, "TPB", D)["verdict"] == BD.NOT_CANDIDATE)
    ghost = tpb_series(q1=201, cost1=(200 * 16800 + 1 * 100) / 201)
    check("A5 lệnh ma 1cp giá 100đ (giá vốn vẫn tăng) ⇒ NOT_CANDIDATE",
          BD.account_evidence(ghost, "TPB", D)["verdict"] == BD.NOT_CANDIDATE)
    sold = tpb_series(closed1=10, accum1=240)
    check("A6 có bán trong cửa sổ ⇒ AMBIGUOUS",
          BD.account_evidence(sold, "TPB", D)["verdict"] == BD.AMBIGUOUS)
    sold_inconsistent = tpb_series(closed1=10)       # closed đổi mà accum vẫn khớp KL (phòng thủ kép)
    check("A6b closedQuantity đổi (dù accum khớp) ⇒ AMBIGUOUS",
          BD.account_evidence(sold_inconsistent, "TPB", D)["verdict"] == BD.AMBIGUOUS)
    mid = tpb_series(mod="2026-10-01T03:00:00.000Z")           # 10:00 ICT giữa phiên
    e = BD.account_evidence(mid, "TPB", D)
    check("A7 credit giữa phiên ⇒ AMBIGUOUS (không có bằng chứng ex-date)",
          e["verdict"] == BD.AMBIGUOUS and "cửa sổ" in e["why"], e.get("why"))
    late = tpb_series(mod="2026-10-01T17:30:00.000Z")          # 00:30 ICT 10-02
    check("A8 credit sau nửa đêm ⇒ AMBIGUOUS",
          BD.account_evidence(late, "TPB", D)["verdict"] == BD.AMBIGUOUS)
    one = tpb_series(post_n=1)
    check("A9 mới 1 bản ghi sau credit ⇒ INSUFFICIENT",
          BD.account_evidence(one, "TPB", D)["verdict"] == BD.INSUFFICIENT)
    tradeable = tpb_series(trade1=230)
    check("A10 CP mới bán được ngay (trade > KL trước) ⇒ AMBIGUOUS",
          BD.account_evidence(tradeable, "TPB", D)["verdict"] == BD.AMBIGUOUS)
    fills = [(BD.modified_ict("2026-10-01T07:00:00Z"), 30, "NB")]
    check("A11 sổ lệnh có khớp sau bản ghi trước credit ⇒ AMBIGUOUS",
          BD.account_evidence(tpb_series(), "TPB", D, fills)["verdict"] == BD.AMBIGUOUS)
    early_fill = [(BD.modified_ict("2026-10-01T02:00:00Z"), 30, "NB")]   # 09:00 < bản ghi 11:16
    check("A11b khớp TRƯỚC bản ghi trước-credit không làm hỏng",
          BD.account_evidence(tpb_series(), "TPB", D, early_fill)["verdict"] == BD.CONFIRMABLE)
    accbad = tpb_series(accum1=231)
    check("A12 accumulateQuantity lệch KL ⇒ AMBIGUOUS",
          BD.account_evidence(accbad, "TPB", D)["verdict"] == BD.AMBIGUOUS)
    frac5 = BD.modified_ict("2026-09-09T11:45:22.23138Z")
    check("A13 modifiedDate 5 chữ số thập phân parse được (VIB)",
          frac5 is not None and frac5.hour == 18 and frac5.minute == 45, frac5)
    nano = BD.modified_ict("2026-08-14T12:09:00.785778421Z")
    check("A13b modifiedDate nano giây parse được", nano is not None and nano.hour == 19, nano)

    # quyền mua (MBB-like): KL +15% nhưng giá tham chiếu rơi sâu hơn ⇒ không giao
    mbb = BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400 * 1.12)
    check("A14 giá không khớp hệ số KL (quyền mua/khác sự kiện) ⇒ AMBIGUOUS, nói rõ KL∩giá rỗng",
          mbb["verdict"] == BD.AMBIGUOUS and "KHÔNG giao" in mbb.get("why", ""), mbb.get("why"))
    check("A15 thiếu giá cum ⇒ INSUFFICIENT",
          BD.decide("TPB", D, EX, {"SpaceX": ev}, [], None)["verdict"] == BD.INSUFFICIENT)
    check("A16 tài khoản khác giữ mã mà chưa credit ⇒ INSUFFICIENT",
          BD.decide("TPB", D, EX, {"SpaceX": ev}, ["ZaloPay"], 14400)["verdict"] == BD.INSUFFICIENT)
    ev2 = dict(ev, cash_leg=450.0)
    check("A17 chân tiền lệch giữa tài khoản ⇒ AMBIGUOUS",
          BD.decide("TPB", D, EX, {"SpaceX": ev, "ZaloPay": ev2}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)
    iss = {"ticker": "TPB", "date": EX, "event_code": "ISS", "price_adjusting": True,
           "exercise_ratio": 0.15}
    check("A18 vendor có ISS ⇒ DEFER_VENDOR (không ghi đè)",
          BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400, iss)["verdict"] == BD.DEFER_VENDOR)
    div = {"ticker": "TPB", "date": EX, "event_code": "DIV", "price_adjusting": True,
           "value_per_share": 800}
    check("A19 vendor DIV 800 ≠ chân tiền 500 ⇒ AMBIGUOUS",
          BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400, div)["verdict"] == BD.AMBIGUOUS)
    div_ok = dict(div, value_per_share=500)
    check("A19b vendor DIV 500 = chân tiền ⇒ vẫn CONFIRMABLE",
          BD.decide("TPB", D, EX, {"SpaceX": ev}, [], 14400, div_ok)["verdict"] == BD.CONFIRMABLE)
    amb = dict(ev, verdict=BD.AMBIGUOUS, why="x")
    check("A20 một tài khoản AMBIGUOUS ⇒ cả mã AMBIGUOUS",
          BD.decide("TPB", D, EX, {"SpaceX": ev, "ZaloPay": amb}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)
    ev_m = dict(ev, q0=100, q1=1200, m_lo=12.0, m_hi=12.01, cash_leg=0.0, mkt1=[1200.0])
    check("A21 hệ số > QTY_MULT_MAX ⇒ AMBIGUOUS (không để validate() nổ ở điểm ghi)",
          BD.decide("TPB", D, EX, {"SpaceX": ev_m}, [], 14400)["verdict"] == BD.AMBIGUOUS)
    disj = dict(ev, m_lo=1.2, m_hi=1.21)
    check("A22 hệ số KL hai tài khoản không giao nhau ⇒ AMBIGUOUS",
          BD.decide("TPB", D, EX, {"SpaceX": ev, "ZaloPay": disj}, [], 14400)["verdict"]
          == BD.AMBIGUOUS)

    # BID-like: ZaloPay 2 gói vay, credit DỞ 19:10 (1 gói) rồi xong 20:15
    def bid(ts, l1, l2):
        return snap(ts, l1, l2)
    m0 = "2026-08-13T11:40:12Z"
    p1 = lot(1, 100, 39550, 38850, m0, acct=A2[0], sym="BID")
    p2 = lot(2, 300, 40316.6667, 38850, m0, closed=600, accum=900, acct=A2[0], sym="BID")
    c1 = lot(1, 107, 36962.6168, 35800, "2026-08-14T12:09:00.785778Z", trade=100, accum=107,
             acct=A2[0], sym="BID")
    c2 = lot(2, 320, 37796.875, 35800, "2026-08-14T13:15:09Z", trade=300, closed=600, accum=920,
             acct=A2[0], sym="BID")
    ser = [bid("2026-08-13T23:00:00", p1, p2), bid("2026-08-14T19:04:00", p1, p2),
           bid("2026-08-14T19:10:23", c1, p2)]
    e_mid = BD.account_evidence(ser, "BID", "2026-08-14")
    check("A23 gói vay dở (marketPrice lẫn hệ) ⇒ INSUFFICIENT, không phải AMBIGUOUS",
          e_mid["verdict"] == BD.INSUFFICIENT, e_mid)
    ser2 = ser + [bid("2026-08-14T20:15:02", c1, c2), bid("2026-08-14T20:30:02", c1, c2)]
    e_done = BD.account_evidence(ser2, "BID", "2026-08-14")
    check("A24 gói vay xong ⇒ lùi qua trạng thái dở, KL 400→427",
          e_done["verdict"] == BD.CONFIRMABLE and e_done["q0"] == 400 and e_done["q1"] == 427,
          e_done)
    sx = BD.account_evidence([snap("2026-08-13T23:00:00", lot(9, 1100, 42269.3675, 38850, m0, sym="BID")),
                              snap("2026-08-14T19:11:05", lot(9, 1175, 39571.3228, 35800,
                                                             "2026-08-14T12:08:57.584625573Z",
                                                             trade=1100, sym="BID")),
                              snap("2026-08-14T20:15:03", lot(9, 1175, 39571.3228, 35800,
                                                             "2026-08-14T12:08:57.584625Z",
                                                             trade=1100, sym="BID"))], "BID", "2026-08-14")
    dbid = BD.decide("BID", "2026-08-14", "2026-08-17", {"SpaceX": sx, "ZaloPay": e_done}, [], 38250)
    check("A26 BID 2 tài khoản ⇒ ×1.069 (số NGẮN NHẤT tái tạo 1100→1175 VÀ 400→427)",
          dbid["verdict"] == BD.CONFIRMABLE and dbid.get("qty_multiplier") == 1.069, dbid.get("why"))
    check("A25 simplest_in", BD.simplest_in(1.068182, 1.069091) == 1.069
          and BD.simplest_in(1.15, 1.155) == 1.15 and BD.simplest_in(1.26, 1.2608333) == 1.26
          and BD.simplest_in(1.0, 1.0) is None)


# ─────────────────────────────────────────────────────────────── B. run_broker sandbox ──

class _Bus:
    calls = []

    @staticmethod
    def run(cmd, **kw):
        _Bus.calls.append(list(cmd))

        class R:
            returncode, stdout, stderr = 0, "", ""
        return R()


def _write_raw(exec_dir, day, series_by_acct):
    path = os.path.join(exec_dir, f"dnse_raw_{day}.jsonl")
    lines = []
    for (acct, label), series in series_by_acct.items():
        for ts, by in series:
            if not ts.startswith(day):
                continue
            pos = [r for rows in by.values() for r in rows]
            lines.append({"ts": ts, "kind": "positions", "account_no": acct, "account_label": label,
                          "payload": {"positions": pos}})
    lines.sort(key=lambda x: x["ts"])
    with open(path, "w", encoding="utf-8") as f:
        for x in lines:
            f.write(json.dumps(x) + "\n")


def _sandbox(registry_actions=None):
    tmp = tempfile.mkdtemp(prefix="brokerca_")
    ex, ca = os.path.join(tmp, "exec"), os.path.join(tmp, "ca_daily")
    os.makedirs(ex)
    os.makedirs(ca)
    ser = tpb_series()
    _write_raw(ex, PREV, {A1: ser})
    _write_raw(ex, D, {A1: ser})
    reg = os.path.join(tmp, "corp_actions.json")
    with open(reg, "w", encoding="utf-8") as f:
        json.dump({"actions": registry_actions or []}, f)
    cac.EXEC_DIR, cac.CA_DAILY_DIR, cac.CORP_ACTIONS_FILE = ex, ca, reg
    cac.LEDGER_FILE = os.path.join(tmp, "ledger.jsonl")
    cac._px_cum_fn = lambda d: (lambda t, dd: {"TPB": 14400}.get(t))
    _Bus.calls = []
    return tmp, reg


def _ledger_lines():
    if not os.path.exists(cac.LEDGER_FILE):
        return []
    return [json.loads(x) for x in open(cac.LEDGER_FILE, encoding="utf-8") if x.strip()]


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
        check("B2 shadow ghi 1 dòng sổ CONFIRMABLE kèm record dự kiến",
              len(lg) == 1 and lg[0]["verdict"] == BD.CONFIRMABLE and lg[0]["record"]["qty_multiplier"] == 1.15,
              lg)
        kinds = [c[2] for c in _Bus.calls]
        check("B3 shadow: 1 bus finding, 0 question", kinds == ["finding"], _Bus.calls)
        n = len(_Bus.calls)
        cac.run_broker(D, mode="shadow")
        check("B4 shadow chạy lại idempotent (0 dòng sổ mới, 0 bus mới)",
              len(_ledger_lines()) == 1 and len(_Bus.calls) == n)

        tmp, reg = _sandbox()
        rc = cac.run_broker(D, mode="live")
        acts = CA.load_corp_actions(reg)
        check("B5 live: registry có TPB CONFIRMED ×1.15 ex 10-02 chân tiền 500 (đọc lại qua load_corp_actions)",
              rc == 0 and len(acts) == 1 and acts[0]["qty_multiplier"] == 1.15
              and acts[0]["ex_date"] == EX and acts[0]["cash_leg_vnd_per_share"] == 500.0, acts)
        check("B6 live: không file .tmp sót", not [f for f in os.listdir(tmp) if f.endswith(".tmp")])
        check("B7 live: bus finding corp-action-broker-confirm-TPB",
              [c[3] for c in _Bus.calls] == ["corp-action-broker-confirm-TPB"], _Bus.calls)
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
        proposed = dict(manual, _status="PROPOSED — chờ")
        tmp, reg = _sandbox([proposed])
        h0 = _sha(reg)
        cac.run_broker(D, mode="live")
        check("B9b record PROPOSED do người viết ⇒ broker KHÔNG ghi đè/ghi trùng", _sha(reg) == h0)

        tmp, reg = _sandbox()
        cac._px_cum_fn = lambda d: (lambda t, dd: 14400 * 1.12)       # giá không khớp
        cac.run_broker(D, mode="live")
        q = [c for c in _Bus.calls if c[2] == "question"]
        check("B10 live mơ hồ ⇒ đúng 1 question, registry rỗng",
              len(q) == 1 and "corp-action-broker-ambiguous-TPB" in q[0][3]
              and CA.load_corp_actions(reg) == [], _Bus.calls)
        cac.run_broker(D, mode="live")
        check("B11 mơ hồ chạy lại ⇒ không hỏi lần 2",
              len([c for c in _Bus.calls if c[2] == "question"]) == 1)

        tmp, reg = _sandbox()
        os.environ["MIKE_CA_BROKER_SOURCE"] = "off"
        try:
            cac.run_vendor = lambda *a, **k: 0
            rc = cac.run(D)
        finally:
            os.environ.pop("MIKE_CA_BROKER_SOURCE", None)
        check("B12 off ⇒ không sổ, không bus", rc == 0 and not _ledger_lines() and not _Bus.calls)
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
        rc = cac.run_broker(D, mode="live")
        check("B15 record cũ hỏng ⇒ rc=1, registry y nguyên, sổ KHÔNG ghi CONFIRMABLE, có question",
              rc == 1 and _sha(reg) == h0 and not _ledger_lines()
              and any(c[2] == "question" for c in _Bus.calls), (rc, _Bus.calls))
    finally:
        subprocess.run = real_run


# ─────────────────────────────────────────────────────────────── C. exdate_frame fallback ──

def test_C():
    tmp = tempfile.mkdtemp(prefix="brokerca_xf_")
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

MUTANTS = [
    ("bin/corp_action_broker_detect.py", '    if s1["cost"] - s0["cost"] > cost_tol(s0, s1):', '    if False:', "bỏ lọc giá vốn tăng"),
    ("bin/corp_action_broker_detect.py", 'if s1["closed"] != s0["closed"]:', 'if False:', "bỏ check bán"),
    ("bin/corp_action_broker_detect.py", 'if s1["trade"] > q0:', 'if False:', "bỏ check trade"),
    ("bin/corp_action_broker_detect.py", 'm.time() >= CREDIT_WINDOW_START]', 'True]', "bỏ cửa sổ giờ"),
    ("bin/corp_action_broker_detect.py", 'if n_post < MIN_POST_SNAPSHOTS:', 'if False:', "bỏ đòi ≥2 bản ghi"),
    ("bin/corp_action_broker_detect.py", 'if abs((s1["accum"] - s0["accum"]) - (q1 - q0)) > 1e-9:', 'if False:', "bỏ check accum"),
    ("bin/corp_action_broker_detect.py", 'if late:', 'if False:', "bỏ check lệnh khớp muộn"),
    ("bin/corp_action_broker_detect.py", '    if lo2 >= hi2:', '    if False:', "bỏ giao KL∩giá"),
    ("bin/corp_action_broker_detect.py", '    if holders_not_credited:', '    if False:', "bỏ check tài khoản chưa credit"),
    ("bin/corp_action_broker_detect.py", '    if max(cash) - min(cash) > 1.0:', '    if False:', "bỏ check chân tiền chéo"),
    ("bin/corp_action_broker_detect.py", '        if abs(v - c) > 1.0:', '        if False:', "bỏ đối chiếu DIV vendor"),
    ("bin/corp_action_broker_detect.py", '    if m > QTY_MULT_MAX:', '    if False:', "bỏ biên hệ số"),
    ("bin/corp_action_broker_detect.py", '        return dict(out, verdict=DEFER_VENDOR,', '        return dict(out, verdict=CONFIRMABLE,', "không nhường vendor"),
    ("bin/corp_action_broker_detect.py", "(frac + '000000')[:6]", "frac[:6]", "parse 5 chữ số"),
    ("bin/corp_action_broker_detect.py", 'and _credit_like(segs[j - 1][1], segs[j][1]) and _credit_like(segs[j][1], s1)):', 'and False):', "không lùi qua credit dở"),
    ("bin/corp_action_broker_detect.py", '        if off and inside:', '        if False:', "gói vay dở thành AMBIGUOUS/không phát hiện"),
    ("bin/corp_action_broker_detect.py", '    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 1) / q0', '    ev["m_lo"], ev["m_hi"] = q1 / q0, (q1 + 5) / q0', "nới khoảng hệ số KL"),
    ("bin/corp_action_auto_confirm.py", '        if (tk, ex) in in_registry:', '        if False:', "không kiểm registry sẵn có"),
    ("bin/corp_action_auto_confirm.py", '        if key in done:', '        if False:', "bỏ idempotent sổ"),
    ("bin/corp_action_auto_confirm.py", '            if mode == "live":\n                new_recs.append', '            if True:\n                new_recs.append', "shadow vẫn ghi registry"),
    ("bin/corp_action_auto_confirm.py", '        return "shadow"\n    return raw', '        return "live"\n    return raw', "mode lạ ⇒ live"),
    ("bin/corp_action_auto_confirm.py", '            return 1\n        back =', '            pass\n        back =', "nuốt lỗi validate"),
    ("bin/exdate_frame.py", 'return os.environ.get(REGISTRY_FALLBACK_ENV, "0").strip() == "1"', 'return True', "fallback mặc định BẬT"),
    ("bin/exdate_frame.py", '        if a["ex_date"] == nxt:', '        if True:', "bỏ khớp ex phiên kế tiếp"),
    ("bin/exdate_frame.py", '                detail["cash_leg_vnd_per_share"] = ev.get("cash_leg_vnd_per_share", 0.0)', '                pass', "rơi chân tiền"),
]


def run_mutations():
    root = os.path.dirname(HERE)
    killed, survived = [], []
    # PYTHONDONTWRITEBYTECODE: đột biến cùng KÍCH THƯỚC file, ghi trong cùng giây ⇒ `.pyc` cũ
    # (khoá mtime+size) bị coi là còn hợp lệ ⇒ tiến trình sau nạp bản ĐỘT BIẾN trước đó dù file
    # đã khôi phục — đã cắn thật khi viết file này ("(q1 + 5)" sống sót trong __pycache__).
    env = dict(os.environ, BROKERCA_SELFCHECK_CHILD="1", PYTHONDONTWRITEBYTECODE="1")
    pyc = os.path.join(HERE, "__pycache__")

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
            (killed if r.returncode != 0 else survived).append(label)
        finally:
            open(p, "w", encoding="utf-8").write(src)
            assert hashlib.sha256(open(p, encoding="utf-8").read().encode()).hexdigest() == h, \
                f"KHÔNG khôi phục được {rel}"
            _purge()
    print(f"\nMUTATION: {len(killed)}/{len(MUTANTS)} bị giết")
    for s_ in survived:
        print(f"  ⚠ SỐNG: {s_}")
    return not survived


def main():
    test_A()
    test_B()
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
