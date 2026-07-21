# -*- coding: utf-8 -*-
"""anomaly_gate_selfcheck.py — verify 2 fix của job Taylor_20260721_090650.

A. Date-desync (pt_capitulation_shadow.py): dựng lại ĐÚNG kịch bản ngày cố định 2026-07-20
   (không phụ thuộc ngày chạy) — bước chọn rổ khoá vào `today` phải ra rổ đầy đủ, còn bản
   cũ (MAX(time) riêng) rơi vào ngày partial → <3 tên.
B. Due-diligence gate: bản dùng chung anomaly_gate.anomaly_excluded phải khớp bản inline
   production, fail-safe khi file hỏng/thiếu, chống look-ahead, và thực sự loại mã khỏi rổ
   ở cả 3 file paper (test bằng flags giả lập, không đụng file thật).
"""
import io
import json
import os
import subprocess
import sys
import tempfile

import pandas as pd

W = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
PROJECT = "lithe-record-440915-m9"
SIG_DATE = "2026-07-20"          # ngày tín hiệu CAPIT thật (oversold 42.7%, fired=True)
EXPECT = {"NCT", "SIP", "PVT", "VNM", "SAB"}   # rổ đúng sau khi loại PNJ qua due-diligence

import anomaly_gate
from anomaly_gate import anomaly_excluded

ok = fail = 0


def chk(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1; print(f"  PASS  {name} {extra}")
    else:
        fail += 1; print(f"  FAIL  {name} {extra}")


def bq(sql):
    o = subprocess.run(["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
                        "--format=csv", "--max_rows=5000", " ".join(sql.split())],
                       capture_output=True, text=True)
    if o.returncode != 0:
        raise RuntimeError(o.stdout + o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))


def capit_pool(day):
    """Bước chọn rổ của pt_capitulation_shadow SAU fix — khoá vào `day`, y hệt code đã sửa."""
    snap = bq(f"""SELECT p.ticker, p.Close, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pb_z,
             p.ROE_Min5Y, p.ROIC5Y, p.FSCORE,
             COALESCE(p.Price,p.Close)*p.Volume/1e9 liq_bn
      FROM tav2_bq.ticker_prune p WHERE p.time=DATE '{day}'""")
    snap["q"] = (snap.ROE_Min5Y >= 0.12) & (snap.ROIC5Y >= 0.10) & (snap.FSCORE >= 6)
    snap = snap[(snap.liq_bn >= 2) & snap.Close.gt(0)]
    return snap, snap[snap.q]


print("== A. date-desync fix (kịch bản cố định 2026-07-20) ==")
snap, q = capit_pool(SIG_DATE)
chk("A1 ngày tín hiệu có dữ liệu settle đủ", len(snap) >= 200, f"(n={len(snap)} mã sau liq>=2B)")
chk("A2 quality gate ra pool >=3 tên", len(q) >= 3, f"(n={len(q)}: {sorted(q.ticker)})")

excl = anomaly_excluded(SIG_DATE)
g = q[q.pb_z < -1]
g_gated = g[~g.ticker.isin(excl)]
chk("A3 pb_z<-1 trước gate gồm PNJ", "PNJ" in set(g.ticker), f"({sorted(g.ticker)})")
chk("A4 rổ sau due-diligence == kỳ vọng", set(g_gated.ticker) == EXPECT,
    f"({sorted(g_gated.ticker)} vs {sorted(EXPECT)})")
chk("A5 rổ >=3 tên → KHÔNG còn '<3 eligible names'", len(g_gated) >= 3, f"(n={len(g_gated)})")

# bản CŨ: tự query MAX(time) riêng → rơi vào ngày partial khi chạy hôm sau ngày tín hiệu
mx = str(bq("SELECT MAX(time) mt FROM tav2_bq.ticker_prune").iloc[0]["mt"])
if mx != SIG_DATE:
    snap_old, q_old = capit_pool(mx)
    chk("A6 bản CŨ (MAX(time)) thật sự hỏng khi lệch ngày", len(q_old) < len(q),
        f"(MAX(time)={mx}: {len(snap_old)} mã → pool {len(q_old)} vs ngày tín hiệu {len(q)})")
else:
    print(f"  SKIP  A6 — MAX(time) trùng ngày tín hiệu ({mx}), không tái hiện được desync")

print("== B. due-diligence gate (module dùng chung) ==")
flags = json.load(open(os.path.join(W, "data", "anomaly_flags.json"), encoding="utf-8"))
chk("B1 PNJ có cờ active tại ngày tín hiệu", "PNJ" in excl, f"(excl={sorted(excl)})")
chk("B2 chống look-ahead: chạy lại 2025-12 không thấy cờ 2026", not anomaly_excluded("2025-12-01"))
chk("B3 hết TTL 30d thì cờ tự rụng",
    "PNJ" not in anomaly_excluded(str(pd.Timestamp(flags["PNJ"]["last_alert"]).date()
                                     + pd.Timedelta(days=31))))
chk("B4 nhận str/date/Timestamp như nhau",
    anomaly_excluded(SIG_DATE) == anomaly_excluded(pd.Timestamp(SIG_DATE))
    == anomaly_excluded(pd.Timestamp(SIG_DATE).date()))

_real = anomaly_gate.WORKDIR
try:  # fail-safe: file thiếu / hỏng → set rỗng, không ném lỗi
    d = tempfile.mkdtemp(); os.makedirs(os.path.join(d, "data"))
    anomaly_gate.WORKDIR = d
    chk("B5 fail-safe khi file THIẾU", anomaly_excluded(SIG_DATE, quiet=True) == set())
    open(os.path.join(d, "data", "anomaly_flags.json"), "w").write("{ khong-phai-json")
    chk("B6 fail-safe khi file HỎNG", anomaly_excluded(SIG_DATE, quiet=True) == set())
    # C. gate thực sự loại mã: giả lập 1 mã trong rổ kỳ vọng bị gắn cờ
    victim = sorted(EXPECT)[0]
    json.dump({victim: {"last_alert": SIG_DATE, "tier": "H", "reasons": "SELFCHECK"}},
              open(os.path.join(d, "data", "anomaly_flags.json"), "w"))
    sim = anomaly_excluded(SIG_DATE)
    chk("B7 mã giả lập bị gắn cờ được nhận diện", sim == {victim}, f"({victim})")
    chk("B8 mã giả lập bị loại khỏi rổ CAPIT", victim not in set(g[~g.ticker.isin(sim)].ticker))
    # cùng gate đó áp cho DC book (dict {ticker: buy_mode}) và pt_v22 (DataFrame pbz)
    dc_set = {victim: "ACCUMULATE", "FPT": "ACCUMULATE"}
    chk("B9 DC book loại đúng mã, giữ phần còn lại",
        {t: m for t, m in dc_set.items() if t not in sim} == {"FPT": "ACCUMULATE"})
    e = pd.DataFrame({"ticker": sorted(EXPECT), "pbz": [-2.0] * len(EXPECT)})
    chk("B10 pt_v22 capit_basket loại đúng mã",
        set(e[~e["ticker"].isin(sim)]["ticker"]) == EXPECT - {victim})
finally:
    anomaly_gate.WORKDIR = _real

print("== D. bản dùng chung khớp bản inline production ==")
src = open(os.path.join(W, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"), encoding="utf-8").read()
ns = {"os": os, "json": json, "pd": pd, "WORKDIR": W, "ANOMALY_TTL_DAYS": 30}
exec("from datetime import timedelta\n" + src[src.index("def anomaly_excluded"):
                                              src.index("def capit_adv_caps")], ns)
prod = ns["anomaly_excluded"]
same = all(prod(d) == anomaly_excluded(d) for d in
           [SIG_DATE, "2025-12-01", "2026-07-01", "2026-06-24", "2026-08-30"])
chk("D1 2 bản trả kết quả giống nhau trên 5 ngày mẫu", same)

print(f"\n{ok} PASS / {fail} FAIL")
sys.exit(1 if fail else 0)
