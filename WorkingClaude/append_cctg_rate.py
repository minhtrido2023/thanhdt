#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
append_cctg_rate.py — append ONE new Big-4 CCTG rate anchor (12M highest-of-Big-4 since 2026-10-05; 6M before) to the append-only
data/cctg_rate_vn_events.csv, read by cctg_rate_vn.py::cctg_events_df().

Sibling of append_deposit_rate.py (Big-4 12M term deposit) — SEPARATE series, SEPARATE CSV, never
merges into or overwrites the deposit CSV. Reuses append_deposit_rate.py's owner-group domain
logic (`_owner_group`, `SAME_OWNER_GROUPS`) by import rather than duplicating it — that logic is
already hardened through 8 rounds of adversarial review (see that file's docstring) and must not
drift into two copies that silently diverge.

Caller-identity gating (JOB_ID-bound, never a self-declared flag) is IDENTICAL in spirit to
append_deposit_rate.py: a dispatched agent may only use --source web_crosscheck_auto, --force is
human-only, --collected must be today. See that file's docstring for the full threat-model
rationale — not re-litigated here.

NEW requirement vs the Big-4 script (user directive, job Taylor_20261001_054108, weekly CCTG
mechanism): each --sources entry must carry its OWN cited `rate` (%, not just publisher/url/date).
The script mechanically checks that (a) all cited rates agree within CROSS_SOURCE_TOLERANCE_PP of
each other, and (b) --rate itself matches at least one cited source within FLOAT_EPS — so the
agent cannot synthesize a number no single source actually said. This is a genuine gap the Big-4
script does NOT close (its --sources schema has no rate field at all) — deliberately NOT
retrofitted into append_deposit_rate.py here to avoid touching an already-CONFIRMED production
guard outside the scope of this job; flagged for Mike/user to consider porting back separately.

Usage (human, interactive):
  python3 append_cctg_rate.py --rate 7.6 --effective 2026-10-08 --source manual_verify \
          --note "VietnamNet 08/10"

Usage (agent, web_crosscheck_auto):
  python3 append_cctg_rate.py --rate 7.6 --effective 2026-10-08 --source web_crosscheck_auto \
          --sources '[{"publisher":"VietnamNet","url":"https://vietnamnet.vn/...","date":"2026-10-06","rate":7.6},
                       {"publisher":"VnExpress","url":"https://vnexpress.net/...","date":"2026-10-07","rate":7.6}]' \
          --note "..."

Usage (--series tier2 — VPB/MB/TCB/ACB, collect + display only, own file, key = bank x denomination):
  python3 append_cctg_rate.py --series tier2 --bank VPB --product "CCTG Super Thịnh Vượng" \
          --denom 100tr --holding "184-389 ngày" --rate 9.2 --effective 2026-10-13 --source ...

Idempotent: re-running with an effective_date already present is skipped (unless --force).
"""
import argparse
import contextlib
import csv
import fcntl
import json
import os
import sys
import tempfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # coding_guidelines §16: never trust the host system TZ

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from append_deposit_rate import (  # noqa: E402 — reuse hardened domain logic, not a dup
    _owner_group, _check_urls_not_reused, _save_last_auto_urls)

CSV_PATH = os.path.join(HERE, "data", "cctg_rate_vn_events.csv")
# Own sidecar name, separate from append_deposit_rate.py's — two independent series, two
# independent reuse windows (coord job Taylor_20261001_061238 item 3; see
# append_deposit_rate.py's docstring for the full rationale). Derived from CSV_PATH's directory,
# same reasoning as that module's _last_auto_sources_path() — automatically test-isolated
# whenever CSV_PATH itself is monkeypatched to a tmpdir.
LAST_AUTO_SOURCES_NAME = "cctg_rate_last_auto_sources.json"


# --series 6m (user duyệt 2026-10-07): chuỗi CCTG 6 THÁNG cao nhất Big-4, thu SONG SONG chuỗi 12M
# để Bobby đọc đa-proxy. File + sidecar RIÊNG; KHÔNG consumer production nào đọc (không vào
# effective rate / kill-switch A / DCF). Mốc đông cứng = anchor gốc 2026-09-30 7,5% (VCB 6M, chính
# là CCTG_EVENTS[0] của cctg_rate_vn.py trước khi rebase sang 12M ngày 05/10).
CSV_PATH_6M = os.path.join(HERE, "data", "cctg_rate_vn_6m_events.csv")
LAST_AUTO_SOURCES_NAME_6M = "cctg6m_rate_last_auto_sources.json"
SEED_6M = ("2026-09-30", 7.5)

# --series tier2 (user duyệt 2026-10-13): CCTG của nhóm ngân hàng NGAY SAU Big-4. CHỈ THU THẬP +
# HIỂN THỊ — file RIÊNG, KHÔNG consumer nào đọc (cctg_tier2_series_selfcheck.py chứng minh:
# effective rate / kill-switch A / consumer_deposit_rate* / trend check không mở file này).
# Khác 12m/6m: MỘT file chứa nhiều chuỗi con, khoá = (bank, denomination). Guard (idempotent,
# ngày mới hơn, lệch >=1,0pp, URL dùng lại) tính RIÊNG từng khoá, không có mốc đông cứng. Số của
# ngân hàng này KHÔNG BAO GIỜ được dùng để SUY số ngân hàng khác; nhưng để guard lệch >=1,0pp không
# lách được bằng ĐỔI KHOÁ (job Taylor_20261013_090057, arch-review A3), một khoá MỚI do agent mở
# phải qua kiểm tra cơ học (_tier2_new_key_guard): người (không JOB_ID) seed khoá mới thì không bị
# chặn; ngân hàng đã có khoá kiểu 10tr/100tr thì từ chối khoá "" và ngược lại (trừ --force của người).
# Ghi song song: toàn bộ đọc→ghi→sidecar của tier2 nằm trong flock <csv>.lock (A1).
CSV_PATH_TIER2 = os.path.join(HERE, "data", "cctg_rate_vn_tier2_events.csv")
TIER2_BANKS = ("VPB", "MB", "TCB", "ACB")
TIER2_DENOMS = ("10tr", "100tr")  # "" = nguồn không nêu / ngân hàng không chia theo 2 mệnh giá này
HEADER_TIER2 = ["effective_date", "bank", "product", "denomination", "holding_period", "cctg_rate",
                "collected_date", "source", "note"]


def _tier2_sidecar_name(bank, denom):
    return f"cctg_tier2_{bank}_{denom or 'na'}_last_auto_sources.json"


def _last_auto_sources_path():
    return os.path.join(os.path.dirname(CSV_PATH), LAST_AUTO_SOURCES_NAME)
HEADER = ["effective_date", "cctg_rate", "collected_date", "source", "note"]
VALID_SOURCES = {"manual_verify", "web_crosscheck_auto"}
SOURCES_REQUIRING_NOTE = {"web_crosscheck_auto"}
SOURCES_REQUIRING_STRUCTURED_SOURCES = {"web_crosscheck_auto"}
MIN_DISTINCT_OWNERS = 2
MAX_SOURCE_AGE_DAYS = 35
MAX_FUTURE_EFFECTIVE_DAYS = 2
NONINERT_DELTA_PP = 1.0  # same threshold family as append_deposit_rate.py's guard
CROSS_SOURCE_TOLERANCE_PP = 0.1  # per dispatch: sources must agree within 0.1pp of each other
FLOAT_EPS = 1e-6
RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0  # matches cctg_rate_vn.py's own sanity fence


@contextlib.contextmanager
def _tier2_flock(csv_path):
    """Khoá loại trừ cho cả đọc→ghi→sidecar của file tier2 (nhiều lệnh --series tier2 chạy cùng lúc
    từng làm mất dòng im lặng). Khoá giữ trên <csv>.lock, nhả khi thoát khối (kể cả sys.exit)."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path + ".lock", "a") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def _tier2_key_str(bank, denom):
    return f"[tier2 {bank} {denom or 'mệnh giá n/a'}]"


def _latest_by_key(all_rows):
    """{(bank, denom): rate mới nhất theo effective_date} — chỉ để so khoá mới, không suy số."""
    best = {}
    for r in all_rows:
        k = (r.get("bank"), r.get("denomination") or "")
        if k not in best or r["effective_date"] >= best[k][0]:
            best[k] = (r["effective_date"], float(r["cctg_rate"]))
    return {k: v[1] for k, v in best.items()}


def _tier2_new_key_guard(all_rows, bank, denom, rate, is_agent, force):
    """Trả None nếu được ghi, hoặc chuỗi lý do từ chối. Chỉ gọi khi khoá (bank, denom) CHƯA có dòng.
    (a) ngân hàng đã có khoá kiểu mệnh giá ⇄ khoá '' : từ chối (người có --force thì qua);
    (b) agent mở khoá mới cho ngân hàng ĐÃ có dòng: phải lệch <1pp so với ít nhất một khoá cùng
        ngân hàng; (c) agent mở khoá cho ngân hàng CHƯA có dòng: phải nằm trong (min-1, max+1) của
        dòng mới nhất mọi khoá ngân hàng khác; file rỗng ⇒ không có mốc ⇒ từ chối (fail-safe)."""
    latest = _latest_by_key(all_rows)
    same_bank = {k: v for k, v in latest.items() if k[0] == bank}
    kstr = _tier2_key_str(bank, denom)
    if same_bank and not force:
        has_denom = any(k[1] for k in same_bank)
        has_blank = any(not k[1] for k in same_bank)
        if (denom and has_blank and not has_denom) or (not denom and has_denom):
            return (f"{kstr} mở KHOÁ MỚI cho {bank} đang có khoá {sorted(k[1] or '(rỗng)' for k in same_bank)} "
                    f"— đổi kiểu mệnh giá (rỗng ⇄ 10tr/100tr) làm guard lệch >=1pp mất tác dụng. "
                    f"Từ chối; người xác nhận rồi ghi bằng --force.")
    if not is_agent:
        return None
    if same_bank:
        gaps = [abs(rate - v) for v in same_bank.values()]
        if min(gaps) >= NONINERT_DELTA_PP:
            return (f"{kstr} khoá MỚI do agent mở, lệch {min(gaps):.2f}pp (>= {NONINERT_DELTA_PP}pp) so với mọi khoá "
                    f"đã có của {bank} {sorted(same_bank.items())} — từ chối. Nhờ người seed khoá này (manual_verify).")
        return None
    others = list(latest.values())
    if not others:
        return (f"{kstr} khoá MỚI do agent mở nhưng file tier2 chưa có dòng nào làm mốc — từ chối. "
                f"Nhờ người seed (manual_verify) trước.")
    lo, hi = min(others) - NONINERT_DELTA_PP, max(others) + NONINERT_DELTA_PP
    if not (lo < rate < hi):
        return (f"{kstr} ngân hàng CHƯA có dòng nào, rate {rate:g}% nằm ngoài dải ({lo:g}, {hi:g}) của dòng mới nhất "
                f"các ngân hàng khác — từ chối. Nhờ người seed (manual_verify).")
    return None


def _read_rows(path=None):
    path = path or CSV_PATH
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def _valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    with contextlib.ExitStack() as stack:
        return _main_impl(stack)


def _main_impl(stack):
    ap = argparse.ArgumentParser(description="Append one CCTG rate anchor (append-only): --series 12m/6m = highest-of-Big-4 (see cctg_rate_vn.py); --series tier2 = one of VPB/MB/TCB/ACB.")
    ap.add_argument("--rate", type=float, required=True, help="CCTG rate, %%/yr (12m/6m: highest-of-Big-4, e.g. 7.4; tier2: that bank's highest holding<=12m)")
    ap.add_argument("--effective", required=True, help="effective date YYYY-MM-DD")
    ap.add_argument("--source", required=True, help="one of: " + " | ".join(sorted(VALID_SOURCES)))
    ap.add_argument("--collected", default=None, help="real collection date YYYY-MM-DD (default: today)")
    ap.add_argument("--note", default="", help="free-text note")
    ap.add_argument("--sources", default=None,
                    help='JSON array of {"publisher","url","date","rate"} — REQUIRED for '
                         '--source web_crosscheck_auto')
    ap.add_argument("--series", choices=("12m", "6m", "tier2"), default="12m",
                    help="12m (mặc định, chuỗi production) | 6m (chuỗi phụ, file riêng, display-only) "
                         "| tier2 (VPB/MB/TCB/ACB, file riêng, display-only)")
    ap.add_argument("--bank", default=None, help="[tier2] một trong: " + " | ".join(TIER2_BANKS))
    ap.add_argument("--product", default=None, help="[tier2] tên sản phẩm CCTG")
    ap.add_argument("--denom", default=None,
                    help="[tier2] mệnh giá: " + " | ".join(TIER2_DENOMS) + " (bỏ trống nếu nguồn không nêu)")
    ap.add_argument("--holding", default=None,
                    help="[tier2] khoảng thời gian nắm giữ mà mức này áp dụng (vd '184-389 ngày'); "
                         "bỏ trống nếu chưa đối chiếu được")
    ap.add_argument("--force", action="store_true",
                    help="append even if effective_date exists / override delta guard. REFUSED "
                         "when JOB_ID env is set.")
    args = ap.parse_args()
    is_6m = args.series == "6m"
    is_tier2 = args.series == "tier2"
    tier2_given = [n for n in ("bank", "product", "denom", "holding") if getattr(args, n) is not None]
    if not is_tier2 and tier2_given:
        sys.exit(f"ERROR: --{'/--'.join(tier2_given)} chỉ dùng với --series tier2 — từ chối để một "
                 f"dòng ngân hàng ngoài Big-4 không lọt vào chuỗi {args.series}.")
    bank = denom = product = holding = ""
    if is_tier2:
        bank, denom = args.bank or "", (args.denom or "").strip()
        product, holding = (args.product or "").strip(), (args.holding or "").strip()
        if bank not in TIER2_BANKS:
            sys.exit(f"ERROR: --series tier2 cần --bank thuộc {TIER2_BANKS}, nhận '{bank}'.")
        if not product:
            sys.exit("ERROR: --series tier2 cần --product (tên sản phẩm CCTG) không rỗng.")
        if denom and denom not in TIER2_DENOMS:
            sys.exit(f"ERROR: --denom '{denom}' không thuộc {TIER2_DENOMS} (hoặc bỏ trống).")
    # Locals, không gán lại global: selfcheck gọi main() nhiều lần trong 1 process và monkeypatch
    # CSV_PATH/CSV_PATH_6M — gán global sẽ làm lượt 12m sau một lượt 6m ghi nhầm file 6m.
    csv_path = CSV_PATH_TIER2 if is_tier2 else (CSV_PATH_6M if is_6m else CSV_PATH)
    if is_tier2:
        sidecar_path = os.path.join(os.path.dirname(CSV_PATH_TIER2), _tier2_sidecar_name(bank, denom))
    else:
        sidecar_path = (os.path.join(os.path.dirname(CSV_PATH_6M), LAST_AUTO_SOURCES_NAME_6M)
                        if is_6m else _last_auto_sources_path())

    is_dispatched_agent = os.environ.get("JOB_ID") is not None
    if is_dispatched_agent and args.force:
        sys.exit("ERROR: --force is refused — JOB_ID is set (dispatched headless agent). "
                 "Human-only override; resolve escalations interactively.")
    if is_dispatched_agent and args.source != "web_crosscheck_auto":
        sys.exit(f"ERROR: --source '{args.source}' is refused — JOB_ID is set. A dispatched "
                 f"agent may ONLY use --source web_crosscheck_auto. Escalate instead.")

    try:
        eff = _valid_date(args.effective)
    except ValueError:
        sys.exit(f"ERROR: --effective '{args.effective}' is not YYYY-MM-DD")
    real_today = datetime.now(_ICT).date().isoformat()
    if is_dispatched_agent:
        eff_age_days = (eff - _valid_date(real_today)).days
        if eff_age_days > MAX_FUTURE_EFFECTIVE_DAYS or eff_age_days < -MAX_SOURCE_AGE_DAYS:
            sys.exit(f"ERROR: --effective '{args.effective}' is {eff_age_days} days from today "
                     f"({real_today}) — refused for a dispatched agent (max "
                     f"{MAX_FUTURE_EFFECTIVE_DAYS} days forward, {MAX_SOURCE_AGE_DAYS} days back).")
    collected = args.collected or real_today
    try:
        _valid_date(collected)
    except ValueError:
        sys.exit(f"ERROR: --collected '{collected}' is not YYYY-MM-DD")
    if is_dispatched_agent and collected != real_today:
        sys.exit(f"ERROR: --collected '{collected}' is refused — JOB_ID is set, --collected may "
                 f"ONLY be today ({real_today}).")
    if not (RATE_MIN_PCT < args.rate < RATE_MAX_PCT):
        sys.exit(f"ERROR: --rate {args.rate} out of sane range ({RATE_MIN_PCT}, {RATE_MAX_PCT}) "
                 f"— refuse to write")
    if args.source not in VALID_SOURCES:
        sys.exit(f"ERROR: --source '{args.source}' not in {sorted(VALID_SOURCES)}")
    if args.source in SOURCES_REQUIRING_NOTE and not args.note.strip():
        sys.exit(f"ERROR: --source {args.source} requires a non-empty --note.")

    # --- idempotency check FIRST, before the "not newer than last anchor" guard below (fix,
    # coord job Taylor_20261001_061238 item B1): a same-day re-run of the weekly cron used to hit
    # the "not newer" guard instead of this SKIP, because the FIRST run's own write becomes the
    # new last_date seen by the SECOND run — so re-running on an already-written date raised
    # "ERROR: not newer than the last anchor" (rc=1) instead of the intended idempotent SKIP
    # (rc=0), firing a false Winston escalate-question every time the cron (or a human) re-ran on
    # a day already confirmed. append_deposit_rate.py never had this ordering bug because it has
    # no equivalent "not newer" pre-check — only this CCTG script does.
    if is_tier2:
        stack.enter_context(_tier2_flock(csv_path))  # A1: đọc→ghi→sidecar là MỘT đoạn găng
    rows = _read_rows(csv_path)
    all_rows = rows  # tier2: cả file, giữ nguyên thứ tự; `rows` bên dưới chỉ còn khoá đang ghi
    if is_tier2:
        rows = [r for r in rows if (r.get("bank"), r.get("denomination") or "") == (bank, denom)]
    existing = {r["effective_date"] for r in rows}
    if args.effective in existing and not args.force and is_tier2:
        prev = [r for r in rows if r["effective_date"] == args.effective][0]
        same = (prev.get("product", "") == product and abs(float(prev["cctg_rate"]) - args.rate) <= FLOAT_EPS)
        if not same:
            sys.exit(f"ERROR: {_tier2_key_str(bank, denom)} {args.effective} ĐÃ có dòng KHÁC: product='{prev.get('product', '')}' "
                     f"rate={prev['cctg_rate']}% (source={prev.get('source')}) — lệnh này đòi product='{product}' "
                     f"rate={args.rate:g}%. Không ghi; người xác nhận rồi --force.")
        print(f"SKIP: {_tier2_key_str(bank, denom)} effective_date {args.effective} already present, cùng sản phẩm + "
              f"lợi suất (use --force to override). No write — CSV unchanged.")
        return 0
    if args.effective in existing and not args.force:
        print(f"SKIP: effective_date {args.effective} already present (use --force to override). "
              f"No write — CSV unchanged.")
        return 0

    # --- date-newer-than-last-anchor guard (fail fast, before writing a row cctg_events_df()
    # would reject on next load anyway — avoid leaving the CSV in a state nobody notices is broken
    # until the next unrelated reader crashes) ---
    # `--force` khi effective_date ĐÃ TỒN TẠI là đính chính một dòng cũ, không phải chèn ngày mới
    # lệch thứ tự — so last_date trên CẢ series (gồm chính dòng sắp bị thay) luôn tự chặn (eff ==
    # last_date). Loại trừ đúng dòng đang sửa khỏi phép so để guard chỉ còn chặn cái nó PHẢI chặn:
    # ngày nhỏ hơn mốc đông cứng trong code (CCTG_EVENTS/SEED_6M — không ai được sửa qua CLI này).
    import cctg_rate_vn
    is_correction = args.force and args.effective in existing
    if is_tier2:
        other_dates = [_valid_date(r["effective_date"]) for r in rows
                       if not (is_correction and r["effective_date"] == args.effective)]
        last_date = max(other_dates) if other_dates else date.min  # khoá chưa có dòng nào
    elif is_6m:
        other_dates = ([_valid_date(SEED_6M[0])] +
                       [_valid_date(r["effective_date"]) for r in rows
                        if not (is_correction and r["effective_date"] == args.effective)])
        last_date = max(other_dates)
    else:
        if is_correction:
            last_date = _valid_date(cctg_rate_vn.CCTG_EVENTS[-1][0])
        else:
            existing_ev = cctg_rate_vn.cctg_events_df()
            last_date = existing_ev["time"].max().date()
    if eff <= last_date and (is_tier2 or is_6m):
        # cctg_events_df() chỉ đọc file 12M — không nhắc nó với 2 chuỗi này (§29: thông báo phải đúng)
        sys.exit(f"ERROR: {_tier2_key_str(bank, denom) + ' ' if is_tier2 else '[6m] '}--effective {eff} is not newer than the "
                 f"last anchor {last_date} of this series. Refuse to write (typo'd year? duplicate run?).")
    if eff <= last_date:
        sys.exit(f"ERROR: --effective {eff} is not newer than the last anchor {last_date} — "
                 f"cctg_events_df() treats this as corrupt/duplicate data and will raise loudly "
                 f"on next load. Refuse to write (typo'd year? duplicate run?).")

    # --- publisher independence + cross-source rate agreement: mechanically checked ---
    if args.source in SOURCES_REQUIRING_STRUCTURED_SOURCES:
        if not args.sources:
            sys.exit(f"ERROR: --source {args.source} requires --sources (JSON array of "
                     f">= {MIN_DISTINCT_OWNERS} {{publisher,url,date,rate}} entries).")
        try:
            sources = json.loads(args.sources)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: --sources is not valid JSON: {e}")
        if not isinstance(sources, list) or len(sources) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources must be a JSON array with >= {MIN_DISTINCT_OWNERS} "
                     f"entries, got {sources!r}")
        urls = [s.get("url", "") for s in sources if isinstance(s, dict)]
        if len(urls) != len(sources) or not all(urls):
            sys.exit("ERROR: every --sources entry must be an object with a non-empty 'url'.")
        try:
            owner_groups = {_owner_group(u) for u in urls}
        except ValueError as e:
            sys.exit(f"ERROR: {e}")
        if len(owner_groups) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources resolve to only {len(owner_groups)} distinct owner "
                     f"group(s) ({sorted(owner_groups)}) — need >= {MIN_DISTINCT_OWNERS}. Refuse.")
        _check_urls_not_reused(urls, sidecar_path)
        today_d = _valid_date(real_today)
        src_rates = []
        for s in sources:
            raw_date = s.get("date", "")
            try:
                src_date = _valid_date(raw_date)
            except ValueError:
                sys.exit(f"ERROR: --sources entry has invalid/missing 'date' ('{raw_date}').")
            age_days = (today_d - src_date).days
            if age_days < 0 or age_days > MAX_SOURCE_AGE_DAYS:
                sys.exit(f"ERROR: --sources entry dated {raw_date} is {age_days} days from "
                         f"today ({real_today}) (max {MAX_SOURCE_AGE_DAYS}, or future) — too "
                         f"stale/invalid. Refuse to write.")
            raw_rate = s.get("rate", None)
            if raw_rate is None:
                sys.exit(f"ERROR: --sources entry missing 'rate' field (url={s.get('url')!r}) — "
                         f"each cited source must carry its own observed rate for cross-check.")
            try:
                src_rate = float(raw_rate)
            except (TypeError, ValueError):
                sys.exit(f"ERROR: --sources entry 'rate'={raw_rate!r} is not a number.")
            if not (RATE_MIN_PCT < src_rate < RATE_MAX_PCT):
                sys.exit(f"ERROR: --sources entry rate={src_rate} out of sane range "
                         f"({RATE_MIN_PCT}, {RATE_MAX_PCT}).")
            src_rates.append(src_rate)
        spread = max(src_rates) - min(src_rates)
        if spread > CROSS_SOURCE_TOLERANCE_PP + FLOAT_EPS:
            sys.exit(f"ERROR: cited source rates {src_rates} disagree by {spread:.3f}pp "
                     f"(> tolerance {CROSS_SOURCE_TOLERANCE_PP}pp) — refuse to write. Escalate "
                     f"for human review instead of picking one.")
        if not any(abs(args.rate - r) <= FLOAT_EPS for r in src_rates):
            sys.exit(f"ERROR: --rate {args.rate} does not match any cited source rate "
                     f"{src_rates} — refuse to write a number no cited source actually said.")

    # --- delta guard vs current + last human-confirmed anchor ---
    # (rows/existing already loaded by the idempotency check above — nothing has written to disk
    # since, so reusing them here is safe and avoids a second redundant _read_rows() call)
    if is_tier2 and not rows:  # A3: khoá chưa có dòng nào ⇒ không có số cùng khoá; kiểm cơ học khoá MỚI
        why = _tier2_new_key_guard(all_rows, bank, denom, args.rate, is_dispatched_agent, args.force)
        if why:
            sys.exit(f"ERROR: {why}")
    if is_tier2:
        _allk = sorted(rows, key=lambda r: r["effective_date"])
        current_rate = float(_allk[-1]["cctg_rate"]) if _allk else None
    elif is_6m:
        _all6 = sorted(rows, key=lambda r: r["effective_date"])
        current_rate = float(_all6[-1]["cctg_rate"]) if _all6 else SEED_6M[1]
    else:
        current_rate, _ = cctg_rate_vn.current_cctg_rate()
    human_rows = sorted(
        (r for r in rows if r.get("source") not in SOURCES_REQUIRING_STRUCTURED_SOURCES),
        key=lambda r: r["effective_date"])
    last_human_rate = (float(human_rows[-1]["cctg_rate"]) if human_rows
                       else (None if is_tier2 else
                             (SEED_6M[1] if is_6m else cctg_rate_vn.CCTG_EVENTS[-1][1])))
    bases = [b for b in (current_rate, last_human_rate) if b is not None]
    deltas = [abs(args.rate - b) for b in bases]
    if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force and is_tier2:
        sys.exit(f"ERROR: {_tier2_key_str(bank, denom)} rate {args.rate:g}% differs from reference(s) {bases} by up to "
                 f"{max(deltas):.2f}pp (>= {NONINERT_DELTA_PP}pp) — refuse to write. Escalate for "
                 f"human review (--force is human-only).")
    if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force:
        sys.exit(f"ERROR: rate {args.rate:g}% differs from reference(s) {bases} by up to "
                 f"{max(deltas):.2f}pp (>= {NONINERT_DELTA_PP}pp) — refuse to write. Escalate for "
                 f"human review (--force is human-only).")

    if args.force:
        rows = [r for r in rows if r["effective_date"] != args.effective]
    new_row = {"effective_date": args.effective, "cctg_rate": f"{args.rate:g}",
               "collected_date": collected, "source": args.source, "note": args.note}
    if is_tier2:
        new_row.update({"bank": bank, "product": product, "denomination": denom,
                        "holding_period": holding})
        rows = [r for r in all_rows
                if not (args.force and r["effective_date"] == args.effective
                        and (r.get("bank"), r.get("denomination") or "") == (bank, denom))]
    rows.append(new_row)

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(csv_path), prefix=".cctg_", suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER_TIER2 if is_tier2 else HEADER)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, csv_path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    if args.source in SOURCES_REQUIRING_STRUCTURED_SOURCES:
        _save_last_auto_urls(sidecar_path, args.effective, urls)

    if is_tier2:
        print(f"OK: appended [tier2 {bank} {denom or 'mệnh giá n/a'}] {args.effective} = {args.rate:g}% "
              f"(source={args.source}, collected={collected}) -> {csv_path}")
        return 0
    if is_6m:
        print(f"OK: appended [6m] {args.effective} = {args.rate:g}% (source={args.source}, "
              f"collected={collected}) -> {csv_path}")
        return 0
    import importlib
    importlib.reload(cctg_rate_vn)
    ev = cctg_rate_vn.cctg_events_df()
    cur, cur_date = cctg_rate_vn.current_cctg_rate()
    print(f"OK: appended {args.effective} = {args.rate:g}% (source={args.source}, collected={collected}).")
    print(f"    cctg_events_df() now has {len(ev)} anchors; current_cctg_rate() = {cur:.2f}% "
          f"(as of {cur_date}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
