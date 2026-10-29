#!/usr/bin/env python3
"""Selfcheck rights_issue_alert.py — hàm thuần, fixture số THẬT SCL (tav2_bq.corporate_action).

Chạy chính nó dưới `env -u TZ` + 2 TZ lạ (§16/§19), rồi MUTANT — mỗi mutant PHẢI làm đỏ.
    python3 bin/rights_issue_alert_selfcheck.py
"""
import contextlib
import datetime as dt
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + ("" if cond else f"  [{detail}]"))


HOL = {dt.date(2025, 9, 1), dt.date(2025, 9, 2)}
is_hol = HOL.__contains__

# SCL 35,714286% — dòng thật (id, ratio, ex, record, volume, total_value) đọc 2026-10-22
SCL25 = {"id": "682291730e8a716db6edd5a4", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "D", "event_status": "executed", "exright_date": "2025-10-17",
         "record_date": "2025-10-20", "public_date": "2025-10-10", "exercise_ratio": "0.35714286",
         "value_per_share": None, "total_value": "1.0E11", "issue_volumn": "8000000"}
# SCL 15,38% — trạng thái P, chưa ngày/giá (thật, public 2026-09-08)
SCL26 = {"id": "6a0516165b1fb4c98c3ab2a2", "ticker": "SCL", "issue_method_code": "Rights",
         "issue_status_code": "P", "event_status": "announced", "exright_date": None,
         "record_date": None, "public_date": "2026-09-08", "exercise_ratio": "0.15384615",
         "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}
POS = {"SpaceX": {"SCL": 14000, "FPT": 100}, "ZaloPay": {"FPT": 50}}


def run_inner():
    import rights_issue_alert as R
    B = R.build_alerts
    a = B("2025-10-10", POS, [SCL25], set(), is_hol)
    t = a[0]["text"] if a else ""
    ck("SCL 2025 lúc công bố ⇒ 1 cảnh báo", len(a) == 1, a)
    ck("đủ số: 5.000 cp, giá 12.500đ, tiền 62.500.000đ", all(s in t for s in ("5,000 cp", "12,500đ", "62,500,000đ")), t)
    ck("nêu GDKHQ + ngày chốt + thiếu hạn nộp tiền", all(s in t for s in ("2025-10-17", "2025-10-20", "KHÔNG có cột")), t)
    ck("ZaloPay không giữ SCL ⇒ không nêu", "ZaloPay" not in t, t)
    ck("lượt đầu gộp ANNOUNCE+DATED (khoá đủ)", set(a[0]["keys"]) == {f"{SCL25['id']}|announce", f"{SCL25['id']}|dated|2025-10-17"}, a[0]["keys"])
    sent = set(a[0]["keys"])
    ck("cùng ngày chạy lại ⇒ không trùng", B("2025-10-10", POS, [SCL25], sent, is_hol) == [])
    ck("10-10 còn 4 phiên cum; 10-09 còn 5 ⇒ chưa nhắc", R.sessions_until("2025-10-10", "2025-10-17", is_hol) == 4
       and B("2025-10-09", POS, [SCL25], sent, is_hol) == [])
    r = B("2025-10-13", POS, [SCL25], sent, is_hol)
    ck("còn 3 phiên ⇒ REMIND", len(r) == 1 and r[0]["stage"] == "REMIND", r)
    sent |= set(r[0]["keys"]) if r else set()
    r2 = B("2025-10-14", POS, [SCL25], sent, is_hol)
    ck("phiên kế tiếp ⇒ REMIND lại (mỗi phiên 1 lần)", len(r2) == 1 and r2[0]["stage"] == "REMIND", r2)
    ck("ngày GDKHQ trở đi ⇒ im", B("2025-10-17", POS, [SCL25], set(), is_hol) == [])
    ck("ngày lễ không tính là phiên", R.sessions_until("2025-08-29", "2025-09-05", is_hol) == 2)

    p = B("2026-10-22", POS, [SCL26], set(), is_hol)
    tp = p[0]["text"] if p else ""
    ck("SCL 2026 trạng thái P, ngày NULL ⇒ VẪN báo (ANNOUNCE)", len(p) == 1 and p[0]["stage"] == "ANNOUNCE", p)
    ck("P: 2.153 cp, nói rõ CHƯA có ngày/giá", all(s in tp for s in ("2,153 cp", "CHƯA CÓ ngày", "CHƯA CÓ (BQ chưa điền)")), tp)
    sent = set(p[0]["keys"])
    dated = dict(SCL26, exright_date="2026-11-20", record_date="2026-11-23", total_value="1.2E11", issue_volumn="6000000")
    d = B("2026-10-23", POS, [dated], sent, is_hol)
    ck("P → có ngày sau đó ⇒ báo lại DATED dù đã ANNOUNCE", len(d) == 1 and d[0]["stage"] == "DATED", d)
    ck("DATED có giá 20.000 + tiền 43.060.000đ", "43,060,000đ" in (d[0]["text"] if d else ""), d)
    moved = dict(dated, exright_date="2026-11-27")
    ck("đổi ngày GDKHQ ⇒ báo lại", len(B("2026-10-24", POS, [moved], sent | set(d[0]["keys"]), is_hol)) == 1)
    ck("không giữ mã ⇒ im", B("2025-10-10", {"SpaceX": {"FPT": 1}}, [SCL25], set(), is_hol) == [])
    ck("trạng thái N (không thực hiện) ⇒ im", B("2025-10-10", POS, [dict(SCL25, issue_status_code="N")], set(), is_hol) == [])
    dv = B("2025-10-10", POS, [dict(SCL25, issue_method_code="DIV")], set(), is_hol)
    ck("29/10: DIV cổ phiếu ⇒ BÁO mức INFO (không còn im), không có 'được mua'",
       len(dv) == 1 and "INFO" in dv[0]["text"] and "CỔ TỨC BẰNG CP" in dv[0]["text"] and "được mua" not in dv[0]["text"], dv)
    ck("hồi cứu: sự kiện công bố SAU asof ⇒ im (không nhìn trước)", B("2025-10-13", POS, [SCL26], set(), is_hol) == [])
    ck("value_per_share có ⇒ ưu tiên", R.issue_price(dict(SCL25, value_per_share="10000")) == 10000.0)
    inner_b(R, B)
    inner_capraise(R, B)
    inner_main(R)
    n = sum(1 for x in RESULTS if not x)
    print("RESULT:", "PASS" if not n else "FAIL")
    return 0 if not n else 1


# ---- B1: dòng P xác sống — fixture thật đọc từ tav2_bq.corporate_action 2026-10-22
DSC_P1 = {"id": "67f70fd690c07f62ae3f2a46", "ticker": "DSC", "issue_method_code": "Rights", "issue_status_code": "P",
          "event_status": "announced", "exright_date": None, "record_date": None, "public_date": "2025-09-24",
          "exercise_ratio": "0.17251827", "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}
DSC_P2 = dict(DSC_P1, id="68dc754082ba4d1dc754b816", public_date="2025-09-30")
DSC_D = dict(DSC_P1, id="68dc754082ba4d1dc754b817", issue_status_code="D", event_status="executed",
             exright_date="2025-10-03", public_date="2025-09-30", total_value="3.5338458E11", issue_volumn="35338458")
PAN_P = dict(DSC_P1, id="6708f3f60ec61045ab800500", ticker="PAN", public_date="2022-06-06", exercise_ratio="0.5")
ADG_P = dict(DSC_P1, id="6708f3f70ec61045ab80079c", ticker="ADG", public_date="2022-06-27", exercise_ratio="0.352")


def inner_b(R, B):
    pd = {"SpaceX": {"DSC": 1000, "PAN": 1000, "ADG": 1000, "SCL": 14000}}
    ck("DSC: D đã GDKHQ cùng tỉ lệ ⇒ 2 dòng P xác sống KHÔNG báo", B("2025-10-14", pd, [DSC_P1, DSC_P2, DSC_D], set(), is_hol) == [])
    ck("DSC: is_zombie_p đúng 2 dòng P, không phải dòng D",
       [R.is_zombie_p(x, [DSC_P1, DSC_P2, DSC_D], "2025-10-14") for x in (DSC_P1, DSC_P2, DSC_D)] == [True, True, False])
    ck("DSC: D CHƯA tới GDKHQ ⇒ dòng P chưa bị coi là xác sống (đúng đặc tả ≤ asof)",
       not R.is_zombie_p(DSC_P2, [DSC_P2, DSC_D], "2025-10-01"))
    ck("DSC: khác tỉ lệ ⇒ không phải xác sống", not R.is_zombie_p(dict(DSC_P2, exercise_ratio="0.3"), [DSC_P2, DSC_D], "2025-10-14"))
    ck("P công bố SAU GDKHQ của D (đợt mới cùng tỉ lệ) ⇒ KHÔNG xác sống",
       not R.is_zombie_p(dict(DSC_P2, public_date="2025-10-20"), [DSC_D], "2025-10-30"))
    st = B("2026-10-22", pd, [PAN_P, ADG_P], set(), is_hol)
    ck("PAN/ADG 2022 ⇒ đúng 1 tin STALE gộp, không ANNOUNCE", len(st) == 1 and st[0]["stage"] == "STALE", st)
    tx = st[0]["text"] if st else ""
    ck("tin STALE nói 'nghi BỎ DỞ' + kiểm VSDC + ngày công bố 2022", all(x in tx for x in ("BỎ DỞ", "VSDC", "2022-06-06", "2022-06-27")), tx)
    ck("STALE dedupe sau khi gửi", B("2026-10-23", pd, [PAN_P, ADG_P], set(st[0]["keys"]), is_hol) == [])
    pa = B("2022-06-10", pd, [PAN_P], set(), is_hol)
    ck("hồi cứu 2022-06-10: PAN còn mới ⇒ ANNOUNCE có public_date", len(pa) == 1 and pa[0]["stage"] == "ANNOUNCE"
       and "công bố 2022-06-06" in pa[0]["text"], pa)
    sc = B("2026-10-22", pd, [SCL25, SCL26], set(), is_hol)
    ck("SCL 2026: D 2025 khác tỉ lệ + P mới ⇒ VẪN đúng 1 ANNOUNCE", len(sc) == 1 and sc[0]["stage"] == "ANNOUNCE"
       and "công bố 2026-09-08" in sc[0]["text"] and "2,153 cp" in sc[0]["text"], sc)
    tt = B("2025-10-10", POS, [SCL25], set(), is_hol)[0]["text"]
    ck("B4: không còn 'Luật 21/10' (máy KHÔNG áp luật)", "Luật 21/10" not in tt, tt)
    ck("B4 (sau X1 merge): nói bot TỰ giữ lệnh thoát LAG + nếu là mã LAG + cách ack, KHÔNG còn 'CHƯA tự giữ'/'HOLD TAY'",
       all(x in tt for x in ("Bot TỰ giữ lệnh thoát", "nếu là mã LAG", "lag_rights_exit_hold.py --record"))
       and "CHƯA tự giữ" not in tt and "HOLD TAY" not in tt, tt)
    ck("29/10 câu chữ: nêu user CÓ THỂ thoái bằng plan; KHÔNG cố định tên mã/ngày cụ thể trong mẫu định kỳ",
       all(x in tt for x in ("KHÔNG cấm thoái", "thoái bằng plan")) and "SCL là ngoại lệ" not in tt and "29/10/2026" not in tt, tt)
    # B2
    ml = {"SpaceX": {"file": "active_nav_SpaceX.json", "computed_at": "2026-10-20"},
          "ZaloPay": {"file": "active_nav_ZaloPay.json", "computed_at": "2026-10-21"}}
    notes = R.position_health("2026-10-22", ml, ["SpaceX", "ZaloPay"], is_hol)
    ck("tươi: SpaceX 10-20 < phiên trước 10-21 ⇒ cũ; ZaloPay 10-21 ⇒ tươi", ml["SpaceX"]["stale"] and not ml["ZaloPay"]["stale"]
       and len(notes) == 1, notes)
    ck("thiếu account live ⇒ có lý do", any("thiếu" in x and "ZaloPay" in x for x in R.position_health("2026-10-22", {"SpaceX": dict(ml["SpaceX"], computed_at="2026-10-21")}, ["SpaceX", "ZaloPay"], is_hol)))
    ck("labels None ⇒ có lý do", any("danh sách account live" in x for x in R.position_health("2026-10-22", {}, None, is_hol)))
    ck("phiên trước bỏ qua cuối tuần/lễ (T2 10-13-2025 ⇒ T6 10-10)", R.prev_session("2025-10-13", is_hol) == "2025-10-10")
    ml2 = {"SpaceX": {"file": "active_nav_SpaceX.json", "computed_at": "2025-10-01", "stale": True}}
    tm = B("2025-10-10", POS, [SCL25], set(), is_hol, ml2, ["SpaceX: computed_at=2025-10-01 cũ"])[0]["text"]
    ck("tin có computed_at + nguồn + 'VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE'",
       all(x in tm for x in ("computed_at=2025-10-01", "active_nav_SpaceX.json", "VỊ THẾ CÓ THỂ CŨ — tự kiểm trên DNSE")), tm)


# ---- 29/10: tăng vốn MỌI phương thức (capital_raise_lib) — fixture số THẬT đọc tav2_bq.corporate_action 2026-10-29
MBB_DIV = {"id": "mbbdiv202608", "ticker": "MBB", "issue_method_code": "DIV", "issue_status_code": "D",
           "event_status": "executed", "exright_date": "2026-08-11", "record_date": "2026-08-12",
           "public_date": "2026-08-06", "exercise_ratio": "0.15", "value_per_share": None,
           "total_value": "0.0", "issue_volumn": "0"}
MBB_RT = dict(MBB_DIV, id="mbbrt202608", issue_method_code="Rights", exercise_ratio="0.1")
PP_SIM = {"id": "ppsim0001", "ticker": "AAA", "issue_method_code": "PP", "issue_status_code": "P",
          "event_status": "announced", "exright_date": None, "record_date": None, "public_date": "2026-10-20",
          "exercise_ratio": "0", "value_per_share": None, "total_value": "1.5E11", "issue_volumn": "10000000"}
ESOP_SIM = dict(PP_SIM, id="esop0001", issue_method_code="EMPL", exercise_ratio="0.05", total_value="5.0E9",
                issue_volumn="500000", exright_date="2026-11-10", record_date="2026-11-11")
SCL_ESOP_P = {"id": "6a0516165b1fb4c98c3ab29f", "ticker": "SCL", "issue_method_code": "EMPL", "issue_status_code": "P",
              "event_status": "announced", "exright_date": None, "record_date": None, "public_date": "2026-05-07",
              "exercise_ratio": "0.021", "value_per_share": None, "total_value": "0.0", "issue_volumn": "0"}


def inner_capraise(R, B):
    import capital_raise_lib as L
    saved = R.fetch_issuance
    R.fetch_issuance = lambda tk: [MBB_DIV, MBB_RT, PP_SIM]
    try:
        ck("fetch_rights GIỮ hợp đồng chỉ-Rights (lag_rights_exit_hold/daily_nav_snapshot dựa vào)",
           [r["id"] for r in R.fetch_rights({"MBB"})] == ["mbbrt202608"])
    finally:
        R.fetch_issuance = saved
    pm = {"SpaceX": {"MBB": 1000}}
    a = B("2026-08-07", pm, [MBB_DIV], set(), is_hol)
    t = a[0]["text"] if a else ""
    ck("MBB cổ tức CP 15% ⇒ 1 tin INFO, pha loãng 15.00%, ngày chốt còn 3 phiên", len(a) == 1 and "INFO" in t
       and "15.00%" in t and "2026-08-12 (còn 3 phiên)" in t and "luồng corp-action" in t, t)
    ck("INFO không bao giờ REMIND (còn 1 phiên)", all(x["stage"] != "REMIND" for x in B("2026-08-07", pm, [MBB_DIV], set(a[0]["keys"]) if a else set(), is_hol))
       and B("2026-08-07", pm, [MBB_DIV], set(a[0]["keys"]) if a else set(), is_hol) == [])
    r = B("2026-08-07", pm, [MBB_RT], {"mbbrt202608|announce", "mbbrt202608|dated|2026-08-11"}, is_hol)
    ck("Rights cùng ngày VẪN REMIND (đối chứng: REMIND chỉ dành cho Rights)", len(r) == 1 and r[0]["stage"] == "REMIND", r)
    pa = {"SpaceX": {"AAA": 2000}, "ZaloPay": {"AAA": 500}}
    p = B("2026-10-22", pa, [PP_SIM], set(), is_hol, prices={"AAA": 20000.0}, oshares={"AAA": 50_000_000})
    tp = p[0]["text"] if p else ""
    ck("riêng lẻ giả lập: giữ ở 2 account ⇒ ĐÚNG 1 tin gộp, nêu cả 2", len(p) == 1 and "SpaceX: giữ 2,000" in tp
       and "ZaloPay: giữ 500" in tp, p)
    ck("riêng lẻ: ratio=0 ⇒ % từ issue_volumn/OShares = 20.00%; giá 15.000 = 75% thị giá 20.000; WARN",
       all(x in tp for x in ("20.00%", "15,000đ = 75% thị giá 20,000đ", "WARN", "PHÁT HÀNH RIÊNG LẺ")), tp)
    ck("riêng lẻ: nêu mục đích vốn KHÔNG có trong nguồn + 'bot KHÔNG tự bán'", "mục đích sử dụng vốn" in tp
       and "bot KHÔNG tự bán" in tp and "được mua" not in tp, tp)
    ck("không OShares + ratio 0 ⇒ 'CHƯA RÕ' (không đoán 0)", "pha loãng CHƯA RÕ" in B("2026-10-22", pa, [PP_SIM], set(), is_hol)[0]["text"])
    e = B("2026-11-06", {"SpaceX": {"AAA": 100}}, [ESOP_SIM], {"esop0001|announce", "esop0001|dated|2026-11-10"}, is_hol)
    ck("ESOP: đã ANNOUNCE+DATED, còn 1 phiên ⇒ im (không REMIND)", e == [], e)
    ck("mã không giữ ⇒ im (riêng lẻ)", B("2026-10-22", {"SpaceX": {"FPT": 1}}, [PP_SIM], set(), is_hol) == [])
    old = dict(PP_SIM, id="ppold", public_date="2026-01-02")
    st = B("2026-10-22", pa, [old], set(), is_hol)
    ck("riêng lẻ P xác sống > 183 ngày ⇒ chỉ STALE, không ANNOUNCE", len(st) == 1 and st[0]["stage"] == "STALE", st)
    zp = dict(PP_SIM, id="zp")
    zd = dict(PP_SIM, id="zd", issue_status_code="D", exright_date="2026-10-21", public_date="2026-10-21")
    ck("zombie theo CÙNG phương thức: D riêng lẻ cùng tỉ lệ ⇒ P bị bỏ", B("2026-10-22", pa, [zp, zd], set(), is_hol) == [])
    ck("zombie KHÁC phương thức (D là ESOP) ⇒ P riêng lẻ VẪN báo",
       len(B("2026-10-22", pa, [zp, dict(zd, issue_method_code="EMPL")], set(), is_hol)) == 1)
    ck("mã phương thức lạ ⇒ WARN (fail-closed)", L.severity({"issue_method_code": "NEWCODE"}) == "WARN")
    # SCL ca thật: D 2025 tỉ lệ 35,7% + P quyền mua 15,38% (public 09-08, ingest 10-28) + P ESOP 2,1%
    sc = B("2026-10-29", {"SpaceX": {"SCL": 1100}, "ZaloPay": {"SCL": 700}}, [SCL25, SCL26, SCL_ESOP_P], set(), is_hol)
    stg = sorted((x["text"].split("**")[2][:12], x["stage"]) for x in sc)
    ck("SCL 29/10: 2 tin ANNOUNCE (quyền mua + ESOP), D 2025 đã GDKHQ im", len(sc) == 2 and
       all(x["stage"] == "ANNOUNCE" for x in sc), stg)
    ck("SCL quyền mua: 2 account trong 1 tin, 169 + 107 cp", any("169 cp" in x["text"] and "107 cp" in x["text"] for x in sc), sc)
    # Lớp A (pre-entry) — thuần
    fl, wa = L.pre_entry_flags([SCL25, SCL26], "2026-10-23", 38_836_815, 0.734)
    ck("A: SCL 23/10 (trước vào lệnh 26/10) ⇒ WARNING CAPITAL_RAISE_PENDING (KHÔNG cờ), kèm OShares +73.4%",
       fl == [] and [c for c, _ in wa] == ["CAPITAL_RAISE_PENDING"] and "+73.4%" in wa[0][1] and "15.38%" in wa[0][1], (fl, wa))
    fl, wa = L.pre_entry_flags([SCL25], "2025-10-16", None, None)
    ck("A: SCL quyền mua 35,7% GDKHQ 2025-10-17 — asof 2025-10-16 chưa GDKHQ ⇒ warning PENDING, không cờ",
       fl == [] and [c for c, _ in wa] == ["CAPITAL_RAISE_PENDING"], (fl, wa))
    fl, wa = L.pre_entry_flags([SCL25], "2025-11-01", None, None)
    ck("A: asof 2025-11-01 (đã GDKHQ 16 ngày) ⇒ warning CAPITAL_RAISE_12M (+35.7% > 10%), không cờ",
       fl == [] and [c for c, _ in wa] == ["CAPITAL_RAISE_12M"] and "+35.7%" in wa[0][1], (fl, wa))
    ck("A: quá 365 ngày ⇒ hết cảnh báo 12M", L.pre_entry_flags([SCL25], "2026-10-18", None, None) == ([], []))
    esop5 = dict(ESOP_SIM, issue_status_code="D", exright_date="2026-09-01")
    ck("A: ESOP thuần 5% đã thực hiện ⇒ KHÔNG cảnh báo 12M (ngưỡng 10%)", L.pre_entry_flags([esop5], "2026-10-01") == ([], []))
    ck("A: MBB cổ tức CP 15% ĐÃ thực hiện (INFO) ⇒ KHÔNG tính vào pha loãng thu tiền 12M",
       L.pre_entry_flags([MBB_DIV], "2026-10-01") == ([], []))
    b11 = dict(esop5, exercise_ratio="0.11")
    ck("A: 11% thu tiền đã thực hiện ⇒ cảnh báo 12M (không cờ)",
       L.pre_entry_flags([b11], "2026-10-01")[0] == [] and [c for c, _ in L.pre_entry_flags([b11], "2026-10-01")[1]] == ["CAPITAL_RAISE_12M"])
    b10 = dict(esop5, exercise_ratio="0.10")
    ck("A: đúng 10% ⇒ KHÔNG cảnh báo (> chứ không ≥)", L.pre_entry_flags([b10], "2026-10-01") == ([], []))
    fl, wa = L.pre_entry_flags([dict(MBB_DIV, exright_date="2026-11-20")], "2026-10-23")
    ck("A: cổ tức CP sắp tới ⇒ chỉ warning CAPITAL_RAISE_INFO, không cờ", fl == [] and [c for c, _ in wa] == ["CAPITAL_RAISE_INFO"], (fl, wa))
    fl, wa = L.pre_entry_flags([old], "2026-10-22")
    ck("A: P nghi bỏ dở ⇒ chỉ warning", fl == [] and [c for c, _ in wa] == ["CAPITAL_RAISE_NGHI_BO_DO"], (fl, wa))
    ck("A: trạng thái N ⇒ không gì", L.pre_entry_flags([dict(PP_SIM, issue_status_code="N")], "2026-10-22") == ([], []))
    ck("A: công bố SAU asof ⇒ không nhìn trước", L.pre_entry_flags([SCL26], "2026-09-07") == ([], []))


# ---- N1: main() end-to-end trong tmpdir (notify/state/nav đều trỏ vào tmp)
NOTIFY_SH = """#!/bin/bash
D="$(dirname "$0")"; n=$(cat "$D/count" 2>/dev/null || echo 0); n=$((n+1)); echo $n > "$D/count"
[ "$n" = "${MIKE_TEST_FAIL_AT:-0}" ] && { echo "stub fail $n" >&2; exit 7; }
printf '%s\n----\n' "$1" >> "$D/log"
"""


def inner_main(R):
    HPG = dict(SCL25, id="hpgtest0001", ticker="HPG", public_date="2025-10-09")
    td = tempfile.mkdtemp()
    try:
        nav = os.path.join(td, "nav")
        os.makedirs(nav)

        def wnav(acct, qty, ca):
            with open(os.path.join(nav, f"active_nav_{acct}.json"), "w") as fh:
                json.dump({"account": acct, "computed_at": ca,
                           "positions": [{"ticker": t, "qty": q} for t, q in qty.items()]}, fh)
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-09")
        wnav("ZaloPay", {"FPT": 50}, "2025-10-09")
        sh = os.path.join(td, "notify.sh")
        open(sh, "w").write(NOTIFY_SH)
        os.chmod(sh, 0o755)
        state = os.path.join(td, "state.json")
        R.fetch_issuance = lambda tk: [HPG, SCL25]
        R.fetch_oshares = lambda tk: {}
        R.live_labels = lambda: ["SpaceX", "ZaloPay"]

        def run(fail_at=0, extra=(), reset=True, st=state):
            if reset:
                for f in ("count", "log"):
                    if os.path.exists(os.path.join(td, f)):
                        os.remove(os.path.join(td, f))
            os.environ["MIKE_RIGHTS_ALERT_NOTIFY"] = f"bash {sh}"
            os.environ["MIKE_TEST_FAIL_AT"] = str(fail_at)
            sys.argv = ["x", "--asof", "2025-10-10", "--send", "--state", st, "--nav-glob", os.path.join(nav, "active_nav_*.json"), *extra]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = R.main()
            cnt = int(open(os.path.join(td, "count")).read()) if os.path.exists(os.path.join(td, "count")) else 0
            log = open(os.path.join(td, "log")).read() if os.path.exists(os.path.join(td, "log")) else ""
            return rc, buf.getvalue(), cnt, log

        rc, out, cnt, log = run(fail_at=1)
        ck("main: gửi lỗi tin đầu ⇒ rc=1, KHÔNG ghi state", rc == 1 and not os.path.exists(state) and "CHƯA ghi state" in out, (rc, out))
        rc, out, cnt, log = run(fail_at=2)
        keys = set(json.load(open(state))["sent"]) if os.path.exists(state) else set()
        ck("main: gửi lỗi GIỮA vòng ⇒ rc=1, state chỉ chứa tin đã gửi (HPG)", rc == 1 and keys == {"hpgtest0001|announce", "hpgtest0001|dated|2025-10-17"}, (rc, keys))
        rc, out, cnt, log = run()
        keys = set(json.load(open(state))["sent"])
        ck("main: chạy lại sau lỗi ⇒ chỉ gửi tin còn thiếu (SCL), rc=0, state đủ", rc == 0 and cnt == 1 and "**SCL**" in log
           and f"{SCL25['id']}|announce" in keys, (rc, cnt, keys))
        rc, out, cnt, log = run()
        ck("main: idempotent lần 2 ⇒ 0 lần gửi, rc=0", rc == 0 and cnt == 0, (rc, cnt))
        rc, out, cnt, log = run(st=os.path.join(td, "fresh_state.json"))
        ck("main: vị thế tươi + đủ account ⇒ rc=0; tin nêu computed_at nguồn", rc == 0 and cnt == 2 and "computed_at=2025-10-09" in log, (rc, cnt))
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-01")
        rc, out, cnt, log = run(st=os.path.join(td, "stale_state.json"))
        ck("main: file vị thế CŨ ⇒ VẪN gửi nhưng rc=3 + 'VỊ THẾ CÓ THỂ CŨ'", rc == 3 and cnt == 2 and "VỊ THẾ CÓ THỂ CŨ" in log, (rc, cnt, out))
        wnav("SpaceX", {"SCL": 14000, "HPG": 1000}, "2025-10-09")
        os.remove(os.path.join(nav, "active_nav_ZaloPay.json"))
        rc, out, cnt, log = run(st=os.path.join(td, "miss_state.json"))
        ck("main: thiếu file account live (ZaloPay) ⇒ rc=3 + nêu thiếu", rc == 3 and "thiếu file vị thế account live: ZaloPay" in out, (rc, out))
        def boom():
            raise RuntimeError("accounts.json hỏng")
        R.live_labels = boom
        wnav("ZaloPay", {"FPT": 50}, "2025-10-09")
        rc, out, cnt, log = run(st=os.path.join(td, "boom_state.json"))
        ck("main: live_dnse_labels lỗi ⇒ rc=3 + in lỗi thật (§29)", rc == 3 and "accounts.json hỏng" in out, (rc, out))
        for f in os.listdir(nav):
            os.remove(os.path.join(nav, f))
        rc, out, cnt, log = run(st=os.path.join(td, "none_state.json"))
        ck("main: không có file vị thế nào ⇒ rc=2, không gửi gì", rc == 2 and cnt == 0, (rc, cnt))
    finally:
        shutil.rmtree(td, ignore_errors=True)


RA, LB = "rights_issue_alert.py", "capital_raise_lib.py"
MUTANTS = [
    (LB, '        if (r.get("public_date") or "")[:10] > asof:', '        if False:'),
    (LB, '        if ex and ex <= asof:\n            continue', '        if ex and ex < asof:\n            continue'),
    (RA, "            if rights and left <= REMIND_SESSIONS:", "            if rights and left < REMIND_SESSIONS:"),
    (RA, "            if rights and left <= REMIND_SESSIONS:", "            if left <= REMIND_SESSIONS:"),
    (RA, '        stages = [("ANNOUNCE", f"{r[\'id\']}|announce")]', "        stages = []"),
    (RA, '            stages.append(("DATED", f"{r[\'id\']}|dated|{ex}"))', '            stages.append(("DATED", f"{r[\'id\']}|dated"))'),
    (RA, 'f"{r[\'id\']}|remind|{ex}|{asof}"', 'f"{r[\'id\']}|remind|{ex}"'),
    (RA, "                n = math.floor(q * ratio + 1e-9)", "                n = round(q * ratio)"),
    (RA, '        if d.weekday() < 5 and not is_holiday(d):\n            n += 1', '        if d.weekday() < 5:\n            n += 1'),
    (LB, '    return r.get("issue_status_code") == "N" or r.get("event_status") == "not_executed"', '    return r.get("event_status") == "not_executed"'),
    (LB, "    return tv / vol if tv > 0 and vol > 0 else None", "    return None"),
    (LB, "ex and ex <= asof and ex > pub and _same_ratio(o, r):", "ex and ex <= asof and ex > pub:"),
    (LB, "ex and ex <= asof and ex > pub and _same_ratio(o, r):", "ex and ex <= asof and _same_ratio(o, r):"),
    (LB, '                and o.get("issue_method_code") == r.get("issue_method_code") \\\n', ""),
    (LB, "    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > STALE_P_DAYS",
     "    return (dt.date.fromisoformat(asof) - dt.date.fromisoformat(pub)).days > 10 ** 6"),
    (LB, "        if is_zombie_p(r, rows, asof):", "        if False:"),
    (LB, '    return "INFO" if m in INFO_METHODS else "WARN"', '    return "WARN" if m in WARN_METHODS else "INFO"'),
    (LB, "    return vol / os_ if vol > 0 and os_ > 0 else None", "    return 0.0"),
    (LB, "    if g > RAISE_12M_X + 1e-9:", "    if g >= RAISE_12M_X:"),
    (LB, "RAISE_12M_X = 0.10 ", "RAISE_12M_X = 0.05 "),
    (LB, '    lo = (dt.date.fromisoformat(asof) - dt.timedelta(days=WINDOW_12M_DAYS)).isoformat()',
     '    lo = "0000"'),
    (LB, '        if is_dead(r) or severity(r) != "WARN" or r.get("issue_status_code") != "D" or not (lo < ex <= asof):',
     '        if is_dead(r) or r.get("issue_status_code") != "D" or not (lo < ex <= asof):'),
    (LB, '    w = [r for r in live if severity(r) == "WARN"]', '    w = list(live)'),
    (RA, '        rec_s = f"{rec} (còn {sessions_to(asof, rec, is_holiday)} phiên)" if rec and rec > asof else (rec or "CHƯA CÓ")',
     '        rec_s = rec or "CHƯA CÓ"'),
    (RA, "        return f\"giá phát hành: {px:,.0f}đ = {px / mkt:.0%} thị giá {mkt:,.0f}đ (giá active_nav)\"",
     "        return f\"giá phát hành: {px:,.0f}đ\""),
    (RA, '        m["stale"] = (m.get("computed_at") or "")[:10] < cutoff', '        m["stale"] = False'),
    (RA, "    elif [lb for lb in labels if lb not in meta]:", "    elif False:"),
    (RA, "    stale_rc = 3 if notes else 0", "    stale_rc = 0"),
    (RA, "        return 2\n    try:", "        return 0\n    try:"),
    (RA, "        if r.returncode != 0:", "        if False:"),
    (RA, '        r = subprocess.run(notify + [al["text"], TRADING_DAILY_THREAD], capture_output=True, text=True)',
     '        _save_sent(a.state, sent | set(al["keys"]))\n        r = subprocess.run(notify + [al["text"], TRADING_DAILY_THREAD], capture_output=True, text=True)'),
    (RA, "        _save_sent(a.state, sent)              # ghi NGAY sau mỗi lần gửi (§5)", "        pass"),
    (RA, "    sent = _load_sent(a.state) if a.send else set()", "    sent = set()"),
    (RA, "        labels = None\n", "        labels = []\n"),
    (RA, "        holders = [(lb, p[tk]) for lb, p in sorted(positions.items()) if p.get(tk, 0) > 0]",
     "        holders = [(lb, p.get(tk, 0)) for lb, p in sorted(positions.items())]"),
    (RA, '    held = {t for p in positions.values() for t, q in p.items() if q > 0}', '    held = {r.get("ticker") for r in rows}'),
    (RA, '    return [r for r in fetch_issuance(tickers) if r.get("issue_method_code") == "Rights"]',
     '    return fetch_issuance(tickers)'),
]


def run_mutants():
    bad = 0
    for i, (fn, old, new) in enumerate(MUTANTS, 1):
        td = tempfile.mkdtemp()
        try:
            for f in (RA, LB):
                shutil.copy(os.path.join(HERE, f), td)
            shutil.copy(os.path.abspath(__file__), td)
            p = os.path.join(td, fn)
            src = open(p).read()
            if src.count(old) != 1:
                print(f"  ❌ mutant {i} ({fn}): chuỗi gốc không khớp đúng {src.count(old)}≠1 lần — sửa MUTANTS")
                bad += 1
                continue
            open(p, "w").write(src.replace(old, new))
            r = subprocess.run([sys.executable, os.path.join(td, os.path.basename(__file__)), "--inner"],
                               capture_output=True, text=True, timeout=120)
            killed = r.returncode != 0
            print(f"  {'KILLED' if killed else 'SURVIVED'} — mutant {i} ({fn}): {old.strip()[:70]!r}")
            bad += 0 if killed else 1
        finally:
            shutil.rmtree(td, ignore_errors=True)
    print(f"MUTANTS: {len(MUTANTS) - bad}/{len(MUTANTS)} killed")
    return bad


def main():
    if "--inner" in sys.argv:
        sys.path.insert(0, HERE)
        return run_inner()
    rc = 0
    for label, env in (("env -u TZ", {k: v for k, v in os.environ.items() if k != "TZ"}),
                       ("TZ=Pacific/Kiritimati", dict(os.environ, TZ="Pacific/Kiritimati")),
                       ("TZ=America/New_York", dict(os.environ, TZ="America/New_York"))):
        print(f"=== {label} ===")
        env["MIKE_BOT_TEST_MODE"] = "1"
        rc |= subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env).returncode
    print("=== mutants ===")
    if run_mutants():
        rc |= 1
    print("TỔNG:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
