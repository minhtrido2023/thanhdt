"""Ghi dòng mốc chuỗi tier2 vào data/ PRODUCTION bằng writer của nhánh (chưa merge).
Chạy với JOB_ID đang đặt ⇒ chỉ đi được đường web_crosscheck_auto, đủ mọi guard."""
import json, os, sys
WT, PROD = sys.argv[1], "/home/trido/thanhdt/WorkingClaude/data/cctg_rate_vn_tier2_events.csv"
sys.path.insert(0, WT)
import append_cctg_rate as acr
assert os.path.dirname(os.path.abspath(acr.__file__)) == os.path.abspath(WT)
assert os.environ.get("JOB_ID"), "phải chạy dưới JOB_ID"
acr.CSV_PATH_TIER2 = PROD
VNN_2009 = "https://vietnamnet.vn/chung-chi-tien-gui-lai-suat-cao-hon-tiet-kiem-co-noi-niem-yet-9-nam-2553413.html"
BNA_2909 = "https://baonghean.vn/en/lai-suat-chung-chi-tien-gui-ky-han-3-thang-len-82-moi-nam-tai-cac-ngan-hang-ngay-2992026-10352363.html"
VNN_0810 = "https://baomoi.com/lai-suat-ngan-hang-hom-nay-8-10-2026-co-1-trieu-cung-mua-duoc-chung-chi-tien-gui-c56220947.epi"
BNEWS_1310 = "https://bnews.vn/chung-chi-tien-gui-dua-lai-suat-hut-dong-tien/440292.html"
ROWS = [
 dict(bank="VPB", denom="100tr", product="CCTG Super Thịnh Vượng", holding="", rate=9.2,
      note="Menh gia 100tr: 9,2% - VietnamNet 08/10 (doc qua ban Baomoi) ghi dai 184-389 ngay; Bao Nghe An 29/09 ghi dai 4 thang-1 nam. "
           "Hai nguon KHOP so va menh gia nhung LECH dai nam giu => holding_period de trong. Anh app VPBank user gui 13/10 15:09 ICT: 'Loi suat len toi 9.2%/nam' "
           "(anh khong chung minh menh gia/dai nam giu). BNEWS 13/10 con ghi 9,0% (6 thang, tu 100tr) - lech 0,2pp, coi la so cu.",
      sources=[("VietnamNet (ban Baomoi)", VNN_0810, "2026-10-08"), ("Bao Nghe An", BNA_2909, "2026-09-29")]),
 dict(bank="MB", denom=None, product="CCTG MB (nguon khong neu ten san pham)", holding="6-9 tháng", rate=7.1,
      note="MB 6-9 thang 7,1% (cao nhat <=12 thang o bac mua thong thuong). Bao Nghe An 29/09: mua toi thieu 200.000d; bac lon (tu 1 ty 6T 9,1%, tu 10 ty 9,2%) "
           "chi 1 nguon, KHONG phai muc cua chuoi. Nguon khong chia menh gia 10tr/100tr => denomination trong.",
      sources=[("VietnamNet", VNN_2009, "2026-09-20"), ("Bao Nghe An", BNA_2909, "2026-09-29")]),
 dict(bank="ACB", denom=None, product="CCTG ACB (nguon khong neu ten san pham)", holding="3 tháng", rate=7.2,
      note="ACB CCTG 3 thang 7,2% (2 nguon). VietnamNet 20/09 ghi them 6 thang cung 7,2% (1 nguon). Menh gia khong nguon nao neu trong 35 ngay "
           "(VnExpress 24/07: tu 10 trieu - qua cu) => denomination trong.",
      sources=[("VietnamNet", VNN_2009, "2026-09-20"), ("BNEWS/TTXVN", BNEWS_1310, "2026-10-13")]),
]
from datetime import datetime
from zoneinfo import ZoneInfo
today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
for r in ROWS:
    argv = ["--series", "tier2", "--bank", r["bank"], "--product", r["product"], "--rate", str(r["rate"]),
            "--effective", today, "--source", "web_crosscheck_auto", "--collected", today, "--note", r["note"],
            "--sources", json.dumps([{"publisher": p, "url": u, "date": d, "rate": r["rate"]} for p, u, d in r["sources"]])]
    if r["denom"]:
        argv += ["--denom", r["denom"]]
    if r["holding"]:
        argv += ["--holding", r["holding"]]
    sys.argv = ["append_cctg_rate.py"] + argv
    try:
        print(r["bank"], "rc=", acr.main() or 0)
    except SystemExit as e:
        print(r["bank"], "REFUSED:", e.code)
