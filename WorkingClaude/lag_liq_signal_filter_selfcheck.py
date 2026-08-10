# -*- coding: utf-8 -*-
"""lag_liq_signal_filter_selfcheck.py — self-check cho lag_liquidity_filter (LAG + BAL).

Chạy:  $DNA_PYEXE lag_liq_signal_filter_selfcheck.py            (unit, bq giả lập — offline)
       $DNA_PYEXE lag_liq_signal_filter_selfcheck.py --live     (thêm case chạm BQ thật)

Unit dùng bq giả lập nên KHÔNG phụ thuộc mạng/vintage dữ liệu; phần --live xác nhận đúng rổ
ứng viên LAG hiện tại (TMG bị loại, các book khác sạch).

CẤU TRÚC (đổi 2026-08-10 khi thêm sàn ADV 2 tỷ):
  · Khối A = 3 nhánh "KHÔNG đo được/không mua được" (ADV≤0, thiếu dòng giá, stale). Chạy với
    `min_adv_vnd=0` — vừa giữ nguyên ý nghĩa gốc của từng case, vừa là CHÂN CONTROL chứng minh
    `min_adv_vnd=0` tái lập ĐÚNG hành vi trước 2026-08-10.
  · Khối B = sàn ADV 2 tỷ (mặc định production). MỌI case "chặn được" đều có CA CHỨNG MINH
    NGƯỢC: cùng dữ liệu, bỏ sàn ⇒ mã đó THẬT SỰ lọt qua. Khẳng định suông không tính.
  · Khối C = `bal_filter_thin` (BAL, thuần pandas).
  · Khối D = chuỗi lý do phải parse được bởi `lag_liq_ledger.parse_liq_reason` — sổ theo dõi
    tách 'adv_thin' (mua được, dưới sàn) khỏi 'adv_zero' (không mua được) là toàn bộ lý do sổ
    đó tồn tại (kb/projects/lag-adv-filter-tracking.md).
"""
import os, sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from lag_liquidity_filter import (lag_filter_illiquid, bal_filter_thin,
                                  LAG_ADV_MAX_STALE_DAYS, ADV_MIN_VND)

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


print("=" * 78); print("  KHỐI A — UNIT nhánh 'không đo được' (control leg: min_adv_vnd=0)"); print("=" * 78)

# 1. mã ADV bình thường: KHÔNG bị đụng
b = fake_bq({"TRC": (0, 18350.0, 76100.0), "VHC": (0, 240800.0, 54500.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["TRC", "VHC"]), ASOF, min_adv_vnd=0)
check("ADV bình thường → giữ nguyên", len(kept) == 2 and not dropped and err is None, f"{dropped}")

# 2. Volume_3M_P50 == 0 (case TMG) → loại, mã khác trong CÙNG rổ vẫn còn
b = fake_bq({"TMG": (0, 0.0, 64000.0), "TRC": (0, 18350.0, 76100.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["TMG", "TRC"]), ASOF, min_adv_vnd=0)
check("Volume_3M_P50=0 → loại", [d["ticker"] for d in dropped] == ["TMG"], f"{dropped}")
check("… mã còn lại KHÔNG bị loại lây", list(kept["ticker"]) == ["TRC"], f"{list(kept['ticker'])}")

# 3. Volume_3M_P50 NULL → loại (không đo được ≠ đo được và bằng 0, cùng hành vi)
b = fake_bq({"XXX": (0, None, 10000.0)})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["XXX"]), ASOF, min_adv_vnd=0)
check("Volume_3M_P50 NULL → loại", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 4. không có dòng giá nào trong cửa sổ → loại
b = fake_bq({})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["GONE"]), ASOF, min_adv_vnd=0)
check("không có dòng giá → loại", len(kept) == 0 and "không có dòng giá" in dropped[0]["reason"], f"{dropped}")

# 5. stale: đúng ngưỡng thì GIỮ, vượt ngưỡng thì LOẠI (biên)
b = fake_bq({"A": (LAG_ADV_MAX_STALE_DAYS, 1000.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["A"]), ASOF, min_adv_vnd=0)
check(f"stale == {LAG_ADV_MAX_STALE_DAYS} ngày → GIỮ", len(kept) == 1 and not dropped, f"{dropped}")
b = fake_bq({"A": (LAG_ADV_MAX_STALE_DAYS + 1, 1000.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["A"]), ASOF, min_adv_vnd=0)
check(f"stale == {LAG_ADV_MAX_STALE_DAYS + 1} ngày → LOẠI", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 6. ADV âm (dữ liệu bẩn) → loại
b = fake_bq({"NEG": (0, -5.0, 10000.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["NEG"]), ASOF, min_adv_vnd=0)
check("ADV âm → loại", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 7. FAIL-OPEN khi cả truy vấn hỏng: giữ nguyên + báo lỗi (executor vẫn fail-closed)
def _boom(sql):
    raise RuntimeError("BQ down")
kept, dropped, err = lag_filter_illiquid(_boom, cand_df(["TMG", "TRC"]), ASOF, min_adv_vnd=0)
check("BQ lỗi → fail-OPEN, giữ nguyên", len(kept) == 2 and not dropped, f"{dropped}")
check("… và báo lỗi qua lag_liq_filter_error", err is not None and "BQ down" in err, f"{err}")

# 8. rổ rỗng / None → no-op, không nổ
kept, dropped, err = lag_filter_illiquid(fake_bq({}), cand_df([]), ASOF, min_adv_vnd=0)
check("rổ rỗng → no-op", len(kept) == 0 and not dropped and err is None)
kept, dropped, err = lag_filter_illiquid(fake_bq({}), None, ASOF, min_adv_vnd=0)
check("cand=None → no-op", kept is None and not dropped and err is None)

# 9. không đụng cột khác / không đổi thứ tự các dòng còn lại
b = fake_bq({"A": (0, 1.0, 1.0), "B": (0, 0.0, 1.0), "C": (0, 2.0, 1.0)})
src = cand_df(["A", "B", "C"])
kept, dropped, _ = lag_filter_illiquid(b, src, ASOF, min_adv_vnd=0)
check("giữ nguyên thứ tự + cột", list(kept["ticker"]) == ["A", "C"] and list(kept.columns) == list(src.columns))

print("=" * 78)
print(f"  KHỐI B — SÀN ADV {ADV_MIN_VND/1e9:.0f} TỶ trên book LAG (mặc định production)")
print("=" * 78)

check("hằng số sàn = 2 tỷ (đổi ⇒ phải đổi trading_bot/due_diligence.ADV_THIN_VND)",
      ADV_MIN_VND == 2e9, f"{ADV_MIN_VND}")

# B1. TRC — SỐ THẬT đo trên BQ 2026-08-07 (Volume_3M_P50=19.186,5 × px=74.900 = 1,437 tỷ).
#     Đây chính là mã user duyệt mua ngày 07-24 (phương án C, job Taylor_20260721_172103) ⇒ ca
#     đắt nhất của sàn mới, phải có test đóng đinh chứ không để phát hiện trên plan thật.
TRC = (0, 19186.5, 74900.0)          # 1,4370 tỷ  < sàn
VHC = (0, 213400.0, 51400.0)         # 10,969 tỷ  > sàn
b = fake_bq({"TRC": TRC, "VHC": VHC})
kept, dropped, err = lag_filter_illiquid(b, cand_df(["TRC", "VHC"]), ASOF)
check("B1 TRC (ADV 1,44 tỷ) BỊ LOẠI, VHC (10,97 tỷ) giữ",
      [d["ticker"] for d in dropped] == ["TRC"] and list(kept["ticker"]) == ["VHC"], f"{dropped}")
#     CA CHỨNG MINH NGƯỢC: cùng dữ liệu, bỏ sàn ⇒ TRC THẬT SỰ lọt (nếu không, B1 vô nghĩa).
kept0, dropped0, _ = lag_filter_illiquid(b, cand_df(["TRC", "VHC"]), ASOF, min_adv_vnd=0)
check("B1' bỏ sàn ⇒ TRC LỌT QUA (chứng minh B1 do sàn chặn, không do nhánh khác)",
      not dropped0 and list(kept0["ticker"]) == ["TRC", "VHC"], f"{dropped0}")

# B2. BIÊN: `<` chứ không `<=` — đúng sàn thì GIỮ, dưới 1 đồng thì LOẠI.
b = fake_bq({"EQ": (0, 2e9, 1.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["EQ"]), ASOF)
check("B2 ADV == đúng 2,000 tỷ → GIỮ", len(kept) == 1 and not dropped, f"{dropped}")
b = fake_bq({"LO": (0, 2e9 - 1, 1.0)})
kept, dropped, _ = lag_filter_illiquid(b, cand_df(["LO"]), ASOF)
check("B2' ADV == 2 tỷ − 1đ → LOẠI", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# B3. Sàn KHÔNG được nuốt 3 nhánh cũ: ADV=0 phải giữ nguyên lý do 'không mua được', vì sổ
#     lag_liq_ledger phân biệt hai nhóm này (mua được vs không mua được).
b = fake_bq({"Z": (0, 0.0, 64000.0)})
_, dropped, _ = lag_filter_illiquid(b, cand_df(["Z"]), ASOF)
check("B3 ADV=0 vẫn báo lý do 'ADV ≤ 0', KHÔNG phải lý do sàn",
      "ADV ≤ 0" in dropped[0]["reason"] and "< sàn" not in dropped[0]["reason"], f"{dropped}")

# B4. stale ĐI TRƯỚC sàn: mã cũ + ADV to vẫn bị loại vì stale (thứ tự nhánh không đảo).
b = fake_bq({"OLD": (LAG_ADV_MAX_STALE_DAYS + 1, 1e6, 1e5)})   # ADV 100 tỷ nhưng cũ
_, dropped, _ = lag_filter_illiquid(b, cand_df(["OLD"]), ASOF)
check("B4 stale + ADV to → loại vì STALE (không phải vì sàn)",
      "ADV cũ" in dropped[0]["reason"], f"{dropped}")

# B5. dropped của nhánh sàn PHẢI kèm adv_vnd (số) để báo cáo/ledger không phải parse chuỗi.
b = fake_bq({"TRC": TRC})
_, dropped, _ = lag_filter_illiquid(b, cand_df(["TRC"]), ASOF)
check("B5 dropped kèm field adv_vnd số",
      abs(dropped[0].get("adv_vnd", 0) - 19186.5 * 74900.0) < 1.0, f"{dropped}")

# B6. BQ lỗi vẫn fail-OPEN kể cả khi sàn bật (sàn không được biến lỗi mạng thành chặn sạch).
kept, dropped, err = lag_filter_illiquid(_boom, cand_df(["TRC", "VHC"]), ASOF)
check("B6 BQ lỗi + sàn bật → vẫn fail-OPEN giữ nguyên", len(kept) == 2 and not dropped, f"{err}")

print("=" * 78); print("  KHỐI C — bal_filter_thin (BAL, thuần pandas)"); print("=" * 78)


def bal_df(pairs):
    """pairs: [(ticker, liq_vnd)] — mô phỏng dòng SIGNAL_V11 đã lọc TIER_BAL."""
    return pd.DataFrame({"ticker": [t for t, _ in pairs],
                         "play_type": ["MOMENTUM"] * len(pairs),
                         "ta": [300.0] * len(pairs),
                         "liq": [v for _, v in pairs]})


# C1. dưới sàn → loại; trên sàn → giữ. Số lấy từ tên THẬT trong băng [1e9, 2e9) đo 365 ngày.
src = bal_df([("SJS", 1.5e9), ("FPT", 80e9), ("TCI", 1.05e9)])
kept, dropped, err = bal_filter_thin(src)
check("C1 SJS/TCI (<2 tỷ) loại, FPT giữ",
      [d["ticker"] for d in dropped] == ["SJS", "TCI"] and list(kept["ticker"]) == ["FPT"], f"{dropped}")
check("C1a err=None khi cột liq đầy đủ", err is None, f"{err}")
#     CA CHỨNG MINH NGƯỢC
kept0, dropped0, _ = bal_filter_thin(src, min_adv_vnd=0)
check("C1' bỏ sàn ⇒ cả 3 LỌT QUA", not dropped0 and len(kept0) == 3, f"{dropped0}")

# C2. BIÊN `<`: đúng 2 tỷ giữ, thiếu 1 đồng loại.
kept, dropped, _ = bal_filter_thin(bal_df([("EQ", 2e9), ("LO", 2e9 - 1)]))
check("C2 biên: EQ giữ, LO loại",
      list(kept["ticker"]) == ["EQ"] and [d["ticker"] for d in dropped] == ["LO"], f"{dropped}")

# C3. NaN ở TỪNG DÒNG → loại (fail-closed), khác hẳn thiếu CẢ CỘT → fail-open.
kept, dropped, err = bal_filter_thin(bal_df([("NAN", float("nan")), ("OK", 5e9)]))
check("C3 liq=NaN → LOẠI (fail-closed từng dòng)",
      [d["ticker"] for d in dropped] == ["NAN"] and err is None, f"{dropped}")
check("C3a dropped của NaN có adv_vnd=None + lý do đọc được",
      dropped[0]["adv_vnd"] is None and "n/a" in dropped[0]["reason"], f"{dropped}")

# C4. thiếu CẢ cột liq (SQL đổi schema) → FAIL-OPEN + cờ lỗi, KHÔNG chặn sạch book BAL.
no_liq = bal_df([("A", 5e9)]).drop(columns=["liq"])
kept, dropped, err = bal_filter_thin(no_liq)
check("C4 thiếu cột liq → fail-OPEN giữ nguyên + báo lỗi",
      len(kept) == 1 and not dropped and err is not None and "liq" in err, f"{err}")

# C5. liq dạng chuỗi (CSV/BQ trả object) vẫn so sánh đúng, không nổ.
s = bal_df([("S1", 0), ("S2", 0)]); s["liq"] = ["1500000000", "9000000000"]
kept, dropped, err = bal_filter_thin(s)
check("C5 liq kiểu chuỗi → ép số, S1 loại S2 giữ",
      [d["ticker"] for d in dropped] == ["S1"] and list(kept["ticker"]) == ["S2"], f"{dropped}/{err}")

# C6. rỗng/None → no-op; cột + thứ tự giữ nguyên.
kept, dropped, err = bal_filter_thin(bal_df([]))
check("C6 rỗng → no-op", len(kept) == 0 and not dropped and err is None)
kept, dropped, err = bal_filter_thin(None)
check("C6a None → no-op", kept is None and not dropped and err is None)
src = bal_df([("A", 9e9), ("B", 1e9), ("C", 8e9)])
kept, _, _ = bal_filter_thin(src)
check("C6b giữ nguyên thứ tự + cột",
      list(kept["ticker"]) == ["A", "C"] and list(kept.columns) == list(src.columns))

# C7. KHÔNG sửa bảng gốc tại chỗ (golive dùng lại `today` sau đó).
before = len(src)
bal_filter_thin(src)
check("C7 không mutate bảng đầu vào", len(src) == before)

print("=" * 78); print("  KHỐI D — chuỗi lý do phải parse được bởi lag_liq_ledger"); print("=" * 78)

from lag_liq_ledger import parse_liq_reason

b = fake_bq({"TRC": TRC})
_, dropped, _ = lag_filter_illiquid(b, cand_df(["TRC"]), ASOF)
kind, metric = parse_liq_reason(dropped[0]["reason"])
check("D1 lý do sàn → kind='adv_thin' (KHÔNG lẫn sang 'adv_zero')", kind == "adv_thin", f"{kind}")
check("D1a metric = ADV theo VND, khớp số đo (sai số làm tròn 2 chữ số)",
      isinstance(metric, float) and abs(metric - 19186.5 * 74900.0) < 1e7, f"{metric}")

_, dz, _ = lag_filter_illiquid(fake_bq({"Z": (0, 0.0, 64000.0)}), cand_df(["Z"]), ASOF)
check("D2 ADV=0 vẫn ra kind='adv_zero' (thứ tự regex không nuốt nhánh cũ)",
      parse_liq_reason(dz[0]["reason"])[0] == "adv_zero", f"{parse_liq_reason(dz[0]['reason'])}")

_, ds, _ = lag_filter_illiquid(fake_bq({"O": (LAG_ADV_MAX_STALE_DAYS + 1, 1e6, 1e5)}),
                               cand_df(["O"]), ASOF)
check("D3 stale vẫn ra kind='stale_adv'", parse_liq_reason(ds[0]["reason"])[0] == "stale_adv")

_, dn, _ = lag_filter_illiquid(fake_bq({}), cand_df(["GONE"]), ASOF)
check("D4 thiếu dòng giá vẫn ra kind='no_price_row'",
      parse_liq_reason(dn[0]["reason"])[0] == "no_price_row")

_, dbal, _ = bal_filter_thin(bal_df([("NAN", float("nan"))]))
check("D5 lý do BAL (adv=n/a) cũng ra 'adv_thin', metric rỗng — không nổ regex",
      parse_liq_reason(dbal[0]["reason"]) == ("adv_thin", ""), f"{parse_liq_reason(dbal[0]['reason'])}")

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
    # ĐỔI 2026-08-10: trước đây case này khẳng định TRC (ADV ~1,4 tỷ) KHÔNG bị loại. Sàn 2 tỷ
    # đảo đúng câu đó — giữ lại dưới dạng ngược để lần sau ai đọc log thấy ngay là CÓ CHỦ Ý.
    check("live: TRC (ADV ~1,44 tỷ < sàn 2 tỷ) BỊ LOẠI", "TRC" in names)
    kept_bad = [t for t in kept["ticker"] if t in set(names)]
    check("live: không mã nào vừa giữ vừa loại", not kept_bad, f"{kept_bad}")
    # bất biến thật của rổ giữ lại: mọi mã đều ≥ sàn (đo lại độc lập, không tin danh sách dropped)
    if len(kept):
        tl_k = ",".join(f"'{t}'" for t in sorted(set(kept["ticker"])))
        chk = bq(f"""SELECT MIN(t.Volume_3M_P50*COALESCE(t.Price,t.Close)) AS mn FROM (
  SELECT t.* FROM tav2_bq.ticker AS t WHERE t.ticker IN ({tl_k}) AND t.time <= DATE '{asof.date()}'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time DESC) = 1) AS t""")["mn"].iloc[0]
        check(f"live: min ADV của rổ giữ lại ≥ sàn ({float(chk)/1e9:.2f} tỷ)",
              float(chk) >= ADV_MIN_VND, f"min={chk}")

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
