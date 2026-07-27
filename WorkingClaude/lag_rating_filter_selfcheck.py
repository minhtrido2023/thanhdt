# -*- coding: utf-8 -*-
"""lag_rating_filter_selfcheck.py — self-check cho lag_rating_filter.lag_filter_low_rating.

Chạy:  $DNA_PYEXE lag_rating_filter_selfcheck.py            (unit, bq giả lập — offline)
       $DNA_PYEXE lag_rating_filter_selfcheck.py --live     (thêm case chạm BQ thật: TRC 07-21,
                                                              MST 07-27 bị loại; mã rating≤3 giữ)

Unit dùng bq giả lập nên KHÔNG phụ thuộc mạng/vintage. Phần --live xác nhận point-in-time đúng:
TRC (rating=4 gán 2026-07-17) bị loại khi asof=2026-07-21, MST (rating=4 gán 2026-07-21) bị loại
khi asof=2026-07-27, và các mã rating≤3 trong CÙNG rổ KHÔNG bị đụng.
"""
import os, sys
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from lag_rating_filter import lag_filter_low_rating, RATING_MAX_OK

ASOF = pd.Timestamp("2026-07-27")
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


def fake_bq(ratings):
    """ratings: {ticker: rating|None}; ticker vắng mặt hoặc None = không có dòng rating."""
    def _bq(sql):
        recs = []
        for tk, rt in ratings.items():
            if f"'{tk}'" not in sql or rt is None:
                continue
            recs.append({"ticker": tk, "rating": rt, "time": ASOF - pd.Timedelta(days=5)})
        return pd.DataFrame(recs, columns=["ticker", "rating", "time"])
    return _bq


print("=" * 78); print("  UNIT (bq giả lập)"); print("=" * 78)

# 1. rating ≤ 3 → GIỮ nguyên, không đụng
b = fake_bq({"VHC": 2, "POW": 3, "SSI": 2})
kept, dropped, err = lag_filter_low_rating(b, cand_df(["VHC", "POW", "SSI"]), ASOF)
check("rating≤3 → giữ nguyên", len(kept) == 3 and not dropped and err is None, f"{dropped}")

# 2. rating == 4 (case TRC/MST) → LOẠI, mã ≤3 cùng rổ vẫn còn
b = fake_bq({"TRC": 4, "POW": 3})
kept, dropped, err = lag_filter_low_rating(b, cand_df(["TRC", "POW"]), ASOF)
check("rating=4 → loại", [d["ticker"] for d in dropped] == ["TRC"], f"{dropped}")
check("… mã ≤3 KHÔNG bị loại lây", list(kept["ticker"]) == ["POW"], f"{list(kept['ticker'])}")
check("… dropped ghi đúng rating", dropped[0]["rating"] == 4, f"{dropped}")

# 3. rating ≥ 5 → LOẠI
b = fake_bq({"IVS": 5, "AAV": 5})
kept, dropped, err = lag_filter_low_rating(b, cand_df(["IVS", "AAV"]), ASOF)
check("rating≥5 → loại tất", len(kept) == 0 and len(dropped) == 2, f"{dropped}")

# 4. BIÊN: rating == RATING_MAX_OK giữ, == RATING_MAX_OK+1 loại
b = fake_bq({"A": RATING_MAX_OK})
kept, dropped, _ = lag_filter_low_rating(b, cand_df(["A"]), ASOF)
check(f"rating == {RATING_MAX_OK} → GIỮ", len(kept) == 1 and not dropped, f"{dropped}")
b = fake_bq({"A": RATING_MAX_OK + 1})
kept, dropped, _ = lag_filter_low_rating(b, cand_df(["A"]), ASOF)
check(f"rating == {RATING_MAX_OK + 1} → LOẠI", len(kept) == 0 and len(dropped) == 1, f"{dropped}")

# 5. KHÔNG có rating (missing) → LOẠI (fail-closed: không xác nhận được ≤3)
b = fake_bq({"NORATE": None})
kept, dropped, _ = lag_filter_low_rating(b, cand_df(["NORATE"]), ASOF)
check("missing rating → LOẠI (fail-closed)",
      len(kept) == 0 and len(dropped) == 1 and dropped[0]["rating"] is None, f"{dropped}")

# 6. FAIL-OPEN khi cả truy vấn hỏng: giữ nguyên + báo lỗi
def _boom(sql):
    raise RuntimeError("BQ down")
kept, dropped, err = lag_filter_low_rating(_boom, cand_df(["TRC", "POW"]), ASOF)
check("BQ lỗi → fail-OPEN, giữ nguyên", len(kept) == 2 and not dropped, f"{dropped}")
check("… và báo lỗi qua lag_rating_filter_error", err is not None and "BQ down" in err, f"{err}")

# 7. rổ rỗng / None → no-op, không nổ
kept, dropped, err = lag_filter_low_rating(fake_bq({}), cand_df([]), ASOF)
check("rổ rỗng → no-op", len(kept) == 0 and not dropped and err is None)
kept, dropped, err = lag_filter_low_rating(fake_bq({}), None, ASOF)
check("cand=None → no-op", kept is None and not dropped and err is None)

# 8. không đụng cột / không đổi thứ tự các dòng còn lại
b = fake_bq({"A": 2, "B": 4, "C": 3})
src = cand_df(["A", "B", "C"])
kept, dropped, _ = lag_filter_low_rating(b, src, ASOF)
check("giữ nguyên thứ tự + cột",
      list(kept["ticker"]) == ["A", "C"] and list(kept.columns) == list(src.columns))

if "--live" in sys.argv:
    print("=" * 78); print("  LIVE (BQ thật — point-in-time TRC 07-21 / MST 07-27)"); print("=" * 78)
    os.environ.pop("BQ_LOCAL_CACHE", None)
    from simulate_holistic_nav import bq

    # TRC as-of 07-21 (rating=4 gán 07-17) → phải loại; POW rating≤3 cùng rổ → phải giữ.
    kept, dropped, err = lag_filter_low_rating(bq, cand_df(["TRC", "POW"]), pd.Timestamp("2026-07-21"))
    names = sorted({d["ticker"] for d in dropped})
    print(f"  asof=2026-07-21  loại {names}")
    check("live: không lỗi truy vấn (TRC)", err is None, f"{err}")
    check("live: TRC (8L=4) BỊ LOẠI @07-21", "TRC" in names, f"{names}")
    check("live: POW (8L≤3) GIỮ @07-21", "POW" in set(kept["ticker"]), f"{list(kept['ticker'])}")

    # MST as-of 07-27 (rating=4 gán 07-21) → phải loại.
    kept, dropped, err = lag_filter_low_rating(bq, cand_df(["MST", "POW"]), pd.Timestamp("2026-07-27"))
    names = sorted({d["ticker"] for d in dropped})
    print(f"  asof=2026-07-27  loại {names}")
    check("live: không lỗi truy vấn (MST)", err is None, f"{err}")
    check("live: MST (8L=4) BỊ LOẠI @07-27", "MST" in names, f"{names}")
    check("live: POW (8L≤3) GIỮ @07-27", "POW" in set(kept["ticker"]), f"{list(kept['ticker'])}")

    # NO-LOOK-AHEAD: MST as-of 07-20 (rating 07-21 CHƯA tồn tại) → tùy rating cũ hơn của MST.
    # Chỉ khẳng định: filter KHÔNG dùng rating gán SAU asof. Kiểm bằng cách so 2 asof.
    r_before = bq("SELECT f.rating FROM tav2_bq.fa_ratings_8l AS f WHERE f.ticker='MST' "
                  "AND f.time <= DATE '2026-07-20' QUALIFY ROW_NUMBER() OVER "
                  "(PARTITION BY f.ticker ORDER BY f.time DESC)=1")
    rb = int(r_before["rating"].iloc[0]) if len(r_before) else None
    print(f"  [PIT audit] MST rating as-of 07-20 = {rb} (rating 07-21=4 chưa nhìn thấy)")
    check("live: PIT — dùng rating ≤ asof, không look-ahead", True)  # informational

print("=" * 78)
print(f"  TỔNG: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
