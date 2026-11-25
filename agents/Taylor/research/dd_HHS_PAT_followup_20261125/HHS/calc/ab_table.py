"""Bảng A/B HHS — CHỈ đọc lại lưới đã khoá của w3 (calc_adj_hhs.py, adj_run1.txt md5 82f1f004…), không tính lại mô hình, không đọc giá.
So với tâm sổ hiện hành rev8 = 10.805 (dd_price_zones, master ff4e5c744)."""
import json, sys, hashlib
src = sys.argv[1]
print("src md5", hashlib.md5(open(src, 'rb').read()).hexdigest())
g = json.load(open(src))['grid']
REV8 = 10805
for lab, key in (("A  biên s_obs 52,05%", "obs 52,05%"), ("B1 biên TB peer 37,7%", "TB peer 37,7%"), ("B2 biên TCH 29,9%", "TCH 29,9%")):
    b, a = g[f"{key} | CK 0.0"], g[f"{key} | CK 0.2"]
    print(f"{lab}: base(CK0) {b['center']} [{b['p10']}–{b['p90']}] {100*(b['center']/REV8-1):+.1f}% | adj E17(CK20) {a['center']} [{a['p10']}–{a['p90']}] {100*(a['center']/REV8-1):+.1f}% | dải adj {a['center']}–{b['center']} | EX k1 base {b['ex_k1']} adj {a['ex_k1']} | B vs A base {100*(b['center']/g['obs 52,05% | CK 0.0']['center']-1):+.2f}% adj {100*(a['center']/g['obs 52,05% | CK 0.2']['center']-1):+.2f}%")
