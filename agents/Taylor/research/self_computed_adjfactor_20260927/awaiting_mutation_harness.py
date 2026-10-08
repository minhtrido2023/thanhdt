import os, shutil, subprocess, sys, tempfile
SRC = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-await-1008/bin"
PY = sys.argv[1] if len(sys.argv) > 1 else "python3"
DET, AL = "adjfactor_drift_detect.py", "adjfactor_drift_alert.sh"
M = [
 ("D1 nguong 3->2", DET, "AWAIT_MIN_TRADED_SESSIONS = 3", "AWAIT_MIN_TRADED_SESSIONS = 2", "--py"),
 ("D2 nguong 3->4", DET, "AWAIT_MIN_TRADED_SESSIONS = 3", "AWAIT_MIN_TRADED_SESSIONS = 4", "--py"),
 ("D3 < -> <=", DET, 'if out["n_traded"] < AWAIT_MIN_TRADED_SESSIONS:', 'if out["n_traded"] <= AWAIT_MIN_TRADED_SESSIONS:', "--py"),
 ("D4 >=ex -> >ex", DET, 'if b["d"] >= ex and', 'if b["d"] > ex and', "--py"),
 ("D5 vol>0 -> vol>=0", DET, 'b["vol"] > 0))', 'b["vol"] >= 0))', "--py"),
 ("D6 NULL vol = khong khop", DET, '(b.get("vol") is None or b["vol"] > 0)', '(b.get("vol") is not None and b["vol"] > 0)', "--py"),
 ("D7 bo dieu kien dir", DET, 'if out["dir"] == "vendor_missing" and out["corr"]', 'if True and out["corr"]', "--py"),
 ("D8 bo dieu kien corr", DET, 'and out["corr"] == "0" and ex_is_event', 'and ex_is_event', "--py"),
 ("D9 bo ex_is_event", DET, 'out["corr"] == "0" and ex_is_event:', 'out["corr"] == "0":', "--py"),
 ("D10 marker bo held", DET, "|{n_traded}|{held}|{dev:.6f}", "|{n_traded}|none|{dev:.6f}", "--py"),
 ("D11 marker doi cho truong", DET, "|{n_traded}|{held}|{dev:.6f}", "|{held}|{n_traded}|{dev:.6f}", "--py"),
 ("D12 rc awaiting-only -> 0", DET, "if awaiting or uncomp or nodata", "if uncomp or nodata", "--py"),
 ("D13 khong in marker awaiting", DET, "print(marker_awaiting(tk, p, h))", "pass", "--py"),
 ("D14 run_scan bo held", DET, "awaiting.append((tk, payload, h))", 'awaiting.append((tk, payload, "none"))', "--py"),
 ("D15 awaiting dem vao drift", DET, "awaiting.append((tk, payload, h))", "drift.append((tk, payload, h))", "--py"),
 ("D16 vol NULL ep 0", DET, '"vol": None if r.get("vol") is None else float(r["vol"])', '"vol": float(r.get("vol") or 0)', "--py"),
 ("D17 SQL bo Volume", DET, "t.Volume AS vol", "NULL AS vol", "--py"),
 ("A1 early-exit bo AWAITS", AL, ' && [ -z "$AWAITS" ] \\', ' \\', "--sh"),
 ("A2 quiet bo N_AWAIT_HELD_NEW", AL, '&& [ "$N_AWAIT_HELD_NEW" -eq 0 ] ', '', "--sh"),
 ("A3 khong xoa khoa cu", AL, '_sw_err="$(_state_write "" "$AWAIT_DEL_KEYS" 2>&1)"', '_sw_err=""', "--sh"),
 ("A4 khoa awaiting = khoa DRIFT", AL, 'key="${tk}|${ex}|awaiting_trade"', 'key="${tk}|${ex}"', "--sh"),
 ("A5 awaiting giao Winston", AL, '  N_AWAIT=$((N_AWAIT + 1))', '  N_AWAIT=$((N_AWAIT + 1)); SEEN_VENDOR=1', "--sh"),
 ("A6 dry-run van xoa", AL, 'if [ "$DRY_RUN" -eq 0 ] && [ -n "$AWAIT_DEL_KEYS" ]', 'if [ -n "$AWAIT_DEL_KEYS" ]', "--sh"),
 ("A7 bo dong info", AL, '[ -n "$AWAIT_LIST" ] && SECTIONS=', '[ -z "$AWAIT_LIST" ] && SECTIONS=', "--sh"),
 ("A8 an nhan nam LIVE", AL, 'item="**${tk}** (ex ${ex}, ${ntr} phiên khớp, **ĐANG NẮM LIVE: ${held}**)"', 'item="${tk} (ex ${ex}, ${ntr} phiên khớp)"', "--sh"),
 ("A9 held coi nhu none", AL, '''  item="${tk} (ex ${ex}, ${ntr} phiên khớp)"
  if [ "$held" != "none" ] && [ "$held" != "skipped" ]; then''', '''  item="${tk} (ex ${ex}, ${ntr} phiên khớp)"
  if false; then''', "--sh"),
 ("A10 payload bo markers", AL, "'awaiting_trade_markers': lines('AWAITS')", "'awaiting_trade_markers': []", "--sh"),
 ("A11 xoa moi khoa", AL, "deleted = [k.strip() for k in os.environ['DEL_KEYS'].splitlines() if k.strip() in state]", "deleted = list(state) if os.environ['DEL_KEYS'].strip() else []", "--sh"),
 ("A12 state chi ghi khi xoa", AL, "if not new_keys and not deleted:", "if not deleted:", "--sh"),
 ("A13 awaiting-only rc 10", AL, '''khong gui Discord." >&2
    exit 0''', '''khong gui Discord." >&2
    exit 10''', "--sh"),
 ("A14 nhanh awaiting-only luon dung", AL, 'if [ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ] && [ -z "$NODATAS" ]; then', 'if true; then', "--sh"),
 ("A15 khong de-dup held awaiting", AL, '    if ! _is_fresh "$key"; then\n      N_AWAIT_HELD_NEW', '    if true; then\n      N_AWAIT_HELD_NEW', "--sh"),
 ("A16 footer khong dem awaiting", AL, "${N_AWAIT} chờ giao dịch lại", "chờ giao dịch lại", "--sh"),
 ("G1 bo cong nhat quan", DET, 'if abs(out["await_resid"]) <= dev_tol:', 'if True:', "--py"),
 ("G2 Pi chi ex_named", DET, '                if ex >= ex_named:\n                    pending *= f', '                if ex == ex_named:\n                    pending *= f', "--py"),
 ("G3 tol nhan doi", DET, 'if abs(out["await_resid"]) <= dev_tol:', 'if abs(out["await_resid"]) <= 2 * dev_tol:', "--py"),
 ("G4 du bo pending", DET, 'out["await_resid"] = r_obs * pending / r_pred - 1.0', 'out["await_resid"] = r_obs / r_pred - 1.0', "--py"),
 ("G5 bo bang bang chung", DET, "        for tk, p, h in sorted(awaiting):\n            print(f\"{tk:<7}", "        for tk, p, h in []:\n            print(f\"{tk:<7}", "--py"),
 ("G6 bo chung tu awaiting", DET, '        for tk, p, _h in sorted(awaiting):\n            for n in p["notes"]:', '        for tk, p, _h in []:\n            for n in p["notes"]:', "--py"),
 ("G7 note ca khi >=3 phien", DET, '                if abs(out["await_resid"]) <= dev_tol:\n                    return "AWAITING_TRADE", out\n                notes.append(', '                if abs(out["await_resid"]) <= dev_tol:\n                    return "AWAITING_TRADE", out\n            if True:\n                notes.append(', "--py"),
 ("R1 awaiting bo loai skipped", AL, '  if [ "$held" != "none" ] && [ "$held" != "skipped" ]; then\n    # Có thể là tiền thật', '  if [ "$held" != "none" ]; then\n    # Có thể là tiền thật', "--sh"),
 ("R2 quiet chi xet DRIFTS", AL, 'if [ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ] && [ -z "$NODATAS" ]; then', 'if [ -z "$DRIFTS" ]; then', "--sh"),
 ("R4 quiet DRIFTS+UNCOMPS", AL, 'if [ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ] && [ -z "$NODATAS" ]; then', 'if [ -z "$DRIFTS" ] && [ -z "$UNCOMPS" ]; then', "--sh"),
 ("H1 tieu de suy tu TODO rong", AL, 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_NEW" -eq 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ] \\\n   && [ "$N_NODATA_HELD" -eq 0 ] && [ "$FEED_BAD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ]', 'if [ -z "$TODO" ]', "--sh"),
 ("H2 tieu de bo N_NEW", AL, 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_NEW" -eq 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ]', 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ]', "--sh"),
 ("H3 tieu de khong bao gio doi", AL, 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_NEW" -eq 0 ]', 'if false && [ "$N_NEW" -eq 0 ]', "--sh"),
 ("H5 tieu de bo FEED_BAD", AL, '   && [ "$N_NODATA_HELD" -eq 0 ] && [ "$FEED_BAD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ] \\\n   && [ -z "$STATE_DEL_ERR" ]; then\n  # Còn DRIFT', '   && [ "$N_NODATA_HELD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ] \\\n   && [ -z "$STATE_DEL_ERR" ]; then\n  # Còn DRIFT', "--sh"),
 ("H6 tieu de bo N_UNCOMP_HELD", AL, 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_NEW" -eq 0 ] && [ "$N_UNCOMP_HELD" -eq 0 ] \\', 'if [ "$N_AWAIT_HELD_NEW" -gt 0 ] && [ "$N_NEW" -eq 0 ] \\', "--sh"),
 ("H4 tieu de bo N_NODATA_HELD", AL, '   && [ "$N_NODATA_HELD" -eq 0 ] && [ "$FEED_BAD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ] \\\n   && [ -z "$STATE_DEL_ERR" ]; then\n  # Còn DRIFT', '   && [ "$FEED_BAD" -eq 0 ] && [ "$EMPTY_UNIVERSE" -eq 0 ] \\\n   && [ -z "$STATE_DEL_ERR" ]; then\n  # Còn DRIFT', "--sh"),
 ("X2 chi xoa khoa ma khong nam", AL, "  AWAIT_DEL_KEYS=\"${AWAIT_DEL_KEYS}${tk}|${ex}\"", "  [ \"$held\" = none ] && AWAIT_DEL_KEYS=\"${AWAIT_DEL_KEYS}${tk}|${ex}\"", "--sh"),
 ("B1a xoa hong rc 0", AL, "    raise SystemExit(3)", "    raise SystemExit(0)", "--sh"),
 ("B1b xoa hong in 'DA gui roi'", AL, "    if new_keys:\n        sys.stderr.write('adjfactor_drift_alert: KHONG ghi", "    if True:\n        sys.stderr.write('adjfactor_drift_alert: KHONG ghi", "--sh"),
 ("B1c quiet bo STATE_DEL_ERR", AL, ' \\\n   && [ -z "$STATE_DEL_ERR" ]; then\n  [ "$DRY_RUN" -eq 1 ]', '; then\n  [ "$DRY_RUN" -eq 1 ]', "--sh"),
 ("B1d bo muc state", AL, '[ -n "$STATE_DEL_ERR" ] && SECTIONS=', '[ -z "$STATE_DEL_ERR" ] && SECTIONS=', "--sh"),
 ("B2 headline doc SCAN", AL, '  if [ -n "$DRIFTS" ]; then\n    _no_drift', '  if [ "$N_DRIFT" -gt 0 ]; then\n    _no_drift', "--sh"),
 ("B3a khe >1", DET, 'AWAIT_MIN_TRADED_SESSIONS and gap:', 'AWAIT_MIN_TRADED_SESSIONS and len(gap) > 1:', "--py"),
 ("B3b khe >2", DET, 'AWAIT_MIN_TRADED_SESSIONS and gap:', 'AWAIT_MIN_TRADED_SESSIONS and len(gap) > 2:', "--py"),
 ("G8 bo cong cham ex-date", DET, 'if out["n_traded"] < AWAIT_MIN_TRADED_SESSIONS and gap:', 'if False:', "--py"),
 ("G9 gap tinh ca ex", DET, 'gap = [b["d"] for b in series if d1 < b["d"] < ex_named]', 'gap = [b["d"] for b in series if d1 < b["d"] <= ex_named]', "--py"),
 ("G10 gap tinh ca d1", DET, 'gap = [b["d"] for b in series if d1 < b["d"] < ex_named]', 'gap = [b["d"] for b in series if d1 <= b["d"] < ex_named]', "--py"),
 ("H7 headline luon 'that'", AL, '  if [ -n "$DRIFTS" ]; then\n    _no_drift=', '  if false; then\n    _no_drift=', "--sh"),
 ("H8 TODO bo chu MOI", AL, 'TODO=" không có việc MỚI', 'TODO=" không có', "--sh"),
 ("L1 log luon 'khong ma nao'", AL, '    if [ "$N_AWAIT_HELD" -gt 0 ]; then', '    if false; then', "--sh"),
 ("L2 khong dem held", AL, '    N_AWAIT_HELD=$((N_AWAIT_HELD + 1))\n', '', "--sh"),
]

def run_copy(mutate=None, mode="--py"):
    with tempfile.TemporaryDirectory() as tmp:
        b = os.path.join(tmp, "bin"); os.makedirs(b)
        for fn in (DET, AL, "adjfactor_drift_detect_selfcheck.py", "adjfactor_drift_daily.sh"):
            shutil.copy(os.path.join(SRC, fn), b)
        if mutate:
            f, old, new = mutate
            p = os.path.join(b, f); s = open(p).read()
            if s.count(old) != 1:
                return None, f"BADMUT count={s.count(old)}"
            open(p, "w").write(s.replace(old, new))
        r = subprocess.run([PY, os.path.join(b, "adjfactor_drift_detect_selfcheck.py"), mode],
                           capture_output=True, text=True, timeout=900)
        fails = {l.strip()[5:].split("   ")[0] for l in r.stdout.splitlines() if l.strip().startswith("FAIL ")}
        done = "assertion PASS ===" in r.stdout
        return (fails, done, r), None

BASE = {}
for mode in ("--py", "--sh"):
    (fails, done, r), _ = run_copy(None, mode)
    BASE[mode] = fails
    print(f"baseline {mode}: done={done} rc={r.returncode} fails={sorted(fails)}", flush=True)

alive = []
ONLY = os.environ.get("ONLY")
for name, f, old, new, mode in M:
    if ONLY and not name.startswith(tuple(ONLY.split(","))): continue
    res, err = run_copy((f, old, new), mode)
    if err:
        print(f"BADMUT {name}: {err}"); alive.append(name + " (BADMUT)"); continue
    fails, done, r = res
    newf = sorted(fails - BASE[mode])
    killed = bool(newf) or not done
    why = newf[:1] if newf else (["CRASH: " + (r.stderr.strip().splitlines() or ["?"])[-1]] if not done else [])
    print(f"{'KILLED' if killed else 'ALIVE '} {name}  {why}", flush=True)
    if not killed: alive.append(name)
print(f"=== {len(M)-len(alive)}/{len(M)} mutation bi giet; song: {alive}")
