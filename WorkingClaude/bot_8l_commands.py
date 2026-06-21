#!/usr/bin/env python3
"""bot_8l_commands.py — interactive list commands for the 8L Telegram bot.

Three commands, consumed by telegram_8l_bot.py:
  • "10" / "20" / "30" / "top 15" → format_topn(n): the current 8L top-N table.
  • "new" / "mới"                 → format_new(): tickers that ENTERED top-30 within the last week.

The top-N table reads data/rank_8l.csv (composite 8L score, refreshed EOD by rank_8l.py)
plus data/rating_8l.csv for the credit-style quality rating (R, 1=best..5=spec).

"new" needs a ~7-day-old baseline. rank_8l_prev.csv is overwritten every day by
rank_8l_daily_alert.py (so it is only "yesterday"), therefore this module keeps its OWN
dated snapshots under data/rank_8l_snap/. A snapshot is written:
  • every EOD by pt_8l_daily.bat  → python -c "import bot_8l_commands as b; b.snapshot_today()"
  • lazily whenever someone asks "new" (idempotent, cheap).
The baseline for the diff is the snapshot closest to (today − 7 days); if none that old yet,
the oldest snapshot we have is used and its date is shown so the window is explicit.

CLI test:
  python bot_8l_commands.py 10
  python bot_8l_commands.py new
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, glob, datetime
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd

WORKDIR = os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
DATA    = os.path.join(WORKDIR, "data")
RANK_CSV = os.path.join(DATA, "rank_8l.csv")
PREV_CSV = os.path.join(DATA, "rank_8l_prev.csv")
RATING_CSV = os.path.join(DATA, "rating_8l.csv")
VN30_CSV = os.path.join(DATA, "vn30_8l.csv")
SNAP_DIR = os.path.join(DATA, "rank_8l_snap")

ROUTE_SHORT = {"BANK": "BANK", "CYCLICAL": "CYC", "COMPOUNDER": "CMP",
               "POWER": "PWR", "SUGAR": "SUG"}
STATE_INFO = {1: ("💀", "CRISIS", 0, "VỀ CASH — không giải ngân rổ"),
              2: ("🔴", "BEAR", 20, "Giảm mạnh, ~20% NAV — phòng thủ"),
              3: ("🟡", "NEUTRAL", 70, "~70% NAV vào rổ, dư → tiền gửi/ETF"),
              4: ("🟢", "BULL", 100, "Full 100% rổ"),
              5: ("🔥", "EX-BULL", 100, "Full (hệ 5-state cho phép tới 130% đòn bẩy)")}

TOPN_NEW = 30          # universe for the "new" window
WINDOW_DAYS = 7        # "trong tuần" = look back ~7 calendar days
MAX_TOPN = 50          # cap a numeric request so a message stays under Telegram's 4096


# ── data loaders ─────────────────────────────────────────────────────────
def _load_rank(path=RANK_CSV):
    df = pd.read_csv(path)
    if "rank" not in df.columns:
        df = df.reset_index(drop=True); df["rank"] = df.index + 1
    return df.sort_values("rank").reset_index(drop=True)


def _rating_map():
    try:
        r = pd.read_csv(RATING_CSV)
        return {t: (int(v) if pd.notna(v) else None) for t, v in zip(r["ticker"], r["rating"])}
    except Exception:
        return {}


# ── snapshot management ──────────────────────────────────────────────────
def snapshot_today():
    """Idempotently freeze today's rank_8l.csv into the dated snapshot dir. Returns path or None."""
    try:
        os.makedirs(SNAP_DIR, exist_ok=True)
        today = datetime.date.today().isoformat()
        dst = os.path.join(SNAP_DIR, f"rank_8l_{today}.csv")
        if not os.path.exists(dst):
            _load_rank().to_csv(dst, index=False)
        return dst
    except Exception as e:
        print("snapshot_today err:", e); return None


def _seed_from_legacy():
    """Bootstrap the snapshot dir from the two legacy files (rank_8l.csv = today,
    rank_8l_prev.csv = its mtime date) so 'new' has data before a full week accrues."""
    os.makedirs(SNAP_DIR, exist_ok=True)
    for src in (RANK_CSV, PREV_CSV):
        if not os.path.exists(src):
            continue
        d = datetime.date.fromtimestamp(os.path.getmtime(src)).isoformat()
        dst = os.path.join(SNAP_DIR, f"rank_8l_{d}.csv")
        if not os.path.exists(dst):
            try: pd.read_csv(src).to_csv(dst, index=False)
            except Exception: pass


def _list_snapshots():
    out = []
    for f in glob.glob(os.path.join(SNAP_DIR, "rank_8l_*.csv")):
        ds = os.path.basename(f)[len("rank_8l_"):-4]
        try: d = datetime.date.fromisoformat(ds)
        except Exception: continue
        out.append((d, f))
    return sorted(out)


# ── command: top N — DEFAULT = 2-AXIS SCREENER (quality moat-audited × value) ──────────
# (user 2026-06-14) A quality-only top-N surfaces uninvestable names (MCH/VTP at top-0.2% PB). The
# default list must be BOTH axes: rating<=3 (moat-AUDITED) × pb_z (cheap vs own history), zoned into
# BUY-NOW / ACCUMULATE / WATCH-RICH so the reader sees what to buy vs what's great-but-too-expensive.
SCREENER_CSV = os.path.join(DATA, "rating_8l_screener.csv")
_ZONE_LBL = {"1_BUY-NOW": "🟢 BUY-NOW (rẻ vs lịch sử + book-OK)",
             "2_ACCUMULATE": "🟡 ACCUMULATE (định giá hợp lý)",
             "3_WATCH-RICH": "🔴 WATCH-RICH (chất lượng nhưng ĐẮT — đừng đuổi)"}
_MOAT_SHORT = {"WIDE": "WIDE", "NARROW": "NARR", "NONE": "NONE"}

def format_topn(n):
    try:
        s = pd.read_csv(SCREENER_CSV)
    except Exception:
        return _format_rank_composite(n)   # fallback: legacy composite-momentum rank
    n = max(1, min(int(n), MAX_TOPN))
    order = {"1_BUY-NOW": 0, "2_ACCUMULATE": 1, "3_WATCH-RICH": 2, "4_TRAP": 3}
    s["_o"] = s["zone"].map(order)
    s = s.sort_values(["_o", "rating", "pb_z"]).reset_index(drop=True)
    act = s[s["zone"].isin(["1_BUY-NOW", "2_ACCUMULATE"])].head(n)   # actionable first
    lines = ["<b>🎯 8L Screener — 2 trục (chất lượng × định giá)</b>", "<pre>",
             f"{'Mã':<4} {'R':<1} {'Moat':<4} {'pbz':>5}"]
    cur = None
    for _, r in act.iterrows():
        if r["zone"] != cur:
            cur = r["zone"]; lines.append(_ZONE_LBL.get(cur, cur))
        m = _MOAT_SHORT.get(str(r.get("moat5f")), "—")
        lines.append(f"{str(r['ticker']):<4} {int(r['rating']):<1} {m:<4} {float(r['pb_z']):>5.2f}")
    lines.append("</pre>")
    wr = s[s["zone"] == "3_WATCH-RICH"]["ticker"].tolist()
    if wr:
        lines.append(f"<i>🔴 WATCH-RICH ({len(wr)} mã quá đắt, đừng đuổi): " + ", ".join(wr[:12])
                     + ("…" if len(wr) > 12 else "") + "</i>")
    lines.append("<i>R = rating 8L (moat-AUDITED, 1=cao nhất); Moat = 5F tier; pbz = PB vs lịch-sử-riêng "
                 "(âm = rẻ). Gõ mã để xem chi tiết, /rank để xem bảng momentum.</i>")
    return "\n".join(lines)

def _format_rank_composite(n):
    """Legacy composite-momentum rank (rank_8l.csv) — now the /rank view, not the default."""
    try:
        df = _load_rank()
    except Exception as e:
        return f"Không đọc được rank_8l.csv ({e})."
    n = max(1, min(int(n), min(MAX_TOPN, len(df))))
    rmap = _rating_map()
    head = df.head(n)
    lines = [f"<b>🏆 8L — Composite rank Top {n}</b>  <i>(universe {len(df)} mã)</i>", "<pre>",
             f"{'#':>2} {'Mã':<4} {'R':<1} {'Route':<5} {'Sc':>3}  Verdict"]
    for _, r in head.iterrows():
        rk = int(r["rank"]); t = str(r["ticker"])
        route = str(r.get("route", "") or "")[:5]
        sc = float(r["score"]) if pd.notna(r.get("score")) else 0.0
        v = str(r.get("verdict", "") or "")[:13]
        rt = rmap.get(t); rts = str(rt) if rt is not None else "-"
        lines.append(f"{rk:>2} {t:<4} {rts:<1} {route:<5} {sc:>3.0f}  {v}")
    lines.append("</pre>")
    lines.append("<i>R = chất lượng 8L 1–5 (1=cao nhất, ≤3=đầu tư). Gõ mã (vd BMP) để xem chi tiết.</i>")
    return "\n".join(lines)


# ── command: new entrants to top-30 this week ────────────────────────────
def _pick_baseline():
    """Return (baseline_df, baseline_date) ~7 days back, or (None, None)."""
    snaps = _list_snapshots()
    today = datetime.date.today()
    # drop today's own snapshot from baseline candidates
    snaps = [(d, f) for d, f in snaps if d < today]
    if not snaps:
        return None, None
    target = today - datetime.timedelta(days=WINDOW_DAYS)
    older = [(d, f) for d, f in snaps if d <= target]
    d, f = older[-1] if older else snaps[0]   # closest ≤ target, else oldest available
    try:
        return pd.read_csv(f), d
    except Exception:
        return None, None


def format_new(topn=TOPN_NEW):
    try:
        cur = _load_rank()
    except Exception as e:
        return f"Không đọc được rank_8l.csv ({e})."
    _seed_from_legacy()
    snapshot_today()
    base, bdate = _pick_baseline()
    if base is None:
        return ("<b>🆕 8L — mã mới vào Top 30</b>\n"
                "<i>Chưa có baseline tuần trước — đã tạo snapshot hôm nay. "
                "Hỏi lại sau vài phiên để có dữ liệu so sánh.</i>")

    if "rank" not in base.columns:
        base = base.reset_index(drop=True); base["rank"] = base.index + 1
    base_rank = {str(t): int(rk) for t, rk in zip(base["ticker"], base["rank"])}
    base_top = set(base[base["rank"] <= topn]["ticker"].astype(str))

    cur_top = cur[cur["rank"] <= topn]
    rmap = _rating_map()
    try: SDET = pd.read_csv(os.path.join(DATA, "unified_screener.csv")).set_index("ticker")["detail"].to_dict()
    except Exception: SDET = {}
    # valuation axis (zone + pb_z) so a new entrant that is great-but-EXPENSIVE is flagged
    try:
        _sc = pd.read_csv(SCREENER_CSV)
        ZMAP = {str(t): (str(z), float(p) if pd.notna(p) else None)
                for t, z, p in zip(_sc["ticker"], _sc["zone"], _sc["pb_z"])}
    except Exception:
        ZMAP = {}
    _ZEMO = {"1_BUY-NOW": "🟢", "2_ACCUMULATE": "🟡", "3_WATCH-RICH": "🔴", "4_TRAP": "⛔"}

    newcomers = [r for _, r in cur_top.iterrows() if str(r["ticker"]) not in base_top]
    dropped = sorted(base_top - set(cur_top["ticker"].astype(str)))

    days_ago = (datetime.date.today() - bdate).days
    hdr = (f"<b>🆕 8L — mã mới vào Top {topn}</b>\n"
           f"<i>so với {bdate} ({days_ago} ngày trước)</i>")
    if not newcomers:
        msg = hdr + "\n\n<i>Không có mã mới — Top 30 ổn định trong cửa sổ này.</i>"
    else:
        lines = [hdr, "<pre>"]
        lines.append(f"{'Mã':<4} {'R':<1} {'$':<1} {'pbz':>5} {'Route':<6} {'Sc':>3}  Δrank")
        rich_new = []
        for r in newcomers:
            t = str(r["ticker"]); rk = int(r["rank"]); sc = float(r["score"]) if pd.notna(r.get("score")) else 0.0
            route = str(r.get("route", "") or "")[:6]
            rt = rmap.get(t); rts = str(rt) if rt is not None else "-"
            prev = base_rank.get(t)
            where = f"#{prev}→#{rk}" if prev else f"mới→#{rk}"
            z, pz = ZMAP.get(t, ("", None))
            zmark = _ZEMO.get(z, "·"); pzs = f"{pz:>5.2f}" if pz is not None else "   - "
            if z == "3_WATCH-RICH": rich_new.append(t)
            lines.append(f"{t:<4} R{rts} {zmark} {pzs} {route:<6} sc{sc:>3.0f}  {where}")
        lines.append("</pre>")
        lines.append("<i>$ = trục định giá: 🟢 rẻ vs lịch sử / 🟡 hợp lý / 🔴 ĐẮT (WATCH-RICH) / ⛔ trap. pbz = PB z-score.</i>")
        if rich_new:
            lines.append(f"<i>⚠️ Mã mới nhưng ĐẮT (đừng đuổi): {', '.join(rich_new)}</i>")
        # one-line verdicts/details
        for r in newcomers[:8]:
            t = str(r["ticker"]); det = str(SDET.get(t, "")).split("|")[0].strip()[:64]
            v = str(r.get("verdict", "") or "")
            lines.append(f"• <b>{t}</b> {v}" + (f" — <i>{det}</i>" if det else ""))
        msg = "\n".join(lines)
    if dropped:
        msg += f"\n<i>Rời top {topn}: {', '.join(dropped[:12])}</i>"
    return msg


# ── command: the deployable 8L-VN30 basket + live DT5G gate ──────────────
def _dt5g_gate():
    """(state:int, as_of:str, source:str) from the live DT5G engine, or (None,None,None)."""
    try:
        import datetime
        from telegram_recommend import get_dt5g_state
        return get_dt5g_state(datetime.date.today().isoformat())
    except Exception as e:
        print("dt5g gate err:", e); return None, None, None

def format_vn30():
    # ensure the basket cache exists (built EOD by vn30_8l.py); rebuild on-demand if missing
    if not os.path.exists(VN30_CSV):
        try:
            import vn30_8l; vn30_8l.build()
        except Exception as e:
            return f"<b>📦 8L-VN30</b>\n<i>Chưa có cache rổ (data/vn30_8l.csv) và dựng lại lỗi: {e}</i>"
    df = pd.read_csv(VN30_CSV)
    n = len(df)
    # live market gate
    st, asof, src = _dt5g_gate()
    lines = [f"<b>📦 8L-VN30 — {n} mã chất lượng thanh khoản (đều tay {100/n:.1f}%/mã)</b>"]
    if st is not None and int(st) in STATE_INFO:
        em, nm, alloc, act = STATE_INFO[int(st)]
        srcn = ("DT5G+macro" if src == "DT5G_macro" else "DT4 (feed degraded)" if src == "DT4_only" else (src or ""))
        lines.append(f"🛰️ Cổng DT5G: {em} <b>{nm}</b> → phân bổ đề xuất <b>{alloc}%</b> NAV")
        lines.append(f"<i>{act} · as-of {asof}{(' · '+srcn) if srcn else ''}</i>")
    else:
        lines.append("🛰️ <i>Cổng DT5G không khả dụng — hiển thị rổ, tự quyết phân bổ.</i>")
    lines.append("<pre>")
    lines.append(f"{'#':>2} {'Mã':<4} {'Route':<4} {'Sc':>3} {'tỷ/ng':>6}")
    for _, r in df.iterrows():
        rt = ROUTE_SHORT.get(str(r["route"]), str(r["route"])[:4])
        liq = f"{r['liq']:.0f}" if pd.notna(r["liq"]) else "-"
        lines.append(f"{int(r['basket_rank']):>2} {str(r['ticker']):<4} {rt:<4} {r['score']:>3.0f} {liq:>6}")
    lines.append("</pre>")
    lines.append("<i>Lọc ≥10B/ngày, top điểm 8L, tái cơ cấu theo quý. Backtest: vs VN30 lợi thế = "
                 "drawdown thấp hơn ~10pp (phòng thủ), không phải lợi nhuận vượt trội.</i>")
    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    arg = (sys.argv[1] if len(sys.argv) > 1 else "10").strip().lower()
    if arg in ("vn30", "/vn30", "ro", "rổ", "basket"):
        print(format_vn30())
    elif arg in ("new", "mới", "moi", "/new"):
        print(format_new())
    elif arg.isdigit():
        print(format_topn(int(arg)))
    elif arg == "snapshot":
        print("snapshot ->", snapshot_today())
    else:
        print(format_topn(10))
