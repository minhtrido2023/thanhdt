#!/usr/bin/env python3
"""Mutation test cho bin/measured_by_warn_report.py + khối đếm trong bin/daily_retro.sh (vòng bổ sung 13/10).
Mỗi mutant = 1 phép thay chuỗi (phải khớp ĐÚNG 1 lần) trên bản copy; chạy selfcheck tương ứng của bản copy.
CHẾT = selfcheck rc≠0 VÀ có ≥1 dòng FAIL (harness nổ không tính). Đối chứng phải rc=0 trước.
    TZ=Pacific/Kiritimati python3 agents/Wags/research/measured_by_20261013/mutants_warn_report.py"""
import os, shutil, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
H, R = "measured_by_warn_report.py", "daily_retro.sh"
FILES = [H, "measured_by_warn_report_selfcheck.py", R, "daily_retro_measured_by_selfcheck.sh", "usage_limit_phrases.sh"]
# (tên, file, cũ, mới, selfcheck)
HS, RS = "measured_by_warn_report_selfcheck.py", "daily_retro_measured_by_selfcheck.sh"
M = [
 ("W1 cửa sổ 24h thành 25h", H, "H24, H48, D7 = dt.timedelta(hours=24)", "H24, H48, D7 = dt.timedelta(hours=25)", HS),
 ("W2 cửa sổ 24h thành 23h", H, "H24, H48, D7 = dt.timedelta(hours=24)", "H24, H48, D7 = dt.timedelta(hours=23)", HS),
 ("W3 cửa sổ 7 ngày thành 6 ngày", H, "dt.timedelta(days=7)", "dt.timedelta(days=6)", HS),
 ("W4 biên 24h mở (tuổi < 24h)", H, "return lo < (now - t) <= hi if lo is not None else (now - t) <= hi", "return lo < (now - t) <= hi if lo is not None else (now - t) < hi", HS),
 ("W5 ts tương lai được đếm", H, "if t is None or t > now:", "if t is None:", HS),
 ("W6 nhầm nhóm trace_id (đảo)", H, 'has_trace = lambda r: bool(str(r.get("trace_id") or "").strip())', 'has_trace = lambda r: not bool(str(r.get("trace_id") or "").strip())', HS),
 ("W7 trace_id chỉ khoảng trắng tính là có trace", H, 'bool(str(r.get("trace_id") or "").strip())', 'bool(str(r.get("trace_id") or ""))', HS),
 ("W8 trace_id None thành chuỗi 'None' (có trace)", H, 'str(r.get("trace_id") or "")', 'str(r.get("trace_id"))', HS),
 ("W9 dòng hỏng làm nổ (bỏ except ValueError)", H, "                except (ValueError, RecursionError):", "                except KeyError:", HS),
 ("W9b dòng lồng sâu làm nổ (bỏ RecursionError)", H, "                except (ValueError, RecursionError):", "                except ValueError:", HS),
 ("W10 bỏ fail-open ở main (ngoại lệ lọt ra, rc≠0)", H, "    except BaseException:  # noqa: BLE001 — fail-open tuyệt đối: retro không được đổ vì khối thông tin này", "    except ZeroDivisionError:", HS),
 ("W11 exit code 1 khi không dữ liệu", H, "    sys.exit(0)", "    sys.exit(1)", HS),
 ("W12 top agent 8 → 3", H, 'top(agents, 8)', 'top(agents, 3)', HS),
 ("W13 top topic 5 → 9", H, 'top(topics, 5)', 'top(topics, 9)', HS),
 ("W14 mẫu số tính mọi event_type", H, 'if e.get("event_type") != "finding":\n                continue', 'if False:\n                continue', HS),
 ("W15 giờ in theo giờ local, không ICT", H, "now.astimezone(ICT).strftime", "now.astimezone().strftime", HS),
 ("W16 chia 0 không bảo vệ", H, 'return "%.1f%%" % (100.0 * a / b) if b else "n/a"', 'return "%.1f%%" % (100.0 * a / b)', HS),
 ("W17 ghi file (không đọc-only)", H, "    return \"\\n\".join(lines)", "    open(os.path.join(bus, '_x'), 'w').write('x')\n    return \"\\n\".join(lines)", HS),
 ("W18 không cắt topic nhiều dòng", H, 'return " ".join(str(s).split())[:n]', 'return str(s)', HS),
 ("W19 24h-trước dùng cùng cửa sổ 24h", H, "wcount(None, H24), wcount(H24, H48), wcount(None, D7)", "wcount(None, H24), wcount(None, H24), wcount(None, D7)", HS),
 ("D1 [TƯƠNG ĐƯƠNG: retro không có set -e] bỏ || true", R, '2>/dev/null || true)"\n[ -n "$_mb_warn_block" ]', '2>/dev/null)"\n[ -n "$_mb_warn_block" ]', RS),
 ("D6 timeout mặc định 20 -> 0 (không giới hạn)", R, '${DAILY_RETRO_MB_TIMEOUT:-20}', '${DAILY_RETRO_MB_TIMEOUT:-0}', RS),
 ("W18 ts có offset coi như UTC", H, "return t.replace(tzinfo=dt.timezone.utc) if t.tzinfo is None else t.astimezone(dt.timezone.utc)", "return t.replace(tzinfo=dt.timezone.utc)", HS),
 ("W19 ts naive coi như giờ local", H, "return t.replace(tzinfo=dt.timezone.utc) if t.tzinfo is None else t.astimezone(dt.timezone.utc)", "return t.astimezone(dt.timezone.utc)", HS),
 ("W20 lỗi helper in y câu 'không đọc được)' (không phân biệt)", H, 'NO_DATA.replace("không đọc được)", "không đọc được; hoặc helper lỗi)", 1)', 'NO_DATA', HS),
 ("D2 bỏ timeout của helper", R, 'timeout "${DAILY_RETRO_MB_TIMEOUT:-20}" python3', 'python3', RS),
 ("D3 bỏ câu KHÔNG escalate", R, "KHÔNG escalate, KHÔNG tạo question từ nó", "xin cân nhắc", RS),
 ("D4 mục 2f rỗng khi helper không ra gì (bỏ fallback)", R, '[ -n "$_mb_warn_block" ] || _mb_warn_block=', ': || _mb_warn_block=', RS),
 ("D5 helper chạy làm đổi prompt Wags", R, "Trả lời rõ ràng ngay đầu câu trả lời: 'CONFIRMED'", "Trả lời rõ ràng ngay đầu câu trả lời ($_mb_warn_block): 'CONFIRMED'", RS),
]
only = sys.argv[1:]
killed, alive = [], []
def sc(d, which):
    cmd = [sys.executable, d + "/bin/" + which] if which.endswith(".py") else ["bash", d + "/bin/" + which]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=200, start_new_session=True,
                          env={k: v for k, v in os.environ.items() if k != "BASELINE_RETRO"})
for name, fn, old, new, which in [("ĐỐI-CHỨNG", H, "", "", None)] + M:
    if only and name.split()[0] not in only and name != "ĐỐI-CHỨNG":
        continue
    d = tempfile.mkdtemp(prefix="mbwr_mut_"); os.makedirs(d + "/bin")
    try:
        for f in FILES:
            shutil.copy2(os.path.join(ROOT, "bin", f), d + "/bin/" + f)
        if which is None:
            for w in (HS, RS):
                r = sc(d, w); print("ĐỐI CHỨNG %s rc=%d" % (w, r.returncode))
                if r.returncode != 0: print(r.stdout[-500:]); sys.exit("đối chứng đỏ, dừng")
            continue
        p = d + "/bin/" + fn; s = open(p, encoding="utf-8").read()
        if s.count(old) != 1:
            print("KHÔNG ÁP ĐƯỢC (%d): %s" % (s.count(old), name)); alive.append(name + " [không áp được]"); continue
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        try:
            r = sc(d, which)
        except subprocess.TimeoutExpired:
            killed.append(name); print("CHẾT  %-55s treo >200s" % name); continue
        fails = [l.strip()[:100] for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL") or l.startswith("  FAIL")]
        if r.returncode != 0 and not fails: alive.append(name + " [harness nổ]"); print("NỔ    %s :: %s" % (name, r.stderr.strip()[-150:]))
        elif r.returncode != 0: killed.append(name); print("CHẾT  %-55s fail=%d vd: %s" % (name, len(fails), fails[0]))
        else: alive.append(name); print("SỐNG  %s" % name)
    finally:
        shutil.rmtree(d, ignore_errors=True)
print("\nTỔNG: %d mutant · CHẾT %d · SỐNG %d" % (len(killed) + len(alive), len(killed), len(alive)))
for a in alive: print("  còn sống:", a)
