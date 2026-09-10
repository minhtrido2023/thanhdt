# -*- coding: utf-8 -*-
"""hit_details.py — audit tool (Kaffa-style "Hit Details"): for each BAL/LAG ticker that
landed in today's golive_v23_recommendations CSV, print the FORMULA that fired + the real
factor VALUES behind it. Pure observability — does NOT change any filter/order logic.
Context: mike/kb/projects/kaffa-comparison-20260910.md ("Hit Details", item #1).

BAL formula source of truth: signal_v11_sql.py (SIGNAL_V11's `ta` CASE list, lines 66-89).
This script re-derives each term in Python from freshly-fetched raw columns and SELF-CHECKS
the sum against the `ta` already written to the recs CSV by production — a mismatch means
signal_v11_sql.py changed and this file's transcription is stale (flagged loudly, not hidden).

LAG formula: reuses lag_live_schedule.live_lag_candidates() AS-IS (same function production
calls) — no re-derivation, so no duplicate-formula risk on that side.

Usage: python3 hit_details.py [DATE]   (default: latest golive_v23_recommendations_*.csv)
Output: data/hit_details_<DATE>.md
"""
import os, sys, glob, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.pop("BQ_LOCAL_CACHE", None)   # same reasoning as golive_recommend_v23.py: read live

import numpy as np, pandas as pd
from simulate_holistic_nav import bq
from lag_live_schedule import live_lag_candidates, NP_R_MIN, PRIOR_N_MIN, PA_HL3_MIN

OUTDIR = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out")
DATADIR = os.path.join(WORKDIR, "data")

# ---------------------------------------------------------------------------
# BAL: raw factor columns needed by the `ta` CASE list (signal_v11_sql.py:66-89)
# ---------------------------------------------------------------------------
BAL_COLS = ["Close", "D_RSI", "MA20", "MA50", "MA200", "MA50_T1", "Close_T1", "Volume",
            "Volume_3M_P50", "D_MACDdiff", "D_RSI_Max1W", "HI_3M_T1", "ID_HI_3Y",
            "PE", "PE_MA5Y", "PE_SD5Y", "FSCORE", "NP_P0", "NP_P1", "NP_P4", "ICB_Code"]


def fetch_bal_raw(tickers, date):
    if not tickers:
        return pd.DataFrame()
    tl = ",".join(f"'{t}'" for t in sorted(set(tickers)))
    cols = ",".join(f"t.{c}" for c in BAL_COLS)
    df = bq(f"""
        SELECT t.ticker, {cols} FROM tav2_bq.ticker AS t
        WHERE t.ticker IN ({tl}) AND t.time = DATE '{date}'
        UNION ALL
        SELECT t.ticker, {cols} FROM tav2_bq.ticker_1m AS t
        WHERE t.ticker IN ({tl}) AND t.time = DATE '{date}'
          AND NOT EXISTS (SELECT 1 FROM tav2_bq.ticker AS x
                           WHERE x.ticker = t.ticker AND x.time = t.time)
    """)
    if df.empty:
        return df
    fa = bq(f"""
        SELECT f.ticker, f.tier AS fa_tier FROM tav2_bq.fa_ratings AS f
        WHERE f.ticker IN ({tl}) AND f.time <= DATE '{date}'
        QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1
    """)
    df = df.merge(fa, on="ticker", how="left")
    r8 = bq(f"""
        SELECT f.ticker, f.rating FROM tav2_bq.fa_ratings_8l AS f
        WHERE f.ticker IN ({tl})
        QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1
    """)
    df = df.merge(r8, on="ticker", how="left")
    # VNINDEX rsi_max3m: same window definition as signal_v11_sql.py's vni_max3m (60-session
    # rolling max of VNINDEX D_RSI, as of `date`). Single value shared across all tickers.
    vni = bq(f"""
        SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t
        WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL AND t.time <= DATE '{date}'
        ORDER BY t.time DESC LIMIT 60
    """)
    df["vni_rsi_max3m"] = float(vni["D_RSI"].max()) if len(vni) else np.nan
    return df


def _sec(icb):
    return int(icb // 1000) if pd.notna(icb) else None


def ta_terms(r):
    """Mirror signal_v11_sql.py's `ta` CASE list term-by-term. Returns list of
    (label, formula_text, points_if_hit, hit, evidence_str)."""
    g = lambda k: r.get(k)
    sec = _sec(g("ICB_Code"))
    fa_tier = g("fa_tier")
    T = []

    def add(label, formula, pts, hit, evidence):
        T.append((label, formula, pts if hit else 0, bool(hit), evidence))

    d_rsi, close, ma20, ma50, ma200 = g("D_RSI"), g("Close"), g("MA20"), g("MA50"), g("MA200")
    ma50_t1, close_t1, vol, vol3mp50 = g("MA50_T1"), g("Close_T1"), g("Volume"), g("Volume_3M_P50")
    macd, rsi1w, hi3m_t1, id_hi3y = g("D_MACDdiff"), g("D_RSI_Max1W"), g("HI_3M_T1"), g("ID_HI_3Y")
    pe, pe_ma5y, pe_sd5y, fscore = g("PE"), g("PE_MA5Y"), g("PE_SD5Y"), g("FSCORE")
    np0, np1, np4, vrsi3m = g("NP_P0"), g("NP_P1"), g("NP_P4"), g("vni_rsi_max3m")

    add("RSI>0.50", "D_RSI > 0.50", 25, pd.notna(d_rsi) and d_rsi > 0.50, f"D_RSI={d_rsi}")
    add("uptrend", "Close>MA50>MA200", 25,
        pd.notna(close) and pd.notna(ma50) and pd.notna(ma200) and close > ma50 and ma50 > ma200,
        f"Close={close} MA50={ma50} MA200={ma200}")
    add("vol-breakout", "Volume>=Volume_3M_P50*1.3 & Close>Close_T1", 20,
        pd.notna(vol) and pd.notna(vol3mp50) and pd.notna(close) and pd.notna(close_t1)
        and vol >= vol3mp50 * 1.3 and close > close_t1,
        f"Volume={vol} Volume_3M_P50={vol3mp50} Close={close} Close_T1={close_t1}")
    add("MACD>0", "D_MACDdiff > 0", 15, pd.notna(macd) and macd > 0, f"D_MACDdiff={macd}")
    add("Close>MA20", "Close > MA20", 15, pd.notna(close) and pd.notna(ma20) and close > ma20,
        f"Close={close} MA20={ma20}")
    add("RSI>0.75", "D_RSI > 0.75", 5, pd.notna(d_rsi) and d_rsi > 0.75, f"D_RSI={d_rsi}")
    add("RSI<0.30", "D_RSI < 0.30", -10, pd.notna(d_rsi) and d_rsi < 0.30, f"D_RSI={d_rsi}")
    pe_cheap = (pd.notna(pe) and pd.notna(pe_ma5y) and pd.notna(pe_sd5y) and pe > 0 and pe_ma5y > 0
                and pe < pe_ma5y - 0.5 * pe_sd5y)
    add("PE-cheap-vs-5Y", "PE>0 & PE_MA5Y>0 & PE < PE_MA5Y-0.5*PE_SD5Y", 15, pe_cheap,
        f"PE={pe} PE_MA5Y={pe_ma5y} PE_SD5Y={pe_sd5y}")
    pe_rich = (pd.notna(pe) and pd.notna(pe_ma5y) and pd.notna(pe_sd5y) and pe > 0 and pe_ma5y > 0
               and pe > pe_ma5y + 1.0 * pe_sd5y)
    add("PE-rich-vs-5Y", "PE>0 & PE_MA5Y>0 & PE > PE_MA5Y+1.0*PE_SD5Y", -15, pe_rich,
        f"PE={pe} PE_MA5Y={pe_ma5y} PE_SD5Y={pe_sd5y}")
    add("VNI-hot", "VNINDEX RSI_max3m > 0.65", 10, pd.notna(vrsi3m) and vrsi3m > 0.65,
        f"vni_rsi_max3m={vrsi3m}")
    add("near-3Y-high", "ID_HI_3Y <= 5", 8, pd.notna(id_hi3y) and id_hi3y <= 5, f"ID_HI_3Y={id_hi3y}")
    add("RSI1W>0.65", "D_RSI_Max1W > 0.65", 5, pd.notna(rsi1w) and rsi1w > 0.65, f"D_RSI_Max1W={rsi1w}")
    add("FSCORE>=8", "FSCORE >= 8", 10, pd.notna(fscore) and fscore >= 8, f"FSCORE={fscore}")
    np_surge = pd.notna(np0) and pd.notna(np4) and np4 > 0 and np0 > np4 * 1.5
    add("NP-surge-YoY", "NP_P0 > NP_P4*1.5 & NP_P4>0", 8, np_surge, f"NP_P0={np0} NP_P4={np4}")
    np_slump = pd.notna(np0) and pd.notna(np4) and np4 > 0 and np0 < np4 * 0.7
    add("NP-slump-YoY", "NP_P0 < NP_P4*0.7 & NP_P4>0", -8, np_slump, f"NP_P0={np0} NP_P4={np4}")
    add("sector-favored", "sector(ICB) in (8,9)", 5, sec in (8, 9), f"sector={sec}")
    add("sector-avoided", "sector(ICB) in (4,7)", -5, sec in (4, 7), f"sector={sec}")
    ma50_up = pd.notna(ma50_t1) and ma50_t1 > 0 and pd.notna(ma50) and ma50 > ma50_t1
    add("MA50-rising", "MA50_T1>0 & MA50>MA50_T1", 5, ma50_up, f"MA50={ma50} MA50_T1={ma50_t1}")
    ma50_accel = pd.notna(ma50_t1) and ma50_t1 > 0 and pd.notna(ma50) and ma50 > ma50_t1 * 1.005
    add("MA50-accel", "MA50_T1>0 & MA50>MA50_T1*1.005", 5, ma50_accel, f"MA50={ma50} MA50_T1={ma50_t1}")
    ma50_down = pd.notna(ma50_t1) and ma50_t1 > 0 and pd.notna(ma50) and ma50 < ma50_t1
    add("MA50-falling", "MA50_T1>0 & MA50<MA50_T1", -5, ma50_down, f"MA50={ma50} MA50_T1={ma50_t1}")
    pullback = pd.notna(hi3m_t1) and hi3m_t1 > 0 and pd.notna(close) and (close / hi3m_t1) < 0.85
    add("deep-pullback-3M", "HI_3M_T1>0 & Close/HI_3M_T1<0.85", -10, pullback,
        f"Close={close} HI_3M_T1={hi3m_t1}")
    np_qoq = pd.notna(np0) and pd.notna(np1) and np1 > 0 and np0 > np1 * 1.2
    add("NP-surge-QoQ", "NP_P0 > NP_P1*1.2 & NP_P1>0", 8, np_qoq, f"NP_P0={np0} NP_P1={np1}")
    add("FA-D-financials", "sector=8 & fa_tier='D'", 10, sec == 8 and fa_tier == "D",
        f"sector={sec} fa_tier={fa_tier}")
    add("FA-A-financials", "sector=8 & fa_tier='A'", -10, sec == 8 and fa_tier == "A",
        f"sector={sec} fa_tier={fa_tier}")
    return T


def render_bal(ticker, row_recs, raw_row):
    terms = ta_terms(raw_row)
    computed_ta = sum(t[2] for t in terms)
    actual_ta = row_recs.get("ta")
    mismatch = pd.notna(actual_ta) and abs(computed_ta - float(actual_ta)) > 1
    lines = [f"### {ticker} — BAL / {row_recs.get('play_type')} "
             f"(status={row_recs.get('status')}, weight={row_recs.get('weight_pct'):.2f}%)"]
    lines.append(f"ta (CSV, production) = **{actual_ta}** | ta (recomputed here) = **{computed_ta}**"
                 + ("  ⚠️ MISMATCH — signal_v11_sql.py có thể đã đổi, hit_details.py cần cập nhật lại"
                    if mismatch else "  ✓ khớp"))
    lines.append("")
    lines.append("| Điều kiện | Công thức | Điểm | Khớp? | Giá trị thật |")
    lines.append("|---|---|---|---|---|")
    for label, formula, pts, hit, evidence in terms:
        if pts == 0 and not hit:
            continue   # chỉ in điều kiện THỰC SỰ khớp (cộng hoặc trừ điểm) — bảng ngắn, dễ đọc
        lines.append(f"| {label} | `{formula}` | {pts:+d} | {'✅' if hit else ''} | {evidence} |")
    r8 = raw_row.get("rating")
    lines.append(f"\n_8L rating (fa_ratings_8l, để tham khảo weight-halving BEAR/CRISIS): "
                 f"{r8 if pd.notna(r8) else 'n/a'}_")
    return "\n".join(lines)


def render_lag(ticker, row_recs, cand_row):
    lines = [f"### {ticker} — LAG / {row_recs.get('play_type')} (status={row_recs.get('status')}, "
             f"weight={row_recs.get('weight_pct'):.2f}%)"]
    if cand_row is None:
        lines.append("_Không tìm lại được event trong earnings_surprise_data.pkl hôm nay — "
                      "có thể pkl đã refresh/mất event cũ. Xem golive log để có giá trị gốc._")
        return "\n".join(lines)
    lines.append(f"Formula: `NP_R>={NP_R_MIN} & prior_n_good>={PRIOR_N_MIN} & pa_HL3>={PA_HL3_MIN}` "
                 f"(pinned R3 LAG spec, entry T+5 sau Release_Date, hold 25 phiên)")
    lines.append("")
    lines.append("| Biến | Giá trị | Ngưỡng | Khớp? |")
    lines.append("|---|---|---|---|")
    lines.append(f"| NP_R (%) | {cand_row['NP_R']:.2f} | >= {NP_R_MIN} | "
                 f"{'✅' if cand_row['NP_R'] >= NP_R_MIN else '❌'} |")
    lines.append(f"| prior_n_good | {cand_row['prior_n_good']} | >= {PRIOR_N_MIN} | "
                 f"{'✅' if cand_row['prior_n_good'] >= PRIOR_N_MIN else '❌'} |")
    lines.append(f"| pa_HL3 | {cand_row['pa_HL3']:.2f} | >= {PA_HL3_MIN} | "
                 f"{'✅' if cand_row['pa_HL3'] >= PA_HL3_MIN else '❌'} |")
    lines.append(f"| surprise_B_MA (→ tier) | {cand_row['surprise_B_MA']:.3f} | "
                 f"tier=LAG_HI nếu >0.5 | tier={cand_row['tier']} |")
    lines.append(f"| Release_Date | {cand_row['Release_Date'].date()} | quarter={cand_row['quarter']} | |")
    lines.append("\n_Ứng viên này đã qua thêm 3 gate upstream (không recompute ở đây — xem golive log "
                 "ngày này): lag_filter_illiquid (ADV≥2 tỷ/phiên), lag_filter_low_rating (8L rating≤3), "
                 "lag_filter_forensic_banned (không BANNED/forensic)._")
    return "\n".join(lines)


def main():
    date = sys.argv[1] if len(sys.argv) > 1 else None
    if date is None:
        cands = sorted(glob.glob(os.path.join(OUTDIR, "golive_v23_recommendations_*.csv")))
        if not cands:
            sys.exit(f"Không thấy golive_v23_recommendations_*.csv nào trong {OUTDIR}")
        date = os.path.basename(cands[-1])[len("golive_v23_recommendations_"):-len(".csv")]

    recs_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{date}.csv")
    if not os.path.exists(recs_path):
        sys.exit(f"Không thấy {recs_path}")
    recs = pd.read_csv(recs_path)

    bal_rows = recs[(recs["book"] == "BAL") & (recs["status"].isin(["FULL", "HALF_SIZE"]))]
    lag_rows = recs[(recs["book"] == "LAG")]

    sections = [f"# Hit Details — {date}\n",
                "Nguồn: `golive_v23_recommendations_{}.csv` + raw factor fetch trực tiếp BQ "
                "(BAL) / `lag_live_schedule.live_lag_candidates()` (LAG). Công cụ audit thuần — "
                "KHÔNG đổi logic lọc/đặt lệnh. Xem `kb/coding_guidelines.md` §29.\n".format(date)]

    if len(bal_rows):
        raw = fetch_bal_raw(bal_rows["ticker"].tolist(), date)
        raw_idx = raw.set_index("ticker") if len(raw) else pd.DataFrame()
        sections.append(f"## BAL book ({len(bal_rows)} mã)\n")
        for _, r in bal_rows.iterrows():
            t = r["ticker"]
            if t not in raw_idx.index:
                sections.append(f"### {t} — BAL\n_Không fetch được raw factor cho {date} "
                                 f"(ticker/ticker_1m thiếu dòng) — bỏ qua breakdown._")
                continue
            sections.append(render_bal(t, r, raw_idx.loc[t]))
    else:
        sections.append("## BAL book\n_Không có mã BAL FULL/HALF_SIZE hôm nay._")

    if len(lag_rows):
        start = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=120)).strftime("%Y-%m-%d")
        try:
            cand = live_lag_candidates(start=start)
            cand_idx = cand.set_index("ticker")
            cand_err = None
        except Exception as e:
            cand_idx = pd.DataFrame()
            cand_err = f"{type(e).__name__}: {e}"
        sections.append(f"\n## LAG book ({len(lag_rows)} mã)\n")
        if cand_err:
            sections.append(f"_live_lag_candidates() lỗi: {cand_err} — không có breakdown LAG hôm nay._")
        else:
            for _, r in lag_rows.iterrows():
                t = r["ticker"]
                cr = cand_idx.loc[t] if t in cand_idx.index else None
                if isinstance(cr, pd.DataFrame):   # ticker có nhiều quarter event — lấy Release_Date mới nhất
                    cr = cr.sort_values("Release_Date").iloc[-1]
                sections.append(render_lag(t, r, cr))
    else:
        sections.append("\n## LAG book\n_Không có entry LAG upcoming/recent hôm nay._")

    out_path = os.path.join(DATADIR, f"hit_details_{date}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(sections) + "\n")
    print(f"Viết {out_path} ({len(bal_rows)} BAL, {len(lag_rows)} LAG)")


if __name__ == "__main__":
    main()
