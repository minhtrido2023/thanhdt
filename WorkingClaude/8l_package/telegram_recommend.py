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
import json
import time
import argparse
from datetime import datetime

import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
# Note: recommend_holistic.py wraps sys.stdout at import time; rely on that.

CONFIG_PATH = os.path.join(WORKDIR, "telegram_config.json")
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

    # Paper-trade systems (incl. V4 12.1 on DT5G, fresh from today)
    lines.append("")
    lines.append("<b>📊 Paper-trade systems chạy daily</b>")
    lines.append("<pre>")
    lines.append(f"V11        (Song Sinh + KELLY)        → DT5G")
    lines.append(f"V12        (Âm Dương: BAL+LAGGED)     → DT5G")
    lines.append(f"V121_ENS   (V12.1 + Ensemble + BASE)  → TQ34b")
    lines.append(f"V121_Kelly (V12.1 + Ensemble + KELLY) → TQ34b")
    lines.append(f"V4 12.1 ⭐  (V121_ENS + BASE)          → DT5G  [fresh 2026-06-01]")
    lines.append("</pre>")
    v4 = _read_pt_nav("data/pt_v4_dt5g_logs.csv")
    if v4:
        if v4["n"] <= 1:
            lines.append(f"<i>V4 12.1: khởi tạo 50B, <b>chạy từ {v4['start']}</b> — chờ phiên giao dịch đầu tiên.</i>")
        else:
            lines.append(f"<i>V4 12.1: <b>chạy từ {v4['start']}</b> — NAV {v4['nav']/1e9:.3f}B ({v4['ret']:+.2f}%) sau {v4['n']} phiên.</i>")

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


def build_message(target: str, state5, state_label: str,
                   bal_book: pd.DataFrame, vn30_book: pd.DataFrame,
                   pt_counts: dict, fa_count: int,
                   include_f_overlay: bool = True,
                   include_universe: bool = True,
                   second_label: str = "Ensemble (VN30/LAGGED)") -> str:
    """Build the main Telegram HTML message."""

    state_emoji = {"CRISIS": "💀", "BEAR": "🔴", "NEUTRAL": "🟡",
                    "BULL": "🟢", "EX-BULL": "🔥"}.get(state_label, "❓")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"<b>🛰️ V4 12.1 (DT5G) REPORT — {target}</b>",
        f"<i>Sent: {now} (next session T+1 entry)</i>",
        "",
        f"<b>Market regime (DT5G):</b> {state_emoji} {state_label} (state={state5})",
        "",
        f"<b>Strategy:</b> V4 12.1 = 50% BAL + 50% Ensemble (VN30/LAGGED theo mode) + BASE parking",
        f"<b>PM:</b> max=12pos · 10%/pos · hold=45d · stop -20% · BL20 · T+3 min hold",
        f"<b>ETF parking BASE:</b> 70% idle cash → VN30 ETF (NEUTRAL only)",
        f"<b>Fresh-Q SV_TIGHT:</b> ≤30d state 1 / ≤60d state 2-3 / no filter state 4-5",
        f"<b>Overheat P3:</b> block buys when VNI/MA200>1.30 AND (state 5 OR D_RSI>0.75)",
    ]

    if state5 is not None and int(state5) in (1, 2):
        lines.append("")
        lines.append("❌ <b>BEAR/CRISIS regime — V4 12.1 về cash. Không vào lệnh mới.</b>")
        lines.append("")
        lines.append("→ Toàn bộ vốn phòng thủ (deposit). Không ETF parking.")
        return "\n".join(lines)

    # Active books
    lines.append(build_book_section(bal_book, "📋 BOOK A — BAL+Fin/RE-max-4 (50% NAV)"))
    lines.append(build_book_section(vn30_book, f"📋 BOOK B — {second_label} leg (50% NAV) [mode hôm nay]"))

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
    n_vn30 = len(vn30_book)
    lines.append("")
    lines.append("<b>💡 Execution checklist (T+1 next session)</b>")
    lines.append(f"  • BAL: {n_bal} pos × 5% NAV = {n_bal*5}% deployed")
    lines.append(f"  • VN30: {n_vn30} pos × 5% NAV = {n_vn30*5}% deployed")
    if state5 == 3:
        lines.append(f"  • <b>Cash dư → 70% VN30 ETF (E1VFVN30)</b>")
    else:
        lines.append(f"  • Cash dư → deposit (defensive)")
    lines.append(f"  • Stop -20%, hold 45d, BL20 after stop")

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
    vn30_set = set(bq(VN30_QUERY)["ticker"])

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

    # Build books (or empty in BEAR/CRISIS)
    if state5 is not None and int(state5) in (1, 2):
        bal_book = pd.DataFrame()
        vn30_book = pd.DataFrame()
    else:
        bal_book = select_book(df_liq.copy(), max_positions=10, fin_re_cap=4)
        vn30_book = select_book(df_liq[df_liq["ticker"].isin(vn30_set)].copy(),
                                  max_positions=10, fin_re_cap=None)

    # ── Override with ACTUAL V4 12.1 picks from golive_recommend (LAYER 2) ──
    # golive produces BAL book + active 2nd leg (VN30 OR LAGGED, by ensemble mode today) to
    # deploy_golive_dt5g_v4/out/golive_recommendations_<date>.csv (run in papertrade_daily.bat).
    # We keep the BA-core books as fallback; display data (Close/score/FA/RSI/rating) comes from df_liq.
    active_second = "Ensemble (VN30/LAGGED)"
    if state5 is not None and int(state5) not in (1, 2):
        try:
            gpath = os.path.join(WORKDIR, "deploy_golive_dt5g_v4", "out", f"golive_recommendations_{target}.csv")
            g = pd.read_csv(gpath)
            balt = g[g["book"].astype(str).str.startswith("BAL")]["ticker"].tolist()
            secr = g[~g["book"].astype(str).str.startswith("BAL")]
            sect = secr["ticker"].tolist()
            if len(secr): active_second = str(secr["book"].iloc[0]).split("(")[0]   # "VN30" or "LAGGED"
            def _book_from(tks):
                if not tks: return pd.DataFrame()
                sub = df_liq[df_liq["ticker"].isin(tks)].copy()
                order = {t: i for i, t in enumerate(tks)}
                sub["__o"] = sub["ticker"].map(order)
                return sub.sort_values("__o").drop(columns="__o").reset_index(drop=True)
            bal_book = _book_from(balt)
            vn30_book = _book_from(sect)
            print(f"      golive V4 12.1 picks: BAL {len(balt)} + {active_second} {len(sect)}")
        except Exception as e:
            print(f"      golive CSV unavailable ({e}); fallback to BA-core books")

    pt_counts = df_liq["play_type"].value_counts().to_dict()

    print(f"[3/4] Building Telegram message…")
    message = build_message(target, state5, state_label, bal_book, vn30_book,
                             pt_counts, len(fa_df),
                             include_f_overlay=cfg.get("include_f_overlay", True),
                             include_universe=cfg.get("include_universe_stats", True),
                             second_label=active_second)

    # Append DT5G market-state section (engine status + transitions + paper-trade systems)
    print(f"      Building DT5G market-state section…")
    state_section, state_csv_path = build_dt5g_section(target, dt5g_state, dt5g_asof, dt5g_source)
    message = message + "\n" + state_section

    # Save full universe CSV (for attachment + audit log)
    out_csv = os.path.join(WORKDIR, f"holistic_{target}.csv")
    df_liq.to_csv(out_csv, index=False)
    bal_path = os.path.join(WORKDIR, f"ba_book_bal_{target}.csv")
    vn30_path = os.path.join(WORKDIR, f"ba_book_vn30_{target}.csv")
    if not bal_book.empty:
        bal_book.to_csv(bal_path, index=False)
    if not vn30_book.empty:
        vn30_book.to_csv(vn30_path, index=False)

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

    # Send CSV attachments (BA books only — not full universe to save bandwidth)
    if not args.no_attach:
        attach_list = [(bal_path, "BAL book CSV"), (vn30_path, "VN30 book CSV")]
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
