"""Mutation test — do xem selfcheck co THAT SU bat loi khong, hay chi chay xanh cho vui.

Moi mutation la mot loi THAT dang tin ma nguoi viet loader nay de mac:
lat dau sai/thieu, tron tier, noi suy UNSIZED thanh 0, tin so Winston khong verify,
confirmed_asof lac quan hon thuc te... Mutation SONG SOT = lo hong trong selfcheck.

Chay: $DNA_PYEXE mutation_test.py
"""
import os
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SRC = (HERE / "build_treasury_share_events.py").read_text()
CHK = (HERE / "treasury_share_events_selfcheck.py").read_text()
PY = sys.executable

MUTATIONS = [
    ("M01 khong lat dau (tra thang shares_delta)",
     "    return -d", "    return d"),
    ("M02 lat dau CHI cho buy_done",
     "    return -d",
     "    return -d if action_type == 'buy_done' else d"),
    ("M03 bo kiem tra vi pham dau",
     "    if d != 0 and (d > 0) != (VENDOR_SIGN[action_type] > 0):",
     "    if False:"),
    ("M04 UNSIZED noi suy thanh 0",
     'row = dict(outstanding_delta=None, size_status=UNSIZED, source=None,',
     'row = dict(outstanding_delta=0, size_status=UNSIZED, source=None,'),
    ("M05 tron SIBLING_ROW vao VENDOR_PUBLISHED",
     'source = SOURCE_SIBLING if int(e["n_null"]) > 0 else SOURCE_VENDOR',
     'source = SOURCE_VENDOR'),
    ("M06 nang tier suy luan len high",
     'source=SOURCE_INFERRED, confidence="medium",',
     'source=SOURCE_INFERRED, confidence="high",'),
    ("M07 gan nhan suy luan thanh VENDOR_PUBLISHED",
     'source=SOURCE_INFERRED, confidence="medium",',
     'source=SOURCE_VENDOR, confidence="medium",'),
    ("M08 confirmed_asof = public_date (PIT leak)",
     '"confirmed_asof": confirmed_asof_of(after_d, a["release_date"])',
     '"confirmed_asof": d'),
    ("M09 confirmed_asof bo qua Release_Date muon hon",
     "    return max(fin_time, release_date)", "    return fin_time"),
    ("M10 confirmed_asof lay ngay SOM hon",
     "    return max(fin_time, release_date)", "    return min(fin_time, release_date)"),
    ("M11 tin so Winston, bo recompute",
     "    if recomputed != int(inferred_delta):",
     "    if False:"),
    ("M12 verify bo qua sai dau",
     "    if (recomputed > 0) != (OUTSTANDING_SIGN[action_type] > 0):",
     "    if False:"),
    ("M13 OShares bat dong van coi la suy duoc",
     "    if recomputed == 0:", "    if False:"),
    ("M14 thieu OShares van cho qua",
     "    if before_oshares is None or after_oshares is None:", "    if False:"),
    ("M15 ca bi tu choi van duoc nap",
     "        if not ok:", "        if False:"),
    ("M16 id bo action_type -> buy/sell trung id",
     'key = f"{ticker}|{public_date}|{action_type}"',
     'key = f"{ticker}|{public_date}"'),
    ("M17 id khong deterministic",
     'return "TRSY-" + hashlib.sha1(key.encode()).hexdigest()[:16]',
     'return "TRSY-" + hashlib.sha1((key + str(os.getpid())).encode()).hexdigest()[:16]'),
    ("M18 khong keu khi 2 gia tri shares_delta khac nhau",
     '        if int(e["n_distinct"]) > 1:', '        if False:'),
    ("M19 khong keu khi su kien trung",
     "        if key in seen:", "        if False:"),
    ("M20 action_type la van cho qua",
     "        if at not in VENDOR_SIGN:", "        if False:"),
    ("M21 mat unsized_reason",
     'unsized_reason=inf.get("unsized_reason") or "UNKNOWN")',
     'unsized_reason=None)'),
    ("M22 vendor cong bo 0 bi coi la UNSIZED",
     "        if delta is not None:", "        if delta:"),
    ("M23 confirmed_asof gan cho ca VENDOR_PUBLISHED",
     'confidence="high", confirmed_asof=None, unsized_reason=None,',
     'confidence="high", confirmed_asof="2020-01-01", unsized_reason=None,'),
    # --- B1: luat dedup (cung mot giao dich dang 2 lan -> SUM cong 2 lan)
    ("M24 TAT hoan toan luat dedup",
     "                if same_transaction(g[0], r):", "                if False:"),
    ("M25 canonical chon tier IT tin nhat thay vi tin nhat",
     'canon = min(g, key=lambda x: (TIER_RANK[x["source"]], x["public_date"], x["id"]))',
     'canon = max(g, key=lambda x: (TIER_RANK[x["source"]], x["public_date"], x["id"]))'),
    ("M26 bo nguong khoang cach ngay (gop ca 2 dot mua that)",
     "    if gap > DUP_MAX_GAP_DAYS:", "    if False:"),
    ("M27 bo nguong lech gia tri (gop ca 2 su kien khac quy mo)",
     "    return abs(x - y) / m <= DUP_REL_TOL", "    return True"),
    ("M28 chain truyen tiep thay vi neo dong dau nhom",
     "                if same_transaction(g[0], r):",
     "                if same_transaction(g[-1], r):"),
    ("M29 danh dau CA NHOM la canonical (dedup thanh no-op)",
     '            x["is_canonical"] = x is canon', '            x["is_canonical"] = True'),
    ("M30 keo UNSIZED (delta NULL) vao dedup",
     '        if r["outstanding_delta"] is not None:', "        if True:"),
    # --- N1: be rong cua so OShares (5/33 ca phai noi ra 2 quy)
    ("M31 mat inferred_window_days (an ca cua so 2 quy)",
     'inferred_window_days=inf["window_days"])', "inferred_window_days=None)"),
    ("M32 hardcode window_days 1 quy thay vi do tu cua so that",
     '"window_days": (date.fromisoformat(after_d) - date.fromisoformat(before_d)).days,',
     '"window_days": 91,'),
]

killed = survived = skipped = []
killed, survived, skipped = [], [], []
for name, old, new in MUTATIONS:
    if SRC.count(old) != 1:
        skipped.append((name, f"anchor xuat hien {SRC.count(old)} lan"))
        continue
    with tempfile.TemporaryDirectory() as td:
        (pathlib.Path(td) / "build_treasury_share_events.py").write_text(SRC.replace(old, new))
        (pathlib.Path(td) / "treasury_share_events_selfcheck.py").write_text(CHK)
        r = subprocess.run([PY, "treasury_share_events_selfcheck.py"], cwd=td,
                           capture_output=True, text=True, env={**os.environ, "PYTHONPATH": td})
    (killed if r.returncode != 0 else survived).append(name)

print("=" * 70)
for n in killed:
    print(f"  KILLED   {n}")
for n in survived:
    print(f"  SONG SOT {n}   <-- lo hong selfcheck")
for n, why in skipped:
    print(f"  SKIP     {n} ({why})")
print("=" * 70)
print(f"{len(killed)}/{len(killed) + len(survived)} mutation bi giet"
      f"{f' — {len(skipped)} skip' if skipped else ''}   (interpreter: {PY})")
print("=" * 70)
sys.exit(1 if survived or skipped else 0)
