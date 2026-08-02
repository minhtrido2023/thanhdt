"""Dung panel ma-ngay (month-end) cho nghien cuu: IC cua value co doi theo DT5G state?

Nguon (da tra mike/kb/data_registry/ truoc khi chon):
  - tav2_bq.ticker            (CANONICAL, price-volume + fundamentals joined)
  - tav2_mike.universe_pit    (CANONICAL, point-in-time membership — KHONG dung ticker_prune)
  - tav2_bq.fa_ratings_8l     (CANONICAL, 8L rating point-in-time theo eff_date)
  - tav2_bq.vnindex_5state_dt5g_live (DT5G PRODUCTION — KHONG dung bare vnindex_5state)

Ngay quan sat = phien giao dich CUOI moi thang => forward return T+20 gan nhu KHONG chong lan
(20 phien ~ 1 thang) => chuoi he so Fama-MacBeth coi nhu doc lap theo thang.

Tai su dung logic value cua rating_8l.py (VALUE_VERSION=v3_div) o muc co the tai lap PIT.
Sai lech CO CHU DICH (khai bao trong bao cao):
  - THIEU lens ps (1/PS): tav2_bq.ticker khong co Revenue/PS => coverage-aware chuan hoa lai
    trong so con lai. Anh huong route COMPOUNDER/RETAIL.
  - cfo_normy dung norm CF_OA_5Y/5 (ticker khong co CF_OA_3Y) thay vi 3Y.
  - BO peak-earnings guard (can ROE_Trailing, khong co trong ticker).
  - Khong co forensic/moat registry PIT => khong ap (chung deu la cap rating, khong phai value).
"""
import numpy as np, pandas as pd, os

HERE = os.path.dirname(os.path.abspath(__file__))
LIQ_MIN = 3e9          # >=3 ty VND/phien (Trading_Value_1M_P50) — dung nguong production
DA_HEAVY_SET = {"ACV","GMD","HAH","PHP","VSC","PVT","PVP","VOS","CII","HHV","CTI","PC1",
                "FOX","VGI","PVD","BWE","REE","VGC","KSV","MSR","VPL","HAG","AAA"}
VR_W = {"COMPOUNDER": (.45,.30,.25,.00,.15), "CYCLICAL": (.40,.60,.00,.00,.00),
        "RETAIL": (.35,.20,.45,.00,.15), "D&A_HEAVY": (.35,.30,.00,.35,.15),
        "POWER": (.35,.30,.00,.35,.15)}          # (ey, cfy, ps, eveb, dy) — v3_div
LENS = ["ey_pct", "cfy_pct", "ps_pct", "eveb_pct", "dy_pct"]


def asof_rating(panel, fa):
    """rating/route hieu luc tai ngay d = ban ghi fa_ratings_8l moi nhat co time <= d."""
    fa = fa.sort_values("time")
    out = []
    for tk, g in panel.groupby("ticker", sort=False):
        f = fa[fa.ticker == tk]
        if f.empty:
            continue
        m = pd.merge_asof(g.sort_values("d"), f[["time", "route", "rating"]],
                          left_on="d", right_on="time", direction="backward")
        out.append(m)
    return pd.concat(out, ignore_index=True)


def route_pct(df, col):
    """Y HET _route_pct_raw() cua rating_8l: percentile trong route, fallback global neu route <5 quan sat."""
    rr = df.groupby("route")[col].transform(
        lambda g: g.rank(pct=True) if g.notna().sum() >= 5 else pd.Series(np.nan, index=g.index))
    gg = df[col].rank(pct=True)
    m = rr.isna() & df[col].notna()
    rr = rr.copy(); rr[m] = gg[m]
    return rr


def is_consumer(c):
    return pd.notna(c) and ((3500 <= c < 3800) or (5300 <= c < 5400))


def build():
    p = pd.read_csv(os.path.join(HERE, "panel_raw.csv"), parse_dates=["d", "d20", "d60"])
    fa = pd.read_csv(os.path.join(HERE, "fa8l.csv"), parse_dates=["time"])
    p = asof_rating(p, fa)
    p = p[p.rating.notna()].copy()

    # --- cong production: rating<=3 AND liq>=3ty ---
    p = p[(p.rating <= 3) & (p.liq >= LIQ_MIN)].copy()

    # --- sua he so gia: PE/PCF/EVEB luu theo Close DIEU CHINH -> quy ve gia thuc te (Price) ---
    f = np.where(p.Close > 0, p.Price / p.Close, 1.0)
    for c in ("PE", "PCF", "EVEB"):
        p[c] = np.where(p[c] > 0, p[c] * f, p[c])

    p["earn_yield"] = np.where(p.PE > 0, 1.0 / p.PE, np.nan)
    p["cfo_yield"] = np.where(p.PCF > 0, 1.0 / p.PCF, np.nan)
    ttm_cf = p[["CF_OA_P0", "CF_OA_P1", "CF_OA_P2", "CF_OA_P3"]].sum(axis=1, min_count=1)
    norm_cf = p["CF_OA_5Y"] / 5.0
    p["cfo_normy"] = np.where((p.PCF > 0) & (ttm_cf > 0) & (norm_cf > 0),
                              (1.0 / p.PCF) * np.clip(norm_cf / ttm_cf, 0.3, 3.0), np.nan)
    p["eveb_yield"] = np.where(p.EVEB > 0, 1.0 / p.EVEB, np.nan)
    p["div_yield"] = np.where((p.Price > 0) & p.Dividend_Min3Y.notna(), p.Dividend_Min3Y / p.Price, np.nan)
    p["pb_z"] = np.where(p.PB_SD5Y > 0, (p.PB - p.PB_MA5Y) / p.PB_SD5Y, np.nan)

    p["val_route"] = np.where(p.ticker.isin(DA_HEAVY_SET), "D&A_HEAVY",
                     np.where((p.route == "COMPOUNDER") & p.ICB_Code.map(is_consumer), "RETAIL", p.route))
    p["cfy_input"] = np.where(p.route == "CYCLICAL", p.cfo_yield, p.cfo_normy)

    # --- percentile cross-sectional TUNG NGAY (trong route) ---
    parts = []
    for d, g in p.groupby("d", sort=True):
        g = g.copy()
        g["ey_pct"] = route_pct(g, "earn_yield")
        g["cfy_pct"] = route_pct(g, "cfy_input")
        g["eveb_pct"] = route_pct(g, "eveb_yield")
        g["dy_pct"] = route_pct(g, "div_yield")
        g["ps_pct"] = np.nan                       # lens ps khong tai lap duoc tu tav2_bq.ticker
        parts.append(g)
    p = pd.concat(parts, ignore_index=True)

    # --- composite coverage-aware (Sum w*pct present / Sum w present) ---
    P = p[LENS].to_numpy()
    W = np.array([VR_W.get(vr, VR_W["COMPOUNDER"]) for vr in p.val_route])
    pres = ~np.isnan(P)
    num = np.nansum(np.where(pres, P * W, 0.0), axis=1)
    den = np.nansum(np.where(pres, W, 0.0), axis=1)
    comp = np.where(den > 0, num / den, np.nan)
    track = (np.where(p.CF_OA_5Y.fillna(-9) > 0, 0.03, 0.0)
             + np.where(p.ROE_Min5Y.fillna(-9) > 0.10, 0.03, 0.0))
    comp = comp + 0.10 * (p.pb_z <= -1).astype(float).to_numpy() + track
    comp = np.where(p.PB.to_numpy() < 0, 0.0, comp)
    p["vs_proxy"] = np.clip(comp, 0, 1)

    # --- forward return (Close DIEU CHINH -> da gom co tuc/chia tach) ---
    p["fwd20"] = p.c20 / p.Close - 1.0
    p["fwd60"] = p.c60 / p.Close - 1.0
    gap20 = (p.d20 - p.d).dt.days
    gap60 = (p.d60 - p.d).dt.days
    p.loc[~gap20.between(20, 50), "fwd20"] = np.nan      # loai truong hop nghi giao dich lam lech offset
    p.loc[~gap60.between(70, 130), "fwd60"] = np.nan

    p.to_csv(os.path.join(HERE, "panel.csv.gz"), index=False, compression="gzip")
    n_ok = p.dropna(subset=["ey_pct", "fwd20"])
    print(f"panel: {len(p)} dong, {p.d.nunique()} ngay, {p.ticker.nunique()} ma")
    print(f"  co ca ey_pct & fwd20: {len(n_ok)} dong / {n_ok.d.nunique()} ngay")
    print("  ma/ngay:", p.groupby('d').ticker.count().describe()[["min", "25%", "50%", "75%", "max"]].round(0).to_dict())
    print("  coverage lens (%):", {c: round(100 * p[c].notna().mean(), 1) for c in
                                   ["ey_pct", "cfy_pct", "eveb_pct", "dy_pct", "vs_proxy"]})
    print("  so thang moi state:", p.groupby("state").d.nunique().to_dict())
    return p


if __name__ == "__main__":
    build()
