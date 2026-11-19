#!/usr/bin/env python3
"""fz_signal_ledger — SỔ TÍN HIỆU PAPER append-only cho FZ-001 / FZ-002 / C-CEIL / C-NFLOOR.

Chương trình `intraday_fz_signal_ledger` (registry kb/paper_programs_registry.json).
behavior_contract = LOG_ONLY_NO_BROKER_PATH: script này KHÔNG gọi broker, KHÔNG sinh plan/lệnh,
KHÔNG ghi file nào ngoài sổ + file khoá. Không cron, không nối live (xem README).

Đơn vị theo dõi = CỤM ngày signal (gap <= 5 phiên giữa 2 ngày signal liên tiếp của CÙNG setup),
KHÔNG phải book/vị thế. Sổ lưu từng dòng (setup, ngày, mã); cụm dựng lúc đọc (--summary), vì
cụm có thể nối thêm khi có signal mới.

Dùng:
  python3 bin/fz_signal_ledger.py ingest <deals_<setup>.csv> [--ledger PATH] [--forward-from YYYY-MM-DD]
  python3 bin/fz_signal_ledger.py summary [--ledger PATH] [--asof YYYY-MM-DD]

Phí/thuế: THẬT 0,097%/chiều + thuế bán 0,1% (CLAUDE.md §6 / dnse_fee_rates). File deal_export
dùng phí cũ 0,03%/chiều ⇒ net_ret_total của export KHÔNG dùng trực tiếp; dựng lại từ giá điều
chỉnh (entry_px/f_entry, exit_px/f_exit). Rổ cùng ngày (market_drift_same_day) cùng nhân hệ số
phí ⇒ excess tính lại đúng, không cộng xấp xỉ.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import io
import math
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
WC_ROOT = "/home/trido/thanhdt/WorkingClaude"
MIKE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LEDGER = os.path.join(MIKE_ROOT, "data", "fz_signal_ledger.csv")

TRACKED = {"FZ-001", "FZ-002", "C-CEIL", "C-NFLOOR"}
# Mẫu "mới" = sau cửa sổ holdout của nhóm nghiên cứu (holdout kết thúc 2026-11-03).
FORWARD_FROM_DEFAULT = "2026-11-04"
CLUSTER_GAP_SESSIONS = 5
STOP_EARLY_N = 10      # luật khai trước: sau 10 cụm mới, mean excess <= 0 => BÁO USER
GO_MIN_CLUSTERS = 20   # chỉ XÉT GO khi >= 20 cụm mới (+ DSR + skeptic + user — ngoài script)

FEE_REAL = 0.00097     # mỗi chiều
TAX_SELL = 0.001
FEE_EXPORT = 0.0003    # phí trong deal_export (để đối chiếu / quy đổi rổ)

REQUIRED_IN = [
    "setup", "signal_day", "symbol", "status", "entry_ts", "exit_ts", "exit_reason",
    "hold_sessions", "entry_px", "exit_px", "f_entry", "f_exit", "net_ret_total",
    "market_drift_same_day", "in_stats", "signal_id",
]
NUMERIC_IN = ["entry_px", "exit_px", "f_entry", "f_exit", "net_ret_total", "market_drift_same_day"]
LEDGER_COLS = [
    "signal_id", "setup", "signal_day", "symbol", "entry_date", "exit_date", "exit_reason",
    "hold_sessions", "gross_ret_adj", "net_ret_total", "basket_ret", "excess_vs_basket",
    "dep1m_rate_pct", "dep_prorata", "excess_vs_dep", "fee_side", "tax_sell",
    "export_net_ret_total", "ingested_at", "source_file", "source_md5",
]
# Cột bất biến dùng phát hiện xung đột khi cùng signal_id mà giá trị khác.
CONFLICT_COLS = ["setup", "signal_day", "symbol", "entry_date", "exit_date", "net_ret_total"]


class LedgerError(Exception):
    """Fail-closed: không ghi gì."""


# ---------------------------------------------------------------- tính toán
def _k(fee: float, tax: float) -> float:
    return (1.0 - fee - tax) / (1.0 + fee)


def net_ret(entry_px, f_entry, exit_px, f_exit, fee, tax) -> float:
    ratio = (exit_px / f_exit) / (entry_px / f_entry)
    return ratio * _k(fee, tax) - 1.0


def fee_adjust_basket(drift_export: float) -> float:
    """Rổ trong export chịu hệ số phí cũ; quy về phí thật (nhân hệ số, không cộng)."""
    return (1.0 + drift_export) * _k(FEE_REAL, TAX_SELL) / _k(FEE_EXPORT, TAX_SELL) - 1.0


def _default_rate_fn(d: date) -> float:
    if WC_ROOT not in sys.path:
        sys.path.insert(0, WC_ROOT)
    import idle_rate_proxy  # noqa: PLC0415
    return float(idle_rate_proxy.r_idle(d, tier="dep1m"))


def _parse_date(s: str) -> date:
    return datetime.fromisoformat(str(s).strip()).date()


def _holiday_fn():
    try:
        if WC_ROOT not in sys.path:
            sys.path.insert(0, WC_ROOT)
        from trading_bot.vn_market import is_holiday  # noqa: PLC0415
        return is_holiday
    except Exception:  # noqa: BLE001
        return None


def sessions_between(a: date, b: date, is_holiday=None) -> int:
    """Số phiên giao dịch trong (a, b]. Thiếu lịch nghỉ lễ => chỉ loại T7/CN (ước lượng cao)."""
    if b <= a:
        return 0
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5 and not (is_holiday and is_holiday(d)):
            n += 1
    return n


# ---------------------------------------------------------------- IO
def _read_ledger(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames != LEDGER_COLS:
            raise LedgerError(f"header sổ lệch khuôn: {r.fieldnames}")
        return list(r)


def _serialize(rows: list[dict]) -> str:
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=LEDGER_COLS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def _atomic_write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _fmt(x: float) -> str:
    return f"{x:.8f}"


# ---------------------------------------------------------------- ingest
def ingest(src: str, ledger: str = DEFAULT_LEDGER, forward_from: str = FORWARD_FROM_DEFAULT,
           rate_fn=None, now: datetime | None = None) -> dict:
    rate_fn = rate_fn or _default_rate_fn
    now = now or datetime.now(ICT)
    fwd = _parse_date(forward_from)
    with open(src, "rb") as fb:
        raw = fb.read()
    md5 = hashlib.md5(raw).hexdigest()
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    missing = [c for c in REQUIRED_IN if c not in (rdr.fieldnames or [])]
    if missing:
        raise LedgerError(f"thiếu cột bắt buộc {missing} — fail-closed, không ghi gì")

    seen: set[str] = set()
    new_rows: list[dict] = []
    stats = {"read": 0, "skip_other_setup": 0, "skip_not_closed": 0, "skip_overlap": 0,
             "skip_before_forward": 0}
    for i, r in enumerate(rdr, start=2):
        stats["read"] += 1
        sid = (r["signal_id"] or "").strip()
        if not sid:
            raise LedgerError(f"dòng {i}: signal_id rỗng")
        if sid in seen:
            raise LedgerError(f"dòng {i}: signal_id trùng TRONG file: {sid}")
        seen.add(sid)
        setup = (r["setup"] or "").strip().upper()
        if setup not in TRACKED:
            stats["skip_other_setup"] += 1
            continue
        if (r["status"] or "").strip() != "closed":
            stats["skip_not_closed"] += 1
            continue
        if str(r["in_stats"]).strip() != "1":
            stats["skip_overlap"] += 1
            continue
        sday = _parse_date(r["signal_day"])
        if sday < fwd:
            stats["skip_before_forward"] += 1
            continue
        try:
            v = {c: float(r[c]) for c in NUMERIC_IN}
        except (TypeError, ValueError) as e:
            raise LedgerError(f"dòng {i} ({sid}): số không đọc được: {e}") from e
        if any(not math.isfinite(x) for x in v.values()) or v["entry_px"] <= 0 or v["exit_px"] <= 0 \
                or v["f_entry"] <= 0 or v["f_exit"] <= 0:
            raise LedgerError(f"dòng {i} ({sid}): giá/hệ số không hợp lệ (NaN/inf/<=0)")
        old = net_ret(v["entry_px"], v["f_entry"], v["exit_px"], v["f_exit"], FEE_EXPORT, TAX_SELL)
        if abs(old - v["net_ret_total"]) > 1e-5:
            raise LedgerError(
                f"dòng {i} ({sid}): dựng lại net_ret_total (phí export) = {old:.7f} ≠ file "
                f"{v['net_ret_total']:.7f} — định dạng/giả định phí đổi, dừng")
        net = net_ret(v["entry_px"], v["f_entry"], v["exit_px"], v["f_exit"], FEE_REAL, TAX_SELL)
        gross = (v["exit_px"] / v["f_exit"]) / (v["entry_px"] / v["f_entry"]) - 1.0
        basket = fee_adjust_basket(v["market_drift_same_day"])
        ed, xd = _parse_date(r["entry_ts"]), _parse_date(r["exit_ts"])
        rate = rate_fn(ed)
        if not math.isfinite(rate):
            raise LedgerError(f"dòng {i} ({sid}): lãi dep1m không hợp lệ")
        dep = rate / 100.0 * (xd - ed).days / 365.0
        new_rows.append({
            "signal_id": sid, "setup": setup, "signal_day": sday.isoformat(),
            "symbol": r["symbol"].strip(), "entry_date": ed.isoformat(), "exit_date": xd.isoformat(),
            "exit_reason": r["exit_reason"].strip(), "hold_sessions": str(r["hold_sessions"]).strip(),
            "gross_ret_adj": _fmt(gross), "net_ret_total": _fmt(net), "basket_ret": _fmt(basket),
            "excess_vs_basket": _fmt(net - basket), "dep1m_rate_pct": f"{rate:.4f}",
            "dep_prorata": _fmt(dep), "excess_vs_dep": _fmt(net - dep),
            "fee_side": str(FEE_REAL), "tax_sell": str(TAX_SELL),
            "export_net_ret_total": _fmt(v["net_ret_total"]),
            "ingested_at": now.isoformat(timespec="seconds"),
            "source_file": os.path.basename(src), "source_md5": md5,
        })

    lock_path = ledger + ".lock"
    os.makedirs(os.path.dirname(ledger) or ".", exist_ok=True)
    with open(lock_path, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        existing = _read_ledger(ledger)
        by_id = {e["signal_id"]: e for e in existing}
        to_add = []
        dup = 0
        for n in new_rows:
            e = by_id.get(n["signal_id"])
            if e is None:
                to_add.append(n)
                continue
            diff = [c for c in CONFLICT_COLS if e[c] != n[c]]
            # net_ret_total so theo số, không theo chuỗi
            if "net_ret_total" in diff and abs(float(e["net_ret_total"]) - float(n["net_ret_total"])) < 1e-8:
                diff.remove("net_ret_total")
            if diff:
                raise LedgerError(f"{n['signal_id']}: đã có trong sổ nhưng KHÁC ở {diff} — "
                                  "sổ append-only, không ghi đè; điều tra thủ công")
            dup += 1
        if to_add:
            old_text = open(ledger, encoding="utf-8", newline="").read() if os.path.exists(ledger) else ""
            new_text = _serialize(existing + to_add)
            if old_text and not new_text.startswith(old_text):
                raise LedgerError("sổ cũ không còn là tiền tố của bản mới (định dạng đổi?) — dừng")
            _atomic_write(ledger, new_text)
    stats.update({"added": len(to_add), "duplicate_skipped": dup, "ledger_rows": len(existing) + len(to_add)})
    return stats


# ---------------------------------------------------------------- summary
def build_clusters(rows: list[dict], is_holiday=None) -> dict[str, list[list[dict]]]:
    out: dict[str, list[list[dict]]] = {}
    by_setup: dict[str, list[dict]] = {}
    for r in rows:
        by_setup.setdefault(r["setup"], []).append(r)
    for s, rs in by_setup.items():
        rs = sorted(rs, key=lambda r: (r["signal_day"], r["symbol"]))
        clusters: list[list[dict]] = []
        last: date | None = None
        for r in rs:
            d = _parse_date(r["signal_day"])
            if last is None or sessions_between(last, d, is_holiday) > CLUSTER_GAP_SESSIONS:
                clusters.append([])
            clusters[-1].append(r)
            last = d
        out[s] = clusters
    return out


def summarize(ledger: str = DEFAULT_LEDGER, asof: date | None = None, is_holiday=None) -> list[dict]:
    asof = asof or datetime.now(ICT).date()
    rows = _read_ledger(ledger)
    res = []
    for s, clusters in sorted(build_clusters(rows, is_holiday).items()):
        # cụm "đóng" = signal cuối cách asof > 5 phiên (không còn nối thêm được)
        closed = [c for c in clusters
                  if sessions_between(_parse_date(c[-1]["signal_day"]), asof, is_holiday) > CLUSTER_GAP_SESSIONS]
        eb = [sum(float(r["excess_vs_basket"]) for r in c) / len(c) for c in closed]
        ed = [sum(float(r["excess_vs_dep"]) for r in c) / len(c) for c in closed]
        n = len(closed)
        first = eb[:STOP_EARLY_N]
        stop = n >= STOP_EARLY_N and sum(first) / STOP_EARLY_N <= 0
        res.append({
            "setup": s, "rows": sum(len(c) for c in clusters), "clusters_total": len(clusters),
            "clusters_closed": n,
            "mean_excess_basket": (sum(eb) / n) if n else None,
            "mean_excess_dep": (sum(ed) / n) if n else None,
            "stop_early": stop,
            "go_eligible_n": n >= GO_MIN_CLUSTERS,
        })
    return res


def _print_summary(res: list[dict], holiday_ok: bool) -> None:
    print("setup | rows | clusters(closed/total) | mean excess vs basket | vs dep1m | flags")
    if not res:
        print("(sổ rỗng — chưa có signal mới nào được ingest)")
    for r in res:
        f = lambda x: "n/a" if x is None else f"{x*100:+.2f}%"  # noqa: E731
        flags = []
        if r["stop_early"]:
            flags.append("STOP_EARLY: sau 10 cụm mới mean excess<=0 — BÁO USER (không tự tắt)")
        flags.append(f"go_eligible_N={'yes' if r['go_eligible_n'] else 'no'}(cần >=20 cụm + DSR(T=cụm)>=0,95 + quant-skeptic + user)")
        print(f"{r['setup']} | {r['rows']} | {r['clusters_closed']}/{r['clusters_total']} | "
              f"{f(r['mean_excess_basket'])} | {f(r['mean_excess_dep'])} | {'; '.join(flags)}")
    if not holiday_ok:
        print("caveat: không nạp được lịch nghỉ lễ — số phiên chỉ loại T7/CN (cụm có thể bị tách/gộp sai nhẹ)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ingest")
    a.add_argument("deals_csv")
    a.add_argument("--ledger", default=DEFAULT_LEDGER)
    a.add_argument("--forward-from", default=FORWARD_FROM_DEFAULT)
    s = sub.add_parser("summary")
    s.add_argument("--ledger", default=DEFAULT_LEDGER)
    s.add_argument("--asof", default=None)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "ingest":
            print(ingest(args.deals_csv, args.ledger, args.forward_from))
        else:
            hol = _holiday_fn()
            asof = _parse_date(args.asof) if args.asof else None
            _print_summary(summarize(args.ledger, asof, hol), hol is not None)
    except LedgerError as e:
        print(f"FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
