# -*- coding: utf-8 -*-
"""
golive_recommend_v23.py  —  LAYER 2: V2.3 + DT5G daily order/position recommender.

V2.3 = V2.2 (BAL | LAG static, always-on, NO ensemble switch) + parking {3:0.7}
on BOTH books + state-conditional LAG/BAL allocator + CAPIT v2 sleeves.
This is the PRODUCTION recommender (replaces the V4 golive_recommend.py picks
in the 18:00 report as of 2026-06-12; V4 stays as a paper-trade benchmark).

Consumes the gated DT5G state (publish_gated_state.py -> BQ
tav2_bq.vnindex_5state_dt5g_live) and emits TODAY's actionable recommendations:

  • Market regime (gated state5) + ETF parking target {NEUTRAL: 70%} (both books)
  • Allocator: w_LAG target by state {CRISIS .50 / BEAR 0 / NEU·BULL·EXBULL .65},
    EDGE-CONDITIONAL in states 3/4/5 (.65 only when LAG edge-health mean12 >= 4%,
    else .50 — mirrors pinned R3 `edge` allocator, pt_v23_audit_2014.py:1738-1751);
    BAND-only rebalance trigger ±10pp vs current w_LAG (read from pt_v22 logs)
  • BAL book: ranked BA-core picks (SIGNAL_V11 + D1 + SV_TIGHT + overheat
    + AVOID_exbull + regime_size weak-half), max 12, 10%/pos of BAL book
  • LAG book (always-on): PEAD entries due next sessions (NP_R>=15 &
    prior_n_good>=4 & pa_HL3>=5), T+5 entry, hold 25td, LAG_HI 10% / LAG_LO 8%
  • CAPIT v2 monitor: oversold breadth vs 30% gate; if fired -> state-routed
    size + grind x0.5 + BEAR guard (dd52w / VN rv10-cooling) + quality-golden basket

Output:
  deploy_golive_dt5g_v4/out/golive_v23_recommendations_<DATE>.{md,csv}
  data/golive_v23_status.json            (read by the 18:00 telegram report)

Point-in-time snapshot of the SAME logic as pt_v22_dt5g.py — NOT a NAV backtest.
"""
import os, sys, io, json
from datetime import datetime, timedelta
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── FAIL-CLOSED INTERPRETER GUARD (2026-07-31, sự cố ghi đè artifact 07-30) ──
# Sự cố thật: script này bị chạy lại bằng `python3` hệ thống (3.10 / pandas 2.3) lúc 19:04 ICT
# 07-30, ghi ĐÈ artifact canonical của bản chạy đúng lúc 19:00 bằng $DNA_PYEXE (3.12 / pandas 3).
# pandas 2 KHÔNG unpickle được data/earnings_surprise_data.pkl (viết bằng pandas 3) → nhánh except
# → LAG rỗng: bản trên đĩa mất 29 dòng LAG, n_lag_upcoming=0 GIẢ. BQ giữ bản đúng, đĩa giữ bản
# hỏng — và đĩa mới là thứ người/bot đọc. Điều tra: mike/agents/Taylor/research/
# capit_state_visibility_gap_20260731.md §3; incident kb/incidents/2026-07/2026-07-31-*.md
# Cảnh báo LAG PKL WARN (bq_freshness_check.sh:426) chạy TRƯỚC pipeline và bằng $DNA_PYEXE nên
# về bản chất không bắt được lần ghi đè xảy ra SAU đó bằng interpreter khác → chặn tại nguồn.
# Đặt NGAY sau import pandas và TRƯỚC mọi thao tác ghi (os.chdir/OUTDIR/makedirs/mọi open(...,"w")):
# thoát ở đây là thoát SẠCH, không file nào trên đĩa bị đụng tới.
# Kỷ luật liên quan: kb/coding_guidelines.md §8 (interpreter pinned $DNA_PYEXE cho mọi lệnh sinh
# artifact canonical). bq_freshness_check.sh:93 dùng `PY="${DNA_PYEXE:-python3}"` — fallback python3
# im lặng khi env thiếu, đúng con đường tái diễn sự cố; guard này biến nó thành lỗi to, không im.
_PD_MAJOR = int(str(pd.__version__).split(".")[0])
if _PD_MAJOR != 3:
    sys.stderr.write(
        f"FATAL golive_recommend_v23: interpreter SAI — pandas {pd.__version__} "
        f"(cần major 3), sys.executable={sys.executable}.\n"
        f"Artifact canonical (data/golive_v23_status.json, out/golive_v23_recommendations_*.csv|md) "
        f"KHÔNG được ghi. Chạy lại bằng $DNA_PYEXE (/home/trido/thanhdt/wc_venv/bin/python).\n")
    sys.exit(2)

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

# This recommender MUST read LIVE BigQuery, never the local DuckDB cache: wc_env.sh exports
# BQ_LOCAL_CACHE globally, which silently routes simulate_holistic_nav.bq through the
# 23:45-synced cache (always T-1 at the 19:00 slot). Worse, the cache fails OPEN when its
# nightly verify fails — so the data source was flipping live/cache per day depending on the
# previous night's sync, making the plan non-deterministic (probe 2026-07-15: cache vs live
# disagreed on signal_date, breadth_oversold, and custom30V parking membership PVS/VGC).
# Reading live also makes the 17:30->19:00 reschedule (2026-07-10) actually take effect and
# lets bq_freshness_check's gate (live) and this consumer (live) finally see the same data.
# Unset here (process-local; cache consumers like papertrade/sims/backtests are unaffected).
# Same pattern as publish_gated_state.py (audit Winston_20260712_142100 C1, commit 4995262).
os.environ.pop("BQ_LOCAL_CACHE", None)

from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11
from anomaly_gate import anomaly_excluded as _anomaly_excluded_shared
from anomaly_gate import anomaly_flags_freshness as _anomaly_flags_freshness
from lag_liquidity_filter import lag_filter_illiquid, bal_filter_thin, ADV_MIN_VND
from lag_rating_filter import lag_filter_low_rating
from lag_forensic_filter import lag_filter_forensic_banned

OUTDIR = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out"); os.makedirs(OUTDIR, exist_ok=True)
DT_TABLE = "vnindex_5state_dt5g_live"
END = datetime.now().strftime("%Y-%m-%d")
START = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")    # recent window for "today"
START_BR = (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d") # breadth window (grind lookback 90 sessions)
START_VNI = (datetime.now() - timedelta(days=420)).strftime("%Y-%m-%d")# dd52w/rv10 window

MAX_POS = 12; POS_PCT = 0.10; WEAK_PCT = 0.05
TIER_BAL = ["MEGA","MOMENTUM","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]  # MOM_N/MOM_S closed 2026-07-12 (CP1+CP-DVR1 NO-GO, user-approved Scope A — plan_close_mom_20260712.md)
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
             "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
EXB_MOM = {"MEGA","MOMENTUM","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","S_PRO"}
PRIORITY = {t: i for i, t in enumerate(TIER_BAL)}
ETF_PARK = {3: 0.8}                                  # F1, user-confirmed 2026-08-04 via Mike
                                                      # (was 0.7; see data/trading_rules.json
                                                      # neutral_parking.default_park_of_idle_pct
                                                      # + evidence_current_F1_2026-08-04)
STATE_LAG_WEIGHT = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}
EDGE_THR = 4.0   # %: LAG trailing-12M edge-health threshold (pinned R3 = argv "edge")

# ── UNIVERSE SOURCE — P3 cutover 2026-07-22 (§4.2/§4.3/§4.3b ticker_prune_replacement_plan.md) ──
# Scope of THIS constant = the D1 RE_BACKLOG sector-lens panel ONLY (ICB_Code=8633, real estate).
# The CAPIT reads (ADV cap, breadth, pool) have their OWN switch — see "CAPIT UNIVERSE" (P4) below;
# they are deliberately NOT coupled to this one, so either can roll back without the other.
# "pit"   = `tav2_mike.universe_pit_q`, membership PER DAY. This also FIXES a live look-ahead bug:
#           the old `IN (SELECT DISTINCT ticker FROM ticker_prune)` predicate has no time condition,
#           so it admitted a name to every historical panel date — VHM (listed 2018) was sitting in
#           the 2014 panel today (§4.3b). Diff is NOT zero and is not meant to be: ±10-17 names per
#           date (~20% of the panel), the removals being exactly the un-listed-yet names.
# "prune" = legacy DISTINCT-ever predicate. Kept as the ONE-WORD ROLLBACK.
# Module-level constant on purpose, NOT an env var (env inherited through a process is the very
# mechanism behind incident C1 07-12 — coding_guidelines §11).
UNIVERSE_SOURCE = "pit"
UNIVERSE_PIT_TABLE = "lithe-record-440915-m9.tav2_mike.universe_pit_q"


def universe_pred(alias="t"):
    """SQL predicate restricting `alias` (a tav2_bq.ticker / ticker_1m row) to the universe.

    Fail-safe (§4.3): there is deliberately NO branch that silently falls back to `ticker_prune` —
    a silent fallback would re-import the very drift this migration exists to escape."""
    if UNIVERSE_SOURCE == "prune":
        return f"{alias}.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)"
    if UNIVERSE_SOURCE != "pit":
        raise ValueError(f"UNIVERSE_SOURCE={UNIVERSE_SOURCE!r} unknown (pit|prune)")
    return (f"EXISTS(SELECT 1 FROM `{UNIVERSE_PIT_TABLE}` u2 "
            f"WHERE u2.ticker={alias}.ticker AND u2.time={alias}.time AND u2.in_universe)")


def assert_universe_covers(start_date, end_date, icb=8633):
    """Fail-safe (§4.3): STOP WITH AN ERROR if `universe_pit` misses any session on which the D1
    panel actually HAS rows. Without this a missing day silently looks like "no name was in the
    universe that day" — a quietly empty panel instead of a loud failure.

    Scoped to the panel's own rows (ICB=`icb`, `ticker` UNION `ticker_1m`) rather than to every
    session in `tav2_bq.ticker`, and that scoping is deliberate, not laxity: upstream regularly
    leaves a 1-row stub for the current date (e.g. 2026-07-22 had exactly one row, DRL) which
    `build_universe_pit.py`'s B8 integrity gate correctly REFUSES to build a universe day from.
    Erroring on such a stub would take the live recommender down for a day that contributes
    nothing. If the stub ever does contain an ICB-8633 name, this still fails loudly."""
    if UNIVERSE_SOURCE != "pit":
        return
    df = bq(f"""WITH src AS (
  SELECT DISTINCT t.time FROM tav2_bq.ticker AS t
    WHERE t.ICB_Code={icb} AND t.time BETWEEN DATE '{start_date}' AND DATE '{end_date}'
  UNION DISTINCT
  SELECT DISTINCT t.time FROM tav2_bq.ticker_1m AS t
    WHERE t.ICB_Code={icb} AND t.time BETWEEN DATE '{start_date}' AND DATE '{end_date}')
SELECT (SELECT COUNT(*) FROM src) AS n_src,
       (SELECT COUNT(*) FROM src WHERE src.time NOT IN (
          SELECT u.time FROM `{UNIVERSE_PIT_TABLE}` AS u
            WHERE u.time BETWEEN DATE '{start_date}' AND DATE '{end_date}'
            GROUP BY u.time)) AS n_missing,
       (SELECT MAX(u.time) FROM `{UNIVERSE_PIT_TABLE}` AS u) AS uni_max""")
    n_src, n_missing = int(df["n_src"].iloc[0]), int(df["n_missing"].iloc[0])
    if n_missing:
        raise RuntimeError(
            f"universe_pit thieu {n_missing}/{n_src} phien co du lieu panel ICB-{icb} trong "
            f"[{start_date},{end_date}] (universe_pit max={df['uni_max'].iloc[0]}). DUNG — khong tu "
            f"fallback ve ticker_prune (§4.3). Chay mike/bin/build_universe_pit.py "
            f"(+ build_universe_pit_quality.py) cho khoang thieu.")


# ── CAPIT UNIVERSE — P4 cutover 2026-07-22 (§4.4-C-conserv ticker_prune_replacement_plan.md) ──
# Scope = CAPIT chỉ: breadth (trigger), pool (chọn rổ), ADV cap. Switch RIÊNG với UNIVERSE_SOURCE
# ở trên, vì đây là đường CHẠM TIỀN THẬT và phải rollback được độc lập bằng đúng 1 dòng.
#
# TẠI SAO KHÔNG PHẢI "đổi mẫu số, giữ nguyên ngưỡng":
#   `WASHOUT_GATE=0,30` được hiệu chuẩn trên mẫu số `ticker_prune`. Đổi mẫu số mà giữ ngưỡng =
#   âm thầm đổi cả xác suất kích hoạt LẪN size của một lệnh mua thật. Đo trên 3.129 phiên
#   (§4.4-KQ): KHÔNG TỒN TẠI ngưỡng nào bảo toàn đúng tập 82 ngày fire cũ trên mẫu số mới —
#   max(non-fire)=0,3067 > min(fire)=0,2425, hai tập không tách được tuyến tính.
#
# THIẾT KẾ ĐÃ CHỌN (user chốt 2026-07-22 sau 2 vòng escalate) = C-conserv:
#   breadth = tỷ lệ `D_RSI<0,3` trên rổ TOP-250 THANH KHOẢN NHẤT của `universe_pit_q`
#   (rank mỗi ngày theo `Volume_3M_P50 × COALESCE(Price, Close)`), gate 0,31.
#   Lý do chọn top-N thay vì "cả universe": mẫu số universe đã swing 128 → 589 → 365 mã trong
#   2014-2026; một tỷ lệ trên mẫu số co giãn thì thang đo trôi theo. Top-N cố định thì không.
#   Gate 0,31 = TRUNG ĐIỂM khoảng tách (0,3080 ; 0,3120) — quy ước, KHÔNG dò lưới (chống tune:
#   đây là tham số điều khiển tiền thật; N-trial đã khai báo TRƯỚC = 5 giá trị N).
#
# GIÁ PHẢI TRẢ, ĐÃ ĐO VÀ ĐÃ CHẤP NHẬN (đừng phát hiện lại rồi tưởng là bug):
#   - MẤT 7 ngày fire lịch sử, THÊM 0 (toàn bộ lệch theo hướng THẬN TRỌNG, không có fire giả):
#     2015-05-18, 2018-07-05, 2020-02-04, 2020-03-11, 2020-03-25, 2020-04-01, 2022-06-15.
#     Mất HẲN 2 episode 1-ngày: 2015-05-18 và 2018-07-05 (2018-07-05 fire cũ do ĐUÔI ILLIQUID
#     của `ticker_prune` oversold, phần lõi thanh khoản thì không — đúng thứ ta muốn bỏ).
#   - 1 cặp lật `capit_grind` True→False: 2015-08-24/25 ⇒ size 0,375 → 0,75 (GẤP ĐÔI) trên một
#     lần fire thật. Đây là thay đổi nặng nhất về tiền của cả P4.
#   - Ngày LIVE cutover (2026-07-22): fired/grind/size giống hệt nhánh cũ ⇒ 0 tác động lên đợt
#     giải ngân CAPIT đang dở (đo bằng universe_pit_p4_selfcheck.py, không giả định). Pool + ADV
#     cap thì KHÔNG cutover hôm nay — xem khối ngay dưới, đó mới là chỗ có tác động thật.
#   - N=250 chỉ thực sự là "top-N" từ 2014-10-17; trước đó universe < 250 nên br250 ≡ breadth
#     toàn universe. Hành vi đúng của rule, không phải lỗi.
CAPIT_BREADTH_SOURCE = "pit"        # "pit" | "prune"  ← ROLLBACK ĐÚNG 1 DÒNG
CAPIT_TOPN = 250            # chỉ dùng khi CAPIT_BREADTH_SOURCE="pit"
# Ngưỡng ĐI KÈM mẫu số, không tách rời: đặt cạnh nhau để không ai đổi cái này mà quên cái kia.
WASHOUT_GATE = 0.31 if CAPIT_BREADTH_SOURCE == "pit" else 0.30

# ── POOL + ADV: VẪN GHIM `ticker_prune` CÓ CHỦ Ý (2026-07-22) — KHÔNG phải quên ────────────
# Switch RIÊNG với breadth ở trên vì hai thứ này hỏng theo hai kiểu khác nhau: breadth sai thì
# sai NGÀY kích hoạt, pool sai thì sai TÊN MÃ được mua. Cutover trigger đã đo là 0 tác động
# ngày LIVE; cutover pool thì KHÔNG:
#   Đo ngày 2026-07-22 (universe_pit_p4_selfcheck.py T6c/T6d, trong lúc `capit_signal_today=true` và
#   đợt giải ngân CAPIT đang DỞ): pool "pit" thêm **HVT** (pbz −1,362 ⇒ đứng HẠNG 3) ⇒ rổ đổi
#   từ 4 mã [PVT, SAB, SIP, VNM] thành 5 mã [HVT, PVT, SAB, SIP, VNM] — vừa thêm một lệnh mua
#   thật, vừa pha loãng equal-weight 25% → 20% cho 4 mã đang khớp dở.
#   HVT là ca đáng chú ý, KHÔNG phải nhiễu: chất lượng thật (ROE_Min5Y 16,1% · ROIC5Y 24,0% ·
#   FSCORE 7) nhưng THANH KHOẢN THẬT chỉ 0,196 tỷ/phiên; nó lọt sàn "2 tỷ" chỉ vì sàn đó đo
#   turnover MỘT NGÀY (hôm nay 2,063 tỷ — sát mép) chứ không đo ADV. `ticker_prune` vô tình che
#   lỗ hổng này bao lâu nay; bỏ prune ra là lộ. Sửa sàn thanh khoản của pool (ADV thay vì
#   turnover-1-ngày) là ĐỔI CHIẾN LƯỢC — cần R&D + backtest riêng, KHÔNG làm lẫn vào migration.
# ⇒ Ghim tại đây tới khi (a) `capit_signal_today` về false, VÀ (b) user duyệt riêng khoản sàn thanh
#   khoản pool. Cổng "không cutover P4 khi capit_signal_today=true" (§4.4 mục 4, user duyệt Q5) đang
#   CHẶN đúng chỗ nó sinh ra để chặn.
CAPIT_POOL_SOURCE = "prune"         # "pit" | "prune"  ← cutover 1 dòng khi 2 điều kiện trên đủ


def capit_breadth_sql(start, end):
    """Chuỗi breadth oversold — nguồn của trigger `capit_signal_today` VÀ của `capit_grind` (size)."""
    if CAPIT_BREADTH_SOURCE == "prune":
        return f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{start}' AND DATE '{end}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time"""
    if CAPIT_BREADTH_SOURCE != "pit":
        raise ValueError(f"CAPIT_BREADTH_SOURCE={CAPIT_BREADTH_SOURCE!r} unknown (pit|prune)")
    # tie-break `, ticker` là CỐ Ý: hai mã cùng `liq` mà đổi thứ tự giữa 2 lần chạy sẽ làm ranh
    # giới rn=250 nhấp nháy ⇒ breadth không tái lập được. Giữ nguyên đúng bản đã đo (§4.4-C).
    return f"""WITH base AS (
  SELECT t.time, t.ticker, t.D_RSI, t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq
  FROM tav2_bq.ticker t
  JOIN `{UNIVERSE_PIT_TABLE}` u ON u.ticker = t.ticker AND u.time = t.time AND u.in_universe
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}' AND t.Close_T1 > 0),
r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY time ORDER BY liq DESC, ticker) rn FROM base)
SELECT time, AVG(CASE WHEN D_RSI < 0.3 THEN 1.0 ELSE 0 END) oversold
FROM r WHERE rn <= {CAPIT_TOPN} GROUP BY time ORDER BY time"""


def capit_pool_sql(bd):
    """Pool ứng viên rổ CAPIT tại ngày washout `bd` (golden floor + sàn thanh khoản 2 tỷ)."""
    if CAPIT_POOL_SOURCE == "prune":
        return f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{bd}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2"""
    if CAPIT_POOL_SOURCE != "pit":
        raise ValueError(f"CAPIT_POOL_SOURCE={CAPIT_POOL_SOURCE!r} unknown (pit|prune)")
    return f"""SELECT t.ticker, SAFE_DIVIDE(t.PB-t.PB_MA5Y,t.PB_SD5Y) pbz
FROM tav2_bq.ticker t
JOIN `{UNIVERSE_PIT_TABLE}` u ON u.ticker = t.ticker AND u.time = t.time AND u.in_universe
WHERE t.time = DATE '{bd}' AND t.ROE_Min5Y>=0.12 AND t.ROIC5Y>=0.10 AND t.FSCORE>=6
  AND COALESCE(t.Price,t.Close)*t.Volume/1e9 >= 2"""


def capit_breadth_is_stale(br_max, end):
    """FAIL-CLOSED riêng cho CAPIT khi `universe_pit` chậm hơn dữ liệu giá. Trả (stale, src_max).

    Vì sao cần: `universe_pit` do một job RIÊNG build (`mike/bin/build_universe_pit.py`). Nếu job
    đó chưa chạy cho phiên mới nhất, câu breadth vẫn trả kết quả — chỉ thiếu ngày cuối — và
    `br["oversold"].iloc[-1]` lặng lẽ thành breadth của HÔM QUA. Đúng mẫu sự cố C1 07-12 (đọc
    vintage T-1 mà tưởng T), nhưng lần này nó điều khiển một lệnh mua thật.

    KHÔNG raise (sẽ hạ cả recommender, BAL/LAG vô can) mà fail-CLOSED riêng CAPIT: không fire
    lệnh mới trên dữ liệu cũ, và nói to trong status JSON + MD."""
    if CAPIT_BREADTH_SOURCE != "pit":
        return False, None
    try:
        m = bq(f"SELECT MAX(t.time) AS m FROM tav2_bq.ticker AS t "
               f"WHERE t.time <= DATE '{end}' AND t.Close_T1 > 0")
        src_max = pd.Timestamp(m["m"].iloc[0])
    except Exception as ex:
        print(f"  WARNING: không kiểm được độ tươi breadth ({ex}) — CAPIT fail-closed")
        return True, None
    if pd.isna(src_max):
        return True, None
    return bool(pd.isna(br_max) or pd.Timestamp(br_max) < src_max), str(src_max.date())


def w_lag_target(state, asof):
    """Edge-conditional w_LAG target — mirror of pt_v23_audit_2014.py:1738-1751 (pinned R3
    allocator, argv `v23a none postbull 0 edge`): in good states (3/4/5) tilt to 0.65 ONLY
    when LAG's own causal edge-health mean12 (trailing-12M mean LAG trade post-return, from
    data/lag_edge_health.csv, ffill as-of the signal date) >= EDGE_THR%; else hold 0.50.
    BEAR=0 / CRISIS=0.50 unchanged. Verified 0/3107 days mismatch vs the pinned R3 CSV
    w_lag_tgt column (2014 -> 2026-06-19). CSV unreadable -> fail-safe 0.50 (gate-fail branch)."""
    if int(state) in (3, 4, 5):
        try:
            eh = pd.read_csv(os.path.join(WORKDIR, "data", "lag_edge_health.csv"), parse_dates=["entry"])
            eh = eh.drop_duplicates("entry").set_index("entry").sort_index()["mean12"]
            m = eh.asof(pd.Timestamp(asof))
            gate_ok = bool(pd.notna(m) and m >= EDGE_THR)
            print(f"  [edge-alloc] mean12 as-of {pd.Timestamp(asof).date()} = "
                  f"{(f'{m:.1f}%' if pd.notna(m) else 'n/a')} vs thr {EDGE_THR:.0f}% -> w_LAG {'0.65' if gate_ok else '0.50'}")
            return 0.65 if gate_ok else 0.50
        except Exception as e:
            print(f"  WARNING: lag_edge_health.csv unavailable ({e}) -> fail-safe w_LAG=0.50")
            return 0.50
    return STATE_LAG_WEIGHT.get(int(state), 0.5)

ALLOC_BAND = 0.10
LAG_TW = {"LAG_HI": 0.10, "LAG_LO": 0.08}
CAPIT_HOLD = 60   # WASHOUT_GATE: xem khối "CAPIT UNIVERSE" bên dưới (gate ĐI KÈM mẫu số, P4)
ADV_X, ADV_D = 0.10, 2.0   # trần %ADV/tên cho CAPIT — xem capit_adv_caps() (quy ước, KHÔNG backtest)
ACTIVE_NAV_MAX_AGE_D = 5   # active_nav_<label>.json ghi ad-hoc (không cron) — quá hạn thì lùi nav_history
ANOMALY_TTL_DAYS = 30   # cờ due-diligence còn hiệu lực bao lâu kể từ phiên alert cuối
SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

def anomaly_excluded(asof):
    """Due-diligence gate cho rổ CAPIT: set ticker có cờ bất thường còn hiệu lực tại `asof`.

    CAPIT chọn rổ thuần CƠ HỌC (ROE/ROIC/FSCORE + PB z-score cực âm) nên nó KHÔNG biết
    một cú sập giá là "rẻ đi" hay là khủng hoảng doanh nghiệp đang diễn ra — đúng cú sập
    khủng hoảng lại làm pbz âm nhất, tức là đưa mã đó lên ĐẦU danh sách mua (case PNJ
    07/2026: lãnh đạo bị bắt, giá -32% từ đỉnh). Cờ do anomaly_scan.py ghi
    (data/anomaly_flags.json, hiệu lực ANOMALY_TTL_DAYS ngày kể từ phiên alert cuối).

    FAIL-SAFE: file thiếu/hỏng → trả set rỗng + log warning, KHÔNG chặn pipeline —
    một file thiếu không được phép làm treo cả đường lập plan tiền thật.

    Delegates to anomaly_gate.py — nguồn dùng chung với các paper-trading book
    (pt_capitulation_shadow.py, pt_v22_dt5g.py, dc_book_waterfall_paper.py). Đổi
    2026-07-21 (job Taylor_20260721_092529 + Mike áp patch) từ bản inline sang import;
    hành vi giữ nguyên 100% (zero-diff verify 60 phiên, xem anomaly_gate_prod_parity_selfcheck.py).
    """
    return _anomaly_excluded_shared(asof, ttl_days=ANOMALY_TTL_DAYS)


def capit_adv_caps(basket, asof):
    """Trần VND TUYỆT ĐỐI cho mỗi tên trong rổ CAPIT — chống market-impact khi sleeve lớn.

        cap_vnd_i = ADV_X * ADV20_i * ADV_D

    ADV20_i = median giá trị giao dịch (VND) của 20 phiên NGAY TRƯỚC `asof` (ngày washout
    KHÔNG tính vào). Ngày washout theo định nghĩa là ngày volume spike, lấy nó làm mốc sẽ
    thổi phồng thanh khoản khả dụng (đo được: median ADV20-sau / ADV-ngày-vào = 0,54;
    p10 = 0,32 — mike/agents/Taylor/exp_capitexit/RESULT.md §3a). Cửa sổ TRƯỚC cũng là cửa
    sổ duy nhất NHÂN QUẢ (live không biết ADV tương lai).

    NGUỒN GIÁ/KL (P4, 2026-07-22): đi THEO `CAPIT_POOL_SOURCE`, không theo breadth — ADV đo trên
    đúng những cái TÊN mà pool đã chọn, nên hai thứ phải cùng một nguồn hoặc cap có thể rơi vào
    tên mà nguồn kia không có dòng. Hôm nay pool còn ghim "prune" ⇒ ADV cũng đọc `ticker_prune`
    = y hệt hành vi trước P4 (đã đo: cap rổ LIVE 07-22 không đổi 1 đồng).
    Khi pool cutover sang "pit", ADV chuyển sang `tav2_bq.ticker` — CỐ Ý không join `universe_pit`
    ở đây: ADV là SỰ KIỆN THỊ TRƯỜNG THÔ (giá × khối lượng), không phải phán quyết universe; join
    lần nữa chỉ thêm một đường làm MẤT cap, mà mất cap là mất tiền theo hướng xấu
    (cap_capit_orders() fail-closed ⇒ thiếu ADV = CHẶN MUA). Đọc siêu tập `ticker` an toàn hơn.

    ADV_X=10% / ADV_D=2 là QUY ƯỚC NGÀNH, KHÔNG phải tham số đã backtest — không có dữ liệu
    market-impact thật để hiệu chỉnh. Đừng trích dẫn như đã kiểm chứng thực nghiệm, và đừng
    chỉnh chúng để khớp một kỳ vọng biết trước (phương án C job Taylor_20260720_170223 đã
    bị bác chính vì lý do này).

    Trả cap dạng VND TUYỆT ĐỐI (không phải %) — có chủ đích: script này advisory, chạy MỘT
    lần/ngày và phục vụ MỌI account (SpaceX có margin, ZaloPay cash-only, NAV khác nhau).
    Một trần theo % NAV tính từ NAV của một account sẽ SAI cho account còn lại; X·ADV20·D
    độc lập account nên đúng cho mọi account theo cấu tạo. Enforce cứng ở bot_execute.py
    (trading_bot/plan.py::cap_capit_orders) — xem ghi chú kiến trúc ở đó.

    ⚠️ Đây là trần TỔNG của cả FLEET cho một mã, KHÔNG phải trần của một account. Thanh
    khoản của một mã là nguồn lực THỊ TRƯỜNG dùng chung: N account cùng mua một mã trong
    cùng một ngày thì tác động giá cộng dồn. Trần này phải được CHIA cho các account đang
    deploy CAPIT — xem capit_account_shares(); caller ghi ra `capit_adv_caps` đã chia
    theo account, executor mỗi account chỉ thấy phần của mình.

    Tác động lịch sử ĐO ĐƯỢC (selfcheck_capit_adv_cap.py, 14 event washout 2014→2026 ở mức
    sleeve tham chiếu 0,38 tỷ): cap kích hoạt ở ĐÚNG 1/14 event — NNC ngày 2016-01-18,
    ADV20_pre 0,335 tỷ → cap 0,067 tỷ/tên trong khi equal-weight đòi 0,076 tỷ, lệch ~9
    triệu VND ở 1 vị thế. KHÔNG phải "dormant 0/14" như ước tính ban đầu (ước tính đó dùng
    ADV20 SAU khi vào — biến thể không nhân quả). 13/14 event còn lại: không kích hoạt.

    FAIL-SAFE: query lỗi → trả {} + WARNING. Rỗng KHÔNG có nghĩa "không giới hạn":
    cap_capit_orders() fail-closed (chặn lệnh CAPIT khi thiếu cap), nên mất dữ liệu ADV
    dẫn tới KHÔNG mua, chứ không phải mua không giới hạn.
    """
    if not basket:
        return {}
    try:
        tl = ",".join(f"'{t}'" for t in basket)
        a = bq(f"""WITH px AS (
  SELECT p.ticker, p.time, COALESCE(p.Price,p.Close)*p.Volume AS turn,
         ROW_NUMBER() OVER (PARTITION BY p.ticker ORDER BY p.time DESC) rn
  FROM tav2_bq.{'ticker_prune' if CAPIT_POOL_SOURCE == 'prune' else 'ticker'} p
  WHERE p.ticker IN ({tl}) AND p.time < DATE '{pd.Timestamp(asof).date()}'
    AND p.time >= DATE_SUB(DATE '{pd.Timestamp(asof).date()}', INTERVAL 90 DAY))
SELECT ticker, APPROX_QUANTILES(turn, 2)[OFFSET(1)] AS adv20
FROM px WHERE rn <= 20 GROUP BY ticker""")
        caps = {r.ticker: float(ADV_X * r.adv20 * ADV_D)
                for r in a.itertuples() if pd.notna(r.adv20) and r.adv20 > 0}
        missing = sorted(set(basket) - set(caps))
        if missing:
            print(f"  WARNING: thiếu ADV20 cho {missing} — bot_execute sẽ CHẶN các mã này "
                  f"(fail-closed), không mua không giới hạn")
        return caps
    except Exception as ex:
        print(f"  WARNING: không tính được cap %ADV ({ex}) — CAPIT sẽ bị chặn ở executor")
        return {}


def _account_nav_basis(label):
    """Cơ sở NAV để chia trần %ADV cho một account. Trả (VND, nguồn) hoặc (None, lý do).

    Ưu tiên `active_nav` (data/execution_logs/active_nav_<label>.json) — ĐÚNG cơ sở, vì nó
    đã trừ excluded_tickers (vị thế legacy ngoài rebalancing, vd DGC chiếm ~47% NAV
    ZaloPay) và đây cũng chính là con số DollarBill dùng để sizing. Dùng tổng NAV thay thế
    sẽ cho ZaloPay ~50% phần chia trong khi vốn thực sự triển khai được chỉ ~34% — account
    lớn hơn bị cắt trần oan.

    Freshness kiểm theo NỘI DUNG (`computed_at` trong chính file), KHÔNG theo mtime — mtime
    tươi/nội dung cũ là bẫy đã gặp thật (sự cố lag_edge_health 2026-07-12). File này ghi
    ad-hoc (không có cron), nên hết hạn là chuyện bình thường, không phải lỗi.

    Fallback: nav_history_<label>.csv (do daily_nav_snapshot.py ghi mỗi phiên, có cột
    `date` nên cũng dated theo nội dung) — TỔNG NAV, chưa trừ excluded_tickers.
    """
    p = os.path.join(WORKDIR, "data", "execution_logs", f"active_nav_{label}.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
        age = (pd.Timestamp.now().normalize() - pd.Timestamp(d["computed_at"])).days
        if 0 <= age <= ACTIVE_NAV_MAX_AGE_D and float(d["active_nav"]) > 0:
            return float(d["active_nav"]), f"active_nav @{d['computed_at']}"
    except Exception:
        pass
    p = os.path.join(WORKDIR, "data", "execution_logs", f"nav_history_{label}.csv")
    try:
        r = pd.read_csv(p).iloc[-1]
        if float(r["nav"]) > 0:
            return float(r["nav"]), f"nav_history @{r['date']} (TỔNG NAV, chưa trừ excluded)"
    except Exception:
        pass
    return None, "không có active_nav/nav_history dùng được"


def capit_account_shares():
    """Phần chia trần %ADV cho từng account đang deploy CAPIT. Trả (shares, mode, chi tiết).

    Danh sách account đọc ĐỘNG qua config.live_dnse_labels() (enabled ∧ mode=live ∧
    broker=dnse) — cùng nguồn mà mọi cron dùng-chung đã dùng. Thêm account thứ 3/4 vào
    trading_bot_accounts.json là tự áp dụng, KHÔNG sửa code ở đây.

    PRO-RATA theo NAV (chọn) vs CHIA ĐỀU (bác):
      · pro-rata cho mỗi account phần trần tỉ lệ với vốn thực sự triển khai được, nên trần
        bind ở cùng một MỨC TƯƠNG ĐỐI với mọi account — nhất quán với sizing hiện tại (mọi
        book đều size theo NAV account). Chia đều thì account nhỏ nhận phần trần lớn hơn
        khả năng dùng (trần không bao giờ bind, phần dư chết) trong khi account lớn bị cắt
        oan — cùng một cỡ lệnh lại bị đối xử khác nhau chỉ vì đứng cạnh một account nhỏ.
      · chia đều chỉ hơn ở chỗ không cần dữ liệu NAV → giữ đúng vai trò FALLBACK bên dưới.
    N=1: cả hai công thức đều ra share=1.0 → về đúng công thức gốc, không có case đặc biệt.

    BẤT BIẾN (điều kiện an toàn thật sự):
        Σ_account share ≤ 1.0  ⇒  Σ_account cap ≤ X·ADV20·D
    Đúng "=" ở nhánh pro-rata và nhánh fallback chia đều; nhánh KHÔNG có account live nào
    trả {} (Σ=0) — không biết chia cho ai thì không phát trần cho ai, executor fail-closed
    chặn sạch. Chiều duy nhất bị cấm là NỚI: thiếu dữ liệu KHÔNG BAO GIỜ được phép làm tổng
    trần vượt X·ADV20·D — nên fallback là chia đều, không phải "cho mỗi account full trần"
    (chính là bug mà thay đổi này sửa).
    """
    from trading_bot.config import live_dnse_labels
    labels = sorted(live_dnse_labels())
    if not labels:
        print("  WARNING: không có account live nào — CAPIT sẽ bị chặn ở executor")
        return {}, "no-account", {}
    detail = {l: dict(zip(("nav", "source"), _account_nav_basis(l))) for l in labels}
    navs = {l: d["nav"] for l, d in detail.items() if d["nav"]}
    if len(navs) == len(labels):
        tot = sum(navs.values())
        return {l: navs[l] / tot for l in labels}, "pro-rata-nav", detail
    missing = sorted(set(labels) - set(navs))
    print(f"  WARNING: thiếu NAV cho {missing} → chia ĐỀU trần %ADV cho {len(labels)} "
          f"account (tổng trần KHÔNG đổi, chỉ kém tối ưu về phân bổ)")
    return {l: 1.0 / len(labels) for l in labels}, "equal-split-fallback", detail


# ── ĐÒN BẨY MARGIN CHO RIÊNG SLEEVE CAPIT (chính sách, MẶC ĐỊNH TẮT) ────────────────────
# Chuỗi nghiên cứu p1–p5 ngày 2026-08-03 (p5 tầng engine, quant-skeptic CONFIRMED-medium):
# vay margin CHỈ trên rổ CAPIT, hệ số CỐ ĐỊNH f, cổng `dd52<=−20%` — trục DUY NHẤT còn đứng
# vững sau cả 5 phần (p1 §4.1 bác cổng valuation; p3 chưa đủ bằng chứng cho cổng NEUTRAL-only).
# Ở ĐÂY chỉ ĐỌC chính sách + CÔNG BỐ tín hiệu ra artifact; việc gắn cờ vào từng lệnh nằm
# ĐÚNG MỘT CHỖ là trading_bot/plan.py::apply_capit_lever() (coding_guidelines §7).
# FAIL-CLOSED: thiếu file/sai schema/không đọc được → coi như TẮT, không bao giờ đoán "chắc bật".
#
# PHẠM VI USER DUYỆT — ghim trong code có version-control, KHÔNG chỉ trong JSON.
# `data/trading_rules.json` khớp `.gitignore` (`*.json`) nên không có diff/blame/backup nào
# canh nó: sửa `f` hay thêm account vào đó là thay đổi tiền thật mà không để lại dấu vết.
# JSON giữ quyền BẬT/TẮT (đó là công tắc vận hành); nới PHẠM VI thì phải sửa 3 hằng dưới
# đây và đi qua review, như mọi tham số quyết định khác.
#
# IMPORT, không khai lại: nguồn chuẩn tắc là `trading_bot/plan.py` — TẦNG THỰC THI, nơi ép
# envelope lần cuối trước khi lệnh đi ra broker (arch-reviewer 2026-08-03 F2). Hai bản sao
# rời nhau sẽ trôi khỏi nhau, và bản ở tầng thực thi mới là bản giữ tiền.
from trading_bot.plan import (CAPIT_LEVER_APPROVED_F, CAPIT_LEVER_APPROVED_PACKAGE,
                              CAPIT_LEVER_APPROVED_ACCOUNTS)


def capit_lever_policy():
    """Đọc `data/trading_rules.json` → (policy dict, error str|None). Không raise."""
    path = os.path.join(WORKDIR, "data", "trading_rules.json")
    try:
        with open(path, encoding="utf-8") as f:
            blk = (json.load(f) or {}).get("capit_margin_lever") or {}
        if not blk:
            return {}, "trading_rules.json không có khối capit_margin_lever"
        raw_enabled = blk.get("enabled")
        pol = {
            # `is True`, KHÔNG `bool(...)`. Đây là công tắc DUY NHẤT giữa "tắt" và tiền vay
            # thật, mà nó nằm trong một file JSON sửa tay/LLM sửa. `bool("false")` là True
            # — nghĩa là một lỗi gõ tầm thường (`"enabled": "false"` có nháy) sẽ BẬT đòn bẩy.
            # Mọi tham số khác trong khối đã được validate chặt; công tắc chính không được
            # phép là cái duy nhất fail-OPEN. Chỉ đúng literal JSON `true` mới tính là bật.
            "enabled": raw_enabled is True,
            "f": float(blk.get("f") or 0),
            "loan_package_id": blk.get("loan_package_id"),
            "gate": blk.get("gate"),
            "scope": blk.get("scope"),
            "accounts": sorted(blk.get("accounts") or []),
        }
        if raw_enabled is not None and not isinstance(raw_enabled, bool):
            return pol, (f"capit_margin_lever.enabled = {raw_enabled!r} KHÔNG phải boolean "
                         f"JSON (true/false) — coi như TẮT, sửa file cho đúng kiểu")
        # Sanity: mọi tham số quyết định phải hợp lệ, nếu không thì TẮT (không "chạy tạm").
        if pol["f"] < 1.0 or pol["loan_package_id"] is None or pol["scope"] != "capit_only" \
                or not pol["accounts"]:
            return pol, (f"tham số capit_margin_lever không hợp lệ (f={pol['f']}, "
                         f"lp={pol['loan_package_id']}, scope={pol['scope']}, "
                         f"accounts={pol['accounts']}) — coi như TẮT")
        # PHẠM VI ĐÃ DUYỆT ghim trong CODE (được version-control), không chỉ trong JSON.
        # `data/trading_rules.json` bị .gitignore ⇒ không diff, không blame, không backup:
        # một lần sửa f=5.0 hay thêm ZaloPay vào `accounts` sẽ không để lại dấu vết nào.
        # Ba hằng dưới là bản duyệt của user ngày 2026-08-03; JSON được phép TẮT hoặc BẬT,
        # nhưng KHÔNG được phép tự nới rộng phạm vi. Muốn đổi thật thì phải sửa code +
        # qua review, đúng như mọi tham số quyết định khác.
        if (pol["f"] != CAPIT_LEVER_APPROVED_F
                or pol["loan_package_id"] != CAPIT_LEVER_APPROVED_PACKAGE
                or pol["accounts"] != CAPIT_LEVER_APPROVED_ACCOUNTS):
            return pol, (f"capit_margin_lever LỆCH phạm vi user duyệt "
                         f"(f={pol['f']} ≠ {CAPIT_LEVER_APPROVED_F}, "
                         f"lp={pol['loan_package_id']} ≠ {CAPIT_LEVER_APPROVED_PACKAGE}, "
                         f"accounts={pol['accounts']} ≠ {CAPIT_LEVER_APPROVED_ACCOUNTS}) "
                         f"— coi như TẮT; nới phạm vi phải sửa CODE, không sửa JSON")
        return pol, None
    except Exception as ex:
        return {}, f"không đọc được {path}: {type(ex).__name__}: {ex}"


# Ngưỡng cổng: dd52 trong file này tính theo PHẦN TRĂM (−20.0 == −20%). Hằng số ở đây khớp
# `gate: "dd52<=-0.20"` của trading_rules.json; hai bên lệch nhau ⇒ TẮT (kiểm ngay dưới).
CAPIT_LEVER_DD52_PCT = -20.0
# SÀN TỈNH TÁO, không phải tham số chiến lược. `dd52_now` rơi về sentinel −99.0 khi chuỗi
# VNINDEX RỖNG (dòng ~734) — tức là "KHÔNG CÓ DỮ LIỆU", nhưng đọc theo nghĩa đen thì nó THOẢ
# một cổng "≤ −20%" một cách ngoạn mục. Đúng hình dạng bẫy §14: một giá trị canh khuyết được
# tầng dưới hiểu thành tín hiệu cực đoan. Sự cố dữ liệu KHÔNG được phép mở đường vay tiền, nên
# mọi dd52 dưới sàn này bị coi là HỎNG (fail-closed), không phải "washout sâu kỷ lục".
# −95% chọn để tách bạch sentinel: đáy tệ nhất lịch sử VNINDEX còn cách xa mức này.
CAPIT_LEVER_DD52_SANITY_FLOOR = -95.0

# ── PIT filter Loại 1 (STRUCTURAL/MULTI_YEAR) vs Loại 2 (CONFIDENCE_LIQUIDITY/CONTAINABLE) ──
# Nguồn: macro-strategist (Bobby) `kb/data_registry/market-state/vn_macro_regime_history.md`
# (2026-08-25) + tái đánh giá `agents/Taylor/research/macro-margin-review_20260825.md` (job
# Taylor_20260825_040602): capit_margin_lever CHƯA từng test trên một ngày Loại 1 nào — cả 3
# episode trong cửa sổ backtest 2014+ (2018/2020/2022) đều là Loại 2. Ngưỡng dưới đây là
# ĐIỂM GIỮA thực nghiệm của 2 leg (CPI YoY, lãi suất huy động Big-4 12M) đo TẠI ngày mỗi
# cluster dd52<=-20% bắt đầu, trên phần dữ liệu 2011-2026 CÓ SẴN (job
# Taylor_20260825_042209): Loại-1-còn-đo-được (2011-05, 2011-07, 2011-10, 2012-08) CPI
# 6,87-21,60% / deposit 12,0-14,0%; Loại-2 (2018/2020/2022, 6 cluster) CPI 2,71-5,14% /
# deposit 5,50-6,80% — 2 dải KHÔNG chồng lấn (khoảng trống CPI 5,14→6,87; deposit 6,80→12,0).
# ⚠️ GIỚI HẠN PHẢI MANG THEO: cả `cpi_vn.py` lẫn `deposit_rate_vn.py` KHÔNG có anchor nào
# trước 2011-01 -> 6/10 cluster con dd52<=-20% CỦA LOẠI 1 (2007-04 -> 2010-11, GỒM ĐÁY SÂU
# NHẤT lịch sử VNINDEX -71,0% năm 2008-2009) không có dữ liệu để kiểm ngưỡng này — bộ lọc
# CHƯA ĐƯỢC XÁC NHẬN sẽ chặn được ngày ĐẦU của một khủng hoảng cơ cấu mới bùng phát kiểu
# 2007 (CPI/lãi suất khi đó còn chưa kịp leo cao). Đây là lớp phòng thủ THÊM (đúng tinh thần
# DT5G macro gate — "chốt rủi ro fail-safe, không phải công cụ tăng lợi nhuận"), KHÔNG PHẢI
# một luật đã backtest đầy đủ trên toàn bộ Loại 1. `deposit_rate_vn.py` các mốc trước live-
# refresh (2026-07-17) là hồi tố (đã ghi rõ trong registry của nó) — cùng mức tin cậy
# CANONICAL-PROXY mà `rating_8l.py` đang dùng sống, không phải tiêu chuẩn mới đặt ra ở đây.
CAPIT_LEVER_PIT_CPI_THRESHOLD = 6.0
CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD = 9.0


def capit_base(state, dd52w, vn_cooling):
    if state == 1: return 1.0
    if state == 3: return 0.75
    if state in (4, 5): return 0.5
    if state == 2: return 0.5 if (dd52w > -25 or vn_cooling) else 0.0
    return 0.5

print("=" * 90); print(f"  V2.3 + DT5G — DAILY RECOMMENDATIONS  ({END})"); print("=" * 90)

# ── provenance: which state source did the gate pick? ──
prov = {}
try:
    prov = json.load(open(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json"), encoding="utf-8"))
    print(f"  state source: {prov.get('source')} | as_of {prov.get('as_of')} | state {prov.get('state')} ({SNAME.get(prov.get('state'),'?')})")
except Exception as e:
    print(f"  WARNING: golive_state_today.json missing ({e}); run publish_gated_state.py first")

# ── độ tươi CỦA FILE cờ due-diligence (KHÁC TTL 30d của từng cờ) ───────────────────────
# anomaly_flags.json do ops_health_check 08:20 ghi; nếu scan chết im lặng thì file đứng im
# và gate ở §6 sẽ THIẾU mọi mã mới nổ cờ mà không ai biết — người duyệt plan phải THẤY.
# Fail-open giữ nguyên (không loại thêm/bớt mã nào), chỉ THÊM cảnh báo hiển thị.
anomaly_fresh = _anomaly_flags_freshness()
if anomaly_fresh["is_stale"]:
    print(f"  ⚠️ WARNING: anomaly_flags.json KHÔNG tươi hôm nay — {anomaly_fresh['reason']}")
    try:
        import subprocess
        subprocess.run([os.path.join(WORKDIR, "mike", "bin", "append_event.sh"), "Winston", "error",
                        "anomaly-flags-stale",
                        json.dumps({"consumer": "golive_recommend_v23", "date": END,
                                    "generated_at": anomaly_fresh["generated_at"],
                                    "reason": anomaly_fresh["reason"]}, ensure_ascii=False)],
                       timeout=30, capture_output=True)
    except Exception as _e:      # bus lỗi KHÔNG được làm hỏng luồng lập plan
        print(f"  WARNING: không ghi được bus event anomaly-flags-stale ({_e})")

# ── 1. signals with state5 from the gated DT5G series ──
SIG = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", "tav2_bq." + DT_TABLE + " AS s")
sig = bq(SIG.format(start=START, end=END)); sig["time"] = pd.to_datetime(sig["time"])
LATEST = sig["time"].max()
state_today = int(sig.loc[sig["time"] == LATEST, "state5"].dropna().iloc[0]) if (sig["time"] == LATEST).any() else int(prov.get("state", 3))
print(f"  latest signal date: {LATEST.date()} | {len(sig):,} signal rows in window")

# ── 2. D1 RE_BACKLOG (gated state) + SV_TIGHT + overheat (same layering as pt_v22_dt5g) ──
assert_universe_covers(START, END)          # §4.3 fail-safe, BEFORE the first universe-gated query
UNI_PRED = universe_pred("t")
print(f"  D1 panel universe source: {UNIVERSE_SOURCE}")
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f),
tkd AS (
  -- ICB-8633 panel: canonical ticker + ticker_1m fallback for the freshest session not yet in `ticker`
  -- Universe membership is PER DAY via {UNIVERSE_SOURCE} (see universe_pred) — the old DISTINCT-ever
  -- form had no time condition and leaked not-yet-listed names into historical dates (VHM in 2014).
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND {UNI_PRED}
  UNION ALL
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker_1m AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND {UNI_PRED}
    AND NOT EXISTS (SELECT 1 FROM tav2_bq.ticker AS x WHERE x.ticker=t.ticker AND x.time=t.time AND x.ICB_Code IS NOT NULL))
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tkd AS t LEFT JOIN tav2_bq.{DT_TABLE} AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)""")
d1["time"] = pd.to_datetime(d1["time"])
d1m = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C", "D"]) & d1["state5"].isin([3,4,5]) & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
sig = sig.merge(d1.loc[d1m, ["ticker", "time"]].assign(_ok=True), on=["ticker", "time"], how="left")
om = sig["_ok"].fillna(False) & (sig["ta"] >= 120); sig.loc[om, "play_type"] = "RE_BACKLOG_BUY"; sig = sig.drop(columns=["_ok"])

def svk(r):
    s = r.get("state5"); d = r.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True
    if s == 1: return pd.notna(d) and d <= 30
    if s in (2, 3): return pd.notna(d) and d <= 60
    return True
mb = sig["play_type"].isin(BUY_TIERS); sig = sig[(~mb) | sig.apply(svk, axis=1)].copy()
# overheat on latest dates (1-day lag on this slow gate is immaterial — see golive_recommend.py note)
vni = bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time")
vni["time"] = pd.to_datetime(vni["time"])
st = bq(f"SELECT s.time,s.state FROM tav2_bq.{DT_TABLE} AS s WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}'"); st["time"] = pd.to_datetime(st["time"])
v = vni.merge(st, on="time", how="left"); v["state"] = v["state"].ffill()
oh = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["state"] == 5) | (v["D_RSI"] > 0.75))]["time"])
sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

# ── 2b. AVOID_exbull: suppress BAL momentum tiers in EX-BULL (live 2026-06-11, IC inverts in state 5) ──
mexb = (sig["state5"] == 5) & sig["play_type"].isin(EXB_MOM)
sig.loc[mexb, "play_type"] = "AVOID_exbull"
if int(mexb.sum()): print(f"  [EXBULL] suppressed {int(mexb.sum())} momentum signal rows in EX-BULL")

# ── 2c. regime_size weak flag: ABSOLUTE 8L rating >= 4 → half size ONLY in BEAR/CRISIS ──
r8 = bq(f"""SELECT f.ticker, f.rating FROM tav2_bq.fa_ratings_8l AS f
QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) = 1""")
rating8l = dict(zip(r8["ticker"], r8["rating"]))

# ── 3. today's eligible BAL signals ──
today = sig[(sig["time"] == LATEST) & sig["play_type"].isin(TIER_BAL)].copy()
sec_map = bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
today["sec"] = today["ticker"].map(sec_map)
today["prio"] = today["play_type"].map(PRIORITY)
today["rating8l"] = today["ticker"].map(rating8l)
today["weak"] = today["rating8l"].fillna(0).astype(float) >= 4
half_in_state = state_today in (1, 2)
today["weight"] = np.where(today["weak"] & half_in_state, WEAK_PCT, POS_PCT)

# GATE CỨNG sàn thanh khoản ADV3T ≥ 2 tỷ/phiên cho BAL (user chốt 2026-08-10, job
# Taylor_20260810_081207) — LOẠI TRƯỚC `select_book` để slot bị bỏ trống được ứng viên
# XẾP SAU lấp vào (đo 365 ngày: 26/47 phiên có >12 dòng eligible ⇒ hàng đợi thường dài hơn
# MAX_POS, nên phần lớn phiên sẽ có mã lấp chỗ). Trọng số/slot KHÔNG đổi (vẫn POS_PCT) —
# gate này KHÔNG dồn vốn vào mã to hơn, xem báo cáo §2. SIGNAL_V11 đã chặn sẵn `liq >= 1e9`
# nên phần THÊM của sàn 2 tỷ = băng [1e9, 2e9) ≈ 11,1% số dòng eligible (16 tên/365 ngày).
today, bal_liq_dropped, bal_liq_error = bal_filter_thin(today)
if bal_liq_dropped:
    print(f"  [bal-liq] loại {len(bal_liq_dropped)} dòng BAL dưới sàn ADV3T "
          f"{ADV_MIN_VND/1e9:.0f} tỷ: "
          + ", ".join(f"{d['ticker']} ({(d['adv_vnd'] or 0)/1e9:.2f} tỷ)" for d in bal_liq_dropped))
if bal_liq_error:
    print(f"  WARNING: sàn ADV BAL KHÔNG áp được ({bal_liq_error}) — giữ nguyên danh sách "
          f"(SIGNAL_V11 vẫn chặn liq >= 1e9 trong SQL)")

def select_book(cand):
    c = cand.sort_values(["prio", "ta"], ascending=[True, False])
    picked, fin_re = [], 0
    for _, r in c.iterrows():
        if len(picked) >= MAX_POS: break
        is_finre = (r["sec"] == 8)
        exempt = (r["play_type"] == "RE_BACKLOG_BUY")
        if is_finre and not exempt and fin_re >= 4: continue
        picked.append(r)
        if is_finre and not exempt: fin_re += 1
    return pd.DataFrame(picked)

bal = select_book(today)

# ── 4. LAG book (always-on): PEAD entries due ──
trade_dates = sorted(vni["time"].unique())
def td_offset(ref, off):
    """ref + off trading days; returns (date|None, sessions_beyond_LATEST if extrapolated)."""
    pos = int(np.searchsorted(np.array(trade_dates, dtype="datetime64[ns]"), np.datetime64(ref), side="right")) - 1
    if pos < 0: return None, None
    tgt = pos + off
    if tgt < len(trade_dates): return pd.Timestamp(trade_dates[tgt]), 0
    return None, tgt - (len(trade_dates) - 1)     # entry falls N sessions AFTER the latest session

# lag_source_error: None = nguồn LAG đọc OK (n_lag_*=0 nghĩa là THẬT SỰ không có sự kiện);
# string = except-path fired — máy đọc status.json phân biệt được "không có gì" vs "nguồn hỏng"
# (audit M1 Spyros_20260712_131501: pkl lỗi giữa mùa BCTC trước đây chỉ in WARNING vào log cron,
# n_lag_upcoming=0 lặng lẽ tái tạo đúng failure-mode gốc).
lag_up, lag_recent, lag_source_error = [], [], None
lag_liq_dropped, lag_liq_error = [], None
lag_rating_dropped, lag_rating_error = [], None
lag_forensic_dropped, lag_forensic_error = [], None
try:
    # Point-in-time candidate source (fix 2026-07-12, audit Taylor_20260712_121642 R1):
    # events must be visible here FROM their release date. The old source
    # (earnings_events_classified.csv) only surfaces an event once its release+30
    # price mark exists — ~25 sessions AFTER the T+5 entry had already passed — so
    # every new-release entry was silently missed. live_lag_candidates() takes event
    # identity/NP_R/surprise from earnings_surprise_data.pkl (fresh daily, visible
    # same-day) and prior_n_good/pa_HL3 from the classified CSV (priors are >=1
    # quarter old, always fully windowed). The CSV keeps its exact old semantics for
    # the backtest/full-replay path (pt_v23_audit_2014, pt_v22) — untouched.
    from lag_live_schedule import live_lag_candidates
    cand = live_lag_candidates(start=START)
    print(f"  [lag-live] {len(cand)} events in window, {int(cand['qualify'].sum())} qualify"
          + (f", release max {cand['Release_Date'].max().date()}" if len(cand) else ""))
    cand = cand[cand["qualify"]]
    # Lọc thanh khoản Ở TẦNG TÍN HIỆU (user quyết 2026-07-21) — xem lag_filter_illiquid():
    # mã ADV≤0/không đo được KHÔNG thành mục tiêu, nên vốn tự chảy sang event LAG kế tiếp
    # thay vì nằm im chờ một lệnh mà executor sẽ chặn.
    cand, lag_liq_dropped, lag_liq_error = lag_filter_illiquid(bq, cand, LATEST)
    if lag_liq_dropped:
        print(f"  [lag-liq] loại {len(lag_liq_dropped)} ứng viên không đo được thanh khoản: "
              + ", ".join(f"{d['ticker']} ({d['reason']})" for d in lag_liq_dropped))
    # GATE CỨNG chất lượng 8L (user chốt 2026-07-27) — xem lag_filter_low_rating():
    # ứng viên LAG rating≥4 (RATING_FAIL) bị LOẠI THẬT khỏi danh sách, không escalate từng ca.
    # CHỈ book LAG; BAL/CAPIT/custom30V có gate rating riêng, không đụng.
    cand, lag_rating_dropped, lag_rating_error = lag_filter_low_rating(bq, cand, LATEST)
    if lag_rating_dropped:
        print(f"  [lag-rating] loại {len(lag_rating_dropped)} ứng viên RATING_FAIL (8L≥4): "
              + ", ".join(f"{d['ticker']} (8L={d['rating']})" for d in lag_rating_dropped))
    # GATE QUẢN TRỊ: BANNED vĩnh viễn + cờ forensic severity=exclude (user duyệt 2026-08-03,
    # job Taylor_20260803_035250) — xem lag_filter_forensic_banned(). Engine backtest đã có gate
    # này từ 2026-06-20 (LAG_FORENSIC_GATE) nhưng đường live thì KHÔNG: VVS (BANNED + forensic)
    # và BFC (forensic) qua sạch mọi gate tự động, chỉ được chặn BẰNG TAY trong plan note 07-30.
    cand, lag_forensic_dropped, lag_forensic_error = lag_filter_forensic_banned(
        cand, LATEST, workdir=WORKDIR)
    if lag_forensic_dropped:
        print(f"  [lag-forensic] loại {len(lag_forensic_dropped)} ứng viên BANNED/forensic: "
              + ", ".join(f"{d['ticker']} ({d['kind']})" for d in lag_forensic_dropped))
    for _, row in cand.iterrows():
        entry, ahead = td_offset(row["Release_Date"], 5)
        tier = row["tier"]
        item = {"ticker": row["ticker"], "tier": tier, "release": row["Release_Date"].date(),
                "np_r": float(row["NP_R"]), "pa_hl3": float(row["pa_HL3"])}
        if entry is None and ahead is not None and 1 <= ahead <= 5:
            item["entry"] = f"T+{ahead} phiên tới"; lag_up.append(item)
        elif entry is not None and entry > LATEST:
            item["entry"] = str(entry.date()); lag_up.append(item)
        elif entry is not None and entry >= LATEST - pd.Timedelta(days=5) and entry <= LATEST:
            item["entry"] = str(entry.date()); lag_recent.append(item)
except Exception as e:
    lag_source_error = f"{type(e).__name__}: {e}"
    print(f"  WARNING: LAG schedule unavailable ({e})")
print(f"  LAG entries: {len(lag_up)} upcoming, {len(lag_recent)} entered in last sessions")

# ── 5. Allocator: w_LAG target vs current (band ±10pp) ──
w_tgt = w_lag_target(state_today, LATEST)   # edge-conditional (was hardcoded 65% until 2026-07-12)
w_cur, alloc_note = None, "pt_v22 logs unavailable"
try:
    pl = pd.read_csv(os.path.join(WORKDIR, "data", "pt_v22_dt5g_logs.csv"), parse_dates=["ymd"]).sort_values("ymd")
    last = pl.iloc[-1]
    lag_mv = float(last["SECOND_cash"]) + float(last["SECOND_stocks"]) + float(last["SECOND_etf"])
    w_cur = lag_mv / float(last["nav"]) if float(last["nav"]) > 0 else None
    alloc_note = f"as of {last['ymd'].date()}"
except Exception as e:
    print(f"  WARNING: cannot read pt_v22 logs ({e})")
band_breach = (w_cur is not None) and (abs(w_cur - w_tgt) > ALLOC_BAND)

# ── 6. CAPIT v2 monitor (gate 30% + state routing + grind + BEAR guard) ──
br = bq(capit_breadth_sql(START_BR, END))
br["time"] = pd.to_datetime(br["time"])
breadth_today = float(br["oversold"].iloc[-1]) if len(br) else np.nan
breadth_stale, breadth_src_max = capit_breadth_is_stale(br["time"].max() if len(br) else pd.NaT, END)
if breadth_stale:
    print(f"  WARNING: breadth CAPIT CŨ — chuỗi tới {br['time'].max() if len(br) else 'rỗng'} "
          f"nhưng dữ liệu giá đã có tới {breadth_src_max}. CAPIT FAIL-CLOSED (không fire lệnh "
          f"mới trên dữ liệu cũ). Chạy mike/bin/build_universe_pit.py + _quality.py cho ngày thiếu.")
capit_signal_today = bool(pd.notna(breadth_today) and breadth_today >= WASHOUT_GATE and not breadth_stale)
vnh = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_VNI}' AND DATE '{END}' ORDER BY t.time""")
vnh["time"] = pd.to_datetime(vnh["time"]); vnh = vnh.set_index("time")
vnh["dd52"] = (vnh["Close"] / vnh["Close"].rolling(252, min_periods=60).max() - 1) * 100
_r = vnh["Close"].pct_change()
vnh["rv10"] = _r.rolling(10).std() * np.sqrt(252) * 100
vnh["vn_cooling"] = vnh["rv10"] <= vnh["rv10"].rolling(30).max() * 0.85
dd52_now = float(vnh["dd52"].iloc[-1]) if len(vnh) else -99.0
vn_cool_now = bool(vnh["vn_cooling"].iloc[-1]) if len(vnh) and pd.notna(vnh["vn_cooling"].iloc[-1]) else False

capit_size, capit_grind, basket, capit_dd_excluded = 0.0, False, [], []
capit_caps_total, capit_caps, capit_shares, capit_share_mode, capit_share_detail = {}, {}, {}, "n/a", {}
capit_targets = {}
if capit_signal_today:
    wdays = br[br["oversold"] >= WASHOUT_GATE]["time"].tolist()
    bdates = br["time"].tolist(); i0 = len(bdates) - 1
    wset = set(wdays)
    for back in range(20, 91):
        j = i0 - back
        if j >= 0 and bdates[j] in wset: capit_grind = True; break
    base = capit_base(state_today, dd52_now, vn_cool_now)
    capit_size = base * (0.5 if capit_grind else 1.0)
    if capit_size > 0.005:
        bd = br["time"].iloc[-1]
        e = bq(capit_pool_sql(bd.date()))
        excl = anomaly_excluded(bd.date())
        hit = sorted(set(e["ticker"]) & excl) if not e.empty else []
        if hit:
            capit_dd_excluded = hit
            print(f"  CAPIT due-diligence: loại {hit} khỏi pool (cờ bất thường <{ANOMALY_TTL_DAYS}d)")
            e = e[~e["ticker"].isin(excl)]
        if not e.empty:
            g = e[e["pbz"] < -1]; c = e[e["pbz"] < 0]
            pick = g if len(g) >= 3 else (c if len(c) >= 3 else e)
            pick = pick.nsmallest(15, "pbz") if len(pick) > 15 else pick
            basket = sorted(pick["ticker"].tolist())
            # trần TỔNG fleet cho mỗi mã → chia cho từng account đang deploy CAPIT.
            capit_caps_total = capit_adv_caps(basket, bd)
            capit_shares, capit_share_mode, capit_share_detail = capit_account_shares()
            capit_caps = {a: {t: v * s for t, v in capit_caps_total.items()}
                          for a, s in capit_shares.items()}
            # ── VND mục tiêu/slot, TÍNH SẴN MỘT LẦN cho từng account ────────────────────
            # Sự cố 07-21 (finding Taylor_20260731_154624): plan SpaceX nhân `capit_size`
            # HAI LẦN — lấy `weight_pct`=15,0 của dòng CAPIT trong CSV (vốn ĐÃ = capit_size/n)
            # rồi nhân lên `capit_total_target_vnd` (vốn ĐÃ = NAV_book_LAG × capit_size) ⇒
            # hiệu lực capit_size². Deploy 254,4tr thay vì 348,4tr (thiếu 87,1tr; phần còn
            # lại 6,8tr mới là làm tròn lô). Cùng ngày, cùng tín hiệu, plan ZaloPay chia
            # đúng /n ⇒ đây là lỗi ĐỌC MỘT CỘT ĐA NGHĨA, không phải lỗi số học ngẫu nhiên.
            # Cách sửa: publish thẳng VND để tầng plan KHÔNG phải tự lắp lại công thức.
            # Cơ sở NAV = _account_nav_basis() = đúng `active_nav` DollarBill dùng sizing.
            for _a in sorted(capit_shares):
                _nav = (capit_share_detail.get(_a) or {}).get("nav")
                if not _nav:
                    capit_targets[_a] = {"nav_basis_vnd": None, "nav_basis_source":
                                         (capit_share_detail.get(_a) or {}).get("source"),
                                         "error": "không có cơ sở NAV — tầng plan phải tự tính"}
                    continue
                _book = float(_nav) * float(w_tgt)
                _tot = _book * capit_size
                capit_targets[_a] = {
                    "nav_basis_vnd": round(float(_nav)), "nav_basis_source":
                        (capit_share_detail.get(_a) or {}).get("source"),
                    "w_lag_target": w_tgt, "capit_size": round(capit_size, 4),
                    "nav_book_lag_vnd": round(_book), "capit_total_target_vnd": round(_tot),
                    "n_slots": len(basket),
                    "capit_slot_target_vnd": round(_tot / len(basket)),
                    "formula": "slot = active_nav × w_lag_target × capit_size / n_slots "
                               "(công thức booknav user chốt 2026-07-20). ĐÃ GỒM capit_size — "
                               "KHÔNG nhân capit_size hay weight_pct thêm lần nữa.",
                }

# ── 6a. Đòn bẩy margin CHỈ cho sự kiện CAPIT vừa fire (cổng dd52<=−20%) ─────────────────
# Khối này KHÔNG gán lại biến quyết định nào của §6 — nó chỉ ĐỌC (dd52_now, capit_signal_today,
# capit_size, basket) và THÊM trường vào artifact. `enabled=false` ⇒ `active=false` ⇒ mọi tầng
# dưới hành xử y hệt trước khi có tính năng này (không có lệnh nào đổi, không có sizing nào đổi).
#
# Cặp mốc CAPIT_LEVER_BEGIN/END dưới đây KHÔNG phải chú thích trang trí: capit_lever_selfcheck.py
# CẮT ĐÚNG đoạn source giữa hai mốc rồi exec nó với đầu vào washout giả lập. Diễn tập vì thế chạy
# TRÊN CHÍNH code production này, không phải một bản chép tay sẽ trôi khỏi nó (bài học §17
# extract-and-test: tuyên bố "đã kiểm" mà không có test neo vào source thật đã hỏng 2 lần).
# Đổi/di chuyển hai mốc này ⇒ selfcheck fail ngay, đó là chủ đích.
# CAPIT_LEVER_BEGIN
_lever_pol, _lever_err = capit_lever_policy()
# Cổng chỉ được coi là "đạt" khi ngưỡng trong code KHỚP ngưỡng khai trong file chính sách —
# lệch nhau là dấu hiệu ai đó sửa 1 bên (fail-closed, không tự hoà giải).
_gate_decl_ok = str(_lever_pol.get("gate") or "") == f"dd52<={CAPIT_LEVER_DD52_PCT / 100:.2f}"
if _lever_pol and not _gate_decl_ok and not _lever_err:
    _lever_err = (f"gate khai trong trading_rules.json = {_lever_pol.get('gate')!r} ≠ ngưỡng "
                  f"code {CAPIT_LEVER_DD52_PCT}% — coi như TẮT")
_gate_pass = bool(pd.notna(dd52_now)
                  and CAPIT_LEVER_DD52_SANITY_FLOOR <= dd52_now <= CAPIT_LEVER_DD52_PCT)
if pd.notna(dd52_now) and dd52_now < CAPIT_LEVER_DD52_SANITY_FLOOR and not _lever_err:
    _lever_err = (f"dd52={dd52_now} dưới sàn tỉnh táo {CAPIT_LEVER_DD52_SANITY_FLOOR}% — "
                  f"gần như chắc chắn là sentinel thiếu dữ liệu, KHÔNG phải washout; coi như TẮT")

# PIT filter Loại 1/Loại 2 (xem hằng số CAPIT_LEVER_PIT_*_THRESHOLD ở trên cho nguồn gốc
# ngưỡng + giới hạn dữ liệu). Chỉ tính khi còn cơ hội arm (đỡ 1 lượt đọc CPI/lãi suất huy
# động không cần thiết những ngày cổng dd52 chưa đạt) — nhưng LUÔN ghi vào artifact để
# quan sát được ngay cả những ngày lever không fire.
import cpi_vn, deposit_rate_vn
_pit_cpi_yoy = _pit_deposit_rate = None
_pit_structural, _pit_reason = False, "chưa tính (cổng dd52 hoặc công tắc chưa đạt)"
if not _lever_err and _gate_pass:
    try:
        _pit_end = str((LATEST + cpi_vn.pd.DateOffset(months=2)).date())
        _pit_q = cpi_vn.pd.DataFrame({"time": [LATEST]})
        _pit_cpi_yoy = float(cpi_vn.merge_cpi(_pit_q, end=_pit_end)["cpi_yoy"].iloc[0])
        _pit_deposit_rate = float(deposit_rate_vn.merge_deposit(_pit_q)["deposit_rate"].iloc[0])
        # Chặn blind-spot ngoại suy của cpi_vn.py (đo thực nghiệm job Taylor_20260825_042209):
        # QUÁ tháng NSO thật gần nhất (`NSO_CPI_YOY_REAL`, hiện 2026-06), hàm nội suy KHÔNG
        # NaN mà lặng lẽ forward-fill từ mốc Tier-2 CŨ (2025-05, 3,4%) — bỏ qua hoàn toàn xu
        # hướng thật gần nhất (2026 Q2 leo 4,65->5,60->4,69%). Với CỔNG CHẶN VAY, đánh giá
        # THẤP CPI là sai chiều fail-safe -> lấy MAX(giá trị nội suy, số NSO thật gần nhất
        # đã biết) khi ngày hỏi đã qua tháng NSO thật cuối cùng; không bao giờ hạ thấp hơn
        # số thật gần nhất. KHÔNG sửa cpi_vn.py (module dùng chung, ngoài phạm vi job này).
        _real_items = sorted(cpi_vn.NSO_CPI_YOY_REAL.items())
        _last_real_date = cpi_vn.pd.to_datetime(_real_items[-1][0])
        if cpi_vn.pd.Timestamp(LATEST) > _last_real_date and not cpi_vn.pd.isna(_pit_cpi_yoy):
            _pit_cpi_yoy = max(_pit_cpi_yoy, _real_items[-1][1])
    except Exception as _pit_ex:
        _pit_structural = True
        _pit_reason = (f"lỗi đọc CPI/lãi suất huy động ({type(_pit_ex).__name__}: {_pit_ex}) — "
                       f"fail-closed COI NHƯ Loại 1, KHÔNG áp đòn bẩy")
    else:
        if cpi_vn.pd.isna(_pit_cpi_yoy) or cpi_vn.pd.isna(_pit_deposit_rate):
            _pit_structural = True
            _pit_reason = (f"CPI/lãi suất huy động NaN tại {LATEST.date()} (ngoài phạm vi dữ "
                           f"liệu, trước 2011-01) — fail-closed COI NHƯ Loại 1, KHÔNG áp đòn bẩy")
            # Chuẩn hoá NaN -> None TRƯỚC khi vào dict artifact: `json.dump` mặc định ghi
            # literal `NaN` (không phải JSON hợp lệ, nhiều parser khác từ chối đọc) và nó
            # cũng phá luôn phép so sánh `is None` mà mọi field khác trong dict này dùng
            # (vd `dd52_pct` ở trên qua `pd.notna(...) else None`) — cùng quy ước, không bịa
            # quy ước mới riêng cho 2 field này.
            _pit_cpi_yoy = _pit_deposit_rate = None
        elif _pit_cpi_yoy >= CAPIT_LEVER_PIT_CPI_THRESHOLD:
            _pit_structural = True
            _pit_reason = (f"CPI YoY {_pit_cpi_yoy:.2f}% >= ngưỡng "
                           f"{CAPIT_LEVER_PIT_CPI_THRESHOLD}% — dấu hiệu khủng hoảng CƠ CẤU "
                           f"(Loại 1 kiểu 2007-2012), KHÔNG áp đòn bẩy dù dd52 đã đạt cổng")
        elif _pit_deposit_rate >= CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD:
            _pit_structural = True
            _pit_reason = (f"lãi suất huy động Big-4 12M {_pit_deposit_rate:.2f}%/năm >= "
                           f"ngưỡng {CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD}%/năm — dấu hiệu khủng "
                           f"hoảng CƠ CẤU (Loại 1), KHÔNG áp đòn bẩy dù dd52 đã đạt cổng")
        else:
            _pit_reason = (f"CPI YoY {_pit_cpi_yoy:.2f}% < {CAPIT_LEVER_PIT_CPI_THRESHOLD}% và "
                           f"lãi suất huy động {_pit_deposit_rate:.2f}% < "
                           f"{CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD}% — tương thích khủng hoảng "
                           f"NIỀM TIN/THANH KHOẢN có thể chứa được (Loại 2), PIT filter cho qua")

_lever_active = bool(_lever_pol.get("enabled") and not _lever_err and _gate_pass
                     and not _pit_structural
                     and capit_signal_today and capit_size > 0.005 and basket)
if _lever_active:
    _f = float(_lever_pol["f"])
    for _a in list(capit_targets):
        if _a not in _lever_pol["accounts"]:
            continue                      # account ngoài phạm vi duyệt → KHÔNG chạm
        _t = capit_targets[_a]
        if not _t.get("capit_total_target_vnd"):
            continue                      # thiếu cơ sở NAV → để tầng plan tự xử, không bịa số
        _t["lever_f"] = _f
        _t["lever_loan_package_id"] = _lever_pol["loan_package_id"]
        _t["capit_total_target_vnd_levered"] = round(_t["capit_total_target_vnd"] * _f)
        _t["capit_slot_target_vnd_levered"] = round(
            _t["capit_total_target_vnd_levered"] / max(len(basket), 1))
        _t["lever_formula"] = (
            "slot_levered = capit_slot_target_vnd × f. Phần VƯỢT trên vốn tự có là VAY "
            f"(gói {_lever_pol['loan_package_id']}). Trần %ADV `capit_adv_caps` KHÔNG nhân f "
            "(trần đo tác động thị trường, không phụ thuộc nguồn vốn) ⇒ lệnh thật vẫn = "
            "min(mục tiêu, trần).")
capit_lever = {
    "enabled": bool(_lever_pol.get("enabled")),
    "active": _lever_active,
    "f": (_lever_pol.get("f") if _lever_pol else None),
    "loan_package_id": (_lever_pol.get("loan_package_id") if _lever_pol else None),
    "accounts": (_lever_pol.get("accounts") if _lever_pol else []),
    "scope": (_lever_pol.get("scope") if _lever_pol else None),
    "gate": f"dd52<={CAPIT_LEVER_DD52_PCT}%",
    "gate_threshold_pct": CAPIT_LEVER_DD52_PCT,
    "dd52_pct": (round(dd52_now, 2) if pd.notna(dd52_now) else None),
    "gate_pass": _gate_pass,
    "capit_signal_today": capit_signal_today,
    "capit_size": round(capit_size, 4),
    "n_capit_basket": len(basket),
    "policy_error": _lever_err,
    "pit_filter_structural": _pit_structural,
    "pit_filter_reason": _pit_reason,
    "pit_cpi_yoy": (round(_pit_cpi_yoy, 2) if _pit_cpi_yoy is not None else None),
    "pit_deposit_rate": (round(_pit_deposit_rate, 2) if _pit_deposit_rate is not None else None),
    "pit_cpi_threshold": CAPIT_LEVER_PIT_CPI_THRESHOLD,
    "pit_deposit_threshold": CAPIT_LEVER_PIT_DEPOSIT_THRESHOLD,
    "reason": ("đòn bẩy CAPIT ĐANG ÁP cho sự kiện này" if _lever_active else
               ("chính sách TẮT (enabled=false) — cần user xác nhận riêng mới bật"
                if not _lever_pol.get("enabled") else
                (_lever_err or ("cổng dd52 chưa đạt "
                                f"({dd52_now:.2f}% > {CAPIT_LEVER_DD52_PCT}%)" if not _gate_pass
                                else (_pit_reason if _pit_structural
                                      else "không có sự kiện CAPIT đang fire hôm nay"))))),
}
if _lever_err:
    print(f"  WARNING: chính sách đòn bẩy CAPIT — {_lever_err} (fail-closed: KHÔNG áp đòn bẩy)")
if _pit_structural:
    print(f"  WARNING: PIT filter chặn đòn bẩy CAPIT (nghi Loại 1 STRUCTURAL) — {_pit_reason}")
if _lever_active:
    print(f"  🔺 ĐÒN BẨY CAPIT ÁP DỤNG: f={_lever_pol['f']} gói vay "
          f"{_lever_pol['loan_package_id']} cho account {_lever_pol['accounts']} "
          f"(dd52={dd52_now:.1f}% ≤ {CAPIT_LEVER_DD52_PCT}%)")
# CAPIT_LEVER_END

# ── 6b. Sổ episode CAPIT (QUAN SÁT THUẦN — bên NGOÀI nhánh `if capit_signal_today`) ──
# `capit_signal_today` là điều kiện CỦA NGÀY CHẠY: breadth rớt dưới gate ⇒ cờ về False và
# basket/size về rỗng NGAY, dù vị thế thật vẫn đang giữ (đúng cái đã xảy ra 07-29/07-30 khi còn đủ 5 mã ở 2
# account). Sổ episode giữ "đã vào lệnh 07-20, còn mở" để mọi kênh báo cáo không im lặng.
# RÀNG BUỘC: khối này chỉ ĐỌC basket/capit_size/capit_signal_today đã tính xong ở trên và GHI 1 file log
# riêng — không gán lại biến quyết định nào. Xem capit_episode.py (giới hạn + cơ chế đóng episode).
import capit_episode
capit_ep = capit_episode.update(
    signal_date=str(LATEST.date()), signal_today=capit_signal_today, basket=basket, size=capit_size,
    session_dates=[str(d.date()) for d in vnh.index])
if capit_ep.get("capit_episode_open"):
    print(f"  CAPIT episode {capit_ep['capit_episode_id']} ĐANG MỞ "
          f"(entry {capit_ep['capit_episode_entry_date']}, {capit_ep['capit_sessions_held']} phiên, "
          f"rổ gốc {capit_ep['capit_episode_basket']})")
if capit_ep.get("capit_episode_error"):
    print(f"  WARNING: sổ episode CAPIT — {capit_ep['capit_episode_error']}")

# ── 7. emit recommendations (CSV + MD + status JSON) ──
etf_frac = ETF_PARK.get(state_today, 0.0)

# fetch parking basket early — used for both CSV rows and MD text
_park_basket = None
_park_rebal_date = None
if etf_frac > 0:
    try:
        import custom30
        # V2.4 spec: parking = custom30V (yieldcombo, tav2_bq.custom30v_8l) — the basket the
        # +7.4pp result was backtested on. NOT custom30_8l (blend), which this read until
        # 2026-07-11 (mislabel bug: advisory said "custom30V" but served the blend basket).
        _park_basket = custom30.current(bq, table=custom30.TABLE_V)
        if len(_park_basket):
            _park_rebal_date = str(_park_basket["rebal_date"].iloc[0])
    except Exception as _e:
        print(f"  WARNING: custom30 lookup failed: {_e}")

# Field giá trong recs = Close BQ của NGÀY SIGNAL (trễ >=1 phiên lúc DollarBill đọc ~19:00).
# Tên field cố tình xấu (audit Taylor_20260711_031821 F2): sự cố 07-09 cho thấy prompt cấm
# không đủ ngăn LLM lấy field "close" tiện tay làm ref_price — đổi tên để ref_price bắt buộc
# phải lấy từ DNSE live, không còn field "close" nào trong context lập plan để với nhầm.
#
# `weight_pct` DÙNG CHUNG cho 4 book nhưng MẪU SỐ KHÁC NHAU ở mỗi book — cột `weight_base`
# đi kèm nói rõ 100% là của cái gì. Không có nó, sự cố 07-21 đã xảy ra: dòng CAPIT ghi 15,0
# (= capit_size/n, tức ĐÃ gồm capit_size) bị hiểu là "15% của tổng vốn CAPIT" rồi nhân tiếp
# lên tổng ⇒ capit_size². Cùng ngày, cùng CSV, hai plan đọc ra hai nghĩa khác nhau.
recs = []
for _, r in bal.iterrows():
    recs.append({"book": "BAL", "ticker": r["ticker"], "play_type": r["play_type"],
                 "ta": round(float(r["ta"]), 0), "close_bq_stale_DO_NOT_USE_AS_REFPRICE": round(float(r["Close"]), 1),
                 "sector": int(r["sec"]) if pd.notna(r["sec"]) else None,
                 "weight_pct": r["weight"]*100, "weight_base": "BAL_book",
                 "status": "HALF_SIZE" if (r["weak"] and half_in_state) else "FULL"})
for it in lag_up:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "weight_base": "LAG_book",
                 "status": f"UPCOMING {it['entry']}"})
for it in lag_recent:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "weight_base": "LAG_book",
                 "status": f"WINDOW_PASSED {it['entry']}"})
for tk in basket:
    recs.append({"book": "CAPIT", "ticker": tk, "play_type": "CAPIT_GOLDEN",
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(tk),
                 "weight_pct": round(capit_size / max(len(basket), 1) * 100, 2),
                 # Mẫu số là NAV_book_LAG (= active_nav × w_lag_target), và con số này ĐÃ
                 # nhân capit_size sẵn. VND/slot đã tính sẵn ở status["capit_slot_targets"] —
                 # DÙNG THẲNG số đó, đừng lắp lại công thức từ cột này.
                 "weight_base": "NAV_book_LAG__DA_GOM_capit_size__KHONG_NHAN_LAI",
                 "status": "WASHOUT",
                 # TỔNG cả fleet — CSV này account-agnostic. Trần của TỪNG account (đã chia)
                 # nằm ở status["capit_adv_caps"][<label>] và đó mới là cái executor enforce.
                 "capit_cap_total_vnd": round(capit_caps_total[tk]) if tk in capit_caps_total else None})
# parking basket — advisory rows (book=PARK, weight_pct = within-basket cap-weight %)
if _park_basket is not None:
    for pr in _park_basket.itertuples():
        recs.append({"book": "PARK", "ticker": pr.ticker, "play_type": "CUSTOM30V_8L",
                     "ta": float(pr.rating_8l) if pd.notna(pr.rating_8l) else None,
                     "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": None,
                     "weight_pct": round(float(pr.weight) * 100, 4),
                     "weight_base": "parking_basket", "status": "PARK_ADVISORY"})
# ── Due-diligence tổng hợp cho MỌI ứng cử viên (mandate user 2026-07-21) ──
# Đây là CHOKE-POINT SỚM NHẤT: mọi mã ở đây mới chỉ là ứng cử viên, chưa thành lệnh. Lớp này
# THUẦN THÔNG TIN (thanh khoản/universe/cơ học surprise/cờ bất thường/FA/định giá) — KHÔNG loại
# mã, KHÔNG đổi weight, KHÔNG thêm gate. Bối cảnh: rà tay LAG 07-24 (IVS/TMG/TRC) phát hiện
# TMG thanh khoản=0 + ngoài ticker_prune, IVS 39% ADV — không cơ chế tự động nào bắt được.
# Đọc bq_cache local (T-1) qua module riêng, KHÔNG động vào đường BQ live ở trên.
dd_map = {}
try:
    from trading_bot.due_diligence import run_due_diligence as _run_dd
    for _r in recs:
        _t, _b = _r["ticker"], _r["book"]
        if (_t, _b) not in dd_map:
            dd_map[(_t, _b)] = _run_dd(_t, _b, {"asof": str(LATEST.date())})
except Exception as _e:
    print(f"  WARNING: due-diligence layer lỗi: {_e}")
for _r in recs:
    _s = dd_map.get((_r["ticker"], _r["book"]), "")
    _r["due_diligence"] = " | ".join(x.strip() for x in str(_s).splitlines()) if _s else ""

rec_df = pd.DataFrame(recs, columns=["book","ticker","play_type","ta","close_bq_stale_DO_NOT_USE_AS_REFPRICE","sector","weight_pct","weight_base","status","capit_cap_total_vnd","due_diligence"])
csv_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.csv")
rec_df.to_csv(csv_path, index=False)

status = {
    "date": END, "signal_date": str(LATEST.date()), "state": state_today,
    "state_name": SNAME.get(state_today, "?"), "source": prov.get("source"),
    "w_lag_target": w_tgt, "w_lag_current": (round(w_cur, 4) if w_cur is not None else None),
    "alloc_band": ALLOC_BAND, "band_breach": bool(band_breach), "alloc_note": alloc_note,
    "etf_park_frac": etf_frac,
    "breadth_oversold": (round(breadth_today, 4) if pd.notna(breadth_today) else None),
    # ĐỌC KỸ TÊN: `capit_signal_today` = gate breadth CỦA RIÊNG NGÀY CHẠY (tên cũ `capit_fired`
    # đọc nhầm thành "đang giữ CAPIT" — đúng cái sai đã xảy ra 07-30). Muốn biết CÓ ĐANG GIỮ hay
    # không thì đọc `capit_episode_open` (§6b), không đọc cờ này.
    "washout_gate": WASHOUT_GATE, "capit_signal_today": capit_signal_today,
    # ALIAS TƯƠNG THÍCH NGƯỢC — giữ, KHÔNG bỏ: (a) cột BQ `recommend_v23.status.capit_fired` đã có
    # lịch sử, push_recommend_v23_to_bq.py map theo đúng tên này; (b) bản release đóng gói
    # release_8l_full/ là ảnh chụp, không sửa theo. Consumer MỚI phải dùng capit_signal_today.
    "capit_fired": capit_signal_today,
    # P4 (§4.4-C-conserv): mẫu số breadth + ngưỡng ĐI KÈM NHAU — ghi cả hai vào artifact để một
    # bản ghi lịch sử luôn tự nói được nó sinh ra trên thang đo nào.
    "capit_universe_source": CAPIT_BREADTH_SOURCE,
    "capit_breadth_topn": (CAPIT_TOPN if CAPIT_BREADTH_SOURCE == "pit" else None),
    "capit_breadth_stale": breadth_stale, "capit_breadth_src_max": breadth_src_max,
    "capit_size": round(capit_size, 2), "capit_grind": capit_grind,
    "capit_dd_excluded": capit_dd_excluded,
    # Trần VND tuyệt đối/tên ĐÃ CHIA THEO ACCOUNT — NGUỒN CHUẨN TẮC mà bot_execute.py
    # enforce. Cố tình KHÔNG dựa vào DollarBill copy field này vào plan: executor đọc thẳng
    # artifact ở đây, nên plan generator quên áp cap cũng không làm mất cap.
    # Cấu trúc {label: {ticker: vnd}} — mỗi account CHỈ thấy phần của mình; Σ theo account
    # = capit_adv_caps_total (bất biến an toàn). Xem capit_adv_caps()/capit_account_shares().
    "capit_adv_caps": {a: {t: round(v) for t, v in sorted(c.items())}
                       for a, c in sorted(capit_caps.items())},
    "capit_adv_caps_total": {t: round(v) for t, v in sorted(capit_caps_total.items())},
    "capit_adv_shares": {a: round(s, 6) for a, s in sorted(capit_shares.items())},
    "capit_adv_share_mode": capit_share_mode,
    "capit_adv_share_nav": {a: d for a, d in sorted(capit_share_detail.items())},
    "capit_adv_x": ADV_X, "capit_adv_d": ADV_D,
    # VND MỤC TIÊU/slot ĐÃ TÍNH SẴN cho từng account — NGUỒN CHUẨN TẮC để lập plan CAPIT.
    # Tầng plan COPY thẳng `capit_slot_target_vnd`, KHÔNG nhân thêm `weight_pct` của CSV
    # (cột đó ĐÃ gồm capit_size — nhân lại là ra capit_size², đúng lỗi 07-21 làm SpaceX
    # thiếu 87,1tr). KHÁC HẲN `capit_adv_caps`: đó là TRẦN thanh khoản (ràng buộc trên,
    # executor enforce cứng); đây là MỤC TIÊU phân bổ. Lệnh thật = min(mục tiêu, trần),
    # rồi mới làm tròn lô.
    "capit_slot_targets": capit_targets,
    # ĐÒN BẨY MARGIN cho RIÊNG sleeve CAPIT (§6a) — NGUỒN CHUẨN TẮC mà bot_execute.py đọc
    # (trading_bot/plan.py::apply_capit_lever). `active=false` ⇒ KHÔNG lệnh nào được gắn cờ
    # vay; plan có tự viết `lever_f` vào cũng bị GỠ. Xem data/trading_rules.json
    # → capit_margin_lever (mặc định enabled=false, bật cần user xác nhận riêng).
    "capit_lever": capit_lever,
    "dd52w": round(dd52_now, 1), "vn_cooling": vn_cool_now,
    "n_bal": int(len(bal)), "n_lag_upcoming": len(lag_up), "n_lag_recent": len(lag_recent),
    "lag_source_error": lag_source_error,
    # Ứng viên LAG bị loại ở TẦNG TÍN HIỆU vì không đo được thanh khoản (ADV ≤ 0/thiếu/cũ).
    # `lag_liq_filter_error` != None ⇒ tầng này KHÔNG chạy được (fail-open) — phân biệt được
    # "không có mã nào bị loại" với "không lọc được"; executor vẫn fail-closed.
    "lag_liq_excluded": lag_liq_dropped,
    "n_lag_liq_excluded": len(lag_liq_dropped),
    "lag_liq_filter_error": lag_liq_error,
    # Ứng viên LAG bị loại vì GATE CỨNG 8L rating≥4 (RATING_FAIL, user policy 2026-07-27).
    # `lag_rating_filter_error` != None ⇒ gate KHÔNG chạy được (fail-open, KHÔNG có lưới executor).
    "lag_rating_excluded": lag_rating_dropped,
    "n_lag_rating_excluded": len(lag_rating_dropped),
    "lag_rating_filter_error": lag_rating_error,
    # Ứng viên LAG bị loại vì GATE QUẢN TRỊ: BANNED vĩnh viễn hoặc cờ forensic severity=exclude.
    # `lag_forensic_filter_error` != None ⇒ CHỈ phần cờ forensic không chạy được (fail-open);
    # danh sách BANNED là hằng số trong code nên LUÔN áp, không phụ thuộc file.
    "lag_forensic_excluded": lag_forensic_dropped,
    "n_lag_forensic_excluded": len(lag_forensic_dropped),
    "lag_forensic_filter_error": lag_forensic_error,
    # Dòng tín hiệu BAL bị loại vì SÀN THANH KHOẢN ADV3T < 2 tỷ/phiên (user chốt 2026-08-10).
    # `bal_liq_filter_error` != None ⇒ sàn KHÔNG áp được (fail-open); nền `liq >= 1e9` của
    # SIGNAL_V11 vẫn còn vì nó nằm trong chính SQL sinh tín hiệu.
    "adv_min_vnd": ADV_MIN_VND,
    "bal_liq_excluded": bal_liq_dropped,
    "n_bal_liq_excluded": len(bal_liq_dropped),
    "bal_liq_filter_error": bal_liq_error,
    "n_capit_basket": len(basket),
    # Sổ episode (§6b) — TRẠNG THÁI ĐANG GIỮ, khác hẳn capit_signal_today (điều kiện của ngày
    # chạy). Mọi gate báo cáo phải nhìn `capit_signal_today OR capit_episode_open`.
    **capit_ep,
    "n_park": len(_park_basket) if _park_basket is not None else 0,
    "park_rebal_date": _park_rebal_date,
    # Độ tươi CỦA FILE cờ due-diligence (KHÁC TTL 30d của từng cờ). True ⇒ gate anomaly có
    # thể THIẾU mã mới nổ cờ; hành vi loại trừ KHÔNG đổi (fail-open), chỉ để người/máy đọc
    # biết mà tự kiểm thêm trước khi duyệt plan.
    "anomaly_flags_stale": bool(anomaly_fresh["is_stale"]),
    "anomaly_flags_generated_at": anomaly_fresh["generated_at"],
    "anomaly_flags_stale_reason": anomaly_fresh["reason"] or None,
}
with open(os.path.join(WORKDIR, "data", "golive_v23_status.json"), "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

L = []
L.append(f"# V2.3 + DT5G — Daily Recommendations — {END}\n")
L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*\n")
if anomaly_fresh["is_stale"]:
    # Đặt NGAY ĐẦU báo cáo, không giấu trong log: đây là thứ người duyệt plan phải thấy
    # trước khi nhìn danh sách mua (audit §14 cron freshness, Winston_20260731_062642).
    L.append(f"> ⚠️ **`anomaly_flags.json` KHÔNG tươi hôm nay** (generated_at="
             f"`{anomaly_fresh['generated_at'] or 'thiếu'}` — {anomaly_fresh['reason']}). Gate "
             f"due-diligence vẫn chạy trên cờ CŨ ⇒ **CÓ THỂ THIẾU mã vừa nổ cờ bất thường**. "
             f"Tự kiểm tra tin tức/giá các mã trong danh sách mua trước khi duyệt; "
             f"kiểm tra `ops_health_check.sh`/`anomaly_scan.py` có chạy sáng nay không.\n")
L.append("## Regime, allocator & parking\n")
L.append(f"- **Market state (gated):** {state_today} = **{SNAME.get(state_today,'?')}**  (source: {prov.get('source','?')})")
L.append(f"- **Allocator w_LAG:** target **{w_tgt*100:.0f}%**" +
         (f" | current {w_cur*100:.0f}% ({alloc_note})" if w_cur is not None else " | current n/a") +
         (f" → **REBALANCE (band ±{ALLOC_BAND*100:.0f}pp breached)**" if band_breach else f" → trong band ±{ALLOC_BAND*100:.0f}pp, không rebalance"))
if state_today == 2:
    L.append(f"- ⚠️ **BEAR** — LAG book defunded (w_LAG=0: PEAD lỗ trong bear); BAL chỉ Fresh-Q ≤60d, mã rating≥4 half-size.")
if state_today == 1:
    L.append(f"- ⚠️ **CRISIS** — BAL chỉ Fresh-Q ≤30d, mã rating≥4 half-size; theo dõi CAPIT washout (cơ hội capitulation-buy).")
if etf_frac > 0:
    if _park_basket is not None:
        _top = " · ".join(f"{r.ticker} {r.weight*100:.0f}%" for r in _park_basket.head(8).itertuples())
        L.append(f"- **Parking (cả 2 book):** park **{etf_frac*100:.0f}%** cash nhàn rỗi vào "
                 f"**rổ custom30V** (`tav2_bq.custom30v_8l`, yieldcombo, cap-weight namecap≤10%, {len(_park_basket)} mã)"
                 + (" (NEUTRAL)" if state_today == 3 else "") + f"\n    - top: {_top} …")
    else:
        L.append(f"- **Parking (cả 2 book):** park **{etf_frac*100:.0f}%** cash nhàn rỗi vào rổ custom30V "
                 f"(`tav2_bq.custom30v_8l`) — lookup lỗi (xem log)")
else:
    L.append(f"- **Parking:** {etf_frac*100:.0f}% (state {state_today} → KHÔNG park, giữ cash phòng thủ)")
L.append(f"\n## BAL book ({(1-w_tgt)*100:.0f}% NAV target) — {len(bal)} picks\n")
if len(bal):
    L.append("| ticker | tier | 8L | ta | close_bq_stale (CẤM dùng làm ref_price — giá BQ trễ ≥1 phiên, ref_price phải lấy DNSE live) | sector | weight (of book) |")
    L.append("|---|---|---:|---:|---:|---:|---:|")
    for _, r in bal.iterrows():
        rt = rating8l.get(r["ticker"]); rt = int(rt) if pd.notna(rt) and rt is not None else "-"
        L.append(f"| {r['ticker']} | {r['play_type']} | {rt} | {float(r['ta']):.0f} | {float(r['Close']):.1f} | {int(r['sec']) if pd.notna(r['sec']) else '-'} | {r['weight']*100:.0f}% |")
else:
    L.append("_No new BAL entries today_ — không có signal đạt chuẩn trong các tier BAL "
             "(MEGA/MOMENTUM*/DVR/RE_BACKLOG) sau SV_TIGHT/overheat/AVOID_exbull. **Action: giữ vị thế hiện có "
             "(45d) + park cash theo target ở trên.** Đây là hành vi thận trọng bình thường, không phải lỗi.")
_latest = sig[sig["time"] == LATEST]
_exb = _latest[_latest["play_type"] == "AVOID_exbull"]
if len(_exb):
    L.append(f"\n_AVOID_exbull (momentum bị chặn trong EX-BULL):_ " + ", ".join(_exb["ticker"].head(12)))
_info = _latest[_latest["play_type"].isin(["COMPOUNDER_BUY", "S_PRO", "MOMENTUM_QUALITY", "MOMENTUM_S_N"])]
if len(_info):
    L.append(f"\n_Informational (ngoài tier BAL, V2.3 không trade):_ " +
             ", ".join(f"{r['ticker']}({r['play_type']})" for _, r in _info.head(12).iterrows()))
L.append(f"\n## LAG book ({w_tgt*100:.0f}% NAV target, always-on PEAD)\n")
L.append("Entry T+5 sau báo cáo quý mạnh (NP_R≥15, prior_n_good≥4, pa_HL3≥5), hold 25td, NO stop. "
         "LAG_HI (surprise>0.5) 10%/slot, LAG_LO 8%/slot.\n")
if lag_up:
    L.append("**Vào lệnh phiên tới:**")
    for it in lag_up:
        L.append(f"- **{it['ticker']}** ({it['tier']}) — entry {it['entry']} (release {it['release']}, NP_R {it['np_r']:.0f}%, pa_HL3 {it['pa_hl3']:.1f})")
else:
    L.append("_(không có entry PEAD đến hạn phiên tới)_")
if lag_recent:
    # KHÔNG ghi "đã vào lệnh" — sự kiện vendor backfill muộn (Release_Date quá khứ) rơi thẳng vào
    # nhóm này dù chưa từng có lệnh nào (audit L2 Spyros_20260712_131501); người/LLM đọc phải đối
    # chiếu vị thế thực, không mặc định vị thế đã tồn tại.
    L.append("\n_Cửa sổ entry đã qua trong các phiên gần nhất — đối chiếu vị thế thực, KHÔNG mặc định đã vào lệnh:_ "
             + ", ".join(f"{it['ticker']}({it['entry']})" for it in lag_recent))
if lag_liq_error:
    L.append(f"\n⚠️ Bộ lọc thanh khoản LAG KHÔNG chạy được ({lag_liq_error}) — danh sách trên CHƯA "
             "lọc mã ADV≤0; executor (`cap_lag_orders`) vẫn fail-closed nên không mã nào lọt thành "
             "lệnh, nhưng vốn có thể nằm im. Xem log.")
elif lag_liq_dropped:
    _lq = ", ".join(d["ticker"] for d in lag_liq_dropped[:12]) + (" …" if len(lag_liq_dropped) > 12 else "")
    L.append(f"\n_Đã loại ở tầng tín hiệu (ADV≤0/thiếu/cũ — không mua được; vốn dồn sang ứng viên "
             f"kế tiếp thay vì nằm im): {len(lag_liq_dropped)} mã — {_lq}_")
if lag_forensic_error:
    L.append(f"\n⚠️ Cờ forensic KHÔNG đọc được ({lag_forensic_error}) — danh sách trên CHƯA lọc mã "
             "bị cờ `exclude` (danh sách BANNED vĩnh viễn VẪN đã áp). Kiểm `data/forensic_flags.csv` "
             "trước khi duyệt plan.")
if lag_forensic_dropped:
    L.append(f"\n_Đã loại ở tầng tín hiệu (gate quản trị BANNED/forensic): "
             + ", ".join(f"{d['ticker']} ({d['kind']})" for d in lag_forensic_dropped) + "_")
if state_today == 2:
    L.append("\n⚠️ BEAR: allocator w_LAG=0 — KHÔNG cấp vốn entry LAG mới cho tới khi thoát BEAR.")
L.append(f"\n## CAPIT v2 monitor\n")
_brsrc = f"top-{CAPIT_TOPN} thanh khoản universe_pit" if CAPIT_BREADTH_SOURCE == "pit" else "ticker_prune"
L.append(f"- Oversold breadth (D_RSI<0.3, {_brsrc}): **{breadth_today*100:.1f}%** vs gate {WASHOUT_GATE*100:.0f}%")
if breadth_stale:
    L.append(f"- ⛔ **BREADTH CŨ — CAPIT FAIL-CLOSED**: chuỗi breadth mới tới "
             f"{br['time'].max().date() if len(br) else 'rỗng'} trong khi dữ liệu giá đã có tới "
             f"{breadth_src_max}. KHÔNG fire lệnh CAPIT mới trên dữ liệu cũ. Khắc phục: chạy "
             f"`mike/bin/build_universe_pit.py --date <ngày>` + `build_universe_pit_quality.py`.")
if capit_signal_today:
    L.append(f"- 🚨 **WASHOUT GATE FIRED** — state routing size = **{capit_size:.2f}** (grind={capit_grind}, dd52w={dd52_now:.1f}%, vn_cooling={vn_cool_now})")
    # Đòn bẩy margin (§6a) — LUÔN in 1 dòng khi có washout, kể cả khi TẮT: người duyệt plan
    # phải thấy trạng thái của nó, không phải suy ra từ việc thiếu dòng (bài học capit_fired).
    L.append(f"- ⚙️ Đòn bẩy margin CAPIT: **{'ĐANG ÁP' if capit_lever['active'] else 'TẮT'}** "
             f"(enabled={capit_lever['enabled']}, cổng {capit_lever['gate']} "
             f"{'ĐẠT' if capit_lever['gate_pass'] else 'chưa đạt'} @dd52={dd52_now:.1f}%) — "
             f"{capit_lever['reason']}")
    # NHÃN CŨ SAI, đã xoá 2026-07-31: dòng này từng ghi "Committed VND = size x free-cash mỗi
    # book" — công thức free-cash KHÔNG còn dùng từ khi user chốt booknav 2026-07-20. Không
    # plan nào thật sự dùng nó, nhưng để lại là một cách đọc thứ ba cho cùng một con số.
    L.append(f"- **Vốn triển khai = NAV_book_LAG × capit_size** = (active_nav × w_lag_target "
             f"{w_tgt:.0%}) × {capit_size:.2f} — công thức user chốt 2026-07-20. "
             f"Hold {CAPIT_HOLD}td, stop-exempt, slot-exempt.")
    if basket:
        L.append(f"- Basket quality-golden ({len(basket)} mã): " + ", ".join(basket))
        L.append(f"- 💰 **VND MỤC TIÊU/mã — DÙNG THẲNG SỐ NÀY, KHÔNG TỰ NHÂN LẠI** "
                 f"(= status `capit_slot_targets`). Cột `weight_pct`={capit_size/max(len(basket),1)*100:.2f} "
                 f"của dòng CAPIT trong CSV ĐÃ gồm capit_size — nhân nó lên tổng vốn CAPIT "
                 f"là ra capit_size² (lỗi thật 07-21, SpaceX thiếu 87,1tr):")
        for a in sorted(capit_targets):
            _t = capit_targets[a]
            if _t.get("capit_slot_target_vnd") is None:
                L.append(f"    · {a} — ⚠️ {_t.get('error')}")
                continue
            L.append(f"    · {a} — book LAG {_t['nav_book_lag_vnd']/1e6:,.0f}tr × "
                     f"{capit_size:.2f} = tổng {_t['capit_total_target_vnd']/1e6:,.0f}tr "
                     f"⇒ **{_t['capit_slot_target_vnd']/1e6:,.1f}tr/mã** × {_t['n_slots']} mã")
            if _t.get("lever_f"):
                L.append(f"      🔺 ĐÒN BẨY f={_t['lever_f']} (gói vay "
                         f"{_t['lever_loan_package_id']}) ⇒ **{_t['capit_slot_target_vnd_levered']/1e6:,.1f}tr/mã** "
                         f"(tổng {_t['capit_total_target_vnd_levered']/1e6:,.0f}tr, phần vượt vốn "
                         f"tự có là VAY). Trần %ADV KHÔNG nhân f.")
        L.append(f"  Lệnh thật = min(mục tiêu ở trên, trần %ADV bên dưới), rồi mới làm tròn lô.")
        L.append(f"- Trần %ADV/tên — TỔNG cả fleet ({ADV_X:.0%}·ADV20·{ADV_D:.0f} phiên, VND "
                 f"tuyệt đối; phần dư để CASH, không dồn sang tên khác): "
                 + ", ".join(f"{t} {capit_caps_total[t]/1e6:,.0f}tr" if t in capit_caps_total
                             else f"{t} ⚠KHÔNG CÓ ADV → sẽ bị CHẶN" for t in basket))
        L.append(f"  Thanh khoản một mã là nguồn lực THỊ TRƯỜNG dùng chung — trần TỔNG này "
                 f"được CHIA cho {len(capit_shares)} account live ({capit_share_mode}), "
                 f"executor mỗi account enforce cứng phần của mình:")
        for a in sorted(capit_shares):
            nav = capit_share_detail.get(a, {})
            L.append(f"    · {a} — {capit_shares[a]:.1%} "
                     f"(NAV {nav.get('nav') or 0:,.0f}đ, {nav.get('source')}): "
                     + ", ".join(f"{t} {capit_caps[a][t]/1e6:,.0f}tr"
                                 for t in basket if t in capit_caps.get(a, {})))
    else:
        L.append("- Basket: <3 mã quality đạt chuẩn — sleeve không kích hoạt.")
else:
    L.append("- Gate chưa kích hoạt — sleeve dormant.")
if dd_map:
    try:
        from trading_bot.due_diligence import DD_DISCLAIMER as _DDD
    except Exception:
        _DDD = ""
    L.append("\n## Due-diligence ứng cử viên (informational — KHÔNG loại mã, KHÔNG đổi weight)\n")
    # In ĐẦY ĐỦ mã có cờ; mã sạch gộp 1 dòng theo book (CSV vẫn giữ đủ DD cho MỌI dòng —
    # đó mới là artifact tra cứu, MD chỉ để người đọc nhanh).
    _clean = {}
    for (_t, _b), _s in sorted(dd_map.items()):
        if not _s:
            continue
        _ls = str(_s).splitlines()
        if any(("⚠" in x or "🔴" in x) for x in _ls):
            L.append(f"- {_ls[0]}")
            for _x in _ls[1:]:
                L.append(f"  {_x.strip()}")
        else:
            _clean.setdefault(_b, []).append(_t)
    for _b in sorted(_clean):
        L.append(f"- ✅ {_b} không cờ ({len(_clean[_b])}): {', '.join(sorted(_clean[_b]))}")
    if _DDD:
        L.append(f"\n_{_DDD}_")
L.append(f"\n## Notes\n- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = {(1-w_tgt)*100:.0f}% NAV, LAG book = {w_tgt*100:.0f}% NAV theo allocator).")
L.append(f"- BAL: max {MAX_POS} pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.")
L.append(f"- **Sàn thanh khoản CỨNG cả 2 book hệ thống: ADV3T ≥ {ADV_MIN_VND/1e9:.0f} tỷ/phiên** "
         f"(user chốt 2026-08-10 — *hiệu quả vốn*, KHÔNG phải edge: backtest đo phần gia tăng là "
         f"−0,26pp CAGR / PBO 0,916). Phiên này loại {len(bal_liq_dropped)} dòng BAL + "
         f"{sum(1 for d in lag_liq_dropped if 'ADV3T' in d.get('reason', ''))} ứng viên LAG vì dưới sàn.")
L.append(f"- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).")
L.append(f"- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.")
L.append(f"- CSV: `out/golive_v23_recommendations_{END}.csv` | status: `data/golive_v23_status.json`")
md_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.md")
open(md_path, "w", encoding="utf-8").write("\n".join(L))

print(f"\n  state={state_today}({SNAME.get(state_today,'?')})  w_LAG tgt={w_tgt*100:.0f}%" +
      (f" cur={w_cur*100:.0f}%" if w_cur is not None else "") +
      f"  parking={etf_frac*100:.0f}%  breadth={breadth_today*100:.1f}%")
print(f"  BAL picks: {len(bal)} | LAG upcoming: {len(lag_up)} | CAPIT fired: {capit_signal_today}")
print(f"  -> {md_path}")
print(f"  -> {csv_path}")
print("DONE.")
