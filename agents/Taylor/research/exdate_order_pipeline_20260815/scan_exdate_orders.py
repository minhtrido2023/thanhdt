#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tái lập mọi số trong README.md — job Taylor_20260815_050425.

Đo 4 thứ, mỗi thứ từ ARTIFACT thật, không từ giả định:
  [1] Lệnh THẬT từng đặt đúng ngày GDKHQ (dnse_raw_*.jsonl × tav2_bq.corporate_action)
  [2] Độ lớn dịch chuyển giá tham chiếu từng sự kiện (công thức sở giao dịch)
  [3] Plan (kể cả paper) có ref_price ở SAI hệ quy chiếu
  [4] Cú lật hệ quy chiếu của DNSE — thời điểm + bằng chứng KHÔNG NGUYÊN TỬ

R&D THUẦN — chỉ đọc, không ghi vào bất kỳ đường production nào.

Chạy:  python3 mike/agents/Taylor/research/exdate_order_pipeline_20260815/scan_exdate_orders.py
       (thêm --refresh-events để hỏi lại BigQuery; mặc định dùng CSV đã chụp trong data/)
"""
import argparse
import collections
import csv
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
DATA = os.path.join(HERE, "data")
sys.path.insert(0, WC_ROOT)

# Nhãn account: bản ghi place_order CŨ không có `account_label` (389/745 dòng) — thiếu bảng này
# thì 52% lệnh thật rơi khỏi phép quét mà KHÔNG báo lỗi. §12 coding_guidelines.
ACCT = {"0002023347": "SpaceX", "0001743768": "ZaloPay"}

# Giá phát hành quyền mua — KHÔNG có trong `corporate_action` (bảng chỉ có `exercise_ratio`).
# Số này lấy từ công bố của MBB (10.000đ/cp), đã đối soát khớp tuyệt đối với giá tham chiếu
# 20.200 mà user chụp từ app DNSE ngày 08-11. Mã nào không có ở đây ⇒ bỏ qua vế quyền mua và
# NÓI RÕ ra, không im lặng coi như 0.
RIGHTS_ISSUE_PRICE = {("MBB", "2026-08-11"): 10_000}


def load_events(refresh=False):
    """25 sự kiện làm-đổi-giá của các mã ta từng đặt lệnh thật."""
    path = os.path.join(DATA, "corp_events.csv")
    if refresh or not os.path.exists(path):
        tks = sorted({o["ticker"] for o in load_orders() if o["ticker"]})
        inlist = ",".join(f'"{t}"' for t in tks)
        sql = f"""
            SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date, event_status,
                   value_per_share, exercise_ratio, issue_method_name_vi
            FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
            WHERE ticker IN ({inlist})
              AND exright_date BETWEEN DATE "2026-06-01" AND DATE "2026-09-30"
              AND event_status != "not_executed"
            ORDER BY exright_date, ticker"""
        # `!= "not_executed"`, KHÔNG PHẢI `== "executed"`: vendor chỉ đổi announced→executed trong
        # lần reload ~22:2x ICT CỦA CHÍNH ngày sự kiện ⇒ lọc "executed" làm mọi sự kiện TƯƠNG LAI
        # biến mất trong im lặng (bug thật, corp_action_daily.py:422-437).
        out = subprocess.run(["bq", "query", "--use_legacy_sql=false", "--format=csv",
                              "--max_rows=500", "--project_id=lithe-record-440915-m9", sql],
                             capture_output=True, text=True, check=True).stdout
        os.makedirs(DATA, exist_ok=True)
        open(path, "w").write(out)
    from corp_action_lib import is_price_adjusting
    rows = list(csv.DictReader(open(path)))
    return rows, [e for e in rows if is_price_adjusting(e)]


def load_orders():
    """Mọi lệnh THẬT đã gửi sang sở, từ log thô của broker."""
    out = []
    for f in sorted(glob.glob(os.path.join(WC_ROOT, "data/execution_logs/dnse_raw_*.jsonl"))):
        day = os.path.basename(f)[9:19]
        for line in open(f):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("kind") != "place_order":
                continue
            p = r.get("payload") or {}
            req, resp = p.get("req") or [], p.get("resp") or {}
            an = str(r.get("account_no") or resp.get("accountNo") or "")
            out.append(dict(
                day=day, ts=r.get("ts"), acct=r.get("account_label") or ACCT.get(an) or f"?{an}",
                ticker=(req[0] if req else resp.get("symbol")),
                qty=(req[1] if len(req) > 1 else resp.get("quantity")),
                side=(req[2] if len(req) > 2 else resp.get("side")),
                price=(req[3] if len(req) > 3 else resp.get("price"))))
    return out


def ref_after(prev_px, evs):
    """Giá tham chiếu phiên GDKHQ theo công thức sở giao dịch, gộp MỌI sự kiện cùng ngày.

        ref = (P_cum − Σ tiền_mặt + Σ r_i × giá_phát_hành_i) / (1 + Σ r_i)

    Đối soát: khớp TUYỆT ĐỐI 2/2 ca quan sát được (MBB 08-11 → 20.200 = ảnh chụp app DNSE của
    user; SSI 08-17 → 19.600 = q.ref đo ở job Taylor_20260815_034407). Dùng để ĐỐI SOÁT `q.ref`,
    KHÔNG dùng thay `q.ref` — xem README §D5.
    """
    cash, ratio, paid, unknown = 0.0, 0.0, 0.0, []
    for e in evs:
        r = float(e["exercise_ratio"] or 0)
        if e["event_code"] == "DIV":
            cash += float(e["value_per_share"] or 0)
            continue
        ratio += r
        if "Quyền mua" in (e["issue_method_name_vi"] or ""):
            px = RIGHTS_ISSUE_PRICE.get((e["ticker"], e["exright_date"]))
            if px is None:
                unknown.append(e["ticker"])
            else:
                paid += r * px
    return (prev_px - cash + paid) / (1 + ratio), unknown


def prev_price(df, tk, ex):
    import pandas as pd
    s = df[(df.ticker == tk) & (df.time < pd.Timestamp(ex))].sort_values("time")
    return (float(s.iloc[-1]["Price"]), s.iloc[-1]["time"].date()) if len(s) else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-events", action="store_true")
    args = ap.parse_args()

    orders = load_orders()
    all_ev, padj = load_events(args.refresh_events)
    print(f"lệnh THẬT: {len(orders)} ({dict(collections.Counter(o['acct'] for o in orders))})")
    print(f"sự kiện: {len(all_ev)} tổng, {len(padj)} làm-đổi-giá\n")

    # ── [1] lệnh thật đặt đúng ngày GDKHQ
    idx = collections.defaultdict(list)
    for e in padj:
        idx[(e["ticker"], e["exright_date"])].append(e)
    hits = [(o, idx[(o["ticker"], o["day"])]) for o in orders if (o["ticker"], o["day"]) in idx]
    print(f"[1] LỆNH THẬT đặt ĐÚNG ngày GDKHQ: {len(hits)}")
    for o, es in hits:
        print(f"    {o['ts']}  {o['acct']:<8} {o['side']:<4} {o['ticker']:<5} "
              f"{o['qty']:>6}cp @ {o['price']:>8,}  ← "
              + "; ".join(f"{e['event_code']}/{e['issue_method_name_vi'] or 'CASH'}"
                          f"·{e['exercise_ratio']}" for e in es))

    # ── [2] độ lớn
    import pandas as pd
    df = pd.read_parquet(os.path.join(WC_ROOT, "data/bq_cache/ticker/2026.parquet"),
                         columns=["ticker", "time", "Price", "Close"])
    df["time"] = pd.to_datetime(df["time"])
    byd = collections.defaultdict(list)
    for e in padj:
        byd[(e["ticker"], e["exright_date"])].append(e)
    print(f"\n[2] ĐỘ LỚN dịch chuyển giá tham chiếu ({len(byd)} ngày-mã)")
    shifts, unknown_all = [], []
    for (tk, ex), es in sorted(byd.items(), key=lambda kv: kv[0][1]):
        prev, prevd = prev_price(df, tk, ex)
        if prev is None:
            print(f"    {ex} {tk:<5} (không có giá trong cache)")
            continue
        adj, unk = ref_after(prev, es)
        unknown_all += unk
        sh = (adj / prev - 1) * 100
        shifts.append(abs(sh))
        what = " + ".join((e["issue_method_name_vi"] or f"tiền {e['value_per_share']}") for e in es)
        print(f"    {ex} {tk:<5} {what[:44]:<44} {prev:>9,.0f} → {adj:>9,.0f}  {sh:>6.1f}%")
    if unknown_all:
        print(f"    ⚠️ thiếu giá phát hành quyền mua cho {sorted(set(unknown_all))} — vế đó bỏ qua")
    shifts.sort()
    med = shifts[len(shifts) // 2]
    print(f"    n={len(shifts)}  median |dịch|={med:.2f}%  max={max(shifts):.2f}%  "
          f">5%: {sum(x > 5 for x in shifts)}  >10%: {sum(x > 10 for x in shifts)}")

    # ── [3] plan có ref_price sai hệ quy chiếu
    print("\n[3] PLAN có ref_price ở SAI hệ quy chiếu (mọi account, kể cả paper)")
    n_bad = 0
    for (tk, ex), es in sorted(byd.items(), key=lambda kv: kv[0][1]):
        prev, _ = prev_price(df, tk, ex)
        if prev is None:
            continue
        adj, _ = ref_after(prev, es)
        for f in sorted(glob.glob(os.path.join(WC_ROOT, f"data/trade_plans/*_{ex}.json"))):
            try:
                pl = json.load(open(f))
            except ValueError:
                continue
            for o in pl.get("orders") or []:
                if o.get("ticker") != tk or not o.get("ref_price"):
                    continue
                px, dev = float(o["ref_price"]), (float(o["ref_price"]) / adj - 1) * 100
                verdict = "OK (hệ MỚI)" if abs(dev) <= 3 else f"SAI HỆ  {dev:+.1f}%"
                n_bad += abs(dev) > 3
                print(f"    {ex} {os.path.basename(f):<34} {o['side']:<4} {tk:<5} "
                      f"ref={px:>9,.0f} (đúng {adj:>9,.0f})  {verdict}")
    print(f"    → {n_bad} lệnh ở sai hệ quy chiếu")

    # ── [4] cú lật của DNSE
    print("\n[4] CÚ LẬT hệ quy chiếu của DNSE — và bằng chứng KHÔNG NGUYÊN TỬ")
    for tk, days in (("VHM", ("2026-08-05", "2026-08-06")), ("MBB", ("2026-08-10", "2026-08-11")),
                     ("BID", ("2026-08-14",))):
        print(f"    ── {tk}")
        for day in days:
            f = os.path.join(WC_ROOT, f"data/execution_logs/dnse_raw_{day}.jsonl")
            if not os.path.exists(f):
                continue
            prev = {}
            for line in open(f):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if r.get("kind") != "positions":
                    continue
                pay = r.get("payload") or {}
                lots = [p for p in ((pay.get("positions") if isinstance(pay, dict) else pay) or [])
                        if isinstance(p, dict) and p.get("symbol") == tk]
                if not lots:
                    continue
                an = str(r.get("account_no") or "")
                sig = tuple(sorted((p.get("marketPrice"), p.get("openQuantity")) for p in lots))
                if prev.get(an) == sig:
                    continue
                prev[an] = sig
                mixed = len({p.get("marketPrice") for p in lots}) > 1
                tag = "  🔴 TRỘN HỆ QUY CHIẾU (nhiều marketPrice cùng lúc)" if mixed else ""
                print(f"       {r.get('ts')} {an[-4:]} "
                      + " | ".join(f"{p.get('openQuantity')}cp@{p.get('marketPrice'):,}"
                                   f" pkg={p.get('loanPackageId')}" for p in lots) + tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
