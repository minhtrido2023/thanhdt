#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: giá BQ của verify_account_snapshot lấy theo phiên mới nhất CỦA TỪNG MÃ.

Chạy:  python3 mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py
       cd /tmp && env -i PATH=/usr/bin:/bin python3 <repo>/mike/bin/verify_account_snapshot_bq_price_date_selfcheck.py

Bug gốc (code-quality 2026-09-13, cùng lỗi compute_active_nav đã vá ở c9edd4c6): ngày giá =
MAX(time) của mã ĐẦU alphabet, áp cho cả danh mục ⇒ mã đó thiếu dòng phiên mới nhất thì mọi
mã khác bị MẤT giá ("WARN no BQ price") hoặc lấy giá cũ.

Test HÀNH VI, không so chuỗi SQL: gọi `bq_close_prices()` thật, chặn `subprocess.run` và chạy
đúng câu SQL module sinh ra trên DuckDB (có QUALIFY + subquery như BigQuery) với bảng giả.
CHỨNG MINH NGƯỢC: cùng fixture chạy bản TRƯỚC vá (blob git dd2c0d28) phải ra kết quả SAI.
"""
import importlib.util
import io
import json
import os
import subprocess
import sys
import types
from contextlib import redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import duckdb  # noqa: E402

import verify_account_snapshot as VAS  # noqa: E402

PRE_FIX_REF = "dd2c0d28"   # commit cuối của verify_account_snapshot.py trước bản vá
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


# AAA (đầu alphabet) THIẾU dòng 09-11 (ngừng GD/thiếu ingest); FPT, HPG đủ. Có dòng SAU asof
# (09-12) để kiểm lọc <= asof không bị hỏng.
FIXTURE = [("AAA", "2026-09-05", 9000.0), ("AAA", "2026-09-04", 8900.0),
           ("FPT", "2026-09-10", 72000.0), ("FPT", "2026-09-11", 72700.0),
           ("FPT", "2026-09-12", 99999.0),
           ("HPG", "2026-09-10", 21000.0), ("HPG", "2026-09-11", 21300.0)]


def fake_bq_run(cmd, **kw):
    """Chạy câu SQL (tham số cuối của lệnh bq) trên DuckDB, trả stdout JSON như `bq --format=json`."""
    sql = cmd[-1].replace("tav2_bq.ticker", "ticker")
    con = duckdb.connect()
    con.execute("CREATE TABLE ticker (ticker VARCHAR, time DATE, Close DOUBLE)")
    con.executemany("INSERT INTO ticker VALUES (?, ?, ?)", FIXTURE)
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, (str(v) if c == "time" else v for c, v in zip(cols, r))))
            for r in cur.fetchall()]
    return types.SimpleNamespace(returncode=0, stdout=json.dumps(rows), stderr="")


def run_prices(mod, tickers, asof):
    saved = mod.subprocess.run
    mod.subprocess.run = fake_bq_run
    err = io.StringIO()
    try:
        with redirect_stderr(err):
            prices, perr = mod.bq_close_prices(tickers, asof)
    finally:
        mod.subprocess.run = saved
    return prices, perr, err.getvalue()


def load_pre_fix():
    """Nạp bản TRƯỚC vá từ git thành module riêng (__file__ = đường thật để wc_paths neo đúng)."""
    src = subprocess.run(["git", "-C", HERE, "show", f"{PRE_FIX_REF}:bin/verify_account_snapshot.py"],
                         capture_output=True, text=True)
    if src.returncode != 0:
        return None, src.stderr.strip()
    spec = importlib.util.spec_from_loader("vas_pre_fix", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = os.path.join(HERE, "verify_account_snapshot.py")
    exec(compile(src.stdout, "vas_pre_fix", "exec"), mod.__dict__)
    return mod, None


print("[1] 1 mã (AAA, đầu alphabet) thiếu phiên mới nhất ⇒ mã khác vẫn lấy ĐÚNG ngày của mình")
px, perr, stderr = run_prices(VAS, ["HPG", "AAA", "FPT"], "2026-09-11")
check("không lỗi BQ", perr is None, perr)
check("FPT = 72.700 (phiên 09-11 của chính FPT, không phải 09-05 của AAA)",
      px and px.get("FPT") == 72700.0, px)
check("HPG = 21.300 (phiên 09-11)", px and px.get("HPG") == 21300.0, px)
check("AAA vẫn có giá = 9.000 (phiên gần nhất của CHÍNH AAA), không bị bỏ",
      px and px.get("AAA") == 9000.0, px)
check("dòng sau asof (FPT 09-12) KHÔNG bị lấy", px and px.get("FPT") != 99999.0, px)
check("stderr gọi tên AAA tụt ngày (2026-09-05)", "AAA" in stderr and "2026-09-05" in stderr,
      stderr.strip())

print("\n[2] mọi mã đủ phiên mới nhất ⇒ không cảnh báo (không đổi output ca bình thường)")
px, perr, stderr = run_prices(VAS, ["FPT", "HPG"], "2026-09-11")
check("FPT/HPG đúng giá 09-11", px == {"FPT": 72700.0, "HPG": 21300.0}, px)
check("stderr rỗng", stderr == "", stderr.strip())

print("\n[3] CHỨNG MINH NGƯỢC: bản trước vá trên cùng fixture PHẢI sai")
old, lerr = load_pre_fix()
check(f"nạp được bản trước vá ({PRE_FIX_REF})", old is not None, lerr)
if old is not None:
    opx, _, _ = run_prices(old, ["HPG", "AAA", "FPT"], "2026-09-11")
    check("bản cũ: ngày giá neo theo AAA (09-05) ⇒ FPT/HPG MẤT giá — bug tái lập được",
          opx is not None and "FPT" not in opx and "HPG" not in opx, opx)

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
