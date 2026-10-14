#!/usr/bin/env python3
"""Việc 2 — NGUYÊN MẪU chuỗi ZaloPay "phần bot quản lý" (chuỗi b). CHỈ ĐỌC dữ liệu thật; mọi thứ
ghi vào --work (mặc định /tmp/fund_step4_zp) và thư mục này.

    python3 zalopay_bot_series.py [--asof 2026-10-13] [--settle-time 10:00|15:30]

ĐỊNH NGHĨA (một chỗ: `outside_value` + `sleeve_flows`)
  ngoài_bot_t = Σ_{mã ∈ NGOÀI} KL_t × Price_t  +  cổ_tức_phải_thu_GỘP của mã NGOÀI đang nằm trong
                tiền của dòng nav_history ngày t (từ ngày GDKHQ tới trước ngày tiền về)
  NAV_b_t     = NAV_a_t − ngoài_bot_t                     (NAV_a = cột `nav` của nav_history)
  Tiền mặt, Trứng vàng, nợ: thuộc TRỌN chuỗi b (bot là bên duy nhất dùng tiền; DGC không gắn nợ).
  Dòng tiền VÀO chuỗi b (nội bộ với tài khoản, NGOÀI với chuỗi b):
     · cổ tức mã NGOÀI về tiền: +số RÒNG (gộp × 0,95) tại ngày tiền về; thuế 5% là chi phí của
       phần ngoài bot.
     · bán mã NGOÀI: +tiền bán ròng tại ngày khớp (chưa xảy ra — DGC đang bị hạn chế).
     · mua thêm mã NGOÀI bằng tiền của bot: −tiền mua (chưa xảy ra).
  Tỉ suất chuỗi b = `nav_unit_ledger.build_ledger` (ĐÚNG công thức sổ đơn vị bước 1, import chỉ
  đọc) chạy trên bản sao trong --work: nav_history_ZaloPayBot.csv + inception + cash_flows.

ĐỐI SOÁT
  (1) đẳng thức  NAV_a = NAV_b + ngoài_bot  mọi ngày (đúng theo cách dựng — kiểm số học).
  (2) dựng NGƯỢC TỪ DƯỚI LÊN, độc lập với cột `nav`: Σ_{mã ∉ NGOÀI} KL×Price(BQ) + tiền + Trứng
      vàng + offbook − nợ − phải_thu_ngoài  so với NAV_b. Lệch = chênh giữa giá nav_history đã dùng
      (DNSE cuối ngày) và BQ Price ⇒ đo được sai số định giá phần ngoài bot.
  (3) lãi/lỗ cộng được: lãi_a = lãi_b + lãi_ngoài từng ngày và cả kỳ.
"""
import argparse
import csv
import datetime as dt
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
import nav_unit_ledger as NUL  # noqa: E402  (chỉ đọc: dùng build_account_ledger)

ACC_NO = "0001743768"
LOGS = os.path.join(WC, "data", "execution_logs")
PX_CSV = os.path.join(HERE, "px_zalopay_20260625_20261013.csv")
TAX = 0.05
OUTSIDE_MAIN = ("DGC",)                 # chuỗi b chính
OUTSIDE_PURE = ("DGC", "TV1", "DRI")    # biến thể "chỉ V2.4" — ước lượng, xem README
# Biến thể "legacy nghiêm ngặt": 6 mã legacy còn lại cũng NGOÀI bot cho tới khi bán; phần còn lại
# của lô legacy = min chạy của KL (mua thêm sau đó là của bot). Ước lượng — xem README.
LEGACY_OTHERS = ("MSH", "TCM", "TLG", "VHC", "VIB", "VPB")
# Cổ tức tiền mặt của mã NGOÀI: tav2_bq.corporate_action (DGC DIV ex 2026-09-14, 3.000+5.000 đ/cp,
# payout 2026-09-25) ĐỐI CHIẾU dnse_raw cashDividendReceiving ZaloPay: 0 → 80.000.000 (11/09 19:07),
# 81.900.000 → 1.900.000 giữa 25/09 04:51 và 19:07.
OUTSIDE_DIVS = [{"ticker": "DGC", "ex_date": "2026-09-14", "per_share": 8000.0,
                 "settle_date": "2026-09-25"}]


def D(s):
    return dt.date.fromisoformat(s)


class Px(dict):
    """Giá THÔ theo (ngày, mã); ngày không có phiên (vd dòng nav_history 2026-08-31, nghỉ lễ) ⇒ lấy
    giá phiên gần nhất TRƯỚC đó, tối đa 7 ngày lịch — đúng cách nav_history định giá ngày đó."""

    def __missing__(self, key):
        d, s = key
        for k in range(1, 8):
            p = dict.get(self, ((D(d) - dt.timedelta(days=k)).isoformat(), s))
            if p is not None:
                return p
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def load_px():
    px = Px()
    for r in csv.DictReader(open(PX_CSV)):
        px[(r["time"], r["ticker"])] = float(r["Price"])
    return px


def positions_near(date, balance_ts):
    """Bản ghi vị thế của ZaloPay gần `balance_ts` nhất (§12: lọc account ở dòng đầu)."""
    best, gap = None, None
    t0 = dt.datetime.fromisoformat(balance_ts)
    for day in sorted({date, balance_ts[:10]}):
        p = os.path.join(LOGS, f"dnse_raw_{day}.jsonl")
        if not os.path.exists(p):
            continue
        for line in open(p):
            rec = json.loads(line)
            if str(rec.get("account_no")) != ACC_NO:
                continue
            if rec.get("kind") != "positions":
                continue
            g = abs((dt.datetime.fromisoformat(rec["ts"]) - t0).total_seconds())
            if gap is None or g < gap:
                best, gap = rec, g
    if best is None:
        return None, None
    qty = {}
    for p in best["payload"]["positions"]:
        # MỘT mã có thể nằm ở NHIỀU lô (khác loanPackageId) ⇒ phải CỘNG, không ghi đè.
        if p.get("openQuantity"):
            qty[p["symbol"]] = qty.get(p["symbol"], 0) + p["openQuantity"]
    return qty, gap


def outside_value(date, qty, px, outside):
    """(giá trị thị trường mã NGOÀI, phải thu cổ tức gộp của mã NGOÀI đang nằm trong NAV ngày đó)."""
    mv = sum(q * px[(date, s)] for s, q in qty.items() if s in outside)
    recv = 0.0
    for ev in OUTSIDE_DIVS:
        if ev["ticker"] in outside and ev["ex_date"] <= date < ev["settle_date"]:
            recv += ev["per_share"] * qty.get(ev["ticker"], 0)
    return mv, recv


def build(asof, settle_time, outside, work, tag, legacy_strict=False):
    px = load_px()
    rows = [r for r in csv.DictReader(open(os.path.join(LOGS, "nav_history_ZaloPay.csv")))
            if r["date"] <= asof]
    seed = json.load(open(os.path.join(WC, "data", "account_seed_capital.json")))["ZaloPay"]
    inc = json.load(open(os.path.join(WC, "data", "account_inception.json")))["ZaloPay"]
    seed_qty = {k: v["qty"] for k, v in seed["legacy_positions"].items()}
    rem = {s: seed_qty.get(s, 0) for s in LEGACY_OTHERS} if legacy_strict else {}

    def out_qty(qty):
        oq = {s: qty[s] for s in outside if qty.get(s)}
        for s in rem:
            rem[s] = min(rem[s], qty.get(s, 0))
            if rem[s]:
                oq[s] = rem[s]
        return oq

    prev_qty = out_qty(seed_qty)
    out0 = sum(q * px[(inc["inception_date"], s)] for s, q in prev_qty.items())
    table = []
    flows = []
    for r in rows:
        d = r["date"]
        qty, gap = positions_near(d, r["balance_ts"])
        if qty is None:
            raise SystemExit(f"{d}: không có bản ghi vị thế ZaloPay quanh {r['balance_ts']}")
        oq = out_qty(qty)
        mv, recv = outside_value(d, oq, px, set(oq))
        f = lambda k: float(r[k] or 0)  # noqa: E731
        nav_a = float(r["nav"])
        nav_b = nav_a - mv - recv
        in_mv = sum((q - oq.get(s, 0)) * px.get((d, s), float("nan")) for s, q in qty.items())
        bottom_up = in_mv + f("cash") + f("egg_assets") + f("offbook_assets") - f("margin_debt") - recv
        # dòng tiền vào chuỗi b ngày d
        flow, why = 0.0, []
        for ev in OUTSIDE_DIVS:
            if ev["ticker"] in outside and ev["settle_date"] == d:
                net = ev["per_share"] * prev_qty.get(ev["ticker"], 0) * (1 - TAX)
                flow += net
                why.append(f"cổ tức {ev['ticker']} ròng")
                flows.append({"date": d, "time_ict": settle_time, "amount_vnd": net, "kind": "deposit",
                              "evidence": f"NGUYÊN MẪU: cổ tức {ev['ticker']} {ev['per_share']:.0f}đ/cp gộp, "
                                          f"trừ thuế 5%; dnse_raw cashDividendReceiving giảm 80tr ngày {d}"})
        for s in sorted(set(oq) | set(prev_qty)):
            dq = oq.get(s, 0) - prev_qty.get(s, 0)
            if dq and s != "DGC":
                # biến thể "chỉ V2.4": bot dùng tiền mua mã discretionary ⇒ tiền RA khỏi chuỗi b.
                # Giá khớp thật chưa đọc — xấp xỉ bằng giá đóng cửa (README nêu giới hạn).
                amt = -dq * px[(d, s)]
                flow += amt
                why.append(f"{s}{dq:+d}")
                flows.append({"date": d, "time_ict": "10:00", "amount_vnd": amt,
                              "kind": "deposit" if amt > 0 else "withdraw",
                              "evidence": f"NGUYÊN MẪU: {s} {dq:+d} cp × giá đóng cửa (xấp xỉ)"})
            elif dq:
                raise SystemExit(f"{d}: KL DGC đổi {dq:+d} — nguyên mẫu chưa xử lý bán/mua DGC, cần người khai")
        table.append({"date": d, "nav_a": nav_a, "outside_mv": mv, "outside_recv": recv,
                      "nav_b": nav_b, "flow_b": flow, "flow_note": "; ".join(why),
                      "bottom_up_b": bottom_up, "recon_diff": nav_b - bottom_up, "pos_gap_s": gap,
                      "balance_ts": r["balance_ts"], "est": r.get("nav_is_estimate") or ""})
        prev_qty = oq
    # bản sao cho build_ledger
    acct = f"ZaloPayBot{tag}"
    os.makedirs(work, exist_ok=True)
    with open(os.path.join(work, f"nav_history_{acct}.csv"), "w", newline="") as fo:
        w = csv.writer(fo)
        w.writerow(["date", "nav", "balance_ts", "nav_is_estimate"])
        for t in table:
            w.writerow([t["date"], repr(t["nav_b"]), t["balance_ts"], t["est"]])
    ip = os.path.join(work, f"account_inception_{acct}.json")
    json.dump({acct: {"account_no": ACC_NO, "inception_date": inc["inception_date"],
                      "starting_capital": inc["starting_capital"] - out0}}, open(ip, "w"))
    fp = os.path.join(work, f"account_cash_flows_{acct}.json")
    json.dump({"_doc": "nguyên mẫu", acct: flows}, open(fp, "w"), ensure_ascii=False, indent=1)
    ledger, info = NUL.build_account_ledger(acct, nav_dir=work, inception_path=ip, flows_path=fp)
    return table, ledger, info, out0, inc


def ratio(ledger, a, b):
    """Tỉ suất kỳ (a, b]: tỉ số giá đơn vị; a = ngày mốc (dòng cuối có ngày <= a)."""
    pa = [x for x in ledger if x["date"] <= D(a)][-1]
    pb = [x for x in ledger if x["date"] <= D(b)][-1]
    return pb["unit_price"] / pa["unit_price"] - 1, pa["date"], pb["date"]


def real_ledger(account, asof):
    work = "/tmp/fund_step4_zp/real"
    os.makedirs(work, exist_ok=True)
    src = os.path.join(LOGS, f"nav_history_{account}.csv")
    rows = [r for r in csv.DictReader(open(src)) if r["date"] <= asof]
    with open(os.path.join(work, f"nav_history_{account}.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for fn in ("account_inception.json", "account_cash_flows.json"):
        shutil.copy(os.path.join(WC, "data", fn), os.path.join(work, fn))
    return NUL.build_account_ledger(account, nav_dir=work,
                                    inception_path=os.path.join(work, "account_inception.json"),
                                    flows_path=os.path.join(work, "account_cash_flows.json"))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default="2026-10-13")
    ap.add_argument("--settle-time", default="10:00",
                    help="giờ ICT tiền cổ tức DGC về ngày 25/09 (KHÔNG đo được: giữa 04:51 và 19:07). "
                         "10:00 ⇒ luật suy 'bod'; 15:30 ⇒ 'eod'")
    ap.add_argument("--work", default="/tmp/fund_step4_zp")
    a = ap.parse_args()
    pc = lambda v: f"{100 * v:+.3f}%"  # noqa: E731

    table, led_b, info, out0, inc = build(a.asof, a.settle_time, OUTSIDE_MAIN, a.work, "")
    _, led_b_alt, _, _, _ = build(a.asof, "15:30" if a.settle_time < "14:45" else "10:00",
                                  OUTSIDE_MAIN, a.work, "AltTiming")
    tbl2, led_b2, _, out0_2, _ = build(a.asof, a.settle_time, OUTSIDE_PURE, a.work, "PureV24")
    tbl3, led_b3, _, out0_3, _ = build(a.asof, a.settle_time, OUTSIDE_MAIN, a.work, "LegacyStrict",
                                       legacy_strict=True)
    print(f"[biến thể legacy nghiêm ngặt] mốc ngoài bot {out0_3:,.0f}; dòng vào chuỗi:",
          [(t["date"], round(t["flow_b"]), t["flow_note"]) for t in tbl3 if t["flow_b"]])
    led_a = real_ledger("ZaloPay", a.asof)
    led_s = real_ledger("SpaceX", a.asof)

    with open(os.path.join(HERE, "zalopay_bot_series.csv"), "w", newline="") as fo:
        cols = ["date", "nav_a", "outside_mv", "outside_recv", "nav_b", "flow_b", "flow_note",
                "unit_price_a", "unit_price_b", "bottom_up_b", "recon_diff", "pos_gap_s", "est"]
        w = csv.DictWriter(fo, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        ua = {x["date"]: x["unit_price"] for x in led_a}
        ub = {x["date"]: x["unit_price"] for x in led_b}
        for t in table:
            t["unit_price_a"] = round(ua[D(t["date"])], 4)
            t["unit_price_b"] = round(ub[D(t["date"])], 4)
            w.writerow(t)

    print(f"Mốc {inc['inception_date']}: NAV_a {inc['starting_capital']:,.0f} = NAV_b "
          f"{inc['starting_capital'] - out0:,.0f} + ngoài bot {out0:,.0f} "
          f"({100 * out0 / inc['starting_capital']:.1f}% NAV)")
    last = table[-1]
    print(f"Cuối {last['date']}: NAV_a {last['nav_a']:,.0f} = NAV_b {last['nav_b']:,.0f} + ngoài bot "
          f"{last['outside_mv'] + last['outside_recv']:,.0f} "
          f"({100 * (last['outside_mv'] + last['outside_recv']) / last['nav_a']:.1f}% NAV)")
    print("Dòng tiền vào chuỗi b:", [(t["date"], round(t["flow_b"]), t["flow_note"]) for t in table if t["flow_b"]],
          "| treo:", info["pending"], "| loại:", info["dropped"])

    print("\nBẢNG 2c — tỉ suất gia quyền thời gian (tỉ số giá đơn vị), tới", a.asof)
    print(f"{'kỳ':28s} {'ZaloPay (a)':>12s} {'ZaloPay (b)':>12s} {'(b) eod/bod':>12s} {'(b) chỉ V2.4*':>14s} {'(b) legacy*':>12s} {'SpaceX':>10s}")
    for name, a0 in [("từ đầu ZaloPay (06/07)", inc["inception_date"]), ("MTD (30/09)", "2026-09-30"),
                     ("WTD (09/10)", "2026-10-09"), ("tháng 7 (06/07→31/07)", None),
                     ("tháng 8", None), ("tháng 9", None)]:
        rng = {"tháng 7 (06/07→31/07)": ("2026-07-06", "2026-07-31"), "tháng 8": ("2026-07-31", "2026-08-31"),
               "tháng 9": ("2026-08-31", "2026-09-30")}.get(name, (a0, a.asof))
        vals = [ratio(L, *rng)[0] for L in (led_a, led_b, led_b_alt, led_b2, led_b3, led_s)]
        print(f"{name:28s} " + " ".join(f"{pc(v):>12s}" for v in vals))
    print("SpaceX 'từ 06/07' = tỉ số giá đơn vị SpaceX giữa dòng 06/07 và", a.asof,
          "(cùng cửa sổ với ZaloPay, KHÔNG phải số 'từ đầu' 01/07 của SpaceX:",
          pc(ratio(led_s, "2026-07-01", a.asof)[0]) + ")")

    # ĐỐI SOÁT
    ident = max(abs(t["nav_a"] - t["nav_b"] - t["outside_mv"] - t["outside_recv"]) for t in table)
    worst = max(table, key=lambda t: abs(t["recon_diff"]))
    n_big = sum(1 for t in table if abs(t["recon_diff"]) > 0.0005 * t["nav_a"])
    print(f"\nĐỐI SOÁT (1) đẳng thức a = b + ngoài: lệch lớn nhất {ident:.6f} đ trên {len(table)} ngày")
    print(f"ĐỐI SOÁT (2) dựng từ dưới lên vs NAV_b: lệch lớn nhất {worst['recon_diff']:,.0f} đ "
          f"({100 * worst['recon_diff'] / worst['nav_b']:+.3f}% NAV_b) ngày {worst['date']}; "
          f"số ngày |lệch| > 0,05% NAV: {n_big}/{len(table)}; ngày lệch = 0: "
          f"{sum(1 for t in table if abs(t['recon_diff']) < 1)}")
    for t in sorted(table, key=lambda t: -abs(t["recon_diff"]))[:8]:
        print(f"     {t['date']}  lệch {t['recon_diff']:>13,.0f}  gap vị thế {t['pos_gap_s']:.0f}s  est={t['est']}")
    # (3) lãi/lỗ cộng được
    pa = last["nav_a"] - inc["starting_capital"]
    fl = sum(t["flow_b"] for t in table)
    pb = last["nav_b"] - (inc["starting_capital"] - out0) - fl
    po = (last["outside_mv"] + last["outside_recv"]) - out0 + fl
    print(f"ĐỐI SOÁT (3) lãi/lỗ VND cả kỳ: a {pa:,.0f} = b {pb:,.0f} + ngoài bot {po:,.0f}  (lệch {pa - pb - po:.4f})")
    json.dump({"asof": a.asof, "settle_time": a.settle_time, "base_b": inc["starting_capital"] - out0,
               "pnl": {"a": pa, "b": pb, "outside": po}, "flows_b": fl,
               "identity_max_abs": ident, "recon_max": worst["recon_diff"], "recon_max_date": worst["date"]},
              open(os.path.join(HERE, "zalopay_bot_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
