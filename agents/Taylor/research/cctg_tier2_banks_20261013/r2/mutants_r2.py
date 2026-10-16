#!/usr/bin/env python3
"""Mutation run vòng 2 cho cctg_tier2_series_selfcheck.py. Mỗi mutant: chép cây sang thư mục tạm, sửa đúng 1 chỗ,
chạy selfcheck — rc!=0 = BỊ BẮT, rc==0 = SỐNG. Dùng: mutants_r2.py <WorkingClaude dir> [--old-control]
--old-control: chạy mutant MC' trên selfcheck+writer của HEAD (trước vòng 2) để chứng minh nó SỐNG ở đó."""
import os, shutil, subprocess, sys, tempfile

SRC = os.path.abspath(sys.argv[1])
PY = "/home/trido/thanhdt/wc_venv/bin/python"
T2 = '"cctg_rate_vn_" + "tier" + "2_events.csv"'
W = "append_cctg_rate.py"
SC = "cctg_tier2_series_selfcheck.py"
SH = "refresh_deposit_cctg_weekly.sh"
READ = f'''
def _t2_max(_dir):
    import csv as _csv, os as _os
    _p = _os.path.join(_dir, {T2})
    if not _os.path.exists(_p):
        return None
    with open(_p, encoding="utf-8") as _f:
        _v = [float(_r["cctg_rate"]) for _r in _csv.DictReader(_f)]
    return max(_v) if _v else None
'''
# (tên, file, cũ, mới[, env])  |  APPEND: (tên, file, đoạn nối)
TEXT = [
 # --- A1 ghi song song
 ("A1  bỏ flock (khoá no-op)", W, "        fcntl.flock(lk, fcntl.LOCK_EX)", "        pass"),
 ("A1' khoá chỉ bọc đoạn ghi, không bọc đọc", W, "        stack.enter_context(_tier2_flock(csv_path))  # A1: đọc→ghi→sidecar là MỘT đoạn găng\n", "        pass\n"),
 # --- A3 key-hop
 ("A3a bỏ chặn đổi kiểu mệnh giá ''<->10tr/100tr", W, "        if (denom and has_blank and not has_denom) or (not denom and has_denom):", "        if False:"),
 ("A3a' --force của AGENT cũng qua (không phân biệt)", W, "    if same_bank and not force:", "    if same_bank and not (force or is_agent):"),
 ("A3b bỏ kiểm khoá mới cùng ngân hàng (agent)", W, "        if min(gaps) >= NONINERT_DELTA_PP:", "        if False:"),
 ("A3c bỏ kiểm dải ngân hàng chưa có dòng", W, "    if not (lo < rate < hi):", "    if False:"),
 ("A3c' file rỗng + agent: cho qua", W, "    if not others:\n        return (", "    if not others:\n        return None\n        return ("),
 ("A3  tắt toàn bộ guard khoá mới", W, "    if is_tier2 and not rows:  # A3", "    if False and is_tier2 and not rows:  # A3"),
 ("A3d dải dùng max+5pp (nới)", W, "lo, hi = min(others) - NONINERT_DELTA_PP, max(others) + NONINERT_DELTA_PP", "lo, hi = min(others) - NONINERT_DELTA_PP, max(others) + 5.0"),
 # --- B6 thông báo
 ("B6a SKIP luôn rc=0 dù KHÁC sản phẩm/lợi suất", W, "        if not same:\n", "        if False:\n"),
 ("B6b thông báo SKIP tier2 không nêu khoá", W, 'print(f"SKIP: {_tier2_key_str(bank, denom)} effective_date', 'print(f"SKIP: effective_date'),
 ("B6c thông báo lệch tier2 không nêu khoá", W, 'sys.exit(f"ERROR: {_tier2_key_str(bank, denom)} rate {args.rate:g}%', 'sys.exit(f"ERROR: rate {args.rate:g}%'),
 ("B6d 'không mới hơn' tier2/6m lại nhắc cctg_events_df()", W, "    if eff <= last_date and (is_tier2 or is_6m):", "    if False:"),
 # --- B4 pin
 ("B4a TIER2_BANKS thêm HDB", W, 'TIER2_BANKS = ("VPB", "MB", "TCB", "ACB")', 'TIER2_BANKS = ("VPB", "MB", "TCB", "ACB", "HDB")'),
 ("B4b TIER2_DENOMS thêm 1ty", W, 'TIER2_DENOMS = ("10tr", "100tr")', 'TIER2_DENOMS = ("10tr", "100tr", "1ty")'),
 ("B4c --product khoảng trắng qua được", W, '(args.product or "").strip(), (args.holding or "").strip()', '(args.product or ""), (args.holding or "").strip()'),
 ("B4d bỏ mốc NGƯỜI khỏi delta guard tier2", W, "    bases = [b for b in (current_rate, last_human_rate) if b is not None]", "    bases = [b for b in (current_rate,) if b is not None]"),
 ("B4e sidecar chung theo ngân hàng (bỏ mệnh giá)", W, '''return f"cctg_tier2_{bank}_{denom or 'na'}_last_auto_sources.json"''', '''return f"cctg_tier2_{bank}_na_last_auto_sources.json"'''),
 # --- B9
 ("B9  help --rate lại nói 'Big-4 CCTG rate'", W, 'help="CCTG rate, %%/yr (12m/6m: highest-of-Big-4', 'help="Big-4 CCTG rate, %%/yr (12m/6m: highest-of-Big-4'),
 # --- B7/B8 wrapper
 ("B7a bỏ --timeout/--max-turns khỏi dispatch", SH, "--timeout 1200 --max-turns 80 ", ""),
 ("B7b bỏ ràng buộc chuỗi 5 làm SAU CÙNG", SH, "THỨ TỰ BẮT BUỘC: làm chuỗi 5 SAU CÙNG.", "THỨ TỰ: tuỳ bạn."),
 ("B7c post-condition không báo chuỗi thiếu", SH, 'print(",".join(x for x in REQUIRED if x not in seen))', 'print("")'),
 ("B7d bỏ nhánh 'dừng giữa chừng' (chuỗi cũ bị báo hỏng)", SH, 'elif [ "${CONFIRMED:-no}" = "yes" ] && [ -n "${SEEN_SERIES:-}" ]', 'elif false && [ -n "${SEEN_SERIES:-}" ]'),
 ("B7e nhánh 'giữa chừng' lại nói 'KHÔNG có kết quả xác nhận được'", SH, "CHƯA có kết quả xác nhận được cho:", "KHÔNG có kết quả xác nhận được cho:"),
 ("A1c bỏ câu chạy TUẦN TỰ chuỗi 5", SH, "Chạy TUẦN TỰ từng lệnh chuỗi 5", "Chạy từng lệnh chuỗi 5"),
 ("B8  chuỗi 5 được mở question lại", SH, "(status, KHÔNG BAO GIỜ question)", "(status hoặc question)"),
 ("B8' bỏ dòng 'CHUỖI 5 KHÔNG mở question'", SH, "CHUỖI 5 KHÔNG mở question:", "Chuỗi 5 ghi chú:"),
 # --- giữ lại từ vòng 1 (cốt lõi)
 ("M01 tier2 ghi vào file 12M", W, "csv_path = CSV_PATH_TIER2 if is_tier2 else", "csv_path = CSV_PATH if is_tier2 else"),
 ("M05 tắt chặn lệch >=1pp cho tier2 (nhánh tier2)", W, "if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force and is_tier2:", "if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force and False:"),
 ("M03 khoá bỏ bank+denom", W, 'rows = [r for r in rows if (r.get("bank"), r.get("denomination") or "") == (bank, denom)]', "rows = list(rows)"),
 ("M07 nới lệch 2 nguồn 0,1->0,5", W, "CROSS_SOURCE_TOLERANCE_PP = 0.1 ", "CROSS_SOURCE_TOLERANCE_PP = 0.5 "),
 ("M10 agent dùng manual_verify", W, 'if is_dispatched_agent and args.source != "web_crosscheck_auto":', "if False:"),
 ("M11 --bank lọt vào 12m/6m", W, "if not is_tier2 and tier2_given:", "if False:"),
 ("M18 cho phép lợi suất 0", W, "RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0", "RATE_MIN_PCT, RATE_MAX_PCT = -1.0, 30.0"),
 ("M19 lượt tier2 rò global sang 12m", W, "    csv_path = CSV_PATH_TIER2 if is_tier2 else (CSV_PATH_6M if is_6m else CSV_PATH)", "    csv_path = CSV_PATH_TIER2 if is_tier2 else (CSV_PATH_6M if is_6m else CSV_PATH)\n    globals()['CSV_PATH'] = csv_path"),
 ("M23 wrapper truyền tier2 cho trend check", SH, '"$PY" deposit_cctg_trend_check.py >> "$LOG" 2>&1', '"$PY" deposit_cctg_trend_check.py --with-tier2 >> "$LOG" 2>&1'),
 # --- A2: chính selfcheck bị lấy lại đường dẫn production
 ("A2  selfcheck bỏ ghim sys.path về HERE sau dcf import", SC, "sys.path.insert(0, HERE)\nTREE_MODULES", "TREE_MODULES"),
]
APPEND = [
 ("MC' current_cctg_rate_checked() max với file tier2 (effective 15%, kill-switch armed)", "cctg_rate_vn.py", READ + '''
_orig_ccr = current_cctg_rate_checked
def current_cctg_rate_checked(asof=None):
    out = _orig_ccr(asof)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    if m is not None and out[0] is not None and m > out[0]:
        return (m,) + tuple(out[1:])
    return out
'''),
 ("MB1 consumer_deposit_rate_detail max với tier2 [chạy kèm env OVERLAY=0 bên ngoài]", "deposit_rate_vn.py", READ + '''
_orig_cdd = consumer_deposit_rate_detail
def consumer_deposit_rate_detail(asof=None):
    out = _orig_cdd(asof)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    if m is not None and m > out["rate_pct"]:
        out = dict(out, rate_pct=m)
    return out
'''),
 ("MB2 trend.main() chèn dòng tier2 vào series_data", "deposit_cctg_trend_check.py", READ + '''
import cctg_rate_vn as _c0
_orig_main = main
def main():
    global _load_series
    _ols = _load_series
    def _ls():
        out = _ols()
        m = _t2_max(os.path.dirname(_c0._EVENTS_CSV))
        if m is not None:
            out["cctg_6m"] = out["cctg_6m"] + [("2026-10-13", m)]
        return out
    _load_series = _ls
    try:
        return _orig_main()
    finally:
        _load_series = _ols
'''),
 ("MB5a dcf discount_rate đọc WORKDIR/data/cctg_*.csv (glob)", "dcf_valuation.py", '''
_orig_dr5 = discount_rate
def discount_rate(asof, erp=ERP):
    import glob as _g, csv as _csv
    _v = []
    for _p in _g.glob(os.path.join(os.path.dirname(_dep._EVENTS_CSV), "cctg_" + "*" + ".csv")):
        with open(_p, encoding="utf-8") as _f:
            _v += [float(_r["cctg_rate"]) for _r in _csv.DictReader(_f)]
    return max(_orig_dr5(asof, erp), (max(_v) + erp) / 100.0) if _v else _orig_dr5(asof, erp)
'''),
 ("M41 rating_8l.py đọc tier2 bằng đường dẫn ghép chuỗi (khoảng hở vòng 1)", "rating_8l.py", '\n_T2X = os.path.join("data", "cctg_rate_vn_" + "tier" + "2_events.csv")\n'),
 ("MB5b custom30_yield_labels duckdb/read_csv chuỗi f-string 'cctg_'", "custom30_yield_labels.py", '\n_P = f"data/cctg_{\'rate_vn\'}.csv"\n'),
 ("M30 effective_deposit_rate max với tier2", "deposit_rate_vn.py", READ + '''
_orig_eff = effective_deposit_rate
def effective_deposit_rate(asof=None, *a, **k):
    out = _orig_eff(asof, *a, **k)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    if m is not None and m > out["rate_pct"]:
        out = dict(out, rate_pct=m, rate=m / 100.0)
    return out
'''),
 ("M32 kill-switch A armed theo tier2", "deposit_rate_vn.py", READ + '''
_orig_ks = macro_killswitch_a_status
def macro_killswitch_a_status(asof=None, *a, **k):
    out = _orig_ks(asof, *a, **k)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    return dict(out, armed=True) if (m is not None and m > 7.5) else out
'''),
 ("M37 rating_8l.py nhắc tên file tier2 (tĩnh)", "rating_8l.py", '\n_T2 = "data/cctg_rate_vn_tier2_events.csv"\n'),
 ("M38 due_diligence import writer (tĩnh)", "trading_bot/due_diligence.py", "\nimport append_cctg_rate as _acr\n"),
]

def tree(old=False):
    d = tempfile.mkdtemp(prefix="cctg_t2mut2_")
    for n in os.listdir(SRC):
        p = os.path.join(SRC, n)
        if os.path.isfile(p) and n.endswith((".py", ".sh")):
            shutil.copy2(p, d)
    for sub in ("trading_bot", "deploy_golive_dt5g_v4"):
        shutil.copytree(os.path.join(SRC, sub), os.path.join(d, sub),
                        ignore=shutil.ignore_patterns("__pycache__", "*.csv", "*.pkl", "*.json", "*.log", "data"))
    if old:  # selfcheck + writer + wrapper của HEAD (vòng 1)
        for f in (SC, W, SH):
            out = subprocess.run(["git", "show", f"HEAD:WorkingClaude/{f}"], cwd=SRC, capture_output=True, check=True).stdout
            open(os.path.join(d, f), "wb").write(out)
    return d

def run(d, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "JOB_ID"}
    env.update(env_extra or {})
    r = subprocess.run([PY, SC], cwd=d, capture_output=True, text=True, env=env)
    fails = [l[5:70] for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    crash = (r.stderr.strip().splitlines() or [""])[-1][:90] if r.returncode and not fails else ""
    return r.returncode, fails, crash

def apply(d, f, rest):
    p = os.path.join(d, f)
    s = open(p, encoding="utf-8").read()
    if len(rest) == 2:
        assert s.count(rest[0]) == 1, f"{f}: chuỗi gốc xuất hiện {s.count(rest[0])} lần: {rest[0][:60]}"
        s = s.replace(rest[0], rest[1])
    else:
        s += rest[0]
    open(p, "w", encoding="utf-8").write(s)

if "--old-control" in sys.argv:
    name, f, *rest = [m for m in APPEND if m[0].startswith("MC'")][0]
    d = tree(old=True)
    rc0, fails0, crash0 = run(d)
    apply(d, f, rest)
    rc, fails, crash = run(d)
    shutil.rmtree(d)
    print(f"OLD-CONTROL (selfcheck+writer+wrapper của HEAD, vòng 1): baseline rc={rc0}; mutant MC' rc={rc} -> "
          f"{'SỐNG (đúng như reviewer báo)' if rc == 0 else 'BỊ BẮT ' + str(fails[:3])}")
    sys.exit(0)

d = tree(); rc, fails, crash = run(d); shutil.rmtree(d)
print(f"BASELINE rc={rc} fails={fails} {crash}")
assert rc == 0, "baseline phải xanh"
alive = []
ALL = TEXT + APPEND
ONLY = os.environ.get('ONLY')
if ONLY:
    ALL = [m for m in ALL if any(k in m[0] for k in ONLY.split('|'))]
for name, f, *rest in ALL:
    d = tree(); apply(d, f, rest)
    env = {"DEPOSIT_RATE_CCTG_OVERLAY": "0"} if name.startswith("MB1") else None
    rc, fails, crash = run(d, env)
    shutil.rmtree(d)
    if rc == 0:
        alive.append(name)
    print(f"{'SỐNG   ' if rc == 0 else 'BỊ BẮT '} {name} | {('; '.join(x[:30] for x in fails[:3]) or crash)}", flush=True)
print(f"\n{len(ALL) - len(alive)}/{len(ALL)} mutant bị bắt, {len(alive)} sống: {alive}")
