#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phễu candidate hệ thống cho sleeve margin đơn mã discretionary (TV1/DGC-style fear-buy) —
VIỆC 2 của job discretionary-sleeve-candidate-funnel-20260830.

Lỗ hổng nó vá: TV1/DGC vào sleeve qua quan sát TÌNH CỜ của user, không có phễu quét hệ thống,
và KHÔNG có bước lọc marginability trong bất kỳ scan nào (TV1 UPCOM không marginable là lý do
sleeve đang 0 case thật). Script này LẮP RÁP các mảnh đã có, KHÔNG viết lại logic:
  1. Universe fear = washout>=30% (từ đỉnh cục bộ 400 ngày lịch) + dd52<=-20% (per-ticker, CÙNG
     công thức capit_margin_lever — rolling 252-session high — áp cho từng mã thay vì VNINDEX)
     AND [PB<1,0 tuyệt đối HOẶC (percentile PB<=70% AND PB<1,2)] — OR-logic PB thích ứng theo
     chu kỳ, khoá bằng min-CV mechanical rule qua 7 episode lịch sử, quant-skeptic CONFIRMED
     (job Taylor_20260830_085015 round 3, verify quant-skeptic_20260830_085357). Cơ sở
     percentile = `universe_pit ∩ Volume>0` CÙNG NGÀY (không phải toàn bộ mã niêm yết) — xem
     `research/discretionary_funnel_adaptive_pb_round3_20260830.md`. Washout/dd52 từ
     `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (in_universe=True tại phiên gần nhất) —
     cùng định nghĩa đã validate trong `research/discretionary_sleeve_correlation_risk_20260830.md`
     (`analyze_corr.py` bước 1).
  2. Quality floor = `data/rating_8l.csv` (rating_8l.py, 17:45 ICT hàng ngày) — golden floor
     ROE_Min3Y>=0 AND CF_OA_3Y>0, rating<=3.
  3. Negative screens = `data/insider_flags.json` (insider_flags.py) + cột `redflag` có sẵn
     trong rating_8l.csv (NP_TTM<0 / debt/eq>3, forensic exclusion đã bake vào `rating`/`route`).
  4. Marginability + %ADV = `marginability_check.py` (VIỆC 1, chỉ probe DNSE cho SHORTLIST đã
     qua bước 1-3, không probe cả universe) + `adv_3m()` tái dùng nguyên hàm từ
     `discretionary_margin_gate.py` (KHÔNG viết lại công thức ADV).
  5. Cảnh báo tập trung ngành (informational, KHÔNG phải enforcement) — nếu >=2 mã cùng ICB
     (CTCK=8777, hoá chất/phân bón=1357) đều fully_qualified, in cảnh báo theo risk-auditor
     2026-08-30 (job Taylor_20260830_092103 bước 2, CONDITIONAL-APPROVE cả 2 cụm). Funnel này
     STATELESS (không biết case nào đang armed) nên KHÔNG thể enforce cap "≤1 đồng thời mở" —
     enforcement thật phải nằm ở `discretionary_margin_gate.py` (chưa làm, xem bus finding
     discretionary-funnel-adaptive-pb-wire-step2-risk-20260830 + step3).

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
WASHOUT_MIN_PCT = -0.30           # từ đỉnh cục bộ 400 NGÀY LỊCH (dd_stock)
DD52_MAX_PCT = -0.20              # per-ticker, rolling 252-SESSION high (công thức capit_margin_lever)
PANEL_LOOKBACK_DAYS = 410         # 400d peak window + đệm

# PB thích ứng theo chu kỳ — khoá min-CV mechanical, quant-skeptic CONFIRMED round 3
# (job Taylor_20260830_085015, verify quant-skeptic_20260830_085357). KHÔNG re-tune theo lịch sử.
PB_MAX_ABS = 1.0                  # nhánh tuyệt đối, giữ nguyên
PB_PCT_CUTOFF = 0.70              # nhánh percentile: PB percentile <= 70% (min-CV, 7 episode)
PB_MAX_CEIL = 1.2                 # trần PB cho nhánh percentile (min-CV, KHÔNG PHẢI 1.5)

# Cảnh báo tập trung ngành (informational only — xem docstring mục 5)
SECTOR_CONCENTRATION_WATCH = {8777: "CTCK", 1357: "Hoá chất/phân bón"}

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
    """Panel Close/PB/Volume/Trading_Value/ICB_Code cho universe_pit hiện tại, `lookback_days`
    ngày gần nhất — đủ để tính washout(400d) + dd52(252-session). ICB_Code chỉ dùng ở giá trị
    NGÀY GẦN NHẤT (cảnh báo tập trung ngành, mục 5 docstring)."""
    sql = f"""
WITH pit AS (
  SELECT ticker FROM `tav2_mike.universe_pit`
  WHERE time = (SELECT MAX(time) FROM `tav2_mike.universe_pit`) AND in_universe
)
SELECT t.ticker, t.time, t.Close, t.PB, t.Volume, t.Trading_Value, t.ICB_Code
FROM `tav2_bq.ticker` AS t
JOIN pit USING(ticker)
WHERE t.time BETWEEN DATE_SUB(CURRENT_DATE("Asia/Ho_Chi_Minh"), INTERVAL {lookback_days} DAY)
                  AND CURRENT_DATE("Asia/Ho_Chi_Minh")
ORDER BY t.ticker, t.time
"""
    return bq_csv(sql)


def pull_pb_percentile():
    """PB percentile rank cross-section — ĐÚNG công thức đã khoá quant-skeptic CONFIRMED
    (job Taylor_20260830_085015, round 3): PERCENT_RANK() OVER (ORDER BY PB), cơ sở
    `universe_pit ∩ Volume>0` CÙNG MỘT NGÀY = MAX(time) của `tav2_bq.ticker` (không phải
    MAX(time) riêng của universe_pit — khớp `episode_cohort_query.sql` dùng chung 1 biến ngày
    cho cả 2 vế join). KHÔNG toàn bộ mã niêm yết. Trả DataFrame[ticker, pb_pct_rank]."""
    sql = """
WITH asof AS (SELECT MAX(time) AS d FROM `tav2_bq.ticker`),
trough_px AS (
  SELECT t.ticker, t.PB, t.Volume
  FROM `tav2_bq.ticker` AS t, asof
  WHERE t.time = asof.d
),
univ AS (
  SELECT ticker FROM `tav2_mike.universe_pit`, asof
  WHERE time = asof.d AND in_universe
),
cross_section AS (
  SELECT tp.ticker, tp.PB
  FROM trough_px AS tp JOIN univ AS u ON tp.ticker = u.ticker
  WHERE tp.Volume > 0 AND tp.PB IS NOT NULL
)
SELECT ticker, PERCENT_RANK() OVER (ORDER BY PB) AS pb_pct_rank
FROM cross_section
"""
    return bq_csv(sql)


def compute_fear_cohort(panel):
    """panel: DataFrame[ticker,time,Close,PB,Volume,Trading_Value,ICB_Code] -> DataFrame per-ticker
    LATEST row + washout_pct/dd52_pct (KHÔNG áp PB threshold ở đây — xem run_funnel, cần merge
    pb_pct_rank từ pull_pb_percentile() trước khi quyết định OR-logic). dd_stock dùng đỉnh cục bộ
    400 NGÀY LỊCH (khớp analyze_corr.py); dd52 dùng đỉnh rolling 252 PHIÊN (khớp
    capit_margin_lever, per-ticker)."""
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
        icb = g["ICB_Code"].loc[last] if "ICB_Code" in g.columns else None
        rows.append({
            "ticker": ticker,
            "asof": last.date().isoformat(),
            "close": float(g["Close"].loc[last]),
            "pb": float(g["PB"].loc[last]) if pd.notna(g["PB"].loc[last]) else None,
            "icb_code": int(icb) if pd.notna(icb) else None,
            "washout_pct": float(dd_stock.loc[last]) if pd.notna(dd_stock.loc[last]) else None,
            "dd52_pct": float(dd52.loc[last]) if pd.notna(dd52.loc[last]) else None,
            "n_sessions_in_panel": int(len(g)),
        })
    out = pd.DataFrame(rows)
    out["in_washout_dd52"] = (
        out["pb"].notna()
        & out["washout_pct"].notna() & (out["washout_pct"] <= WASHOUT_MIN_PCT)
        & out["dd52_pct"].notna() & (out["dd52_pct"] <= DD52_MAX_PCT)
    )
    return out


def apply_pb_or_logic(cohort):
    """cohort: DataFrame đã lọc washout+dd52 (in_washout_dd52), merge sẵn pb_pct_rank ->
    thêm qualify_via/in_fear_cohort theo OR-logic đã khoá (§ constants). PHẢI gọi sau khi merge
    kết quả pull_pb_percentile() vào cohort."""
    cohort = cohort.copy()
    if "pb_pct_rank" not in cohort.columns:
        cohort["pb_pct_rank"] = None
    qualify_abs = cohort["pb"].notna() & (cohort["pb"] < PB_MAX_ABS)
    qualify_pct = (
        cohort["pb_pct_rank"].notna() & (cohort["pb_pct_rank"] <= PB_PCT_CUTOFF)
        & cohort["pb"].notna() & (cohort["pb"] < PB_MAX_CEIL)
    )
    cohort["qualify_via"] = "none"
    cohort.loc[qualify_pct & ~qualify_abs, "qualify_via"] = "percentile"
    cohort.loc[qualify_abs, "qualify_via"] = "absolute"
    cohort["in_fear_cohort"] = qualify_abs | qualify_pct
    return cohort


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
    washout_dd52 = fear[fear["in_washout_dd52"]].copy()
    meta["n_universe_pit"] = int(n_universe)
    meta["n_washout_dd52_cohort"] = int(len(washout_dd52))

    pct = pull_pb_percentile()                     # bắt buộc, KHÔNG nuốt lỗi (§29)
    washout_dd52 = washout_dd52.merge(pct, on="ticker", how="left")
    fear = apply_pb_or_logic(washout_dd52)
    n_fear_cohort = int(fear["in_fear_cohort"].sum())
    meta["n_fear_cohort"] = n_fear_cohort
    meta["n_qualify_absolute"] = int((fear["qualify_via"] == "absolute").sum())
    meta["n_qualify_percentile"] = int((fear["qualify_via"] == "percentile").sum())

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
            f"universe fear cohort RỖNG ([PB<{PB_MAX_ABS} HOẶC (percentile<={PB_PCT_CUTOFF:.0%} "
            f"AND PB<{PB_MAX_CEIL})] & washout<={WASHOUT_MIN_PCT:.0%} & dd52<={DD52_MAX_PCT:.0%}) "
            f"trong {n_universe} mã universe_pit — funnel dừng ở đây, không có gì để annotate "
            f"marginability/ADV.")
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

    # Cảnh báo tập trung ngành — INFORMATIONAL, không enforce (xem docstring mục 5 + PB_MAX_CEIL
    # constants). Funnel này stateless (không biết case nào đang armed) nên chỉ có thể cảnh báo
    # "N mã cùng ngành đều fully_qualified HÔM NAY", không thể tự áp cap "≤1 đồng thời mở" —
    # điều kiện đó cần state armed-position, sống ở discretionary_margin_gate.py (chưa làm).
    qualified = cohort[cohort["fully_qualified"]]
    for code, label in SECTOR_CONCENTRATION_WATCH.items():
        names = qualified.loc[qualified["icb_code"] == code, "ticker"].tolist()
        if len(names) >= 2:
            meta["warnings"].append(
                f"CẢNH BÁO tập trung ngành: {len(names)} mã {label} (ICB={code}) đều "
                f"fully_qualified hôm nay ({', '.join(sorted(names))}) — risk-auditor 2026-08-30 "
                f"(job Taylor_20260830_092103 bước 2) khuyến nghị cap intra-sector khi ARM "
                f"(CTCK: count<=1 AND combined exposure<=5% NAV; hoá chất/phân bón: <=1 margin "
                f"HOẶC <=2 cash-funded). Funnel này CHƯA enforce cap — chỉ cảnh báo. Enforcement "
                f"thật phải làm ở discretionary_margin_gate.py trước khi arm >1 mã cùng cụm.")

    return cohort, meta


COLS_DISPLAY = ["ticker", "washout_pct", "dd52_pct", "pb", "pb_pct_rank", "qualify_via",
                "icb_code", "rating", "golden_floor_pass", "insider_sell_flag", "redflag",
                "marginable", "margin_package_id", "adv_3m_vnd", "fully_qualified"]


def format_block(cohort, meta):
    lines = [f"=== Discretionary candidate funnel — {meta['run_at']} ===",
             f"universe_pit: {meta.get('n_universe_pit', '?')} mã | "
             f"washout<={WASHOUT_MIN_PCT:.0%} & dd52<={DD52_MAX_PCT:.0%}: "
             f"{meta.get('n_washout_dd52_cohort', '?')} mã | "
             f"[PB<{PB_MAX_ABS} HOẶC (percentile<={PB_PCT_CUTOFF:.0%} AND PB<{PB_MAX_CEIL})]: "
             f"{meta.get('n_fear_cohort', '?')} mã "
             f"(abs={meta.get('n_qualify_absolute', '?')}, "
             f"percentile={meta.get('n_qualify_percentile', '?')})"]
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
        pct_s = f"{r['pb_pct_rank']:.1%}" if pd.notna(r.get("pb_pct_rank")) else "N/A"
        line = (
            f"  {r['ticker']:6} washout={r['washout_pct']:.1%} dd52={r['dd52_pct']:.1%} "
            f"PB={r['pb']:.2f} pct_rank={pct_s} via={r.get('qualify_via', '?')} "
            f"icb={r.get('icb_code', 'NA')} rating={r.get('rating', 'NA')} "
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
