#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutant cho code MỚI của nhánh feat/fund-step4-benchmark-20261014 (quỹ bước 4 phần 2).

Mỗi mutant: chép bin/ của worktree sang /tmp, thay ĐÚNG MỘT chỗ (chuỗi phải xuất hiện đúng 1 lần),
chạy selfcheck liên quan với TZ đã gỡ. Mutant "chết" khi ít nhất một selfcheck rc != 0.

Dùng: python3 mutants.py [--only A1,B2] [--tz Pacific/Kiritimati] [--python /path/python]
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

WT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-step4-1014"
VT, VS = "vnindex_total_return.py", "vnindex_total_return_selfcheck.py"
NS, NSS = "nav_sleeve.py", "nav_sleeve_selfcheck.py"
NP, NPS = "nav_period_returns.py", "nav_period_benchmark_selfcheck.py"
RG, PT, PTS = "report_delivery_gate.py", "period_table_32.py", "period_table_32_selfcheck.py"

M = [
    # ---------------- A: VN-Index có cổ tức
    ("A1", VT, 'u["mc1"] = u.P1 * u.S1', 'u["mc1"] = u.Price * u.OShares', "vốn hoá phiên t thay t-1", (VS,)),
    ("A2", VT, 'd = d[(d.event_status == "executed") & (d.value_per_share > 0)].copy()',
     'd = d[(d.value_per_share > 0)].copy()', "bỏ lọc executed", (VS,)),
    ("A3", VT, '"tr_net": _fmt(chain(prev["tr_net"], ratio, r.y, 1.0 - DIV_TAX_RATE), 15),',
     '"tr_net": _fmt(chain(prev["tr_net"], ratio, r.y, 1.0), 15),', "k của tr_net = 1", (VS,)),
    ("A4", VT, 'base = s.hose & s.t1_ok & s.P1.gt(0)', 'base = s.hose & s.P1.gt(0)',
     "bỏ điều kiện phiên liền trước", (VS,)),
    ("A5", VT, 'd = d.drop_duplicates(["ticker", "exright_date", "value_per_share", "dividend_year",\n                           "dividend_stage_vi"])',
     'd = d.drop_duplicates(["ticker", "exright_date"])', "gộp nhầm hai đợt cùng ngày", (VS,)),
    ("A6", VT, 'd = d.drop_duplicates(["ticker", "exright_date", "value_per_share", "dividend_year",\n                           "dividend_stage_vi"])',
     'd = d', "không bỏ dòng trùng", (VS,)),
    ("A7", VT, '(tt < np.datetime64(b))', '(tt <= np.datetime64(b))', "ngày rời sàn tính cả ngày cuối", (VS,)),
    ("A8", VT, 'if dy > SEALED_Y_TOL or di > SEALED_IDX_TOL:', 'if False:', "không kiểm dòng sealed", (VS,)),
    ("A9", VT, 'raise BuildRefused(f"DNSE có', 'print(f"DNSE có', "không chặn khi BQ thiếu phiên", (VS,)),
    ("A10", VT, '    if d > last:\n', '    if False:\n', "G1 phiên cuối tắt", (VS,)),
    ("A11", VT, 'elif abs(r["vnindex"] / s2 - 1) > G2_TOL:', 'elif False:', "G2 tắt", (VS,)),
    ("A12", VT, 'if not ing or _d(ing) < r["date"]:', 'if False:', "G3 tắt", (VS,)),
    ("A13", VT, 'if abs(dev) > G4_MC_TOL:', 'if False:', "G4 vốn hoá tắt", (VS,)),
    ("A14", VT, 'if abs(synth - off) > G5_TOL:', 'if False:', "G5 tắt", (VS,)),
    ("A15", VT, '(r["date"].isoformat(), r["max_dy_ticker"]) not in acks:', 'False:', "G6 tắt", (VS,)),
    ("A16", VT, 'if not v or (r["date"] - _d(v)).days > G7_MAX_AGE_DAYS:', 'if False:', "G7 tắt", (VS,)),
    ("A17", VT, 'if r["osh_missing_max_pct"] is not None and r["osh_missing_max_pct"] > G8_MAX_SHARE:',
     'if False:', "G8 tắt", (VS,)),
    ("A18", VT, '        if not errs:\n            for k in ("tr_gross", "tr_net"):',
     '        if True:\n            for k in ("tr_gross", "tr_net"):', "cổng hỏng vẫn in số có cổ tức", (VS,)),
    ("A19", VT, 'r["status"] = "sealed" if n - 1 - j >= SEAL_AFTER else "provisional"',
     'r["status"] = "sealed"', "đóng dấu sealed ngay", (VS,)),
    ("A20", VT, 'if abs(dn) > G4_MAX_N_CHANGE_FRAC * p["n_members"]:', 'if False:', "G4 số mã tắt", (VS,)),
    # ---------------- B: chuỗi phần bot quản lý
    ("B1", NS, 'recv = sum(r["gross_vnd"] for r in transfers', 'recv = 0 * sum(r["gross_vnd"] for r in transfers',
     "bỏ recv", (NSS,)),
    ("B2", NS, 'out.append({"date": r["date"], "amount_vnd": r["amount_vnd"],',
     'out.append({"date": r["date"], "amount_vnd": r["gross_vnd"] or r["amount_vnd"],', "dòng vào (b) dùng số gộp", (NSS,)),
    ("B3", NS, 'return {e["ticker"] for e in scope if e["from"] <= d and (e["to"] is None or d <= e["to"])}',
     'return {e["ticker"] for e in scope if e["from"] <= d and (e["to"] is None or d <= e["to"])} | {"PNJ"}',
     "phạm vi lẫn excluded_tickers (PNJ)", (NSS,)),
    ("B4", NS, 'qty[p["symbol"]] = qty.get(p["symbol"], 0) + p["openQuantity"]', 'qty[p["symbol"]] = p["openQuantity"]',
     "ghi đè lô", (NSS,)),
    ("B5", NS, 'if str(rec.get("account_no")) != str(account_no):\n                    continue\n                if rec.get("kind") != "positions":',
     'if rec.get("kind") != "positions":', "positions_at bỏ lọc account (§12)", (NSS,)),
    ("B6", NS, 'return qty, best["ts"], gap, gap > POS_WINDOW_S', 'return qty, best["ts"], gap, False',
     "không gắn cờ vị thế lệch giờ", (NSS,)),
    ("B7", NS, '        if r is None:\n            out.append(', '        if False:\n            out.append(', "S1 tắt", (NSS,)),
    ("B8", NS, '            if got != dq:', '            if False:', "S2 tắt", (NSS,)),
    ("B9", NS, ' and _drop_persists(div_recv, i + 1, v0)', '', "tin bản ghi số dư hỏng", (NSS,)),
    ("B10", NS, '    if base_b <= 0 or base_b < MIN_BASE_FRAC * cap:\n        raise SleeveError(f"S7',
     '    if False:\n        raise SleeveError(f"S7', "S7 tắt", (NSS,)),
    ("B11", NS, 'if old and olds != {new_md5}:', 'if False:', "S6 ghi tắt", (NSS,)),
    ("B12", NS, 'if abs(float(h["nav_a"]) - nav) > 0.5:', 'if False:', "consumer không kiểm nav_a", (NSS,)),
    ("B13", NS, 'if got is None or not (got[0] and math.isfinite(got[0])):', 'if False:', "S3 tắt", (NSS,)),
    ("B14", NS, '"amount_vnd": gross * (1 - DIV_TAX_RATE)}', '"amount_vnd": gross}', "đề xuất cổ tức số gộp", (NSS,)),
    ("B15", NS, '(r["date"] is None or d < r["date"]))', '(r["date"] is None or d <= r["date"]))',
     "recv còn tính ngày tiền về", (NSS,)),
    ("B16", NS, 'if md5s != {scope_md5(scope)}:', 'if False:', "S6 consumer tắt", (NSS,)),
    ("B17", NS, '        if h["blocked_reason"]:\n            raise SleeveUnavailable', '        if False:\n            raise SleeveUnavailable',
     "consumer bỏ qua dòng bị chặn", (NSS,)),
    # ---------------- C: nav_period_returns (khối benchmark, --sleeve)
    ("C1", NP, 'bm = benchmark(p["from_date"], p["to_date"])', 'bm = benchmark(out["inception"]["from_date"], p["to_date"])',
     "mốc chỉ số không theo dòng sổ của kỳ", (NPS,)),
    ("C2", NP, '("excess_vs_tr_pp", "vnindex_tr_pct")', '("excess_vs_tr_pp", "vnindex_tr_gross_pct")',
     "chênh tính theo gross dù cờ = net", (NPS,)),
    ("C3", NP, 'if bm.get(col) is not None else None', 'if bm.get(col) is not None else 0.0',
     "thiếu số ⇒ chênh 0 thay vì None", (NPS,)),
    ("C4", NP, '    out["series"] = "bot"\n', '', "chuỗi b không gắn nhãn", (NPS,)),
    ("C5", NP, '                return 3\n', '                return 0\n', "--sleeve bot không có số vẫn rc=0", (NPS,)),
    ("C6", NP, '    if benchmark is not None:\n        for key', '    if True:\n        benchmark = benchmark or (lambda a, b: {})\n        for key',
     "luôn thêm khối benchmark (phá byte-identical)", (NPS,)),
    ("C7", VT, 'out["vnindex_tr_pct"] = res.get(f"vnindex_{kind}_pct")', 'out["vnindex_tr_pct"] = res.get("vnindex_tr_net_pct")',
     "cờ Q2 không có tác dụng", (NPS,)),
    ("C8", VT, 'out["vnindex_tr_pct"] = res.get(f"vnindex_{kind}_pct")',
     'out["vnindex_tr_pct"] = res.get(f"vnindex_{kind}_pct") or res.get("vnindex_price_pct")',
     "rơi im lặng về chỉ số giá", (NPS,)),
    ("C9", VT, '    while not _calendar_session(prev):\n        prev -= dt.timedelta(days=1)\n    if prev not in dates:',
     '    if True:\n        return d, None\n    if prev not in dates:', "dòng sổ ngày nghỉ không ánh xạ phiên", (NPS,)),
    ("C10", VT, '        return DEFAULT_REPORT_TR_KIND\n    with open', '        return "tr_gross"\n    with open',
     "mặc định Q2 sai (gross)", (NPS,)),
    # ---------------- D: bảng 3.2 + cổng giao báo cáo
    ("D1", PT, 'if abs(v - w) > CELL_TOL_PP + 1e-9:', 'if abs(v - w) > 0.05:', "dung sai 0,05 thay 0,005", (PTS,)),
    ("D2", PT, 'if c in (COL_TR, COL_XT) and not sleeve:', 'if False:', "Q9 tắt (cột có cổ tức thiếu số vẫn gửi)", (PTS,)),
    ("D3", PT, '            if w is None:\n                if v != NO_NUMBER:', '            if w is None:\n                if False:',
     "CLI không có số mà bảng ghi số vẫn qua", (PTS,)),
    ("D4", PT, '        if series_installed():\n', '        if False:\n', "bỏ cột có cổ tức vẫn qua", (PTS,)),
    ("D5", PT, 'if foot and foot not in text:', 'if False:', "không kiểm chú thích", (PTS,)),
    ("D6", PT, '            if nums:\n', '            if False:\n', "dòng lạ có số vẫn qua", (PTS,)),
    ("D7", PT, 'bad = [f"{c}={raw!r}" for c, (raw, v) in cells.items() if v != NO_NUMBER]', 'bad = []',
     "chuỗi b chưa có số mà bảng ghi số vẫn qua", (PTS,)),
    ("D8", PT, '    tr = bm.get("vnindex_tr_pct")\n', '    tr = bm.get("vnindex_tr_pct") or bm.get("vnindex_price_pct")\n',
     "render thay giá vào cột có cổ tức", (PTS,)),
    ("D9", RG, '                    _check_benchmark_table(report)\n', '', "deliver() không gọi cổng bảng", (PTS,)),
    ("D10", PT, '    rc, j, err = cli(account, report_date, False)\n    if rc != 0 or not j:',
     '    rc, j, err = cli(account, report_date, False)\n    if not j:', "bỏ qua rc≠0 của CLI", (PTS,)),
    ("D11", RG, 'return pt.run_cli(account, d, sleeve, bin_dir=str(ROOT / "bin"))', 'return pt.run_cli(account, d, sleeve)',
     "cổng gọi CLI của cây đang chạy thay cây canonical", (PTS,)),
]


def run(m, tz, py):
    mid, fn, old, new, why, checks = m
    src = os.path.join(WT, "bin", fn)
    with open(src, encoding="utf-8") as f:
        text = f.read()
    n = text.count(old)
    if n != 1:
        return mid, "LỖI-MUTANT", f"chuỗi gốc xuất hiện {n} lần trong {fn}"
    tmp = tempfile.mkdtemp(prefix=f"mut_{mid}_")
    try:
        b = os.path.join(tmp, "bin")
        shutil.copytree(os.path.join(WT, "bin"), b, symlinks=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
        with open(os.path.join(b, fn), "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        env["WC_ROOT"] = "/home/trido/thanhdt/WorkingClaude"   # code thật (trading_bot) — selfcheck không ghi data/
        if tz:
            env["TZ"] = tz
        rcs = []
        for c in checks:
            cp = subprocess.run([py, os.path.join(b, c)], capture_output=True, text=True, env=env,
                                timeout=600)
            rcs.append((c, cp.returncode, (cp.stderr or cp.stdout).strip().splitlines()[-1:] or [""]))
        dead = any(rc != 0 for _, rc, _ in rcs)
        return mid, "CHẾT" if dead else "SỐNG", f"{why} | " + "; ".join(f"{c} rc={rc} {t[0][:140]}" for c, rc, t in rcs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--tz")
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    sel = [m for m in M if not a.only or m[0] in a.only.split(",")]
    alive = 0
    for m in sel:
        mid, st, msg = run(m, a.tz, a.python)
        alive += st != "CHẾT"
        print(f"{mid:4s} {st:11s} {msg}")
    print(f"TỔNG {len(sel)} mutant, {len(sel) - alive} chết, {alive} sống/lỗi")
    return 1 if alive else 0


if __name__ == "__main__":
    raise SystemExit(main())
