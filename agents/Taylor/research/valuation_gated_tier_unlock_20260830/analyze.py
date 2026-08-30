#!/usr/bin/env python3
"""analyze.py — valuation-gated tier-unlock: PRE-REGISTERED design, test toàn lịch sử 2008-2026.
Job Taylor_20260830_124256. Ephemeral, không canonical.

Cơ chế (PRE-REGISTERED TRƯỚC KHI xem 2009, threshold IMPORT NGUYÊN VĂN từ nghiên cứu ĐỘC LẬP
2026-06-22 archive/2026-W26-W27-raw-events.md "recovery event-study": pb_z<=-0.3, KHÔNG tune lại):
  Tier momentum mạnh (MEGA/S_PRO/MOMENTUM/MOMENTUM_QUALITY/MOMENTUM_S/MOMENTUM_A) hiện đòi
  state5 IN (4,5). Biến thể mới: cho fire thêm khi state5 IN (1,2,3) VÀ pb_z_ticker <= -0.3
  (PB so với chính lịch sử 5 năm của MÃ ĐÓ, công thức y hệt 8L IC panel pb_z + recovery-deploy
  study — không phải số mới bịa ra).

State5 dùng ở đây là DT5G/DT4-base CANONICAL (phaseA CSV cho <2014-01-02, production
`vnindex_5state_dt5g_live` cho >=2014-01-02) — KHÔNG phải `tav2_bq.vnindex_5state` (v3.4b BASE,
bẫy CLAUDE.md) mà signal_v11_sql.py hiện đang join nội bộ. Baseline ở đây vì vậy có thể lệch nhẹ
so với hành vi thật của signal_v11_sql.py hôm nay — ghi rõ, KHÔNG sửa file production đó.
"""
import numpy as np
import pandas as pd

R = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/valuation_gated_tier_unlock_20260830"
PBZ_THRESHOLD = -0.3   # imported unchanged, 2026-06-22 study (recovery-deploy, unrelated dataset)

STRONG_TIERS_STATE_COND = {"MEGA", "S_PRO", "MOMENTUM", "MOMENTUM_QUALITY", "MOMENTUM_S", "MOMENTUM_A"}

def load_state():
    phaseA = pd.read_csv(f"{R}/../phaseA_dt5g_2007_2019.csv" if False else
                          "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_insider/phaseA_dt5g_2007_2019.csv")
    phaseA["time"] = pd.to_datetime(phaseA["time"])
    prod = pd.read_csv(f"{R}/dt5g_prod_2014plus.csv")
    prod["time"] = pd.to_datetime(prod["time"])
    pre = phaseA[phaseA["time"] < "2014-01-02"][["time", "state"]]
    post = prod[["time", "state"]]
    s = pd.concat([pre, post], ignore_index=True).drop_duplicates("time").sort_values("time")
    return s.set_index("time")["state"]


def classify(ta, fa_tier, pe_z, pb_z, warn_ext, np_yoy, rev_yoy, days_since_release, state5, unlock_on):
    """Tái tạo CASE list signal_v11_sql.py; days_since_release/np_yoy/rev_yoy không có trong panel
    (query không kéo) -> MOMENTUM_N/DEEP_VALUE_RECOVERY luôn None ở đây (không ảnh hưởng test này,
    chúng không nằm trong STRONG_TIERS_STATE_COND)."""
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


def run():
    df = pd.read_csv(f"{R}/panel_raw.csv")
    df["time"] = pd.to_datetime(df["time"])
    state = load_state()
    df["state5"] = df["time"].map(state)
    before = len(df)
    df = df.dropna(subset=["state5"])
    print(f"[coverage] {before} -> {len(df)} rows have canonical DT5G state ({before-len(df)} dropped, no state)")
    df["state5"] = df["state5"].astype(int)
    df["warn_ext"] = df["warn_ext"].astype(bool)

    for tag, unlock_on in [("baseline", False), ("tier_unlock", True)]:
        df[f"play_{tag}"] = [
            classify(r.ta, r.fa_tier, r.pe_z, r.pb_z, r.warn_ext, None, None, None, r.state5, unlock_on)
            for r in df.itertuples()
        ]

    df["is_new_fire"] = df["play_tier_unlock"].isin(STRONG_TIERS_STATE_COND) & ~df["play_baseline"].isin(STRONG_TIERS_STATE_COND)
    new_fires = df[df["is_new_fire"]].copy()

    print(f"\n=== TỔNG QUAN: {len(new_fires)} phiên-mã 'mở mới' bởi tier-unlock (toàn 2008-2026) ===")
    print(new_fires.groupby(new_fires["time"].dt.year).size().to_string())

    print("\n=== 2009 cụ thể: có mở không? ===")
    y2009 = new_fires[new_fires["time"].dt.year == 2009]
    print(f"n phiên-mã mở mới trong 2009: {len(y2009)}")
    if len(y2009):
        print(y2009[["ticker", "time", "ta", "pb_z", "state5", "play_tier_unlock"]].head(20).to_string())
        print(f"tickers duy nhất 2009: {sorted(y2009['ticker'].unique().tolist())}")

    # episode construction: gộp các phiên liên tiếp (gap<=5 phiên) cùng ticker thành 1 "episode"
    def episodes(g):
        g = g.sort_values("time")
        gap = g["time"].diff().dt.days.fillna(999)
        ep_id = (gap > 7).cumsum()
        return g.groupby(ep_id).agg(start=("time", "min"), end=("time", "max"), n_days=("time", "size"),
                                     pb_z_at_start=("pb_z", "first"))
    ep = new_fires.groupby("ticker", group_keys=True).apply(episodes).reset_index()
    print(f"\n=== N episode (mã+đợt liên tục, gap>7 phiên = episode mới): {len(ep)} ===")
    print(f"Phân bố theo năm bắt đầu:\n{ep['start'].dt.year.value_counts().sort_index().to_string()}")

    # forward return: dùng profit_2M (T+40, chỉ evaluation — CLAUDE.md: train-only, KHÔNG filter live;
    # ở đây dùng để ĐÁNH GIÁ chất lượng lịch sử của tín hiệu, không phải làm bộ lọc sống)
    print("\n=== Forward profit_2M cho quần thể 'mở mới' vs 2 nhóm đối chứng ===")
    grpA = new_fires["profit_2M"].dropna()
    grpB = df[df["play_baseline"].isin(STRONG_TIERS_STATE_COND)]["profit_2M"].dropna()
    grpC = df[(df["state5"].isin([1, 2, 3])) & (~df["is_new_fire"]) & (df["pb_z"] > PBZ_THRESHOLD)]["profit_2M"].dropna()
    for name, g in [("A: mở mới (unlock, state 1-3 + cheap)", grpA),
                    ("B: baseline hiện tại (state 4-5, đã fire)", grpB),
                    ("C: đối chứng (state 1-3, KHÔNG cheap, bị loại đúng)", grpC)]:
        if len(g) == 0:
            print(f"{name}: n=0 (profit_2M rỗng cho nhóm này — có thể do panel_raw chỉ query từ tav2_bq.ticker, thiếu ticker_1m fallback profit_2M)")
            continue
        print(f"{name}: n={len(g):5d}  mean={g.mean():+6.2f}%  median={g.median():+6.2f}%  win={100*(g>0).mean():5.1f}%  p5={g.quantile(.05):+6.1f}%")

    # IS/OOS theo yêu cầu: vì trục chính là PRE-2014, dùng chia phù hợp: IS = trước 2020, OOS = 2020+
    print("\n=== IS(<2020) / OOS(>=2020) cho nhóm A (mở mới) ===")
    for name, sub in [("IS <2020", grpA[new_fires.loc[grpA.index, "time"] < "2020-01-01"] if len(grpA) else grpA),
                       ("OOS >=2020", grpA[new_fires.loc[grpA.index, "time"] >= "2020-01-01"] if len(grpA) else grpA)]:
        if len(sub) == 0:
            print(f"{name}: n=0")
            continue
        print(f"{name}: n={len(sub):5d} mean={sub.mean():+6.2f}% win={100*(sub>0).mean():5.1f}%")

    new_fires.to_csv(f"{R}/new_fires_detail.csv", index=False)
    ep.to_csv(f"{R}/new_fires_episodes.csv", index=False)
    df[["ticker", "time", "ta", "fa_tier", "pb_z", "state5", "play_baseline", "play_tier_unlock", "profit_2M"]].to_csv(
        f"{R}/panel_classified.csv", index=False)
    print(f"\nwrote new_fires_detail.csv ({len(new_fires)}), new_fires_episodes.csv ({len(ep)}), panel_classified.csv ({len(df)})")


if __name__ == "__main__":
    run()
