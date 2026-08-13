#!/usr/bin/env python3
"""consumer_c_driver.py — consumer THỨ BA của `oshares_at`, không nằm trong đề bài dispatch:
`mike/bin/corp_action_daily.py` (cron LIVE từ 2026-08-13) import THẲNG `oshares_at`, không qua
`oshares_pit`. Đó chính là hình dạng rủi ro mà vòng 4 đang đóng — nên phải ĐO nó, không suy luận.

⚠️ VÒNG 5 — BẢN TRƯỚC ĐO THIẾU 2/3 ĐIỂM GỌI (quant-skeptic vòng 4 tìm ra, đúng).
`corp_action_daily.py` gọi `oshares_at` ở BA chỗ, mỗi chỗ hỏi một CÂU KHÁC NHAU, nên một chỗ
không nói thay được hai chỗ kia:

  1. `publish`     (~dòng 1008) `oshares_at(track, asof)`      — số CÔNG BỐ ra snapshot, tại `asof`.
  2. `check_retro` (~dòng 837)  `oshares_at(tickers, prev_asof)` — tính lại QUÁ KHỨ (phiên trước).
  3. `crosscheck`  (~dòng 872)  `oshares_at([tk], qd)`         — tại NGÀY DÒNG QUÝ *của từng mã*,
     khác nhau mỗi mã và có thể lùi tới ~3 tháng. Đây là điểm bản trước bỏ sót, và cũng là điểm
     đổi NHIỀU NHẤT: cổng chứng nhận bật/tắt làm **TCB** — vị thế đang giữ THẬT ở cả SpaceX lẫn
     ZaloPay — chuyển `DIVERGENT` → `NO_MODEL_VALUE`, tức là mất khả năng đối soát chứ không phải
     "hết lệch".

Dựng lại đúng `track set` của lượt chạy thật (mã đang giữ ∪ ex-right hôm nay ∪ AIS hiệu lực hôm
nay) rồi chụp CẢ BA điểm trên đúng tập đó.

Dùng:
    python3 consumer_c_driver.py OUT.json [ASOF]

Chụp CẢ HAI chân trong MỘT tiến trình, trên CÙNG một `cache` đã fetch: `gate_on` (code hôm nay) và
`gate_off` (`_ais_certified` luôn True = hành vi TRƯỚC vòng 4). Một tiến trình / một cache là CỐ Ý,
không phải tiện tay: chạy hai lượt riêng thì hai lượt fetch BQ khác nhau, và mọi khác biệt quan sát
được sẽ lẫn giữa "cổng làm đổi" với "feed đổi giữa hai lượt". Ở đây `cache` là hằng số theo xây
dựng nên khác biệt duy nhất còn lại đúng là cái cổng.
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import oshares_live as OL                                                   # noqa: E402
import corp_action_daily as C                                              # noqa: E402
from oshares_live import _fetch, oshares_at                                # noqa: E402

argv = [a for a in sys.argv[1:] if not a.startswith("--")]
out_path = argv[0]
asof = argv[1] if len(argv) > 1 else C.today_ict()

pos = C.read_positions(asof=asof)
held = sorted({tk for a in pos.values() for tk in a["positions"]})
ex_today, ais_today, _ev = C.triggered_today(asof)
track = sorted(set(held) | ex_today | ais_today)
cache = _fetch(track, asof) if track else ([], [])
quarters, _corp = cache

# Hôm nay (2026-08-13) mới có ĐÚNG MỘT snapshot đã publish nên `prior_snapshot` trả None ⇒ điểm
# `check_retro` CHƯA kích hoạt trong lượt chạy thật; nó kích hoạt từ lượt 08-14. Đo bằng phiên
# giao dịch liền trước để biết TRƯỚC nó sẽ làm gì, và ghi rõ đó là giả định (`synthetic`), không
# phải số của lượt hôm nay.
prev_asof, _prev_snap = C.prior_snapshot(asof)
retro_synthetic = prev_asof is None
if retro_synthetic:
    prev_asof = C.prev_trading_day(dt.date.fromisoformat(asof)).isoformat()


def _row(r):
    return {"value": r["value"], "method": r["method"], "anchor_date": r.get("anchor_date"),
            "anchor_source": r.get("anchor_source"),
            "uncertified_value": r.get("uncertified_value")}


def measure():
    """Ba điểm gọi, đo trên `cache` đã fetch sẵn (không truy vấn thêm ⇒ hai chân so được)."""
    # ── ĐIỂM 1 · publish (dòng ~1008) — tại `asof`
    cur = oshares_at(track, asof, _cache=cache) if track else {}

    # ── ĐIỂM 2 · check_retro (dòng ~837) — tại PHIÊN TRƯỚC, trên tập mã đã publish
    back = oshares_at(sorted(cur), prev_asof, _cache=cache) if (cur and prev_asof) else {}

    # ── ĐIỂM 3 · crosscheck (dòng ~872) — tại NGÀY DÒNG QUÝ CỦA TỪNG MÃ (khác nhau mỗi mã)
    xchk = {}
    for tk in track:
        qs = [q for q in quarters if q["ticker"] == tk and q["time"] <= asof]
        if not qs:
            continue                                # crosscheck() bỏ qua im lặng, giữ y hệt
        q = max(qs, key=lambda r: r["time"])
        mine = oshares_at([tk], q["time"], _cache=cache)[tk]
        row = _row(mine)
        row["quarter_date"] = q["time"]
        row["ticker_financial"] = float(q["OShares"])
        # nhãn ĐÚNG như `crosscheck()` sẽ gắn, để so before/after ở cấp KẾT LUẬN chứ không chỉ
        # cấp số: "hết DIVERGENT" và "không đối soát được nữa" là hai chuyện khác hẳn nhau.
        if mine["value"] is None:
            row["kind"] = "NO_MODEL_VALUE"
        else:
            err = abs(float(mine["value"]) - row["ticker_financial"]) / row["ticker_financial"] \
                if row["ticker_financial"] else 0.0
            row["err_pct_vs_ticker_financial"] = err * 100
            row["kind"] = "DIVERGENT" if err > OL.EXPLAIN_TOL else "OK"
        xchk[tk] = row

    return {"publish": {"at": asof, "n": len(cur),
                        "rows": {t: _row(r) for t, r in sorted(cur.items())}},
            "check_retro": {"at": prev_asof, "synthetic": retro_synthetic, "n": len(back),
                            "rows": {t: _row(r) for t, r in sorted(back.items())}},
            "crosscheck": {"at": "ngày dòng quý của TỪNG mã", "n": len(xchk),
                           "rows": dict(sorted(xchk.items()))}}


legs = {"gate_on": measure()}                       # code hôm nay
_keep = OL._ais_certified
OL._ais_certified = lambda *_a, **_k: True          # hành vi TRƯỚC vòng 4
try:
    legs["gate_off"] = measure()
finally:
    OL._ais_certified = _keep

# ── DIFF theo ĐIỂM: mã nào đổi, đổi từ gì sang gì
diff = {}
for pt in ("publish", "check_retro", "crosscheck"):
    on_r, off_r = legs["gate_on"][pt]["rows"], legs["gate_off"][pt]["rows"]
    changed = {}
    for tk in sorted(set(on_r) | set(off_r)):
        a, b = off_r.get(tk), on_r.get(tk)          # a = trước (gate off), b = sau (gate on)
        if a == b:
            continue
        changed[tk] = {"before": a, "after": b, "held": tk in held}
    diff[pt] = {"n_changed": len(changed), "tickers": sorted(changed), "rows": changed}

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump({"asof": asof, "prev_asof": prev_asof, "retro_synthetic": retro_synthetic,
               "n_track": len(track), "n_held": len(held), "held": held,
               "legs": legs, "diff_gate_off_to_on": diff},
              fh, ensure_ascii=False, indent=1, sort_keys=True)

print(f"asof={asof} track={len(track)} held={len(held)} retro@{prev_asof}"
      f"{' (SYNTHETIC)' if retro_synthetic else ''}")
for pt in ("publish", "check_retro", "crosscheck"):
    d = diff[pt]
    hv = [t for t in d["tickers"] if t in held]
    print(f"  {pt:12s} n={legs['gate_on'][pt]['n']:3d}  đổi={d['n_changed']:2d} "
          f"{d['tickers']}  (đang giữ THẬT: {hv})")
print(f"-> {out_path}")
