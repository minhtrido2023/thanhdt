#!/usr/bin/env python3
"""Định giá MÙ GIÁ PAT — FCFE (V_dài) + LNST chuẩn hoá (V_ngắn).
Đọc tham số DUY NHẤT từ khối JSON trong ../assumptions_blind.md; dừng nếu md5 không khớp lock.txt.
Không đọc bất kỳ dữ liệu giá cổ phiếu nào. Chạy: python3 calc/model_blind.py (từ thư mục làm việc hoặc bất kỳ đâu).
"""
import csv, datetime as dt, hashlib, json, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASM = os.path.join(ROOT, "assumptions_blind.md")
LOCK = os.path.join(ROOT, "lock.txt")

# ---------- 0. khoá ----------
md5 = hashlib.md5(open(ASM, "rb").read()).hexdigest()
lock_md5 = re.search(r"\b([0-9a-f]{32})\b", open(LOCK).read()).group(1)
if md5 != lock_md5:
    sys.exit(f"MD5 MISMATCH: assumptions {md5} != lock {lock_md5}")
txt = open(ASM, encoding="utf-8").read()
A = json.loads(re.search(r"```json\n(.*?)\n```", txt, re.S).group(1))
SH = A["shares_mn"]  # triệu cp ⇒ tỷ đồng / triệu cp × 1000 = đ/cp
def ps(v_bn):
    return v_bn / SH * 1000.0

# ---------- 1. kiểm tổng khớp BCTC (số đọc từ ảnh gốc, mục A) ----------
checks = []
def chk(name, a, b, tol=0.01):
    ok = abs(a - b) <= tol
    checks.append((name, round(a, 3), round(b, 3), ok))
H1 = dict(rev=939.271, gp=186.994, lntt=166.638, lnst=156.393)
Q3 = dict(rev=440.032, gp=63.604, lntt=63.747, lnst=59.320)
N9 = dict(rev=1379.304, gp=250.598, lntt=230.384, lnst=215.713)
for k in H1:
    chk(f"H1+Q3=9T {k}", H1[k] + Q3[k], N9[k], 0.005)
chk("BS tong TS = No + VCSH", 233.744 + 708.446, 942.190, 0.002)
chk("VCSH = VDL+DTPT+LNCPP", 250.0 + 242.733 + 215.713, 708.446, 0.002)
chk("LNST quy 2026 (BQ) = 9T", 46.556 + 109.837 + 59.320, 215.713, 0.005)
chk("LNST quy 2024 (BQ) = KT 2024", 60.830 + 55.723 + 67.382 + 81.007, 264.94, 0.01)
chk("Q3 LNTT = LNgop+DTTC-CPTC-CPBH-QLDN", 63.604 + 11.371 - 1.467 - 5.049 - 4.711, 63.747, 0.002)
chk("Thue XK 9T / DT nuoc ngoai ~10%", 51.61 / 487.51, 0.10, 0.01)
chk("KTPL 2025 / LNST 2025 = 6%", 20.713 / 343.21, 0.06, 0.002)
chk("EBIT HD TTM = Q4/25 + 9T26", (439.45 - 82.15 - 18.16) - (347.084 - 63.192 - 12.851) + (250.598 - 32.289 - 12.750), 273.7, 0.1)  # mục B: 273,7

# ---------- 2. tham số ----------
nc = A["net_cash"]
NET_CASH = nc["cash"] + nc["htm"] - nc["debt"] - nc["ktpl_fund"]
G = A["g"]; KT = A["ktpl_rate"]; NWC0 = A["nwc"]; LAST = A["last_explicit_year"]
def r_of(d_dep=0.0, beta=None):
    beta = A["beta"] if beta is None else beta
    return A["r_anchor"] + beta * (A["dep_now"] + d_dep - A["dep_anchor"])
R = r_of()
ROLL = (dt.date.fromisoformat(A["val_date"]) - dt.date.fromisoformat(A["val_anchor"])).days / 365.0

def tax(y, override=None):
    if override is not None:
        return override
    t = A["tax"]
    return t["to_2030"] if y <= 2030 else (t["y2031_2032"] if y <= 2032 else t["from_2033"])

def dcf(ebit27, ebitq4, r=None, g=None, tax_override=None, cash_adj=0.0,
        tv_mult=1.0, finite_end=None, restoration=0.0, detail=False):
    """PV vốn cổ phần (tỷ đồng) tại val_date. Dòng tiền giữa kỳ; neo 30/09/2026."""
    r = R if r is None else r
    g = G if g is None else g
    rows = []
    pv = 0.0
    # Q4/2026: t = 0.125 năm, không ΔVLĐ
    f = ebitq4 * (1 - tax(2026, tax_override)) * (1 - KT)
    pv += f / (1 + r) ** 0.125
    rows.append((2026.75, ebitq4, f))
    nwc = NWC0
    end = finite_end if finite_end else LAST
    for y in range(2027, end + 1):
        e = ebit27 * (1 + g) ** (y - 2027)
        dnwc = g * nwc
        nwc += dnwc
        f = e * (1 - tax(y, tax_override)) * (1 - KT) - dnwc
        t = y - 2026 - 0.25  # giữa năm y tính từ 30/09/2026
        pv += f / (1 + r) ** t
        rows.append((y, e, f))
    t_end = end - 2026 + 0.25
    if finite_end:
        pv += (nwc - restoration) / (1 + r) ** t_end
        tv_pv = 0.0
    else:
        y1 = end + 1
        e1 = ebit27 * (1 + g) ** (y1 - 2027)
        f1 = (e1 * (1 - tax(y1, tax_override)) * (1 - KT) - g * nwc) * tv_mult
        tv = f1 / (r - g)
        tv_pv = tv / (1 + r) ** t_end
        pv += tv_pv
    eq = (pv + NET_CASH + cash_adj) * (1 + r) ** ROLL
    if detail:
        return eq, rows, tv_pv * (1 + r) ** ROLL
    return eq

SC = A["scenarios"]
def weighted(**kw):
    vals = {k: dcf(v["ebit_2027"], v["ebit_q4_2026"], **kw) for k, v in SC.items()}
    ev = sum(SC[k]["p"] * vals[k] for k in SC)
    return ev, vals

assert abs(sum(v["p"] for v in SC.values()) - 1) < 1e-9
EV, VALS = weighted()

# ---------- 3. V_ngắn ----------
vs = A["vshort"]
q = dict(vs["np_q"])
for k, add in vs["one_off_addback"].items():
    q[k] += add
keys = sorted(q)
ttm = [sum(q[keys[i - j]] for j in range(4)) for i in range(3, len(keys))]
ttm12 = ttm[-12:]
assert len(ttm12) == 12, len(ttm12)
NP_N = statistics.median(ttm12)
ttm_now = ttm[-1] - sum(vs["one_off_addback"].get(k, 0) for k in keys[-4:])  # TTM báo cáo thô
ROE = ttm_now / ((vs["equity_open"] + vs["equity_close"]) / 2)
b = min(max(G / ROE, 0.0), 0.8)
V_SHORT = NP_N * (1 - b) * (1 + G) / (R - G)
import math
D = abs(math.log(V_SHORT / EV))

# ---------- 4. độ nhạy ----------
sens = []
def add(group, name, v):
    sens.append((group, name, round(v, 1), round(ps(v)), round(ps(v) / ps(EV) - 1, 4)))
for beta in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.0, 0.005, 0.01):
        rr = r_of(d, beta)
        add("r_lai_huy_dong", f"beta={beta} dDep={d*1e4:+.0f}bp r={rr:.4f}", weighted(r=rr)[0])
for gg in (0.0, 0.02, 0.03):
    add("g", f"g={gg:.2f}", weighted(g=gg)[0])
add("tien_cam_co", "S1 tru 42,6 ty cam co cho cong ty thanh vien", weighted(cash_adj=-A["pledged"]["member_cos"])[0])
add("tien_cam_co", "S2 tru toan bo 441,6 ty cam co", weighted(cash_adj=-A["pledged"]["total"])[0])
L = A["legal"]
add("phap_ly_WARNING", "L1 thue 20% tu Q4/26 + truy thu 210 + moi truong 100",
    weighted(tax_override=L["tax_rate"], cash_adj=-(L["back_tax"] + L["env_liab"]))[0])
add("dat_thue", f"K dong tien toi {A['lease_end_year']}, khong TV, hoan nguyen {A['restoration_cost']}",
    weighted(finite_end=A["lease_end_year"], restoration=A["restoration_cost"])[0])
add("moat", "fade: FCFE gia tri cuoi x0,8", weighted(tv_mult=0.8)[0])
for name, v in SC.items():
    add("kich_ban_EBIT", f"{name} EBIT±10%: +10%", dcf(v["ebit_2027"] * 1.1, v["ebit_q4_2026"] * 1.1))
    add("kich_ban_EBIT", f"{name} EBIT±10%: -10%", dcf(v["ebit_2027"] * 0.9, v["ebit_q4_2026"] * 0.9))

# ---------- 5. thanh khoản (chỉ khối lượng) ----------
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from trading_bot.vn_market import is_holiday  # noqa: E402
vol = {}
with open(os.path.join(HERE, "bq_vol_pat.csv")) as fh:
    for row in csv.DictReader(fh):
        vol[dt.date.fromisoformat(row["time"])] = float(row["Volume"] or 0)
last = dt.date(2026, 11, 13)
def liq(months):
    start = dt.date(last.year, last.month, last.day)
    m = start.month - months
    y = start.year
    while m <= 0:
        m += 12; y -= 1
    start = dt.date(y, m, min(start.day, 28)) + dt.timedelta(days=1)
    d = start; sess = []
    while d <= last:
        if d.weekday() < 5 and not is_holiday(d):
            sess.append(vol.get(d, 0.0))
        d += dt.timedelta(days=1)
    return statistics.median(sess), sum(1 for x in sess if x <= 0), len(sess), start
liq6 = liq(6); liq3 = liq(3)

# ---------- 6. xuất ----------
out = os.path.join(HERE, "valuation_blind.csv")
with open(out, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["section", "item", "value_bn", "per_share_vnd", "rel_to_EV"])
    w.writerow(["meta", f"assumptions_md5={md5}", "", "", ""])
    w.writerow(["meta", f"r={R:.4f} g={G:.3f} net_cash_bn={NET_CASH:.2f} roll_years={ROLL:.4f}", "", "", ""])
    for k, v in VALS.items():
        w.writerow(["scenario", f"{k} (p={SC[k]['p']})", round(v, 1), round(ps(v)), round(ps(v) / ps(EV) - 1, 4)])
    w.writerow(["center", "EV_weighted_pre_liquidity", round(EV, 1), round(ps(EV)), 0])
    w.writerow(["center", "range_low_0.85", round(EV * 0.85, 1), round(ps(EV) * 0.85), -0.15])
    w.writerow(["center", "range_high_1.15", round(EV * 1.15, 1), round(ps(EV) * 1.15), 0.15])
    w.writerow(["vshort", f"NP_norm_median_TTM12={NP_N:.2f} ROE={ROE:.4f} b={b:.4f}", round(V_SHORT, 1), round(ps(V_SHORT)), round(V_SHORT / EV - 1, 4)])
    w.writerow(["vshort", f"D=|ln(Vngan/Vdai)|={D:.4f}", "", "", ""])
    for s in sens:
        w.writerow(["sens:" + s[0], s[1], s[2], s[3], s[4]])
    for dsc in A["liq_discounts"]:
        w.writerow(["liq_discount", f"CK {int(dsc*100)}% (Mike ap)", round(EV * (1 - dsc), 1), round(ps(EV) * (1 - dsc)), -dsc])
    w.writerow(["liquidity", f"6T tu {liq6[3]}: median_vol_cp={liq6[0]:.0f} phien_khong_khop={liq6[1]}/{liq6[2]}", "", "", ""])
    w.writerow(["liquidity", f"3T tu {liq3[3]}: median_vol_cp={liq3[0]:.0f} phien_khong_khop={liq3[1]}/{liq3[2]}", "", "", ""])
    for c in checks:
        w.writerow(["check", f"{c[0]}: {c[1]} vs {c[2]} -> {'OK' if c[3] else 'FAIL'}", "", "", ""])

# ---------- in ----------
print(f"md5 {md5} (khop lock)")
for c in checks:
    print(("OK  " if c[3] else "FAIL") + f" {c[0]}: {c[1]} vs {c[2]}")
print(f"r={R:.4f} g={G} net_cash={NET_CASH:.2f} ty ({ps(NET_CASH):.0f} d/cp) roll={ROLL:.3f}y")
for k, v in VALS.items():
    eq, rows, tvpv = dcf(SC[k]["ebit_2027"], SC[k]["ebit_q4_2026"], detail=True)
    print(f"{k:5s} p={SC[k]['p']}: {v:8.1f} ty = {ps(v):8.0f} d/cp | TV share {tvpv/eq:.1%} | FCFE 2027 {rows[1][2]:.1f}, 2033 {rows[7][2]:.1f}")
print(f"EV weighted = {EV:.1f} ty = {ps(EV):.0f} d/cp (truoc CK thanh khoan); vung [{0.85*ps(EV):.0f}; {1.15*ps(EV):.0f}]")
print(f"V_ngan: NP_norm={NP_N:.2f} (TTM12 {[round(x,1) for x in ttm12]}) ROE={ROE:.3f} b={b:.3f} -> {V_SHORT:.1f} ty = {ps(V_SHORT):.0f} d/cp; D={D:.3f}")
for s in sens:
    print(f"  [{s[0]}] {s[1]}: {s[3]} d/cp ({s[4]:+.1%})")
print(f"Thanh khoan 6T: median {liq6[0]:.0f} cp/phien, khong khop {liq6[1]}/{liq6[2]}; 3T: median {liq3[0]:.0f}, khong khop {liq3[1]}/{liq3[2]}")
if not all(c[3] for c in checks):
    sys.exit("BCTC CHECK FAIL")
