"""Mutation cho từng nhánh mới của gate-source check. Mỗi mutant: sửa 1 chỗ trong bản worktree,
chạy selfcheck liên quan, PHẢI đỏ; rồi khôi phục nguyên văn (kiểm md5 sau cùng)."""
import hashlib, re, subprocess, sys
from pathlib import Path
W = Path(sys.argv[1])
SH, PYH, SPR = W / "bin/bq_freshness_check.sh", W / "bin/gate_source_check.py", W / "bin/send_plan_report.sh"
CHAIN = ["python3", str(W / "bin/bq_freshness_check_selfcheck.py")]
PLAN = ["python3", str(W / "bin/send_plan_report_state_gate_selfcheck.py")]
M = [
 ("S1 bỏ tee (không giữ output lượt publish)", SH, ' | tee "$GATE_PUB_OUT"\n', '\n', CHAIN),
 ("S2 bỏ --alert (không gửi kênh nào)", SH, '--since-epoch "$PIPELINE_START_EPOCH" --alert \\', '--since-epoch "$PIPELINE_START_EPOCH" \\', CHAIN),
 ("S3 bỏ --since-epoch (báo cả file state cũ)", SH, '  --since-epoch "$PIPELINE_START_EPOCH" --alert \\', '  --alert \\', CHAIN),
 ("S4 helper lỗi ⇒ exit 1 (biến cảnh báo thành CHẶN)", SH, '  || echo "  [WARN] gate_source_check.py thoát rc=$?', '  || exit 1; echo "  [WARN] gate_source_check.py thoát rc=$?', CHAIN),
 ("S5 không xoá file tạm", SH, '[ "$GATE_PUB_OUT" = /dev/null ] || rm -f "$GATE_PUB_OUT"', ':', CHAIN),
 ("S6 nguồn suy giảm ⇒ FAILED=1 (chặn plan)", SH, '[ "$GATE_PUB_OUT" = /dev/null ] || rm -f "$GATE_PUB_OUT"', '[ "$GATE_PUB_OUT" = /dev/null ] || rm -f "$GATE_PUB_OUT"; grep -q DT5G_macro deploy_golive_dt5g_v4/golive_state_today.json || FAILED=1', CHAIN),
 ("S7 bỏ fallback /dev/null khi mktemp hỏng", SH, 'GATE_PUB_OUT="$(mktemp)" || GATE_PUB_OUT=/dev/null', 'GATE_PUB_OUT="$(mktemp)"', CHAIN),
 ("P20 /dev/null bị báo thành 'không tìm thấy dòng cổng'", PYH, '    if not publish_log or publish_log == os.devnull:', '    if not publish_log:', CHAIN),
 ("P1 DT5G_macro vẫn báo (bỏ nhánh im lặng)", PYH, '    if src == GOOD_SOURCE:\n        return 0\n\n    doc = doc or {}', '    doc = doc or {}', CHAIN),
 ("P2 thiếu trường source coi như DT5G_macro", PYH, '    return MISSING_SOURCE if src is None else str(src)', '    return GOOD_SOURCE if src is None else str(src)', CHAIN + PLAN),
 ("P3 file state hỏng ⇒ im lặng", PYH, '    src = UNREADABLE if doc is None else source_of(doc)', '    src = GOOD_SOURCE if doc is None else source_of(doc)', CHAIN),
 ("P4 giá trị lạ coi như ổn (chỉ báo 2 nguồn đã biết)", PYH, '    if src == GOOD_SOURCE:\n        return 0\n\n    doc = doc or {}', '    if src not in NO_CAP_SOURCES and src not in (MISSING_SOURCE, UNREADABLE):\n        return 0\n\n    doc = doc or {}', CHAIN),
 ("P5 bỏ khoá chống lặp", PYH, '    same = prev.get("publish_date") == publish_date and prev.get("source") == src', '    same = False', CHAIN),
 ("P6 khoá chống lặp không theo ngày", PYH, '    same = prev.get("publish_date") == publish_date and prev.get("source") == src', '    same = prev.get("source") == src', CHAIN),
 ("P7 đánh dấu đã gửi dù kênh hỏng", PYH, '        if ok:\n            sent[kind] = True', '        if ok or True:\n            sent[kind] = True', CHAIN),
 ("P8 không bỏ qua khi lượt publish không ghi file", PYH, '    if mtime is None or mtime < a.since_epoch:', '    if mtime is None:', CHAIN),
 ("P9 file state không tồn tại ⇒ vẫn báo", PYH, '    if mtime is None or mtime < a.since_epoch:', '    if mtime is not None and mtime < a.since_epoch:', CHAIN),
 ("P10 nguyên nhân HARDCODE thay vì dòng cổng thật", PYH, '    return hits[-1][:300], ""', '    return "[get_gated_state] DT4_only: file health cũ quá 1440 phút", ""', CHAIN),
 ("P11 không có dòng cổng ⇒ đoán nguyên nhân", PYH, '        return "", "không tìm thấy dòng [get_gated_state] trong output lượt publish này"', '        return "", "nhiều khả năng do file health cũ"', CHAIN),
 ("P12 bỏ ts của macro_health khỏi tin", PYH, '        return (f"status={h.get(\'status\')}, ts={h.get(\'ts\')}, "', '        return (f"status={h.get(\'status\')}, "', CHAIN),
 ("P13 health không đọc được ⇒ giấu lỗi thật", PYH, '        return f"KHÔNG đọc được ({_err(exc)})"', '        return "status=?, ts=?"', CHAIN),
 ("P14 luôn khẳng định 'KHÔNG áp macro cap'", PYH, '    if src in NO_CAP_SOURCES:', '    if True:', CHAIN + PLAN),
 ("P15 thêm Telegram (2 tin tới người)", PYH, '        ("discord", [os.path.join(MIKE_BIN, "notify_thread.sh"), msg, CHANNEL]),', '        ("discord", [os.path.join(MIKE_BIN, "notify_thread.sh"), msg, CHANNEL]),\n        ("tg", [os.path.join(MIKE_BIN, "notify.sh"), msg]),', CHAIN),
 ("P16 bus event không phải error", PYH, '"Taylor", "error",', '"Taylor", "finding",', CHAIN),
 ("P17 bus topic không khoá theo ngày publish", PYH, 'f"dt5g-gate-source-degraded-{publish_date}"', '"dt5g-gate-source-degraded"', CHAIN),
 ("P18 nguồn suy giảm ⇒ thoát rc≠0", PYH, '    for kind, cmd in sends:', '    return 3\n    for kind, cmd in sends:', CHAIN),
 ("P19 sai topic Discord", PYH, 'CHANNEL = "trading_daily"', 'CHANNEL = "plan_approval"', CHAIN),
 ("R1 plan report tin marker của lượt publish khác", PYH, '    if m.get("source") == src and m.get("published_at") == doc.get("published_at"):', '    if m.get("source") == src:', PLAN),
 ("R2 plan report in dòng cả khi DT5G_macro", PYH, '    if src == GOOD_SOURCE:\n        return ""\n    m = load_marker(workdir)', '    m = load_marker(workdir)', PLAN + CHAIN),
 ("R3 send_plan_report không chèn dòng", SPR, 'if _gs_line:\n    lines.append(f"   {_gs_line}")', 'if False:\n    lines.append(f"   {_gs_line}")', PLAN),
 ("R4 send_plan_report nuốt lỗi import câm", SPR, '    from gate_source_check import plan_report_line as _gate_src_line', '    from gate_source_check_KHONG_CO import plan_report_line as _gate_src_line', PLAN),
]
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
before = {p: md5(p) for p in (SH, PYH, SPR)}
bad = 0
for name, path, old, new, cmd in M:
    orig = path.read_text(encoding="utf-8")
    if orig.count(old) != 1:
        print(f"LỖI-MUTANT  {name}: chuỗi gốc xuất hiện {orig.count(old)} lần (cần đúng 1)"); bad += 1; continue
    try:
        path.write_text(orig.replace(old, new), encoding="utf-8")
        outs, rcs = [], []
        for i in range(0, len(cmd), 2):
            r = subprocess.run(cmd[i:i + 2], capture_output=True, text=True, timeout=600)
            outs.append(r.stdout + r.stderr); rcs.append(r.returncode)
        allout = "\n".join(outs)
        nfail = len(re.findall(r"^FAIL: |^\[FAIL\]", allout, flags=re.M))
        killed = any(rcs) and nfail > 0
        first = next((l for l in allout.splitlines() if l.startswith(("FAIL: ", "[FAIL]"))), "")[:110]
        print(f"{'BẮT ĐƯỢC ' if killed else 'SỐNG SÓT'}  {name}: rc={rcs} assertion đỏ={nfail} · {first}")
        bad += 0 if killed else 1
    finally:
        path.write_text(orig, encoding="utf-8")
print(f"\nTổng {len(M)} mutant · không bắt được/lỗi: {bad} · file khôi phục nguyên văn: {all(md5(p) == h for p, h in before.items())}")
for cmd in (CHAIN, PLAN):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(f"sau khôi phục {Path(cmd[1]).name}: rc={r.returncode} · {(r.stdout.strip().splitlines() or ['?'])[-1]}")
