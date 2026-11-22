#!/usr/bin/env python3
"""thesis_cards.py — đọc/kiểm sổ thẻ luận điểm `kb/thesis_cards.json` (B3, 22/11/2026).

CHỈ HIỂN THỊ/NHẮC: không đụng luật thoát, plan, lệnh, trading_bot. Dùng chung cho
`thesis_cards_selfcheck.py` và `thesis_card_watch.py`.
"""
import datetime as dt
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.dirname(HERE)
WC = "/home/trido/thanhdt/WorkingClaude"
CARDS = os.path.join(MIKE, "kb", "thesis_cards.json")
LEDGER = os.path.join(MIKE, "kb", "dd_price_zones.json")
EXEC_DIR = os.environ.get("TC_EXEC_DIR") or os.path.join(WC, "data", "execution_logs")
EXIT_RULES = os.path.join(WC, "data", "discretionary_exit_rules.json")
DEAL_TYPES = ("value_long", "event_trade", "fixed_rules")
MS_STATUS = ("pending", "checked_ok", "checked_bad", "waived")
ACCOUNTS = ("SpaceX", "ZaloPay")
DISC_BOOK = "DISCRETIONARY_SPECIAL"
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def latest_cards(doc):
    """{ticker: card rev cao nhất}."""
    out = {}
    for c in doc.get("cards", []):
        t = c.get("ticker")
        if t and (t not in out or c.get("rev", 1) > out[t].get("rev", 1)):
            out[t] = c
    return out


def latest_ledger(entries):
    """{ticker: entry (dd_date, rev) cao nhất} — cùng luật sổ giá."""
    out = {}
    for e in entries:
        k = (e.get("dd_date", ""), e.get("rev", 1))
        t = e["ticker"]
        if t not in out or k > (out[t].get("dd_date", ""), out[t].get("rev", 1)):
            out[t] = e
    return out


def is_iso(s):
    if not isinstance(s, str) or not _ISO.match(s):
        return False
    try:
        dt.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def validate(doc, ledger_entries, held=None):
    """→ list lỗi (rỗng = OK). held = {ticker: {account: qty}} mã đang giữ trong book DISCRETIONARY_SPECIAL
    (None = bỏ qua kiểm 'mã đang giữ phải có thẻ')."""
    errs = []
    if doc.get("schema") != "thesis_cards/v1":
        errs.append("schema != thesis_cards/v1")
    cards = doc.get("cards")
    if not isinstance(cards, list) or not cards:
        return errs + ["cards rỗng/không phải list"]
    seen = {}
    for i, c in enumerate(cards):
        tag = f"cards[{i}] {c.get('ticker')}#{c.get('rev')}"
        for k in ("ticker", "accounts", "deal_type", "exit_policy", "entry", "thesis", "dd_ref", "milestones",
                  "abandon_triggers", "drawdown_review", "last_review_at", "status"):
            if k not in c:
                errs.append(f"{tag}: thiếu '{k}'")
        t, rev = c.get("ticker"), c.get("rev")
        if not isinstance(rev, int) or rev < 1:
            errs.append(f"{tag}: rev phải int ≥1")
        else:
            seen.setdefault(t, []).append(rev)
        if c.get("deal_type") not in DEAL_TYPES:
            errs.append(f"{tag}: deal_type {c.get('deal_type')!r} ∉ {DEAL_TYPES}")
        if c.get("status") not in ("active", "closed"):
            errs.append(f"{tag}: status {c.get('status')!r}")
        if not is_iso(c.get("last_review_at")):
            errs.append(f"{tag}: last_review_at không phải ISO")
        ep = c.get("exit_policy") or {}
        if not ep.get("kind") or not ep.get("approval_ref"):
            errs.append(f"{tag}: exit_policy cần kind + approval_ref")
        if c.get("deal_type") == "value_long" and ep.get("kind") != "user_decides":
            errs.append(f"{tag}: value_long ⇒ exit_policy.kind phải 'user_decides'")
        if c.get("deal_type") == "fixed_rules" and not ep.get("approval_ref"):
            errs.append(f"{tag}: fixed_rules cần approval_ref")
        th = c.get("thesis")
        if not isinstance(th, list) or not (1 <= len(th) <= 3):
            errs.append(f"{tag}: thesis phải list 1–3 dòng")
        en = c.get("entry") or {}
        if not is_iso(en.get("date")) or not en.get("source") or not isinstance(en.get("cost"), dict) or not en["cost"]:
            errs.append(f"{tag}: entry cần date ISO + cost{{account}} + source")
        else:
            for a, v in en["cost"].items():
                if not isinstance(v.get("cost_price"), (int, float)) or v["cost_price"] <= 0:
                    errs.append(f"{tag}: entry.cost[{a}].cost_price không hợp lệ")
        dr = c.get("drawdown_review") or {}
        if dr.get("pct") != 15 or "KHÔNG phải lệnh bán" not in str(dr.get("protocol")):
            errs.append(f"{tag}: drawdown_review phải pct=15 + protocol nêu 'KHÔNG phải lệnh bán'")
        ids = set()
        for m in c.get("milestones") or []:
            mt = f"{tag} milestone {m.get('id')}"
            if not m.get("id") or m["id"] in ids:
                errs.append(f"{mt}: id thiếu/trùng")
            ids.add(m.get("id"))
            if not is_iso(m.get("date")):
                errs.append(f"{mt}: date không ISO")
            if not m.get("source"):
                errs.append(f"{mt}: thiếu source")
            if not m.get("owner") or not m.get("metric"):
                errs.append(f"{mt}: thiếu owner/metric")
            if m.get("status") not in MS_STATUS:
                errs.append(f"{mt}: status {m.get('status')!r}")
            if m.get("status") in ("checked_ok", "checked_bad") and not is_iso(m.get("checked_at")):
                errs.append(f"{mt}: đã chấm mà thiếu checked_at ISO")
        if not (c.get("milestones") or []):
            errs.append(f"{tag}: milestones rỗng")
        aids = set()
        for a in c.get("abandon_triggers") or []:
            at = f"{tag} abandon {a.get('id')}"
            if not a.get("id") or a["id"] in aids:
                errs.append(f"{at}: id thiếu/trùng")
            aids.add(a.get("id"))
            if not a.get("condition") or not a.get("how_measured") or not a.get("current_status"):
                errs.append(f"{at}: thiếu condition/how_measured/current_status")
        if not (c.get("abandon_triggers") or []):
            errs.append(f"{tag}: abandon_triggers rỗng")
        if c.get("draft_pending_user_review") is not None and not isinstance(c["draft_pending_user_review"], bool):
            errs.append(f"{tag}: draft_pending_user_review phải bool")
    # append-only: rev liên tục 1..N mỗi mã, không trùng
    for t, revs in seen.items():
        if sorted(revs) != list(range(1, len(revs) + 1)):
            errs.append(f"{t}: rev không liên tục/trùng {sorted(revs)} (append-only: 1..N)")
    # dd_ref khớp sổ giá rev cuối (hoặc ghi lý do)
    lg = latest_ledger(ledger_entries)
    for t, c in latest_cards(doc).items():
        d = c.get("dd_ref") or {}
        e = lg.get(t)
        if e is None:
            errs.append(f"{t}: không có entry trong sổ giá DD")
            continue
        if d.get("stale_reason"):
            continue
        for k_ref, k_led in (("dd_date", "dd_date"), ("rev", "rev"), ("center", "center"),
                             ("zone_low", "zone_low"), ("zone_high", "zone_high")):
            if d.get(k_ref) != e.get(k_led, 1 if k_led == "rev" else None):
                errs.append(f"{t}: dd_ref.{k_ref}={d.get(k_ref)!r} ≠ sổ giá rev cuối {e.get(k_led)!r} "
                            f"(cập nhật thẻ rev+1 hoặc ghi dd_ref.stale_reason)")
    # mọi mã đang giữ trong book DISCRETIONARY_SPECIAL phải có thẻ active
    if held is not None:
        act = {t for t, c in latest_cards(doc).items() if c.get("status") == "active"}
        for t, accs in held.items():
            if t not in act:
                errs.append(f"{t}: đang giữ trong {DISC_BOOK} ({', '.join(sorted(accs))}) nhưng KHÔNG có thẻ active")
    return errs


# ---------------------------------------------------------------- vị thế đang giữ
def raw_positions(exec_dir=None):
    """Bản ghi `positions` MỚI NHẤT mỗi account từ dnse_raw_*.jsonl mới nhất (lọc account §12 qua account_label).
    → ({account: {ticker: {qty, cost, market}}}, {account: ts}, file) — rỗng nếu không có."""
    exec_dir = exec_dir or EXEC_DIR
    files = sorted(glob.glob(os.path.join(exec_dir, "dnse_raw_*.jsonl")))
    if not files:
        return {}, {}, None
    f = files[-1]
    last = {}
    with open(f, encoding="utf-8") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("kind") == "positions" and r.get("account_label") in ACCOUNTS:
                last[r["account_label"]] = r
    pos, ts = {}, {}
    for a, r in last.items():
        pos[a] = {}
        for p in (r.get("payload") or {}).get("positions", []):
            if p.get("openQuantity"):
                pos[a][p["symbol"]] = {"qty": p["openQuantity"], "cost": p.get("costPrice"),
                                       "market": p.get("marketPrice")}
        ts[a] = r.get("ts")
    return pos, ts, os.path.basename(f)


def held_discretionary(lot_fn=None, fallback_tickers=None):
    """→ (held {ticker:{account:qty}}, nguồn (str), lỗi (list)). Ưu tiên sổ lô `portfolio_status.book_lot_snapshot`
    (chỉ-đọc broker); lỗi ⇒ nói rõ lý do thật và dùng fallback SUY BIẾN (mã trong thẻ/exit-rules ∩ dnse_raw) — nhãn 'degraded'."""
    errs, held = [], {}
    try:
        if lot_fn is None:
            sys.path.insert(0, HERE)
            import portfolio_status as P
            lot_fn = P.book_lot_snapshot
        for a in ACCOUNTS:
            lots, ok, reason, blocked = lot_fn(a, DISC_BOOK)
            if not ok:
                raise RuntimeError(f"{a}: {reason}")
            for t, v in lots.items():
                held.setdefault(t, {})[a] = v["qty"]
            for t, why in (blocked or {}).items():
                errs.append(f"{a} {t}: sổ lô unverified ({why}) — mã vẫn phải có thẻ")
                held.setdefault(t, {})[a] = None
        return held, "book_lot_snapshot (sổ lô, broker chỉ-đọc)", errs
    except Exception as e:  # noqa: BLE001 — nói thẳng lý do thật
        errs.append(f"book_lot_snapshot lỗi: {type(e).__name__}: {e}")
    pos, _, fname = raw_positions()
    names = set(fallback_tickers or [])
    try:
        names |= {p["ticker"] for p in read_json(EXIT_RULES).get("positions", [])}
    except Exception as e:  # noqa: BLE001
        errs.append(f"không đọc exit-rules: {type(e).__name__}: {e}")
    for a, d in pos.items():
        for t in names:
            if t in d:
                held.setdefault(t, {})[a] = d[t]["qty"]
    return held, f"degraded: dnse_raw {fname} ∩ (thẻ ∪ exit-rules) — KHÔNG biết book thật", errs
