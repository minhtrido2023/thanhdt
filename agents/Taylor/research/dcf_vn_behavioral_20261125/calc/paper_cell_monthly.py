# -*- coding: utf-8 -*-
"""paper_cell_monthly.py — GHI NHẬN hằng tháng ô bốn-ô + điểm thừa nhận hi52 (DISPLAY-ONLY, theo dõi paper; user duyệt 25/11/2026).
KHÔNG sizing, KHÔNG gate, KHÔNG đụng dcf_valuation.py / macro_state_live.py. Append-only CSV, mỗi (asof_ym) ghi đúng 1 lần.
Nguồn (đã tra mike/kb/data_registry/): universe_pit (data/bq_cache/universe_pit, CANONICAL; KHÔNG ticker_prune) · giá = data/bq_cache/ticker (Close điều chỉnh)
· lv_ENS2 + route = panel V3.1 `vp2.parquet` (cần dựng lại hằng tháng — xem PAPER_REGISTRY_PROPOSED.md).
Fail-closed: universe_pit không phủ ngày as-of ⇒ rc=3, KHÔNG ghi. Ô: v = hạng lv_ENS2 (trong nhóm route BANK / phi-BANK nếu ≥15 mã, else toàn universe),
a = hạng hi52 = log(Close / max Close 252 phiên) toàn universe; ô theo trung vị v,a (>=0,5 = cao). Nhãn ô là MÔ TẢ (giả thuyết), không phải tín hiệu.
Dùng:  python paper_cell_monthly.py --asof-ym 2026-10 [--ledger PATH] [--panel PATH] [--dry-run]"""
import argparse, hashlib, os, sys, glob, csv
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, duckdb
WC = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude"); HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.environ.get("V3_PANEL", f"{WC}/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/out_F/vp2.parquet")
LEDGER = os.environ.get("PCM_LEDGER", os.path.join(HERE, "..", "out", "paper_cell_ledger.csv"))
_ICT = ZoneInfo("Asia/Ho_Chi_Minh"); MINGRP = 15
COLS = ["asof_ym", "asof_date", "ticker", "route", "lv_ENS2", "hi52", "v_grp", "v_all", "a", "cell", "panel_time_match", "computed_at_ict", "panel_md5"]
CELL = {(1, 1): "RE_DUOC_THUA_NHAN", (1, 0): "RE_CHUA_THUA_NHAN", (0, 1): "DAT_CON_NEO", (0, 0): "DAT_DANG_NGUOI"}

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--asof-ym", required=True); ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--panel", default=PANEL); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    ym = a.asof_ym
    if os.path.exists(a.ledger) and (pd.read_csv(a.ledger, usecols=["asof_ym"]).asof_ym == ym).any():
        print(f"SKIP: {ym} đã có trong {a.ledger} (append-only, idempotent)"); return 0
    c = duckdb.connect()
    px = c.execute(f"""SELECT ticker, CAST(time AS DATE) AS time, Close FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
                       WHERE Close > 0 AND CAST(time AS DATE) >= DATE '{ym}-01' - INTERVAL 450 DAY AND strftime(CAST(time AS DATE), '%Y-%m') <= '{ym}'""").df()
    px["time"] = pd.to_datetime(px.time)
    D = px[px.time.dt.strftime("%Y-%m") == ym].time.max()
    if pd.isna(D): print(f"FAIL: không có giá ngày nào của {ym}", file=sys.stderr); return 3
    u = pd.read_parquet(f"{WC}/data/bq_cache/universe_pit/{D.year}.parquet", columns=["time", "ticker", "in_universe"]); u["time"] = pd.to_datetime(u.time)
    ud = u[u.time == D]
    if ud.empty:
        print(f"FAIL-CLOSED: universe_pit không phủ {D.date()} (max {u.time.max().date()}) — KHÔNG ghi {ym}", file=sys.stderr); return 3
    px = px.sort_values(["ticker", "time"]).reset_index(drop=True); g = px.groupby("ticker")
    px["hi52"] = np.log(px.Close) - np.log(g.Close.rolling(252, min_periods=120).max().reset_index(level=0, drop=True).sort_index().values)
    f = px[px.time == D][["ticker", "hi52"]]
    pan = pd.read_parquet(a.panel, columns=["ticker", "ym", "time", "route", "lv_ENS2"]); pan = pan[pan.ym.astype(str) == ym]
    d = ud[ud.in_universe].merge(f, on="ticker").merge(pan[["ticker", "time", "route", "lv_ENS2"]].rename(columns={"time": "ptime"}), on="ticker").dropna(subset=["hi52", "lv_ENS2"]).copy()
    if len(d) < 50: print(f"FAIL-CLOSED: chỉ {len(d)} mã đủ dữ liệu ở {ym}", file=sys.stderr); return 3
    d["v_all"] = d.lv_ENS2.rank(pct=True); d["a"] = d.hi52.rank(pct=True); d["isb"] = d.route == "BANK"
    d["v_grp"] = d.groupby("isb").lv_ENS2.rank(pct=True); n = d.groupby("isb").ticker.transform("size"); d["v_grp"] = np.where(n >= MINGRP, d.v_grp, d.v_all)
    d["cell"] = [CELL[(int(v >= 0.5), int(x >= 0.5))] for v, x in zip(d.v_grp, d.a)]
    d["panel_time_match"] = (d.ptime == D); d["asof_ym"] = ym; d["asof_date"] = D.date()
    d["computed_at_ict"] = datetime.now(_ICT).strftime("%Y-%m-%d %H:%M"); d["panel_md5"] = md5(a.panel)
    out = d[COLS].sort_values("ticker")
    print(f"{ym}: as-of {D.date()} n={len(out)} (BANK {int(d.isb.sum())}) panel_time_match={out.panel_time_match.mean():.3f}"); print(out.cell.value_counts().to_string())
    if a.dry_run: print("dry-run: không ghi"); return 0
    os.makedirs(os.path.dirname(os.path.abspath(a.ledger)), exist_ok=True); new = not os.path.exists(a.ledger)
    tmp = a.ledger + ".tmp"
    if new: out.to_csv(tmp, index=False)
    else: pd.concat([pd.read_csv(a.ledger), out], ignore_index=True).to_csv(tmp, index=False)
    os.replace(tmp, a.ledger); print("ĐÃ GHI", a.ledger); return 0

if __name__ == "__main__": sys.exit(main())
