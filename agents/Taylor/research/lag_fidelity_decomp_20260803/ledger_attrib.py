# -*- coding: utf-8 -*-
"""ledger_attrib.py — T3: phân rã Δ(L1−L0) từ SỔ LỆNH của 2 chân A/B (KHÔNG chạy backtest mới).

Job Taylor_20260803_021414. Trả lời đúng câu quant-skeptic đòi (verify_20260802_173456.log):
tách "vốn chảy sang event LAG tốt hơn" (edge) khỏi "sổ 25B không fill nổi size" (hiện vật fill).

Ba đại lượng đo được thẳng từ CSV audit, không suy luận:
  (1) BLOCKED bucket  — mã CÓ vào lệnh ở L0 nhưng KHÔNG hề có ở L1 (= nhóm ADV<=0 bị chặn).
                         P&L thực hiện của nhóm này ở L0 = tác động TRỰC TIẾP (né lỗ/né lãi).
  (2) SUBSTITUTION     — phần Δ NAV còn lại sau khi trừ (1) = do vốn tái triển khai + compounding.
  (3) IDLE/DEPLOYMENT  — tỷ lệ vốn sổ LAG thực sự nằm trong cổ phiếu (lag_stocks/(cash+stocks))
                         theo phiên. Giả thuyết "không fill nổi" BẮT BUỘC kéo tỷ lệ này XUỐNG ở L1.
"""
import sys
import pandas as pd

L0 = sys.argv[1]
L1 = sys.argv[2]


def load(path):
    d = pd.read_csv(path, low_memory=False)
    tx = d[d.record_type == "TX"].copy()
    tx["ymd"] = pd.to_datetime(tx["ymd"])
    for c in ("shares", "buy_amount", "sell_amount", "fee"):
        tx[c] = pd.to_numeric(tx[c], errors="coerce").fillna(0.0)
    daily = d[d.record_type == "DAILY"].copy()
    daily["ymd"] = pd.to_datetime(daily["ymd"])
    for c in ("lag_cash_ref", "lag_stocks_ref", "lag_etf_ref", "nav_lag_ref", "combined_nav"):
        daily[c] = pd.to_numeric(daily[c], errors="coerce")
    return tx, daily


def holdings(tx):
    """Gộp TX theo holding_id trong sổ LAG -> 1 dòng/vị thế với P&L thực hiện."""
    lag = tx[tx.book == "LAG"].copy()
    g = lag.groupby("holding_id")
    h = pd.DataFrame({
        "ticker": g["ticker"].first(),
        "play_type": g["play_type"].first(),
        "first_ymd": g["ymd"].min(),
        "last_ymd": g["ymd"].max(),
        "n_fills": g.apply(lambda x: (x.reason == "ENTRY_FILL").sum(), include_groups=False),
        "cost": g.apply(lambda x: (x.loc[x.action == "buy", "buy_amount"]
                                   + x.loc[x.action == "buy", "fee"]).sum(), include_groups=False),
        "proceeds": g.apply(lambda x: (x.loc[x.action == "sell", "sell_amount"]
                                       - x.loc[x.action == "sell", "fee"]).sum(), include_groups=False),
        "abandoned": g.apply(lambda x: (x.reason == "ABANDONED_REFUND").any(), include_groups=False),
    })
    h["pnl"] = h["proceeds"] - h["cost"]
    h["ret"] = h["pnl"] / h["cost"].where(h["cost"] > 0)
    return h


tx0, dy0 = load(L0)
tx1, dy1 = load(L1)
h0, h1 = holdings(tx0), holdings(tx1)

print("=" * 100)
print("T3 — PHAN RA LEDGER  L0 (control) vs L1 (LIQ_ZERO_BLOCK=lag)")
print("=" * 100)

nav0 = dy0.sort_values("ymd")["combined_nav"].iloc[-1]
nav1 = dy1.sort_values("ymd")["combined_nav"].iloc[-1]
print(f"NAV cuoi: L0={nav0/1e9:,.2f}B  L1={nav1/1e9:,.2f}B  DELTA={(nav1-nav0)/1e9:,.2f}B")

for tag, h in (("L0", h0), ("L1", h1)):
    done = h[~h.abandoned]
    ab = h[h.abandoned]
    print(f"\n[{tag}] vi the LAG: tong {len(h)}  hoan tat {len(done)}  abandoned {len(ab)} "
          f"({len(ab)/max(len(h),1):.1%})")
    print(f"      P&L thuc hien (hoan tat): {done.pnl.sum()/1e9:,.2f}B  | abandoned: {ab.pnl.sum()/1e9:,.3f}B")
    print(f"      von trien khai (tong cost hoan tat): {done.cost.sum()/1e9:,.1f}B")

# ---- (1) BLOCKED bucket ------------------------------------------------------
tk0 = set(h0.ticker)
tk1 = set(h1.ticker)
blocked = sorted(tk0 - tk1)
added = sorted(tk1 - tk0)
print(f"\n--- (1) BLOCKED = ma co o L0, KHONG he co o L1: {len(blocked)} ma ---")
b0 = h0[h0.ticker.isin(blocked)]
b0d = b0[~b0.abandoned]
print(f"  vi the: {len(b0)} (hoan tat {len(b0d)}), von trien khai {b0d.cost.sum()/1e9:,.2f}B")
print(f"  P&L TRUC TIEP cua nhom bi chan, do o L0: {b0.pnl.sum()/1e9:,.3f}B")
print(f"  ty le tren DELTA NAV: {b0.pnl.sum()/(nav1-nav0):.2%}  (am = nhom nay LO o L0)")
print(f"  10 ma lo nhat: ")
print(b0.groupby('ticker').pnl.sum().sort_values().head(10).div(1e9).round(3).to_string())

print(f"\n--- ma XUAT HIEN THEM o L1 (khong co o L0): {len(added)} ---")
a1 = h1[h1.ticker.isin(added)]
print(f"  vi the {len(a1)}, P&L {a1.pnl.sum()/1e9:,.3f}B")

# ---- (2) chung ca 2 chan -----------------------------------------------------
both = sorted(tk0 & tk1)
print(f"\n--- ma CO O CA HAI chan: {len(both)} ---")
c0 = h0[h0.ticker.isin(both)]
c1 = h1[h1.ticker.isin(both)]
print(f"  L0: {len(c0)} vi the, cost {c0.cost.sum()/1e9:,.1f}B, P&L {c0.pnl.sum()/1e9:,.2f}B")
print(f"  L1: {len(c1)} vi the, cost {c1.cost.sum()/1e9:,.1f}B, P&L {c1.pnl.sum()/1e9:,.2f}B")
print(f"  => chenh P&L tren cung tap ma: {(c1.pnl.sum()-c0.pnl.sum())/1e9:,.2f}B "
      f"(= hieu ung SIZING/TIMING/COMPOUNDING, khong phai chon ma khac)")

# ---- (3) deployment / idle ---------------------------------------------------
print("\n--- (3) MUC DO TRIEN KHAI VON SO LAG theo phien ---")
for tag, dy in (("L0", dy0), ("L1", dy1)):
    d = dy.dropna(subset=["lag_stocks_ref", "lag_cash_ref"]).copy()
    tot = d.lag_stocks_ref + d.lag_cash_ref + d.lag_etf_ref.fillna(0.0)
    dep = d.lag_stocks_ref / tot.where(tot > 0)
    print(f"  [{tag}] n={len(d)} phien  deployed_frac: mean={dep.mean():.3f} "
          f"median={dep.median():.3f} p10={dep.quantile(.10):.3f} p90={dep.quantile(.90):.3f}")
    print(f"        tien mat trung binh so LAG: {d.lag_cash_ref.mean()/1e9:,.2f}B  "
          f"NAV LAG trung binh: {tot.mean()/1e9:,.2f}B")

# ---- (4) so lan vao lenh / hoan tat theo nam ---------------------------------
print("\n--- (4) attempts vs completions theo nam ---")
for tag, h in (("L0", h0), ("L1", h1)):
    h = h.copy()
    h["yr"] = h.first_ymd.dt.year
    t = h.groupby("yr").agg(attempts=("ticker", "size"),
                            done=("abandoned", lambda s: (~s).sum()))
    t["fill_rate"] = t["done"] / t["attempts"]
    print(f"  [{tag}]")
    print(t.to_string())
