#!/usr/bin/env python3
"""Mutation test cho cổng measured_by. Mỗi mutant = 1 phép thay chuỗi (phải khớp ĐÚNG 1 lần)
trên bản copy của bin/, rồi chạy bin/append_event_selfcheck.py của bản copy đó.
CHẾT = selfcheck rc≠0 VÀ có ≥1 dòng assertion FAIL (harness nổ không tính là chết).
Lượt ĐỐI CHỨNG (không mutant) phải rc=0 trước, nếu không thì dừng. Chạy dưới TZ lệch xa UTC để mutant gmtime→localtime lộ ra.
    TZ=Pacific/Kiritimati python3 agents/Wags/research/measured_by_20261013/mutants.py
"""
import os, shutil, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
FILES = ["append_event.sh", "append_event_selfcheck.py", "mike_json.py", "json_payload_diag.py",
         "finding_measured_by.py", "verify_finding.sh", "wags_autofix.sh"]
SH, PY = "append_event.sh", "finding_measured_by.py"
M = [
 ("S1 cổng chạy cho MỌI event_type", SH, 'case "$etype" in finding)\n  if [ "${AE_MEASURED', 'case "$etype" in *)\n  if [ "${AE_MEASURED'),
 ("S2 bỏ `|| true` sau helper", SH, '"$BUS/_measured_by_warn.jsonl" 9>&- \\\n      || true\n', '"$BUS/_measured_by_warn.jsonl" 9>&-\n'),
 ("S3 bỏ timeout", SH, "| timeout 2 python3", "| python3"),
 ("S4 đảo công tắc tắt khẩn", SH, '"${AE_MEASURED_BY_CHECK:-1}" != 0', '"${AE_MEASURED_BY_CHECK:-1}" = 0'),
 ("S5 file cảnh báo nằm TRONG inbox", SH, '"$BUS/_measured_by_warn.jsonl" 9>&- \\', '"$BUS/inbox/_measured_by_warn.jsonl" 9>&- \\'),
 ("S6 không nhả flock", SH, "    flock -u 9 2>/dev/null || true\n", ""),
 ("S7 đưa payload thay vì dòng event cho helper", SH, '''    printf '%s\\n' "$line" \\\n      | timeout''', '''    printf '%s\\n' "$payload" \\\n      | timeout'''),
 ("S8 không truyền đường dẫn file cảnh báo", SH, ' "$BUS/_measured_by_warn.jsonl" 9>&- \\', ' 9>&- \\'),
 ("S9 kiểm TRƯỚC khi ghi + chặn khi cảnh báo (exit 1 nếu helper có in)", SH,
  'mkdir -p "$BUS/inbox"\nexec 9>>', 'case "$etype" in finding) python3 "$ROOT/bin/finding_measured_by.py" </dev/null ;; esac\nmkdir -p "$BUS/inbox"\nexec 9>>'),
 ("S10 đổi stdout dòng appended", SH, 'echo "appended $etype/$topic for $id"', 'echo "appended $etype/$topic for $id (checked)"'),
 ("P1 đảo điều kiện event_type", PY, 'event.get("event_type") != "finding"', 'event.get("event_type") == "finding"'),
 ("P2 bool tính là số", PY, "        if isinstance(v, bool):\n            continue\n", ""),
 ("P3 measured_by toàn khoảng trắng được chấp nhận", PY, "return bool(mb.strip())", "return bool(mb)"),
 ("P4 measured_by list/dict rỗng được chấp nhận", PY, "    if isinstance(mb, (list, dict)):\n        return bool(mb)", "    if isinstance(mb, (list, dict)):\n        return True"),
 ("P5 measured_by kiểu khác được chấp nhận", PY, "        return bool(mb)\n    return False", "        return bool(mb)\n    return mb is not None"),
 ("P6 bỏ qua measured_by (luôn cảnh báo)", PY, "not isinstance(payload, dict) or has_measured_by(payload)", "not isinstance(payload, dict)"),
 ("P7 payload không phải dict vẫn xét", PY, "    if not isinstance(payload, dict) or has_measured_by(payload):\n        return None", "    if isinstance(payload, dict) and has_measured_by(payload):\n        return None"),
 ("P8 bỏ luật ngày d/m", PY, 'r"\\b(?:0?[1-9]|[12]\\d|3[01])/(?:0?[1-9]|1[0-2])(?:/\\d{2,4})?\\b"', 'r"\\bZZZ\\b"'),
 ("P9 bỏ luật giờ", PY, 'r"|\\b\\d{1,2}:\\d{2}(?::\\d{2})?\\b"', 'r"|\\bZZZ\\b"'),
 ("P10 bỏ luật đường dẫn", PY, '("/" in word and _HAS_ALPHA_RE.search(word)) or _FILE_RE.search(word)', "_FILE_RE.search(word)"),
 ("P11 bỏ luật tên file", PY, '("/" in word and _HAS_ALPHA_RE.search(word)) or _FILE_RE.search(word)', '("/" in word and _HAS_ALPHA_RE.search(word))'),
 ("P12 mọi từ có `/` đều bỏ (mất +480/-611)", PY, '("/" in word and _HAS_ALPHA_RE.search(word))', '("/" in word)'),
 ("P13 lookbehind bỏ `.`", PY, "(?<![\\w.,:#§-])", "(?<![\\w,:#§-])"),
 ("P14 lookbehind bỏ `,`", PY, "(?<![\\w.,:#§-])", "(?<![\\w.:#§-])"),
 ("P15 lookbehind bỏ `:`", PY, "(?<![\\w.,:#§-])", "(?<![\\w.,#§-])"),
 ("P16 lookbehind bỏ `#`", PY, "(?<![\\w.,:#§-])", "(?<![\\w.,:§-])"),
 ("P17 lookbehind bỏ `§`", PY, "(?<![\\w.,:#§-])", "(?<![\\w.,:#-])"),
 ("P18 lookbehind bỏ `-`", PY, "(?<![\\w.,:#§-])", "(?<![\\w.,:#§])"),
 ("P19 lookbehind bỏ `\\w`", PY, "(?<![\\w.,:#§-])", "(?<![.,:#§-])"),
 ("P20 lookahead bỏ `-\\d`", PY, "(?!\\w|-\\d|[.,]\\d)", "(?!\\w|[.,]\\d)"),
 ("P21 lookahead bỏ `\\w`", PY, "(?!\\w|-\\d|[.,]\\d)", "(?!-\\d|[.,]\\d)"),
 ("P22 số JSON không tính", PY, "        if isinstance(v, (int, float)):\n            found.append(repr(v))\n        elif", "        if isinstance(v, (int, float)):\n            pass\n        elif"),
 ("P23 chuỗi không quét", PY, "        elif isinstance(v, str):", "        elif False:"),
 ("P24 không đệ quy vào dict lồng", PY, "        for v in x.values():\n            yield from _values(v)", "        for v in x.values():\n            yield v"),
 ("P25 không đệ quy vào list", PY, "        for v in x:\n            yield from _values(v)", "        for v in x:\n            yield v"),
 ("P26 đảo điều kiện có-mẫu trong main", PY, "    if not samples:\n        return", "    if samples:\n        return"),
 ("P27 bỏ finally (file lỗi ⇒ mất luôn stderr)", PY, "    finally:\n        sys.stderr.write(", "    if True:\n        sys.stderr.write("),
 ("P28 ts dùng giờ địa phương", PY, "time.gmtime()", "time.localtime()"),
 ("P29 helper exit 1", PY, "        pass\n    os._exit(0)", "        pass\n    os._exit(1)"),
 ("P30 helper để lọt exception", PY, "    except BaseException:  # noqa: BLE001 — fail-open tuyệt đối, kể cả SystemExit/KeyboardInterrupt\n        pass", "    except KeyError:\n        pass"),
 ("P31 ensure_ascii=False", PY, "json.dumps(rec, ensure_ascii=True)", "json.dumps(rec, ensure_ascii=False)"),
 ("P32 không cắt topic", PY, 'str(event.get("topic", ""))[:200]', 'str(event.get("topic", ""))'),
 ("P33 giới hạn mẫu 5→50", PY, "_MAX_SAMPLES = 5", "_MAX_SAMPLES = 50"),
 ("P34 bỏ event_id khỏi bản ghi", PY, '"event_id": event.get("event_id"), ', ""),
 ("P35 bỏ trace_id khỏi bản ghi", PY, '"trace_id": event.get("trace_id"),', '"trace_id": None,'),
 ("P36 measured_by nhận ở mọi cấp (tìm trong chuỗi JSON)", PY, '    mb = payload.get("measured_by")', '    mb = payload.get("measured_by") or ("x" if "measured_by" in json.dumps(payload) else None)'),
 ("P37 file cảnh báo ghi đè thay vì nối", PY, 'open(argv[1], "a", encoding="ascii")', 'open(argv[1], "w", encoding="ascii")'),
 ("P38 stderr bỏ chữ KHÔNG chặn", PY, "[CẢNH BÁO — KHÔNG chặn, event ĐÃ ghi, ĐỪNG gửi lại]", "[CẢNH BÁO]"),
]

# ── Vòng 2: mutant do arch-reviewer nghĩ thêm (1844cac8e) + mutant cho phần sửa vòng 2 ──
GATE_START = "\n# --- Cổng `measured_by` cho finding"
def _relocate(before_marker):
    """Dời NGUYÊN khối cổng (từ comment tới `;; esac` cuối file) lên ngay trước `before_marker`."""
    def f(s):
        i = s.index(GATE_START); gate = s[i + 1:]; body = s[:i + 1]
        assert body.count(before_marker) == 1
        return body.replace(before_marker, gate + before_marker)
    return f
CASE_OLD = 'case "$etype" in finding)\n  if [ "${AE_MEASURED'
M += [
 ("A1 cổng chạy TRƯỚC dòng appended (sau ghi bus)", SH, _relocate('echo "appended $etype/$topic for $id"\n'), None),
 ("A2 cổng chạy TRƯỚC khi ghi bus", SH, _relocate("printf '%s\\n' \"$line\" >&9\n"), None),
 ("A3 case finding*)", SH, CASE_OLD, CASE_OLD.replace("finding)", "finding*)")),
 ("A4 case không phân biệt hoa/thường", SH, CASE_OLD, CASE_OLD.replace("finding)", "[Ff][Ii][Nn][Dd][Ii][Nn][Gg])")),
 ("A10 cổng chạy cả cho verification", SH, CASE_OLD, CASE_OLD.replace("finding)", "finding|verification|VERIFY)")),
 ("A5 công tắc: chỉ =1 mới bật", SH, '"${AE_MEASURED_BY_CHECK:-1}" != 0', '"${AE_MEASURED_BY_CHECK:-1}" = 1'),
 ("A7 helper chạy NỀN (mồ côi)", SH, ' 9>&- \\\n      || true\n', ' 9>&- \\\n      || true &\n'),
 ("A11 helper thừa hưởng fd 9", SH, '"$BUS/_measured_by_warn.jsonl" 9>&- \\', '"$BUS/_measured_by_warn.jsonl" \\'),
 ("A12 bỏ chốt [ -f helper ]", SH, ' && [ -r "$ROOT/bin/finding_measured_by.py" ]; then', '; then'),
 ("A13 timeout 2 → 30", SH, "| timeout 2 python3", "| timeout 30 python3"),
 ("B1 lookahead bỏ [.,]\\d", PY, "(?!\\w|-\\d|[.,]\\d)", "(?!\\w|-\\d)"),
 ("B2 bỏ dấu [+-]?", PY, "[\\w.,:#§-])[+-]?\\d+", "[\\w.,:#§-])\\d+"),
 ("B3 bỏ %?", PY, "(?:[.,]\\d+)*%?(?!", "(?:[.,]\\d+)*(?!"),
 ("B4 bỏ phần thập phân", PY, "\\d+(?:[.,]\\d+)*%?", "\\d+%?"),
 ("B5 quét cả tên khoá", PY, "        for v in x.values():\n            yield from _values(v)", "        for k, v in x.items():\n            yield k\n            yield from _values(v)"),
 ("B6 quét cả topic", PY, "    return number_tokens(payload) or None", "    return number_tokens([payload, event.get('topic', '')]) or None"),
 ("B7 tháng không chặn ≤12", PY, "(?:0?[1-9]|1[0-2])(?:/", "(?:\\d{1,2})(?:/"),
 ("B8 ngày không chặn ≤31", PY, 'r"\\b(?:0?[1-9]|[12]\\d|3[01])/', 'r"\\b(?:\\d{1,2})/'),
 ("B10 _HAS_ALPHA chỉ chữ thường", PY, 're.compile(r"[A-Za-z]")', 're.compile(r"[a-z]")'),
 ("B11 _FILE_RE bỏ \\b cuối", PY, "yaml|yml|toml)\\b", "yaml|yml|toml)"),
 ("B12 _FILE_RE chỉ còn py|json|md", PY, "(?:py|sh|json|jsonl|md|csv|txt|log|html|sql|yaml|yml|toml)", "(?:py|json|md)"),
 ("B13 except BaseException → Exception (quanh main)", PY, "    except BaseException:  # noqa: BLE001 — fail-open tuyệt đối", "    except Exception:  # noqa: BLE001 — fail-open tuyệt đối"),
 ("B15 đổi giá trị trường warn", PY, '"warn": "finding_missing_measured_by"', '"warn": "x"'),
 ("B16 agent_id không cắt 80", PY, 'str(event.get("agent_id", ""))[:80]', 'str(event.get("agent_id", ""))'),
 ("B17a mẫu trong file không cắt 24", PY, '"sample_numbers": [s[:24] for s in samples]', '"sample_numbers": list(samples)'),
 ("B17b mẫu trên stderr không cắt 24", PY, 'shown = ", ".join(s[:24] for s in samples)', 'shown = ", ".join(samples)'),
 ("B18a stderr bỏ 'ĐỪNG gửi lại'", PY, "event ĐÃ ghi, ĐỪNG gửi lại]", "event ĐÃ ghi]"),
 ("B18b stderr bỏ 'Lần sau'", PY, "CẤP CAO NHẤT. Lần sau khai", "CẤP CAO NHẤT. Khai"),
 ("B18c stderr bỏ 'CẤP CAO NHẤT'", PY, ' ở CẤP CAO NHẤT. Lần sau', '. Lần sau'),
 ("B20 nhận khoá có khoảng trắng thừa", PY, '    mb = payload.get("measured_by")', '    mb = payload.get("measured_by") or payload.get("measured_by ") or payload.get(" measured_by")'),
 ("B21 nhận khoá measuredBy/measured-by", PY, '    mb = payload.get("measured_by")', '    mb = payload.get("measured_by") or payload.get("measuredBy") or payload.get("measured-by")'),
 ("B28 list/dict toàn giá trị rỗng bị từ chối", PY, "        return bool(mb)\n    return False", "        return any(mb.values()) if isinstance(mb, dict) else any(mb)\n    return False"),
 ("C1 bỏ bước gỡ hậu tố đơn vị", PY, '                word = _UNIT_SUFFIX_RE.sub("", word)\n', ""),
 ("C2 hậu tố đơn vị nhận cả chữ số", PY, 're.compile(r"/[^\\W\\d_]+[.,;:!?)\\]]*$")', 're.compile(r"/\\w+$")'),
 ("C3 stdin đọc theo locale", PY, 'json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))', "json.loads(sys.stdin.read())"),
 ("C4 topic không ép 1 dòng trên stderr", PY, '% (" ".join(topic.split()), shown))', "% (topic, shown))"),
 ("C5 kết thúc bằng sys.exit(0) thay os._exit(0)", PY, "        pass\n    os._exit(0)", "        pass\n    sys.exit(0)"),
 ("R3-1 hậu tố đơn vị không nhận dấu câu theo sau (vòng bổ sung 13/10)", PY, '[.,;:!?)\\]]*$"', '$"'),
 ("R3-2 [ -r ] đổi lại thành [ -f ] (vòng bổ sung 13/10)", SH, '[ -r "$ROOT/bin/finding_measured_by.py" ]', '[ -f "$ROOT/bin/finding_measured_by.py" ]'),
]
only = sys.argv[1:]
killed, alive = [], []
for name, fn, old, new in [("ĐỐI-CHỨNG không mutant", SH, "", "")] + M:
    if only and name.split()[0] not in only and not name.startswith("ĐỐI-CHỨNG"):
        continue
    d = tempfile.mkdtemp(prefix="ae_mut_"); os.makedirs(d + "/bin"); os.makedirs(d + "/kb")
    try:
        for f in FILES:
            shutil.copy2(os.path.join(ROOT, "bin", f), d + "/bin/" + f)
        open(d + "/kb/version.txt", "w").write("1\n")
        p = d + "/bin/" + fn
        s = open(p, encoding="utf-8").read()
        if name.startswith("ĐỐI-CHỨNG"):
            r = subprocess.run([sys.executable, d + "/bin/append_event_selfcheck.py"], capture_output=True, text=True, timeout=600)
            print("ĐỐI CHỨNG rc=%d PASS=%d FAIL=%d" % (r.returncode, r.stdout.count("\n  PASS"), r.stdout.count("\n  FAIL")))
            if r.returncode != 0:
                print(r.stdout[-600:], r.stderr[-600:]); sys.exit("đối chứng đỏ ⇒ mọi kết quả mutant vô nghĩa, dừng")
            continue
        if callable(old):
            open(p, "w", encoding="utf-8").write(old(s))
        elif s.count(old) != 1:
            print("KHÔNG ÁP ĐƯỢC (%d lần khớp): %s" % (s.count(old), name)); alive.append(name + " [không áp được]"); continue
        else:
            open(p, "w", encoding="utf-8").write(s.replace(old, new))
        try:
            r = subprocess.run([sys.executable, d + "/bin/append_event_selfcheck.py"], capture_output=True, text=True, timeout=150,
                               start_new_session=True)
        except subprocess.TimeoutExpired:
            # selfcheck TREO quá 150s (bình thường ~15s) = mutant làm đường ghi treo ⇒ tính là CHẾT.
            killed.append(name); print("CHẾT  %-58s selfcheck TREO >150s" % name); continue
        fails = [l.strip()[:110] for l in r.stdout.splitlines() if l.startswith("  FAIL")]
        if r.returncode != 0 and not fails:
            alive.append(name + " [harness nổ, KHÔNG tính chết]"); print("NỔ    %s :: %s" % (name, r.stderr.strip()[-200:]))
        elif r.returncode != 0:
            killed.append(name); print("CHẾT  %-58s rc=%d fail=%d  vd: %s" % (name, r.returncode, len(fails), fails[0] if fails else r.stderr.strip()[-110:]))
        else:
            alive.append(name); print("SỐNG  %s" % name)
    finally:
        shutil.rmtree(d, ignore_errors=True)
print("\nTỔNG: %d mutant · CHẾT %d · SỐNG %d" % (len(killed) + len(alive), len(killed), len(alive)))
for a in alive: print("  còn sống:", a)
