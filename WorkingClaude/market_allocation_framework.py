# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
"""
market_allocation_framework.py
================================
He thong danh gia thi truong tong hop -> Quyet dinh ty trong co phieu / tien mat
Bao gom:
  [A] VNINDEX_PE valuation score (tu VNINDEX.csv)
  [B] Market Phase score (RSI/MACD/CMF/MA200)
  [C] VNI Signal score (BullDvgVNI / BearDvgVNI tu filter.json)
  [D] Lai suat tien gui SBV (domestic rate)
  [E] Chinh sach Fed (USD rate)
  [F] -> Tong hop thanh MARKET SCORE (0-100) -> Allocation strategy
"""

import os, json
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ══════════════════════════════════════════════════════════════════════
# PHAN 1: DU LIEU LICH SU LAI SUAT (nhung moc quan trong)
# ══════════════════════════════════════════════════════════════════════
# SBV deposit rate (12-month, %/year) - moc chinh sach quan trong
# Nguon: SBV + Cafef
SBV_RATE_HISTORY = [
    # (date_from, rate_pct, direction, note)
    ("2012-03-13", 12.0, "CUT",  "SBV cat lai suat tu 14% xuong 12%"),
    ("2012-06-11",  9.0, "CUT",  "Cat xuong 9%"),
    ("2012-09-11",  8.0, "CUT",  "Cat xuong 8%"),
    ("2013-03-26",  7.5, "CUT",  "Cat xuong 7.5%"),
    ("2013-05-13",  7.0, "CUT",  "Cat xuong 7%"),
    ("2013-06-28",  6.5, "CUT",  "Cat xuong 6.5%"),
    ("2014-03-17",  6.0, "CUT",  "Cat xuong 6%"),
    ("2014-10-29",  5.5, "CUT",  "Cat xuong 5.5%"),
    ("2016-06-29",  5.5, "HOLD", "Giu nguyen 5.5%"),
    ("2019-09-16",  5.5, "HOLD", "Giu nguyen"),
    ("2020-03-17",  5.0, "CUT",  "COVID - cat 0.5pp"),
    ("2020-05-13",  4.75,"CUT",  "Cat tiep"),
    ("2020-09-30",  4.0, "CUT",  "Cat xuong 4%"),
    ("2022-09-22",  5.0, "HIKE", "SBV tang lai suat doi pho lam phat/USD"),
    ("2022-10-25",  6.0, "HIKE", "Tang manh len 6%"),
    ("2023-03-15",  5.5, "CUT",  "Cat 0.5pp"),
    ("2023-05-25",  5.0, "CUT",  "Cat xuong 5%"),
    ("2023-06-19",  4.75,"CUT",  "Cat xuong 4.75%"),
    ("2024-01-01",  4.75,"HOLD", "Giu 4.75%"),
    ("2024-06-01",  4.5, "CUT",  "Cat xuong 4.5%"),
    ("2025-01-01",  4.5, "HOLD", "Giu 4.5%"),
    ("2026-01-01",  4.5, "HOLD", "Giu 4.5% - dieu kien kinh te on"),
]

# Fed Funds Rate (upper bound, %/year)
FED_RATE_HISTORY = [
    ("2014-01-01", 0.25, "HOLD", "QE tapering"),
    ("2015-12-17", 0.50, "HIKE", "Dau hike cycle"),
    ("2016-12-15", 0.75, "HIKE", "+0.25pp"),
    ("2017-03-16", 1.00, "HIKE", "+0.25pp"),
    ("2017-06-15", 1.25, "HIKE", "+0.25pp"),
    ("2017-12-14", 1.50, "HIKE", "+0.25pp"),
    ("2018-03-22", 1.75, "HIKE", "+0.25pp"),
    ("2018-06-14", 2.00, "HIKE", "+0.25pp"),
    ("2018-09-27", 2.25, "HIKE", "+0.25pp"),
    ("2018-12-20", 2.50, "HIKE", "Peak 2018"),
    ("2019-08-01", 2.25, "CUT",  "Phong ngua suy thoai"),
    ("2019-09-19", 2.00, "CUT",  "Cat tiep"),
    ("2019-10-31", 1.75, "CUT",  "Cat tiep"),
    ("2020-03-03", 1.25, "CUT",  "COVID emergency"),
    ("2020-03-16", 0.25, "CUT",  "Zero rate COVID"),
    ("2022-03-17", 0.50, "HIKE", "Bat dau hike chong lam phat"),
    ("2022-05-05", 1.00, "HIKE", "+0.5pp"),
    ("2022-06-16", 1.75, "HIKE", "+0.75pp"),
    ("2022-07-28", 2.50, "HIKE", "+0.75pp"),
    ("2022-09-22", 3.25, "HIKE", "+0.75pp"),
    ("2022-11-03", 4.00, "HIKE", "+0.75pp"),
    ("2022-12-15", 4.50, "HIKE", "+0.5pp"),
    ("2023-02-02", 4.75, "HIKE", "+0.25pp"),
    ("2023-03-23", 5.00, "HIKE", "+0.25pp"),
    ("2023-05-04", 5.25, "HIKE", "+0.25pp"),
    ("2023-07-27", 5.50, "HIKE", "Peak - highest since 2001"),
    ("2024-09-19", 5.00, "CUT",  "Bat dau cycle cat"),
    ("2024-11-08", 4.75, "CUT",  "Cat tiep"),
    ("2024-12-19", 4.50, "CUT",  "Cat 0.25pp"),
    ("2025-01-29", 4.50, "HOLD", "Tam dung - cho du lieu"),
    ("2025-06-01", 4.25, "CUT",  "Cat tiep voi lam phat giam"),
    ("2025-12-01", 4.00, "CUT",  "Cat them"),
    ("2026-01-01", 4.00, "HOLD", "Giu 4% - chua ro xu huong"),
]

def get_rate_at_date(rate_history, target_date):
    """Tra ve lai suat + direction tai ngay target_date"""
    target = pd.Timestamp(target_date)
    rate_df = pd.DataFrame(rate_history, columns=["date", "rate", "direction", "note"])
    rate_df["date"] = pd.to_datetime(rate_df["date"])
    rate_df = rate_df.sort_values("date")
    valid = rate_df[rate_df["date"] <= target]
    if len(valid) == 0:
        return None, None, None
    last = valid.iloc[-1]
    # Xac dinh trend: so sanh voi 3 moc truoc
    trend_window = valid.tail(4)
    if len(trend_window) >= 2:
        rates = trend_window["rate"].values
        direction = trend_window["direction"].values
        # Cut: 2/3 lan cuoi la CUT
        recent_dirs = direction[-3:]
        if sum(d == "CUT" for d in recent_dirs) >= 2:
            trend = "CUTTING"
        elif sum(d == "HIKE" for d in recent_dirs) >= 2:
            trend = "HIKING"
        else:
            trend = "HOLD"
    else:
        trend = last["direction"]
    return float(last["rate"]), trend, last["note"]

# ══════════════════════════════════════════════════════════════════════
# PHAN 2: SCORING FUNCTIONS (0-100 diem)
# ══════════════════════════════════════════════════════════════════════

def score_pe_valuation(pe_current, pe_percentile):
    """
    [A] VNINDEX_PE Valuation Score (0-30 diem)
    Dua tren muc PE tuyet doi va percentile lich su
    """
    if pd.isna(pe_current):
        return 15, "UNKNOWN"

    # Diem theo PE tuyet doi
    if pe_current < 10:
        abs_score = 30
        zone = "SIEU_RE (<10x)"
    elif pe_current < 12:
        abs_score = 25
        zone = "RAT_RE (10-12x)"
    elif pe_current < 14:
        abs_score = 18
        zone = "RE (12-14x)"
    elif pe_current < 16:
        abs_score = 12
        zone = "BINH_THUONG (14-16x)"
    elif pe_current < 18:
        abs_score = 7
        zone = "CAO (16-18x)"
    elif pe_current < 20:
        abs_score = 3
        zone = "RAT_CAO (18-20x)"
    else:
        abs_score = 0
        zone = "NGUY_HIEM (>20x)"

    # Dieu chinh theo percentile lich su
    if pe_percentile < 0.20:
        pct_adj = +3
    elif pe_percentile < 0.40:
        pct_adj = +1
    elif pe_percentile < 0.60:
        pct_adj = 0
    elif pe_percentile < 0.80:
        pct_adj = -2
    else:
        pct_adj = -4

    return max(0, min(30, abs_score + pct_adj)), zone

def score_market_phase(rsi, macd, cmf, close, ma200):
    """
    [B] Market Phase Score (0-25 diem)
    Dua tren vi tri gia va cac chi so ky thuat
    """
    if pd.isna(rsi) or pd.isna(close) or pd.isna(ma200):
        return 12, "UNKNOWN"

    above_ma200 = close > ma200
    score = 0
    phase = ""

    if not above_ma200:
        if rsi < 0.30:
            score = 24
            phase = "BEAR_BOTTOM"
        elif rsi < 0.45:
            score = 20
            phase = "ACCUMULATION"
        elif not pd.isna(macd) and macd > 0 and rsi > 0.40:
            score = 16
            phase = "RECOVERY_BELOW_MA200"
        else:
            score = 14
            phase = "SIDEWAYS_BELOW"
    else:  # above MA200
        if not pd.isna(macd) and macd < 0:
            score = 16
            phase = "RECOVERY"
        elif rsi < 0.50:
            score = 14
            phase = "BULL_EARLY"
        elif rsi < 0.65:
            score = 10
            phase = "BULL_STRONG"
        elif rsi < 0.80:
            score = 5
            phase = "DISTRIBUTION_WARNING"
        else:
            score = 1
            phase = "DISTRIBUTION_DANGER"

    # CMF adjustment
    if not pd.isna(cmf):
        if cmf > 0.1:
            score = min(25, score + 2)
        elif cmf < -0.1:
            score = max(0, score - 2)

    return score, phase

def score_vni_signal(row):
    """
    [C] VNI Technical Signal Score (0-20 diem)
    Evaluate BullDvgVNI / BearDvgVNI tu filter.json
    Dung truc tiep cot trong VNINDEX.csv
    """
    try:
        rsi_min1w  = row.get("D_RSI_Min1W", np.nan)
        rsi_min3m  = row.get("D_RSI_Min3M", np.nan)
        rsi_mint3  = row.get("D_RSI_MinT3", np.nan)
        rsi_max1w  = row.get("D_RSI_Max1W", np.nan)
        rsi_max3m  = row.get("D_RSI_Max3M", np.nan)
        rsi_t1w    = row.get("D_RSI_T1W", np.nan)
        rsi        = row.get("D_RSI", np.nan)
        macd       = row.get("D_MACDdiff", np.nan)
        cmf        = row.get("D_CMF", np.nan)
        c_l1m      = row.get("C_L1M", np.nan)
        c_l1w      = row.get("C_L1W", np.nan)
        close      = row.get("Close", np.nan)
        rsi_min1w_close = row.get("D_RSI_Min1W_Close", np.nan)
        rsi_min3m_close = row.get("D_RSI_Min3M_Close", np.nan)
        rsi_max1w_close = row.get("D_RSI_Max1W_Close", np.nan)
        rsi_max3m_close = row.get("D_RSI_Max3M_Close", np.nan)
        rsi_max1w_macd  = row.get("D_RSI_Max1W_MACD", np.nan)
        rsi_max3m_macd  = row.get("D_RSI_Max3M_MACD", np.nan)

        def safe(a, b, op, val):
            try:
                if op == ">": return float(a)/float(b) > val
                if op == "<": return float(a)/float(b) < val
            except: return False

        # BullDvgVNI1 (filter.json: _BullDvgVNI1)
        bull1 = (
            safe(rsi_min1w, rsi_min3m, ">", 0.9) and
            (not pd.isna(rsi_min1w) and rsi_min1w < 0.6) and
            (not pd.isna(rsi_min3m) and rsi_min3m < 0.4) and
            safe(rsi_min1w_close, rsi_min3m_close, "<", 1.15) and
            (not pd.isna(macd) and macd > 0) and
            (not pd.isna(rsi_mint3) and rsi_mint3 < 0.5) and
            (not pd.isna(rsi_max1w) and rsi_max1w < 0.48) and
            safe(rsi, rsi_t1w, ">", 1.12) and
            (not pd.isna(cmf) and cmf > 0) and
            (not pd.isna(c_l1m) and c_l1m < 1.21) and
            (not pd.isna(c_l1w) and c_l1w < 1.05)
        )

        # BullDvgVNI12 (filter.json: _BullDvgVNI12) - manh hon
        bull12 = (
            safe(rsi_min1w, rsi_min3m, ">", 0.92) and
            (not pd.isna(rsi_min1w) and rsi_min1w < 0.52) and
            (not pd.isna(rsi_min3m) and rsi_min3m < 0.38) and
            safe(rsi_min1w_close, rsi_min3m_close, "<", 1.1) and
            (not pd.isna(macd) and macd > 0) and
            (not pd.isna(rsi_mint3) and rsi_mint3 < 0.56) and
            (not pd.isna(rsi_max1w) and rsi_max1w < 0.64) and
            safe(rsi, rsi_t1w, ">", 1.1) and
            (not pd.isna(cmf) and cmf > 0) and
            (not pd.isna(c_l1m) and c_l1m < 1.2) and
            (not pd.isna(c_l1w) and c_l1w < 1.025)
        )

        # BearDvgVNI2 (filter.json: ~BearDvgVNI2) - tin hieu ban
        bear2 = (
            safe(rsi_max1w, rsi, ">", 1.016) and
            (not pd.isna(rsi_max3m) and rsi_max3m > 0.77) and
            (not pd.isna(rsi_max1w) and rsi_max1w < 0.79) and
            (not pd.isna(rsi_max1w) and rsi_max1w > 0.6) and
            safe(rsi_max1w_close, rsi_max3m_close, ">", 1.008) and
            safe(rsi_max3m_macd, rsi_max1w_macd, ">", 1.1) and
            (not pd.isna(macd) and macd < 0) and
            safe(close, rsi_max3m_close, ">", 0.97) and
            (not pd.isna(rsi_mint3) and rsi_mint3 > 0.5) and
            (not pd.isna(cmf) and cmf < 0.15)
        )

        if bull12:
            return 20, "BULL_DVG_STRONG"
        elif bull1:
            return 16, "BULL_DVG"
        elif bear2:
            return 2, "BEAR_DVG_STRONG"
        else:
            return 10, "NEUTRAL"
    except:
        return 10, "NEUTRAL"

def score_sbv_rate(rate, trend):
    """
    [D] SBV Interest Rate Score (0-15 diem)
    Lai suat thap + dang cat = ung ho thi truong co phieu
    """
    if rate is None:
        return 8, "UNKNOWN"

    # Diem theo muc tuyet doi
    if rate <= 4.0:
        abs_s = 12
    elif rate <= 5.0:
        abs_s = 9
    elif rate <= 6.0:
        abs_s = 6
    elif rate <= 8.0:
        abs_s = 3
    else:
        abs_s = 0

    # Diem theo xu huong (trend)
    if trend == "CUTTING":
        trend_s = 3
        trend_label = "CUTTING (tai san rui ro duoc ung ho)"
    elif trend == "HOLD":
        trend_s = 1
        trend_label = "HOLD (on dinh)"
    else:
        trend_s = 0
        trend_label = "HIKING (ap luc ban ra)"

    return min(15, abs_s + trend_s), f"{rate}% - {trend_label}"

def score_fed_rate(rate, trend):
    """
    [E] Fed Policy Score (0-10 diem)
    Fed cat lai suat -> von chay vao EM (Vietnam huong loi)
    Fed tang manh -> dong USD, von rut khoi EM
    """
    if rate is None:
        return 5, "UNKNOWN"

    if trend == "CUTTING":
        trend_s = 4
        label = "CUTTING -> von EM duoc ung ho"
    elif trend == "HOLD":
        trend_s = 2
        label = "HOLD -> trung tinh"
    else:
        trend_s = 0
        label = "HIKING -> ap luc von rut"

    if rate <= 1.0:
        abs_s = 6
    elif rate <= 2.5:
        abs_s = 5
    elif rate <= 4.0:
        abs_s = 4
    elif rate <= 5.0:
        abs_s = 3
    else:
        abs_s = 1

    return min(10, abs_s + trend_s), f"{rate}% - {label}"

def total_score_to_allocation(score):
    """
    Tong diem (0-100) -> Allocation + Leverage decision
    """
    if score >= 80:
        return {
            "stock_pct": 150,  # co the dung margin 1:0.5
            "cash_pct": -50,
            "leverage": "VAY 1:0.5 (50% margin)",
            "strategy": "CUC KY THUAN LOI - Tang toi da co phieu, co the vay them",
            "color": "XANH_DAM"
        }
    elif score >= 70:
        return {
            "stock_pct": 100,
            "cash_pct": 0,
            "leverage": "VAY 1:1 (100% margin) neu co kinh nghiem",
            "strategy": "RAT THUAN LOI - Full co phieu, co the vay",
            "color": "XANH"
        }
    elif score >= 60:
        return {
            "stock_pct": 85,
            "cash_pct": 15,
            "leverage": "KHONG vay",
            "strategy": "THUAN LOI - Full co phieu, giu it tien mat",
            "color": "XANH_NHAT"
        }
    elif score >= 50:
        return {
            "stock_pct": 70,
            "cash_pct": 30,
            "leverage": "KHONG vay",
            "strategy": "KHA THUAN LOI - Co phieu la chu yeu, giu 30% tien",
            "color": "VANG_XANH"
        }
    elif score >= 40:
        return {
            "stock_pct": 50,
            "cash_pct": 50,
            "leverage": "KHONG vay",
            "strategy": "TRUNG TINH - Can bang co phieu / tien mat",
            "color": "VANG"
        }
    elif score >= 30:
        return {
            "stock_pct": 30,
            "cash_pct": 70,
            "leverage": "TUYET DOI KHONG vay",
            "strategy": "KEM THUAN LOI - Giu nhieu tien, chi chon lot tung co phieu",
            "color": "CAM"
        }
    elif score >= 20:
        return {
            "stock_pct": 15,
            "cash_pct": 85,
            "leverage": "TUYET DOI KHONG vay",
            "strategy": "NGUY HIEM - Phan lon tien mat, sap co dot mua tot hon",
            "color": "DO_NHAT"
        }
    else:
        return {
            "stock_pct": 0,
            "cash_pct": 100,
            "leverage": "TUYET DOI KHONG vay - co the dang short neu co cong cu",
            "strategy": "THOAT HANG - Nhanh chong chuyen sang tien mat",
            "color": "DO_DAM"
        }

# ══════════════════════════════════════════════════════════════════════
# PHAN 3: CHAY LICH SU + HIEN TAI
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("LOAD VNINDEX.csv va tinh Market Score toan lich su")
print("=" * 70)

vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
vni = vni[vni["time"] >= "2016-01-01"].copy()  # Chi tu 2016 khi co VNINDEX_PE

# Convert numeric
for col in ["VNINDEX_PE","VNINDEX_PE_MA2Y","VNINDEX_PE_MA4Y","VNINDEX_PE_MA5Y",
            "Close","D_RSI","D_CMF","D_MACDdiff","MA50","MA200",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_MinT3","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_T1W","D_RSI_Min1W_Close","D_RSI_Min3M_Close",
            "D_RSI_Max1W_Close","D_RSI_Max3M_Close","D_RSI_Max1W_MACD","D_RSI_Max3M_MACD",
            "C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

# Tinh PE percentile rolling (dung 5Y window)
pe_all = vni["VNINDEX_PE"].dropna()
pe_sorted = np.sort(pe_all.values)

def pe_percentile(pe_val):
    if pd.isna(pe_val):
        return np.nan
    return float(np.searchsorted(pe_sorted, pe_val)) / len(pe_sorted)

vni["pe_percentile"] = vni["VNINDEX_PE"].apply(pe_percentile)

# ─────────────────────────────────────────────
# Tinh score cho tung ngay
# ─────────────────────────────────────────────
print("Tinh Market Score cho tung ngay...")
records = []
for _, row in vni.iterrows():
    date = row["time"]

    # [A] PE score
    pe_score, pe_zone = score_pe_valuation(
        row.get("VNINDEX_PE", np.nan),
        row.get("pe_percentile", 0.5)
    )

    # [B] Phase score
    phase_score, phase = score_market_phase(
        row.get("D_RSI", np.nan),
        row.get("D_MACDdiff", np.nan),
        row.get("D_CMF", np.nan),
        row.get("Close", np.nan),
        row.get("MA200", np.nan)
    )

    # [C] VNI Signal score
    sig_score, sig_label = score_vni_signal(row)

    # [D] SBV rate score
    sbv_rate, sbv_trend, _ = get_rate_at_date(SBV_RATE_HISTORY, date)
    sbv_score, sbv_label = score_sbv_rate(sbv_rate, sbv_trend)

    # [E] Fed score
    fed_rate, fed_trend, _ = get_rate_at_date(FED_RATE_HISTORY, date)
    fed_score, fed_label = score_fed_rate(fed_rate, fed_trend)

    total = pe_score + phase_score + sig_score + sbv_score + fed_score

    alloc = total_score_to_allocation(total)

    records.append({
        "date": date,
        "close": row.get("Close", np.nan),
        "vnindex_pe": row.get("VNINDEX_PE", np.nan),
        "pe_pctile": row.get("pe_percentile", np.nan),
        "pe_zone": pe_zone,
        "pe_score": pe_score,
        "phase": phase,
        "phase_score": phase_score,
        "sig_label": sig_label,
        "sig_score": sig_score,
        "sbv_rate": sbv_rate,
        "sbv_score": sbv_score,
        "sbv_label": sbv_label,
        "fed_rate": fed_rate,
        "fed_score": fed_score,
        "fed_label": fed_label,
        "total_score": total,
        "stock_pct": alloc["stock_pct"],
        "cash_pct": alloc["cash_pct"],
        "leverage": alloc["leverage"],
        "strategy": alloc["strategy"],
    })

score_df = pd.DataFrame(records)
print(f"Computed {len(score_df):,} daily scores")

# ══════════════════════════════════════════════════════════════════════
# PHAN 4: LICH SU CAC MOC QUAN TRONG
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("LICH SU MARKET SCORE TAI CAC MOC QUAN TRONG")
print("=" * 70)

key_dates = [
    "2017-03-01", "2017-10-01",           # Bull run 2017
    "2018-03-01", "2018-10-01",           # Dinh 1200 + giam
    "2019-03-01",                          # Phuc hoi 2019
    "2020-03-23",                          # Day COVID
    "2020-07-01",                          # Sau COVID
    "2021-03-01", "2021-11-01",           # Bull 2021
    "2022-01-10",                          # Dinh 2022
    "2022-06-14", "2022-11-16",           # Day 2022
    "2023-06-01",                          # Phuc hoi
    "2024-01-01", "2024-09-01",           # 2024
    "2025-01-15", "2025-04-15",           # ATH 2025
    "2026-01-15", "2026-04-17",           # Hien tai 2026
]

print(f"\n{'Date':>12} {'VNI':>6} {'PE':>6} {'PctR':>5} {'Tot':>5} {'PE_s':>5} {'Ph_s':>5} {'Sig_s':>5} {'SBV':>5} {'Fed':>5}  Strategy")
print("-" * 120)

for kd in key_dates:
    kdate = pd.Timestamp(kd)
    sub = score_df[score_df["date"] <= kdate]
    if len(sub) == 0:
        continue
    row = sub.iloc[-1]
    print(f"  {str(row['date'].date()):>12} {row['close']:>6.0f} {row['vnindex_pe']:>6.1f} {row['pe_pctile']:>5.0%} "
          f"{row['total_score']:>5.0f} {row['pe_score']:>5.0f} {row['phase_score']:>5.0f} "
          f"{row['sig_score']:>5.0f} {row['sbv_score']:>5.0f} {row['fed_score']:>5.0f}  "
          f"{row['strategy'][:50]}")

# ══════════════════════════════════════════════════════════════════════
# PHAN 5: PHAN BO SCORE THEO TUNG VUNG
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PHAN BO MARKET SCORE - BAO NHIEU NGAY O TUNG VUNG?")
print("=" * 70)

# Phan phoi score
score_df["score_zone"] = pd.cut(score_df["total_score"],
    bins=[0, 20, 30, 40, 50, 60, 70, 80, 101],
    labels=["<20 THOAT HANG", "20-30 NGUY HIEM", "30-40 KEM",
            "40-50 TRUNG TINH", "50-60 KHA", "60-70 TOT",
            "70-80 RAT TOT (co the vay)", ">80 VANG (full leverage)"])

zone_dist = score_df.groupby("score_zone", observed=True).agg(
    n_days=("date", "count"),
    pe_avg=("vnindex_pe", "mean"),
    close_avg=("close", "mean"),
    score_avg=("total_score", "mean"),
).reset_index()

print(f"\n{'Zone':<32} {'Days':>6} {'%':>6} {'VNI_avg':>8} {'PE_avg':>7} {'Score_avg':>10}")
print("-" * 80)
total_days = len(score_df)
for _, row in zone_dist.iterrows():
    pct = row["n_days"] / total_days * 100
    print(f"  {str(row['score_zone']):<32} {row['n_days']:>6} {pct:>5.1f}% {row['close_avg']:>8.0f} {row['pe_avg']:>7.1f} {row['score_avg']:>10.1f}")

# ══════════════════════════════════════════════════════════════════════
# PHAN 6: VALIDATE - KHI SCORE CAO, LUI VE PROFIT CO THUC SU TOT?
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("VALIDATE: Market Score cao -> Forward return tot hon?")
print("=" * 70)

# Tinh forward return (60 ngay trading ~ 3 thang)
score_valid = score_df[score_df["close"].notna()].copy()
score_valid = score_valid.reset_index(drop=True)

for fwd in [20, 40, 60]:
    score_valid[f"fwd_{fwd}d"] = (
        score_valid["close"].shift(-fwd) / score_valid["close"] - 1
    ) * 100

# Phan bo theo score bucket
score_valid["score_bucket"] = pd.cut(score_valid["total_score"],
    bins=[0, 30, 40, 50, 60, 70, 80, 101],
    labels=["<30", "30-40", "40-50", "50-60", "60-70", "70-80", ">80"])

print(f"\n{'Score':>8} {'n':>5} {'Fwd1M':>8} {'Fwd2M':>8} {'Fwd3M':>8}  {'Win3M':>8}")
print("-" * 55)
for bucket in ["<30","30-40","40-50","50-60","60-70","70-80",">80"]:
    sub = score_valid[score_valid["score_bucket"] == bucket].dropna(subset=["fwd_60d"])
    if len(sub) < 10:
        continue
    fwd1 = sub["fwd_20d"].median()
    fwd2 = sub["fwd_40d"].median()
    fwd3 = sub["fwd_60d"].median()
    win3 = (sub["fwd_60d"] > 0).mean()
    print(f"  {bucket:>8} {len(sub):>5} {fwd1:>+8.1f}% {fwd2:>+8.1f}% {fwd3:>+8.1f}%  {win3:>7.1%}")

# ══════════════════════════════════════════════════════════════════════
# PHAN 7: DASHBOARD HIEN TAI
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("=== DASHBOARD DANH GIA THI TRUONG HIEN TAI (2026-04-17) ===")
print("=" * 70)

latest = score_df.iloc[-1]
alloc_now = total_score_to_allocation(latest["total_score"])

print(f"""
  ┌──────────────────────────────────────────────────────────┐
  │  VNINDEX: {latest['close']:>6.0f}  │  VNINDEX_PE: {latest['vnindex_pe']:>5.2f}x  │  Percentile: {latest['pe_pctile']:.0%}
  ├──────────────────────────────────────────────────────────┤
  │  [A] PE Valuation   : {latest['pe_score']:>2.0f}/30 pt  - {latest['pe_zone']}
  │  [B] Market Phase   : {latest['phase_score']:>2.0f}/25 pt  - {latest['phase']}
  │  [C] VNI Signal     : {latest['sig_score']:>2.0f}/20 pt  - {latest['sig_label']}
  │  [D] SBV Lai suat   : {latest['sbv_score']:>2.0f}/15 pt  - {latest['sbv_label']}
  │  [E] Fed Policy     : {latest['fed_score']:>2.0f}/10 pt  - {latest['fed_label']}
  ├──────────────────────────────────────────────────────────┤
  │  TONG DIEM          : {latest['total_score']:>2.0f}/100
  ├──────────────────────────────────────────────────────────┤
  │  KHUYEN NGHI PHAN BO:
  │    Co phieu : {alloc_now['stock_pct']:>3}%
  │    Tien mat : {alloc_now['cash_pct']:>3}%
  │    Don bay  : {alloc_now['leverage']}
  │  CHIEN LUOC : {alloc_now['strategy']}
  └──────────────────────────────────────────────────────────┘
""")

# ══════════════════════════════════════════════════════════════════════
# PHAN 8: SCENARIOS TU DONG - NHU VUNG NAO TRONG VONG 6 THANG TI
# ══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("SCENARIOS: Neu thi truong thay doi -> Score thay doi the nao?")
print("=" * 70)

scenarios = [
    {"ten": "Base case (hien tai)", "vni": 1817, "pe": 15.45, "rsi": 0.65, "sbv": 4.5, "sbv_trend": "HOLD", "fed": 4.0, "fed_trend": "HOLD", "ma200": 1550},
    {"ten": "Bull break ATH 2000+", "vni": 2100, "pe": 18.0, "rsi": 0.78, "sbv": 4.5, "sbv_trend": "HOLD", "fed": 3.75, "fed_trend": "CUTTING", "ma200": 1600},
    {"ten": "Correction 1500", "vni": 1500, "pe": 13.5, "rsi": 0.42, "sbv": 4.5, "sbv_trend": "CUTTING", "fed": 3.75, "fed_trend": "CUTTING", "ma200": 1550},
    {"ten": "Bear 1200 (VNI duoi MA200)", "vni": 1200, "pe": 11.5, "rsi": 0.32, "sbv": 5.0, "sbv_trend": "HOLD", "fed": 5.0, "fed_trend": "HIKING", "ma200": 1450},
    {"ten": "Khung hoang 900 (2022 lap lai)", "vni": 900, "pe": 9.5, "rsi": 0.22, "sbv": 6.0, "sbv_trend": "HIKING", "fed": 5.5, "fed_trend": "HIKING", "ma200": 1300},
    {"ten": "SBV cat manh, Fed cat", "vni": 1700, "pe": 14.5, "rsi": 0.55, "sbv": 3.5, "sbv_trend": "CUTTING", "fed": 3.0, "fed_trend": "CUTTING", "ma200": 1500},
    {"ten": "Day COVID (2020-03)", "vni": 660, "pe": 10.2, "rsi": 0.18, "sbv": 5.0, "sbv_trend": "CUTTING", "fed": 0.25, "fed_trend": "CUTTING", "ma200": 950},
]

print(f"\n{'Scenario':<38} {'VNI':>5} {'PE':>5} {'Score':>6} {'Stock%':>7} {'Cash%':>6}  Strategy")
print("-" * 100)
for s in scenarios:
    pe_s, pe_z = score_pe_valuation(s["pe"], pe_percentile(s["pe"]))
    ph_s, ph = score_market_phase(s["rsi"], 0 if s["rsi"] < 0.5 else 1, 0, s["vni"], s["ma200"])
    sbv_s, _ = score_sbv_rate(s["sbv"], s["sbv_trend"])
    fed_s, _ = score_fed_rate(s["fed"], s["fed_trend"])
    sig_s = 10  # neutral signal
    total_s = pe_s + ph_s + sig_s + sbv_s + fed_s
    alloc_s = total_score_to_allocation(total_s)
    print(f"  {s['ten']:<38} {s['vni']:>5} {s['pe']:>5.1f} {total_s:>6} "
          f"{alloc_s['stock_pct']:>7}% {alloc_s['cash_pct']:>6}%  {alloc_s['strategy'][:45]}")

# ══════════════════════════════════════════════════════════════════════
# PHAN 9: TONG KET PHUONG PHAP
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TONG KET: PHUONG PHAP DANH GIA 5 TRU COT (0-100 DIEM)")
print("=" * 70)
print("""
  [A] VNINDEX_PE Valuation (0-30 diem)
      PE < 10x      = 30 diem  (SIEU RE - chi xuat hien 2022-Q4, 2020-COVID)
      PE 10-12x     = 25 diem  (RAT RE - thoi ky suy thoai)
      PE 12-14x     = 18 diem  (RE - vung tich luy tot)
      PE 14-16x     = 12 diem  (BINH THUONG - hien tai 15.4x)
      PE 16-18x     =  7 diem  (CAO - can chon loc)
      PE 18-20x     =  3 diem  (RAT CAO - chi mua tang truong cao)
      PE > 20x      =  0 diem  (NGUY HIEM - tranh mua)

  [B] Market Phase (0-25 diem)
      BEAR_BOTTOM   = 24 diem  (Gia duoi MA200, RSI < 0.30)
      ACCUMULATION  = 20 diem  (Gia duoi MA200, RSI 0.30-0.45)
      RECOVERY_LOW  = 16 diem  (MACD duong nhung gia van thap)
      RECOVERY      = 16 diem  (Gia tren MA200, MACD am -> dang phuc hoi)
      BULL_EARLY    = 14 diem  (Gia tren MA200, RSI < 0.50)
      BULL_STRONG   = 10 diem  (Gia tren MA200, RSI 0.50-0.65) <- HIEN TAI
      DISTRIBUTION  =  1 diem  (RSI > 0.80, dinh thi truong)

  [C] VNI Technical Signal (0-20 diem)
      BullDvgVNI12  = 20 diem  (RSI phan ky tang manh - mua dot)
      BullDvgVNI1   = 16 diem  (RSI phan ky tang nhe)
      NEUTRAL       = 10 diem  (Khong co tin hieu ro)
      BearDvgVNI2   =  2 diem  (RSI phan ky giam - giam ty trong)

  [D] SBV Lai suat (0-15 diem)
      Rate <= 4% + CUTTING  = 15 diem  (Tien re, co phieu hap dan)
      Rate <= 5% + CUTTING  = 12 diem
      Rate <= 5% + HOLD     = 10 diem  <- HIEN TAI (4.5% HOLD)
      Rate 5-6% + HOLD      =  7 diem
      Rate > 6% + HIKING    =  3 diem  (Tien dat, anh huong dinh gia)

  [E] Fed Policy (0-10 diem)
      Rate <= 2.5% + CUTTING = 10 diem  (Von vao EM manh)
      Rate <= 4% + CUTTING   =  7 diem  <- HIEN TAI (4.0% HOLD)
      Rate <= 5% + HOLD      =  5 diem
      Rate > 5% + HIKING     =  1 diem  (Von rut khoi EM)

  TONG DIEM -> PHAN BO TAI SAN:
  ┌────────────┬────────────┬───────────┬───────────────────────────────┐
  │ Score      │ Co phieu%  │ Tien%     │ Don bay / Chien luoc          │
  ├────────────┼────────────┼───────────┼───────────────────────────────┤
  │ 80-100     │   150%     │  -50%     │ Vay 1:0.5 (margin 50%)        │
  │ 70-79      │   100%     │    0%     │ Co the Vay 1:1 neu kinh nghiem │
  │ 60-69      │    85%     │   15%     │ Full - khong vay              │
  │ 50-59      │    70%     │   30%     │ Can bang nghieng co phieu     │
  │ 40-49      │    50%     │   50%     │ Can bang 50/50                │
  │ 30-39      │    30%     │   70%     │ Phong thu, giu nhieu tien     │
  │ 20-29      │    15%     │   85%     │ Gian toi thieu, cho co hoi    │
  │ 0-19       │     0%     │  100%     │ Thoat toan bo, tien mat       │
  └────────────┴────────────┴───────────┴───────────────────────────────┘
""")

# Save
score_df.to_csv(os.path.join(WORKDIR, "data/market_score_history.csv"), index=False)
print(f"Saved: market_score_history.csv ({len(score_df):,} rows)")
print("\nDone!")
