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

# ── FIXTURE ĐÓNG BĂNG (2026-08-08) ─────────────────────────────────────────────────────────
# Bài test này dựng lại MỘT kịch bản lịch sử cố định (2026-07-20). Bản đầu đọc thẳng 2 nguồn
# SỐNG và cả hai đều đã trôi, làm 3 assert đỏ mà production KHÔNG hề sai:
#   • `tav2_bq.ticker_prune` bị TRUNCATE+rebuild mỗi ngày ⇒ rổ của một ngày QUÁ KHỨ đổi theo
#     thời gian (A1: 200+ mã lúc viết → 189 hôm nay). Cùng lớp với sự cố "58 mã rụng lặng lẽ".
#   • `data/anomaly_flags.json` là file SỐNG: cờ PNJ của 07/2026 đã bị một alert MỚI
#     (last_alert=2026-08-05) ghi đè, nên tại 2026-07-20 gate đúng ra phải KHÔNG loại PNJ
#     (chống look-ahead — production đang chạy ĐÚNG). A4/B1 đỏ vì fixture cũ, không phải bug.
# ⇒ đóng băng CẢ HAI đầu vào (coding_guidelines §23 hệ luận 1). Snapshot BQ nằm ở
# data/fixtures/…csv; cờ để inline ngay đây để đọc kịch bản là thấy ngay.
SNAP_FIXTURE = os.path.join(W, "data", "fixtures", "anomaly_gate_capit_snapshot_20260720.csv")
SNAP_N_RAW = 218          # số dòng fixture (trước lọc thanh khoản)
SNAP_N_LIQ = 189          # sau liq_bn>=2 & Close>0
FLAGS_FIXTURE = {         # trạng thái cờ ĐÚNG NHƯ LÚC diễn ra kịch bản 2026-07-20
    "PNJ": {"last_alert": "2026-07-14", "tier": "H", "reasons": "IDIOCRASH,VOLSPIKE",
            "ret": -6.9, "idio": -7.1, "vol_x": 3.1},
    "LPB": {"last_alert": "2026-06-24", "tier": "H", "reasons": "VOLSPIKE",
            "ret": 5.51, "idio": 5.03, "vol_x": 5.99},
}

import anomaly_gate
from anomaly_gate import anomaly_excluded

# Trỏ gate vào WORKDIR giả chứa fixture cờ — mọi assert của kịch bản chạy trên đầu vào đóng
# băng. (Các nhánh fail-safe B5-B8 tự trỏ sang WORKDIR tạm riêng của chúng, không đụng cái này.)
_REAL_WORKDIR = anomaly_gate.WORKDIR
_FIX_DIR = tempfile.mkdtemp(prefix="anomaly_fixture_")
os.makedirs(os.path.join(_FIX_DIR, "data"))
json.dump(FLAGS_FIXTURE, open(os.path.join(_FIX_DIR, "data", "anomaly_flags.json"), "w"))
anomaly_gate.WORKDIR = _FIX_DIR

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


SNAP_SQL = """SELECT p.ticker, p.Close, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pb_z,
             p.ROE_Min5Y, p.ROIC5Y, p.FSCORE,
             COALESCE(p.Price,p.Close)*p.Volume/1e9 liq_bn
      FROM tav2_bq.ticker_prune p WHERE p.time=DATE '{day}'"""


def _select(snap):
    """Bước chọn rổ của pt_capitulation_shadow SAU fix — LOGIC đang được test."""
    snap = snap.copy()
    snap["q"] = (snap.ROE_Min5Y >= 0.12) & (snap.ROIC5Y >= 0.10) & (snap.FSCORE >= 6)
    snap = snap[(snap.liq_bn >= 2) & snap.Close.gt(0)]
    return snap, snap[snap.q]


def capit_pool(day):
    """Như trên nhưng lấy snapshot SỐNG từ BQ (chỉ dùng cho nhánh đối chứng A6)."""
    return _select(bq(SNAP_SQL.format(day=day)))


print("== A. date-desync fix (kịch bản cố định 2026-07-20, snapshot ĐÓNG BĂNG) ==")
_raw = pd.read_csv(SNAP_FIXTURE)
snap, q = _select(_raw)
chk("A1 fixture snapshot nguyên vẹn (không bị cắt/ghi đè)",
    len(_raw) == SNAP_N_RAW and len(snap) == SNAP_N_LIQ
    and {"ticker", "Close", "pb_z", "ROE_Min5Y", "ROIC5Y", "FSCORE", "liq_bn"} <= set(_raw.columns),
    f"(raw={len(_raw)}/{SNAP_N_RAW}, sau liq>=2B={len(snap)}/{SNAP_N_LIQ})")
# Thông tin, KHÔNG phải assert: ticker_prune rebuild mỗi ngày nên rổ của ngày quá khứ trôi.
# Đây là vấn đề CHẤT LƯỢNG DỮ LIỆU đã biết (dự án universe_pit), không phải việc của bài test này.
try:
    _live_n = len(capit_pool(SIG_DATE)[0])
    print(f"  INFO  ticker_prune SỐNG tại {SIG_DATE} hôm nay: {_live_n} mã sau lọc "
          f"(fixture đóng băng 2026-08-08: {SNAP_N_LIQ}) — chênh = data drift, không phải lỗi code")
except Exception as _ex:
    print(f"  INFO  không đọc được ticker_prune sống ({_ex}) — bỏ qua, fixture vẫn đủ chạy")
chk("A2 quality gate ra pool >=3 tên", len(q) >= 3, f"(n={len(q)}: {sorted(q.ticker)})")

excl = anomaly_excluded(SIG_DATE)
g = q[q.pb_z < -1]
g_gated = g[~g.ticker.isin(excl)]
chk("A3 pb_z<-1 trước gate gồm PNJ", "PNJ" in set(g.ticker), f"({sorted(g.ticker)})")
chk("A4 rổ sau due-diligence == kỳ vọng", set(g_gated.ticker) == EXPECT,
    f"({sorted(g_gated.ticker)} vs {sorted(EXPECT)})")
chk("A5 rổ >=3 tên → KHÔNG còn '<3 eligible names'", len(g_gated) >= 3, f"(n={len(g_gated)})")

# A6 — ĐỐI CHỨNG SỐNG, cố ý không đóng băng: bản CŨ tự query MAX(time) riêng nên rơi vào ngày
# partial. "Ngày mới nhất có bị thiếu settle không" là TRẠNG THÁI SỐNG của bảng, không phải tính
# chất của code ta ⇒ không tái hiện được thì SKIP, không FAIL (nội dung regression thật nằm ở
# A2-A5 trên fixture). Cũng SKIP khi BQ không sẵn sàng — bài test vẫn chạy offline được.
try:
    mx = str(bq("SELECT MAX(time) mt FROM tav2_bq.ticker_prune").iloc[0]["mt"])
    if mx == SIG_DATE:
        print(f"  SKIP  A6 — MAX(time) trùng ngày tín hiệu ({mx}), không tái hiện được desync")
    else:
        snap_old, q_old = capit_pool(mx)
        if len(q_old) < len(q):
            chk("A6 bản CŨ (MAX(time)) thật sự hỏng khi lệch ngày", True,
                f"(MAX(time)={mx}: {len(snap_old)} mã → pool {len(q_old)} vs ngày tín hiệu {len(q)})")
        else:
            print(f"  SKIP  A6 — MAX(time)={mx} hôm nay KHÔNG partial (pool {len(q_old)} ≥ "
                  f"{len(q)}); desync không tái hiện được bằng dữ liệu sống")
except Exception as _ex:
    print(f"  SKIP  A6 — không truy vấn được BQ ({_ex})")

print("== B. due-diligence gate (module dùng chung) ==")
flags = FLAGS_FIXTURE      # kịch bản đóng băng, KHÔNG đọc data/anomaly_flags.json sống
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

print("== D. bản dùng chung khớp bản inline production (PRE-PATCH, ghim git rev) ==")
# golive_recommend_v23.py từ 2026-07-21 (job Taylor_20260721_092529 + Mike áp patch) đã
# delegate sang anomaly_gate.py — không còn bản inline độc lập để so (exec thân hàm hiện
# tại sẽ NameError vì _anomaly_excluded_shared không có trong ns). Ghim về commit NGAY
# TRƯỚC lần refactor đó (569bdca) để bài test vẫn chạy được và còn giá trị regression.
PINNED_REV = "569bdca742b55a13314df4c83108b059ec14e543"
_o = subprocess.run(["git", "show", f"{PINNED_REV}:WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py"],
                     cwd=W, capture_output=True, text=True)
if _o.returncode != 0:
    raise RuntimeError(f"không đọc được rev ghim {PINNED_REV}: {_o.stderr}")
src = _o.stdout
# WORKDIR = fixture dir: cả 2 bản phải đọc CÙNG file cờ thì so sánh mới có nghĩa.
ns = {"os": os, "json": json, "pd": pd, "WORKDIR": _FIX_DIR, "ANOMALY_TTL_DAYS": 30}
exec("from datetime import timedelta\n" + src[src.index("def anomaly_excluded"):
                                              src.index("def capit_adv_caps")], ns)
prod = ns["anomaly_excluded"]
same = all(prod(d) == anomaly_excluded(d) for d in
           [SIG_DATE, "2025-12-01", "2026-07-01", "2026-06-24", "2026-08-30"])
chk("D1 2 bản trả kết quả giống nhau trên 5 ngày mẫu (pre-patch pinned vs shared)", same)

print(f"\n{ok} PASS / {fail} FAIL")
sys.exit(1 if fail else 0)
