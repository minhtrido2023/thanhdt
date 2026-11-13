"""A7 việc 3: vì sao engine 1B chạm trần ADV ở 65,5% ngày mua LAG mà live 0/48?
Tách tỉ số  r = lệnh/(0,20·ADV_pit)  thành  (cỡ lệnh)  ×  (1/ADV mã được chọn), so engine vs live.
Engine: ledger A6 (TX book LAG buy, play LAG_HI/LAG_LO) — gộp theo holding (tổng vốn mua, ngày fill đầu); ADV pit dựng lại
  y engine (median Volume t-60..t-1 min20 × PxAdv t-1) từ cache pin-era bq_cache_asof20260729_postrestate.
Live: A5 logs/lag_orders.json (48 lệnh qty>0, plan chính tắc) + A5 logs/bq_px_vol.csv (tav2_bq.ticker kéo 13/11), cùng công thức pit.
Usage: diag_lag.py lab=ledger.csv ..."""
import sys, json, numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"; A5 = f"{WC}/mike/agents/Taylor/research/live_gap_exec_A5"
def pit_adv(px):
    px = px.sort_values(["ticker", "time"], kind="mergesort").copy(); px["P"] = px.Price.fillna(px.Close)
    g = px.groupby("ticker")
    px["pit"] = g.Volume.transform(lambda v: v.shift(1).rolling(60, min_periods=20).median()) * g.P.shift(1)
    return px
def q(x): x = pd.Series(x).dropna(); return f"p25 {x.quantile(.25):8.3g} | p50 {x.median():8.3g} | p75 {x.quantile(.75):8.3g} (n={len(x)})"
# ---------------- live
o = pd.DataFrame(json.load(open(f"{A5}/logs/lag_orders.json"))); o = o[o.qty.fillna(0) > 0].copy()
lp = pit_adv(pd.read_csv(f"{A5}/logs/bq_px_vol.csv", parse_dates=["time"]))
navh = {a: pd.read_csv(f"{WC}/data/execution_logs/nav_history_{a}.csv", parse_dates=["date"]).sort_values("date") for a in ("SpaceX", "ZaloPay")}
L = []
for _, r in o.iterrows():
    t = pd.Timestamp(r.date); c = lp[(lp.ticker == r.tk) & (lp.time == t)]
    nh = navh[r.acct]; nh = nh[nh.date < t]
    L.append(dict(acct=r.acct, date=t, tk=r.tk, val=r.qty * r.px, adv=c.pit.iloc[0] if len(c) else np.nan,
                  nav=nh.nav.iloc[-1] if len(nh) else np.nan, fillq=r.fillq))
L = pd.DataFrame(L); L["r"] = L.val / (0.2 * L.adv); L["r_share"] = L.val / (0.2 * L.adv * 0.5); L["w"] = L.val / L.nav
print("=== LIVE: 48 lệnh mua LAG (qty>0), 07-27→11-09 ===")
print(f"  cỡ lệnh VND        {q(L.val)}\n  ADV pit VND        {q(L.adv)}\n  lệnh/NAV acct      {q(L.w)}")
print(f"  lệnh/(0,2·ADV)     {q(L.r)}  ⇒ >1: {(L.r > 1).sum()}/{L.r.notna().sum()}")
print(f"  lệnh/(0,2·ADV·½)   {q(L.r_share)}  ⇒ >1: {(L.r_share > 1).sum()}/{L.r_share.notna().sum()} (trần live thật, share=1/2 account)")
print(f"  NAV acct lúc đặt   {q(L.nav)}")
u = L.drop_duplicates(["tk", "date"]); print(f"  N độc lập: {len(u)} cặp (mã,ngày), {u.tk.nunique()} mã: {sorted(u.tk.unique())}")
# ---------------- engine
con = duckdb.connect()
for lab, p in (a.split("=", 1) for a in sys.argv[1:]):
    T = pd.read_csv(p, low_memory=False)
    D = T[T.record_type == "DAY"] if "DAY" in set(T.record_type) else None
    X = T[(T.record_type == "TX") & (T.book == "LAG") & (T.action == "buy") & T.play_type.isin(["LAG_HI", "LAG_LO"])].copy()
    X["ymd"] = pd.to_datetime(X.ymd); X["cost"] = X.buy_amount.astype(float) + X.fee.astype(float)
    H = X.groupby("holding_id").agg(tk=("ticker", "first"), d0=("ymd", "min"), cost=("cost", "sum"), nd=("ymd", "nunique")).reset_index()
    F = X.groupby(["holding_id", "ymd"]).cost.sum().reset_index().sort_values("ymd").groupby("holding_id").first().reset_index()
    H = H.merge(F.rename(columns={"cost": "cost_d0"})[["holding_id", "cost_d0"]], on="holding_id")
    tks = sorted(H.tk.unique())
    px = con.sql(f"""SELECT ticker, CAST(time AS DATE) AS time, Volume, Price, Close FROM read_parquet('{WC}/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
      WHERE ticker IN ({','.join(repr(t) for t in tks)}) AND time >= '2013-06-01'""").df(); px["time"] = pd.to_datetime(px.time)
    px = pit_adv(px)[["ticker", "time", "pit"]]
    H = H.merge(px, left_on=["tk", "d0"], right_on=["ticker", "time"], how="left")
    H["r"] = H.cost / (0.2 * H.pit); H["r_d0"] = H.cost_d0 / (0.2 * H.pit)
    # NAV tổng engine tại ngày vào (combined_nav trên dòng TX)
    nv = T[T.record_type == "TX"][["ymd", "combined_nav"]].dropna(); nv["ymd"] = pd.to_datetime(nv.ymd)
    nv = nv.groupby("ymd").combined_nav.last()
    H["nav"] = H.d0.map(nv); H["w"] = H.cost / H.nav
    print(f"\n=== ENGINE {lab}: {len(H)} holding LAG, {H.tk.nunique()} mã ===")
    for nm, h in (("2014-2026 toàn kỳ", H), ("2024-07→2026-06 (2 năm cuối)", H[H.d0 >= "2024-07-01"])):
        print(f" [{nm}]")
        print(f"  cỡ lệnh (tổng holding) {q(h.cost)}\n  ADV pit VND        {q(h.pit)}\n  lệnh/NAV tổng      {q(h.w)}")
        print(f"  tổng/(0,2·ADV)     {q(h.r)}  ⇒ >1: {(h.r > 1).mean():.1%}; ADV≤0/thiếu: {(~(h.pit > 0)).sum()}")
        print(f"  ngày fill          {q(h.nd)}  ⇒ ≥2 ngày: {(h.nd >= 2).mean():.1%}")
    # phản thực tế: nếu engine đặt lệnh cỡ live (median lệnh live) vào đúng các mã của nó, bao nhiêu % vượt trần?
    for nm, sz in (("cỡ lệnh live p50", L.val.median()), ("cỡ lệnh live p75", L.val.quantile(.75))):
        print(f"  [phản thực tế] {nm} {sz/1e6:.1f}tr vào mã engine: >0,2·ADV {(sz > 0.2 * H.pit).mean():.1%}, >0,1·ADV (share ½) {(sz > 0.1 * H.pit).mean():.1%}")
    print(f"  [phản thực tế] mã live (ADV p50 {L.adv.median()/1e9:.2f}B) nhận cỡ lệnh engine p50 {H.cost.median()/1e6:.1f}tr: >0,2·ADV {(H.cost.median() > 0.2 * L.adv).mean():.1%}")
# ---- phần 2: sàn ADV 2 tỷ live (lag_liquidity_filter.ADV_MIN_VND) — engine có bao nhiêu holding / vốn dưới sàn?
    lo = H.pit < 2e9
    print(f"  [sàn 2 tỷ] holding ADV_pit<2B: {lo.mean():.1%} số lệnh, {H.cost[lo].sum()/H.cost.sum():.1%} vốn mua LAG; "
          f"trong nhóm đó tổng/(0,2·ADV)>1: {(H.r[lo] > 1).mean():.1%}; nhóm ≥2B: {(H.r[~lo] > 1).mean():.1%}")
print(f"\nLIVE: ADV_pit min {L.adv.min()/1e9:.2f}B; <2B: {(L.adv < 2e9).sum()}/{L.adv.notna().sum()} lệnh")
