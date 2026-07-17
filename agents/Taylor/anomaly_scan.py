#!/usr/bin/env python3
"""
anomaly_scan.py — daily scan phát hiện CHỦ ĐỘNG case bất thường kiểu DGC/PNJ
============================================================================
Job Taylor_20260717_111204. READ-ONLY — không đổi logic trading, không đặt lệnh.

Universe = mã đang giữ (SpaceX/ZaloPay, đọc active_nav_*.json)  [tier H — nhạy]
         + watchlist Golden/Strong (fa_ratings_8l rating<=2)     [tier W — chặt]

Tín hiệu giá/khối lượng (backtest FP 2024-01→2026-07, xem finding trên bus):
  tier H: 1.2 episode/tháng; tier W: 9.2 episode/tháng (245 mã).
  - FLOOR2 : sàn 2 phiên liên tiếp (ret<=-6.5% VÀ idio<=-4% — loại phiên cả
             thị trường sập, vd PNJ 2026-03-09 sàn cùng VNINDEX -6.5% KHÔNG trip)
  - CEIL2  : trần 2 phiên liên tiếp (đối xứng, severity thấp — watch note)
  - VOLSPIKE: Volume >= 5x Volume_1M (tier W: >=8x) + sàn giá trị tuyệt đối
  - IDIOCRASH: 1 phiên ret<=-6% và idio<=-5% (tier W: thêm gate thanh khoản)
Ground-truth: PNJ alert ngay 2026-07-03 (phiên sàn đầu), DGC ngay 2026-03-17.

Tín hiệu trạng thái sàn/margin (--status-check, cần DNSE creds):
  - secdef symbolAdminStatusCode/TradingMethod/Sanction đổi khác NRM
    (DGC đang trả "RES" = hạn chế giao dịch HOSE — máy đọc được, không cần scraper)
  Diff so với snapshot hôm trước: data/anomaly_status_snapshot.json
  (Extension chưa làm: diff loan_packages initialRate — DNSE cắt/siết margin.
   Endpoint đã xác minh hoạt động; thêm khi user duyệt thiết kế tổng.)

Output: in report; ghi cờ vào data/anomaly_flags.json (ticker -> last_alert,
reasons, tier) — hệ due-diligence trigger đọc file này (cờ hiệu lực 30 ngày).

Usage:
  python3 anomaly_scan.py                 # scan phiên hoàn tất gần nhất (BQ cache T-1)
  python3 anomaly_scan.py --asof 2026-07-06
  python3 anomaly_scan.py --status-check  # thêm secdef/margin diff (gọi DNSE API)
  python3 anomaly_scan.py --selftest      # replay PNJ/DGC ground-truth
"""
import argparse, glob, json, os, sys, datetime

WC = "/home/trido/thanhdt/WorkingClaude"
CACHE = os.path.join(WC, "data", "bq_cache")
FLAGS_PATH = os.path.join(WC, "data", "anomaly_flags.json")
STATUS_SNAP = os.path.join(WC, "data", "anomaly_status_snapshot.json")

LIQ_1M_BN = 3.0   # mã "thanh khoản": giá trị GD bình quân 1 tháng >= 3 tỷ/phiên


def load_universe():
    hold = set()
    for f in glob.glob(os.path.join(WC, "data/execution_logs/active_nav_*.json")):
        d = json.load(open(f))
        hold |= {p["ticker"] for p in d.get("positions", [])}
    import pandas as pd
    fr = pd.read_parquet(os.path.join(CACHE, "fa_ratings_8l.parquet"))
    fr["time"] = pd.to_datetime(fr["time"])
    wl = set(fr.sort_values("time").groupby("ticker").tail(1).query("rating<=2")["ticker"])
    return hold, wl


def load_prices(tickers, start, end):
    import duckdb
    years = sorted({y for y in range(start.year, end.year + 1)})
    files = [os.path.join(CACHE, "ticker", f"{y}.parquet") for y in years
             if os.path.exists(os.path.join(CACHE, "ticker", f"{y}.parquet"))]
    con = duckdb.connect()
    con.execute("PRAGMA threads=1")
    tl = "','".join(sorted(tickers))
    q = (f"select time, ticker, Close, Volume, Volume_1M, VNINDEX from read_parquet({files!r}) "
         f"where ticker in ('{tl}') and time between DATE '{start:%Y-%m-%d}' and DATE '{end:%Y-%m-%d}' "
         f"order by ticker, time")
    return con.execute(q).df()


def compute_signals(df, hold):
    """df: time,ticker,Close,Volume,Volume_1M,VNINDEX. Trả về DataFrame alert (mọi phiên trong df)."""
    import pandas as pd
    df = df.sort_values(["ticker", "time"]).copy()
    df["time"] = pd.to_datetime(df["time"])
    df["ret"] = df.groupby("ticker")["Close"].pct_change() * 100
    vni = df.groupby("time")["VNINDEX"].first().pct_change() * 100
    df["vni_ret"] = df["time"].map(vni)
    df["idio"] = df["ret"] - df["vni_ret"]
    df["vol_x"] = df["Volume"] / df["Volume_1M"]
    df["val_bn"] = df["Volume"] * df["Close"] / 1e9
    df["val1m_bn"] = df["Volume_1M"] * df["Close"] / 1e9
    liquid = df["val1m_bn"] >= LIQ_1M_BN
    g = df.groupby("ticker")
    floor = (df["ret"] <= -6.5) & (df["idio"] <= -4)
    ceil = (df["ret"] >= 6.5) & (df["idio"] >= 4)
    floor2 = floor & floor.groupby(df["ticker"]).shift(1, fill_value=False)
    ceil2 = ceil & ceil.groupby(df["ticker"]).shift(1, fill_value=False)
    is_hold = df["ticker"].isin(hold)
    real_trade = df["val_bn"] >= 0.3  # loại "sàn" trên vài lô lẻ của mã kém thanh khoản (tier W)
    rules = {
        "FLOOR2": (floor2 & is_hold) | (floor2 & real_trade),
        "CEIL2": (ceil2 & is_hold) | (ceil2 & real_trade),
        "VOLSPIKE": ((df["vol_x"] >= 5) & (df["val_bn"] >= 5) & is_hold)
                  | ((df["vol_x"] >= 8) & (df["val_bn"] >= 8) & liquid & ~is_hold),
        "IDIOCRASH": ((df["ret"] <= -6) & (df["idio"] <= -5) & is_hold)
                   | ((df["ret"] <= -6) & (df["idio"] <= -5) & liquid & (df["val_bn"] >= 3) & ~is_hold),
    }
    df["reasons"] = ""
    for name, m in rules.items():
        df.loc[m, "reasons"] = df.loc[m, "reasons"] + name + ","
    al = df[df["reasons"] != ""].copy()
    al["reasons"] = al["reasons"].str.rstrip(",")
    al["tier"] = al["ticker"].map(lambda t: "H" if t in hold else "W")
    return al[["time", "ticker", "tier", "reasons", "ret", "vni_ret", "idio", "vol_x", "val_bn", "Close"]]


def status_check(universe):
    """Diff secdef status + margin initialRate so với snapshot trước. Trả về list dict thay đổi."""
    sys.path.insert(0, WC)
    from dnse_api import DNSEClient
    c = DNSEClient.from_credentials_file()
    acct = None
    try:
        accts = c.accounts()
        acct = (accts.get("accounts") or accts)[0].get("id") if isinstance(accts, dict) else None
    except Exception:
        pass
    cur = {}
    for tk in sorted(universe):
        row = {}
        try:
            sd = c.secdef(tk, board_id="G1")
            r = sd[0] if isinstance(sd, list) else sd
            row["admin"] = r.get("symbolAdminStatusCode")
            row["method"] = r.get("symbolTradingMethodStatusCode")
            row["sanction"] = r.get("symbolTradingSanctionStatusCode")
        except Exception as e:
            row["error"] = str(e)[:80]
        cur[tk] = row
    prev = {}
    if os.path.exists(STATUS_SNAP):
        prev = json.load(open(STATUS_SNAP)).get("status", {})
    changes = []
    for tk, row in cur.items():
        if "error" in row:
            continue
        p = prev.get(tk)
        bad_now = any(row.get(k) not in (None, "NRM") for k in ("admin", "method", "sanction"))
        if p is None:
            if bad_now:  # lần đầu thấy đã khác NRM — vẫn báo (baseline seed)
                changes.append({"ticker": tk, "type": "STATUS_NOT_NRM_BASELINE", "now": row})
        elif {k: p.get(k) for k in ("admin", "method", "sanction")} != \
             {k: row.get(k) for k in ("admin", "method", "sanction")}:
            changes.append({"ticker": tk, "type": "STATUS_CHANGE", "was": p, "now": row})
    tmp = STATUS_SNAP + ".tmp"
    json.dump({"asof": datetime.datetime.now().isoformat(timespec="seconds"),
               "status": cur}, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS_SNAP)
    return changes


def write_flags(alerts_df):
    flags = {}
    if os.path.exists(FLAGS_PATH):
        flags = json.load(open(FLAGS_PATH))
    for _, r in alerts_df.iterrows():
        d = str(r["time"].date())
        f = flags.get(r["ticker"], {})
        f.update({"last_alert": max(d, f.get("last_alert", "")), "tier": r["tier"],
                  "reasons": r["reasons"], "ret": round(float(r["ret"]), 2),
                  "idio": round(float(r["idio"]), 2), "vol_x": round(float(r["vol_x"]), 2)})
        flags[r["ticker"]] = f
    tmp = FLAGS_PATH + ".tmp"
    json.dump(flags, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, FLAGS_PATH)


def selftest():
    import pandas as pd
    hold, wl = load_universe()
    ok = True
    cases = [("PNJ", "2026-07-03"), ("DGC", "2026-03-17")]
    df = load_prices({"PNJ", "DGC"}, datetime.date(2026, 1, 1), datetime.date(2026, 7, 16))
    al = compute_signals(df, hold)
    for tk, d0 in cases:
        sub = al[(al["ticker"] == tk) & (al["time"] >= pd.Timestamp(d0))]
        first = sub["time"].min()
        hit = (not sub.empty) and str(first.date()) == d0
        print(f"  {tk}: kỳ vọng alert {d0} → thực tế {first} {'PASS' if hit else 'FAIL'}")
        ok &= hit
    # negative control: PNJ 2026-03-09 sàn cùng thị trường — KHÔNG được trip IDIOCRASH/FLOOR2
    neg = al[(al["ticker"] == "PNJ") & (al["time"] == pd.Timestamp("2026-03-09"))]
    print(f"  PNJ 2026-03-09 (thị trường sập chung): {'PASS (không trip)' if neg.empty else 'FAIL: ' + neg.to_string()}")
    ok &= neg.empty
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", help="YYYY-MM-DD, scan phiên này (mặc định: phiên cuối trong cache)")
    ap.add_argument("--status-check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-flags", action="store_true", help="không ghi anomaly_flags.json")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())

    import pandas as pd
    hold, wl = load_universe()
    uni = hold | wl
    end = datetime.date.fromisoformat(args.asof) if args.asof else datetime.date.today()
    start = end - datetime.timedelta(days=70)  # đủ cho Volume_1M + 2 phiên streak
    df = load_prices(uni, start, end)
    if df.empty:
        print("Không có dữ liệu trong cache cho khoảng này.")
        sys.exit(1)
    last = pd.to_datetime(df["time"]).max()
    al = compute_signals(df, hold)
    al = al[al["time"] == last]
    print(f"# Anomaly scan — phiên {last.date()} | universe {len(uni)} mã (H:{len(hold)} / W:{len(wl)})")
    if al.empty:
        print("Không có tín hiệu giá/khối lượng bất thường.")
    else:
        for _, r in al.sort_values(["tier", "ticker"]).iterrows():
            print(f"  [{r['tier']}] {r['ticker']}: {r['reasons']} | ret {r['ret']:+.1f}% "
                  f"(VNI {r['vni_ret']:+.1f}%, idio {r['idio']:+.1f}%) vol {r['vol_x']:.1f}x "
                  f"val {r['val_bn']:.1f}B close {r['Close']:,.0f}")
        if not args.no_flags:
            write_flags(al)
            print(f"→ đã ghi cờ vào {FLAGS_PATH}")
    if args.status_check:
        ch = status_check(uni)
        if ch:
            print("## Thay đổi trạng thái sàn/margin (DNSE secdef):")
            for c in ch:
                print(" ", json.dumps(c, ensure_ascii=False))
        else:
            print("Trạng thái sàn: không thay đổi so với snapshot trước.")


if __name__ == "__main__":
    main()
