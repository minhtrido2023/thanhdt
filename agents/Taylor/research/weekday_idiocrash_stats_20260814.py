#!/usr/bin/env python3
"""weekday_idiocrash_stats_20260814.py — script ĐO MỘT LẦN cho §C.2/§C.3/§C.4/§F.2 của
research/portfolio_wide_badnews_protection_20260814.md.

VÌ SAO TỒN TẠI: vòng verify quant-skeptic (job Taylor_20260814_041116) phải TỰ VIẾT LẠI từ đầu
mới kiểm được bảng số trong report, vì phép đo chỉ tồn tại dưới dạng văn xuôi markdown. Lần tái
lập độc lập đó ra 2 con số KHÁC report (N episode toàn thị trường, N episode trên 29 mã đang giữ)
⇒ phải có script để chỉ ra CHÍNH XÁC bộ lọc nào sinh ra số nào.

§8/§10 coding_guidelines: đây KHÔNG phải file canonical, KHÔNG pin vào results_registry.md. Một
lần đo, tên có ngày, output CSV cùng thư mục.

CHẠY (§8 coding_guidelines — CHÉP NGUYÊN VĂN, đừng thay bằng `python3`):
    /home/trido/thanhdt/wc_venv/bin/python \
        mike/agents/Taylor/research/weekday_idiocrash_stats_20260814.py

⚠️ HAI CÁI BẪY ĐÃ CẮN THẬT (2026-08-14, vòng verify quant-skeptic) — đừng gỡ 2 guard dưới đây:
  (1) `pct_change(fill_method=None)` PHẢI khai tường minh. Mặc định của pandas 2.x là
      `fill_method='pad'`, pandas 3.x là None ⇒ CÙNG script + CÙNG dữ liệu ra SỐ KHÁC NHAU tuỳ
      interpreter (đo được: N episode market/none 71.749 dưới pandas 2.3.3 vs 71.637 dưới 3.0.2).
      Gốc: cột mirror `VNINDEX` NULL ở 5 phiên (2016-01-04, 2020-01-02, 2020-01-03, 2025-05-04,
      2025-05-11); pandas 2 pad giá trị phiên trước ⇒ BỊA ra "phiên đó VNINDEX đi ngang 0%" ⇒
      `idio` có giá trị ở nơi lẽ ra phải khuyết ⇒ đếm dôi episode. Khai `None` = phiên thiếu dữ
      liệu thị trường thì KHÔNG có idio, đúng bản chất.
  (2) `Close > 0` PHẢI lọc ở SQL. 2.419 dòng có `Close <= 0` (dữ liệu hỏng) làm mẫu số của
      lợi suất forward ⇒ `fwd*` ra `inf`, kéo theo trung bình `inf` trong CSV audit.

Đọc: data/bq_cache/ticker/{year}.parquet (cache local, KHÔNG gọi BQ).
Ghi: weekday_idiocrash_stats_20260814_{weekday,forward,episodes}.csv cùng thư mục.
     (`weekday` = phân bố theo thứ cho CẢ 2 phạm vi market/hold29 × 3 biến thể thanh khoản;
      `forward` = lợi suất +1/+2/+3 phiên sau cú sập; `episodes` = từng episode toàn thị trường,
      để ai cũng recompute lại được mà không cần chạy script này.)

BA BIẾN THỂ BỘ LỌC THANH KHOẢN — cố ý chạy CẢ BA, vì chính chỗ này là nguồn của mọi chênh N:
  liq=none  : không lọc thanh khoản (= đúng nhánh `is_hold` của anomaly_scan.compute_signals)
  liq=adv   : val1m_bn >= 3          (chỉ sàn thanh khoản bình quân 1 tháng)
  liq=both  : val1m_bn >= 3 AND val_bn >= 3   (= đúng nhánh tier-W của anomaly_scan)
Luật production `IDIOCRASH` dùng `none` cho mã ĐANG GIỮ và `both` cho mã KHÔNG giữ — nên câu
"N của báo cáo là bao nhiêu" KHÔNG có một đáp án duy nhất trừ khi nói rõ biến thể.
"""
import os
import sys

import duckdb
import numpy as np
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WC, "data", "bq_cache")
OUTDIR = os.path.dirname(os.path.abspath(__file__))
STEM = os.path.join(OUTDIR, "weekday_idiocrash_stats_20260814")

START = "2016-01-01"          # §C.2 khai "2016→2026-08"
WARMUP_YEAR = 2015            # cần 1 năm trước để pct_change/Volume_1M của phiên đầu 2016 có nghĩa
CRASH_RET, CRASH_IDIO = -6.0, -5.0    # luật IDIOCRASH
UP_RET, UP_IDIO = 6.0, 5.0            # đối chứng đối xứng
FLOOR_RET, FLOOR_IDIO = -6.5, -4.0    # luật FLOOR2 (2 phiên liên tiếp)
LIQ_1M_BN = 3.0
MERGE_DAYS = 7                # hợp nhất phiên cách nhau <= 7 ngày LỊCH thành 1 episode
WD = ["Hai", "Ba", "Tu", "Nam", "Sau"]

# 29 mã đang giữ, chụp 2026-08-14 từ anomaly_scan.py --print-universe (vị thế thật 2 account).
# CHÉP CỨNG CÓ CHỦ Ý: đây là phép đo hồi tố một lần trên rổ TẠI THỜI ĐIỂM ĐO — nếu để nó đọc
# watchlist sống thì cùng script chạy lại tháng sau ra số khác mà không ai biết vì sao (§23 hệ
# luận 1: đừng assert/đo lên trạng thái SỐNG trong artifact cố định).
HOLD29 = ("ACB BID CTG HDB LPB MBB MSB SHB TCB TPB VCB VIB VPB "
          "CSV DGC DRI EVF HPG NCT PVT SAB SCL SIP TV1 VHM VIX VND VNM VRE").split()


def load_panel():
    years = sorted(int(f[:4]) for f in os.listdir(os.path.join(CACHE, "ticker"))
                   if f.endswith(".parquet") and f[:4].isdigit() and int(f[:4]) >= WARMUP_YEAR)
    files = [os.path.join(CACHE, "ticker", f"{y}.parquet") for y in years]
    con = duckdb.connect()
    con.execute("PRAGMA threads=1")
    df = con.execute(
        f"select time, ticker, Close, Volume, Volume_1M, VNINDEX from read_parquet({files!r}) "
        f"where Close > 0 and ticker <> 'VNINDEX' order by ticker, time").df()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["ticker", "time"]).reset_index(drop=True)
    # fill_method=None tường minh ở CẢ HAI chỗ: xem bẫy (1) ở docstring — bỏ đi là để kết quả
    # phụ thuộc phiên bản pandas của người chạy.
    df["ret"] = df.groupby("ticker")["Close"].pct_change(fill_method=None) * 100
    vni = df.groupby("time")["VNINDEX"].first().pct_change(fill_method=None) * 100
    df["vni_ret"] = df["time"].map(vni)
    df["idio"] = df["ret"] - df["vni_ret"]
    df["val_bn"] = df["Volume"] * df["Close"] / 1e9
    df["val1m_bn"] = df["Volume_1M"] * df["Close"] / 1e9
    # lợi suất cộng dồn +1/+2/+3 PHIÊN kể từ phiên sập (theo Close, cùng mã)
    g = df.groupby("ticker")["Close"]
    for k in (1, 2, 3):
        df[f"fwd{k}"] = (g.shift(-k) / df["Close"] - 1) * 100
    df["wd"] = df["time"].dt.weekday          # 0=Hai
    return df


def liq_mask(df, variant):
    if variant == "none":
        return pd.Series(True, index=df.index)
    if variant == "adv":
        return df["val1m_bn"] >= LIQ_1M_BN
    if variant == "both":
        return (df["val1m_bn"] >= LIQ_1M_BN) & (df["val_bn"] >= LIQ_1M_BN)
    raise ValueError(variant)


def episodes(df, hits):
    """Giữ phiên ĐẦU của mỗi cụm: cùng mã, cách phiên hit trước <= MERGE_DAYS ngày lịch thì bỏ."""
    h = df[hits & (df["time"] >= START)].sort_values(["ticker", "time"])
    if h.empty:
        return h
    gap = h.groupby("ticker")["time"].diff()
    keep = gap.isna() | (gap > pd.Timedelta(days=MERGE_DAYS))
    return h[keep]


def sessions_by_wd(df):
    d = df.loc[df["time"] >= START, ["time"]].drop_duplicates()
    return d["time"].dt.weekday.value_counts().reindex(range(5), fill_value=0).sort_index()


def chi2_uniform_rate(obs, sess):
    """χ² của phân bố episode theo thứ, kỳ vọng TỈ LỆ THUẬN số phiên của thứ đó."""
    exp = sess / sess.sum() * obs.sum()
    stat = float((((obs - exp) ** 2) / exp).sum())
    # p-value chi2 df=4 bằng chuỗi đóng (df chẵn): P(X>x) = exp(-x/2)*(1 + x/2)
    p = float(np.exp(-stat / 2) * (1 + stat / 2))
    return stat, p, exp


def two_prop_z(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    pp = (k1 + k2) / (n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se
    # p 2 phía từ xấp xỉ Abramowitz-Stegun 7.1.26 của erf
    x = abs(z) / np.sqrt(2)
    t = 1 / (1 + 0.3275911 * x)
    erf = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t
               + 0.254829592) * t * np.exp(-x * x)
    return float(z), float(1 - erf)


def boot_mean_ci(x, n_boot=2000, seed=20260814):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 30:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    m = x[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    df = load_panel()
    sess = sessions_by_wd(df)
    out_wd, out_fwd, ep_rows = [], [], []

    crash_raw = (df["ret"] <= CRASH_RET) & (df["idio"] <= CRASH_IDIO)
    up_raw = (df["ret"] >= UP_RET) & (df["idio"] >= UP_IDIO)
    floor = (df["ret"] <= FLOOR_RET) & (df["idio"] <= FLOOR_IDIO)
    floor2_raw = floor & floor.groupby(df["ticker"]).shift(1, fill_value=False)

    print(f"panel: {len(df):,} dòng · {df['ticker'].nunique():,} mã · "
          f"{df.loc[df['time'] >= START, 'time'].min():%Y-%m-%d} → "
          f"{df['time'].max():%Y-%m-%d}")
    print(f"phiên theo thứ (T2..T6): {list(sess.values)}  tổng {int(sess.sum()):,}\n")

    for scope, tickers in (("market", None), ("hold29", HOLD29)):
        sub = df if tickers is None else df[df["ticker"].isin(tickers)]
        # FLOOR1 = phiên sàn ĐƠN LẺ (ngày 1); FLOOR2 = sàn 2 phiên LIÊN TIẾP. Chạy cả hai vì
        # bản report đầu gắn nhãn "FLOOR2" cho số thực ra là FLOOR1 — không có cả hai thì không
        # ai truy được nhãn nào ứng với số nào (§F.7).
        for rule, raw in (("IDIOCRASH", crash_raw), ("UPSPIKE", up_raw),
                          ("FLOOR1", floor), ("FLOOR2", floor2_raw)):
            for variant in ("none", "adv", "both"):
                hits = raw.loc[sub.index] & liq_mask(sub, variant)
                ep = episodes(sub, hits)
                if ep.empty:
                    continue
                obs = ep["wd"].value_counts().reindex(range(5), fill_value=0).sort_index()
                stat, p, exp = chi2_uniform_rate(obs, sess)
                rate = obs / sess
                mon_ratio = rate.iloc[0] / rate.iloc[1:].mean()
                out_wd.append(dict(
                    scope=scope, rule=rule, liq=variant, n_episode=int(obs.sum()),
                    n_mon=int(obs.iloc[0]), n_tue=int(obs.iloc[1]), n_wed=int(obs.iloc[2]),
                    n_thu=int(obs.iloc[3]), n_fri=int(obs.iloc[4]),
                    mon_share_pct=round(100 * obs.iloc[0] / obs.sum(), 2),
                    mon_vs_rest_ratio=round(float(mon_ratio), 4),
                    chi2=round(stat, 2), p_value=f"{p:.3g}"))
                if rule == "IDIOCRASH":
                    for wd in range(5):
                        e = ep[ep["wd"] == wd]
                        lo1, hi1 = boot_mean_ci(e["fwd1"])
                        out_fwd.append(dict(
                            scope=scope, liq=variant, wd=WD[wd], n=len(e),
                            crash_day_ret=round(float(e["ret"].mean()), 3),
                            fwd1_mean=round(float(e["fwd1"].mean()), 3),
                            fwd1_ci_lo=None if np.isnan(lo1) else round(lo1, 3),
                            fwd1_ci_hi=None if np.isnan(hi1) else round(hi1, 3),
                            fwd2_mean=round(float(e["fwd2"].mean()), 3),
                            fwd3_mean=round(float(e["fwd3"].mean()), 3),
                            p_next_neg_pct=round(100 * float((e["fwd1"] < 0).mean()), 2)))
                    # dump episode chi tiết cho 2 biến thể ĐƯỢC TRÍCH trong report; bỏ liq=none
                    # (71.749 episode toàn thị trường, không bảng nào dùng, CSV phình lên 12MB).
                    if scope == "market" and variant in ("adv", "both"):
                        keep = ep[["time", "ticker", "wd", "ret", "vni_ret", "idio",
                                   "val_bn", "val1m_bn", "fwd1", "fwd2", "fwd3"]].round(4).copy()
                        keep.insert(0, "liq", variant)
                        ep_rows.append(keep)

    wd_df = pd.DataFrame(out_wd)
    fwd_df = pd.DataFrame(out_fwd)
    wd_df.to_csv(f"{STEM}_weekday.csv", index=False)
    fwd_df.to_csv(f"{STEM}_forward.csv", index=False)
    pd.concat(ep_rows).to_csv(f"{STEM}_episodes.csv", index=False)

    pd.set_option("display.width", 200, "display.max_columns", 40)
    print("=== §C.2 — phân bố episode theo THỨ ===")
    print(wd_df.to_string(index=False))
    print("\n=== §C.3 — lợi suất sau cú sập (IDIOCRASH) ===")
    print(fwd_df.to_string(index=False))

    # đối chứng đối xứng §C.2 (sập vs tăng), biến thể 'both' = luật tier-W production
    for variant in ("adv", "both"):
        d = wd_df[(wd_df.scope == "market") & (wd_df.liq == variant)].set_index("rule")
        if {"IDIOCRASH", "UPSPIKE"} <= set(d.index):
            c, u = d.loc["IDIOCRASH"], d.loc["UPSPIKE"]
            z, p = two_prop_z(c.n_mon, c.n_episode, u.n_mon, u.n_episode)
            print(f"\n[liq={variant}] tỉ trọng T2: sập {c.mon_share_pct}% (N={c.n_episode}) vs "
                  f"tăng {u.mon_share_pct}% (N={u.n_episode}) → chênh "
                  f"{c.mon_share_pct - u.mon_share_pct:+.1f}pp, z={z:.2f}, p={p:.2g}")

    print(f"\nĐã ghi: {STEM}_{{weekday,forward,episodes}}.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
