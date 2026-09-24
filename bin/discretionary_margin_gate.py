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
import math
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(__file__)
MIKE_ROOT = os.path.join(WC_ROOT, "mike")   # dùng để gọi append_event.sh/notify_thread.sh CANONICAL
                                             # (subprocess, không phải Python import) — KHÔNG
                                             # push vào sys.path: chèn `MIKE_ROOT/bin` sẽ đặt
                                             # `mike/bin` CANONICAL trước chính thư mục file này
                                             # trong sys.path, khiến `import daily_nav_snapshot`/
                                             # `corp_actions` từ TRONG worktree lại nạp bản
                                             # CANONICAL đã landed thay vì bản đang sửa dở trong
                                             # worktree (bug cùng lớp với compute_active_nav
                                             # 833abcc5 — phát hiện khi test 22a/§29 vòng 6 dùng
                                             # hàm thật không stub, xem selfcheck).
sys.path.insert(0, WC_ROOT)

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


def corp_action_frame_multiplier(ticker, arm_date):
    """factor — hệ số quy đổi `arm_price` về CÙNG HỆ QUY CHIẾU với `px` (giá hiện tại, DNSE G1)
    trước khi tính drawdown. `arm_date` = ngày ARM (YYYY-MM-DD, hệ giá TRƯỚC mọi sự kiện).

    CHỈ phủ sự kiện ĐỔI KHỐI LƯỢNG (`corp_actions.py QTY_EVENT_TYPES` — stock dividend/bonus
    issue/split), vì `data/corp_actions.json` chỉ ghi loại sự kiện đó. Cổ tức TIỀN MẶT KHÔNG
    nằm trong registry này — giá vẫn bị cắt đúng ex-date nhưng KL không đổi, nên hàm này trả
    factor=1.0 (không quy đổi) và drawdown vẫn bị phóng đại đúng bằng tỉ lệ cổ tức/giá (ca
    thật DGC 8.000đ/46.750đ ≈ 17,1%, sát ngưỡng −20%). KHÔNG có cơ chế cảnh báo riêng cho
    trường hợp này ở tầng này — người vận hành cần tự nhớ khi thấy drawdown gần ngưỡng ngay
    sau một ex-date cổ tức tiền mặt.

    §corp-action (job Taylor_20260924_064510+_073500, Việc 2 — THIẾT KẾ LẠI sau arch-review
    NEEDS_CHANGES bản đầu e75788f8). Bản đầu dùng `exdate_frame.classify_positions()` — cơ chế
    đối chiếu THEO NGÀY (so vị thế broker HÔM NAY với snapshot NGÀY TRƯỚC `asof`, chỉ khớp sự
    kiện có `ex_date` = ĐÚNG phiên KẾ TIẾP `asof`). Cron `check-exits` chạy 15:20 ICT — TRƯỚC
    cửa sổ broker credit thật (~19:07-19:10 ICT, đo VPB 09-23/VIB 09-09/BID-MBB-VCB 08-14) ⇒
    KHÔNG BAO GIỜ khớp đúng lúc chạy (no-op CẤU TRÚC, không phải hiếm gặp — đo VPB thật: dd
    -21,1% BÁO SAI). Cũng KHÔNG idempotent: `corp_action_multiplier` bị NHÂN DỒN mỗi lần gọi
    lại trong cùng cửa sổ (che mất một breach thật sau vài lần chạy lại).

    Thay bằng `daily_nav_snapshot.confirmed_qty_multiplier_after(ticker, arm_date)` — TÁI DÙNG
    nguyên hàm đã audit (dùng cho quy đổi NGƯỢC vị thế broker LIVE về vị thế lịch sử), đọc
    THẲNG `data/corp_actions.json` (registry CONFIRMED do `corp_action_auto_confirm.py` ghi
    19:25 ICT — TRƯỚC cả cửa sổ credit của phiên MAI, PERSISTENT trong file, không phụ thuộc
    THỜI ĐIỂM gọi hàm trong ngày). Tích luỹ TẤT CẢ sự kiện CONFIRMED có `ex_date > arm_date` —
    đúng "cả khoảng [arm_date, hôm nay]" thay vì chỉ 1 phiên kế tiếp — và TỰ ĐỘNG idempotent:
    hàm đọc lại từ nguồn mỗi lần gọi (KHÔNG cộng dồn state), gọi 2 lần cùng dữ liệu trả cùng
    kết quả.

    KHÔNG còn nhánh `blocked`/fail-closed — hàm chỉ đọc registry đã CONFIRMED (do người/agent
    xác nhận qua 2-3 nguồn độc lập, xem `corp_actions.json._status`), không tự suy từ diff KL
    broker nữa nên không còn "KL bất thường chưa giải thích được" để fail-safe ở TẦNG NÀY.

    §29 vòng 5 — `dns.confirmed_qty_multiplier_after()` tự trả 1.0 IM LẶNG khi file registry
    KHÔNG TỒN TẠI (fail-open đúng ý cho call-site GỐC của nó trong `daily_nav_snapshot.main()`,
    nơi thiếu file hợp lệ nghĩa là "không có corp-action nào cần quy đổi"). Ở ĐÂY thì khác:
    `cmd_check_exits()` cần phân biệt "registry nói 0 sự kiện" (factor=1.0 tin được) với
    "registry vắng nên chưa hề đọc được gì" (factor=1.0 không có nghĩa gì) — file vắng ở 11/12
    worktree anh em là chuyện thường, không phải hiếm. Không tự đổi hành vi fail-open của hàm
    dùng chung (sẽ vỡ call-site kia) — kiểm `exists()` NGAY TẠI ĐÂY và ném exception thật để đi
    đúng nhánh except đã có sẵn ở `cmd_check_exits()` (giữ nguyên hệ số cũ, không ghi
    `corp_action_adjustments`, báo "KHÔNG XÁC ĐỊNH ĐƯỢC").
    """
    import daily_nav_snapshot as dns
    if not os.path.exists(dns.CORP_ACTIONS_FILE):
        raise FileNotFoundError(f"registry corp-action không tồn tại: {dns.CORP_ACTIONS_FILE}")
    return dns.confirmed_qty_multiplier_after(ticker, arm_date)


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

    if not math.isfinite(args.f) or args.f > MAX_F + 1e-9:
        print(f"❌ f={args.f} không phải số hữu hạn ≤ hard-cap {MAX_F} (đồng quy ước "
              f"capit_margin_lever, KHÔNG dùng broker-max 2,0).", file=sys.stderr)
        return 2

    if not math.isfinite(args.arm_price) or args.arm_price <= 0:
        print(f"❌ --arm-price={args.arm_price} không phải số hữu hạn dương (nan/inf/≤0) — "
              f"cấm arm: mọi phép chia dùng arm_price ở cmd_check_exits sẽ ÂM THẦM cho drawdown "
              f"=nan và bị bỏ qua khỏi breach check (§29 coding_guidelines).", file=sys.stderr)
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
    factor_lookup_failed = {}   # id(arm dict) -> lỗi thật, chỉ tồn tại trong LƯỢT NÀY (không
                                 # persist vào arm JSON) — dùng để rẽ câu khi build tin breach
                                 # (§29). Key theo id(a), KHÔNG theo ticker: 2 arm CÙNG ticker
                                 # (blocker 3) sẽ collide nếu key bằng ticker string.
    for a in live:
        px, src, err = current_price(a["ticker"])
        if err:
            errors.append(f"{a['ticker']}: {err}")
            continue

        # arm_date = ngày ARM (hệ giá TRƯỚC mọi sự kiện kể từ đó) — registry đọc lại TOÀN BỘ
        # sự kiện CONFIRMED có ex_date > arm_date mỗi lần gọi, nên tự idempotent (không cộng
        # dồn state, xem docstring corp_action_frame_multiplier).
        #
        # §29 vòng 6 blocker 2: bản cũ `str(a.get("armed_at") or "")[:10]` + `if arm_date else
        # 1.0` coi armed_at RỖNG hoặc KHÔNG PHẢI ngày hợp lệ (vd "unknown-date"[:10]=
        # "unknown-da") là "không có ngày arm ⇒ không có sự kiện" và rơi thẳng vào nhánh
        # SUCCESS bên dưới — ghi note "tích luỹ sự kiện CONFIRMED ex_date > '' ⇒ hệ số
        # ×1.000000", ĐÈ MẤT multiplier cũ đã biết (từ lần đọc thành công trước) về 1.0 dù CHƯA
        # HỀ đọc registry lượt này. Sửa: parse ISO TRƯỚC khi gọi registry; rỗng/không hợp lệ đi
        # thẳng vào nhánh "unverified" giống hệt lỗi đọc registry (giữ nguyên hệ số cũ, không
        # note giả, factor_lookup_failed) — KHÔNG BAO GIỜ vào nhánh success với arm_date rỗng.
        arm_date_raw = str(a.get("armed_at") or "")[:10]
        err_detail = None
        try:
            arm_date = dt.date.fromisoformat(arm_date_raw).isoformat()
        except ValueError:
            arm_date = None
            err_detail = f"armed_at={a.get('armed_at')!r} rỗng hoặc không phải ngày ISO hợp lệ"

        if err_detail is None:
            try:
                factor = corp_action_frame_multiplier(a["ticker"], arm_date)
            except Exception as exc:
                err_detail = f"{type(exc).__name__}: {exc}"

        if err_detail is not None:
            # §29: "lỗi đọc registry"/"arm_date không hợp lệ" ≠ "registry nói không có sự
            # kiện" — KHÔNG được ghi a["corp_action_multiplier"] hay khẳng định đã đọc được
            # registry lượt này (vòng 3 từng vá sai: fail-open factor=1.0 rồi vẫn rơi vào nhánh
            # ghi note "tích luỹ sự kiện ⇒ ×1.000000", ĐÈ MẤT hệ số 1.30 đã biết từ lần đọc
            # thành công trước đó).
            # Sửa: GIỮ NGUYÊN corp_action_multiplier đã biết gần nhất (nếu chưa từng đọc thành
            # công thì mặc định 1.0). An toàn MỘT CHIỀU, không phải mọi chiều: hệ số chỉ TÍCH LUỸ
            # TĂNG DẦN theo sự kiện CONFIRMED mới (§corp-action ở trên) nên giữ giá trị cũ thường
            # làm drawdown tính RA ÂM HƠN thực (cảnh báo giả, không bỏ sót cảnh báo thật). Chiều
            # NGƯỢC LẠI — một sự kiện CONFIRMED bị REVOKE khiến hệ số thật đã giảm xuống dưới giá
            # trị cache — thì giữ hệ số CŨ (cao hơn) làm drawdown tính RA ÍT ÂM HƠN thực, CÓ THỂ
            # che một breach thật. Chưa có cơ chế fail-closed cho chiều này (revoke hiếm, và
            # fail-closed sẽ chặn oan mọi lần registry chỉ đơn thuần tạm không đọc được) — người
            # vận hành cần biết giới hạn này khi thấy dòng "KHÔNG XÁC ĐỊNH ĐƯỢC" lặp lại nhiều lần.
            # Không `continue` — arm này vẫn được đánh giá breach, các arm KHÁC trong vòng lặp
            # không bị 1 registry lỗi làm crash lây.
            msg = (f"{a['ticker']}: lỗi đọc corp-action registry khi tính multiplier — "
                   f"KHÔNG cập nhật hệ số (giữ nguyên giá trị đã biết gần nhất, nếu có). "
                   f"Lỗi thật: {err_detail}")
            print(f"⚠ {msg}", file=sys.stderr)
            errors.append(msg)
            factor_lookup_failed[id(a)] = err_detail
        else:
            prior_factor = a.get("corp_action_multiplier", 1.0)
            if factor != prior_factor:
                note = (f"registry corp_actions.json: tích luỹ sự kiện CONFIRMED ex_date > "
                        f"{arm_date} ⇒ hệ số ×{factor:.6f} (trước đó ×{prior_factor:.6f})")
                a.setdefault("corp_action_adjustments", []).append(
                    {"at": dt.datetime.now(ICT).isoformat(timespec="seconds"),
                     "factor_before": prior_factor, "factor_after": factor, "note": note})
                a["corp_action_multiplier"] = factor
                print(f"  [CORPACTION] {a['ticker']}: {note}")

        # BLOCKER 2 arch-review vòng 8: `math.isfinite` đã gác `mult` khi GHI vào
        # `corp_actions.json` (§29), nhưng phép chia dưới đây dùng `a["arm_price"]` (đọc từ
        # arms JSON, không qua CA.validate()) làm SỐ BỊ CHIA — nan/inf ở đây làm `drawdown`=nan,
        # so sánh `nan <= EXIT_DD_PCT` luôn False ⇒ arm ÂM THẦM rơi khỏi breach check, in "OK"
        # dù drawdown thật KHÔNG so sánh được (đo thật: --arm-price nan qua CLI trước bản vá
        # BLOCKER 1 ở cmd_arm vẫn tới được đây nếu file arms bị sửa tay/hỏng dữ liệu cũ).
        mult_now = a.get("corp_action_multiplier", 1.0)
        if (not math.isfinite(a["arm_price"]) or a["arm_price"] <= 0
                or not math.isfinite(mult_now) or mult_now <= 0):
            msg = (f"{a['ticker']}: arm_price={a['arm_price']!r} hoặc "
                   f"corp_action_multiplier={mult_now!r} không phải số hữu hạn dương — "
                   f"KHÔNG tính được drawdown, bỏ qua breach check cho case này lượt này.")
            print(f"⚠ {msg}", file=sys.stderr)
            errors.append(msg)
            a["last_checked"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
            a["last_price"] = px
            a["last_price_source"] = src
            changed = True
            continue

        arm_price_frame = a["arm_price"] / mult_now
        drawdown = px / arm_price_frame - 1.0
        a["last_checked"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
        a["last_price"] = px
        a["last_price_source"] = src
        a["last_drawdown"] = round(drawdown, 4)
        a["arm_price_frame_adjusted"] = round(arm_price_frame, 2)
        changed = True
        if drawdown <= EXIT_DD_PCT + 1e-9:      # epsilon: tránh lệch làm tròn nhị phân bỏ sót đúng ngưỡng
            a["exit_alerts"].append({"date": a["last_checked"], "price": px,
                                      "drawdown": round(drawdown, 4)})
            # §29 vòng 6 blocker 3: mang thẳng OBJECT `a` (không phải chỉ ticker) — tra lại qua
            # ticker string bên dưới (`by_ticker = {a["ticker"]: a for a in live}`) collapse 2
            # arm CÙNG ticker (vd re-arm lại giá khác, cmd_arm không có guard chặn) thành 1 entry,
            # khiến alert của arm A in nhầm arm_price/frame của arm B (đo thật: 2 arm VPB 26.000
            # và 39.000 cùng breach, alert của arm dd −25% lại in "arm_price 39.000" của arm kia).
            breaches.append((a, px, drawdown))

    if changed:
        save_arms(arms)

    for ticker, err in [(None, e) for e in errors]:
        print(f"⚠ {err}")

    if breaches:
        for a, px, drawdown in breaches:
            ticker = a["ticker"]
            frame_note = ""
            if id(a) in factor_lookup_failed:
                # §29: registry lỗi lượt này — KHÔNG in bất kỳ số nào ngụ ý đã đọc được registry
                # (kể cả hệ số cũ đã biết), tuyệt đối không lặp lại bug "×1.000000" vòng 3.
                frame_note = (f" (⚠ hệ số corp-action KHÔNG XÁC ĐỊNH ĐƯỢC lượt này — lỗi đọc "
                               f"registry: {factor_lookup_failed[id(a)]}. Drawdown dưới đây "
                               f"CHƯA xác nhận quy đổi theo sự kiện mới nhất, có thể là cảnh "
                               f"báo giả)")
            elif "arm_price_frame_adjusted" in a:
                frame_note = (f" (quy đổi corp-action: arm_price {a['arm_price']:,.0f} → "
                               f"{a['arm_price_frame_adjusted']:,.0f}, hệ số ×"
                               f"{a.get('corp_action_multiplier', 1.0):.6f})")
            msg = (f"🚨 **KỶ LUẬT THOÁT −20% CHẠM** — {ticker}: giá hiện tại {px:,.0f} vs giá arm "
                   f"→ drawdown {drawdown:.1%} ≤ {EXIT_DD_PCT:.0%}{frame_note}. Chính sách yêu cầu "
                   f"de-lever BẮT BUỘC (`discretionary-margin-policy-20260823.md` §Rào chắn rủi "
                   f"ro) — đây là CẢNH BÁO, hành động thoát vẫn cần người quyết.")
            print(msg)
            bus_payload = {"ticker": ticker, "price": px, "drawdown": drawdown,
                           "frame_unverified": id(a) in factor_lookup_failed}
            if id(a) in factor_lookup_failed:
                bus_payload["frame_unverified_reason"] = factor_lookup_failed[id(a)]
            _bus("error", f"discretionary-margin-exit-breach-{ticker}", bus_payload)
            _notify(msg)

    # R9-2 arch-review vòng 10: PHẢI là `if` ĐỘC LẬP, không phải `elif` của nhánh breaches ở
    # trên — khi CÙNG lượt có ≥1 arm breach VÀ ≥1 arm khác rơi vào errors (giá không lấy được /
    # registry lỗi / isfinite fail), `elif errors:` cũ KHÔNG BAO GIỜ chạy vì đã vào nhánh
    # `if breaches:` trước đó ⇒ cảnh báo/bus/notify cho arm KHÔNG kiểm được biến mất hoàn toàn
    # khỏi mọi kênh (chỉ còn dòng "⚠" rơi vào log cron, mù với ERROR_RE). Sleeve có trần 10%
    # NAV / 5% per-name nên 2-3 arm cùng lúc là hình dạng bình thường, không phải ca hiếm.
    if errors:
        summary = (f"⚠ {len(live)} case active, {len(errors)} case KHÔNG kiểm được breach lượt "
                   f"này (xem cảnh báo ⚠ ở trên) — KHÔNG phải xác nhận an toàn.")
        print(summary)
        # B-2 arch-review vòng 9: nhánh này trước đây chỉ in stdout/stderr — rc=1 rơi vào log
        # cron không MAILTO, cron_health_check.py's ERROR_RE chỉ bắt dòng bắt đầu "❌", MÙ với
        # "⚠" (đo thật). Ca thật tái hiện được: registry/multiplier hỏng khiến TOÀN BỘ case active
        # rơi vào errors (0 breach nào tính được) mà không ai được báo. Bắn bus+notify ở đây —
        # tần suất thấp (chỉ khi có lỗi giá/registry/dữ liệu VÀ còn case đang sống).
        ok_b = _bus("error", "discretionary-margin-check-exits-errors",
                    {"live_count": len(live), "error_count": len(errors), "errors": errors})
        ok_n = _notify(f"⚠️ **discretionary_margin_gate check-exits**: {summary}\n" +
                       "\n".join(f"• {e}" for e in errors))
        if not (ok_b and ok_n):
            # R9-3 arch-review vòng 10: nếu _bus/_notify thất bại, không có dấu vết nào khớp
            # ERROR_RE của cron_health_check.py — dùng đúng marker "NOTIFY_FAILED" đã có tiền lệ
            # trong chính codebase (corp_action_feed_canary.py:416).
            print("❌ NOTIFY_FAILED discretionary-margin-check-exits-errors — bản ghi errors đã "
                  "in ở trên nhưng dấu vết bus/Discord không đầy đủ, báo lại kênh "
                  "discretionary_stocks bằng tay.")

    if not breaches and not errors:
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
