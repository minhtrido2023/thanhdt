# -*- coding: utf-8 -*-
"""BA-system daily Telegram notifier.

Workflow:
  1. Run BA-system live engine (reads ticker_1m for latest data)
  2. Format watchlist as Telegram HTML message
  3. Send to configured Telegram chat
  4. Attach full CSV files for detailed reference

Usage:
  python telegram_recommend.py                  # use latest data
  python telegram_recommend.py 2026-05-08       # specific date
  python telegram_recommend.py --dry-run        # build message but don't send

Requires:
  telegram_config.json with bot_token + chat_id
  (template at telegram_config.template.json)
"""
import os
import sys
import glob
import json
import time
import argparse
from datetime import datetime

import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
# Note: recommend_holistic.py wraps sys.stdout at import time; rely on that.

CONFIG_PATH = os.path.join(WORKDIR, "secrets/telegram_config.json")
TG_MAX_MSG = 4000   # Telegram limit is 4096; leave margin


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: {CONFIG_PATH} not found.")
        print(f"Copy telegram_config.template.json → telegram_config.json and fill in bot_token + chat_id.")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def send_telegram_text(bot_token: str, chat_id: str, text: str,
                        parse_mode: str = "HTML") -> dict:
    """Send a text message (≤ 4096 chars) to Telegram."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    r = requests.post(url, data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }, timeout=30)
    return r.json()


def send_telegram_document(bot_token: str, chat_id: str,
                            file_path: str, caption: str = "") -> dict:
    """Upload a file as document attachment."""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as f:
        r = requests.post(url, data={
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "HTML",
        }, files={"document": f}, timeout=60)
    return r.json()


def split_message(text: str, max_len: int = TG_MAX_MSG) -> list:
    """Split a long message into chunks ≤ max_len, breaking at newlines."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    cur = []
    cur_len = 0
    for line in text.split("\n"):
        line_len = len(line) + 1
        if cur_len + line_len > max_len and cur:
            chunks.append("\n".join(cur))
            cur = [line]
            cur_len = line_len
        else:
            cur.append(line)
            cur_len += line_len
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def _esc(s) -> str:
    """Escape HTML special chars."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    s = str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─── DT5G market-state engine (gated live, fail-safe to DT4) ─────────────
DT5G_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
GOLIVE_JSON_CANDIDATES = [
    os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "golive_state_today.json"),
    os.path.join(WORKDIR, "golive_state_today.json"),
]


def get_dt5g_state(target: str):
    """Latest DT5G gated state with time <= target.
    Returns (state:int|None, as_of:str|None, source:str|None).
    Provenance (DT5G_macro vs DT4_only) is read from golive_state_today.json
    when its as_of matches the published row."""
    from recommend_holistic import bq
    try:
        df = bq(f"SELECT s.time, s.state FROM {DT5G_TABLE} AS s "
                f"WHERE s.time <= DATE '{target}' ORDER BY s.time DESC LIMIT 1")
    except Exception as e:
        print(f"  WARN: DT5G query failed ({e}); falling back to TQ34b state.")
        return None, None, None
    if df.empty:
        return None, None, None
    state = int(df["state"].iloc[0])
    as_of = str(pd.to_datetime(df["time"].iloc[0]).date())
    source = None
    for jp in GOLIVE_JSON_CANDIDATES:
        if os.path.exists(jp):
            try:
                with open(jp, "r", encoding="utf-8") as f:
                    j = json.load(f)
                if str(j.get("as_of")) == as_of:
                    source = j.get("source")
            except Exception:
                pass
            break
    return state, as_of, source


def load_dt5g_history(start_date="2026-04-01", end_date=None) -> pd.DataFrame:
    """Load DT5G gated state series [start_date, end_date] from BQ."""
    from recommend_holistic import bq
    sql = (f"SELECT s.time, s.state FROM {DT5G_TABLE} AS s "
           f"WHERE s.time >= DATE '{start_date}'")
    if end_date:
        sql += f" AND s.time <= DATE '{end_date}'"
    sql += " ORDER BY s.time"
    try:
        df = bq(sql)
    except Exception:
        return pd.DataFrame()
    if df.empty:
        return df
    df["time"] = pd.to_datetime(df["time"])
    return df.reset_index(drop=True)


def _read_pt_nav(logs_rel_path: str):
    """Read start/latest NAV from a paper-trade logs CSV. Returns dict or None."""
    p = os.path.join(WORKDIR, logs_rel_path)
    if not os.path.exists(p):
        return None
    try:
        df = pd.read_csv(p, parse_dates=["ymd"]).sort_values("ymd")
        if df.empty:
            return None
        nav0 = float(df["nav"].iloc[0]); nav1 = float(df["nav"].iloc[-1])
        ret = (nav1 / nav0 - 1) * 100 if nav0 else 0.0
        return {"nav": nav1, "ret": ret, "start": df["ymd"].iloc[0].date(),
                "end": df["ymd"].iloc[-1].date(), "n": len(df)}
    except Exception:
        return None


def build_dt5g_section(target_date: str, dt5g_state, dt5g_asof, dt5g_source) -> tuple:
    """Build the DT5G market-state section (engine status + transitions + paper-trade
    systems incl. V4 12.1). Returns (message_text, csv_path) for attachment."""
    state_emoji = {1: "💀", 2: "🔴", 3: "🟡", 4: "🟢", 5: "🔥"}
    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

    lines = ["", "<b>🛰️ MARKET-STATE ENGINE — DT5G (gated live)</b>"]
    if dt5g_state is None:
        lines.append("<i>DT5G live unavailable — đã fallback sang state cũ ở trên.</i>")
        return "\n".join(lines), None

    src = dt5g_source or "DT5G_macro"
    src_note = ("DT5G + macro overlay" if src == "DT5G_macro"
                else "DT4-only (macro feed degraded → fail-safe)" if src == "DT4_only"
                else src)
    em = state_emoji.get(dt5g_state, "❓"); nm = state_names.get(dt5g_state, "?")
    lines.append("<pre>")
    lines.append(f"As of:   {dt5g_asof}")
    lines.append(f"Source:  {src_note}")
    lines.append("</pre>")
    if dt5g_asof and str(dt5g_asof) < str(target_date):
        lines.append(f"<i>⚠️ DT5G as-of {dt5g_asof} trễ hơn signal date {target_date} — dùng state công bố gần nhất "
                     f"(DT5G dormant/sticky trong regime lành tính).</i>")

    # DT5G transitions since Apr 1
    hist = load_dt5g_history(start_date="2026-04-01", end_date=target_date)
    csv_path = None
    if not hist.empty:
        sv = hist["state"].values
        tv = hist["time"].values
        trans = [(pd.Timestamp(tv[i]), int(sv[i-1]), int(sv[i]))
                 for i in range(1, len(sv)) if sv[i] != sv[i-1]]
        lines.append("")
        lines.append("<b>🔄 DT5G transitions từ 2026-04-01</b>")
        lines.append("<pre>")
        lines.append(f"Số ngày: {len(hist)}   |   transitions: {len(trans)}")
        for d, fr, to in trans[-6:]:
            lines.append(f"  {d.strftime('%Y-%m-%d')}  {state_names[fr]:>8} → {state_names[to]:<8}")
        if not trans:
            lines.append("  (không có transition — state ổn định)")
        lines.append("</pre>")
        csv_path = os.path.join(WORKDIR, f"dt5g_state_history_{target_date}.csv")
        h = hist.copy()
        h["state_name"] = h["state"].map(state_names)
        h.to_csv(csv_path, index=False)

    # V2.3 LIVE forward track (production) + benchmark control arms (V4 demoted 2026-06-12)
    lines.append("")
    lines.append("<b>📊 V2.3 LIVE paper-trade — forward OOS track</b>")
    v23 = _read_pt_nav("data/pt_v22_dt5g_logs.csv")
    if v23 is None:
        lines.append("<i>V2.3 logs chưa có (pt_v22_dt5g.py chưa chạy?).</i>")
    elif v23["n"] <= 1:
        lines.append(f"<i>V2.3: khởi tạo 50B, <b>chạy từ {v23['start']}</b> — chờ phiên giao dịch đầu tiên.</i>")
    else:
        lines.append(f"<i>V2.3: <b>chạy từ {v23['start']}</b> — NAV {v23['nav']/1e9:.3f}B ({v23['ret']:+.2f}%) sau {v23['n']} phiên.</i>")

    lines.append("")
    lines.append("<b>🧪 Benchmark / control arms (paper-trade nền)</b>")
    lines.append("<pre>")
    # V121_ENS / V121_Kelly (ensemble switch) removed 2026-06-16 — faithful-audit edge
    # was a reduced-harness artifact (16.85% < V11/V2.3); dropped from daily comparison.
    bench = [
        ("V4 12.1 ⭐ctrl", "data/pt_v4_dt5g_logs.csv"),
        ("V11 SongSinh ", "data/pt_v11_tq34b_logs.csv"),
        ("V12 AmDuong  ", "data/pt_v12_macro_logs.csv"),
    ]
    for nm, path in bench:
        b = _read_pt_nav(path)
        if b:
            lines.append(f"{nm} {str(b['start'])} → {b['ret']:+6.2f}% ({b['n']}p)")
        else:
            lines.append(f"{nm} (logs n/a)")
    lines.append("</pre>")
    lines.append("<i>V4 12.1 = control arm của OOS showdown vs V2.3 (ensemble-switch, rời production "
                 "2026-06-12). Ret% tính từ ngày start mỗi sim — không so trực tiếp giữa sim khác start.</i>")

    return "\n".join(lines), csv_path


def _load_rating_map():
    """8L credit-style quality rating 1-5 per ticker (from rating_8l.py). 'R' column in book tables."""
    try:
        r = pd.read_csv(os.path.join(WORKDIR, "data", "rating_8l.csv"))
        return {t: (int(v) if pd.notna(v) else None) for t, v in zip(r["ticker"], r["rating"])}
    except Exception:
        return {}
RATING_MAP = _load_rating_map()

def build_book_section(book_df: pd.DataFrame, label: str) -> str:
    """Build HTML table-style section for one book. Includes 8L quality rating (R) column."""
    if book_df.empty:
        return f"\n<b>{label}</b>\n<i>Không có signal — giữ cash cho book này.</i>\n"

    # Short tier names for compact display
    TIER_SHORT = {
        "MEGA": "MEGA",
        "MOMENTUM": "MOM",
        "MOMENTUM_N": "MOM_N",
        "MOMENTUM_S": "MOM_S",
        "DEEP_VALUE_RECOVERY": "DVR",
    }

    lines = [f"\n<b>{label}</b> ({len(book_df)} mã)\n"]
    lines.append("<pre>")
    lines.append(f"{'Ticker':<7} {'Tier':<6} {'R':<2} {'Close':>8} {'Sc':>4} {'FA':>3} {'RSI':>5} {'Days':>5}")
    lines.append("-" * 50)
    for _, r in book_df.iterrows():
        ticker = _esc(r["ticker"])
        tier_full = _esc(r["play_type"])
        tier = TIER_SHORT.get(tier_full, tier_full[:6])
        rt = RATING_MAP.get(r["ticker"])
        rt_str = str(rt) if rt is not None else "-"
        close = f"{r['Close']:,.0f}" if pd.notna(r["Close"]) else "-"
        score = int(r["ta_score"]) if pd.notna(r["ta_score"]) else 0
        fa = _esc(r.get("fa_tier", ""))[:3]
        rsi = f"{r['rsi']:.2f}" if pd.notna(r["rsi"]) else "-"
        days = r.get("days_since_release", None)
        days_str = f"{int(days)}d" if pd.notna(days) else "-"
        lines.append(f"{ticker:<7} {tier:<6} {rt_str:<2} {close:>8} {score:>4} {fa:>3} {rsi:>5} {days_str:>5}")
    lines.append("</pre>")
    lines.append("<i>R = 8L rating 1-5 (1=cao nhất, ≤3=đầu tư) · Days = ngày từ Q-report (Fresh-Q ≤60)</i>")
    return "\n".join(lines)


def build_lag_section(lag_df: pd.DataFrame, w_tgt=None) -> str:
    """BOOK B — LAG (PEAD always-on). lag_df = raw rows from golive_v23 CSV
    (ticker, play_type LAG_HI/LAG_LO, weight_pct, status UPCOMING/ENTERED)."""
    hdr = "📋 BOOK B — LAG (PEAD always-on"
    hdr += f", {w_tgt*100:.0f}% NAV target)" if w_tgt is not None else ")"
    if lag_df is None or lag_df.empty:
        return (f"\n<b>{hdr}</b>\n<i>Không có entry PEAD đến hạn — giữ vị thế LAG hiện có "
                f"(hold 25td, NO stop) + parking.</i>\n")
    lines = [f"\n<b>{hdr}</b> ({len(lag_df)} entries)\n", "<pre>"]
    lines.append(f"{'Ticker':<7} {'Tier':<7} {'W%':>3} {'Status':<20}")
    lines.append("-" * 42)
    for _, r in lag_df.iterrows():
        w = f"{float(r['weight_pct']):.0f}" if pd.notna(r.get("weight_pct")) else "-"
        lines.append(f"{_esc(r['ticker']):<7} {_esc(r['play_type']):<7} {w:>3} {_esc(r.get('status', '')):<20}")
    lines.append("</pre>")
    lines.append("<i>UPCOMING = vào lệnh phiên tới (T+5 sau release) · ENTERED = đã vào · W% trên vốn book LAG</i>")
    return "\n".join(lines)


def build_message(target: str, state5, state_label: str,
                   bal_book: pd.DataFrame, lag_df: pd.DataFrame, capit_df: pd.DataFrame,
                   pt_counts: dict, fa_count: int,
                   include_universe: bool = True,
                   v23_status: dict = None) -> str:
    """Build the main Telegram HTML message — V2.3 production view (2026-06-12).
    V2.3 = BAL | LAG static two-book + state-conditional allocator + parking + CAPIT v2."""

    state_emoji = {"CRISIS": "💀", "BEAR": "🔴", "NEUTRAL": "🟡",
                    "BULL": "🟢", "EX-BULL": "🔥"}.get(state_label, "❓")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st = v23_status or {}
    w_tgt = st.get("w_lag_target")
    w_cur = st.get("w_lag_current")

    lines = [
        f"<b>🛰️ V2.3 (DT5G) REPORT — {target}</b>",
        f"<i>Sent: {now} (next session T+1 entry)</i>",
        "",
        f"<b>Market regime (DT5G):</b> {state_emoji} {state_label} (state={state5})",
        "",
        f"<b>Strategy:</b> V2.3 = BAL | LAG static (always-on, no ensemble switch) + allocator + CAPIT v2",
        f"<b>BAL:</b> max=12 · 10%/pos (book) · hold 45d · stop -20% · Fin/RE cap 4 · 8L≥4 half-size in BEAR/CRISIS",
        f"<b>LAG:</b> PEAD T+5 entry · hold 25td · NO stop · LAG_HI 10% / LAG_LO 8% (book)",
        f"<b>ETF parking:</b> 70% idle cash → E1VFVN30 (NEUTRAL, cả 2 book)",
        f"<b>Guards:</b> SV_TIGHT Fresh-Q · overheat P3 · AVOID_exbull (momentum chặn ở state 5)",
    ]

    # ── Allocator: state-conditional w_LAG, BAND-only rebalance ±10pp ──
    if w_tgt is not None:
        a = f"<b>⚖️ Allocator w_LAG:</b> target <b>{w_tgt*100:.0f}%</b> (state {state5})"
        if w_cur is not None:
            a += f" · current {w_cur*100:.0f}%"
            if st.get("band_breach"):
                a += " → 🔁 <b>REBALANCE — band ±10pp breached</b>"
            else:
                a += " → trong band ±10pp, không trim"
        lines += ["", a]

    # ── State warnings (V2.3 KHÔNG full-cash trong BEAR/CRISIS như V4 cũ) ──
    if state5 is not None and int(state5) == 2:
        lines += ["", "🔴 <b>BEAR:</b> LAG defunded (w_LAG=0 — PEAD lỗ trong bear). "
                      "BAL chỉ Fresh-Q ≤60d, mã 8L≥4 half-size."]
    elif state5 is not None and int(state5) == 1:
        lines += ["", "💀 <b>CRISIS:</b> BAL chỉ Fresh-Q ≤30d, mã 8L≥4 half-size · w_LAG 50% · "
                      "theo dõi CAPIT washout (capitulation-buy)."]

    # Active books
    lines.append(build_book_section(bal_book, "📋 BOOK A — BAL (momentum, allocator-weighted)"))
    lines.append(build_lag_section(lag_df, w_tgt))

    # ── CAPIT v2 monitor ──
    br = st.get("breadth_oversold")
    if br is not None:
        lines.append("")
        if st.get("capit_fired"):
            lines.append(f"<b>🧯 CAPIT v2:</b> 🚨 <b>WASHOUT</b> — breadth oversold {br*100:.1f}% ≥ gate 30%")
            lines.append(f"  size={st.get('capit_size', 0):.2f} (grind={st.get('capit_grind')}, "
                         f"dd52w={st.get('dd52w', '?')}%, vn_cooling={st.get('vn_cooling')})")
            if capit_df is not None and not capit_df.empty:
                lines.append(f"  basket ({len(capit_df)}): " +
                             ", ".join(_esc(t) for t in capit_df["ticker"].tolist()))
            lines.append("  → committed = size × free cash mỗi book · hold 60td · stop/slot-exempt")
        else:
            lines.append(f"<b>🧯 CAPIT v2:</b> breadth oversold {br*100:.1f}% &lt; gate 30% — dormant")

    # Universe stats
    if include_universe and pt_counts:
        lines.append("")
        lines.append("<b>📊 Universe distribution</b>")
        BA_CORE = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
        ba_n = sum(pt_counts.get(t, 0) for t in BA_CORE)
        lines.append(f"  BA-core: <b>{ba_n}</b> mã | Compounder/info: "
                    f"{pt_counts.get('COMPOUNDER_BUY',0)+pt_counts.get('MOMENTUM_QUALITY',0)} mã")
        lines.append(f"  Wait/Pass/Avoid: "
                    f"{pt_counts.get('WAIT',0)+pt_counts.get('PASS',0)+pt_counts.get('AVOID_faE',0)} mã")

    # Execution checklist
    n_bal = len(bal_book)
    n_lag_up = 0
    if lag_df is not None and not lag_df.empty and "status" in lag_df.columns:
        n_lag_up = int(lag_df["status"].astype(str).str.startswith("UPCOMING").sum())
    lines.append("")
    lines.append("<b>💡 Execution checklist (T+1 next session)</b>")
    if w_tgt is not None:
        lines.append(f"  • Vốn: BAL {100 - w_tgt*100:.0f}% / LAG {w_tgt*100:.0f}% NAV (rebal CHỈ khi lệch &gt;10pp)")
    lines.append(f"  • BAL: {n_bal} pos × 10% book · stop -20% · hold 45d")
    lines.append(f"  • LAG: {n_lag_up} entry mới (10/8% book) · NO stop · hold 25td")
    if state5 is not None and int(state5) == 3:
        lines.append(f"  • <b>Cash dư cả 2 book → 70% E1VFVN30</b>")
    else:
        lines.append(f"  • Cash dư → deposit (không parking ngoài NEUTRAL)")

    return "\n".join(lines)


def build_vol_spike_hedge_section() -> str:
    """Block VOL-SPIKE HEDGE cho V5 (paper-trade tạm thời → 2026-06-30).
    Đọc data/vol_spike_hedge_status.json do vol_spike_hedge_pt.py ghi ở papertrade_daily.bat."""
    path = os.path.join(WORKDIR, "data", "vol_spike_hedge_status.json")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as fp:
            s = json.load(fp)
    except Exception:
        return ""
    on = s.get("signal_on", False)
    lines = ["", "<b>🛡️ VOL-SPIKE HEDGE cho V5 (paper-trade → 30/06)</b>", "<pre>"]
    lines.append(f"As of:  {s.get('asof','?')}   VN30F={s.get('vn30f','?')}")
    lines.append(f"rv10 = {s.get('rv10',0)*100:.1f}%   ngưỡng = {s.get('threshold',0)*100:.1f}%")
    if on:
        lines.append(f"CÒ: 🔴 ON (SHORT)")
        lines.append(f"→ Đặt phiên kế: SHORT {s.get('reco_contracts',0)} HĐ VN30F")
        lines.append(f"  (notional {s.get('reco_notional',0):,.0f})")
    else:
        lines.append(f"CÒ: 🟢 OFF (flat) — không hedge")
    if s.get("window_started"):
        lines.append("-"*30)
        lines.append(f"Paper {s.get('n_days',0)} phiên | hedge ON {s.get('on_days',0)}")
        lines.append(f"V5 only   : {s.get('v5_only_ret',0)*100:+.2f}%")
        lines.append(f"V5+hedge  : {s.get('v5_hedged_ret',0)*100:+.2f}%")
        lines.append(f"Đóng góp  : {s.get('hedge_pp',0):+.2f}pp ({s.get('hedge_vnd',0):+,.0f}đ)")
    else:
        lines.append("(paper-trade chờ phiên NAV đầu trong cửa sổ)")
    lines.append("</pre>")
    return "\n".join(lines)


def build_f_sleeve_section() -> str:
    """Block F-SYSTEM STANDALONE sleeve (DT5G+Van, paper-trade → 2026-06-30).
    Đọc data/f_sleeve_status.json do f_sleeve_pt.py ghi ở papertrade_daily.bat."""
    path = os.path.join(WORKDIR, "data", "f_sleeve_status.json")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as fp:
            s = json.load(fp)
    except Exception:
        return ""
    side = s.get("side", "FLAT")
    emoji = "🟢" if side == "LONG" else ("🔴" if side == "SHORT" else "⚪")
    lines = ["", "<b>⚙️ F-SYSTEM sleeve riêng (DT5G+Van, paper → 30/06)</b>", "<pre>"]
    lines.append(f"As of:  {s.get('asof','?')}   VN30F={s.get('vn30f','?')}")
    lines.append(f"DT5G={s.get('state_name','?')}  base={s.get('base',0):+.2f} x scale={s.get('applied_scale',0):.2f}")
    lines.append(f"Position = {s.get('position',0):+.2f}")
    lines.append(f"{emoji} Phiên kế: {side} {s.get('reco_contracts',0)} HĐ VN30F")
    lines.append(f"  (notional {s.get('reco_notional',0):,.0f})")
    if s.get("window_started"):
        lines.append("-"*30)
        lines.append(f"Sleeve base {s.get('sleeve_base',0)/1e9:.0f}B | {s.get('n_days',0)} phiên")
        lines.append(f"Return    : {s.get('sleeve_ret',0)*100:+.2f}%")
        lines.append(f"NAV       : {s.get('sleeve_nav',0):,.0f}")
    lines.append("</pre>")
    return "\n".join(lines)


def build_orb_section() -> str:
    """Block ORB intraday VN30F (paper-trade live). Đọc data/orb_pt_status.json do orb_pt.py ghi."""
    path = os.path.join(WORKDIR, "data", "orb_pt_status.json")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as fp:
            s = json.load(fp)
    except Exception:
        return ""
    lines = ["", "<b>📈 ORB intraday VN30F (paper-trade live)</b>", "<pre>"]
    lines.append(f"Data: {s.get('asof_bar','?')}  VN30F={s.get('latest_vn30f','?')}")
    lines.append("Rule: 09:30 dấu OR(09:00-09:30)")
    lines.append("  → long/short giữ đến 14:30, no stop")
    lines.append(f"Phiên kế: {s.get('reco_contracts',0)} HĐ (sleeve {s.get('sleeve_base',0)/1e9:.0f}B)")
    if s.get("window_started"):
        side = "LONG" if s.get("last_sig",0) > 0 else "SHORT"
        em = "🟢" if s.get("last_net",0) >= 0 else "🔴"
        lines.append("-"*30)
        lines.append(f"Phiên cuối {s.get('last_date','?')}: {side} {em}{s.get('last_net',0)*100:+.2f}%")
        lines.append(f"{s.get('n_days',0)} phiên | WR {s.get('wr',0)*100:.0f}% | Sharpe {s.get('sharpe',0):.2f}")
        lines.append(f"Cum {s.get('cum_ret',0)*100:+.2f}% | NAV {s.get('nav',0):,.0f}")
    else:
        lines.append("(chờ phiên hoàn chỉnh đầu tiên)")
    lines.append("</pre>")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?", help="Target date YYYY-MM-DD (default: latest)")
    parser.add_argument("--dry-run", action="store_true", help="Build message but don't send")
    parser.add_argument("--no-attach", action="store_true", help="Skip CSV attachments")
    args = parser.parse_args()

    cfg = load_config()
    bot_token = cfg["bot_token"]
    chat_id = cfg["chat_id"]

    # Import live engine functions (avoid running its main)
    from recommend_holistic import (bq, load_fa_full, classify_play_type,
                                     select_book, BA_CORE_TIERS,
                                     SCORE_SQL, LATEST_DATE_SQL, VN30_QUERY)

    target = args.date or str(bq(LATEST_DATE_SQL)["d"].iloc[0])
    print(f"[1/4] Target signal date: {target}")

    print(f"[2/4] Loading TA v10 + 5-state…")
    ta_df = bq(SCORE_SQL.format(day=target))
    print(f"      {len(ta_df)} tickers scored")

    fa_df = load_fa_full(target)

    fa_cols = ["ticker", "tier", "total_score", "score_quality", "score_stability",
               "score_cash", "score_shareholder", "score_growth", "score_health",
               "score_valuation", "NP_R", "Revenue_YoY_P0", "NP_peak_ratio",
               "Rev_peak_ratio"]
    fa_subset = fa_df[fa_cols].rename(columns={"tier": "fa_tier",
                                                "total_score": "fa_total_score"})
    df = ta_df.merge(fa_subset, on="ticker", how="left")
    df_liq = df[df["liq_b_vnd"] >= 1.0].copy()

    # ─── DT5G market-detection override (production engine; replaces TQ34b) ───
    # Drive both the headline regime AND book gating / SV_TIGHT / overheat from the
    # DT5G gated live state. Falls back to the TQ34b state5 from SCORE_SQL if DT5G
    # is unavailable, so the report never breaks.
    dt5g_state, dt5g_asof, dt5g_source = get_dt5g_state(target)
    if dt5g_state is not None:
        df_liq["state5"] = dt5g_state
        print(f"      DT5G state: {dt5g_state} (as_of {dt5g_asof}, src {dt5g_source})")
    else:
        print("      DT5G unavailable — keeping TQ34b state5 from SCORE_SQL.")

    play_results = df_liq.apply(classify_play_type, axis=1, result_type="expand")
    play_results.columns = ["play_type", "conviction", "action_note"]
    df_liq = pd.concat([df_liq, play_results], axis=1)
    df_liq = df_liq.sort_values("conviction", ascending=False).reset_index(drop=True)

    state5 = df_liq["state5"].dropna().iloc[0] if df_liq["state5"].notna().any() else None
    state_names = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
    state_label = state_names.get(int(state5)) if state5 else "?"

    print(f"      Market state: {state_label} (state={state5})")

    # Fallback BAL book (BA-core) — overridden by ACTUAL V2.3 picks below when available.
    # V2.3 does NOT go full-cash in BEAR/CRISIS (BAL stays on with Fresh-Q gate + weak
    # half-size; LAG is defunded by the allocator in BEAR) → books are always built,
    # state warnings are added inside build_message.
    bal_book = select_book(df_liq.copy(), max_positions=10, fin_re_cap=4)
    lag_df = pd.DataFrame()
    capit_df = pd.DataFrame()

    # ── Override with ACTUAL V2.3 picks from golive_recommend_v23 (LAYER 2) ──
    # golive_v23 produces BAL + LAG (always-on PEAD) + CAPIT basket to
    # deploy_golive_dt5g_v4/out/golive_v23_recommendations_<date>.csv plus
    # data/golive_v23_status.json (allocator/capit state) — papertrade_daily.bat [4c2].
    # Display data (Close/score/FA/RSI/rating) for the BAL book comes from df_liq.
    v23_status = None
    try:
        with open(os.path.join(WORKDIR, "data", "golive_v23_status.json"), encoding="utf-8") as f:
            v23_status = json.load(f)
    except Exception:
        pass
    try:
        gpath = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out",
                             f"golive_v23_recommendations_{target}.csv")
        if not os.path.exists(gpath):
            # file is named by RUN date; signal date can lag (ticker ingest) → take the newest
            cands = sorted(glob.glob(os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out",
                                                  "golive_v23_recommendations_*.csv")))
            if cands:
                gpath = cands[-1]
        g = pd.read_csv(gpath)
        balt = g[g["book"] == "BAL"]["ticker"].tolist()
        lag_df = g[g["book"] == "LAG"].copy()
        capit_df = g[g["book"] == "CAPIT"].copy()
        def _book_from(tks):
            if not tks: return pd.DataFrame()
            sub = df_liq[df_liq["ticker"].isin(tks)].copy()
            order = {t: i for i, t in enumerate(tks)}
            sub["__o"] = sub["ticker"].map(order)
            return sub.sort_values("__o").drop(columns="__o").reset_index(drop=True)
        bal_book = _book_from(balt)
        print(f"      golive V2.3 picks: BAL {len(balt)} + LAG {len(lag_df)} + CAPIT {len(capit_df)}"
              f" ({os.path.basename(gpath)})")
    except Exception as e:
        print(f"      golive V2.3 CSV unavailable ({e}); fallback to BA-core BAL book")

    pt_counts = df_liq["play_type"].value_counts().to_dict()

    print(f"[3/4] Building Telegram message…")
    message = build_message(target, state5, state_label, bal_book, lag_df, capit_df,
                             pt_counts, len(fa_df),
                             include_universe=cfg.get("include_universe_stats", True),
                             v23_status=v23_status)

    # Append DT5G market-state section (engine status + transitions + paper-trade systems)
    print(f"      Building DT5G market-state section…")
    state_section, state_csv_path = build_dt5g_section(target, dt5g_state, dt5g_asof, dt5g_source)
    message = message + "\n" + state_section

    # Append VOL-SPIKE HEDGE block (paper-trade tạm thời cho V5 → 2026-06-30)
    hedge_section = build_vol_spike_hedge_section()
    if hedge_section:
        message = message + "\n" + hedge_section

    # Append F-SYSTEM standalone sleeve block (DT5G+Van paper-trade → 2026-06-30)
    fsleeve_section = build_f_sleeve_section()
    if fsleeve_section:
        message = message + "\n" + fsleeve_section

    # Append ORB intraday block (paper-trade live)
    orb_section = build_orb_section()
    if orb_section:
        message = message + "\n" + orb_section

    # Save full universe CSV (for attachment + audit log)
    out_csv = os.path.join(WORKDIR, f"holistic_{target}.csv")
    df_liq.to_csv(out_csv, index=False)
    bal_path = os.path.join(WORKDIR, f"ba_book_bal_{target}.csv")
    lag_path = os.path.join(WORKDIR, f"ba_book_lag_{target}.csv")
    if not bal_book.empty:
        bal_book.to_csv(bal_path, index=False)
    if not lag_df.empty:
        lag_df.to_csv(lag_path, index=False)

    print()
    print("=" * 80)
    print("MESSAGE PREVIEW")
    print("=" * 80)
    print(message)
    print("=" * 80)
    print(f"Message length: {len(message)} chars (Telegram limit ~4096)")

    if args.dry_run:
        print("\n[--dry-run] not sending. Done.")
        return

    print(f"\n[4/4] Sending to Telegram chat {chat_id}…")
    chunks = split_message(message)
    for i, ch in enumerate(chunks, 1):
        r = send_telegram_text(bot_token, chat_id, ch)
        ok = r.get("ok", False)
        print(f"  Chunk {i}/{len(chunks)} ({len(ch)} chars): {'✓ sent' if ok else '✗ ' + str(r)}")
        time.sleep(0.5)  # rate limit safety

    # AMH Cockpit (V6 Tứ Trụ allocation + #1 edge-health/capit-edge + #4 ecology) as a separate message
    cockpit_path = os.path.join(WORKDIR, "data", "amh_cockpit.md")
    if os.path.exists(cockpit_path):
        try:
            with open(cockpit_path, encoding="utf-8") as f:
                cockpit = f.read().strip()
            for i, ch in enumerate(split_message(cockpit), 1):
                r = send_telegram_text(bot_token, chat_id, ch)
                print(f"  Cockpit {i} ({len(ch)} chars): {'✓ sent' if r.get('ok') else '✗ ' + str(r)}")
                time.sleep(0.5)
        except Exception as e:
            print(f"  [cockpit] skipped: {e}")

    # Send CSV attachments (BA books only — not full universe to save bandwidth)
    if not args.no_attach:
        attach_list = [(bal_path, "BAL book CSV"), (lag_path, "LAG book CSV")]
        if state_csv_path and os.path.exists(state_csv_path):
            attach_list.append((state_csv_path, "DT5G state history from Apr 1"))
        for path, label in attach_list:
            if os.path.exists(path) and os.path.getsize(path) < 50_000_000:  # 50MB limit
                r = send_telegram_document(bot_token, chat_id, path,
                                            caption=f"<b>{label}</b> — {target}")
                ok = r.get("ok", False)
                fname = os.path.basename(path)
                print(f"  Attachment {fname}: {'✓ sent' if ok else '✗'}")
                time.sleep(0.5)

    print("\n✓ Done.")


if __name__ == "__main__":
    main()
