#!/usr/bin/env python3
"""Gói due-diligence (DD) TRƯỚC PLAN cho ứng viên book LAG — cổng CLEARED/FLAG.

Chỉ đạo user 2026-10-21 22:10 ICT (job Taylor_20261021_151302): "Candidate của lag book vẫn phải
qua DD chứ không tự mặc định vào plan mua. Phải chạy DD trước rồi mới đưa vào plan tôi duyệt."
Ba điểm user chốt: (1) mã FLAG chưa được user trả lời ⇒ ĐỨNG NGOÀI plan (fail-closed);
(2) CLEARED = DD cơ bản KHÔNG có cờ nào; (3) thí điểm HT1/SCL/VPB.

Mỗi ứng viên LAG (đã qua mọi lọc hiện có — rating 8L, ADV, forensic/BANNED — vì nguồn là CSV
khuyến nghị golive) ⇒ 1 file `data/lag_dd/<ticker>_<release_date>.json` (ghi atomic):
  (a) dd_basic        — TRÍCH bằng chứng từ trading_bot.due_diligence.run_due_diligence (as_dict)
                        + adv_vnd + DCF/sector-lens + gate có sẵn (lag_rating_filter,
                        lag_forensic_filter). KHÔNG viết lại logic DD.
  (b) earnings_quality — chất lượng cú bất ngờ lợi nhuận từ tav2_bq.ticker_financial (registry
                        fundamentals/ticker_financial.md: CANONICAL): nền cùng kỳ, CFO vs LNST,
                        phải thu/tồn kho vs doanh thu, proxy lãi ngoài hoạt động (NPM vs EBITM —
                        bảng KHÔNG có cột LNTT/thu nhập khác, xem registry ticker_financial.md mục
                        IntCov). Thiếu dữ liệu ⇒ "không đủ dữ liệu", KHÔNG đoán 0.
  (c) macro_note      — chỗ trống cho ghi chú vĩ mô (Bobby/macro-strategist; Mike gắn). Không đổi status.
  (d) status          — CLEARED ⇔ danh sách `flags` RỖNG. Mọi nhánh lỗi/thiếu dữ liệu sinh cờ
                        `*_NA` ⇒ FLAG. KHÔNG BAO GIỜ CLEARED vì vắng mặt bằng chứng.

DANH SÁCH CỜ = `FLAG_CODES` dưới đây (cơ học: so ngưỡng số / thành viên danh sách / trường enum;
KHÔNG dò từ khoá trong văn bản tự do). Cờ pháp lý (forensic flag_type ∈ LEGAL_FLAG_TYPES) theo
luật user 27/09: phân tích bình thường, chỉ WARNING tường minh, KHÔNG loại — nhưng vẫn làm
status=FLAG để user xem.

Trạng thái xác nhận của user nằm ở `data/lag_dd/ack.json` (Mike ghi bằng bin/lag_dd_ack.py);
script NÀY KHÔNG BAO GIỜ ghi ack.

Thông báo (`--notify`): 1 tin vào channel `plan_approval` (tên trong kb/discord_channels.json),
idempotent theo (ticker, release_date, flags_hash); chỉ ghi state SAU khi gửi rc=0.

    python3 bin/lag_dd_pack.py [--signal-date YYYY-MM-DD | --tickers HT1,SCL --release-date D]
        [--asof D] [--macro-note PATH | --macro-note TICKER=PATH] [--notify] [--dry-run] [--json]

Mã thoát: 0 mọi gói CLEARED · 2 có ≥1 gói FLAG (không phải lỗi script) · 1 lỗi (không ghi được
gói / không có ứng viên đọc được).
"""
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
if WC_ROOT not in sys.path:
    sys.path.insert(0, WC_ROOT)
ROOT = os.path.dirname(HERE)
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")

SCHEMA_VERSION = 1
CHANNEL = "plan_approval"
SUBPROC_TIMEOUT_S = 60
FIN_FRESH_MAX_DAYS = 60          # release gần nhất ≤ asof phải trong 60 ngày ⇒ mới là "cú bất ngờ" đang xét
BANK_ICB = 8355                   # cùng hằng số với due_diligence.YIELD_FLOOR_ICB_BANKING / rating_8l
LEGAL_FLAG_TYPES = {"fraud_confirmed", "legal", "legal_case", "criminal"}   # enum flag_type forensic_flags.csv

# Ngưỡng chất lượng lợi nhuận — ĐẶT TAY (ước lượng), CHƯA backtest. Chỉ quyết định "đưa user xem",
# không loại mã nào. Đổi ngưỡng = đổi tỷ lệ FLAG, không đổi rủi ro tiền (FLAG chỉ chặn tới khi user trả lời).
EQ_BASE_LOW_RATIO = 0.5           # NP_P4 < 50% trung vị NP_P5..P7 ⇒ nền cùng kỳ thấp bất thường
EQ_CFO_NP_MIN = 0.5               # ΣCFO 4 quý < 50% ΣLNST 4 quý ⇒ lợi nhuận chưa thành tiền
EQ_WC_GAP_PP = 0.30               # phải thu/tồn kho tăng YoY nhanh hơn doanh thu > 30pp
# AR_P0 = TỔNG phải thu ngắn hạn (gồm trả trước cho người bán, phải thu khác, trừ dự phòng). Tra
# 2026-10-22: ticker_financial KHÔNG có cột tách phải thu KHÁCH HÀNG / trả trước người bán
# (AdvCust_P* là NGƯỜI MUA trả trước — nợ phải trả, không phải cấu phần của AR) ⇒ cờ giữ trên tổng
# (fail-closed, không đoán) và nói rõ điều đó trong bằng chứng. Ca SCL 2026Q3: user kiểm tay BCTC.
AR_BASIS_NOTE = ("AR_P0 = TỔNG phải thu NH (gồm trả trước người bán + phải thu khác − dự phòng); "
                 "ticker_financial không tách được phải thu khách hàng/trả trước ⇒ cờ tính trên tổng, "
                 "kiểm thuyết minh BCTC trước khi kết luận")

FLAG_CODES = {
    # --- DD cơ bản: echo cờ đỏ due_diligence.RED_FLAG_CODES (mã nào lạ cũng thành cờ) ---
    "DD_KHONG_CHAY_DUOC":    "run_due_diligence không chạy được / lỗi đọc",
    "THANH_KHOAN_CHET":      "ADV3T ≤ 100tr/phiên (due_diligence)",
    "NGOAI_UNIVERSE":        "ngoài universe_pit (due_diligence)",
    "LENH_QUA_LON_VS_ADV":   "lệnh dự kiến > 25% ADV (due_diligence)",
    "SURPRISE_PHONG_CO_HOC": "nền YoY NP_P4 ≤ 0 (due_diligence)",
    # --- DD cơ bản: các mức ⚠ của DD (user: CLEARED = KHÔNG có cờ nào) ---
    "THANH_KHOAN_MONG":      "ADV3T < 2 tỷ/phiên (due_diligence.ADV_THIN_VND)",
    "CO_CHAT_LUONG_UNIVERSE": "universe_pit quality_flag ≠ QUALITY_OK",
    "QUY_LO_TRONG_NEN":      "có quý NP ≤ 0 trong NP_P1..P4",
    "BAT_THUONG_ANOMALY":    "có bản ghi trong data/anomaly_flags.json",
    "INSIDER_BAN_RONG":      "nội bộ bán ròng ≥1% CP lưu hành/90 ngày (due_diligence)",
    "EXDATE_SAP_TOI":        "cổ tức tiền mặt GDKHQ trong 25 ngày tới (cảnh báo chi phí)",
    "FORENSIC_BANNED":       "BANNED / user-loại / forensic exclude (lag_forensic_filter)",
    "FORENSIC_WATCH":        "forensic_flags.csv severity khác exclude đã hiệu lực",
    "PHAP_LY_WARNING":       "cờ pháp lý (forensic flag_type pháp lý) — CHỈ WARNING, không loại (luật 27/09)",
    "RATING_8L_FAIL":        "8L rating ≥ 4 hoặc không có rating ≤ asof",
    "RATING_8L_CU":          "dòng 8L mới nhất có time < Release_Date của sự kiện (chấm bằng BCTC cũ)",
    # CAPITAL_RAISE_PENDING / CAPITAL_RAISE_12M KHÔNG phải cờ: chỉ WARNING trong pack['warnings'] (user chọn (b) 29/10 —
    # "đưa warning", không chặn mua; xem capital_raise_lib.pre_entry_flags). Chỉ nguồn lỗi mới là cờ (fail-closed):
    "CAPITAL_RAISE_NA":      "không đọc được sự kiện phát hành CP từ tav2_bq.corporate_action (fail-closed)",
    "DCF_RICH":              "DCF status RICH SÂU: biên an toàn < -100% (hoặc thiếu MoS ⇒ fail-closed); RICH nhẹ chỉ là cảnh báo, xem pack['warnings']",
    # --- Chất lượng cú bất ngờ lợi nhuận (b) ---
    "EQ_NEN_THAP":           f"NP_P4 > 0 nhưng < {EQ_BASE_LOW_RATIO:.0%} trung vị NP_P5..P7",
    "EQ_CFO_YEU":            f"ΣCF_OA 4 quý < {EQ_CFO_NP_MIN:.0%} ΣNP 4 quý (phi ngân hàng)",
    "EQ_NGOAI_HOAT_DONG":    "NPM_P0 > EBITM_P0 — lãi ròng vượt lãi hoạt động (proxy thu nhập khác)",
    "EQ_PHAI_THU_TANG":      f"phải thu YoY − doanh thu YoY > {EQ_WC_GAP_PP:.0%}",
    "EQ_TON_KHO_TANG":       f"tồn kho YoY − doanh thu YoY > {EQ_WC_GAP_PP:.0%}",
    # --- Fail-closed: thiếu dữ liệu / lỗi đọc ---
    "RELEASE_NA":            "không xác định được Release_Date sự kiện trong ticker_financial",
    "FIN_NA":                "không đọc được ticker_financial / thiếu cột lõi NP/Revenue/CF_OA",
    "ADV_NA":                "không tính được ADV",
    "UNIVERSE_NA":           "không đọc được universe_pit",
    "ANOMALY_NA":            "không đọc được data/anomaly_flags.json",
    "INSIDER_NA":            "nguồn insider không đọc được / cũ",
    "CORP_FEED_NA":          "feed corporate_action cũ / không đọc được (ex-date không kết luận được)",
    "FORENSIC_NA":           "không đọc được data/forensic_flags.csv",
    "RATING_NA":             "không truy vấn được fa_ratings_8l",
    "DINH_GIA_NA":           "không có DCF lẫn lăng kính định giá thay thế",
}
WARNING_ONLY = {"PHAP_LY_WARNING"}


def _env(name, default):
    return os.environ.get(name) or default


def dd_dir():
    return _env("MIKE_LAG_DD_DIR", os.path.join(WC_ROOT, "data", "lag_dd"))


def today_ict():
    return dt.datetime.now(_ICT).date()


def _num(x):
    """float hữu hạn hoặc None (KHÔNG đoán 0)."""
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _jsonable(x):
    return json.loads(json.dumps(x, ensure_ascii=False, default=str))


def flags_hash(flags):
    """Băm theo MÃ cờ (không theo số bằng chứng — ADV đổi mỗi ngày không được làm mới ack/tin)."""
    codes = sorted({f["code"] for f in flags})
    return hashlib.sha256(json.dumps(codes).encode()).hexdigest()[:16]


# ── nguồn dữ liệu (tách hàm để selfcheck thay bằng giả) ──────────────────────────────────────
def _bq(sql):
    """BQ LIVE — cố ý gỡ BQ_LOCAL_CACHE (wc_env.sh bật nó): đo 21/10 parquet cục bộ thiếu
    CF_OA_P0 quý 2026Q3 của SCL trong khi tav2_bq.ticker_financial live đã có."""
    from simulate_holistic_nav import bq
    saved = os.environ.pop("BQ_LOCAL_CACHE", None)
    try:
        return bq(sql)
    finally:
        if saved is not None:
            os.environ["BQ_LOCAL_CACHE"] = saved


def fetch_fin_rows(ticker, asof):
    """≤ 8 dòng ticker_financial mới nhất có Release_Date ≤ asof (mới → cũ), list dict."""
    df = _bq(f"""SELECT f.* FROM tav2_bq.ticker_financial AS f
WHERE f.ticker = '{ticker}' AND f.Release_Date <= DATE '{asof}'
ORDER BY f.time DESC LIMIT 8""")
    return [] if df is None else df.to_dict("records")


def fetch_issuance(ticker, asof):
    """Mọi dòng phát hành CP (event_code ISS) của mã từ tav2_bq.corporate_action (list dict, kiểu chuỗi như
    rights_issue_alert). Lọc 'công bố ≤ asof' làm trong capital_raise_lib (không nhìn trước)."""
    df = _bq(f"""SELECT c.id, c.ticker, c.issue_method_code, c.issue_status_code, c.event_status,
  CAST(c.exright_date AS STRING) exright_date, CAST(c.record_date AS STRING) record_date,
  CAST(c.public_date AS STRING) public_date, c.exercise_ratio, c.value_per_share, c.total_value, c.issue_volumn
FROM tav2_bq.corporate_action AS c WHERE c.ticker = '{ticker}' AND c.event_code = 'ISS'""")
    if df is None:
        raise RuntimeError("BQ trả None")
    return [{k: (None if v is None or (isinstance(v, float) and math.isnan(v)) else v) for k, v in r.items()}
            for r in df.to_dict("records")]


def capital_raise_eval(rows, issuance, asof):
    """(flags, warnings) lớp A. rows = ticker_financial mới → cũ (lấy OShares). Thuần — selfcheck gọi thẳng."""
    from capital_raise_lib import pre_entry_flags
    os_ = [_num(r.get("OShares")) for r in rows[:5]] if rows else []
    g12 = os_[0] / os_[4] - 1 if len(os_) == 5 and os_[0] and os_[4] else None
    fl, wa = pre_entry_flags(issuance, str(asof)[:10], os_[0] if os_ else None, g12)
    return ([_f(c, e) for c, e in fl],
            [{"code": c, "severity": "WARNING", "evidence": e[:500]} for c, e in wa])


def run_dd(ticker, asof):
    from trading_bot import due_diligence as dd
    d = dd.run_due_diligence(ticker, "LAG", {"asof": asof, "skip_dcf": True}, as_dict=True)
    adv, adv_date, adv_err = dd.adv_vnd(ticker, asof)
    # Phân biệt "không có sự kiện" với "không đọc được" — run_due_diligence gộp cả hai thành None.
    try:
        insider_ok = dd._insider_scan(dd._as_date(asof)) is not None
    except Exception:
        insider_ok = False
    try:
        corp_ok = bool(dd._corp_action_feed_ok(dd._as_date(asof)))
    except Exception:
        corp_ok = False
    anomaly = anomaly_evidence(ticker, asof)
    return {"dd": d, "adv": adv, "adv_date": adv_date, "adv_err": adv_err,
            "adv_thin_vnd": dd.ADV_THIN_VND, "insider_ok": insider_ok, "corp_ok": corp_ok,
            "anomaly_ok": anomaly[0], "anomaly_rec": anomaly[1], "anomaly_err": anomaly[2]}


def anomaly_evidence(ticker, asof):
    """(ok, bản ghi|None, lỗi|None) qua anomaly_gate CANONICAL (cùng cổng với production + 3 sổ paper):
    file cũ / thiếu `_meta` / không đọc được ⇒ ok=False ⇒ ANOMALY_NA (fail-closed — `anomaly_excluded`
    gốc fail-OPEN và trả set rỗng, không thể dùng một mình làm bằng chứng "sạch"). Bản ghi chỉ tính khi
    ticker ∈ anomaly_excluded(asof) = cửa sổ asof−ANOMALY_TTL_DAYS ≤ last_alert ≤ asof (không look-ahead).
    Độ tươi so với ngày `asof`: gói hồi cứu (asof ≠ ngày file được ghi) ⇒ ANOMALY_NA, cố ý."""
    import anomaly_gate as ag
    fr = ag.anomaly_flags_freshness(asof)
    if fr["is_stale"]:
        return False, None, f"anomaly_flags.json cũ/không dùng được: {fr['reason']}"
    try:
        with open(os.path.join(ag.WORKDIR, "data", "anomaly_flags.json"), encoding="utf-8") as fh:
            recs = json.load(fh)
    except Exception as e:
        return False, None, f"{type(e).__name__}: {str(e)[:120]}"
    return True, (recs.get(ticker) if ticker in ag.anomaly_excluded(asof, quiet=True) else None), None


def run_valuation(ticker, asof):
    """(dcf dict|None, chuỗi hiển thị, lăng kính thay thế, lỗi|None) — gọi lại strategies, không viết lại."""
    from trading_bot import due_diligence as dd
    from trading_bot.strategies import _dcf_check_for_order, format_dcf_check, _format_alt_lens
    try:
        px = dd._ref_price_for(ticker, asof)
        dcf = _dcf_check_for_order(ticker, float(px), asof) if px else None
        alt = _format_alt_lens(ticker) or ""
        return dcf, (format_dcf_check(dcf, side="buy", ticker=ticker) if dcf else ""), alt, (
            None if px else "không có giá tham chiếu bq_cache")
    except Exception as e:
        return None, "", "", f"{type(e).__name__}: {str(e)[:160]}"


def run_rating(ticker, asof, release_date):
    """{rating, rating_date, fail, stale, err}. Dùng lại NGUYÊN 2 hàm của lag_rating_filter."""
    import pandas as pd
    from lag_rating_filter import lag_filter_low_rating, lag_rating_stale_flags
    cand = pd.DataFrame({"ticker": [ticker], "Release_Date": [release_date]})
    _, dropped, err = lag_filter_low_rating(_bq, cand, asof)
    if err:
        return {"err": err}
    stale, err2 = lag_rating_stale_flags(_bq, cand, asof)
    out = {"err": err2, "fail": dropped[0] if dropped else None,
           "stale": stale[0] if stale else None}
    return _jsonable(out)


def run_forensic(ticker, asof):
    """{dropped, watch[], err}. BANNED/exclude qua lag_forensic_filter; watch đọc thẳng CSV."""
    import pandas as pd
    from lag_forensic_filter import lag_filter_forensic_banned, FORENSIC_CSV
    _, dropped, err = lag_filter_forensic_banned(pd.DataFrame({"ticker": [ticker]}), asof,
                                                 workdir=WC_ROOT)
    watch = []
    try:
        with open(os.path.join(WC_ROOT, FORENSIC_CSV), encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if (r.get("ticker") or "").strip().upper() == ticker and \
                        str(r.get("date") or "")[:10] <= str(asof):
                    watch.append({k: (r.get(k) or "")[:300] for k in
                                  ("flag_type", "severity", "date", "source", "note")})
    except Exception as e:
        err = err or f"{type(e).__name__}: {e}"
    return _jsonable({"dropped": dropped, "rows": watch, "err": err})


def read_macro_note(path):
    if not path:
        return {"path": None, "status": "chưa có — Mike gắn ghi chú vĩ mô (Bobby) sau, không đổi status"}
    try:
        with open(path, "rb") as fh:
            b = fh.read()
        return {"path": path, "status": "đã gắn", "sha256_16": hashlib.sha256(b).hexdigest()[:16],
                "excerpt": b.decode("utf-8", "replace")[:1500]}
    except OSError as e:
        return {"path": path, "status": f"KHÔNG đọc được: {e}"}


def read_bank_ratios(ticker):
    """Thông tin NPL/LLR/CASA quý gần nhất (fiinprox, registry fiinprox_bank_ratios_quarterly.md:
    DERIVED, nguồn trial hết hạn 09-28). CHỈ THÔNG TIN — không sinh cờ (spec: "nếu có cột")."""
    p = os.path.join(WC_ROOT, "mike", "data", "fiinprox_bank_ratios_quarterly_20260914.csv")
    try:
        with open(p, encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(fh) if (r.get("ticker") or "").upper() == ticker]
    except OSError as e:
        return {"note": f"không đủ dữ liệu ({e})"}
    if not rows:
        return {"note": "không đủ dữ liệu (mã không có trong file fiinprox)"}
    def _yq(r):
        y, q = _num(r.get("year")), _num(r.get("quarter"))
        return (int(y), int(q)) if y is not None and q is not None else None
    rows = sorted((r for r in rows if _yq(r)), key=_yq)
    if not rows:
        return {"note": "không đủ dữ liệu (dòng fiinprox thiếu year/quarter)"}
    y, q = _yq(rows[-1])
    ago = next((r for r in rows if _yq(r) == (y - 1, q)), None)
    return {"source": os.path.relpath(p, WC_ROOT), "latest_quarter": f"{y}Q{q}", "latest": rows[-1],
            "year_ago": ago if ago else "không đủ dữ liệu",
            "note": f"số FiinPro mới nhất {y}Q{q} (trial hết hạn 09-28) — KHÔNG phải quý công bố đang xét; "
                    "tăng trưởng tín dụng: không đủ dữ liệu (không có cột). CHỈ THÔNG TIN, không sinh cờ."}


# ── (b) chất lượng cú bất ngờ lợi nhuận ──────────────────────────────────────────────────────
def earnings_quality(rows, is_bank):
    """rows: dòng ticker_financial mới → cũ (rows[0] = sự kiện). Trả (dict, flags)."""
    out, flags = {}, []
    if not rows:
        return {"note": "không đủ dữ liệu"}, [_f("FIN_NA", "không có dòng ticker_financial nào ≤ asof")]
    r = rows[0]
    np_ = [_num(r.get(f"NP_P{i}")) for i in range(8)]
    out["quarter"] = r.get("quarter")
    out["np_vnd"] = {f"P{i}": v for i, v in enumerate(np_)}
    out["np_yoy"] = (np_[0] / np_[4] - 1) if np_[0] is not None and np_[4] and np_[4] > 0 else None
    out["np_r_bq"] = _num(r.get("NP_R"))
    if np_[0] is None or np_[4] is None:
        flags.append(_f("FIN_NA", f"thiếu NP_P0/NP_P4 (NP_P0={np_[0]}, NP_P4={np_[4]})"))
    missing = []                # tên trường thiếu ⇒ MỘT cờ FIN_NA cuối hàm (vắng dữ liệu KHÔNG BAO GIỜ là sạch)
    missing += [f"NP_P{i}" for i in (5, 6, 7) if np_[i] is None]
    base = [v for v in np_[5:8] if v is not None]
    if len(base) == 3 and np_[4] is not None:
        med = sorted(base)[1]
        out["base_same_q_vs_median_p5_p7"] = (np_[4] / med) if med > 0 else None
        if np_[4] > 0 and med > 0 and np_[4] < EQ_BASE_LOW_RATIO * med:
            flags.append(_f("EQ_NEN_THAP", f"NP_P4={np_[4]/1e9:,.1f} tỷ < {EQ_BASE_LOW_RATIO:.0%} × "
                                           f"trung vị NP_P5..P7={med/1e9:,.1f} tỷ"))
    else:
        out["base_same_q_vs_median_p5_p7"] = "không đủ dữ liệu"
    neg = [f"P{i}" for i in (1, 2, 3, 4) if np_[i] is not None and np_[i] <= 0]
    if neg:
        flags.append(_f("QUY_LO_TRONG_NEN", "NP ≤ 0 ở " + ",".join(
            f"{q}={np_[int(q[1])]/1e9:,.1f} tỷ" for q in neg)))

    if is_bank:
        out["revenue_yoy"] = "không áp dụng cho ngân hàng"
        out["cfo_vs_np"] = "không áp dụng cho ngân hàng (CFO NH phản ánh huy động/cho vay)"
        out["working_capital"] = "không áp dụng cho ngân hàng"
        out["non_operating_proxy"] = "không áp dụng cho ngân hàng (EBITM=0)"
        if missing:
            flags.append(_f("FIN_NA", "thiếu " + ", ".join(missing)))
        return out, flags

    rev0, rev4 = _num(r.get("Revenue_P0")), _num(r.get("Revenue_P4"))
    missing += [n for n, v in (("Revenue_P0", rev0), ("Revenue_P4", rev4)) if v is None]
    if rev4 is not None and rev4 <= 0:
        missing.append(f"Revenue_P4={rev4:g} (≤0, không tính được tăng trưởng)")
    rev_g = (rev0 / rev4 - 1) if rev0 is not None and rev4 and rev4 > 0 else None
    out["revenue_yoy"] = rev_g if rev_g is not None else "không đủ dữ liệu"
    notes = out["data_notes"] = []

    cfo = [_num(r.get(f"CF_OA_P{i}")) for i in range(4)]
    if all(v is not None for v in cfo) and all(v is not None for v in np_[:4]):
        s_cfo, s_np = sum(cfo), sum(np_[:4])
        out["cfo_vs_np"] = {"cfo_4q_vnd": s_cfo, "np_4q_vnd": s_np,
                            "ratio": (s_cfo / s_np) if s_np > 0 else None,
                            "cfo_p0_vnd": cfo[0], "np_p0_vnd": np_[0],
                            # 2 quý gần nhất (chỉ hiển thị, KHÔNG sinh cờ ⇒ không đổi flags_hash): ΣCFO 4Q
                            # có thể che 1 quý rất xấu gần đây
                            "cfo_2q_vnd": cfo[0] + cfo[1], "np_2q_vnd": np_[0] + np_[1]}
        if s_np > 0 and s_cfo < EQ_CFO_NP_MIN * s_np:
            flags.append(_f("EQ_CFO_YEU", f"ΣCF_OA 4Q={s_cfo/1e9:,.1f} tỷ < {EQ_CFO_NP_MIN:.0%} × "
                                          f"ΣNP 4Q={s_np/1e9:,.1f} tỷ"))
    else:
        out["cfo_vs_np"] = "không đủ dữ liệu"
        flags.append(_f("FIN_NA", f"thiếu CF_OA_P0..P3 hoặc NP_P0..P3 (CF_OA={cfo})"))

    npm, ebm = _num(r.get("NPM_P0")), _num(r.get("EBITM_P0"))
    missing += [n for n, v in (("NPM_P0", npm), ("EBITM_P0", ebm)) if v is None]
    if npm == 0 and ebm == 0:
        out["non_operating_proxy"] = "không áp dụng (NPM_P0 = EBITM_P0 = 0)"
    elif npm is not None and ebm is not None:
        out["non_operating_proxy"] = {"NPM_P0": npm, "EBITM_P0": ebm,
                                      "note": "ticker_financial KHÔNG có cột LNTT/thu nhập khác ⇒ "
                                              "không đo được % thu nhập khác/LNTT; dùng proxy NPM>EBITM"}
        if npm > ebm:
            flags.append(_f("EQ_NGOAI_HOAT_DONG", f"NPM_P0={npm:.1%} > EBITM_P0={ebm:.1%}"))
    else:
        out["non_operating_proxy"] = "không đủ dữ liệu (NPM_P0/EBITM_P0 trống)"

    wc = {}
    prev = None                 # dòng CÙNG KỲ năm trước theo NHÃN quý (không tin vị trí: có thể trùng/thiếu quý)
    q = str(r.get("quarter") or "")
    if len(q) == 6 and q[:4].isdigit() and q[4] == "Q":
        yoy_q = f"{int(q[:4]) - 1}{q[4:]}"
        prev = next((x for x in rows[1:] if str(x.get("quarter")) == yoy_q), None)
    for key, col, code in (("receivables", "AR_P0", "EQ_PHAI_THU_TANG"),
                           ("inventory", "Inventory_P0", "EQ_TON_KHO_TANG")):
        cur = _num(r.get(col))
        old = _num(prev.get(col)) if prev else (_num(r.get("Inventory_P4")) if col == "Inventory_P0" else None)
        if cur is None:
            missing.append(col)
        if old is None:
            missing.append(f"{col} cùng kỳ năm trước" + ("" if prev or col == "Inventory_P0" else
                                                      " (không có dòng quý cùng kỳ)"))
        if cur is None or old is None:
            wc[key] = "không đủ dữ liệu"
            continue
        if cur == 0 and old == 0:
            wc[key] = "không áp dụng (=0 cả hai kỳ, vd dịch vụ không có tồn kho)"
            continue
        if rev_g is None:
            wc[key] = "không đủ dữ liệu"       # Revenue thiếu đã vào `missing`
            continue
        if old == 0:                           # từ 0 lên >0: tăng vô hạn — không tính được %, vẫn đưa user xem
            wc[key] = {"now_vnd": cur, "year_ago_vnd": old, "yoy": None, "gap_vs_revenue": None}
            flags.append(_f(code, f"{col} từ 0 lên {cur:,.0f} (doanh thu YoY {rev_g:+.0%})"
                            + (f" — {AR_BASIS_NOTE}" if col == "AR_P0" else "")))
            continue
        g = cur / old - 1
        wc[key] = {"now_vnd": cur, "year_ago_vnd": old, "yoy": g, "gap_vs_revenue": g - rev_g}
        if g - rev_g > EQ_WC_GAP_PP:
            flags.append(_f(code, f"{col} YoY {g:+.0%} vs doanh thu YoY {rev_g:+.0%}"
                            + (f" — {AR_BASIS_NOTE}" if col == "AR_P0" else "")))
    if isinstance(wc.get("receivables"), dict):
        wc["receivables"]["basis"] = AR_BASIS_NOTE
    for k in ("DSO", "DIO"):
        a, b = _num(r.get(f"{k}_P0")), _num(r.get(f"{k}_P4"))
        wc[k] = {"P0": a, "P4": b} if a is not None and b is not None else "không đủ dữ liệu"
    ar = wc.get("receivables")
    dso = wc.get("DSO")
    if isinstance(ar, dict) and ar.get("yoy") is not None and isinstance(dso, dict) and dso["P4"]:
        dd_ = dso["P0"] / dso["P4"] - 1
        # DSO ~ AR/doanh thu ⇒ hướng DSO KỲ VỌNG = (1+AR YoY)/(1+DT YoY)-1, không phải dấu của AR YoY
        # (AR +50% mà DT +80% thì DSO GIẢM là đúng, không phải mâu thuẫn — ca MSR 24/10)
        exp_ = (1 + ar["yoy"]) / (1 + rev_g) - 1 if rev_g is not None and rev_g > -1 else ar["yoy"]
        if abs(exp_) > 0.10 and abs(dd_) > 0.10 and (exp_ > 0) != (dd_ > 0):
            rg_s = f"{rev_g:+.0%}" if rev_g is not None else "n/a"
            notes.append(f"DỮ LIỆU MÂU THUẪN: phải thu thô YoY {ar['yoy']:+.0%} (doanh thu {rg_s}, "
                         f"DSO kỳ vọng {exp_:+.0%}) nhưng DSO vendor "
                         f"P0 {dso['P0']:.1f} vs P4 {dso['P4']:.1f} ({dd_:+.0%}) đi NGƯỢC chiều — "
                         "kiểm tra nguồn trước khi tin cả hai")
    out["working_capital"] = wc
    if missing:
        flags.append(_f("FIN_NA", "thiếu " + ", ".join(missing)))
    return out, flags


def _f(code, evidence):
    assert code in FLAG_CODES, code
    return {"code": code, "evidence": str(evidence)[:500],
            "severity": "WARNING" if code in WARNING_ONLY else "FLAG",
            "meaning": FLAG_CODES[code]}


# user chốt 2026-10-24 (phương án A, sau Taylor dcf_rich_outlook_20261024 + rerun, quant-skeptic CONFIRMED số đo):
# DCF RICH chỉ là CỜ (đòi dcf_override_reason / ack) khi RICH SÂU (MoS < -100%), KHÔNG miễn theo ROE;
# RICH nhẹ (-100%..0) không mang thông tin trong nghiên cứu ⇒ chỉ cảnh báo trong pack['warnings'], không đổi status.
DCF_RICH_DEEP_MOS = -1.0


def _rich_deep(dcf):
    """True nếu RICH sâu HOẶC không đọc được MoS HOẶC MoS > 0 (RICH mà MoS dương = dữ liệu mâu thuẫn).
    Fail-closed: thiếu/lạ bằng chứng ⇒ vẫn cờ."""
    mos = _num(dcf.get("margin_of_safety"))
    return mos is None or mos < DCF_RICH_DEEP_MOS or mos > 0


def soft_warnings(ev):
    """Cảnh báo KHÔNG đổi status/flags_hash (hiển thị cho user): RICH nhẹ kèm số."""
    out = []
    dcf = (ev.get("valuation") or {}).get("dcf")
    if isinstance(dcf, dict) and dcf.get("status") == "RICH" and not _rich_deep(dcf):
        d = ev.get("dd") or {}
        roe = None
        m = re.search(r"ROE5Y\s*(-?[\d.]+)%", str(d.get("fundamentals") or "")) if isinstance(d, dict) else None
        if m:
            roe = m.group(1)
        out.append({"code": "DCF_RICH_NHE", "severity": "WARNING",
                    "evidence": f"DCF RICH nhẹ: MoS {_num(dcf.get('margin_of_safety'))*100:.1f}% (ngưỡng cờ < {DCF_RICH_DEEP_MOS*100:.0f}%)"
                                f"{', ROE5Y ' + roe + '%' if roe else ''} — nghiên cứu 24/10: RICH nhẹ không khác đối chứng về LN/drift"})
    return out


# ── (a) DD cơ bản → cờ ───────────────────────────────────────────────────────────────────────
def basic_flags(ev):
    """ev = run_dd() + valuation + rating + forensic. Trả list cờ. Thuần — selfcheck gọi thẳng."""
    flags = []
    d = ev.get("dd") or {}
    if not isinstance(d, dict) or d.get("error"):
        flags.append(_f("DD_KHONG_CHAY_DUOC", (d or {}).get("error") if isinstance(d, dict) else repr(d)))
        d = d if isinstance(d, dict) else {}
    for code in d.get("red_flags") or []:
        if code == "DD_KHONG_CHAY_DUOC" and any(f["code"] == code for f in flags):
            continue
        flags.append(_f(code, d.get("liquidity") or d.get("signal_mechanics") or "")
                     if code in FLAG_CODES else
                     _f("DD_KHONG_CHAY_DUOC", f"mã cờ DD lạ {code!r} — coi như cờ"))
    adv = _num(ev.get("adv"))
    if adv is None:
        flags.append(_f("ADV_NA", ev.get("adv_err") or "adv None"))
    elif adv < ev.get("adv_thin_vnd", 2e9) and "THANH_KHOAN_CHET" not in (d.get("red_flags") or []):
        flags.append(_f("THANH_KHOAN_MONG", f"ADV3T {adv/1e9:,.2f} tỷ/phiên (data {ev.get('adv_date')})"))
    if d.get("in_universe") is None and not d.get("error"):
        flags.append(_f("UNIVERSE_NA", f"universe_source={d.get('universe_source')}"))
    qf = d.get("quality_flag")
    if d.get("in_universe") and qf and qf != "QUALITY_OK":
        flags.append(_f("CO_CHAT_LUONG_UNIVERSE", f"quality_flag={qf}"))
    if not ev.get("anomaly_ok"):
        flags.append(_f("ANOMALY_NA", ev.get("anomaly_err")))
    elif ev.get("anomaly_rec"):
        a = ev["anomaly_rec"]
        flags.append(_f("BAT_THUONG_ANOMALY", f"tier={a.get('tier')} reasons={a.get('reasons')} "
                                              f"last_alert={a.get('last_alert')}"))
    if not ev.get("insider_ok"):
        flags.append(_f("INSIDER_NA", "_insider_scan trả None (lỗi/nguồn cũ)"))
    elif d.get("insider_net_sell"):
        i = d["insider_net_sell"]
        flags.append(_f("INSIDER_BAN_RONG", f"bán ròng {i.get('net_sell_pct', 0)*100:.2f}% CPLH/"
                                            f"{i.get('window_days')} ngày, {i.get('n_sellers')} người bán "
                                            f"vs {i.get('n_buyers')} mua, lần cuối {i.get('last_sell_date')}"))
    if not ev.get("corp_ok"):
        flags.append(_f("CORP_FEED_NA", "_corp_action_feed_ok=False"))
    elif d.get("upcoming_exdate"):
        x = d["upcoming_exdate"]
        flags.append(_f("EXDATE_SAP_TOI", f"GDKHQ {x.get('exright_date')} ({x.get('days_to_ex')} ngày), "
                                          f"{x.get('value_per_share')}đ/cp, yield {x.get('gross_yield_pct')}%"))
    rt = ev.get("rating") or {}
    if rt.get("err") and not (rt.get("fail") or rt.get("stale")):
        flags.append(_f("RATING_NA", rt["err"]))
    if rt.get("fail"):
        flags.append(_f("RATING_8L_FAIL", rt["fail"].get("reason")))
    if rt.get("stale"):
        s = rt["stale"]
        flags.append(_f("RATING_8L_CU", f"rating {s.get('rating')} ngày {s.get('rating_date')} < "
                                        f"Release_Date {s.get('release_date')}"))
    fx = ev.get("forensic") or {}
    if fx.get("err"):
        flags.append(_f("FORENSIC_NA", fx["err"]))
    for x in fx.get("dropped") or []:
        flags.append(_f("FORENSIC_BANNED", f"{x.get('kind')}: {x.get('reason')}"))
    for x in fx.get("rows") or []:
        if str(x.get("flag_type")).strip().lower() in LEGAL_FLAG_TYPES:
            flags.append(_f("PHAP_LY_WARNING", f"{x.get('flag_type')} {x.get('date')}: {x.get('note')}"))
        elif str(x.get("severity")).strip().lower() != "exclude":
            flags.append(_f("FORENSIC_WATCH", f"{x.get('flag_type')}/{x.get('severity')} {x.get('date')}: "
                                              f"{x.get('note')}"))
    val = ev.get("valuation") or {}
    dcf = val.get("dcf")
    if isinstance(dcf, dict) and dcf.get("status") == "RICH" and _rich_deep(dcf):
        flags.append(_f("DCF_RICH", val.get("text") or "status=RICH"))
    computed = isinstance(dcf, dict) and dcf.get("status") in ("CHEAP", "RICH", "FAIR")
    if not computed and not val.get("alt_lens"):
        flags.append(_f("DINH_GIA_NA", val.get("err") or val.get("text") or "dcf None, alt lens rỗng"))
    return flags


def find_release(rows, asof):
    """(release_date str|None, lý do). rows mới → cũ."""
    if not rows:
        return None, "không có dòng ticker_financial ≤ asof"
    rel = str(rows[0].get("Release_Date") or "")[:10]
    try:
        age = (dt.date.fromisoformat(str(asof)[:10]) - dt.date.fromisoformat(rel)).days
    except ValueError:
        return None, f"Release_Date đọc không được: {rows[0].get('Release_Date')!r}"
    if age > FIN_FRESH_MAX_DAYS:
        return None, f"Release_Date gần nhất {rel} cách asof {age} ngày > {FIN_FRESH_MAX_DAYS}"
    return rel, ""


def build_pack(ticker, asof, cand=None, release_date=None, macro_note=None, sources=None):
    """Dựng 1 gói. KHÔNG raise: lỗi ở bất kỳ nguồn nào ⇒ cờ *_NA ⇒ FLAG."""
    s = sources or {}
    ticker = ticker.strip().upper()
    flags, errors = [], {}

    def _try(name, fn, *a):
        try:
            return fn(*a)
        except Exception as e:                              # fail-closed, có bằng chứng
            errors[name] = f"{type(e).__name__}: {str(e)[:200]}"
            return None

    rows = _try("fin", s.get("fin", fetch_fin_rows), ticker, asof)
    rel_auto, why = find_release(rows or [], asof)
    rel = release_date or rel_auto
    if rows is None:
        flags.append(_f("FIN_NA", errors.get("fin")))
    if not rel:
        flags.append(_f("RELEASE_NA", why))
    elif release_date and rel_auto and rel_auto != release_date:
        flags.append(_f("RELEASE_NA", f"--release-date {release_date} ≠ Release_Date mới nhất {rel_auto}"))
    ev = _try("dd", s.get("dd", run_dd), ticker, asof) or {"dd": {"error": errors.get("dd")}}
    v = _try("valuation", s.get("valuation", run_valuation), ticker, asof)
    ev["valuation"] = ({"dcf": v[0], "text": v[1], "alt_lens": v[2], "err": v[3]} if v else
                       {"err": errors.get("valuation")})
    ev["rating"] = _try("rating", s.get("rating", run_rating), ticker, asof, rel or asof) or \
        {"err": errors.get("rating")}
    ev["forensic"] = _try("forensic", s.get("forensic", run_forensic), ticker, asof) or \
        {"err": errors.get("forensic")}
    flags += basic_flags(ev)
    iss = _try("capital_raise", s.get("capraise", fetch_issuance), ticker, asof)
    if iss is None:
        flags.append(_f("CAPITAL_RAISE_NA", errors.get("capital_raise")))
        cr_warn = []
    else:
        cr_warn = capital_raise_eval(rows or [], iss, asof)[1]   # [0] (cờ) luôn rỗng: tăng vốn chỉ là WARNING (user chọn (b) 29/10)

    d = ev.get("dd") or {}
    icb = (d.get("yield_floor") or {}).get("icb_code") if isinstance(d, dict) else None
    is_bank = _num(icb) == BANK_ICB
    if rows and not is_bank and all(_num(rows[0].get(c)) in (0, None) for c in ("EBITM_P0", "AR_P0", "Inventory_P0")):
        is_bank = None                          # không rõ ngành mà cột = 0/NULL ⇒ coi như thiếu dữ liệu
    eq, eq_flags = earnings_quality(rows or [], bool(is_bank))
    if is_bank is None:
        eq_flags.append(_f("FIN_NA", "EBITM/AR/Inventory = 0 hoặc NULL nhưng không xác nhận được là ngân hàng"))
    flags += [f for f in eq_flags if not (f["code"] == "QUY_LO_TRONG_NEN"
                                         and any(x["code"] == "SURPRISE_PHONG_CO_HOC" for x in flags))]
    if is_bank:
        eq["bank"] = _try("bank", s.get("bank", read_bank_ratios), ticker) or {"note": "không đủ dữ liệu"}

    # gộp cờ trùng mã (giữ bằng chứng đầu tiên)
    seen, uniq = set(), []
    for f in flags:
        k = (f["code"], f["evidence"])
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    status = "CLEARED" if not uniq else "FLAG"
    pack = {
        "schema_version": SCHEMA_VERSION,
        "ticker": ticker, "book": "LAG", "release_date": rel, "asof": str(asof),
        "generated_at": dt.datetime.now(_ICT).isoformat(timespec="seconds"),
        "generator": "mike/bin/lag_dd_pack.py",
        "candidate": cand or {},
        "status": status,
        "flags": uniq, "flags_hash": flags_hash(uniq),
        "warnings": soft_warnings(ev) + cr_warn,
        "flag_definition": "CLEARED ⇔ flags rỗng; danh sách mã cờ = lag_dd_pack.FLAG_CODES",
        "dd_basic": _jsonable({k: ev.get(k) for k in ("dd", "adv", "adv_date", "adv_err", "insider_ok",
                                                      "corp_ok", "anomaly_rec", "anomaly_err",
                                                      "valuation", "rating", "forensic")}),
        "earnings_quality": _jsonable(eq),
        "macro_note": (s.get("macro", read_macro_note))(macro_note),
        "source_errors": errors,
        "plan_contract": "DollarBill CHỈ đưa vào orders[] mã có status=CLEARED HOẶC ack PROCEED "
                         "(decided_by=user) trong data/lag_dd/ack.json; FLAG chưa ack ⇒ ngoài plan.",
    }
    return pack


def pack_path(ticker, release_date):
    return os.path.join(dd_dir(), f"{ticker}_{release_date or 'NA'}.json")


def write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, default=str)
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


# ── ứng viên ─────────────────────────────────────────────────────────────────────────────────
def candidates_from_csv(signal_date=None):
    """Ứng viên LAG chưa qua cửa sổ của CSV khuyến nghị (due_today + upcoming). (list, lỗi|None)."""
    import filter_lag_entry_window as flw
    from trading_bot.vn_market import next_trading_day
    csv_path, sig = (None, signal_date) if signal_date else flw.latest_recs_csv()
    if not sig:
        return [], "không thấy CSV khuyến nghị"
    plan_date = next_trading_day(flw._d(sig))
    res = flw.filter_window(plan_date, signal_date=sig, csv_path=csv_path, anchor_fetcher=None)
    if res.get("error"):
        return [], res["error"]
    out = []
    for k in ("due_today", "upcoming_next_plans"):
        for it in res.get(k, []):
            out.append({"ticker": it["ticker"], "play_type": it.get("tier"), "status_raw": it.get("status_raw"),
                        "entry_date": it.get("entry_date") or it.get("entry_date_est"),
                        "entry_window_day": it.get("entry_window_day"), "signal_date": res.get("signal_date"),
                        "csv": res.get("csv"), "bucket": k})
    if res.get("unparsed"):
        return out, f"{len(res['unparsed'])} dòng LAG không phân loại được: " + \
            ",".join(i["ticker"] for i in res["unparsed"])
    return out, None


# ── thông báo ────────────────────────────────────────────────────────────────────────────────
def _deadline(entry_date):
    """Vòng lập plan cuối cùng trước phiên vào lệnh. Vào lệnh thứ Hai: vòng CN 19:00 chỉ chạy mùa
    BCTC (sunday_plan_round.sh tự gate) ⇒ nêu cả mốc thứ Sáu. Ngày lễ giữa tuần: chưa xử lý (ghi rõ)."""
    try:
        e = dt.date.fromisoformat(str(entry_date)[:10])
    except (TypeError, ValueError):
        return "19:00 ICT ngày lập plan (không xác định được ngày vào lệnh)"
    d = e - dt.timedelta(days=1)
    if d.weekday() == 6:
        fri = e - dt.timedelta(days=3)
        return (f"19:00 ICT CN {d.isoformat()} (vòng plan CN mùa BCTC cho phiên {e}; ngoài mùa: "
                f"19:00 T6 {fri.isoformat()})")
    return f"19:00 ICT {d.isoformat()} (vòng lập plan cho phiên {e}; lệch nếu {d} là ngày lễ)"


def render_message(packs):
    lines = ["🧾 **DD trước plan — book LAG** (CLEARED = không có cờ nào; FLAG chưa trả lời ⇒ ĐỨNG NGOÀI plan)"]
    for p in packs:
        c = p.get("candidate") or {}
        head = f"- **{p['ticker']}** (release {p['release_date']}, vào lệnh ~{c.get('entry_date', '?')}): "
        if p["status"] == "CLEARED":
            lines.append(head + "✅ CLEARED")
            for w in p.get("warnings") or []:
                lines.append(f"    ⚠️ WARNING `{w['code']}` — {w['evidence'][:220]}")
            continue
        lines.append(head + f"🚩 FLAG — {len(p['flags'])} cờ, hash `{p['flags_hash']}` "
                            f"({','.join(sorted({f['code'] for f in p['flags']}))}):")
        for f in p["flags"]:
            mark = "⚠️ WARNING" if f["severity"] == "WARNING" else "•"
            lines.append(f"    {mark} `{f['code']}` — {f['evidence'][:220]}")
        lines.append(f"    ➜ Trả lời trước **{_deadline(c.get('entry_date'))}**: "
                     f"(1) nghiên cứu thêm · (2) loại · (3) mua dù có cờ. Không trả lời = đứng ngoài plan. "
                     f"(Ack gắn hash `{p['flags_hash']}`; gói đổi cờ sau tin này ⇒ ack bị từ chối, sẽ hỏi lại.)")
        for w in p.get("warnings") or []:
            lines.append(f"    ⚠️ WARNING `{w['code']}` — {w['evidence'][:220]}")
        for note in (p.get("earnings_quality") or {}).get("data_notes") or []:
            lines.append(f"    ℹ️ {note}")
        cn = (p.get("earnings_quality") or {}).get("cfo_vs_np")
        if isinstance(cn, dict) and cn.get("cfo_2q_vnd") is not None:
            lines.append(f"    ℹ️ CFO/LNST: 4Q {cn['cfo_4q_vnd']/1e9:,.1f}/{cn['np_4q_vnd']/1e9:,.1f} tỷ · "
                         f"2Q gần nhất {cn['cfo_2q_vnd']/1e9:,.1f}/{cn['np_2q_vnd']/1e9:,.1f} tỷ")
        mn = p.get("macro_note") or {}
        if mn.get("path"):
            lines.append(f"    vĩ mô: {mn['path']}")
    lines.append("Gói đầy đủ: `data/lag_dd/<mã>_<release>.json`.")
    return "\n".join(lines)


def _state_path():
    return os.path.join(_env("MIKE_LAG_DD_STATE_DIR", os.path.join(ROOT, "state", "lag_dd_notify")),
                        "sent.json")


def _nkey(p):
    k = f"{p['ticker']}|{p['release_date']}|{p['flags_hash']}|{p['status']}"
    w = sorted({x["code"] for x in p.get("warnings") or []})
    return k + ("|W:" + ",".join(w) if w else "")          # warning mới trên gói CLEARED ⇒ gửi lại


def notify(packs, dry_run=False):
    """Gửi gói CHƯA gửi (theo khoá ticker|release|flags_hash|status). Trả (n_gửi, msg)."""
    sp = _state_path()
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    with open(sp + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(sp, encoding="utf-8") as fh:
                sent = set(json.load(fh).get("sent", []))
        except (OSError, ValueError):
            sent = set()
        new = [p for p in packs if _nkey(p) not in sent]
        if not new:
            return 0, ""
        msg = render_message(new)
        if dry_run:
            return len(new), msg
        cmd = [_env("MIKE_LAG_DD_NOTIFY", os.path.join(HERE, "notify_thread.sh")), msg, CHANNEL]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=SUBPROC_TIMEOUT_S)
            rc, err = r.returncode, (r.stderr or r.stdout or "").strip()[:200]
        except (OSError, subprocess.TimeoutExpired) as e:
            rc, err = 1, f"{type(e).__name__}: {e}"
        if rc != 0:
            print(f"  ❌ notify rc={rc}: {err} — CHƯA ghi state, lượt sau gửi lại", file=sys.stderr)
            return -1, msg
        write_atomic(sp, {"sent": sorted(sent | {_nkey(p) for p in new})})
        return len(new), msg


def _macro_map(items):
    m, default = {}, None
    for it in items or []:
        if "=" in it and not os.path.exists(it):
            k, v = it.split("=", 1)
            m[k.strip().upper()] = v
        else:
            default = it
    return m, default


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--signal-date", help="CSV khuyến nghị golive (mặc định: mới nhất)")
    ap.add_argument("--tickers", help="danh sách mã thủ công, phân tách dấu phẩy (bỏ qua CSV)")
    ap.add_argument("--release-date", help="ép release_date (chỉ dùng với --tickers); lệch BQ ⇒ cờ RELEASE_NA")
    ap.add_argument("--entry-date", help="ngày vào lệnh (chỉ dùng với --tickers, để tính hạn trả lời)")
    ap.add_argument("--asof", help="ngày dữ liệu DD (mặc định hôm nay ICT)")
    ap.add_argument("--macro-note", action="append", help="PATH (mọi mã) hoặc TICKER=PATH")
    ap.add_argument("--notify", action="store_true", help=f"gửi 1 tin vào channel {CHANNEL}")
    ap.add_argument("--dry-run", action="store_true", help="in tin thay vì gửi, KHÔNG ghi state notify")
    ap.add_argument("--no-write", action="store_true", help="không ghi data/lag_dd")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    asof = a.asof or today_ict().isoformat()
    if a.tickers:
        cands = [{"ticker": t.strip().upper(), "entry_date": a.entry_date, "bucket": "manual"}
                 for t in a.tickers.split(",") if t.strip()]
        cerr = None
    else:
        try:
            cands, cerr = candidates_from_csv(a.signal_date)
        except Exception as e:
            print(f"lỗi đọc ứng viên: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    if cerr:
        print(f"  ⚠ {cerr}", file=sys.stderr)
    if not cands:
        print("không có ứng viên LAG nào" + (f" ({cerr})" if cerr else ""), file=sys.stderr)
        return 1 if cerr else 0
    mmap, mdefault = _macro_map(a.macro_note)
    packs = []
    for c in cands:
        p = build_pack(c["ticker"], asof, cand=c,
                       release_date=a.release_date if a.tickers else None,
                       macro_note=mmap.get(c["ticker"], mdefault))
        if not a.no_write:
            path = pack_path(p["ticker"], p["release_date"])
            try:
                write_atomic(path, p)
            except OSError as e:
                print(f"lỗi ghi {path}: {e}", file=sys.stderr)
                return 1
            p["_path"] = os.path.relpath(path, WC_ROOT)
        packs.append(p)
    for p in packs:
        codes = ",".join(f["code"] for f in p["flags"]) or "-"
        print(f"{p['ticker']:5s} release={p['release_date']} status={p['status']:7s} flags={codes} "
              f"{p.get('_path', '')}")
    if a.json:
        print(json.dumps(packs, ensure_ascii=False, indent=1, default=str))
    if a.notify or a.dry_run:
        n, msg = notify(packs, dry_run=a.dry_run)
        if a.dry_run and msg:
            print("\n--- TIN SẼ GỬI (dry-run) ---\n" + msg)
        if n < 0:
            return 1
    return 2 if any(p["status"] != "CLEARED" for p in packs) else 0


if __name__ == "__main__":
    sys.exit(main())
