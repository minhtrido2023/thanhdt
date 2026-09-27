#!/usr/bin/env python3
"""Ghim HO TRIAL cua job repin-dep1m thanh manifest bat bien — job Taylor_20260927_170645.

Ho = 4 cau hinh DA DUOC SO SANH VOI NHAU khi chot con so pin duoi quy uoc tien nhan roi moi:
  1 chan quy uoc CU (carry 0%/nam = rp_ctrl, byte-identical anchor R3) + 3 chan quy uoc MOI
  (tier dep1m tai 3 gia tri offset bac cau: median / p25 / p75).
KHONG dung glob (benh §8). Duong dan lay tu dong engine TU IN trong log, khong doan tu env.

Chay:  build_rp_manifest.py [--extended]
  --extended : them 10 chan W2/Q2 (cung phuong tien, cung ngay) => N=14, ban DSR THAN TRONG.
"""
import datetime, hashlib, io, json, os, sys
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import load_nav

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
W2LOGS = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/c30v_w2_q2_20260927/logs"
TAGS = [("rp_ctrl", f"{HERE}/logs", "quy uoc CU: carry 0%/nam (= anchor R3, md5 4707bcbe)"),
        ("rp_pin", f"{HERE}/logs", "quy uoc MOI: tier dep1m, offset bac cau = MEDIAN -2.525pp (CHAN PIN)"),
        ("rp_p25", f"{HERE}/logs", "quy uoc MOI: tier dep1m, offset = p25 -3.400pp (bang bat dinh cau)"),
        ("rp_p75", f"{HERE}/logs", "quy uoc MOI: tier dep1m, offset = p75 -2.300pp (bang bat dinh cau)")]
EXT = [(f"w2{k}_{t}", W2LOGS, f"W2/Q2 leg w2{k}_{t} (ho chon phuong tien park, job Taylor_20260927_141318)")
       for t in ("baseline", "floor") for k in ("d", "a", "b", "c6", "c10")]

def md5_of(p, chunk=1 << 20):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def entry(tag, logs, reason):
    txt = io.open(f"{logs}/{tag}.log", encoding="utf-8", errors="replace").read()
    assert f"EXIT=0 ({tag}" in txt, f"{tag}: khong EXIT=0"
    hits = [l.split("->", 1)[1].split("(")[0].strip() for l in txt.splitlines()
            if l.strip().startswith("-> ") and l.strip().endswith("rows)")]
    assert len(hits) == 1, (tag, hits)
    p = hits[0]
    s = load_nav(p)
    return {"path": p, "md5": md5_of(p), "size": os.path.getsize(p),
            "mtime_ict": datetime.datetime.fromtimestamp(os.path.getmtime(p), ICT).isoformat(),
            "n_obs": 0 if s is None else int(len(s)), "reason": reason}

ext = "--extended" in sys.argv
tags = TAGS + (EXT if ext else [])
entries = sorted((entry(*t) for t in tags), key=lambda e: e["path"])
man = {
 "_doc": "Ho trial CO DINH cho dsr_pbo_annex.py. KHONG sua tay.",
 "manifest_version": 1,
 "created_at_ict": datetime.datetime.now(ICT).isoformat(),
 "criterion": {
   "glob": "KHONG dung glob — liet ke tuong minh",
   "mtime_before_ict": None, "min_obs": 0,
   "reason": ("Ho trial dung nghia Bailey-Borwein-LdP-Zhu 2017 cho job repin-dep1m "
              "(Taylor_20260927_170645) = tap cau hinh DA DUOC SO SANH VOI NHAU khi chot con so pin "
              "duoi quy uoc tien nhan roi moi: 1 chan quy uoc CU (carry 0%) + 3 chan tier dep1m x "
              "{median, p25, p75} offset bac cau = 4. LUU Y dien giai: chan pin KHONG duoc chon vi "
              "'tot nhat' — offset median la luat DINH TRUOC cua dispatch, va tren so thuc te chan "
              "median cho CAGR THAP NHAT trong 3 chan. Nen rui ro multiple-testing o day khong phai "
              "'chon chan thang' ma la 'quy uoc do co the duoc chon co loi'."
              + (" BAN --extended: them 10 chan W2/Q2 cung phuong tien cung ngay => N=14, doc nhu "
                 "chan tren THAN TRONG cua so trial." if ext else ""))},
 "n_entries": len(entries), "n_candidates_globbed": None, "skipped": {}, "entries": entries}
out = f"/home/trido/thanhdt/WorkingClaude/data/dsr_family_manifest_repin_dep1m_2026-09-28{'_ext' if ext else ''}.json"
json.dump(man, open(out, "w"), indent=1)
print(f"-> {out}  n_entries={len(entries)}")
for e in entries:
    print(f"   {e['md5']}  n_obs={e['n_obs']:<5} {e['path'].rsplit('/',1)[-1][:110]}")
