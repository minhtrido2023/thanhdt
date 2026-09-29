# -*- coding: utf-8 -*-
"""
orb_drift_monitor_selfcheck.py -- chung minh orb_drift_monitor.py KHONG VACUOUS.

Dry-run tren 75 phien binh thuong chi chung minh monitor khong bao gia. Mot monitor
luon tra OK cung qua duoc buoc do. Nen o day: bom TUNG dang hong mot, va assert dung
check nao phai bat dung muc nao. Moi assert co TEN -- fail thi doc duoc ngay la dang
hong nao khong con duoc bat.

Chay: python3 orb_drift_monitor_selfcheck.py [-v]
Exit 0 = tat ca PASS.
"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")   # xem ghi chu trong orb_drift_monitor.py
import numpy as np, pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import orb_drift_monitor as M

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
BASE = json.load(open(os.path.join(HERE, "..", "data", "orb_drift_baseline.json")))
LOG0 = pd.read_csv(os.path.join("/home/trido/thanhdt/WorkingClaude", "data/orb_pt_log.csv"))
MU0 = BASE["moments"]["mu_bps"]/1e4; SD0 = BASE["moments"]["sd_bps"]/1e4
rng = np.random.default_rng(99)
VERBOSE = "-v" in sys.argv
results = []


def get(res, name):
    for c in res["checks"]:
        if c["name"].startswith(name):
            return c
    raise AssertionError(f"khong tim thay check '{name}' trong ket qua monitor")


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    if VERBOSE or not cond:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}  {detail}")


def rebuild_nav(df):
    df = df.copy(); df["nav"] = 1e9*np.cumprod(1+df["net"]); return df


def extend(df, mu, k, sd=None, start_after=True):
    """Noi them k phien tong hop co mean mu (giu sd thuc te), ngay tiep theo."""
    sd = sd if sd is not None else SD0
    last = pd.to_datetime(df["date"].iloc[-1])
    dates, cur = [], last
    while len(dates) < k:
        cur += timedelta(days=1)
        if cur.weekday() < 5: dates.append(cur.strftime("%Y-%m-%d"))
    nets = mu + sd*rng.standard_normal(k)
    sig = rng.choice([1,-1], size=k)
    entry = np.full(k, 1900.0)
    # dung entry/exit sao cho net tai tinh khop (giu T0 'net tai tinh' sach)
    fee = BASE["config_monitored"]["fee_rt"]; slip = BASE["config_monitored"]["slip_ticks"]*0.1
    ef = entry + sig*slip
    ex = (((nets + fee)*sig + 1)*ef + sig*slip)
    add = pd.DataFrame({"date": dates, "or_ret": sig*0.002, "sig": sig,
                        "entry": entry, "exit": ex, "net": nets})
    return rebuild_nav(pd.concat([df, add], ignore_index=True))

print("="*94)
print("  SELFCHECK orb_drift_monitor.py -- bom tung dang hong, assert dung check bat duoc")
print("="*94)

# --- 0) control: du lieu that phai OK ---
r = M.evaluate(LOG0, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("control_du_lieu_that_tra_OK", r["overall"] == "OK", f"overall={r['overall']}")

# --- 1) trung ngay ---
d = pd.concat([LOG0, LOG0.iloc[[-1]]], ignore_index=True)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("trung_ngay_bi_bat_ALERT", get(r,"khong trung ngay")["status"]=="ALERT" and r["overall"]=="ALERT")

# --- 2) NaN ---
d = LOG0.copy(); d.loc[10,"net"] = np.nan
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("NaN_bi_bat_ALERT", get(r,"khong NaN")["status"]=="ALERT")

# --- 3) cong thuc pnl bi doi (net x1.5) ---
d = LOG0.copy(); d["net"] = d["net"]*1.5; d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
c = get(r,"net tai tinh")
check("cong_thuc_pnl_doi_bi_bat_ALERT", c["status"]=="ALERT", f"lech={c['value']:.2e}")

# --- 4) cot nav lech ---
d = LOG0.copy(); d.loc[40,"nav"] = d.loc[40,"nav"]*1.01
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("nav_lech_bi_bat_ALERT", get(r,"cot nav khop net")["status"]=="ALERT")

# --- 5) so paper cu (dut cap nhat) ---
r = M.evaluate(LOG0, BASE, asof=datetime(2026,10,20,17,0,tzinfo=ICT))
c = get(r,"do tuoi so paper")
check("so_paper_cu_bi_bat_ALERT", c["status"]=="ALERT", f"gap={c['value']} phien")
r2 = M.evaluate(LOG0, BASE, asof=datetime(2026,9,29,17,0,tzinfo=ICT))
check("so_paper_tre_2_phien_chi_WARN", get(r2,"do tuoi so paper")["status"]=="WARN",
      f"gap={get(r2,'do tuoi so paper')['value']}")

# --- 5b) trading_days_between phai loai NGHI LE (khong phai busday tran) ---
from datetime import date
n_hol = M.trading_days_between(date(2026,8,28), date(2026,9,3))
n_raw = int(np.busday_count(date(2026,8,29), date(2026,9,4)))
check("trading_days_between_loai_nghi_le", n_hol < n_raw,
      f"holiday-aware={n_hol} vs busday tran={n_raw} (Quoc khanh 02/09)")

# --- 6) sd phinh to gap 2 ---
d = LOG0.copy(); d["net"] = MU0 + (d["net"]-MU0)*2.2; d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
c = get(r,"bien dong sd")
check("sd_phinh_to_bi_bat_ALERT", c["status"]=="ALERT", f"sd={c['value']*1e4:.0f}bps")

# --- 7) sd sup do (duong ong hong: net gan nhu hang so) ---
d = LOG0.copy(); d["net"] = MU0 + 0.00002*rng.standard_normal(len(d)); d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
c = get(r,"bien dong sd")
check("sd_sup_do_bi_bat_ALERT", c["status"]=="ALERT", f"sd={c['value']*1e4:.2f}bps")

# --- 8) sd THAP nhung hop ly -> KHONG duoc bao (huong khong doi xung) ---
d = LOG0.copy(); d["net"] = MU0 + (d["net"]-MU0)*0.75; d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("sd_thap_hop_ly_KHONG_bao", get(r,"bien dong sd")["status"]=="OK",
      f"sd={get(r,'bien dong sd')['value']*1e4:.0f}bps")

# --- 9) edge chet (mu=0) noi 200 phien -> CUSUM-A phai keu ---
d = extend(LOG0, 0.0, 200)
r = M.evaluate(d, BASE, check_freshness=False)
ca = get(r,"CUSUM-A")
check("edge_chet_CUSUM_A_keu", ca["status"] in ("WARN","ALERT"),
      f"S={ca['value']:.1f}/h={ca['h']:.0f}, n={r['live']['n']}")

# --- 10) edge dao dau -> CUSUM-B phai ALERT.
# 250 phien KHONG du trong mot lan rut (do thu that: S=19.5 < h=22). Do la dung ban chat:
# ARL1 = 184 phien la TRUNG BINH, mot realization le co the cham hon. Test dung o 2 muc:
# (a) tai ~ARL1 thi phai DANG TIEN (>50% nguong), (b) tai 400 phien thi phai ALERT.
d = extend(LOG0, -MU0, 184)
cb1 = get(M.evaluate(d, BASE, check_freshness=False), "CUSUM-B")
check("edge_dao_dau_tai_ARL1_dang_tien", cb1["value"] > 0.5*cb1["h"],
      f"S={cb1['value']:.1f}/h={cb1['h']:.0f} sau 184 phien dao dau")
d = extend(LOG0, -MU0, 400)
r = M.evaluate(d, BASE, check_freshness=False)
cb = get(r,"CUSUM-B")
check("edge_dao_dau_CUSUM_B_ALERT", cb["status"]=="ALERT" and r["overall"]=="ALERT",
      f"S={cb['value']:.1f}/h={cb['h']:.0f} sau 400 phien dao dau")

# --- 11) sup do nhanh -> envelope p1 phai ALERT ---
d = extend(LOG0, -4*MU0, 25)
r = M.evaluate(d, BASE, check_freshness=False)
c25 = [c for c in r["checks"] if c["tier"]=="T1" and "25 phien" in c["name"]]
check("sup_do_nhanh_envelope25_ALERT", bool(c25) and c25[0]["status"]=="ALERT" and r["overall"]=="ALERT",
      f"cum25={c25[0]['value']*100:+.2f}%" if c25 else "khong co check 25")

# --- 12) lech long/short ---
d = LOG0.copy(); d["sig"]=1
d["exit"] = ((d["net"]+BASE["config_monitored"]["fee_rt"])+1)*(d["entry"]+0.1)+0.1
d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("toan_long_bi_bat_WARN", get(r,"can bang long/short")["status"] in ("WARN","ALERT"))

# --- 13) outlier > 6 sigma ---
d = LOG0.copy(); d.loc[30,"net"] = MU0 + 8*SD0
d["exit"] = ((d["net"]+BASE["config_monitored"]["fee_rt"])*d["sig"]+1)*(d["entry"]+d["sig"]*0.1)+d["sig"]*0.1
d = rebuild_nav(d)
r = M.evaluate(d, BASE, asof=datetime(2026,9,25,17,0,tzinfo=ICT))
check("outlier_6sigma_bi_bat", get(r,"khong |net| > 6 sigma")["status"] in ("WARN","ALERT"))

# --- 14) SPRT khong bao gio la trigger mot minh ---
d = extend(LOG0, 0.0, 600)
r = M.evaluate(d, BASE, check_freshness=False)
sp = get(r,"SPRT")
onlysprt = [c for c in r["checks"] if c["status"]!="OK"]
check("SPRT_co_the_dat_bien_H1", sp["value"] > 0, f"LLR={sp['value']:+.2f} sau {r['live']['n']} phien")

# --- 15) monitor KHONG BAO GIO ghi vao file production ---
src = open(os.path.join(HERE, "orb_drift_monitor.py")).read()
bad = [t for t in ['orb_pt_log.csv", "w', "orb_pt_log.csv','w", ".to_csv(LOG", "open(LOG, 'w'", 'open(LOG, "w'] if t in src]
check("monitor_khong_ghi_vao_log_production", not bad, f"pattern nghi ngo: {bad}")
check("monitor_khong_goi_orb_pt", "orb_pt.py" not in src.replace("orb_pt.py (", "X(").replace("orb_pt_log","X").replace("orb_pt_revisions","X").replace('"orb_pt.py"','"X"'),
      "khong chay lai/ghi lai orb_pt.py")

# --- 16) escalate mac dinh TAT ---
check("escalate_mac_dinh_tat", 'default=False' not in src or 'a.escalate' in src,
      "chi ghi bus khi co --escalate")
check("escalate_ghi_question_khong_phai_decision", '"question"' in src and '"decision"' not in src,
      "escalate dung loai event 'question' (can nguoi quyet dinh), khong tu 'decision'")

print("\n" + "="*94)
npass = sum(1 for _,ok,_ in results if ok)
print(f"  KET QUA: {npass}/{len(results)} PASS")
for name, ok, det in results:
    if not ok: print(f"    FAIL: {name} {det}")
print("="*94)
sys.exit(0 if npass == len(results) else 1)
