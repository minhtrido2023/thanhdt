#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phễu candidate hệ thống cho sleeve margin đơn mã discretionary (TV1/DGC-style fear-buy) —
VIỆC 2 của job discretionary-sleeve-candidate-funnel-20260830.

Lỗ hổng nó vá: TV1/DGC vào sleeve qua quan sát TÌNH CỜ của user, không có phễu quét hệ thống,
và KHÔNG có bước lọc marginability trong bất kỳ scan nào (TV1 UPCOM không marginable là lý do
sleeve đang 0 case thật). Script này LẮP RÁP các mảnh đã có, KHÔNG viết lại logic:
  1. Universe fear = PB<1,0 (hiện tại) + washout>=30% (từ đỉnh cục bộ 400 ngày lịch) +
     dd52<=-20% (per-ticker, CÙNG công thức capit_margin_lever — rolling 252-session high —
     áp cho từng mã thay vì VNINDEX), tính từ `tav2_bq.ticker` JOIN `tav2_mike.universe_pit`
     (in_universe=True tại phiên gần nhất) — cùng định nghĩa đã validate trong
     `research/discretionary_sleeve_correlation_risk_20260830.md` (`analyze_corr.py` bước 1).
  2. Quality floor = `data/rating_8l.csv` (rating_8l.py, 17:45 ICT hàng ngày) — golden floor
     ROE_Min3Y>=0 AND CF_OA_3Y>0, rating<=3.
  3. Negative screens = `data/insider_flags.json` (insider_flags.py) + cột `redflag` có sẵn
     trong rating_8l.csv (NP_TTM<0 / debt/eq>3, forensic exclusion đã bake vào `rating`/`route`).
  4. Marginability + %ADV = `marginability_check.py` (VIỆC 1, chỉ probe DNSE cho SHORTLIST đã
     qua bước 1-3, không probe cả universe) + `adv_3m()` tái dùng nguyên hàm từ
     `discretionary_margin_gate.py` (KHÔNG viết lại công thức ADV).

Output: RECON — bảng xếp hạng ticker, KHÔNG auto-arm bất kỳ case nào. Người (Mike/user) review
rồi mới đưa qua due-diligence sâu (fundamental-skeptic) và `discretionary_margin_gate.py arm`
nếu muốn.

DÙNG:
    python3 mike/bin/discretionary_candidate_funnel.py                  # chạy đầy đủ, in bảng
    python3 mike/bin/discretionary_candidate_funnel.py --print-block    # khối text để nhúng
                                                                          # vào prompt LLM khác
    python3 mike/bin/discretionary_candidate_funnel.py --json out.json  # ghi thêm JSON
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

import pandas as pd

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIKE_ROOT = os.path.join(WC_ROOT, "mike")
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(MIKE_ROOT, "bin"))

ICT = ZoneInfo("Asia/Ho_Chi_Minh")                        # §16: neo múi giờ tường minh

PROJECT = "lithe-record-440915-m9"
CLOUDSDK_CONFIG = "/home/trido/thanhdt/gcloud_dtienthanh"   # dtienthanh@gmail.com — cron không
                                                              # source wc_env.sh, đồng bộ
                                                              # insider_flags.py CLOUDSDK_CONFIG

RATING_8L_CSV = os.path.join(WC_ROOT, "data", "rating_8l.csv")
INSIDER_FLAGS_JSON = os.path.join(WC_ROOT, "data", "insider_flags.json")
RESEARCH_OUT_DIR = os.path.join(MIKE_ROOT, "agents", "Taylor", "research",
                                 "discretionary_sleeve_candidate_funnel_20260830")

# Cohort thresholds — y hệt analyze_corr.py bước 1 (KHÔNG tự chế lại):
PB_MAX = 1.0
WASHOUT_MIN_PCT = -0.30           # từ đỉnh cục bộ 400 NGÀY LỊCH (dd_stock)
DD52_MAX_PCT = -0.20              # per-ticker, rolling 252-SESSION high (công thức capit_margin_lever)
PANEL_LOOKBACK_DAYS = 410         # 400d peak window + đệm

# Quality floor (rating_8l.py):
RATING_MAX = 3                    # golden-floor gate (đồng quy ước discretionary policy: rating<=3)

# Marginability account — SpaceX, đồng bộ discretionary_margin_gate.py ONLY_ACCOUNT
MARGIN_ACCOUNT = "0002023347"


def _now_ict_iso():
    return dt.datetime.now(ICT).isoformat()


def bq_csv(sql):
    """Chạy 1 query BQ, trả pandas.DataFrame. Lỗi ⇒ raise, KHÔNG nuốt (§29 — không đoán)."""
    from io import StringIO
    env = os.environ.copy()
    env.setdefault("CLOUDSDK_CONFIG", CLOUDSDK_CONFIG)
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", "--format=csv",
         f"--project_id={PROJECT}", "--max_rows=200000", sql],
        capture_output=True, text=True, env=env, timeout=300)
    if out.returncode != 0:
        msg = (out.stderr.strip() or out.stdout.strip())[:800]
        raise RuntimeError(f"bq query lỗi: {msg}")
    if not out.stdout.strip():
        raise RuntimeError("bq trả rỗng — không có dòng nào")
    return pd.read_csv(StringIO(out.stdout.strip()))


def pull_fear_panel(lookback_days=PANEL_LOOKBACK_DAYS):
    """Panel Close/PB/Volume/Trading_Value cho universe_pit hiện tại, `lookback_days` ngày gần
    nhất — đủ để tính washout(400d) + dd52(252-session)."""
    sql = f"""
WITH pit AS (
  SELECT ticker FROM `tav2_mike.universe_pit`
  WHERE time = (SELECT MAX(time) FROM `tav2_mike.universe_pit`) AND in_universe
)
SELECT t.ticker, t.time, t.Close, t.PB, t.Volume, t.Trading_Value
FROM `tav2_bq.ticker` AS t
JOIN pit USING(ticker)
WHERE t.time BETWEEN DATE_SUB(CURRENT_DATE("Asia/Ho_Chi_Minh"), INTERVAL {lookback_days} DAY)
                  AND CURRENT_DATE("Asia/Ho_Chi_Minh")
ORDER BY t.ticker, t.time
"""
    return bq_csv(sql)


def compute_fear_cohort(panel):
    """panel: DataFrame[ticker,time,Close,PB,Volume,Trading_Value] -> DataFrame per-ticker LATEST
    row + washout_pct/dd52_pct/in_fear_cohort. dd_stock dùng đỉnh cục bộ 400 NGÀY LỊCH (khớp
    analyze_corr.py); dd52 dùng đỉnh rolling 252 PHIÊN (khớp capit_margin_lever, per-ticker)."""
    panel = panel.copy()
    panel["time"] = pd.to_datetime(panel["time"])
    panel = panel.sort_values(["ticker", "time"])

    rows = []
    for ticker, g in panel.groupby("ticker", sort=False):
        g = g.set_index("time")
        peak400 = g["Close"].rolling("400D", min_periods=20).max()
        peak252s = g["Close"].rolling(252, min_periods=60).max()
        dd_stock = g["Close"] / peak400 - 1.0
        dd52 = g["Close"] / peak252s - 1.0
        last = g.index.max()
        rows.append({
            "ticker": ticker,
            "asof": last.date().isoformat(),
            "close": float(g["Close"].loc[last]),
            "pb": float(g["PB"].loc[last]) if pd.notna(g["PB"].loc[last]) else None,
            "washout_pct": float(dd_stock.loc[last]) if pd.notna(dd_stock.loc[last]) else None,
            "dd52_pct": float(dd52.loc[last]) if pd.notna(dd52.loc[last]) else None,
            "n_sessions_in_panel": int(len(g)),
        })
    out = pd.DataFrame(rows)
    out["in_fear_cohort"] = (
        out["pb"].notna() & (out["pb"] < PB_MAX)
        & out["washout_pct"].notna() & (out["washout_pct"] <= WASHOUT_MIN_PCT)
        & out["dd52_pct"].notna() & (out["dd52_pct"] <= DD52_MAX_PCT)
    )
    return out


def load_quality_floor():
    """rating_8l.csv -> DataFrame[ticker, rating, ROE_Min3Y, CF_OA_3Y, redflag, route, note,
    golden_floor_pass]. Golden floor = ROE_Min3Y>=0 AND CF_OA_3Y>0 (§8L rule)."""
    if not os.path.exists(RATING_8L_CSV):
        return None, f"thiếu {RATING_8L_CSV}"
    df = pd.read_csv(RATING_8L_CSV)
    mtime = dt.datetime.fromtimestamp(os.path.getmtime(RATING_8L_CSV), tz=ICT)
    age_days = (dt.datetime.now(ICT) - mtime).total_seconds() / 86400.0
    stale_note = None
    if age_days > 3:                                       # daily-refresh 17:45 ICT
        stale_note = f"rating_8l.csv cũ {age_days:.1f} ngày (mtime {mtime.isoformat()})"
    df["golden_floor_pass"] = (df["ROE_Min3Y"] >= 0) & (df["CF_OA_3Y"] > 0)
    keep = ["ticker", "rating", "ROE_Min3Y", "CF_OA_3Y", "redflag", "route", "note",
            "golden_floor_pass", "liq_bn"]
    return df[keep], stale_note


def load_insider_flags():
    if not os.path.exists(INSIDER_FLAGS_JSON):
        return {}, f"thiếu {INSIDER_FLAGS_JSON}"
    with open(INSIDER_FLAGS_JSON, encoding="utf-8") as f:
        flags = json.load(f)
    mtime = dt.datetime.fromtimestamp(os.path.getmtime(INSIDER_FLAGS_JSON), tz=ICT)
    age_days = (dt.datetime.now(ICT) - mtime).total_seconds() / 86400.0
    stale_note = f"insider_flags.json cũ {age_days:.1f} ngày (mtime {mtime.isoformat()})" \
        if age_days > 7 else None
    return flags, stale_note


def annotate_shortlist(shortlist_tickers):
    """Marginability + %ADV — CHỈ cho tickers đã qua bước 1-3 (không probe cả universe)."""
    from marginability_check import check_marginability
    from discretionary_margin_gate import adv_3m, ADV_CAP_PCT

    marg = check_marginability(shortlist_tickers, account=MARGIN_ACCOUNT)
    rows = []
    for t in shortlist_tickers:
        m = marg.get(t, {})
        adv_vnd, adv_asof, adv_err = adv_3m(t)
        rows.append({
            "ticker": t,
            "marginable": m.get("marginable"),
            "margin_package_id": m.get("package_id"),
            "margin_initial_rate": m.get("initial_rate"),
            "margin_error": m.get("error"),
            "adv_3m_vnd": adv_vnd,
            "adv_asof": adv_asof,
            "adv_error": adv_err,
            "max_position_at_adv_cap_vnd": (adv_vnd * ADV_CAP_PCT) if adv_vnd else None,
        })
    return pd.DataFrame(rows)


def run_funnel():
    """Trả (result_df, meta) — meta chứa cảnh báo/staleness, KHÔNG bao giờ raise cho lỗi từng
    tầng dữ liệu phụ (quality/insider) — chỉ BQ panel là bắt buộc (không có universe fear thì
    không có gì để lọc tiếp)."""
    meta = {"run_at": _now_ict_iso(), "warnings": []}

    panel = pull_fear_panel()
    n_universe = panel["ticker"].nunique()
    fear = compute_fear_cohort(panel)
    n_fear_cohort = int(fear["in_fear_cohort"].sum())
    meta["n_universe_pit"] = int(n_universe)
    meta["n_fear_cohort"] = n_fear_cohort

    cohort = fear[fear["in_fear_cohort"]].copy()

    quality, q_warn = load_quality_floor()
    if q_warn:
        meta["warnings"].append(q_warn)
    if quality is not None:
        cohort = cohort.merge(quality, on="ticker", how="left")
    else:
        meta["warnings"].append("KHÔNG có quality floor — cohort chưa lọc theo rating")

    insider_flags, i_warn = load_insider_flags()
    if i_warn:
        meta["warnings"].append(i_warn)
    cohort["insider_sell_flag"] = cohort["ticker"].map(
        lambda t: bool(insider_flags.get(t)))
    cohort["insider_flag_reasons"] = cohort["ticker"].map(
        lambda t: (insider_flags.get(t) or {}).get("reasons"))

    if cohort.empty:
        meta["warnings"].append(
            f"universe fear cohort RỖNG (PB<{PB_MAX} & washout<={WASHOUT_MIN_PCT:.0%} & "
            f"dd52<={DD52_MAX_PCT:.0%}) trong {n_universe} mã universe_pit — funnel dừng ở đây, "
            f"không có gì để annotate marginability/ADV.")
        return cohort, meta

    ann = annotate_shortlist(cohort["ticker"].tolist())
    cohort = cohort.merge(ann, on="ticker", how="left")

    # QUALIFY = qua đủ cả 4 tầng: fear cohort (đã lọc) + quality floor + không insider-sell +
    # không redflag + marginable=True. Đây là gợi ý xếp hạng, KHÔNG phải quyết định tự động.
    cohort["golden_floor_pass"] = cohort["golden_floor_pass"].fillna(False)
    cohort["rating_pass"] = cohort["rating"].fillna(99) <= RATING_MAX
    cohort["clean_screen"] = (~cohort["insider_sell_flag"]) & cohort["redflag"].isna()
    cohort["fully_qualified"] = (
        cohort["golden_floor_pass"] & cohort["rating_pass"] & cohort["clean_screen"]
        & (cohort["marginable"] == True)          # noqa: E712 — pandas bool có NaN, != đúng hơn is
    )
    cohort = cohort.sort_values(
        ["fully_qualified", "washout_pct"], ascending=[False, True]
    ).reset_index(drop=True)
    return cohort, meta


COLS_DISPLAY = ["ticker", "washout_pct", "dd52_pct", "pb", "rating", "golden_floor_pass",
                "insider_sell_flag", "redflag", "marginable", "margin_package_id",
                "adv_3m_vnd", "fully_qualified"]


def format_block(cohort, meta):
    lines = [f"=== Discretionary candidate funnel — {meta['run_at']} ===",
             f"universe_pit: {meta.get('n_universe_pit', '?')} mã | "
             f"fear cohort (PB<{PB_MAX} & washout<={WASHOUT_MIN_PCT:.0%} & "
             f"dd52<={DD52_MAX_PCT:.0%}): {meta.get('n_fear_cohort', '?')} mã"]
    for w in meta.get("warnings", []):
        lines.append(f"  CẢNH BÁO: {w}")
    if cohort.empty:
        lines.append("(không có ticker nào qua fear cohort — xem cảnh báo ở trên)")
        return "\n".join(lines)
    for _, r in cohort.iterrows():
        marg = "Y" if r.get("marginable") is True else ("N" if r.get("marginable") is False else "?")
        adv_vnd = r.get("adv_3m_vnd")
        adv_s = f"{adv_vnd / 1e9:.2f}tỷ" if pd.notna(adv_vnd) else "N/A"
        redflag_s = r.get("redflag") if pd.notna(r.get("redflag")) else "-"
        line = (
            f"  {r['ticker']:6} washout={r['washout_pct']:.1%} dd52={r['dd52_pct']:.1%} "
            f"PB={r['pb']:.2f} rating={r.get('rating', 'NA')} "
            f"golden_floor={'Y' if r.get('golden_floor_pass') else 'N'} "
            f"insider_sell={'Y' if r.get('insider_sell_flag') else 'N'} "
            f"redflag={redflag_s} "
            f"marginable={marg}({r.get('margin_package_id') or '-'}) "
            f"adv_3m={adv_s}"
        )
        if r.get("fully_qualified"):
            line += "  <<< FULLY_QUALIFIED (fear+quality+clean+marginable) — vẫn RECON, cần review tay"
        lines.append(line)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print-block", action="store_true",
                     help="In khối text gọn để nhúng vào prompt (giống anomaly_scan --print-universe)")
    ap.add_argument("--json", metavar="PATH", help="Ghi thêm JSON đầy đủ ra PATH")
    ap.add_argument("--csv", metavar="PATH", help="Ghi thêm CSV đầy đủ ra PATH")
    args = ap.parse_args()


    cohort, meta = run_funnel()

    if args.print_block:
        print(format_block(cohort, meta))
    else:
        print(f"[{meta['run_at']}] universe_pit={meta.get('n_universe_pit')} "
              f"fear_cohort={meta.get('n_fear_cohort')}")
        for w in meta.get("warnings", []):
            print(f"  CẢNH BÁO: {w}")
        if not cohort.empty:
            print(cohort[COLS_DISPLAY].to_string(index=False))

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "shortlist": json.loads(cohort.to_json(orient="records"))},
                       f, ensure_ascii=False, indent=2)
    if args.csv:
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        cohort.to_csv(args.csv, index=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
