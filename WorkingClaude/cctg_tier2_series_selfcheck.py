#!/usr/bin/env python3
"""Selfcheck cho append_cctg_rate.py --series tier2 (user duyệt 2026-10-13): CCTG của nhóm ngân
hàng ngay sau Big-4 (VPB/MB/TCB/ACB) — CHỈ THU THẬP + HIỂN THỊ.

Phần W (writer): file + sidecar riêng; khoá = (bank, denomination); mọi guard tính riêng từng khoá
(không suy số ngân hàng này từ ngân hàng khác); giữ đủ guard của 12m/6m; không rò sang 12m/6m.
Phần B (ranh giới cứng): effective_deposit_rate / macro_killswitch_a_status /
consumer_deposit_rate* / chuỗi của deposit_cctg_trend_check / dcf_valuation.discount_rate cho
kết quả giống hệt từng byte khi file tier2 VẮNG so với khi CÓ (kể cả dòng 9,2% và 15%), và không
lần nào mở/dò file đó; quét tĩnh: không consumer nào nhắc tới file hay import writer.
Chạy từ chính thư mục chứa file (tự định vị, chạy được trong worktree)."""
import ast
import builtins
import csv
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import append_cctg_rate as acr  # noqa: E402
import cctg_rate_vn as cctg  # noqa: E402
import deposit_rate_vn as dep  # noqa: E402
import deposit_cctg_trend_check as trend  # noqa: E402
import dcf_valuation as dcf  # noqa: E402
import pandas as pd  # noqa: E402

for _m in (acr, cctg, dep, trend, dcf):
    assert os.path.dirname(os.path.abspath(_m.__file__)) == HERE, f"nạp nhầm {_m.__name__} ngoài cây này"
_TODAY_D = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
TODAY = _TODAY_D.isoformat()
TOMORROW = (_TODAY_D + timedelta(days=1)).isoformat()
YESTERDAY = (_TODAY_D - timedelta(days=1)).isoformat()
EXPECTED_HEADER = ["effective_date", "bank", "product", "denomination", "holding_period", "cctg_rate",
                   "collected_date", "source", "note"]
FAILS = []
N = 0


def check(label, cond):
    global N
    N += 1
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


def run(argv, job_id=None):
    old_argv, old_job = sys.argv, os.environ.get("JOB_ID")
    sys.argv = ["append_cctg_rate.py"] + argv
    os.environ.pop("JOB_ID", None)
    if job_id:
        os.environ["JOB_ID"] = job_id
    try:
        return (acr.main() or 0), ""
    except SystemExit as e:
        return 1, str(e.code)
    finally:
        sys.argv = old_argv
        os.environ.pop("JOB_ID", None)
        if old_job is not None:
            os.environ["JOB_ID"] = old_job


def rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def raw(path):
    with open(path, "rb") as f:
        return f.read()


def src(pub, url, rate):
    return {"publisher": pub, "url": url, "date": TODAY, "rate": rate}


def t2(bank, rate, eff, denom=None, source="manual_verify", product="CCTG X", holding=None, extra=()):
    argv = ["--series", "tier2", "--rate", str(rate), "--effective", eff, "--source", source]
    if bank is not None:
        argv += ["--bank", bank]
    if product is not None:
        argv += ["--product", product]
    if denom is not None:
        argv += ["--denom", denom]
    if holding is not None:
        argv += ["--holding", holding]
    return argv + list(extra)


d = tempfile.mkdtemp(prefix="cctg_t2sc_")
csv12 = os.path.join(d, "cctg_rate_vn_events.csv")
csv6 = os.path.join(d, "cctg_rate_vn_6m_events.csv")
csvt = os.path.join(d, "cctg_rate_vn_tier2_events.csv")
csvdep = os.path.join(d, "deposit_rate_vn_events.csv")
SEED12 = "effective_date,cctg_rate,collected_date,source,note\n2026-10-05,7.4,2026-10-05,manual_verify,seed12\n"
with open(csv12, "w", encoding="utf-8") as f:
    f.write(SEED12)
with open(csvdep, "w", encoding="utf-8") as f:
    f.write("effective_date,deposit_rate,collected_date,source,note\n2026-09-04,6.8,2026-09-04,manual_verify,seed\n")
bytes12 = raw(csv12)
orig = (acr.CSV_PATH, acr.CSV_PATH_6M, getattr(acr, "CSV_PATH_TIER2", None), cctg._EVENTS_CSV, dep._EVENTS_CSV)
acr.CSV_PATH, acr.CSV_PATH_6M, acr.CSV_PATH_TIER2 = csv12, csv6, csvt
cctg._EVENTS_CSV, dep._EVENTS_CSV = csv12, csvdep
try:
    # ---------- W: writer ----------
    rc, msg = run(t2(None, 9.2, TODAY, "100tr"))
    check("W1 thiếu --bank bị chặn", rc == 1 and "--bank" in msg and not rows(csvt))
    rc, msg = run(t2("VCB", 9.2, TODAY, "100tr"))
    check("W2 --bank VCB (Big-4, ngoài nhóm tier2) bị chặn", rc == 1 and "--bank" in msg and not rows(csvt))
    rc, msg = run(t2("VPB", 9.2, TODAY, "50tr"))
    check("W3 --denom ngoài 10tr/100tr bị chặn", rc == 1 and "--denom" in msg and not rows(csvt))
    rc, msg = run(t2("VPB", 9.2, TODAY, "100tr", product=None))
    check("W4 thiếu --product bị chặn", rc == 1 and "--product" in msg and not rows(csvt))
    rc, msg = run(t2("VPB", 0, TODAY, "100tr"))
    check("W5 lợi suất 0 bị chặn (không điền 0 cho ngân hàng thiếu số)",
          rc == 1 and "out of sane range" in msg and not rows(csvt))

    rc, msg = run(t2("VPB", 9.2, TODAY, "100tr", product="CCTG Super Thịnh Vượng", extra=["--note", "ảnh app"]))
    rt = rows(csvt)
    check("W6 ghi tay VPB 100tr 9,2% -> đúng 1 dòng, đủ trường",
          rc == 0 and len(rt) == 1 and rt[0] == {
              "effective_date": TODAY, "bank": "VPB", "product": "CCTG Super Thịnh Vượng",
              "denomination": "100tr", "holding_period": "", "cctg_rate": "9.2",
              "collected_date": TODAY, "source": "manual_verify", "note": "ảnh app"})
    with open(csvt, newline="", encoding="utf-8") as f:
        check("W6b header file tier2 đúng 9 cột", next(csv.reader(f)) == EXPECTED_HEADER)
    check("W6c file 12M không đổi từng byte, file 6M không bị tạo",
          raw(csv12) == bytes12 and not os.path.exists(csv6))
    check("W6d ghi tay không tạo sidecar nào", not glob.glob(os.path.join(d, "*last_auto_sources*")))

    rc, msg = run(t2("VPB", 9.2, TODAY, "100tr"))
    check("W7 cùng (ngày, VPB, 100tr) chạy lại SKIP rc=0", rc == 0 and len(rows(csvt)) == 1)
    rc, msg = run(t2("VPB", 7.5, TODAY, "10tr", holding="184-389 ngày"))
    rt = rows(csvt)
    check("W8 VPB 10tr cùng ngày là khoá RIÊNG -> ghi thêm, giữ holding_period",
          rc == 0 and len(rt) == 2 and rt[1]["denomination"] == "10tr" and rt[1]["holding_period"] == "184-389 ngày")
    rc, msg = run(t2("MB", 7.1, TODAY))
    rt = rows(csvt)
    check("W9 MB 7,1% (lệch 2,1pp so với VPB) vẫn ghi — không so chéo ngân hàng; denomination để trống",
          rc == 0 and len(rt) == 3 and rt[2]["bank"] == "MB" and rt[2]["denomination"] == "")
    rc, msg = run(t2("VPB", 10.3, TOMORROW, "100tr"))
    check("W10 VPB 100tr lệch 1,1pp so với kỳ trước CÙNG khoá bị chặn",
          rc == 1 and "differs" in msg and len(rows(csvt)) == 3)
    rc, msg = run(t2("VPB", 9.2, YESTERDAY, "100tr"))
    check("W11 VPB 100tr ngày cũ hơn dòng cuối cùng khoá bị chặn",
          rc == 1 and "not newer" in msg and len(rows(csvt)) == 3)
    rc, msg = run(t2("ACB", 7.2, YESTERDAY, holding="3 tháng"))
    check("W11b ACB ngày hôm qua vẫn ghi (ngày mới-hơn tính riêng từng khoá)", rc == 0 and len(rows(csvt)) == 4)
    check("W12 thứ tự dòng = thứ tự ghi (append-only, không xáo)",
          [(r["bank"], r["denomination"]) for r in rows(csvt)] == [("VPB", "100tr"), ("VPB", "10tr"), ("MB", ""), ("ACB", "")])

    rc, msg = run(t2("TCB", 8.0, TODAY), job_id="selfcheck_job")
    check("W13 JOB_ID + manual_verify bị từ chối", rc == 1 and "manual_verify" in msg and len(rows(csvt)) == 4)
    rc, msg = run(t2("TCB", 8.0, TODAY, source="web_crosscheck_auto", extra=["--note", "x", "--force"]),
                  job_id="selfcheck_job")
    check("W13b JOB_ID + --force bị từ chối", rc == 1 and "--force is refused" in msg)

    def auto(bank, rate, eff, sources, denom=None):
        return run(t2(bank, rate, eff, denom, source="web_crosscheck_auto",
                      extra=["--collected", TODAY, "--note", "x", "--sources", json.dumps(sources)]),
                   job_id="selfcheck_job")

    rc, msg = auto("TCB", 8.0, TODAY, [src("CafeF", "https://cafef.vn/a", 8.0), src("Kenh14", "https://kenh14.vn/b", 8.0)])
    check("W14 2 nguồn cùng chủ bị chặn", rc == 1 and "distinct owner" in msg and len(rows(csvt)) == 4)
    rc, msg = auto("TCB", 8.0, TODAY, [src("VietnamNet", "https://vietnamnet.vn/a", 8.0), src("Nghe An", "https://baonghean.vn/b", 8.2)])
    check("W14b 2 nguồn lệch 0,2pp bị chặn", rc == 1 and "disagree" in msg and len(rows(csvt)) == 4)
    rc, msg = auto("TCB", 8.1, TODAY, [src("VietnamNet", "https://vietnamnet.vn/a", 8.0), src("Nghe An", "https://baonghean.vn/b", 8.0)])
    check("W14c --rate không nguồn nào nói bị chặn", rc == 1 and "does not match" in msg and len(rows(csvt)) == 4)
    good = [src("VietnamNet", "https://vietnamnet.vn/t2", 8.0), src("Nghe An", "https://baonghean.vn/t2", 8.0)]
    rc, msg = auto("TCB", 8.0, TODAY, good)
    check("W15 auto hợp lệ TCB ghi được", rc == 0 and len(rows(csvt)) == 5)
    check("W15b sidecar RIÊNG theo khoá (TCB, n/a); không tạo sidecar 12M/6M",
          sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*last_auto_sources*")))
          == ["cctg_tier2_TCB_na_last_auto_sources.json"])
    good_acb = [dict(s, rate=7.2) for s in good]
    rc, msg = auto("ACB", 7.2, TODAY, good_acb)
    check("W16 cùng bài báo dùng cho ngân hàng KHÁC vẫn ghi (1 bài phủ nhiều ngân hàng)",
          rc == 0 and len(rows(csvt)) == 6)
    rc, msg = auto("TCB", 8.0, TOMORROW, good)
    check("W16b cùng URL dùng lại cho CÙNG khoá kỳ sau bị chặn",
          rc == 1 and "already used" in msg and len(rows(csvt)) == 6)

    rc, msg = auto("TCB", 9.1, TOMORROW, [src("VnExpress", "https://vnexpress.net/t2b", 9.1),
                                         src("Dan Tri", "https://dantri.com.vn/t2b", 9.1)])
    check("W16c khoá chỉ có dòng auto (TCB): kỳ sau lệch 1,1pp vẫn bị chặn",
          rc == 1 and "differs" in msg and len(rows(csvt)) == 6)

    bytes_t = raw(csvt)
    rc, msg = run(["--rate", "7.4", "--effective", TODAY, "--source", "manual_verify"])
    check("W17 lượt 12m mặc định SAU lượt tier2 ghi vào file 12M, không đụng file tier2",
          rc == 0 and len(rows(csv12)) == 2 and raw(csvt) == bytes_t)
    b12 = raw(csv12)
    rc, msg = run(["--rate", "7.4", "--effective", TOMORROW, "--source", "manual_verify", "--bank", "VPB"])
    rc6, msg6 = run(["--series", "6m", "--rate", "7.5", "--effective", TODAY, "--source", "manual_verify",
                     "--denom", "100tr"])
    check("W18 --bank/--denom với chuỗi 12m/6m bị từ chối, không ghi",
          rc == 1 and "tier2" in msg and rc6 == 1 and "tier2" in msg6
          and raw(csv12) == b12 and not os.path.exists(csv6))
    rc, msg = run(t2("VPB", 9.1, TODAY, "100tr", extra=["--force"]))
    rt = rows(csvt)
    check("W19 --force (người) đính chính đúng 1 dòng của đúng khoá, các khoá khác nguyên vẹn",
          rc == 0 and len(rt) == 6
          and [r["cctg_rate"] for r in rt if (r["bank"], r["denomination"]) == ("VPB", "100tr")] == ["9.1"]
          and sorted((r["bank"], r["denomination"], r["cctg_rate"]) for r in rt if r["bank"] != "VPB" or r["denomination"] != "100tr")
          == sorted([("VPB", "10tr", "7.5"), ("MB", "", "7.1"), ("ACB", "", "7.2"), ("ACB", "", "7.2"), ("TCB", "", "8")]))

    # ---------- B: ranh giới cứng ----------
    with open(csv12, "w", encoding="utf-8") as f:
        f.write(SEED12)
    cctg._EVENTS_CSV = csv12  # lượt 12m ở W17 reload cctg_rate_vn -> đường dẫn về mặc định; gắn lại fixture
    ASOFS = [None, "2025-06-30", "2026-09-30", "2026-10-13", "2026-12-15"]
    touched = []

    def _note(p):
        try:
            s = os.fspath(p)
        except TypeError:
            return
        if isinstance(s, bytes):
            s = s.decode("utf-8", "replace")
        if "tier2" in os.path.basename(s) or os.path.abspath(s) == d:  # mở file tier2, hoặc liệt kê thư mục chứa nó
            touched.append(s)

    def snapshot():
        """Mọi đầu ra consumer-facing, dưới bẫy ghi lại mọi lần mở/dò/liệt kê đường dẫn tier2."""
        real = (builtins.open, os.path.exists, os.path.isfile, os.stat, os.listdir, os.scandir,
                glob.glob, pd.read_csv)

        def wrap(fn):
            def inner(p=".", *a, **k):
                _note(p)
                return fn(p, *a, **k)
            return inner
        (builtins.open, os.path.exists, os.path.isfile, os.stat, os.listdir, os.scandir,
         glob.glob, pd.read_csv) = [wrap(f) for f in real]
        try:
            out = []
            for a in ASOFS:
                for fn in (dep.current_deposit_rate, dep.effective_deposit_rate, dep.macro_killswitch_a_status,
                           dep.consumer_deposit_rate_detail, dep.consumer_deposit_rate, cctg.current_cctg_rate):
                    out.append((fn.__name__, a, repr(fn(a))))
                if a is not None:
                    dcf._RATE_CACHE.clear()
                    out.append(("dcf.discount_rate", a, repr(dcf.discount_rate(a))))
            out.append(("deposit_events_df", dep.deposit_events_df().to_csv()))
            out.append(("effective_deposit_events_df", dep.effective_deposit_events_df().to_csv()))
            out.append(("cctg_events_df", cctg.cctg_events_df().to_csv()))
            series = trend._load_series()
            out.append(("trend._load_series", repr(series)))
            out.append(("trend.heartbeat", repr(trend._heartbeat_lines(series, date(2026, 10, 13)))))
            out.append(("trend.declines", repr(trend.check_declines(series, {}))))
            out.append(("trend.staleness", repr(trend.check_staleness(series, {}, date(2026, 10, 13)))))
            return out
        finally:
            (builtins.open, os.path.exists, os.path.isfile, os.stat, os.listdir, os.scandir,
             glob.glob, pd.read_csv) = real

    os.remove(csvt)
    for p in glob.glob(os.path.join(d, "cctg_tier2_*")):
        os.remove(p)
    snap_absent = snapshot()
    touched_absent = list(touched)
    rc1, _ = run(t2("VPB", 9.2, TODAY, "100tr", product="CCTG Super Thịnh Vượng"))
    rc2, _ = run(t2("MB", 15.0, TODAY))  # vượt xa ngưỡng kill-switch A 7,5% — ai đọc nhầm là lộ ngay
    check("B0 dựng file tier2 có dòng 9,2% và 15% cạnh các file chuỗi production",
          rc1 == 0 and rc2 == 0 and [r["cctg_rate"] for r in rows(csvt)] == ["9.2", "15"]
          and os.path.dirname(csvt) == os.path.dirname(cctg._EVENTS_CSV) == os.path.dirname(dep._EVENTS_CSV))
    del touched[:]
    snap_present = snapshot()
    h = lambda s: hashlib.sha256(repr(s).encode("utf-8")).hexdigest()  # noqa: E731
    check(f"B1 {len(snap_absent)} đầu ra (effective/kill-switch A/consumer*/DCF r/trend) giống hệt từng byte "
          f"vắng vs có file tier2 [sha256 {h(snap_absent)[:12]}]",
          len(snap_absent) >= 40 and h(snap_absent) == h(snap_present))
    for name in ("effective_deposit_rate", "macro_killswitch_a_status", "consumer_deposit_rate_detail",
                 "consumer_deposit_rate", "dcf.discount_rate", "trend._load_series"):
        a_ = [x for x in snap_absent if x[0] == name]
        b_ = [x for x in snap_present if x[0] == name]
        check(f"B1 {name}: {len(a_)} giá trị, vắng == có", bool(a_) and a_ == b_)
    check(f"B2 không consumer nào mở/dò file tier2 hay liệt kê thư mục chứa nó (cả 2 lượt; thấy: {touched_absent + touched})",
          touched_absent == [] and touched == [])
    check("B2b chuỗi trend check chỉ gồm đúng 2 khoá Big-4, không có 9,2/15",
          set(trend._load_series()) == {"big4_12m", "cctg_6m"} and set(trend.SERIES) == {"big4_12m", "cctg_6m"}
          and not any(r in (9.2, 15.0) for pts in trend._load_series().values() for _, r in pts))
    eff13, ks13 = dep.effective_deposit_rate("2026-10-13"), dep.macro_killswitch_a_status("2026-10-13")
    check(f"B2c 13/10 có file tier2 15%: effective = {eff13['rate_pct']}% (nguồn {eff13['rate_source']}), "
          f"kill-switch A armed={ks13['armed']}",
          eff13["rate_pct"] <= 7.5 and "tier2" not in eff13["rate_source"] and ks13["armed"] is False)
    # đối chứng dương: bẫy phải bắt được một lần đọc thật (không thì B2 là rỗng nghĩa)
    del touched[:]
    real_open, real_exists = builtins.open, os.path.exists
    builtins.open = lambda p, *a, **k: (_note(p), real_open(p, *a, **k))[1]
    os.path.exists = lambda p: (_note(p), real_exists(p))[1]
    try:
        acr._read_rows(csvt)
    finally:
        builtins.open, os.path.exists = real_open, real_exists
    check("B3 đối chứng dương: bẫy ghi nhận được lần đọc file tier2 của chính writer", len(touched) >= 2)

    # ---------- S: quét tĩnh ----------
    TOKEN = re.compile(r"tier2_events|CSV_PATH_TIER2|cctg_tier2|series[ =\"',]+tier2", re.I)
    ALLOWED = {"append_cctg_rate.py", "cctg_tier2_series_selfcheck.py", "refresh_deposit_cctg_weekly.sh"}
    CONSUMERS = ["deposit_rate_vn.py", "cctg_rate_vn.py", "deposit_cctg_trend_check.py", "rating_8l.py",
                 "dcf_valuation.py", "dcf_refresh_gate.py", "custom30_yield_labels.py", "value_radar.py",
                 "dna_report.py", "trading_bot/due_diligence.py",
                 "deploy_golive_dt5g_v4/golive_recommend_v23.py"]
    files = []
    for pat in ("*.py", "*.sh", "trading_bot/**/*.py", "deploy_golive_dt5g_v4/**/*.py", "mike/bin/*"):
        files += [p for p in glob.glob(os.path.join(HERE, pat), recursive=True) if os.path.isfile(p)]
    offenders, importers = [], []
    for p in sorted(set(files)):
        rel = os.path.relpath(p, HERE)
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        if TOKEN.search(text) and rel not in ALLOWED:
            offenders.append(rel)
        if rel.endswith(".py") and "append_cctg_rate" in text and rel != "append_cctg_rate.py":
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                         else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                if any(n.split(".")[0] == "append_cctg_rate" for n in names):
                    importers.append(rel)
    check(f"S1 quét {len(set(files))} file: chỉ writer/selfcheck/wrapper tuần nhắc tới chuỗi tier2 (vi phạm: {offenders})",
          len(set(files)) > 50 and offenders == [])
    missing = [c for c in CONSUMERS if not os.path.isfile(os.path.join(HERE, c))]
    check(f"S2 đủ {len(CONSUMERS)} file consumer được nêu tên nằm trong phạm vi quét (thiếu: {missing})", missing == [])
    check(f"S3 chỉ selfcheck mới import writer append_cctg_rate (import: {sorted(set(importers))})",
          all(os.path.basename(r).endswith("_selfcheck.py") for r in importers)
          and not set(importers) & set(CONSUMERS))
    globby = [c for c in CONSUMERS if os.path.isfile(os.path.join(HERE, c))
              and re.search(r"cctg_rate_vn[^\"'\n]*\*", open(os.path.join(HERE, c), encoding="utf-8").read())]
    check(f"S4 không consumer nào glob 'cctg_rate_vn*' (vi phạm: {globby})", globby == [])
    with open(os.path.join(HERE, "refresh_deposit_cctg_weekly.sh"), encoding="utf-8") as f:
        sh = f.read()
    check("S5 wrapper tuần có lệnh --series tier2 với đủ --bank/--product/--denom/--holding và series=cctg_tier2",
          all(t in sh for t in ("--series tier2 --bank", "--product", "--denom", "--holding",
                                "sbv_policy / cctg_tier2")))
    check("S5b wrapper tuần nêu đủ 4 ngân hàng và luật không-điền-0 / không-suy-từ-ngân-hàng-khác",
          all(t in sh for t in ("VPB", "MB", "TCB", "ACB", "KHÔNG điền 0", "KHÔNG suy")))
    check("S5c wrapper tuần chỉ gọi trend check đúng như cũ (không truyền tham số tier2)",
          re.findall(r"deposit_cctg_trend_check\.py[^\n]*", sh).count('deposit_cctg_trend_check.py >> "$LOG" 2>&1') == 1
          and not re.search(r"deposit_cctg_trend_check\.py[^\n]*tier2", sh))
finally:
    acr.CSV_PATH, acr.CSV_PATH_6M, acr.CSV_PATH_TIER2, cctg._EVENTS_CSV, dep._EVENTS_CSV = orig
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{N - len(FAILS)}/{N} PASS")
sys.exit(1 if FAILS else 0)
