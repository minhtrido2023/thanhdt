#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate + checker cho sleeve margin đơn mã discretionary (TV1/DGC-style fear-buy).

Chính sách: `kb/projects/discretionary-margin-policy-20260823.md` (RESYNC 2026-08-30,
`decided_by: user`). KHÁC `capit_margin_lever`/`apply_capit_lever`: đây KHÔNG wire vào
`plan.py`/`executor.py`/`trading_rules.json` — quy trình arm là hành động TAY của user (qua
subcommand `arm` ở đây), checker exit chạy cron đọc-only, không có auto-sell.

Rào chắn cưỡng chế (mọi %NAV = EXPOSURE, không phải vốn tự có — §"Rào chắn rủi ro" chính sách):
  - per-name  : exposure ≤ 5% NAV
  - sleeve tổng: Σ exposure các case ĐANG active ≤ 10% NAV (user 08-30; trigger mở 15%: ≥3 case
    marginable đồng thời THẬT → escalate user, không tự động)
  - đòn bẩy   : f ≤ 1,3 (hard-cap, đồng quy ước capit_margin_lever — KHÔNG dùng broker-max 2,0)
  - thanh khoản: exposure ≤ 10% ADV-3-tháng (đọc `data/bq_cache/ticker/<year>.parquet`)
  - marginability: PHẢI có xác nhận Mafee (chuỗi thật, không phải placeholder) trước khi arm
FAIL-SAFE: thiếu bất kỳ dữ liệu nào ở trên (NAV, ADV, marginability) → CHẶN arm, không đoán.

DÙNG:
    python3 mike/bin/discretionary_margin_gate.py arm --ticker TV1 --arm-price 20640 \
        --shares 2000 --f 1.3 \
        --marginability-confirmed-by "Mafee — loan_packages API symbol=TV1, job Mafee_..." \
        --fundamental-skeptic-confirmed --rating-8l 2 \
        --approved-by "user (John) — Discord discretionary_stocks 23:10" --decided-by user

    python3 mike/bin/discretionary_margin_gate.py check-exits      # cron hằng ngày
    python3 mike/bin/discretionary_margin_gate.py list
    python3 mike/bin/discretionary_margin_gate.py exit --ticker TV1 --reason "chốt lãi thủ công"
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIKE_ROOT = os.path.join(WC_ROOT, "mike")
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(MIKE_ROOT, "bin"))

ICT = ZoneInfo("Asia/Ho_Chi_Minh")                       # §16: neo múi giờ tường minh

ARMS_PATH = os.path.join(WC_ROOT, "data", "discretionary_margin_arms.json")
NAV_HISTORY = os.path.join(WC_ROOT, "data", "execution_logs", "nav_history_{account}.csv")
BQ_CACHE_TICKER_DIR = os.path.join(WC_ROOT, "data", "bq_cache", "ticker")

ONLY_ACCOUNT = "SpaceX"           # chính sách chỉ áp dụng account có margin (ZaloPay cash-only)
PER_NAME_CAP_PCT = 0.05            # NAV exposure — user 08-29, đổi từ 3%
SLEEVE_CAP_PCT = 0.10                # NAV exposure tổng — user 08-30 11:52 ICT, đổi từ 5%.
                                       # Trigger mở lại 15%: ≥3 case marginable đồng thời THẬT
                                       # (Mafee xác nhận, không phải giả định) → escalate
                                       # Mike/user xem xét, KHÔNG tự động nâng lên 15%.
MAX_F = 1.3                          # hard-cap đòn bẩy, đồng quy ước capit_margin_lever
ADV_CAP_PCT = 0.10                    # exposure <= 10% ADV-3-thang
ADV_WINDOW_SESSIONS = 63               # ~3 tháng phiên giao dịch
ADV_STALE_DAYS = 10                     # ADV asof cũ hơn 10 ngày lịch -> fail-safe block
EXIT_DD_PCT = -0.20                       # kỷ luật thoát tự áp, từ giá arm

from trading_bot.plan import APPROVAL_PLACEHOLDERS as PLACEHOLDER  # noqa: E402


def _bus(kind, topic, payload, trace_id=None):
    """Ghi bus — trả True nếu ghi được (xem lý do kiểm rc trong approve_margin_day.py)."""
    cmd = [os.path.join(MIKE_ROOT, "bin", "append_event.sh"), "Taylor", kind, topic,
           json.dumps(payload, ensure_ascii=False)]
    if trace_id:
        cmd.append(trace_id)
    try:
        r = subprocess.run(cmd, check=False, capture_output=True, timeout=60)
        if r.returncode != 0:
            print(f"⚠ append_event.sh trả rc={r.returncode}: "
                  f"{(r.stderr or b'').decode('utf-8', 'replace').strip()[:300]}")
            return False
        return True
    except Exception as ex:
        print(f"⚠ không ghi được bus event ({type(ex).__name__}: {ex})")
        return False


def _notify(msg):
    try:
        r = subprocess.run([os.path.join(MIKE_ROOT, "bin", "notify_thread.sh"), msg,
                            "discretionary_stocks"], check=False, capture_output=True, timeout=60)
        if r.returncode != 0:
            print(f"⚠ notify_thread.sh trả rc={r.returncode}: "
                  f"{(r.stderr or b'').decode('utf-8', 'replace').strip()[:300]}")
            return False
        return True
    except Exception as ex:
        print(f"⚠ không đẩy được Discord ({type(ex).__name__}: {ex})")
        return False


# ---------------------------------------------------------------- arms store (atomic) ----------

def load_arms():
    if not os.path.exists(ARMS_PATH):
        return []
    with open(ARMS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_arms(arms):
    os.makedirs(os.path.dirname(ARMS_PATH), exist_ok=True)
    tmp = ARMS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:          # §5: ghi nguyên tử, kill giữa chừng
        json.dump(arms, f, ensure_ascii=False, indent=2)  # không được để lại JSON cụt
    os.replace(tmp, ARMS_PATH)


def active_arms(arms):
    return [a for a in arms if not a.get("exited")]


# ---------------------------------------------------------------- data readers (fail-safe) ------

def latest_nav(account):
    """Trả (nav_vnd, date) từ nav_history_{account}.csv, hoặc (None, lý_do) nếu thiếu."""
    path = NAV_HISTORY.format(account=account)
    if not os.path.exists(path):
        return None, f"không có {path}"
    import csv
    last = None
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("nav"):
                last = row
    if last is None:
        return None, f"{path} không có dòng nào có cột nav"
    try:
        return float(last["nav"]), last["date"]
    except (TypeError, ValueError):
        return None, f"{path} dòng cuối có nav không parse được: {last.get('nav')!r}"


def adv_3m(ticker):
    """ADV-3-tháng thật (mean Trading_Value, ~63 phiên gần nhất) từ bq_cache local.

    Trả (adv_vnd, asof_date, None) khi OK, hoặc (None, None, lý_do) khi fail-safe block —
    KHÔNG đoán ADV khi thiếu dữ liệu (coding_guidelines §29: không hardcode/đoán nguyên nhân,
    ở đây là không đoán SỐ khi thiếu bằng chứng).
    """
    today = dt.datetime.now(ICT).date()
    years = sorted({today.year, today.year - 1})
    frames = []
    try:
        import pandas as pd
    except ImportError:
        return None, None, "thiếu pandas — không đọc được bq_cache"
    for y in years:
        path = os.path.join(BQ_CACHE_TICKER_DIR, f"{y}.parquet")
        if not os.path.exists(path):
            continue
        df = pd.read_parquet(path, columns=["time", "ticker", "Trading_Value"])
        frames.append(df[df["ticker"] == ticker])
    if not frames:
        return None, None, f"không tìm thấy {BQ_CACHE_TICKER_DIR}/<year>.parquet cho {years}"
    import pandas as pd
    df = pd.concat(frames, ignore_index=True)
    if df.empty:
        return None, None, f"bq_cache không có dòng nào cho ticker={ticker}"
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")
    asof = df["time"].max().date()
    if (today - asof).days > ADV_STALE_DAYS:
        return None, None, (f"ADV cache cho {ticker} cũ hơn {ADV_STALE_DAYS} ngày "
                             f"(asof={asof}, hôm nay={today}) — fail-safe, không đoán ADV")
    window = df.tail(ADV_WINDOW_SESSIONS)
    adv = float(window["Trading_Value"].mean())
    if not (adv > 0):
        return None, None, f"ADV tính được cho {ticker} không dương ({adv!r})"
    return adv, asof.isoformat(), None


def current_price(ticker):
    """Giá hiện tại qua DNSE (§6 CLAUDE.md — same-day PHẢI DNSE, không BQ). Tái dùng
    `verify_account_snapshot.dnse_close_prices` (đã vá 2 cửa sổ tiền-phiên/giữa-phiên +
    UPCOM basicPrice), không tự viết lại logic giá phiên hôm nay.
    """
    from verify_account_snapshot import dnse_close_prices
    prices, sources, substituted = dnse_close_prices([ticker], with_source=True)
    if ticker not in prices:
        return None, None, f"DNSE không trả được giá cho {ticker}"
    return prices[ticker], sources.get(ticker), None


# ---------------------------------------------------------------- arm ---------------------------

def cmd_arm(args):
    if args.account != ONLY_ACCOUNT:
        print(f"❌ account {args.account!r} ngoài phạm vi chính sách (chỉ {ONLY_ACCOUNT} có "
              f"margin) — KHÔNG arm.", file=sys.stderr)
        return 2

    who_confirm = (args.marginability_confirmed_by or "").strip()
    if who_confirm.lower() in PLACEHOLDER:
        print(f"❌ --marginability-confirmed-by {args.marginability_confirmed_by!r} không phải "
              f"một xác nhận thật (chuỗi giữ chỗ/tên tác nhân tự động). Cần Mafee xác nhận "
              f"marginable TỪNG CASE trước khi arm (chính sách §Vận hành).", file=sys.stderr)
        return 2

    who_approve = (args.approved_by or "").strip()
    if who_approve.lower() in PLACEHOLDER:
        print(f"❌ --approved-by {args.approved_by!r} không phải một người duyệt thật.",
              file=sys.stderr)
        return 2

    if not args.fundamental_skeptic_confirmed:
        print("❌ --fundamental-skeptic-confirmed bắt buộc (Cổng vào mục 2 — không dùng verdict "
              "sơ bộ một mình).", file=sys.stderr)
        return 2

    if args.rating_8l > 2:
        print(f"❌ rating 8L={args.rating_8l} > 2 — Cổng vào mục 3 yêu cầu ≤2 xác nhận LẠI SAU "
              f"sự kiện.", file=sys.stderr)
        return 2

    if args.f > MAX_F + 1e-9:
        print(f"❌ f={args.f} vượt hard-cap {MAX_F} (đồng quy ước capit_margin_lever, KHÔNG dùng "
              f"broker-max 2,0).", file=sys.stderr)
        return 2

    exposure_vnd = args.exposure_vnd if args.exposure_vnd is not None else args.shares * args.arm_price
    if not (exposure_vnd > 0):
        print("❌ exposure phải > 0 (truyền --shares + --arm-price, hoặc --exposure-vnd).",
              file=sys.stderr)
        return 2

    nav, nav_date = latest_nav(args.account)
    if nav is None:
        print(f"❌ FAIL-SAFE: không đọc được NAV thật ({nav_date}) — KHÔNG arm khi thiếu dữ "
              f"liệu.", file=sys.stderr)
        return 3

    per_name_cap_vnd = nav * PER_NAME_CAP_PCT
    if exposure_vnd > per_name_cap_vnd:
        print(f"❌ exposure {exposure_vnd:,.0f} VND > trần per-name {PER_NAME_CAP_PCT:.0%} NAV "
              f"({per_name_cap_vnd:,.0f} VND, NAV={nav:,.0f} @ {nav_date}).", file=sys.stderr)
        return 2

    arms = load_arms()
    existing_sleeve = sum(a["exposure_vnd"] for a in active_arms(arms) if a["ticker"] != args.ticker)
    sleeve_total = existing_sleeve + exposure_vnd
    sleeve_cap_vnd = nav * SLEEVE_CAP_PCT
    if sleeve_total > sleeve_cap_vnd:
        print(f"❌ sleeve tổng sẽ là {sleeve_total:,.0f} VND > trần {SLEEVE_CAP_PCT:.0%} NAV "
              f"({sleeve_cap_vnd:,.0f} VND) — case khác đang active: "
              f"{existing_sleeve:,.0f} VND.", file=sys.stderr)
        return 2

    adv, adv_asof, adv_err = adv_3m(args.ticker)
    if adv_err:
        print(f"❌ FAIL-SAFE: {adv_err} — KHÔNG arm khi thiếu ADV.", file=sys.stderr)
        return 3
    adv_cap_vnd = adv * ADV_CAP_PCT
    if exposure_vnd > adv_cap_vnd:
        print(f"❌ exposure {exposure_vnd:,.0f} VND > trần {ADV_CAP_PCT:.0%} ADV-3-tháng "
              f"({adv_cap_vnd:,.0f} VND, ADV={adv:,.0f}/ngày asof={adv_asof}).", file=sys.stderr)
        return 2

    rec = {
        "ticker": args.ticker,
        "account": args.account,
        "arm_price": args.arm_price,
        "shares": args.shares,
        "exposure_vnd": round(exposure_vnd),
        "f": args.f,
        "nav_at_arm": round(nav),
        "nav_at_arm_date": nav_date,
        "adv_3m_vnd": round(adv),
        "adv_3m_asof": adv_asof,
        "pct_adv": round(exposure_vnd / adv, 4),
        "pct_nav_exposure": round(exposure_vnd / nav, 4),
        "marginability_confirmed_by": who_confirm,
        "fundamental_skeptic_confirmed": True,
        "rating_8l": args.rating_8l,
        "approved_by": who_approve,
        "decided_by": args.decided_by,
        "armed_at": dt.datetime.now(ICT).isoformat(timespec="seconds"),
        "exited": False,
        "exit_alerts": [],
        "written_by": "mike/bin/discretionary_margin_gate.py",
    }

    if args.dry_run:
        print(f"[dry-run] sẽ arm:\n{json.dumps(rec, ensure_ascii=False, indent=2)}")
        return 0

    arms.append(rec)
    save_arms(arms)
    print(f"✅ ĐÃ ARM {args.ticker} — exposure {exposure_vnd:,.0f} VND "
          f"({rec['pct_nav_exposure']:.2%} NAV, {rec['pct_adv']:.2%} ADV), f={args.f}")

    msg = (f"🔓 **ARM MARGIN DISCRETIONARY** — {args.ticker} ({args.account})\n"
           f"• Giá arm: {args.arm_price:,.0f} · Exposure: {exposure_vnd/1e6:,.1f}tr "
           f"({rec['pct_nav_exposure']:.1%} NAV) · f={args.f}\n"
           f"• %ADV-3m: {rec['pct_adv']:.1%} (ADV={adv/1e6:,.1f}tr/ngày asof {adv_asof})\n"
           f"• Sleeve tổng sau case này: {sleeve_total/1e6:,.1f}tr / trần "
           f"{sleeve_cap_vnd/1e6:,.1f}tr\n"
           f"• Kỷ luật thoát: de-lever bắt buộc tại {EXIT_DD_PCT:.0%} từ giá arm (tự áp, "
           f"checker cron alert khi chạm) HOẶC rating 8L tụt >2.\n"
           f"• Marginability: {who_confirm}\n"
           f"• Duyệt: {who_approve} (decided_by={args.decided_by})")
    ok_b = _bus("decision", f"discretionary-margin-arm-{args.ticker}-{args.account}", rec)
    ok_n = _notify(msg)
    if not (ok_b and ok_n):
        print("⚠ CẢNH BÁO: bản ghi arm đã ghi nhưng dấu vết bus/Discord không đầy đủ — báo lại "
              "kênh discretionary_stocks bằng tay.")
        return 3
    return 0


# ---------------------------------------------------------------- check-exits -------------------

def cmd_check_exits(args):
    arms = load_arms()
    live = active_arms(arms)
    if not live:
        print("Không có case discretionary margin nào đang active.")
        return 0

    changed = False
    breaches = []
    errors = []
    for a in live:
        px, src, err = current_price(a["ticker"])
        if err:
            errors.append(f"{a['ticker']}: {err}")
            continue
        drawdown = px / a["arm_price"] - 1.0
        a["last_checked"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
        a["last_price"] = px
        a["last_price_source"] = src
        a["last_drawdown"] = round(drawdown, 4)
        changed = True
        if drawdown <= EXIT_DD_PCT + 1e-9:      # epsilon: tránh lệch làm tròn nhị phân bỏ sót đúng ngưỡng
            a["exit_alerts"].append({"date": a["last_checked"], "price": px,
                                      "drawdown": round(drawdown, 4)})
            breaches.append((a["ticker"], px, drawdown))

    if changed:
        save_arms(arms)

    for ticker, err in [(None, e) for e in errors]:
        print(f"⚠ {err}")

    if breaches:
        for ticker, px, drawdown in breaches:
            msg = (f"🚨 **KỶ LUẬT THOÁT −20% CHẠM** — {ticker}: giá hiện tại {px:,.0f} vs giá arm "
                   f"→ drawdown {drawdown:.1%} ≤ {EXIT_DD_PCT:.0%}. Chính sách yêu cầu de-lever "
                   f"BẮT BUỘC (`discretionary-margin-policy-20260823.md` §Rào chắn rủi ro) — đây "
                   f"là CẢNH BÁO, hành động thoát vẫn cần người quyết.")
            print(msg)
            _bus("error", f"discretionary-margin-exit-breach-{ticker}",
                 {"ticker": ticker, "price": px, "drawdown": drawdown})
            _notify(msg)
    else:
        print(f"OK — {len(live)} case active, không case nào chạm {EXIT_DD_PCT:.0%}.")
    return 1 if errors else 0


# ---------------------------------------------------------------- exit / list -------------------

def cmd_exit(args):
    arms = load_arms()
    found = False
    for a in arms:
        if a["ticker"] == args.ticker and not a.get("exited"):
            a["exited"] = True
            a["exited_at"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
            a["exit_reason"] = args.reason
            found = True
    if not found:
        print(f"⚠ không có case active nào cho ticker={args.ticker}", file=sys.stderr)
        return 1
    save_arms(arms)
    msg = f"✅ ĐÃ EXIT {args.ticker} — lý do: {args.reason}"
    print(msg)
    _bus("decision", f"discretionary-margin-exit-{args.ticker}",
         {"ticker": args.ticker, "reason": args.reason})
    _notify(msg)
    return 0


def cmd_list(args):
    arms = load_arms()
    live = active_arms(arms)
    if not live:
        print("Không có case active.")
        return 0
    for a in live:
        dd = a.get("last_drawdown")
        dd_str = f"{dd:.1%}" if dd is not None else "chưa check"
        print(f"{a['ticker']:6s} exposure={a['exposure_vnd']:>14,.0f} VND "
              f"({a['pct_nav_exposure']:.1%} NAV) f={a['f']} arm_price={a['arm_price']:,.0f} "
              f"drawdown={dd_str}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_arm = sub.add_parser("arm", help="arm một case margin discretionary mới")
    p_arm.add_argument("--account", default=ONLY_ACCOUNT)
    p_arm.add_argument("--ticker", required=True)
    p_arm.add_argument("--arm-price", type=float, required=True)
    p_arm.add_argument("--shares", type=float, default=0)
    p_arm.add_argument("--exposure-vnd", type=float, default=None,
                        help="override thay vì shares*arm_price")
    p_arm.add_argument("--f", type=float, default=MAX_F)
    p_arm.add_argument("--marginability-confirmed-by", required=True)
    p_arm.add_argument("--fundamental-skeptic-confirmed", action="store_true")
    p_arm.add_argument("--rating-8l", type=int, required=True)
    p_arm.add_argument("--approved-by", required=True)
    p_arm.add_argument("--decided-by", choices=["user", "agent"], default="agent")
    p_arm.add_argument("--dry-run", action="store_true")
    p_arm.set_defaults(func=cmd_arm)

    p_check = sub.add_parser("check-exits", help="checker hằng ngày: giá DNSE so giá arm")
    p_check.set_defaults(func=cmd_check_exits)

    p_exit = sub.add_parser("exit", help="đóng một case (thoát margin)")
    p_exit.add_argument("--ticker", required=True)
    p_exit.add_argument("--reason", required=True)
    p_exit.set_defaults(func=cmd_exit)

    p_list = sub.add_parser("list", help="liệt kê case đang active")
    p_list.set_defaults(func=cmd_list)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
