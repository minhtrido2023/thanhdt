"""E1 phụ — quy lệnh bị DEFER trong plan 07-28/29 (SpaceX, ZaloPay) ra pp trên cửa sổ con 07-20→07-31.
Mỗi lệnh lấy lần XUẤT HIỆN ĐẦU (plan ngày d = ngày khớp dự kiến, theo quy ước plan_<acct>_<d>.json); giá vào = Open d
(Open × Price/Close để về giá thực), giá ra = Price 07-31; notional = qty × giá vào. pp = Σ notional·r / NAV(07-17).
XẤP XỈ: bỏ phí; giả định khớp trọn tại Open; không mô hình hoá việc tiền đó (nếu không defer) phải lấy từ bán park."""
import glob, json, os
import pandas as pd
R = os.path.dirname(os.path.abspath(__file__)); TP = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
X = pd.read_parquet(f"{R}/sb/data/bq_cache_asof20261111/ticker/2026.parquet", columns=["time", "ticker", "Open", "Close", "Price"])
X["time"] = pd.to_datetime(X.time).dt.strftime("%Y-%m-%d"); X = X.set_index(["ticker", "time"])
navs = {"SpaceX": 990304455.0, "ZaloPay": 528085454.0}
for acct in navs:
    h = pd.read_csv(f"/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_history_{acct}.csv").drop_duplicates("date", keep="last").set_index("date")
    if acct == "ZaloPay":
        h = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/execution_logs/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last").set_index("date").rename(columns={"nav_b": "nav"})
    navs[acct] = float(h.loc[h.index <= "2026-07-17", "nav"].iloc[-1])
rows, seen = [], set()
for f in sorted(glob.glob(f"{TP}/plan_*_2026-07-2[0-9].json") + glob.glob(f"{TP}/plan_*_2026-07-3[01].json")):
    acct = os.path.basename(f).split("_")[1]
    if acct not in navs: continue
    d = os.path.basename(f).split("_")[2][:10]
    for o in json.load(open(f)).get("deferred_orders") or []:
        k = (acct, o.get("ticker"))
        if k in seen or not o.get("qty"): continue
        seen.add(k)
        try:
            r0 = X.loc[(o["ticker"], d)]; r1 = X.loc[(o["ticker"], "2026-07-31")]
        except KeyError:
            continue
        p0 = float(r0.Open) * float(r0.Price) / float(r0.Close); p1 = float(r1.Price)
        n = o["qty"] * p0
        rows.append(dict(TK=acct, plan=d, ticker=o["ticker"], book=o.get("book"), qty=o["qty"], notional=n, r_pct=100 * (p1 / p0 - 1),
                         pp=100 * n * (p1 / p0 - 1) / navs[acct], in_sub=d <= "2026-07-31"))
T = pd.DataFrame(rows); T.to_csv(f"{R}/e1_deferred.csv", index=False, float_format="%.4f")
print(T.to_string(index=False)); print(T.groupby(["TK", "book"]).agg(notional=("notional", "sum"), pp=("pp", "sum")))
print("TỔNG pp theo TK:", T.groupby("TK").pp.sum().round(3).to_dict(), "NAV 07-17:", navs)

# Ròng so với nguồn tiền thực tế: lệnh bị defer vì tiền nằm ở rổ park ⇒ muốn khớp phải bán park cùng phiên.
# r_park = chỉ số rổ park của engine (bal_etf_ref, chân fidT cùng TK) từ đóng cửa phiên TRƯỚC d tới 07-31 (xấp xỉ: Open d ≈ close d−1).
pk = {}
for acct, k in (("SpaceX", "SX"), ("ZaloPay", "Z")):
    L = pd.read_csv(glob.glob(f"{R}/ledgers/*gapE_{k}cold_fidT_*.csv")[0], low_memory=False); L = L[L.record_type == "DAILY"]
    pk[acct] = pd.Series(L.bal_etf_ref.astype(float).values, index=L.ymd.astype(str).str[:10])
def rpark(acct, d):
    s = pk[acct]; return float(s[s.index <= "2026-07-31"].iloc[-1]) / float(s[s.index < d].iloc[-1]) - 1
T["r_park_pct"] = [100 * rpark(a, d) for a, d in zip(T.TK, T.plan)]
T["pp_net_park"] = T.notional * (T.r_pct - T.r_park_pct) / 100 / T.TK.map(navs) * 100
T.to_csv(f"{R}/e1_deferred.csv", index=False, float_format="%.4f")
print(T[["TK", "plan", "ticker", "book", "r_pct", "r_park_pct", "pp", "pp_net_park"]].to_string(index=False))
print("TỔNG ròng park:", T.groupby("TK").pp_net_park.sum().round(3).to_dict())
