#!/usr/bin/env python3
"""
dna_report.py — 2-block (DNA + NOW) Telegram report renderer for the 8L bot
===========================================================================
Imported by telegram_8l_bot.py (the existing interactive long-poll bot — NOT rebuilt).
`build_report(tk)` returns a Telegram-HTML string laid out as TWO CLOCKS:

  🧬 DNA  (slow, structural — "what the company IS"): route · engine · moat+5F+risk1
          · runway/TAM · margin-cycle. Sourced from CACHED files (these change per
          quarter/year, so caching is correct — no live cost paid for slow data).
  ⚡ NOW  (fast, live AT QUERY TIME — "where it stands today"): price · valuation-vs-
          own-history · drawdown · liquidity · Ngũ-Hành market regime · 8L rank.
          The price/valuation/regime lines are queried LIVE from BigQuery on each call.

Design rationale: only the NOW block pays the live-query cost; the DNA block (moat,
engine, TAM) is slow-moving so it reads cached unified_screener/dna_cards/moat_tags.
Each block is stamped with its own freshness so nothing pretends to be more live than
it is. Run standalone for a quick text preview: `python dna_report.py VCS`.
"""
import os, re, time, tempfile, subprocess
from io import StringIO
import pandas as pd, numpy as np

W = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT = "lithe-record-440915-m9"
BQ_BIN = os.environ.get("BQ_BIN", (r"bq" if os.name == "nt" else "bq"))
# 5-state Ngũ Hành regime: state -> (name, target weight, emoji). Values are 1..5 in vnindex_5state.
STATE_MAP = {1: ("CRISIS", "0%", "🔴"), 2: ("BEAR", "20%", "🟠"), 3: ("NEUTRAL", "70%", "🟡"),
             4: ("BULL", "100%", "🟢"), 5: ("EX-BULL", "130%", "🔵")}
_REGIME_CACHE = {"t": 0.0, "val": None}   # avoid re-querying regime on every message (5-min TTL)
_CAPIT_CACHE = {"t": 0.0, "val": None}
# Crisis-capitulation thresholds (research 2026-06-04, dt5g_8l_crisis_capitulation):
#   WATCH  = DT5G CRISIS & oversold breadth >= 5.7%  (quality+golden edge active)
#   STRONG = oversold breadth >= 40% (extreme washout, any state) -> bottom ~3d away,
#            fwd60 +12% med/100% win. Go (near) all-in; expect a final flush.
WATCH_OVERSOLD, STRONG_OVERSOLD = 0.057, 0.40


def _bq(sql, max_rows=10):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cat = "type" if os.name == "nt" else "cat"
        r = subprocess.run(f'{cat} "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows={max_rows}',
                           capture_output=True, text=True, timeout=90, shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    try: return pd.read_csv(StringIO(r.stdout.strip()))
    except Exception: return pd.DataFrame()


def get_regime():
    """Latest market state, live (cached 5 min).
    Source = vnindex_5state_dt5g_live (the TRUE production DT5G regime, fail-safe to DT4 — same
    series golive_recommend + pt_v4_dt5g consume). NOT the bare `vnindex_5state` table, which is
    the v3.4b BASE (TQ34b, no DT-gate/macro), repointed 2026-06-03 to stop the bot reporting the
    base regime instead of the live DT5G one."""
    if _REGIME_CACHE["val"] is not None and (time.time() - _REGIME_CACHE["t"]) < 300:
        return _REGIME_CACHE["val"]
    d = _bq("SELECT t.time, t.state FROM tav2_bq.vnindex_5state_dt5g_live t ORDER BY t.time DESC LIMIT 1")
    val = None
    if len(d):
        st = int(d.iloc[0]["state"]); nm, wt, em = STATE_MAP.get(st, ("?", "?", "⚪"))
        val = {"state": st, "name": nm, "weight": wt, "emoji": em, "asof": str(d.iloc[0]["time"])}
    _REGIME_CACHE.update(t=time.time(), val=val)
    return val


STATE_WEIGHT = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}   # reserve = 1 - weight


def get_capitulation():
    """Live market capitulation gauge (cached 5 min): DT5G state + oversold breadth ->
    DORMANT / WATCH / STRONG / STRONG_GRIND. STRONG downgrades to STRONG_GRIND when a
    prior washout fired 20-90 sessions ago (grinding bear). Also returns the deployable
    cash reserve = 1 - state target weight."""
    if _CAPIT_CACHE["val"] is not None and (time.time() - _CAPIT_CACHE["t"]) < 300:
        return _CAPIT_CACHE["val"]
    d = _bq("""WITH daily AS (
        SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
        FROM tav2_bq.ticker_prune p WHERE p.Close_T1>0 GROUP BY p.time)
      SELECT d.time, s.state, d.oversold
      FROM daily d JOIN tav2_bq.vnindex_5state_dt5g_live s USING(time)
      ORDER BY d.time DESC LIMIT 120""", max_rows=200)
    val = None
    if len(d):
        d = d.sort_values("time").reset_index(drop=True)
        st = int(d.iloc[-1]["state"]); os_ = float(d.iloc[-1]["oversold"])
        reserve = max(0.0, 1.0 - STATE_WEIGHT.get(st, 0.70))
        prior = d.iloc[:-1]; pw = prior[prior["oversold"] >= STRONG_OVERSOLD]
        grind = False
        if len(pw):
            last_pos = (len(d) - 1) - pw.index.max()
            grind = 20 <= last_pos <= 90
        if os_ >= STRONG_OVERSOLD:               level = "STRONG_GRIND" if grind else "STRONG"
        elif st == 1 and os_ >= WATCH_OVERSOLD:   level = "WATCH"
        else:                                     level = "DORMANT"
        val = {"state": st, "oversold": os_, "level": level, "reserve": reserve,
               "grind": grind, "asof": str(d.iloc[-1]["time"])}
    _CAPIT_CACHE.update(t=time.time(), val=val)
    return val


_COMPASS_CACHE = {"t": 0.0, "val": None}


def get_compass():
    """La bàn 2 — 3 trục (cached 15 min): breadth-level × breadth-momentum × concentration.
    Validated 2026-06-11 (memory breadth_compass_p1_2026): MONITOR-ONLY, không phải trigger
    (gate test fail walk-forward). Trục 1-2 live từ ticker_prune (% Close>MA200, MA10 smooth,
    >=100 mã); trục 3 = concentration switch M1+M3r AND-hold của V4/V5 ensemble, đọc từ
    compare_v11_v12_concentration_switch.csv (cờ chậm đa-tháng, chấp nhận stale vài tuần)."""
    if _COMPASS_CACHE["val"] is not None and (time.time() - _COMPASS_CACHE["t"]) < 900:
        return _COMPASS_CACHE["val"]
    val = None
    try:
        d = _bq("""SELECT t.time, SAFE_DIVIDE(COUNTIF(t.Close>t.MA200),COUNT(*)) AS breadth, COUNT(*) AS n,
            AVG(SAFE_DIVIDE(t.Close,t.Close_T1)-1) AS ew_ret
          FROM tav2_bq.ticker_prune AS t
          WHERE t.MA200 IS NOT NULL AND t.time>=DATE_SUB(CURRENT_DATE(),INTERVAL 130 DAY)
          GROUP BY t.time HAVING COUNT(*)>=100 ORDER BY t.time""", max_rows=200)
        vn = _bq("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
          WHERE t.ticker='VNINDEX' AND t.time>=DATE_SUB(CURRENT_DATE(),INTERVAL 60 DAY)
          ORDER BY t.time""", max_rows=80)
        if len(d) >= 51:
            b = pd.to_numeric(d["breadth"]).rolling(10, min_periods=5).mean()
            lvl_v = float(b.iloc[-1])
            m10 = float(b.iloc[-1] - b.iloc[-11])
            m40 = float(b.iloc[-1] - b.iloc[-41]) if len(b) > 41 else np.nan
            level = "WEAK" if lvl_v < 0.35 else ("STRONG" if lvl_v > 0.55 else "MID")
            fast = m10 < -0.06
            mom = "BLEED" if (m40 == m40 and m40 < -0.10) else ("HEAL" if (m40 == m40 and m40 > 0.10) else "FLAT")
            conc, conc_asof = None, ""
            try:
                cs = pd.read_csv(os.path.join(W, "compare_v11_v12_concentration_switch.csv"),
                                 usecols=["time", "sig_m1", "sig_m3"])
                cur = int(cs["sig_m1"].iloc[0])
                for a, bb in zip(cs["sig_m1"].astype(int), cs["sig_m3"].astype(int)):
                    if a == bb: cur = int(a)
                conc, conc_asof = cur, str(cs["time"].iloc[-1])[:10]
            except Exception:
                pass
            st = (get_regime() or {}).get("state")
            # rotation/decoupling detector (user 2026-06-12): radar-1-down x radar-2-up —
            # the UNPRECEDENTED cell (9/9 historical "defensive x breadth-strong" episodes
            # had EW falling too; this watches for the first true exception, e.g. a
            # VIC-family mean-reversion). Capit washout will NOT fire here by design
            # (no simultaneous crash), so this line is the only dedicated eye on it.
            ew20, vni20, spread20 = np.nan, np.nan, np.nan
            try:
                er = pd.to_numeric(d["ew_ret"]).tail(20)
                ew20 = float((1 + er).prod() - 1)
                if len(vn) >= 21:
                    vc = pd.to_numeric(vn["Close"])
                    vni20 = float(vc.iloc[-1] / vc.iloc[-21] - 1)
                    spread20 = ew20 - vni20
            except Exception:
                pass
            decoupling = (st is not None and st <= 2 and ew20 == ew20 and ew20 > 0
                          and spread20 == spread20 and spread20 > 0.03)
            rotation = (not decoupling and vni20 == vni20 and vni20 < -0.02
                        and spread20 == spread20 and spread20 > 0.015)
            # cell verdicts from the validated fwd60 matrix (EW ticker_prune, 2014-2026)
            if st is not None and st >= 3:
                if level == "WEAK" and fast:        cell, act = "FAST-WASHOUT", "vùng MUA (fwd60 +15.8%/86% win)"
                elif level == "WEAK" and conc == 1: cell, act = "DEAD-MONEY", "không tăng risk momentum; re-engage khi HEAL +10pp/40 phiên hoặc fast-washout"
                elif level == "WEAK":               cell, act = "WASHOUT-RECOVERY", "breadth yếu nhưng lãnh đạo rộng (fwd60 +13.9%/100%)"
                elif mom == "BLEED" and conc == 1:  cell, act = "GENERALS-ONLY", "tướng-bỏ-quân (kiểu 10-12/2025): thận trọng momentum mới"
                else:                                cell, act = "ĐỒNG PHA", "không cảnh báo"
            elif st is not None:
                if level == "STRONG":  cell, act = "CRISIS-SỚM", "breadth chưa gãy — ĐỪNG bắt đáy (fwd60 −4.3%/31%)"
                elif level == "WEAK":  cell, act = "WASHED-OUT", "vùng capitulation (fwd60 +7%/81%) — theo còi washout/capit"
                else:                  cell, act = "CHUYỂN PHA", "theo dõi washout"
            else:
                cell, act = "?", ""
            val = {"lvl_v": lvl_v, "level": level, "m10": m10, "m40": m40, "mom": mom, "fast": fast,
                   "conc": conc, "conc_asof": conc_asof, "cell": cell, "act": act,
                   "ew20": ew20, "vni20": vni20, "spread20": spread20,
                   "decoupling": decoupling, "rotation": rotation,
                   "asof": str(d["time"].iloc[-1])[:10]}
    except Exception:
        val = None
    _COMPASS_CACHE.update(t=time.time(), val=val)
    return val


def build_compass_line(html=True):
    """One-line 3-axis compass for NOW blocks / daily report. None on data failure."""
    c = get_compass()
    if not c:
        return None
    conc_s = {1: "conc=1 megacap-led", 0: "conc=0 broad"}.get(c["conc"], "conc=?")
    m40_s = f"{c['m40']*100:+.0f}pp/40d" if c["m40"] == c["m40"] else "Δ40d n/a"
    cell = f"<b>{c['cell']}</b>" if html else c["cell"]
    asof = f"  <i>[{c['asof']}]</i>" if html else f"  [{c['asof']}]"
    line = (f"La bàn2: breadth {c['lvl_v']*100:.0f}% {c['level']} ({m40_s} {c['mom']}"
            f"{', fast-washout' if c['fast'] else ''}) × {conc_s} → {cell}"
            + (f" · {c['act']}" if c["act"] else "") + asof)
    if c.get("decoupling"):
        line += (f"\n🚨 DECOUPLING (ô CHƯA TỪNG CÓ): EW {c['ew20']*100:+.1f}%/20d trong khi VNI "
                 f"{c['vni20']*100:+.1f}% & DT5G defensive → playbook §7: GIỮ w_LAG 0.50 (đừng về 0), "
                 f"entry theo signal thường, capit im lặng là ĐÚNG thiết kế. Human review bắt buộc.")
    elif c.get("rotation"):
        line += (f"\n⚠ ROTATION-WATCH: VNI {c['vni20']*100:+.1f}%/20d vs EW {c['ew20']*100:+.1f}% "
                 f"(spread {c['spread20']*100:+.1f}pp) — tướng rơi nhanh hơn quân; theo dõi cell decoupling.")
    return line


def build_market_alert():
    """Market-level capitulation message for the daily push. Returns None when DORMANT
    so the scheduler only pings on a real WATCH/STRONG signal."""
    cap = get_capitulation()
    if not cap or cap["level"] == "DORMANT":
        return None
    nm = STATE_MAP.get(cap["state"], ("?",))[0]
    res = f"reserve {cap.get('reserve',0)*100:.0f}% (1−tỉ trọng {nm})"
    if cap["level"] == "STRONG":
        head = (f"🔴🔴 <b>WASHOUT CỰC ĐOAN</b> — oversold {cap['oversold']*100:.0f}% "
                f"(>= {STRONG_OVERSOLD*100:.0f}%), {nm}\nĐáy cách ~3 phiên (median) · fwd60 +12%/100% win.")
        act = f"→ BƠM HẾT {res} vào rổ 8L quality+golden, (gần) ALL-IN, giữ ~60 phiên rồi reset. Chấp nhận flush cuối (~-12%)."
    elif cap["level"] == "STRONG_GRIND":
        head = (f"🟠 <b>WASHOUT (GRIND)</b> — oversold {cap['oversold']*100:.0f}%, {nm} · ⚠ washout lặp gần đây "
                f"(gấu grind, bẫy 2022)\nCó thể chưa phải đáy cuối.")
        act = f"→ RẢI LỆNH: bơm ~NỬA {res} bây giờ, giữ phần còn lại cho washout kế (>30 phiên). Giữ ~60 phiên rồi reset."
    else:  # WATCH
        head = (f"🟢 <b>CRISIS panic</b> — oversold {cap['oversold']*100:.0f}% (>= {WATCH_OVERSOLD*100:.0f}%), "
                f"regime {nm}.\nQuality+golden edge bật (fwd60 +16% med/83% win ở golden).")
        act = f"→ Xây vị thế thăm dò từ {res}; dồn lệnh khi washout sâu tới 40% (STRONG)."
    return (f"🧭 <b>TÍN HIỆU MUA-KHI-SỢ (DT5G×8L)</b>  <i>[{cap['asof']}]</i>\n"
            f"{head}\n{act}\nChi tiết: <code>python crisis_capitulation_signal.py</code>")


def live_now(tk):
    """Live one-ticker snapshot at query time: price, %chg, valuation-vs-history, dd, liquidity."""
    d = _bq(f"""WITH lt AS (SELECT t.ticker,MAX(t.time) mx FROM tav2_bq.ticker_1m t
                 WHERE t.ticker='{tk}' AND t.PB IS NOT NULL GROUP BY t.ticker),
      hiw AS (SELECT MAX(t.Close) hi FROM tav2_bq.ticker t
                 WHERE t.ticker='{tk}' AND t.time>=DATE_SUB(CURRENT_DATE(),INTERVAL 365 DAY))
      SELECT t.time, t.Close, t.Price, ROUND(t.PE,1) PE,
             ROUND((t.PE-t.PE_MA5Y)/NULLIF(t.PE_SD5Y,0),2) pe_z,
             ROUND(t.PB,2) PB, ROUND((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2) pb_z,
             ROUND(t.Close/NULLIF(t.Close_T1,0)-1,4) chg,
             ROUND(t.Close/NULLIF((SELECT hi FROM hiw),0)-1,2) dd,
             ROUND(COALESCE(t.Price,t.Close)*t.Volume_3M_P50/1e9,1) liqB
      FROM tav2_bq.ticker_1m t JOIN lt ON lt.ticker=t.ticker AND lt.mx=t.time
      WHERE t.ticker='{tk}'""")
    return d.iloc[0].to_dict() if len(d) else None


def _s(v):
    """Clean a possibly-NaN/'nan' cell to a display string ('' if empty)."""
    if v is None or (isinstance(v, float) and pd.isna(v)): return ""
    s = str(v).strip()
    return "" if s.lower() == "nan" else s


def _f(v, suf="", mul=1, plus=False, dec=0):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "n/a"
    s = f"{v*mul:+.{dec}f}" if plus else f"{v*mul:.{dec}f}"
    return s + suf


def build_report(tk):
    tk = tk.upper()
    # ---- cached structural sources (DNA — slow-moving, caching is correct) ----
    try: scr = pd.read_csv(os.path.join(W, "data", "unified_screener.csv")).set_index("ticker")
    except Exception: scr = pd.DataFrame()
    try: rank = pd.read_csv(os.path.join(W, "data", "rank_8l.csv"))
    except Exception: rank = pd.DataFrame()
    try: dna = pd.read_csv(os.path.join(W, "data", "dna_cards.csv")).set_index("ticker")
    except Exception: dna = pd.DataFrame()
    try:
        from moat_5f import load_moat_tags; MOAT5F = load_moat_tags(W)
    except Exception: MOAT5F = {}

    in_univ = len(scr) and tk in scr.index
    s = scr.loc[tk] if in_univ else None
    route = s["route"] if in_univ else "?"
    verdict = s["verdict"] if in_univ else "?"
    action = s.get("action", "") if in_univ else ""
    engine = str(s.get("engine", "") or "") if in_univ else ""
    dcard = dna.loc[tk].to_dict() if (len(dna) and tk in dna.index) else {}
    m5 = MOAT5F.get(tk)

    # rank position (cached EOD — rank is a prioritization, recomputed nightly)
    rkline = "—"
    if len(rank):
        rr = rank[rank["ticker"] == tk]
        if len(rr):
            r0 = rr.iloc[0]; rkline = f"#{int(r0['rank'])}/{len(rank)} · score {r0['score']:.0f}"
        elif in_univ:
            rkline = "GATED (AVOID/distressed)"

    # ---- live block (NOW — queried at message time) ----
    now = live_now(tk)
    reg = get_regime()

    # ===== assemble =====
    L = []
    struct = dcard.get("struct")
    has_struct = route == "CYCLICAL" and struct is not None and pd.notna(struct) and str(struct).strip() not in ("", "nan")
    head_route = f"{route}" + (f"/{struct}" if has_struct else "")
    L.append(f"📊 <b>{tk}</b> — {head_route}  ·  {rkline}")

    # --- DNA block ---
    L.append("──────── 🧬 <b>DNA</b> (cấu trúc, đổi chậm) ────────")
    if in_univ:   # verdict/action covers the WHOLE universe (screener), so DNA is never empty
        L.append(f"Verdict: <b>{verdict}</b>" + (f" · {action}" if action and str(action) != "nan" else ""))
    if engine and engine != "nan":
        L.append(f"Engine : <b>{engine}</b>" + (f"  ROIC {_f(dcard.get('roic'),'%',1)}" if dcard.get("roic") == dcard.get("roic") else ""))
    # moat: numeric proxy + 5F durability verdict + kill-condition
    moat_proxy = _s(dcard.get("moat"))
    moat_type = _s(dcard.get("moat_type")) or (m5["type"] if m5 else "")
    if m5:
        L.append(f"Moat   : <b>{m5['tier']}</b> [{m5['type']}]" + (f" · số:{moat_proxy}" if moat_proxy else ""))
        L.append(f"  ⚠ risk#1: {m5['risk1']}")
    elif moat_proxy:
        L.append(f"Moat   : {moat_proxy}" + (f" [{moat_type}]" if moat_type else "") + "  <i>(chưa tag 5F)</i>")
    runway, tam = _s(dcard.get("runway")), _s(dcard.get("tam"))
    if runway:
        L.append(f"TAM    : {runway}" + (f" [{tam}]" if tam else ""))
    mcyc = _s(dcard.get("margin_cycle"))
    if mcyc and mcyc != "n/a":
        L.append(f"Margin : {mcyc}")

    # --- NOW block ---
    asof = str(now["time"])[:10] if now else "?"
    L.append(f"──────── ⚡ <b>NOW</b> (live {asof}) ────────")
    if now:
        chg = now.get("chg"); chg_s = _f(chg, "%", 100, plus=True, dec=1) if chg == chg else "n/a"
        ddv = now.get("dd"); blood = " 🩸" if (ddv == ddv and ddv <= -0.30) else ""
        L.append(f"Giá    : {_f(now.get('Price') or now.get('Close'), '', 1, dec=1)} ({chg_s} phiên) · dd 52w {_f(ddv,'%',100,plus=True)}{blood}")
        L.append(f"Định giá: PE {now.get('PE')} · pe_z {_f(now.get('pe_z'),'',1,plus=True,dec=1)} · PB {now.get('PB')} · pb_z {_f(now.get('pb_z'),'',1,plus=True,dec=1)}")
        liq = now.get("liqB"); dep = " ✅" if (liq == liq and liq >= 4) else (" ⚠️thin" if liq == liq else "")
        L.append(f"Thanh kh: {_f(liq,' tỷ/phiên',1,dec=0)}{dep}")
    else:
        L.append("Giá/định giá: n/a (không lấy được dữ liệu live)")
    if reg:
        edge = "FA-edge mạnh" if reg["state"] <= 2 else ("FA-edge yếu" if reg["state"] >= 3 else "")
        L.append(f"Regime : {reg['emoji']} <b>{reg['name']}</b> ({reg['weight']}) · {edge}  <i>[{reg['asof']}]</i>")
    comp = build_compass_line()
    if comp:
        L.append(comp)
    cap = get_capitulation()
    if cap and cap["level"] == "STRONG":
        L.append(f"Panic  : 🔴 <b>WASHOUT CỰC ĐOAN</b> (oversold {cap['oversold']*100:.0f}%) — MUA-KHI-SỢ, đáy ~3 phiên · bơm reserve {cap.get('reserve',0)*100:.0f}%")
    elif cap and cap["level"] == "STRONG_GRIND":
        L.append(f"Panic  : 🟠 WASHOUT GRIND (oversold {cap['oversold']*100:.0f}%) — ⚠ washout lặp = gấu grind, RẢI lệnh (½ reserve)")
    elif cap and cap["level"] == "WATCH":
        L.append(f"Panic  : 🟢 CRISIS panic (oversold {cap['oversold']*100:.0f}%) — quality+golden edge bật")
    # flags
    flags = []
    det = str(s["detail"]) if in_univ else ""
    if "VALUE_TRAP" in str(verdict) or "VALUE_TRAP" in det: flags.append("⚑ VALUE_TRAP→event_check")
    if dcard.get("asset_play") in (True, "True"): flags.append("⚑ ASSET_PLAY→NAV")
    ev = dcard.get("event")
    if ev is not None and pd.notna(ev) and str(ev).strip() not in ("", "nan"): flags.append(f"⚑ EVENT: {ev}")
    if m5 and m5["tier"] == "NONE": flags.append("⚑ no-moat: ROE cao = chu kỳ/transient")
    if flags: L.append("Cờ     : " + "\n         ".join(flags))

    # --- quick read (gate-style synthesis, not a buy signal) ---
    L.append("──────── 🎯 <b>ĐỌC NHANH</b> ────────")
    L.append(_quick_read(tk, route, verdict, engine, now, reg, m5))
    # freshness footer
    L.append(f"<i>Data: giá live {asof} · FA quý (cache) · moat asof {(m5['asof'] if m5 else '—')}</i>")
    return "\n".join(L)


def _quick_read(tk, route, verdict, engine, now, reg, m5):
    bits = []
    if "COMPOUNDER" in str(engine): bits.append("compounder thật")
    elif route == "BANK": bits.append("ngân hàng")
    elif route == "CYCLICAL": bits.append("hàng hóa chu kỳ")
    if m5 and m5["tier"] == "WIDE": bits.append("hào BỀN")
    elif m5 and m5["tier"] == "NONE": bits.append("KHÔNG hào (ROE chu kỳ)")
    ddv = now.get("dd") if now else None
    deep = (ddv == ddv and ddv is not None and ddv <= -0.30)
    cheap = bool(now and ((now.get("pe_z") == now.get("pe_z") and now.get("pe_z") is not None and now.get("pe_z") < -1)
                          or (now.get("pb_z") == now.get("pb_z") and now.get("pb_z") is not None and now.get("pb_z") < -1)))
    regname = reg["name"] if reg else "?"
    tail = []
    if reg and reg["state"] >= 3: tail.append(f"regime {regname} chưa ưu tiên FA")
    elif reg: tail.append(f"regime {regname} = FA-edge mạnh")
    if deep: tail.append("dd sâu = panic")
    if cheap: tail.append("rẻ-vs-lịch-sử (z<−1)")
    verdict_buy = (cheap and deep and m5 and m5["tier"] == "WIDE" and reg and reg["state"] <= 2)
    lead = " · ".join(bits) if bits else "—"
    cond = ("; ".join(tail)) if tail else "không tín hiệu nổi bật"
    closer = "→ vùng MUA-KHI-SỢ đáng chú ý." if verdict_buy else "→ THEO DÕI, chưa phải mua-ngay (gate, không phải buy signal)."
    return f"{lead}. {cond}. {closer}"


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        print(build_report(a)); print()
