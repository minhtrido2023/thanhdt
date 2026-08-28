# -*- coding: utf-8 -*-
"""freshness_warn_selfcheck.py — kiểm 3 fix "cron freshness WARN" (job Winston_20260731_062642).

Audit §14 tìm 3 cặp cron producer→consumer mà consumer KHÔNG biết input có được ghi HÔM NAY
không (chỉ đọc nội dung file/bảng, file đứng im 1 tuần đọc y hệt file mới):
  A. ops_health_check 08:20 → anomaly_flags.json → golive_recommend_v23 19:00
  B. daily_refresh 18:30 → dt5g_live/golive_state_today.json → rating_8l / eod_report 19:10
  C. pt_8l_daily 19:20 → data/rating_8l.csv → telegram_run_daily 19:35

Nguyên tắc kiểm CHUNG cho cả 3 (phải test CẢ HAI CHIỀU, không chỉ chiều bắt lỗi):
  (1) input CŨ  ⇒ cảnh báo XUẤT HIỆN;
  (2) input HÔM NAY ⇒ TUYỆT ĐỐI KHÔNG có cảnh báo giả (WARN kêu oan mỗi ngày = bị bỏ qua,
      tệ hơn không có WARN);
  (3) hành vi cũ KHÔNG đổi (fail-open, gate loại trừ y nguyên) — job này chỉ THÊM visibility;
  (4) mọi so sánh ngày phải ra CÙNG kết quả dưới mọi TZ hệ thống. Chạy lại chính file này
      dưới `env -u TZ` / TZ=UTC / TZ=America/New_York và so kết quả — bài học
      dt5g_writer_watch.py (2026-07-31) là bug TZ latent vì mọi caller đều tình cờ có TZ=ICT.

Chạy:  python3 mike/agents/Winston/freshness_warn_selfcheck.py          # 1 lượt, TZ hiện tại
       python3 mike/agents/Winston/freshness_warn_selfcheck.py --tz-matrix   # tự chạy lại 3 TZ
Không đụng file production nào: mọi test ghi vào tempdir, đọc file thật chỉ để READ.
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

W = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
sys.path.insert(0, os.path.join(W, "mike", "agents", "Taylor"))

ICT = datetime.timezone(datetime.timedelta(hours=7))
ok = fail = 0


def chk(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1; print(f"  PASS  {name} {extra}")
    else:
        fail += 1; print(f"  FAIL  {name} {extra}")


def _utc_stamp(dt):
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ══════════════════════════════════════════════════════════════════════════════════════
print("== A. anomaly_flags.json — độ tươi CỦA FILE (khác TTL 30d của từng cờ) ==")
import anomaly_gate
from anomaly_gate import anomaly_excluded, anomaly_flags_freshness

REF = datetime.date(2026, 7, 31)          # ngày tham chiếu CỐ ĐỊNH → test không đổi theo hôm chạy
_real_wd = anomaly_gate.WORKDIR
try:
    d = tempfile.mkdtemp(); os.makedirs(os.path.join(d, "data"))
    anomaly_gate.WORKDIR = d
    fp = os.path.join(d, "data", "anomaly_flags.json")

    chk("A1 file THIẾU → is_stale", anomaly_flags_freshness(REF)["is_stale"])
    open(fp, "w").write("{ khong-phai-json")
    chk("A2 file HỎNG → is_stale", anomaly_flags_freshness(REF)["is_stale"])

    # file kiểu CŨ (anomaly_scan trước patch): có cờ, KHÔNG có _meta ⇒ đúng ca của audit §14
    legacy = {"PNJ": {"last_alert": "2026-07-24", "tier": "W", "reasons": "FLOOR2"}}
    json.dump(legacy, open(fp, "w"))
    r = anomaly_flags_freshness(REF)
    chk("A3 thiếu _meta.generated_at → is_stale + nêu lý do", r["is_stale"] and "generated_at" in r["reason"])
    chk("A3b gate loại trừ KHÔNG đổi khi thiếu _meta (fail-open y như cũ)",
        anomaly_excluded("2026-07-25") == {"PNJ"})

    # scan chết im lặng 6 ngày: nội dung cờ vẫn "hợp lệ" theo TTL, chỉ _meta tố cáo
    stale = dict(legacy, _meta={"generated_at": "2026-07-25T01:20:00Z", "scan_asof": "2026-07-24"})
    json.dump(stale, open(fp, "w"))
    r = anomaly_flags_freshness(REF)
    chk("A4 _meta cũ 6 ngày → is_stale", r["is_stale"], f"({r['reason']})")
    chk("A4b nhưng cờ PNJ VẪN active theo TTL 30d — TTL không bị đụng",
        "PNJ" in anomaly_excluded("2026-07-25"))

    # ── ranh giới ICT: 2026-07-30T18:00Z = 2026-07-31 01:00 ICT ⇒ ĐÃ là 'hôm nay' theo VN
    json.dump(dict(legacy, _meta={"generated_at": "2026-07-30T18:00:00Z"}), open(fp, "w"))
    chk("A5 ranh giới ICT: 07-30T18:00Z (=07-31 01:00 ICT) → TƯƠI",
        not anomaly_flags_freshness(REF)["is_stale"])
    # 2026-07-30T16:59Z = 23:59 ICT ngày 07-30 ⇒ vẫn là HÔM QUA
    json.dump(dict(legacy, _meta={"generated_at": "2026-07-30T16:59:00Z"}), open(fp, "w"))
    chk("A6 ranh giới ICT: 07-30T16:59Z (=23:59 ICT 07-30) → CŨ",
        anomaly_flags_freshness(REF)["is_stale"])

    # ── ca bình thường: scan chạy 08:20 ICT hôm nay ⇒ KHÔNG được có cảnh báo giả
    json.dump(dict(legacy, _meta={"generated_at": "2026-07-31T01:20:00Z"}), open(fp, "w"))
    r = anomaly_flags_freshness(REF)
    chk("A7 scan 08:20 ICT hôm nay → KHÔNG cảnh báo (chống WARN giả)", not r["is_stale"], f"({r})")

    # ── writer thật (anomaly_scan.write_flags) phải đóng dấu _meta mà gate đọc được
    import anomaly_scan
    _real_fp = anomaly_scan.FLAGS_PATH
    try:
        anomaly_scan.FLAGS_PATH = fp
        json.dump(legacy, open(fp, "w"))                     # file cũ có sẵn cờ PNJ
        empty = pd.DataFrame(columns=["ticker", "time", "tier", "reasons", "ret", "idio", "vol_x"])
        anomaly_scan.write_flags(empty, scan_asof=datetime.date(2026, 7, 30))
        got = json.load(open(fp, encoding="utf-8"))
        chk("A8 write_flags đóng dấu _meta.generated_at", bool(got.get("_meta", {}).get("generated_at")))
        chk("A8b ngày SẠCH (0 alert) vẫn đóng dấu → không sinh WARN giả",
            not anomaly_flags_freshness()["is_stale"], f"({got['_meta']})")
        chk("A8c merge KHÔNG mất cờ cũ", got.get("PNJ", {}).get("last_alert") == "2026-07-24")
        chk("A8d _meta KHÔNG lọt vào set loại trừ (không có mã ảo '_meta')",
            anomaly_excluded("2026-07-25") == {"PNJ"})
    finally:
        anomaly_scan.FLAGS_PATH = _real_fp
finally:
    anomaly_gate.WORKDIR = _real_wd

# ── nhánh STALE trong golive_recommend_v23.py: chạy THẬT khối lệnh đó (trích nguyên văn từ
# file production, KHÔNG chép lại logic — chép lại thì test xanh trong khi production hỏng).
# Chạy full script cần BQ vài phút và ghi đè artifact ngày hôm nay, nên chỉ exec 2 khối.
GOLIVE = os.path.join(W, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
src = open(GOLIVE, encoding="utf-8").read()
M1 = "# ── độ tươi CỦA FILE cờ due-diligence"
blk_warn = src[src.index(M1):src.index("# ── 1. signals with state5")]
blk_rep = src[src.index('L.append(f"# V2.3 + DT5G'):src.index('L.append("## Regime, allocator & parking')]
chk("A9 khối cảnh báo còn nguyên trong production (2 điểm: log + bus)",
    "anomaly_flags.json KHÔNG tươi" in blk_warn and "append_event.sh" in blk_warn)

d2 = tempfile.mkdtemp()          # WORKDIR giả ⇒ append_event.sh KHÔNG tồn tại
stale_fresh = {"is_stale": True, "generated_at": "2026-07-25T01:20:00Z",
               "reason": "lần ghi cuối 2026-07-25 (ICT) ≠ ngày giao dịch 2026-07-31"}
ns = {"os": os, "json": json, "WORKDIR": d2, "END": "2026-07-31",
      "_anomaly_flags_freshness": lambda: stale_fresh, "print": print}
exec(blk_warn, ns)
chk("A10 bus lỗi/không gọi được KHÔNG làm chết luồng lập plan (fail-open)",
    ns["anomaly_fresh"]["is_stale"] is True)
chk("A10b đường dẫn append_event.sh thật có tồn tại (WORKDIR thật)",
    os.path.exists(os.path.join(W, "mike", "bin", "append_event.sh")))

ns2 = {"L": [], "datetime": datetime.datetime, "END": "2026-07-31", "anomaly_fresh": stale_fresh}
exec(blk_rep, ns2)
warn_lines = [x for x in ns2["L"] if "KHÔNG tươi" in x]
chk("A11 báo cáo DollarBill/user đọc CÓ dòng cảnh báo, nằm TRƯỚC mục Regime",
    len(warn_lines) == 1 and "2026-07-25" in warn_lines[0] and ns2["L"].index(warn_lines[0]) <= 2,
    f"({warn_lines[0][:80] if warn_lines else 'THIẾU'}…)")
ns3 = {"L": [], "datetime": datetime.datetime, "END": "2026-07-31",
       "anomaly_fresh": {"is_stale": False, "generated_at": "x", "reason": ""}}
exec(blk_rep, ns3)
chk("A11b file tươi → báo cáo KHÔNG có dòng cảnh báo giả",
    not any("KHÔNG tươi" in x for x in ns3["L"]))

# file THẬT đang chạy production: chỉ đọc, không ghi
real = anomaly_flags_freshness()
print(f"  [thật] anomaly_flags.json: is_stale={real['is_stale']} generated_at={real['generated_at']} {real['reason']}")

# ══════════════════════════════════════════════════════════════════════════════════════
print("== B. DT5G — bằng chứng publisher CỦA TA (golive_state_today.json) ==")
from dt5g_freshness import dt5g_publisher_evidence, dt5g_warn_line

d = tempfile.mkdtemp()
sj = os.path.join(d, "golive_state_today.json")
TODAY_TRADING = datetime.date(2026, 7, 31)     # thứ SÁU, phiên giao dịch
PREV_TRADING = datetime.date(2026, 7, 30)
SUNDAY = datetime.date(2026, 8, 2)             # ngày KHÔNG giao dịch


def _write(as_of, ok_flag=True, mtime=None):
    json.dump({"as_of": str(as_of), "bq_publish_ok": ok_flag,
               "published_at": f"{as_of}T11:35:00Z"}, open(sj, "w"))
    if mtime is not None:
        t = datetime.datetime.combine(mtime, datetime.time(19, 0), tzinfo=ICT).timestamp()
        os.utime(sj, (t, t))


chk("B1 file THIẾU → is_stale", dt5g_publisher_evidence(TODAY_TRADING, sj)["is_stale"])
_write(PREV_TRADING, True, PREV_TRADING)
r = dt5g_publisher_evidence(TODAY_TRADING, sj)
chk("B2 publisher chưa chạy hôm nay (as_of=T-1) → is_stale", r["is_stale"], f"({r['reason']})")
chk("B2b dòng cảnh báo có nội dung đọc được", "DT5G" in dt5g_warn_line(TODAY_TRADING, sj))
_write(TODAY_TRADING, False, TODAY_TRADING)
r = dt5g_publisher_evidence(TODAY_TRADING, sj)
chk("B3 as_of đúng nhưng bq_publish_ok=false → is_stale", r["is_stale"], f"({r['reason']})")
# ca HIỂM: kaffa_v2 đẩy MAX(time)=hôm nay lúc 17:12 nên bảng BQ "trông tươi", nhưng
# publisher của ta chết ⇒ file bằng chứng còn nguyên nội dung + mtime hôm qua.
_write(TODAY_TRADING, True, PREV_TRADING)
r = dt5g_publisher_evidence(TODAY_TRADING, sj)
chk("B4 as_of=hôm nay nhưng mtime=hôm qua (chain ta chết, kaffa che bảng) → is_stale",
    r["is_stale"], f"({r['reason']})")
_write(TODAY_TRADING, True, TODAY_TRADING)
r = dt5g_publisher_evidence(TODAY_TRADING, sj)
chk("B5 publisher chạy xong hôm nay → KHÔNG cảnh báo", not r["is_stale"], f"({r})")
chk("B5b warn_line rỗng khi tươi", dt5g_warn_line(TODAY_TRADING, sj) == "")
# CN/lễ: cron 19:10/19:35 vẫn chạy T2-T6, nhưng ngày nghỉ thì as_of=phiên gần nhất là ĐÚNG
_write(TODAY_TRADING, True, TODAY_TRADING)
r = dt5g_publisher_evidence(SUNDAY, sj)
chk("B6 ngày KHÔNG giao dịch: as_of=phiên gần nhất, bỏ điều kiện mtime → KHÔNG báo oan",
    not r["is_stale"], f"(ltd={r['last_trading_day']})")
chk("B6b nhận diện đúng phiên gần nhất của CN 08-02 là T6 07-31",
    r["last_trading_day"] == "2026-07-31" and r["is_trading_today"] is False)
_write(PREV_TRADING, True, TODAY_TRADING)
chk("B7 ngày nghỉ mà as_of vẫn tụt 1 phiên → VẪN báo", dt5g_publisher_evidence(SUNDAY, sj)["is_stale"])
chk("B8 file HỎNG → is_stale, KHÔNG raise (báo cáo không được chết)",
    (open(sj, "w").write("{ hong") or True) and dt5g_publisher_evidence(TODAY_TRADING, sj)["is_stale"])

# artifact THẬT: chỉ đọc
rb = dt5g_publisher_evidence()
print(f"  [thật] golive_state_today.json: is_stale={rb['is_stale']} as_of={rb['as_of']} "
      f"ok={rb['bq_publish_ok']} mtime={rb['mtime_date']} ltd={rb['last_trading_day']} {rb['reason']}")

# ══════════════════════════════════════════════════════════════════════════════════════
print("== B-wiring. 2 consumer 19:10 / 19:20 thật sự CHÈN được cảnh báo ==")
# Chạy NGUYÊN VĂN script production trong cây thư mục giả + stub (notify/nav/append_event):
# test "code có chèn đúng không", KHÔNG gửi Discord/Telegram thật, KHÔNG chạm BQ.
EOD = os.path.join(W, "mike", "bin", "eod_trading_report.sh")
STUB_WARN = "⚠️ Trạng thái DT5G có thể là dữ liệu HÔM QUA (stub) — xem lại trước khi dùng."


def _fake_tree(warn_on):
    """Cây giả: <root>/mike/bin/<script + stub>, <root>/dt5g_freshness.py in warn hoặc im."""
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "mike", "bin")); os.makedirs(os.path.join(root, "data", "trade_plans"))
    open(os.path.join(root, "dt5g_freshness.py"), "w").write(
        f"print({STUB_WARN!r})\n" if warn_on else "pass\n")
    dst = os.path.join(root, "mike", "bin", "eod_trading_report.sh")
    open(dst, "w").write(open(EOD, encoding="utf-8").read())
    for stub, body in (("notify_thread.sh", '#!/bin/bash\ncat > "$(dirname "$0")/../../sent.txt" <<< "$1"\n'),
                       ("notify.sh", "#!/bin/bash\nexit 0\n"),
                       ("append_event.sh", "#!/bin/bash\nexit 0\n"),
                       ("daily_nav_snapshot.py", "print('NAV: 1.000.000.000đ (stub)')\n"),
                       # Từ §6.6 (2026-08) eod_trading_report.sh KHÔNG gọi notify_thread.sh nữa —
                       # nó giao artifact cho report_delivery_gate.py. Thiếu stub này thì script
                       # thoát rc=1 "DELIVERY INCOMPLETE", sent.txt không bao giờ ra đời và B9/B9b/
                       # B9c/B10 đọc chuỗi RỖNG ⇒ 4 FAIL GIẢ (weekly audit 2026-08-29). Stub ghi
                       # lại chính artifact được giao để 4 assertion vẫn soi đúng nội dung gửi đi.
                       ("report_delivery_gate.py",
                        "import sys\n"
                        "a=[x for x in sys.argv[1:] if not x.startswith('--')]\n"
                        "open(sys.path[0]+'/../../sent.txt','w').write("
                        "open(a[0],encoding='utf-8').read()) if a else None\n")):
        f = os.path.join(root, "mike", "bin", stub); open(f, "w").write(body); os.chmod(f, 0o755)
    json.dump({"orders": []}, open(os.path.join(root, "data", "trade_plans",
                                                "plan_SpaceX_2026-07-31.json"), "w"))
    return root, dst


for warn_on, label in ((True, "STALE"), (False, "TƯƠI")):
    root, dst = _fake_tree(warn_on)
    p = subprocess.run(["bash", dst, "--account", "SpaceX", "--date", "2026-07-31"],
                       capture_output=True, text=True, cwd=root)
    body = open(os.path.join(root, "sent.txt"), encoding="utf-8").read() if \
        os.path.exists(os.path.join(root, "sent.txt")) else ""
    if warn_on:
        first = body.strip().splitlines()[0] if body.strip() else ""
        chk("B9 eod_trading_report: cảnh báo là DÒNG ĐẦU tin nhắn gửi đi",
            first.startswith("⚠️") and "HÔM QUA" in first, f"({first[:60]}…)")
        chk("B9b có dòng TRỐNG ngăn cách, không dính tiêu đề (bẫy $() nuốt newline)",
            "\n\n📊 **EOD Trading Report" in body)
        chk("B9c phần báo cáo cũ VẪN nguyên vẹn (chỉ THÊM, không thay)",
            "HOLD" in body and "NAV" in body and p.returncode == 0)
    else:
        chk("B10 DT5G tươi → KHÔNG có cảnh báo giả, tin nhắn bắt đầu bằng tiêu đề",
            body.strip().startswith("📊 **EOD Trading Report") and "⚠️" not in body,
            f"({body.strip()[:50]}…)")

# pt_8l_daily.sh: trích NGUYÊN VĂN khối [0-fresh] rồi chạy với stub notify (cả chain cần BQ,
# không chạy được ở đây — nhưng khối cần kiểm chỉ là khối này).
PT = open(os.path.join(W, "pt_8l_daily.sh"), encoding="utf-8").read()
blk = PT[PT.index("# --- Độ tươi DT5G"):PT.index('run "[1] rating_8l"')]
d = tempfile.mkdtemp()
open(os.path.join(d, "notify_stub.sh"), "w").write('#!/bin/bash\necho "$1" >> "$(dirname "$0")/sent.txt"\n')
os.chmod(os.path.join(d, "notify_stub.sh"), 0o755)
for warn_on in (True, False):
    open(os.path.join(d, "py_stub.sh"), "w").write(
        f'#!/bin/bash\n{"echo " + repr(STUB_WARN) if warn_on else "true"}\n')
    os.chmod(os.path.join(d, "py_stub.sh"), 0o755)
    if os.path.exists(os.path.join(d, "sent.txt")):
        os.remove(os.path.join(d, "sent.txt"))
    p = subprocess.run(["bash", "-c", f'PY={d}/py_stub.sh\n' + blk], capture_output=True, text=True,
                       env=dict(os.environ, NOTIFY_BIN=f"{d}/notify_stub.sh",
                                NOTIFY_THREAD_BIN=f"{d}/notify_stub.sh"))
    sent = open(os.path.join(d, "sent.txt"), encoding="utf-8").read() if \
        os.path.exists(os.path.join(d, "sent.txt")) else ""
    if warn_on:
        chk("B11 pt_8l_daily: DT5G cũ → log [0-fresh] STALE + alert Telegram/Discord",
            "[0-fresh] DT5G STALE" in p.stdout and "pt_8l_daily" in sent and "HÔM QUA" in sent)
    else:
        chk("B12 pt_8l_daily: DT5G tươi → log 1 dòng heartbeat, KHÔNG alert",
            "[0-fresh] DT5G tươi" in p.stdout and sent == "", f"(sent={sent!r})")

# rating_8l.py: cờ mặc định TẮT (không phá >20 caller) và bật đúng khi stale
import importlib
r8 = importlib.import_module("rating_8l")
chk("B13 rating_8l.DT5G_STALE mặc định False — caller cũ không thấy gì mới",
    r8.DT5G_STALE is False and hasattr(r8, "dt5g_state_today"))
importlib.reload(r8)
_flag = r8.dt5g_freshness_flag(quiet=True)
chk("B13b dt5g_freshness_flag() đặt cờ khớp bằng chứng thật (không chạm BQ)",
    _flag == r8.DT5G_STALE == dt5g_publisher_evidence()["is_stale"],
    f"(stale={_flag} reason={r8.DT5G_STALE_REASON})")

# ══════════════════════════════════════════════════════════════════════════════════════
print("== C. rating_8l.csv — file có được ghi hôm nay không (telegram_run_daily 19:35) ==")
CHECKER = os.path.join(W, "mike", "bin", "csv_fresh_today.sh")
LABEL = "⚠️ Dữ liệu 8L rating có thể chưa cập nhật hôm nay (file cũ)."
d = tempfile.mkdtemp(); csv = os.path.join(d, "rating_8l.csv")


def run_c(mtime_date=None, exists=True, ref="2026-07-31", tz=None):
    if exists:
        open(csv, "w").write("ticker,rating\nFPT,1\n")
        if mtime_date:
            t = datetime.datetime.combine(mtime_date, datetime.time(19, 20), tzinfo=ICT).timestamp()
            os.utime(csv, (t, t))
    elif os.path.exists(csv):
        os.remove(csv)
    env = dict(os.environ, FRESH_REF_DATE=str(ref))
    env.pop("TZ", None)
    if tz:
        env["TZ"] = tz
    p = subprocess.run(["bash", CHECKER, csv, LABEL], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout.strip()


rc, out = run_c(datetime.date(2026, 7, 31))
chk("C1 file ghi HÔM NAY → rc=0, im lặng (không cảnh báo giả)", rc == 0 and out == "", f"(out={out!r})")
rc, out = run_c(datetime.date(2026, 7, 30))
chk("C2 file của HÔM QUA (pt_8l_daily fail im lặng) → rc=1 + đúng câu cảnh báo",
    rc == 1 and out.startswith(LABEL) and "2026-07-30" in out, f"(out={out!r})")
rc, out = run_c(exists=False)
chk("C3 file KHÔNG tồn tại → rc=1 + cảnh báo", rc == 1 and "KHÔNG TÌM THẤY" in out, f"(out={out!r})")
# ranh giới ICT: 07-30T18:30Z = 01:30 ICT 07-31 ⇒ ĐÃ là hôm nay theo giờ VN dù TZ tiến trình là gì
t = datetime.datetime(2026, 7, 30, 18, 30, tzinfo=datetime.timezone.utc).timestamp()
for tz in (None, "UTC", "America/New_York"):
    open(csv, "w").write("x\n"); os.utime(csv, (t, t))
    env = dict(os.environ, FRESH_REF_DATE="2026-07-31"); env.pop("TZ", None)
    if tz:
        env["TZ"] = tz
    p = subprocess.run(["bash", CHECKER, csv, LABEL], capture_output=True, text=True, env=env)
    chk(f"C4 ranh giới ICT dưới TZ={tz or 'unset'}: mtime 07-30T18:30Z → coi là HÔM NAY",
        p.returncode == 0, f"(rc={p.returncode} {p.stdout.strip()!r})")

# wiring: telegram_run_daily.sh truyền cảnh báo vào ĐẦU tin nhắn qua EXTRA_WARN_HEADER
TRD = open(os.path.join(W, "telegram_run_daily.sh"), encoding="utf-8").read()
chk("C5 telegram_run_daily gọi checker + export EXTRA_WARN_HEADER trước khi build/send",
    "csv_fresh_today.sh" in TRD and "export EXTRA_WARN_HEADER" in TRD
    and TRD.index("export EXTRA_WARN_HEADER") < TRD.index("telegram_recommend.py"))
# build_message: exec NGUYÊN VĂN khối header trích từ telegram_recommend.py
TR = open(os.path.join(W, "telegram_recommend.py"), encoding="utf-8").read()
hdr = TR[TR.index("    # Cảnh báo độ tươi INPUT"):TR.index('        f"<b>Market regime (DT5G):</b>')]
hdr = "\n".join(l[4:] if l.startswith("    ") else l for l in hdr.splitlines()) + "]"  # đóng list bị cắt
ns = {"os": os, "target": "2026-07-31", "now": "2026-07-31 19:35", "state_emoji": "🟡",
      "state_label": "NEUTRAL", "state5": 3}
os.environ["EXTRA_WARN_HEADER"] = LABEL + " (ghi lần cuối 2026-07-30)"
exec(hdr, ns)
chk("C6 tin nhắn Telegram: cảnh báo nằm DÒNG ĐẦU, trước tiêu đề báo cáo",
    ns["lines"][0].startswith("<b>⚠️ Dữ liệu 8L") and "V2.3 (DT5G) REPORT" in ns["lines"][2],
    f"({ns['lines'][0][:50]}…)")
os.environ.pop("EXTRA_WARN_HEADER")
ns2 = dict(ns); ns2.pop("lines")
exec(hdr, ns2)
chk("C7 không có env (mọi caller khác + ngày file tươi) → tin nhắn KHÔNG đổi một chữ",
    ns2["lines"][0].startswith("<b>🛰️ V2.3 (DT5G) REPORT"))

print(f"\n== TỔNG: {ok} PASS / {fail} FAIL ==")

if "--tz-matrix" in sys.argv:
    # Chạy lại chính file này dưới 3 TZ khác nhau; kết quả phải GIỐNG HỆT dòng tổng kết.
    print("\n== TZ matrix (kết quả phải bằng nhau ở mọi TZ) ==")
    base = dict(os.environ); base.pop("TZ", None)
    outs = {}
    for label, env in (("unset", base),
                       ("UTC", dict(base, TZ="UTC")),
                       ("America/New_York", dict(base, TZ="America/New_York")),
                       ("Asia/Ho_Chi_Minh", dict(base, TZ="Asia/Ho_Chi_Minh"))):
        p = subprocess.run([sys.executable, os.path.abspath(__file__)],
                           capture_output=True, text=True, env=env)
        line = [l for l in p.stdout.splitlines() if l.startswith("== TỔNG")]
        outs[label] = line[0] if line else f"(crash rc={p.returncode}) {p.stderr[-300:]}"
        print(f"  TZ={label:18s} {outs[label]}")
    same = len(set(outs.values())) == 1 and "FAIL ==" in list(outs.values())[0] and \
        list(outs.values())[0].endswith("0 FAIL ==")
    print(f"  {'PASS' if same else 'FAIL'}  TZ-independence (mọi TZ ra cùng kết quả, 0 FAIL)")
    sys.exit(0 if same else 1)

sys.exit(0 if fail == 0 else 1)
