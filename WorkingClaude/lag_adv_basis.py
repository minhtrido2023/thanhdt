"""ADV basis helper cho 3 engine papertrade (pt_v22 / pt_v4 / pt_v12) — 2026-11-10 r3.

Volume_3M_P50 là số cổ phiếu THÔ ⇒ ADV VND phải nhân với giá THÔ (cột Price), không phải
Close/Open ĐIỀU CHỈNH (cache lagged_pos_ov sau apply). Pkl cũ không có cột Price ⇒ giữ hành vi cũ.
"""
import pandas as pd


def raw_price_panel(ov, master_idx):
    """Panel giá THÔ (Price) hoặc None nếu pkl không có cột Price."""
    if "Price" not in ov.columns:
        return None
    return (ov.pivot_table(index="time", columns="ticker", values="Price", aggfunc="first")
              .sort_index().reindex(master_idx).ffill(limit=5))


def adv_px(px_raw, dt, tk, fallback):
    """COALESCE(Price thô, fallback). px_raw None / thiếu mã / NaN ⇒ fallback (hành vi cũ)."""
    if px_raw is not None and tk in px_raw.columns:
        v = px_raw.at[dt, tk]
        if pd.notna(v):
            return v
    return fallback
