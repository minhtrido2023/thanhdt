#!/usr/bin/env python3
"""VIỆC ĐO THÊM (arch-review vòng 1): dòng nav_history mang cờ `nav_is_estimate` lệch bao nhiêu so
với "NAV thật"?

Sự thật đọc từ code + dữ liệu (không phải giả định): dòng ước tính do `daily_nav_snapshot.py
--from-raw` ghi cho một ngày QUÁ KHỨ thiếu dòng, và KHÔNG BAO GIỜ được thay bằng một "NAV thật"
về sau — nên không có cặp (tạm tính, số chốt sau đó) để trừ nhau. Thứ khác nhau giữa hai đường
ghi chỉ là GIÁ định giá cổ phiếu: đường thường dùng giá broker, đường --from-raw dùng giá đóng cửa
chưa điều chỉnh của BQ (cột Price); tiền/nợ/egg đều lấy từ cùng bản ghi balances của broker.

Vì vậy đo bằng hai phép thay thế, đều trên dữ liệu còn trên đĩa:
  (1) ĐỐI CHỨNG trên các ngày KHÔNG ước tính (có dòng thật): nếu ngày đó bị định giá theo kiểu
      ước tính (KL cuối phiên × BQ Price) thì giá trị cổ phiếu lệch dòng thật bao nhiêu % NAV.
      Đây là phân phối sai số của CHÍNH phương pháp ước tính, đo ở nơi có đáp án.
  (2) Trên các ngày ƯỚC TÍNH: giá trị cổ phiếu của dòng lệch bao nhiêu % NAV so với định giá bằng
      `marketPrice` của broker trong cùng bản ghi positions cuối phiên.
  (3) Đếm trên lịch sử: nếu chỉ đẩy tin khi "không có số" hoặc "số tạm tính cách ngưỡng dưới X
      điểm %" thì bớt được bao nhiêu tin (dùng state seed của thư mục này, tới 2026-10-09).
KL = bản ghi positions cuối cùng của account, chụp từ giờ đóng cửa trở đi (cùng hàm monitor dùng).

⚠️ Phép (1) là định giá NGÂY THƠ (không có cổng corp-action của `--from-raw` thật). Ngày lệch lớn
duy nhất, 2026-08-05 (SpaceX +7,97% / ZaloPay +5,03% NAV), là ca VHM tách 1:2: tối 05/08 broker đã
ghi KL mới (500→1.000 / 300→600) và giá sau tách (76.500) trong khi BQ Price còn là giá trước tách
(153.000). `--from-raw` thật gặp ca này thì quy KL về trước sự kiện hoặc từ chối ghi (rc=4), nên
con số đó là sai số của phép đo ngây thơ, KHÔNG phải của dòng ước tính.

Dùng: python3 measure_estimate_rows.py --price-csv bq_price_held_20260701_20261012_exp.csv \\
          --state-dir seed
"""
import argparse
import csv
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "bin")))
import nav_loss_brake_monitor as m  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--price-csv", required=True)
ap.add_argument("--state-dir", required=True)
args = ap.parse_args()
price = {}
with open(args.price_csv, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        price[(r["ticker"], r["time"])] = float(r["Price"])

ctx = m.Ctx()
ctx.pos_cache = {}
profiles = m.load_profiles(ctx.secrets_path)


def pctl(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


for account in ("SpaceX", "ZaloPay"):
    rows = list(csv.DictReader(open(os.path.join(ctx.exec_dir, f"nav_history_{account}.csv"),
                                    encoding="utf-8")))
    ctrl, est, skipped = [], [], []
    for r in rows:
        d = m.datetime.date.fromisoformat(r["date"])
        nav, mtm = float(r["nav"]), float(r["mtm_stock"])
        is_est = r["nav_is_estimate"] == "True"
        if not m.is_session(d):
            skipped.append(f"{d}: không phải phiên")
            continue
        if m.close_capture_problem(d, r["balance_ts"]) and not is_est:
            skipped.append(f"{d}: dòng thật không phải giá chốt ({r['balance_ts']})")
            continue
        pos, ts, why = m.close_positions(ctx, profiles[account]["account_id"], d)
        if pos is None:
            skipped.append(f"{d}: {why[:70]}")
            continue
        missing = [p["symbol"] for p in pos if (p["symbol"], r["date"]) not in price]
        if missing:
            skipped.append(f"{d}: CSV không có giá {missing}")
            continue
        v_bq = sum(float(p["openQuantity"]) * price[(p["symbol"], r["date"])] for p in pos)
        v_mp = sum(float(p["openQuantity"]) * float(p.get("marketPrice") or 0) for p in pos)
        rec = {"date": r["date"], "bq_vs_row": (v_bq - mtm) / nav, "mp_vs_row": (v_mp - mtm) / nav,
               "mp_vs_bq": (v_mp - v_bq) / nav}
        (est if is_est else ctrl).append(rec)
    print(f"\n=== {account}: {len(rows)} dòng · {len(est)} dòng ước tính đo được · "
          f"{len(ctrl)} dòng thật làm đối chứng · bỏ {len(skipped)}")
    for s in skipped:
        print(f"   bỏ {s}")
    a = [abs(x["bq_vs_row"]) for x in ctrl]
    print(f"  (1) ĐỐI CHỨNG — |KL×BQ Price − mtm_stock dòng thật| / NAV trên {len(a)} ngày có dòng thật:")
    print(f"      trung vị {statistics.median(a)*100:.3f}% · p90 {pctl(a, .9)*100:.3f}% · "
          f"p95 {pctl(a, .95)*100:.3f}% · lớn nhất {max(a)*100:.3f}%")
    for x in sorted(ctrl, key=lambda x: -abs(x["bq_vs_row"]))[:5]:
        print(f"        {x['date']}: BQ−dòng {x['bq_vs_row']*100:+.3f}% NAV · "
              f"marketPrice−dòng {x['mp_vs_row']*100:+.3f}% NAV")
    n_big = sum(1 for v in a if v > 0.005)
    print(f"      số ngày lệch > 0,5% NAV: {n_big}/{len(a)} · > 1% NAV: "
          f"{sum(1 for v in a if v > 0.01)}/{len(a)} · > 2% NAV: {sum(1 for v in a if v > 0.02)}/{len(a)}")
    print(f"  (2) DÒNG ƯỚC TÍNH — so với định giá marketPrice của broker (cùng bản ghi positions):")
    for x in est:
        print(f"        {x['date']}: KL×BQ Price−dòng {x['bq_vs_row']*100:+.3f}% NAV (kiểm tái lập) · "
              f"marketPrice−dòng {x['mp_vs_row']*100:+.3f}% NAV")
    if est:
        b = [abs(x["mp_vs_row"]) for x in est]
        print(f"      |marketPrice − dòng ước tính| / NAV: trung vị {statistics.median(b)*100:.3f}% · "
              f"lớn nhất {max(b)*100:.3f}%")

# ---- (3) luật "chỉ đẩy tin khi không có số, hoặc tạm tính cách ngưỡng dưới X điểm %"
LAST = m.datetime.date(2026, 10, 9)
ctx = m.Ctx(state_dir=os.path.abspath(args.state_dir),
            now=m.datetime.datetime(2026, 10, 9, 22, 5, tzinfo=m.ICT))
ctx.pos_cache = {}
th, th_err = m.load_thresholds(ctx.rules_path)
print(f"\n=== (3) Nếu chỉ đẩy tin khi 'không có số' HOẶC 'tạm tính cách ngưỡng dưới X điểm %' — "
      f"đếm trên lịch sử tới {LAST}")
for account in ("SpaceX", "ZaloPay"):
    chain = m.build_chain(ctx, account, profiles[account], ctx.now.date())
    d, n, alert = chain["ledger"][0]["date"], 0, []
    while d < LAST:
        d += m.datetime.timedelta(days=1)
        if not m.is_session(d):
            continue
        n += 1
        g = m.lever_guard(ctx, account, profiles[account]["account_id"], d, th["lever_package_id"],
                          [], [])
        res = m.evaluate(ctx, account, d, chain, th, th_err, [], g)
        bad = [res[b] for b in m.BRAKES if res[b]["status"] in m.ALERTING]
        if not bad:
            continue
        only_est = all(r.get("value") is not None
                       and all("nav_is_estimate" in p for p in r["reason"].split("; ")) for r in bad)
        dist = min((r["distance_pp"] for r in bad if r.get("value") is not None), default=None)
        alert.append((d, only_est, any(r.get("value") is None for r in bad), dist))
    est = [x for x in alert if x[1]]
    nonum = sum(1 for x in alert if x[2])
    print(f"  {account}: {n} phiên · {len(alert)} phiên kêu = {len(est)} phiên CHỈ vì cờ "
          f"nav_is_estimate (đều có số tạm tính) + {nonum} phiên có ít nhất một phanh 'không có số' "
          f"+ {len(alert) - len(est) - nonum} phiên có số tạm tính vì lý do khác (giờ chụp / thiếu "
          f"phiên trước)")
    ds = sorted(x[3] for x in est)
    print(f"     khoảng cách tới ngưỡng của số tạm tính ở {len(est)} phiên đó: nhỏ nhất "
          f"{ds[0]:.2f}pp · trung vị {ds[len(ds) // 2]:.2f}pp")
    for X in (1.0, 2.0, 3.0):
        print(f"     X = {X:.0f}pp ⇒ còn {sum(1 for v in ds if v < X)}/{len(est)} phiên phải đẩy tin")
