#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAP_SIGNAL advisory check — tín hiệu ADVISORY THAM KHẢO (KHÔNG wire production), user duyệt
2026-08-30 21:10 ICT (decided_by=user), nguồn:
research/diverge_indicator_strategy_backtest_round2_20260830.md (quant-skeptic CONFIRMED medium
confidence, nhưng N~6 cụm macro độc lập/15 năm — quá mỏng để wire kỹ thuật).

Composite = DIVERGE (EM_dd60<=-8% AND VNI_dd60>=-3%) AND xác nhận (DXY_mom60>=5% OR TNX>=3.0).
Ngưỡng PRE-REGISTERED, giống hệt production_mechanism_2009_2018_20260830.md §B.2 +
cap_signal_grid_test_round2.py — KHÔNG re-tune ở đây.

Nguồn dữ liệu SỐNG (không phải data/tier2_macro_panel.csv — file đó đóng băng 2026-05-15,
KHÔNG refresh tự động, KHÔNG dùng cho advisory sống):
  - VNI (VNINDEX Close)  <- tav2_bq.ticker (sync nightly 23:45 ICT, xem CLAUDE.md same-day trap)
  - EEM/DXY/TNX          <- yfinance (EEM, DX-Y.NYB, ^TNX), free/scriptable, verified sống 2026-08-30

Mỗi lần fire ghi 1 dòng vào registry CSV (kb/data_registry/market-state/cap_signal_advisory_log.csv).
Cụm hoá: fire cách fire gần nhất trong CÙNG cụm <=60 ngày lịch -> vẫn cụm đó; >60 ngày -> cụm mới
(khớp đúng luật gộp cụm dùng trong round2 nghiên cứu, đơn vị N là CỤM MACRO ĐỘC LẬP, không phải
số lần fire).

Ngưỡng nâng cấp: N_clusters >= 10 (tham khảo cỡ mẫu tối thiểu cho DSR/PBO chính thức theo
quant-research skill — 6 hiện tại quá mỏng, 10-12 là ngưỡng thường dùng để bắt đầu chạy DSR có
ý nghĩa). Khi đạt, script tự bắn 1 bus `question` đề xuất escalate xem xét wire — KHÔNG tự wire.

DÙNG:
    python3 mike/agents/Taylor/cap_signal_advisory_check.py                # chạy check, in + ghi registry
    python3 mike/agents/Taylor/cap_signal_advisory_check.py --print-block  # khối text ngắn để nhúng report
    python3 mike/agents/Taylor/cap_signal_advisory_check.py --dry-run      # tính toán, KHÔNG ghi registry
"""
import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
REGISTRY_CSV = f"{WC}/mike/kb/data_registry/market-state/cap_signal_advisory_log.csv"
PROJECT = "lithe-record-440915-m9"
W = 60
EM_DD_THRESH = -0.08
VNI_DD_THRESH = -0.03
DXY_MOM_THRESH = 0.05
TNX_THRESH = 3.0
CLUSTER_GAP_DAYS = 60
UPGRADE_N_CLUSTERS = 10

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")


def fetch_vni_bq():
    """VNI Close, 400 lịch gần nhất, đủ warmup cho rolling 60-phiên."""
    cmd = [
        "bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}", "--format=csv",
        "SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' "
        "ORDER BY t.time DESC LIMIT 400",
    ]
    env = os.environ.copy()
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=WC, env=env, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(f"bq query VNI FAIL: {out.stderr[:500]}")
    from io import StringIO
    df = pd.read_csv(StringIO(out.stdout))
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df = df.rename(columns={"Close": "VNI"})
    return df[["time", "VNI"]]


def fetch_global_proxies_yf():
    import yfinance as yf
    frames = {}
    for name, sym in [("EEM", "EEM"), ("DXY", "DX-Y.NYB"), ("TNX", "^TNX")]:
        h = yf.Ticker(sym).history(period="400d", auto_adjust=False)
        if len(h) < 100:
            raise RuntimeError(f"yfinance {name} ({sym}): chỉ {len(h)} dòng, không đủ warmup 60d")
        h = h[["Close"]].copy()
        h.columns = [name]
        h.index = pd.to_datetime(h.index.date)
        frames[name] = h
    df = pd.concat(frames.values(), axis=1, join="outer", sort=True)
    df = df.rename_axis("time").reset_index()
    return df


def compute_signal():
    vni = fetch_vni_bq()
    proxies = fetch_global_proxies_yf()
    mp = pd.merge(vni, proxies, on="time", how="inner").sort_values("time").reset_index(drop=True)
    # yfinance có thể trả dòng NGÀY CUỐI với Close NaN nếu phiên Mỹ chưa đóng cửa tại thời điểm
    # fetch (VN giờ đi trước) — bỏ các dòng CHƯA HOÀN TẤT thay vì tính rolling trên dữ liệu rỗng.
    mp = mp.dropna(subset=["EEM", "DXY", "TNX"]).reset_index(drop=True)
    if len(mp) < W + 5:
        raise RuntimeError(f"Sau merge chỉ {len(mp)} phiên trùng ngày VNI/yfinance — không đủ.")

    mp["EM_dd60"] = mp["EEM"] / mp["EEM"].rolling(W, min_periods=W).max() - 1
    mp["VNI_dd60"] = mp["VNI"] / mp["VNI"].rolling(W, min_periods=W).max() - 1
    mp["DXY_mom60"] = mp["DXY"] / mp["DXY"].shift(W) - 1
    mp["diverge"] = (mp["EM_dd60"] <= EM_DD_THRESH) & (mp["VNI_dd60"] >= VNI_DD_THRESH)
    mp["cap_signal"] = mp["diverge"] & ((mp["DXY_mom60"] >= DXY_MOM_THRESH) | (mp["TNX"] >= TNX_THRESH))

    latest = mp.iloc[-1]
    return mp, latest


def load_registry():
    if not os.path.exists(REGISTRY_CSV):
        return pd.DataFrame(columns=["fire_date", "cluster_id", "EM_dd60", "VNI_dd60", "DXY_mom60", "TNX", "checked_at_ict"])
    return pd.read_csv(REGISTRY_CSV, parse_dates=["fire_date"])


def append_registry(fire_date, em_dd60, vni_dd60, dxy_mom60, tnx):
    reg = load_registry()
    if len(reg) and (reg["fire_date"] == pd.Timestamp(fire_date)).any():
        return reg, False  # đã ghi ngày này rồi, tránh trùng khi chạy lại nhiều lần/ngày
    if len(reg):
        last_fire = reg["fire_date"].max()
        gap = (pd.Timestamp(fire_date) - last_fire).days
        cluster_id = int(reg["cluster_id"].max()) if gap <= CLUSTER_GAP_DAYS else int(reg["cluster_id"].max()) + 1
    else:
        cluster_id = 1
    row = {
        "fire_date": fire_date, "cluster_id": cluster_id,
        "EM_dd60": round(em_dd60, 4), "VNI_dd60": round(vni_dd60, 4),
        "DXY_mom60": round(dxy_mom60, 4), "TNX": round(tnx, 3),
        "checked_at_ict": datetime.now(_ICT).strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    reg = pd.concat([reg, pd.DataFrame([row])], ignore_index=True)
    os.makedirs(os.path.dirname(REGISTRY_CSV), exist_ok=True)
    reg.to_csv(REGISTRY_CSV, index=False)
    return reg, True


def n_independent_clusters(reg):
    return reg["cluster_id"].nunique() if len(reg) else 0


def maybe_escalate(reg, trace_id=None):
    n = n_independent_clusters(reg)
    if n < UPGRADE_N_CLUSTERS:
        return
    payload = (
        f'{{"n_clusters": {n}, "upgrade_threshold": {UPGRADE_N_CLUSTERS}, '
        f'"registry": "kb/data_registry/market-state/cap_signal_advisory_log.csv", '
        f'"note": "CAP_SIGNAL da tich luy du {n} cum doc lap, de xuat quant-skeptic + user xem '
        f'xet wire production (KHONG tu dong wire)"}}'
    )
    cmd = [f"{WC}/mike/bin/append_event.sh", "Taylor", "question", "cap-signal-upgrade-threshold-reached", payload]
    if trace_id:
        cmd.append(trace_id)
    subprocess.run(cmd, check=False)


def build_advisory_line(mp, reg, html=False):
    latest = mp.iloc[-1]
    n = n_independent_clusters(reg)
    fired = bool(latest["cap_signal"])
    date_s = pd.Timestamp(latest["time"]).strftime("%Y-%m-%d")
    status = "FIRE" if fired else ("diverge-only" if bool(latest["diverge"]) else "quiet")
    line = (
        f"CAP_SIGNAL advisory ({date_s}): {status} | EM_dd60={latest['EM_dd60']*100:.1f}% "
        f"VNI_dd60={latest['VNI_dd60']*100:.1f}% DXY_mom60={latest['DXY_mom60']*100:.1f}% "
        f"TNX={latest['TNX']:.2f} | N_clusters={n}/{UPGRADE_N_CLUSTERS} — ADVISORY THAM KHẢO, "
        f"KHÔNG phải tín hiệu mua/bán tự động."
    )
    if html:
        return f"<p>{line}</p>"
    return line


def run_advisory(write_registry=True, trace_id=None):
    """Single entry point for embedding the advisory in a report (dna_report.py's
    build_cap_signal_advisory_line): compute the live composite, persist a fire to the
    registry if one occurred today (idempotent — append_registry no-ops on a duplicate
    date, so calling this from >=1 report/day is safe), return the display line.
    Raises on any live-data failure — caller (dna_report.py) is responsible for the
    fail-safe try/except, same contract as build_dt_gate_line/build_value_radar_line."""
    mp, latest = compute_signal()
    reg = load_registry()
    if write_registry and bool(latest["cap_signal"]):
        reg, wrote = append_registry(
            pd.Timestamp(latest["time"]).date(),
            float(latest["EM_dd60"]), float(latest["VNI_dd60"]),
            float(latest["DXY_mom60"]), float(latest["TNX"]),
        )
        if wrote:
            maybe_escalate(reg, trace_id=trace_id)
    return build_advisory_line(mp, reg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-block", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--trace-id", default=None)
    args = ap.parse_args()

    mp, latest = compute_signal()
    reg = load_registry()
    wrote = False
    if bool(latest["cap_signal"]) and not args.dry_run:
        reg, wrote = append_registry(
            pd.Timestamp(latest["time"]).date(),
            float(latest["EM_dd60"]), float(latest["VNI_dd60"]),
            float(latest["DXY_mom60"]), float(latest["TNX"]),
        )
        if wrote:
            maybe_escalate(reg, trace_id=args.trace_id)

    if args.print_block:
        print(build_advisory_line(mp, reg))
        return

    print(f"Latest session: {pd.Timestamp(latest['time']).date()}")
    print(f"  EM_dd60={latest['EM_dd60']*100:.2f}%  VNI_dd60={latest['VNI_dd60']*100:.2f}%  "
          f"DXY_mom60={latest['DXY_mom60']*100:.2f}%  TNX={latest['TNX']:.2f}")
    print(f"  diverge={bool(latest['diverge'])}  cap_signal(FIRE)={bool(latest['cap_signal'])}")
    print(f"  registry write: {'YES (new fire logged)' if wrote else 'no (dry-run/no-fire/dup)'}")
    print(f"  N cụm độc lập tích luỹ: {n_independent_clusters(reg)} / ngưỡng nâng cấp {UPGRADE_N_CLUSTERS}")
    print()
    print(build_advisory_line(mp, reg))


if __name__ == "__main__":
    sys.exit(main())
