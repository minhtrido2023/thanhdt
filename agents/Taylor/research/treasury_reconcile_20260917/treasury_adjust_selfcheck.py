"""Hermetic selfcheck cho treasury_adjust.py — KHÔNG đọc BQ. Số neo từ BQ thật 2026-09-17 (đóng băng)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treasury_adjust as T

fails = []
def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        fails.append(name)

VRE_LISTED, VRE_FIN = 2_328_818_410.0, 2_272_318_410.0
vre_fin = [("2019-07-29", VRE_LISTED), ("2019-10-29", VRE_FIN), ("2026-07-29", VRE_FIN)]
vre_ev = [{"public_date": "2019-12-19", "action_type": "buy_done", "abs_delta": None}]
lst = lambda d: VRE_LISTED

# V1: VRE giả định có AIS mới (neo niêm yết) ⇒ phải trừ đúng 56,5tr
v, lab, _ = T.treasury_adjust(VRE_LISTED, "corporate_action.AIS", "2026-09-01", "2026-09-17", vre_fin, lst, vre_ev)
check("V1 VRE neo AIS ⇒ trừ 56.500.000", v == VRE_FIN and lab == "TREASURY_AIS_ADJ", f"{v} {lab}")
# V2: VRE neo BCTC ⇒ không trừ lần hai
v, lab, _ = T.treasury_adjust(VRE_FIN, "ticker_financial", "2026-07-29", "2026-09-17", vre_fin, lst, vre_ev)
check("V2 VRE neo BCTC ⇒ giữ nguyên", v == VRE_FIN and lab == "TREASURY_FIN_FWD", f"{v} {lab}")
# V3: PIT 2019-10-30: dòng quý 10-29 đã restate SỚM gồm lô 56,5tr; sự kiện 12-19 chưa xảy ra ⇒ không áp
v, lab, _ = T.treasury_adjust(VRE_FIN, "ticker_financial", "2019-10-29", "2019-10-30", vre_fin, lst, vre_ev)
check("V3 PIT trước ngày sự kiện ⇒ không áp", v == VRE_FIN, f"{v} {lab}")
# V4: dòng quý restate sớm + sự kiện có cỡ rơi SAU dòng quý ⇒ hấp thụ, KHÔNG trừ lần 2
ev_sized = [{"public_date": "2019-12-19", "action_type": "buy_done", "abs_delta": 56_500_000}]
v, lab, _ = T.treasury_adjust(VRE_FIN, "ticker_financial", "2019-10-29", "2019-12-31", vre_fin[:2], lst, ev_sized)
check("V4 BCTC restate sớm ⇒ ABSORBED", v == VRE_FIN and lab == "TREASURY_FIN_ABSORBED", f"{v} {lab}")
# V5: dòng quý CHƯA gồm (không đổi so với quý trước) ⇒ áp tiến −56,5tr
fin_unabs = [("2019-07-29", VRE_LISTED), ("2019-10-29", VRE_LISTED)]
v, lab, _ = T.treasury_adjust(VRE_LISTED, "ticker_financial", "2019-10-29", "2019-12-31", fin_unabs, lst, ev_sized)
check("V5 BCTC chưa gồm ⇒ áp tiến", v == VRE_FIN and lab == "TREASURY_FIN_FWD", f"{v} {lab}")
# S1: sell_done tăng lưu hành (dấu)
ev_sell = [{"public_date": "2020-01-10", "action_type": "sell_done", "abs_delta": 1_000_000}]
v, lab, _ = T.treasury_adjust(100_000_000.0, "ticker_financial", "2019-12-31", "2020-02-01",
                              [("2019-09-30", 100_000_000.0), ("2019-12-31", 100_000_000.0)], lambda d: 100e6, ev_sell)
check("S1 sell_done ⇒ +1.000.000", v == 101_000_000.0, f"{v} {lab}")
# U1: sự kiện sau dòng quý thiếu cỡ ⇒ không đoán
ev_uns = [{"public_date": "2020-01-10", "action_type": "buy_done", "abs_delta": None}]
v, lab, _ = T.treasury_adjust(100e6, "ticker_financial", "2019-12-31", "2020-02-01", [("2019-12-31", 100e6)], lambda d: 100e6, ev_uns)
check("U1 thiếu cỡ ⇒ TREASURY_UNSIZED", lab == "TREASURY_UNSIZED", lab)
# C1: niêm yết giảm (huỷ CP quỹ) sau dòng quý + neo AIS ⇒ fail-closed
v, lab, _ = T.treasury_adjust(VRE_FIN, "corporate_action.AIS", "2026-09-01", "2026-09-17", vre_fin, lst, vre_ev, listed_cuts=("2026-08-20",))
check("C1 huỷ CP quỹ sau dòng quý ⇒ None", v is None and lab == "TREASURY_CANCEL_AMBIGUOUS", lab)
# C2: cut TRƯỚC dòng quý ⇒ đã phản ánh trong hiệu chuẩn, không chặn
v, lab, _ = T.treasury_adjust(VRE_LISTED, "corporate_action.AIS", "2026-09-01", "2026-09-17", vre_fin, lst, vre_ev, listed_cuts=("2026-07-01",))
check("C2 cut trước dòng quý ⇒ không chặn", lab == "TREASURY_AIS_ADJ", lab)
# K1: vượt trần 15% ⇒ None
v, lab, _ = T.treasury_adjust(100e6, "ticker_financial", "2019-12-31", "2020-02-01", [("2019-12-31", 100e6)], lambda d: 100e6,
                              [{"public_date": "2020-01-10", "action_type": "buy_done", "abs_delta": 20_000_000}])
check("K1 trần 15% ⇒ TREASURY_CEILING", v is None and lab == "TREASURY_CEILING", lab)
# K2: đúng 15% biên ⇒ nhận
v, lab, _ = T.treasury_adjust(100e6, "ticker_financial", "2019-12-31", "2020-02-01", [("2019-12-31", 100e6)], lambda d: 100e6,
                              [{"public_date": "2020-01-10", "action_type": "buy_done", "abs_delta": 15_000_000}])
check("K2 biên 15% ⇒ nhận", v == 85e6, f"{v} {lab}")
# G1: GDT-like — niêm yết > lưu hành nhưng KHÔNG có tin buy_done nào trước dòng quý ⇒ không trừ mù (ca PAN/KLB)
v, lab, _ = T.treasury_adjust(258_072_996.0, "corporate_action.AIS", "2026-07-13", "2026-09-17",
                              [("2026-07-28", 250_673_166.0)], lambda d: 258_072_996.0, [])
check("G1 lệch không có tin ⇒ UNCORROBORATED, giữ nguyên", v == 258_072_996.0 and lab == "TREASURY_GAP_UNCORROBORATED", lab)
# G2: GDT thật — có buy_done 2026-05-14 trước dòng quý 07-31 ⇒ trừ 316.310
v, lab, _ = T.treasury_adjust(27_391_721.0, "corporate_action.AIS", "2026-09-16", "2026-09-17",
                              [("2026-07-31", 27_075_411.0)], lambda d: 27_391_721.0,
                              [{"public_date": "2026-05-14", "action_type": "buy_done", "abs_delta": None}])
check("G2 GDT neo AIS ⇒ 27.075.411", v == 27_075_411.0 and lab == "TREASURY_AIS_ADJ", f"{v} {lab}")
# N1: lưu hành > niêm yết ⇒ không phải CP quỹ
v, lab, _ = T.treasury_adjust(71_742_434.0, "corporate_action.AIS", "2026-08-18", "2026-09-17",
                              [("2026-07-31", 73_647_114.0)], lambda d: 71_742_434.0, vre_ev)
check("N1 gap âm ⇒ NEG_GAP giữ nguyên", v == 71_742_434.0 and lab == "TREASURY_NEG_GAP", lab)
# P1: None vào ⇒ None ra (không hồi sinh số đã fail-closed)
v, lab, _ = T.treasury_adjust(None, "corporate_action.AIS", None, "2026-09-17", vre_fin, lst, vre_ev)
check("P1 base None ⇒ None", v is None, lab)
# L1: không dựng được niêm yết tại dòng quý ⇒ None
v, lab, _ = T.treasury_adjust(VRE_LISTED, "corporate_action.AIS", "2026-09-01", "2026-09-17", vre_fin, lambda d: None, vre_ev)
check("L1 listed None ⇒ None", v is None and lab == "TREASURY_NO_LISTED", lab)
# F0: không có dòng BCTC
v, lab, _ = T.treasury_adjust(5.0, "corporate_action.AIS", "2026-09-01", "2026-09-17", [], lst, vre_ev)
check("F0 không BCTC ⇒ giữ, nhãn NO_FIN", v == 5.0 and lab == "TREASURY_NO_FIN", lab)

# B1: sự kiện TRÙNG ngày dòng quý ⇒ coi là dòng quý đã phản ánh (không áp) — khoá biên trái
ev_b = [{"public_date": "2019-12-31", "action_type": "buy_done", "abs_delta": 1_000_000}]
v, lab, _ = T.treasury_adjust(100e6, "ticker_financial", "2019-12-31", "2020-02-01", [("2019-12-31", 100e6)], lambda d: 100e6, ev_b)
check("B1 sự kiện = ngày dòng quý ⇒ không áp", v == 100e6, f"{v} {lab}")
# B2: sự kiện ĐÚNG ngày asof ⇒ áp — khoá biên phải
v, lab, _ = T.treasury_adjust(100e6, "ticker_financial", "2019-12-31", "2020-02-01", [("2019-12-31", 100e6)], lambda d: 100e6,
                              [{"public_date": "2020-02-01", "action_type": "buy_done", "abs_delta": 1_000_000}])
check("B2 sự kiện = asof ⇒ áp", v == 99e6, f"{v} {lab}")
# A2: neo AIS + CP quỹ tồn + mua THÊM sau dòng quý có cỡ ⇒ trừ cả hai
v, lab, _ = T.treasury_adjust(VRE_LISTED, "corporate_action.AIS", "2026-09-01", "2026-09-17", vre_fin, lst,
                              vre_ev + [{"public_date": "2026-08-15", "action_type": "buy_done", "abs_delta": 10_000_000}])
check("A2 neo AIS + mua thêm ⇒ trừ 66,5tr", v == VRE_FIN - 10_000_000 and lab == "TREASURY_AIS_ADJ", f"{v} {lab}")

print(f"\n{len(fails)} FAIL" if fails else "\nALL PASS")
sys.exit(1 if fails else 0)
