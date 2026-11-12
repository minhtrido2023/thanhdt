#!/usr/bin/env python3
"""GĐ2-B (job Taylor_20261112_125912): H5 kiểm lại THEO EPISODE trên chuỗi lãi PIT thật.
Chuỗi: fiinprox dep1m (Big-4 CÁ NHÂN KỲ HẠN 1 THÁNG; PIT thật 2019-02→2026-09; mốc tháng T dùng từ ngày 1 tháng T+1).
KHÁC kỳ hạn 12T của hurdle_pit (12T, 26 mốc neo hồi tố ⇒ không PIT). CCTG (cctg_rate_vn): chỉ 1 anchor + 3 mốc từ 2026-10 ⇒ không dựng được episode.
Trạng thái 'TĂNG' tại ngày t: dep1m_known(t) − dep1m_known(t−91d) ≥ BAND. Episode = cụm tháng liên tiếp ở trạng thái TĂNG.
Δ = TB excess sự kiện TRONG episode − TB excess sự kiện NGOÀI mọi episode (cùng vùng phủ PIT thật, 2019-03→). N độc lập = SỐ EPISODE."""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
W = "/home/trido/thanhdt/WorkingClaude"
CSV = W + "/mike/agents/Taylor/research/idle_cash_proxy_20260927/fiinprox_deposit_1m_big4_monthly_2019_2026.csv"
TAG = sys.argv[1] if len(sys.argv) > 1 else "liqz_all"

def known_series():
    s = pd.read_csv(CSV)
    s["avail"] = pd.to_datetime(s.period + "-01") + pd.offsets.MonthBegin(1)      # tháng T dùng từ ngày 1 tháng T+1
    return s[["period", "avail", "rate_pct"]].sort_values("avail").reset_index(drop=True)

def known_at(s, dts):
    x = pd.DataFrame({"t": pd.to_datetime(dts)}).reset_index().sort_values("t")
    m = pd.merge_asof(x, s.rename(columns={"avail": "t"}), on="t")
    return m.set_index("index").reindex(range(len(x))).rate_pct.values

def episodes_from_months(s, band):
    """trạng thái tháng m (đầu tháng): known(m) − known(m−91d) ≥ band. Trả danh sách (start, end) theo tháng liên tiếp."""
    ms = pd.date_range("2019-05-01", "2026-06-01", freq="MS")          # 2019-05 là tháng đầu có đủ lùi 91d trong PIT thật (avail đầu 2019-03-01)
    cur = known_at(s, ms); prev = known_at(s, ms - pd.Timedelta(days=91))
    st = ((cur - prev) >= band) if band > 0 else ((cur - prev) > 1e-9)      # band 0 = TĂNG THỰC SỰ (>0), không tính phẳng
    eps, start = [], None
    for m, f in zip(ms, st):
        if f and start is None: start = m
        if not f and start is not None: eps.append((start, last)); start = None
        last = m
    if start is not None: eps.append((start, last))
    return eps, pd.DataFrame({"m": ms, "cur": cur, "prev": prev, "up": st})

def main():
    s = known_series()
    E = pd.read_csv(os.path.join(HERE, f"events_{TAG}.csv"), parse_dates=["sig_date"])
    E = E[E.sig_date >= "2019-05-01"].copy()                           # vùng phủ PIT thật (OOS 2020+ ⊂ vùng này; 2019-05→12 thuộc IS)
    E["chg"] = known_at(s, E.sig_date) - known_at(s, E.sig_date - pd.Timedelta(days=91))
    E["ym"] = E.sig_date.dt.to_period("M").dt.to_timestamp()
    E["ex_dm"] = E.excess_pp - E.groupby("year").excess_pp.transform("mean")      # khử mức năm
    out = {}
    lines = []
    for band in (0.2, 0.0):
        eps, mt = episodes_from_months(s, band)
        mt.to_csv(os.path.join(HERE, f"h5_months_{TAG}_band{band}.csv"), index=False)
        inep = np.zeros(len(E), bool); rows = []
        for (a, b) in eps:
            m = (E.ym >= a) & (E.ym <= b); inep |= m.values
        for (a, b) in eps:
            m = ((E.ym >= a) & (E.ym <= b)).values
            for bk in ("ALL", "BAL", "LAG"):
                sel = np.ones(len(E), bool) if bk == "ALL" else (E.book == bk).values
                i, o = sel & m, sel & ~inep
                rows.append(dict(band=band, episode=f"{a:%Y-%m}→{b:%Y-%m}", book=bk, n_in=int(i.sum()), n_out=int(o.sum()),
                                 mean_in=E.excess_pp[i].mean(), mean_out=E.excess_pp[o].mean(),
                                 d_raw=E.excess_pp[i].mean() - E.excess_pp[o].mean(),
                                 d_year_demeaned=E.ex_dm[i].mean() - E.ex_dm[o].mean(),
                                 years_in=",".join(map(str, sorted(E.year[i].unique())))))
        R = pd.DataFrame(rows)
        # leave-one-year-out (pooled all-episodes vs outside), bỏ từng năm
        loo = []
        for y in sorted(E.year.unique()):
            k = (E.year != y).values
            loo.append(dict(band=band, dropped_year=int(y), n_in=int((inep & k).sum()), n_out=int((~inep & k).sum()),
                            d_raw=E.excess_pp[inep & k].mean() - E.excess_pp[~inep & k].mean()))
        L = pd.DataFrame(loo)
        pooled = dict(band=band, n_episodes=len(eps), n_in=int(inep.sum()), n_out=int((~inep).sum()),
                      d_raw=E.excess_pp[inep].mean() - E.excess_pp[~inep].mean(),
                      d_year_demeaned=E.ex_dm[inep].mean() - E.ex_dm[~inep].mean())
        R.to_csv(os.path.join(HERE, f"h5_episodes_{TAG}_band{band}.csv"), index=False)
        L.to_csv(os.path.join(HERE, f"h5_loyo_{TAG}_band{band}.csv"), index=False)
        out[f"band{band}"] = dict(pooled=pooled, episodes=[f"{a:%Y-%m}→{b:%Y-%m}" for a, b in eps])
        print(f"== band {band}pp: {len(eps)} episode"); print(R[R.book == "ALL"].round(2).to_string()); print(R[R.book != "ALL"].round(2).to_string())
        print("pooled", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in pooled.items()})
        print(L.round(2).to_string())
    # Chuỗi dựng lại 2014-19 (tier baseline của idle_rate_proxy = sbv_low − haircut; KHÔNG phải số Big-4 công bố) — chỉ để thấy IS, KHÔNG dùng làm bằng chứng
    sys.path.insert(0, W)
    try:
        import idle_rate_proxy as I
        E2 = pd.read_csv(os.path.join(HERE, f"events_{TAG}.csv"), parse_dates=["sig_date"])
        E2 = E2[E2.sig_date < "2019-05-01"].copy()
        r0 = I.r_idle_series(E2.sig_date, tier="baseline"); r1 = I.r_idle_series(E2.sig_date - pd.Timedelta(days=91), tier="baseline")
        E2["chg_recon"] = r0 - r1
        up = E2.chg_recon >= 0.2
        out["recon_IS"] = dict(n_up=int(up.sum()), n_not=int((~up).sum()), mean_up=float(E2.excess_pp[up].mean()), mean_not=float(E2.excess_pp[~up].mean()))
        print("recon IS", out["recon_IS"])
    except Exception as e:
        out["recon_IS"] = f"không chạy được: {e}"
    json.dump(out, open(os.path.join(HERE, f"h5_summary_{TAG}.json"), "w"), indent=1, default=str)
    print(s.assign(chg=s.rate_pct.diff(3)).tail(0))

if __name__ == "__main__":
    main()
