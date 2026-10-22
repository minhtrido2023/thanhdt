#!/usr/bin/env python3
"""A/B — gán mã nguyên nhân cho từng (ứng viên × account) + định lượng vốn mục tiêu bị lỡ.

Mã gán TAY từ artifact đã đọc (plan JSON từng ngày + journal + dnse_raw), xem `EVIDENCE` bên
dưới — mỗi mã có trích nguồn. Fill = cột d*_fill của audit_live_rows.csv (dnse_raw, lọc account).
Slot mục tiêu (VND) lấy từ chính plan: SpaceX lag_hi/lo_target_vnd (plan 07-28: 91,05tr/72,84tr);
ZaloPay 'Cần ~27,07M LAG_HI / 21,66M LAG_LO' (plan 08-06). Áp các slot này cho mọi ngày = ƯỚC LƯỢNG.
"""
import csv, os, collections

OUT = os.path.dirname(os.path.abspath(__file__))
SLOT = {("SpaceX", "LAG_HI"): 91_046_364, ("SpaceX", "LAG_LO"): 72_837_091,
        ("ZaloPay", "LAG_HI"): 27_070_000, ("ZaloPay", "LAG_LO"): 21_660_000}
PT = dict(x.split(",") for x in (
    "AFX,LAG_LO AGR,LAG_LO AMC,LAG_HI APF,LAG_HI BMS,LAG_HI BSI,LAG_LO BSR,LAG_HI BVB,LAG_HI CLC,LAG_LO "
    "CSV,LAG_HI DCM,LAG_HI DDN,LAG_HI DGW,LAG_HI DHD,LAG_LO DRI,LAG_HI EVF,LAG_LO FID,LAG_LO FTS,LAG_LO "
    "GEE,LAG_LO GVR,LAG_LO HAR,LAG_LO HCM,LAG_LO HMH,LAG_LO HT1,LAG_HI IDV,LAG_HI ITQ,LAG_HI IVS,LAG_HI "
    "KHS,LAG_HI MAC,LAG_HI MCP,LAG_LO MDF,LAG_HI MST,LAG_LO NBC,LAG_HI NVB,LAG_HI PCT,LAG_HI PGS,LAG_HI "
    "PHR,LAG_HI POW,LAG_HI PRC,LAG_HI PRE,LAG_LO PSI,LAG_LO PV2,LAG_LO PVT,LAG_HI PXL,LAG_LO SCL,LAG_HI "
    "SPM,LAG_HI SSI,LAG_LO TCI,LAG_HI TIN,LAG_LO TMG,LAG_HI TRC,LAG_LO TV2,LAG_LO TV3,LAG_LO TVN,LAG_HI "
    "UNI,LAG_HI VCI,LAG_LO VCR,LAG_LO VE9,LAG_LO VGS,LAG_LO VLG,LAG_HI VND,LAG_HI VNF,LAG_HI VNP,LAG_HI "
    "VPB,LAG_LO VSI,LAG_LO VVS,LAG_HI XPH,LAG_HI").split())

# Lọc ở tầng tín hiệu/DD — KHÔNG phải ứng viên mục tiêu (theo chính luật fleet ghi trong plan)
FILTER = {
    "SIG_FILTER_ADV_UNIV": "AFX BMS HAR NBC PXL DDN KHS SPM VLG CLC HT1 IDV ITQ TCI PRC AMC MDF TIN VE9 PV2 UNI "
                           "PCT XPH VCR FID DHD MAC TV3 PRE HMH PGS VSI VNF",
    "EXCLUDED_DD": "TRC GEE VNP MST BVB DGW BSR GVR VGS NVB PHR TVN",
    "EXCLUDED_USER_BANNED": "IVS TMG VVS",
}
# (ticker, account) → (mã, bằng chứng) cho mọi ca vượt qua lọc tín hiệu
OPS = {
    ("VPB", "ZaloPay"): ("FILLED_D1", "plan_ZaloPay_07-27 BUY-VPB-01 700cp; dnse_raw 07-27 fill 700"),
    ("VPB", "SpaceX"): ("ALREADY_HELD", "plan_SpaceX_07-27: 'VPB — 2300cp đã trong portfolio, không mua lại'"),
    ("VND", "SpaceX"): ("ALREADY_HELD", "plan_SpaceX_07-27: 'VND — 300cp từ plan trước'"),
    ("VND", "ZaloPay"): ("WAIT_CASH", "plan_ZaloPay_07-27 deferred_insufficient_cash"),
    ("PVT", "SpaceX"): ("ALREADY_HELD", "plan_SpaceX_08-05 PVT NEEDS_USER_DECISION — đang giữ trong rổ CAPIT"),
    ("PVT", "ZaloPay"): ("ALREADY_HELD", "PVT đang giữ trong rổ CAPIT (plan_ZaloPay_07-24 capit_basket_held)"),
    **{(t, "SpaceX"): ("PLAN_CALENDAR_ERROR",
                       "engine: UPCOMING T+3 từ 07-22 ⇒ entry 07-27; plan_SpaceX_07-24 ghi 'T+2 entry 07-25' "
                       "(THỨ BẢY); plan_SpaceX_07-27 ghi 'CỬA SỔ ĐÃ ĐÓNG… MISSED'; dispatch tối 07-24 fail "
                       "do weekly usage limit (plan_ZaloPay_07-27)") for t in "AGR BSI FTS HCM".split()},
    **{(t, "ZaloPay"): ("WAIT_CASH", "plan_ZaloPay_07-27 deferred_insufficient_cash (sau khi VPB dùng ppse)")
       for t in "AGR BSI FTS HCM".split()},
    ("CSV", "ZaloPay"): ("FILLED_D1", "plan_ZaloPay_07-28 BUY CSV; dnse_raw 07-28 fill 1000"),
    **{(t, "SpaceX"): ("WAIT_CASH", "plan_SpaceX_07-28 t1_candidates_valid → deferred_orders "
                                     "('Nếu user không nạp vốn kịp… lỡ cửa sổ — chấp nhận')")
       for t in "CSV EVF PSI VCI".split()},
    **{(t, "ZaloPay"): ("EXCLUDED_DD_INCONSISTENT",
                        "plan_ZaloPay_07-28 'FLOOR_FAIL — skip' trong khi plan_SpaceX cùng ngày xếp VALID")
       for t in "EVF PSI VCI".split()},
    ("MCP", "ZaloPay"): ("SIG_FILTER_ADV_UNIV", "plan_ZaloPay_07-28 excluded_no_liquidity"),
    ("MCP", "SpaceX"): ("EXCLUDED_DD", "plan_SpaceX_07-28 'DCF RICH (MoS -20.1%, robust)'"),
    ("APF", "SpaceX"): ("WAIT_CASH", "plan_SpaceX_08-04/05/06 deferred_orders WINDOW_OPEN_DEFERRED (DD: ADV 1,16 tỷ < 2 tỷ)"),
    ("APF", "ZaloPay"): ("SIG_FILTER_ADV_UNIV", "không có trong plan_ZaloPay 08-04..06; DD ADV3T 1,16 tỷ < sàn 2 tỷ"),
    ("TV2", "SpaceX"): ("WAIT_CASH", "plan_SpaceX_08-04 deferred 'Cần ~74,3M cash'"),
    ("TV2", "ZaloPay"): ("WAIT_CASH", "plan_ZaloPay_08-04 'DEFERRED — thiếu cash… cash chỉ có 5.82M'; d3 BLOCKED_RECONCILE"),
    ("DCM", "SpaceX"): ("WAIT_CASH", "plan_SpaceX_08-05/06 deferred WINDOW_OPEN_DEFERRED; 08-06 park_trim BLOCKED_RECONCILE"),
    ("DCM", "ZaloPay"): ("WAIT_CASH", "plan_ZaloPay_08-05 'DEFERRED — thiếu cash'; 08-06 BLOCKED_RECONCILE"),
    ("DRI", "SpaceX"): ("PLAN_EMPTY_BLOCKED",
                        "d1 08-06 plan 0 lệnh, park_trim BLOCKED_RECONCILE (lệch sổ VHM) → deferred; d2 08-07 "
                        "đặt 3500 nhưng WAIT_CASH ×94 'sức mua broker 0 cp'; d3 08-10 trần=anchor 13.000, 0 fill"),
    ("DRI", "ZaloPay"): ("WAIT_CASH", "d1 deferred thiếu cash 5,82M; d2 không có trong plan; d3 WAIT_CASH ×27 + trần anchor, 0 fill"),
    ("POW", "SpaceX"): ("PLAN_EMPTY_BLOCKED",
                        "d1 08-06 plan rỗng BLOCKED_RECONCILE; d2 08-07 không lên plan; d3 08-10 trần=anchor 13.400, 0 fill"),
    ("POW", "ZaloPay"): ("WAIT_CASH", "d1 deferred thiếu cash; d3 WAIT_CASH ×119 (PARK sell 'HTTP 400 deal not found')"),
    ("SCL", "SpaceX"): ("FILLED_LATE", "d1 08-06 plan rỗng BLOCKED_RECONCILE; d3 08-10 fill 1500/1500 (email broker 1500)"),
    ("SCL", "ZaloPay"): ("PARTIAL_LATE", "d1 deferred thiếu cash; d3 08-10 fill 1000/1500, WAIT_CASH ×50 (email 1000)"),
    ("SSI", "SpaceX"): ("PLAN_DECIDED_NOT_ORDERED",
                        "d1 08-07 lag_analysis decision=BUY nhưng KHÔNG có trong orders[]/deferred; d2 08-10 trần=anchor "
                        "24.450, 0 fill; d3 08-11 SKIP live 25.100 > anchor"),
    ("SSI", "ZaloPay"): ("PLAN_DECIDED_NOT_ORDERED",
                         "d1 08-07 decision=BUY không vào orders[]; d2 08-10 WAIT_CASH ×119; d3 08-11 SKIP live > anchor"),
}
WINDOW_CAUSE = {"PRICE_CEILING"}       # khai để rõ: không ca nào có mã chính là cửa sổ/trần (xem secondary)
# mã PHỤ — trần/hết cửa sổ có xuất hiện như quân domino cuối ở các ca này:
SECONDARY_CEILING = {("DRI", "SpaceX"), ("POW", "SpaceX"), ("SSI", "SpaceX"), ("SSI", "ZaloPay"),
                     ("DRI", "ZaloPay")}

rows = list(csv.DictReader(open(f"{OUT}/audit_live_rows.csv", encoding="utf-8")))
flt = {t: k for k, v in FILTER.items() for t in v.split()}
out = []
for r in rows:
    tk, acct = r["ticker"], r["account"]
    if (tk, acct) in OPS:
        code, ev = OPS[(tk, acct)]
    elif tk in flt:
        code, ev = flt[tk], "plan lag_analysis / DD cột due_diligence (xem audit_live_stdout.txt)"
    else:
        code, ev = "UNEXPLAINED", ""
    fills = [int(r[f"d{k}_fill"]) for k in (1, 2, 3)]
    out.append({"ticker": tk, "entry": r["entry"], "account": acct, "play_type": PT.get(tk, ""),
                "code": code, "secondary_ceiling": (tk, acct) in SECONDARY_CEILING,
                "fill_d1": fills[0], "fill_d2": fills[1], "fill_d3": fills[2],
                "evidence": ev})
with open(f"{OUT}/audit_live_classified.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

NONTARGET = {"SIG_FILTER_ADV_UNIV", "EXCLUDED_DD", "EXCLUDED_USER_BANNED", "ALREADY_HELD", "EXCLUDED_DD_INCONSISTENT"}
cnt = collections.Counter((o["account"], o["code"]) for o in out)
print("== mã nguyên nhân theo account (ứng viên×account)")
for (a, c), n in sorted(cnt.items()):
    print(f"  {a:7} {c:26} {n}")
tg = [o for o in out if o["code"] not in NONTARGET]
print(f"\n== ứng viên MỤC TIÊU (qua lọc tín hiệu của chính fleet): {len(tg)} / {len(out)} ứng viên×account")
# giá trị: fill thật lấy qty × giá đặt của plan 08-10 / giá dnse; đơn giản hoá: đã khớp đủ = 1 slot,
# partial = tỷ lệ qty, còn lại = 0. Qty mục tiêu: SCL ZaloPay 1500 (plan 08-10).
dep = {("VPB", "ZaloPay"): (1.0, 1), ("CSV", "ZaloPay"): (1.0, 1), ("SCL", "SpaceX"): (1.0, 3),
       ("SCL", "ZaloPay"): (1000 / 1500, 3)}
tot = collections.defaultdict(float); miss = collections.defaultdict(float)
late = collections.defaultdict(float); bycode = collections.defaultdict(float)
for o in tg:
    v = SLOT[(o["account"], o["play_type"])]
    tot[o["account"]] += v
    frac, day = dep.get((o["ticker"], o["account"]), (0.0, None))
    miss[o["account"]] += v * (1 - frac)
    if day and day > 1:
        late[o["account"]] += v * frac
    bycode[o["code"]] += v * (1 - frac)
T = sum(tot.values())
for a in tot:
    print(f"  {a:7} mục tiêu {tot[a]/1e6:8.1f}tr | KHÔNG triển khai {miss[a]/1e6:7.1f}tr ({miss[a]/tot[a]:.0%}) "
          f"| triển khai TRỄ (phiên 3) {late[a]/1e6:6.1f}tr ({late[a]/tot[a]:.0%})")
print(f"  TỔNG   mục tiêu {T/1e6:8.1f}tr | không triển khai {sum(miss.values())/1e6:7.1f}tr "
      f"({sum(miss.values())/T:.0%}) | trễ {sum(late.values())/1e6:.1f}tr ({sum(late.values())/T:.0%})")
print("\n== vốn KHÔNG triển khai theo mã nguyên nhân CHÍNH (tr VND, ƯỚC LƯỢNG slot):")
for c, v in sorted(bycode.items(), key=lambda x: -x[1]):
    print(f"  {c:26} {v/1e6:7.1f}tr  ({v/sum(miss.values()):.0%})")
sec = sum(SLOT[(o['account'], o['play_type'])] for o in tg if o["secondary_ceiling"])
print(f"\n  trong đó ca có trần/hết cửa sổ là quân domino CUỐI (sau khi phiên 1 đã mất vì vận hành): "
      f"{sec/1e6:.1f}tr ({sec/sum(miss.values()):.0%})")
print(f"  ca mà trần/cửa sổ là nguyên nhân CHÍNH (phiên 1 có lệnh hợp lệ đủ tiền mà vẫn không khớp): 0")
