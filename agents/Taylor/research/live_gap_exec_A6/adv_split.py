"""A6 việc 4: pit-ADV thấp GIẢ sau thưởng/cổ tức CP (và quyền mua) — đo theo từng (mã, ngày) mua LAG.
pit-ADV(t)  = median(Volume_raw[t-60..t-1], min 20) × PxAdv(t-1)        (ĐÚNG công thức engine LAG_ADV_SRC=pit, L1578-1580)
adj-ADV(t)  = median(Volume_raw[d] × F(d→t-1), d∈[t-60..t-1]) × PxAdv(t-1), F = Π(1+exercise_ratio) các sự kiện ex trong (d, t-1]
Sự kiện: data/snapshots/corp_action_share_20260927.parquet (= BASKET_CA_SNAPSHOT của engine), ISS price_adjusting=True,
  exright_date có. Nhóm A = thưởng + cổ tức CP (số CP tăng chắc chắn 1+r); nhóm B = quyền mua (1+r là CẬN TRÊN — chỉ phần đăng ký).
Kiểm hệ số bằng giá: k=Price/Close; R = k(ex-1)/k(ex+1) (né Price đứng yên đúng ngày GDKHQ, bẫy registry) phải ≈ 1+r.
Data giá/khối lượng = cache pin-era data/bq_cache_asof20260729_postrestate/ticker/*.parquet (đúng dữ liệu engine đọc).
Lệnh mua LAG = TX book LAG action buy play_type LAG_HI/LAG_LO trong ledger; cap ràng buộc ⇔ buy_amount+fee ≥ 0,999×0,20×pitADV.
Ba bộ hệ số (env ADV_EV_SET): Av = nhóm A ĐÃ kiểm bằng giá |log(R/f)|≤0,05 (TIÊU ĐỀ) | A = mọi nhóm A | AB = A + quyền mua (cận trên).
Usage: ADV_EV_SET=Av adv_split.py label=ledger.csv ..."""
import os
EVSET = os.environ.get("ADV_EV_SET", "Av")
import sys, numpy as np, pandas as pd, duckdb
WC = "/home/trido/thanhdt/WorkingClaude"
ca = pd.read_parquet(f"{WC}/data/snapshots/corp_action_share_20260927.parquet")
ca = ca[(ca.event_code == "ISS") & ca.price_adjusting & ca.exright_date.notna() & (ca.exercise_ratio > 0)].copy()
ca["grp"] = np.where(ca.issue_method_name_vi.str.startswith("Quyền mua"), "B_rights", "A_bonus_stockdiv")
ca["f"] = 1 + ca.exercise_ratio
ca = ca.groupby(["ticker", "exright_date", "grp"], as_index=False)["f"].max()   # dòng trùng cùng ngày: lấy 1
leds = [a.split("=", 1) for a in sys.argv[1:]]
buys = {}
for lab, p in leds:
    T = pd.read_csv(p, low_memory=False); T = T[(T.record_type == "TX") & (T.book == "LAG") & (T.action == "buy")
                                               & T.play_type.isin(["LAG_HI", "LAG_LO"])]
    T["ymd"] = pd.to_datetime(T.ymd); T["cost"] = T.buy_amount.astype(float) + T.fee.astype(float)
    buys[lab] = T.groupby(["ticker", "ymd"], as_index=False).agg(cost=("cost", "sum"), n=("cost", "size"),
                                                                  hid=("holding_id", "first"))
tks = sorted(set().union(*[set(b.ticker) for b in buys.values()]))
con = duckdb.connect()
px = con.sql(f"""SELECT ticker, CAST(time AS DATE) AS time, Volume, Price, Close FROM read_parquet('{WC}/data/bq_cache_asof20260729_postrestate/ticker/*.parquet')
 WHERE ticker IN ({','.join(repr(t) for t in tks)})""").df()
px["time"] = pd.to_datetime(px.time); px = px.sort_values(["ticker", "time"], kind="mergesort").reset_index(drop=True)
px["PxAdv"] = px.Price.fillna(px.Close)
rows, chk = [], []
for tk, g in px.groupby("ticker", sort=False):
    g = g.reset_index(drop=True); t = g.time.values; V = g.Volume.astype(float).values; P = g.PxAdv.values
    ev = ca[ca.ticker == tk]
    # F_cum[i] = Π f của sự kiện ex ≤ t[i]  ⇒ F(d→t-1) = F_cum[t-1]/F_cum[d]
    fcum = np.ones(len(g)); evpos = []
    for _, e in ev.iterrows():
        j = np.searchsorted(t, np.datetime64(e.exright_date))      # phiên đầu tiên ≥ ex
        if j >= len(g): continue
        Rp = np.nan
        if 1 <= j < len(g) - 1 and g.Close[j-1] > 0 and g.Close[j+1] > 0:
            k0, k1 = g.Price[j-1] / g.Close[j-1], g.Price[j+1] / g.Close[j+1]
            if k1 > 0: Rp = k0 / k1; chk.append((tk, e.grp, e.f, Rp))
        use = (e.grp == "A_bonus_stockdiv" and (EVSET != "Av" or (Rp == Rp and abs(np.log(Rp / e.f)) <= 0.05))) \
              or (e.grp == "B_rights" and EVSET == "AB")
        if use: fcum[j:] *= e.f; evpos.append((j, e.grp, e.f))
    for lab, b in buys.items():
        for _, x in b[b.ticker == tk].iterrows():
            i = np.searchsorted(t, np.datetime64(x.ymd))
            if i >= len(g) or t[i] != np.datetime64(x.ymd) or i < 21: continue
            lo = max(0, i - 60); w = V[lo:i]; ok = ~np.isnan(w)
            if ok.sum() < 20: continue
            adv_pit = np.median(w[ok]) * P[i-1]
            adv_adj = np.median((w * fcum[i-1] / fcum[lo:i])[ok]) * P[i-1]
            hit = [(gp, f) for j, gp, f in evpos if lo < j <= i - 1]           # ex trong cửa sổ (t-60, t-1]
            rows.append(dict(led=lab, ticker=tk, ymd=x.ymd, cost=x.cost, adv_pit=adv_pit, adv_adj=adv_adj,
                             grp=("+".join(sorted({h[0] for h in hit})) if hit else "none"), hid=x.hid))
R = pd.DataFrame(rows); R["ratio"] = R.adv_adj / R.adv_pit
R["bind"] = R.cost >= 0.999 * 0.20 * R.adv_pit
R["miscap"] = R.bind & (R.ratio > 1.001)          # trần pit ràng buộc VÀ trần đúng (adj) rộng hơn
R["miscap5"] = R.bind & (R.ratio > 1.05)          # ... rộng hơn >5% (đáng kể)
C = pd.DataFrame(chk, columns=["ticker", "grp", "f", "R"]); C["lr"] = np.log(C.R / C.f)
print("Kiểm hệ số sự kiện bằng giá (R=k(ex-1)/k(ex+1) so với 1+r), sự kiện có trong cache:")
for gp, c in C.groupby("grp"):
    print(f"  {gp}: n={len(c)}  |log(R/f)|≤0,05: {(c.lr.abs() <= 0.05).mean():.1%}  median log(R/f)={c.lr.median():+.4f}")
for lab, _ in leds:
    r = R[R.led == lab]; N = len(r); hid = r.hid.nunique()
    print(f"\n=== {lab}: {N} (mã,ngày) mua LAG, {r.ticker.nunique()} mã, {hid} lệnh (holding) ===")
    print(f"  cap ràng buộc (pit): {r.bind.sum()} (mã,ngày) = {r.bind.mean():.1%}; số lệnh có ≥1 ngày bị cap: {r[r.bind].hid.nunique()}")
    for gp in ["A_bonus_stockdiv", "B_rights", "A_bonus_stockdiv+B_rights"]:
        a = r[r.grp == gp]
        if not len(a): continue
        q = a.ratio.quantile([.5, .95]).values
        print(f"  {gp}: {len(a)} (mã,ngày) = {len(a)/N:.2%} | {a.ticker.nunique()} mã | adj/pit median {q[0]:.3f} p95 {q[1]:.3f} max {a.ratio.max():.3f}"
              f" | cap ràng buộc {a.bind.sum()} | cap SAI (bind ∧ adj>pit) {a.miscap.sum()} (mã,ngày), {a[a.miscap].hid.nunique()} lệnh; >5%: {a.miscap5.sum()} / {a[a.miscap5].hid.nunique()} lệnh")
    aff = r[r.grp != "none"]
    print(f"  TỔNG chịu ảnh hưởng: {len(aff)} = {len(aff)/max(N,1):.2%}; ratio>1,05: {(aff.ratio>1.05).sum()}; "
          f"cap sai: {aff.miscap.sum()} (mã,ngày) / {aff[aff.miscap].hid.nunique()} lệnh / {hid} lệnh LAG ⇒ {aff[aff.miscap].hid.nunique()/max(hid,1):.2%}; "
          f">5%: {aff.miscap5.sum()} (mã,ngày) / {aff[aff.miscap5].hid.nunique()} lệnh ⇒ {aff[aff.miscap5].hid.nunique()/max(hid,1):.2%}")
    # thiếu hụt vốn mua trong ngày bị cap sai: (min(remaining?, 0,2×adj) − cost) — cận trên = 0,2×(adj−pit)
    m = aff[aff.miscap]; print(f"  vốn mua thêm CẬN TRÊN nếu trần đúng (Σ0,2×(adj−pit) ngày cap sai) = {(0.2*(m.adv_adj-m.adv_pit)).sum()/1e9:.2f} tỷ"
          f" vs Σ cost mua LAG {r.cost.sum()/1e9:.1f} tỷ ⇒ {(0.2*(m.adv_adj-m.adv_pit)).sum()/r.cost.sum():.2%}")
    ctl = r[r.grp == "none"]; print(f"  control (không sự kiện): adj/pit max |log| = {np.abs(np.log(ctl.ratio)).max():.2e} (phải 0)")
R.to_csv(f"logs/adv_split_rows_{EVSET}.csv", index=False)
print(f"\nADV_EV_SET={EVSET}")
