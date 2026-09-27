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

HAIRCUT_PP = 2.04          # median(SBV low >12-24M - lien NH 3M), 143 thang 2014-01..2026-08
HAIRCUT_TENOR = "3 tháng"  # tenor dung de hieu chinh haircut (dispatch W1 muc 2)
FLOOR_TENOR = "1 tháng"    # tang 2 (ke hoach §2.2)

SPOT_RATE_PCT = 8.543      # carry egg DNSE do that, Job U Taylor_20260927_085628
SPOT_VALID_FROM = date(2026, 8, 18)   # ngay dau tien egg.totalValue != 0
SPOT_VALID_TO = date(2027, 3, 31)     # ke hoach §2.2: chi cho "ky nhin truoc ngan (<= 6 thang)"

TIERS = ("baseline", "floor", "spot")


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

    df = dep.join(ib, how="outer").sort_index()
    df.index.name = "month"
    return df


def monthly_table(data_dir: str | None = None) -> pd.DataFrame:
    """Bang thang da dan xuat: sbv_low, ib_*, baseline_pct, floor_pct. KHONG co PIT o day."""
    df = _load(data_dir or DATA_DIR).copy()
    df["baseline_pct"] = (df["sbv_low"] - HAIRCUT_PP).clip(lower=0.0)
    df["floor_pct"] = df["ib_" + FLOOR_TENOR].clip(lower=0.0)
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

    col = "baseline_pct" if tier == "baseline" else "floor_pct"
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

    if len(sys.argv) > 1 and sys.argv[1] == "--haircut":
        for tn in ("qua đêm", "1 tháng", "3 tháng", "6 tháng"):
            print(json.dumps(measure_haircut(tenor=tn), ensure_ascii=False))
        raise SystemExit(0)

    t = monthly_table()
    print(f"HAIRCUT_PP={HAIRCUT_PP} ({HAIRCUT_TENOR})  FLOOR_TENOR={FLOOR_TENOR}  SPOT={SPOT_RATE_PCT}")
    print(t.loc["2014-01":, ["sbv_low", "baseline_pct", "ib_" + FLOOR_TENOR, "floor_pct"]].to_string())
    for d in ("2014-02-03", "2020-12-31", "2022-12-01", "2026-09-27"):
        print(d, "baseline", round(r_idle(d), 3), "floor", round(r_idle(d, "floor"), 3))
