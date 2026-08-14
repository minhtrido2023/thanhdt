#!/usr/bin/env python3
"""Đo tác động NẾU mở hard-block anomaly sang BAL/LAG (hiện chỉ áp cho rổ CAPIT).

Job Taylor_20260814_041116, Việc 4. **ĐO LƯỜNG THUẦN — KHÔNG đổi một dòng code chọn mã nào.**
Đây là câu hỏi CHÍNH SÁCH (user quyết sau khi xem số), không phải câu hỏi kỹ thuật.

Câu hỏi cần trả lời chính xác:
  (1) Nếu hard-block áp cho BAL/LAG như CAPIT, nó sẽ chặn BAO NHIÊU lệnh mua trong lịch sử?
  (2) Trong số bị chặn, bao nhiêu là case xấu THẬT (kiểu DGC/PNJ) vs chặn oan cơ hội tốt?

Nguồn:
  - Lệnh mua BAL/LAG thật: sổ giao dịch của backtest R3 đã pin
    data/v23_golive_audit_2014_now_...cap50b_ideal_univpit.csv (record_type=TX), 2014-01→2026-06.
  - Cờ anomaly lịch sử: TÁI LẬP bằng chính `anomaly_scan.compute_signals()` (import, không chép
    lại luật — chép lại là tự tạo ra một bản thứ hai lệch dần) trên `data/bq_cache/ticker/*.parquet`.
  - Universe PIT của bộ quét: `data/bq_cache/fa_ratings_8l.parquet` (rating<=2), có từ 2014-07.

KHÔNG look-ahead: cờ chỉ được tính là "đã biết" nếu phiên alert <= ngày mua − 1 (production:
anomaly_scan 08:20 đọc cache T-1 → golive_recommend 19:00 cùng ngày → lệnh cho phiên sau).
"""
import argparse
import os
import sys

import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(WC, "mike/agents/Taylor"))
import anomaly_scan as A   # noqa: E402  — dùng LẠI luật tín hiệu, không viết lại

AUDIT = os.path.join(WC, "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
                         "etfliqcustompitg_wtnamecap_liquncap_advprice_exp_cap50b_ideal_univpit.csv")
TTL_DAYS = 30          # bằng ANOMALY_TTL_DAYS của anomaly_gate.py
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Lệnh mua thuộc rổ CAPIT (đã bị chặn cứng HÔM NAY) và parking ETF (không phải chọn mã) không
# nằm trong câu hỏi — câu hỏi là phần CHƯA bị chặn.
EXCLUDE_PLAY_PREFIX = ("CAPITB", "CAPITL", "ETF_PARK")


def load_buys():
    d = pd.read_csv(AUDIT, low_memory=False)
    tx = d[d.record_type == "TX"].copy()
    tx["ymd"] = pd.to_datetime(tx["ymd"])
    buys = tx[(tx.action == "buy") & (~tx.play_type.astype(str).str.startswith(EXCLUDE_PLAY_PREFIX))].copy()
    sells = tx[tx.action == "sell"].copy()
    return buys, sells


def realized_by_holding(buys, sells):
    """Lãi/lỗ thực của TỪNG vị thế (khớp buy↔sell qua holding_id, gộp bán từng phần)."""
    b = buys.groupby("holding_id").agg(buy_amt=("buy_amount", "sum"),
                                       fee_b=("fee", "sum")).reset_index()
    s = sells.groupby("holding_id").agg(sell_amt=("sell_amount", "sum"),
                                        fee_s=("fee", "sum"),
                                        exit_ymd=("ymd", "max")).reset_index()
    m = b.merge(s, on="holding_id", how="left")
    m["closed"] = m["sell_amt"].notna()
    m["pnl_vnd"] = m["sell_amt"].fillna(0) - m["buy_amt"] - m["fee_b"] - m["fee_s"].fillna(0)
    m["ret_pct"] = 100 * m["pnl_vnd"] / m["buy_amt"]
    return m


def rebuild_flags(tickers, start, end):
    """Tái lập cờ anomaly lịch sử bằng ĐÚNG luật production.

    hold=set() ⇒ áp nhánh tier W (chặt hơn: có cổng thanh khoản + giá trị GD tuyệt đối). Đó là
    nhánh ĐÚNG cho một mã đang là ỨNG VIÊN MUA — nó chưa nằm trong danh mục. Dùng nhánh tier H
    ở đây sẽ thổi phồng số lần chặn.
    """
    out = []
    tickers = sorted(tickers)
    step = 120
    for i in range(0, len(tickers), step):
        chunk = set(tickers[i:i + step])
        df = A.load_prices(chunk, start, end)
        if df.empty:
            continue
        out.append(A.compute_signals(df, hold=set()))
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def pit_rating_universe():
    """(ticker, time, rating) — để hỏi 'tại ngày D, mã này có nằm trong universe quét không'."""
    fr = pd.read_parquet(os.path.join(WC, "data/bq_cache/fa_ratings_8l.parquet"))
    fr["time"] = pd.to_datetime(fr["time"])
    return fr[["ticker", "time", "rating"]].sort_values("time")


def was_flagged(alerts_by_tk, ticker, buy_date, lag_days=1):
    """Cờ còn hiệu lực tại ngày mua, KHÔNG look-ahead (alert <= buy_date − lag_days)."""
    a = alerts_by_tk.get(ticker)
    if a is None:
        return None
    hi = buy_date - pd.Timedelta(days=lag_days)
    lo = buy_date - pd.Timedelta(days=TTL_DAYS)
    hit = a[(a["time"] >= lo) & (a["time"] <= hi)]
    return None if hit.empty else hit.iloc[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lag-days", type=int, default=1,
                    help="cờ phải có trước ngày mua bao nhiêu ngày mới coi là 'đã biết'")
    args = ap.parse_args()

    buys, sells = load_buys()
    print(f"# Sổ giao dịch R3 (pin 2026-08-03) — {AUDIT.split('/')[-1]}")
    print(f"  lệnh mua BAL/LAG (đã trừ CAPIT + ETF_PARK): {len(buys)} "
          f"trên {buys.ticker.nunique()} mã, {buys.ymd.min().date()} → {buys.ymd.max().date()}")
    print("  phân bố book/play:", buys.groupby(["book", "play_type"]).size().to_dict())

    pnl = realized_by_holding(buys, sells).set_index("holding_id")
    start = (buys.ymd.min() - pd.Timedelta(days=120)).date()
    end = buys.ymd.max().date()
    print(f"\n# Tái lập cờ anomaly (tier W, luật production) {start} → {end} …")
    al = rebuild_flags(set(buys.ticker), start, end)
    print(f"  {len(al)} phiên-cờ trên {al.ticker.nunique()} mã")

    alerts_by_tk = {tk: g.sort_values("time") for tk, g in al.groupby("ticker")}
    fr = pit_rating_universe()
    rat_by_tk = {tk: g for tk, g in fr.groupby("ticker")}

    rows = []
    for _, r in buys.iterrows():
        hit = was_flagged(alerts_by_tk, r["ticker"], r["ymd"], args.lag_days)
        # Universe PIT: bản rating gần nhất CÓ TRƯỚC ngày mua (không nhìn tương lai).
        g = rat_by_tk.get(r["ticker"])
        in_scan_uni = False
        if g is not None:
            prior = g[g["time"] <= r["ymd"]]
            if not prior.empty:
                in_scan_uni = bool(prior.iloc[-1]["rating"] <= 2)
        p = pnl.loc[r["holding_id"]] if r["holding_id"] in pnl.index else None
        rows.append({
            "ymd": r["ymd"], "book": r["book"], "play": r["play_type"], "ticker": r["ticker"],
            "holding_id": r["holding_id"], "buy_amount": r["buy_amount"],
            "flagged": hit is not None,
            "flag_date": None if hit is None else str(hit["time"].date()),
            "flag_reasons": None if hit is None else hit["reasons"],
            "flag_ret": None if hit is None else round(float(hit["ret"]), 2),
            "in_scan_universe_pit": in_scan_uni,
            "closed": bool(p["closed"]) if p is not None else False,
            "ret_pct": float(p["ret_pct"]) if p is not None else float("nan"),
            "pnl_vnd": float(p["pnl_vnd"]) if p is not None else float("nan"),
        })
    R = pd.DataFrame(rows)
    out_csv = os.path.join(OUT_DIR, "balleg_hardblock_events.csv")
    R.to_csv(out_csv, index=False)

    def summarize(sub, label):
        n = len(sub)
        if n == 0:
            print(f"  {label}: 0 lệnh")
            return
        c = sub[sub.closed]
        win = (c.ret_pct > 0).sum()
        sev = (c.ret_pct <= -20).sum()
        print(f"  {label}: n={n} | đã đóng {len(c)} | thắng {win} ({100*win/max(len(c),1):.1f}%) "
              f"| lỗ nặng ≤−20%: {sev} ({100*sev/max(len(c),1):.1f}%) "
              f"| ret trung vị {c.ret_pct.median():+.2f}% trung bình {c.ret_pct.mean():+.2f}% "
              f"| tổng P&L {c.pnl_vnd.sum()/1e9:+.2f} tỷ")

    print(f"\n# (1) HARD-BLOCK SẼ CHẶN BAO NHIÊU LỆNH? (lag {args.lag_days} ngày, TTL {TTL_DAYS} ngày)")
    print(f"  TỔNG lệnh mua BAL/LAG: {len(R)}")
    blk_all = R[R.flagged]
    blk_real = R[R.flagged & R.in_scan_universe_pit]
    print(f"  bị chặn — CẬN TRÊN (giả định bộ quét phủ mọi ứng viên): {len(blk_all)} "
          f"({100*len(blk_all)/len(R):.1f}%)")
    print(f"  bị chặn — THỰC TẾ HÔM NAY (mã nằm trong universe quét rating<=2 tại thời điểm đó): "
          f"{len(blk_real)} ({100*len(blk_real)/len(R):.1f}%)")

    print("\n# (2) CHẶN ĐÚNG HAY CHẶN OAN? — so kết cục THẬT của chính những lệnh đó")
    summarize(R[~R.flagged], "KHÔNG bị chặn (đối chứng)")
    summarize(blk_all, "BỊ CHẶN (cận trên)   ")
    summarize(blk_real, "BỊ CHẶN (thực tế)    ")

    # Phân rã theo LOẠI cờ. `anomaly_excluded()` production KHÔNG phân biệt lý do — mọi cờ đều
    # loại mã. Nhưng CEIL2 là "trần 2 phiên" = giá TĂNG mạnh: chặn lệnh mua vì cổ phiếu vừa tăng
    # KHÔNG phải là "bảo vệ khỏi tin xấu", và nó là phần lớn số ca ở đây. Phải tách ra mới trả
    # lời được đúng câu hỏi user hỏi (case xấu thật kiểu DGC/PNJ).
    def cls(reasons):
        r = set(str(reasons).split(","))
        if r & {"FLOOR2", "IDIOCRASH"}:
            return "SẬP (FLOOR2/IDIOCRASH) — đúng hình dạng DGC/PNJ"
        if "CEIL2" in r:
            return "TĂNG TRẦN (CEIL2) — không phải tin xấu"
        return "VOLSPIKE đơn thuần"

    print("\n# (3) PHÂN RÃ THEO LOẠI CỜ — production hiện KHÔNG phân biệt, nhưng nên phân biệt")
    R["flag_class"] = R.flag_reasons.map(lambda x: cls(x) if pd.notna(x) else None)
    for k in sorted(R.flag_class.dropna().unique()):
        summarize(R[R.flag_class == k], f"{k:52s}")
    print("  → so sánh: " + f"{'KHÔNG bị chặn (đối chứng)':52s}")
    summarize(R[~R.flagged], f"{'(đối chứng, không cờ)':52s}")

    print("\n# (4) NĂM NÀO GÁNH KẾT QUẢ? (edge mỏng năm = reshuffle-luck, không phải tín hiệu bền)")
    blk = R[R.flagged & R.closed].copy()
    blk["year"] = blk.ymd.dt.year
    per = blk.groupby("year").agg(n=("ret_pct", "size"), ret_tb=("ret_pct", "mean"),
                                  pnl_ty=("pnl_vnd", lambda s: s.sum() / 1e9)).round(2)
    print(per.to_string())

    print("\n# Chi tiết từng lệnh bị chặn (cận trên), sắp theo lãi/lỗ thật:")
    cols = ["ymd", "book", "play", "ticker", "flag_date", "flag_reasons", "flag_ret",
            "in_scan_universe_pit", "closed", "ret_pct", "pnl_vnd"]
    bb = blk_all[cols].copy()
    bb["ymd"] = bb["ymd"].dt.date
    bb["pnl_vnd"] = (bb["pnl_vnd"] / 1e6).round(1)
    bb = bb.rename(columns={"pnl_vnd": "pnl_trieu"})
    print(bb.sort_values("ret_pct").to_string(index=False))

    print(f"\n→ CSV đầy đủ: {out_csv}")


if __name__ == "__main__":
    main()
