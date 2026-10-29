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
        "capraise": lambda t, a: [],
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

        # 1b. tăng vốn (29/10, capital_raise_lib) — SCL quyền mua P 15,38% (thật) ⇒ cờ; lỗi nguồn ⇒ _NA
        scl_p = {"id": "6a0516165b1fb4c98c3ab2a2", "ticker": "AAA", "issue_method_code": "Rights",
                 "issue_status_code": "P", "event_status": "announced", "exright_date": None, "record_date": None,
                 "public_date": "2026-09-08", "exercise_ratio": 0.15384615, "value_per_share": None,
                 "total_value": 0.0, "issue_volumn": 0}
        Bc = lambda iss, **kw: P.build_pack("AAA", "2026-10-21", cand={"entry_date": "2026-10-26"},  # noqa: E731
                                            sources=dict(sources(**dict(GOOD, **kw)), capraise=iss))
        p = Bc(lambda t, a: [scl_p])
        ck("tăng vốn đang chạy ⇒ gói VẪN CLEARED, chỉ WARNING CAPITAL_RAISE_PENDING (user chọn (b): không chặn mua; bằng chứng có 15.38%)",
           p["status"] == "CLEARED" and codes(p) == [] and
           [w["code"] for w in p["warnings"]] == ["CAPITAL_RAISE_PENDING"] and "15.38%" in p["warnings"][0]["evidence"],
           (codes(p), p["warnings"]))
        p = Bc(boom)
        ck("nguồn phát hành lỗi ⇒ CAPITAL_RAISE_NA + lỗi thật trong source_errors (§29)",
           codes(p) == ["CAPITAL_RAISE_NA"] and "nguồn hỏng giả" in p["source_errors"].get("capital_raise", ""), (codes(p), p["source_errors"]))
        p = Bc(lambda t, a: [dict(scl_p, issue_method_code="DIV", exercise_ratio=0.15)])
        ck("cổ tức CP sắp tới ⇒ vẫn CLEARED, chỉ warnings CAPITAL_RAISE_INFO",
           p["status"] == "CLEARED" and any(w["code"] == "CAPITAL_RAISE_INFO" for w in p["warnings"]), (codes(p), p["warnings"]))
        os_rows = [dict(r, OShares=v) for r, v in zip(fin_rows(), (38_836_815, 37e6, 32e6, 24e6, 22_392_839))]
        p = Bc(lambda t, a: [scl_p], fin=os_rows)
        ck("cảnh báo tăng vốn kèm số CP lưu hành 4 quý +73.4% (OShares P0/P4)",
           any("+73.4%" in w["evidence"] for w in p["warnings"] if w["code"] == "CAPITAL_RAISE_PENDING"), p["warnings"])
        p0 = Bc(lambda t, a: [])
        ck("flags_hash KHÔNG đổi khi có cảnh báo tăng vốn (ack cũ không bị mất hiệu lực)",
           P.flags_hash(p["flags"]) == P.flags_hash(p0["flags"]) and p["flags_hash"] == p0["flags_hash"], (p["flags_hash"], p0["flags_hash"]))

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
            ("EBITM/AR/Inventory NULL mà không phải NH", dict(fin=fin_rows(EBITM_P0=None, AR_P0=None, Inventory_P0=None)), "FIN_NA"),
            ("thiếu Revenue_P0", dict(fin=fin_rows(Revenue_P0=None)), "FIN_NA"),
            ("thiếu Revenue_P4", dict(fin=fin_rows(Revenue_P4=None)), "FIN_NA"),
            ("Revenue_P4 = 0", dict(fin=fin_rows(Revenue_P4=0)), "FIN_NA"),
            ("thiếu AR_P0 (NH khác có số)", dict(fin=fin_rows(AR_P0=None)), "FIN_NA"),
            ("thiếu Inventory_P0", dict(fin=fin_rows(Inventory_P0=None)), "FIN_NA"),
            ("thiếu NPM_P0", dict(fin=fin_rows(NPM_P0=None)), "FIN_NA"),
            ("thiếu EBITM_P0", dict(fin=fin_rows(EBITM_P0=None)), "FIN_NA"),
            ("thiếu NP_P5", dict(fin=fin_rows(NP_P5=None)), "FIN_NA"),
            ("thiếu NP_P7", dict(fin=fin_rows(NP_P7=float("nan"))), "FIN_NA"),
            ("EBITM=0 + AR có số + thiếu Revenue_P4", dict(fin=fin_rows(EBITM_P0=0, Revenue_P4=None)), "FIN_NA"),
            ("thiếu AR kỳ cùng kỳ năm trước", dict(fin=[fin_row()] + fin_rows()[1:4]), "FIN_NA"),
        ]
        for name, kw, code in cases:
            p = B(**kw)
            ck(f"fail-closed: {name} ⇒ {code}, FLAG", p["status"] == "FLAG" and code in codes(p), codes(p))
        p = B(fin=fin_rows(EBITM_P0=None, AR_P0=None, Inventory_P0=None))
        ck("is_bank bắt cả NULL: EBITM/AR/Inventory NULL ⇒ FIN_NA nêu 'không xác nhận được là ngân hàng'",
           any("không xác nhận" in f["evidence"] for f in p["flags"] if f["code"] == "FIN_NA"), p["flags"])
        p = B(fin=fin_rows(Revenue_P4=None, AR_P0=None, NPM_P0=None, NP_P6=None))
        ev = " ".join(f["evidence"] for f in p["flags"] if f["code"] == "FIN_NA")
        ck("FIN_NA nêu TÊN trường thiếu", all(n in ev for n in ("Revenue_P4", "AR_P0", "NPM_P0", "NP_P6")), ev)
        p2 = B(fin=[dict(fin_row(AR_P0=0.0, Inventory_P0=0.0, Inventory_P4=0.0)),
                    {"quarter": "2025Q3", "AR_P0": 0.0, "Inventory_P0": 0.0}])
        ck("AR/tồn kho = 0 cả hai kỳ ⇒ 'không áp dụng', KHÔNG cờ FIN_NA/EQ",
           p2["status"] == "CLEARED" and "không áp dụng" in str(p2["earnings_quality"]["working_capital"]["inventory"]),
           (codes(p2), p2["earnings_quality"]["working_capital"]))
        p3 = B(fin=[fin_row(AR_P0=50.0), {"quarter": "2025Q3", "AR_P0": 0.0, "Inventory_P0": 100.0}])
        ck("phải thu từ 0 lên >0 ⇒ EQ_PHAI_THU_TANG (không lọt)", "EQ_PHAI_THU_TANG" in codes(p3), codes(p3))
        ck("phải thu từ 0 lên: bằng chứng cũng nói 'không tách được'", any(
           "không tách được" in f["evidence"] for f in p3["flags"] if f["code"] == "EQ_PHAI_THU_TANG"), p3["flags"])
        # SCL 2026Q3 số THẬT (tav2_bq.ticker_financial, đọc 2026-10-22): AR_P0 203,5 tỷ gồm 86,6 tỷ trả
        # trước người bán (BCTC V.3–V.6) nhưng BQ không có cột tách ⇒ cờ VẪN giữ trên tổng + nói rõ.
        scl = [fin_row(AR_P0=203497947567.0, AdvCust_P0=1798711058.0, Revenue_P0=277941239226.0,
                       Revenue_P4=147251526187.0),
               {"quarter": "2025Q3", "AR_P0": 78458871880.0, "Inventory_P0": 100.0}]
        ps = B(fin=scl)
        ev = " ".join(f["evidence"] for f in ps["flags"] if f["code"] == "EQ_PHAI_THU_TANG")
        ck("SCL thật: AR tổng +159% vs DT +89% ⇒ VẪN EQ_PHAI_THU_TANG (không tách được trả trước)",
           ps["status"] == "FLAG" and "EQ_PHAI_THU_TANG" in codes(ps), codes(ps))
        ck("bằng chứng cờ phải thu nói rõ 'không tách được' trả trước", "không tách được" in ev, ev)
        ck("working_capital.receivables ghi cơ sở tính (tổng phải thu)",
           "không tách được" in str(ps["earnings_quality"]["working_capital"]["receivables"].get("basis")),
           ps["earnings_quality"]["working_capital"]["receivables"])
        pa = B(fin=fin_rows(AR_P0=200.0, AdvCust_P0=150.0))
        ck("AdvCust (NGƯỜI MUA trả trước) lớn KHÔNG được trừ khỏi AR ⇒ vẫn cờ",
           "EQ_PHAI_THU_TANG" in codes(pa), codes(pa))
        pt = B(fin=fin_rows(Inventory_P0=200.0))
        ck("cờ tồn kho KHÔNG kèm ghi chú phải thu",
           all("không tách được" not in f["evidence"] for f in pt["flags"] if f["code"] == "EQ_TON_KHO_TANG"),
           pt["flags"])
        d = fin_rows(AR_P0=200.0, DSO_P0=20.0, DSO_P4=40.0)
        p4 = B(fin=d)
        ck("DSO vendor đi ngược AR thô ⇒ ghi chú dữ liệu mâu thuẫn", any("MÂU THUẪN" in n for n in
           p4["earnings_quality"]["data_notes"]), p4["earnings_quality"]["data_notes"])
        ck("tin Discord nêu ghi chú mâu thuẫn DSO", "MÂU THUẪN" in P.render_message([p4]))
        # DT tăng mạnh hơn AR ⇒ DSO GIẢM là đúng (không mâu thuẫn); DSO TĂNG mới là mâu thuẫn (ca MSR 24/10)
        pd1 = B(fin=fin_rows(AR_P0=150.0, Revenue_P0=200.0, DSO_P0=20.0, DSO_P4=40.0))
        ck("AR +50% < DT +100% & DSO giảm ⇒ KHÔNG ghi chú mâu thuẫn giả",
           not any("MÂU THUẪN" in n for n in pd1["earnings_quality"]["data_notes"]),
           pd1["earnings_quality"]["data_notes"])
        pd2 = B(fin=fin_rows(AR_P0=150.0, Revenue_P0=200.0, DSO_P0=60.0, DSO_P4=40.0))
        ck("AR +50% < DT +100% mà DSO TĂNG ⇒ ghi chú mâu thuẫn",
           any("MÂU THUẪN" in n for n in pd2["earnings_quality"]["data_notes"]),
           pd2["earnings_quality"]["data_notes"])
        c2 = p4["earnings_quality"]["cfo_vs_np"]
        ck("CFO/LNST có 2 quý gần nhất (14+13 / 13+12) và tin hiện dòng đó",
           c2.get("cfo_2q_vnd") == 27.0 and c2.get("np_2q_vnd") == 25.0
           and "2Q gần nhất" in P.render_message([B(dd=dd_ok(adv=1.5e9))]), c2)
        ck("CFO 2Q chỉ hiển thị: không đổi flags_hash",
           B()["flags_hash"] == B()["flags_hash"] and "cfo_2q_vnd" not in json.dumps(B()["flags"]))

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
        # DCF RICH: chỉ SÂU (MoS < -100%) mới là cờ; RICH nhẹ = cảnh báo, không đổi status (user chốt 24/10, phương án A)
        pm = B(val=({"status": "RICH", "margin_of_safety": -0.5}, "🔴 DCF RICH nhẹ", "", None))
        ck("RICH nhẹ (MoS -50%) ⇒ KHÔNG cờ DCF_RICH, status CLEARED",
           "DCF_RICH" not in codes(pm) and pm["status"] == "CLEARED", codes(pm))
        ck("RICH nhẹ ⇒ pack['warnings'] có DCF_RICH_NHE kèm số MoS",
           [w["code"] for w in pm.get("warnings", [])] == ["DCF_RICH_NHE"] and "-50.0%" in pm["warnings"][0]["evidence"],
           pm.get("warnings"))
        ck("RICH nhẹ: warnings KHÔNG vào flags_hash", pm["flags_hash"] == B()["flags_hash"])
        ck("RICH nhẹ: tin Discord hiện WARNING dù CLEARED", "DCF_RICH_NHE" in P.render_message([pm]))
        pd = B(val=({"status": "RICH", "margin_of_safety": -1.38}, "🔴 DCF RICH sâu", "", None))
        ck("RICH sâu (MoS -138%) ⇒ cờ DCF_RICH, status FLAG, không warning nhẹ",
           "DCF_RICH" in codes(pd) and pd["status"] == "FLAG" and not pd.get("warnings"), (codes(pd), pd.get("warnings")))
        pe = B(val=({"status": "RICH", "margin_of_safety": -1.0}, "x", "", None))
        ck("RICH đúng -100% (biên) ⇒ nhẹ, KHÔNG cờ (ngưỡng là < -100%)", "DCF_RICH" not in codes(pe), codes(pe))
        pn = B(val=({"status": "RICH", "margin_of_safety": None}, "x", "", None))
        ck("RICH thiếu MoS ⇒ fail-closed vẫn cờ DCF_RICH", "DCF_RICH" in codes(pn), codes(pn))
        for nm, bad in (("NaN", float("nan")), ("inf", float("inf")), ("'nan'", "nan"), ("chuỗi lạ", "abc")):
            pb = B(val=({"status": "RICH", "margin_of_safety": bad}, "x", "", None))
            ck(f"RICH MoS={nm} ⇒ fail-closed vẫn cờ DCF_RICH, không warning",
               "DCF_RICH" in codes(pb) and not pb.get("warnings"), (codes(pb), pb.get("warnings")))
        pk = B(val=({"status": "RICH"}, "x", "", None))
        ck("RICH thiếu hẳn key MoS ⇒ cờ DCF_RICH", "DCF_RICH" in codes(pk), codes(pk))
        pp = B(val=({"status": "RICH", "margin_of_safety": 0.3}, "x", "", None))
        ck("RICH mà MoS dương (dữ liệu mâu thuẫn) ⇒ fail-closed cờ DCF_RICH", "DCF_RICH" in codes(pp), codes(pp))
        ck("khoá notify không warning GIỮ ĐỊNH DẠNG CŨ (không gửi lại gói cũ)",
           P._nkey(dict(pm, warnings=[])) == f"{pm['ticker']}|{pm['release_date']}|{pm['flags_hash']}|CLEARED",
           P._nkey(dict(pm, warnings=[])))
        ck("khoá notify: gói CLEARED có warning ≠ khoá không warning",
           P._nkey(pm) != P._nkey(dict(pm, warnings=[])), (P._nkey(pm), P._nkey(dict(pm, warnings=[]))))
        pf = B(val=({"status": "FAIR", "margin_of_safety": 0.05}, "x", "", None))
        ck("FAIR/CHEAP ⇒ không cờ, không warning", "DCF_RICH" not in codes(pf) and not pf.get("warnings"), pf.get("warnings"))
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

        # 3b. anomaly qua anomaly_gate canonical (stale ⇒ NA; quá TTL / tương lai ⇒ không cờ)
        import anomaly_gate as AG
        agd = os.path.join(td, "ag")
        os.makedirs(os.path.join(agd, "data"))
        old_wd = AG.WORKDIR
        AG.WORKDIR = agd

        def put_anom(meta_gen="2026-10-21T01:00:00Z", **recs):
            d = {k: {"last_alert": v, "tier": "H", "reasons": "x"} for k, v in recs.items()}
            if meta_gen:
                d["_meta"] = {"generated_at": meta_gen}
            json.dump(d, open(os.path.join(agd, "data", "anomaly_flags.json"), "w"))
        try:
            put_anom(VPB="2026-10-10")
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: file tươi + last_alert trong TTL ⇒ có bản ghi", ok and rec and rec["last_alert"] == "2026-10-10", (ok, rec, err))
            put_anom(VPB="2026-09-18")
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: last_alert 33 ngày > TTL 30 ⇒ KHÔNG cờ (ok, rec=None)", ok and rec is None, (ok, rec, err))
            put_anom(VPB="2026-11-02")
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: last_alert TƯƠNG LAI ⇒ không cờ (không look-ahead)", ok and rec is None, (ok, rec, err))
            put_anom(meta_gen="2026-10-15T01:00:00Z", VPB="2026-10-10")
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: file ghi ngày khác asof (stale) ⇒ ok=False", not ok and "cũ" in str(err), (ok, rec, err))
            put_anom(meta_gen=None, VPB="2026-10-10")
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: thiếu _meta.generated_at ⇒ ok=False", not ok, (ok, rec, err))
            os.remove(os.path.join(agd, "data", "anomaly_flags.json"))
            ok, rec, err = P.anomaly_evidence("VPB", "2026-10-21")
            ck("anomaly: file không có ⇒ ok=False", not ok, (ok, rec, err))
            p = B(dd=dd_ok(anomaly_ok=ok, anomaly_err=err))
            ck("anomaly: ok=False ⇒ pack FLAG ANOMALY_NA", "ANOMALY_NA" in codes(p), codes(p))
        finally:
            AG.WORKDIR = old_wd

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
            dict(flags_hash="0000000000000000"), dict(flags_hash=""), dict(source=""), dict(source="  "),
        ]
        base = dict(ticker="SCL", release_date="2026-10-19", decision="PROCEED", decided_by="user",
                    at="2026-10-25T18:30:00+07:00", flags_hash=flagged["flags_hash"], source="discord test msg")
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
        regen = dict(B(dd=dd_ok(adv=1.5e9, anomaly_rec={"tier": "H"})), ticker="SCL")
        P.write_atomic(P.pack_path("SCL", "2026-10-19"), regen)
        try:
            K.record(**base)
            ok = False
        except ValueError as e:
            ok = "flags_hash" in str(e)
        ck("ack: gói sinh lại giữa tin và trả lời ⇒ record từ chối (hash cũ), không đóng dấu bộ cờ mới", ok)
        n_acks = len(json.load(open(K.ack_path()))["acks"])
        ck("ack: lần từ chối không ghi thêm mục", n_acks == 1, n_acks)
        P.write_atomic(P.pack_path("SCL", "2026-10-19"), dict(flagged, ticker="SCL"))
        K.record(**base)
        ck("gate: ack PROCEED mới nhất thắng ⇒ ACK_PROCEED", G("SCL") == "ACK_PROCEED", G("SCL"))
        P.write_atomic(P.pack_path("SCL", "2026-10-19"), regen)
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
        # CLEARED không nuốt DROP/RESEARCH của user cho đúng release (gói sinh lại sạch cờ ⇒ hash đổi)
        P.write_atomic(P.pack_path("DRP", "2026-10-19"), dict(cleared, ticker="DRP"))
        mk = lambda **kw: dict(dict(ticker="DRP", release_date="2026-10-19", decision="DROP", decided_by="user",  # noqa: E731
                                    at="2026-10-24T11:06:00+07:00", flags_hash="deadbeefdeadbeef",
                                    source="selfcheck"), **kw)
        P.write_atomic(K.ack_path(), {"acks": [mk()]})
        ck("gate: pack CLEARED + user DROP cũ (hash khác) ⇒ ACK_DROP, KHÔNG mua", G("DRP") == "ACK_DROP", G("DRP"))
        P.write_atomic(K.ack_path(), {"acks": [mk(decision="RESEARCH")]})
        ck("gate: pack CLEARED + user RESEARCH ⇒ ACK_RESEARCH", G("DRP") == "ACK_RESEARCH", G("DRP"))
        P.write_atomic(K.ack_path(), {"acks": [mk(decision="PROCEED")]})
        ck("gate: pack CLEARED + ack PROCEED ⇒ vẫn CLEARED (PROCEED không được đọc ở nhánh CLEARED)",
           G("DRP") == "CLEARED", G("DRP"))
        P.write_atomic(K.ack_path(), {"acks": [mk(decided_by="agent")]})
        ck("gate: pack CLEARED + DROP do agent ⇒ không phải quyết định user ⇒ CLEARED", G("DRP") == "CLEARED", G("DRP"))
        P.write_atomic(K.ack_path(), {"acks": [mk(release_date="2026-07-19")]})
        ck("gate: pack CLEARED + DROP của release KHÁC ⇒ CLEARED", G("DRP") == "CLEARED", G("DRP"))
        open(K.ack_path(), "w").write("{hỏng")
        ck("gate: pack CLEARED + ack.json hỏng ⇒ giữ CLEARED (hành vi cũ)", G("DRP") == "CLEARED", G("DRP"))
        os.remove(K.ack_path())

        # 4b. độ tươi gói / gói NA mới hơn / gắn release ứng viên (n1)
        old_pk = dict(cleared, ticker="STL", asof="2026-10-10")
        P.write_atomic(P.pack_path("STL", "2026-10-19"), old_pk)
        ck("gate: gói asof cách plan_date > 7 ngày ⇒ PACK_STALE (dù CLEARED)", G("STL") == "PACK_STALE", G("STL"))
        P.write_atomic(P.pack_path("NAN", "2026-10-19"), dict(cleared, ticker="NAN", generated_at="2026-10-20T08:00:00+07:00"))
        P.write_atomic(P.pack_path("NAN", None), dict(flagged, ticker="NAN", release_date=None,
                                                      generated_at="2026-10-21T08:00:00+07:00"))
        ck("gate: gói NA MỚI hơn ⇒ thắng gói CLEARED cũ (không dùng CLEARED cũ)", G("NAN") != "CLEARED", G("NAN"))
        P.write_atomic(P.pack_path("NAO", "2026-10-19"), dict(cleared, ticker="NAO", generated_at="2026-10-21T08:00:00+07:00"))
        P.write_atomic(P.pack_path("NAO", None), dict(flagged, ticker="NAO", release_date=None,
                                                      generated_at="2026-10-20T08:00:00+07:00"))
        ck("gate: gói NA CŨ hơn gói có release ⇒ dùng gói có release", G("NAO") == "CLEARED", G("NAO"))
        ck("gate: release ứng viên khác release của gói ⇒ NO_PACK",
           K.dd_gate("HT1", "2026-10-26", release_date="2026-10-12")["state"] == "NO_PACK")
        ck("gate: release ứng viên khớp ⇒ CLEARED",
           K.dd_gate("HT1", "2026-10-26", release_date="2026-10-19")["state"] == "CLEARED")

        # 4c. ghi chú prompt DollarBill: quy mô user chốt trong ack (job Taylor_20261025_043744)
        ck("ack_tier: 'LAG_LO 8%' ⇒ (LAG_LO, 8)", K.ack_tier("vào LAG_LO 8% (~4% NAV)") == ("LAG_LO", "8"))
        ck("ack_tier: không nêu ⇒ (None, None)", K.ack_tier("PROCEED") == (None, None))
        ck("ack_tier: LO và HI cùng lúc ⇒ mơ hồ (None, None)",
           K.ack_tier("không LAG_HI 10%, vào LAG_LO 8%") == (None, None))
        ck("ack_tier: 2 tier không phủ định ('LAG_HI 10% hoặc LAG_LO 8%') ⇒ mơ hồ",
           K.ack_tier("LAG_HI 10% hoặc LAG_LO 8%") == (None, None))
        ck("ack_tier: LAG_LOW không phải tier", K.ack_tier("LAG_LOW 8%") == (None, None))
        ck("ack_tier: phủ định 'không vào LAG_HI 10%' ⇒ mơ hồ", K.ack_tier("không vào LAG_HI 10%") == (None, None))
        ck("ack_tier: note SCL thật ⇒ LAG_LO 8", K.ack_tier("PROCEED theo đề xuất 21/10: quy mô LAG_LO 8% (~4% NAV); "
                                                         "user tự thực hiện ĐẦY ĐỦ quyền mua") == ("LAG_LO", "8"))
        nd = os.path.join(td, "note")
        os.makedirs(nd)
        for t in ("CLR", "PRO", "AMB", "DRO", "NOA"):
            P.write_atomic(os.path.join(nd, f"{t}_2026-10-19.json"),
                           dict(cleared if t == "CLR" else flagged, ticker=t))
        P.write_atomic(os.path.join(nd, "OLD_2026-08-01.json"), dict(cleared, ticker="OLD", release_date="2026-08-01"))
        mka = lambda t, d, n: dict(ticker=t, release_date="2026-10-19", decision=d, decided_by="user",  # noqa: E731
                                   at="2026-10-24T11:06:00+07:00", flags_hash=flagged["flags_hash"], note=n, source="sc")
        P.write_atomic(os.path.join(nd, "ack.json"), {"acks": [
            mka("PRO", "PROCEED", "vào LAG_HI 10%"), mka("PRO", "PROCEED", "user chốt LAG_LO 8% (~4% NAV)"),
            mka("AMB", "PROCEED", "proceed"), mka("DRO", "DROP", "loại")]})
        nt = K.prompt_note("2026-10-26", nd)
        ok_part, bad_part = nt.split("KHÔNG ĐƯA VÀO orders[]", 1) if "KHÔNG ĐƯA VÀO orders[]" in nt else (nt, "")
        ck("note: PROCEED lấy quy mô ack MỚI NHẤT (LAG_LO 8%)", "PRO (user PROCEED" in ok_part
           and "quy mô LAG_LO 8% DO USER CHỐT" in ok_part, nt[:400])
        ck("note: CLEARED vào danh sách được vào", "CLR (CLEARED" in ok_part, nt[:300])
        ck("note: PROCEED không nêu quy mô ⇒ nói rõ KHÔNG nêu, không đoán tier",
           "AMB (user PROCEED" in ok_part and "KHÔNG nêu quy mô" in ok_part.split("AMB (", 1)[1].split(");", 1)[0], nt)
        ck("note: DROP / FLAG chưa ack ⇒ danh sách KHÔNG vào", "DRO (ACK_DROP)" in bad_part
           and "NOA (FLAG_NO_ACK)" in bad_part and "DRO (" not in ok_part and "NOA (" not in ok_part, nt[-500:])
        ck("note: gói ngoài cửa sổ (NO_PACK) bị bỏ qua", "OLD" not in nt, nt)
        ck("note: có câu PHẠM VI (chỉ mã recommend đề xuất đúng phiên, không kéo ngày sớm)",
           "PHẠM VI" in nt and "KHÔNG kéo ngày vào sớm" in nt, nt[:300])
        ck("note: không khẳng định sai 'chặn cứng' (checker chỉ cảnh báo)", "chặn cứng các mã" not in nt
           and "chưa chặn cứng" in nt, nt[-300:])
        ck("note: PROCEED không tier ⇒ KHÔNG mặc định LAG_HI, đòi user duyệt",
           "KHÔNG mặc định LAG_HI" in nt and "requires_user_approval=true" in nt, nt)
        ck("note: thư mục không có gói ⇒ chuỗi rỗng", K.prompt_note("2026-10-26", os.path.join(td, "empty")) == "")
        open(os.path.join(nd, "ack.json"), "w").write("{hỏng")
        nt = K.prompt_note("2026-10-26", nd)
        ck("note: ack.json hỏng ⇒ mã FLAG rơi vào KHÔNG vào (ACK_UNREADABLE), không raise",
           "PRO (ACK_UNREADABLE)" in nt.split("KHÔNG ĐƯA VÀO orders[]", 1)[1], nt[-400:])

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
        P.write_atomic(P.pack_path("SCL", "2026-10-19"), dict(flagged, ticker="SCL"))
        K.record(**base)       # ack cho bộ cờ hiện tại của SCL
        r = A(plan([o("SCL")], [due("SCL")]))
        ck("checker: ack PROCEED (user, khớp hash) ⇒ được mua", V(r) == [], V(r))
        r = C.analyze(plan([o("ZZZ")], []), crosscheck=False, dd_gate=False)
        ck("checker: --no-dd-gate tắt cổng", V(r) == [])

        # 5b. vòng 2: due_today TAKE / deferred_orders / FUNDING_ALERT / nhận diện book
        def dfr(t, book="LAG", side="buy"):
            return {"ticker": t, "side": side, "book": book, "status": "WAIT_CASH", "reason": "thiếu tiền"}
        os.remove(K.ack_path())
        r = A(dict(plan([], [due("SCL", "BUY")]), deferred_orders=[dfr("SCL")]))
        F = lambda r, k: sorted((f["ticker"]) for f in r["findings"] if f["kind"] == k)   # noqa: E731
        ck("checker: SCL FLAG chưa ack + due BUY + deferred WAIT_CASH ⇒ VIOLATION",
           V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        ck("checker: …và KHÔNG có FUNDING_ALERT cho SCL (tắt đề xuất cấp vốn cho mã bị chặn)",
           F(r, "FUNDING_ALERT") == [], F(r, "FUNDING_ALERT"))
        r0 = C.analyze(dict(plan([], [due("SCL", "BUY")]), deferred_orders=[dfr("SCL")]), crosscheck=False, dd_gate=False)
        ck("control (chân không cổng): cùng plan ⇒ CÓ FUNDING_ALERT cho SCL", F(r0, "FUNDING_ALERT") == ["SCL"], F(r0, "FUNDING_ALERT"))
        for dec in ("DEFER", "DEFERRED", "BUY_DEFERRED", "WAIT_CASH", "RESIDUAL", "ORDER"):
            r = A(plan([], [due("SCL", dec)]))
            ck(f"checker: due_today decision={dec} (không có lệnh) ⇒ vẫn bị cổng", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        r = A(plan([], [due("SCL", "SKIP")]))
        ck("checker: due_today SKIP ⇒ không vi phạm (chỉ chờ DD)", V(r) == [] and len(r["dd_pending"]) == 1, (V(r), r["dd_pending"]))
        r = A(dict(plan([], []), deferred_orders=[dfr("SCL")]))
        ck("checker: deferred_orders LAG (book LAG) không có due ⇒ bị cổng", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        r = A(dict(plan([], []), deferred_orders=[dfr("HT1"), dfr("SCL", side="sell")]))
        ck("checker: deferred mã CLEARED / lệnh bán ⇒ không vi phạm", V(r) == [], V(r))
        for bk in ("PEAD", "LAG-PEAD", "lag", "LAG_BOOK"):
            r = A(plan([o("SCL", book=bk)], []))
            ck(f"checker: book {bk!r} nhận là LAG", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        # Arch-review vòng 2: cổng KHÔNG áp cho lệnh khai book non-LAG (BAL/CAPIT/DISCRETIONARY) dù mã là ứng viên LAG
        for bk in ("BAL", "CAPIT", "DISCRETIONARY", "PARK"):
            r = A(plan([o("SCL", book=bk)], [due("SCL", "SKIP")]))
            ck(f"checker: lệnh book {bk} mua mã LAG (due SKIP) ⇒ KHÔNG vi phạm", V(r) == [], V(r))
        p_up = plan([o("SCL", book="BAL")], [])
        p_up["lag_analysis"]["lag_upcoming_for_next_plans"] = [{"ticker": "SCL"}]
        ck("checker: lệnh BAL mua mã LAG-upcoming ⇒ KHÔNG vi phạm", V(A(p_up)) == [], V(A(p_up)))
        p_nb = plan([o("SCL", book="")], [])
        p_nb["lag_analysis"]["lag_upcoming_for_next_plans"] = [{"ticker": "SCL"}]
        ck("checker: lệnh THIẾU book mua mã LAG-upcoming ⇒ vẫn bị cổng", ("SCL", "LAG_DD_FLAG_NO_ACK") in V(A(p_nb)), V(A(p_nb)))
        r = A(plan([o("SCL", book="BAL")], [due("SCL", "BUY")]))
        ck("checker: BAL mua SCL nhưng due_today SCL=BUY ⇒ vi phạm CHỈ vì due_today", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")]
           and str([f for f in r["findings"] if f["kind"] == "LAG_DD_GATE_VIOLATION"][0].get("evidence", "")).startswith("[due_today]"), V(r))
        r = A(dict(plan([], []), deferred_orders=[dict(dfr("SCL"), status="SKIPPED_BY_GATE")]))
        ck("checker: deferred status SKIPPED_BY_GATE (không qty) ⇒ không vi phạm", V(r) == [], V(r))
        r = A(dict(plan([], []), deferred_orders=[dict(dfr("SCL"), status="EXCLUDED_DD")]))
        ck("checker: deferred status EXCLUDED_DD ⇒ không vi phạm", V(r) == [], V(r))
        r = A(dict(plan([], []), deferred_orders=[dict(dfr("SCL"), qty=0)]))
        ck("checker: deferred WAIT_CASH qty=0 ⇒ không vi phạm", V(r) == [], V(r))
        r = A(dict(plan([], []), deferred_orders=[dict(dfr("SCL"), qty=500)]))
        ck("checker: deferred WAIT_CASH qty>0 ⇒ vi phạm", V(r) == [("SCL", "LAG_DD_FLAG_NO_ACK")], V(r))
        r = A(plan([o("SCL", side="BUY")], [due("SCL", "BUY")]))
        ck("checker: side 'BUY' hoa ⇒ nhận là mua", ("SCL", "LAG_DD_FLAG_NO_ACK") in V(r), V(r))
        r = A(plan([o("SCL", book="FLAGSHIP")], []))
        ck("checker: book chứa 'LAG' trong từ khác (FLAGSHIP) không bị nhận nhầm là LAG", V(r) == [], V(r))

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
    # tăng vốn (29/10)
    ("lag_dd_pack.py", '        flags.append(_f("CAPITAL_RAISE_NA", errors.get("capital_raise")))', "        pass"),
    ("lag_dd_pack.py", "capital_raise_eval(rows or [], iss, asof)[1]", "capital_raise_eval(rows or [], iss, asof)[0]"),
    ("lag_dd_pack.py", '        "warnings": soft_warnings(ev) + cr_warn,', '        "warnings": soft_warnings(ev),'),
    ("lag_dd_pack.py", "    g12 = os_[0] / os_[4] - 1 if len(os_) == 5 and os_[0] and os_[4] else None", "    g12 = None"),
    # DCF RICH sâu/nhẹ (user chốt 24/10, arch-review: mutant NaN từng sống sót)
    ("lag_dd_pack.py", "    return mos is None or mos < DCF_RICH_DEEP_MOS or mos > 0",
     "    return mos is not None and mos < DCF_RICH_DEEP_MOS"),
    ("lag_dd_pack.py", '    mos = _num(dcf.get("margin_of_safety"))\n    return mos is None',
     '    mos = dcf.get("margin_of_safety")\n    return mos is None'),
    ("lag_dd_pack.py", "mos is None or mos < DCF_RICH_DEEP_MOS or mos > 0",
     "mos is None or mos <= DCF_RICH_DEEP_MOS or mos > 0"),
    ("lag_dd_pack.py", "mos is None or mos < DCF_RICH_DEEP_MOS or mos > 0",
     "mos is None or mos < DCF_RICH_DEEP_MOS"),
    ("lag_dd_pack.py", '                            + (f" — {AR_BASIS_NOTE}" if col == "AR_P0" else "")))\n    if isinstance',
     '                            ))\n    if isinstance'),
    ("lag_dd_pack.py", '        wc["receivables"]["basis"] = AR_BASIS_NOTE', '        pass'),
    ("lag_dd_pack.py", "        cur = _num(r.get(col))\n",
     '        cur = (_num(r.get(col)) or 0) - (_num(r.get("AdvCust_P0")) or 0) if col == "AR_P0" else _num(r.get(col))\n'),
    ("lag_dd_pack.py", '                            + (f" — {AR_BASIS_NOTE}" if col == "AR_P0" else "")))\n    if isinstance',
     '                            + f" — {AR_BASIS_NOTE}"))\n    if isinstance'),
    ("lag_dd_pack.py", '                            + (f" — {AR_BASIS_NOTE}" if col == "AR_P0" else "")))\n            continue',
     '                            ))\n            continue'),
    ("lag_plan_consistency_check.py", 'return bool(_RE_LAG_BOOK.search(bk)) or (not bk and _tk(o.get("ticker")) in lag_tk)',
     'return bool(_RE_LAG_BOOK.search(bk)) or _tk(o.get("ticker")) in lag_tk'),
    ("lag_plan_consistency_check.py", 'and not str(d.get("status") or "").strip().upper().startswith(("SKIP", "EXCLUD"))', 'and True'),
    ("lag_dd_pack.py", 'status = "CLEARED" if not uniq else "FLAG"', 'status = "CLEARED"'),
    ("lag_dd_pack.py", '        flags.append(_f("INSIDER_NA", "_insider_scan trả None (lỗi/nguồn cũ)"))', "        pass"),
    ("lag_dd_pack.py", '            errors[name] = f"{type(e).__name__}: {str(e)[:200]}"\n            return None',
     '            return {}'),
    ("lag_dd_pack.py", "        if g - rev_g > EQ_WC_GAP_PP:", "        if False:"),
    ("lag_dd_pack.py", '            "severity": "WARNING" if code in WARNING_ONLY else "FLAG",', '            "severity": "FLAG",'),
    ("lag_dd_pack.py", "        write_atomic(sp, {\"sent\": sorted(sent | {_nkey(p) for p in new})})\n        return len(new), msg",
     "        return len(new), msg"),
    ("lag_dd_pack.py", '        if rc != 0:', '        if False:'),
    ("lag_dd_pack.py", '        if cur is None:\n            missing.append(col)', '        if False:\n            missing.append(col)'),
    ("lag_dd_pack.py", '    missing += [n for n, v in (("Revenue_P0", rev0), ("Revenue_P4", rev4)) if v is None]',
     '    missing += []'),
    ("lag_dd_pack.py", '    missing += [n for n, v in (("NPM_P0", npm), ("EBITM_P0", ebm)) if v is None]', '    missing += []'),
    ("lag_dd_pack.py", '    missing += [f"NP_P{i}" for i in (5, 6, 7) if np_[i] is None]', '    missing += []'),
    ("lag_dd_pack.py", 'in (0, None) for c in ("EBITM_P0"', 'in (0,) for c in ("EBITM_P0"'),
    ("lag_dd_pack.py", '    if fr["is_stale"]:', '    if False:'),
    ("lag_dd_pack.py", 'if ticker in ag.anomaly_excluded(asof, quiet=True) else None', 'if True else None'),
    ("lag_dd_ack.py", '    if str(flags_hash).strip() != pk.get("flags_hash"):', '    if False:'),
    ("lag_dd_ack.py", '    if not str(source or "").strip():', '    if False:'),
    ("lag_dd_ack.py", '    if age > PACK_ASOF_MAX_DAYS or age < 0:', '    if False:'),
    ("lag_dd_ack.py", '        if g_na is None or g_best is None or g_na > g_best:', '        if False:'),
    ("lag_dd_ack.py", '        if release_date and m.group(2) != str(release_date)[:10]:', '        if False:'),
    ("lag_plan_consistency_check.py", '    for d in plan.get("deferred_orders") or []:\n        if (isinstance(d, dict) and', '    for d in []:\n        if (isinstance(d, dict) and'),
    ("lag_plan_consistency_check.py", '    for t in take:\n        hits.setdefault(t, []).append("due_today")', '    for t in []:\n        hits.setdefault(t, []).append("due_today")'),
    ("lag_plan_consistency_check.py", '        kept = [f for f in res["findings"] if not (f["kind"] == "FUNDING_ALERT" and f.get("ticker") in blocked)]',
     '        kept = list(res["findings"])'),
    ("lag_plan_consistency_check.py", '        return bool(_RE_LAG_BOOK.search(bk)) or (not bk and _tk(o.get("ticker")) in lag_tk)',
     '        return bk == "LAG"'),
    ("lag_dd_ack.py", '    elif a.get("decided_by") != "user":', '    elif False:'),
    ("lag_dd_ack.py", '    elif a.get("flags_hash") != fh:', '    elif False:'),
    ("lag_dd_ack.py", '    if status == "CLEARED" and not fl:', '    if status == "CLEARED":'),
    ("lag_dd_ack.py", '    if decided_by != "user":', '    if False:'),
    ("lag_dd_ack.py", 'if la and la.get("decided_by") == "user" and la.get("decision") in ("DROP", "RESEARCH"):',
     'if False:'),
    ("lag_dd_ack.py", 'if la and la.get("decided_by") == "user" and la.get("decision") in ("DROP", "RESEARCH"):',
     'if la and la.get("decision") in ("DROP", "RESEARCH"):'),
    ("lag_dd_ack.py", 'if la and la.get("decided_by") == "user" and la.get("decision") in ("DROP", "RESEARCH"):',
     'if la and la.get("decided_by") == "user":'),
    ("lag_dd_pack.py", "if abs(exp_) > 0.10 and abs(dd_) > 0.10 and (exp_ > 0) != (dd_ > 0):",
     'if abs(ar["yoy"]) > 0.10 and abs(dd_) > 0.10 and (ar["yoy"] > 0) != (dd_ > 0):'),
    ("lag_dd_pack.py", '"cfo_2q_vnd": cfo[0] + cfo[1]', '"cfo_2q_vnd": cfo[0]'),
    ("lag_dd_ack.py", "        if rel <= d0 and (d0 - rel).days <= PACK_MAX_AGE_DAYS", "        if True"),
    ("lag_dd_ack.py", "    if len(tiers) != 1:", "    if not tiers:"),
    ("lag_dd_ack.py", '    if _RE_TIER_NEG.search(str(note or "")):', "    if False:"),
    ("lag_dd_ack.py", '        if st == "NO_PACK":\n            continue', '        if False:\n            continue'),
    ("lag_plan_consistency_check.py", '            if g["state"] in BUY_OK:\n                continue',
     '            if g["state"] != "NO_PACK":\n                continue'),
]


def run_mutants():
    bad = 0
    for i, (fn, old, new) in enumerate(MUTANTS, 1):
        td = tempfile.mkdtemp()
        try:
            for f in ("lag_dd_pack.py", "lag_dd_ack.py", "lag_plan_consistency_check.py", "wc_paths.py",
                      "capital_raise_lib.py", os.path.basename(__file__)):
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
