# -*- coding: utf-8 -*-
"""
orig_config_forward.py — item 2/6 cua job Taylor_20260925_095910.

MUC DICH: chay CONFIG GOC (cai duy nhat tung duoc validate) FORWARD tren dung cua so
paper live da co, thay vi backtest lai lich su. Day la lan DAU TIEN config nay duoc do
tren du lieu forward -- va no chinh la config ma gate criterion #2 cua
kb/paper_programs_registry.json (khoan lo ca nam 2024) noi den.

Config GOC : exit 14:00 | stop 0.7% (intraday, low/high) | loc |OR30| >= 0.2% | TC 2.5bps
             (nguon: vn30f_orb_strategy.py muc C, walk-forward theo nam)
Config DEPLOY: exit 14:30 | khong stop | tat ca ngay | slip 1 tick/chieu + fee 0.6bps
             (nguon: orb_pt.py)

Logic sim COPY NGUYEN VAN tu vn30f_orb_strategy.py::sim() -- khong tinh lai theo cach khac.
Du lieu: snapshot vendor da dong bang (vn30f1m_live_snapshot_20260925.csv) de tai lap duoc.
KHONG ghi de data/orb_pt_log.csv.
"""
import sys, io, json, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

HERE = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/orb_reeval_20260925"
SNAP = HERE + "/vn30f1m_live_snapshot_20260925.csv"
STARTDATE = "2026-06-09"     # = orb_pt.py STARTDATE
ENDDATE   = "2026-09-24"     # dung cua so 74 phien cua re-eval job _052050

df = pd.read_csv(SNAP); df["time"] = pd.to_datetime(df["time"])
df["date"] = df["time"].dt.date; df["hm"] = df["time"].dt.strftime("%H:%M")
snap_sha = hashlib.sha256(open(SNAP, "rb").read()).hexdigest()

# ---- per-day pre-split. Dung DUNG quy tac completeness cua orb_pt.py (last bar >= 14:25),
#      khong phai len(g)>=150 cua script research -- xem C4 trong FINDINGS.md.
days = []
for d, g in df.groupby("date"):
    ds = str(d)
    if ds < STARTDATE or ds > ENDDATE: continue
    g = g.sort_values("time").reset_index(drop=True)
    op = g[g["hm"] <= "09:30"]
    seg_dep = g[(g["hm"] > "09:30") & (g["hm"] <= "14:30")]
    if not (len(op) >= 10 and len(seg_dep) > 0 and g["hm"].iloc[-1] >= "14:25"): continue
    entry = op["close"].iloc[-1]; or_ret = entry / g["close"].iloc[0] - 1
    days.append({"date": ds, "or_ret": or_ret, "entry": entry,
                 "post": g[g["hm"] > "09:30"].reset_index(drop=True)})
print(f"Snapshot {SNAP.split('/')[-1]} sha256 {snap_sha[:16]}...  "
      f"phien hoan chinh trong [{STARTDATE},{ENDDATE}] = {len(days)}")

def sim(exit_hm="14:00", stop=None, tc=0.00025, min_or=0.002):
    """COPY tu vn30f_orb_strategy.py::sim() (default tc doi 1.5->2.5bps = config muc C)."""
    recs = []
    for dd in days:
        if abs(dd["or_ret"]) < min_or: continue
        sig = np.sign(dd["or_ret"]); entry = dd["entry"]; post = dd["post"]
        if sig == 0: continue      # = orb_pt.py "if sig==0: continue" (min_or=0 khong loc noi OR==0)
        seg = post[post["hm"] <= exit_hm]
        if len(seg) == 0: continue
        exit_px = seg["close"].iloc[-1]; stopped = False
        if stop is not None:
            if sig > 0:
                hit = seg[seg["low"] <= entry * (1 - stop)]
                if len(hit) > 0: exit_px = entry * (1 - stop); stopped = True
            else:
                hit = seg[seg["high"] >= entry * (1 + stop)]
                if len(hit) > 0: exit_px = entry * (1 + stop); stopped = True
        pnl = sig * (exit_px / entry - 1) - tc
        recs.append({"date": dd["date"], "or_ret": dd["or_ret"], "sig": int(sig),
                     "entry": entry, "exit": exit_px, "pnl": pnl, "stopped": stopped})
    return pd.DataFrame(recs)

def stat(r):
    if len(r) == 0: return None
    n = len(r); sd = r["pnl"].std()
    mean = r["pnl"].mean(); nav = (1 + r["pnl"]).cumprod()
    tstat = mean / (sd / np.sqrt(n)) if (n > 1 and sd > 0) else 0.0
    return dict(n=n, wr=float((r["pnl"] > 0).mean()), mean=float(mean), sd=float(sd),
                sh=float(mean / sd * np.sqrt(252)) if (n > 1 and sd > 0) else 0.0,
                cum=float(nav.iloc[-1] - 1), mdd=float((nav / nav.cummax() - 1).min()),
                stp=float(r["stopped"].mean()), t=float(tstat))

def line(tag, s):
    if s is None: return f"  {tag:<34}  KHONG CO PHIEN NAO QUA FILTER"
    return (f"  {tag:<34}{s['n']:>5}{s['wr']*100:>7.1f}%{s['mean']*1e4:>+9.2f}{s['sh']:>8.2f}"
            f"{s['t']:>+7.2f}{s['mdd']*100:>+8.1f}%{s['stp']*100:>6.0f}%{s['cum']*100:>+8.2f}%")

print("\n" + "=" * 104)
print("  FORWARD TEST tren cua so PAPER LIVE — config GOC (da validate) vs config DANG DEPLOY")
print("=" * 104)
print(f"  {'config':<34}{'n':>5}{'WR':>8}{'mean/d':>9}{'Sharpe':>8}{'t':>7}{'MaxDD':>9}{'%stp':>6}{'cum':>9}")
print("  " + "-" * 100)
r_orig = sim("14:00", 0.007, 0.00025, 0.002)
r_dep  = sim("14:30", None,  0.00025, 0.0)     # cung ham, chi doi tham so
print(line("GOC exit14:00 stop0.7% |OR|>=.2%", stat(r_orig)))
print(line("DEPLOY exit14:30 nostop all-days", stat(r_dep)))
print("  " + "-" * 100)
print("  (2 dong tren dung CUNG ham sim + CUNG TC 2.5bps => khac biet chi den tu 3 truc config)")

# doi chieu: dung subset ngay ma config GOC co trade, chay config DEPLOY tren dung cac ngay do
if len(r_orig):
    sel = set(r_orig["date"])
    r_dep_same = r_dep[r_dep["date"].isin(sel)]
    print(line("DEPLOY, chi tren ngay GOC co trade", stat(r_dep_same)))

# per-month cua config GOC
if len(r_orig):
    print("\n  --- config GOC theo thang ---")
    rr = r_orig.copy(); rr["m"] = rr["date"].str[:7]
    for m, gg in rr.groupby("m"):
        s = stat(gg); print(f"    {m}  n={s['n']:>3}  mean {s['mean']*1e4:>+7.2f}bps  cum {s['cum']*100:>+6.2f}%")
    print("\n  --- chi tiet tung phien (config GOC) ---")
    for _, x in r_orig.iterrows():
        print(f"    {x['date']}  OR {x['or_ret']*100:+.2f}%  sig {x['sig']:+d}  "
              f"entry {x['entry']:.1f} -> exit {x['exit']:.1f}  pnl {x['pnl']*100:+.2f}%"
              f"{'  [STOPPED]' if x['stopped'] else ''}")

s_o, s_d = stat(r_orig), stat(r_dep)
res = {"job": "Taylor_20260925_095910", "item": "2/6",
       "snapshot": SNAP, "snapshot_sha256": snap_sha,
       "window": [STARTDATE, ENDDATE], "sessions_complete": len(days),
       "orig_config": {"exit": "14:00", "stop": 0.007, "min_or": 0.002, "tc_bps": 2.5,
                       "source": "vn30f_orb_strategy.py section C"},
       "deploy_config": {"exit": "14:30", "stop": None, "min_or": 0.0, "tc_bps": 2.5,
                         "source": "orb_pt.py (TC normalised to 2.5bps for comparability)"},
       "orig_forward": s_o, "deploy_forward_same_tc": s_d,
       "orig_2024_reference": {"n": 76, "mean_bps": -5.93, "sharpe": -1.84, "cum": -0.0450,
                               "source": "FINDINGS.md C5 (job Taylor_20260925_052050)"}}
with open(HERE + "/orig_config_forward_result.json", "w", encoding="utf-8") as fp:
    json.dump(res, fp, ensure_ascii=False, indent=2, default=float)
if len(r_orig):
    r_orig.to_csv(HERE + "/orig_config_forward_trades.csv", index=False)
print("\n  -> orig_config_forward_result.json + orig_config_forward_trades.csv")
print("Done.")
