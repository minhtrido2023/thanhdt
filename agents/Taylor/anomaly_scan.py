#!/usr/bin/env python3
"""
anomaly_scan.py — daily scan phát hiện CHỦ ĐỘNG case bất thường kiểu DGC/PNJ
============================================================================
Job Taylor_20260717_111204. READ-ONLY — không đổi logic trading, không đặt lệnh.

Universe = mã đang giữ (SpaceX/ZaloPay, đọc active_nav_*.json)  [tier H — nhạy]
         + watchlist Golden/Strong (fa_ratings_8l rating<=2)     [tier W — chặt]
Cổng độ tươi cho nguồn watchlist: `universe_freshness()` (§14, thêm 2026-08-14 job
Taylor_20260814_041116) — producer active_nav chạy cron RIÊNG 20:15 ICT, chết một tối là
sáng sau quét sổ cũ trong im lặng. CẢNH BÁO, không fail-closed; cờ ra `--emit-json`.

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
ACTIVE_NAV_GLOB = os.path.join(WC, "data/execution_logs/active_nav_*.json")

LIQ_1M_BN = 3.0   # mã "thanh khoản": giá trị GD bình quân 1 tháng >= 3 tỷ/phiên

# Producer của `active_nav_*.json` = compute_active_nav_all.sh, cron 20:15 ICT T2-T6.
# Cho nó tới 21:00 ICT mới coi là "đáng lẽ đã có bản của hôm nay" (45' dự phòng cho retry/
# DNSE chậm — §14: đủ rộng cho jitter thường, đủ chặt để trượt TRỌN một phiên là trip).
_ACTIVE_NAV_DONE_BY_ICT = datetime.time(21, 0)

sys.path.insert(0, WC)


def _ict_now():
    """Giờ ICT thật, KHÔNG phụ thuộc TZ của process gọi vào (§16 — cron chạy dưới TZ=UTC)."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=7)


def _is_trading_day(d):
    from trading_bot.vn_market import is_holiday
    return d.weekday() < 5 and not is_holiday(d)


def _prev_trading_day(d):
    d -= datetime.timedelta(days=1)
    while not _is_trading_day(d):
        d -= datetime.timedelta(days=1)
    return d


def expected_universe_asof(now_ict=None):
    """Ngày `computed_at` MỚI NHẤT mà producer đã có thể ghi, tính tới thời điểm `now_ict`.

    Sáng thứ Hai 08:20 ⇒ Thứ Sáu (producer chưa chạy lượt 20:15 của thứ Hai). Tối thứ Ba
    22:00 ⇒ thứ Ba. Không phải "hôm nay" — đó chính là chỗ một cổng độ tươi ngây thơ sẽ báo
    động giả mỗi sáng.
    """
    now = now_ict or _ict_now()
    d = now.date()
    if _is_trading_day(d) and now.time() >= _ACTIVE_NAV_DONE_BY_ICT:
        return d
    return _prev_trading_day(d)


def _sessions_between(older, newer):
    """Số phiên giao dịch mà `older` bị trễ so với `newer` (0 = không trễ)."""
    n, d = 0, newer
    while d > older and n < 60:
        d = _prev_trading_day(d)
        n += 1
    return n


def universe_freshness(files, now_ict=None):
    """Cổng độ tươi cho nguồn watchlist `active_nav_*.json` (§14 producer→consumer).

    Producer (compute_active_nav_all.sh, 20:15 ICT T2-T6) và consumer (anomaly_scan qua
    ops_health_check, 08:20 ICT) chạy trên HAI cron độc lập. Producer chết một tối ⇒ sáng
    hôm sau scan này quét một danh mục CŨ và không ai biết: mã vừa mua hôm qua vô hình với
    lớp bảo vệ. `load_universe()` trước đây chỉ `json.load()` nên không phân biệt được.

    CHỈ CẢNH BÁO, KHÔNG fail-closed — cùng lựa chọn với `anomaly_gate.anomaly_flags_freshness()`:
    quét sổ cũ vẫn hơn không quét gì. Nhưng phải NÓI RA (quiet-heartbeat: "đã quét, sạch" phải
    phân biệt được với "quét nhầm sổ cũ").

    Trả dict {"is_stale", "asof", "expected", "lag_sessions", "reason", "files"}.
    """
    exp = expected_universe_asof(now_ict)
    per_file, dates, bad = [], [], []
    for f in sorted(files):
        rec = {"file": os.path.basename(f), "computed_at": None}
        try:
            d = json.load(open(f, encoding="utf-8"))
            rec["computed_at"] = d.get("computed_at")
            rec["n_positions"] = len(d.get("positions", []))
            dates.append(datetime.date.fromisoformat(str(d["computed_at"])))
        except Exception as ex:
            rec["error"] = str(ex)[:120]
            bad.append(f"{rec['file']}: {str(ex)[:60]}")
        per_file.append(rec)
    if not files:
        return {"is_stale": True, "asof": None, "expected": str(exp), "lag_sessions": None,
                "reason": "không thấy file active_nav_*.json nào", "files": []}
    if bad:
        return {"is_stale": True, "asof": None, "expected": str(exp), "lag_sessions": None,
                "reason": "không đọc được computed_at (" + "; ".join(bad) + ")", "files": per_file}
    # Lấy file CŨ NHẤT: 1 account trễ cũng đủ làm watchlist thiếu mã của account đó.
    oldest = min(dates)
    if oldest >= exp:
        return {"is_stale": False, "asof": str(oldest), "expected": str(exp),
                "lag_sessions": 0, "reason": "", "files": per_file}
    lag = _sessions_between(oldest, exp)
    return {"is_stale": True, "asof": str(oldest), "expected": str(exp), "lag_sessions": lag,
            "reason": f"computed_at cũ nhất {oldest} trễ {lag} phiên so với kỳ vọng {exp} "
                      f"(compute_active_nav_all.sh 20:15 ICT T2-T6 có chạy không?)",
            "files": per_file}


def load_universe(now_ict=None):
    """→ (hold, watchlist, freshness_meta). `freshness_meta` KHÔNG được bỏ qua ở caller —
    xem `universe_freshness()`; nó là lý do duy nhất để phân biệt sổ hôm nay với sổ tuần trước."""
    files = glob.glob(ACTIVE_NAV_GLOB)
    meta = universe_freshness(files, now_ict=now_ict)
    hold = set()
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue          # đã được ghi nhận trong meta.reason ở trên
        hold |= {p["ticker"] for p in d.get("positions", [])}
    import pandas as pd
    fr = pd.read_parquet(os.path.join(CACHE, "fa_ratings_8l.parquet"))
    fr["time"] = pd.to_datetime(fr["time"])
    wl = set(fr.sort_values("time").groupby("ticker").tail(1).query("rating<=2")["ticker"])
    return hold, wl, meta


ICB_BANK = 8355   # ICB level-4 "Banks". EVF (8773 tài chính tiêu dùng) và VIX/VND (8777
                  # chứng khoán) là tài chính NHƯNG KHÔNG phải ngân hàng — bộ từ khoá
                  # "kiểm soát đặc biệt / chuyển giao bắt buộc" không áp cho chúng.


def classify_bank_group(tickers):
    """Chia watchlist thành (ngân hàng, ngoài ngân hàng) theo ICB_Code — KHÔNG chép cứng
    danh sách mã. Đây là điểm của Việc E2: danh sách ngân hàng chép tay sẽ lạc hậu đúng lúc
    danh mục đổi (thêm/bớt 1 nhà băng), mà đó lại là lúc cần nó nhất.

    Không tra được ICB (mã mới, cache thiếu) → xếp vào NGOÀI ngân hàng: bộ từ khoá chung vẫn
    phủ, chỉ mất phần bổ sung riêng ngành — fail-safe đúng chiều.
    """
    import duckdb
    tickers = sorted(tickers)
    if not tickers:
        return [], []
    files = sorted(glob.glob(os.path.join(CACHE, "ticker", "*.parquet")))[-2:]
    tl = "','".join(tickers)
    q = (f"select ticker, last(ICB_Code order by time) icb from read_parquet({files!r}) "
         f"where ticker in ('{tl}') and ICB_Code is not null group by ticker")
    icb = dict(duckdb.connect().execute(q).df().itertuples(index=False, name=None))
    banks = [t for t in tickers if int(icb.get(t) or 0) == ICB_BANK]
    return banks, [t for t in tickers if t not in banks]


def print_universe_block():
    """In khối watchlist SỐNG, dạng text nhúng thẳng vào prompt dispatch (fearbuy scan).

    Cố ý KHÔNG dùng ký tự ` hay " — chuỗi này được nội suy vào heredoc bash của
    fearbuy_weekly_scan.sh; cả hai đều là metachar sống trong nháy kép (§15).
    """
    hold, wl, meta = load_universe()
    banks, others = classify_bank_group(hold)
    state = "QUA HAN — DANH MUC CO THE THIEU MA MOI MUA" if meta["is_stale"] else "TUOI"
    print("WATCHLIST SONG — sinh tu dong tu vi the that cua ca 2 account, KHONG chep cung.")
    print(f"  nguon: data/execution_logs/active_nav_*.json | computed_at={meta['asof']} [{state}]")
    if meta["is_stale"]:
        print(f"  CANH BAO: {meta['reason']}")
    print(f"  NHOM NGAN HANG (ICB {ICB_BANK}, n={len(banks)}): {' '.join(banks) if banks else '(khong co)'}")
    print(f"  NHOM NGOAI NGAN HANG (n={len(others)}): {' '.join(others) if others else '(khong co)'}")
    print(f"  (tier W — watchlist chat luong 8L rating<=2, khong phai vi the: {len(wl)} ma)")


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


def write_flags(alerts_df, scan_asof=None):
    """Ghi/merge cờ + ĐÓNG DẤU ĐỘ TƯƠI của cả FILE vào `_meta.generated_at`.

    `_meta` KHÁC HẲN `last_alert` của từng cờ: `last_alert` = phiên cờ đó nổ (TTL 30 ngày,
    chính sách hiệu lực của 1 cờ); `_meta.generated_at` = lần cuối scan này CHẠY XONG, tức
    file có được làm mới hôm nay không. Không có nó thì một file đứng im 1 tuần (scan chết
    im lặng) đọc y hệt file mới — consumer downstream (golive_recommend_v23 → plan tiền
    thật) không phân biệt được (audit §14 cron freshness, Winston_20260731_060739).

    Cố ý dùng key lồng `_meta` (dict) chứ KHÔNG phải field top-level kiểu chuỗi: mọi reader
    hiện có duyệt `flags.items()` rồi gọi `f.get("last_alert")` — một giá trị CHUỖI ở
    top-level sẽ ném AttributeError, rơi vào except fail-open và TẮT ÂM THẦM cả cái gate an
    toàn. `_meta` là dict nên `.get()` vẫn chạy, trả "" ⇒ tự động rớt khỏi cửa sổ TTL.
    """
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
    flags["_meta"] = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scan_asof": str(scan_asof) if scan_asof is not None else None,
        "n_alerts_this_run": int(len(alerts_df)),
    }
    tmp = FLAGS_PATH + ".tmp"
    json.dump(flags, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, FLAGS_PATH)


def selftest():
    import pandas as pd
    hold, wl, _meta = load_universe()
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
    ap.add_argument("--print-universe", action="store_true",
                    help="in watchlist SỐNG theo nhóm ngân hàng/ngoài ngân hàng để nhúng vào "
                         "prompt dispatch (fearbuy_weekly_scan.sh) — thay danh sách chép cứng")
    ap.add_argument("--no-flags", action="store_true", help="không ghi anomaly_flags.json")
    ap.add_argument("--backfill-days", type=int, default=0,
                    help="ghi cờ cho MỌI phiên trong N ngày gần nhất thay vì chỉ phiên cuối "
                         "(seed lần đầu / bù những ngày chưa chạy scan)")
    ap.add_argument("--emit-json", help="ghi tóm tắt phiên (tier_h/tier_w_count/status_changes) ra PATH "
                    "cho hệ escalation đọc — máy-đọc, không parse text")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.print_universe:
        print_universe_block()
        return

    import pandas as pd
    hold, wl, uni_meta = load_universe()
    uni = hold | wl
    end = datetime.date.fromisoformat(args.asof) if args.asof else _ict_now().date()
    start = end - datetime.timedelta(days=70 + args.backfill_days)  # đủ cho Volume_1M + 2 phiên streak
    df = load_prices(uni, start, end)
    if df.empty:
        print("Không có dữ liệu trong cache cho khoảng này.")
        sys.exit(1)
    last = pd.to_datetime(df["time"]).max()
    al = compute_signals(df, hold)
    if args.backfill_days:
        al = al[al["time"] >= last - pd.Timedelta(days=args.backfill_days)]
    else:
        al = al[al["time"] == last]
    emit = {"asof": str(last.date()), "tier_h": [], "tier_w_count": 0, "status_changes": [],
            # Cổng độ tươi watchlist — anomaly_escalate.py đọc 3 field này để báo Trading Daily.
            # Không đưa ra emit thì cảnh báo chết trong /tmp và không ai thấy.
            "universe_stale": bool(uni_meta["is_stale"]),
            "universe_asof": uni_meta["asof"],
            "universe_stale_reason": uni_meta["reason"]}
    for _, r in al.iterrows():
        rec = {"ticker": r["ticker"], "reasons": r["reasons"], "ret": round(float(r["ret"]), 2),
               "vni_ret": round(float(r["vni_ret"]), 2), "idio": round(float(r["idio"]), 2),
               "vol_x": round(float(r["vol_x"]), 2), "val_bn": round(float(r["val_bn"]), 2),
               "close": round(float(r["Close"]), 0)}
        if r["tier"] == "H":
            emit["tier_h"].append(rec)
        else:
            emit["tier_w_count"] += 1
    print(f"# Anomaly scan — phiên {last.date()} | universe {len(uni)} mã (H:{len(hold)} / W:{len(wl)})")
    if uni_meta["is_stale"]:
        print(f"⚠️ WATCHLIST QUÁ HẠN — {uni_meta['reason']}")
        print("   ⇒ đang quét theo SỔ CŨ: mã mua sau ngày đó KHÔNG được bảo vệ. Vẫn quét tiếp "
              "(quét sổ cũ hơn không quét gì), nhưng đừng đọc kết quả này như 'danh mục sạch'.")
    else:
        print(f"  watchlist tươi (active_nav computed_at {uni_meta['asof']})")
    if al.empty:
        print("Không có tín hiệu giá/khối lượng bất thường.")
    else:
        for _, r in al.sort_values(["tier", "ticker", "time"]).iterrows():
            print(f"  [{r['tier']}] {r['time'].date()} {r['ticker']}: {r['reasons']} | ret {r['ret']:+.1f}% "
                  f"(VNI {r['vni_ret']:+.1f}%, idio {r['idio']:+.1f}%) vol {r['vol_x']:.1f}x "
                  f"val {r['val_bn']:.1f}B close {r['Close']:,.0f}")
    # Đóng dấu độ tươi CẢ KHI KHÔNG có tín hiệu — "hôm nay không có anomaly" là kết quả
    # hợp lệ của một lần scan chạy tốt; nếu chỉ ghi khi có alert thì ngày sạch cũng làm
    # file trông cũ y như ngày scan chết → cảnh báo giả mỗi ngày, WARN mất giá trị.
    if not args.no_flags:
        write_flags(al, scan_asof=last.date())
        print(f"→ đã ghi cờ + dấu độ tươi (_meta.generated_at) vào {FLAGS_PATH}")
    if args.status_check:
        ch = status_check(uni)
        emit["status_changes"] = ch
        if ch:
            print("## Thay đổi trạng thái sàn/margin (DNSE secdef):")
            for c in ch:
                print(" ", json.dumps(c, ensure_ascii=False))
        else:
            print("Trạng thái sàn: không thay đổi so với snapshot trước.")

    if args.emit_json:
        tmp = args.emit_json + ".tmp"
        json.dump(emit, open(tmp, "w"), ensure_ascii=False, indent=1)
        os.replace(tmp, args.emit_json)


if __name__ == "__main__":
    main()
