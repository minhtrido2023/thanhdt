# -*- coding: utf-8 -*-
"""Mutation test cho refresh_earnings_surprise_pkl.py. Dùng: $DNA_PYEXE mutants_refresh_pkl.py <WC worktree>"""
import os, shutil, subprocess, sys, tempfile
WT = os.path.abspath(sys.argv[1]); SRC = os.path.join(WT, "refresh_earnings_surprise_pkl.py"); SC = os.path.join(WT, "refresh_earnings_surprise_pkl_selfcheck.py")
M = [
 ("R01 ghi thẳng vào pkl đích (không nguyên tử)", '    tmp = f"{path}.tmp.{os.getpid()}"\n', '    tmp = path\n'),
 ("R02 bỏ fsync", "        os.fsync(f.fileno())\n", ""),
 ("R03 bỏ chốt co lại", "        if len(fin) < len(old) * (1 - MAX_SHRINK):", "        if False:"),
 ("R04 ngưỡng co 2% → 20%", "MAX_SHRINK = 0.02", "MAX_SHRINK = 0.20"),
 ("R05 ngưỡng co 2% → 1%", "MAX_SHRINK = 0.02", "MAX_SHRINK = 0.01"),
 ("R06 bỏ chốt max Release_Date lùi", "        if pd.notna(old_max) and new_max < old_max:", "        if False:"),
 ("R07 0 dòng vẫn nhận", "    if not len(fin):\n        return \"0 dòng\"\n", ""),
 ("R08 thiếu cột vẫn nhận", "    if missing:\n", "    if False:\n"),
 ("R09 không gỡ BQ_LOCAL_CACHE", '    os.environ.pop("BQ_LOCAL_CACHE", None)\n', ""),
 ("R10 không gỡ LOCAL_SNAPSHOT_DIR", '    os.environ.pop("LOCAL_SNAPSHOT_DIR", None)\n', ""),
 ("R11 SQL lệch (bỏ lọc NP_P0)", " AND f.NP_P0 IS NOT NULL\"\"\"", "\"\"\""),
 ("R12 SQL lệch (mốc 2010)", "f.Release_Date >= '2009-01-01'", "f.Release_Date >= '2010-01-01'"),
 ("R13 luôn ghi dù không đổi", "    if old is not None and _same(old, fin):\n        return \"unchanged\", info\n", ""),
 ("R14 kept_old trả exit 0", '    return 1 if res == "kept_old" else 0', "    return 0"),
 ("R15 BQ raise lan ra ngoài", "    except Exception as ex:\n        reason = f\"{type(ex).__name__}: {ex}\"\n", "    except ZeroDivisionError as ex:\n        reason = f\"{type(ex).__name__}: {ex}\"\n"),
 ("R16 không dọn file tạm mồ côi", '    for stale in glob.glob(f"{path}.tmp.*"):', '    for stale in []:'),
 ("R17 không chuẩn hoá datetime ns", '            fin[c] = fin[c].astype("datetime64[ns]")', "            pass"),
 ("R18 pkl cũ hỏng → từ chối bản mới", '            old, old_err = None, f"{type(ex).__name__}: {ex}"\n', '            return "kept_old", {"reason": "pkl cũ hỏng"}\n'),
 ("R19 lỗi ghi lan ra ngoài (không kept_old)", "    try:\n        write_atomic(fin, path)\n    except Exception as ex:", "    try:\n        write_atomic(fin, path)\n    except ZeroDivisionError as ex:"),
 ("R20 lý do từ chối bị nuốt", '        info["reason"] = reason\n', '        info["reason"] = ""\n'),
 ("R21 không kiểm DataFrame", "    if not isinstance(fin, pd.DataFrame):", "    if False:"),
 ("R22 bỏ đọc lại file tạm", "    if len(back) != len(fin):", "    if False:"),
 ("R23 không nạp được accessor → exit 0", "              f\"Lỗi thật: {type(ex).__name__}: {ex}\")\n        return 1", "              f\"Lỗi thật: {type(ex).__name__}: {ex}\")\n        return 0"),
 ("R24 StringDtype không đổi object", "            fin[c] = fin[c].astype(object)", "            pass"),
 ("R25 Release_Date toàn NaT vẫn nhận", "    if pd.isna(new_max):\n        return \"Release_Date toàn NaT\"\n", ""),
 ("R26 cột bị xáo thứ tự", "fin = normalize(fin)[COLUMNS + [c for c in fin.columns if c not in COLUMNS]]", "fin = normalize(fin)[list(reversed(COLUMNS))]"),
]
ONLY = sys.argv[2].split(',') if len(sys.argv) > 2 else None
k = s_ = na = 0; surv = []
for name, old, new in M:
    if ONLY and name.split(' ')[0] not in ONLY: continue
    tmp = tempfile.mkdtemp(prefix="respmut_"); p = os.path.join(tmp, "refresh_earnings_surprise_pkl.py")
    try:
        src = open(SRC, encoding="utf-8").read()
        if src.count(old) != 1:
            na += 1; print(f"NOT-APPLIED ({src.count(old)} khớp)  {name}"); continue
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
        r = subprocess.run([sys.executable, SC], capture_output=True, text=True, env=dict(os.environ, RESP_TARGET=p), timeout=180)
        fails = [l.strip()[:100] for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        if r.returncode != 0:
            k += 1; print(f"KILLED   {name}  ← {len(fails)} FAIL" + (f" (vd: {fails[0]})" if fails else " (crash)"))
        else:
            s_ += 1; surv.append(name); print(f"SURVIVED {name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
print(f"\nTỔNG: {k} killed / {s_} survived / {na} not-applied")
for x in surv: print("  SỐNG:", x)
