#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck bộ chọn DD v2 (`discretionary_dd_pick.py`) — dữ liệu tổng hợp, sandbox tmpdir, 0 BQ/DNSE.
Chạy: python3 bin/discretionary_dd_pick_selfcheck.py   (chạy cả dưới `env -u TZ` và TZ=America/New_York)."""
import datetime as dt
import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_dd_pick as P  # noqa: E402

FAILS = []
N = [0]


def ok(cond, msg):
    N[0] += 1
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


ICT = P.ICT
ASOF = dt.date(2026, 10, 30)          # thứ Sáu
NOW = dt.datetime(2026, 10, 30, 19, 37, tzinfo=ICT)


def gate(tmp, mode):
    """Cổng mùa giả: 'RUN' / 'SKIP' / 'BROKEN' (rc 1)."""
    p = os.path.join(tmp, f"gate_{mode}.sh")
    body = {"RUN": 'echo RUN', "SKIP": 'echo "SKIP: month=12 ngoai cua so"', "BROKEN": 'echo boom >&2; exit 1'}[mode]
    with open(p, "w") as f:
        f.write(f"#!/bin/bash\n{body}\n")
    return p


def rating_df():
    rows = [
        # ticker route rating ROE CF redflag liq PE earn_yield cfo_np
        ("AAA", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 8, 0.125, 1.2),
        ("BBB", "COMPOUNDER", 2, 0.1, 1.0, None, 5.0, 6, 0.166, 0.8),
        ("CCC", "COMPOUNDER", 3, 0.1, 1.0, None, 5.0, 5, 0.20, -0.5),
        ("HLD", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # đang giữ
        ("REC", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # DD gần đây (thư mục)
        ("BAN", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # BANNED
        ("LOW", "CYCLICAL", 2, 0.1, 1.0, None, 5.0, 5, 0.20, 1.0),     # nền thấp
        ("BNK", "BANK", 2, 0.1, 1.0, None, 50.0, 5, 0.20, None),       # DCF NA
        ("BNX", "BANK", 3, 0.1, 1.0, None, 50.0, 8, 0.125, None),
        ("R4", "COMPOUNDER", 4, 0.1, 1.0, None, 5.0, 3, 0.33, 1.0),    # rating 4 ⇒ ngoài vũ trụ
        ("ILQ", "COMPOUNDER", 1, 0.1, 1.0, None, 0.1, 3, 0.33, 1.0),   # thanh khoản thấp
    ]
    df = pd.DataFrame(rows, columns=["ticker", "route", "rating", "ROE_Min3Y", "CF_OA_3Y", "redflag",
                                     "liq_bn", "PE", "earn_yield", "cfo_np"])
    df["PB"], df["pb_z"], df["drop_pct"], df["ICB_Code"] = 1.0, 0.0, -5.0, 1000.0
    return df


def fin_df():
    k_new, k_old = pd.Timestamp("2026-10-20"), pd.Timestamp("2026-07-25")
    d = {  # NP_P0, NP_P1, NP_P4, known
        "AAA": (150, 120, 100, k_new), "BBB": (200, 150, 100, k_new), "CCC": (300, 200, 100, k_new),
        "HLD": (300, 200, 100, k_new), "REC": (300, 200, 100, k_new), "BAN": (300, 200, 100, k_new),
        "LOW": (500, 100, 50, k_new), "BNK": (120, 110, 100, k_old), "BNX": (130, 110, 100, k_old),
        "R4": (100, 90, 80, k_new), "ILQ": (100, 90, 80, k_new)}
    f = pd.DataFrame([(t, "2026Q3", v[3], v[0], v[1], v[2]) for t, v in d.items()],
                     columns=["ticker", "quarter", "known", "NP_P0", "NP_P1", "NP_P4"]).set_index("ticker")
    f["season_norm"], f["seasonal"], f["season_eta2"], f["np_missing"] = 0.0, False, np.nan, False
    return f


MOS = {"AAA": 0.50, "BBB": 0.30, "CCC": 0.60, "HLD": 0.9, "REC": 0.9, "BAN": 0.9, "LOW": 0.70,
       "R4": 0.9, "ILQ": 0.9}


def dcf_fn(t, p):
    if t not in MOS:
        return {"ok": False, "reason": "financial-sector"}
    m = MOS[t]
    fv = p / (1 - m)
    sens = {k: {"fv": fv} for k in P._dcf_engine()._SENS_KEYS}
    return {"ok": True, "margin_of_safety": m, "fair_value_ps": fv, "sensitivity": sens}


def setup(tmp):
    ex = os.path.join(tmp, "exec")
    os.makedirs(ex, exist_ok=True)
    for a, pos, excl in (("SpaceX", [{"ticker": "HLD", "qty": 100}, {"ticker": "ZZZ", "qty": 0}], []),
                         ("ZaloPay", [], ["CCC_NOT"])):
        with open(os.path.join(ex, f"active_nav_{a}.json"), "w") as f:
            json.dump({"positions": pos, "excluded_tickers": excl}, f)
    rd = os.path.join(tmp, "research")
    os.makedirs(os.path.join(rd, "dd_REC_20261015"), exist_ok=True)
    os.makedirs(os.path.join(rd, "dd_AAA_20260601"), exist_ok=True)       # quá 90 ngày ⇒ không chặn
    base = os.path.join(tmp, "data")
    os.makedirs(base, exist_ok=True)
    return ex, rd, base


def run(tmp, base, ex, rd, gmode="RUN", asof=ASOF, now=NOW, live_fn=None, write=True):
    prices = {t: (10000.0, asof) for t in rating_df()["ticker"]}
    cands = pd.DataFrame({"ticker": ["CCC"], "lane": ["A"]})
    return P.run_pick(rating_df(), fin_df(), cands, {"BAN"}, {}, {}, asof, base_dir=base, write=write,
                      now=now, exec_dir=ex, research_dir=rd, gate=gate(tmp, gmode), dcf_fn=dcf_fn,
                      live_fn=live_fn, prices=prices)


def t_scoring():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r = run(tmp, base, ex, rd)
        tk = [x["ticker"] for x in r["top"]]
        for bad in ("HLD", "REC", "BAN", "R4", "ILQ"):
            ok(bad not in tk, f"{bad} phải bị loại khỏi pool, top={tk}")
        ok("AAA" in tk, "AAA (DD cũ > 90 ngày) KHÔNG bị chặn")
        ok(r["pool_n"] == 6, f"pool_n 6, được {r['pool_n']}")
        top = {x["ticker"]: x for x in r["top"]}
        # LOW: YoY 900% ⇒ nen_thap, q=0,3, không lên tầng đầy đủ dù MoS 70%
        ok("nen_thap" in top["LOW"]["labels"] and top["LOW"]["q"] == P.Q_BAD, "LOW phải nen_thap q=0,3")
        ok(top["LOW"]["escalate_full"] is False, "nen_thap không được escalate")
        # CCC cfo_np<0 ⇒ q 0,3; làn A ⇒ nhãn lech_gia nhưng không cộng điểm
        ok(top["CCC"]["q"] == P.Q_BAD and "lech_gia" in top["CCC"]["labels"], "CCC q=0,3 + nhãn lech_gia")
        # BNK/BNX: dcf_na, V = phân vị earn_yield trong route BANK × 0,8; BCTC cũ ⇒ E=0
        ok(top["BNK"]["V"] == 1.0 * P.DCF_NA_HAIRCUT and top["BNX"]["V"] == 0.5 * P.DCF_NA_HAIRCUT,
           f"V dcf_na sai {top['BNK']['V']} {top['BNX']['V']}")
        ok(top["BNK"]["E"] == 0.0 and "bctc_moi" not in top["BNK"]["labels"], "BCTC > 45 ngày ⇒ E=0")
        ok(top["BNK"]["escalate_full"] is False, "dcf_na không tự escalate")
        # score = công thức PREREG
        for x in r["top"]:
            ok(abs(x["score"] - (0.5 * x["V"] + 0.3 * x["E"] + 0.2 * x["R"])) < 1e-9, f"score {x['ticker']}")
        ok([x["score"] for x in r["top"]] == sorted([x["score"] for x in r["top"]], reverse=True), "thứ tự score")
        ok(r["picked"]["ticker"] == r["top"][0]["ticker"] and r["picked"]["picked"] is True, "pick = top-1")
        ok(sum(1 for x in r["top"] if x["picked"]) == 1, "đúng 1 picked")
        json.dumps(r, ensure_ascii=False)                    # serialize được (result json)
        ok(True, "json")


def t_append_only_replay():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r1 = run(tmp, base, ex, rd)
        log = P.pick_paths(base)["log"]
        b1 = open(log, "rb").read()
        MOS["BBB"] = 0.99                                   # dữ liệu đổi — chạy lại cùng asof vẫn KHÔNG đổi
        try:
            r2 = run(tmp, base, ex, rd)
        finally:
            MOS["BBB"] = 0.30
        ok(open(log, "rb").read() == b1, "chạy lại cùng asof KHÔNG được ghi thêm/ghi đè nhật ký")
        ok(r2["replayed"] and r2["picked"]["ticker"] == r1["picked"]["ticker"], "replay giữ nguyên pick")
        ok(len(pd.read_csv(log)) == len(r1["top"]) >= 5, "K>=5 dòng/asof gồm cả mã không chọn")
        # asof mới ⇒ append, mã đã picked hôm trước bị cooldown
        r3 = run(tmp, base, ex, rd, asof=dt.date(2026, 11, 2), now=NOW + dt.timedelta(days=3))
        ok(len(pd.read_csv(log)) == len(r1["top"]) + len(r3["top"]), "asof mới append")
        ok(r1["picked"]["ticker"] not in [x["ticker"] for x in r3["top"]], "mã đã đề xuất bị cooldown 90 ngày")
        ok(open(log, "rb").read().startswith(b1), "phần cũ của nhật ký giữ nguyên byte")
        # write=False không ghi
        with tempfile.TemporaryDirectory() as t2:
            ex2, rd2, base2 = setup(t2)
            run(t2, base2, ex2, rd2, write=False)
            ok(not os.path.exists(P.pick_paths(base2)["log"]), "dry-run không ghi nhật ký")


def t_offseason_week():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r1 = run(tmp, base, ex, rd, gmode="SKIP", asof=dt.date(2026, 12, 1), now=NOW + dt.timedelta(days=32))
        ok(r1["picked"] is not None and r1["season"] is False, "ngoài mùa: pick đầu tuần OK")
        r2 = run(tmp, base, ex, rd, gmode="SKIP", asof=dt.date(2026, 12, 2), now=NOW + dt.timedelta(days=33))
        ok(r2["picked"] is None and "tuần này đã đề xuất" in r2["reason"], f"ngoài mùa: pick 2 cùng tuần phải bị chặn ({r2['reason']})")
        ok(len(r2["top"]) >= 5, "vẫn ghi top-K khi không chọn")
        r3 = run(tmp, base, ex, rd, gmode="SKIP", asof=dt.date(2026, 12, 7), now=NOW + dt.timedelta(days=38))
        ok(r3["picked"] is not None, "tuần ISO mới ⇒ pick lại được")
        # mùa: mỗi asof 1 pick
        r4 = run(tmp, base, ex, rd, gmode="RUN", asof=dt.date(2027, 1, 12), now=NOW + dt.timedelta(days=74))
        r5 = run(tmp, base, ex, rd, gmode="RUN", asof=dt.date(2027, 1, 13), now=NOW + dt.timedelta(days=75))
        ok(r4["picked"] is not None and r5["picked"] is not None, "mùa: 1 pick mỗi phiên")
        # cổng mùa hỏng ⇒ NGOÀI mùa (chặt hơn)
        s, note = P.in_season(dt.date(2027, 1, 14), gate(tmp, "BROKEN"))
        ok(s is False and "coi NGOÀI mùa" in note, "cổng mùa lỗi ⇒ ngoài mùa")


def t_claims():
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "d")
        os.makedirs(base)
        d0 = dt.date(2026, 12, 1)                           # thứ Ba, ngoài mùa
        g = gate(tmp, "SKIP")
        ok(P.claim("aaa", "full", d0, base, gate=g)[0] == 0, "off full #1")
        ok(P.claim("bbb", "full", d0 + dt.timedelta(days=1), base, gate=g)[0] == 0, "off full #2")
        rc, msg = P.claim("ccc", "full", d0 + dt.timedelta(days=2), base, gate=g)
        ok(rc == 2 and "HẾT SUẤT" in msg, "off full #3 cùng tuần phải bị chặn")
        ok(P.claim("ccc", "full", dt.date(2026, 12, 7), base, gate=g)[0] == 0, "tuần mới full OK")
        ok(P.claim("x", "light", d0, base, gate=g)[0] == 0, "off light #1")
        ok(P.claim("y", "light", d0 + dt.timedelta(days=3), base, gate=g)[0] == 2, "off light #2 cùng tuần chặn")
        gr = gate(tmp, "RUN")
        dd = dt.date(2027, 1, 12)
        ok(P.claim("m1", "full", dd, base, gate=gr)[0] == 0, "mùa full #1/ngày")
        ok(P.claim("m2", "full", dd, base, gate=gr)[0] == 2, "mùa full #2 cùng ngày chặn")
        ok(P.claim("m3", "full", dd + dt.timedelta(days=1), base, gate=gr)[0] == 0, "mùa ngày mới OK")
        # cổng mùa hỏng trong mùa ⇒ áp trần ngoài mùa (2/tuần): tuần đã dùng 2 ⇒ chặn
        ok(P.claim("m4", "full", dd + dt.timedelta(days=2), base, gate=gate(tmp, "BROKEN"))[0] == 2,
           "cổng hỏng ⇒ trần tuần (đã 2) ⇒ chặn")
        ok(P.claim("z", "medium", dd, base, gate=gr)[0] == 2, "tier sai rc=2")
        led = P.pick_paths(base)["ledger"]
        n_before = sum(1 for _ in open(led))
        with open(led, "a") as f:
            f.write("{hỏng\n")
        rc, msg = P.claim("q", "light", dt.date(2027, 2, 1), base, gate=gr)
        ok(rc == 2 and "fail-closed" in msg, "sổ hỏng ⇒ từ chối")
        ok("KHÔNG XÁC ĐỊNH" in P.slots_line(dd, base, gr), "slots_line báo sổ hỏng")
        ok(sum(1 for _ in open(led)) == n_before + 1, "claim bị từ chối không ghi thêm")
        # sổ hỏng ⇒ run_pick không đề xuất
        ex, rd, _ = setup(tmp)
        r = run(tmp, base, ex, rd)
        ok(r["picked"] is None and "fail-closed" in r["reason"], "sổ hỏng ⇒ không pick")


def t_live_downgrade_and_topic():
    MOS["AAA"] = 0.95                                       # AAA đứng đầu + đạt ngưỡng fin-path
    try:
        _t_live()
    finally:
        MOS["AAA"] = 0.50


def _t_live():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r0 = run(tmp, base, ex, rd, write=False, live_fn=lambda t, p: {"ok": True, "margin_of_safety": 0.9})
        ok(r0["picked"]["ticker"] == "AAA" and r0["picked"]["escalate_full"] is True, "AAA escalate khi live đạt")
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r = run(tmp, base, ex, rd, live_fn=lambda t, p: {"ok": True, "margin_of_safety": 0.10})
        ok(r["picked"]["escalate_full"] is False and "live_mos_0.10" in r["picked"]["labels"],
           "MoS live < 25% ⇒ hạ tầng đầy đủ")
        line = P.topic_line(r, ASOF + dt.timedelta(days=3), base, gate(tmp, "RUN"))
        ok(line.startswith("🔎 Mã DD hôm nay: **") and "chỉ DD tầng nhẹ" in line and "còn 1/1 hôm nay" in line,
           f"dòng topic: {line[:160]}")
        ok("\n" not in line, "đúng 1 dòng")
        ok("bộ chọn KHÔNG chạy" in P.topic_line(None, ASOF, base, gate(tmp, "RUN")), "pick None ⇒ báo, không im")
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        def boom(t, p):
            raise RuntimeError("x")
        r = run(tmp, base, ex, rd, live_fn=boom)
        ok(r["picked"]["escalate_full"] is False and any("DCF live" in w for w in r["warnings"]), "live lỗi ⇒ không escalate + cảnh báo")
        r2 = run(tmp, base, ex, rd, live_fn=lambda t, p: {"ok": True, "margin_of_safety": 0.9})
        ok(r2["replayed"], "replay")


def t_dd_after_asof():
    """Ca thật HPG: DD ngày 31/10, asof 30/10, chạy 01/11 ⇒ phải bị cooldown."""
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        os.makedirs(os.path.join(rd, "dd_BBB_20261031"))
        r = run(tmp, base, ex, rd, now=NOW + dt.timedelta(days=2), write=False)
        ok("BBB" not in [x["ticker"] for x in r["top"]], "DD sau asof trước lúc chạy phải chặn")
        os.makedirs(os.path.join(rd, "dd_AAA_20261105"))              # sau lúc chạy ⇒ chưa biết
        r = run(tmp, base, ex, rd, now=NOW + dt.timedelta(days=2), write=False)
        ok("AAA" in [x["ticker"] for x in r["top"]], "thư mục ngày tương lai không chặn")


def t_held_missing():
    with tempfile.TemporaryDirectory() as tmp:
        h, e, w = P.held_and_excluded(os.path.join(tmp, "nope"))
        ok(not h and len(w) == 2, "thiếu active_nav ⇒ 2 cảnh báo")


if __name__ == "__main__":
    for fn in (t_scoring, t_append_only_replay, t_offseason_week, t_claims, t_live_downgrade_and_topic,
               t_held_missing, t_dd_after_asof):
        fn()
    print(f"TZ={os.environ.get('TZ', '<unset>')} checks={N[0]} fails={len(FAILS)}")
    sys.exit(1 if FAILS else 0)
