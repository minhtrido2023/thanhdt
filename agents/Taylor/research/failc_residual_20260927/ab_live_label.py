"""A/B: nhan `entry` vs `known_date` tren duong LIVE (w_lag_target) va tren neg_streak.

KHONG import golive_recommend_v23 (module do keo BQ + config live). Thay vao do TAI TAO
DUNG 2 phep tinh cua no, roi doi chieu voi ham that o buoc sau (harness rieng).

Muc dich: chung minh delta = 0 tren mean12/w_LAG (live luon lay dong CUOI) va delta != 0
tren `asof` (nhan bao cao) + `neg_streak`.
"""
import os, sys
import pandas as pd

EDGE_THR = 1.0   # doc lai tu golive_recommend_v23 o buoc verify; hardcode o day chi de A/B


def live_read(path, label):
    """Tai tao golive_recommend_v23.w_lag_target's edge read voi nhan `label`."""
    eh = pd.read_csv(path)
    if label not in eh.columns:
        return None
    eh[label] = pd.to_datetime(eh[label])
    s = eh.drop_duplicates(label).set_index(label).sort_index()["mean12"]
    return s


def neg_streak(path, label):
    eh = pd.read_csv(path)
    if label not in eh.columns:
        return None, None
    eh[label] = pd.to_datetime(eh[label])
    d = eh.sort_values(label)
    mo = d.set_index(label)["mean12"].resample("ME").last().dropna()
    ns = 0
    for v in mo.values[::-1]:
        if v < 0:
            ns += 1
        else:
            break
    return ns, mo


def main():
    WC = "/home/trido/thanhdt/WorkingClaude"
    files = {
        "NEW (co known_date)": WC + "/data/lag_edge_health.csv",
        "BACKUP (pre-FAIL-C, KHONG co known_date)": WC + "/data/lag_edge_health.csv.bak_20260927_prefailc",
    }
    # asof ma live dung: phien gan nhat (hom nay, HOSE dong cua) -> lay ngay cuoi cua chuoi + 1 thang
    asof_live = pd.Timestamp("2026-09-27")

    for fname, path in files.items():
        print("=" * 78)
        print(f"FILE: {fname}")
        print(f"      {path}")
        cols = pd.read_csv(path, nrows=0).columns.tolist()
        print(f"      columns = {cols}")
        for label in ("entry", "known_date"):
            s = live_read(path, label)
            if s is None:
                print(f"  [{label:<10}] COT THIEU -> live phai FALLBACK sang 'entry'")
                continue
            m = s.asof(asof_live)
            w = 0.65 if (pd.notna(m) and m >= EDGE_THR) else 0.50
            ns, mo = neg_streak(path, label)
            print(f"  [{label:<10}] rows={len(s):<6} asof_label={s.index[-1].date()} "
                  f"mean12(as-of {asof_live.date()})={m:.4f}%  -> w_LAG={w:.2f}  neg_streak={ns}")
            print(f"               thang cuoi cua chuoi: "
                  f"{', '.join(f'{k.strftime('%Y-%m')}={v:+.3f}' for k, v in mo.tail(5).items())}")
    print("=" * 78)


if __name__ == "__main__":
    main()
