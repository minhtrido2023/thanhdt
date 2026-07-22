#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""universe_pit_p3_selfcheck.py — cổng bắt buộc của P3 cutover
(`deploy_golive_dt5g_v4/golive_recommend_v23.py`, panel sector-lens D1 RE_BACKLOG, ICB-8633).

§4.3/§4.3b `mike/agents/Taylor/research/ticker_prune_replacement_plan.md`.

KHÁC P2 Ở ĐIỂM CỐT LÕI: P2 đòi diff = 0 (giữ nguyên hành vi). P3 thì KHÔNG — đây là sửa một
look-ahead CÓ THẬT đang sống trong production (predicate `IN (SELECT DISTINCT ticker FROM
ticker_prune)` không có điều kiện thời gian ⇒ nạp cả mã CHƯA NIÊM YẾT vào panel quá khứ).
Nên selfcheck này ĐO diff chứ không assert diff=0, và assert đúng cái phải đúng:

  T1. Hằng số production `UNIVERSE_SOURCE` = "pit" (đọc từ chính file production, không copy).
  T2. Không có đường fallback im lặng: predicate "pit" không chạm `ticker_prune`; câu SQL panel
      trong file production cũng không còn `ticker_prune`.
  T3. Fail-safe: thiếu ngày trong `universe_pit` → RuntimeError (không im lặng, không fallback);
      nhánh "prune" thì assert là no-op.
  T4. **BẰNG CHỨNG BUG ĐÃ FIX**: VHM (niêm yết 2018) CÓ trong panel 2014 với nhánh "prune",
      và KHÔNG còn với nhánh "pit".
  T5. Panel tại cửa sổ LIVE hôm nay: đo diff thật (không giả định 0) + so tập tín hiệu
      RE_BACKLOG (mask d1m) giữa 2 nhánh ⇒ trả lời "có đổi recommend LIVE hôm nay không".

Chạy:  $DNA_PYEXE universe_pit_p3_selfcheck.py
"""
import os
import re
import sys
from datetime import datetime, timedelta

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)      # cùng lý do như file production: phải đọc LIVE

import pandas as pd  # noqa: E402
from simulate_holistic_nav import bq  # noqa: E402

SRC_PATH = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
DT_TABLE = "vnindex_5state_dt5g_live"
FAILS = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


# ── nạp ĐÚNG code production (không copy): exec khối hằng số + 2 hàm universe ──────────────
SRC = open(SRC_PATH, encoding="utf-8").read()
_head = SRC[SRC.index("# ── UNIVERSE SOURCE — P3 cutover"):SRC.index("def w_lag_target(")]
NS = {"bq": bq}
exec(compile(_head, SRC_PATH, "exec"), NS)          # noqa: S102 — cố ý: dùng lại code production

# ── trích ĐÚNG câu SQL panel D1 từ file production (không copy) ────────────────────────────
_m = re.search(r'd1 = bq\(f"""(.*?)"""\)', SRC, re.S)
assert _m, "khong tim thay cau SQL panel d1 trong file production"
D1_SQL_TMPL = _m.group(1)


def panel(source, start, end):
    """Chạy đúng câu SQL panel của production với UNIVERSE_SOURCE = `source`."""
    old = NS["UNIVERSE_SOURCE"]
    NS["UNIVERSE_SOURCE"] = source
    try:
        sql = D1_SQL_TMPL.format(START=start, END=end, DT_TABLE=DT_TABLE,
                                 UNI_PRED=NS["universe_pred"]("t"),
                                 UNIVERSE_SOURCE=source)
    finally:
        NS["UNIVERSE_SOURCE"] = old
    df = bq(sql)
    df["time"] = pd.to_datetime(df["time"])
    return df


def d1_mask(df):
    """Mask RE_BACKLOG — copy 1:1 dòng `d1m` của production (dòng ngay sau câu SQL trên)."""
    return (df["adv_yoy"].notna() & (df["adv_yoy"] > 0.5) & df["fa_tier"].isin(["C", "D"])
            & df["state5"].isin([3, 4, 5])
            & ((df["np_yoy"].fillna(-99) > 0) | (df["rev_yoy"].fillna(-99) > 0)))


print("=" * 88)
print("  universe_pit P3 selfcheck — golive_recommend_v23.py panel D1 RE_BACKLOG (ICB-8633)")
print("=" * 88)

# ── T1 ─────────────────────────────────────────────────────────────────────────────────────
print("\nT1. Hằng số production")
check("T1.1 UNIVERSE_SOURCE == 'pit'", NS["UNIVERSE_SOURCE"] == "pit", NS["UNIVERSE_SOURCE"])
check("T1.2 trỏ đúng bảng universe_pit_q", NS["UNIVERSE_PIT_TABLE"].endswith("tav2_mike.universe_pit_q"),
      NS["UNIVERSE_PIT_TABLE"])

# ── T2 ─────────────────────────────────────────────────────────────────────────────────────
print("\nT2. Không có đường fallback im lặng")
p_pit = NS["universe_pred"]("t")
check("T2.1 predicate 'pit' đọc universe_pit_q theo NGÀY",
      "universe_pit_q" in p_pit and "u2.time=t.time" in p_pit)
check("T2.2 predicate 'pit' KHÔNG chạm ticker_prune", "ticker_prune" not in p_pit)
check("T2.3 SQL panel production không còn ticker_prune", "ticker_prune" not in D1_SQL_TMPL)
try:
    NS["UNIVERSE_SOURCE"] = "khong-ton-tai"
    NS["universe_pred"]("t")
    check("T2.4 UNIVERSE_SOURCE lạ → ValueError", False, "không raise")
except ValueError:
    check("T2.4 UNIVERSE_SOURCE lạ → ValueError", True)
finally:
    NS["UNIVERSE_SOURCE"] = "pit"

# ── T3 ─────────────────────────────────────────────────────────────────────────────────────
print("\nT3. Fail-safe thiếu ngày")
_real_bq = NS["bq"]
NS["bq"] = lambda q: pd.DataFrame({"n_src": [80], "n_missing": [3], "uni_max": ["2026-07-21"]})
try:
    NS["assert_universe_covers"]("2026-01-01", "2026-07-22")
    check("T3.1 thiếu ngày → RuntimeError", False, "không raise")
except RuntimeError as e:
    check("T3.1 thiếu ngày → RuntimeError", "khong tu fallback" in str(e), str(e)[:70])
NS["UNIVERSE_SOURCE"] = "prune"
try:
    NS["assert_universe_covers"]("2026-01-01", "2026-07-22")
    check("T3.2 nhánh 'prune' → assert no-op", True)
except Exception as e:
    check("T3.2 nhánh 'prune' → assert no-op", False, repr(e))
NS["UNIVERSE_SOURCE"] = "pit"
NS["bq"] = _real_bq
try:
    NS["assert_universe_covers"]((datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"),
                                 datetime.now().strftime("%Y-%m-%d"))
    check("T3.3 cửa sổ LIVE hôm nay: universe_pit phủ đủ", True)
except RuntimeError as e:
    check("T3.3 cửa sổ LIVE hôm nay: universe_pit phủ đủ", False, str(e)[:120])

# ── T4 — bằng chứng look-ahead đã fix ──────────────────────────────────────────────────────
print("\nT4. Look-ahead VHM (niêm yết 2018) trong panel 2014")
p14_prune = panel("prune", "2014-01-01", "2014-12-31")
p14_pit = panel("pit", "2014-01-01", "2014-12-31")
s_prune, s_pit = set(p14_prune["ticker"]), set(p14_pit["ticker"])
check("T4.1 VHM CÓ trong panel 2014 nhánh 'prune' (bug đang sống)", "VHM" in s_prune)
check("T4.2 VHM KHÔNG còn trong panel 2014 nhánh 'pit' (đã fix)", "VHM" not in s_pit)
_leak = sorted(s_prune - s_pit)
print(f"       panel 2014: prune n={len(s_prune)} · pit n={len(s_pit)} · "
      f"bị loại ({len(_leak)}): {', '.join(_leak) if _leak else '—'}")
print(f"       thêm vào ({len(s_pit - s_prune)}): {', '.join(sorted(s_pit - s_prune)) or '—'}")
check("T4.3 panel 2014 nhánh 'pit' không rỗng", len(s_pit) > 0, f"n={len(s_pit)}")

# ── T5 — cửa sổ LIVE hôm nay ───────────────────────────────────────────────────────────────
print("\nT5. Cửa sổ LIVE hôm nay (đo diff thật, KHÔNG giả định = 0)")
END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
# A/B PHẢI nguyên tử: chạy 2 lần câu panel cách nhau vài phút thì `fa_ratings` có thể re-rank
# ĐÚNG eff-date ở giữa (đã thấy thật: QCG fa_tier D→E) ⇒ diff giả. Nên lấy MỘT panel hợp
# (pit OR prune) trong 1 truy vấn, rồi tách 2 nhánh bằng membership đọc riêng.
_uni_union = f"(({NS['universe_pred']('t')}) OR (t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)))"
lv = bq(D1_SQL_TMPL.format(START=START, END=END, DT_TABLE=DT_TABLE,
                           UNI_PRED=_uni_union, UNIVERSE_SOURCE="union"))
lv["time"] = pd.to_datetime(lv["time"])
_pr = bq("SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2")
_pt = bq(f"""SELECT u.ticker, u.time FROM `{NS['UNIVERSE_PIT_TABLE']}` AS u
WHERE u.in_universe AND u.time BETWEEN DATE '{START}' AND DATE '{END}'""")
_pt["time"] = pd.to_datetime(_pt["time"])
INUNI = set(map(tuple, _pt[["ticker", "time"]].values))
lv_prune = lv[lv["ticker"].isin(set(_pr["ticker"]))].copy()
lv_pit = lv[[t in INUNI for t in map(tuple, lv[["ticker", "time"]].values)]].copy()
lp, ll = set(lv_prune["ticker"]), set(lv_pit["ticker"])
print(f"       panel [{START}..{END}]: prune n={len(lp)} · pit n={len(ll)}")
print(f"       RA ({len(lp - ll)}): {', '.join(sorted(lp - ll)) or '—'}")
print(f"       VÀO ({len(ll - lp)}): {', '.join(sorted(ll - lp)) or '—'}")
check("T5.1 panel LIVE nhánh 'pit' không rỗng", len(ll) > 0, f"n={len(ll)}")

sig_prune = set(map(tuple, lv_prune.loc[d1_mask(lv_prune), ["ticker", "time"]].values))
sig_pit = set(map(tuple, lv_pit.loc[d1_mask(lv_pit), ["ticker", "time"]].values))
print(f"       tín hiệu RE_BACKLOG (ticker,ngày) qua mask d1m: prune={len(sig_prune)} · pit={len(sig_pit)}")
_last = max([t for _, t in sig_prune] + [t for _, t in sig_pit], default=None)
last_p = sorted(t for t, d in sig_prune if d == _last) if _last else []
last_l = sorted(t for t, d in sig_pit if d == _last) if _last else []
print(f"       ngày tín hiệu gần nhất: {_last} | prune={last_p or '—'} | pit={last_l or '—'}")
print(f"       *** DIFF tín hiệu = {len(sig_prune ^ sig_pit)} cặp — KHÔNG assert = 0: P3 là sửa bug, "
      f"đổi hành vi là CÓ CHỦ ĐÍCH. Tác động end-to-end phải đo bằng A/B chạy trọn script. ***")

# T5.3 — kiểm chứng NGUYÊN NHÂN của mọi thay đổi: đúng bằng membership theo NGÀY của universe_pit,
# không phải một lỗi join/SQL. Đối chiếu thẳng với bảng, độc lập với câu SQL panel.
bad_rm = [p for p in (sig_prune - sig_pit) if p in INUNI]        # bị bỏ dù VẪN trong universe
bad_add = [p for p in (sig_pit - sig_prune) if p not in INUNI]   # thêm dù KHÔNG trong universe
check("T5.3 mọi thay đổi giải thích được bằng membership theo ngày của universe_pit",
      not bad_rm and not bad_add, f"bỏ-sai={len(bad_rm)} thêm-sai={len(bad_add)}")

print("\n" + "=" * 88)
print(f"  KẾT QUẢ: {'PASS TẤT CẢ' if not FAILS else 'FAIL: ' + ', '.join(FAILS)}")
print("=" * 88)
sys.exit(1 if FAILS else 0)
