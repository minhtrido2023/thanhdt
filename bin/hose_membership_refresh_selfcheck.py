#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck KHÉP KÍN cho `hose_membership_refresh.py` (N-d vòng 2): số mã HOSE đổi > 5% so với `_latest`
⇒ rc=2, KHÔNG ghi đè; `--accept-count-change` ⇒ ghi; file tạm cũ bị dọn, file tạm mới giữ; ghi lỗi giữa
chừng không để lại `.tmp`. Chỉ chạy offline (`--from-files`) trong thư mục tạm — không mạng, không BQ,
không ghi `data/`.

    env -u TZ python3 mike/bin/hose_membership_refresh_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/hose_membership_refresh_selfcheck.py
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd  # noqa: E402

import hose_membership_refresh as H  # noqa: E402

N_OK = 0


def ok(cond, msg):
    global N_OK
    if not cond:
        raise AssertionError(msg)
    N_OK += 1


def files(d, n_hose):
    fl = {"HOSE": [{"code": f"H{i:03d}", "status": "listed", "listedDate": "2010-01-01"} for i in range(n_hose)],
          "HNX": [], "UPCOM": []}
    for k, v in fl.items():
        with open(os.path.join(d, f"vndirect_stocks_{k}.json"), "w") as f:
            json.dump({"data": v}, f)
    pd.DataFrame({"ticker": ["Z"], "event_code": ["DIV"], "effective_date": ["2020-01-01"],
                  "event_title_vi": [""]}).to_parquet(os.path.join(d, "ca.parquet"))
    pd.DataFrame({"time": pd.to_datetime(["2014-01-02"]), "ticker": ["H000"]}).to_parquet(
        os.path.join(d, "panel.parquet"))


def run(src, out, vintage, *extra):
    argv = ["--from-files", src, "--ca-parquet", os.path.join(src, "ca.parquet"), "--panel-parquet",
            os.path.join(src, "panel.parquet"), "--out-dir", out, "--vintage", vintage, *extra]
    e = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(e):
        rc = H.main(argv)
    return rc, e.getvalue()


def n_latest(out):
    return len(json.load(open(os.path.join(out, "hose_membership_latest.json")))["hose_now"])


def main() -> int:
    src, out = tempfile.mkdtemp(prefix="hmr_src_"), tempfile.mkdtemp(prefix="hmr_out_")
    files(src, 100)
    rc, _ = run(src, out, "2030-01-05")
    ok(rc == 0 and n_latest(out) == 100, f"lần đầu (chưa có _latest) ghi: rc={rc}")

    files(src, 105)                                   # +5 = đúng 5% ⇒ hợp lý
    rc, _ = run(src, out, "2030-01-12")
    ok(rc == 0 and n_latest(out) == 105, f"+5% ⇒ ghi: rc={rc}")

    files(src, 60)                                    # nguồn trả thiếu
    rc, err = run(src, out, "2030-01-19")
    ok(rc == 2 and "105 → 2030-01-19 = 60" in err and "KHÔNG ghi" in err, f"−43% ⇒ rc=2 + lý do: {rc} {err}")
    ok(n_latest(out) == 105 and not os.path.exists(os.path.join(out, "hose_membership_2030-01-19.json")),
       "−43% ⇒ _latest + bản theo ngày KHÔNG bị ghi")
    rc, _ = run(src, out, "2030-01-19", "--accept-count-change")
    ok(rc == 0 and n_latest(out) == 60, "--accept-count-change ⇒ ghi")

    # file tạm: cũ > 1 giờ bị dọn, mới giữ nguyên (có thể là lần chạy song song đang ghi)
    old_t = os.path.join(out, "hose_membership_latest.json.tmp.111")
    new_t = os.path.join(out, "hose_membership_latest.json.tmp.222")
    for p in (old_t, new_t):
        open(p, "w").close()
    os.utime(old_t, (time.time() - 7200, time.time() - 7200))
    rc, err = run(src, out, "2030-01-26")
    ok(rc == 0 and not os.path.exists(old_t) and os.path.exists(new_t) and "tmp.111" in err,
       f"dọn tmp cũ, giữ tmp mới: {os.listdir(out)} {err}")

    # ghi lỗi giữa chừng (đối tượng không JSON được) ⇒ không để lại .tmp.<pid>
    bad = os.path.join(out, "x.json")
    try:
        H._atomic_json(bad, {"k": object()})
        ok(False, "phải TypeError")
    except TypeError:
        pass
    ok(not os.path.exists(f"{bad}.tmp.{os.getpid()}") and not os.path.exists(bad), "lỗi ghi ⇒ không còn .tmp")

    ok(H.implausible({}, {"hose_now": []}) is None, "chưa có _latest ⇒ không chặn")
    print(f"OK — {N_OK} assertion PASS (hose_membership_refresh_selfcheck.py, TZ={os.environ.get('TZ')!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
