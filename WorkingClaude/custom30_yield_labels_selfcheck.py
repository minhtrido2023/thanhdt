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

# --- D. `feed_asof` tach coi: feed cu CHI anh huong lo neo o HOM NAY -------------------------
# Hoi quy cho fix 2026-09-30 (job Taylor_20260930_030814, quant-skeptic vong 1 bat): cong
# freshness `corporate_action` la TOAN CUC cho mot lo, nen `custom30_history.py` goi 2 lo —
# lo lich su neo `feed_asof=<rebal hien tai>`, lo ky mo neo `feed_asof=hom nay`. Neu ai gop lai
# thanh 1 lo (hoac bo `feed_asof`), mot ngay feed cu >4 ngay se keo CA lich su ve NO_DATA.
# Test nay chet ngay khi dieu do xay ra — truoc day chi duoc chung minh 1 lan bang tay.
import datetime as _dt
from zoneinfo import ZoneInfo
import corp_action_lib as _cal
import trading_bot.due_diligence as _dd

_today = _dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
_cur_rd_d = _dt.date.fromisoformat(str(rd)[:10])
_rds = sorted(df["rebal_date"].unique())

def _clear_fresh_cache():
    """Cong freshness cache theo (key, ngay-neo) trong process — phai xoa, khong thi test gia PASS."""
    for k in [k for k in _dd._CACHE if isinstance(k, tuple) and k and k[0] == "_ca_fresh"]:
        del _dd._CACHE[k]

if (_today - _cur_rd_d).days <= _dd.CORP_ACTION_STALE_DAYS_MAX or len(_rds) < 2:
    print(f"[D] SKIP — hai neo cach nhau {(_today-_cur_rd_d).days}d <= nguong "
          f"{_dd.CORP_ACTION_STALE_DAYS_MAX}d (vua rebal xong) ⇒ khong co gi de tach")
else:
    _prev = _rds[-2]
    _pc = [(t, _prev) for t in df[df["rebal_date"] == _prev]["ticker"]]
    _po = [(t, str(_today)) for t in cur["ticker"]]
    _clear_fresh_cache()
    _ref = yfl.label_basket(bq, _pc, verbose=False, feed_asof=str(rd))
    _orig_ff = _cal.feed_freshness
    # Feed dung o `rd`: TUOI voi neo lich su (tuoi 0) nhung CU voi neo hom nay (~1 quy).
    _cal.feed_freshness = lambda *a, **k: {"max_ingested": str(rd)}
    try:
        _clear_fresh_cache()
        _sc = yfl.label_basket(bq, _pc, verbose=False, feed_asof=str(rd))
        _so = yfl.label_basket(bq, _po, verbose=False, feed_asof=str(_today))
    finally:
        _cal.feed_freshness = _orig_ff
        _clear_fresh_cache()
    _ok_closed = (_sc == _ref) and any(v != ("NO_DATA", None) for v in _ref.values())
    _ok_open = bool(_so) and all(v == ("NO_DATA", None) for v in _so.values())
    print(f"[D] feed cu -> lich su ({_prev}) GIU NGUYEN: {'PASS' if _ok_closed else 'FAIL'} "
          f"| ky mo ({_today}) ve NO_DATA: {'PASS' if _ok_open else 'FAIL'}")
    if not _ok_closed:
        fails.append("D: feed cu lam DOI nhan ky da dong (cong freshness bi gop lo)")
    if not _ok_open:
        fails.append("D: feed cu ma ky mo KHONG ve NO_DATA (cong freshness khong con neo o hom nay)")

print("\n" + ("SELFCHECK FAIL: " + "; ".join(fails) if fails else "SELFCHECK PASS (A+B+C+D)"))
sys.exit(1 if fails else 0)
