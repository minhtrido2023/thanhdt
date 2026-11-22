#!/usr/bin/env python3
"""Selfcheck dd_reconfirm_plan.py bằng fixture (sổ/state/rules tmp). Chạy dưới env -u TZ và TZ lạ."""
import json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
res = []
def chk(n, ok): res.append(ok); print(("PASS " if ok else "FAIL ") + n)
def E(t, rev, c, lbl, st, fin="FIXED_UNVERIFIED", lo=100, d="2026-11-01"):
    return {"ticker": t, "dd_date": d, "rev": rev, "center": c, "zone_low": lo, "verdict_label": lbl, "skeptic_status": st, "skeptic_final": fin}
ents = [
  E("AAA", 1, 1000, "TRONG vùng: x", "CONFIRMED (medium)"), E("AAA", 2, 1030, "TRONG vùng: y", "r3 sửa theo SKEPTIC_R2; CHƯA chạy skeptic trên r3"),   # Δ+3% cùng nhãn ⇒ MECH
  E("BBB", 1, 1000, "TRONG vùng: x", "CONFIRMED"), E("BBB", 2, 1100, "TRONG vùng: y", "REFUTED-đã-áp"),                                           # Δ+10% ⇒ FULL
  E("CCC", 1, 1000, "TRONG vùng: x", "CONFIRMED"), E("CCC", 2, 1010, "NON — x", "REFUTED-đã-áp"),                                              # nhãn đổi ⇒ FULL
  E("DDD", 1, 1000, "TRONG vùng: x", "r2: skeptic REFUTED đã áp"),                                                                              # 1 rev APPLIED ⇒ ?
  E("EEE", 1, 1000, "TRONG vùng", "CONFIRMED", fin="CONFIRMED"),                                                                                # OK
  E("FFF", 1, 1000, "TRONG vùng", "CHƯA qua skeptic"), E("FFF", 2, 1000, "TRONG vùng", "CHƯA chạy fundamental-skeptic trên r2"),              # không rev nào đọc ⇒ ?
  E("GGG", 1, None, "TRONG vùng", "CONFIRMED"), E("GGG", 2, 900, "TRONG vùng", "REFUTED-đã-áp"),                                              # tâm null ⇒ ?
  E("HHH", 1, 1000, "TRONG vùng", "CONFIRMED"), E("HHH", 2, 1000, "TRONG vùng", "REFUTED-đã-áp", lo=100),                                      # held
  E("III", 1, 1000, "TRONG vùng", "CONFIRMED"), E("III", 2, 1000, "TRONG vùng", "REFUTED-đã-áp", lo=500),                                      # giá dưới đáy
]
with tempfile.TemporaryDirectory() as td:
    L = os.path.join(td, "l.json"); json.dump({"entries": ents}, open(L, "w"))
    S = os.path.join(td, "s.json"); json.dump({"days": {"2026-11-19": {"III": {"close": 1}}, "2026-11-20": {"III": {"close": 400}, "HHH": {"close": 50}}}}, open(S, "w"))
    R = os.path.join(td, "r.json"); json.dump({"positions": [{"ticker": "HHH"}]}, open(R, "w"))
    env = dict(os.environ, DDZ_STATE=S, DD_EXIT_RULES=R)
    out = os.path.join(td, "PLAN.md")
    p = subprocess.run([sys.executable, os.path.join(HERE, "dd_reconfirm_plan.py"), "--ledger", L, "--out", out], capture_output=True, text=True, env=env)
    txt = open(out).read() if os.path.isfile(out) else ""
    row = {l.split("|")[2].strip(): [c.strip() for c in l.split("|")[1:-1]] for l in txt.splitlines() if re.match(r"\| P\d", l)}
    chk("rc=0, 9 mã trong bảng", p.returncode == 0 and len(row) == 9)
    chk("AAA Δ+3% cùng nhãn ⇒ MECH", row["AAA"][7] == "**MECH**" and row["AAA"][4] == "2026-11-01#1")
    chk("BBB Δ+10% ⇒ FULL", row["BBB"][7] == "**FULL**" and row["BBB"][5] == "+10.0%")
    chk("CCC Δ+1% nhưng đổi nhãn ⇒ FULL", row["CCC"][7] == "**FULL**" and row["CCC"][6] == "có")
    chk("DDD 1 rev đã-áp-sửa ⇒ không xác định / ?", row["DDD"][4] == "không xác định" and row["DDD"][7] == "**?**")
    chk("EEE skeptic_final=CONFIRMED ⇒ OK", row["EEE"][7] == "**OK**")
    chk("FFF không rev nào được đọc ⇒ ?", row["FFF"][7] == "**?**")
    chk("GGG tâm null ⇒ ?", row["GGG"][7] == "**?**")
    chk("HHH đang giữ ⇒ P1 (dù cũng dưới đáy)", row["HHH"][0] == "P1")
    chk("III close ngày LỚN NHẤT (400<500) ⇒ P2, giá<đáy có", row["III"][0] == "P2" and row["III"][8] == "có")
    pr = [l.split("|")[1].strip() for l in txt.splitlines() if re.match(r"\| P\d", l)]
    chk("thứ tự: P1 trước P2 trước P3", pr == sorted(pr))
    chk("CHỈ ĐỌC: sổ fixture không đổi", json.load(open(L)) == {"entries": ents})
    p2 = subprocess.run([sys.executable, os.path.join(HERE, "dd_reconfirm_plan.py"), "--ledger", os.path.join(td, "nope.json")], capture_output=True, text=True, env=env)
    chk("sổ không tồn tại ⇒ rc=2 + lý do", p2.returncode == 2 and "LỖI" in p2.stderr)
print("-- %d/%d PASS" % (sum(res), len(res))); sys.exit(0 if all(res) else 1)
