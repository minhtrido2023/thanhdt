import json
P = json.load(open("positions_20260930.json")); NS = json.load(open("navstats.json"))
def vn(x, d=0):
    s = f"{x:,.{d}f}"; return s.replace(",", "X").replace(".", ",").replace("X", ".")
def sg(x, d=2): return ("+" if x > 0 else ("−" if x < 0 else "")) + vn(abs(x), d)
for acc in ["SpaceX", "ZaloPay"]:
    nav = NS[acc]["nav1"]; last = NS[acc]["last"]
    out = ["| Mã | Khối lượng | Giá vốn (đ/cp) | Giá đóng cửa 30/09 | Giá trị thị trường (đ) | % NAV | Lãi/lỗ chưa thực hiện (%) |", "|---|---:|---:|---:|---:|---:|---:|"]
    for r in P[acc]["rows"]:
        pct = "—¹" if r["sym"] == "DRI" else sg(r["pct"]) + "%"
        nm = r["sym"]
        if acc == "ZaloPay" and nm == "DGC": nm = "**DGC** (legacy, excluded)"
        out.append(f"| {nm} | {vn(r['qty'])} | {vn(r['raw_cost'])} | {vn(r['px'])} | {vn(r['mv'])} | {vn(r['mv']/nav*100,1)}% | {pct} |")
    mv = sum(r["mv"] for r in P[acc]["rows"])
    cash, egg, debt = float(last["cash"]), float(last["egg_assets"]), float(last["margin_debt"])
    out.append(f"| **Tổng cổ phiếu** | | | | **{vn(mv)}** | **{vn(mv/nav*100,1)}%** | |")
    out.append(f"| Tiền mặt | | | | {vn(cash)} | {vn(cash/nav*100,1)}% | |")
    out.append(f"| Tiền gửi sinh lời tại CTCK | | | | {vn(egg)} | {vn(egg/nav*100,1)}% | |")
    out.append(f"| Dư nợ ký quỹ | | | | −{vn(debt)} | 0,0% | |")
    out.append(f"| **NAV** | | | | **{vn(mv+cash+egg-debt)}** | **100%** | |")
    open(f"table_{acc}.md", "w").write("\n".join(out) + "\n")
    print(acc, mv + cash + egg - debt, nav)
