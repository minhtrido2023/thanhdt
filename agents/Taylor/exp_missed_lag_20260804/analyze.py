#!/usr/bin/env python3
"""Do THAT: ung vien LAG bi bo lo vi thieu tien vs LAG da mua that.
Nguon: plan files that (data/trade_plans) + gia BQ tav2_bq.ticker (Close da dieu chinh
=> total return da bao gom co tuc, dung ky luat coding_guidelines §21).
Endpoint = 2026-08-03 (phien co du lieu moi nhat; 08-04 dang giao dich, chua co close)."""
import csv, statistics, random, os

HERE = os.path.dirname(os.path.abspath(__file__))
END = "2026-08-03"

px = {}
for r in csv.DictReader(open(os.path.join(HERE, "prices_full.csv"))):
    px.setdefault(r["ticker"], {})[r["time"]] = float(r["Close"])

# --- Nhom BO LO: du dieu kien vao lenh, DEFER VI THIEU TIEN, cua so da het, khong bao gio mua ---
MISSED = [
    # (ticker, entry_date, account, size_vnd_du_kien, nguon)
    ("AGR", "2026-07-27", "ZaloPay", None, "plan_ZaloPay_2026-07-27.lag_status.deferred_insufficient_cash"),
    ("BSI", "2026-07-27", "ZaloPay", None, "same"),
    ("FTS", "2026-07-27", "ZaloPay", None, "same"),
    ("HCM", "2026-07-27", "ZaloPay", None, "same"),
    ("VND", "2026-07-27", "ZaloPay", None, "same"),
    ("CSV", "2026-07-28", "SpaceX", 90067500, "plan_SpaceX_2026-07-28.deferred_orders[BUY-CSV-LAG-04]"),
    ("EVF", "2026-07-28", "SpaceX", 72054000, "plan_SpaceX_2026-07-28.deferred_orders[BUY-EVF-LAG-05]"),
    ("PSI", "2026-07-28", "SpaceX", 72594405, "plan_SpaceX_2026-07-28.deferred_orders[BUY-PSI-LAG-06]"),
    ("VCI", "2026-07-28", "SpaceX", 72008966, "plan_SpaceX_2026-07-28.deferred_orders[BUY-VCI-LAG-07]"),
]
# --- Nhom DA MUA THAT: fill xac nhan tu broker raw (averagePrice), da loc accountNo ---
BOUGHT = [
    ("VPB", "2026-07-27", "ZaloPay", 700, 24950.0),
    ("CSV", "2026-07-28", "ZaloPay", 1000, 19750.0),
]

def ret(t, d0, d1=END):
    return (px[t][d1] / px[t][d0] - 1) * 100

SESS = sorted(px["VNINDEX"])
def nsess(d0, d1=END):
    return SESS.index(d1) - SESS.index(d0)

print("=" * 78)
print("A. NHOM BO LO (deferred vi THIEU TIEN, cua so het han, khong bao gio mua)")
print("=" * 78)
print(f"{'TICK':<6}{'ACCT':<9}{'ENTRY':<12}{'P_entry':>9}{'P_0803':>9}{'RET%':>8}{'phien':>6}  size_du_kien")
m = []
for t, d, a, sz, _ in MISSED:
    r = ret(t, d); m.append(r)
    print(f"{t:<6}{a:<9}{d:<12}{px[t][d]:>9.0f}{px[t][END]:>9.0f}{r:>+8.2f}{nsess(d):>6}  {sz and f'{sz/1e6:.1f}tr' or 'n/a'}")

print()
print("=" * 78)
print("B. NHOM DA MUA THAT (fill xac nhan broker)")
print("=" * 78)
print(f"{'TICK':<6}{'ACCT':<9}{'ENTRY':<12}{'fill':>9}{'P_entry':>9}{'P_0803':>9}{'RET%_BQ':>9}{'RET%_fill':>10}{'phien':>6}")
b, b_fill = [], []
for t, d, a, q, fp in BOUGHT:
    r = ret(t, d); rf = (px[t][END] / fp - 1) * 100
    b.append(r); b_fill.append(rf)
    print(f"{t:<6}{a:<9}{d:<12}{fp:>9.0f}{px[t][d]:>9.0f}{px[t][END]:>9.0f}{r:>+9.2f}{rf:>+10.2f}{nsess(d):>6}")

vn27, vn28 = ret("VNINDEX", "2026-07-27"), ret("VNINDEX", "2026-07-28")
print(f"\nVNINDEX cung cua so: tu 07-27 {vn27:+.2f}%  |  tu 07-28 {vn28:+.2f}%")

mm, bb = statistics.mean(m), statistics.mean(b)
print()
print("=" * 78)
print("C. SO SANH")
print("=" * 78)
print(f"BO LO   : N={len(m)}  mean {mm:+.2f}%  median {statistics.median(m):+.2f}%  "
      f"min {min(m):+.2f}%  max {max(m):+.2f}%  sd {statistics.stdev(m):.2f}")
print(f"DA MUA  : N={len(b)}  mean {bb:+.2f}%  median {statistics.median(b):+.2f}%  "
      f"min {min(b):+.2f}%  max {max(b):+.2f}%  (fill-basis mean {statistics.mean(b_fill):+.2f}%)")
print(f"CHENH   : {mm - bb:+.2f} pp (bo lo - da mua)")

# Bootstrap CI cho hieu trung binh — N cuc nho, chi de CHO THAY khoang rong den muc nao
random.seed(20260804)
diffs = []
for _ in range(20000):
    rm = [random.choice(m) for _ in m]
    rb = [random.choice(b) for _ in b]
    diffs.append(statistics.mean(rm) - statistics.mean(rb))
diffs.sort()
lo, hi = diffs[int(.025 * len(diffs))], diffs[int(.975 * len(diffs))]
print(f"Bootstrap 95% CI cho chenh lech: [{lo:+.2f}, {hi:+.2f}] pp  (20.000 resample)")
print(f"  -> khoang rong {hi - lo:.1f} pp, chua 0 = KHONG phan biet duoc voi 0.")

# Permutation test (exact-ish) — lai chi de cho thay N=2 khong the co y nghia
import itertools
allv = m + b
cnt = tot = 0
for combo in itertools.combinations(range(len(allv)), len(b)):
    bs = [allv[i] for i in combo]
    ms = [allv[i] for i in range(len(allv)) if i not in combo]
    if abs(statistics.mean(ms) - statistics.mean(bs)) >= abs(mm - bb): cnt += 1
    tot += 1
print(f"Permutation test (exact, {tot} hoan vi): p = {cnt/tot:.3f}")

print()
print("=" * 78)
print("D. THI NGHIEM TU NHIEN SACH NHAT — CSV cung ma, cung ngay, 2 account")
print("=" * 78)
print(f"  ZaloPay MUA THAT CSV 1.000cp @ 19.750 (07-28) -> 08-03 {px['CSV'][END]:.0f} = {(px['CSV'][END]/19750-1)*100:+.2f}%")
print(f"  SpaceX  DEFER CSV 4.500cp (90,07tr, thieu tien) -> cung gia, cung ngay, ret {ret('CSV','2026-07-28'):+.2f}% (BQ close basis)")
print(f"  => Chenh lech giua 2 account KHONG do chat luong tin hieu, chi do CO TIEN hay KHONG.")
print(f"  Gia tri SpaceX bo lo tren CSV: 90,07tr x {ret('CSV','2026-07-28'):+.2f}% = "
      f"{90.0675 * ret('CSV','2026-07-28') / 100:+.2f} tr VND (chua tinh 20 phien con lai cua hold 25)")

print()
print("=" * 78)
print("E. TIEN BI BO LO (chi cac lenh CO SIZE du kien tuong minh — SpaceX 07-28)")
print("=" * 78)
tot_sz = tot_pnl = 0
for t, d, a, sz, _ in MISSED:
    if sz:
        p = sz * ret(t, d) / 100
        tot_sz += sz; tot_pnl += p
        print(f"  {t}: {sz/1e6:>6.1f}tr x {ret(t,d):+6.2f}% = {p/1e6:+6.2f}tr")
print(f"  TONG: {tot_sz/1e6:.1f}tr trien khai hut -> P&L gia dinh {tot_pnl/1e6:+.2f}tr "
      f"({tot_pnl/tot_sz*100:+.2f}% tren von)")
print(f"  (5 ma ZaloPay 07-27 khong co size tuong minh trong plan -> khong quy ra tien duoc)")

print()
print("F. CANH BAO PHAM VI: hold LAG = 25 phien. Moi do duoc "
      f"{nsess('2026-07-27')}/25 va {nsess('2026-07-28')}/25 phien "
      f"({nsess('2026-07-28')/25*100:.0f}-{nsess('2026-07-27')/25*100:.0f}% cua chu ky). CHUA phai ket qua cuoi cung.")

# ============================================================================
print()
print("=" * 78)
print("G. CHUAN HOA — tru beta thi truong (VNINDEX) va so voi NGUON VON THAT SU")
print("=" * 78)
pk = {}
for r in csv.DictReader(open(os.path.join(HERE, "park_prices.csv"))):
    pk.setdefault(r["ticker"], {})[r["time"]] = float(r["Close"])
QTY = {'VCB':1300,'VHM':500,'CTG':2300,'BID':1900,'TCB':2000,'MBB':2400,'LPB':900,
       'HDB':1500,'ACB':1500,'SHB':1500,'TPB':800,'VIX':700,'SHS':200,'VPB':2300}
def park_ret(d0):
    v0 = sum(QTY[t]*pk[t][d0] for t in QTY); v1 = sum(QTY[t]*pk[t][END] for t in QTY)
    return (v1/v0 - 1)*100

print(f"{'TICK':<6}{'NHOM':<9}{'ENTRY':<12}{'RET%':>8}{'VNINDEX%':>10}{'EXCESS%':>9}")
ex_m, ex_b = [], []
for t, d, a, sz, _ in MISSED:
    e = ret(t,d) - ret("VNINDEX",d); ex_m.append(e)
    print(f"{t:<6}{'BO LO':<9}{d:<12}{ret(t,d):>+8.2f}{ret('VNINDEX',d):>+10.2f}{e:>+9.2f}")
for t, d, a, q, fp in BOUGHT:
    e = ret(t,d) - ret("VNINDEX",d); ex_b.append(e)
    print(f"{t:<6}{'DA MUA':<9}{d:<12}{ret(t,d):>+8.2f}{ret('VNINDEX',d):>+10.2f}{e:>+9.2f}")
print(f"\nEXCESS vs VNINDEX: BO LO mean {statistics.mean(ex_m):+.2f}pp (N=9) | "
      f"DA MUA mean {statistics.mean(ex_b):+.2f}pp (N=2) | chenh {statistics.mean(ex_m)-statistics.mean(ex_b):+.2f}pp")
print("  -> CA HAI nhom deu ~= hoac THUA thi truong. Khong nhom nao co alpha nhin thay duoc.")

print()
print("--- Doi chieu NGUON VON THAT: muon mua LAG phai BAN PARK (cash chi 4,5tr) ---")
for d0, names, lab in [("2026-07-27", ["AGR","BSI","FTS","HCM","VND"], "ZaloPay 07-27"),
                       ("2026-07-28", ["CSV","EVF","PSI","VCI"], "SpaceX 07-28")]:
    lagr = statistics.mean(ret(t, d0) for t in names)
    pr = park_ret(d0)
    print(f"  {lab}: LAG bo lo mean {lagr:+.2f}%  vs  PARK (nguon von) {pr:+.2f}%  "
          f"=> doi PARK->LAG se {lagr-pr:+.2f} pp")
print("  -> Trong cua so nay, BAN PARK de mua LAG se LAM XAU ket qua o CA HAI ngay.")
