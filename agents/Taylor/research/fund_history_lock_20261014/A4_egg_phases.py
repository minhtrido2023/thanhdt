#!/usr/bin/env python3
"""A4 — 3 giai đoạn ghi Trứng vàng trong nav_history (CHỈ ĐỌC data/ thật).
In: ngày đổi cách ghi (offbook_assets / egg_assets: trống | 0 | >0), tổng off-book mỗi bên ranh,
và bước nhảy NAV ngày ranh so với biến động mtm cùng ngày (bước nhảy giả = NAV đổi mà mtm+cash-debt không giải thích).
"""
import csv, sys
R = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
def f(x):
    return None if x in ("", None) else float(x)
def cls(x):
    return "trống" if x is None else ("0" if x == 0 else ">0")
for acc in ("SpaceX", "ZaloPay"):
    rows = list(csv.DictReader(open(f"{R}/nav_history_{acc}.csv", encoding="utf-8")))
    print(f"===== {acc}: {len(rows)} dòng")
    prev = None; segs = []
    for r in rows:
        key = (cls(f(r["offbook_assets"])), cls(f(r["egg_assets"])))
        if not segs or segs[-1][0] != key:
            segs.append([key, r["date"], r["date"], 0])
        segs[-1][2] = r["date"]; segs[-1][3] += 1
    for key, a, b, n in segs:
        print(f"  {a} → {b} ({n:2d} dòng): offbook_assets {key[0]:5s} | egg_assets {key[1]}")
    # bất biến + bước nhảy quanh mỗi ranh
    bad = 0
    for i, r in enumerate(rows):
        nav = float(r["nav"]); comp = float(r["mtm_stock"]) + float(r["cash"]) - float(r["margin_debt"]) \
            + (f(r["offbook_assets"]) or 0) + (f(r["egg_assets"]) or 0)
        if abs(nav - comp) > 1:
            bad += 1; print(f"  ⚠ {r['date']}: nav {nav:,.0f} ≠ mtm+cash−debt+offbook+egg {comp:,.0f} (lệch {nav-comp:+,.0f})")
    print(f"  bất biến nav = mtm + cash − debt + offbook + egg: {len(rows)-bad}/{len(rows)} dòng khớp (≤1đ)")
    for j in range(1, len(segs)):
        d = segs[j][1]; i = next(k for k, r in enumerate(rows) if r["date"] == d)
        a, b = rows[i-1], rows[i]
        off = lambda r: (f(r["offbook_assets"]) or 0) + (f(r["egg_assets"]) or 0)
        own = lambda r: float(r["cash"]) - float(r["margin_debt"]) + off(r)   # tiền sở hữu kể cả Trứng vàng
        dnav = float(b["nav"]) - float(a["nav"]); dmtm = float(b["mtm_stock"]) - float(a["mtm_stock"])
        print(f"  ranh {a['date']} → {b['date']}: offbook+egg {off(a):,.0f} → {off(b):,.0f} | ΔNAV {dnav:+,.0f} "
              f"({dnav/float(a['nav'])*100:+.4f}%) | Δmtm {dmtm:+,.0f} | Δ(tiền sở hữu gồm Trứng vàng) {own(b)-own(a):+,.0f} "
              f"| Δ(tiền sở hữu)+Δmtm−ΔNAV = {own(b)-own(a)+dmtm-dnav:+,.0f}")
