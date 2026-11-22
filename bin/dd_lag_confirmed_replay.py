#!/usr/bin/env python3
"""dd_lag_confirmed_replay.py — CHỈ ĐỌC. Replay "lệnh MUA LAG chỉ qua cổng DD khi skeptic_final = CONFIRMED".

Đo: so với cổng hiện tại (trading_bot/plan.py::filter_lag_dd_zone_orders) luật D1 chặn THÊM bao nhiêu lệnh.
KHÔNG nối vào cổng, KHÔNG ghi plan/sổ. In bảng ra stdout (markdown).
CAVEAT: nhãn skeptic_final của entry mới nhất được BACKFILL 22/11 (xấp xỉ, không phải verdict gốc).

Dùng: dd_lag_confirmed_replay.py [--ledger F] [--plans-dir D] [--mike-root R] [--no-corp]
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
from collections import Counter
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
HERE = os.path.dirname(os.path.abspath(__file__))
WC = "/home/trido/thanhdt/WorkingClaude"
MIKE_CANON = WC + "/mike"
PLAN_RE = re.compile(r"plan_(?P<acct>[A-Za-z0-9]+)_(?P<d>\d{4}-\d{2}-\d{2})\.json$")


def load_watch(root):
    sys.path.insert(0, WC)
    sys.path.insert(0, os.path.join(root, "bin"))
    import dd_price_zone_watch as m
    return m


def gate_a(o, entries, asof_d, w, events, lock_root):
    """Bản sao điều kiện filter_lag_dd_zone_orders → None nếu QUA, chuỗi lý do nếu CHẶN."""
    px_c = [float(x) for x in (o.get("ref_price"), o.get("hard_no_chase_ceiling_vnd")) if x and float(x) > 0]
    px = min(px_c) if px_c else None
    e = entries.get((o.get("ticker") or "").upper())
    if e is None:
        return "chưa có DD trong sổ", None, px
    lm = w.lock_mismatch(e, lock_root)
    center, zh = e.get("center"), e.get("zone_high")
    cap = min(center, zh) if (center and zh) else center
    if lm:
        return "khoá md5 lệch", e, px
    try:
        exp, why = w.expiry_of(e, asof_d, None)
        if exp:
            return f"DD hết hạn ({why})", e, px
    except Exception as ex:  # noqa: BLE001
        return f"không kiểm được hạn ({type(ex).__name__})", e, px
    if events is None:
        return "không kiểm được corp-action (fail-closed)", e, px
    try:
        _n, blk = w.frame_check(e, events.get((o.get("ticker") or "").upper()), asof_d)
        if blk:
            return "sự kiện quyền sau DD", e, px
    except Exception as ex:  # noqa: BLE001
        return f"không kiểm được hệ giá ({type(ex).__name__})", e, px
    if not center or center <= 0:
        return "không có tâm hợp lệ", e, px
    if px is None:
        return "không có giá tham chiếu", e, px
    if px > cap:
        return f"giá {px:,.0f} > tâm/đỉnh vùng {cap:,.0f}", e, px
    return None, e, px


def rule_b(e):
    """Luật D1: CONFIRMED mới qua."""
    return (e or {}).get("skeptic_final") == "CONFIRMED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json"))
    ap.add_argument("--plans-dir", default=WC + "/data/trade_plans")
    ap.add_argument("--mike-root", default=os.path.dirname(HERE))
    ap.add_argument("--no-corp", action="store_true")
    a = ap.parse_args()
    w = load_watch(a.mike_root)
    with open(a.ledger, encoding="utf-8") as fh:
        ledger = json.load(fh)
    print(f"# replay — chạy {dt.datetime.now(_ICT):%Y-%m-%d %H:%M} ICT · sổ {a.ledger} ({len(ledger['entries'])} entry)")
    print("> CAVEAT: nhãn skeptic_final của entry mới nhất = BACKFILL 22/11 (xấp xỉ), không phải verdict gốc.\n")

    rows, plans_seen = [], []
    for f in sorted(glob.glob(os.path.join(a.plans_dir, "plan_*_*.json"))):
        m = PLAN_RE.search(f)
        if not m:
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                p = json.load(fh)
        except (OSError, ValueError):
            continue
        pdate = m.group("d")
        for kind in ("orders", "cancelled_orders"):
            for o in p.get(kind) or []:
                if (o.get("book") or "").upper() == "LAG" and (o.get("side") or "").lower() == "buy":
                    rows.append((pdate, m.group("acct"), kind, p.get("approved_by"), o, f))
        plans_seen.append(pdate)
    asof_cache, ev_cache = {}, {}
    out = []
    for pdate, acct, kind, appr, o, f in rows:
        asof_d = dt.date.fromisoformat(pdate)
        ent = asof_cache.setdefault(pdate, w.latest_entries(ledger, asof_d))
        t = (o.get("ticker") or "").upper()
        key = (pdate, t)
        if key not in ev_cache:
            if a.no_corp or t not in ent:
                ev_cache[key] = {}
            else:
                ev_cache[key] = w.corp_events([t], {t: ent[t]}, asof_d)
        why_a, e, px = gate_a(o, ent, asof_d, w, ev_cache[key], MIKE_CANON)
        a_pass = why_a is None
        b_pass = rule_b(e)
        out.append({"plan_date": pdate, "account": acct, "kind": kind, "approved_by": bool(appr),
                        "approved_by_txt": (str(appr)[:40] if appr else ""), "ticker": t, "qty": o.get("qty"), "px": px,
                        "sf": (e or {}).get("skeptic_final", "NO_DD"), "basis": (e or {}).get("skeptic_final_basis"),
                        "dd_date": (e or {}).get("dd_date"), "a_pass": a_pass, "why_a": why_a or "", "b_pass": b_pass,
                        "extra": a_pass and not b_pass, "status": ((e or {}).get("skeptic_status") or "")[:140]})
    print(f"## 1. Lệnh MUA LAG (orders + cancelled_orders): {len(out)} dòng / {len({(r['plan_date'], r['account'], r['ticker']) for r in out})} cặp (plan_date,account,ticker)\n")
    print("| plan_date | acct | list | approved | tk | qty | px | DD(dd_date) | skeptic_final | (a) cổng nay | (b) CONFIRMED | chặn THÊM |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in out:
        pxs = f"{r['px']:,.0f}" if r["px"] else "-"
        print(f"| {r['plan_date']} | {r['account']} | {r['kind']} | {'Y' if r['approved_by'] else 'N'} | {r['ticker']} | {r['qty']} | "
              f"{pxs} | {r['dd_date'] or '-'} | {r['sf']} | "
              f"{'qua' if r['a_pass'] else 'chặn: ' + r['why_a']} | {'qua' if r['b_pass'] else 'chặn'} | {'**CÓ**' if r['extra'] else ''} |")
    ex = [r for r in out if r["extra"]]
    pairs = {(r["plan_date"], r["account"], r["ticker"]) for r in out}
    xp = {(r["plan_date"], r["account"], r["ticker"]) for r in ex}
    print(f"\n**Chặn THÊM: {len(ex)} dòng lệnh / {len(xp)} cặp (plan,acct,mã) trên tổng {len(out)} dòng / {len(pairs)} cặp; "
          f"mã riêng biệt bị chặn thêm: {sorted({r['ticker'] for r in ex})}**")
    print(f"(a) qua: {sum(r['a_pass'] for r in out)} dòng · (b) qua: {sum(r['b_pass'] for r in out)} dòng")
    for r in ex:
        print(f"- {r['plan_date']} {r['account']} {r['ticker']} qty={r['qty']} sf={r['sf']} ({r['basis']}): {r['status']}")
    by_month = Counter(r["plan_date"][:7] for r in out)
    print(f"\nLệnh MUA LAG theo tháng (dòng): {dict(sorted(by_month.items()))}")
    d1020 = sorted({r["plan_date"] for r in out if r["plan_date"] >= "2026-10-01"})
    print(f"Ngày plan có lệnh MUA LAG từ 10/2026: {d1020}")
    print(f"Lệnh MUA LAG plan_date >= 2026-11-10: {sum(1 for r in out if r['plan_date'] >= '2026-11-10')} dòng")

    today = dt.date(2026, 11, 22)
    ent = w.latest_entries(ledger, today)
    print(f"\n## 2. Sổ hôm nay ({today}): {len(ent)} mã\n")
    print("| mã | dd_date | rev | skeptic_final | basis | path | ambiguous_backfill | tâm |")
    print("|---|---|---|---|---|---|---|---|")
    for t in sorted(ent):
        e = ent[t]
        print(f"| {t} | {e['dd_date']} | {e.get('rev', 1)} | {e.get('skeptic_final')} | {e.get('skeptic_final_basis')} | "
              f"{e.get('skeptic_verdict_path') or '-'} | {'Y' if e.get('skeptic_final_basis') == 'ambiguous_backfill' else 'N'} | {e.get('center')} |")
    c = Counter(e.get("skeptic_final") for e in ent.values())
    print(f"\nĐếm: {dict(c)}")
    ca = sorted(t for t, e in ent.items() if e.get('skeptic_final') == 'CONFIRMED' and e.get('skeptic_final_basis') == 'ambiguous_backfill')
    print(f"CONFIRMED mà basis=ambiguous_backfill: {ca}")
    print(f"basis=ambiguous_backfill (mọi nhãn): {sorted(t for t, e in ent.items() if e.get('skeptic_final_basis') == 'ambiguous_backfill')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
