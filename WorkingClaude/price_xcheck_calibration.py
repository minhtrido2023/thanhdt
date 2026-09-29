#!/usr/bin/env python3
"""Calibration measurement for `close_repair.PRICE_XCHECK_TOL` — committed, re-runnable version of
the ad-hoc /tmp measurement cited in `close_repair.py`'s docstring (Việc B, dispatch
Taylor_20260929_042515, 2026-09-29). The /tmp artifacts it replaces
(`/tmp/xcheck_result.txt`, `/tmp/xcheck_full_measure.{sql,json}`) do not survive a reboot — §8c
(kb/coding_guidelines.md) requires a published number to have a re-runnable artifact, not a /tmp
file.

LỆNH TÁI LẬP:
    source wc_env.sh
    python3 price_xcheck_calibration.py

VINTAGE: đo lần đầu 2026-09-29, nguồn `tav2_bq.corporate_action` × `tav2_bq.ticker`. Cửa sổ sự
kiện 2025-01-01..2026-09-15 (khớp docstring PRICE_XCHECK_TOL), cửa sổ giá 2024-11-15..2026-09-20
(đệm ~45 ngày trước sự kiện sớm nhất cho `_lift_neighbour`/band-guard cần bar liền trước). Chi phí
đo bằng `bq query --dry_run` ngày 2026-09-29: events ~1,3MB, bars ~26,6MB — không đáng kể so với
hạn mức free-tier 1TB/tháng.

MẪU SỐ — đọc trước khi diễn giải bảng in ra (bản công bố round-2 ban đầu CỘNG KHÔNG KHỚP vì trộn 2
tầng mẫu số khác nhau — Mike phát hiện 2026-09-29 khi review dispatch này; sửa ở đây bằng cách tách
tường minh):

  Tầng 1 — TOÀN BỘ (ticker, ex-date) price-adjusting event trong cửa sổ (N = A):
    no_series_for_ticker  : ticker KHÔNG CÓ DÒNG NÀO trong toàn bộ `tav2_bq.ticker` trong cửa sổ
                             giá đã fetch — THIẾU PHỦ DỮ LIỆU, không phải lỗi của
                             `price_crosscheck` (quant-skeptic round 2 xác minh 54 ticker dạng
                             này; nhãn gốc "script gap" trong finding đầu là SAI, đã sửa ở đây).
    ex_beyond_series_max  : ticker CÓ series nhưng ex-date nằm SAU ngày cuối series fetch được —
                             giới hạn CỬA SỔ CỦA SCRIPT ĐO này, không phải của `price_crosscheck`.
    n_candidate            : phần còn lại — có series VÀ ex <= series_max — đây mới là input thật
                             đưa vào `close_repair.price_crosscheck_after`.
    A = no_series_for_ticker + ex_beyond_series_max + n_candidate

  Tầng 2 — CHỈ bên trong n_candidate, verdict từ CHÍNH `price_crosscheck_after` (KHÔNG tính lại
  logic — gọi thẳng hàm production). 4 nhánh, KHÔNG PHẢI 3 — bản đo đầu tiên (round 2, /tmp,
  2026-09-29 sáng) gộp "ffill_cum_band" dưới nhãn "uncomputable_formula" vì đoán theo TÊN chung
  chung thay vì đọc đúng `note` production in ra; verify lại bằng CHÍNH `_categorize()` bên dưới
  trên dữ liệu thật phát hiện ra: TOÀN BỘ 681 ca đó là `group_factor`'s CUM bar bị
  `_band_lifted_suspect` từ chối (Price nằm ngoài band đã lift raw), KHÔNG PHẢI rights
  issue/unparsable/cash≥price như mô tả gốc — trong cửa sổ đo này (chỉ DIV + ISS
  bonus/cổ-tức-cổ-phiếu, không có rights issue) số ca uncomputable_formula THẬT là 0:
    tested                 : `price_crosscheck` trả `dev` (có hoặc không mismatch trong
                             PRICE_XCHECK_TOL) — đây là tập `|dev|` được báo cáo bên dưới.
    ffill_cum_band         : phiên CUM bị `_band_lifted_suspect` từ chối vì Price nằm ngoài
                             [Low,High] đã lift raw (note chứa "outside the raw-lifted").
    ffill_chained          : bị `_lift_neighbour`'s `chained` từ chối — Price LẶP LẠI phiên liền
                             trước, ở phiên CUM (note "phiên cum ... nghi ffill") HOẶC phiên
                             EX-DATE (note "phiên ex-date ...", 1 trong 3 nhãn §29 của Việc A).
    uncomputable_formula   : `group_factor` trả None vì lý do cú pháp/kinh tế THẬT — rights issue
                             ("quyền mua"/"unknowable"), exercise_ratio/value_per_share unparsable
                             hoặc <=0, cash >= raw price — KHÔNG liên quan ffill. 0 trong mẫu này,
                             giữ nhánh lại vì đây là hành vi ĐÚNG của `group_factor`, có thể khác 0
                             ở cửa sổ khác/loại event khác.
    no_cum_bar_in_window   : không có phiên nào trước ex-date trong cửa sổ giá đã fetch (hiếm —
                             chỉ xảy ra ở rìa đầu cửa sổ).
    n_candidate = tested + ffill_cum_band + ffill_chained + uncomputable_formula
                  + no_cum_bar_in_window

Phân loại Tầng 2 đọc TRỰC TIẾP từ `note` do chính `price_crosscheck` in ra (xem
`_CATEGORY_PATTERNS` bên dưới) — không suy diễn, không hardcode nguyên nhân (§29).
"""
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import close_repair as cr  # noqa: E402

PROJECT = "lithe-record-440915-m9"
EVENT_START, EVENT_END = "2025-01-01", "2026-09-15"
PRICE_START, PRICE_END = "2024-11-15", "2026-09-20"

SQL_EVENTS = f"""
SELECT ticker, CAST(exright_date AS STRING) AS exright_date, event_code,
       TRIM(IFNULL(issue_method_name_vi,"")) AS issue_method_name_vi,
       SAFE_CAST(exercise_ratio AS FLOAT64) AS exercise_ratio,
       SAFE_CAST(value_per_share AS FLOAT64) AS value_per_share
FROM `{PROJECT}`.tav2_bq.corporate_action
WHERE exright_date BETWEEN "{EVENT_START}" AND "{EVENT_END}"
  AND (
    event_code = "DIV"
    OR (event_code = "ISS" AND TRIM(IFNULL(issue_method_name_vi,"")) IN
        ("Trả Cổ tức bằng Cổ phiếu","Cổ phiếu thưởng"))
  )
"""

SQL_BARS = f"""
WITH tickers_needed AS (
  SELECT DISTINCT ticker FROM `{PROJECT}`.tav2_bq.corporate_action
  WHERE exright_date BETWEEN "{EVENT_START}" AND "{EVENT_END}"
    AND (
      event_code = "DIV"
      OR (event_code = "ISS" AND TRIM(IFNULL(issue_method_name_vi,"")) IN
          ("Trả Cổ tức bằng Cổ phiếu","Cổ phiếu thưởng"))
    )
)
SELECT t.ticker, CAST(t.time AS STRING) AS d, t.Close, t.Price, t.High, t.Low
FROM `{PROJECT}`.tav2_bq.ticker t
JOIN tickers_needed tn ON tn.ticker = t.ticker
WHERE t.time BETWEEN "{PRICE_START}" AND "{PRICE_END}"
  AND t.Price > 0 AND t.Close > 0
ORDER BY t.ticker, t.time
"""

# `price_crosscheck`'s own note text is the ONLY source of truth for Tầng-2 category (§29) — no
# guessed cause. `ffill_cum_band` ("outside the raw-lifted" — `_band_lifted_suspect` rejecting the
# CUM bar) is textually DISTINCT from `ffill_chained` ("nghi ffill" on the cum bar's own chained
# check, or the 3 §29 ex-date labels from Việc A) — verified on real data that these two never
# collide (see module docstring). `no_cum_bar_in_window` checked before the catch-all since its
# note also mentions "cum". Anything left over is the ACTUAL `group_factor` formula failure
# (rights issue/unparsable/cash>=price) — 0 occurrences in this window, not 681 (see docstring).
_CATEGORY_PATTERNS = [
    ("ffill_cum_band", ("outside the raw-lifted",)),
    ("ffill_chained", ("phiên cum", "phiên ex-date")),
    ("no_cum_bar_in_window", ("no cum session inside the price window",
                               "không có phiên cum trong cửa sổ")),
]


def _categorize(note: str) -> str:
    for cat, needles in _CATEGORY_PATTERNS:
        if any(n in note for n in needles):
            return cat
    return "uncomputable_formula"


def main() -> int:
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    print(f"Đang truy vấn corporate_action ({EVENT_START}..{EVENT_END})...", file=sys.stderr)
    events_df = client.query(SQL_EVENTS).to_dataframe()
    print(f"  {len(events_df)} event rows.", file=sys.stderr)
    print(f"Đang truy vấn ticker bars ({PRICE_START}..{PRICE_END}, chỉ ticker có sự kiện)...",
          file=sys.stderr)
    bars_df = client.query(SQL_BARS).to_dataframe()
    print(f"  {len(bars_df)} bar rows, {bars_df['ticker'].nunique()} ticker.", file=sys.stderr)

    events_by_ticker = defaultdict(list)
    for row in events_df.itertuples(index=False):
        events_by_ticker[row.ticker].append({
            "ticker": row.ticker, "exright_date": row.exright_date, "event_code": row.event_code,
            "issue_method_name_vi": row.issue_method_name_vi,
            "exercise_ratio": row.exercise_ratio, "value_per_share": row.value_per_share,
        })

    series_by_ticker = defaultdict(list)
    for row in bars_df.itertuples(index=False):
        series_by_ticker[row.ticker].append(
            {"d": row.d, "close": float(row.Close), "price": float(row.Price),
             "high": float(row.High or 0), "low": float(row.Low or 0)})
    for tk in series_by_ticker:
        series_by_ticker[tk].sort(key=lambda b: b["d"])

    # Tầng 1: group events into (ticker, ex-date) pairs (mirrors `factor_after`'s own grouping —
    # same-day tranches on one ticker collapse to ONE candidate, matching what `price_crosscheck`
    # actually evaluates once per ex-date).
    all_pairs = set()
    for tk, evs in events_by_ticker.items():
        for ev in evs:
            all_pairs.add((tk, ev["exright_date"]))

    tier1 = Counter()
    tested_devs = []
    tier2 = Counter()
    tickers_no_series = set()

    for tk, ex in sorted(all_pairs):
        series = series_by_ticker.get(tk, [])
        if not series:
            tier1["no_series_for_ticker"] += 1
            tickers_no_series.add(tk)
            continue
        series_max = series[-1]["d"]
        if ex > series_max:
            tier1["ex_beyond_series_max"] += 1
            continue
        tier1["n_candidate"] += 1

        # `evs` is already narrowed to exactly this one ex-date, so any `date` strictly before
        # `EVENT_START` satisfies `price_crosscheck_after`'s own `date < ex <= series_max` filter
        # without risk of excluding an event dated exactly on `EVENT_START` itself.
        evs = [e for e in events_by_ticker[tk] if e["exright_date"] == ex]
        mismatches, notes = cr.price_crosscheck_after("2000-01-01", evs, series, series_max)
        # one (ticker, ex) can only ever contribute ONE verdict note here since `evs` is already
        # narrowed to this single ex-date.
        assert len(notes) <= 1, (tk, ex, notes)
        if not notes:
            tier2["no_cum_bar_in_window"] += 1   # date filter excluded it — same as "not reached"
            continue
        note = notes[0]
        if "dev=" in note and ("khớp" in note or "MISMATCH" in note):
            tier2["tested"] += 1
            # `note` embeds dev already MULTIPLIED into percent units by Python's `%` format spec
            # (e.g. dev=0.014099 prints as "dev=+1.4099%") — dividing back by 100 here keeps
            # `tested_devs` a plain FRACTION, so `f"{x:.4%}"` below formats it correctly instead of
            # re-multiplying by 100 a second time (bug caught 2026-09-29: first draft printed
            # p50=140.85% and FP-vs-tol counts inflated ~65x because of exactly this double-scale).
            dev_str = note.split("dev=")[1].split("%")[0].replace("+", "")
            tested_devs.append(abs(float(dev_str)) / 100.0)
        else:
            tier2[_categorize(note)] += 1

    print()
    print(f"=== Tầng 1 — toàn bộ (ticker, ex-date) price-adjusting event, {EVENT_START}..{EVENT_END} ===")
    n_a = sum(tier1.values())
    for k in ("n_candidate", "no_series_for_ticker", "ex_beyond_series_max"):
        print(f"  {k}: {tier1[k]}")
    print(f"  TỔNG A = {n_a}")
    print(f"  ({len(tickers_no_series)} ticker riêng biệt trong no_series_for_ticker)")

    n_cand = tier1["n_candidate"]
    print()
    print(f"=== Tầng 2 — verdict của price_crosscheck_after trên n_candidate={n_cand} ===")
    for k in ("tested", "ffill_cum_band", "ffill_chained", "uncomputable_formula",
              "no_cum_bar_in_window"):
        print(f"  {k}: {tier2[k]}")
    print(f"  TỔNG tầng 2 = {sum(tier2.values())} (phải == n_candidate={n_cand})")
    assert sum(tier2.values()) == n_cand, "Tầng 2 không cộng khớp n_candidate — có nhánh chưa phân loại"

    if tested_devs:
        tested_devs.sort()
        n = len(tested_devs)
        print()
        print(f"=== |dev| trên {n} sự kiện TESTED ===")

        def pct(p):
            idx = min(n - 1, int(round(p * (n - 1))))
            return tested_devs[idx]

        for p in (0.50, 0.75, 0.90, 0.95, 0.97, 0.99):
            print(f"  p{int(p*100)}: {pct(p):.4%}")
        print(f"  max: {tested_devs[-1]:.4%}")
        print()
        for tol in (0.10, 0.15, 0.20, 0.25, 0.30):
            fp = sum(1 for d in tested_devs if d > tol)
            print(f"  ngưỡng {tol:.0%}: {fp}/{n} = {fp/n:.2%} false-positive")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
