"""SOTP TV1 theo kịch bản giá Sông Bung 5 sau 2027 (job Taylor_20261013_061651).

Mọi giả định là THAM SỐ ở đầu file; nguồn từng tham số ghi trong README.md cùng thư mục.
Chạy: python3 sotp_sb5.py  -> in bảng + ghi sotp_sb5_scenarios.csv
"""
import csv
import os

SHARES = 26_691_319            # BQ ticker_financial.OShares 2026Q2
PRICE = 19_200                 # đóng cửa 2026-10-12 (BQ ticker.Price)
NET_DEBT = 117.0               # tỷ; giữ số SOTP cũ. 2026Q2: 133,6+0,4-61,8=72,2; +~40 cổ tức 15% chi T10 ≈ 112
OM_TARIFF_2027 = 95.0          # đ/kWh; 75,75 (2018) x 1,025^9 — phần O&M của giá, trượt 2,5%/năm
ESC = 0.025
CASH_OM = 25.0                 # tỷ/năm 2027: giá vốn điện 2025 96,5 - khấu hao ~35 - thuế TN+phí ~37
CAPEX = 5.0                    # tỷ/năm bảo trì
DEP, DEP_YEARS = 33.0, 15      # lá chắn thuế khấu hao
CIT = 0.20
PRICES = {"a_giu_2021_25": 950.0, "b_600": 600.0, "c_500": 500.0, "d_du_thao_2018": 340.0}
VOLUMES = [175.3, 187.0, 210.0, 236.0]   # triệu kWh
RATES = [0.10, 0.11, 0.12]
LIFE = 30
CONSULT = {"tu_van_0": 0.0, "tu_van_50": 50.0, "tu_van_100": 100.0}


def hydro_ev(p0, q, r, life=LIFE):
    ev, fcf1 = 0.0, None
    for t in range(1, life + 1):
        g = (1 + ESC) ** (t - 1)
        rev = q * (p0 + OM_TARIFF_2027 * (g - 1)) / 1000.0   # tỷ đồng, chưa gồm thuế TN + phí DVMTR
        om, capex = CASH_OM * g, CAPEX * g
        dep = DEP if t <= DEP_YEARS else 0.0
        tax = max(0.0, CIT * (rev - om - dep))
        fcf = rev - om - capex - tax
        fcf1 = fcf if t == 1 else fcf1
        ev += fcf / (1 + r) ** t
    return ev, fcf1


def main():
    rows = []
    for name, p0 in PRICES.items():
        for q in VOLUMES:
            for r in RATES:
                ev, fcf1 = hydro_ev(p0, q, r)
                for cname, cv in CONSULT.items():
                    eq = ev - NET_DEBT + cv
                    ps = eq * 1e9 / SHARES
                    rows.append({"kich_ban": name, "gia_net_d_kwh": p0, "san_luong_tr_kwh": q, "chiet_khau": r,
                                 "fcf_2027_ty": round(fcf1, 1), "hydro_ev_ty": round(ev), "tu_van": cname,
                                 "equity_ty": round(eq), "gia_tri_cp": round(ps, -2),
                                 "vs_gia_19200_pct": round((ps / PRICE - 1) * 100, 1)})
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sotp_sb5_scenarios.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("== Q=210, tư vấn=0 ==")
    for row in rows:
        if row["san_luong_tr_kwh"] == 210.0 and row["tu_van"] == "tu_van_0":
            print(row["kich_ban"], row["chiet_khau"], "FCF", row["fcf_2027_ty"], "EV", row["hydro_ev_ty"],
                  "eq", row["equity_ty"], "/cp", row["gia_tri_cp"], row["vs_gia_19200_pct"], "%")
    print("== r=11%, tư vấn=0, nhạy sản lượng ==")
    for row in rows:
        if row["chiet_khau"] == 0.11 and row["tu_van"] == "tu_van_0":
            print(row["kich_ban"], row["san_luong_tr_kwh"], "EV", row["hydro_ev_ty"], "/cp", row["gia_tri_cp"],
                  row["vs_gia_19200_pct"], "%")
    print("== giá hoà vốn (equity = vốn hoá, tư vấn=0, Q=210) ==")
    for r in RATES:
        lo, hi = 100.0, 1500.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if (hydro_ev(mid, 210.0, r)[0] - NET_DEBT) * 1e9 / SHARES > PRICE:
                hi = mid
            else:
                lo = mid
        print(r, round(hi), "đ/kWh")
    print("rows", len(rows), "->", out)


if __name__ == "__main__":
    main()
