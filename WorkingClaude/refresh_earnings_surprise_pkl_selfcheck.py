# -*- coding: utf-8 -*-
"""refresh_earnings_surprise_pkl_selfcheck.py — self-check cho refresh_earnings_surprise_pkl.py.

Offline (bq giả lập, pkl trong thư mục tạm) — KHÔNG đụng data/earnings_surprise_data.pkl thật.
`--live`: kéo BQ sống ra một pkl TẠM rồi cho `live_lag_candidates` đọc thử + so định dạng với pkl
production (chỉ đọc). `RESP_TARGET=<đường dẫn bản cần kiểm>` cho mutation test.
Chạy bằng $DNA_PYEXE (pandas 3 — pandas 2 không unpickle được pkl production).
"""
import importlib.util
import os
import pickle
import re
import sys
import tempfile

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.abspath(os.environ.get("RESP_TARGET") or os.path.join(HERE, "refresh_earnings_surprise_pkl.py"))
_spec = importlib.util.spec_from_file_location("resp_under_test", TARGET)
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


def raw_frame(n=200, last="2026-08-21", extra=()):
    """Khung giống thứ BQ trả: ngày dạng CHUỖI (đường bq CLI) — chính dạng đã làm nổ bản đầu."""
    rng = np.random.RandomState(7)
    rel = pd.date_range(end=last, periods=n, freq="D").strftime("%Y-%m-%d")
    d = {"ticker": [f"T{i % 40:02d}" for i in range(n)], "quarter": [f"2026Q{i % 4 + 1}" for i in range(n)],
         "time": list(rel), "Release_Date": list(rel)}
    for c in R.COLUMNS[4:]:
        d[c] = rng.randn(n)
    df = pd.DataFrame(d)
    for tk, q, r in extra:
        row = {c: 0.5 for c in R.COLUMNS[4:]}; row.update(ticker=tk, quarter=q, time=r, Release_Date=r)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    return df


class Box:
    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="resp_"); self.path = os.path.join(self.dir, "es.pkl"); self.logs = []
    def run(self, bq_fn):
        return R.refresh(bq_fn, self.path, out=self.logs.append)
    def bytes(self):
        with open(self.path, "rb") as f:
            return f.read()
    def load(self):
        with open(self.path, "rb") as f:
            return pickle.load(f)
    def tmps(self):
        return [f for f in os.listdir(self.dir) if f != "es.pkl"]


print("=" * 78); print("  1. đường thuận + idempotent"); print("=" * 78)
b = Box()
res, info = b.run(lambda sql: raw_frame())
check("1a chưa có pkl → updated", res == "updated" and info["new_rows"] == 200 and info["new_max"] == "2026-08-21", f"{res} {info}")
df = b.load()
check("1b pkl đọc lại được, đủ cột đúng thứ tự", list(df.columns) == R.COLUMNS and len(df) == 200)
check("1c kiểu: 2 cột ngày = datetime64[ns], ticker/quarter = object (như pkl 15:30)",
      str(df["Release_Date"].dtype) == "datetime64[ns]" and str(df["time"].dtype) == "datetime64[ns]"
      and df["ticker"].dtype == object and df["quarter"].dtype == object, f"{df.dtypes.to_dict()}")
check("1d không để lại file tạm", b.tmps() == [], f"{b.tmps()}")
m0, by0 = os.stat(b.path).st_mtime_ns, b.bytes()
res, info = b.run(lambda sql: raw_frame())
check("1e chạy lại cùng dữ liệu → unchanged, KHÔNG ghi (mtime + bytes giữ nguyên)",
      res == "unchanged" and os.stat(b.path).st_mtime_ns == m0 and b.bytes() == by0, res)
res, info = b.run(lambda sql: raw_frame(extra=[("KBC", "2026Q3", "2026-10-12")]))
df = b.load()
check("1f có sự kiện mới (KBC 2026Q3 release 10-12) → updated, pkl thấy đúng dòng đó",
      res == "updated" and info["old_max"] == "2026-08-21" and info["new_max"] == "2026-10-12" and len(df) == 201
      and ((df["ticker"] == "KBC") & (df["quarter"] == "2026Q3")).sum() == 1, f"{res} {info}")
seen = []
b2 = Box(); b2.run(lambda sql: (seen.append(sql), raw_frame())[1])
check("1g truy vấn đúng 1 lần, đúng SQL hằng số", seen == [R.SQL])
for kind, conv in (("datetime.date", lambda s: pd.Timestamp(s).date()), ("Timestamp[us]", lambda s: pd.Timestamp(s).as_unit("us"))):
    bx = Box(); f = raw_frame(); f["Release_Date"] = [conv(x) for x in f["Release_Date"]]; f["time"] = [conv(x) for x in f["time"]]
    res, _ = bx.run(lambda sql, f=f: f)
    check(f"1h ngày kiểu {kind} từ BQ → updated, vẫn ra datetime64[ns]",
          res == "updated" and str(bx.load()["Release_Date"].dtype) == "datetime64[ns]", res)

print("=" * 78); print("  2. thất bại → GIỮ pkl cũ (bytes y nguyên), có lý do thật"); print("=" * 78)
def _boom(sql):
    raise RuntimeError("bq: quota exceeded")
cases = [
    ("BQ raise", _boom, "quota exceeded"),
    ("0 dòng", lambda s: raw_frame().iloc[0:0], "0 dòng"),
    ("thiếu cột NP_P3", lambda s: raw_frame().drop(columns=["NP_P3"]), "thiếu cột ['NP_P3']"),
    ("thiếu cột Release_Date", lambda s: raw_frame().drop(columns=["Release_Date"]), "thiếu cột ['Release_Date']"),
    ("Release_Date toàn NULL", lambda s: raw_frame().assign(Release_Date=None), "toàn NaT"),
    ("trả None", lambda s: None, "DataFrame"),
    ("co lại 10%", lambda s: raw_frame().iloc[20:], "co lại"),
    ("max Release_Date lùi", lambda s: pd.concat([raw_frame(last="2026-08-10"), raw_frame(last="2026-08-10").iloc[:5]]), "lùi"),
    ("Release_Date toàn rác", lambda s: raw_frame().assign(Release_Date="không-phải-ngày"), ""),
]
for nm, fn, kw in cases:
    bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes(); bx.logs.clear()
    try:
        res, info = bx.run(fn); raised = False
    except Exception as ex:
        res, info, raised = f"RAISED {ex}", {}, True
    check(f"2 {nm} → kept_old, pkl cũ nguyên vẹn, không raise, không file tạm",
          res == "kept_old" and not raised and bx.bytes() == by and bx.tmps() == [], f"{res} {info}")
    check(f"2 {nm} → lý do thật có trong info + log", kw in info.get("reason", "") and any(kw in l for l in bx.logs) and info.get("reason"),
          f"{info.get('reason')} | {bx.logs}")
bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes()
res, _ = bx.run(lambda s: raw_frame().iloc[3:])   # co 1,5% < 2% ⇒ chấp nhận (restate nhỏ)
check("2i co lại 1,5% (dưới ngưỡng 2%) → vẫn updated", res == "updated" and len(bx.load()) == 197, res)
bx = Box()
res, info = bx.run(_boom)
check("2j chưa có pkl + BQ lỗi → kept_old, KHÔNG tạo pkl rỗng", res == "kept_old" and not os.path.exists(bx.path), res)

print("=" * 78); print("  3. bị kill giữa chừng / ghi nguyên tử"); print("=" * 78)
bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes()
new = lambda sql: raw_frame(extra=[("KBC", "2026Q3", "2026-10-12")])
_rep = os.replace
def _kill_replace(a, c):
    raise KeyboardInterrupt("timeout giết tiến trình ngay trước os.replace")
os.replace = _kill_replace
try:
    bx.run(new); killed = False
except KeyboardInterrupt:
    killed = True
finally:
    os.replace = _rep
check("3a kill ngay trước os.replace → pkl cũ nguyên vẹn + đọc được; còn file tạm mồ côi",
      killed and bx.bytes() == by and len(bx.load()) == 200 and len(bx.tmps()) == 1, f"killed={killed} {bx.tmps()}")
with open(bx.path + ".tmp.999999", "wb") as f:      # file tạm của một tiến trình KHÁC đã chết (pid khác)
    f.write(b"rac")
res, _ = bx.run(new)
check("3b lượt sau: dọn file tạm mồ côi (kể cả của pid khác), cập nhật bình thường",
      res == "updated" and bx.tmps() == [] and len(bx.load()) == 201, f"{res} {bx.tmps()}")
bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes()
_ld = R._load
R._load = lambda path: _ld(path).iloc[:-7] if ".tmp." in path else _ld(path)   # file tạm đọc lại bị hụt dòng
try:
    res, info = bx.run(new)
finally:
    R._load = _ld
check("3b2 đọc lại file tạm lệch số dòng → kept_old, pkl cũ nguyên vẹn, file tạm bị xoá",
      res == "kept_old" and "lệch số dòng" in info.get("reason", "") and bx.bytes() == by and bx.tmps() == [], f"{res} {info} {bx.tmps()}")
bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes()
_dump = pickle.dump
def _half_dump(obj, f, *a, **k):
    f.write(b"\x80\x05half-written"); raise KeyboardInterrupt("kill giữa lúc dump")
R.pickle.dump = _half_dump
try:
    bx.run(new); killed = False
except KeyboardInterrupt:
    killed = True
finally:
    R.pickle.dump = _dump
check("3c kill GIỮA lúc dump → pkl thật không hề bị chạm (rác chỉ nằm ở file tạm)", killed and bx.bytes() == by and len(bx.load()) == 200)
bx = Box(); bx.run(lambda sql: raw_frame()); by = bx.bytes()
def _oserr(a, c):
    raise OSError("đĩa đầy")
os.replace = _oserr
try:
    res, info = bx.run(new)
finally:
    os.replace = _rep
check("3d os.replace lỗi thường → kept_old + lý do, pkl cũ nguyên vẹn", res == "kept_old" and "đĩa đầy" in info.get("reason", "") and bx.bytes() == by, f"{res} {info}")
bx = Box()
with open(bx.path, "wb") as f:
    f.write(b"khong phai pickle")
res, info = bx.run(lambda sql: raw_frame())
check("3e pkl cũ HỎNG → thay bằng bản mới hợp lệ (có log nêu lỗi đọc)", res == "updated" and len(bx.load()) == 200 and any("KHÔNG đọc được" in l for l in bx.logs), f"{res} {bx.logs}")
bx = Box()
with open(bx.path, "wb") as f:
    f.write(b"khong phai pickle")
by = bx.bytes(); res, _ = bx.run(_boom)
check("3f pkl cũ hỏng + BQ lỗi → kept_old, không xoá file cũ", res == "kept_old" and bx.bytes() == by, res)
src = open(TARGET, encoding="utf-8").read()
check("3g nguồn: ghi qua file tạm cùng thư mục + fsync + os.replace; không mở thẳng pkl đích để ghi",
      'tmp = f"{path}.tmp.{os.getpid()}"' in src and "os.fsync(" in src and "os.replace(tmp, path)" in src
      and src.count('"wb"') == 1 and 'open(tmp, "wb")' in src)

print("=" * 78); print("  4. BQ SỐNG + trùng SQL với bước [3] gốc"); print("=" * 78)
os.environ["BQ_LOCAL_CACHE"] = "data/bq_cache"; os.environ["LOCAL_SNAPSHOT_DIR"] = "/x"
_mods = {k: sys.modules.pop(k) for k in list(sys.modules) if k == "simulate_holistic_nav"}
fake = type(sys)("simulate_holistic_nav"); fake.bq = lambda sql: "FAKE"; fake.seen_env = None
sys.modules["simulate_holistic_nav"] = fake
try:
    got = R.live_bq()
    check("4a live_bq(): gỡ BQ_LOCAL_CACHE + LOCAL_SNAPSHOT_DIR trước khi lấy accessor",
          "BQ_LOCAL_CACHE" not in os.environ and "LOCAL_SNAPSHOT_DIR" not in os.environ and got is fake.bq)
finally:
    sys.modules.pop("simulate_holistic_nav", None); sys.modules.update(_mods)
    os.environ.pop("BQ_LOCAL_CACHE", None); os.environ.pop("LOCAL_SNAPSHOT_DIR", None)
i_pop, i_imp = src.find('os.environ.pop("BQ_LOCAL_CACHE", None)'), src.find("from simulate_holistic_nav import bq")
check("4b nguồn: gỡ cache TRƯỚC dòng import simulate_holistic_nav", 0 < i_pop < i_imp, f"{i_pop} {i_imp}")
orig = open(os.path.join(HERE, "refresh_lagged_caches.py"), encoding="utf-8").read()
m = re.search(r'\[3\] earnings_surprise_data\.pkl.*?fin = bq\("""(.*?)"""\)', orig, re.S)
norm = lambda s: " ".join(s.split())
check("4c SQL trùng nguyên văn bước [3] của refresh_lagged_caches.py (so sau khi chuẩn hoá khoảng trắng)",
      m is not None and norm(m.group(1)) == norm(R.SQL), "SQL đã lệch nhau — pkl 15:30 và 19:00 sẽ khác tập sự kiện")
check("4d COLUMNS khớp danh sách cột trong SQL",
      [c.strip().replace("f.", "") for c in norm(R.SQL).split(" FROM ")[0].replace("SELECT ", "").split(",")] == R.COLUMNS)

print("=" * 78); print("  5. main(): mã thoát"); print("=" * 78)
_live, _argv = R.live_bq, sys.argv
try:
    bx = Box(); sys.argv = ["x", "--out", bx.path]
    R.live_bq = lambda: (lambda sql: raw_frame())
    check("5a updated → exit 0", R.main() == 0 and os.path.exists(bx.path))
    check("5b unchanged → exit 0", R.main() == 0)
    R.live_bq = lambda: _boom
    check("5c kept_old → exit 1 (caller WARN, không chặn)", R.main() == 1)
    def _noacc():
        raise ImportError("simulate_holistic_nav hỏng")
    R.live_bq = _noacc
    check("5d không nạp được accessor → exit 1, không raise", R.main() == 1)
finally:
    R.live_bq, sys.argv = _live, _argv

if "--live" in sys.argv:
    print("=" * 78); print("  6. LIVE (BQ sống → pkl TẠM; pkl production chỉ ĐỌC)"); print("=" * 78)
    import hashlib, time
    prod = os.environ.get("RESP_PROD_PKL") or "/home/trido/thanhdt/WorkingClaude/data/earnings_surprise_data.pkl"
    md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
    before = md5(prod)
    bx = Box()
    with open(prod, "rb") as fsrc, open(bx.path, "wb") as fdst:
        fdst.write(fsrc.read())
    t0 = time.monotonic(); res, info = bx.run(R.live_bq()); dt = time.monotonic() - t0
    print(f"    {res} {info} ({dt:.1f}s)")
    check("6a kéo BQ sống: updated|unchanged, không kept_old", res in ("updated", "unchanged"), f"{res} {info}")
    new, old = bx.load(), pickle.load(open(prod, "rb"))
    check("6b định dạng trùng pkl production (cột + dtype)", list(new.columns) == list(old.columns) and (new.dtypes == old.dtypes).all(),
          f"{new.dtypes.to_dict()}")
    check("6c không lùi: số dòng ≥ 98% và max Release_Date ≥ bản production",
          len(new) >= 0.98 * len(old) and new["Release_Date"].max() >= old["Release_Date"].max(), f"{len(new)} vs {len(old)}")
    sys.path.insert(0, HERE)
    from lag_live_schedule import live_lag_candidates
    csv = os.path.join(os.path.dirname(prod), "earnings_events_classified.csv")
    c_new = live_lag_candidates(start="2026-06-15", pkl_path=bx.path, csv_path=csv)
    c_old = live_lag_candidates(start="2026-06-15", pkl_path=prod, csv_path=csv)
    k = ["ticker", "quarter"]
    merged = c_old.merge(c_new, on=k, how="left", suffixes=("_o", "_n"))
    check("6d live_lag_candidates đọc được pkl mới; mọi sự kiện cũ vẫn còn và qualify không đổi",
          merged["qualify_n"].notna().all() and (merged["qualify_o"] == merged["qualify_n"]).all(),
          f"{len(c_old)} cũ / {len(c_new)} mới")
    print(f"    sự kiện chỉ có ở pkl mới: {sorted(set(map(tuple, c_new[k].values)) - set(map(tuple, c_old[k].values)))}")
    check("6e pkl production KHÔNG bị chạm (md5 trước = sau)", md5(prod) == before)
    check("6f thời gian kéo < 120s", dt < 120, f"{dt:.1f}s")

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL   (target={TARGET})")
sys.exit(1 if FAIL else 0)
