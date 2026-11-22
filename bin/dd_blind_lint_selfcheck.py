#!/usr/bin/env python3
"""Selfcheck cho bin/dd_blind_lint.py — rc 0 = PASS. Chạy cả `env -u TZ` và TZ lạ (không phụ thuộc TZ)."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dd_blind_lint as L  # noqa: E402

LINT = os.path.join(HERE, "dd_blind_lint.py")
ROOT = os.path.dirname(HERE)
FAILS = []


def check(name, cond):
    if not cond:
        FAILS.append(name)
    print(("PASS " if cond else "FAIL ") + name)


LEDGER = ["VLB", "PAT", "DGC"]
# (kind, dòng dương, dòng âm tương ứng)
CASES = [
    ("PRICE_TOKEN", "Giá đóng cửa 13/11/2026 = 72.700", "Giá bán xi măng 50.000 đ/tấn"),
    ("PRICE_TOKEN", "vùng giá 55,0–66,7k so với thị giá", "Dung Quất 148k thùng/ngày"),
    ("PRICE_TOKEN", "Cổ phiếu đang ở 71.000đ", "Tỷ giá trung tâm 25.627 đ/USD"),
    ("MULTIPLE", "Ngành PE 14,2 hiện nay", "So sánh PE 2025 với 2026"),
    ("MULTIPLE", "EV/EBITDA 8x của peer", "ROE 14% và đòn bẩy 2x"),
    ("MARKET_CAP", "Vốn hoá 12.000 tỷ", "lãi vay vốn hoá; nợ đến hạn 12 tháng"),
    ("TICKER", "Công ty VLB báo lãi", "Vlb viết thường không có trong sổ, file .csv"),
    ("PATH_LEAK", "xem agents/Taylor/research/dd_VLB_20261122/macro.md", "xem agents/Taylor/research/macro.md"),
    ("PATH_LEAK", "file VLB_DD_report.md", "file report.md"),
    ("FORWARD_RETURN", "forward return 1M của mã là cao", "Không thấy forward return nào"),
    ("FORWARD_RETURN", "kỳ vọng +12% trong 1 tháng", "kỳ vọng Q3 tăng nhờ nhu cầu"),
    ("VERDICT_LEAK", "cổ phiếu này đang rẻ", "giá điện đắt hơn năm trước"),
    ("VERDICT_LEAK", "Kết luận QUALIFY cho mã", "Điều kiện chất lượng chung"),
]
TABLE = "| Mã | P/E | ROE |\n|---|---|---|\n| X | 12,3 | 15% |\n"


def kinds(text, **kw):
    kw.setdefault("ledger", LEDGER)
    v, ex = L.lint_text(text, **kw)
    return {k for _, k, _ in v}, ex


def run_cases(label=""):
    bad = []
    for k, pos, neg in CASES:
        if k not in kinds(pos)[0]:
            bad.append("dương " + k + ": " + pos)
        if k in kinds(neg)[0]:
            bad.append("âm " + k + ": " + neg)
    if "MULTIPLE" not in kinds(TABLE)[0]:
        bad.append("dương bảng P/E")
    if "MULTIPLE" in kinds("| Mã | ROE |\n|---|---|\n| X | 15% |\n")[0]:
        bad.append("âm bảng không có P/E")
    return bad


def main():
    bad = run_cases()
    check("bộ ca dương+âm (%d ca + bảng)" % len(CASES), not bad)
    for b in bad:
        print("   ", b)
    # --ticker riêng, không dùng sổ
    k, _ = kinds("Mã ABC tốt", tickers=["abc"], ledger=None)
    check("--ticker khớp không phân biệt hoa/thường", "TICKER" in k)
    k, _ = kinds("VLB và PAT", tickers=["abc"], ledger=None)
    check("--ticker: mã sổ không bị báo khi chỉ định ticker", "TICKER" not in k)
    k, _ = kinds("đọc dd_ABC_2026", tickers=["abc"], ledger=None)
    check("PATH_LEAK theo --ticker", "PATH_LEAK" in k)
    # mode
    v, _ = L.lint_text("cổ phiếu đang rẻ", None, None, "skeptic")
    check("mode skeptic bỏ VERDICT_LEAK", not v)
    # miễn
    v, ex = L.lint_text("Giá đóng cửa = 72.700 <!-- blind-ok: đối chiếu -->", None, None, "sector")
    check("blind-ok miễn dòng + đếm", not v and ex >= 1)
    # mutation: tắt từng loại => ít nhất 1 ca fail
    saved = {n: getattr(L, n) for n in ("_PRICE", "_NUM_K", "_MULT", "_MCAP", "_FWD", "_VERD", "_PATH", "_TBL_PE")}
    muts = {
        "PRICE_TOKEN": ["_PRICE", "_NUM_K"], "MULTIPLE": ["_MULT", "_TBL_PE"], "MARKET_CAP": ["_MCAP"],
        "FORWARD_RETURN": ["_FWD"], "VERDICT_LEAK": ["_VERD"], "PATH_LEAK": ["_PATH"],
    }
    import re
    for kind, attrs in muts.items():
        for a in attrs:
            setattr(L, a, re.compile(r"(?!x)x") if a in ("_NUM_K", "_TBL_PE") else [])
        killed = bool(run_cases())
        for a in attrs:
            setattr(L, a, saved[a])
        check("mutation tắt %s => có ca fail" % kind, killed)
    orig = L.lint_text
    L.lint_text = lambda *a, **kw: ([x for x in orig(*a, **kw)[0] if x[1] != "TICKER"], 0)
    check("mutation tắt TICKER => có ca fail", bool(run_cases()))
    L.lint_text = orig
    # CLI: rc
    env = dict(os.environ)
    env.pop("MIKE_BLIND_LINT", None)
    with tempfile.TemporaryDirectory() as td:
        f_bad, f_ok = os.path.join(td, "bad.md"), os.path.join(td, "ok.md")
        open(f_bad, "w", encoding="utf-8").write("Giá đóng cửa = 72.700\n")
        open(f_ok, "w", encoding="utf-8").write("Ngành điện, giá điện bán lẻ ổn định.\n")

        def rc(*args, e=env):
            return subprocess.run([sys.executable, LINT, *args], env=e, capture_output=True, text=True)
        r = rc(f_bad)
        check("rc=1 khi có vi phạm; định dạng file:dòng: LOẠI", r.returncode == 1 and (f_bad + ":1: PRICE_TOKEN") in r.stdout)
        check("rc=0 khi sạch", rc(f_ok).returncode == 0)
        check("rc=2 file không tồn tại", rc(os.path.join(td, "none.md")).returncode == 2)
        check("rc=2 thiếu đối số", rc().returncode == 2)
        e2 = dict(env, MIKE_BLIND_LINT="off")
        r = rc(f_bad, e=e2)
        check("MIKE_BLIND_LINT=off => rc=0 + cảnh báo", r.returncode == 0 and "BỊ TẮT" in r.stderr)
        r = rc(f_bad, "--json")
        check("--json hợp lệ", r.returncode == 1 and '"kind": "PRICE_TOKEN"' in r.stdout)
    # file thật
    def real(p, *a):
        return subprocess.run([sys.executable, LINT, os.path.join(ROOT, p), *a], env=env, capture_output=True, text=True)
    for p in ("agents/Taylor/research/dd_PAT_20261114/brief.md", "agents/Taylor/research/dd_PAT_20261114/brief_r2.md"):
        if os.path.exists(os.path.join(ROOT, p)):
            r = real(p)
            check("brief PAT bị bắt giá: " + p.split("/")[-1], r.returncode == 1 and "PRICE_TOKEN" in r.stdout)
    p = "kb/data_registry/market-state/sector_read_da_xay_dung_dnb_20261122.md"
    if os.path.exists(os.path.join(ROOT, p)):
        r = real(p)
        check("sector_read VLB 22/11 bị bắt PATH_LEAK", "PATH_LEAK: dd_VLB_20261122" in r.stdout)
    print("TZ=%r" % os.environ.get("TZ"))
    print("KẾT QUẢ: %s" % ("PASS" if not FAILS else "FAIL " + str(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
