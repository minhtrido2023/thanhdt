# -*- coding: utf-8 -*-
"""lag_liq_signal_filter_selfcheck.py — self-check cho lag_liquidity_filter.lag_filter_illiquid.

Chạy:  $DNA_PYEXE lag_liq_signal_filter_selfcheck.py            (unit, bq giả lập — offline)
       $DNA_PYEXE lag_liq_signal_filter_selfcheck.py --live     (thêm 4 case chạm BQ thật)

Unit dùng bq giả lập nên KHÔNG phụ thuộc mạng/vintage dữ liệu; phần --live xác nhận đúng rổ
ứng viên LAG hiện tại (TMG bị loại, mã ADV bình thường không bị đụng, các book khác sạch).
"""
import os, sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from lag_liquidity_filter import lag_filter_illiquid, LAG_ADV_MAX_STALE_DAYS

ASOF = pd.Timestamp("2026-07-21")
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  {detail}")


def cand_df(tickers):
    return pd.DataFrame({"ticker": list(tickers),
                         "tier": ["LAG_HI"] * len(tickers),
                         "NP_R": [50.0] * len(tickers)})


def fake_bq(rows):
    """rows: {ticker: (days_stale, Volume_3M_P50, px)}; ticker vắng mặt = không có dòng giá.
    `px` = COALESCE(Price, Close) — cơ sở giá THÔ, đúng SELECT hiện tại (đổi 2026-08-02)."""
    def _bq(sql):
        recs = []
        for tk, (st, vol, px) in rows.items():
            if f"'{tk}'" not in sql:
                continue
            adv = None if (vol is None or px is None) else vol * px
            recs.append({"ticker": tk, "time": ASOF - pd.Timedelta(days=st),
                         "Volume_3M_P50": vol, "px": px, "adv_vnd": adv})
        return pd.DataFrame(recs, columns=["ticker", "time", "Volume_3M_P50", "px", "adv_vnd"])
    return _bq


print("=" * 78); print("  UNIT (bq giả lập)"); print("=" * 78)

# 1. mã ADV bình thường: KHÔNG bị đụng
b = fake_bq({"TRC": (0, 18350.0, 76100.0), "VHC": (0, 240800.0, 54500.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["TRC", "VHC"]), ASOF)
check("ADV bình thường → giữ nguyên", len(kept) == 2 and not dropped and err is None, f"{dropped}")

# 2. Volume_3M_P50 == 0 (case TMG) → loại, mã khác trong CÙNG rổ vẫn còn
b = fake_bq({"TMG": (0, 0.0, 64000.0), "TRC": (0, 18350.0, 76100.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["TMG", "TRC"]), ASOF)
check("Volume_3M_P50=0 → loại", [d["ticker"] for d in dropped] == ["TMG"], f"{dropped}")
check("… mã còn lại KHÔNG bị loại lây", list(kept["ticker"]) == ["TRC"], f"{list(kept['ticker'])}")

# 3. Volume_3M_P50 NULL → loại (không đo được ≠ đo được và bằng 0, cùng hành vi)
b = fake_bq({"XXX": (0, None, 10000.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["XXX"]), ASOF)
check("Volume_3M_P50 NULL → loại", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 4. không có dòng giá nào trong cửa sổ → loại
b = fake_bq({})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["GONE"]), ASOF)
check("không có dòng giá → loại", len(kept) == 0 and "không có dòng giá" in dropped[0]["reason"], f"{dropped}")

# 5. stale: đúng ngưỡng thì GIỮ, vượt ngưỡng thì LOẠI (biên)
b = fake_bq({"A": (LAG_ADV_MAX_STALE_DAYS, 1000.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["A"]), ASOF)
check(f"stale == {LAG_ADV_MAX_STALE_DAYS} ngày → GIỮ", len(kept) == 1 and not dropped, f"{dropped}")
b = fake_bq({"A": (LAG_ADV_MAX_STALE_DAYS + 1, 1000.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["A"]), ASOF)
check(f"stale == {LAG_ADV_MAX_STALE_DAYS + 1} ngày → LOẠI", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 6. ADV âm (dữ liệu bẩn) → loại
b = fake_bq({"NEG": (0, -5.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["NEG"]), ASOF)
check("ADV âm → loại", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 7. FAIL-OPEN khi cả truy vấn hỏng: giữ nguyên + báo lỗi (executor vẫn fail-closed)
def _boom(sql):
    raise RuntimeError("BQ down")
kept, dropped, err = lag_filter_illiquid(_boom, cand_df(["TMG", "TRC"]), ASOF)
check("BQ lỗi → fail-OPEN, giữ nguyên", len(kept) == 2 and not dropped, f"{dropped}")
check("… và báo lỗi qua lag_liq_filter_error", err is not None and "BQ down" in err, f"{err}")

# 8. rổ rỗng / None → no-op, không nổ
kept, dropped, err = lag_filter_illiquid(fake_bq({}), cand_df([]), ASOF)
check("rổ rỗng → no-op", len(kept) == 0 and not dropped and err is None)
kept, dropped, err = lag_filter_illiquid(fake_bq({}), None, ASOF)
check("cand=None → no-op", kept is None and not dropped and err is None)

# 9. không đụng cột khác / không đổi thứ tự các dòng còn lại
b = fake_bq({"A": (0, 1.0, 1.0), "B": (0, 0.0, 1.0), "C": (0, 2.0, 1.0)})
src = cand_df(["A", "B", "C"])
kept, dropped, _ = lag_filter_illiquid(b, src, ASOF)
check("giữ nguyên thứ tự + cột", list(kept["ticker"]) == ["A", "C"] and list(kept.columns) == list(src.columns))

if "--live" in sys.argv:
    print("=" * 78); print("  LIVE (BQ thật — rổ ứng viên LAG hiện tại)"); print("=" * 78)
    os.environ.pop("BQ_LOCAL_CACHE", None)
    from datetime import datetime, timedelta
    from simulate_holistic_nav import bq
    from lag_live_schedule import live_lag_candidates
    import custom30

    start = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
    q = live_lag_candidates(start=start); q = q[q["qualify"]]
    asof = pd.Timestamp(bq("SELECT MAX(t.time) AS m FROM tav2_bq.ticker AS t "
                           "WHERE t.ticker='VNINDEX'")["m"].iloc[0])
    kept, dropped, err = lag_filter_illiquid(bq, q, asof)
    names = sorted({d["ticker"] for d in dropped})
    print(f"  asof={asof.date()}  ứng viên {q['ticker'].nunique()} mã → loại {len(names)}: {names}")
    check("live: không lỗi truy vấn", err is None, f"{err}")
    check("live: TMG (Volume_3M_P50=0) BỊ LOẠI", "TMG" in names)
    check("live: TRC (ADV ~1,4 tỷ) KHÔNG bị loại", "TRC" not in names and "TRC" in set(kept["ticker"]))
    check("live: mọi mã giữ lại đều có ADV > 0",
          not set(kept["ticker"]) & set(names))

    # phạm vi: 3 book còn lại không có mã ADV≤0 (lý do KHÔNG áp filter cho chúng)
    capit = bq("""SELECT COUNTIF(p.Volume_3M_P50 IS NULL OR p.Volume_3M_P50<=0) AS nbad
FROM tav2_bq.ticker_prune AS p
WHERE p.time BETWEEN DATE '2014-01-01' AND DATE '2026-06-15'
  AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")["nbad"].iloc[0]
    check("phạm vi: pool CAPIT 2014+ có 0 dòng ADV≤0", int(capit) == 0, f"nbad={capit}")

    pk = custom30.current(bq, table=custom30.TABLE_V)
    tl = ",".join(f"'{t}'" for t in pk["ticker"])
    pl = bq(f"""SELECT t.ticker, t.Volume_3M_P50*t.Close AS adv FROM tav2_bq.ticker AS t
WHERE t.ticker IN ({tl}) AND t.time <= DATE '{asof.date()}'
  AND t.time >= DATE_SUB(DATE '{asof.date()}', INTERVAL 30 DAY)
QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC)=1""")
    check("phạm vi: rổ PARK custom30V không có mã ADV≤0",
          bool(((pl["adv"].notna()) & (pl["adv"] > 0)).all()), f"{pl[pl['adv'].fillna(0)<=0]}")

    # CƠ SỞ GIÁ (thêm 2026-08-02, job Taylor_20260802_163657) — positive control 2 chiều:
    # module PHẢI trả ADV theo giá THÔ (Price), KHÔNG theo Close đã điều chỉnh. Chọn mã có
    # Close != Price để hai chân tách rời được; nếu không có mã nào như vậy thì check vô nghĩa
    # và phải nói ra, không im lặng PASS.
    probe = bq(f"""SELECT t.ticker, t.time, t.Volume_3M_P50, t.Price, t.Close
FROM tav2_bq.ticker AS t
WHERE t.time <= DATE '{asof.date()}' AND t.time >= DATE_SUB(DATE '{asof.date()}', INTERVAL 10 DAY)
  AND t.Volume_3M_P50 > 0 AND t.Price > 0 AND ABS(t.Close - t.Price) / t.Price > 0.05
ORDER BY t.time DESC, t.ticker LIMIT 1""")
    check("cơ sở giá: tìm được mã Close≠Price để kiểm", len(probe) == 1, "0 mã — check dưới vô nghĩa")
    if len(probe) == 1:
        r0 = probe.iloc[0]
        # CÙNG (ticker, time) với dòng probe — nếu để cửa sổ ngày rộng thì hai truy vấn có thể
        # rơi vào HAI phiên khác nhau và check so hai số không cùng gốc (đã bị chính nó bắt).
        a = bq(f"""SELECT t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS adv_vnd
FROM tav2_bq.ticker AS t
WHERE t.ticker='{r0.ticker}' AND t.time = DATE '{pd.Timestamp(r0.time).date()}'""")["adv_vnd"].iloc[0]
        want_px = float(r0.Volume_3M_P50) * float(r0.Price)
        want_cl = float(r0.Volume_3M_P50) * float(r0.Close)
        check(f"cơ sở giá: ADV({r0.ticker}) == Volume_3M_P50 × Price",
              abs(float(a) - want_px) < 1.0, f"got {a:,.0f} want {want_px:,.0f}")
        check(f"cơ sở giá: ADV({r0.ticker}) != Volume_3M_P50 × Close (chiều ngược)",
              abs(float(a) - want_cl) > 1.0, f"got {a:,.0f} == Close-basis {want_cl:,.0f}")

print("=" * 78)
print(f"  {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
