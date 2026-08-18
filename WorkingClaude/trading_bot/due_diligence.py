# -*- coding: utf-8 -*-
"""Due-diligence tổng hợp cho MỌI ứng cử viên mua (user mandate 2026-07-21).

BỐI CẢNH: chuỗi rà tay LAG 07-24 (IVS/TMG/TRC, job Taylor_20260721_130404/_133858) cho thấy
quy trình tự động KHÔNG bắt được: TMG thanh khoản = 0 (ngoài ticker_prune), IVS ADV mỏng +
surprise phồng cơ học do nền lỗ quý trước. Các cơ chế due-diligence sẵn có chỉ chạy khi có cờ
đặc biệt (forensic/legal list, >7% NAV, first-time-buy, DCF RICH-robust, anomaly Tier-H) hoặc
chỉ soi 1 trục (DCF/sector-lens). Mandate: MỘT bước tổng hợp chạy MẶC ĐỊNH cho MỌI candidate,
ở CẢ production lẫn paper.

⚠️ THUẦN THÔNG TIN — giống format_dcf_check(): KHÔNG chặn lệnh, KHÔNG đổi hành vi mua/bán,
KHÔNG thêm hard-gate nào. 4 hard-gate cũ (forensic/legal, >7% NAV, first-time-buy, DCF
RICH-robust) + anomaly gate của CAPIT giữ nguyên, không đụng tới.

Nguồn dữ liệu (đã tra mike/kb/data_registry.md — coding_guidelines §9):
  - `data/bq_cache/ticker/<year>.parquet` (THƯ MỤC chunked, KHÔNG phải file monolith đã chết)
    → thanh khoản + FA point-in-time (NP_P0..P4, ROE5Y, ROE_Min3Y, FSCORE, Debt_Eq_P0, PE).
    Cache sync 23:45 ICT ⇒ trễ tới 1 phiên. CHẤP NHẬN ĐƯỢC ở đây: mọi số dùng là trung vị
    3 tháng / chỉ số quý, 1 phiên lệch không đổi kết luận. TUYỆT ĐỐI không dùng cho ref_price
    (bright-line rule §6: giá trong ngày phải lấy DNSE).
  - `tav2_mike.universe_pit_q` (BQ live) → cờ "có nằm trong universe không" + `quality_flag`
    (Q-C, user chốt 2026-07-22). Cutover P1 §4.2 của `ticker_prune_replacement_plan.md`.
    Rollback = đặt `UNIVERSE_SOURCE = "prune"` (nhánh cũ `bq_cache/ticker_prune/` giữ nguyên).
    Đọc lỗi/thiếu ngày → nhãn "n/a", KHÔNG tự fallback về `ticker_prune` (§4.3).
  - `data/anomaly_flags.json` qua anomaly_gate (echo lại, KHÔNG scan lại).
  - DCF/sector-lens qua trading_bot.strategies.format_dcf_check (gọi lại, KHÔNG viết lại).

Fail-safe tuyệt đối: mọi lỗi → trả dòng "DD: n/a (<lý do>)", KHÔNG raise. Report gọi hàm này
không bao giờ được hỏng vì nó.
"""

import datetime as dt
import glob
import json
import logging
import os
from zoneinfo import ZoneInfo

from .config import WORKDIR, DATA_DIR

_log = logging.getLogger(__name__)

# Ngưỡng CẢNH BÁO hiển thị TRONG FILE NÀY (file này vẫn thuần thông tin, không chặn lệnh).
# ADV_THIN neo theo sàn thanh khoản 2 tỷ/phiên mà rổ CAPIT trong golive_recommend_v23.py đã dùng
# (`Price*Volume/1e9 >= 2`) — giữ 1 con số chung cho cả fleet thay vì đẻ ngưỡng mới.
#
# ⚠️ TỪ 2026-08-10 CÙNG CON SỐ NÀY LÀ **GATE CỨNG** Ở TẦNG CHỌN MÃ cho 2 book hệ thống
# (user chốt, job Taylor_20260810_081207): `lag_liquidity_filter.ADV_MIN_VND` loại thẳng ứng
# viên LAG và dòng tín hiệu BAL có ADV3T < 2 tỷ TRƯỚC khi vào plan. Ở ĐÂY vẫn là CẢNH BÁO,
# và điều đó KHÔNG phải code chết — mọi lệnh MUA trong plan đều chạy qua đây
# (`send_plan_report.sh:611`), gồm cả những đường KHÔNG đi qua 2 gate kia:
#   · sleeve discretionary/fear-buy (`discretionary_accumulation.py` — không import file này,
#     cũng không qua lag/bal filter) — đây là ca mà cảnh báo mỏng còn nguyên giá trị;
#   · vị thế legacy/exclude và mọi book khác (CAPIT/PARK) có gate thanh khoản RIÊNG.
# Với mã book LAG/BAL thì đúng là cảnh báo này gần như không còn cơ hội in ra — đó là hệ quả
# MONG MUỐN của gate, không phải dấu hiệu ngưỡng sai. Đổi 1 trong 2 con số ⇒ phải đổi con kia.
ADV_THIN_VND = 2e9
ADV_DEAD_VND = 1e8          # gần như không có giao dịch thật
ORDER_ADV_WARN = 0.10       # lệnh > 10% ADV → cảnh báo impact
ORDER_ADV_HARD = 0.25       # > 25% ADV → cảnh báo mạnh

_CACHE = {}                 # (kind, year) -> DataFrame, tránh đọc lại parquet nhiều lần/1 report


def _read_year(kind, year, columns=None):
    """Đọc 1 chunk năm từ bq_cache. kind ∈ {'ticker','ticker_prune'}."""
    key = (kind, year, tuple(columns) if columns else None)
    if key in _CACHE:
        return _CACHE[key]
    import pandas as pd
    path = os.path.join(DATA_DIR, "bq_cache", kind, f"{year}.parquet")
    if not os.path.exists(path):
        # cuối năm/đầu năm: chunk của năm as_of có thể chưa tồn tại → lùi 1 năm
        cands = sorted(glob.glob(os.path.join(DATA_DIR, "bq_cache", kind, "*.parquet")))
        if not cands:
            raise FileNotFoundError(f"bq_cache/{kind} rỗng")
        path = cands[-1]
    df = pd.read_parquet(path, columns=columns)
    _CACHE[key] = df
    return df


_TICKER_COLS = ["ticker", "time", "Close", "Price", "Volume", "Volume_3M_P50",
                "NP_P0", "NP_P1", "NP_P2", "NP_P3", "NP_P4",
                "ROE5Y", "ROE_Min3Y", "FSCORE", "Debt_Eq_P0", "PE"]


def _latest_row(ticker, asof):
    """Dòng ticker mới nhất <= asof (point-in-time, không look-ahead). None nếu không có."""
    import pandas as pd
    year = int(str(asof)[:4])
    df = _read_year("ticker", year, _TICKER_COLS)
    d = df[(df["ticker"] == ticker) & (pd.to_datetime(df["time"]) <= pd.Timestamp(asof))]
    if d.empty:
        # ticker mới niêm yết đầu năm / asof đầu năm → thử chunk năm trước
        try:
            df2 = _read_year("ticker", year - 1, _TICKER_COLS)
            d = df2[(df2["ticker"] == ticker) &
                    (pd.to_datetime(df2["time"]) <= pd.Timestamp(asof))]
        except Exception:
            pass
    if d.empty:
        return None
    return d.sort_values("time").iloc[-1]


def _in_prune(ticker, asof):
    """Nhánh CŨ (rollback): membership theo `ticker_prune` từ bq_cache."""
    import pandas as pd
    year = int(str(asof)[:4])
    df = _read_year("ticker_prune", year, ["ticker", "time"])
    d = df[df["ticker"] == ticker]
    if d.empty:
        return False, None, None
    last = pd.to_datetime(d["time"]).max()
    # còn "sống" trong prune nếu xuất hiện trong vòng 30 ngày trước asof
    return bool((pd.Timestamp(asof) - last).days <= 30), str(last)[:10], None


def _in_universe_pit(ticker, asof):
    """Nhánh MỚI (P1, §4.2): membership + cờ chất lượng từ `tav2_mike.universe_pit_q`.

    Trả (in_universe, last_date, quality_flag). in_universe=None nghĩa là KHÔNG BIẾT (bảng
    thiếu ngày / lỗi đọc) — **tuyệt đối không tự fallback về `ticker_prune`** (§4.3): fallback
    im lặng tái nhập đúng cái drift ta đang bỏ chạy. Nhãn sẽ hiện "n/a", không hiện "NGOÀI".
    """
    from google.cloud import bigquery
    client = _CACHE.get("_bqclient")
    if client is None:
        client = bigquery.Client(project="lithe-record-440915-m9", location="asia-southeast1")
        _CACHE["_bqclient"] = client
    # `latest` = trạng thái mới nhất <= asof; `last_in` = lần cuối THỰC SỰ ở trong universe
    # (hai thứ khác nhau khi mã vừa bị loại — nhãn cần nói đúng cái sau).
    sql = """
SELECT ARRAY_AGG(STRUCT(in_universe, quality_flag) ORDER BY time DESC LIMIT 1)[OFFSET(0)] AS latest,
       MAX(IF(in_universe, time, NULL)) AS last_in
FROM `lithe-record-440915-m9.tav2_mike.universe_pit_q`
WHERE ticker = @tk AND time <= @asof AND time >= DATE_SUB(@asof, INTERVAL 30 DAY)"""
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("tk", "STRING", ticker),
        bigquery.ScalarQueryParameter("asof", "DATE", str(asof)[:10])])
    rows = list(client.query(sql, job_config=cfg, location="asia-southeast1").result())
    if not rows or rows[0]["latest"] is None:
        # không có dòng nào trong 30 ngày: mã chưa từng có trong `ticker`, HOẶC bảng chưa
        # build tới ngày này. Hai thứ khác nhau — phân biệt bằng chính ngày mới nhất của bảng.
        mx = list(client.query(
            "SELECT MAX(time) AS d FROM `lithe-record-440915-m9.tav2_mike.universe_pit`",
            location="asia-southeast1").result())[0]["d"]
        if mx is None or str(mx) < str(asof)[:10]:
            raise RuntimeError(f"universe_pit chi co toi {mx} < asof {str(asof)[:10]}")
        return False, None, None
    r = rows[0]
    last_in = str(r["last_in"])[:10] if r["last_in"] is not None else None
    return bool(r["latest"]["in_universe"]), last_in, r["latest"]["quality_flag"]


# Nguồn universe cho nhãn DD. Hằng số module-level (KHÔNG env var — env thừa hưởng qua process
# là đúng cơ chế đã gây sự cố C1 07-12, coding_guidelines §11). Rollback = đổi về "prune".
UNIVERSE_SOURCE = "pit"


def _in_universe(ticker, asof):
    """(in_universe|None, last_date, quality_flag) — None = không kết luận được, KHÔNG fallback."""
    try:
        if UNIVERSE_SOURCE == "prune":
            return _in_prune(ticker, asof)
        return _in_universe_pit(ticker, asof)
    except Exception as exc:
        _log.warning("universe (%s) doc loi (%s): %s", UNIVERSE_SOURCE, ticker, exc)
        return None, None, None


def adv_vnd(ticker, asof):
    """ADV notional (VND/phiên) theo ĐÚNG công thức backtest LAG dùng:
    Volume_3M_P50 × COALESCE(Price, Close) (`pt_v23_audit_2014.py` LAG_ADV_BASIS="price").

    Trả (adv, data_date, err): adv=None khi không tính được, err = lý do (chuỗi) để caller
    tự quyết fail-closed. KHÔNG raise — nhưng KHÁC run_due_diligence ở chỗ lỗi được trả về
    tường minh thay vì nuốt thành text, vì caller (trading_bot.plan.cap_lag_orders) là một
    hard-gate chặn lệnh thật và phải phân biệt được "ADV mỏng" với "không đọc được dữ liệu".

    CƠ SỞ GIÁ = `Price` (THÔ), sửa 2026-08-02 (job Taylor_20260802_163657) — trước đó dùng
    `Close`. `Volume_3M_P50` là SỐ LƯỢNG CP THÔ: đo được `Trading_Value == Volume × Price` khớp
    100% số dòng, `Volume × Close` thì không ⇒ ADV tiền đồng đúng phải nhân giá THÔ. `Close` đã
    điều chỉnh hồi tố nên vừa SAI ĐỘ LỚN (~−7,4% median, trần live chặt hơn thực tế) vừa mang
    LOOK-AHEAD khi hệ thống replay lịch sử (hệ số Close/Price phụ thuộc sự kiện quyền SAU ngày t).
    Bất biến parity live == mô phỏng được GIỮ NGUYÊN: engine đổi cùng lúc (`LAG_ADV_BASIS`).
    """
    import pandas as pd
    try:
        row = _latest_row(ticker, asof)
    except Exception as exc:
        return None, None, f"không đọc được bq_cache/ticker: {str(exc)[:120]}"
    if row is None:
        return None, None, "không có dòng nào trong bq_cache/ticker"
    data_date = str(row.get("time"))[:10]
    v50, px = row.get("Volume_3M_P50"), row.get("Price")
    if pd.isna(px):                       # COALESCE(Price, Close) — đúng engine
        px = row.get("Close")
    if pd.isna(v50) or pd.isna(px):
        return None, data_date, "thiếu Volume_3M_P50 hoặc Price/Close"
    return float(v50) * float(px), data_date, None


def _anomaly_note(ticker, asof):
    """Echo cờ anomaly_scan hiện có. KHÔNG scan lại, KHÔNG đổi gate CAPIT."""
    try:
        path = os.path.join(DATA_DIR, "anomaly_flags.json")
        with open(path, encoding="utf-8") as f:
            flags = json.load(f)
        rec = flags.get(ticker)
        if not rec:
            return ""
        return (f"⚠ cờ bất thường {rec.get('tier', '?')} [{rec.get('reasons', '?')}] "
                f"ngày {rec.get('last_alert', '?')}")
    except Exception as exc:
        _log.warning("anomaly flags đọc lỗi (%s): %s", ticker, exc)
        return ""


# =======================================================================================
# 2 trường THÔNG TIN mới (2026-08-17, job Taylor_20260817_041248) — cổ tức sắp GDKHQ +
# nội bộ bán ròng. **CHỈ nằm trong dict trả về** (`as_dict=True` / `parts`), CỐ Ý KHÔNG in ra
# dòng text của run_due_diligence: đưa vào text = đổi ngay nội dung mọi report đang chạy, mà
# bước đó phải qua quant-skeptic trước (dispatch nói rõ). Không sinh cờ đỏ, không chặn gì.
#
# Vì sao 2 trường này là CẢNH BÁO CHI PHÍ / RỦI RO ĐUÔI TRÁI chứ không phải factor:
#   · cổ tức: BHAR_20 ≈ −0,50pp cho mỗi 1pp tỉ suất gộp (t=−5,60) — nhưng hiệu ứng TẬP TRUNG ở
#     nhóm ADV thấp; nửa ADV cao (đúng rổ thật sau cổng ADV3T ≥ 2 tỷ) chỉ −0,52% với p=0,124,
#     KHÔNG có ý nghĩa. ⇒ dùng làm cảnh báo chi phí, TUYỆT ĐỐI không làm gate.
#     Nguồn: Sprint 2 corp-action (job Taylor_20260815_121850/_125247).
#   · insider: P(fwd60 < −20%) = 19,7% khi có cờ vs 11,3% nền (lift 1,745×, z=12,90), ổn định
#     IS↔OOS — nhưng ~80% mã bị bắt KHÔNG sập ⇒ WATCH, không exclude.
#     Nguồn: research/insider_transaction_scoping_20260729.md §3.4.
CORP_ACTION_LOOKAHEAD_DAYS = 25     # cửa sổ "sắp GDKHQ" — phủ horizon BHAR_20 (20 phiên)
CORP_ACTION_STALE_DAYS_MAX = 4      # feed nạp ~22:2x ICT mỗi ngày; 4 ngày phủ được cuối tuần + 1 lễ
EXDATE_COST_PP_PER_PP_YIELD = 0.50  # hệ số hồi quy BHAR_20 ~ tỉ suất gộp (pin Sprint 2)

# Định nghĩa cờ insider PIN ở `mike/agents/Taylor/insider_flags.py` (§3.4) — là AND của HAI vế,
# không chỉ vế khối lượng. Prompt dispatch chỉ nhắc vế ≥1%; lift 1,745× đo trên CẢ HAI vế nên
# bỏ vế `nsell > nbuy` là báo một con số không thuộc về định nghĩa đang chạy.
INSIDER_WINDOW_DAYS = 90
INSIDER_SELL_PCT_OSH_MIN = 0.01
INSIDER_STALE_SESSIONS_MAX = 10     # bảng cũ hơn ~10 phiên ⇒ coi như nguồn chết, KHÔNG kết luận

_EXDATE_NOTE = ("COST-INFO: ước phí post-ex trung bình ~0.50pp/1pp yield "
                "(ADV-thấp; không có ý nghĩa ở ADV-cao)")
_INSIDER_NOTE = ("RISK-INFO: bán ròng nội bộ ≥1% CP lưu hành — P(fwd60<-20%) lift ~1.75x "
                 "(IS/OOS ổn định, scoping 2026-07-29)")

# ---------------------------------------------------------------------------------------
# Trường THÔNG TIN thứ 3 (2026-08-18, job Taylor_20260818_032101) — "sàn giá cổ tức".
# **DISPLAY_ONLY**: không sizing, không gate, không cờ đỏ, không filter mã nào.
#
# Nguồn: research `dividend_yield_floor_20260818` (FINDINGS.md, CONFIRMED chân H2 / REFUTED
# chân H1). Đọc nguyên văn trước khi diễn giải con số này:
#   · CÁI ĐO ĐƯỢC: mã trả cổ tức tiền mặt ổn định 3 năm liên tiếp, khi tỉ suất trailing chạm
#     lãi suất tiền gửi (prox ∈ [0,97; 1,03]) → MDD 60 phiên tiếp theo NHẸ HƠN 3,46pp so với
#     nhóm chứng ghép cặp cùng ICB + cùng rvol (t=5,14, n=412 episode/188 mã;
#     IS +4,53pp t=4,11 · OOS +2,93pp t=3,48).
#   · CÁI **KHÔNG** ĐO ĐƯỢC: lợi suất vượt trội. BHAR_60 = +0,64pp, t=0,67, **median âm**
#     (−0,97pp). ⇒ đây là ĐỆM ĐUÔI TRÁI, TUYỆT ĐỐI không phải tín hiệu mua.
#   · Mức tin cậy research tự khai: TRUNG BÌNH (placebo ghép cặp không bằng 0; phần dư sau khi
#     trừ placebo không đạt t≥2,0). Đủ để HIỂN THỊ, chưa đủ để đổi cách làm.
#   · Ngân hàng: n=3 episode, không có ý nghĩa thống kê, và cơ chế cổ tức ngân hàng khác hẳn
#     (phụ thuộc room vốn/NHNN duyệt, nhiều năm chia bằng cổ phiếu) ⇒ loại khỏi diễn giải.
#
# Định nghĩa BÁM ĐÚNG research (`research/dividend_yield_floor_20260818/build.py`), không tự
# chế lại: cửa sổ 365 ngày lịch (không phải "năm dương lịch"), dedup DIV theo
# (ticker, exright_date, dividend_year, dividend_stage_vi) lấy `public_date` mới nhất rồi SUM
# các tranche còn lại (registry Bẫy 3: gộp theo (mã, ex-date) trần sẽ nuốt mất 1 đợt chi trả).
YIELD_FLOOR_NEAR_LO = 0.97          # PREREG §6 — dải "chạm sàn" [0,97; 1,03]
YIELD_FLOOR_NEAR_HI = 1.03
YIELD_FLOOR_ICB_BANKING = 8355      # ICB subsector 4 chữ số (DEVIATIONS.md D3), KHÔNG phải "NH"
YIELD_FLOOR_DEPOSIT_FALLBACK_PCT = 5.5   # chỉ dùng khi deposit_rate_vn.py không import được

_YIELD_FLOOR_NOTE = ("DOWNSIDE-INFO (DISPLAY_ONLY): chạm sàn cổ tức ⇒ MDD60 nhẹ hơn ~3,46pp vs "
                     "nhóm chứng ghép cặp (t=5,14) — KHÔNG có alpha lợi suất (BHAR60 t=0,67, "
                     "median âm). Không phải tín hiệu mua.")
_YIELD_FLOOR_BANKING_NOTE = ("Ngân hàng loại khỏi diễn giải: n=3 episode, không có ý nghĩa; "
                             "cơ chế cổ tức ngân hàng khác (room vốn/NHNN duyệt).")

# Đếm DIV theo 3 cửa sổ 365 ngày liên tiếp lùi từ asof — n0/n1/n2 và div0 giữ NGUYÊN ngữ nghĩa
# của `build.py` (`stable3 = n0>=1 ∧ n1>=1 ∧ n2>=1`, `div0` = tổng VND/cp cửa sổ gần nhất).
_YIELD_FLOOR_SQL = """
WITH dd AS (
  SELECT c.exright_date AS ex, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` AS c
  WHERE c.event_code = "DIV" AND c.event_status = "executed"
    AND c.ticker = "{ticker}"
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
    AND c.exright_date <= DATE "{asof}"
    AND c.exright_date > DATE_SUB(DATE "{asof}", INTERVAL 1095 DAY)
)
SELECT
  IFNULL(SUM(IF(ex > DATE_SUB(DATE "{asof}", INTERVAL 365 DAY), value_per_share, 0)), 0) AS div0,
  COUNTIF(ex > DATE_SUB(DATE "{asof}", INTERVAL 365 DAY)) AS n0,
  COUNTIF(ex <= DATE_SUB(DATE "{asof}", INTERVAL 365 DAY)
      AND ex >  DATE_SUB(DATE "{asof}", INTERVAL 730 DAY)) AS n1,
  COUNTIF(ex <= DATE_SUB(DATE "{asof}", INTERVAL 730 DAY)
      AND ex >  DATE_SUB(DATE "{asof}", INTERVAL 1095 DAY)) AS n2
FROM dd WHERE rn = 1
"""


def _icb_code(ticker, asof):
    """ICB subsector 4 chữ số tại phiên gần nhất ≤ asof — None nếu không đọc được.

    Đọc RIÊNG khỏi `_latest_row`: thêm cột vào `_TICKER_COLS` sẽ đổi khoá cache và lượng đọc
    của MỌI caller sẵn có (§3 surgical). Cache theo (ticker, asof) như các trường khác."""
    key = ("_icb", ticker, str(asof)[:10])
    if key in _CACHE:
        return _CACHE[key]
    import pandas as pd
    out = None
    try:
        year = int(str(asof)[:4])
        cols = ["ticker", "time", "ICB_Code"]
        d = None
        for y in (year, year - 1):
            try:
                df = _read_year("ticker", y, cols)
            except Exception:
                continue
            d = df[(df["ticker"] == ticker) &
                   (pd.to_datetime(df["time"]) <= pd.Timestamp(str(asof)[:10]))]
            if not d.empty:
                break
        if d is not None and not d.empty:
            v = d.sort_values("time").iloc[-1]["ICB_Code"]
            out = None if pd.isna(v) else int(v)
    except Exception as exc:
        _log.warning("ICB_Code doc loi (%s): %s", ticker, str(exc)[:200])
        out = None
    _CACHE[key] = out
    return out


def _deposit_rate_pct(asof):
    """Lãi suất tiền gửi 12M Big-4 tại asof (%/năm) — `deposit_rate_vn.current_deposit_rate`.

    Đây là ĐÚNG chuỗi research dùng (`analyze.py` import `merge_deposit` từ cùng module), nên
    không hardcode khi module có sẵn. Fallback 5,5% chỉ khi import/đọc hỏng — khi đó
    con số hiển thị không còn cùng hệ với research, nên block tự hạ về NO_DATA ở tầng trên nếu
    cả giá lẫn cổ tức cũng thiếu; ở đây chỉ trả cờ để caller ghi rõ nguồn."""
    key = ("_deprate", str(asof)[:10])
    if key in _CACHE:
        return _CACHE[key]
    out = (YIELD_FLOOR_DEPOSIT_FALLBACK_PCT, "fallback")
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        from deposit_rate_vn import current_deposit_rate
        out = (float(current_deposit_rate(str(asof)[:10])), "deposit_rate_vn")
    except Exception as exc:
        _log.warning("deposit_rate_vn doc loi: %s", str(exc)[:200])
    _CACHE[key] = out
    return out


def _yield_floor(ticker, asof, ref_price=None):
    """Sàn giá cổ tức — DISPLAY_ONLY, xem khối chú thích ở `_YIELD_FLOOR_NOTE`.

    Trả dict luôn ĐỦ khoá (không bao giờ None, không bao giờ raise). Mọi đường hỏng —
    feed corporate_action cũ/không đọc được, không có DIV, thiếu giá — đều về
    `yield_floor_note = "NO_DATA"` và KHÔNG chặn gì.

    ⚠️ `prox_to_floor < 1` = giá DƯỚI sàn = tỉ suất CAO HƠN lãi tiền gửi. Cùng đại lượng với
    `prox = deposit_rate / yield` của research (`analyze.py:347`), chỉ viết theo hệ giá.
    """
    asof = str(_as_date(asof))
    out = {"is_stable_payer": None, "trailing_annual_div_vnd": None, "trailing_yield_pct": None,
           "deposit_rate_pct": None, "deposit_rate_source": None, "yield_floor_price_vnd": None,
           "prox_to_floor": None, "ref_price_vnd": None, "icb_code": None,
           "n_div_windows": None, "yield_floor_note": "NO_DATA", "note": _YIELD_FLOOR_NOTE}
    key = ("_yfloor", ticker, asof)
    if key in _CACHE and ref_price is None:
        return _CACHE[key]
    try:
        dep, dep_src = _deposit_rate_pct(asof)
        out["deposit_rate_pct"] = round(dep, 4)
        out["deposit_rate_source"] = dep_src
        icb = _icb_code(ticker, asof)
        out["icb_code"] = icb

        if _corp_action_feed_ok(_as_date(asof)):
            rows = _corp_action_lib().bq(_YIELD_FLOOR_SQL.format(ticker=ticker, asof=asof))
            if rows:
                r = rows[0]
                n0, n1, n2 = int(r["n0"]), int(r["n1"]), int(r["n2"])
                div0 = float(r["div0"] or 0.0)
                out["n_div_windows"] = [n0, n1, n2]
                out["trailing_annual_div_vnd"] = round(div0, 4)
                stable = (n0 >= 1 and n1 >= 1 and n2 >= 1)
                px = ref_price if ref_price else _ref_price_for(ticker, asof)
                out["ref_price_vnd"] = float(px) if px else None
                if div0 > 0 and px and dep > 0:
                    out["trailing_yield_pct"] = round(div0 / float(px) * 100.0, 4)
                    floor_px = div0 / (dep / 100.0)
                    out["yield_floor_price_vnd"] = round(floor_px, 2)
                    prox = float(px) / floor_px
                    out["prox_to_floor"] = round(prox, 4)
                    if stable:
                        out["yield_floor_note"] = (
                            "BELOW_FLOOR" if prox < YIELD_FLOOR_NEAR_LO else
                            "ABOVE_FLOOR" if prox > YIELD_FLOOR_NEAR_HI else "NEAR_FLOOR")
                # `is_stable_payer` là SỰ THẬT đo được, tách khỏi nhãn diễn giải: mã trả đều
                # nhưng thiếu giá vẫn là stable payer, chỉ không định vị được so với sàn.
                out["is_stable_payer"] = bool(stable)

        # Ngân hàng: giữ NGUYÊN các số thô (chúng là sự thật), chỉ CẤM phần diễn giải —
        # research không có quyền phát biểu ở đây (n=3).
        if icb == YIELD_FLOOR_ICB_BANKING:
            out["is_stable_payer"] = None
            out["yield_floor_note"] = "BANKING_EXCLUDED"
            out["note"] = _YIELD_FLOOR_BANKING_NOTE
    except Exception as exc:
        _log.warning("yield_floor loi (%s): %s", ticker, str(exc)[:200])
        out["yield_floor_note"] = "NO_DATA"
    if ref_price is None:
        _CACHE[key] = out
    return out


def _today_ict():
    """Ngày hôm nay theo giờ VN — §16: KHÔNG bao giờ tin TZ của process gọi."""
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()


def _as_date(x):
    """date | str | None → date (None ⇒ hôm nay ICT). Không raise."""
    if isinstance(x, dt.date) and not isinstance(x, dt.datetime):
        return x
    if isinstance(x, dt.datetime):
        return x.date()
    try:
        return dt.date.fromisoformat(str(x)[:10])
    except Exception:
        return _today_ict()


def _corp_action_lib():
    """Import `corp_action_lib` ở repo root (reader + taxonomy dùng chung, đã có 7 ca hồi quy).

    Neo sys.path giống `strategies.py` — module này sống ở root chứ không trong package.
    KHÔNG viết lại reader: `pricing_events()` là cái DUY NHẤT đúng cho lịch giá TƯƠNG LAI
    (bao gồm `announced`; `events()` lọc `executed` ⇒ rỗng đúng những ngày cần).
    """
    import sys as _sys
    if WORKDIR not in _sys.path:
        _sys.path.insert(0, WORKDIR)
    import corp_action_lib
    return corp_action_lib


def _corp_action_feed_ok(today):
    """Cổng freshness BẮT BUỘC cho `corporate_action` (§14 + registry: bảng KHÔNG có writer
    trong repo, chỉ có lời hứa refresh hằng ngày ⇒ verify artifact mỗi lần đọc).

    Cache 1 lần/process: 1 query cho cả report, không phải mỗi mã."""
    key = ("_ca_fresh", str(today))
    if key in _CACHE:
        return _CACHE[key]
    ok = False
    try:
        fr = _corp_action_lib().feed_freshness()
        ing = str(fr.get("max_ingested") or "")[:10]
        age = (today - dt.date.fromisoformat(ing)).days
        ok = age <= CORP_ACTION_STALE_DAYS_MAX
        if not ok:
            _log.warning("corporate_action feed cu %s ngay (max_ingested=%s) — bo qua exdate",
                         age, ing)
    except Exception as exc:
        _log.warning("corporate_action freshness doc loi: %s", str(exc)[:200])
    _CACHE[key] = ok
    return ok


def _get_upcoming_exdate(ticker, today_ict=None, ref_price=None):
    """Cổ tức TIỀN MẶT sắp GDKHQ trong {CORP_ACTION_LOOKAHEAD_DAYS} ngày tới — hoặc None.

    Trả dict: exright_date, value_per_share, gross_yield_pct, cost_estimate_20d_pp, note …
    None = KHÔNG có sự kiện, HOẶC không đọc được/feed cũ (fail-closed, gộp làm một theo spec).

    ⚠️ CẤM đọc `ticker.Price`/`Close` của CHÍNH ngày ex-date (cổng Sprint 1): giá ngày đó đã
    điều chỉnh quyền, lấy nó làm mẫu số là trộn hai hệ quy chiếu. Ở đây không thể vi phạm —
    ex-date nằm trong TƯƠNG LAI, giá tham chiếu luôn là phiên gần nhất ≤ asof.
    """
    today = _as_date(today_ict)
    key = ("_exdate", ticker, str(today))
    if key in _CACHE and ref_price is None:
        return _CACHE[key]
    out = None
    try:
        if _corp_action_feed_ok(today):
            rows = _corp_action_lib().pricing_events(
                [ticker], since=today.isoformat(),
                until=(today + dt.timedelta(days=CORP_ACTION_LOOKAHEAD_DAYS)).isoformat(),
                codes=("DIV",))
            rows = [r for r in rows
                    if r.get("exright_date") and r.get("value_per_share") not in (None, "")]
            if rows:
                ex = min(str(r["exright_date"])[:10] for r in rows)
                same = [r for r in rows if str(r["exright_date"])[:10] == ex]
                # Bẫy (3) registry: trùng (ticker, exright_date, event_code) có thể là NHIỀU ĐỢT
                # (SUM đúng) hoặc AMENDMENT (lấy public_date mới nhất). Không SUM mù — lấy bản
                # công bố mới nhất và CÔNG BỐ số dòng để người đọc biết còn nghi ngờ.
                pick = sorted(same, key=lambda r: str(r.get("public_date") or ""))[-1]
                vps = float(pick["value_per_share"])
                px = ref_price if ref_price else _ref_price_for(ticker, today)
                gy = (vps / float(px) * 100.0) if px else None
                out = {
                    "exright_date": ex,
                    "days_to_ex": (dt.date.fromisoformat(ex) - today).days,
                    "value_per_share": vps,
                    "ref_price": float(px) if px else None,
                    "gross_yield_pct": round(gy, 4) if gy is not None else None,
                    "cost_estimate_20d_pp": (round(gy * EXDATE_COST_PP_PER_PP_YIELD, 4)
                                             if gy is not None else None),
                    "n_events_same_date": len(same),
                    "event_status": pick.get("event_status"),
                    "note": _EXDATE_NOTE,
                }
    except Exception as exc:
        _log.warning("upcoming ex-date loi (%s): %s", ticker, str(exc)[:200])
        out = None
    if ref_price is None:
        _CACHE[key] = out
    return out


def _ref_price_for(ticker, asof):
    """Giá tham chiếu để quy ra tỉ suất = phiên gần nhất ≤ asof (KHÔNG phải ngày ex-date).

    COALESCE(Price, Close) — cùng quy ước với `adv_vnd()`. None nếu không đọc được."""
    import pandas as pd
    try:
        row = _latest_row(ticker, str(asof)[:10])
    except Exception:
        return None
    if row is None:
        return None
    px = row.get("Price")
    if pd.isna(px):
        px = row.get("Close")
    return None if pd.isna(px) else float(px)


_INSIDER_SQL = """
WITH ins AS (
  SELECT i.ticker, i.public_date, i.trader_person_id AS pid,
         IF(i.action_code = "S", -ABS(i.share_acquire), ABS(i.share_acquire)) AS qty
  FROM `lithe-record-440915-m9.tav2_bq.insider_transaction` AS i
  WHERE i.event_code IN ("DDIND","DDRP")
    AND i.action_code IN ("B","S")
    AND i.trade_status = "Đã thực hiện xong"
    AND i.share_acquire IS NOT NULL AND ABS(i.share_acquire) > 0
    AND i.public_date <= DATE "{asof}"
    AND i.public_date > DATE_SUB(DATE "{asof}", INTERVAL {win} DAY)
),
agg AS (
  SELECT x.ticker,
         SUM(IF(x.qty < 0, -x.qty, 0)) AS sell_sh_90,
         COUNT(DISTINCT IF(x.qty < 0, x.pid, NULL)) AS nsell_90,
         COUNT(DISTINCT IF(x.qty > 0, x.pid, NULL)) AS nbuy_90,
         MAX(IF(x.qty < 0, x.public_date, NULL)) AS last_sell_date
  FROM ins x GROUP BY 1
),
osh AS (
  SELECT q.ticker, q.OShares
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS q
  WHERE q.OShares > 0 AND q.time <= DATE "{asof}"
  QUALIFY ROW_NUMBER() OVER (PARTITION BY q.ticker ORDER BY q.time DESC) = 1
)
SELECT a.ticker, CAST(a.last_sell_date AS STRING) AS last_sell_date,
       a.nsell_90, a.nbuy_90, a.sell_sh_90, o.OShares,
       SAFE_DIVIDE(a.sell_sh_90, o.OShares) AS sell_pct_osh
FROM agg a JOIN osh o ON o.ticker = a.ticker
WHERE a.nsell_90 > a.nbuy_90
  AND SAFE_DIVIDE(a.sell_sh_90, o.OShares) >= {thr}
"""


def _insider_scan(asof):
    """Quét CẢ THỊ TRƯỜNG 1 lần/asof → {ticker: rec}. None = không kết luận được (fail-closed).

    Quét cả thị trường thay vì lọc theo mã CỐ Ý: 1 query cho cả report (bảng ~vài chục MB,
    quét full rất rẻ) thay vì 1 query/mã. Bản sao SQL của `insider_flags.py` — selfcheck
    `due_diligence_corp_flags_selfcheck.py` (ca E) so hai bên tại chỗ để bắt drift định nghĩa.
    """
    key = ("_insider", str(asof))
    if key in _CACHE:
        return _CACHE[key]
    res = None
    try:
        lib = _corp_action_lib()          # dùng chung wrapper bq() (đã chống cắt 100 dòng)
        mx = lib.bq("SELECT CAST(MAX(public_date) AS STRING) d "
                    "FROM `lithe-record-440915-m9.tav2_bq.insider_transaction`")[0]["d"]
        stale = _sessions_between(dt.date.fromisoformat(str(mx)[:10]), _as_date(asof))
        if stale > INSIDER_STALE_SESSIONS_MAX:
            _log.warning("insider_transaction cu ~%s phien (MAX(public_date)=%s) — khong ket luan",
                         stale, mx)
        else:
            rows = lib.bq(_INSIDER_SQL.format(asof=str(asof)[:10], win=INSIDER_WINDOW_DAYS,
                                              thr=INSIDER_SELL_PCT_OSH_MIN))
            res = {r["ticker"]: r for r in rows}
    except Exception as exc:
        _log.warning("insider scan loi: %s", str(exc)[:200])
        res = None
    _CACHE[key] = res
    return res


def _sessions_between(d0, d1):
    """Số phiên xấp xỉ (đếm T2-T6, kể cả lễ) — cùng cách đếm với `insider_flags.py`:
    ước lượng THỪA ⇒ dễ WARN hơn, đúng hướng cho một cổng 'đừng kết luận khi nguồn có thể chết'."""
    n, d = 0, d0
    while d < d1:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def _get_insider_net_sell_flag(ticker, today_ict=None):
    """Cờ "nội bộ bán ròng ≥1% CP lưu hành/90 ngày" — hoặc None.

    None = KHÔNG có cờ, HOẶC không đọc được/nguồn cũ (fail-closed, gộp làm một theo spec).
    Trả dict: net_sell_pct (thập phân), window_days, n_sellers, n_buyers, last_sell_date, note.
    """
    today = _as_date(today_ict)
    scan = _insider_scan(today)
    if not scan:
        return None
    r = scan.get(ticker)
    if not r:
        return None
    try:
        return {
            "net_sell_pct": round(float(r["sell_pct_osh"]), 5),
            "window_days": INSIDER_WINDOW_DAYS,
            "n_sellers": int(r["nsell_90"]),
            "n_buyers": int(r["nbuy_90"]),
            "last_sell_date": str(r.get("last_sell_date") or "")[:10] or None,
            "note": _INSIDER_NOTE,
        }
    except Exception as exc:
        _log.warning("insider flag doc loi (%s): %s", ticker, str(exc)[:200])
        return None


def _corp_flags(ticker, asof):
    """(upcoming_exdate, insider_net_sell) — không bao giờ raise, không bao giờ chặn gì."""
    try:
        ex = _get_upcoming_exdate(ticker, asof)
    except Exception as exc:                       # lưới cuối, 2 hàm trên đã tự nuốt lỗi
        _log.warning("corp flag exdate loi (%s): %s", ticker, str(exc)[:200])
        ex = None
    try:
        ins = _get_insider_net_sell_flag(ticker, asof)
    except Exception as exc:
        _log.warning("corp flag insider loi (%s): %s", ticker, str(exc)[:200])
        ins = None
    return ex, ins


def _fmt_vnd(x):
    if x is None:
        return "n/a"
    if x >= 1e9:
        return f"{x / 1e9:,.2f} tỷ"
    return f"{x / 1e6:,.0f} tr"


def _liquidity_part(row, in_universe, universe_last, est_value_vnd, quality_flag=None):
    """Trả (text, red_flags) — red_flags = list mã cờ ĐỎ (xem RED_FLAG_CODES)."""
    import pandas as pd
    v50 = row.get("Volume_3M_P50")
    px = row.get("Price") if pd.notna(row.get("Price")) else row.get("Close")
    adv = None
    if pd.notna(v50) and pd.notna(px):
        adv = float(v50) * float(px)
    bits, red = [], []
    if adv is None:
        bits.append("⚠ thanh khoản: n/a (thiếu Volume_3M_P50)")
    elif adv <= ADV_DEAD_VND:
        bits.append(f"🔴 thanh khoản ~0 (ADV3T {_fmt_vnd(adv)}/phiên) — NGOÀI mô hình backtest")
        red.append("THANH_KHOAN_CHET")
    elif adv < ADV_THIN_VND:
        bits.append(f"⚠ thanh khoản mỏng (ADV3T {_fmt_vnd(adv)}/phiên < sàn {ADV_THIN_VND/1e9:.0f} tỷ "
                    f"— sàn CỨNG của book LAG/BAL từ 2026-08-10; lệnh này tới được đây nghĩa là "
                    f"nó KHÔNG đi qua gate đó)")
    else:
        bits.append(f"thanh khoản OK (ADV3T {_fmt_vnd(adv)}/phiên)")
    src = "ticker_prune" if UNIVERSE_SOURCE == "prune" else "universe_pit"
    if in_universe is None:
        bits.append(f"⚠ {src}: n/a (không đọc được)")
    elif not in_universe:
        bits.append(f"🔴 NGOÀI {src}" + (f" (lần cuối {universe_last})" if universe_last else ""))
        red.append("NGOAI_UNIVERSE")
    elif quality_flag and quality_flag != "QUALITY_OK":
        # Q-C: cờ THUẦN THÔNG TIN cho due-diligence, KHÔNG chặn gì (§3.2b, user chốt 2026-07-22)
        bits.append(f"⚠ cờ chất lượng {quality_flag}")
    if est_value_vnd and adv:
        pct = est_value_vnd / adv
        mark = "🔴" if pct > ORDER_ADV_HARD else ("⚠" if pct > ORDER_ADV_WARN else "")
        if pct > ORDER_ADV_HARD:
            red.append("LENH_QUA_LON_VS_ADV")
        bits.append(f"{mark} lệnh dự kiến {_fmt_vnd(est_value_vnd)} = {pct*100:.0f}% ADV".strip())
    return " · ".join(bits), red


def _pead_part(row):
    """Tính CƠ HỌC của surprise PEAD: nền YoY (NP_P4) âm hay có quý lỗ trong 4 quý nền
    → % surprise phồng lên do mẫu số/nền âm, không phải cải thiện thật.

    Trả (text, red_flags) — cùng convention với _liquidity_part."""
    import pandas as pd
    np0 = row.get("NP_P0")
    base = [row.get(f"NP_P{i}") for i in (1, 2, 3, 4)]
    if pd.isna(np0) or all(pd.isna(b) for b in base):
        return "surprise: n/a (thiếu NP_P0..P4)", []
    np4 = row.get("NP_P4")
    neg_q = [f"P{i}" for i in (1, 2, 3, 4)
             if pd.notna(row.get(f"NP_P{i}")) and float(row.get(f"NP_P{i}")) <= 0]
    if pd.notna(np4) and float(np4) <= 0:
        return ("🔴 surprise PHỒNG CƠ HỌC: nền YoY NP_P4 ≤ 0 "
                f"({float(np4)/1e9:,.1f} tỷ) — %YoY vô nghĩa"), ["SURPRISE_PHONG_CO_HOC"]
    if neg_q:
        return (f"⚠ có quý LỖ trong nền 4 quý ({','.join(neg_q)}) — surprise có thể do nền thấp"), []
    return "nền YoY dương (surprise không phồng do nền âm)", []


def _fa_part(row):
    import pandas as pd
    def g(k, pct=False, dec=2):
        v = row.get(k)
        if v is None or pd.isna(v):
            return "n/a"
        return f"{float(v)*100:.1f}%" if pct else f"{float(v):.{dec}f}"
    return (f"FA: ROE5Y {g('ROE5Y', pct=True)} · ROE_Min3Y {g('ROE_Min3Y', pct=True)} · "
            f"FSCORE {g('FSCORE', dec=0)} · D/E {g('Debt_Eq_P0')} · PE {g('PE')}")


# ---------------------------------------------------------------------------------------
# Cờ ĐỎ cơ học (2026-08-03, sau case DHD) — bước XÁC NHẬN ĐÃ ĐỌC, KHÔNG phải hard-gate.
#
# VÌ SAO CÓ: mandate 07-21 sinh ra lớp DD thuần thông tin, nhưng không ai BUỘC phải đọc/quyết
# định trước khi mua → thực tế bị bỏ qua (DHD 08-03: ADV3T ~58,7tr/phiên + NGOÀI universe_pit,
# hai dòng 🔴 hiện đủ trong report mà vẫn lọt vào plan). Cơ chế bắt buộc dùng lại ĐÚNG pattern
# dcf_override_reason (Pha 2 DCF, 2026-07-14): có cờ đỏ + side=buy mà thiếu `dd_override_reason`
# → hiện ⚠ ở mọi kênh + bus event audit-trail khi khớp lệnh thật. KHÔNG chặn lệnh (mandate gốc
# "THUẦN THÔNG TIN — KHÔNG chặn lệnh" của file này giữ nguyên, user KHÔNG yêu cầu đảo ngược).
#
# Cờ được sinh TẠI CHỖ tính (mỗi nhánh 🔴 trong _liquidity_part/_pead_part trả kèm mã cờ), KHÔNG
# grep emoji ở tầng trên — đổi câu chữ hiển thị không được làm vỡ cơ chế phát hiện.
#
# KHÔNG nằm trong danh sách này (có chủ ý):
#   · DCF RICH+robust → đã có `dcf_override_reason` riêng, không hỏi người 2 lần cùng 1 việc.
#   · Các cảnh báo ⚠ (thanh khoản mỏng <2 tỷ, cờ chất lượng Q-C, quý lỗ trong nền, anomaly tier)
#     → mức CÂN NHẮC, không phải mức "phải viết lý do"; giữ ngưỡng ⚠/🔴 sẵn có, không đẻ ngưỡng mới.
RED_FLAG_CODES = {
    "THANH_KHOAN_CHET":      f"ADV3T ≤ {ADV_DEAD_VND/1e6:.0f}tr/phiên — ngoài mô hình backtest",
    "NGOAI_UNIVERSE":        "không nằm trong universe (universe_pit/ticker_prune)",
    "LENH_QUA_LON_VS_ADV":   f"lệnh dự kiến > {ORDER_ADV_HARD:.0%} ADV — impact/không khớp nổi",
    "SURPRISE_PHONG_CO_HOC": "nền YoY NP_P4 ≤ 0 → %surprise PEAD vô nghĩa",
    "DD_KHONG_CHAY_DUOC":    "không chạy được due-diligence (thiếu dữ liệu/lỗi đọc) — mua mù",
}


def format_dd_check(dd, side="buy", has_override=False):
    """1 dòng hiển thị chuẩn cho dd_check dict — analog format_dcf_check(). Informational.

    Trả "" khi không có cờ đỏ (hoặc side != buy) — caller bỏ dòng, không hiện gì."""
    if not dd or not isinstance(dd, dict) or not dd.get("has_red_flag"):
        return ""
    if str(side).lower() != "buy":
        return ""
    flags = ", ".join(dd.get("red_flags") or [])
    out = f"🔴 DD cờ đỏ: {flags}"
    return out + (" ⚠" if has_override else " ⚠ cần dd_override_reason")


def dd_check_for_order(ticker, book=None, asof=None, est_value_vnd=None):
    """dict gọn để GẮN VÀO PlannedOrder.dd_check — analog _dcf_check_for_order().

    Cố ý KHÔNG chứa text dài (plan JSON đọc bằng mắt): chỉ cờ + bằng chứng 1 dòng thanh khoản.
    skip_dcf=True — trục định giá đã có dcf_check riêng. KHÔNG BAO GIỜ raise."""
    ctx = {"asof": asof or dt.date.today(), "skip_dcf": True, "skip_corp_flags": True}
    if est_value_vnd:
        ctx["est_value_vnd"] = est_value_vnd
    d = run_due_diligence(ticker, book, ctx, as_dict=True)
    if not isinstance(d, dict):
        return None
    return {"has_red_flag": bool(d.get("has_red_flag")),
            "red_flags": list(d.get("red_flags") or []),
            "as_of": d.get("as_of"), "data_date": d.get("data_date"),
            "universe_source": d.get("universe_source"),
            "evidence": str(d.get("liquidity") or d.get("error") or "")[:200]}


def run_due_diligence(ticker, book=None, context=None, as_dict=False):
    """Due-diligence tổng hợp cho 1 ứng cử viên mua. Trả 1-3 dòng text (informational).

    ticker  : mã.
    book    : "BAL"/"LAG"/"CAPIT"/"DC"/"PARK"/... — chỉ dùng để chọn trục cần soi
              (trục PEAD chỉ có nghĩa với LAG/PEAD) + hiển thị.
    context : dict tuỳ chọn — {"asof": date, "price": float, "est_value_vnd": float,
              "dcf": dcf_check dict đã tính sẵn, "skip_dcf": True,
              "skip_corp_flags": True (bỏ 2 trường corp-action/insider — xem _corp_flags),
              "side": "buy"|"sell", "dd_override_reason": str}.
              side/dd_override_reason CHỈ đổi dòng ⚠ cuối (mirror format_dcf_check(has_override)),
              không đổi nội dung phân tích.
    as_dict : True → trả dict các trục thay vì text (cho caller muốn tự render);
              luôn kèm "red_flags" (list) + "has_red_flag" (bool).

    KHÔNG BAO GIỜ raise.
    """
    ctx = context or {}
    asof = str(ctx.get("asof") or dt.date.today())[:10]
    prefix = f"DD {ticker}" + (f" [{book}]" if book else "")
    is_buy = str(ctx.get("side", "buy")).lower() in ("buy", "mua", "b")
    has_override = bool(ctx.get("dd_override_reason") or ctx.get("has_override"))
    try:
        row = _latest_row(ticker, asof)
        if row is None:
            out = {"ticker": ticker, "book": book, "as_of": asof,
                   "error": "không có dữ liệu trong bq_cache/ticker",
                   "upcoming_exdate": None, "insider_net_sell": None, "yield_floor": None,
                   "red_flags": ["DD_KHONG_CHAY_DUOC"], "has_red_flag": True}
            if as_dict:
                return out
            msg = f"{prefix}: ⚠ DD n/a — không thấy mã trong bq_cache/ticker"
            warn = format_dd_check(out, "buy" if is_buy else "sell", has_override)
            return msg + (f"\n    {warn}" if warn else "")

        in_universe, universe_last, quality_flag = _in_universe(ticker, asof)
        est_val = ctx.get("est_value_vnd")
        liq_s, red = _liquidity_part(row, in_universe, universe_last, est_val, quality_flag)
        parts = {
            "data_date": str(row.get("time"))[:10],
            "liquidity": liq_s,
            "in_universe": in_universe,
            "universe_source": UNIVERSE_SOURCE,
            "quality_flag": quality_flag,
            "fundamentals": _fa_part(row),
            "anomaly": _anomaly_note(ticker, asof),
        }
        if str(book or "").upper() in ("LAG", "PEAD"):
            parts["signal_mechanics"], _pead_red = _pead_part(row)
            red += _pead_red
        # 2 trường THÔNG TIN (2026-08-17) — chỉ vào dict, KHÔNG vào text, KHÔNG sinh cờ đỏ.
        # `skip_corp_flags` cho đường SINH LỆNH (dd_check_for_order): 2 trường này không đi vào
        # PlannedOrder.dd_check, nên ở đó chúng chỉ là ~1 query BQ/mã trên đúng đường găng 21:00.
        if ctx.get("skip_corp_flags"):
            parts["upcoming_exdate"], parts["insider_net_sell"] = None, None
            parts["yield_floor"] = None
        else:
            parts["upcoming_exdate"], parts["insider_net_sell"] = _corp_flags(ticker, asof)
            # DISPLAY_ONLY (2026-08-18) — cùng cổng `skip_corp_flags` với 2 trường trên vì cùng
            # đọc `corporate_action`: đường SINH LỆNH 21:00 không phải trả thêm query/mã.
            # KHÔNG đi vào text, KHÔNG sinh cờ đỏ, KHÔNG đụng `red`/`has_red_flag`.
            try:
                parts["yield_floor"] = _yield_floor(ticker, asof, ctx.get("price"))
            except Exception as exc:                   # lưới cuối; _yield_floor đã tự nuốt lỗi
                _log.warning("yield_floor wrapper loi (%s): %s", ticker, str(exc)[:200])
                parts["yield_floor"] = None

        parts["red_flags"] = red
        parts["has_red_flag"] = bool(red)

        # ---- valuation: gọi lại lăng kính DCF/sector sẵn có, không viết lại ----
        dcf_s = ""
        if not ctx.get("skip_dcf"):
            try:
                from .strategies import _dcf_check_for_order, format_dcf_check
                dcf = ctx.get("dcf")
                if not dcf:
                    px = ctx.get("price")
                    if px is None:
                        import pandas as _pd
                        px = row.get("Price") if _pd.notna(row.get("Price")) else row.get("Close")
                    dcf = _dcf_check_for_order(ticker, float(px), asof) if px else None
                dcf_s = format_dcf_check(dcf, side="buy", ticker=ticker) if dcf else ""
            except Exception as exc:
                _log.warning("DD valuation lỗi (%s): %s", ticker, exc)
        parts["valuation"] = dcf_s

        if as_dict:
            parts.update({"ticker": ticker, "book": book, "as_of": asof})
            return parts

        line1 = [parts["liquidity"]]
        if parts.get("signal_mechanics"):
            line1.append(parts["signal_mechanics"])
        if parts["anomaly"]:
            line1.append(parts["anomaly"])
        lines = [f"{prefix} (data {parts['data_date']}): " + " · ".join(line1),
                 f"    {parts['fundamentals']}"]
        if dcf_s:
            lines.append(f"    {dcf_s}")
        warn = format_dd_check(parts, "buy" if is_buy else "sell", has_override)
        if warn:
            lines.append(f"    {warn}")
        return "\n".join(lines)

    except Exception as exc:
        _log.warning("run_due_diligence lỗi (%s): %s", ticker, exc)
        out = {"ticker": ticker, "book": book, "error": str(exc)[:200],
               "upcoming_exdate": None, "insider_net_sell": None, "yield_floor": None,
               "red_flags": ["DD_KHONG_CHAY_DUOC"], "has_red_flag": True}
        if as_dict:
            return out
        msg = f"{prefix}: ⚠ DD n/a ({str(exc)[:80]})"
        warn = format_dd_check(out, "buy" if is_buy else "sell", has_override)
        return msg + (f"\n    {warn}" if warn else "")


DD_DISCLAIMER = ("Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/"
                 "cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache "
                 "local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu. "
                 "Có 🔴 cờ đỏ mà vẫn mua → PHẢI ghi `dd_override_reason` trong plan (thiếu = WARN, "
                 "vẫn thực thi).")
