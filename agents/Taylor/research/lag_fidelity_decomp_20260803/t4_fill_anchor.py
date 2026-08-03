# -*- coding: utf-8 -*-
"""t4_fill_anchor.py — T4: NEO mo hinh fill cua engine vao FILL THAT cua DNSE (pha the sim-vs-sim, D3).

Job Taylor_20260803_045138 (tiep Taylor_20260803_021414).

Engine gia dinh (pt_v23_audit_2014.py:1329-1335, LIQ_LAG / LIQ_FULL):
    daily_max = (Volume_3M_P50 * Px) * 0.20      # tran mua MOI PHIEN cua 1 vi the
tuc: "mot phien co the mua toi 20% cua ADV (median 3 thang) ma van fill duoc".

Do tren fill THAT:
  (A) size_ratio = order_value / (ADV * 0.20)    -> lenh that lon co nao so voi tran engine
  (B) fill_rate  = filled_value / order_value    -> lenh do co fill KHONG
  (C) ratio_prereg = filled_value / (ADV * 0.20) -> chi so DA DANG KY TRUOC o README §4

Luu y BAT BUOC (coding_guidelines §12): dnse_raw_*.jsonl la file DUNG CHUNG nhieu account —
loc accountNo la buoc DAU TIEN, truoc moi phep tinh.
"""
import json
import glob
import os
import subprocess
import sys
from collections import defaultdict

WD = "/home/trido/thanhdt/WorkingClaude"
ACCOUNTS = {"0002023347": "SpaceX", "0001743768": "ZaloPay"}
START = "2026-07-01"

# ---------------------------------------------------------------- 1. plan -> book cua tung lenh
plan_book = {}          # (account, date, ticker) -> (book, play_type, plan_qty)
for f in sorted(glob.glob(f"{WD}/data/trade_plans/plan_*_2026-0[78]-*.json")):
    d = json.load(open(f))
    if d.get("mode") != "live":
        continue
    for o in d.get("orders") or []:
        if o.get("side") != "buy":
            continue
        plan_book[(d["account"], d["plan_date"], o.get("ticker"))] = (
            o.get("book"), o.get("play_type"), o.get("qty"))

# ---------------------------------------------------------------- 2. fill that tu dnse_raw
# Lay SNAPSHOT CUOI CUNG cua moi order id (orders/place_order deu chua snapshot).
final = {}              # (account_no, order_id) -> snapshot
for path in sorted(glob.glob(f"{WD}/data/execution_logs/dnse_raw_*.jsonl")):
    day = os.path.basename(path)[len("dnse_raw_"):-len(".jsonl")]
    if day < START:
        continue
    with open(path) as fh:
        for ln in fh:
            try:
                rec = json.loads(ln)
            except Exception:
                continue
            acc = str(rec.get("account_no"))
            if acc not in ACCOUNTS:          # <-- §12: LOC ACCOUNT TRUOC MOI PHEP TINH
                continue
            pl = rec.get("payload") or {}
            snaps = []
            if rec.get("kind") == "orders":
                snaps = pl.get("orders") or []
            elif rec.get("kind") == "place_order":
                r = pl.get("resp") or {}
                if r:
                    snaps = [r]
            for s in snaps:
                if str(s.get("accountNo")) != acc:   # <-- §12 lan 2: record long nhau
                    continue
                oid = s.get("id")
                if oid is None:
                    continue
                key = (acc, oid)
                prev = final.get(key)
                # snapshot "moi hon" = fillQuantity lon hon, hoac trang thai cuoi
                if prev is None or (s.get("fillQuantity") or 0) >= (prev.get("fillQuantity") or 0):
                    final[key] = s

buys = []
for (acc, oid), s in final.items():
    if s.get("side") not in ("NB", "B", "buy"):
        continue
    d = s.get("transDate")
    if not d or d < START:
        continue
    buys.append(dict(account=ACCOUNTS[acc], account_no=acc, oid=oid, date=d,
                     ticker=s.get("symbol"), qty=s.get("quantity") or 0,
                     fill_qty=s.get("fillQuantity") or 0,
                     px=s.get("price") or 0, avg_px=s.get("averagePrice") or 0,
                     status=s.get("orderStatus")))

print(f"[1] lenh MUA that (da loc accountNo, tu {START}): {len(buys)} order id doc lap")

# ---------------------------------------------------------------- 3. ADV tu BQ (dung dinh nghia engine)
tks = sorted({b["ticker"] for b in buys if b["ticker"]})
dmin, dmax = min(b["date"] for b in buys), max(b["date"] for b in buys)
in_list = ",".join(f"'{t}'" for t in tks)
sql = (f"SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Volume_3M_P50, t.Close, "
       f"COALESCE(t.Price, t.Close) AS PxAdv FROM tav2_bq.ticker AS t "
       f"WHERE t.ticker IN ({in_list}) AND t.time BETWEEN DATE '{dmin}' AND DATE '{dmax}'")
out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=json",
                      "--max_rows=100000", "--project_id=lithe-record-440915-m9", sql],
                     capture_output=True, text=True)
if out.returncode != 0:
    sys.exit("BQ FAIL:\n" + out.stderr[-2000:])
adv = {}
for r in json.loads(out.stdout):
    v, cl, pa = r["Volume_3M_P50"], r["Close"], r["PxAdv"]
    if v is None or cl is None:
        continue
    adv[(r["ticker"], r["d"])] = (float(v) * float(cl), float(v) * float(pa))
print(f"[2] ADV BQ: {len(adv):,} (ticker,ngay) — co so 'close' va 'price' (LAG_ADV_BASIS)")

# ---------------------------------------------------------------- 4. rap lai
rows = []
for b in buys:
    key = (b["ticker"], b["date"])
    a = adv.get(key)
    if a is None:                       # ngay giao dich chua co trong BQ (sync T-1)
        continue
    adv_close, adv_price = a
    cap = adv_close * 0.20
    order_val = b["qty"] * (b["px"] or 0)
    filled_val = b["fill_qty"] * (b["avg_px"] or b["px"] or 0)
    bk = plan_book.get((b["account"], b["date"], b["ticker"]), (None, None, None))
    rows.append(dict(**b, book=bk[0], play_type=bk[1], adv_close=adv_close, adv_price=adv_price,
                     cap=cap, order_val=order_val, filled_val=filled_val,
                     size_ratio=order_val / cap if cap > 0 else None,
                     fill_rate=filled_val / order_val if order_val > 0 else None,
                     ratio_prereg=filled_val / cap if cap > 0 else None))

import statistics as st
def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else float("nan")

print(f"[3] ghep duoc ADV: {len(rows)}/{len(buys)} order id\n")

# ---------------------------------------------------------------- 5. GOP ve SU KIEN DOC LAP
# skill §4: N = so SU KIEN doc lap, KHONG phai so dong/so order id. Executor cat 1 y dinh mua
# thanh nhieu slice (dat lai gia, du lot le) => moi (account, ngay, ma) MOI la 1 su kien.
ev = defaultdict(lambda: dict(order_val=0.0, filled_val=0.0, qty=0, fill_qty=0,
                              n_slice=0, cap=0.0, book=None, play_type=None, plan_qty=None))
for r in rows:
    k = (r["account"], r["date"], r["ticker"])
    e = ev[k]
    e["order_val"] += r["order_val"]; e["filled_val"] += r["filled_val"]
    e["qty"] += r["qty"]; e["fill_qty"] += r["fill_qty"]; e["n_slice"] += 1
    e["cap"] = r["cap"]; e["book"] = r["book"]; e["play_type"] = r["play_type"]
    e["plan_qty"] = plan_book.get(k, (None, None, None))[2]

events = []
for (acct, d, tk), e in ev.items():
    # size = y dinh mua that (plan qty * gia dat trung binh), KHONG cong don slice tai-dat-gia
    px = (e["order_val"] / e["qty"]) if e["qty"] else 0.0
    intent_qty = e["plan_qty"] if e["plan_qty"] else e["fill_qty"]
    intent_val = intent_qty * px
    events.append(dict(account=acct, date=d, ticker=tk, book=e["book"], play_type=e["play_type"],
                       n_slice=e["n_slice"], intent_qty=intent_qty, fill_qty=e["fill_qty"],
                       intent_val=intent_val, filled_val=e["filled_val"], cap=e["cap"],
                       size_ratio=(intent_val / e["cap"]) if e["cap"] > 0 else None,
                       fill_rate=(e["fill_qty"] / intent_qty) if intent_qty else None,
                       ratio_prereg=(e["filled_val"] / e["cap"]) if e["cap"] > 0 else None))

print("=" * 112)
print("T4 — FILL THAT vs MO HINH FILL ENGINE (tran = 20% ADV/phien), GOP theo SU KIEN (account,ngay,ma)")
print("=" * 112)
hdr = (f"{'date':11s} {'acct':8s} {'tk':5s} {'book':21s} {'slice':>5s} {'y_dinh':>7s} {'fill':>7s} "
       f"{'val_VND':>12s} {'cap=20%ADV':>14s} {'size/cap':>9s} {'fill%':>7s}")
print(hdr); print("-" * len(hdr))
for r in sorted(events, key=lambda x: (x["date"], x["ticker"], x["account"])):
    print(f"{r['date']:11s} {r['account']:8s} {r['ticker'] or '?':5s} {str(r['book']):21s} "
          f"{r['n_slice']:5d} {r['intent_qty']:7,.0f} {r['fill_qty']:7,.0f} {r['intent_val']:12,.0f} "
          f"{r['cap']:14,.0f} {(r['size_ratio'] or 0):9.4f} {(r['fill_rate'] or 0)*100:6.1f}%")

def block(name, sub):
    if not sub:
        print(f"\n### {name}: N=0"); return
    print(f"\n### {name}  (N = {len(sub)} SU KIEN doc lap)")
    print(f"  size_ratio  = y_dinh/(ADV*0.20)  : trung vi {med([r['size_ratio'] for r in sub]):.4f}  "
          f"max {max(r['size_ratio'] for r in sub):.4f}")
    print(f"  fill_rate   = filled/y_dinh      : trung vi {med([r['fill_rate'] for r in sub]):.4f}  "
          f"min {min(r['fill_rate'] for r in sub):.4f}  "
          f"fill >=99%: {sum(1 for r in sub if (r['fill_rate'] or 0) >= 0.99)}/{len(sub)}")
    print(f"  ratio_prereg= filled/(ADV*0.20)  : TRUNG VI {med([r['ratio_prereg'] for r in sub]):.4f}"
          f"   <-- chi so DANG KY TRUOC (PASS >=1.0 / FAIL <0.5)")
    full = [r for r in sub if (r['fill_rate'] or 0) >= 0.99]
    if full:
        m = max(r['size_ratio'] for r in full)
        print(f"  => CAN DUOI xac nhan duoc: su kien fill >=99% LON NHAT = {m:.4f} lan tran engine "
              f"(= {m*0.20*100:.3f}% ADV/phien)")

block("A. So LAG — pham vi DANG KY TRUOC", [r for r in events if r["book"] == "LAG"])
block("B. MOI lenh mua live (engine ap CUNG tran 20%ADV cho moi so) — MO RONG, khong dang ky truoc",
      events)
block("C. CAPIT (size lon nhat trong ky)", [r for r in events if r["book"] == "CAPIT"])
block("D. custom30V parking", [r for r in events if r["book"] == "custom30V_parking"])
block("E. DISCRETIONARY (TV1 — ma kem thanh khoan nhat)",
      [r for r in events if r["book"] == "DISCRETIONARY_SPECIAL"])

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "t4_fills.json"), "w") as fh:
    json.dump(dict(slices=rows, events=events), fh, ensure_ascii=False, indent=1)
print("\n-> t4_fills.json")
