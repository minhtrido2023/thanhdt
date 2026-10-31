# GAPS 31/10/2026 — phep tinh bo sung (nguon ghi canh tung so)
N=1003.312808  # tr cp TCH [TM21d]
px=11850
hhs_sh=431.985968; hhs_px=9450        # BQ ticker_financial OShares; DNSE/BQ dong cua 30/10
hhs_mcap=hhs_sh*hhs_px/1000           # ty
tch_hhs=0.5831*hhs_mcap
crv_eq_3103=7579; crv_direct=0.3819   # BCTN25 tr.19 (CRV VCSH 31/03/2026); TM1.5 bieu quyet truc tiep
crv_dir_bv=crv_direct*crv_eq_3103
par_eq=10530.239; par_inv_net=4854.015-282.445  # BCTC rieng 30/09/2026 tr.4-5
par_ex=par_eq-par_inv_net
sotp=par_ex+crv_dir_bv+tch_hhs
print(f"HHS mcap {hhs_mcap:.1f} ty; TCH 58,31% = {tch_hhs:.1f} ty = {tch_hhs/N*1000:.0f} d/cp")
print(f"CRV truc tiep 38,19% x VCSH 31/03 {crv_eq_3103} = {crv_dir_bv:.1f} ty")
print(f"Me tru dau tu con: {par_eq:.1f}-{par_inv_net:.1f} = {par_ex:.1f} ty")
print(f"SOTP hon hop = {sotp:.1f} ty = {sotp/N*1000:.0f} d/cp vs gia {px} ({sotp/N*1000/px-1:+.1%})")
crv_sh=678.4; crv_px=23000
print(f"CRV P/B tai 23.000: {crv_sh*crv_px/1000/crv_eq_3103:.2f}x (von dieu le 6.784 ty ~678,4 tr cp); P/E FY25 {crv_sh*crv_px/1000/76.23:.0f}x")
tax=2.735112269+13.675561345+3.798166882
print(f"QD thue 1020: tong {tax:.2f} ty = {tax/N*1000:.1f} d/cp")
print(f"DHDCD 2026: 460.731.803 cp du = 50,51%; nhom Ha+HH Finance 328.247.206 = {328.247206/460.731803:.1%} phieu du hop")
print(f"Tien CBCP con lai 25/09/2026 865,53 / tien+HTM me 30/09 {852.204+1391.981:.1f} = {865.531/(852.204+1391.981):.0%}")
print(f"KH FY26: 6T LNST HN 914,29 = {914.29/2000:.1%}; DT 2.414 = {2414/5000:.1%}")
