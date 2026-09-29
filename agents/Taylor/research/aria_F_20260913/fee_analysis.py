"""aria-F1b: phan phoi phi/thue theo chieu x account x thang tu all_fills.csv + doi chieu sao ke T07."""
import os, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(H, "all_fills.csv"), dtype={"tieu_khoan": str})
d["exch"] = d.ma.map(lambda t: "UPCOM" if t in {"DRI", "TV1", "SCL"} else "HOSE")
out = []
g = d.groupby(["acct", "loai_lenh", "month"]).agg(N_fill=("ma", "size"), N_phien=("email_date", "nunique"), gia_tri=("gia_tri_khop", "sum"),
    phi=("fee", "sum"), thue=("thue", "sum"), r_min=("r_total", "min"), r_med=("r_total", "median"), r_max=("r_total", "max"))
g["phi_vw_%"] = g.phi / g.gia_tri * 100; g["thue_vw_%"] = g.thue / g.gia_tri * 100
out.append("## Phân phối phí (phí sở + phí DNSE) / giá trị khớp, % \n\n" + "```\n" + g.round(4).to_string() + "\n```")
for side, s in d.groupby("loai_lenh"):
    mode = s.r_total.round(3).mode()[0]
    out.append(f"- {side}: N={len(s)}, mode {mode}% — trong ±0,002pp của mode: {((s.r_total-mode).abs()<=0.002).mean():.1%}; "
               f"phí DNSE trong 0,070±0,002: {((s.r_dnse-0.07).abs()<=0.002).mean():.1%}; "
               + "; ".join(f"sở {ex}: N={len(x)}, trong ±0,002pp của {x.r_so.round(3).mode()[0]}: {((x.r_so-x.r_so.round(3).mode()[0]).abs()<=0.002).mean():.1%}" for ex, x in s.groupby("exch")))
bv = d[d.loai_lenh == "MUA"]
out.append(f"- MUA theo giá trị: UPCOM {bv[bv.exch=='UPCOM'].gia_tri_khop.sum()/bv.gia_tri_khop.sum():.1%}; phí VW mua toàn bộ {bv.fee.sum()/bv.gia_tri_khop.sum()*100:.4f}%, bán {d[d.loai_lenh=='BÁN'].fee.sum()/d[d.loai_lenh=='BÁN'].gia_tri_khop.sum()*100:.4f}%")
out.append(f"- Thuế bán: {(d[d.loai_lenh=='BÁN'].r_tax.round(3)==0.1).sum()}/{(d.loai_lenh=='BÁN').sum()} fill đúng 0,1%; ngoại lệ = TCM 09/07 ZaloPay (thuế CK quyền 55.000đ gộp vào dòng)")
open(os.path.join(H, "fee_analysis_out.md"), "w").write("\n\n".join(out) + "\n")
print("\n\n".join(out))
