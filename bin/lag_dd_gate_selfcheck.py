#!/usr/bin/env python3
"""Selfcheck cổng DD LAG: lag_dd_pack.py + lag_dd_ack.py + nhánh LAG_DD_GATE_VIOLATION của
lag_plan_consistency_check.py. Thuần offline (nguồn dữ liệu giả, không BQ/Discord/bus).

Chạy lại chính nó dưới `env -u TZ` và 2 TZ lạ (§16/§19), rồi chạy MUTANT (phá logic cờ /
fail-closed / ack / cổng) — mỗi mutant PHẢI làm selfcheck đỏ.

    python3 bin/lag_dd_gate_selfcheck.py            # đủ: 3 TZ + mutants
    python3 bin/lag_dd_gate_selfcheck.py --inner    # 1 lượt
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


def write_exec(p, body):
    with open(p, "w") as fh:
        fh.write(body)
    os.chmod(p, 0o755)


# ── nguồn giả ────────────────────────────────────────────────────────────────────────────────
def fin_row(**kw):
    r = {"ticker": "AAA", "quarter": "2026Q3", "Release_Date": "2026-10-19", "time": "2026-10-19",
         "NP_R": 0.3, "Revenue_P0": 130.0, "Revenue_P4": 100.0, "NPM_P0": 0.08, "EBITM_P0": 0.10,
         "AR_P0": 110.0, "Inventory_P0": 105.0, "Inventory_P4": 100.0,
         "DSO_P0": 30.0, "DSO_P4": 30.0, "DIO_P0": 40.0, "DIO_P4": 40.0}
    for i, v in enumerate([13, 12, 11, 10, 10, 9, 9, 8]):
        r[f"NP_P{i}"] = float(v)
    for i, v in enumerate([14, 13, 12, 11]):
        r[f"CF_OA_P{i}"] = float(v)
    r.update(kw)
    return r


def fin_rows(**kw):
    yago = {"ticker": "AAA", "quarter": "2025Q3", "AR_P0": 100.0, "Inventory_P0": 100.0}
    return [fin_row(**kw), {"quarter": "2026Q2"}, {"quarter": "2026Q1"}, {"quarter": "2025Q4"}, yago]


def dd_ok(**kw):
    d = {"dd": {"in_universe": True, "quality_flag": "QUALITY_OK", "red_flags": [], "liquidity": "OK",
                "upcoming_exdate": None, "insider_net_sell": None,
                "yield_floor": {"icb_code": 2353}},
         "adv": 5e9, "adv_date": "2026-10-20", "adv_err": None, "adv_thin_vnd": 2e9,
         "insider_ok": True, "corp_ok": True, "anomaly_ok": True, "anomaly_rec": None, "anomaly_err": None}
    for k, v in kw.items():
        if k in d["dd"]:
            d["dd"][k] = v
        else:
            d[k] = v
    return d


def sources(fin=None, dd=None, val=None, rating=None, forensic=None):
    return {
        "fin": (lambda t, a: fin) if not callable(fin) else fin,
        "dd": (lambda t, a: dd) if not callable(dd) else dd,
        "valuation": (lambda t, a: val) if not callable(val) else val,
        "rating": (lambda t, a, r: rating) if not callable(rating) else rating,
        "forensic": (lambda t, a: forensic) if not callable(forensic) else forensic,
        "bank": lambda t: {"note": "fake"},
        "macro": lambda p: {"path": p, "status": "fake"},
    }


GOOD = dict(fin=fin_rows(), dd=dd_ok(),
            val=({"status": "CHEAP", "robust": True}, "🟢 DCF CHEAP", "", None),
            rating={"err": None, "fail": None, "stale": None},
            forensic={"dropped": [], "rows": [], "err": None})


def boom(*a):
    raise RuntimeError("nguồn hỏng giả")


def codes(p):
    return sorted({f["code"] for f in p["flags"]})


def run_inner():
    import lag_dd_pack as P
    import lag_dd_ack as K
    import lag_plan_consistency_check as C
    td = tempfile.mkdtemp()
    os.environ["MIKE_LAG_DD_DIR"] = td
    os.environ["MIKE_LAG_DD_STATE_DIR"] = os.path.join(td, "st")
    try:
        B = lambda **kw: P.build_pack("AAA", "2026-10-21", cand={"entry_date": "2026-10-26"},  # noqa: E731
                                      sources=sources(**dict(GOOD, **kw)))
        # 1. sạch ⇒ CLEARED
        p = B()
        ck("bằng chứng sạch ⇒ CLEARED, 0 cờ", p["status"] == "CLEARED" and p["flags"] == [], codes(p))
        ck("release lấy từ Release_Date dòng mới nhất", p["release_date"] == "2026-10-19", p["release_date"])

        # 2. fail-closed: mỗi nguồn hỏng ⇒ cờ *_NA ⇒ FLAG
        cases = [
            ("ticker_financial raise", dict(fin=boom), "FIN_NA"),
            ("ticker_financial rỗng", dict(fin=[]), "RELEASE_NA"),
            ("release cũ > 60 ngày", dict(fin=fin_rows(Release_Date="2026-07-01")), "RELEASE_NA"),
            ("run_dd raise", dict(dd=boom), "DD_KHONG_CHAY_DUOC"),
            ("insider không đọc được", dict(dd=dd_ok(insider_ok=False)), "INSIDER_NA"),
            ("feed corp-action cũ", dict(dd=dd_ok(corp_ok=False)), "CORP_FEED_NA"),
            ("anomaly_flags.json hỏng", dict(dd=dd_ok(anomaly_ok=False, anomaly_err="x")), "ANOMALY_NA"),
            ("ADV None", dict(dd=dd_ok(adv=None, adv_err="thiếu Volume")), "ADV_NA"),
            ("universe None", dict(dd=dd_ok(in_universe=None)), "UNIVERSE_NA"),
            ("rating raise", dict(rating=boom), "RATING_NA"),
            ("rating lỗi truy vấn", dict(rating={"err": "BQ 500"}), "RATING_NA"),
            ("forensic raise", dict(forensic=boom), "FORENSIC_NA"),
            ("forensic CSV hỏng", dict(forensic={"dropped": [], "rows": [], "err": "csv"}), "FORENSIC_NA"),
            ("định giá raise", dict(val=boom), "DINH_GIA_NA"),
            ("DCF NOT_COMPUTED + không lens", dict(val=({"status": "NOT_COMPUTED"}, "", "", None)), "DINH_GIA_NA"),
            ("thiếu CF_OA_P0", dict(fin=fin_rows(CF_OA_P0=None)), "FIN_NA"),
            ("thiếu NP_P4", dict(fin=fin_rows(NP_P4=float("nan"))), "FIN_NA"),
            ("EBITM/AR/Inventory = 0 mà không phải NH", dict(fin=fin_rows(EBITM_P0=0, AR_P0=0, Inventory_P0=0)), "FIN_NA"),
        ]
        for name, kw, code in cases:
            p = B(**kw)
            ck(f"fail-closed: {name} ⇒ {code}, FLAG", p["status"] == "FLAG" and code in codes(p), codes(p))

        # 3. cờ cơ học
        cases = [
            ("DD red flag NGOAI_UNIVERSE", dict(dd=dd_ok(red_flags=["NGOAI_UNIVERSE"])), "NGOAI_UNIVERSE"),
            ("DD red flag mã lạ", dict(dd=dd_ok(red_flags=["XYZ_MOI"])), "DD_KHONG_CHAY_DUOC"),
            ("ADV 1,5 tỷ", dict(dd=dd_ok(adv=1.5e9)), "THANH_KHOAN_MONG"),
            ("quality_flag", dict(dd=dd_ok(quality_flag="Q_THIN")), "CO_CHAT_LUONG_UNIVERSE"),
            ("anomaly", dict(dd=dd_ok(anomaly_rec={"tier": "H", "reasons": "IDIOCRASH"})), "BAT_THUONG_ANOMALY"),
            ("insider bán ròng", dict(dd=dd_ok(insider_net_sell={"net_sell_pct": 0.02})), "INSIDER_BAN_RONG"),
            ("ex-date", dict(dd=dd_ok(upcoming_exdate={"exright_date": "2026-11-01"})), "EXDATE_SAP_TOI"),
            ("rating ≥4", dict(rating={"err": None, "fail": {"reason": "RATING_FAIL 8L=5"}, "stale": None}), "RATING_8L_FAIL"),
            ("rating cũ", dict(rating={"err": None, "fail": None, "stale": {"rating": 3}}), "RATING_8L_CU"),
            ("forensic exclude", dict(forensic={"dropped": [{"kind": "banned"}], "rows": [], "err": None}), "FORENSIC_BANNED"),
            ("forensic watch", dict(forensic={"dropped": [], "rows": [{"flag_type": "related_party", "severity": "watch"}], "err": None}), "FORENSIC_WATCH"),
            ("DCF RICH", dict(val=({"status": "RICH"}, "🔴 DCF RICH", "", None)), "DCF_RICH"),
            ("nền cùng kỳ thấp", dict(fin=fin_rows(NP_P4=3.0)), "EQ_NEN_THAP"),
            ("quý lỗ trong nền", dict(fin=fin_rows(NP_P2=-1.0)), "QUY_LO_TRONG_NEN"),
            ("CFO yếu", dict(fin=fin_rows(CF_OA_P0=0.0, CF_OA_P1=0.0, CF_OA_P2=1.0, CF_OA_P3=1.0)), "EQ_CFO_YEU"),
            ("NPM > EBITM", dict(fin=fin_rows(NPM_P0=0.2, EBITM_P0=0.1)), "EQ_NGOAI_HOAT_DONG"),
            ("phải thu tăng nhanh", dict(fin=fin_rows(AR_P0=200.0)), "EQ_PHAI_THU_TANG"),
            ("tồn kho tăng nhanh", dict(fin=fin_rows(Inventory_P0=200.0)), "EQ_TON_KHO_TANG"),
        ]
        for name, kw, code in cases:
            p = B(**kw)
            ck(f"cờ: {name} ⇒ {code}", p["status"] == "FLAG" and code in codes(p), codes(p))
        p = B(forensic={"dropped": [], "rows": [{"flag_type": "fraud_confirmed", "severity": "exclude"}], "err": None})
        w = [f for f in p["flags"] if f["code"] == "PHAP_LY_WARNING"]
        ck("pháp lý ⇒ WARNING tường minh, vẫn status FLAG", w and w[0]["severity"] == "WARNING" and p["status"] == "FLAG",
           p["flags"])
        p = B(fin=fin_rows(NP_P4=-1.0), dd=dd_ok(red_flags=["SURPRISE_PHONG_CO_HOC"]))
        ck("nền âm: SURPRISE_PHONG_CO_HOC, không nhân đôi QUY_LO_TRONG_NEN",
           "SURPRISE_PHONG_CO_HOC" in codes(p) and "QUY_LO_TRONG_NEN" not in codes(p), codes(p))
        bank = dict(dd=dd_ok(yield_floor={"icb_code": 8355}),
                    fin=fin_rows(EBITM_P0=0, AR_P0=0, Inventory_P0=0, CF_OA_P0=-99.0),
                    val=({"status": "NOT_COMPUTED"}, "", "🟢 Gordon P/B", None))
        p = B(**bank)
        ck("ngân hàng: CFO/vốn lưu động không áp dụng, không cờ giả ⇒ CLEARED", p["status"] == "CLEARED",
           codes(p))
        ck("ngân hàng: có mục bank (thông tin)", "bank" in p["earnings_quality"], p["earnings_quality"].keys())
        ck("thiếu dữ liệu ghi 'không đủ dữ liệu', không đoán 0",
           B(fin=[fin_row(AR_P0=None)])["earnings_quality"]["working_capital"]["receivables"] == "không đủ dữ liệu")
        h1, h2 = B(dd=dd_ok(adv=1.5e9))["flags_hash"], B(dd=dd_ok(adv=1.2e9))["flags_hash"]
        ck("flags_hash theo MÃ cờ, không theo số bằng chứng", h1 == h2 and h1 != B()["flags_hash"])

        # 4. ghi gói + ack
        cleared, flagged = B(), B(dd=dd_ok(adv=1.5e9))
        P.write_atomic(P.pack_path("HT1", "2026-10-19"), dict(cleared, ticker="HT1"))
        P.write_atomic(P.pack_path("SCL", "2026-10-19"), dict(flagged, ticker="SCL"))
        P.write_atomic(P.pack_path("OLD", "2026-08-01"), dict(cleared, ticker="OLD", release_date="2026-08-01"))
        G = lambda t: K.dd_gate(t, "2026-10-26")["state"]     # noqa: E731
        ck("gate: CLEARED", G("HT1") == "CLEARED", G("HT1"))
        ck("gate: FLAG chưa ack ⇒ FLAG_NO_ACK", G("SCL") == "FLAG_NO_ACK", G("SCL"))
        ck("gate: không có gói ⇒ NO_PACK", G("ZZZ") == "NO_PACK")
        ck("gate: gói release > 30 ngày ⇒ NO_PACK", G("OLD") == "NO_PACK", G("OLD"))
        ck("gate: release SAU plan_date ⇒ NO_PACK", K.dd_gate("HT1", "2026-10-18")["state"] == "NO_PACK")
        bad = [
            dict(decided_by="mike"), dict(decision="MAYBE"), dict(at="2026-10-25T18:30:00"),
            dict(ticker="ZZZ"), dict(release_date="2026-10-20"),
        ]
        base = dict(ticker="SCL", release_date="2026-10-19", decision="PROCEED", decided_by="user",
                    at="2026-10-25T18:30:00+07:00")
        for b in bad:
            try:
                K.record(**dict(base, **b))
                ok = False
            except ValueError:
                ok = True
            ck(f"ack từ chối {b}", ok)
        ck("ack hỏng không ghi gì", not os.path.exists(K.ack_path()))
        K.record(**dict(base, decision="RESEARCH"))
        ck("gate: ack RESEARCH ⇒ không được mua", G("SCL") == "ACK_RESEARCH", G("SCL"))
        K.record(**base)
        ck("gate: ack PROCEED mới nhất thắng ⇒ ACK_PROCEED", G("SCL") == "ACK_PROCEED", G("SCL"))
        P.write_atomic(P.pack_path("SCL", "2026-10-19"),
                       dict(B(dd=dd_ok(adv=1.5e9, anomaly_rec={"tier": "H"})), ticker="SCL"))
        ck("gate: gói sinh lại ra BỘ CỜ KHÁC ⇒ ack cũ ACK_STALE", G("SCL") == "ACK_STALE", G("SCL"))
        acks = json.load(open(K.ack_path()))["acks"]
        acks.append(dict(acks[-1], decided_by="agent"))
        P.write_atomic(K.ack_path(), {"acks": acks})
        ck("gate: ack decided_by≠user ⇒ ACK_NOT_USER", G("SCL") == "ACK_NOT_USER", G("SCL"))
        open(K.ack_path(), "w").write("{hỏng")
        ck("gate: ack.json hỏng ⇒ ACK_UNREADABLE (không mua)", G("SCL") == "ACK_UNREADABLE", G("SCL"))
        os.remove(K.ack_path())
        open(P.pack_path("BAD", "2026-10-19"), "w").write("{")
        ck("gate: gói hỏng ⇒ PACK_UNREADABLE", G("BAD") == "PACK_UNREADABLE", G("BAD"))
        P.write_atomic(P.pack_path("LIE", "2026-10-19"), dict(flagged, ticker="LIE", status="CLEARED"))
        ck("gate: status CLEARED mà có cờ ⇒ KHÔNG coi là CLEARED", G("LIE") == "FLAG_NO_ACK", G("LIE"))

        # 5. checker: LAG_DD_GATE_VIOLATION + chờ DD
        def plan(orders, due, upc=()):
            return {"account": "SpaceX", "plan_date": "2026-10-26", "orders": orders,
                    "lag_analysis": {"due_today": list(due), "lag_upcoming_for_next_plans": list(upc)}}

        def o(t, book="LAG", qty=100, side="buy"):
            return {"ticker": t, "side": side, "qty": qty, "book": book}

        def due(t, decision="BUY"):
            return {"ticker": t, "decision": decision, "entry_window_day": 1, "entry_date": "2026-10-26"}

        A = lambda p: C.analyze(p, crosscheck=False)            # noqa: E731
        V = lambda r: sorted((f["ticker"], f["cause"]) for f in r["findings"]   # noqa: E731
                             if f["kind"] == "LAG_DD_GATE_VIOLATION")
        r = A(plan([o("HT1")], [due("HT1")]))
        ck("checker: lệnh LAG mã CLEARED ⇒ không vi phạm", V(r) == [], V(r))
        r = A(plan([o("HT1"), o("SCL")], [due("HT1"), due("SCL")]))
        ck("checker: lệnh LAG mã FLAG chưa ack ⇒ LAG_DD_FLAG_NO_ACK", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        r = A(plan([o("SCL", book="")], [due("SCL")]))
        ck("checker: thiếu book nhưng due_today BUY ⇒ vẫn bị cổng", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        r = A(plan([o("SCL", book="BAL")], []))
        ck("checker: lệnh BAL không bị cổng DD LAG", V(r) == [], V(r))
        r = A(plan([o("SCL", qty=0), o("SCL", side="sell")], [due("SCL", "SKIP")]))
        ck("checker: qty 0 / lệnh bán không bị cổng", V(r) == [], V(r))
        r = A({"account": "SpaceX", "plan_date": "2026-10-26", "orders": [o("ZZZ")]})
        ck("checker: thiếu lag_analysis vẫn bắt lệnh LAG không có gói", V(r) == [("ZZZ", "LAG_DD_NO_PACK")], V(r))
        r = A(plan([o("HT1")], [due("HT1"), due("SCL", "SKIP")], [{"ticker": "ZZZ"}]))
        pend = sorted((x["ticker"], x["state"]) for x in r["dd_pending"])
        ck("checker: mã FLAG ngoài plan ⇒ dòng chờ DD (cả upcoming)",
           pend == [("SCL", "FLAG_NO_ACK"), ("ZZZ", "NO_PACK")] and V(r) == [], pend)
        txt = "\n".join(C.render(r))
        ck("checker: render có '⏳ Chờ DD' khi chỉ có pending", "Chờ DD" in txt and "SCL" in txt, txt)
        r = A(plan([o("SCL")], [due("SCL")]))
        ck("checker: render vi phạm ĐỎ", "CHƯA QUA CỔNG DD" in "\n".join(C.render(r)))
        ck("checker: tin Discord (pending=False) không chứa dòng chờ DD",
           "Chờ DD" not in "\n".join(C.render(dict(r, dd_pending=[{"ticker": "X", "source": "s", "state": "s",
                                                                  "evidence": ""}]), pending=False)))
        K.record(**base)       # ack cho bộ cờ hiện tại của SCL
        r = A(plan([o("SCL")], [due("SCL")]))
        ck("checker: ack PROCEED (user, khớp hash) ⇒ được mua", V(r) == [], V(r))
        r = C.analyze(plan([o("ZZZ")], []), crosscheck=False, dd_gate=False)
        ck("checker: --no-dd-gate tắt cổng", V(r) == [])

        # 6. notify idempotent, chỉ ghi state sau khi gửi xong
        nlog = os.path.join(td, "n.log")
        nf = os.path.join(td, "n.sh")
        write_exec(nf, f'#!/bin/bash\necho "$2|$1" >> {nlog}\nexit ${{FAKE_NOTIFY_RC:-0}}\n')
        os.environ["MIKE_LAG_DD_NOTIFY"] = nf
        pk = [dict(cleared, ticker="HT1"), dict(flagged, ticker="SCL")]
        lines = lambda: open(nlog).read().count("plan_approval|") if os.path.exists(nlog) else 0  # noqa: E731
        n0, msg0 = P.notify(pk, dry_run=True)
        ck("notify dry-run: không gửi, không ghi state", n0 == 2 and lines() == 0
           and not os.path.exists(P._state_path()) and "(3) mua dù có cờ" in msg0)
        os.environ["FAKE_NOTIFY_RC"] = "5"
        n1, _ = P.notify(pk)
        ck("notify lỗi ⇒ -1, CHƯA ghi state", n1 == -1 and not os.path.exists(P._state_path()), n1)
        os.environ.pop("FAKE_NOTIFY_RC")
        n2, _ = P.notify(pk)
        n3, _ = P.notify(pk)
        ck("notify: gửi 1 lần vào plan_approval, lần 2 không gửi lại", (n2, n3) == (2, 0) and lines() == 2, (n2, n3))
        n4, m4 = P.notify([dict(flagged, ticker="SCL", flags=flagged["flags"] + [P._f("DCF_RICH", "x")],
                                flags_hash="khac")] + pk)
        ck("notify: bộ cờ đổi ⇒ gửi lại đúng mã đó", n4 == 1 and "SCL" in m4 and "HT1" not in m4, (n4, m4))
        ck("tin có hạn trả lời 19:00 CN trước phiên thứ Hai + mốc T6 ngoài mùa", "19:00 ICT CN 2026-10-25" in m4 and "19:00 T6 2026-10-23" in m4, m4)
        ck("hạn trả lời ngày thường = 19:00 hôm trước", "19:00 ICT 2026-10-27" in P._deadline("2026-10-28"))
    finally:
        shutil.rmtree(td, ignore_errors=True)
    n_fail = RESULTS.count(False)
    print(f"CASES: {RESULTS.count(True)} pass / {n_fail} fail")
    print("RESULT:", "PASS" if not n_fail else "FAIL")
    return 0 if not n_fail else 1


# ── mutants: mỗi cái PHẢI làm selfcheck đỏ ─────────────────────────────────────────────────────
MUTANTS = [
    ("lag_dd_pack.py", 'status = "CLEARED" if not uniq else "FLAG"', 'status = "CLEARED"'),
    ("lag_dd_pack.py", '        flags.append(_f("INSIDER_NA", "_insider_scan trả None (lỗi/nguồn cũ)"))', "        pass"),
    ("lag_dd_pack.py", '            errors[name] = f"{type(e).__name__}: {str(e)[:200]}"\n            return None',
     '            return {}'),
    ("lag_dd_pack.py", "        if g - rev_g > EQ_WC_GAP_PP:", "        if False:"),
    ("lag_dd_pack.py", '            "severity": "WARNING" if code in WARNING_ONLY else "FLAG",', '            "severity": "FLAG",'),
    ("lag_dd_pack.py", "        write_atomic(sp, {\"sent\": sorted(sent | {_nkey(p) for p in new})})\n        return len(new), msg",
     "        return len(new), msg"),
    ("lag_dd_pack.py", '        if rc != 0:', '        if False:'),
    ("lag_dd_ack.py", '    elif a.get("decided_by") != "user":', '    elif False:'),
    ("lag_dd_ack.py", '    elif a.get("flags_hash") != fh:', '    elif False:'),
    ("lag_dd_ack.py", '    if status == "CLEARED" and not fl:', '    if status == "CLEARED":'),
    ("lag_dd_ack.py", '    if decided_by != "user":', '    if False:'),
    ("lag_dd_ack.py", "        if rel <= d0 and (d0 - rel).days <= PACK_MAX_AGE_DAYS", "        if True"),
    ("lag_plan_consistency_check.py", '        if book == "LAG" or (not book and _tk(o.get("ticker")) in buy_dec):',
     '        if book == "LAG":'),
    ("lag_plan_consistency_check.py", '            if g["state"] in BUY_OK:\n                continue',
     '            if g["state"] != "NO_PACK":\n                continue'),
]


def run_mutants():
    bad = 0
    for i, (fn, old, new) in enumerate(MUTANTS, 1):
        td = tempfile.mkdtemp()
        try:
            for f in ("lag_dd_pack.py", "lag_dd_ack.py", "lag_plan_consistency_check.py", "wc_paths.py",
                      os.path.basename(__file__)):
                shutil.copy(os.path.join(HERE, f), td)
            src = open(os.path.join(td, fn)).read()
            if src.count(old) != 1:
                print(f"  ❌ mutant {i} ({fn}): chuỗi gốc không khớp đúng 1 lần — sửa danh sách MUTANTS")
                bad += 1
                continue
            open(os.path.join(td, fn), "w").write(src.replace(old, new))
            env = dict(os.environ, WC_ROOT=os.environ.get("WC_ROOT") or _wc_root())
            r = subprocess.run([sys.executable, os.path.join(td, os.path.basename(__file__)), "--inner"],
                               capture_output=True, text=True, env=env, timeout=300)
            killed = r.returncode != 0
            print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i} {fn}: {old.strip()[:70]!r}")
            bad += 0 if killed else 1
        finally:
            shutil.rmtree(td, ignore_errors=True)
    print(f"MUTANTS: {len(MUTANTS) - bad}/{len(MUTANTS)} killed")
    return bad


def _wc_root():
    import wc_paths
    return wc_paths.find_wc_root(__file__)


def main():
    if "--inner" in sys.argv:
        return run_inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"=== {label} ===")
        env["MIKE_BOT_TEST_MODE"] = "1"
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env)
        rc |= r.returncode
    print("=== mutants ===")
    if run_mutants():
        rc |= 1
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
