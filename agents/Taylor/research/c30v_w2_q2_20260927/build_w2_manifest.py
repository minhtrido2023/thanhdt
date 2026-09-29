#!/usr/bin/env python3
"""Ghim HỌ TRIAL của W2/Q2 thành manifest bất biến — job Taylor_20260927_141318.

`dsr_family_manifest.py build` chỉ dựng họ bằng GLOB + mốc mtime, nên không diễn đạt được họ của
W2: đây là 10 cấu hình CỤ THỂ được so sánh VỚI NHAU khi chọn (5 phương tiện × 2 tầng proxy), không
phải "mọi CSV cũ hơn mốc X". Ghi thẳng theo ĐÚNG schema `manifest_version: 1` để
`dsr_pbo_annex.load_manifest()` fail-closed (thiếu file / md5 lệch ⇒ raise) vẫn hiệu lực y nguyên.
Đường dẫn lấy từ dòng engine TỰ IN trong log, không đoán từ env (§8).
"""
import datetime, hashlib, io, json, os, sys
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
LOGS = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs"
TAGS = [f"w2{k}_{t}" for t in ("baseline", "floor") for k in ("d", "a", "b", "c6", "c10")]

def md5_of(p, chunk=1 << 20):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

entries = []
for tag in TAGS:
    txt = io.open(f"{LOGS}/{tag}.log", encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: khong EXIT=0"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, (tag, hits)
    p = hits[0]
    s = load_nav(p)
    entries.append({"path": p, "md5": md5_of(p), "size": os.path.getsize(p),
                    "mtime_ict": datetime.datetime.fromtimestamp(os.path.getmtime(p), ICT).isoformat(),
                    "n_obs": 0 if s is None else int(len(s)), "reason": f"W2/Q2 leg {tag}"})
entries.sort(key=lambda e: e["path"])
man = {
 "_doc": "Ho trial CO DINH cho dsr_pbo_annex.py. KHONG sua tay.",
 "manifest_version": 1,
 "created_at_ict": datetime.datetime.now(ICT).isoformat(),
 "criterion": {"glob": "KHONG dung glob — liet ke tuong minh 10 chan W2/Q2",
   "mtime_before_ict": None, "min_obs": 0,
   "reason": "Ho trial DUNG nghia Bailey-Borwein-LdP-Zhu 2017 = tap cau hinh DA DUOC SO SANH VOI "
             "NHAU khi chon phuong tien park trong W2/Q2 (job Taylor_20260927_141318): 5 phuong tien "
             "{D khong park, A custom30V, B custom30, C6, C10} x 2 tang proxy tien nhan roi "
             "{baseline, floor} = 10. Moi backtest R&D khac, chay cho cau hoi khac, KHONG thuoc ho "
             "nay — do la benh glob dong ma dsr_family_manifest.py duoc dung de chua."},
 "n_entries": len(entries), "n_candidates_globbed": None, "skipped": {},
 "entries": entries}
out = "/home/trido/thanhdt/WorkingClaude/data/dsr_family_manifest_w2q2_2026-09-27.json"
json.dump(man, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"Ghi {out}: {len(entries)} CSV")
for e in entries:
    print(f"  {e['n_obs']:>5} obs  {e['md5'][:10]}  {os.path.basename(e['path'])[-70:]}")
