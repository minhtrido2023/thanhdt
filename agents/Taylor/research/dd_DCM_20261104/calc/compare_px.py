"""CHẠY SAU khoá md5 (calc/LOCK_md5.txt 23:12:56 ICT). Giá đóng cửa 04/11/2026 = 33.000 (tav2_bq.ticker, calc/px_liq_out.csv; chưa đối chiếu DNSE)."""
import sys; sys.path.insert(0,'calc'); import model as M
PX=33000; base=M.run()
print(f"Giá {PX:,} vs kỳ vọng {base['EV']:,.0f}: {PX/base['EV']-1:+.1%}; vs CYC {PX/base['CYC']-1:+.1%}; ADMIN {PX/base['ADMIN']-1:+.1%}; STRUCT {PX/base['STRUCT']-1:+.1%}")
lo,hi=100,500
for _ in range(60):
    mid=(lo+hi)/2; v=M.run(s_tc=mid)['EV']; lo,hi=(mid,hi) if v<PX else (lo,mid)
print(f"Biên dài hạn hàm ý (mọi nhánh khác giữ nguyên): {mid:.0f} USD/t vs TB chu kỳ 2016-25 {M.spread_tc:.0f}; 2025 {M.proxy[2025]:.0f}; 2024 {M.proxy[2024]:.0f}; 2023 {M.proxy[2023]:.0f}")
lnst_imp = M.lnst_at(mid,M.TAX_NEW)
print(f"LNST hoạt động hàm ý (thuế 20%) {lnst_imp:,.0f} tỷ; + lãi tiền ròng sau thuế {M.NI_cash_pre*0.8:,.0f} => {lnst_imp+M.NI_cash_pre*0.8:,.0f} tỷ")
bv=11849.414; ttm=389.45+2282.09
print(f"P/B {PX/(bv*1e9/M.SH):.2f} (BVPS {bv*1e9/M.SH:,.0f}); P/E TTM {PX/(ttm*1e9/M.SH):.1f} (LNST mẹ 4Q {ttm:,.0f}; Q4/25 dùng LNST HN); "
      f"giá − net cash = {PX-M.ps(M.net_cash):,.0f} đ/cp; P/E ex-cash trên LNST hoạt động CYC (20%) {(PX-M.ps(M.net_cash))/M.ps(base['lr_cyc']):.1f}x, (10,8%) {(PX-M.ps(M.net_cash))/M.ps(M.lnst_at(M.spread_tc,M.TAX_HIST)):.1f}x")
