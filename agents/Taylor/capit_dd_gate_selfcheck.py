#!/usr/bin/env python3
"""
capit_dd_gate_selfcheck.py — self-check cho due-diligence gate của rổ CAPIT.
Job Taylor_20260720_081359. READ-ONLY với dữ liệu thật (BQ live), không đặt lệnh.

Kiểm 4 việc:
  A. Tiền đề: PNJ CÓ lọt qua bộ lọc chất lượng CAPIT (nếu không thì gate vô nghĩa).
  B. Gate loại đúng PNJ khỏi pool ứng viên với dữ liệu thật hôm nay.
  C. Regression: ngày KHÔNG có cờ nào active → rổ giống HỆT trước khi thêm gate.
  D. Fail-safe: file cờ thiếu / hỏng / rỗng → set rỗng, KHÔNG ném lỗi (pipeline chạy tiếp).

Hàm anomaly_excluded được TRÍCH TỪ CHÍNH golive_recommend_v23.py (AST), không copy lại —
tránh selfcheck trôi khỏi code thật đang chạy.
"""
import ast, json, os, sys, tempfile, datetime
from datetime import timedelta

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)   # đọc BQ LIVE như script thật
SRC = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_recommend_v23.py")
FLAGS = os.path.join(WORKDIR, "data", "anomaly_flags.json")

# ── trích hàm thật + hằng số TTL từ source production ──
# Từ 2026-07-21 (job Taylor_20260721_092529 + Mike áp patch), thân hàm production chỉ còn
# 1 dòng delegate sang anomaly_gate.anomaly_excluded (_anomaly_excluded_shared) — bơm đúng
# tên đó vào ns để AST-extract vẫn chạy được, và nhờ vậy test này giờ CÀNG sát code thật
# đang chạy (gọi thẳng qua module dùng chung, không còn 2 bản logic tách biệt để lệch).
tree = ast.parse(open(SRC, encoding="utf-8").read())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "anomaly_excluded")
ttl = next(n.value.value for n in tree.body
           if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "ANOMALY_TTL_DAYS")
import pandas as pd
from anomaly_gate import anomaly_excluded as _anomaly_excluded_shared
ns = {"os": os, "json": json, "timedelta": timedelta, "pd": pd,
      "WORKDIR": WORKDIR, "ANOMALY_TTL_DAYS": ttl,
      "_anomaly_excluded_shared": _anomaly_excluded_shared}
exec(compile(ast.Module([fn], []), SRC, "exec"), ns)
anomaly_excluded = ns["anomaly_excluded"]
print(f"# trích anomaly_excluded() từ {os.path.basename(SRC)} | TTL={ttl}d")

from simulate_holistic_nav import bq

CANDIDATE_SQL = """SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{d}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2"""


def pick_basket(e):
    """Sao đúng logic chọn rổ ở golive_recommend_v23.py (sau bước lọc gate)."""
    if e.empty:
        return []
    g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
    p = g if len(g) >= 3 else (c if len(c) >= 3 else e)
    p = p.nsmallest(15, "pbz") if len(p) > 15 else p
    return sorted(p["ticker"].tolist())


ok = True
# phiên HOÀN CHỈNH gần nhất — KHÔNG dùng MAX(time): ngày đang chạy có thể mới load vài mã
# (2026-07-20 lúc 15h chỉ có 2/262 dòng) → rổ ứng viên rỗng, selfcheck vô nghĩa.
sig = bq("""SELECT p.time d FROM tav2_bq.ticker_prune p
GROUP BY p.time HAVING COUNT(*) >= 100 ORDER BY p.time DESC LIMIT 1""")["d"].iloc[0]
sig = pd.Timestamp(sig).date()   # BQ trả date dạng chuỗi — chính chỗ này lộ ra nhu cầu chuẩn hoá
print(f"# phiên hoàn chỉnh gần nhất (BQ live): {sig}")

# ── A + B: pool thật hôm nay, trước vs sau gate ──
e = bq(CANDIDATE_SQL.format(d=sig))
excl = anomaly_excluded(sig)
before, after = pick_basket(e), pick_basket(e[~e["ticker"].isin(excl)])
in_pool = "PNJ" in set(e["ticker"])
print(f"\nA. PNJ lọt bộ lọc chất lượng CAPIT: {in_pool}"
      + (f" | pbz={float(e.set_index('ticker').loc['PNJ','pbz']):+.2f}" if in_pool else ""))
print(f"   cờ active ({len(excl)} mã): {sorted(excl)}")
print(f"B. rổ TRƯỚC gate ({len(before)}): {before}")
print(f"   rổ SAU  gate ({len(after)}): {after}")
if in_pool:
    a = "PNJ" in before and "PNJ" not in after
    print(f"   → PNJ có trong rổ trước & bị loại sau: {'PASS' if a else 'FAIL'}"); ok &= a
else:
    print("   → PNJ KHÔNG qua nổi bộ lọc chất lượng: gate không phải lớp chặn duy nhất (ghi nhận)")

# ── C: regression trên ngày không có cờ active ──
old = sig - datetime.timedelta(days=200)
eo = bq(CANDIDATE_SQL.format(d=old))
while eo.empty:                       # lùi qua ngày nghỉ
    old -= datetime.timedelta(days=1); eo = bq(CANDIDATE_SQL.format(d=old))
xo = anomaly_excluded(old)
same = pick_basket(eo) == pick_basket(eo[~eo["ticker"].isin(xo)])
print(f"\nC. regression {old} (cờ active: {len(xo)}) → rổ không đổi: {'PASS' if same else 'FAIL'}")
ok &= same
# C2 — chống look-ahead: mọi cờ hiện có đều thuộc 2026, ngày quá khứ này PHẢI thấy 0 cờ.
# (Nếu chỉ kiểm "rổ không đổi" thì test đậu do may — cờ tình cờ không nằm trong rổ hôm đó.)
print(f"C2. không cờ tương lai rò về {old}: {'PASS' if not xo else f'FAIL: {sorted(xo)}'}")
ok &= (not xo)

# ── D: fail-safe khi file cờ thiếu / hỏng / rỗng ──
print("\nD. fail-safe:")
# asof kiểu chuỗi (BQ trả date dạng str tuỳ driver) vẫn phải ra ĐÚNG set, không rơi vào except
s = anomaly_excluded(str(sig))
print(f"   asof là chuỗi '{sig}': {'PASS' if s == excl else 'FAIL (khác kết quả với date)'}")
ok &= (s == excl)
bak = FLAGS + ".selfcheck_bak"
os.rename(FLAGS, bak)
try:
    for label, content in [("thiếu file", None), ("JSON hỏng", "{not json"), ("rỗng", "{}")]:
        if content is None:
            if os.path.exists(FLAGS):
                os.remove(FLAGS)
        else:
            open(FLAGS, "w").write(content)
        try:
            r = anomaly_excluded(sig)
            p = (r == set())
        except Exception as ex:
            r, p = f"RAISED {ex}", False
        print(f"   {label}: {r} → {'PASS' if p else 'FAIL (phải trả set rỗng, không ném lỗi)'}")
        ok &= p
        if os.path.exists(FLAGS):
            os.remove(FLAGS)
finally:
    os.rename(bak, FLAGS)   # luôn khôi phục file thật

print("\nSELFCHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
