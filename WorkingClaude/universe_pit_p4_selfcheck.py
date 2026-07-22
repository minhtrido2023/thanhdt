#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""universe_pit_p4_selfcheck.py — cổng bắt buộc của P4 cutover
(`deploy_golive_dt5g_v4/golive_recommend_v23.py`: CAPIT breadth + pool + ADV cap).

§4.4-C-conserv `mike/agents/Taylor/research/ticker_prune_replacement_plan.md`.

KHÁC P2 VÀ P3:
  P2 đòi diff = 0 (giữ nguyên hành vi). P3 đo diff của một look-ahead ĐANG SỬA.
  P4 thì hành vi lịch sử CÓ ĐỔI, đã đo trước, user đã duyệt — nên selfcheck này KHÔNG assert
  diff=0 mà assert **đổi ĐÚNG những gì đã báo cáo, không hơn một ngày nào**. Một thay đổi
  "gần đúng" ở đây là một lệnh mua thật sai size.

  HAI SWITCH RIÊNG (đừng gộp lại): `CAPIT_BREADTH_SOURCE` (trigger — CUTOVER hôm nay) và
  `CAPIT_POOL_SOURCE` (chọn rổ + ADV cap — VẪN GHIM "prune", xem T6c). Chúng hỏng theo hai
  kiểu khác nhau: breadth sai ⇒ sai NGÀY kích hoạt; pool sai ⇒ sai TÊN MÃ được mua.

  T1. Hằng số production đúng bản đã duyệt: BREADTH="pit", TOPN=250, gate=0,31, POOL="prune".
  T2. Gate ĐI KÈM mẫu số: lật BREADTH về "prune" thì gate tự về 0,30 (không có trạng
      thái "mẫu số mới + ngưỡng cũ" — đó là dạng hỏng nguy hiểm nhất của P4).
  T3. Không fallback im lặng: SQL breadth nhánh "pit" không chạm `ticker_prune`; pool đang ghim
      thì PHẢI đọc `ticker_prune`; nhánh lạ (cả hai switch) thì raise.
  T4. LỊCH SỬ (2014→nay, chạy SQL THẬT của production cho cả 2 nhánh): tập ngày fire mới lệch
      tập cũ ĐÚNG 7 ngày, toàn bộ theo hướng MẤT (0 fire giả), và đúng 7 ngày đã công bố.
  T5. LỊCH SỬ — SIZE: `capit_grind` lật đúng 1 cặp ngày đã công bố (2015-08-24/25), không hơn.
  T6. NGÀY LIVE: breadth→fired, grind (cổng "không đổi đợt giải ngân đang dở"); pool production
      == pool legacy TRÙNG KHÍT; và ĐO delta của nhánh pool "pit" CHƯA bật (phải đúng {HVT} như
      đã ghi trong doc — nếu lệch nghĩa là căn cứ hoãn cutover pool đã cũ, phải đo lại).
  T7. Fail-closed độ tươi: universe_pit chậm hơn dữ liệu giá ⇒ stale=True (và nhánh "prune"
      là no-op). Đây là bảo hiểm cho đúng sự cố đã suýt xảy ra ngày 2026-07-22.

Chạy:  $DNA_PYEXE universe_pit_p4_selfcheck.py
"""
import os
import re
import sys
from datetime import datetime, timedelta

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)      # cùng lý do như file production: phải đọc LIVE

import numpy as np   # noqa: E402
import pandas as pd  # noqa: E402
from simulate_holistic_nav import bq  # noqa: E402

SRC_PATH = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
FAILS = []

# Tập thay đổi ĐÃ CÔNG BỐ VÀ ĐÃ ĐƯỢC USER DUYỆT (§4.4-C). Hard-code ở đây là CỐ Ý: selfcheck
# phải so với con số con người đã duyệt, không phải với thứ code hôm nay tình cờ sinh ra.
LOST_EXPECTED = ["2015-05-18", "2018-07-05", "2020-02-04", "2020-03-11",
                 "2020-03-25", "2020-04-01", "2022-06-15"]
GRIND_FLIP_EXPECTED = ["2015-08-24", "2015-08-25"]
HIST_START = "2014-01-01"


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


# ── nạp ĐÚNG code production (không copy): khối hằng số + các hàm universe/CAPIT ───────────
SRC = open(SRC_PATH, encoding="utf-8").read()
_head = SRC[SRC.index("# ── UNIVERSE SOURCE — P3 cutover"):SRC.index("def w_lag_target(")]
NS = {"bq": bq, "pd": pd}
exec(compile(_head, SRC_PATH, "exec"), NS)          # noqa: S102 — cố ý: dùng lại code production

capit_breadth_sql = NS["capit_breadth_sql"]
capit_pool_sql = NS["capit_pool_sql"]
capit_breadth_is_stale = NS["capit_breadth_is_stale"]

print("=" * 88)
print("  universe_pit P4 selfcheck — CAPIT breadth + pool + ADV cap (C-conserv)")
print("=" * 88)

# ── T1: hằng số production ────────────────────────────────────────────────────────────────
check("T1a CAPIT_BREADTH_SOURCE='pit'", NS["CAPIT_BREADTH_SOURCE"] == "pit", f"= {NS['CAPIT_BREADTH_SOURCE']!r}")
check("T1b CAPIT_TOPN=250", NS["CAPIT_TOPN"] == 250, f"= {NS['CAPIT_TOPN']}")
check("T1c WASHOUT_GATE=0.31", abs(NS["WASHOUT_GATE"] - 0.31) < 1e-12, f"= {NS['WASHOUT_GATE']}")
check("T1d CAPIT_POOL_SOURCE='prune' (còn ghim có chủ ý)", NS["CAPIT_POOL_SOURCE"] == "prune",
      f"= {NS['CAPIT_POOL_SOURCE']!r}")

# ── T2: gate đi kèm mẫu số (rollback 1 dòng phải kéo theo ngưỡng) ──────────────────────────
_ns2 = {"bq": bq, "pd": pd}
exec(compile(_head.replace('CAPIT_BREADTH_SOURCE = "pit"', 'CAPIT_BREADTH_SOURCE = "prune"'), SRC_PATH, "exec"), _ns2)
check("T2 rollback 'prune' ⇒ gate tự về 0.30",
      _ns2["CAPIT_BREADTH_SOURCE"] == "prune" and abs(_ns2["WASHOUT_GATE"] - 0.30) < 1e-12,
      f"gate={_ns2['WASHOUT_GATE']}")

# ── T3: không fallback im lặng ────────────────────────────────────────────────────────────
sql_pit_br, sql_pool_prod = capit_breadth_sql("2026-01-01", "2026-07-22"), capit_pool_sql("2026-07-22")
check("T3a SQL breadth 'pit' không chạm ticker_prune", "ticker_prune" not in sql_pit_br)
check("T3b SQL pool đang GHIM ⇒ đọc ticker_prune, không chạm universe_pit",
      "ticker_prune" in sql_pool_prod and "universe_pit" not in sql_pool_prod)
check("T3c SQL breadth 'pit' dùng universe_pit_q + top-N",
      "universe_pit_q" in sql_pit_br and "rn <= 250" in sql_pit_br)
NS["CAPIT_BREADTH_SOURCE"] = "xxx"
try:
    capit_breadth_sql("2026-01-01", "2026-07-22"); _raised = False
except ValueError:
    _raised = True
NS["CAPIT_BREADTH_SOURCE"] = "pit"
check("T3d CAPIT_BREADTH_SOURCE lạ ⇒ raise (không đoán mò)", _raised)
NS["CAPIT_POOL_SOURCE"] = "xxx"
try:
    capit_pool_sql("2026-07-22"); _raised2 = False
except ValueError:
    _raised2 = True
NS["CAPIT_POOL_SOURCE"] = "prune"
check("T3e CAPIT_POOL_SOURCE lạ ⇒ raise", _raised2)
NS["CAPIT_POOL_SOURCE"] = "pit"
_br_after_pool_flip = capit_breadth_sql("2026-01-01", "2026-07-22")
_pool_pit = capit_pool_sql("2026-07-22")
NS["CAPIT_POOL_SOURCE"] = "prune"
check("T3f hai switch ĐỘC LẬP (lật pool không đụng breadth, và ngược lại)",
      _br_after_pool_flip == sql_pit_br and "universe_pit" in _pool_pit
      and "ticker_prune" in capit_pool_sql("2026-07-22"))

# ── nạp 2 chuỗi breadth lịch sử bằng ĐÚNG SQL production ───────────────────────────────────
END = datetime.now().strftime("%Y-%m-%d")
print(f"\n  … tải 2 chuỗi breadth {HIST_START} → {END} (SQL production, cả 2 nhánh)")
new = bq(capit_breadth_sql(HIST_START, END)).rename(columns={"oversold": "br_new"})
NS["CAPIT_BREADTH_SOURCE"] = "prune"
old = bq(capit_breadth_sql(HIST_START, END)).rename(columns={"oversold": "br_old"})
NS["CAPIT_BREADTH_SOURCE"] = "pit"
for d in (new, old):
    d["time"] = pd.to_datetime(d["time"])
d = old.merge(new, on="time", how="inner").sort_values("time").reset_index(drop=True)
print(f"    {len(d):,} phiên khớp (old {len(old):,} / new {len(new):,})")

fire_old = (d.br_old.values >= 0.30)
fire_new = (d.br_new.values >= NS["WASHOUT_GATE"])

# ── T4: tập ngày fire lệch đúng như đã công bố ─────────────────────────────────────────────
lost = [str(t.date()) for t in d.time[fire_old & ~fire_new]]
added = [str(t.date()) for t in d.time[~fire_old & fire_new]]
check("T4a THÊM 0 ngày fire (không có fire giả)", added == [], f"added={added}")
check("T4b MẤT đúng 7 ngày đã công bố", lost == LOST_EXPECTED,
      f"mất {len(lost)}: {lost}" if lost != LOST_EXPECTED else f"{len(lost)} ngày")
# CỐ Ý không pin con số tuyệt đối (82→75 đo tới 2026-07-21): mỗi ngày fire MỚI làm cả hai vế
# tăng 1, nên pin tổng sẽ tự hỏng sau mỗi lần CAPIT fire. Bất biến thật = HIỆU đúng bằng số ngày
# mất, và tập fire mới là TẬP CON của tập cũ (đã có T4a chặn chiều ngược).
check("T4c fire_new = fire_old − đúng 7 ngày (tập con thật sự)",
      int(fire_old.sum()) - int(fire_new.sum()) == len(LOST_EXPECTED)
      and bool((fire_new & ~fire_old).sum() == 0),
      f"old={int(fire_old.sum())} new={int(fire_new.sum())} (đo tới {d.time.iloc[-1].date()}; "
      f"tham chiếu §4.4 đo tới 2026-07-21 là 82→75)")


def grind_map(mask):
    """Bản sao NGỮ NGHĨA của vòng lặp grind trong production (`for back in range(20, 91)`):
    một ngày fire là 'grind' nếu có ngày fire khác cách nó 20-90 PHIÊN về trước."""
    idx = np.where(mask)[0]
    s = set(int(i) for i in idx)
    return {str(d.time[i].date()): any((i - b) in s for b in range(20, 91)) for i in idx}


g_old, g_new = grind_map(fire_old), grind_map(fire_new)
flips = sorted(k for k in set(g_old) & set(g_new) if g_old[k] != g_new[k])
check("T5 grind lật đúng 1 cặp ngày đã công bố (size ×2)", flips == GRIND_FLIP_EXPECTED,
      f"flips={flips}")

# ── T6: NGÀY LIVE — hai nhánh phải ra cùng một quyết định ──────────────────────────────────
print("\n  … A/B trên ngày LIVE (cổng 'không đổi đợt giải ngân đang dở')")
live = d.time.iloc[-1]
b_old, b_new = float(d.br_old.iloc[-1]), float(d.br_new.iloc[-1])
f_old, f_new = b_old >= 0.30, b_new >= NS["WASHOUT_GATE"]
check("T6a fired giống nhau", f_old == f_new,
      f"live={live.date()} old br={b_old:.4f}→{f_old} / new br={b_new:.4f}→{f_new}")
check("T6b grind giống nhau", g_old.get(str(live.date())) == g_new.get(str(live.date())),
      f"old={g_old.get(str(live.date()))} new={g_new.get(str(live.date()))}")

# Pool đang GHIM ⇒ pool production PHẢI trùng khít pool legacy (đây là bảo đảm "0 lệnh mua mới
# phát sinh vì migration" trong lúc đợt giải ngân CAPIT còn dở).
pool_prod = set(bq(capit_pool_sql(live.date()))["ticker"])
NS["CAPIT_POOL_SOURCE"] = "pit"
pool_pit = set(bq(capit_pool_sql(live.date()))["ticker"])
NS["CAPIT_POOL_SOURCE"] = "prune"
pool_legacy = set(bq(f"""SELECT p.ticker FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{live.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")["ticker"])
check("T6c pool production == pool legacy (ghim ⇒ trùng khít)", pool_prod == pool_legacy,
      f"n={len(pool_prod)} | lệch={sorted(pool_prod ^ pool_legacy)}")
# Delta của nhánh CHƯA bật — không phải để chặn, mà để CĂN CỨ HOÃN không âm thầm cũ đi.
check("T6c2 delta pool 'pit' đúng như doc ({HVT})", sorted(pool_pit - pool_prod) == ["HVT"]
      and pool_prod - pool_pit == set(),
      f"pit thêm={sorted(pool_pit - pool_prod)} bớt={sorted(pool_prod - pool_pit)} "
      f"(nếu lệch: đo lại §4.4 trước khi trích dẫn)")

# ADV cap: nguồn đi theo pool. Ghim ⇒ `ticker_prune`; đo luôn nhánh `ticker` để biết cutover pool
# sau này có đổi trần VND nào không.
pool_new = pool_prod
if pool_new:
    tl = ",".join(f"'{t}'" for t in sorted(pool_new))
    adv = {}
    for tag, tbl in (("new", "ticker"), ("old", "ticker_prune")):
        a = bq(f"""WITH px AS (
  SELECT p.ticker, p.time, COALESCE(p.Price,p.Close)*p.Volume AS turn,
         ROW_NUMBER() OVER (PARTITION BY p.ticker ORDER BY p.time DESC) rn
  FROM tav2_bq.{tbl} p
  WHERE p.ticker IN ({tl}) AND p.time < DATE '{live.date()}'
    AND p.time >= DATE_SUB(DATE '{live.date()}', INTERVAL 90 DAY))
SELECT ticker, APPROX_QUANTILES(turn, 2)[OFFSET(1)] AS adv20
FROM px WHERE rn <= 20 GROUP BY ticker""")
        adv[tag] = {r.ticker: float(r.adv20) for r in a.itertuples() if pd.notna(r.adv20)}
    diff = {t: (adv["old"].get(t), adv["new"].get(t)) for t in sorted(pool_new)
            if adv["old"].get(t) != adv["new"].get(t)}
    check("T6d ADV20 (⇒ trần %ADV) `ticker` vs `ticker_prune` không lệch 1 đồng trên pool live",
          diff == {}, f"n={len(adv['new'])} mã" if not diff else f"lệch: {diff}")
else:
    check("T6d ADV20 từng mã không đổi", True, "pool rỗng — không có gì để so")

# ── T7: fail-closed độ tươi ───────────────────────────────────────────────────────────────
print()
src_max = pd.Timestamp(bq(f"SELECT MAX(t.time) AS m FROM tav2_bq.ticker AS t "
                          f"WHERE t.time <= DATE '{END}' AND t.Close_T1 > 0")["m"].iloc[0])
st_ok, _ = capit_breadth_is_stale(src_max, END)
st_bad, sm = capit_breadth_is_stale(src_max - pd.Timedelta(days=1), END)
st_nat, _ = capit_breadth_is_stale(pd.NaT, END)
check("T7a chuỗi breadth tươi ⇒ stale=False", st_ok is False)
check("T7b chuỗi breadth chậm 1 ngày ⇒ stale=True (CAPIT fail-closed)", st_bad is True,
      f"src_max={sm}")
check("T7c chuỗi rỗng/NaT ⇒ stale=True", st_nat is True)
NS["CAPIT_BREADTH_SOURCE"] = "prune"
check("T7d nhánh 'prune' ⇒ kiểm tra là no-op",
      capit_breadth_is_stale(src_max - pd.Timedelta(days=30), END) == (False, None))
NS["CAPIT_BREADTH_SOURCE"] = "pit"

print("\n" + "=" * 88)
print(f"  {'✅ PASS TẤT CẢ' if not FAILS else '❌ FAIL: ' + ', '.join(FAILS)}")
print("=" * 88)
sys.exit(1 if FAILS else 0)
