"""
AMH Cockpit — daily 18:00 market-status block for V6 "Tứ Trụ"
=============================================================
Assembles ONE report combining the live monitoring layers built in the AMH arc:
  #4 Ecology   (fragility: breadth / dispersion / mood / divergence)
  #1 EdgeHealth (which edges are alive/flipped + CAPIT-EDGE health gate)
  V6 allocation (today's Tứ Trụ NAV split from the levered allocator, with the
                 capit carve CAPPED by the live capit-edge health from #1)

Reads the artifacts produced by ecology_dashboard.py + edge_health_monitor.py,
computes today's V6 split, writes data/amh_cockpit.md (+ prints). Wire into the
daily bat so the 18:00 push can include it.

Run: python amh_cockpit.py
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
from sleeve_pnl_levered import allocate_lev, MAX_GROSS
from edge_health_monitor import capit_edge_health

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATEF = WORKDIR + r"/data/dt5g_vnindex.csv"
ECOF = WORKDIR + r"/data/ecology_panel.csv"
STATE_LBL = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "(n/a — chạy script nguồn trước)"


def today_signals():
    st = pd.read_csv(STATEF, parse_dates=["time"]).sort_values("time")
    state = int(st["state"].iloc[-1])
    px = st["vnindex"]; idx3m = px.iloc[-1] / px.iloc[-63] - 1 if len(px) > 63 else 0.0
    eco = pd.read_csv(ECOF, parse_dates=["time"]).sort_values("time").iloc[-1]
    oversold = float(eco["pct_oversold"]); breadth = float(eco["breadth200"])
    capit_on = oversold >= 0.30
    grind_on = (state == 3) and (abs(idx3m) < 0.05) and (breadth < 0.45)
    return state, capit_on, grind_on, oversold, breadth, st["time"].iloc[-1].date()


def main():
    state, capit_on, grind_on, oversold, breadth, asof = today_signals()
    ce = capit_edge_health()
    a = allocate_lev(state, capit_on, grind_on)
    # apply the live capit-edge cap from #1 (don't carve capit beyond what its edge supports)
    capit_cap = ce["max_carve"] if ce else 0.40
    if a["capit"] > capit_cap:
        a["core"] = a.get("core", 0) + (a["capit"] - capit_cap)   # shift overflow to core
        a["capit"] = capit_cap
        a["gross"] = a["core"] + a["value"] + a["capit"] + a["grind"]
        if a["gross"] > MAX_GROSS:
            a["core"] -= (a["gross"] - MAX_GROSS); a["gross"] = MAX_GROSS
        a["cash"] = max(0.0, 1.0 - a["gross"])

    L = []
    L.append(f"🧭 <b>AMH COCKPIT — V6 “Tứ Trụ”</b>  <i>[{asof}]</i>")
    L.append(f"DT5G: <b>{STATE_LBL[state]}</b> · breadth {breadth*100:.0f}% · oversold {oversold*100:.0f}%")
    L.append("")
    L.append(f"📦 <b>Phân bổ hôm nay</b> (gross {a['gross']*100:.0f}%, cap {MAX_GROSS*100:.0f}%):")
    L.append(f"  core {a['core']*100:.0f}% · value {a['value']*100:.0f}% · "
             f"capit {a['capit']*100:.0f}% · grind {a['grind']*100:.0f}% · cash {a['cash']*100:.0f}%")
    if ce:
        flag = {"HEALTHY": "🟢", "FADING": "🟡", "NEGATIVE": "🔴"}[ce["verdict"]]
        L.append(f"  {flag} capit-edge {ce['verdict']} → trần carve {ce['max_carve']*100:.0f}% "
                 f"(recent {ce['rec_mean']:+.1f}%/hit{ce['rec_hit']:.0%}, last {ce['last']:+.1f}%)")
    L.append("")
    L.append("──────── 🌊 <b>#4 ECOLOGY</b> ────────")
    L.append(_read(WORKDIR + r"/data/ecology_now.md"))
    L.append("")
    L.append("──────── 🧬 <b>#1 EDGE HEALTH</b> ────────")
    L.append(_read(WORKDIR + r"/data/edge_health_block.md"))
    msg = "\n".join(L)
    with open(WORKDIR + r"/data/amh_cockpit.md", "w", encoding="utf-8") as f:
        f.write(msg)
    # console-readable (strip a few HTML tags)
    print(msg.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))
    print("\nSaved: data/amh_cockpit.md  (Telegram-HTML; daily push reads this)")


if __name__ == "__main__":
    main()
