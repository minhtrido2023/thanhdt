#!/usr/bin/env python3
"""Selfcheck cho append_cctg_rate.py --series tier2 (user duyệt 2026-10-13): CCTG của nhóm ngân
hàng ngay sau Big-4 (VPB/MB/TCB/ACB) — CHỈ THU THẬP + HIỂN THỊ.

Phần W (writer): file + sidecar riêng; khoá = (bank, denomination); mọi guard tính riêng từng khoá
(không suy số ngân hàng này từ ngân hàng khác); giữ đủ guard của 12m/6m; không rò sang 12m/6m.
Phần B (ranh giới cứng): effective_deposit_rate / macro_killswitch_a_status /
consumer_deposit_rate* / chuỗi của deposit_cctg_trend_check / dcf_valuation.discount_rate cho
kết quả giống hệt từng byte khi file tier2 VẮNG so với khi CÓ (kể cả dòng 9,2% và 15%), và không
lần nào mở/dò file đó; quét tĩnh: không consumer nào nhắc tới file hay import writer.
Chạy từ chính thư mục chứa file (tự định vị, chạy được trong worktree).

Vòng 2 (arch-review, job Taylor_20261013_090057): ghi song song (flock), khoá mới không lách được
guard lệch >=1pp, selfcheck không rơi sang cây PRODUCTION (sys.path), không phụ thuộc env ngoài."""
import ast
import builtins
import contextlib
import csv
import glob
import io
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

os.environ.pop("DEPOSIT_RATE_CCTG_OVERLAY", None)  # B1: không phụ thuộc rollback knob của môi trường gọi
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import append_cctg_rate as acr  # noqa: E402
import cctg_rate_vn as cctg  # noqa: E402
import deposit_rate_vn as dep  # noqa: E402
import deposit_cctg_trend_check as trend  # noqa: E402
import dcf_valuation as dcf  # noqa: E402
import pandas as pd  # noqa: E402

# A2: dcf_valuation chèn thư mục PRODUCTION lên đầu sys.path (dcf_valuation.py:55-56); từ đây về sau
# importlib.reload(cctg_rate_vn) (lượt 12m của writer) sẽ nạp file production nếu không ghim lại HERE.
sys.path.insert(0, HERE)
TREE_MODULES = ("append_cctg_rate", "cctg_rate_vn", "deposit_rate_vn", "deposit_cctg_trend_check", "dcf_valuation")


def assert_tree(where):
    for n in TREE_MODULES:
        m = sys.modules[n]
        assert os.path.dirname(os.path.abspath(m.__file__)) == HERE, f"[{where}] nạp nhầm {n} ngoài cây này: {m.__file__}"
    import importlib.util
    spec = importlib.util.find_spec("cctg_rate_vn")  # đúng thứ importlib.reload sẽ tìm
    assert os.path.dirname(os.path.abspath(spec.origin)) == HERE, f"[{where}] reload sẽ nạp {spec.origin}"


assert_tree("sau import")
_TODAY_D = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
TODAY = _TODAY_D.isoformat()
TOMORROW = (_TODAY_D + timedelta(days=1)).isoformat()
YESTERDAY = (_TODAY_D - timedelta(days=1)).isoformat()
EXPECTED_HEADER = ["effective_date", "bank", "product", "denomination", "holding_period", "cctg_rate",
                   "collected_date", "source", "note"]
FAILS = []
N = 0
LAST_OUT = ""


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
    global LAST_OUT
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            return (acr.main() or 0), ""
    except SystemExit as e:
        return 1, str(e.code)
    finally:
        LAST_OUT = buf.getvalue()
        sys.stdout.write(LAST_OUT)
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

    rc, msg = run(t2("VPB", 9.2, TODAY, "100tr", product="CCTG Super Thịnh Vượng"))
    check("W7 cùng (ngày, VPB, 100tr) + cùng sản phẩm + cùng lợi suất chạy lại: SKIP rc=0, thông báo nêu khoá",
          rc == 0 and len(rows(csvt)) == 1 and "SKIP" in LAST_OUT and "[tier2 VPB 100tr]" in LAST_OUT)
    b_t = raw(csvt)
    rc, msg = run(t2("VPB", 9.2, TODAY, "100tr", product="CCTG Khác"))
    check("W7b cùng khoá cùng ngày NHƯNG KHÁC sản phẩm: rc != 0, in dòng đang có, không ghi",
          rc != 0 and "CCTG Super Thịnh Vượng" in msg and "9.2" in msg and "[tier2 VPB 100tr]" in msg and raw(csvt) == b_t)
    rc, msg = run(t2("VPB", 9.3, TODAY, "100tr", product="CCTG Super Thịnh Vượng"))
    check("W7c cùng khoá cùng ngày NHƯNG KHÁC lợi suất: rc != 0, in dòng đang có (9.2), không ghi",
          rc != 0 and "rate=9.2%" in msg and "9.3%" in msg and raw(csvt) == b_t)
    rc, msg = run(t2("VPB", 7.5, TODAY, "10tr", holding="184-389 ngày"))
    rt = rows(csvt)
    check("W8 VPB 10tr cùng ngày là khoá RIÊNG -> ghi thêm, giữ holding_period",
          rc == 0 and len(rt) == 2 and rt[1]["denomination"] == "10tr" and rt[1]["holding_period"] == "184-389 ngày")
    rc, msg = run(t2("MB", 7.1, TODAY))
    rt = rows(csvt)
    check("W9 MB 7,1% (lệch 2,1pp so với VPB) vẫn ghi — không so chéo ngân hàng; denomination để trống",
          rc == 0 and len(rt) == 3 and rt[2]["bank"] == "MB" and rt[2]["denomination"] == "")
    rc, msg = run(t2("VPB", 10.3, TOMORROW, "100tr"))
    check("W10 VPB 100tr lệch 1,1pp so với kỳ trước CÙNG khoá bị chặn; thông báo nêu khoá [tier2 VPB 100tr]",
          rc == 1 and "differs" in msg and "[tier2 VPB 100tr]" in msg and len(rows(csvt)) == 3)
    rc, msg = run(t2("VPB", 9.2, YESTERDAY, "100tr"))
    check("W11 VPB 100tr ngày cũ hơn dòng cuối cùng khoá bị chặn; thông báo nêu khoá và KHÔNG nhắc cctg_events_df()",
          rc == 1 and "not newer" in msg and "[tier2 VPB 100tr]" in msg and "cctg_events_df" not in msg
          and len(rows(csvt)) == 3)
    rc6_, msg6_ = run(["--series", "6m", "--rate", "7.5", "--effective", "2026-09-01", "--source", "manual_verify"])
    check("W11a chuỗi 6m: thông báo 'không mới hơn' cũng không nhắc cctg_events_df() (hàm đó chỉ đọc file 12M)",
          rc6_ == 1 and "not newer" in msg6_ and "cctg_events_df" not in msg6_)
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


    # ---------- A3: đổi khoá không được lách guard lệch >=1pp ----------
    def fresh():
        for pth in [csvt, csvt + ".lock"] + glob.glob(os.path.join(d, "cctg_tier2_*")):
            if os.path.exists(pth):
                os.remove(pth)

    def seed(bank, rate, eff, denom=None, product="CCTG X"):
        r_, m_ = run(t2(bank, rate, eff, denom, product=product))  # người: không JOB_ID
        assert r_ == 0, m_

    def agent_run(bank, rate, eff, denom=None, tag="k"):
        pub = [src("VietnamNet", f"https://vietnamnet.vn/{tag}-{bank}-{denom}-{rate}", rate),
               src("Nghe An", f"https://baonghean.vn/{tag}-{bank}-{denom}-{rate}", rate)]
        return run(t2(bank, rate, eff, denom, source="web_crosscheck_auto",
                      extra=["--collected", TODAY, "--note", "x", "--sources", json.dumps(pub)]), job_id="selfcheck_job")

    fresh()
    seed("VPB", 9.2, YESTERDAY, "100tr")
    rc, msg = run(t2("VPB", 12.0, TODAY, "100tr"))
    check("K1 [gốc] VPB 100tr 9,2% có sẵn, người ghi 12,0% vào CÙNG khoá: bị từ chối", rc == 1 and "differs" in msg)
    n0 = len(rows(csvt))
    rc, msg = run(t2("VPB", 12.0, TODAY))  # bỏ --denom ⇒ khoá '' (khoá mới)
    check("K2 [A3a] người bỏ --denom để lách (khoá '' cho VPB đang có khoá 100tr): bị từ chối", rc == 1 and "KHOÁ MỚI" in msg and len(rows(csvt)) == n0)
    rc, msg = agent_run("VPB", 12.0, TODAY, None)
    check("K3 [A3a] agent bỏ --denom để lách: bị từ chối", rc == 1 and "KHOÁ MỚI" in msg and len(rows(csvt)) == n0)
    rc, msg = run(t2("VPB", 9.4, TODAY, "10tr"))
    check("K4 người seed khoá 10tr cho VPB (đã có 100tr) vẫn ghi được (không rơi vào A3a; người không bị A3b/c)",
          rc == 0 and len(rows(csvt)) == n0 + 1)
    rc, msg = run(t2("VPB", 12.0, TODAY, extra=["--force"]))
    check("K5 [A3a] người có --force được mở khoá '' (lối thoát có chủ đích của người)", rc == 0 and len(rows(csvt)) == n0 + 2)
    fresh()
    seed("VPB", 9.2, YESTERDAY, "100tr")
    rc, msg = agent_run("VPB", 12.0, TODAY, "10tr")
    check("K6 [A3b] agent mở khoá MỚI VPB 10tr 12,0% (lệch 2,8pp so với khoá cùng ngân hàng): bị từ chối, nhắc người seed",
          rc == 1 and "seed" in msg and len(rows(csvt)) == 1)
    rc, msg = agent_run("VPB", 9.7, TODAY, "10tr")
    check("K7 [A3b] agent mở khoá MỚI VPB 10tr 9,7% (lệch 0,5pp): ghi được", rc == 0 and len(rows(csvt)) == 2)
    rc, msg = agent_run("TCB", 29.9, TODAY)
    check("K8 [A3c] agent mở ngân hàng CHƯA có dòng TCB 29,9%: ngoài dải (8,2; 10,7) -> bị từ chối",
          rc == 1 and "ngoài dải" in msg and "seed" in msg and len(rows(csvt)) == 2)
    rc, msg = agent_run("TCB", 8.0, TODAY)
    check("K9 [A3c] TCB 8,0% vẫn ngoài dải (8,2; 10,7): bị từ chối", rc == 1 and len(rows(csvt)) == 2)
    res_ = [agent_run("TCB", r_, TODAY, tag=f"b{r_}") for r_ in (12.0, 10.8, 7.0)]
    check("K9b [A3c] biên dải (8,2; 10,7): TCB 12,0% / 10,8% (trên) và 7,0% (dưới) đều bị từ chối vì 'ngoài dải'",
          all(rc_ == 1 and "ngoài dải" in m_ for rc_, m_ in res_) and len(rows(csvt)) == 2)
    rc, msg = agent_run("TCB", 9.0, TODAY)
    check("K10 [A3c] TCB 9,0% trong dải (8,2; 10,7): ghi được", rc == 0 and len(rows(csvt)) == 3)
    fresh()
    rc, msg = agent_run("TCB", 9.0, TODAY)
    check("K11 [A3c] file RỖNG, agent mở khoá đầu tiên: không có mốc ⇒ bị từ chối (fail-safe), file không được tạo",
          rc == 1 and "chưa có dòng nào" in msg and not rows(csvt))
    fresh()
    seed("MB", 7.1, YESTERDAY)
    seed("ACB", 7.2, YESTERDAY)
    rc1, _ = agent_run("MB", 7.3, TODAY, None, tag="mb")
    rc2, _ = agent_run("ACB", 7.2, TODAY, None, tag="acb")
    check("K12 dòng mốc MB/ACB hiện có (khoá mệnh giá rỗng) vẫn ghi tiếp được bằng agent (cùng khoá, không phải khoá mới)",
          rc1 == 0 and rc2 == 0 and len(rows(csvt)) == 4)
    rc, msg = agent_run("MB", 7.3, TOMORROW, "10tr", tag="mb2")
    check("K13 [A3a] MB đang có khoá '' mà agent mở khoá 10tr: bị từ chối (đổi kiểu mệnh giá)",
          rc == 1 and "KHOÁ MỚI" in msg and len(rows(csvt)) == 4)
    # B4: mốc NGƯỜI trong delta guard của tier2 (agent trôi dần 0,7pp/lần không vượt được mốc người 1pp)
    fresh()
    d3, d2, d1 = [(_TODAY_D - timedelta(days=k)).isoformat() for k in (3, 2, 1)]
    seed("MB", 7.0, d3)
    rc1, _ = run(t2("MB", 7.6, d2, source="web_crosscheck_auto",
                    extra=["--collected", TODAY, "--note", "x", "--sources", json.dumps(
                        [src("VietnamNet", "https://vietnamnet.vn/h1", 7.6), src("Nghe An", "https://baonghean.vn/h1", 7.6)])]),
                  job_id="selfcheck_job")
    rc2, msg2 = run(t2("MB", 8.2, d1, source="web_crosscheck_auto",
                       extra=["--collected", TODAY, "--note", "x", "--sources", json.dumps(
                           [src("VietnamNet", "https://vietnamnet.vn/h2", 8.2), src("Nghe An", "https://baonghean.vn/h2", 8.2)])]),
                    job_id="selfcheck_job")
    check("B4a mốc NGƯỜI trong delta guard của tier2: 7,0 (người) -> 7,6 (agent) ghi; 8,2 (agent) lệch 0,6pp so với kỳ trước "
          "nhưng 1,2pp so với mốc người => bị chặn",
          rc1 == 0 and rc2 == 1 and "differs" in msg2 and "[tier2 MB" in msg2 and len(rows(csvt)) == 2)
    # B4: sidecar tách theo mệnh giá của CÙNG ngân hàng
    fresh()
    seed("VPB", 9.2, YESTERDAY, "100tr")
    seed("VPB", 9.2, YESTERDAY, "10tr")
    same = [src("VietnamNet", "https://vietnamnet.vn/sd", 9.2), src("Nghe An", "https://baonghean.vn/sd", 9.2)]

    def agent_same(denom, eff):
        return run(t2("VPB", 9.2, eff, denom, source="web_crosscheck_auto",
                      extra=["--collected", TODAY, "--note", "x", "--sources", json.dumps(same)]), job_id="selfcheck_job")
    r_a, _ = agent_same("100tr", TODAY)
    r_b, _ = agent_same("10tr", TODAY)  # cùng URL, mệnh giá KHÁC của cùng ngân hàng: sidecar riêng ⇒ vẫn ghi
    r_c, m_c = agent_same("100tr", TOMORROW)  # cùng URL, CÙNG khoá, kỳ sau ⇒ chặn
    check("B4b sidecar tách theo mệnh giá của cùng ngân hàng: 2 file riêng; URL dùng cho 10tr không cản 100tr; dùng lại trong "
          "cùng khoá thì bị chặn",
          r_a == 0 and r_b == 0 and r_c == 1 and "already used" in m_c
          and sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "cctg_tier2_*sources.json")))
          == ["cctg_tier2_VPB_100tr_last_auto_sources.json", "cctg_tier2_VPB_10tr_last_auto_sources.json"])
    # B4: --product toàn khoảng trắng; pin danh sách ngân hàng / mệnh giá
    rc, msg = run(t2("VPB", 9.2, TOMORROW, "100tr", product="   "))
    check("B4c --product toàn khoảng trắng bị chặn", rc == 1 and "--product" in msg)
    check("B4d TIER2_BANKS ghim đúng (VPB, MB, TCB, ACB) — thêm ngân hàng phải sửa selfcheck có chủ đích",
          acr.TIER2_BANKS == ("VPB", "MB", "TCB", "ACB"))
    check("B4e TIER2_DENOMS ghim đúng (10tr, 100tr)", acr.TIER2_DENOMS == ("10tr", "100tr"))
    rc, msg = run(t2("HDB", 7.0, TOMORROW))
    rc2, msg2 = run(t2("VPB", 9.2, TOMORROW, "1ty"))
    check("B4f --bank HDB và --denom 1ty bị chặn", rc == 1 and rc2 == 1 and "--bank" in msg and "--denom" in msg2)
    fresh()

    # ---------- A1: ghi song song không được làm mất dòng ----------
    DRIVER = (
        "import os, sys, time\n"
        "sys.path.insert(0, os.environ['T2_HERE'])\n"
        "import append_cctg_rate as a\n"
        "a.CSV_PATH_TIER2 = os.environ['T2_CSV']\n"
        "tag, go = sys.argv[1], os.environ['T2_GO']\n"
        "open(go + '.ready.' + tag, 'w').close()\n"
        "t0 = time.time()\n"
        "while not os.path.exists(go) and time.time() - t0 < 90:\n"
        "    time.sleep(0.005)\n"
        "sys.argv = ['append_cctg_rate.py'] + sys.argv[2:]\n"
        "sys.exit(a.main() or 0)\n")
    PROCS = [("VPB", "10tr", "7.5"), ("VPB", "100tr", "9.2"), ("MB", "", "7.1"), ("TCB", "", "8.0"), ("ACB", "", "7.2"),
             ("VPB", "100tr", "9.2"), ("VPB", "100tr", "9.2"), ("MB", "", "7.1")]  # 3 lệnh TRÙNG khoá+ngày cuối: phải SKIP
    EXPECT_ROWS = 5
    bad_rounds, detail = 0, []
    for rnd in range(3):
        cdir = tempfile.mkdtemp(prefix="cctg_t2conc_")
        ccsv, go = os.path.join(cdir, "cctg_rate_vn_tier2_events.csv"), os.path.join(cdir, "go")
        env = {k: v for k, v in os.environ.items() if k != "JOB_ID"}
        env.update(T2_HERE=HERE, T2_CSV=ccsv, T2_GO=go)
        ps = []
        for i, (bk, dn, rt) in enumerate(PROCS):
            argv = ["--series", "tier2", "--bank", bk, "--product", "CCTG X", "--rate", rt, "--effective", TODAY,
                    "--source", "manual_verify"] + (["--denom", dn] if dn else [])
            ps.append(subprocess.Popen([sys.executable, "-c", DRIVER, str(i)] + argv, env=env, cwd=cdir,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        t0 = datetime.now()
        while len(glob.glob(go + ".ready.*")) < len(ps) and (datetime.now() - t0).seconds < 90:
            if any(p_.poll() is not None for p_ in ps):
                break
            pass
        open(go, "w").close()
        outs = [p_.communicate(timeout=120) for p_ in ps]
        n_ok = sum(o[0].count("OK: appended") for o in outs)
        n_skip = sum(o[0].count("SKIP:") for o in outs)
        got = rows(ccsv)
        keys = sorted((r["bank"], r["denomination"]) for r in got)
        if not (n_ok == len(got) == EXPECT_ROWS and n_skip == len(PROCS) - EXPECT_ROWS and len(set(keys)) == EXPECT_ROWS
                and all(p_.returncode == 0 for p_ in ps)):
            bad_rounds += 1
            detail.append((rnd, n_ok, n_skip, len(got), [p_.returncode for p_ in ps], [o[1][-200:] for o in outs if o[1]]))
        shutil.rmtree(cdir, ignore_errors=True)
    check(f"A1a 3 vòng x {len(PROCS)} tiến trình --series tier2 chạy ĐỒNG THỜI (có rào xuất phát): số dòng == số 'OK: appended' "
          f"== {EXPECT_ROWS}, 3 lệnh trùng khoá đều SKIP, không dòng nào mất (vòng lỗi: {bad_rounds} {detail[:1]})", bad_rounds == 0)
    # sidecar không mất: agent chạy đồng thời trên 5 khoá có sẵn; sau đó dùng lại URL ở khoá nào cũng phải bị chặn
    cdir = tempfile.mkdtemp(prefix="cctg_t2conc_")
    ccsv, go = os.path.join(cdir, "cctg_rate_vn_tier2_events.csv"), os.path.join(cdir, "go")
    old_csvt = acr.CSV_PATH_TIER2
    acr.CSV_PATH_TIER2 = ccsv
    try:
        for bk, dn, rt in PROCS[:5]:
            seed(bk, float(rt), YESTERDAY, dn or None)
    finally:
        acr.CSV_PATH_TIER2 = old_csvt
    env = {k: v for k, v in os.environ.items()}
    env.update(T2_HERE=HERE, T2_CSV=ccsv, T2_GO=go, JOB_ID="selfcheck_job")
    ps = []
    for i, (bk, dn, rt) in enumerate(PROCS[:5]):
        pub = json.dumps([{"publisher": "VietnamNet", "url": f"https://vietnamnet.vn/c-{i}", "date": TODAY, "rate": float(rt)},
                          {"publisher": "Nghe An", "url": f"https://baonghean.vn/c-{i}", "date": TODAY, "rate": float(rt)}])
        argv = ["--series", "tier2", "--bank", bk, "--product", "CCTG X", "--rate", rt, "--effective", TODAY,
                "--source", "web_crosscheck_auto", "--collected", TODAY, "--note", "x", "--sources", pub] + (["--denom", dn] if dn else [])
        ps.append(subprocess.Popen([sys.executable, "-c", DRIVER, str(i)] + argv, env=env, cwd=cdir,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
    t0 = datetime.now()
    while len(glob.glob(go + ".ready.*")) < len(ps) and (datetime.now() - t0).seconds < 90 and not any(p_.poll() is not None for p_ in ps):
        pass
    open(go, "w").close()
    outs = [p_.communicate(timeout=120) for p_ in ps]
    got = rows(ccsv)
    check(f"A1b 5 agent ghi đồng thời lên 5 khoá có sẵn: 10 dòng (5 seed + 5 mới), 5 sidecar riêng đều còn "
          f"({len(got)} dòng, {sorted(os.path.basename(x) for x in glob.glob(os.path.join(cdir, 'cctg_tier2_*')))})",
          len(got) == 10 and sum(o[0].count("OK: appended") for o in outs) == 5
          and len(glob.glob(os.path.join(cdir, "cctg_tier2_*sources.json"))) == 5)
    shutil.rmtree(cdir, ignore_errors=True)

    # B9: help không còn nói --rate là 'Big-4' cho mọi chuỗi
    old_argv_ = sys.argv
    sys.argv = ["append_cctg_rate.py", "--help"]
    hb = io.StringIO()
    try:
        with contextlib.redirect_stdout(hb):
            acr.main()
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv_
    help_txt = " ".join(hb.getvalue().split())
    check("B9 --help: --rate mô tả cả tier2 (không chỉ 'Big-4 CCTG rate')",
          "Big-4 CCTG rate" not in help_txt and "tier2: that bank" in help_txt and "VPB/MB/TCB/ACB" in help_txt)

    # ---------- B: ranh giới cứng ----------
    assert_tree("trước phần B")
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
            old_argv, buf = sys.argv, io.StringIO()
            sys.argv = ["deposit_cctg_trend_check.py", "--dry-run"]
            try:
                with contextlib.redirect_stdout(buf):
                    rc_main = trend.main()
            finally:
                sys.argv = old_argv
            out.append(("trend.main --dry-run", repr((rc_main, buf.getvalue()))))
            return out
        finally:
            (builtins.open, os.path.exists, os.path.isfile, os.stat, os.listdir, os.scandir,
             glob.glob, pd.read_csv) = real

    fresh()
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
    check(f"B1 {len(snap_absent)} đầu ra (effective/kill-switch A/consumer*/DCF r/trend/trend.main --dry-run) giống hệt từng byte "
          f"vắng vs có file tier2 [sha256 {h(snap_absent)[:12]}]",
          len(snap_absent) >= 40 and h(snap_absent) == h(snap_present))
    for name in ("effective_deposit_rate", "macro_killswitch_a_status", "consumer_deposit_rate_detail",
                 "consumer_deposit_rate", "dcf.discount_rate", "trend._load_series", "trend.main --dry-run"):
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
    for pat in ("*.py", "*.sh", "trading_bot/**/*.py", "deploy_golive_dt5g_v4/**/*.py"):
        files += [p for p in glob.glob(os.path.join(HERE, pat), recursive=True) if os.path.isfile(p)]
    # B3: mike/bin chỉ có ở cây canonical (nested repo, không nằm trong worktree) — nói rõ quét hay không, không im lặng
    CANON_MIKEBIN = "/home/trido/thanhdt/WorkingClaude/mike/bin"
    own_mb = os.path.join(HERE, "mike", "bin")
    if os.path.isdir(own_mb):
        mb_dir, mb_note = own_mb, "mike/bin: QUÉT (của cây này)"
    elif os.path.isdir(CANON_MIKEBIN):
        mb_dir, mb_note = CANON_MIKEBIN, f"mike/bin: cây này KHÔNG có mike/bin -> QUÉT THAY bằng bản canonical {CANON_MIKEBIN}"
    else:
        mb_dir, mb_note = None, "mike/bin: KHÔNG QUÉT (cây này và canonical đều vắng) — phạm vi quét hẹp hơn đủ"
    print("S0 " + mb_note)
    if mb_dir:
        files += [p for p in glob.glob(os.path.join(mb_dir, "*")) if os.path.isfile(p)]
    # Người đọc ĐÃ BIẾT, user duyệt 2026-10-13 15:21 ICT (commit 0adc1293f): ngưỡng Macro Watch (6) nằm trong PROMPT của
    # vn_realestate_monthly_check.py, bảo agent đọc số kỳ trước ở file tier2 — đọc để HIỂN THỊ/escalate, không phải code số.
    PROMPT_READERS = {"vn_realestate_monthly_check.py"}
    offenders, importers, prompt_readers = [], [], []
    for p in sorted(set(files)):
        rel = os.path.relpath(p, HERE)
        try:
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        if TOKEN.search(text) and rel not in ALLOWED:
            if mb_dir and os.path.dirname(p) == mb_dir and os.path.basename(p) in PROMPT_READERS:
                prompt_readers.append(os.path.basename(p))
            else:
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
    check(f"S1 quét {len(set(files))} file [{mb_note}]: chỉ writer/selfcheck/wrapper tuần nhắc tới chuỗi tier2 (vi phạm: {offenders}; người đọc đã biết qua prompt: {prompt_readers})",
          len(set(files)) > 50 and offenders == [])
    missing = [c for c in CONSUMERS if not os.path.isfile(os.path.join(HERE, c))]
    check(f"S2 đủ {len(CONSUMERS)} file consumer được nêu tên nằm trong phạm vi quét (thiếu: {missing})", missing == [])
    check(f"S3 chỉ selfcheck mới import writer append_cctg_rate (import: {sorted(set(importers))})",
          all(os.path.basename(r).endswith("_selfcheck.py") for r in importers)
          and not set(importers) & set(CONSUMERS))
    # B5: AST — trong file consumer ngoài 3 module chính, MỌI hằng chuỗi một-token chứa 'cctg' phải thuộc danh sách nhãn đã
    # biết; bắt đường dẫn ghép chuỗi ("cctg_rate_vn_" + "tier" + ...), glob "cctg_*.csv", duckdb/pd.read_csv — thứ mà quét
    # regex trên văn bản không thấy. KHÔNG bắt được: chuỗi tạo hoàn toàn động ("cc" + "tg") — khoảng hở đã biết.
    CCTG_LABELS_OK = {"cctg_6m", "cctg_note"}  # nhãn khoá dict/hiển thị (value_radar.py, dna_report.py), không phải đường dẫn
    ast_bad, ast_scanned = [], 0
    for c in CONSUMERS:
        if os.path.basename(c) in ("deposit_rate_vn.py", "cctg_rate_vn.py", "deposit_cctg_trend_check.py"):
            continue
        pth = os.path.join(HERE, c)
        if not os.path.isfile(pth):
            continue
        try:
            tree_ = ast.parse(open(pth, encoding="utf-8").read())
        except SyntaxError:
            ast_bad.append((c, "SyntaxError"))
            continue
        ast_scanned += 1
        for node in ast.walk(tree_):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str) and "cctg" in node.value.lower()
                    and re.fullmatch(r"\S+", node.value) and node.value not in CCTG_LABELS_OK):
                ast_bad.append((c, node.lineno, node.value[:80]))
    # 3 module chính: chỉ được nhắc đúng các file CCTG đã biết (đường dẫn thật)
    KNOWN_FILES = {"cctg_rate_vn_events.csv", "cctg_rate_vn_6m_events.csv", "cctg_rate_last_auto_sources.json",
                   "cctg6m_rate_last_auto_sources.json", "cctg_trend_alert_state.json"}
    path_bad = []
    for c in ("deposit_rate_vn.py", "cctg_rate_vn.py", "deposit_cctg_trend_check.py"):
        pth = os.path.join(HERE, c)
        for node in ast.walk(ast.parse(open(pth, encoding="utf-8").read())):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for m_ in re.findall(r"cctg[\w*]*\.(?:csv|json)", node.value):
                    if m_ not in KNOWN_FILES:
                        path_bad.append((c, node.lineno, m_))
    check(f"S6 [AST] {ast_scanned} consumer ngoài 3 module chính: không hằng chuỗi 'cctg' nào ngoài nhãn đã biết "
          f"({ast_bad}); 3 module chính chỉ nhắc file CCTG đã biết ({path_bad})",
          ast_bad == [] and path_bad == [] and ast_scanned >= 8)
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
    # ---------- B7 / B8: wrapper cron ----------
    check("B7a dispatch của wrapper đặt --timeout 1200 --max-turns 80",
          re.search(r'dispatch\.sh"? Winston "\$PROMPT" --timeout 1200 --max-turns 80', sh) is not None)
    check("B7b prompt buộc làm chuỗi 5 SAU CÙNG: event done + Discord cho chuỗi 1-4 TRƯỚC khi bắt đầu chuỗi 5",
          "làm chuỗi 5 SAU CÙNG" in sh and "TRƯỚC khi bắt đầu chuỗi 5" in sh)
    check("A1c prompt buộc chạy TUẦN TỰ từng lệnh chuỗi 5", "Chạy TUẦN TỰ từng lệnh chuỗi 5" in sh and "KHÔNG chạy song song" in sh)
    check("B8 chuỗi 5 KHÔNG mở question: prompt nói rõ chỉ event DONE, mâu thuẫn ghi vào note + Discord",
          "CHUỖI 5 KHÔNG mở question" in sh and "KHÔNG BAO GIỜ question" in sh and "chỉ dùng question khi" not in sh
          and "escalate nhắc xác nhận tay" not in sh)
    m_pc = re.search(r"<<'PYEOF' 2>>\"\$LOG\"\n(.*?)\nPYEOF\n", sh, re.S)
    check("B7c tách được khối post-condition python từ wrapper", m_pc is not None)
    if m_pc:
        def postcond(events):
            cw = tempfile.mkdtemp(prefix="cctg_t2pc_")
            os.makedirs(os.path.join(cw, "mike", "bus", "inbox"))
            start = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            ts = (datetime.utcnow() + timedelta(seconds=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(os.path.join(cw, "mike", "bus", "inbox", "Winston.jsonl"), "w", encoding="utf-8") as f:
                for topic, et, series in events:
                    f.write(json.dumps({"ts": ts, "agent_id": "Winston", "event_type": et, "topic": topic,
                                        "payload": {"series": series}}) + "\n")
            r_ = subprocess.run([sys.executable, "-c", m_pc.group(1), start], cwd=cw, capture_output=True, text=True)
            shutil.rmtree(cw, ignore_errors=True)
            return r_.stdout.strip().splitlines(), r_.returncode
        done = "deposit-cctg-weekly-done"
        out_, rc_ = postcond([(done, "status", s_) for s_ in ("big4_12m", "cctg_12m", "cctg_6m", "sbv_policy")])
        check("B7d chuỗi 1-4 có event, chuỗi 5 chưa: post-condition = yes, thiếu đúng 'cctg_tier2' (không báo hỏng cho chuỗi cũ)",
              rc_ == 0 and len(out_) >= 3 and out_[0] == "yes" and out_[2] == "cctg_tier2" and "big4_12m" in out_[1] and "cctg_tier2" not in out_[1])
        out_, rc_ = postcond([])
        check("B7e không event nào: post-condition = no, thiếu cả 5 chuỗi", rc_ == 0 and len(out_) >= 3 and out_[0] == "no" and len(out_[2].split(",")) == 5)
        out_, rc_ = postcond([(done, "status", s_) for s_ in ("big4_12m", "cctg_12m", "cctg_6m", "sbv_policy", "cctg_tier2")])
        check("B7f đủ 5 chuỗi: không thiếu chuỗi nào", rc_ == 0 and out_[0] == "yes" and (len(out_) < 3 or out_[2] == ""))
        # nhánh thông báo của wrapper: chuỗi 5 hỏng + dispatch rc != 0 -> KHÔNG dùng câu 'KHÔNG có kết quả xác nhận được'
        i_part = sh.find('elif [ "${CONFIRMED:-no}" = "yes" ] && [ -n "${SEEN_SERIES:-}" ]')
        i_old = sh.find('elif [ "$DISPATCH_RC" -ne 0 ] || [ "${CONFIRMED:-no}" != "yes" ]; then')
        part_branch = sh[i_part:i_old] if 0 <= i_part < i_old else ""
        i_part = i_part if part_branch else i_old + 1
        check("B7g nhánh 'dừng giữa chừng' đứng TRƯỚC nhánh cũ, nêu chuỗi đã xong + chuỗi thiếu, không chứa câu "
              "'KHÔNG có kết quả xác nhận được'",
              i_part < i_old and "${SEEN_SERIES}" in part_branch and "${MISSING_SERIES}" in part_branch
              and "KHÔNG có kết quả xác nhận được" not in part_branch and "KHÔNG cần làm lại" in part_branch)
    assert_tree("cuối file")
finally:
    acr.CSV_PATH, acr.CSV_PATH_6M, acr.CSV_PATH_TIER2, cctg._EVENTS_CSV, dep._EVENTS_CSV = orig
    shutil.rmtree(d, ignore_errors=True)

print(f"\n{N - len(FAILS)}/{N} PASS")
sys.exit(1 if FAILS else 0)
