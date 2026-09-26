#!/usr/bin/env python3
"""Hợp nhất raw harvest FiinPro-X (trial, kết thúc 2026-09-28) thành 2 CSV:

  data/fiinprox_oshares_pit_20260926.csv   — số CP lưu hành theo NGÀY ĐỔI SỐ (event-only)
  data/fiinprox_usd_fx_monthly_20260926.csv — tỷ giá USD tháng (trung tâm / VCB / tự do / NHNN)

Raw OShares: `TICKER|nN|bB|yymmdd:level;yymmdd:+delta;...` (mốc đầu là mức, mốc sau là delta,
đã lọc 'nháy' ≤5 phiên quay về giá trị cũ — xem CODE_OSHARES trong fiinprox_harvest_tick.py).
Raw FX: header `#fx YYYY n`, rồi `YYYY-MM,central,vcb_bid_tf,vcb_ask,free_ask,sbv_ask` (rỗng = NaN).

Idempotent, ghi nguyên tử. Không gọi mạng.
"""
import csv
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OSH_RAW = os.path.join(ROOT, "data", "fiinprox_oshares_raw")
FX_RAW = os.path.join(ROOT, "data", "fiinprox_fx_raw")
OSH_OUT = os.path.join(ROOT, "data", "fiinprox_oshares_pit_20260926.csv")
FX_OUT = os.path.join(ROOT, "data", "fiinprox_usd_fx_monthly_20260926.csv")


def atomic_csv(path, header, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def parse_oshares():
    rows, na, dup = [], [], {}
    for fp in sorted(glob.glob(os.path.join(OSH_RAW, "b*.txt"))):
        with open(fp) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                t = parts[0]
                if len(parts) == 2 and parts[1] == "NA":
                    na.append(t)
                    continue
                if len(parts) != 4:
                    raise ValueError(f"{fp}: dòng lạ: {line[:80]}")
                n_obs = int(parts[1][1:])
                blips = int(parts[2][1:])
                if t in dup:
                    dup[t] += 1
                    continue
                dup[t] = 1
                level = None
                for i, ev in enumerate(parts[3].split(";")):
                    d, v = ev.split(":")
                    date = f"20{d[:2]}-{d[2:4]}-{d[4:6]}"
                    if i == 0:
                        level = int(v)
                        delta = ""
                        flag = "first_obs"
                    else:
                        delta = int(v)
                        level += delta
                        flag = ""
                        if level <= 0:
                            flag = "nonpositive_level"
                        elif abs(delta) / max(level - delta, 1) < 1e-5:
                            flag = "tiny_delta"
                    rows.append([t, date, level, delta, n_obs, blips, flag])
    return rows, na, {k: v for k, v in dup.items() if v > 1}


def parse_fx():
    rows, seen = [], set()
    for fp in sorted(glob.glob(os.path.join(FX_RAW, "usd_*.txt"))):
        with open(fp) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cols = line.split(",")
                if len(cols) != 6:
                    raise ValueError(f"{fp}: cần 6 cột, có {len(cols)}: {line}")
                if cols[0] in seen:
                    continue
                seen.add(cols[0])
                rows.append(cols)
    rows.sort(key=lambda r: r[0])
    return rows


def main():
    osh, na, dup = parse_oshares()
    atomic_csv(OSH_OUT, ["ticker", "date", "shares", "delta", "n_obs", "blips", "flags"], osh)
    tickers = {r[0] for r in osh}
    print(f"oshares: {len(osh)} sự kiện, {len(tickers)} mã, NA={len(na)} {na[:10]}, trùng={dup}")
    print(f"  tiny_delta={sum(1 for r in osh if r[6]=='tiny_delta')}, nonpositive={sum(1 for r in osh if r[6]=='nonpositive_level')}")
    fx = parse_fx()
    atomic_csv(FX_OUT, ["month", "central", "vcb_bid_tf", "vcb_ask", "free_ask", "sbv_ask"], fx)
    miss = {h: sum(1 for r in fx if r[i] == "") for i, h in enumerate(["month", "central", "vcb_bid_tf", "vcb_ask", "free_ask", "sbv_ask"]) if i}
    print(f"fx: {len(fx)} tháng {fx[0][0]}→{fx[-1][0]}, trống theo cột: {miss}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
