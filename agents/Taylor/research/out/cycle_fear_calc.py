"""Outcome calc cho PREREG cycle_fear_prereg_20260822.md. Chay SAU khi prereg commit 4e36d170.

Tai lap du lieu tho (out/cycle_fear_px.csv):
  source /home/trido/thanhdt/WorkingClaude/wc_env.sh
  bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=200000 '
    SELECT ticker, time, Close FROM `lithe-record-440915-m9.tav2_bq.ticker`
    WHERE ticker IN ("VNINDEX","HPG","HSG","NKG","SSI","VCI","HCM","DIG","PDR","NVL","DBC","BAF",
                     "DCM","DPM","DGC","RAL","MSH","TNG","VHC","FMC","VNM","FPT","MWG")
      AND time BETWEEN "2019-01-01" AND "2026-06-15" AND Close IS NOT NULL
    ORDER BY ticker, time' > out/cycle_fear_px.csv
Dung Close (adjusted), KHONG dung Price (raw) - prereg §2.
"""
import csv, collections, statistics, datetime as dt, json

PX = collections.defaultdict(dict)
with open('out/cycle_fear_px.csv') as f:
    for r in csv.DictReader(f):
        PX[r['ticker']][dt.date.fromisoformat(r['time'])] = float(r['Close'])
DAYS = {t: sorted(v) for t, v in PX.items()}

CASES = [  # (ticker, group, sector, win_start, win_end) — CHOT o prereg §3, khong sua
 ("HPG","b","Thep","2022-06-01","2023-01-31"),
 ("HSG","b","Thep","2022-06-01","2023-01-31"),
 ("NKG","b","Thep","2022-06-01","2023-01-31"),
 ("SSI","b","ChungKhoan","2022-09-01","2023-01-31"),
 ("VCI","b","ChungKhoan","2022-09-01","2023-01-31"),
 ("HCM","b","ChungKhoan","2022-09-01","2023-01-31"),
 ("DIG","b","BDS","2022-09-01","2023-03-31"),
 ("PDR","b","BDS","2022-09-01","2023-03-31"),
 ("NVL","b","BDS","2022-09-01","2023-03-31"),
 ("DBC","b","ChanNuoi","2022-10-01","2023-06-30"),
 ("BAF","b","ChanNuoi","2022-10-01","2023-06-30"),
 ("DCM","b","PhanBon","2022-09-01","2023-06-30"),
 ("DPM","b","PhanBon","2022-09-01","2023-06-30"),
 ("DGC","b","HoaChat","2020-02-15","2020-05-31"),
 ("VNINDEX","c","Index","2020-02-15","2020-05-31"),
 ("VNINDEX","c","Index","2022-01-01","2022-12-31"),
 ("VNM","c","LargeCap","2020-02-15","2020-05-31"),
 ("FPT","c","LargeCap","2020-02-15","2020-05-31"),
 ("MWG","c","LargeCap","2020-02-15","2020-05-31"),
 ("RAL","d","ThietBiDien","2019-08-28","2020-01-31"),
 ("MSH","d","DetMay","2021-07-01","2021-12-31"),
 ("TNG","d","DetMay","2021-07-01","2021-12-31"),
 ("VHC","d","ThuySan","2021-07-01","2021-12-31"),
 ("FMC","d","ThuySan","2021-07-01","2021-12-31"),
]

def px_on_or_before(tk, day):
    ds = DAYS[tk]
    lo, hi = 0, len(ds)-1
    if day < ds[0]: return None, None
    best = None
    while lo <= hi:
        mid = (lo+hi)//2
        if ds[mid] <= day: best = ds[mid]; lo = mid+1
        else: hi = mid-1
    return best, PX[tk][best]

def add_months(d, m):
    y, mo = d.year + (d.month-1+m)//12, (d.month-1+m)%12 + 1
    dd = min(d.day, [31,29 if y%4==0 and (y%100!=0 or y%400==0) else 28,31,30,31,30,31,31,30,31,30,31][mo-1])
    return dt.date(y, mo, dd)

rows = []
for tk, grp, sec, ws, we in CASES:
    ws, we = dt.date.fromisoformat(ws), dt.date.fromisoformat(we)
    win = [d for d in DAYS[tk] if ws <= d <= we]
    if not win: rows.append(dict(ticker=tk, group=grp, sector=sec, note="NO_DATA")); continue
    trough = min(win, key=lambda d: PX[tk][d])
    idx = DAYS[tk].index(trough)
    t20 = DAYS[tk][min(idx+20, len(DAYS[tk])-1)]
    out = dict(ticker=tk, group=grp, sector=sec, win=f"{ws}..{we}",
               trough=str(trough), trough_px=PX[tk][trough],
               t20=str(t20), t20_px=PX[tk][t20])
    for anchor, aday in (("T0", trough), ("T20", t20)):
        for H in (6, 12, 24):
            end = add_months(aday, H)
            _, p_end = px_on_or_before(tk, end)
            _, v0 = px_on_or_before("VNINDEX", aday)
            _, v1 = px_on_or_before("VNINDEX", end)
            if p_end is None or end > DAYS[tk][-1]:
                out[f"{anchor}_r{H}"] = None; out[f"{anchor}_bhar{H}"] = None; continue
            r = p_end/PX[tk][aday] - 1
            b = v1/v0 - 1
            out[f"{anchor}_r{H}"] = round(100*r, 1)
            out[f"{anchor}_bhar{H}"] = None if tk == "VNINDEX" else round(100*(r-b), 1)
    rows.append(out)

with open('out/cycle_fear_results.json','w') as f: json.dump(rows, f, indent=1, ensure_ascii=False)

hdr = f"{'MA':<8}{'GRP':<4}{'NGANH':<12}{'DAY':<12}{'GIA':>9} | {'T0_r12':>7}{'T0_b6':>7}{'T0_b12':>7}{'T0_b24':>7} | {'T20_b12':>8}{'T20_b24':>8}"
print(hdr); print("-"*len(hdr))
for r in rows:
    if r.get("note"): print(f"{r['ticker']:<8}{r['group']:<4}{r['sector']:<12}  {r['note']}"); continue
    g = lambda k: ("  n/a" if r.get(k) is None else f"{r[k]:>7.1f}")
    print(f"{r['ticker']:<8}{r['group']:<4}{r['sector']:<12}{r['trough']:<12}{r['trough_px']:>9.0f} | "
          f"{g('T0_r12')}{g('T0_bhar6')}{g('T0_bhar12')}{g('T0_bhar24')} | {g('T20_bhar12'):>8}{g('T20_bhar24'):>8}")

# --- self-check: recompute 1 case tu 2 diem gia tho ---
hp = [r for r in rows if r['ticker']=='HPG'][0]
d0 = dt.date.fromisoformat(hp['trough']); d1 = add_months(d0, 12)
_, p1 = px_on_or_before('HPG', d1); _, v0 = px_on_or_before('VNINDEX', d0); _, v1 = px_on_or_before('VNINDEX', d1)
man = 100*((p1/hp['trough_px']-1) - (v1/v0-1))
print(f"\nSELF-CHECK HPG T0_bhar12: pipeline={hp['T0_bhar12']} recompute_tay={man:.1f} "
      f"({'PASS' if abs(man-hp['T0_bhar12'])<0.15 else 'FAIL'})")
print(f"  HPG trough Close={hp['trough_px']:.0f} @{hp['trough']} | +12M Close={p1:.0f} | VNINDEX {v0:.1f}->{v1:.1f}")
