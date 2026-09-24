#!/usr/bin/env python3
"""K1/K2 — đo phân bố vendor_check trên dữ liệu THẬT (mã đã/đang giữ ở 2 TK).

⚠️ NHÃN CỘT (sửa 2026-09-24 sau arch-review vòng 2, SAI 2): cột dưới là `per_share`, KHÔNG
phải "số broker giải ra" ở mọi dòng. Với `kind == CASH_VENDOR`, `dividend_adjusted_return.py:1036`
đã gán `adj.per_share = adj.vendor_cash` TRƯỚC khi in ⇒ hai cột bằng nhau BY CONSTRUCTION, đó là
TAUTOLOGY chứ không phải đối soát hai nguồn. Bản trước nhãn cột là `broker=` nên 17 dòng
CASH_VENDOR "khớp" mời người đọc hiểu là 23 ca có bằng chứng độc lập. CƠ SỞ BẰNG CHỨNG ĐỘC LẬP
CHỈ LÀ 6 ca `CASH_CONFIRMED` (broker giải từ tiền thật, vendor xác nhận) — xem cột `kind`.
"""
import os, sys, json, collections
BIN = sys.argv[1] if len(sys.argv) > 1 else "/home/trido/thanhdt/WorkingClaude/mike/bin"
sys.path.insert(0, BIN)
import dividend_adjusted_return as dar

TICKERS = "ACB,BID,CSV,CTG,DCM,DGC,DRI,EVF,HAH,HDB,HPG,LPB,MBB,MBS,MSB,MSH,NCT,PVT,SAB,SCL,SHB,SHS,SIP,TCB,TCM,TLG,TPB,TV1,VCB,VGC,VHC,VHM,VIB,VIX,VND,VNM,VPB,VPI,VRE".split(",")
START, END = os.environ.get("K1_START", "2026-03-24"), os.environ.get("K1_END", "2026-09-24")

adjs = dar.resolve_dividends(TICKERS, START, END, with_crosscheck=False)
cnt = collections.Counter()
rows = []
for a in sorted(adjs, key=lambda z: (z.ex_date, z.ticker)):
    cnt[(a.kind, a.vendor_check)] += 1
    rows.append(dict(ticker=a.ticker, ex_date=a.ex_date, kind=a.kind, source=a.source,
                     per_share=a.per_share, vendor_cash=a.vendor_cash,
                     vendor_stock=a.vendor_stock, vendor_check=a.vendor_check,
                     share_multiplier=a.share_multiplier, vendor_note=a.vendor_note[:120]))
print(f"Cửa sổ {START} → {END} · {len(TICKERS)} mã · {len(adjs)} sự kiện\n")
for k, v in sorted(cnt.items()):
    print(f"  {k[0]:17s} vendor_check={k[1]:12s} : {v}")
print("\n--- CHI TIẾT ---")
for r in rows:
    flag = " <<< MISMATCH" if r["vendor_check"] == "mismatch" else ""
    print(f"  {r['ticker']:5s} {r['ex_date']}  {r['kind']:17s} {r['source']:14s} "
          f"per_share={r['per_share']:>9,.1f}  vendor_cash={r['vendor_cash']:>9,.1f} "
          f"vendor_stock={r['vendor_stock']:.4f}  mult={r['share_multiplier']:.4f} "
          f"[{r['vendor_check']}]{flag}")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "k1_rows.json"), "w") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)
