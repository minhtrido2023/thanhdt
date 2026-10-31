#!/usr/bin/env python3
"""R9/việc 3: đếm truy vấn BQ trên ĐƯỜNG PLAN 21:00 khi bật live: _dcf_check_for_order(tk, ref_price, asof) — KHÔNG
price_date (send_plan_report/eod_trading_report), KHÔNG prime cache. Đếm google.cloud.bigquery.Client.query (vá ở
mức client: mọi đường đi tới BQ đều qua nó) + số lời gọi oshares_dcf.oshares_for. corp_action_lib.bq đi qua `bq` CLI
(subprocess.run, timeout 300s) ⇒ đếm subprocess.run có argv[0] là bq. Truy vấn bị CHẶN (raise) để không chạm mạng/không
chờ timeout — chặn không đổi đếm vì đếm trước khi raise.
Dùng: python bq_calls_r9.py <dir_code_outer> <asof> <ticker...>"""
import os, sys, io, contextlib, json
code, asof, tks = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, code)
import dcf_valuation as dv
sys.path.insert(0, code)
import oshares_dcf as osd
import trading_bot.strategies as st
from google.cloud import bigquery
for m in (dv, osd, st):
    assert os.path.abspath(m.__file__).startswith(code + "/"), m.__file__
import subprocess
n = {"bq_query": 0, "bq_cli": 0, "oshares_for": 0}
_real_run = subprocess.run
def _run(args, *a, **k):
    if isinstance(args, (list, tuple)) and args and os.path.basename(str(args[0])) == "bq" or (isinstance(args, str) and args.lstrip().startswith("bq ")):
        n["bq_cli"] += 1
        raise RuntimeError("BQ CLI chặn (đếm)")
    return _real_run(args, *a, **k)
subprocess.run = _run
def _q(self, *a, **k):
    n["bq_query"] += 1
    raise RuntimeError("BQ chặn (đếm)")
bigquery.Client.query = _q
real = osd.oshares_for
def _osf(*a, **k):
    n["oshares_for"] += 1
    return real(*a, **k)
osd.oshares_for = _osf
dv.OSHARES_SOURCE = "live"
err = io.StringIO()
res = {}
with contextlib.redirect_stderr(err):
    for tk in tks:
        px = dv.latest_price(tk, asof)
        d = st._dcf_check_for_order(tk, px, asof)
        res[tk] = d.get("status")
print(json.dumps({"code": code, "asof": asof, "n_ticker": len(tks), **n, "status": res}, ensure_ascii=False))
