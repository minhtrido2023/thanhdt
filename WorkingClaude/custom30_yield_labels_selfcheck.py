# -*- coding: utf-8 -*-
"""Selfcheck cho `custom30_yield_labels.py` (Phase 1 Option C, job Taylor_20260818_134610).

Ba câu hỏi, không phải "chạy có ra output không":
  A. Nhãn batch có ĐÚNG BẰNG `trading_bot.due_diligence._yield_floor()` không — trên chính 30 mã
     của rổ production hiện tại, gọi thật cả hai đường.
  B. Hỏng thì có fail-open không — `bq` ném lỗi ⇒ toàn bộ NO_DATA/None, KHÔNG raise ra pipeline.
  C. Nhãn có bao giờ NULL/rỗng không (cột phải luôn có giá trị, kể cả đường hỏng).
Kiểm tra "rổ 30 mã không đổi" nằm ở tầng ngoài (chạy lại custom30_history.py với đích scratch
rồi diff CSV) — xem FINDINGS/bus event của job.
"""
import os, sys
import pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom30_yield_labels as yfl
from trading_bot.due_diligence import _yield_floor

CSV = "data/custom30v_8l_publish.csv"
fails = []

df = pd.read_csv(CSV)
rd = df["rebal_date"].max()
cur = df[df["rebal_date"] == rd]
pairs = [(t, rd) for t in cur["ticker"]]
print(f"[setup] rebal {rd}, {len(pairs)} ma tu {CSV}")

# --- A. batch == _yield_floor(), goi that ca hai duong ---------------------------------------
lab = yfl.label_basket(bq, pairs)
mism = []
for tk, d in pairs:
    got = lab.get((tk, d), ("NO_DATA", None))
    ref = _yield_floor(tk, d)
    exp = (ref["yield_floor_note"], ref["is_stable_payer"])
    if got != exp:
        mism.append((tk, got, exp))
print(f"[A] batch vs _yield_floor: {len(pairs)-len(mism)}/{len(pairs)} khop")
for m in mism:
    print(f"    MISMATCH {m[0]}: batch={m[1]} _yield_floor={m[2]}")
if mism:
    fails.append(f"A: {len(mism)} ma lech nhan")
print("    phan bo: " + ", ".join(f"{k}={v}" for k, v in
                                  pd.Series([v[0] for v in lab.values()]).value_counts().items()))

# --- B. fail-open khi bq hong ----------------------------------------------------------------
def _boom(sql):
    raise RuntimeError("bq down (selfcheck)")
try:
    bad = yfl.label_basket(_boom, pairs, verbose=False)
    ok_b = (len(bad) == len(pairs) and all(v == ("NO_DATA", None) for v in bad.values()))
    print(f"[B] bq hong -> fail-open: {'PASS' if ok_b else 'FAIL'} ({len(bad)} cap)")
    if not ok_b:
        fails.append("B: khong fail-open dung ve NO_DATA/None")
except Exception as exc:
    print(f"[B] FAIL — label_basket RAISE ra ngoai: {exc}")
    fails.append("B: label_basket raise (pipeline se chet)")

# --- C. khong bao gio thieu key / nhan rong ---------------------------------------------------
missing = [p for p in pairs if (p[0], p[1]) not in lab]
empty = [k for k, v in lab.items() if not v[0]]
print(f"[C] thieu key: {len(missing)} | nhan rong: {len(empty)}")
if missing or empty:
    fails.append("C: thieu key hoac nhan rong")

print("\n" + ("SELFCHECK FAIL: " + "; ".join(fails) if fails else "SELFCHECK PASS (A+B+C)"))
sys.exit(1 if fails else 0)
