#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Funnel 8L hằng ngày cho discretionary sleeve — 2 làn trên `data/rating_8l.csv`
(plan `kb/projects/discretionary-8l-candidate-funnel-plan-20261006.md`, mục "Bản sửa sau trả lời
user 2026-10-06"; job Taylor_20261005_180152). Chạy 19:35 ICT T2-T6 SAU `pt_8l_daily` 19:20.
KHÔNG LLM, KHÔNG BQ — chỉ đọc file 8L đã chấm sẵn.

Vũ trụ chất lượng (cả 2 làn): rating<=3 ∧ golden floor (ROE_Min3Y>=0 ∧ CF_OA_3Y>0) ∧ redflag rỗng
∧ liq_bn>=0,3 tỷ ∧ KHÔNG thuộc: BANNED (`lag_forensic_filter.BANNED`) / `data/forensic_flags.csv`
severity=exclude có hiệu lực (`lag_forensic_filter._load_forensic_excludes`) / cờ nội bộ bán còn
trong cửa sổ 90 ngày (file `anomaly_gate` đọc, validate schema — `load_insider`). Kiểm CẢ 3, không giả định rating đã bake.
  Làn A "lệch giá":   pb_z<=-1 ∧ drop_pct<=-20 (drop_pct ĐƠN VỊ %, vd -59.9).
  Làn B "giá trị sâu": PE>0, xếp earn_yield GIẢM DẦN TRONG CÙNG route, top-3/route (loại trừ trước
                      khi xếp — mã bị loại không chiếm chỗ). KHÔNG dùng composite value_score.
Nhãn bối cảnh (KHÔNG loại), peer = cùng ICB_Code có liq_bn>=0,3 (ICB < 5 mã ⇒ fallback cùng route):
  KHÔNG-GIẢM — drop_pct > -10% (không cần Bobby);
  IDIO       — drop_pct <= trung vị peer − 15 điểm %;
  NGÀNH      — giảm đáng kể nhưng không tách khỏi peer >= 15pp ⇒ "cần Bobby trước" (macro-strategist,
               mù forward return). drop/peer không biết ⇒ NGÀNH (bảo thủ).

Lớp washout(400d)/dd52 + PB OR-logic + marginability của bản 2026-08-30 KHÔNG nằm trong làn A:
plan duyệt định nghĩa làn A chỉ bằng pb_z + drop_pct; AND thêm washout<=-30% sẽ cắt mất phần lớn
11 mã đối chiếu, OR thêm dd52 sẽ nới rộng ra ngoài định nghĩa ⇒ mâu thuẫn ⇒ chọn theo plan. Đường
cũ (BQ + probe DNSE margin) giữ nguyên sau cờ `--legacy-fear` để không mất code đã CONFIRMED.

Trạng thái `data/discretionary_candidates_state.json` (khoá ticker|làn): chỉ BÁO khi
  NEW      — chưa từng báo, HOẶC rời làn rồi quay lại khi đã quá cooldown 30 ngày lịch từ lần báo trước;
  PBZ_DROP — pb_z <= pb_z lần báo trước − 0,5 (xấu đi đáng kể; KHÔNG chịu cooldown — mỗi bậc 0,5
             là thông tin mới, tự giới hạn tần suất).
  SEED     — lần chạy đầu (state rỗng): mọi mã ghi sổ, khối 08:00 chỉ in "khởi tạo: N mã".
Chạy lại cùng asof ⇒ cùng danh sách báo (mục có last_reported==asof), không ghi đè thông tin.
asof lùi so với lần chạy trước / rating_8l dưới sàn sanity ⇒ KHÔNG ghi state, cảnh báo ở khối 08:00.
State hỏng ⇒ raise (không reset im lặng). Thứ tự ghi: snapshot → log → kết quả → state SAU CÙNG.
Ghi kèm: log `data/discretionary_candidates_log.csv` (MỌI mã trong làn mỗi asof — đo forward excess,
checkpoint 2027-04-06), snapshot PIT `data/rating_8l_daily/rating_8l_<asof>.csv`, kết quả
`data/discretionary_funnel_latest.json`. Mọi ghi = tmp + os.replace. asof = ngày ICT của mtime
`rating_8l.csv` (ngày tri thức 8L có mặt), KHÔNG phải ngày chạy.

DÙNG:
    python3 mike/bin/discretionary_candidate_funnel.py               # chạy funnel, ghi file, in bảng
    python3 mike/bin/discretionary_candidate_funnel.py --dry-run     # tính + in, KHÔNG ghi gì
    python3 mike/bin/discretionary_candidate_funnel.py --print-block # topic sáng: ĐỌC file kết quả,
                                                                       # không chạy lại funnel
    python3 mike/bin/discretionary_candidate_funnel.py [--json P] [--csv P]  # + ghi kết quả ra P
    python3 mike/bin/discretionary_candidate_funnel.py --legacy-fear [--json P --csv P]  # đường cũ
"""

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
MIKE_ROOT = os.path.join(WC_ROOT, "mike")
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(MIKE_ROOT, "bin"))

ICT = ZoneInfo("Asia/Ho_Chi_Minh")                        # §16: neo múi giờ tường minh

PROJECT = "lithe-record-440915-m9"
CLOUDSDK_CONFIG = "/home/trido/thanhdt/gcloud_dtienthanh"   # dtienthanh@gmail.com — cron không
                                                              # source wc_env.sh, đồng bộ
                                                              # insider_flags.py CLOUDSDK_CONFIG

DATA_DIR = os.path.join(WC_ROOT, "data")
RATING_8L_CSV = os.path.join(DATA_DIR, "rating_8l.csv")
INSIDER_FLAGS_JSON = os.path.join(DATA_DIR, "insider_flags.json")
FORENSIC_FLAGS_CSV = os.path.join(DATA_DIR, "forensic_flags.csv")
RESEARCH_OUT_DIR = os.path.join(MIKE_ROOT, "agents", "Taylor", "research",
                                 "discretionary_sleeve_candidate_funnel_20260830")

# --- Funnel 8L hằng ngày (plan 2026-10-06) ---
LIQ_MIN_BN = 0.3                  # tỷ VND/ngày — đủ size 5% NAV (~50tr/TK) ở trần 10% ADV
LANE_A_PBZ_MAX = -1.0
LANE_A_DROP_MAX = -20.0           # drop_pct đơn vị % (Close vs đỉnh 3 tháng)
LANE_B_TOP_PER_ROUTE = 3
IDIO_GAP_PP = 15.0                # IDIO ⇔ drop_pct <= trung vị route − 15 điểm %
PBZ_DROP_REPORT = 0.5
COOLDOWN_DAYS = 30
DROP_SIGNIFICANT = -10.0          # drop_pct <= -10% ⇒ "giảm đáng kể"; trên mức này ⇒ KHÔNG-GIẢM
PEER_MIN = 5                      # ICB peer (liq>=0,3) < 5 mã ⇒ fallback trung vị cùng route
# Sàn sanity rating_8l.csv (thật 2026-10-05: 770 dòng; non-null pb_z 96%, earn_yield 91%,
# drop_pct/liq_bn 100%). Dưới sàn ⇒ cảnh báo, KHÔNG báo mã mới, KHÔNG ghi state/log.
RATING_MIN_ROWS = 500
RATING_MIN_NONNULL = {"pb_z": 0.80, "drop_pct": 0.90, "earn_yield": 0.75, "liq_bn": 0.90}

LANE_NAMES = {"A": "lệch giá", "B": "giá trị sâu"}


def daily_paths(base_dir=DATA_DIR):
    """Đường dẫn các file của funnel hằng ngày; `base_dir` khác ⇒ sandbox (selfcheck/--out-dir)."""
    return {
        "state": os.path.join(base_dir, "discretionary_candidates_state.json"),
        "log": os.path.join(base_dir, "discretionary_candidates_log.csv"),
        "result": os.path.join(base_dir, "discretionary_funnel_latest.json"),
        "snap_dir": os.path.join(base_dir, "rating_8l_daily"),
    }

# --- Đường cũ --legacy-fear (bản 2026-08-30, giữ nguyên) ---
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


# Docstring gốc của đường cũ (2026-08-30) — các chú thích "docstring mục N" bên dưới trỏ vào đây:
# """Phễu candidate hệ thống cho sleeve margin đơn mã discretionary (TV1/DGC-style fear-buy) —
# VIỆC 2 của job discretionary-sleeve-candidate-funnel-20260830.
#
# Lỗ hổng nó vá: TV1/DGC vào sleeve qua quan sát TÌNH CỜ của user, không có phễu quét hệ thống,
# và KHÔNG có bước lọc marginability trong bất kỳ scan nào (TV1 UPCOM không marginable là lý do
# sleeve đang 0 case thật). Script này LẮP RÁP các mảnh đã có, KHÔNG viết lại logic:
#   1. Universe fear = washout>=30% (từ đỉnh cục bộ 400 ngày lịch) + dd52<=-20% (per-ticker, CÙNG
#      công thức capit_margin_lever — rolling 252-session high — áp cho từng mã thay vì VNINDEX)
#      AND [PB<1,0 tuyệt đối HOẶC (percentile PB<=70% AND PB<1,2)] — OR-logic PB thích ứng theo
#      chu kỳ, khoá bằng min-CV mechanical rule qua 7 episode lịch sử, quant-skeptic CONFIRMED
#      (job Taylor_20260830_085015 round 3, verify quant-skeptic_20260830_085357). Cơ sở
#      percentile = `universe_pit ∩ Volume>0` CÙNG NGÀY (không phải toàn bộ mã niêm yết) — xem
#      `research/discretionary_funnel_adaptive_pb_round3_20260830.md`. Washout/dd52 từ
#      `tav2_bq.ticker` JOIN `tav2_mike.universe_pit` (in_universe=True tại phiên gần nhất) —
#      cùng định nghĩa đã validate trong `research/discretionary_sleeve_correlation_risk_20260830.md`
#      (`analyze_corr.py` bước 1).
#   2. Quality floor = `data/rating_8l.csv` (rating_8l.py, 17:45 ICT hàng ngày) — golden floor
#      ROE_Min3Y>=0 AND CF_OA_3Y>0, rating<=3.
#   3. Negative screens = `data/insider_flags.json` (insider_flags.py) + cột `redflag` có sẵn
#      trong rating_8l.csv (NP_TTM<0 / debt/eq>3, forensic exclusion đã bake vào `rating`/`route`).
#   4. Marginability + %ADV = `marginability_check.py` (VIỆC 1, chỉ probe DNSE cho SHORTLIST đã
#      qua bước 1-3, không probe cả universe) + `adv_3m()` tái dùng nguyên hàm từ
#      `discretionary_margin_gate.py` (KHÔNG viết lại công thức ADV).
#   5. Cảnh báo tập trung ngành (informational, KHÔNG phải enforcement) — nếu >=2 mã cùng ICB
#      (CTCK=8777, hoá chất/phân bón=1357) đều fully_qualified, in cảnh báo theo risk-auditor
#      2026-08-30 (job Taylor_20260830_092103 bước 2, CONDITIONAL-APPROVE cả 2 cụm). Funnel này
#      STATELESS (không biết case nào đang armed) nên KHÔNG thể enforce cap "≤1 đồng thời mở" —
#      enforcement thật phải nằm ở `discretionary_margin_gate.py` (chưa làm, xem bus finding
#      discretionary-funnel-adaptive-pb-wire-step2-risk-20260830 + step3).
#
# Output: RECON — bảng xếp hạng ticker, KHÔNG auto-arm bất kỳ case nào. Người (Mike/user) review
# rồi mới đưa qua due-diligence sâu (fundamental-skeptic) và `discretionary_margin_gate.py arm`
# nếu muốn.


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


# =============================================================================================
# Funnel 8L hằng ngày (plan 2026-10-06) — làn A/B, sổ trạng thái, log, snapshot, khối topic
# =============================================================================================

def _atomic_write_bytes(path, data):
    """tmp + fsync + os.replace (§5): kill giữa chừng không bao giờ để lại file ghi dở; lỗi ⇒
    dọn .tmp rồi raise lại (không để rác cho lần sau)."""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    fd = os.open(d, os.O_RDONLY)                              # rename bền qua mất điện
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_write_text(path, text):
    _atomic_write_bytes(path, text.encode("utf-8"))


def prev_trading_day(d):
    """Phiên giao dịch gần nhất TRƯỚC ngày d (bỏ T7/CN + lễ của trading_bot.vn_market)."""
    from trading_bot.vn_market import is_holiday
    d = d - dt.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d -= dt.timedelta(days=1)
    return d


RATING_REQUIRED_COLS = ["ticker", "route", "rating", "ROE_Min3Y", "CF_OA_3Y", "redflag", "liq_bn",
                        "pb_z", "drop_pct", "PE", "PB", "earn_yield", "ICB_Code"]


def read_rating(path):
    """Đọc rating_8l.csv MỘT lần ⇒ (bytes, asof, DataFrame). Cùng bytes dùng cho tính làn lẫn
    snapshot — không thể lệch nhau. asof = ngày ICT của mtime; file bị ghi lại giữa lúc đọc ⇒ raise."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"thiếu {path} — pt_8l_daily chưa chạy?")
    m1 = os.stat(path).st_mtime_ns
    with open(path, "rb") as f:
        data = f.read()
    if os.stat(path).st_mtime_ns != m1:
        raise RuntimeError(f"{path} bị ghi lại trong lúc đọc (pt_8l_daily đang chạy?) — chạy lại")
    asof = dt.datetime.fromtimestamp(m1 / 1e9, tz=ICT).date()
    df = pd.read_csv(io.BytesIO(data))
    missing = [c for c in RATING_REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{path} thiếu cột {missing} — schema rating_8l đổi?")
    return data, asof, df


def rating_sanity(df):
    """Danh sách vi phạm sàn sanity (rỗng = đạt)."""
    bad = []
    if len(df) < RATING_MIN_ROWS:
        bad.append(f"{len(df)} dòng < sàn {RATING_MIN_ROWS}")
    for c, floor in RATING_MIN_NONNULL.items():
        r = float(df[c].notna().mean()) if len(df) else 0.0
        if r < floor:
            bad.append(f"{c} non-null {r:.0%} < sàn {floor:.0%}")
    return bad


def _insider_path():
    """MỘT nguồn đường dẫn cho cả cờ lẫn cảnh báo: đúng file `anomaly_gate` đọc."""
    import anomaly_gate
    return os.path.join(anomaly_gate.WORKDIR, "data", "insider_flags.json")


def load_insider(asof):
    """(flagged {ticker: rec}, warnings). Tự đọc + validate schema thay vì dựa vào
    `insider_sell_flagged(quiet=True)` (hàm đó nuốt mọi lỗi thành {} ⇒ funnel không biết mình
    đang KHÔNG lọc insider). Cửa sổ 2 đầu `asof-TTL <= last_alert <= asof` (TTL lấy từ
    anomaly_gate). File thiếu/hỏng/schema lạ ⇒ cảnh báo hiện ở khối 08:00, không im lặng."""
    from anomaly_gate import INSIDER_TTL_DAYS
    path = _insider_path()
    if not os.path.exists(path):
        return {}, [f"thiếu {path} — KHÔNG lọc được cờ nội bộ bán (insider)"]
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError) as e:
        return {}, [f"{path} hỏng ({e}) — KHÔNG lọc được cờ nội bộ bán (insider)"]
    if not isinstance(raw, dict):
        return {}, [f"{path} schema lạ (gốc là {type(raw).__name__}, cần dict ticker→cờ) — "
                    f"KHÔNG lọc được cờ nội bộ bán (insider)"]
    warnings, bad, flagged = [], [], {}
    lo, hi = asof - dt.timedelta(days=INSIDER_TTL_DAYS), asof
    for t, rec in raw.items():
        try:
            d = dt.date.fromisoformat(str(rec["last_alert"])[:10])
        except (TypeError, KeyError, ValueError):
            bad.append(str(t))
            continue
        if lo <= d <= hi:
            flagged[t] = rec
    if bad:
        warnings.append(f"insider_flags: {len(bad)} cờ thiếu/sai last_alert ({','.join(sorted(bad)[:10])})"
                        f" — KHÔNG xác định được cửa sổ, KHÔNG loại; kiểm insider_flags.py")
    age = (dt.datetime.now(ICT) - dt.datetime.fromtimestamp(os.path.getmtime(path), tz=ICT))
    if age.total_seconds() > 7 * 86400:
        warnings.append(f"{path} cũ {age.total_seconds() / 86400:.1f} ngày — cờ insider có thể thiếu")
    return flagged, warnings


def load_exclusions(asof, forensic_csv=FORENSIC_FLAGS_CSV, insider=None):
    """(banned:set, forensic:{ticker: ngày cờ | None}, insider:{ticker: rec}, warnings).
    Tái dùng BANNED/_load_forensic_excludes có sẵn. Forensic chỉ áp khi ngày cờ <= asof (chống
    look-ahead khi replay); dòng exclude ngày trống/NaT ⇒ LOẠI (fail-closed, giá trị None) + cảnh
    báo. `insider=None` ⇒ `load_insider(asof)` (file thật qua anomaly_gate.WORKDIR)."""
    from lag_forensic_filter import BANNED, EXCLUDE_SEVERITY, _load_forensic_excludes
    warnings = []
    asof_ts = pd.Timestamp(asof)
    if not os.path.exists(forensic_csv):
        raise FileNotFoundError(f"thiếu {forensic_csv} — không lọc được forensic exclude, dừng")
    forensic = {t: d for t, d in _load_forensic_excludes(forensic_csv).items()
                if pd.notna(d) and d <= asof_ts}
    ff = pd.read_csv(forensic_csv, dtype=str)
    is_ex = ff["severity"].fillna("").str.strip().str.lower() == EXCLUDE_SEVERITY
    no_date = ff["date"].fillna("").str.strip().map(lambda s: s == "" or pd.isna(pd.Timestamp(s)))
    nodate = sorted(set(ff.loc[is_ex & no_date, "ticker"].str.strip()))
    for t in nodate:
        forensic[t] = None
    if nodate:
        warnings.append(f"forensic_flags: dòng exclude KHÔNG có ngày ({','.join(nodate)}) ⇒ coi là "
                        f"LOẠI (fail-closed) — điền cột date")
    if insider is None:
        insider, i_warn = load_insider(asof)
        warnings += i_warn
    return set(BANNED), forensic, dict(insider), warnings


def context_label(drop, peer_med):
    """3 trạng thái: KHÔNG-GIẢM (drop > -10%, không cần Bobby) / IDIO (giảm sâu hơn trung vị
    peer >= 15 điểm %) / NGÀNH (giảm đáng kể nhưng KHÔNG tách khỏi peer >= 15pp ⇒ cần Bobby).
    drop hoặc trung vị peer không biết ⇒ NGÀNH (bảo thủ: không chứng minh được là riêng mã)."""
    if drop is None or pd.isna(drop):
        return "NGÀNH"
    if drop > DROP_SIGNIFICANT:
        return "KHÔNG-GIẢM"
    if peer_med is not None and not pd.isna(peer_med) and drop <= peer_med - IDIO_GAP_PP:
        return "IDIO"
    return "NGÀNH"


def build_lanes(rating, banned, forensic, insider):
    """rating: DataFrame rating_8l.csv. Trả (cands, excluded):
    cands    — 1 dòng / (ticker, làn) với nhãn bối cảnh;
    excluded — mã ĐÁNG LẼ vào làn nhưng bị loại bởi BANNED/forensic/insider (minh bạch)."""
    df = rating.copy()
    df["golden_floor_pass"] = (df["ROE_Min3Y"] >= 0) & (df["CF_OA_3Y"] > 0)
    quality = ((df["rating"] <= RATING_MAX) & df["golden_floor_pass"] & df["redflag"].isna()
               & (df["liq_bn"] >= LIQ_MIN_BN))

    def _why(t):
        why = []
        if t in banned:
            why.append("BANNED")
        if t in forensic:
            d = forensic[t]
            why.append(f"forensic_exclude({d.date() if d is not None else 'ngày trống'})")
        if t in insider:
            why.append(f"insider_sell({insider[t].get('last_alert')})")
        return ",".join(why)
    df["excl_reason"] = df["ticker"].map(_why)
    clean = df["excl_reason"] == ""

    lane_a = quality & (df["pb_z"] <= LANE_A_PBZ_MAX) & (df["drop_pct"] <= LANE_A_DROP_MAX)
    b_pool = quality & (df["PE"] > 0) & df["earn_yield"].notna()

    def _top_b(mask):
        sub = df[mask].sort_values(["route", "earn_yield", "ticker"],
                                   ascending=[True, False, True])
        sub = sub.groupby("route", sort=False).head(LANE_B_TOP_PER_ROUTE).copy()
        sub["lane_rank"] = sub.groupby("route").cumcount() + 1
        return sub

    a = df[lane_a & clean].assign(lane="A", lane_rank=pd.NA)
    b = _top_b(b_pool & clean).assign(lane="B")
    cands = pd.concat([a, b], ignore_index=True)

    # Minh bạch: ai bị loại khỏi làn VÌ danh sách loại trừ (B: so với top-3 khi KHÔNG loại trừ)
    ex_a = df[lane_a & ~clean].assign(lane="A")
    b_raw = _top_b(b_pool)
    ex_b = b_raw[b_raw["excl_reason"] != ""].assign(lane="B")
    excluded = pd.concat([ex_a, ex_b], ignore_index=True)[["ticker", "lane", "route", "excl_reason"]]

    # Nhãn bối cảnh: peer = cùng ICB_Code, thanh khoản liq>=0,3 (KHÔNG chỉ mã chất lượng — "cả ngành
    # cùng giảm" là câu hỏi về ngành, không về rổ rating); ICB < PEER_MIN mã ⇒ fallback cùng route.
    peers = df[(df["liq_bn"] >= LIQ_MIN_BN) & df["drop_pct"].notna()]
    icb_med = peers.groupby("ICB_Code")["drop_pct"].median()
    icb_n = peers.groupby("ICB_Code").size()
    route_med = peers.groupby("route")["drop_pct"].median()
    route_n = peers.groupby("route").size()

    def _peer(r):
        code = r["ICB_Code"]
        n = int(icb_n.get(code, 0)) if pd.notna(code) else 0
        if n >= PEER_MIN:
            return icb_med[code], f"ICB {int(code)} n={n}"
        return route_med.get(r["route"]), f"route {r['route']} n={int(route_n.get(r['route'], 0))}"
    pe = [_peer(r) for _, r in cands.iterrows()]
    cands["peer_median_drop"] = [p[0] for p in pe]
    cands["peer_basis"] = [p[1] for p in pe]
    cands["context"] = [context_label(d, m) for d, m in
                        zip(cands["drop_pct"], cands["peer_median_drop"])]
    cands = cands.sort_values(["lane", "route", "lane_rank", "ticker"],
                              na_position="last").reset_index(drop=True)
    return cands, excluded


def _num(x):
    return None if x is None or pd.isna(x) else float(x)


class AsofRegress(ValueError):
    """asof < last_run_asof: dữ liệu đi lùi (rating cũ được khôi phục?) — không ghi state."""


def update_state(state, cands, asof):
    """state (dict, có thể rỗng) + cands hôm nay ⇒ (state_mới, reported: list[dict]).
    Xem docstring module cho luật NEW / PBZ_DROP / cooldown. Thuần hàm, không I/O.
    Lần chạy đầu (state rỗng) ⇒ mọi mã nhận reason SEED (khởi tạo, KHÔNG phải "mới").
    asof < last_run_asof ⇒ raise AsofRegress."""
    asof_s = str(asof)
    st = json.loads(json.dumps(state or {}))                  # deep copy
    entries = st.setdefault("entries", {})
    last_run = st.get("last_run_asof")
    if last_run and asof_s < last_run:
        raise AsofRegress(f"asof {asof_s} < lần chạy trước {last_run} — dữ liệu 8L đi lùi; "
                          f"TỪ CHỐI ghi state")
    if not entries and "seeded_on" not in st:
        st["seeded_on"] = asof_s
    seeding = st.get("seeded_on") == asof_s
    if last_run == asof_s:                                    # chạy lại cùng asof
        ref_run = st.get("prev_run_asof")
    else:
        ref_run = last_run
        st["prev_run_asof"] = last_run
        st["last_run_asof"] = asof_s
    asof_d = dt.date.fromisoformat(asof_s)

    reported = []
    for _, r in cands.iterrows():
        key = f"{r['ticker']}|{r['lane']}"
        pbz = _num(r.get("pb_z"))
        e = entries.get(key)
        reason = None
        if e is None:
            reason = "SEED" if seeding else "NEW"
            e = entries[key] = {"ticker": r["ticker"], "lane": r["lane"],
                                "first_seen": asof_s}
        elif e.get("last_reported") == asof_s:
            reason = e.get("last_reason")                    # idempotent: đã báo ở asof này
        else:
            continuous = e.get("last_seen") in (asof_s, ref_run)
            last_rep = e.get("last_reported")
            cooled = (last_rep is None or
                      (asof_d - dt.date.fromisoformat(last_rep)).days >= COOLDOWN_DAYS)
            prev_pbz = e.get("last_reported_pb_z")
            if pbz is not None and prev_pbz is not None and pbz <= prev_pbz - PBZ_DROP_REPORT:
                reason = "PBZ_DROP"
            elif not continuous and cooled:
                reason = "NEW"
        if reason and e.get("last_reported") != asof_s:
            e["prev_reported_pb_z"] = e.get("last_reported_pb_z")
            e["last_reported"] = asof_s
            e["last_reported_pb_z"] = pbz
            e["last_reason"] = reason
        e["last_seen"] = asof_s
        if reason:
            reported.append({"ticker": r["ticker"], "lane": r["lane"], "reason": reason,
                             "prev_pb_z": e.get("prev_reported_pb_z")
                             if reason == "PBZ_DROP" else None})
    return st, reported


def load_state(path):
    """Thiếu ⇒ {} (lần đầu). Hỏng/schema lạ ⇒ RAISE — KHÔNG reset im lặng về {} (reset = báo lại
    toàn bộ như mới + mất mốc cooldown)."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        st = json.load(f)
    if not isinstance(st, dict) or not isinstance(st.get("entries", {}), dict):
        raise ValueError(f"{path} schema lạ (cần dict có 'entries' dict) — sửa tay, không tự reset")
    return st


LOG_COLS = ["date", "ticker", "lane", "route", "rating", "PE", "PB", "pb_z", "drop_pct",
            "liq_bn", "earn_yield", "context", "peer_median_drop", "peer_basis", "reported"]


def append_log(path, cands, asof, reported):
    """Ghi MỌI mã trong làn của asof; idempotent theo ngày (xoá dòng cùng date rồi ghi lại)."""
    rep = {(x["ticker"], x["lane"]): x["reason"] for x in reported}
    rows = cands.assign(date=str(asof)).copy()
    rows["reported"] = [rep.get((t, l), "") for t, l in zip(rows["ticker"], rows["lane"])]
    rows = rows[LOG_COLS]
    if os.path.exists(path):
        old = pd.read_csv(path, dtype={"date": str})
        rows = pd.concat([old[old["date"] != str(asof)], rows], ignore_index=True)
    _atomic_write_text(path, rows.to_csv(index=False))
    return len(rows)


def snapshot_rating(data, snap_dir, asof):
    """Chụp bytes rating_8l.csv (ĐÚNG bytes đã dùng tính làn) → snap_dir/rating_8l_<asof>.csv.
    'created' | 'unchanged' | 'replaced' (rating chạy lại cùng ngày ⇒ bản cuối ngày thắng)."""
    dst = os.path.join(snap_dir, f"rating_8l_{asof}.csv")
    if os.path.exists(dst):
        with open(dst, "rb") as f:
            if hashlib.md5(f.read()).hexdigest() == hashlib.md5(data).hexdigest():
                return "unchanged", dst
        status = "replaced"
    else:
        status = "created"
    _atomic_write_bytes(dst, data)
    return status, dst


def _rec(r):
    keep = ["ticker", "lane", "lane_rank", "route", "rating", "PE", "PB", "pb_z", "drop_pct",
            "liq_bn", "earn_yield", "context", "peer_median_drop", "peer_basis"]
    out = {}
    for k in keep:
        v = r.get(k)
        if k in ("ticker", "lane", "route", "context", "peer_basis"):
            out[k] = v
        elif k in ("rating", "lane_rank"):
            out[k] = None if v is None or pd.isna(v) else int(v)
        else:
            out[k] = _num(v)
    return out


def run_daily(rating_csv=RATING_8L_CSV, base_dir=DATA_DIR, write=True, now=None,
              forensic_csv=FORENSIC_FLAGS_CSV, insider=None):
    """Chạy funnel 1 lần. Trả dict kết quả (đồng thời ghi file nếu write=True).
    Thứ tự ghi: snapshot → log → KẾT QUẢ → STATE SAU CÙNG — crash giữa chừng không bao giờ
    đánh dấu "đã báo" cho mã chưa nằm trong file kết quả (chạy lại cùng asof báo lại y hệt)."""
    now = now or dt.datetime.now(ICT)
    paths = daily_paths(base_dir)
    data, asof, rating = read_rating(rating_csv)
    warnings = []
    if asof != now.date():
        warnings.append(f"rating_8l.csv KHÔNG phải của hôm nay: mtime ICT {asof} "
                        f"(chạy lúc {now:%Y-%m-%d %H:%M}) — pt_8l_daily 19:20 lỗi/trễ?")
    insane = rating_sanity(rating)
    if insane:
        warnings.append("DỮ LIỆU 8L DƯỚI SÀN SANITY: " + "; ".join(insane))
    banned, forensic, insider, ex_warn = load_exclusions(asof, forensic_csv, insider)
    warnings += ex_warn
    cands, excluded = build_lanes(rating, banned, forensic, insider)

    state = load_state(paths["state"])
    state_ok, new_state, rep_all = not insane, state, []
    if state_ok:
        try:
            new_state, rep_all = update_state(state, cands, asof)
        except AsofRegress as e:
            warnings.append(str(e))
            state_ok = False
    result = {
        "asof": str(asof), "run_at": now.isoformat(), "rating_csv": rating_csv,
        "warnings": warnings,
        "state_ok": state_ok, "sanity_fail": bool(insane),
        "n_lane_a": int((cands["lane"] == "A").sum()),
        "n_lane_b": int((cands["lane"] == "B").sum()),
        "n_tracking": int(cands["ticker"].nunique()),
        "seeded": sum(1 for x in rep_all if x["reason"] == "SEED"),
        "reported": [x for x in rep_all if x["reason"] != "SEED"],
        "candidates": [_rec(r) for _, r in cands.iterrows()],
        "excluded": excluded.to_dict(orient="records"),
    }
    if write:
        snap_status, snap_path = snapshot_rating(data, paths["snap_dir"], asof)
        result["snapshot"] = {"status": snap_status, "path": snap_path}
        if not insane:                                       # log đo forward excess: không ghi rác
            result["log_rows"] = append_log(paths["log"], cands, asof, rep_all)
        _atomic_write_text(paths["result"], json.dumps(result, ensure_ascii=False, indent=1))
        if state_ok:
            _atomic_write_text(paths["state"], json.dumps(new_state, ensure_ascii=False, indent=1))
    return result


def _vn(x, nd=1):
    return "?" if x is None else f"{x:.{nd}f}".replace(".", ",")


def candidate_line(c, reason=None, prev_pbz=None):
    ctx = c["context"] + (" — cần Bobby trước" if c["context"] == "NGÀNH" else "")
    if c["context"] != "KHÔNG-GIẢM":
        ctx += f" (peer {c.get('peer_basis')} trung vị {_vn(c.get('peer_median_drop'))}%)"
    lane = f"{c['lane']} {LANE_NAMES[c['lane']]}"
    if c["lane"] == "B":
        lane += f" #{c['lane_rank']} {c['route']}"
    tag = ""
    if reason == "PBZ_DROP":
        tag = f" [pb_z giảm thêm từ {_vn(prev_pbz, 2)}]"
    return (f"• {c['ticker']} · làn {lane} · rating {c['rating']} · PE {_vn(c['PE'])} · "
            f"pb_z {_vn(c['pb_z'], 2)} · drop {_vn(c['drop_pct'])}% · liq {_vn(c['liq_bn'], 2)} tỷ"
            f" · {ctx}{tag}")


def format_topic_block(result, today):
    """Khối cho daily_decision_topic.py. `result=None` ⇒ thiếu file (vẫn in, không im lặng).
    Danh sách "mới" chỉ là MỚI ở sáng ngay sau asof; T7/CN/T2 đọc lại kết quả thứ Sáu ⇒ ghi
    rõ "từ phiên <asof>"."""
    head = "**D. Funnel 8L (discretionary)**"
    if result is None:
        return f"{head}\n⚠️ CHƯA có kết quả funnel ({daily_paths()['result']}) — cron 19:35 chưa chạy?"
    lines = [f"{head} — dữ liệu 8L ngày {result['asof']}"]
    asof = dt.date.fromisoformat(result["asof"])
    expect = prev_trading_day(today)
    if asof < expect:
        lines.append(f"⚠️ KẾT QUẢ CŨ: asof {asof} < phiên gần nhất {expect} — funnel/pt_8l_daily "
                     f"không chạy hoặc lỗi; danh sách dưới đây KHÔNG phải của phiên gần nhất.")
    for w in result.get("warnings", []):
        lines.append(f"⚠️ {w}")
    if not result.get("state_ok", True):
        lines.append("⛔ KHÔNG báo mã mới phiên này (xem cảnh báo trên) — số 'đang theo dõi' "
                     "không đáng tin cho tới khi dữ liệu 8L đạt lại.")
        return "\n".join(lines)
    first_view = today == asof + dt.timedelta(days=1)
    since = "" if first_view else f" TỪ PHIÊN {asof} (đã hiện sáng {asof + dt.timedelta(days=1)})"
    if result.get("seeded"):
        lines.append(f"Khởi tạo{since}: {result['seeded']} mã đang theo dõi (lần chạy đầu — không "
                     f"báo hàng loạt là mới; từ phiên sau chỉ báo mã MỚI/xấu đi).")
    by_key = {(c["ticker"], c["lane"]): c for c in result["candidates"]}
    rep = result.get("reported", [])
    tracking = (f"{result['n_tracking']} đang theo dõi: A={result['n_lane_a']}, "
                f"B={result['n_lane_b']}")
    if not rep:
        if not result.get("seeded"):
            lines.append(f"0 mới{since} ({tracking})")
    else:
        lines.append(f"{len(rep)} mã mới/xấu đi{since} ({tracking}) — chọn mã nào đáng làm due "
                     f"diligence (mặc định: không làm gì):")
        for x in rep:
            lines.append(candidate_line(by_key[(x["ticker"], x["lane"])], x["reason"],
                                        x.get("prev_pb_z")))
    return "\n".join(lines)


def print_block(today=None, result_path=None):
    today = today or dt.datetime.now(ICT).date()
    path = result_path or daily_paths()["result"]
    result = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            result = json.load(f)
    return format_topic_block(result, today)


def format_run_report(result):
    lines = [f"=== Funnel 8L asof {result['asof']} (run {result['run_at']}) — "
             f"A={result['n_lane_a']} B={result['n_lane_b']} theo dõi={result['n_tracking']} "
             f"báo={len(result['reported'])} khởi tạo={result['seeded']} "
             f"state={'OK' if result['state_ok'] else 'KHÔNG GHI'} ==="]
    for w in result["warnings"]:
        lines.append(f"  CẢNH BÁO: {w}")
    rep = {(x["ticker"], x["lane"]): x for x in result["reported"]}
    for c in result["candidates"]:
        x = rep.get((c["ticker"], c["lane"]))
        mark = f"  <<< {x['reason']}" if x else ""
        lines.append(candidate_line(c, x and x["reason"], x and x.get("prev_pb_z")) + mark)
    for e in result["excluded"]:
        lines.append(f"  LOẠI {e['ticker']} (làn {e['lane']}, {e['route']}): {e['excl_reason']}")
    if "snapshot" in result:
        lines.append(f"  snapshot: {result['snapshot']['status']} {result['snapshot']['path']}")
        lines.append(f"  log: {result.get('log_rows', 'KHÔNG GHI (dưới sàn)')} dòng")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print-block", action="store_true",
                    help="Khối topic sáng: ĐỌC file kết quả mới nhất, không chạy lại funnel "
                         "(kèm --legacy-fear ⇒ khối của đường cũ)")
    ap.add_argument("--dry-run", action="store_true", help="Tính + in, KHÔNG ghi file nào")
    ap.add_argument("--out-dir", metavar="DIR",
                    help="Ghi state/log/result/snapshot vào DIR thay vì data/ (sandbox)")
    ap.add_argument("--rating-csv", metavar="PATH", default=RATING_8L_CSV,
                    help="Đọc rating_8l từ PATH (mặc định data/rating_8l.csv)")
    ap.add_argument("--legacy-fear", action="store_true",
                    help="Đường cũ 2026-08-30: BQ washout/dd52 + PB OR-logic + probe margin DNSE")
    ap.add_argument("--json", metavar="PATH", help="Ghi thêm JSON kết quả đầy đủ ra PATH")
    ap.add_argument("--csv", metavar="PATH", help="Ghi thêm CSV (đường mới: candidates) ra PATH")
    args = ap.parse_args(argv)

    if args.legacy_fear:
        return legacy_main(args)
    if args.print_block:
        if args.json or args.csv:
            ap.error("--json/--csv không dùng với --print-block (khối chỉ ĐỌC file kết quả)")
        print(print_block(result_path=daily_paths(args.out_dir)["result"]
                          if args.out_dir else None))
        return 0
    result = run_daily(rating_csv=args.rating_csv, base_dir=args.out_dir or DATA_DIR,
                       write=not args.dry_run)
    print(format_run_report(result))
    if args.json:
        _atomic_write_text(args.json, json.dumps(result, ensure_ascii=False, indent=1))
    if args.csv:
        _atomic_write_text(args.csv, pd.DataFrame(result["candidates"]).to_csv(index=False))
    return 0


def legacy_main(args):
    cohort, meta = run_funnel()
    print(format_block(cohort, meta))
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
