import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv", usecols=["time", "Close"])
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)
df = df.set_index("time")

def asof_close(date_str, tolerance_days=10):
    d = pd.Timestamp(date_str)
    idx = df.index.asof(d)
    if pd.isna(idx):
        return None, None
    if abs((idx - d).days) > tolerance_days:
        return None, None
    return idx, df.loc[idx, "Close"]

def ret_before(peak_date_str, months):
    peak_d, peak_close = asof_close(peak_date_str, tolerance_days=3)
    target = pd.Timestamp(peak_date_str) - pd.DateOffset(months=months)
    base_d, base_close = asof_close(target.strftime("%Y-%m-%d"), tolerance_days=15)
    if base_close is None:
        return None, None, None
    return (peak_close / base_close - 1) * 100, base_d, base_close

def months_since_last_10pct_correction(peak_date_str):
    peak_d = df.index.asof(pd.Timestamp(peak_date_str))
    sub = df.loc[:peak_d, "Close"]
    runmax = sub.cummax()
    dd = sub / runmax - 1
    corrected = dd[dd <= -0.10]
    if len(corrected) == 0:
        # no correction >=10% found in entire available history
        first_date = sub.index[0]
        months = (peak_d - first_date).days / 30.44
        return months, first_date, True  # True = hit start of data, lower bound
    last_correction_date = corrected.index[-1]
    months = (peak_d - last_correction_date).days / 30.44
    return months, last_correction_date, False

episodes = [
    ("2007-2009 Wave1", "2007-03-12"),
    ("2011-2012 Wave2/3", "2009-10-22"),
    ("2018", "2018-04-09"),
    ("2020 COVID", "2020-01-22"),
    ("2022", "2022-01-06"),
]

print("="*100)
print("PRIOR TREND trước từng đỉnh (12 tháng, 24 tháng, số tháng uptrend liên tục không có correction >-10%)")
print("="*100)
for name, peak in episodes:
    r12, b12d, b12c = ret_before(peak, 12)
    r24, b24d, b24c = ret_before(peak, 24)
    months_up, last_corr_date, is_lower_bound = months_since_last_10pct_correction(peak)
    peak_d, peak_close = asof_close(peak, tolerance_days=3)
    print(f"\n--- {name} | peak={peak_d.date()} Close={peak_close:.2f} ---")
    print(f"  12mo return trước đỉnh: {r12:+.2f}% (base {b12d.date()} Close={b12c:.2f})" if r12 is not None else "  12mo return: N/A (thiếu data)")
    print(f"  24mo return trước đỉnh: {r24:+.2f}% (base {b24d.date()} Close={b24c:.2f})" if r24 is not None else "  24mo return: N/A (thiếu data)")
    lb = " (LOWER BOUND - chạm đầu dữ liệu, chưa từng có correction 10% trong toàn bộ lịch sử trước đó)" if is_lower_bound else ""
    print(f"  Số tháng uptrend liên tục (không correction >-10%) ngay trước đỉnh: {months_up:.1f} tháng (correction gần nhất: {last_corr_date.date()}){lb}")

# 07/2026 case - need BQ data since local file only to 2026-05-26 (peak itself 2026-05-18 is within range,
# but 12/24mo lookback needs 2024-05 and 2023-05, both well within range - fine, no BQ needed for THIS calc)
print("\n" + "="*100)
print("2026 case (dùng riêng, verify claim 'nền bình thường')")
print("="*100)
peak2026 = "2026-05-18"
r12, b12d, b12c = ret_before(peak2026, 12)
r24, b24d, b24c = ret_before(peak2026, 24)
months_up, last_corr_date, is_lower_bound = months_since_last_10pct_correction(peak2026)
peak_d, peak_close = asof_close(peak2026, tolerance_days=3)
print(f"peak={peak_d.date()} Close={peak_close:.2f}")
print(f"  12mo return: {r12:+.2f}% (base {b12d.date()} Close={b12c:.2f})")
print(f"  24mo return: {r24:+.2f}% (base {b24d.date()} Close={b24c:.2f})")
lb = " (LOWER BOUND)" if is_lower_bound else ""
print(f"  Tháng uptrend liên tục không correction >-10%: {months_up:.1f} tháng (correction gần nhất: {last_corr_date.date()}){lb}")

def months_uptrend_local_anchor(trough_date_str, peak_date_str):
    """Cummax/drawdown tính từ trough của khủng hoảng TRƯỚC (không phải all-time-high toàn lịch sử) -
    tránh bẫy 'peak vẫn thấp hơn ATH cũ rất xa nên dd luôn <=-10% ngay tại điểm peak'."""
    t = df.index.asof(pd.Timestamp(trough_date_str))
    p = df.index.asof(pd.Timestamp(peak_date_str))
    sub = df.loc[t:p, "Close"]
    runmax = sub.cummax()
    dd = sub / runmax - 1
    corrected = dd[dd <= -0.10]
    if len(corrected) == 0:
        months = (p - t).days / 30.44
        return months, t, True
    last_correction_date = corrected.index[-1]
    months = (p - last_correction_date).days / 30.44
    return months, last_correction_date, False

print("\n" + "="*100)
print("Sửa lỗi phương pháp: 'tháng uptrend' đo LỆCH-ANCHOR (ATH toàn lịch sử) cho 2 case peak vẫn CHƯA vượt ATH cũ")
print("="*100)
for name, trough, peak in [
    ("2011-2012 Wave2/3 (peak 2009-10-22, anchor=trough Wave1 2009-02-24)", "2009-02-24", "2009-10-22"),
    ("2020 COVID (peak 2020-01-22, anchor=trough 2018 2018-10-30)", "2018-10-30", "2020-01-22"),
]:
    months, last_d, lb = months_uptrend_local_anchor(trough, peak)
    lb_s = " (LOWER BOUND, chạm luôn điểm trough anchor - không có correction >-10% nào trong toàn bộ leg)" if lb else ""
    print(f"{name}: {months:.1f} tháng uptrend liên tục kể từ trough gần nhất (correction gần nhất trong leg: {last_d.date()}){lb_s}")

print("\n" + "="*100)
print("2020 COVID case — verify claim user: cumulative return từ đỉnh 2018-04-09 đến đỉnh 2020-01-22")
print("="*100)
d1, c1 = asof_close("2018-04-09", 3)
d2, c2 = asof_close("2020-01-22", 3)
print(f"{d1.date()} Close={c1:.2f} -> {d2.date()} Close={c2:.2f} : cumulative return = {(c2/c1-1)*100:+.2f}% qua {(d2-d1).days} ngày (~{(d2-d1).days/30.44:.1f} tháng)")
# also the trough within that window and the path (min-to-max range) to check "sideway" claim
sub = df.loc[d1:d2, "Close"]
print(f"  Min trong giai đoạn: {sub.min():.2f} ({sub.idxmin().date()}), Max: {sub.max():.2f} ({sub.idxmax().date()})")
print(f"  Return từ đáy 2018 (30/10/2018, 888.69) đến đỉnh trước COVID (22/01/2020): {(c2/888.69-1)*100:+.2f}%")
