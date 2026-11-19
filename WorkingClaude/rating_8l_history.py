#!/usr/bin/env python3
"""rating_8l_history.py — POINT-IN-TIME historical reconstruction of the 8L 1-5 quality rating.

Goal (B2 of the FA_rating <- 8L group-aware project): replay rating_8l.py's rate_row() logic over the
FULL ticker_financial history so we get a (ticker, effective_date, rating 1-5, route) panel that can be
back-tested exactly like the flat fa_ratings table. We then map 1->A .. 5->E and re-run the per-group
forward-return IC diagnosis (B1) on the NEW rating to see, group by group, whether 8L preserves the
compounder monotonicity and FIXES the cyclical inversion the flat composite has.

Point-in-time honesty:
  - Each rating is computed ONLY from that quarter's financial row (no future data).
  - Effective date = Release_Date (when the financials became public) -> first tradable day >= that;
    untrusted Release_Date (copied from prior quarter or before quarter end) -> ticker_financial.time.
  - COMPOUNDER / CYCLICAL / REALESTATE / SECURITIES / INSURANCE: reconstructed EXACTLY (all inputs are in
    ticker_financial historically).
  - BANK: AQ-AWARE since 2026-09-27 (H1 wire, job Taylor_20260927_022319). rate_bank_hist() ports
    rating_8l.py::rate_bank() thresholds VERBATIM and feeds them point-in-time NPL / LLR-coverage from
    mike/data/fiinprox_bank_ratios_quarterly_20260914.csv (FiinPro-X, 27 banks, 2010Q1-2026Q2), taking
    for each eff_date the LATEST FiinPro quarter already past its publication lag (>=45d after quarter
    end; Q4 >=90d) -> no look-ahead. ROE stays the ticker_financial chain (ROE_Trailing -> ROE5Y ->
    ROE3Y) the old proxy used, so the 3/4 gate boundary is unchanged by construction (proof below).
    Falls back to rate_bank_proxy() (ROE-only) per row whenever the FiinPro file is missing or the
    bank/quarter has no usable NPL+coverage — never fails open to a fabricated grade.
    SOURCE CONTINUITY (FiinPro-X trial ended 2026-09-28, NO refresh): the file is a frozen HISTORY
    vintage and is only ever read for eff_date <= its last covered quarter. The live path for names we
    actually hold is the OCR pipeline `bank_npl_coverage_primary` (data/bank_npl_coverage_primary_*.csv
    -> data/bank_lens_v3.csv -> rating_8l.py::rate_bank), which keeps feeding the CURRENT row via
    override_current_bank_aq() below; this module's FiinPro read never needs to be refreshed.
    INVARIANT THAT MAKES THIS A DATA-HYGIENE WIRE, NOT A STRATEGY CHANGE: rate_bank_hist() and
    rate_bank_proxy() return <=3 iff ROE>=12%, =4 iff 8%<=ROE<12%, =5 iff ROE<8% — NPL/coverage only
    discriminate 1 vs 2 vs 3 INSIDE the <=3 region. Every V2.4 consumer of fa_ratings_8l gates on the
    binary rating<=3 (custom_basket.py BASKET_GATE_RATING=3, regime_size_overlay.py WEAK_RATING_MIN=4,
    golive_recommend_v23.py rating>=4, CAPIT_QEXIT r8l>3, build_universe_pit_quality QUALITY_OK<=3), so
    0 V2.4 decisions change. Verified by exhaustive grid + real-panel A/B in
    rating_8l_history_bank_aq_selfcheck.py. This stops holding if anyone sets BASKET_GATE_RATING<3 or
    switches ETF_LIQ to a quality=tilt variant (custompitgq), which DOES read 1/2/3 apart.
    ⚠️ THE INVARIANT IS ABOUT THE 3/4 BOUNDARY ONLY -- it says NOTHING about rating<=2, and the AQ
    data moves the 2/3 boundary a LOT: 266 of 981 BANK rows (27.1%) cross <=2 (1->3:153, 2->3:112,
    3->2:1). Consumers that gate at <=2, enumerated 2026-09-27 (quant-skeptic surfaced this gap):
      - mike/agents/Taylor/anomaly_scan.py:156 `query("rating<=2")` reads THIS table (via
        data/bq_cache/fa_ratings_8l.parquet) and runs on cron (08:20 T2-T6 inside
        ops_health_check.sh, plus fearbuy_weekly_scan.sh Friday 08:10). LIVE DELTA = exactly one
        name: ABB's latest row 3 -> 2, so ABB joins the tier-W quality watchlist. A watchlist, not a
        position or a sizing decision.
      - custom30v_hybrid.py (rating<=2 swap rule) reads fa_ratings_8l from BQ -> its BACKTEST would
        change across those 266 rows. R&D variant, not V2.4 production.
      - cheap_pb_floor.py, sector_lens_monitor.py, newdeals_daily_report.py also gate at <=2 but read
        data/rating_8l.csv (the LIVE rate_bank output), which this module never writes -> unaffected.
  - ROUTE (sector) is POINT-IN-TIME since 2026-09-27 (FAIL-G fix, audit measurement-integrity-2026-09-27):
    ICB_Code is taken from CONSECUTIVE RUNS of >=ICB_MIN_RUN (20) sessions in tav2_bq.ticker and as-of
    joined backward on eff_date, replacing the old `ANY_VALUE(ICB_Code) GROUP BY ticker`, which stamped
    TODAY's sector onto the whole 2014->now panel and was not even deterministic.
    ⚠️ DATA LIMIT, stated so nobody over-reads this fix: `tav2_bq.ticker` is a rebuilt daily panel, NOT a
    sector-vintage source. It records only 6 tickers with >1 ICB_Code ever, and 5 of the 6 first differ in
    2017 or later (2 of them only within the last 2 months) -> the source ESSENTIALLY DOES NOT RECORD
    re-classifications before 2026. So this fix guarantees (a) determinism and (b) correct PIT for the
    changes that ARE recorded; sector changes that were never recorded CANNOT be recovered from this
    table. Fixing those needs a vintaged sector source (FiinPro-X / HOSE industry history).
    Registry: mike/kb/data_registry/fundamentals/rating_8l_history.md.
  - POWER: the live rate_power() needs the lifecycle verdict (snapshot) -> we proxy with the D/E trajectory
    (STLTDebt_Eq_P0 vs _P4) + TTM-NP sign. Small-n group; flagged.

Writes data/rating_8l_history.csv and (optionally) loads it to BQ tmp table for the IC join.
Usage: python rating_8l_history.py
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

# Ngay hieu luc (eff_date) cua 1 dong rating khi vendor THIEU Release_Date = q_time + NULL_RD_EFF_OFFSET_DAYS.
# 2026-10-16 (user chi dao uoc luong ngay hieu luc; doi tu +45): do tren ticker_financial 2014+ — dong CO Release_Date
# thi time == Release_Date o 99,2% (=> `time` chinh la ngay cong bo/co du lieu); dong NULL la placeholder (qend+32,
# ID_Release rong, khong co phan ung khoi luong) hoac late-filer (phan ung bat dau dung k=0 so voi `time`). Nen KHONG
# cong 45 ngay (lam eff_date tuong lai, vd PMT 2026-10-18) va KHONG lui -1..3 ngay (khong co bang chung). Bao thu: qend+32
# ~ p90 do tre cong bo that (trung vi 29). Doi gia tri o DAY — 3 cho dung no (main, attach_icb_pit, bank_eff_date).
NULL_RD_EFF_OFFSET_DAYS = 0


def eff_date_of(release_date, q_time, rd_untrusted=None):
    """NGUON DUY NHAT cua eff_date: Release_Date, thieu thi q_time + NULL_RD_EFF_OFFSET_DAYS; Release_Date KHONG
    DANG TIN (rd_untrusted, xem release_date_untrusted) thi q_time DUNG BANG (khong cong offset — luat user duyet
    2026-10-20 la "eff_date = time"). Nhan Series HOAC scalar (cung kieu dau vao => cung kieu dau ra).
    3 noi dung: main(), attach_icb_pit(), bank_eff_date()."""
    rel = pd.to_datetime(release_date, errors="coerce")
    qt = pd.to_datetime(q_time, errors="coerce")
    fb = qt + pd.Timedelta(days=NULL_RD_EFF_OFFSET_DAYS)
    if hasattr(rel, "fillna"):
        out = rel.fillna(fb)
        if rd_untrusted is not None:
            bad = pd.Series(rd_untrusted, index=out.index).fillna(False).astype(bool)
            out = out.mask(bad, qt)
        return out
    if rd_untrusted is not None and pd.notna(rd_untrusted) and bool(rd_untrusted) and pd.notna(rel):
        return qt
    return fb if pd.isna(rel) else rel


# GUARD Release_Date (user duyet 2026-10-20, job Taylor_20261020_045223; bang chung:
# mike/agents/Taylor/research/rating_8l_lag_20261020/REPORT.md §0.3, §3). Vendor co luc CHEP Release_Date cua quy
# truoc sang quy moi (vd BGE 2026Q1: RD 2026-02-02 = RD 2025Q4, time 2026-05-04) => eff_date som ~91 ngay va ghi de
# dung dong rating quy truoc trong fa_ratings_8l. Luat: RD <= RD cua quy LIEN TRUOC (cung ma) HOAC RD < ngay cuoi
# quy => RD khong dang tin, eff_date = q_time (= ticker_financial.time). Co y KHONG ap cho cum RD 01-07/04 cua Q1
# 2025/2026 (chi "kha nang cao", khong chung minh duoc). Quy truoc thieu / RD quy truoc NULL => chi xet ve cuoi quy.
def release_date_untrusted(df):
    """Bool Series (cung index df) — True khi Release_Date khong dang tin theo luat tren. Can cot ticker, quarter
    ('YYYYQn'), Release_Date. RD NULL => False (da co fallback rieng trong eff_date_of)."""
    rd = pd.to_datetime(df["Release_Date"], errors="coerce")
    qs = df["quarter"].astype(str).str.extract(r"^(\d{4})Q([1-4])$")
    yr = pd.to_numeric(qs[0], errors="coerce"); qn = pd.to_numeric(qs[1], errors="coerce")
    qend = pd.to_datetime(dict(year=yr, month=qn * 3, day=1), errors="coerce") + pd.offsets.MonthEnd(0)
    qidx = yr * 4 + qn
    key = pd.DataFrame({"ticker": df["ticker"].values, "qidx": qidx.values, "rd": rd.values})
    prev = key.dropna(subset=["qidx"]).drop_duplicates(["ticker", "qidx"]).assign(qidx=lambda k: k["qidx"] + 1)
    prev_rd = key[["ticker", "qidx"]].merge(prev.rename(columns={"rd": "prev_rd"}), on=["ticker", "qidx"],
                                            how="left")["prev_rd"]
    prev_rd = pd.Series(pd.to_datetime(prev_rd.values), index=df.index)
    return ((rd <= prev_rd) | (rd < qend)).fillna(False) & rd.notna()

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))

# --- router sets (identical to rating_8l.py) ---
COMMODITY_MAP = {
 "DRI":"rubber","PHR":"rubber","DPR":"rubber","GVR":"rubber","TRC":"rubber","HRC":"rubber",
 "HPG":"iron_ore","HSG":"iron_ore","NKG":"iron_ore","SMC":"iron_ore","POM":"iron_ore",
 "DCM":"urea","DPM":"urea","DDV":"dap","LAS":"dap","DGC":"dap","CSV":"caustic_soda"}
SUGAR_SET = {"SLS","SBT","LSS","KTS","QNS"}
CEMENT_SET = {"CLH","HT1","HOM","BCC","HVX","SCJ","BTS","QNC","CCM"}
HOLDING_OVERRIDE = {"REE"}
REALESTATE_OVERRIDE = {"HHS"}
INSURANCE_ICB  = lambda c: pd.notna(c) and 8530 <= c <= 8579
SECURITIES_ICB = lambda c: pd.notna(c) and 8770 <= c <= 8779
# 5F-audited moat governance (user 2026-06-14, "siết A-mềm"): the quant moat +1 notch is honored ONLY for
# a 5F-WIDE moat (data/moat_tags.csv moat_tier); registry NARROW/NONE -> NO notch (NARROW can erode, must
# not reach AAA via the notch). Absent-from-registry -> notch kept (quant, audit dần). Quant-fortress
# (core>=10 -> prelim 1) is moat-independent and unaffected. PIT-honesty: the registry is a CURRENT (2026-06)
# verdict, so the no-notch override applies ONLY to ratings effective >= MOAT_GOV_CUTOFF (trailing window);
# deep history (2014-2024) keeps the point-in-time quant proxy. Bounded distortion: recent quarters only.
MOAT_TIER = {}
MOAT_GOV_CUTOFF = pd.Timestamp("2025-06-01")


def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        r = subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                           f'--project_id={PROJECT} --format=csv --max_rows=2000000',
                           capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    if not r.stdout.strip(): raise RuntimeError("bq no rows. stderr:\n"+r.stderr[-1500:])
    return pd.read_csv(StringIO(r.stdout.strip()))


# Pull FULL financial history. One row per (ticker, quarter). Includes _P4 leverage for the power proxy.
HIST_SQL = """
SELECT f.ticker, f.quarter, f.time AS q_time, f.Release_Date,
  f.ROIC3Y, f.ROIC_Min3Y, f.ROE_Min3Y, f.ROIC_Trailing, f.ROIC5Y, f.ROIC_Min5Y, f.ROE_Min5Y, f.ROE3Y, f.ROE5Y,
  f.ROE_Trailing, f.Debt_Eq_P0, f.Debt_Eq_P4, f.STLTDebt_Eq_P0, f.STLTDebt_Eq_P4, f.FSCORE,
  f.CF_OA_P0, f.CF_OA_P1, f.CF_OA_P2, f.CF_OA_P3, f.CF_OA_5Y,
  f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4, f.NP_P5, f.NP_P6, f.NP_P7,
  f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
  f.Revenue_P0, f.Revenue_P1, f.Revenue_P2, f.Revenue_P3,
  f.Revenue_P4, f.Revenue_P5, f.Revenue_P6, f.Revenue_P7,
  f.UnearnRev_P0, f.totalAsset_P0
FROM tav2_bq.ticker_financial AS f
WHERE f.time >= '2014-06-01'
"""

# ĐỀ XUẤT 2026-09-27 (audit measurement-integrity FAIL-G). Bản cũ:
#     SELECT t.ticker, ANY_VALUE(t.ICB_Code) ... GROUP BY t.ticker
# gán phân ngành CỦA HÔM NAY cho toàn bộ panel lịch sử 2014→nay, và `ANY_VALUE` KHÔNG tất định.
#
# ĐO THẬT 2026-09-27 trên `tav2_bq.ticker`:
#   - 1.285/1.291 mã chỉ có MỘT `ICB_Code` ⇒ nguồn gần như KHÔNG đổi theo thời gian.
#   - 6 mã có HAI giá trị; 3 trong số đó (DIH, HDG, SBM) nhảy qua ranh giới `route_of()`.
#   - Chỉ **4 mã** trên toàn bảng có >1 "đoạn" ICB_Code dài ≥20 phiên liên tiếp ⇒ tái phân ngành
#     THẬT là cực hiếm; phần còn lại là NHIỄU một-vài-phiên. SBM là ca mẫu: `ICB_Code` nhảy qua
#     lại 7535↔2357 suốt 2020-2025, mỗi lần 1-4 phiên. Vì thế chỉ as-of theo MIN(time) của mỗi mã
#     là KHÔNG đủ — nó biến một phiên nhiễu 2020-11-23 thành "đổi ngành vĩnh viễn".
#   - Hậu quả đã xảy ra, có artifact: `data/rating_8l_history.csv` dựng lại 2026-09-27 gán
#     HDG route=POWER cho MỌI dòng từ 2014-08-01, trong khi `ICB_Code=7535` của HDG chỉ xuất hiện
#     từ 2026-09-07 (trước đó 8633 = REALESTATE, 4.136 phiên). DIH cũng vậy (8633 từ 2026-08-21
#     áp hồi tố về 2011). HDG là thành viên rổ custom30V (26 lượt trong
#     `data/custom30v_8l_publish.csv`) ⇒ đây là ĐƯỜNG QUYẾT ĐỊNH, không phải hiển thị.
#
# Bản vá: lấy các ĐOẠN LIÊN TIẾP (run) của `ICB_Code`, chỉ coi là đổi ngành khi đoạn dài
# ≥ `ICB_MIN_RUN` phiên, rồi as-of join theo `eff_date`. Tất định theo định nghĩa (hết ANY_VALUE).
# ⚠️ GIỚI HẠN thừa nhận rõ: nguồn hầu như KHÔNG ghi lại tái phân ngành TRƯỚC 2026, nên bản vá chỉ
# đảm bảo TẤT ĐỊNH + đúng PIT cho những lần đổi ĐƯỢC GHI. Những lần đổi không được ghi thì
# **không sửa được từ dữ liệu này** — cần một nguồn phân ngành có vintage (FiinProX/HOSE).
ICB_MIN_RUN = 20   # số phiên liên tiếp tối thiểu để một ICB_Code được coi là ĐÃ XÁC LẬP
ICB_SQL = f"""
WITH d AS (
  SELECT t.ticker, t.time, CAST(t.ICB_Code AS INT64) AS icb,
         ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) rn
  FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL),
g AS (SELECT d.*, d.rn - ROW_NUMBER() OVER(PARTITION BY d.ticker, d.icb ORDER BY d.time) grp FROM d),
runs AS (SELECT ticker, icb, MIN(time) AS icb_from, COUNT(*) AS run_len
         FROM g GROUP BY ticker, icb, grp)
-- MỖI đoạn đủ dài là MỘT dòng hiệu lực riêng. KHÔNG `GROUP BY ticker, icb` + `MIN(icb_from)`:
-- gộp như vậy làm một mã đi X->Y->X mất lần QUAY LẠI X (as-of sau `icb_from` của Y sẽ mãi trả Y).
-- Hiện thực tế 0/1.291 mã gặp ca này (chỉ 4 mã có >1 đoạn >=20 phiên, không mã nào lặp lại mã cũ),
-- nên sửa ở đây là chặn bẫy latent — nếu ai hạ `ICB_MIN_RUN` thì nó sẽ thành bug thật.
-- Nhiều dòng cùng (ticker, icb) với `icb_from` khác nhau là VÔ HẠI cho `merge_asof` backward.
SELECT ticker, icb AS ICB_Code, icb_from
FROM runs WHERE run_len >= {ICB_MIN_RUN}
ORDER BY ticker, icb_from
"""


def attach_icb_pit(df, icb):
    """As-of join `ICB_Code` theo ngày hiệu lực (backward), thay cho `ANY_VALUE` toàn-lịch-sử.

    Dòng có ngày hiệu lực TRƯỚC đoạn ICB đầu tiên nhận mã SỚM NHẤT đã xác lập — trung thực nhất
    có thể (mã muộn hơn là hindsight). Mã không có đoạn nào ≥ICB_MIN_RUN (toàn nhiễu) rơi về
    NaN ⇒ `route_of()` trả COMPOUNDER, đúng như hành vi với ICB_Code NULL hiện tại.
    """
    # ĐỘ PHÂN GIẢI datetime phải ĐỒNG NHẤT ở CẢ HAI khoá, nếu không `merge_asof` NÉM MergeError
    # ("incompatible merge keys ... <M8[s]  và  <M8[us]") và chết cả lần build lịch sử 8L.
    # Đo thật trên pandas 3.0.2 (2026-09-28):
    #   pd.to_datetime([None])          -> datetime64[s]    (cột Release_Date rỗng HOÀN TOÀN)
    #   pd.to_datetime(["2020-03-31"])  -> datetime64[us]
    #   Series[s].fillna(Series[us])    -> GIỮ [s] của bên trái  (im lặng)
    # ⇒ lô nào mà Release_Date null TOÀN BỘ thì `_eff` ra [s] còn `icb_from` ra [us] ⇒ crash.
    # Production thường có Release_Date nên đây là bẫy LATENT, nhưng nó đã giết
    # `rating8l_icb_pit_selfcheck.py` T6 (không phải lỗi của test). Ép cả hai về [us] — nới từ [s]
    # lên [us] là KHÔNG mất mát (mọi giá trị ở đây là ngày, phần giây luôn = 0).
    _RES = "datetime64[us]"
    icb = icb.copy()
    icb["icb_from"] = pd.to_datetime(icb["icb_from"]).astype(_RES)
    icb = icb.sort_values(["ticker", "icb_from"])
    left = df.copy()
    # `eff_date` chưa tồn tại ở điểm gọi (nó được dựng ở cuối main) ⇒ dùng CHUNG eff_date_of() với main()
    # và bank_eff_date() — một nguồn duy nhất (§28), không dựng lại công thức ở từng nơi.
    left["_eff"] = eff_date_of(left["Release_Date"], left["q_time"], left.get("rd_untrusted")).astype(_RES)
    left = left.sort_values("_eff")
    out = pd.merge_asof(left, icb.sort_values("icb_from"), left_on="_eff",
                        right_on="icb_from", by="ticker", direction="backward")
    first = icb.groupby("ticker")["ICB_Code"].first()
    out["ICB_Code"] = out["ICB_Code"].fillna(out["ticker"].map(first))
    return out.drop(columns=["_eff", "icb_from"]).reset_index(drop=True)


# ---------- ported scorecards (faithful to rating_8l.py) ----------
def real_lev(r):
    v = r.get("STLTDebt_Eq_P0", np.nan)
    return v if pd.notna(v) else r.get("Debt_Eq_P0", np.nan)

def moat_tag(r, roe5y):
    gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]
    gpms = [g for g in gpms if pd.notna(g)]
    if not gpms: return "WEAK"
    gmean = float(np.mean(gpms))
    cv = (float(np.std(gpms))/gmean) if gmean > 0 else 9.0
    hi_level  = gmean >= 0.25
    stable    = (len(gpms) >= 4 and cv <= 0.20)
    hi_roe    = pd.notna(roe5y) and roe5y >= 0.15
    if gmean < 0.15 or (pd.notna(roe5y) and roe5y < 0.10): return "WEAK"
    if hi_level and stable and hi_roe: return "STRONG"
    if (hi_level and (stable or hi_roe)) or (stable and hi_roe): return "MODERATE+"
    return "MODERATE"

def core_score(r):
    ttm_cfo = sum(r.get("CF_OA_P%d"%i, np.nan) for i in range(4))
    ttm_np  = sum(r.get("NP_P%d"%i,    np.nan) for i in range(4))
    cfo_np  = (ttm_cfo/ttm_np) if (pd.notna(ttm_np) and ttm_np != 0) else np.nan
    roic, roicm, roe_tr, de, fs = r.get("ROIC3Y",np.nan), r.get("ROIC_Min3Y",np.nan), r.get("ROE_Trailing", np.nan), real_lev(r), r.get("FSCORE", np.nan)
    s  = (2 if roic>=0.15 else 1 if roic>=0.10 else 0) if pd.notna(roic) else 0
    s += (2 if roicm>=0.10 else 1 if roicm>=0.05 else 0) if pd.notna(roicm) else 0
    s += (2 if roe_tr>=0.18 else 1 if roe_tr>=0.12 else 0) if pd.notna(roe_tr) else 0
    s += (2 if de<=0.3 else 1 if de<=1.0 else 0) if pd.notna(de) else 0
    s += (2 if (pd.notna(cfo_np) and cfo_np>=1.0 and ttm_cfo>0) else 1 if (pd.notna(cfo_np) and cfo_np>=0.7) else 0)
    s += (2 if fs>=8 else 1 if fs>=6 else 0) if pd.notna(fs) else 0
    return s, (round(cfo_np,2) if pd.notna(cfo_np) else np.nan), ttm_np

def stability(r):
    s = 1.0
    if r.get("route") not in ("BANK","INSURANCE","SECURITIES"):
        gpms = [r.get("GPM_P%d"%i, np.nan) for i in range(8)]; gpms = [g for g in gpms if pd.notna(g)]
        if len(gpms) >= 4:
            m = float(np.mean(gpms))
            if m > 0:
                cv = float(np.std(gpms))/m
                s = min(s, 1.0 if cv<=0.20 else 0.8 if cv<=0.40 else 0.55)
    rt, r3 = r.get("ROE_Trailing", np.nan), r.get("ROE3Y", np.nan)
    if pd.notna(rt) and pd.notna(r3) and r3 > 0:
        ratio = rt/r3
        s = min(s, 1.0 if ratio<=1.3 else 0.75 if ratio<=1.8 else 0.5)
    return round(s, 2)

def redflag(r, ttm_np):
    rs = []
    if pd.notna(ttm_np) and ttm_np < 0: rs.append("NP_TTM<0")
    lev = real_lev(r)
    if pd.notna(lev) and lev > 3: rs.append("debt/eq>3")
    return ",".join(rs)

def bin_core(s):
    return 1 if s>=10 else 2 if s>=7 else 3 if s>=4 else 4 if s>=2 else 5

def eq_flag(r):
    """Earnings-quality gate for COMPOUNDER/CYCLICAL (identical logic to rating_8l.py.eq_flag, int return).
    TWO TIERS (structural tier added 2026-06-17 to fix HAG quarter-to-quarter flicker):
      * IMPAIRED(5) = STRUCTURAL: 2-year (8q) cumulative NP/GP >= 0.65 AND CF_OA_5Y <= 0, levered. Both
        legs slow-moving -> catches HAG's lumpy non-core gains whichever quarter they land in, immune to
        one-off COVID scars. Fires HAG every quarter 2023Q4->2026Q1 (incl. 2025Q4 the old gate missed).
      * SPECULATIVE(4) = TRANSIENT: TTM (4q) NP/GP >= 0.90, levered, 5Y cash still positive.
    Leverage precondition (real_lev>=0.25) spares net-cash holdcos (VEA/PHR). Cash leg vetoes cyclical
    margin-troughs (HPG/BSR, positive 5Y cash); non-core leg vetoes operating-loss recoverers (VJC/FRT).
    Fail-safe on missing data (8q unavailable -> TTM-4 leg only)."""
    lev = real_lev(r)
    if not (pd.notna(lev) and lev >= 0.25): return 0
    def _npgp(n):
        np_ = [r.get("NP_P%d"%i, np.nan) for i in range(n)]
        rev = [r.get("Revenue_P%d"%i, np.nan) for i in range(n)]
        gpm = [r.get("GPM_P%d"%i, np.nan) for i in range(n)]
        if any(pd.isna(x) for x in np_ + rev + gpm): return None
        tot_np = sum(np_); tot_gp = sum(g*v for g, v in zip(gpm, rev))
        if tot_np <= 0: return None
        return np.inf if tot_gp <= 0 else tot_np/tot_gp
    cf5 = r.get("CF_OA_5Y", np.nan)
    nocash = pd.notna(cf5) and cf5 <= 0
    r8 = _npgp(8)
    if r8 is not None and r8 >= 0.65 and nocash: return 5
    r4 = _npgp(4)
    if r4 is not None and r4 >= 0.90: return 5 if nocash else 4
    return 0

def rate_securities(r):
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe
    ttm_np = sum(r.get("NP_P%d"%i, np.nan) for i in range(4))
    if (pd.notna(roe) and roe < 0) or (pd.notna(ttm_np) and ttm_np < 0): return 5
    if pd.notna(roe) and roe>=0.13 and pd.notna(r3) and r3>=0.11: return 2
    if pd.notna(roe) and roe>=0.09 and pd.notna(r3) and r3>=0.07: return 3
    if pd.notna(roe) and roe>=0.05: return 4
    return 5

def rate_insurance(r):
    roe_tr = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe_tr): roe_tr = r.get("ROE_Min3Y", np.nan)
    if pd.notna(roe_tr) and roe_tr < 0: return 5
    r3 = r.get("ROE3Y", np.nan)
    if pd.isna(r3): r3 = roe_tr
    if pd.notna(roe_tr) and roe_tr>=0.15 and pd.notna(r3) and r3>=0.12: return 1
    if pd.notna(roe_tr) and roe_tr>=0.11 and pd.notna(r3) and r3>=0.09: return 2
    if pd.notna(roe_tr) and roe_tr>=0.07: return 3
    if pd.notna(roe_tr): return 4
    return 4

def rate_realestate(r, cfo_np, ttm_np):
    if pd.notna(ttm_np) and ttm_np < 0: return 5
    roe_tr, roic, de, fs, roicm = r.get("ROE_Trailing",np.nan), r.get("ROIC3Y",np.nan), real_lev(r), r.get("FSCORE", np.nan), r.get("ROIC_Min3Y",np.nan)
    unearn, assets = r.get("UnearnRev_P0",np.nan), r.get("totalAsset_P0",np.nan)
    pipeline = (unearn/assets) if (pd.notna(unearn) and pd.notna(assets) and assets>0) else np.nan
    s  = (2 if (pd.notna(roe_tr) and roe_tr>=0.18) else 1 if (pd.notna(roe_tr) and roe_tr>=0.10) else 0)
    s += (2 if (pd.notna(roic) and roic>=0.12) else 1 if (pd.notna(roic) and roic>=0.07) else 0)
    s += (2 if (pd.notna(de) and de<=0.5) else 1 if (pd.notna(de) and de<=1.5) else 0)
    s += (1 if (pd.notna(cfo_np) and cfo_np>=0.8) else 0)
    s += (1 if (pd.notna(fs) and fs>=6) else 0)
    s += (1 if (pd.notna(roicm) and roicm>=0) else 0)
    s += (1 if (pd.notna(pipeline) and pipeline>=0.15) else 0)
    return 2 if s>=6 else 3 if s>=4 else 4

# ---------- BANK asset quality, point-in-time (H1 wire 2026-09-27) ----------
# Registry: mike/kb/data_registry/fundamentals/fiinprox_bank_ratios_quarterly.md (status DERIVED).
# Trap 6 of that entry is exactly why avail_date() exists: the file carries NO publication date, so a
# quarter may only be read after its statutory lag. Overridable for the selfcheck sandbox ONLY.
BANK_AQ_CSV = os.environ.get(
    "BANK_AQ_CSV", os.path.join(WORKDIR, "mike", "data", "fiinprox_bank_ratios_quarterly_20260914.csv"))
BANK_AQ = {}          # (ticker, "YYYYQn") -> dict(npl=decimal|None, cov=decimal|None)
BANK_AQ_BY_TK = {}    # ticker -> [(avail_date, "YYYYQn"), ...] sorted by avail_date
_QEND = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def bank_aq_avail_date(q):
    """First date a FiinPro quarter may be READ: quarter end + 45d (Q4 + 90d). PIT gate, see trap 6."""
    y, qq = int(q[:4]), int(q[-1])
    m, d = _QEND[qq]
    return pd.Timestamp(year=y, month=m, day=d) + pd.Timedelta(days=90 if qq == 4 else 45)


def load_bank_aq():
    """Load FiinPro quarterly NPL / LLR-coverage into BANK_AQ. Missing file -> empty dict, and every
    bank row then falls back to rate_bank_proxy (ROE-only) -> the pre-wire behaviour, never fail-open."""
    global BANK_AQ, BANK_AQ_BY_TK
    BANK_AQ, BANK_AQ_BY_TK = {}, {}
    try:
        fp = pd.read_csv(BANK_AQ_CSV)
    except Exception as e:
        print(f"  [bank-AQ hist] FiinPro file unavailable -> ROE-only proxy for ALL bank rows: {e}")
        return
    for _, row in fp.iterrows():
        q = f"{int(row['year'])}Q{int(row['quarter'])}"
        npl = row.get("npl_ratio_3_5_pct"); cov = row.get("llr_coverage_pct")
        npl = float(npl) / 100.0 if pd.notna(npl) else None
        cov = float(cov) / 100.0 if pd.notna(cov) else None
        if npl is None and cov is None: continue          # nim_only rows carry no asset quality
        BANK_AQ[(row["ticker"], q)] = dict(npl=npl, cov=cov)
    for (tk, q) in BANK_AQ:
        BANK_AQ_BY_TK.setdefault(tk, []).append((bank_aq_avail_date(q), q))
    for tk in BANK_AQ_BY_TK:
        BANK_AQ_BY_TK[tk].sort()
    print(f"  [bank-AQ hist] {len(BANK_AQ)} bank-quarter NPL/LLR rows, {len(BANK_AQ_BY_TK)} banks "
          f"from {os.path.basename(BANK_AQ_CSV)} (PIT lag >=45d, Q4 >=90d)")


def bank_aq_asof(ticker, eff_date):
    """Latest FiinPro quarter for `ticker` whose publication lag has elapsed by `eff_date`.
    Returns (npl, cov, quarter_label); (None, None, "") when nothing is readable yet."""
    hist = BANK_AQ_BY_TK.get(ticker)
    if not hist or pd.isna(eff_date): return None, None, ""
    best_q = ""
    for avail, q in hist:                                  # sorted by avail -> last one <= eff wins
        if avail <= eff_date: best_q = q
        else: break
    if not best_q: return None, None, ""
    f = BANK_AQ[(ticker, best_q)]
    return f["npl"], f["cov"], best_q


def bank_eff_date(r):
    """Same effective date main() stamps on the row (eff_date_of): Release_Date, else q_time + NULL_RD_EFF_OFFSET_DAYS;
    Release_Date khong dang tin (rd_untrusted) => q_time."""
    return eff_date_of(r.get("Release_Date"), r.get("q_time"), r.get("rd_untrusted"))


def rate_bank_hist(r):
    """AQ-aware historical bank rating. Thresholds copied VERBATIM from rating_8l.py::rate_bank();
    ROE uses the same ticker_financial chain as rate_bank_proxy, so the <=3 / >=4 boundary is
    identical to the proxy (see module docstring invariant). No AQ readable -> proxy."""
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE5Y", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    if pd.isna(roe): return 3                              # same as proxy / rate_bank "bank-noROE"
    if roe < 0.08: return 5                                # only genuine weakness -> 5
    npl, cov, _q = bank_aq_asof(r.get("ticker"), bank_eff_date(r))
    if npl is None and cov is None:
        return rate_bank_proxy(r)                          # no AQ yet -> pre-wire behaviour
    pristine = npl is not None and npl <= 0.012 and cov is not None and cov >= 1.5
    strong   = npl is not None and npl <= 0.020 and cov is not None and cov >= 0.9
    if roe >= 0.15 and pristine: return 1                  # elite asset-quality
    if roe >= 0.14 and strong:   return 2                  # strong asset-quality
    if roe >= 0.12: return 3                               # profitable (AQ-modulated)
    return 4                                               # modest ROE


def rate_bank_proxy(r):
    """HISTORICAL proxy: ROE-only (no NPL/coverage history). Mirrors the franchise base of rate_bank()."""
    roe = r.get("ROE_Trailing", np.nan)
    if pd.isna(roe): roe = r.get("ROE5Y", np.nan)
    if pd.isna(roe): roe = r.get("ROE3Y", np.nan)
    if pd.isna(roe): return 3
    if roe < 0.08: return 5
    if roe >= 0.18: return 1       # elite ROE (proxy for elite franchise; no AQ data to gate)
    if roe >= 0.14: return 2
    if roe >= 0.12: return 3
    return 4

def rate_power_proxy(r, ttm_np):
    """HISTORICAL proxy for the debt-paydown lifecycle: D/E trajectory (STLTDebt_Eq_P0 vs _P4) + TTM-NP."""
    de0 = r.get("STLTDebt_Eq_P0", np.nan)
    if pd.isna(de0): de0 = r.get("Debt_Eq_P0", np.nan)
    de4 = r.get("STLTDebt_Eq_P4", np.nan)
    if pd.isna(de4): de4 = r.get("Debt_Eq_P4", np.nan)
    if pd.notna(ttm_np) and ttm_np < 0:
        return 5 if (pd.notna(de0) and de0 > 1.0) else 4         # losing money: stress
    if pd.isna(de0): return 3
    if de0 <= 0.3 and (pd.isna(de4) or de0 <= de4): return 2     # mature / low-debt yield
    if pd.notna(de4) and de0 < de4 - 0.05: return 3             # actively paying down = pre-inflection
    if pd.notna(de4) and de0 > de4 + 0.10 and de0 > 1.0: return 4  # leveraging up + high debt = stress
    return 3

def route_of(tk, icb):
    if tk in HOLDING_OVERRIDE: return "COMPOUNDER"
    if tk in REALESTATE_OVERRIDE: return "REALESTATE"
    if icb == 8355: return "BANK"
    if INSURANCE_ICB(icb): return "INSURANCE"
    if SECURITIES_ICB(icb): return "SECURITIES"
    if icb == 7535: return "POWER"
    if tk in COMMODITY_MAP or tk in SUGAR_SET or tk in CEMENT_SET: return "CYCLICAL"
    if icb == 8633: return "REALESTATE"
    return "COMPOUNDER"

def rate_row(r):
    route = r["route"]
    s, cfo_np, ttm_np = core_score(r)
    if route == "SECURITIES": return rate_securities(r)
    if route == "INSURANCE":  return rate_insurance(r)
    if route == "REALESTATE": return rate_realestate(r, cfo_np, ttm_np)
    if route == "BANK":       return rate_bank_hist(r)
    if route == "POWER":      return rate_power_proxy(r, ttm_np)
    rf = redflag(r, ttm_np)
    if route == "CYCLICAL":
        if rf: return 5
        if pd.notna(real_lev(r)) and real_lev(r) > 1.5: return 5
        prelim = bin_core(s)
        fortress = (pd.notna(real_lev(r)) and real_lev(r)<=0.2 and pd.notna(r.get("ROIC3Y")) and r["ROIC3Y"]>=0.20)
        rating = prelim if prelim>=2 else (1 if fortress else 2)
        return max(rating, eq_flag(r))          # earnings-quality gate (downgrade-only)
    # COMPOUNDER
    if rf: return 4   # red-flag -> impaired, but profitable->4 floor applies (5 only via... see live: 5->4)
    prelim = bin_core(s)
    rating = prelim
    moat = moat_tag(r, r.get("ROE5Y", np.nan))
    if moat=="STRONG" and prelim in (2,3):
        _eff = pd.to_datetime(r.get("Release_Date"), errors="coerce")
        _recent = pd.notna(_eff) and _eff >= MOAT_GOV_CUTOFF
        _tier = MOAT_TIER.get(r.get("ticker"))
        _revoke = _recent and (_tier is not None and _tier != "WIDE")   # 5F NARROW/NONE: no AAA notch (recent)
        if not _revoke: rating = prelim-1
    stab_cap = stability(r)
    if pd.notna(stab_cap) and stab_cap <= 0.5 and rating < 3: rating = 3
    if rating == 5: rating = 4
    return max(rating, eq_flag(r))              # earnings-quality gate (downgrade-only, post-moat)


# ---- bank-nodata DOWNGRADE-ONLY + cổng chặn (phương án B, user duyệt 2026-11-19 21:5x ICT,
#      job Taylor_20261119_145312) -------------------------------------------------------------------
NODATA_NOTES = ("bank-nodata", "bank-noROE")
BANK_NODATA_FLOOR = 4            # mã bank thiếu lens ⇒ dòng live mới nhất KHÔNG được tốt hơn 4 (cổng ≤3 chặn)
# Ngưỡng G3: tỉ lệ (nodata ∪ noROE)/số mã BANK trong rating_8l.csv. Đo 2026-11-19: 10/28 = 35,7% là
# CẤU TRÚC (18 mã lens / 28 mã BANK). 45% chừa chỗ cho +2..3 mã bank mới niêm yết chưa có lens
# (12/30=40,0%, 13/31=41,9%) mà vẫn bắt việc mất ≥3 mã lens (13/28=46,4%). Mất 1-2 mã lens (nodata) do G2/G4
# bắt; mất ROE của 1-2 mã còn trong lens (noROE) do G4 bắt (G2 không áp được) — G3 chỉ là lưới cho mất hàng loạt.
BANK_NODATA_MAX_FRAC = 0.45


def _bank_gate_bus_event(reasons, notify_err):
    """Dấu vết BỀN ngoài log (log cron không ai đọc): append bus event `warning` do Winston đứng tên. PHẠM VI THẬT
    (đã kiểm 2026-11-19): event vào kb/events_buffer.md + tóm tắt Fleet Updates #mike; KHÔNG vào delta-append của
    mike_json.py (chỉ finding/answer/decision/verification) và ops_health_check.sh KHÔNG quét `warning` ⇒ đây là
    dấu vết để điều tra sau, KHÔNG phải kênh có người/checker chủ động đọc — kênh chủ động vẫn là Discord. Dedup: marker JSON = hash(reasons +
    ngày ICT + notify_lỗi?) ⇒ cùng bộ lý do cùng ngày chỉ ghi 1 lần (GIỚI HẠN: ngày mới hoặc bộ lý do đổi thì
    ghi lại; marker chỉ ghi SAU khi append rc=0 nên lỗi append sẽ được thử lại ở run sau). Chỉ gọi ở live_run."""
    import json, hashlib
    from datetime import datetime
    from zoneinfo import ZoneInfo
    day = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d")
    key = hashlib.sha1(json.dumps([sorted(reasons), day, bool(notify_err)], ensure_ascii=False).encode()).hexdigest()
    marker = os.environ.get("R8L_BANK_GATE_MARKER") or os.path.join(WORKDIR, "data", "bank_gate_alert_marker.json")
    try:
        with open(marker, encoding="utf-8") as f:
            if json.load(f).get("key") == key:
                print(f"  [bank-gate] bus event DEDUP (cùng bộ lý do trong ngày {day}, marker {marker})"); return
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"  [bank-gate] marker {marker} đọc lỗi ({type(e).__name__}: {e}) — ghi bus event lại")
    bus = os.environ.get("R8L_BANK_GATE_BUS") or os.path.join(WORKDIR, "mike", "bin", "append_event.sh")
    payload = {"reasons": reasons, "notify_error": notify_err, "day": day,
               "measured_by": "rating_8l_history.bank_nodata_gate / override_current_bank_aq lúc chạy"}
    try:
        r = subprocess.run([bus, "Winston", "warning", "fa_ratings_8l-bank-nodata-gate",
                            json.dumps(payload, ensure_ascii=False)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"  [bank-gate] append_event rc={r.returncode} — bus CHƯA có dấu vết. stderr thật: "
                  f"{r.stderr.strip()[-500:]}"); return
        tmp = marker + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump({"key": key, "day": day}, f)
        os.replace(tmp, marker)
    except Exception as e:
        print(f"  [bank-gate] gọi {bus} lỗi — bus CHƯA có dấu vết: {type(e).__name__}: {e}")


def _bank_gate_alert(text, send, reasons=None):
    """Cảnh báo TO khi cổng chặn bật: luôn in banner vào log; ghi R8L_BANK_GATE_ALERT_SINK nếu có (selfcheck);
    gửi Trading Daily qua notify_thread.sh CHỈ khi `send` (run canonical/ép BQ) và không ở chế độ test; cùng
    điều kiện đó ghi bus event bền (_bank_gate_bus_event), kèm lỗi notify nếu có.
    Lỗi gửi ⇒ in rc + stderr THẬT (§29), không nuốt."""
    print("!" * 100 + "\n" + text + "\n" + "!" * 100)
    sink = os.environ.get("R8L_BANK_GATE_ALERT_SINK")
    if sink:
        with open(sink, "a", encoding="utf-8") as f: f.write(text + "\n---\n")
    if not send or os.environ.get("MIKE_BOT_TEST_MODE") == "1":
        print("  [bank-gate] alert KHÔNG gửi Discord (run thí nghiệm/test) — chỉ log"); return
    notify = os.environ.get("R8L_BANK_GATE_NOTIFY") or os.path.join(WORKDIR, "mike", "bin", "notify_thread.sh")
    notify_err = None
    try:
        r = subprocess.run([notify, text, "trading_daily"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            notify_err = f"notify_thread.sh rc={r.returncode} stderr={r.stderr.strip()[-500:]}"
            print(f"  [bank-gate] {notify_err} — CẢNH BÁO CHƯA TỚI Discord")
    except Exception as e:
        notify_err = f"gọi {notify} lỗi: {type(e).__name__}: {e}"
        print(f"  [bank-gate] {notify_err} — CẢNH BÁO CHƯA TỚI Discord")
    _bank_gate_bus_event(reasons if reasons else [text], notify_err)


def bank_nodata_gate(lb):
    """Cổng chặn trước khi hạ hạng hàng loạt. Trả (lý do bật cổng [list str], tập ticker lens hiện tại|None).
    Bất kỳ lý do nào ⇒ run này KHÔNG hạ hạng mã nodata nào (giữ proxy như trước phương án B) + cảnh báo.
      G1 bank_lens_v3.csv đọc lỗi / rỗng (rating_8l.py:551-556 chỉ print ⇒ MỌI bank thành nodata).
      G2 mã mang nhãn bank-nodata NHƯNG có trong lens file hiện tại (2 nguồn mâu thuẫn).
      G3 tỉ lệ nodata trong BANK > BANK_NODATA_MAX_FRAC (hoặc không có dòng BANK nào).
      G4 mã có hạng lens THẬT ở snapshot kỳ trước nay mang nhãn bank-nodata HOẶC bank-noROE (noROE = mã CÒN
         trong lens nhưng ROE NaN ⇒ G2 không thấy được; snapshot đọc lỗi cũng bật cổng)."""
    import json
    reasons = []
    lens_path = os.path.join(WORKDIR, "data", "bank_lens_v3.csv")
    lens = None
    try:
        _ld = pd.read_csv(lens_path)
        lens = set(_ld["ticker"].dropna().astype(str))
        if not lens: reasons.append(f"G1 lens RỖNG: {lens_path} đọc được nhưng 0 mã")
    except Exception as e:
        reasons.append(f"G1 lens ĐỌC LỖI: {lens_path}: {type(e).__name__}: {e}")
    tks = [str(t) for t in lb["ticker"]]
    nodata = sorted(t for t, nt in zip(tks, lb["note"]) if "bank-nodata" in str(nt))
    bad = sorted(t for t, nt in zip(tks, lb["note"]) if any(k in str(nt) for k in NODATA_NOTES))
    n_all = len(set(tks))
    if n_all == 0:
        reasons.append("G3 rating_8l.csv không có dòng BANK nào")
    elif len(bad) / n_all > BANK_NODATA_MAX_FRAC:
        reasons.append(f"G3 tỉ lệ nodata {len(bad)}/{n_all} = {len(bad)/n_all:.1%} > ngưỡng "
                       f"{BANK_NODATA_MAX_FRAC:.0%}: {', '.join(bad)}")
    if lens:
        inc = [t for t in nodata if t in lens]
        if inc:
            _lm = os.path.join(WORKDIR, "data", "rating_8l.csv")
            _mt = lambda q: (pd.Timestamp(os.path.getmtime(q), unit="s", tz="UTC").tz_convert("Asia/Ho_Chi_Minh")
                             .strftime("%Y-%m-%d %H:%M ICT") if os.path.exists(q) else "không có file")
            reasons.append(f"G2 {len(inc)} mã gắn nhãn bank-nodata NHƯNG có trong {lens_path}: {', '.join(inc)} "
                           f"(mtime rating_8l.csv {_mt(_lm)}, bank_lens_v3.csv {_mt(lens_path)}). Nguyên nhân CHƯA "
                           f"xác định — kiểm log pt_8l_daily dòng 'bank lens load fail'")
    snap = os.environ.get("R8L_BANK_LENS_SNAPSHOT") or os.path.join(WORKDIR, "data", "bank_lens_ticker_snapshot.json")
    if os.path.exists(snap):
        try:
            with open(snap, encoding="utf-8") as f: prev = set(json.load(f)["lens_tickers"])
            lost = [t for t in bad if t in prev]
            if lost:
                reasons.append(f"G4 {len(lost)} mã có hạng lens THẬT ở snapshot kỳ trước ({snap}) nay thành bank-nodata/bank-noROE: "
                               f"{', '.join(lost)}. Nếu bỏ lens có chủ đích: sửa snapshot bằng tay rồi chạy lại")
        except Exception as e:
            reasons.append(f"G4 snapshot ĐỌC LỖI: {snap}: {type(e).__name__}: {e}")
    else:
        print(f"  [bank-gate] G4 chưa có snapshot {snap} (lần đầu) — G2 vẫn phủ ca lens đọc lỗi")
    return reasons, lens


def _write_lens_snapshot(lens):
    """Ghi snapshot tập mã lens (atomic tmp + os.replace, §5) — CHỈ gọi ở run canonical khi cổng KHÔNG bật."""
    import json
    from datetime import datetime
    from zoneinfo import ZoneInfo
    snap = os.environ.get("R8L_BANK_LENS_SNAPSHOT") or os.path.join(WORKDIR, "data", "bank_lens_ticker_snapshot.json")
    tmp = snap + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"asof": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M ICT"),
                   "source": os.path.join(WORKDIR, "data", "bank_lens_v3.csv"),
                   "lens_tickers": sorted(lens)}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, snap)


def override_current_bank_aq(out, live_run=False):
    """Override ONLY the CURRENT-snapshot bank rating with the live AQ-aware rate_bank value (NPL/coverage
    from data/bank_lens_v3.csv, via rating_8l.py -> data/rating_8l.csv) while leaving the entire historical
    proxy series untouched. Rationale (user 2026-06-16): the history publisher rates banks ROE-only because
    NPL/coverage have no deep history (avoids look-ahead); but for the MOST RECENT snapshot we DO have current
    asset quality, so the latest row per bank should reflect it (e.g. BID/SHB/HDB proxy=1 -> AQ-aware=3 when
    coverage<0.9). Only the single latest eff_date row per BANK ticker changes; all prior (backtest) rows keep
    the proxy -> no look-ahead introduced. Fail-safe: missing live file / ticker -> keep proxy.

    NO-DATA = CHỈ ĐƯỢC HẠ HẠNG (phương án B, user duyệt 2026-11-19; thay luật "loại bỏ" 2026-09-27):
    dòng live mang nhãn "bank-nodata" (mã vắng data/bank_lens_v3.csv; rating_8l.py nay trả 4) hoặc
    "bank-noROE" (lens có mã nhưng ROE trống; rating_8l.py vẫn trả 3) KHÔNG còn bị bỏ qua để giữ proxy
    nữa: dòng MỚI NHẤT của mã đó nhận max(proxy, live, BANK_NODATA_FLOOR=4) ⇒ không bao giờ tốt hơn proxy,
    không bao giờ lọt cổng ≤3 (LAG/BAL/custom30V đọc fa_ratings_8l). Chuỗi lịch sử (backtest) KHÔNG đổi.
    Proxy noROE của chính module này (rate_bank_hist/proxy trả 3 khi ROE trống) KHÔNG đổi: đo 2026-11-19
    0/1009 dòng BANK 2014-2026 dính (REPORT_B.md mục 3).
    CỔNG CHẶN (bank_nodata_gate): lens đọc lỗi/rỗng, mâu thuẫn lens↔nhãn, tỉ lệ nodata > ngưỡng, hoặc mã có
    lens kỳ trước nay nodata ⇒ run này KHÔNG hạ hạng mã nào (fail-OPEN về hành vi cũ = giữ proxy) + cảnh
    báo Trading Daily — vì hạ hàng loạt khi lens hỏng sẽ chặn mua LAG cả mã đang giữ (MBB/VPB/VIB).
    `note` absent from the CSV -> reject EVERY override rather than guess (§28).
    live_run=True (chỉ main() ở run canonical/ép BQ): gửi cảnh báo Discord + cập nhật snapshot lens."""
    try:
        live = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l.csv"))
    except Exception as e:
        _p = os.path.join(WORKDIR, "data", "rating_8l.csv")
        _why = f"rating_8l.csv ĐỌC LỖI/KHÔNG CÓ: {_p}: {type(e).__name__}: {e}"
        print(f"  [bank-AQ override] SKIPPED (live rating_8l.csv unavailable -> keep proxy): {e}")
        _bank_gate_alert("[8L bank-nodata] CỔNG CHẶN BẬT (override BỎ QUA) — fa_ratings_8l run này KHÔNG hạ "
                         "hạng mã ngân hàng thiếu lens, mã nodata giữ proxy cũ (có thể lọt cổng ≤3). Bằng chứng:\n- "
                         + _why, send=live_run, reasons=["SKIPPED " + _why])
        return out
    lb = live[live["route"] == "BANK"] if "route" in live.columns else live.iloc[0:0]
    if "note" not in lb.columns:
        _why = (f"rating_8l.csv KHÔNG có cột `note` (cột thật: {list(live.columns)}) ⇒ không phân biệt được "
                "hạng bank-nodata/bank-noROE với hạng thật")
        print(f"  [bank-AQ override] SKIPPED: {_why} -> keep proxy")
        _bank_gate_alert("[8L bank-nodata] CỔNG CHẶN BẬT (override BỎ QUA) — fa_ratings_8l run này KHÔNG hạ "
                         "hạng mã ngân hàng thiếu lens, mã nodata giữ proxy cũ (có thể lọt cổng ≤3). Bằng chứng:\n- "
                         + _why, send=live_run, reasons=["SKIPPED " + _why])
        return out
    lb = lb[lb["rating"].notna()]
    reasons, lens = bank_nodata_gate(lb)
    live_map, nodata_map = {}, {}
    for _t, _r, _nt in zip(lb["ticker"], lb["rating"], lb["note"]):
        if any(k in str(_nt) for k in NODATA_NOTES): nodata_map[_t] = (int(_r), str(_nt).strip())
        else: live_map[_t] = int(_r)
    if reasons:
        _bank_gate_alert(
            "[8L bank-nodata] CỔNG CHẶN BẬT — fa_ratings_8l run này KHÔNG hạ hạng mã ngân hàng thiếu lens "
            f"({len(nodata_map)} mã giữ proxy cũ, có thể lọt cổng ≤3). Bằng chứng:\n- " + "\n- ".join(reasons),
            send=live_run, reasons=reasons)
    r2t = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    n, moved = 0, []
    for tk in out.loc[out["route"] == "BANK", "ticker"].unique():
        sub = out.loc[(out["ticker"] == tk) & (out["route"] == "BANK")].sort_values("eff_date")
        if not len(sub): continue
        i = sub.index[-1]; cur = int(out.at[i, "rating"])
        if tk in live_map:
            new_r = live_map[tk]
        elif tk in nodata_map and not reasons:
            new_r = max(cur, nodata_map[tk][0], BANK_NODATA_FLOOR)   # downgrade-only
            if new_r != cur: moved.append(f"{tk} {cur}->{new_r}({nodata_map[tk][1]})")
        else:
            continue
        if cur != new_r:
            out.at[i, "rating"] = new_r; out.at[i, "tier"] = r2t[new_r]; n += 1
    if nodata_map:
        print(f"  [bank-AQ override] {len(nodata_map)} live row(s) no-lens: "
              + (f"GIỮ proxy (cổng chặn bật): {', '.join(sorted(nodata_map))}" if reasons else
                 f"downgrade-only max(proxy,live,{BANK_NODATA_FLOOR}); đổi {len(moved)}: {', '.join(moved) or '-'}"))
    if live_run and not reasons and lens:
        # Snapshot = tập mã có hạng THẬT: live_map (csv chấm bằng lens thật) ∪ (lens hiện tại − mã nodata/noROE).
        # (a) KHÔNG chỉ lens hiện tại: rating_8l.csv sinh 19:20 HÔM TRƯỚC còn chấm mã vừa mất khỏi lens bằng lens
        # thật; snapshot = lens hôm nay làm mất mã đó đúng lúc csv ngày sau chuyển nó sang nodata ⇒ G4 điếc.
        # (b) trừ nodata_map: mã nằm trong lens nhưng ROE NaN (noROE) dai dẳng không vào snapshot ⇒ không làm
        # G4 dính vĩnh viễn; mã từng có hạng thật rồi mới thành noROE vẫn nằm trong live_map kỳ trước ⇒ G4 bắt.
        _write_lens_snapshot(set(live_map) | (set(lens) - set(nodata_map)))
    print(f"  [bank-AQ override] current-snapshot bank rating changed for {n} bank(s); history proxy untouched")
    return out


def _is_live_run(path, canon, env):
    """Run này có quyền gửi cảnh báo thật/ghi snapshot không? True ⇔ ghi đích canonical hoặc ép BQ tường minh."""
    return env.get("R8L_HIST_BQ_REFRESH") == "1" or os.path.realpath(path) == os.path.realpath(canon)


def refresh_bq_table(csv_path):
    """Refresh tav2_bq.fa_ratings_8l (ticker,time,route,rating,tier) from the history CSV — one-command
    refresh so the live regime_size overlay reads the latest point-in-time ratings. Dedup per (ticker,eff_date)."""
    try:
        load = (f'"{BQ_BIN}" load --replace --source_format=CSV --skip_leading_rows=1 '
                f'--project_id={PROJECT} tav2_bq.tmp_r8l_refresh "{csv_path}" '
                f'ticker:STRING,eff_date:DATE,q_time:DATE,route:STRING,rating:INT64,core_score:INT64,tier:STRING')
        subprocess.run(load, shell=True, capture_output=True, text=True, timeout=300)
        sql = ("CREATE OR REPLACE TABLE tav2_bq.fa_ratings_8l AS "
               "SELECT tk AS ticker, eff_date AS time, ANY_VALUE(route) AS route, "
               "ANY_VALUE(rating) AS rating, ANY_VALUE(tier) AS tier FROM ("
               "SELECT h.ticker AS tk, h.eff_date, h.route, h.rating, h.tier, "
               "ROW_NUMBER() OVER (PARTITION BY h.ticker, h.eff_date ORDER BY h.q_time DESC) rn "
               "FROM tav2_bq.tmp_r8l_refresh AS h) WHERE rn=1 GROUP BY tk, eff_date")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write(sql); tmp = f.name
        subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                       f'--project_id={PROJECT}', shell=True, capture_output=True, text=True, timeout=300)
        os.unlink(tmp)
        subprocess.run(f'"{BQ_BIN}" rm -f -t {PROJECT}:tav2_bq.tmp_r8l_refresh', shell=True, capture_output=True, text=True)
        print("refreshed BQ table tav2_bq.fa_ratings_8l")
    except Exception as e:
        print(f"[!] BQ table refresh skipped: {e}")

def main():
    print("pulling financial history ...")
    df = bq(HIST_SQL)
    # PHAI tinh TRUOC attach_icb_pit / rate_row: ca 3 cho dung eff_date_of doc cot nay.
    df["rd_untrusted"] = release_date_untrusted(df)
    print(f"  [rd-guard] {int(df['rd_untrusted'].sum())} dong Release_Date khong dang tin -> eff_date = q_time")
    icb = bq(ICB_SQL)
    df = attach_icb_pit(df, icb)
    print(f"  {len(df)} financial rows, {df['ticker'].nunique()} tickers")

    df["route"] = [route_of(t, c) for t, c in zip(df["ticker"], df["ICB_Code"])]
    load_bank_aq()          # PIT NPL/LLR for the AQ-aware BANK route (rate_bank_hist)
    global MOAT_TIER
    try:
        _mg = pd.read_csv(os.path.join(WORKDIR,"data","moat_tags.csv"))
        MOAT_TIER = dict(zip(_mg["ticker"], _mg["moat_tier"]))
        _wide = sorted(t for t,v in MOAT_TIER.items() if v=="WIDE")
        print(f"  [moat-gov] {len(MOAT_TIER)} 5F tiers; only WIDE earns +1 from {MOAT_GOV_CUTOFF.date()}: "
              f"{_wide}; registry NARROW/NONE -> no notch (recent)")
    except Exception as e:
        print("moat_tags load fail (quant ungated):", e); MOAT_TIER = {}
    # stability() reads route off the row
    df["rating"] = df.apply(lambda r: rate_row(r), axis=1)
    df["core_score"] = df.apply(lambda r: core_score(r)[0], axis=1)

    # ---- per-group A-E mapping (user choice: per-group percentile) ----
    # COMPOUNDER: percentile-rank core_score WITHIN each quarter's cross-section (point-in-time, ~500 names
    #   -> stable) using the same thresholds as the old fa_ratings (A top10 / B 10-30 / C 30-60 / D 60-85 / E
    #   bottom15). This restores a balanced A-E with a real E-floor that the fixed 1-5 bins lost for compounders.
    # SMALL GROUPS (bank/power/cyclical/RE/sec/ins): keep the validated discrete 8L rating 1->A..5->E
    #   (per-quarter cross-section is too thin to percentile reliably).
    def pct_tier(s):
        # percentile rank in [0,1]; higher score = better = A
        r = s.rank(pct=True, method="average")
        return pd.cut(r, bins=[-0.01,0.15,0.40,0.70,0.90,1.01], labels=["E","D","C","B","A"])
    df["tier"] = df["rating"].map({1:"A",2:"B",3:"C",4:"D",5:"E"})
    comp = df["route"]=="COMPOUNDER"
    df.loc[comp, "tier"] = (
        df.loc[comp].groupby("q_time")["core_score"].transform(lambda s: pct_tier(s)).astype(str)
    )
    # CONSISTENCY: an IMPAIRED rating (5) must not show an investment-grade TIER from a still-decent
    # core_score percentile. The EQ gate downgrades rating (e.g. HAG: scorecard ok but non-core/no-cash/
    # levered -> rating 5) without touching core_score, so force rating-5 names to the bottom tier (E).
    df.loc[df["rating"]==5, "tier"] = "E"

    # effective date = Release_Date (public) ; fall back to q_time + NULL_RD_EFF_OFFSET_DAYS if missing, q_time if
    # Release_Date untrusted (eff_date_of / release_date_untrusted)
    df["eff_date"] = eff_date_of(df["Release_Date"], df["q_time"], df["rd_untrusted"])
    df = df.dropna(subset=["eff_date"])

    out = df[["ticker","eff_date","q_time","route","rating","core_score","tier"]].copy()
    out["eff_date"] = out["eff_date"].dt.strftime("%Y-%m-%d")
    _canon = os.path.join(WORKDIR, "data", "rating_8l_history.csv")
    path = os.environ.get("R8L_HIST_OUT") or _canon
    _live_run = _is_live_run(path, _canon, os.environ)
    # latest-snapshot bank rating -> live AQ (history proxy untouched); live_run: cảnh báo Discord + snapshot lens
    out = override_current_bank_aq(out, live_run=_live_run)
    # FORENSIC EXCLUDE (2026-06-20, date-aware, NO hindsight): human-flagged 'exclude' (related-party/
    # manipulation, data/forensic_flags.csv). The flagged name's latest rating row predates the flag date,
    # so we APPEND an override row stamped at the flag date (rating 5/tier E) -> as-of-forward reads return 5
    # for every fa_ratings_8l consumer (custom30, golive sizing, audits); all history before it untouched.
    try:
        _ff = pd.read_csv(os.path.join(WORKDIR,"data","forensic_flags.csv"))
        _add = []
        for _, fr in _ff.iterrows():
            if str(fr["severity"]).strip() != "exclude": continue
            tk = fr["ticker"]; fdate = str(pd.Timestamp(fr["date"]).date())
            _rt = out.loc[out["ticker"] == tk, "route"]; rte = _rt.iloc[-1] if len(_rt) else "COMPOUNDER"
            _add.append({"ticker": tk, "eff_date": fdate, "q_time": fdate, "route": rte,
                         "rating": 5, "core_score": 0, "tier": "E"})
        if _add:
            out = pd.concat([out, pd.DataFrame(_add)], ignore_index=True)
            print(f"  [forensic] appended {len(_add)} exclude override row(s) rating 5 @flag date: {[a['ticker'] for a in _add]}")
    except Exception as e:
        print("  forensic_flags load fail:", e)
    # coding_guidelines §8: an A/B or selfcheck run must never be able to target the registry-pinned
    # data/rating_8l_history.csv nor REPLACE tav2_bq.fa_ratings_8l. Both are explicit opt-outs; with no
    # env set the canonical production invocation behaves byte-for-byte as before.
    out.to_csv(path, index=False)
    print(f"wrote {path}  ({len(out)} rows)")
    # REFRESH BQ TU SUY THEO DICH ĐEN, khong con "mac dinh refresh tru khi nho bat co" (retro
    # 2026-09-27 Pattern 1, user duyet 16:52 ICT 2026-09-28). Su co goc: mot run EXP ghi ra file
    # KHAC nhung VAN REPLACE `tav2_bq.fa_ratings_8l` vi nguoi chay quen dat
    # `R8L_HIST_NO_BQ_REFRESH=1` ⇒ bang production mang so cua thi nghiem, mat ~2h khoi phuc.
    # Mot guard OPT-IN thu cong (bien moi truong nguoi phai tu nho) khong the dua vao — no chi
    # dung khi nguoi dung da y thuc duoc rui ro, tuc dung luc nao cung KHONG can guard.
    # Nay: chi refresh khi dich ghi DUNG LA canonical; moi dich khac ⇒ KHONG dung toi bang
    # production, va NOI RO vi sao. Co the ep tuong minh bang R8L_HIST_BQ_REFRESH=1 (cho ca
    # duong phuc hoi: ghi ra file tam roi chu dong day len BQ).
    _force = os.environ.get("R8L_HIST_BQ_REFRESH") == "1"
    _is_canon = os.path.realpath(path) == os.path.realpath(_canon)
    if os.environ.get("R8L_HIST_NO_BQ_REFRESH") == "1":
        print("  [bq] refresh SKIPPED (R8L_HIST_NO_BQ_REFRESH=1) -- tav2_bq.fa_ratings_8l untouched")
    elif _force:
        print(f"  [bq] refresh ÉP TƯỜNG MINH (R8L_HIST_BQ_REFRESH=1) tu {path}")
        refresh_bq_table(path)
    elif _is_canon:
        refresh_bq_table(path)
    else:
        print(f"  [bq] refresh SKIPPED -- dich ghi KHONG phai canonical"
              f" ({path} != {_canon}) ⇒ day la run THI NGHIEM/A-B, khong dung toi"
              f" tav2_bq.fa_ratings_8l. Muon day len that: R8L_HIST_BQ_REFRESH=1")
    print("\ndistribution by route x rating (raw 1-5):")
    print(pd.crosstab(out["route"], out["rating"]).to_string())
    print("\ndistribution by route x TIER (final A-E, compounder=per-qtr percentile):")
    print(pd.crosstab(out["route"], out["tier"]).to_string())

if __name__ == "__main__":
    main()
