#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck bộ chọn DD v2 (`discretionary_dd_pick.py`) — dữ liệu tổng hợp, sandbox tmpdir, 0 BQ/DNSE.
Chạy: python3 bin/discretionary_dd_pick_selfcheck.py   (chạy cả dưới `env -u TZ` và TZ=America/New_York)."""
import datetime as dt
import json
import multiprocessing as mp
import os
import sys
import tempfile
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_dd_pick as P  # noqa: E402

FAILS = []
N = [0]
_KB_EMPTY = tempfile.mkdtemp(prefix="kbempty_")
P.KB_PROJECTS_DIR = _KB_EMPTY          # cô lập khỏi kb/projects thật (DD thật sẽ làm lệch fixture)


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
    body = {"SLOWRUN": 'sleep 0.3; echo RUN', "RUN": 'echo RUN', "SKIP": 'echo "SKIP: month=12 ngoai cua so"', "BROKEN": 'echo boom >&2; exit 1'}[mode]
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
        ("EXC", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # excluded_tickers (ZaloPay)
        ("FOR", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # forensic
        ("INS", "COMPOUNDER", 1, 0.1, 1.0, None, 5.0, 4, 0.25, 1.0),   # insider
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
        "R4": (100, 90, 80, k_new), "ILQ": (100, 90, 80, k_new),
        "EXC": (300, 200, 100, k_new), "FOR": (300, 200, 100, k_new), "INS": (300, 200, 100, k_new)}
    f = pd.DataFrame([(t, "2026Q3", v[3], v[0], v[1], v[2]) for t, v in d.items()],
                     columns=["ticker", "quarter", "known", "NP_P0", "NP_P1", "NP_P4"]).set_index("ticker")
    f["season_norm"], f["seasonal"], f["season_eta2"], f["np_missing"] = 0.0, False, np.nan, False
    return f


MOS = {"AAA": 0.50, "BBB": 0.30, "CCC": 0.60, "HLD": 0.9, "REC": 0.9, "BAN": 0.9, "LOW": 0.70,
       "R4": 0.9, "ILQ": 0.9, "EXC": 0.9, "FOR": 0.9, "INS": 0.9}


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
                         ("ZaloPay", [], ["EXC"])):
        with open(os.path.join(ex, f"active_nav_{a}.json"), "w") as f:
            json.dump({"positions": pos, "excluded_tickers": excl}, f)
    rd = os.path.join(tmp, "research")
    os.makedirs(os.path.join(rd, "dd_REC_20261025"), exist_ok=True)   # SAU BCTC 10-20 ⇒ loại
    os.makedirs(os.path.join(rd, "dd_AAA_20260601"), exist_ok=True)       # DD TRƯỚC BCTC 10-20 ⇒ mã quay lại pool
    base = os.path.join(tmp, "data")
    os.makedirs(base, exist_ok=True)
    return ex, rd, base


def run(tmp, base, ex, rd, gmode="RUN", asof=ASOF, now=NOW, live_fn=None, write=True, dcf=None):
    prices = {t: (10000.0, asof) for t in rating_df()["ticker"]}
    cands = pd.DataFrame({"ticker": ["CCC"], "lane": ["A"]})
    return P.run_pick(rating_df(), fin_df(), cands, {"BAN"}, {"FOR": "x"}, {"INS": "y"}, asof, base_dir=base,
                      write=write, now=now, exec_dir=ex, research_dir=rd, gate=gate(tmp, gmode),
                      dcf_fn=dcf or dcf_fn,
                      live_fn=live_fn, prices=prices, kb_dir=_KB_EMPTY)


def t_scoring():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r = run(tmp, base, ex, rd)
        tk = [x["ticker"] for x in r["top"]]
        for bad in ("HLD", "REC", "BAN", "R4", "ILQ", "EXC", "FOR", "INS"):
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
        ok("dropped_held_or_recent" in r and r["dropped_n"] == 6, f"dropped_n {r['dropped_n']} (HLD,REC,BAN,EXC,FOR,INS)")
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
        r0 = run(tmp, base, ex, rd, write=False, live_fn=lambda t, p, pdt=None: {"ok": True, "margin_of_safety": 0.9})
        ok(r0["picked"]["ticker"] == "AAA" and r0["picked"]["escalate_full"] is True, "AAA escalate khi live đạt")
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r = run(tmp, base, ex, rd, live_fn=lambda t, p, pdt=None: {"ok": True, "margin_of_safety": 0.10})
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
        r2 = run(tmp, base, ex, rd, live_fn=lambda t, p, pdt=None: {"ok": True, "margin_of_safety": 0.9})
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


def _slow_dcf(t, p):
    time.sleep(0.3)
    return dcf_fn(t, p)


def _w_claim(args):
    tmp, base, tk = args
    return P.claim(tk, "full", dt.date(2027, 1, 12), base, gate=gate(tmp, "SLOWRUN"))[0]


def _w_pick(args):
    tmp, base, ex, rd = args
    r = run(tmp, base, ex, rd, dcf=_slow_dcf)
    return (r["replayed"], r["picked"]["ticker"])


def t_concurrency():
    ctx = mp.get_context("fork")
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "d")
        os.makedirs(base)
        with ctx.Pool(3) as pool:                            # 3 TIẾN TRÌNH claim full cùng ngày, mùa (cap 1)
            rcs = pool.map(_w_claim, [(tmp, base, t) for t in ("m1", "m2", "m3")])
        ok(sorted(rcs) == [0, 2, 2], f"3 tiến trình claim song song: đúng 1 rc=0, được {rcs}")
        ok(sum(1 for _ in open(P.pick_paths(base)["ledger"])) == 1, "sổ đúng 1 dòng")
        # claim lại cùng (date,ticker,tier) ⇒ rc=0, không tiêu thêm
        won = [t for t, rc in zip(("m1", "m2", "m3"), rcs) if rc == 0][0]
        rc, msg = P.claim(won, "full", dt.date(2027, 1, 12), base, gate=gate(tmp, "RUN"))
        ok(rc == 0 and "đã claim" in msg, f"claim lại cùng bộ ba ⇒ rc=0 ({msg})")
        ok(sum(1 for _ in open(P.pick_paths(base)["ledger"])) == 1, "claim lại không ghi thêm")
        ok(P.claim("m9", "full", dt.date(2027, 1, 12), base, gate=gate(tmp, "RUN"))[0] == 2,
           "claim lại không làm hở suất cho mã khác")
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        with ctx.Pool(2) as pool:                            # 2 run_pick song song cùng asof
            res = pool.map(_w_pick, [(tmp, base, ex, rd)] * 2)
        log = pd.read_csv(P.pick_paths(base)["log"], dtype={"asof": str})
        ok(sorted(r[0] for r in res) == [False, True], f"1 run chấm + 1 run đọc lại: {res}")
        ok(len(set(r[1] for r in res)) == 1, "2 run cùng 1 picked")
        ok(log["asof"].nunique() == 1 and len(log) >= 5, f"1 bộ top-K, {len(log)} dòng")
        ok(int(log["picked"].astype(str).str.lower().isin(["true", "1"]).sum()) == 1, "đúng 1 picked trong log")
        ok(log["logged_at"].nunique() == 1, "1 lô ghi")
        # khử trùng theo asof khi log đã có 2 lô (hỏng cũ): giữ lô đầu
        lp = P.pick_paths(base)["log"]
        dup = pd.read_csv(lp, dtype={"asof": str, "ticker": str})
        dup["logged_at"] = "2099-01-01T00:00:00+07:00"
        dup["picked"] = False
        dup.to_csv(lp, mode="a", header=False, index=False)
        rd2 = P.read_pick_log(lp)
        ok(len(rd2) == len(log) and rd2["picked"].astype(str).str.lower().eq("true").sum() == 1,
           "read_pick_log khử trùng theo asof, giữ lô đầu")
        # append CSV = MỘT lần ghi, dòng cuối kết thúc bằng \n
        ok(open(lp, "rb").read().endswith(b"\n"), "log kết thúc bằng newline")


def t_price_date_and_timeout():
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        seen = {}

        def live(t, p, pdt=None):
            seen["pdt"] = pdt
            return {"ok": True, "margin_of_safety": 0.9}
        MOS["AAA"] = 0.95
        try:
            prices = {t: (10000.0, dt.date(2026, 10, 29)) for t in rating_df()["ticker"]}   # giá T-1
            cands = pd.DataFrame({"ticker": ["CCC"], "lane": ["A"]})
            P.run_pick(rating_df(), fin_df(), cands, {"BAN"}, {"FOR": "x"}, {"INS": "y"}, ASOF, base_dir=base,
                       write=False, now=NOW, exec_dir=ex, research_dir=rd, gate=gate(tmp, "RUN"),
                       dcf_fn=dcf_fn, live_fn=live, prices=prices)
            ok(seen.get("pdt") == "2026-10-29", f"live nhận price_date=phiên thật T-1, không phải asof: {seen}")
            # trần thời gian: live treo ⇒ fail-soft, nhãn rõ, cảnh báo, không ném
            old = P.LIVE_DEADLINE_S
            P.LIVE_DEADLINE_S = 0.2
            try:
                t0 = time.time()
                r = P.run_pick(rating_df(), fin_df(), cands, {"BAN"}, {"FOR": "x"}, {"INS": "y"}, ASOF,
                               base_dir=base, write=False, now=NOW, exec_dir=ex, research_dir=rd,
                               gate=gate(tmp, "RUN"), dcf_fn=dcf_fn,
                               live_fn=lambda t, p, pdt=None: time.sleep(5), prices=prices)
                ok(time.time() - t0 < 3, "live treo bị cắt theo trần")
            finally:
                P.LIVE_DEADLINE_S = old
            ok(r["picked"]["escalate_full"] is False, "live timeout ⇒ không escalate")
            ok("live_timeout" in r["picked"]["labels"] and any("quá trần" in w for w in r["warnings"]),
               f"timeout ⇒ nhãn + cảnh báo: {r['picked']['labels']}")
        finally:
            MOS["AAA"] = 0.50
    D = P._dcf_engine()
    import inspect
    ok("price_date" in inspect.signature(D.fair_value).parameters, "dcf_valuation.fair_value còn tham số price_date")


def t_fin_none():
    """fin=None ⇒ không BCTC mới ⇒ E=0 cho mọi mã, không ném (nhánh NaT)."""
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        prices = {t: (10000.0, ASOF) for t in rating_df()["ticker"]}
        r = P.run_pick(rating_df(), None, pd.DataFrame({"ticker": [], "lane": []}), {"BAN"}, {}, {}, ASOF,
                       base_dir=base, write=False, now=NOW, exec_dir=ex, research_dir=rd,
                       gate=gate(tmp, "RUN"), dcf_fn=dcf_fn, prices=prices)
        ok(len(r["top"]) > 0 and all(x["E"] == 0.0 for x in r["top"]), "fin=None ⇒ E=0, vẫn chọn được theo V+R")
        ok(all("bctc_moi" not in x["labels"] for x in r["top"]), "fin=None ⇒ không nhãn bctc_moi")


def t_recent_names_and_topic():
    with tempfile.TemporaryDirectory() as tmp:
        rd = os.path.join(tmp, "r")
        for n in ("dd_blind2_BBB_20261015", "dd_CCC_reweight_20261016", "dd_AAA_20260601", "dd_HPG_20261020"):
            os.makedirs(os.path.join(rd, n))
        got = P.recent_dd(ASOF, pd.DataFrame(columns=P.LOG_COLS), [], rd, kb_dir=_KB_EMPTY)
        ok(got == {"BBB", "CCC", "HPG"}, f"recent_dd bắt cả blind2/reweight (fallback 120d): {got}")
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        line = P.topic_line(run(tmp, base, ex, rd), ASOF, base, gate(tmp, "RUN"))
        ok("top-1 lịch sử KÉM rank 2-8" in line and "MoS DCF" in line, "cảnh báo top-1 kém cạnh MoS")
        ok("KHÔNG phải tín hiệu mua" in line and "không edge" in line and "ĐỀ XUẤT lên DD đầy đủ" not in line,
           f"nhãn cố định: {line[:200]}")
        # replay giữ warnings
        run(tmp, base, ex, rd)
        os.remove(os.path.join(ex, "active_nav_SpaceX.json"))
        r3 = run(tmp, base, ex, rd)
        ok(r3["replayed"] and any("không đọc được" in w for w in r3["warnings"]), "replay vẫn mang cảnh báo nguồn")


def t_dd_skip_after_bctc():
    """User 2026-11-01: DD (picker HOẶC user chỉ định) có ngày ≥ ngày BCTC quý mới nhất ⇒ loại; BCTC mới
    công bố SAU DD ⇒ quay lại; user-source không trừ suất."""
    asof, run_day = dt.date(2026, 10, 30), dt.date(2026, 11, 2)
    empty = pd.DataFrame(columns=P.LOG_COLS)
    with tempfile.TemporaryDirectory() as tmp:
        rd, kb = os.path.join(tmp, "r"), os.path.join(tmp, "kb")
        os.makedirs(kb)
        for n in ("dd_HHS_20261101", "dd_TV2_20261101", "dd_SIP_20261101", "dd_FPT_20261101",
                  "dd_OLD_20260901", "dd_NRL_20260801", "dd_NRM_20260620"):
            os.makedirs(os.path.join(rd, n))
        open(os.path.join(kb, "scl-dd-research-20261101.md"), "w").close()
        open(os.path.join(kb, "mbb-dd-20261031.md"), "w").close()
        rel = {t: pd.Timestamp("2026-10-25") for t in ("HHS", "TV2", "SIP", "FPT", "SCL", "MBB")}
        rel["OLD"] = pd.Timestamp("2026-10-20")      # BCTC mới (10-20) công bố SAU DD 09-01 ⇒ quay lại
        # (NRL, NRM không có Release_Date ⇒ fallback 120 ngày)
        got = P.recent_dd(asof, empty, [], rd, upto=run_day, release=rel, kb_dir=kb)
        ok({"HHS", "TV2", "SIP", "FPT"} <= got, f"(a) 4 mã DD user 01/11 bị loại: {got}")
        ok({"SCL", "MBB"} <= got, f"(a) DD nhận diện qua kb/projects/*-dd-*: {got}")
        ok("OLD" not in got, f"(b) BCTC mới sau DD ⇒ quay lại pool: {got}")
        ok("NRL" in got and "NRM" not in got, f"fallback 120d: NRL(91d) loại, NRM(132d) không: {got}")
        # DD cùng ngày công bố BCTC: tính là SAU BCTC (>=)
        rel2 = dict(rel, HHS=pd.Timestamp("2026-11-01"))
        ok("HHS" in P.recent_dd(asof, empty, [], rd, upto=run_day, release=rel2, kb_dir=kb), "DD cùng ngày BCTC ⇒ loại")
        # BCTC mới ra SAU DD (02/11 > DD 01/11) ⇒ quay lại. upto=11-02 để thấy được release (known ≤ run)
        rel3 = dict(rel, HHS=pd.Timestamp("2026-11-02"))
        ok("HHS" not in P.recent_dd(asof, empty, [], rd, upto=run_day, release=rel3, kb_dir=kb),
           "(b) BCTC công bố 02/11 sau DD 01/11 ⇒ quay lại")
        # picked 10-01 → DD user 10-02 → BCTC 10-25: luật BCTC thắng cooldown 90d (addendum §3) ⇒ QUAY LẠI
        lg2 = pd.DataFrame([{"asof": "2026-10-01", "ticker": "PBD", "picked": True}])
        os.makedirs(os.path.join(rd, "dd_PBD_20261002"))
        got3 = P.recent_dd(asof, lg2, [], rd, upto=run_day, release={"PBD": pd.Timestamp("2026-10-25")}, kb_dir=kb)
        ok("PBD" not in got3, f"picked→DD→BCTC mới ⇒ quay lại pool (không bị cooldown 90d): {got3}")
        got3b = P.recent_dd(asof, lg2, [], rd, upto=run_day, release={"PBD": pd.Timestamp("2026-09-20")}, kb_dir=kb)
        ok("PBD" in got3b, "picked→DD sau BCTC ⇒ vẫn loại")
        # claim trong sổ cũng là DD; pick-only vẫn cooldown 90d
        led = [{"date": "2026-10-28", "ticker": "LED", "tier": "light"}]
        lg = pd.DataFrame([{"asof": "2026-10-10", "ticker": "PKD", "picked": True},
                           {"asof": "2026-06-01", "ticker": "PKO", "picked": True}])
        got2 = P.recent_dd(asof, lg, led, rd, upto=run_day, release={"LED": pd.Timestamp("2026-10-25")}, kb_dir=kb)
        ok("LED" in got2 and "PKD" in got2 and "PKO" not in got2, f"claim=DD; pick-only 90d: {got2}")
        ok("LED" not in P.recent_dd(asof, empty, led, rd, upto=run_day,
                                    release={"LED": pd.Timestamp("2026-10-29")}, kb_dir=kb), "claim trước BCTC ⇒ quay lại")
    # (c) source=user không trừ suất; picker vẫn bị trần
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "d")
        os.makedirs(base)
        g = gate(tmp, "SKIP")
        d0 = dt.date(2026, 12, 1)                     # ngoài mùa: full 2/tuần
        for tk in ("HHS", "TV2", "SIP", "FPT"):
            rc, msg = P.claim(tk, "full", d0, base, gate=g, source="user")
            ok(rc == 0 and "KHÔNG trừ suất" in msg, f"user claim {tk}: {msg}")
        ok(P.claim("p1", "full", d0, base, gate=g)[0] == 0, "(c) sau 4 DD user, picker vẫn còn đủ suất #1")
        ok(P.claim("p2", "full", d0, base, gate=g)[0] == 0, "(c) picker #2")
        ok(P.claim("p3", "full", d0, base, gate=g)[0] == 2, "picker #3 vẫn bị trần 2/tuần")
        ok(P.claim("ZZZ", "full", d0, base, gate=g, source="user")[0] == 0, "user claim vẫn ghi được khi suất picker ĐÃ HẾT")
        ok("đầy đủ đã dùng tuần này 2" in P.slots_line(d0, base, g), "slots_line không đếm user")
        ok("+5 do user chỉ định" in P.slots_line(d0, base, g), f"slots_line nêu số user: {P.slots_line(d0, base, g)}")
        ok(P.claim("x", "full", d0, base, gate=g, source="bogus")[0] == 2, "source sai ⇒ rc=2")
        recs = P.read_ledger(P.pick_paths(base)["ledger"])
        ok(sum(r.get("source") == "user" for r in recs) == 5 and all("source" in r for r in recs), "sổ ghi source")
    # bản ghi KIỂU CŨ (không có trường source) PHẢI tính vào trần picker (bắt mutant default source→"user")
    with tempfile.TemporaryDirectory() as tmp:
        base = os.path.join(tmp, "d")
        os.makedirs(base)
        g = gate(tmp, "SKIP")
        d0 = dt.date(2026, 12, 1)
        with open(P.pick_paths(base)["ledger"], "w") as f:
            for tk in ("OLD1", "OLD2"):
                f.write(json.dumps({"date": str(d0), "ticker": tk, "tier": "full", "season": False,
                                    "by": "", "job": "", "at": "x"}) + "\n")
        rc, msg = P.claim("NEW1", "full", d0, base, gate=g)
        ok(rc == 2 and "HẾT SUẤT" in msg, f"2 bản ghi cũ không source tính vào trần picker: {rc} {msg}")
        ok("đầy đủ đã dùng tuần này 2" in P.slots_line(d0, base, g), "slots_line đếm bản ghi cũ")
        # --source user bắt buộc --by
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            rc1 = P.main(["--claim", "XYZ", "--tier", "light", "--source", "user", "--out-dir", base])
        ok(rc1 == 2 and not any(r["ticker"] == "XYZ" for r in P.read_ledger(P.pick_paths(base)["ledger"])),
           "--source user thiếu --by ⇒ rc=2, không ghi")
    # tích hợp: run_pick dùng release=fin.known ⇒ REC (DD 10-25 sau BCTC 10-20) loại, AAA (DD 06-01) ở lại
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        r = run(tmp, base, ex, rd, write=False)
        tk = [x["ticker"] for x in r["top"]]
        ok("REC" not in tk and "AAA" in tk, f"tích hợp run_pick: {tk}")
        ok("REC" in r["dropped_held_or_recent"], "REC nằm trong dropped_held_or_recent")
    # M6: mã NEW có DD 09-01 (TRƯỚC BCTC 10-20, nhưng TRONG 120d fallback ⇒ nếu không dùng release sẽ bị loại) —
    # chỉ quay lại pool nếu nhánh release=fin.known thật sự được dùng trong _run_pick
    with tempfile.TemporaryDirectory() as tmp:
        ex, rd, base = setup(tmp)
        os.makedirs(os.path.join(rd, "dd_NEW_20260901"))
        rt = rating_df()
        rt = pd.concat([rt, rt[rt["ticker"] == "AAA"].assign(ticker="NEW")], ignore_index=True)
        fn = fin_df()
        fn.loc["NEW"] = fn.loc["AAA"]
        MOS["NEW"] = 0.50
        try:
            prices = {t: (10000.0, ASOF) for t in rt["ticker"]}
            cands = pd.DataFrame({"ticker": ["CCC"], "lane": ["A"]})
            r = P.run_pick(rt, fn, cands, {"BAN"}, {"FOR": "x"}, {"INS": "y"}, ASOF, base_dir=base, write=False,
                           now=NOW, exec_dir=ex, research_dir=rd, gate=gate(tmp, "RUN"), dcf_fn=dcf_fn,
                           prices=prices, kb_dir=_KB_EMPTY)
        finally:
            MOS.pop("NEW", None)
        ok("NEW" not in r["dropped_held_or_recent"],
           f"M6: DD 09-01 < BCTC 10-20 ⇒ NEW quay lại pool qua fin.known: dropped={r['dropped_held_or_recent']}")


def t_robust_gate():
    """PREREG §5: escalate_full cần robust (MoS giữ dấu ở cả 4 điểm nhạy). MoS 95% nhưng 1 điểm nhạy
    fv < giá ⇒ KHÔNG robust ⇒ không escalate. Bắt mutant M9 (bỏ `& df['robust']`)."""
    def dcf_nonrobust(t, p):
        r = dcf_fn(t, p)
        if t == "AAA" and r.get("ok"):
            k0 = sorted(P._dcf_engine()._SENS_KEYS)[0]
            r["sensitivity"][k0] = {"fv": p * 0.9}          # fv < giá ⇒ dấu MoS đảo ở 1 điểm
        return r
    MOS["AAA"] = 0.95
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ex, rd, base = setup(tmp)
            c = run(tmp, base, ex, rd, write=False)
            ok(c["picked"]["ticker"] == "AAA" and c["picked"]["escalate_full"] is True, "control: AAA robust ⇒ escalate")
        with tempfile.TemporaryDirectory() as tmp:
            ex, rd, base = setup(tmp)
            r = run(tmp, base, ex, rd, write=False, dcf=dcf_nonrobust)
            ok(r["picked"]["ticker"] == "AAA" and r["picked"]["mos"] >= P.ESCALATE_MOS, "AAA vẫn top, MoS≥25%")
            ok(r["picked"]["escalate_full"] is False, "MoS cao nhưng KHÔNG robust ⇒ không escalate")
    finally:
        MOS["AAA"] = 0.50


def t_held_missing():
    with tempfile.TemporaryDirectory() as tmp:
        h, e, w = P.held_and_excluded(os.path.join(tmp, "nope"))
        ok(not h and len(w) == 2, "thiếu active_nav ⇒ 2 cảnh báo")


if __name__ == "__main__":
    for fn in (t_scoring, t_append_only_replay, t_offseason_week, t_claims, t_live_downgrade_and_topic,
               t_held_missing, t_dd_after_asof, t_concurrency, t_price_date_and_timeout, t_fin_none,
               t_recent_names_and_topic, t_dd_skip_after_bctc, t_robust_gate):
        fn()
    print(f"TZ={os.environ.get('TZ', '<unset>')} checks={N[0]} fails={len(FAILS)}")
    sys.exit(1 if FAILS else 0)
