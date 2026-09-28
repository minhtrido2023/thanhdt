#!/usr/bin/env python3
"""Proxy lai tien nhan roi (idle-cash carry) cho backtest — thay gia dinh 0%/nam.

KHONG WIRE VAO ENGINE. Module doc-only, dung cho R&D (W1 cua
`mike/kb/projects/custom30v-revalidation-plan-20260927.md`, user duyet §7 ngay 2026-09-27).

Ba tang (dung dung ten user da duyet o §2.2 cua ke hoach):

  baseline : SBV "tren 12 thang den 24 thang" muc THAP NHAT - HAIRCUT_PP, clip >= 0.
             Dung cho MOI so pin / moi so sanh tien-vs-equity.
  floor    : max(0, lai suat BQ lien NH ky han 1 thang). Kich ban stress "tien chi duoc
             lai qua money-market, mat het spread san pham".
  spot     : carry egg DNSE do that (8.543%/nam). CHI cho cua so nhin truoc ngan;
             goi voi ngay ngoai khoang -> raise ValueError.
  dep1m    : lai suat HUY DONG ky han 1 THANG, khach CA NHAN, binh quan nhom Big 4 (FiinPro).
             Day la tier user CHOT 2026-09-27 23:58 ICT lam quy uoc pin ("tien mat thi neo theo
             lai suat huy dong 1 thang"). HAI DOAN, KHAC NHAU VE BAN CHAT:
               2019-02..2026-09 = SO THAT do FiinPro cong bo (92 thang, moi thang chup ngay 15).
               truoc 2019-02     = DUNG LAI  = sbv_low + DEP1M_OFFSET_PP. KHONG phai so cong bo.
             Route FiinPro tra HTTP 500 cho moi ngay <= 2018-12 (Mike do 2014/2015/2016/2018 deu
             rong) va trial het han 2026-09-28 ⇒ KHONG the keo them. Doan dung lai phu 53/150
             thang cua cua so backtest (2014-01..2026-06 — dung con so ENGINE TU IN qua
             `dep1m_coverage()`; ban dau docstring ghi "54/143", sai ca tu va mau, quant-skeptic
             bat 2026-09-27) ⇒ moi ket luan phai kem bang bat dinh offset (p25/p75).

HAIRCUT_PP = 2.04 — KHONG phai con so quy uoc 1.0pp trong ban ke hoach. Do that tren
143 thang 2014-01..2026-08: median(SBV low >12-24M - lien NH 3M) = +2.040pp
(p25 +0.360, p75 +3.150, mean +1.587, sd 1.923, 21.0% thang am). Dung MEDIAN theo yeu cau
dispatch W1 muc 2 — trung vi ben voi duoi (chuoi lien NH la mot phien duy nhat moi thang,
xem "Bay" ben duoi). Do bang `idle_rate_proxy_selfcheck.py --haircut`.

POINT-IN-TIME (bat buoc, la ly do module nay ton tai):
  Moc thang T CHI duoc dung tu ngay dau thang T+1. SBV cong bo bao cao "Dien bien lai suat
  thang T" trong thang T+1 — nen quy uoc nay la CHAN TREN cua do tuoi that (SBV thuong cong bo
  giua thang T+1, tuc thuc te con tre hon). Khong co gia tri nao cua thang T ro ri vao ngay
  trong thang T.

Nguon (snapshot mot lan 2026-09-27, FiinPro-X trial het han 2026-09-28):
  `mike/agents/Taylor/research/idle_cash_proxy_20260927/`
  - fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv
  - fiinprox_interbank_avg_rate_monthly_2014_2026.csv
Registry: `mike/kb/data_registry/macro/fiinprox_rates_snapshot_20260927.md`.

BAY (mang theo khi bao so):
 1. Chuoi lien NH KHONG phai binh quan thang — la ban in cua MOT phien cuoi thang
    (2026-09 khop 7/7 tenor voi bang SBV dttktt ngay 24/09/2026). Lai suat O/N VN dao dong
    0%..16.39% trong 2026 ⇒ mot phien khong dai dien cho thang. Vi vay tang `floor` la
    MOT KICH BAN, khong phai uoc luong trung tam.
 2. Nhan FiinPro "binh quan tren 12 thang" GAY NHAM: gia tri khop chinh xac o cua
    "Tren 12 thang den 24 thang" cua bang SBV, KHONG bao gom cua "Tren 24 thang", va la
    HAI DAU MUT cua khoang lai suat pho bien, khong phai mot binh quan gia quyen.
 3. `floor` KHONG luon <= `baseline` (2022-11, 2025-12, 2026-06...). No la kich ban khac,
    khong phai chan duoi theo thu tu. Muon chan duoi thuc su thi lay min() o phia goi —
    module khong tu y lam thay.
 4. Doi chieu cheo chi phu 2025-11..2026-09 (3 moc/chuoi, lech 0.00pp). Doan 2014..2025-10
    CHUA co nguon doc lap xac minh — xem REPORT.md muc 1.
 5. Tier `dep1m` KHONG dong nhat ve chat luong theo thoi gian: 2019-02 tro di la so cong bo,
    truoc do la SO DUNG LAI tu mot offset trung vi do tren 90 thang overlap. Lien ngan hang
    KHONG bac cau duoc (median dep1m - ibor1M = -0.240 nhung sd 2.472, corr -0.141) — chi
    sbv_low bac cau duoc (median -2.525, sd 0.883, corr +0.619). Do lai bang
    `measure_dep1m_offset()`.
 6. 8 thang trong doan dung lai KHUYET sbv_low (2015-02, 2016-02, 2016-08, 2017-01..03, 2017-05,
    2017-09) ⇒ duoc forward-fill tu thang truoc, y nhu hai tier kia. Day la ff cua mot moc CHINH
    SACH da cong bo (dung PIT), KHONG phai noi suy tuong lai. `monthly_table()` ghi nhan bang cot
    `dep1m_src` (real / recon / recon_ff) de dem duoc.
"""
from __future__ import annotations

import os
from datetime import date, datetime
from functools import lru_cache

import numpy as np
import pandas as pd

_DEFAULT_DIR = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/idle_cash_proxy_20260927"
DATA_DIR = os.environ.get("IDLE_RATE_PROXY_DIR", _DEFAULT_DIR)

SBV_CSV = "fiinprox_sbv_avg_deposit_rate_monthly_2011_2026.csv"
IB_CSV = "fiinprox_interbank_avg_rate_monthly_2014_2026.csv"
DEP1M_CSV = "fiinprox_deposit_1m_big4_monthly_2019_2026.csv"

HAIRCUT_PP = 2.04          # median(SBV low >12-24M - lien NH 3M), 143 thang 2014-01..2026-08
HAIRCUT_TENOR = "3 tháng"  # tenor dung de hieu chinh haircut (dispatch W1 muc 2)
FLOOR_TENOR = "1 tháng"    # tang 2 (ke hoach §2.2)

SPOT_RATE_PCT = 8.543      # carry egg DNSE do that, Job U Taylor_20260927_085628
SPOT_VALID_FROM = date(2026, 8, 18)   # ngay dau tien egg.totalValue != 0
SPOT_VALID_TO = date(2027, 3, 31)     # ke hoach §2.2: chi cho "ky nhin truoc ngan (<= 6 thang)"

# Tier `dep1m` (user chot 2026-09-27 23:58 ICT). Offset dung de DUNG LAI doan truoc 2019-02:
# median(dep1m - sbv_low) do tren 90 thang overlap 2019-02..2026-08 = -2.525pp
# (mean -2.857, sd 0.883, p25 -3.400, p75 -2.300, corr +0.619). Dung MEDIAN theo yeu cau dispatch.
# Ghi de qua env chi de do BANG BAT DINH cua cau (chan p25 / p75) — KHONG de "tune".
DEP1M_OFFSET_PP = float(os.environ.get("IDLE_DEP1M_OFFSET_PP", "-2.525"))
DEP1M_REAL_FROM = "2019-02"        # thang dau tien co SO THAT (FiinPro tra 500 cho moi ngay <= 2018-12)

TIERS = ("baseline", "floor", "spot", "dep1m")


def _to_date(d) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, pd.Timestamp):
        return d.date()
    return pd.Timestamp(d).date()


def _pit_month(d: date) -> str:
    """Thang moi nhat duoc PHEP dung tai ngay `d` = thang TRUOC thang chua `d`."""
    y, m = d.year, d.month
    if m == 1:
        return f"{y - 1:04d}-12"
    return f"{y:04d}-{m - 1:02d}"


@lru_cache(maxsize=4)
def _load(data_dir: str) -> pd.DataFrame:
    """Bang thang (index 'YYYY-MM') voi cot sbv_low / sbv_high / ib_<tenor>."""
    s = pd.read_csv(os.path.join(data_dir, SBV_CSV))
    s["hl"] = np.where(s["series"].str.contains("thấp"), "sbv_low", "sbv_high")
    dep = s.pivot(index="period", columns="hl", values="rate_pct")

    i = pd.read_csv(os.path.join(data_dir, IB_CSV))
    i = i[i["series"].str.startswith("Lãi suất")].copy()   # bo cac dong "Doanh so ..." (VND, khong phai %)
    i["ten"] = "ib_" + i["series"].str.replace("Lãi suất BQ liên NH kỳ hạn ", "", regex=False)
    i["m"] = i["period"].str.slice(0, 7)
    ib = i.pivot(index="m", columns="ten", values="rate_pct")

    d1 = pd.read_csv(os.path.join(data_dir, DEP1M_CSV))
    d1 = d1[d1["series"] == "big4_1m_individual"].copy()      # mot chuoi duy nhat; loc tuong minh
    d1m = d1.set_index("period")["rate_pct"].rename("dep1m_real")

    df = dep.join(ib, how="outer").join(d1m, how="outer").sort_index()
    df.index.name = "month"
    return df


def monthly_table(data_dir: str | None = None) -> pd.DataFrame:
    """Bang thang da dan xuat: sbv_low, ib_*, baseline_pct, floor_pct. KHONG co PIT o day."""
    df = _load(data_dir or DATA_DIR).copy()
    df["baseline_pct"] = (df["sbv_low"] - HAIRCUT_PP).clip(lower=0.0)
    df["floor_pct"] = df["ib_" + FLOOR_TENOR].clip(lower=0.0)
    # dep1m: SO THAT tu DEP1M_REAL_FROM tro di; truoc do DUNG LAI tu sbv_low + offset.
    # KHONG back-fill so that ve qua khu (se la nhin trom tuong lai) va KHONG dung recon de
    # lap cho thang khuyet cua doan that (de ham r_idle ff nhu hai tier kia, xem BAY 6).
    real = df["dep1m_real"].where(df.index >= DEP1M_REAL_FROM)
    recon = (df["sbv_low"] + DEP1M_OFFSET_PP).clip(lower=0.0).where(df.index < DEP1M_REAL_FROM)
    df["dep1m_pct"] = real.combine_first(recon)
    df["dep1m_src"] = np.where(real.notna(), "real",
                               np.where(recon.notna(), "recon", ""))
    return df


def measure_haircut(data_dir: str | None = None, tenor: str = HAIRCUT_TENOR) -> dict:
    """Do lai khoang cach (SBV low >12-24M - lien NH <tenor>) — bang chung cho HAIRCUT_PP."""
    df = _load(data_dir or DATA_DIR)
    d = (df["sbv_low"] - df["ib_" + tenor]).dropna()
    return {
        "tenor": tenor, "n": int(len(d)),
        "first": str(d.index[0]), "last": str(d.index[-1]),
        "median": float(d.median()), "p25": float(d.quantile(0.25)),
        "p75": float(d.quantile(0.75)), "mean": float(d.mean()),
        "sd": float(d.std()), "frac_negative": float((d < 0).mean()),
    }


def measure_dep1m_offset(data_dir: str | None = None, ref: str = "sbv_low") -> dict:
    """Do offset (dep1m THAT - chuoi bac cau) tren doan overlap — bang chung cho DEP1M_OFFSET_PP.

    ref = "sbv_low" (cau DUNG DUOC) hoac "ib_1 tháng" (cau KHONG dung duoc, giu lai de chung minh).
    """
    df = _load(data_dir or DATA_DIR)
    d = (df["dep1m_real"] - df[ref]).dropna()
    j = df[["dep1m_real", ref]].dropna()
    return {
        "ref": ref, "n": int(len(d)),
        "first": str(d.index[0]), "last": str(d.index[-1]),
        "median": float(d.median()), "mean": float(d.mean()),
        "sd": float(d.std()), "p25": float(d.quantile(0.25)), "p75": float(d.quantile(0.75)),
        "corr": float(j["dep1m_real"].corr(j[ref])),
    }


def dep1m_coverage(data_dir: str | None = None, first_month: str = "2014-01",
                   last_month: str = "2026-06") -> dict:
    """Dem thang THAT vs DUNG LAI vs FF trong mot cua so — so phai bao cao kem moi ket luan."""
    tbl = monthly_table(data_dir)
    months = [f"{y}-{m:02d}" for y in range(int(first_month[:4]), int(last_month[:4]) + 1)
              for m in range(1, 13)]
    months = [m for m in months if first_month <= m <= last_month]
    real = [m for m in months if m in tbl.index and tbl.loc[m, "dep1m_src"] == "real"]
    recon = [m for m in months if m in tbl.index and tbl.loc[m, "dep1m_src"] == "recon"]
    ff = [m for m in months if m not in tbl.index or tbl.loc[m, "dep1m_src"] == ""]
    return {"window": f"{first_month}..{last_month}", "n_months": len(months),
            "n_real": len(real), "n_recon": len(recon), "n_ff": len(ff), "ff_months": ff}


def r_idle(d, tier: str = "baseline", data_dir: str | None = None) -> float:
    """Lai tien nhan roi %/nam tai ngay `d`, theo `tier` in {baseline, floor, spot}.

    baseline/floor: point-in-time — chi doc moc thang <= thang truoc thang cua `d`,
    forward-fill neu thang do khuyet. Raise neu `d` truoc moc dau tien co du lieu.
    spot: hang so do that, raise neu `d` ngoai [SPOT_VALID_FROM, SPOT_VALID_TO].
    """
    if tier not in TIERS:
        raise ValueError(f"tier khong hop le: {tier!r}; phai thuoc {TIERS}")
    dd = _to_date(d)

    if tier == "spot":
        if not (SPOT_VALID_FROM <= dd <= SPOT_VALID_TO):
            raise ValueError(
                f"tier 'spot' chi hop le trong [{SPOT_VALID_FROM}, {SPOT_VALID_TO}] "
                f"(carry egg do that 2026-08-18 tro di, ke hoach §2.2 gioi han cua so nhin "
                f"truoc <= 6 thang). Ngay yeu cau: {dd}. Dung tier 'baseline' cho lich su."
            )
        return SPOT_RATE_PCT

    col = {"baseline": "baseline_pct", "floor": "floor_pct", "dep1m": "dep1m_pct"}[tier]
    tbl = monthly_table(data_dir)[col].dropna()
    cutoff = _pit_month(dd)
    avail = tbl.loc[:cutoff]              # <= cutoff: PIT + forward-fill trong mot buoc
    if len(avail) == 0:
        raise ValueError(
            f"khong co moc nao <= {cutoff} cho tier {tier!r} (moc som nhat "
            f"{tbl.index[0]}); ngay yeu cau {dd} truoc khi chuoi bat dau."
        )
    return float(avail.iloc[-1])


def r_idle_series(dates, tier: str = "baseline", data_dir: str | None = None) -> np.ndarray:
    """r_idle cho mot chuoi ngay, tra %/nam. Cung dung ham r_idle nen cung dam bao PIT."""
    return np.array([r_idle(d, tier=tier, data_dir=data_dir) for d in dates], dtype=float)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--dep1m":
        print(json.dumps(measure_dep1m_offset(), ensure_ascii=False))
        print(json.dumps(measure_dep1m_offset(ref="ib_1 tháng"), ensure_ascii=False))
        print(json.dumps(dep1m_coverage(), ensure_ascii=False))
        t = monthly_table()
        print(t.loc["2014-01":, ["sbv_low", "dep1m_real", "dep1m_pct", "dep1m_src"]].to_string())
        raise SystemExit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--haircut":
        for tn in ("qua đêm", "1 tháng", "3 tháng", "6 tháng"):
            print(json.dumps(measure_haircut(tenor=tn), ensure_ascii=False))
        raise SystemExit(0)

    t = monthly_table()
    print(f"HAIRCUT_PP={HAIRCUT_PP} ({HAIRCUT_TENOR})  FLOOR_TENOR={FLOOR_TENOR}  SPOT={SPOT_RATE_PCT}")
    print(t.loc["2014-01":, ["sbv_low", "baseline_pct", "ib_" + FLOOR_TENOR, "floor_pct"]].to_string())
    for d in ("2014-02-03", "2020-12-31", "2022-12-01", "2026-09-27"):
        print(d, "baseline", round(r_idle(d), 3), "floor", round(r_idle(d, "floor"), 3))
