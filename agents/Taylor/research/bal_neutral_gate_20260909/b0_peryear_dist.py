"""VONG 3 truc B — B0: la DAC TINH hay KHIEM KHUYET? Phan phoi lenh BAL theo tung nam 2014-2026.
job Taylor_20260909_121342, PAPER-ONLY, MO TA (khong treatment, khong tieu trial).
Nguon duy nhat: so lenh CCS Phase 0 (pin R3, snapshot bq_cache_asof20260729_postrestate).
Loc theo dung quy uoc Phan 1 §6: book=BAL, is_capit_arm=False, bo exit_reason=ABANDONED_REFUND.
Nam cua mot lenh = nam cua entry_fill_date (ngay khop MUA), khong phai ngay thoat."""
import numpy as np
import pandas as pd
from scipy import stats

SRC = "../ccs_phase0_Taylor_20260905_135003/trade_ledger_bal_lag_exp.csv"
L = pd.read_csv(SRC, parse_dates=["entry_fill_date", "exit_date", "signal_date"])
raw_bal = int((L.book == "BAL").sum())
d = L[(L.book == "BAL") & (~L.is_capit_arm.astype(bool))].copy()
n_abandoned = int((d.exit_reason == "ABANDONED_REFUND").sum())
d = d[d.exit_reason != "ABANDONED_REFUND"]
d = d[d.ret.notna()]
d["yr"] = d.entry_fill_date.dt.year
print(f"BAL rows raw={raw_bal}  after capit-arm drop+ABANDONED_REFUND({n_abandoned})+ret-notna = {len(d)}")
print("exit_reason mix:", d.exit_reason.value_counts().to_dict())


def blk(g):
    r = g.ret.values
    c = g.contribution_vnd.values
    pos = c[c > 0]
    top3 = np.sort(c)[::-1][:3]
    return pd.Series({
        "n": len(r),
        "mean_%": r.mean() * 100,
        "median_%": np.median(r) * 100,
        "hit_%": (r > 0).mean() * 100,
        "skew": stats.skew(r) if len(r) > 2 else np.nan,
        "p10_%": np.percentile(r, 10) * 100,
        "p90_%": np.percentile(r, 90) * 100,
        "net_B": c.sum() / 1e9,
        "gross_gain_B": pos.sum() / 1e9,
        "top3_share_of_gain_%": (top3[top3 > 0].sum() / pos.sum() * 100) if pos.sum() > 0 else np.nan,
        "topdec_share_of_gain_%": (np.sort(c)[::-1][:max(1, int(round(len(c) * 0.1)))].sum() / pos.sum() * 100) if pos.sum() > 0 else np.nan,
        "n_ret_gt20": int((r > 0.20).sum()),
        "gain_from_ret_gt20_%": (c[r > 0.20][c[r > 0.20] > 0].sum() / pos.sum() * 100) if pos.sum() > 0 else np.nan,
        "ey_median": g.ey.median(),
        "stop_%": (g.exit_reason == "STOP").mean() * 100,
    })


Y = d.groupby("yr").apply(blk, include_groups=False)
ALL = blk(d).rename("ALL")
Y.loc["ALL"] = ALL
pd.set_option("display.width", 250)
print("\n=== B0: phan phoi lenh BAL theo nam (entry year) ===")
print(Y.round(2).to_string())
Y.to_csv("b0_peryear_dist.csv")

# --- la median am co phai chuan muc cua chinh book nay? ---
yrs = Y.drop(index="ALL")
neg_med = yrs[yrs["median_%"] < 0]
print(f"\nSo nam co MEDIAN AM: {len(neg_med)}/{len(yrs)}  -> {sorted(neg_med.index.tolist())}")
print(f"So nam mean > median (lech phai): {(yrs['mean_%'] > yrs['median_%']).sum()}/{len(yrs)}")
print(f"So nam skew > 0: {(yrs['skew'] > 0).sum()}/{len(yrs)}")

# --- 2025 co bat thuong so voi chinh lich su BAL khong? (mo ta, khong p-value quyet dinh) ---
oth = yrs.drop(index=[y for y in (2025,) if y in yrs.index])
print("\n=== 2025 vs 12 nam con lai (percentile cua 2025 trong phan phoi cac nam) ===")
for col in ["median_%", "hit_%", "skew", "top3_share_of_gain_%", "topdec_share_of_gain_%", "mean_%", "ey_median", "n"]:
    v = yrs.loc[2025, col]
    pct = (oth[col].dropna() < v).mean() * 100
    print(f"  {col:24s} 2025={v:8.2f}   khac-nam min={oth[col].min():8.2f} med={oth[col].median():8.2f} "
          f"max={oth[col].max():8.2f}   pctile(2025)={pct:5.1f}%")

# --- pooled: bao nhieu % tong lai cua CA KY den tu bao nhieu % so lenh? ---
c = np.sort(d.contribution_vnd.values)[::-1]
tot_gain = c[c > 0].sum()
for k in (1, 3, 5, 10):
    print(f"  top {k:2d} lenh ({k/len(d)*100:4.1f}% so lenh) = {c[:k].sum()/tot_gain*100:5.1f}% tong lai gop toan ky")


# --- do nhay: neu KHONG loai arm CAPIT (Phan 1 co the da gop) -> so 2025 co doi khong? ---
print("\n=== do nhay bo loc is_capit_arm (Phan 1 §6 bao median 2025 = -0.4%, hit 52%) ===")
for lab, dd in [("BAL momentum only (dung o tren)", d),
                ("BAL incl CAPIT arms", L[(L.book == "BAL") & (L.exit_reason != "ABANDONED_REFUND") & L.ret.notna()].assign(yr=lambda x: x.entry_fill_date.dt.year))]:
    g = dd[dd.yr == 2025]
    print(f"  {lab:34s} n={len(g):3d}  median={np.median(g.ret)*100:+6.2f}%  hit={(g.ret>0).mean()*100:5.1f}%")
