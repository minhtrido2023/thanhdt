"""Selfcheck HERMETIC cho build_treasury_share_events.py — 0 lan cham BigQuery.

Moi fixture la du lieu bia dat trong file nay; khong doc CSV, khong doc mang.
Chay:  $DNA_PYEXE treasury_share_events_selfcheck.py
       env -u TZ $DNA_PYEXE treasury_share_events_selfcheck.py     # TZ-doc-lap
       TZ=America/New_York $DNA_PYEXE treasury_share_events_selfcheck.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_treasury_share_events as M  # noqa: E402

PASS = FAIL = 0


def ck(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL  {name} {extra}")


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
        return False
    except Exception:
        return True


# ------------------------------------------------------------------- fixtures
def ev(ticker, date, at, delta=None, n_null=0, n_rows=1, n_distinct=1, news="1"):
    return dict(ticker=ticker, public_date=date, action_type=at, shares_delta=delta,
                n_rows=n_rows, n_null=n_null, n_distinct=n_distinct, news_ids=news,
                first_public_datetime=f"{date}T17:00:00")


FIX_EVENTS = [
    ev("AAA", "2019-03-01", "buy_done", 100_000),                    # vendor, mua
    ev("BBB", "2020-05-06", "sell_done", -250_000),                  # vendor, ban
    ev("CCC", "2018-02-06", "sell_done", -448_500, n_null=1, n_rows=2, n_distinct=1),  # sibling
    ev("DDD", "2021-02-01", "buy_done", None),                       # -> suy luan
    ev("EEE", "2017-06-20", "buy_done", 0),                          # vendor cong bo 0
    ev("FFF", "2022-09-22", "sell_done", None),                      # -> UNSIZED co ly do
    ev("GGG", "2023-01-05", "buy_done", None),                       # -> UNSIZED khong ly do
    # --- B1: CUNG MOT giao dich that bi dang o 2 ngay (ca NDN + CTD do tu BQ that)
    ev("NDN", "2018-05-17", "buy_done", 1_000_000),   # 2 dong vendon giong het, cach 1 ngay
    ev("NDN", "2018-05-18", "buy_done", 1_000_000),
    ev("CTD", "2021-02-01", "buy_done", None),        # dong suy tu OShares (-2.008.900)
    ev("CTD", "2021-02-03", "buy_done", 2_000_000),   # dong vendor (-2.000.000), cach 2 ngay
    # --- KHONG duoc gop: 2 dot mua THAT cung so luong, cach 274 ngay (ca HWS that)
    ev("HWS", "2018-09-24", "buy_done", 58_500),
    ev("HWS", "2019-06-25", "buy_done", 58_500),
    # --- KHONG duoc gop: gan ngay nhung so lech xa (so that cua GDT, lech 65,6%)
    ev("GDT", "2016-08-11", "buy_done", 5_700),
    ev("GDT", "2016-08-13", "buy_done", 1_960),
    # --- chain guard: 3 dong cung so, moi buoc 10 ngay (< 14) nhung tong trai 20 ngay
    ev("CHN", "2020-01-01", "buy_done", 7_000),
    ev("CHN", "2020-01-11", "buy_done", 7_000),
    ev("CHN", "2020-01-21", "buy_done", 7_000),
    # --- 2 dong UNSIZED sat nhau (dang that: 18 cap <=14 ngay tren BQ, vd STB sell_done):
    #     delta NULL nen KHONG so duoc theo gia tri => tuyet doi khong keo vao dedup
    ev("HHH", "2021-07-23", "sell_done", None),
    ev("HHH", "2021-07-30", "sell_done", None),
    # --- N1: ca suy luan phai noi cua so ra 2 quy (do duoc 176-188 ngay tren 5/33 ca that)
    ev("III", "2020-04-06", "buy_done", None),
]
FIX_INFERRED = {
    ("DDD", "2021-02-01", "buy_done"): {"outstanding_delta": -2_008_900,
                                        "confirmed_asof": "2021-02-05",
                                        "window_days": 94},    # cua so 1 quy
    ("CTD", "2021-02-01", "buy_done"): {"outstanding_delta": -2_008_900,
                                        "confirmed_asof": "2021-02-05",
                                        "window_days": 94},
    ("III", "2020-04-06", "buy_done"): {"outstanding_delta": -11_000,
                                        "confirmed_asof": "2020-07-24",
                                        "window_days": 184},   # cua so 2 quy (ca DRH that)
    ("FFF", "2022-09-22", "sell_done"): {"unsized_reason": "NO_MOVE"},
}
LOADED = "2026-09-18T17:00:00+07:00"

print("=" * 70)
print("1. event_id — deterministic, duy nhat, on dinh qua lan chay")
print("=" * 70)
i1 = M.event_id("VRE", "2019-12-19", "buy_done")
ck("prefix TRSY-", i1.startswith("TRSY-"))
ck("do dai 21", len(i1) == 21, i1)
ck("deterministic", i1 == M.event_id("VRE", "2019-12-19", "buy_done"))
ck("doi ticker -> doi id", i1 != M.event_id("VRF", "2019-12-19", "buy_done"))
ck("doi ngay -> doi id", i1 != M.event_id("VRE", "2019-12-20", "buy_done"))
ck("doi action -> doi id", i1 != M.event_id("VRE", "2019-12-19", "sell_done"))
ck("gia tri co dinh", i1 == "TRSY-" + __import__("hashlib").sha1(
    b"VRE|2019-12-19|buy_done").hexdigest()[:16], i1)

print("=" * 70)
print("2. vendor_outstanding_delta — LAT DAU dung mot lan, sai dau thi keu")
print("=" * 70)
ck("buy_done 100k -> luu hanh -100k", M.vendor_outstanding_delta(100_000, "buy_done") == -100_000)
ck("sell_done -250k -> luu hanh +250k", M.vendor_outstanding_delta(-250_000, "sell_done") == 250_000)
ck("0 -> 0", M.vendor_outstanding_delta(0, "buy_done") == 0)
ck("None -> None", M.vendor_outstanding_delta(None, "sell_done") is None)
ck("float lam tron", M.vendor_outstanding_delta(100_000.0, "buy_done") == -100_000)
ck("buy_done AM -> ValueError", raises(M.vendor_outstanding_delta, -5, "buy_done"))
ck("sell_done DUONG -> ValueError", raises(M.vendor_outstanding_delta, 5, "sell_done"))
ck("khong lat 2 lan", M.vendor_outstanding_delta(
    M.vendor_outstanding_delta(100_000, "buy_done") and 100_000, "buy_done") == -100_000)

print("=" * 70)
print("3. parse_quarter_window")
print("=" * 70)
ck("doc duoc cua so", M.parse_quarter_window(
    "dOSh=6,222,000 (0.38%) q2019-10-22..2020-01-21") == ("2019-10-22", "2020-01-21"))
ck("chuoi khong co cua so -> None", M.parse_quarter_window("OShares bat dong qua 2 quy") is None)
ck("chuoi rong -> None", M.parse_quarter_window("") is None)
ck("None -> None", M.parse_quarter_window(None) is None)

print("=" * 70)
print("4. verify_inferred — RECOMPUTE doc lap, khong tin so Winston vo dieu kien")
print("=" * 70)
ok, rec, why = M.verify_inferred(-2_008_900, 76_292_573, 74_283_673, "buy_done")
ck("khop -> ok", ok and rec == -2_008_900, (ok, rec, why))
ok, rec, why = M.verify_inferred(6_222_000, 1_656_515_277, 1_662_737_277, "sell_done")
ck("sell_done khop -> ok", ok and rec == 6_222_000, (ok, rec, why))
ok, rec, why = M.verify_inferred(-2_008_900, 76_292_573, 76_000_000, "buy_done")
ck("lech so Winston -> tu choi", not ok and "LECH_SO_WINSTON" in why, why)
ok, rec, why = M.verify_inferred(2_008_900, 76_292_573, 78_301_473, "buy_done")
ck("buy_done ma OShares TANG -> tu choi", not ok and why == "SAI_DAU_KY_VONG", why)
ok, rec, why = M.verify_inferred(-2_008_900, 76_292_573, 76_292_573, "buy_done")
ck("OShares bat dong -> tu choi (KHONG thanh 0)", not ok and why == "OSHARES_KHONG_DOI", why)
ck("thieu OShares truoc -> tu choi",
   M.verify_inferred(-1, None, 100, "buy_done")[2] == "THIEU_OSHARES")
ck("thieu OShares sau -> tu choi",
   M.verify_inferred(-1, 100, None, "buy_done")[2] == "THIEU_OSHARES")

print("=" * 70)
print("5. confirmed_asof_of — khong bao gio lac quan hon thuc te")
print("=" * 70)
ck("Release_Date NULL -> time", M.confirmed_asof_of("2020-01-21", None) == "2020-01-21")
ck("Release_Date rong -> time", M.confirmed_asof_of("2020-01-21", "") == "2020-01-21")
ck("Release_Date SAU time -> lay Release_Date",
   M.confirmed_asof_of("2020-01-21", "2020-02-05") == "2020-02-05")
ck("Release_Date TRUOC time -> giu time (khong lui ve som hon)",
   M.confirmed_asof_of("2020-01-21", "2020-01-10") == "2020-01-21")
ck("bang nhau", M.confirmed_asof_of("2020-01-21", "2020-01-21") == "2020-01-21")

print("=" * 70)
print("6. build_rows — 3 TIER KHONG TRON LAN")
print("=" * 70)
rows = M.build_rows(FIX_EVENTS, FIX_INFERRED, LOADED)
by = {r["ticker"]: r for r in rows if r["ticker"] not in
      ("NDN", "CTD", "HWS", "GDT", "CHN", "HHH")}   # nhung ma co >1 dong: dung byk
byk = {(r["ticker"], r["public_date"]): r for r in rows}
ck("du so dong", len(rows) == len(FIX_EVENTS), len(rows))
ck("id duy nhat", len({r["id"] for r in rows}) == len(rows))
ck("cot dung thu tu schema", all(list(r) == M.FIELDS for r in rows))

ck("AAA vendor: source", by["AAA"]["source"] == "VENDOR_PUBLISHED")
ck("AAA vendor: SIZED + high", by["AAA"]["size_status"] == "SIZED"
   and by["AAA"]["confidence"] == "high")
ck("AAA vendor: delta lat dau", by["AAA"]["outstanding_delta"] == -100_000)
ck("AAA vendor: confirmed_asof NULL", by["AAA"]["confirmed_asof"] is None)

ck("CCC sibling: source rieng", by["CCC"]["source"] == "SIBLING_ROW")
ck("CCC sibling: high (so vendor, khong phai suy luan)", by["CCC"]["confidence"] == "high")
ck("CCC sibling: confirmed_asof NULL", by["CCC"]["confirmed_asof"] is None)
ck("CCC sibling: delta lat dau", by["CCC"]["outstanding_delta"] == 448_500)

ck("DDD inferred: source rieng", by["DDD"]["source"] == "OSHARES_DELTA_INFERRED")
ck("DDD inferred: confidence MEDIUM (khong phai high)", by["DDD"]["confidence"] == "medium")
ck("DDD inferred: co confirmed_asof", by["DDD"]["confirmed_asof"] == "2021-02-05")
ck("DDD inferred: SIZED", by["DDD"]["size_status"] == "SIZED")
ck("DDD inferred: giu be rong cua so OShares that (1 quy)",
   by["DDD"]["inferred_window_days"] == 94)
ck("III inferred: cua so 2 quy hien ra SO DO, khong bi lam tron thanh nhan",
   by["III"]["inferred_window_days"] == 184)
ck("BAT BIEN: inferred_window_days CHI co tren OSHARES_DELTA_INFERRED",
   {r["source"] for r in rows if r["inferred_window_days"]} == {"OSHARES_DELTA_INFERRED"})
ck("BAT BIEN: MOI dong suy luan deu co inferred_window_days (khong sot)",
   all(r["inferred_window_days"] for r in rows if r["source"] == "OSHARES_DELTA_INFERRED"))

ck("EEE vendor cong bo 0: SIZED voi delta 0 (khong phai UNSIZED)",
   by["EEE"]["size_status"] == "SIZED" and by["EEE"]["outstanding_delta"] == 0)

ck("FFF UNSIZED: delta None", by["FFF"]["outstanding_delta"] is None)
ck("FFF UNSIZED: KHONG noi suy thanh 0", by["FFF"]["outstanding_delta"] != 0)
ck("FFF UNSIZED: source None", by["FFF"]["source"] is None)
ck("FFF UNSIZED: confidence None", by["FFF"]["confidence"] is None)
ck("FFF UNSIZED: giu ly do cua Winston", by["FFF"]["unsized_reason"] == "NO_MOVE")
ck("GGG UNSIZED khong ly do -> UNKNOWN", by["GGG"]["unsized_reason"] == "UNKNOWN")

ck("BAT BIEN: chi OSHARES_DELTA_INFERRED moi co confirmed_asof",
   {r["source"] for r in rows if r["confirmed_asof"]} == {"OSHARES_DELTA_INFERRED"})
ck("BAT BIEN: chi OSHARES_DELTA_INFERRED moi confidence=medium",
   {r["source"] for r in rows if r["confidence"] == "medium"} == {"OSHARES_DELTA_INFERRED"})
ck("BAT BIEN: UNSIZED <=> delta None",
   all((r["size_status"] == "UNSIZED") == (r["outstanding_delta"] is None) for r in rows))
ck("BAT BIEN: SIZED <=> co source", all((r["size_status"] == "SIZED") == bool(r["source"])
                                        for r in rows))
ck("BAT BIEN: unsized_reason chi tren UNSIZED",
   all(r["size_status"] == "UNSIZED" for r in rows if r["unsized_reason"]))
ck("lineage giu nguyen", by["AAA"]["source_news_ids"] == "1"
   and by["AAA"]["first_public_datetime"] == "2019-03-01T17:00:00")
ck("loaded_at/version dong deu", all(r["loaded_at"] == LOADED
                                     and r["loader_version"] == M.LOADER_VERSION for r in rows))

print("=" * 70)
print("7. build_rows — FAIL LOUD, khong doan bua")
print("=" * 70)
ck("action_type la",
   raises(M.build_rows, [ev("XXX", "2020-01-01", "buy")], {}, LOADED))
ck("su kien TRUNG sau khi gop",
   raises(M.build_rows, [ev("AAA", "2019-03-01", "buy_done", 1),
                         ev("AAA", "2019-03-01", "buy_done", 2)], {}, LOADED))
ck("2 gia tri shares_delta khac nhau -> dung lai",
   raises(M.build_rows, [ev("AAA", "2019-03-01", "buy_done", 1, n_distinct=2, n_rows=2)],
          {}, LOADED))
ck("vi pham dau lan len build_rows",
   raises(M.build_rows, [ev("AAA", "2019-03-01", "buy_done", -1)], {}, LOADED))

print("=" * 70)
print("8. resolve_inferred — noi verify gap loader")
print("=" * 70)
fin = {("DDD", "2020-10-30"): {"oshares": 76_292_573.0, "release_date": None},
       ("DDD", "2021-02-01"): {"oshares": 74_283_673.0, "release_date": "2021-02-05"},
       ("ZZZ", "2020-10-30"): {"oshares": 1_000_000.0, "release_date": None},
       ("ZZZ", "2021-02-01"): {"oshares": 990_000.0, "release_date": None}}
res_ok = [dict(ticker="DDD", public_date="2021-02-01", action_type="buy_done",
               inferred="-2008900", why="dOSh=-2,008,900 (2.63%) q2020-10-30..2021-02-01")]
inf, rej = M.resolve_inferred(res_ok, {}, fin)
ck("ca khop -> vao map", not rej and inf[("DDD", "2021-02-01", "buy_done")][
    "outstanding_delta"] == -2_008_900, rej)
ck("confirmed_asof lay Release_Date muon hon",
   inf[("DDD", "2021-02-01", "buy_done")]["confirmed_asof"] == "2021-02-05")
ck("window_days tinh tu CHINH cua so da verify (2020-10-30..2021-02-01 = 94 ngay)",
   inf[("DDD", "2021-02-01", "buy_done")]["window_days"] == 94,
   inf[("DDD", "2021-02-01", "buy_done")].get("window_days"))
res_bad = [dict(ticker="ZZZ", public_date="2021-02-01", action_type="buy_done",
                inferred="-99999", why="dOSh=-99,999 q2020-10-30..2021-02-01")]
inf, rej = M.resolve_inferred(res_bad, {}, fin)
ck("so Winston lech OShares that -> BI TU CHOI, khong nap", len(rej) == 1 and not inf, (inf, rej))
res_nowin = [dict(ticker="DDD", public_date="2021-02-01", action_type="buy_done",
                  inferred="-2008900", why="khong co cua so")]
inf, rej = M.resolve_inferred(res_nowin, {}, fin)
ck("khong doc duoc cua so -> tu choi", len(rej) == 1 and not inf)
res_nofin = [dict(ticker="QQQ", public_date="2021-02-01", action_type="buy_done",
                  inferred="-1", why="q2020-10-30..2021-02-01")]
inf, rej = M.resolve_inferred(res_nofin, {}, fin)
ck("thieu dong BCTC -> tu choi", len(rej) == 1 and not inf)
inf, rej = M.resolve_inferred([], {("W", "2020-01-01", "buy_done"): {"unsized_reason": "NO_MOVE"}},
                              fin)
ck("ly do UNSIZED di qua nguyen ven", inf[("W", "2020-01-01", "buy_done")]["unsized_reason"]
   == "NO_MOVE")

print("=" * 70)
print("9. same_transaction — luat nhan dien CUNG MOT giao dich")
print("=" * 70)


def r_(tk, d, at, delta):
    return dict(ticker=tk, public_date=d, action_type=at, outstanding_delta=delta)


ck("cach 1 ngay, so giong het -> cung giao dich", M.same_transaction(
    r_("NDN", "2018-05-17", "buy_done", -1_000_000),
    r_("NDN", "2018-05-18", "buy_done", -1_000_000)))
ck("cach 2 ngay, lech 0,44% -> cung giao dich", M.same_transaction(
    r_("CTD", "2021-02-01", "buy_done", -2_008_900),
    r_("CTD", "2021-02-03", "buy_done", -2_000_000)))
ck("dung nguong gap (14 ngay) -> con la cung giao dich", M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("X", "2020-01-15", "buy_done", -100)))
ck("vuot nguong gap (15 ngay) -> KHAC giao dich", not M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("X", "2020-01-16", "buy_done", -100)))
ck("thu tu nguoc lai cho cung ket qua (doi xung)", M.same_transaction(
    r_("X", "2020-01-15", "buy_done", -100), r_("X", "2020-01-01", "buy_done", -100)))
ck("dung nguong lech gia tri (5%) -> cung giao dich", M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("X", "2020-01-02", "buy_done", -95)))
ck("vuot nguong lech gia tri (6%) -> KHAC giao dich", not M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("X", "2020-01-02", "buy_done", -94)))
ck("khac ticker -> KHAC giao dich", not M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("Y", "2020-01-02", "buy_done", -100)))
ck("khac action_type -> KHAC giao dich", not M.same_transaction(
    r_("X", "2020-01-01", "buy_done", -100), r_("X", "2020-01-02", "sell_done", 100)))
ck("ca hai delta 0 -> cung giao dich", M.same_transaction(
    r_("X", "2020-01-01", "buy_done", 0), r_("X", "2020-01-02", "buy_done", 0)))

print("=" * 70)
print("10. dedup — SUM(is_canonical) = quy mo THAT cua mot giao dich")
print("=" * 70)
ndn_a, ndn_b = byk[("NDN", "2018-05-17")], byk[("NDN", "2018-05-18")]
ck("NDN: hai dong CUNG nhom", ndn_a["dup_group_id"] and
   ndn_a["dup_group_id"] == ndn_b["dup_group_id"], ndn_a["dup_group_id"])
ck("NDN: dung MOT dong canonical", [ndn_a["is_canonical"], ndn_b["is_canonical"]].count(True) == 1)
ck("NDN: canonical = ngay cong bo SOM hon", ndn_a["is_canonical"] and not ndn_b["is_canonical"])
ck("NDN: dong bi loai tro ve canonical", ndn_b["duplicate_of"] == ndn_a["id"]
   and ndn_a["duplicate_of"] is None)
ck("NDN: SUM canonical = -1.000.000 (MOT giao dich, KHONG phai -2.000.000)",
   sum(r["outstanding_delta"] for r in (ndn_a, ndn_b) if r["is_canonical"]) == -1_000_000,
   sum(r["outstanding_delta"] for r in (ndn_a, ndn_b) if r["is_canonical"]))
ck("NDN: dong khong-canonical VAN o trong bang (audit)",
   ndn_b["outstanding_delta"] == -1_000_000)

ctd_i, ctd_v = byk[("CTD", "2021-02-01")], byk[("CTD", "2021-02-03")]
ck("CTD: nhom BAT CHEO tier (inferred + vendor)", ctd_i["dup_group_id"]
   and ctd_i["dup_group_id"] == ctd_v["dup_group_id"])
ck("CTD: canonical = dong VENDOR (tier tin hon), khong phai dong suy luan",
   ctd_v["is_canonical"] and not ctd_i["is_canonical"],
   (ctd_v["source"], ctd_i["source"]))
ck("CTD: dong suy luan tro ve dong vendor", ctd_i["duplicate_of"] == ctd_v["id"])
ck("CTD: SUM canonical = -2.000.000 (KHONG phai -4.008.900)",
   sum(r["outstanding_delta"] for r in (ctd_i, ctd_v) if r["is_canonical"]) == -2_000_000,
   sum(r["outstanding_delta"] for r in (ctd_i, ctd_v) if r["is_canonical"]))

hws = [byk[("HWS", "2018-09-24")], byk[("HWS", "2019-06-25")]]
ck("HWS: 2 dot mua THAT cung so luong cach 274 ngay -> KHONG gop",
   all(r["is_canonical"] and r["dup_group_id"] is None for r in hws))
ck("HWS: SUM giu ca hai dot", sum(r["outstanding_delta"] for r in hws) == -117_000)
gdt = [byk[("GDT", "2016-08-11")], byk[("GDT", "2016-08-13")]]
ck("GDT: gan ngay nhung lech 65,6% -> KHONG gop",
   all(r["is_canonical"] and r["dup_group_id"] is None for r in gdt))
chn = [byk[("CHN", f"2020-01-{d}")] for d in ("01", "11", "21")]
ck("CHN chain guard: dong 1+2 gop (cach 10 ngay)",
   chn[0]["dup_group_id"] and chn[0]["dup_group_id"] == chn[1]["dup_group_id"])
ck("CHN chain guard: dong 3 KHONG bi chain vao (cach NEO 20 ngay)",
   chn[2]["dup_group_id"] is None and chn[2]["is_canonical"])
ck("CHN chain guard: SUM canonical = -14.000 (2 giao dich, khong phai -7.000)",
   sum(r["outstanding_delta"] for r in chn if r["is_canonical"]) == -14_000,
   sum(r["outstanding_delta"] for r in chn if r["is_canonical"]))

ck("BAT BIEN: is_canonical la BOOL, khong bao gio NULL",
   all(isinstance(r["is_canonical"], bool) for r in rows))
ck("BAT BIEN: duplicate_of co gia tri <=> khong canonical",
   all(bool(r["duplicate_of"]) == (not r["is_canonical"]) for r in rows))
ck("BAT BIEN: khong-canonical PHAI co dup_group_id",
   all(r["dup_group_id"] for r in rows if not r["is_canonical"]))
ck("BAT BIEN: moi nhom co DUNG 1 canonical", all(
   sum(1 for r in rows if r["dup_group_id"] == g and r["is_canonical"]) == 1
   for g in {r["dup_group_id"] for r in rows if r["dup_group_id"]}))
ck("BAT BIEN: duplicate_of luon tro ve mot id co that va DANG canonical",
   all(next(c for c in rows if c["id"] == r["duplicate_of"])["is_canonical"]
       for r in rows if r["duplicate_of"]))
ck("BAT BIEN: UNSIZED khong bao gio bi danh dau trung (delta NULL, khong so duoc)",
   all(r["dup_group_id"] is None and r["is_canonical"]
       for r in rows if r["size_status"] == "UNSIZED"))
ck("2 dong UNSIZED cach 7 ngay cung ticker+action -> khong gop, khong crash",
   all(byk[("HHH", d)]["dup_group_id"] is None and byk[("HHH", d)]["is_canonical"]
       for d in ("2021-07-23", "2021-07-30")))
ck("dup_group_id deterministic qua lan chay",
   [r["dup_group_id"] for r in M.build_rows(FIX_EVENTS, FIX_INFERRED, LOADED)]
   == [r["dup_group_id"] for r in rows])
ck("nguong la HANG SO tuong minh, khong an trong code",
   M.DUP_MAX_GAP_DAYS == 14 and M.DUP_REL_TOL == 0.05)

print("=" * 70)
print(f"KET QUA: {PASS} PASS / {FAIL} FAIL  (TZ={os.environ.get('TZ', '(khong dat)')})")
print("=" * 70)
sys.exit(1 if FAIL else 0)
