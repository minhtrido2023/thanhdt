#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""basket_oshares_step_exdate_selfcheck.py — selfcheck cho chân WEIGHT của custom30V:
`OShares` phải BƯỚC tại EX-DATE, không phải tại NGÀY CÔNG BỐ QUÝ.
(job Taylor_20260927_043542 — xem khối WEIGHT LEG ở đầu `custom_basket.py`.)

Chạy (ĐỌC docstring trước khi "đơn giản hoá" bất cứ dòng nào):
  DNA_PYEXE=/home/trido/thanhdt/wc_venv/bin/python
  $DNA_PYEXE basket_oshares_step_exdate_selfcheck.py [--publish-diff]

Mọi kiểm tra về NGÀY đều chạy trên SNAPSHOT corp-action đã ghim
(`data/snapshots/corp_action_share_20260927.parquet`) chứ không đọc live: bảng
`tav2_bq.corporate_action` bị UPSERT IN-PLACE nên một selfcheck đọc live sẽ đổi kết quả theo ngày
chạy — đúng lớp lỗi "test phụ thuộc môi trường" của skill `verify-before-done`.

KHÔNG dùng `BQ_LOCAL_CACHE` mặc định của phiên: T3/T4 gọi `oshares_pit_grid` qua một `bq` DuckDB
trỏ THẲNG vào parquet đã ghim, nên kết quả không đổi khi cache của máy được sync lại.
"""
import os
import re
import sys

os.environ.setdefault("TZ", "")          # xem T9: không dòng nào ở đây được phụ thuộc TZ
WT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WT)

import duckdb                            # noqa: E402
import numpy as np                        # noqa: E402
import pandas as pd                       # noqa: E402

import custom_basket as cb                # noqa: E402

CANON = "/home/trido/thanhdt/WorkingClaude"
CA_SNAP = f"{CANON}/data/snapshots/corp_action_share_20260927.parquet"
FIN_PARQUET = f"{CANON}/data/bq_cache_asof20260729_postrestate/ticker_financial.parquet"
# Vòng review 2: cặp `expwexdate2_*` được sinh VỚI `BASKET_CA_SNAPSHOT` truyền vào (vòng 1 đọc
# live BQ — bảng đó bị UPSERT in-place nên claim "0/30 ở rebal 2026-08-05" không tái lập được).
PUB_Q = f"{CANON}/data/custom30v_8l_publish_expwexdate2_quarter.csv"
PUB_E = f"{CANON}/data/custom30v_8l_publish_expwexdate2_exdate.csv"

FAILS = []
N = [0]


def ck(name, cond, detail=""):
    N[0] += 1
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"   [{detail}]" if detail else ""))
    if not cond:
        FAILS.append(name)


def bq_pinned(sql):
    """`bq` đọc THẲNG parquet ticker_financial đã ghim — selfcheck không được phụ thuộc vào
    BQ_LOCAL_CACHE của máy (nó được sync lại hằng ngày). Cú pháp BigQuery -> DuckDB đi qua
    `bq_local_cache.BQLocalCache._translate`, cùng bộ dịch mà backtest dùng thật, để selfcheck
    không kiểm một phương ngữ SQL khác với production."""
    from bq_local_cache import BQLocalCache
    sql = BQLocalCache._translate(None, sql)     # also strips the `tav2_bq.` dataset prefix
    sql = re.sub(r"\bticker_financial\b", f"read_parquet('{FIN_PARQUET}')", sql)
    return duckdb.connect().execute(sql).df()


def basket_union(path=None):
    """Union mọi mã đã từng là thành viên custom30V (publish CSV) — 203 mã. Đọc từ CSV publish
    thay vì hardcode để tập mã không lệch khỏi cái `custom30_history.py` chạy thật."""
    path = path or f"{CANON}/data/custom30v_8l_publish.csv"
    return sorted(pd.read_csv(path, usecols=["ticker"])["ticker"].unique().tolist())


def fin_rows_many(tickers, since="2012-11-28"):
    """fin_rows cho NHIỀU mã trong MỘT query — 203 query duckdb riêng lẻ mất hàng phút."""
    inlist = ",".join(f"'{t}'" for t in tickers)
    d = bq_pinned(f"""SELECT ticker, time AS eff_date, OShares FROM tav2_bq.ticker_financial
        WHERE ticker IN ({inlist}) AND OShares IS NOT NULL AND time >= DATE '{since}'
        ORDER BY ticker, time""")
    d["eff_date"] = pd.to_datetime(d["eff_date"])
    return d


def fin_rows(ticker, since="2012-11-28"):
    """`since` mirrors oshares_pit_grid's own window (lo_date − 400 days for lo=2014-01-01);
    without it the level-set test compares the grid against 13 extra years of pre-2013 rows."""
    d = bq_pinned(f"""SELECT ticker, time AS eff_date, OShares FROM tav2_bq.ticker_financial
        WHERE ticker='{ticker}' AND OShares IS NOT NULL AND time >= DATE '{since}'
        ORDER BY time""")
    d["eff_date"] = pd.to_datetime(d["eff_date"])
    return d


# ---------------------------------------------------------------- T1: cái knob
def t1_knob():
    print("\nT1 — knob BASKET_OSHARES_STEP đọc tại CALL time, mặc định = exdate")
    old = os.environ.pop("BASKET_OSHARES_STEP", None)
    try:
        ck("mặc định (không set env) = exdate", cb.oshares_step_quarter() is False)
        for v, want in (("quarter", True), ("QUARTER", True), ("exdate", False),
                        ("ExDate", False), ("", False), ("bogus", False)):
            os.environ["BASKET_OSHARES_STEP"] = v
            ck(f"BASKET_OSHARES_STEP={v!r} -> quarter_mode={want}",
               cb.oshares_step_quarter() is want)
    finally:
        os.environ.pop("BASKET_OSHARES_STEP", None)
        if old is not None:
            os.environ["BASKET_OSHARES_STEP"] = old


# --------------------------------------------- T2: luật khớp sự kiện (đơn vị)
def t2_match_rule():
    print("\nT2 — _match_step_date: chỉ khớp khi CỠ khớp, không phải chỉ vì có sự kiện trong cửa sổ")
    ts = pd.Timestamp
    # price_adjusting is part of the real frame's schema (normalise_corp_action fills it), so the
    # synthetic frames carry it too — a stub missing a column tests a shape production never sees.
    ev = pd.DataFrame([
        dict(ticker="X", event_code="ISS", share_date=ts("2024-06-20"), exercise_ratio=1.0,
             shares_total_after=np.nan, price_adjusting=True),
        dict(ticker="X", event_code="ISS", share_date=ts("2024-03-01"), exercise_ratio=0.05,
             shares_total_after=np.nan, price_adjusting=True),
        dict(ticker="X", event_code="ISS", share_date=ts("2024-09-05"), exercise_ratio=0.02,
             shares_total_after=np.nan, price_adjusting=True),
        dict(ticker="X", event_code="ISS", share_date=ts("2024-09-05"), exercise_ratio=0.03,
             shares_total_after=np.nan, price_adjusting=True),
        dict(ticker="X", event_code="AIS", share_date=ts("2024-12-02"), exercise_ratio=np.nan,
             shares_total_after=2_000_000_000.0, price_adjusting=False),
        dict(ticker="X", event_code="ISS", share_date=ts("2025-03-11"), exercise_ratio=0.012,
             shares_total_after=np.nan, price_adjusting=False),      # ESOP: dated, not adjusting
    ])
    lo, hi = ts("2024-01-01"), ts("2025-01-01")
    d, how = cb._match_step_date(2.0, 2e9, lo, hi, ev)
    ck("ratio 2.0 -> ISS exercise_ratio=1.0 ngày 2024-06-20", (d == ts("2024-06-20"), how)[0]
       and how == "ISS_RATIO", how)
    d, how = cb._match_step_date(1.05, 1e9, lo, hi, ev)
    ck("ratio 1.05 -> đúng sự kiện 5% ngày 2024-03-01", d == ts("2024-03-01") and how == "ISS_RATIO", how)
    d, how = cb._match_step_date(1.05, 1e9, ts("2024-08-01"), hi, ev)
    ck("cùng ratio 1.05 nhưng chỉ còn 2 tranche 2%+3% cùng ngày -> ISS_RATIO_SUM",
       d == ts("2024-09-05") and how == "ISS_RATIO_SUM", how)
    d, how = cb._match_step_date(1.37, 2e9, ts("2024-11-01"), hi, ev)
    ck("không có ratio khớp nhưng AIS khớp MỨC -> AIS_LEVEL",
       d == ts("2024-12-02") and how == "AIS_LEVEL", how)
    d, how = cb._match_step_date(1.37, 9e9, ts("2024-11-01"), hi, ev)
    ck("AIS lệch mức >0,1% -> KHÔNG khớp (EVENT_BUT_NO_RATIO_MATCH)",
       d is None and how == "EVENT_BUT_NO_RATIO_MATCH", how)
    d, how = cb._match_step_date(1.5, 1e9, ts("2025-04-01"), ts("2025-06-01"), ev)
    ck("cửa sổ không có sự kiện nào -> NO_EVENT_IN_WINDOW",
       d is None and how == "NO_EVENT_IN_WINDOW", how)
    # dung sai 2% + 0,2pp: 0,15 vs 0,153 lọt, 0,15 vs 0,158 KHÔNG
    ev2 = pd.DataFrame([dict(ticker="X", event_code="ISS", share_date=ts("2025-07-21"),
                             exercise_ratio=0.15, shares_total_after=np.nan,
                             price_adjusting=True)])
    d, _ = cb._match_step_date(1.153, 1e9, ts("2025-04-01"), ts("2025-09-01"), ev2)
    ck("dung sai: mục tiêu 0,153 vs sự kiện 0,150 -> KHỚP", d == ts("2025-07-21"))
    d, _ = cb._match_step_date(1.158, 1e9, ts("2025-04-01"), ts("2025-09-01"), ev2)
    ck("dung sai: mục tiêu 0,158 vs sự kiện 0,150 -> KHÔNG khớp (fallback ngày quý)", d is None)
    # ISS KHÔNG điều chỉnh giá vẫn khớp BÌNH THƯỜNG (xem header "WHY NOT SPLIT ISS") — chỉ được
    # GẮN NHÃN. Đây là chốt chống hồi quy cho đúng cái lệch header/code của vòng review 2.
    d, how = cb._match_step_date(1.012, 1e9, ts("2025-01-01"), ts("2025-06-01"), ev)
    ck("ESOP (không điều chỉnh giá) VẪN khớp ex-date, nhãn mang hậu tố _NONADJ",
       d == ts("2025-03-11") and how == "ISS_RATIO_NONADJ", how)
    d, how = cb._match_step_date(2.0, 2e9, lo, hi, ev)
    ck("ISS điều chỉnh giá -> nhãn KHÔNG có hậu tố _NONADJ", how == "ISS_RATIO", how)


# ------------------------------- T2b: cổng PIT 3 — clamp theo public_date
def t2b_public_clamp():
    print("\nT2b — cổng PIT 3: share_date không bao giờ TRƯỚC public_date")
    ts = pd.Timestamp
    raw = pd.DataFrame([
        dict(ticker="X", share_date=ts("2024-05-10"), public_date=ts("2024-05-15")),   # công bố MUỘN
        dict(ticker="X", share_date=ts("2024-07-01"), public_date=ts("2024-06-20")),   # công bố TRƯỚC
        dict(ticker="X", share_date=ts("2024-08-01"), public_date=pd.NaT),             # thiếu -> giữ
    ])
    out = cb._clamp_share_date_to_public(raw.copy())
    ck("public_date SAU share_date -> dời tới public_date", out.share_date.iloc[0] == ts("2024-05-15"),
       str(out.share_date.iloc[0].date()))
    ck("public_date TRƯỚC share_date -> giữ nguyên", out.share_date.iloc[1] == ts("2024-07-01"))
    ck("public_date thiếu (NaT) -> giữ nguyên (fail-safe)", out.share_date.iloc[2] == ts("2024-08-01"))
    ck("IDEMPOTENT: clamp lần 2 không đổi gì",
       cb._clamp_share_date_to_public(out.copy()).share_date.equals(out.share_date))
    nopub = pd.DataFrame([dict(ticker="X", share_date=ts("2024-05-10"))])
    ck("thiếu CẢ CỘT public_date (vintage cũ) -> không lỗi, giữ nguyên",
       cb._clamp_share_date_to_public(nopub.copy()).share_date.iloc[0] == ts("2024-05-10"))
    # ĐỘT BIẾN: snapshot đã ghim PHẢI thực sự bị clamp khi đọc, nếu không cổng 3 là no-op im lặng
    ev = pd.read_parquet(CA_SNAP)
    ev["share_date"] = pd.to_datetime(ev["share_date"])
    pub = pd.to_datetime(ev["public_date"], errors="coerce")
    n = int((pub.notna() & (pub > ev["share_date"])).sum())
    ck("ĐỘT BIẾN: snapshot ghim CÓ dòng cần clamp (cổng 3 không phải no-op)", n > 0, f"{n} dòng")


# ------------------------------------- T3: ca thật, ĐÚNG ngày, ĐÚNG hướng
def t3_real_cases():
    print("\nT3 — ca thật trên snapshot đã ghim (cả hai HƯỚNG lệch)")
    os.environ["BASKET_CA_SNAPSHOT"] = CA_SNAP
    cb._CA_CACHE.clear()
    grid, rep = cb.oshares_pit_grid(bq_pinned, ["TCB", "ACB", "HPG", "FPT"],
                                    "2014-01-01", "2026-09-25")
    r = rep.set_index(["ticker", rep["quarter_date"].astype(str)])

    # (a) ca quant-skeptic nêu: TCB x2. Ngày quý 2024-07-22, ex-date thật 2024-06-20 => TRỄ 32 ngày.
    row = r.loc[("TCB", "2024-07-22")]
    ck("TCB x2: ngày hiệu lực dời về ex-date 2024-06-20",
       str(row["eff_date"].date()) == "2024-06-20" and int(row["moved_days"]) == 32,
       f"eff={row['eff_date'].date()} moved={row['moved_days']}")
    ck("TCB x2: tỷ lệ bước ĐÚNG 2.0 (không đổi MỨC, chỉ đổi NGÀY)",
       abs(float(row["ratio"]) - 2.0) < 1e-9, f"ratio={row['ratio']}")

    # (b) hướng NGƯỢC LẠI = look-ahead: dòng quý 2024-10-22 đã mang số CP của ESOP đi ex 11-30.
    # Ex-date vendor ghi 2024-11-30 nhưng public_date là 2024-12-03 ⇒ cổng PIT 3 dời tới ngày CÔNG
    # BỐ. ESOP không điều chỉnh giá ⇒ nhãn phải có hậu tố _NONADJ (không bị lọc bỏ — xem header).
    row = r.loc[("TCB", "2024-10-22")]
    ck("TCB ESOP: dời MUỘN tới public_date 2024-12-03 (bỏ look-ahead + cổng PIT 3)",
       str(row["eff_date"].date()) == "2024-12-03" and int(row["moved_days"]) == -42,
       f"eff={row['eff_date'].date()} moved={row['moved_days']}")
    ck("TCB ESOP: nhãn ghi rõ ISS không điều chỉnh giá (_NONADJ)",
       "_NONADJ" in str(row["match"]), str(row["match"]))

    # (c) ca KHÔNG khớp được -> PHẢI giữ ngày quý (fallback = hành vi hiện tại, không bịa ngày)
    row = r.loc[("FPT", "2025-07-22")]
    ck("FPT 2025-07-22 (cỡ không khớp sự kiện nào) -> GIỮ ngày quý",
       str(row["eff_date"].date()) == "2025-07-22" and int(row["moved_days"]) == 0
       and "KEEP_QUARTER" in row["match"], f"{row['match']} eff={row['eff_date'].date()}")

    # (d) bất biến cấu trúc: MỨC không bao giờ bị đổi, chỉ NGÀY
    for tk in ("TCB", "ACB", "HPG", "FPT"):
        got = sorted(grid.loc[grid.ticker == tk, "OShares"].unique().tolist())
        want = sorted(fin_rows(tk)["OShares"].unique().tolist())
        ck(f"{tk}: tập MỨC OShares y nguyên (chỉ NGÀY đổi)", got == want,
           f"{len(got)} vs {len(want)} mức")

    # (e) cổng PIT 1: không bước nào dời về TRƯỚC/ĐÚNG ngày dòng quý liền trước
    bad = []
    for tk, g in grid.groupby("ticker"):
        q = fin_rows(tk)
        for _, s in rep[rep.ticker == tk].iterrows():
            prev_q = q.loc[q.eff_date < s["quarter_date"], "eff_date"].max()
            if pd.notna(prev_q) and s["eff_date"] <= prev_q:
                bad.append((tk, str(s["quarter_date"].date()), str(s["eff_date"].date())))
    ck("cổng PIT 1: không có bước nào dời tới/qua ngày dòng quý TRƯỚC đó", not bad, str(bad[:3]))

    # (f) cổng PIT 2 + merge_asof: eff_date tăng ngặt theo từng mã
    bad = [tk for tk, g in grid.groupby("ticker")
           if not g["eff_date"].is_monotonic_increasing or g["eff_date"].duplicated().any()]
    ck("cổng PIT 2: eff_date tăng NGẶT trong từng mã", not bad, str(bad))


# ------------------- T4: hành vi trên frame NGÀY — bất biến quan trọng nhất
def t4_daily_frame():
    """Chạy trên TOÀN BỘ union 203 mã từng vào rổ, không phải 4 mã mẫu (mở rộng vòng review 2,
    2026-09-27): đây là CỔNG MERGE — "ngoài cửa sổ dời thì byte-identical" chỉ có giá trị khi đo
    trên đúng tập mã mà `custom30_history.py` sẽ chạy thật."""
    tks = basket_union()
    print(f"\nT4 — apply_oshares trên frame NGÀY, TOÀN BỘ union {len(tks)} mã "
          f"(ngày KHÔNG có sự kiện phải Y NGUYÊN)")
    os.environ["BASKET_CA_SNAPSHOT"] = CA_SNAP
    cb._CA_CACHE.clear()
    grid, rep = cb.oshares_pit_grid(bq_pinned, tks, "2014-01-01", "2026-09-25")
    days = pd.bdate_range("2014-01-02", "2026-09-25")
    bx0 = pd.DataFrame([(t, d) for t in tks for d in days], columns=["ticker", "time"])
    # nạp OShares theo đúng cách SQL của build/build_pit: t.time >= f.time (ngày CÔNG BỐ quý)
    fin = fin_rows_many(tks).rename(columns={"eff_date": "time"})
    bx0 = pd.merge_asof(bx0.sort_values("time"), fin.sort_values("time"),
                        on="time", by="ticker", direction="backward")
    bx0["Close"] = 10.0
    bx0["pxw"] = 10.0
    # build()/build_pit() both hand `bx` over sorted by (ticker, time). The legacy fill's `bfill()`
    # is NOT grouped, so its result DEPENDS on that row order — feeding a time-sorted frame here
    # would test a fill that production never performs (found by this very check, first run).
    bx0 = bx0.sort_values(["ticker", "time"]).reset_index(drop=True)

    os.environ["BASKET_OSHARES_STEP"] = "quarter"
    bq_, _ = cb.apply_oshares(bq_pinned, bx0.copy(), tks)
    os.environ["BASKET_OSHARES_STEP"] = "exdate"
    cb._CA_CACHE.clear()
    os.environ["BASKET_CA_SNAPSHOT"] = CA_SNAP
    be_, _ = cb.apply_oshares(bq_pinned, bx0.copy(), tks)

    key = ["ticker", "time"]
    m = bq_[key + ["OShares"]].merge(be_[key + ["OShares"]], on=key, suffixes=("_q", "_e"))
    ck("không mất/không thêm dòng nào", len(m) == len(bx0) == len(bq_) == len(be_),
       f"{len(m)}/{len(bx0)}")
    ck("mặt nạ valid (OShares NaN) Y NGUYÊN giữa 2 chế độ",
       m["OShares_q"].isna().equals(m["OShares_e"].isna()),
       f"NaN q={int(m.OShares_q.isna().sum())} e={int(m.OShares_e.isna().sum())}")

    diff = m[(m.OShares_q != m.OShares_e) & m.OShares_q.notna() & m.OShares_e.notna()]
    # Tập ngày LỆCH phải ĐÚNG BẰNG hợp của các cửa sổ [min(eff,quý), max(eff,quý)) của bước ĐÃ DỜI
    want = set()
    for _, s in rep[rep.moved_days != 0].iterrows():
        a, b = sorted([s["eff_date"], s["quarter_date"]])
        for d in days[(days >= a) & (days < b)]:
            want.add((s["ticker"], d))
    got = set(zip(diff["ticker"], diff["time"]))
    ck("ngày LỆCH == đúng hợp các cửa sổ dời (không rò ra ngoài một ngày nào)", got == want,
       f"got {len(got)} want {len(want)} chỉ-got {len(got - want)} chỉ-want {len(want - got)}")
    ck("ngoài các cửa sổ đó: OShares (và do đó mcapw) BYTE-IDENTICAL",
       len(m) - len(diff) == len(m) - len(want), f"{len(m) - len(diff)} ngày giống nhau")

    # trong cửa sổ, tỷ số giữa 2 chế độ phải ĐÚNG bằng ratio của bước (không phải "gần bằng")
    bad = []
    for _, s in rep[rep.moved_days != 0].iterrows():
        a, b = sorted([s["eff_date"], s["quarter_date"]])
        w = diff[(diff.ticker == s["ticker"]) & (diff.time >= a) & (diff.time < b)]
        if not len(w):
            continue
        # dời SỚM hơn (moved>0): trong cửa sổ, exdate đã mang số MỚI, quarter còn số CŨ.
        exp = s["ratio"] if s["moved_days"] > 0 else 1.0 / s["ratio"]
        got_r = (w.OShares_e / w.OShares_q).unique()
        if len(got_r) != 1 or abs(got_r[0] - exp) > 1e-9:
            bad.append((s["ticker"], str(s["quarter_date"].date()), list(got_r)[:2], exp))
    ck("trong cửa sổ: OShares_exdate/OShares_quarter == ĐÚNG tỷ lệ của bước", not bad, str(bad[:3]))

    # chế độ quarter phải tái lập ĐÚNG dòng code trước khi sửa (ffill+bfill của join SQL)
    ref = bx0.sort_values(["ticker", "time"]).copy()
    ref["OShares"] = ref.groupby("ticker")["OShares"].ffill().bfill()
    r2 = bq_.sort_values(["ticker", "time"])
    ck("chế độ 'quarter' == dòng gốc trước khi sửa (ffill().bfill()), byte-identical",
       np.array_equal(ref["OShares"].to_numpy(), r2["OShares"].to_numpy(), equal_nan=True))

    # ĐỘT BIẾN: hai chế độ PHẢI khác nhau ở đâu đó, nếu không bản vá là no-op im lặng (§29)
    ck("ĐỘT BIẾN: hai chế độ thực sự KHÁC nhau (bản vá không phải no-op)", len(diff) > 0,
       f"{len(diff)} ngày lệch")


# ----------------------------- T5: diff publish CSV — từng tên, hai chế độ
def t5_publish_diff():
    print("\nT5 — diff publish CSV (đường tiền LIVE): liệt kê TỪNG TÊN đổi weight")
    if not (os.path.exists(PUB_Q) and os.path.exists(PUB_E)):
        ck("có cả 2 publish CSV để diff", False, "chạy custom30_history.py 2 chế độ trước")
        return
    q = pd.read_csv(PUB_Q)
    e = pd.read_csv(PUB_E)
    ck("THÀNH VIÊN rổ không đổi (selection không dùng OShares)",
       q[["rebal_date", "ticker", "liq_rank"]].equals(e[["rebal_date", "ticker", "liq_rank"]]))
    m = q.merge(e, on=["rebal_date", "ticker"], suffixes=("_q", "_e"))
    m["dw"] = m.weight_e - m.weight_q
    ck("tổng weight mỗi rebal vẫn = 1 ở CẢ HAI chế độ",
       bool(np.allclose(m.groupby("rebal_date").weight_q.sum(), 1.0, atol=2e-6))
       and bool(np.allclose(m.groupby("rebal_date").weight_e.sum(), 1.0, atol=2e-6)))
    ch = m[m.dw.abs() > 1e-9]
    same = sorted(set(m.rebal_date) - set(ch.rebal_date))
    print(f"    {ch.rebal_date.nunique()}/{m.rebal_date.nunique()} rebal đổi weight; "
          f"{len(same)} rebal BYTE-IDENTICAL")
    for rd, g in ch.groupby("rebal_date"):
        g = g.reindex(g.dw.abs().sort_values(ascending=False).index)
        top = ", ".join(f"{r.ticker} {r.dw * 100:+.3f}pp" for r in list(g.itertuples())[:4])
        print(f"      {rd}: {len(g)} tên, sum|dw| {g.dw.abs().sum()*100:.3f}pp | {top}")
    cur = m[m.rebal_date == m.rebal_date.max()]
    print(f"    REBAL HIỆN TẠI {cur.rebal_date.iloc[0]}: "
          f"{int((cur.dw.abs() > 1e-9).sum())}/{len(cur)} tên đổi, "
          f"max |dw| {cur.dw.abs().max()*100:.4f}pp")
    ck("mọi thay đổi weight đều bị chặn trên bởi trần 10% (không tên nào vượt cap)",
       float(m.weight_e.max()) <= 0.10 + 1e-9, f"max weight_e={m.weight_e.max():.6f}")


# ------------- T6: lỗi TIỀM ẨN CŨ mà T4 phát hiện — `bfill()` KHÔNG group theo mã
def t6_ungrouped_bfill():
    """Dòng gốc `bx.groupby("ticker")["OShares"].ffill().bfill()`: `.ffill()` có group, `.bfill()`
    thì KHÔNG (nó chạy trên Series kết quả). Với frame sắp theo (ticker,time), NaN ở ĐẦU một mã vẫn
    được lấp đúng bằng số của chính mã đó (hàng kế tiếp theo thứ tự là của mã đó) — nên lỗi này
    LẶNG. Nó chỉ cắn khi một mã KHÔNG CÓ dòng OShares nào: cả group là NaN, `.bfill()` ngoài group
    lấp bằng số của MÃ KẾ TIẾP theo thứ tự — trái đúng câu header "a name with no OShares row at
    all is excluded exactly as before".
    Chân `exdate` dùng `groupby(...).bfill()` (có group) nên KHÔNG có đường rò này. Kiểm ở đây để
    (1) ghim hành vi, (2) chứng minh hướng sửa, (3) đo xem nó có cắn thật trên rổ hay không."""
    print("\nT6 — lỗi tiềm ẩn CŨ: bfill() không group (ngoài phạm vi ticket, ghim lại để không mất)")
    bx = pd.DataFrame({
        "ticker": ["AAA"] * 3 + ["BBB"] * 3,
        "time": list(pd.bdate_range("2020-01-01", periods=3)) * 2,
        "OShares": [np.nan, np.nan, np.nan, 1e9, 1e9, 1e9],
    })
    legacy = bx.groupby("ticker")["OShares"].ffill().bfill()
    ck("tái hiện lỗi cũ: mã AAA (không có dòng nào) bị lấp bằng số của BBB",
       bool((legacy.iloc[:3] == 1e9).all()), f"AAA -> {legacy.iloc[0]}")
    grouped = bx.groupby("ticker")["OShares"].ffill().groupby(bx["ticker"]).bfill()
    ck("hướng sửa (bfill CÓ group): AAA vẫn NaN -> vẫn bị mặt nạ valid loại ra",
       bool(grouped.iloc[:3].isna().all()))


def main():
    print(f"custom_basket = {cb.__file__}")
    print(f"corp-action snapshot = {CA_SNAP}")
    print(f"TZ = {os.environ.get('TZ', '<unset>')!r}")
    t1_knob()
    t2_match_rule()
    t2b_public_clamp()
    t3_real_cases()
    t4_daily_frame()
    t5_publish_diff()
    t6_ungrouped_bfill()
    print(f"\n==== {N[0] - len(FAILS)}/{N[0]} PASS ====")
    if FAILS:
        print("FAILED: " + "; ".join(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
