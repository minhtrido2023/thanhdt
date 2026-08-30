#!/usr/bin/env python3
"""analyze_round2.py — làm lại đúng 5 điểm quant-skeptic REFUTED yêu cầu (round 1: verify_finding
job Taylor_20260830_124256, medium confidence). Job Taylor_20260830_132917.

Tái dùng panel_raw.csv/dt5g_prod_2014plus.csv/phaseA_dt5g_2007_2019.csv đã pull ở round 1 (không
đổi query/threshold/design — chỉ sửa đúng 5 điểm bị REFUTED). KHÔNG chạm production code.

5 điểm sửa:
 1. Baseline state — VERIFY (không cần đổi code): design gốc ĐÃ dùng DT5G-live (482 ngày state4/5,
    2014-2026) cho CẢ group A và B, không phải v3.4b BASE (515 ngày). Quant-skeptic so 2 bảng đúng
    số (515 vs 482, verify lại bằng BQ live hôm nay khớp 100%) nhưng complaint của họ là:
    signal_v11_sql.py THẬT đang chạy live join v3.4b BASE (bug riêng, chưa sửa) — nên group B
    "baseline đã fire" trong backtest là counterfactual "nếu sửa bug đó" chứ không phải hành vi
    live 100% hiện tại. Dispatch round 2 (user 20:28 ICT) giải quyết ambiguity này: dùng state THẬT
    đang chạy sản xuất = DT5G-live qua get_gated_state() — đây CHÍNH LÀ cái design gốc đã làm.
    Kết luận: không cần sửa code, chỉ cần verify + nói rõ trong báo cáo (làm ở dưới + trong .md).
 2. Cluster-robust SE theo tháng-lịch (không dùng t-stat episode-level thô).
 3. Loại 15 mã BANNED trước khi tính bất kỳ số tổng hợp nào.
 4. Capacity/ADV cho nhóm mở mới — liq đã có sẵn trong panel (Volume_3M_P50 * Price).
 5. NAV-impact ở NAV production thật (50B, pin registry) — contribution-weighted approximation,
    có giới hạn nói rõ (không rerun full NAV engine — ngoài ngân sách job).
"""
import numpy as np
import pandas as pd

R = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/valuation_gated_tier_unlock_20260830"
PBZ_THRESHOLD = -0.3

STRONG_TIERS_STATE_COND = {"MEGA", "S_PRO", "MOMENTUM", "MOMENTUM_QUALITY", "MOMENTUM_S", "MOMENTUM_A"}

BANNED = {"PC1", "VVS", "KSF", "NKG", "HSG", "HVN", "VJC", "NVL", "GEG", "SBA",
          "DMC", "IMP", "TRA", "TOS", "VTP"}

NAV = 50e9  # VND, pinned R3 backtest (data/results_registry.md, universe_pit, 2026-08-03)


def load_state():
    phaseA = pd.read_csv("/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider/phaseA_dt5g_2007_2019.csv")
    phaseA["time"] = pd.to_datetime(phaseA["time"])
    prod = pd.read_csv(f"{R}/dt5g_prod_2014plus.csv")
    prod["time"] = pd.to_datetime(prod["time"])
    pre = phaseA[phaseA["time"] < "2014-01-02"][["time", "state"]]
    post = prod[["time", "state"]]
    s = pd.concat([pre, post], ignore_index=True).drop_duplicates("time").sort_values("time")
    return s.set_index("time")["state"]


def classify(ta, fa_tier, pe_z, pb_z, warn_ext, state5, unlock_on):
    cheap = unlock_on and pd.notna(pb_z) and pb_z <= PBZ_THRESHOLD
    strong_state = state5 in (4, 5) or (unlock_on and state5 in (1, 2, 3) and cheap)
    if state5 in (1, 2) and not (unlock_on and cheap):
        return "AVOID_bear"
    if fa_tier == "E":
        return "AVOID_faE"
    if ta >= 170 and strong_state and fa_tier in ("C", "D"):
        return "MEGA"
    if ta >= 170 and strong_state:
        return "S_PRO"
    if ta >= 155 and strong_state and fa_tier in ("C", "D"):
        return "MOMENTUM"
    if ta >= 155 and strong_state and fa_tier in ("A", "B"):
        return "MOMENTUM_QUALITY"
    if pd.notna(fa_tier) and fa_tier in ("A", "B") and pd.notna(pe_z) and pe_z < -0.5 and ta >= 95 and state5 in (3, 4, 5) and not warn_ext:
        return "COMPOUNDER_BUY"
    if ta >= 140 and strong_state:
        return "MOMENTUM_S"
    if ta >= 125 and strong_state:
        return "MOMENTUM_A"
    if pd.notna(fa_tier) and fa_tier in ("A", "B") and 70 <= ta < 130:
        return "COMPOUNDER_HOLD"
    if pd.notna(fa_tier) and fa_tier in ("A", "B"):
        return "WAIT"
    return "PASS"


def cluster_robust_tstat(values, cluster_ids, n_boot=5000, seed=42):
    """Pairs-cluster bootstrap ĐÚNG (sửa bug quant-skeptic tìm ra 2026-08-30 round 2 lần 1):
    resample CLUSTER (tháng) có hoàn lại, nhưng mỗi lần resample phải GIỮ NGUYÊN toàn bộ episode
    thuộc cluster được chọn (không rút gọn về trung bình-của-trung bình trước) rồi tính lại
    episode-weighted mean trên tập đã pool — numerator/denominator PHẢI cùng 1 estimator
    (episode-weighted), khác bug cũ (tử số episode-weighted, mẫu số lại là SE của phân phối
    bootstrap trên trung bình-CỤM-đã-lấy-trung-bình-trước = equal-weight-by-month, ước lượng
    khác hẳn — sinh CI không chứa nổi điểm ước lượng của chính nó)."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({"v": values, "c": cluster_ids})
    clusters = df["c"].unique()
    n_c = len(clusters)
    by_cluster = {c: g["v"].values for c, g in df.groupby("c")}
    grand_mean = df["v"].mean()
    boot_means = np.empty(n_boot)
    for b in range(n_boot):
        picked = rng.choice(clusters, size=n_c, replace=True)
        pooled = np.concatenate([by_cluster[c] for c in picked])
        boot_means[b] = pooled.mean()
    se_cluster = boot_means.std(ddof=1)
    t_cluster = grand_mean / se_cluster if se_cluster > 0 else np.nan
    p_le_0 = (boot_means <= 0).mean()
    cluster_means_equal_w = df.groupby("c")["v"].mean()
    frac_cluster_neg = (cluster_means_equal_w < 0).mean()
    return {
        "n_clusters": n_c, "grand_mean": grand_mean, "se_cluster": se_cluster,
        "t_cluster": t_cluster, "P(boot_mean<=0)": p_le_0,
        "frac_cluster_months_neg": frac_cluster_neg,
        "boot_ci_5_95": (np.percentile(boot_means, 5), np.percentile(boot_means, 95)),
    }


def run():
    df = pd.read_csv(f"{R}/panel_raw.csv")
    df["time"] = pd.to_datetime(df["time"])
    state = load_state()
    df["state5"] = df["time"].map(state)
    before = len(df)
    df = df.dropna(subset=["state5"])
    df["state5"] = df["state5"].astype(int)
    df["warn_ext"] = df["warn_ext"].astype(bool)

    # --- điểm 3: loại BANNED SỚM, trước mọi tính toán ---
    n_before_ban = len(df)
    df = df[~df["ticker"].isin(BANNED)].copy()
    print(f"[banned filter] {n_before_ban} -> {len(df)} rows ({n_before_ban-len(df)} dropped, "
          f"{sorted(BANNED)})")

    for tag, unlock_on in [("baseline", False), ("tier_unlock", True)]:
        df[f"play_{tag}"] = [
            classify(r.ta, r.fa_tier, r.pe_z, r.pb_z, r.warn_ext, r.state5, unlock_on)
            for r in df.itertuples()
        ]

    df["is_new_fire"] = df["play_tier_unlock"].isin(STRONG_TIERS_STATE_COND) & ~df["play_baseline"].isin(STRONG_TIERS_STATE_COND)
    new_fires = df[df["is_new_fire"]].copy()

    print(f"\n=== [điểm 1 VERIFY] state5 dùng ở đây = DT5G-live/DT4-base canonical (không phải "
          f"v3.4b BASE) — như design round 1, đúng directive round 2. ===")

    print(f"\n=== [điểm 3] TỔNG QUAN sau loại banned: {len(new_fires)} phiên-mã 'mở mới' ===")
    print(new_fires.groupby(new_fires["time"].dt.year).size().to_string())

    y2009 = new_fires[new_fires["time"].dt.year == 2009]
    print(f"\n2009: n phiên-mã={len(y2009)}, mã duy nhất={sorted(y2009['ticker'].unique().tolist())}")

    # episode construction (giống round 1: gap>7 phiên = episode mới)
    def episodes(g):
        g = g.sort_values("time")
        gap = g["time"].diff().dt.days.fillna(999)
        ep_id = (gap > 7).cumsum()
        return g.groupby(ep_id).agg(start=("time", "min"), end=("time", "max"), n_days=("time", "size"),
                                     pb_z_at_start=("pb_z", "first"), liq_at_start=("liq", "first"),
                                     profit_2M_at_start=("profit_2M", "first"))
    ep = new_fires.groupby("ticker", group_keys=True).apply(episodes).reset_index()
    ep["start_month"] = ep["start"].dt.to_period("M").astype(str)
    print(f"\n=== N episode (sau loại banned): {len(ep)} (round1 REFUTED report: 1399 trước loại banned) ===")

    ep_ret = ep.dropna(subset=["profit_2M_at_start"])
    print(f"episode có profit_2M: n={len(ep_ret)}")
    print(f"mean={ep_ret['profit_2M_at_start'].mean():+.2f}%  median={ep_ret['profit_2M_at_start'].median():+.2f}%  "
          f"win={100*(ep_ret['profit_2M_at_start']>0).mean():.1f}%")

    # --- điểm 2: cluster-robust SE theo tháng ---
    print("\n=== [điểm 2] Cluster-robust (bootstrap theo tháng-lịch, 5000 resample) ===")
    cr = cluster_robust_tstat(ep_ret["profit_2M_at_start"].values, ep_ret["start_month"].values)
    for k, v in cr.items():
        print(f"  {k}: {v}")
    naive_t = ep_ret["profit_2M_at_start"].mean() / (ep_ret["profit_2M_at_start"].std(ddof=1) / np.sqrt(len(ep_ret)))
    print(f"  (so sánh) naive episode-level t (không cluster): {naive_t:.2f}")

    # IS/OOS sau loại banned + cluster check theo năm
    print("\n=== IS(<2020)/OOS(>=2020), sau loại banned ===")
    for name, sub in [("IS <2020", ep_ret[ep_ret["start"] < "2020-01-01"]),
                       ("OOS >=2020", ep_ret[ep_ret["start"] >= "2020-01-01"])]:
        v = sub["profit_2M_at_start"]
        print(f"{name}: n={len(sub)} mean={v.mean():+.2f}% median={v.median():+.2f}% win={100*(v>0).mean():.1f}%")

    print("\n=== Theo năm (mean/median/n), sau loại banned ===")
    yr = ep_ret.groupby(ep_ret["start"].dt.year)["profit_2M_at_start"].agg(["count", "mean", "median"])
    print(yr.to_string())

    # --- điểm 4: capacity/ADV ---
    print("\n=== [điểm 4] Capacity/ADV — liq_at_start (VND/ngày, = Volume_3M_P50 * Price) ===")
    print(ep_ret["liq_at_start"].describe().to_string())
    for pct in (0.02, 0.03, 0.05):
        pos_size = NAV * pct
        # quy ước tham gia thị trường: không vượt quá 10% ADV/phiên để tránh market impact
        # (participation-rate convention phổ biến, KHÔNG phải số đã kiểm chứng riêng cho VN)
        thin = ep_ret[ep_ret["liq_at_start"] * 0.10 < pos_size]
        print(f"  cap={pct*100:.0f}% NAV (position={pos_size/1e9:.2f} tỷ): "
              f"{len(thin)}/{len(ep_ret)} episode ({100*len(thin)/len(ep_ret):.1f}%) có ADV*10% < position size "
              f"(cần >1 phiên để vào đủ)")
    thinnest = ep_ret.nsmallest(10, "liq_at_start")[["ticker", "start", "liq_at_start", "profit_2M_at_start"]]
    print("\n10 episode mỏng nhất (liq_at_start thấp nhất):")
    print(thinnest.to_string())

    # --- điểm 5: NAV-impact (contribution-weighted approximation) ---
    print("\n=== [điểm 5] NAV-impact — contribution-weighted approximation, NAV=50 tỷ ===")
    print("GIỚI HẠN: không rerun full NAV/position-sizing engine (Kelly, ramp T+1, TC 0.1%) — đây "
          "là ước lượng đóng góp = (position_size/NAV) * profit_2M, position_size = min(cap%*NAV, "
          "10%*ADV_start). Không mô hình hoá overlap/tranh chấp vốn giữa các episode đồng thời "
          "(concurrent positions có thể vượt NAV khả dụng thật của book).")
    for pct in (0.02, 0.03):
        cap_nav = NAV * pct
        pos = np.minimum(cap_nav, 0.10 * ep_ret["liq_at_start"].values)
        contrib = (pos / NAV) * (ep_ret["profit_2M_at_start"].values / 100.0)
        total_days = (ep_ret["start"].max() - ep_ret["start"].min()).days
        years = total_days / 365.25
        # tổng đóng góp tuyệt đối / số năm, coi các episode trải đều theo thời gian (không netting)
        pp_per_year = 100 * contrib.sum() / years
        print(f"  cap={pct*100:.0f}%: tổng đóng góp cộng dồn = {100*contrib.sum():+.2f}pp trên "
              f"{years:.1f} năm (~{pp_per_year:+.2f}pp/năm nếu trải đều, KHÔNG compound, KHÔNG netting)")

    ep_ret.to_csv(f"{R}/round2_episodes_clean.csv", index=False)
    print(f"\nwrote round2_episodes_clean.csv ({len(ep_ret)})")


if __name__ == "__main__":
    run()
