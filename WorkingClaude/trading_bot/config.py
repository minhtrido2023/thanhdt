# -*- coding: utf-8 -*-
"""Cấu hình bot — đọc/ghi data/trading_bot_config.json (tạo mặc định nếu chưa có)."""

import json
import os

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKDIR, "data")
PLAN_DIR = os.path.join(DATA_DIR, "trade_plans")
EXEC_DIR = os.path.join(DATA_DIR, "execution_logs")
CONFIG_FILE = os.path.join(os.path.dirname(DATA_DIR), "secrets", "trading_bot_config.json")
ACCOUNTS_FILE = os.path.join(os.path.dirname(DATA_DIR), "secrets", "trading_bot_accounts.json")
STOP_FILE = os.path.join(DATA_DIR, "BOT_STOP")          # tạo file này → bot dừng + hủy lệnh treo

DEFAULTS = {
    # --- chung ---
    "mode": "paper",                  # "paper" | "live"
    "broker": "phs",                  # "phs" | "dnse" (per-account override được)
    "strategy": "v23",                # key trong strategies.REGISTRY
    "account_id": None,               # None → tiểu khoản đầu tiên từ PHS
    "etf_symbol": "E1VFVN30",
    "include_etf_park": True,         # mirror cả phần park ETF của paper book

    # --- sizing / mirror ---
    "paper_init_cash": 1_000_000_000, # tiền ảo khởi tạo cho PaperBroker (VND)
    "min_order_value": 5_000_000,     # bỏ qua lệnh < 5M VND (dust)
    "qty_tolerance_pct": 0.05,        # |lệch| < 5% target → không phát lệnh sync

    # --- slicing / execution ---
    "max_child_value": 200_000_000,   # VND tối đa mỗi lệnh con
    "max_participation": 0.10,        # mua/bán ≤ 10% KL khớp lũy kế trong ngày của mã
    "slice_interval_min": 8,          # phút giữa 2 lệnh con cùng một parent
    "poll_interval_sec": 20,          # chu kỳ poll sổ lệnh + quote
    "chase_ticks": 1,                 # mua: đặt bid + n tick (passive); 0 = đặt ngay bid
    "buy_cross_spread": True,          # True: mua đặt thẳng giá ask (marketable)
    "cross_mode": "adaptive",         # "adaptive" (default, user+Taylor 2026-06-26): DIP khi
                                      #   order_value/ADV < adaptive_cross_adv_threshold, else
                                      #   TWAP. @1B hầu hết lệnh <0.1% ADV → DIP tự nhiên;
                                      #   khi NAV lớn shift TWAP không cần reconfig.
                                      # "always": TWAP — cross mọi slice (archived; Taylor
                                      #   backtest: fill-rate hơn dip 3.5bps nhưng variance 2×).
                                      # "dip": S2 mean-reversion (archived — beat by adaptive).
    "adaptive_cross_adv_threshold": 0.01,  # 1% ADV: dưới ngưỡng → DIP; trên → TWAP.
                                           # Taylor backtest: DIP fill 0.90→0.38 khi >1% ADV.
    "dip_window_min": 15,             # cửa sổ return quyết định cross/passive
    "px_sample_sec": 60,              # chu kỳ ghi giá vào px_hist (tính r15)
    "max_chase_pct_buy": 0.015,       # trần đuổi giá mua = ref_plan × (1+1.5%)
    "max_chase_pct_sell": 0.03,       # sàn đuổi giá bán = ref_plan × (1−3%)
    "atc_remainder_sell": True,       # phần bán còn sót → quét ATC
    "atc_remainder_buy": False,       # phần mua còn sót → mặc định bỏ (mai plan mới tự sync)
    "paper_fee_rate": 0.0015,         # phí mô phỏng paper (0.15% mỗi chiều)

    # --- fill-timing (Layer-3 WHEN-to-fill, đặt trên adaptive cross_mode) ---
    # Taylor backtest 16 names 9670 ticker-days: Open là giờ TỆ nhất mua (+18.7bps),
    # 11:15 là đáy intraday (+1.1bps). SELL: Open là TỐT nhất (+18.7bps morning premium).
    # Lợi ~17.6bps/lệnh mua vs Open, ~5-6bps vs uniform/VWAP (edge trung bình, std cao).
    "fill_timing_enabled": True,      # True: side-aware schedule; False: uniform (tắt hẳn)
    "fill_timing_live_gate": True,    # True: chỉ paper; live cần user tắt thủ công (real money)
    "buy_window_start": "10:45",      # BUY: đầu cửa sổ tập trung (ICT)
    "buy_window_end": "11:15",        # BUY: cuối cửa sổ (đáy intraday)
    "sell_window_start": "09:15",     # SELL: tập trung ở Open (đỉnh morning premium)
    "sell_window_end": "09:45",       # SELL: cuối cửa sổ Open
    "fill_timing_outside_mult": 4.0,  # interval × mult ngoài cửa sổ (8min → 32min mặc định)

    # --- an toàn ---
    "max_orders_per_day": 60,         # tổng số parent order tối đa trong 1 plan
    "max_daily_gross_value": 20_000_000_000,  # tổng GTGD tối đa 1 ngày (VND)
}


ACCOUNT_DEFAULTS = {
    "label": "main",            # tên định danh — namespace mọi file plan/state/journal
    "enabled": True,
    "mode": None,               # None → dùng mode chung trong trading_bot_config.json
    "broker": None,             # None → broker chung; "phs" | "dnse"
    "credentials_file": None,   # None → creds mặc định theo broker
    "account_id": None,         # None → tiểu khoản đầu tiên của login/key đó
    "note": "",
    "overrides": {},            # override bất kỳ khóa nào của config chung cho riêng account
}


def load_accounts(cfg, path=ACCOUNTS_FILE):
    """Đọc danh sách account profile; chưa có file → tạo template 1 profile 'main'.

    Trả về list profile đã chuẩn hóa, mỗi profile có thêm khóa "cfg" = config
    hiệu lực (config chung + overrides + mode/account_id của profile).
    """
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            raw = json.load(f).get("accounts", [])
    else:
        raw = [{"label": "main", "mode": cfg["mode"],
                "account_id": cfg.get("account_id"),
                "note": "profile mặc định — thêm account mới vào danh sách này"}]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"accounts": raw}, f, indent=2, ensure_ascii=False)
        print(f"[config] tạo file account profile mặc định: {path}")

    profiles, seen = [], set()
    for r in raw:
        p = dict(ACCOUNT_DEFAULTS)
        p.update(r)
        if p["label"] in seen:
            raise ValueError(f"trùng label account '{p['label']}' trong {path}")
        seen.add(p["label"])
        eff = dict(cfg)
        eff.update(p.get("overrides") or {})
        eff["mode"] = p["mode"] or cfg["mode"]
        eff["account_id"] = p["account_id"]
        p["cfg"] = eff
        profiles.append(p)
    return profiles


def pick_accounts(profiles, labels=None):
    """Lọc profile theo --account labels; mặc định = mọi profile enabled."""
    if labels:
        by = {p["label"]: p for p in profiles}
        missing = [l for l in labels if l not in by]
        if missing:
            raise KeyError(f"không có account {missing} — có: {sorted(by)}")
        return [by[l] for l in labels]
    return [p for p in profiles if p["enabled"]]


def load_config(path=CONFIG_FILE):
    cfg = dict(DEFAULTS)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        unknown = sorted(set(user) - set(DEFAULTS))
        if unknown:
            print(f"[config] ⚠ khóa lạ trong {os.path.basename(path)}: {unknown}")
        cfg.update(user)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULTS, f, indent=2, ensure_ascii=False)
        print(f"[config] tạo file cấu hình mặc định: {path}")
    return cfg
