# -*- coding: utf-8 -*-
"""
orb_drift_monitor.py -- CANH BAO SOM lech ky vong cho paper program ORB intraday.

=====================  PHAM VI -- DOC TRUOC KHI CHAY  =========================
Co che nay CHI GIAM SAT. Nó KHONG:
  - doi bat ky tham so chien luoc nao,
  - dung paper program,
  - ghi vao data/orb_pt_log.csv hay bat ky file production nao.
Moi hanh dong dua tren canh bao phai qua Mike/user. Script chi ghi log + (tuy chon)
escalate mot bus question cho Mike. Exit code: 0=OK 10=WARN 20=ALERT 2=loi ky thuat.
===============================================================================

TAI SAO THIET KE NHU THE NAY (khong phai rolling-Sharpe, khong phai CUSUM don):
  SNR cua chien luoc = mu/sd = 0.1003 moi phien (mu0 +9.34bps, sd 93.1bps). Hai he qua
  do lai bang mo phong ARL tren residual THAT (kurtosis 5.76), khong lay tu bang Gauss:
   (1) Can ~614 phien de phan biet mu0 voi 0 o alpha 5% / power 80%. Hien co 75.
   (2) CUSUM nham vao "edge ve 0" o nguong du nhay (h=5-10) cho ty so ARL0/ARL1 chi
       1.6-2.2 -- tuc bao dong khi HONG va khi KHONG hong xay ra gan nhu nhu nhau.
       Rolling-N Sharpe con te hon: o N=25, sd cua Sharpe annualised ~3.2.
  => Khong ton tai nguong nao vua nhay vua it bao gia TREN CHUOI LOI NHUAN. Nen thiet ke
  chia 4 tang theo DO PHAT HIEN DUOC, va noi thang tang nao la "phat hien that", tang nao
  chi la "hien trang":

  T0 SUC KHOE SO LIEU (power cao, phat hien trong 1 phien) -- day la noi co gia tri that.
     Hau het cach mot paper program "lech ky vong" trong thuc te la HONG DUONG ONG
     (vendor doi du lieu, log dut, cong thuc pnl doi, size sai), khong phai alpha decay.
  T1 ENVELOPE PHAN PHOI (calibrated by construction, khong claim power): cum cua k phien
     gan nhat so voi phan phoi cum cua k phien LIEN TIEP trong 670 phien pre-live.
     Nguong p5 fire dung 5% thoi gian khi moi thu binh thuong -- con so nay la DINH NGHIA
     cua nguong, khong phai uoc luong.
  T2 CUSUM (phat hien CHAM, chi bat su co lon): hai so do song song
     A_warn  k=mu0/2, h=18 -> ARL0 809 phien,  ARL1 215 phien ("edge ve 0")
     B_alert k=0,      h=22 -> ARL0 3580 phien, ARL1 184 phien ("edge dao dau")
  T3 SPRT -- KHONG phai trigger, la THANH TIEN DO. In ra LLR va con bao nhieu phien nua
     moi du bang chung ket luan, de khong ai tuong da co ket luan.

Nguon ky vong: orb_drift_baseline.json (dong bang tu 670 phien PRE-LIVE cua DUNG config
dang deploy, job Taylor_20260925_103217). Khong dung phien live nao de dung ky vong.

Chay:
  python3 orb_drift_monitor.py                 # kiem tra hom nay
  python3 orb_drift_monitor.py --json          # chi in JSON
  python3 orb_drift_monitor.py --replay         # dry-run: phat lai tung phien, dem bao gia
  python3 orb_drift_monitor.py --escalate       # cho phep ghi bus question khi ALERT
"""
import sys, io, os, json, argparse, math, hashlib
# reconfigure thay vi tao TextIOWrapper moi: khi file nay duoc IMPORT boi mot script da
# tu wrap stdout (selfcheck), wrapper cu bi GC va DONG luon buffer goc -> "I/O operation
# on closed file". Loi nay chi hien duoi python3.12 ($DNA_PYEXE), khong hien duoi 3.10.
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
WC   = "/home/trido/thanhdt/WorkingClaude"
LOG  = os.path.join(WC, "data/orb_pt_log.csv")
BASE = os.path.join(HERE, "orb_drift_baseline.json")
REVLOG = os.path.join(WC, "data/orb_pt_revisions.log")
ICT  = ZoneInfo("Asia/Ho_Chi_Minh")
sys.path.insert(0, HERE)
from normstat import ncdf

OK, WARN, ALERT = "OK", "WARN", "ALERT"
RANK = {OK: 0, WARN: 1, ALERT: 2}


def trading_days_between(d0, d1, vn_holidays=None):
    """So phien giao dich giua 2 ngay (loai T7/CN + nghi le VN). vn_holidays BAT BUOC
    truyen tuong minh hoac de None de tu lay tu trading_bot.vn_market.is_holiday --
    np.busday_count tran tung dem 4 'trading day' cho ky nghi Quoc khanh (coding_guidelines
    §16 RULE 2, incident 2026-09-04)."""
    if vn_holidays is None:
        sys.path.insert(0, WC)
        from trading_bot.vn_market import is_holiday
        hol = is_holiday
    else:
        hol = lambda d: d in vn_holidays
    n, cur = 0, d0 + timedelta(days=1)
    while cur <= d1:
        if cur.weekday() < 5 and not hol(cur):
            n += 1
        cur += timedelta(days=1)
    return n


def chi2_sf(x, k):
    """P(Chi2_k > x), k chan hoac le, chuoi khong can scipy (Wilson-Hilferty cho k lon)."""
    if x <= 0: return 1.0
    z = ((x / k) ** (1.0/3.0) - (1 - 2.0/(9*k))) / math.sqrt(2.0/(9*k))
    return 1.0 - ncdf(z)


def evaluate(log, base, asof=None, check_freshness=True):
    """Tra ve dict ket qua. log = DataFrame da doc; base = baseline dict."""
    mu0 = base["moments"]["mu_bps"] / 1e4
    sd0 = base["moments"]["sd_bps"] / 1e4
    x = log["net"].values
    n = len(x)
    checks = []

    def add(tier, name, status, detail, **kw):
        checks.append(dict(tier=tier, name=name, status=status, detail=detail, **kw))

    # ---------------- T0 SUC KHOE SO LIEU ----------------
    d = pd.to_datetime(log["date"])
    dup = log["date"].duplicated().sum()
    add("T0", "khong trung ngay", ALERT if dup else OK,
        f"{dup} ngay trung" if dup else f"{n} ngay, 0 trung")
    nonmono = int((d.diff().dt.days.dropna() <= 0).sum())
    add("T0", "ngay tang don dieu", ALERT if nonmono else OK,
        f"{nonmono} vi tri khong tang" if nonmono else "OK")
    nan = int(log[["or_ret","sig","entry","exit","net"]].isna().sum().sum())
    add("T0", "khong NaN", ALERT if nan else OK, f"{nan} o NaN" if nan else "OK")

    # net tai tinh tu entry/exit/sig -> bat cong thuc pnl bi doi
    cfg = base["config_monitored"]
    ef = log["entry"] + log["sig"] * cfg["slip_ticks"] * 0.1
    xf = log["exit"]  - log["sig"] * cfg["slip_ticks"] * 0.1
    net_rc = log["sig"] * (xf/ef - 1) - cfg["fee_rt"]
    worst = float((net_rc - log["net"]).abs().max())
    add("T0", "net tai tinh tu entry/exit/sig", ALERT if worst > 1e-9 else OK,
        f"lech lon nhat {worst:.2e}" + (" -- cong thuc pnl da DOI" if worst > 1e-9 else ""),
        value=worst)

    if "nav" in log.columns:
        nav_rc = 1e9 * np.cumprod(1 + x)
        wn = float(np.abs(nav_rc - log["nav"].values).max())
        add("T0", "cot nav khop net", ALERT if wn > 1.0 else OK, f"lech lon nhat {wn:,.2f} VND", value=wn)

    if os.path.exists(REVLOG):
        nrev = sum(1 for _ in open(REVLOG) if _.strip())
        add("T0", "vendor revision log", WARN if nrev else OK,
            f"{nrev} dong -- vendor da sua so ngay cu, so cu duoc giu (dung), nhung can doc")
    else:
        add("T0", "vendor revision log", OK, "chua co revision nao")

    out6 = int((np.abs(x - mu0) > 6*sd0).sum())
    add("T0", "khong |net| > 6 sigma", WARN if out6 else OK,
        f"{out6} phien vuot 6 sigma ({6*sd0*1e4:.0f}bps)" +
        (" -- kiem tra tape/roll hop dong" if out6 else ""))

    if check_freshness:
        last = d.iloc[-1].date()
        today = (asof or datetime.now(ICT)).date()
        gap = trading_days_between(last, today)
        st = OK if gap <= 1 else (WARN if gap <= 3 else ALERT)
        add("T0", "do tuoi so paper", st,
            f"phien cuoi {last}, cach hom nay {gap} phien giao dich (nguong WARN>1, ALERT>3)",
            value=gap)

    # Bien dong (sd) -- thu DUY NHAT trong phan phoi loi nhuan do duoc o n nho.
    # Dung ENVELOPE BOOTSTRAP tu 670 phien pre-live, KHONG dung chi2: kurtosis = 5.76 nen
    # gia dinh chuan cua chi2 sai va p-value cua no lech. Dry-run vong 1 da chung minh:
    # bien ban chi2 bao ALERT 8/56 lan tren chinh 75 phien BINH THUONG (bao gia 14%).
    # Huong cung KHONG doi xung: sd THAP hon ky vong khong phai van de (chi la phien em);
    # chi bao khi (a) sd VUOT tran -> rui ro dang bi uoc thieu, hoac (b) sd SUP DO
    # (< p0.5 VA < 50% ky vong) -> dau hieu duong ong hong, khong phai may man.
    sdenv = base.get("sd_envelope_by_k_sessions", {})
    if n >= 20 and sdenv:
        kk = max((int(k) for k in sdenv if int(k) <= n), default=None)
        if kk:
            sdl = float(np.std(x[-kk:], ddof=1)); e = sdenv[str(kk)]
            if sdl > e["p99.5"]:   st, why = ALERT, "VUOT tran p99.5 -- rui ro dang bi uoc thieu"
            elif sdl > e["p95"]:   st, why = WARN,  "tren p95"
            elif sdl < e["p0.5"] and sdl < 0.5*sd0: st, why = ALERT, "SUP DO -- nghi duong ong hong"
            else:                  st, why = OK,    "trong envelope"
            add("T0", f"bien dong sd ({kk} phien)", st,
                f"sd {sdl*1e4:.1f}bps | p0.5 {e['p0.5']*1e4:.1f} p5 {e['p5']*1e4:.1f} "
                f"p50 {e['p50']*1e4:.1f} p95 {e['p95']*1e4:.1f} p99.5 {e['p99.5']*1e4:.1f}bps"
                f" -- {why}", value=sdl)
        # can bang long/short
        lf = float((log["sig"] > 0).mean()); lf0 = base["moments"]["long_frac"]
        se = math.sqrt(lf0*(1-lf0)/n); z = (lf-lf0)/se if se > 0 else 0.0
        p = 2*(1-ncdf(abs(z)))
        add("T0", "can bang long/short", OK if p > 0.01 else WARN,
            f"long {lf*100:.1f}% vs ky vong {lf0*100:.1f}%, z = {z:+.2f}, p = {p:.3f}", value=p)
        # bien do OR (dac tinh tape)
        ma = float(log["or_ret"].abs().mean()); ma0 = base["moments"]["mean_abs_or_ret"]
        sa0 = base["moments"]["sd_abs_or_ret"]
        z2 = (ma-ma0)/(sa0/math.sqrt(n)); p3 = 2*(1-ncdf(abs(z2)))
        add("T0", "bien do OR (dac tinh tape)", OK if p3 > 0.01 else WARN,
            f"mean|OR| live {ma*100:.3f}% vs ky vong {ma0*100:.3f}%, z = {z2:+.2f}, p = {p3:.3f}",
            value=p3)

    # ---------------- T1 ENVELOPE ----------------
    # CHI 2 cua so tinh vao trang thai: dai nhat (toan bo lich su live) + 25 phien (gan day).
    # Vong 1 cua dry-run tinh CA 6 cua so chong lan nhau => ty le WARN doi len 19.6% tren
    # du lieu binh thuong, cao hon nhieu muc 5% ma nguong p5 hua. Cua so trung gian van
    # duoc in ra nhung gan tier "T1i" (INFO) va KHONG tinh vao trang thai tong.
    env = base["cum_envelope_by_k_sessions"]
    ks = sorted((int(k) for k in env if int(k) <= n), reverse=True)
    voting = {ks[0]} | ({25} if 25 in ks else set())
    for k in ks:
        cum = float(np.prod(1 + x[-k:]) - 1)
        e = env[str(k)]
        st = ALERT if cum < e["p1"] else (WARN if cum < e["p5"] else OK)
        vote = k in voting
        add("T1" if vote else "T1i", f"cum {k} phien gan nhat vs envelope", st if vote else OK,
            f"{cum*100:+.2f}% | p1 {e['p1']*100:+.2f}% p5 {e['p5']*100:+.2f}% "
            f"p50 {e['p50']*100:+.2f}% p95 {e['p95']*100:+.2f}%"
            + ("" if vote else f"  [INFO, khong tinh vao trang thai; muc thô = {st}]"), value=cum)

    # ---------------- T2 CUSUM ----------------
    for key, lbl in [("A_warn", "CUSUM-A (edge -> 0)"), ("B_alert", "CUSUM-B (edge dao dau)")]:
        c = base["cusum"][key]; k_ref = c["k_bps"]/1e4; h = c["h"]
        S = 0.0; Smax = 0.0; peak_i = -1
        for i, v in enumerate(x):
            S = max(0.0, S - (v - k_ref)/sd0)
            if S > Smax: Smax, peak_i = S, i
        st = OK
        if S > h: st = WARN if key == "A_warn" else ALERT
        add("T2", lbl, st,
            f"S = {S:.2f} / h = {h:.0f} ({S/h*100:.0f}% nguong); dinh {Smax:.2f} tai phien "
            f"{peak_i+1} ({log['date'].iloc[peak_i] if peak_i>=0 else '-'}); "
            f"ARL0 {c['arl0_sessions']} ph / ARL1 {c['arl1_sessions']} ph", value=S, h=h)

    # ---------------- T3 SPRT (thanh tien do, khong phai trigger) ----------------
    sp = base["sprt"]
    llr_step = (0.0 - mu0)/sd0**2
    llr = float(np.sum(llr_step * (x - (mu0 + 0.0)/2)))
    up, lo = sp["bound_accept_h1"], sp["bound_accept_h0"]
    if llr >= up:   sst, txt = ALERT, "DA DU bang chung: edge chet (H1)"
    elif llr <= lo: sst, txt = OK,    "DA DU bang chung: edge con song (H0)"
    else:
        rate = llr/n if n else 0.0
        need = (f"~{int((up-llr)/rate)} phien nua den bien H1" if rate > 1e-12 else
                f"~{int((lo-llr)/rate)} phien nua den bien H0" if rate < -1e-12 else "khong tien trien")
        sst, txt = OK, f"CHUA DU bang chung ca hai chieu ({need} theo nhip hien tai)"
    add("T3", "SPRT (tien do, KHONG phai trigger)", sst,
        f"LLR = {llr:+.3f} trong [{lo:+.3f} .. {up:+.3f}] -- {txt}", value=llr)

    worst_rank = max(RANK[c["status"]] for c in checks)
    overall = [k for k, v in RANK.items() if v == worst_rank][0]
    live = dict(n=n, mean_bps=float(x.mean()*1e4), sd_bps=float(x.std(ddof=1)*1e4),
                sharpe=float(x.mean()/x.std(ddof=1)*math.sqrt(252)) if x.std(ddof=1) > 0 else 0.0,
                wr=float((x > 0).mean()), cum=float(np.prod(1+x)-1))
    return dict(asof=(asof or datetime.now(ICT)).isoformat(), overall=overall,
                live=live, expected={"mean_bps": mu0*1e4, "sd_bps": sd0*1e4,
                "sharpe": float(mu0/sd0*math.sqrt(252))}, checks=checks)


def render(res):
    L, E = res["live"], res["expected"]
    print("=" * 94)
    print(f"  ORB DRIFT MONITOR -- CHI GIAM SAT, khong doi tham so, khong dung paper")
    print(f"  asof {res['asof']}  |  TRANG THAI TONG: {res['overall']}")
    print("=" * 94)
    print(f"  Live  n={L['n']:>4}  mean {L['mean_bps']:+7.2f}bps  sd {L['sd_bps']:6.2f}bps"
          f"  Sharpe {L['sharpe']:+5.2f}  WR {L['wr']*100:5.1f}%  cum {L['cum']*100:+6.2f}%")
    print(f"  Ky vong        mean {E['mean_bps']:+7.2f}bps  sd {E['sd_bps']:6.2f}bps"
          f"  Sharpe {E['sharpe']:+5.2f}   (670 phien pre-live, config dang deploy)")
    cur = None
    ORDER = {"T0":0,"T1":1,"T1i":2,"T2":3,"T3":4}
    TIER = {"T0": "T0 SUC KHOE SO LIEU (power cao, phat hien 1 phien)",
            "T1": "T1 ENVELOPE PHAN PHOI (nguong calibrated by construction) -- TINH vao trang thai",
            "T1i": "T1i cua so trung gian -- INFO, KHONG tinh vao trang thai",
            "T2": "T2 CUSUM (phat hien CHAM -- chi bat su co lon)",
            "T3": "T3 SPRT (THANH TIEN DO, khong phai trigger)"}
    for c in sorted(res["checks"], key=lambda c: ORDER.get(c["tier"], 9)):
        if c["tier"] != cur:
            cur = c["tier"]; print(f"\n  --- {TIER[cur]} ---")
        mk = {OK: "  ok ", WARN: " WARN", ALERT: "ALERT"}[c["status"]]
        print(f"  [{mk}] {c['name']:<34} {c['detail']}")
    print("\n" + "-" * 94)
    print(f"  HANH DONG theo TRANG THAI TONG = {res['overall']}:")
    if res["overall"] == OK:
        print("    khong lam gi. Ghi 1 dong log.")
    elif res["overall"] == WARN:
        print("    ghi log + 1 dong trong bao cao paper ke tiep. KHONG escalate, KHONG doi gi.")
    else:
        print("    escalate bus question cho Mike (--escalate). KHONG tu dung paper,")
        print("    KHONG tu doi tham so. Mike/user quyet dinh.")
    print("-" * 94)


def replay(log, base):
    """Dry-run: phat lai tung phien tu min_n, dem so phien moi tang bao WARN/ALERT.
    Muc dich: dem BAO GIA tren 75 phien da biet la 'binh thuong' (Viec B xac nhan
    khop ky vong, phan vi 50) TRUOC khi de xuat dua vao san xuat."""
    rows = []
    for i in range(20, len(log)+1):
        r = evaluate(log.iloc[:i].reset_index(drop=True), base, check_freshness=False)
        rows.append({"i": i, "date": log["date"].iloc[i-1], "overall": r["overall"],
                     **{f"{c['tier']}:{c['name']}": c["status"] for c in r["checks"]}})
    D = pd.DataFrame(rows)
    print("=" * 94)
    print(f"  DRY-RUN tren {len(log)} phien paper da co (phat lai tu phien 20 -> {len(log)})")
    print(f"  Ky vong: 0 ALERT. Viec B da xac nhan cua so nay o phan vi 50 cua phan phoi")
    print(f"  ky vong => bat ky ALERT nao o day la BAO GIA va thiet ke phai sua.")
    print("=" * 94)
    tot = len(D)
    print(f"  Tong so lan chay mo phong: {tot}")
    print(f"  {'trang thai tong':<20}{'so lan':>8}{'ty le':>9}")
    for s in [OK, WARN, ALERT]:
        c = int((D["overall"] == s).sum())
        print(f"  {s:<20}{c:>8}{c/tot*100:>8.1f}%")
    print(f"\n  Chi tiet tung check (so lan KHONG phai OK / {tot}):")
    cols = [c for c in D.columns if ":" in c]
    for c in cols:
        nw = int((D[c] == WARN).sum()); na = int((D[c] == ALERT).sum())
        flag = "  <== BAO GIA" if na else ("  <-- co WARN" if nw else "")
        print(f"    {c:<52} WARN {nw:>3}  ALERT {na:>3}{flag}")
    bad = D[D["overall"] == ALERT]
    if len(bad):
        print(f"\n  !!! {len(bad)} lan ALERT tren du lieu BINH THUONG -- thiet ke CHUA dat:")
        print(bad[["i","date","overall"]].to_string(index=False))
    else:
        print(f"\n  => 0 ALERT tren 75 phien binh thuong. Thiet ke qua buoc validate false-positive.")
    D.to_csv(os.path.join(HERE, "drift_monitor_replay.csv"), index=False)
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--escalate", action="store_true",
                    help="cho phep ghi bus question khi ALERT (mac dinh KHONG ghi gi)")
    ap.add_argument("--log", default=LOG)
    a = ap.parse_args()
    base = json.load(open(BASE))
    log = pd.read_csv(a.log)
    if a.replay:
        replay(log, base); return 0
    res = evaluate(log, base)
    if a.json:
        print(json.dumps(res, indent=1, default=str))
    else:
        render(res)
    if res["overall"] == ALERT and a.escalate:
        import subprocess
        fails = [c for c in res["checks"] if c["status"] == ALERT]
        payload = json.dumps({"monitor": "orb_drift_monitor.py", "overall": ALERT,
                              "live": res["live"], "expected": res["expected"],
                              "failing_checks": fails,
                              "scope": "GIAM SAT ONLY -- monitor khong doi tham so, khong dung paper. Can Mike/user quyet dinh."},
                             ensure_ascii=True)
        subprocess.run([os.path.join(WC, "mike/bin/append_event.sh"), "Taylor", "question",
                        "orb-drift-alert", payload], check=False)
        print("  -> da ghi bus question 'orb-drift-alert' cho Mike.")
    return {OK: 0, WARN: 10, ALERT: 20}[res["overall"]]


if __name__ == "__main__":
    sys.exit(main())
