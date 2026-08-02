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

from .config import WORKDIR, DATA_DIR

_log = logging.getLogger(__name__)

# Ngưỡng CẢNH BÁO hiển thị (không phải gate). ADV_THIN neo theo sàn thanh khoản 2 tỷ/phiên mà
# rổ CAPIT trong golive_recommend_v23.py đã dùng (`Price*Volume/1e9 >= 2`) — giữ 1 con số chung
# cho cả fleet thay vì đẻ ngưỡng mới.
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


def _fmt_vnd(x):
    if x is None:
        return "n/a"
    if x >= 1e9:
        return f"{x / 1e9:,.2f} tỷ"
    return f"{x / 1e6:,.0f} tr"


def _liquidity_part(row, in_universe, universe_last, est_value_vnd, quality_flag=None):
    import pandas as pd
    v50 = row.get("Volume_3M_P50")
    px = row.get("Price") if pd.notna(row.get("Price")) else row.get("Close")
    adv = None
    if pd.notna(v50) and pd.notna(px):
        adv = float(v50) * float(px)
    bits = []
    if adv is None:
        bits.append("⚠ thanh khoản: n/a (thiếu Volume_3M_P50)")
    elif adv <= ADV_DEAD_VND:
        bits.append(f"🔴 thanh khoản ~0 (ADV3T {_fmt_vnd(adv)}/phiên) — NGOÀI mô hình backtest")
    elif adv < ADV_THIN_VND:
        bits.append(f"⚠ thanh khoản mỏng (ADV3T {_fmt_vnd(adv)}/phiên < sàn {ADV_THIN_VND/1e9:.0f} tỷ)")
    else:
        bits.append(f"thanh khoản OK (ADV3T {_fmt_vnd(adv)}/phiên)")
    src = "ticker_prune" if UNIVERSE_SOURCE == "prune" else "universe_pit"
    if in_universe is None:
        bits.append(f"⚠ {src}: n/a (không đọc được)")
    elif not in_universe:
        bits.append(f"🔴 NGOÀI {src}" + (f" (lần cuối {universe_last})" if universe_last else ""))
    elif quality_flag and quality_flag != "QUALITY_OK":
        # Q-C: cờ THUẦN THÔNG TIN cho due-diligence, KHÔNG chặn gì (§3.2b, user chốt 2026-07-22)
        bits.append(f"⚠ cờ chất lượng {quality_flag}")
    if est_value_vnd and adv:
        pct = est_value_vnd / adv
        mark = "🔴" if pct > ORDER_ADV_HARD else ("⚠" if pct > ORDER_ADV_WARN else "")
        bits.append(f"{mark} lệnh dự kiến {_fmt_vnd(est_value_vnd)} = {pct*100:.0f}% ADV".strip())
    return " · ".join(bits)


def _pead_part(row):
    """Tính CƠ HỌC của surprise PEAD: nền YoY (NP_P4) âm hay có quý lỗ trong 4 quý nền
    → % surprise phồng lên do mẫu số/nền âm, không phải cải thiện thật."""
    import pandas as pd
    np0 = row.get("NP_P0")
    base = [row.get(f"NP_P{i}") for i in (1, 2, 3, 4)]
    if pd.isna(np0) or all(pd.isna(b) for b in base):
        return "surprise: n/a (thiếu NP_P0..P4)"
    np4 = row.get("NP_P4")
    neg_q = [f"P{i}" for i in (1, 2, 3, 4)
             if pd.notna(row.get(f"NP_P{i}")) and float(row.get(f"NP_P{i}")) <= 0]
    if pd.notna(np4) and float(np4) <= 0:
        return ("🔴 surprise PHỒNG CƠ HỌC: nền YoY NP_P4 ≤ 0 "
                f"({float(np4)/1e9:,.1f} tỷ) — %YoY vô nghĩa")
    if neg_q:
        return (f"⚠ có quý LỖ trong nền 4 quý ({','.join(neg_q)}) — surprise có thể do nền thấp")
    return "nền YoY dương (surprise không phồng do nền âm)"


def _fa_part(row):
    import pandas as pd
    def g(k, pct=False, dec=2):
        v = row.get(k)
        if v is None or pd.isna(v):
            return "n/a"
        return f"{float(v)*100:.1f}%" if pct else f"{float(v):.{dec}f}"
    return (f"FA: ROE5Y {g('ROE5Y', pct=True)} · ROE_Min3Y {g('ROE_Min3Y', pct=True)} · "
            f"FSCORE {g('FSCORE', dec=0)} · D/E {g('Debt_Eq_P0')} · PE {g('PE')}")


def run_due_diligence(ticker, book=None, context=None, as_dict=False):
    """Due-diligence tổng hợp cho 1 ứng cử viên mua. Trả 1-3 dòng text (informational).

    ticker  : mã.
    book    : "BAL"/"LAG"/"CAPIT"/"DC"/"PARK"/... — chỉ dùng để chọn trục cần soi
              (trục PEAD chỉ có nghĩa với LAG/PEAD) + hiển thị.
    context : dict tuỳ chọn — {"asof": date, "price": float, "est_value_vnd": float,
              "dcf": dcf_check dict đã tính sẵn, "skip_dcf": True}.
    as_dict : True → trả dict các trục thay vì text (cho caller muốn tự render).

    KHÔNG BAO GIỜ raise.
    """
    ctx = context or {}
    asof = str(ctx.get("asof") or dt.date.today())[:10]
    prefix = f"DD {ticker}" + (f" [{book}]" if book else "")
    try:
        row = _latest_row(ticker, asof)
        if row is None:
            out = {"ticker": ticker, "book": book, "as_of": asof,
                   "error": "không có dữ liệu trong bq_cache/ticker"}
            return out if as_dict else f"{prefix}: ⚠ DD n/a — không thấy mã trong bq_cache/ticker"

        in_universe, universe_last, quality_flag = _in_universe(ticker, asof)
        est_val = ctx.get("est_value_vnd")
        parts = {
            "data_date": str(row.get("time"))[:10],
            "liquidity": _liquidity_part(row, in_universe, universe_last, est_val, quality_flag),
            "in_universe": in_universe,
            "universe_source": UNIVERSE_SOURCE,
            "quality_flag": quality_flag,
            "fundamentals": _fa_part(row),
            "anomaly": _anomaly_note(ticker, asof),
        }
        if str(book or "").upper() in ("LAG", "PEAD"):
            parts["signal_mechanics"] = _pead_part(row)

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
        return "\n".join(lines)

    except Exception as exc:
        _log.warning("run_due_diligence lỗi (%s): %s", ticker, exc)
        msg = f"{prefix}: ⚠ DD n/a ({str(exc)[:80]})"
        return {"ticker": ticker, "book": book, "error": str(exc)[:200]} if as_dict else msg


DD_DISCLAIMER = ("Due-diligence tự động = LỚP THÔNG TIN (thanh khoản/universe/cơ học tín hiệu/"
                 "cờ bất thường/FA thô/định giá). KHÔNG phải gate chặn lệnh; số từ bq_cache "
                 "local (trễ tối đa 1 phiên), không dùng làm giá tham chiếu.")
