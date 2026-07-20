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
ETF_PARK = {3: 0.7}                                  # both books in V2.3
STATE_LAG_WEIGHT = {1: 0.50, 2: 0.00, 3: 0.65, 4: 0.65, 5: 0.65}
EDGE_THR = 4.0   # %: LAG trailing-12M edge-health threshold (pinned R3 = argv "edge")

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
WASHOUT_GATE = 0.30; CAPIT_HOLD = 60
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
    """
    p = os.path.join(WORKDIR, "data", "anomaly_flags.json")
    try:
        flags = json.load(open(p, encoding="utf-8"))
        # chuẩn hoá asof (date / Timestamp / str đều nhận) — sai kiểu ở caller mà rơi vào
        # except sẽ TẮT ÂM THẦM cả cái gate an toàn này, nên không để nó có cửa xảy ra.
        d = pd.Timestamp(asof).date()
        # CỬA SỔ HAI ĐẦU: cutoff <= last_alert <= asof. Chặn trên là chống look-ahead — nếu
        # chỉ so >= cutoff thì chạy lại cho một ngày quá khứ sẽ áp cả cờ của TƯƠNG LAI
        # (vd rerun 2025-12: cờ PNJ 07/2026 vẫn "active"). Live thì asof≈hôm nay nên vô hại,
        # nhưng để vậy là mời gọi kết quả backtest sai lệch về sau.
        lo, hi = str(d - timedelta(days=ANOMALY_TTL_DAYS)), str(d)
        return {t for t, f in flags.items() if lo <= str(f.get("last_alert", "")) <= hi}
    except Exception as ex:
        print(f"  WARNING: due-diligence flags không đọc được ({ex}) — CAPIT chạy KHÔNG có gate")
        return set()


def capit_adv_caps(basket, asof):
    """Trần VND TUYỆT ĐỐI cho mỗi tên trong rổ CAPIT — chống market-impact khi sleeve lớn.

        cap_vnd_i = ADV_X * ADV20_i * ADV_D

    ADV20_i = median giá trị giao dịch (VND) của 20 phiên NGAY TRƯỚC `asof` (ngày washout
    KHÔNG tính vào). Ngày washout theo định nghĩa là ngày volume spike, lấy nó làm mốc sẽ
    thổi phồng thanh khoản khả dụng (đo được: median ADV20-sau / ADV-ngày-vào = 0,54;
    p10 = 0,32 — mike/agents/Taylor/exp_capitexit/RESULT.md §3a). Cửa sổ TRƯỚC cũng là cửa
    sổ duy nhất NHÂN QUẢ (live không biết ADV tương lai).

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
  FROM tav2_bq.ticker_prune p
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

    BẤT BIẾN (điều kiện an toàn thật sự, đúng ở MỌI nhánh kể cả fallback):
        Σ_account share = 1.0  ⇒  Σ_account cap = X·ADV20·D
    Thiếu NAV KHÔNG BAO GIỜ được phép nới tổng trần — nên fallback là chia đều, không phải
    "cho mỗi account full trần" (chính là bug mà thay đổi này sửa).
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

# ── 1. signals with state5 from the gated DT5G series ──
SIG = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", "tav2_bq." + DT_TABLE + " AS s")
sig = bq(SIG.format(start=START, end=END)); sig["time"] = pd.to_datetime(sig["time"])
LATEST = sig["time"].max()
state_today = int(sig.loc[sig["time"] == LATEST, "state5"].dropna().iloc[0]) if (sig["time"] == LATEST).any() else int(prov.get("state", 3))
print(f"  latest signal date: {LATEST.date()} | {len(sig):,} signal rows in window")

# ── 2. D1 RE_BACKLOG (gated state) + SV_TIGHT + overheat (same layering as pt_v22_dt5g) ──
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f),
tkd AS (
  -- ICB-8633 panel: canonical ticker + ticker_1m fallback for the freshest session not yet in `ticker`
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  UNION ALL
  SELECT t.ticker,t.time,t.NP_P0,t.NP_P4 FROM tav2_bq.ticker_1m AS t
  WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
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
br = bq(f"""SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
FROM tav2_bq.ticker_prune p
WHERE p.time BETWEEN DATE '{START_BR}' AND DATE '{END}' AND p.Close_T1>0
GROUP BY p.time ORDER BY p.time""")
br["time"] = pd.to_datetime(br["time"])
breadth_today = float(br["oversold"].iloc[-1]) if len(br) else np.nan
capit_fired = bool(pd.notna(breadth_today) and breadth_today >= WASHOUT_GATE)
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
if capit_fired:
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
        e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pbz
FROM tav2_bq.ticker_prune p
WHERE p.time = DATE '{bd.date()}' AND p.ROE_Min5Y>=0.12 AND p.ROIC5Y>=0.10 AND p.FSCORE>=6
  AND COALESCE(p.Price,p.Close)*p.Volume/1e9 >= 2""")
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
recs = []
for _, r in bal.iterrows():
    recs.append({"book": "BAL", "ticker": r["ticker"], "play_type": r["play_type"],
                 "ta": round(float(r["ta"]), 0), "close_bq_stale_DO_NOT_USE_AS_REFPRICE": round(float(r["Close"]), 1),
                 "sector": int(r["sec"]) if pd.notna(r["sec"]) else None,
                 "weight_pct": r["weight"]*100, "status": "HALF_SIZE" if (r["weak"] and half_in_state) else "FULL"})
for it in lag_up:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "status": f"UPCOMING {it['entry']}"})
for it in lag_recent:
    recs.append({"book": "LAG", "ticker": it["ticker"], "play_type": it["tier"],
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(it["ticker"]),
                 "weight_pct": LAG_TW[it["tier"]]*100, "status": f"WINDOW_PASSED {it['entry']}"})
for tk in basket:
    recs.append({"book": "CAPIT", "ticker": tk, "play_type": "CAPIT_GOLDEN",
                 "ta": None, "close_bq_stale_DO_NOT_USE_AS_REFPRICE": None, "sector": sec_map.get(tk),
                 "weight_pct": round(capit_size / max(len(basket), 1) * 100, 2), "status": "WASHOUT",
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
                     "status": "PARK_ADVISORY"})
rec_df = pd.DataFrame(recs, columns=["book","ticker","play_type","ta","close_bq_stale_DO_NOT_USE_AS_REFPRICE","sector","weight_pct","status","capit_cap_total_vnd"])
csv_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.csv")
rec_df.to_csv(csv_path, index=False)

status = {
    "date": END, "signal_date": str(LATEST.date()), "state": state_today,
    "state_name": SNAME.get(state_today, "?"), "source": prov.get("source"),
    "w_lag_target": w_tgt, "w_lag_current": (round(w_cur, 4) if w_cur is not None else None),
    "alloc_band": ALLOC_BAND, "band_breach": bool(band_breach), "alloc_note": alloc_note,
    "etf_park_frac": etf_frac,
    "breadth_oversold": (round(breadth_today, 4) if pd.notna(breadth_today) else None),
    "washout_gate": WASHOUT_GATE, "capit_fired": capit_fired,
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
    "dd52w": round(dd52_now, 1), "vn_cooling": vn_cool_now,
    "n_bal": int(len(bal)), "n_lag_upcoming": len(lag_up), "n_lag_recent": len(lag_recent),
    "lag_source_error": lag_source_error,
    "n_capit_basket": len(basket),
    "n_park": len(_park_basket) if _park_basket is not None else 0,
    "park_rebal_date": _park_rebal_date,
}
with open(os.path.join(WORKDIR, "data", "golive_v23_status.json"), "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

L = []
L.append(f"# V2.3 + DT5G — Daily Recommendations — {END}\n")
L.append(f"*Generated {datetime.now():%Y-%m-%d %H:%M}. System: V2.3 = BAL | LAG (static, always-on) + allocator + parking + CAPIT v2, gated DT5G state (fail-safe DT4).*\n")
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
if state_today == 2:
    L.append("\n⚠️ BEAR: allocator w_LAG=0 — KHÔNG cấp vốn entry LAG mới cho tới khi thoát BEAR.")
L.append(f"\n## CAPIT v2 monitor\n")
L.append(f"- Oversold breadth (D_RSI<0.3, ticker_prune): **{breadth_today*100:.1f}%** vs gate {WASHOUT_GATE*100:.0f}%")
if capit_fired:
    L.append(f"- 🚨 **WASHOUT GATE FIRED** — state routing size = **{capit_size:.2f}** (grind={capit_grind}, dd52w={dd52_now:.1f}%, vn_cooling={vn_cool_now})")
    L.append(f"- Committed VND = size × free cash mỗi book, hold {CAPIT_HOLD}td, stop-exempt, slot-exempt.")
    if basket:
        L.append(f"- Basket quality-golden ({len(basket)} mã): " + ", ".join(basket))
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
L.append(f"\n## Notes\n- Sizing: %/slot tính trên VỐN CỦA BOOK (BAL book = {(1-w_tgt)*100:.0f}% NAV, LAG book = {w_tgt*100:.0f}% NAV theo allocator).")
L.append(f"- BAL: max {MAX_POS} pos, hold 45d, stop -20%, Fin/RE (sector 8) cap 4 (RE_BACKLOG exempt); mã 8L rating≥4 half-size CHỈ trong BEAR/CRISIS.")
L.append(f"- LAG: KHÔNG ensemble switch (always-on), KHÔNG stop — quản trị bằng allocator (BEAR=0).")
L.append(f"- State là chuỗi gated fail-safe; nếu macro feed lỗi, source = 'DT4_only'.")
L.append(f"- CSV: `out/golive_v23_recommendations_{END}.csv` | status: `data/golive_v23_status.json`")
md_path = os.path.join(OUTDIR, f"golive_v23_recommendations_{END}.md")
open(md_path, "w", encoding="utf-8").write("\n".join(L))

print(f"\n  state={state_today}({SNAME.get(state_today,'?')})  w_LAG tgt={w_tgt*100:.0f}%" +
      (f" cur={w_cur*100:.0f}%" if w_cur is not None else "") +
      f"  parking={etf_frac*100:.0f}%  breadth={breadth_today*100:.1f}%")
print(f"  BAL picks: {len(bal)} | LAG upcoming: {len(lag_up)} | CAPIT fired: {capit_fired}")
print(f"  -> {md_path}")
print(f"  -> {csv_path}")
print("DONE.")
