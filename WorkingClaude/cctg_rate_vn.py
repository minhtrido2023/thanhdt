# -*- coding: utf-8 -*-
"""
cctg_rate_vn.py — Big-4 (VCB/BIDV/CTG/Agribank) CHỨNG CHỈ TIỀN GỬI (CCTG) rate, 6-month tenor.

NEW series, bootstrapped 2026-10-01 per user directive ("CCTG đưa vào model làm nguồn lãi proxy
nếu lãi suất cao hơn gửi tiết kiệm"). SEPARATE from deposit_rate_vn.py's Big-4 12M term-deposit
series — NEVER merges into or overwrites it. Combine the two only through
deposit_rate_vn.effective_deposit_rate(), which takes max(Big-4 12M, this CCTG series) — never
average, never silently replace one with the other.

Legal/instrument context (legal-vn secondary-source summary relayed in the 2026-10-01 user
directive, NOT independently re-verified this session -- re-verify with legal-vn before citing in
a client-facing document): CCTG ≈ term deposit for deposit-insurance purposes (Luật 111/2025, hạn
mức bảo hiểm 350 triệu VND), lãi CCTG được miễn thuế TNCN giống tiền gửi tiết kiệm, và lãi suất kỳ
hạn >=6 tháng do thị trường quyết định (không trần SBV). Vẫn là MỘT CÔNG CỤ KHÁC VỀ KỲ HẠN so với
sổ tiết kiệm 12 tháng: đây là lý do dùng max(), không gộp mù hai chuỗi khác kỳ hạn thành một.

Tenor mismatch (must NOT be papered over): deposit_rate_vn.py's series is **12-month**; this
series is **6-month**. A 6M rate sitting above a 12M rate is itself a market signal (inverted
curve / banks bidding up short tenor for liquidity) — effective_deposit_rate() surfacing that via
max() is intentional, not a bug, but any report citing the number must say which tenor is driving
it (see deposit_rate_vn.effective_deposit_rate()'s `driver` field).

First anchor only so far:
  - 2026-09-30: Big-4 CCTG 6-thang = 7.5%/nam (VietnamNet, 30/09/2026; mot so NH co phan toi 9.4%,
    nhung chuoi nay CHỈ theo dõi nhóm Big-4 để nhất quán với deposit_rate_vn.py's Big-4 scope).

Append-only: no observation before the first anchor's effective_date -> current_cctg_rate()
returns None (NOT an error, NOT a forward/backward guess) -- any backtest run before this file
existed, or any asof earlier than 2026-09-30, is BYTE-IDENTICAL to a world where this module never
existed (effective_deposit_rate() falls back to the Big-4 12M series alone whenever this returns
None). Future anchors go in `data/cctg_rate_vn_events.csv` (same append-only CSV pattern as
deposit_rate_vn.py's `_EVENTS_CSV` -- gitignored, never committed, forward-fill only).
"""
import os
import pandas as pd

CCTG_EVENTS = [
    ("2026-09-30", 7.5),
]

# Same sanity fence as deposit_rate_vn.py's Big-4 guard (0.5%..30%) -- duplicated, not imported,
# to avoid a circular import (deposit_rate_vn.py imports FROM this module).
RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0

_EVENTS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cctg_rate_vn_events.csv")


def cctg_events_df():
    """Loads the frozen CCTG_EVENTS anchor(s) plus any live append-only rows in _EVENTS_CSV.

    Quant-skeptic round-3 fix (2026-10-01): UNLIKE deposit_rate_vn.deposit_events_df() (which has
    a real pre-2026-07 legacy CSV format to stay backward-compatible with), CCTG is a BRAND NEW
    series bootstrapped 2026-10-01 -- there is no old format to tolerate. A wrong/missing header, an
    unparseable date, or an unparseable rate value (e.g. "9.4%", "9,4") used to be silently coerced
    to NaN and dropped via `dropna()`, so a broken append row vanished with zero trace and
    current_cctg_rate() just kept reading the last GOOD anchor -- "CLEAR" with no sign anything was
    wrong. Every one of those cases now raises loudly instead (same loud-propagation policy as the
    ParserError case already had), so the error reaches current_cctg_rate_checked() and from there
    macro_killswitch_a_status()/effective_deposit_rate()/effective_deposit_events_df() -- a missing
    or malformed row must surface, never disappear."""
    ev = pd.DataFrame(CCTG_EVENTS, columns=["time", "cctg_rate"])
    ev["time"] = pd.to_datetime(ev["time"])
    if os.path.exists(_EVENTS_CSV):
        try:
            extra = pd.read_csv(_EVENTS_CSV)
        except pd.errors.EmptyDataError:
            extra = None  # empty file (fresh install, no row appended yet) -> frozen anchor(s) only
        except pd.errors.ParserError:
            raise  # corrupt CSV -> surface loudly, same policy as deposit_rate_vn.py (2026-10-01)
        if extra is not None and len(extra):
            missing = {"effective_date", "cctg_rate"} - set(extra.columns)
            if missing:
                raise ValueError(
                    f"{_EVENTS_CSV}: thiếu cột {sorted(missing)} (header sai/cũ) -- CCTG là chuỗi "
                    f"MỚI (bootstrap 2026-10-01), không có định dạng cũ cần tương thích ngược như "
                    f"deposit_rate_vn.py, nên header sai PHẢI sửa file, không được âm thầm bỏ qua")
            extra = extra[["effective_date", "cctg_rate"]].rename(columns={"effective_date": "time"})
            raw_time, raw_rate = extra["time"].copy(), extra["cctg_rate"].copy()
            extra["time"] = pd.to_datetime(raw_time, errors="coerce")
            extra["cctg_rate"] = pd.to_numeric(raw_rate, errors="coerce")
            bad = extra["time"].isna() | extra["cctg_rate"].isna()
            if bad.any():
                bad_rows = list(zip(raw_time[bad].tolist(), raw_rate[bad].tolist()))
                raise ValueError(
                    f"{_EVENTS_CSV}: {bad.sum()} dòng không parse được (ngày hoặc cctg_rate): "
                    f"{bad_rows[:5]} -- phải sửa file, không được âm thầm drop")
            # Range guard at LOAD time, not just at the single-value current_cctg_rate_checked()
            # lookup -- effective_deposit_events_df() (Value Radar's full historical step series)
            # calls this function directly and previously had NO range validation at all, so a
            # format-valid-but-semantically-wrong typo (e.g. "85" meaning 8.5%) flowed straight
            # into the displayed deposit_rate as a NAKED 85% (quant-skeptic round-3 finding,
            # reproduced in cctg_overlay_selfcheck.py T_range_radar).
            oor = ~extra["cctg_rate"].between(RATE_MIN_PCT, RATE_MAX_PCT)
            if oor.any():
                bad_vals = extra.loc[oor, "cctg_rate"].tolist()
                raise ValueError(
                    f"{_EVENTS_CSV}: {oor.sum()} dòng cctg_rate ngoài khoảng hợp lệ "
                    f"[{RATE_MIN_PCT},{RATE_MAX_PCT}]: {bad_vals[:5]} -- phải sửa file, không được "
                    f"âm thầm drop/dùng thẳng")
            # Round-5 fix (2026-10-01, quant-skeptic round-4): a row with effective_date <=
            # anchor's own max date used to be silently filtered out by `extra["time"] >
            # ev["time"].max()` with zero trace (e.g. a typo'd year like "2025-10-02" instead of
            # "2026-10-02" would just vanish, leaving current_cctg_rate() quietly reading the
            # 2026-09-30 anchor forever while the human believes a newer row was appended). <=
            # (not just <, i.e. a duplicate of the anchor date itself) also raises -- a same-date
            # append is either a genuine duplicate or an intended correction, neither of which this
            # append-only module may silently drop or silently accept.
            not_newer = extra["time"] <= ev["time"].max()
            if not_newer.any():
                bad_dates = [str(d) for d in extra.loc[not_newer, "time"].dt.date.tolist()]
                raise ValueError(
                    f"{_EVENTS_CSV}: {not_newer.sum()} dòng effective_date <= anchor hiện tại "
                    f"({ev['time'].max().date()}): {bad_dates[:5]} -- có thể là lỗi gõ ngày (năm "
                    f"cũ) hoặc trùng ngày -- phải sửa file, không được âm thầm drop")
            ev = pd.concat([ev, extra[["time", "cctg_rate"]]], ignore_index=True)
    return ev.sort_values("time").reset_index(drop=True)


def current_cctg_rate(asof=None):
    """Returns (rate_pct, last_date) or (None, None) if no CCTG observation exists at/before asof
    (in particular: any asof before 2026-09-30). asof=None means TODAY (see deposit_rate_vn's
    current_deposit_rate() docstring for why this must anchor to the real clock, not just the
    series' own last row)."""
    ev = cctg_events_df()
    asof_ts = pd.Timestamp.today().normalize() if asof is None else pd.to_datetime(asof)
    avail = ev[ev.time <= asof_ts]
    if avail.empty:
        return None, None
    last_date = avail.iloc[-1]["time"]
    rate_pct = float(avail.iloc[-1]["cctg_rate"])
    return rate_pct, last_date


def current_cctg_rate_checked(asof=None):
    """Same as current_cctg_rate() but makes CCTG-side problems VISIBLE to the caller instead of
    letting them disappear into "no CCTG data, fall back to Big-4 silently" -- added 2026-10-01
    per quant-skeptic round-2 fix 1. Before this, every CCTG-side failure mode (a corrupt/
    unparseable CSV, an out-of-range typo'd value e.g. a fraction-vs-percent slip) was swallowed by
    macro_killswitch_a_status()'s bare `except Exception: pass` around the CCTG overlay call --
    degrading a fail-CLOSED gate into fail-OPEN on the Big-4-only reading whenever the CCTG side
    broke, asymmetric with how every Big-4-side failure in that same function is handled (fail-
    closed with an explicit reason). This function centralizes the validation so every caller
    (macro_killswitch_a_status, effective_deposit_rate) gets the same symmetric treatment.

    Returns (rate_pct|None, date|None, error|None):
      - error is a short diagnostic string (rate_pct/date forced to None) when: (a)
        cctg_events_df() raises (corrupt CSV -- same loud-propagation policy as
        deposit_rate_vn.deposit_events_df()'s ParserError handling), or (b) the raw value is
        outside the sanity fence [RATE_MIN_PCT, RATE_MAX_PCT].
      - error is None (rate_pct/date may legitimately still be None) when there is simply no CCTG
        observation at/before asof -- that is NOT an error, it is the normal pre-anchor state
        (any asof before 2026-09-30) and callers must keep treating it as silent Big-4 fallback."""
    try:
        rate_pct, date = current_cctg_rate(asof)
    except Exception as exc:
        return None, None, f"cctg error: {exc!r}"
    if rate_pct is None:
        return None, None, None
    if not (RATE_MIN_PCT <= rate_pct <= RATE_MAX_PCT):
        return None, None, (f"cctg rate_pct={rate_pct!r} ngoài khoảng hợp lệ "
                             f"[{RATE_MIN_PCT},{RATE_MAX_PCT}]")
    return rate_pct, date, None
