#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oshares_step_vs_exdate_measure.py — BƯỚC 0 của TICKET 1 (job Taylor_20260927_043542).

ĐO TRƯỚC KHI SỬA: mọi (mã, khoảng ngày) 2014-2026 mà `ticker_financial.OShares` — chân WEIGHT
của custom_basket (`mcapw = COALESCE(Price,Close) x OShares`) — BƯỚC tại NGÀY QUÝ
(= `ticker_financial.time`, đo được bằng `Release_Date`) thay vì tại EX-DATE thật.

Nguồn sự thật ex-date: `tav2_bq.corporate_action` qua semantics `corp_action_lib.pricing_events`
(`event_status != "not_executed"`), codes ISS + AIS. Nguồn thứ 2 (ĐỐI CHIẾU, không phải sự thật):
`data/fiinprox_oshares_pit_20260926.csv` (registry status UNVERIFIED-PIT, trượt ngưỡng ±3 phiên
85,7%/89,2% — xem fundamentals/fiinprox_oshares_pit.md).

KHÔNG sửa gì. Chỉ in + ghi CSV.
"""
import os
import sys
from datetime import date, timedelta

import duckdb
import pandas as pd

WT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WT)
import corp_action_lib as cal  # noqa: E402

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/oshares_weight_exdate_20260927"
CANON = "/home/trido/thanhdt/WorkingClaude"
PINNED_CACHE = f"{CANON}/data/bq_cache_asof20260729_postrestate/ticker_financial.parquet"
LIVE_CACHE = f"{CANON}/data/bq_cache/ticker_financial.parquet"
PUBLISH = f"{CANON}/data/custom30v_8l_publish.csv"
FIINPROX = f"{CANON}/mike/data/fiinprox_oshares_pit_20260926.csv"
START, END = date(2013, 1, 1), date(2026, 12, 31)


def oshares_steps(parquet_path, tickers):
    """Steps as custom_basket SEES them: the join is t.time >= fin.ftime, so a quarterly row's
    OShares becomes effective on that row's own `time`. A step = row whose OShares differs from
    the previous (non-null) row of the same ticker."""
    tk = ",".join(f"'{t}'" for t in tickers)
    con = duckdb.connect()
    df = con.execute(f"""
        SELECT ticker, CAST(time AS DATE) qtime, OShares
        FROM read_parquet('{parquet_path}')
        WHERE ticker IN ({tk}) AND OShares IS NOT NULL
          AND time BETWEEN DATE '{START}' AND DATE '{END}'
        ORDER BY ticker, time""").df()
    df["qtime"] = pd.to_datetime(df["qtime"]).dt.date
    df = df.sort_values(["ticker", "qtime"])
    df["prev_os"] = df.groupby("ticker")["OShares"].shift()
    df["prev_qtime"] = df.groupby("ticker")["qtime"].shift()
    st = df[df["prev_os"].notna() & (df["OShares"] != df["prev_os"])].copy()
    st["ratio"] = st["OShares"] / st["prev_os"]
    return st.reset_index(drop=True)


def load_events(tickers):
    rows = []
    B = 60
    for i in range(0, len(tickers), B):
        rows += cal._events(tickers[i:i + B], None, None, ("ISS", "AIS"),
                            'event_status != "not_executed"')
    ev = pd.DataFrame(rows)
    for c in ("exright_date", "effective_date", "public_date"):
        ev[c] = pd.to_datetime(ev[c], errors="coerce").dt.date
    for c in ("exercise_ratio", "shares_delta", "shares_total_after"):
        ev[c] = pd.to_numeric(ev[c], errors="coerce")
    # share-date = the day the SHARE COUNT of a cap-weight index should step.
    #   price-adjusting ISS (stock div / bonus / rights to existing holders) -> exright_date:
    #     the price is diluted that day, so the share count must rise the same day or the market
    #     cap collapses by the ratio for the gap.  (corp_action_lib.PRICE_ADJUSTING_ISS)
    #   non-accruing ISS (ESOP / placement / conversion) -> no price step; shares enter on the
    #     additional-listing date, which is the AIS row, so leave the ISS row's own date as a
    #     fallback only.
    #   AIS -> effective_date (registry: `shares_total_after` only populated here).
    # NaN -> "" : corp_action_lib.is_price_adjusting does `(x or "").strip()`, and a pandas NaN
    # is a float that passes `or` but has no .strip(). Normalise here, don't patch the shared lib.
    ev["issue_method_name_vi"] = ev["issue_method_name_vi"].fillna("")
    ev["adj"] = ev.apply(lambda r: cal.is_price_adjusting(r.to_dict()), axis=1)
    def _share_date(r):
        # .dt.date leaves missing values as NaT/NaN floats, so test with pd.isna — `x or y`
        # mis-handles both and a mixed date/float column then breaks every comparison.
        if r["event_code"] == "ISS":
            d = r["exright_date"]
        else:
            d = r["effective_date"]
            if pd.isna(d):
                d = r["exright_date"]
        return None if pd.isna(d) else d

    ev["share_date"] = ev.apply(_share_date, axis=1)
    return ev


def match_step(row, ev_t):
    """Find the event(s) that explain a step. Returns (true_date, how, detail)."""
    q, p, ratio, new = row["qtime"], row["prev_qtime"], row["ratio"], row["OShares"]
    lo = (p - timedelta(days=30)) if pd.notna(p) else q - timedelta(days=200)
    hi = q + timedelta(days=45)
    c = ev_t[(ev_t["share_date"].notna()) & (ev_t["share_date"] > lo) & (ev_t["share_date"] <= hi)]
    if c.empty:
        return None, "NO_EVENT_IN_WINDOW", ""
    # 1) AIS level match — the exact ground truth when it exists.
    a = c[(c["event_code"] == "AIS") & c["shares_total_after"].notna()]
    a = a[(a["shares_total_after"] - new).abs() / new <= 0.001]
    # 2) ISS ratio match (single tranche, then same-day sum of tranches).
    iss = c[(c["event_code"] == "ISS") & c["exercise_ratio"].notna() & (c["exercise_ratio"] > 0)]
    tgt = ratio - 1.0
    hit_iss = iss[(iss["exercise_ratio"] - tgt).abs() <= 0.02 * abs(tgt) + 0.002]
    if hit_iss.empty and not iss.empty:
        g = iss.groupby("share_date")["exercise_ratio"].sum()
        g = g[(g - tgt).abs() <= 0.02 * abs(tgt) + 0.002]
        if len(g):
            d = g.index.min()
            return d, "ISS_RATIO_SUM", f"sum_ratio={g.iloc[0]:.6f} vs target={tgt:.6f}"
    if not hit_iss.empty:
        d = hit_iss["share_date"].min()
        r = hit_iss.iloc[0]
        return d, "ISS_RATIO", f"{r['issue_method_name_vi']} ratio={r['exercise_ratio']:.6f} vs {tgt:.6f}"
    if not a.empty:
        d = a["share_date"].min()
        return d, "AIS_LEVEL", f"shares_total_after={a.iloc[0]['shares_total_after']:.0f}"
    return None, "EVENT_BUT_NO_RATIO_MATCH", f"n_cand={len(c)} target={tgt:.6f}"


def main():
    pub = pd.read_csv(PUBLISH)
    tickers = sorted(pub["ticker"].dropna().unique().tolist())
    print(f"[universe] {len(tickers)} mã đã từng vào rổ custom30V (nguồn {PUBLISH})")

    ev = load_events(tickers)
    print(f"[corp_action] {len(ev)} dòng ISS+AIS (status != not_executed), "
          f"{ev['ticker'].nunique()} mã, share_date {ev['share_date'].dropna().min()}→{ev['share_date'].dropna().max()}")

    fx = pd.read_csv(FIINPROX)
    fx["date"] = pd.to_datetime(fx["date"]).dt.date
    fx = fx[fx["flags"].fillna("").str.contains("first_obs") == False]  # noqa: E712

    for tag, path in (("pinned_postrestate", PINNED_CACHE), ("live_bqcache", LIVE_CACHE)):
        st = oshares_steps(path, tickers)
        st = st[st["qtime"] >= date(2014, 1, 1)].reset_index(drop=True)
        recs = []
        for _, r in st.iterrows():
            ev_t = ev[ev["ticker"] == r["ticker"]]
            td, how, detail = match_step(r, ev_t)
            lag = (r["qtime"] - td).days if td else None
            # fiinprox second source
            fxt = fx[fx["ticker"] == r["ticker"]].copy()
            fxd = None
            if len(fxt):
                fxt["rr"] = fxt["shares"] / (fxt["shares"] - fxt["delta"].fillna(0))
                cand = fxt[(fxt["rr"] - r["ratio"]).abs() <= 0.02 * abs(r["ratio"] - 1) + 0.002]
                cand = cand[(cand["date"] > r["qtime"] - timedelta(days=240)) &
                            (cand["date"] <= r["qtime"] + timedelta(days=45))]
                if len(cand):
                    fxd = cand["date"].min()
            recs.append(dict(ticker=r["ticker"], prev_qtime=r["prev_qtime"], qtime=r["qtime"],
                             oshares_old=r["prev_os"], oshares_new=r["OShares"],
                             ratio=round(r["ratio"], 6), true_date=td, match=how,
                             lag_days=lag, detail=detail, fiinprox_date=fxd,
                             fiinprox_lag=(r["qtime"] - fxd).days if fxd else None))
        out = pd.DataFrame(recs)
        f = f"{OUT}/steps_{tag}.csv"
        out.to_csv(f, index=False)
        m = out[out["lag_days"].notna()]
        print(f"\n===== VINTAGE {tag} =====  ({len(out)} bước OShares, {out['ticker'].nunique()} mã)")
        print("match breakdown:\n" + out["match"].value_counts().to_string())
        if len(m):
            print(f"\nlag_days (qtime - true_date) trên {len(m)} bước khớp được sự kiện:")
            print(m["lag_days"].describe(percentiles=[.05, .25, .5, .75, .95]).to_string())
            print(f"  lag == 0 (đúng ngày)      : {(m['lag_days'] == 0).sum()}")
            print(f"  lag  > 0 (quarter TRỄ)    : {(m['lag_days'] > 0).sum()}   "
                  f"median {m.loc[m['lag_days'] > 0, 'lag_days'].median()} ngày")
            print(f"  lag  < 0 (quarter SỚM=LA) : {(m['lag_days'] < 0).sum()}   "
                  f"min {m['lag_days'].min()}")
            big = m[(m["ratio"] - 1).abs() >= 0.05]
            print(f"\n  bước |ratio-1| >= 5%: {len(big)}; lệch ngày median "
                  f"{big['lag_days'].median()}, |lag| max {big['lag_days'].abs().max()}")
        fxm = out[out["fiinprox_lag"].notna() & out["lag_days"].notna()]
        if len(fxm):
            agree = (fxm["fiinprox_date"] == fxm["true_date"]).sum()
            print(f"\n  đối chiếu FiinProX (nguồn 2): {len(fxm)} bước có cả hai; "
                  f"cùng ngày {agree} ({agree/len(fxm)*100:.1f}%), "
                  f"|lệch| median {(fxm['fiinprox_date'] - fxm['true_date']).apply(lambda d: abs(d.days)).median()} ngày")
        print(f"  -> {f}")


if __name__ == "__main__":
    main()
