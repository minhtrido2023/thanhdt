#!/usr/bin/env python3
"""Mutation run cho cctg_tier2_series_selfcheck.py. Mỗi mutant: chép cây code sang thư mục tạm,
sửa đúng 1 chỗ, chạy selfcheck — rc!=0 = BỊ BẮT, rc==0 = SỐNG. Dùng: mutants.py <WorkingClaude dir>"""
import os, shutil, subprocess, sys, tempfile

SRC = os.path.abspath(sys.argv[1])
PY = "/home/trido/thanhdt/wc_venv/bin/python"
T2 = '"cctg_rate_vn_" + "tier" + "2_events.csv"'  # né token quét tĩnh -> chỉ kiểm tra ĐỘNG bắt được

W = "append_cctg_rate.py"
TEXT = [  # (tên, file, cũ, mới)
 ("M01 tier2 ghi vào file 12M", W, "csv_path = CSV_PATH_TIER2 if is_tier2 else", "csv_path = CSV_PATH if is_tier2 else"),
 ("M02 bỏ whitelist ngân hàng", W, "if bank not in TIER2_BANKS:", "if not bank:"),
 ("M03 khoá bỏ cả bank+denom (gộp mọi ngân hàng)", W,
  'rows = [r for r in rows if (r.get("bank"), r.get("denomination") or "") == (bank, denom)]', "rows = list(rows)"),
 ("M04 khoá bỏ denomination", W,
  'rows = [r for r in rows if (r.get("bank"), r.get("denomination") or "") == (bank, denom)]',
  'rows = [r for r in rows if r.get("bank") == bank]'),
 ("M05 tắt chặn lệch >=1pp cho tier2", W, "if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force:",
  "if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force and not is_tier2:"),
 ("M06 tier2 không so với dòng gần nhất (chỉ so dòng người ghi)", W,
  'current_rate = float(_allk[-1]["cctg_rate"]) if _allk else None', "current_rate = None"),
 ("M07 nới lệch 2 nguồn 0,1 -> 0,5pp", W, "CROSS_SOURCE_TOLERANCE_PP = 0.1 ", "CROSS_SOURCE_TOLERANCE_PP = 0.5 "),
 ("M08 sidecar tier2 dùng chung sidecar 12M", W,
  "sidecar_path = os.path.join(os.path.dirname(CSV_PATH_TIER2), _tier2_sidecar_name(bank, denom))",
  "sidecar_path = _last_auto_sources_path()"),
 ("M09 sidecar tier2 chung cho mọi khoá", W, '''return f"cctg_tier2_{bank}_{denom or 'na'}_last_auto_sources.json"''',
  'return "cctg_tier2_last_auto_sources.json"'),
 ("M10 agent (JOB_ID) được dùng manual_verify", W,
  'if is_dispatched_agent and args.source != "web_crosscheck_auto":', "if False:"),
 ("M11 --bank/--denom lọt vào chuỗi 12m/6m", W, "if not is_tier2 and tier2_given:", "if False:"),
 ("M12 bỏ bắt buộc --product", W, "if not product:", "if False:"),
 ("M13 bỏ kiểm --denom", W, "if denom and denom not in TIER2_DENOMS:", "if False:"),
 ("M14 tier2 bỏ chặn ngày không-mới-hơn", W, "    if eff <= last_date:", "    if eff <= last_date and not is_tier2:"),
 ("M15 chèn dòng mới lên đầu file", W, "    rows.append(new_row)", "    rows.insert(0, new_row)"),
 ("M16 --force xoá mọi khoá cùng ngày", W,
  '''if not (args.force and r["effective_date"] == args.effective
                        and (r.get("bank"), r.get("denomination") or "") == (bank, denom))]''',
  '''if not (args.force and r["effective_date"] == args.effective)]'''),
 ("M17 header tier2 thiếu holding_period", W, '"denomination", "holding_period", "cctg_rate",', '"denomination", "cctg_rate",'),
 ("M18 cho phép lợi suất 0", W, "RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0", "RATE_MIN_PCT, RATE_MAX_PCT = -1.0, 30.0"),
 ("M19 lượt tier2 rò global sang lượt 12m", W,
  "    csv_path = CSV_PATH_TIER2 if is_tier2 else (CSV_PATH_6M if is_6m else CSV_PATH)",
  "    csv_path = CSV_PATH_TIER2 if is_tier2 else (CSV_PATH_6M if is_6m else CSV_PATH)\n    globals()['CSV_PATH'] = csv_path"),
 ("M20 không ghi bank vào dòng", W, '"bank": bank, "product": product,', '"bank": "", "product": product,'),
 ("M21 wrapper bỏ luật KHÔNG điền 0", "refresh_deposit_cctg_weekly.sh", "KHÔNG điền 0, ", ""),
 ("M22 wrapper bỏ --bank khỏi lệnh mẫu", "refresh_deposit_cctg_weekly.sh", "--series tier2 --bank <VPB|MB|TCB|ACB> ", "--series tier2 "),
 ("M23 wrapper truyền tier2 cho trend check", "refresh_deposit_cctg_weekly.sh",
  '"$PY" deposit_cctg_trend_check.py >> "$LOG" 2>&1', '"$PY" deposit_cctg_trend_check.py --with-tier2 >> "$LOG" 2>&1'),
 ("M24 wrapper bỏ series cctg_tier2 khỏi event", "refresh_deposit_cctg_weekly.sh", " / cctg_tier2 —", " —"),
]
_READ = f'''
def _t2_max(_dir):
    import csv as _csv, os as _os
    _p = _os.path.join(_dir, {T2})
    if not _os.path.exists(_p):
        return None
    with open(_p, encoding="utf-8") as _f:
        _v = [float(_r["cctg_rate"]) for _r in _csv.DictReader(_f)]
    return max(_v) if _v else None
'''
APPEND = [  # (tên, file, đoạn nối vào cuối file)
 ("M30 effective_deposit_rate lấy max với tier2 (đường dẫn né quét tĩnh)", "deposit_rate_vn.py", _READ + '''
_orig_eff = effective_deposit_rate
def effective_deposit_rate(asof=None, *a, **k):
    out = _orig_eff(asof, *a, **k)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    if m is not None and m > out["rate_pct"]:
        out = dict(out, rate_pct=m, rate=m / 100.0)
    return out
'''),
 ("M31 effective_deposit_rate chỉ DÒ file tier2, không đổi kết quả", "deposit_rate_vn.py", f'''
_orig_eff = effective_deposit_rate
def effective_deposit_rate(asof=None, *a, **k):
    os.path.exists(os.path.join(os.path.dirname(_EVENTS_CSV), {T2}))
    return _orig_eff(asof, *a, **k)
'''),
 ("M32 kill-switch A armed theo tier2", "deposit_rate_vn.py", _READ + '''
_orig_ks = macro_killswitch_a_status
def macro_killswitch_a_status(asof=None, *a, **k):
    out = _orig_ks(asof, *a, **k)
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    return dict(out, armed=True) if (m is not None and m > 7.5) else out
'''),
 ("M33 consumer_deposit_rate cộng tier2", "deposit_rate_vn.py", _READ + '''
_orig_cdr = consumer_deposit_rate
def consumer_deposit_rate(asof=None):
    m = _t2_max(os.path.dirname(_EVENTS_CSV))
    return max(_orig_cdr(asof), m or 0.0)
'''),
 ("M34 trend check nạp thêm chuỗi tier2", "deposit_cctg_trend_check.py", _READ + '''
_orig_ls = _load_series
def _load_series():
    import cctg_rate_vn as _c
    out = _orig_ls()
    m = _t2_max(os.path.dirname(_c._EVENTS_CSV))
    if m is not None:
        out["cctg_6m"] = out["cctg_6m"] + [("2026-10-13", m)]
    return out
'''),
 ("M35 cctg_events_df glob mọi file cctg_rate_vn_*_events.csv", "cctg_rate_vn.py", '''
_orig_ev = cctg_events_df
def cctg_events_df():
    import glob as _g
    ev = _orig_ev()
    for _p in _g.glob(os.path.join(os.path.dirname(_EVENTS_CSV), "cctg_rate_vn_" + "?*_events.csv")):
        _x = pd.read_csv(_p)
        ev = pd.concat([ev, pd.DataFrame({"time": pd.to_datetime(_x["effective_date"]) + pd.Timedelta(days=1),
                                          "cctg_rate": _x["cctg_rate"].astype(float)})], ignore_index=True)
    return ev.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
'''),
 ("M36 dcf discount_rate lấy max với tier2", "dcf_valuation.py", _READ + '''
_orig_dr = discount_rate
def discount_rate(asof, erp=ERP):
    m = _t2_max(os.path.dirname(_dep._EVENTS_CSV))
    return max(_orig_dr(asof, erp), ((m or 0.0) + erp) / 100.0)
'''),
 ("M37 rating_8l.py nhắc đường dẫn file tier2 (tĩnh)", "rating_8l.py", '\n_T2 = "data/cctg_rate_vn_tier2_events.csv"\n'),
 ("M38 due_diligence import writer append_cctg_rate (tĩnh)", "trading_bot/due_diligence.py", "\nimport append_cctg_rate as _acr\n"),
 ("M39 golive_recommend_v23 dùng CSV_PATH_TIER2 (tĩnh)", "deploy_golive_dt5g_v4/golive_recommend_v23.py",
  "\n_T2P = 'CSV_PATH_TIER2'\n"),
 ("M41 [KHOẢNG HỞ ĐÃ BIẾT] rating_8l.py đọc tier2 bằng đường dẫn né quét tĩnh", "rating_8l.py",
  '\n_T2X = os.path.join("data", "cctg_rate_vn_" + "tier" + "2_events.csv")\n'),
 ("M40 custom30_yield_labels glob cctg_rate_vn* (tĩnh)", "custom30_yield_labels.py", '\n_G = "data/cctg_rate_vn*.csv"\n'),
]

def tree():
    d = tempfile.mkdtemp(prefix="cctg_t2mut_")
    for n in os.listdir(SRC):
        p = os.path.join(SRC, n)
        if os.path.isfile(p) and n.endswith((".py", ".sh")):
            shutil.copy2(p, d)
    for sub in ("trading_bot", "deploy_golive_dt5g_v4"):
        shutil.copytree(os.path.join(SRC, sub), os.path.join(d, sub),
                        ignore=shutil.ignore_patterns("__pycache__", "*.csv", "*.pkl", "*.json", "*.log", "data"))
    return d

def run(d):
    r = subprocess.run([PY, "cctg_tier2_series_selfcheck.py"], cwd=d, capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if k != "JOB_ID"})
    fails = [l[5:70] for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    crash = (r.stderr.strip().splitlines() or [""])[-1][:90] if r.returncode and not fails else ""
    return r.returncode, fails, crash

d = tree(); rc, fails, crash = run(d); shutil.rmtree(d)
print(f"BASELINE (không mutant) rc={rc} fails={fails} {crash}")
assert rc == 0, "baseline phải xanh"
alive = 0
for name, f, *rest in TEXT + APPEND:
    d = tree()
    p = os.path.join(d, f)
    s = open(p, encoding="utf-8").read()
    if len(rest) == 2:
        assert s.count(rest[0]) == 1, f"{name}: chuỗi gốc xuất hiện {s.count(rest[0])} lần"
        s = s.replace(rest[0], rest[1])
    else:
        s += rest[0]
    open(p, "w", encoding="utf-8").write(s)
    rc, fails, crash = run(d)
    shutil.rmtree(d)
    alive += rc == 0
    print(f"{'SỐNG   ' if rc == 0 else 'BỊ BẮT '} {name} | {('; '.join(f[:28] for f in fails[:4]) or crash)}")
print(f"\n{len(TEXT + APPEND) - alive}/{len(TEXT + APPEND)} mutant bị bắt, {alive} sống")
