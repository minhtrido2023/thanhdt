#!/usr/bin/env python3
"""So đầu ra master vs nhánh trên MỌI khoá của hợp đồng cũ. rc=0 ⇔ không khoá cũ nào đổi."""
import json, sys
old = json.load(open(sys.argv[1])); new = json.load(open(sys.argv[2]))
n = bad = 0
newkeys = set()
for acct in old:
    assert set(old[acct]) == set(new[acct]), acct
    for d, o in old[acct].items():
        w = new[acct][d]
        for k, v in o.items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    n += 1
                    if w[k].get(kk) != vv or type(w[k].get(kk)) is not type(vv):
                        bad += 1; print("LỆCH", acct, d, k, kk, vv, w[k].get(kk))
                newkeys |= set(w[k]) - set(v)
            else:
                n += 1
                if w.get(k) != v:
                    bad += 1; print("LỆCH", acct, d, k, v, w.get(k))
        for per in ("inception", "wtd", "mtd"):       # không dòng tiền ⇒ mwr == twr, quy năm null
            if "error" in w: continue
            p = w[per]
            n += 1
            if not (p["mwr_pct"] == p["return_pct"] and p["annualized_return_pct"] is None
                    and p["mwr_annualized_pct"] is None and p["pnl_vnd"] == p["nav1"] - p["nav0"]):
                bad += 1; print("LỆCH khoá mới", acct, d, per, p)
print(f"so {n} giá trị trên {sum(len(v) for v in old.values())} (account, ngày lịch): {bad} lệch")
print("khoá MỚI thêm vào mỗi kỳ:", sorted(newkeys))
sys.exit(1 if bad else 0)
