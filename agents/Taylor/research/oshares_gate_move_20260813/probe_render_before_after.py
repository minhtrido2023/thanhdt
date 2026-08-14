#!/usr/bin/env python3
"""probe_render_before_after.py — CHUỖI Discord THẬT, khuôn CŨ vs khuôn MỚI, trên dữ liệu SỐNG.

Chạy `crosscheck()` thật (BQ, track set thật của 2026-08-13) rồi render bản ghi thu được bằng
ĐÚNG biểu thức f-string cũ (chép nguyên văn từ commit 8908640, dòng ~1182) và bằng
`_fmt_divergence()` mới. Mục đích: chứng minh lỗi hiển thị là THẬT trên mã ĐANG GIỮ, chứ không
phải suy ra bằng số học trên giấy.
"""
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import corp_action_daily as C                                              # noqa: E402
from oshares_live import _fetch                                            # noqa: E402

asof = sys.argv[1] if len(sys.argv) > 1 else C.today_ict()
pos = C.read_positions(asof=asof)
held = sorted({tk for a in pos.values() for tk in a["positions"]})
ex_today, ais_today, _ = C.triggered_today(asof)
track = sorted(set(held) | ex_today | ais_today)
diverge = C.crosscheck(asof, track, _fetch(track, asof))

# ── khuôn CŨ, chép nguyên văn (commit 8908640)
old = (f"⚠️ **Lệch nguồn Oshares** ({len(diverge)} mã, script KHÔNG tự chọn số): " +
       "; ".join(f"{d['ticker']}@{d['at']} corp-action "
                 f"{(d['oshares_live'] or 0):,.0f} vs bq_admin "
                 f"{d['ticker_financial']:,.0f}"
                 f" ({d.get('err_pct_vs_ticker_financial', 0):.2f}%)"
                 for d in diverge[:8]))
new = C._fmt_divergence(diverge)

print("=== KHUÔN CŨ (đang chạy tới commit 8908640) ===")
print(old)
print("\n=== KHUÔN MỚI ===")
print(new)
print("\n=== KIỂM ===")
bad = [d["ticker"] for d in diverge if d.get("oshares_live") is None]
print(f"mã bị khuôn cũ in thành 'corp-action 0 ... (0.00%)': {bad}")
print(f"trong đó ĐANG GIỮ THẬT: {[t for t in bad if t in held]}")
print(f"khuôn cũ chứa 'corp-action 0': {'corp-action 0' in old}  | khuôn mới: "
      f"{'corp-action 0' in new}")
print(f"khuôn cũ chứa '(0.00%)':      {'(0.00%)' in old}  | khuôn mới: {'(0.00%)' in new}")
