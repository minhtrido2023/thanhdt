#!/usr/bin/env python3
"""Selfcheck livermore_report_block.py — KHÔNG gọi claude thật (LIVERMORE_CLAUDE_BIN giả), KHÔNG chạm BQ/sổ thật.

Chạy 3 TZ (env -u TZ, America/New_York, UTC — §16/§19) rồi chạy MUTANT (sửa 1 chỗ trong bản sao mã, mỗi mutant
phải bị ít nhất 1 assertion bắt). rc 0 = mọi TZ PASS và mọi mutant bị bắt.
"""
import datetime as dt
import math
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.environ.get("LVB_SC_BIN") or HERE
WC_ROOT = os.path.dirname(os.path.dirname(HERE))      # <WorkingClaude>/<mike|worktree>/bin → <WorkingClaude>

FAKE_CLAUDE = r'''#!/usr/bin/env python3
import os, re, sys
P = sys.argv[-1]; mode = os.environ.get("FAKE_MODE", "good")
open(os.environ["FAKE_CLAUDE_COUNT"], "a").write("x\n")
if "CHẾ ĐỘ REPORT_BLOCK" not in P:                      # đường đọc có forecast (livermore_run.sh)
    d = re.search(r"AS_OF = ([0-9-]+)", P).group(1)
    print("# fake\n<<<FORECAST\n- H20_DIR: DOWN\n- H20_P_UP: 0.40\n- LEVEL: 1650 BREAK\n"
          "- INVALIDATION: đóng >1800 hai phiên\nFORECAST>>>\nRESULT|%s|DOWN|0.40|BREAK" % d)
    sys.exit(0)
open(os.environ["FAKE_BLOCK_COUNT"], "a").write("x\n")
nblk = len(open(os.environ["FAKE_BLOCK_COUNT"]).read().split())
if mode == "exit1":
    sys.exit(1)
F = dict(re.findall(r"^- ([^:\n]+): (.+)$", P, re.M))
v = lambda pre: next(val for k, val in F.items() if k.startswith(pre))
close = v("Đóng cửa ")
xu = f"- *Xu hướng:* chỉ số đóng cửa {close}, thay đổi trong kỳ {v('Thay đổi trong kỳ')}."
if mode == "round":
    xu = "- *Xu hướng:* chỉ số đóng cửa " + re.sub(r",\d+", "", close) + "."
if mode == "stray" or (mode == "stray_once" and nblk == 1):
    xu += " Mục tiêu 1.800 điểm."
if mode == "date":
    xu += " Kể từ 30/10/2026."
if mode == "deny":
    xu += " Theo DT5G thì ổn."
if mode == "ema":
    xu += " Cần vượt EMA 1800."
if mode == "rsi70":
    xu += " RSI(70) là vùng quá mua."
if mode == "signflip":
    ch = v("Thay đổi trong kỳ")
    xu = "- *Xu hướng:* thay đổi trong kỳ " + ({"+": "\u2212", "\u2212": "+"}[ch[0]] + ch[1:]) + "."
if mode == "s200":
    xu += " Có thể thêm 200 điểm."
if mode == "sameday":
    xu += " Phiên 23/10 đáng chú ý."   # as-of có trong SỐ LIỆU dạng dd/mm/yyyy ⇒ hợp lệ khi viết dd/mm
hk = f"- *Hỗ trợ/kháng cự:* vùng MA20 {v('MA20 ngày')}; MA200 là kháng cự."
dl = f"- *Động lượng:* RSI(14) {v('RSI(14)')}."
tk = f"- *Thanh khoản:* khối lượng trung bình {v('Khối lượng khớp trung bình phiên trong kỳ')}."
if "KHÔNG có số liệu độ rộng" in P:
    dr = "- *Độ rộng:* không có số liệu đã đối soát cho kỳ này."
    if mode == "breadth_num":
        dr = "- *Độ rộng:* khoảng 45,0% mã trên MA50."
else:
    dr = f"- *Độ rộng:* {v('Tỷ lệ cổ phiếu đóng cửa trên MA50 ngày')}."
lines = [xu, hk, dl, tk, dr]
if mode == "fourlines":
    lines = lines[:4]
if mode == "nomarker":
    print("\n".join(lines)); sys.exit(0)
print("Lời dẫn thừa\n<<<BLOCK\n" + "\n".join(lines) + "\nBLOCK>>>\nđuôi thừa")
'''

AS_OF = dt.date(2026, 10, 23)
REG_HEAD = "# Livermore reads (append-only)\n\n## Entries\n"


def entry(as_of, due, trig="LIVE-BASELINE"):
    return (f"\n### LVR-{as_of}\n- as_of: {as_of}\n- created: x\n- trigger: {trig}\n- close_asof: 1700.0\n"
            f"- due: {due} (calendar=CONFIRMED)\n- report: x\n- dt5g_at_asof: 3\n- forecast:\n"
            f"    - H20_DIR: UP\n    - H20_P_UP: 0.56\n    - LEVEL: 1677 HOLD\n"
            f"    - INVALIDATION: đóng <1690 trong 5 phiên với vol ≥700M, hoặc bất kỳ phiên đóng <1677.\n"
            f"- result: RESULT|{as_of}|UP|0.56|HOLD\n- outcome:\n")


def inner():
    tmp = tempfile.mkdtemp(prefix="lvb_sc_")
    env = dict(LIVERMORE_TEST="1", LIVERMORE_NOW="2026-10-24T09:00:00",
               LIVERMORE_REGISTRY=os.path.join(tmp, "reg.md"), LIVERMORE_DATA_DIR=os.path.join(tmp, "data"),
               LIVERMORE_STATE_DIR=os.path.join(tmp, "state"), LIVERMORE_BARS_CSV=os.path.join(tmp, "bars.csv"),
               LIVERMORE_IND_CSV=os.path.join(tmp, "ind.csv"), LIVERMORE_BREADTH_CSV=os.path.join(tmp, "br.csv"),
               LIVERMORE_DT5G_CSV=os.path.join(tmp, "dt5g.csv"), LIVERMORE_CLAUDE_BIN=os.path.join(tmp, "claude_fake"),
               LIVERMORE_RUN_BIN=os.path.join(BIN, "livermore_run.sh"), LIVERMORE_PY=sys.executable,
               FAKE_CLAUDE_COUNT=os.path.join(tmp, "cc"), FAKE_BLOCK_COUNT=os.path.join(tmp, "bc"))
    os.environ.update(env)
    p = env["LIVERMORE_CLAUDE_BIN"]
    open(p, "w").write(FAKE_CLAUDE.replace("#!/usr/bin/env python3", "#!" + sys.executable, 1))
    os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    sys.path.insert(0, BIN)
    import livermore_common as C
    import livermore_report_block as B

    fails, oks = [], []

    def check(name, cond, detail=""):
        (oks if cond else fails).append(name)
        print(("  ✅ " if cond else "  ❌ ") + name + ("" if cond else f"  [{str(detail)[:300]}]"))

    # ── dữ liệu tổng hợp: 400 phiên tới AS_OF + 3 phiên SAU (mù về sau phải loại) ──
    days, d = [], AS_OF
    while len(days) < 400:
        if C.is_session(d):
            days.append(d)
        d -= dt.timedelta(days=1)
    days.reverse()
    after, d = [], AS_OF
    for _ in range(3):
        d = C.next_session(d); after.append(d)
    all_days = days + after
    closes = [1700 + 60 * math.sin(i / 17) + 0.2 * i for i in range(len(all_days))]

    def write_bars(drop_asof=False):
        with open(env["LIVERMORE_BARS_CSV"], "w") as fh:
            fh.write("time,Open,High,Low,Close,Volume\n")
            for i, (dd, c) in enumerate(zip(all_days, closes)):
                if drop_asof and dd == AS_OF:
                    continue
                fh.write(f"{dd},{c - 2},{c + 5},{c - 6},{c},{6e8 + 1e7 * (i % 9)}\n")

    def write_ind(ma_bias=1.0):
        with open(env["LIVERMORE_IND_CSV"], "w") as fh:
            fh.write("time,MA20,MA50,MA200,D_RSI,D_MACDdiff,D_CMF\n")
            for i, dd in enumerate(all_days):
                if i < 200:
                    continue
                m = {n: sum(closes[i - n + 1:i + 1]) / n for n in (20, 50, 200)}
                fh.write(f"{dd},{m[20] * ma_bias},{m[50]},{m[200]},0.55,{math.sin(i / 3)},0.01\n")

    def write_breadth(on=True):
        with open(env["LIVERMORE_BREADTH_CSV"], "w") as fh:
            fh.write("time,pct,n\n")
            if on:
                for i, dd in enumerate(all_days[-30:]):
                    fh.write(f"{dd},{30 + i},{340 + i % 3}\n")

    open(env["LIVERMORE_DT5G_CSV"], "w").write("time,state\n")

    def sess_before(n):
        return days[-1 - n]

    def reset(reg_entries=(), mode="good"):
        for k in ("cc", "bc"):
            open(os.path.join(tmp, k), "w").close()
        shutil.rmtree(env["LIVERMORE_DATA_DIR"], ignore_errors=True)
        open(env["LIVERMORE_REGISTRY"], "w").write(REG_HEAD + "".join(reg_entries))
        os.environ["FAKE_MODE"] = mode
        write_bars(); write_ind(); write_breadth()

    def nblock():
        return len(open(os.path.join(tmp, "bc")).read().split())

    def run(kind="weekly", pe=AS_OF):
        return B.ensure(kind, pe)

    md_p, js_p, fj_p = B.paths(AS_OF, "weekly")

    # 1. REPEAT: forecast 2 phiên trước ⇒ nhắc lại nguyên văn, không ghi sổ, 1 lần gọi khối
    reset([entry(sess_before(2), sess_before(-18))])
    rc, meta = run()
    md = open(md_p).read() if os.path.exists(md_p) else ""
    check("#1 REPEAT rc=0 PASS", rc == 0 and meta.get("status") == "PASS", meta)
    check("#1b mode REPEAT, entry đúng", (meta.get("forecast") or {}).get("mode") == "REPEAT"
          and meta["forecast"]["entry_as_of"] == str(sess_before(2)), meta.get("forecast"))
    check("#1c INVALIDATION nguyên văn từ sổ", "đóng <1690 trong 5 phiên với vol ≥700M, hoặc bất kỳ phiên đóng <1677." in md)
    check("#1d sổ KHÔNG có entry mới", "LVR-2026-10-23" not in open(env["LIVERMORE_REGISTRY"]).read())
    check("#1e đúng 1 lần gọi khối, 5 dòng + dòng dự báo + nguồn Livermore", nblock() == 1
          and md.count("\n- *") == 6 and "nhận định độc lập của Livermore" in md and "nhắc lại nguyên văn" in md, md[:200])
    check("#1f không hứa độ chính xác: có câu 'chưa đủ để đánh giá độ chính xác'", "chưa đủ" in md and "không phải khuyến nghị" in md)
    check("#1g mù về sau: không có ngày sau as-of trong khối", all(x.strftime("%d/%m/%Y") not in md for x in after))
    # 2. idempotent
    rc2, meta2 = run()
    check("#2 chạy lại ⇒ EXISTS, không gọi LLM", rc2 == 0 and meta2.get("note") == "EXISTS" and nblock() == 1, meta2)
    # 3. md bị sửa ⇒ sha lệch ⇒ không còn PASS, verify-report
    rep = os.path.join(tmp, "rep.md")
    open(rep, "w").write("# r\n\n" + md + "\n## khác\n")
    rcv, _ = B.verify_report(rep, "weekly", AS_OF)
    check("#3 verify-report: chứa nguyên văn ⇒ rc0", rcv == 0)
    open(rep, "w").write("# r\n\n" + md.replace("Xu hướng", "Xu hướng chính") + "\n")
    rcv, outv = B.verify_report(rep, "weekly", AS_OF)
    check("#3b verify-report: bị sửa chữ ⇒ rc1 NOT_VERBATIM", rcv == 1 and outv["status"] == "NOT_VERBATIM", outv)
    open(md_p, "a").write("số lậu 9.999\n")
    ok, why = B.verify_pass(AS_OF, "weekly")
    check("#3c md bị sửa sau PASS ⇒ verify_pass False", not ok, why)
    # 4. biên khoảng cách: 19 phiên ⇒ REPEAT, 20 ⇒ NEW
    reset([entry(sess_before(19), "2026-11-30")])
    rc, meta = run()
    check("#4 gap 19 phiên ⇒ REPEAT", rc == 0 and meta["forecast"]["mode"] == "REPEAT" and meta["forecast"]["gap"] == 19, meta.get("forecast"))
    reset([entry(sess_before(20), "2026-11-30")])
    rc, meta = run()
    regtxt = open(env["LIVERMORE_REGISTRY"]).read()
    check("#4b gap 20 phiên ⇒ NEW qua livermore_run.sh, ghi sổ trigger REPORT_BLOCK_WEEKLY",
          rc == 0 and (meta.get("forecast") or {}).get("mode") == "NEW" and "### LVR-2026-10-23" in regtxt
          and "trigger: REPORT_BLOCK_WEEKLY" in regtxt, (meta, regtxt[-300:]))
    check("#4c NEW: dòng dự báo lấy từ entry mới (GIẢM, 1650 bị phá)", "**GIẢM**" in open(md_p).read()
          and "1650: bị phá" in open(md_p).read() and "lập mới" in open(md_p).read())
    # 5. mù về sau: entry SAU as-of KHÔNG được nhắc lại; nó nằm trong 20 phiên ⇒ không lập NEW lùi ngày ⇒ NONE
    reset([entry(after[0], "2026-12-01")])
    rc, meta = run()
    md5 = open(md_p).read() if os.path.exists(md_p) else ""
    check("#5 entry sau as-of KHÔNG được dùng làm forecast đang mở (NONE, không ghi sổ, không lộ)",
          rc == 0 and meta["forecast"]["mode"] == "NONE" and meta["forecast"]["entry_as_of"] is None
          and "LVR-2026-10-23" not in open(env["LIVERMORE_REGISTRY"]).read()
          and "không có dự báo được lập cho kỳ này" in md5 and "1677" not in md5, meta.get("forecast"))
    # 5b. báo cáo trễ (> LATE_MAX phiên) ⇒ không lập forecast lùi ngày
    reset([entry(sess_before(25), "2026-11-01")])
    os.environ["LIVERMORE_NOW"] = "2026-11-06T20:00:00"
    rc, meta = run()
    os.environ["LIVERMORE_NOW"] = env["LIVERMORE_NOW"]
    check("#5b báo cáo trễ 10 phiên ⇒ NONE, sổ không có entry lùi ngày", rc == 0 and meta["forecast"]["mode"] == "NONE"
          and "báo cáo trễ" in meta["forecast"]["why"] and "LVR-2026-10-23" not in open(env["LIVERMORE_REGISTRY"]).read(),
          meta.get("forecast"))
    # 5c. dòng dự báo từ sổ chứa từ cấm ⇒ FAIL
    reset([entry(sess_before(2), "2026-11-20").replace("hoặc bất kỳ", "theo DT5G hoặc bất kỳ")])
    rc, meta = run()
    check("#5c INVALIDATION trong sổ lộ DT5G ⇒ FAIL, không .md", rc == 1 and not os.path.exists(md_p), meta)
    # 6. số lạ ⇒ FAIL sau 2 lần, không PASS file
    for mode, tag in (("stray", "số lạ 1.800"), ("date", "ngày lạ 30/10"), ("deny", "từ cấm DT5G"),
                      ("round", "làm tròn 1.774"), ("ema", "ngưỡng tự đặt EMA 1800"), ("rsi70", "ngưỡng RSI(70)"),
                      ("signflip", "sai dấu thay đổi trong kỳ"), ("s200", "số 200 (MA200 không được cho lậu 200)"),
                      ("nomarker", "thiếu dấu mốc"), ("fourlines", "thiếu dòng"), ("exit1", "claude rc≠0")):
        reset([entry(sess_before(2), "2026-11-20")], mode)
        rc, meta = run()
        check(f"#6 {tag} ⇒ FAIL, không có .md/.json PASS, có FAILED.json",
              rc == 1 and not os.path.exists(md_p) and not os.path.exists(js_p) and os.path.exists(fj_p), meta)
    reset([entry(sess_before(2), "2026-11-20")], "stray")
    run()
    check("#6b retry đúng 2 lần rồi dừng", nblock() == 2, nblock())
    reset([entry(sess_before(2), "2026-11-20")], "stray_once")
    rc, meta = run()
    check("#6c lần 1 lỗi, lần 2 sạch ⇒ PASS attempts=2, FAILED cũ không có", rc == 0 and meta.get("attempts") == 2
          and not os.path.exists(fj_p), meta)
    reset([entry(sess_before(2), "2026-11-20")], "sameday")
    rc, meta = run()
    check("#6d ngày dd/mm có trong SỐ LIỆU ⇒ hợp lệ", rc == 0, meta)
    # 7. as-of lệch / kỳ chưa đóng / MA lệch
    reset([entry(sess_before(2), "2026-11-20")]); write_bars(drop_asof=True)
    try:
        run(); r7 = "no-raise"
    except B.BlockError as ex:
        r7 = str(ex)
    check("#7 thiếu bar đúng as-of ⇒ BlockError as-of lệch", "as-of lệch" in r7, r7)
    reset([entry(sess_before(2), "2026-11-20")])
    os.environ["LIVERMORE_NOW"] = "2026-10-23T15:00:00"      # trước giờ đóng sổ ⇒ phiên 23/10 chưa có
    try:
        run(); r7 = "no-raise"
    except B.BlockError as ex:
        r7 = str(ex)
    os.environ["LIVERMORE_NOW"] = env["LIVERMORE_NOW"]
    check("#7b kỳ chưa đóng ⇒ BlockError", "kỳ chưa đóng" in r7 and nblock() == 0, r7)
    reset([entry(sess_before(2), "2026-11-20")]); write_ind(ma_bias=1.01)
    try:
        run(); r7 = "no-raise"
    except B.BlockError as ex:
        r7 = str(ex)
    check("#7c MA20 BQ lệch SMA tự tính 1% ⇒ BlockError", "MA20" in r7, r7)
    # 8. không có độ rộng
    reset([entry(sess_before(2), "2026-11-20")]); write_breadth(on=False)
    rc, meta = run()
    check("#8 không có độ rộng ⇒ câu quy định, PASS", rc == 0 and "không có số liệu đã đối soát" in open(md_p).read(), meta)
    reset([entry(sess_before(2), "2026-11-20")], "breadth_num"); write_breadth(on=False)
    rc, meta = run()
    check("#8b không có độ rộng mà Livermore bịa số độ rộng ⇒ FAIL", rc == 1, meta)
    # 9. monthly
    try:
        B.period_bounds("monthly", dt.date(2026, 9, 29)); r9 = "no-raise"
    except B.BlockError as ex:
        r9 = str(ex)
    check("#9 monthly period_end không phải cuối tháng ⇒ BlockError", "cuối tháng" in r9, r9)
    a9, p9, s9, ps9 = B.period_bounds("monthly", dt.date(2026, 9, 30))
    check("#9b monthly 09/2026: as_of 30/09, kỳ trước 31/08, đầu kỳ 01/09",
          (a9, s9, ps9) == (dt.date(2026, 9, 30), dt.date(2026, 9, 1), dt.date(2026, 8, 1)) and p9 <= dt.date(2026, 8, 31),
          (a9, p9, s9, ps9))
    # 10. tokenizer
    _, n = B.tokens("MA20 1.774,15 RSI(14) 57,2 MA200")
    check("#10 tokens: định danh MA20/RSI(14)/MA200 không sinh số", n == {"abs:1774.15", "abs:57.2"}, n)
    _, n = B.tokens("thay đổi +4,00% (cuối kỳ trước \u22126,06) vùng 1.740-1.800")
    check("#10b tokens: dấu giữ khi đứng sau khoảng trắng/'(', gạch nối khoảng không phải dấu",
          n == {"abs:4", "+4", "abs:6.06", "-6.06", "abs:1740", "abs:1800"}, n)
    # 12. cổng giao báo cáo (gate_report + report_delivery_gate._check_livermore_block)
    reset([entry(sess_before(2), "2026-11-20")]); run()
    blk = open(md_p).read().strip()
    check("#12 gate: PASS + nguyên văn ⇒ qua", B.gate_report("x\n" + blk + "\ny", "weekly", AS_OF) is None)
    check("#12b gate: PASS + khối bị sửa ⇒ CHẶN", B.gate_report(blk.replace("*Xu hướng:* ", "*Xu hướng:* đã sửa "), "weekly", AS_OF) is not None)
    check("#12c gate: PASS + người soạn tự viết khối khác ⇒ CHẶN", B.gate_report("**Kỹ thuật** tự viết", "weekly", AS_OF) is not None)
    os.remove(js_p)
    check("#12d gate: không PASS + gắn tên Livermore ⇒ CHẶN", B.gate_report(blk, "weekly", AS_OF) is not None)
    check("#12e gate: không PASS + khối tự viết không gắn tên ⇒ qua (fallback)",
          B.gate_report("**Kỹ thuật** tự viết", "weekly", AS_OF) is None)
    if os.path.exists(os.path.join(BIN, "report_delivery_gate.py")):
        import report_delivery_gate as RDG
        from pathlib import Path
        rp = Path(tmp) / "SpaceX_weekly_report_2026-10-19_to_2026-10-23.md"
        rp.write_text("# r\n" + blk + "\n", encoding="utf-8")
        try:
            RDG._check_livermore_block(rp); r12 = "pass"
        except RuntimeError as ex:
            r12 = str(ex)
        check("#12f report_delivery_gate._check_livermore_block CHẶN khi gắn tên Livermore mà không có PASS",
              "livermore-block BLOCK" in r12, r12)
    # 11. lệnh CLI dưới TZ hiện tại
    r = subprocess.run([sys.executable, os.path.join(BIN, "livermore_report_block.py"), "facts", "--kind", "weekly",
                        "--period-end", str(AS_OF)], capture_output=True, text=True, env=dict(os.environ))
    check("#11 CLI facts rc=0, as_of đúng, không ngày sau as-of",
          r.returncode == 0 and '"as_of": "2026-10-23"' in r.stdout and all(x.strftime("%d/%m/%Y") not in r.stdout for x in after),
          r.stderr[-300:])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'❌ FAIL' if fails else '✅ PASS'} {len(oks)}/{len(oks) + len(fails)}")
    return 1 if fails else 0


MUTANTS = [
    ("M1 bỏ kiểm số lạ", "    bad_n = sorted(b_nums - f_nums)", "    bad_n = []"),
    ("M2 khoảng cách 19 phiên", "MIN_GAP = C.HORIZON ", "MIN_GAP = C.HORIZON - 1 "),
    ("M3 bỏ lọc mù entry sau as-of", 'if e["as_of"] <= as_of]', "if True]"),
    ("M4 bỏ kiểm bar đúng as-of", 'if not bars or bars[-1]["time"] != as_of:', "if not bars:"),
    ("M5 bỏ kiểm ngày lạ", "    if bad_d:\n", "    if False:\n"),
    ("M6 bỏ từ cấm", "    m = DENY.search(body)", "    m = None"),
    ("M7 bỏ kiểm sha", 'meta.get("sha256") != sha or ', ""),
    ("M8 bỏ kiểm kỳ chưa đóng", "    if as_of > exp:", "    if False:"),
    ("M9 bỏ lọc định danh chỉ báo", "    t = _ID.sub(\" \", text)", "    t = text"),
    ("M11 bỏ dấu khi so số", "        if sign:\n", "        if False:\n"),
    ("M12 regex định danh rộng", '_ID = re.compile(r"\\bMA(?:20|50|200)\\b|\\bRSI\\(14\\)")',
     '_ID = re.compile(r"\\b(?:MA|SMA|EMA)\\s?\\d+\\b|\\bRSI\\s?\\(\\s?\\d+\\s?\\)")'),
    ("M13 bỏ chặn forecast lùi ngày", "        if late > LATE_MAX or fut:", "        if False:"),
    ("M14 gate bỏ kiểm nguyên văn", "return None if block in text else", "return None if True else"),
    ("M15 gate bỏ chặn gắn tên khi không PASS", "    if MARKER in text:", "    if False:"),
    ("M10 bỏ đối chiếu MA", "        if abs(ind[as_of][f\"MA{n}\"] / sma - 1) > MA_TOL:", "        if False:"),
]


def run_tz(bin_dir):
    rcs = []
    for label, extra, unset in (("TZ-unset", {}, True), ("TZ=America/New_York", {"TZ": "America/New_York"}, False),
                                ("TZ=UTC", {"TZ": "UTC"}, False)):
        env = dict(os.environ, LVB_SC_BIN=bin_dir, **extra)
        if unset:
            env.pop("TZ", None)
        r = subprocess.run([sys.executable, os.path.join(bin_dir, "livermore_report_block_selfcheck.py"), "--inner"],
                           capture_output=True, text=True, env=env, timeout=600)
        rcs.append((label, r.returncode, r.stdout))
    return rcs


def main():
    if "--inner" in sys.argv:
        return inner()
    bad = 0
    for label, rc, out in run_tz(HERE):
        print(f"── {label}: rc={rc} · {out.strip().splitlines()[-1] if out.strip() else ''}")
        if rc:
            print(out); bad += 1
    caught = 0
    for name, old, new in MUTANTS:
        top = tempfile.mkdtemp(prefix="lvb_mut_")
        d = os.path.join(top, "bin")                      # giữ bố cục <root>/bin: livermore_run.sh tìm $ROOT/bin/livermore_common.py
        os.makedirs(d)
        for f in ("livermore_common.py", "livermore_run.sh", "livermore_report_block.py", "livermore_report_block_selfcheck.py"):
            shutil.copy(os.path.join(HERE, f), d)
        p = os.path.join(d, "livermore_report_block.py")
        src = open(p).read()
        if src.count(old) != 1:
            print(f"  ⚠️ {name}: chuỗi mutant không khớp đúng 1 lần ({src.count(old)}) — selfcheck lỗi thời")
            bad += 1
            continue
        open(p, "w").write(src.replace(old, new))
        env = dict(os.environ, LVB_SC_BIN=d, PYTHONPATH=WC_ROOT)   # trading_bot.vn_market từ repo thật (chỉ đọc lịch)
        r = subprocess.run([sys.executable, os.path.join(d, "livermore_report_block_selfcheck.py"), "--inner"],
                           capture_output=True, text=True, env=env, timeout=600)
        first = next((ln.strip() for ln in r.stdout.splitlines() if "❌" in ln), "")
        killed = r.returncode != 0 and bool(first)          # crash KHÔNG tính là bắt — phải là assertion fail thật
        caught += killed
        if r.returncode != 0 and not first:
            print(f"  ⚠️ {name}: mutant CRASH (không phải assertion): {r.stderr.strip()[-300:]}")
        print(f"  {'🎯' if killed else '😱'} {name}: {'bị bắt' if killed else 'SỐNG SÓT'} {first[:110]}")
        shutil.rmtree(top, ignore_errors=True)
    print(f"\nmutant bị bắt {caught}/{len(MUTANTS)}")
    ok = bad == 0 and caught == len(MUTANTS)
    print("✅ SELFCHECK PASS" if ok else "❌ SELFCHECK FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
