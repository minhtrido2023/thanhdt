#!/usr/bin/env python3
"""Acceptance V3 (arch-review vòng 2, E1): ca CÓ tỉ suất được CÔNG BỐ **và** có lệch nguồn.

Acceptance vòng 1 vô nghĩa vì cả 2 daily report 09-23 công bố 0 dòng bảng + 0 tỉ suất văn xuôi
⇒ chạy với `published = {}`, không thể phân biệt nhánh chặn mới. Ở đây dựng đúng ca đó, và
KHÔNG monkeypatch `entitled_gross` (patch tầng dưới `dar.*`) để cây cầu thật được đi qua.

Chạy:  $DNA_PYEXE acceptance_v3_endtoend.py <đường dẫn cây (worktree hoặc canonical)>
"""
import io
import os
import subprocess
import sys
import tempfile

TREE = sys.argv[1] if len(sys.argv) > 1 else "/home/trido/thanhdt/WorkingClaude/mike"
sys.path.insert(0, os.path.join(TREE, "bin"))
import dividend_adjusted_return as dar          # noqa: E402
import report_return_gate as g                  # noqa: E402

FAILS = []


def check(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got={got!r} want={want!r}")
    if not ok:
        FAILS.append(name)


def adj(tk, ex, ps, kind, vcheck, vcash):
    a = dar.Adjustment(ticker=tk, ex_date=ex, last_cum_date=ex, last_cum_price=30_000.0,
                       per_share=ps)
    a.kind, a.vendor_check, a.vendor_cash = kind, vcheck, vcash
    return a


ADJS = [adj("ZZZ", "2026-09-10", 1_000.0, "UNVERIFIED", "mismatch", 1_500.0)]


def run_case(body):
    """(rc, output) của cổng THẬT trên một báo cáo tạm — chỉ patch broker/giá/dar, KHÔNG patch
    `entitled_gross`."""
    keep_g = {k: getattr(g, k) for k in ("broker_positions", "excluded_tickers")}
    keep_d = {k: getattr(dar, k) for k in ("resolve_dividends", "broker_qty", "_qty_at")}
    g.broker_positions = lambda acct, asof, **kw: {"ZZZ": (100.0, 27_800.0, 24_464.0)}
    g.excluded_tickers = lambda lb: set()
    dar.resolve_dividends = lambda tks, s, e: list(ADJS)
    dar.broker_qty = lambda acct: {"stub": True}
    dar._qty_at = lambda qmap, a, frame=None: 100.0
    with tempfile.NamedTemporaryFile("w", suffix="_SpaceX_report_2026-09-24.md", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(body)
        path = fh.name
    buf = io.StringIO()
    try:
        rc = g.run_gate(path, out=buf)
    finally:
        for k, v in keep_g.items():
            setattr(g, k, v)
        for k, v in keep_d.items():
            setattr(dar, k, v)
        os.unlink(path)
    return rc, buf.getvalue()


def alert(out_text, fname):
    p = subprocess.run([os.path.join(TREE, "bin", "vendor_mismatch_alert.sh"), fname,
                        "trading_report", "--dry-run"],
                       input=out_text, capture_output=True, text=True)
    return p.returncode, p.stdout


print("== CA 1: báo cáo CÓ công bố tỉ suất cho chính mã lệch nguồn ==")
PUBLISHED = "## Vị thế\n\n| Mã | KL | % lãi/lỗ |\n|---|---|---|\n| ZZZ | 100 | -12,00% |\n"
rc1, out1 = run_case(PUBLISHED)
check("cổng CHẶN (rc=1)", rc1, 1)
check("có khối cảnh báo cho người đọc", "LỆCH NGUỒN VENDOR" in out1, True)
check("có dòng máy đọc, cờ published=1",
      "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-10|1000|1500|1" in out1, True)
check("chỉ đích danh Winston", "Winston" in out1, True)
arc1, atxt1 = alert(out1, "SpaceX_daily_report_2026-09-24.md")
check("alert shell: rc=10 (có lệch nguồn)", arc1, 10)
check("alert shell: nhận đúng blocked=1", "blocked=1" in atxt1, True)

print("\n== CA 2: KHÔNG công bố tỉ suất mã đó ⇒ cổng cho qua (rc=0) — ca warning từng chết trong log ==")
rc2, out2 = run_case("## Không công bố tỉ suất mã nào\n")
check("cổng KHÔNG chặn (rc=0)", rc2, 0)
check("vẫn in cảnh báo (không im lặng)", "LỆCH NGUỒN VENDOR" in out2, True)
check("dòng máy đọc vẫn có, cờ published=0",
      "VENDOR_MISMATCH_ALERT|SpaceX|ZZZ|2026-09-10|1000|1500|0" in out2, True)
arc2, atxt2 = alert(out2, "SpaceX_daily_report_2026-09-24.md")
check("alert shell VẪN bắn dù rc=0 (đây là điểm V3)", arc2, 10)
check("alert shell: blocked=0", "blocked=0" in atxt2, True)

print("\n== CA 3: không lệch nguồn ⇒ im lặng hoàn toàn (không báo động giả) ==")
ADJS[:] = [adj("ZZZ", "2026-09-10", 1_000.0, "CASH_CONFIRMED", "match", 1_000.0)]
rc3, out3 = run_case("## Không công bố tỉ suất mã nào\n")
check("rc=0", rc3, 0)
check("không có dòng máy đọc nào", "VENDOR_MISMATCH_ALERT" in out3, False)
arc3, _ = alert(out3, "SpaceX_daily_report_2026-09-24.md")
check("alert shell: rc=0 (không gửi gì)", arc3, 0)

print()
if FAILS:
    print(f"❌ ACCEPTANCE FAIL — {len(FAILS)}: " + "; ".join(FAILS))
    sys.exit(1)
print("✅ ACCEPTANCE PASS")
