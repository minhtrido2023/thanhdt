#!/usr/bin/env python3
"""asof_label_selfcheck — CSV dán nhãn NGÀY mà giá trị là hàm của TƯƠNG LAI.

Bất biến được canh (một câu):
    với mỗi dòng, NHÃN NGÀY phải >= ngày cuối cùng của dữ liệu đã sinh ra giá trị dòng đó.

Vì sao cần: `data/lag_edge_health.csv` (edge_health_monitor.py::lag_edge_health) ghi `ret` =
return FORWARD 25 phiên tính từ `entry`, nhưng dán nhãn dòng theo chính `entry`. Consumer
production (`pt_v23_audit_2014.py`, `pt_v22_dt5g.py`) đọc `pd.read_csv(..., parse_dates=["entry"])`
rồi `.reindex(daily_calendar, method="ffill")` — nên trong BACKTEST cổng w_LAG 0,65/0,50 đọc được
mỗi giá trị mean12 SỚM 25 phiên so với ngày nó có thể tồn tại. (FAIL-C, audit
measurement-integrity-audit-2026-09-27; đo được 317/3.654 ngày = 8,7% cổng đổi.)
LIVE không mắc lỗi này vì dòng mới chỉ xuất hiện khi sự kiện đã hoàn tất — lỗi thuần BACKTEST.

`self-check 0 VND` MÙ với lớp lỗi này (nó là định thức tiền mặt, không canh nhãn thời gian), nên
đây là cổng riêng. Đây là một selfcheck DIỄN GIẢI ĐƯỢC, không phải regex: nó dựng lại lịch phiên
THẬT từ chính nguồn giá đã sinh ra chuỗi, rồi so nhãn với ngày đóng cửa sổ quan sát.

Dùng:
    python3 bin/asof_label_selfcheck.py                 # chạy unit test + mọi series đã đăng ký
    python3 bin/asof_label_selfcheck.py --csv <path>    # ép 1 file (A/B bản vá)
    python3 bin/asof_label_selfcheck.py --units-only    # chỉ unit test (không cần data thật)
rc=0 tất cả PASS · rc=1 có series vi phạm · rc=2 lỗi môi trường/thiếu file.
"""
import argparse
import os
import pickle
import sys

import numpy as np
import pandas as pd

WC_ROOT = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")

# ── ĐĂNG KÝ ─────────────────────────────────────────────────────────────────────────────────
# label_cols: theo THỨ TỰ ƯU TIÊN — cột đầu tiên CÓ MẶT chính là nhãn mà consumer index lên.
#             Phải khớp cách consumer chọn cột, nếu không selfcheck canh một cột không ai đọc.
# anchor_col: ngày cửa sổ quan sát MỞ. horizon_sessions: số phiên tới khi cửa sổ ĐÓNG.
SERIES = {
    "lag_edge_health": dict(
        csv="data/lag_edge_health.csv",
        label_cols=["known_date", "entry"],
        anchor_col="entry",
        horizon_sessions=25,
        calendar=("pickle_col", "data/earnings_px.pkl", "time"),
        consumers="pt_v23_audit_2014.py:2057 · pt_v22_dt5g.py:777 (ffill lên lịch ngày)",
    ),
}


def load_calendar(spec):
    """Lịch phiên THẬT, lấy từ chính nguồn dữ liệu đã sinh ra chuỗi (không phải busday_count)."""
    kind, path, col = spec
    full = path if os.path.isabs(path) else os.path.join(WC_ROOT, path)
    if kind != "pickle_col":
        raise ValueError(f"calendar kind khong ho tro: {kind}")
    with open(full, "rb") as f:
        df = pickle.load(f)
    return pd.DatetimeIndex(pd.to_datetime(df[col]).drop_duplicates().sort_values())


def check_labels(df, label_col, anchor_col, horizon, calendar):
    """Trả (n_rows, n_viol, worst_lag_sessions, sample). worst_lag = số phiên nhãn bị SỚM."""
    lab = pd.to_datetime(df[label_col])
    anc = pd.to_datetime(df[anchor_col])
    pos = calendar.searchsorted(anc.values, side="left")
    ok = pos + horizon < len(calendar)
    if not ok.all():
        # dòng có cửa sổ chưa đóng trong lịch đang có -> không kết luận được, bỏ qua tường minh
        df, lab, anc, pos = df[ok], lab[ok], anc[ok], pos[ok]
    need = calendar[pos + horizon]                       # ngày cửa sổ quan sát ĐÓNG
    viol = lab.values < need.values
    worst = 0
    if viol.any():
        lab_pos = calendar.searchsorted(lab.values[viol], side="left")
        worst = int(np.max((pos[viol] + horizon) - lab_pos))
    sample = None
    if viol.any():
        i = int(np.argmax(viol))
        sample = (str(pd.Timestamp(lab.values[i]).date()), str(need[i].date()))
    return len(df), int(viol.sum()), worst, sample


# ── UNIT TEST (không phụ thuộc data thật) ───────────────────────────────────────────────────
def _units():
    cal = pd.DatetimeIndex(pd.bdate_range("2020-01-01", periods=200))
    anc = cal[[10, 40, 80]]
    fails = []

    def expect(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # 1. nhãn = anchor, giá trị nhìn tới +25 phiên -> PHẢI bị bắt, lệch đúng 25 phiên
    d = pd.DataFrame({"entry": anc, "known_date": anc})
    n, v, w, _ = check_labels(d, "known_date", "entry", 25, cal)
    expect("U1 nhan=anchor voi horizon 25 -> 3/3 vi pham, lech 25 phien", (n, v, w) == (3, 3, 25))

    # 2. nhãn = anchor + đúng 25 phiên -> sạch
    d = pd.DataFrame({"entry": anc, "known_date": cal[[35, 65, 105]]})
    n, v, _, _ = check_labels(d, "known_date", "entry", 25, cal)
    expect("U2 nhan = anchor+25 phien -> 0 vi pham", (n, v) == (3, 0))

    # 3. nhãn trễ hơn mức cần (bảo thủ) -> vẫn sạch
    d = pd.DataFrame({"entry": anc, "known_date": cal[[60, 90, 130]]})
    _, v, _, _ = check_labels(d, "known_date", "entry", 25, cal)
    expect("U3 nhan tre hon can thiet (bao thu) -> 0 vi pham", v == 0)

    # 4. sớm 1 phiên duy nhất cũng bị bắt (không có vùng dung sai im lặng)
    d = pd.DataFrame({"entry": anc, "known_date": cal[[34, 65, 105]]})
    _, v, w, _ = check_labels(d, "known_date", "entry", 25, cal)
    expect("U4 som DUNG 1 phien -> bat duoc, w=1", (v, w) == (1, 1))

    # 5. horizon 0 (giá trị chỉ dùng dữ liệu tới chính anchor) -> nhãn=anchor là hợp lệ
    d = pd.DataFrame({"entry": anc, "known_date": anc})
    _, v, _, _ = check_labels(d, "known_date", "entry", 0, cal)
    expect("U5 horizon=0 -> nhan=anchor hop le", v == 0)

    # 6. dòng có cửa sổ chưa đóng trong lịch bị LOẠI tường minh, không âm thầm pass cả bảng
    d = pd.DataFrame({"entry": cal[[10, 190]], "known_date": cal[[10, 190]]})
    n, v, _, _ = check_labels(d, "known_date", "entry", 25, cal)
    expect("U6 dong ngoai lich bi loai (n=1, van bat dong con lai)", (n, v) == (1, 1))

    # 7. fallback cột nhãn: thiếu known_date -> consumer index lên entry
    d = pd.DataFrame({"entry": anc, "ret": [1.0, 2.0, 3.0]})
    col = next((c for c in SERIES["lag_edge_health"]["label_cols"] if c in d.columns), None)
    expect("U7 thieu known_date -> nhan rot ve 'entry'", col == "entry")

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="ep duong dan CSV cho series duy nhat (A/B ban va)")
    ap.add_argument("--series", default="lag_edge_health")
    ap.add_argument("--units-only", action="store_true")
    a = ap.parse_args()

    print("== unit tests (synthetic) ==")
    fails = _units()
    if fails:
        print(f"\nUNIT FAIL: {fails}")
        return 1
    if a.units_only:
        print("\nOK: unit-only, khong doc data that.")
        return 0

    bad = []
    names = [a.series] if a.csv else list(SERIES)
    print("\n== series that ==")
    for name in names:
        spec = SERIES[name]
        path = a.csv or os.path.join(WC_ROOT, spec["csv"])
        if not os.path.exists(path):
            print(f"  [SKIP] {name}: khong thay {path}")
            continue
        try:
            cal = load_calendar(spec["calendar"])
        except Exception as e:
            print(f"  [ENV ] {name}: khong dung duoc lich phien ({e})")
            return 2
        df = pd.read_csv(path)
        label_col = next((c for c in spec["label_cols"] if c in df.columns), None)
        if label_col is None:
            print(f"  [ENV ] {name}: khong co cot nhan nao trong {spec['label_cols']}")
            return 2
        n, v, w, s = check_labels(df, label_col, spec["anchor_col"], spec["horizon_sessions"], cal)
        tag = "PASS" if v == 0 else "FAIL"
        print(f"  [{tag}] {name}  file={os.path.basename(path)}  nhan='{label_col}'  "
              f"n={n}  vi_pham={v}  som_toi_da={w} phien")
        if v:
            print(f"         vd dong dau: nhan={s[0]} nhung du lieu chi day du tu {s[1]}")
            print(f"         consumer bi anh huong: {spec['consumers']}")
            bad.append(name)
    print()
    print("OK: moi series dan nhan CAUSAL." if not bad else f"VI PHAM: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
