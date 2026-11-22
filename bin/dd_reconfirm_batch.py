#!/usr/bin/env python3
"""dd_reconfirm_batch — chạy bin/dd_skeptic_run.py (DD_GENERAL) cho 1 danh sách mã theo lô song song, GHI bảng tổng.

  python3 bin/dd_reconfirm_batch.py --tickers DCM,VLB,BSR [--workers 3] [--out <file.json>]

Mỗi mã: báo cáo = `source_file` của entry CUỐI trong kb/dd_price_zones.json; dir = thư mục chứa báo cáo
(`investor_report/` ⇒ thư mục cha; thư mục dùng chung nhiều mã `dd_dilution_update_*` ⇒ <dir>/<MÃ>).
KHÔNG sửa DD, KHÔNG ghi sổ: chỉ sinh <dir>/skeptic/rN.json qua dd_skeptic_run (script ghi). CONFIRMED ⇒ người gọi chạy
dd_ledger_append_confirmed.py --dry-run rồi --write. Bảng tổng ghi --out (mặc định logs/dd_reconfirm_batch_<UTC>.json) cập nhật SAU MỖI mã.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONES = os.path.join(ROOT, "kb", "dd_price_zones.json")
RUN = os.path.join(ROOT, "bin", "dd_skeptic_run.py")


def last_entry(t):
    es = [e for e in json.load(open(ZONES, encoding="utf-8"))["entries"] if e["ticker"] == t]
    return max(es, key=lambda e: (e["dd_date"], e["rev"])) if es else None


def dir_for(t, report_rel):
    d = os.path.dirname(report_rel)
    if os.path.basename(d) == "investor_report":
        d = os.path.dirname(d)
    if "dd_dilution_update" in d:
        d = os.path.join(d, t)
    return d


def one(t):
    e = last_entry(t)
    if not e or not e.get("source_file"):
        return {"ticker": t, "status": "SKIP", "why": "không có entry/source_file trong sổ"}
    rep = e["source_file"]
    if not os.path.isfile(os.path.join(ROOT, rep)):
        return {"ticker": t, "status": "SKIP", "why": "source_file không tồn tại: %s" % rep}
    d = dir_for(t, rep)
    os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    p = subprocess.run([sys.executable, RUN, "--dir", d, "--report", rep, "--mode", "DD_GENERAL"],
                       capture_output=True, text=True, cwd=ROOT)
    rec = {"ticker": t, "dir": d, "report": rep, "rc": p.returncode, "tail": (p.stdout + p.stderr).strip()[-300:]}
    if p.returncode == 0:
        sk = os.path.join(ROOT, d, "skeptic")
        n = max(int(f[1:-5]) for f in os.listdir(sk) if f.startswith("r") and f.endswith(".json") and f[1:-5].isdigit())
        j = json.load(open(os.path.join(sk, "r%d.json" % n), encoding="utf-8"))
        rec.update(status=j["verdict"], round=n, confidence=j.get("confidence"), cost_usd=j.get("cost_usd"),
                   verdict_path=os.path.join(d, "skeptic", "r%d.json" % n), summary=(j.get("summary") or "")[:400])
    else:
        rec["status"] = "ERROR"
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tickers", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    ts = [x.strip().upper() for x in a.tickers.split(",") if x.strip()]
    out = a.out or os.path.join(ROOT, "logs", "dd_reconfirm_batch_%s.json" % dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = []
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(one, ts):
            res.append(r)
            tmp = out + ".tmp"
            json.dump({"tickers": ts, "done": len(res), "results": res}, open(tmp, "w"), ensure_ascii=False, indent=1)
            os.replace(tmp, out)
            print("%s %s cost=%s" % (r["ticker"], r["status"], r.get("cost_usd")), flush=True)
    print("OUT", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
