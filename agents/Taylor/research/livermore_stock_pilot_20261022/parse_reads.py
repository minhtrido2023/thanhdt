#!/usr/bin/env python3
"""Parse raw/E###.txt -> reads.csv, ghi md5 vào lock log. KHÔNG đọc key/outcome."""
import glob, hashlib, os, re, datetime
D = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(f"{D}/raw/E*.txt")):
    t = open(f).read(); i = os.path.basename(f)[:-4]
    g = lambda k: re.search(rf"^{k}:\s*(.+?)\s*$", t, re.M | re.I)
    ph, rk, pp, inv, con = (g(k) for k in ("P_HIT15", "RISK", "P_POS", "INVALIDATION", "CONTAMINATION"))
    q = lambda s: '"' + s.replace('"', "'") + '"'
    rows.append(f"{i},{float(ph.group(1))},{rk.group(1).upper()},{float(pp.group(1))},{q(inv.group(1) if inv else '')},{q(con.group(1) if con else 'MISSING')}")
open(f"{D}/reads.csv", "w").write("id,P_HIT15,RISK,P_POS,INVALIDATION,CONTAMINATION\n" + "\n".join(rows) + "\n")
m = hashlib.md5(open(f"{D}/reads.csv", "rb").read()).hexdigest()
msg = f"{datetime.datetime.now().astimezone().isoformat(timespec='seconds')} reads.csv n={len(rows)} md5={m} (khoá TRƯỚC khi join outcome)"
open(f"{D}/reads_md5.lock.log", "a").write(msg + "\n"); print(msg)
